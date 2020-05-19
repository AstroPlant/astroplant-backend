FROM python:3.7

RUN apt-get update && apt-get install capnproto librdkafka-dev libpq-dev -y

COPY ./database ./database
COPY ./mqtt-connector ./mqtt-connector

WORKDIR ./mqtt-connector

RUN pip install -r requirements.txt
RUN pip install -e .

CMD [ "astroplant-mqtt-connector", "to-database" ]
