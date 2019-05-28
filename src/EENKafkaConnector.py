
import threading, logging, time
import json

from kafka import KafkaProducer, KafkaConsumer


class Producer(threading.Thread):

	def __init__(self, topic):
		self.topic = topic

	def send(self, msg):
		producer = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'), 
					bootstrap_servers='localhost:9092')

		producer.send(self.topic, msg)
		producer.flush()