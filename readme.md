# Skript für Minitelex im i-Telex-Netz

Gegen Ende der Fernschreiberära bot die schon privatisierte Telekom an, statt richtiger Fernschreiber Telefaxgeräte als reine Empfangsmaschinen ans Telexnetz anzuschließen. Was damals dafür gedacht war, die Abschaltung des Telexnetzes vorzubereiten ist jetzt ein netter Spaß für Sammler und Bewahrer alter Kommunikationstechnik, sind doch Faxgeräte selber schon historisch.

Fernschreiber können über das [i-Telex-Netz](http://www.i-telex.net/) wieder zum Leben erweckt werden, dieses Skript hier stellt die [Minitelex-Funktion](https://www.telexforum.de/viewtopic.php?f=235&t=1572) nach.

Ein Pythonscript stellt den Server bereit, der die Faxe mit Hylafax-Sendfax versendet. Haylafax verwendet IAXModem, auf dem Server läuft Asterisk, dass von IAX auf SIP übersetzt. Asterisk ist direkt mit einem VOIP-Provider konfiguriert. Die Hylafax-IAXModem-Asterisk-Installation folgt [dieser Anleitung](https://www.yajhfc.de/84-documentation/howtos/160-hylafax-mit-voip-ueber-fritz-box).

Die Teilnehmereinträge sind in einer Datei `telexbuch.txt`, mit einer Zeile pro Eintrag, Angaben getrennt mit Doppelpunkt `port:kennung:faxnummer`

Die obsolete Version 1 fiel eher in die Kategorie schnell und einfach als elegant, der Faxversand wird über die mail2fax-Funktion eines VOIP-Provider erledigt. Alle Login-Daten waren in die creds.py Datei ausgelagert, siehe creds_example.py. Diese wird in der aktuellen Version nicht mehr verwendet.