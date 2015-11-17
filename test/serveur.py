#!/usr/bin/python2.6
# -*-coding:Latin-1 -*

#-------------------------------------------------------------------#
#         Serveur utilisant le protocole SnakeChannel                #
#-------------------------------------------------------------------#

import sys  #pour exit
import select 
import snakeChannel
 
host = '127.0.0.1'  
port = 8889

sc = snakeChannel.snakeChannel(host,port,1,True)

#Server is running
server_running = True; 
while server_running:
	reply = sc.read()
    	if reply :
		print 'Message from Client : ' +reply[0]
		msg = 'Message "' + str(reply[0]) + '" bien reçu'
		sc.write(False,msg,(host, 8888))
 
s.close()

