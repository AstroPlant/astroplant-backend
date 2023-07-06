FROM postgres:12

ENV POSTGRES_USER=astroplant
ENV POSTGRES_PASSWORD=astroplant
ENV POSTGRES_DB=astroplant

RUN apt-get update && apt-get install ca-certificates build-essential python3 python3-pip python3-setuptools python3-dev libpq-dev -y

COPY ./docker/init.sh /docker-entrypoint-initdb.d/init.sh

WORKDIR /usr/src/astroplant-database
COPY . .
RUN pip3 install .[cli]
