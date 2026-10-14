"""The "Debug it (Python)" Canvas track: find the one bug in a small Python program.

The Python twin of the JavaScript "Debug it" track. Every step hands you a
small canvas program that is mostly right and runs without raising, with ONE
bug in it. The goal says what is wrong in terms of behaviour (what you would
see when you play it) and never where; you find the line, fix it, and the
check plays the program and passes only when the behaviour is right.

The steps are independent: a starter is its own buggy program, not the step
before it. Each solution is its starter with a small change (a line or two),
and the suite holds every step to that. The check message for a buggy starter
describes the SYMPTOM, never the cause - the learner has to find the cause.

The bugs are Python's own, one class each:

    1  time: movement per frame instead of per second (a /60 written into the code)
    2  an off-by-one: range(n + 1) draws a cell too many, worst when n is 0
    3  a canvas that is never cleared: the wipe runs once at load, not every frame
    4  half a collision test: only the x axis is asked
    5  removing from a list while a for loop walks it: items are skipped
    6  late binding: lambdas made in a loop all see the last value of i
    7  a missing `global`: the quiet local, nothing raised and nothing happens
    8  [[0] * W] * H: one row listed H times, so one click lights a whole column
    9  a mutable default argument: a shared list piles enemies up across restarts
    10 int(x / TILE) truncates towards zero where x // TILE floors

and an open step, "Break your own": plant bugs for a friend.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

TRACK = "Debug it (Python)"

#: Prepended to every check. Fields are a dict's or an object's, so a check
#: reads and sets them with get() and put(); `need` says a name the goal
#: states is missing, in the check's own words.
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

'''


def _fix(code: str, *swaps: tuple[str, str]) -> str:
    """The solution: the starter with a few small swaps made (each must be found)."""
    for old, new in swaps:
        assert old in code, old
        code = code.replace(old, new, 1)
    return code


# ── 1. Time: the ball that slows down ───────────────────────────────────

_SLOW = """import math

from canvas import ctx, WIDTH, HEIGHT, on_frame

ball = {'x': 60, 'y': 160, 'r': 12, 'vx': 200}


def update(dt):
    ball['x'] += ball['vx'] / 60
    if ball['x'] + ball['r'] > WIDTH:
        ball['x'] = WIDTH - ball['r']
        ball['vx'] = -abs(ball['vx'])
    if ball['x'] - ball['r'] < 0:
        ball['x'] = ball['r']
        ball['vx'] = abs(ball['vx'])


def draw():
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)
    ctx.fill_style = 'tomato'
    ctx.begin_path()
    ctx.arc(ball['x'], ball['y'], ball['r'], 0, math.tau)
    ctx.fill()
    ctx.fill_style = 'white'
    ctx.font = '16px monospace'
    ctx.fill_text(f"x: {ball['x']:.0f}", 10, 24)


def loop(dt):
    update(dt)
    draw()


on_frame(loop)
"""

_SLOW_FIXED = _fix(_SLOW, ("ball['x'] += ball['vx'] / 60", "ball['x'] += ball['vx'] * dt"))

_SLOW_CHECK = r"""
need("ball", "Requirement 1: keep the ball in a dict called ball: ball = {'x': 60, 'y': 160, 'r': 12, 'vx': 200}")


def B(k):
    return get(g.ball, k)


def reset():
    put(g.ball, "x", 100)
    put(g.ball, "y", 160)
    put(g.ball, "vx", 200)


reset()
cc.frames(2)
expect(any(near(a["x"], B("x"), 6) and near(a["y"], B("y"), 6) and a["r"] == B("r") for a in cc.arcs()), "Requirement 1: the ball should be drawn every frame as a filled circle at its x and y.")

for fps in (60, 30, 24, 120):
    reset()
    cc.frames(fps // 2, 1 / fps)
    moved = B("x") - 100
    expect(near(moved, 100, 3), f"Requirement 2: with the game running at {fps} frames a second, half a second of play moved the ball {num(moved)} pixels; at 200 pixels a second it should be 100. The ball should cover the same distance in the same time whatever the frame rate - on a slow machine as on a fast one.")

# The walls, played at 30 frames a second for six seconds.
reset()
turned = None
for i in range(1, 181):
    cc.frames(1, 1 / 30)
    expect(B("r") - 0.01 <= B("x") <= WIDTH - B("r") + 0.01, f"Requirement 3: {i / 30:.2f} seconds in, the ball is at x {B('x'):.1f} - partly outside the canvas. It should turn round at the walls, with its edge on the wall.")
    if turned is None and B("vx") < 0:
        turned = i / 30
expect(turned is not None and near(turned, 1.84, 0.1), f"Requirement 3: starting at x 100 and moving right at 200 pixels a second, the ball should reach the right wall (x 468) and turn round after about 1.84 seconds; it turned at {turned if turned is None else round(turned, 2)} seconds.")
expect(B("vx") > 0, "Requirement 3: after bouncing off the right wall and then the left wall, the ball should be heading right again.")
"""

# ── 2. An off-by-one: the fuel gauge ────────────────────────────────────

_GAUGE = """from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down

MAX_FUEL = 10
fuel = 6


def burn(key):
    global fuel
    if key == ' ' and fuel > 0:
        fuel -= 1
    elif key == 'r':
        fuel = MAX_FUEL


on_key_down(burn)


def draw_gauge():
    ctx.fill_style = '#f6ad55'
    for i in range(fuel + 1):
        ctx.fill_rect(20 + i * 26, 20, 20, 30)


def draw(dt):
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)
    draw_gauge()
    ctx.fill_style = 'white'
    ctx.font = '16px monospace'
    ctx.fill_text(f'fuel {fuel} / {MAX_FUEL}', 20, 80)
    ctx.fill_text('Space burns fuel, R refuels', 20, 300)


on_frame(draw)
"""

_GAUGE_FIXED = _fix(_GAUGE, ("range(fuel + 1)", "range(fuel)"))

_GAUGE_CHECK = r"""
need("fuel", "Requirement 1: keep the fuel in a variable called fuel - a whole number from 0 to 10: fuel = 6")


def cells():
    return sorted(r["x"] for r in cc.rects() if r["w"] == 20 and r["h"] == 30)


def show(n):
    g.fuel = n
    cc.frames(1)
    return cells()


def tap(key):
    cc.press(key)
    cc.frames(1)
    cc.release(key)


cc.frames(1)
for n in (6, 3, 1, 10, 0):
    got = show(n)
    want = [20 + 26 * i for i in range(n)]
    ending = " An empty tank should show no cells at all." if n == 0 else ""
    expect(got == want, f"Requirement 1: with the fuel at {n} the gauge shows {len(got)} cells (at x {[round(v) for v in got]}); it should show exactly {n}, side by side from x 20 and 26 pixels apart.{ending}")

g.fuel = 4
tap(" ")
expect(g.fuel == 3 and len(cells()) == 3, f"Requirement 2: Space burns one fuel: from 4 to 3, and the gauge follows; the fuel is {g.fuel} and the gauge shows {len(cells())} cells.")
g.fuel = 1
tap(" ")
tap(" ")
tap(" ")
expect(g.fuel == 0 and cells() == [], f"Requirement 2: the tank can be emptied but not past empty: the fuel is {g.fuel} and the gauge shows {len(cells())} cells after burning more than was left.")
tap("r")
expect(g.fuel == 10 and len(cells()) == 10, f"Requirement 3: R refills the tank to 10 and the gauge shows ten cells; the fuel is {g.fuel} and the gauge shows {len(cells())}.")
"""

# ── 3. A canvas that is never cleared ───────────────────────────────────

_TRAILS = """from canvas import ctx, WIDTH, HEIGHT, on_frame, keys

player = {'x': 224, 'y': 144, 'size': 32, 'speed': 240}

ctx.fill_style = '#10141f'
ctx.fill_rect(0, 0, WIDTH, HEIGHT)


def update(dt):
    if 'ArrowLeft' in keys:
        player['x'] -= player['speed'] * dt
    if 'ArrowRight' in keys:
        player['x'] += player['speed'] * dt
    if 'ArrowUp' in keys:
        player['y'] -= player['speed'] * dt
    if 'ArrowDown' in keys:
        player['y'] += player['speed'] * dt
    player['x'] = max(0, min(WIDTH - player['size'], player['x']))
    player['y'] = max(0, min(HEIGHT - player['size'], player['y']))


def draw():
    ctx.fill_style = '#4fd1c5'
    ctx.fill_rect(player['x'], player['y'], player['size'], player['size'])


def loop(dt):
    update(dt)
    draw()


on_frame(loop)
"""

_TRAILS_BG = "    ctx.fill_style = '#10141f'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n"
_TRAILS_FIXED = _fix(
    _TRAILS,
    ("\nctx.fill_style = '#10141f'\nctx.fill_rect(0, 0, WIDTH, HEIGHT)\n\n", "\n"),
    ("def draw():\n", "def draw():\n" + _TRAILS_BG),
)

_TRAILS_CHECK = r"""
need("player", "Requirement 1: keep the square in a dict called player: player = {'x': 224, 'y': 144, 'size': 32, 'speed': 240}")


def P(k):
    return get(g.player, k)


def covers(c):
    a = c["args"]
    return c["name"] in ("fill_rect", "clear_rect") and a[0] <= 0 and a[1] <= 0 and a[2] >= WIDTH and a[3] >= HEIGHT


def look():
    calls = cc.drawn()
    wipe = next((i for i, c in enumerate(calls) if covers(c)), None)
    body = next((i for i, c in enumerate(calls) if c["name"] == "fill_rect" and c["args"][2] == P("size") and c["args"][3] == P("size")), None)
    return wipe, body


def seen(label):
    wipe, body = look()
    expect(body is not None, "Requirement 1: the square is not drawn: draw it every frame as a filled square of its size.")
    expect(wipe is not None, f"Requirement 1: {label} the square leaves a trail - what was drawn in the frames before is still on the screen, so moving makes a smear instead of a square. Only the square's current place should show.")
    expect(wipe < body, "Requirement 1: the square cannot be seen at all - something painted over it after it was drawn.")


cc.frames(1)
seen("")

put(g.player, "x", 100)
put(g.player, "y", 140)
x0 = P("x")
cc.press("ArrowRight")
for i in range(15):
    cc.frames(1, 1 / 30)
    seen(f"after {i + 1} frames of moving right, ")
cc.release("ArrowRight")
expect(near(P("x") - x0, 120, 3), f"Requirement 2: holding ArrowRight for half a second at 30 frames a second moved the square {num(P('x') - x0)} pixels; at 240 pixels a second it should be about 120.")

y0 = P("y")
cc.press("ArrowUp")
cc.frames(6, 1 / 30)
cc.release("ArrowUp")
expect(near(y0 - P("y"), 48, 3), f"Requirement 2: holding ArrowUp for a fifth of a second moved the square {num(y0 - P('y'))} pixels up; it should be about 48.")

cc.press("ArrowRight")
cc.frames(90, 1 / 30)
cc.release("ArrowRight")
expect(near(P("x"), WIDTH - P("size"), 0.01), f"Requirement 2: after three seconds of ArrowRight the square is at x {num(P('x'))}; it should stop with its right edge on the canvas edge, x {WIDTH - P('size')}.")
cc.frames(2, 1 / 30)
seen("at the edge, ")
"""

# ── 4. Half a collision test: the rock ──────────────────────────────────

_ROCK = """import random

from canvas import ctx, WIDTH, HEIGHT, on_frame, keys

player = {'x': 220, 'y': 270, 'w': 40, 'h': 40}
rock = {'x': 100, 'y': -30, 'w': 30, 'h': 30, 'vy': 180}
lives = 3


def hits(a, b):
    return a['x'] < b['x'] + b['w'] and a['x'] + a['w'] > b['x']


def drop_rock():
    rock['x'] = random.randint(0, WIDTH - rock['w'])
    rock['y'] = -rock['h']


def update(dt):
    global lives
    if 'ArrowLeft' in keys:
        player['x'] -= 260 * dt
    if 'ArrowRight' in keys:
        player['x'] += 260 * dt
    player['x'] = max(0, min(WIDTH - player['w'], player['x']))
    rock['y'] += rock['vy'] * dt
    if hits(player, rock):
        lives -= 1
        drop_rock()
    elif rock['y'] > HEIGHT:
        drop_rock()


def draw():
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)
    ctx.fill_style = '#4fd1c5'
    ctx.fill_rect(player['x'], player['y'], player['w'], player['h'])
    ctx.fill_style = '#a0aec0'
    ctx.fill_rect(rock['x'], rock['y'], rock['w'], rock['h'])
    ctx.fill_style = 'white'
    ctx.font = '16px monospace'
    ctx.fill_text(f'lives: {lives}', 10, 24)


def loop(dt):
    update(dt)
    draw()


on_frame(loop)
"""

_ROCK_HITS = "    return a['x'] < b['x'] + b['w'] and a['x'] + a['w'] > b['x']\n"
_ROCK_FIXED = _fix(_ROCK, (_ROCK_HITS, (
    "    return (a['x'] < b['x'] + b['w'] and a['x'] + a['w'] > b['x']\n"
    "            and a['y'] < b['y'] + b['h'] and a['y'] + a['h'] > b['y'])\n"
)))

_ROCK_CHECK = r"""
need("player", "Requirement 1: keep the player in a dict called player: {'x': 220, 'y': 270, 'w': 40, 'h': 40}")
need("rock", "Requirement 1: keep the rock in a dict called rock: {'x': 100, 'y': -30, 'w': 30, 'h': 30, 'vy': 180}")
need("lives", "Requirement 1: keep the lives in a variable called lives: lives = 3")

px, py, pw, ph = (get(g.player, k) for k in ("x", "y", "w", "h"))
rw, rh = get(g.rock, "w"), get(g.rock, "h")


def place(x, y):
    put(g.rock, "x", x)
    put(g.rock, "y", y)
    put(g.rock, "vy", 0)
    g.lives = 3
    cc.frames(2)
    return g.lives


cc.frames(1)
expect(any(r["x"] == get(g.rock, "x") and r["y"] == get(g.rock, "y") and r["w"] == rw and r["h"] == rh for r in cc.rects()), "Requirement 1: draw the rock every frame as a filled rectangle at its x and y.")

left = place(px, 20)
expect(left == 3, f"Requirement 2: a rock near the top of the canvas, far above the player's head, took {3 - left} of the player's 3 lives. A rock far away from the square should be harmless.")
left = place(px, py - rh - 3)
expect(left == 3, f"Requirement 2: a rock 3 pixels above the square, not yet touching it, took {3 - left} of the player's lives. It should only hurt once it touches.")
left = place(px - 150, py)
expect(left == 3, f"Requirement 2: a rock level with the square but 150 pixels to the side took {3 - left} lives. It should miss.")
left = place(px + pw + 2, py)
expect(left == 3, f"Requirement 2: a rock level with the square and 2 pixels clear of its right edge took {3 - left} lives. It should miss.")
left = place(px, py + ph + 5)
expect(left == 3, f"Requirement 2: a rock that is already below the square, 5 pixels past its bottom edge, took {3 - left} lives. It should miss.")
left = place(px, py)
expect(left == 2, f"Requirement 3: a rock right on top of the square should cost exactly one life; the player has {left} of 3 left.")
expect(get(g.rock, "y") < py - 100, "Requirement 3: after hitting the player the rock should start again from the top of the canvas.")
left = place(px + pw - 10, py - rh + 10)
expect(left == 2, f"Requirement 3: a rock overlapping the square's top-right corner by 10 pixels should cost one life; the player has {left} of 3 left.")

for fps in (30, 60):
    g.lives = 3
    put(g.rock, "x", px)
    put(g.rock, "y", -rh)
    put(g.rock, "vy", 180)
    n = 0
    while g.lives == 3 and n < 4 * fps:
        cc.frames(1, 1 / fps)
        n += 1
    expect(g.lives == 2, f"Requirement 4: at {fps} frames a second a rock fell straight onto the square and the player still has {g.lives} lives; it should have cost exactly one.")
    expect(near(n / fps, 1.5, 0.12), f"Requirement 4: at {fps} frames a second a rock falling at 180 pixels a second from the top should reach the square after about 1.5 seconds; it hurt after {n / fps:.2f}.")
    cc.frames(fps // 2, 1 / fps)
    expect(g.lives == 2, f"Requirement 4: one rock should cost one life; half a second later the player is down to {g.lives}.")
"""

# ── 5. Removing from a list while looping over it ───────────────────────

_BALLOONS = """import math

from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down

balloons = [
    {'x': 40 + i * 50, 'y': 150 + (i % 3) * 20, 'r': 20,
     'color': 'red' if c == 'r' else 'blue'}
    for i, c in enumerate('rrbrrrbrr')
]


def sweep(key):
    if key == 'c':
        for b in balloons:
            if b['color'] == 'red':
                balloons.remove(b)


on_key_down(sweep)


def draw(dt):
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)
    for b in balloons:
        ctx.fill_style = b['color']
        ctx.begin_path()
        ctx.arc(b['x'], b['y'], b['r'], 0, math.tau)
        ctx.fill()
    ctx.fill_style = 'white'
    ctx.font = '16px monospace'
    ctx.fill_text(f'{len(balloons)} balloons - press C to pop the red ones', 10, 24)


on_frame(draw)
"""

_BALLOONS_LOOP = "        for b in balloons:\n            if b['color'] == 'red':\n"
_BALLOONS_FIXED = _fix(_BALLOONS, (_BALLOONS_LOOP, "        for b in list(balloons):\n            if b['color'] == 'red':\n"))

_BALLOONS_CHECK = r"""
need("balloons", "Requirement 1: keep the balloons in a list called balloons - each a dict with 'x', 'y', 'r' and 'color' ('red' or 'blue').")


def count(colour):
    return sum(1 for b in g.balloons if get(b, "color") == colour)


def line_up(pattern):
    g.balloons[:] = [{"x": 40 + i * 50, "y": 150, "r": 20, "color": "red" if c == "r" else "blue"} for i, c in enumerate(pattern)]


def pop():
    cc.press("c")
    cc.frames(1)
    cc.release("c")


cc.frames(1)
expect(len(g.balloons) == 9 and count("red") == 7 and count("blue") == 2, f"Requirement 1: the row starts with 9 balloons, 7 red and 2 blue; the list has {len(g.balloons)} ({count('red')} red, {count('blue')} blue).")
expect(len(cc.arcs()) == 9, f"Requirement 1: every balloon in the list is drawn every frame as a circle; {len(cc.arcs())} circles on the screen.")

pop()
left = count("red")
expect(left == 0, f"Requirement 2: after one press of C, {left} of the 7 red balloons are still floating there (pressing C again pops a few more). One press should pop every red balloon.")
expect(count("blue") == 2 and len(g.balloons) == 2, f"Requirement 3: only the red balloons pop; the 2 blue ones stay. The row has {count('blue')} blue balloons and {len(g.balloons)} balloons in all.")
expect(len(cc.arcs()) == 2, f"Requirement 3: the screen should show exactly the balloons in the list: 2 circles, but there are {len(cc.arcs())}.")
pop()
expect(count("blue") == 2 and len(g.balloons) == 2, "Requirement 3: popping when there is nothing red left must change nothing.")

line_up("rrrrrrrb")
pop()
left = count("red")
expect(left == 0 and count("blue") == 1, f"Requirement 2: a row of seven red balloons with a blue at the end: after one press of C {left} red balloons are still there. All seven should pop at once, the blue one stays.")
line_up("brrrrbrrb")
pop()
left = count("red")
expect(left == 0 and count("blue") == 3 and len(g.balloons) == 3, f"Requirement 2: in a row of blue, four red, blue, two red, blue, one press of C should leave exactly the 3 blue balloons; there are {len(g.balloons)} balloons, {left} of them red.")
"""

# ── 6. Late binding: the sparks ─────────────────────────────────────────

_SPARKS = """import math

from canvas import ctx, WIDTH, HEIGHT, on_frame, after

sparks = []


def spawn(i):
    sparks.append({'x': 60 + i * 90, 'y': 160, 'r': 6 + i * 3})


for i in range(5):
    after(i * 0.5, lambda: spawn(i))


def draw(dt):
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)
    ctx.fill_style = '#f6e05e'
    for s in sparks:
        ctx.begin_path()
        ctx.arc(s['x'], s['y'], s['r'], 0, math.tau)
        ctx.fill()
    ctx.fill_style = 'white'
    ctx.font = '16px monospace'
    ctx.fill_text(f'{len(sparks)} sparks', 10, 24)


on_frame(draw)
"""

_SPARKS_FIXED = _fix(_SPARKS, ("lambda: spawn(i)", "lambda i=i: spawn(i)"))

_SPARKS_CHECK = r"""
need("sparks", "Requirement 1: keep the sparks in a list called sparks - each a dict with 'x', 'y' and 'r'.")

appeared = []
for i in range(1, 91):
    cc.frames(1, 1 / 30)
    while len(appeared) < len(g.sparks):
        appeared.append(i / 30)

xs = [get(s, "x") for s in g.sparks]
rs = [get(s, "r") for s in g.sparks]
expect(len(g.sparks) == 5, f"Requirement 1: after three seconds there are {len(g.sparks)} sparks on the screen; there should be five.")
expect(xs == [60, 150, 240, 330, 420], f"Requirement 2: the five sparks should be spread across the screen, one at each of x 60, 150, 240, 330 and 420, left to right. Yours are at x {[round(x) for x in xs]}.")
expect(rs == [6, 9, 12, 15, 18], f"Requirement 2: the sparks should grow from left to right, with radii 6, 9, 12, 15 and 18. Yours are {rs}.")
for k, t in enumerate(appeared):
    expect(near(t, k * 0.5, 0.07), f"Requirement 3: the sparks should light up one at a time, the first at once and then one every half second; spark {k + 1} lit up at {t:.2f} seconds, it should be at {k * 0.5:.1f}.")
cc.frames(1)
expect(len(cc.arcs()) == 5, f"Requirement 2: every spark is drawn as a circle every frame; {len(cc.arcs())} circles on the screen.")
"""

# ── 7. A missing global: the quiet local ────────────────────────────────

_CLOCK = """import math

from canvas import ctx, WIDTH, HEIGHT, on_frame, on_click

score = 0
time_left = 5.0
state = 'playing'
target = {'x': 240, 'y': 170, 'r': 40}


def click(x, y):
    global score
    if state != 'playing':
        return
    if (x - target['x']) ** 2 + (y - target['y']) ** 2 <= target['r'] ** 2:
        score += 1


on_click(click)


def update(dt):
    global time_left
    time_left -= dt
    if time_left <= 0:
        state = 'over'


def draw():
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)
    ctx.fill_style = '#f6ad55'
    ctx.begin_path()
    ctx.arc(target['x'], target['y'], target['r'], 0, math.tau)
    ctx.fill()
    ctx.fill_style = 'white'
    ctx.font = '20px monospace'
    ctx.fill_text(f'Score: {score}', 10, 28)
    ctx.fill_text(f'{max(time_left, 0):.1f}s', 410, 28)
    if state == 'over':
        ctx.font = '32px monospace'
        ctx.fill_text('Time is up!', 150, 90)


def loop(dt):
    update(dt)
    draw()


on_frame(loop)
"""

_CLOCK_FIXED = _fix(_CLOCK, ("    global time_left\n    time_left -= dt", "    global time_left, state\n    time_left -= dt"))

#: The body of the clock check, with FPS filled in by a line above it.
_CLOCK_BODY = r"""
need("score", "Requirement 1: keep the points in a variable called score: score = 0")


def secs(s):
    cc.frames(round(s * FPS), 1 / FPS)


def tap():
    cc.click(240, 170)


secs(0.2)
tap()
expect(g.score == 1, f"Requirement 1: a click on the big circle should score a point; the score is {g.score}.")
cc.click(40, 40)
expect(g.score == 1, f"Requirement 1: a click outside the circle should score nothing; the score is {g.score}.")
secs(4)
tap()
expect(g.score == 2, f"Requirement 2: with about 0.8 seconds left on the clock a click on the circle should still score; the score is {g.score}.")
secs(1.5)
before = g.score
tap()
cc.frames(1, 1 / FPS)
expect(g.score == before, f"Requirement 3: the clock ran out more than a second ago, yet a click on the circle still scored (the score went from {before} to {g.score}). Once time is up the game is over and clicks do nothing.")
expect(any(re.search("time is up", t, re.I) for t in cc.texts()), "Requirement 3: when the 5 seconds are over, 'Time is up!' should be on the screen - and it never appears. Nothing is raised, nothing happens.")
"""

_CLOCK_CHECK = "import re\n\nFPS = 30\n" + _CLOCK_BODY

# ── 8. [[0] * W] * H: one row listed H times ────────────────────────────

_PAINT = """from canvas import ctx, WIDTH, HEIGHT, on_frame, on_click

COLS, ROWS, CELL = 12, 8, 40
grid = [[0] * COLS] * ROWS


def toggle(x, y):
    col, row = int(x // CELL), int(y // CELL)
    if 0 <= col < COLS and 0 <= row < ROWS:
        grid[row][col] = 1 - grid[row][col]


on_click(toggle)


def draw(dt):
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)
    ctx.fill_style = '#f6ad55'
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell:
                ctx.fill_rect(c * CELL + 1, r * CELL + 1, CELL - 2, CELL - 2)
    ctx.fill_style = '#a0aec0'
    ctx.font = '14px monospace'
    ctx.fill_text('Click a square', 10, 18)


on_frame(draw)
"""

_PAINT_FIXED = _fix(_PAINT, ("grid = [[0] * COLS] * ROWS", "grid = [[0] * COLS for _ in range(ROWS)]"))

_PAINT_CHECK = r"""
need("grid", "Requirement 1: keep the squares in a list of rows called grid - grid[row][col], 0 or 1 - 8 rows of 12.")


def lit():
    return sorted((r["x"], r["y"]) for r in cc.rects() if r["w"] == 38 and r["h"] == 38)


def total():
    return sum(sum(row) for row in g.grid)


def tap(col, row):
    cc.click(col * 40 + 20, row * 40 + 20)
    cc.frames(1)


def square(col, row):
    return (col * 40 + 1, row * 40 + 1)


cc.frames(1)
expect(len(g.grid) == 8 and all(len(row) == 12 for row in g.grid), "Requirement 1: the grid is 8 rows of 12 squares: grid[row][col].")
expect(total() == 0 and lit() == [], "Requirement 1: nothing is lit to start with.")

tap(3, 2)
seen = lit()
cols = sorted({(x - 1) // 40 for x, y in seen})
rows = sorted({(y - 1) // 40 for x, y in seen})
expect(seen == [square(3, 2)], f"Requirement 2: one click on the square in column 3, row 2 lit {len(seen)} squares (in columns {cols} and rows {rows}). Only the square that was clicked should light up.")
expect(total() == 1 and g.grid[2][3] == 1, f"Requirement 2: the grid should hold exactly one lit cell, grid[2][3]; it holds {total()}.")
tap(3, 5)
expect(lit() == [square(3, 2), square(3, 5)], f"Requirement 2: a second click, further down the same column, should light that square only; {len(lit())} squares are lit.")
tap(11, 7)
tap(0, 0)
expect(lit() == [square(0, 0), square(3, 2), square(3, 5), square(11, 7)], f"Requirement 3: four clicks (corners and all) should light four separate squares; {len(lit())} are lit.")
tap(3, 2)
expect(lit() == [square(0, 0), square(3, 5), square(11, 7)], f"Requirement 3: clicking a lit square again puts it out, and only it; {len(lit())} squares are lit.")
expect(total() == 3 and g.grid[2][3] == 0, f"Requirement 3: the grid should hold 3 lit cells now; it holds {total()}.")
"""

# ── 9. A mutable default argument: the wave that doubles ────────────────

_WAVES = """from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down


def make_wave(count, enemies=[]):
    for i in range(count):
        enemies.append({'x': 40 + i * 80, 'y': -20, 'w': 30, 'h': 30})
    return enemies


enemies = make_wave(5)


def restart(key):
    global enemies
    if key == 'r':
        enemies = make_wave(5)


on_key_down(restart)


def update(dt):
    for e in enemies:
        e['y'] += 60 * dt


def draw():
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)
    ctx.fill_style = '#fc8181'
    for e in enemies:
        ctx.fill_rect(e['x'], e['y'], e['w'], e['h'])
    ctx.fill_style = 'white'
    ctx.font = '16px monospace'
    ctx.fill_text(f'{len(enemies)} enemies - R starts the wave again', 10, 310)


def loop(dt):
    update(dt)
    draw()


on_frame(loop)
"""

_WAVES_FIXED = _fix(_WAVES, ("def make_wave(count, enemies=[]):\n", "def make_wave(count, enemies=None):\n    if enemies is None:\n        enemies = []\n"))

_WAVES_CHECK = r"""
need("enemies", "Requirement 1: keep the enemies in a list called enemies - each a dict with 'x', 'y', 'w' and 'h'.")


def wave():
    return [(round(get(e, "x")), round(get(e, "y"))) for e in g.enemies]


def drawn():
    return sum(1 for r in cc.rects() if r["w"] == 30 and r["h"] == 30)


def fresh():
    return [(40 + i * 80, -20) for i in range(5)]


expect(wave() == fresh(), f"Requirement 1: the game starts with 5 enemies at the top, at x 40, 120, 200, 280 and 360 and y -20; the list holds {wave()}.")


def restart_after(seconds):
    cc.frames(round(seconds * 30), 1 / 30)
    cc.press("r")
    cc.release("r")


for press in (1, 2, 3):
    restart_after(1)
    expect(len(g.enemies) == 5, f"Requirement 2: after pressing R {press} time(s) the screen holds {len(g.enemies)} enemies; every press of R should start a new wave of exactly 5, in place of the old one.")
    expect(wave() == fresh(), f"Requirement 2: after pressing R the new wave should be 5 enemies all back at the top, at y -20; the screen holds {wave()}.")
    cc.frames(1, 1 / 30)
    expect(drawn() == 5, f"Requirement 2: after pressing R {press} time(s) there are {drawn()} enemies drawn on the screen; there should be 5.")

cc.frames(30, 1 / 30)
ys = sorted({y for x, y in wave()})
expect(len(ys) == 1 and near(ys[0], 42, 3), f"Requirement 3: a second after the new wave starts, all five enemies should have crept down to about y 42 (60 pixels a second for just over a second); they are at y {ys}.")
"""

# ── 10. / and // : one tile off ─────────────────────────────────────────

_TILES = """from canvas import ctx, WIDTH, HEIGHT, on_frame, keys

TILE = 40
MID = WIDTH // 2
player = {'x': 100.0, 'speed': 160}


def tile_of(x):
    return int(x / TILE)


def update(dt):
    if 'ArrowLeft' in keys:
        player['x'] -= player['speed'] * dt
    if 'ArrowRight' in keys:
        player['x'] += player['speed'] * dt
    player['x'] = max(-MID, min(MID - 1, player['x']))


def draw():
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)
    ctx.fill_style = '#2d3a5a'
    for k in range(-6, 6):
        ctx.fill_rect(MID + k * TILE + 1, 200, TILE - 2, 8)
    col = tile_of(player['x'])
    ctx.fill_style = '#2c5282'
    ctx.fill_rect(MID + col * TILE, 120, TILE, TILE)
    ctx.fill_style = '#f6e05e'
    ctx.begin_path()
    ctx.arc(MID + player['x'], 140, 8, 0, 6.2832)
    ctx.fill()
    ctx.fill_style = 'white'
    ctx.font = '16px monospace'
    ctx.fill_text(f'tile {col}', 10, 24)


def loop(dt):
    update(dt)
    draw()


on_frame(loop)
"""

_TILES_FIXED = _fix(_TILES, ("return int(x / TILE)", "return int(x // TILE)"))

_TILES_CHECK = r"""
import math
import re

need("player", "Requirement 1: keep the player in a dict called player with its 'x' - the world position, from -240 (the left edge) to 239: player = {'x': 100.0, 'speed': 160}")


def look():
    boxes = [r["x"] for r in cc.rects() if r["w"] == 40 and r["h"] == 40]
    labels = [t.strip() for t in cc.texts() if t.strip().startswith("tile")]
    return boxes, labels


def right_here(x, where):
    col = math.floor(x / 40)
    boxes, labels = look()
    expect(len(boxes) == 1, f"Requirement 1: {where}the highlight is one square, 40 by 40; {len(boxes)} such squares are drawn.")
    shown = (boxes[0] - 240) / 40
    label = labels[0] if labels else "no label"
    expect(boxes[0] == 240 + col * 40, f"Requirement 2: {where}the player is at x {x:.1f}, which is inside tile {col} (tile 0 is the 40 pixels right of the middle line, tile -1 the 40 to its left); but the highlight is on tile {shown:g} and the label says '{label}'. The highlight should sit exactly under the player.")
    expect(any(re.fullmatch(rf"tile {col}(\.0)?", t) for t in labels), f"Requirement 2: {where}the player is at x {x:.1f}, in tile {col}, but the label says '{label}'.")


for x in (100, 10, 79, 0, 40, 239, -1, -10, -39, -40, -41, -79.5, -150, -239.5):
    put(g.player, "x", x)
    cc.frames(1)
    right_here(x, "at rest, ")

# Walk left across the middle line at 30 frames a second.
put(g.player, "x", 100)
cc.press("ArrowLeft")
for i in range(66):
    cc.frames(1, 1 / 30)
    right_here(get(g.player, "x"), f"walking left, {i + 1} frames in, ")
cc.release("ArrowLeft")
"""

# ── 11. Break your own ──────────────────────────────────────────────────

_CATCH = """import random

from canvas import ctx, WIDTH, HEIGHT, on_frame, keys

basket = {'x': 215, 'y': 285, 'w': 50, 'h': 20, 'speed': 280}
star = {'x': 100, 'y': 0, 'size': 18, 'vy': 140}
score = 0
misses = 0


def new_star():
    star['x'] = random.randint(0, WIDTH - star['size'])
    star['y'] = -star['size']


def caught():
    return (basket['x'] < star['x'] + star['size']
            and basket['x'] + basket['w'] > star['x']
            and basket['y'] < star['y'] + star['size']
            and basket['y'] + basket['h'] > star['y'])


def update(dt):
    global score, misses
    if 'ArrowLeft' in keys:
        basket['x'] -= basket['speed'] * dt
    if 'ArrowRight' in keys:
        basket['x'] += basket['speed'] * dt
    basket['x'] = max(0, min(WIDTH - basket['w'], basket['x']))
    star['y'] += star['vy'] * dt
    if caught():
        score += 1
        new_star()
    elif star['y'] > HEIGHT:
        misses += 1
        new_star()


def draw():
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)
    ctx.fill_style = '#4fd1c5'
    ctx.fill_rect(basket['x'], basket['y'], basket['w'], basket['h'])
    ctx.fill_style = '#f6e05e'
    ctx.fill_rect(star['x'], star['y'], star['size'], star['size'])
    ctx.fill_style = 'white'
    ctx.font = '16px monospace'
    ctx.fill_text(f'caught {score}  missed {misses}', 10, 24)


def loop(dt):
    update(dt)
    draw()


on_frame(loop)
"""

_OPEN_TEACHES = (
    "Nothing to match here and no check: this is a small, working catch "
    "game, and your job is the other half of debugging - planting a bug "
    "for someone else, the way the ten programs before it did. A good bug "
    "looks right at a glance, runs without an error, and shows up as a "
    "symptom you can describe without saying where it is. Python "
    "flavours to plant: a missing `global` (the score never goes up); a "
    "late-binding lambda in a loop; a [[0] * 5] * 5 grid; a mutable "
    "default argument; removing from a list while looping over it; "
    "`range(n + 1)`; int(x / n) where x // n belongs; `is` where == "
    "belongs (it works on small numbers and then does not); a copy that "
    "is not a copy (b = a, then changing b); a speed per frame instead of "
    "per second; a collision that checks one axis; `=` where `+=` "
    "belongs. Then run it and write the symptom in one sentence, hand it "
    "over, and watch what they try first: print(), a smaller program, or "
    "breakpoint() in a terminal. If it takes them more than ten minutes "
    "the bug is good."
)


def _step(**fields: object) -> Step:
    """A step on this track: Python, in the Debug it (Python) track."""
    fields["track"] = TRACK
    fields["language"] = "python"
    check = str(fields.get("check", ""))
    if check:
        fields["check"] = _HELPERS + check
    return Step(**fields)  # type: ignore[arg-type]


PYDEBUG_STEPS: tuple[Step, ...] = (
    _step(
        id="pydbg-01-slow-ball",
        title="The ball that slows down",
        teaches=(
            "Bug class: time. A frame is not a unit of time. A game that "
            "moves by a fixed amount each frame runs fast on a quick "
            "machine and slowly on a slow one - and looks perfect on the "
            "machine it was written on. dt is the seconds since the last "
            "frame, so anything with a speed moves by speed * dt (pixels a "
            "second times seconds); a number like / 60 or * 0.016 is only a "
            "guess at dt, written into the code. How to hunt it: print(dt) "
            "at the top of the function to see what the loop really hands "
            "you (print output appears under the canvas here), then print "
            "the thing that should move by a known amount in a known time "
            "- 'one second on, x should be 200 further' - and look at every "
            "number in that function that smells like a frame rate."
        ),
        goal=(
            "A ball bounces between the left and right walls at 200 pixels a second. It looks right on the machine it was written on. "
            "But when the game runs at 30 frames a second instead of 60 (a slower machine), the same ball crawls along at half the speed, and at 120 frames a second it races. "
            "The check reads `ball`, a dict with x, y, r and vx. Find what is wrong and fix it so that: "
            "1) the ball covers the same distance in the same time at 24, 30, 60 and 120 frames a second; "
            "2) it still turns round at the left and right walls without leaving the canvas; "
            "3) it is still drawn every frame as a circle."
        ),
        starter=_SLOW,
        solution=_SLOW_FIXED,
        check=_SLOW_CHECK,
        hint=(
            "Put print(dt) at the top of update(). Then read the line that moves the ball and ask: where does the time "
            "come from, and is it the time this frame really took?"
        ),
    ),
    _step(
        id="pydbg-02-fuel-gauge",
        title="One cell too many",
        teaches=(
            "Bug class: the off-by-one, the oldest bug there is. range(n) "
            "gives n numbers, 0 to n - 1; range(n + 1) gives one more, "
            "which is right only when you really want the end included. "
            "Python's ranges and slices stop BEFORE their end, so a loop "
            "that 'includes the last one' is usually the wrong instinct. "
            "The smallest case shows it worst, so hunt there: try 0, then a "
            "middle value, then the biggest. print(list(range(fuel + 1))) "
            "shows exactly what the loop walks over (print the repr of what "
            "you loop over, not what you think it is), and print(len(...)) "
            "counts what you drew against what you meant. Count the fence "
            "posts and the gaps: a gauge of n cells needs n, not n + 1."
        ),
        goal=(
            "A fuel gauge shows one orange cell for each unit of fuel left: with 6 fuel, 6 cells. Space burns one fuel and R fills the tank to 10. "
            "Something is off with the gauge: it shows more cells than there is fuel - and even an empty tank still shows a cell. "
            "The check reads `fuel`, a whole number from 0 to 10. Find what is wrong and fix it so that: "
            "1) the gauge shows exactly `fuel` cells, each 20 pixels wide and 30 tall, side by side from x 20 and 26 pixels apart; "
            "2) Space burns one fuel and never takes it below 0; "
            "3) R refills the tank to 10 and the gauge follows."
        ),
        starter=_GAUGE,
        solution=_GAUGE_FIXED,
        check=_GAUGE_CHECK,
        hint=(
            "Set fuel = 0 and look at the gauge. Then print(list(range(fuel + 1))) inside draw_gauge() for a few values "
            "of fuel and compare how many numbers you get with how many cells you want."
        ),
    ),
    _step(
        id="pydbg-03-smear",
        title="The smeared square",
        teaches=(
            "Bug class: state that outlives the frame. A canvas keeps every "
            "pixel you paint until something paints over it; a new frame is "
            "not a fresh sheet. So each frame must start by wiping the last "
            "one - and a wipe that runs once, at the top of the file, "
            "happens once. The question that finds it is not 'what does "
            "this line say?' but 'when does this line run?': code at the "
            "top level runs once, as the program loads; code inside a "
            "function runs every time the function is called. Hunt it by "
            "putting print('draw') in draw() and print('setup') at the top "
            "level and counting what comes out; or shrink the program to "
            "only the drawing and see which lines the picture really needs "
            "every frame."
        ),
        goal=(
            "A teal square moves with the arrow keys at 240 pixels a second and stops at the edges of the canvas. "
            "But the picture is a mess: wherever the square has been, a copy of it stays on the screen, so moving paints a long smear instead of moving a square. "
            "The check reads `player`, a dict with x, y, size and speed. Find what is wrong and fix it so that: "
            "1) you only ever see the square where it is now, in every frame - moving or at rest; "
            "2) it still moves at 240 pixels a second at any frame rate and stops at the canvas edges."
        ),
        starter=_TRAILS,
        solution=_TRAILS_FIXED,
        check=_TRAILS_CHECK,
        hint=(
            "Find the lines that paint the dark background and ask when each one runs. A print('draw') inside draw() "
            "tells you every time it runs; try one next to the background lines, too."
        ),
    ),
    _step(
        id="pydbg-04-overhead-rock",
        title="Hit by a rock overhead",
        teaches=(
            "Bug class: half a test. Two boxes overlap only when they "
            "overlap on BOTH axes - across and up-and-down - which takes "
            "four comparisons. A test with only the x pair says 'same "
            "column', which is true of a rock at the top of the screen and "
            "a player at the bottom. Hunt it by turning the question into a "
            "case you can do by hand: put the rock far above the player and "
            "work out what the function should answer (False), then ask "
            "it: print(hits(player, rock)). Try the cases on every side - "
            "above, below, left, right, touching a corner - not only the one "
            "you saw. Print the pieces of a long condition separately, "
            "print(a['x'] < b['x'] + b['w'], ...), to see which part is "
            "True when it should not be. In a terminal, breakpoint() stops "
            "the program there and lets you look at a and b."
        ),
        goal=(
            "A rock falls from the top and the player, a square at the bottom, moves with the arrow keys. Touching the rock costs one of the three lives and the rock starts again from the top; a rock that misses just starts again. "
            "But lives vanish for no reason: every so often, the moment a rock appears high above the player's head, a life is gone though nothing has touched anything. "
            "The check reads `player` and `rock` (dicts with x, y, w and h; the rock also has vy) and `lives`. Find what is wrong and fix it so that: "
            "1) a rock costs a life only when it really touches the player - not when it is above, below or beside it; "
            "2) one rock falling straight at the player costs exactly one life, about 1.5 seconds after it appears, at 30 and at 60 frames a second; "
            "3) after a hit the rock starts again from the top."
        ),
        starter=_ROCK,
        solution=_ROCK_FIXED,
        check=_ROCK_CHECK,
        hint=(
            "Set rock['y'] = 0 by hand (or in a print) and ask the collision function whether a rock at the top of the "
            "screen and a player at the bottom touch. Then read it: which of the four sides of the boxes does it ask about?"
        ),
    ),
    _step(
        id="pydbg-05-red-balloons",
        title="The balloons that stay",
        teaches=(
            "Bug class: changing a list while you loop over it. A for loop "
            "over a list walks an index - 0, 1, 2 - and when you remove an "
            "item, everything after it slides left one place; the item "
            "that slid into the index you just left is never looked at. So "
            "the loop skips every other neighbour, and the bug only shows "
            "when removable items sit next to each other. Hunt it: print(b) "
            "inside the loop to see which items the loop really visits (it "
            "will miss some), and print the list before and after - the "
            "repr shows every dict. The cures: loop over a copy "
            "(list(balloons) or balloons[:]), loop backwards, or build a "
            "list of the keepers with a comprehension and put it back "
            "in place: balloons[:] = [b for b in balloons if ...]. A plain "
            "balloons = [...] inside a function makes a new local name "
            "instead - that needs `global`."
        ),
        goal=(
            "Nine balloons float in a row, seven red and two blue. Pressing C should pop every red balloon and leave the blue ones. "
            "It only half works: after one press some red balloons are gone but others are still floating there - press C again and a few more pop. "
            "The check reads `balloons`, a list of dicts with x, y, r and color ('red' or 'blue'). Find what is wrong and fix it so that: "
            "1) one press of C pops every red balloon, however they are lined up; "
            "2) the blue balloons stay, and a press with nothing red left changes nothing; "
            "3) the screen shows exactly the balloons that are in the list."
        ),
        starter=_BALLOONS,
        solution=_BALLOONS_FIXED,
        check=_BALLOONS_CHECK,
        hint=(
            "Put print(b['x']) at the top of the for loop's body and press C: which balloons does the loop actually visit? "
            "Then print(len(balloons)) after each removal and think about where the next item went."
        ),
    ),
    _step(
        id="pydbg-06-same-spark",
        title="All the sparks in one place",
        teaches=(
            "Bug class: late binding. A lambda does not copy the variables "
            "it uses - it remembers where they live, and looks them up when "
            "it is finally called. Make five lambdas in a loop and by the "
            "time any of them runs the loop is long over, i is 4, and every "
            "one says spawn(4). The same goes for functions made in a loop "
            "for buttons and timers. Hunt it: print(i) inside the function "
            "the lambda calls and see the same number five times, and print "
            "the list the program fills - its repr shows five identical "
            "entries. The cures bind the value NOW: a default argument "
            "(lambda i=i: spawn(i)), functools.partial(spawn, i), or a small "
            "function that makes the callback: def later(i): return "
            "lambda: spawn(i), because each call has its own i."
        ),
        goal=(
            "Five sparks should light up one after another across the screen: the first at once, then one every half second, at x 60, 150, 240, 330 and 420, each a little bigger than the one before. "
            "Instead the sparks appear on time - one every half second - but every one lands in the same place, on top of the others. "
            "The check reads `sparks`, a list of dicts with x, y and r. Find what is wrong and fix it so that: "
            "1) after three seconds there are five sparks at x 60, 150, 240, 330 and 420, left to right; "
            "2) their radii are 6, 9, 12, 15 and 18; "
            "3) they still light up one at a time, at 0, 0.5, 1, 1.5 and 2 seconds."
        ),
        starter=_SPARKS,
        solution=_SPARKS_FIXED,
        check=_SPARKS_CHECK,
        hint=(
            "Put print('spawn', i) at the top of spawn() and watch the numbers go by. What number is in i by the time "
            "the first timer fires, and where was that i when the lambda was made?"
        ),
    ),
    _step(
        id="pydbg-07-time-is-up",
        title="The clock that never stops",
        teaches=(
            "Bug class: scope, and the quiet kind. Assigning to a name "
            "inside a function makes that name local to the whole "
            "function - it does not touch the module-level name of the "
            "same spelling, and Python does not complain, even if you never "
            "read the local. `global state` is the line that says 'this "
            "name belongs to the module'. If the function READS the name "
            "before assigning it (score += 1 with no global), you get an "
            "UnboundLocalError and a traceback: read its last line first, "
            "then the line number it points to. If the function only "
            "assigns, nothing is raised and nothing happens - the bug is "
            "silence. Hunt it: print(state) in draw() and in update() "
            "and compare; look at each function that assigns a module-level "
            "name for its global line, and at which names are listed. A "
            "linter (pyflakes) reports 'local variable assigned to but "
            "never used'."
        ),
        goal=(
            "A five-second clicker: click the big circle to score a point; the clock in the corner counts down. When it reaches 0 the game is over: 'Time is up!' is on the screen and clicks stop scoring. "
            "Nothing is raised and nothing crashes, and everything is right while the clock runs. But when it reaches 0 nothing happens: the clock sits at 0.0, no message, and clicks keep scoring. "
            "The check reads `score`. Find what is wrong and fix it so that: "
            "1) a click on the circle scores a point while there is time left, and a click outside the circle never does; "
            "2) when 5 seconds of game time have passed - at any frame rate - 'Time is up!' is on the screen; "
            "3) after that, clicks on the circle score nothing."
        ),
        starter=_CLOCK,
        solution=_CLOCK_FIXED,
        check=_CLOCK_CHECK,
        hint=(
            "Put print('state is', state) at the top of draw(), and print(state) right after the line that sets it in "
            "update(). Do they agree? Then look at how click() and update() each start."
        ),
    ),
    _step(
        id="pydbg-08-stripe",
        title="A whole column lights up",
        teaches=(
            "Bug class: aliasing. `[0] * 12` makes a list of twelve zeros; "
            "`[[0] * 12] * 8` makes ONE row and a list holding eight "
            "references to it - the * repeats the reference, it does not "
            "copy. Numbers are safe because you cannot change a number in "
            "place, but a row is a list, so setting one cell of 'row 3' "
            "changes every row, and a click lights a whole column. Hunt it: "
            "print(grid[0] is grid[1]) says True when they are the same "
            "list; print the ids with [id(row) for row in grid] (eight "
            "equal numbers); print(grid) after one click and read the "
            "repr. Build each row on its own: [[0] * 12 for _ in range(8)] "
            "runs [0] * 12 afresh for each row. copy.deepcopy keeps the "
            "sharing, so it does not help."
        ),
        goal=(
            "A paint grid: 12 columns by 8 rows of squares, 40 pixels each. Click a square and it lights up (an orange 38 by 38 square); click it again and it goes out. "
            "But a click lights up much more than the square you clicked: a whole stripe of squares through the screen. "
            "The check reads `grid`, the list of rows, read as grid[row][col], each cell 0 or 1. Find what is wrong and fix it so that: "
            "1) one click lights exactly the clicked square; "
            "2) clicking it again puts it out, and only it; "
            "3) every square, corners included, can be lit on its own."
        ),
        starter=_PAINT,
        solution=_PAINT_FIXED,
        check=_PAINT_CHECK,
        hint=(
            "Click once, then print(grid) from toggle() and read it row by row. Then try print(grid[0] is grid[1]) and "
            "look at how the grid is built."
        ),
    ),
    _step(
        id="pydbg-09-doubled-wave",
        title="Twice as many enemies",
        teaches=(
            "Bug class: the mutable default argument. A default value is "
            "made ONCE, when the `def` line runs - not each time the "
            "function is called. A default of [] or {} is therefore one "
            "list, shared by every call that does not pass its own, and "
            "it remembers what earlier calls put in it. Hunt it: "
            "print(make_wave.__defaults__) after a few calls - you will see "
            "the 'default' list growing; print(len(enemies)) and "
            "print(enemies) after each restart, and notice some entries "
            "are old (their y has moved). The cure: default to None and "
            "make the list inside the function - if enemies is None: "
            "enemies = []. (`enemies or []` also works here, but misleads "
            "when an empty list you were handed should be used.) Linters "
            "flag it as B006."
        ),
        goal=(
            "A wave of five enemies starts at the top of the screen and creeps down at 60 pixels a second. R starts the wave again: five fresh enemies at the top, in place of the old ones. "
            "But R does not give a fresh wave: the screen fills up instead. After one press there are ten enemies on the screen, after two there are fifteen - and half of them are already part-way down. "
            "The check reads `enemies`, a list of dicts with x, y, w and h. Find what is wrong and fix it so that: "
            "1) the game starts with 5 enemies at y -20 and x 40, 120, 200, 280 and 360; "
            "2) every press of R, however many and whenever, leaves exactly 5 enemies, all at the top; "
            "3) the new wave then creeps down like the first one."
        ),
        starter=_WAVES,
        solution=_WAVES_FIXED,
        check=_WAVES_CHECK,
        hint=(
            "Press R and print(len(enemies)) afterwards. Then print(make_wave.__defaults__) before and after a call to "
            "make_wave(5): what is that default value, and when was it made?"
        ),
    ),
    _step(
        id="pydbg-10-one-tile-off",
        title="One tile off",
        teaches=(
            "Bug class: division. In Python 3 `/` always gives a float, "
            "`//` divides and rounds DOWN (towards minus infinity), and "
            "int() chops the decimals off (towards zero). For positive "
            "numbers they agree. Below zero they part ways: -10 // 40 is "
            "-1 but int(-10 / 40) is 0 - so a tile number made with "
            "int(x / TILE) is right to the right of the origin and one off "
            "to its left. A / on its own is another trap: tiles[x / 40] is "
            "a float index and raises TypeError: read the traceback, it "
            "names the line and the type. Hunt it: try the numbers in a "
            "print - print(-10 / 40, -10 // 40, int(-10 / 40)) - and test "
            "both sides of zero, and the exact edges (-40, 0, 40), where "
            "an off-by-one hides. The label that prints the value on "
            "screen is your repr here."
        ),
        goal=(
            "A highlight follows the player along a floor made of 40-pixel tiles. The middle of the canvas is x 0: tile 0 is the 40 pixels to its right, tile -1 the 40 pixels to its left, tile -2 the next, and so on. "
            "The blue highlight should sit exactly under the player and the label says which tile ('tile -1'). "
            "On the right half everything is correct, and nothing crashes. But once the player walks to the left of the middle, the highlight and the label lag one tile behind. "
            "The check reads `player`, a dict with x from -240 to 239. Find what is wrong and fix it so that: "
            "1) at every x the highlight and the label show the tile the player is standing in (x -10 is in tile -1, x -40 is in tile -1, x -41 is in tile -2); "
            "2) the highlight is always one 40 by 40 square that snaps to whole tiles."
        ),
        starter=_TILES,
        solution=_TILES_FIXED,
        check=_TILES_CHECK,
        hint=(
            "Walk the player left and watch the label as it crosses the middle. Then print(x, x / TILE, int(x / TILE), "
            "x // TILE) for a few negative x and compare the last two columns."
        ),
    ),
    _step(
        id="pydbg-11-break-your-own",
        title="Break your own",
        teaches=_OPEN_TEACHES,
        goal=(
            "No check here - plant a bug. This is a small working catch game: move the basket, catch the stars. "
            "Add ONE realistic bug that looks right at a glance and runs without an error, describe its symptom in a sentence (never where it is), and hand it to a friend. "
            "Run it, play it, break it, fix it."
        ),
        starter=_CATCH,
        solution=_CATCH,
        check="",
    ),
)
