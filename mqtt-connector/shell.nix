with import <nixpkgs> { };
let
  python-packages = python-packages: [ python-packages.pip ];
  python-with-packages = python37.withPackages python-packages;
in pkgs.mkShell {
  buildInputs = [
    bashInteractive
    ncurses
    python-with-packages
    postgresql
    python37Packages.black
    python37Packages.python-language-server
    capnproto
  ];
  PIP_PREFIX = toString ./_build/pip_packages;
  shellHook = ''
    mkdir -p ${toString ./_build/pip_packages/lib/python3.7/site-packages}
    mkdir -p ${toString ./_build/python3.7/site-packages}
    export PYTHONPATH="${
      toString ./_build/pip_packages/lib/python3.7/site-packages
    }:${toString ./_build/python3.7/site-packages}:$PYTHONPATH"
    export PATH="${toString ./_build/pip_packages/bin}:$PATH"

    unset SOURCE_DATE_EPOCH
  '';
}
