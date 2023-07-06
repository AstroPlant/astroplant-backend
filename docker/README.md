# Dockerized AstroPlant back-end
The Docker Compose files here serve as a means to quickly get a full
development AstroPlant back-end setup running, as well as a potential starting
point for a production back-end.

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
git clone https://github.com/AstroPlant/astroplant-api.git
git clone https://github.com/AstroPlant/astroplant-frontend-web.git
git clone https://github.com/AstroPlant/astroplant-backend.git
```

Next, run the Compose file:

```shell
cd astroplant-backend/docker
docker-compose up
```

Wait for everything to build. After a few minutes you can navigate to
`http://localhost:5173` in your browser.

The API listens at `localhost:8080`. The MQTT broker (for kit connections)
listens at `localhost:1883`. You can connect to the database at
`postgres://astroplant:astroplant@localhost/astroplant`.

You might also want to look at
[astroplant-kit](https://github.com/AstroPlant/astroplant-kit) and
[astroplant-simulation](https://github.com/AstroPlant/astroplant-simulation) to
connect a (virtual) kit to this back-end.
