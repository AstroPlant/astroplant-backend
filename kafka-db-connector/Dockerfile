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

RUN apk add --update --no-cache --virtual .fetch-deps \
    postgresql-dev gcc python3-dev musl-dev

ADD requirements.txt /
ADD connector /
ADD schema /

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENV DATABASE_HOST=postgresql-postgresql.default.svc.cluster.local
ENV DATABASE_PORT=5432
ENV DATABASE_USERNAME=
ENV DATABASE_PASSWORD=
ENV DATABASE_DATABASE=astroplant
ENV KAFKA_HOST=kafka-headless.default.svc.cluster.local
ENV KAFKA_PORT=31090
ENV KAFKA_USERNAME=
ENV KAFKA_PASSWORD=
ENV KAFKA_CONSUMER_GROUP=server-aggregate-group
ENV SCHEMA_REGISTRY_URL=http://schema-registry-cp-schema-registry.default.svc.cluster.local:8081  

CMD [ "python", "connector.py", "run", "--stream", "aggregate" ]
