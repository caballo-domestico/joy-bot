from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from enum import Enum
import time
import logging
import json

KAFKA_ADDR = None

def setKafkaAddr(addr, port):
    global KAFKA_ADDR
    KAFKA_ADDR = f"{addr}:{port}"

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
                # kafka's not online yet, will retry after a brief pause
                logging.info('Waiting for Kafka to be ready...')
                time.sleep(1)