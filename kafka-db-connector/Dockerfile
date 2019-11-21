FROM ubuntu:18.04

LABEL maintainer="david.salek@surfsara.nl"

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN apt-get install -y libpq-dev librdkafka-dev capnproto

ADD requirements.txt /
ADD kafka_db_connector /kafka_db_connector
ADD proto /proto

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENV DATABASE_HOST=postgresql.default.svc.cluster.local
ENV DATABASE_PORT=5432
ENV DATABASE_USERNAME=
ENV DATABASE_PASSWORD=
ENV DATABASE_DATABASE=astroplant
ENV KAFKA_HOST=kafka-cp-kafka-headless.default.svc.cluster.local
ENV KAFKA_PORT=9092
ENV KAFKA_USERNAME=
ENV KAFKA_PASSWORD=
ENV KAFKA_CONSUMER_GROUP=server-aggregate-group

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

CMD [ "python", "kafka_db_connector/connector.py", "run", "--stream", "aggregate" ]
