"""
Code Coach engine — Stage 1.5

Looks at student code (path or in-memory), optionally runs it,
scores waypoints, returns teaching-oriented next step (not personal data).
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import signal
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

# Cap runaway student programs (e.g. while True).
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


def _interpreter_for(path: Path) -> list[str] | None:
    """The command that runs this file, or None if we can't run its kind.

    Dart is found on PATH; `shutil.which` resolves the .bat shim that the
    Flutter SDK installs on Windows.
    """
    suffix = path.suffix.lower()
    if suffix == ".py":
        return [sys.executable, str(path)]
    if suffix == ".dart":
        dart = shutil.which("dart")
        return [dart, "run", str(path)] if dart else None
    if suffix in (".js", ".mjs"):
        node = shutil.which("node")
        return [node, str(path)] if node else None
    return [sys.executable, str(path)]


def dart_available() -> bool:
    return shutil.which("dart") is not None


def run_file(path: Path, *, timeout: float = RUN_TIMEOUT_SECONDS) -> tuple[str, str, int]:
    """Execute a student file with a wall-clock timeout, in-kernel CPU/memory
    caps, a new session (so a timeout kills the whole process group, not just
    the direct child), and bounded captured output.

    Note: this runs the student's code with the server's own privileges — it is
    NOT a security sandbox. It is a guard against runaway/accidental programs on
    a local, single-user tool. Do not expose this server beyond localhost.
    """
    popen_kwargs: dict[str, Any] = dict(
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        text=True,
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


_SUFFIXES = {"dart": ".dart", "javascript": ".js", "python": ".py"}


def run_code(
    code: str,
    *,
    timeout: float | None = None,
    language: str = "python",
) -> tuple[str, str, int]:
    """Run a snippet in the given language. The extension picks the runner."""
    is_dart = language == "dart"
    suffix = _SUFFIXES.get(language, ".py")
    if timeout is None:
        timeout = DART_TIMEOUT_SECONDS if is_dart else RUN_TIMEOUT_SECONDS

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=suffix,
        encoding="utf-8",
        delete=False,
    ) as tmp:
        tmp.write(code)
        tmp_path = Path(tmp.name)
    try:
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
