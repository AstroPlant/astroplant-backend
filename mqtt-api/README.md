# MQTT API
This program processes messages from AstroPlant kits over MQTT.
Measurements are sent by kits to an MQTT topic specific to---and only writable by---that kit: `kit/<serial>/measurements/aggregate`.
This program enforces the correct kit IDs are in the measurement and subsequently passes the message on to Kafka.

# Configuration
Set environment variables to configure the program.

| Variable | Description | Default |
|-|-|-|
| `MQTT_HOST` | The hostname of the MQTT broker. | `mqtt.ops` |
| `MQTT_PORT` | The port of the MQTT broker. | `1883` |
| `MQTT_USERNAME` | The username for MQTT authentication. | `server` |
| `MQTT_PASSWORD` | The password for MQTT authentication. | |
| `KAFKA_HOST` | The hostname of one Kafka broker in the cluster. | `kafka.ops` |
| `KAFKA_PORT` | The port of the Kafka broker. | `9092` |
