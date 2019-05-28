
import websocket
import time

import binascii
import setproctitle

from BBResponse import BBResponse
from kafka import KafkaConsumer
from EENKafkaConnector import Producer

setproctitle.setproctitle("alrm")

ws = websocket.create_connection('ws://localhost:80')

consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                                 auto_offset_reset='latest')

consumer.subscribe(['Data4mGeoEventServer','Message4mGeoEventServer'])

for message in consumer:

	msg = str(message.value)
    	msg = msg.replace(';','')

	bb = BBResponse()
	binary_rspnse, deviceStatus, end = bb.getResponseMSG(message.topic,msg)
	
	ws.send_binary(binary_rspnse)

ws.close()
    
    
