"""The child process a Python Canvas program runs in.

    python -I -u -X utf8 driver.py serve    the preview: a line protocol, a frame at a time
    python -I -u -X utf8 driver.py check    one step's check: a payload in, one verdict out

Both load the learner's code the same way (compiled as "game.py", so a
traceback's line numbers are the learner's own), against the same library
(lib/canvas.py), so the game a check plays is the game you watched.

The wire, in `serve` mode. One JSON object per line each way; ours go out
behind a marker so a stray write to stdout cannot be mistaken for one:

    parent -> child   {"op": "start", "code": "...", "limit": 2.0}
                      {"op": "step", "frames": 1, "dt": 0.0167, "keys": ["ArrowLeft"],
                       "events": [{"type": "keydown"|"keyup"|"click"|"mousemove", ...}]}
                      {"op": "stop"}
    child -> parent   "\\x1ePY" + {"calls": [...], "logs": [...], "error": null | {"message", "line"},
                                    "pid": <start only>}

Every reply also says `frames` (the program wants frames: an on_frame function or
a pending timer) and `input` (it wants key or click events); when both are false
nothing it does can change and the page stops asking.

A call is [name, args, fill_style, stroke_style, {lineWidth, font, textAlign,
textBaseline, globalAlpha}]. `print` is caught and comes back in logs; stdout
belongs to the protocol. A program that runs past its limit is stopped with
an exception from a watchdog thread (so the error has a line), and killed
outright if it will not stop.
"""

from __future__ import annotations

import builtins
import ctypes
import json
import os
import sys
import threading
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
# -I leaves the script's own folder off sys.path; only the library goes on.
sys.path.insert(0, os.path.join(HERE, "lib"))

import canvas  # noqa: E402  - the learner's library, found by the line above

PREFIX = "\x1ePY"
GAME_FILE = "game.py"
#: What check mode seeds `random` with before the learner's code runs.
SEED = 20260926
TIMEOUT_MESSAGE = (
    "Your code ran out of time. Is there a loop that never ends - a while "
    "whose condition never turns false?"
)
#: A step may take this long (seconds), or a single call in check mode.
DEFAULT_LIMIT = 2.0
#: In check mode: each call into the program (the top level, one frame's function).
CHECK_LIMIT = 3.0
#: How long the program has, after the watchdog speaks, before the process is ended.
HARD_GRACE = 1.0
MAX_LOGS = 200
MAX_LOG_CHARS = 2000


class TimeLimit(BaseException):
    """Raised in the program by the watchdog. Not an Exception: `except Exception` won't eat it."""


class CheckFail(Exception):
    """expect() failed: the message is the learner's."""


class MissingName(AttributeError):
    """The check asked `g` for a name the learner's program never made."""


# -- The watchdog ----------------------------------------------------------


class Watchdog:
    def __init__(self) -> None:
        self.main = threading.main_thread().ident
        self.deadline: float | None = None
        self.fired_at: float | None = None
        threading.Thread(target=self._watch, daemon=True).start()

    def _watch(self) -> None:
        while True:
            time.sleep(0.02)
            deadline = self.deadline
            if deadline is None:
                continue
            now = time.monotonic()
            if now <= deadline:
                continue
            if self.fired_at is None:
                self.fired_at = now
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_ulong(self.main), ctypes.py_object(TimeLimit)
                )
            elif now > self.fired_at + HARD_GRACE:
                os._exit(3)  # it swallowed the exception: nothing is waiting on it

    def arm(self, seconds: float) -> None:
        self.fired_at = None
        self.deadline = time.monotonic() + seconds

    def disarm(self) -> None:
        self.deadline = None
        if self.fired_at is not None:
            # It spoke just as the program finished: take the exception back.
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_ulong(self.main), None)
            self.fired_at = None


class Guard:
    """`with guard(seconds):` - the program is stopped if the block runs longer."""

    def __init__(self, dog: Watchdog) -> None:
        self.dog = dog

    def __call__(self, seconds: float) -> "_Armed":
        return _Armed(self.dog, seconds)


class _Armed:
    def __init__(self, dog: Watchdog, seconds: float) -> None:
        self.dog = dog
        self.seconds = seconds
        self.owner = False

    def __enter__(self) -> None:
        if self.dog.deadline is None:  # nested: the outer one is the clock
            self.dog.arm(self.seconds)
            self.owner = True

    def __exit__(self, *exc: object) -> None:
        if self.owner:
            self.dog.disarm()


# -- Catching print --------------------------------------------------------


class Log:
    """Stands in for sys.stdout and sys.stderr: whole lines are kept for the console."""

    encoding = "utf-8"
    errors = "strict"

    def __init__(self) -> None:
        self.lines: list[str] = []
        self.partial = ""
        self.dropped = 0

    def write(self, text: str) -> int:
        self.partial += text
        while "\n" in self.partial:
            line, self.partial = self.partial.split("\n", 1)
            self._keep(line)
        return len(text)

    def _keep(self, line: str) -> None:
        if len(self.lines) >= MAX_LOGS:
            self.dropped += 1
        else:
            self.lines.append(line[:MAX_LOG_CHARS])

    def flush(self) -> None:
        pass

    def isatty(self) -> bool:
        return False

    def drain(self, everything: bool = False) -> list[str]:
        if everything and self.partial:
            self._keep(self.partial)
            self.partial = ""
        out, self.lines = self.lines, []
        if self.dropped:
            out.append(f"... {self.dropped} more lines not shown")
            self.dropped = 0
        return out


def _no_input(prompt: object = "") -> str:
    raise RuntimeError(
        "input() cannot be used in a game - it would wait forever for typing "
        "that never comes. Read the keys held with `keys`, or on_key_down."
    )


# -- Running the learner's code -------------------------------------------


def describe(exc: BaseException) -> dict:
    """{message, line} for an exception, the line being the learner's (game.py) or None."""
    if isinstance(exc, TimeLimit):
        return {"message": TIMEOUT_MESSAGE, "line": last_game_line(exc)}
    if isinstance(exc, SystemExit):
        return {
            "message": "Your program called exit(). A game keeps running - take that out.",
            "line": last_game_line(exc),
        }
    if isinstance(exc, SyntaxError) and exc.filename == GAME_FILE:
        return {"message": f"SyntaxError: {exc.msg}", "line": exc.lineno}
    return {"message": f"{type(exc).__name__}: {exc}", "line": last_game_line(exc)}


def last_game_line(exc: BaseException) -> int | None:
    line = None
    for frame in traceback.extract_tb(exc.__traceback__):
        if frame.filename == GAME_FILE:
            line = frame.lineno
    return line


class Game:
    """The learner's program, loaded."""

    def __init__(self, guard: Guard, per_call: bool, limit: float) -> None:
        self.guard = guard
        self.per_call = per_call
        self.limit = limit
        self.ns: dict = {"__name__": "__main__", "__file__": GAME_FILE, "__builtins__": builtins}

    def call(self, fn, *args):
        """Every call into the learner's code goes through here."""
        if self.per_call:
            with self.guard(self.limit):
                return fn(*args)
        return fn(*args)

    def load(self, code: str) -> None:
        with self.guard(self.limit):
            exec(compile(code, GAME_FILE, "exec"), self.ns)


def new_game(log: Log, per_call: bool, limit: float, dog: Watchdog) -> Game:
    sys.stdout = log
    sys.stderr = log
    sys.stdin = open(os.devnull, "r", encoding="utf-8")
    builtins.input = _no_input
    return Game(Guard(dog), per_call, limit)


def say(out, payload: dict) -> None:
    out.write(PREFIX + json.dumps(payload, default=str, allow_nan=False) + "\n")
    out.flush()


# -- serve: the preview ----------------------------------------------------


def serve(out, inp) -> None:
    log = Log()
    dog = Watchdog()
    game: Game | None = None
    crashed: dict | None = None
    rt = canvas._rt

    def reply(error: dict | None, extra: dict | None = None) -> None:
        calls, rt.calls = rt.calls, []
        wants = error is None
        say(out, {"calls": calls, "logs": log.drain(everything=error is not None), "error": error,
                  "frames": wants and bool(rt.frame_fns or rt.timers),
                  "input": wants and bool(rt.key_down_fns or rt.key_up_fns or rt.click_fns),
                  **(extra or {})})

    for raw in inp:
        raw = raw.strip()
        if not raw:
            continue
        msg = json.loads(raw)
        op = msg.get("op")
        if op == "stop":
            return
        if op == "start":
            limit = float(msg.get("limit") or DEFAULT_LIMIT)
            game = new_game(log, False, limit, dog)
            error = None
            try:
                game.load(str(msg.get("code", "")))
            except BaseException as exc:  # noqa: BLE001 - everything the program does is reported
                error = describe(exc)
            crashed = error
            reply(error, {"pid": os.getpid()})
            continue
        if game is None:
            reply({"message": "The program has not been started.", "line": None})
            continue
        if crashed is not None:
            say(out, {"calls": [], "logs": log.drain(everything=True), "error": crashed,
                      "frames": False, "input": False})
            continue
        # op == "step"
        frames = max(1, min(120, int(msg.get("frames") or 1)))
        dt = float(msg.get("dt") or canvas.DEFAULT_DT)
        dt = max(0.001, min(0.1, dt))
        rt.calls = []
        error = None
        try:
            with game.guard(game.limit):
                for ev in msg.get("events") or []:
                    kind = ev.get("type")
                    if kind == "keydown":
                        rt.key_down(ev.get("key", ""), game.call)
                    elif kind == "keyup":
                        rt.key_up(ev.get("key", ""), game.call)
                    elif kind == "mousemove":
                        rt.move(float(ev.get("x", 0)), float(ev.get("y", 0)))
                    elif kind == "click":
                        rt.click(float(ev.get("x", 0)), float(ev.get("y", 0)), game.call)
                if msg.get("keys") is not None:
                    rt.hold(msg["keys"])
                for _ in range(frames):
                    rt.frame(dt, game.call)
        except BaseException as exc:  # noqa: BLE001
            error = describe(exc)
            crashed = error
        reply(error)


# -- check: one step's verdict --------------------------------------------


class Cc:
    """`cc`: what a check plays the game with."""

    def __init__(self, game: Game) -> None:
        self._game = game
        self._rt = canvas._rt

    @property
    def time(self) -> float:
        """Game seconds since the program started."""
        return self._rt.clock

    def frames(self, n: int, dt: float = canvas.DEFAULT_DT) -> None:
        """Run n frames of dt seconds each (60 a second by default)."""
        for _ in range(int(n)):
            self._rt.calls = []
            self._rt.frame(dt, self._game.call)

    def press(self, key: str) -> None:
        self._rt.key_down(key, self._game.call)

    def release(self, key: str) -> None:
        self._rt.key_up(key, self._game.call)

    def click(self, x: float, y: float) -> None:
        self._rt.click(x, y, self._game.call)

    def pointer(self, x: float, y: float = 0) -> None:
        self._rt.move(x, y)

    def drawn(self) -> list[dict]:
        """Every drawing call made since the current frame began."""
        out = []
        for name, args, fill, stroke, extra in self._rt.calls:
            out.append({"name": name, "args": list(args), "fill": fill, "stroke": stroke,
                        "line_width": extra["lineWidth"], "font": extra["font"],
                        "text_align": extra["textAlign"], "text_baseline": extra["textBaseline"],
                        "alpha": extra["globalAlpha"]})
        return out

    def rects(self) -> list[dict]:
        """The filled rectangles of the current frame: {x, y, w, h, fill}."""
        return [
            {"x": a[0], "y": a[1], "w": a[2], "h": a[3], "fill": fill}
            for name, a, fill, _stroke, _extra in self._rt.calls if name == "fill_rect"
        ]

    def arcs(self) -> list[dict]:
        """The circles drawn this frame: arc(x, y, r, ...) calls, as {x, y, r, fill}."""
        return [
            {"x": a[0], "y": a[1], "r": a[2], "fill": fill}
            for name, a, fill, _stroke, _extra in self._rt.calls if name == "arc"
        ]

    def texts(self) -> list[str]:
        """The text written this frame."""
        return [a[0] for name, a, *_ in self._rt.calls if name in ("fill_text", "stroke_text")]


class Names:
    """`g`: the learner's top-level names, to read and to set - g.player['x'], g.enemies = []."""

    def __init__(self, ns: dict) -> None:
        object.__setattr__(self, "_ns", ns)

    def __getattr__(self, name: str):
        ns = object.__getattribute__(self, "_ns")
        if name.startswith("__") or name not in ns:
            raise MissingName(name)
        return ns[name]

    def __setattr__(self, name: str, value: object) -> None:
        object.__getattribute__(self, "_ns")[name] = value

    def __delattr__(self, name: str) -> None:
        object.__getattribute__(self, "_ns").pop(name, None)

    def __contains__(self, name: str) -> bool:
        return name in object.__getattribute__(self, "_ns")


def expect(ok: object, message: str) -> None:
    if not ok:
        raise CheckFail(message)


def near(a: object, b: float, within: float) -> bool:
    return isinstance(a, (int, float)) and not isinstance(a, bool) and abs(a - b) <= within


def verdict(code: str, check: str, seed: int = SEED) -> dict:
    """Load the learner's program, play the check against it, and say what happened."""
    log = Log()
    dog = Watchdog()
    game = new_game(log, True, CHECK_LIMIT, dog)
    import random

    random.seed(seed)
    try:
        game.load(code)
    except BaseException as exc:  # noqa: BLE001
        return {"passed": False, "message": crash(exc)}
    scope = {
        "cc": Cc(game), "expect": expect, "near": near, "g": Names(game.ns),
        "WIDTH": canvas.WIDTH, "HEIGHT": canvas.HEIGHT,
        "__name__": "__check__", "__builtins__": builtins,
    }
    try:
        exec(compile(check, "check.py", "exec"), scope)
    except CheckFail as exc:
        return {"passed": False, "message": str(exc)}
    except MissingName as exc:
        name = exc.args[0] if exc.args else "?"
        return {"passed": False, "message": (
            f"Your program has no name `{name}` yet. The goal says what to call it - "
            "it has to be a name in your code, outside any function.")}
    except BaseException as exc:  # noqa: BLE001
        if last_game_line(exc) is not None or isinstance(exc, (TimeLimit, SystemExit)):
            return {"passed": False, "message": crash(exc)}
        where = ""
        for frame in traceback.extract_tb(exc.__traceback__):
            if frame.filename == "check.py":
                where = f" (check line {frame.lineno})"
        return {"passed": False, "message": f"The check could not run: {type(exc).__name__}: {exc}{where}"}
    return {"passed": True, "message": ""}


def crash(exc: BaseException) -> str:
    """The learner's own error, said the way the JavaScript side says it."""
    if isinstance(exc, TimeLimit):
        return TIMEOUT_MESSAGE
    found = describe(exc)
    where = f" on line {found['line']}" if found["line"] else ""
    return f"Your code threw{where}: {found['message']}"


def main() -> None:
    # stdout is the protocol; the program gets a Log in its place (new_game).
    # The driver's own crashes go to the real stderr, which the parent reads.
    sys.excepthook = lambda *a: traceback.print_exception(*a, file=sys.__stderr__)
    out = sys.stdout
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "serve":
        serve(out, sys.stdin)
    elif mode == "check":
        payload = json.loads(sys.stdin.read())
        say_plain = verdict(payload["code"], payload["check"], int(payload.get("seed") or SEED))
        out.write(json.dumps(say_plain) + "\n")
        out.flush()
    else:
        sys.stderr.write("usage: driver.py serve|check\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
