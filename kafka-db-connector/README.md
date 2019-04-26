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

```
export DOCKER_ID_USER="salekd"
docker login https://index.docker.io/v1/

docker build . -f Dockerfile -t astroplant-kafka2db
docker tag astroplant-kafka2db $DOCKER_ID_USER/astroplant-kafka2db:0.0.1
docker push $DOCKER_ID_USER/astroplant-kafka2db:0.0.1
```

```
mkvirtualenv astroplant
pip install -r requirements.txt

workon astroplant

source env.sh
python connector/connector.py setup-schema
python connector/connector.py insert-develop-data
python connector/connector.py run
```
