#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Minitelex script v3.0
# Socket Server als i-Telexdiensteübergang
# Individuelle Ports
# Faxversand IAXMODEM -> ASTERISK -> personal-voip

# from creds import *
import socket
import select
import sys
import requests
from _thread import *
from time import sleep
from subprocess import call

anschluesse = {}
knng = {}
faxe = {}
isA4 = {}

enscriptEps = '~epsf[sx1.05 sy0.95 x-4a y0a]{telexpapier.eps}'

HOST = ''   # Symbolic name, meaning all available interfaces

with open('minitelexbuch.txt', 'r') as f:
	for line in f:
		port, kng, fax, iA4 = line.strip().split(':')
		knng[port] = kng
		faxe[port] = fax
		isA4[port] = iA4
		print (port + knng[port] + faxe[port])
servers = []

for port in knng:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print ('Socket created')
	try:
		s.bind((HOST, int(port)))
	except socket.error as msg:
		print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		sys.exit()
	
	print ('Socket bind complete on port: ' + port)

	s.listen(10)
	print ('Socket now listening')
	servers.append(s)

#Function for handling connections. This will be used to create threads
def clientthread(conn):
	port = str(conn.getsockname()[1])
	print('Port: ' + port)
	print('--------------------------')
	print('Nachrichtenempfang:')
	nachricht = ""
	sleep(2)
	while True:
		#Receiving from client
		bytData = conn.recv(1024)
		data = bytData.decode('utf-8')
		print (data)
		if not bytData:
			break
		if '@' in data:
			sleep(1)
			kennu = '\r\n' + knng[port]
			for x in range(len(kennu)):
				conn.send(kennu[x].encode('utf-8'))
				sleep(0.15)
			print (kennu)
			nachricht += kennu
		elif '#' in data:
			data = ''		
		else:
			nachricht += data

	#came out of loop
	conn.close()

	print(nachricht)
	print('--------------------------')
	print ('connection closed')

	if (len(nachricht) > 20) and (isA4[port] == '0'):
		print('hallo, wahl ist kurze seite')
		with open(port + ".txt", "w+") as tf:
			tf.write(nachricht)
		rc = call(['sendfax -n -d %s %s.txt' % (faxe[port],port)], shell=True)
	elif (len(nachricht) > 20) and (isA4[port] == '1'):
		print('hallo, wahl ist a4')
		with open(port + ".txt", "w+") as tf:
			tf.write(nachricht)
		rc = call(["./txt2pdf.sh " + port], shell=True)
		rc = call(['sendfax -n -d %s %s.pdf' % (faxe[port],port)], shell=True)
	elif (len(nachricht) > 20) and (isA4[port] == '2'):
		print('hallo, wahl ist rand')
		if len(nachricht.split('\r\n')) > 58:
			zeilen = nachricht.split('\r\n')
			n = 58
			i = n
			while i < len(zeilen):
				zeilen.insert(i, enscriptEps)
				i += (n+1)
			nachricht = '\r\n'.join(zeilen)
		nachricht += enscriptEps
		with open(port + ".txt", "w+") as tf:
			tf.write(nachricht)
		rc = call(["./telex2pdf.sh " + port], shell=True)
		rc = call(['sendfax -n -d %s %s.pdf' % (faxe[port],port)], shell=True)
	
#now keep talking with the client
while True:
	readable,_,_ = select.select(servers, [], [])
	ready_server = readable[0]
    #accept only active connections - non-blocking call
	conn, addr = ready_server.accept()
	print ('Connected with ' + addr[0] + ':' + str(addr[1]))
	#start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
	start_new_thread(clientthread ,(conn,))
	
for port in knng:
	s.close()
	