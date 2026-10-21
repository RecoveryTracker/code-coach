"""Run one short program for real, in a throwaway folder, and report what it printed.

Used by "Run it" on a card and to build the cards the user adds. It is the user's own code on their own
machine, like the rest of Code Coach, but it is kept tame: a bare environment (nothing of the server's
reaches it), an empty working folder, no input (stdin is closed), 5 seconds, and at most 64 KB of output.
The tests do not trust this module: they run the built-in cards with their own subprocess calls.

Python and JavaScript are run straight away. Every other language goes through `toolchains.plan`, which uses
the engine's own toolchain lookup (the one a workbook Run uses): compiled languages are built first - the
compile has its own, longer ceiling (Visual Studio's first start alone can take 3 seconds) and the 5 seconds
are for the program - and then the program is run under the same rules. A few tools compile inside the run
command (Java's launcher, `dotnet run`, `dart run`, ABCL); those get the compile allowance on top, and say so
(`Plan.one_step`). Compiler warnings are dropped: only a failed build says anything, and then it is a compile
error, not output.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from . import langs, toolchains
from .toolchains import RunnerUnavailable

__all__ = ["COMPILE_SECONDS", "LIMIT_SECONDS", "MAX_OUTPUT", "RunResult", "RunnerUnavailable", "available_languages",
           "c_available", "error_name", "last_error_line", "run_program", "run_twice", "tidy_paths"]

#: A program that runs longer than this is stopped (the same ceiling as the cards' own tests).
LIMIT_SECONDS = 5.0
#: Output beyond this is cut off.
MAX_OUTPUT = 64_000
#: Building a program may take this long (the program itself still gets LIMIT_SECONDS).
COMPILE_SECONDS = 15.0


@dataclass(frozen=True)
class RunResult:
    stdout: str
    stderr: str
    returncode: int
    seconds: float
    timed_out: bool
    #: A compiled language: the program did not build; `stderr` holds the compiler's words.
    compile_error: bool = False

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out and not self.compile_error


def _read(path: Path) -> str:
    data = path.read_bytes()[:MAX_OUTPUT]
    return data.decode("utf-8", errors="replace").replace("\r\n", "\n")


def c_available() -> bool:
    """Whether a C compiler is installed (looked up each time, so a test can say there is none)."""
    from code_coach import engine

    return engine.c_available()


def available_languages() -> list[str]:
    """The registered languages whose toolchain is installed on this machine, in display order."""
    return [lang.id for lang in langs.LANGS if toolchains.available(lang.id)]


def _first_error(diagnostics: str) -> str:
    """The first line that is an error (clang, gcc, cl, rustc, tsc... all say so), else the first line there is."""
    lines = [ln.strip() for ln in diagnostics.splitlines() if ln.strip()]
    for line in lines:
        if re.search(r"\berror\b", line, re.I):
            return line
    # Go says "undefined: x" under a "# command-line-arguments" heading: take the first line about the file
    for line in lines:
        if _SNIPPET_PATH.search(line) or line.startswith(("snippet.", "Main.kt")):
            return line
    plain = [ln for ln in lines if not ln.startswith("#")]
    return (plain or lines or ["the compiler gave no reason"])[0]


#: A path to the throwaway source file (snippet.c, snippet.rs, Main.kt).
_SNIPPET_PATH = re.compile(r"(?:[A-Za-z]:)?[^\s\"'(]*?[\\/](snippet\.\w+|Main\.kt)")


def tidy_paths(text: str) -> str:
    """Show `snippet.c`, not the throwaway folder it was in."""
    return _SNIPPET_PATH.sub(r"\1", text)


def _execute(language: str, code: str, timeout: float, seeds: tuple[int, ...]) -> list[RunResult]:
    """Build once (if the language builds), then run once per seed. A build that fails is one result."""
    from code_coach.canvas.pyharness.session import child_flags, kill_tree, remove_folder

    folder = Path(tempfile.mkdtemp(prefix="gotcha_run_"))
    try:
        plan = toolchains.plan(language, folder, code, hashseed=seeds[0])
        if plan.build is not None:
            started = time.monotonic()
            built, diagnostics = plan.build(COMPILE_SECONDS)
            if not built:
                return [RunResult("", tidy_paths(diagnostics), 1, time.monotonic() - started, False,
                                  compile_error=True)]
        limit = timeout + (COMPILE_SECONDS if plan.one_step else 0.0)
        swap = langs.get(language).output_on_stderr
        results: list[RunResult] = []
        for seed in seeds:
            env = dict(plan.env)
            if language == "python":
                env["PYTHONHASHSEED"] = str(seed)
            out_path, err_path = folder / "out.txt", folder / "err.txt"
            started = time.monotonic()  # the program's own clock: a separate build does not count against it
            timed_out = False
            with open(out_path, "wb") as out, open(err_path, "wb") as err:
                proc = subprocess.Popen(plan.run, cwd=folder, env=env, stdin=subprocess.DEVNULL,
                                        stdout=out, stderr=err, creationflags=child_flags())
                try:
                    proc.wait(timeout=limit)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    kill_tree(proc)
            seconds = time.monotonic() - started
            stdout, stderr = _read(out_path), tidy_paths(_read(err_path))
            if swap and not timed_out and proc.returncode == 0:
                stdout, stderr = stderr, stdout
            if (plan.compile_marker and not timed_out and proc.returncode != 0
                    and re.search(plan.compile_marker, stdout + "\n" + stderr)):
                # a one-step tool's failed build: the compiler's words, however it said them
                words = tidy_paths((stdout + "\n" + stderr).strip())
                results.append(RunResult("", words, 1, seconds, False, compile_error=True))
                break
            code = -9 if timed_out else proc.returncode
            if (plan.failure_marker and code == 0
                    and re.search(plan.failure_marker, stdout + "\n" + stderr, re.M)):
                code = 1  # the tool exited 0 although the program failed
            results.append(RunResult(stdout, stderr, code, seconds, timed_out))
            if timed_out:
                break
        return results
    finally:
        remove_folder(folder)


def run_program(language: str, code: str, *, hashseed: int = 0,
                timeout: float = LIMIT_SECONDS) -> RunResult:
    """Run `code` as a program of `language`; never raises for the program's own failures."""
    return _execute(language, code, timeout, (hashseed,))[0]


def run_twice(language: str, code: str, *, timeout: float = LIMIT_SECONDS) -> tuple[RunResult, RunResult]:
    """Two runs to compare (Python with two hash seeds; every other language from one build).

    If the first run timed out the second is just a copy of it - there is no point waiting again."""
    results = _execute(language, code, timeout, (0, 1))
    return results[0], results[-1]


_PY_ERROR = re.compile(r"^([A-Za-z_][\w.]*)(?::|$)")
_JS_ERROR = re.compile(r"^(\w*(?:Error|Exception)):", re.M)


def error_name(language: str, result: RunResult) -> str:
    """The name of the uncaught error that ended the program ("NameError"), or "" if none did.

    Only Python and JavaScript have error names to speak of. For every other language a build that failed is
    "CompileError", and a program that ended badly is reported by its exit code ("exit code 139",
    "exit code 3221225477" - the numbers differ by system)."""
    if result.ok:
        return ""
    if language == "python":
        for line in reversed(result.stderr.strip().splitlines()):
            m = _PY_ERROR.match(line.strip())
            if m and not line.startswith(" "):
                return m.group(1).split(".")[-1]
        return ""
    if language == "javascript":
        m = _JS_ERROR.search(result.stderr)
        return m.group(1) if m else ""
    if result.compile_error:
        return "CompileError"
    return "timeout" if result.timed_out else f"exit code {result.returncode}"


def last_error_line(result: RunResult) -> str:
    """The line a person would read from stderr: the last non-blank one, trimmed.

    For a build that failed it is the compiler's first error instead (the last line is only a count)."""
    if result.compile_error:
        return _first_error(result.stderr)[:200]
    lines = [ln.strip() for ln in result.stderr.strip().splitlines() if ln.strip()]
    return lines[-1][:200] if lines else ""
