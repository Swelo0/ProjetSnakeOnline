#!/usr/bin/python2.6
# -*-coding:Latin-1 -*

#-------------------------------------------------------------------#
#         Client utilisant le protocole SnakeChannel                #
#-------------------------------------------------------------------#
 
import sys  #pour exit
import select 
import snakeChannel
 
host = '127.0.0.1';
port = 8888;

sc = snakeChannel.snakeChannel(host,port,1,False)

sc.Connexion(host, 8889)

#Test du protocole en envoyant des messages
while(1) :
	msg = raw_input('Enter message to send : ')
	sc.write(False,msg,(host, 8889))
	reply = sc.read()
	if reply :
		print 'Server reply : ' + str(reply)

