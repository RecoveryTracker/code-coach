"""
Code Coach engine — Stage 1.5

Looks at student code (path or in-memory), optionally runs it,
scores waypoints, returns teaching-oriented next step (not personal data).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os
import signal
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

# Cap runaway student programs (e.g. while True).
#
# Three seconds is the rule for a person sitting in front of the app, and
# it is the right one: a `while True` should stop the screen for three
# seconds, not thirty.
#
# It is the wrong rule for the suite, which starts thousands of processes
# back to back. Under that load Windows can spend seconds on process
# startup alone, so a program that finishes in 0.3s gets killed at the
# three-second mark and reported as a possible infinite loop. That has
# happened twice in hour-long runs - `dataclass-06` and the marker's
# syntax-error test - both times to code that runs in well under a
# second when asked on its own.
#
# A suite that fails at random is worse than no suite, because you stop
# believing it. So the ceiling is settable, the app never sets it, and
# tests/conftest.py raises it for the duration of a run.
RUN_TIMEOUT_SECONDS = 3.0

# Dart compiles before it runs, so a first execution costs seconds that have
# nothing to do with the student's loop. Its own ceiling, not Python's.
DART_TIMEOUT_SECONDS = 25.0
# Hard CPU-seconds cap enforced in-kernel (belt-and-suspenders with the timeout).
# RLIMIT_CPU is honored on Linux and macOS.
CPU_SECONDS = 5
# Address-space cap so `x = "a" * 10**10` is killed instead of eating all RAM.
# NOTE: RLIMIT_AS is enforced on Linux but IGNORED on macOS (Darwin) — on macOS
# the effective guards are the wall-clock timeout, RLIMIT_CPU, and the output cap.
# Generous enough for the interpreter + normal beginner scripts.
MEM_BYTES = 700 * 1024 * 1024
# Cap captured output so a runaway print loop can't balloon the response.
MAX_OUTPUT_CHARS = 100_000

_IS_POSIX = os.name == "posix"

#: Environment variable that raises the ceiling. Read per call rather
#: than at import, so setting it cannot depend on which module was
#: imported first.
TIMEOUT_ENV = "CODE_COACH_RUN_TIMEOUT"


def default_timeout(language: str = "python") -> float:
    """How long this language's programs get, in seconds.

    Slow languages compile before they run, and that cost has nothing to
    do with the student's loop, so they keep their own larger ceiling —
    raised too if the override asks for more than it.
    """
    floor = (
        DART_TIMEOUT_SECONDS if language in _SLOW_LANGUAGES
        else RUN_TIMEOUT_SECONDS
    )
    raised = os.environ.get(TIMEOUT_ENV, "").strip()
    if not raised:
        return floor
    try:
        # Never lower the ceiling: the override exists to stop false
        # timeouts, and a too-small value would manufacture them instead.
        return max(floor, float(raised))
    except ValueError:
        return floor


# How a child program's output is read back.
#
# UTF-8 rather than whatever the machine's locale happens to be, because
# the programs being run are not written for this machine: Node emits
# UTF-8 always, and on Windows the locale is cp1252, so a JavaScript
# program printing an ellipsis came back as three characters of
# nonsense. errors="replace" so a program that emits something genuinely
# undecodable still reports what it managed rather than killing the run
# with an exception from the reader thread.
_TEXT_OUT = {"text": True, "encoding": "utf-8", "errors": "replace"}

try:
    import resource as _resource  # POSIX only
except ImportError:  # pragma: no cover - Windows
    _resource = None


def _apply_limits() -> None:
    """Run in the child before exec (POSIX). Best-effort; never blocks a start."""
    if _resource is None:
        return
    for res, cap in (
        (_resource.RLIMIT_CPU, CPU_SECONDS),
        (_resource.RLIMIT_AS, MEM_BYTES),
    ):
        try:
            _resource.setrlimit(res, (cap, cap))
        except (ValueError, OSError):
            pass


def _cap_output(text: str) -> str:
    if text is None:
        return ""
    if len(text) > MAX_OUTPUT_CHARS:
        return text[:MAX_OUTPUT_CHARS] + "\n…(output truncated)"
    return text


@dataclass
class CoachResult:
    lesson_title: str
    practice_path: Path
    code: str
    stdout: str
    stderr: str
    exit_code: int
    checks: list[tuple[str, bool]]  # (label, passed)
    passed: int
    total: int
    next_label: str | None
    next_concept: str | None
    next_why: str | None
    next_hint: str | None
    next_example: str | None
    # Back-compat alias used by older callers / CLI wording
    next_suggest: str | None
    ran: bool = True

    @property
    def complete(self) -> bool:
        return self.next_label is None


def load_code(path: Path) -> str:
    return path.read_text(encoding="utf-8")


#: Toolchains installed for this app rather than system-wide, because
#: this machine has no package manager and putting four more compilers on
#: the system PATH is not a thing a learning app should do to you. PATH is
#: still asked first, so a real system install always wins.
_LOCAL_TOOLCHAINS = Path.home() / "toolchains"


def _tool(name: str, *candidates: str) -> str | None:
    """The path to a toolchain binary: PATH first, then our own directory."""
    found = shutil.which(name)
    if found:
        return found
    for rel in candidates:
        here = _LOCAL_TOOLCHAINS / rel
        if here.exists():
            return str(here)
    return None


def _interpreter_for(path: Path) -> list[str] | None:
    """The command that runs this file, or None if we can't run its kind.

    Dart is found on PATH; `shutil.which` resolves the .bat shim that the
    Flutter SDK installs on Windows.

    Go and Zig are compiled, but both have a `run` subcommand that builds
    and executes in one step, so they belong here rather than with the
    compilers below: there is no separate binary to clean up.
    """
    suffix = path.suffix.lower()
    if suffix == ".py":
        return [sys.executable, str(path)]
    if suffix == ".dart":
        dart = dart_path()
        return [dart, "run", str(path)] if dart else None
    if suffix in (".js", ".mjs"):
        node = shutil.which("node")
        return [node, str(path)] if node else None
    if suffix == ".go":
        go = _tool("go", "go/bin/go.exe", "go/bin/go")
        return [go, "run", str(path)] if go else None
    if suffix == ".php":
        php = _tool("php", "php/php.exe", "php/php")
        return [php, str(path)] if php else None
    if suffix == ".lua":
        lua = _tool("lua", "lua/bin/lua.exe", "lua/bin/lua")
        return [lua, str(path)] if lua else None
    if suffix == ".java":
        # Java 21's source launcher compiles in memory and does not mind
        # that the temp file is not named after the class.
        java = _tool("java", "jdk-21.0.12.1+1/bin/java.exe", "jdk/bin/java.exe")
        return [java, str(path)] if java else None
    if suffix == ".cs":
        # .NET 10 runs a single .cs file directly. The first ever run
        # initialises the SDK and takes minutes; every run after is under
        # a second, including for a file it has not seen.
        dotnet = _tool("dotnet", "dotnet/dotnet.exe", "dotnet/dotnet")
        return [dotnet, "run", str(path)] if dotnet else None
    if suffix == ".odin":
        odin = _tool("odin", "odin/dist/odin.exe", "odin/odin.exe")
        return [odin, "run", str(path), "-file"] if odin else None
    if suffix == ".lisp":
        # ABCL is a Common Lisp that runs on the JVM, which is why it is
        # the one that installed: SBCL ships only through SourceForge and
        # that returned 403, and the JDK was already here for Java.
        #
        # --batch with stdin closed, or it opens a REPL and waits forever.
        # --add-opens because ABCL 1.9.2 introspects virtual threads on
        # startup and Java 21 refuses without it; the run works either way
        # but prints a stack trace to stderr that is not the program's.
        java = _tool("java", "jdk-21.0.12.1+1/bin/java.exe", "jdk/bin/java.exe")
        jar = _LOCAL_TOOLCHAINS / "abcl" / "abcl-bin-1.9.2" / "abcl.jar"
        if java and jar.exists():
            return [
                java,
                "--add-opens", "java.base/java.lang=ALL-UNNAMED",
                "-jar", str(jar),
                "--noinform", "--batch",
                "--load", str(path),
                "--eval", "(quit)",
            ]
        return None
    if suffix == ".rb":
        ruby = _tool(
            "ruby",
            "rubyinstaller-4.0.6-1-x64/bin/ruby.exe",
            "ruby/bin/ruby.exe",
            "ruby/bin/ruby",
        )
        return [ruby, str(path)] if ruby else None
    if suffix == ".zig":
        zig = _tool(
            "zig",
            "zig-x86_64-windows-0.16.0/zig.exe",
            "zig/zig.exe",
            "zig/zig",
        )
        return [zig, "run", str(path)] if zig else None
    return [sys.executable, str(path)]


# Compiled languages: (compiler candidates, extra args). The binary lands
# beside the source and is removed with it.
_COMPILERS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    # -lm only where libm is a separate library, which is to say not on
    # Windows: there the maths functions are already in the C runtime and
    # the flag sends the linker looking for an m.lib that does not exist.
    #
    # This sat harmlessly wrong for as long as no clang was on PATH here —
    # C fell through to MSVC, which never saw the flag. Installing Swift
    # put its own clang on PATH, `shutil.which("clang")` started finding
    # it, and seventy-five C tests failed at the link step on a machine
    # where nothing about C had changed.
    ".c": (("gcc", "clang"), ("-std=c17", *(("-lm",) if _IS_POSIX else ()))),
    ".cpp": (("g++", "clang++"), ("-std=c++17",)),
    # Pin the edition. Without it rustc defaults to 2015, which is not what
    # anyone writing Rust means today — and the difference is not cosmetic:
    # array .into_iter() yields references in 2015 and values in 2021, so
    # ordinary modern code fails for a reason that is nothing to do with it.
    # C and C++ above already pin their language version; Rust was the odd
    # one out.
    ".rs": (("rustc",), ("-O", "--edition", "2021")),
}


def _find_tsc() -> Path | None:
    """The TypeScript compiler, preferring the copy the web app already has.

    Looking here first means TypeScript works out of the box for anyone who
    has run `npm install` in web/ — no separate global install.
    """
    local = (
        Path(__file__).resolve().parent.parent
        / "web"
        / "node_modules"
        / "typescript"
        / "bin"
        / "tsc"
    )
    if local.exists():
        return local
    found = shutil.which("tsc")
    return Path(found) if found else None


def typescript_available() -> bool:
    return _find_tsc() is not None and shutil.which("node") is not None


def _run_typescript(path: Path, timeout: float) -> tuple[str, str, int]:
    """Type-check and compile to JavaScript, then run that.

    `--noEmitOnError` so a type error stops the run and gets reported — the
    type checking is the reason to write TypeScript at all, and silently
    running past it would teach the wrong lesson.

    `--strict` for the same reason, one level up. Without it the compiler
    is a different and much weaker language than the one anybody writes:
    parameters are implicitly any, null and undefined belong to every type,
    and — the case that exposed this — a boolean discriminant does not
    narrow on truthiness, so `if (result.ok)` leaves the union un-narrowed.
    A workbook that teaches TypeScript in a mode nobody ships would be
    teaching something adjacent to TypeScript.
    """
    tsc = _find_tsc()
    node = shutil.which("node")
    if tsc is None or node is None:
        return (
            "",
            "TypeScript needs Node and the TypeScript compiler. Run "
            "`npm install` in the web folder, then try again.",
            127,
        )

    built = path.with_suffix(".js")
    try:
        compiled = subprocess.run(
            [
                node,
                str(tsc),
                str(path),
                "--target", "es2020",
                "--module", "commonjs",
                "--skipLibCheck",
                "--noEmitOnError",
                "--strict",
            ],
            capture_output=True,
            **_TEXT_OUT,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return "", f"Type-checking timed out after {timeout:g}s.", 124

    if compiled.returncode != 0:
        # tsc reports errors on stdout, not stderr.
        return "", _cap_output(compiled.stdout or compiled.stderr), compiled.returncode

    try:
        ran = subprocess.run(
            [node, str(built)],
            capture_output=True,
            **_TEXT_OUT,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
        return _cap_output(ran.stdout), _cap_output(ran.stderr), ran.returncode
    except subprocess.TimeoutExpired:
        return "", f"Program timed out after {timeout:g}s.", 124
    finally:
        try:
            built.unlink(missing_ok=True)
        except OSError:
            pass


# Windows without a GNU toolchain still compiles: fall back to MSVC. cl.exe
# only works inside the environment vcvars64.bat sets up, so a build is one
# cmd session that calls that first and then compiles.
# C11 atomics are standard C, but MSVC keeps <stdatomic.h> behind a switch
# and errors out with "C atomic support is not enabled" without it. Passing
# it makes standard code compile; gcc and clang need nothing, which is why
# this lives on the MSVC path rather than in the shared flags.
_MSVC_STD = {
    ".c": "/std:c17 /experimental:c11atomics",
    ".cpp": "/std:c++17",
}
_VSWHERE = Path(
    r"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
)
_VCVARS_FALLBACK = Path(
    r"C:\Program Files\Microsoft Visual Studio\2022\Community"
    r"\VC\Auxiliary\Build\vcvars64.bat"
)


@lru_cache(maxsize=1)
def _find_vcvars() -> Path | None:
    """vcvars64.bat from the newest Visual Studio that ships the C++ tools.

    vswhere is the supported way to find an install — Professional, Enterprise
    and side-by-side versions all answer it — and the hardcoded Community path
    is only a backstop for machines missing the installer. Cached because every
    Run would otherwise pay for the lookup.
    """
    if os.name != "nt":
        return None

    candidates: list[Path] = []
    if _VSWHERE.exists():
        try:
            found = subprocess.run(
                [
                    str(_VSWHERE),
                    "-latest",
                    "-products", "*",
                    "-requires",
                    "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                    "-property", "installationPath",
                ],
                capture_output=True,
                **_TEXT_OUT,
                timeout=15,
            )
        except (OSError, subprocess.TimeoutExpired):
            found = None
        if found is not None and found.returncode == 0:
            root = found.stdout.strip().splitlines()
            if root:
                candidates.append(
                    Path(root[0]) / "VC" / "Auxiliary" / "Build" / "vcvars64.bat"
                )
    candidates.append(_VCVARS_FALLBACK)

    return next((c for c in candidates if c.exists()), None)


def msvc_available() -> bool:
    return _find_vcvars() is not None


def _strip_cl_echo(text: str, source: Path) -> str:
    """Drop the source file name cl prints before anything else.

    That line is build chatter; the student never wrote a program to say it.
    """
    kept = [line for line in text.splitlines() if line.strip() != source.name]
    return "\n".join(kept).strip()


def _run_msvc(path: Path, timeout: float) -> tuple[str, str, int]:
    """Compile with cl.exe inside a vcvars64 session, then run the result.

    vcvars64.bat changes the working directory, so the source, the .obj and
    the .exe are all named absolutely; the build products land in their own
    temp directory instead of beside the source.
    """
    vcvars = _find_vcvars()
    if vcvars is None:  # pragma: no cover - callers look before they leap
        return "", "No Visual Studio C++ toolchain was found.", 127

    with tempfile.TemporaryDirectory(prefix="code-coach-msvc-") as build:
        build_dir = Path(build)
        obj = build_dir / "program.obj"
        exe = build_dir / "program.exe"
        command = (
            f'call "{vcvars}" >nul && '
            f'cl /nologo /EHsc {_MSVC_STD[path.suffix.lower()]} '
            f'"{path}" /Fo"{obj}" /Fe"{exe}"'
        )
        # One string, not a list: an argv list gets re-quoted on the way to
        # cmd and the quotes around these paths come out mangled. `/s` tells
        # cmd to strip the outer quotes and run the rest verbatim.
        try:
            built = subprocess.run(
                f'cmd /s /c "{command}"',
                capture_output=True,
                # The one place that does NOT want UTF-8. This is the
                # compiler talking, not the student's program, and cl
                # writes in the console codepage — so the locale codec
                # is the right reader here and _TEXT_OUT is not. Forcing
                # UTF-8 on it turned four compiler messages into
                # mojibake and clashed with the errors= already here.
                text=True,
                errors="replace",
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return "", f"Compiler timed out after {timeout:g}s.", 124

        if built.returncode != 0 or not exe.exists():
            # cl reports diagnostics on stdout, so that is the error text.
            problem = _strip_cl_echo(built.stdout, path) or built.stderr.strip()
            return "", _cap_output(problem), built.returncode or 1

        # A successful build says only the file name; that is not output.
        try:
            ran = subprocess.run(
                [str(exe)],
                capture_output=True,
                **_TEXT_OUT,
                timeout=timeout,
                stdin=subprocess.DEVNULL,
            )
            return _cap_output(ran.stdout), _cap_output(ran.stderr), ran.returncode
        except subprocess.TimeoutExpired:
            return "", f"Program timed out after {timeout:g}s.", 124


def _kotlin_parts() -> tuple[Path, Path, Path] | None:
    """The compiler, the standard library, and a JVM to run the result."""
    kotlinc = _tool("kotlinc", "kotlinc/bin/kotlinc.bat", "kotlinc/bin/kotlinc")
    java = _tool("java", "jdk-21.0.12.1+1/bin/java.exe", "jdk/bin/java.exe")
    stdlib = _LOCAL_TOOLCHAINS / "kotlinc" / "lib" / "kotlin-stdlib.jar"
    if not kotlinc or not java or not stdlib.exists():
        return None
    return Path(kotlinc), stdlib, Path(java)


def _run_kotlin(path: Path, timeout: float) -> tuple[str, str, int]:
    """Compile one file and run the class that comes out.

    The source is copied to `Main.kt` first, so the class is `MainKt`
    whatever the temporary file was called — Kotlin names the class after
    the file, and a name like `tmp1x7t5lmz.kt` is a class nobody can
    predict from the outside.

    This is four and a half seconds, nearly all of it starting a JVM, and
    that is the cost of pressing Run. The suite does not pay it: it
    compiles a folder of exercises in one call, where the same startup is
    amortised across all of them and each file costs about a seventh of a
    second.
    """
    parts = _kotlin_parts()
    if parts is None:
        return (
            "",
            "kotlinc isn't installed, so this can't be compiled. The "
            "type-along drills still work — only Run needs the toolchain.",
            127,
        )
    kotlinc, stdlib, java = parts
    folder = Path(tempfile.mkdtemp())
    try:
        source = folder / "Main.kt"
        source.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        out = folder / "out"
        env = dict(os.environ)
        env.setdefault("JAVA_HOME", str(java.parent.parent))
        try:
            built = subprocess.run(
                [str(kotlinc), str(source), "-d", str(out)],
                capture_output=True, timeout=timeout, env=env, **_TEXT_OUT,
            )
        except subprocess.TimeoutExpired:
            return "", f"Compiler timed out after {timeout:g}s.", 124
        if built.returncode != 0:
            return "", _cap_output(built.stderr or built.stdout), built.returncode

        classpath = os.pathsep.join([str(out), str(stdlib)])
        try:
            ran = subprocess.run(
                [str(java), "-cp", classpath, "MainKt"],
                capture_output=True, timeout=timeout, **_TEXT_OUT,
                stdin=subprocess.DEVNULL, env=env,
            )
        except subprocess.TimeoutExpired:
            return "", f"Program timed out after {timeout:g}s.", 124
        return _cap_output(ran.stdout), _cap_output(ran.stderr), ran.returncode
    finally:
        shutil.rmtree(folder, ignore_errors=True)


def _swift_home() -> Path | None:
    """Where the Swift for Windows installer put things.

    Not `~/toolchains` like the rest: Swift ships an installer rather than
    an archive, and it chooses its own home. The version is in the folder
    name, so the newest one is taken rather than a version written down
    here that goes stale on the next release.
    """
    roots = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Swift",
        Path(os.environ.get("ProgramFiles", "")) / "Swift",
    ]
    for root in roots:
        if not root.is_dir():
            continue
        toolchains = sorted(
            (root / "Toolchains").glob("*/usr/bin/swiftc.exe"), reverse=True)
        if toolchains:
            return root
    return None


def _swift_env(home: Path) -> dict[str, str] | None:
    """PATH and SDKROOT for a Swift build.

    The installer sets both for the user, and a server started before it
    ran has neither — which shows up as a compiler that exits with
    0xC0000135 and says nothing, because the runtime DLLs are beside the
    compiler rather than on the path. Setting them here means it works
    however the server was started.
    """
    compilers = sorted(
        (home / "Toolchains").glob("*/usr/bin/swiftc.exe"), reverse=True)
    if not compilers:
        return None
    version = compilers[0].parents[2].name.split("+")[0]
    runtime = home / "Runtimes" / version / "usr" / "bin"
    sdk = (home / "Platforms" / version / "Windows.platform" / "Developer"
           / "SDKs" / "Windows.sdk")
    env = dict(os.environ)
    env["PATH"] = os.pathsep.join(
        [str(compilers[0].parent), str(runtime), env.get("PATH", "")])
    if sdk.is_dir():
        env["SDKROOT"] = str(sdk)
    return env


def _run_swift(path: Path, timeout: float) -> tuple[str, str, int]:
    """Build with swiftc and run what came out.

    Compiled rather than run as a script, because `swift file.swift` on
    Windows goes through a JIT that cannot resolve the standard library's
    array symbols — a program as small as declaring a list and printing
    its total fails there and builds fine. Building costs about half a
    second, which is cheaper than the interpreter was anyway.
    """
    home = _swift_home()
    env = _swift_env(home) if home else None
    if home is None or env is None:
        return (
            "",
            "Swift isn't installed, so this can't be compiled. The "
            "type-along drills still work — only Run needs the toolchain.",
            127,
        )
    swiftc = sorted(
        (home / "Toolchains").glob("*/usr/bin/swiftc.exe"), reverse=True)[0]
    exe = path.with_suffix(".exe")
    try:
        built = subprocess.run(
            [str(swiftc), str(path), "-o", str(exe)],
            capture_output=True, timeout=timeout, env=env, **_TEXT_OUT,
            cwd=str(path.parent),
        )
    except subprocess.TimeoutExpired:
        return "", f"Compiler timed out after {timeout:g}s.", 124
    if built.returncode != 0:
        return "", _cap_output(built.stderr or built.stdout), built.returncode

    try:
        ran = subprocess.run(
            [str(exe)], capture_output=True, timeout=timeout, **_TEXT_OUT,
            stdin=subprocess.DEVNULL, env=env,
        )
        return _cap_output(ran.stdout), _cap_output(ran.stderr), ran.returncode
    except subprocess.TimeoutExpired:
        return "", f"Program timed out after {timeout:g}s.", 124
    finally:
        for leftover in (exe, exe.with_suffix(".pdb"), exe.with_suffix(".lib"),
                         exe.with_suffix(".exp"), exe.with_suffix(".obj")):
            try:
                leftover.unlink(missing_ok=True)
            except OSError:
                pass


def _compile_then_run(path: Path, timeout: float) -> tuple[str, str, int]:
    """Build the source, then run what came out."""
    suffix = path.suffix.lower()
    candidates, extra = _COMPILERS[suffix]
    compiler = next((c for c in candidates if shutil.which(c)), None)
    if compiler is None:
        if suffix in _MSVC_STD and _find_vcvars() is not None:
            return _run_msvc(path, timeout)
        names = " or ".join(candidates)
        return (
            "",
            f"{names} isn't on your PATH, so this can't be compiled. The "
            "type-along drills still work — only Run needs the toolchain.",
            127,
        )

    exe = path.with_suffix(".exe" if os.name == "nt" else ".out")
    if suffix == ".rs":
        build = [compiler, *extra, "-o", str(exe), str(path)]
    else:
        build = [compiler, str(path), *extra, "-o", str(exe)]

    try:
        built = subprocess.run(
            build, capture_output=True, timeout=timeout, **_TEXT_OUT
        )
    except subprocess.TimeoutExpired:
        return "", f"Compiler timed out after {timeout:g}s.", 124
    if built.returncode != 0:
        return "", _cap_output(built.stderr or built.stdout), built.returncode

    try:
        ran = subprocess.run(
            [str(exe)],
            capture_output=True,
            **_TEXT_OUT,
            timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
        return _cap_output(ran.stdout), _cap_output(ran.stderr), ran.returncode
    except subprocess.TimeoutExpired:
        return "", f"Program timed out after {timeout:g}s.", 124
    finally:
        for leftover in (exe, exe.with_suffix(".pdb")):
            try:
                leftover.unlink(missing_ok=True)
            except OSError:
                pass


#: Where Flutter usually lands when it is unzipped by hand, which is how
#: its install guide does it. The folder is often not on PATH yet - adding
#: it is a step people skip - so these are looked in as well.
FLUTTER_HOMES = (
    "C:/flutter", "C:/Flutter/flutter", "C:/src/flutter", "~/flutter",
    "~/development/flutter", "~/src/flutter", "/opt/flutter",
)


@lru_cache(maxsize=1)
def dart_path() -> str | None:
    """The dart executable: on PATH, under FLUTTER_ROOT, or in a usual place.

    Flutter carries its own Dart in bin/, so installing Flutter is enough.
    """
    found = shutil.which("dart")
    if found:
        return found
    homes = [os.environ.get("FLUTTER_ROOT", ""), *FLUTTER_HOMES]
    for home in homes:
        if not home:
            continue
        for name in ("dart.bat", "dart.exe", "dart"):
            candidate = Path(home).expanduser() / "bin" / name
            if candidate.is_file():
                return str(candidate)
    return None


def dart_available() -> bool:
    return dart_path() is not None


def c_available() -> bool:
    """Whether C can be compiled here: gcc or clang, or MSVC on Windows."""
    return bool(shutil.which("gcc") or shutil.which("clang") or msvc_available())


def if_c(items) -> tuple:
    """The items, if a C compiler is installed - otherwise none of them."""
    return tuple(items) if c_available() else ()


def if_dart(items) -> tuple:
    """The items, if Dart is installed - otherwise none of them.

    Every collection with Dart content passes it through here, so a
    machine without Dart never offers an exercise it cannot check. The
    content itself is still imported and tested wherever Dart is there.
    """
    return tuple(items) if dart_available() else ()


def run_file(
    path: Path, *, timeout: float | None = None
) -> tuple[str, str, int]:
    """Execute a student file with a wall-clock timeout, in-kernel CPU/memory
    caps, a new session (so a timeout kills the whole process group, not just
    the direct child), and bounded captured output.

    Note: this runs the student's code with the server's own privileges — it is
    NOT a security sandbox. It is a guard against runaway/accidental programs on
    a local, single-user tool. Do not expose this server beyond localhost.
    """
    if timeout is None:
        timeout = default_timeout()
    popen_kwargs: dict[str, Any] = dict(
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        # Tell the child to write UTF-8, since that is what is read back.
        # Node does anyway; Python asks the machine, and on Windows the
        # answer is cp1252 — so `print("…")` arrived as a byte that is
        # not valid UTF-8 and came out as the replacement character.
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        **_TEXT_OUT,
    )
    if _IS_POSIX:
        popen_kwargs["preexec_fn"] = _apply_limits
        popen_kwargs["start_new_session"] = True

    argv = _interpreter_for(path)
    if argv is None:
        tool = {"": "the runtime", ".dart": "Dart", ".js": "Node", ".mjs": "Node"}.get(
            path.suffix.lower(), "the runtime"
        )
        return (
            "",
            f"{tool} isn't on your PATH. Install it and reopen your terminal, "
            "then try Run again.",
            127,
        )

    proc = subprocess.Popen(argv, **popen_kwargs)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return _cap_output(stdout), _cap_output(stderr), proc.returncode
    except subprocess.TimeoutExpired:
        # Kill the whole group so children/grandchildren don't leak.
        if _IS_POSIX:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                proc.kill()
        else:
            proc.kill()
        stdout, stderr = proc.communicate()
        stdout = _cap_output(stdout)
        stderr = _cap_output(stderr)
        if not stderr.strip():
            stderr = f"Program timed out after {timeout:g}s (possible infinite loop)."
        return stdout, stderr, 124


_SUFFIXES = {
    "dart": ".dart",
    "javascript": ".js",
    "typescript": ".ts",
    "c": ".c",
    "cpp": ".cpp",
    "rust": ".rs",
    "python": ".py",
    "go": ".go",
    "php": ".php",
    "lua": ".lua",
    "zig": ".zig",
    "swift": ".swift",
    "kotlin": ".kt",
    "ruby": ".rb",
    "java": ".java",
    "csharp": ".cs",
    "odin": ".odin",
    "lisp": ".lisp",
}

# Languages that compile before they run get a longer clock — the wait is the
# toolchain, not the student's loop. Go and Zig build on every run, and Zig
# in particular is slow the first time it sees a standard library.
_SLOW_LANGUAGES = {
    "dart", "c", "cpp", "rust", "typescript", "go", "zig",
    "java", "csharp", "odin", "lisp", "swift", "kotlin",
}


def run_code(
    code: str,
    *,
    timeout: float | None = None,
    language: str = "python",
) -> tuple[str, str, int]:
    """Run a snippet in the given language. The extension picks the runner."""
    if language == "sql":
        from code_coach.sql_runner import run_sql

        return run_sql(code)
    if language == "postgresql":
        # A server rather than a file, so it has its own runner and its
        # own timeout — the wall-clock ceiling here is for a program
        # this process started, and psql waiting on a connection is a
        # different kind of slow.
        from code_coach.pg_runner import run_postgres

        return run_postgres(code)

    suffix = _SUFFIXES.get(language, ".py")
    if timeout is None:
        timeout = default_timeout(language)

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=suffix,
        encoding="utf-8",
        delete=False,
    ) as tmp:
        tmp.write(code)
        tmp_path = Path(tmp.name)
    try:
        if suffix == ".ts":
            return _run_typescript(tmp_path, timeout)
        if suffix == ".swift":
            return _run_swift(tmp_path, timeout)
        if suffix == ".kt":
            return _run_kotlin(tmp_path, timeout)
        if suffix in _COMPILERS:
            return _compile_then_run(tmp_path, timeout)
        return run_file(tmp_path, timeout=timeout)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass


def _next_from_waypoint(wp: Any) -> dict[str, str | None]:
    """Support both teaching waypoints and legacy `suggest`-only ones."""
    concept = getattr(wp, "concept", None)
    why = getattr(wp, "why", None)
    hint = getattr(wp, "hint", None)
    example = getattr(wp, "example", None) or getattr(wp, "suggest", None)
    return {
        "label": wp.label,
        "concept": concept,
        "why": why,
        "hint": hint,
        "example": example,
        "suggest": example,  # alias
    }


def _score_waypoints(
    lesson: dict[str, Any],
    code: str,
) -> tuple[list[tuple[str, bool]], int, dict[str, str | None] | None]:
    checks: list[tuple[str, bool]] = []
    next_wp: dict[str, str | None] | None = None
    passed = 0

    for wp in lesson["waypoints"]:
        ok = bool(wp.check(code))
        checks.append((wp.label, ok))
        if ok:
            passed += 1
        elif next_wp is None:
            next_wp = _next_from_waypoint(wp)

    return checks, passed, next_wp


def evaluate_code(
    lesson: dict[str, Any],
    code: str,
    *,
    run: bool = True,
    practice_path: Path | None = None,
) -> CoachResult:
    """Score waypoints against `code`; optionally execute it."""
    path = practice_path or Path("<editor>")
    checks, passed, next_wp = _score_waypoints(lesson, code)

    if run:
        stdout, stderr, exit_code = run_code(code)
    else:
        stdout, stderr, exit_code = "", "", 0

    return CoachResult(
        lesson_title=lesson["title"],
        practice_path=path,
        code=code,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        checks=checks,
        passed=passed,
        total=len(lesson["waypoints"]),
        next_label=next_wp["label"] if next_wp else None,
        next_concept=next_wp["concept"] if next_wp else None,
        next_why=next_wp["why"] if next_wp else None,
        next_hint=next_wp["hint"] if next_wp else None,
        next_example=next_wp["example"] if next_wp else None,
        next_suggest=next_wp["suggest"] if next_wp else None,
        ran=run,
    )


def evaluate(lesson: dict[str, Any], practice_path: Path) -> CoachResult:
    code = load_code(practice_path)
    return evaluate_code(lesson, code, run=True, practice_path=practice_path)


def result_to_dict(result: CoachResult) -> dict[str, Any]:
    return {
        "lesson_title": result.lesson_title,
        "practice_path": str(result.practice_path),
        "code": result.code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.exit_code,
        "checks": [
            {"label": label, "passed": ok} for label, ok in result.checks
        ],
        "passed": result.passed,
        "total": result.total,
        "next_label": result.next_label,
        "next_concept": result.next_concept,
        "next_why": result.next_why,
        "next_hint": result.next_hint,
        "next_example": result.next_example,
        "next_suggest": result.next_suggest,
        "ran": result.ran,
        "complete": result.complete,
    }


def format_report(result: CoachResult) -> str:
    lines: list[str] = []
    lines.append("=== Code Coach ===")
    lines.append(f"Lesson: {result.lesson_title}")
    lines.append(f"File:   {result.practice_path}")
    lines.append("")

    for i, (label, ok) in enumerate(result.checks, start=1):
        mark = "x" if ok else " "
        lines.append(f"  [{mark}] {i}. {label}")

    lines.append("")
    lines.append(f"Position: {result.passed}/{result.total}")

    if result.ran and result.exit_code != 0:
        lines.append("")
        lines.append("Runtime error:")
        lines.append(result.stderr.strip() or "(no details)")
        lines.append("")
        lines.append("Fix the error, then try again.")
        return "\n".join(lines)

    if result.ran and result.stdout.strip():
        lines.append("")
        lines.append("Program output:")
        for line in result.stdout.rstrip().splitlines():
            lines.append(f"  | {line}")

    lines.append("")
    if result.complete:
        lines.append("Status: lesson complete.")
    else:
        lines.append(f"Next goal: {result.next_label}")
        if result.next_concept:
            lines.append(f"Concept:  {result.next_concept}")
        if result.next_why:
            lines.append(f"Why:      {result.next_why}")
        if result.next_hint:
            lines.append(f"Hint:     {result.next_hint}")
        if result.next_example:
            lines.append("Example pattern (your values can differ):")
            lines.append(f"  {result.next_example}")

    return "\n".join(lines)
