'''
	By: Saurav Acharya @ Gas Technology Institute
'''
import json
import struct
import binascii
import datetime

from collections import OrderedDict

class PayloadBB:

	def __init__(self, binary_msg, device_list):
		self.__decodedMSG = ''
		self.__messageId = ''
                self.__deviceId = ''
                self.__alarm = False
		self.__application = 'DEV' # default
		
		if self.__isBinary(binary_msg):
			self.__parse(binary_msg, device_list) 

	def __isBinary(self, binary_msg):
		try:
			if "\0" in binary_msg:
				return True
	        except Exception:
			return False
		return False

	def __intArray2String(self, intArray):
    		decoded_string = ''
    		for intV in intArray:
        		char=chr(intV)
        		if "\0" in char or "\r" in char:
            			return decoded_string
        		decoded_string+=char
            
    		return decoded_string

        def __toGeoEventText(self, msg_dict):
		return ','.join(msg_dict.values()) + ';'

	'''
		parse binary message
	'''
	def __parse(self, binary_msg, device_list):
		try:
			bin_msg_len = len(binary_msg)

			# find the type of message
			if bin_msg_len == 83: # 1. data payload
				self.__decodedMSG = self.__parseData(binary_msg, device_list)
				self.__messageId = '1'

			elif bin_msg_len == 106: # 2. system configuration message
				self.__decodedMSG = self.__parseSystemConfig(binary_msg, device_list)
			        self.__messageId = '2'

			elif bin_msg_len == 9: # 4. response message
				self.__decodedMSG = self.__parseResponse(binary_msg)
				self.__messageId  = '129'

	    	except Exception:
			print len(binary_msg), '---', 'exception raised'
	    		pass

	''' 
		data payload
	'''	
	def __parseData(self, binary_msg, device_list):

	    # decode and create dictionary
	    msg_dict = OrderedDict()

	    messageId, padding, deviceId, longitude, latitude, altitude, numStats, \
            fixQual, speed, dateTimeYear, dateTimeMonth, dateTimeDay, \
            dateTimeHour, dateTimeMin, dateTimeSec, bearing, accelX, \
            accelY, accelZ, orientX, orientY, orientZ, gyroX, gyroY, gyroZ, \
            temperature, cellSignal, updateRate, status = struct.unpack('<BBI2df2Bf6B10fbBHB', binary_msg)

            self.__deviceId = str(deviceId)

	    # get deployed utility name
	    if self.__deviceId in device_list:
        	self.__application = device_list.get(self.__deviceId)

	    # massage field values for GEN
            longitude = format(longitude, '.6f')
            latitude = format(latitude, '.6f')
            altitude = int(altitude)
            speed = format(speed, '.1f')
            bearing = format(bearing, '.3f')
            accelX = format(accelX, '.3f')
            accelY = format(accelY, '.3f')
            accelZ = format(accelZ, '.3f')
            orientX = format(orientX, '.3f')
            orientY = format(orientY, '.3f')
            orientZ = format(orientZ, '.3f')
            gyroX = format(gyroX, '.3f')
            gyroY = format(gyroY, '.3f')
            gyroZ = format(gyroZ, '.3f')

	    # add to dictionary
	    msg_dict['application'] = self.__application
            msg_dict['messageId'] = str(messageId)
            msg_dict['deviceId'] = str(deviceId)
            msg_dict['longitude'] = str(longitude)
            msg_dict['latitude'] = str(latitude)
            msg_dict['altitude'] = str(altitude)
            msg_dict['numSats'] = str(numStats)
            msg_dict['fixQual'] = str(fixQual)
            msg_dict['speed'] = str(speed)
            msg_dict['dateTime'] = str(dateTimeMonth)+'/'+str(dateTimeDay)+'/'+str(dateTimeYear)+' '+str(dateTimeHour)+':'+str(dateTimeMin)+':'+str(dateTimeSec)
            msg_dict['bearing'] = str(bearing)
            msg_dict['accelX'] = str(accelX)
            msg_dict['accelY'] = str(accelY)
            msg_dict['accelZ'] = str(accelZ)
            msg_dict['orientX'] = str(orientX)
            msg_dict['orientY'] = str(orientY)
            msg_dict['orientZ'] = str(orientZ)
            msg_dict['gyroX'] = str(gyroX)
            msg_dict['gyroY'] = str(gyroY)
            msg_dict['gyroZ'] = str(gyroZ)
            msg_dict['temperature'] = str(temperature)
            msg_dict['cellSignal'] = str(cellSignal)
            msg_dict['updateRate'] = str(updateRate)
	    msg_dict['status'] = str(status)
            
	    if status == 0:
	    	msg_dict['status'] = ''	
	    elif status == 1:
            	msg_dict['status'] = 'AL'
            elif status == 2:
            	msg_dict['status'] = 'SL'
            elif status == 3:
            	msg_dict['status'] = 'AL-SL'
            elif status == 4:
            	msg_dict['status'] = 'DI'
            elif status == 5:
            	msg_dict['status'] = 'DI-AL'
            elif status == 6:
            	msg_dict['status'] = 'DI-SL'
            elif status == 7:
            	msg_dict['status'] = 'DI-AL-SL'
	    
            # create json
            #return json.dumps(msg_dict)
            return self.__toGeoEventText(msg_dict)   

	'''
		system configuration message
	'''
	def __parseSystemConfig(self, binary_msg, device_list):

	    # decode and create dictionary
	    msg_dict = OrderedDict()

	    data = struct.unpack('<2BI96B2H', binary_msg)

	    self.__deviceId = str(data[2])

	    # get deployed utility name
	    if self.__deviceId in device_list:
        	self.__application = device_list.get(self.__deviceId)

            msg_dict['application'] = self.__application
	    msg_dict['messageId'] = str(data[0])
	    msg_dict['deviceId'] = str(data[2])
	    msg_dict['imie'] = self.__intArray2String(data[3:18])
	    msg_dict['simId'] = self.__intArray2String(data[19:38])
	    msg_dict['deviceName'] = self.__intArray2String(data[39:59])
	    msg_dict['deviceModel'] = self.__intArray2String(data[59:79])
	    msg_dict['deviceManufacture'] = self.__intArray2String(data[79:99])
	    msg_dict['versionHardware'] = str(data[99])
	    msg_dict['versionSoftware'] = str(data[100])
	    d_utc = datetime.datetime.utcnow()
            msg_dict['dateTime'] = str(d_utc.month) + '/'+ str(d_utc.day) + '/' + str(d_utc.year) + ' ' + str(d_utc.hour)+':'+str(d_utc.minute)+':'+str(d_utc.second)

	    # create json
            #return json.dumps(msg_dict)
            # return GeoEventText
            return self.__toGeoEventText(msg_dict)

        '''
		Response
        '''
        def __parseResponse(self, binary_msg):
            # decode and create dictionary
	    msg_dict = OrderedDict()

	    messageId,padding,deviceId,updateRate,command = struct.unpack('<BBIHB', binary_msg)
            msg_dict['messageId'] = str(messageId)
	    msg_dict['padding'] = str(padding)
	    msg_dict['deviceId'] = str(deviceId)
	    msg_dict['updateRate'] = str(updateRate)
	    msg_dict['command'] = str(command)

            self.__deviceId = str(deviceId)
            if command == 2 or command == 5:
		self.__alarm = True
	    elif command == 3:
		self.__alarm = False

	    return self.__toGeoEventText(msg_dict)

	'''
		return payload
	'''
	def payload(self):
		return self.__decodedMSG

	'''
		return messageId
	'''
	def messageId(self):
		return self.__messageId

        '''
		return deviceId
	'''
	def deviceId(self):
		return self.__deviceId

        '''
               return alarm status
        '''
	def isAlarmOn(self):
		return self.__alarm

	'''
		return deployed utility/application name
	'''
	def application(self):
		return self.__application
