{ stdenv, lib, buildGoModule, fetchFromGitHub, pkgs }:

buildGoModule rec {
  pname = "mosquitto-go-auth";
  version = "1.8.2";

  vendorSha256 = "sha256-MDjmG3rIzslxCGQh5ZBK54LaMNlhXzZoyJLLsMLN1K8=";

  src = fetchFromGitHub {
    owner = "iegomez";
    repo = "mosquitto-go-auth";
    rev = version;
    sha256 = "sha256-omUdInRxBz1XXdmuZNmaxjlovSpn/0ZIeWXa0IOB/mo=";
  };

  propagatedBuildInputs = [ pkgs.gcc pkgs.pkgconfig pkgs.mosquitto ];

  buildPhase = ''
    export CGO_FLAGS="-I${pkgs.mosquitto}/include -fPIC"
    export CGO_LDFLAGS="-shared"
    go build -buildmode=c-archive go-auth.go
    go build -buildmode=c-shared -o go-auth.so
  '';

  installPhase = ''
    install -m644 -D ./go-auth.so $out/lib/go-auth.so
  '';

  meta = with lib; {
    homepage = "https://github.com/iegomez/mosquitto-go-auth";
    description = "Auth plugin for mosquitto";
    maintainers = [ ];
    license = licenses.mit;
    platforms = platforms.unix;
  };
}
