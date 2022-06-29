mosquitto-go-auth: { config, lib, pkgs, ... }:
let
  cfg = config.astroplant.services.mqtt;
  makeAclFile = staticUsers: with lib; pkgs.writeText "mqtt-acl" (
    concatStringsSep "\n" (flatten (
      mapAttrsToList (name: user: [ "user ${name}" ] ++ map (topic: "topic ${topic}") user.acl) staticUsers
    ))
  );
  makePasswdFile = staticUsers: with lib; pkgs.writeText "mqtt-passwd" (
    concatStringsSep "\n" (
      mapAttrsToList (name: user: "${name}:${user.hashedPassword}") staticUsers
    )
  );
  anonymousListen = ''
    listener ${toString cfg._anonymousPort}
    allow_anonymous true
  '';
  configFile = pkgs.writeText "mosquitto.conf" ''
    per_listener_settings true
    persistence true
    log_dest stderr

    ${if cfg._anonymousPort != null then anonymousListen else ""}

    listener ${toString cfg.port}
    allow_anonymous false
    use_username_as_clientid true
    auth_plugin ${mosquitto-go-auth}/lib/go-auth.so
    auth_plugin_deny_special_chars true
    auth_opt_backends files, postgres
    auth_opt_files_register user, acl
    auth_opt_pg_register user, acl
    auth_opt_hasher pbkdf2
    auth_opt_hasher_salt_encoding utf-8
    auth_opt_files_password_path ${makePasswdFile cfg.staticUsers}
    auth_opt_files_acl_path ${makeAclFile cfg.staticUsers}
    auth_opt_pg_host ${cfg.dbHost}
    auth_opt_pg_port ${toString cfg.dbPort}
    auth_opt_pg_user ${cfg.dbUser}
    auth_opt_pg_password ${cfg.dbPassword}
    auth_opt_pg_dbname ${cfg.dbDatabase}
    auth_opt_pg_aclquery SELECT CONCAT('kit/', $1::VARCHAR, '/#') WHERE $2 = $2
    auth_opt_pg_userquery SELECT password_hash FROM kits WHERE serial = $1::VARCHAR LIMIT 1
    auth_opt_cache true
    auth_opt_cache_type go-cache
    auth_opt_cache_refresh false
    # kit passwords can change...
    auth_opt_auth_cache_seconds 5
    # ... but ACL is static
    auth_opt_acl_cache_seconds 3600
  '';
in
{
  options.astroplant.services.mqtt = with lib; {
    enable = mkEnableOption "Enables the AstroPlant MQTT service with client authentication";
    package = mkOption {
      type = types.package;
      default = pkgs.mosquitto;
      defaultText = literalExpression "pkgs.mosquitto";
      description = "Mosquitto package to use";
    };
    dataDir = mkOption {
      default = "/var/lib/mosquitto";
      type = types.path;
      description = "The data directory";
    };
    dbHost = mkOption {
      type = types.str;
      default = "localhost";
      description = "The address Postgres listens on";
    };
    _anonymousPort = mkOption {
      type = types.nullOr types.port;
      default = null;
      description = "A listen port accepting users without athentication. Make sure this is not publicly accessible!";
    };
    port = mkOption {
      type = types.port;
      default = 1883;
      description = "The port to listen on";
    };
    dbPort = mkOption {
      type = types.port;
      default = 5432;
      description = "The port Postgres listens on";
    };
    dbUser = mkOption {
      type = types.str;
      default = "astroplant";
      description = "The Postgres user";
    };
    dbPassword = mkOption {
      type = types.str;
      default = "astroplant";
      description = "The Postgres password";
    };
    dbDatabase = mkOption {
      type = types.str;
      default = "astroplant";
      description = "The Postgres database name";
    };
    # It would be nice to allow static users to connect only on a specific port,
    # but mosquitto-go-auth does not correctly support this. Instead we currently
    # have _anonymousPort that allows clients to connection without authentication.
    # This can be used on internal networks, but should not be exposed publicly.
    # See: https://github.com/iegomez/mosquitto-go-auth/issues/213
    staticUsers = mkOption {
      type = types.attrsOf (types.submodule {
        options = {
          hashedPassword = mkOption {
            type = types.str;
            description = "Hash in the format 'PBKDF2$sha512$100$salt$hash'";
          };
          acl = mkOption {
            type = types.listOf types.str;
            example = [ "readwrite something/#" ];
            default = [ ];
            description = "Client access";
          };
        };
      });
      example = { someone = { hashedPassword = "PBKDF2$sha512$100$salt$hash"; acl = [ "#" ]; }; };
      description = "Static clients and their access";
      default = { };
    };
  };

  config = lib.mkIf cfg.enable {
    # Re-use upstream Mosquitto UID and GID
    users.users.mosquitto = {
      description = "Mosquitto MQTT Broker Daemon owner";
      group = "mosquitto";
      uid = config.ids.uids.mosquitto;
      home = cfg.dataDir;
      createHome = true;
    };
    users.groups.mosquitto.gid = config.ids.gids.mosquitto;
    systemd.services."astroplant.mqtt" = {
      description = "AstroPlant Mosquitto MQTT Broker Daemon";
      wantedBy = [ "multi-user.target" ];
      after = [ "network-online.target" ];
      serviceConfig = {
        Type = "notify";
        NotifyAccess = "main";
        User = "mosquitto";
        Group = "mosquitto";
        RuntimeDirectory = "mosquitto";
        WorkingDirectory = cfg.dataDir;
        Restart = "on-failure";
        ExecStart = "${cfg.package}/bin/mosquitto -c ${configFile}";
        ExecReload = "${pkgs.coreutils}/bin/kill -HUP $MAINPID";
      };
    };
  };
}
