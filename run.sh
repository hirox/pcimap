#!/bin/bash

DATA=`sudo lspci -vvv`

#echo "$DATA" | python3 convert.py | plantuml -p -tsvg
echo "$DATA" | python3 convert.py -m > out.md
