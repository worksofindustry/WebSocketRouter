*************************************************************************************
Python File Name: PayloadBB.py
Description of File: 
•	Decodes binary message to csv format message
How it works: 
•	Parses the binary message from the black box based on the length of the message. The message can be any of the following – data payload, system configuration, or response message 
•	Calls the appropriate functions to decode the binary message. Decodes binary message from the black box into a csv message delimited by semicolon
Connections to other components (software/scripts) in the ecosystem: 
•	      Not Applicable
*************************************************************************************
Python File Name: EENRouter.py
Description of File: 
•	Acts as the routing protocol between the WebSocket Router and Apache Kafka
How it works: 
•	Creates 4 producer instances that produce data to 4 topics (RawData4mBlackbox, RawData4mBlackbox_Dev, Data2Blackbox, SystemConfig4mBlackbox)
•	Gets a list of the devices deployed and the corresponding utility by reading the Production.csv file
•	Calls the PayloadBB script to decode the binary message. Based on the messageId and the application field values, it produces the decoded message to one of the topics above
Connections to other components (software/scripts) in the ecosystem:
•	References PayloadBB, EENWebSocketServer and EENKafkaConnector scripts
*************************************************************************************
Python File Name: EENKafkaConnector.py
Description of File:
•	Creates a producer instance that can produce data to a topic
How it works:
•	Instantiates a KafkaProducer object that produces the message to a specific topic
Connections to other components (software/scripts) in the ecosystem:
•	      Not Applicable
*************************************************************************************
Python File Name: Classifier.py
Description of File: 
•	Returns the device activity. Brain of the algorithm.
How it works:
•	Preprocessing – Filters the data for any outliers before feature extraction is performed.
•	Feature Extraction - Extracts 6 features (Mean, Median, Minimum, Maximum, Standard Deviation, Energy) for the 3 data fields (defined in BBResponse). A total of 18 features are extracted
•	Classification - Performs some mathematical calculations on the extracted features. Returns the device status (one of IDLE, DIGGING, DRIVING) based on those results and the speed. There are 2 algorithms that do the classification based on where the black box is deployed – 1 for backhoe/excavator and 1 for agricultural equipment. 
Connections to other components (software/scripts) in the ecosystem:
•	      Not Applicable
*************************************************************************************
Python File Name: BBresponse.py
Description of File:
•	Encodes the message to binary format and returns it along with device activity, if applicable
How it works:
•	Receives the csv message and the topic it was consumed on as the input
•	If the topic is either Message4mGeoEventServer or Data4mGeoEventServer, it sets the appropriate command for the alarm and the lights based on the speed and the geo boundaries. Encodes the fields into binary format and returns the binary message.
•	If the topic is either RawData4mBlackbox or RawData4mBlackbox_Dev, it calculates the 3 new data features (accel, orient, gyro) based on 9 DOF values. Adds this new data to the 2- minute rolling window. Calls the Classifier script to predict the activity only after 2 minutes. 
Returns the binary response along with the activity.
•	Dimensionality Reduction – Reduces the data from 9 DOF to 3 (one for accelerometer, one for gyroscope, one for magnetometer)
Connections to other components (software/scripts) in the ecosystem:
•	References Classifier and EENKafkaConnector
*************************************************************************************
Python File Name: BBPredictActivity.py
Description of File:
•	Produces csv format message along with the device activity to the topics that are subscribed by GeoEvent
How it works:
•	Creates a new KafkaConsumer instance that subscribes to 2 topics (RawData4mBlackbox, RawData4mBlackbox_Dev)
•	For each message received on these topics, it calls the BBResponse script to get the device activity
•	Creates 2 producer instances that can produce data to 2 topics (Data4mBlackbox, Data4mBlackbox_Dev). Based on the topic where the initial message was received, it sends the initial message along with the device activity (from BBResponse above) to one of these topics.
Connections to other components (software/scripts) in the ecosystem:
•	References BBResponse and EENKafkaConnector
*************************************************************************************
Python File Name: Alarm2BB.py
Description of File:
•	Encodes the message (regarding alarms and lights) to binary format and sends it over web socket to the black box
How it works:
•	Creates a new KafkaConsumer instance that subscribes to 2 topics (Data4mGeoEventServer, Message4mGeoEventServer)
•	For each message consumed on these topics, it calls the BBResponse script that returns the binary response message
•	Also, a connection to the web socket is created. The binary message gets sent back to the black box over the web socket.
Connections to other components (software/scripts) in the ecosystem:
•	References BBResponse and EENKafkaConnector
*************************************************************************************
