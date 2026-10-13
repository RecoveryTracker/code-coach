"""Python Canvas sessions: a program running in a child process, a frame at a time.

The learner's Python runs here on the server, in a process of its own
(driver.py serve), and the browser draws what it records. Each request is
one line to the child and one line back (the protocol is in driver.py), so
the game moves exactly as fast as the page asks it to.

A session is a child process and a temp folder it runs in. They are kept in a
small registry: at most `max_sessions` at once (the least recently used is
stopped to make room), and one nobody has stepped for `idle_seconds` is
stopped. Stop, evict, idle and server exit all end the child and delete the
folder. If the server itself is killed outright, the child's stdin closes and
the child exits on its own.
"""

from __future__ import annotations

import atexit
import json
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
DRIVER = HERE / "driver.py"
PREFIX = "\x1ePY"

#: One step (a frame or a few) may take this long before "out of time".
STEP_SECONDS = 2.0
#: The child has this much longer than its own limit to answer before it is killed.
KILL_GRACE = 2.5
#: Starting a process takes a moment (slower with a virus scanner): extra time for that.
SPAWN_SECONDS = 10.0
#: What a check seeds `random` with before the program loads (driver.py has the same number).
SEED = 20260926
MAX_SESSIONS = 4
IDLE_SECONDS = 60.0

TIMEOUT_MESSAGE = (
    "Your code ran out of time. Is there a loop that never ends - a while "
    "whose condition never turns false?"
)


def child_env() -> dict[str, str]:
    """A bare environment: nothing of the server's (keys, paths) reaches the program."""
    env = {"PYTHONIOENCODING": "utf-8"}
    for name in ("SYSTEMROOT", "SystemRoot", "TEMP", "TMP"):
        if name in os.environ:
            env[name] = os.environ[name]
    return env


def child_command(mode: str) -> list[str]:
    return [sys.executable, "-I", "-u", "-X", "utf8", str(DRIVER), mode]


def child_flags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0


def kill_tree(proc: subprocess.Popen) -> None:
    """End a process and anything it started (a venv's python.exe can be a launcher)."""
    if proc.poll() is None:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        if proc.poll() is None:
            proc.kill()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        pass


def remove_folder(folder: Path) -> None:
    """Delete a folder; Windows may hold it for a moment after its process ends."""
    for _ in range(20):
        shutil.rmtree(folder, ignore_errors=True)
        if not folder.exists():
            return
        time.sleep(0.05)


def sweep_stale(older_than: float = 3600.0) -> list[str]:
    """Delete the folders of sessions a killed server never got to clean up.

    A server that is killed outright (a restart on a code change) runs no exit
    code; its children end on their own, but their folders stay. Anything this
    old cannot belong to a live session (idle ones are reaped after a minute).
    """
    gone: list[str] = []
    root = Path(tempfile.gettempdir())
    try:
        found = [p for p in root.iterdir() if p.name.startswith("cc-pycanvas-") and p.is_dir()]
    except OSError:
        return gone
    for folder in found:
        try:
            if time.time() - folder.stat().st_mtime > older_than:
                remove_folder(folder)
                gone.append(folder.name)
        except OSError:
            pass
    return gone


class Unknown(KeyError):
    """No such session - it was never started, or it was stopped, replaced or idle."""


def _error(message: str, line: int | None = None) -> dict:
    return {"calls": [], "logs": [], "error": {"message": message, "line": line},
            "frames": False, "input": False}


class PySession:
    """One program, one child process."""

    def __init__(self, session_id: str, step_id: str, step_seconds: float = STEP_SECONDS) -> None:
        self.id = session_id
        self.step_id = step_id
        self.step_seconds = step_seconds
        #: The child's own process id (the launcher may be a different one).
        self.pid = 0
        self.last_used = 0.0
        self._lock = threading.Lock()
        self._closed = False
        self._tomb: dict | None = None  # the error a finished program keeps answering with
        # The program runs in `work`, empty; our own notes (its stderr) sit beside it.
        self._dir = Path(tempfile.mkdtemp(prefix="cc-pycanvas-"))
        (self._dir / "work").mkdir()
        self._stderr = open(self._dir / "stderr.txt", "wb")
        self._lines: queue.Queue = queue.Queue()
        self._proc = subprocess.Popen(
            child_command("serve"),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self._stderr,
            cwd=self._dir / "work", env=child_env(), creationflags=child_flags(),
        )
        threading.Thread(target=self._read, daemon=True).start()

    @property
    def alive(self) -> bool:
        return not self._closed and self._proc.poll() is None

    # -- talking to the child ----------------------------------------------
    def _read(self) -> None:
        out = self._proc.stdout
        try:
            for raw in out:  # type: ignore[union-attr]
                text = raw.decode("utf-8", "replace")
                if text.startswith(PREFIX):
                    try:
                        self._lines.put(json.loads(text[len(PREFIX):]))
                    except ValueError:
                        pass
        except (ValueError, OSError):
            pass
        finally:
            self._lines.put(None)
            try:
                out.close()  # type: ignore[union-attr]
            except OSError:
                pass

    def _stderr_tail(self) -> str:
        try:
            self._stderr.flush()
            text = (self._dir / "stderr.txt").read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""
        return text.strip()[-400:]

    def request(self, message: dict, wait: float) -> dict:
        """One line out, one line back; {calls, logs, error} whatever happens."""
        with self._lock:
            if self._tomb is not None:
                return dict(self._tomb)
            if self._closed:
                return self._finish(_error("This game was stopped. Press Run to start it again."))
            try:
                self._proc.stdin.write((json.dumps(message) + "\n").encode("utf-8"))  # type: ignore[union-attr]
                self._proc.stdin.flush()  # type: ignore[union-attr]
                got = self._lines.get(timeout=wait)
            except queue.Empty:
                return self._finish(_error(TIMEOUT_MESSAGE))
            except (BrokenPipeError, OSError):
                got = None
            if got is None:
                try:
                    code = self._proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    code = None
                if code == 3:  # the driver's own last resort for a program that would not stop
                    return self._finish(_error(TIMEOUT_MESSAGE))
                detail = self._stderr_tail()
                return self._finish(_error(
                    "The program stopped unexpectedly." + (f" {detail}" if detail else "")))
            if got.get("pid"):
                self.pid = int(got["pid"])
            reply = {k: got.get(k) for k in ("calls", "logs", "error", "frames", "input")}
            if got.get("error"):
                self._tomb = {"calls": [], "logs": [], "error": got["error"], "frames": False, "input": False}
                self._end()
            return reply

    def _finish(self, reply: dict) -> dict:
        self._tomb = {**reply, "frames": False, "input": False}
        self._end()
        return reply

    # -- the two things a page asks ------------------------------------------
    def start(self, code: str) -> dict:
        message = {"op": "start", "code": code, "limit": self.step_seconds}
        return self.request(message, SPAWN_SECONDS + self.step_seconds + KILL_GRACE)

    def step(self, frames: int, dt: float | None, keys: list[str], events: list[dict]) -> dict:
        message = {"op": "step", "frames": frames, "dt": dt, "keys": keys, "events": events}
        return self.request(message, self.step_seconds + KILL_GRACE)

    # -- ending ----------------------------------------------------------------
    def _end(self) -> None:
        """Stop the child and delete its folder. Safe to call twice."""
        kill_tree(self._proc)
        for pipe in (self._proc.stdin, self._stderr):
            try:
                if pipe:
                    pipe.close()
            except OSError:
                pass
        remove_folder(self._dir)

    def close(self) -> None:
        """Stop it now, from any thread - a step in progress comes back as an error."""
        if self._closed:
            return
        self._closed = True
        self._end()


class PyRegistry:
    """The live sessions, the limits on them, and what happens when one is neglected."""

    def __init__(
        self,
        *,
        max_sessions: int = MAX_SESSIONS,
        idle_seconds: float = IDLE_SECONDS,
        step_seconds: float = STEP_SECONDS,
        clock: Callable[[], float] = time.monotonic,
        reaper: bool = False,
    ) -> None:
        self.max_sessions = max_sessions
        self.idle_seconds = idle_seconds
        self.step_seconds = step_seconds
        self.clock = clock
        self._reaper = reaper
        self._sessions: dict[str, PySession] = {}
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._quit = threading.Event()
        self._swept = False

    def __len__(self) -> int:
        with self._lock:
            return len(self._sessions)

    def ids(self) -> list[str]:
        with self._lock:
            return list(self._sessions)

    # -- the three calls --------------------------------------------------------
    def start(self, step_id: str, code: str) -> dict:
        """Run a program. {session, calls, logs, error}; session is "" when it failed to start."""
        if not self._swept:
            self._swept = True
            sweep_stale()
        self.reap()
        session = PySession(uuid.uuid4().hex, step_id, self.step_seconds)
        session.last_used = self.clock()
        evicted: list[PySession] = []
        with self._lock:
            self._sessions[session.id] = session
            while len(self._sessions) > self.max_sessions:
                oldest = min((s for s in self._sessions.values() if s is not session),
                             key=lambda s: s.last_used)
                evicted.append(self._sessions.pop(oldest.id))
        for old in evicted:
            old.close()
        self._ensure_reaper()
        try:
            reply = session.start(code)
        except BaseException:
            self._drop(session.id)
            raise
        session.last_used = self.clock()
        if reply["error"]:
            # Nothing to step: free it now rather than leaving a slot.
            self._drop(session.id)
            return {"session": "", **reply}
        return {"session": session.id, **reply}

    def step(self, session_id: str, frames: int = 1, dt: float | None = None,
             keys: list[str] | None = None, events: list[dict] | None = None) -> dict:
        self.reap()
        session = self._get(session_id)
        session.last_used = self.clock()
        reply = session.step(frames, dt, keys or [], events or [])
        session.last_used = self.clock()
        return reply

    def stop(self, session_id: str) -> None:
        with self._lock:
            session = self._sessions.pop(session_id, None)
        if session is None:
            raise Unknown(session_id)
        session.close()

    # -- housekeeping -------------------------------------------------------------
    def _get(self, session_id: str) -> PySession:
        with self._lock:
            session = self._sessions.get(session_id)
        if session is None:
            raise Unknown(session_id)
        return session

    def _drop(self, session_id: str) -> None:
        with self._lock:
            session = self._sessions.pop(session_id, None)
        if session is not None:
            session.close()

    def reap(self) -> list[str]:
        """Stop every session nobody has stepped for idle_seconds. Returns their ids."""
        now = self.clock()
        with self._lock:
            stale = [s for s in self._sessions.values() if now - s.last_used > self.idle_seconds]
            for s in stale:
                del self._sessions[s.id]
        for s in stale:
            s.close()
        return [s.id for s in stale]

    def close_all(self) -> None:
        self._quit.set()
        with self._lock:
            sessions = list(self._sessions.values())
            self._sessions.clear()
        for s in sessions:
            s.close()

    def _ensure_reaper(self) -> None:
        if not self._reaper or (self._thread and self._thread.is_alive()):
            return
        self._quit.clear()

        def sweep() -> None:
            while not self._quit.wait(5.0):
                self.reap()

        self._thread = threading.Thread(target=sweep, daemon=True)
        self._thread.start()


#: The one the server uses.
REGISTRY = PyRegistry(reaper=True)
atexit.register(REGISTRY.close_all)
