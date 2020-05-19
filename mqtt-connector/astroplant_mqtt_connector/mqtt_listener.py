"""
AstroPlant MQTT listener.
"""

import os
import logging
import paho.mqtt.client as mqtt
import queue

from .schema import astroplant_capnp


logger = logging.getLogger("astroplant_mqtt_connector.mqtt_listener")


class UnrecognizedTopicError(ValueError):
    def __init__(self, topic):
        self.topic = topic


class CapnpDecoderError(ValueError):
    def __init__(self, kit_serial):
        self.kit_serial = kit_serial


class MqttListener(object):
    """
    The MQTT API server.
    """

    def __init__(self, host, port, username, password, keepalive=60):
        self._host = host
        self._port = port
        self._keepalive = keepalive
        self._message_id = 0

        self.connected = False
        self.message_queue = queue.Queue()

        self._mqtt_client = mqtt.Client()
        self._mqtt_client.on_connect = self._on_connect
        self._mqtt_client.on_disconnect = self._on_disconnect
        self._mqtt_client.on_message = self._on_message_wrap

        self._mqtt_client.reconnect_delay_set(min_delay=1, max_delay=128)

        self._mqtt_client.username_pw_set(username=username, password=password)

    def start(self):
        """
        Start the client. Non-blocking.
        """
        logger.info("Server starting.")
        logger.debug(f"MQTT connecting to {self._host}:{self._port}.")
        self._mqtt_client.connect_async(
            host=self._host, port=self._port, keepalive=self._keepalive,
        )
        self._mqtt_client.loop_start()

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
        self._mqtt_client.subscribe(
            [("kit/+/measurement/raw", 2), ("kit/+/measurement/aggregate", 2)]
        )

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
                f"Message {self._message_id}: " f"unrecognized MQTT topic: {e.topic}"
            )
        except CapnpDecoderError as e:
            logger.warning(
                f"Message {self._message_id}: "
                f"malformed capnp message, from: {e.kit_serial}"
            )
        except:
            logger.exception(
                f"Message {self._message_id}: "
                "unexpected exception caught in message handler."
            )

    def _on_message(self, client, user_data, msg, message_id):
        logger.debug(f"Message {message_id}: '{msg.topic}': {msg.payload}")

        topic = msg.topic.split("/")

        if (
            len(topic) != 4
            or topic[0] != "kit"
            or topic[2] != "measurement"
            or not topic[3] in ["raw", "aggregate"]
        ):
            raise UnrecognizedTopicError(msg.topic)

        kit_serial = topic[1]
        message_type = topic[3]

        message = None
        if message_type == "raw":
            try:
                raw_measurement = astroplant_capnp.RawMeasurement.from_bytes_packed(
                    msg.payload
                )
            except Exception as e:
                raise CapnpDecoderError(kit_serial)
            logger.debug(f"Message {message_id}: decoded {raw_measurement}")
            raw_measurement = astroplant_capnp.RawMeasurement.new_message(
                **raw_measurement.to_dict()
            )
            raw_measurement.kitSerial = kit_serial
            message = raw_measurement
        elif message_type == "aggregate":
            try:
                aggregate_measurement = astroplant_capnp.AggregateMeasurement.from_bytes_packed(
                    msg.payload
                )
            except:
                raise CapnpDecoderError(kit_serial)
            logger.debug(f"Message {message_id}: decoded {aggregate_measurement}")
            aggregate_measurement = astroplant_capnp.AggregateMeasurement.new_message(
                **aggregate_measurement.to_dict()
            )
            aggregate_measurement.kitSerial = kit_serial
            message = aggregate_measurement

        if message is not None:
            self.message_queue.put((message_type, message, message_id), block=True)
