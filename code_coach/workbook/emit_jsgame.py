"""JavaScript: game math.

A game written from scratch in JavaScript runs on a small, fixed toolkit of
arithmetic: keep a number inside a range, ease toward a target, measure a
distance, test two boxes or two circles for a hit, move by speed times the
time since the last frame, wrap around the screen edge, turn pixels into
tiles and back, aim with angles, and pick which animation frame to draw.
These pages drill each one as a short program with no canvas and no DOM, so
the whole answer runs in plain node and the numbers are the point.

Anything that is not a whole number is printed with toFixed, or computed so
that JavaScript and Python agree on it to the last digit: the answers here
are worked out in Python, and node has to print the same text.
"""

from __future__ import annotations

import math
from decimal import ROUND_HALF_UP, Decimal

from code_coach.workbook.complexity import Cost
from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_game_clamp", "keeping a number inside a range"),
    Shape("js_game_lerp", "moving part of the way toward a target"),
    Shape("js_game_distance", "how far apart two points are"),
    Shape("js_game_aabb", "whether two rectangles overlap"),
    Shape("js_game_circles", "whether two circles touch"),
    Shape("js_game_velocity", "speed times delta time"),
    Shape("js_game_wrap", "wrapping around the edge of the screen"),
    Shape("js_game_grid", "tiles to pixels and back"),
    Shape("js_game_angles", "degrees, radians, aiming and moving at an angle"),
    Shape("js_game_frames", "which animation frame to draw"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── Numbers, as JavaScript writes them ───────────────────────


def _lit(x) -> str:
    """A number literal for the program: 3, -12, 0.25."""
    if isinstance(x, bool):
        raise ValueError("a bool is not a number here")
    if isinstance(x, float) and x.is_integer():
        raise ValueError(f"write {x} as an int, or it prints differently")
    return repr(x)


def _num(x) -> str:
    """A computed number exactly as console.log would show it.

    Python and JavaScript both print the shortest digits that read back as
    the same double, so they agree everywhere except whole floats (5.0
    against 5) and the far ends of the range, where each switches to an
    exponent at a different point. Those are refused rather than guessed.
    """
    if isinstance(x, int):
        return str(x)
    if x.is_integer():
        return str(int(x)) if x != 0 else "0"
    if not 1e-4 <= abs(x) < 1e15:
        raise ValueError(f"{x} would print in exponent form")
    return repr(x)


def _fixed(x: float, digits: int) -> str:
    """JavaScript's toFixed.

    Python's own formatting rounds an exact halfway double to even and
    toFixed rounds it away from zero, so this rounds the exact decimal
    value of the double itself, the way the spec says to.
    """
    sign = "-" if x < 0 else ""
    exact = Decimal(abs(x)).quantize(Decimal(1).scaleb(-digits), ROUND_HALF_UP)
    return sign + f"{exact:f}"


def _bool(b: bool) -> str:
    return "true" if b else "false"


def _obj(name: str, **fields) -> str:
    body = ", ".join(f"{k}: {_lit(v)}" for k, v in fields.items())
    return f"const {name} = {{ {body} }};"


# ── 1. Clamp ─────────────────────────────────────────────────

_CLAMP = "const clamp = (value, min, max) => Math.min(Math.max(value, min), max);"


def _clamp(a: dict) -> str:
    v, want = a["var"], a["want"]
    if want == "clamp":
        inner = v
    else:
        inner = f"{v} {'-' if want == 'damage' else '+'} {_lit(a['amount'])}"
    return _lines(
        _CLAMP,
        f"let {v} = {_lit(a['value'])};",
        f"{v} = clamp({inner}, {_lit(a['min'])}, {_lit(a['max'])});",
        f"console.log({v});",
    )


# ── 2. Lerp ──────────────────────────────────────────────────

_LERP = "const lerp = (a, b, t) => a + (b - a) * t;"


def _lerp(a: dict) -> str:
    v = a["var"]
    if a["want"] == "once":
        return _lines(
            _LERP,
            f"const {v} = lerp({_lit(a['a'])}, {_lit(a['b'])}, {_lit(a['t'])});",
            f"console.log({v});",
        )
    return _lines(
        _LERP,
        f"let {v} = {_lit(a['a'])};",
        f"for (let i = 0; i < {a['n']}; i++) {{",
        f"  {v} = lerp({v}, {_lit(a['b'])}, {_lit(a['t'])});",
        "}",
        f"console.log({v}.toFixed(2));",
    )


# ── 3. Distance ──────────────────────────────────────────────


def _distance(a: dict) -> str:
    (n1, x1, y1), (n2, x2, y2) = a["one"], a["two"]
    head = [_obj(n1, x=x1, y=y1), _obj(n2, x=x2, y=y2),
            f"const range = {_lit(a['range'])};"]
    if a["want"] == "squared":
        return _lines(
            *head,
            f"const dx = {n2}.x - {n1}.x;",
            f"const dy = {n2}.y - {n1}.y;",
            "console.log(dx * dx + dy * dy);",
            "console.log(dx * dx + dy * dy <= range * range);",
        )
    shown = "dist" if a["want"] == "exact" else "dist.toFixed(2)"
    return _lines(
        *head,
        f"const dist = Math.hypot({n2}.x - {n1}.x, {n2}.y - {n1}.y);",
        f"console.log({shown});",
        "console.log(dist <= range);",
    )


# ── 4. Rectangles ────────────────────────────────────────────


def _aabb(a: dict) -> str:
    boxes = a["boxes"]
    mover = boxes[0][0]
    return _lines(
        "const overlaps = (a, b) =>",
        "  a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;",
        *(_obj(n, x=x, y=y, w=w, h=h) for n, x, y, w, h in boxes),
        *(f"console.log(overlaps({mover}, {n}));" for n, *_ in boxes[1:]),
    )


# ── 5. Circles ───────────────────────────────────────────────


def _circles(a: dict) -> str:
    (n1, x1, y1, r1), (n2, x2, y2, r2) = a["one"], a["two"]
    head = [_obj(n1, x=x1, y=y1, r=r1), _obj(n2, x=x2, y=y2, r=r2)]
    if a["want"] == "touch":
        return _lines(
            *head,
            f"const dx = {n2}.x - {n1}.x;",
            f"const dy = {n2}.y - {n1}.y;",
            f"console.log(dx * dx + dy * dy <= ({n1}.r + {n2}.r) ** 2);",
        )
    return _lines(
        *head,
        f"const gap = Math.hypot({n2}.x - {n1}.x, {n2}.y - {n1}.y) - ({n1}.r + {n2}.r);",
        "console.log(gap);",
        "console.log(gap <= 0);",
    )


# ── 6. Velocity and delta time ───────────────────────────────


def _velocity(a: dict) -> str:
    want = a["want"]
    if want == "frame":
        v = a["var"]
        return _lines(
            f"let {v} = {_lit(a['start'])};",
            f"const speed = {_lit(a['speed'])};",
            f"const dt = {a['ms']} / 1000;",
            f"{v} += speed * dt;",
            f"console.log({v}.toFixed(2));",
        )
    if want == "frames":
        v = a["var"]
        return _lines(
            f"let {v} = {_lit(a['start'])};",
            f"const speed = {_lit(a['speed'])};",
            f"const dt = 1 / {a['fps']};",
            f"for (let frame = 0; frame < {a['n']}; frame++) {{",
            f"  {v} += speed * dt;",
            "}",
            f"console.log({v}.toFixed(2));",
        )
    return _lines(
        "let y = 0;",
        "let vy = 0;",
        f"const gravity = {_lit(a['gravity'])};",
        f"const dt = 1 / {a['fps']};",
        f"for (let frame = 0; frame < {a['n']}; frame++) {{",
        "  vy += gravity * dt;",
        "  y += vy * dt;",
        "}",
        "console.log(y.toFixed(1));",
    )


# ── 7. Wrap-around ───────────────────────────────────────────

_WRAP = "const wrap = (value, size) => ((value % size) + size) % size;"


def _wrap(a: dict) -> str:
    want, size = a["want"], _lit(a["size"])
    if want == "values":
        return _lines(
            _WRAP,
            *(f"console.log(wrap({_lit(v)}, {size}));" for v in a["values"]),
        )
    if want == "naive":
        v = _lit(a["value"])
        return _lines(
            _WRAP,
            f"console.log({v} % {size});",
            f"console.log(wrap({v}, {size}));",
        )
    return _lines(
        _WRAP,
        f"let x = {_lit(a['x'])};",
        f"for (let frame = 0; frame < {a['n']}; frame++) {{",
        f"  x = wrap(x + {_lit(a['vx'])}, {size});",
        "}",
        "console.log(x);",
    )


# ── 8. Grid and pixels ───────────────────────────────────────


def _grid(a: dict) -> str:
    want = a["want"]
    tile = f"const tileSize = {_lit(a['tile'])};"
    if want == "tile":
        return _lines(
            tile,
            f"const x = {_lit(a['x'])};",
            f"const y = {_lit(a['y'])};",
            "console.log(Math.floor(x / tileSize));",
            "console.log(Math.floor(y / tileSize));",
        )
    if want == "index":
        return _lines(
            tile,
            f"const cols = {_lit(a['cols'])};",
            f"const col = Math.floor({_lit(a['x'])} / tileSize);",
            f"const row = Math.floor({_lit(a['y'])} / tileSize);",
            "console.log(row * cols + col);",
        )
    return _lines(
        tile,
        f"const cols = {_lit(a['cols'])};",
        f"const index = {_lit(a['index'])};",
        "const col = index % cols;",
        "const row = Math.floor(index / cols);",
        "console.log(col * tileSize, row * tileSize);",
    )


# ── 9. Angles ────────────────────────────────────────────────


def _angles(a: dict) -> str:
    want = a["want"]
    if want == "rad":
        return _lines(
            f"const degrees = {_lit(a['degrees'])};",
            "const radians = degrees * Math.PI / 180;",
            "console.log(radians.toFixed(4));",
        )
    if want == "deg":
        return _lines(
            f"const radians = {_lit(a['radians'])};",
            "const degrees = radians * 180 / Math.PI;",
            "console.log(degrees.toFixed(1));",
        )
    if want == "aim":
        (n1, x1, y1), (n2, x2, y2) = a["one"], a["two"]
        return _lines(
            _obj(n1, x=x1, y=y1),
            _obj(n2, x=x2, y=y2),
            f"const angle = Math.atan2({n2}.y - {n1}.y, {n2}.x - {n1}.x);",
            "console.log((angle * 180 / Math.PI).toFixed(1));",
        )
    return _lines(
        f"const angle = {_lit(a['degrees'])} * Math.PI / 180;",
        f"const speed = {_lit(a['speed'])};",
        f"const x = {_lit(a['x'])} + Math.cos(angle) * speed;",
        f"const y = {_lit(a['y'])} + Math.sin(angle) * speed;",
        "console.log(x.toFixed(2), y.toFixed(2));",
    )


# ── 10. Animation frames ─────────────────────────────────────


def _frames(a: dict) -> str:
    want = a["want"]
    if want == "fps":
        frame_time = f"const frameTime = 1000 / {a['fps']};"
    else:
        frame_time = f"const frameTime = {_lit(a['frame_ms'])};"
    head = [frame_time,
            f"const frameCount = {_lit(a['count'])};",
            f"const elapsed = {_lit(a['elapsed'])};"]
    if want == "once":
        return _lines(
            *head,
            "const frame = Math.min(Math.floor(elapsed / frameTime), frameCount - 1);",
            "console.log(frame);",
        )
    step = "const frame = Math.floor(elapsed / frameTime) % frameCount;"
    if want == "sheet":
        return _lines(
            *head,
            f"const frameWidth = {_lit(a['width'])};",
            step,
            "console.log(frame, frame * frameWidth);",
        )
    return _lines(*head, step, "console.log(frame);")


_BUILDERS = {
    "js_game_clamp": _clamp,
    "js_game_lerp": _lerp,
    "js_game_distance": _distance,
    "js_game_aabb": _aabb,
    "js_game_circles": _circles,
    "js_game_velocity": _velocity,
    "js_game_wrap": _wrap,
    "js_game_grid": _grid,
    "js_game_angles": _angles,
    "js_game_frames": _frames,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


# ── What each should print, worked out in Python ─────────────


def _rem(a: int, b: int) -> int:
    """JavaScript's %: the sign follows the left side, unlike Python's."""
    r = abs(a) % abs(b)
    return -r if a < 0 else r


def _js_wrap(v: int, size: int) -> int:
    return _rem(_rem(v, size) + size, size)


def expected_output(shape: str, args: dict, value=None) -> str:
    a = args
    if shape == "js_game_clamp":
        lo, hi, v = a["min"], a["max"], a["value"]
        if lo >= hi:
            raise ValueError("an empty range clamps nothing")
        if a["want"] == "damage":
            v = v - a["amount"]
        elif a["want"] == "heal":
            v = v + a["amount"]
        return str(min(max(v, lo), hi))
    if shape == "js_game_lerp":
        lo, hi, t = a["a"], a["b"], a["t"]
        if not 0 < t < 1:
            raise ValueError("t between 0 and 1, or it is not part of the way")
        if a["want"] == "once":
            return _num(lo + (hi - lo) * t)
        if a["n"] < 2:
            raise ValueError("follow for more than one step")
        x = lo
        for _ in range(a["n"]):
            x = x + (hi - x) * t
        return _fixed(x, 2)
    if shape == "js_game_distance":
        (_, x1, y1), (_, x2, y2) = a["one"], a["two"]
        dx, dy, r = x2 - x1, y2 - y1, a["range"]
        if a["want"] == "squared":
            sq = dx * dx + dy * dy
            return NL.join([str(sq), _bool(sq <= r * r)])
        dist = math.hypot(dx, dy)
        if a["want"] == "exact":
            if not dist.is_integer():
                raise ValueError("an exact distance must come out whole")
            shown = _num(dist)
        else:
            if dist.is_integer():
                raise ValueError("a whole distance belongs on the exact rows")
            shown = _fixed(dist, 2)
        return NL.join([shown, _bool(dist <= r)])
    if shape == "js_game_aabb":
        boxes = a["boxes"]
        if len(boxes) < 2:
            raise ValueError("a hit needs two boxes")
        _, ax, ay, aw, ah = boxes[0]
        return NL.join(
            _bool(ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by)
            for _, bx, by, bw, bh in boxes[1:])
    if shape == "js_game_circles":
        (_, x1, y1, r1), (_, x2, y2, r2) = a["one"], a["two"]
        dx, dy = x2 - x1, y2 - y1
        if a["want"] == "touch":
            return _bool(dx * dx + dy * dy <= (r1 + r2) ** 2)
        dist = math.hypot(dx, dy)
        if not dist.is_integer():
            raise ValueError("the gap rows need a whole distance")
        gap = dist - (r1 + r2)
        return NL.join([_num(gap), _bool(gap <= 0)])
    if shape == "js_game_velocity":
        want = a["want"]
        if want == "frame":
            x = a["start"]
            x += a["speed"] * (a["ms"] / 1000)
            return _fixed(x, 2)
        if want == "frames":
            x, dt = a["start"], 1 / a["fps"]
            for _ in range(a["n"]):
                x += a["speed"] * dt
            return _fixed(x, 2)
        y, vy, dt = 0, 0, 1 / a["fps"]
        for _ in range(a["n"]):
            vy += a["gravity"] * dt
            y += vy * dt
        return _fixed(y, 1)
    if shape == "js_game_wrap":
        want, size = a["want"], a["size"]
        if want == "values":
            return NL.join(str(_js_wrap(v, size)) for v in a["values"])
        if want == "naive":
            v = a["value"]
            if v >= 0:
                raise ValueError("the plain % only goes wrong below zero")
            if _rem(v, size) == 0:
                raise ValueError("that prints -0 in JavaScript")
            return NL.join([str(_rem(v, size)), str(_js_wrap(v, size))])
        x = a["x"]
        for _ in range(a["n"]):
            x = _js_wrap(x + a["vx"], size)
        return str(x)
    if shape == "js_game_grid":
        want, tile = a["want"], a["tile"]
        if want == "tile":
            return NL.join([str(a["x"] // tile), str(a["y"] // tile)])
        if want == "index":
            col, row = a["x"] // tile, a["y"] // tile
            if col >= a["cols"]:
                raise ValueError("x is off the right of the map")
            return str(row * a["cols"] + col)
        col, row = a["index"] % a["cols"], a["index"] // a["cols"]
        return f"{col * tile} {row * tile}"
    if shape == "js_game_angles":
        want = a["want"]
        if want == "rad":
            return _fixed(a["degrees"] * math.pi / 180, 4)
        if want == "deg":
            return _fixed(a["radians"] * 180 / math.pi, 1)
        if want == "aim":
            (_, x1, y1), (_, x2, y2) = a["one"], a["two"]
            angle = math.atan2(y2 - y1, x2 - x1)
            return _fixed(angle * 180 / math.pi, 1)
        angle = a["degrees"] * math.pi / 180
        x = a["x"] + math.cos(angle) * a["speed"]
        y = a["y"] + math.sin(angle) * a["speed"]
        return f"{_fixed(x, 2)} {_fixed(y, 2)}"
    if shape == "js_game_frames":
        want, count, elapsed = a["want"], a["count"], a["elapsed"]
        frame_time = 1000 / a["fps"] if want == "fps" else a["frame_ms"]
        ticks = math.floor(elapsed / frame_time)
        if want == "once":
            return str(min(ticks, count - 1))
        frame = ticks % count
        if want == "sheet":
            return f"{frame} {frame * a['width']}"
        return str(frame)
    raise KeyError(shape)


# ── Complexity notes ─────────────────────────────────────────

NOTES: dict[str, Cost] = {
    "js_game_clamp": Cost(
        "O(1)",
        "Constant: one Math.max and one Math.min, whatever the numbers are. "
        "That is why it is safe to clamp every value on every frame."),
    "js_game_lerp": Cost(
        "O(n)",
        "One lerp is constant: a subtraction, a multiply and an add. "
        "Following a target calls it once per frame, so n frames cost n "
        "steps, and each step only closes a fraction of the gap — it gets "
        "close quickly and never quite arrives."),
    "js_game_distance": Cost(
        "O(1)",
        "Constant for one pair. Checking every enemy against the player is "
        "linear in the number of enemies, and every enemy against every "
        "other is n squared, which is when skipping the square root and "
        "comparing squared distances starts to pay."),
    "js_game_aabb": Cost(
        "O(k)",
        "Four comparisons per pair, constant each, and && stops at the "
        "first one that fails. Testing one box against k others is linear "
        "in k."),
    "js_game_circles": Cost(
        "O(1)",
        "Constant: two subtractions, a few multiplies and one comparison. "
        "Comparing the squared distance with the squared radii skips the "
        "square root, the one step here that is slower than the rest."),
    "js_game_velocity": Cost(
        "O(n)",
        "One update is constant: a multiply and an add per value. Running "
        "n frames is n updates, and multiplying by dt is what keeps the "
        "distance covered the same whether those frames are fast or slow."),
    "js_game_wrap": Cost(
        "O(1)",
        "Constant: two remainders and an add, however far past the edge the "
        "value is. A loop that subtracts the width until the value fits "
        "would slow down the further out it started."),
    "js_game_grid": Cost(
        "O(1)",
        "Constant: a division and a floor each way. This is why tile maps "
        "are stored as grids — finding the tile under a point is arithmetic, "
        "not a search through every tile."),
    "js_game_angles": Cost(
        "O(1)",
        "Constant: a multiply to convert, and one call to atan2, cos or sin, "
        "each of which takes about the same time for any angle."),
    "js_game_frames": Cost(
        "O(1)",
        "Constant: one division, one floor and one remainder, however long "
        "the animation has been playing. Working the frame out from the "
        "elapsed time means nothing has to be counted up frame by frame."),
}


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)
