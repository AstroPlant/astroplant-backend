{
  description = "AstroPlant backend packages and services";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };

    astroplant-api = {
      url = "github:astroplant/astroplant-api";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    astroplant-frontend = {
      url = "github:astroplant/astroplant-frontend-web";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, astroplant-api, astroplant-frontend, ... }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          packages.mosquitto-go-auth = pkgs.callPackage ./pkgs/mosquitto-go-auth.nix { };
          nixosModules.database = import ./services/database.nix;
          nixosModules.mqtt = import ./services/mqtt.nix self.packages.${system}.mosquitto-go-auth;
          nixosModules.mqtt-ingest = import ./services/mqtt-ingest.nix astroplant-api;
          nixosModules.api = import ./services/api.nix astroplant-api;
          devShell = pkgs.mkShell {
            venvDir = "./.venv";
            buildInputs = with pkgs; let
              pythonWithPackages = python3.withPackages (pypkgs: with pypkgs; [
                pip
                setuptools
                pbkdf2
                psycopg2
                sqlalchemy
              ]);
            in
            [
              black
              postgresql
              python3Packages.venvShellHook
              python-language-server
              pythonWithPackages
            ];
          };
        }) //
    {
      nixosConfigurations.container = nixpkgs.lib.nixosSystem {
        system = "x86_64-linux";
        modules = [
          self.nixosModules."x86_64-linux".mqtt
          self.nixosModules."x86_64-linux".database
          self.nixosModules."x86_64-linux".mqtt-ingest
          self.nixosModules."x86_64-linux".api
          ({ pkgs, ... }: {
            system.stateVersion = "22.11";
            boot.isContainer = true;
            networking.hostName = "astroplant-container";
            networking.firewall.allowedTCPPorts = [ 80 81 1883 5432 ];
            environment.systemPackages = with pkgs; [
              neovim
              mosquitto
            ];
            services.nginx = {
              enable = true;
              recommendedOptimisation = true;
              recommendedGzipSettings = true;
              recommendedProxySettings = true;
              virtualHosts."localhost" = {
                default = true;
                locations."/" = {
                  proxyPass = "http://127.0.0.1:8080";
                  proxyWebsockets = true;
                };
                listen = [{ addr = "0.0.0.0"; port = 81; }];
              };
              virtualHosts."frontend" = {
                serverName = "frontend";
                listen = [{ addr = "0.0.0.0"; port = 80; }];
                root = astroplant-frontend.packageExprs."x86_64-linux".astroplant-frontend {
                  apiUrl = "http://10.240.1.2:81";
                  websocketUrl = "ws://10.240.1.2:81/ws";
                };
                locations."/" = {
                  index = "index.html";
                  tryFiles = "$uri /index.html =404";
                };
              };
            };
            astroplant.services.database.enable = true;
            astroplant.services.database.listenRemote = true;
            astroplant.services.mqtt.enable = true;
            astroplant.services.mqtt.staticUsers = {
              astroplant-api = {
                acl = [ "readwrite kit/#" ];
                # Password: "abcdef"
                hashedPassword = "PBKDF2$sha512$100000$K7yuzFFHfm$ApJQCKmfWDjcxkkRD61UdsqQRQEYHAlFCRiSZdKYL60YhuStXat8XhmWAWn/ODjUcX2vS7/MveHHTTOWGu2QLw==";
              };
              astroplant-mqtt-ingest = {
                acl = [ "readwrite kit/#" ];
                # Password: "abcdef"
                hashedPassword = "PBKDF2$sha512$100000$K7yuzFFHfm$ApJQCKmfWDjcxkkRD61UdsqQRQEYHAlFCRiSZdKYL60YhuStXat8XhmWAWn/ODjUcX2vS7/MveHHTTOWGu2QLw==";
              };
            };
            astroplant.services.mqtt-ingest = {
              enable = true;
              mqttUser = "astroplant-mqtt-ingest";
              mqttPassword = "abcdef";
              dbUrl = "postgres://astroplant:astroplant@localhost/astroplant";
            };
            astroplant.services.api = {
              enable = true;
              mqttUser = "astroplant-api";
              mqttPassword = "abcdef";
              dbUrl = "postgres://astroplant:astroplant@localhost/astroplant";
              signerKeyFile = pkgs.writeText "api-signer-key" ''
                this is not a secure key
                only use it for testing
              '';
            };
          })
        ];
      };
    };
}
