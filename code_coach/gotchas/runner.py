"""Run one short program for real, in a throwaway folder, and report what it printed.

Used by "Run it" on a card and to build the cards the user adds. It is the user's own code on their own
machine, like the rest of Code Coach, but it is kept tame: a bare environment (nothing of the server's
reaches it), an empty working folder, no input (stdin is closed), 5 seconds, and at most 64 KB of output.
The tests do not trust this module: they run the built-in cards with their own subprocess calls.

C is compiled first (by the engine's own C building code: gcc, clang or Visual Studio, whichever is installed)
and then the program is run under the same rules. The compile has its own, longer ceiling (Visual Studio's
first start alone can take 3 seconds); the 5 seconds are for the program. Compiler warnings are dropped:
only a failed build says anything, and then it is a compile error, not output.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

#: A program that runs longer than this is stopped (the same ceiling as the cards' own tests).
LIMIT_SECONDS = 5.0
#: Output beyond this is cut off.
MAX_OUTPUT = 64_000


#: Building a C program may take this long (the program itself still gets LIMIT_SECONDS).
COMPILE_SECONDS = 15.0


class RunnerUnavailable(RuntimeError):
    """The language's runtime is not installed (no node on the PATH, no C compiler)."""


@dataclass(frozen=True)
class RunResult:
    stdout: str
    stderr: str
    returncode: int
    seconds: float
    timed_out: bool
    #: C only: the program did not build; `stderr` holds the compiler's words.
    compile_error: bool = False

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out and not self.compile_error


def _command(language: str, script: Path) -> list[str]:
    if language == "python":
        # -s/-B: no user site, no .pyc. Not -I: that would also ignore PYTHONHASHSEED.
        return [sys.executable, "-s", "-B", "-X", "utf8", str(script)]
    node = shutil.which("node")
    if node is None:
        raise RunnerUnavailable("Node is not installed, so JavaScript cannot be run here.")
    return [node, str(script)]


def _env(hashseed: int) -> dict[str, str]:
    from code_coach.canvas.pyharness.session import child_env

    env = child_env()
    env["PYTHONHASHSEED"] = str(hashseed)
    return env


def _read(path: Path) -> str:
    data = path.read_bytes()[:MAX_OUTPUT]
    return data.decode("utf-8", errors="replace").replace("\r\n", "\n")


def c_available() -> bool:
    """Whether a C compiler is installed (looked up each time, so a test can say there is none)."""
    from code_coach import engine

    return engine.c_available()


def available_languages() -> list[str]:
    """The languages a program can be run in on this machine: C only with a compiler."""
    return ["python", "javascript", *(["c"] if c_available() else [])]


def _first_error(diagnostics: str) -> str:
    """The first line that is an error (clang, gcc and cl all say so), else the first line there is."""
    lines = [ln.strip() for ln in diagnostics.splitlines() if ln.strip()]
    for line in lines:
        if re.search(r"\berror\b", line):
            return line
    return lines[0] if lines else "the compiler gave no reason"


_SNIPPET_PATH = re.compile(r"(?:[A-Za-z]:)?[^\s\"'(]*?[\\/](snippet\.(?:py|js|c))")


def tidy_paths(text: str) -> str:
    """Show `snippet.c`, not the throwaway folder it was in."""
    return _SNIPPET_PATH.sub(r"\1", text)


def _run_c(code: str, timeout: float, times: int = 1) -> list[RunResult]:
    """Build once, run `times` times (a compile that fails is one result)."""
    from code_coach import engine
    from code_coach.canvas.pyharness.session import child_env, child_flags, kill_tree, remove_folder

    if not engine.c_available():
        raise RunnerUnavailable("No C compiler is installed (gcc, clang or Visual Studio), so C cannot be run here.")
    folder = Path(tempfile.mkdtemp(prefix="gotcha_run_"))
    try:
        src = folder / "snippet.c"
        exe = folder / ("snippet.exe" if os.name == "nt" else "snippet.out")
        src.write_text(code + "\n", encoding="utf-8", newline="\n")
        started = time.monotonic()
        built, diagnostics = engine.compile_c(src, exe, COMPILE_SECONDS)
        if not built:
            return [RunResult("", tidy_paths(diagnostics), 1, time.monotonic() - started, False,
                              compile_error=True)]
        results = []
        for _ in range(times):
            out_path, err_path = folder / "out.txt", folder / "err.txt"
            started = time.monotonic()  # the program's own clock: the compile does not count against it
            timed_out = False
            with open(out_path, "wb") as out, open(err_path, "wb") as err:
                proc = subprocess.Popen(
                    [str(exe)], cwd=folder, env=child_env(), stdin=subprocess.DEVNULL,
                    stdout=out, stderr=err, creationflags=child_flags(),
                )
                try:
                    proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    kill_tree(proc)
            seconds = time.monotonic() - started
            results.append(RunResult(_read(out_path), _read(err_path), -9 if timed_out else proc.returncode,
                                     seconds, timed_out))
            if timed_out:
                break
        return results
    finally:
        remove_folder(folder)


def run_program(language: str, code: str, *, hashseed: int = 0,
                timeout: float = LIMIT_SECONDS) -> RunResult:
    """Run `code` as a script of `language`; never raises for the program's own failures."""
    from code_coach.canvas.pyharness.session import child_flags, kill_tree, remove_folder

    if language == "c":
        return _run_c(code, timeout)[0]
    folder = Path(tempfile.mkdtemp(prefix="gotcha_run_"))
    try:
        script = folder / ("snippet.py" if language == "python" else "snippet.js")
        script.write_text(code + "\n", encoding="utf-8", newline="\n")
        out_path, err_path = folder / "out.txt", folder / "err.txt"
        started = time.monotonic()
        timed_out = False
        with open(out_path, "wb") as out, open(err_path, "wb") as err:
            proc = subprocess.Popen(
                _command(language, script), cwd=folder, env=_env(hashseed),
                stdin=subprocess.DEVNULL, stdout=out, stderr=err, creationflags=child_flags(),
            )
            try:
                proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                kill_tree(proc)
        seconds = time.monotonic() - started
        return RunResult(_read(out_path), _read(err_path), -9 if timed_out else proc.returncode,
                         seconds, timed_out)
    finally:
        remove_folder(folder)


def run_twice(language: str, code: str, *, timeout: float = LIMIT_SECONDS) -> tuple[RunResult, RunResult]:
    """Two runs to compare (Python and JavaScript with different hash seeds; C from one build).

    If the first run timed out the second is just a copy of it - there is no point waiting again."""
    if language == "c":
        results = _run_c(code, timeout, times=2)
        return results[0], results[-1]
    first = run_program(language, code, hashseed=0, timeout=timeout)
    if first.timed_out:
        return first, first
    return first, run_program(language, code, hashseed=1, timeout=timeout)


_PY_ERROR = re.compile(r"^([A-Za-z_][\w.]*)(?::|$)")
_JS_ERROR = re.compile(r"^(\w*(?:Error|Exception)):", re.M)


def error_name(language: str, result: RunResult) -> str:
    """The name of the uncaught error that ended the program ("NameError"), or "" if none did.

    C has no error names: a build that failed is "CompileError", and a program that ended badly is
    reported by its exit code ("exit code 139", "exit code 3221225477" - the numbers differ by system)."""
    if result.ok:
        return ""
    if language == "c":
        if result.compile_error:
            return "CompileError"
        return "timeout" if result.timed_out else f"exit code {result.returncode}"
    if language == "python":
        for line in reversed(result.stderr.strip().splitlines()):
            m = _PY_ERROR.match(line.strip())
            if m and not line.startswith(" "):
                return m.group(1).split(".")[-1]
        return ""
    m = _JS_ERROR.search(result.stderr)
    return m.group(1) if m else ""


def last_error_line(result: RunResult) -> str:
    """The line a person would read from stderr: the last non-blank one, trimmed.

    For a C build that failed it is the compiler's first error instead (the last line is only a count)."""
    if result.compile_error:
        return _first_error(result.stderr)[:200]
    lines = [ln.strip() for ln in result.stderr.strip().splitlines() if ln.strip()]
    return lines[-1][:200] if lines else ""
