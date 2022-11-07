#!/bin/bash

# Cleanup to be "stateless" on startup, otherwise pulseaudio daemon can't start
rm -rf /var/run/pulse /var/lib/pulse /root/.config/pulse

# Start pulseaudio as system wide daemon; for debugging it helps to start in non-daemon mode
#pulseaudio -D --verbose --exit-idle-time=-1 --system --disallow-exit
pulseaudio --start -vvv --disallow-exit --log-target=syslog --high-priority --exit-idle-time=-1

# Create a virtual audio source; fixed by adding source master and format
echo "Creating virtual audio source: ";
pactl load-module module-virtual-source master=auto_null.monitor format=s16le source_name=VirtualMic

# Set VirtualMic as default input source;
echo "Setting default source: ";
pactl set-default-source VirtualMic

gunicorn -b 0.0.0.0:8001 --workers 3 --timeout 200  wsgi:app
