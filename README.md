# AstroPlant Backend
This repository contains utilities to build the modules that form the
AstroPlant backend. The main API, necessary for running the backend, is
available at the [astroplant-api](https://github.com/AstroPlant/astroplant-api)
repository. A front-end UI for interacting with the backend is available at
the
[astroplant-frontend-web](https://github.com/AstroPlant/astroplant-frontend-web)
repository.

# Description of the backend architecture
The AstroPlant backend consists of various modules.

Communication between kits and the backend is over MQTT. A service ingests
measurements over MQTT into the database. The main [AstroPlant
API](https://github.com/AstroPlant/astroplant-api) implements the
bi-directional kit RPC. It further implements the HTTP API used by front-end
clients.

The SQLAlchemy database ORM and some databates utilities are provided by
`astroplant-database`, available in this repository at `./database`.

# File tree
- `./database` contains the SQLAlchemy database ORM and utilities;
- `./docker` contains Docker Compose scripts to spin up a development backend;
- `./pkgs` contains [nixpkgs](https://nixos.org) package declarations used for
  backend services (astroplant-api and astroplant-frontend provide their own
  nixpkgs declarations in their respective repositories); and
- `./services` contains NixOS service module declarations for the backend
  modules.
- `./flake.nix` re-exports the NixOS service module declarations and provides a
  container declaration to spin up a NixOS-based development backend.

# Creating a development backend
This repository provides two methods for creating backends for development
purposes: Docker Compose and a [NixOS](https://nixos.org) container.

## Docker Compose
A Docker Compose file to launch a development backend including the web
front-end is available in the `./docker` subdirectory.

To get started quickly, run:

```shell
$ git clone https://github.com/AstroPlant/astroplant-api.git
$ git clone https://github.com/AstroPlant/astroplant-frontend-web.git
$ git clone https://github.com/AstroPlant/astroplant-backend.git
$ cd astroplant-backend/docker
$ docker-compose up
```

Then navigate to `http://localhost:5173` in your browser.

See the `./docker` directory for more details.

## NixOS container
A NixOS container declaration is given in `./flake.nix`. On NixOS, you can
start it imperatively:

```shell
$ git clone https://github.com/AstroPlant/astroplant-backend.git
$ cd astroplant-backend
$ sudo nixos-container create astroplant --flake .
$ sudo nixos-container start astroplant
```

See https://nixos.wiki/wiki/NixOS_Containers for more information.
