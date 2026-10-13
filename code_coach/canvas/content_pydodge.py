"""Dodge in Python: the same small game as the first Canvas track, written in Python.

Your Python runs on the server, a frame at a time, and the page draws what
it records - see pyharness/. You write plain top-level Python against one
library:

    from canvas import ctx, WIDTH, HEIGHT, on_frame, keys, on_key_down

so the steps teach the game and the Python that suits it, not JavaScript in
Python clothes: a dict and a dataclass for a thing's fields, `in` on a set of
held keys, min() and max() to clamp, a list comprehension to drop the dead,
`any()` over a generator for a collision, `global` for a name a function
rebinds, f-strings for the score.

As in the JavaScript track, each step starts from the one before, finished,
and its check fails on that starter. A check is Python statements run with
`cc` (frames, press, release, click, rects, texts ...), `expect(ok, message)`,
`near(a, b, within)` and `g`, the learner's own top-level names:
`g.player`, `g.enemies = []`. See pyharness/check.py. Checks play the game
rather than read the code, so any way of writing it that works, passes.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

TRACK = "Dodge (Python)"

#: Prepended to every check. A thing's fields can be a dict's or an object's,
#: so a check reads them with get() and never cares which the learner chose.
_HELPERS = """def get(o, k, default=None):
    if isinstance(o, dict):
        return o.get(k, default)
    return getattr(o, k, default)

"""

_S1 = """from canvas import ctx

ctx.fill_style = 'tomato'
ctx.fill_rect(100, 80, 40, 40)
"""

_S2 = """from canvas import ctx, WIDTH, HEIGHT

ctx.fill_style = '#10141f'
ctx.fill_rect(0, 0, WIDTH, HEIGHT)

ctx.fill_style = 'tomato'
ctx.fill_rect(100, 80, 40, 40)
"""

_S3 = """from canvas import ctx, WIDTH, HEIGHT

player = {'x': 100, 'y': 260, 'size': 32}

ctx.fill_style = '#10141f'
ctx.fill_rect(0, 0, WIDTH, HEIGHT)

ctx.fill_style = '#4fd1c5'
ctx.fill_rect(player['x'], player['y'], player['size'], player['size'])
"""

_DRAW_PLAYER = """def draw():
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)

    ctx.fill_style = '#4fd1c5'
    ctx.fill_rect(player['x'], player['y'], player['size'], player['size'])
"""

_S4 = """from canvas import ctx, WIDTH, HEIGHT, on_frame

player = {'x': 100, 'y': 260, 'size': 32}


def update():
    player['x'] += 2


""" + _DRAW_PLAYER + """

def loop(dt):
    update()
    draw()


on_frame(loop)
"""

_LOOP = """

def loop(dt):
    update(dt)
    draw()


on_frame(loop)
"""

_S5 = """from canvas import ctx, WIDTH, HEIGHT, on_frame

player = {'x': 100, 'y': 260, 'size': 32, 'speed': 240}


def update(dt):
    player['x'] += player['speed'] * dt


""" + _DRAW_PLAYER + _LOOP

_S6 = """from canvas import ctx, WIDTH, HEIGHT, on_frame, keys

player = {'x': 100, 'y': 260, 'size': 32, 'speed': 240}


def update(dt):
    if 'ArrowLeft' in keys:
        player['x'] -= player['speed'] * dt
    if 'ArrowRight' in keys:
        player['x'] += player['speed'] * dt


""" + _DRAW_PLAYER + _LOOP

_MOVE_PLAYER = """    if 'ArrowLeft' in keys:
        player['x'] -= player['speed'] * dt
    if 'ArrowRight' in keys:
        player['x'] += player['speed'] * dt
    player['x'] = max(0, min(WIDTH - player['size'], player['x']))
"""

_S7 = """from canvas import ctx, WIDTH, HEIGHT, on_frame, keys

player = {'x': 100, 'y': 260, 'size': 32, 'speed': 240}


def update(dt):
""" + _MOVE_PLAYER + """

""" + _DRAW_PLAYER + _LOOP

_DRAW_ENEMIES = """def draw():
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)

    ctx.fill_style = '#4fd1c5'
    ctx.fill_rect(player['x'], player['y'], player['size'], player['size'])

    ctx.fill_style = '#f56565'
    for e in enemies:
        ctx.fill_rect(e['x'], e['y'], e['size'], e['size'])
"""

_S8 = """from canvas import ctx, WIDTH, HEIGHT, on_frame, keys

player = {'x': 100, 'y': 260, 'size': 32, 'speed': 240}
enemies = [{'x': 200, 'y': 0, 'size': 24, 'speed': 150}]


def update(dt):
""" + _MOVE_PLAYER + """
    for e in enemies:
        e['y'] += e['speed'] * dt


""" + _DRAW_ENEMIES + _LOOP

_SPAWN = """
    spawn_timer += dt
    if spawn_timer >= 1:
        spawn_timer -= 1
        enemies.append({'x': random.uniform(0, WIDTH - 24), 'y': -24, 'size': 24, 'speed': 150})
    for e in enemies:
        e['y'] += e['speed'] * dt
    enemies = [e for e in enemies if e['y'] < HEIGHT]
"""

_S9 = """import random

from canvas import ctx, WIDTH, HEIGHT, on_frame, keys

player = {'x': 100, 'y': 260, 'size': 32, 'speed': 240}
enemies = []
spawn_timer = 0


def update(dt):
    global spawn_timer, enemies
""" + _MOVE_PLAYER + _SPAWN + """

""" + _DRAW_ENEMIES + _LOOP

_OVERLAPS = """def overlaps(a, b):
    return (a['x'] < b['x'] + b['size'] and b['x'] < a['x'] + a['size'] and
            a['y'] < b['y'] + b['size'] and b['y'] < a['y'] + a['size'])
"""

_S10 = """import random

from canvas import ctx, WIDTH, HEIGHT, on_frame, keys

player = {'x': 100, 'y': 260, 'size': 32, 'speed': 240}
enemies = []
spawn_timer = 0
state = 'playing'


""" + _OVERLAPS + """

def update(dt):
    global spawn_timer, enemies, state
    if state != 'playing':
        return
""" + _MOVE_PLAYER + _SPAWN + """
    if any(overlaps(player, e) for e in enemies):
        state = 'over'


""" + _DRAW_ENEMIES + _LOOP

_DRAW_SCORE = """def draw():
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)

    ctx.fill_style = '#4fd1c5'
    ctx.fill_rect(player['x'], player['y'], player['size'], player['size'])

    ctx.fill_style = '#f56565'
    for e in enemies:
        ctx.fill_rect(e['x'], e['y'], e['size'], e['size'])

    ctx.fill_style = 'white'
    ctx.font = '16px monospace'
    ctx.fill_text(f'Score: {int(score)}', 10, 22)
"""

_S11 = """import random

from canvas import ctx, WIDTH, HEIGHT, on_frame, keys

player = {'x': 100, 'y': 260, 'size': 32, 'speed': 240}
enemies = []
spawn_timer = 0
state = 'playing'
score = 0


""" + _OVERLAPS + """

def update(dt):
    global spawn_timer, enemies, state, score
    if state != 'playing':
        return
""" + _MOVE_PLAYER + _SPAWN + """
    score += dt
    if any(overlaps(player, e) for e in enemies):
        state = 'over'


""" + _DRAW_SCORE + _LOOP

_S12 = """import random

from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down, keys

player = {'x': 100, 'y': 260, 'size': 32, 'speed': 240}
enemies = []
spawn_timer = 0
state = 'playing'
score = 0


def restart():
    global enemies, spawn_timer, score, state
    player['x'] = 100
    enemies = []
    spawn_timer = 0
    score = 0
    state = 'playing'


def key_down(key):
    if key == 'Enter' and state == 'over':
        restart()


on_key_down(key_down)


""" + _OVERLAPS + """

def update(dt):
    global spawn_timer, enemies, state, score
    if state != 'playing':
        return
""" + _MOVE_PLAYER + _SPAWN + """
    score += dt
    if any(overlaps(player, e) for e in enemies):
        state = 'over'


""" + _DRAW_SCORE + """
    if state == 'over':
        ctx.font = '32px monospace'
        ctx.fill_text('Game over', 150, 150)
        ctx.font = '16px monospace'
        ctx.fill_text('Press Enter to play again', 130, 180)
""" + _LOOP


def _step(**fields: object) -> Step:
    """A step on this track: Python, in the Python Dodge track."""
    fields["track"] = TRACK
    fields["language"] = "python"
    check = str(fields.get("check", ""))
    if check:
        fields["check"] = _HELPERS + check
    return Step(**fields)  # type: ignore[arg-type]


PYDODGE_STEPS: tuple[Step, ...] = (
    _step(
        id="pydodge-01-square",
        title="A square on the screen",
        teaches=(
            "A canvas is a grid of pixels you paint with Python. "
            "`from canvas import ctx` gives you the drawing context, and "
            "every drawing call goes through it. x counts from the left "
            "edge and y counts DOWN from the top, so (0, 0) is the top-left "
            "corner, not the bottom. This canvas is 480 wide and 320 tall. "
            "ctx.fill_style sets the colour for what you draw next (a name "
            "like 'tomato' or a hex code, as text), and ctx.fill_rect(x, y, "
            "width, height) paints a rectangle whose top-left corner is at "
            "x, y. Python names are snake_case, so fill_rect, not fillRect."
        ),
        goal="Draw a 40 by 40 square with its top-left corner at x 100, y 80, in any colour.",
        starter="from canvas import ctx\n\n# Your square here.\n",
        solution=_S1,
        check="""
hit = any(r['x'] == 100 and r['y'] == 80 and r['w'] == 40 and r['h'] == 40 for r in cc.rects())
expect(hit, "There is no 40 by 40 square at x 100, y 80 yet. fill_rect takes x, y, width, height - in that order.")
""",
        hint="ctx.fill_style = 'tomato'  then  ctx.fill_rect(100, 80, 40, 40)",
    ),
    _step(
        id="pydodge-02-background",
        title="Paint the background first",
        teaches=(
            "The canvas is painted in order, like layers of paint: whatever "
            "you draw later covers whatever was there. So a scene is drawn "
            "back to front - background first, then the things on it. "
            "WIDTH and HEIGHT (import them from canvas) are the canvas's "
            "size, so ctx.fill_rect(0, 0, WIDTH, HEIGHT) covers all of it "
            "without you writing 480 and 320 into your code. Capital "
            "letters are Python's way of saying 'a constant: look, don't "
            "change'."
        ),
        goal="Fill the whole canvas with a dark colour, then draw the square from step 1 on top of it in a different colour.",
        starter=_S1,
        solution=_S2,
        check="""
rects = cc.rects()
expect(len(rects) >= 2, "Draw two things: the background, then the square.")
bg = rects[0]
expect(bg['x'] == 0 and bg['y'] == 0 and bg['w'] >= 480 and bg['h'] >= 320, "The first thing drawn should cover the whole canvas: ctx.fill_rect(0, 0, WIDTH, HEIGHT).")
sq = next((r for r in rects[1:] if r['x'] == 100 and r['y'] == 80 and r['w'] == 40 and r['h'] == 40), None)
expect(sq is not None, "The square at x 100, y 80 has to be drawn after the background, or the background paints over it.")
expect(sq['fill'] != bg['fill'], "The square is the same colour as the background, so you cannot see it. Set fill_style again before drawing the square.")
""",
        hint="Two pairs of lines: fill_style + fill_rect for the background, then fill_style + fill_rect for the square.",
    ),
    _step(
        id="pydodge-03-player",
        title="The player is a dict",
        teaches=(
            "A game keeps what it knows about each thing in one place. The "
            "quickest Python way is a dict: player = {'x': 100, 'y': 260, "
            "'size': 32}, read as player['x']. Change player['x'] and the "
            "next drawing is somewhere else; nothing else has to know. "
            "There is a tidier way once you have many fields - a "
            "@dataclass (from dataclasses import dataclass; class Player "
            "with x: float, y: float, size: int), read as player.x, where a "
            "typo in a field name is an error instead of a quietly missing "
            "key. This track uses dicts; either works, and the checks "
            "accept both."
        ),
        goal="Make player = {'x': 100, 'y': 260, 'size': 32} and draw the player as a square using its fields, on the background. The old square can go.",
        starter=_S2,
        solution=_S3,
        check="""
expect(hasattr(g, 'player'), "Make a dict called player: player = {'x': 100, 'y': 260, 'size': 32}")
p = g.player
expect(get(p, 'x') == 100 and get(p, 'y') == 260 and get(p, 'size') == 32, "player should start with x 100, y 260 and size 32.")
drawn = any(r['x'] == get(p, 'x') and r['y'] == get(p, 'y') and r['w'] == get(p, 'size') and r['h'] == get(p, 'size') for r in cc.rects())
expect(drawn, "Draw the player from its own fields: ctx.fill_rect(player['x'], player['y'], player['size'], player['size']).")
""",
        hint="ctx.fill_rect(player['x'], player['y'], player['size'], player['size'])",
    ),
    _step(
        id="pydodge-04-loop",
        title="The game loop",
        teaches=(
            "A game is a picture redrawn 60 times a second. You do not "
            "write the loop yourself: you hand a function to on_frame(), "
            "and canvas calls it once a frame, passing dt (more in the next "
            "step - for now your function just has to accept it). Split the "
            "work in two: update() changes the numbers, draw() paints the "
            "whole scene again. Forget the background in draw and every old "
            "square stays on screen, smeared into a line. Pass on_frame the "
            "function itself - on_frame(loop), not on_frame(loop()), which "
            "would run it once and hand over its result."
        ),
        goal="Put the drawing in a draw() function, add update() that moves the player 2 pixels right, and a loop(dt) that calls both. Register it with on_frame(loop).",
        starter=_S3,
        solution=_S4,
        check="""
x0 = get(g.player, 'x')
cc.frames(10)
moved = get(g.player, 'x') - x0
expect(moved != 0, "The player has not moved after 10 frames. Change player['x'] inside a function, and pass that function to on_frame() once to start it.")
expect(near(moved, 20, 0.001), f"After 10 frames the player moved {moved} pixels; it should be 20 - two a frame. Does loop run every frame?")
rects = cc.rects()
expect(len(rects) > 0 and rects[0]['x'] == 0 and rects[0]['y'] == 0 and rects[0]['w'] >= 480 and rects[0]['h'] >= 320, "Each frame should start by painting the background again, or the old squares stay on screen as a smear.")
expect(any(r['x'] == get(g.player, 'x') and r['y'] == get(g.player, 'y') for r in rects), "Each frame should draw the player where it is now.")
""",
        hint="def loop(dt): update(); draw()  and, at the bottom, on_frame(loop)",
    ),
    _step(
        id="pydodge-05-delta-time",
        title="Speed in pixels a second",
        teaches=(
            "Moving 2 pixels a frame means the game runs twice as fast on "
            "a screen that draws 120 frames a second as on one that draws "
            "60. The fix is delta time: on_frame passes your function dt, "
            "the SECONDS since the last frame (a float, about 0.0167 at 60 "
            "frames a second). Move by speed * dt and speed means pixels a "
            "second, whatever the frame rate. Pass dt on - loop(dt) calls "
            "update(dt) - or update has nothing to multiply by."
        ),
        goal="Give player a 'speed' of 240. loop(dt) passes dt to update(dt), which moves the player right by player['speed'] * dt.",
        starter=_S4,
        solution=_S5,
        check="""
expect(get(g.player, 'speed') == 240, "Give player a speed of 240 - pixels a second: {'x': 100, 'y': 260, 'size': 32, 'speed': 240}.")
x0 = get(g.player, 'x')
cc.frames(30, 1 / 30)
slow = get(g.player, 'x') - x0
x0 = get(g.player, 'x')
cc.frames(60, 1 / 60)
fast = get(g.player, 'x') - x0
expect(near(fast, 240, 5), f"In one second at 60 frames a second the player moved {round(fast)} pixels; at speed 240 it should move 240. Move by player['speed'] * dt, with dt in seconds.")
expect(near(slow, 240, 9), f"In one second at 30 frames a second the player moved {round(slow)} pixels, and at 60 it moved {round(fast)}. With delta time both are 240: the frame rate stops mattering.")
""",
        hint="def update(dt): player['x'] += player['speed'] * dt   and   def loop(dt): update(dt); draw()",
    ),
    _step(
        id="pydodge-06-keys",
        title="Arrow keys",
        teaches=(
            "A game wants to know, every frame, what is held right now. "
            "`keys` (import it from canvas) is a set of the names of the "
            "keys held at this moment - 'ArrowLeft', 'ArrowRight', ' ' for "
            "the space bar, 'Enter', 'a' to 'z'. It fills and empties "
            "itself; you only ask it, with `in`: if 'ArrowLeft' in keys. "
            "(A set answers `in` instantly and holds each key once, which "
            "is why it is a set and not a list.) Click the game before "
            "pressing keys, so it has the keyboard."
        ),
        goal="Stop the automatic movement. In update, move the player left while 'ArrowLeft' in keys and right while 'ArrowRight' in keys, at player['speed'].",
        starter=_S5,
        solution=_S6,
        check="""
x0 = get(g.player, 'x')
cc.frames(30)
expect(near(get(g.player, 'x'), x0, 0.01), "The player moves on its own. It should stand still until an arrow key is held.")
cc.press("ArrowRight")
cc.frames(30)
cc.release("ArrowRight")
right = get(g.player, 'x') - x0
expect(near(right, 120, 6), f"Holding ArrowRight for half a second moved the player {round(right)} pixels; it should be about 120 (240 a second). Ask `keys` in update: if 'ArrowRight' in keys.")
x1 = get(g.player, 'x')
cc.frames(30)
expect(near(get(g.player, 'x'), x1, 0.01), "The player kept going after ArrowRight was let go. Is something remembering the key after it came up?")
cc.press("ArrowLeft")
cc.frames(30)
cc.release("ArrowLeft")
expect(near(x1 - get(g.player, 'x'), 120, 6), "ArrowLeft should move the player left at the same speed.")
""",
        hint="if 'ArrowLeft' in keys: player['x'] -= player['speed'] * dt   (and the same for ArrowRight with +=)",
    ),
    _step(
        id="pydodge-07-clamp",
        title="Stay on the screen",
        teaches=(
            "Nothing stops player['x'] going to -500 or 5000; the canvas "
            "just stops showing it. Clamping keeps a number inside a "
            "range, and Python spells it with two built-ins: "
            "max(low, min(high, x)) is x, unless x is below low (then low) "
            "or above high (then high). The player's x is its left edge, "
            "so the right-most it can go is WIDTH - player['size']."
        ),
        goal="After moving, clamp player['x'] so the player never leaves the canvas on either side.",
        starter=_S6,
        solution=_S7,
        check="""
cc.press("ArrowRight")
cc.frames(180)
cc.release("ArrowRight")
x = get(g.player, 'x')
expect(near(x, WIDTH - get(g.player, 'size'), 0.01), f"After three seconds of ArrowRight the player is at x {round(x)}. It should stop with its right edge on the canvas edge: x = WIDTH - player['size'].")
cc.press("ArrowLeft")
cc.frames(180)
cc.release("ArrowLeft")
x = get(g.player, 'x')
expect(near(x, 0, 0.01), f"After three seconds of ArrowLeft the player is at x {round(x)}. It should stop at 0.")
""",
        hint="player['x'] = max(0, min(WIDTH - player['size'], player['x']))",
    ),
    _step(
        id="pydodge-08-enemy",
        title="Something falls",
        teaches=(
            "One enemy could be one more dict, but a game has many, so "
            "they go in a list from the start. Every frame, update moves "
            "each one and draw paints each one - a `for e in enemies:` loop "
            "in both. Enemies fall, so it is their y that grows. Dicts in a "
            "list are shared, not copied: `e` is the enemy itself, so "
            "e['y'] += ... really moves it."
        ),
        goal="Add enemies = [{'x': 200, 'y': 0, 'size': 24, 'speed': 150}]. Each frame, move every enemy down by its speed * dt and draw it in its own colour.",
        starter=_S7,
        solution=_S8,
        check="""
expect(hasattr(g, 'enemies') and isinstance(g.enemies, list) and len(g.enemies) >= 1, "Make a list called enemies with one enemy in it: {'x': 200, 'y': 0, 'size': 24, 'speed': 150}.")
e = g.enemies[0]
y0 = get(e, 'y')
cc.frames(60)
fell = get(e, 'y') - y0
expect(near(fell, 150, 5), f"In one second the enemy fell {round(fell)} pixels; at speed 150 it should fall 150. Move every enemy down by e['speed'] * dt.")
expect(any(near(r['x'], get(e, 'x'), 0.01) and near(r['y'], get(e, 'y'), 0.01) and r['w'] == get(e, 'size') for r in cc.rects()), "Draw every enemy each frame, after the background.")
""",
        hint="In update: for e in enemies: e['y'] += e['speed'] * dt   In draw: for e in enemies: ctx.fill_rect(e['x'], e['y'], e['size'], e['size'])",
    ),
    _step(
        id="pydodge-09-spawn",
        title="Spawn on a timer",
        teaches=(
            "A timer in a game is a number you add dt to. When it passes "
            "the interval, something happens and you take the interval "
            "off (rather than setting it to 0, which throws away the few "
            "milliseconds over and makes the rhythm drift). random.uniform"
            "(low, high) picks a float in a range - `import random` first. "
            "Enemies that have fallen off the bottom should leave the list "
            "or it grows forever: enemies = [e for e in enemies if e['y'] "
            "< HEIGHT] builds a new list of only the ones still on screen. "
            "That line RE-BINDS the name enemies, and a function that "
            "re-binds a top-level name must say so with `global enemies` "
            "- without it Python decides enemies is local to update and "
            "fails with UnboundLocalError. (enemies[:] = [...] changes the "
            "list in place and needs no global.)"
        ),
        goal="Start with enemies = [] and spawn_timer = 0. Every second, append a new enemy at a random x across the canvas, just above the top (y -24). Remove enemies once they fall past the bottom.",
        starter=_S8,
        solution=_S9,
        check="""
expect(hasattr(g, 'enemies') and isinstance(g.enemies, list), "Keep the enemies in a list called enemies.")
seen = {id(e): e for e in g.enemies}
for _ in range(10 * 60):
    cc.frames(1)
    for e in g.enemies:
        seen[id(e)] = e
expect(9 <= len(seen) <= 12, f"In ten seconds {len(seen)} enemies appeared (counting any you started with); one a second makes about ten. Add dt to a timer, and when it reaches 1, take 1 off and append a new enemy.")
for e in seen.values():
    expect(get(e, 'x') >= 0 and get(e, 'x') + get(e, 'size') <= WIDTH, "Every enemy should start fully across the canvas: x from 0 to WIDTH - size. random.uniform(0, WIDTH - 24) does it.")
expect(len(g.enemies) <= 4, f"There are {len(g.enemies)} enemies in the list, some long gone past the bottom. Remove them: enemies = [e for e in enemies if e['y'] < HEIGHT]")
""",
        hint="spawn_timer += dt; if spawn_timer >= 1: spawn_timer -= 1; enemies.append({...})  - and put `global spawn_timer, enemies` first in update.",
    ),
    _step(
        id="pydodge-10-collision",
        title="Hit!",
        teaches=(
            "Two boxes overlap when they overlap on x AND on y. On x: a's "
            "left edge is left of b's right edge (a['x'] < b['x'] + "
            "b['size']) and b's left edge is left of a's right edge. The "
            "same for y. Use < rather than <=, so boxes that only touch "
            "edges do not count. Ask 'does ANY enemy overlap the player?' "
            "with any(overlaps(player, e) for e in enemies) - any() stops "
            "at the first True. A state variable says what the game is "
            "doing - 'playing' or 'over' - and update does nothing once it "
            "is over. state is assigned inside update, so it needs a "
            "`global` too."
        ),
        goal="Add state = 'playing' and a function overlaps(a, b). When any enemy overlaps the player, set state to 'over'; once it is over, update stops moving anything.",
        starter=_S9,
        solution=_S10,
        check="""
expect(hasattr(g, 'state') and g.state == 'playing', "Keep what the game is doing in a variable: state = 'playing'")
p = g.player
px, py, ps = get(p, 'x'), get(p, 'y'), get(p, 'size')
g.enemies = [
    {'x': px + 200, 'y': py, 'size': 24, 'speed': 0},
    {'x': px + ps, 'y': py, 'size': 24, 'speed': 0},
    {'x': px + 8, 'y': py - 100, 'size': 24, 'speed': 0},
]
cc.frames(2)
expect(g.state == 'playing', "The game ended with no enemy overlapping the player - one only touches its right edge, one is far above it. Use < in overlaps, and check x and y both.")
g.enemies = [{'x': px + 8, 'y': py - 8, 'size': 24, 'speed': 0}]
cc.frames(2)
expect(g.state == 'over', "An enemy is sitting on the player and the game carried on. When any enemy overlaps the player, set state = 'over'.")
x = get(g.player, 'x')
cc.press("ArrowRight")
cc.frames(30)
cc.release("ArrowRight")
expect(near(get(g.player, 'x'), x, 0.01), "The player still moves after the game is over. Start update with: if state != 'playing': return")
""",
        hint="if any(overlaps(player, e) for e in enemies): state = 'over'",
    ),
    _step(
        id="pydodge-11-score",
        title="Score",
        teaches=(
            "In Dodge you score by surviving, so the score is time: add dt "
            "while playing. ctx.fill_text(text, x, y) writes on the canvas "
            "in the current fill_style and font; y is the text's baseline, "
            "so text at y 0 is off the top. Build the text with an "
            "f-string - f'Score: {int(score)}' - and int() to show whole "
            "seconds, not 3.1666666. score is re-bound by update (score += "
            "dt), so add it to the `global` line."
        ),
        goal="Add score = 0, add dt to it each frame while playing, and write it in the top-left corner each frame with ctx.fill_text.",
        starter=_S10,
        solution=_S11,
        check="""
expect(hasattr(g, 'score') and isinstance(g.score, (int, float)), "Keep the score in a variable: score = 0")
g.enemies = []
s0 = g.score
cc.frames(60)
gained = g.score - s0
expect(near(gained, 1, 0.05), f"One second of play added {gained:.2f} to the score; it should add 1. Add dt to it in update.")
cc.frames(60)
shown = {str(int(g.score)), str(round(g.score))}
expect(any(s in t for t in cc.texts() for s in shown), f"Write the score on the screen every frame with ctx.fill_text - it should show {int(g.score)} now.")
""",
        hint="ctx.fill_style = 'white'; ctx.font = '16px monospace'; ctx.fill_text(f'Score: {int(score)}', 10, 22)",
    ),
    _step(
        id="pydodge-12-restart",
        title="Game over, and again",
        teaches=(
            "A finished game says it is over and lets you go again. The "
            "restart puts back everything that changed during play - "
            "position, enemies, timers, score, state - which is exactly "
            "the list of names update re-binds, plus the player's fields. "
            "Keys that do something once (Enter to restart) are events, "
            "not held keys: on_key_down(fn) calls fn(key) when a key goes "
            "down, and `keys` stays for what is held."
        ),
        goal="When the game is over, write 'Game over' on the screen. Pressing Enter then starts a new game: player back to x 100, no enemies, score 0, state 'playing'.",
        starter=_S11,
        solution=_S12,
        check="""
import re

g.enemies = []
cc.frames(30)
g.enemies = [{'x': get(g.player, 'x'), 'y': get(g.player, 'y'), 'size': 24, 'speed': 0}]
cc.frames(2)
expect(g.state == 'over', "Put an enemy on the player and the game should end - that part is from step 10.")
expect(any(re.search('game over', t, re.I) for t in cc.texts()), "When the game is over, write 'Game over' on the screen.")
cc.press("Enter")
cc.frames(2)
cc.release("Enter")
expect(g.state == 'playing', "Pressing Enter after a game over should start a new game: state back to 'playing'. Clear the enemies too, or the one on the player ends it again at once.")
expect(g.score < 0.1, "A new game starts with the score back at 0.")
expect(len(g.enemies) <= 1, "A new game starts with no enemies - empty the list.")
expect(not any(re.search('game over', t, re.I) for t in cc.texts()), "'Game over' is still on the screen after the restart.")
""",
        hint="def key_down(key): if key == 'Enter' and state == 'over': restart()  - then on_key_down(key_down)",
    ),
    _step(
        id="pydodge-13-yours",
        title="Now it's yours",
        teaches=(
            "That is a whole game: loop, time, input, a list of things, "
            "spawning, collision, score and restart. Every bigger game is "
            "more of the same parts. Some things to try, roughly easiest "
            "first: make enemies fall faster as the score goes up; give "
            "enemies different sizes and speeds; three lives instead of "
            "one; a high score kept across restarts; a pause on 'p' "
            "(another state); dodging on both axes with ArrowUp and "
            "ArrowDown; coins to collect that add to the score. When the "
            "dicts get crowded, turn Player and Enemy into @dataclass "
            "classes - or try after(2, fn) and every(5, fn), which call a "
            "function later or over and over, on game time."
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_S12,
        solution=_S12,
        check="",
    ),
)
