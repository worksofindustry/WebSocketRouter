'''
Saurav Acharya @ Gas Technology Institute
'''
import websocket
import time
import binascii

from kafka import KafkaConsumer

consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                                 auto_offset_reset='earliest')
consumer.subscribe(['Data4mBlackbox','SystemConfig4mBlackbox'])

_deviceLastConnected = {}
_deviceOnelineStatus = {}
_deviceDataCount = {}
_deviceLastSeen = {}


for message in consumer:
	msg = str(message.value)
    	msg = msg.replace(';','')
	deviceId = ''

    	if message.topic == 'Data4mBlackbox':
		application, messageId, deviceId, longtitude, latitude, altitude, numStats, fixQual,\
    		speed, dateTime, bearing, accelX, accelY, accelZ, orientX, orientY, orientZ, gyroX, gyroY,\
    		gyroZ, temperature, cellSignal, updateRate, status = msg.split(",")
	elif message.topic == 'SystemConfig4mBlackbox':
    		application, messageId, deviceId, imie, simId, deviceName, deviceModel, deviceManufacture,\
    		versionHardware, versionSoftware, dateTime = msg.split(",")
	else:
		print 'Unhandled exception'
	
	if deviceId == '' or updateRate == '':
		continue

	bb = deviceId2BB.get(deviceId,None)
	if not bb:
		bb = BBResponse()

	binary_rspnse = bb.getResponseMSG(message.topic,msg)
	deviceId2BB[deviceId] = bb
