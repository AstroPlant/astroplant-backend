astroplant: { config, lib, pkgs, ... }:
let
  cfg = config.astroplant.services.mqtt-ingest;
in
{
  options.astroplant.services.mqtt-ingest = with lib; {
    enable = mkEnableOption "Enables the AstroPlant MQTT ingest service";
    package = mkOption {
      type = types.package;
      default = astroplant.packages.${pkgs.stdenv.hostPlatform.system}.astroplant;
      description = "AstroPlant package to use";
    };
    mqttHost = mkOption {
      type = types.str;
      default = "localhost";
      description = "The MQTT broker address";
    };
    mqttPort = mkOption {
      type = types.port;
      default = 1883;
      description = "The MQTT broker port";
    };
    mqttUser = mkOption {
      type = types.str;
      default = "astroplant";
      description = "The user to authenticate as to MQTT";
    };
    mqttPassword = mkOption {
      type = types.str;
      default = "astroplant";
      description = "The password for authenticating to MQTT";
    };
    dbUrl = mkOption {
      type = types.str;
      description = "The PostgreSQL connection URL";
    };
  };

  config = lib.mkIf cfg.enable {
    users.users.mqttingest = {
      description = "AstroPlant MQTT ingest daemon owner";
      group = "mqttingest";
      isSystemUser = true;
    };
    users.groups.mqttingest = { };
    systemd.services."astroplant.mqtt-ingest" = {
      description = "AstroPlant MQTT ingest daemon";
      wantedBy = [ "multi-user.target" ];
      after = [
        "postgresql.service"
        "astroplant.mqtt.service"
      ];
      serviceConfig = {
        Type = "simple";
        User = "mqttingest";
        Group = "mqttingest";
        Restart = "on-failure";
        ExecStart = "${cfg.package}/bin/astroplant-mqtt-ingest";
      };
      environment = {
        MQTT_HOST = cfg.mqttHost;
        MQTT_PORT = toString cfg.mqttPort;
        MQTT_USERNAME = cfg.mqttUser;
        MQTT_PASSWORD = cfg.mqttPassword;
        DATABASE_URL = cfg.dbUrl;
      };
    };
  };
}
