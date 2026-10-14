"""Canvas: the "Debug it (Python)" track.

Like the "From blank (Python)" track (test_canvas_pyblank.py) these steps are
independent: each starter is its OWN buggy program, not the step before. So
the suite holds each step to: ids unique, only the last step open, every buggy
starter RUNS (it never raises before the check) and FAILS the check with a
symptom - a message that begins "Requirement N:" and does not give the cause
away - every solution passes, every starter differs from its solution by a
small change, each plausible half-fix still fails, and other right ways of
writing the fix pass. The timing-sensitive steps are held at 30 and 60 frames
a second.

The tests look steps up by id in their own module, so they need no
registration in canvas/__init__.py.
"""

from __future__ import annotations

import difflib
import re

import pytest

from code_coach.canvas import run_py_check
from code_coach.canvas.content_pydebug import PYDEBUG_STEPS as STEPS

BY_ID = {s.id: s for s in STEPS}
CHECKED = [s.id for s in STEPS if s.check]

# A change is a list of (old, new) swaps applied together; each entry is
# (label, [swaps]).
Change = tuple[str, list[tuple[str, str]]]


def _apply(code: str, swaps: list[tuple[str, str]]) -> str:
    for old, new in swaps:
        assert code.count(old) >= 1, old
        code = code.replace(old, new)
    return code


#: How much a solution may differ from its starter: changed lines, counting a
#: line that was swapped as two (one out, one in).
MAX_DIFF_LINES = {
    "pydbg-01-slow-ball": 2,
    "pydbg-02-fuel-gauge": 2,
    "pydbg-03-smear": 8,
    "pydbg-04-overhead-rock": 4,
    "pydbg-05-red-balloons": 2,
    "pydbg-06-same-spark": 2,
    "pydbg-07-time-is-up": 2,
    "pydbg-08-stripe": 2,
    "pydbg-09-doubled-wave": 4,
    "pydbg-10-one-tile-off": 2,
}

# The names the check reads: the goal must name each one, in backticks.
NAMED_IN_SPEC: dict[str, list[str]] = {
    "pydbg-01-slow-ball": ["ball"],
    "pydbg-02-fuel-gauge": ["fuel"],
    "pydbg-03-smear": ["player"],
    "pydbg-04-overhead-rock": ["player", "rock", "lives"],
    "pydbg-05-red-balloons": ["balloons"],
    "pydbg-06-same-spark": ["sparks"],
    "pydbg-07-time-is-up": ["score"],
    "pydbg-08-stripe": ["grid"],
    "pydbg-09-doubled-wave": ["enemies"],
    "pydbg-10-one-tile-off": ["player"],
}

#: Words that would give the CAUSE away. A failing starter's message talks
#: about what you would see, so none of them may appear in it.
CAUSE_WORDS: dict[str, list[str]] = {
    "pydbg-01-slow-ball": ["dt", "/ 60", "divide"],
    "pydbg-02-fuel-gauge": ["range", "off-by-one", "off by one", "+ 1"],
    "pydbg-03-smear": ["fill_rect", "background", "clear", "each frame must", "wipe"],
    "pydbg-04-overhead-rock": ["overlap", "axis", "y test", "comparison"],
    "pydbg-05-red-balloons": ["remove", "iterat", "loop over", "copy"],
    "pydbg-06-same-spark": ["lambda", "closure", "late", "bind"],
    "pydbg-07-time-is-up": ["global", "local", "scope", "assign"],
    "pydbg-08-stripe": ["[[0]", "alias", "same list", "one row", "reference"],
    "pydbg-09-doubled-wave": ["default", "shared", "mutable", "=[]"],
    "pydbg-10-one-tile-off": ["int(", "floor", "//", "truncat", "round"],
}

# -- Pieces of the solutions the mistakes and other ways cut out ----------------------

_SLOW_MOVE = "ball['x'] += ball['vx'] * dt"
_SLOW_CLAMPS = (
    "        ball['x'] = WIDTH - ball['r']\n",
    "        ball['x'] = ball['r']\n",
)

_GAUGE_LOOP = "    for i in range(fuel):\n        ctx.fill_rect(20 + i * 26, 20, 20, 30)\n"

_TRAILS_DRAW = (
    "def draw():\n"
    "    ctx.fill_style = '#10141f'\n"
    "    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n"
    "    ctx.fill_style = '#4fd1c5'\n"
    "    ctx.fill_rect(player['x'], player['y'], player['size'], player['size'])\n"
)
_TRAILS_LOOP = "def loop(dt):\n    update(dt)\n    draw()\n"

_ROCK_HITS = (
    "    return (a['x'] < b['x'] + b['w'] and a['x'] + a['w'] > b['x']\n"
    "            and a['y'] < b['y'] + b['h'] and a['y'] + a['h'] > b['y'])\n"
)

_BALLOONS_LOOP = "        for b in list(balloons):\n            if b['color'] == 'red':\n                balloons.remove(b)\n"

_BALLOONS_BUGGY = (
    "        for b in balloons:\n            if b['color'] == 'red':\n                balloons.remove(b)\n"
)

_SPARKS_AFTER = "    after(i * 0.5, lambda i=i: spawn(i))\n"

_CLOCK_UPDATE = "    global time_left, state\n"

_PAINT_GRID = "grid = [[0] * COLS for _ in range(ROWS)]"

_WAVES_DEF = "def make_wave(count, enemies=None):\n    if enemies is None:\n        enemies = []\n"
_WAVES_RESTART = "        enemies = make_wave(5)\n\n\non_key_down"

_TILES_COL = "return int(x // TILE)"


#: Half-fixes and wrong fixes, each a real mistake at that step, that the
#: check must still fail - with a message that begins "Requirement N:", or,
#: where the mistake crashes the program, the harness's "Your code threw".
MISTAKES: dict[str, list[Change]] = {
    "pydbg-01-slow-ball": [
        ("a fixed fraction of a second (right at 60 frames, wrong at 30)",
         [(_SLOW_MOVE, "ball['x'] += ball['vx'] * 0.016")]),
        ("the other frame rate written in (right at 30, wrong at 60)",
         [(_SLOW_MOVE, "ball['x'] += ball['vx'] / 30")]),
        ("dt used, and the 60 kept in as well",
         [(_SLOW_MOVE, "ball['x'] += ball['vx'] * dt * 60")]),
        ("dt fixed but the walls no longer put the ball back",
         [(_SLOW_CLAMPS[0], ""), (_SLOW_CLAMPS[1], "")]),
    ],
    "pydbg-02-fuel-gauge": [
        ("starts at 1, so the gauge is shifted a cell right",
         [(_GAUGE_LOOP, "    for i in range(1, fuel + 1):\n        ctx.fill_rect(20 + i * 26, 20, 20, 30)\n")]),
        ("one cell short", [("range(fuel)", "range(fuel - 1)")]),
        ("only the empty cell hidden",
         [("range(fuel)", "range(fuel + (1 if fuel else 0))")]),
        ("always a full tank", [("range(fuel)", "range(MAX_FUEL)")]),
        ("Space can burn the tank below empty", [(" and fuel > 0", "")]),
    ],
    "pydbg-03-smear": [
        ("the wipe only covers the top of the canvas",
         [(_TRAILS_DRAW, _TRAILS_DRAW.replace("fill_rect(0, 0, WIDTH, HEIGHT)", "fill_rect(0, 0, WIDTH, 100)"))]),
        ("the wipe is painted after the square, so the square cannot be seen",
         [(_TRAILS_DRAW, (
             "def draw():\n    ctx.fill_style = '#4fd1c5'\n"
             "    ctx.fill_rect(player['x'], player['y'], player['size'], player['size'])\n"
             "    ctx.fill_style = '#10141f'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n"))]),
        ("the wipe is back at the top of the file, as it was",
         [(_TRAILS_DRAW, "def draw():\n    ctx.fill_style = '#4fd1c5'\n"
                         "    ctx.fill_rect(player['x'], player['y'], player['size'], player['size'])\n"),
          ("\n\ndef update(dt):", "\nctx.fill_style = '#10141f'\nctx.fill_rect(0, 0, WIDTH, HEIGHT)\n\n\ndef update(dt):")]),
        ("the square no longer moves at its speed", [("player['speed'] * dt", "player['speed'] / 60")]),
    ],
    "pydbg-04-overhead-rock": [
        ("only the rock's top edge is asked about",
         [(_ROCK_HITS, "    return (a['x'] < b['x'] + b['w'] and a['x'] + a['w'] > b['x']\n"
                       "            and b['y'] < a['y'] + a['h'])\n")]),
        ("only the rock's bottom edge is asked about",
         [(_ROCK_HITS, "    return (a['x'] < b['x'] + b['w'] and a['x'] + a['w'] > b['x']\n"
                       "            and b['y'] + b['h'] > a['y'])\n")]),
        ("the x test is dropped, so a rock beside the player hurts",
         [(_ROCK_HITS, "    return a['y'] < b['y'] + b['h'] and a['y'] + a['h'] > b['y']\n")]),
        ("a rock only counts when its top-left corner is inside the player",
         [(_ROCK_HITS, "    return (a['x'] < b['x'] < a['x'] + a['w']\n"
                       "            and a['y'] < b['y'] < a['y'] + a['h'])\n")]),
        ("a hit takes a life but the rock keeps falling through (no restart)",
         [("        lives -= 1\n        drop_rock()\n", "        lives -= 1\n")]),
    ],
    "pydbg-05-red-balloons": [
        ("the buggy loop runs twice, which hides the bug on one row but not the next",
         [(_BALLOONS_LOOP, _BALLOONS_BUGGY + _BALLOONS_BUGGY)]),
        ("everything is cleared, the blue ones too", [(_BALLOONS_LOOP, "        balloons.clear()\n")]),
        ("only the first red balloon goes",
         [("                balloons.remove(b)\n", "                balloons.remove(b)\n                break\n")]),
        ("the comprehension keeps the red ones", [(_BALLOONS_LOOP, "        balloons[:] = [b for b in balloons if b['color'] == 'red']\n")]),
        ("the comprehension is assigned to a name inside the function (a new local)",
         [(_BALLOONS_LOOP, "        balloons = [b for b in balloons if b['color'] != 'red']\n")]),
    ],
    "pydbg-06-same-spark": [
        ("all the sparks at once, at the right places",
         [(_SPARKS_AFTER, "    after(0.5, lambda i=i: spawn(i))\n")]),
        ("the callback is called now and its None is handed to after()",
         [(_SPARKS_AFTER, "    after(i * 0.5, spawn(i))\n")]),
        ("no timer at all: all five spawn at load", [(_SPARKS_AFTER, "    spawn(i)\n")]),
        ("a lambda that reads i through another name: still the last i",
         [(_SPARKS_AFTER, "    after(i * 0.5, lambda: spawn(i + 0))\n")]),
        ("the right place but a timer that is one-and-a-half times too slow",
         [(_SPARKS_AFTER, "    after(i * 0.75, lambda i=i: spawn(i))\n")]),
    ],
    "pydbg-07-time-is-up": [
        ("global for the wrong other name", [(_CLOCK_UPDATE, "    global time_left, score\n")]),
        ("global for the clock dropped: the clock itself can no longer be changed",
         [(_CLOCK_UPDATE, "    global state\n")]),
        ("over too early", [("if time_left <= 0:", "if time_left <= 3:")]),
        ("clicks go on scoring once it is over",
         [("    if state != 'playing':\n        return\n", "")]),
        ("clicks stop but nothing says why",
         [("    if state == 'over':\n        ctx.font = '32px monospace'\n        ctx.fill_text('Time is up!', 150, 90)\n", "")]),
        ("the message is shown, but the game is not over for clicks", [
            ("    if state != 'playing':\n        return\n", ""),
            ("        state = 'over'\n", "        state = 'over'\n        draw_over()\n"),
            ("def update(dt):", (
                "def draw_over():\n    ctx.font = '32px monospace'\n    ctx.fill_text('Time is up!', 150, 90)\n\n\n"
                "def update(dt):"))]),
    ],
    "pydbg-08-stripe": [
        ("still one row listed eight times, however it is written",
         [(_PAINT_GRID, "grid = [[0 for _ in range(COLS)]] * ROWS")]),
        ("a list of the same row, built by a loop",
         [(_PAINT_GRID, "row = [0] * COLS\ngrid = [row for _ in range(ROWS)]")]),
        ("a deepcopy of the shared row keeps it shared",
         [(_PAINT_GRID, "grid = copy.deepcopy([[0] * COLS] * ROWS)"),
          ("from canvas import", "import copy\n\nfrom canvas import")]),
        ("rows and columns swapped",
         [(_PAINT_GRID, "grid = [[0] * ROWS for _ in range(COLS)]")]),
        ("clicking again never puts a square out",
         [("grid[row][col] = 1 - grid[row][col]", "grid[row][col] = 1")]),
    ],
    "pydbg-09-doubled-wave": [
        ("the old enemies are cut off by slicing: they are still the moved ones",
         [(_WAVES_DEF, "def make_wave(count, enemies=[]):\n"),
          ("        enemies = make_wave(5)\n\n\non_key_down", "        enemies = make_wave(5)[:5]\n\n\non_key_down"),
          ("    return enemies\n", "    return enemies\n")]),
        ("None is the default but no list is ever made",
         [("    if enemies is None:\n        enemies = []\n", "")]),
        ("list() instead of [] is still made once",
         [(_WAVES_DEF, "def make_wave(count, enemies=list()):\n")]),
        ("a tuple default cannot be appended to",
         [(_WAVES_DEF, "def make_wave(count, enemies=()):\n")]),
        ("a fresh wave of the wrong size", [("make_wave(5)\n\n\ndef restart", "make_wave(5)\n\n\ndef restart"),
                                            (_WAVES_RESTART, "        enemies = make_wave(4)\n\n\non_key_down")]),
    ],
    "pydbg-10-one-tile-off": [
        ("a float, never turned into a tile number", [(_TILES_COL, "return x / TILE")]),
        ("rounded, which moves the boundary half a tile", [(_TILES_COL, "return round(x / TILE)")]),
        ("int() with one taken off for the left half (wrong at the exact edges)",
         [(_TILES_COL, "return int(x / TILE) - (1 if x < 0 else 0)")]),
        ("the original int(x / TILE)", [(_TILES_COL, "return int(x / TILE)")]),
        ("floor division but on the wrong thing",
         [(_TILES_COL, "return int(x // TILE) if x >= 0 else int(x / TILE)")]),
    ],
}

#: Right fixes written another way, which the check must still pass.
OTHER_WAYS: dict[str, list[Change]] = {
    "pydbg-01-slow-ball": [
        ("position set from the old one", [(_SLOW_MOVE, "ball['x'] = ball['x'] + ball['vx'] * dt")]),
        ("a step worked out first", [(_SLOW_MOVE, "step = ball['vx'] * dt\n    ball['x'] += step")]),
        ("dt capped, so a long pause is not a jump",
         [("def update(dt):\n", "def update(dt):\n    dt = min(dt, 0.05)\n"), (_SLOW_MOVE, "ball['x'] += ball['vx'] * dt")]),
        ("the clock used instead of dt", [
            ("from canvas import ctx, WIDTH, HEIGHT, on_frame", "from canvas import ctx, WIDTH, HEIGHT, on_frame, now"),
            ("def update(dt):\n", "last = [0.0]\n\n\ndef update(dt):\n    dt = now() - last[0]\n    last[0] = now()\n"),
            (_SLOW_MOVE, "ball['x'] += ball['vx'] * dt")]),
    ],
    "pydbg-02-fuel-gauge": [
        ("a comprehension of positions", [(_GAUGE_LOOP, (
            "    for x in [20 + i * 26 for i in range(fuel)]:\n        ctx.fill_rect(x, 20, 20, 30)\n"))]),
        ("counting from 1", [(_GAUGE_LOOP, (
            "    for i in range(1, fuel + 1):\n        ctx.fill_rect(20 + (i - 1) * 26, 20, 20, 30)\n"))]),
        ("a while loop", [(_GAUGE_LOOP, (
            "    i = 0\n    while i < fuel:\n        ctx.fill_rect(20 + i * 26, 20, 20, 30)\n        i += 1\n"))]),
        ("capped at the tank size", [("range(fuel)", "range(min(fuel, MAX_FUEL))")]),
    ],
    "pydbg-03-smear": [
        ("clear_rect for the wipe", [(_TRAILS_DRAW, _TRAILS_DRAW.replace(
            "    ctx.fill_style = '#10141f'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n",
            "    ctx.clear_rect(0, 0, WIDTH, HEIGHT)\n"))]),
        ("the wipe painted by the loop before it draws", [
            (_TRAILS_DRAW, "def draw():\n    ctx.fill_style = '#4fd1c5'\n"
                           "    ctx.fill_rect(player['x'], player['y'], player['size'], player['size'])\n"),
            (_TRAILS_LOOP, "def loop(dt):\n    update(dt)\n    ctx.fill_style = '#10141f'\n"
                           "    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n    draw()\n")]),
        ("a different colour of wipe", [(_TRAILS_DRAW, _TRAILS_DRAW.replace("#10141f", "#202a44"))]),
        ("the wipe in its own function", [
            (_TRAILS_DRAW, "def wipe():\n    ctx.fill_style = '#10141f'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n\n\n"
                           "def draw():\n    wipe()\n    ctx.fill_style = '#4fd1c5'\n"
                           "    ctx.fill_rect(player['x'], player['y'], player['size'], player['size'])\n")]),
    ],
    "pydbg-04-overhead-rock": [
        ("<= and >=, the edges counting", [(_ROCK_HITS, (
            "    return (a['x'] <= b['x'] + b['w'] and a['x'] + a['w'] >= b['x']\n"
            "            and a['y'] <= b['y'] + b['h'] and a['y'] + a['h'] >= b['y'])\n"))]),
        ("one axis at a time", [(_ROCK_HITS, (
            "    return (overlap(a['x'], a['w'], b['x'], b['w'])\n"
            "            and overlap(a['y'], a['h'], b['y'], b['h']))\n")),
            ("def hits(a, b):", (
                "def overlap(p, p_len, q, q_len):\n    return p < q + q_len and p + p_len > q\n\n\ndef hits(a, b):"))]),
        ("centres and half-sizes", [(_ROCK_HITS, (
            "    return (abs((a['x'] + a['w'] / 2) - (b['x'] + b['w'] / 2)) < (a['w'] + b['w']) / 2\n"
            "            and abs((a['y'] + a['h'] / 2) - (b['y'] + b['h'] / 2)) < (a['h'] + b['h']) / 2)\n"))]),
        ("not (any gap between them)", [(_ROCK_HITS, (
            "    apart = (a['x'] >= b['x'] + b['w'] or a['x'] + a['w'] <= b['x']\n"
            "             or a['y'] >= b['y'] + b['h'] or a['y'] + a['h'] <= b['y'])\n"
            "    return not apart\n"))]),
    ],
    "pydbg-05-red-balloons": [
        ("a slice copy", [(_BALLOONS_LOOP, _BALLOONS_LOOP.replace("list(balloons)", "balloons[:]"))]),
        ("backwards", [(_BALLOONS_LOOP, _BALLOONS_LOOP.replace("list(balloons)", "reversed(balloons)"))]),
        ("a comprehension put back in place", [(_BALLOONS_LOOP, "        balloons[:] = [b for b in balloons if b['color'] != 'red']\n")]),
        ("a comprehension with global", [
            (_BALLOONS_LOOP, "        global balloons\n        balloons = [b for b in balloons if b['color'] != 'red']\n")]),
        ("look again until none is left", [(_BALLOONS_LOOP, (
            "        while any(b['color'] == 'red' for b in balloons):\n"
            "            balloons.remove(next(b for b in balloons if b['color'] == 'red'))\n"))]),
    ],
    "pydbg-06-same-spark": [
        ("a different name for the bound value", [(_SPARKS_AFTER, "    after(i * 0.5, lambda n=i: spawn(n))\n")]),
        ("functools.partial", [
            (_SPARKS_AFTER, "    after(i * 0.5, functools.partial(spawn, i))\n"),
            ("import math\n", "import functools\nimport math\n")]),
        ("a function that makes the callback", [
            (_SPARKS_AFTER, "    after(i * 0.5, later(i))\n"),
            ("for i in range(5):", "def later(n):\n    return lambda: spawn(n)\n\n\nfor i in range(5):")]),
        ("a helper that sets the timer", [
            (_SPARKS_AFTER, "    spawn_later(i)\n"),
            ("for i in range(5):", (
                "def spawn_later(n):\n    after(n * 0.5, lambda: spawn(n))\n\n\nfor i in range(5):"))]),
    ],
    "pydbg-07-time-is-up": [
        ("the clock itself says it is over: no state needed", [
            (_CLOCK_UPDATE, "    global time_left\n"),
            ("    if state != 'playing':\n        return\n", "    if time_left <= 0:\n        return\n"),
            ("    if state == 'over':\n", "    if time_left <= 0:\n")]),
        ("a function that finishes the game, with its own global", [
            (_CLOCK_UPDATE, "    global time_left\n"),
            ("        state = 'over'\n", "        finish()\n"),
            ("def update(dt):", "def finish():\n    global state\n    state = 'over'\n\n\ndef update(dt):")]),
        ("the module's names asked for directly", [
            (_CLOCK_UPDATE, "    global time_left\n"),
            ("        state = 'over'\n", "        globals()['state'] = 'over'\n")]),
        ("the clock written out in full", [("    time_left -= dt\n", "    time_left = time_left - dt\n")]),
    ],
    "pydbg-08-stripe": [
        ("a comprehension inside a comprehension",
         [(_PAINT_GRID, "grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]")]),
        ("a copy of each row",
         [(_PAINT_GRID, "grid = [row[:] for row in [[0] * COLS] * ROWS]")]),
        ("built row by row", [(_PAINT_GRID, "grid = []\nfor _ in range(ROWS):\n    grid.append([0] * COLS)")]),
        ("list() of each row", [(_PAINT_GRID, "grid = [list([0] * COLS) for r in range(ROWS)]")]),
    ],
    "pydbg-09-doubled-wave": [
        ("the caller hands in a new list", [
            (_WAVES_DEF, "def make_wave(count, enemies=[]):\n"),
            (_WAVES_RESTART, "        enemies = make_wave(5, [])\n\n\non_key_down")]),
        ("a copy of the default before using it", [
            (_WAVES_DEF, "def make_wave(count, enemies=[]):\n    enemies = enemies[:]\n")]),
        ("None replaced with or", [
            (_WAVES_DEF, "def make_wave(count, enemies=None):\n    enemies = enemies or []\n")]),
        ("the list is made inside; no argument at all", [
            (_WAVES_DEF, "def make_wave(count):\n    enemies = []\n")]),
        ("the shared list emptied before it is filled", [
            (_WAVES_DEF, "def make_wave(count, enemies=[]):\n    enemies.clear()\n")]),
    ],
    "pydbg-10-one-tile-off": [
        ("math.floor", [(_TILES_COL, "return math.floor(x / TILE)"), ("from canvas import", "import math\n\nfrom canvas import")]),
        ("floor division without int()", [(_TILES_COL, "return x // TILE")]),
        ("shifted so everything is positive first", [(_TILES_COL, "return int((x + MID) // TILE) - MID // TILE")]),
        ("divmod", [(_TILES_COL, "return int(divmod(x, TILE)[0])")]),
    ],
}


def _cases(table: dict[str, list[Change]]):
    return [pytest.param(step_id, label, swaps, id=f"{step_id}:{label[:48]}")
            for step_id, changes in table.items() for label, swaps in changes]


def _changed_lines(a: str, b: str) -> int:
    return sum(1 for line in difflib.ndiff(a.splitlines(), b.splitlines()) if line[:2] in ("+ ", "- "))


class TestShape:
    def test_ids_unique_numbered_and_titled(self) -> None:
        ids = [s.id for s in STEPS]
        assert len(ids) == len(set(ids))
        assert len({s.title for s in STEPS}) == len(STEPS)
        assert len(STEPS) == 11
        for n, s in enumerate(STEPS, 1):
            assert re.fullmatch(rf"pydbg-{n:02d}-[a-z-]+", s.id), s.id
            assert s.track == "Debug it (Python)"
            assert s.language == "python"
            assert s.kind == "canvas"
            assert len(s.teaches) > 120, s.id
            assert s.goal.endswith("."), s.id

    def test_only_the_last_step_is_open(self) -> None:
        assert [s.id for s in STEPS if not s.check] == [STEPS[-1].id]
        assert STEPS[-1].id == "pydbg-11-break-your-own"

    def test_every_checked_step_has_a_hint_and_the_open_one_does_not_need_one(self) -> None:
        for s in STEPS[:-1]:
            assert s.hint, s.id
            assert s.hint.endswith("?") or s.hint.endswith("."), s.id

    def test_the_open_step_suggests_bugs_to_plant(self) -> None:
        last = STEPS[-1]
        assert len(last.teaches) > 400
        assert last.teaches.count(";") >= 6
        assert last.solution == last.starter
        assert "plant" in last.goal

    def test_starters_are_their_own_programs_and_independent(self) -> None:
        starters = [s.starter for s in STEPS]
        assert len(set(starters)) == len(STEPS)
        for s in STEPS:
            compile(s.starter, s.id, "exec")
            compile(s.solution, s.id, "exec")
            for code in (s.starter, s.solution):
                assert "from canvas import" in code, s.id
                assert "\r" not in code and not code.endswith("\n\n"), s.id
                assert "ctx.fillStyle" not in code and "requestAnimationFrame" not in code
            if s.check:
                compile(s.check, s.id + " check", "exec")

    @pytest.mark.parametrize("step_id", CHECKED)
    def test_a_starter_differs_from_its_solution_by_a_small_change(self, step_id: str) -> None:
        s = BY_ID[step_id]
        assert s.starter != s.solution
        assert 0 < _changed_lines(s.starter, s.solution) <= MAX_DIFF_LINES[step_id], step_id
        assert len(s.starter.splitlines()) >= 18, "a program, not a snippet"
        assert len(s.starter.splitlines()) <= 70, "small enough to read at a glance"

    def test_each_goal_names_what_the_check_reads_and_numbers_what_should_hold(self) -> None:
        assert set(NAMED_IN_SPEC) == set(CHECKED)
        for step_id, names in NAMED_IN_SPEC.items():
            goal = BY_ID[step_id].goal
            assert "\n" not in goal, step_id
            assert "1) " in goal and "2) " in goal, step_id
            for name in names:
                assert f"`{name}`" in goal, f"{step_id}: the goal does not name `{name}`"

    def test_a_goal_says_what_you_would_see_not_where_the_bug_is(self) -> None:
        for s in STEPS[:-1]:
            goal = s.goal
            assert re.search(r"\bline \d", goal) is None, s.id
            assert "on line" not in goal and "the bug is" not in goal.lower(), s.id

    def test_every_checked_step_has_mistakes_and_other_ways(self) -> None:
        for step_id in CHECKED:
            assert len(MISTAKES[step_id]) >= 3, step_id
            assert len(OTHER_WAYS[step_id]) >= 2, step_id
        for step_id in list(MISTAKES) + list(OTHER_WAYS):
            assert step_id in BY_ID, step_id

    def test_the_python_bug_classes_are_what_gets_taught(self) -> None:
        text = " ".join(s.teaches + " " + s.hint for s in STEPS)
        for word in ("print(", "breakpoint()", "traceback", "repr", "dt", "range(n + 1)",
                     "late binding", "lambda i=i", "functools.partial", "global", "UnboundLocalError",
                     "[[0] * 12] * 8", "[[0] * 12 for _ in range(8)]", "is grid[1]", "__defaults__",
                     "enemies is None", "is None", "//", "int(-10 / 40)", "balloons[:]", "list(balloons)"):
            assert word in text, word

    def test_every_teaches_names_how_to_hunt_the_bug(self) -> None:
        for s in STEPS[:-1]:
            assert "print" in s.teaches, s.id
            assert re.search(r"[Hh]unt|[Hh]ow to hunt", s.teaches), s.id

    def test_the_timing_sensitive_checks_run_at_30_frames_a_second(self) -> None:
        for step_id in ("pydbg-01-slow-ball", "pydbg-03-smear", "pydbg-04-overhead-rock",
                        "pydbg-06-same-spark", "pydbg-07-time-is-up", "pydbg-10-one-tile-off"):
            check = BY_ID[step_id].check
            assert "1 / 30" in check or "FPS = 30" in check or "(30, 60)" in check, step_id
        for step_id in ("pydbg-01-slow-ball", "pydbg-04-overhead-rock"):
            assert "60" in BY_ID[step_id].check, step_id


class TestChecks:
    @pytest.mark.parametrize("step_id", CHECKED)
    def test_the_solution_passes(self, step_id: str) -> None:
        s = BY_ID[step_id]
        got = run_py_check(s.solution, s.check)
        assert got.passed, got.message

    @pytest.mark.parametrize("step_id", CHECKED)
    def test_the_buggy_starter_runs_and_fails_with_a_symptom(self, step_id: str) -> None:
        s = BY_ID[step_id]
        got = run_py_check(s.starter, s.check)
        assert not got.passed
        assert got.message.startswith("Requirement"), got.message
        assert "Your code threw" not in got.message
        low = got.message.lower()
        for word in CAUSE_WORDS[step_id]:
            assert word.lower() not in low, f"{step_id}: the message names the cause ({word}): {got.message}"

    @pytest.mark.parametrize("step_id", CHECKED)
    def test_the_buggy_starter_runs_without_raising_at_30_and_60_frames_a_second(self, step_id: str) -> None:
        # The bug is quiet: the program loads, runs and draws; nothing raises.
        s = BY_ID[step_id]
        got = run_py_check(s.starter, "cc.frames(120)\ncc.frames(90, 1 / 30)\ncc.press('ArrowLeft')\n"
                                      "cc.frames(30)\ncc.release('ArrowLeft')\ncc.click(240, 170)\ncc.frames(5)")
        assert got.passed, f"{step_id}: {got.message}"

    @pytest.mark.parametrize("step_id,label,swaps", _cases(MISTAKES))
    def test_half_fixes_and_wrong_fixes_still_fail(self, step_id: str, label: str, swaps) -> None:
        s = BY_ID[step_id]
        got = run_py_check(_apply(s.solution, swaps), s.check)
        assert not got.passed, f"the check let this mistake through: {label}"
        assert got.message.startswith(("Requirement", "Your code threw")), f"{label}: {got.message}"

    @pytest.mark.parametrize("step_id,label,swaps", _cases(OTHER_WAYS))
    def test_other_right_fixes_pass(self, step_id: str, label: str, swaps) -> None:
        s = BY_ID[step_id]
        got = run_py_check(_apply(s.solution, swaps), s.check)
        assert got.passed, f"{label}: {got.message}"


#: The behaviour at other frame rates: the solution holds at every one, the
#: starter does not.
_SLOW_AT = """
FPS = {fps}
put = lambda o, k, v: o.__setitem__(k, v)
g.ball['x'] = 100
g.ball['vx'] = 200
cc.frames(FPS, 1 / FPS)
moved = g.ball['x'] - 100
expect(abs(moved - 200) <= 4, f"Requirement 2: at {{FPS}} frames a second one second moved the ball {{moved:.0f}} pixels.")
"""

_ROCK_AT = """
FPS = {fps}
g.lives = 3
g.rock['x'] = g.player['x']
g.rock['y'] = -30
g.rock['vy'] = 180
n = 0
while g.lives == 3 and n < 4 * FPS:
    cc.frames(1, 1 / FPS)
    n += 1
expect(g.lives == 2 and abs(n / FPS - 1.5) < 0.12, f"Requirement 4: at {{FPS}} frames a second the rock hit after {{n / FPS:.2f}} seconds with {{g.lives}} lives left.")
"""


class TestFrameRates:
    @pytest.mark.parametrize("fps", [15, 24, 30, 60, 90, 120])
    def test_the_slow_ball_is_the_same_speed_at_every_frame_rate(self, fps: int) -> None:
        s = BY_ID["pydbg-01-slow-ball"]
        check = _SLOW_AT.format(fps=fps)
        assert run_py_check(s.solution, check).passed
        got = run_py_check(s.starter, check)
        assert (not got.passed) == (fps != 60), f"{fps}: {got.message}"

    @pytest.mark.parametrize("fps", [20, 30, 60, 120])
    def test_a_rock_hurts_at_the_same_time_at_every_frame_rate(self, fps: int) -> None:
        s = BY_ID["pydbg-04-overhead-rock"]
        check = _ROCK_AT.format(fps=fps)
        got = run_py_check(s.solution, check)
        assert got.passed, got.message
        assert not run_py_check(s.starter, check).passed

    @pytest.mark.parametrize("fps", [30, 60, 120])
    def test_the_clock_runs_out_after_five_seconds_at_every_frame_rate(self, fps: int) -> None:
        from code_coach.canvas.content_pydebug import _CLOCK_BODY, _HELPERS

        s = BY_ID["pydbg-07-time-is-up"]
        check = _HELPERS + f"import re\n\nFPS = {fps}\n" + _CLOCK_BODY
        got = run_py_check(s.solution, check)
        assert got.passed, got.message
        assert not run_py_check(s.starter, check).passed


class TestMessages:
    """A failure says what you would see - and not the cause."""

    def _fails(self, step_id: str, swaps: list[tuple[str, str]] | None = None) -> str:
        s = BY_ID[step_id]
        code = _apply(s.solution, swaps) if swaps else s.starter
        got = run_py_check(code, s.check)
        assert not got.passed
        return got.message

    def test_the_slow_ball_names_the_frame_rate_and_the_distance(self) -> None:
        msg = self._fails("pydbg-01-slow-ball")
        assert "Requirement 2" in msg and "30 frames a second" in msg and "50 pixels" in msg

    def test_the_gauge_counts_cells(self) -> None:
        msg = self._fails("pydbg-02-fuel-gauge")
        assert "fuel at 6" in msg and "7 cells" in msg and "exactly 6" in msg
        msg = self._fails("pydbg-02-fuel-gauge", [("range(fuel)", "range(fuel + (1 if fuel else 0))")])
        assert "fuel at 6" in msg or "Requirement" in msg

    def test_the_smear_says_what_stays_on_the_screen(self) -> None:
        msg = self._fails("pydbg-03-smear")
        assert "leaves a trail" in msg and "smear" in msg
        msg = self._fails("pydbg-03-smear", [(_TRAILS_DRAW, (
            "def draw():\n    ctx.fill_style = '#4fd1c5'\n"
            "    ctx.fill_rect(player['x'], player['y'], player['size'], player['size'])\n"
            "    ctx.fill_style = '#10141f'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n"))])
        assert "cannot be seen" in msg

    def test_the_rock_says_which_rock_hurt_and_how_many_lives(self) -> None:
        msg = self._fails("pydbg-04-overhead-rock")
        assert "Requirement 2" in msg and "far above the player's head" in msg and "1 of the player's 3 lives" in msg

    def test_the_balloons_count_what_is_left(self) -> None:
        msg = self._fails("pydbg-05-red-balloons")
        assert "3 of the 7 red balloons are still floating" in msg

    def test_the_sparks_list_where_they_are(self) -> None:
        msg = self._fails("pydbg-06-same-spark")
        assert "[420, 420, 420, 420, 420]" in msg

    def test_the_clock_says_nothing_is_raised(self) -> None:
        msg = self._fails("pydbg-07-time-is-up")
        assert "clicks do nothing" in msg
        # A silent bug stays silent: the starter's trace holds no error.
        s = BY_ID["pydbg-07-time-is-up"]
        got = run_py_check(s.starter, "cc.frames(400, 1 / 30)")
        assert got.passed

    def test_a_missing_global_on_the_clock_itself_is_a_traceback_with_its_line(self) -> None:
        # The loud twin of the quiet bug: reading the name first raises, and the harness says where.
        s = BY_ID["pydbg-07-time-is-up"]
        code = _apply(s.solution, [("    global time_left, state\n", "    global state\n")])
        got = run_py_check(code, s.check)
        assert not got.passed
        assert "UnboundLocalError" in got.message and "line" in got.message

    def test_the_grid_says_which_squares_lit(self) -> None:
        msg = self._fails("pydbg-08-stripe")
        assert "lit 8 squares" in msg and "rows [0, 1, 2, 3, 4, 5, 6, 7]" in msg

    def test_the_wave_counts_enemies(self) -> None:
        msg = self._fails("pydbg-09-doubled-wave")
        assert "10 enemies" in msg and "exactly 5" in msg

    def test_the_tile_names_the_player_the_tile_and_the_label(self) -> None:
        msg = self._fails("pydbg-10-one-tile-off")
        assert "inside tile -1" in msg and "label says 'tile 0'" in msg


class TestTheOpenStep:
    def test_it_has_no_check_and_a_working_program_as_its_start(self) -> None:
        last = STEPS[-1]
        assert last.check == ""
        assert last.solution == last.starter

    def test_the_program_runs_and_catches_a_star(self) -> None:
        last = STEPS[-1]
        check = (
            "cc.frames(30, 1 / 30)\n"
            "g.star['x'] = g.basket['x']\n"
            "g.star['y'] = g.basket['y'] - 10\n"
            "before = g.score\n"
            "cc.frames(3, 1 / 30)\n"
            "expect(g.score == before + 1, 'the basket should catch a star that falls onto it')\n"
            "cc.press('ArrowLeft')\n"
            "cc.frames(180, 1 / 60)\n"
            "cc.release('ArrowLeft')\n"
            "expect(g.basket['x'] == 0, 'the basket stops at the left edge')\n"
            "expect(any('caught' in t for t in cc.texts()), 'the score is on the screen')\n"
        )
        got = run_py_check(last.starter, check)
        assert got.passed, got.message
