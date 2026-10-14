"""Canvas: the "From blank (Python)" track.

Like the JavaScript "From blank" track (test_canvas_blank.py) these steps are
independent: each starter is blank, not the step before. So the suite holds
each project to: ids unique, only the last step open, every blank starter
FAILS its check (with a message that begins "Requirement N:"), every solution
passes, each real mistake fails (with a "Requirement N:" message that says
what is wrong), and other ways of writing the same behaviour pass - the check
plays the program and reads only the names the spec states, in a dict or in a
dataclass alike.

The tests look steps up by id in their own module, so they need no
registration in canvas/__init__.py.
"""

from __future__ import annotations

import re

import pytest

from code_coach.canvas import run_py_check
from code_coach.canvas.content_pyblank import PYBLANK_STEPS as STEPS

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


# The names the check reads: the goal must name each one, in backticks.
NAMED_IN_SPEC: dict[str, list[str]] = {
    "pyblank-01-pong": ["left", "right", "ball", "score"],
    "pyblank-02-flappy": ["bird", "pipes", "score", "state"],
    "pyblank-03-memory": ["cards", "state"],
    "pyblank-04-stacker": ["grid", "piece", "score", "state"],
}

# -- Pieces of the solutions the mistakes cut out --------------------------------

_PONG_HITS = (
    "    nearest_x = max(p['x'], min(b['x'], p['x'] + p['w']))\n"
    "    nearest_y = max(p['y'], min(b['y'], p['y'] + p['h']))\n"
    "    return math.hypot(b['x'] - nearest_x, b['y'] - nearest_y) < b['r']\n"
)
_PONG_LEFT_BOUNCE = (
    "    if ball['vx'] < 0 and hits(ball, left):\n"
    "        ball['x'] = left['x'] + left['w'] + ball['r']\n"
    "        ball['vx'] = abs(ball['vx'])\n"
)
_PONG_RIGHT_BOUNCE = (
    "    if ball['vx'] > 0 and hits(ball, right):\n"
    "        ball['x'] = right['x'] - ball['r']\n"
    "        ball['vx'] = -abs(ball['vx'])\n"
)
_PONG_BOTTOM = (
    "    if ball['y'] + ball['r'] > HEIGHT:\n"
    "        ball['y'] = HEIGHT - ball['r']\n"
    "        ball['vy'] = -abs(ball['vy'])\n"
)

_FLAPPY_SPAWN = (
    "    spawn_timer += dt\n    if spawn_timer >= 1.5:\n        spawn_timer -= 1.5\n"
    "        pipes.append(Pipe(WIDTH, random.uniform(30, 180)))\n"
)
_FLAPPY_TOUCHES = (
    "    nearest_x = max(x, min(bird['x'], x + w))\n"
    "    nearest_y = max(y, min(bird['y'], y + h))\n"
    "    return math.dist((bird['x'], bird['y']), (nearest_x, nearest_y)) < bird['r']\n"
)
_FLAPPY_TRIM = "    pipes = [p for p in pipes if p.x + p.w > 0]\n"

_MEMORY_DEAL = (
    "cards = []\nfor i, value in enumerate(values):\n    row, col = divmod(i, 4)\n"
    "    cards.append(Card(30 + col * 110, 20 + row * 100, value))\n"
)
_MEMORY_LATER = "        after(0.8, lambda: hide(a, card))\n"
_MEMORY_DRAW_VALUE = (
    "        if c.face_up:\n            ctx.fill_style = '#10141f'\n"
    "            ctx.fill_text(f'{c.value}', c.x + 36, c.y + 52)\n"
)

_STACKER_CLEAR = (
    "    kept = [row for row in grid if not all(row)]\n    cleared = ROWS - len(kept)\n"
    "    grid = empty_rows(cleared) + kept\n    score += 10 * cleared\n"
)
_STACKER_KEYS = (
    "    if key == 'ArrowLeft' and fits(piece['col'] - 1, piece['row']):\n        piece['col'] -= 1\n"
    "    elif key == 'ArrowRight' and fits(piece['col'] + 1, piece['row']):\n        piece['col'] += 1\n"
    "    elif key == 'ArrowDown':\n"
)

#: Wrong programs, each a real mistake at that project, that the check must
#: fail - and fail with a message that begins "Requirement N:".
MISTAKES: dict[str, list[Change]] = {
    "pyblank-01-pong": [
        ("no clamp: paddles leave the canvas",
         [("    p['y'] = max(0, min(HEIGHT - p['h'], p['y']))\n", "")]),
        ("paddle speed per frame, not per second",
         [("p['y'] -= p['speed'] * dt", "p['y'] -= 5"), ("p['y'] += p['speed'] * dt", "p['y'] += 5")]),
        ("the ball does not bounce off the left paddle", [(_PONG_LEFT_BOUNCE, "")]),
        ("the ball does not bounce off the right paddle", [(_PONG_RIGHT_BOUNCE, "")]),
        ("a fast ball passes through: only the ball's centre is tested",
         [(_PONG_HITS, "    return p['x'] <= b['x'] <= p['x'] + p['w'] and p['y'] <= b['y'] <= p['y'] + p['h']\n")]),
        ("the paddle test ignores where the paddle is vertically",
         [(_PONG_HITS, "    return b['x'] - b['r'] < p['x'] + p['w'] and b['x'] + b['r'] > p['x']\n")]),
        ("points go to the wrong player",
         [("        score['right'] += 1\n        serve(-1)", "        score['left'] += 1\n        serve(-1)"),
          ("        score['left'] += 1\n        serve(1)", "        score['right'] += 1\n        serve(1)")]),
        ("no serve after a point",
         [("        score['right'] += 1\n        serve(-1)\n", "        score['right'] += 1\n")]),
        ("served away from the loser", [("        serve(-1)\n", "        serve(1)\n")]),
        ("served away from the loser after a point on the right",
         [("        score['left'] += 1\n        serve(1)", "        score['left'] += 1\n        serve(-1)")]),
        ("r does not put the paddles back", [("        left['y'] = right['y'] = 130\n", "")]),
        ("r does not reset the score", [("        score['left'] = score['right'] = 0\n", "")]),
        ("r does not serve", [("        serve(1)\n\n\non_key_down", "        pass\n\n\non_key_down")]),
        ("no bounce off the bottom edge", [(_PONG_BOTTOM, "")]),
        ("a bounce off the top leaves the ball outside",
         [("        ball['y'] = ball['r']\n", "")]),
    ],
    "pyblank-02-flappy": [
        ("flap adds to vy instead of setting it",
         [("        bird['vy'] = -300\n", "        bird['vy'] -= 300\n")]),
        ("a pipe is counted every frame once passed",
         [("if not p.passed and p.x + p.w < bird['x']:", "if p.x + p.w < bird['x']:")]),
        ("gravity per frame, not per second", [("bird['vy'] += 900 * dt", "bird['vy'] += 15")]),
        ("pipes move per frame, not per second", [("p.x -= 150 * dt", "p.x -= 2.5")]),
        ("pipes arrive by counting frames", [(_FLAPPY_SPAWN, (
            "    spawn_timer += 1\n    if spawn_timer >= 90:\n        spawn_timer -= 90\n"
            "        pipes.append(Pipe(WIDTH, random.uniform(30, 180)))\n"))]),
        ("pipes are never recycled", [(_FLAPPY_TRIM, "")]),
        ("collision uses only the centre of the bird",
         [(_FLAPPY_TOUCHES, "    return x <= bird['x'] <= x + w and y <= bird['y'] <= y + h\n")]),
        ("the bottom half of a pipe is harmless",
         [(" or touches(p.x, p.gap_y + p.gap_h, p.w, HEIGHT)", "")]),
        ("everything keeps moving after game over",
         [("    if state != 'playing':\n        return\n    bird['vy']", "    bird['vy']")]),
        ("restart leaves the old pipes", [("    pipes = []\n    spawn_timer = 0\n", "    spawn_timer = 0\n")]),
        ("restart leaves the old score", [("    score = 0\n    state = 'playing'\n", "    state = 'playing'\n")]),
        ("the floor is safe",
         [("if bird['y'] - bird['r'] < 0 or bird['y'] + bird['r'] > HEIGHT:", "if bird['y'] - bird['r'] < 0:")]),
        ("the restart press also flaps",
         [("        restart()\n", "        restart()\n        bird['vy'] = -300\n")]),
        ("the gaps are all in the same place", [("random.uniform(30, 180)", "100")]),
        ("gaps can leave the canvas", [("random.uniform(30, 180)", "random.uniform(0, 260)")]),
    ],
    "pyblank-03-memory": [
        ("the mismatch timeout counts frames", [
            (_MEMORY_LATER, "        pending[:] = [a, card, 48]\n"),
            ("on_frame(draw)\n", (
                "pending = []\n\n\ndef tick(dt):\n    if pending:\n        pending[2] -= 1\n"
                "        if pending[2] <= 0:\n            hide(pending[0], pending[1])\n"
                "            pending.clear()\n    draw(dt)\n\n\non_frame(tick)\n"))]),
        ("mismatch flips back too soon", [("after(0.8,", "after(0.1,")]),
        ("a mismatch never flips back", [(_MEMORY_LATER, "        pass\n")]),
        ("a third card can be turned while two are showing",
         [("    if locked or state != 'playing':\n", "    if state != 'playing':\n")]),
        ("a match does not stay face up",
         [("        a.matched = card.matched = True\n",
           "        a.matched = card.matched = True\n        a.face_up = card.face_up = False\n")]),
        ("a pair is never marked matched", [("        a.matched = card.matched = True\n", "        pass\n")]),
        ("the cards are one card listed twelve times (aliasing)",
         [(_MEMORY_DEAL, "cards = [Card(30, 20, 0)] * 12\n")]),
        ("a face-up card can be clicked again and matches itself",
         [("if not c.face_up and c.x <= x", "if c.x <= x")]),
        ("the lock is never taken off", [("    a.face_up = b.face_up = False\n    locked = False\n", "    a.face_up = b.face_up = False\n")]),
        ("the first pick is never forgotten", [("    a, first = first, None\n", "    a = first\n")]),
        ("any one match wins", [("if all(c.matched for c in cards):", "if any(c.matched for c in cards):")]),
        ("face-down cards show their value",
         [(_MEMORY_DRAW_VALUE, "        ctx.fill_style = '#10141f'\n        ctx.fill_text(f'{c.value}', c.x + 36, c.y + 52)\n")]),
        ("not shuffled", [("random.shuffle(values)\n", "")]),
    ],
    "pyblank-04-stacker": [
        ("landing ignores filled cells",
         [(" and not grid[row + dr][col + dc]", "")]),
        ("no left wall", [("0 <= col + dc < COLS", "col + dc < COLS")]),
        ("rows are zeroed but the rows above stay put", [(_STACKER_CLEAR, (
            "    cleared = 0\n    for row in grid:\n        if all(row):\n"
            "            row[:] = [0] * COLS\n            cleared += 1\n    score += 10 * cleared\n"))]),
        ("a row with any cell filled is cleared", [("if not all(row)]", "if not any(row)]")]),
        ("only one row is cleared when two fill", [(_STACKER_CLEAR, (
            "    cleared = 0\n    for r in range(ROWS - 1, -1, -1):\n        if all(grid[r]):\n"
            "            del grid[r]\n            grid.insert(0, [0] * COLS)\n            cleared += 1\n"
            "    score += 10 * cleared\n"))]),
        ("rows clear but the score does not move", [("    score += 10 * cleared\n", "")]),
        ("the grid is one row listed twenty times (aliasing)",
         [("    return [[0] * COLS for _ in range(n)]", "    return [[0] * COLS] * n")]),
        ("new rows after a clear are one row listed twice (aliasing)",
         [("    grid = empty_rows(cleared) + kept\n", "    grid = [[0] * COLS] * cleared + kept\n")]),
        ("no game over", [("    if not fits(4, 0):\n        state = 'over'\n", "")]),
        ("Enter does not restart", [("        if key == 'Enter':\n            restart()\n", "        pass\n")]),
        ("restart does not clear the grid",
         [("    grid = empty_rows(ROWS)\n    score = 0\n", "    score = 0\n")]),
        ("restart does not reset the score",
         [("    score = 0\n    state = 'playing'\n    piece", "    state = 'playing'\n    piece")]),
        ("gravity every frame", [("every(0.5, gravity)\n", "on_frame(lambda dt: gravity())\n")]),
        ("gravity counts frames", [("every(0.5, gravity)\n", (
            "ticks = [0]\n\n\ndef count_frames(dt):\n    ticks[0] += 1\n    if ticks[0] % 30 == 0:\n"
            "        gravity()\n\n\non_frame(count_frames)\n"))]),
        ("holding a key moves the piece every frame", [
            ("on_key_down, every\n", "on_key_down, every, keys\n"),
            (_STACKER_KEYS, "    if key == 'ArrowDown':\n"),
            ("on_key_down(key_down)\n", (
                "on_key_down(key_down)\n\n\ndef move_sideways(dt):\n    if state != 'playing':\n        return\n"
                "    if 'ArrowLeft' in keys and fits(piece['col'] - 1, piece['row']):\n        piece['col'] -= 1\n"
                "    if 'ArrowRight' in keys and fits(piece['col'] + 1, piece['row']):\n        piece['col'] += 1\n\n\n"
                "on_frame(move_sideways)\n"))]),
    ],
}


# -- The same programs, written another way ---------------------------------------


def _pong_dataclasses(code: str) -> str:
    """Pong with the paddles, the ball and the score dataclasses: ball.x for ball['x']."""
    code = code.replace("import math\n", "import math\nfrom dataclasses import dataclass\n", 1)
    code = code.replace(
        "left = {'x': 20, 'y': 130, 'w': 10, 'h': 60, 'speed': 300}\n"
        "right = {'x': 450, 'y': 130, 'w': 10, 'h': 60, 'speed': 300}\n"
        "ball = {'x': 240, 'y': 160, 'r': 8, 'vx': 220, 'vy': 140}\n"
        "score = {'left': 0, 'right': 0}\n",
        "@dataclass\nclass Paddle:\n    x: float\n    y: float\n    w: int\n    h: int\n    speed: float\n\n\n"
        "@dataclass\nclass Ball:\n    x: float\n    y: float\n    r: int\n    vx: float\n    vy: float\n\n\n"
        "@dataclass\nclass Score:\n    left: int = 0\n    right: int = 0\n\n\n"
        "left = Paddle(20, 130, 10, 60, 300)\nright = Paddle(450, 130, 10, 60, 300)\n"
        "ball = Ball(240, 160, 8, 220, 140)\nscore = Score()\n",
    )
    made = re.sub(r"\b(ball|left|right|score|p|b)\['(\w+)'\]", r"\1.\2", code)
    assert "['" not in made
    return made


def _flappy_dicts(code: str) -> str:
    """Flappy with the pipes dicts, not a dataclass: p['x'] for p.x."""
    code = code.replace("from dataclasses import dataclass\n", "")
    code = code.replace(
        "@dataclass\nclass Pipe:\n    x: float\n    gap_y: float\n    w: int = 50\n    gap_h: int = 110\n"
        "    passed: bool = False\n",
        "def Pipe(x, gap_y):\n    return {'x': x, 'gap_y': gap_y, 'w': 50, 'gap_h': 110, 'passed': False}\n",
    )
    return re.sub(r"\bp\.(x|w|gap_y|gap_h|passed)\b", r"p['\1']", code)


def _flappy_bird_dataclass(code: str) -> str:
    if "from dataclasses import dataclass" not in code:
        code = code.replace("import random\n", "import random\nfrom dataclasses import dataclass\n", 1)
    code = code.replace(
        "bird = {'x': 100, 'y': 160, 'r': 12, 'vy': 0}\n",
        "@dataclass\nclass Bird:\n    x: float\n    y: float\n    r: int\n    vy: float\n\n\n"
        "bird = Bird(100, 160, 12, 0)\n",
    )
    made = re.sub(r"\bbird\['(\w+)'\]", r"bird.\1", code)
    assert "bird['" not in made
    return made


def _memory_dicts(code: str) -> str:
    """Memory with the cards dicts, not a dataclass: card['face_up'] for card.face_up."""
    code = code.replace("from dataclasses import dataclass\n", "")
    code = code.replace(
        "@dataclass\nclass Card:\n    x: float\n    y: float\n    value: int\n    w: int = 90\n    h: int = 80\n"
        "    face_up: bool = False\n    matched: bool = False\n",
        "def Card(x, y, value):\n    return {'x': x, 'y': y, 'value': value, 'w': 90, 'h': 80,"
        " 'face_up': False, 'matched': False}\n",
    )
    return re.sub(r"\b(c|card|a|b)\.(x|y|w|h|value|face_up|matched)\b", r"\1['\2']", code)


def _stacker_dataclass(code: str) -> str:
    """Stacker with the piece a dataclass: piece.col for piece['col']."""
    code = code.replace("from canvas import", "from dataclasses import dataclass\n\nfrom canvas import", 1)
    code = code.replace(
        "piece = {'col': 4, 'row': 0}\n",
        "@dataclass\nclass Piece:\n    col: int\n    row: int\n\n\npiece = Piece(4, 0)\n",
    )
    made = re.sub(r"\bpiece\['(\w+)'\]", r"piece.\1", code)
    assert "piece['" not in made
    return made


#: Whole-program rewrites: the same game, held in other structures.
REWRITES: dict[str, dict[str, object]] = {
    "pyblank-01-pong": {"paddles, ball and score as dataclasses": _pong_dataclasses},
    "pyblank-02-flappy": {
        "pipes as dicts": _flappy_dicts,
        "the bird a dataclass": _flappy_bird_dataclass,
        "the bird and the pipes both written the other way": lambda c: _flappy_bird_dataclass(_flappy_dicts(c)),
    },
    "pyblank-03-memory": {"cards as dicts": _memory_dicts},
    "pyblank-04-stacker": {"the piece a dataclass": _stacker_dataclass},
}

#: Right programs written another way, which the check must still pass.
OTHER_WAYS: dict[str, list[Change]] = {
    "pyblank-01-pong": [
        ("the ball as a box against the paddle", [(_PONG_HITS, (
            "    return (b['x'] + b['r'] > p['x'] and b['x'] - b['r'] < p['x'] + p['w']\n"
            "            and b['y'] + b['r'] > p['y'] and b['y'] - b['r'] < p['y'] + p['h'])\n"))]),
        ("on_frame as a decorator", [(
            "def loop(dt):\n    update(dt)\n    draw()\n\n\non_frame(loop)\n",
            "@on_frame\ndef loop(dt):\n    update(dt)\n    draw()\n")]),
        ("r read from the held keys", [
            ("on_key_down(new_match)\n", ""),
            ("def loop(dt):\n    update(dt)\n", "def loop(dt):\n    if 'r' in keys:\n        new_match('r')\n    update(dt)\n")]),
        ("copysign for the bounces", [
            ("ball['vy'] = abs(ball['vy'])", "ball['vy'] = math.copysign(ball['vy'], 1)")]),
        ("a serve that starts with a different vy", [("ball['vx'], ball['vy'] = 220 * direction, 140", "ball['vx'], ball['vy'] = 220 * direction, -90")]),
    ],
    "pyblank-02-flappy": [
        ("position before velocity", [(
            "    bird['vy'] += 900 * dt\n    bird['y'] += bird['vy'] * dt",
            "    bird['y'] += bird['vy'] * dt\n    bird['vy'] += 900 * dt")]),
        ("pipes spawned by every()", [
            ("on_key_down\n", "on_key_down, every\n"),
            (_FLAPPY_SPAWN, ""),
            ("def update(dt):", (
                "def spawn():\n    if state == 'playing':\n        pipes.append(Pipe(WIDTH, random.uniform(30, 180)))\n\n\n"
                "every(1.5, spawn)\n\n\ndef update(dt):"))]),
        ("the bird as a box", [(_FLAPPY_TOUCHES, (
            "    return (bird['x'] + bird['r'] > x and bird['x'] - bird['r'] < x + w\n"
            "            and bird['y'] + bird['r'] > y and bird['y'] - bird['r'] < y + h)\n"))]),
        ("pipes trimmed in place, so no global for them", [
            ("    global pipes, spawn_timer, score, state\n    if state != 'playing':",
             "    global spawn_timer, score, state\n    if state != 'playing':"),
            (_FLAPPY_TRIM, "    pipes[:] = [p for p in pipes if p.x + p.w > 0]\n")]),
        ("whole-number gaps", [("random.uniform(30, 180)", "random.randint(30, 180)")]),
        ("pipes trimmed a little later", [("p.x + p.w > 0", "p.x + p.w > -50")]),
    ],
    "pyblank-03-memory": [
        ("a lock worked out from the cards", [(
            "    if locked or state != 'playing':\n",
            "    if sum(1 for c in cards if c.face_up and not c.matched) >= 2 or state != 'playing':\n")]),
        ("shuffled with sample", [("random.shuffle(values)\n", "values = random.sample(values, len(values))\n")]),
        ("a slower flip back", [("after(0.8,", "after(0.9,")]),
        ("dealt with zip", [(_MEMORY_DEAL, (
            "slots = [(col, row) for row in range(3) for col in range(4)]\n"
            "cards = [Card(30 + col * 110, 20 + row * 100, value) for value, (col, row) in zip(values, slots)]\n"))]),
        ("on_click as a decorator", [
            ("def click(x, y):\n    global first, locked, state\n",
             "@on_click\ndef click(x, y):\n    global first, locked, state\n"),
            ("on_click(click)\n", "")]),
    ],
    "pyblank-04-stacker": [
        ("gravity from a timer you add dt to", [("every(0.5, gravity)\n", (
            "timer = 0\n\n\ndef tick(dt):\n    global timer\n    timer += dt\n    if timer >= 0.5:\n"
            "        timer -= 0.5\n        gravity()\n\n\non_frame(tick)\n"))]),
        ("clearing rows with a loop that looks again", [(_STACKER_CLEAR, (
            "    cleared = 0\n    r = ROWS - 1\n    while r >= 0:\n        if all(grid[r]):\n"
            "            del grid[r]\n            grid.insert(0, [0] * COLS)\n            cleared += 1\n"
            "        else:\n            r -= 1\n    score += 10 * cleared\n"))]),
        ("the grid changed in place, so no global for it", [
            ("    global grid, score\n    kept", "    global score\n    kept"),
            ("    grid = empty_rows(cleared) + kept\n", "    grid[:] = empty_rows(cleared) + kept\n")]),
        ("restart empties the grid in place", [
            ("    global grid, score, state\n", "    global score, state\n"),
            ("    grid = empty_rows(ROWS)\n    score = 0\n", "    grid[:] = empty_rows(ROWS)\n    score = 0\n")]),
        ("piece cells from nested loops", [(
            "    for dc, dr in SHAPE:\n        grid[piece['row'] + dr][piece['col'] + dc] = 1\n",
            "    for dr in range(2):\n        for dc in range(2):\n            grid[piece['row'] + dr][piece['col'] + dc] = 1\n")]),
    ],
}


def _cases(table: dict[str, list[Change]]):
    return [pytest.param(step_id, label, swaps, id=f"{step_id}:{label[:48]}")
            for step_id, changes in table.items() for label, swaps in changes]


class TestShape:
    def test_ids_unique_numbered_and_titled(self) -> None:
        ids = [s.id for s in STEPS]
        assert len(ids) == len(set(ids))
        assert len({s.title for s in STEPS}) == len(STEPS)
        for n, s in enumerate(STEPS, 1):
            assert re.fullmatch(rf"pyblank-{n:02d}-[a-z-]+", s.id), s.id
            assert s.track == "From blank (Python)"
            assert s.language == "python"
            assert s.kind == "canvas"
            assert len(s.teaches) > 120, s.id
            assert s.goal.endswith("."), s.id

    def test_only_the_last_step_is_open(self) -> None:
        assert [s.id for s in STEPS if not s.check] == [STEPS[-1].id]
        assert STEPS[-1].id == "pyblank-05-yours"

    def test_the_open_step_has_a_brainstorm_list(self) -> None:
        open_step = STEPS[-1]
        assert len(open_step.teaches) > 400
        assert open_step.teaches.count(";") >= 6

    def test_starters_are_blank_and_independent(self) -> None:
        for s in STEPS:
            assert len(s.starter) < 220, s.id
            assert "from canvas import" in s.starter and "import random" in s.starter
            assert "def " not in s.starter and "on_frame(" not in s.starter
            assert "\r" not in s.starter
            assert s.starter.rstrip().endswith("# Your game goes here.")
        assert len({s.starter for s in STEPS}) == 1
        for s in STEPS[:-1]:
            assert s.starter != s.solution

    def test_every_program_is_python_that_compiles_and_uses_the_library(self) -> None:
        for s in STEPS:
            for code in (s.starter, s.solution):
                compile(code, s.id, "exec")
                assert "from canvas import" in code, s.id
                assert "ctx.fillStyle" not in code and "requestAnimationFrame" not in code
                assert "\r" not in code and not code.endswith("\n\n")
            if s.check:
                compile(s.check, s.id + " check", "exec")

    def test_each_goal_is_a_numbered_spec_that_names_what_the_check_reads(self) -> None:
        for step_id, names in NAMED_IN_SPEC.items():
            s = BY_ID[step_id]
            assert s.hint, step_id
            numbers = [f"{n}) " for n in range(1, 7)]
            assert all(n in s.goal for n in numbers), f"{step_id}: numbered requirements 1) to 6)"
            assert "\n" not in s.goal, f"{step_id}: one inline paragraph"
            for name in names:
                assert f"`{name}`" in s.goal, f"{step_id}: the goal does not name `{name}`"

    def test_the_spec_says_how_the_things_are_held(self) -> None:
        # Pong pinned score.left / score.right in the JavaScript track; here it is the dict's keys.
        pong = BY_ID["pyblank-01-pong"].goal
        assert "score['left']" in pong and ".left and .right" in pong
        assert "dataclass" in pong
        assert "gap_y" in BY_ID["pyblank-02-flappy"].goal and "gap_h" in BY_ID["pyblank-02-flappy"].goal
        assert "face_up" in BY_ID["pyblank-03-memory"].goal and "after(0.8" in BY_ID["pyblank-03-memory"].goal
        assert "holding the key does not repeat" in BY_ID["pyblank-04-stacker"].goal

    def test_every_checked_step_has_mistakes_and_other_ways(self) -> None:
        assert set(NAMED_IN_SPEC) == set(CHECKED)
        for step_id in CHECKED:
            assert len(MISTAKES[step_id]) >= 2, step_id
            assert len(OTHER_WAYS[step_id]) >= 1, step_id
            assert step_id in REWRITES, step_id
        for step_id in list(MISTAKES) + list(OTHER_WAYS) + list(REWRITES):
            assert step_id in BY_ID, step_id

    def test_the_python_way_is_what_gets_taught(self) -> None:
        text = " ".join(s.teaches + " " + s.hint for s in STEPS)
        for word in ("@dataclass", "dict", "comprehension", "[[0] * 10 for _ in range(20)]", "[[0] * 10] * 20",
                     "random.shuffle", "random.sample", "zip", "enumerate", "divmod", "after(0.8", "every(0.5",
                     "unpacks a tuple", "any(", "all(row)", "f-string", "global", "on_key_down", "math.dist",
                     "max(0, min("):
            assert word in text, word

    def test_the_timing_sensitive_checks_run_at_30_frames_a_second(self) -> None:
        for step_id in CHECKED:
            check = BY_ID[step_id].check
            assert "1 / 30" in check or "S30" in check or "S = 1 / 30" in check, step_id


class TestChecks:
    @pytest.mark.parametrize("step_id", CHECKED)
    def test_the_solution_passes(self, step_id: str) -> None:
        s = BY_ID[step_id]
        got = run_py_check(s.solution, s.check)
        assert got.passed, got.message

    @pytest.mark.parametrize("step_id", CHECKED)
    def test_the_blank_starter_fails_and_says_which_requirement(self, step_id: str) -> None:
        s = BY_ID[step_id]
        got = run_py_check(s.starter, s.check)
        assert not got.passed
        assert got.message.startswith("Requirement"), got.message
        assert "Your code threw" not in got.message

    @pytest.mark.parametrize("step_id,label,swaps", _cases(MISTAKES))
    def test_real_mistakes_fail_and_say_what_is_wrong(self, step_id: str, label: str, swaps) -> None:
        s = BY_ID[step_id]
        got = run_py_check(_apply(s.solution, swaps), s.check)
        assert not got.passed, f"the check let this mistake through: {label}"
        assert got.message.startswith("Requirement"), f"{label}: {got.message}"

    @pytest.mark.parametrize("step_id,label,swaps", _cases(OTHER_WAYS))
    def test_other_right_answers_pass(self, step_id: str, label: str, swaps) -> None:
        s = BY_ID[step_id]
        got = run_py_check(_apply(s.solution, swaps), s.check)
        assert got.passed, f"{label}: {got.message}"

    @pytest.mark.parametrize(
        "step_id,label",
        [pytest.param(step_id, label, id=f"{step_id}:{label}")
         for step_id, ways in REWRITES.items() for label in ways],
    )
    def test_dicts_and_dataclasses_both_pass(self, step_id: str, label: str) -> None:
        s = BY_ID[step_id]
        code = REWRITES[step_id][label](s.solution)  # type: ignore[operator]
        assert code != s.solution
        compile(code, step_id, "exec")
        got = run_py_check(code, s.check)
        assert got.passed, f"{label}: {got.message}"

    def test_the_other_structure_still_fails_the_same_mistakes(self) -> None:
        # The dataclass form of a few mistakes that hang on a field's name: the check reads both forms alike.
        pong = BY_ID["pyblank-01-pong"]
        code = _pong_dataclasses(_apply(pong.solution, [(_PONG_LEFT_BOUNCE, "")]))
        assert not run_py_check(code, pong.check).passed
        flappy = BY_ID["pyblank-02-flappy"]
        code = _flappy_dicts(_apply(flappy.solution, [(_FLAPPY_TRIM, "")]))
        assert not run_py_check(code, flappy.check).passed
        memory = BY_ID["pyblank-03-memory"]
        code = _memory_dicts(_apply(memory.solution, [("random.shuffle(values)\n", "")]))
        assert not run_py_check(code, memory.check).passed
        stacker = BY_ID["pyblank-04-stacker"]
        code = _stacker_dataclass(_apply(stacker.solution, [("0 <= col + dc < COLS", "col + dc < COLS")]))
        assert not run_py_check(code, stacker.check).passed


class TestMessages:
    """A failure says which requirement and what to change, not only that it failed."""

    def _fails(self, step_id: str, swaps: list[tuple[str, str]]) -> str:
        s = BY_ID[step_id]
        got = run_py_check(_apply(s.solution, swaps), s.check)
        assert not got.passed
        return got.message

    def test_pong_names_the_frame_rate_and_the_fast_ball(self) -> None:
        msg = self._fails("pyblank-01-pong", [("p['y'] -= p['speed'] * dt", "p['y'] -= 5"),
                                               ("p['y'] += p['speed'] * dt", "p['y'] += 5")])
        assert "Requirement 3" in msg and "30 frames a second" in msg
        msg = self._fails("pyblank-01-pong",
                          [(_PONG_HITS, "    return p['x'] <= b['x'] <= p['x'] + p['w'] and p['y'] <= b['y'] <= p['y'] + p['h']\n")])
        assert "Requirement 5" in msg and "fast ball" in msg

    def test_pong_serve_directions_are_separate_requirements(self) -> None:
        msg = self._fails("pyblank-01-pong", [("        serve(-1)\n", "        serve(1)\n")])
        assert "Requirement 7" in msg and "towards the left player" in msg
        msg = self._fails("pyblank-01-pong", [("        score['left'] = score['right'] = 0\n", "")])
        assert "Requirement 8" in msg and "scores" in msg

    def test_flappy_says_gravity_is_per_second_and_a_flap_sets(self) -> None:
        msg = self._fails("pyblank-02-flappy", [("bird['vy'] += 900 * dt", "bird['vy'] += 15")])
        assert "Requirement 2" in msg and "900" in msg and "dt" in msg
        msg = self._fails("pyblank-02-flappy", [("        bird['vy'] = -300\n", "        bird['vy'] -= 300\n")])
        assert "Requirement 3" in msg and "SET" in msg
        msg = self._fails("pyblank-02-flappy", [(_FLAPPY_TOUCHES, "    return x <= bird['x'] <= x + w and y <= bird['y'] <= y + h\n")])
        assert "Requirement 6" in msg and "circle" in msg

    def test_memory_says_seconds_not_frames_and_the_aliasing_trap(self) -> None:
        msg = self._fails("pyblank-03-memory", [
            (_MEMORY_LATER, "        pending[:] = [a, card, 48]\n"),
            ("on_frame(draw)\n", (
                "pending = []\n\n\ndef tick(dt):\n    if pending:\n        pending[2] -= 1\n"
                "        if pending[2] <= 0:\n            hide(pending[0], pending[1])\n"
                "            pending.clear()\n    draw(dt)\n\n\non_frame(tick)\n"))])
        assert "Requirement 5" in msg and "30" in msg and "after(0.8" in msg
        msg = self._fails("pyblank-03-memory", [(_MEMORY_DEAL, "cards = [Card(30, 20, 0)] * 12\n")])
        assert "Requirement 1" in msg and "12 different cards" in msg

    def test_stacker_names_the_aliasing_trap_and_the_skipped_row(self) -> None:
        msg = self._fails("pyblank-04-stacker", [("    return [[0] * COLS for _ in range(n)]", "    return [[0] * COLS] * n")])
        assert "Requirement 1" in msg and "[[0] * 10] * 20" in msg and "for _ in range(20)" in msg
        msg = self._fails("pyblank-04-stacker", [(_STACKER_CLEAR, (
            "    cleared = 0\n    for r in range(ROWS - 1, -1, -1):\n        if all(grid[r]):\n"
            "            del grid[r]\n            grid.insert(0, [0] * COLS)\n            cleared += 1\n"
            "    score += 10 * cleared\n"))])
        assert "Requirement 7" in msg and "two full rows" in msg and "not all(row)" in msg
        msg = self._fails("pyblank-04-stacker", [
            ("on_key_down, every\n", "on_key_down, every, keys\n"),
            (_STACKER_KEYS, "    if key == 'ArrowDown':\n"),
            ("on_key_down(key_down)\n", (
                "on_key_down(key_down)\n\n\ndef move_sideways(dt):\n    if state != 'playing':\n        return\n"
                "    if 'ArrowLeft' in keys and fits(piece['col'] - 1, piece['row']):\n        piece['col'] -= 1\n"
                "    if 'ArrowRight' in keys and fits(piece['col'] + 1, piece['row']):\n        piece['col'] += 1\n\n\n"
                "on_frame(move_sideways)\n"))])
        assert "Requirement 4" in msg and "on_key_down" in msg

    def test_a_missing_global_is_reported_with_its_line(self) -> None:
        # Not a "Requirement": the learner's own program crashed, and the harness says where.
        flappy = BY_ID["pyblank-02-flappy"]
        code = _apply(flappy.solution, [("    global pipes, spawn_timer, score, state\n    if state",
                                         "    global spawn_timer, score, state\n    if state")])
        got = run_py_check(code, flappy.check)
        assert not got.passed
        assert "UnboundLocalError" in got.message and "line" in got.message

    def test_a_crash_is_reported_with_its_line(self) -> None:
        s = STEPS[0]
        got = run_py_check(s.starter + "\nnope()\n", s.check)
        assert not got.passed
        assert "nope" in got.message and "line" in got.message

    def test_an_endless_loop_is_reported_not_waited_on(self) -> None:
        s = STEPS[0]
        got = run_py_check(s.starter + "\nwhile True:\n    pass\n", s.check)
        assert not got.passed
        assert "loop that never ends" in got.message


class TestTheOpenStep:
    def test_it_has_no_check_and_a_blank_solution(self) -> None:
        last = STEPS[-1]
        assert last.check == ""
        assert last.solution == last.starter
