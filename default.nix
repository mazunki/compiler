{ pkgs
, stdenv
, cflags ? "-O2"
, debug ? false
}:

pkgs.stdenv.mkDerivation {
  pname = "compile";
  version = "dev";
  src = ./.;

  dontConfigure = true;
  dontBuild = true;

  installPhase = ''
    install -D command.py $out/bin/command.py
    install -D languages.py $out/bin/languages.py
    substituteInPlace $out/bin/languages.py \
      --subst-var-by CC     "${stdenv.cc}/bin/cc" \
      --subst-var-by CXX    "${stdenv.cc}/bin/c++" \
      --subst-var-by CFLAGS "${cflags}" \
      --subst-var-by LIBCXX "${pkgs.toolchain.libcxx_musl}/lib"

    install -D compile $out/bin/compile
    substituteInPlace $out/bin/compile \
      --replace-fail "#!/usr/bin/env python3" "#!${pkgs.python3}/bin/python3"
  '';
}
