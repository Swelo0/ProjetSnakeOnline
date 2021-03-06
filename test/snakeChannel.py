#!/usr/bin/python2.6
# -*-coding:Latin-1 -*

import socket
import sys
from random import randint

class snakeChannel:
	# - host
	# - port
	# - s (socket)
	# - reply
	# - addr

	def __init__(self,host,port,timeout,isServ):

		self.host = host
		self.port = port
		self.reply = ''
		self.isConnected = False
		#Les numéros de séquence pour la communication
		self.isServ = isServ
		self.randNum = randint(0,2**32-1)#Notre num aléatoire pour la demande de token
		self.numSeqMax = format(2**32-1,'08x')
		#if isServ:
		self.toSeq = {}
		self.fromSeq = {}
		self.clientPhase = {}
		self.clientChallenge = {}
		#else :
		#	self.numSeq = 0
		#	self.numSeqServ = 0
		#Création socket
		try :
			self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			print 'Socket created'
		except socket.error, msg :
			print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			sys.exit()
		#if isServ:
			#Bind
		try:
			self.s.bind((host, port))
			print 'Liaison au socket effectuée'
		except socket.error , msg:
			print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			sys.exit()
		#Timeout set à 1 seconde si null
		if not timeout:
			self.s.settimeout(1)
		else:
			self.s.settimeout(timeout)


	def Connexion(self, host, port):

		
		#Demande de connexion client
		msg = 'GetToken '+str(self.randNum)+' Snake'
		#-------------------------------------------------------------------#
		# On demande un Token au serveur, on boucle tant qu'on ne l'a pas.  #
		#-------------------------------------------------------------------#
		while(1):
			# On envoie de la demande de Token
			self.write(True,msg,(host, port))

			#On attend la réponse, si on reçoit rien, on relance
			try:
				d = self.s.recvfrom(1024)
				self.reply = d[0].split(" ")
				print self.reply 
				if self.reply[1] == 'Token' and self.reply[3] == str(self.randNum) :
					Token = self.reply[2]
				else:
					print 'Error message' # test
					continue
				break
			except socket.timeout :
				continue

		#-----------------------------------------------------------------------------#
		# Demande de connection au serveur, on boucle tant qu on n est pas connecté.  #
		#-----------------------------------------------------------------------------#	
		while self.isConnected == False :
			data = format(2**32-1,'02x')+' Connect \challenge\\'+ Token +'\protocol\\19'
			print data
			self.s.sendto(data,(host, port))

			#On attend la réponse, si on reçoit rien, on relance
			try:
				d = self.s.recvfrom(1024)
				self.reply = d[0].split(" ")
				addr = d[1]		
				if self.reply[1] == 'Connected' and self.reply[2] == Token :
					print 'Connected to host'
					self.isConnected = True
#On crée un num de séquence sur 4 bytes pour ce client qu'on initialise à 0
					self.toSeq[addr] = 0
#On crée un num de séquence sur 4 bytes pour le serveur pour cette connexion qu'on initialise à 0
					self.fromSeq[addr] = 0
				else:
					print 'Error message' # test
					continue
				break
			except socket.timeout :
				continue

###############################################
	def read(self):
		try:
			data, addr = self.s.recvfrom(1024)
			self.reply = data.split(" ")	
		except socket.timeout :
			return

		#if self.isServ:
		#--------------------------------------------------------#
		# Si séquence égale demande de connexion phase GetToken  #
		#--------------------------------------------------------#		
		if self.reply[0] == self.numSeqMax and self.reply[1] == 'GetToken':
			msg = 'Token '+str(self.randNum)+' '+self.reply[2]+' 19'
			self.write(True,msg,addr)
			self.clientPhase[addr] 	= 'GetToken'
			self.clientChallenge[addr]	= self.randNum
		#--------------------------------------------------------#
		# Si séquence égale demande de connexion phase Connexion #
		#--------------------------------------------------------#
		elif self.reply[0] == self.numSeqMax and self.reply[1] == 'Connect':
#Vérification de la présence du client dans le dico de connexion
			if self.clientPhase.has_key(addr):
#Vérification que ce client a bien passé la phase GetToken
				if self.clientPhase[addr] == 'GetToken':
					print'Its a demand to make a connection, phase Connect\n'
					chall_split = self.reply[2].split("\\")
#Vérification de la chaine ascii envoyée par le client
					if chall_split[1] == 'challenge' and chall_split[2] == str(self.clientChallenge.get(addr)) and chall_split[3] == 'protocol' and chall_split[4] == '19':
#Ecriture et envoi de la réponse
						msg = 'Connected ' + str(self.clientChallenge.get(addr))
						self.write(True,msg,addr)
#Mise à jour du dictionnaire de connexion
						self.clientPhase[addr] = 'Connected'
#Mise à jour des clients connectés
#On crée un num de séquence sur 4 bytes pour ce client qu'on initialise à 0
						self.toSeq[addr] = 0
#On crée un num de séquence sur 4 bytes pour le serveur pour cette connexion qu'on initialise à 0
						self.fromSeq[addr] = 0	
			#--------------------------------------------------------#
			# Si séquence n'est pas égale aux messages hors-bandes   #
			#--------------------------------------------------------#	
		elif self.reply[0] < format(2**32-1,'02x'):
			if self.reply[0] > self.toSeq.get(addr):
				self.toSeq[addr] = self.reply[0]
				return (data, addr)
# Partie Client (obsolète)
		'''else :
			# On recois les donnees du client
			try :
				d = self.s.recvfrom(1024)
				self.reply = d[0].split(" ")

				if self.reply[0] <= self.numSequServ :
					self.reply = ''
				else :
					self.numSequServ = self.reply[0]
				return reply
			except socket.timeout :
				return '''
			
		



###############################################				
	def write(self,isNumSeqMax,msg,addr):
		if isNumSeqMax :
			msg = self.numSeqMax + ' ' + msg
			self.s.sendto(msg, addr)
		else :
			#if self.isServ : 
			msg = format(self.fromSeq[addr],'08x') + ' ' + msg
			self.fromSeq[addr] = self.fromSeq[addr] + 1
			#else :
			#	msg = format(self.numSeq,'08x') + ' ' + msg
			#	self.numSeq = self.numSeq + 1
			self.s.sendto(msg, addr)
		
