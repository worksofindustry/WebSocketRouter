import binascii
import struct

import numpy as np
import string

from EENKafkaConnector import Producer
from Classifier import Classifier 

class BBResponse:

	def __init__(self):
		self.__window = []
		self.__WINDOWSIZE = 24
		self.__ml_classifier = Classifier(self.__WINDOWSIZE)

	def __addNewData2Window(self, data):
		if len(self.__window)== self.__WINDOWSIZE:
        		self.__window.pop(0)
    		self.__window.append(data)

	def __createResponseMSG(self, deviceId, updateRate, command):
		messageId = 129
		padding = 1
		binary_msg = struct.pack('<BBIHB',messageId,padding,deviceId,updateRate,command)
		return binary_msg
	
        def getResponseMSG(self, topic, message):
		command = 3  # by default ALARM OFF

		deviceStatus = ''
		deviceTime = ''
		binary_response = ''
		
    		if topic == 'Message4mGeoEventServer':
			name, deviceId, speed, updateRate = message.split(",")
			command=3 # ALARM OFF

			updateRate = 5
			# remove non-printable characters
			#updateRate = ''.join(filter(lambda x:x in string.printable, updateRate))

			binary_response = self.__createResponseMSG(int(deviceId), int(updateRate), command)

		elif topic == 'Data4mGeoEventServer':
			name, deviceId, speed, updateRate = message.split(",")
			if float(speed)<=4:
				command=2 # ALARM ON
			
			updateRate = 5
			# remove non-printable characters
			#updateRate = ''.join(filter(lambda x:x in string.printable, updateRate))

			binary_response = self.__createResponseMSG(int(deviceId), int(updateRate), command)

		elif topic == 'RawData4mBlackbox' or topic == 'RawData4mBlackbox_Dev': 
    			application, messageId, deviceId, longtitude, latitude, altitude, numStats, fixQual,\
    			speed, dateTime, bearing, accelX, accelY, accelZ, orientX, orientY, orientZ, gyroX, gyroY,\
    			gyroZ, temperature, cellSignal, updateRate, status = message.split(",")

			# process status
			deviceTime = dateTime

			# calculate accel, orient, gyro
			accel = np.sqrt(float(accelX)*float(accelX)+float(accelY)*float(accelY)+float(accelZ)*float(accelZ))
			orient = np.sqrt(float(orientX)*float(orientX)+float(orientY)*float(orientY)+float(orientZ)*float(orientZ))
			gyro = np.sqrt(float(gyroX)*float(gyroX)+float(gyroY)*float(gyroY)+float(gyroZ)*float(gyroZ))
			
			# new data features
			data9dof = {}
    			data9dof['accel'] = accel
    			data9dof['orient'] = orient
    			data9dof['gyro'] = gyro
			
			# add new data to window
			self.__addNewData2Window(data9dof)
			# classify activities	
			deviceStatus = self.__ml_classifier.classifyActivity(self.__window, speed)
			
		return binary_response, deviceStatus, deviceTime
