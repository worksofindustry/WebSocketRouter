import json
import datetime

from kafka import KafkaProducer, KafkaConsumer

producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'), 
					bootstrap_servers='localhost:9092')

type = "service-status"
system = "NTF"
notification = "NTF Service Stopped"
d_utc = datetime.datetime.utcnow()
time = str(d_utc.month) + '/'+ str(d_utc.day) + '/' + str(d_utc.year) + ' ' + str(d_utc.hour)+':'+str(d_utc.minute)+':'+str(d_utc.second) + ' UTC' 

msg = type + ',' + system + ',' + notification + ',' + time  

producer.send("Notification4mSystem", msg)
producer.flush()