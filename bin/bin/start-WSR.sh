#!/bin/bash
clear

while true;do
        echo "Killing existing WSR process"
	sudo kill -9 $(sudo lsof -t -i:80)
        sleep 1
        echo "Starting new WSR process"
        sudo python ~/EENWebsocketRouter/automation/notifyWSRStarted.py
        sleep 1
	sudo python ~/EENWebsocketRouter/src/EENRouter.py --run router
        sleep 0.5
        sudo python ~/EENWebsocketRouter/automation/notifyWSRStopped.py
done
