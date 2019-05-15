#!/usr/bin/env python3

"""
This program consumes messages from the Kafka measurement message queue,
and inserts them into the PostgreSQL database.
"""

import os
import logging
import argparse
import datetime
import database as d
import sys


def utc_from_millis(t):
    return datetime.datetime.fromtimestamp(t / 1000, datetime.timezone.utc)


def _run_connector(db, kafka_consumer):
    from io import BytesIO
    import json
    from sqlalchemy.orm.exc import NoResultFound
    import fastavro

    with open('./schema/aggregate.avsc', 'r') as f:
        aggregate_schema = fastavro.parse_schema(json.load(f))

    for record in kafka_consumer:
        payload = BytesIO(record.value)
        try:
            msg = fastavro.schemaless_reader(payload, aggregate_schema)
            logger.debug(f"Received message from Kafka: {msg}")
        except:
            # Could not decode message.
            logger.warn(f"Could not decode message: {payload}")

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

            measurement = d.Measurement(
                kit=kit,
                peripheral=peripheral,
                quantity_type=qt,
                aggregate_type=msg['type'],
                value=msg['value'],
                start_datetime=utc_from_millis(msg['start_datetime']),
                end_datetime=utc_from_millis(msg['end_datetime']),
            )
            logger.debug(f"Measurement modeled as: {measurement.__dict__}")
            db.Session.add(measurement)
            db.Session.commit()
            logger.debug(f"Measurement committed to database.")
        except NoResultFound:
            # Malformed measurement. Perhaps using an old kit configuration?
            logger.warn((
                "Message not compatible with database (wrong config?): "
                f"{msg}"
            ))
            pass
        except KeyError:
            # Malformed measurement. Not all required keys were available.
            pass
        except:
            logger.exception(
                f"Message {msg}: "
                "unexpected exception caught in message handler."
            )


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

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'command',
        choices=[
            'setup-schema',
            'insert-develop-data',
            'run',
        ],
    )
    parser.parse_args()
    args = parser.parse_args()

    db = d.DatabaseManager(
        host=os.environ.get('DATABASE_HOST', 'database.ops'),
        port=int(os.environ.get('DATABASE_PORT', '5432')),
        username=os.environ.get('DATABASE_USERNAME', 'astroplant'),
        password=os.environ.get('DATABASE_PASSWORD', 'astroplant'),
        database=os.environ.get('DATABASE_DATABASE', 'astroplant'),
    )
    if args.command == 'setup-schema':
        db.setup_schema()
    elif args.command == 'insert-develop-data':
        db.insert_develop_data()
    elif args.command == 'run':
        from kafka import KafkaConsumer

        logger.debug("Creating Kafka consumer.")
        kafka_host = os.environ.get('KAFKA_HOST', 'kafka.ops')
        kafka_port = int(os.environ.get('KAFKA_PORT', '9092'))
        kafka_username = os.environ.get('KAFKA_USERNAME')
        kafka_password = os.environ.get('KAFKA_PASSWORD')
        kafka_consumer_group = os.environ.get('KAFKA_CONSUMER_GROUP')

        logger.info(f"Kafka bootstrapping to {kafka_host}:{kafka_port}.")
        logger.info(f"Kafka consumer group: {kafka_consumer_group}.")
        kafka_consumer = KafkaConsumer(
            'aggregate-schema',
            bootstrap_servers=[f'{kafka_host}:{kafka_port}'],
            group_id=kafka_consumer_group,
            security_protocol="SASL_PLAINTEXT",
            sasl_mechanism="PLAIN",
            sasl_plain_username=kafka_username,
            sasl_plain_password=kafka_password
        )

        logger.info("Running connector.")
        _run_connector(db, kafka_consumer)
