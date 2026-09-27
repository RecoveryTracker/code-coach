"""Pages 188-197: JavaScript, game math.

Every game written from scratch in JavaScript leans on the same handful of
formulas long before it needs a physics engine: clamp, lerp, distance, two
kinds of collision, delta time, screen wrapping, tile grids, angles, and
sprite animation. These ten pages drill each one on its own, with the
numbers changing from exercise to exercise, so the formula is second nature
by the time the game loop needs it.

Numbered after the "Working with data" pages (178-187, content_js11), so
this tuple has to be registered after JS11_PAGES for the book to stay in
order.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

JS_ONLY = ("javascript",)


def _page(page_id, number, name, teaches, example, shape, rows) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(
            Exercise(
                id=f"{page_id}-{i + 1:02d}",
                prompt=prompt,
                shape=shape,
                args=args,
            )
            for i, (prompt, args) in enumerate(rows)
        ),
        languages=JS_ONLY,
        tier="intermediate",
    )


# ── 188. Clamp ───────────────────────────────────────────────

_CLAMPS = (
    # want, variable, what it is, value, min, max, amount
    ("clamp", "x", "The player's x position", 830, 0, 800, 0),
    ("clamp", "x", "The player's x position", -12, 0, 800, 0),
    ("clamp", "y", "The player's y position", 240, 0, 600, 0),
    ("clamp", "y", "The ship's y position", -40, 0, 480, 0),
    ("clamp", "volume", "The volume", 130, 0, 100, 0),
    ("clamp", "zoom", "The camera zoom", 5, 1, 4, 0),
    ("clamp", "speed", "The car's speed", -15, 0, 120, 0),
    ("clamp", "angle", "The cannon's angle", 95, 10, 80, 0),
    ("clamp", "brightness", "The brightness", 55, 20, 90, 0),
    ("clamp", "x", "The paddle's x position", 710, 0, 640, 0),
    ("damage", "health", "health", 30, 0, 100, 45),
    ("damage", "health", "health", 80, 0, 100, 25),
    ("damage", "shield", "shield", 10, 0, 50, 12),
    ("damage", "hp", "boss's hp", 500, 0, 500, 120),
    ("damage", "armor", "armor", 20, 0, 40, 20),
    ("heal", "health", "health", 90, 0, 100, 25),
    ("heal", "health", "health", 40, 0, 100, 30),
    ("heal", "mana", "mana", 45, 0, 50, 10),
    ("heal", "hp", "player's hp", 1, 0, 20, 5),
    ("heal", "stamina", "stamina", 95, 0, 100, 5),
)


def _clamp_prompt(want, var, what, value, lo, hi, amount) -> str:
    if want == "clamp":
        return (f"{what}, {var}, is {value}, and it has to stay between {lo} "
                f"and {hi}. Clamp {var} into that range and print it.")
    verb = "Take" if want == "damage" else "Heal"
    tail = "damage" if want == "damage" else "points"
    return (f"The {what} is {value} out of {hi}, kept in {var}. {verb} "
            f"{amount} {tail}, clamp the result between 0 and {hi}, and "
            f"print {var}.")


CLAMP_PAGE = _page(
    "js-game-clamp", 188, "Game math: clamp a value into a range",
    "Games are full of numbers that must never leave a range: the player's "
    "x has to stay on the screen, health has to stay between 0 and the "
    "maximum, volume between 0 and 100. Clamping is the fix, and it is two "
    "built-ins: Math.max(value, min) lifts anything too small up to min, "
    "then Math.min(that, max) pulls anything too big down to max. A value "
    "already inside the range comes through untouched. Write it once as a "
    "small clamp function and call it every time a number changes, after "
    "the change rather than before.",
    "const clamp = (value, min, max) => Math.min(Math.max(value, min), max); "
    "clamp(830, 0, 800) is 800, clamp(-12, 0, 800) is 0, and "
    "health = clamp(health - 45, 0, 100) can never go below 0",
    "js_game_clamp",
    tuple(
        (_clamp_prompt(*row),
         {"want": row[0], "var": row[1], "value": row[3], "min": row[4],
          "max": row[5], "amount": row[6]})
        for row in _CLAMPS
    ),
)


# ── 189. Lerp ────────────────────────────────────────────────

_LERPS = (
    # want, variable, from, to, t, times
    ("once", "x", 0, 200, 0.25, 1),
    ("once", "x", 100, 300, 0.5, 1),
    ("once", "alpha", 1, 0, 0.25, 1),
    ("once", "alpha", 0, 1, 0.1, 1),
    ("once", "y", 50, 150, 0.3, 1),
    ("once", "volume", 0, 80, 0.75, 1),
    ("once", "zoom", 1, 2, 0.5, 1),
    ("once", "x", -100, 100, 0.5, 1),
    ("once", "hue", 0, 360, 0.2, 1),
    ("once", "y", 400, 0, 0.1, 1),
    ("follow", "camera", 0, 100, 0.5, 3),
    ("follow", "camera", 0, 200, 0.25, 2),
    ("follow", "camera", 50, 150, 0.1, 5),
    ("follow", "camera", 0, 1000, 0.2, 4),
    ("follow", "x", 0, 64, 0.5, 6),
    ("follow", "alpha", 1, 0, 0.3, 3),
    ("follow", "camera", 300, 0, 0.5, 4),
    ("follow", "y", 0, 90, 0.1, 10),
    ("follow", "camera", -50, 50, 0.25, 3),
    ("follow", "x", 10, 20, 0.75, 2),
)


def _lerp_prompt(want, var, lo, hi, t, n) -> str:
    base = ("Write lerp(a, b, t), which returns the point the fraction t of "
            "the way from a to b. ")
    if want == "once":
        return base + (f"Use it to set {var} to the point {t} of the way "
                       f"from {lo} to {hi}, and print {var}.")
    return base + (f"Start {var} at {lo}, then {n} times in a row move it "
                   f"{t} of the way from where it is toward {hi}, and print "
                   f"{var} to two decimal places.")


LERP_PAGE = _page(
    "js-game-lerp", 189, "Game math: lerp part of the way toward a target",
    "Lerp, short for linear interpolation, answers 'what is the number some "
    "fraction of the way from a to b?'. The formula is a + (b - a) * t: "
    "b - a is the whole trip, times t is the part of it you travel, and "
    "adding a starts you from the right place. t = 0 gives a, t = 1 gives "
    "b, t = 0.5 gives the halfway point. The game trick is to lerp from "
    "where something is now toward its target every frame: each step "
    "covers a fraction of the remaining gap, so a camera or a fade moves "
    "fast when far away and eases in gently as it gets close.",
    "const lerp = (a, b, t) => a + (b - a) * t; lerp(0, 200, 0.25) is 50; "
    "camera = lerp(camera, 100, 0.5) three times goes 50, 75, 87.5",
    "js_game_lerp",
    tuple(
        (_lerp_prompt(*row),
         {"want": row[0], "var": row[1], "a": row[2], "b": row[3],
          "t": row[4], "n": row[5]})
        for row in _LERPS
    ),
)


# ── 190. Distance ────────────────────────────────────────────

_DISTANCES = (
    # want, (name, x, y), (name, x, y), range
    ("exact", ("player", 10, 20), ("enemy", 13, 24), 6),
    ("exact", ("player", 0, 0), ("enemy", 6, 8), 9),
    ("exact", ("ship", 100, 100), ("rock", 105, 112), 13),
    ("exact", ("hero", 40, 10), ("coin", 48, 25), 20),
    ("exact", ("tower", 200, 150), ("orc", 191, 138), 12),
    ("exact", ("player", 5, 5), ("enemy", 12, 29), 30),
    ("exact", ("ship", 0, 0), ("rock", -12, 16), 18),
    ("exact", ("hero", 300, 200), ("door", 320, 221), 29),
    ("fixed", ("player", 0, 0), ("enemy", 1, 1), 2),
    ("fixed", ("player", 10, 10), ("enemy", 20, 15), 10),
    ("fixed", ("ship", 50, 80), ("rock", 70, 60), 25),
    ("fixed", ("hero", 3, 7), ("coin", 9, 2), 7),
    ("fixed", ("tower", 120, 40), ("orc", 100, 75), 40),
    ("fixed", ("player", -5, 4), ("enemy", 6, -3), 12),
    ("squared", ("player", 10, 20), ("enemy", 13, 24), 4),
    ("squared", ("ship", 0, 0), ("rock", 7, 7), 10),
    ("squared", ("tower", 50, 50), ("orc", 58, 56), 10),
    ("squared", ("hero", 100, 40), ("coin", 91, 52), 14),
    ("squared", ("player", 0, 0), ("enemy", 20, 20), 25),
    ("squared", ("magnet", 30, 30), ("coin", 34, 33), 6),
)


def _distance_prompt(want, one, two, r) -> str:
    base = (f"The {one[0]} is at ({one[1]}, {one[2]}) and the {two[0]} is at "
            f"({two[1]}, {two[2]}). ")
    if want == "exact":
        return base + (f"Print the distance between them, then whether it "
                       f"is at most {r}.")
    if want == "fixed":
        return base + (f"Print the distance between them to two decimal "
                       f"places, then whether it is at most {r}.")
    return base + (f"Without a square root, print the squared distance "
                   f"between them, then whether they are within {r} of "
                   f"each other by comparing it with {r} squared.")


DISTANCE_PAGE = _page(
    "js-game-distance", 190, "Game math: the distance between two points",
    "Is the enemy close enough to attack, is the coin close enough to pick "
    "up? Both are a distance. Subtract the x's to get dx and the y's to get "
    "dy: those are the two short sides of a right triangle, and the "
    "distance is its long side, the square root of dx * dx + dy * dy. "
    "Math.hypot(dx, dy) does all of that in one call. When you only need "
    "to compare, 'is it within range?', you can skip the square root "
    "entirely and compare dx * dx + dy * dy with range * range, which "
    "gives the same yes or no for less work.",
    "Math.hypot(13 - 10, 24 - 20) is 5, the 3-4-5 triangle; dx = 3, dy = 4, "
    "so dx * dx + dy * dy is 25 and 25 <= 6 * 6 is true",
    "js_game_distance",
    tuple(
        (_distance_prompt(*row),
         {"want": row[0], "one": row[1], "two": row[2], "range": row[3]})
        for row in _DISTANCES
    ),
)


# ── 191. Rectangles ──────────────────────────────────────────

_RECTS = (
    (("player", 10, 10, 20, 20), ("wall", 25, 15, 10, 10)),
    (("player", 10, 10, 20, 20), ("wall", 30, 10, 10, 10)),
    (("player", 0, 0, 32, 32), ("coin", 40, 8, 16, 16)),
    (("player", 100, 50, 30, 40), ("spike", 120, 85, 20, 10)),
    (("player", 100, 50, 30, 40), ("spike", 120, 90, 20, 10)),
    (("ball", 60, 60, 8, 8), ("paddle", 40, 66, 64, 12)),
    (("ball", 60, 40, 8, 8), ("paddle", 40, 66, 64, 12)),
    (("bullet", 200, 100, 4, 10), ("alien", 190, 95, 24, 16)),
    (("bullet", 230, 100, 4, 10), ("alien", 190, 95, 24, 16)),
    (("mouse", 75, 30, 1, 1), ("button", 50, 20, 100, 30)),
    (("mouse", 45, 30, 1, 1), ("button", 50, 20, 100, 30)),
    (("hero", 0, 0, 16, 16), ("door", 16, 0, 16, 16)),
    (("hero", 0, 0, 16, 16), ("door", 15, 15, 16, 16)),
    (("player", 10, 10, 20, 20), ("wall", 25, 15, 10, 10), ("coin", 50, 10, 8, 8)),
    (("ship", 100, 100, 40, 20), ("rock", 90, 110, 20, 20), ("rock2", 150, 100, 10, 10)),
    (("player", 64, 64, 32, 32), ("floor", 0, 96, 320, 32), ("ledge", 80, 40, 64, 16)),
    (("ball", 5, 5, 10, 10), ("brick", 0, 15, 30, 10), ("brick2", 14, 0, 30, 6)),
    (("cursor", 300, 200, 2, 2), ("menu", 250, 150, 100, 60), ("close", 340, 150, 10, 10)),
    (("hero", 48, 48, 16, 24), ("chest", 60, 60, 16, 16), ("trap", 30, 72, 20, 8)),
    (("player", 0, 0, 10, 10), ("wall", 10, 10, 10, 10), ("coin", 9, 9, 4, 4)),
)


def _box(box) -> str:
    name, x, y, w, h = box
    return f"{name} at x {x}, y {y}, {w} wide and {h} tall"


def _rect_prompt(boxes) -> str:
    others = ", ".join(b[0] for b in boxes[1:])
    which = (f"the {others}" if len(boxes) == 2
             else f"each of {others}, in that order, one per line")
    return (f"Boxes: {'; '.join(_box(b) for b in boxes)}. Print whether the "
            f"{boxes[0][0]} overlaps {which}. Boxes that only share an edge "
            f"do not overlap.")


AABB_PAGE = _page(
    "js-game-aabb", 191, "Game math: do two rectangles overlap",
    "Most 2D collision is rectangles lined up with the screen, called "
    "axis-aligned bounding boxes, or AABBs: x and y for the top-left "
    "corner, w and h for the size. Two of them overlap only when they "
    "overlap on the x axis and on the y axis at once. On x, that means a's "
    "left edge is left of b's right edge (a.x < b.x + b.w) and a's right "
    "edge is right of b's left edge (a.x + a.w > b.x); y is the same with "
    "y and h. Four comparisons joined with &&. Using < and > rather than "
    "<= and >= means boxes that only touch along an edge do not count, "
    "which is what you want when a player stands flush against a wall.",
    "const overlaps = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x && "
    "a.y < b.y + b.h && a.y + a.h > b.y; a box at x 10 w 20 reaches to 30, "
    "so it overlaps a box starting at 25 but not one starting at 30",
    "js_game_aabb",
    tuple(
        (_rect_prompt(boxes), {"boxes": boxes})
        for boxes in _RECTS
    ),
)


# ── 192. Circles ─────────────────────────────────────────────

_CIRCLES = (
    # want, (name, x, y, r), (name, x, y, r)
    ("touch", ("ball", 0, 0, 5), ("coin", 6, 8, 5)),
    ("touch", ("ball", 0, 0, 4), ("coin", 6, 8, 5)),
    ("touch", ("ship", 100, 100, 12), ("rock", 120, 115, 15)),
    ("touch", ("ship", 100, 100, 10), ("rock", 130, 140, 20)),
    ("touch", ("player", 50, 50, 16), ("bullet", 70, 60, 3)),
    ("touch", ("player", 50, 50, 16), ("bullet", 75, 50, 3)),
    ("touch", ("magnet", 0, 0, 30), ("coin", 25, 25, 6)),
    ("touch", ("bomb", 200, 200, 40), ("tank", 250, 230, 18)),
    ("touch", ("bomb", 200, 200, 40), ("tank", 260, 240, 18)),
    ("touch", ("orb", -10, -10, 7), ("wisp", -2, -4, 2)),
    ("gap", ("ball", 0, 0, 2), ("coin", 6, 8, 3)),
    ("gap", ("ball", 0, 0, 5), ("coin", 6, 8, 5)),
    ("gap", ("ball", 0, 0, 8), ("coin", 6, 8, 7)),
    ("gap", ("ship", 10, 10, 4), ("rock", 15, 22, 5)),
    ("gap", ("ship", 10, 10, 6), ("rock", 15, 22, 9)),
    ("gap", ("player", 100, 50, 10), ("enemy", 108, 65, 10)),
    ("gap", ("player", 100, 50, 5), ("enemy", 124, 57, 5)),
    ("gap", ("planet", 0, 0, 20), ("moon", 12, 16, 3)),
    ("gap", ("planet", 0, 0, 12), ("moon", -20, 21, 12)),
    ("gap", ("orb", 30, 40, 1), ("wisp", 39, 52, 1)),
)


def _circle(c) -> str:
    name, x, y, r = c
    article = "an" if name[0] in "aeiou" else "a"
    return f"{article} {name} at ({x}, {y}) with radius {r}"


def _circle_prompt(want, one, two) -> str:
    base = f"There is {_circle(one)} and {_circle(two)}. "
    if want == "touch":
        return base + ("Without a square root, print whether they touch or "
                       "overlap.")
    return base + ("Print the gap between their edges, the distance between "
                   "centres minus both radii, then whether they touch.")


CIRCLES_PAGE = _page(
    "js-game-circles", 192, "Game math: do two circles touch",
    "Balls, bullets, planets and pickup ranges are circles, and circles "
    "have the easiest collision test there is. Two circles touch when the "
    "distance between their centres is no more than the two radii added "
    "together. That is the distance from the last-but-one page plus one "
    "comparison. Skipping the square root works here too: compare "
    "dx * dx + dy * dy with (a.r + b.r) ** 2. Keeping the distance minus "
    "the radii instead gives the gap between the edges, which is negative "
    "when they overlap and says by how much.",
    "centres 10 apart with radii 5 and 5: 10 * 10 <= (5 + 5) ** 2 is true, "
    "they just touch; Math.hypot(6, 8) - (2 + 3) is a gap of 5",
    "js_game_circles",
    tuple(
        (_circle_prompt(*row),
         {"want": row[0], "one": row[1], "two": row[2]})
        for row in _CIRCLES
    ),
)


# ── 193. Velocity and delta time ─────────────────────────────

_MOVES = (
    ("frame", "x", 100, 250, 16),
    ("frame", "x", 0, 300, 33),
    ("frame", "y", 50, 120, 17),
    ("frame", "x", 640, -200, 16),
    ("frame", "y", 400, -90, 20),
    ("frame", "x", 12, 75, 50),
    ("frame", "x", 300, 180, 8),
    ("frames", "x", 0, 120, 30, 30),
    ("frames", "x", 0, 120, 60, 60),
    ("frames", "x", 100, 200, 60, 30),
    ("frames", "y", 480, -150, 60, 45),
    ("frames", "x", 0, 90, 30, 10),
    ("frames", "x", 20, 64, 144, 72),
    ("frames", "y", 0, 33, 60, 100),
    ("fall", 980, 60, 30),
    ("fall", 980, 60, 60),
    ("fall", 980, 30, 30),
    ("fall", 500, 60, 20),
    ("fall", 1200, 120, 60),
    ("fall", 9.8, 60, 120),
)


def _velocity_row(row):
    if row[0] == "frame":
        _, v, start, speed, ms = row
        return (f"The position {v} starts at {start} and moves at {speed} "
                f"pixels per second. The last frame took {ms} milliseconds: turn that "
                f"into seconds, move {v} by speed times that, and print it "
                f"to two decimal places.",
                {"want": "frame", "var": v, "start": start, "speed": speed,
                 "ms": ms})
    if row[0] == "frames":
        _, v, start, speed, fps, n = row
        return (f"The position {v} starts at {start} and moves at {speed} "
                f"pixels per second. Each frame lasts 1 / {fps} of a second; move it "
                f"for {n} frames, then print {v} to two decimal places.",
                {"want": "frames", "var": v, "start": start, "speed": speed,
                 "fps": fps, "n": n})
    _, g, fps, n = row
    return (f"Something falls from y 0 with no speed. Each frame lasts "
            f"1 / {fps} of a second: add gravity {g} times the frame time to "
            f"its speed, then add speed times the frame time to y. Run "
            f"{n} frames and print y to one decimal place.",
            {"want": "fall", "gravity": g, "fps": fps, "n": n})


VELOCITY_PAGE = _page(
    "js-game-velocity", 193, "Game math: velocity and delta time",
    "A game loop runs once per frame, and frames do not all take the same "
    "time: 60 a second on one machine, 30 on another, and a hiccup now and "
    "then. If you add 5 to x every frame, the game runs at a different "
    "speed on every computer. The fix is to measure speed in pixels per "
    "second and multiply by dt, the time the last frame took, in seconds: "
    "x += speed * dt. requestAnimationFrame hands you milliseconds, so "
    "divide by 1000 first. Gravity works the same way one level up: it "
    "changes the speed by gravity * dt, and the speed changes the position.",
    "at 250 pixels a second, a 16 ms frame is dt = 16 / 1000 = 0.016, so "
    "x += 250 * 0.016 moves 4 pixels; 30 frames at 1 / 30 or 60 at 1 / 60 "
    "both cover one second's worth",
    "js_game_velocity",
    tuple(_velocity_row(row) for row in _MOVES),
)


# ── 194. Wrap-around ─────────────────────────────────────────

_WRAPS = (
    ("values", 800, (-30, 830)),
    ("values", 800, (-800, 1600, 400)),
    ("values", 640, (-1, 640, 641)),
    ("values", 480, (-100, 500)),
    ("values", 360, (-90, 370, 720)),
    ("values", 1024, (-24, 1030)),
    ("values", 10, (-3, 13, -21)),
    ("naive", 800, -30),
    ("naive", 640, -1),
    ("naive", 360, -90),
    ("naive", 10, -13),
    ("naive", 480, -500),
    ("move", 800, 790, 25, 1),
    ("move", 800, 10, -25, 1),
    ("move", 640, 600, 30, 3),
    ("move", 640, 20, -15, 4),
    ("move", 480, 0, -100, 7),
    ("move", 360, 350, 45, 10),
    ("move", 100, 50, 33, 5),
    ("move", 1024, 1000, 64, 2),
)


def _wrap_row(row):
    want, size = row[0], row[1]
    base = (f"Write wrap(value, size) that brings any whole number back into "
            f"0 up to but not including size, even a negative one. ")
    if want == "values":
        values = row[2]
        listed = ", ".join(str(v) for v in values)
        return (base + f"With a size of {size}, print wrap of each of "
                f"{listed}, one per line.",
                {"want": "values", "size": size, "values": values})
    if want == "naive":
        v = row[2]
        return (base + f"Print {v} % {size} as it is, to see it stay "
                f"negative, then print wrap({v}, {size}).",
                {"want": "naive", "size": size, "value": v})
    _, _, x, vx, n = row
    return (base + f"A ship starts at x {x} on a screen {size} wide and "
            f"moves {vx} each frame, wrapping every time. Run {n} frames "
            f"and print x.",
            {"want": "move", "size": size, "x": x, "vx": vx, "n": n})


WRAP_PAGE = _page(
    "js-game-wrap", 194, "Game math: wrap around the screen edge",
    "In Asteroids, fly off the right edge and you come back on the left. "
    "That is a remainder: x % width is always less than width. The catch "
    "is that JavaScript's % keeps the sign of the left side, so -30 % 800 "
    "is -30, not 770, and a ship going off the left edge would vanish "
    "instead of reappearing. Adding width and taking the remainder a second "
    "time fixes it: ((x % width) + width) % width is always between 0 and "
    "width - 1, for any whole x, positive or negative. The same wrap turns "
    "an angle of -90 degrees into 270.",
    "const wrap = (value, size) => ((value % size) + size) % size; "
    "-30 % 800 is -30 but wrap(-30, 800) is 770, and wrap(830, 800) is 30",
    "js_game_wrap",
    tuple(_wrap_row(row) for row in _WRAPS),
)


# ── 195. Grid and pixels ─────────────────────────────────────

_GRIDS = (
    ("tile", 32, 100, 70),
    ("tile", 32, 31, 32),
    ("tile", 16, 250, 9),
    ("tile", 64, 640, 383),
    ("tile", 48, 95, 96),
    ("tile", 8, 7, 800),
    ("tile", 20, 199, 401),
    ("index", 32, 10, 100, 70),
    ("index", 32, 10, 0, 0),
    ("index", 16, 20, 250, 40),
    ("index", 64, 8, 500, 300),
    ("index", 24, 12, 280, 50),
    ("index", 10, 5, 49, 49),
    ("index", 32, 25, 790, 32),
    ("back", 32, 10, 23),
    ("back", 32, 10, 0),
    ("back", 16, 20, 45),
    ("back", 64, 8, 63),
    ("back", 24, 12, 100),
    ("back", 10, 5, 17),
)


def _grid_row(row):
    want, tile = row[0], row[1]
    if want == "tile":
        _, _, x, y = row
        return (f"Tiles are {tile} pixels square. For the point at x {x}, "
                f"y {y}, print the column of the tile it is in, then the "
                f"row, counting both from 0.",
                {"want": "tile", "tile": tile, "x": x, "y": y})
    if want == "index":
        _, _, cols, x, y = row
        return (f"A map is {cols} tiles wide, each {tile} pixels square, "
                f"stored row by row in one flat array. Print the array "
                f"index of the tile under the point x {x}, y {y}.",
                {"want": "index", "tile": tile, "cols": cols, "x": x, "y": y})
    _, _, cols, index = row
    return (f"A map is {cols} tiles wide, each {tile} pixels square, stored "
            f"row by row. For tile number {index}, print the x and y of its "
            f"top-left corner in pixels, on one line with a space between.",
            {"want": "back", "tile": tile, "cols": cols, "index": index})


GRID_PAGE = _page(
    "js-game-grid", 195, "Game math: tiles to pixels and back",
    "Platformers, puzzle games and RPG maps are grids of square tiles. To "
    "find which tile a pixel is in, divide by the tile size and round down: "
    "Math.floor(x / tileSize) is the column, and the same with y is the "
    "row. Maps are usually stored as one flat array read row by row, so "
    "the tile at (col, row) is at index row * cols + col. Going back, "
    "index % cols is the column and Math.floor(index / cols) is the row, "
    "and multiplying each by the tile size gives the pixel corner to draw "
    "it at.",
    "with 32-pixel tiles, x 100 is Math.floor(100 / 32), column 3; on a map "
    "10 wide, column 3 of row 2 is index 2 * 10 + 3 = 23, and index 23 is "
    "back to 23 % 10 = 3, Math.floor(23 / 10) = 2",
    "js_game_grid",
    tuple(_grid_row(row) for row in _GRIDS),
)


# ── 196. Angles ──────────────────────────────────────────────

_ANGLES = (
    ("rad", 45),
    ("rad", 90),
    ("rad", 180),
    ("rad", 30),
    ("rad", 270),
    ("deg", 1.5),
    ("deg", 3.14),
    ("deg", 0.5),
    ("aim", ("player", 100, 100), ("mouse", 200, 200)),
    ("aim", ("player", 100, 100), ("mouse", 100, 50)),
    ("aim", ("turret", 0, 0), ("enemy", -40, 30)),
    ("aim", ("turret", 50, 80), ("enemy", 10, 80)),
    ("aim", ("ship", 320, 240), ("mouse", 400, 180)),
    ("aim", ("player", 10, 10), ("mouse", 13, 14)),
    ("move", 30, 10, 50, 50),
    ("move", 0, 5, 100, 20),
    ("move", 90, 8, 40, 40),
    ("move", 45, 20, 0, 0),
    ("move", 135, 12, 200, 150),
    ("move", 300, 6, 60, 60),
)


def _angle_row(row):
    want = row[0]
    if want == "rad":
        d = row[1]
        return (f"Convert {d} degrees to radians and print it to four "
                f"decimal places.",
                {"want": "rad", "degrees": d})
    if want == "deg":
        r = row[1]
        return (f"Convert {r} radians to degrees and print it to one "
                f"decimal place.",
                {"want": "deg", "radians": r})
    if want == "aim":
        _, one, two = row
        return (f"The {one[0]} is at ({one[1]}, {one[2]}) and the {two[0]} "
                f"is at ({two[1]}, {two[2]}), with y growing downward. Find "
                f"the angle from the {one[0]} to the {two[0]} with atan2 and "
                f"print it in degrees to one decimal place.",
                {"want": "aim", "one": one, "two": two})
    _, d, speed, x, y = row
    return (f"Something at ({x}, {y}) moves {speed} pixels at an angle of "
            f"{d} degrees. Print its new x and y, each to two decimal "
            f"places, on one line with a space between.",
            {"want": "move", "degrees": d, "speed": speed, "x": x, "y": y})


ANGLES_PAGE = _page(
    "js-game-angles", 196, "Game math: angles, aiming and moving",
    "People think in degrees and JavaScript's Math functions think in "
    "radians, where a full turn is 2 * Math.PI instead of 360. Multiply by "
    "Math.PI / 180 to go to radians, by 180 / Math.PI to come back. To aim "
    "at the mouse, Math.atan2(dy, dx) gives the angle from you to it, y "
    "first, and gets the direction right in every quarter of the circle. "
    "To move along an angle, Math.cos(angle) * speed is how far to go in x "
    "and Math.sin(angle) * speed is how far in y. On a canvas y grows "
    "downward, so positive angles turn clockwise.",
    "45 * Math.PI / 180 is about 0.7854; Math.atan2(100, 100) * 180 / "
    "Math.PI is 45; moving 10 at 0 degrees adds Math.cos(0) * 10 = 10 to x "
    "and Math.sin(0) * 10 = 0 to y",
    "js_game_angles",
    tuple(_angle_row(row) for row in _ANGLES),
)


# ── 197. Animation frames ────────────────────────────────────

_FRAMES = (
    ("loop", 100, 6, 1250, 0),
    ("loop", 100, 6, 250, 0),
    ("loop", 80, 8, 2000, 0),
    ("loop", 150, 4, 1000, 0),
    ("loop", 50, 10, 777, 0),
    ("loop", 120, 3, 5000, 0),
    ("once", 100, 6, 250, 0),
    ("once", 100, 6, 1250, 0),
    ("once", 80, 8, 500, 0),
    ("once", 150, 4, 10000, 0),
    ("fps", 12, 6, 1000, 0),
    ("fps", 8, 4, 900, 0),
    ("fps", 24, 10, 2500, 0),
    ("fps", 10, 5, 1550, 0),
    ("fps", 6, 3, 333, 0),
    ("sheet", 100, 6, 1250, 32),
    ("sheet", 80, 8, 700, 48),
    ("sheet", 125, 4, 3000, 64),
    ("sheet", 60, 12, 1000, 16),
    ("sheet", 200, 5, 1900, 24),
)


def _frame_row(row):
    want, speed, count, elapsed, width = row
    if want == "fps":
        timing = f"plays at {speed} frames per second"
        args = {"want": "fps", "fps": speed}
    else:
        timing = f"shows each frame for {speed} milliseconds"
        args = {"want": want, "frame_ms": speed}
    args.update(count=count, elapsed=elapsed)
    base = (f"An animation has {count} frames, numbered from 0, and "
            f"{timing}. {elapsed} milliseconds have passed. ")
    if want == "once":
        return (base + "It plays once and then holds its last frame. Print "
                "the frame to draw.", args)
    if want == "sheet":
        args["width"] = width
        return (base + f"It loops, and every frame is {width} pixels wide on "
                "the sprite sheet. Print the frame to draw and the x of that "
                "frame on the sheet, on one line with a space between.", args)
    return base + "It loops. Print the frame to draw.", args


FRAMES_PAGE = _page(
    "js-game-frames", 197, "Game math: which animation frame to draw",
    "A walk cycle is a strip of pictures, a sprite sheet, shown one after "
    "another. Rather than counting frames as they go by, work out the right "
    "one from the time: Math.floor(elapsed / frameTime) is how many frames "
    "have been shown so far, and % frameCount makes it start over when it "
    "runs off the end. For an animation that plays once, like an "
    "explosion, use Math.min(that, frameCount - 1) instead of % so it "
    "stops on the last frame. The frame times its width is where that "
    "picture starts on the sheet.",
    "at 100 ms a frame with 6 frames, 1250 ms in is Math.floor(1250 / 100) "
    "= 12 frames shown, and 12 % 6 is frame 0 again; at 32 pixels a frame, "
    "frame 3 starts at x 96 on the sheet",
    "js_game_frames",
    tuple(_frame_row(row) for row in _FRAMES),
)


JSGAME_PAGES: tuple[Page, ...] = (
    CLAMP_PAGE,
    LERP_PAGE,
    DISTANCE_PAGE,
    AABB_PAGE,
    CIRCLES_PAGE,
    VELOCITY_PAGE,
    WRAP_PAGE,
    GRID_PAGE,
    ANGLES_PAGE,
    FRAMES_PAGE,
)
