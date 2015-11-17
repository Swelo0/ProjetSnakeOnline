#!/usr/bin/python2.6
# -*-coding:Latin-1 -*

import socket
import sys
import select
from random import randint
 
host = ''   # Symbolic name meaning all available interfaces
port = 8888 # Arbitrary non-privileged port

#Liste des séquences clients avec la dernière séquence
clients_sequence = {}
#Liste des séquences serveur avec la dernière séquence
serveur_sequence = {}
#Liste des clients en cours de connexion
clients_phase = {}
#Liste des challenges des clients
clients_challenge = {}
 
# Datagram (udp) socket
try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'Socket created'
except socket.error, msg :
    print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
 
 
# Bind socket to local host and port
try:
    s.bind((host, port))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'

#Server is running
server_running = True; 
#now keep talking with the client
while server_running:
# receive data from client (data, addr)
    data, addr = s.recvfrom(1024)
 
    if not data:
        break

#Affichage du message reçu
    print 'Message reçu de [' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
#Split du message reçu
    data_split = data.split(" ")  
#Contrôle du numéro de séquence
#--------------------------------------------------------#
# Si séquence égale demande de connexion phase GetToken  #
#--------------------------------------------------------#
    if data_split[0] == format(2**32-1,'02x') and data_split[1] == 'GetToken':
        print'Its a demand to make a connection, phase GetToken\n'
        randNum = randint(0,2**32-1)
#Ecriture et envoi de la réponse
        reply = format(2**32-1,'02x')+' Token '+str(randNum)+' '+data_split[2]+' 19'
		print 'Message envoye: ' + reply + ' au client [' + addr[0] + ':' + str(addr[1]) + ']'
		s.sendto(reply , addr)
#Mise à jour du dictionnaire de connexion
		clients_phase[addr] = 'GetToken'
#Mise à jour du challenge
        clients_challenge[addr] = randNum
#--------------------------------------------------------#
# Si séquence égale demande de connexion phase Connexion #
#--------------------------------------------------------#
    elif data_split[0] == format(2**32-1,'02x') and data_split[1] == 'Connect':
#Vérification de la présence du client dans le dico de connexion
        if clients_phase.has_key(addr):
#Vérification que ce client a bien passé la phase GetToken
            if clients_phase[addr] == 'GetToken':
				print'Its a demand to make a connection, phase Connect\n'
                chall_split = data_split[2].split("\\")
#Vérification de la chaine ascii envoyée par le client
                if chall_split[1] == 'challenge' and chall_split[2] == str(clients_challenge.get(addr)) and chall_split[3] == 'protocol' and chall_split[4] == '19':
#Ecriture et envoi de la réponse
                    reply = format(2**32-1,'02x')+' Connected ' + str(clients_challenge.get(addr))
                    print 'Message envoye: ' + reply + ' au client [' + addr[0] + ':' + str(addr[1]) + ']'
		    s.sendto(reply , addr)
#Mise à jour du dictionnaire de connexion
	            clients_phase[addr] = 'Connected'
#Mise à jour des clients connectés
#On crée un num de séquence sur 4 bytes pour ce client qu'on initialise à 0
        	    clients_sequence[addr] = 0
		    print 'Le numéro de séquence pour le client [' + addr[0] + ':' + str(addr[1]) + '] est égal à ' + format(clients_sequence.get(addr),'08x')
#On crée un num de séquence sur 4 bytes pour le serveur pour cette connexion qu'on initialise à 0
		    serveur_sequence[addr] = 0
		    print 'Le numéro de séquence pour le serveur de cette connexion [' + addr[0] + ':' + str(addr[1]) + '] est égal à ' + format(serveur_sequence.get(addr),'08x')
#--------------------------------------------------------#
# Si séquence n'est pas égale aux messages hors-bandes   #
#--------------------------------------------------------#
    elif data_split[0] < format(2**32-1,'02x'):
        if data_split[0] > clients_sequence.get(addr):
	    clients_sequence[addr] = data_split[0]
#Debug pour incrément séquence
#	    reply = 'Message reçu:' + data_split[1] + ' avec le numéro de séquence: ' + clients_sequence.get(addr) + ' effectivement supérieur'
#On donne une réponse et on incrémente le num séquence du serveur
	    reply = format(serveur_sequence.get(addr),'08x') + ' Message reçu:' + data_split[1]
	    serveur_sequence[addr] = serveur_sequence.get(addr) + 1
	    print 'Message envoye: ' + reply + ' au client [' + addr[0] + ':' + str(addr[1]) + '] avec le numero de sequence ' + format(serveur_sequence.get(addr),'08x')
	    s.sendto(reply , addr)
#--------------------------------------------------------#
# Sinon on traite les formats inconnus (débuggage)       #
#--------------------------------------------------------# 
    else:
        reply = 'Ce message possède un format inconnu du serveur. Message reçu = ' + data
	print 'Message envoye: ' + reply + ' au client [' + addr[0] + ':' + str(addr[1]) + ']'
	s.sendto(reply , addr)
		
#reply = 'OK...' + data
#s.sendto(reply , addr)
#print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
     
s.close()
