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
