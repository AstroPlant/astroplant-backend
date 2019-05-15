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
| `KAFKA_USERNAME` | The username for plain sasl authentication. | |
| `KAFKA_PASSWORD` | The password for plain sasl authentication. | |
| `LOG_LEVEL` | The minimum level of logs shown. One of `DEBUG`, `INFO`, `WARNING`, `ERROR`. | `INFO` |

```shell
$ export DOCKER_ID_USER="salekd"
$ docker login https://index.docker.io/v1/

$ docker build . -f Dockerfile -t astroplant-mqtt2kafka
$ docker tag astroplant-mqtt2kafka $DOCKER_ID_USER/astroplant-mqtt2kafka:0.0.1
$ docker push $DOCKER_ID_USER/astroplant-mqtt2kafka:0.0.1
```

```shell
$ mkvirtualenv astroplant
$ pip install -r requirements.txt

$ workon astroplant

$ source env.sh
$ python astroplant_mqtt_api.py
```
