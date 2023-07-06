# Dockerized AstroPlant backend
The Docker Compose files here serve as a means to quickly get a full
development AstroPlant backend setup running, as well as a potential starting
point for a production backend.

# Getting started
The Compose files here assume a specific file tree of the `astroplant-api`,
`astroplant-frontend-web` and `astroplant-backend` repositories:

```shell
$ tree -L 1
.
├── astroplant-api
├── astroplant-backend
└── astroplant-frontend-web
```

Clone these repositories:

```shell
$ git clone https://github.com/AstroPlant/astroplant-api.git
$ git clone https://github.com/AstroPlant/astroplant-frontend-web.git
$ git clone https://github.com/AstroPlant/astroplant-backend.git
```

Next, run the Compose file:

```shell
$ cd astroplant-backend/docker
$ docker-compose up
```

Wait for everything to build. After a few minutes you can navigate to
`http://localhost:5173` in your browser.

The API listens at `localhost:8080`. The MQTT broker (for kit connections)
listens at `localhost:1883`. You can connect to the database at
`postgres://astroplant:astroplant@localhost/astroplant`.

## Connecting a kit
Take a look at [astroplant-kit](https://github.com/AstroPlant/astroplant-kit)
and
[astroplant-simulation](https://github.com/AstroPlant/astroplant-simulation) to
connect a (virtual) kit to this backend. This Dockerized backend does not
perform true kit authentication. Instead, it provides wildcard authentication
with a single predefined username and password. You can use the following
`kit_config.toml`:

```toml
[message_broker]
host = "localhost"
port = 1883

[message_broker.auth]
username = "k-develop"
serial = "<<kit serial as given by the frontend>>"
secret = "abcdef"

[debug]
level = "INFO"

[debug.peripheral_display]
module_name = "astroplant_kit.peripheral"
class_name = "DebugDisplay"
```
