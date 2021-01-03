#!/bin/bash

DATA=`sudo lspci -vvv`

echo "$DATA" | python3 convert.py
#echo -n -e $DATA | python3 convert.py

