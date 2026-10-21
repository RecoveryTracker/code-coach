"""How to build and run one program in each language the quiz knows, using the engine's own toolchain lookup.

`plan(language, folder, code)` writes the source into the throwaway `folder` and says how to turn it into a
running program: an optional build step (a compiler, which gets the machine's environment because compilers
need it) and the command that runs the result (which gets a bare environment: nothing of the server's keys or
paths reaches the program). The runner (`runner.py`) owns the folder, the clocks and the cleanup.

A few tools build and run in one go (`java file.java`, `dotnet run file.cs`, `dart run`, ABCL): those are
`one_step`, the program's clock includes the tool's start-up, and the runner allows for that.

`available(language)` is the probe: whether the toolchain is installed here (it rides on the engine's cached
PATH lookups, so it is cheap and notices an install within a minute).
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from code_coach import engine

#: A build step: seconds allowed -> (it built, the compiler's own words).
Build = Callable[[float], tuple[bool, str]]


class RunnerUnavailable(RuntimeError):
    """The language's runtime is not installed (no node on the PATH, no C compiler)."""


@dataclass
class Plan:
    #: The command that runs the program (after the build, if there is one).
    run: list[str]
    #: Its environment.
    env: dict[str, str]
    build: Build | None = None
    #: The tool compiles inside the run command: the run gets extra time for that.
    one_step: bool = False
    #: One-step tools report a failed build as a failed run (dotnet on stdout, java and dart on stderr): a run
    #: that exits non-zero with this in its output is a compile error, not a program that crashed.
    compile_marker: str = ''
    #: A tool that exits 0 even when the program failed (ABCL's --batch says "Error loading ..." and carries on):
    #: a run that exits 0 with this in its output is a failed run (exit code 1), never an answer.
    failure_marker: str = ''
    #: Environment overrides for the build step (None: the machine's own).
    build_env: dict[str, str] | None = None
    #: The file the build reads, for tidying a compiler's paths out of its messages.
    source: Path | None = None
    cleanup: list[Path] = field(default_factory=list)


def _bare() -> dict[str, str]:
    from code_coach.canvas.pyharness.session import child_env

    return child_env()


#: What the toolchains that start other tools need to find themselves (no keys, no tokens): where things
#: are installed and where to cache, never the server's secrets.
_TOOL_KEYS = ("PATH", "PATHEXT", "WINDIR", "COMSPEC", "ComSpec", "USERPROFILE", "HOME", "HOMEDRIVE", "HOMEPATH",
              "LOCALAPPDATA", "APPDATA", "PROGRAMDATA", "ProgramFiles", "ProgramFiles(x86)", "ProgramW6432",
              "JAVA_HOME", "NUMBER_OF_PROCESSORS", "PROCESSOR_ARCHITECTURE", "OS", "USERNAME")


def _tool_env(folder: Path | None = None, **extra: str) -> dict[str, str]:
    env = _bare()
    for key in _TOOL_KEYS:
        if key in os.environ:
            env[key] = os.environ[key]
    if folder is not None:
        # what the tool would leave in the temp folder is left in the throwaway one instead
        scratch = folder / "tmp"
        scratch.mkdir(exist_ok=True)
        env["TEMP"] = env["TMP"] = str(scratch)
    env.update(extra)
    return env


def _exe(folder: Path, name: str = "snippet") -> Path:
    return folder / (f"{name}.exe" if os.name == "nt" else f"{name}.out")


def _which_exe(path: Path) -> str | None:
    argv = engine._interpreter_for(path)
    return argv[0] if argv else None


def _interpreter(src: Path) -> list[str]:
    argv = engine._interpreter_for(src)
    if argv is None:
        raise RunnerUnavailable(f"The toolchain for {src.suffix} is not installed, so it cannot be run here.")
    return argv


# ── Builds ───────────────────────────────────────────────────────────────


def _run_tool(argv: list[str], cwd: Path, env: dict[str, str] | None, timeout: float) -> tuple[int, str, bool]:
    """Run a build tool to the end (or the timeout, killing its whole tree): (exit code, its words, timed out)."""
    import subprocess
    import tempfile

    from code_coach.canvas.pyharness.session import child_flags, kill_tree

    with tempfile.TemporaryFile() as out:
        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=out,
                                stderr=subprocess.STDOUT, creationflags=child_flags())
        timed_out = False
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            kill_tree(proc)
        out.seek(0)
        text = out.read(200_000).decode("utf-8", errors="replace").replace("\r\n", "\n")
    return (-9 if timed_out else proc.returncode), text.strip(), timed_out


def _tool_build(argv: list[str], cwd: Path, exe: Path, env: dict[str, str] | None = None) -> Build:
    def build(timeout: float) -> tuple[bool, str]:
        code, text, timed_out = _run_tool(argv, cwd, env, timeout)
        if timed_out:
            return False, f"The compiler timed out after {timeout:g}s."
        return code == 0 and exe.exists(), text

    return build


def _native_build(suffix: str, src: Path, exe: Path) -> Build:
    """C++ and Rust the way the engine's own Run builds them: g++/clang++/rustc, else Visual Studio for C++."""

    def build(timeout: float) -> tuple[bool, str]:
        candidates, extra = engine._COMPILERS[suffix]
        compiler = next((c for c in candidates if engine._which(c)), None)
        if compiler is None:
            if suffix in engine._MSVC_STD and engine._find_vcvars() is not None:
                code, text = engine._msvc_compile(src, exe.with_suffix(".obj"), exe, timeout)
                return code == 0, text
            raise RunnerUnavailable(f"No {' or '.join(candidates)} is installed, so {suffix} cannot be built here.")
        if suffix == ".rs":
            argv = [engine._which(compiler) or compiler, *extra, "-o", str(exe), str(src)]
        else:
            argv = [engine._which(compiler) or compiler, str(src), *extra, "-o", str(exe)]
        return _tool_build(argv, src.parent, exe)(timeout)

    return build


def _c_build(src: Path, exe: Path) -> Build:
    def build(timeout: float) -> tuple[bool, str]:
        return engine.compile_c(src, exe, timeout)

    return build


# ── The plans ────────────────────────────────────────────────────────────


def _ts_plan(folder: Path, src: Path) -> Plan:
    tsc, node = engine._find_tsc(), engine._which("node")
    if tsc is None or node is None:
        raise RunnerUnavailable("TypeScript needs Node and the TypeScript compiler (npm install in web/).")
    built = src.with_suffix(".js")

    def build(timeout: float) -> tuple[bool, str]:
        argv = [node, str(tsc), str(src), "--target", "es2020", "--module", "commonjs", "--skipLibCheck",
                "--noEmitOnError", "--strict"]
        code, text, timed_out = _run_tool(argv, folder, None, timeout)
        if timed_out:
            return False, f"The compiler timed out after {timeout:g}s."
        return code == 0 and built.exists(), text

    return Plan([node, str(built)], _bare(), build=build)


def _kotlin_plan(folder: Path, src: Path) -> Plan:
    parts = engine._kotlin_parts()
    if parts is None:
        raise RunnerUnavailable("kotlinc is not installed, so Kotlin cannot be run here.")
    kotlinc, stdlib, java = parts
    main = folder / "Main.kt"
    out = folder / "out"
    env = dict(os.environ)
    env.setdefault("JAVA_HOME", str(java.parent.parent))

    def build(timeout: float) -> tuple[bool, str]:
        main.write_text(src.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
        code, text, timed_out = _run_tool([str(kotlinc), str(main), "-d", str(out)], folder, env, timeout)
        if timed_out:
            return False, f"The compiler timed out after {timeout:g}s."
        return code == 0 and out.exists(), text

    run_env = _tool_env(JAVA_HOME=str(java.parent.parent))
    return Plan([str(java), "-cp", os.pathsep.join([str(out), str(stdlib)]), "MainKt"], run_env, build=build,
                source=main)


def _swift_plan(folder: Path, src: Path) -> Plan:
    home = engine._swift_home()
    env = engine._swift_env(home) if home else None
    if home is None or env is None:
        raise RunnerUnavailable("Swift is not installed, so it cannot be run here.")
    swiftc = sorted((home / "Toolchains").glob("*/usr/bin/swiftc.exe"), reverse=True)[0]
    exe = _exe(folder)
    run_env = _bare()
    run_env["PATH"] = env["PATH"]  # the Swift runtime's DLLs sit beside the compiler
    return Plan([str(exe)], run_env, build=_tool_build([str(swiftc), str(src), "-o", str(exe)], folder, exe, env))


def _go_plan(folder: Path, src: Path) -> Plan:
    go = _which_exe(src)
    if go is None:
        raise RunnerUnavailable("Go is not installed, so it cannot be run here.")
    exe = _exe(folder)
    env = _tool_env(GOFLAGS="-mod=mod", GOTOOLCHAIN="local", GO111MODULE="off", CGO_ENABLED="0")
    env["GOPATH"] = str(folder / "gopath")
    return Plan([str(exe)], _bare(), build=_tool_build([go, "build", "-o", str(exe), str(src)], folder, exe, env),
                build_env=env)


def _zig_plan(folder: Path, src: Path) -> Plan:
    zig = _which_exe(src)
    if zig is None:
        raise RunnerUnavailable("Zig is not installed, so it cannot be run here.")
    exe = _exe(folder)
    env = _tool_env()
    argv = [zig, "build-exe", str(src), f"-femit-bin={exe}"]
    return Plan([str(exe)], _bare(), build=_tool_build(argv, folder, exe, env))


def _odin_plan(folder: Path, src: Path) -> Plan:
    odin = _which_exe(src)
    if odin is None:
        raise RunnerUnavailable("Odin is not installed, so it cannot be run here.")
    exe = _exe(folder)
    env = _tool_env()
    argv = [odin, "build", str(src), "-file", f"-out:{exe}"]
    return Plan([str(exe)], _bare(), build=_tool_build(argv, folder, exe, env))


def _sql_plan(folder: Path, src: Path) -> Plan:
    driver = folder / "sqlrun.py"
    driver.write_text(SQL_DRIVER, encoding="utf-8", newline="\n")
    return Plan([sys.executable, "-I", "-s", "-B", "-X", "utf8", str(driver), str(src)], _bare())


#: Runs a SQL program on a throwaway in-memory SQLite and prints the rows of its last SELECT on one line:
#: `a|b` per row, rows joined with `; `, NULL as NULL. An error is printed to stderr and exits 1.
SQL_DRIVER = r'''
import sqlite3
import sys

text = open(sys.argv[1], encoding="utf-8").read()
db = sqlite3.connect(":memory:")
statements, start = [], 0
for i, ch in enumerate(text):
    if ch == ";" and sqlite3.complete_statement(text[start:i + 1]):
        statements.append(text[start:i + 1].strip())
        start = i + 1
if text[start:].strip():
    statements.append(text[start:].strip())
rows = None
try:
    for statement in statements:
        cursor = db.execute(statement)
        if cursor.description is not None:
            rows = cursor.fetchall()
except sqlite3.Error as exc:
    sys.stderr.write(f"SQLError: {exc}\n")
    sys.exit(1)
if rows is None:
    sys.exit(0)


def show(value):
    if value is None:
        return "NULL"
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, bytes):
        return "x'" + value.hex() + "'"
    return str(value)


print("; ".join("|".join(show(v) for v in row) for row in rows))
'''


def plan(language: str, folder: Path, code: str, *, hashseed: int = 0) -> Plan:
    """Write the program into `folder` and say how to build and run it. Raises RunnerUnavailable."""
    from . import langs

    ext = langs.get(language).ext
    src = folder / f"snippet.{ext}"
    src.write_text(code + "\n", encoding="utf-8", newline="\n")
    if language == "python":
        # -s/-B: no user site, no .pyc. Not -I: that would also ignore PYTHONHASHSEED.
        env = _bare()
        env["PYTHONHASHSEED"] = str(hashseed)
        return Plan([sys.executable, "-s", "-B", "-X", "utf8", str(src)], env)
    if language == "javascript":
        node = engine._which("node")
        if node is None:
            raise RunnerUnavailable("Node is not installed, so JavaScript cannot be run here.")
        return Plan([node, str(src)], _bare())
    if language == "c":
        if not engine.c_available():
            raise RunnerUnavailable(
                "No C compiler is installed (gcc, clang or Visual Studio), so C cannot be run here.")
        return Plan([str(_exe(folder))], _bare(), build=_c_build(src, _exe(folder)), source=src)
    if language == "cpp":
        return Plan([str(_exe(folder))], _bare(), build=_native_build(".cpp", src, _exe(folder)), source=src)
    if language == "rust":
        if engine._which("rustc") is None:
            raise RunnerUnavailable("rustc is not installed, so Rust cannot be run here.")
        return Plan([str(_exe(folder))], _bare(), build=_native_build(".rs", src, _exe(folder)), source=src)
    if language == "typescript":
        return _ts_plan(folder, src)
    if language == "kotlin":
        return _kotlin_plan(folder, src)
    if language == "swift":
        return _swift_plan(folder, src)
    if language == "go":
        return _go_plan(folder, src)
    if language == "zig":
        return _zig_plan(folder, src)
    if language == "odin":
        return _odin_plan(folder, src)
    if language == "sql":
        return _sql_plan(folder, src)
    if language in ("ruby", "php", "lua"):
        return Plan(_interpreter(src), _tool_env(folder))
    if language == "dart":
        from code_coach.farm.stubs.render import dart_executable

        dart = dart_executable()
        if dart is None:
            raise RunnerUnavailable("Dart is not installed, so it cannot be run here.")
        
        return Plan([dart, "run", str(src)], _tool_env(folder), one_step=True, compile_marker=r": Error: ")
    if language in ("java", "csharp", "lisp"):
        argv = _interpreter(src)
        extra = {"DOTNET_NOLOGO": "1", "DOTNET_CLI_TELEMETRY_OPTOUT": "1", "DOTNET_SKIP_FIRST_TIME_EXPERIENCE": "1",
                 "MSBUILDDISABLENODEREUSE": "1"}
        if language == "csharp":
            # No compiler server (VBCSCompiler): it outlives the run, holds the throwaway folder open so it
            # cannot be deleted, and sits in memory for minutes. (The env var of that name is not enough.)
            # NuGetAudit off: the vulnerability-data check is not needed for a one-file program, needs the
            # network, and when two builds overlap it prints a NU1900 warning into the program's stdout.
            argv = [*argv[:-1], "-p:UseSharedCompilation=false", "-p:NuGetAudit=false", argv[-1]]
        marker = {"csharp": r"error CS\d+", "java": r"error: compilation failed|\.java:\d+: error:"}.get(language, "")
        failure = r"^Error loading |Exception in thread" if language == "lisp" else ""
        return Plan(argv, _tool_env(folder, **(extra if language == "csharp" else {})), one_step=True,
                    compile_marker=marker, failure_marker=failure)
    raise RunnerUnavailable(f"There is no way to run {language} here.")


def available(language: str) -> bool:
    """Whether this language's toolchain is installed on this machine."""
    if language == "python":
        return True
    if language == "sql":
        return True
    if language == "javascript":
        return engine._which("node") is not None
    if language == "c":
        return engine.c_available()
    if language == "cpp":
        return bool(engine._which("g++") or engine._which("clang++") or engine.msvc_available())
    if language == "rust":
        return engine._which("rustc") is not None
    if language == "typescript":
        return engine.typescript_available()
    if language == "kotlin":
        return engine._kotlin_parts() is not None
    if language == "swift":
        home = engine._swift_home()
        return home is not None and engine._swift_env(home) is not None
    if language == "dart":
        return engine.dart_available()
    from . import langs

    if language in langs.BY_ID:
        return engine._interpreter_for(Path(f"probe.{langs.get(language).ext}")) is not None
    return False
