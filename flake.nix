# SPDX-License-Identifier: Unlicense
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    # systems.url = "github:nix-systems/default";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachSystem nixpkgs.lib.systems.flakeExposed (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
      in
      {

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; if pkgs.stdenv.isLinux then [
            libxcb
          ] else [];

          LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${pkgs.libxcb}/lib:${pkgs.libGL}/lib:${pkgs.glib.out}/lib";
        };
      }
    );
}
