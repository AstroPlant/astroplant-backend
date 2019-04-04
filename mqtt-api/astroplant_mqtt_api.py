import os
import paho.mqtt.client as mqtt
from kafka import KafkaProducer
import fastavro
import json
from io import BytesIO
import logging

class Server(object):
    """
    AstroPlant MQTT API.
    """

    def __init__(self, host, port, username, password, kafka_producer, keepalive=10):
        self._host = host
        self._port = port
        self._keepalive = keepalive
        self._kafka_producer = kafka_producer
        
        self.connected = False

        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_disconnect = self._on_disconnect
        self._mqtt_client.on_message = self._on_message

        self._mqtt_client.reconnect_delay_set(min_delay=1, max_delay=128)

        with open('./schema/aggregate.avsc', 'r') as f:
            self._aggregate_schema = fastavro.parse_schema(json.load(f))

        with open('./schema/stream.avsc', 'r') as f:
            self._stream_schema = fastavro.parse_schema(json.load(f))

        self._mqtt_client.username_pw_set(
            username=username,
            password=password
        )

    def start(self):
        """
        Start the client. Blocking.
        """
        self._mqtt_client.connect(host=self._host, port=self._port, keepalive=self._keepalive)
        self._mqtt_client.loop_forever()

    def stop(self):
        """
        Stop the client background thread.
        """
        self._mqtt_client.loop_stop()

    def _on_connect(self, client, user_data, flags, rc):
        self.connected = True
        self._mqtt_client.subscribe(
            "kit/+/measurement/aggregate",
            qos=2 # Ensure exactly once delivery from the broker.
        )

    def _on_disconnect(self, client, user_data, rc):
        self.connected = False

    def _on_message(self, client, user_data, msg):
        topic = msg.topic.split("/")
        payload = BytesIO(msg.payload)
        
        if (
                len(topic) != 4
                or topic[0] != "kit"
                or topic[2] != "measurement"
                or topic[3] != "aggregate"
        ):
            return
        
        serial = topic[1]
        message = fastavro.schemaless_reader(payload, self._aggregate_schema)
        message['kit_serial'] = serial

        logger.debug(f"Message received and sending to Kafka: {message}")
        
        msg = BytesIO()
        fastavro.schemaless_writer(
            msg,
            self._aggregate_schema,
            message
        )

        self._kafka_producer.send(topic="measurement_aggregate", value=msg.getvalue())

if __name__ == "__main__":
    logger = logging.getLogger("AstroPlant_MQTT_API")
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO')))

    formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')

    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.debug('Creating Kafka producer.')
    kafka_producer = KafkaProducer(
        bootstrap_servers=os.environ.get('KAFKA_SERVER', 'message-broker.ops:9092'),
        client_id="astroplant-mqtt-kafka-connector",
        acks=1 # Topic leader must acknowledge our messages.
    )

    logger.debug('Creating server.')
    server = Server(
        host=os.environ.get('MQTT_HOST', 'mqtt.ops'),
        port=int(os.environ.get('MQTT_PORT', '1883')),
        username=os.environ.get('MQTT_USERNAME', 'server'),
        password=os.environ.get('MQTT_PASSWORD', ''),
        kafka_producer=kafka_producer
    )

    logger.info('Starting.')
    server.start()

