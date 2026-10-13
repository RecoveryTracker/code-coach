"""Snake in Python: the grid game of the JavaScript Snake track, taught the Python way.

Not a transliteration. The game is the same - tile coordinates, a snake that
is a sequence of cells, a fixed timestep, a direction that waits for the next
tick and cannot turn back, food on a free cell, growth, wall and self
collision, a score, a restart - but the parts are Python's own:

  * a cell is a tuple `(col, row)`: immutable, hashable (so it can live in a
    set), compared by value with `==`, and unpacked with `x, y = head`
  * the body is a `collections.deque` (appendleft and pop are both instant);
    a list with insert(0, ...) and slicing does the same job, and the checks
    accept either
  * `set(snake)` for self-collision, a set difference for the free cells,
    `random.choice(sorted(free))` (a set is not a sequence: a good TypeError)
  * a dict of direction vectors, `DIRS`
  * `match` for the keys, once there are two kinds of key to tell apart
  * `global` where a function re-binds a top-level name - and what Python
    does when it is missing (UnboundLocalError, or a quiet local variable)

As in the other tracks, each step starts from the one before, finished, and a
check plays the game rather than reading the code. The checks read these
top-level names, and set them: snake, direction, next_dir, food, state,
score (and call spawn_food()). The body may be a list or a deque: checks only
ever look at `list(g.snake)`, and put a new body back as the same type.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

TRACK = "Snake (Python)"

# -- Shared check helpers ---------------------------------------------------

#: Prepended to every check that plays the snake: put it somewhere, and wait
#: for one move however the learner keeps time. `place` gives g.snake back as
#: the type it already is (a list or a deque), so either body works.
_HELPERS = """
def cells():
    return list(g.snake)


def at():
    return cells()[0]


def tick(dt=1 / 60):
    before = at()
    for _ in range(30):
        if at() != before:
            return
        cc.frames(1, dt)


def place(body, d):
    g.snake = type(g.snake)(body)
    g.direction = d
    if 'next_dir' in g:
        g.next_dir = d
    if 'state' in g:
        g.state = 'playing'


def steer(*held, dt=1 / 60):
    for k in held:
        cc.press(k)
    tick(dt)
    for k in held:
        cc.release(k)


"""

# -- The programs -----------------------------------------------------------

_IMP1 = "from canvas import ctx, WIDTH, HEIGHT, on_frame"
_IMP3 = "from collections import deque\n\nfrom canvas import ctx, WIDTH, HEIGHT, on_frame"
_IMP4 = "from collections import deque\n\nfrom canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down"
_IMP6 = (
    "import random\nfrom collections import deque\n\n"
    "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down"
)

_GRID = "CELL = 20\nCOLS = WIDTH // CELL\nROWS = HEIGHT // CELL"
_TICK = "TICK = 0.12"
_DIRS = """DIRS = {
    'ArrowUp': (0, -1),
    'ArrowDown': (0, 1),
    'ArrowLeft': (-1, 0),
    'ArrowRight': (1, 0),
}"""
_START = "START = ((12, 8), (11, 8), (10, 8))"

_DRAW_CELL = """def draw_cell(col, row, color):
    ctx.fill_style = color
    ctx.fill_rect(col * CELL, row * CELL, CELL - 1, CELL - 1)"""

_UPDATE_NOTHING = """def update(dt):
    pass"""

_UPDATE_TICK = """def update(dt):
    global acc
    acc += dt
    while acc >= TICK:
        acc -= TICK
        step()"""

_UPDATE_GUARDED = """def update(dt):
    global acc
    if state != 'playing':
        return
    acc += dt
    while acc >= TICK:
        acc -= TICK
        step()"""

_STEP3 = """def step():
    x, y = snake[0]
    dx, dy = direction
    snake.appendleft((x + dx, y + dy))
    snake.pop()"""

_STEP4 = """def step():
    global direction
    direction = next_dir
    x, y = snake[0]
    dx, dy = direction
    snake.appendleft((x + dx, y + dy))
    snake.pop()"""

_STEP7 = """def step():
    global direction
    direction = next_dir
    x, y = snake[0]
    dx, dy = direction
    head = (x + dx, y + dy)
    snake.appendleft(head)
    if head == food:
        spawn_food()
    else:
        snake.pop()"""

_STEP8 = """def step():
    global direction, state
    direction = next_dir
    x, y = snake[0]
    dx, dy = direction
    head = (x + dx, y + dy)
    col, row = head
    if not (0 <= col < COLS and 0 <= row < ROWS):
        state = 'over'
        return
    snake.appendleft(head)
    if head == food:
        spawn_food()
    else:
        snake.pop()"""

_STEP9 = """def step():
    global direction, state
    direction = next_dir
    x, y = snake[0]
    dx, dy = direction
    head = (x + dx, y + dy)
    eating = head == food
    occupied = set(snake)
    if not eating:
        occupied.discard(snake[-1])
    col, row = head
    if not (0 <= col < COLS and 0 <= row < ROWS) or head in occupied:
        state = 'over'
        return
    snake.appendleft(head)
    if eating:
        spawn_food()
    else:
        snake.pop()"""

_STEP10 = """def step():
    global direction, state, score
    direction = next_dir
    x, y = snake[0]
    dx, dy = direction
    head = (x + dx, y + dy)
    eating = head == food
    occupied = set(snake)
    if not eating:
        occupied.discard(snake[-1])
    col, row = head
    if not (0 <= col < COLS and 0 <= row < ROWS) or head in occupied:
        state = 'over'
        return
    snake.appendleft(head)
    if eating:
        score += 10
        spawn_food()
    else:
        snake.pop()"""

_SPAWN = """def spawn_food():
    global food
    cells = {(col, row) for col in range(COLS) for row in range(ROWS)}
    free = cells - set(snake)
    food = random.choice(sorted(free))


spawn_food()"""

_RESET = """def reset():
    global snake, direction, next_dir, acc, score, state
    snake = deque(START)
    direction = (1, 0)
    next_dir = (1, 0)
    acc = 0
    score = 0
    state = 'playing'
    spawn_food()"""

_KEYS4 = """def key_down(key):
    global next_dir
    if key in DIRS:
        next_dir = DIRS[key]


on_key_down(key_down)"""

_KEYS5 = """def key_down(key):
    global next_dir
    if key in DIRS:
        dx, dy = direction
        if DIRS[key] != (-dx, -dy):
            next_dir = DIRS[key]


on_key_down(key_down)"""

_KEYS11 = """def key_down(key):
    global next_dir
    match key:
        case 'Enter' if state == 'over':
            reset()
        case 'ArrowUp' | 'ArrowDown' | 'ArrowLeft' | 'ArrowRight':
            dx, dy = direction
            if DIRS[key] != (-dx, -dy):
                next_dir = DIRS[key]


on_key_down(key_down)"""

_LOOP = """def loop(dt):
    update(dt)
    draw()


on_frame(loop)"""

_D_BG = "    ctx.fill_style = '#10141f'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n"
_D_TILE = "    draw_cell(3, 2, '#4fd1c5')\n"
_D_FOOD = "    draw_cell(*food, '#fc8181')\n"
_D_SNAKE = "    for col, row in snake:\n        draw_cell(col, row, '#68d391')\n"
_D_SCORE = (
    "    ctx.fill_style = 'white'\n    ctx.font = '16px monospace'\n"
    "    ctx.fill_text(f'Score: {score}', 10, 20)\n"
)
_D_OVER = (
    "    if state == 'over':\n        ctx.fill_style = 'white'\n        ctx.font = '32px monospace'\n"
    "        ctx.fill_text('Game over', 150, 170)\n"
)
_D_OVER_AGAIN = (
    "    if state == 'over':\n        ctx.fill_style = 'white'\n        ctx.font = '32px monospace'\n"
    "        ctx.fill_text('Game over', 150, 170)\n"
    "        ctx.font = '16px monospace'\n        ctx.fill_text('Press Enter to play again', 120, 200)\n"
)


def _draw(*parts: str) -> str:
    return "def draw():\n" + "".join(parts)


def _program(head: str, *defs: str) -> str:
    """One whole program: the imports and names on top, then each block, two blank lines apart."""
    return head.strip("\n") + "\n\n\n" + "\n\n\n".join(d.strip("\n") for d in defs) + "\n"


_SNAKE_LIST = "snake = [(12, 8), (11, 8), (10, 8)]"
_SNAKE_DEQUE = "snake = deque([(12, 8), (11, 8), (10, 8)])"

_P0 = _program(_IMP1, _UPDATE_NOTHING, _draw(_D_BG), _LOOP)

_P1 = _program(
    _IMP1 + "\n\n" + _GRID,
    _DRAW_CELL, _UPDATE_NOTHING, _draw(_D_BG, _D_TILE), _LOOP,
)

_P2 = _program(
    _IMP1 + "\n\n" + _GRID + "\n\n" + _SNAKE_LIST,
    _DRAW_CELL, _UPDATE_NOTHING, _draw(_D_BG, _D_SNAKE), _LOOP,
)

_STATE3 = _GRID + "\n" + _TICK + "\n\n" + _SNAKE_DEQUE + "\ndirection = (1, 0)\nacc = 0"
_P3 = _program(
    _IMP3 + "\n\n" + _STATE3,
    _DRAW_CELL, _STEP3, _UPDATE_TICK, _draw(_D_BG, _D_SNAKE), _LOOP,
)

_STATE4 = (
    _GRID + "\n" + _TICK + "\n" + _DIRS + "\n\n" + _SNAKE_DEQUE
    + "\ndirection = (1, 0)\nnext_dir = (1, 0)\nacc = 0"
)
_P4 = _program(
    _IMP4 + "\n\n" + _STATE4,
    _DRAW_CELL, _STEP4, _KEYS4, _UPDATE_TICK, _draw(_D_BG, _D_SNAKE), _LOOP,
)

_P5 = _program(
    _IMP4 + "\n\n" + _STATE4,
    _DRAW_CELL, _STEP4, _KEYS5, _UPDATE_TICK, _draw(_D_BG, _D_SNAKE), _LOOP,
)

_STATE6 = _STATE4 + "\nfood = None"
_P6 = _program(
    _IMP6 + "\n\n" + _STATE6,
    _DRAW_CELL, _SPAWN, _STEP4, _KEYS5, _UPDATE_TICK, _draw(_D_BG, _D_FOOD, _D_SNAKE), _LOOP,
)

_P7 = _program(
    _IMP6 + "\n\n" + _STATE6,
    _DRAW_CELL, _SPAWN, _STEP7, _KEYS5, _UPDATE_TICK, _draw(_D_BG, _D_FOOD, _D_SNAKE), _LOOP,
)

_STATE8 = _STATE6 + "\nstate = 'playing'"
_P8 = _program(
    _IMP6 + "\n\n" + _STATE8,
    _DRAW_CELL, _SPAWN, _STEP8, _KEYS5, _UPDATE_GUARDED,
    _draw(_D_BG, _D_FOOD, _D_SNAKE, _D_OVER), _LOOP,
)

_P9 = _program(
    _IMP6 + "\n\n" + _STATE8,
    _DRAW_CELL, _SPAWN, _STEP9, _KEYS5, _UPDATE_GUARDED,
    _draw(_D_BG, _D_FOOD, _D_SNAKE, _D_OVER), _LOOP,
)

_STATE10 = _STATE8 + "\nscore = 0"
_P10 = _program(
    _IMP6 + "\n\n" + _STATE10,
    _DRAW_CELL, _SPAWN, _STEP10, _KEYS5, _UPDATE_GUARDED,
    _draw(_D_BG, _D_FOOD, _D_SNAKE, _D_SCORE, _D_OVER), _LOOP,
)

_STATE11 = (
    _GRID + "\n" + _TICK + "\n" + _DIRS + "\n" + _START + "\n\n"
    + "snake = deque(START)\ndirection = (1, 0)\nnext_dir = (1, 0)\nacc = 0\n"
    + "food = None\nstate = 'playing'\nscore = 0"
)
_P11 = _program(
    _IMP6 + "\n\n" + _STATE11,
    _DRAW_CELL, _SPAWN, _STEP10, _RESET, _KEYS11, _UPDATE_GUARDED,
    _draw(_D_BG, _D_FOOD, _D_SNAKE, _D_SCORE, _D_OVER_AGAIN), _LOOP,
)

# -- The checks ---------------------------------------------------------------

_CHECK1 = """
expect(hasattr(g, 'CELL') and g.CELL == 20, "Add CELL = 20 - the size of one tile in pixels.")
cols, rows = getattr(g, 'COLS', None), getattr(g, 'ROWS', None)
expect(cols == 24 and rows == 16, f"The grid is {cols} by {rows}; a 480 by 320 canvas of 20 pixel tiles is 24 by 16. Work them out from the canvas: COLS = WIDTH // CELL.")
expect(isinstance(cols, int) and isinstance(rows, int), f"COLS and ROWS should be whole numbers, but they are {cols!r} and {rows!r}: / always gives a float in Python. Use // to divide and keep a whole number.")
expect(callable(getattr(g, 'draw_cell', None)), "Write def draw_cell(col, row, color) that fills one tile.")
cc.frames(1)
rects = cc.rects()
bg = next((i for i, r in enumerate(rects) if r['x'] == 0 and r['y'] == 0 and r['w'] >= WIDTH and r['h'] >= HEIGHT), None)
tile = next((i for i, r in enumerate(rects) if r['x'] == 60 and r['y'] == 40), None)
expect(tile is not None, "Draw a tile at column 3, row 2 each frame: draw_cell(3, 2, ...) inside draw(), after the background. (Column 3 is pixel x 60, row 2 is y 40.)")
expect(bg is not None and tile > bg, "The tile has to be drawn after the background, or the background paints over it.")
g.draw_cell(7, 4, 'orange')
r = next((q for q in cc.rects() if q['x'] == 140 and q['y'] == 80), None)
expect(r is not None, "draw_cell(7, 4, ...) should fill a tile at pixel x 140, y 80: column * CELL, row * CELL.")
expect(g.CELL - 2 <= r['w'] <= g.CELL and g.CELL - 2 <= r['h'] <= g.CELL, "A tile should be about CELL pixels across (CELL - 1 leaves a thin line between tiles).")
expect(r['fill'] == 'orange', "draw_cell should fill the tile with the colour it is given.")
"""

_CHECK2 = _HELPERS + """
import collections

expect(hasattr(g, 'snake') and isinstance(g.snake, (list, collections.deque)), "Make a list called snake: snake = [(12, 8), ...]")
body = cells()
expect(len(body) == 3, f"The snake has {len(body)} cells; start it with 3.")
expect(all(isinstance(c, tuple) for c in body), "Each cell is a tuple - round brackets, (col, row) - not a list or a dict. A tuple cannot change and can go in a set later.")
expect(body[0] == (12, 8), "The head is snake[0], and it starts at column 12, row 8 (in tiles, not pixels).")
expect(body[1] == (11, 8) and body[2] == (10, 8), "The body trails behind the head, to the left: (11, 8) then (10, 8).")
cc.frames(1)
drawn = cc.rects()
for col, row in body:
    expect(any(q['x'] == col * g.CELL and q['y'] == row * g.CELL for q in drawn), f"Draw every cell of the snake each frame - there is nothing at column {col}, row {row}. A loop over snake does it: for col, row in snake:")
expect(not any(q['x'] == 60 and q['y'] == 40 for q in drawn), "The test tile at column 3, row 2 is still being drawn. Take it out.")
"""

_CHECK3 = _HELPERS + """
body = cells()
expect(len(body) == 3, "Start with the three-cell snake.")
cc.frames(1)
expect(at() == (12, 8), "The snake moved in the very first frame. It should move once per tick - every 0.12 seconds - not once per frame.")
cc.frames(299)
moved = at()[0] - 12
expect(40 <= moved <= 43, f"After five seconds the head moved {moved} cells along; a tick every 0.12 seconds is about 42. Add dt to acc each frame and step while acc >= TICK, taking TICK off each time (acc -= TICK, not acc = 0, which throws the leftover time away).")
expect(at()[1] == 8, "Heading right, direction (1, 0), the head's row should not change.")
cc.frames(150, 1 / 30)
x = at()[0]
moved2 = x - 12 - moved
expect(40 <= moved2 <= 43, f"On a slower screen (30 frames a second) the head moved {moved2} cells in five seconds; it should still be about 42. Count time with dt, not frames.")
cc.frames(20, 0.25)
moved3 = at()[0] - x
expect(40 <= moved3 <= 43, f"When a frame lasts a quarter of a second the head moved {moved3} cells in five seconds, not about 42. One long frame can hold more than one tick: use `while acc >= TICK`, not `if`.")
body = cells()
expect(len(body) == 3, f"The snake is {len(body)} cells long now; it should slide, not grow - take the tail off after adding a head.")
expect(all(isinstance(c, tuple) and len(c) == 2 for c in body), "Each cell should still be a tuple (col, row): snake.appendleft((x + dx, y + dy)).")
for a, b in zip(body, body[1:]):
    gap = abs(a[0] - b[0]) + abs(a[1] - b[1])
    expect(gap == 1, "Each cell should sit right next to the one before it - add the new head at the front with appendleft, and take the tail with pop.")
"""

_R3 = "[(12, 8), (11, 8), (10, 8)]"

_CHECK4 = _HELPERS + """
for dt in (1 / 60, 1 / 30):
    place(%(r3)s, (1, 0))
    cc.press('q')
    cc.release('q')
    steer('ArrowDown', dt=dt)
    expect(at() == (12, 9), f"After pressing ArrowDown the head should step down a row, to (12, 9); it is at {at()}. y grows downwards, so down is (0, 1).")
    steer('ArrowLeft', dt=dt)
    expect(at() == (11, 9), f"After ArrowLeft the head should step left, to (11, 9); it is at {at()}.")
    steer('ArrowUp', dt=dt)
    expect(at() == (11, 8), f"After ArrowUp the head should step up, to (11, 8); it is at {at()}. Up is (0, -1).")
    steer('ArrowRight', dt=dt)
    expect(at() == (12, 8), f"After ArrowRight the head should step right, to (12, 8); it is at {at()}.")
    expect(len(cells()) == 3, "Turning should not change the snake's length.")
""" % {"r3": _R3}

_CHECK5 = _HELPERS + """
for dt in (1 / 60, 1 / 30):
    place(%(r3)s, (1, 0))
    steer('ArrowLeft', dt=dt)
    expect(at() == (13, 8), f"Heading right, ArrowLeft was obeyed and the head is at {at()} - on top of the body. Ignore a turn that is exactly opposite to direction.")
    place(%(r3)s, (1, 0))
    steer('ArrowUp', 'ArrowLeft', dt=dt)
    expect(at() == (12, 7), f"Up then Left within one tick sent the head to {at()}. Left is the opposite of the way the snake LAST MOVED (right), so it is still ignored - compare with direction, not next_dir.")
    steer('ArrowLeft', dt=dt)
    expect(at() == (11, 7), f"After moving up, a turn to the left is allowed; the head is at {at()} and should be at (11, 7).")
""" % {"r3": _R3}

_CHECK6 = _HELPERS + """
expect(callable(getattr(g, 'spawn_food', None)), "Write def spawn_food() that puts a new (col, row) tuple into food.")
expect(getattr(g, 'food', None) is not None, "Call spawn_food() when the game starts, so there is food to find.")


def legal(f):
    return (isinstance(f, tuple) and len(f) == 2 and all(isinstance(v, int) for v in f)
            and 0 <= f[0] < g.COLS and 0 <= f[1] < g.ROWS)


expect(legal(g.food), f"Food is a (col, row) tuple of whole numbers inside the grid: col from 0 to COLS - 1, row from 0 to ROWS - 1. Yours is {g.food!r}.")
expect(g.food not in cells(), "The first food landed on the snake.")
cc.frames(1)
fc, fr = g.food
expect(any(r['x'] == fc * g.CELL and r['y'] == fr * g.CELL for r in cc.rects()), "Draw the food each frame, in its own colour.")
top = [(c, r) for r in range(8) for c in range(g.COLS)]
place(top, (1, 0))
seen = set()
for _ in range(200):
    g.spawn_food()
    expect(legal(g.food), f"Food landed at {g.food!r} - outside the grid. The cells are range(COLS) by range(ROWS): column COLS itself is off the edge.")
    expect(g.food not in top, "With the snake filling the top half of the grid, food landed on it. Only choose from the cells the snake is not on.")
    seen.add(g.food)
expect(len(seen) > 20, "The food keeps landing in the same few places - choose with random.choice.")
"""

_CHECK7 = _HELPERS + """
place([(10, 8), (9, 8), (8, 8)], (1, 0))
g.food = (11, 8)
tick()
expect(at() == (11, 8), f"The head should step onto the food at column 11; it is at {at()}.")
expect(len(cells()) == 4, f"The snake ate and is {len(cells())} cells long; it should be 4. When the head lands on the food, do not remove the tail. (Compare cells with ==; `is` asks whether two names are the very same object, and two tuples built apart never are.)")
expect(cells()[3] == (8, 8), "A snake that grows keeps its tail where it was; only the head moves.")
expect(g.food != (11, 8) and g.food not in cells(), "After eating, call spawn_food() so there is new food, and not under the snake.")
g.food = (0, 0)
tick()
expect(len(cells()) == 4, f"A step that does not eat should leave the length alone; the snake is {len(cells())} now. Take the tail off unless it ate.")
expect(at() == (12, 8), "The snake should keep moving after it eats.")
"""

_CHECK8 = _HELPERS + """
import re

expect(getattr(g, 'state', None) == 'playing', "Keep what the game is doing in a variable: state = 'playing'")


def inside(c):
    return 0 <= c[0] < g.COLS and 0 <= c[1] < g.ROWS


walls = [
    ("right", [(22, 8), (21, 8), (20, 8)], (1, 0)),
    ("left", [(1, 8), (2, 8), (3, 8)], (-1, 0)),
    ("top", [(12, 1), (12, 2), (12, 3)], (0, -1)),
    ("bottom", [(12, 14), (12, 13), (12, 12)], (0, 1)),
]
for name, body, d in walls:
    place(body, d)
    g.food = (0, 15)
    tick()
    expect(g.state == 'playing', f"Moving onto the {name} edge cell is still legal, but the game ended there. The edge cells are 0 and COLS - 1 (or ROWS - 1): the wall is one step further.")
    tick()
    expect(g.state == 'over', f"The snake ran into the {name} wall and state is {g.state!r}. When the new head is off the grid (col < 0, col >= COLS, row < 0 or row >= ROWS), set state to 'over'.")
    expect(inside(at()), f"The head is at {at()} - outside the grid. Test the new head before adding it to the snake.")
frozen = cells()
g.next_dir = (0, -1)
g.direction = (0, -1)
cc.frames(60)
expect(cells() == frozen, "After game over the snake should stop moving - even if a key has just changed its direction. Start update with: if state != 'playing': return")
expect(any(re.search('game over', t, re.I) for t in cc.texts()), "When the game is over, say so on the screen.")
"""

_CHECK9 = _HELPERS + """
place(%(r3)s, (1, 0))
g.food = (20, 12)
tick()
expect(g.state == 'playing' and at() == (13, 8), "A snake just moving along ended the game. Test the new head against the body before it is added, or the head always finds itself.")
place([(5, 5), (6, 5), (6, 6), (5, 6), (4, 6)], (0, 1))
g.food = (20, 12)
tick()
expect(g.state == 'over', f"The head turned down into its own body at (5, 6) and state is {g.state!r}. If the new head is on a snake cell, set state to 'over'.")
place([(5, 5), (6, 5), (6, 6), (5, 6)], (0, 1))
g.food = (20, 12)
tick()
expect(g.state == 'playing' and at() == (5, 6) and len(cells()) == 4, "The head stepped into the cell the tail was leaving, and the game ended. The tail moves away on the same step, so it is safe - leave it out of the cells you test, unless the snake is eating (then the tail stays).")
place([(5, 5), (6, 5), (6, 6), (5, 6)], (0, 1))
g.food = (5, 6)
tick()
expect(g.state == 'over', "The snake ate on the same step its head reached the tail's cell. When it eats, the tail stays, so that cell is still body: game over.")
""" % {"r3": _R3}

_CHECK10 = _HELPERS + """
import re

expect(getattr(g, 'score', None) == 0, "Start with score = 0")
cc.frames(1)
expect(any(re.search('score', t, re.I) and '0' in t for t in cc.texts()), "Show the score on the screen from the start: it should say Score: 0.")
place([(10, 8), (9, 8), (8, 8)], (1, 0))
g.food = (11, 8)
tick()
expect(g.score == 10, f"One piece of food is worth 10; the score is {g.score}.")
cc.frames(1)
expect(any('10' in t for t in cc.texts()), "Show the new score on the screen.")
g.food = (0, 0)
tick()
expect(g.score == 10, f"A step that eats nothing scored: the score is {g.score}. Only eating adds to it.")
"""

_CHECK11 = _HELPERS + """
import re

place([(12, 1), (12, 2), (12, 3)], (0, -1))
g.food = (20, 12)
g.score = 30
cc.press('Enter')
cc.release('Enter')
expect(g.score == 30 and at() == (12, 1), "Enter in the middle of a game restarted it. Only restart when state is 'over'.")
tick()
tick()
expect(g.state == 'over', "The snake should have hit the top wall.")
cc.frames(1)
expect(any(re.search('enter', t, re.I) for t in cc.texts()), "On the game-over screen, tell the player how to go again: 'Press Enter to play again'.")
cc.press('ArrowLeft')
cc.release('ArrowLeft')
expect(g.state == 'over', "A key other than Enter restarted the game. Only Enter should.")
g.food = (11, 8)
cc.press('Enter')
cc.release('Enter')
expect(g.state == 'playing', f"Pressing Enter after game over should start a new game; state is {g.state!r}.")
expect(g.score == 0, f"A new game should start with a score of 0; it is {g.score}.")
body = cells()
expect(len(body) == 3 and body[0] == (12, 8), "A new game starts with the three-cell snake, head at (12, 8).")
expect(g.food not in body, "The new food should not be on the new snake.")
cc.frames(1)
expect(not any(re.search('game over', t, re.I) for t in cc.texts()), "'Game over' is still on the screen after the restart.")
steer('ArrowLeft')
expect(at() == (13, 8), f"The new snake should set off to the right, from (12, 8) to (13, 8), and ignore a turn straight back; its head is at {at()}. Put direction and next_dir back to (1, 0).")
"""


def _step(**fields: object) -> Step:
    """A step on this track: Python, in the Python Snake track."""
    fields["track"] = TRACK
    fields["language"] = "python"
    return Step(**fields)  # type: ignore[arg-type]


PYSNAKE_STEPS: tuple[Step, ...] = (
    _step(
        id="pysnake-01-tiles",
        title="Tiles, not pixels",
        teaches=(
            "Snake lives on a grid, so think in tiles: a cell is a column "
            "and a row, and only when you draw does it become pixels - "
            "column * CELL, row * CELL. Keep one CELL size and work the "
            "number of columns and rows out from the canvas: COLS = WIDTH "
            "// CELL. Use // there, not /. In Python / always gives a "
            "float (24.0), and range(24.0) is a TypeError; // divides and "
            "keeps the whole number, 24. Capital letters mark a constant. "
            "Everything else in the game is whole numbers - you cannot be "
            "at column 3.4."
        ),
        goal="Add CELL = 20, COLS and ROWS worked out from WIDTH and HEIGHT with //, and draw_cell(col, row, color), which fills one tile. Draw a tile at column 3, row 2 each frame, after the background.",
        starter=_P0,
        solution=_P1,
        check=_CHECK1,
        hint="def draw_cell(col, row, color): ctx.fill_style = color; ctx.fill_rect(col * CELL, row * CELL, CELL - 1, CELL - 1)   then draw_cell(3, 2, '#4fd1c5') in draw().",
    ),
    _step(
        id="pysnake-02-snake",
        title="A snake is a list of tuples",
        teaches=(
            "The snake is a list of cells, head first: snake[0] is the "
            "head and snake[-1] the tail (a negative index counts from the "
            "end). Each cell is a tuple (col, row) - round brackets, not "
            "square. A tuple cannot be changed once made, which makes it "
            "hashable: it can go in a set or be a dict key, and a list "
            "cannot (set([[1, 2]]) is a TypeError). Two tuples with the "
            "same numbers are ==. And a tuple unpacks: col, row = cell, "
            "which is what `for col, row in snake:` does for every cell. "
            "Nothing else is stored - no direction per segment, no pixels."
        ),
        goal="Make snake, a top-level list of three (col, row) tuples, head first: (12, 8), (11, 8), (10, 8). Draw every cell each frame and take out the test tile.",
        starter=_P1,
        solution=_P2,
        check=_CHECK2,
        hint="snake = [(12, 8), (11, 8), (10, 8)]   and in draw():  for col, row in snake: draw_cell(col, row, '#68d391')",
    ),
    _step(
        id="pysnake-03-tick",
        title="Move on a tick",
        teaches=(
            "A snake that jumped a cell every frame would race on a fast "
            "screen and crawl on a slow one. Give it its own clock: add "
            "each frame's dt to an accumulator, acc, and while acc holds a "
            "whole TICK, take TICK off it and step once. Taking TICK off "
            "(not setting acc to 0) keeps the leftover, so the speed is "
            "right however long frames take, and `while` (not `if`) lets "
            "one long frame step twice. acc += dt re-binds a top-level "
            "name, so the function needs `global acc` - without it Python "
            "decides acc is local and fails with UnboundLocalError. A step "
            "unpacks the head (x, y = snake[0]), puts a new head on the "
            "front and takes the tail off the back. A list can do that "
            "with insert(0, cell), but that shifts every cell along; "
            "collections.deque is built for both ends, and appendleft and "
            "pop are instant."
        ),
        goal="Make the body a collections.deque of the same three cells (a list with insert(0, ...) also works). Add direction = (1, 0), acc = 0 and TICK = 0.12 - top-level names. Every TICK seconds of accumulated dt, step() the snake one cell along direction: a new head tuple on the front, the tail off the back.",
        starter=_P2,
        solution=_P3,
        check=_CHECK3,
        hint="def update(dt): global acc; acc += dt; while acc >= TICK: acc -= TICK; step()   and step(): x, y = snake[0]; dx, dy = direction; snake.appendleft((x + dx, y + dy)); snake.pop()",
    ),
    _step(
        id="pysnake-04-steer",
        title="Steer on the tick",
        teaches=(
            "A key press should not move the snake - the tick does. The "
            "key only records what you want: next_dir. At the start of "
            "each step the snake adopts it (direction = next_dir) and "
            "moves. That is why the snake turns on a grid line, and why a "
            "key pressed any time in the last tick counts. A dict from key "
            "name to direction, DIRS, keeps the handler short, and `key in "
            "DIRS` asks whether the key is one of its keys - look up 'q' "
            "without asking and you get a KeyError. on_key_down(fn) calls "
            "fn(key) when a key goes down. Assigning next_dir inside the "
            "handler needs `global next_dir`, and here forgetting it is "
            "worse than an error: Python quietly makes a local variable "
            "and the real next_dir never changes."
        ),
        goal="Add DIRS (a dict from key name to direction tuple), next_dir = (1, 0) and a handler registered with on_key_down: an arrow key sets next_dir, and step() copies next_dir into direction before it moves. Other keys do nothing.",
        starter=_P3,
        solution=_P4,
        check=_CHECK4,
        hint="DIRS = {'ArrowUp': (0, -1), ...}   def key_down(key): global next_dir; if key in DIRS: next_dir = DIRS[key]   and  direction = next_dir  at the top of step().",
    ),
    _step(
        id="pysnake-05-no-reverse",
        title="No turning back",
        teaches=(
            "Heading right, pressing left would put the new head on the "
            "snake's own neck: an instant death the player never chose. So "
            "ignore a turn that is the exact opposite of the way the snake "
            "is going: unpack dx, dy = direction and skip DIRS[key] when it "
            "equals (-dx, -dy). Tuples compare by value, element by "
            "element, so (-1, 0) == (-1, 0) is True. Compare with "
            "direction, the way the snake LAST MOVED, not with next_dir. "
            "Compare with next_dir and a quick Up then Left slips "
            "through: Left is fine against Up, and on the next tick the "
            "snake reverses."
        ),
        goal="Ignore a key that would turn the snake straight back on itself, judged against direction, the way it last moved, not against next_dir.",
        starter=_P4,
        solution=_P5,
        check=_CHECK5,
        hint="dx, dy = direction  and then  if DIRS[key] != (-dx, -dy): next_dir = DIRS[key]",
    ),
    _step(
        id="pysnake-06-food",
        title="Food on a free cell",
        teaches=(
            "Pick a random column and row and sometimes it is under the "
            "snake. You could keep guessing until it is free, but there is "
            "a neater way that cannot loop for ever: build every cell as a "
            "set, take the snake away with a set difference (cells - "
            "set(snake)), and choose from what is left. random.choice "
            "needs a sequence it can index, a list or a tuple, and a set "
            "is not one: random.choice(free) is a TypeError. sorted(free) "
            "makes a list, in a fixed order. spawn_food re-binds food, so "
            "it says `global food`. And draw_cell(*food, color) spreads "
            "the tuple out into the col and row arguments."
        ),
        goal="Add food (a (col, row) tuple, a top-level name) and spawn_food(): take the free cells - every cell minus the snake - and choose one with random.choice, then call spawn_food() once at the start. Draw the food.",
        starter=_P5,
        solution=_P6,
        check=_CHECK6,
        hint="free = {(col, row) for col in range(COLS) for row in range(ROWS)} - set(snake)   then   food = random.choice(sorted(free))   (and global food)",
    ),
    _step(
        id="pysnake-07-grow",
        title="Eat and grow",
        teaches=(
            "Growing is the cheapest trick in the game: a step normally "
            "adds a head AND removes the tail. When the new head lands on "
            "the food, skip the removal. The snake is one cell longer, and "
            "the tail has not moved. Then call spawn_food() - after the "
            "new head is on the snake, so the new food cannot land on it. "
            "Compare cells with ==, which looks at the numbers. `is` asks "
            "whether two names are the very same object, and two tuples "
            "built in different places are two objects even with the same "
            "numbers, so head is food would never be True."
        ),
        goal="When the new head equals food, keep the tail (the snake grows by one) and call spawn_food(). Otherwise pop the tail as before.",
        starter=_P6,
        solution=_P7,
        check=_CHECK7,
        hint="snake.appendleft(head); if head == food: spawn_food() else: snake.pop()",
    ),
    _step(
        id="pysnake-08-walls",
        title="Hit the wall",
        teaches=(
            "The grid has columns 0 to COLS - 1, so the first column off "
            "the edge is COLS itself. Python lets you chain comparisons: "
            "0 <= col < COLS means 0 <= col and col < COLS, and reads like "
            "the maths. Get an end wrong by one and the snake slides one "
            "cell into the wall before it dies, or dies a cell early. Work "
            "out the new head first, test it, and only then add it to the "
            "snake - a snake never drawn off the grid needs no cleaning "
            "up. Put what the game is doing in state = 'playing'. step() "
            "assigns it, so it joins the `global` line, and update stops "
            "when it is not 'playing'."
        ),
        goal="Add state = 'playing'. If the new head would be off the grid, set state to 'over' without moving the snake, stop updating, and write 'Game over' on the screen.",
        starter=_P7,
        solution=_P8,
        check=_CHECK8,
        hint="col, row = head; if not (0 <= col < COLS and 0 <= row < ROWS): state = 'over'; return   and  if state != 'playing': return  at the top of update.",
    ),
    _step(
        id="pysnake-09-self",
        title="Don't bite yourself",
        teaches=(
            "The new head dies if it lands on any cell of the body. "
            "set(snake) turns the body into a set, and `head in occupied` "
            "then answers with one hash lookup instead of walking the "
            "body cell by cell - which only works because tuples are "
            "hashable. There is one cell to be careful of: the tail. On an "
            "ordinary step the tail moves away as the head arrives, so "
            "chasing your own tail is safe, and a snake that dies there "
            "feels cheated: occupied.discard(snake[-1]) leaves it out. "
            "When the snake eats, the tail stays, and then that cell does "
            "count. (A deque cannot be sliced, so snake[:-1] would not "
            "work on it; a list can.)"
        ),
        goal="If the new head lands on the snake's own body, the game is over. The tail cell does not count unless the snake is eating, because it is about to move away.",
        starter=_P8,
        solution=_P9,
        check=_CHECK9,
        hint="eating = head == food; occupied = set(snake); if not eating: occupied.discard(snake[-1]); then  head in occupied",
    ),
    _step(
        id="pysnake-10-score",
        title="Keep score",
        teaches=(
            "A score is a number that changes in exactly one place: the "
            "branch of step() where the snake eats. Put the addition "
            "anywhere else - in the tick itself, say - and it counts "
            "time, not food. step() re-binds score, so score joins the "
            "`global` line, or Python raises UnboundLocalError on "
            "score += 10. Drawing text needs a font and a colour and a "
            "position, then ctx.fill_text. An f-string builds the message "
            "in one go: f'Score: {score}'. The text goes in draw(), every "
            "frame, so it always shows the latest number."
        ),
        goal="Add score = 0. Eating food adds 10 to it. Write the score on the screen.",
        starter=_P9,
        solution=_P10,
        check=_CHECK10,
        hint="In step(): if eating: score += 10; spawn_food()   and in draw(): ctx.fill_text(f'Score: {score}', 10, 20)",
    ),
    _step(
        id="pysnake-11-restart",
        title="Play again",
        teaches=(
            "A restart is a function that puts every piece of the game "
            "back as it was: snake, direction AND next_dir (leave next_dir "
            "pointing up and the new snake turns up on its first step), "
            "acc, score, state - and new food. Every name it assigns must "
            "be on its `global` line: leave score off and `score = 0` "
            "quietly makes a local variable while the real score stays. "
            "START, a tuple of tuples, holds the starting cells where "
            "nothing can change them, and deque(START) makes a fresh body "
            "from it for each game. Now one handler has two jobs, arrows "
            "and Enter, and `match` is made for that: case 'Enter' if "
            "state == 'over': ... case 'ArrowUp' | 'ArrowDown' | ...: ... "
            "The | joins alternatives, `if` adds a condition, and the "
            "first case that fits wins. Enter in the middle of a game, or "
            "any other key, must not wipe it."
        ),
        goal="Write reset() and call it when Enter is pressed after a game over: snake, direction, next_dir, acc, score and state back as they began, and new food. Write 'Press Enter to play again' on the game-over screen. Enter does nothing during a game.",
        starter=_P10,
        solution=_P11,
        check=_CHECK11,
        hint="def reset(): global snake, direction, next_dir, acc, score, state; snake = deque(START); direction = next_dir = (1, 0); ...; spawn_food()   and  match key: case 'Enter' if state == 'over': reset()",
    ),
    _step(
        id="pysnake-12-yours",
        title="Now it's yours",
        teaches=(
            "A whole game on a grid, with its own clock. Ideas, easier "
            "first: speed up a little every time it eats (make TICK a "
            "variable and give it a global); walls that wrap round with "
            "col % COLS; WASD as well as the arrows (case 'w' | "
            "'ArrowUp':); P to pause (another state); a best score that "
            "survives restarts; a second kind of food worth more that "
            "vanishes after a few seconds (after(5, fn)); obstacles in a "
            "set; a queue of two turns, so two quick presses both count - "
            "a deque(maxlen=2) fits; and a win when the snake fills the "
            "board - what does random.choice do with an empty list?"
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_P11,
        solution=_P11,
        check="",
    ),
)
