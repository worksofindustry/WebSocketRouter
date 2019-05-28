#!/bin/bash
clear

while true;do
        echo "Killing existing ALRM process"
	sudo pkill alrm
        sleep 1
        echo "Starting new ALRM process"
        sudo python ~/EENWebsocketRouter/automation/notifyALRMStarted.py
        sleep 1
	sudo python ~/EENWebsocketRouter/src/Alarm2BB.py
        sleep 0.5
        sudo python ~/EENWebsocketRouter/automation/notifyALRMStopped.py
done
