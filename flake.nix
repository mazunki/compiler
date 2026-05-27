{
  description = "language-detecting compiler wrapper";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/25.05";

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs {
      inherit system;
      overlays = [ (import ./toolchain.nix {}) ];
    };
    stdenv = pkgs.toolchain.stdenv';

    mkCompile = args: pkgs.callPackage ./default.nix (args // { inherit pkgs stdenv; });
    compile = mkCompile {};
  in
  {
    packages.${system} = { default = compile; inherit compile; };

    apps.${system} = {
      default = { type = "app"; program = "${compile}/bin/compile"; };
      compile = { type = "app"; program = "${compile}/bin/compile"; };
    };

    lib.${system} = { inherit mkCompile; };
  };
}
