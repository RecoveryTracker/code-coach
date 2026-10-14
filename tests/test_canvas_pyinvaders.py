"""Canvas: the Python Space Invaders steps and their checks.

A game with no JavaScript twin, played in a child process. A check is held to
three things: the step's own solution passes, its starter (the step before,
finished) does not, and the mistakes people really make at that step fail it
too - moving per frame instead of per second (the checks run at 30 frames a
second as well as 60), a cannon with no clamp, a bullet per frame instead of one
at a time, a bullet that is never given back, a block that only turns at one
edge (or judges the edge by the first alien in the list), a drop with no turn
(so it drops every frame), a speed that never rises, `remove()` inside a `for`
over the same list, `aliens.pop()` for the alien that was hit, a hit test on
the centre alone, bombs from any alien instead of the bottom of a column, a
bomb that is never removed (a life a frame), a game that never ends, a wave that
never starts (or starts every frame), a restart that leaves the aliens as they
were, a `global` line that is missing a name. A check that let those through
would be checking nothing.

Cannon, bullet, aliens and bombs may be dataclasses or dicts; the checks work
with both, and so do these tests (`_as_dicts` rewrites every solution with
dicts). Nothing here needs the track to be registered in canvas/__init__.py:
the tests that do are skipped until it is.
"""

from __future__ import annotations

import re

import pytest

from code_coach.canvas import STEPS as ALL_STEPS
from code_coach.canvas import check_step, run_py_check
from code_coach.canvas import content_pyinvaders as K
from code_coach.canvas.content_pyinvaders import PYINVADERS_STEPS as STEPS

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

_BG = K._D_BG
_CANNON_DRAW = K._D_CANNON
_BULLET_DRAW = K._D_BULLET
_ALIENS_DRAW = K._D_ALIENS
_BOMBS_DRAW = K._D_BOMBS
_CLAMP = "    cannon.x = max(0, min(WIDTH - cannon.w, cannon.x))\n"
_ALIEN_LIST = K._N_ALIENS + "\n"
_AT_RIGHT = "    at_right = direction > 0 and any(a.x + a.w > WIDTH for a in aliens)\n"
_AT_LEFT = "    at_left = direction < 0 and any(a.x < 0 for a in aliens)\n"
_DROP_ROWS = "        for a in aliens:\n            a.y += DROP"
_OVERLAP_BODY = "    return a.x < b.x + b.w and a.x + a.w > b.x and a.y < b.y + b.h and a.y + a.h > b.y"
_HIT_BODY = (
    "    hit = [a for a in aliens if overlap(bullet, a)]\n    if hit:\n"
    "        aliens = [a for a in aliens if a not in hit]\n        bullet = None\n"
    "        score += sum(ROW_POINTS[a.row] for a in hit)"
)
_BOTTOMS = (
    "    bottoms = {}\n    for a in aliens:\n        low = bottoms.get(a.col)\n"
    "        if low is None or a.y > low.y:\n            bottoms[a.col] = a\n"
    "    shooter = random.choice(list(bottoms.values()))\n"
)
_BOMB_FILTER = "    bombs = [b for b in bombs if b.y < HEIGHT]"
_HIT_CANNON_BODY = (
    "    hit = [b for b in bombs if overlap(b, cannon)]\n    if hit:\n"
    "        bombs = [b for b in bombs if b not in hit]\n        lives = max(0, lives - len(hit))"
)
_GUARD = "    if state != 'playing':\n        return\n"
_WIN = "    if not aliens:\n        start_wave(wave + 1)\n"

#: Wrong programs, each a real mistake at that step, that the check must fail.
#: An entry is one (what to find in the solution, what to put there instead),
#: or a list of those, made together.
MISTAKES: dict[str, list] = {
    "pyinv-01-cannon": [
        # Width and height the wrong way round.
        ("Cannon(222, 296, 36, 12)", "Cannon(222, 296, 12, 36)"),
        # Not in the middle, or not at the bottom.
        ("Cannon(222, 296, 36, 12)", "Cannon(0, 296, 36, 12)"),
        ("Cannon(222, 296, 36, 12)", "Cannon(222, 100, 36, 12)"),
        # Drawn first: the background paints over it.
        (_BG + "\n" + _CANNON_DRAW, _CANNON_DRAW + "\n" + _BG),
        # Never drawn.
        ("\n" + _CANNON_DRAW, ""),
        # The colour of the background.
        ("ctx.fill_style = '#4fd1c5'", "ctx.fill_style = '#10141f'"),
        # Drawn once while the program loads, not every frame.
        [("\n" + _CANNON_DRAW, ""),
         ("on_frame(loop)\n", "ctx.fill_style = '#4fd1c5'\nctx.fill_rect(222, 296, 36, 12)\non_frame(loop)\n")],
        # No speed on the cannon.
        ("    speed: float = 240", "    speed: float = 3"),
    ],
    "pyinv-02-move": [
        # Per frame, not per second.
        [("        cannon.x -= cannon.speed * dt\n", "        cannon.x -= 4\n"),
         ("        cannon.x += cannon.speed * dt\n", "        cannon.x += 4\n")],
        # Speed with no dt: pixels a frame.
        ("cannon.speed * dt", "cannon.speed"),
        # dt written in as a constant: right at 60 frames a second, wrong at 30.
        ("cannon.speed * dt", "cannon.speed / 60"),
        # Only one direction.
        ("    if 'ArrowLeft' in keys:\n        cannon.x -= cannon.speed * dt\n", ""),
        ("    if 'ArrowRight' in keys:\n        cannon.x += cannon.speed * dt\n", ""),
        # No clamp, or half of one.
        (_CLAMP, "    pass\n"),
        ("max(0, min(WIDTH - cannon.w, cannon.x))", "min(WIDTH - cannon.w, cannon.x)"),
        ("min(WIDTH - cannon.w, cannon.x)", "min(WIDTH, cannon.x)"),
        # A held-key set of your own that is added to and never emptied.
        ("from canvas import ctx, WIDTH, HEIGHT, on_frame, keys\n",
         "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down\n\nkeys = set()\non_key_down(keys.add)\n"),
        # update never calls move_cannon.
        ("    move_cannon(dt)\n", "    pass\n"),
    ],
    "pyinv-03-bullet": [
        # Several at once: a new bullet whenever Space is down.
        ("    if ' ' in keys and bullet is None:", "    if ' ' in keys:"),
        # A list of bullets is another game; the name is `bullet`.
        ("bullet = None\n\n\ndef move_cannon", "bullets = []\n\n\ndef move_cannon"),
        # Per frame, not per second.
        ("    bullet.y += bullet.vy * dt\n", "    bullet.y -= 6\n"),
        ("bullet.vy * dt", "bullet.vy / 60"),
        # Flying down.
        ("vy: float = -360", "vy: float = 360"),
        # Never given back: one shot per game.
        ("    if bullet.y + bullet.h < 0:\n        bullet = None", "    pass"),
        # Given back while still on screen: a second shot in the air.
        ("bullet.y + bullet.h < 0", "bullet.y < 150"),
        # Born inside the cannon, or at its left end.
        ("cannon.y - 10", "cannon.y + 10"),
        ("Bullet(cannon.x + cannon.w / 2 - 2,", "Bullet(cannon.x,"),
        # Fires without Space.
        ("    if ' ' in keys and bullet is None:", "    if bullet is None:"),
        # Never drawn.
        ("\n" + _BULLET_DRAW, ""),
        # Re-binding without `global`: UnboundLocalError, or a quiet local.
        ("def fire():\n    global bullet\n", "def fire():\n"),
        ("def move_bullet(dt):\n    global bullet\n", "def move_bullet(dt):\n"),
        # fire() is never called.
        ("    fire()\n", "    pass\n"),
    ],
    "pyinv-04-aliens": [
        # One alien, forty names for it.
        (_ALIEN_LIST, "aliens = [Alien(40, 40, 0, 0, '#fc8181')] * 40\n"),
        # Eight aliens, five names for each.
        (_ALIEN_LIST,
         "aliens = [Alien(40 + col * 36, 40, 0, col, ROW_COLORS[0]) for col in range(COLS)] * 5\n"),
        # Row and column swapped.
        ("Alien(40 + col * 36, 40 + row * 26, row, col, color)", "Alien(40 + row * 36, 40 + col * 26, row, col, color)"),
        # The fields in the wrong order.
        ("Alien(40 + col * 36, 40 + row * 26, row, col, color)", "Alien(40 + col * 36, 40 + row * 26, col, row, color)"),
        ("enumerate(ROW_COLORS)", "enumerate(ROW_COLORS[:4])"),
        ("for col in range(COLS)", "for col in range(COLS - 1)"),
        # Never drawn, or drawn first and painted over.
        (_ALIENS_DRAW, ""),
        (_BG + "\n" + _ALIENS_DRAW, _ALIENS_DRAW + "\n" + _BG),
        # Every row the same colour.
        ("ctx.fill_style = a.color", "ctx.fill_style = '#fc8181'"),
        # Tall and thin.
        ("    w: float = 24\n    h: float = 16", "    w: float = 16\n    h: float = 24"),
    ],
    "pyinv-05-march": [
        # Per frame, not per second.
        ("direction * ALIEN_SPEED * dt", "direction * ALIEN_SPEED / 60"),
        ("direction * ALIEN_SPEED * dt", "direction * ALIEN_SPEED"),
        ("direction * ALIEN_SPEED * dt", "direction * 0.7"),
        # direction ignored: it can only go right.
        ("direction * ALIEN_SPEED * dt", "ALIEN_SPEED * dt"),
        # Only one alien, or one row.
        ("    for a in aliens:\n        a.x += direction * ALIEN_SPEED * dt", "    aliens[0].x += direction * ALIEN_SPEED * dt"),
        ("    for a in aliens:\n        a.x += direction * ALIEN_SPEED * dt", "    for a in aliens[:8]:\n        a.x += direction * ALIEN_SPEED * dt"),
        # They sink as they march.
        ("        a.x += direction * ALIEN_SPEED * dt", "        a.x += direction * ALIEN_SPEED * dt\n        a.y += 1"),
        # Too fast, or the wrong way to start.
        ("ALIEN_SPEED = 40", "ALIEN_SPEED = 80"),
        ("direction = 1", "direction = -1"),
        # Never called.
        ("    march(dt)", "    pass"),
    ],
    "pyinv-06-edges": [
        # Only one edge.
        (_AT_LEFT + "    if at_right or at_left:", "    if at_right:"),
        (_AT_RIGHT + _AT_LEFT + "    if at_right or at_left:", _AT_LEFT + "    if at_left:"),
        # The edge judged by the first alien in the list.
        ("any(a.x + a.w > WIDTH for a in aliens)", "aliens[0].x + aliens[0].w > WIDTH"),
        ("any(a.x < 0 for a in aliens)", "aliens[0].x < 0"),
        # A width written in, so a block that has lost its end columns still turns too soon.
        ("any(a.x + a.w > WIDTH for a in aliens)", "aliens[0].x + 276 > WIDTH"),
        # The left side of an alien for the right edge.
        ("any(a.x + a.w > WIDTH for a in aliens)", "any(a.x > WIDTH for a in aliens)"),
        # A margin: turning before the edge is touched.
        ("a.x + a.w > WIDTH for a in aliens", "a.x + a.w > WIDTH - 20 for a in aliens"),
        ("a.x < 0 for a in aliens", "a.x < 20 for a in aliens"),
        # Dropping but not turning round: still over the edge, so it drops every frame.
        ("        direction = -direction\n", ""),
        # Turning round but not dropping, or only one alien dropping.
        (_DROP_ROWS, "        pass"),
        (_DROP_ROWS, "        aliens[0].y += DROP"),
        # The wrong size of drop.
        ("DROP = 16", "DROP = 8"),
        # Always turns to the same side.
        ("direction = -direction", "direction = -1"),
        # Re-binding without `global`: UnboundLocalError.
        ("def march(dt):\n    global direction\n", "def march(dt):\n"),
    ],
    "pyinv-07-shoot": [
        # The classic: remove() while a for walks the list (and bullet = None breaks the next pass).
        (_HIT_BODY,
         "    for a in aliens:\n        if overlap(bullet, a):\n            aliens.remove(a)\n"
         "            bullet = None\n            score += ROW_POINTS[a.row]"),
        # The wrong alien.
        ("        aliens = [a for a in aliens if a not in hit]\n", "        aliens.pop()\n"),
        ("        aliens = [a for a in aliens if a not in hit]\n", "        aliens.remove(aliens[0])\n"),
        # The bullet is not used up.
        ("        bullet = None\n        score +=", "        score +="),
        # Points that ignore the row.
        ("sum(ROW_POINTS[a.row] for a in hit)", "10 * len(hit)"),
        ("ROW_POINTS[a.row]", "ROW_POINTS[a.col % 5]"),
        ("ROW_POINTS = [30, 20, 20, 10, 10]", "ROW_POINTS = [10, 10, 20, 20, 30]"),
        # Score never shown.
        ("    ctx.fill_text(f'Score: {score}', 10, 20)\n", ""),
        # No hit at all when there is no bullet: crashes on None.
        ("    if bullet is None:\n        return\n    hit =", "    hit ="),
        # Hit tests that are not boxes.
        (_OVERLAP_BODY,
         "    cx, cy = a.x + a.w / 2, a.y + a.h / 2\n    return b.x <= cx <= b.x + b.w and b.y <= cy <= b.y + b.h"),
        (_OVERLAP_BODY, "    return a.x < b.x + b.w and a.x + a.w > b.x"),
        (_OVERLAP_BODY, "    return a.y < b.y + b.h and a.y + a.h > b.y"),
        (_OVERLAP_BODY, "    return a.x < b.x + b.w and a.x + a.w > b.x and a.y < b.y + b.h"),
        (_OVERLAP_BODY,
         "    return a.x < b.x + b.w + 10 and a.x + a.w > b.x - 10 and a.y < b.y + b.h and a.y + a.h > b.y"),
        # Re-binding without `global`.
        ("    global bullet, aliens, score\n", "    global bullet, score\n"),
        ("    global bullet, aliens, score\n", "    global bullet, aliens\n"),
        ("    global bullet, aliens, score\n", "    global aliens, score\n"),
        # Never called.
        ("    hit_aliens()\n", "    pass\n"),
    ],
    "pyinv-08-faster": [
        # Never rises.
        (K._SPEED8, "def march_speed():\n    return ALIEN_SPEED"),
        # Rises the wrong way round.
        ("ALIEN_SPEED + 3 * (TOTAL - len(aliens))", "ALIEN_SPEED + 3 * len(aliens)"),
        ("ALIEN_SPEED + 3 * (TOTAL - len(aliens))", "ALIEN_SPEED - 0.5 * (TOTAL - len(aliens))"),
        # Stands still at the start.
        ("ALIEN_SPEED + 3 * (TOTAL - len(aliens))", "ALIEN_SPEED * (TOTAL - len(aliens))"),
        # A rise too small to notice, or too big to play.
        ("ALIEN_SPEED + 3 * (TOTAL - len(aliens))", "ALIEN_SPEED + 0.2 * (TOTAL - len(aliens))"),
        ("ALIEN_SPEED + 3 * (TOTAL - len(aliens))", "ALIEN_SPEED + 30 * (TOTAL - len(aliens))"),
        # Per frame, not per second.
        ("direction * march_speed() * dt", "direction * march_speed() / 60"),
        ("direction * march_speed() * dt", "direction * march_speed()"),
        # march_speed is never used.
        ("direction * march_speed() * dt", "direction * ALIEN_SPEED * dt"),
    ],
    "pyinv-09-bombs": [
        # From any alien, not only the bottom of a column.
        ("    shooter = random.choice(list(bottoms.values()))", "    shooter = random.choice(aliens)"),
        # Always the same column.
        ("random.choice(list(bottoms.values()))", "list(bottoms.values())[0]"),
        # The highest alien of each column, not the lowest.
        ("a.y > low.y", "a.y < low.y"),
        # A dict keyed by row, not column: the first alien of every row.
        [("bottoms.get(a.col)", "bottoms.get(a.row)"), ("bottoms[a.col] = a", "bottoms[a.row] = a")],
        # Bombs never leave.
        (_BOMB_FILTER, "    pass"),
        # Bombs that vanish half way down.
        ("b.y < HEIGHT]", "b.y < 200]"),
        # Per frame, not per second.
        ("b.y += b.vy * dt", "b.y += 3"),
        ("b.y += b.vy * dt", "b.y += b.vy / 60"),
        # Counted in frames, not seconds: right at 60 a second, half as many at 30.
        [("\nevery(BOMB_EVERY, drop_bomb)", ""),
         ("score = 0\nbombs = []", "score = 0\nbombs = []\ntick = 0"),
         ("    move_bombs(dt)\n",
          "    global tick\n    tick += 1\n    if tick % 48 == 0:\n        drop_bomb()\n    move_bombs(dt)\n")],
        # Never dropped.
        ("\nevery(BOMB_EVERY, drop_bomb)", ""),
        # Born at the alien's top-left corner.
        ("Bomb(shooter.x + shooter.w / 2 - 2, shooter.y + shooter.h, 4, 10)", "Bomb(shooter.x, shooter.y, 4, 10)"),
        # Never drawn.
        ("\n" + _BOMBS_DRAW, ""),
        # Re-binding without `global`.
        ("def move_bombs(dt):\n    global bombs\n", "def move_bombs(dt):\n"),
    ],
    "pyinv-10-lives": [
        # A life lost on every frame the bomb is over the cannon.
        ("        bombs = [b for b in bombs if b not in hit]\n", ""),
        # No life taken.
        ("        lives = max(0, lives - len(hit))\n", "        pass\n"),
        # Never over at 0 lives.
        ("lives <= 0 or ", "lives < 0 or "),
        # Aliens landing do not end the game, or by their tops.
        ("lives <= 0 or any(a.y + a.h >= cannon.y for a in aliens)", "lives <= 0"),
        ("a.y + a.h >= cannon.y", "a.y >= cannon.y"),
        # Nothing stops when it is over.
        (_GUARD + "    move_cannon", "    move_cannon"),
        ("    if state != 'playing' or not aliens:", "    if not aliens:"),
        # Hit tests that are not boxes.
        (_OVERLAP_BODY, "    return a.x < b.x + b.w and a.x + a.w > b.x"),
        (_OVERLAP_BODY, "    return a.y < b.y + b.h and a.y + a.h > b.y"),
        # Not shown.
        (K._HUD_LIVES, ""),
        (K._HUD_OVER, ""),
        # Wrong number of lives.
        ("lives = 3", "lives = 5"),
        # Re-binding without `global`.
        ("    global state\n", ""),
        ("    global bombs, lives\n", "    global bombs\n"),
        ("    global bombs, lives\n", "    global lives\n"),
        # Never called.
        ("    hit_cannon()\n", "    pass\n"),
        ("    check_over()\n", "    pass\n"),
    ],
    "pyinv-11-waves": [
        # No win.
        (_WIN, ""),
        # Wave one, again.
        ("    wave = n\n", ""),
        # Not faster.
        ("10 * (wave - 1) + ", ""),
        ("10 * (wave - 1) + ", "0.5 * (wave - 1) + "),
        # A wave that starts with no aliens: and starts again every frame.
        ("    aliens = make_aliens()\n    bombs = []", "    bombs = []"),
        # Won too early, with an alien still standing.
        (_WIN, "    if len(aliens) <= 1:\n        start_wave(wave + 1)\n"),
        # Old bombs still falling; the block still heading left.
        ("    bombs = []\n    bullet = None", "    bullet = None"),
        ("    direction = 1\n", ""),
        # Score thrown away.
        [("    global aliens, bombs, bullet, direction, wave\n", "    global aliens, bombs, bullet, direction, wave, score\n"),
         ("    wave = n\n", "    wave = n\n    score = 0\n")],
        # Wave not shown.
        (K._HUD_WAVE, ""),
        # Re-binding without `global`.
        ("    global aliens, bombs, bullet, direction, wave\n", "    global bombs, bullet, direction, wave\n"),
        ("    global aliens, bombs, bullet, direction, wave\n", "    global aliens, bombs, bullet, direction\n"),
    ],
    "pyinv-12-restart": [
        # The aliens are left as the last game left them.
        [("    start_wave(1)\n", "    wave = 1\n"), ("    global score, lives, state\n", "    global score, lives, state, wave\n")],
        # The wave number carries on.
        ("start_wave(1)", "start_wave(wave)"),
        # A name missing from `global`: a quiet local.
        ("    global score, lives, state\n", "    global score, lives\n"),
        ("    global score, lives, state\n", "    global lives, state\n"),
        ("    global score, lives, state\n", "    global score, state\n"),
        # The cannon left where it was.
        ("    cannon.x = WIDTH / 2 - cannon.w / 2\n", ""),
        # Enter in the middle of a game, or any key at all.
        ("    if key == 'Enter' and state == 'over':", "    if key == 'Enter':"),
        ("    if key == 'Enter' and state == 'over':", "    if state == 'over':"),
        # Only after the lives run out, not when the aliens land.
        ("state == 'over':\n        restart()", "state == 'over' and lives == 0:\n        restart()"),
        ("on_key_down(key_down)\n", ""),
        (K._HUD_ENTER, ""),
        # The score and lives left alone.
        ("    score = 0\n", ""),
        ("    lives = 3\n    state", "    state"),
    ],
}

#: Right programs written another way, which the check must still pass. Each
#: way is one (old, new), or a list of them made together.
OTHER_WAYS: dict[str, list] = {
    "pyinv-01-cannon": [
        ("Cannon(222, 296, 36, 12)", "Cannon(x=222, y=296, w=36, h=12)"),
        ("ctx.fill_style = '#4fd1c5'", "ctx.fill_style = 'orange'"),
    ],
    "pyinv-02-move": [
        # elif: right wins over left, nobody minds.
        ("    if 'ArrowRight' in keys:\n", "    elif 'ArrowRight' in keys:\n"),
        # A clamp written out.
        (_CLAMP,
         "    if cannon.x < 0:\n        cannon.x = 0\n"
         "    if cannon.x > WIDTH - cannon.w:\n        cannon.x = WIDTH - cannon.w\n"),
        (_CLAMP, "    cannon.x = min(max(cannon.x, 0), WIDTH - cannon.w)\n"),
        # Your own held-key set, kept the right way.
        ("from canvas import ctx, WIDTH, HEIGHT, on_frame, keys\n",
         "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down, on_key_up\n\n"
         "keys = set()\non_key_down(keys.add)\non_key_up(keys.discard)\n"),
    ],
    "pyinv-03-bullet": [
        ("    if ' ' in keys and bullet is None:", "    if bullet == None and ' ' in keys:"),
        ("    if bullet is None:\n        return\n    bullet.y += bullet.vy * dt\n    if bullet.y + bullet.h < 0:\n        bullet = None",
         "    if bullet is not None:\n        bullet.y += bullet.vy * dt\n        if bullet.y + bullet.h < 0:\n            bullet = None"),
        ("Bullet(cannon.x + cannon.w / 2 - 2, cannon.y - 10, 4, 10)",
         "Bullet(x=cannon.x + cannon.w / 2 - 2, y=cannon.y - 12, w=4, h=10)"),
        # The bullet goes once it is clear of the top, not when its bottom is.
        ("bullet.y + bullet.h < 0", "bullet.y < -bullet.h"),
    ],
    "pyinv-04-aliens": [
        # itertools.product in place of the two for clauses.
        [("from dataclasses import dataclass\n", "from dataclasses import dataclass\nfrom itertools import product\n"),
         (_ALIEN_LIST,
          "aliens = [\n    Alien(40 + col * 36, 40 + row * 26, row, col, ROW_COLORS[row])\n"
          "    for row, col in product(range(len(ROW_COLORS)), range(COLS))\n]\n")],
        # Two plain loops and append.
        (_ALIEN_LIST,
         "aliens = []\nfor row, color in enumerate(ROW_COLORS):\n    for col in range(COLS):\n"
         "        aliens.append(Alien(40 + col * 36, 40 + row * 26, row, col, color))\n"),
        # A comprehension with the rows in range().
        (_ALIEN_LIST,
         "aliens = [\n    Alien(40 + col * 36, 40 + row * 26, row, col, ROW_COLORS[row])\n"
         "    for row in range(5)\n    for col in range(COLS)\n]\n"),
        # Keywords.
        ("Alien(40 + col * 36, 40 + row * 26, row, col, color)", "Alien(x=40 + col * 36, y=40 + row * 26, row=row, col=col, color=color)"),
    ],
    "pyinv-05-march": [
        ("    for a in aliens:\n        a.x += direction * ALIEN_SPEED * dt",
         "    step = direction * ALIEN_SPEED * dt\n    for a in aliens:\n        a.x += step"),
        ("        a.x += direction * ALIEN_SPEED * dt", "        a.x = a.x + direction * ALIEN_SPEED * dt"),
    ],
    "pyinv-06-edges": [
        # One test for both edges: turning round makes it safe next frame.
        (_AT_RIGHT + _AT_LEFT + "    if at_right or at_left:",
         "    if any(a.x + a.w > WIDTH or a.x < 0 for a in aliens):"),
        # max and min of a generator.
        [("any(a.x + a.w > WIDTH for a in aliens)", "max(a.x + a.w for a in aliens) > WIDTH"),
         ("any(a.x < 0 for a in aliens)", "min(a.x for a in aliens) < 0")],
        # max and min that survive an empty formation.
        [("any(a.x + a.w > WIDTH for a in aliens)", "max((a.x + a.w for a in aliens), default=0) > WIDTH"),
         ("any(a.x < 0 for a in aliens)", "min((a.x for a in aliens), default=WIDTH) < 0")],
        # The drop in one line.
        (_DROP_ROWS, "        for a in aliens:\n            a.y = a.y + DROP"),
    ],
    "pyinv-07-shoot": [
        # remove() is fine when the loop stops straight after.
        (_HIT_BODY,
         "    for a in aliens:\n        if overlap(bullet, a):\n            aliens.remove(a)\n"
         "            score += ROW_POINTS[a.row]\n            bullet = None\n            break"),
        # A dict of points.
        ("ROW_POINTS = [30, 20, 20, 10, 10]", "ROW_POINTS = {0: 30, 1: 20, 2: 20, 3: 10, 4: 10}"),
        # A loop in place of sum().
        ("        score += sum(ROW_POINTS[a.row] for a in hit)", "        for a in hit:\n            score += ROW_POINTS[a.row]"),
        # Boxes that do NOT miss.
        (_OVERLAP_BODY,
         "    return not (a.x + a.w <= b.x or b.x + b.w <= a.x or a.y + a.h <= b.y or b.y + b.h <= a.y)"),
    ],
    "pyinv-08-faster": [
        # A speed-up that grows faster the fewer are left.
        ("ALIEN_SPEED + 3 * (TOTAL - len(aliens))", "ALIEN_SPEED + (TOTAL - len(aliens)) ** 2 / 10"),
        ("ALIEN_SPEED + 3 * (TOTAL - len(aliens))", "ALIEN_SPEED * (1 + (TOTAL - len(aliens)) / 10)"),
        ("ALIEN_SPEED + 3 * (TOTAL - len(aliens))", "ALIEN_SPEED + 4 * (TOTAL - len(aliens))"),
        # A speed kept in a variable that every kill raises.
        [(K._SPEED8, "def march_speed():\n    return speed"),
         ("direction = 1\nscore = 0", "direction = 1\nscore = 0\nspeed = ALIEN_SPEED"),
         ("    global bullet, aliens, score\n", "    global bullet, aliens, score, speed\n"),
         ("        bullet = None\n        score +=", "        bullet = None\n        speed += 3 * len(hit)\n        score +=")],
    ],
    "pyinv-09-bombs": [
        # max() with a key, one column at a time.
        (_BOTTOMS,
         "    columns = {a.col for a in aliens}\n"
         "    bottoms = [max((a for a in aliens if a.col == c), key=lambda a: a.y) for c in columns]\n"
         "    shooter = random.choice(bottoms)\n"),
        # Sorted, so the lowest alien of a column is written last and wins.
        (_BOTTOMS,
         "    bottoms = {}\n    for a in sorted(aliens, key=lambda a: a.y):\n        bottoms[a.col] = a\n"
         "    shooter = random.choice(list(bottoms.values()))\n"),
        # A copy of the list, and remove().
        [("    global bombs\n", ""),
         (_BOMB_FILTER, "    for b in bombs[:]:\n        if b.y >= HEIGHT:\n            bombs.remove(b)")],
        ("BOMB_EVERY = 0.8", "BOMB_EVERY = 1.0"),
        ("BOMB_EVERY = 0.8", "BOMB_EVERY = 0.6"),
    ],
    "pyinv-10-lives": [
        ("        lives = max(0, lives - len(hit))\n", "        lives -= len(hit)\n"),
        ("lives <= 0 or", "lives == 0 or"),
        ("any(a.y + a.h >= cannon.y for a in aliens)", "max((a.y + a.h for a in aliens), default=0) >= cannon.y"),
        # A loop over a copy, and remove().
        [("    global bombs, lives\n", "    global lives\n"),
         (_HIT_CANNON_BODY,
          "    for b in bombs[:]:\n        if overlap(b, cannon):\n            bombs.remove(b)\n"
          "            lives = max(0, lives - 1)")],
    ],
    "pyinv-11-waves": [
        (_WIN, "    if len(aliens) == 0:\n        start_wave(wave + 1)\n"),
        (_WIN, "    if aliens == []:\n        start_wave(wave + 1)\n"),
        ("ALIEN_SPEED + 10 * (wave - 1) + 3 * (TOTAL - len(aliens))",
         "ALIEN_SPEED * (1 + 0.25 * (wave - 1)) + 3 * (TOTAL - len(aliens))"),
        # Change the list in place: no `global aliens` needed.
        [("    global aliens, bombs, bullet, direction, wave\n", "    global bombs, bullet, direction, wave\n"),
         ("    aliens = make_aliens()\n", "    aliens[:] = make_aliens()\n")],
        # A fresh list of rows built by loops.
        (K._MAKE_ALIENS,
         "def make_aliens():\n    fresh = []\n    for row, color in enumerate(ROW_COLORS):\n        for col in range(COLS):\n"
         "            fresh.append(Alien(40 + col * 36, 40 + row * 26, row, col, color))\n    return fresh"),
    ],
    "pyinv-12-restart": [
        ("    if key == 'Enter' and state == 'over':\n        restart()",
         "    if state != 'over':\n        return\n    if key == 'Enter':\n        restart()"),
        ("    cannon.x = WIDTH / 2 - cannon.w / 2\n", "    cannon.x = 222\n"),
        ("    score = 0\n    lives = 3\n    state = 'playing'\n", "    score, lives, state = 0, 3, 'playing'\n"),
    ],
}


def _as_dicts(code: str) -> str:
    """The same program with cannon, bullet, aliens and bombs dicts, not dataclasses: a['x'] for a.x."""

    def factory(m: re.Match[str]) -> str:
        fields = re.findall(r"^    (\w+): \w+(?: = (.+))?$", m.group(2), re.M)
        params = ", ".join(f"{name}={default}" if default else name for name, default in fields)
        body = ", ".join(f"'{name}': {name}" for name, _ in fields)
        return f"def {m.group(1)}({params}):\n    return {{{body}}}\n"

    made = re.sub(r"@dataclass\nclass (\w+):\n((?:    .+\n?)+)", factory, code)
    made = made.replace("from dataclasses import dataclass\n", "")
    made = re.sub(r"\b(cannon|bullet|a|b|low|shooter)\.(x|y|w|h|vy|row|col|speed|color)\b", r"\1['\2']", made)
    assert made != code and "@dataclass" not in made
    return made


class TestShape:
    def test_ids_unique_numbered_and_titled(self) -> None:
        ids = [s.id for s in STEPS]
        assert len(ids) == len(set(ids))
        assert len(STEPS) == 13
        for n, s in enumerate(STEPS, 1):
            assert re.fullmatch(rf"pyinv-{n:02d}-[a-z-]+", s.id), s.id
            assert s.title
            assert len(s.teaches) > 120, s.id
            assert s.goal.endswith("."), s.id

    def test_they_are_python_steps_on_their_own_track(self) -> None:
        assert {s.track for s in STEPS} == {"Space Invaders (Python)"}
        assert {s.language for s in STEPS} == {"python"}
        assert all(s.kind == "canvas" for s in STEPS)

    @pytest.mark.skipif(not _REGISTERED, reason="PYINVADERS_STEPS is not in canvas/__init__.py STEPS yet")
    def test_they_are_registered_together_after_the_other_python_tracks(self) -> None:
        ids = [s.id for s in ALL_STEPS]
        first = ids.index(STEPS[0].id)
        assert ids[first:first + len(STEPS)] == [s.id for s in STEPS]
        order = [s.track for s in ALL_STEPS]
        assert order.index("Dodge (Python)") < order.index("Space Invaders (Python)")
        assert order.index("To-do") < order.index("Space Invaders (Python)")

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
            "pyinv-01-cannon": ["cannon", "Cannon"],
            "pyinv-02-move": ["move_cannon", "cannon.speed"],
            "pyinv-03-bullet": ["bullet", "Bullet", "fire()", "move_bullet", "None"],
            "pyinv-04-aliens": ["aliens", "Alien", "ROW_COLORS"],
            "pyinv-05-march": ["direction", "ALIEN_SPEED", "march"],
            "pyinv-06-edges": ["DROP", "direction", "march"],
            "pyinv-07-shoot": ["score", "ROW_POINTS", "overlap", "hit_aliens", "bullet", "aliens"],
            "pyinv-08-faster": ["march_speed", "TOTAL"],
            "pyinv-09-bombs": ["Bomb", "bombs", "BOMB_EVERY", "drop_bomb", "move_bombs", "random", "every"],
            "pyinv-10-lives": ["lives", "state", "'over'", "hit_cannon", "check_over"],
            "pyinv-11-waves": ["wave", "make_aliens", "start_wave", "march_speed"],
            "pyinv-12-restart": ["restart", "start_wave", "Enter", "'over'"],
        }
        for step_id, wanted in names.items():
            for name in wanted:
                assert name in BY_ID[step_id].goal, f"{step_id}: the goal does not say {name}"

    def test_the_python_way_is_what_gets_taught(self) -> None:
        text = " ".join(s.teaches for s in STEPS)
        for word in ("@dataclass", "default", "list comprehension", "enumerate", "itertools.product",
                     "[Alien(...)] * 40", "[[0] * 8] * 5", "is None", "global", "UnboundLocalError",
                     "any(", "max(", "min(", "ValueError", "aliens.remove(a)", "sum(", "f-string",
                     "random.choice", "bottoms", "key=lambda", "every(", "not aliens", "zip(", "dict",
                     "on_key_down", "keys"):
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
            ("pyinv-03-bullet", ("    if ' ' in keys and bullet is None:", "    if ' ' in keys:")),
            ("pyinv-04-aliens", (_ALIEN_LIST, "aliens = [Alien(40, 40, 0, 0, '#fc8181')] * 40\n")),
            ("pyinv-07-shoot", ("        aliens = [a for a in aliens if a not in hit]\n", "        aliens.pop()\n")),
            ("pyinv-09-bombs", ("    shooter = random.choice(list(bottoms.values()))", "    shooter = random.choice(aliens)")),
            ("pyinv-10-lives", ("        bombs = [b for b in bombs if b not in hit]\n", "")),
        ):
            s = BY_ID[step_id]
            got = run_py_check(_as_dicts(_swaps(s.solution, entry)), s.check)
            assert not got.passed, step_id

    def test_the_checks_say_what_to_fix_not_just_that_it_failed(self) -> None:
        move = BY_ID["pyinv-02-move"]
        got = run_py_check(_swap(move.solution, "cannon.speed * dt", "cannon.speed / 60"), move.check)
        assert "30 frames a second" in got.message

        bullet = BY_ID["pyinv-03-bullet"]
        got = run_py_check(_swap(bullet.solution, "    if ' ' in keys and bullet is None:", "    if ' ' in keys:"),
                           bullet.check)
        assert "only one in the air" in got.message or "one in the air" in got.message
        got = run_py_check(_swap(bullet.solution, "    if bullet.y + bullet.h < 0:\n        bullet = None", "    pass"),
                           bullet.check)
        assert "bullet = None" in got.message
        got = run_py_check(_swap(bullet.solution, "def fire():\n    global bullet\n", "def fire():\n"), bullet.check)
        assert "UnboundLocalError" in got.message or "bullet" in got.message
        assert "line" in got.message

        aliens = BY_ID["pyinv-04-aliens"]
        got = run_py_check(_swap(aliens.solution, _ALIEN_LIST, "aliens = [Alien(40, 40, 0, 0, '#fc8181')] * 40\n"),
                           aliens.check)
        assert "forty times" in got.message

        march = BY_ID["pyinv-05-march"]
        got = run_py_check(_swap(march.solution, "direction * ALIEN_SPEED * dt", "ALIEN_SPEED * dt"), march.check)
        assert "direction" in got.message

        edges = BY_ID["pyinv-06-edges"]
        got = run_py_check(_swap(edges.solution, "        direction = -direction\n", ""), edges.check)
        assert "Turn round" in got.message or "turning" in got.message
        got = run_py_check(_swap(edges.solution, "any(a.x + a.w > WIDTH for a in aliens)",
                                 "aliens[0].x + 276 > WIDTH"), edges.check)
        assert "STILL THERE" in got.message or "right edge" in got.message
        got = run_py_check(_swap(edges.solution, "def march(dt):\n    global direction\n", "def march(dt):\n"),
                           edges.check)
        assert "UnboundLocalError" in got.message and "line" in got.message

        shoot = BY_ID["pyinv-07-shoot"]
        got = run_py_check(_swap(shoot.solution, _HIT_BODY,
                                 "    for a in aliens:\n        if overlap(bullet, a):\n            aliens.remove(a)\n"
                                 "            bullet = None\n            score += ROW_POINTS[a.row]"), shoot.check)
        assert "line" in got.message
        got = run_py_check(_swap(shoot.solution, "sum(ROW_POINTS[a.row] for a in hit)", "10 * len(hit)"), shoot.check)
        assert "ROW_POINTS[a.row]" in got.message

        faster = BY_ID["pyinv-08-faster"]
        got = run_py_check(_swap(faster.solution, K._SPEED8, "def march_speed():\n    return ALIEN_SPEED"),
                           faster.check)
        assert "times as fast" in got.message

        bombs = BY_ID["pyinv-09-bombs"]
        got = run_py_check(_swap(bombs.solution, "    shooter = random.choice(list(bottoms.values()))",
                                 "    shooter = random.choice(aliens)"), bombs.check)
        assert "lowest alien" in got.message

        lives = BY_ID["pyinv-10-lives"]
        got = run_py_check(_swap(lives.solution, "        bombs = [b for b in bombs if b not in hit]\n", ""),
                           lives.check)
        assert "ONE life" in got.message or "removed" in got.message
        got = run_py_check(_swap(lives.solution, _GUARD + "    move_cannon", "    move_cannon"), lives.check)
        assert "state != 'playing'" in got.message

        waves = BY_ID["pyinv-11-waves"]
        got = run_py_check(_swap(waves.solution, _WIN, ""), waves.check)
        assert "start the next wave" in got.message

        restart = BY_ID["pyinv-12-restart"]
        got = run_py_check(_swap(restart.solution, "    global score, lives, state\n", "    global score, lives\n"),
                           restart.check)
        assert "global state" in got.message

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

    @pytest.mark.skipif(not _REGISTERED, reason="PYINVADERS_STEPS is not in canvas/__init__.py STEPS yet")
    def test_the_open_step_always_passes(self) -> None:
        got = check_step(STEPS[-1].id, "")
        assert got is not None and got.passed

    @pytest.mark.skipif(not _REGISTERED, reason="PYINVADERS_STEPS is not in canvas/__init__.py STEPS yet")
    def test_check_step_runs_a_python_step_through_the_python_harness(self) -> None:
        s = STEPS[3]
        assert check_step(s.id, s.solution).passed
        assert not check_step(s.id, s.starter).passed
