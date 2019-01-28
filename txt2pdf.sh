# !/bin/bash

echo "$0"

textFile="$1"."txt"
psFile="$1"."ps"
pdfFile="$1"."pdf"

echo "$textFile"

enscript -B -j --margins=35:35:60:60 -M A4 -f Courier12 --word-wrap -p "$psFile" "$textFile"
ps2pdf "$psFile" "$pdfFile"