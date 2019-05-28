#!/bin/bash
clear

while true;do
        echo "Killing existing PRS process"
	sudo pkill prs
        sleep 1
        echo "Starting new PRS process"
        sudo python ~/EENWebsocketRouter/automation/notifyPRSStarted.py
        sleep 1
	sudo python ~/EENWebsocketRouter/src/BBPredictActivity.py
        sleep 0.5
        sudo python ~/EENWebsocketRouter/automation/notifyPRSStopped.py
done
