"""Canvas: the Python Platformer steps and their checks.

Like the JavaScript Platformer (test_canvas_platformer.py), but the program is
Python and the check plays it in a child process. A check is held to three
things: the step's own solution passes, its starter (the step before,
finished) does not, and the mistakes people really make at that step fail it
too - gravity added per frame instead of per second (run at 30 frames a
second), a jump while airborne, a `|` where `&` was meant, friction as a
fraction per frame, the map's rows and columns swapped (`level[col][row]`),
a tile lookup with no guard (Python's `level[-1]` is the last row, not an
error), `int()` where floor division was needed on a negative number, a box
that counts touching as overlapping, x and y moved together so the player
sticks to walls, tunnelling through a thin tile with no cap on dt, a one-way
ledge that lets go of a standing player (`<` for `<=`) or blocks from below, a
ledge in row 0 lost to `if row:`, coyote time counted in frames, a jump that
is never cut short, a coin that counts every frame, a `global` line that is
missing, a camera that is not clamped. A check that let those through would be
checking nothing.

The player may be a dataclass or a dict; the checks work with both, and so do
these tests (`_as_dicts` rewrites every solution with a dict).
"""

from __future__ import annotations

import re

import pytest

from code_coach.canvas import STEPS as ALL_STEPS
from code_coach.canvas import check_step, run_py_check
from code_coach.canvas.content_pyplatformer import PYPLATFORMER_STEPS as STEPS

BY_ID = {s.id: s for s in STEPS}

_REGISTERED = all(s.id in {a.id for a in ALL_STEPS} for s in STEPS)


def _swap(code: str, old: str, new: str) -> str:
    assert code.count(old) >= 1, old
    return code.replace(old, new)


def _swaps(code: str, entry) -> str:
    """Apply one mistake or one other way: (old, new), a function of the code, or a list of those made together."""
    for item in entry if isinstance(entry, list) else [entry]:
        code = item(code) if callable(item) else _swap(code, *item)
    return code


def _label(entry) -> str:
    last = (entry if isinstance(entry, list) else [entry])[-1]
    if callable(last):
        return last.__name__
    old, new = last
    return (new or old)[:60]


# -- Pieces of the solutions the mistakes cut out --------------------------------

_FALL_Y = "    player.y += player.vy * dt\n"
_TILES_RANGE = "    return range(math.floor(start / TILE), math.ceil((start + size) / TILE))"
_GUARD_ROW = "    if row < 0 or row >= len(level):\n        return '.'\n"
_GUARD_COL = "    if col < 0 or col >= len(level[0]):\n        return '#'\n"
_ROWS = "    rows = tiles_covered(player.y, player.h)\n"
_UPDATE6 = "    move_x(dt)\n    move_y(dt)"
_HEAD_BUMP = "    if touches(SOLID):\n        if player.vy > 0:\n"
_RUN_FRICTION = "        slow = min(abs(player.vx), FRICTION * dt)\n        player.vx -= math.copysign(slow, player.vx)"
_ONE_WAY_TEST = "    if any(tile_at(col, row) == '=' for col in tiles_covered(player.x, player.w)):\n"
_COIN_TEST = "        if abs(c['x'] - cx) < 8 + player.w / 2 and abs(c['y'] - cy) < 8 + player.h / 2:\n"
_DRAW_COIN_SKIP = "        if c['taken']:\n            continue\n        ctx.begin_path()"
_CAMERA_LINE = "    camera_x = max(0, min(len(level[0]) * TILE - WIDTH, target))"
_COLLECT = (
    "def collect_coins():\n    global score\n    cx = player.x + player.w / 2\n    cy = player.y + player.h / 2\n"
    "    for c in coins:\n        if c['taken']:\n            continue\n"
    + _COIN_TEST + "            c['taken'] = True\n            score += 1"
)
_TOUCHES_BODY = (
    "    cols = tiles_covered(player.x, player.w)\n    rows = tiles_covered(player.y, player.h)\n"
    "    return any(tile_at(col, row) in kinds for row in rows for col in cols)"
)


def _dedent_map(code: str) -> str:
    """The same program with the map typed as a triple-quoted string, split into rows."""
    found = re.search(r"level = \[\n((?:    '.*',\n)+)\]", code)
    assert found
    rows = re.findall(r"'(.*)',", found.group(1))
    block = "level = textwrap.dedent('''\n" + "".join(f"    {r}\n" for r in rows) + "''').strip().splitlines()"
    code = code[:found.start()] + block + code[found.end():]
    return code.replace("import math\n", "import math\nimport textwrap\n", 1)


def _sentinel_minus_one(code: str) -> str:
    """one_way_row says -1 for 'none' instead of None."""
    code = code.replace("        return None\n", "        return -1\n").replace("    return None", "    return -1")
    return code.replace("if row is not None:", "if row != -1:")


#: Wrong programs, each a real mistake at that step, that the check must fail.
#: An entry is one (what to find in the solution, what to put there instead),
#: a function from code to code, or a list of those, made together.
MISTAKES: dict[str, list] = {
    "pyplat-01-gravity": [
        # Gravity per frame, not per second: right at 60 a second, wrong at 30.
        ("    player.vy += GRAVITY * dt\n", "    player.vy += 30\n"),
        # The speed moves the player a fixed step a frame.
        (_FALL_Y, "    player.y += player.vy / 60\n"),
        # on_ground set true on landing but never cleared.
        ("    player.on_ground = False\n", ""),
        # Never set true.
        ("        player.on_ground = True", "        pass"),
        # The feet are not put back on the floor.
        ("        player.y = FLOOR - player.h\n", ""),
        # The speed is not zeroed on the floor.
        ("        player.vy = 0\n        player.on_ground = True", "        player.on_ground = True"),
        # Never drawn.
        ("    ctx.fill_rect(player.x, player.y, player.w, player.h)", "    pass"),
    ],
    "pyplat-02-jump": [
        # Jump while airborne.
        ("    if player.on_ground and keys & JUMP_KEYS:\n", "    if keys & JUMP_KEYS:\n"),
        # Jumps down.
        ("        player.vy = -JUMP\n", "        player.vy = JUMP\n"),
        # | where & was meant: a set that is never empty, so it always jumps.
        ("    if player.on_ground and keys & JUMP_KEYS:\n", "    if player.on_ground and keys | JUMP_KEYS:\n"),
        # The space bar is forgotten.
        ("JUMP_KEYS = {'ArrowUp', ' '}", "JUMP_KEYS = {'ArrowUp'}"),
        # A hop that is too small, or a rocket.
        ("JUMP = 620", "JUMP = 300"),
        ("JUMP = 620", "JUMP = 900"),
    ],
    "pyplat-03-run": [
        # Friction as a fraction per frame: depends on the frame rate.
        (_RUN_FRICTION, "        player.vx *= 0.9"),
        # A fixed amount per frame.
        ("FRICTION * dt)", "FRICTION / 60)"),
        # Friction that can overshoot zero and shuffle backwards.
        ("        slow = min(abs(player.vx), FRICTION * dt)\n", "        slow = FRICTION * dt\n"),
        # Friction that speeds the player up.
        ("math.copysign(slow, player.vx)", "math.copysign(slow, -player.vx)"),
        # No top speed.
        ("    player.vx = max(-MAX_SPEED, min(MAX_SPEED, player.vx))", "    pass"),
        # Speed set, not built up.
        ("        player.vx += direction * ACCEL * dt", "        player.vx = direction * MAX_SPEED"),
        # Acceleration per frame.
        ("        player.vx += direction * ACCEL * dt", "        player.vx += direction * ACCEL / 60"),
        # Left and right the wrong way round.
        ("('ArrowRight' in keys) - ('ArrowLeft' in keys)", "('ArrowLeft' in keys) - ('ArrowRight' in keys)"),
        # x moved by a fixed step, or never.
        ("    player.x += player.vx * dt\n    fall(dt)", "    player.x += player.vx / 60\n    fall(dt)"),
        ("    player.x += player.vx * dt\n    fall(dt)", "    fall(dt)"),
    ],
    "pyplat-04-tilemap": [
        # Row and column swapped.
        ("                ctx.fill_rect(col * TILE, row * TILE, TILE, TILE)",
         "                ctx.fill_rect(row * TILE, col * TILE, TILE, TILE)"),
        # Every tile drawn, air included.
        ("            if tile == '#':", "            if tile != 'x':"),
        # A copy of the map made once: editing the map no longer edits the game.
        ("def draw_tiles():\n    ctx.fill_style = '#4a5568'\n    for row, line in enumerate(level):\n"
         "        for col, tile in enumerate(line):\n            if tile == '#':\n"
         "                ctx.fill_rect(col * TILE, row * TILE, TILE, TILE)",
         "WALLS = [(c, r) for r, line in enumerate(level) for c, t in enumerate(line) if t == '#']\n\n\n"
         "def draw_tiles():\n    ctx.fill_style = '#4a5568'\n    for col, row in WALLS:\n"
         "        ctx.fill_rect(col * TILE, row * TILE, TILE, TILE)"),
        # The wrong tile size.
        ("TILE = 32\n", "TILE = 16\n"),
    ],
    "pyplat-05-floor": [
        # Touching counts as overlapping: hovers beside a platform's edge.
        (_TILES_RANGE, "    return range(math.floor(start / TILE), math.floor((start + size) / TILE) + 1)"),
        # A head bump treated as a landing.
        (_HEAD_BUMP, "    if touches(SOLID):\n        if True:\n"),
        # Row and column swapped: level[col][row].
        ("    return level[row][col]", "    return level[col][row]"),
        # No guard above the map: level[-1] is the last row, so the sky is a floor.
        (_GUARD_ROW, "    if row >= len(level):\n        return '.'\n"),
        # No guard below the map: IndexError.
        (_GUARD_ROW, ""),
        # all() where any() was meant: only a box wholly inside solid tiles is touching.
        ("    return any(tile_at(col, row) in kinds", "    return all(tile_at(col, row) in kinds"),
        # Feet put in the tile, not on it.
        ("            player.y = row * TILE - player.h\n            player.on_ground = True",
         "            player.y = row * TILE\n            player.on_ground = True"),
        # Standing never noticed.
        ("            player.y = row * TILE - player.h\n            player.on_ground = True\n",
         "            player.y = row * TILE - player.h\n"),
        # The head put in the tile, not under it.
        ("            player.y = (row + 1) * TILE\n", "            player.y = row * TILE\n"),
        # Speed kept after a landing.
        ("        player.vy = 0", "        pass"),
    ],
    "pyplat-06-walls": [
        # Standing exactly on a tile counts as touching it from the side.
        (_ROWS,
         "    rows = range(math.floor(player.y / TILE), math.floor((player.y + player.h) / TILE) + 1)\n"),
        # Both axes moved, then y settled first: sticks to walls.
        (_UPDATE6, "    player.x += player.vx * dt\n    player.y += player.vy * dt\n    move_y(0)\n    move_x(0)"),
        # int() cuts toward zero: a box half off the left edge is in column 0, not -1.
        (_TILES_RANGE, "    return range(int(start / TILE), math.ceil((start + size) / TILE))"),
        ("    return int(x // TILE), int(y // TILE)", "    return int(x / TILE), int(y / TILE)"),
        # No guard on the columns: level[row][-1] is the far end of the map.
        (_GUARD_COL, ""),
        (_GUARD_COL, "    if col >= len(level[0]):\n        return '#'\n"),
        ("    if col < 0 or col >= len(level[0]):\n        return '#'\n",
         "    if col < 0:\n        return '#'\n"),
        # The edge not put flush.
        ("            player.x = col * TILE - player.w\n", "            player.x = col * TILE\n"),
        ("            player.x = (col + 1) * TILE\n", "            player.x = col * TILE\n"),
        # Only walls on the right are handled.
        ("        else:\n            col, _ = tile_of(player.x, player.y)\n            player.x = (col + 1) * TILE\n", ""),
    ],
    "pyplat-07-fast": [
        # No cap on a long frame: tunnels through thin tiles.
        ("    dt = min(dt, MAX_DT)\n", ""),
        # A cap that is too generous.
        ("MAX_DT = 1 / 30", "MAX_DT = 0.25"),
        # No terminal velocity.
        ("min(player.vy + GRAVITY * dt, MAX_FALL)", "player.vy + GRAVITY * dt"),
        # A terminal velocity that is no cap, or a crawl.
        ("MAX_FALL = 900", "MAX_FALL = 2000"),
        ("MAX_FALL = 900", "MAX_FALL = 300"),
    ],
    "pyplat-08-oneway": [
        # < for <=: lets go of a player who is already standing on it.
        ("    if prev_bottom > row * TILE:", "    if prev_bottom >= row * TILE:"),
        # Grabs a player whose feet were already below the top.
        ("    if prev_bottom > row * TILE:\n        return None\n", ""),
        # Anything that is not air is a wall: the ledge blocks from below.
        ("SOLID = {'#'}", "SOLID = {'#', '='}"),
        # `if row:` is false for row 0.
        ("        if row is not None:\n", "        if row:\n"),
        # Only the left-hand tile of the feet is looked at.
        (_ONE_WAY_TEST, "    if tile_at(int(player.x // TILE), row) == '=':\n"),
    ],
    "pyplat-09-feel": [
        # The coyote time is never used up: a double jump.
        ("        player.coyote = 0\n", ""),
        # A window so long it is a free air jump, or so short nobody can use it.
        ("COYOTE = 0.1", "COYOTE = 0.5"),
        ("COYOTE = 0.1", "COYOTE = 0.01"),
        # No coyote time at all.
        ("    if jump_held and player.coyote > 0:", "    if jump_held and player.on_ground:"),
        # The jump is always cut, held or not.
        ("    if not jump_held and player.vy < -JUMP_CUT:", "    if player.vy < -JUMP_CUT:"),
        # The jump is never cut.
        ("    if not jump_held and player.vy < -JUMP_CUT:\n        player.vy = -JUMP_CUT", "    pass"),
        # Coyote time counted in frames: right at 60 a second, twice as long at 30.
        [("COYOTE = 0.1", "COYOTE = 6"), ("        player.coyote -= dt\n", "        player.coyote -= 1\n")],
    ],
    "pyplat-10-coins": [
        # A coin is never marked taken: counts every frame.
        ("            c['taken'] = True\n", ""),
        # Collected without touching.
        (_COIN_TEST, "        if True:\n"),
        # Only one axis is tested.
        (_COIN_TEST, "        if abs(c['x'] - cx) < 8 + player.w / 2:\n"),
        (_COIN_TEST, "        if abs(c['y'] - cy) < 8 + player.h / 2:\n"),
        # Taken coins still drawn.
        (_DRAW_COIN_SKIP, "        ctx.begin_path()"),
        # score += 1 in a function with no `global score`: UnboundLocalError.
        ("    global score\n", ""),
        # The score is never shown.
        ("    ctx.fill_text(f'Coins: {score}', 10, 20)", "    pass"),
    ],
    "pyplat-11-goal": [
        # Respawns while standing on the floor.
        ("    if player.y > HEIGHT + 100:", "    if player.y > 100:"),
        # Comes back still falling.
        ("    player.vx = player.vy = 0\n", "    player.vx = 0\n"),
        # Comes back in the wrong place.
        ("    player.x, player.y = START\n", "    player.x, player.y = 0, 0\n"),
        # Keeps playing after winning.
        ("    if state != 'playing':\n        return\n", ""),
        # `state = 'won'` with no `global state`: a quiet local, never won.
        ("    global state\n", ""),
        # Won without touching the flag.
        ("    if touches({'F'}):", "    if True:"),
        # No message.
        ("        ctx.fill_text('You made it!', 140, 160)", "        pass"),
    ],
    "pyplat-12-camera": [
        # Scrolls the wrong way.
        ("    ctx.translate(-camera_x, 0)\n", "    ctx.translate(camera_x, 0)\n"),
        # Not clamped at the left end.
        (_CAMERA_LINE, "    camera_x = min(len(level[0]) * TILE - WIDTH, target)"),
        # Not clamped at the right end.
        (_CAMERA_LINE, "    camera_x = max(0, target)"),
        # Aims the player's corner, not its centre.
        ("    target = player.x + player.w / 2 - WIDTH / 2", "    target = player.x - WIDTH / 2"),
        # The score drawn inside the scrolling world.
        ("    ctx.restore()\n", ""),
        # `camera_x = ...` with no `global camera_x`: a quiet local.
        ("    global camera_x\n", ""),
        # The tiles are drawn before the shift.
        ("    ctx.translate(-camera_x, 0)\n    draw_tiles()\n    draw_coins()\n",
         "    draw_tiles()\n    ctx.translate(-camera_x, 0)\n    draw_coins()\n"),
        # The camera is never updated.
        ("\n    update_camera()", ""),
    ],
}

#: Right programs written another way, which the check must still pass. Each
#: way is one (old, new), a function of the code, or a list of those made together.
OTHER_WAYS: dict[str, list] = {
    "pyplat-01-gravity": [
        ("    if player.y + player.h >= FLOOR:", "    if player.y + player.h > FLOOR:"),
        ("    if player.y + player.h >= FLOOR:", "    if player.y >= FLOOR - player.h:"),
    ],
    "pyplat-02-jump": [
        # Another way to say "either key".
        ("    if player.on_ground and keys & JUMP_KEYS:\n",
         "    if player.on_ground and (keys & JUMP_KEYS):\n"),
        ("    if player.on_ground and keys & JUMP_KEYS:\n",
         "    if player.on_ground and any(k in keys for k in JUMP_KEYS):\n"),
        ("    if player.on_ground and keys & JUMP_KEYS:\n",
         "    if player.on_ground and not keys.isdisjoint(JUMP_KEYS):\n"),
        ("    if player.on_ground and keys & JUMP_KEYS:\n",
         "    if player.on_ground and ('ArrowUp' in keys or ' ' in keys):\n"),
        # fall() already says "not on the ground" every frame.
        ("        player.vy = -JUMP\n        player.on_ground = False\n", "        player.vy = -JUMP\n"),
    ],
    "pyplat-03-run": [
        # Friction written as an if / elif.
        (_RUN_FRICTION,
         "        if player.vx > 0:\n            player.vx = max(0, player.vx - FRICTION * dt)\n"
         "        else:\n            player.vx = min(0, player.vx + FRICTION * dt)"),
        # The direction with ifs.
        ("    direction = ('ArrowRight' in keys) - ('ArrowLeft' in keys)\n",
         "    direction = 0\n    if 'ArrowRight' in keys:\n        direction += 1\n    if 'ArrowLeft' in keys:\n"
         "        direction -= 1\n"),
        ("    player.vx = max(-MAX_SPEED, min(MAX_SPEED, player.vx))",
         "    player.vx = min(MAX_SPEED, max(-MAX_SPEED, player.vx))"),
        ("ACCEL = 1600", "ACCEL = 1500"),
    ],
    "pyplat-04-tilemap": [
        # The map typed as one triple-quoted string.
        _dedent_map,
        # range(len(...)) loops and indexing.
        ("    for row, line in enumerate(level):\n        for col, tile in enumerate(line):\n            if tile == '#':\n",
         "    for row in range(len(level)):\n        for col in range(len(level[row])):\n"
         "            if level[row][col] == '#':\n"),
    ],
    "pyplat-05-floor": [
        # A tiny shrink of the box instead of ceil(...).
        (_TILES_RANGE,
         "    return range(math.floor(start / TILE), math.floor((start + size - 0.001) / TILE) + 1)"),
        # Floor division all the way.
        (_TILES_RANGE, "    return range(int(start // TILE), int((start + size - 1e-9) // TILE) + 1)"),
        # divmod for the tile.
        ("    return int(x // TILE), int(y // TILE)",
         "    return int(divmod(x, TILE)[0]), int(divmod(y, TILE)[0])"),
        # Another way to write the guards.
        ("    if col < 0 or col >= len(level[0]):", "    if not 0 <= col < len(level[0]):"),
        ("SOLID = {'#'}", "SOLID = '#'"),
        # Loops instead of any().
        (_TOUCHES_BODY,
         "    cols = tiles_covered(player.x, player.w)\n    rows = tiles_covered(player.y, player.h)\n"
         "    for row in rows:\n        for col in cols:\n            if tile_at(col, row) in kinds:\n"
         "                return True\n    return False"),
        # A set comprehension of the tiles under the box.
        (_TOUCHES_BODY,
         "    cols = tiles_covered(player.x, player.w)\n    rows = tiles_covered(player.y, player.h)\n"
         "    under = {tile_at(col, row) for row in rows for col in cols}\n    return bool(under & set(kinds))"),
    ],
    "pyplat-06-walls": [
        ("            col, _ = tile_of(player.x + player.w, player.y)\n            player.x = col * TILE - player.w",
         "            player.x = (player.x + player.w) // TILE * TILE - player.w"),
        ("            col, _ = tile_of(player.x, player.y)\n            player.x = (col + 1) * TILE",
         "            player.x = (player.x // TILE + 1) * TILE"),
    ],
    "pyplat-07-fast": [
        ("MAX_DT = 1 / 30", "MAX_DT = 1 / 20"),
        ("    dt = min(dt, MAX_DT)\n    update(dt)\n", "    update(min(dt, MAX_DT))\n"),
        ("MAX_FALL = 900", "MAX_FALL = 880"),
    ],
    "pyplat-08-oneway": [
        # -1 as the answer for "no ledge".
        _sentinel_minus_one,
    ],
    "pyplat-09-feel": [
        ("COYOTE = 0.1", "COYOTE = 0.12"),
        ("JUMP_CUT = 200", "JUMP_CUT = 240"),
        ("    jump_held = bool(keys & JUMP_KEYS)\n", "    jump_held = any(k in keys for k in JUMP_KEYS)\n"),
    ],
    "pyplat-10-coins": [
        # A circle test instead of the box.
        (_COIN_TEST, "        if math.hypot(c['x'] - cx, c['y'] - cy) < 22:\n"),
        # Coins removed from the list instead of flagged.
        [(_COLLECT,
          "def collect_coins():\n    global coins, score\n    cx = player.x + player.w / 2\n"
          "    cy = player.y + player.h / 2\n"
          "    hit = [c for c in coins if abs(c['x'] - cx) < 8 + player.w / 2 and abs(c['y'] - cy) < 8 + player.h / 2]\n"
          "    score += len(hit)\n    coins = [c for c in coins if c not in hit]"),
         (_DRAW_COIN_SKIP, "        ctx.begin_path()")],
        # Coins as dataclasses.
        [("coins = [\n    {'x': col * TILE + TILE / 2, 'y': row * TILE + TILE / 2, 'taken': False}\n",
          "@dataclass\nclass Coin:\n    x: float\n    y: float\n    taken: bool = False\n\n\n"
          "coins = [\n    Coin(col * TILE + TILE / 2, row * TILE + TILE / 2)\n"),
         ("        if c['taken']:\n            continue\n" + _COIN_TEST + "            c['taken'] = True",
          "        if c.taken:\n            continue\n"
          "        if abs(c.x - cx) < 8 + player.w / 2 and abs(c.y - cy) < 8 + player.h / 2:\n            c.taken = True"),
         ("        if c['taken']:\n            continue\n        ctx.begin_path()\n        ctx.arc(c['x'], c['y'], 8, 0, math.tau)",
          "        if c.taken:\n            continue\n        ctx.begin_path()\n        ctx.arc(c.x, c.y, 8, 0, math.tau)")],
    ],
    "pyplat-11-goal": [
        # START as a dict.
        [("START = (64, 258)", "START = {'x': 64, 'y': 258}"),
         ("    player.x, player.y = START\n", "    player.x, player.y = START['x'], START['y']\n")],
        ("    if player.y > HEIGHT + 100:", "    if player.y > len(level) * TILE:"),
        ("    player.vx = player.vy = 0\n", "    player.vx = 0\n    player.vy = 0\n"),
    ],
    "pyplat-12-camera": [
        # A camera dict instead of a number.
        [("camera_x = 0\n", "camera = {'x': 0}\n"),
         ("    global camera_x\n", ""),
         (_CAMERA_LINE, "    camera['x'] = max(0, min(len(level[0]) * TILE - WIDTH, target))"),
         ("ctx.translate(-camera_x, 0)", "ctx.translate(-camera['x'], 0)")],
        # The clamp written out.
        (_CAMERA_LINE,
         "    camera_x = target\n    camera_x = min(camera_x, len(level[0]) * TILE - WIDTH)\n    camera_x = max(camera_x, 0)"),
    ],
}


def _as_dicts(code: str) -> str:
    """The same program with the player a dict, not a dataclass: player['x'] for player.x."""
    found = re.search(r"@dataclass\nclass Player:\n((?:    .+\n?)+)", code)
    assert found
    fields = re.findall(r"^    (\w+): \w+ = (.+)$", found.group(1), re.M)
    literal = "player = {" + ", ".join(f"'{name}': {default}" for name, default in fields) + "}"
    made = code[:found.start()] + code[found.end():]
    made = made.replace("player = Player()", literal)
    made = re.sub(r"from dataclasses import dataclass\n", "", made)
    made = re.sub(r"\bplayer\.(\w+)", r"player['\1']", made)
    assert made != code and "@dataclass" not in made and "Player" not in made
    return made


class TestShape:
    def test_ids_unique_numbered_and_titled(self) -> None:
        ids = [s.id for s in STEPS]
        assert len(ids) == len(set(ids))
        assert len(STEPS) == 13
        for n, s in enumerate(STEPS, 1):
            assert re.fullmatch(rf"pyplat-{n:02d}-[a-z-]+", s.id), s.id
            assert s.title
            assert len(s.teaches) > 120, s.id
            assert s.goal.endswith("."), s.id

    def test_they_are_python_steps_on_their_own_track(self) -> None:
        assert {s.track for s in STEPS} == {"Platformer (Python)"}
        assert {s.language for s in STEPS} == {"python"}
        assert all(s.kind == "canvas" for s in STEPS)

    @pytest.mark.skipif(not _REGISTERED, reason="PYPLATFORMER_STEPS is not in canvas/__init__.py STEPS yet")
    def test_they_are_registered_as_one_block(self) -> None:
        ids = [s.id for s in ALL_STEPS]
        first = ids.index(STEPS[0].id)
        assert ids[first:first + len(STEPS)] == [s.id for s in STEPS]
        order = [s.track for s in ALL_STEPS]
        for before in ("Dodge (Python)", "Platformer"):
            assert order.index(before) < order.index("Platformer (Python)")

    def test_each_step_starts_where_the_last_one_finished(self) -> None:
        for before, after in zip(STEPS, STEPS[1:]):
            assert after.starter == before.solution, after.id

    def test_only_the_last_step_is_open(self) -> None:
        assert [s.id for s in STEPS if not s.check] == [STEPS[-1].id]

    def test_every_program_is_python_that_compiles_and_uses_the_library(self) -> None:
        for s in STEPS:
            for code in (s.starter, s.solution):
                compile(code, s.id, "exec")
                assert "from canvas import" in code, s.id
                assert "ctx.fillStyle" not in code and "requestAnimationFrame" not in code
                assert "\r" not in code and not code.endswith("\n\n")

    def test_every_mistake_and_other_way_names_a_real_step(self) -> None:
        for step_id in list(MISTAKES) + list(OTHER_WAYS):
            assert step_id in BY_ID, step_id

    def test_every_checked_step_has_a_real_mistake(self) -> None:
        for s in STEPS:
            if s.check:
                assert MISTAKES.get(s.id), f"{s.id} has no mistake the check is held against"

    def test_the_hints_are_written(self) -> None:
        for s in STEPS:
            if s.check:
                assert s.hint, s.id

    def test_the_map_is_a_rectangle_of_known_tiles(self) -> None:
        rows = re.findall(r"^    '([^']*)',$", BY_ID["pyplat-04-tilemap"].solution, re.M)
        assert len(rows) == 10
        assert {len(r) for r in rows} == {30}
        assert set("".join(rows)) <= set("#.=oF")
        # The player starts in open air over the floor, and the flag is reachable.
        assert rows[8][2] == "." and rows[9][2] == "#"
        assert "F" in "".join(rows) and "o" in "".join(rows)

    def test_the_goals_name_what_the_checks_read(self) -> None:
        names = {
            "pyplat-01-gravity": ["GRAVITY", "FLOOR", "Player", "player", "on_ground", "fall", "dict"],
            "pyplat-02-jump": ["JUMP", "JUMP_KEYS", "keys & JUMP_KEYS", "jump", "on_ground"],
            "pyplat-03-run": ["ACCEL", "FRICTION", "MAX_SPEED", "run", "vx"],
            "pyplat-04-tilemap": ["TILE", "level", "list of 10 strings", "replaces rows of level"],
            "pyplat-05-floor": ["SOLID", "tile_of", "tile_at", "tiles_covered", "touches", "move_y", "level"],
            "pyplat-06-walls": ["move_x", "move_y", "level", "player"],
            "pyplat-07-fast": ["MAX_DT", "MAX_FALL", "dt", "move_y"],
            "pyplat-08-oneway": ["'='", "one_way_row", "None", "SOLID", "move_y"],
            "pyplat-09-feel": ["COYOTE", "JUMP_CUT", "coyote", "jump(dt)"],
            "pyplat-10-coins": ["coins", "score", "collect_coins", "global", "taken"],
            "pyplat-11-goal": ["START", "state", "'won'", "global", "respawn", "HEIGHT + 100"],
            "pyplat-12-camera": ["camera_x", "update_camera", "global", "ctx.restore()", "-camera_x"],
        }
        for step_id, wanted in names.items():
            for name in wanted:
                assert name in BY_ID[step_id].goal, f"{step_id}: the goal does not say {name}"

    def test_the_python_way_is_what_gets_taught(self) -> None:
        text = " ".join(s.teaches for s in STEPS)
        for word in ("@dataclass", "enumerate", "divmod", " // ", "math.floor", "math.ceil", "range(", "any()",
                     "all()", "SOLID", "textwrap.dedent", "splitlines", "math.copysign", "abs(", "min(", "max(",
                     "f'Coins: {score}'", "global", "UnboundLocalError", "level[-1]", "if row:", "int(",
                     "tuple", "unpacks", "keys & JUMP_KEYS", "set", "level[row][col]", "is not None",
                     "a bool is a number", "list comprehension", "START = (64, 258)",
                     "player.vx = player.vy = 0", "generator"):
            assert word in text, word


class TestChecks:
    def test_every_solution_passes_its_check(self) -> None:
        for s in STEPS:
            if not s.check:
                continue
            got = run_py_check(s.solution, s.check)
            assert got.passed, f"{s.id}: {got.message}"

    def test_every_starter_fails_its_check(self) -> None:
        for s in STEPS:
            if not s.check:
                continue
            got = run_py_check(s.starter, s.check)
            assert not got.passed, s.id
            assert got.message, s.id

    def test_real_mistakes_fail(self) -> None:
        for step_id, entries in MISTAKES.items():
            s = BY_ID[step_id]
            for entry in entries:
                got = run_py_check(_swaps(s.solution, entry), s.check)
                assert not got.passed, f"{step_id}: the check let this mistake through: {_label(entry)!r}"
                assert got.message, step_id

    def test_other_right_answers_pass(self) -> None:
        for step_id, entries in OTHER_WAYS.items():
            s = BY_ID[step_id]
            for entry in entries:
                got = run_py_check(_swaps(s.solution, entry), s.check)
                assert got.passed, f"{step_id}: {_label(entry)!r}: {got.message}"

    def test_dicts_pass_wherever_the_player_is_a_dataclass(self) -> None:
        for s in STEPS:
            if not s.check:
                continue
            got = run_py_check(_as_dicts(s.solution), s.check)
            assert got.passed, f"{s.id}: {got.message}"

    def test_dict_mistakes_fail_too(self) -> None:
        # The dict form of a few mistakes that hang on a field's name: the check reads both forms alike.
        for step_id, entry in (
            ("pyplat-01-gravity", ("    player.vy += GRAVITY * dt\n", "    player.vy += 30\n")),
            ("pyplat-02-jump", ("    if player.on_ground and keys & JUMP_KEYS:\n", "    if keys & JUMP_KEYS:\n")),
            ("pyplat-06-walls", (_UPDATE6, "    player.x += player.vx * dt\n    player.y += player.vy * dt\n"
                                             "    move_y(0)\n    move_x(0)")),
            ("pyplat-08-oneway", ("    if prev_bottom > row * TILE:", "    if prev_bottom >= row * TILE:")),
            ("pyplat-09-feel", ("        player.coyote = 0\n", "")),
        ):
            s = BY_ID[step_id]
            got = run_py_check(_as_dicts(_swaps(s.solution, entry)), s.check)
            assert not got.passed, step_id

    def test_the_checks_say_what_to_fix_not_just_that_it_failed(self) -> None:
        gravity = BY_ID["pyplat-01-gravity"]
        got = run_py_check(_swap(gravity.solution, "    player.vy += GRAVITY * dt\n", "    player.vy += 30\n"),
                           gravity.check)
        assert "30 frames a second" in got.message

        jump = BY_ID["pyplat-02-jump"]
        got = run_py_check(_swap(jump.solution, "    if player.on_ground and keys & JUMP_KEYS:\n",
                                 "    if keys & JUMP_KEYS:\n"), jump.check)
        assert "on_ground" in got.message and "mid-air" in got.message

        run = BY_ID["pyplat-03-run"]
        got = run_py_check(_swap(run.solution, _RUN_FRICTION, "        player.vx *= 0.9"), run.check)
        assert "frame rate" in got.message

        floor = BY_ID["pyplat-05-floor"]
        got = run_py_check(_swap(floor.solution, _GUARD_ROW, "    if row >= len(level):\n        return '.'\n"),
                           floor.check)
        assert "level[-1]" in got.message

        walls = BY_ID["pyplat-06-walls"]
        got = run_py_check(_swap(walls.solution, _TILES_RANGE,
                                 "    return range(int(start / TILE), math.ceil((start + size) / TILE))"), walls.check)
        assert "int()" in got.message

        fast = BY_ID["pyplat-07-fast"]
        got = run_py_check(_swap(fast.solution, "    dt = min(dt, MAX_DT)\n", ""), fast.check)
        assert "Cap dt" in got.message

        oneway = BY_ID["pyplat-08-oneway"]
        got = run_py_check(_swap(oneway.solution, "        if row is not None:\n", "        if row:\n"), oneway.check)
        assert "is not None" in got.message

        feel = BY_ID["pyplat-09-feel"]
        got = run_py_check(_swaps(feel.solution, [("COYOTE = 0.1", "COYOTE = 6"),
                                                  ("        player.coyote -= dt\n", "        player.coyote -= 1\n")]),
                           feel.check)
        assert "not in frames" in got.message

        coins = BY_ID["pyplat-10-coins"]
        got = run_py_check(_swap(coins.solution, "    global score\n", ""), coins.check)
        assert "UnboundLocalError" in got.message and "line" in got.message

        goal = BY_ID["pyplat-11-goal"]
        got = run_py_check(_swap(goal.solution, "    global state\n", ""), goal.check)
        assert "global state" in got.message

        camera = BY_ID["pyplat-12-camera"]
        got = run_py_check(_swap(camera.solution, "    ctx.restore()\n", ""), camera.check)
        assert "ctx.restore()" in got.message

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

    def test_a_level_the_check_replaces_is_read_every_frame(self) -> None:
        # The program must read the global `level`, not a copy: a copy would make step 5's check pass the wrong way.
        s = BY_ID["pyplat-05-floor"]
        copy = _swap(s.solution, "    return level[row][col]", "    return WORLD[row][col]")
        copy = _swap(copy, "player = Player()", "player = Player()\nWORLD = list(level)")
        got = run_py_check(copy, s.check)
        assert not got.passed

    @pytest.mark.skipif(not _REGISTERED, reason="PYPLATFORMER_STEPS is not in canvas/__init__.py STEPS yet")
    def test_the_open_step_always_passes(self) -> None:
        got = check_step(STEPS[-1].id, "")
        assert got is not None and got.passed

    @pytest.mark.skipif(not _REGISTERED, reason="PYPLATFORMER_STEPS is not in canvas/__init__.py STEPS yet")
    def test_check_step_runs_a_python_step_through_the_python_harness(self) -> None:
        s = STEPS[4]
        assert check_step(s.id, s.solution).passed
        assert not check_step(s.id, s.starter).passed
