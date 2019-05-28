'''
Gas Technology Institute
'''
import signal
import sys
import ssl
import json
import csv
import time

import binascii
import struct

import setproctitle

from EENWebSocketServer import WebSocket, EENWebSocketServer, EENSSLWebSocketServer
from optparse import OptionParser

from EENKafkaConnector import Producer
from PayloadBB import PayloadBB

setproctitle.setproctitle("wsr")

# constants
_responseMessageId = 129
_updateRate = 5

# list of clients
_clients = []
#deviceID, clients
_devId2clients = {}
# alarm on or not
_alarmOnClients = {}
# production or development
_prodDev = {}

## producers
prod_Data4mBlackbox = Producer("RawData4mBlackbox")
prod_Data4mBlackbox_Dev = Producer("RawData4mBlackbox_Dev")
prod_Data2Blackbox = Producer("Data2Blackbox")
prod_SystemConfig4mBlackbox = Producer("SystemConfig4mBlackbox")

class EENRouter(WebSocket):

  def handleMessage(self):     
    binary_msg = self.data

    # Convert binary message to JSON message
    bb = PayloadBB(binary_msg)
    messageId = bb.messageId()
    deviceId = bb.deviceId()

    # Pass the message to correct topic in A. Kafka
    if messageId == '1' or messageId == '2':

      if messageId == '1':
        if _prodDev.get(deviceId,None) == 'PRODUCTION':
        	prod_Data4mBlackbox.send(bb.payload())
        else:
        	prod_Data4mBlackbox_Dev.send(bb.payload())

      elif messageId == '2':
        prod_SystemConfig4mBlackbox.send(bb.payload())
        _alarmOnClients[deviceId] = False

	# remove previously connected port for the device
        connectedClient = _devId2clients.get(deviceId, None)
      	if connectedClient:
      		for client in _clients:
        		if client.address[0] == connectedClient[0] and client.address[1] == connectedClient[1]:
          			_clients.remove(client)
	print (deviceId, 'connected.', 'Total connections #', len(_clients))
				
      # Send an ACK response message <messageId,padding,deviceId,updateRate,command>
      isAlarmOn = _alarmOnClients.get(deviceId, None)
      if not isAlarmOn:
      	rspnse_bin_msg = struct.pack('<BBIHB',_responseMessageId,1,int(deviceId),_updateRate,3)
      	self.sendMessage(rspnse_bin_msg)

        prod_Data2Blackbox.send(str(_responseMessageId)+',1,'+deviceId+','+str(_updateRate)+',3')

      # Store address
      _devId2clients[deviceId] = self.address

    elif messageId == '129':
      msg2client = _devId2clients.get(deviceId, None)
      if msg2client:
      	for client in _clients:
        	if client.address[0] == msg2client[0] and client.address[1] == msg2client[1]:
          		client.sendMessage(binary_msg)
			_alarmOnClients[deviceId] = bb.isAlarmOn()
				
        		prod_Data2Blackbox.send(bb.payload())

    else:
      # Send an ACK response message <messageId,padding,deviceId,updateRate,command>
      rspnse_bin_msg = struct.pack('<BBIHB',_responseMessageId,1,12345678,_updateRate,3)
      self.sendMessage(rspnse_bin_msg)

  def handleConnected(self):
    try:
    	_clients.append(self)
    except Exception:
	pass


  def handleClose(self):
    try:
    	_clients.remove(self)
    except Exception:
	pass

### usage: python EENRouter.py --run router
if __name__ == "__main__":
  
  prod_Data4mBlackbox = Producer("RawData4mBlackbox")
  prod_Data4mBlackbox_Dev = Producer("RawData4mBlackbox_Dev")
  prod_Data2Blackbox = Producer("Data2Blackbox")
  prod_SystemConfig4mBlackbox = Producer("SystemConfig4mBlackbox")

  # production vs development
  with open('/home/ubuntu/EENWebsocketRouter/settings/Production.csv', mode='r') as infile:
  	reader = csv.reader(infile)
  	_prodDev = {rows[0]:rows[1] for rows in reader}

  parser = OptionParser(usage="usage: %prog [options]", version="%prog 1.0")
  parser.add_option("--host", default='', type='string', action="store", dest="host", help="hostname (localhost)")
  parser.add_option("--port", default=80, type='int', action="store", dest="port", help="port (80)")
  parser.add_option("--run", default='echo', type='string', action="store", dest="run", help="echo, chat")
  parser.add_option("--ssl", default=0, type='int', action="store", dest="ssl", help="ssl (1: on, 0: off (default))")
  parser.add_option("--cert", default='./cert.pem', type='string', action="store", dest="cert", help="cert (./cert.pem)")
  parser.add_option("--ver", default=ssl.PROTOCOL_TLSv1, type=int, action="store", dest="ver", help="ssl version")

  (options, args) = parser.parse_args()

  cls = EENRouter
  if options.run == 'chat':
  	cls = EENChat
  elif options.run == 'echo':
  	cls = EENEcho

  if options.ssl == 1:
  	server = EENSSLWebSocketServer(options.host, options.port, cls, options.cert, options.cert, version=options.ver)
  else:
  	server = EENWebSocketServer(options.host, options.port, cls)

  def close_sig_handler(signal, frame):
  	server.close()
  	sys.exit()

  signal.signal(signal.SIGINT, close_sig_handler)
  server.serveforever()
