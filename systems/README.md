# Nixops deployment
These are Nixops deployment scripts for the systems used in the AstroPlant
backend.
It spins up the MQTT broker, Kafka and PostgreSQL with a development
configuration.
To use these scripts, you must have Nixops and VirtualBox installed.


# Usage
Deploy using:

```shell
$ nixops create ./systems.nix ./vbox.nix -d astroplant
$ nixops deploy -d astroplant
```

See the [Nixops manual](https://nixos.org/nixops/manual/) for more information.
