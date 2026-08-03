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
            # matplotlib啥的，画图（显示验证码和识别结果）要用。仅开发阶段测试需要。
            libxcb
          ] else [];

          LD_LIBRARY_PATH="$LD_LIBRARY_PATH:${pkgs.libxcb}/lib:${pkgs.libGL}/lib:${pkgs.glib.out}/lib";
        };
      }
    );
}
