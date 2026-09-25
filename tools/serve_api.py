"""Run the API, and restart it whenever a Python file under code_coach/ changes.

Uvicorn has --reload, and this project turned it off on purpose: on the
machine it was built on, uvicorn's reloader logs "Reloading..." and then
never restarts, so the app carries on serving the code it started with
while looking perfectly healthy. Forgetting to restart by hand does the
same thing more quietly - screens failing with an Internal Server Error
because half the modules in memory are from before the last change.

So this does the reloading itself, the plain way. It starts uvicorn as a
child process, looks at the modification times of the source files once
a second, and on a change it stops the child completely, waits for the
port to be free, and starts a new one. Nothing is reloaded in place:
every restart is a fresh process, which is what makes it hard to wedge.

A burst of saves (a formatter, a git pull) is waited out rather than
restarted for one file at a time.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WATCHED = ROOT / "code_coach"
HOST, PORT = "127.0.0.1", 8765
#: How long to wait after the last change before restarting.
SETTLE = 0.6


def snapshot() -> dict[str, float]:
    """Every watched file and when it last changed."""
    stamps: dict[str, float] = {}
    for path in WATCHED.rglob("*"):
        if path.suffix in (".py", ".dart", ".js") and "__pycache__" not in path.parts:
            try:
                stamps[str(path)] = path.stat().st_mtime
            except OSError:
                pass  # deleted between listing and reading
    return stamps


def port_free() -> bool:
    with socket.socket() as s:
        return s.connect_ex((HOST, PORT)) != 0


def start() -> subprocess.Popen:
    while not port_free():
        time.sleep(0.2)
    print(f"[serve_api] starting the API on {HOST}:{PORT}", flush=True)
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", "code_coach.api.server:app",
        "--no-use-colors", "--host", HOST, "--port", str(PORT),
    ], cwd=ROOT)


def stop(child: subprocess.Popen) -> None:
    if child.poll() is not None:
        return
    child.terminate()
    try:
        child.wait(timeout=10)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait()


def main() -> int:
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    seen = snapshot()
    child = start()
    try:
        while True:
            time.sleep(1)
            now = snapshot()
            if now != seen:
                # Wait out a burst of saves, then restart once.
                while True:
                    time.sleep(SETTLE)
                    settled = snapshot()
                    if settled == now:
                        break
                    now = settled
                changed = sorted(p for p in set(now) | set(seen)
                                 if now.get(p) != seen.get(p))
                shown = ", ".join(Path(p).relative_to(ROOT).as_posix() for p in changed[:3])
                more = f" and {len(changed) - 3} more" if len(changed) > 3 else ""
                print(f"[serve_api] changed: {shown}{more} - restarting", flush=True)
                seen = now
                stop(child)
                child = start()
            elif child.poll() is not None:
                # It crashed on its own - most often a syntax error in the
                # file just saved. Say so, and try again on the next change
                # rather than looping on a crash.
                print(f"[serve_api] the API exited ({child.returncode}); "
                      "waiting for the next change to try again", flush=True)
                while snapshot() == seen:
                    time.sleep(1)
                seen = snapshot()
                child = start()
    except KeyboardInterrupt:
        pass
    finally:
        stop(child)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
