{
  description = "AstroPlant backend packages and services";
  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.flake-compat = {
    url = "github:edolstra/flake-compat";
    flake = false;
  };
  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        {
          packages.mosquitto-go-auth = pkgs.callPackage ./pkgs/mosquitto-go-auth.nix { };
          nixosModules.database = import ./services/database.nix;
          nixosModules.mqtt = import ./services/mqtt.nix;
          devShell = pkgs.mkShell {
            venvDir = "./.venv";
            buildInputs = with pkgs; let
              pythonWithPackages = python3.withPackages (pypkgs: with pypkgs; [
                pip
                setuptools
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
          {
            nixpkgs.overlays = [
              (self_: super: {
                mosquitto-go-auth = self.packages."x86_64-linux".mosquitto-go-auth;
              })
            ];
          }
          self.nixosModules."x86_64-linux".mqtt
          self.nixosModules."x86_64-linux".database
          ({ pkgs, ... }: {
            system.stateVersion = "22.11";
            boot.isContainer = true;
            networking.hostName = "astroplant-container";
            networking.firewall.allowedTCPPorts = [ 80 1883 5432 ];
            environment.systemPackages = with pkgs; [
              neovim
              mosquitto
            ];
            services.nginx.enable = true;
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
          })
        ];
      };
    };
}
