"""Run one short program for real, in a throwaway folder, and report what it printed.

Used by "Run it" on a card and to build the cards the user adds. It is the user's own code on their own
machine, like the rest of Code Coach, but it is kept tame: a bare environment (nothing of the server's
reaches it), an empty working folder, no input (stdin is closed), 5 seconds, and at most 64 KB of output.
The tests do not trust this module: they run the built-in cards with their own subprocess calls.
"""

from __future__ import annotations

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


class RunnerUnavailable(RuntimeError):
    """The language's runtime is not installed (no node on the PATH)."""


@dataclass(frozen=True)
class RunResult:
    stdout: str
    stderr: str
    returncode: int
    seconds: float
    timed_out: bool

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out


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


def run_program(language: str, code: str, *, hashseed: int = 0,
                timeout: float = LIMIT_SECONDS) -> RunResult:
    """Run `code` as a script of `language`; never raises for the program's own failures."""
    from code_coach.canvas.pyharness.session import child_flags, kill_tree, remove_folder

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


_PY_ERROR = re.compile(r"^([A-Za-z_][\w.]*)(?::|$)")
_JS_ERROR = re.compile(r"^(\w*(?:Error|Exception)):", re.M)


def error_name(language: str, result: RunResult) -> str:
    """The name of the uncaught error that ended the program ("NameError"), or "" if none did."""
    if result.ok:
        return ""
    if language == "python":
        for line in reversed(result.stderr.strip().splitlines()):
            m = _PY_ERROR.match(line.strip())
            if m and not line.startswith(" "):
                return m.group(1).split(".")[-1]
        return ""
    m = _JS_ERROR.search(result.stderr)
    return m.group(1) if m else ""


def last_error_line(result: RunResult) -> str:
    """The line a person would read from stderr: the last non-blank one, trimmed."""
    lines = [ln.strip() for ln in result.stderr.strip().splitlines() if ln.strip()]
    return lines[-1][:200] if lines else ""
