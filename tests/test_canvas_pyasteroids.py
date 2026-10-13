"""Canvas: the Python Asteroids steps and their checks.

Like the JavaScript Asteroids (test_canvas_asteroids.py), but the program is
Python and the check plays it in a child process. A check is held to three
things: the step's own solution passes, its starter (the step before,
finished) does not, and the mistakes people really make at that step fail it
too - turning by degrees (or per frame), thrust added to the position instead
of the velocity, sin for x and cos for y, friction as a number per frame (or a
fixed amount taken away), a wrap that only knows about some of the edges (or
has no margin), bullets that never expire, a cooldown or a protection counted
in frames, removing from a list while a `for` walks it, a square collision
test (or squared distance against unsquared radii), a rock that splits
without being removed (or into one rock twice), lives lost on every frame of
the invulnerability, a `global` line that is missing a name. A check that let
those through would be checking nothing.

Ship, bullets and rocks may be dataclasses or dicts; the checks work with
both, and so do these tests (`_as_dicts` rewrites every solution with dicts).
"""

from __future__ import annotations

import re

import pytest

from code_coach.canvas import STEPS as ALL_STEPS
from code_coach.canvas import check_step, run_py_check
from code_coach.canvas.content_pyasteroids import PYASTEROIDS_STEPS as STEPS

BY_ID = {s.id: s for s in STEPS}

_REGISTERED = all(s.id in {a.id for a in ALL_STEPS} for s in STEPS)


def _swap(code: str, old: str, new: str) -> str:
    assert code.count(old) >= 1, old
    return code.replace(old, new)


def _swaps(code: str, entry) -> str:
    """Apply one mistake or one other way: a single (old, new), or a list of them made together."""
    for old, new in (entry if isinstance(entry, list) else [entry]):
        code = _swap(code, old, new)
    return code


def _label(entry) -> str:
    old, new = (entry if isinstance(entry, list) else [entry])[-1]
    return (new or old)[:60]


# -- Pieces of the solutions the mistakes cut out --------------------------------

_THRUST = (
    "        ship.vx += math.cos(ship.angle) * THRUST * dt\n"
    "        ship.vy += math.sin(ship.angle) * THRUST * dt\n"
)
_DRAG = "    ship.vx *= damp\n    ship.vy *= damp\n"
_WRAP_BODY = "    o.x = (o.x + o.r) % (WIDTH + 2 * o.r) - o.r\n    o.y = (o.y + o.r) % (HEIGHT + 2 * o.r) - o.r"
_IF_WRAP = (
    "    if o.x < -o.r:\n        o.x = WIDTH + o.r\n    elif o.x > WIDTH + o.r:\n        o.x = -o.r\n"
    "    if o.y < -o.r:\n        o.y = HEIGHT + o.r\n    elif o.y > HEIGHT + o.r:\n        o.y = -o.r"
)
_FIRE_VEL = "        ship.vx + c * BULLET_SPEED,\n        ship.vy + s * BULLET_SPEED,\n"
_FIRE_NOSE = "        ship.x + c * ship.r,\n        ship.y + s * ship.r,\n"
_MOVE_BULLETS6 = (
    "def move_bullets(dt):\n    global bullets\n    for b in bullets:\n        b.x += b.vx * dt\n"
    "        b.y += b.vy * dt\n        b.life -= dt\n        wrap(b)\n"
    "    bullets = [b for b in bullets if b.life > 0]"
)
_CULL = "    bullets = [b for b in bullets if b.life > 0]\n"
_SPAWN = (
    "def spawn_rocks(n):\n    for _ in range(n):\n        while True:\n"
    "            x = random.uniform(0, WIDTH)\n            y = random.uniform(0, HEIGHT)\n"
    "            if math.hypot(x - ship.x, y - ship.y) >= 120:\n                break\n"
    "        rocks.append(make_rock(x, y, random.choice((2, 3))))"
)
_OVERLAP = "    return math.hypot(a.x - b.x, a.y - b.y) < a.r + b.r"
_HIT8 = (
    "def hit_rocks():\n    global bullets, rocks, score\n    live = list(rocks)\n    for b in bullets:\n"
    "        for rk in live:\n            if overlap(b, rk):\n                score += POINTS[rk.size]\n"
    "                live.remove(rk)\n                b.life = 0\n                break\n"
    "    rocks = live\n    bullets = [b for b in bullets if b.life > 0]"
)
_BREAK_ROCK = "    return [make_rock(rk.x, rk.y, rk.size - 1) for _ in range(2)]"
_SQUARE = "    return abs(a.x - b.x) < a.r + b.r and abs(a.y - b.y) < a.r + b.r"
_BLINK = "    if ship.invuln > 0 and int(ship.invuln * 10) % 2 == 1:\n        return\n"
_HIT_SHIP = "    if ship.invuln <= 0 and any(overlap(ship, rk) for rk in rocks):\n"
_GLOBAL_RESET = "    global bullets, rocks, cooldown, score, lives, state\n"

#: Wrong programs, each a real mistake at that step, that the check must fail.
#: An entry is one (what to find in the solution, what to put there instead),
#: or a list of those, made together.
MISTAKES: dict[str, list] = {
    "pyast-01-turn": [
        # Degrees where radians are needed.
        ("TURN = 4", "TURN = 230"),
        ("    ship.angle += turn * TURN * dt", "    ship.angle += math.radians(turn * TURN * dt)"),
        ("    ctx.rotate(ship.angle)\n", "    ctx.rotate(math.degrees(ship.angle))\n"),
        # A turn per frame: right at 60 a second, wrong at 30.
        ("    ship.angle += turn * TURN * dt", "    ship.angle += turn * 0.07"),
        # Left and right the wrong way round.
        ("turn = ('ArrowRight' in keys) - ('ArrowLeft' in keys)", "turn = ('ArrowLeft' in keys) - ('ArrowRight' in keys)"),
        # Drawn without turning, or about the corner of the canvas.
        ("    ctx.rotate(ship.angle)\n", ""),
        ("    ctx.translate(ship.x, ship.y)\n", ""),
        # The nose not along +x.
        ("    ctx.move_to(ship.r, 0)\n", "    ctx.move_to(0, -ship.r)\n"),
        # Starts pointing right, not up.
        ("ship = Ship(240, 160)", "ship = Ship(240, 160, 0)"),
        # Never turned.
        ("    turn_ship(dt)\n", "    pass\n"),
    ],
    "pyast-02-thrust": [
        # Thrust moves the ship directly: no glide, no velocity.
        (_THRUST,
         "        ship.x += math.cos(ship.angle) * THRUST * dt\n        ship.y += math.sin(ship.angle) * THRUST * dt\n"),
        # Sin for x and cos for y.
        (_THRUST,
         "        ship.vx += math.sin(ship.angle) * THRUST * dt\n        ship.vy += math.cos(ship.angle) * THRUST * dt\n"),
        # Thrust per frame, not per second.
        (_THRUST,
         "        ship.vx += math.cos(ship.angle) * THRUST / 60\n        ship.vy += math.sin(ship.angle) * THRUST / 60\n"),
        # Always thrusting.
        ("    if 'ArrowUp' in keys:\n", "    if True:\n"),
        # Velocity never moves the ship.
        ("    ship.x += ship.vx * dt\n    ship.y += ship.vy * dt", "    pass"),
        # Only the x part moves.
        ("    ship.y += ship.vy * dt", "    pass"),
    ],
    "pyast-03-friction": [
        # A fraction per frame: depends on the frame rate.
        ("    damp = DRAG ** dt\n", "    damp = 0.99\n"),
        ("    damp = DRAG ** dt\n", "    damp = DRAG ** (1 / 60)\n"),
        # Only x is slowed: the ship's direction drifts.
        ("    ship.vy *= damp\n", ""),
        # A fixed amount taken away, not a fraction.
        (_DRAG,
         "    sp = math.hypot(ship.vx, ship.vy)\n    k = max(0, sp - 40 * dt) / (sp or 1)\n"
         "    ship.vx *= k\n    ship.vy *= k\n"),
        # No friction at all.
        (_DRAG, ""),
    ],
    "pyast-04-wrap": [
        # A single if per axis: only the right and bottom edges.
        (_WRAP_BODY,
         "    if o.x > WIDTH + o.r:\n        o.x = -o.r\n    if o.y > HEIGHT + o.r:\n        o.y = -o.r"),
        # Only the x axis.
        (_WRAP_BODY, _IF_WRAP.split("    if o.y")[0].rstrip("\n")),
        # Modulo with no margin: the ship pops out while half of it is still on screen.
        (_WRAP_BODY, "    o.x %= WIDTH\n    o.y %= HEIGHT"),
        # An off-by-one margin: the stage is 2 * r wider, not r.
        (_WRAP_BODY,
         "    o.x = (o.x + o.r) % (WIDTH + o.r) - o.r\n    o.y = (o.y + o.r) % (HEIGHT + o.r) - o.r"),
        # The margin the wrong way round.
        (_WRAP_BODY,
         "    if o.x < o.r:\n        o.x = WIDTH - o.r\n    elif o.x > WIDTH - o.r:\n        o.x = o.r\n"
         "    if o.y < o.r:\n        o.y = HEIGHT - o.r\n    elif o.y > HEIGHT - o.r:\n        o.y = o.r"),
        # Sent to the wrong place.
        (_WRAP_BODY, _IF_WRAP.replace("        o.x = -o.r\n", "        o.x = WIDTH\n")),
        # Never called.
        ("\n    wrap(ship)", ""),
    ],
    "pyast-05-bullets": [
        # Sin for x and cos for y.
        (_FIRE_VEL, "        ship.vx + s * BULLET_SPEED,\n        ship.vy + c * BULLET_SPEED,\n"),
        # The ship's own velocity is dropped.
        (_FIRE_VEL, "        c * BULLET_SPEED,\n        s * BULLET_SPEED,\n"),
        # Born in the corner, not at the nose.
        (_FIRE_NOSE, "        0,\n        0,\n"),
        # Bullets leave the screen for good.
        ("        wrap(b)\n", ""),
        # Moved by a fixed step per frame.
        ("        b.x += b.vx * dt", "        b.x += b.vx / 60"),
        # Never drawn.
        ("        ctx.arc(b.x, b.y, b.r, 0, math.tau)\n", ""),
        # Fires twice.
        ("    if key == ' ':\n        fire()", "    if key == ' ':\n        fire()\n        fire()"),
    ],
    "pyast-06-gun": [
        # Bullets never expire.
        (_CULL, ""),
        # Life counted in frames.
        ("        b.life -= dt", "        b.life -= BULLET_LIFE / 60"),
        # Cooldown counted in frames.
        ("cooldown = max(0, cooldown - dt)", "cooldown = max(0, cooldown - COOLDOWN / 15)"),
        # No cooldown: a bullet every frame.
        ("        fire()\n        cooldown = COOLDOWN", "        fire()"),
        # Fires without the key held.
        ("    if ' ' in keys and cooldown <= 0:", "    if cooldown <= 0:"),
        # Bullets that die too soon.
        ("BULLET_LIFE = 1\n", "BULLET_LIFE = 0.3\n"),
        # The classic: removing from the list while a for walks it.
        (_MOVE_BULLETS6,
         "def move_bullets(dt):\n    for b in bullets:\n        b.x += b.vx * dt\n        b.y += b.vy * dt\n"
         "        b.life -= dt\n        wrap(b)\n        if b.life <= 0:\n            bullets.remove(b)"),
        # Re-binding without `global`: UnboundLocalError.
        ("    global cooldown\n", ""),
        ("    global bullets\n", ""),
    ],
    "pyast-07-rocks": [
        # Rocks leave and never return.
        ("        wrap(rk)\n", ""),
        # Spin and drift counted per frame.
        ("        rk.angle += rk.spin * dt", "        rk.angle += rk.spin / 60"),
        ("        rk.x += rk.vx * dt", "        rk.x += rk.vx / 60"),
        # Every rock the same size.
        ("random.choice((2, 3))", "3"),
        # Rocks can start on the ship.
        ("            if math.hypot(x - ship.x, y - ship.y) >= 120:\n", "            if True:\n"),
        # Every rock drifts the same way.
        ("    heading = random.uniform(0, math.tau)", "    heading = 1"),
        # Too fast, no spin, no outline, the wrong radius.
        ("random.uniform(20, 60)", "random.uniform(200, 600)"),
        ("spin=random.uniform(-1, 1)", "spin=0"),
        ("shape=[random.uniform(0.75, 1.2) for _ in range(10)]", "shape=[]"),
        ("        size * 14,\n", "        size * 10,\n"),
        # Drawn without their spin.
        ("        ctx.rotate(rk.angle)\n", ""),
        # The mutable default: refused by dataclass (ValueError) - one list for every rock.
        ("shape: list = field(default_factory=list)", "shape: list = []"),
        # [make_rock(...)] * n is one rock, n names.
        (_SPAWN,
         "def spawn_rocks(n):\n    rocks.extend([make_rock(random.uniform(0, WIDTH), random.uniform(0, HEIGHT), 2)] * n)"),
        # No rocks at the start.
        ("spawn_rocks(4)\n", ""),
    ],
    "pyast-08-shoot": [
        # A square, not a circle.
        (_OVERLAP, _SQUARE),
        # Squared distance against radii that were not squared.
        (_OVERLAP, "    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2 < a.r + b.r"),
        # Every rock treated as one big one.
        ("< a.r + b.r", "< a.r + 40"),
        # The bullet survives its hit.
        ("                b.life = 0\n", ""),
        # The rock survives its hit.
        ("                live.remove(rk)\n", ""),
        # The same score whatever the size.
        ("score += POINTS[rk.size]", "score += 10"),
        # One bullet keeps going and breaks several rocks.
        ("                b.life = 0\n                break\n", "                b.life = 0\n"),
        # The classic: removing from the list while a for walks it (the next bullet is skipped).
        (_HIT8,
         "def hit_rocks():\n    global rocks, score\n    for b in bullets:\n        for rk in rocks:\n"
         "            if overlap(b, rk):\n                score += POINTS[rk.size]\n"
         "                rocks.remove(rk)\n                bullets.remove(b)\n                break"),
        # The score is never shown.
        ("    ctx.fill_text(f'Score: {score}', 10, 20)", "    pass"),
        # Re-binding without `global`: UnboundLocalError.
        ("    global bullets, rocks, score\n", "    global bullets, rocks\n"),
        ("    global bullets, rocks, score\n", "    global score\n"),
        # Never called.
        ("    hit_rocks()", "    pass"),
    ],
    "pyast-09-split": [
        # The parent stays behind.
        ("                live.remove(rk)\n", ""),
        # The pieces are as big as the rock.
        ("make_rock(rk.x, rk.y, rk.size - 1)", "make_rock(rk.x, rk.y, rk.size)"),
        # Small rocks split too (into size 0).
        ("    if rk.size == 1:\n", "    if rk.size == 0:\n"),
        # Only one piece.
        ("for _ in range(2)]", "for _ in range(1)]"),
        # Born in the corner.
        ("make_rock(rk.x, rk.y, rk.size - 1)", "make_rock(0, 0, rk.size - 1)"),
        # [x] * 2: one rock, two names - they fly together.
        (_BREAK_ROCK, "    return [make_rock(rk.x, rk.y, rk.size - 1)] * 2"),
        # The pieces are made and thrown away.
        ("                pieces += break_rock(rk)\n", ""),
        ("    rocks = live + pieces\n", "    rocks = live\n"),
    ],
    "pyast-10-lives": [
        # A life lost on every frame of the protection.
        (_HIT_SHIP, "    if any(overlap(ship, rk) for rk in rocks):\n"),
        # Protection counted in frames.
        ("ship.invuln = max(0, ship.invuln - dt)", "ship.invuln = max(0, ship.invuln - 1 / 60)"),
        # Square test against the rocks.
        (_OVERLAP, _SQUARE),
        # Never put back in the middle.
        ("    ship.x, ship.y = WIDTH / 2, HEIGHT / 2\n", ""),
        # Comes back still flying, or pointing the old way.
        ("    ship.vx = ship.vy = 0\n", ""),
        ("    ship.angle = -math.pi / 2\n", ""),
        # No protection, or protection that never ends, or ends at once.
        ("    ship.invuln = INVULN\n", ""),
        ("INVULN = 2", "INVULN = 20"),
        ("INVULN = 2", "INVULN = 0.2"),
        # Protected but not blinking.
        (_BLINK, ""),
        # Lives not shown.
        ("    ctx.fill_text(f'Lives: {lives}', 10, 40)", "    pass"),
        # Re-binding without `global`: UnboundLocalError.
        ("    global lives\n", ""),
        # Never checked.
        ("    hit_ship(dt)", "    pass"),
    ],
    "pyast-11-over": [
        # Enter restarts a game in progress, or any key at all restarts a finished one.
        ("    if key == 'Enter' and state == 'over':", "    if key == 'Enter':"),
        ("    if key == 'Enter' and state == 'over':", "    if state == 'over':"),
        ("on_key_down(key_down)\n", ""),
        # A reset that forgets things.
        ("    score = 0\n    lives = 3\n", "    lives = 3\n"),
        ("    score = 0\n    lives = 3\n", "    score = 0\n"),
        ("    bullets = []\n", ""),
        ("    rocks = []\n", ""),
        ("    cooldown = 0\n", ""),
        ("    place_ship()\n    ship.invuln = 0\n", "    ship.invuln = 0\n"),
        # The game never stops.
        ("    if state != 'playing':\n        return\n", ""),
        ("        state = 'over'\n        return\n", "        return\n"),
        # One life too many.
        ("    if lives <= 0:", "    if lives < 0:"),
        # No message.
        ("        ctx.fill_text('Game over', 150, 150)\n", "        pass\n"),
        # state (or another name) re-bound without `global`: a quiet local.
        ("    global lives, state\n", "    global lives\n"),
        (_GLOBAL_RESET, "    global bullets, rocks, cooldown, score, lives\n"),
        (_GLOBAL_RESET, "    global bullets, rocks, cooldown, lives, state\n"),
        (_GLOBAL_RESET, "    global rocks, cooldown, score, lives, state\n"),
        (_GLOBAL_RESET, "    global bullets, rocks, score, lives, state\n"),
    ],
}

#: Right programs written another way, which the check must still pass. Each
#: way is one (old, new), or a list of them made together.
OTHER_WAYS: dict[str, list] = {
    "pyast-01-turn": [
        # Two ifs instead of the subtraction.
        ("    turn = ('ArrowRight' in keys) - ('ArrowLeft' in keys)\n    ship.angle += turn * TURN * dt",
         "    if 'ArrowRight' in keys:\n        ship.angle += TURN * dt\n    if 'ArrowLeft' in keys:\n        ship.angle -= TURN * dt"),
        ("TURN = 4", "TURN = 3.5"),
        ("Ship(240, 160)", "Ship(x=240, y=160)"),
        # Degrees, converted at the last moment.
        ("-math.pi / 2", "math.radians(-90)"),
    ],
    "pyast-02-thrust": [
        (_THRUST,
         "        push = THRUST * dt\n        ship.vx += push * math.cos(ship.angle)\n        ship.vy += push * math.sin(ship.angle)\n"),
        ("    ship.x += ship.vx * dt\n    ship.y += ship.vy * dt",
         "    ship.x, ship.y = ship.x + ship.vx * dt, ship.y + ship.vy * dt"),
    ],
    # Continuous decay, written other ways; and a linear approximation.
    "pyast-03-friction": [
        ("    damp = DRAG ** dt\n", "    damp = math.exp(-0.7 * dt)\n"),
        ("    damp = DRAG ** dt\n", "    damp = 1 - 0.7 * dt\n"),
        ("    damp = DRAG ** dt\n", "    damp = math.pow(DRAG, dt)\n"),
    ],
    "pyast-04-wrap": [
        # The if / elif way.
        (_WRAP_BODY, _IF_WRAP),
        # A margin written out.
        (_WRAP_BODY,
         "    w, h = WIDTH + 2 * o.r, HEIGHT + 2 * o.r\n    o.x = (o.x + o.r) % w - o.r\n    o.y = (o.y + o.r) % h - o.r"),
    ],
    "pyast-05-bullets": [
        ("    if key == ' ':\n        fire()", "    if key == ' ' and len(bullets) < 50:\n        fire()"),
        ("    c, s = math.cos(ship.angle), math.sin(ship.angle)\n",
         "    c = math.cos(ship.angle)\n    s = math.sin(ship.angle)\n"),
    ],
    "pyast-06-gun": [
        ("COOLDOWN = 0.25", "COOLDOWN = 0.3"),
        ("BULLET_LIFE = 1\n", "BULLET_LIFE = 1.2\n"),
        ("    cooldown = max(0, cooldown - dt)\n", "    if cooldown > 0:\n        cooldown -= dt\n"),
        # Change the list in place: no `global bullets` needed.
        [("    global bullets\n    for b in bullets:", "    for b in bullets:"),
         (_CULL, "    bullets[:] = [b for b in bullets if b.life > 0]\n")],
        # remove() is fine in a loop over a COPY of the list.
        (_MOVE_BULLETS6,
         "def move_bullets(dt):\n    for b in bullets[:]:\n        b.x += b.vx * dt\n        b.y += b.vy * dt\n"
         "        b.life -= dt\n        wrap(b)\n        if b.life <= 0:\n            bullets.remove(b)"),
        (_CULL, "    bullets = list(filter(lambda b: b.life > 0, bullets))\n"),
    ],
    "pyast-07-rocks": [
        ("random.choice((2, 3))", "random.randint(2, 3)"),
        ("math.hypot(x - ship.x, y - ship.y) >= 120", "math.sqrt((x - ship.x) ** 2 + (y - ship.y) ** 2) >= 120"),
        ("math.hypot(x - ship.x, y - ship.y) >= 120", "math.dist((x, y), (ship.x, ship.y)) >= 120"),
        # Two plain statements for the heading.
        ("        math.cos(heading) * speed,\n        math.sin(heading) * speed,\n",
         "        speed * math.cos(heading),\n        speed * math.sin(heading),\n"),
    ],
    # Squared distances, no square root; and loops over copies.
    "pyast-08-shoot": [
        (_OVERLAP, "    dx, dy = a.x - b.x, a.y - b.y\n    return dx * dx + dy * dy < (a.r + b.r) ** 2"),
        (_OVERLAP, "    return math.dist((a.x, a.y), (b.x, b.y)) < a.r + b.r"),
        (_HIT8,
         "def hit_rocks():\n    global score\n    for b in bullets[:]:\n        for rk in rocks[:]:\n"
         "            if overlap(b, rk):\n                score += POINTS[rk.size]\n"
         "                rocks.remove(rk)\n                bullets.remove(b)\n                break"),
    ],
    "pyast-09-split": [
        ("                pieces += break_rock(rk)\n", "                pieces.extend(break_rock(rk))\n"),
        (_BREAK_ROCK,
         "    return [make_rock(rk.x, rk.y, rk.size - 1), make_rock(rk.x, rk.y, rk.size - 1)]"),
        ("    rocks = live + pieces\n", "    rocks = [*live, *pieces]\n"),
        ("    if rk.size == 1:\n        return []\n", "    if rk.size < 2:\n        return []\n"),
    ],
    "pyast-10-lives": [
        # A loop and a break instead of any().
        (_HIT_SHIP + "        lose_life()",
         "    if ship.invuln <= 0:\n        for rk in rocks:\n            if overlap(ship, rk):\n"
         "                lose_life()\n                break"),
        (_HIT_SHIP, "    if ship.invuln == 0 and any(overlap(ship, rk) for rk in rocks):\n"),
        # Another blink.
        (_BLINK, "    if ship.invuln > 0 and (ship.invuln * 10) % 2 >= 1:\n        return\n"),
        ("    ship.x, ship.y = WIDTH / 2, HEIGHT / 2\n    ship.vx = ship.vy = 0\n",
         "    ship.x = WIDTH / 2\n    ship.y = HEIGHT / 2\n    ship.vx = 0\n    ship.vy = 0\n"),
    ],
    "pyast-11-over": [
        # Empty the lists in place: no `global bullets, rocks` needed.
        [(_GLOBAL_RESET, "    global cooldown, score, lives, state\n"),
         ("    bullets = []\n    rocks = []\n", "    bullets.clear()\n    rocks.clear()\n")],
        ("    if key == 'Enter' and state == 'over':", "    if state == 'over' and key == 'Enter':"),
        ("    if state != 'playing':\n        return\n    turn_ship(dt)", "    if state == 'over':\n        return\n    turn_ship(dt)"),
        ("    if lives <= 0:", "    if not lives:"),
    ],
}


def _as_dicts(code: str) -> str:
    """The same program with ship, bullets and rocks dicts, not dataclasses: ship['x'] for ship.x."""

    def factory(m: re.Match[str]) -> str:
        fields = re.findall(r"^    (\w+): \w+(?: = (.+))?$", m.group(2), re.M)
        params = ", ".join(f"{name}={default}" if default else name for name, default in fields)
        body = ", ".join(f"'{name}': {name}" for name, _ in fields)
        return f"def {m.group(1)}({params}):\n    return {{{body}}}\n"

    code = code.replace("field(default_factory=list)", "None")
    made = re.sub(r"@dataclass\nclass (\w+):\n((?:    .+\n?)+)", factory, code)
    made = re.sub(r"from dataclasses import .+\n", "", made)
    made = re.sub(r"\b(ship|b|rk|o|a)\.(x|y|vx|vy|r|angle|spin|size|shape|life|invuln)\b", r"\1['\2']", made)
    assert made != code and "@dataclass" not in made
    return made


class TestShape:
    def test_ids_unique_numbered_and_titled(self) -> None:
        ids = [s.id for s in STEPS]
        assert len(ids) == len(set(ids))
        assert len(STEPS) == 12
        for n, s in enumerate(STEPS, 1):
            assert re.fullmatch(rf"pyast-{n:02d}-[a-z-]+", s.id), s.id
            assert s.title
            assert len(s.teaches) > 120, s.id
            assert s.goal.endswith("."), s.id

    def test_they_are_python_steps_on_their_own_track(self) -> None:
        assert {s.track for s in STEPS} == {"Asteroids (Python)"}
        assert {s.language for s in STEPS} == {"python"}
        assert all(s.kind == "canvas" for s in STEPS)

    @pytest.mark.skipif(not _REGISTERED, reason="PYASTEROIDS_STEPS is not in canvas/__init__.py STEPS yet")
    def test_they_are_registered_after_the_other_python_tracks(self) -> None:
        ids = [s.id for s in ALL_STEPS]
        first = ids.index(STEPS[0].id)
        assert ids[first:first + len(STEPS)] == [s.id for s in STEPS]
        order = [s.track for s in ALL_STEPS]
        for before in ("Dodge (Python)", "Snake (Python)", "Breakout (Python)", "Asteroids"):
            assert order.index(before) < order.index("Asteroids (Python)")

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

    def test_the_goals_name_what_the_checks_read(self) -> None:
        names = {
            "pyast-01-turn": ["ship", "Ship", "TURN", "turn_ship"],
            "pyast-02-thrust": ["THRUST", "fly_ship", "ship.vx", "ship.vy"],
            "pyast-03-friction": ["DRAG", "DRAG ** dt", "ship.vx"],
            "pyast-04-wrap": ["wrap", "ship", "o.r"],
            "pyast-05-bullets": ["bullets", "Bullet", "BULLET_SPEED", "move_bullets"],
            "pyast-06-gun": ["bullets", "BULLET_LIFE", "COOLDOWN", "cooldown", "run_gun", "global bullets"],
            "pyast-07-rocks": ["rocks", "Rock", "make_rock", "spawn_rocks", "default_factory", "move_rocks"],
            "pyast-08-shoot": ["score", "POINTS", "overlap", "hit_rocks", "bullets", "rocks", "make_rock"],
            "pyast-09-split": ["break_rock", "make_rock", "score", "rocks"],
            "pyast-10-lives": ["lives", "INVULN", "invuln", "hit_ship", "lose_life", "rocks"],
            "pyast-11-over": ["state", "'over'", "reset", "score", "lives", "bullets", "rocks", "global"],
        }
        for step_id, wanted in names.items():
            for name in wanted:
                assert name in BY_ID[step_id].goal, f"{step_id}: the goal does not say {name}"

    def test_the_python_way_is_what_gets_taught(self) -> None:
        text = " ".join(s.teaches for s in STEPS)
        for word in ("@dataclass", "default_factory", "list comprehension", "enumerate", "math.hypot",
                     "math.copysign", "math.atan2", "math.cos", "math.sin", "math.radians", "math.tau",
                     "any(", "-5 % 480", "global", "UnboundLocalError", "f-string", "unpacking",
                     "itertools", "random.uniform", "random.choice", "random.randint", "complex", "Vector2",
                     "ValueError", "bullets.remove", "[make_rock(...)] * 2", "def f(seen=[])", "DRAG ** dt",
                     "True is 1", "while True"):
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

    def test_dicts_pass_wherever_the_entities_are_dataclasses(self) -> None:
        for s in STEPS:
            if not s.check:
                continue
            got = run_py_check(_as_dicts(s.solution), s.check)
            assert got.passed, f"{s.id}: {got.message}"

    def test_dict_mistakes_fail_too(self) -> None:
        # The dict form of a few mistakes that hang on a field's name: the check reads both forms alike.
        for step_id, entry in (
            ("pyast-02-thrust", (_THRUST, "        ship.x += math.cos(ship.angle) * THRUST * dt\n"
                                          "        ship.y += math.sin(ship.angle) * THRUST * dt\n")),
            ("pyast-06-gun", (_CULL, "")),
            ("pyast-09-split", (_BREAK_ROCK, "    return [make_rock(rk.x, rk.y, rk.size - 1)] * 2")),
            ("pyast-10-lives", (_HIT_SHIP, "    if any(overlap(ship, rk) for rk in rocks):\n")),
        ):
            s = BY_ID[step_id]
            got = run_py_check(_as_dicts(_swaps(s.solution, entry)), s.check)
            assert not got.passed, step_id

    def test_the_checks_say_what_to_fix_not_just_that_it_failed(self) -> None:
        turn = BY_ID["pyast-01-turn"]
        got = run_py_check(_swap(turn.solution, "TURN = 4", "TURN = 230"), turn.check)
        assert "radians" in got.message
        got = run_py_check(_swap(turn.solution, "    ship.angle += turn * TURN * dt", "    ship.angle += turn * 0.07"),
                           turn.check)
        assert "30 frames a second" in got.message

        thrust = BY_ID["pyast-02-thrust"]
        got = run_py_check(_swap(thrust.solution, _THRUST,
                                 "        ship.vx += math.sin(ship.angle) * THRUST * dt\n"
                                 "        ship.vy += math.cos(ship.angle) * THRUST * dt\n"), thrust.check)
        assert "math.cos(ship.angle)" in got.message

        friction = BY_ID["pyast-03-friction"]
        got = run_py_check(_swap(friction.solution, "    damp = DRAG ** dt\n", "    damp = 0.99\n"), friction.check)
        assert "30 frames a second" in got.message

        wrap = BY_ID["pyast-04-wrap"]
        got = run_py_check(_swap(wrap.solution, _WRAP_BODY, "    o.x %= WIDTH\n    o.y %= HEIGHT"), wrap.check)
        assert "fully off" in got.message and "margin" in got.message

        gun = BY_ID["pyast-06-gun"]
        got = run_py_check(_swap(gun.solution, _MOVE_BULLETS6,
                                 "def move_bullets(dt):\n    for b in bullets:\n        b.x += b.vx * dt\n"
                                 "        b.y += b.vy * dt\n        b.life -= dt\n        wrap(b)\n"
                                 "        if b.life <= 0:\n            bullets.remove(b)"), gun.check)
        assert "skipped" in got.message
        got = run_py_check(_swap(gun.solution, "    global cooldown\n", ""), gun.check)
        assert "UnboundLocalError" in got.message and "line" in got.message

        rocks = BY_ID["pyast-07-rocks"]
        got = run_py_check(_swap(rocks.solution, "shape: list = field(default_factory=list)", "shape: list = []"),
                           rocks.check)
        assert "ValueError" in got.message

        shoot = BY_ID["pyast-08-shoot"]
        got = run_py_check(_swap(shoot.solution, _OVERLAP, _SQUARE), shoot.check)
        assert "math.hypot" in got.message

        split = BY_ID["pyast-09-split"]
        got = run_py_check(_swap(split.solution, _BREAK_ROCK, "    return [make_rock(rk.x, rk.y, rk.size - 1)] * 2"),
                           split.check)
        assert "same rock twice" in got.message

        lives = BY_ID["pyast-10-lives"]
        got = run_py_check(_swap(lives.solution, _HIT_SHIP, "    if any(overlap(ship, rk) for rk in rocks):\n"),
                           lives.check)
        assert "every frame" in got.message

        over = BY_ID["pyast-11-over"]
        got = run_py_check(_swap(over.solution, "    global lives, state\n", "    global lives\n"), over.check)
        assert "global state" in got.message
        got = run_py_check(_swap(over.solution, _GLOBAL_RESET, "    global bullets, rocks, cooldown, lives, state\n"),
                           over.check)
        assert "global" in got.message and "score" in got.message

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

    @pytest.mark.skipif(not _REGISTERED, reason="PYASTEROIDS_STEPS is not in canvas/__init__.py STEPS yet")
    def test_the_open_step_always_passes(self) -> None:
        got = check_step(STEPS[-1].id, "")
        assert got is not None and got.passed

    @pytest.mark.skipif(not _REGISTERED, reason="PYASTEROIDS_STEPS is not in canvas/__init__.py STEPS yet")
    def test_check_step_runs_a_python_step_through_the_python_harness(self) -> None:
        s = STEPS[3]
        assert check_step(s.id, s.solution).passed
        assert not check_step(s.id, s.starter).passed
