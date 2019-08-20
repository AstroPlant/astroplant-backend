#!/usr/bin/env python3

"""
This program consumes messages from the Kafka measurement message queue,
and inserts them into the PostgreSQL database.
"""

import os
import logging
import click
import datetime
import database as d
import sys


def utc_from_millis(t):
    return datetime.datetime.fromtimestamp(t / 1000, datetime.timezone.utc)


def _run_connector(db, kafka_consumer, stream_type):
    """
    :param db: A SQLAlchemy database handle.
    :param kafka_consumer: A KafkaConsumer subscribed to a topic.
    :param stream_type: Must be either 'aggregate' or 'raw'.
    """
    import fastavro
    from io import BytesIO
    import json
    from sqlalchemy.orm.exc import NoResultFound

    if stream_type == 'aggregate':
        schema_file_name = './schema/aggregate-measurement.avsc'
    elif stream_type == 'raw':
        schema_file_name = './schema/raw-measurement.avsc'

    with open(schema_file_name, 'r') as f:
        schema = fastavro.parse_schema(json.load(f))

    for record in kafka_consumer:
        payload = BytesIO(record.value)
        try:
            msg = fastavro.schemaless_reader(payload, schema)
            logger.debug(f"Received message from Kafka: {msg}")
        except:
            # Could not decode message.
            logger.warning(f"Could not decode message: {payload}")
            continue

        try:
            kit = (
                db.Session
                .query(d.Kit)
                .filter(d.Kit.serial==msg['kit_serial'])
                .one()
            )

            peripheral = (
                db.Session
                .query(d.Peripheral)
                .filter(
                    d.Peripheral.name==msg['peripheral'],
                    d.Peripheral.kit==kit
                )
                .one()
            )

            qt = (
                db.Session
                .query(d.QuantityType)
                .filter(
                    d.QuantityType.physical_quantity==msg['physical_quantity'],
                    d.QuantityType.physical_unit==msg['physical_unit']
                )
                .one()
            )

            if stream_type == 'aggregate':
                measurement = d.AggregateMeasurement(
                    kit=kit,
                    peripheral=peripheral,
                    quantity_type=qt,
                    aggregate_type=msg['type'],
                    value=msg['value'],
                    start_datetime=utc_from_millis(msg['start_datetime']),
                    end_datetime=utc_from_millis(msg['end_datetime']),
                )
            elif stream_type == 'raw':
                measurement = d.RawMeasurement(
                    kit=kit,
                    peripheral=peripheral,
                    quantity_type=qt,
                    value=msg['value'],
                    datetime=utc_from_millis(msg['datetime']),
                )
            logger.debug(f"Measurement modeled as: {measurement.__dict__}")
            db.Session.add(measurement)
            db.Session.commit()
            logger.debug(f"Measurement committed to database.")

            # Commit the offest manually after the message has been successfully processed.
            kafka_consumer.commit()
        except NoResultFound:
            # Malformed measurement. Perhaps using an old kit configuration?
            logger.warning(
                "Message not compatible with database (wrong config?): "
                f"{msg}"
            )
        except KeyError:
            # Malformed measurement. Not all required keys were available.
            # This indicates a serious logic error, as the message corresponds
            # to the Avro schema. As such, this case should never happen.
            logger.exception(
                "Unexpected invalid data in well-formed message: "
                f"{payload}"
            )

            # Commit the offest manually in case the message cannot be processed.
            # In this way, the consumer will proceed towards the next message.
            kafka_consumer.commit()
        except:
            logger.exception(
                f"Message {msg}: "
                "unexpected exception caught in message handler."
            )


def _db_handle():
    return d.DatabaseManager(
        host=os.environ.get('DATABASE_HOST', 'database.ops'),
        port=int(os.environ.get('DATABASE_PORT', '5432')),
        username=os.environ.get('DATABASE_USERNAME', 'astroplant'),
        password=os.environ.get('DATABASE_PASSWORD', 'astroplant'),
        database=os.environ.get('DATABASE_DATABASE', 'astroplant'),
    )


@click.group()
def cli():
    pass


@cli.command()
def setup_schema():
    """
    Set up the database schema.
    """
    db = _db_handle()
    db.setup_schema()


@cli.command()
def insert_develop_data():
    """
    Insert data for development into the database. The development data includes
    a kit configured for a simulated environment.
    """
    db = _db_handle()
    db.insert_develop_data()


@cli.command()
@click.option('-s', '--stream', 'stream_type', default='aggregate',
              show_default=True, type=click.Choice(['raw', 'aggregate']))
def run(stream_type):
    """
    Run the measurements connector.
    :param stream: Which measurements stream to consume from Kafka and input to
    the database.
    """
    from kafka import KafkaConsumer

    logger.info(f"Running {stream_type} connector.")

    logger.debug("Creating Kafka consumer.")
    kafka_host = os.environ.get('KAFKA_HOST', 'kafka.ops')
    kafka_port = int(os.environ.get('KAFKA_PORT', '9092'))
    kafka_username = os.environ.get('KAFKA_USERNAME')
    kafka_password = os.environ.get('KAFKA_PASSWORD')
    kafka_consumer_group = os.environ.get('KAFKA_CONSUMER_GROUP')

    logger.info(f"Kafka bootstrapping to {kafka_host}:{kafka_port}.")
    logger.info(f"Kafka consumer group: {kafka_consumer_group}.")

    # Kafka consumer configuration
    # - Consume earliest available message.
    # - It is recommended to set the offest manually after the message has been processed.
    # - Authentication is optional.
    kafka_consumer = KafkaConsumer(
        f'{stream_type}',
        bootstrap_servers=[f'{kafka_host}:{kafka_port}'],
        group_id=kafka_consumer_group,
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        security_protocol="SASL_PLAINTEXT" if kafka_username else "PLAINTEXT",
        sasl_mechanism="PLAIN" if kafka_username else None,
        sasl_plain_username=kafka_username,
        sasl_plain_password=kafka_password
    )

    db = _db_handle()
    _run_connector(db, kafka_consumer, stream_type)


if __name__ == '__main__':
    logger = logging.getLogger("astroplant.kafka_db_connector")
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO')))

    formatter = logging.Formatter(
        '%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s'
    )

    ch.setFormatter(formatter)
    logger.addHandler(ch)

    cli()
