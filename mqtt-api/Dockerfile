FROM python:3.6.5-alpine3.7

LABEL maintainer="david.salek@surfsara.nl"

RUN apk add --update --no-cache --virtual .fetch-deps \
    gcc libc-dev bash g++ make

RUN wget https://github.com/edenhill/librdkafka/archive/v0.11.6.tar.gz && \
    tar xf v0.11.6.tar.gz && \
    rm v0.11.6.tar.gz && \
    cd librdkafka-0.11.6 && \
    ./configure && \
    make && \
    make install 

ADD requirements.txt /
ADD astroplant_mqtt_api.py /
ADD schema /schema

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENV MQTT_HOST=lb.cluster-astroplant-dev.aws.surfsaralabs.nl
ENV MQTT_PORT=9997
ENV MQTT_USERNAME=
ENV MQTT_PASSWORD=
ENV KAFKA_HOST=kafka-headless.default.svc.cluster.local
ENV KAFKA_PORT=31090
ENV KAFKA_USERNAME=
ENV KAFKA_PASSWORD=
ENV SCHEMA_REGISTRY_URL=http://schema-registry-cp-schema-registry.default.svc.cluster.local:8081  

CMD [ "python", "astroplant_mqtt_api.py" ]
