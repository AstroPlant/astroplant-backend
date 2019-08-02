#!/usr/bin/env python3

import fastavro
import json
from io import BytesIO

with open('../mqtt-api/schema/aggregate-measurement.avsc', 'r') as f:
    aggregate_schema = fastavro.parse_schema(json.load(f))
print(aggregate_schema)

with open('example-aggregate.json', 'r') as f:
    msg_json = json.load(f)
print(msg_json)

stream = BytesIO()
fastavro.schemaless_writer(stream, aggregate_schema, msg_json)
msg_encoded = stream.getvalue()
print(msg_encoded)

stream = BytesIO(msg_encoded)
msg_json = fastavro.schemaless_reader(stream, aggregate_schema)
print(msg_json)
