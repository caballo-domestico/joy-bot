from kafka import KafkaProducer

KAFKA_ADDR = 'kafka:9092'

class Topic(Enum):
    PRESCRIPTION_UPLOADED = 'prescription_uploaded'

class Publisher(KafkaProducer):

    def __init__(self):
        super().__init__(bootstrap_servers=KAFKA_ADDR,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                         client_id="webserver")