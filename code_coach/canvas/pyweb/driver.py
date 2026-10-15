"""The child process a Python web app runs in.

    python -I -u -X utf8 driver.py serve    the preview: a line protocol, the server runs until `stop`
    python -I -u -X utf8 driver.py check    one step's check: a payload in, one verdict out

Both load the learner's code the same way (compiled as "app.py", so a
traceback's line numbers are the learner's own) against the same library
(lib/web.py), then start that library's server in this process, on a thread,
bound to 127.0.0.1 and a port the system picks. So the app a check talks to is
the app you were trying out.

The wire, in `serve` mode. One JSON object per line each way; ours go out
behind a marker so a stray write to stdout cannot be mistaken for one:

    parent -> child   {"op": "start", "code": "...", "limit": 3.0}
                      {"op": "logs"}
                      {"op": "stop"}
    child -> parent   "\\x1ePW" + {"error": null | {"message", "line"}, "logs": [...],
                                   "host": "127.0.0.1", "port": 49152, "pid": 1234,
                                   "routes": [{"method", "path"}]}        (to start)
                      "\\x1ePW" + {"logs": [...]}                         (to logs)

The parent makes the HTTP requests itself (http.client, against that host and
port); the child only serves. What the program prints, and the traceback of a
route that failed, wait in the child's log until `logs` takes them.

In `check` mode the same child also runs the check body, with `cc` (a small
HTTP client for this very server), `expect` and `near`; the verdict is one
JSON line, {"passed", "message"}. The check talks to the app only over HTTP -
it never looks at the learner's names - so any program that behaves right passes.
"""

from __future__ import annotations

import builtins
import ctypes
import http.client
import json
import linecache
import os
import re
import socket
import sys
import threading
import time
import traceback
from email.utils import parsedate_to_datetime
from urllib.parse import quote, urlencode, urljoin, urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
# -I leaves the script's own folder off sys.path; only the library goes on.
sys.path.insert(0, os.path.join(HERE, "lib"))

import web  # noqa: E402  - the learner's library, found by the line above

# Held now, before any learner code runs: a program that rebinds these names
# in the http.client module cannot reach a check's own requests.
_Connection = http.client.HTTPConnection

PREFIX = "\x1ePW"
APP_FILE = web.APP_FILE
HOST = web.HOST
#: Each route has this long (seconds) before it is stopped; so does the top level of the program.
DEFAULT_LIMIT = 3.0
#: How long the program has, after the watchdog speaks, before the process is ended.
HARD_GRACE = 1.0
#: A check's request waits this long (seconds) for its answer.
REQUEST_SECONDS = 5.0
MAX_LOGS = 200
MAX_LOG_CHARS = 2000
TIMEOUT_MESSAGE = (
    "Your code ran out of time. Is there a loop that never ends - a while "
    "whose condition never turns false?"
)


class CheckFail(Exception):
    """expect() failed: the message is the learner's."""


# -- The watchdog -----------------------------------------------------------


class Watchdog:
    """Stops a thread that overruns its time by raising web.TimeLimit in it; ends the process if that is ignored."""

    def __init__(self) -> None:
        self._armed: dict[int, list] = {}  # thread id -> [deadline, fired_at]
        self._lock = threading.Lock()
        threading.Thread(target=self._watch, daemon=True).start()

    def _watch(self) -> None:
        while True:
            time.sleep(0.02)
            now = time.monotonic()
            with self._lock:
                for tid, state in list(self._armed.items()):
                    if now <= state[0]:
                        continue
                    if state[1] is None:
                        state[1] = now
                        ctypes.pythonapi.PyThreadState_SetAsyncExc(
                            ctypes.c_ulong(tid), ctypes.py_object(web.TimeLimit))
                    elif now > state[1] + HARD_GRACE:
                        os._exit(3)  # it swallowed the exception: nothing is waiting on it

    def guard(self, seconds: float):
        """`with dog.guard(s):` - this thread is stopped if the block runs longer. Nested: the outer clock rules."""
        return _Armed(self, seconds)


class _Armed:
    def __init__(self, dog: Watchdog, seconds: float) -> None:
        self.dog = dog
        self.seconds = seconds
        self.tid = 0
        self.owner = False

    def __enter__(self) -> None:
        self.tid = threading.get_ident()
        with self.dog._lock:
            if self.tid not in self.dog._armed:
                self.dog._armed[self.tid] = [time.monotonic() + self.seconds, None]
                self.owner = True

    def __exit__(self, *exc: object) -> None:
        if not self.owner:
            return
        with self.dog._lock:
            state = self.dog._armed.pop(self.tid, None)
            if state is not None and state[1] is not None:
                # It spoke just as the block finished: take the exception back.
                ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_ulong(self.tid), None)


# -- Catching print ----------------------------------------------------------


class Log:
    """Stands in for sys.stdout and sys.stderr: whole lines are kept for the console. Thread-safe."""

    encoding = "utf-8"
    errors = "strict"

    def __init__(self) -> None:
        self.lines: list[str] = []
        #: Everything kept since the start (a check's cc.logs()); `lines` is what is not yet taken.
        self.history: list[str] = []
        self.partial = ""
        self.dropped = 0
        self._lock = threading.Lock()

    def write(self, text: str) -> int:
        with self._lock:
            self.partial += text
            while "\n" in self.partial:
                line, self.partial = self.partial.split("\n", 1)
                self._keep(line)
        return len(text)

    def _keep(self, line: str) -> None:
        line = line[:MAX_LOG_CHARS]
        if len(self.history) < 10 * MAX_LOGS:
            self.history.append(line)
        if len(self.lines) >= MAX_LOGS:
            self.dropped += 1
        else:
            self.lines.append(line)

    def flush(self) -> None:
        pass

    def isatty(self) -> bool:
        return False

    def drain(self, everything: bool = False) -> list[str]:
        with self._lock:
            if everything and self.partial:
                self._keep(self.partial)
                self.partial = ""
            out, self.lines = self.lines, []
            if self.dropped:
                out.append(f"... {self.dropped} more lines not shown")
                self.dropped = 0
            return out

    def all(self) -> list[str]:
        with self._lock:
            return list(self.history)


def _no_input(prompt: object = "") -> str:
    raise RuntimeError(
        "input() cannot be used in a web app - it would wait forever for typing "
        "that never comes. Read what the visitor sent from `request`."
    )


# -- Running the learner's code ------------------------------------------------


def describe(exc: BaseException) -> dict:
    """{message, line} for an exception, the line being the learner's (app.py) or None."""
    if isinstance(exc, web.TimeLimit):
        return {"message": TIMEOUT_MESSAGE, "line": last_app_line(exc)}
    if isinstance(exc, SystemExit):
        return {
            "message": "Your program called exit(). A web app keeps running - take that out.",
            "line": last_app_line(exc),
        }
    if isinstance(exc, SyntaxError) and exc.filename == APP_FILE:
        return {"message": f"{type(exc).__name__}: {exc.msg}", "line": exc.lineno}
    return {"message": f"{type(exc).__name__}: {exc}", "line": last_app_line(exc)}


def last_app_line(exc: BaseException) -> int | None:
    line = None
    for frame in traceback.extract_tb(exc.__traceback__):
        if frame.filename == APP_FILE:
            line = frame.lineno
    return line


def prepare(log: Log) -> None:
    sys.stdout = log
    sys.stderr = log
    sys.stdin = open(os.devnull, "r", encoding="utf-8")
    builtins.input = _no_input


def load(code: str, dog: Watchdog, limit: float) -> dict | None:
    """Run the learner's program (its top level). The error as {message, line}, or None."""
    # So a traceback can show the learner's own line of code under its number.
    linecache.cache[APP_FILE] = (len(code), None, code.splitlines(True), APP_FILE)
    ns = {"__name__": "__main__", "__file__": APP_FILE, "__builtins__": builtins}
    try:
        with dog.guard(limit):
            exec(compile(code, APP_FILE, "exec"), ns)
    except BaseException as exc:  # noqa: BLE001 - everything the program does is reported
        return describe(exc)
    return None


def start_server(dog: Watchdog, limit: float):
    """The library's server, serving on a thread. Routes are stopped after `limit` seconds."""
    web.hooks.guard = lambda: dog.guard(limit)
    server = web.make_server()
    threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True).start()
    return server


def say(out, payload: dict) -> None:
    out.write(PREFIX + json.dumps(payload, default=str, allow_nan=False) + "\n")
    out.flush()


NO_ROUTES = (
    "Your app has no routes yet. Add one: @app.get(\"/\") above a function that returns the page."
)


# -- serve: the preview ----------------------------------------------------------


def serve(out, inp) -> None:
    log = Log()
    dog = Watchdog()
    prepare(log)
    server = None
    for raw in inp:
        raw = raw.strip()
        if not raw:
            continue
        msg = json.loads(raw)
        op = msg.get("op")
        if op == "stop":
            break
        if op == "logs":
            say(out, {"logs": log.drain(everything=True)})
            continue
        if op != "start" or server is not None:
            continue
        limit = float(msg.get("limit") or DEFAULT_LIMIT)
        error = load(str(msg.get("code", "")), dog, limit)
        reply: dict = {"error": error, "pid": os.getpid(), "host": None, "port": None, "routes": []}
        if error is None:
            if not web.app.routes():
                print(NO_ROUTES)
            server = start_server(dog, limit)
            reply.update(host=server.server_address[0], port=server.server_address[1],
                         routes=web.app.routes())
        reply["logs"] = log.drain(everything=error is not None)
        say(out, reply)
    out.flush()
    os._exit(0)  # a non-daemon thread of the learner's must not keep the process alive


# -- check: one step's verdict --------------------------------------------------


def _snippet(text: str, n: int = 90) -> str:
    flat = re.sub(r"\s+", " ", text).strip()
    return repr(flat[:n] + ("..." if len(flat) > n else ""))


def _parse_set_cookie(line: str) -> dict:
    """{name, value, path, httponly, secure, max_age, samesite, expires} from a Set-Cookie header."""
    pieces = [p.strip() for p in line.split(";")]
    name, _, value = pieces[0].partition("=")
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = re.sub(r"\\(?:([0-3][0-7]{2})|(.))", lambda m: chr(int(m.group(1), 8)) if m.group(1)
                       else m.group(2), value[1:-1])
    info = {"name": name, "value": value, "path": None, "httponly": False, "secure": False,
            "max_age": None, "samesite": None, "expires": None}
    for piece in pieces[1:]:
        key, _, val = piece.partition("=")
        key = key.strip().lower()
        if key == "httponly":
            info["httponly"] = True
        elif key == "secure":
            info["secure"] = True
        elif key == "path":
            info["path"] = val
        elif key == "samesite":
            info["samesite"] = val
        elif key == "max-age":
            try:
                info["max_age"] = int(val)
            except ValueError:
                pass
        elif key == "expires":
            info["expires"] = val
    return info


def _expired(info: dict) -> bool:
    if info["max_age"] is not None:
        return info["max_age"] <= 0
    if info["expires"]:
        try:
            when = parsedate_to_datetime(info["expires"])
            return when.timestamp() < time.time()
        except (TypeError, ValueError):
            return False
    return False


class Resp:
    """An answer the app gave: .status .reason .headers .text .body .json() .cookies .location, and expect_*()."""

    def __init__(self, cc: "Cc", what: str, status: int, reason: str, pairs, body: bytes, seconds: float,
                 method: str, path: str, sent_body: bytes | None, sent_headers: dict) -> None:
        self._cc = cc
        self.what = what
        self.status = status
        self.reason = reason
        self.headers = web.Headers(pairs)
        self.body = body
        self.seconds = seconds
        self._method = method
        self._path = path
        self._sent_body = sent_body
        self._sent_headers = sent_headers
        self.set_cookies = [_parse_set_cookie(v) for v in self.headers.getlist("Set-Cookie")]
        #: name -> value, from the Set-Cookie headers of this answer.
        self.cookies = {c["name"]: c["value"] for c in self.set_cookies}

    @property
    def content_type(self) -> str:
        """The media type alone, lower case: 'text/html'."""
        return (self.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()

    @property
    def text(self) -> str:
        charset = "utf-8"
        found = re.search(r"charset=([\w-]+)", self.headers.get("Content-Type") or "", re.I)
        if found:
            charset = found.group(1)
        try:
            return self.body.decode(charset, "replace")
        except LookupError:
            return self.body.decode("utf-8", "replace")

    @property
    def location(self) -> str | None:
        return self.headers.get("Location")

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    def snippet(self, n: int = 90) -> str:
        """The start of the body, on one line, as a quoted string for a message."""
        return _snippet(self.text, n)

    def json(self):
        try:
            return json.loads(self.text)
        except ValueError:
            raise CheckFail(
                f"{self.what} should answer with JSON, but its body is not valid JSON "
                f"(Content-Type {self.content_type or 'missing'}): {self.snippet()}") from None

    def cookie(self, name: str) -> dict | None:
        """The parsed Set-Cookie for `name`: {value, httponly, secure, path, max_age, samesite}, or None."""
        return next((c for c in self.set_cookies if c["name"] == name), None)

    def expect_status(self, *codes: int, why: str = "") -> "Resp":
        if self.status in codes:
            return self
        wanted = " or ".join(str(c) for c in codes)
        message = f"{self.what} returned {self.status} {self.reason}, expected {wanted}."
        if why:
            message += f" {why}"
        if self.status == 405 and self.headers.get("Allow"):
            message += f" The path exists but only allows {self.headers.get('Allow')}."
        elif self.status == 500:
            tail = self._cc._last_error()
            message += f" Your app crashed on it ({tail})." if tail else " Your app crashed on it - see the console."
        elif self.body:
            message += f" It sent: {self.snippet()}"
        raise CheckFail(message)

    def expect_type(self, *types: str) -> "Resp":
        if any(self.content_type.startswith(t) for t in types):
            return self
        wanted = " or ".join(types)
        raise CheckFail(
            f"{self.what} answered with Content-Type {self.headers.get('Content-Type') or '(none)'}, "
            f"expected {wanted}.")

    def expect_json(self):
        """The parsed body, after checking it was sent as application/json."""
        self.expect_type("application/json")
        return self.json()


class Cc:
    """`cc`: what a check talks to the app with. Real HTTP requests, over the socket, to the learner's server."""

    def __init__(self, port: int, log: Log) -> None:
        self._port = port
        self._log = log
        #: With jar = True, cookies the app sets are kept here and sent back on every request.
        self.jar = False
        self.cookies: dict[str, str] = {}

    def logs(self) -> list[str]:
        """Everything the app has printed so far (and the traceback of any route that crashed)."""
        return self._log.all()

    def _last_error(self) -> str:
        for line in reversed(self._log.all()):
            if line and not line[0].isspace() and not line.startswith(("Traceback", "500 ")):
                return line[:200]
        return ""

    def get(self, path: str, headers: dict | None = None, cookies: dict | None = None) -> Resp:
        return self.request("GET", path, headers=headers, cookies=cookies)

    def post(self, path: str, form=None, json=None, body=None, headers=None, cookies=None) -> Resp:
        return self.request("POST", path, form, json, body, headers, cookies)

    def put(self, path: str, form=None, json=None, body=None, headers=None, cookies=None) -> Resp:
        return self.request("PUT", path, form, json, body, headers, cookies)

    def delete(self, path: str, form=None, json=None, body=None, headers=None, cookies=None) -> Resp:
        return self.request("DELETE", path, form, json, body, headers, cookies)

    def request(self, method: str, path: str, form=None, json=None, body=None, headers=None,
                cookies=None, _what: str | None = None) -> Resp:
        given = [x is not None for x in (form, json, body)]
        if sum(given) > 1:
            raise CheckFail("The check passed more than one of form, json and body.")
        sent: dict[str, str] = {}
        data: bytes | None = None
        if form is not None:
            data = urlencode(form, doseq=True).encode()
            sent["Content-Type"] = "application/x-www-form-urlencoded"
        elif json is not None:
            import json as _json

            data = _json.dumps(json).encode()
            sent["Content-Type"] = "application/json"
        elif body is not None:
            data = body if isinstance(body, bytes) else str(body).encode()
        for name, value in (headers or {}).items():
            sent = {k: v for k, v in sent.items() if k.lower() != str(name).lower()}
            sent[str(name)] = str(value)
        pairs = dict(self.cookies) if self.jar else {}
        pairs.update(cookies or {})
        if pairs and not any(k.lower() == "cookie" for k in sent):
            sent["Cookie"] = "; ".join(f"{k}={v}" for k, v in pairs.items())
        what = _what or f"{method} {path}"
        started = time.monotonic()
        try:
            conn = _Connection(HOST, self._port, timeout=REQUEST_SECONDS)
            try:
                conn.request(method, quote(path, safe="/?&=%+:@,;~!$'()*#[]"), body=data, headers=sent)
                sock = conn.sock  # the response closes conn.sock when it ends
                reply = conn.getresponse()
                chunks: list[bytes] = []
                while True:
                    left = REQUEST_SECONDS - (time.monotonic() - started)
                    if left <= 0:
                        raise TimeoutError("took too long")
                    try:
                        sock.settimeout(left)
                    except OSError:
                        pass  # the answer has ended and closed it
                    piece = reply.read(65536)
                    if not piece:
                        break
                    chunks.append(piece)
                    if sum(map(len, chunks)) > 1_000_000:
                        break
                pairs_back = reply.getheaders()
                status, reason = reply.status, reply.reason
            finally:
                conn.close()
        except (OSError, http.client.HTTPException, TimeoutError, socket.timeout) as exc:
            raise CheckFail(
                f"{what} got no answer ({type(exc).__name__}: {exc}). Did your app stop, "
                f"or take too long?") from None
        resp = Resp(self, what, status, reason, pairs_back, b"".join(chunks),
                    time.monotonic() - started, method, path, data, sent)
        if self.jar:
            for info in resp.set_cookies:
                if _expired(info):
                    self.cookies.pop(info["name"], None)
                else:
                    self.cookies[info["name"]] = info["value"]
        return resp

    def follow(self, resp: Resp) -> Resp:
        """Take one redirect hop, the way a browser does: 303 (and 301/302 after a POST) become a GET."""
        if resp.status not in (301, 302, 303, 307, 308) or not resp.location:
            raise CheckFail(
                f"{resp.what} returned {resp.status} {resp.reason}, not a redirect with a Location "
                "header, so there is nothing to follow.")
        target = urljoin(f"http://{HOST}:{self._port}{resp._path}", resp.location)
        parts = urlsplit(target)
        if parts.hostname not in (HOST, "localhost") or (parts.port or 80) != self._port:
            raise CheckFail(f"{resp.what} redirects to {resp.location}, which is not this app.")
        path = parts.path + (f"?{parts.query}" if parts.query else "")
        method = resp._method
        keep = resp.status in (307, 308)
        if not keep and not (resp.status in (301, 302) and method in ("GET", "HEAD")):
            method = "GET"
        data = resp._sent_body if keep else None
        extra = {k: v for k, v in resp._sent_headers.items() if keep and k.lower() == "content-type"}
        return self.request(method, path or "/", body=data, headers=extra,
                            _what=f"{method} {path or '/'} (after {resp.status} from {resp.what})")


def expect(ok: object, message: str) -> None:
    if not ok:
        raise CheckFail(message)


def near(a: object, b: float, within: float) -> bool:
    return isinstance(a, (int, float)) and not isinstance(a, bool) and abs(a - b) <= within


def crash(exc: BaseException) -> str:
    """The learner's own error, said the way the other Canvas tracks say it."""
    if isinstance(exc, web.TimeLimit):
        return TIMEOUT_MESSAGE
    found = describe(exc)
    where = f" on line {found['line']}" if found["line"] else ""
    return f"Your code threw{where}: {found['message']}"


def verdict(code: str, check: str, limit: float = DEFAULT_LIMIT) -> dict:
    """Load the learner's app, serve it, run the check against it over HTTP, and say what happened."""
    log = Log()
    dog = Watchdog()
    prepare(log)
    error = load(code, dog, limit)
    if error is not None:
        where = f" on line {error['line']}" if error["line"] else ""
        if error["message"] == TIMEOUT_MESSAGE:
            return {"passed": False, "message": TIMEOUT_MESSAGE}
        return {"passed": False, "message": f"Your code threw{where}: {error['message']}"}
    server = start_server(dog, limit)
    cc = Cc(server.server_address[1], log)
    scope = {"cc": cc, "expect": expect, "near": near, "__name__": "__check__", "__builtins__": builtins}
    try:
        exec(compile(check, "check.py", "exec"), scope)
    except CheckFail as exc:
        return {"passed": False, "message": str(exc)}
    except BaseException as exc:  # noqa: BLE001
        where = ""
        for frame in traceback.extract_tb(exc.__traceback__):
            if frame.filename == "check.py":
                where = f" (check line {frame.lineno})"
        return {"passed": False, "message": f"The check could not run: {type(exc).__name__}: {exc}{where}"}
    return {"passed": True, "message": ""}


def main() -> None:
    # stdout is the protocol; the program gets a Log in its place (prepare).
    # The driver's own crashes go to the real stderr, which the parent reads.
    sys.excepthook = lambda *a: traceback.print_exception(*a, file=sys.__stderr__)
    out = sys.stdout
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "serve":
        serve(out, sys.stdin)
    elif mode == "check":
        payload = json.loads(sys.stdin.read())
        got = verdict(payload["code"], payload["check"], float(payload.get("limit") or DEFAULT_LIMIT))
        out.write(json.dumps(got) + "\n")
        out.flush()
        os._exit(0)  # the server thread and any thread of the learner's end with the process
    else:
        sys.stderr.write("usage: driver.py serve|check\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
