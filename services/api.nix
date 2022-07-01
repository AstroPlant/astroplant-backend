astroplant: { config, lib, pkgs, ... }:
let
  cfg = config.astroplant.services.api;
in
{
  options.astroplant.services.api = with lib; {
    enable = mkEnableOption "Enables the AstroPlant API service";
    package = mkOption {
      type = types.package;
      default = astroplant.packages.${pkgs.stdenv.hostPlatform.system}.astroplant-api;
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
    awsS3Region = mkOption {
      type = types.str;
      description = "The S3-like API region.";
      default = "us-east-1";
    };
    awsS3Endpoint = mkOption {
      type = types.str;
      description = "The S3-like endpoint.";
      default = "https://s3.eu-west-1.amazonaws.com";
    };
    awsAccessKeyId = mkOption {
      type = types.nullOr types.str;
      description = "The object store access key.";
      default = "http://localhost:9000";
    };
    awsSecretAccessKey = mkOption {
      type = types.nullOr types.str;
      description = "The object store secret key associated with the access key.";
      default = null;
    };
    signerKeyFile = mkOption {
      type = types.path;
      description = "A file containing a signing key. This is used by the AstroPlant API to sign and verify tokens";
    };
  };

  config = lib.mkIf cfg.enable {
    users.users.astroplantapi = {
      description = "AstroPlant API daemon owner";
      group = "astroplantapi";
      isSystemUser = true;
    };
    users.groups.astroplantapi = { };
    systemd.services."astroplant.api" = {
      description = "AstroPlant API daemon";
      wantedBy = [ "multi-user.target" ];
      after = [
        "postgresql.service"
        "astroplant.mqtt.service"
      ];
      serviceConfig = {
        Type = "simple";
        User = "astroplantapi";
        Group = "astroplantapi";
        Restart = "on-failure";
        ExecStart = "${cfg.package}/bin/astroplant-api";
      };
      environment = {
        MQTT_HOST = cfg.mqttHost;
        MQTT_PORT = toString cfg.mqttPort;
        MQTT_USERNAME = cfg.mqttUser;
        MQTT_PASSWORD = cfg.mqttPassword;
        DATABASE_URL = cfg.dbUrl;
        TOKEN_SIGNER_KEY = toString cfg.signerKeyFile;
        AWS_S3_REGION = cfg.awsS3Region;
        AWS_S3_ENDPOINT = cfg.awsS3Endpoint;
        AWS_ACCESS_KEY_ID = cfg.awsAccessKeyId;
        AWS_SECRET_ACCESS_KEY = cfg.awsSecretAccessKey;
      };
    };
  };
}

