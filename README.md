# compile
a universal compiler

this is a wrapper around several compilers in order to quickly get freestanding elf binaries that can run in freestanding environments.

supports c, c++ and zig currently.

if multiple compatible sources exist in the same direc

## usage
```sh
nix run github:mazunki/compiler
nix run github:mazunki/compiler -- some/path
nix run github:mazunki/compiler -- some/source/file.c
nix run github:mazunki/compiler -- --compiler /path/to/compiler some/path

nix shell github:mazunki/compiler
compile
compile --debug some/path
compile --out meow.out
compile -h
```

`-v` can be enabled to see the command used, `--verbose=oneline` or `-v1` places it on one line
`--debug` can be passed to enable gdb-relevant debugging information. this is embedded into the ELF file.

## contributing
`languages.py` includes implementations for different languages
`command.py` handles prettyprinting and stuff
`compile` handles argument parsing and is the user's entry point

note that some `@PLACEHOLDER@` values are derived from nix builds. this can be useful for toolchains that can't rely on hardcoded paths. fallback values allow this to not have a hard nix dependency.

