#!/bin/bash
clear

echo "Stopping KAFKA services"

sleep 3
echo "Stopping WSR services"
sh ~/EENWebsocketRouter/bin/stop-WSR.sh

sleep 3
echo "Stopping PRS services"
sh ~/EENWebsocketRouter/bin/stop-PRS.sh

sleep 3
echo "Stopping NOTIFICATION services"
sh ~/EENWebsocketRouter/bin/stop-NTF.sh

sleep 3
echo "Stopping ALRM services"
sh ~/EENWebsocketRouter/bin/stop-ALRM.sh

sleep 3
echo "All services stopped"

