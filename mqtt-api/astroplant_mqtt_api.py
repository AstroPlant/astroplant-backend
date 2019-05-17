#!/usr/bin/env python3

"""
AstroPlant MQTT API.

Connects MQTT and Kafka.
"""

import os
import paho.mqtt.client as mqtt
from kafka import KafkaProducer
import fastavro
import json
from io import BytesIO
import logging


class UnrecognizedTopicError(ValueError):
    def __init__(self, topic):
        self.topic = topic


class AvroDecoderError(ValueError):
    def __init__(self, kit_serial):
        self.kit_serial = kit_serial


class Server(object):
    """
    The MQTT API server.
    """

    def __init__(self, host, port, username, password, kafka_producer,
                 keepalive=60):
        self._host = host
        self._port = port
        self._keepalive = keepalive
        self._kafka_producer = kafka_producer
        self._message_id = 0

        self.connected = False

        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_disconnect = self._on_disconnect
        self._mqtt_client.on_message = self._on_message_wrap

        self._mqtt_client.reconnect_delay_set(min_delay=1, max_delay=128)

        with open('./schema/aggregate-measurement.avsc', 'r') as f:
            self._aggregate_schema = fastavro.parse_schema(json.load(f))

        with open('./schema/raw-measurement.avsc', 'r') as f:
            self._raw_schema = fastavro.parse_schema(json.load(f))

        self._mqtt_client.username_pw_set(
            username=username,
            password=password
        )


    def start(self):
        """
        Start the client. Blocking.
        """
        logger.info("Server starting.")
        logger.debug(f"MQTT connecting to {self._host}:{self._port}.")
        self._mqtt_client.connect(
            host=self._host,
            port=self._port,
            keepalive=self._keepalive,
        )
        self._mqtt_client.loop_forever()
        logger.info("MQTT stopped.")

    def stop(self):
        """
        Stop the client background thread.
        """
        self._mqtt_client.loop_stop()

    def _on_connect(self, client, user_data, flags, rc):
        logger.info("MQTT connected.")
        self.connected = True
        # Subscribe to multiple topics.
        # Use QoS=2 to ensure exactly once delivery from the broker.
        self._mqtt_client.subscribe([
            ('kit/+/measurement/raw', 2),
            ('kit/+/measurement/aggregate', 2)
        ])

    def _on_disconnect(self, client, user_data, rc):
        logger.info("MQTT disconnected.")
        self.connected = False

    def _on_message_wrap(self, *args, **kwargs):
        self._message_id += 1
        try:
            self._on_message(*args, message_id=self._message_id, **kwargs)
        except (KeyboardInterrupt, SystemExit):
            raise
        except UnrecognizedTopicError as e:
            logger.warning(
                f"Message {self._message_id}: "
                f"unrecognized MQTT topic: {e.topic}"
            )
        except AvroDecoderError as e:
            logger.warning(
                f"Message {self._message_id}: "
                f"malformed avro message, from: {e.kit_serial}"
            )
        except:
            logger.exception(
                f"Message {self._message_id}: "
                "unexpected exception caught in message handler."
            )

    def _on_message(self, client, user_data, msg, message_id):
        logger.debug(f"Message {message_id}: '{msg.topic}': {msg.payload}")

        topic = msg.topic.split("/")
        payload = BytesIO(msg.payload)

        if (
                len(topic) != 4
                or topic[0] != 'kit'
                or topic[2] != 'measurement'
                or not topic[3] in ['raw', 'aggregate']
        ):
            raise UnrecognizedTopicError(msg.topic)

        kit_serial = topic[1]
        message_type = topic[3]
        pipeline = {
                'raw': {
                    'avro_schema': self._raw_schema,
                    'kafka_topic': 'raw-schema'
                },
                'aggregate': {
                    'avro_schema': self._aggregate_schema,
                    'kafka_topic': 'aggregate-schema'
                }
        }

        try:
            message = fastavro.schemaless_reader(payload, pipeline[message_type]['avro_schema'])
        except:
            raise AvroDecoderError(kit_serial)

        message['kit_serial'] = kit_serial
        logger.debug(f"Message {message_id}: decoded {message}")

        msg = BytesIO()
        fastavro.schemaless_writer(
            msg,
            pipeline[message_type]['avro_schema'],
            message
        )

        result = self._kafka_producer.send(
            topic=pipeline[message_type]['kafka_topic'],
            value=msg.getvalue(),
        )
        result.add_callback(
            lambda res: logger.debug(
                f"Message {message_id}: successfully sent to Kafka. "
                f"Partition: {res.partition}. "
                f"Offset: {res.offset}."
            )
        )
        result.add_errback(
            lambda err: logger.warning(
                f"Message {message_id} could not be sent to Kafka: {err}"
            )
        )


if __name__ == "__main__":
    logger = logging.getLogger('astroplant.mqtt_api')
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO')))

    formatter = logging.Formatter(
        '%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s'
    )

    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.debug("Creating Kafka producer.")
    kafka_host = os.environ.get('KAFKA_HOST', 'kafka.ops')
    kafka_port = os.environ.get('KAFKA_PORT', '9092')
    kafka_username = os.environ.get('KAFKA_USERNAME')
    kafka_password = os.environ.get('KAFKA_PASSWORD')

    logger.info(f"Kafka bootstrapping to {kafka_host}:{kafka_port}.")
    kafka_producer = KafkaProducer(
        bootstrap_servers=f"{kafka_host}:{kafka_port}",
        client_id="astroplant-mqtt-kafka-connector",
        acks=1, # Topic leader must acknowledge our messages.
        security_protocol="SASL_PLAINTEXT" if kafka_username else "PLAINTEXT",
        sasl_mechanism="PLAIN" if kafka_username else None,
        sasl_plain_username=kafka_username,
        sasl_plain_password=kafka_password
    )

    logger.debug('Creating server.')
    server = Server(
        host=os.environ.get('MQTT_HOST', 'mqtt.ops'),
        port=int(os.environ.get('MQTT_PORT', '1883')),
        username=os.environ.get('MQTT_USERNAME', 'server'),
        password=os.environ.get('MQTT_PASSWORD', ''),
        kafka_producer=kafka_producer
    )

    server.start()
