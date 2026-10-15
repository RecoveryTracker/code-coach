"""Web (Python) sessions: a learner's app running in a child process, tried out by requests.

The learner's program runs on the server in a process of its own (driver.py
serve) that serves it on 127.0.0.1, a port the system picks. A page's Try it
panel asks Code Coach for a request; Code Coach (this module, in the server
process) makes it with http.client against that port - never following a
redirect, at most 1 MB back, at most 5 seconds - and returns the app's real
answer with whatever the program printed meanwhile. Nothing listens beyond
127.0.0.1, and the browser never talks to the app's port.

A session is a child process and a temp folder it runs in, kept in a registry
like the Python Canvas one (pyharness/session.py, which supplies the child
helpers and the registry): at most `max_sessions` at once (the least recently
used is stopped), one nobody has sent a request to for `idle_seconds` is
stopped. Stop, evict, idle and server exit all end the child and delete the
folder; a child whose server dies exits on stdin EOF.

The line protocol with the child is in driver.py: `start`, `logs`, `stop`.
"""

from __future__ import annotations

import atexit
import base64
import http.client
import json
import queue
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Callable

import subprocess

from code_coach.canvas.pyharness.session import (  # noqa: F401 - re-exported for the check and the tests
    PyRegistry,
    Unknown,
    child_env,
    child_flags,
    kill_tree,
    remove_folder,
)

HERE = Path(__file__).resolve().parent
DRIVER = HERE / "driver.py"
PREFIX = "\x1ePW"

#: A route has this long (seconds) before the child stops it; the top level of the program too.
HANDLER_SECONDS = 3.0
#: A request made for a page waits at most this long for its answer.
REQUEST_SECONDS = 5.0
#: The child has this much longer than its own limit to answer `start` before it is killed.
KILL_GRACE = 2.5
#: Starting a process takes a moment (slower with a virus scanner): extra time for that.
SPAWN_SECONDS = 10.0
MAX_BODY = 1_000_000
MAX_SESSIONS = 4
IDLE_SECONDS = 120.0
#: Request headers the server sets itself.
FORBIDDEN_HEADERS = {"host", "content-length", "connection", "transfer-encoding", "expect", "upgrade"}

TIMEOUT_MESSAGE = (
    "Your code ran out of time. Is there a loop that never ends - a while "
    "whose condition never turns false?"
)
GONE_MESSAGE = "This app was stopped. Press Run to start it again."


def child_command(mode: str) -> list[str]:
    import sys

    return [sys.executable, "-I", "-u", "-X", "utf8", str(DRIVER), mode]


def sweep_stale(older_than: float = 3600.0) -> list[str]:
    """Delete the folders of sessions a killed server never got to clean up (see pyharness/session.py)."""
    gone: list[str] = []
    try:
        found = [p for p in Path(tempfile.gettempdir()).iterdir()
                 if p.name.startswith("cc-pyweb-") and p.is_dir()]
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


def _failure(message: str, logs: list[str] | None = None) -> dict:
    return {"status": 0, "reason": "", "headers": [], "body": "", "binary": False, "truncated": False,
            "seconds": 0.0, "logs": logs or [], "error": message}


class WebSession:
    """One app, one child process."""

    def __init__(self, session_id: str, step_id: str, handler_seconds: float = HANDLER_SECONDS) -> None:
        self.id = session_id
        self.step_id = step_id
        self.handler_seconds = handler_seconds
        #: The child's own process id (the launcher may be a different one).
        self.pid = 0
        self.host = ""
        self.port = 0
        self.last_used = 0.0
        self._lock = threading.Lock()
        self._closed = False
        self._tomb: str | None = None  # why a finished program is finished
        # The program runs in `work`, empty; our own notes (its stderr) sit beside it.
        self._dir = Path(tempfile.mkdtemp(prefix="cc-pyweb-"))
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
        return not self._closed and self._tomb is None and self._proc.poll() is None

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

    def _died(self) -> str:
        """Why the child is gone, in the learner's words."""
        try:
            code = self._proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            code = None
        if code == 3:  # the driver's own last resort for a program that would not stop
            return TIMEOUT_MESSAGE
        detail = self._stderr_tail()
        return "The program stopped unexpectedly." + (f" {detail}" if detail else "")

    def _ask(self, message: dict, wait: float) -> dict | None:
        """One line out, one line back. None when the child is gone or silent for too long."""
        with self._lock:
            if self._closed or self._tomb is not None:
                return None
            try:
                self._proc.stdin.write((json.dumps(message) + "\n").encode("utf-8"))  # type: ignore[union-attr]
                self._proc.stdin.flush()  # type: ignore[union-attr]
                return self._lines.get(timeout=wait)
            except queue.Empty:
                self._tomb = TIMEOUT_MESSAGE
                self._end()
                return None
            except (BrokenPipeError, OSError):
                return None

    # -- the things a page asks -------------------------------------------------
    def start(self, code: str) -> dict:
        """Run the program. {error, logs, host, port, routes, pid}."""
        message = {"op": "start", "code": code, "limit": self.handler_seconds}
        got = self._ask(message, SPAWN_SECONDS + self.handler_seconds + KILL_GRACE)
        if got is None:
            reason = self._tomb or self._died()
            self._tomb = reason
            self._end()
            return {"error": {"message": reason, "line": None}, "logs": [], "host": "", "port": 0, "routes": []}
        self.pid = int(got.get("pid") or 0)
        if not got.get("error"):
            self.host, self.port = str(got["host"]), int(got["port"])
        return {k: got.get(k) for k in ("error", "logs", "host", "port", "routes")}

    def _logs(self) -> list[str]:
        got = self._ask({"op": "logs"}, 3.0)
        return list(got.get("logs") or []) if got else []

    def request(self, method: str, path: str, headers: dict | None = None, body: str | None = None) -> dict:
        """Make one request to the app, as a browser would; its real answer, and what it printed."""
        if self._closed:
            return _failure(GONE_MESSAGE)
        if self._tomb is not None:
            return _failure(self._tomb)
        data = (body or "").encode("utf-8")
        if len(data) > MAX_BODY:
            return _failure("The body is over 1 MB.")
        sent = {k: str(v) for k, v in (headers or {}).items() if str(k).lower() not in FORBIDDEN_HEADERS}
        started = time.monotonic()
        error = ""
        status, reason, pairs, chunks, truncated = 0, "", [], [], False
        try:
            conn = http.client.HTTPConnection(self.host, self.port, timeout=REQUEST_SECONDS)
            try:
                conn.request(method, path, body=data or None, headers=sent)
                sock = conn.sock  # the response closes conn.sock when it ends
                reply = conn.getresponse()
                while True:
                    left = REQUEST_SECONDS - (time.monotonic() - started)
                    if left <= 0:
                        raise TimeoutError("the app took too long to answer")
                    try:
                        sock.settimeout(left)
                    except OSError:
                        pass  # the answer has ended and closed it
                    piece = reply.read(65536)
                    if not piece:
                        break
                    chunks.append(piece)
                    if sum(map(len, chunks)) > MAX_BODY:
                        truncated = True
                        break
                status, reason, pairs = reply.status, reply.reason, reply.getheaders()
            finally:
                conn.close()
        except TimeoutError:
            # The app is wedged (a sleep or a read nothing can interrupt): take what it printed, then end it.
            logs = self._logs()
            self._tomb = TIMEOUT_MESSAGE
            self._end()
            return _failure(TIMEOUT_MESSAGE, logs)
        except OSError as exc:
            if self._proc.poll() is not None or isinstance(exc, ConnectionError):
                logs = self._logs()
                self._tomb = self._died()
                self._end()
                return _failure(self._tomb, logs)
            error = f"{type(exc).__name__}: {exc}"
        except (http.client.HTTPException, ValueError) as exc:
            error = f"That request could not be sent: {exc}"
        logs = self._logs()
        raw = b"".join(chunks)[:MAX_BODY]
        try:
            text, binary = raw.decode("utf-8"), False
        except UnicodeDecodeError:
            text, binary = base64.b64encode(raw).decode("ascii"), True
        return {"status": status, "reason": reason, "headers": [[k, v] for k, v in pairs],
                "body": text, "binary": binary, "truncated": truncated,
                "seconds": round(time.monotonic() - started, 4), "logs": logs, "error": error}

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
        """Stop it now, from any thread."""
        if self._closed:
            return
        self._closed = True
        self._end()


class WebRegistry(PyRegistry):
    """The live web sessions. Housekeeping (limits, idle reaping, stop, close_all) is PyRegistry's."""

    def __init__(
        self,
        *,
        max_sessions: int = MAX_SESSIONS,
        idle_seconds: float = IDLE_SECONDS,
        handler_seconds: float = HANDLER_SECONDS,
        clock: Callable[[], float] = time.monotonic,
        reaper: bool = False,
    ) -> None:
        super().__init__(max_sessions=max_sessions, idle_seconds=idle_seconds, clock=clock, reaper=reaper)
        self.handler_seconds = handler_seconds

    def start(self, step_id: str, code: str) -> dict:
        """Run a program. {session, error, logs, host, port, routes}; session is "" when it failed to start."""
        if not self._swept:
            self._swept = True
            sweep_stale()
        self.reap()
        session = WebSession(uuid.uuid4().hex, step_id, self.handler_seconds)
        session.last_used = self.clock()
        evicted = []
        with self._lock:
            self._sessions[session.id] = session  # type: ignore[assignment]
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
            # Nothing to try: free it now rather than leaving a slot.
            self._drop(session.id)
            return {"session": "", **reply}
        return {"session": session.id, **reply}

    def request(self, session_id: str, method: str, path: str,
                headers: dict | None = None, body: str | None = None) -> dict:
        self.reap()
        session = self._get(session_id)
        session.last_used = self.clock()
        reply = session.request(method, path, headers, body)  # type: ignore[attr-defined]
        session.last_used = self.clock()
        return reply


#: The one the server uses.
REGISTRY = WebRegistry(reaper=True)
atexit.register(REGISTRY.close_all)
