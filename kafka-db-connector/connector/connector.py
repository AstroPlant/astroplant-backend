import os
import argparse
import datetime
import database as d


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
        msg = fastavro.schemaless_reader(payload, aggregate_schema)
        print(msg)

        try:
            kit = db.Session\
                    .query(d.Kit)\
                    .filter(d.Kit.serial==msg['kit_serial'])\
                    .one()
            peripheral = db.Session\
                           .query(d.Peripheral)\
                           .filter(
                               d.Peripheral.name==msg['peripheral'],
                               d.Peripheral.kit==kit,
                           )\
                           .one()
            qt = db.Session\
                   .query(d.QuantityType)\
                   .filter(
                       d.QuantityType.physical_quantity==msg['physical_quantity'],
                       d.QuantityType.physical_unit==msg['physical_unit']
                   )\
                   .one()

            measurement = d.Measurement(
                kit=kit,
                peripheral=peripheral,
                quantity_type=qt,
                aggregate_type=msg['type'],
                value=msg['value'],
                start_datetime=utc_from_millis(msg['start_datetime']),
                end_datetime=utc_from_millis(msg['end_datetime']),
            )
            db.Session.add(measurement)
            db.Session.commit()
            print(kit)
            print(peripheral)
        except NoResultFound:
            # Malformed measurement. Perhaps using an old kit configuration?
            pass


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
        from kafka import KafkaConsumer

        kafka_host = os.environ.get('KAFKA_HOST', 'kafka.ops')
        kafka_port = int(os.environ.get('KAFKA_PORT', '9092'))

        kafka_consumer = KafkaConsumer(
            'measurement_aggregate',
            #group_id='db-connector',
            bootstrap_servers=[f'{kafka_host}:{kafka_port}'],
        )

        _run_connector(db, kafka_consumer)
