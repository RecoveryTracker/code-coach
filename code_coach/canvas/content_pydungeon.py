"""Dungeon in Python: the turn-based roguelike of the JavaScript Dungeon track, taught the Python way.

Not a transliteration. The game is the same - a map of tiles made of strings, a
turn instead of a clock (one key press, one step), a camera, a seeded
procedural generator (rooms that do not overlap, joined by corridors, all
reachable), stairs down, monsters that move after you, bump to attack, fog of
war with remembered tiles, potions, game over and again - but the parts are
Python's own:

  * the map is a list of strings (`tiles`, not `map`, which would hide the
    built-in); strings are immutable, so the generator builds a list of lists
    of characters and `"".join`s each row at the end. `[["#"] * W for _ in
    range(H)]` and the `[["#"] * W] * H` aliasing trap
  * a position is a tuple `(x, y)`: unpacked with `x, y = pos`, compared with
    `==`, put in a set or a dict, spread with `draw_tile(*pos, color)`
  * `Room` is a `@dataclass` with `center` as a property and `intersects`
    as a method; `any()` asks "does it hit one already placed"
  * `random.Random(seed)` for an instance of its own (same seed, same dungeon),
    `randint` (both ends included) against `randrange` (like range)
  * `itertools.pairwise` joins consecutive rooms; `range(min(a, b), max(a, b)
    + 1)` runs a corridor either way round; `collections.deque` for the flood
    fill (and why `list.pop(0)` is O(n))
  * a `set` of seen tiles grown with `|=` (which needs `global`, because it
    re-binds the name), slicing and `enumerate(..., start)` for the camera
  * `match` with guards for the keys, f-strings for the HUD, `global` only
    where a function re-binds a top-level name

As in the other tracks, each step starts from the one before, finished, and a
check plays the game rather than reading the code. The checks read these
top-level names (and set them): tiles, rooms, player, stairs, enemies, items,
seen, depth, potions, state, and call generate(), camera(), flood(),
visible(), update_fog(). A thing's fields may be a dict's or a dataclass's:
checks read them with get() and put(), and build a new enemy by copying one
the learner's own generator made. The generator is checked on properties of
the levels it makes over many seeds, never on a layout, so any correct
generator passes.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

TRACK = "Dungeon (Python)"

# A hand-drawn 30 by 20 map: the canvas at 16 pixels a tile, exactly.
_HAND_MAP = (
    "##############################",
    "#............#...............#",
    "#............#...............#",
    "#............#.......###.....#",
    "#............#.......#.#.....#",
    "#....................###.....#",
    "#............#...............#",
    "#............#...............#",
    "######.#######...............#",
    "#............................#",
    "#............................#",
    "#...###...........######.....#",
    "#...#.#...........#....#.....#",
    "#...#.#...........#....#.....#",
    "#...#.#...........######.....#",
    "#............................#",
    "#....########................#",
    "#............................#",
    "#............................#",
    "##############################",
)

# -- Pieces of the program --------------------------------------------------

_KEYS = """KEYS = {
    'ArrowUp': (0, -1),
    'ArrowDown': (0, 1),
    'ArrowLeft': (-1, 0),
    'ArrowRight': (1, 0),
}"""

_CLAMP = """def clamp(v, lo, hi):
    return max(lo, min(hi, v))"""

_WALLS = """def in_map(x, y):
    return 0 <= y < len(tiles) and 0 <= x < len(tiles[y])


def is_wall(x, y):
    return not in_map(x, y) or tiles[y][x] == '#'"""

_ROOM_BASE = """@dataclass
class Room:
    x: int
    y: int
    w: int
    h: int

    @property
    def center(self):
        return (self.x + self.w // 2, self.y + self.h // 2)

    def intersects(self, other):
        return (self.x <= other.x + other.w and other.x <= self.x + self.w
                and self.y <= other.y + other.h and other.y <= self.y + self.h)"""

_ROOM_TILE = """

    def random_tile(self, rng):
        return (rng.randrange(self.x, self.x + self.w),
                rng.randrange(self.y, self.y + self.h))"""

_DIG = """def dig_corridor(grid, a, b):
    (ax, ay), (bx, by) = a, b
    for x in range(min(ax, bx), max(ax, bx) + 1):
        grid[ay][x] = '.'
    for y in range(min(ay, by), max(ay, by) + 1):
        grid[y][bx] = '.'"""

_FLOOD = """def flood(start):
    reached = {start}
    todo = deque([start])
    while todo:
        x, y = todo.popleft()
        for dx, dy in KEYS.values():
            step = (x + dx, y + dy)
            if step not in reached and not is_wall(*step):
                reached.add(step)
                todo.append(step)
    return reached"""

_CAMERA = """def camera():
    px, py = player['pos']
    return (clamp(px - VIEW_W // 2, 0, len(tiles[0]) - VIEW_W),
            clamp(py - VIEW_H // 2, 0, len(tiles) - VIEW_H))"""

_VISIBLE = """def visible(x, y):
    px, py = player['pos']
    dx, dy = x - px, y - py
    if dx * dx + dy * dy > RADIUS * RADIUS:
        return False
    steps = max(abs(dx), abs(dy))
    for i in range(1, steps):
        cx = round(px + dx * i / steps)
        cy = round(py + dy * i / steps)
        if is_wall(cx, cy):
            return False
    return True


def update_fog():
    global seen
    px, py = player['pos']
    seen |= {(x, y)
             for y in range(py - RADIUS, py + RADIUS + 1)
             for x in range(px - RADIUS, px + RADIUS + 1)
             if in_map(x, y) and visible(x, y)}"""

_ENEMY_AT = """def enemy_at(pos):
    return next((e for e in enemies if e['pos'] == pos), None)"""

_PICKUP = """def pick_up():
    global potions
    pos = player['pos']
    if pos in items:
        items.remove(pos)
        potions += 1


def drink():
    global potions
    if potions == 0:
        return
    potions -= 1
    player['hp'] = min(player['max_hp'], player['hp'] + 5)
    end_turn()"""

_RESTART = """def restart():
    global depth, potions, state
    depth = 1
    player['hp'] = player['max_hp']
    potions = 0
    state = 'playing'
    generate()"""

_FRAME = """def frame(dt):
    draw()"""


def _imports(n: int) -> str:
    std = []
    if n >= 5:
        std.append("import random")
    if n >= 6:
        std.append("from collections import deque")
    if n >= 5:
        std.append("from dataclasses import dataclass")
    if n >= 6:
        std.append("from itertools import pairwise")
    names = "ctx, WIDTH, HEIGHT, on_frame" + (", on_key_down" if n >= 2 else "")
    top = "\n".join(std) + "\n\n" if std else ""
    return top + "from canvas import " + names


def _consts(n: int) -> str:
    lines = ["TILE = %d" % (32 if n >= 4 else 16)]
    if n >= 4:
        lines += ["VIEW_W = WIDTH // TILE", "VIEW_H = HEIGHT // TILE"]
    if n >= 5:
        lines += ["MAP_W = 50", "MAP_H = 30"]
    if n >= 9:
        lines += ["PLAYER_DAMAGE = 2", "ENEMY_DAMAGE = 1"]
    if n >= 10:
        lines += ["RADIUS = 6"]
    out = "\n".join(lines)
    if n >= 2:
        out += "\n\n" + _KEYS
    return out


def _state(n: int) -> str:
    if n >= 5:
        lines = ["tiles = []", "rooms = []"]
    else:
        lines = ["tiles = [", *("    '%s'," % row for row in _HAND_MAP), "]"]
    if n >= 2:
        if n >= 9:
            lines.append("player = {'pos': (1, 1), 'hp': 10, 'max_hp': 10}")
        else:
            lines.append("player = {'pos': (1, 1)}")
    if n >= 7:
        lines += ["stairs = (0, 0)", "depth = 1"]
    if n >= 8:
        lines.append("enemies = []")
    if n >= 11:
        lines += ["items = []", "potions = 0"]
    if n >= 10:
        lines.append("seen = set()")
    if n >= 12:
        lines.append("state = 'playing'")
    return "\n".join(lines)


def _generate(n: int) -> str:
    names = ["tiles", "rooms"]
    if n >= 7:
        names.append("stairs")
    if n >= 8:
        names.append("enemies")
    if n >= 11:
        names.append("items")
    if n >= 10:
        names.append("seen")
    s = "def generate(seed=None):\n    global " + ", ".join(names) + "\n"
    s += """    rng = random.Random(seed)
    grid = [['#'] * MAP_W for _ in range(MAP_H)]
    rooms = []
    for _ in range(60):
        if len(rooms) == 8:
            break
        w = rng.randint(4, 9)
        h = rng.randint(4, 7)
        room = Room(rng.randint(1, MAP_W - w - 1), rng.randint(1, MAP_H - h - 1), w, h)
        if any(room.intersects(other) for other in rooms):
            continue
        rooms.append(room)
        for y in range(room.y, room.y + room.h):
            for x in range(room.x, room.x + room.w):
                grid[y][x] = '.'
"""
    if n >= 6:
        s += """    for a, b in pairwise(rooms):
        dig_corridor(grid, a.center, b.center)
"""
    s += "    tiles = [''.join(row) for row in grid]\n"
    if n >= 6:
        s += """    floor = {(x, y) for y, row in enumerate(tiles) for x, ch in enumerate(row) if ch == '.'}
    assert flood(rooms[0].center) == floor, 'some rooms are cut off'
"""
    s += "    player['pos'] = rooms[0].center\n"
    if n >= 7:
        s += "    stairs = rooms[-1].center\n"
    if n >= 8:
        hp = ", 'hp': 4" if n >= 9 else ""
        s += """    enemies = []
    for room in rooms[1:]:
        spot = room.random_tile(rng)
        if spot != stairs:
            enemies.append({'pos': spot%s})
""" % hp
    if n >= 11:
        s += "    items = [room.random_tile(rng) for room in rooms[1:] if rng.random() < 0.6]\n"
    if n >= 10:
        s += "    seen = set()\n    update_fog()\n"
    return s.rstrip("\n")


def _enemies_act(n: int) -> str:
    attack = ""
    if n >= 9:
        attack = """        if abs(dx) + abs(dy) == 1:
            player['hp'] -= ENEMY_DAMAGE
            continue
"""
    s = """def enemies_act():
    for e in enemies:
        ex, ey = e['pos']
        px, py = player['pos']
        dx, dy = px - ex, py - ey
""" + attack + """        step_x, step_y = clamp(dx, -1, 1), clamp(dy, -1, 1)
        tries = [(step_x, 0), (0, step_y)] if abs(dx) >= abs(dy) else [(0, step_y), (step_x, 0)]
        for sx, sy in tries:
            nx, ny = ex + sx, ey + sy
            if (sx, sy) == (0, 0) or is_wall(nx, ny) or (nx, ny) == player['pos']:
                continue
            e['pos'] = (nx, ny)
            break


def end_turn():
"""
    if n >= 12:
        s += "    global state\n"
    s += "    enemies_act()\n"
    if n >= 10:
        s += "    update_fog()\n"
    if n >= 12:
        s += "    if player['hp'] <= 0:\n        state = 'over'\n"
    return s.rstrip("\n")


def _move(n: int) -> str:
    s = "def move(dx, dy):\n"
    if n >= 7:
        s += "    global depth\n"
    s += """    x, y = player['pos']
    nx, ny = x + dx, y + dy
    if is_wall(nx, ny):
        return
"""
    if n >= 9:
        s += """    target = enemy_at((nx, ny))
    if target is not None:
        target['hp'] -= PLAYER_DAMAGE
        if target['hp'] <= 0:
            enemies.remove(target)
        end_turn()
        return
"""
    s += "    player['pos'] = (nx, ny)\n"
    if n >= 11:
        s += "    pick_up()\n"
    if n >= 7:
        s += "    if player['pos'] == stairs:\n        depth += 1\n        generate()\n"
        if n >= 8:
            s += "        return\n"
    if n >= 8:
        s += "    end_turn()\n"
    return s.rstrip("\n")


def _key_down(n: int) -> str:
    if n == 2:
        s = """def key_down(key):
    if key in KEYS:
        dx, dy = KEYS[key]
        x, y = player['pos']
        player['pos'] = (x + dx, y + dy)"""
    elif n <= 10:
        s = """def key_down(key):
    if key in KEYS:
        move(*KEYS[key])"""
    elif n == 11:
        s = """def key_down(key):
    match key:
        case 'h':
            drink()
        case 'ArrowUp' | 'ArrowDown' | 'ArrowLeft' | 'ArrowRight':
            move(*KEYS[key])"""
    else:
        s = """def key_down(key):
    match key:
        case 'Enter' if state == 'over':
            restart()
        case _ if state == 'over':
            pass
        case 'h':
            drink()
        case 'ArrowUp' | 'ArrowDown' | 'ArrowLeft' | 'ArrowRight':
            move(*KEYS[key])"""
    return s + "\n\n\non_key_down(key_down)"


def _draw_tile(n: int) -> str:
    if n < 4:
        return """def draw_tile(x, y, color):
    ctx.fill_style = color
    ctx.fill_rect(x * TILE, y * TILE, TILE, TILE)"""
    return """def draw_tile(x, y, color):
    cam_x, cam_y = camera()
    ctx.fill_style = color
    ctx.fill_rect((x - cam_x) * TILE, (y - cam_y) * TILE, TILE, TILE)"""


def _draw(n: int) -> str:
    fog = n >= 10
    s = """def draw():
    ctx.fill_style = '#10141f'
    ctx.fill_rect(0, 0, WIDTH, HEIGHT)
"""
    if n < 4:
        s += """    for y, row in enumerate(tiles):
        for x, ch in enumerate(row):
            draw_tile(x, y, '#4a5568' if ch == '#' else '#2d3748')
"""
    else:
        s += """    cam_x, cam_y = camera()
    for y, row in enumerate(tiles[cam_y:cam_y + VIEW_H], cam_y):
        for x, ch in enumerate(row[cam_x:cam_x + VIEW_W], cam_x):
"""
        if fog:
            s += """            if visible(x, y):
                draw_tile(x, y, '#4a5568' if ch == '#' else '#2d3748')
            elif (x, y) in seen:
                draw_tile(x, y, '#262c37' if ch == '#' else '#1c2230')
"""
        else:
            s += "            draw_tile(x, y, '#4a5568' if ch == '#' else '#2d3748')\n"
    if n >= 7:
        if fog:
            s += "    if stairs in seen:\n        draw_tile(*stairs, '#b794f4')\n"
        else:
            s += "    draw_tile(*stairs, '#b794f4')\n"
    if n >= 11:
        s += "    for pos in items:\n        if visible(*pos):\n            draw_tile(*pos, '#f6e05e')\n"
    if n >= 8:
        if fog:
            s += "    for e in enemies:\n        if visible(*e['pos']):\n            draw_tile(*e['pos'], '#f56565')\n"
        else:
            s += "    for e in enemies:\n        draw_tile(*e['pos'], '#f56565')\n"
    if n >= 2:
        s += "    draw_tile(*player['pos'], '#4fd1c5')\n"
    if n >= 7:
        s += "    ctx.fill_style = 'white'\n    ctx.font = '16px monospace'\n"
        s += "    ctx.fill_text(f'Depth: {depth}', 8, 20)\n"
        if n >= 9:
            s += "    ctx.fill_text(f\"HP: {player['hp']}/{player['max_hp']}\", 8, 40)\n"
        if n >= 11:
            s += "    ctx.fill_text(f'Potions: {potions}', 8, 60)\n"
    if n >= 12:
        s += """    if state == 'over':
        ctx.font = '32px monospace'
        ctx.fill_text('Game over', 150, 160)
        ctx.font = '16px monospace'
        ctx.fill_text('Enter to play again', 150, 190)
"""
    return s.rstrip("\n")


def _game(n: int) -> str:
    """The whole program as it stands when step n is finished (0: the empty start)."""
    if n == 0:
        return (
            "from canvas import ctx, WIDTH, HEIGHT, on_frame\n\n\n"
            "def draw():\n    ctx.fill_style = '#10141f'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n\n\n"
            + _FRAME + "\n\n\non_frame(frame)\n"
        )
    head = _imports(n) + "\n\n" + _consts(n) + ("\n\n\n" if n >= 5 else "\n\n")
    if n >= 5:
        head += _ROOM_BASE + (_ROOM_TILE if n >= 8 else "") + "\n\n\n"
    head += _state(n)
    blocks = []
    if n >= 4:
        blocks.append(_CLAMP)
    if n >= 3:
        blocks.append(_WALLS)
    if n >= 6:
        blocks += [_DIG, _FLOOD]
    if n >= 4:
        blocks.append(_CAMERA)
    if n >= 10:
        blocks.append(_VISIBLE)
    if n >= 5:
        blocks.append(_generate(n))
    if n >= 9:
        blocks.append(_ENEMY_AT)
    if n >= 11:
        blocks.append(_PICKUP)
    if n >= 8:
        blocks.append(_enemies_act(n))
    if n >= 3:
        blocks.append(_move(n))
    if n >= 12:
        blocks.append(_RESTART)
    if n >= 2:
        blocks.append(_key_down(n))
    blocks.append(_draw_tile(n))
    blocks.append(_draw(n))
    blocks.append(_FRAME)
    tail = ("generate()\n" if n >= 5 else "") + "on_frame(frame)\n"
    return head + "\n\n\n" + "\n\n\n".join(blocks) + "\n\n\n" + tail


_P = [_game(i) for i in range(13)]

# -- Shared by the checks ----------------------------------------------------

#: Prepended to every check. A thing's fields can be a dict's or an object's, so
#: a check reads them with get() and never cares which the learner chose.
#: press is one key press as a turn-based game wants it: down, up, and a frame
#: so a game that reads its input in the frame loop sees it too.
_HELPERS = """
import copy
import dataclasses
import inspect
import random


def get(o, k, default=None):
    if isinstance(o, dict):
        return o.get(k, default)
    return getattr(o, k, default)


def put(o, k, v):
    if isinstance(o, dict):
        o[k] = v
    else:
        setattr(o, k, v)


def pos_of(o):
    p = get(o, 'pos')
    return tuple(p) if isinstance(p, (list, tuple)) else p


def at():
    return pos_of(g.player)


def put_player(x, y):
    put(g.player, 'pos', (x, y))


def press(key):
    cc.press(key)
    cc.release(key)
    cc.frames(1)


def arena(walls=(), border=False):
    w = len(g.tiles[0])
    h = len(g.tiles)
    wall = set(walls)
    rows = []
    for y in range(h):
        row = ''
        for x in range(w):
            edge = border and (x in (0, w - 1) or y in (0, h - 1))
            row += '#' if edge or (x, y) in wall else '.'
        rows.append(row)
    g.tiles = rows


"""

#: What was drawn where, once there is a camera (step 4 on).
_DRAWN = """
def drawn_at():
    found = {}
    for r in cc.rects():
        found[(r['x'], r['y'])] = r
    return found


def tile_fill(tx, ty):
    cam_x, cam_y = g.camera()
    r = drawn_at().get(((tx - cam_x) * g.TILE, (ty - cam_y) * g.TILE))
    return r['fill'] if r is not None and r['w'] >= g.TILE - 1 else None


"""

#: The generator's checks: properties of a level, and a flood fill that is the
#: check's own, not the learner's. regen(seed) seeds the module's random AND hands
#: the seed to generate() if it takes one, so a generator that draws from
#: random.Random(seed) and one that draws from random.randint both play fair.
_LEVELS = """
_Real = random.Random
_n = [0]


class _Det(_Real):
    # random.Random() with no seed would be different on every run of the check; here it is a
    # fresh seed from a counter instead, so a check always plays the same game. random.Random(7)
    # is untouched, and a program that never passes a seed still gets a different level each time.
    def __init__(self, x=None):
        if x is None:
            _n[0] += 1
            x = 900000 + _n[0]
        super().__init__(x)


random.Random = _Det


def regen(s):
    random.seed(s)
    try:
        params = inspect.signature(g.generate).parameters.values()
    except (TypeError, ValueError):
        params = []
    takes = any(p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.VAR_POSITIONAL) for p in params)
    if takes:
        g.generate(s)
    else:
        g.generate()


def box(r):
    return get(r, 'x'), get(r, 'y'), get(r, 'w'), get(r, 'h')


def describe(r):
    x, y, w, h = box(r)
    return f'x {x}, y {y}, {w} by {h}'


def in_room(p, r):
    x, y, w, h = box(r)
    return x <= p[0] < x + w and y <= p[1] < y + h


def room_of(p):
    for i, r in enumerate(g.rooms):
        if in_room(p, r):
            return i
    return -1


def floors():
    return {(x, y) for y, row in enumerate(g.tiles) for x, ch in enumerate(row) if ch == '.'}


def reach(start, fl):
    got = {start}
    todo = [start]
    while todo:
        x, y = todo.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n in fl and n not in got:
                got.add(n)
                todo.append(n)
    return got


def check_level(tag):
    t = g.tiles
    expect(isinstance(t, (list, tuple)) and len(t) == g.MAP_H and all(isinstance(row, str) and len(row) == g.MAP_W for row in t),
           f'{tag}: after generate(), tiles should be MAP_H strings of MAP_W characters each. Build the grid as lists of characters and join each row: [chr for chr in row] -> "".join(row).')
    expect(isinstance(g.rooms, list) and len(g.rooms) >= 3, f'{tag}: generate() made {len(g.rooms) if isinstance(g.rooms, list) else 0} rooms; a level should have several (keep trying to place rooms until there are a handful).')
    W, H = g.MAP_W, g.MAP_H
    for r in g.rooms:
        x, y, w, h = box(r)
        expect(all(isinstance(v, int) for v in (x, y, w, h)) and w >= 2 and h >= 2, f'{tag}: every room has whole-number x, y, w, h - at least 2 tiles each way.')
        expect(x >= 1 and y >= 1 and x + w <= W - 1 and y + h <= H - 1, f'{tag}: a room at {describe(r)} runs into the edge of the {W} by {H} map. Keep a wall all round the edge: x from 1 to MAP_W - w - 1 and y from 1 to MAP_H - h - 1 (randint includes both ends).')
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                expect(t[yy][xx] == '.', f'{tag}: the room at {describe(r)} is not all floor - column {xx}, row {yy} is {t[yy][xx]!r}.')
    for i, a in enumerate(g.rooms):
        for b in g.rooms[i + 1:]:
            ax, ay, aw, ah = box(a)
            bx, by, bw, bh = box(b)
            overlap = ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah
            expect(not overlap, f'{tag}: two rooms overlap ({describe(a)} and {describe(b)}). Throw a room away if it intersects one already placed.')
    expect(all(c == '#' for c in t[0]) and all(c == '#' for c in t[H - 1]), f'{tag}: the top and bottom rows of the map should be wall all the way along. (If every row is the same, the grid was made with [row] * MAP_H: that repeats ONE row. Use a comprehension: [["#"] * MAP_W for _ in range(MAP_H)].)')
    expect(all(row[0] == '#' and row[W - 1] == '#' for row in t), f'{tag}: the first and last column of the map should be wall all the way down.')
    p = at()
    expect(isinstance(p, tuple) and len(p) == 2 and in_room(p, g.rooms[0]) and t[p[1]][p[0]] == '.', f'{tag}: the player is at {p}, not inside the first room. Put the player in the center of rooms[0].')


def sound_stairs(tag):
    s = g.stairs
    expect(isinstance(s, tuple) and len(s) == 2 and all(isinstance(v, int) for v in s) and g.tiles[s[1]][s[0]] == '.', f'{tag}: stairs should be an (x, y) tuple on a floor tile; it is {s!r}.')
    expect(room_of(s) != -1, f'{tag}: the stairs are not inside a room.')
    expect(room_of(s) != room_of(at()), f'{tag}: the stairs are in the same room as the player. Put them in a different room - the last one in the list.')
    expect(s != at(), f'{tag}: the player starts on the stairs.')


"""

#: A copy of an enemy the learner's own generator made, so a check can build more
#: of the same kind whether it is a dict or a dataclass.
_ENEMIES = """
regen(3)
expect(isinstance(g.enemies, list) and len(g.enemies) >= 1, 'Level 3 has no enemies. Put one on a random tile of every room except the first.')
PROTO = copy.deepcopy(g.enemies[0])


def mk(p, hp=None):
    e = copy.deepcopy(PROTO)
    put(e, 'pos', tuple(p))
    if hp is not None:
        put(e, 'hp', hp)
    return e


def enemy_pos(i=0):
    return pos_of(g.enemies[i])


"""

# -- The checks ---------------------------------------------------------------

_CHECK1 = """
expect(getattr(g, 'TILE', None) == 16, 'Add TILE = 16 - the size of one tile in pixels.')
tiles = g.tiles
expect(isinstance(tiles, (list, tuple)) and len(tiles) == 20, 'Make tiles a list of 20 strings - one string per row.')
for y in range(20):
    expect(isinstance(tiles[y], str) and len(tiles[y]) == 30, f'Row {y} of tiles should be a string of exactly 30 characters (a 30 by 20 map of 16 pixel tiles fills the 480 by 320 canvas).')
    expect(set(tiles[y]) <= {'#', '.'}, f"Row {y} has a character that is not '#' or '.'.")
expect(all(tiles[0][x] == '#' and tiles[19][x] == '#' for x in range(30)), 'The top and bottom rows should be wall all the way along.')
expect(all(tiles[y][0] == '#' and tiles[y][29] == '#' for y in range(20)), 'The first and last column should be wall all the way down.')
expect(tiles[1][1] == '.', 'Column 1, row 1 should be floor - the player will start there. tiles[1][1] is the second character of the second string.')
inner = sum(tiles[y][x] == '#' for y in range(1, 19) for x in range(1, 29))
expect(inner >= 5, 'Put a few walls inside the map too - a pillar, a short wall - so there is something to walk round.')
cc.frames(1)
drawn = {(r['x'], r['y']): r for r in cc.rects()}
wall_fills = set()
floor_fills = set()
for y in range(20):
    for x in range(30):
        r = drawn.get((x * g.TILE, y * g.TILE))
        expect(r is not None and r['w'] >= g.TILE - 1 and r['h'] >= g.TILE - 1, f'The tile at column {x}, row {y} is not drawn. It belongs at pixel x {x * g.TILE}, y {y * g.TILE}: fill_rect(x * TILE, y * TILE, TILE, TILE), once for every character of every row.')
        (wall_fills if tiles[y][x] == '#' else floor_fills).add(r['fill'])
expect(not (wall_fills & floor_fills), "Walls and floor are drawn in the same colour. Set fill_style by what the character is: '#' one colour, '.' another.")
"""

_CHECK2 = _HELPERS + """
expect('player' in g, "Make a player: player = {'pos': (1, 1)} - its position is a tuple, (x, y), in tiles.")
p0 = get(g.player, 'pos')
expect(isinstance(p0, tuple) and p0 == (1, 1), f"The player starts at column 1, row 1, and its position is a tuple: player = {{'pos': (1, 1)}}. Yours is {p0!r}.")
cc.frames(1)
drawn = {(r['x'], r['y']): r for r in cc.rects()}
floor_fill = None
for y, row in enumerate(g.tiles):
    for x, ch in enumerate(row):
        if ch == '.' and (x, y) != (1, 1) and floor_fill is None:
            floor_fill = drawn.get((x * g.TILE, y * g.TILE), {}).get('fill')
me = drawn.get((g.TILE, g.TILE))
expect(me is not None and me['fill'] != floor_fill, "Draw the player after the map, as a tile in a colour of its own: fill_rect(x * TILE, y * TILE, TILE, TILE) at the player's position.")
press('ArrowRight')
expect(at() == (2, 1), f'ArrowRight should move the player one tile right, to (2, 1); it is at {at()}. Positions are in tiles, so add 1, not TILE.')
expect(isinstance(get(g.player, 'pos'), tuple), "The position should stay a tuple: player['pos'] = (x + dx, y + dy). A tuple cannot be changed, so a move builds a new one.")
press('ArrowDown')
expect(at() == (2, 2), f'ArrowDown should move the player one tile down, to (2, 2); it is at {at()}. y grows downwards.')
press('ArrowLeft')
expect(at() == (1, 2), f'ArrowLeft should move the player one tile left, to (1, 2); it is at {at()}.')
press('ArrowUp')
expect(at() == (1, 1), f'ArrowUp should move the player one tile up, to (1, 1); it is at {at()}.')
press('q')
cc.frames(10)
expect(at() == (1, 1), 'A key that is not an arrow should do nothing. Ask `if key in KEYS` before looking the key up.')
cc.frames(60)
expect(at() == (1, 1), 'The player moves on its own. In a turn-based game nothing happens until a key is pressed.')
cc.press('ArrowRight')
cc.frames(30)
cc.release('ArrowRight')
expect(at() == (2, 1), f'Holding ArrowRight for half a second left the player at {at()}. A press is one step, however long the key stays down - do the step in the on_key_down handler, not once per frame while the key is in `keys`.')
"""

_CHECK3 = _HELPERS + """
W = len(g.tiles[0])
H = len(g.tiles)
arena([(10, 3)], False)
for key, x, y, where in [('ArrowRight', 9, 3, 'left of'), ('ArrowLeft', 11, 3, 'right of'), ('ArrowDown', 10, 2, 'above'), ('ArrowUp', 10, 4, 'below')]:
    put_player(x, y)
    press(key)
    expect(at() == (x, y), f"The player stood {where} a wall tile and walked into it (it is at {at()}). Work out the tile you would step onto, and stay put if it is '#'.")
put_player(3, 10)
press('ArrowRight')
expect(at() == (4, 10), f'With a wall only at column 10, row 3, the player at column 3, row 10 should be free to step right - it is at {at()}. Is the map read as tiles[y][x], row first?')
put_player(9, 4)
press('ArrowRight')
expect(at() == (10, 4), 'The tile beside a wall (column 10, row 4) is open floor but the player was stopped. Check only the tile it is stepping onto.')
arena([], False)
for x, y, key in [(0, 0, 'ArrowLeft'), (0, 0, 'ArrowUp'), (W - 1, H - 1, 'ArrowRight'), (W - 1, H - 1, 'ArrowDown'),
                  (W - 1, 0, 'ArrowRight'), (W - 1, 0, 'ArrowUp'), (0, H - 1, 'ArrowLeft'), (0, H - 1, 'ArrowDown')]:
    put_player(x, y)
    press(key)
    expect(at() == (x, y), f'At column {x}, row {y} the player walked off the edge of the map with {key} (it is at {at()}). Anything off the map counts as a wall - check 0 <= x < len(tiles[y]) before reading tiles[y][x]. Python will not stop you: tiles[-1] is the LAST row, not an error.')
put_player(0, 0)
press('ArrowRight')
press('ArrowDown')
expect(at() == (1, 1), f'Along the edge the player should still move freely; it is at {at()}.')
"""

_CHECK4 = _HELPERS + _DRAWN + """
expect(getattr(g, 'TILE', None) == 32, 'Zoom in: TILE = 32 - then a 480 by 320 canvas shows 15 by 10 tiles.')
vw, vh = getattr(g, 'VIEW_W', None), getattr(g, 'VIEW_H', None)
expect(isinstance(vw, int) and isinstance(vh, int) and (vw, vh) == (15, 10), f'Add VIEW_W = WIDTH // TILE and VIEW_H = HEIGHT // TILE: how many tiles fit across and down (15 and 10). Use //, not / - a float like 15.0 cannot be a slice or a range. Yours are {vw!r} and {vh!r}.')
expect(callable(getattr(g, 'camera', None)), 'Write def camera(): it returns (cam_x, cam_y), the tile at the top-left of the view, worked out from the player.')
arena([], False)
W = len(g.tiles[0])
H = len(g.tiles)


def place(x, y):
    put_player(x, y)
    cc.frames(1)


place(1, 1)
cam = g.camera()
expect(isinstance(cam, (tuple, list)) and len(cam) == 2 and all(isinstance(v, int) for v in cam), f'camera() should return two whole numbers, (cam_x, cam_y); it returned {cam!r}.')
expect(tuple(cam) == (0, 0), f'Near the top-left corner the camera is at {tuple(cam)}; it should stop at (0, 0) rather than show what is beyond the map. Clamp it: max(0, min(map width - VIEW_W, ...)).')
place(W - 2, H - 2)
cam = tuple(g.camera())
expect(cam == (W - vw, H - vh), f"Near the bottom-right corner the camera is at {cam}; it should stop at {(W - vw, H - vh)} (the map's size minus the view's) so the map's edge sits at the edge of the screen.")
mx, my = W // 2, H // 2
place(mx, my)
cam = tuple(g.camera())
expect(abs(mx - cam[0] - (vw - 1) / 2) <= 1, f"In the middle of the map the player is at column {mx} and the camera's left edge at {cam[0]}: the player should be in the middle of the view, about {(vw - 1) / 2} tiles in. cam_x = px - VIEW_W // 2.")
expect(abs(my - cam[1] - (vh - 1) / 2) <= 1, f"In the middle of the map the player is at row {my} and the camera's top edge at {cam[1]}: the player should be in the middle of the view. cam_y = py - VIEW_H // 2.")
arena([(mx + 2, my)], False)
cc.frames(1)
floor_fill = tile_fill(mx - 2, my)
wall_fill = tile_fill(mx + 2, my)
player_fill = tile_fill(mx, my)
expect(floor_fill is not None and wall_fill is not None and player_fill is not None, 'A tile near the player is not drawn where the camera says it should be: draw tile (x, y) at ((x - cam_x) * TILE, (y - cam_y) * TILE) - for the map AND the player.')
expect(wall_fill != floor_fill and player_fill != floor_fill, 'The wall, the floor and the player should be three different colours.')
cam = tuple(g.camera())
for y in range(cam[1], cam[1] + vh):
    for x in range(cam[0], cam[0] + vw):
        expect(tile_fill(x, y) is not None, f'The tile at column {x}, row {y} is in view but not drawn at ((x - cam_x) * TILE, (y - cam_y) * TILE).')
place(W - 2, H - 2)
press('ArrowLeft')
expect(tuple(g.camera()) == (W - vw, H - vh), 'The camera should keep following as the player moves.')
"""

_CHECK5 = _HELPERS + _LEVELS + """
expect(callable(getattr(g, 'generate', None)), 'Write def generate(seed=None) that builds a whole level and is called once at the start.')
expect(getattr(g, 'MAP_W', None) == 50 and getattr(g, 'MAP_H', None) == 30, 'Add MAP_W = 50 and MAP_H = 30 - the size of the dungeon in tiles.')
expect(isinstance(g.rooms, list), 'Keep the rooms in rooms = [] - each one a Room(x, y, w, h): the top-left tile and the size in tiles.')
for s in range(1, 31):
    regen(s * 7919)
    check_level('Level ' + str(s))
regen(11)
first = list(g.tiles)
regen(11)
expect(first == list(g.tiles), 'Calling generate with the same seed twice made two different dungeons. Make one rng = random.Random(seed) and take every random number from it (rng.randint, rng.random). random.Random() with no seed is different every time.')
regen(11)
a = tuple(g.tiles)
regen(12)
b = tuple(g.tiles)
regen(13)
c = tuple(g.tiles)
expect(len({a, b, c}) > 1, 'Three different seeds made the same dungeon. Every room should be placed with numbers from the rng.')
cc.frames(1)
"""

_CHECK6 = _HELPERS + _LEVELS + """
expect(callable(getattr(g, 'generate', None)) and isinstance(g.rooms, list), 'Keep generate() and rooms from the last step.')
for s in range(1, 31):
    regen(s * 104729)
    check_level('Level ' + str(s))
    fl = floors()
    got = reach(at(), fl)
    expect(got == fl, f'Level {s}: {len(fl) - len(got)} of the {len(fl)} floor tiles cannot be reached from the player - some rooms are cut off from the rest. Dig a corridor from each room to the one before it (itertools.pairwise gives the pairs).')
    inside = sum(get(r, 'w') * get(r, 'h') for r in g.rooms)
    expect(len(fl) > inside, f'Level {s}: there is no floor outside the rooms - dig corridors between them.')
expect(callable(getattr(g, 'flood', None)), 'Write def flood(start): a set of every floor tile reachable from start - a deque of tiles still to visit, and a set of the ones already reached.')
saved = g.tiles
g.tiles = ['#########', '#..#....#', '#..#.##.#', '#..#....#', '#########']
left = {(1, 1), (2, 1), (1, 2), (2, 2), (1, 3), (2, 3)}
right = {(4, 1), (5, 1), (6, 1), (7, 1), (4, 2), (7, 2), (4, 3), (5, 3), (6, 3), (7, 3)}
got = {tuple(c) for c in g.flood((1, 1))}
expect(got == left, f'flood((1, 1)) on a map with a wall down column 3 should give just the six tiles of the left room; it gave {sorted(got ^ left)[:4]} too many or too few. Step to the four neighbours, skip walls, and never visit a tile twice.')
got = {tuple(c) for c in g.flood((7, 3))}
expect(got == right, f'flood((7, 3)) should give the ten floor tiles of the right-hand side and stop at the wall; it was out by {sorted(got ^ right)[:4]}.')
g.tiles = ['...', '...']
got = {tuple(c) for c in g.flood((0, 0))}
every = {(x, y) for x in range(3) for y in range(2)}
expect(got == every, f'On an open 3 by 2 map flood((0, 0)) should give all six tiles and then stop at the edge of the map; it gave {sorted(got)}. Anything off the map is a wall.')
g.tiles = saved
"""

_CHECK7 = _HELPERS + _LEVELS + _DRAWN + """
expect(isinstance(getattr(g, 'stairs', None), tuple) and isinstance(getattr(g, 'depth', None), int), 'Add stairs = (0, 0), a position tuple, and depth = 1.')
expect(g.depth == 1, 'A game starts at depth 1.')
for s in range(1, 21):
    regen(s * 3331)
    sound_stairs('Level ' + str(s))
dirs = [('ArrowRight', 1, 0), ('ArrowLeft', -1, 0), ('ArrowDown', 0, 1), ('ArrowUp', 0, -1)]


def beside_stairs():
    for key, dx, dy in dirs:
        nx, ny = g.stairs[0] - dx, g.stairs[1] - dy
        if g.tiles[ny][nx] == '.':
            put_player(nx, ny)
            return key
    raise AssertionError('no floor beside the stairs')


regen(4242)
g.depth = 1
key = beside_stairs()
cc.frames(1)
cam = g.camera()
floor_fill = None
for y in range(cam[1], cam[1] + g.VIEW_H):
    for x in range(cam[0], cam[0] + g.VIEW_W):
        if g.tiles[y][x] == '.' and (x, y) not in (at(), g.stairs) and floor_fill is None:
            floor_fill = tile_fill(x, y)
sf = tile_fill(*g.stairs)
expect(sf is not None and sf != floor_fill, 'Draw the stairs as a tile in a colour of their own, after the map: draw_tile(*stairs, color).')
expect(any('depth' in t.lower() and '1' in t for t in cc.texts()), "Write the depth on the screen: 'Depth: 1' - an f-string does it: f'Depth: {depth}'.")
for k, dx, dy in dirs:
    tx, ty = at()[0] + dx, at()[1] + dy
    if g.tiles[ty][tx] == '.' and (tx, ty) != g.stairs:
        before = '|'.join(g.tiles)
        press(k)
        expect(g.depth == 1 and '|'.join(g.tiles) == before, 'Stepping somewhere that is not the stairs changed the level. Only the stairs go down.')
        break
before = '|'.join(g.tiles)
key = beside_stairs()
press(key)
expect(g.depth == 2, f'The player stepped onto the stairs and depth is {g.depth}; it should be 2. depth is re-bound in move(), so it needs `global depth`.')
expect('|'.join(g.tiles) != before, 'Depth went up but the level is the same. Call generate() as well, to build a new one.')
check_level('The new level')
sound_stairs('The new level')
cc.frames(1)
expect(any('depth' in t.lower() and '2' in t for t in cc.texts()), 'The depth on the screen should now say 2.')
"""

_CHECK8 = _HELPERS + _LEVELS + _DRAWN + _ENEMIES + """
for s in range(1, 121):
    regen(s * 6151)
    expect(isinstance(g.enemies, list) and len(g.enemies) >= 1, f'Level {s} has no enemies. Put one on a random tile of every room except the first.')
    for e in g.enemies:
        ep = pos_of(e)
        expect(isinstance(ep, tuple) and len(ep) == 2 and g.tiles[ep[1]][ep[0]] == '.', f'Level {s}: an enemy at {ep} is not on a floor tile. Each enemy has a pos, an (x, y) tuple.')
        expect(not in_room(ep, g.rooms[0]), f"Level {s}: an enemy starts in the player's own room - leave the first room empty.")
        expect(ep != g.stairs, f'Level {s}: an enemy starts on the stairs.')


def setup(px, py, foes, walls=()):
    arena(walls, True)
    put_player(px, py)
    g.enemies = [mk(c) for c in foes]


def dist(i=0):
    ex, ey = enemy_pos(i)
    px, py = at()
    return abs(ex - px) + abs(ey - py)


setup(10, 10, [(15, 10)])
press('ArrowUp')
expect(at() == (10, 9), f'The player should have stepped up to (10, 9); it is at {at()}.')
ex, ey = enemy_pos()
expect(abs(ex - 15) + abs(ey - 10) == 1, f"After the player's step the enemy should have moved exactly one tile - up, down, left or right. It was at (15, 10) and is at {(ex, ey)}.")
expect(dist() == 5, f'The enemy should have moved toward the player (distance 6 before its move, 5 after) but it is {dist()} away.')
setup(10, 10, [(15, 10)])
cc.frames(120)
expect(enemy_pos() == (15, 10), 'The enemy moved while the player did nothing. In a turn-based game they only move after the player does - not on the frame loop.')
setup(1, 10, [(6, 10)])
press('ArrowLeft')
expect(at() == (1, 10) and enemy_pos() == (6, 10), 'The player walked into a wall, which is not a turn - but the enemy moved. Return from move() before the enemies act.')
setup(10, 10, [(15, 12)], [(11, 10)])
press('ArrowRight')
expect(at() == (10, 10) and enemy_pos() == (15, 12), 'Bumping into an inner wall is not a turn either - the enemy moved.')
setup(10, 10, [(12, 10)])
press('ArrowRight')
expect(at() == (11, 10), f'The player should have stepped right to column 11; it is at {at()}.')
expect(enemy_pos() == (12, 10), f"The enemy was two tiles away and the player stepped toward it. It should wait next to the player at (12, 10); it is at {enemy_pos()}. Enemies move AFTER the player, and never onto the player's tile.")
setup(5, 5, [(20, 12)])
for i in range(60):
    if dist() <= 3:
        break
    press('ArrowRight' if i % 2 == 0 else 'ArrowLeft')
    ex, ey = enemy_pos()
    expect(g.tiles[ey][ex] == '.', f'Turn {i + 1}: the enemy is on {(ex, ey)}, which is not floor.')
    expect((ex, ey) != at(), f"Turn {i + 1}: the enemy is on the player's tile.")
expect(dist() <= 3, f'After 60 turns the enemy is still {dist()} tiles from the player, who barely moved. It should have walked right up.')
column = [(12, y) for y in range(6, 15)]
setup(8, 10, [(16, 10), (16, 12)], column)
for i in range(60):
    press('ArrowUp' if i % 2 == 0 else 'ArrowDown')
    for k in range(2):
        ex, ey = enemy_pos(k)
        expect(0 <= ey < len(g.tiles) and 0 <= ex < len(g.tiles[ey]) and g.tiles[ey][ex] == '.', f'Turn {i + 1}: an enemy walked into {(ex, ey)}, which is a wall or off the map. Enemies are blocked by walls: test the tile before stepping.')
        expect((ex, ey) != at(), f"Turn {i + 1}: an enemy is on the player's tile.")
setup(10, 10, [(12, 10)])
cc.frames(1)
foe = tile_fill(12, 10)
expect(foe is not None and foe != tile_fill(11, 10) and foe != tile_fill(13, 10), 'Draw each enemy as a tile in a colour of its own, after the map.')
"""

_CHECK9 = _HELPERS + _LEVELS + _DRAWN + _ENEMIES + """
expect(getattr(g, 'PLAYER_DAMAGE', None) == 2 and getattr(g, 'ENEMY_DAMAGE', None) == 1, 'Add PLAYER_DAMAGE = 2 and ENEMY_DAMAGE = 1.')
expect(get(g.player, 'hp') == 10 and get(g.player, 'max_hp') == 10, "The player has hp and max_hp, both 10: player = {'pos': (1, 1), 'hp': 10, 'max_hp': 10}.")
regen(5)
expect(len(g.enemies) >= 1 and all(get(e, 'hp') == 4 for e in g.enemies), "Every enemy should be created with hp 4: {'pos': spot, 'hp': 4}.")


def setup(foes, hp):
    arena([], True)
    put_player(10, 10)
    put(g.player, 'hp', hp)
    g.enemies = [mk(c, 4) for c in foes]


def hp():
    return get(g.player, 'hp')


setup([(11, 10)], 10)
press('ArrowRight')
expect(at() == (10, 10), f'Walking into an enemy should hit it, not move onto it; the player is at {at()}.')
left = [get(e, 'hp') for e in g.enemies]
expect(left == [2], f'One hit does 2 damage: an enemy with 4 hp should have 2 left. {"They have " + str(left) + "." if left else "It is gone."}')
expect(hp() == 9, f'Hitting an enemy is a turn, and the enemy next to the player hits back for 1: hp should be 9; it is {hp()}.')
press('ArrowRight')
expect(len(g.enemies) == 0, f'The second hit leaves the enemy at 0 hp, and it should be removed from enemies; the list still has {len(g.enemies)}. enemies.remove(target).')
expect(hp() == 9, f'A dead enemy should not hit back, but the player hp is {hp()}.')
expect(at() == (10, 10), 'Killing an enemy should not move the player into its tile on the same step.')
press('ArrowRight')
expect(at() == (11, 10), f'With the enemy gone, the way is clear: the player should step to column 11; it is at {at()}.')
setup([(15, 10)], 10)
press('ArrowUp')
expect(hp() == 10, f'An enemy five tiles away hurt the player (hp is {hp()}). Only an enemy next to the player attacks.')
setup([(12, 10)], 10)
press('ArrowDown')
expect(hp() == 10, f'An enemy two tiles away hurt the player (hp is {hp()}). It should step closer; it attacks on a later turn.')
setup([(11, 10), (10, 9)], 10)
press('ArrowRight')
expect(hp() == 8, f'Two enemies are next to the player and each should hit once per turn: hp 10 should be 8; it is {hp()}.')
setup([(11, 10)], 10)
cc.frames(1)
expect(any('hp' in t.lower() and '10' in t for t in cc.texts()), "Show the player's health as text, like 'HP: 10/10'.")
put(g.player, 'hp', 4)
cc.frames(1)
expect(any('hp' in t.lower() and '4' in t for t in cc.texts()), 'The health on the screen should follow the player hp.')
"""

_CHECK10 = _HELPERS + _LEVELS + _DRAWN + _ENEMIES + """
expect(callable(getattr(g, 'visible', None)) and callable(getattr(g, 'update_fog', None)), 'Write def visible(x, y) and def update_fog().')
expect(getattr(g, 'RADIUS', None) == 6, 'Add RADIUS = 6')
expect(isinstance(getattr(g, 'seen', None), set), 'Keep what the player has seen in seen = set() - one (x, y) tuple for each tile.')


def setup(px, py, walls=()):
    arena(walls, True)
    put_player(px, py)
    g.enemies = []
    g.seen = set()
    g.update_fog()


setup(10, 10)
for x, y in [(10, 10), (12, 10), (10, 12), (8, 9), (10, 14), (7, 10)]:
    expect(g.visible(x, y) is True, f'The tile at column {x}, row {y} is a few tiles from the player in an empty room and should be visible. A tile is visible when dx * dx + dy * dy <= RADIUS * RADIUS.')
for x, y in [(20, 10), (10, 19), (30, 10), (1, 1), (10, 25)]:
    expect(g.visible(x, y) is False, f'The tile at column {x}, row {y} is far from the player (more than RADIUS tiles) and should not be visible - the fog is not doing anything.')
expect({(10, 10), (12, 10), (10, 14)} <= set(g.seen), 'update_fog() should add the visible tiles to seen as (x, y) tuples - e.g. (10, 10).')
expect((20, 10) not in g.seen and len(g.seen) < 200, 'update_fog() added tiles that are far away. Only what is visible goes into seen.')
setup(10, 10, [(13, 10)])
expect(g.visible(12, 10) is True and g.visible(13, 10) is True, 'You can see right up to a wall, and the wall itself.')
expect(g.visible(15, 10) is False and g.visible(16, 10) is False, 'A tile behind a wall is hidden: walls block sight. Walk the line from the player to the tile, and stop at the first wall.')
expect(g.visible(10, 14) is True and g.visible(10, 6) is True, 'A wall to the east should not hide tiles to the north and south.')
setup(5, 10)
for i in range(12):
    press('ArrowRight')
expect(at() == (17, 10), f'The player should have walked to column 17; it is at {at()}.')
expect((22, 10) in g.seen, 'The fog should lift as the player walks: after each turn, call update_fog() so what is now visible is added to seen.')
expect((5, 10) in g.seen and (8, 10) in g.seen and not g.visible(5, 10), 'Tiles the player has walked away from should stay in seen - the map is remembered.')
expect((30, 10) not in g.seen and (40, 10) not in g.seen and len(g.seen) < len(g.tiles) * len(g.tiles[0]) / 2, 'Most of the map should still be unseen.')
setup(5, 5)
cc.frames(1)
near_floor = tile_fill(6, 5)
near_wall = tile_fill(0, 5)
expect(near_floor is not None and near_wall is not None and near_floor != near_wall, 'Visible tiles are drawn in colours - the floor and the wall different - at ((x - cam_x) * TILE, (y - cam_y) * TILE).')
far = tile_fill(14, 8)
expect(far is None or (far != near_floor and far != near_wall), 'A tile the player has never seen is drawn like one in plain sight. Draw only what is visible, or seen before.')
put_player(13, 5)
g.update_fog()
cc.frames(1)
remembered = tile_fill(6, 5)
expect(remembered is not None, 'A tile seen earlier but out of sight now should still be drawn, as a memory.')
expect(remembered != near_floor, 'Remembered tiles should look different from visible ones: draw them in a darker colour (a different fill_style).')
for s in range(1, 4):
    random.seed(s)
    g.seen.update((1000 + i, 1000) for i in range(600))
    regen(s * 211)
    expect(len(g.seen) < 200 and at() in g.seen, 'A new level should start with a fresh fog: seen = set(), then update_fog() once the player is placed.')
"""

_CHECK11 = _HELPERS + _LEVELS + _DRAWN + _ENEMIES + """
expect(isinstance(getattr(g, 'items', None), list) and isinstance(getattr(g, 'potions', None), int), 'Add items = [] (each one an (x, y) tuple) and potions = 0.')
total = 0
for s in range(1, 21):
    regen(s * 977)
    total += len(g.items)
    for it in g.items:
        expect(isinstance(it, tuple) and len(it) == 2 and g.tiles[it[1]][it[0]] == '.', f'Level {s}: a potion at {it!r} is not an (x, y) tuple on a floor tile.')
        expect(it != at(), f'Level {s}: a potion is under the player at the start.')
expect(total >= 5, 'Across twenty levels there should be potions lying about. Scatter a few on random tiles of the rooms: a comprehension with an if can pick which rooms get one.')


def setup(things, hp, count, foes=()):
    arena([], True)
    put_player(10, 10)
    put(g.player, 'hp', hp)
    g.enemies = [mk(c, 4) for c in foes]
    g.items = [tuple(c) for c in things]
    g.potions = count
    g.seen = set()
    g.update_fog()


def hp():
    return get(g.player, 'hp')


setup([(11, 10)], 10, 0)
press('ArrowRight')
expect(g.items == [], 'The player stepped onto a potion and it is still in items. Pick it up: take it out of the list with items.remove(pos).')
expect(g.potions == 1, f'Picking up a potion should make potions 1; it is {g.potions}.')
setup([(15, 10)], 10, 0)
press('ArrowUp')
expect(len(g.items) == 1 and g.potions == 0, 'A potion the player has not walked onto was picked up.')
setup([], 3, 2)
press('h')
expect(hp() == 8 and g.potions == 1, f'Drinking at 3 hp should heal 5 (to 8) and use one potion (1 left); hp is {hp()}, potions {g.potions}.')
press('h')
expect(hp() == 10, f'Drinking at 8 hp should stop at the maximum, 10 - not climb to {hp()}. min(player max_hp, hp + 5).')
expect(g.potions == 0, f'Both potions are drunk; potions is {g.potions}.')
put(g.player, 'hp', 5)
press('h')
expect(hp() == 5 and g.potions == 0, f'With no potions, h should do nothing; hp is {hp()} and potions {g.potions}.')
setup([], 5, 1, [(15, 10)])
press('h')
expect(enemy_pos() != (15, 10), 'Drinking a potion is a turn: the enemy should have moved.')
setup([], 5, 0, [(15, 10)])
press('h')
expect(enemy_pos() == (15, 10), 'With no potion to drink, h is not a turn - the enemy moved.')
setup([], 5, 3)
cc.frames(1)
expect(any('potion' in t.lower() and '3' in t for t in cc.texts()), "Show the potions you carry as text, like 'Potions: 3'.")
setup([(12, 10)], 10, 0)
cc.frames(1)
pf = tile_fill(12, 10)
expect(pf is not None and pf != tile_fill(11, 10) and pf != tile_fill(13, 10), 'Draw each potion (while it is in sight) as a tile in a colour of its own, after the map.')
"""

_CHECK12 = _HELPERS + _LEVELS + _DRAWN + _ENEMIES + """
expect(getattr(g, 'state', None) == 'playing', "Keep what the game is doing in state = 'playing'")


def setup(hp):
    arena([], True)
    put_player(10, 10)
    put(g.player, 'hp', hp)
    g.enemies = [mk((11, 10), 4)]
    g.items = []
    g.potions = 2
    g.depth = 3
    g.seen = set()
    g.update_fog()


def hp():
    return get(g.player, 'hp')


def snapshot():
    return (at(), [(pos_of(e), get(e, 'hp')) for e in g.enemies], g.potions, g.depth)


setup(5)
press('ArrowRight')
expect(g.state == 'playing', f"The player is at {hp()} hp and the game is {g.state!r} - it should go on.")
setup(1)
press('ArrowRight')
expect(hp() <= 0, f'The enemy should have hit the player down to {hp()}.')
expect(g.state == 'over', f"The player is at {hp()} hp and state is {g.state!r}. At the end of the turn, if hp <= 0 then state = 'over' - and end_turn re-binds state, so it needs `global state`.")
cc.frames(1)
expect(any('game over' in t.lower() for t in cc.texts()), "When the game is over, write 'Game over' on the screen.")
frozen = snapshot()
press('ArrowLeft')
press('ArrowUp')
press('h')
cc.frames(30)
expect(snapshot() == frozen, 'After game over the dungeon should be frozen: the arrow keys and h do nothing. Only Enter does anything.')
press('Enter')
expect(g.state == 'playing', f'Enter after game over should start a new game; state is {g.state!r}. restart() re-binds state, so state is on its `global` line.')
expect(hp() == get(g.player, 'max_hp'), f"A new game starts at full health ({get(g.player, 'max_hp')}); hp is {hp()}.")
expect(g.depth == 1, f'A new game starts at depth 1; depth is {g.depth}.')
expect(g.potions == 0, f'A new game starts with no potions; potions is {g.potions}.')
expect(isinstance(g.rooms, list) and len(g.rooms) >= 3 and in_room(at(), g.rooms[0]), 'A new game needs a new level: call generate().')
expect(not any(get(e, 'hp') == 2 for e in g.enemies), 'The old enemies are still there. A restart builds the whole level again.')
cc.frames(1)
expect(not any('game over' in t.lower() for t in cc.texts()), "'Game over' is still on the screen after the restart.")
g.depth = 2
level = '|'.join(g.tiles)
press('Enter')
expect(g.depth == 2 and '|'.join(g.tiles) == level and g.state == 'playing', "Enter in the middle of a game restarted it. Only restart when state is 'over'.")
"""


def _step(**fields: object) -> Step:
    """A step on this track: Python, in the Python Dungeon track."""
    fields["track"] = TRACK
    fields["language"] = "python"
    return Step(**fields)  # type: ignore[arg-type]


PYDUNGEON_STEPS: tuple[Step, ...] = (
    _step(
        id="pydg-01-map",
        title="A map made of strings",
        teaches=(
            "A roguelike map is just text: a list of strings, one string per "
            "row, one character per tile - '#' is wall, '.' is floor. "
            "tiles[y][x] is the tile in row y, column x, with the ROW first: "
            "tiles[y] picks the string and [x] picks the character in it. "
            "Swap them and you read the wrong tile, or hit an IndexError on a "
            "map that is wider than it is tall. Drawing is two loops, and "
            "enumerate hands you each item with its index: for y, row in "
            "enumerate(tiles), then for x, ch in enumerate(row). One fill_rect "
            "per tile at x * TILE, y * TILE, and a conditional expression "
            "picks the colour: '#4a5568' if ch == '#' else '#2d3748'. Take the "
            "sizes from the map itself, not from a 30 and a 20 typed into the "
            "loops. (It is called tiles, not map: map is a built-in function, "
            "and a name of your own would quietly hide it.)"
        ),
        goal="Add TILE = 16 and tiles, a list of 20 strings of 30 characters each: '#' all round the edge, a few walls inside, and floor at column 1, row 1. Draw every tile each frame, walls and floor in different colours.",
        starter=_P[0],
        solution=_P[1],
        check=_CHECK1,
        hint="for y, row in enumerate(tiles): for x, ch in enumerate(row): draw_tile(x, y, '#4a5568' if ch == '#' else '#2d3748')   and draw_tile fills x * TILE, y * TILE, TILE, TILE.",
    ),
    _step(
        id="pydg-02-turns",
        title="One key press, one step",
        teaches=(
            "A position is a pair of whole numbers, and in Python the right "
            "thing for a pair is a tuple: (x, y). A tuple cannot be changed, "
            "so a move builds a new one and puts it back - x, y = pos "
            "unpacks it, player['pos'] = (x + dx, y + dy) replaces it. The "
            "game is turn-based: a key press is the unit of time, not a frame. "
            "on_key_down(fn) calls fn(key) once when a key goes down, so do "
            "the whole step right there and let the frame loop only draw. "
            "Poll `keys` in on_frame and holding ArrowRight would sprint "
            "across the dungeon, one tile a frame. A dict from key name to "
            "(dx, dy) keeps the handler short, and `if key in KEYS` asks "
            "whether the key is one of them before looking it up. y grows "
            "downwards, so up is (0, -1)."
        ),
        goal="Add player = {'pos': (1, 1)} (a dict, or a dataclass, with a pos tuple) and draw it as a tile in its own colour. Add KEYS and an on_key_down handler: each arrow key press moves the player one tile; holding a key does not move it again, and other keys do nothing.",
        starter=_P[1],
        solution=_P[2],
        check=_CHECK2,
        hint="KEYS = {'ArrowUp': (0, -1), ...}   def key_down(key): if key in KEYS: dx, dy = KEYS[key]; x, y = player['pos']; player['pos'] = (x + dx, y + dy)   then on_key_down(key_down)",
    ),
    _step(
        id="pydg-03-walls",
        title="Walls stop you",
        teaches=(
            "Before the player steps, work out where the step would land - "
            "nx, ny = x + dx, y + dy - and ask whether that tile is a wall. "
            "Asked this often, it earns a function: is_wall(x, y). Make it "
            "say yes for anything off the map and the edge needs no special "
            "case, but ask in_map first, because Python has a trap here that "
            "most languages do not: tiles[-1] is not an error, it is the LAST "
            "row, and tiles[y][-1] is the last character. A step off the left "
            "or top edge silently reads the far side of the map, and off the "
            "right edge it is an IndexError. A chained comparison guards both "
            "ends: 0 <= x < len(tiles[y]). A step into a wall does nothing "
            "at all (return) - it is not a turn, which matters once the "
            "monsters arrive. A function that only reads a top-level name "
            "needs no `global`."
        ),
        goal="Write in_map(x, y) and is_wall(x, y), and move(dx, dy): work out the tile the player would step onto, and only move there if it is on the map and is not a wall. The key handler calls move.",
        starter=_P[2],
        solution=_P[3],
        check=_CHECK3,
        hint="def is_wall(x, y): return not in_map(x, y) or tiles[y][x] == '#'   and in move: if is_wall(nx, ny): return",
    ),
    _step(
        id="pydg-04-camera",
        title="A camera that follows",
        teaches=(
            "Most dungeons are bigger than the screen. A camera is the tile "
            "in the top-left corner of what you can see, and camera() can "
            "return it as a tuple, (cam_x, cam_y), worked out fresh from the "
            "player each time - it can never fall out of step. Put the player "
            "in the middle: px - VIEW_W // 2, with // (not /) so you keep "
            "whole tiles - 15.0 is a float, and a float cannot be a slice "
            "index. Then clamp, so near an edge the camera stops instead of "
            "showing nothing: max(lo, min(hi, v)), between 0 and the map's "
            "width minus the view. Slicing draws just what is in view: "
            "enumerate(tiles[cam_y:cam_y + VIEW_H], cam_y), where the second "
            "argument says where to start counting so y is the real row. "
            "Slices never raise an error, they quietly give less - which is "
            "why a wrong camera shows a half-empty screen instead of "
            "crashing. Subtract the camera from EVERY position you draw."
        ),
        goal="Make TILE 32 and add VIEW_W and VIEW_H (whole tiles that fit across and down the canvas, with //) and camera(), which returns (cam_x, cam_y): the player in the middle of the view, clamped so it never leaves the map. Draw only the tiles in view at (x - cam_x) * TILE, (y - cam_y) * TILE.",
        starter=_P[3],
        solution=_P[4],
        check=_CHECK4,
        hint="def clamp(v, lo, hi): return max(lo, min(hi, v))   camera: return (clamp(px - VIEW_W // 2, 0, len(tiles[0]) - VIEW_W), clamp(py - VIEW_H // 2, 0, len(tiles) - VIEW_H))",
    ),
    _step(
        id="pydg-05-rooms",
        title="Rooms, placed at random",
        teaches=(
            "A dungeon built by hand is the same dungeon every time, so write "
            "a generator: start with all wall, then try rooms - pick a "
            "random size and place, throw the room away if it overlaps one "
            "already placed, otherwise carve it out. A fixed number of tries "
            "(not 'until there are enough') means a bad run cannot loop for "
            "ever. A Room is a @dataclass: just its fields, x, y, w, h, with "
            "__init__ and == written for you - and the right home for the "
            "questions you ask of a room: center as a @property (room.center, "
            "no brackets) and intersects(other) as a method. any(room."
            "intersects(r) for r in rooms) stops at the first yes. Strings "
            "cannot be changed - grid[y][x] = '.' on a string is a TypeError "
            "- so build a list of lists of characters and ''.join(row) each "
            "row at the end. Make the grid with a comprehension, [['#'] * "
            "MAP_W for _ in range(MAP_H)]; [['#'] * MAP_W] * MAP_H repeats "
            "ONE row MAP_H times, and editing one edits them all. "
            "random.Random(seed) is a generator of your own: the same seed "
            "gives the same dungeon, and seed=None a different one each time. "
            "randint(a, b) includes b - unlike range and randrange."
        ),
        goal="Replace the hand-made map with a Room dataclass (x, y, w, h; a center property and an intersects(other) method) and generate(seed=None): it sets tiles (MAP_W by MAP_H, 50 by 30, as strings) and rooms (at least 3, none overlapping, none touching the edge) from a random.Random(seed), and puts the player at the center of rooms[0]. Call generate() once to start.",
        starter=_P[4],
        solution=_P[5],
        check=_CHECK5,
        hint="rng = random.Random(seed); grid = [['#'] * MAP_W for _ in range(MAP_H)]; try 60 times: room = Room(...); if any(room.intersects(other) for other in rooms): continue; then set its tiles to '.'; at the end tiles = [''.join(row) for row in grid]",
    ),
    _step(
        id="pydg-06-corridors",
        title="Corridors join the rooms",
        teaches=(
            "Rooms alone are islands. The simplest scheme that always works: "
            "dig from the center of each room to the center of the one "
            "before - along a row to the right column, then along that "
            "column. Every room is linked to the previous one, so the whole "
            "level is one piece. itertools.pairwise (Python 3.10+) hands you "
            "the pairs: for a, b in pairwise(rooms). Dig with range(min(a, b), "
            "max(a, b) + 1) so it does not matter which end is left or above "
            "- the + 1 is there because range stops short. Then prove it: a "
            "flood fill starts at one tile and spreads to every floor "
            "neighbour. Use a collections.deque for the tiles still to visit: "
            "popleft() is instant, while list.pop(0) must shuffle every "
            "other item along, O(n). A set of the tiles reached makes 'been "
            "here' a single lookup. assert says what must be true, and tells "
            "you if it is not."
        ),
        goal="Write dig_corridor(grid, a, b): a horizontal stretch then a vertical one of '.', from tile a to tile b. In generate(), after placing the rooms, join each room to the one before it. Write flood(start): the set of every floor tile reachable from start (a tuple) by steps up, down, left and right; use it to assert that every floor tile of a new level is reachable.",
        starter=_P[5],
        solution=_P[6],
        check=_CHECK6,
        hint="for a, b in pairwise(rooms): dig_corridor(grid, a.center, b.center)   and flood: reached = {start}; todo = deque([start]); while todo: x, y = todo.popleft(); ... add each neighbour that is not a wall and not reached",
    ),
    _step(
        id="pydg-07-stairs",
        title="Stairs down",
        teaches=(
            "A level needs a way out. Put the stairs - a tuple, like every "
            "other position - at the center of a different room from the "
            "player's: rooms[-1], the last item (a negative index counts "
            "from the end), is never rooms[0] as long as there are two. "
            "When the player steps onto them, `player['pos'] == stairs` "
            "compares the two tuples by value, and the dungeon gets deeper: "
            "add 1 to depth and call generate() again. That one call is the "
            "whole new level, because generate() builds everything from "
            "scratch - which is why it is worth keeping every piece of a "
            "level inside it. move() re-binds depth, a top-level name, so "
            "it needs `global depth`; and generate() with no seed makes a "
            "different level every time. An f-string puts the depth on the "
            "screen: f'Depth: {depth}'."
        ),
        goal="Add stairs (an (x, y) tuple) and depth = 1. generate() puts the stairs at the center of a room that is not the player's. Draw them in their own colour, and show 'Depth: 1' as text. Stepping onto the stairs adds 1 to depth and generates a new level.",
        starter=_P[6],
        solution=_P[7],
        check=_CHECK7,
        hint="In generate: stairs = rooms[-1].center   In move: if player['pos'] == stairs: depth += 1; generate()   (global depth)   and ctx.fill_text(f'Depth: {depth}', 8, 20)",
    ),
    _step(
        id="pydg-08-enemies",
        title="The monsters take their turn",
        teaches=(
            "In a roguelike the world waits for you. Nothing else moves "
            "until the player does something that takes a turn - and then "
            "each enemy takes exactly one. Put 'everyone else's turn' in one "
            "function, end_turn(), and call it at the end of the player's "
            "move. Two details decide whether it feels fair: a step into a "
            "wall must return before end_turn, and the enemies move after "
            "the player, so they react to where you ARE. To chase, move one "
            "tile along whichever axis is further away, and if a wall is in "
            "the way try the other. The step is the difference clamped to "
            "-1..1 - the same clamp() as the camera. They stop next to you: "
            "the player's tile is not theirs to step on. Each enemy is a "
            "dict (or a dataclass) with a pos tuple; `for e in enemies` "
            "hands you the real thing, so e['pos'] = ... changes it in "
            "place and needs no `global`. Put the random tile in a Room "
            "method: rng.randrange(x, x + w) works like range."
        ),
        goal="Add enemies, a list of things with a pos tuple: generate() puts one on a random tile of every room except the first (never on the stairs), and they are drawn in their own colour. Write enemies_act() and end_turn(): after every step the player takes, each enemy moves one tile (up, down, left or right) toward the player, never into a wall or onto the player. A step into a wall is not a turn.",
        starter=_P[7],
        solution=_P[8],
        check=_CHECK8,
        hint="def end_turn(): enemies_act()   enemies_act: dx, dy = px - ex, py - ey; try the axis with the larger distance first; step only if not is_wall(nx, ny) and (nx, ny) != player['pos']. Call end_turn() last in move().",
    ),
    _step(
        id="pydg-09-bump",
        title="Bump to attack",
        teaches=(
            "Roguelikes have no attack button: you fight by walking into the "
            "enemy. In move(), before stepping, look for an enemy on the "
            "tile you are heading for. If there is one, you hit it instead "
            "of moving: take the damage off its hp, and if that leaves 0 or "
            "less, enemies.remove(target) - a dead enemy left in the list "
            "keeps chasing and hitting you. remove changes the list in "
            "place, so no `global`. next((e for e in enemies if e['pos'] == "
            "pos), None) finds the first match, or the default when there "
            "is none. A bump is a turn, so the enemies respond; and one "
            "already next to you does not need to move any more, it hits "
            "(abs(dx) + abs(dy) == 1). Keep the numbers - 2 damage from you, "
            "1 from them, 4 hp and 10 hp - as named constants, so tuning the "
            "game is one edit. A dict key inside an f-string needs the "
            "other kind of quote: f\"HP: {player['hp']}\"."
        ),
        goal="Give enemies hp 4 and the player hp 10 and max_hp 10 (fields 'hp' and 'max_hp'); add PLAYER_DAMAGE = 2 and ENEMY_DAMAGE = 1. Walking into an enemy hits it instead of moving (and takes a turn); at 0 hp it is removed from enemies. An enemy next to the player hits instead of moving. Show 'HP: 10/10' as text.",
        starter=_P[8],
        solution=_P[9],
        check=_CHECK9,
        hint="In move(): target = enemy_at((nx, ny)); if target is not None: target['hp'] -= PLAYER_DAMAGE; if target['hp'] <= 0: enemies.remove(target); end_turn(); return",
    ),
    _step(
        id="pydg-10-fog",
        title="Fog of war",
        teaches=(
            "A dungeon you can see all of has no mystery. Fog of war keeps "
            "two things: what you can see RIGHT NOW (a pure function of "
            "where you stand) and what you have SEEN (a memory that only "
            "grows). A tile is visible if it is within RADIUS - dx * dx + "
            "dy * dy <= RADIUS * RADIUS, no square root needed - and no wall "
            "is in the way: walk along the line from the player to the tile "
            "and give up at the first wall (round() rounds halves to even in "
            "Python, round(2.5) is 2, which is fine here). The memory is a "
            "set of (x, y) tuples, and a set answers `(x, y) in seen` with "
            "one lookup. Grow it with a set comprehension and |=. But |= "
            "re-binds the name, even though a set changes in place - so "
            "inside a function it needs `global seen`, or Python raises "
            "UnboundLocalError (seen.update(...) would not). Draw visible "
            "tiles bright, remembered ones dimmer, the rest not at all; "
            "monsters and potions only show while in sight."
        ),
        goal="Add RADIUS = 6, seen = set(), visible(x, y) (within RADIUS and no wall in the line between) and update_fog() (adds every visible tile as an (x, y) tuple to seen). Update it after each turn and when a level is generated (starting from an empty set). Draw visible tiles bright, seen ones in a darker colour (set fill_style, not global_alpha), unseen ones not at all.",
        starter=_P[9],
        solution=_P[10],
        check=_CHECK10,
        hint="def update_fog(): global seen; seen |= {(x, y) for y in range(py - RADIUS, py + RADIUS + 1) for x in range(...) if in_map(x, y) and visible(x, y)}   visible: return False at the first is_wall on the line",
    ),
    _step(
        id="pydg-11-potions",
        title="Potions",
        teaches=(
            "Items are the same idea as enemies without the brain: a list "
            "of (x, y) tuples, scattered by generate(), drawn, and collected "
            "by walking onto them. A list comprehension with a condition "
            "scatters them - [room.random_tile(rng) for room in rooms[1:] "
            "if rng.random() < 0.6] builds the list and picks which rooms "
            "get one in a single line. `pos in items` asks whether the "
            "player is standing on one (== on tuples), and items.remove(pos) "
            "takes it out in place. What you hold is not an object yet, just "
            "a count, potions, which pick_up() and drink() re-bind - so they "
            "say `global potions`. Drinking (H) spends one, heals by 5 and "
            "takes a turn, but clamp the healing, min(max_hp, hp + 5), or hp "
            "climbs past the maximum. With none left, H does nothing at all: "
            "no healing, no negative count, no turn. Now the handler has two "
            "kinds of key, and match is made for that: case 'h': ... case "
            "'ArrowUp' | 'ArrowDown' | ...: ... - the | joins alternatives "
            "and the first case that fits wins."
        ),
        goal="Add items (a list of (x, y) tuples) and potions = 0. generate() scatters potions on floor tiles of the rooms but not the first; they are drawn (while visible) in their own colour. Walking onto one picks it up: it leaves items and potions goes up by 1. Pressing h drinks one: hp goes up by 5, never past max_hp, and it takes a turn; with none left, h does nothing. Show 'Potions: N' as text, and handle the keys with match.",
        starter=_P[10],
        solution=_P[11],
        check=_CHECK11,
        hint="def pick_up(): global potions; if player['pos'] in items: items.remove(player['pos']); potions += 1   drink: player['hp'] = min(player['max_hp'], player['hp'] + 5); end_turn()",
    ),
    _step(
        id="pydg-12-gameover",
        title="Game over, and again",
        teaches=(
            "You will die, so the game needs an ending and a way back. "
            "state is 'playing' or 'over'; when hp reaches 0 at the end of a "
            "turn (after the enemies have acted) it becomes 'over', the "
            "screen says so, and the game stops listening to everything "
            "except Enter. match handles it neatly, because a case can have "
            "a guard: case 'Enter' if state == 'over': restart(), then case "
            "_ if state == 'over': pass swallows every other key, and only "
            "after those do the real keys get a look. Restarting undoes "
            "everything that changed over a run: depth back to 1, hp back "
            "to full, no potions, state 'playing', and generate() for a new "
            "level - one call rebuilds rooms, stairs, enemies, items and fog. "
            "Every name restart() re-binds must be on its `global` line: "
            "leave state off and `state = 'playing'` quietly makes a local "
            "variable while the real state stays 'over'. end_turn() needs "
            "its own `global state`, or the game never ends. Enter must do "
            "nothing in the middle of a game."
        ),
        goal="Add state = 'playing'. When the player's hp reaches 0 at the end of a turn, state becomes 'over' and the screen says 'Game over'. While it is over, only Enter does anything: restart() starts again at depth 1 with full hp and no potions on a new level.",
        starter=_P[11],
        solution=_P[12],
        check=_CHECK12,
        hint="In end_turn(): if player['hp'] <= 0: state = 'over'   In key_down: match key: case 'Enter' if state == 'over': restart()   case _ if state == 'over': pass   ... and global state",
    ),
    _step(
        id="pydg-13-yours",
        title="Now it's yours",
        teaches=(
            "A whole roguelike: a map of strings, a turn instead of a clock, "
            "a seeded generator, enemies that chase, fog, items and an "
            "ending. Ideas, easiest first: enemies that start asleep and "
            "wake when you are within five tiles; WASD as well as the arrows "
            "(case 'w' | 'ArrowUp':); a message line ('You hit the goblin') "
            "kept in a deque(maxlen=3); enemies that get tougher with depth; "
            "a second kind of monster in a dataclass of its own; a sword "
            "that raises PLAYER_DAMAGE; waiting a turn with the space bar; "
            "a minimap; corridors that bend; a seed shown on screen so a "
            "good dungeon can be shared; and a best depth that survives a "
            "restart. BFS from the player with flood() could make the "
            "enemies walk round corners instead of getting stuck on walls."
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_P[12],
        solution=_P[12],
        check="",
    ),
)
