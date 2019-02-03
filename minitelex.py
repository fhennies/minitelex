#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Minitelex script v3.1
# Kennungsgeberabfrage, speichere jobid
# bessere struktur
# Socket Server als i-Telexdiensteübergang
# Individuelle Ports
# Faxversand IAXMODEM -> ASTERISK -> personal-voip

from telex import *
import socket
import select
import sys
import requests
import datetime
from _thread import *
from time import sleep
from subprocess import call
from tinydb import TinyDB, Query

anschluesse = {}
knng = {}
faxe = {}
isA4 = {}

servers = []

enscriptEps = '~epsf[sx1.05 sy0.95 x-4a y0a]{telexpapier.eps}'

HOST = ''   # Symbolic name, meaning all available interfaces

def zieheKennung(nachricht):
	zeilen = nachricht.split('\r\n')
	hierIst = ''
	if len(zeilen) > 4:
		if len(zeilen[-1]) > 5:
			hierIst = zeilen[-1].strip('+')
			werDa = zeilen[-2]
		elif len(zeilen[-2]) > 5:
			hierIst = zeilen[-2].strip('+')
			werDa = zeilen[-3]
		elif len(zeilen[-3]) > 5:
			hierIst = zeilen[-3].strip('+')
			werDa = zeilen[-4]
		print (hierIst)
	return hierIst

def telexRand(text):
	zeilen = text.split('\r\n')
	mitRand = text
	if len(zeilen) > 58:
		n = 58
		i = n
		while i < len(zeilen):
			zeilen.insert(i, enscriptEps)
			i += (n+1)
		mitRand = '\r\n'.join(zeilen)
	mitRand += enscriptEps
	return mitRand

def faxen(nachricht, port, jobtag):
	if (len(nachricht) > 40) and (isA4[port] == '0'):
		print('wahl ist kurze seite')
		with open('cache/%s.txt' % port, "w+") as tf:
			tf.write(nachricht)
		rc = call(['sendfax -n -i %s -d %s cache/%s.txt' % (jobtag, faxe[port],port)], shell=True)
	elif (len(nachricht) > 40) and (isA4[port] == '1'):
		print('wahl ist a4')
		with open('cache/%s.txt' % port, "w+") as tf:
			tf.write(nachricht)
		rc = call(['cache/txt2pdf.sh ' + port], shell=True)
		rc = call(['sendfax -n -i %s -d %s cache/%s.pdf' % (jobtag, faxe[port],port)], shell=True)
	elif (len(nachricht) > 40) and (isA4[port] == '2'):
		print('wahl ist rand')
		nachrichtRand = telexRand(nachricht)
		with open('cache/%s.txt' % port, "w+") as tf:
			tf.write(nachrichtRand)
		rc = call(['cache/telex2pdf.sh ' + port], shell=True)
		rc = call(['sendfax -n -i %s -d %s cache/%s.pdf' % (jobtag, faxe[port],port)], shell=True)

#Function for handling connections. This will be used to create threads
def clientthread(conn):
	port = str(conn.getsockname()[1])
	print('Port: ' + port)
	jetzt = datetime.datetime.now().replace(microsecond=0).isoformat(' ')
	print('--------------------------')
	print('Nachrichtenempfang:')
	nachricht = jetzt + '\r\n'
	sleep(2)
	nachricht += empfangen(knng[port], conn)

	#came out of loop
	conn.close()

	print(nachricht)
	print('--------------------------')
	print ('connection closed')

	hierIst = zieheKennung(nachricht)
	senderNummer = hierIst.split(' ')
	senderExist, senderHost, senderIp, durchwahl = auskunft(senderNummer[0])
	jobTagID = 0
	db = TinyDB('minifaxe.json')
	suche = Query()
	if 'ok' in senderExist:
		try:
			od = sorted(db.search(suche.Minitelex == str(port)), key=lambda k: k['jobTagID'])
			jobTagID = od[-1]['jobTagID']+1
		except:
			jobTagID = 1
		db.insert({'Minitelex' : str(port), 'MiniKennung' : knng[port], 'jobTagID' : jobTagID, 'Kennung' : hierIst, \
			'Nummer' : senderNummer[0], 'Zeit' : jetzt})
	db.close()
	jobtag = str(port) + '-' + str(jobTagID)
	faxen(nachricht, port, jobtag)

# ende der definitionen

with open('minitelexbuch.txt', 'r') as f:
	for line in f:
		port, kng, fax, iA4 = line.strip().split(':')
		knng[port] = kng
		faxe[port] = fax
		isA4[port] = iA4
		print (port + knng[port] + faxe[port])

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
	