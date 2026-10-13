"""Tower defense in Python: the road-and-towers game of the JavaScript track, taught the Python way.

Not a transliteration. The game is the same - creeps walk a fixed road of
waypoints, you build towers on free tiles with the mouse, towers shoot the
creep furthest along in range with homing shots, creeps have health and pay
a reward, waves come on a timer, escapes cost lives, and there is a game over
and a restart - but the parts are Python's own:

  * the road is a list of tuples, `*path[0]` spreads a point into arguments,
    and `zip(path, path[1:])` pairs each waypoint with the next
  * Creep, Tower and Shot are `@dataclass` classes (`eq=False` where identity
    matters, `field(default_factory=list)` for a list of their own); a dict with
    the same keys works too and every check accepts both
  * `math.hypot` and `math.dist` for distances, `//` for a pixel's tile, a
    `set` of road tiles with `|=` and `in`, `any()` for "is this tile taken"
  * `max(creeps, key=lambda c: c.dist, default=None)` for the furthest-along
    target (and what `default=` is for)
  * list comprehensions to drop the dead and the spent - and the classic bug
    of removing from a list while a `for` walks it
  * a generator (`yield`) for the wave schedule, `not queue` for "nothing left"
  * `global` only where a function re-binds a top-level name, and what Python
    does when it is missing (UnboundLocalError, or - worse - silence)
  * f-strings for the HUD

As in the other tracks, each step starts from the one before, finished, and a
check plays the game rather than reading the code. The checks read - and set -
these top-level names: path, TILE, creeps, towers, shots, money, lives, waves,
wave, state, countdown, queue, spawn_timer, plus the functions make_creep,
tile_at, make_tower and find_target. The program re-binds creeps, shots, money,
lives and state, so a check always looks them up again rather than holding on.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

TRACK = "Tower defense (Python)"


def _t(text: str) -> str:
    """A block of the learner's program, without the newlines round it."""
    return text.strip("\n")


def _v(n: int, variants: dict[int, str]) -> str:
    """The text for step n: the variant with the greatest key not above n ('' before the first)."""
    keys = [k for k in variants if k <= n]
    return variants[max(keys)] if keys else ""


# -- The programs ------------------------------------------------------------
# Each is built from named blocks, each block as it stands at that step, so a
# step's solution is the step before plus the one change - the learner's diff.

_IMPORTS = {
    0: "from canvas import ctx, WIDTH, HEIGHT, on_frame",
    2: "import math\nfrom dataclasses import dataclass\n\nfrom canvas import ctx, WIDTH, HEIGHT, on_frame",
    5: "import math\nfrom dataclasses import dataclass\n\n"
       "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_click",
    8: "import math\nfrom dataclasses import dataclass, field\n\n"
       "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_click",
    11: "import math\nfrom dataclasses import dataclass, field\n\n"
        "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_click, on_key_down",
}

_CONSTS = {
    1: "TILE = 40",
    3: "TILE = 40\nBAR_W = 24",
    4: "TILE = 40\nBAR_W = 24\nSPAWN_EVERY = 1.5",
    9: "TILE = 40\nBAR_W = 24\nSPAWN_EVERY = 1.5\nTOWER_COST = 50",
    10: "TILE = 40\nBAR_W = 24\nSPAWN_EVERY = 1.5\nTOWER_COST = 50\nGAP = 5",
}

_PATH = _t("""
# The road, as the centre of each tile it turns at: (column * TILE + TILE / 2, row * TILE + TILE / 2).
path = [(20, 60), (380, 60), (380, 220), (140, 220), (140, 300)]
""")

_TILE_AT = _t("""
def tile_at(x, y):
    # Floor division rounds down, so 119.9 is still in column 2.
    return int(x // TILE), int(y // TILE)
""")

_TILES_BETWEEN = _t("""
def tiles_between(a, b):
    # Every tile from the one holding point a to the one holding point b.
    (col1, row1), (col2, row2) = tile_at(*a), tile_at(*b)
    return {
        (col, row)
        for col in range(min(col1, col2), max(col1, col2) + 1)
        for row in range(min(row1, row2), max(row1, row2) + 1)
    }
""")

_PATH_TILES = _t("""
# Every tile the road covers, worked out once from the waypoints.
path_tiles = set()
for a, b in zip(path, path[1:]):
    path_tiles |= tiles_between(a, b)
""")

_CREEP = {
    2: _t("""
@dataclass(eq=False)
class Creep:
    x: float
    y: float
    leg: int = 1  # the index in path of the waypoint it is walking to
    dist: float = 0  # how far along the road it has walked
    speed: float = 80
"""),
    3: _t("""
@dataclass(eq=False)
class Creep:
    x: float
    y: float
    leg: int = 1  # the index in path of the waypoint it is walking to
    dist: float = 0  # how far along the road it has walked
    speed: float = 80
    hp: float = 10
    max_hp: float = 10
"""),
    9: _t("""
@dataclass(eq=False)
class Creep:
    x: float
    y: float
    leg: int = 1  # the index in path of the waypoint it is walking to
    dist: float = 0  # how far along the road it has walked
    speed: float = 80
    hp: float = 10
    max_hp: float = 10
    reward: int = 5
"""),
}

_MAKE_CREEP = {
    2: _t("""
def make_creep():
    return Creep(*path[0])
"""),
    3: _t("""
def make_creep(hp=10):
    return Creep(*path[0], hp=hp, max_hp=hp)
"""),
}

_TOWER = {
    5: _t("""
@dataclass
class Tower:
    col: int
    row: int
    x: float
    y: float
"""),
    6: _t("""
@dataclass
class Tower:
    col: int
    row: int
    x: float
    y: float
    range: float = 120
"""),
    7: _t("""
@dataclass
class Tower:
    col: int
    row: int
    x: float
    y: float
    range: float = 120
    damage: float = 2
    rate: float = 0.5  # seconds between shots
    reload: float = 0  # seconds until it may fire again
"""),
}

_MAKE_TOWER = _t("""
def make_tower(col, row):
    return Tower(col, row, col * TILE + TILE / 2, row * TILE + TILE / 2)
""")

_SHOT = _t("""
@dataclass(eq=False)
class Shot:
    x: float
    y: float
    target: Creep
    damage: float
    speed: float = 300
    done: bool = False
    trail: list = field(default_factory=list)  # where it has just been
""")

_WAVE_PLAN = _t("""
def wave_plan():
    # Each wave in turn: the hit points of the creeps to send, in order.
    for count, hp in waves:
        yield [hp] * count
""")

_STATE = {
    2: "creeps = [make_creep()]",
    4: "creeps = []\nspawn_timer = 0",
    5: "creeps = []\ntowers = []\nspawn_timer = 0",
    8: "creeps = []\ntowers = []\nshots = []\nspawn_timer = 0",
    9: "creeps = []\ntowers = []\nshots = []\nmoney = 100\nspawn_timer = 0",
    10: _t("""
creeps = []
towers = []
shots = []
money = 100
waves = [(5, 10), (8, 16), (12, 24)]  # (how many creeps, each one's hp)
wave = 0
state = 'countdown'
countdown = 3
queue = []  # the hit points of the creeps this wave has still to send
spawn_timer = 0
plan = wave_plan()
"""),
    11: _t("""
creeps = []
towers = []
shots = []
money = 100
lives = 10
waves = [(5, 10), (8, 16), (12, 24)]  # (how many creeps, each one's hp)
wave = 0
state = 'countdown'
countdown = 3
queue = []  # the hit points of the creeps this wave has still to send
spawn_timer = 0
plan = wave_plan()
"""),
}

_MOVE_CREEP = _t("""
def move_creep(c, dt):
    # Walk speed * dt pixels along the path, turning each corner on the way.
    left = c.speed * dt
    while left > 0 and c.leg < len(path):
        px, py = path[c.leg]
        d = math.hypot(px - c.x, py - c.y)
        if d <= left:
            c.x, c.y = px, py
            c.leg += 1
            c.dist += d
            left -= d
        else:
            c.x += (px - c.x) / d * left
            c.y += (py - c.y) / d * left
            c.dist += left
            left = 0
""")

_SPAWN_CREEP = {
    4: "def spawn_creep():\n    creeps.append(make_creep())",
    10: "def spawn_creep(hp):\n    creeps.append(make_creep(hp))",
}

_CLICK = {
    5: _t("""
def click(x, y):
    col, row = tile_at(x, y)
    taken = any(t.col == col and t.row == row for t in towers)
    if (col, row) in path_tiles or taken:
        return
    towers.append(make_tower(col, row))
"""),
    9: _t("""
def click(x, y):
    global money
    col, row = tile_at(x, y)
    taken = any(t.col == col and t.row == row for t in towers)
    if (col, row) in path_tiles or taken or money < TOWER_COST:
        return
    money -= TOWER_COST
    towers.append(make_tower(col, row))
"""),
}

_FIND_TARGET = _t("""
def find_target(t):
    # The creep in range that has walked furthest along the path, or None.
    in_range = [c for c in creeps if math.dist((c.x, c.y), (t.x, t.y)) <= t.range]
    return max(in_range, key=lambda c: c.dist, default=None)
""")

_UPDATE_TOWER = {
    7: _t("""
def update_tower(t, dt):
    # Count the reload down with dt; when it is ready, fire at the first creep in range.
    t.reload = max(0, t.reload - dt)
    if t.reload > 0:
        return
    target = find_target(t)
    if target is None:
        return
    target.hp -= t.damage
    t.reload = t.rate
"""),
    8: _t("""
def update_tower(t, dt):
    # Count the reload down with dt; when it is ready, fire at the first creep in range.
    t.reload = max(0, t.reload - dt)
    if t.reload > 0:
        return
    target = find_target(t)
    if target is None:
        return
    shots.append(Shot(t.x, t.y, target, t.damage))
    t.reload = t.rate
"""),
}

_MOVE_SHOT = _t("""
def move_shot(s, dt):
    # Fly straight at the target's current position, so a moving target is followed.
    s.trail.append((s.x, s.y))
    del s.trail[:-6]
    dx, dy = s.target.x - s.x, s.target.y - s.y
    d = math.hypot(dx, dy)
    step = s.speed * dt
    if d <= step:
        s.target.hp -= s.damage
        s.done = True
    else:
        s.x += dx / d * step
        s.y += dy / d * step
""")

_START_WAVE = _t("""
def start_wave():
    global wave, queue, spawn_timer, state
    wave += 1
    queue = next(plan)
    spawn_timer = SPAWN_EVERY
    state = 'wave'
""")

_UPDATE_WAVES = _t("""
def update_waves(dt):
    global countdown, spawn_timer, state
    if state == 'countdown':
        countdown -= dt
        if countdown <= 0:
            start_wave()
    elif state == 'wave':
        spawn_timer += dt
        if queue and spawn_timer >= SPAWN_EVERY:
            spawn_timer -= SPAWN_EVERY
            spawn_creep(queue.pop(0))
        # The wave is over when nothing is left to spawn and nothing is still walking.
        if not queue and not creeps:
            if wave == len(waves):
                state = 'won'
            else:
                state = 'countdown'
                countdown = GAP
""")

_RESTART = _t("""
def restart():
    global creeps, towers, shots, money, lives, wave, state, countdown, queue, spawn_timer, plan
    creeps = []
    towers = []
    shots = []
    money = 100
    lives = 10
    wave = 0
    state = 'countdown'
    countdown = 3
    queue = []
    spawn_timer = 0
    plan = wave_plan()
""")

_KEY_DOWN = _t("""
def key_down(key):
    if key == 'Enter' and state == 'over':
        restart()
""")


def _update(n: int) -> str:
    if n < 2:
        return "def update(dt):\n    pass"
    names = ["creeps"]
    if n >= 8:
        names.append("shots")
    if n >= 9:
        names.append("money")
    if n >= 11:
        names += ["lives", "state"]
    if 4 <= n < 10:
        names.append("spawn_timer")
    lines = ["def update(dt):", "    global " + ", ".join(names)]
    if n >= 11:
        lines += ["    if state == 'over':", "        return"]
    if 4 <= n < 10:
        lines += ["    spawn_timer += dt", "    if spawn_timer >= SPAWN_EVERY:",
                  "        spawn_timer -= SPAWN_EVERY", "        spawn_creep()"]
    if n >= 10:
        lines.append("    update_waves(dt)")
    lines += ["    for c in creeps:", "        move_creep(c, dt)"]
    if n >= 7:
        lines += ["    for t in towers:", "        update_tower(t, dt)"]
    if n >= 8:
        lines += ["    for s in shots:", "        move_shot(s, dt)"]
    if n >= 9:
        lines.append("    money += sum(c.reward for c in creeps if c.hp <= 0)")
    if n >= 11:
        lines.append("    lives = max(0, lives - sum(1 for c in creeps if c.hp > 0 and c.leg >= len(path)))")
    lines.append("    creeps = [c for c in creeps if " + ("c.hp > 0 and " if n >= 3 else "") + "c.leg < len(path)]")
    if n >= 8:
        lines.append("    shots = [s for s in shots if not s.done and s.target in creeps]")
    if n >= 11:
        lines += ["    if lives <= 0:", "        state = 'over'"]
    return "\n".join(lines)


_DRAW_ROAD = _t("""
def draw_road():
    ctx.stroke_style = '#3b4252'
    ctx.line_width = TILE
    ctx.begin_path()
    ctx.move_to(*path[0])
    for point in path[1:]:
        ctx.line_to(*point)
    ctx.stroke()
""")

_DRAW_CREEP = {
    2: _t("""
def draw_creep(c):
    ctx.fill_style = '#f6ad55'
    ctx.begin_path()
    ctx.arc(c.x, c.y, 12, 0, math.tau)
    ctx.fill()
"""),
    3: _t("""
def draw_creep(c):
    ctx.fill_style = '#f6ad55'
    ctx.begin_path()
    ctx.arc(c.x, c.y, 12, 0, math.tau)
    ctx.fill()
    x = c.x - BAR_W / 2
    ctx.fill_style = '#742a2a'
    ctx.fill_rect(x, c.y - 24, BAR_W, 4)
    ctx.fill_style = '#68d391'
    ctx.fill_rect(x, c.y - 24, BAR_W * max(0, c.hp) / c.max_hp, 4)
"""),
}

_DRAW_TOWER = {
    5: _t("""
def draw_tower(t):
    ctx.fill_style = '#63b3ed'
    ctx.fill_rect(t.x - 14, t.y - 14, 28, 28)
"""),
    6: _t("""
def draw_tower(t):
    ctx.fill_style = '#63b3ed'
    ctx.fill_rect(t.x - 14, t.y - 14, 28, 28)
    target = find_target(t)
    if target:
        ctx.stroke_style = '#f6e05e'
        ctx.line_width = 2
        ctx.begin_path()
        ctx.move_to(t.x, t.y)
        ctx.line_to(target.x, target.y)
        ctx.stroke()
"""),
}

_DRAW_SHOT = _t("""
def draw_shot(s):
    ctx.fill_style = '#975a16'
    for x, y in s.trail:
        ctx.begin_path()
        ctx.arc(x, y, 2, 0, math.tau)
        ctx.fill()
    ctx.fill_style = '#f6e05e'
    ctx.begin_path()
    ctx.arc(s.x, s.y, 4, 0, math.tau)
    ctx.fill()
""")


def _draw(n: int) -> str:
    lines = ["def draw():", "    ctx.fill_style = '#10141f'", "    ctx.fill_rect(0, 0, WIDTH, HEIGHT)"]
    if n >= 1:
        lines.append("    draw_road()")
    if n >= 5:
        lines += ["    for t in towers:", "        draw_tower(t)"]
    if n >= 2:
        lines += ["    for c in creeps:", "        draw_creep(c)"]
    if n >= 8:
        lines += ["    for s in shots:", "        draw_shot(s)"]
    if n >= 9:
        lines += ["    ctx.fill_style = 'white'", "    ctx.font = '16px monospace'",
                  "    ctx.fill_text(f'${money}', 10, 20)"]
    if n >= 10:
        lines.append("    ctx.fill_text(f'Wave {wave}/{len(waves)}', 90, 20)")
    if n >= 11:
        lines.append("    ctx.fill_text(f'Lives: {lives}', 220, 20)")
    if n >= 10:
        lines += ["    if state == 'countdown':",
                  "        ctx.fill_text(f'Next wave in {math.ceil(countdown)}', 160, 310)",
                  "    if state == 'won':", "        ctx.font = '32px monospace'",
                  "        ctx.fill_text('You win!', 170, 170)"]
    if n >= 11:
        lines += ["    if state == 'over':", "        ctx.font = '32px monospace'",
                  "        ctx.fill_text('Game over', 150, 160)", "        ctx.font = '16px monospace'",
                  "        ctx.fill_text('Enter to play again', 160, 190)"]
    return "\n".join(lines)


_LOOP = "def loop(dt):\n    update(dt)\n    draw()"


def _program(n: int) -> str:
    """The whole program as it stands after step n (0 is the empty board)."""
    blocks = [
        _v(n, _IMPORTS),
        _v(n, _CONSTS),
        _PATH if n >= 1 else "",
        _TILE_AT if n >= 5 else "",
        _TILES_BETWEEN if n >= 5 else "",
        _PATH_TILES if n >= 5 else "",
        _v(n, _CREEP),
        _v(n, _MAKE_CREEP),
        _v(n, _TOWER),
        _MAKE_TOWER if n >= 5 else "",
        _SHOT if n >= 8 else "",
        _WAVE_PLAN if n >= 10 else "",
        _v(n, _STATE),
        _MOVE_CREEP if n >= 2 else "",
        _v(n, _SPAWN_CREEP),
        _v(n, _CLICK),
        "on_click(click)" if n >= 5 else "",
        _FIND_TARGET if n >= 6 else "",
        _v(n, _UPDATE_TOWER),
        _MOVE_SHOT if n >= 8 else "",
        _START_WAVE if n >= 10 else "",
        _UPDATE_WAVES if n >= 10 else "",
        _RESTART if n >= 11 else "",
        _KEY_DOWN if n >= 11 else "",
        "on_key_down(key_down)" if n >= 11 else "",
        _update(n),
        _DRAW_ROAD if n >= 1 else "",
        _v(n, _DRAW_CREEP),
        _v(n, _DRAW_TOWER),
        _DRAW_SHOT if n >= 8 else "",
        _draw(n),
        _LOOP,
        "on_frame(loop)",
    ]
    return "\n\n\n".join(b for b in blocks if b) + "\n"


_P = [_program(n) for n in range(12)]


# -- Shared check helpers ----------------------------------------------------

#: Prepended to every check. A thing's fields can be a dict's or an object's,
#: so a check reads them with get() and writes them with put(), and never
#: cares which the learner chose. The lists and numbers the program re-binds
#: (creeps, shots, money ...) are always looked up afresh through g.
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


def click_tile(col, row):
    cc.click(col * 40 + 20, row * 40 + 20)


def alive(o):
    return any(c is o for c in g.creeps)


def quiet():
    # A quiet board: no creeps, towers or shots, and nothing about to arrive.
    if 'spawn_timer' in g:
        g.spawn_timer = -1e9
    if 'countdown' in g:
        g.countdown = 1e9
    g.creeps = []
    if 'towers' in g:
        g.towers = []
    if 'shots' in g:
        g.shots = []


def still(x, y, hp=10, dist=0):
    # A creep that stands still where the check puts it.
    c = g.make_creep()
    for k, v in (('x', x), ('y', y), ('speed', 0), ('hp', hp), ('max_hp', hp), ('dist', dist)):
        put(c, k, v)
    return c


def launch(x, y, target, speed, damage):
    # A shot of the learner's own kind: fired by a real tower, then put where the check wants it.
    saved = (g.towers, g.creeps, g.shots)
    tower = g.make_tower(5, 3)
    put(tower, 'reload', 0)
    g.towers, g.creeps, g.shots = [tower], [still(get(tower, 'x') + 30, get(tower, 'y'), 1000)], []
    cc.frames(1)
    expect(len(g.shots) == 1, "A tower with a creep in range and no reload left should fire a shot.")
    shot = g.shots[0]
    g.towers, g.creeps, g.shots = saved
    for k, v in (('x', x), ('y', y), ('target', target), ('speed', speed), ('damage', damage), ('done', False)):
        put(shot, k, v)
    if get(shot, 'trail') is not None:
        put(shot, 'trail', [])
    return shot


"""

_ROAD_SAMPLE = "[(0, 1), (4, 1), (9, 1), (9, 3), (9, 5), (6, 5), (3, 5), (3, 6), (3, 7)]"


def _step(**fields: object) -> Step:
    """A step on this track: Python, in the Python Tower defense track."""
    fields["track"] = TRACK
    fields["language"] = "python"
    check = str(fields.get("check", ""))
    if check:
        fields["check"] = _HELPERS + check
    return Step(**fields)  # type: ignore[arg-type]


PYTOWERS_STEPS: tuple[Step, ...] = (
    _step(
        id="pytd-01-path",
        title="A path is a list of points",
        teaches=(
            "A tower defense game is a road and things that walk along it. "
            "The road is not a picture, it is data: a list of points, called "
            "waypoints, and everything else - where creeps walk, which tiles "
            "are taken, what to draw - is worked out from that list. In Python "
            "a point is a tuple, (x, y): a fixed pair. Put each at the centre "
            "of a tile, column * TILE + TILE / 2. A tile is TILE pixels square "
            "(40, so the canvas is 12 tiles across and 8 down); the capitals "
            "say 'a constant: look, do not change'. Drawing the road is one "
            "line through the points: begin_path, move_to the first, line_to "
            "each of the others, stroke - with a line_width as thick as a "
            "tile, so it reads as a road and not a wire. `*path[0]` spreads "
            "the pair into two arguments, and `path[1:]` is every point but the first."
        ),
        goal="Add TILE = 40 and path, a list of (x, y) tuples: (20, 60), (380, 60), (380, 220), (140, 220), (140, 300). Draw the road every frame as one line through them with ctx.line_width = TILE.",
        starter=_P[0],
        solution=_P[1],
        check="""
want = [(20, 60), (380, 60), (380, 220), (140, 220), (140, 300)]
expect('TILE' in g and g.TILE == 40, "Add TILE = 40 - the size of one square of the grid, in pixels.")
expect('path' in g and isinstance(g.path, list), "Make a list called path: path = [(20, 60), (380, 60), ...] - each point a tuple (x, y).")
expect(len(g.path) == len(want), f"path has {len(g.path)} points; the road has {len(want)} - the start, three corners and the end. List each one.")
for i, w in enumerate(want):
    p = g.path[i]
    ok = isinstance(p, (list, tuple)) and len(p) == 2 and p[0] == w[0] and p[1] == w[1]
    expect(ok, f"path[{i}] should be {w}. Points go at the CENTRE of a tile: column * TILE + TILE / 2, row * TILE + TILE / 2 (column 0, row 1 is x 20, y 60).")
cc.frames(1)
calls = cc.drawn()
strokes = [c for c in calls if c['name'] == 'stroke']
expect(strokes, "Draw the road as a line: begin_path, move_to the first point, line_to each of the others, then stroke - every frame, inside draw().")
expect(any(c['name'] == 'move_to' and near(c['args'][0], 20, 0.01) and near(c['args'][1], 60, 0.01) for c in calls), "Start the line at the first point: ctx.move_to(*path[0]) - the star spreads the (x, y) pair into two arguments.")
for w in want[1:]:
    expect(any(c['name'] == 'line_to' and near(c['args'][0], w[0], 0.01) and near(c['args'][1], w[1], 0.01) for c in calls), f"The road never goes through {w}. Draw a line_to for every point after the first - a for loop over path[1:] does it.")
lw = strokes[-1]['line_width']
expect(32 <= lw <= 48, f"The road is {lw} pixels wide; make it about a tile: ctx.line_width = TILE.")
""",
        hint="ctx.line_width = TILE; ctx.begin_path(); ctx.move_to(*path[0]); for point in path[1:]: ctx.line_to(*point); ctx.stroke()",
    ),
    _step(
        id="pytd-02-walk",
        title="Walk the path",
        teaches=(
            "A creep has fields, so it is a @dataclass: Creep(x, y, leg, dist, "
            "speed). Plain @dataclass compares by value, so two creeps with the "
            "same numbers would be 'equal' (and unhashable); eq=False keeps "
            "each creep itself. A creep walks toward path[leg]. Each frame it "
            "may cover speed * dt pixels - pixels a second times seconds, never "
            "a fixed number a frame. To aim, take the vector to the waypoint "
            "and divide by its length d (math.hypot). The trap is the corner: "
            "if the waypoint is closer than this frame's step, walking the "
            "whole step overshoots, and next frame the creep turns round and "
            "overshoots back. So when the waypoint is within reach, snap onto "
            "it, move leg on, and spend what is left of the step going the new "
            "way - a while loop does that. dist is how far along the road the "
            "creep has walked: towers will want it. The comprehension that "
            "drops creeps past the end RE-BINDS creeps, so update needs `global "
            "creeps`; without it Python decides creeps is local and the first "
            "`for c in creeps` raises UnboundLocalError."
        ),
        goal="Add a @dataclass(eq=False) class Creep with x, y, leg (the index in path of the waypoint it is walking to; 1 at the start), dist (0) and speed (80), and make_creep(), which returns a Creep standing on path[0]. Start with creeps = [make_creep()]. Every frame move each creep speed * dt along the path - onto each waypoint, never past it, then on toward the next (leg goes up) - adding what it walks to dist. Remove a creep whose leg has reached len(path) (update says global creeps). Draw each creep as a circle.",
        starter=_P[1],
        solution=_P[2],
        check="""
ROAD = [(20, 60), (380, 60), (380, 220), (140, 220), (140, 300)]


def road_dist(px, py):
    best = 1e9
    for (ax, ay), (bx, by) in zip(ROAD, ROAD[1:]):
        vx, vy = bx - ax, by - ay
        k = max(0, min(1, ((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy)))
        best = min(best, math.hypot(px - (ax + k * vx), py - (ay + k * vy)))
    return best


def along(d):
    for (ax, ay), (bx, by) in zip(ROAD, ROAD[1:]):
        length = math.hypot(bx - ax, by - ay)
        if d <= length:
            return ax + (bx - ax) * d / length, ay + (by - ay) * d / length
        d -= length
    return ROAD[-1]


expect('make_creep' in g and callable(g.make_creep), "Write def make_creep() that returns a new Creep standing on path[0].")
expect('creeps' in g and isinstance(g.creeps, list) and len(g.creeps) == 1, "Start with one creep: creeps = [make_creep()]")
c = g.creeps[0]
expect(near(get(c, 'x'), 20, 0.5) and near(get(c, 'y'), 60, 0.5), "A new creep stands on the first point of the path: x 20, y 60. Creep(*path[0]) fills x and y from it.")
speed = get(c, 'speed')
expect(get(c, 'leg') == 1 and get(c, 'dist') == 0 and isinstance(speed, (int, float)) and speed > 0, "A new creep has leg 1 (the waypoint it is walking to), dist 0 and a speed in pixels a second, 80.")
v = speed
cc.frames(1)
expect(any(near(a['x'], get(c, 'x'), 1.5) and near(a['y'], get(c, 'y'), 1.5) for a in cc.arcs()), "Draw each creep every frame as a circle: ctx.arc(c.x, c.y, 12, 0, math.tau), then ctx.fill().")


def back():
    for k, val in (('x', 20), ('y', 60), ('leg', 1), ('dist', 0)):
        put(c, k, val)
    if not alive(c):
        g.creeps.append(c)


def walk(seconds, fps):
    # Walk for some seconds at a frame rate; the creep must be on the road after every frame.
    for i in range(round(seconds * fps)):
        cc.frames(1, 1 / fps)
        expect(alive(c), f"The creep disappeared after {i / fps:.1f} seconds, long before the end of the road.")
        x, y = get(c, 'x'), get(c, 'y')
        expect(road_dist(x, y) <= 0.5, f"The creep left the road: it is at ({x:.1f}, {y:.1f}) at {(i + 1) / fps:.2f} seconds. Walking the whole step past a waypoint overshoots it - snap onto the waypoint when it is within reach.")


back()
cc.frames(120)
x, y = get(c, 'x'), get(c, 'y')
expect(near(x, 20 + 2 * v, 3) and near(y, 60, 1), f"After 2 seconds at {v} pixels a second the creep should be at x {20 + 2 * v}, y 60; it is at ({x:.1f}, {y:.1f}). Move it speed * dt each frame.")
back()
cc.frames(60, 1 / 30)
x = get(c, 'x')
expect(near(x, 20 + 2 * v, 3), f"On a slower screen (30 frames a second) the creep is at x {x:.1f} after 2 seconds; it should be at {20 + 2 * v} just the same. Move speed * dt, not a fixed amount a frame.")
# A speed that does not divide the road's pieces evenly, so a corner is rarely landed on exactly.
W = 77
put(c, 'speed', W)
for fps in (60, 30):
    back()
    walk(7, fps)
    ex, ey = along(7 * W)
    x, y = get(c, 'x'), get(c, 'y')
    expect(math.hypot(x - ex, y - ey) <= 7, f"After 7 seconds at {fps} frames a second the creep should be at about ({ex:.0f}, {ey:.0f}), after two corners; it is at ({x:.1f}, {y:.1f}). At a waypoint, move leg on to the following one and keep walking.")
    expect(near(get(c, 'dist'), 7 * W, 7), f"dist should be how far the creep has walked, about {7 * W} after 7 seconds; it is {get(c, 'dist'):.1f}. Add each piece of the walk to dist.")
back()
put(c, 'x', 370)
cc.frames(1, 1.0)
x, y = get(c, 'x'), get(c, 'y')
expect(road_dist(x, y) <= 0.5 and get(c, 'leg') >= 2, f"One very long frame (a second) pushed the creep off the road to ({x:.1f}, {y:.1f}). If the waypoint is closer than the step, put the creep on it and turn - never walk past.")
for fps in (60, 30):
    back()
    cc.frames(math.ceil(((840 + 40) / W) * fps), 1 / fps)
    expect(not alive(c), f"After walking the whole road at {fps} frames a second the creep is still in creeps. Once leg reaches len(path), take it out of the list.")
""",
        hint="left = c.speed * dt; while left > 0 and c.leg < len(path): px, py = path[c.leg]; d = math.hypot(...); if d <= left: snap to (px, py), c.leg += 1, c.dist += d, left -= d; else: move left toward it, left = 0",
    ),
    _step(
        id="pytd-03-health",
        title="Health bars",
        teaches=(
            "A creep has hp, its health now, and max_hp, what it started with. "
            "The bar over its head is the fraction hp / max_hp times the bar's "
            "full width, drawn on top of a darker bar of full width. Draw it "
            "from the creep's own x and y every frame, so it walks along with "
            "it, and clamp with max(0, hp) so a creep on -3 hp never draws a "
            "bar of negative width. Dying is just a filter: keep the creeps "
            "with hp above zero, and every other part of the game can lower hp "
            "without worrying about removing anyone. Build a NEW list for it, "
            "with a list comprehension. The classic bug is `for c in creeps: "
            "if c.hp <= 0: creeps.remove(c)` - removing from a list while a "
            "for loop walks it shifts everything left under the loop's feet, "
            "so it skips the creep after each one removed and some dead creeps "
            "live on."
        ),
        goal="Give Creep hp and max_hp, both 10, and make_creep(hp=10) that sets both. Add BAR_W = 24 and draw a bar above each creep: a dark one BAR_W wide and a green one on top of it, BAR_W * hp / max_hp wide. Remove creeps whose hp is 0 or less (build a new list; do not remove while looping).",
        starter=_P[2],
        solution=_P[3],
        check="""
expect('creeps' in g and len(g.creeps) >= 1, "The creep from the last step should still be there at the start.")
c = g.creeps[0]
expect(get(c, 'hp') == 10 and get(c, 'max_hp') == 10, "A new creep has hp 10 and max_hp 10. Give the Creep both fields (and make_creep(hp=10) sets both).")
v = get(c, 'speed')
put(c, 'speed', 0)


def bars():
    cx, cy = get(c, 'x'), get(c, 'y')
    return [r for r in cc.rects() if r['h'] <= 8 and r['y'] >= cy - 40 and r['y'] + r['h'] <= cy and r['x'] + r['w'] >= cx - 16 and r['x'] <= cx + 16]


cc.frames(1)
widths = [r['w'] for r in bars()]
expect(widths, "Draw a health bar above each creep: a thin rectangle (4 pixels tall) a little above its circle, with ctx.fill_rect.")
full = max(widths)
expect(16 <= full <= 48, f"The health bar is {full} pixels wide at full health; make it about as wide as the creep, BAR_W = 24.")
put(c, 'hp', 5)
cc.frames(1)
expect(any(near(r['w'], full / 2, 1.5) for r in bars()), f"At 5 of 10 hp the green part of the bar should be half as wide as at full health ({full / 2} pixels): BAR_W * hp / max_hp.")
put(c, 'hp', 3)
cc.frames(1)
expect(any(near(r['w'], full * 0.3, 1.5) for r in bars()), f"At 3 of 10 hp the bar should be {full * 0.3:.1f} pixels wide.")
put(c, 'hp', 10)
put(c, 'speed', v)
cc.frames(60)
expect(alive(c) and get(c, 'x') > 60, "The creep should be walking again.")
expect(bars(), "The bar should follow the creep: draw it from the creep's current x and y every frame.")
put(c, 'hp', 1)
cc.frames(2)
expect(alive(c), "A creep with 1 hp left is still alive.")
put(c, 'hp', 0)
cc.frames(1)
expect(not alive(c), "A creep with 0 hp should be taken out of creeps. Keep only the ones with hp > 0.")
d = g.make_creep()
g.creeps.append(d)
put(d, 'hp', -4)
cc.frames(1)
expect(not alive(d), "A creep below 0 hp is dead as well.")
dead = [still(100 + 20 * i, 100, 10) for i in range(4)]
healthy = still(300, 100, 10)
for o in dead:
    put(o, 'hp', 0)
g.creeps = [dead[0], dead[1], healthy, dead[2], dead[3]]
cc.frames(1)
left = sum(1 for o in dead if alive(o))
expect(left == 0, f"{left} of 4 dead creeps are still in creeps after the frame. Removing from a list while a for loop walks it skips the creep after each one removed - build a new list instead: creeps = [c for c in creeps if ...].")
expect(alive(healthy), "A creep with full health was taken out with the dead ones.")
""",
        hint="creeps = [c for c in creeps if c.hp > 0 and c.leg < len(path)]   and   ctx.fill_rect(x, c.y - 24, BAR_W * max(0, c.hp) / c.max_hp, 4)",
    ),
    _step(
        id="pytd-04-spawn",
        title="Send them in",
        teaches=(
            "Spawning on a timer is the Snake tick again: add each frame's dt "
            "to spawn_timer, and when it holds a whole SPAWN_EVERY, take "
            "SPAWN_EVERY off it (not set it to zero: the leftover keeps the "
            "rhythm exact) and spawn one creep. All creeps walk at the same "
            "speed, so they arrive in a column, 1.5 seconds and 120 pixels "
            "apart. spawn_timer is assigned inside update, so it joins the "
            "`global` line - spawn_creep() only appends to the list, which "
            "needs no global. Leave it out and Python says UnboundLocalError "
            "on the very first `spawn_timer += dt`: an assignment anywhere in "
            "a function makes the name local to the whole function."
        ),
        goal="Start with no creeps: creeps = []. Add SPAWN_EVERY = 1.5, spawn_timer = 0 and spawn_creep(), which appends a make_creep() to creeps. Add dt to spawn_timer every frame, and every SPAWN_EVERY seconds spawn one creep (spawn_timer is assigned in update, so it needs global).",
        starter=_P[3],
        solution=_P[4],
        check="""
expect('spawn_creep' in g and callable(g.spawn_creep), "Write def spawn_creep() that appends a new creep, make_creep(), to creeps.")
expect('SPAWN_EVERY' in g and g.SPAWN_EVERY == 1.5, "Add SPAWN_EVERY = 1.5 - the seconds between creeps.")
expect('spawn_timer' in g and isinstance(g.spawn_timer, (int, float)), "Keep the time since the last creep in spawn_timer = 0")
expect(isinstance(g.creeps, list) and len(g.creeps) == 0, "The game starts with no creeps: creeps = []")
cc.frames(80)
expect(len(g.creeps) == 0, f"{len(g.creeps)} creep(s) after 1.3 seconds; the first should come after 1.5 seconds (SPAWN_EVERY), not before.")
cc.frames(15)
expect(len(g.creeps) == 1, f"{len(g.creeps)} creep(s) after 1.6 seconds; there should be exactly one, spawned at 1.5.")
first = g.creeps[0]
expect(math.hypot(get(first, 'x') - 20, get(first, 'y') - 60) < 25, "A new creep starts at the beginning of the path, path[0] - this one is already far from it.")
cc.frames(277)
expect(len(g.creeps) == 4, f"{len(g.creeps)} creeps after 6.2 seconds; one every 1.5 seconds makes 4 (at 1.5, 3, 4.5 and 6).")
expect(len({id(o) for o in g.creeps}) == 4, "Each spawn should make a new creep: append make_creep(), not the same object again.")
cs = g.creeps
for i in range(len(cs) - 1):
    gap = get(cs[i], 'dist') - get(cs[i + 1], 'dist')
    want = g.SPAWN_EVERY * get(cs[0], 'speed')
    expect(near(gap, want, 8), f"Creeps should walk in a column {want} pixels apart (1.5 seconds at speed {get(cs[0], 'speed')}); these are {gap:.0f} apart.")
g.creeps = []
g.spawn_timer = 0
cc.frames(186, 1 / 30)
expect(len(g.creeps) == 4, f"On a slower screen (30 frames a second) there are {len(g.creeps)} creeps after 6.2 seconds; there should still be 4. Count time with dt, not frames.")
""",
        hint="spawn_timer += dt; if spawn_timer >= SPAWN_EVERY: spawn_timer -= SPAWN_EVERY; spawn_creep()   - and global creeps, spawn_timer at the top of update.",
    ),
    _step(
        id="pytd-05-build",
        title="Click a tile",
        teaches=(
            "on_click(fn) calls fn(x, y) with the click already in canvas "
            "pixels - no page-to-canvas scaling for you to do. The game wants "
            "a tile: a column and a row. x // TILE is floor division, which "
            "rounds DOWN: 119.9 // 40 is 2.0 and 120 // 40 is 3.0, so every "
            "tile owns exactly its own 40 pixels. (round() would give the "
            "right half of every tile to its neighbour; divmod(x, TILE) gives "
            "the tile AND how far into it, in one go.) A tuple (col, row) is "
            "a handy key, so the road's tiles go in a set of them: a set "
            "answers `in` instantly and `|=` adds another set. A straight "
            "piece of road covers every tile between its two ends, not just "
            "the ends - testing the waypoints alone misses all the tiles "
            "between; zip(path, path[1:]) pairs each waypoint with the next "
            "to walk the pieces. A tower may go on a tile only if it is not "
            "road and not already taken, and any() asks 'is there one?'."
        ),
        goal="Add towers = [], a @dataclass Tower with col, row, x, y (x and y the tile's centre), make_tower(col, row), tile_at(x, y) returning (col, row) for a point in canvas pixels, and path_tiles, a set of the (col, row) of every tile the road covers. A click (on_click) on a tile that is neither road nor already a tower appends a tower to towers. Draw each tower as a square inside its tile.",
        starter=_P[4],
        solution=_P[5],
        check="""
expect('tile_at' in g and callable(g.tile_at), "Write def tile_at(x, y) that returns (col, row) for a point in canvas pixels.")


def T(x, y):
    return tuple(g.tile_at(x, y))


expect(T(0, 0) == (0, 0) and T(39.9, 39.9) == (0, 0), "The top-left tile is column 0, row 0: x from 0 up to (not including) 40, and the same for y. Use // (it rounds down), not round().")
expect(T(40, 40) == (1, 1) and T(130, 250) == (3, 6), f"tile_at(130, 250) should be (3, 6) - column 3, row 6 (x // TILE, y // TILE); it says {T(130, 250)}.")
expect(T(479, 319) == (11, 7), f"The bottom-right corner is column 11, row 7; tile_at says {T(479, 319)}.")
expect(T(119.9, 83) == (2, 2) and T(120, 83) == (3, 2), f"x 119.9 is in column 2 and x 120 in column 3 (use // , which rounds down, not round()); tile_at says {T(119.9, 83)} and {T(120, 83)}.")
expect('path_tiles' in g, "Add path_tiles: a set of the (col, row) of every tile the road covers.")
expected = {(c, 1) for c in range(0, 10)} | {(9, r) for r in range(1, 6)} | {(c, 5) for c in range(3, 10)} | {(3, r) for r in range(5, 8)}
got_tiles = {tuple(t) for t in g.path_tiles}
missing = sorted(expected - got_tiles)
extra = sorted(got_tiles - expected)
expect(not missing, f"path_tiles is missing {len(missing)} road tile(s), for instance {missing[:1]}. A piece of road covers every tile BETWEEN its two waypoints, not just the ends - zip(path, path[1:]) pairs each waypoint with the next.")
expect(not extra, f"path_tiles has {len(extra)} tile(s) that are not road, for instance {extra[:1]}.")
expect(isinstance(g.towers, list) and len(g.towers) == 0, "Start with no towers: towers = []")
quiet()
click_tile(5, 3)
expect(len(g.towers) == 1, "A click on a free tile (column 5, row 3) should build a tower: append one to towers. (on_click(fn) calls fn(x, y) with the click in canvas pixels.)")
t = g.towers[0]
expect(get(t, 'col') == 5 and get(t, 'row') == 3 and get(t, 'x') == 220 and get(t, 'y') == 140, "The tower is on column 5, row 3 and its x, y are the tile's centre: 220, 140.")
cc.click(119.9, 83)
cc.click(120, 83)
cc.click(479, 319)
click_tile(10, 3)
click_tile(5, 3)
got = sorted((get(o, 'col'), get(o, 'row')) for o in g.towers)
expect(got == sorted([(10, 3), (11, 7), (2, 2), (3, 2), (5, 3)]), f"Towers are on {got}; clicks at x 119.9 and 120 are in columns 2 and 3 (floor, not round), the bottom-right corner is column 11, row 7, and a second click on a tower's tile builds nothing.")
before = len(g.towers)
for col, row in ROAD_SAMPLE:
    click_tile(col, row)
expect(len(g.towers) == before, "A click on the road must not build: a tower there would block the creeps' way and look wrong. Check the tile against path_tiles first.")
cc.frames(1)


def in_tile(col, row):
    return any(r['w'] >= 16 and r['h'] >= 16 and r['x'] >= col * 40 and r['x'] + r['w'] <= col * 40 + 40 and r['y'] >= row * 40 and r['y'] + r['h'] <= row * 40 + 40 for r in cc.rects())


for col, row in ((5, 3), (2, 2), (11, 7)):
    expect(in_tile(col, row), f"Draw every tower as a square inside its tile - nothing is drawn in column {col}, row {row}.")
""".replace("ROAD_SAMPLE", _ROAD_SAMPLE),
        hint="col, row = tile_at(x, y); if (col, row) in path_tiles or taken: return   and   for a, b in zip(path, path[1:]): path_tiles |= tiles_between(a, b)",
    ),
    _step(
        id="pytd-06-target",
        title="Range and the first target",
        teaches=(
            "A tower sees a circle: a creep is in range when its distance "
            "from the tower, math.dist((cx, cy), (tx, ty)) or math.hypot(dx, "
            "dy), is at most the range. Testing |dx| and |dy| on their own "
            "sees a square whose corners reach too far. Several creeps can be "
            "in range at once, so a tower needs a rule for choosing. The "
            "usual one is the first: the creep that has walked furthest along "
            "the path, which is what dist is for. max(in_range, key=lambda c: "
            "c.dist) picks the biggest by that key - and min(..., key=lambda "
            "c: distance to the tower) would be 'nearest', which feels "
            "natural but has the tower shoot a straggler while the leaders "
            "walk away. An empty list has no biggest: max([]) raises "
            "ValueError, unless you pass default=None for the empty case."
        ),
        goal="Give every Tower a range of 120. Write find_target(tower), which returns the creep within range of the tower that has the largest dist, or None when there is none (use max with key= and default=). Draw a yellow line from each tower to its target.",
        starter=_P[5],
        solution=_P[6],
        check="""
quiet()
click_tile(5, 3)
expect(len(g.towers) == 1, "Building a tower with a click should still work.")
t = g.towers[0]
R = get(t, 'range')
expect(isinstance(R, (int, float)) and R > 0, "Give every tower a range: range = 120, in pixels - a field of Tower.")
expect('find_target' in g and callable(g.find_target), "Write def find_target(t) that returns the creep it should shoot, or None.")
tx, ty = get(t, 'x'), get(t, 'y')


def target_of(creeps):
    g.creeps = creeps
    try:
        return g.find_target(t)
    except ValueError:
        expect(False, "find_target crashed when there was nothing in range: max() of an empty list raises ValueError. Give it default=None.")


near1 = still(tx + R * 0.8, ty, 10, 100)
far1 = still(tx + R + 10, ty, 10, 900)
expect(target_of([near1, far1]) is near1, "A creep just outside the range (range + 10 away) must not be chosen, however far along it is. A creep is in range when math.dist(...) <= range.")
corner = still(tx + R * 0.8, ty + R * 0.8, 10, 100)
expect(not target_of([corner]), "A creep at 0.8 range across and 0.8 range down is 1.13 ranges away - out of range. Range is a circle: compare the distance, math.dist or math.hypot, with range, not dx and dy one by one.")
expect(not target_of([]), "With no creeps there is no target: return None (max(..., default=None) does it).")
lead = still(tx - R * 0.9, ty, 10, 500)
back_ = still(tx + R * 0.3, ty, 10, 100)
expect(target_of([back_, lead]) is lead, "Two creeps in range: the tower should shoot the one that has walked furthest (the larger dist), not the nearest one to the tower.")
expect(target_of([lead, back_]) is lead, "The creep that has walked furthest is the target whichever order they are in the list - compare dist.")
mid = still(tx, ty - R * 0.5, 10, 300)
expect(target_of([lead, mid, back_]) is lead, "With three in range the largest dist wins.")
edge = target_of([back_, still(tx + R * 0.99, ty, 10, 50)])
expect(edge is not None and get(edge, 'dist') >= 50, "A creep right at the edge of the range, just inside it, is in range.")
g.creeps = [near1]
cc.frames(1)
calls = cc.drawn()
i = next((k for k, c in enumerate(calls) if c['name'] == 'move_to' and near(c['args'][0], tx, 1) and near(c['args'][1], ty, 1)), -1)
expect(i >= 0 and any(c['name'] == 'line_to' and near(c['args'][0], get(near1, 'x'), 1) and near(c['args'][1], get(near1, 'y'), 1) for c in calls[i:]), "Draw a line from the tower to its target: begin_path, move_to(t.x, t.y), line_to(target.x, target.y), stroke.")
g.creeps = [far1]
cc.frames(1)
expect(not any(c['name'] == 'move_to' and near(c['args'][0], tx, 1) and near(c['args'][1], ty, 1) for c in cc.drawn()), "A tower with no target in range should not draw a line.")
""",
        hint="in_range = [c for c in creeps if math.dist((c.x, c.y), (t.x, t.y)) <= t.range]   then   max(in_range, key=lambda c: c.dist, default=None)",
    ),
    _step(
        id="pytd-07-cooldown",
        title="Fire rate",
        teaches=(
            "A tower that fires every frame is a machine gun, and one that "
            "fires every N frames is a different tower on a faster screen. "
            "Give it a reload: the seconds until it may fire again. Each frame "
            "take dt off it, never below zero (max(0, reload - dt)); when it "
            "is zero and there is a target, fire and set it back to the rate. "
            "Only resetting it when it fires means a tower with nothing to "
            "shoot is ready the moment something comes into range. For now a "
            "hit is instant: the target simply loses the tower's damage. Only "
            "the target is hit, not everything in range. `target is None` is "
            "the exact way to ask 'did find_target find nobody?'; a creep "
            "object is always truthy, so `if not target` works too."
        ),
        goal="Give every Tower damage 2, rate 0.5 (seconds between shots) and reload 0. Write update_tower(t, dt), called for every tower each frame: take dt off reload, not going below 0. When it is 0 and find_target finds a creep, take damage off that creep's hp and set reload to rate.",
        starter=_P[6],
        solution=_P[7],
        check="""
for fps in (60, 30):
    quiet()
    click_tile(5, 3)
    expect(len(g.towers) == 1, "Building a tower with a click should still work.")
    t = g.towers[0]
    expect(all(isinstance(get(t, k), (int, float)) for k in ('damage', 'rate', 'reload')) and get(t, 'damage') > 0, "Give every tower damage = 2, rate = 0.5 and reload = 0 - fields of Tower.")
    put(t, 'rate', 0.5)
    put(t, 'reload', 0)
    c = still(get(t, 'x') + 60, get(t, 'y'), 1000, 100)
    other = still(get(t, 'x') - 60, get(t, 'y'), 1000, 10)
    g.creeps = [other, c]
    cc.frames(1, 1 / fps)
    expect(get(c, 'hp') < 1000, "A tower whose reload is 0, with a creep in range, should fire at once: take damage off the target's hp.")
    hits = 1
    for i in range(1, 3 * fps):
        hp = get(c, 'hp')
        cc.frames(1, 1 / fps)
        if get(c, 'hp') < hp:
            hits += 1
    expect(5 <= hits <= 7, f"At {fps} frames a second the tower hit {hits} times in 3 seconds; with a rate of 0.5 seconds it should be 6 or 7. Count the reload down with dt, not frames.")
    expect(near(get(c, 'hp'), 1000 - hits * get(t, 'damage'), 0.001), f"Each hit should take exactly damage ({get(t, 'damage')}) off the hp; {hits} hits left it on {get(c, 'hp')}.")
    expect(get(other, 'hp') == 1000, "The creep nearer to the tower but behind the leader lost hp: only the target (the one that has walked furthest) is hit.")
""",
        hint="t.reload = max(0, t.reload - dt); if t.reload > 0: return; target = find_target(t); if target is None: return; target.hp -= t.damage; t.reload = t.rate",
    ),
    _step(
        id="pytd-08-shots",
        title="Shots that home",
        teaches=(
            "An instant hit is hard to read. A shot is a small object that "
            "flies: a @dataclass Shot with x, y, target, damage, speed. Each "
            "frame it heads straight for where its target is now, speed * dt "
            "along the line, so it homes - it bends after a creep going round "
            "a corner. Within one step of the target it lands: the damage is "
            "dealt and it is done. It must also go when the target dies or "
            "walks off the end first - `s.target in creeps` asks that, and "
            "because Creep is eq=False it asks about THAT creep, not one that "
            "merely looks the same. A shot keeps a short trail of where it has "
            "been: `trail: list = []` is refused by dataclass (ValueError: "
            "mutable default - every shot would share one list), so write "
            "field(default_factory=list), which makes a fresh list per shot; "
            "`del s.trail[:-6]` keeps only the last six points."
        ),
        goal="Add shots = [] and a @dataclass(eq=False) class Shot with x, y, target, damage, speed (300), done (False) and trail (a list, field(default_factory=list)). A tower that fires appends Shot(t.x, t.y, target, t.damage) instead of an instant hit. move_shot(s, dt), each frame for every shot: add its position to its trail and keep only the last 6; move speed * dt toward the target's current position; on arriving, take damage off the target's hp and set done. Remove shots that are done or whose target is no longer in creeps (update says global shots). Draw each shot as a small circle.",
        starter=_P[7],
        solution=_P[8],
        check="""
expect('shots' in g and isinstance(g.shots, list), "Add shots = []")
for fps in (60, 30):
    quiet()
    c = still(250, 50, 10, 50)
    s = launch(50, 50, c, 200, 3)
    g.creeps = [c]
    g.shots = [s]
    cc.frames(fps // 2, 1 / fps)
    expect(near(get(s, 'x'), 150, 6) and near(get(s, 'y'), 50, 2), f"At {fps} frames a second a shot of speed 200 should have flown 100 pixels in half a second, to x 150; it is at ({get(s, 'x'):.1f}, {get(s, 'y'):.1f}). Move it speed * dt.")
    expect(get(c, 'hp') == 10, "The shot has not arrived yet; the creep should not have lost hp.")
    cc.frames(round(fps * 0.6), 1 / fps)
    expect(get(c, 'hp') == 7, f"The shot should have landed after a second: damage 3 off 10 hp leaves 7; the creep has {get(c, 'hp')}.")
    expect(len(g.shots) == 0, "A shot that has landed must be removed from shots (it hits once).")
quiet()
h = still(250, 50, 10, 50)
hs = launch(50, 50, h, 200, 3)
g.creeps = [h]
g.shots = [hs]
cc.frames(15)
put(h, 'y', 250)
cc.frames(30)
expect(near(get(hs, 'x'), 160, 8) and near(get(hs, 'y'), 130, 8), f"The creep moved and the shot should have turned after it, to about (160, 130); it is at ({get(hs, 'x'):.1f}, {get(hs, 'y'):.1f}). Aim at the target's current x and y every frame.")
cc.frames(70)
expect(get(h, 'hp') == 7 and len(g.shots) == 0, "The shot should have caught the creep and landed, once.")
quiet()
d = still(250, 50, 10, 50)
ds = launch(50, 50, d, 200, 3)
g.creeps = [d]
g.shots = [ds]
cc.frames(5)
put(d, 'hp', 0)
cc.frames(2)
expect(len(g.shots) == 0, "The target died while the shot was flying, and the shot is still there. Remove shots whose target is no longer in creeps.")
quiet()
e = still(250, 50, 10, 50)
es = launch(50, 50, e, 200, 3)
g.creeps = [e]
g.shots = [es]
cc.frames(5)
put(e, 'leg', len(g.path))
cc.frames(2)
expect(len(g.shots) == 0, "The target left the game (walked off the end) and the shot is still flying. Remove shots whose target is no longer in creeps.")
quiet()
f = still(250, 50, 10, 50)
fs = launch(100, 50, f, 200, 3)
g.creeps = [f]
g.shots = [fs]
cc.frames(1)
expect(any(near(a['x'], get(fs, 'x'), 2) and near(a['y'], get(fs, 'y'), 2) and a['r'] < 8 for a in cc.arcs()), "Draw each shot as a small circle (radius under 8) at its x and y.")
quiet()
click_tile(5, 3)
t = g.towers[0]
put(t, 'reload', 0)
target = still(get(t, 'x') + 60, get(t, 'y'), 10, 100)
g.creeps = [target]
cc.frames(1)
expect(len(g.shots) == 1 and get(g.shots[0], 'target') is target, "A tower that fires should append a Shot with the creep as its target.")
expect(get(target, 'hp') == 10, "The creep lost hp the moment the tower fired. The damage should land when the shot arrives.")
cc.frames(20)
expect(get(target, 'hp') == 10 - get(t, 'damage') and len(g.shots) == 0, f"After the shot has had time to arrive the creep should be on {10 - get(t, 'damage')} hp and the shot gone; hp is {get(target, 'hp')} and there are {len(g.shots)} shots.")
quiet()
ta, tb = g.make_tower(5, 3), g.make_tower(7, 3)
for o in (ta, tb):
    put(o, 'reload', 0)
prey = still(260, 250, 100000)
g.towers = [ta, tb]
g.creeps = [prey]
cc.frames(1)
expect(len(g.shots) == 2, f"Two towers with a creep in range should fire a shot each; there are {len(g.shots)} shots.")
for o in g.shots:
    put(o, 'speed', 60)
cc.frames(25)
trails = [get(o, 'trail') for o in g.shots]
expect(all(isinstance(tr, list) for tr in trails), "Give every Shot a trail, a list of where it has been: trail: list = field(default_factory=list), and add its position to it each frame.")
expect(trails[0] is not trails[1], "Both shots are sharing ONE trail list. A dataclass default of [] is shared; field(default_factory=list) makes a new list for each Shot.")
expect(all(2 <= len(tr) <= 10 for tr in trails), f"A shot's trail should be a short list of its last few points (here {[len(tr) for tr in trails]} after 25 frames): add its position, then del s.trail[:-6] to keep the last six.")
""",
        hint="shots.append(Shot(t.x, t.y, target, t.damage))   in move_shot: if d <= step: s.target.hp -= s.damage; s.done = True  else move step toward the target   shots = [s for s in shots if not s.done and s.target in creeps]",
    ),
    _step(
        id="pytd-09-money",
        title="Money",
        teaches=(
            "Money is a number with two doors. In: a creep that dies pays its "
            "reward. Out: a tower costs TOWER_COST, and without enough money "
            "the click does nothing. Decide before you spend, so a refused "
            "click (on the road, on a tower, too poor) costs nothing. And pay "
            "the reward in one place only, where dead creeps are taken out: "
            "money += sum(c.reward for c in creeps if c.hp <= 0) just before "
            "the comprehension that removes them. Pay it when a shot lands "
            "instead and two shots arriving on the same frame both find a "
            "dead creep and both pay. A creep that walks off the end is taken "
            "out too but nobody killed it: only hp <= 0 pays. money is "
            "re-bound in two functions (click and update), so each says "
            "`global money`. The HUD is an f-string: f'${money}' puts the "
            "number into the text."
        ),
        goal="Add money = 100, TOWER_COST = 50 and reward 5 on every Creep. Building costs TOWER_COST (click says global money); with less money than that a click builds nothing. A creep removed because its hp ran out adds its reward to money, once; one that walked off the end pays nothing. Write the money on the screen with an f-string.",
        starter=_P[8],
        solution=_P[9],
        check="""
expect('money' in g and g.money == 100, "Start with money = 100")
expect('TOWER_COST' in g and g.TOWER_COST == 50, "Add TOWER_COST = 50 - what a tower costs.")
cc.frames(1)
expect(any('100' in t for t in cc.texts()), "Write the money on the screen, for instance f'${money}' - it should show 100 at the start.")
quiet()
click_tile(5, 3)
expect(len(g.towers) == 1 and g.money == 50, f"A tower should cost TOWER_COST: money should be 50 after the first, and is {g.money}.")
click_tile(4, 1)
click_tile(5, 3)
expect(g.money == 50, f"A click that builds nothing (on the road, or on a tower) must cost nothing; money is {g.money}. Check the tile first, then spend.")
click_tile(7, 3)
expect(len(g.towers) == 2 and g.money == 0, f"A second tower takes the last of the money: 2 towers and money 0; there are {len(g.towers)} and money is {g.money}.")
click_tile(2, 2)
expect(len(g.towers) == 2 and g.money == 0, f"With no money a click must not build, and money must not go below 0: {len(g.towers)} towers, money {g.money}.")
cc.frames(1)
expect(any('0' in t for t in cc.texts()), "The screen should show the money.")
quiet()
g.money = 0
dead = still(200, 100, 5, 0)
put(dead, 'reward', 7)
put(dead, 'hp', 0)
g.creeps = [dead]
cc.frames(1)
expect(g.money == 7 and len(g.creeps) == 0, f"A creep that dies should pay its reward (7 here) and be removed: money is {g.money}.")
cc.frames(5)
expect(g.money == 7, f"The reward was paid again after the creep was gone: money is {g.money}. Pay it once, where the dead are taken out.")
quiet()
g.money = 0
pair = still(200, 100, 5, 0)
put(pair, 'reward', 7)
first = launch(200, 100, pair, 300, 10)
second = launch(200, 100, pair, 300, 10)
g.creeps = [pair]
g.shots = [first, second]
cc.frames(3)
expect(g.money == 7, f"Two shots landed on one creep on the same frame and money is {g.money}; the creep is paid for once (7), however many shots killed it.")
quiet()
g.money = 0
ran = still(140, 290, 10, 800)
put(ran, 'reward', 7)
put(ran, 'speed', 80)
put(ran, 'leg', len(g.path) - 1)
g.creeps = [ran]
cc.frames(30)
expect(len(g.creeps) == 0 and g.money == 0, f"A creep that walked off the end was not killed and should pay nothing; money is {g.money}.")
quiet()
g.money = 100
click_tile(5, 3)
t = g.towers[0]
prey = still(get(t, 'x') + 60, get(t, 'y'), 1, 100)
put(prey, 'reward', 4)
g.creeps = [prey]
cc.frames(60)
expect(len(g.creeps) == 0 and g.money == 54, f"A tower killed a creep worth 4 with 50 left in the bank: money should be 54, it is {g.money}.")
""",
        hint="money += sum(c.reward for c in creeps if c.hp <= 0)  before the creeps filter, and in click: if ... or money < TOWER_COST: return; money -= TOWER_COST   (global money in both)",
    ),
    _step(
        id="pytd-10-waves",
        title="Waves",
        teaches=(
            "A wave is data: how many creeps, how tough - waves = [(5, 10), "
            "(8, 16), (12, 24)], each a (count, hp) tuple you can unpack in a "
            "for. A generator turns that list into a schedule: a function "
            "with `yield` does not run when called, it hands back an object, "
            "and each next(plan) runs it up to the next yield and gives you "
            "that value, remembering where it stopped. wave_plan() yields one "
            "list of hit points per wave, [hp] * count. The game becomes a "
            "small state machine: 'countdown' takes dt off countdown; 'wave' "
            "spawns from queue, one creep per SPAWN_EVERY; after the final "
            "wave it is 'won'. The thing to get right is when a wave ends: not "
            "when its last creep is spawned but when nothing is left to spawn "
            "and nothing is still walking - `not queue and not creeps`, since "
            "an empty list is falsy."
        ),
        goal="Replace the endless spawning. Add waves = [(5, 10), (8, 16), (12, 24)] (a list of (count, hp) tuples), wave = 0, state = 'countdown', countdown = 3, queue = [] (the hit points of the creeps still to send) and GAP = 5, plus a generator wave_plan() that yields one list of hp's per wave. When countdown reaches 0, wave goes up by one and queue becomes that wave's list (next(plan)); one creep, with that hp, is spawned per SPAWN_EVERY. When queue and creeps are both empty the next countdown (GAP seconds) starts; after the last wave state is 'won'. Write the wave and the countdown on the screen, and 'You win!' when won. The check changes waves in place and sets countdown, so keep them top-level.",
        starter=_P[9],
        solution=_P[10],
        check="""
expect(all(n in g for n in ('waves', 'wave', 'state', 'countdown', 'queue')) and isinstance(g.waves, list) and isinstance(g.queue, list), "Add waves (a list of (count, hp) tuples), wave = 0, state = 'countdown', countdown = 3 and queue = [].")
expect(g.wave == 0 and g.state == 'countdown' and g.countdown > 0, f"The game starts with wave 0, state 'countdown' and a few seconds on the clock; wave is {g.wave}, state is '{g.state}', countdown is {g.countdown}.")
expect(len(g.creeps) == 0, "No creeps before the first wave.")
cc.frames(1)
expect(any(re.search('wave', t, re.I) for t in cc.texts()), "Write the wave on the screen, for instance f'Wave {wave}/{len(waves)}', and 'Next wave in 3' during a countdown.")
g.waves[:] = [(2, 5), (3, 9)]
g.towers = []
seen = {}
peak = 0


def play(cond, limit, fps):
    # Play until cond() or limit frames; note every creep the first time it is seen.
    global peak
    n = 0
    while not cond() and n < limit:
        cc.frames(1, 1 / fps)
        n += 1
        peak = max(peak, len(g.creeps))
        for c in g.creeps:
            if id(c) not in seen:
                seen[id(c)] = (c, get(c, 'hp'), cc.time)
    return n


c0 = g.countdown
t0 = cc.time
play(lambda: g.wave == 1, 60 * (c0 + 3), 60)
expect(g.wave == 1 and g.state == 'wave', f"The countdown ran out and wave should be 1 with state 'wave'; wave is {g.wave}, state is '{g.state}'.")
expect(near(cc.time - t0, c0, 0.1), f"The first wave should start {c0} seconds in; it started after {cc.time - t0:.2f}. Take dt off countdown each frame.")
cc.frames(1)
expect(any(re.search(r'wave\\s*1', t, re.I) for t in cc.texts()), "Write the wave number on the screen: Wave 1.")
play(lambda: g.state != 'wave', 60 * 40, 60)
expect(g.state == 'countdown' and g.wave == 1, f"After the first wave state should be 'countdown' with wave still 1; state is '{g.state}', wave {g.wave}. (A wave is over when everything is spawned AND nothing is left walking.)")
expect(len(g.creeps) == 0, "The next countdown started while creeps were still on the road: a wave ends only when none are left.")
expect(len(seen) == 2 and peak == 2, f"Wave 1 should send 2 creeps; {len(seen)} were spawned.")
born = list(seen.values())
expect(all(hp == 5 for _, hp, _ in born), "Wave 1's creeps should have the wave's hp (5): make_creep(hp) with the hp from the wave's list.")
gap = born[1][2] - born[0][2]
expect(near(gap, g.SPAWN_EVERY, 0.1), f"The creeps of a wave come one per SPAWN_EVERY ({g.SPAWN_EVERY} seconds); these were {gap:.2f} apart.")
expect(g.countdown > 1, f"A new countdown of GAP seconds should start between waves; it is {g.countdown}.")
cc.frames(1)
expect(any(re.search('wave', t, re.I) for t in cc.texts()), "Keep the wave on the screen during the countdown.")
seen = {}
peak = 0
c1 = g.countdown
t1 = cc.time
play(lambda: g.wave == 2, 30 * (c1 + 3), 30)
expect(g.wave == 2 and g.state == 'wave', f"The second wave should start; wave is {g.wave}, state is '{g.state}'.")
expect(near(cc.time - t1, c1, 0.15), f"At 30 frames a second the second wave started after {cc.time - t1:.2f} seconds instead of {c1:.2f}. Count the countdown with dt, not frames.")
play(lambda: g.state != 'wave', 30 * 40, 30)
expect(len(seen) == 3 and peak == 3, f"Wave 2 should send 3 creeps; {len(seen)} were spawned.")
expect(all(hp == 9 for _, hp, _ in seen.values()), "Wave 2's creeps should have hp 9, from the second tuple of waves.")
expect(g.state == 'won' and g.wave == 2, f"After the last wave state should be 'won'; it is '{g.state}' with wave {g.wave}.")
cc.frames(300)
expect(g.wave == 2 and len(g.creeps) == 0 and g.state == 'won', "Once the game is won nothing else should spawn.")
expect(any(re.search('win', t, re.I) for t in cc.texts()), "Say 'You win!' on the screen when the game is won.")
""",
        hint="if not queue and not creeps: if wave == len(waves): state = 'won' else: state = 'countdown'; countdown = GAP   and   queue = next(plan) in start_wave",
    ),
    _step(
        id="pytd-11-lives",
        title="Lives and game over",
        teaches=(
            "Every creep that walks off the end costs a life. The subtle part "
            "is that it costs one life, once: if the creep stays in the list, "
            "the check that notices it fires every frame and ten lives are "
            "gone in a sixth of a second. Take the creep out as the life is "
            "taken, and count only the living ones - a creep killed on the "
            "last step is not an escape (sum(1 for c in creeps if ...) counts "
            "them). At zero the game is over: a state, like in Snake. "
            "Restarting is a function that puts every top-level name back as "
            "it was at the start - the lists, the money, the lives, the wave, "
            "the clock and the wave plan. Each name it assigns needs `global`, "
            "and here is the nasty part: a function that only ASSIGNS a name "
            "and forgets `global` raises no error - it quietly makes a "
            "local, and the restart does nothing. (creeps.clear() empties a "
            "list in place and needs no global.) Enter does it, but only when "
            "the game is over: on_key_down(fn) calls fn(key)."
        ),
        goal="Add lives = 10. A creep that reaches the end of the path (and was not killed) costs one life, once, and is removed; at 0 lives state becomes 'over', everything stops, and the screen says 'Game over'. restart() puts creeps, towers, shots, money, lives, wave, state, countdown, queue, spawn_timer and plan back as they were at the start (every name it assigns is in its global line); on_key_down calls it for Enter, but only when state is 'over'. Write the lives on the screen.",
        starter=_P[10],
        solution=_P[11],
        check="""
expect('lives' in g and isinstance(g.lives, int) and g.lives > 0, "Add lives = 10")
L0 = g.lives
M0 = g.money
C0 = g.countdown
cc.frames(1)
expect(any(re.search('live', t, re.I) and str(L0) in t for t in cc.texts()), "Write the lives on the screen, for instance f'Lives: {lives}'.")
# Start the first wave so the wave plan has moved on, then clear the field.
g.countdown = 0.01
cc.frames(3)
g.queue = []
g.creeps = []
cc.frames(2)
# Hold the next wave off while the check sets things up.
g.countdown = 1000


def runner(hp):
    c = still(140, 290, hp, 800)
    put(c, 'speed', 80)
    put(c, 'leg', len(g.path) - 1)
    return c


g.creeps = [runner(10)]
cc.frames(40)
expect(len(g.creeps) == 0, "A creep that walked off the end should be removed from creeps.")
expect(g.lives == L0 - 1, f"One creep reached the end: lives should go from {L0} to {L0 - 1}; it is {g.lives}. It costs one life, once - remove the creep as you take the life.")
cc.frames(60)
expect(g.lives == L0 - 1, f"Lives kept dropping after the creep was gone ({g.lives}). Take a life once per creep.")
killed = runner(10)
put(killed, 'leg', len(g.path))
put(killed, 'hp', 0)
g.creeps = [killed]
cc.frames(40)
expect(g.lives == L0 - 1, f"A creep that was killed on the last step cost a life (lives is {g.lives}). Only living creeps hurt.")
click_tile(5, 3)
expect(len(g.towers) == 1, "Building a tower with a click should still work.")
marker = g.money
cc.press('Enter')
cc.release('Enter')
expect(len(g.towers) == 1 and g.money == marker and g.lives == L0 - 1, "Enter in the middle of a game restarted it. Only restart when state is 'over'.")
spare = launch(10, 10, still(10, 10, 5, 0), 100, 1)
g.wave = 2
g.queue = [10, 10, 10, 10]
g.spawn_timer = 0.7
g.lives = 1
g.creeps = [runner(10)]
cc.frames(40)
expect(g.lives == 0 and g.state == 'over', f"The last life is gone and state should be 'over'; lives is {g.lives} and state is '{g.state}'.")
expect(any(re.search('game over', t, re.I) for t in cc.texts()), "When the game is over, say so on the screen: Game over.")
walker = still(20, 60, 10, 0)
put(walker, 'speed', 80)
g.creeps = [walker]
cc.frames(60)
expect(get(walker, 'x') == 20 and get(walker, 'y') == 60, "After game over everything should stop - the creeps are still walking.")
expect(g.wave == 2 and len(g.queue) == 4, "Nothing about the waves should change after game over.")
g.shots = [spare]
cc.press('ArrowLeft')
cc.release('ArrowLeft')
expect(g.state == 'over', "A key other than Enter restarted the game. Only Enter should.")
cc.press('Enter')
cc.release('Enter')
expect(g.state == 'countdown' and g.wave == 0, f"Pressing Enter after game over should start again: state 'countdown' and wave 0; state is '{g.state}' and wave {g.wave}. (restart() assigns these, so each one has to be in its global line.)")
expect(g.lives == L0 and g.money == M0, f"A new game starts with {L0} lives and {M0} money; there are {g.lives} and {g.money}.")
expect(len(g.creeps) == 0 and len(g.towers) == 0 and len(g.shots) == 0, f"A new game starts with no creeps, towers or shots; there are {len(g.creeps)}, {len(g.towers)} and {len(g.shots)}.")
expect(len(g.queue) == 0 and g.spawn_timer == 0, f"A new game starts with an empty queue and spawn_timer 0; they are {len(g.queue)} items and {g.spawn_timer}.")
expect(near(g.countdown, C0, 0.01), f"The new game's countdown should be back at {C0}; it is {g.countdown}.")
t2 = cc.time
n = 0
while g.wave == 0 and n < 60 * 20:
    cc.frames(1, 1 / 30)
    n += 1
expect(g.wave == 1 and near(cc.time - t2, C0, 0.15), f"The first wave of the new game should come after {C0} seconds; wave is {g.wave} after {cc.time - t2:.2f}.")
cc.frames(3, 1 / 30)
expect(len(g.creeps) == 1 and get(g.creeps[0], 'hp') == g.waves[0][1], "The new game's first wave should send its first creep, with the first wave's hp - restart() needs a fresh wave_plan(), or the schedule carries on from where the last game stopped.")
""",
        hint="lives = max(0, lives - sum(1 for c in creeps if c.hp > 0 and c.leg >= len(path)))  then  if lives <= 0: state = 'over'   and a restart() whose global line names everything it assigns",
    ),
    _step(
        id="pytd-12-yours",
        title="Now it's yours",
        teaches=(
            "A whole tower defense: a road that is data, walkers, health, a "
            "mouse that picks tiles, targeting, reloads, homing shots, money, "
            "waves and lives. Ideas, easier first: balance it (can you win? "
            "can anyone?); sell a tower for half its price; draw each tower's "
            "range when the mouse is over it (mouse.x, mouse.y); Enter to "
            "restart after winning too; a second tower type that is slow and "
            "hits hard, or one that slows creeps; creeps that are faster or "
            "tougher or that pay more - a wave could yield (hp, speed) pairs "
            "instead of a bare hp; a key to call the next wave early; "
            "upgrading a tower; a second map, which is only a different path "
            "list; or after(2, fn) and every(5, fn) for timed events."
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_P[11],
        solution=_P[11],
        check="",
    ),
)
