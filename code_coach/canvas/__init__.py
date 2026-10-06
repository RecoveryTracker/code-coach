"""Canvas: write JavaScript that draws and plays, a step at a time.

The steps are in content.py. Your code runs twice: live in the browser, in
a sandboxed frame, so you can watch and play it; and here, in node, against
a stand-in canvas, where a step's check plays it by hand - so many frames,
this key held - and looks at what happened. Both load harness.js first, so
the game the check plays is the game you watched.

The To-do track (content_dom.py) is the exception: it works on a web page,
and a page's check needs a real browser, so it runs in one - see dom.py.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from code_coach.canvas.content import STEPS as DODGE_STEPS, Step
from code_coach.canvas.content_breakout import BREAKOUT_STEPS
from code_coach.canvas.content_dom import TODO_STEPS
from code_coach.canvas.content_farm import FARM_STEPS

#: Every track, in the order they are taught. Within a track, each step
#: starts from the last one finished.
STEPS: tuple[Step, ...] = DODGE_STEPS + BREAKOUT_STEPS + FARM_STEPS + TODO_STEPS

HERE = Path(__file__).resolve().parent
HARNESS = HERE / "harness.js"
NODE_CHECK = HERE / "node_check.js"

#: Long enough for a check that plays ten seconds of game time on a slow
#: machine; short enough that an endless loop is reported rather than waited on.
TIMEOUT_SECONDS = 15


@dataclass(frozen=True)
class CheckResult:
    passed: bool
    message: str


def steps() -> tuple[Step, ...]:
    return STEPS


def step(step_id: str) -> Step | None:
    return next((s for s in STEPS if s.id == step_id), None)


def harness_source() -> str:
    return HARNESS.read_text(encoding="utf-8")


def node_available() -> bool:
    return shutil.which("node") is not None


def run_check(code: str, check: str, world: str = "") -> CheckResult:
    """Play `code` in node - after `world`, if the step has one - and run `check`."""
    node = shutil.which("node")
    if node is None:
        return CheckResult(False, "Checking needs Node.js, and it is not installed.")
    payload = json.dumps({"harness": harness_source(), "world": world, "code": code, "check": check})
    try:
        done = subprocess.run(
            [node, str(NODE_CHECK)],
            input=payload,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return CheckResult(
            False,
            "The check ran out of time. Is there a loop that never ends - a "
            "while whose condition never turns false?",
        )
    line = done.stdout.strip().splitlines()[-1] if done.stdout.strip() else ""
    try:
        got = json.loads(line)
    except json.JSONDecodeError:
        return CheckResult(False, "The check could not run: " + (done.stderr.strip()[-400:] or "no output"))
    message = str(got.get("message", ""))
    if "Script execution timed out" in message:
        message = (
            "Your code ran out of time. Is there a loop that never ends - a "
            "while whose condition never turns false?"
        )
    return CheckResult(bool(got.get("passed")), message)


def check_step(step_id: str, code: str) -> CheckResult | None:
    found = step(step_id)
    if found is None:
        return None
    if not found.check:
        return CheckResult(True, "")
    if found.kind == "dom":
        return CheckResult(False, "This step is checked in your browser, not here.")
    return run_check(code, found.check, found.world)
