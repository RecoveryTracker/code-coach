"""The "From blank (Python)" Canvas track: build a whole small project yourself, in Python.

The Python twin of the "From blank" track (content_blank.py). Every other
track hands you the previous step's finished code and asks for one change.
This one hands you nothing: a spec and a check. Each project is ONE step whose
starter is only the two setup lines, whose goal is a full spec (numbered
requirements, with the names and numbers the check reads), and whose check
plays what you built.

The steps are independent: a starter is NOT the previous solution. The checks
play the program rather than read it, and read only the names the spec
states (left, right, ball, score ...) - everything else about how it is
written is yours, so any structure that behaves right passes. A thing's
fields may be a dict's or an object's (a @dataclass, a SimpleNamespace); the
checks read and set them with get() and put() and never care which.

The Python is Python's own, not JavaScript in Python clothes: `@dataclass` or
dict entities, comprehensions that build a grid (and the `[[0] * W] * H`
trap), `random.shuffle`, `enumerate`/`divmod`/`zip`, `after()` and `every()`
for time, tuple unpacking, `any`/`all`, f-strings, `global` where a function
re-binds a name.

Projects: Pong for two, a Flappy-style gap game, Memory cards (clicks), a
falling-blocks stacker, and an open step.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

TRACK = "From blank (Python)"

#: Prepended to every check. Fields are a dict's or an object's, so a check
#: reads and sets them with get() and put(); `need` is how a check says that a
#: name the spec asks for is missing, in the check's own words ("Requirement N")
#: rather than the harness's.
_HELPERS = '''def get(o, k, default=None):
    if isinstance(o, dict):
        return o.get(k, default)
    return getattr(o, k, default)


def put(o, k, v):
    if isinstance(o, dict):
        o[k] = v
    else:
        setattr(o, k, v)


def need(name, message):
    expect(name in g, message)


def num(v):
    return round(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else v


def show(o, *ks):
    return ", ".join(f"{k} {num(get(o, k))}" for k in ks)


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)

'''

_SETUP = """import random

from canvas import ctx, WIDTH, HEIGHT, on_frame, keys, on_key_down, on_click, after, every
"""

_BLANK = _SETUP + "\n# Your game goes here.\n"

# ── 1. Pong for two ──────────────────────────────────────────────────────

_PONG = """import math

from canvas import ctx, WIDTH, HEIGHT, on_frame, keys, on_key_down

left = {'x': 20, 'y': 130, 'w': 10, 'h': 60, 'speed': 300}
right = {'x': 450, 'y': 130, 'w': 10, 'h': 60, 'speed': 300}
ball = {'x': 240, 'y': 160, 'r': 8, 'vx': 220, 'vy': 140}
score = {'left': 0, 'right': 0}


def serve(direction):
    ball['x'], ball['y'] = 240, 160
    ball['vx'], ball['vy'] = 220 * direction, 140


def new_match(key):
    if key == 'r':
        score['left'] = score['right'] = 0
        left['y'] = right['y'] = 130
        serve(1)


on_key_down(new_match)


def hits(b, p):
    nearest_x = max(p['x'], min(b['x'], p['x'] + p['w']))
    nearest_y = max(p['y'], min(b['y'], p['y'] + p['h']))
    return math.hypot(b['x'] - nearest_x, b['y'] - nearest_y) < b['r']


def move_paddle(p, up, down, dt):
    if up in keys:
        p['y'] -= p['speed'] * dt
    if down in keys:
        p['y'] += p['speed'] * dt
    p['y'] = max(0, min(HEIGHT - p['h'], p['y']))


def update(dt):
    for paddle, up, down in ((left, 'w', 's'), (right, 'ArrowUp', 'ArrowDown')):
        move_paddle(paddle, up, down, dt)

    ball['x'] += ball['vx'] * dt
    ball['y'] += ball['vy'] * dt
    if ball['y'] - ball['r'] < 0:
        ball['y'] = ball['r']
        ball['vy'] = abs(ball['vy'])
    if ball['y'] + ball['r'] > HEIGHT:
        ball['y'] = HEIGHT - ball['r']
        ball['vy'] = -abs(ball['vy'])
    if ball['vx'] < 0 and hits(ball, left):
        ball['x'] = left['x'] + left['w'] + ball['r']
        ball['vx'] = abs(ball['vx'])
    if ball['vx'] > 0 and hits(ball, right):
        ball['x'] = right['x'] - ball['r']
        ball['vx'] = -abs(ball['vx'])
    if ball['x'] + ball['r'] < 0:
        score['right'] += 1
        serve(-1)
    if ball['x'] - ball['r'] > WIDTH:
        score['left'] += 1
        serve(1)


def draw():
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)

    ctx.fill_style = '#4fd1c5'
    for p in (left, right):
        ctx.fill_rect(p['x'], p['y'], p['w'], p['h'])

    ctx.fill_style = 'white'
    ctx.begin_path()
    ctx.arc(ball['x'], ball['y'], ball['r'], 0, math.tau)
    ctx.fill()

    ctx.font = '24px monospace'
    ctx.fill_text(f"{score['left']} : {score['right']}", 210, 36)


def loop(dt):
    update(dt)
    draw()


on_frame(loop)
"""

_PONG_CHECK = r"""
need("left", "Requirement 2: make the left paddle a dict called left: left = {'x': 20, 'y': 130, 'w': 10, 'h': 60, 'speed': 300}")
need("right", "Requirement 2: make the right paddle a dict called right: right = {'x': 450, 'y': 130, 'w': 10, 'h': 60, 'speed': 300}")
need("ball", "Requirement 4: make the ball a dict called ball: ball = {'x': 240, 'y': 160, 'r': 8, 'vx': 220, 'vy': 140}")
need("score", "Requirement 6: keep the points in a dict called score: score = {'left': 0, 'right': 0} (an object with .left and .right works too)")

expect(near(get(g.left, "x"), 20, 0.01) and near(get(g.left, "y"), 130, 0.01) and get(g.left, "w") == 10 and get(g.left, "h") == 60, f"Requirement 2: left starts at x 20, y 130, 10 wide and 60 tall; yours is {show(g.left, 'x', 'y', 'w', 'h')}.")
expect(near(get(g.right, "x"), 450, 0.01) and near(get(g.right, "y"), 130, 0.01) and get(g.right, "w") == 10 and get(g.right, "h") == 60, f"Requirement 2: right starts at x 450, y 130, 10 wide and 60 tall; yours is {show(g.right, 'x', 'y', 'w', 'h')}.")
expect(near(get(g.ball, "x"), 240, 0.01) and near(get(g.ball, "y"), 160, 0.01) and get(g.ball, "r") == 8, f"Requirement 4: the ball starts at x 240, y 160 with r 8; yours is {show(g.ball, 'x', 'y', 'r')}.")
expect(is_num(get(g.ball, "vx")) and abs(get(g.ball, "vx")) > 100 and is_num(get(g.ball, "vy")), "Requirement 4: the ball needs a velocity - 'vx' (about 220) and 'vy' - so that it starts moving.")
expect(get(g.score, "left") == 0 and get(g.score, "right") == 0, "Requirement 6: the points start at 0 for both players: score = {'left': 0, 'right': 0}")

cc.frames(2)
first = cc.rects()
expect(len(first) >= 3 and first[0]["x"] <= 0 and first[0]["y"] <= 0 and first[0]["w"] >= WIDTH and first[0]["h"] >= HEIGHT, "Requirement 1: every frame starts with a dark background over the whole canvas - ctx.fill_rect(0, 0, WIDTH, HEIGHT) - before anything else is drawn (and the loop must be running: on_frame).")


def drawn_box(p):
    return any(near(r["x"], get(p, "x"), 0.01) and near(r["y"], get(p, "y"), 0.01) and r["w"] == get(p, "w") and r["h"] == get(p, "h") for r in cc.rects())


expect(drawn_box(g.left), "Requirement 2: draw the left paddle every frame as a filled rectangle: ctx.fill_rect(left['x'], left['y'], left['w'], left['h']).")
expect(drawn_box(g.right), "Requirement 2: draw the right paddle every frame as a filled rectangle: ctx.fill_rect(right['x'], right['y'], right['w'], right['h']).")
expect(any(near(a["x"], get(g.ball, "x"), 6) and near(a["y"], get(g.ball, "y"), 6) and a["r"] == get(g.ball, "r") for a in cc.arcs()), "Requirement 4: draw the ball every frame as a filled circle: ctx.begin_path(), ctx.arc(ball['x'], ball['y'], ball['r'], 0, math.tau), ctx.fill().")


def put_ball(x, y, vx, vy):
    for k, v in (("x", x), ("y", y), ("vx", vx), ("vy", vy)):
        put(g.ball, k, v)


def hold(key, n, dt=1 / 60):
    cc.press(key)
    cc.frames(n, dt)
    cc.release(key)


def reset():
    put(g.left, "y", 130)
    put(g.right, "y", 130)
    put_ball(240, 160, 0, 0)


def ly():
    return get(g.left, "y")


def ry():
    return get(g.right, "y")


def B(k):
    return get(g.ball, k)


reset()
hold("w", 6, 1 / 30)
expect(near(ly(), 70, 8), f"Requirement 3: holding w for a fifth of a second (at 30 frames a second) moved the left paddle from y 130 to {num(ly())}; at speed 300 it should reach about 70. Move by speed * dt, with dt in seconds, while 'w' in keys.")
expect(near(ry(), 130, 0.01), "Requirement 3: w moved the right paddle too. w and s belong to left only.")
reset()
hold("s", 12)
expect(near(ly(), 190, 8), f"Requirement 3: holding s for a fifth of a second moved the left paddle from y 130 to {num(ly())}; it should reach about 190.")
reset()
hold("ArrowUp", 6, 1 / 30)
expect(near(ry(), 70, 8), f"Requirement 3: holding ArrowUp for a fifth of a second (at 30 frames a second) moved the right paddle from y 130 to {num(ry())}; it should reach about 70.")
expect(near(ly(), 130, 0.01), "Requirement 3: ArrowUp moved the left paddle too. The arrows belong to right only.")
reset()
hold("ArrowDown", 12)
expect(near(ry(), 190, 8), f"Requirement 3: holding ArrowDown for a fifth of a second moved the right paddle from y 130 to {num(ry())}; it should reach about 190.")
reset()
hold("w", 120)
expect(near(ly(), 0, 0.01), f"Requirement 3: after two seconds of w the left paddle is at y {num(ly())}; it should stop with its top on the canvas edge, y 0. Clamp it: max(0, min(HEIGHT - paddle['h'], paddle['y'])).")
hold("s", 120)
expect(near(ly(), HEIGHT - get(g.left, "h"), 0.01), f"Requirement 3: after two seconds of s the left paddle is at y {num(ly())}; it should stop with its bottom on the canvas edge, y {HEIGHT - get(g.left, 'h')}.")
hold("ArrowUp", 120)
expect(near(ry(), 0, 0.01), "Requirement 3: the right paddle should stop at the top edge too (y 0).")
hold("ArrowDown", 120)
expect(near(ry(), HEIGHT - get(g.right, "h"), 0.01), "Requirement 3: the right paddle should stop at the bottom edge too.")

reset()
put_ball(240, 25, 0, -300)
cc.frames(10)
expect(B("vy") > 0, "Requirement 5: the ball hit the top edge and did not turn round. When ball['y'] - ball['r'] goes below 0, send it down.")
expect(B("y") - B("r") >= -0.01, "Requirement 5: after the bounce the ball is still partly above the canvas. Put it back on the edge as well as turning it round.")
put_ball(240, HEIGHT - 25, 0, 300)
cc.frames(10)
expect(B("vy") < 0, "Requirement 5: the ball hit the bottom edge and did not turn round. When ball['y'] + ball['r'] goes past the bottom, send it up.")
put_ball(240, 100, 0, 250)
for i in range(1, 201):
    cc.frames(1)
    expect(B("y") - B("r") >= -0.01 and B("y") + B("r") <= HEIGHT + 0.01, f"Requirement 5: after {i} frames the ball is at y {B('y'):.1f} - partly through the top or bottom. Put it back on the edge as well as turning it round.")
expect(near(abs(B("vy")), 250, 0.5), "Requirement 5: a bounce should change the ball's direction, not its speed.")

reset()
put_ball(get(g.left, "x") + get(g.left, "w") + 30, ly() + get(g.left, "h") / 2, -250, 0)
cc.frames(20)
expect(B("vx") > 0, "Requirement 5: the ball ran straight into the left paddle and kept going. When it reaches the paddle, send it back to the right (vx > 0).")
expect(B("x") - B("r") >= get(g.left, "x") + get(g.left, "w") - 0.5, "Requirement 5: after bouncing off the left paddle the ball is still inside it. Sit it on the paddle's face as well as turning it round, so it cannot flip again next frame.")
reset()
put_ball(get(g.right, "x") - 30, ry() + get(g.right, "h") / 2, 250, 0)
cc.frames(20)
expect(B("vx") < 0, "Requirement 5: the ball ran straight into the right paddle and kept going. When it reaches the paddle, send it back to the left (vx < 0).")
expect(B("x") + B("r") <= get(g.right, "x") + 0.5, "Requirement 5: after bouncing off the right paddle the ball is still inside it.")

reset()
put_ball(155, ly() + get(g.left, "h") / 2, -600, 0)
cc.frames(10, 1 / 30)
expect(B("vx") > 0, "Requirement 5: a fast ball (600 pixels a second, 20 pixels a frame at 30 frames a second) went through the left paddle. Ask whether the ball's circle overlaps the paddle's whole rectangle, not whether the ball's centre happens to be inside it.")
reset()
put_ball(325, ry() + get(g.right, "h") / 2, 600, 0)
cc.frames(10, 1 / 30)
expect(B("vx") < 0, "Requirement 5: a fast ball (600 pixels a second) went through the right paddle. Ask whether the ball's circle overlaps the paddle's whole rectangle, not whether the ball's centre happens to be inside it.")


def total():
    return get(g.score, "left") + get(g.score, "right")


def point(x, vx):
    reset()
    put_ball(x, 20, vx, 0)
    before = total()
    for _ in range(90):
        if total() != before:
            break
        cc.frames(1)
    return before


before = point(60, -300)
expect(total() == before + 1, f"Requirement 5/6: a ball sent along the top, well clear of the paddle, should miss it and give a point; the points added are {total() - before}. A paddle only stops the ball where the paddle actually is.")
expect(get(g.score, "right") == 1 and get(g.score, "left") == 0, f"Requirement 6: the ball went off the LEFT edge, so the right player scores: right 1, left 0. Yours is left {get(g.score, 'left')}, right {get(g.score, 'right')}.")
expect(near(B("x"), 240, 6) and near(B("y"), 160, 6), f"Requirement 7: after a point the ball is served from the centre (x 240, y 160); it is at x {num(B('x'))}, y {num(B('y'))}.")
expect(B("vx") < -100, "Requirement 7: after the left player loses a point, the ball is served towards the left player (vx negative, about -220).")
cc.frames(10)
expect(total() == before + 1, "Requirement 6: one miss should be one point. Is the ball still off the edge after the point, scoring again every frame?")
before = point(420, 300)
expect(get(g.score, "left") == 1 and get(g.score, "right") == 1, f"Requirement 6: the ball went off the RIGHT edge, so the left player scores. Yours is left {get(g.score, 'left')}, right {get(g.score, 'right')}.")
expect(near(B("x"), 240, 6) and near(B("y"), 160, 6), "Requirement 7: after a point on the right the ball is served from the centre too.")
expect(B("vx") > 100, "Requirement 7: after the right player loses a point, the ball is served towards the right player (vx positive, about 220).")
before = point(420, 300)
expect(get(g.score, "left") == 2, "Requirement 6: a second point on the right edge should make it left 2.")
before = point(60, -300)
expect(get(g.score, "right") == 2 and get(g.score, "left") == 2, "Requirement 6: the score should add up from point to point - left 2, right 2 now.")

reset()
put(g.score, "left", 3)
put(g.score, "right", 7)
cc.frames(1)
words = " ".join(cc.texts())
expect("3" in words and "7" in words, f"Requirement 6: draw both scores as text every frame - with 3 and 7 it should show both numbers; the text on screen is '{words}'.")

put(g.score, "left", 3)
put(g.score, "right", 7)
put(g.left, "y", 0)
put(g.right, "y", 260)
put_ball(100, 50, 0, 0)
cc.press("r")
cc.frames(1)
cc.release("r")
expect(get(g.score, "left") == 0 and get(g.score, "right") == 0, "Requirement 8: pressing r should start a new match with both scores back at 0.")
expect(near(ly(), 130, 0.01) and near(ry(), 130, 0.01), "Requirement 8: pressing r should put both paddles back at y 130.")
expect(near(B("x"), 240, 6) and near(B("y"), 160, 6), "Requirement 8: pressing r should serve the ball from the centre.")
"""

# ── 2. A Flappy-style gap game ───────────────────────────────────────────

_FLAPPY = """import math
import random
from dataclasses import dataclass

from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down

bird = {'x': 100, 'y': 160, 'r': 12, 'vy': 0}
pipes = []
spawn_timer = 0
score = 0
state = 'playing'


@dataclass
class Pipe:
    x: float
    gap_y: float
    w: int = 50
    gap_h: int = 110
    passed: bool = False


def restart():
    global pipes, spawn_timer, score, state
    bird['y'], bird['vy'] = 160, 0
    pipes = []
    spawn_timer = 0
    score = 0
    state = 'playing'


def key_down(key):
    if key != ' ':
        return
    if state == 'playing':
        bird['vy'] = -300
    else:
        restart()


on_key_down(key_down)


def touches(x, y, w, h):
    nearest_x = max(x, min(bird['x'], x + w))
    nearest_y = max(y, min(bird['y'], y + h))
    return math.dist((bird['x'], bird['y']), (nearest_x, nearest_y)) < bird['r']


def update(dt):
    global pipes, spawn_timer, score, state
    if state != 'playing':
        return
    bird['vy'] += 900 * dt
    bird['y'] += bird['vy'] * dt
    if bird['y'] - bird['r'] < 0 or bird['y'] + bird['r'] > HEIGHT:
        state = 'over'

    spawn_timer += dt
    if spawn_timer >= 1.5:
        spawn_timer -= 1.5
        pipes.append(Pipe(WIDTH, random.uniform(30, 180)))
    for p in pipes:
        p.x -= 150 * dt
        if not p.passed and p.x + p.w < bird['x']:
            p.passed = True
            score += 1
    pipes = [p for p in pipes if p.x + p.w > 0]
    if any(touches(p.x, 0, p.w, p.gap_y) or touches(p.x, p.gap_y + p.gap_h, p.w, HEIGHT) for p in pipes):
        state = 'over'


def draw():
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)

    ctx.fill_style = '#68d391'
    for p in pipes:
        ctx.fill_rect(p.x, 0, p.w, p.gap_y)
        ctx.fill_rect(p.x, p.gap_y + p.gap_h, p.w, HEIGHT - p.gap_y - p.gap_h)

    ctx.fill_style = '#f6e05e'
    ctx.begin_path()
    ctx.arc(bird['x'], bird['y'], bird['r'], 0, math.tau)
    ctx.fill()

    ctx.fill_style = 'white'
    ctx.font = '20px monospace'
    ctx.fill_text(f'Score: {score}', 10, 26)
    if state == 'over':
        ctx.font = '32px monospace'
        ctx.fill_text('Game over', 150, 150)
        ctx.font = '16px monospace'
        ctx.fill_text('Press Space to play again', 140, 180)


def loop(dt):
    update(dt)
    draw()


on_frame(loop)
"""

_FLAPPY_CHECK = r"""
import re

need("bird", "Requirement 2: make the bird a dict called bird: bird = {'x': 100, 'y': 160, 'r': 12, 'vy': 0}")
need("pipes", "Requirement 4: keep the pipes in a list called pipes, empty at the start: pipes = []")
need("score", "Requirement 5: keep the score in a variable: score = 0")
need("state", "Requirement 6: keep what the game is doing in a variable: state = 'playing'")

expect(near(get(g.bird, "x"), 100, 0.01) and near(get(g.bird, "y"), 160, 0.01) and get(g.bird, "r") == 12 and get(g.bird, "vy") == 0, f"Requirement 2: the bird starts as x 100, y 160, r 12, vy 0; yours is {show(g.bird, 'x', 'y', 'r', 'vy')}.")
expect(isinstance(g.pipes, list) and len(g.pipes) == 0, "Requirement 4: keep the pipes in a list called pipes, empty at the start (the first pipe comes after 1.5 seconds).")
expect(is_num(g.score) and g.score == 0, "Requirement 5: the score starts at 0: score = 0")
expect(g.state == "playing", "Requirement 6: the game starts with state = 'playing'")

cc.frames(2)
first = cc.rects()
expect(len(first) >= 1 and first[0]["x"] <= 0 and first[0]["y"] <= 0 and first[0]["w"] >= WIDTH and first[0]["h"] >= HEIGHT, "Requirement 1: every frame starts with a dark background over the whole canvas - ctx.fill_rect(0, 0, WIDTH, HEIGHT) (and the loop must be running: on_frame).")
expect(any(near(a["x"], get(g.bird, "x"), 6) and near(a["y"], get(g.bird, "y"), 6) and a["r"] == get(g.bird, "r") for a in cc.arcs()), "Requirement 2: draw the bird every frame as a filled circle: ctx.begin_path(), ctx.arc(bird['x'], bird['y'], bird['r'], 0, math.tau), ctx.fill().")


def bird_set(y, vy=0):
    put(g.bird, "y", y)
    put(g.bird, "vy", vy)


def by():
    return get(g.bird, "y")


S30 = 1 / 30

# Gravity and the flap, at 30 frames a second so that dt matters.
bird_set(160)
cc.frames(15, S30)
fell = by() - 160
expect(near(fell, 112, 14), f"Requirement 2: in half a second of falling from y 160 the bird moved {num(fell)} pixels down; gravity of 900 pixels a second, a second should make it about 112. Add 900 * dt to vy, and vy * dt to y - dt is in seconds, so not a fixed amount a frame.")
falling = by()
cc.press(" ")
cc.frames(1)
cc.release(" ")
vy = get(g.bird, "vy")
expect(-330 < vy < -250, f"Requirement 3: a flap should SET vy to -300 (the bird was falling fast, so adding to it is not enough); one frame after the flap vy is {num(vy)}.")
cc.frames(4)
expect(by() < falling, "Requirement 3: after a flap the bird should rise.")


# Pipes: fly through the middle of every gap for 15 seconds, at 30 frames a second.
def fly(n, dt=1 / 60):
    for _ in range(n):
        bx, br = get(g.bird, "x"), get(g.bird, "r")
        p = next((q for q in g.pipes if get(q, "x") + get(q, "w", 50) > bx - br - 2), None)
        if p is None:
            bird_set(160)
        else:
            expect(is_num(get(p, "gap_y")) and is_num(get(p, "gap_h")) and is_num(get(p, "x")), "Requirement 4: each pipe needs 'x', 'w', 'gap_y' (the top of the gap) and 'gap_h' (its height) - as dict keys or attributes.")
            bird_set(get(p, "gap_y") + get(p, "gap_h") / 2)
        cc.frames(1, dt)


bird_set(160)
seen = {}
prev_x = {}
last_score = g.score
while cc.time < 15:
    fly(1, S30)
    expect(g.state == "playing", f"Requirement 6: the game ended at {cc.time:.1f} seconds although the bird was flown through the middle of every gap. The bird should only die by touching a pipe, the floor or the ceiling - and only a pipe that is really at the bird.")
    for q in g.pipes:
        if id(q) in prev_x:
            moved = prev_x[id(q)] - get(q, "x")
            expect(near(moved, 5, 0.6), f"Requirement 4: a pipe moved {moved:.1f} pixels in one frame at 30 frames a second; at 150 pixels a second it should move 5. Move by 150 * dt, with dt in seconds - not a fixed amount a frame.")
        prev_x[id(q)] = get(q, "x")
        if id(q) not in seen:
            seen[id(q)] = (cc.time, get(q, "x"), q)
    expect(g.score - last_score <= 1, f"Requirement 5: the score jumped by {g.score - last_score} in a single frame. Count each pipe once - remember which pipes the bird has already passed.")
    last_score = g.score
born = sorted(seen.values(), key=lambda t: t[0])
expect(len(born) >= 8, f"Requirement 4: {len(born)} pipes appeared in 15 seconds; one every 1.5 seconds makes about 9. Add dt to a timer and, at 1.5, take 1.5 off and append a new pipe (or every(1.5, fn) - game seconds, not frames).")
expect(near(born[0][0], 1.5, 0.07), f"Requirement 4: the first pipe appeared at {born[0][0] * 1000:.0f} ms; it should come after 1.5 seconds - in seconds, not in frames.")
for i in range(1, len(born)):
    gap = born[i][0] - born[i - 1][0]
    expect(near(gap, 1.5, 0.04), f"Requirement 4: pipes should arrive every 1.5 seconds; pipe {i + 1} came {gap * 1000:.0f} ms after the one before.")
expect(all(near(b[1], WIDTH, 6) for b in born), "Requirement 4: a new pipe starts at the right edge of the canvas, x = WIDTH.")
pipe_objs = [b[2] for b in born]
expect(all(get(p, "w") == 50 and get(p, "gap_h") == 110 for p in pipe_objs), "Requirement 4: every pipe is 50 wide with a gap 110 tall: w 50, gap_h 110.")
expect(all(29.99 <= get(p, "gap_y") <= 180.01 for p in pipe_objs), "Requirement 4: the top of the gap, gap_y, should be between 30 and 180, so the gap is always fully on the canvas: random.uniform(30, 180).")
expect(len({round(get(p, "gap_y")) for p in pipe_objs}) >= 4, "Requirement 4: the gaps should be at random heights - random.uniform - not all in the same place.")
expect(len(g.pipes) <= 5, f"Requirement 4: there are {len(g.pipes)} pipes in the list, some long gone off the left edge. Take them out of the list once they have left the canvas: pipes = [p for p in pipes if ...] (with global pipes).")
expect(7 <= g.score <= 8, f"Requirement 5: the bird flew through about 8 pipes and the score is {g.score}. Add 1 once for each pipe the bird gets past.")
tail = g.pipes[-1]
tail_x = get(tail, "x")
fly(15, S30)
expect(near(tail_x - get(tail, "x"), 75, 6), f"Requirement 4: in half a second (at 30 frames a second) a pipe moved {num(tail_x - get(tail, 'x'))} pixels left; at 150 pixels a second it should be 75. Move by 150 * dt.")
tail_x = get(tail, "x")
fly(30, 1 / 60)
expect(near(tail_x - get(tail, "x"), 75, 6), f"Requirement 4: in half a second (at 60 frames a second) a pipe moved {num(tail_x - get(tail, 'x'))} pixels left; it should be 75.")
expect(g.state == "playing", "Requirement 6: the game should still be going.")
fly(1)
expect(any(str(g.score) in t for t in cc.texts()), f"Requirement 5: draw the score as text every frame (ctx.fill_text and an f-string) - it should show {g.score} now.")
shown = next((p for p in g.pipes if get(p, "x") > 0 and get(p, "x") + get(p, "w") < WIDTH), None)
expect(shown is not None, "Requirement 4: there should be a pipe on the canvas to look at.")
rs = cc.rects()
expect(any(near(r["x"], get(shown, "x"), 0.01) and r["y"] == 0 and r["w"] == get(shown, "w") and near(r["h"], get(shown, "gap_y"), 0.01) for r in rs), "Requirement 4: draw the top half of each pipe: x, 0, w, gap_y.")
expect(any(near(r["x"], get(shown, "x"), 0.01) and near(r["y"], get(shown, "gap_y") + get(shown, "gap_h"), 0.01) and r["y"] + r["h"] >= HEIGHT - 0.01 for r in rs), "Requirement 4: draw the bottom half of each pipe: from gap_y + gap_h down to the bottom of the canvas.")

# Hitting things. One of the pipes the program made is moved about, so it is
# whatever the program makes pipes of (a dict, a dataclass).
proto = shown
bx, br = get(g.bird, "x"), get(g.bird, "r")


def set_pipe(x, gap_y):
    put(proto, "x", x)
    put(proto, "gap_y", gap_y)
    if get(proto, "passed") is not None:
        put(proto, "passed", False)
    g.pipes[:] = [proto]


def again():
    cc.press(" ")
    cc.frames(1)
    cc.release(" ")


set_pipe(bx + 120, 200)
bird_set(100)
cc.frames(2)
expect(g.state == "playing", "Requirement 6: the game ended while the nearest pipe was still 120 pixels away. A pipe only counts when it overlaps the bird across as well as up and down.")
set_pipe(bx - 200, 200)
bird_set(100)
cc.frames(2)
expect(g.state == "playing", "Requirement 6: the game ended because of a pipe that is already behind the bird. A pipe behind the bird is harmless.")
set_pipe(bx - 25, 200)
bird_set(255)
cc.frames(2)
expect(g.state == "playing", "Requirement 6: the bird is in the middle of the gap, and the game ended. Inside the gap it is safe.")
for y in (200 + br + 3, 310 - br - 3):
    set_pipe(bx - 25, 200)
    bird_set(y)
    cc.frames(2)
    expect(g.state == "playing", f"Requirement 6: the bird (a circle of radius {br}) is squeezing through the gap at y {num(y)} without touching either pipe half, and the game ended. Touching means the circle overlaps the box.")
set_pipe(bx + br + 8, 100)
bird_set(50)
cc.frames(2)
expect(g.state == "playing", "Requirement 6: the pipe is still 8 pixels ahead of the bird's edge and the game ended. It is only a hit when the bird overlaps the pipe.")
set_pipe(bx + 5, 100)
bird_set(50)
cc.frames(2)
expect(g.state == "over", "Requirement 6: the bird's edge is inside the front of the top half of a pipe (the bird's centre is just before it) and the game carried on. The bird is a circle: it hits as soon as the circle overlaps the pipe, not only when its centre is inside it.")
again()
expect(g.state == "playing", "Requirement 7: Space should start a new game each time the game is over.")
set_pipe(bx - 25, 200)
bird_set(100)
cc.frames(2)
expect(g.state == "over", "Requirement 6: the bird is inside the top half of a pipe and the game carried on. Touching a pipe ends the game: state = 'over'.")
expect(any(re.search("game over", t, re.I) for t in cc.texts()), "Requirement 6: when the game is over, put 'Game over' on the screen.")
over_y = by()
over_x = [get(p, "x") for p in g.pipes]
over_score = g.score
cc.frames(30)
expect(near(by(), over_y, 0.01) and [get(p, "x") for p in g.pipes] == over_x and g.score == over_score, "Requirement 6: once the game is over nothing should move - the bird, the pipes and the score all stay where they were. Start update with: if state != 'playing': return")
cc.press(" ")
cc.frames(1)
cc.release(" ")
expect(g.state == "playing", "Requirement 7: pressing Space after a game over should start again: state back to 'playing'. (If it ended again at once, is the pipe that ended the game still there? A new game starts with no pipes.)")
expect(near(by(), 160, 2.5), f"Requirement 7: a new game starts with the bird back at y 160 (and the Space that restarts it must not also flap); the bird is at y {num(by())}.")
expect(abs(get(g.bird, "vy")) < 40, f"Requirement 7: a new game starts with the bird at rest (vy 0); its vy is {num(get(g.bird, 'vy'))}.")
expect(len(g.pipes) == 0, "Requirement 7: a new game starts with no pipes - empty the list, or the one that ended the last game ends this one too.")
expect(g.score == 0, f"Requirement 7: a new game starts with the score back at 0; it is {g.score}.")
expect(not any(re.search("game over", t, re.I) for t in cc.texts()), "Requirement 7: 'Game over' is still on the screen after restarting.")

set_pipe(bx - 25, 100)
bird_set(250)
cc.frames(2)
expect(g.state == "over", "Requirement 6: the bird is inside the bottom half of a pipe and the game carried on.")
again()
set_pipe(bx - 25, 100)
bird_set(205)
cc.frames(2)
expect(g.state == "over", "Requirement 6: the bird's centre is in the gap, but 5 pixels above the bottom half and the bird is 12 across (r 12): it overlaps the pipe and the game carried on. The bird is a circle, not a point.")
again()
set_pipe(bx - 25, 100)
bird_set(105)
cc.frames(2)
expect(g.state == "over", "Requirement 6: the bird's centre is in the gap, but 5 pixels below the top half, so the bird overlaps the pipe and the game carried on.")
again()
bird_set(HEIGHT - 5)
cc.frames(2)
expect(g.state == "over", "Requirement 6: touching the floor ends the game too.")
again()
bird_set(5)
cc.frames(2)
expect(g.state == "over", "Requirement 6: touching the ceiling ends the game too.")
again()
expect(g.state == "playing", "Requirement 7: Space should start a new game each time the game is over.")
"""

# ── 3. Memory cards ──────────────────────────────────────────────────────

_MEMORY = """import random
from dataclasses import dataclass

from canvas import ctx, WIDTH, HEIGHT, on_frame, on_click, after


@dataclass
class Card:
    x: float
    y: float
    value: int
    w: int = 90
    h: int = 80
    face_up: bool = False
    matched: bool = False


values = [v for v in range(6) for _ in range(2)]
random.shuffle(values)

cards = []
for i, value in enumerate(values):
    row, col = divmod(i, 4)
    cards.append(Card(30 + col * 110, 20 + row * 100, value))

first = None
locked = False
state = 'playing'


def hide(a, b):
    global locked
    a.face_up = b.face_up = False
    locked = False


def click(x, y):
    global first, locked, state
    if locked or state != 'playing':
        return
    card = next((c for c in cards if not c.face_up and c.x <= x < c.x + c.w and c.y <= y < c.y + c.h), None)
    if card is None:
        return
    card.face_up = True
    if first is None:
        first = card
        return
    a, first = first, None
    if a.value == card.value:
        a.matched = card.matched = True
        if all(c.matched for c in cards):
            state = 'won'
    else:
        locked = True
        after(0.8, lambda: hide(a, card))


on_click(click)


def draw(dt):
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)
    ctx.font = '36px monospace'
    for c in cards:
        ctx.fill_style = '#f6e05e' if c.face_up else '#2d3a5a'
        ctx.fill_rect(c.x, c.y, c.w, c.h)
        if c.face_up:
            ctx.fill_style = '#10141f'
            ctx.fill_text(f'{c.value}', c.x + 36, c.y + 52)
    if state == 'won':
        ctx.fill_style = 'white'
        ctx.font = '32px monospace'
        ctx.fill_text('You win!', 170, 316)


on_frame(draw)
"""

_MEMORY_CHECK = r"""
import re

need("cards", "Requirement 1: make a list called cards with 12 cards in it, in a grid of 4 columns by 3 rows.")
need("state", "Requirement 6: keep what the game is doing in a variable: state = 'playing'")
expect(isinstance(g.cards, list) and len(g.cards) == 12, "Requirement 1: make a list called cards with 12 cards in it, in a grid of 4 columns by 3 rows.")
expect(len({id(c) for c in g.cards}) == 12, "Requirement 1: the 12 cards must be 12 different cards. [card] * 12 (or [Card(...)] * 12) is ONE card listed twelve times - turn one over and all twelve turn. Build them one at a time, in a loop or a comprehension.")
want = {(30 + col * 110, 20 + row * 100) for row in range(3) for col in range(4)}
got = {(get(c, "x"), get(c, "y")) for c in g.cards}
expect(got == want, "Requirement 1: the cards make a grid: x = 30 + col * 110 and y = 20 + row * 100, for columns 0 to 3 and rows 0 to 2 - each card has its own 'x' and 'y'.")
expect(all(get(c, "w") == 90 and get(c, "h") == 80 for c in g.cards), "Requirement 1: every card is 90 wide and 80 tall ('w': 90, 'h': 80).")
expect(all(get(c, "face_up") is False and get(c, "matched") is False for c in g.cards), "Requirement 1: every card starts face down and unmatched: 'face_up': False, 'matched': False.")
counts = {}
for c in g.cards:
    counts[get(c, "value")] = counts.get(get(c, "value"), 0) + 1
expect(counts == {v: 2 for v in range(6)}, "Requirement 2: each card has a 'value', and the values 0 to 5 each appear on exactly two cards - 6 pairs.")
order = [get(c, "value") for c in sorted(g.cards, key=lambda c: (get(c, "y"), get(c, "x")))]
expect(order != [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5] and order != [0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5], "Requirement 2: the values should be shuffled - the cards are dealt in order. random.shuffle(values) mixes a list in place.")
expect(g.state == "playing", "Requirement 6: the game starts with state = 'playing'")

S = 1 / 30


def tap(c):
    cc.click(get(c, "x") + get(c, "w") / 2, get(c, "y") + get(c, "h") / 2)


def up():
    return sum(1 for c in g.cards if get(c, "face_up"))


def labels():
    return [t.strip() for t in cc.texts()]


def fill_of(c):
    hits = [r for r in cc.rects() if r["x"] == get(c, "x") and r["y"] == get(c, "y") and r["w"] == get(c, "w") and r["h"] == get(c, "h")]
    return hits[-1]["fill"] if hits else None


cc.frames(2)
first = cc.rects()
expect(len(first) >= 13, "Requirement 3: every frame, draw a dark background and then each card as a rectangle - 13 rectangles in all (and the loop must be running: on_frame).")
expect(all(fill_of(c) is not None for c in g.cards), "Requirement 3: draw every card each frame as a rectangle at its own x, y, w and h.")
for v in range(6):
    expect(str(v) not in labels(), "Requirement 3: a face-down card must not show its value. Write the value only for cards whose face_up is True.")

cc.click(125, 60)
cc.click(5, 5)
cc.click(470, 310)
cc.frames(1)
expect(up() == 0, "Requirement 4: a click in the gap between cards, or outside the grid, should do nothing. (on_click(fn) gives fn(x, y) in canvas pixels already.)")

by_value = {}
for c in g.cards:
    by_value.setdefault(get(c, "value"), []).append(c)
pairs = [by_value[v] for v in range(6)]
a = pairs[0][0]
b = pairs[1][0]
other = pairs[2][0]

# Anywhere on a card turns it over, not just the middle.
corner_card = pairs[3][0]
cc.click(get(corner_card, "x") + 1, get(corner_card, "y") + 1)
expect(get(corner_card, "face_up") is True, "Requirement 4: a click anywhere on a face-down card turns it over - its top-left corner too: x <= click_x < x + w and y <= click_y < y + h.")
cc.click(get(corner_card, "x") + get(corner_card, "w") - 1, get(corner_card, "y") + get(corner_card, "h") - 1)
expect(up() == 1 and get(corner_card, "face_up") is True and not get(corner_card, "matched"), "Requirement 4: a click on the same card's bottom-right corner is a click on a card that is already face up: it does nothing - it must not count as the second card (a card does not match itself).")
cc.click(get(corner_card, "x") - 1, get(corner_card, "y") - 1)
expect(up() == 1, "Requirement 4: a click 1 pixel outside a card is in the gap and does nothing.")
# Turn it back for the rest: a lone face-up card is "first"; hold on to it by finishing a pair.
partner = pairs[3][1]
tap(partner)
cc.frames(1)
expect(get(corner_card, "matched") and get(partner, "matched"), "Requirement 5: the pair is two cards with the same value: both get matched True.")
expect(get(corner_card, "face_up") and get(partner, "face_up"), "Requirement 5: matched cards stay face up.")
expect(g.state == "playing", "Requirement 6: one pair found does not win - the game is won only when every card is matched.")

tap(a)
cc.frames(1)
expect(get(a, "face_up") is True, "Requirement 4: clicking the middle of a face-down card should turn it face up - set its face_up to True.")
expect(up() == 3, "Requirement 4: one click should turn over exactly one card.")
expect(str(get(a, "value")) in labels(), "Requirement 3: a face-up card shows its value - write it on the card with ctx.fill_text.")
expect(fill_of(a) != fill_of(other), "Requirement 3: a face-up card should be drawn in a different colour from a face-down one.")
tap(a)
cc.frames(1)
expect(get(a, "face_up") is True and get(a, "matched") is False and up() == 3, "Requirement 4: clicking a card that is already face up does nothing - it must not turn it back over or count as the second card (a card does not match itself).")

tap(b)
cc.frames(1, S)
expect(get(a, "face_up") and get(b, "face_up"), "Requirement 5: two different cards are showing, so both should stay face up for a moment so the player can see them.")
expect(not get(a, "matched") and not get(b, "matched"), "Requirement 5: cards with different values must not be matched.")
cc.frames(6, S)
tap(other)
cc.frames(12, S)
expect(get(a, "face_up") and get(b, "face_up"), "Requirement 5: the two different cards flipped back before 800 ms had passed (about 0.6 seconds went by at 30 frames a second). Leave them face up for 0.8 seconds - after(0.8, fn) counts in seconds; counting frames is right at 60 a second and wrong at 30.")
expect(not get(other, "face_up"), "Requirement 5: while two different cards are showing, clicks should do nothing - a third card turned over.")
cc.frames(12, S)
expect(not get(a, "face_up") and not get(b, "face_up"), "Requirement 5: after 800 ms the two different cards should flip back face down - by the clock, so also at 30 frames a second: after(0.8, fn).")
expect(up() == 2 and not get(a, "matched") and not get(b, "matched"), "Requirement 5: after a mismatch, nothing should be left face up or matched (only the pair found earlier is).")
tap(a)
cc.frames(1)
expect(get(a, "face_up") is True, "Requirement 5: once the two cards have flipped back, the next click must turn a card over again. Is something still locked?")
tap(pairs[0][1])
cc.frames(1)
expect(get(a, "matched") is True and get(pairs[0][1], "matched") is True, "Requirement 5: two cards with the same value are a match - set matched to True on both.")
expect(get(a, "face_up") and get(pairs[0][1], "face_up"), "Requirement 5: matched cards stay face up.")
expect(g.state == "playing", "Requirement 6: one pair found does not win - the game is won only when every card is matched.")
cc.frames(80, S)
expect(get(a, "face_up") and get(pairs[0][1], "face_up") and up() == 4, "Requirement 5: matched cards must stay face up for good, not flip back.")
tap(pairs[1][0])
cc.frames(1)
expect(get(pairs[1][0], "face_up"), "Requirement 5: after a match the player can go straight on - the next click should turn a card over.")
tap(a)
cc.frames(1)
expect(get(a, "face_up") and up() == 5, "Requirement 4: clicking a card that is already matched does nothing.")
tap(pairs[1][1])
cc.frames(1)
expect(get(pairs[1][0], "matched") and get(pairs[1][1], "matched"), "Requirement 5: the second pair should match too - a click on a matched card must not count as a pick.")
for pair in (pairs[2], pairs[4]):
    for c in pair:
        tap(c)
cc.frames(1)
done = sum(1 for c in g.cards if get(c, "matched"))
expect(done == 10, f"Requirement 5: five pairs should be matched now; {done // 2} are.")
expect(g.state == "playing", "Requirement 6: one pair is still hidden, so the game is not won yet.")
expect(not any(re.search("win", t, re.I) for t in cc.texts()), "Requirement 6: do not say 'You win!' until the last pair is found.")
tap(pairs[5][0])
tap(pairs[5][1])
cc.frames(1)
expect(g.state == "won", f"Requirement 6: with every card matched the game is won; state is '{g.state}'. Use all(card matched for every card).")
expect(any(re.search("you win", t, re.I) for t in cc.texts()), "Requirement 6: put 'You win!' on the screen when the game is won.")
"""

# ── 4. A falling-blocks stacker ─────────────────────────────────────────

_STACKER = """from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down, every

COLS, ROWS, CELL, LEFT = 10, 20, 16, 160
SHAPE = [(0, 0), (1, 0), (0, 1), (1, 1)]


def empty_rows(n):
    return [[0] * COLS for _ in range(n)]


grid = empty_rows(ROWS)
piece = {'col': 4, 'row': 0}
score = 0
state = 'playing'


def fits(col, row):
    return all(
        0 <= col + dc < COLS and row + dr < ROWS and not grid[row + dr][col + dc]
        for dc, dr in SHAPE
    )


def spawn():
    global state
    piece['col'], piece['row'] = 4, 0
    if not fits(4, 0):
        state = 'over'


def clear_lines():
    global grid, score
    kept = [row for row in grid if not all(row)]
    cleared = ROWS - len(kept)
    grid = empty_rows(cleared) + kept
    score += 10 * cleared


def lock():
    for dc, dr in SHAPE:
        grid[piece['row'] + dr][piece['col'] + dc] = 1
    clear_lines()
    spawn()


def step_down():
    if fits(piece['col'], piece['row'] + 1):
        piece['row'] += 1
    else:
        lock()


def gravity():
    if state == 'playing':
        step_down()


every(0.5, gravity)


def restart():
    global grid, score, state
    grid = empty_rows(ROWS)
    score = 0
    state = 'playing'
    piece['col'], piece['row'] = 4, 0


def key_down(key):
    if state == 'over':
        if key == 'Enter':
            restart()
        return
    if key == 'ArrowLeft' and fits(piece['col'] - 1, piece['row']):
        piece['col'] -= 1
    elif key == 'ArrowRight' and fits(piece['col'] + 1, piece['row']):
        piece['col'] += 1
    elif key == 'ArrowDown':
        while fits(piece['col'], piece['row'] + 1):
            piece['row'] += 1
        lock()


on_key_down(key_down)


def draw_cell(col, row):
    ctx.fill_rect(LEFT + col * CELL, row * CELL, CELL - 1, CELL - 1)


def draw(dt):
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)
    ctx.fill_style = '#1a2236'
    ctx.fill_rect(LEFT, 0, COLS * CELL, ROWS * CELL)

    ctx.fill_style = '#f6ad55'
    for r, row in enumerate(grid):
        for c, filled in enumerate(row):
            if filled:
                draw_cell(c, r)

    ctx.fill_style = '#4fd1c5'
    for dc, dr in SHAPE:
        draw_cell(piece['col'] + dc, piece['row'] + dr)

    ctx.fill_style = 'white'
    ctx.font = '16px monospace'
    ctx.fill_text(f'Score: {score}', 10, 22)
    if state == 'over':
        ctx.font = '24px monospace'
        ctx.fill_text('Game over', 190, 150)
        ctx.font = '12px monospace'
        ctx.fill_text('Press Enter to play again', 180, 175)


on_frame(draw)
"""

_STACKER_CHECK = r"""
import re

need("grid", "Requirement 1: make grid, a list of 20 rows each holding 10 cells, read as grid[row][col]: grid = [[0] * 10 for _ in range(20)]")
need("piece", "Requirement 2: keep the falling piece in piece = {'col': 4, 'row': 0}, its top-left cell (an object with .col and .row works too).")
need("score", "Requirement 7: keep the score in a variable: score = 0")
need("state", "Requirement 8: keep what the game is doing in a variable: state = 'playing'")

expect(isinstance(g.grid, list) and len(g.grid) == 20 and all(isinstance(r, list) and len(r) == 10 for r in g.grid), "Requirement 1: make grid, a list of 20 rows each holding 10 cells, read as grid[row][col]: grid = [[0] * 10 for _ in range(20)]")
expect(len({id(r) for r in g.grid}) == 20, "Requirement 1: the 20 rows of grid are the SAME list repeated - [[0] * 10] * 20 copies the reference to one row, not the row, so filling a cell in one row fills it in every row. Build the rows one at a time: [[0] * 10 for _ in range(20)].")
expect(all(not v for r in g.grid for v in r), "Requirement 1: the grid starts empty - every cell 0.")
expect(get(g.piece, "col") == 4 and get(g.piece, "row") == 0, "Requirement 2: the falling piece starts at col 4, row 0: piece = {'col': 4, 'row': 0}")
expect(is_num(g.score) and g.score == 0, "Requirement 7: the score starts at 0: score = 0")
expect(g.state == "playing", "Requirement 8: the game starts with state = 'playing'")


def cells():
    return [[1 if v else 0 for v in r] for r in g.grid]


def total():
    return sum(sum(r) for r in cells())


def clear_grid():
    for r in g.grid:
        r[:] = [0] * len(r)


def pc():
    return get(g.piece, "col")


def pr():
    return get(g.piece, "row")


def place(col, row):
    put(g.piece, "col", col)
    put(g.piece, "row", row)


def tap(key, frames=1):
    cc.press(key)
    cc.frames(frames)
    cc.release(key)


def drop(col, row=0):
    place(col, row)
    tap("ArrowDown", 2)


# Gravity: one row every half second.
cc.frames(28)
expect(pr() == 0, f"Requirement 3: after 0.47 seconds the piece is on row {pr()}; it should still be on row 0 - it moves down one row every 0.5 seconds.")
cc.frames(5)
expect(pr() == 1, f"Requirement 3: after 0.55 seconds the piece should be on row 1; it is on row {pr()}. Add dt to a timer, and every 0.5 seconds take 0.5 off it and move down one row - or every(0.5, fn).")
cc.frames(30)
expect(pr() == 2, f"Requirement 3: after 1.05 seconds the piece should be on row 2; it is on row {pr()}.")
row_before = pr()
cc.frames(15, 1 / 30)
expect(pr() == row_before + 1, f"Requirement 3: half a second at 30 frames a second should move the piece down exactly one row (from {row_before}); it is on row {pr()}. Count seconds, not frames.")

# Left and right: one column for each key PRESS.
place(4, 2)
tap("ArrowLeft")
expect(pc() == 3, f"Requirement 4: one press of ArrowLeft should move the piece one column left, from 4 to 3; it is at {pc()}.")
tap("ArrowRight")
expect(pc() == 4, f"Requirement 4: one press of ArrowRight should move the piece one column right; it is at {pc()}.")
cc.press("ArrowLeft")
cc.frames(10)
cc.release("ArrowLeft")
expect(pc() == 3, f"Requirement 4: holding ArrowLeft down for a sixth of a second moved the piece from col 4 to col {pc()}; one key PRESS is one column. Use on_key_down(fn), which runs once as the key goes down - `'ArrowLeft' in keys` is true on every frame the key is held.")
place(4, 2)
for _ in range(7):
    tap("ArrowLeft")
expect(pc() == 0, f"Requirement 4: the piece should stop at the left wall, col 0; after 7 presses it is at col {pc()}.")
for _ in range(12):
    tap("ArrowRight")
expect(pc() == 8, f"Requirement 4: the piece is 2 cells wide, so the right wall stops it at col 8; after 12 presses it is at col {pc()}.")
place(4, 2)
for r in range(20):
    g.grid[r][6] = 1
tap("ArrowRight")
expect(pc() == 4, "Requirement 4: the piece should not move into a filled cell - there is a wall of filled cells just to its right and it went through.")
tap("ArrowLeft")
expect(pc() == 3, "Requirement 4: moving the other way, where nothing is in the way, should still work.")
clear_grid()

# Drop and lock.
drop(4)
expect(all(g.grid[r][c] for r in (18, 19) for c in (4, 5)), f"Requirement 5/6: ArrowDown should drop the piece all the way down and lock it into the grid: cells (row 18, 19) x (col 4, 5) should be 1. Rows 18 and 19 are {cells()[18]} and {cells()[19]}. (Or was the new row cleared at once? A row is cleared only when ALL ten of its cells are filled.)")
expect(total() == 4, f"Requirement 6: a piece locks as exactly 4 filled cells; the grid has {total()}.")
expect(pc() == 4 and pr() <= 1, f"Requirement 6: after locking, a new piece starts at col 4, row 0; it is at col {pc()}, row {pr()}.")
expect(g.state == "playing", "Requirement 6: nothing is wrong yet - the game should still be playing.")
drop(4)
expect(all(g.grid[r][c] for r in (16, 17) for c in (4, 5)) and total() == 8, f"Requirement 6: the second piece should land ON the first one, in rows 16 and 17, not fall through it. The grid holds {total()} filled cells.")
clear_grid()

# A piece comes to rest on the floor by gravity alone, and locks there.
place(0, 18)
cc.frames(40)
expect(all(g.grid[r][c] for r in (18, 19) for c in (0, 1)) and total() == 4, f"Requirement 6: a piece that cannot move down any more (the floor) should lock where it is - after gravity had a chance to lock it from row 18 the grid has {total()} filled cells and rows 18 and 19 are {cells()[18]} and {cells()[19]}.")
clear_grid()
place(4, 0)

# Full rows.
score0 = g.score
for c in (0, 1, 2, 3, 4, 5, 8, 9):
    g.grid[19][c] = 1
g.grid[17][0] = 1
drop(6)
expect(g.score - score0 == 10, f"Requirement 7: a full row was made and the score went up by {g.score - score0}; it should go up by 10 for each cleared row.")
expect(cells()[19] == [0, 0, 0, 0, 0, 0, 1, 1, 0, 0], f"Requirement 7: the full bottom row should be removed and everything above should drop one row, so the bottom row now holds only the top half of the block that completed it (cells 6 and 7). Row 19 is {cells()[19]}.")
expect(cells()[18] == [1, 0, 0, 0, 0, 0, 0, 0, 0, 0], f"Requirement 7: the cell that was on row 17 should have dropped to row 18. Row 18 is {cells()[18]}.")
expect(total() == 3, f"Requirement 7: after the clear there should be 3 filled cells; the grid has {total()}.")
expect(len(g.grid) == 20 and all(len(r) == 10 for r in g.grid), f"Requirement 7: the grid must still be 20 rows of 10 after a clear; it is {len(g.grid)} rows.")
clear_grid()

score1 = g.score
for r in (18, 19):
    for c in range(10):
        if c not in (4, 5):
            g.grid[r][c] = 1
drop(4)
expect(total() == 0, f"Requirement 7: two full rows were made at once and {total()} cells are left; both rows should be cleared. If you remove rows in a loop, take care not to skip the one that drops into the place of the row you just removed - building a list of the rows to KEEP (a comprehension with `not all(row)`) has no such trap.")
expect(g.score - score1 == 20, f"Requirement 7: clearing two rows at once should add 20 to the score; it added {g.score - score1}.")
expect(len(g.grid) == 20 and len({id(r) for r in g.grid}) == 20, "Requirement 7: after clearing two rows, some rows of grid are the same list - [[0] * 10] * 2 makes two names for ONE row. Make the new empty rows with [[0] * 10 for _ in range(n)].")
g.grid[0][0] = 1
expect(sum(1 for r in g.grid if r[0]) == 1, "Requirement 7: filling a cell on the top row filled a cell on another row too: the rows added after a clear are the same list. Make each new row separately: [[0] * 10 for _ in range(n)].")
clear_grid()

score2 = g.score
for c in (0, 1, 5, 6, 7, 8, 9):
    g.grid[19][c] = 1
drop(2)
expect(g.score == score2 and total() == 11, f"Requirement 7: the bottom row still has a hole (col 4), so it is not full and must stay. The score changed by {g.score - score2} and the grid has {total()} filled cells (should be 11).")
clear_grid()
cc.frames(1)
expect(any(str(g.score) in t for t in cc.texts()), f"Requirement 7: draw the score as text every frame - it should show {g.score}.")

# Drawing.
lay = cc.rects()
expect(len(lay) >= 1 and lay[0]["x"] <= 0 and lay[0]["y"] <= 0 and lay[0]["w"] >= WIDTH, "Requirement 1: every frame starts with a dark background over the whole canvas (and the loop must be running: on_frame).")
g.grid[19][0] = 1
g.grid[19][9] = 1
place(4, 3)
cc.frames(1)


def has_cell(c, r):
    return any(160 + c * 16 - 0.01 <= q["x"] <= 160 + c * 16 + 2 and r * 16 - 0.01 <= q["y"] <= r * 16 + 2 and 14 <= q["w"] <= 16 and 14 <= q["h"] <= 16 for q in cc.rects())


expect(has_cell(0, 19) and has_cell(9, 19), "Requirement 1: draw every filled cell of the grid as a square, 16 pixels (15 leaves a gap) at x 160 + col * 16, y row * 16 - the corners (col 0 and col 9, row 19) are missing.")
expect(all(has_cell(pc() + dc, pr() + dr) for dc in (0, 1) for dr in (0, 1)), "Requirement 2: draw the falling piece's four cells every frame, the same size and place as the grid's cells.")
clear_grid()

# The end.
g.grid[0][4] = 1
drop(0)
expect(g.state == "over", f"Requirement 8: a new piece has no room to start - col 4, row 0 is already filled - so the game is over; state is '{g.state}'.")
cc.frames(1)
expect(any(re.search("game over", t, re.I) for t in cc.texts()), "Requirement 8: put 'Game over' on the screen when the game is over.")
frozen = (cells()[19], cells()[18], pc(), pr())
tap("ArrowLeft")
tap("ArrowRight")
tap("ArrowDown", 2)
cc.frames(60)
expect(frozen == (cells()[19], cells()[18], pc(), pr()), "Requirement 8: once the game is over nothing should move: no gravity, no keys.")
cc.press("Enter")
cc.frames(1)
cc.release("Enter")
expect(g.state == "playing", "Requirement 8: Enter after a game over should start again: state back to 'playing'.")
expect(total() == 0 and g.score == 0, f"Requirement 8: a new game starts with an empty grid ({total()} filled) and score 0 (it is {g.score}).")
expect(len(g.grid) == 20 and len({id(r) for r in g.grid}) == 20, "Requirement 8: after a restart the grid must still be 20 separate rows of 10.")
expect(pc() == 4 and pr() <= 1, "Requirement 8: a new game starts with the piece at col 4, row 0.")
expect(not any(re.search("game over", t, re.I) for t in cc.texts()), "Requirement 8: 'Game over' is still on the screen after restarting.")
"""

# ── 5. Your own game ────────────────────────────────────────────────────

_OPEN_TEACHES = (
    "Nothing to match here and no check: start from the two setup lines and "
    "build any small canvas game you like, from nothing, the way the four "
    "projects before it asked. Some ideas, roughly easiest first: Snake "
    "(a list of (col, row) tuples, a direction, eat to grow); Pong against "
    "the computer (its paddle follows the ball, a little late); "
    "Asteroids-lite (a ship that turns and thrusts, rocks that drift and "
    "wrap round the edges with %); Whack-a-mole with on_click and a "
    "countdown from every(1, fn); Simon (a growing list of colours to "
    "repeat, shown with after()); the Chrome dinosaur (jump over cactuses "
    "that come faster and faster); Space Invaders; a platformer with one "
    "screen and a jump; Minesweeper on a grid you build with a "
    "comprehension; Conway's Game of Life with a click to toggle cells; a "
    "top-down maze with a key and a door. Start with one square that moves, "
    "then add a thing at a time - the same order every project here was "
    "built in."
)


def _step(**fields: object) -> Step:
    """A step on this track: Python, in the Python From blank track."""
    fields["track"] = TRACK
    fields["language"] = "python"
    check = str(fields.get("check", ""))
    if check:
        fields["check"] = _HELPERS + check
    return Step(**fields)  # type: ignore[arg-type]


PYBLANK_STEPS: tuple[Step, ...] = (
    _step(
        id="pyblank-01-pong",
        title="Pong for two",
        teaches=(
            "No starter and no steps: a spec and a check that plays what you "
            "build. Break it down the way the earlier tracks did. The game "
            "loop first: on_frame(fn) calls fn(dt) with the seconds since the "
            "last frame. Then two paddles - a dict each ({'x': 20, 'y': 130, "
            "...}), or a @dataclass Paddle with the same fields if you prefer "
            "paddle.y to paddle['y']; the check reads both - and ONE function "
            "that moves either, called in a loop that unpacks a tuple each "
            "time: for paddle, up, down in ((left, 'w', 's'), (right, "
            "'ArrowUp', 'ArrowDown')). `up in keys` asks whether a key is "
            "held. Clamp with max(0, min(HEIGHT - paddle['h'], paddle['y'])). "
            "The ball and its four edges: abs() and -abs() point a velocity "
            "one way without caring which way it pointed. The bounce off a "
            "paddle only counts while the ball is heading towards it, and "
            "only where the paddle is. Going off a side is a point and a "
            "serve(direction) rather than a bounce. 'r' is a one-off press, "
            "so on_key_down(fn), which hands fn the key's name. Draw the "
            "score with an f-string. Changing what a dict holds needs no "
            "`global`; re-binding a name does. Keep the names the spec "
            "gives - the check reads those, and nothing else."
        ),
        goal=(
            "Build Pong for two players from a blank page. The names and numbers below are what the check reads; the rest is yours. "
            "1) Redraw every frame (on_frame, with dt in seconds): first a dark background over the whole canvas, then everything below. "
            "2) Two paddles kept in `left` and `right`, each with x, y, w: 10, h: 60 and speed: 300 (a dict like {'x': 20, ...}, or a dataclass or any object with those attributes): `left` at x 20 and `right` at x 450, both at y 130. Draw each as a filled rectangle. "
            "3) The keys 'w' and 's' move `left` up and down at its speed, and 'ArrowUp' and 'ArrowDown' move `right`; neither paddle can leave the canvas. "
            "4) The ball is kept in `ball` with x, y, r, vx and vy: x 240, y 160, r 8, a vx of about 220 and some vy. Draw it as a filled circle. "
            "5) The ball bounces off the top and bottom edges, and off a paddle where the paddle actually is - each time it ends up heading away. "
            "6) When the ball goes fully off the left edge the right player scores, and off the right edge the left player scores: keep the points in `score` - a dict {'left': 0, 'right': 0}, read as score['left'] (an object with .left and .right works too) - both starting at 0, and draw them as text. "
            "7) After each point the ball is served from x 240, y 160, towards the player who just lost it. "
            "8) Pressing 'r' starts a new match: both scores 0, both paddles back at y 130, the ball served from the centre."
        ),
        starter=_BLANK,
        solution=_PONG,
        check=_PONG_CHECK,
        hint=(
            "One function can move both paddles: move_paddle(p, up, down, dt) - and `for paddle, up, down in "
            "((left, 'w', 's'), (right, 'ArrowUp', 'ArrowDown')):` calls it for each. Test the ball against a paddle "
            "only while it is heading towards it (vx < 0 for left), and put it on the paddle's face when it bounces."
        ),
    ),
    _step(
        id="pyblank-02-flappy",
        title="A Flappy-style gap game",
        teaches=(
            "A second whole game from nothing. The new parts: gravity is an "
            "acceleration - add to vy each frame, then move by vy - and a "
            "flap sets vy rather than adding to it, or a falling bird barely "
            "notices. Pipes are a list you append to on a timer (random."
            "uniform(30, 180) picks a gap height) and trim as they leave "
            "with a list comprehension - pipes = [p for p in pipes if ...] "
            "re-binds the name, so update needs `global pipes`. A pipe is a "
            "dict, or a small @dataclass Pipe(x, gap_y) with defaults for "
            "the rest, which the check reads either way. Each pipe is two "
            "rectangles round a gap, and a pipe should add to the score "
            "once, so it needs to remember it has been passed. The bird is "
            "a circle and a pipe half is a box: find the box's nearest "
            "point to the circle's centre, with max(left, min(x, right)), "
            "and compare math.dist to the radius. any() over the pipes "
            "asks whether any touches. Space is a one-off press: "
            "on_key_down(fn) gets ' ' for the space bar. Times are seconds "
            "(dt, or every(1.5, fn)), never a count of frames."
        ),
        goal=(
            "Build a Flappy-style game from a blank page. The names and numbers below are what the check reads; the rest is yours. "
            "1) Redraw every frame (on_frame, dt in seconds), a dark background first. "
            "2) The bird is `bird` with x, y, r and vy - {'x': 100, 'y': 160, 'r': 12, 'vy': 0} - drawn as a filled circle. Gravity adds 900 to vy every second, and y moves by vy * dt. "
            "3) Space (the key ' ') flaps: it sets vy to -300 (sets it, rather than adding to it). "
            "4) `pipes` is a list, empty at the start. Every 1.5 seconds a pipe is appended at x = WIDTH, with x, w: 50, gap_y and gap_h: 110 (as a dict or as an object), where gap_y, the top of the gap, is random from 30 to 180. Draw each pipe as two rectangles (from the top down to gap_y, and from gap_y + gap_h to the bottom of the canvas). Pipes move left at 150 pixels a second and leave the list once they are off the left edge. "
            "5) `score` (starts at 0) goes up by 1, once, for each pipe the bird gets past; draw it as text. "
            "6) `state` starts as 'playing'. It becomes 'over' when the bird touches a pipe, the floor or the ceiling; after that nothing moves and 'Game over' is on the screen. "
            "7) Space while the game is over starts again: bird back at y 160 with vy 0 (that press does not also flap), no pipes, score 0, state 'playing'."
        ),
        starter=_BLANK,
        solution=_FLAPPY,
        check=_FLAPPY_CHECK,
        hint=(
            "Each frame: bird['vy'] += 900 * dt; bird['y'] += bird['vy'] * dt. A pipe half is hit when the circle's nearest point on the box is "
            "closer than r: nearest_x = max(x, min(bird['x'], x + w)), the same for y, then math.dist(...) < bird['r'] - once for the top half "
            "and once for the bottom, inside any(... for p in pipes)."
        ),
    ),
    _step(
        id="pyblank-03-memory",
        title="Memory cards",
        teaches=(
            "This one is driven by the mouse, and by time. on_click(fn) calls "
            "fn(x, y) with the click already in canvas pixels, so find which "
            "card holds that point: next((c for c in cards if ...), None) "
            "gives the first match, or None. Build the deck as a list of "
            "pairs - [v for v in range(6) for _ in range(2)] - and mix it "
            "with random.shuffle(values), which shuffles in place (random."
            "sample(values, len(values)) returns a mixed copy). Deal it with "
            "enumerate and divmod(i, 4), which gives (row, col) from a card's "
            "number: for i, value in enumerate(values): row, col = divmod(i, "
            "4) - or zip the values with a list of (col, row) slots. Make each card its own object - [card] * 12 is ONE card "
            "listed twelve times, so turn one over and all twelve turn. The "
            "rules are a small state machine: no card picked, one picked, or "
            "two different cards showing while a timer runs - and during that "
            "last state clicks must be ignored. after(0.8, fn) runs fn once, "
            "0.8 game seconds later (counting 48 frames is right at 60 a "
            "second and wrong at 30); a lambda keeps the two cards for fn to "
            "turn back: after(0.8, lambda: hide(a, b)). Re-binding a name in "
            "the click handler needs `global`."
        ),
        goal=(
            "Build a Memory card game from a blank page. The names and numbers below are what the check reads; the rest is yours. "
            "1) `cards` is a list of 12 separate cards in a grid of 4 columns by 3 rows, each with x: 30 + col * 110, y: 20 + row * 100, w: 90, h: 80, value, face_up: False and matched: False (a dict each, or a dataclass). "
            "2) The values 0 to 5 each appear on exactly two cards, and they are shuffled. "
            "3) Redraw every frame (on_frame): a dark background, then each card as a rectangle - face down in one colour with no text, face up in another colour with its value written on it (ctx.fill_text). "
            "4) on_click gives the click in canvas pixels: a click on a face-down card turns it face up (face_up True). Clicks between cards or outside the grid, and clicks on a card that is already face up, do nothing. "
            "5) When the second card is turned: equal values - both get matched True and stay face up; different values - both stay face up for 0.8 seconds (after(0.8, fn) counts seconds, not frames) and then turn back down. While two different cards are showing, clicks do nothing. "
            "6) `state` starts as 'playing'; when every card is matched it becomes 'won' and 'You win!' is on the screen."
        ),
        starter=_BLANK,
        solution=_MEMORY,
        check=_MEMORY_CHECK,
        hint=(
            "def click(x, y): ... with on_click(click). Find the card with next((c for c in cards if not c.face_up and c.x <= x < c.x + c.w and "
            "c.y <= y < c.y + c.h), None). Remember the first pick in a variable (global first); on a mismatch set a locked flag, "
            "after(0.8, lambda: hide(a, b)) to turn both back and unlock. all(c.matched for c in cards) says the game is won."
        ),
    ),
    _step(
        id="pyblank-04-stacker",
        title="Falling blocks",
        teaches=(
            "A small Tetris with one kind of piece, a 2 by 2 square, so "
            "there is no rotation - the parts are the board and the rules "
            "around it. The board is a list of rows you read as grid[row]"
            "[col]. Build it with a comprehension, [[0] * 10 for _ in "
            "range(20)] - NOT [[0] * 10] * 20, which is ONE row listed "
            "twenty times: fill a cell in it and every row has it. The falling "
            "piece is NOT in the grid, only its top-left cell is kept, "
            "and it is written into the grid when it lands (it locks). One "
            "function, fits(col, row), that asks 'would the piece be inside "
            "the walls and on empty cells there?' answers every question: "
            "can it move left, right, down, can a new one start - all(...) "
            "over the four cells, with a chained comparison 0 <= col < 10. "
            "A full row is `all(row)`; to clear rows keep the others - kept "
            "= [row for row in grid if not all(row)] - and put new empty "
            "rows on top, which also avoids removing rows while counting "
            "through them (the next row takes the place of the one you "
            "removed, and a loop that moves on skips it). Gravity is "
            "every(0.5, fn), or a timer you add dt to. Moves are key PRESSES: "
            "on_key_down(fn) runs once as the key goes down, while "
            "`'ArrowLeft' in keys` is true on every frame it is held. Re-"
            "binding grid needs `global grid`."
        ),
        goal=(
            "Build a falling-blocks stacker from a blank page. The names and numbers below are what the check reads; the rest is yours. "
            "1) `grid` is a list of 20 rows of 10 cells, each row its own list, read as grid[row][col], 0 for empty and 1 for filled, and starts empty. Redraw every frame (on_frame, dt in seconds), a dark background first, and draw each filled cell as a square 16 pixels wide (15 leaves a gap) at x 160 + col * 16, y row * 16. "
            "2) There is one kind of piece, a 2 by 2 square, kept in `piece` with col and row - {'col': 4, 'row': 0}, its top-left cell (a dict, or an object with .col and .row). A new piece starts at col 4, row 0; draw its four cells. "
            "3) Every 0.5 seconds the piece moves down one row. "
            "4) ArrowLeft and ArrowRight move it one column for each key press (holding the key does not repeat), never into a wall or a filled cell. "
            "5) ArrowDown drops it all the way down at once. "
            "6) A piece that cannot move down any further (the floor, or a filled cell below) locks: its four cells become 1 in the grid, full rows are cleared, and a new piece starts. "
            "7) A full row (all 10 cells filled) is removed and everything above it drops one row; `score` (starts at 0) goes up by 10 for each row removed, and is drawn as text. "
            "8) `state` starts as 'playing'. If a new piece starts on filled cells, state becomes 'over' and 'Game over' is on the screen; nothing moves after that until Enter, which starts again with an empty grid, score 0 and state 'playing'."
        ),
        starter=_BLANK,
        solution=_STACKER,
        check=_STACKER_CHECK,
        hint=(
            "def fits(col, row): return all(0 <= col + dc < 10 and row + dr < 20 and not grid[row + dr][col + dc] for dc, dr in SHAPE) "
            "with SHAPE = [(0, 0), (1, 0), (0, 1), (1, 1)] - and use it for every move. To clear: kept = [row for row in grid if "
            "not all(row)], then grid = [[0] * 10 for _ in range(20 - len(kept))] + kept (with global grid)."
        ),
    ),
    _step(
        id="pyblank-05-yours",
        title="Your own game",
        teaches=_OPEN_TEACHES,
        goal="No check here - build whatever you like. Run it, play it, break it, fix it.",
        starter=_BLANK,
        solution=_BLANK,
        check="",
    ),
)
