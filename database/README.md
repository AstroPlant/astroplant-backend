# AstroPlant Database
This package contains the AstroPlant database specification and utilities. This package will also contain database migration scripts to update between official releases.

## Utilities
The `astroplant-database` program provides utilities to create the AstroPlant database.

To create a database and insert AstroPlant's quantity types and peripheral device definitions into it, run:

```shell
$ export DATABASE_URL=postgres+psycopg2://astroplant:password@database-host/astroplant
$ astroplant-database create-schema
$ astroplant-database insert-definitions --simulation-definitions
```

## Specification
The package provides a SqlAlchemy ORM mapping of the AstroPlant data models.
It also provides a convenience thread-safe session factory for database connections.
They can be used in Python code:

```python
import astroplant_database.specification as d

db = d.DatabaseManager("postgres+psycopg2://astroplant:astroplant@localhost/astroplant")

kit = db.Session.query(d.Kit).filter(d.Kit.serial == "k-abc-def-ghi").one()
```

# Installing the module
To install the Python package using pip, run:

```shell
$ pip install "git+https://github.com/AstroPlant/astroplant-backend.git#egg=astroplant-database&subdirectory=database"
```

# Installing the module for development
Inside the `astroplant-backend/database` directory:

```shell
$ pip install -e .
```

This installs the Python package as editable and makes the `astroplant-database` program available.


# Configuration
Set environment variables to configure the program.

| Variable | Description | Default |
|-|-|-|
| `DATABASE_URL` | The connection URL of the database. | `postgres+psycopg2://astroplant:astroplant@localhost/astroplant` |
| `LOG_LEVEL` | The minimum level of logs shown. One of `DEBUG`, `INFO`, `WARNING`, `ERROR`. | `INFO` |

