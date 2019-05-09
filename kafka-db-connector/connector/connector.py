import os
import logging
import argparse
import datetime
import database as d
import sys


logger = logging.getLogger('astroplant.connector.connector')


def utc_from_millis(t):
    return datetime.datetime.fromtimestamp(t / 1000, datetime.timezone.utc)


def _run_connector(db, kafka_consumer):
    from confluent_kafka import KafkaError
    from confluent_kafka.avro.serializer import SerializerError
    from sqlalchemy.orm.exc import NoResultFound

    # Read messages from Kafka, print to stdout
    try:
        while True:
            try:
                msg = kafka_consumer.poll(timeout=1.0)

            except SerializerError as e:
                print("Message deserialization failed for {}: {}".format(msg, e))
                break

            if msg is None:
                continue

            if msg.error():
                # Error or event
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                else:
                    # Error
                    raise KafkaException(msg.error())
            else:
                # Proper message
                sys.stderr.write('%% %s [%d] at offset %d with key %s:\n' %
                                 (msg.topic(), msg.partition(), msg.offset(),
                                  str(msg.key())))
                print(msg.value())

                value = msg.value()

                try:
                    kit = db.Session\
                            .query(d.Kit)\
                            .filter(d.Kit.serial==value['kit_serial'])\
                            .one()
                    peripheral = db.Session\
                                   .query(d.Peripheral)\
                                   .filter(
                                       d.Peripheral.name==value['peripheral'],
                                       d.Peripheral.kit==kit,
                                   )\
                                   .one()
                    qt = db.Session\
                           .query(d.QuantityType)\
                           .filter(
                               d.QuantityType.physical_quantity==value['physical_quantity'],
                               d.QuantityType.physical_unit==value['physical_unit']
                           )\
                           .one()

                    measurement = d.Measurement(
                        kit=kit,
                        peripheral=peripheral,
                        quantity_type=qt,
                        aggregate_type=value['type'],
                        value=value['value'],
                        start_datetime=utc_from_millis(value['start_datetime']),
                        end_datetime=utc_from_millis(value['end_datetime']),
                    )
                    db.Session.add(measurement)
                    db.Session.commit()
                    print(kit)
                    print(peripheral)
                except NoResultFound:
                    # Malformed measurement. Perhaps using an old kit configuration?
                    logger.warn((
                        "Message not compatible with database (wrong config?): "
                        f"{value}"
                    ))
                    pass

                except KeyError:
                    # Malformed measurement. Not all required keys were available.
                    pass

    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')

    finally:
        # Close down consumer to commit final offsets.
        kafka_consumer.close()


if __name__ == '__main__':
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
        from confluent_kafka.avro import AvroConsumer

        kafka_host = os.environ.get('KAFKA_HOST', 'kafka.ops')
        kafka_port = int(os.environ.get('KAFKA_PORT', '9092'))
        kafka_username = os.environ.get('KAFKA_USERNAME')
        kafka_password = os.environ.get('KAFKA_PASSWORD')
        kafka_consumer_group = os.environ.get('KAFKA_CONSUMER_GROUP')
        kafka_topic = os.environ.get('KAFKA_TOPIC')
        schema_registry_url = os.environ.get('SCHEMA_REGISTRY_URL')

        conf = {
            'bootstrap.servers': f'{kafka_host}:{kafka_port}',
            'schema.registry.url': schema_registry_url,
            #'debug': 'security',
            'security.protocol': 'SASL_PLAINTEXT',
            'sasl.mechanisms': 'PLAIN',
            'sasl.username': kafka_username,
            'sasl.password': kafka_password,
            'group.id': kafka_consumer_group,
            'session.timeout.ms': 6000,
            'auto.offset.reset': 'earliest'
        }
        kafka_consumer = AvroConsumer(conf)
        kafka_consumer.subscribe([kafka_topic])

        _run_connector(db, kafka_consumer)
