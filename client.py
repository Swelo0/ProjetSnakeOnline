#!/usr/bin/python2.6
# -*-coding:Latin-1 -*

#-------------------------------------------------------------------#
#         Client utilisant le protocole SnakeChannel                #
#-------------------------------------------------------------------#

import socket   
import sys  #pour exit
import select 
 
# create dgram udp socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print 'Failed to create socket'
    sys.exit()
 
host = 'localhost';
port = 8888;

from random import randint
randNum = randint(0,2**32-1)#Notre num aléatoire pour la demande de token
#Construction du message de demande de token
data = format(2**32-1,'02x')+' GetToken '+str(randNum)+' Snake'

#Timeout set à 1 seconde
s.settimeout(1)
#Variable pour savoir si on est connecte, pas encore utilise
#mais peut etre utile par la suite
connected = False
#-------------------------------------------------------------------#
# On demande un Token au serveur, on boucle tant qu'on ne l'a pas.  #
#-------------------------------------------------------------------#
while(1):
	# Onvoie de la demande de Token
	s.sendto(data,(host, port))
	print 'send : ' + data + ' to host'
	
	#On attend la réponse, si on reçoit rien, on relance
	try:
		d = s.recvfrom(1024)
		reply = d[0].split(" ")
		addr = d[1]
	
		if reply[1] == 'Token' and reply[3] == str(randNum) :
			Token = reply[2]
			print 'Get Token from host ' + Token
		else:
			print 'Error message' # test
			continue
		break
	except socket.timeout :
		continue

#-----------------------------------------------------------------------------#
# Demande de connection au serveur, on boucle tant qu on n est pas connecté.  #
#-----------------------------------------------------------------------------#	
while connected == False :
	data = format(2**32-1,'02x')+' Connect \challenge\\'+ Token +'\protocol\\19'
	print data
	s.sendto(data,(host, port))	
	
	#On attend la réponse, si on reçoit rien, on relance
	try:
		d = s.recvfrom(1024)
		reply = d[0].split(" ")
		addr = d[1]		
		if reply[1] == 'Connected' and reply[2] == Token :
			print 'Connected to host'
			connected = True
		else:
			print 'Error message' # test
			continue
		break
	except socket.timeout :
		continue
	
 
#Les numéros de séquence pour la communication
numSequ = 0;
numSequServ = 0;
#Test du protocole en envoyant des messages
while(1) :
	msg = raw_input('Enter message to send : ')
	msg = format(numSequ,'08x')+' '+msg
	try :
        #On envoie le message
		s.sendto(msg, (host, port))
		numSequ = numSequ + 1
		# On recois les donnees du client
		try :
			d = s.recvfrom(1024)
			reply = d[0].split(" ")
			if reply[0] <= numSequServ :
				continue
			numSequServ = reply[0]
			addr = d[1]
		except socket.timeout :
			continue
		
		print 'Server reply : ' +reply[0]+ ' ' + reply[1] + ' ' + reply[2]
		
	except socket.error, msg :
		print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
		sys.exit()
