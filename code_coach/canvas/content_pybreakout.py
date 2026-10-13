"""Breakout in Python: the paddle-and-bricks game of the JavaScript Breakout track, taught the Python way.

Not a transliteration. The game is the same - a paddle that follows the keys
and the mouse, a ball with a velocity that bounces off the walls and the
paddle (the bounce angle depends on where it lands), a wall of bricks the
ball removes, a score, lives, a win, a game over and a restart - but the
parts are Python's own:

  * Paddle, Ball and Brick are `@dataclass` classes (a dict with the same
    keys works too, and every check accepts both)
  * the brick grid is one list comprehension with two `for` clauses, and
    `enumerate` over the row colours; `[Brick(...)] * 40` is the classic trap
  * destroyed bricks are *removed* with a comprehension (or `bricks[:] = `),
    never with `remove()` inside a `for` over the same list
  * `max`/`min` to clamp, `math.hypot` for a distance and a speed,
    `math.copysign` to say "this size, that way", `math.sin`/`math.cos`
    to split a speed into a direction
  * tuple unpacking (`ball.x, ball.y = 240, 200`), f-strings for the HUD,
    `not bricks` for the win (and why `any(bricks)` is the opposite question),
    a dict of messages, `global` only where a function re-binds a top-level
    name - and what Python does when it is missing

As in the other tracks, each step starts from the one before, finished, and a
check plays the game rather than reading the code. The checks read these
top-level names, and set them: paddle, ball, bricks, score, lives, state.
`bricks`, `score`, `lives` and `state` are re-bound by the program, so a check
always looks them up again rather than holding on to one.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

TRACK = "Breakout (Python)"

# -- Shared check helpers ---------------------------------------------------

#: Prepended to every check. A thing's fields can be a dict's or an object's,
#: so a check reads them with get() and writes them with put(), and never
#: cares which the learner chose. P() and B() look the paddle and the ball up
#: afresh: a program may re-bind either one.
_HELPERS = """def get(o, k, default=None):
    if isinstance(o, dict):
        return o.get(k, default)
    return getattr(o, k, default)


def put(o, k, v):
    if isinstance(o, dict):
        o[k] = v
    else:
        setattr(o, k, v)


def P():
    return g.paddle


def B():
    return g.ball


def place(x, y, vx, vy):
    for k, v in (('x', x), ('y', y), ('vx', vx), ('vy', vy)):
        put(B(), k, v)


def centre(p):
    return get(p, 'x') + get(p, 'w') / 2


"""

# -- The programs -----------------------------------------------------------

_I0 = "from canvas import ctx, WIDTH, HEIGHT, on_frame"
_I1 = "from dataclasses import dataclass\n\nfrom canvas import ctx, WIDTH, HEIGHT, on_frame"
_I2 = "from dataclasses import dataclass\n\nfrom canvas import ctx, WIDTH, HEIGHT, on_frame, keys"
_I3 = "from dataclasses import dataclass\n\nfrom canvas import ctx, WIDTH, HEIGHT, on_frame, keys, mouse"
_I4 = (
    "import math\nfrom dataclasses import dataclass\n\n"
    "from canvas import ctx, WIDTH, HEIGHT, on_frame, keys, mouse"
)
_I11 = (
    "import math\nfrom dataclasses import dataclass\n\n"
    "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down, keys, mouse"
)

_ROW_COLORS = "ROW_COLORS = ['#fc8181', '#f6ad55', '#f6e05e', '#68d391', '#63b3ed']"
_MESSAGES = "MESSAGES = {'over': 'Game over', 'won': 'You win!'}"

_CLASS_PADDLE = """@dataclass
class Paddle:
    x: float
    y: float
    w: float
    h: float
    speed: float = 360"""

_CLASS_BALL = """@dataclass
class Ball:
    x: float
    y: float
    r: float
    vx: float = 0
    vy: float = 0"""

_CLASS_BRICK = """@dataclass
class Brick:
    x: float
    y: float
    w: float
    h: float
    color: str = '#f6ad55'"""

_MAKE_BRICKS = """def make_bricks():
    return [
        Brick(16 + col * 56, 30 + row * 22, 50, 16, color)
        for row, color in enumerate(ROW_COLORS)
        for col in range(8)
    ]"""

_N_PADDLE = "paddle = Paddle(200, 296, 80, 10)"
_N_MOUSE = "last_mouse_x = mouse.x"
_N_BALL = "ball = Ball(240, 160, 8, 180, -180)"
_N_BRICKS = """bricks = [
    Brick(16 + col * 56, 30 + row * 22, 50, 16, color)
    for row, color in enumerate(ROW_COLORS)
    for col in range(8)
]"""
_N_BRICKS_CALL = "bricks = make_bricks()"
_N_SCORE = "score = 0"
_N_LIVES = "lives = 3"
_N_STATE = "state = 'playing'"

_MOVE_PADDLE2 = """def move_paddle(dt):
    if 'ArrowLeft' in keys:
        paddle.x -= paddle.speed * dt
    if 'ArrowRight' in keys:
        paddle.x += paddle.speed * dt
    paddle.x = max(0, min(WIDTH - paddle.w, paddle.x))"""

_MOVE_PADDLE3 = """def move_paddle(dt):
    global last_mouse_x
    if 'ArrowLeft' in keys:
        paddle.x -= paddle.speed * dt
    if 'ArrowRight' in keys:
        paddle.x += paddle.speed * dt
    if mouse.x != last_mouse_x:
        last_mouse_x = mouse.x
        paddle.x = mouse.x - paddle.w / 2
    paddle.x = max(0, min(WIDTH - paddle.w, paddle.x))"""

_MOVE_BALL = """def move_ball(dt):
    ball.x += ball.vx * dt
    ball.y += ball.vy * dt"""

_WALLS5 = """def bounce_off_walls():
    if ball.x - ball.r < 0:
        ball.x = ball.r
        ball.vx = math.copysign(ball.vx, 1)
    if ball.x + ball.r > WIDTH:
        ball.x = WIDTH - ball.r
        ball.vx = math.copysign(ball.vx, -1)
    if ball.y - ball.r < 0:
        ball.y = ball.r
        ball.vy = math.copysign(ball.vy, 1)
    if ball.y + ball.r > HEIGHT:
        ball.y = HEIGHT - ball.r
        ball.vy = math.copysign(ball.vy, -1)"""

_WALLS6 = """def bounce_off_walls():
    if ball.x - ball.r < 0:
        ball.x = ball.r
        ball.vx = math.copysign(ball.vx, 1)
    if ball.x + ball.r > WIDTH:
        ball.x = WIDTH - ball.r
        ball.vx = math.copysign(ball.vx, -1)
    if ball.y - ball.r < 0:
        ball.y = ball.r
        ball.vy = math.copysign(ball.vy, 1)"""

_HITS_RECT = """def hits_rect(c, r):
    nearest_x = max(r.x, min(c.x, r.x + r.w))
    nearest_y = max(r.y, min(c.y, r.y + r.h))
    return math.hypot(c.x - nearest_x, c.y - nearest_y) < c.r"""

_BOUNCE_PADDLE = """def bounce_off_paddle():
    if ball.vy > 0 and hits_rect(ball, paddle):
        speed = math.hypot(ball.vx, ball.vy)
        offset = (ball.x - (paddle.x + paddle.w / 2)) / (paddle.w / 2)
        angle = max(-1, min(1, offset)) * math.radians(60)
        ball.vx = speed * math.sin(angle)
        ball.vy = -speed * math.cos(angle)
        ball.y = paddle.y - ball.r"""

_BREAK = """def break_bricks():
    global bricks, score
    hit = [b for b in bricks if hits_rect(ball, b)]
    if hit:
        bricks = [b for b in bricks if b not in hit]
        ball.vy = -ball.vy
        score += 10 * len(hit)"""

_SERVE = """def serve():
    ball.x, ball.y = 240, 200
    ball.vx, ball.vy = 180, -180"""

_LOSE9 = """def lose_ball():
    global lives
    if ball.y - ball.r > HEIGHT:
        lives -= 1
        serve()"""

_LOSE10 = """def lose_ball():
    global lives, state
    if ball.y - ball.r > HEIGHT:
        lives -= 1
        if lives == 0:
            state = 'over'
        else:
            serve()"""

_WIN = """def check_win():
    global state
    if not bricks:
        state = 'won'"""

_RESTART = """def restart():
    global bricks, score, lives, state
    bricks = make_bricks()
    paddle.x = 200
    serve()
    score = 0
    lives = 3
    state = 'playing'"""

_KEYS11 = """def key_down(key):
    if key == 'Enter' and state != 'playing':
        restart()


on_key_down(key_down)"""

_UPDATE_PASS = """def update(dt):
    pass"""

_UPDATE2 = """def update(dt):
    move_paddle(dt)"""

_UPDATE4 = """def update(dt):
    move_paddle(dt)
    move_ball(dt)"""

_UPDATE5 = """def update(dt):
    move_paddle(dt)
    move_ball(dt)
    bounce_off_walls()"""

_UPDATE6 = """def update(dt):
    move_paddle(dt)
    move_ball(dt)
    bounce_off_walls()
    bounce_off_paddle()"""

_UPDATE8 = """def update(dt):
    move_paddle(dt)
    move_ball(dt)
    bounce_off_walls()
    bounce_off_paddle()
    break_bricks()"""

_UPDATE9 = """def update(dt):
    move_paddle(dt)
    move_ball(dt)
    bounce_off_walls()
    bounce_off_paddle()
    break_bricks()
    lose_ball()"""

_UPDATE10 = """def update(dt):
    if state != 'playing':
        return
    move_paddle(dt)
    move_ball(dt)
    bounce_off_walls()
    bounce_off_paddle()
    break_bricks()
    check_win()
    lose_ball()"""

_LOOP = """def loop(dt):
    update(dt)
    draw()


on_frame(loop)"""

_D_BG = "    ctx.fill_style = '#10141f'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n"
_D_BRICKS = "    for b in bricks:\n        ctx.fill_style = b.color\n        ctx.fill_rect(b.x, b.y, b.w, b.h)\n"
_D_PADDLE = "    ctx.fill_style = '#4fd1c5'\n    ctx.fill_rect(paddle.x, paddle.y, paddle.w, paddle.h)\n"
_D_BALL = (
    "    ctx.fill_style = 'white'\n    ctx.begin_path()\n"
    "    ctx.arc(ball.x, ball.y, ball.r, 0, math.tau)\n    ctx.fill()\n"
)
_HUD8 = (
    "    ctx.fill_style = 'white'\n    ctx.font = '16px monospace'\n"
    "    ctx.fill_text(f'Score: {score}', 10, 20)\n"
)
_HUD9 = _HUD8 + "    ctx.fill_text(f'Lives: {lives}', 390, 20)\n"
_HUD10 = _HUD9 + (
    "    if state in MESSAGES:\n        ctx.font = '32px monospace'\n"
    "        ctx.fill_text(MESSAGES[state], 150, 200)\n"
)
_HUD11 = _HUD10 + (
    "    if state != 'playing':\n        ctx.font = '16px monospace'\n"
    "        ctx.fill_text('Press Enter to play again', 130, 230)\n"
)


def _draw(*parts: str) -> str:
    return "def draw():\n" + "\n".join(parts)


def _program(imports: str, consts: str, classes: tuple[str, ...], names: tuple[str, ...], *funcs: str) -> str:
    """One whole program: imports, constants, classes, the game's names, then each function."""
    blocks = [imports]
    if consts:
        blocks.append(consts)
    blocks.extend(classes)
    blocks.append("\n".join(names))
    blocks.extend(funcs)
    return "\n\n\n".join(b.strip("\n") for b in blocks) + "\n"


_NONE: tuple[str, ...] = ()

_P0 = _program(_I0, "", _NONE, _NONE, _UPDATE_PASS, _draw(_D_BG), _LOOP)

_P1 = _program(
    _I1, "", (_CLASS_PADDLE,), (_N_PADDLE,),
    _UPDATE_PASS, _draw(_D_BG, _D_PADDLE), _LOOP,
)

_P2 = _program(
    _I2, "", (_CLASS_PADDLE,), (_N_PADDLE,),
    _MOVE_PADDLE2, _UPDATE2, _draw(_D_BG, _D_PADDLE), _LOOP,
)

_P3 = _program(
    _I3, "", (_CLASS_PADDLE,), (_N_PADDLE, _N_MOUSE),
    _MOVE_PADDLE3, _UPDATE2, _draw(_D_BG, _D_PADDLE), _LOOP,
)

_P4 = _program(
    _I4, "", (_CLASS_PADDLE, _CLASS_BALL), (_N_PADDLE, _N_MOUSE, _N_BALL),
    _MOVE_PADDLE3, _MOVE_BALL, _UPDATE4,
    _draw(_D_BG, _D_PADDLE, _D_BALL), _LOOP,
)

_P5 = _program(
    _I4, "", (_CLASS_PADDLE, _CLASS_BALL), (_N_PADDLE, _N_MOUSE, _N_BALL),
    _MOVE_PADDLE3, _MOVE_BALL, _WALLS5, _UPDATE5,
    _draw(_D_BG, _D_PADDLE, _D_BALL), _LOOP,
)

_P6 = _program(
    _I4, "", (_CLASS_PADDLE, _CLASS_BALL), (_N_PADDLE, _N_MOUSE, _N_BALL),
    _MOVE_PADDLE3, _MOVE_BALL, _WALLS6, _HITS_RECT, _BOUNCE_PADDLE, _UPDATE6,
    _draw(_D_BG, _D_PADDLE, _D_BALL), _LOOP,
)

_P7 = _program(
    _I4, _ROW_COLORS, (_CLASS_PADDLE, _CLASS_BALL, _CLASS_BRICK),
    (_N_PADDLE, _N_MOUSE, _N_BALL, _N_BRICKS),
    _MOVE_PADDLE3, _MOVE_BALL, _WALLS6, _HITS_RECT, _BOUNCE_PADDLE, _UPDATE6,
    _draw(_D_BG, _D_BRICKS, _D_PADDLE, _D_BALL), _LOOP,
)

_P8 = _program(
    _I4, _ROW_COLORS, (_CLASS_PADDLE, _CLASS_BALL, _CLASS_BRICK),
    (_N_PADDLE, _N_MOUSE, _N_BALL, _N_BRICKS, _N_SCORE),
    _MOVE_PADDLE3, _MOVE_BALL, _WALLS6, _HITS_RECT, _BOUNCE_PADDLE, _BREAK, _UPDATE8,
    _draw(_D_BG, _D_BRICKS, _D_PADDLE, _D_BALL, _HUD8), _LOOP,
)

_P9 = _program(
    _I4, _ROW_COLORS, (_CLASS_PADDLE, _CLASS_BALL, _CLASS_BRICK),
    (_N_PADDLE, _N_MOUSE, _N_BALL, _N_BRICKS, _N_SCORE, _N_LIVES),
    _MOVE_PADDLE3, _MOVE_BALL, _WALLS6, _HITS_RECT, _BOUNCE_PADDLE, _BREAK,
    _SERVE, _LOSE9, _UPDATE9,
    _draw(_D_BG, _D_BRICKS, _D_PADDLE, _D_BALL, _HUD9), _LOOP,
)

_P10 = _program(
    _I4, _ROW_COLORS + "\n" + _MESSAGES, (_CLASS_PADDLE, _CLASS_BALL, _CLASS_BRICK),
    (_N_PADDLE, _N_MOUSE, _N_BALL, _N_BRICKS, _N_SCORE, _N_LIVES, _N_STATE),
    _MOVE_PADDLE3, _MOVE_BALL, _WALLS6, _HITS_RECT, _BOUNCE_PADDLE, _BREAK, _WIN,
    _SERVE, _LOSE10, _UPDATE10,
    _draw(_D_BG, _D_BRICKS, _D_PADDLE, _D_BALL, _HUD10), _LOOP,
)

_P11 = _program(
    _I11, _ROW_COLORS + "\n" + _MESSAGES,
    (_CLASS_PADDLE, _CLASS_BALL, _CLASS_BRICK, _MAKE_BRICKS),
    (_N_PADDLE, _N_MOUSE, _N_BALL, _N_BRICKS_CALL, _N_SCORE, _N_LIVES, _N_STATE),
    _MOVE_PADDLE3, _MOVE_BALL, _WALLS6, _HITS_RECT, _BOUNCE_PADDLE, _BREAK, _WIN,
    _SERVE, _LOSE10, _RESTART, _KEYS11, _UPDATE10,
    _draw(_D_BG, _D_BRICKS, _D_PADDLE, _D_BALL, _HUD11), _LOOP,
)

# -- The checks ---------------------------------------------------------------

_CHECK1 = _HELPERS + """
expect('paddle' in g, "Make the paddle: paddle = Paddle(200, 296, 80, 10) (or a dict with x, y, w and h) - a name in your code, outside any function.")
p = g.paddle
expect(get(p, 'x') == 200 and get(p, 'y') == 296 and get(p, 'w') == 80 and get(p, 'h') == 10, "The paddle should start at x 200, y 296, 80 wide and 10 tall. The order matters: Paddle(x, y, w, h).")
cc.frames(1)
rects = cc.rects()
expect(rects and rects[0]['x'] == 0 and rects[0]['y'] == 0 and rects[0]['w'] >= WIDTH and rects[0]['h'] >= HEIGHT, "Each frame should start by painting the background over the whole canvas.")
at = [i for i, r in enumerate(rects) if near(r['x'], get(p, 'x'), 0.01) and near(r['y'], get(p, 'y'), 0.01) and r['w'] == get(p, 'w') and r['h'] == get(p, 'h')]
expect(at, "Draw the paddle every frame, inside draw(): ctx.fill_rect(paddle.x, paddle.y, paddle.w, paddle.h).")
expect(at[0] > 0, "The paddle has to be drawn after the background, or the background paints over it.")
expect(rects[at[0]]['fill'] != rects[0]['fill'], "The paddle is the same colour as the background, so you cannot see it. Set fill_style again before drawing the paddle.")
"""

_CHECK2 = _HELPERS + """
expect('paddle' in g, "Keep the paddle from the last step.")
x0 = get(P(), 'x')
cc.frames(30)
expect(near(get(P(), 'x'), x0, 0.01), "The paddle moves on its own. It should stand still until an arrow key is held.")
for dt, n in ((1 / 60, 30), (1 / 30, 15)):
    fps = round(1 / dt)
    put(P(), 'x', 200)
    cc.press('ArrowRight')
    cc.frames(n, dt)
    cc.release('ArrowRight')
    moved = get(P(), 'x') - 200
    expect(near(moved, 180, 9), f"At {fps} frames a second, half a second of ArrowRight moved the paddle {round(moved)} pixels; at a speed of 360 a second it should be about 180. Ask `keys` with `in` and move by paddle.speed * dt - dt is seconds, so the frame rate stops mattering.")
    cc.press('ArrowLeft')
    cc.frames(n, dt)
    cc.release('ArrowLeft')
    expect(near(get(P(), 'x'), 200, 9), f"At {fps} frames a second, half a second of ArrowLeft moved the paddle to x {round(get(P(), 'x'))}; it should be back near 200, the same speed the other way.")
x1 = get(P(), 'x')
cc.frames(30)
expect(near(get(P(), 'x'), x1, 0.01), "The paddle kept going after the key was let go. Move it only while the key is in `keys`.")
cc.press('ArrowRight')
cc.frames(180)
cc.release('ArrowRight')
expect(near(get(P(), 'x'), WIDTH - get(P(), 'w'), 0.01), f"After three seconds of ArrowRight the paddle is at x {round(get(P(), 'x'))}. It should stop with its right edge on the canvas edge: x = WIDTH - paddle.w. Clamp with max(0, min(WIDTH - paddle.w, paddle.x)).")
cc.press('ArrowLeft')
cc.frames(180)
cc.release('ArrowLeft')
expect(near(get(P(), 'x'), 0, 0.01), f"After three seconds of ArrowLeft the paddle is at x {round(get(P(), 'x'))}. It should stop at 0.")
cc.frames(1)
expect(any(near(r['x'], get(P(), 'x'), 0.01) and r['y'] == get(P(), 'y') and r['w'] == get(P(), 'w') for r in cc.rects()), "Keep drawing the paddle every frame, where it is now.")
"""

_CHECK3 = _HELPERS + """
cc.frames(5)
expect(near(get(P(), 'x'), 200, 0.01), f"The paddle moved by itself, to x {round(get(P(), 'x'))}, before the mouse did anything. mouse.x is 0 until the pointer first moves, so follow it only when it CHANGES: remember last_mouse_x = mouse.x at the start and compare.")
for dt in (1 / 60, 1 / 30):
    cc.pointer(300, 200)
    cc.frames(1, dt)
    c = centre(P())
    expect(near(c, 300, 1), f"The pointer is at x 300 but the paddle's centre is at {round(c)}. Put the CENTRE under the pointer: paddle.x = mouse.x - paddle.w / 2.")
    n = int(0.25 / dt)
    start = get(P(), 'x')
    cc.press('ArrowRight')
    cc.frames(n, dt)
    cc.release('ArrowRight')
    want = n * dt * 360
    moved = get(P(), 'x') - start
    expect(near(moved, want, 6), f"With the mouse still, ArrowRight moved the paddle {round(moved)} pixels in {n} frames; it should be about {round(want)}. If you set paddle.x from mouse.x every frame the mouse overwrites the keys - only follow it when mouse.x has changed since last time.")
    cc.pointer(5, 200)
    cc.frames(1, dt)
    expect(near(get(P(), 'x'), 0, 0.01), f"With the pointer near the left edge the paddle should stop at 0, not hang off the canvas - it is at {round(get(P(), 'x'))}. Clamp after you move it.")
    cc.pointer(478, 200)
    cc.frames(1, dt)
    expect(near(get(P(), 'x'), WIDTH - get(P(), 'w'), 0.01), f"With the pointer near the right edge the paddle should stop with its right edge on the canvas edge - it is at x {round(get(P(), 'x'))}.")
"""

_CHECK4 = _HELPERS + """
expect('ball' in g, "Make the ball: ball = Ball(240, 160, 8, 180, -180) - or a dict with x, y, r, vx and vy.")
b = g.ball
expect(get(b, 'x') == 240 and get(b, 'y') == 160 and get(b, 'r') == 8, "The ball starts at x 240, y 160 with a radius of 8: Ball(240, 160, 8, ...).")
expect(get(b, 'vx') == 180 and get(b, 'vy') == -180, "Give the ball vx 180 and vy -180 - pixels a second, and a negative vy goes UP.")
cc.frames(1)
b = B()
arc = next((a for a in cc.arcs() if near(a['x'], get(b, 'x'), 0.01) and near(a['y'], get(b, 'y'), 0.01) and a['r'] == get(b, 'r')), None)
expect(arc is not None, "Draw the ball each frame, inside draw(): ctx.arc(ball.x, ball.y, ball.r, 0, math.tau).")
names = [c['name'] for c in cc.drawn()]
i = max(i for i, n in enumerate(names) if n == 'arc')
expect('begin_path' in names[:i], "Call ctx.begin_path() before the arc, so each frame's circle is a new path.")
expect('fill' in names[i:], "An arc on its own is only an outline in waiting - call ctx.fill() after it.")
for dt, n in ((1 / 60, 30), (1 / 30, 15)):
    place(240, 160, 180, -180)
    cc.frames(n, dt)
    dx = get(B(), 'x') - 240
    dy = get(B(), 'y') - 160
    expect(near(dx, 90, 4), f"At {round(1 / dt)} frames a second the ball moved {round(dx)} pixels across in half a second; at vx 180 it should move 90. Use ball.x += ball.vx * dt.")
    expect(near(dy, -90, 4), f"At {round(1 / dt)} frames a second the ball moved {round(dy)} pixels down in half a second; at vy -180 it should move 90 UP, so y goes down by 90 the other way: ball.y += ball.vy * dt.")
"""

_CHECK5 = _HELPERS + """
for dt, frames in ((1 / 60, 600), (1 / 30, 300)):
    place(240, 160, 180, -180)
    xs, ys = [], []
    for i in range(1, frames + 1):
        cc.frames(1, dt)
        b = B()
        x, y, r = get(b, 'x'), get(b, 'y'), get(b, 'r')
        inside = x - r >= -0.01 and x + r <= WIDTH + 0.01 and y - r >= -0.01 and y + r <= HEIGHT + 0.01
        expect(inside, f"After {i} frames (at {round(1 / dt)} a second) the ball is at x {round(x)}, y {round(y)} - partly through a wall. When it crosses an edge, put it back on the edge as well as turning it round.")
        xs.append(x)
        ys.append(y)
    window = frames // 5
    expect(max(xs[-window:]) - min(xs[-window:]) > 30 and max(ys[-window:]) - min(ys[-window:]) > 30, "The ball has stopped or is stuck along a wall. At each wall, send it the other way - set the sign of the speed that wall flips, not just the position.")
    expect(min(xs) <= 8.5 and max(xs) >= WIDTH - 8.5 and min(ys) <= 8.5 and max(ys) >= HEIGHT - 8.5, "The ball should reach and bounce off all four walls - left, right, top and bottom.")
    b = B()
    expect(near(abs(get(b, 'vx')), 180, 0.01) and near(abs(get(b, 'vy')), 180, 0.01), "A bounce should change the ball's direction, not its speed - math.copysign(ball.vx, -1) keeps the size of vx and sets the way.")
"""

_CHECK6 = _HELPERS + """
import math

SPEED = math.hypot(180, 180)


def land(offset, dt):
    put(P(), 'x', 200)
    p = P()
    place(centre(p) + offset * get(p, 'w') / 2, get(p, 'y') - 30, 0, SPEED)
    for _ in range(40):
        if get(B(), 'vy') < 0:
            break
        cc.frames(1, dt)
    b = B()
    expect(get(b, 'vy') < 0, f"The ball fell onto the paddle (at {round(1 / dt)} frames a second) and did not bounce. When it is moving down (ball.vy > 0) and hits the paddle, send it up.")
    expect(near(math.hypot(get(b, 'vx'), get(b, 'vy')), SPEED, 1), "Aiming should change the ball's direction, not its speed - work out speed = math.hypot(ball.vx, ball.vy) first and keep it.")
    expect(get(b, 'y') + get(b, 'r') <= get(P(), 'y') + 0.01, "After the bounce the ball should sit on top of the paddle, not inside it: ball.y = paddle.y - ball.r. Left inside, it catches on the paddle.")
    return get(b, 'vx')


for dt in (1 / 60, 1 / 30):
    left = land(-0.9, dt)
    middle = land(0, dt)
    right = land(0.9, dt)
    expect(left < -100, f"Landing near the left end sent the ball off with vx {round(left)}; it should go well to the left. Work out how far from the middle it landed, -1 to 1, and turn that into an angle.")
    expect(right > 100, f"Landing near the right end sent the ball off with vx {round(right)}; it should go well to the right.")
    expect(abs(middle) < 10, f"Landing in the middle sent the ball off with vx {round(middle)}; it should go almost straight up.")
put(P(), 'x', 200)
p = P()
place(get(p, 'x') - 7, get(p, 'y') - 7, 0, 30)
cc.frames(1)
expect(get(B(), 'vy') > 0, "The ball bounced off empty space just past the paddle's corner. A circle only touches a box when the nearest point of the box is closer than the radius - treating the ball as a box bounces it off thin air.")
place(get(p, 'x') - 4, get(p, 'y') - 4, 0, 60)
cc.frames(1)
expect(get(B(), 'vy') < 0, "The ball touched the paddle's corner (the nearest point of the paddle is closer than the radius) and went straight through. Test the nearest point, not just the ball's centre.")
place(centre(p), get(p, 'y') + 5, 0, -100)
cc.frames(1)
expect(get(B(), 'y') > get(p, 'y'), "A ball already moving UP through the paddle was lifted on top of it. Only bounce a ball that is moving down: ball.vy > 0.")
for dt, n in ((1 / 60, 60), (1 / 30, 30)):
    put(P(), 'x', 0)
    place(400, 250, 0, 180)
    cc.frames(n, dt)
    expect(get(B(), 'y') > HEIGHT, "The ball missed the paddle and bounced off the floor. Take the floor bounce out - a miss is a miss.")
"""

_CHECK7 = _HELPERS + """
expect('bricks' in g and isinstance(g.bricks, list), "Make a list called bricks - a name in your code, outside any function.")
bs = g.bricks
expect(len(bs) == 40, f"There are {len(bs)} bricks; 5 rows of 8 is 40. A comprehension with two for clauses (for row ... for col ...) makes them.")
places = {(get(b, 'x'), get(b, 'y')) for b in bs}
expect(len(places) == 40, "Some bricks are on top of each other - x should come from the column and y from the row. (And [Brick(...)] * 40 is ONE brick forty times: the list holds forty names for the same object.)")
xs = {get(b, 'x') for b in bs}
ys = {get(b, 'y') for b in bs}
expect(xs == {16 + c * 56 for c in range(8)} and ys == {30 + r * 22 for r in range(5)}, "The bricks should make a grid: x is 16 + col * 56 for 8 columns, y is 30 + row * 22 for 5 rows.")
expect(all(get(b, 'w') == 50 and get(b, 'h') == 16 for b in bs), "Every brick is 50 wide and 16 tall.")
cc.frames(1)
drawn = cc.rects()
expect(all(any(r['x'] == get(b, 'x') and r['y'] == get(b, 'y') and r['w'] == get(b, 'w') and r['h'] == get(b, 'h') for r in drawn) for b in bs), "Draw every brick each frame: for b in bricks: ctx.fill_rect(b.x, b.y, b.w, b.h).")
"""

_CHECK8 = _HELPERS + """
import re

expect('score' in g and isinstance(g.score, (int, float)) and g.score == 0, "Start with score = 0.")
cc.frames(1)
expect(any(re.search('score', t, re.I) and '0' in t for t in cc.texts()), "Show the score on the screen from the start: it should say Score: 0.")
orig = list(g.bricks)
expect(len(orig) == 40, "Keep the 40 bricks from the last step.")
bottom_y = max(get(b, 'y') for b in orig)
bottom = sorted((b for b in orig if get(b, 'y') == bottom_y), key=lambda b: get(b, 'x'))
bh = get(bottom[0], 'h')


def shoot(x, dt, below=9, vy=-180, tries=12):
    g.bricks = list(orig)
    g.score = 0
    place(x, bottom_y + bh + below, 0, vy)
    n0 = len(g.bricks)
    for _ in range(tries):
        cc.frames(1, dt)
        if len(g.bricks) != n0:
            break
    return n0


target = bottom[2]
for dt in (1 / 60, 1 / 30):
    n0 = shoot(centre(target), dt)
    left = len(g.bricks)
    expect(left != n0, f"The ball flew into a brick (at {round(1 / dt)} frames a second) and nothing broke. Take every brick the ball touches out of bricks.")
    expect(left == n0 - 1, f"Exactly one brick should break here, but {n0 - left} did.")
    expect(all(b is not target for b in g.bricks), "A brick broke, but not the one the ball hit. Keep the bricks the ball is NOT touching: [b for b in bricks if b not in hit].")
    expect(g.score == 10, f"A brick is worth 10; the score is {g.score}.")
    cc.frames(10, dt)
    expect(get(B(), 'vy') > 0, "After breaking a brick the ball should bounce back down: flip ball.vy once.")
    expect(any('10' in t for t in cc.texts()), "Show the score on the screen - it should say 10 now.")
corner = bottom[0]
n0 = shoot(get(corner, 'x') - 4, 1 / 60, below=4, vy=-60, tries=3)
expect(len(g.bricks) == n0 - 1, "The ball touched a brick's corner (the nearest point of the brick is closer than its radius) and went through. Test the nearest point of the brick, not just the ball's centre: use hits_rect.")
a, b2 = bottom[5], bottom[6]
gap_x = (get(a, 'x') + get(a, 'w') + get(b2, 'x')) / 2
for dt in (1 / 60, 1 / 30):
    n0 = shoot(gap_x, dt)
    left = len(g.bricks)
    expect(left == n0 - 2, f"The ball flew into the gap between two bricks, touching both, and {n0 - left} broke on that frame; both should go. Collect everything it touches first, then remove them all together - take bricks out of a list while a `for` is walking it and the next one is skipped.")
    expect(g.score == 20, f"Two bricks broke, 10 each: the score should be 20, not {g.score}.")
    cc.frames(10, dt)
    expect(get(B(), 'vy') > 0, "After breaking two bricks at once the ball should still turn round - once. Flip ball.vy once per frame, not once per brick (twice is no flip at all).")
"""

_CHECK9 = _HELPERS + """
expect('lives' in g and g.lives == 3, "Start with lives = 3.")
cc.frames(30)
expect(g.lives == 3, f"The lives dropped to {g.lives} before any ball was lost. Take one off only when the ball is below the bottom.")
expect(any('3' in t for t in cc.texts()), "Show the lives on the screen - it should say 3.")


def drop(dt):
    put(P(), 'x', 0)
    place(400, 280, 0, 300)
    before = g.lives
    for _ in range(60):
        cc.frames(1, dt)
        if g.lives != before:
            break
    return before


before = drop(1 / 60)
expect(g.lives == before - 1, f"A ball fell off the bottom and the lives are {g.lives}; they should be {before - 1}. When the whole ball is below the bottom edge (ball.y - ball.r > HEIGHT), take one off.")
b = B()
expect(get(b, 'y') - get(b, 'r') <= HEIGHT and get(b, 'vy') < 0, "After a lost ball, serve a new one: back near x 240, y 200, going up. Without that the ball is still below the screen next frame and costs another life, and another, every frame.")
expect(near(get(b, 'x'), 240, 14) and near(get(b, 'y'), 200, 14), f"The new ball should start in the middle, near x 240, y 200; it is at x {round(get(b, 'x'))}, y {round(get(b, 'y'))}.")
cc.frames(30)
expect(g.lives == before - 1, f"The lives kept falling after the new ball was served ({g.lives}). One lost ball costs one life.")
expect(any('2' in t for t in cc.texts()), "Show the lives on the screen - it should say 2 now.")
before = drop(1 / 30)
expect(g.lives == before - 1 == 1, f"A second lost ball should leave 1 life; the lives are {g.lives}.")
expect(get(B(), 'vy') < 0, "After the second lost ball, serve another one going up.")
cc.frames(1)
expect(any('1' in t for t in cc.texts()), "Show the lives on the screen - it should say 1 now.")
"""

_CHECK10 = _HELPERS + """
import re

expect('state' in g and g.state == 'playing', "Keep what the game is doing in a top-level state = 'playing'.")
orig = list(g.bricks)
target = max(orig, key=lambda b: (get(b, 'y'), -abs(get(b, 'x') - 150)))
cc.frames(2)
expect(g.state == 'playing', f"The game is already '{g.state}' two frames in, with a full wall of bricks and lives to spare. It is won only when NO brick is left - `not bricks` - and over only when the lives run out.")
g.bricks = [target]
cc.frames(1)
expect(g.state == 'playing', "The game was won with a brick still standing. Win when the list is empty: `if not bricks:` - an empty list is falsy, a list with anything in it is truthy.")
place(centre(target), get(target, 'y') + get(target, 'h') + 9, 0, -180)
for _ in range(12):
    cc.frames(1)
    if g.state != 'playing':
        break
expect(len(g.bricks) == 0, "The last brick should break, as before.")
expect(g.state == 'won', f"With every brick broken the game should be won; state is {g.state!r}. After the bricks are broken, `if not bricks: state = 'won'`.")
cc.frames(1)
expect(any(re.search('win', t, re.I) for t in cc.texts()), "Tell the player they won: write 'You win!' on the screen when state is 'won'.")
frozen = (get(B(), 'x'), get(B(), 'y'))
cc.frames(20)
expect((get(B(), 'x'), get(B(), 'y')) == frozen, "After the game is won the ball keeps moving. Start update with: if state != 'playing': return")


def drop(dt):
    put(P(), 'x', 0)
    place(400, 280, 0, 300)
    cc.frames(30, dt)


g.state = 'playing'
g.bricks = list(orig)
g.lives = 2
drop(1 / 60)
expect(g.lives == 1 and g.state == 'playing', f"One ball lost with lives to spare: there should be 1 life left and the game still playing - lives is {g.lives}, state is {g.state!r}. The game is over when the lives reach 0.")
g.lives = 1
drop(1 / 30)
expect(g.lives == 0 and g.state == 'over', f"The last life was lost: lives should be 0 and state 'over' - lives is {g.lives}, state is {g.state!r}.")
cc.frames(1)
expect(any(re.search('game over', t, re.I) for t in cc.texts()), "When the game is over, write 'Game over' on the screen.")
frozen = (get(B(), 'x'), get(B(), 'y'))
cc.frames(20)
expect(g.lives == 0 and (get(B(), 'x'), get(B(), 'y')) == frozen, "After the game is over nothing should move or cost another life. Start update with: if state != 'playing': return")
"""

_CHECK11 = _HELPERS + """
import re

expect(len(g.bricks) == 40 and g.lives == 3 and g.state == 'playing', "Keep the game from the last step: 40 bricks, 3 lives, state 'playing'.")
expected = {(get(b, 'x'), get(b, 'y')) for b in g.bricks}
g.bricks = g.bricks[:20]
g.score = 30
g.lives = 2
put(P(), 'x', 50)
place(240, 250, 0, 0)
cc.press('Enter')
cc.release('Enter')
cc.frames(1)
expect(len(g.bricks) == 20 and g.score == 30 and g.lives == 2 and g.state == 'playing', "Enter in the middle of a game restarted it. Only restart when the game is over or won: `state != 'playing'`.")
g.lives = 1
put(P(), 'x', 0)
place(400, 280, 0, 300)
cc.frames(30)
expect(g.state == 'over', "The last life should end the game - that part is from step 10.")
cc.frames(1)
expect(any(re.search('enter', t, re.I) for t in cc.texts()), "On the end screen, tell the player how to go again: 'Press Enter to play again'.")
cc.press('ArrowLeft')
cc.release('ArrowLeft')
cc.press(' ')
cc.release(' ')
expect(g.state == 'over', "A key other than Enter restarted the game. Only Enter should.")
cc.press('Enter')
cc.release('Enter')
expect(g.state == 'playing', f"Pressing Enter after a game over should start a new game: state is {g.state!r}. restart() assigns state, so it needs `global state` - without it Python makes a quiet local variable and the real one never changes.")
expect(g.score == 0, f"A new game starts with a score of 0; it is {g.score}.")
expect(g.lives == 3, f"A new game starts with 3 lives; it is {g.lives}.")
expect(len(g.bricks) == 40 and {(get(b, 'x'), get(b, 'y')) for b in g.bricks} == expected, f"A new game needs a full wall of 40 bricks - there are {len(g.bricks)}. Build a new list: bricks = make_bricks() (and `global bricks`).")
b = B()
expect(near(get(b, 'x'), 240, 14) and near(get(b, 'y'), 200, 14) and get(b, 'vy') < 0, "A new game serves a new ball from x 240, y 200, going up: call serve() in restart().")
expect(near(get(P(), 'x'), 200, 1), "A new game puts the paddle back at x 200.")
cc.frames(1)
expect(not any(re.search('game over', t, re.I) for t in cc.texts()), "'Game over' is still on the screen after the restart.")
cc.frames(30)
expect(g.state == 'playing' and g.lives == 3, f"The new game fell over at once (state {g.state!r}, lives {g.lives}). Put everything back: the ball, the lives, the state.")
g.bricks = []
g.state = 'won'
cc.press('Enter')
cc.release('Enter')
expect(g.state == 'playing' and len(g.bricks) == 40, "Enter after winning should start a new game too: a full wall of bricks and state 'playing'.")
cc.frames(30)
expect(g.state == 'playing', "The new game after a win ended at once. Is the wall of bricks back?")
"""


def _step(**fields: object) -> Step:
    """A step on this track: Python, in the Python Breakout track."""
    fields["track"] = TRACK
    fields["language"] = "python"
    return Step(**fields)  # type: ignore[arg-type]


PYBREAKOUT_STEPS: tuple[Step, ...] = (
    _step(
        id="pybo-01-paddle",
        title="The paddle is a dataclass",
        teaches=(
            "A game keeps what it knows about each thing in one place: where "
            "it is, how big it is, how fast it goes. Python's tidy way to "
            "write that down is a @dataclass (from dataclasses import "
            "dataclass). List the fields with their types and Python writes "
            "the constructor for you, so Paddle(200, 296, 80, 10) makes a "
            "paddle and paddle.x reads its x. A field with = 360 after it has "
            "a default you can leave out. The dataclass reads as paddle.x "
            "instead of paddle['x'], prints as Paddle(x=200, ...) and "
            "compares by value. A plain dict - {'x': 200, 'y': 296, 'w': 80, "
            "'h': 10} - works too, and the checks accept either. A box is "
            "placed by its top-left corner, so its right edge is x + w. Draw "
            "it after the background: the canvas paints back to front."
        ),
        goal="Add a Paddle dataclass with fields x, y, w, h and speed (default 360) and make paddle = Paddle(200, 296, 80, 10) - a dict with those keys works too. Draw it every frame, after the background, as a filled rectangle.",
        starter=_P0,
        solution=_P1,
        check=_CHECK1,
        hint="@dataclass class Paddle: x: float, y: float, w: float, h: float, speed: float = 360   then   ctx.fill_rect(paddle.x, paddle.y, paddle.w, paddle.h) in draw().",
    ),
    _step(
        id="pybo-02-keys",
        title="Steer with the keys",
        teaches=(
            "`keys` (import it from canvas) is a set of the names of the keys "
            "held right now - 'ArrowLeft', 'ArrowRight', ' ' for the space "
            "bar, 'Enter', 'a' to 'z'. It fills and empties itself; you only "
            "ask it, with `in`: if 'ArrowLeft' in keys. Move by speed * dt. "
            "dt is the SECONDS since the last frame (about 0.0167), so a "
            "speed of 360 means 360 pixels a second at any frame rate - "
            "paddle.x += 4 would be twice as fast on a screen that draws "
            "twice as often. Then clamp: max(low, min(high, x)) is x unless "
            "it is below low or above high. The paddle's x is its left edge, "
            "so the right-most it can go is WIDTH - paddle.w. One small "
            "function per rule - move_paddle(dt) - keeps update(dt) readable. "
            "Click the game before pressing keys, so it has the keyboard."
        ),
        goal="Add move_paddle(dt), called from update(dt): while ArrowLeft is held the paddle moves left, and while ArrowRight is held it moves right, at paddle.speed pixels a second, and it never leaves the canvas.",
        starter=_P1,
        solution=_P2,
        check=_CHECK2,
        hint="if 'ArrowLeft' in keys: paddle.x -= paddle.speed * dt   (and += for ArrowRight), then paddle.x = max(0, min(WIDTH - paddle.w, paddle.x))",
    ),
    _step(
        id="pybo-03-mouse",
        title="Steer with the mouse",
        teaches=(
            "`mouse` (import it from canvas) has mouse.x and mouse.y: where "
            "the pointer is, already in canvas pixels, 0 to 480, however big "
            "the page draws the canvas - there is no page-pixel sum to do. "
            "But mouse.x is where the mouse IS, not an event. Before it has "
            "moved it is 0, and if you set paddle.x from it every frame the "
            "paddle sits at the left edge and the mouse overwrites the arrow "
            "keys. So remember where it was: last_mouse_x = mouse.x at the "
            "start; when mouse.x != last_mouse_x the mouse has moved, so "
            "take the new place and put the paddle's CENTRE under it "
            "(paddle.x = mouse.x - paddle.w / 2). A function that re-binds a "
            "top-level name needs `global last_mouse_x`; without it Python "
            "makes a local variable and fails with UnboundLocalError. Clamp "
            "after both, so keys and mouse stay on the canvas."
        ),
        goal="Let the mouse steer too: remember where the mouse was last (last_mouse_x = mouse.x), and when mouse.x changes put the paddle's centre under it. The arrow keys still work, and the paddle stays on the canvas.",
        starter=_P2,
        solution=_P3,
        check=_CHECK3,
        hint="if mouse.x != last_mouse_x: last_mouse_x = mouse.x; paddle.x = mouse.x - paddle.w / 2   - and `global last_mouse_x` at the top of move_paddle.",
    ),
    _step(
        id="pybo-04-ball",
        title="A ball with a velocity",
        teaches=(
            "Ball is a second dataclass: x, y, r (the radius) and a "
            "velocity. A velocity has two parts, vx pixels a second sideways "
            "and vy pixels a second DOWN - y grows downwards, so a negative "
            "vy goes up. Fields with defaults (vx: float = 0) must come "
            "after the ones without. Each frame x += vx * dt and y += vy * "
            "dt - the same delta time as the paddle. A circle is a path: "
            "ctx.begin_path() starts a new one, ctx.arc(x, y, r, 0, "
            "math.tau) traces a full turn round its CENTRE (angles are in "
            "radians, and math.tau is a full turn, 2 * pi), and ctx.fill() "
            "paints what was traced. Leave out begin_path and the next fill "
            "paints every arc since the last one again - the classic "
            "smeared trail."
        ),
        goal="Add a Ball dataclass (x, y, r, vx, vy) and ball = Ball(240, 160, 8, 180, -180) - a dict with those keys works too. Move it every frame by its velocity times dt, and draw it as a filled circle.",
        starter=_P3,
        solution=_P4,
        check=_CHECK4,
        hint="def move_ball(dt): ball.x += ball.vx * dt; ball.y += ball.vy * dt   and in draw(): ctx.begin_path(); ctx.arc(ball.x, ball.y, ball.r, 0, math.tau); ctx.fill()",
    ),
    _step(
        id="pybo-05-walls",
        title="Bounce off the walls",
        teaches=(
            "A bounce off a side wall flips vx; off the top or the bottom, "
            "vy. Flipping alone is not enough: by the time you notice, the "
            "ball is a little way into the wall, and if it is still in "
            "there next frame it flips again and sticks, shivering. So put "
            "it back on the edge as well, and SET the direction instead of "
            "flipping it: math.copysign(x, sign) gives x's size with the "
            "sign you pass in, so math.copysign(ball.vx, -1) means 'vx's "
            "size, going left' however many frames it takes to get out. "
            "(-abs(ball.vx) says the same.) The ball's edge is its centre "
            "plus or minus r, so the left wall is ball.x - ball.r < 0. For "
            "now the floor bounces too, so the ball cannot get away."
        ),
        goal="Add bounce_off_walls(): keep the ball inside all four edges - when its edge crosses a wall, put it back on the wall and send it the other way at the same speed.",
        starter=_P4,
        solution=_P5,
        check=_CHECK5,
        hint="if ball.x + ball.r > WIDTH: ball.x = WIDTH - ball.r; ball.vx = math.copysign(ball.vx, -1)   and the same idea for the other three walls.",
    ),
    _step(
        id="pybo-06-paddle-bounce",
        title="Bounce and aim off the paddle",
        teaches=(
            "Does a circle touch a box? Find the point of the box nearest "
            "the circle's centre - clamp the centre's x into the box's left "
            "and right, max(r.x, min(c.x, r.x + r.w)), and the same for y - "
            "and they touch if that point is closer than the radius. "
            "math.hypot(dx, dy) is the distance, no square root to write. "
            "Treating the ball as a box makes it bounce off thin air at the "
            "corners; testing only its centre lets it sink in. Only bounce "
            "a ball that is moving down (ball.vy > 0), and sit it back on "
            "top of the paddle (ball.y = paddle.y - ball.r), or it catches "
            "and rattles. Then let the player aim: how far from the middle "
            "did it land, -1 to 1 (offset)? Turn that into an angle, up to "
            "60 degrees (math.radians(60)), keep the speed (math.hypot(vx, "
            "vy)) and split it with trigonometry: speed * math.sin(angle) "
            "goes sideways, -speed * math.cos(angle) goes up. The floor "
            "stops bouncing now: miss, and the ball is gone."
        ),
        goal="Write hits_rect(c, r) the circle way, with max, min and math.hypot. In bounce_off_paddle(), when the ball is moving down and hits the paddle, sit it on top of the paddle and send it off at an angle set by where it landed - left end left, middle straight up, right end right - at the same speed. Take the floor bounce out.",
        starter=_P5,
        solution=_P6,
        check=_CHECK6,
        hint="nearest_x = max(r.x, min(c.x, r.x + r.w)) (and y), then math.hypot(c.x - nearest_x, c.y - nearest_y) < c.r   -   offset = (ball.x - paddle centre) / (paddle.w / 2), angle = offset * math.radians(60).",
    ),
    _step(
        id="pybo-07-bricks",
        title="A wall of bricks",
        teaches=(
            "Forty bricks are not typed out; they are built. A list "
            "comprehension can have two for clauses, and that is a nested "
            "loop in one expression: [Brick(...) for row, color in "
            "enumerate(ROW_COLORS) for col in range(8)] counts rows in the "
            "outer loop and columns in the inner one. enumerate hands back "
            "(index, item) pairs, which the for unpacks - the row number and "
            "its colour. Each brick's place is arithmetic: x = left + col * "
            "(width + gap). Beware the shortcut [Brick(16, 30, 50, 16)] * "
            "40: it does not make forty bricks, it makes one brick and "
            "forty names for it. Give Brick a colour field with a default, "
            "and draw every brick."
        ),
        goal="Add a Brick dataclass (x, y, w, h and a color) and build bricks, a list of 5 rows of 8 with a list comprehension: x 16 + col * 56, y 30 + row * 22, each 50 by 16, a colour for each row. Draw every brick, behind the paddle and ball.",
        starter=_P6,
        solution=_P7,
        check=_CHECK7,
        hint="bricks = [Brick(16 + col * 56, 30 + row * 22, 50, 16, color) for row, color in enumerate(ROW_COLORS) for col in range(8)]",
    ),
    _step(
        id="pybo-08-break",
        title="Break bricks, keep score",
        teaches=(
            "Each frame, ask which bricks the ball touches: hit = [b for b "
            "in bricks if hits_rect(ball, b)]. (any(hits_rect(ball, b) for "
            "b in bricks) is the yes-or-no version, but you need to know "
            "which.) If there are any, build the list again without them - "
            "bricks = [b for b in bricks if b not in hit] - flip ball.vy "
            "once, and add 10 for each. Never call bricks.remove(b) inside a "
            "`for b in bricks:` loop: removing shifts every later brick one "
            "place down and the loop steps over the next one, a bug that "
            "only shows when two bricks are hit together. Re-binding the "
            "name needs `global bricks` (so does score += 10, "
            "`global score`); bricks[:] = [...] changes the list in place "
            "instead and needs neither. Show the score with an f-string: "
            "f'Score: {score}'."
        ),
        goal="Add score = 0 and break_bricks(), called from update(dt). Every brick the ball touches in a frame is removed from bricks and scores 10, and the ball turns round once (flip ball.vy). Show the score as text on the screen.",
        starter=_P7,
        solution=_P8,
        check=_CHECK8,
        hint="hit = [b for b in bricks if hits_rect(ball, b)]; if hit: bricks = [b for b in bricks if b not in hit]; ball.vy = -ball.vy; score += 10 * len(hit)   (global bricks, score)",
    ),
    _step(
        id="pybo-09-lives",
        title="Three lives",
        teaches=(
            "A ball whose top is below the bottom edge (ball.y - ball.r > "
            "HEIGHT) is a lost ball: take one life off and serve a new one "
            "from the middle. serve() is a function of its own because "
            "restarting will want it too, and tuple unpacking sets two "
            "fields at once: ball.x, ball.y = 240, 200 (the right side is a "
            "tuple, the left side takes it apart). Serving is what makes "
            "the loss count ONCE. Take a life without serving and the "
            "ball is still below the screen next frame, and costs another "
            "life, and another - sixty a second. lose_ball() re-binds "
            "lives, so it needs `global lives`. Draw the lives where the "
            "player can see them: f'Lives: {lives}'."
        ),
        goal="Add lives = 3 and serve(), which puts the ball at x 240, y 200 going up (vx 180, vy -180). When the ball is completely below the bottom edge it costs one life and serves a new ball. Show the lives on the screen.",
        starter=_P8,
        solution=_P9,
        check=_CHECK9,
        hint="if ball.y - ball.r > HEIGHT: lives -= 1; serve()   with   def serve(): ball.x, ball.y = 240, 200; ball.vx, ball.vy = 180, -180",
    ),
    _step(
        id="pybo-10-win-over",
        title="Win and game over",
        teaches=(
            "The game needs to know what it is doing: state = 'playing', "
            "'won' or 'over'. update() does nothing unless it is 'playing' "
            "- a one-line guard at the top that stops the ball, the paddle "
            "and the lives together. Lose is the lives reaching 0. Win is "
            "no bricks left, and Python says that as `not bricks`: an empty "
            "list is falsy and a list with anything in it is truthy. Do not "
            "reach for any(): any(bricks) asks 'is there at least one?', "
            "the opposite question, and it is True the moment the game "
            "starts. (all(...) over an empty list is True - handy if "
            "bricks were flagged instead of removed.) A dict of messages, "
            "MESSAGES[state], picks the words on the end screen. state is "
            "assigned in functions, so each needs it on its `global` line."
        ),
        goal="Add state = 'playing'. When the lives run out, set state to 'over'; when no bricks are left, set it to 'won'. While state is not 'playing', update does nothing. Write 'Game over' or 'You win!' on the screen.",
        starter=_P9,
        solution=_P10,
        check=_CHECK10,
        hint="if not bricks: state = 'won'   and   if lives == 0: state = 'over' else: serve()   and  if state != 'playing': return  at the top of update.",
    ),
    _step(
        id="pybo-11-restart",
        title="Play again",
        teaches=(
            "A restart puts back everything that changed during play: "
            "bricks, paddle, ball, score, lives and state. Every name it "
            "re-binds goes on its `global` line - leave score off and "
            "`score = 0` quietly makes a local variable while the real "
            "score stays. The bricks need a function that builds a NEW list "
            "each time it is called, make_bricks(): hand the old name "
            "another list and you get back the same wall, already broken. "
            "Keys that do something once are events, not held keys: "
            "on_key_down(fn) calls fn(key) when a key goes down. Enter "
            "restarts only when the game is over or won, so a stray key in "
            "the middle of a game does not wipe it. Tell the player which "
            "key, on the end screen."
        ),
        goal="Add make_bricks() and write restart() - a fresh wall, paddle back at x 200, a new ball served, score 0, lives 3, state 'playing' - and call it when Enter is pressed while the game is over or won, but not during play. Write 'Press Enter to play again' on the end screen.",
        starter=_P10,
        solution=_P11,
        check=_CHECK11,
        hint="def restart(): global bricks, score, lives, state; bricks = make_bricks(); paddle.x = 200; serve(); score = 0; lives = 3; state = 'playing'   and   if key == 'Enter' and state != 'playing': restart()",
    ),
    _step(
        id="pybo-12-yours",
        title="Now it's yours",
        teaches=(
            "A whole game: two ways to steer, a bouncing ball you can aim, "
            "a wall that breaks, score, lives, a win, a game over and a "
            "restart. Ideas, easier first: bricks worth more near the top "
            "(a points field on Brick); bricks that take two hits; the ball "
            "speeding up a little on every paddle hit; a level drawn as "
            "strings, like '##.##.##', turned into bricks by enumerate; a "
            "ball trail - give Ball trail: list = field(default_factory="
            "list), because a plain `= []` is refused (ValueError: mutable "
            "default) to stop every ball sharing ONE list, the same trap "
            "as def f(seen=[]); power-ups that fall from broken bricks and "
            "widen the paddle (after(10, fn) puts it back); two balls "
            "(make ball a list and loop); a pause on 'p', which is another "
            "state."
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_P11,
        solution=_P11,
        check="",
    ),
)
