#!/usr/bin/env python3

"""
This program consumes messages from the Kafka measurement message queue,
and inserts them into the PostgreSQL database.
"""

import logging
import os
import sys
import datetime
import uuid
import click
import astroplant_database.specification as d


from .schema import astroplant_capnp


logger = logging.getLogger("astroplant_kafka_connector.kafka_listener")


def utc_from_millis(t):
    return datetime.datetime.fromtimestamp(t / 1000, datetime.timezone.utc)


def run_connector(db, kafka_consumer, stream_type):
    """
    :param db: A SQLAlchemy database handle.
    :param kafka_consumer: A KafkaConsumer subscribed to a topic.
    :param stream_type: Must be either 'aggregate' or 'raw'.
    """
    from io import BytesIO
    import json
    from sqlalchemy.orm.exc import NoResultFound

    logger.debug("Connector starting.")

    for record in kafka_consumer:
        payload = record.value
        received_measurement = None
        if stream_type == "aggregate":
            try:
                received_measurement = astroplant_capnp.AggregateMeasurement.from_bytes_packed(
                    payload
                )
            except:
                # Could not decode message.
                logger.warning(f"Could not decode message: {payload}")
                continue
        elif stream_type == "raw":
            try:
                received_measurement = astroplant_capnp.RawMeasurement.from_bytes_packed(
                    payload
                )
            except:
                # Could not decode message.
                logger.warning(f"Could not decode message: {payload}")
                continue

        try:
            kit = (
                db.Session.query(d.Kit)
                .filter(d.Kit.serial == received_measurement.kitSerial)
                .one()
            )
            peripheral = (
                db.Session.query(d.Peripheral)
                .filter(d.Peripheral.id == received_measurement.peripheral)
                .filter(d.Peripheral.kit == kit)
                .one()
            )

            if not kit or not peripheral:
                logger.warning(f"Kit or peripheral not found for message {message_id}")
                continue

            measurement = None
            if stream_type == "aggregate":
                values = {
                    aggregate.type: aggregate.value
                    for aggregate in received_measurement.values
                    if 0 < len(aggregate.type) <= 50
                }

                if 0 < len(values) <= 16:
                    measurement = d.AggregateMeasurement(
                        id=uuid.UUID(bytes=received_measurement.id),
                        kit=kit,
                        kit_configuration=peripheral.kit_configuration,
                        peripheral=peripheral,
                        quantity_type_id=received_measurement.quantityType,
                        datetime_start=utc_from_millis(received_measurement.datetimeStart),
                        datetime_end=utc_from_millis(received_measurement.datetimeEnd),
                        values=values,
                    )
            elif stream_type == "raw":
                measurement = d.RawMeasurement(
                    id=uuid.UUID(bytes=received_measurement.id),
                    kit=kit,
                    kit_configuration=peripheral.kit_configuration,
                    peripheral=peripheral,
                    quantity_type_id=received_measurement.quantityType,
                    value=received_measurement.value,
                    datetime=utc_from_millis(received_measurement.datetime),
                )

            logger.debug(f"Measurement modeled as: {measurement.__dict__}")
            db.Session.add(measurement)
            try:
                db.Session.commit()
                logger.debug(f"Measurement committed to database.")
            except:
                logger.debug(f"Error while committing to database.")
                db.Session.rollback()

            # Commit the offest manually after the message has been successfully processed.
            kafka_consumer.commit()
        except NoResultFound:
            # Malformed measurement. Perhaps using an old kit configuration?
            logger.warning(
                "Message not compatible with database (wrong config?): " f"{payload}"
            )

            # Commit the offest manually in case the message cannot be processed.
            # In this way, the consumer will proceed towards the next message.
            kafka_consumer.commit()
        except KeyError:
            # Malformed measurement. Not all required keys were available.
            # This indicates a serious logic error, as the message corresponds
            # to the Avro schema. As such, this case should never happen.
            logger.exception(
                "Unexpected invalid data in well-formed message: " f"{payload}"
            )

            # Commit the offest manually in case the message cannot be processed.
            # In this way, the consumer will proceed towards the next message.
            kafka_consumer.commit()
        except:
            logger.exception(f"Unexpected exception caught in message handler.")


def _db_handle():
    return d.DatabaseManager(
        host=os.environ.get("DATABASE_HOST", "database.ops"),
        port=int(os.environ.get("DATABASE_PORT", "5432")),
        username=os.environ.get("DATABASE_USERNAME", "astroplant"),
        password=os.environ.get("DATABASE_PASSWORD", "astroplant"),
        database=os.environ.get("DATABASE_DATABASE", "astroplant"),
    )


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "-s",
    "--stream",
    "stream_type",
    default="aggregate",
    show_default=True,
    type=click.Choice(["raw", "aggregate"]),
)
def run(stream_type):
    """
    Run the measurements connector.
    :param stream: Which measurements stream to consume from Kafka and input to
    the database.
    """
    from kafka import KafkaConsumer

    logger.info(f"Running {stream_type} connector.")

    logger.debug("Creating Kafka consumer.")
    kafka_host = os.environ.get("KAFKA_HOST", "kafka.ops")
    kafka_port = int(os.environ.get("KAFKA_PORT", "9092"))
    kafka_username = os.environ.get("KAFKA_USERNAME")
    kafka_password = os.environ.get("KAFKA_PASSWORD")
    kafka_consumer_group = os.environ.get("KAFKA_CONSUMER_GROUP")

    logger.info(f"Kafka bootstrapping to {kafka_host}:{kafka_port}.")
    logger.info(f"Kafka consumer group: {kafka_consumer_group}.")

    # Kafka consumer configuration
    # - Consume earliest available message.
    # - It is recommended to set the offest manually after the message has been processed.
    # - Authentication is optional.
    kafka_consumer = KafkaConsumer(
        f"{stream_type}",
        bootstrap_servers=[f"{kafka_host}:{kafka_port}"],
        group_id=kafka_consumer_group,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        security_protocol="SASL_PLAINTEXT" if kafka_username else "PLAINTEXT",
        sasl_mechanism="PLAIN" if kafka_username else None,
        sasl_plain_username=kafka_username,
        sasl_plain_password=kafka_password,
    )

    db = _db_handle()
    _run_connector(db, kafka_consumer, stream_type)
