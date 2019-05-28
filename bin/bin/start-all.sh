#!/bin/bash
clear

echo "Starting ZOOKEEPER services"
nohup sudo ~/zookeeper-3.4.8/bin/zkServer.sh start

sleep 45
echo "Starting KAFKA services"
nohup sudo ~/Kafka/bin/kafka-server-start.sh ~/Kafka/config/server.properties > ~/Kafka/kafka.log 2>&1 &

sleep 3
echo "Starting NOTIFICATION services"
screen -d -m -S NTF bash -c "sleep 0.5; ~/EENWebsocketRouter/bin/start-NTF.sh"

sleep 3
echo "Starting WSR services"
screen -d -m -S WSR bash -c "sleep 0.5; ~/EENWebsocketRouter/bin/start-WSR.sh"

sleep 3
echo "Starting PRS services"
screen -d -m -S PRS bash -c "sleep 0.5; ~/EENWebsocketRouter/bin/start-PRS.sh"

sleep 3
echo "Starting ALRM services"
screen -d -m -S ALRM bash -c "sleep 0.5; ~/EENWebsocketRouter/bin/start-ALRM.sh"

sleep 3
echo "Services running now"

