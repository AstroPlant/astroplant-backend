FROM ubuntu:18.04

LABEL maintainer="david.salek@surfsara.nl"

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN apt-get install -y librdkafka-dev capnproto

ADD requirements.txt /
ADD mqtt_api /mqtt_api
ADD proto /proto

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENV MQTT_HOST=mosquitto.default.svc.cluster.local
ENV MQTT_PORT=1883
ENV MQTT_USERNAME=
ENV MQTT_PASSWORD=
ENV KAFKA_HOST=kafka-cp-kafka-headless.default.svc.cluster.local
ENV KAFKA_PORT=9092
ENV KAFKA_USERNAME=
ENV KAFKA_PASSWORD=

CMD [ "python", "mqtt_api/astroplant_mqtt_api.py" ]
