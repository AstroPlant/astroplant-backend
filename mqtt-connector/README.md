# AstroPlant MQTT connector
This program processes messages from AstroPlant kits over MQTT.
Measurements are sent by kits to an MQTT topic specific to---and only writable by---that kit: `kit/<serial>/measurements/aggregate`.
This program enforces the correct kit IDs are in the measurement and subsequently either enters the message into the database or passes the message on to Kafka.

# Installing the module for development
Inside the `astroplant-backend/mqtt_connector` directory:

```shell
$ pip install -r requirements.txt
$ pip install -e .
```

Note the `pip install -r requirements.txt` step. This installs the `astroplant-database` package from `../database`, relative to this package. To also install that package as editable, instead run `pip install -e ../database`.

This installs the Python package as editable and makes the `astroplant-mqtt-connector` program available.

# Running the connector
To run the connector, listening to MQTT and entering messages directory into the database, execute:

```shell
$ astroplant-mqtt-connector to-database
```

To pass messages on to Kafka instead, and letting a different program handle insertion into the database, execute:

```shell
$ astroplant-mqtt-connector to-kafka
```

# Configuration
Set environment variables to configure the program.

| Variable | Description | Default |
|-|-|-|
| `MQTT_HOST` | The hostname of the MQTT broker. | `localhost` |
| `MQTT_PORT` | The port of the MQTT broker. | `1883` |
| `MQTT_USERNAME` | The username for MQTT authentication. | `server` |
| `MQTT_PASSWORD` | The password for MQTT authentication. | |
| `DATABASE_URL` | The connection URL for the database. | `postgres+psycopg2://astroplant:astroplant@localhost/astroplant` |
| `KAFKA_HOST` | The hostname of one Kafka broker in the cluster. | `localhost` |
| `KAFKA_PORT` | The port of the Kafka broker. | `9092` |
| `KAFKA_USERNAME` | The username for plain sasl authentication. | |
| `KAFKA_PASSWORD` | The password for plain sasl authentication. | |
| `LOG_LEVEL` | The minimum level of logs shown. One of `DEBUG`, `INFO`, `WARNING`, `ERROR`. | `INFO` |

# Dockerfile
The Dockerfile in this directory assumes the build context is at the root of the repository.
In `./astroplant-backend` you can run: `$ docker build -f mqtt-connector/Dockerfile .`
