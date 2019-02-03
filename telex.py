#!/usr/bin/env python3
# -*- coding: utf-8 -*-

	# Gemeinsame Telexfunktionen
	# f. Telegraf, Minitelex, Auftragsdienst

import socket
import sys
from time import sleep
from textwrap import wrap

AUSKUNFTHOST = 'sonnibs.no-ip.org'
AUSKUNFTPORT = 11811

ita2bu = 'abcdefghijklmnopqrstuvwxyz \r\n'
ita2zi = ' -?:38().,9014\'57=2/6+\r\n'
ita2 = 'abcdefghijklmnopqrstuvwxyz -?:38().,9014\'57=2/6+\r\n'

def auskunft(anschluss):
	ipaddr = {}
	port = {}
	hostip = '0.0.0.0'
	hostport = 0
	durchwahl = ''
	with open('telegrafenbuch.txt', 'r') as f:
		for line in f:
			nummer, ipad, prt = line.strip().split(':')
			ipaddr[nummer] = ipad
			port[nummer] = int(prt)
	if anschluss in ipaddr:
		resultat = 'ok'
		hostip = ipaddr[anschluss]
		hostport = port[anschluss]
	else:
		datensatz = ''
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(2)
		try:
			s.connect((AUSKUNFTHOST, AUSKUNFTPORT))
		except socket.timeout:
			sys.exit()
		s.send(('q' + str(anschluss)).encode('utf-8'))
		while True:
			try:
				data = s.recv(1024).decode('utf-8')
				datensatz += data
			finally:
				break
		lines = datensatz.split('\r\n')
		if 'ok' in lines[0]:
			resultat = 'ok'
			hostip = lines[4]
			hostport = int(lines[5])
			durchwahl = lines[6].strip('-')
		else:
			resultat = 'np'
	try:
		hostip = socket.gethostbyname(hostip)
	except socket.error as msg:
		print ('%s : ERROR: %s' % (hostip, msg))
	return resultat, hostip, hostport, durchwahl

def cleanText(text):
	ita2repl = {'ä':'ae','ö':'oe','ü':'ue','å':'aa','ß':'ss','\"':'\'',\
			'[':'(',']':')','{':'(','}':')',';':',','!':'.','„':'\'','“':'\''}
	text = text.lower()
	for x in ita2repl:
		text = text.replace(x, ita2repl[x])
	for x in text:
		if x not in ita2:
			text = text.replace(x, '')
	return text

def umbrechen(text):
	zeilen = []
	absaetze = text.split('\n')
	for stueck in absaetze:
		umbruch = "\r\n".join(wrap(stueck, width=68))
		zeilen.append(umbruch)
	fertigText = "\r\n".join(zeilen)
	return fertigText
	
def zaehleBuZi(text):
	i = 0
	for x in range(len(text)-1):
		if (text[x] in ita2bu) != (text[x+1] in ita2bu):
			i += 1
	return i

def senden(text, conn):
	gesendet = ''
	for x in range(len(text)):
		conn.send(text[x].encode('utf-8'))
		sleep(0.16)
	if not '@' in text:
		gesendet+=text
	sleep(zaehleBuZi(text) * 0.16)
	return gesendet

def empfangen(kennung, conn):
	empfText = ''
	while True:
		try:
			byteData = conn.recv(1024)
			data = byteData.decode('utf-8')
			if not byteData:
				break
			if '@' in data:
				sleep(1)
				data = senden('\r\n' + kennung, conn)
			empfText+=data
		except socket.timeout:
			break
	return cleanText(empfText)

def sendeTelex(text, nummer, kennung):
	text = cleanText(text)
	text = umbrechen(text)
	ergebnis, ipaddr, port, durchwahl = auskunft(nummer)
	if 'np' in ergebnis:
		return 'np', ''     # return np kein teilnehmer und leere nachricht
	message = ''
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(6)
	print (ipaddr + ':' + str(port))
	try:
		s.connect((ipaddr, port))
	except socket.timeout:
		return 'occ', ''	# return occ besetzt und leere nachricht
	except socket.gaierror as msg:
		print ('%s : ERROR: %s' % (ipaddr, msg))
		return 'np', ''     # return np kein teilnehmer und leere nachricht
	except ConnectionRefusedError:
		return 'occ', ''	# return occ besetzt und leere nachricht
	nul = s.send(('*' + durchwahl + '*').encode('utf-8'))
	s.settimeout(4)
	message += senden('\r\n', s)
	message += empfangen(kennung, s)
	if ('occ' in message):
		return 'occ', ''	# return occ besetzt und leere nachricht
	if ('abs' in message):
		return 'abs', ''	# return abs abwesend und leere nachricht
	s.settimeout(4)
	message += senden('\r\n', s)
	message += senden('@\r', s)
	message += empfangen(kennung, s)
	sleep(2)
	message += senden('\r\n' + kennung, s)
	message += senden('\r\n', s)
	message += senden(text + '\r\n', s)
	sleep(4)
	message += senden('@\r', s)
	message += empfangen(kennung, s)
	sleep(2)
	message += senden('\r\n' + kennung, s)
	message += senden('+++\r\n', s)
	sleep(4)
	s.close()
	return 'r', message		# return r erhalten und nachricht




