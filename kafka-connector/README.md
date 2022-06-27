# AstroPlant Kafka connector
This program consumes messages from the Kafka measurement message queue,
and inserts them into the PostgreSQL database.

# Installing the module for development
Inside the `astroplant-backend/kafka_connector` directory:

```shell
$ pip install -r requirements.txt
$ pip install -e .
```

Note the `pip install -r requirements.txt` step. This installs the `astroplant-database` package from `../database`, relative to this package. To also install that package as editable, instead run `pip install -e ../database`.

This installs the Python package as editable and makes the `astroplant-kafka-connector` program available.

# Configuration
Set environment variables to configure the program.

| Variable | Description | Default |
|-|-|-|
| `DATABASE_URL` | The connection URL of the database. | `postgresql+psycopg2://astroplant:astroplant@localhost/astroplant` |
| `KAFKA_HOST` | The hostname of one Kafka broker in the cluster. | `localhost` |
| `KAFKA_PORT` | The port of the Kafka broker. | `9092` |
| `KAFKA_USERNAME` | The username for plain sasl authentication. | |
| `KAFKA_PASSWORD` | The password for plain sasl authentication. | |
| `KAFKA_CONSUMER_GROUP` | The name of the consumer group for dynamic partition assignment. | `astroplant-kafka-connector` |
| `LOG_LEVEL` | The minimum level of logs shown. One of `DEBUG`, `INFO`, `WARNING`, `ERROR`. | `INFO` |


# Running the connector
To run the connector after installation, run e.g.:

```shell
$ astroplant-kafka-connector run --stream=aggregate
```

See `astroplant-kafka-connector --help` for available commands.

# Dockerfile
The Dockerfile in this directory assumes the build context is at the root of the repository.
In `./astroplant-backend` you can run: `$ docker build -f kafka-connector/Dockerfile .`
