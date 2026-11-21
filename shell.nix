{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  buildInputs = [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.pygame
    ]))
  ];

  shellHook = ''
    export PYTHONPATH="$PWD/src:$PYTHONPATH"
  '';
}
