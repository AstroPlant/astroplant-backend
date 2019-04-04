# MQTT API
This program processes messages from AstroPlant kits over MQTT.
Measurements are sent by kits to an MQTT topic specific to---and only writable by---that kit: `kit/<serial>/measurements/aggregate`.
This program enforces the correct kit IDs are in the measurement and subsequently passes the message on to Kafka.
