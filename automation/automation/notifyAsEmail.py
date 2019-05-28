'''
@Saurav.Acharya@gastechnology.org
'''
# source: http://stackoverflow.com/questions/25944883/how-to-send-an-email-through-gmail-without-enabling-insecure-access

import base64
import httplib2
import os

import time
import setproctitle

from kafka import KafkaConsumer
from email.mime.text import MIMEText

from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

setproctitle.setproctitle("ntf")

# Path to the client_secret.json file downloaded from the Developer Console
CLIENT_SECRET_FILE = '/home/ubuntu/EENWebsocketRouter/automation/client_secret.json'

# Check https://developers.google.com/gmail/api/auth/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.compose'

def sendMessage(sender, receivers, emailSubject, emailMsg):

	# Location of the credentials storage file
	STORAGE = Storage('/home/ubuntu/EENWebsocketRouter/automation/gmail.storage')

	# Start the OAuth flow to retrieve credentials
	flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
	http = httplib2.Http()

	# Try to retrieve credentials from storage or run the flow to generate them
	credentials = STORAGE.get()
	if credentials is None or credentials.invalid:
  		credentials = run_flow(flow, STORAGE, http=http)

	# Authorize the httplib2.Http object with our credentials
	http = credentials.authorize(http)

	# Build the Gmail service from discovery
	gmail_service = build('gmail', 'v1', http=http)

	# create a message to send
	message = MIMEText(emailMsg)
	message['to'] = ",".join(receivers)
	message['from'] = sender
	message['subject'] = emailSubject

	body = {'raw': base64.b64encode(message.as_string())}

	# send it
	try:
  		message = (gmail_service.users().messages().send(userId="me", body=body).execute())
  		#print('Message Id: %s' % message['id'])
  		#print(message)
	except Exception as error:
  		print('An error occurred: %s' % error)

if __name__ == "__main__":

	consumer = KafkaConsumer(bootstrap_servers='localhost:9092',
                                 auto_offset_reset='smallest')
	consumer.subscribe(['Notification4mSystem'])
        
	sender = "een.server1@gmail.com"
	receivers = ["Saurav.Acharya@GASTECHNOLOGY.ORG","acharyasaurav@gmail.com","Jason.Sphar@GASTECHNOLOGY.ORG","Robert.Marros@GASTECHNOLOGY.ORG"]
	
        last_sent_lookup = {}

	for message in consumer:
		msg = message.value
                msg = msg.replace('"','')
                type, system, notification, timestamp = msg.split(',')
		print msg
		current_sent = time.time()
                last_sent = last_sent_lookup.get(system,None)
		if not last_sent:
			sendMessage(sender, receivers, notification, notification + ' - '+timestamp)
		else:
			if current_sent-last_sent>=60*30:
				sendMessage(sender, receivers, notification, notification + '- '+timestamp)

		last_sent_lookup[system] = current_sent
		
				

		
		
	