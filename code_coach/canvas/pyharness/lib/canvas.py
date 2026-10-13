"""canvas - the library a Python Canvas program imports.

    from canvas import ctx, WIDTH, HEIGHT, on_frame, keys

It is the Python side of the same 2D canvas the JavaScript steps draw on:
`ctx` mirrors the browser's CanvasRenderingContext2D with snake_case names
(fill_style, fill_rect, begin_path ...). Nothing is drawn here. Every call is
written down, with the colour and font it was made in, and handed back to
the page, which paints the list on a real <canvas>. Check mode reads the
same list.

Your program runs one frame at a time, in step with the page: the page
sends the keys held and the clicks, this runs one frame (timers first, then
your on_frame functions, in the order you registered them), and the draw
calls come back. Time is game time - dt is 1/60 of a second a frame - so a
speed of 240 pixels a second means the same thing on a slow machine.

This file is loaded from a child process (driver.py) and nowhere else.
"""

from __future__ import annotations

import math
import random  # noqa: F401  - `from canvas import random` works, and the harness seeds it
import re

__all__ = [
    "ctx", "WIDTH", "HEIGHT", "keys", "mouse", "random", "now",
    "on_frame", "on_key_down", "on_key_up", "on_click", "after", "every", "cancel",
]

WIDTH = 480
HEIGHT = 320

#: A frame's dt unless you are told otherwise: 60 frames a second.
DEFAULT_DT = 1 / 60

#: How far past its time a timer may be and still be "due" - float sums like
#: 60 * (1/60) land a hair under or over 1.0.
_EPS = 1e-9

_COLOURISH = ("fill_style", "stroke_style")
_TEXTISH = ("font", "text_align", "text_baseline")
_STATE_FIELDS = _COLOURISH + _TEXTISH + ("line_width", "global_alpha")
#: Property name -> the key the page applies it under.
_EXTRA_KEYS = {
    "line_width": "lineWidth",
    "font": "font",
    "text_align": "textAlign",
    "text_baseline": "textBaseline",
    "global_alpha": "globalAlpha",
}

_CAMEL = re.compile(r"(?<!^)(?=[A-Z])")


def _snake(name: str) -> str:
    return _CAMEL.sub("_", name).lower()


def _is_number(v: object) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _numbers(method: str, labels: str, values: tuple) -> bool:
    """Check every argument is a number. False when one is NaN or infinite.

    A real canvas ignores a call like that; so does this (nothing is
    recorded), rather than sending the page something it cannot draw.
    """
    names = labels.split()
    for label, v in zip(names, values):
        if not _is_number(v):
            raise TypeError(f"ctx.{method}() needs numbers, but {label} is {v!r}")
    return all(math.isfinite(v) for v in values)


# -- The context ----------------------------------------------------------


class _Context:
    """ctx: set a style, then draw. Unknown names are an error, not a silent no-op."""

    def __init__(self) -> None:
        object.__setattr__(self, "_s", {
            "fill_style": "#000000",
            "stroke_style": "#000000",
            "line_width": 1,
            "font": "10px sans-serif",
            "text_align": "start",
            "text_baseline": "alphabetic",
            "global_alpha": 1,
        })
        object.__setattr__(self, "_stack", [])
        object.__setattr__(self, "_extra", {})
        self._refresh()

    # -- state ------------------------------------------------------------
    def _refresh(self) -> None:
        s = self._s
        object.__setattr__(self, "_extra", {key: s[name] for name, key in _EXTRA_KEYS.items()})

    def __setattr__(self, name: str, value: object) -> None:
        if name not in _STATE_FIELDS:
            raise AttributeError(_no_such(name))
        if name in _COLOURISH or name in _TEXTISH:
            if not isinstance(value, str):
                raise TypeError(f"ctx.{name} must be text, like 'tomato' or '#4fd1c5' - got {value!r}")
        elif not _is_number(value):
            raise TypeError(f"ctx.{name} must be a number - got {value!r}")
        elif name == "line_width" and not (value > 0 and math.isfinite(value)):
            raise ValueError("ctx.line_width must be more than 0")
        elif name == "global_alpha" and not (0 <= value <= 1):
            raise ValueError("ctx.global_alpha must be between 0 (invisible) and 1 (solid)")
        self._s[name] = value
        if name in _EXTRA_KEYS:
            self._refresh()

    def __getattr__(self, name: str) -> object:
        # Only reached when normal lookup fails.
        if name in _STATE_FIELDS:
            return self._s[name]
        raise AttributeError(_no_such(name))

    def __dir__(self) -> list[str]:
        return sorted(set(_STATE_FIELDS) | {m for m in _METHOD_NAMES})

    # -- recording --------------------------------------------------------
    def _rec(self, name: str, *args: object) -> None:
        s = self._s
        _rt.calls.append([name, list(args), s["fill_style"], s["stroke_style"], self._extra])

    # -- rectangles -------------------------------------------------------
    def fill_rect(self, x, y, width, height) -> None:
        if _numbers("fill_rect", "x y width height", (x, y, width, height)):
            self._rec("fill_rect", x, y, width, height)

    def clear_rect(self, x, y, width, height) -> None:
        if _numbers("clear_rect", "x y width height", (x, y, width, height)):
            self._rec("clear_rect", x, y, width, height)

    def stroke_rect(self, x, y, width, height) -> None:
        if _numbers("stroke_rect", "x y width height", (x, y, width, height)):
            self._rec("stroke_rect", x, y, width, height)

    def rect(self, x, y, width, height) -> None:
        if _numbers("rect", "x y width height", (x, y, width, height)):
            self._rec("rect", x, y, width, height)

    # -- paths ------------------------------------------------------------
    def begin_path(self) -> None:
        self._rec("begin_path")

    def close_path(self) -> None:
        self._rec("close_path")

    def move_to(self, x, y) -> None:
        if _numbers("move_to", "x y", (x, y)):
            self._rec("move_to", x, y)

    def line_to(self, x, y) -> None:
        if _numbers("line_to", "x y", (x, y)):
            self._rec("line_to", x, y)

    def arc(self, x, y, radius, start_angle, end_angle, counterclockwise=False) -> None:
        ok = _numbers("arc", "x y radius start_angle end_angle", (x, y, radius, start_angle, end_angle))
        if ok and radius < 0:
            raise ValueError("ctx.arc() radius cannot be negative")
        if ok:
            self._rec("arc", x, y, radius, start_angle, end_angle, bool(counterclockwise))

    def ellipse(self, x, y, radius_x, radius_y, rotation, start_angle, end_angle, counterclockwise=False) -> None:
        vals = (x, y, radius_x, radius_y, rotation, start_angle, end_angle)
        ok = _numbers("ellipse", "x y radius_x radius_y rotation start_angle end_angle", vals)
        if ok and (radius_x < 0 or radius_y < 0):
            raise ValueError("ctx.ellipse() radii cannot be negative")
        if ok:
            self._rec("ellipse", *vals, bool(counterclockwise))

    def quadratic_curve_to(self, cpx, cpy, x, y) -> None:
        if _numbers("quadratic_curve_to", "cpx cpy x y", (cpx, cpy, x, y)):
            self._rec("quadratic_curve_to", cpx, cpy, x, y)

    def bezier_curve_to(self, cp1x, cp1y, cp2x, cp2y, x, y) -> None:
        vals = (cp1x, cp1y, cp2x, cp2y, x, y)
        if _numbers("bezier_curve_to", "cp1x cp1y cp2x cp2y x y", vals):
            self._rec("bezier_curve_to", *vals)

    def fill(self) -> None:
        self._rec("fill")

    def stroke(self) -> None:
        self._rec("stroke")

    # -- text -------------------------------------------------------------
    def fill_text(self, text, x, y) -> None:
        if _numbers("fill_text", "x y", (x, y)):
            self._rec("fill_text", str(text), x, y)

    def stroke_text(self, text, x, y) -> None:
        if _numbers("stroke_text", "x y", (x, y)):
            self._rec("stroke_text", str(text), x, y)

    def measure_text(self, text) -> float:
        """The width of `text` in the current font, in pixels.

        Python cannot ask the page's fonts, so this is an estimate: 0.6 of
        the font size per character, which is exact for a monospace font.
        """
        found = re.search(r"(\d+(?:\.\d+)?)px", self._s["font"])
        size = float(found.group(1)) if found else 10.0
        return len(str(text)) * size * 0.6

    # -- the transform and the state stack --------------------------------
    def save(self) -> None:
        self._stack.append(dict(self._s))
        self._rec("save")

    def restore(self) -> None:
        if self._stack:
            self._s.update(self._stack.pop())
            self._refresh()
        self._rec("restore")

    def translate(self, x, y) -> None:
        if _numbers("translate", "x y", (x, y)):
            self._rec("translate", x, y)

    def rotate(self, angle) -> None:
        if _numbers("rotate", "angle", (angle,)):
            self._rec("rotate", angle)

    def scale(self, x, y) -> None:
        if _numbers("scale", "x y", (x, y)):
            self._rec("scale", x, y)


_METHOD_NAMES = tuple(
    n for n, v in vars(_Context).items() if callable(v) and not n.startswith("_")
)


def _no_such(name: str) -> str:
    snake = _snake(name)
    if snake != name and (snake in _STATE_FIELDS or snake in _METHOD_NAMES):
        return f"ctx has no '{name}' - in Python it is ctx.{snake}"
    return f"ctx has no '{name}'. Properties: {', '.join(_STATE_FIELDS)}"


# -- The mouse ------------------------------------------------------------


class _Mouse:
    __slots__ = ("x", "y")

    def __init__(self) -> None:
        self.x = 0
        self.y = 0

    def __repr__(self) -> str:
        return f"mouse(x={self.x}, y={self.y})"


# -- The runtime: frames, keys, timers ------------------------------------


def _key(name: object) -> str:
    """KeyboardEvent.key names, with letters lower-cased so 'A' and 'a' agree."""
    key = str(name)
    return key.lower() if len(key) == 1 else key


class _Runtime:
    def __init__(self) -> None:
        self.clock = 0.0
        self.calls: list[list] = []
        self.frame_fns: list = []
        self.key_down_fns: list = []
        self.key_up_fns: list = []
        self.click_fns: list = []
        self.timers: list[dict] = []
        self.next_timer = 1
        self.keys: set[str] = set()
        self.mouse = _Mouse()

    # -- one frame --------------------------------------------------------
    def frame(self, dt: float, call) -> None:
        """Advance game time by dt seconds: due timers, then every on_frame function."""
        self.clock += dt
        self.fire_timers(call)
        for fn in list(self.frame_fns):
            call(fn, dt)

    def fire_timers(self, call) -> None:
        while True:
            due = [t for t in self.timers if t["at"] <= self.clock + _EPS]
            if not due:
                return
            t = min(due, key=lambda t: (t["at"], t["id"]))
            if t["every"]:
                t["at"] += t["every"]
            else:
                self.timers.remove(t)
            call(t["fn"])

    # -- input ------------------------------------------------------------
    def key_down(self, key: object, call) -> None:
        key = _key(key)
        self.keys.add(key)
        for fn in list(self.key_down_fns):
            call(fn, key)

    def key_up(self, key: object, call) -> None:
        key = _key(key)
        self.keys.discard(key)
        for fn in list(self.key_up_fns):
            call(fn, key)

    def hold(self, held) -> None:
        """Make `keys` exactly these keys (the page says what is held, whatever it missed)."""
        now = {_key(k) for k in held}
        self.keys.difference_update(self.keys - now)
        self.keys.update(now)

    def move(self, x: float, y: float) -> None:
        self.mouse.x, self.mouse.y = x, y

    def click(self, x: float, y: float, call) -> None:
        self.move(x, y)
        for fn in list(self.click_fns):
            call(fn, x, y)


_rt = _Runtime()

ctx = _Context()
keys = _rt.keys
mouse = _rt.mouse


def _function(name: str, fn: object):
    if not callable(fn):
        hint = f"pass the function itself - {name}(update), not {name}(update())"
        raise TypeError(f"{name}() needs a function: {hint}")
    return fn


def on_frame(fn):
    """Call fn(dt) once a frame; dt is the seconds since the last one. Works as a decorator."""
    _rt.frame_fns.append(_function("on_frame", fn))
    return fn


def on_key_down(fn):
    """Call fn(key) when a key goes down; key is a name like "ArrowLeft", " ", "Enter" or "a"."""
    _rt.key_down_fns.append(_function("on_key_down", fn))
    return fn


def on_key_up(fn):
    """Call fn(key) when a key comes up."""
    _rt.key_up_fns.append(_function("on_key_up", fn))
    return fn


def on_click(fn):
    """Call fn(x, y) when the canvas is clicked; x and y are canvas pixels."""
    _rt.click_fns.append(_function("on_click", fn))
    return fn


def _timer(name: str, seconds: object, fn: object, every: bool) -> int:
    if not _is_number(seconds) or not math.isfinite(seconds):
        raise TypeError(f"{name}() needs the seconds as a number, but got {seconds!r}")
    if every and seconds <= 0:
        raise ValueError("every() needs more than 0 seconds")
    if seconds < 0:
        raise ValueError("after() cannot go back in time: seconds must not be negative")
    _function(name, fn)
    tid = _rt.next_timer
    _rt.next_timer += 1
    _rt.timers.append({"id": tid, "at": _rt.clock + seconds, "every": seconds if every else 0, "fn": fn})
    return tid


def after(seconds, fn) -> int:
    """Call fn() once, `seconds` of game time from now. Returns an id for cancel()."""
    return _timer("after", seconds, fn, False)


def every(seconds, fn) -> int:
    """Call fn() every `seconds` of game time. Returns an id for cancel()."""
    return _timer("every", seconds, fn, True)


def cancel(timer_id) -> None:
    """Stop a timer made with after() or every(). Cancelling one that is gone does nothing."""
    _rt.timers[:] = [t for t in _rt.timers if t["id"] != timer_id]


def now() -> float:
    """Game time: seconds since the program started, counted in frames."""
    return _rt.clock
