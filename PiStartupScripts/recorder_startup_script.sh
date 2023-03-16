#!/bin/bash

printf '#############################################\nStart of AXD Localisation Streaming\n############################################\n'

# Change to correct folder
cd /home/pi/StringTheory_AXD/PiStartupScripts

# Start ssh-agent so password not required
eval $(ssh-agent -s)

# Start recording script
printf 'Starting Streaming\n'
sudo python3 python_stream.py
