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

    version = self.dirtyShortRev or "unknown";

    mkCompile = args: pkgs.callPackage ./default.nix (args // { inherit pkgs stdenv version; });
    compile = mkCompile {};

    shell = pkgs.symlinkJoin {
      name = "compiler-shell";
      paths = [
        compile
        pkgs.gdb
        pkgs.llvmPackages_20.lldb
        pkgs.toolchain.clang_musl_libcxx
      ];
    };
  in
  {
    packages.${system} = { default = shell; inherit compile shell; };

    apps.${system} = {
      default = { type = "app"; program = "${compile}/bin/compile"; };
      compile = { type = "app"; program = "${compile}/bin/compile"; };
    };

    lib.${system} = { inherit mkCompile; };
  };
}
