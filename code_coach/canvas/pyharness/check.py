"""Check a Python Canvas step: play the program in a child process.

The same harness the preview runs (driver.py, lib/canvas.py), but here a
step's check - Python statements - plays it by hand: so many frames, this
key held, then looks at what was drawn. The program and the check run in one
child (`python -I -u`, in an empty temp folder, with a bare environment), and
the verdict comes back as one JSON line: {"passed", "message"}.

The check body runs with these in scope:

    cc       frames(n, dt=1/60), press(key), release(key), click(x, y),
             pointer(x, y), rects(), arcs(), texts(), drawn(), time
    expect   expect(ok, message): fail the check with the message unless ok
    near     near(a, b, within): is a a number within `within` of b
    g        the learner's top-level names: g.player['x'], g.enemies = []
    WIDTH, HEIGHT
"""

from __future__ import annotations

import json
import subprocess
import tempfile

from code_coach.canvas import TIMEOUT_SECONDS, CheckResult
from code_coach.canvas.pyharness.session import SEED, TIMEOUT_MESSAGE, child_command, child_env, child_flags, kill_tree

CHECK_TIMEOUT_MESSAGE = (
    "The check ran out of time. Is there a loop that never ends - a "
    "while whose condition never turns false?"
)


def run_py_check(code: str, check: str, seed: int = SEED, timeout: float = TIMEOUT_SECONDS) -> CheckResult:
    """Play `code` and run `check` against it, in a child process of its own."""
    payload = json.dumps({"code": code, "check": check, "seed": seed})
    with tempfile.TemporaryDirectory(prefix="cc-pycheck-") as folder:
        proc = subprocess.Popen(
            child_command("check"),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=folder, env=child_env(), creationflags=child_flags(),
        )
        try:
            out, err = proc.communicate(payload.encode("utf-8"), timeout=timeout)
        except subprocess.TimeoutExpired:
            kill_tree(proc)
            proc.communicate()
            return CheckResult(False, CHECK_TIMEOUT_MESSAGE)
        finally:
            kill_tree(proc)
    if proc.returncode == 3:
        # The program caught the watchdog's exception and kept going: the driver ended it.
        return CheckResult(False, TIMEOUT_MESSAGE)
    text = out.decode("utf-8", "replace").strip()
    line = text.splitlines()[-1] if text else ""
    try:
        got = json.loads(line)
    except json.JSONDecodeError:
        tail = err.decode("utf-8", "replace").strip()[-400:]
        return CheckResult(False, "The check could not run: " + (tail or "no output"))
    return CheckResult(bool(got.get("passed")), str(got.get("message", "")))
