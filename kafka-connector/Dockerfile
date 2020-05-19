FROM python:3.7

RUN apt-get update && apt-get install capnproto librdkafka-dev libpq-dev -y

COPY ./database ./database
COPY ./kafka-connector ./kafka-connector

WORKDIR ./kafka-connector

RUN pip install -r requirements.txt
RUN pip install -e .

CMD [ "astroplant-kafka-connector", "run", "--stream=aggregate" ]
