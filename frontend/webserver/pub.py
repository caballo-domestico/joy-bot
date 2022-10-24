from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from enum import Enum
import time
import logging
import json

KAFKA_ADDR = 'kafka:9092'

class Topic(Enum):
    PRESCRIPTION_UPLOADED = 'prescription_uploaded'

class Publisher(KafkaProducer):

    def __init__(self):
        connected = False
        while not connected:
            try:
                super().__init__(bootstrap_servers=KAFKA_ADDR,
                         value_serializer=lambda v: bytes(json.dumps(v), "utf-8"),
                         client_id="webserver")
                connected = True
            except NoBrokersAvailable:
                logging.info('Waiting for Kafka to be ready...')
                time.sleep(1)