# Kafka database connector
This program consumes messages from the Kafka measurement message queue,
and inserts them into the PostgreSQL database.

# Configuration
Set environment variables to configure the program.

| Variable | Description | Default |
|-|-|-|
| `DATABASE_HOST` | The hostname of the database server. | `database.ops` |
| `DATABASE_PORT` | The port of the database server. | `5432` |
| `DATABASE_USERNAME` | The username for database authentication. | `astroplant` |
| `DATABASE_PASSWORD` | The password for database authentication. | `astroplant` |
| `DATABASE_DATABASE` | The name of the AstroPlant database on the server. | `astroplant` |
| `KAFKA_HOST` | The hostname of one Kafka broker in the cluster. | `kafka.ops` |
| `KAFKA_PORT` | The port of the Kafka broker. | `9092` |
| `KAFKA_USERNAME` | The username for plain sasl authentication. | |
| `KAFKA_PASSWORD` | The password for plain sasl authentication. | |
| `KAFKA_CONSUMER_GROUP` | The name of the consumer group for dynamic partition assignment. | |

# Setting up a development enviroment

Create a python environment dedicated to this project.

```shell
mkvirtualenv astroplant
pip install -r requirements.txt
workon astroplant
```

To initialize the database table schemas and add AstroPlant development data, execute:

```shell
$ python connector/connector.py setup-schema
$ python connector/connector.py insert-develop-data
```

# Running the connector
To run the connector, execute:

```shell
$ python connector/connector.py run
```

# Docker

```shell
export DOCKER_ID_USER="salekd"
docker login https://index.docker.io/v1/

docker build . -f Dockerfile -t astroplant-kafka2db
docker tag astroplant-kafka2db $DOCKER_ID_USER/astroplant-kafka2db:0.0.1
docker push $DOCKER_ID_USER/astroplant-kafka2db:0.0.1
```