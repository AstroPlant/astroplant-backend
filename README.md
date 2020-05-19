# AstroPlant Backend

This repository contains several modules that are part of the AstroPlant back-end.
The modules each have a readme.
The main API, necessary for running the back-end, is available at [astroplant-api](https://github.com/AstroPlant/astroplant-api) repository.
A front-end UI for interacting with the back-end is availabl at the [astroplant-frontend-web](https://github.com/AstroPlant/astroplant-frontend-web) repository.

# Docker Compose
A Docker Compose file to launch a full back-end including the web front-end is available in the `./docker` subdirectory.

To get started quickly, run:

```shell
$ git clone https://github.com/AstroPlant/astroplant-api.git
$ git clone https://github.com/AstroPlant/astroplant-frontend-web.git
$ git clone https://github.com/AstroPlant/astroplant-backend.git
$ cd astroplant-backend/docker
$ docker-compose up
```

Then navigate to `https://localhost:3000` in your browser.

See `./docker` for more details.

# Description of the back-end architecture

The AstroPlant back-end consists of various modules.

Communication between kits and the back-end is over MQTT.
Two modules in the back-end handle the MQTT communication.
Firstly, astroplant-mqtt-connector---in this repository at `./mqtt-connector`---
pushes measurements received over MQTT either directly into the database or to Kafka.
Secondly, the main [AstroPlant API](https://github.com/AstroPlant/astroplant-api) implements the bi-directional kit RPC.

The AstroPlant API further implements the HTTP API used for front-end clients.

The SQLAlchemy database ORM and some databates utilities are provided by `astroplant-database`, available in this repository at `./database`.

# File tree

- `./database` contains the SQLAlchemy database ORM and utilities;
- `./mqtt-connector` listens to MQTT for measurements by kits, and either places those measurements into the database or passes them on to Kafka;
- `./kafka-connector` listens to Kafka for measurements, and places them into the database (only used if mqtt-connector is used to forward measurements to Kafka); and
- `./docker` contains Docker Compose scripts to spin up the back-end.

# Requirements
The modules have Python 3.7 as a common requirement.
Please see the individual modules for more information.
