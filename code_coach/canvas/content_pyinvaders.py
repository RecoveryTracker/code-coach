"""Space Invaders in Python: a game with no JavaScript twin, so its steps are designed for Python.

A cannon at the bottom slides left and right and fires one bullet at a time; a
formation of aliens marches sideways as one block, drops a row and turns round
whenever any alien touches an edge, and speeds up as it thins out; the aliens
rain bombs from the bottom of a random column; a bomb on the cannon costs a
life; an alien on the cannon's row ends the game; clear the formation and the
next wave is faster; Enter starts over. The parts are Python's own:

  * Cannon, Bullet, Alien and Bomb are `@dataclass` classes (a dict with the
    same keys works too, and every check accepts both)
  * the formation is one list comprehension with two `for` clauses and
    `enumerate` over the row colours; `[Alien(...)] * 40` and `[[0] * 8] * 5`
    are the aliasing traps (`itertools.product` is the other way to write it)
  * `any(a.x < 0 for a in aliens)`, `min`/`max` over a generator, and checking
    only the edge the block is heading for
  * the bullet is `None` or a Bullet (`is None`), so "one at a time" is a
    single test, and `global` is written only where a function re-binds a
    top-level name
  * dead aliens, bullets and bombs are *filtered out* with comprehensions,
    never `remove()`d from the list a `for` is walking
  * the bombs come from `bottoms = {}`, a dict keyed by column holding the
    lowest alien of each, and `random.choice(list(bottoms.values()))`; `every`
    drops them on a timer in game seconds
  * f-strings for the HUD, `sum(...)` for points, tuple unpacking for
    constants, a score table indexed by row

As in the other tracks, each step starts from the one before, finished, and a
check plays the game rather than reading the code. The checks read these
top-level names, and set them: cannon, bullet, aliens, direction, score,
bombs, lives, state, wave. `bullet`, `aliens`, `direction`, `score`, `bombs`,
`lives`, `state` and `wave` are re-bound by the program, so a check always
looks them up again rather than holding on to one.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

TRACK = "Space Invaders (Python)"

# -- Shared check helpers ---------------------------------------------------

#: Prepended to every check. A thing's fields can be a dict's or an object's,
#: so a check reads them with get() and writes them with put(), and never
#: cares which the learner chose. C() looks the cannon up afresh. fire_now()
#: fires a real bullet; kill(a) shoots alien a for real (a bullet put on it and
#: one tiny frame, so nothing moves while the hit is decided); shift() moves the
#: whole block; speed_now() measures the pixels a second the block marches at.
#: Dataclasses compare by value, so a check asks alive() (is this very object
#: still in the list) and never `in`.
_HELPERS = """import re


def get(o, k, default=None):
    if isinstance(o, dict):
        return o.get(k, default)
    return getattr(o, k, default)


def put(o, k, v):
    if isinstance(o, dict):
        o[k] = v
    else:
        setattr(o, k, v)


def C():
    return g.cannon


def mid(o):
    return get(o, 'x') + get(o, 'w') / 2


def alive(o, items):
    return any(x is o for x in items)


def fire_now():
    cc.press(' ')
    cc.frames(1, 1 / 30)
    cc.release(' ')
    expect(g.bullet is not None, "Holding Space for a frame should fire a bullet: bullet should become a Bullet (or a dict), not stay None.")
    return g.bullet


def kill(a):
    if 'lives' in g:
        g.lives = 99
    if 'state' in g:
        g.state = 'playing'
    g.bullet = None
    b = fire_now()
    put(b, 'x', mid(a) - get(b, 'w') / 2)
    put(b, 'y', get(a, 'y') + get(a, 'h') - 2)
    cc.frames(1, 0.001)
    expect(not alive(a, g.aliens), "A bullet sitting right on an alien did not take that alien out of aliens.")


def block_left():
    return min(get(a, 'x') for a in g.aliens)


def shift(dx, dy=0):
    for a in g.aliens:
        put(a, 'x', get(a, 'x') + dx)
        put(a, 'y', get(a, 'y') + dy)


def speed_now():
    shift(100 - block_left())
    g.direction = 1
    x0 = [get(a, 'x') for a in g.aliens]
    cc.frames(6, 1 / 30)
    x1 = [get(a, 'x') for a in g.aliens]
    return sum(b - a for a, b in zip(x0, x1)) / len(x0) / 0.2


"""

# -- The programs -----------------------------------------------------------

_I0 = "from canvas import ctx, WIDTH, HEIGHT, on_frame"
_I1 = "from dataclasses import dataclass\n\nfrom canvas import ctx, WIDTH, HEIGHT, on_frame"
_I2 = "from dataclasses import dataclass\n\nfrom canvas import ctx, WIDTH, HEIGHT, on_frame, keys"
_I9 = (
    "import random\nfrom dataclasses import dataclass\n\n"
    "from canvas import ctx, WIDTH, HEIGHT, on_frame, keys, every"
)
_I12 = (
    "import random\nfrom dataclasses import dataclass\n\n"
    "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down, keys, every"
)

_K4 = "COLS = 8\nROW_COLORS = ['#fc8181', '#f6ad55', '#f6e05e', '#68d391', '#63b3ed']"
_K5 = _K4 + "\nALIEN_SPEED = 40"
_K6 = _K5 + "\nDROP = 16"
_K7 = _K6 + "\nROW_POINTS = [30, 20, 20, 10, 10]"
_K8 = _K7 + "\nTOTAL = len(ROW_COLORS) * COLS"
_K9 = _K8 + "\nBOMB_EVERY = 0.8"

_CLASS_CANNON = """@dataclass
class Cannon:
    x: float
    y: float
    w: float
    h: float
    speed: float = 240"""

_CLASS_BULLET = """@dataclass
class Bullet:
    x: float
    y: float
    w: float
    h: float
    vy: float = -360"""

_CLASS_ALIEN = """@dataclass
class Alien:
    x: float
    y: float
    row: int
    col: int
    color: str
    w: float = 24
    h: float = 16"""

_CLASS_BOMB = """@dataclass
class Bomb:
    x: float
    y: float
    w: float
    h: float
    vy: float = 150"""

_MAKE_ALIENS = """def make_aliens():
    return [
        Alien(40 + col * 36, 40 + row * 26, row, col, color)
        for row, color in enumerate(ROW_COLORS)
        for col in range(COLS)
    ]"""

_N_CANNON = "cannon = Cannon(222, 296, 36, 12)"
_N_BULLET = "bullet = None"
_N_ALIENS = """aliens = [
    Alien(40 + col * 36, 40 + row * 26, row, col, color)
    for row, color in enumerate(ROW_COLORS)
    for col in range(COLS)
]"""
_N_ALIENS_CALL = "aliens = make_aliens()"
_N_DIRECTION = "direction = 1"
_N_SCORE = "score = 0"
_N_BOMBS = "bombs = []"
_N_LIVES = "lives = 3"
_N_STATE = "state = 'playing'"
_N_WAVE = "wave = 1"

_MOVE_CANNON = """def move_cannon(dt):
    if 'ArrowLeft' in keys:
        cannon.x -= cannon.speed * dt
    if 'ArrowRight' in keys:
        cannon.x += cannon.speed * dt
    cannon.x = max(0, min(WIDTH - cannon.w, cannon.x))"""

_FIRE = """def fire():
    global bullet
    if ' ' in keys and bullet is None:
        bullet = Bullet(cannon.x + cannon.w / 2 - 2, cannon.y - 10, 4, 10)"""

_MOVE_BULLET = """def move_bullet(dt):
    global bullet
    if bullet is None:
        return
    bullet.y += bullet.vy * dt
    if bullet.y + bullet.h < 0:
        bullet = None"""

_MARCH5 = """def march(dt):
    for a in aliens:
        a.x += direction * ALIEN_SPEED * dt"""

_MARCH6 = """def march(dt):
    global direction
    for a in aliens:
        a.x += direction * ALIEN_SPEED * dt
    at_right = direction > 0 and any(a.x + a.w > WIDTH for a in aliens)
    at_left = direction < 0 and any(a.x < 0 for a in aliens)
    if at_right or at_left:
        direction = -direction
        for a in aliens:
            a.y += DROP"""

_MARCH8 = """def march(dt):
    global direction
    step = direction * march_speed() * dt
    for a in aliens:
        a.x += step
    at_right = direction > 0 and any(a.x + a.w > WIDTH for a in aliens)
    at_left = direction < 0 and any(a.x < 0 for a in aliens)
    if at_right or at_left:
        direction = -direction
        for a in aliens:
            a.y += DROP"""

_SPEED8 = """def march_speed():
    return ALIEN_SPEED + 3 * (TOTAL - len(aliens))"""

_SPEED11 = """def march_speed():
    return ALIEN_SPEED + 10 * (wave - 1) + 3 * (TOTAL - len(aliens))"""

_OVERLAP = """def overlap(a, b):
    return a.x < b.x + b.w and a.x + a.w > b.x and a.y < b.y + b.h and a.y + a.h > b.y"""

_HIT_ALIENS = """def hit_aliens():
    global bullet, aliens, score
    if bullet is None:
        return
    hit = [a for a in aliens if overlap(bullet, a)]
    if hit:
        aliens = [a for a in aliens if a not in hit]
        bullet = None
        score += sum(ROW_POINTS[a.row] for a in hit)"""

_DROP_BOMB9 = """def drop_bomb():
    if not aliens:
        return
    bottoms = {}
    for a in aliens:
        low = bottoms.get(a.col)
        if low is None or a.y > low.y:
            bottoms[a.col] = a
    shooter = random.choice(list(bottoms.values()))
    bombs.append(Bomb(shooter.x + shooter.w / 2 - 2, shooter.y + shooter.h, 4, 10))"""

_DROP_BOMB10 = _DROP_BOMB9.replace("    if not aliens:\n", "    if state != 'playing' or not aliens:\n")

_MOVE_BOMBS = """def move_bombs(dt):
    global bombs
    for b in bombs:
        b.y += b.vy * dt
    bombs = [b for b in bombs if b.y < HEIGHT]"""

_HIT_CANNON = """def hit_cannon():
    global bombs, lives
    hit = [b for b in bombs if overlap(b, cannon)]
    if hit:
        bombs = [b for b in bombs if b not in hit]
        lives = max(0, lives - len(hit))"""

_CHECK_OVER = """def check_over():
    global state
    if lives <= 0 or any(a.y + a.h >= cannon.y for a in aliens):
        state = 'over'"""

_START_WAVE = """def start_wave(n):
    global aliens, bombs, bullet, direction, wave
    wave = n
    aliens = make_aliens()
    bombs = []
    bullet = None
    direction = 1"""

_RESTART = """def restart():
    global score, lives, state
    score = 0
    lives = 3
    state = 'playing'
    cannon.x = WIDTH / 2 - cannon.w / 2
    start_wave(1)"""

_KEYS12 = """def key_down(key):
    if key == 'Enter' and state == 'over':
        restart()


on_key_down(key_down)"""

_UPDATE_PASS = """def update(dt):
    pass"""

_UPDATE2 = """def update(dt):
    move_cannon(dt)"""

_UPDATE3 = """def update(dt):
    move_cannon(dt)
    fire()
    move_bullet(dt)"""

_UPDATE5 = """def update(dt):
    move_cannon(dt)
    fire()
    move_bullet(dt)
    march(dt)"""

_UPDATE7 = """def update(dt):
    move_cannon(dt)
    fire()
    move_bullet(dt)
    march(dt)
    hit_aliens()"""

_UPDATE9 = """def update(dt):
    move_cannon(dt)
    fire()
    move_bullet(dt)
    march(dt)
    hit_aliens()
    move_bombs(dt)"""

_UPDATE10 = """def update(dt):
    if state != 'playing':
        return
    move_cannon(dt)
    fire()
    move_bullet(dt)
    march(dt)
    hit_aliens()
    move_bombs(dt)
    hit_cannon()
    check_over()"""

_UPDATE11 = """def update(dt):
    if state != 'playing':
        return
    move_cannon(dt)
    fire()
    move_bullet(dt)
    march(dt)
    hit_aliens()
    if not aliens:
        start_wave(wave + 1)
    move_bombs(dt)
    hit_cannon()
    check_over()"""

_LOOP = """def loop(dt):
    update(dt)
    draw()


on_frame(loop)"""

_LOOP9 = _LOOP + "\nevery(BOMB_EVERY, drop_bomb)"

_D_BG = "    ctx.fill_style = '#10141f'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n"
_D_CANNON = (
    "    ctx.fill_style = '#4fd1c5'\n    ctx.fill_rect(cannon.x, cannon.y, cannon.w, cannon.h)\n"
    "    ctx.fill_rect(cannon.x + cannon.w / 2 - 2, cannon.y - 6, 4, 6)\n"
)
_D_BULLET = (
    "    if bullet is not None:\n        ctx.fill_style = 'white'\n"
    "        ctx.fill_rect(bullet.x, bullet.y, bullet.w, bullet.h)\n"
)
_D_ALIENS = "    for a in aliens:\n        ctx.fill_style = a.color\n        ctx.fill_rect(a.x, a.y, a.w, a.h)\n"
_D_BOMBS = "    for b in bombs:\n        ctx.fill_style = '#faf089'\n        ctx.fill_rect(b.x, b.y, b.w, b.h)\n"
_HUD7 = (
    "    ctx.fill_style = 'white'\n    ctx.font = '16px monospace'\n"
    "    ctx.fill_text(f'Score: {score}', 10, 20)\n"
)
_HUD_WAVE = "    ctx.fill_text(f'Wave {wave}', 215, 20)\n"
_HUD_LIVES = "    ctx.fill_text(f'Lives: {lives}', 390, 20)\n"
_HUD_OVER = "    if state == 'over':\n        ctx.font = '32px monospace'\n        ctx.fill_text('Game over', 150, 200)\n"
_HUD_ENTER = "        ctx.font = '16px monospace'\n        ctx.fill_text('Press Enter to play again', 130, 230)\n"
_HUD10 = _HUD7 + _HUD_LIVES + _HUD_OVER
_HUD11 = _HUD7 + _HUD_WAVE + _HUD_LIVES + _HUD_OVER
_HUD12 = _HUD11 + _HUD_ENTER


def _draw(*parts: str) -> str:
    return "def draw():\n" + "\n".join(parts)


def _program(imports: str, consts: str, classes: tuple[str, ...], names: tuple[str, ...], *funcs: str) -> str:
    """One whole program: imports, constants, classes, the game's names, then each function."""
    blocks = [imports]
    if consts:
        blocks.append(consts)
    blocks.extend(classes)
    if names:
        blocks.append("\n".join(names))
    blocks.extend(funcs)
    return "\n\n\n".join(b.strip("\n") for b in blocks) + "\n"


_NONE: tuple[str, ...] = ()

_P0 = _program(_I0, "", _NONE, _NONE, _UPDATE_PASS, _draw(_D_BG), _LOOP)

_P1 = _program(
    _I1, "", (_CLASS_CANNON,), (_N_CANNON,),
    _UPDATE_PASS, _draw(_D_BG, _D_CANNON), _LOOP,
)

_P2 = _program(
    _I2, "", (_CLASS_CANNON,), (_N_CANNON,),
    _MOVE_CANNON, _UPDATE2, _draw(_D_BG, _D_CANNON), _LOOP,
)

_P3 = _program(
    _I2, "", (_CLASS_CANNON, _CLASS_BULLET), (_N_CANNON, _N_BULLET),
    _MOVE_CANNON, _FIRE, _MOVE_BULLET, _UPDATE3,
    _draw(_D_BG, _D_CANNON, _D_BULLET), _LOOP,
)

_P4 = _program(
    _I2, _K4, (_CLASS_CANNON, _CLASS_BULLET, _CLASS_ALIEN), (_N_CANNON, _N_BULLET, _N_ALIENS),
    _MOVE_CANNON, _FIRE, _MOVE_BULLET, _UPDATE3,
    _draw(_D_BG, _D_ALIENS, _D_CANNON, _D_BULLET), _LOOP,
)

_P5 = _program(
    _I2, _K5, (_CLASS_CANNON, _CLASS_BULLET, _CLASS_ALIEN), (_N_CANNON, _N_BULLET, _N_ALIENS, _N_DIRECTION),
    _MOVE_CANNON, _FIRE, _MOVE_BULLET, _MARCH5, _UPDATE5,
    _draw(_D_BG, _D_ALIENS, _D_CANNON, _D_BULLET), _LOOP,
)

_P6 = _program(
    _I2, _K6, (_CLASS_CANNON, _CLASS_BULLET, _CLASS_ALIEN), (_N_CANNON, _N_BULLET, _N_ALIENS, _N_DIRECTION),
    _MOVE_CANNON, _FIRE, _MOVE_BULLET, _MARCH6, _UPDATE5,
    _draw(_D_BG, _D_ALIENS, _D_CANNON, _D_BULLET), _LOOP,
)

_P7 = _program(
    _I2, _K7, (_CLASS_CANNON, _CLASS_BULLET, _CLASS_ALIEN),
    (_N_CANNON, _N_BULLET, _N_ALIENS, _N_DIRECTION, _N_SCORE),
    _MOVE_CANNON, _FIRE, _MOVE_BULLET, _MARCH6, _OVERLAP, _HIT_ALIENS, _UPDATE7,
    _draw(_D_BG, _D_ALIENS, _D_CANNON, _D_BULLET, _HUD7), _LOOP,
)

_P8 = _program(
    _I2, _K8, (_CLASS_CANNON, _CLASS_BULLET, _CLASS_ALIEN),
    (_N_CANNON, _N_BULLET, _N_ALIENS, _N_DIRECTION, _N_SCORE),
    _MOVE_CANNON, _FIRE, _MOVE_BULLET, _SPEED8, _MARCH8, _OVERLAP, _HIT_ALIENS, _UPDATE7,
    _draw(_D_BG, _D_ALIENS, _D_CANNON, _D_BULLET, _HUD7), _LOOP,
)

_P9 = _program(
    _I9, _K9, (_CLASS_CANNON, _CLASS_BULLET, _CLASS_ALIEN, _CLASS_BOMB),
    (_N_CANNON, _N_BULLET, _N_ALIENS, _N_DIRECTION, _N_SCORE, _N_BOMBS),
    _MOVE_CANNON, _FIRE, _MOVE_BULLET, _SPEED8, _MARCH8, _OVERLAP, _HIT_ALIENS,
    _DROP_BOMB9, _MOVE_BOMBS, _UPDATE9,
    _draw(_D_BG, _D_ALIENS, _D_CANNON, _D_BULLET, _D_BOMBS, _HUD7), _LOOP9,
)

_P10 = _program(
    _I9, _K9, (_CLASS_CANNON, _CLASS_BULLET, _CLASS_ALIEN, _CLASS_BOMB),
    (_N_CANNON, _N_BULLET, _N_ALIENS, _N_DIRECTION, _N_SCORE, _N_BOMBS, _N_LIVES, _N_STATE),
    _MOVE_CANNON, _FIRE, _MOVE_BULLET, _SPEED8, _MARCH8, _OVERLAP, _HIT_ALIENS,
    _DROP_BOMB10, _MOVE_BOMBS, _HIT_CANNON, _CHECK_OVER, _UPDATE10,
    _draw(_D_BG, _D_ALIENS, _D_CANNON, _D_BULLET, _D_BOMBS, _HUD10), _LOOP9,
)

_P11 = _program(
    _I9, _K9, (_CLASS_CANNON, _CLASS_BULLET, _CLASS_ALIEN, _CLASS_BOMB, _MAKE_ALIENS),
    (_N_CANNON, _N_BULLET, _N_ALIENS_CALL, _N_DIRECTION, _N_SCORE, _N_BOMBS, _N_LIVES, _N_STATE, _N_WAVE),
    _MOVE_CANNON, _FIRE, _MOVE_BULLET, _SPEED11, _MARCH8, _OVERLAP, _HIT_ALIENS,
    _DROP_BOMB10, _MOVE_BOMBS, _HIT_CANNON, _CHECK_OVER, _START_WAVE, _UPDATE11,
    _draw(_D_BG, _D_ALIENS, _D_CANNON, _D_BULLET, _D_BOMBS, _HUD11), _LOOP9,
)

_P12 = _program(
    _I12, _K9, (_CLASS_CANNON, _CLASS_BULLET, _CLASS_ALIEN, _CLASS_BOMB, _MAKE_ALIENS),
    (_N_CANNON, _N_BULLET, _N_ALIENS_CALL, _N_DIRECTION, _N_SCORE, _N_BOMBS, _N_LIVES, _N_STATE, _N_WAVE),
    _MOVE_CANNON, _FIRE, _MOVE_BULLET, _SPEED11, _MARCH8, _OVERLAP, _HIT_ALIENS,
    _DROP_BOMB10, _MOVE_BOMBS, _HIT_CANNON, _CHECK_OVER, _START_WAVE, _RESTART, _KEYS12, _UPDATE11,
    _draw(_D_BG, _D_ALIENS, _D_CANNON, _D_BULLET, _D_BOMBS, _HUD12), _LOOP9,
)

# -- The checks ---------------------------------------------------------------

_CHECK1 = _HELPERS + """
expect('cannon' in g, "Make the cannon: cannon = Cannon(222, 296, 36, 12) (or a dict with x, y, w and h) - a name in your code, outside any function.")
c = g.cannon
expect(get(c, 'x') == 222 and get(c, 'y') == 296 and get(c, 'w') == 36 and get(c, 'h') == 12, "The cannon should start at x 222, y 296, 36 wide and 12 tall - low and in the middle. The order matters: Cannon(x, y, w, h).")
expect(get(c, 'speed') == 240, "Give the cannon a speed of 240 pixels a second: a field speed with a default, speed: float = 240.")
cc.frames(1)
rects = cc.rects()
expect(rects and rects[0]['x'] == 0 and rects[0]['y'] == 0 and rects[0]['w'] >= WIDTH and rects[0]['h'] >= HEIGHT, "Each frame should start by painting the background over the whole canvas.")
at = [i for i, r in enumerate(rects) if near(r['x'], get(c, 'x'), 0.01) and near(r['y'], get(c, 'y'), 0.01) and r['w'] == get(c, 'w') and r['h'] == get(c, 'h')]
expect(at, "Draw the cannon every frame, inside draw(): ctx.fill_rect(cannon.x, cannon.y, cannon.w, cannon.h).")
expect(at[0] > 0, "The cannon has to be drawn after the background, or the background paints over it.")
expect(rects[at[0]]['fill'] != rects[0]['fill'], "The cannon is the same colour as the background, so you cannot see it. Set fill_style again before drawing the cannon.")
"""

_CHECK2 = _HELPERS + """
expect('cannon' in g, "Keep the cannon from the last step.")
x0 = get(C(), 'x')
cc.frames(30)
expect(near(get(C(), 'x'), x0, 0.01), "The cannon moves on its own. It should stand still until an arrow key is held.")
for dt, n in ((1 / 30, 15), (1 / 60, 30)):
    fps = round(1 / dt)
    put(C(), 'x', 200)
    cc.press('ArrowRight')
    cc.frames(n, dt)
    cc.release('ArrowRight')
    moved = get(C(), 'x') - 200
    expect(near(moved, 120, 6), f"At {fps} frames a second, half a second of ArrowRight moved the cannon {round(moved)} pixels; at a speed of 240 a second it should be about 120. Ask `keys` with `in` and move by cannon.speed * dt - dt is seconds, so the frame rate stops mattering.")
    cc.press('ArrowLeft')
    cc.frames(n, dt)
    cc.release('ArrowLeft')
    expect(near(get(C(), 'x'), 200, 6), f"At {fps} frames a second, half a second of ArrowLeft moved the cannon to x {round(get(C(), 'x'))}; it should be back near 200, the same speed the other way.")
x1 = get(C(), 'x')
cc.frames(30)
expect(near(get(C(), 'x'), x1, 0.01), "The cannon kept going after the key was let go. Move it only while the key is in `keys`.")
cc.press('ArrowRight')
cc.frames(120, 1 / 30)
cc.release('ArrowRight')
expect(near(get(C(), 'x'), WIDTH - get(C(), 'w'), 0.01), f"After four seconds of ArrowRight the cannon is at x {round(get(C(), 'x'))}. It should stop with its right edge on the canvas edge: x = WIDTH - cannon.w. Clamp with max(0, min(WIDTH - cannon.w, cannon.x)).")
cc.press('ArrowLeft')
cc.frames(240, 1 / 30)
cc.release('ArrowLeft')
expect(near(get(C(), 'x'), 0, 0.01), f"After eight seconds of ArrowLeft the cannon is at x {round(get(C(), 'x'))}. It should stop at 0.")
cc.frames(1)
expect(any(near(r['x'], get(C(), 'x'), 0.01) and r['y'] == get(C(), 'y') and r['w'] == get(C(), 'w') for r in cc.rects()), "Keep drawing the cannon every frame, where it is now.")
"""

_CHECK3 = _HELPERS + """
expect('bullet' in g and g.bullet is None, "Start with bullet = None - nothing in the air yet. It is a name in your code, outside any function.")
cc.frames(10, 1 / 30)
expect(g.bullet is None, "A bullet appeared with nobody pressing Space.")
cc.press(' ')
cc.frames(1, 1 / 30)
b = g.bullet
expect(b is not None, "Holding Space for a frame should make a bullet: in fire(), when ' ' is in keys and bullet is None, set bullet = Bullet(...).")
expect(near(mid(b), mid(C()), 3), f"The bullet should come out of the middle of the cannon (x {round(mid(C()))}), but it is at x {round(mid(b))}.")
expect(get(b, 'w') == 4 and get(b, 'h') == 10, "A bullet is 4 wide and 10 tall: Bullet(x, y, 4, 10).")
expect(get(b, 'y') + get(b, 'h') <= get(C(), 'y') + 1, "The bullet should start above the cannon, flying up, not below its top edge. Try y = cannon.y - 10.")
y1 = get(b, 'y')
for _ in range(6):
    cc.frames(1, 1 / 30)
    expect(g.bullet is not None, "The bullet disappeared after a fifth of a second. It should fly on until it leaves the top of the canvas.")
    expect(g.bullet is b, "Holding Space made a new bullet on the very next frame. There must be only one in the air: fire only when bullet is None.")
moved = y1 - get(g.bullet, 'y')
expect(near(moved, 72, 6), f"At 30 frames a second, a fifth of a second of flight moved the bullet {round(moved)} pixels up; at 360 pixels a second it should be about 72. Move it by bullet.vy * dt (vy is -360: negative is up).")
seen = [b]
for _ in range(8):
    cc.frames(1, 1 / 30)
    cur = g.bullet
    if cur is not None and not alive(cur, seen):
        seen.append(cur)
expect(len(seen) == 1, f"Holding Space for half a second made {len(seen)} different bullets. There must be only one in the air: fire only when bullet is None.")
first = seen[0]
last_y = get(first, 'y')
fresh = None
for _ in range(70):
    cc.frames(1, 1 / 30)
    cur = g.bullet
    if cur is first:
        last_y = get(first, 'y')
    elif cur is not None:
        fresh = cur
        break
expect(fresh is not None, "The bullet left the top of the canvas but Space (still held) never fired another. When the bullet is out of sight, give it back: bullet = None.")
expect(last_y < 30, f"A new bullet was fired while the old one was still at y {round(last_y)}, well inside the canvas. The next shot has to wait until the last one has left the top.")
cc.frames(1, 1 / 30)
cur = g.bullet
expect(cur is not None and any(near(r['x'], get(cur, 'x'), 0.01) and near(r['y'], get(cur, 'y'), 0.01) and r['w'] == get(cur, 'w') and r['h'] == get(cur, 'h') for r in cc.rects()), "Draw the bullet every frame while there is one: if bullet is not None: ctx.fill_rect(bullet.x, bullet.y, bullet.w, bullet.h).")
cc.release(' ')
cc.frames(80, 1 / 30)
expect(g.bullet is None, "With Space let go, the bullet should fly off the top and nothing should take its place. Is it given back (bullet = None) once it has left?")
cc.press(' ')
cc.frames(1)
cc.release(' ')
b = g.bullet
expect(b is not None, "Space fires again once the last bullet has gone.")
y1 = get(b, 'y')
cc.frames(12)
expect(g.bullet is b and near(y1 - get(b, 'y'), 72, 6), "At 60 frames a second the bullet is not where bullet.vy * dt puts it: 12 frames of 1/60 second at 360 pixels a second is 72 pixels.")
"""

_CHECK4 = _HELPERS + """
expect('aliens' in g and isinstance(g.aliens, list), "Make a list called aliens - a name in your code, outside any function.")
al = g.aliens
expect(len(al) == 40, f"There are {len(al)} aliens; 5 rows of 8 is 40. A comprehension with two for clauses (for row ... for col ...) makes them.")
places = {(get(a, 'x'), get(a, 'y')) for a in al}
expect(len(places) == 40, "Some aliens are on top of each other - x should come from the column and y from the row. (And [Alien(...)] * 40 is ONE alien forty times: the list holds forty names for the same object.)")
expect(len({id(a) for a in al}) == 40, "The list holds the same alien more than once. [Alien(...)] * 40 (or [[...] * 8] * 5) copies the reference, not the alien - build every alien inside the comprehension.")
xs = {get(a, 'x') for a in al}
ys = {get(a, 'y') for a in al}
expect(xs == {40 + c * 36 for c in range(8)} and ys == {40 + r * 26 for r in range(5)}, "The aliens should make a grid: x is 40 + col * 36 for 8 columns, y is 40 + row * 26 for 5 rows.")
expect(all(get(a, 'w') == 24 and get(a, 'h') == 16 for a in al), "Every alien is 24 wide and 16 tall (defaults on the dataclass).")
expect(all(get(a, 'row') == round((get(a, 'y') - 40) / 26) and get(a, 'col') == round((get(a, 'x') - 40) / 36) for a in al), "Every alien needs its own row and col: row 0 is the top row, col 0 the left column. Later steps score by row and drop bombs by column.")
cc.frames(1)
rects = cc.rects()
bg = max((i for i, r in enumerate(rects) if r['x'] == 0 and r['y'] == 0 and r['w'] >= WIDTH and r['h'] >= HEIGHT), default=-1)
expect(bg >= 0, "Each frame should start by painting the background over the whole canvas.")
fills = {}
for a in al:
    got = [(i, r) for i, r in enumerate(rects) if r['x'] == get(a, 'x') and r['y'] == get(a, 'y') and r['w'] == get(a, 'w') and r['h'] == get(a, 'h')]
    expect(got, "Draw every alien each frame: for a in aliens: ctx.fill_rect(a.x, a.y, a.w, a.h).")
    expect(got[0][0] > bg, "The aliens have to be drawn after the background, or the background paints over them.")
    fills.setdefault(get(a, 'row'), set()).add(got[0][1]['fill'])
expect(all(len(f) == 1 for f in fills.values()), "Every alien in a row should be the same colour: pick it from ROW_COLORS by the row.")
expect(len({next(iter(f)) for f in fills.values()}) == 5, "Give each row its own colour: five rows, five colours in ROW_COLORS.")
"""

_CHECK5 = _HELPERS + """
expect('direction' in g and g.direction == 1, "Add direction = 1: 1 means right, -1 means left. A name in your code, outside any function.")
al = list(g.aliens)
expect(len(al) == 40, "Keep the 40 aliens from the last step.")
home = [(get(a, 'x'), get(a, 'y')) for a in al]


def back():
    for a, (x, y) in zip(al, home):
        put(a, 'x', x)
        put(a, 'y', y)


for dt, n in ((1 / 30, 6), (1 / 60, 12)):
    fps = round(1 / dt)
    back()
    g.direction = 1
    cc.frames(n, dt)
    dxs = [get(a, 'x') - x for a, (x, y) in zip(al, home)]
    expect(all(near(d, 8, 1.2) for d in dxs), f"At {fps} frames a second, a fifth of a second moved the aliens {round(min(dxs), 1)} to {round(max(dxs), 1)} pixels to the right; at ALIEN_SPEED = 40 pixels a second it should be 8. Move every alien by direction * ALIEN_SPEED * dt.")
    expect(max(dxs) - min(dxs) < 0.01, "The aliens march as ONE block: every alien moves by the same amount. Loop over all of aliens.")
    expect(all(near(get(a, 'y'), y, 0.01) for a, (x, y) in zip(al, home)), "The aliens drift up or down. For now they only march sideways.")
back()
g.direction = -1
cc.frames(6, 1 / 30)
dxs = [get(a, 'x') - x for a, (x, y) in zip(al, home)]
expect(all(near(d, -8, 1.2) for d in dxs), f"With direction = -1 the block should march LEFT at the same speed; it moved {round(sum(dxs) / 40, 1)} pixels in a fifth of a second. Multiply by direction: a.x += direction * ALIEN_SPEED * dt.")
cc.frames(1)
expect(any(near(r['x'], get(al[5], 'x'), 0.01) and near(r['y'], get(al[5], 'y'), 0.01) for r in cc.rects()), "Keep drawing the aliens every frame, where they are now.")
"""

_CHECK6 = _HELPERS + """
expect('direction' in g and g.direction in (1, -1), "Keep direction from the last step: 1 for right, -1 for left.")
al0 = list(g.aliens)
expect(len(al0) == 40, "Keep the 40 aliens from the last step.")
home = [(get(a, 'x'), get(a, 'y')) for a in al0]


def reset(keep=None):
    for a, (x, y) in zip(al0, home):
        put(a, 'x', x)
        put(a, 'y', y)
    g.aliens = [a for a in al0 if keep is None or keep(a)]


def right_edge():
    return max(get(a, 'x') + get(a, 'w') for a in g.aliens)


def left_edge():
    return min(get(a, 'x') for a in g.aliens)


def top():
    return min(get(a, 'y') for a in g.aliens)


def run_to_turn(heading, frames=80):
    g.direction = heading
    ys = {id(a): get(a, 'y') for a in g.aliens}
    for _ in range(frames):
        cc.frames(1, 1 / 30)
        if any(abs(get(a, 'y') - ys[id(a)]) > 0.01 for a in g.aliens):
            drops = [get(a, 'y') - ys[id(a)] for a in g.aliens]
            expect(all(near(d, 16, 0.5) for d in drops), f"The whole block should drop by DROP = 16 pixels together, but the aliens dropped by {sorted(set(round(d, 1) for d in drops))}.")
            return left_edge(), right_edge()
    return None


reset()
shift(WIDTH - 6 - right_edge())
got = run_to_turn(1)
expect(got is not None, "The block marched into the right edge and never dropped. When the right-most alien (max of a.x + a.w) touches WIDTH while the block is heading right, every alien drops by DROP and the block turns round.")
expect(WIDTH - 2 <= got[1] <= WIDTH + 2, f"The block turned when its right edge was at x {round(got[1])}; it should turn when its right-most alien touches the edge of the canvas, at {WIDTH}.")
t1, l1 = top(), left_edge()
cc.frames(15, 1 / 30)
expect(near(top(), t1, 0.01), "The block dropped again straight after turning at the right edge. It should drop once per touch: turn round (direction = -direction) as well as dropping, or it is still over the edge next frame and drops again.")
expect(near(l1 - left_edge(), 20, 3), f"After touching the right edge the block should march LEFT; in half a second it moved {round(l1 - left_edge())} pixels left (about 20 expected). Turn round: direction = -direction.")

reset()
shift(6 - left_edge())
got = run_to_turn(-1)
expect(got is not None, "The block marched into the left edge and never dropped. It has two edges: when the left-most alien (min of a.x) passes 0 while the block is heading left, drop and turn round as well.")
expect(-2 <= got[0] <= 2, f"The block turned when its left edge was at x {round(got[0])}; it should turn when its left-most alien touches the edge of the canvas, at 0.")
t1, r1 = top(), right_edge()
cc.frames(15, 1 / 30)
expect(near(top(), t1, 0.01), "The block dropped again straight after turning at the left edge. Once per touch.")
expect(near(right_edge() - r1, 20, 3), f"After touching the left edge the block should march RIGHT; in half a second it moved {round(right_edge() - r1)} pixels (about 20 expected).")

reset(keep=lambda a: get(a, 'col') < 6)
shift(WIDTH - 30 - right_edge())
got = run_to_turn(1)
expect(got is not None, "With the two right-hand columns shot away the block never turned. The edge is the right-most alien that is STILL THERE: max(a.x + a.w for a in aliens), not a fixed width.")
expect(WIDTH - 2 <= got[1] <= WIDTH + 2, f"With the two right-hand columns gone the block turned with its right edge at x {round(got[1])}; it should march on until the right-most alien left touches {WIDTH}. Work the edge out from the aliens that are left, every frame.")

reset(keep=lambda a: not (get(a, 'row') == 0 and get(a, 'col') < 7))
shift(25 - left_edge())
got = run_to_turn(-1)
expect(got is not None, "The block never turned at the left edge when the left-most aliens were not the first in the list. Look at ALL the aliens: min(a.x for a in aliens), or any(a.x < 0 for a in aliens) - not aliens[0] alone.")
expect(-2 <= got[0] <= 2, f"The block turned with its left edge at x {round(got[0])}; it should turn when the left-most alien that is left touches 0. Do not use the first alien in the list.")

reset()
g.direction = 1
tops = [top()]
lo, hi = left_edge(), right_edge()
for _ in range(360):
    cc.frames(1, 1 / 30)
    lo, hi = min(lo, left_edge()), max(hi, right_edge())
    if not near(top(), tops[-1], 0.01):
        tops.append(top())
expect([round(t) for t in tops] == [40, 56, 72], f"In twelve seconds a block that starts at the top should touch an edge twice and drop twice, 16 pixels each time (tops of the block: {[round(t) for t in tops]}, expected [40, 56, 72]). Drop once per edge touch.")
expect(lo >= -2.5 and hi <= WIDTH + 2.5, f"The block went past the edge of the canvas (x {round(lo)} to {round(hi)}). It should turn round as soon as it touches.")
"""

_CHECK7 = _HELPERS + """
expect('score' in g and isinstance(g.score, (int, float)) and g.score == 0, "Start with score = 0 - a name in your code, outside any function.")
cc.frames(1)
expect(any(re.search('score', t, re.I) and '0' in t for t in cc.texts()), "Show the score on the screen from the start: it should say Score: 0.")
al0 = list(g.aliens)
rows = sorted({get(a, 'y') for a in al0})
expect(len(al0) == 40 and len(rows) == 5, "Keep the 40 aliens in 5 rows from the last steps.")


def row_aliens(r):
    return sorted((a for a in al0 if get(a, 'y') == rows[r]), key=lambda a: get(a, 'x'))


def shot(a, ox, oy):
    g.bullet = None
    b = fire_now()
    put(b, 'x', get(a, 'x') + ox)
    put(b, 'y', get(a, 'y') + oy)
    before = g.score
    n = len(g.aliens)
    cc.frames(1, 0.001)
    return b, n - len(g.aliens), g.score - before


t = row_aliens(4)[3]
b, killed, gained = shot(t, 10, 14)
expect(killed == 1, f"A bullet sitting inside an alien took {killed} aliens out of aliens; it should take out exactly that one. The bullet and alien touch when their boxes overlap: overlap(a, b).")
expect(not alive(t, g.aliens), "An alien was removed, but not the one the bullet hit. Keep every alien that is NOT touching the bullet: aliens = [a for a in aliens if a not in hit].")
expect(len(g.aliens) == 39 and all(alive(a, g.aliens) for a in al0 if a is not t), "Only the alien that was hit should leave the list; the other 39 stay.")
expect(g.bullet is None, "A bullet that hit an alien is used up: set bullet back to None, so Space can fire the next one.")
expect(gained == 10, f"An alien in the bottom row is worth 10; the score went up by {gained}.")
for r, pts in enumerate((30, 20, 20, 10, 10)):
    a = row_aliens(r)[r + 2]
    b, killed, gained = shot(a, 10, 14)
    expect(killed == 1 and gained == pts, f"An alien in row {r} (the top row is row 0) is worth {pts}; the score went up by {gained}. Look the points up by the alien's row: ROW_POINTS[a.row].")
for label, target, ox, oy in (
    ("in the gap beside it (it touches neither box)", row_aliens(2)[5], 28, 14),
    ("1.5 pixels away from its left side", row_aliens(2)[5], -5.5, 14),
    ("far below the bottom of the formation, in its column", row_aliens(4)[7], 10, 54),
    ("above the top row, already past it", row_aliens(0)[6], 10, -15),
):
    b, killed, gained = shot(target, ox, oy)
    expect(killed == 0 and gained == 0 and g.bullet is b, f"A bullet {label} counts as a hit. Compare all four sides: the boxes overlap only if a.x < b.x + b.w and a.x + a.w > b.x and a.y < b.y + b.h and a.y + a.h > b.y.")
b, killed, gained = shot(row_aliens(2)[0], -30, 14)
expect(killed == 0 and gained == 0, "A bullet level with the top rows but far off to the left counts as a hit. The x sides matter as well as the y sides.")
b, killed, gained = shot(row_aliens(2)[5], -3, -9)
expect(killed == 1, "A bullet whose corner overlaps an alien's corner by a pixel should hit it: this is box against box, not the bullet's centre point against the alien.")
cc.frames(1)
expect(any(re.search('score', t, re.I) and str(g.score) in t for t in cc.texts()), f"Show the score on the screen: it should say Score: {g.score}.")
"""

_CHECK8 = _HELPERS + """
expect('direction' in g and 'score' in g, "Keep direction and score from the last steps.")
s_start = speed_now()
expect(near(s_start, 40, 4), f"With all 40 aliens alive the block should march at 40 pixels a second (ALIEN_SPEED); it moves at {round(s_start)}.")
speeds = {40: s_start}
for target in (30, 20, 10, 5, 1):
    while len(g.aliens) > target:
        kill(g.aliens[-1])
    speeds[target] = speed_now()
order = [speeds[n] for n in (40, 30, 20, 10, 5, 1)]
for slower, faster, n in zip(order, order[1:], (30, 20, 10, 5, 1)):
    expect(faster >= slower - 1.5, f"With {n} aliens left the block marches at {round(faster)} pixels a second, no faster than with more of them ({round(slower)}). The fewer aliens are left, the faster they march.")
expect(speeds[20] >= 1.3 * s_start, f"With 20 aliens left the block should march at least 1.3 times as fast as with 40 (40 pixels a second): it goes {round(speeds[20])}.")
expect(speeds[1] >= 3 * s_start, f"With ONE alien left the block should march at least 3 times as fast as at the start (40 pixels a second): it goes {round(speeds[1])}.")
expect(speeds[1] <= 400, f"With one alien left the block marches at {round(speeds[1])} pixels a second - too fast to play. About 150 is plenty.")
shift(100 - block_left())
g.direction = 1
x0 = get(g.aliens[0], 'x')
cc.frames(12)
v = (get(g.aliens[0], 'x') - x0) / 0.2
expect(near(v, speeds[1], speeds[1] * 0.08 + 1), f"At 60 frames a second the last alien marches at {round(v)} pixels a second, at 30 frames a second {round(speeds[1])}. The speed must be pixels a SECOND, whatever the frame rate: multiply by dt.")
"""

_CHECK9 = _HELPERS + """
expect('bombs' in g and isinstance(g.bombs, list), "Make a list called bombs - bombs = [] - a name in your code, outside any function.")
expect(len(g.bombs) == 0, "There should be no bombs before the first drop.")
al0 = list(g.aliens)
home = [(get(a, 'x'), get(a, 'y')) for a in al0]


def restore(keep=None):
    for a, (x, y) in zip(al0, home):
        put(a, 'x', x)
        put(a, 'y', y)
    g.aliens = [a for a in al0 if keep is None or keep(a)]
    g.direction = 1
    g.bombs = []


def new_bombs(seen):
    fresh = []
    for b in g.bombs:
        if id(b) not in seen:
            seen[id(b)] = b
            fresh.append(b)
    return fresh


seen = {}
born = None
for _ in range(90):
    cc.frames(1, 1 / 30)
    f = new_bombs(seen)
    if f:
        born = f[0]
        break
expect(born is not None, "No bomb appeared in three seconds. Start a timer: every(BOMB_EVERY, drop_bomb), with BOMB_EVERY = 0.8, and have drop_bomb() append a Bomb to bombs.")
y0 = get(born, 'y')
cc.frames(15, 1 / 30)
expect(alive(born, g.bombs), "A bomb vanished half a second after it was dropped - it was nowhere near the bottom of the canvas.")
fell = get(born, 'y') - y0
expect(near(fell, 75, 8), f"A bomb fell {round(fell)} pixels in half a second at 30 frames a second; at 150 pixels a second it should fall about 75. Move it by b.vy * dt (vy defaults to 150).")
expect(any(near(r['x'], get(born, 'x'), 0.01) and near(r['y'], get(born, 'y'), 0.01) and r['w'] == get(born, 'w') and r['h'] == get(born, 'h') for r in cc.rects()), "Draw every bomb each frame: for b in bombs: ctx.fill_rect(b.x, b.y, b.w, b.h).")

restore()
seen = {}
count = 0
for _ in range(480):
    cc.frames(1, 1 / 60)
    count += len(new_bombs(seen))
expect(6 <= count <= 15, f"In eight seconds at 60 frames a second {count} bombs fell; one every 0.8 seconds is about 10. Let the timer count game SECONDS: every(BOMB_EVERY, drop_bomb), not a count of frames.")

restore(keep=lambda a: get(a, 'col') != 7 and not (get(a, 'col') in (0, 1) and get(a, 'row') >= 3) and not (get(a, 'col') in (5, 6) and get(a, 'row') == 4))
seen = {}
cols = set()
total = 0
for _ in range(900):
    cc.frames(1, 1 / 30)
    for b in new_bombs(seen):
        total += 1
        cands = sorted((a for a in g.aliens if abs(mid(a) - mid(b)) <= 4 and -20 <= get(b, 'y') - (get(a, 'y') + get(a, 'h')) <= 18), key=lambda a: -get(a, 'y'))
        expect(cands, "A bomb appeared where there is no alien just above it. A bomb starts under the middle of its alien: x = shooter.x + shooter.w / 2 - 2, y = shooter.y + shooter.h.")
        a = cands[0]
        below = [o for o in g.aliens if abs(mid(o) - mid(a)) < 1 and get(o, 'y') > get(a, 'y')]
        expect(not below, "A bomb fell from an alien that has another alien below it. Only the lowest alien of each column drops bombs: find those first (a dict keyed by column), then choose one at random.")
        cols.add(get(a, 'col'))
    expect(all(get(b, 'y') <= HEIGHT + 12 for b in g.bombs), "Bombs are never removed after they leave the bottom of the canvas. Keep only bombs with b.y < HEIGHT: bombs = [b for b in bombs if b.y < HEIGHT].")
expect(22 <= total <= 70, f"{total} bombs fell in 30 seconds; one every 0.8 seconds is about 37.")
expect(len(cols) >= 5, f"Bombs only fell from {len(cols)} of the 7 columns that still have aliens. Choose the column at random each time: random.choice over the bottom aliens.")
expect(cols & {0, 1}, "Columns 0 and 1 have lost their two bottom rows, but their lowest aliens (row 2) never dropped a bomb. Every column's LOWEST alien can drop one, however high that is.")
"""

_CHECK10 = _HELPERS + """
expect('lives' in g and g.lives == 3, "Start with lives = 3 - a name in your code, outside any function.")
expect('state' in g and g.state == 'playing', "Keep what the game is doing in a top-level state = 'playing'.")
al0 = list(g.aliens)
home = [(get(a, 'x'), get(a, 'y')) for a in al0]
start_x = get(C(), 'x')


def reset():
    for a, (x, y) in zip(al0, home):
        put(a, 'x', x)
        put(a, 'y', y)
    g.aliens = list(al0)
    g.direction = 1
    g.bombs = []
    g.bullet = None
    g.lives = 3
    g.state = 'playing'
    put(C(), 'x', start_x)


def one_bomb():
    g.bombs = []
    for _ in range(80):
        cc.frames(1, 1 / 30)
        if g.bombs:
            break
    expect(g.bombs, "No bomb fell in over two seconds - keep the bombs from the last step.")
    b = g.bombs[0]
    g.bombs = [b]
    return b


def put_bomb(b, x, y):
    put(b, 'x', x)
    put(b, 'y', y)


reset()
cc.frames(1)
expect(any(re.search('lives', t, re.I) and '3' in t for t in cc.texts()), "Show the lives on the screen - it should say Lives: 3.")
b = one_bomb()
c = C()
put_bomb(b, mid(c) - get(b, 'w') / 2, get(c, 'y') - 4)
cc.frames(1, 0.001)
expect(g.lives == 2, f"A bomb landed on the cannon and the lives are {g.lives}; they should be 2. Collect the bombs that overlap the cannon (overlap(b, cannon)) and take a life for each.")
expect(not alive(b, g.bombs), "A bomb that hit the cannon should be removed from bombs, or it keeps hitting.")
expect(g.state == 'playing', "One lost life with two to spare should not end the game.")
cc.frames(10, 1 / 30)
expect(g.lives == 2, f"The lives kept falling ({g.lives}) after one bomb. One bomb costs ONE life: remove the bomb when it hits, or it takes a life every frame it overlaps the cannon.")
cc.frames(1)
expect(any(re.search('lives', t, re.I) and '2' in t for t in cc.texts()), "Show the lives on the screen - it should say Lives: 2 now.")

reset()
b = one_bomb()
c = C()
put_bomb(b, 0, get(c, 'y'))
cc.frames(1, 0.001)
expect(g.lives == 3 and alive(b, g.bombs), "A bomb level with the cannon but far off to one side cost a life. A hit needs the boxes to overlap in x as well as y.")
put_bomb(b, mid(c) - 2, get(c, 'y') - 40)
cc.frames(1, 0.001)
expect(g.lives == 3 and alive(b, g.bombs), "A bomb straight above the cannon but still high up cost a life. A hit needs the boxes to overlap in y as well as x.")
put_bomb(b, get(c, 'x') - 5.5, get(c, 'y') - 9)
cc.frames(1, 0.001)
expect(g.lives == 3 and alive(b, g.bombs), "A bomb 1.5 pixels beside the cannon's corner cost a life. Boxes that do not overlap do not hit.")
put_bomb(b, get(c, 'x') - 3, get(c, 'y') - 9)
cc.frames(1, 0.001)
expect(g.lives == 2, "A bomb overlapping the cannon's corner by a pixel should hit it: box against box.")

reset()
g.lives = 1
b = one_bomb()
c = C()
put_bomb(b, mid(c) - get(b, 'w') / 2, get(c, 'y') - 4)
cc.frames(1, 0.001)
expect(g.lives == 0 and g.state == 'over', f"The last life was lost: lives should be 0 and state 'over' - lives is {g.lives}, state is {g.state!r}.")
cc.frames(1)
expect(any(re.search('game over', t, re.I) for t in cc.texts()), "When the game is over, write 'Game over' on the screen.")
ax = [get(a, 'x') for a in g.aliens]
cx0 = get(C(), 'x')
known = {id(b) for b in g.bombs}
cc.press('ArrowRight')
cc.press(' ')
cc.frames(50, 1 / 30)
cc.release('ArrowRight')
cc.release(' ')
expect(all(near(get(a, 'x'), x, 0.001) for a, x in zip(g.aliens, ax)), "After the game is over the aliens keep marching. Start update with: if state != 'playing': return")
expect(near(get(C(), 'x'), cx0, 0.001) and g.bullet is None, "After the game is over the cannon still moves or fires. Start update with: if state != 'playing': return")
expect(all(id(b) in known for b in g.bombs), "After the game is over new bombs keep dropping. The timer keeps running, so drop_bomb must check: if state != 'playing' ...: return")
expect(g.lives == 0, f"The lives changed after the game was over ({g.lives}).")

reset()
g.lives = 5
low = max(get(a, 'y') + get(a, 'h') for a in g.aliens)
shift(0, (get(C(), 'y') - 3) - low)
cc.frames(3, 1 / 30)
expect(g.state == 'playing', "The lowest alien is still 3 pixels above the cannon's top, and the game was already over. It ends when an alien's bottom (a.y + a.h) reaches the cannon's top (cannon.y).")
shift(0, 6)
cc.frames(1, 0.001)
expect(g.state == 'over', "An alien has reached the cannon's row and the game is not over. Check any(a.y + a.h >= cannon.y for a in aliens) every frame.")
"""

_CHECK11 = _HELPERS + """
expect('wave' in g and g.wave == 1, "Start with wave = 1 - a name in your code, outside any function.")
expect('state' in g and 'lives' in g and 'score' in g, "Keep score, lives and state from the last steps.")
cc.frames(1)
expect(any(re.search('wave', t, re.I) and '1' in t for t in cc.texts()), "Show the wave on the screen: it should say Wave 1.")
s1 = speed_now()
expect(near(s1, 40, 4), f"The first wave with all 40 aliens should still march at 40 pixels a second; it moves at {round(s1)}.")
while len(g.aliens) > 1:
    kill(g.aliens[-1])
expect(g.wave == 1 and len(g.aliens) == 1, f"The next wave started while {len(g.aliens)} alien(s) were still alive (wave {g.wave}). A wave is won when NO alien is left: if not aliens.")
old = None
for _ in range(80):
    cc.frames(1, 1 / 30)
    if g.bombs:
        old = g.bombs[0]
        break
last = g.aliens[0]
g.direction = -1
before = g.score
pts = (30, 20, 20, 10, 10)[get(last, 'row')]
kill(last)
expect(g.wave == 2, f"The last alien was shot and the wave is {g.wave}. When no aliens are left (if not aliens), start the next wave: wave goes up by one.")
expect(len(g.aliens) == 40 and len({id(a) for a in g.aliens}) == 40, f"The next wave needs a fresh formation of 40 aliens; there are {len(g.aliens)}. Build a new list with make_aliens() and bind it to aliens (global aliens).")
expect(g.score == before + pts, f"The score should carry on into the next wave: it was {before}, the last alien was worth {pts}, and it is now {g.score}.")
expect(g.lives == 99, "The lives should carry on into the next wave, not be reset.")
expect(g.state == 'playing', f"The game should go on after the last alien: state is {g.state!r}.")
expect(min(get(a, 'y') for a in g.aliens) == 40, "The new formation starts back at the top, y 40 for the first row.")
expect(g.bullet is None, "The bullet that killed the last alien is used up; nothing should be in the air at the start of a wave.")
expect(old is None or not alive(old, g.bombs), "Bombs from the last wave were still falling when the new one started. Clear them: bombs = [].")
x0 = [get(a, 'x') for a in g.aliens]
cc.frames(6, 1 / 30)
expect(all(get(a, 'x') > x + 5 for a, x in zip(g.aliens, x0)), "The new formation should start marching to the RIGHT. Put direction = 1 back when a wave starts.")
cc.frames(30, 1 / 30)
expect(g.wave == 2 and len(g.aliens) == 40, f"A second after the new wave started it is wave {g.wave} with {len(g.aliens)} aliens. A wave should start once, not every frame.")
s2 = speed_now()
expect(s2 >= 1.15 * s1, f"Wave 2 marches at {round(s2)} pixels a second, wave 1 started at {round(s1)}. Each wave should be faster: add 10 pixels a second per wave after the first.")
expect(s2 <= 2.5 * s1, f"Wave 2 marches at {round(s2)} pixels a second - too big a jump from {round(s1)}. About +10 a wave is plenty.")
while len(g.aliens) > 1:
    kill(g.aliens[-1])
kill(g.aliens[0])
expect(g.wave == 3 and len(g.aliens) == 40, f"Clearing wave 2 should start wave 3 with 40 aliens: wave is {g.wave}, aliens {len(g.aliens)}.")
s3 = speed_now()
expect(s3 >= 1.05 * s2, f"Wave 3 marches at {round(s3)} pixels a second, no faster than wave 2 ({round(s2)}). Every wave is faster than the one before.")
"""

_CHECK12 = _HELPERS + """
expect(g.state == 'playing' and g.lives == 3 and g.wave == 1 and g.score == 0, "Keep the game from the last step: state 'playing', 3 lives, wave 1, score 0.")
al0 = list(g.aliens)
homes = {(get(a, 'x'), get(a, 'y')) for a in al0}
start_x = get(C(), 'x')
kill(g.aliens[-1])
kill(g.aliens[-1])
n, sc = len(g.aliens), g.score
g.lives = 3
cc.press('Enter')
cc.release('Enter')
expect(len(g.aliens) == n and g.score == sc and g.state == 'playing', "Enter in the middle of a game restarted it. Only restart when the game is over: state == 'over'.")
put(C(), 'x', 10)
g.score = 90
g.wave = 3
g.lives = 1
g.bombs = []
for _ in range(80):
    cc.frames(1, 1 / 30)
    if g.bombs:
        break
expect(g.bombs, "No bomb fell in over two seconds - keep the bombs from the earlier steps.")
b = g.bombs[0]
g.bombs = [b]
put(b, 'x', mid(C()) - get(b, 'w') / 2)
put(b, 'y', get(C(), 'y') - 4)
cc.frames(1, 0.001)
expect(g.state == 'over', "The last life should end the game - that part is from step 10.")
cc.frames(1)
expect(any(re.search('enter', t, re.I) for t in cc.texts()), "On the end screen, tell the player how to go again: 'Press Enter to play again'.")
for k in ('ArrowLeft', ' ', 'a', 'Escape'):
    cc.press(k)
    cc.release(k)
expect(g.state == 'over', "A key other than Enter restarted the game. Only Enter should.")
cc.press('Enter')
cc.release('Enter')
expect(g.state == 'playing', f"Pressing Enter after a game over should start a new game: state is {g.state!r}. restart() assigns state, so it needs `global state` - without it Python makes a quiet local variable and the real one never changes.")
expect(g.score == 0, f"A new game starts with a score of 0; it is {g.score}.")
expect(g.lives == 3, f"A new game starts with 3 lives; it is {g.lives}.")
expect(g.wave == 1, f"A new game starts at wave 1; it is wave {g.wave}.")
expect(len(g.aliens) == 40 and {(get(a, 'x'), get(a, 'y')) for a in g.aliens} == homes, f"A new game needs a fresh formation of 40 aliens at the top; there are {len(g.aliens)}. start_wave(1) builds one.")
expect(near(get(C(), 'x'), start_x, 1), f"A new game puts the cannon back in the middle (x {round(start_x)}); it is at x {round(get(C(), 'x'))}.")
expect(g.bullet is None and not g.bombs, "A new game starts with no bullet and no bombs in the air.")
cc.frames(1)
expect(not any(re.search('game over', t, re.I) for t in cc.texts()), "'Game over' is still on the screen after the restart.")
s = speed_now()
expect(near(s, 40, 4), f"A new game should march at the wave 1 speed, 40 pixels a second; it moves at {round(s)}. Put wave back to 1: start_wave(1).")
cc.frames(30, 1 / 30)
expect(g.state == 'playing' and g.lives == 3, f"The new game fell over at once (state {g.state!r}, lives {g.lives}). Put everything back: the lives, the state, the formation.")
g.lives = 3
low = max(get(a, 'y') + get(a, 'h') for a in g.aliens)
shift(0, (get(C(), 'y') + 3) - low)
cc.frames(1, 0.001)
expect(g.state == 'over', "The aliens reached the cannon and the game did not end - that part is from step 10.")
cc.press('Enter')
cc.release('Enter')
expect(g.state == 'playing' and len(g.aliens) == 40 and min(get(a, 'y') for a in g.aliens) == 40, "Enter after the aliens landed should start a new game with a fresh formation back at the top.")
cc.frames(30, 1 / 30)
expect(g.state == 'playing', "The new game after the aliens landed ended at once. Is the formation back at the top?")
"""


def _step(**fields: object) -> Step:
    """A step on this track: Python, in the Space Invaders (Python) track."""
    fields["track"] = TRACK
    fields["language"] = "python"
    return Step(**fields)  # type: ignore[arg-type]


PYINVADERS_STEPS: tuple[Step, ...] = (
    _step(
        id="pyinv-01-cannon",
        title="The cannon is a dataclass",
        teaches=(
            "A game keeps what it knows about each thing in one place: where "
            "it is, how big it is, how fast it goes. Python's tidy way to "
            "write that down is a @dataclass (from dataclasses import "
            "dataclass). List the fields with their types and Python writes "
            "the constructor, so Cannon(222, 296, 36, 12) makes a cannon and "
            "cannon.x reads its x. A field with = 240 after it is a default "
            "you can leave out. A plain dict - {'x': 222, 'y': 296, 'w': 36, "
            "'h': 12} - works too, and the checks accept either. The canvas "
            "is 480 by 320 and y grows DOWNWARDS, so a cannon on the floor "
            "has a big y; a box is placed by its top-left corner. Paint the "
            "background first: the canvas draws back to front."
        ),
        goal="Add a Cannon dataclass with fields x, y, w, h and speed (default 240) and make cannon = Cannon(222, 296, 36, 12) - a dict with those keys works too. Draw it every frame, after the background, as a filled rectangle.",
        starter=_P0,
        solution=_P1,
        check=_CHECK1,
        hint="@dataclass class Cannon: x: float, y: float, w: float, h: float, speed: float = 240   then   ctx.fill_rect(cannon.x, cannon.y, cannon.w, cannon.h) in draw().",
    ),
    _step(
        id="pyinv-02-move",
        title="Slide with the keys",
        teaches=(
            "`keys` (import it from canvas) is a set of the names of the keys "
            "held right now - 'ArrowLeft', 'ArrowRight', ' ' for the space "
            "bar, 'Enter', 'a' to 'z'. It fills and empties itself; you only "
            "ask it, with `in`. Move by speed * dt. dt is the SECONDS since "
            "the last frame (about 0.0167, or 0.033 on a slow screen), so a "
            "speed of 240 means 240 pixels a second at any frame rate - "
            "cannon.x += 4 would be half as fast on a slower screen. Then "
            "clamp: max(low, min(high, x)) is x unless it is below low or "
            "above high; the right-most the cannon can go is WIDTH - "
            "cannon.w, because x is its left edge. One small function per "
            "rule - move_cannon(dt) - keeps update(dt) readable. Click the "
            "game before pressing keys, so it has the keyboard."
        ),
        goal="Add move_cannon(dt), called from update(dt): while ArrowLeft is held the cannon moves left, and while ArrowRight is held it moves right, at cannon.speed pixels a second, and it never leaves the canvas.",
        starter=_P1,
        solution=_P2,
        check=_CHECK2,
        hint="if 'ArrowLeft' in keys: cannon.x -= cannon.speed * dt   (and += for ArrowRight), then cannon.x = max(0, min(WIDTH - cannon.w, cannon.x))",
    ),
    _step(
        id="pyinv-03-bullet",
        title="One bullet at a time",
        teaches=(
            "The classic cannon has exactly one bullet in the air, so the "
            "bullet is either nothing or a Bullet: bullet = None to start, "
            "and `bullet is None` asks 'is the gun free?' (use `is None`, "
            "not == None). Firing is one rule: if ' ' in keys and bullet is "
            "None, make a Bullet at the cannon's middle, just above its top. "
            "It flies up at vy = -360 pixels a second (negative is up, and "
            "dt keeps it per second); once its bottom is above the canvas "
            "give the gun back with bullet = None. Both functions re-bind the "
            "top-level name, so each needs `global bullet` - without it "
            "Python makes a quiet local variable (UnboundLocalError when it "
            "is read first). A list of bullets and a cooldown timer would "
            "fire a stream; None-or-one is the whole rule. Draw the bullet "
            "only when there is one."
        ),
        goal="Add a Bullet dataclass (x, y, w, h and vy, default -360) and bullet = None, fire() and move_bullet(dt), called from update(dt). Holding Space makes a Bullet(..., 4, 10) at the cannon's middle just above its top, but only while bullet is None; it flies up at 360 pixels a second and goes back to None once it has left the top of the canvas. Draw it. bullet is re-bound by the program, so a check looks it up again.",
        starter=_P2,
        solution=_P3,
        check=_CHECK3,
        hint="def fire(): global bullet; if ' ' in keys and bullet is None: bullet = Bullet(cannon.x + cannon.w / 2 - 2, cannon.y - 10, 4, 10)   and in move_bullet: bullet.y += bullet.vy * dt; if bullet.y + bullet.h < 0: bullet = None",
    ),
    _step(
        id="pyinv-04-aliens",
        title="A block of aliens",
        teaches=(
            "Forty aliens are not typed out; they are built. A list "
            "comprehension can have two for clauses, and that is a nested "
            "loop in one expression: [Alien(...) for row, color in "
            "enumerate(ROW_COLORS) for col in range(COLS)] counts rows in "
            "the outer loop and columns in the inner one, and enumerate hands "
            "back (index, item) pairs that the for unpacks. Each alien's "
            "place is arithmetic: x = 40 + col * 36, y = 40 + row * 26. "
            "(itertools.product(range(5), range(8)) is the other way to "
            "write the two loops.) Beware the shortcuts [Alien(...)] * 40 "
            "and [[0] * 8] * 5: they do not make forty aliens or five rows, "
            "they make one object and many names for it, so changing one "
            "changes them all. Fields with defaults (w: float = 24) must "
            "come after the ones without. Draw every alien in its row's "
            "colour."
        ),
        goal="Add an Alien dataclass (x, y, row, col, color, then w 24 and h 16 as defaults) and build aliens, a list of 5 rows of 8 with one list comprehension: x 40 + col * 36, y 40 + row * 26, each row its own color from ROW_COLORS. Draw every alien, behind the cannon.",
        starter=_P3,
        solution=_P4,
        check=_CHECK4,
        hint="aliens = [Alien(40 + col * 36, 40 + row * 26, row, col, color) for row, color in enumerate(ROW_COLORS) for col in range(COLS)]",
    ),
    _step(
        id="pyinv-05-march",
        title="The block marches",
        teaches=(
            "The whole formation moves as one block, so one number says "
            "which way: direction = 1 means right and -1 means left. "
            "Multiplying by it turns 'left or right?' into arithmetic with "
            "no if: a.x += direction * ALIEN_SPEED * dt. ALIEN_SPEED is "
            "pixels a SECOND and dt is seconds, so the march looks the same "
            "at any frame rate (a.x += 1 would be twice as fast at 60 "
            "frames a second as at 30). Notice what needs `global` and what "
            "does not: the for loop changes a field of each alien, "
            "a.x += ..., which is not re-binding a name, so march() needs "
            "no global yet. Assigning to the name itself - direction = "
            "-direction - will, in the next step."
        ),
        goal="Add direction = 1 (1 is right, -1 is left), ALIEN_SPEED = 40 and march(dt), called from update(dt): every alien moves together by direction * ALIEN_SPEED * dt. The block does not turn round yet.",
        starter=_P4,
        solution=_P5,
        check=_CHECK5,
        hint="def march(dt): for a in aliens: a.x += direction * ALIEN_SPEED * dt   - and call march(dt) from update.",
    ),
    _step(
        id="pyinv-06-edges",
        title="Drop a row and turn round",
        teaches=(
            "The block hits an edge when ANY alien does: any(a.x + a.w > "
            "WIDTH for a in aliens) is True as soon as one alien's right "
            "side passes the edge, and any(a.x < 0 for a in aliens) is the "
            "left. (max(a.x + a.w for a in aliens) > WIDTH says the same, "
            "but max() and min() of an empty sequence raise ValueError "
            "unless you pass default=.) Do not look at aliens[0] alone: it "
            "is only the top-left alien, and it is gone when it is shot. "
            "Check only the edge the block is heading for: `direction > 0 "
            "and ...` for the right edge, `direction < 0 and ...` for the "
            "left. Then turn round (direction = -direction) AND drop every "
            "alien by DROP. Turn round once: drop without turning and the "
            "block is still over the edge next frame, and drops again and "
            "again. direction is re-bound, so march() needs `global "
            "direction`; leave it out and Python raises UnboundLocalError."
        ),
        goal="Add DROP = 16. In march(dt), when the block is heading right and any alien's right side passes WIDTH, or heading left and any alien's left side passes 0, set direction = -direction and move every alien down by DROP - once per touch. It must work with the right-hand or left-hand columns gone.",
        starter=_P5,
        solution=_P6,
        check=_CHECK6,
        hint="at_right = direction > 0 and any(a.x + a.w > WIDTH for a in aliens)   at_left = direction < 0 and any(a.x < 0 for a in aliens)   if at_right or at_left: direction = -direction; for a in aliens: a.y += DROP   (global direction)",
    ),
    _step(
        id="pyinv-07-shoot",
        title="Shoot them, score by row",
        teaches=(
            "Two boxes overlap when they overlap along x AND along y: a.x < "
            "b.x + b.w and a.x + a.w > b.x and a.y < b.y + b.h and a.y + "
            "a.h > b.y. One function, overlap(a, b), serves every box in "
            "the game. Ask which aliens the bullet touches with a list "
            "comprehension - hit = [a for a in aliens if overlap(bullet, a)] "
            "- and keep the others with another: aliens = [a for a in aliens "
            "if a not in hit]. Never call aliens.remove(a) inside `for a in "
            "aliens:`: removing shifts every later alien one place down, so "
            "the loop steps over the next one (and if you set bullet = None "
            "inside that loop, the next pass crashes on None). The points "
            "come from a table indexed by row, ROW_POINTS[a.row], added up "
            "with sum(...) - the top rows are worth most. The function "
            "re-binds bullet, aliens and score, so it needs `global` for "
            "all three. Show the score with an f-string: f'Score: {score}'."
        ),
        goal="Add score = 0, ROW_POINTS = [30, 20, 20, 10, 10], overlap(a, b) (two boxes) and hit_aliens(), called from update(dt). When the bullet touches an alien that alien is taken out of aliens, bullet goes back to None, and score goes up by the points of the alien's row. Show the score as text. aliens, bullet and score are re-bound by the program.",
        starter=_P6,
        solution=_P7,
        check=_CHECK7,
        hint="hit = [a for a in aliens if overlap(bullet, a)]; if hit: aliens = [a for a in aliens if a not in hit]; bullet = None; score += sum(ROW_POINTS[a.row] for a in hit)   (global bullet, aliens, score; return early if bullet is None)",
    ),
    _step(
        id="pyinv-08-faster",
        title="Faster as they thin out",
        teaches=(
            "The fewer aliens, the faster the block - the classic panic. "
            "Don't keep a speed variable in step with the kills; work it "
            "out from what is left, every frame, in a small function: "
            "march_speed() returns ALIEN_SPEED + 3 * (TOTAL - len(aliens)), "
            "where TOTAL - len(aliens) is how many are dead. Then the speed "
            "is always right, whoever removed the aliens. Any formula that "
            "never goes down as aliens die will do; 3 pixels a second per "
            "kill takes the block from 40 to about 157 for the last alien "
            "(a bigger number is too fast to play). Work the speed out once "
            "per frame, step = direction * march_speed() * dt, and use step "
            "for every alien, instead of calling the function forty times. "
            "It is still pixels a SECOND: dt is in there."
        ),
        goal="Add TOTAL = len(ROW_COLORS) * COLS and march_speed(), and use it in march(dt): the block marches at ALIEN_SPEED (40) pixels a second with all 40 aliens, and faster with every alien that dies - with 20 left at least 1.3 times as fast, with one left at least 3 times as fast.",
        starter=_P7,
        solution=_P8,
        check=_CHECK8,
        hint="def march_speed(): return ALIEN_SPEED + 3 * (TOTAL - len(aliens))   and in march: step = direction * march_speed() * dt; for a in aliens: a.x += step",
    ),
    _step(
        id="pyinv-09-bombs",
        title="They shoot back",
        teaches=(
            "Only the LOWEST alien of each column can shoot - the others "
            "would be firing through their friends. Find them with a dict "
            "keyed by column: bottoms = {}; for a in aliens, keep the "
            "lowest one seen for a.col (a.y bigger is lower). Then "
            "random.choice(list(bottoms.values())) picks one shooter at "
            "random. (max(column, key=lambda a: a.y) finds the lowest of one "
            "column; random.choice(aliens) is the bug, since most aliens "
            "have another alien below them.) Drop the bomb from just under "
            "its middle. Timing: every(0.8, drop_bomb) from canvas calls a "
            "function every 0.8 game seconds, whatever the frame rate - "
            "count seconds, not frames. bombs.append(...) changes the list "
            "and needs no `global`; bombs = [b for b in bombs if b.y < "
            "HEIGHT] re-binds it, so move_bombs does. The checks seed "
            "random, so a run is repeatable."
        ),
        goal="Add import random, every from canvas, a Bomb dataclass (x, y, w, h and vy, default 150), bombs = [], BOMB_EVERY = 0.8, drop_bomb() and move_bombs(dt). every(BOMB_EVERY, drop_bomb): each time, a random column's bottom-most alien drops a Bomb(..., 4, 10) from just under its middle. Bombs fall at 150 pixels a second and are taken out of bombs once they leave the bottom. Draw them.",
        starter=_P8,
        solution=_P9,
        check=_CHECK9,
        hint="bottoms = {}; for a in aliens: low = bottoms.get(a.col); if low is None or a.y > low.y: bottoms[a.col] = a   then   shooter = random.choice(list(bottoms.values())); bombs.append(Bomb(shooter.x + shooter.w / 2 - 2, shooter.y + shooter.h, 4, 10))",
    ),
    _step(
        id="pyinv-10-lives",
        title="Lives and game over",
        teaches=(
            "A bomb on the cannon is another overlap(b, cannon). Collect "
            "the bombs that hit - hit = [b for b in bombs if overlap(b, "
            "cannon)] - take them out of bombs, and take a life for each: "
            "lives = max(0, lives - len(hit)). Removing the bomb is what "
            "makes it cost ONE life; leave it in and it overlaps the "
            "cannon next frame, and the next, sixty lives a second. (With "
            "many bullets and many aliens you would test every pair: for b, "
            "a in itertools.product(bullets, aliens), or zip(...) when "
            "things pair up one to one.) The game is over when lives reach "
            "0 or when any alien reaches the cannon: any(a.y + a.h >= "
            "cannon.y for a in aliens). Keep what the game is doing in "
            "state = 'playing' or 'over', and start update with `if state "
            "!= 'playing': return` so nothing moves - but every(...) keeps "
            "ticking, so drop_bomb must check the state too. Each function "
            "that assigns lives or state needs it on its `global` line."
        ),
        goal="Add lives = 3, state = 'playing', hit_cannon() and check_over(). A bomb that touches the cannon is removed and costs one life; when lives reach 0, or any alien's bottom reaches the cannon's top (cannon.y), state becomes 'over'. While state is not 'playing', update does nothing and no new bombs drop. Show Lives: 3 and, when over, Game over.",
        starter=_P9,
        solution=_P10,
        check=_CHECK10,
        hint="hit = [b for b in bombs if overlap(b, cannon)]; if hit: bombs = [b for b in bombs if b not in hit]; lives = max(0, lives - len(hit))   and   if lives <= 0 or any(a.y + a.h >= cannon.y for a in aliens): state = 'over'   (global each)",
    ),
    _step(
        id="pyinv-11-waves",
        title="Clear it and go again, faster",
        teaches=(
            "A wave is won when no alien is left, and Python says that as "
            "`not aliens`: an empty list is falsy, a list with anything in "
            "it is truthy. Winning starts the next wave: put everything a "
            "wave owns back - a fresh formation, no bullet, no bombs, "
            "marching right - and add one to wave. The fresh formation "
            "must be a NEW list each time, so the code that builds it "
            "moves into make_aliens(), a function that returns one; "
            "start_wave(n) calls it and re-binds aliens, bombs, bullet, "
            "direction and wave, all on its `global` line. Score and lives "
            "carry on. Making wave 2 faster is one more term in the speed "
            "from step 8: 10 * (wave - 1) adds 10 pixels a second per wave, "
            "so it stays pixels a second. Show the wave number with an "
            "f-string."
        ),
        goal="Add wave = 1, make_aliens() (returns a new full formation) and start_wave(n). When no aliens are left, start_wave(wave + 1): wave goes up by one, a fresh 40 aliens at the top marching right, no bullet or bombs in the air, score and lives carried on. Each wave marches faster: add 10 pixels a second to march_speed() for each wave after the first. Show Wave 1.",
        starter=_P10,
        solution=_P11,
        check=_CHECK11,
        hint="if not aliens: start_wave(wave + 1)   with   def start_wave(n): global aliens, bombs, bullet, direction, wave; wave = n; aliens = make_aliens(); bombs = []; bullet = None; direction = 1   and  ALIEN_SPEED + 10 * (wave - 1) + ...",
    ),
    _step(
        id="pyinv-12-restart",
        title="Play again",
        teaches=(
            "A restart puts back everything the game changed: score, "
            "lives, state, the cannon, and the wave - start_wave(1) already "
            "does the aliens, bombs, bullet and direction, so reuse it "
            "instead of copying its lines. Every name restart() assigns "
            "goes on its `global` line - leave state off and `state = "
            "'playing'` quietly makes a local variable while the real one "
            "stays 'over'. The cannon is an object whose field we change "
            "(cannon.x = ...), which needs no global. Keys that do "
            "something once are events, not held keys: on_key_down(fn) "
            "calls fn(key) when a key goes down. Enter restarts only when "
            "state == 'over', so a stray key in the middle of a game does "
            "not wipe it. Tell the player which key, on the end screen."
        ),
        goal="Write restart() - score 0, lives 3, state 'playing', the cannon back in the middle (x 222) and start_wave(1) - and call it from on_key_down when Enter is pressed while state is 'over', not during play and not for other keys. Write 'Press Enter to play again' on the end screen.",
        starter=_P11,
        solution=_P12,
        check=_CHECK12,
        hint="def restart(): global score, lives, state; score = 0; lives = 3; state = 'playing'; cannon.x = WIDTH / 2 - cannon.w / 2; start_wave(1)   and   if key == 'Enter' and state == 'over': restart()",
    ),
    _step(
        id="pyinv-13-yours",
        title="Now it's yours",
        teaches=(
            "A whole game: a cannon you steer, a single shot, a marching "
            "block that drops and speeds up, bombs from the bottom of "
            "random columns, lives, waves and a restart. Ideas, easier "
            "first: a mystery ship that crosses the top now and then "
            "(after(10, fn) or every(15, fn)) worth a random 50 to 300; "
            "shields - a list of blocks that each take three hits, drawn "
            "with their hits left in the colour; two shots at once (make "
            "bullet a list and filter it with a comprehension); a high "
            "score kept in a module-level name; aliens that animate by "
            "swapping between two shapes every march step (itertools.cycle); "
            "a bomb that comes down in a wiggle; a pause on 'p', which is "
            "another state."
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_P12,
        solution=_P12,
        check="",
    ),
)
