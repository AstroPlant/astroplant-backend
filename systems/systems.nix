{
  network.description = "AstroPlant back-end network";

  database =
    { config, pkgs, ...}:
    {
      environment.systemPackages = with pkgs; [
        rxvt_unicode.terminfo
      ];
      services.postgresql = {
        enable = true;
        package = pkgs.postgresql;
        enableTCPIP = true;
        port = 5432;
        authentication = ''
          local all all trust
          host all all 127.0.0.1/32 trust
          host all all 192.168.0.0/16 trust
          host all all 172.16.0.0/12 trust
          host all all 10.0.0.0/8 trust
        '';
        initialScript = pkgs.writeText "initScript" ''
          CREATE ROLE astroplant WITH LOGIN PASSWORD 'astroplant' CREATEDB;
          CREATE DATABASE astroplant;
          GRANT ALL PRIVILEGES ON DATABASE astroplant TO astroplant;
        '';
      }; 
      networking.firewall.allowedTCPPorts = [
        22 # SSH
        5432 # Postgres
      ];
    };

  kafka =
    { pkgs, ...}:
    {
      environment.systemPackages = with pkgs; [
        rxvt_unicode.terminfo
      ];
      services.zookeeper.enable = true;
      services.apache-kafka = {
        enable = true;
        port = 9092;
        hostname = "";
        extraProperties = ''
          listeners=PLAINTEXT://0.0.0.0:9092
          advertised.listeners=PLAINTEXT://kafka.ops:9092
        '';
      };
      networking.firewall.allowedTCPPorts = [
        22 # SSH
        2181 # Zookeeper
        9092 # Kafka
      ];
    };

  mqtt =
    { pkgs, ...}:
    {
      environment.systemPackages = with pkgs; [
        rxvt_unicode.terminfo
      ];
      services.mosquitto = {
        enable = true;
        host = "0.0.0.0";
        port = 1883;
        allowAnonymous = false;
        users = {
          k_develop = {
            password = "abcdef";
            acl = [ "topic readwrite kit/#" ];
          };
          server = {
            password = "abcdef";
            acl = [ "topic read kit/#" ];
          };
        };
      };
      networking.firewall.allowedTCPPorts = [
        22 # SSH
        1883 # MQTT
      ];
    };
}
