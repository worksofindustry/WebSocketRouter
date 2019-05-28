#!/bin/bash
clear

while true;do
        echo "Killing existing NTF process"
	sudo pkill ntf
        sleep 1
        echo "Starting new NTF process"
        sudo python ~/EENWebsocketRouter/automation/notifyNTFStarted.py
        sleep 1
	sudo python ~/EENWebsocketRouter/automation/notifyAsEmail.py
        sleep 0.5
        sudo python ~/EENWebsocketRouter/automation/notifyNTFStopped.py
done