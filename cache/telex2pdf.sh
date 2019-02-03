# !/bin/bash

cd cache/
echo "$0"

textFile="$1"."txt"
psFile="$1"."ps"
pdfFile="$1"."pdf"

echo "$textFile"

enscript -e~ -B --margins=40:10:30:30 -M A4 -f Courier12 --word-wrap -p "$psFile" "$textFile"
ps2pdf "$psFile" "$pdfFile"