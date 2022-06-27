{ config, lib, pkgs, ... }:
let cfg = config.astroplant.services.database;
in
{
  options.astroplant.services.database = with lib; {
    enable = mkEnableOption "Enables the AstroPlant database. Initial database setup and migrations need to be performed manually.";
    listenRemote = mkOption {
      type = types.bool;
      default = false;
      description = "Whether the database is accessible over the internet. If false, the database can be accessed only on the local machine. Make sure you have firewalling in place if you enable this.";
    };
  };
  config = lib.mkIf cfg.enable {
    services.postgresql = {
      enable = true;
      ensureDatabases = [ "astroplant" ];
      enableTCPIP = cfg.listenRemote;
      authentication = if cfg.listenRemote then ''
        host all all 0.0.0.0/0 md5
        host all all ::/0 md5
      '' else "";
      initialScript = pkgs.writeText "initScript" ''
        CREATE USER astroplant WITH PASSWORD 'astroplant';
        GRANT ALL PRIVILEGES ON DATABASE astroplant TO astroplant;
      '';
    };
  };
}
