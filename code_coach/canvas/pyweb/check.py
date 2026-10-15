"""Check a Web (Python) step: start the learner's app, make real HTTP requests to it.

The learner's program and the check run in one child (`python -I -u -X utf8
driver.py check`, in an empty temp folder, with a bare environment). The
program is served by the web library on 127.0.0.1, a port the system picks, and
the check body - Python statements - talks to it over a socket with `cc`. It
never looks at the program's names, so any program that behaves right passes.
The verdict comes back as one JSON line: {"passed", "message"}.

The check body runs with these in scope:

    cc       get(path, headers=None, cookies=None)
             post(path, form=None, json=None, body=None, headers=None, cookies=None)
             put(...) and delete(...) like post; request(method, path, ...)
             follow(resp)      one redirect hop, as a browser takes it
             jar = True        keep the cookies the app sets and send them back
             cookies           that jar, a dict (cc.cookies.clear() is a new visitor)
             logs()            what the app printed, and the traceback of a route that crashed
    resp     (what a request gives back) .status .reason .headers (case-insensitive,
             .get(name) / .getlist(name)) .text .body .json() .cookies {name: value}
             .set_cookies [{name, value, httponly, secure, path, max_age, samesite}]
             .cookie(name) .location .content_type .ok .snippet()
             .expect_status(*codes, why="") .expect_type(*prefixes) .expect_json()
    expect   expect(ok, message): fail the check with the message unless ok
    near     near(a, b, within): is a a number within `within` of b
"""

from __future__ import annotations

import json
import subprocess
import tempfile

from code_coach.canvas import TIMEOUT_SECONDS, CheckResult
from code_coach.canvas.pyweb.session import TIMEOUT_MESSAGE, child_command, child_env, child_flags, kill_tree

CHECK_TIMEOUT_MESSAGE = (
    "The check ran out of time. Is there a loop that never ends - a "
    "while whose condition never turns false?"
)


def run_pyweb_check(code: str, check: str, timeout: float = TIMEOUT_SECONDS) -> CheckResult:
    """Serve `code` and run `check` against it, in a child process of its own."""
    payload = json.dumps({"code": code, "check": check})
    with tempfile.TemporaryDirectory(prefix="cc-pywebcheck-") as folder:
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
