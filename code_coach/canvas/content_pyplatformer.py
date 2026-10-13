"""Platformer in Python: the side-on game of the JavaScript Platformer track, taught the Python way.

Not a transliteration. The game is the same - gravity as an acceleration, a
jump only from the ground, running with momentum, a level that is a grid of
tiles, collision settled one axis at a time, nothing tunnelling, one-way
ledges, a jump that forgives, coins, a flag and a respawn, a scrolling camera -
but the parts are Python's own:

  * the map is a list of strings (`level[row][col]`, rows first), `enumerate`
    walks it, and a triple-quoted map goes through `textwrap.dedent` and
    `str.splitlines`; the solid tiles are a `set` (`SOLID = {'#'}`) tested
    with `in`
  * pixel to tile is `//` (floor division, which rounds a negative number
    down - `int()` rounds it toward zero and puts the player in the wrong
    tile), `divmod`, `math.floor` and `math.ceil`; the tiles a box covers are
    a `range`, and `any()` over a generator asks "is any of them solid?"
  * the player is a `@dataclass` (a dict with the same keys works too, and
    every check accepts both); a hit is a tuple, `col, _ = tile_of(x, y)`
  * `keys` is a real `set`, so `keys & JUMP_KEYS` asks about two keys at once
  * `min` / `max` clamp, `abs` and `math.copysign` handle the sign of a speed,
    `START = (64, 258)` unpacks into `player.x, player.y`
  * a negative index is not an error in Python: `level[-1]` is the LAST row,
    which is why a tile lookup needs a guard; `if row:` is false for row 0
  * f-strings for the HUD, `global` only where a function re-binds a
    top-level name (`score`, `state`, `camera_x`) - and what Python does
    when it is missing (UnboundLocalError, or a quiet local)

As in the other tracks, each step starts from the one before, finished, and a
check plays the game rather than reading the code. The checks read these
top-level names, and set them: player, level, TILE, coins, score, START,
state, camera_x (or camera). `level` is a list of strings that the checks
replace with their own worlds of the same size (`g.level = [...]`), so a
program must read the global `level` each time and never keep a copy.
`score`, `state` and `camera_x` are re-bound by the program, so a check
always looks them up again rather than holding on to one.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

TRACK = "Platformer (Python)"

# -- Shared check helpers ---------------------------------------------------

#: Prepended to every check. The player's fields can be a dict's or an object's,
#: so a check reads them with get() and writes them with put(), and never cares
#: which the learner chose. P() looks the player up afresh. place() puts the
#: player somewhere, still. tap() is a one-frame key press. feet() is the y of
#: the player's feet.
_HELPERS = """import math
import re


def get(o, k, default=None):
    if isinstance(o, dict):
        return o.get(k, default)
    return getattr(o, k, default)


def put(o, k, v):
    if isinstance(o, dict):
        o[k] = v
    else:
        setattr(o, k, v)


def P():
    return g.player


def feet():
    return get(P(), 'y') + get(P(), 'h')


def grounded():
    return bool(get(P(), 'on_ground'))


def place(x, y):
    p = P()
    put(p, 'x', x)
    put(p, 'y', y)
    put(p, 'vx', 0)
    put(p, 'vy', 0)


def tap(key, dt=1 / 60):
    cc.press(key)
    cc.frames(1, dt)
    cc.release(key)


"""

#: From step 4 on: a check that needs a level builds its own, by replacing
#: `level` with a new list of the same size, so it does not depend on the map
#: the learner drew. clear() is open air over a solid floor (the bottom row,
#: y 288); lay() lays tiles in a row; no_floor() is open air all the way down.
_WORLD = """W = len(g.level[0])
H = len(g.level)
OPEN = '.' * W


def clear():
    g.level = [OPEN] * (H - 1) + ['#' * W]


def no_floor():
    g.level = [OPEN] * H


def lay(r, first, last, ch):
    rows = list(g.level)
    rows[r] = rows[r][:first] + ch * (last - first + 1) + rows[r][last + 1:]
    g.level = rows


"""

# -- The programs -----------------------------------------------------------

_I0 = "from canvas import ctx, WIDTH, HEIGHT, on_frame"
_I1 = "from dataclasses import dataclass\n\nfrom canvas import ctx, WIDTH, HEIGHT, on_frame"
_I2 = "from dataclasses import dataclass\n\nfrom canvas import ctx, WIDTH, HEIGHT, on_frame, keys"
_I3 = "import math\nfrom dataclasses import dataclass\n\nfrom canvas import ctx, WIDTH, HEIGHT, on_frame, keys"

_K1 = "GRAVITY = 1800\nFLOOR = 288"
_K2 = "GRAVITY = 1800\nJUMP = 620\nJUMP_KEYS = {'ArrowUp', ' '}\nFLOOR = 288"
_K3 = (
    "GRAVITY = 1800\nJUMP = 620\nJUMP_KEYS = {'ArrowUp', ' '}\n"
    "ACCEL = 1600\nFRICTION = 1400\nMAX_SPEED = 220\nFLOOR = 288"
)
_K4 = _K3 + "\nTILE = 32"
_K5 = (
    "GRAVITY = 1800\nJUMP = 620\nJUMP_KEYS = {'ArrowUp', ' '}\n"
    "ACCEL = 1600\nFRICTION = 1400\nMAX_SPEED = 220\nTILE = 32\nSOLID = {'#'}"
)
_K7 = _K5 + "\nMAX_FALL = 900\nMAX_DT = 1 / 30"
_K9 = _K7 + "\nCOYOTE = 0.1\nJUMP_CUT = 200"
_K11 = _K9 + "\nSTART = (64, 258)"

_LEVEL = """level = [
    '#............................#',
    '#............................#',
    '#............................#',
    '#............................#',
    '#.........oo.................#',
    '#........====.........oo.....#',
    '#....oo..............====....#',
    '#...====.........##..........#',
    '#..............o.##......o.F.#',
    '###########...################',
]"""

_CLASS_PLAYER = """@dataclass
class Player:
    x: float = 64
    y: float = 0
    w: float = 24
    h: float = 30
    vx: float = 0
    vy: float = 0
    on_ground: bool = False"""

_CLASS_PLAYER9 = _CLASS_PLAYER + "\n    coyote: float = 0"

_N1 = "player = Player()"
_N4 = _LEVEL + "\n\n\n" + _N1

_COINS = """coins = [
    {'x': col * TILE + TILE / 2, 'y': row * TILE + TILE / 2, 'taken': False}
    for row, line in enumerate(level)
    for col, tile in enumerate(line)
    if tile == 'o'
]
score = 0"""

_N10 = _N4 + "\n\n\n" + _COINS
_N11 = _N10 + "\nstate = 'playing'"
_N12 = _N11 + "\ncamera_x = 0"

_FALL = """def fall(dt):
    player.vy += GRAVITY * dt
    player.y += player.vy * dt
    player.on_ground = False
    if player.y + player.h >= FLOOR:
        player.y = FLOOR - player.h
        player.vy = 0
        player.on_ground = True"""

_JUMP = """def jump():
    if player.on_ground and keys & JUMP_KEYS:
        player.vy = -JUMP
        player.on_ground = False"""

_JUMP9 = """def jump(dt):
    jump_held = bool(keys & JUMP_KEYS)
    if player.on_ground:
        player.coyote = COYOTE
    else:
        player.coyote -= dt
    if jump_held and player.coyote > 0:
        player.vy = -JUMP
        player.coyote = 0
    if not jump_held and player.vy < -JUMP_CUT:
        player.vy = -JUMP_CUT"""

_RUN = """def run(dt):
    direction = ('ArrowRight' in keys) - ('ArrowLeft' in keys)
    if direction:
        player.vx += direction * ACCEL * dt
    else:
        slow = min(abs(player.vx), FRICTION * dt)
        player.vx -= math.copysign(slow, player.vx)
    player.vx = max(-MAX_SPEED, min(MAX_SPEED, player.vx))"""

_TILES5 = """def tile_of(x, y):
    return int(x // TILE), int(y // TILE)


def tile_at(col, row):
    if col < 0 or col >= len(level[0]):
        return '#'
    if row < 0 or row >= len(level):
        return '.'
    return level[row][col]


def tiles_covered(start, size):
    return range(math.floor(start / TILE), math.ceil((start + size) / TILE))


def touches(kinds):
    cols = tiles_covered(player.x, player.w)
    rows = tiles_covered(player.y, player.h)
    return any(tile_at(col, row) in kinds for row in rows for col in cols)"""

_MOVE_Y5 = """def move_y(dt):
    player.vy += GRAVITY * dt
    player.y += player.vy * dt
    player.on_ground = False
    if touches(SOLID):
        if player.vy > 0:
            _, row = tile_of(player.x, player.y + player.h)
            player.y = row * TILE - player.h
            player.on_ground = True
        else:
            _, row = tile_of(player.x, player.y)
            player.y = (row + 1) * TILE
        player.vy = 0"""

_MOVE_X = """def move_x(dt):
    player.x += player.vx * dt
    if touches(SOLID):
        if player.vx > 0:
            col, _ = tile_of(player.x + player.w, player.y)
            player.x = col * TILE - player.w
        else:
            col, _ = tile_of(player.x, player.y)
            player.x = (col + 1) * TILE
        player.vx = 0"""

_MOVE_Y7 = _MOVE_Y5.replace(
    "    player.vy += GRAVITY * dt\n",
    "    player.vy = min(player.vy + GRAVITY * dt, MAX_FALL)\n",
)

_ONE_WAY = """def one_way_row(prev_bottom):
    _, row = tile_of(player.x, player.y + player.h)
    if prev_bottom > row * TILE:
        return None
    if any(tile_at(col, row) == '=' for col in tiles_covered(player.x, player.w)):
        return row
    return None"""

_MOVE_Y8 = """def move_y(dt):
    prev_bottom = player.y + player.h
    player.vy = min(player.vy + GRAVITY * dt, MAX_FALL)
    player.y += player.vy * dt
    player.on_ground = False
    if touches(SOLID):
        if player.vy > 0:
            _, row = tile_of(player.x, player.y + player.h)
            player.y = row * TILE - player.h
            player.on_ground = True
        else:
            _, row = tile_of(player.x, player.y)
            player.y = (row + 1) * TILE
        player.vy = 0
    elif player.vy > 0:
        row = one_way_row(prev_bottom)
        if row is not None:
            player.y = row * TILE - player.h
            player.vy = 0
            player.on_ground = True"""

_COLLECT = """def collect_coins():
    global score
    cx = player.x + player.w / 2
    cy = player.y + player.h / 2
    for c in coins:
        if c['taken']:
            continue
        if abs(c['x'] - cx) < 8 + player.w / 2 and abs(c['y'] - cy) < 8 + player.h / 2:
            c['taken'] = True
            score += 1"""

_GOAL = """def respawn():
    player.x, player.y = START
    player.vx = player.vy = 0


def check_goal():
    global state
    if player.y > HEIGHT + 100:
        respawn()
    if touches({'F'}):
        state = 'won'"""

_CAMERA = """def update_camera():
    global camera_x
    target = player.x + player.w / 2 - WIDTH / 2
    camera_x = max(0, min(len(level[0]) * TILE - WIDTH, target))"""

_UPDATE_PASS = """def update(dt):
    pass"""

_UPDATE1 = """def update(dt):
    fall(dt)"""

_UPDATE2 = """def update(dt):
    jump()
    fall(dt)"""

_UPDATE3 = """def update(dt):
    jump()
    run(dt)
    player.x += player.vx * dt
    fall(dt)"""

_UPDATE5 = """def update(dt):
    jump()
    run(dt)
    player.x += player.vx * dt
    move_y(dt)"""

_UPDATE6 = """def update(dt):
    jump()
    run(dt)
    move_x(dt)
    move_y(dt)"""

_UPDATE9 = """def update(dt):
    jump(dt)
    run(dt)
    move_x(dt)
    move_y(dt)"""

_UPDATE10 = _UPDATE9 + "\n    collect_coins()"

_UPDATE11 = """def update(dt):
    if state != 'playing':
        return
    jump(dt)
    run(dt)
    move_x(dt)
    move_y(dt)
    collect_coins()
    check_goal()"""

_UPDATE12 = _UPDATE11 + "\n    update_camera()"

_DRAW_FLOOR = """def draw_floor():
    ctx.fill_style = '#2d3748'
    ctx.fill_rect(0, FLOOR, WIDTH, HEIGHT - FLOOR)"""

_DRAW_PLAYER = """def draw_player():
    ctx.fill_style = '#4fd1c5'
    ctx.fill_rect(player.x, player.y, player.w, player.h)"""

_DRAW_TILES4 = """def draw_tiles():
    ctx.fill_style = '#4a5568'
    for row, line in enumerate(level):
        for col, tile in enumerate(line):
            if tile == '#':
                ctx.fill_rect(col * TILE, row * TILE, TILE, TILE)"""

_DRAW_TILES8 = """def draw_tiles():
    for row, line in enumerate(level):
        for col, tile in enumerate(line):
            if tile == '#':
                ctx.fill_style = '#4a5568'
                ctx.fill_rect(col * TILE, row * TILE, TILE, TILE)
            elif tile == '=':
                ctx.fill_style = '#a0aec0'
                ctx.fill_rect(col * TILE, row * TILE, TILE, 8)"""

_DRAW_TILES11 = _DRAW_TILES8 + """
            elif tile == 'F':
                ctx.fill_style = '#fc8181'
                ctx.fill_rect(col * TILE + 14, row * TILE, 4, TILE)"""

_DRAW_COINS = """def draw_coins():
    ctx.fill_style = '#f6e05e'
    for c in coins:
        if c['taken']:
            continue
        ctx.begin_path()
        ctx.arc(c['x'], c['y'], 8, 0, math.tau)
        ctx.fill()"""

_HUD10 = """def draw_hud():
    ctx.fill_style = 'white'
    ctx.font = '16px monospace'
    ctx.fill_text(f'Coins: {score}', 10, 20)"""

_HUD11 = _HUD10 + """
    if state == 'won':
        ctx.font = '32px monospace'
        ctx.fill_text('You made it!', 140, 160)"""

_BG = "    ctx.fill_style = '#10141f'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)"


def _draw(*calls: str) -> str:
    return "def draw():\n" + "\n".join([_BG, *("    " + c for c in calls)])


_DRAW12 = (
    "def draw():\n" + _BG + "\n"
    "    ctx.save()\n    ctx.translate(-camera_x, 0)\n"
    "    draw_tiles()\n    draw_coins()\n    draw_player()\n"
    "    ctx.restore()\n    draw_hud()"
)

_LOOP = """def loop(dt):
    update(dt)
    draw()


on_frame(loop)"""

_LOOP7 = """def loop(dt):
    dt = min(dt, MAX_DT)
    update(dt)
    draw()


on_frame(loop)"""


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
    _I1, _K1, (_CLASS_PLAYER,), _N1,
    _FALL, _UPDATE1, _DRAW_FLOOR, _DRAW_PLAYER, _draw("draw_floor()", "draw_player()"), _LOOP,
)

_P2 = _program(
    _I2, _K2, (_CLASS_PLAYER,), _N1,
    _JUMP, _FALL, _UPDATE2, _DRAW_FLOOR, _DRAW_PLAYER, _draw("draw_floor()", "draw_player()"), _LOOP,
)

_P3 = _program(
    _I3, _K3, (_CLASS_PLAYER,), _N1,
    _JUMP, _RUN, _FALL, _UPDATE3, _DRAW_FLOOR, _DRAW_PLAYER, _draw("draw_floor()", "draw_player()"), _LOOP,
)

_P4 = _program(
    _I3, _K4, (_CLASS_PLAYER,), _N4,
    _JUMP, _RUN, _FALL, _UPDATE3, _DRAW_TILES4, _DRAW_PLAYER, _draw("draw_tiles()", "draw_player()"), _LOOP,
)

_P5 = _program(
    _I3, _K5, (_CLASS_PLAYER,), _N4,
    _JUMP, _RUN, _TILES5, _MOVE_Y5, _UPDATE5,
    _DRAW_TILES4, _DRAW_PLAYER, _draw("draw_tiles()", "draw_player()"), _LOOP,
)

_P6 = _program(
    _I3, _K5, (_CLASS_PLAYER,), _N4,
    _JUMP, _RUN, _TILES5, _MOVE_X, _MOVE_Y5, _UPDATE6,
    _DRAW_TILES4, _DRAW_PLAYER, _draw("draw_tiles()", "draw_player()"), _LOOP,
)

_P7 = _program(
    _I3, _K7, (_CLASS_PLAYER,), _N4,
    _JUMP, _RUN, _TILES5, _MOVE_X, _MOVE_Y7, _UPDATE6,
    _DRAW_TILES4, _DRAW_PLAYER, _draw("draw_tiles()", "draw_player()"), _LOOP7,
)

_P8 = _program(
    _I3, _K7, (_CLASS_PLAYER,), _N4,
    _JUMP, _RUN, _TILES5, _ONE_WAY, _MOVE_X, _MOVE_Y8, _UPDATE6,
    _DRAW_TILES8, _DRAW_PLAYER, _draw("draw_tiles()", "draw_player()"), _LOOP7,
)

_P9 = _program(
    _I3, _K9, (_CLASS_PLAYER9,), _N4,
    _JUMP9, _RUN, _TILES5, _ONE_WAY, _MOVE_X, _MOVE_Y8, _UPDATE9,
    _DRAW_TILES8, _DRAW_PLAYER, _draw("draw_tiles()", "draw_player()"), _LOOP7,
)

_P10 = _program(
    _I3, _K9, (_CLASS_PLAYER9,), _N10,
    _JUMP9, _RUN, _TILES5, _ONE_WAY, _MOVE_X, _MOVE_Y8, _COLLECT, _UPDATE10,
    _DRAW_TILES8, _DRAW_COINS, _DRAW_PLAYER, _HUD10,
    _draw("draw_tiles()", "draw_coins()", "draw_player()", "draw_hud()"), _LOOP7,
)

_P11 = _program(
    _I3, _K11, (_CLASS_PLAYER9,), _N11,
    _JUMP9, _RUN, _TILES5, _ONE_WAY, _MOVE_X, _MOVE_Y8, _COLLECT, _GOAL, _UPDATE11,
    _DRAW_TILES11, _DRAW_COINS, _DRAW_PLAYER, _HUD11,
    _draw("draw_tiles()", "draw_coins()", "draw_player()", "draw_hud()"), _LOOP7,
)

_P12 = _program(
    _I3, _K11, (_CLASS_PLAYER9,), _N12,
    _JUMP9, _RUN, _TILES5, _ONE_WAY, _MOVE_X, _MOVE_Y8, _COLLECT, _GOAL, _CAMERA, _UPDATE12,
    _DRAW_TILES11, _DRAW_COINS, _DRAW_PLAYER, _HUD11, _DRAW12, _LOOP7,
)

# -- The checks ---------------------------------------------------------------

_CHECK1 = _HELPERS + """
expect('player' in g, "Make the player: a Player dataclass (x, y, w, h, vx, vy, on_ground) and player = Player() - or a dict with those keys. It has to be a name in your code, outside any function.")
for k in ('x', 'y', 'w', 'h', 'vx', 'vy', 'on_ground'):
    expect(get(P(), k) is not None, f"The player needs a '{k}' - the fields are x, y, w, h, vx, vy and on_ground.")
put(P(), 'y', 0)
put(P(), 'vy', 0)
cc.frames(30)
vy = get(P(), 'vy')
expect(near(vy, 900, 25), f"After half a second of falling, vy is {vy:.0f}. Gravity is an acceleration - 1800 pixels a second, every second - so vy should be about 900. Each frame: player.vy += GRAVITY * dt.")
y = get(P(), 'y')
expect(near(y, 235, 15), f"After half a second the player is at y {y:.0f}; it should have fallen to about 235. After changing vy, move y by player.vy * dt.")
put(P(), 'y', 0)
put(P(), 'vy', 0)
cc.frames(15, 1 / 30)
vy = get(P(), 'vy')
expect(near(vy, 900, 25), f"The same half second at 30 frames a second gave vy {vy:.0f}, not 900. Gravity has to be GRAVITY * dt: a slow screen then falls at the same speed, instead of getting a fixed nudge per frame.")
y = get(P(), 'y')
expect(near(y, 235, 15), f"The same half second at 30 frames a second left the player at y {y:.0f}, but at 60 it fell to about 235. Move y by player.vy * dt, not by a fixed step each frame.")
cc.frames(120)
expect(near(feet(), 288, 0.5), f"The player's feet are at y {feet():.0f}. It should land on the floor at y 288 and stay there: if the feet reach FLOOR, put them on it.")
expect(near(get(P(), 'vy'), 0, 1) and grounded(), "Standing on the floor, vy should be 0 and on_ground true.")
put(P(), 'y', 100)
put(P(), 'vy', 0)
cc.frames(1)
expect(not grounded(), "In the air, on_ground must be False. Set it to False every frame, then True only when the floor catches the player.")
expect(any(near(r['x'], get(P(), 'x'), 0.01) and near(r['y'], get(P(), 'y'), 0.01) and r['w'] == get(P(), 'w') and r['h'] == get(P(), 'h') for r in cc.rects()), "Draw the player every frame: ctx.fill_rect(player.x, player.y, player.w, player.h).")
"""

_CHECK2 = _HELPERS + """
cc.frames(90)
y0 = get(P(), 'y')
tap('ArrowUp')
vy = get(P(), 'vy')
expect(vy < -500, f"Pressing ArrowUp on the ground should launch the player upward; vy is {vy:.0f}. y grows downward, so an upward speed is negative: player.vy = -JUMP.")
top = get(P(), 'y')
n = 0
while get(P(), 'vy') < 0 and n < 120:
    cc.frames(1)
    top = min(top, get(P(), 'y'))
    n += 1
expect(near(y0 - top, 104, 12), f"The jump rose {y0 - top:.0f} pixels; with a take-off speed of 620 and gravity 1800 it should rise about 104.")
cc.frames(120)
expect(grounded(), "After a jump the player should land and be on_ground again.")
tap(' ')
expect(get(P(), 'vy') < -500, "The space bar should jump too: keys & JUMP_KEYS is true when either ArrowUp or ' ' is held.")
cc.frames(120)
tap('ArrowUp')
cc.frames(10)
tap('ArrowUp')
vy = get(P(), 'vy')
expect(vy > -400, f"The player jumped again in mid-air (vy is {vy:.0f}). Only jump when player.on_ground is true - and set it False when you take off.")
cc.frames(120)
cc.frames(30)
expect(near(get(P(), 'vy'), 0, 1), "With no key pressed the player should stay on the floor.")
"""

_CHECK3 = _HELPERS + """
cc.frames(90)
put(P(), 'x', 100)
put(P(), 'vx', 0)
cc.press('ArrowRight')
cc.frames(6)
vx = get(P(), 'vx')
expect(near(vx, 160, 20), f"After a tenth of a second of holding ArrowRight the speed is {vx:.0f}. Running should build up (ACCEL = 1600 pixels a second per second, so about 160 here) rather than jump to top speed.")
cc.frames(60)
vx = get(P(), 'vx')
expect(near(vx, 220, 0.5), f"Held for a second, the speed is {vx:.0f}. It should stop growing at MAX_SPEED, 220: clamp vx to between -220 and 220 with max() and min().")
cc.release('ArrowRight')
cc.frames(1)
vx = get(P(), 'vx')
expect(100 < vx < 220, f"One frame after letting go the speed is {vx:.0f}. Friction should slow the player down over a moment, not stop or ignore it.")
cc.frames(60)
vx = get(P(), 'vx')
expect(near(vx, 0, 0.5), f"A second after letting go the speed is {vx}. Friction should bring it to exactly 0 and stop there, not leave it creeping or push it backwards past 0: take away min(abs(vx), FRICTION * dt), with the sign of vx.")
put(P(), 'x', 300)
cc.press('ArrowLeft')
cc.frames(60)
vx = get(P(), 'vx')
expect(near(vx, -220, 0.5), f"Held left for a second, the speed is {vx:.0f}; it should be -220.")
cc.release('ArrowLeft')
cc.frames(60)
expect(near(get(P(), 'vx'), 0, 0.5), "Friction should stop the player after running left as well.")
put(P(), 'x', 100)
put(P(), 'vx', 0)
cc.press('ArrowRight')
cc.frames(3, 1 / 30)
cc.release('ArrowRight')
vx = get(P(), 'vx')
expect(near(vx, 160, 20), f"A tenth of a second of ArrowRight at 30 frames a second gave a speed of {vx:.0f}, but at 60 it gave about 160. Acceleration is ACCEL * dt a frame, so the frame rate does not matter.")
put(P(), 'x', 100)
put(P(), 'vx', 0)
cc.press('ArrowRight')
cc.frames(30)
d60 = get(P(), 'x') - 100
put(P(), 'x', 100)
put(P(), 'vx', 0)
cc.frames(15, 1 / 30)
d30 = get(P(), 'x') - 100
cc.release('ArrowRight')
expect(70 < d60 < 125, f"Running right for half a second moved the player {d60:.0f} pixels; about 97 is right. Every frame x changes by vx * dt: update must add the speed to x.")
expect(near(d30, d60, 10), f"Half a second of running moved the player {d30:.0f} pixels at 30 frames a second but {d60:.0f} at 60. Move by vx * dt, not a fixed step per frame.")
put(P(), 'vx', 200)
cc.frames(6)
sixty = get(P(), 'vx')
put(P(), 'vx', 200)
cc.frames(3, 1 / 30)
slow = get(P(), 'vx')
expect(near(sixty, slow, 4), f"A tenth of a second of friction left {sixty:.0f} at 60 frames a second but {slow:.0f} at 30. Take away FRICTION * dt each frame - not a fixed fraction of the speed per frame, which depends on the frame rate.")
"""

_CHECK4 = _HELPERS + """
expect('TILE' in g and g.TILE == 32, "Make TILE = 32 - one tile is 32 by 32 pixels.")
TILE = g.TILE
expect('level' in g and isinstance(g.level, list) and len(g.level) == 10 and all(isinstance(r, str) for r in g.level), "Make level: a list of 10 strings, one for each row of tiles.")
lv = g.level
expect(all(len(r) == len(lv[0]) for r in lv) and len(lv[0]) >= 30, "Every row must be the same length, and at least 30 tiles wide (the canvas is only 15 tiles across).")
cc.frames(1)
squares = [r for r in cc.rects() if r['w'] == TILE and r['h'] == TILE]
drawn = {(r['x'], r['y']) for r in squares}
solids = 0
for row, line in enumerate(lv):
    for col, ch in enumerate(line):
        if ch != '#':
            continue
        solids += 1
        expect((col * TILE, row * TILE) in drawn, f"The '#' at column {col}, row {row} is not drawn at x {col * TILE}, y {row * TILE}. A tile's corner is col * TILE across and row * TILE down - level[row][col], rows first.")
expect(solids >= 20, "Put some solid tiles in the map: a floor of '#' along the bottom row, and a few more.")
expect(len(squares) == solids, f"The map has {solids} '#' tiles but {len(squares)} tile-sized squares were drawn. Draw a square only where the map says '#'.")
was = lv[2]
lv[2] = was[:5] + '#' + was[6:]
cc.frames(1)
expect(any(r['x'] == 160 and r['y'] == 64 and r['w'] == TILE and r['h'] == TILE for r in cc.rects()), "Draw from level every frame, so that changing the map changes the picture.")
lv[2] = was
"""

_CHECK5 = _HELPERS + _WORLD + """
clear()
place(100, 0)
cc.frames(90)
expect(near(feet(), 288, 0.5) and grounded(), f"Dropped onto the floor row, the player's feet are at y {feet():.0f} (on_ground {grounded()}). It should stand on the top of the floor tiles, y 288.")
lay(6, 2, 6, '#')
lay(6, 8, 12, '#')
place(100, 0)
cc.frames(60)
expect(near(feet(), 192, 0.5) and grounded(), f"Over a platform of tiles the player's feet ended at y {feet():.0f}; it should land on top of it, at y 192 (row 6). The tile under the feet is level[row][col] - row first.")
place(8 * 32 - 24, 0)
cc.frames(90)
expect(near(feet(), 288, 0.5), f"The player fell right beside the platform, touching its edge but not over it, and stopped at y {feet():.0f}. A box that only touches a tile does not overlap it: the last column is ceil((x + w) / TILE) - 1, so range(floor(x / TILE), ceil((x + w) / TILE)).")
clear()
lay(5, 3, 4, '#')
place(100, 258)
cc.frames(10)
tap('ArrowUp')
top = get(P(), 'y')
for _ in range(60):
    cc.frames(1)
    top = min(top, get(P(), 'y'))
expect(top >= 192 - 0.01, f"Jumping up into a tile overhead, the player's top reached y {top:.0f}, inside the tile (its underside is at y 192). Moving up into a tile should stop the head against it and set vy to 0.")
expect(near(feet(), 288, 0.5), "After bumping its head the player should drop back to the floor.")
no_floor()
place(100, 250)
cc.frames(30)
expect(get(P(), 'y') > 300, "The player is standing on thin air over a gap in the floor. The tiles are the floor now: take out the flat FLOOR line and let the map hold the player up.")
clear()
place(100, -60)
cc.frames(120)
expect(near(feet(), 288, 0.5) and grounded(), f"A player above the top of the map (y -60) did not fall back to the floor; its feet are at y {feet():.0f}. A row number below 0 is not a row of the map - but level[-1] is, in Python, the LAST row. Return '.' from tile_at for row < 0 before you index.")
"""

_CHECK6 = _HELPERS + _WORLD + """
clear()
lay(6, 10, 10, '#')
lay(7, 10, 10, '#')
lay(8, 10, 10, '#')
place(200, 258)
cc.frames(20)
cc.press('ArrowRight')
cc.frames(90)
cc.release('ArrowRight')
right = get(P(), 'x') + get(P(), 'w')
expect(near(right, 320, 0.5), f"Running right into a wall, the player's right edge ended at x {right:.0f}. It should stop flush against the wall, at 320: move along x, and if that overlaps a tile put the edge on the tile's edge and zero vx.")
expect(grounded() and near(feet(), 288, 0.5), "Pressed against the wall, the player should still be standing on the floor. Standing on a tile is not touching it from the side.")
cc.press('ArrowLeft')
cc.frames(30)
cc.release('ArrowLeft')
expect(get(P(), 'x') < 250, "After touching the wall the player should be able to walk away from it again.")
place(296, 175)
cc.press('ArrowRight')
cc.frames(90)
cc.release('ArrowRight')
expect(get(P(), 'x') + get(P(), 'w') <= 320.01, "The player went into the wall.")
expect(near(feet(), 288, 0.5) and grounded(), f"Falling while pushing against the wall, the player ended at y {feet():.0f} instead of reaching the floor: it is stuck to the wall. Move and fix x on its own first, then move and fix y.")
clear()
place(60, 258)
cc.frames(10)
lowest = get(P(), 'x')
cc.press('ArrowLeft')
for _ in range(60):
    cc.frames(1)
    lowest = min(lowest, get(P(), 'x'))
cc.release('ArrowLeft')
expect(lowest >= -0.01 and near(get(P(), 'x'), 0, 0.5), f"Running left, the player got as far as x {lowest:.0f} - out past the left edge of the map. Beyond the edge is a wall: tile_at returns '#' for a column below 0 (in Python level[row][-1] is the last column, so test col < 0 yourself). And a tile number from x is x // TILE or math.floor(x / TILE) - int() rounds -0.5 to 0, not -1.")
place(900, 258)
cc.frames(10)
farthest = get(P(), 'x') + get(P(), 'w')
cc.press('ArrowRight')
for _ in range(60):
    cc.frames(1)
    farthest = max(farthest, get(P(), 'x') + get(P(), 'w'))
cc.release('ArrowRight')
expect(farthest <= W * 32 + 0.01 and near(get(P(), 'x') + get(P(), 'w'), W * 32, 0.5), f"Running right, the player's edge got to x {farthest:.0f} and stopped at {get(P(), 'x') + get(P(), 'w'):.0f}; it should stop flush against the right end of the map ({W * 32}). A column past the last one is a wall: tile_at returns '#' for col >= len(level[0]).")
"""

_CHECK7 = _HELPERS + _WORLD + """
clear()
lay(6, 2, 8, '#')
place(100, 40)
cc.frames(3, 0.4)
cc.frames(120)
expect(grounded() and near(feet(), 192, 0.5), f"After three very long frames (a tab left in the background) the player's feet are at y {feet():.0f} - it fell straight through a one-tile platform. Cap dt at 1 / 30 so a long frame is still a short step: dt = min(dt, MAX_DT).")
no_floor()
place(100, 0)
cc.frames(180)
vy = get(P(), 'vy')
expect(850 < vy <= 901, f"After a long fall the speed is {vy:.0f}. A fall should top out at MAX_FALL, 900 pixels a second: after gravity, vy = min(vy, MAX_FALL).")
clear()
place(100, 0)
cc.frames(120)
expect(grounded() and near(feet(), 288, 0.5), "Normal play should work as before: the player should land on the floor.")
"""

_CHECK8 = _HELPERS + _WORLD + """
clear()
lay(7, 2, 8, '=')
place(100, 100)
cc.frames(60)
expect(grounded() and near(feet(), 224, 0.5), f"Dropped onto a '=' ledge from above, the player's feet are at y {feet():.0f}. It should land on top, at y 224 (row 7).")
cc.frames(30)
expect(grounded() and near(feet(), 224, 0.5), f"Standing on the ledge for half a second, the player's feet are at y {feet():.0f}. The ledge should hold the player up: if the feet were at or above the top last frame and are past it now, land. Use prev_bottom <= top (not <) - a standing player's feet are exactly at the top.")
place(100, 258)
cc.frames(10)
tap('ArrowUp')
lowest = 999
for _ in range(120):
    cc.frames(1)
    lowest = min(lowest, feet())
expect(lowest < 224 - 10, "Jumping from underneath the ledge, the player did not get above it: a '=' tile must let the player pass up through it - it is not in SOLID.")
expect(grounded() and near(feet(), 224, 0.5), f"After jumping up through the ledge the player should land on top of it (feet at y 224); they are at y {feet():.0f}.")
clear()
lay(5, 2, 8, '=')
place(100, 258)
cc.frames(10)
tap('ArrowUp')
cc.frames(120)
expect(near(feet(), 288, 0.5), f"A jump that peaks inside a ledge should not grab the player and lift them onto it: the feet were below its top last frame, so it must let them fall back to the floor (they are at y {feet():.0f}).")
clear()
lay(8, 9, 10, '=')
place(200, 258)
cc.frames(20)
cc.press('ArrowRight')
cc.frames(60)
cc.release('ArrowRight')
expect(get(P(), 'x') > 360, f"A '=' tile at the player's own height must not block: only the walls ('#') do. The player stopped at x {get(P(), 'x'):.0f}.")
clear()
lay(7, 2, 8, '=')
place(2 * 32 - 12, 100)
cc.frames(60)
expect(grounded() and near(feet(), 224, 0.5), f"A player with only the right half of its box over the end of a ledge fell past it (feet at y {feet():.0f}). Look at every column the box covers - tiles_covered - not just the first.")
clear()
lay(0, 2, 8, '=')
place(100, -90)
cc.frames(60)
expect(grounded() and near(feet(), 0, 0.5), f"A ledge in the top row of the map (row 0) did not hold the player: its feet are at y {feet():.0f}, not 0. Row 0 is a real row, but `if row:` is false for 0 - say `if row is not None:`.")
"""

_CHECK9 = _HELPERS + _WORLD + """
expect(isinstance(get(P(), 'coyote'), (int, float)), "Keep a timer on the player: coyote, in seconds (a field of Player, or a key in the dict).")
clear()
place(100, 258)
cc.frames(30)
y1 = get(P(), 'y')
tap('ArrowUp')
top = get(P(), 'y')
n = 0
while get(P(), 'vy') < 0 and n < 90:
    cc.frames(1)
    top = min(top, get(P(), 'y'))
    n += 1
expect(y1 - top < 60, f"A quick tap of the jump key rose {y1 - top:.0f} pixels. Letting go while still rising should cut the jump short: if the key is up and vy is faster than -JUMP_CUT, set vy to -JUMP_CUT.")
cc.frames(120)
y2 = get(P(), 'y')
cc.press('ArrowUp')
top = get(P(), 'y')
for _ in range(40):
    cc.frames(1)
    top = min(top, get(P(), 'y'))
cc.release('ArrowUp')
expect(y2 - top > 90, f"Holding the jump key rose only {y2 - top:.0f} pixels. A held key should still give the full jump, about 104.")


def off_ledge(dt):
    clear()
    g.level = g.level[:-1] + ['#' * 6 + '.' * (W - 6)]
    place(140, 258)
    cc.frames(10, dt)
    cc.press('ArrowRight')
    n = 0
    while grounded() and n < 120:
        cc.frames(1, dt)
        n += 1
    cc.release('ArrowRight')


off_ledge(1 / 60)
expect(not grounded(), "The player should walk off the end of the floor and start to fall.")
cc.frames(3)
tap('ArrowUp')
expect(get(P(), 'vy') < -400, f"The jump key was pressed 0.05 seconds after running off the ledge and nothing happened (vy {get(P(), 'vy'):.0f}). Coyote time: keep a short timer, set to COYOTE (0.1) on the ground and counted down in the air, and allow the jump while it is above 0.")
off_ledge(1 / 60)
cc.frames(18)
tap('ArrowUp')
expect(get(P(), 'vy') > 0, f"A jump 0.3 seconds after leaving the ledge should not work, but vy is {get(P(), 'vy'):.0f}. The window is only a tenth of a second.")
off_ledge(1 / 30)
cc.frames(1, 1 / 30)
tap('ArrowUp', 1 / 30)
expect(get(P(), 'vy') < -400, "At 30 frames a second, a jump 0.07 seconds after leaving the ledge should still work.")
off_ledge(1 / 30)
cc.frames(4, 1 / 30)
tap('ArrowUp', 1 / 30)
expect(get(P(), 'vy') > 0, "At 30 frames a second, a jump 0.17 seconds after leaving the ledge worked, but at 60 the window is a tenth of a second. Count the coyote time down in seconds - subtract dt - not in frames.")
clear()
place(100, 258)
cc.frames(10)
tap('ArrowUp')
cc.frames(4)
tap('ArrowUp')
expect(get(P(), 'vy') > -540, f"A second press in mid-air jumped again (vy {get(P(), 'vy'):.0f}). Using up the coyote time - set it to 0 when you jump - stops a double jump.")
"""

_CHECK10 = _HELPERS + _WORLD + """
expect('coins' in g and isinstance(g.coins, list) and len(g.coins) >= 3, "Make coins - a list with a coin for each 'o' in the map (put at least three 'o' in your level): {'x': ..., 'y': ..., 'taken': False}, at the middle of the tile.")
expect('score' in g and isinstance(g.score, (int, float)) and g.score == 0, "Start with score = 0 - a name in your code, outside any function.")
spots = [(get(c, 'x'), get(c, 'y')) for c in g.coins]
expect(all(isinstance(x, (int, float)) and isinstance(y, (int, float)) for x, y in spots), "Every coin needs a number x and a number y - its middle, in pixels.")
total = len(spots)
cc.frames(1)
expect(len(cc.arcs()) == total, f"There are {total} coins in the list but {len(cc.arcs())} circles drawn. Draw every coin that has not been collected, as a filled circle: ctx.arc(x, y, 8, 0, math.tau) then ctx.fill().")
cc.frames(30)
expect(g.score == 0, f"The score is {g.score} without the player having touched a coin: collect only the ones the player overlaps.")


def at(spot, dx=0, dy=0):
    put(P(), 'x', spot[0] - get(P(), 'w') / 2 + dx)
    put(P(), 'y', spot[1] - get(P(), 'h') / 2 + dy)
    put(P(), 'vx', 0)
    put(P(), 'vy', 0)


at(spots[0], 0, -100)
cc.frames(1)
expect(g.score == 0, f"The player is 100 pixels above a coin and the score is {g.score}. A coin is collected only when the player is level with it as well as beside it: test the vertical distance too.")
at(spots[0], 100, 0)
cc.frames(1)
expect(g.score == 0, f"The player is 100 pixels to the side of a coin and the score is {g.score}. Test the horizontal distance too.")
at(spots[0])
cc.frames(1)
expect(g.score == 1, f"The player is on top of a coin but the score is {g.score}. Add 1 when the player overlaps a coin.")
expect(len(cc.arcs()) == total - 1, "A collected coin should disappear: stop drawing it.")
cc.frames(10)
expect(g.score == 1, f"The score is {g.score}: a coin counts once. Mark it taken (or remove it) the moment it is collected.")
at(spots[1])
cc.frames(1)
expect(g.score == 2, f"After a second coin the score is {g.score}; it should be 2.")
expect(any('2' in t for t in cc.texts()), "Show the score on the screen - it should say 2 now: ctx.fill_text(f'Coins: {score}', 10, 20).")
"""

_CHECK11 = _HELPERS + _WORLD + """
expect('state' in g and g.state == 'playing', "Keep what the game is doing in state = 'playing' - a name in your code, outside any function.")
expect('START' in g, "Make START - where the player begins and comes back to: START = (64, 258) (a tuple of x and y; a dict with x and y works too).")
s = g.START
if isinstance(s, dict):
    sx, sy = s.get('x'), s.get('y')
elif isinstance(s, (tuple, list)) and len(s) == 2:
    sx, sy = s
else:
    sx, sy = getattr(s, 'x', None), getattr(s, 'y', None)
expect(isinstance(sx, (int, float)) and isinstance(sy, (int, float)), "START should hold an x and a y: START = (64, 258).")
clear()
place(300, 258)
cc.frames(60)
expect(g.state == 'playing' and near(get(P(), 'x'), 300, 1), "A player standing on the floor should not be sent back to the start.")
no_floor()
place(300, 250)
came = False
for _ in range(300):
    before = get(P(), 'y')
    cc.frames(1)
    if get(P(), 'y') < before - 30:
        came = True
        break
expect(came, "The player fell out of the bottom of the world and never came back. When it is well below the canvas (y over HEIGHT + 100), respawn it.")
expect(near(get(P(), 'x'), sx, 1) and near(get(P(), 'y'), sy, 1), f"The respawn put the player at {get(P(), 'x'):.0f}, {get(P(), 'y'):.0f}; it should be at START ({sx}, {sy}).")
expect(near(get(P(), 'vy'), 0, 100), f"The respawned player is still falling at {get(P(), 'vy'):.0f}. Reset vx and vy to 0 as well as the position.")
clear()
lay(8, 10, 10, 'F')
place(100, 258)
cc.frames(5)
expect(g.state == 'playing', "The game is won only when the player touches the flag ('F').")
place(10 * 32 + 4, 258)
cc.frames(3)
expect(g.state == 'won', f"The player is standing in the flag's tile but state is {g.state!r}. When the player overlaps an 'F' tile, set state to 'won' - and since that re-binds a top-level name, the function needs `global state`: without it the assignment makes a quiet local variable and the real state never changes.")
expect(any(re.search('made it|win|goal', t, re.I) for t in cc.texts()), "When the game is won, say so on the screen.")
x0 = get(P(), 'x')
cc.press('ArrowRight')
cc.frames(15)
cc.release('ArrowRight')
expect(near(get(P(), 'x'), x0, 0.01), "Once the game is won the player should stop moving: return from update when state is not 'playing'.")
"""

_CHECK12 = _HELPERS + _WORLD + """
expect('camera_x' in g or 'camera' in g, "Make camera_x = 0 - how far along the level the left edge of the screen is - a name in your code, outside any function.")


def cam():
    if 'camera_x' in g:
        return g.camera_x
    return get(g.camera, 'x')


def placed():
    dx = 0
    stack = []
    out = []
    for c in cc.drawn():
        name, a = c['name'], c['args']
        if name == 'save':
            stack.append(dx)
        elif name == 'restore':
            dx = stack.pop() if stack else 0
        elif name == 'translate':
            dx += a[0]
        elif name == 'fill_rect':
            out.append(('rect', a[0] + dx, a[1], a[2], a[3]))
        elif name == 'fill_text':
            out.append(('text', a[1] + dx, a[2], a[0]))
    return out


TILE = g.TILE
clear()
place(64, 258)
cc.frames(2)
expect(near(cam(), 0, 0.5), f"At the left end of the level the camera is at {cam():.0f}. It should stop at 0 rather than scroll into empty space: max(0, ...).")
place(468, 258)
cc.frames(2)
expect(near(cam(), 240, 3), f"With the player in the middle of the level the camera is at {cam():.0f}. Put the player's centre in the middle of the screen: player.x + player.w / 2 - WIDTH / 2.")
me = next((r for r in placed() if r[0] == 'rect' and r[3] == get(P(), 'w') and r[4] == get(P(), 'h')), None)
expect(me and near(me[1], get(P(), 'x') - cam(), 1), f"The player is drawn at screen x {round(me[1]) if me else 'nowhere'}; it should be at player.x - camera_x, {get(P(), 'x') - cam():.0f}. Shift everything you draw left by the camera: ctx.translate(-camera_x, 0).")
expect(any(r[0] == 'rect' and r[3] == TILE and r[4] == TILE and near(r[2], 288, 0.01) and near(r[1], 640 - cam(), 0.5) for r in placed()), "The tiles should scroll with the camera too: a floor tile in column 20 should be drawn at 640 - camera_x.")
place(900, 258)
cc.frames(2)
want = len(g.level[0]) * TILE - WIDTH
expect(near(cam(), want, 0.5), f"At the right end of the level the camera is at {cam():.0f}; it should stop at the level's width minus the screen's, {want}: min(len(level[0]) * TILE - WIDTH, ...).")
off = [t for t in placed() if t[0] == 'text' and (t[1] < -1 or t[1] > WIDTH)]
expect(not off, "The score is drawn off the screen when the camera has scrolled. Text for the player to read goes after ctx.restore(), so it stays put.")
"""


def _step(**fields: object) -> Step:
    """A step on this track: Python, in the Python Platformer track."""
    fields["track"] = TRACK
    fields["language"] = "python"
    return Step(**fields)  # type: ignore[arg-type]


PYPLATFORMER_STEPS: tuple[Step, ...] = (
    _step(
        id="pyplat-01-gravity",
        title="Gravity pulls",
        teaches=(
            "Gravity is not a speed, it is an acceleration: it changes the "
            "speed, every second, by the same amount. So each frame does two "
            "things in this order: vy += GRAVITY * dt, then y += vy * dt. "
            "Multiply by dt both times and the fall takes the same real time "
            "on any screen; leave dt off the first and a 30 frames a second "
            "screen falls at half the pull of a 60 one. The player is a "
            "@dataclass: the fields with a = after them have defaults, so "
            "Player() is a whole player (a dict with the same keys works "
            "just as well - player['y'] for player.y). A floor is a line "
            "the feet may not cross: when they do, put them on it, zero vy, "
            "and note that the player is standing - on_ground is a bool, "
            "set to False at the start of every frame and True only when "
            "the floor catches the player."
        ),
        goal="Add GRAVITY = 1800, FLOOR = 288 and a Player dataclass (x = 64, y = 0, w = 24, h = 30, vx = 0, vy = 0, on_ground = False) with player = Player() - a dict with those keys works too. Write fall(dt), called from update(dt): pull the player down with gravity, stop its feet on the floor, set on_ground, and draw the floor and the player. The check reads player.",
        starter=_P0,
        solution=_P1,
        check=_CHECK1,
        hint="player.vy += GRAVITY * dt; player.y += player.vy * dt; player.on_ground = False; then if player.y + player.h >= FLOOR: player.y = FLOOR - player.h; player.vy = 0; player.on_ground = True",
    ),
    _step(
        id="pyplat-02-jump",
        title="Jump from the ground only",
        teaches=(
            "A jump is a single instant: set vy to a big upward number "
            "(negative, because y grows downwards) and let gravity do the "
            "rest. It rises while vy is negative, slows, turns, and comes "
            "down on its own; the height is JUMP squared over twice "
            "gravity, so 620 gives about 100 pixels. The rule that makes it "
            "a platformer: only jump while on_ground, or holding the key "
            "flies. And when you take off, say you are no longer on the "
            "ground. `keys` is a real set of the keys held, so two keys "
            "at once is set arithmetic: JUMP_KEYS = {'ArrowUp', ' '}, and "
            "keys & JUMP_KEYS is the keys in BOTH - an empty set (false) "
            "or not (true). & binds tighter than and, so player.on_ground "
            "and keys & JUMP_KEYS reads the way it sounds."
        ),
        goal="Add JUMP = 620 and JUMP_KEYS = {'ArrowUp', ' '}. Write jump(), called from update(dt) before fall: when a jump key is held (keys & JUMP_KEYS) and the player is on_ground, set vy to -JUMP and on_ground to False. The check reads player.",
        starter=_P1,
        solution=_P2,
        check=_CHECK2,
        hint="if player.on_ground and keys & JUMP_KEYS: player.vy = -JUMP; player.on_ground = False",
    ),
    _step(
        id="pyplat-03-run",
        title="Running with momentum",
        teaches=(
            "Setting vx straight to a speed feels like a cursor. Real "
            "running has weight: holding a direction ACCELERATES vx "
            "(vx += direction * ACCEL * dt), letting go lets friction take "
            "speed away (also times dt), and a clamp stops it at "
            "MAX_SPEED. direction is -1, 0 or 1: a bool is a number in "
            "Python, so ('ArrowRight' in keys) - ('ArrowLeft' in keys) is "
            "the whole sum. Friction must stop at zero. Take away "
            "min(abs(vx), FRICTION * dt) - never more than there is - and "
            "give it vx's own sign with math.copysign(amount, vx): "
            "friction pulls toward 0 from either side, and never pushes "
            "past it, or the player shuffles backwards for ever. The clamp "
            "is max(-MAX_SPEED, min(MAX_SPEED, vx)). Do not multiply vx "
            "by 0.9 each frame: that is a different friction at every "
            "frame rate."
        ),
        goal="Add ACCEL = 1600, FRICTION = 1400, MAX_SPEED = 220 and run(dt), called from update(dt): the arrow keys accelerate vx, no key slows it to exactly 0, vx stays within the maximum. Then update moves x by vx * dt. The check reads player.",
        starter=_P2,
        solution=_P3,
        check=_CHECK3,
        hint="direction = ('ArrowRight' in keys) - ('ArrowLeft' in keys); if direction: player.vx += direction * ACCEL * dt  else: slow = min(abs(player.vx), FRICTION * dt); player.vx -= math.copysign(slow, player.vx)   then the max/min clamp",
    ),
    _step(
        id="pyplat-04-tilemap",
        title="A level made of strings",
        teaches=(
            "A level is not a list of rectangles you type out; it is a "
            "grid you can SEE in the code: a list of strings, one per row, "
            "one character per tile - '#' solid, '.' air. level[row][col] "
            "reads a tile, row FIRST (level[col][row] is the classic "
            "mix-up), and a tile's pixel position is col * TILE across and "
            "row * TILE down. enumerate gives each row its number and each "
            "character its number, so drawing is a pair of nested loops "
            "with no range(len(...)) in sight. A map is easier to draw "
            "as one triple-quoted string; textwrap.dedent(...).strip()."
            "splitlines() turns it into this same list. Strings cannot be "
            "changed in place - to change a tile you build the row again: "
            "row[:c] + '#' + row[c + 1:]. Read the map live every frame, so "
            "editing the map edits the game. Add symbols as you need them: "
            "'=' for ledges, 'o' for coins, 'F' for the flag."
        ),
        goal="Add TILE = 32 and level: a list of 10 strings of at least 30 characters each, '#' for solid and '.' for air, with a floor along the bottom row. Draw a square for every '#' (draw_tiles), instead of the old flat floor. The check reads TILE and level, and replaces rows of level to build its own worlds - keep it a plain list of strings that you read every frame.",
        starter=_P3,
        solution=_P4,
        check=_CHECK4,
        hint="for row, line in enumerate(level): for col, tile in enumerate(line): if tile == '#': ctx.fill_rect(col * TILE, row * TILE, TILE, TILE)",
    ),
    _step(
        id="pyplat-05-floor",
        title="Land on tiles",
        teaches=(
            "To collide with a grid you do not test the player against "
            "every tile: you work out which tiles the box covers. A pixel "
            "is in tile x // TILE - floor division, which rounds DOWN, so "
            "-5 // 32 is -1 (int(-5 / 32) is 0: int() cuts toward zero, "
            "which puts a player standing half off the edge in the wrong "
            "tile; divmod(x, TILE) gives the tile and the offset inside it "
            "together). A box covers range(math.floor(x / TILE), math.ceil((x "
            "+ w) / TILE)) - ceil, and range stops BEFORE its end, because a box "
            "ending exactly on a tile boundary does not touch the next "
            "tile. Then any() over a generator asks whether any of those "
            "tiles is solid - and `in SOLID`, a set, says which characters "
            "are (all() would ask whether every one is). tile_of returns a "
            "tuple, (col, row), and `_, row = tile_of(...)` unpacks the part "
            "you want. In tile_at, guard the edges: Python does not "
            "complain about level[-1], it quietly gives you the LAST row. "
            "Moving down into a solid tile puts the feet on its top "
            "(on_ground); moving up puts the head under it. Zero vy either "
            "way. The tiles are the floor now, so FLOOR goes."
        ),
        goal="Replace FLOOR with tiles: add SOLID = {'#'} and write tile_of(x, y) (returns (col, row)), tile_at(col, row) ('#' beyond the left and right, '.' above and below the map), tiles_covered(start, size) (a range), touches(kinds) (is the player's box on any tile whose character is in kinds) and move_y(dt): gravity, move y, and if the box touches SOLID put the feet on top (on_ground) or the head underneath, and zero vy. The check reads player and level.",
        starter=_P4,
        solution=_P5,
        check=_CHECK5,
        hint="after player.y += ...: if touches(SOLID): if player.vy > 0: _, row = tile_of(player.x, player.y + player.h); player.y = row * TILE - player.h; player.on_ground = True  else: _, row = tile_of(player.x, player.y); player.y = (row + 1) * TILE   then player.vy = 0",
    ),
    _step(
        id="pyplat-06-walls",
        title="Walls: one axis at a time",
        teaches=(
            "Moving sideways collides with tiles too, but do not move x "
            "and y together and then try to untangle the overlap: you "
            "cannot tell which way you hit the tile, and the player "
            "snags on corners or sticks to a wall it is only brushing. "
            "Move on ONE axis, fix that axis, then do the other. x first: "
            "move, and if the box now touches a solid tile put the edge "
            "back flush - the right edge on the tile's left side, or the "
            "left edge on its right - and zero vx. The tile number comes "
            "from a tuple again: col, _ = tile_of(player.x + player.w, "
            "player.y). Then y as before. Each test then has only one "
            "thing it could mean. And the map has ends: a tile_at that "
            "answers '#' for a column below 0 is what keeps the player "
            "inside (without the guard level[row][-1] is the far end of "
            "the map), and floor division is what keeps a negative x in "
            "the tile to its left."
        ),
        goal="Add move_x(dt): move x by vx * dt and if that touches a solid tile put the player flush against it and zero vx. update calls move_x then move_y each frame, in place of the free x move. The check reads player and level.",
        starter=_P5,
        solution=_P6,
        check=_CHECK6,
        hint="same shape as move_y: player.x += player.vx * dt; if touches(SOLID): if player.vx > 0: col, _ = tile_of(player.x + player.w, player.y); player.x = col * TILE - player.w  else: col, _ = tile_of(player.x, player.y); player.x = (col + 1) * TILE   then player.vx = 0",
    ),
    _step(
        id="pyplat-07-fast",
        title="Nothing tunnels",
        teaches=(
            "Collision only looks at where the player ends up each frame. "
            "If a frame moves it further than a tile is thick, it lands "
            "past the tile and never notices: tunnelling. It happens when "
            "the browser stalls (a hidden tab can deliver a 400 ms frame) "
            "or when something is simply fast. Two cheap fixes, both "
            "min(): cap dt so no frame is ever long - dt = min(dt, "
            "MAX_DT), the argument you were handed is just a name, so you "
            "can re-bind it - and cap the fall speed (terminal velocity, "
            "900 here) with vy = min(vy + GRAVITY * dt, MAX_FALL), so one "
            "frame is at most a few tiles. Real games also split a frame "
            "into smaller steps; for tiles this big, the caps are enough."
        ),
        goal="Add MAX_DT = 1 / 30 and MAX_FALL = 900. In the loop, cap dt at MAX_DT before update runs; in move_y, after gravity vy is never more than MAX_FALL. The check reads player and level.",
        starter=_P6,
        solution=_P7,
        check=_CHECK7,
        hint="in loop: dt = min(dt, MAX_DT)   and in move_y: player.vy = min(player.vy + GRAVITY * dt, MAX_FALL)",
    ),
    _step(
        id="pyplat-08-oneway",
        title="One-way ledges",
        teaches=(
            "A '=' ledge is solid from above only: jump up through it, "
            "land on it. So it is not in SOLID, and it is not a wall. It "
            "catches the player on the way DOWN, and only if the feet "
            "were at or above its top on the previous frame: prev_bottom "
            "<= top. Without that, a jump that peaks inside the ledge "
            "would snap the player up onto it. Use <=, not <: a player "
            "already standing has its feet exactly at the top, and with < "
            "the ledge lets go of them next frame and they fall through. "
            "one_way_row answers 'which row?' or 'none' - and in Python "
            "'none' is None, not -1 and not 0. Test it with `is not None`: "
            "`if row:` is false for row 0, so a ledge in the top row would "
            "never catch anyone."
        ),
        goal="Make '=' tiles one-way: no blocking from the side or below, but landing on one when moving down with the feet at or above its top last frame. Write one_way_row(prev_bottom), which returns the ledge's row or None, and use it in move_y; keep '=' out of SOLID. Draw the ledges as a thin bar. The check reads player and level.",
        starter=_P7,
        solution=_P8,
        check=_CHECK8,
        hint="prev_bottom = player.y + player.h before moving. After the SOLID test: elif player.vy > 0: row = one_way_row(prev_bottom); if row is not None: stand on it. In one_way_row: if prev_bottom > row * TILE: return None; and any(tile_at(col, row) == '=' for col in tiles_covered(player.x, player.w))",
    ),
    _step(
        id="pyplat-09-feel",
        title="A jump that forgives",
        teaches=(
            "Two small things separate a platformer that feels fair from "
            "one that feels cheap. Coyote time: for a tenth of a second "
            "after running off a ledge you can still jump, because people "
            "press a hair late. Keep a timer in SECONDS (a field on the "
            "player, coyote), refill it to COYOTE while on_ground, count "
            "it down by dt in the air, and jump while it is above 0 - and "
            "set it to 0 on the jump, or you get a double jump. Count it "
            "in frames instead (COYOTE = 6; coyote -= 1) and a 30 frames "
            "a second screen gives twice the time. Variable height: let go "
            "of the key while rising and the jump is cut short - vy limited "
            "to -JUMP_CUT. Tap for a hop, hold for the full height. "
            "jump_held = bool(keys & JUMP_KEYS) works out the key once."
        ),
        goal="Add COYOTE = 0.1, JUMP_CUT = 200 and a coyote field on the player (0). Change jump to jump(dt): allow a jump while coyote is above 0 (and use it up), and when the jump key is up and vy is faster than -JUMP_CUT, set vy to -JUMP_CUT. The check reads player and level.",
        starter=_P8,
        solution=_P9,
        check=_CHECK9,
        hint="on the ground player.coyote = COYOTE, else player.coyote -= dt. Jump if jump_held and player.coyote > 0, then player.coyote = 0. If not jump_held and player.vy < -JUMP_CUT: player.vy = -JUMP_CUT",
    ),
    _step(
        id="pyplat-10-coins",
        title="Coins",
        teaches=(
            "The map already says where things are, so build the coins "
            "from it: loop over the level once at the start, and for every "
            "'o' make a coin at the middle of that tile (col * TILE + TILE "
            "/ 2). One list comprehension does it - two for clauses "
            "(for row, line in enumerate(level) / for col, tile in "
            "enumerate(line)) and an if - and the map stays the level's "
            "whole description. Each coin is a small dict, {'x': ..., 'y': "
            "..., 'taken': False}. Each frame, for every coin not yet "
            "taken, test it against the player's box with abs(); on a hit "
            "mark it taken and add to the score. The taken flag is what "
            "makes a coin count once: without it you would collect it again "
            "on every frame you stand in it. score += 1 in a function "
            "re-binds the top-level score, so it needs `global score` - "
            "leave it off and Python raises UnboundLocalError, because "
            "the assignment made score a local. f'Coins: {score}' writes "
            "the HUD."
        ),
        goal="Put at least three 'o' in your map. Build coins from them ({'x': ..., 'y': ..., 'taken': False} at each tile's middle) and set score = 0. Write collect_coins(), called from update: a coin the player overlaps is collected once (taken, score + 1; score is re-bound, so global). Draw the other coins as circles and write the score on the screen, as Coins: 0. The check reads player, level, coins and score.",
        starter=_P9,
        solution=_P10,
        check=_CHECK10,
        hint="abs(c['x'] - cx) < 8 + player.w / 2 and the same for y; then c['taken'] = True; score += 1 (global score). Draw only if not c['taken'].",
    ),
    _step(
        id="pyplat-11-goal",
        title="A flag, and starting over",
        teaches=(
            "A game needs an end and a way back. The flag is one more "
            "map symbol, 'F': ask whether the player's box covers a tile "
            "with that character - touches({'F'}), the same function as "
            "the walls, with a different set - and set state to 'won'. "
            "Falling out of the world is the other: the map has a pit, "
            "and below the bottom there is nothing to land on, so when the "
            "player is far below the canvas (HEIGHT + 100) put it back at "
            "START. START = (64, 258) is a tuple, so player.x, player.y = "
            "START unpacks it, and player.vx = player.vy = 0 zeroes the "
            "speed as well, or it arrives still falling at full speed. "
            "state is another name a function re-binds, so check_goal "
            "needs `global state` - and this time leaving it off raises "
            "no error: state = 'won' quietly makes a local variable, and "
            "the game is never won. Once it is won, update does nothing."
        ),
        goal="Add START = (64, 258) (a tuple; a dict with x and y works too) and state = 'playing'. Below HEIGHT + 100, respawn at START with no speed. Touching an 'F' tile sets state to 'won' (global), stops the game, and says You made it! on the screen. Draw the flag. The check reads player, level, START and state.",
        starter=_P10,
        solution=_P11,
        check=_CHECK11,
        hint="def respawn(): player.x, player.y = START; player.vx = player.vy = 0   and in check_goal: global state; if player.y > HEIGHT + 100: respawn(); if touches({'F'}): state = 'won'   and update starts with: if state != 'playing': return",
    ),
    _step(
        id="pyplat-12-camera",
        title="A camera",
        teaches=(
            "The level is twice as wide as the screen, so something has "
            "to decide which part you see. That is the camera: one number, "
            "how far along the level the left edge of the screen is. Aim "
            "it so the player's CENTRE is in the middle of the screen "
            "(player.x + player.w / 2 - WIDTH / 2) and clamp it to 0 and "
            "the level's width minus the screen's - max(0, min(len(level"
            "[0]) * TILE - WIDTH, target)) - so it never shows past the "
            "ends. camera_x is re-bound by update_camera, so `global "
            "camera_x`. To draw, shift the whole world left by the "
            "camera: ctx.save(), ctx.translate(-camera_x, 0), draw, "
            "ctx.restore(). The score is not part of the world: draw it "
            "after the restore."
        ),
        goal="Add camera_x = 0, following the player's centre and clamped to the level (update_camera, called from update; camera_x is re-bound, so global). Draw the tiles, coins and player translated by -camera_x, and the text after ctx.restore(). The check reads player, level and camera_x (a camera dict or object with an x works too).",
        starter=_P11,
        solution=_P12,
        check=_CHECK12,
        hint="camera_x = max(0, min(len(level[0]) * TILE - WIDTH, player.x + player.w / 2 - WIDTH / 2))   and in draw: ctx.save(); ctx.translate(-camera_x, 0); ...; ctx.restore(); draw_hud()",
    ),
    _step(
        id="pyplat-13-yours",
        title="Now it's yours",
        teaches=(
            "A whole platformer, and every part of it is something you "
            "can change. Ideas, easier first: more levels as more lists "
            "of strings, switched when you reach the flag; a timer with "
            "f'{seconds:.1f}'; spikes ('^') that respawn you - touches("
            "{'^'}); holding ArrowDown to drop through a ledge; a double "
            "jump; a jump buffer (a press just BEFORE landing still "
            "counts); enemies that walk back and forth and turn at walls; "
            "moving platforms; a camera that eases toward the player "
            "instead of locking to it; a level typed as a triple-quoted "
            "string and split with textwrap.dedent and splitlines."
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_P12,
        solution=_P12,
        check="",
    ),
)
