with import <nixpkgs> {};
let
  python-packages = python-packages: [
    python-packages.pip
  ];
  python-with-packages = python37.withPackages python-packages;
in  
  pkgs.mkShell {
    buildInputs = [
      bashInteractive
      ncurses
      python-with-packages
      python37Packages.black
      python37Packages.python-language-server
      capnproto
    ];
    shellHook = ''
      export PIP_PREFIX="$(pwd)/_build/pip_packages"
      export PYTHONPATH="$(pwd)/_build/pip_packages/lib/python3.7/site-packages:$PYTHONPATH"
      unset SOURCE_DATE_EPOCH
    '';
  }
