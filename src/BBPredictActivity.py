
import websocket
import time

import binascii

import setproctitle

from BBResponse import BBResponse
from kafka import KafkaConsumer
from EENKafkaConnector import Producer

setproctitle.setproctitle("prs")

consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                                 auto_offset_reset="latest")
consumer.subscribe(['RawData4mBlackbox', 'RawData4mBlackbox_Dev'])

deviceId2BB = {}

prod_ActivityPrediction4mAlgorithm = Producer("ActivityPrediction4mAlgorithm")
prod_Data4mBlackbox = Producer("Data4mBlackbox")
prod_Data4mBlackbox_Dev = Producer("Data4mBlackbox_Dev")

for message in consumer:

	# prettify 
	msg = str(message.value)
    	msg = msg.replace(';','')
	msg = msg.replace('\\','')
	msg = msg.replace('\"','')

	deviceId = ''

    	application, messageId, deviceId, longtitude, latitude, altitude, numStats, fixQual,\
    	speed, dateTime, bearing, accelX, accelY, accelZ, orientX, orientY, orientZ, gyroX, gyroY,\
    	gyroZ, temperature, cellSignal, updateRate, status = msg.split(",")
	
	bb = deviceId2BB.get(deviceId,None)
	if not bb:
		bb = BBResponse()
	
	binary_rspnse, deviceStatus, end = bb.getResponseMSG(message.topic,msg)

	deviceId2BB[deviceId] = bb

	# add device status
	if message.topic == 'RawData4mBlackbox':
		prod_Data4mBlackbox.send(msg+','+deviceStatus+';')
	elif message.topic == 'RawData4mBlackbox_Dev':
		prod_Data4mBlackbox_Dev.send(msg+','+deviceStatus+';')


    
    
