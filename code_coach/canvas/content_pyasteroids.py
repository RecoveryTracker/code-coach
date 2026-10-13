"""Asteroids in Python: the ship-and-rocks game of the JavaScript Asteroids track, taught the Python way.

Not a transliteration. The game is the same - a ship that turns and thrusts
with a velocity and a friction that does not depend on the frame rate, a
screen that wraps round on every edge, bullets with a cooldown and a
lifetime, rocks that drift, spin and break in two, circle collisions, score,
lives with a moment of invulnerability, a game over and a restart - but the
parts are Python's own:

  * Ship, Bullet and Rock are `@dataclass` classes (a dict with the same keys
    works too, and every check accepts both); a rock's outline is a
    `field(default_factory=list)`, because a plain `= []` is refused
  * the heading is `math.cos` / `math.sin` of an angle in radians
    (`math.radians`, `math.tau`); `DRAG ** dt` is friction per second
  * the screen wraps with the `%` operator - which, unlike JavaScript's,
    gives a positive answer for a negative number
  * `any()` over a generator for "is the ship touching a rock", `math.hypot`
    for a distance, nested loops for the bullet-against-rock pairs
  * list comprehensions to cull the expired bullets, and the classic bug of
    removing from a list while a `for` is walking it
  * `random.uniform` / `random.choice`, tuple unpacking, f-strings for the
    HUD, `enumerate` for the rock's outline, `global` only where a function
    re-binds a top-level name - and what Python does when it is missing

As in the other tracks, each step starts from the one before, finished, and a
check plays the game rather than reading the code. The checks read these
top-level names, and set them: ship, bullets, rocks, score, lives, state
(and call make_rock and spawn_rocks). `bullets`, `rocks`, `score`, `lives` and
`state` are re-bound by the program, so a check always looks them up again
rather than holding on to one.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

TRACK = "Asteroids (Python)"

# -- Shared check helpers ---------------------------------------------------

#: Prepended to every check. A thing's fields can be a dict's or an object's,
#: so a check reads them with get() and writes them with put(), and never cares
#: which the learner chose. S() looks the ship up afresh. stage() puts the game
#: in a known place (and empties the bullets and rocks); rock() makes a rock
#: that sits still; shoot() fires one bullet and freezes it so a check can put it
#: where it likes. Dataclasses are compared by value, so a check asks `alive()`
#: (is this very object still in the list) and never `in`.
_HELPERS = """import math


def get(o, k, default=None):
    if isinstance(o, dict):
        return o.get(k, default)
    return getattr(o, k, default)


def put(o, k, v):
    if isinstance(o, dict):
        o[k] = v
    else:
        setattr(o, k, v)


def S():
    return g.ship


def stage(x=240, y=160, angle=0.0):
    s = S()
    put(s, 'x', x)
    put(s, 'y', y)
    put(s, 'angle', angle)
    put(s, 'vx', 0)
    put(s, 'vy', 0)
    if get(s, 'invuln') is not None:
        put(s, 'invuln', 0)
    if 'state' in g:
        g.state = 'playing'
    if 'cooldown' in g:
        g.cooldown = 0
    if 'bullets' in g:
        g.bullets.clear()
    if 'rocks' in g:
        g.rocks.clear()


def speed():
    return math.hypot(get(S(), 'vx'), get(S(), 'vy'))


def alive(o, items):
    return any(x is o for x in items)


def rock(x, y, size):
    rk = g.make_rock(x, y, size)
    for k, v in (('vx', 0), ('vy', 0), ('spin', 0), ('angle', 0.5)):
        put(rk, k, v)
    g.rocks.append(rk)
    return rk


def shoot():
    cc.frames(20)
    old = list(g.bullets)
    cc.press(' ')
    cc.frames(1)
    cc.release(' ')
    new = [b for b in g.bullets if not alive(b, old)]
    expect(new, "Holding Space should put a bullet into the bullets list.")
    b = new[-1]
    put(b, 'vx', 0)
    put(b, 'vy', 0)
    return b


"""

# -- The programs -----------------------------------------------------------

_I0 = "from canvas import ctx, WIDTH, HEIGHT, on_frame"
_I1 = "import math\nfrom dataclasses import dataclass\n\nfrom canvas import ctx, WIDTH, HEIGHT, on_frame, keys"
_I5 = (
    "import math\nfrom dataclasses import dataclass\n\n"
    "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down, keys"
)
_I7 = (
    "import math\nimport random\nfrom dataclasses import dataclass, field\n\n"
    "from canvas import ctx, WIDTH, HEIGHT, on_frame, keys"
)
_I11 = (
    "import math\nimport random\nfrom dataclasses import dataclass, field\n\n"
    "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down, keys"
)

_C1 = "TURN = 4"
_C2 = _C1 + "\nTHRUST = 160"
_C3 = _C2 + "\nDRAG = 0.5"
_C5 = _C3 + "\nBULLET_SPEED = 360"
_C6 = _C5 + "\nBULLET_LIFE = 1\nCOOLDOWN = 0.25"
_C8 = _C6 + "\nPOINTS = {1: 100, 2: 50, 3: 20}"
_C10 = _C8 + "\nINVULN = 2"

_CLASS_SHIP = """@dataclass
class Ship:
    x: float
    y: float
    angle: float = -math.pi / 2
    vx: float = 0
    vy: float = 0
    r: float = 12"""

_CLASS_SHIP10 = _CLASS_SHIP + "\n    invuln: float = 0"

_CLASS_BULLET5 = """@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    r: float = 2"""

_CLASS_BULLET6 = _CLASS_BULLET5 + "\n    life: float = BULLET_LIFE"

_CLASS_ROCK = """@dataclass
class Rock:
    x: float
    y: float
    vx: float
    vy: float
    size: int
    r: float
    angle: float = 0
    spin: float = 0
    shape: list = field(default_factory=list)"""

_N1 = "ship = Ship(240, 160)"
_N5 = _N1 + "\nbullets = []"
_N6 = _N1 + "\nbullets = []\ncooldown = 0"
_N7 = _N6 + "\nrocks = []"
_N8 = _N7 + "\nscore = 0"
_N10 = _N8 + "\nlives = 3"
_N11 = _N10 + "\nstate = 'playing'"

_TURN = """def turn_ship(dt):
    turn = ('ArrowRight' in keys) - ('ArrowLeft' in keys)
    ship.angle += turn * TURN * dt"""

_FLY2 = """def fly_ship(dt):
    if 'ArrowUp' in keys:
        ship.vx += math.cos(ship.angle) * THRUST * dt
        ship.vy += math.sin(ship.angle) * THRUST * dt
    ship.x += ship.vx * dt
    ship.y += ship.vy * dt"""

_FLY3 = """def fly_ship(dt):
    if 'ArrowUp' in keys:
        ship.vx += math.cos(ship.angle) * THRUST * dt
        ship.vy += math.sin(ship.angle) * THRUST * dt
    damp = DRAG ** dt
    ship.vx *= damp
    ship.vy *= damp
    ship.x += ship.vx * dt
    ship.y += ship.vy * dt"""

_FLY4 = _FLY3 + "\n    wrap(ship)"

_WRAP = """def wrap(o):
    o.x = (o.x + o.r) % (WIDTH + 2 * o.r) - o.r
    o.y = (o.y + o.r) % (HEIGHT + 2 * o.r) - o.r"""

_FIRE = """def fire():
    c, s = math.cos(ship.angle), math.sin(ship.angle)
    bullets.append(Bullet(
        ship.x + c * ship.r,
        ship.y + s * ship.r,
        ship.vx + c * BULLET_SPEED,
        ship.vy + s * BULLET_SPEED,
    ))"""

_MOVE_BULLETS5 = """def move_bullets(dt):
    for b in bullets:
        b.x += b.vx * dt
        b.y += b.vy * dt
        wrap(b)"""

_MOVE_BULLETS6 = """def move_bullets(dt):
    global bullets
    for b in bullets:
        b.x += b.vx * dt
        b.y += b.vy * dt
        b.life -= dt
        wrap(b)
    bullets = [b for b in bullets if b.life > 0]"""

_KEYS5 = """def key_down(key):
    if key == ' ':
        fire()


on_key_down(key_down)"""

_GUN = """def run_gun(dt):
    global cooldown
    cooldown = max(0, cooldown - dt)
    if ' ' in keys and cooldown <= 0:
        fire()
        cooldown = COOLDOWN"""

_MAKE_ROCK = """def make_rock(x, y, size):
    heading = random.uniform(0, math.tau)
    speed = random.uniform(20, 60)
    return Rock(
        x, y,
        math.cos(heading) * speed,
        math.sin(heading) * speed,
        size,
        size * 14,
        angle=random.uniform(0, math.tau),
        spin=random.uniform(-1, 1),
        shape=[random.uniform(0.75, 1.2) for _ in range(10)],
    )"""

_SPAWN = """def spawn_rocks(n):
    for _ in range(n):
        while True:
            x = random.uniform(0, WIDTH)
            y = random.uniform(0, HEIGHT)
            if math.hypot(x - ship.x, y - ship.y) >= 120:
                break
        rocks.append(make_rock(x, y, random.choice((2, 3))))"""

_SPAWN_CALL = "spawn_rocks(4)"

_MOVE_ROCKS = """def move_rocks(dt):
    for rk in rocks:
        rk.x += rk.vx * dt
        rk.y += rk.vy * dt
        rk.angle += rk.spin * dt
        wrap(rk)"""

_OVERLAP = """def overlap(a, b):
    return math.hypot(a.x - b.x, a.y - b.y) < a.r + b.r"""

_HIT8 = """def hit_rocks():
    global bullets, rocks, score
    live = list(rocks)
    for b in bullets:
        for rk in live:
            if overlap(b, rk):
                score += POINTS[rk.size]
                live.remove(rk)
                b.life = 0
                break
    rocks = live
    bullets = [b for b in bullets if b.life > 0]"""

_HIT9 = """def break_rock(rk):
    if rk.size == 1:
        return []
    return [make_rock(rk.x, rk.y, rk.size - 1) for _ in range(2)]


def hit_rocks():
    global bullets, rocks, score
    live = list(rocks)
    pieces = []
    for b in bullets:
        for rk in live:
            if overlap(b, rk):
                score += POINTS[rk.size]
                live.remove(rk)
                pieces += break_rock(rk)
                b.life = 0
                break
    rocks = live + pieces
    bullets = [b for b in bullets if b.life > 0]"""

_LOSE10 = """def place_ship():
    ship.x, ship.y = WIDTH / 2, HEIGHT / 2
    ship.vx = ship.vy = 0
    ship.angle = -math.pi / 2


def lose_life():
    global lives
    lives -= 1
    place_ship()
    ship.invuln = INVULN


def hit_ship(dt):
    ship.invuln = max(0, ship.invuln - dt)
    if ship.invuln <= 0 and any(overlap(ship, rk) for rk in rocks):
        lose_life()"""

_LOSE11 = """def place_ship():
    ship.x, ship.y = WIDTH / 2, HEIGHT / 2
    ship.vx = ship.vy = 0
    ship.angle = -math.pi / 2


def lose_life():
    global lives, state
    lives -= 1
    if lives <= 0:
        state = 'over'
        return
    place_ship()
    ship.invuln = INVULN


def hit_ship(dt):
    ship.invuln = max(0, ship.invuln - dt)
    if ship.invuln <= 0 and any(overlap(ship, rk) for rk in rocks):
        lose_life()"""

_RESET = """def reset():
    global bullets, rocks, cooldown, score, lives, state
    place_ship()
    ship.invuln = 0
    cooldown = 0
    bullets = []
    rocks = []
    spawn_rocks(4)
    score = 0
    lives = 3
    state = 'playing'"""

_KEYS11 = """def key_down(key):
    if key == 'Enter' and state == 'over':
        reset()


on_key_down(key_down)"""

_UPDATE_PASS = """def update(dt):
    pass"""

_UPDATE1 = """def update(dt):
    turn_ship(dt)"""

_UPDATE2 = """def update(dt):
    turn_ship(dt)
    fly_ship(dt)"""

_UPDATE5 = _UPDATE2 + "\n    move_bullets(dt)"

_UPDATE6 = """def update(dt):
    turn_ship(dt)
    fly_ship(dt)
    run_gun(dt)
    move_bullets(dt)"""

_UPDATE7 = _UPDATE6 + "\n    move_rocks(dt)"
_UPDATE8 = _UPDATE7 + "\n    hit_rocks()"
_UPDATE10 = _UPDATE8 + "\n    hit_ship(dt)"
_UPDATE11 = """def update(dt):
    if state != 'playing':
        return
    turn_ship(dt)
    fly_ship(dt)
    run_gun(dt)
    move_bullets(dt)
    move_rocks(dt)
    hit_rocks()
    hit_ship(dt)"""

_LOOP = """def loop(dt):
    update(dt)
    draw()


on_frame(loop)"""

_DRAW_SHIP = """def draw_ship():
    ctx.save()
    ctx.translate(ship.x, ship.y)
    ctx.rotate(ship.angle)
    ctx.stroke_style = '#e2e8f0'
    ctx.line_width = 2
    ctx.begin_path()
    ctx.move_to(ship.r, 0)
    ctx.line_to(-ship.r, -ship.r * 0.7)
    ctx.line_to(-ship.r * 0.5, 0)
    ctx.line_to(-ship.r, ship.r * 0.7)
    ctx.close_path()
    ctx.stroke()
    ctx.restore()"""

_DRAW_SHIP10 = _DRAW_SHIP.replace(
    "def draw_ship():\n",
    "def draw_ship():\n    if ship.invuln > 0 and int(ship.invuln * 10) % 2 == 1:\n        return\n",
)

_DRAW_BULLETS = """def draw_bullets():
    ctx.fill_style = '#fbd38d'
    for b in bullets:
        ctx.begin_path()
        ctx.arc(b.x, b.y, b.r, 0, math.tau)
        ctx.fill()"""

_DRAW_ROCKS = """def draw_rocks():
    ctx.stroke_style = '#a0aec0'
    ctx.line_width = 2
    for rk in rocks:
        ctx.save()
        ctx.translate(rk.x, rk.y)
        ctx.rotate(rk.angle)
        ctx.begin_path()
        for i, k in enumerate(rk.shape):
            a = i / len(rk.shape) * math.tau
            px = math.cos(a) * rk.r * k
            py = math.sin(a) * rk.r * k
            if i == 0:
                ctx.move_to(px, py)
            else:
                ctx.line_to(px, py)
        ctx.close_path()
        ctx.stroke()
        ctx.restore()"""

_HUD8 = """def draw_hud():
    ctx.fill_style = 'white'
    ctx.font = '16px monospace'
    ctx.fill_text(f'Score: {score}', 10, 20)"""

_HUD10 = _HUD8 + "\n    ctx.fill_text(f'Lives: {lives}', 10, 40)"

_HUD11 = _HUD10 + """
    if state == 'over':
        ctx.font = '32px monospace'
        ctx.fill_text('Game over', 150, 150)
        ctx.font = '16px monospace'
        ctx.fill_text(f'Score: {score} - Enter to play again', 110, 180)"""

_BG = "    ctx.fill_style = '#080b14'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)"
_CALL_SHIP = "    draw_ship()"
_CALL_BULLETS = "    draw_bullets()"
_CALL_ROCKS = "    draw_rocks()"
_CALL_HUD = "    draw_hud()"


def _draw(*calls: str) -> str:
    return "def draw():\n" + "\n".join([_BG, *calls])


def _program(imports: str, consts: str, classes: tuple[str, ...], names: str, *funcs: str) -> str:
    """One whole program: imports, constants, classes, the game's names, then each function."""
    blocks = [imports]
    if consts:
        blocks.append(consts)
    blocks.extend(classes)
    if names:
        blocks.append(names)
    blocks.extend(funcs)
    return "\n\n\n".join(b.strip("\n") for b in blocks) + "\n"


_P0 = _program(_I0, "", (), "", _UPDATE_PASS, _draw(), _LOOP)

_P1 = _program(
    _I1, _C1, (_CLASS_SHIP,), _N1,
    _TURN, _UPDATE1, _DRAW_SHIP, _draw(_CALL_SHIP), _LOOP,
)

_P2 = _program(
    _I1, _C2, (_CLASS_SHIP,), _N1,
    _TURN, _FLY2, _UPDATE2, _DRAW_SHIP, _draw(_CALL_SHIP), _LOOP,
)

_P3 = _program(
    _I1, _C3, (_CLASS_SHIP,), _N1,
    _TURN, _FLY3, _UPDATE2, _DRAW_SHIP, _draw(_CALL_SHIP), _LOOP,
)

_P4 = _program(
    _I1, _C3, (_CLASS_SHIP,), _N1,
    _TURN, _FLY4, _WRAP, _UPDATE2, _DRAW_SHIP, _draw(_CALL_SHIP), _LOOP,
)

_P5 = _program(
    _I5, _C5, (_CLASS_SHIP, _CLASS_BULLET5), _N5,
    _TURN, _FLY4, _WRAP, _FIRE, _MOVE_BULLETS5, _KEYS5, _UPDATE5,
    _DRAW_SHIP, _DRAW_BULLETS, _draw(_CALL_BULLETS, _CALL_SHIP), _LOOP,
)

_P6 = _program(
    _I1, _C6, (_CLASS_SHIP, _CLASS_BULLET6), _N6,
    _TURN, _FLY4, _WRAP, _FIRE, _GUN, _MOVE_BULLETS6, _UPDATE6,
    _DRAW_SHIP, _DRAW_BULLETS, _draw(_CALL_BULLETS, _CALL_SHIP), _LOOP,
)

_P7 = _program(
    _I7, _C6, (_CLASS_SHIP, _CLASS_BULLET6, _CLASS_ROCK), _N7,
    _TURN, _FLY4, _WRAP, _FIRE, _GUN, _MOVE_BULLETS6,
    _MAKE_ROCK, _SPAWN, _SPAWN_CALL, _MOVE_ROCKS, _UPDATE7,
    _DRAW_SHIP, _DRAW_BULLETS, _DRAW_ROCKS,
    _draw(_CALL_ROCKS, _CALL_BULLETS, _CALL_SHIP), _LOOP,
)

_P8 = _program(
    _I7, _C8, (_CLASS_SHIP, _CLASS_BULLET6, _CLASS_ROCK), _N8,
    _TURN, _FLY4, _WRAP, _FIRE, _GUN, _MOVE_BULLETS6,
    _MAKE_ROCK, _SPAWN, _SPAWN_CALL, _MOVE_ROCKS, _OVERLAP, _HIT8, _UPDATE8,
    _DRAW_SHIP, _DRAW_BULLETS, _DRAW_ROCKS, _HUD8,
    _draw(_CALL_ROCKS, _CALL_BULLETS, _CALL_SHIP, _CALL_HUD), _LOOP,
)

_P9 = _program(
    _I7, _C8, (_CLASS_SHIP, _CLASS_BULLET6, _CLASS_ROCK), _N8,
    _TURN, _FLY4, _WRAP, _FIRE, _GUN, _MOVE_BULLETS6,
    _MAKE_ROCK, _SPAWN, _SPAWN_CALL, _MOVE_ROCKS, _OVERLAP, _HIT9, _UPDATE8,
    _DRAW_SHIP, _DRAW_BULLETS, _DRAW_ROCKS, _HUD8,
    _draw(_CALL_ROCKS, _CALL_BULLETS, _CALL_SHIP, _CALL_HUD), _LOOP,
)

_P10 = _program(
    _I7, _C10, (_CLASS_SHIP10, _CLASS_BULLET6, _CLASS_ROCK), _N10,
    _TURN, _FLY4, _WRAP, _FIRE, _GUN, _MOVE_BULLETS6,
    _MAKE_ROCK, _SPAWN, _SPAWN_CALL, _MOVE_ROCKS, _OVERLAP, _HIT9, _LOSE10, _UPDATE10,
    _DRAW_SHIP10, _DRAW_BULLETS, _DRAW_ROCKS, _HUD10,
    _draw(_CALL_ROCKS, _CALL_BULLETS, _CALL_SHIP, _CALL_HUD), _LOOP,
)

_P11 = _program(
    _I11, _C10, (_CLASS_SHIP10, _CLASS_BULLET6, _CLASS_ROCK), _N11,
    _TURN, _FLY4, _WRAP, _FIRE, _GUN, _MOVE_BULLETS6,
    _MAKE_ROCK, _SPAWN, _SPAWN_CALL, _MOVE_ROCKS, _OVERLAP, _HIT9, _LOSE11, _RESET, _KEYS11, _UPDATE11,
    _DRAW_SHIP10, _DRAW_BULLETS, _DRAW_ROCKS, _HUD11,
    _draw(_CALL_ROCKS, _CALL_BULLETS, _CALL_SHIP, _CALL_HUD), _LOOP,
)

# -- The checks ---------------------------------------------------------------

_CHECK1 = _HELPERS + """
expect('ship' in g, "Make the ship: ship = Ship(240, 160) (or a dict with x, y, angle, vx, vy and r) - a name in your code, outside any function.")
s = S()
expect(near(get(s, 'x'), 240, 1) and near(get(s, 'y'), 160, 1), "The ship starts in the middle of the canvas: x 240, y 160.")
a = get(s, 'angle')
expect(isinstance(a, (int, float)) and near(math.cos(a), 0, 0.02) and near(math.sin(a), -1, 0.02), "The ship starts pointing up. Angles are in radians, 0 points right and y grows downwards, so up is -math.pi / 2.")
cc.frames(1)
d = cc.drawn()
expect(any(c['name'] == 'translate' and near(c['args'][0], get(s, 'x'), 0.5) and near(c['args'][1], get(s, 'y'), 0.5) for c in d), "Draw the ship every frame, inside draw(): ctx.translate(ship.x, ship.y) moves the origin to the ship, so the ship can be drawn around (0, 0).")
expect(sum(c['name'] == 'line_to' for c in d) >= 2 and any(c['name'] in ('stroke', 'fill') for c in d), "Draw the ship as a triangle: ctx.move_to the nose, ctx.line_to the other corners, then ctx.stroke() or ctx.fill().")
nose = next((c for c in d if c['name'] == 'move_to'), None)
expect(nose and nose['args'][0] > 0 and near(nose['args'][1], 0, 0.5), "Start the triangle at the nose, out along the +x axis: ctx.move_to(ship.r, 0). ctx.rotate turns +x to face the heading.")
put(s, 'angle', 1.2)
cc.frames(1)
expect(any(c['name'] == 'rotate' and near(c['args'][0], 1.2, 0.01) for c in cc.drawn()), "Turn the drawing to face the heading: ctx.rotate(ship.angle), after the translate and before the lines.")
stage(240, 160, 0)
cc.press('ArrowRight')
cc.frames(30)
cc.release('ArrowRight')
half = get(S(), 'angle')
expect(1 < half < 4, f"Holding ArrowRight for half a second turned the ship {half:.2f} radians; about 2 is right (TURN is 4 radians a second). Angles are radians - a full turn is math.tau, about 6.28 - not degrees (math.radians converts).")
stage(240, 160, 0)
cc.press('ArrowRight')
cc.frames(15, 1 / 30)
cc.release('ArrowRight')
got = get(S(), 'angle')
expect(near(got, half, 0.1), f"At 30 frames a second, half a second of ArrowRight turned the ship {got:.2f} radians, but at 60 it turned {half:.2f}. The turn per frame is TURN * dt, so the speed does not depend on the frame rate.")
stage(240, 160, 0)
cc.press('ArrowLeft')
cc.frames(30)
cc.release('ArrowLeft')
got = get(S(), 'angle')
expect(-4 < got < -1, f"ArrowLeft should turn the ship the other way (anticlockwise: a smaller angle); the angle is {got:.2f} after half a second.")
stage(240, 160, 0)
cc.press('ArrowLeft')
cc.press('ArrowRight')
cc.frames(20)
expect(near(get(S(), 'angle'), 0, 0.01), "Holding both arrows should cancel out and leave the ship pointing the same way.")
cc.release('ArrowLeft')
cc.release('ArrowRight')
still = get(S(), 'angle')
cc.frames(20)
expect(near(get(S(), 'angle'), still, 0.0001), "The ship kept turning after the keys were let go. It should only turn while an arrow is held.")
"""

_CHECK2 = _HELPERS + """
stage(240, 160, 0)
cc.frames(30)
expect(near(get(S(), 'vx'), 0, 0.01) and near(get(S(), 'vy'), 0, 0.01) and near(get(S(), 'x'), 240, 0.5), "With no key held the ship should sit still: only ArrowUp pushes it.")
cc.press('ArrowUp')
cc.frames(30)
cc.release('ArrowUp')
v60 = get(S(), 'vx')
expect(30 < v60 < 200, f"Facing right and holding ArrowUp for half a second, vx is {v60:.1f}; about 80 is right (THRUST is 160 pixels a second, every second). Thrust adds to the velocity (ship.vx, ship.vy), it does not move the ship directly - and x goes with math.cos(ship.angle), y with math.sin(ship.angle).")
expect(near(get(S(), 'vy'), 0, 0.5), f"Facing right, thrust should push straight right, but vy is {get(S(), 'vy'):.1f}. x uses math.cos(ship.angle) and y uses math.sin(ship.angle).")
x1 = get(S(), 'x')
cc.frames(30)
glided = get(S(), 'x') - x1
expect(glided > 20 and near(glided, get(S(), 'vx') * 0.5, 2), "After you let go, the ship should keep gliding at the speed it had: every frame ship.x += ship.vx * dt, whether or not a key is held.")
stage(240, 160, -math.pi / 2)
cc.press('ArrowUp')
cc.frames(30)
cc.release('ArrowUp')
vx, vy = get(S(), 'vx'), get(S(), 'vy')
expect(near(vx, 0, 0.5) and vy < -30, f"Facing up, thrust should push the ship up (vy negative, vx near 0); vx is {vx:.1f} and vy is {vy:.1f}. If they look swapped, you used sin for x and cos for y.")
y1 = get(S(), 'y')
cc.frames(30)
expect(y1 - get(S(), 'y') > 20 and near(get(S(), 'x'), 240, 1), "Facing up, the ship should keep gliding up after you let go: every frame ship.y += ship.vy * dt, as well as ship.x.")
stage(240, 160, math.pi)
cc.press('ArrowUp')
cc.frames(30)
cc.release('ArrowUp')
vx, vy = get(S(), 'vx'), get(S(), 'vy')
expect(vx < -30 and near(vy, 0, 0.5), f"Facing left, thrust should push the ship left (vx negative); vx is {vx:.1f}.")
stage(240, 160, 1)
cc.press('ArrowUp')
cc.frames(30)
cc.release('ArrowUp')
heading = math.atan2(get(S(), 'vy'), get(S(), 'vx'))
expect(speed() > 30 and near(heading, 1, 0.03), f"Facing a heading of 1 radian, the ship should accelerate along (math.cos(1), math.sin(1)); its velocity points at {heading:.2f} radians.")
stage(240, 160, 0)
cc.press('ArrowUp')
cc.frames(15, 1 / 30)
cc.release('ArrowUp')
expect(near(get(S(), 'vx'), v60, 2.5), f"At 30 frames a second, half a second of thrust gave vx {get(S(), 'vx'):.1f} but at 60 it gave {v60:.1f}. Thrust per frame is THRUST * dt, so the frame rate does not matter.")
"""

_CHECK3 = _HELPERS + """
stage(240, 160, 0)
put(S(), 'vx', 100)
put(S(), 'vy', -40)
s0 = speed()
cc.frames(60)
r1 = speed() / s0
expect(0.25 < r1 < 0.85, f"After a second of coasting the ship has {r1 * 100:.0f}% of its speed. Friction should take a good part of it - but not all - in a second: keep a fraction each second, DRAG ** dt.")
expect(near(math.atan2(get(S(), 'vy'), get(S(), 'vx')), math.atan2(-40, 100), 0.02), "Friction slows the ship without turning it: multiply vx and vy by the same factor.")
s1 = speed()
cc.frames(60)
expect(near(speed() / s1, r1, 0.08), "Friction should take the same fraction of the speed every second - a big speed loses more than a small one. Taking away a fixed amount makes the ship stop dead, or even roll backwards.")
stage(240, 160, 0)
put(S(), 'vx', 100)
put(S(), 'vy', -40)
cc.frames(30, 1 / 30)
kept = speed() / s0
expect(near(kept, r1, 0.05), f"After a second at 30 frames a second the ship kept {kept * 100:.0f}% of its speed, but at 60 it kept {r1 * 100:.0f}%. Use dt: DRAG ** dt, not a number per frame.")
stage(240, 160, 0)
put(S(), 'vx', 100)
cc.frames(600)
vx = get(S(), 'vx')
expect(-0.001 <= vx < 1, f"After ten seconds of coasting vx is {vx:.2f}; friction should bring the ship almost to a halt, never push it backwards.")
stage(240, 160, 0)
cc.press('ArrowUp')
cc.frames(480)
s8 = speed()
cc.frames(240)
s12 = speed()
cc.release('ArrowUp')
expect(100 < s8 < 400, f"Holding ArrowUp for 8 seconds the ship reaches {s8:.0f} pixels a second. Thrust against friction should settle around 230.")
expect(s12 < s8 * 1.05, "Thrust against friction should level out at a top speed, but the ship is still speeding up after 8 seconds.")
"""

_CHECK4 = _HELPERS + """
expect('wrap' in g and callable(g.wrap), "Write def wrap(o) that moves o to the opposite edge when it has gone off the canvas, then call wrap(ship) after moving the ship.")


def fly(x, y, vx, vy, n=30):
    stage(x, y, 0)
    put(S(), 'vx', vx)
    put(S(), 'vy', vy)
    path = [(get(S(), 'x'), get(S(), 'y'))]
    for _ in range(n):
        cc.frames(1)
        path.append((get(S(), 'x'), get(S(), 'y')))
    return path


def jumps(path, axis):
    return [i for i in range(1, len(path)) if abs(path[i][axis] - path[i - 1][axis]) > 150]


r = get(S(), 'r')
EDGES = (
    ('right', 400, 160, 300, 0, 0, WIDTH, 1),
    ('left', 80, 160, -300, 0, 0, WIDTH, -1),
    ('bottom', 240, 280, 0, 300, 1, HEIGHT, 1),
    ('top', 240, 40, 0, -300, 1, HEIGHT, -1),
)
for name, x, y, vx, vy, axis, size, way in EDGES:
    path = fly(x, y, vx, vy)
    j = jumps(path, axis)
    other = 1 - axis
    expect(j, f"The ship flew off the {name} edge and is at {'xy'[axis]} {round(path[-1][axis])}; it should come back in from the opposite edge. Every edge needs its own case - left and top as well as right and bottom.")
    expect(len(j) == 1, f"The ship flew off the {name} edge and jumped {len(j)} times; it should jump once, to the opposite side.")
    before, after = path[j[0] - 1][axis], path[j[0]][axis]
    if way > 0:
        fine = before >= size + r - 5.5 and -r - 0.5 <= after <= -r + 5.5
    else:
        fine = before <= -r + 5.5 and size + r - 5.5 <= after <= size + r + 0.5
    expect(fine, f"Off the {name} edge the ship vanished at {'xy'[axis]} {round(before)} and came back at {round(after)}. It should disappear only when it is fully off - past its radius, {size + r if way > 0 else -r} - and come back just outside the opposite edge. Give the wrap a margin of o.r each side.")
    expect(near(path[-1][other], (y, x)[axis], 3), f"Wrapping off the {name} edge moved the ship sideways: {'yx'[axis]} is {round(path[-1][other])}. Only the axis that left changes.")
path = fly(100, 100, 50, 0, 12)
expect(not jumps(path, 0) and 100 < path[-1][0] < 115 and near(path[-1][1], 100, 1), "A ship in the middle of the screen must not be moved by wrap - only one that has gone off an edge.")
"""

_CHECK5 = _HELPERS + """
expect('bullets' in g and isinstance(g.bullets, list), "Keep the bullets in a list: bullets = [] - a name in your code, outside any function.")


def fire_at(angle, vx, vy, x=240, y=160):
    stage(x, y, angle)
    put(S(), 'vx', vx)
    put(S(), 'vy', vy)
    cc.press(' ')
    cc.release(' ')
    n = len(g.bullets)
    expect(n == 1, f"Pressing Space should add exactly one bullet to bullets; there are {n}.")
    return g.bullets[0]


first = fire_at(0, 0, 0)
fx, fy = get(first, 'x'), get(first, 'y')
expect(math.hypot(fx - get(S(), 'x'), fy - get(S(), 'y')) <= get(S(), 'r') + 8 and fx > get(S(), 'x'), "The bullet should start at the ship's nose, ship.r pixels along the heading: ship.x + math.cos(ship.angle) * ship.r.")
for a in (0, 1, 2.5, -math.pi / 2):
    b = fire_at(a, 0, 0)
    bx, by = get(b, 'vx'), get(b, 'vy')
    along = (bx * math.cos(a) + by * math.sin(a)) / (math.hypot(bx, by) or 1)
    expect(along > 0.999, f"Facing {a:.2f} radians, the bullet flew off along ({bx:.0f}, {by:.0f}). A heading is (math.cos(angle), math.sin(angle)): cos for x, sin for y.")
    expect(math.hypot(bx, by) > 200, "The bullet should be fast - BULLET_SPEED is 360 pixels a second.")
moving = fire_at(-math.pi / 2, 80, 0)
mx, my = get(moving, 'vx'), get(moving, 'vy')
expect(near(mx, 80, 5) and my < -200, f"Fired straight up from a ship moving right at 80, the bullet should still drift right at 80 (it has the ship's velocity as well as its own); its velocity is ({mx:.0f}, {my:.0f}).")
f = fire_at(0, 0, 0)
x0 = get(f, 'x')
cc.frames(8, 1 / 30)
want = x0 + get(f, 'vx') * 8 / 30
expect(near(get(f, 'x'), want, 3), f"After a quarter of a second at 30 frames a second the bullet is at x {get(f, 'x'):.0f}, not {want:.0f}. Move it by velocity * dt.")
b = fire_at(0, 0, 0)
bx0 = get(b, 'x')
cc.frames(16)
expect(near(get(b, 'x'), bx0 + get(b, 'vx') * 16 / 60, 3), "At 60 frames a second the bullet is not where velocity * dt puts it.")
cc.frames(1)
expect(any(near(c['x'], get(b, 'x'), 1) and near(c['y'], get(b, 'y'), 1) for c in cc.arcs()), "Draw each bullet as a small circle: ctx.begin_path(), ctx.arc(b.x, b.y, b.r, 0, math.tau), then ctx.fill().")
edge = fire_at(0, 0, 0, 460, 160)
cc.frames(6)
expect(-30 < get(edge, 'x') < 150, f"A bullet fired off the right edge is at x {get(edge, 'x'):.0f}; bullets wrap round the screen too - call wrap(b).")
top = fire_at(-math.pi / 2, 0, 0, 240, 20)
cc.frames(6)
expect(200 < get(top, 'y') < 340, f"A bullet fired off the top is at y {get(top, 'y'):.0f}; it should come in from the bottom.")
"""

_CHECK6 = _HELPERS + """
expect('bullets' in g and isinstance(g.bullets, list), "Keep the bullets in a list: bullets = [] - a name in your code, outside any function.")
stage()
cc.press(' ')
cc.frames(1)
cc.release(' ')
expect(len(g.bullets) == 1, f"Holding Space for a frame should fire a bullet; there are {len(g.bullets)}.")
cc.frames(2)
cc.press(' ')
cc.frames(1)
cc.release(' ')
expect(len(g.bullets) == 1, "A second tap a few frames later fired again. The gun needs time to cool down: COOLDOWN seconds between shots, however the key is pressed.")
seen = {}


def hold(n, dt):
    seen.clear()
    stage()
    cc.frames(20)
    last = {}
    cc.press(' ')
    for _ in range(n):
        cc.frames(1, dt)
        now = {}
        for b in g.bullets:
            seen[id(b)] = b
            life = get(b, 'life')
            expect(isinstance(life, (int, float)), "Give each bullet a life, in seconds: Bullet has a life field (BULLET_LIFE) that counts down.")
            if id(b) in last:
                expect(near(last[id(b)] - life, dt, 1e-6), "A bullet's life did not go down by dt on every frame - one was skipped. That is what happens when you remove from a list while a for loop is walking it: the next item slides into the gap and is stepped over. Build a new list with a comprehension instead.")
            now[id(b)] = life
        last = now
    cc.release(' ')
    return len(seen)


n60 = hold(120, 1 / 60)
expect(6 <= n60 <= 10, f"Holding Space for two seconds fired {n60} bullets; with a cooldown of 0.25 seconds it should be about 8. Holding the key should keep firing, one shot every COOLDOWN seconds.")
n30 = hold(60, 1 / 30)
expect(6 <= n30 <= 10, f"At 30 frames a second, two seconds of holding Space fired {n30} bullets (60 frames a second fired {n60}). Count the cooldown down in seconds - subtract dt - not in frames.")
count = len(seen)
cc.frames(30)
for b in g.bullets:
    seen[id(b)] = b
expect(len(seen) == count, "The gun kept firing after Space was let go.")


def expiry(dt, early, late):
    stage()
    cc.frames(20)
    cc.press(' ')
    cc.frames(1, dt)
    cc.release(' ')
    expect(g.bullets, "Holding Space should fire a bullet.")
    b = g.bullets[0]
    cc.frames(early, dt)
    expect(alive(b, g.bullets), "A bullet vanished before its second was up. BULLET_LIFE is 1 second.")
    cc.frames(late, dt)
    expect(not alive(b, g.bullets), "A bullet was still flying about 1.4 seconds after it was fired. Give each bullet a life, take dt off it every frame, and remove it when it reaches 0.")


expiry(1 / 60, 36, 48)
expiry(1 / 30, 17, 24)
"""

_CHECK7 = _HELPERS + """
expect('make_rock' in g and callable(g.make_rock), "Write def make_rock(x, y, size) that returns a new rock.")
expect('spawn_rocks' in g and callable(g.spawn_rocks), "Write def spawn_rocks(n) that adds n rocks to the rocks list.")
expect('rocks' in g and isinstance(g.rocks, list) and len(g.rocks) == 4, "Call spawn_rocks(4) when the game starts, so there are four rocks to shoot, in a list called rocks.")
sx, sy = get(S(), 'x'), get(S(), 'y')
for rk in g.rocks:
    expect(math.hypot(get(rk, 'x') - sx, get(rk, 'y') - sy) >= 100, "A rock started right next to the ship. Choose a spot, and while it is within 120 pixels of the ship choose again (while True: ... break).")
g.rocks.clear()
g.spawn_rocks(30)
expect(len(g.rocks) == 30, f"spawn_rocks(30) made {len(g.rocks)} rocks.")
fields = ('x', 'y', 'vx', 'vy', 'angle', 'spin', 'size', 'r')
for rk in g.rocks:
    expect(all(isinstance(get(rk, k), (int, float)) and math.isfinite(get(rk, k)) for k in fields), "Every rock needs numbers x, y, vx, vy, angle, spin, size and r.")
    expect(near(get(rk, 'r'), get(rk, 'size') * 14, 0.5), f"A rock of size {get(rk, 'size')} has radius {get(rk, 'r')}; the radius is size * 14.")
    expect(math.hypot(get(rk, 'x') - sx, get(rk, 'y') - sy) >= 100, "A rock started right next to the ship.")
    expect(len(get(rk, 'shape') or []) >= 6, "Give each rock an outline to draw: shape, a list of ten random factors (0.75 to 1.2) that stretch the radius.")
expect(len({id(rk) for rk in g.rocks}) == 30, "spawn_rocks put the same rock in the list more than once. [make_rock(...)] * n is one rock and n names for it - call make_rock inside the loop, once per rock.")
sizes = {get(rk, 'size') for rk in g.rocks}
expect(len(sizes) >= 2 and all(s in (1, 2, 3) for s in sizes), "spawn_rocks should make rocks of random sizes - 2 or 3 - with random.choice or random.randint.")
speeds = [math.hypot(get(rk, 'vx'), get(rk, 'vy')) for rk in g.rocks]
expect(all(8 < s < 120 for s in speeds), "Rocks drift slowly: a speed of 20 to 60 pixels a second (random.uniform(20, 60)).")
expect(len({round(get(rk, 'vx')) for rk in g.rocks}) >= 15 and len({round(math.atan2(get(rk, 'vy'), get(rk, 'vx')) * 2) for rk in g.rocks}) >= 6, "Every rock should drift its own way: choose a random heading and a random speed, then vx = math.cos(heading) * speed and vy = math.sin(heading) * speed.")
expect(any(abs(get(rk, 'spin')) > 0.1 for rk in g.rocks) and all(abs(get(rk, 'spin')) < 4 for rk in g.rocks), "Rocks spin: give each a random spin (radians a second), a small number either way - random.uniform(-1, 1).")
g.rocks.clear()
rk = g.make_rock(100, 100, 3)
g.rocks.append(rk)
for k, v in (('vx', 60), ('vy', -30), ('spin', 2), ('angle', 0)):
    put(rk, k, v)
cc.frames(30, 1 / 30)
expect(near(get(rk, 'x'), 160, 1.5) and near(get(rk, 'y'), 70, 1.5), f"A rock with vx 60 and vy -30 should be at (160, 70) after a second; it is at ({get(rk, 'x'):.1f}, {get(rk, 'y'):.1f}). x += vx * dt and y += vy * dt, every frame.")
expect(near(get(rk, 'angle'), 2, 0.05), f"A rock spinning at 2 radians a second should have turned 2 radians after a second; its angle is {get(rk, 'angle'):.2f}. angle += spin * dt.")
put(rk, 'x', 100)
put(rk, 'y', 100)
put(rk, 'angle', 0)
cc.frames(60)
expect(near(get(rk, 'x'), 160, 1.5) and near(get(rk, 'angle'), 2, 0.05), "At 60 frames a second the rock is not where velocity * dt and spin * dt put it.")
cc.frames(1)
expect(any(c['name'] == 'translate' and near(c['args'][0], get(rk, 'x'), 1.5) and near(c['args'][1], get(rk, 'y'), 1.5) for c in cc.drawn()) and any(c['name'] == 'rotate' and near(c['args'][0], get(rk, 'angle'), 0.05) for c in cc.drawn()), "Draw each rock with ctx.save(), ctx.translate(rk.x, rk.y), ctx.rotate(rk.angle), the outline around (0, 0), then ctx.restore().")


def drift(x, y, vx, vy):
    for k, v in (('x', x), ('y', y), ('vx', vx), ('vy', vy), ('spin', 0)):
        put(rk, k, v)
    cc.frames(60)


r = get(rk, 'r')
drift(470, 160, 60, 0)
expect(get(rk, 'x') < 150 and get(rk, 'x') > -2 * r, f"A rock drifted off the right edge and is at x {get(rk, 'x'):.0f}; rocks wrap round the screen: call wrap(rk).")
drift(10, 160, -60, 0)
expect(350 < get(rk, 'x') < 480 + 2 * r, f"A rock drifted off the left edge and is at x {get(rk, 'x'):.0f}; it should come back in from the right.")
drift(240, 10, 0, -60)
expect(250 < get(rk, 'y') < 320 + 2 * r, f"A rock drifted off the top and is at y {get(rk, 'y'):.0f}; it should come back in from the bottom.")
drift(240, 310, 0, 60)
expect(-2 * r < get(rk, 'y') < 100, f"A rock drifted off the bottom and is at y {get(rk, 'y'):.0f}; it should come back in from the top.")
"""

_CHECK8 = _HELPERS + """
import re

expect('score' in g and isinstance(g.score, (int, float)) and g.score == 0, "Start with score = 0 - a name in your code, outside any function.")


def trial(size, dx, dy):
    stage(100, 160, 0)
    b = shoot()
    rk = rock(300, 160, size)
    put(b, 'x', get(rk, 'x') + dx)
    put(b, 'y', get(rk, 'y') + dy)
    before = g.score
    cc.frames(1)
    return alive(rk, g.rocks), alive(b, g.bullets), g.score - before


rock_there, bullet_there, gained = trial(3, 40, 0)
expect(not rock_there, "A bullet 40 pixels from the centre of a big rock (radius 42) should hit it. They overlap when the distance between the centres is less than the two radii added together: math.hypot(dx, dy) < a.r + b.r.")
expect(not bullet_there, "A bullet that hit a rock should be removed too.")
expect(gained == 20, f"Breaking a big rock is worth 20 points; the score went up by {gained}.")
rock_there, bullet_there, gained = trial(3, 33, 33)
expect(rock_there and bullet_there and gained == 0, "A bullet at the corner of a big rock's bounding square, about 47 pixels from its centre, should miss. Test the distance math.hypot(dx, dy) against the radii, not x and y one at a time.")
rock_there, bullet_there, gained = trial(1, 30, 0)
expect(rock_there and gained == 0, "A bullet 30 pixels from a small rock (radius 14) should miss. Use each rock's own radius: a.r + b.r.")
rock_there, bullet_there, gained = trial(1, 10, 0)
expect(not rock_there and not bullet_there, "A bullet 10 pixels from the centre of a small rock should hit it.")
expect(gained == 100, f"A small rock is worth 100 points; the score went up by {gained}.")
rock_there, bullet_there, gained = trial(2, 20, 0)
expect(not rock_there and not bullet_there and gained == 50, f"A medium rock is worth 50 points; the score went up by {gained} (rock gone: {not rock_there}).")
stage(100, 160, 0)
b = shoot()
for _ in range(3):
    rock(300, 160, 3)
put(b, 'x', 310)
put(b, 'y', 160)
before = g.score
cc.frames(1)
expect(len(g.rocks) == 2 and g.score - before == 20, f"Three rocks lay under one bullet: it should break one and be used up. {len(g.rocks)} are left and the score went up by {g.score - before}. Stop looking after a hit (break) - a bullet breaks one rock.")
stage(100, 160, 0)
b1 = shoot()
b2 = shoot()
rk1 = rock(100, 60, 3)
rk2 = rock(300, 260, 3)
put(b1, 'x', 100)
put(b1, 'y', 60)
put(b2, 'x', 300)
put(b2, 'y', 260)
before = g.score
cc.frames(1)
expect(not alive(rk1, g.rocks) and not alive(rk2, g.rocks) and not alive(b1, g.bullets) and not alive(b2, g.bullets) and g.score - before == 40, f"Two bullets hit two different rocks in the same frame, and both should break: {len(g.rocks)} rocks and {len(g.bullets)} bullets are left, the score went up by {g.score - before}. If you take bullets out of the list while a for loop walks it, the next bullet is skipped - build the new list afterwards instead.")
cc.frames(1)
expect(any(re.search('score', t, re.I) and str(g.score) in t for t in cc.texts()), f"Write the score on the screen: it should say Score: {g.score}.")
"""

_CHECK9 = _HELPERS + """
def smash(size):
    stage(100, 160, 0)
    b = shoot()
    parent = rock(300, 160, size)
    put(b, 'x', 310)
    put(b, 'y', 160)
    before = g.score
    cc.frames(1)
    return parent, g.score - before


parent, gained = smash(3)
expect(not alive(parent, g.rocks), "The rock that was hit is still in the rocks list. Take it out before adding its pieces.")
expect(len(g.rocks) == 2, f"Breaking a big rock should leave exactly two pieces; there are {len(g.rocks)} rocks.")
expect(all(get(c, 'size') == 2 and near(get(c, 'r'), 28, 0.5) for c in g.rocks), "The pieces of a big rock (size 3) are medium (size 2, radius 28): make_rock(rk.x, rk.y, rk.size - 1).")
expect(g.rocks[0] is not g.rocks[1], "The two pieces are the same rock twice. [make_rock(...)] * 2 is one rock with two names - call make_rock once per piece, for example in a list comprehension.")
expect(all(math.hypot(get(c, 'x') - 300, get(c, 'y') - 160) < 30 for c in g.rocks), "The pieces should start where the rock was broken.")
a, b = g.rocks
expect(math.hypot(get(a, 'vx') - get(b, 'vx'), get(a, 'vy') - get(b, 'vy')) > 2, "The two pieces should fly apart: each one needs its own random velocity (make_rock gives it one).")
expect(gained == 20, f"A big rock is still worth 20 points; the score went up by {gained}.")
parent, gained = smash(2)
expect(not alive(parent, g.rocks) and len(g.rocks) == 2 and all(get(c, 'size') == 1 and near(get(c, 'r'), 14, 0.5) for c in g.rocks), f"Breaking a medium rock should leave two small ones (size 1, radius 14); there are {len(g.rocks)} rocks.")
expect(gained == 50, f"A medium rock is still worth 50 points; the score went up by {gained}.")
parent, gained = smash(1)
expect(len(g.rocks) == 0, f"A small rock breaks into nothing; {len(g.rocks)} rocks are left.")
expect(gained == 100, f"A small rock is worth 100 points; the score went up by {gained}.")
smash(3)
cc.frames(30)
expect(len(g.rocks) == 2, f"The pieces should drift on without breaking again; {len(g.rocks)} rocks are left.")
"""

_CHECK10 = _HELPERS + """
expect('lives' in g and g.lives == 3, "Start with lives = 3 - a name in your code, outside any function.")
expect(isinstance(get(S(), 'invuln'), (int, float)), "Give the ship a number of seconds of protection: an invuln field, starting at 0.")
cc.frames(1)
expect(any('live' in t.lower() and '3' in t for t in cc.texts()), "Write the lives on the screen from the start: it should say Lives: 3.")
stage(100, 100, 0)
rock(250, 100, 3)
cc.frames(10)
expect(g.lives == 3, "A rock 150 pixels away cost a life. The ship and a rock touch when the distance between their centres is less than the two radii added together.")
stage(100, 100, 0)
rock(140, 140, 3)
cc.frames(2)
expect(g.lives == 3, "A rock whose bounding square touches the ship's, but whose circle does not (about 57 pixels away, radii 12 + 42), cost a life. Use the distance, math.hypot, not x and y separately.")
stage(100, 100, 0)
put(S(), 'vx', 40)
rk = rock(130, 100, 3)
cc.frames(1)
expect(g.lives == 2, f"The ship touched a rock and lives is {g.lives}; it should be 2.")
expect(near(get(S(), 'x'), WIDTH / 2, 1) and near(get(S(), 'y'), HEIGHT / 2, 1), "After a hit the ship goes back to the middle of the canvas.")
expect(near(get(S(), 'vx'), 0, 0.5) and near(get(S(), 'vy'), 0, 0.5), "After a hit the ship starts again standing still: vx and vy back to 0.")
expect(near(math.sin(get(S(), 'angle')), -1, 0.02), "After a hit the ship points up again: angle -math.pi / 2.")
expect(1 < get(S(), 'invuln') <= 3, f"After a hit the ship should be protected for INVULN (2) seconds; its invuln is {get(S(), 'invuln')}.")
cc.frames(1)
expect(any('live' in t.lower() and '2' in t for t in cc.texts()), "Show the new number of lives on the screen.")
put(rk, 'x', WIDTH / 2)
put(rk, 'y', HEIGHT / 2)
cc.frames(30, 1 / 30)
expect(g.lives == 2, f"A rock sat on the respawned ship for a second and lives went down to {g.lives}. While ship.invuln is above 0, rocks must not hurt it - otherwise a life goes every frame.")
shown = hidden = 0
for _ in range(20):
    cc.frames(1)
    if any(c['name'] == 'rotate' and near(c['args'][0], get(S(), 'angle'), 0.001) for c in cc.drawn()):
        shown += 1
    else:
        hidden += 1
expect(shown >= 1 and hidden >= 1, "While the ship is protected it should blink: drawn on some frames and not on others (for example when int(ship.invuln * 10) % 2 is 1, skip drawing it).")
cc.frames(30, 1 / 30)
expect(g.lives == 1, f"After the protection ran out (2 seconds) the rock still on top of the ship should cost another life; lives is {g.lives}. Count ship.invuln down in seconds with dt, not in frames.")
expect(get(S(), 'invuln') > 0, "Every life lost starts the protection again.")
"""

_CHECK11 = _HELPERS + """
import re

expect('state' in g and g.state == 'playing', "Keep what the game is doing in a top-level state = 'playing'.")
stage(100, 100, -math.pi / 2)
g.score = 50
g.lives = 3
cc.press('Enter')
cc.release('Enter')
cc.frames(2)
expect(g.score == 50 and g.lives == 3 and g.state == 'playing', "Enter in the middle of a game restarted it. Only restart when state is 'over'.")
cc.press(' ')
cc.frames(1)
cc.release(' ')
expect(len(g.bullets) == 1, "Fire a bullet before dying: Space should still work while the game is on.")
cc.frames(7)
put(S(), 'vx', 20)
put(S(), 'vy', -10)
g.lives = 1
rk = rock(130, 100, 3)
cc.frames(1)
expect(g.lives == 0, f"The ship hit a rock on its last life and lives is {g.lives}; it should be 0.")
expect(g.state == 'over', f"With no lives left state is {g.state!r}; it should be 'over'. lose_life assigns state, so it needs `global state` - without it Python makes a quiet local variable and the real one never changes.")
cc.frames(1)
expect(any(re.search('game over', t, re.I) for t in cc.texts()), "When the game is over, say so on the screen.")
before = (get(rk, 'x'), get(S(), 'x'), get(S(), 'angle'), len(g.bullets))
put(rk, 'vx', 60)
for k in ('ArrowLeft', 'ArrowUp', ' '):
    cc.press(k)
cc.frames(30)
for k in ('ArrowLeft', 'ArrowUp', ' '):
    cc.release(k)
after = (get(rk, 'x'), get(S(), 'x'), get(S(), 'angle'), len(g.bullets))
expect(before == after, "After game over everything should freeze: no flying, no turning, no firing, no drifting rocks. Return from update when state is not 'playing'.")
cc.press('ArrowRight')
cc.frames(2)
cc.release('ArrowRight')
expect(g.state == 'over', "A key other than Enter restarted the game. Only Enter should.")
cc.press('Enter')
cc.release('Enter')
expect(g.state == 'playing', f"Pressing Enter after game over should start a new game; state is {g.state!r}. reset() assigns state, so it needs `global state`.")
expect(g.score == 0 and g.lives == 3, f"A new game starts with a score of 0 and 3 lives; they are {g.score} and {g.lives}. reset() re-binds them, so each needs a name on its `global` line - without it `score = 0` makes a quiet local variable.")
expect(len(g.bullets) == 0, "A new game should start with no bullets in the air: empty the bullets list.")
expect(len(g.rocks) == 4, f"A new game starts with 4 new rocks (the old ones gone); there are {len(g.rocks)}. Empty the rocks list, then spawn_rocks(4).")
expect(all(math.hypot(get(r, 'x') - get(S(), 'x'), get(r, 'y') - get(S(), 'y')) >= 100 for r in g.rocks), "The new rocks should start well away from the ship.")
expect(near(get(S(), 'x'), WIDTH / 2, 1) and near(get(S(), 'y'), HEIGHT / 2, 1) and near(get(S(), 'vx'), 0, 0.5) and near(get(S(), 'vy'), 0, 0.5), "A new game starts with the ship still, in the middle.")
expect(near(math.sin(get(S(), 'angle')), -1, 0.02), "A new game starts with the ship pointing up.")
cc.press(' ')
cc.frames(1)
cc.release(' ')
expect(len(g.bullets) == 1, "In the new game Space should fire at once: put cooldown back to 0 too.")
cc.frames(30)
expect(g.lives == 3 and g.state == 'playing', "The new game should not start with the ship already hit.")
cc.frames(1)
expect(not any(re.search('game over', t, re.I) for t in cc.texts()), "'Game over' is still on the screen after the restart.")
"""


def _step(**fields: object) -> Step:
    """A step on this track: Python, in the Python Asteroids track."""
    fields["track"] = TRACK
    fields["language"] = "python"
    return Step(**fields)  # type: ignore[arg-type]


PYASTEROIDS_STEPS: tuple[Step, ...] = (
    _step(
        id="pyast-01-turn",
        title="A ship that turns",
        teaches=(
            "Asteroids is a game about angles. The ship has a heading, one "
            "number in RADIANS: 0 points right, and because y grows "
            "downwards a positive angle turns clockwise, so straight up is "
            "-math.pi / 2. A full turn is math.tau (2 * pi, about 6.28), so "
            "'turn 4 a second' is about two thirds of a circle. Never "
            "degrees: math.cos, math.sin and ctx.rotate all want radians, "
            "and math.radians(90) is how you convert one you already have. "
            "Ship is a @dataclass - the fields with a = after them are "
            "defaults, so Ship(240, 160) is enough. To steer, a bool is a "
            "number in Python (True is 1, False is 0), so ('ArrowRight' in "
            "keys) - ('ArrowLeft' in keys) is +1, -1 or 0. To draw a turned "
            "ship, ctx.translate to the ship and ctx.rotate by the heading; "
            "draw the nose along +x. Wrap it in ctx.save() and "
            "ctx.restore() so the turn does not leak."
        ),
        goal="Add a Ship dataclass (x, y, angle, vx, vy, r) and make ship = Ship(240, 160) - angle -math.pi / 2 (straight up), vx and vy 0, r 12; a dict with those keys works too. Add TURN = 4 and turn_ship(dt), called from update(dt): ArrowRight turns the ship clockwise and ArrowLeft anticlockwise, TURN radians a second. Draw the ship every frame as a triangle: ctx.translate(ship.x, ship.y), ctx.rotate(ship.angle), the nose along +x. The check reads ship.",
        starter=_P0,
        solution=_P1,
        check=_CHECK1,
        hint="turn = ('ArrowRight' in keys) - ('ArrowLeft' in keys); ship.angle += turn * TURN * dt   and in draw_ship: ctx.save(); ctx.translate(ship.x, ship.y); ctx.rotate(ship.angle); ... ctx.restore()",
    ),
    _step(
        id="pyast-02-thrust",
        title="Thrust along the heading",
        teaches=(
            "Thrust pushes the ship the way it faces, and 'the way it "
            "faces' is two numbers: math.cos(angle) is how far along x, "
            "math.sin(angle) how far along y. Cos goes with x and sin with "
            "y - swap them and the ship flies sideways. (math.atan2(dy, dx) "
            "is the way back, from a direction to an angle. Python can also "
            "hold the pair as one complex number - cmath.rect(1, angle) - "
            "or as a pygame Vector2; two plain floats keep it simple here.) "
            "The push changes the VELOCITY (vx, vy) in pixels per second, "
            "not the position: every frame position += velocity * dt. That "
            "one change is what makes it feel like space - let go of the "
            "key and the ship keeps gliding, because velocity stays until "
            "something changes it. Acceleration is pixels per second PER "
            "second, so it is THRUST * dt."
        ),
        goal="Add THRUST = 160 and fly_ship(dt), called from update(dt) after turn_ship. While ArrowUp is held, add math.cos(ship.angle) * THRUST * dt to ship.vx and the sin version to ship.vy. Every frame, move the ship by its velocity: ship.x += ship.vx * dt, ship.y += ship.vy * dt. The check reads ship.",
        starter=_P1,
        solution=_P2,
        check=_CHECK2,
        hint="if 'ArrowUp' in keys: ship.vx += math.cos(ship.angle) * THRUST * dt; ship.vy += math.sin(ship.angle) * THRUST * dt   then   ship.x += ship.vx * dt; ship.y += ship.vy * dt",
    ),
    _step(
        id="pyast-03-friction",
        title="A little friction",
        teaches=(
            "Real space has no friction, but a game with none is nearly "
            "impossible to fly: you can never stop, and every mistake "
            "stays for ever. A touch of drag gives the ship a top speed "
            "and lets it settle. The trap is how: 'vx *= 0.99' each frame "
            "slows a 60 fps screen twice as fast as a 30 fps one. Say "
            "instead what fraction of the speed is KEPT after one whole "
            "second (DRAG = 0.5 keeps half) and scale it to this frame "
            "with a power: DRAG ** dt. Python's ** takes a float exponent, "
            "and the same formula is math.exp(-k * dt) written another "
            "way. Multiply BOTH vx and vy by the same number - friction "
            "slows the ship, it does not turn it. A fraction also never "
            "reverses the ship, which taking away a fixed amount would."
        ),
        goal="Add DRAG = 0.5, the fraction of its speed the ship keeps after one second. In fly_ship, before the ship moves, multiply ship.vx and ship.vy by DRAG ** dt. The check reads ship.",
        starter=_P2,
        solution=_P3,
        check=_CHECK3,
        hint="damp = DRAG ** dt; ship.vx *= damp; ship.vy *= damp   (after the thrust, before ship.x += ...)",
    ),
    _step(
        id="pyast-04-wrap",
        title="Round the edges",
        teaches=(
            "In Asteroids the screen is a doughnut: fly off one edge and "
            "you come in on the opposite one. Python has the tool built in: "
            "the % operator. x % WIDTH always lands in 0 to WIDTH, and "
            "unlike JavaScript - where -5 % 480 is -5, so you need ((x % w) "
            "+ w) % w - Python gives 475 for a negative number, so one "
            "expression covers the left edge too. But modulo alone makes a "
            "ship pop out the instant its CENTRE crosses the edge, half of "
            "it still on screen. Give it a margin of the thing's own "
            "radius, so it disappears completely before it reappears: the "
            "stage is WIDTH + 2 * o.r wide, starting at -o.r, so "
            "(o.x + o.r) % (WIDTH + 2 * o.r) - o.r. An if / elif for each "
            "of the four edges works too - but forget one (the classic: "
            "only the right and bottom) and the ship is lost for ever. "
            "Write it once as wrap(o) for anything with x, y and r."
        ),
        goal="Write wrap(o): an object that goes off one edge comes in on the opposite one, on all four edges, once it is fully off (past its radius o.r) - and it comes back just outside that edge. Call wrap(ship) at the end of fly_ship. The check reads ship and wrap.",
        starter=_P3,
        solution=_P4,
        check=_CHECK4,
        hint="o.x = (o.x + o.r) % (WIDTH + 2 * o.r) - o.r   and the same for y with HEIGHT.   (Or: if o.x < -o.r: o.x = WIDTH + o.r  elif o.x > WIDTH + o.r: o.x = -o.r ...)",
    ),
    _step(
        id="pyast-05-bullets",
        title="Fire along the heading",
        teaches=(
            "A bullet leaves the nose in the direction the ship faces, so "
            "it is the thrust trick again: (math.cos(angle), math.sin("
            "angle)) times a speed. Work the pair out once with tuple "
            "unpacking - c, s = math.cos(a), math.sin(a) - and use it "
            "twice. Start the bullet at the nose, ship.r along the "
            "heading, so it does not appear in the middle of the hull. "
            "And ADD the ship's own velocity: a bullet fired while flying "
            "sideways keeps drifting sideways, as it would in space. A "
            "Bullet is another @dataclass - x, y, vx, vy and an r of 2 as "
            "a default, so wrap(b) and, later, the collision test can "
            "treat it as a small circle. Bullets live in a list, moved "
            "every frame like everything else, and wrapped like "
            "everything else. on_key_down(fn) calls fn(key) the moment a "
            "key goes down - the space bar is ' '."
        ),
        goal="Add BULLET_SPEED = 360, a Bullet dataclass (x, y, vx, vy, r = 2) and bullets = [], a list. Pressing Space (on_key_down) appends a Bullet at the ship's nose, flying along the heading at BULLET_SPEED plus the ship's own velocity. Write move_bullets(dt), called from update(dt), to move and wrap the bullets every frame, and draw each as a small filled circle. The check reads ship and bullets.",
        starter=_P4,
        solution=_P5,
        check=_CHECK5,
        hint="c, s = math.cos(ship.angle), math.sin(ship.angle); bullets.append(Bullet(ship.x + c * ship.r, ship.y + s * ship.r, ship.vx + c * BULLET_SPEED, ship.vy + s * BULLET_SPEED))",
    ),
    _step(
        id="pyast-06-gun",
        title="A gun that cools, bullets that expire",
        teaches=(
            "Two problems with the last step. A bullet that wraps round "
            "for ever fills the sky and the list: give each one a life in "
            "seconds (a field with a default, life: float = BULLET_LIFE), "
            "take dt off every frame, and drop it at zero. Drop it with a "
            "list comprehension - bullets = [b for b in bullets if "
            "b.life > 0] - and NOT with bullets.remove(b) inside the "
            "`for b in bullets:` that is walking the list: removing "
            "shifts the next bullet into the gap and the loop steps over "
            "it, a bug that only shows when two bullets are in the air. "
            "Re-binding the name needs `global bullets` (bullets[:] = [...] "
            "changes it in place and needs none). And a space bar that "
            "fires on every key event is either one shot per press or a "
            "firehose. A gun wants a COOLDOWN: seconds left before it can "
            "fire again, max(0, cooldown - dt) each frame, set when you "
            "fire. That is another re-bound name - leave `global "
            "cooldown` off and Python raises UnboundLocalError. Count it "
            "in seconds, never frames."
        ),
        goal="Add BULLET_LIFE = 1, COOLDOWN = 0.25 and cooldown = 0. Give Bullet a life field (BULLET_LIFE): move_bullets takes dt off it each frame and drops the bullets at 0 or less - build a new list with a comprehension, with `global bullets`. Replace the key press with run_gun(dt) in update: while Space is held in keys it fires whenever cooldown is 0, then sets it to COOLDOWN; it counts down by dt. The check reads ship and bullets (cooldown is yours).",
        starter=_P5,
        solution=_P6,
        check=_CHECK6,
        hint="cooldown = max(0, cooldown - dt); if ' ' in keys and cooldown <= 0: fire(); cooldown = COOLDOWN   (global cooldown)   and   b.life -= dt   then   bullets = [b for b in bullets if b.life > 0]   (global bullets)",
    ),
    _step(
        id="pyast-07-rocks",
        title="Rocks that drift and spin",
        teaches=(
            "The rocks are bullets with more to them: a position, a "
            "velocity, and a spin - radians per second, added to the angle "
            "each frame, so it too is spin * dt. A Rock is a @dataclass "
            "again, with one new thing: its outline is a LIST of ten radius "
            "factors, and a list cannot be a plain default - `shape: list "
            "= []` is refused with ValueError (mutable default) to stop "
            "every rock sharing ONE list, the same trap as def f(seen=[]). "
            "Write shape: list = field(default_factory=list) "
            "(from dataclasses import field) and each rock gets its own. "
            "make_rock(x, y, size) has the randomness in it: random.uniform "
            "for a heading (0 to math.tau) and a speed, then cos and sin "
            "turn the pair into vx and vy; for a spin; random.choice((2, "
            "3)) or random.randint(2, 3) for a size; and a list "
            "comprehension, [random.uniform(0.75, 1.2) for _ in range(10)], "
            "for the outline. The outline is picked once and kept, so a "
            "rock turns as a lumpy shape; enumerate gives each point its "
            "number when you draw it. Spawn them away from the ship: Python "
            "has no do-while, so while True: pick a spot; if far enough: "
            "break."
        ),
        goal="Add a Rock dataclass (x, y, vx, vy, size, r, angle, spin, shape - shape built with field(default_factory=list)) and rocks = []. Write make_rock(x, y, size), which returns a Rock with r = size * 14, a random heading and speed (20 to 60 pixels a second), a random angle and spin, and a shape of ten random factors; and spawn_rocks(n), which appends n rocks of size 2 or 3, each at least 120 pixels from the ship. Call spawn_rocks(4) at the start. move_rocks(dt) moves, spins and wraps every rock; draw each with translate and rotate. The check reads ship, rocks, make_rock and spawn_rocks.",
        starter=_P6,
        solution=_P7,
        check=_CHECK7,
        hint="heading = random.uniform(0, math.tau); speed = random.uniform(20, 60); vx = math.cos(heading) * speed; vy = math.sin(heading) * speed   and   rk.x += rk.vx * dt; rk.y += rk.vy * dt; rk.angle += rk.spin * dt; wrap(rk)",
    ),
    _step(
        id="pyast-08-shoot",
        title="Shoot a rock",
        teaches=(
            "Two circles overlap when the distance between their centres "
            "is less than the sum of their radii: math.hypot(dx, dy) < "
            "a.r + b.r. That is not comparing x and y separately, which "
            "tests a SQUARE around each circle: a bullet near the corner "
            "of that square is miles from a round rock yet counts as a "
            "hit. (To skip the square root, compare squares - dx * dx + "
            "dy * dy < (a.r + b.r) ** 2 - but square BOTH sides: leave the "
            "radii as they are and every hit is missed.) Use each thing's "
            "own radius, so a small rock is harder to hit than a big one. "
            "Every bullet against every rock is a nested loop (itertools."
            "product(bullets, rocks) is the same pairs in one for, but it "
            "cannot break out of just the inner loop). A hit takes the "
            "rock out and spends the bullet - score += POINTS[rk.size], a "
            "dict lookup - and one bullet breaks one rock, so break. "
            "Removing from a list inside the for that walks it skips the "
            "next item; here it is safe only because of the break, and "
            "bullets are not removed in their own loop at all - they are "
            "spent (b.life = 0) and the comprehension drops them after. "
            "any() answers 'is there a hit?' when you do not need which. "
            "Show the score with an f-string: f'Score: {score}'."
        ),
        goal="Add POINTS = {1: 100, 2: 50, 3: 20} and score = 0. Write overlap(a, b), true when two circles (anything with x, y and r) overlap, and hit_rocks(), called from update(dt): when a bullet overlaps a rock, remove the rock, drop the bullet and add POINTS[rock.size] to score. One bullet breaks at most one rock. Write the score on the screen, as Score: 0. bullets, rocks and score are re-bound by hit_rocks (global). The check reads ship, bullets, rocks, score and make_rock.",
        starter=_P7,
        solution=_P8,
        check=_CHECK8,
        hint="math.hypot(a.x - b.x, a.y - b.y) < a.r + b.r   then: for b in bullets: for rk in live: if overlap(b, rk): score += POINTS[rk.size]; live.remove(rk); b.life = 0; break   and  bullets = [b for b in bullets if b.life > 0]",
    ),
    _step(
        id="pyast-09-split",
        title="Rocks break in two",
        teaches=(
            "A hit rock does not just vanish: a big one breaks into two "
            "medium ones, a medium into two small, and a small one is "
            "gone. break_rock(rk) answers 'what is left?' with a list - "
            "[] for the smallest, otherwise two rocks one size down, made "
            "by make_rock at the parent's position. Build the two with "
            "[make_rock(...) for _ in range(2)]. NOT [make_rock(...)] * 2: "
            "that makes ONE rock and puts it in the list twice, two names "
            "for the same object, so the pieces fly together and break "
            "together. Keep the pieces in their own list (pieces += "
            "break_rock(rk)) and join it on at the end, rocks = live + "
            "pieces: they join the game next frame, not in the middle of "
            "this one's loops. Forget to take the parent out and it stays "
            "behind to be hit again, for ever. make_rock gives each child "
            "its own random heading, speed and spin, so the two fly apart "
            "on their own."
        ),
        goal="Add break_rock(rk), which returns the pieces of a broken rock: an empty list for a rock of size 1, otherwise two rocks of size - 1 made with make_rock at its position. hit_rocks removes the hit rock and adds its pieces to rocks. The score and the one-bullet-one-rock rule stay as they were. The check reads ship, bullets, rocks, score and make_rock.",
        starter=_P8,
        solution=_P9,
        check=_CHECK9,
        hint="def break_rock(rk): if rk.size == 1: return []   return [make_rock(rk.x, rk.y, rk.size - 1) for _ in range(2)]   and in hit_rocks: live.remove(rk); pieces += break_rock(rk)   ...   rocks = live + pieces",
    ),
    _step(
        id="pyast-10-lives",
        title="Lives and a second chance",
        teaches=(
            "A ship touching a rock is the same circle test as before, "
            "ship against rock - and any() says it in one line: "
            "any(overlap(ship, rk) for rk in rocks) is True as soon as one "
            "rock touches. What is new is the aftermath. Losing a life "
            "puts the ship back in the middle, stopped, and then protects "
            "it: a short invulnerability, a number of seconds left that "
            "counts down with dt (max(0, ship.invuln - dt)), during which "
            "rocks cannot hurt it. Without that, a rock drifting over the "
            "respawn point takes a life EVERY FRAME and three lives are "
            "gone in a twentieth of a second. Tuple unpacking sets two "
            "fields at once - ship.x, ship.y = WIDTH / 2, HEIGHT / 2 - and "
            "a chained assignment, ship.vx = ship.vy = 0, zeroes two. "
            "lose_life re-binds lives, so it needs `global lives`. "
            "Flashing the ship while it is protected tells the player why "
            "nothing is happening: int(ship.invuln * 10) % 2 flips every "
            "tenth of a second. Count the protection in seconds, not "
            "frames, or it lasts twice as long on a slow screen. "
            "f'Lives: {lives}' shows the count."
        ),
        goal="Add lives = 3, INVULN = 2 and an invuln field on Ship (0 to start). Write hit_ship(dt), called from update(dt): ship.invuln counts down by dt, and when it is 0 or less and the ship overlaps a rock, lose_life() takes a life, puts the ship back in the middle (stopped and pointing up) and sets ship.invuln to INVULN. Make the ship blink while it is above 0. Write the lives on the screen, as Lives: 3. The check reads ship, rocks, lives and make_rock.",
        starter=_P9,
        solution=_P10,
        check=_CHECK10,
        hint="ship.invuln = max(0, ship.invuln - dt); if ship.invuln <= 0 and any(overlap(ship, rk) for rk in rocks): lose_life()   and lose_life: global lives; lives -= 1; ship.x, ship.y = WIDTH / 2, HEIGHT / 2; ship.vx = ship.vy = 0; ship.invuln = INVULN",
    ),
    _step(
        id="pyast-11-over",
        title="Game over, play again",
        teaches=(
            "When the last life goes, the game stops being a simulation "
            "and becomes a screen. Keep what the game is doing in one "
            "word, state: 'playing' or 'over'. update returns at once "
            "when it is not 'playing' - no flying, firing or drifting "
            "rocks - and draw adds the 'Game over' message. A restart "
            "is a function that puts EVERY piece back: the ship "
            "(position, speed, heading, protection), the gun's cooldown, "
            "the bullets and rocks (new empty lists, then spawn new rocks "
            "- forget and the old ones are still out there), the score "
            "and the lives. Every name it re-binds goes on its `global` "
            "line: leave `state` off and `state = 'playing'` quietly makes "
            "a local variable while the real one stays 'over', and the "
            "game never restarts. lose_life needs `global state` too. "
            "Miss one piece and the second game plays differently from the "
            "first. Bind it to Enter with on_key_down, and only when the "
            "game is over."
        ),
        goal="Add state = 'playing'. When lives reaches 0, set state to 'over' and stop updating the game (draw 'Game over' on the screen). Write reset(), which puts the ship (in the middle, still, pointing up, invuln 0), cooldown, bullets, rocks (4 new ones), score, lives and state back as they began; Enter calls it through on_key_down, but only when the game is over. bullets, rocks, cooldown, score, lives and state are re-bound by reset (global). The check reads ship, bullets, rocks, score, lives and state.",
        starter=_P10,
        solution=_P11,
        check=_CHECK11,
        hint="def reset(): global bullets, rocks, cooldown, score, lives, state; place_ship(); ship.invuln = 0; cooldown = 0; bullets = []; rocks = []; spawn_rocks(4); score = 0; lives = 3; state = 'playing'   and   if key == 'Enter' and state == 'over': reset()",
    ),
    _step(
        id="pyast-12-yours",
        title="Now it's yours",
        teaches=(
            "A whole arcade game on angles. Ideas, easier first: draw a "
            "flame behind the ship while ArrowUp is held; a new wave of "
            "bigger rocks when the last one goes (a for / else, or "
            "`if not rocks:`); a hyperspace key that jumps to a random "
            "spot with random.uniform; a ship that BOUNCES off the edges "
            "instead of wrapping - flip the velocity with math.copysign("
            "ship.vx, -1); a small saucer that crosses the screen and "
            "shoots back, aimed with math.atan2(dy, dx) - the inverse of "
            "cos and sin; an extra life every 10000 points; a high score "
            "written to a file with json; rocks that shatter into sparks "
            "(a particle dataclass with a life, culled like the bullets); "
            "an after(2, fn) timer for a power-up. Or make the ship turn "
            "at the speed you hold the key: what does that do to the feel?"
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_P11,
        solution=_P11,
        check="",
    ),
)
