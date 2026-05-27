import abc
import dataclasses
from pathlib import Path
from typing import Self, Optional

from command import KwArg, FlagArg, Args, Command


def _nix_or[T](val: str, fallback: T) -> str|T:
    return fallback if (val.startswith("@") and val.endswith("@")) else val

def _nix_flags(val: str, fallback: Args) -> Args:
    return fallback if (val.startswith("@") and val.endswith("@")) else val.split()


@dataclasses.dataclass
class Language(abc.ABC):
    extensions: frozenset[str] = dataclasses.field(default_factory=frozenset)
    compiler:   Args           = dataclasses.field(default_factory=list)
    cflags:     Args           = dataclasses.field(default_factory=list)
    static:     bool           = True
    debug:      bool           = False

    def with_compiler(self, compiler: Args) -> Self:
        return dataclasses.replace(self, compiler=compiler)

    def with_cflags(self, cflags: Args) -> Self:
        return dataclasses.replace(self, cflags=cflags)

    def with_static(self, enabled: bool = True) -> Self:
        return dataclasses.replace(self, static=enabled)

    def with_debug(self, enabled: bool = True) -> Self:
        return dataclasses.replace(self, debug=enabled)

    @property
    @abc.abstractmethod
    def debug_flags(self) -> Args: ...

    @property
    @abc.abstractmethod
    def static_flags(self) -> Args: ...

    @abc.abstractmethod
    def build_static(self, sources: list[Path], out: Path) -> Command: ...

    @abc.abstractmethod
    def build_dynamic(self, sources: list[Path], out: Path) -> Command: ...

    def build(self, sources: list[Path], out: Path) -> Command:
        return self.build_static(sources, out) if self.static else self.build_dynamic(sources, out)


@dataclasses.dataclass
class C(Language):
    extensions: frozenset[str] = dataclasses.field(default=frozenset({".c"}))
    compiler:   Args           = dataclasses.field(default_factory=lambda: ["cc"])

    @property
    def debug_flags(self):
        return ["-ggdb3"] if self.debug else []

    @property
    def static_flags(self):
        return ["-static", "-rtlib=compiler-rt"]

    def build_static(self, sources, out):
        cmd = Command(list(self.compiler))
        cmd += self.cflags
        cmd += self.static_flags
        cmd += self.debug_flags
        cmd += sources
        cmd += FlagArg("-o", out)
        return cmd

    def build_dynamic(self, sources, out):
        cmd = Command(list(self.compiler))
        cmd += self.cflags
        cmd += self.debug_flags
        cmd += sources
        cmd += FlagArg("-o", out)
        return cmd


@dataclasses.dataclass
class Cpp(Language):
    extensions:  frozenset[str] = dataclasses.field(default=frozenset({".cpp", ".cc", ".cxx"}))
    compiler:    Args           = dataclasses.field(default_factory=lambda: ["c++"])
    libcxx_path: Optional[str]  = dataclasses.field(default_factory=lambda: _nix_or("@LIBCXX@", None))

    @property
    def debug_flags(self):
        return ["-ggdb3"] if self.debug else []

    @property
    def static_flags(self):
        return ["-static", "-rtlib=compiler-rt", f"-L{self.libcxx_path}"]

    def build_static(self, sources, out):
        if self.libcxx_path is None:
            raise RuntimeError("C++ static linking requires libcxx_path; set @LIBCXX@ or pass --no-static")
        cmd = Command(list(self.compiler))
        cmd += self.cflags
        cmd += self.static_flags
        cmd += self.debug_flags
        cmd += sources
        cmd += FlagArg("-o", out)
        return cmd

    def build_dynamic(self, sources, out):
        cmd = Command(list(self.compiler))
        cmd += self.cflags
        cmd += self.debug_flags
        cmd += sources
        cmd += FlagArg("-o", out)
        return cmd


@dataclasses.dataclass
class Zig(Language):
    extensions: frozenset[str] = dataclasses.field(default=frozenset({".zig"}))
    compiler:   Args           = dataclasses.field(default_factory=lambda: ["zig", "build-exe"])

    @property
    def debug_flags(self):
        return ["-Doptimize=Debug"] if self.debug else []

    @property
    def static_flags(self):
        return []

    def build_static(self, sources, out):
        cmd = Command(list(self.compiler))
        cmd += sources
        cmd += self.debug_flags
        cmd += f"-femit-bin={out}"
        return cmd

    def build_dynamic(self, sources, out):
        cmd = Command(list(self.compiler))
        cmd += sources
        cmd += self.debug_flags
        cmd += f"-femit-bin={out}"
        return cmd


c = C(
    compiler=[_nix_or("@CC@", "cc")],
    cflags=_nix_flags("@CFLAGS@", []),
)
cpp = Cpp(
    compiler=[_nix_or("@CXX@", "c++")],
    cflags=_nix_flags("@CFLAGS@", []),
)
zig = Zig()

LANGUAGES: list[Language] = [zig, cpp, c]
