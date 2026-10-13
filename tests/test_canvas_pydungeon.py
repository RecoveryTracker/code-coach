"""Canvas: the Python Dungeon steps and their checks.

Like the JavaScript Dungeon (test_canvas_dungeon.py), but the program is
Python and the check plays it in a child process. A check is held to three
things: the step's own solution passes, its starter (the step before,
finished) does not, and the mistakes people really make at that step fail it
too - moving every frame a key is held instead of once per press, a missing or
off-by-one wall test (and Python's own trap: tiles[-1] is the last row, not an
error), tiles[x][y] for tiles[y][x], a camera that is not clamped or not
subtracted when drawing, `[["#"] * W] * H` (one row, H times), editing a string,
rooms that overlap or run into the border, rooms that are not all joined,
stairs in the player's room or that do not regenerate the level, enemies that
act before the player, on a bumped wall or on the clock, enemies that walk
through walls, a dead enemy left in the list, fog that shows everything (or
ignores walls, or forgets, or is missing its `global`), healing past max hp,
and a game over that is not final or a restart that leaves something behind.

The generator's checks are about properties, never layouts, so OTHER_WAYS
holds different but correct generators too (module-level random instead of a
Random(seed), another corridor shape, a list or a stack for the flood fill,
dicts or dataclasses for the player and the enemies).
"""

from __future__ import annotations

import re

import pytest

from code_coach.canvas import STEPS as ALL_STEPS
from code_coach.canvas import check_step, run_py_check
from code_coach.canvas.content_pydungeon import PYDUNGEON_STEPS as STEPS

BY_ID = {s.id: s for s in STEPS}

_REGISTERED = all(s.id in {a.id for a in ALL_STEPS} for s in STEPS)


def _by_id(step_id: str):
    return BY_ID[step_id]


def _swap(code: str, change: tuple) -> str:
    """Apply one change: (old, new), or a tuple of such pairs applied in turn."""
    pairs = (change,) if isinstance(change[0], str) else change
    for old, new in pairs:
        assert code.count(old) >= 1, old
        code = code.replace(old, new)
    return code


def _label(change: tuple) -> str:
    pair = change if isinstance(change[0], str) else change[0]
    return (pair[1] or pair[0])[:60]


_ARROW = "'#4a5568' if ch == '#' else '#2d3748'"
_IMPORT_2 = "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down"
_POLL = "on_frame(lambda dt: [key_down(k) for k in list(keys)])\n"
_WALL_RETURN = "    if is_wall(nx, ny):\n        return\n"
_CAM_RET = (
    "    return (clamp(px - VIEW_W // 2, 0, len(tiles[0]) - VIEW_W),\n"
    "            clamp(py - VIEW_H // 2, 0, len(tiles) - VIEW_H))\n"
)
_ASSERT = "    assert flood(rooms[0].center) == floor, 'some rooms are cut off'\n"
_CORRIDORS = "    for a, b in pairwise(rooms):\n        dig_corridor(grid, a.center, b.center)\n"
_VERTICAL = "    for y in range(min(ay, by), max(ay, by) + 1):\n        grid[y][bx] = '.'\n"
_INTERSECTS = (
    "        return (self.x <= other.x + other.w and other.x <= self.x + self.w\n"
    "                and self.y <= other.y + other.h and other.y <= self.y + self.h)"
)
_ROOM_CHECK = "        if any(room.intersects(other) for other in rooms):\n            continue\n"
_ON_STAIRS = (
    "    player['pos'] = (nx, ny)\n"
    "    if player['pos'] == stairs:\n        depth += 1\n        generate()\n        return\n    end_turn()\n"
)
_ACT = "(sx, sy) == (0, 0) or is_wall(nx, ny) or (nx, ny) == player['pos']"
_ATTACK = "        if abs(dx) + abs(dy) == 1:\n            player['hp'] -= ENEMY_DAMAGE\n            continue\n"
_BUMP = (
    "        target['hp'] -= PLAYER_DAMAGE\n        if target['hp'] <= 0:\n            enemies.remove(target)\n"
    "        end_turn()\n        return\n"
)
_DIM = "            elif (x, y) in seen:\n                draw_tile(x, y, '#262c37' if ch == '#' else '#1c2230')\n"
_SEEN_RESET = "    seen = set()\n    update_fog()\n"
_DRINK = "    player['hp'] = min(player['max_hp'], player['hp'] + 5)\n    end_turn()\n"
_POTION_DRAW = "    for pos in items:\n        if visible(*pos):\n            draw_tile(*pos, '#f6e05e')\n"
_END_TURN = "    enemies_act()\n    update_fog()\n    if player['hp'] <= 0:\n        state = 'over'\n"
_OVER_GUARD = "        case _ if state == 'over':\n            pass\n"
_MATCH = (
    "    match key:\n"
    "        case 'Enter' if state == 'over':\n            restart()\n"
    "        case _ if state == 'over':\n            pass\n"
    "        case 'h':\n            drink()\n"
    "        case 'ArrowUp' | 'ArrowDown' | 'ArrowLeft' | 'ArrowRight':\n            move(*KEYS[key])\n"
)
_MATCH_11 = (
    "    match key:\n"
    "        case 'h':\n            drink()\n"
    "        case 'ArrowUp' | 'ArrowDown' | 'ArrowLeft' | 'ArrowRight':\n            move(*KEYS[key])\n"
)
_ROOM_DICTS = [
    # The same generator with dicts for rooms instead of a Room dataclass.
    (
        "@dataclass\nclass Room:\n    x: int\n    y: int\n    w: int\n    h: int\n\n"
        "    @property\n    def center(self):\n        return (self.x + self.w // 2, self.y + self.h // 2)\n\n"
        "    def intersects(self, other):\n" + _INTERSECTS,
        "def make_room(x, y, w, h):\n    return {'x': x, 'y': y, 'w': w, 'h': h}\n\n\n"
        "def center(r):\n    return (r['x'] + r['w'] // 2, r['y'] + r['h'] // 2)\n\n\n"
        "def intersects(a, b):\n"
        "    return (a['x'] <= b['x'] + b['w'] and b['x'] <= a['x'] + a['w']\n"
        "            and a['y'] <= b['y'] + b['h'] and b['y'] <= a['y'] + a['h'])",
    ),
    ("room = Room(rng.randint", "room = make_room(rng.randint"),
    ("room.intersects(other)", "intersects(room, other)"),
    ("range(room.y, room.y + room.h)", "range(room['y'], room['y'] + room['h'])"),
    ("range(room.x, room.x + room.w)", "range(room['x'], room['x'] + room['w'])"),
    ("rooms[0].center", "center(rooms[0])"),
]

#: Wrong programs, each a real mistake at that step, that the check must fail:
#: (what to find in the solution, what to put there instead), or a tuple of such pairs.
MISTAKES: dict[str, list[tuple]] = {
    "pydg-01-map": [
        # Row and column swapped when reading the map.
        (_ARROW, "'#4a5568' if tiles[x][y] == '#' else '#2d3748'"),
        # Off by one: the last row, or the last column, is never drawn.
        ("enumerate(tiles):", "enumerate(tiles[:-1]):"),
        ("enumerate(row):", "enumerate(row[:-1]):"),
        # Pixels swapped.
        ("ctx.fill_rect(x * TILE, y * TILE, TILE, TILE)", "ctx.fill_rect(y * TILE, x * TILE, TILE, TILE)"),
        # Walls and floor the same colour.
        ("else '#2d3748'", "else '#4a5568'"),
        # A map whose rows are one character short.
        ("'#............#...............#',", "'#............#..............#',"),
        # Rows made of lists, not strings.
        ("    '#............................#',\n    '##############################',\n]",
         "    '#............................#',\n    list('##############################'),\n]"),
    ],
    "pydg-02-turns": [
        # Moves again on every frame a key is down, as well as on the press.
        ((_IMPORT_2, _IMPORT_2 + ", keys"), ("on_key_down(key_down)\n", "on_key_down(key_down)\n" + _POLL)),
        # Moves only by polling the held keys: a press that is released at once is missed.
        ((_IMPORT_2, _IMPORT_2 + ", keys"), ("on_key_down(key_down)\n", _POLL)),
        # Pixels, not tiles.
        ("(x + dx, y + dy)", "(x + dx * TILE, y + dy * TILE)"),
        # Up is down.
        ("'ArrowUp': (0, -1)", "'ArrowUp': (0, 1)"),
        # x and y swapped.
        ("(x + dx, y + dy)", "(x + dy, y + dx)"),
        # The player is never drawn.
        ("    draw_tile(*player['pos'], '#4fd1c5')\n", ""),
        # A list for a position, not a tuple.
        ("player['pos'] = (x + dx, y + dy)", "player['pos'] = [x + dx, y + dy]"),
        # Looking a key up without asking: 'q' is a KeyError.
        ("    if key in KEYS:\n        dx, dy = KEYS[key]\n        x, y = player['pos']\n        player['pos'] = (x + dx, y + dy)\n",
         "    dx, dy = KEYS[key]\n    x, y = player['pos']\n    player['pos'] = (x + dx, y + dy)\n"),
        # Starts somewhere else.
        ("player = {'pos': (1, 1)}", "player = {'pos': (2, 2)}"),
    ],
    "pydg-03-walls": [
        # Walls do not stop anyone.
        (_WALL_RETURN, ""),
        # Walls do, the edge of the map does not (and tiles[-1] is the last row).
        ("    return not in_map(x, y) or tiles[y][x] == '#'", "    return tiles[y][x] == '#'"),
        # tiles[x][y]
        ("or tiles[y][x] == '#'", "or tiles[x][y] == '#'"),
        # Off by one at the right edge, and at the bottom edge.
        ("0 <= x < len(tiles[y])", "0 <= x <= len(tiles[y])"),
        ("0 <= y < len(tiles) and", "0 <= y <= len(tiles) and"),
        # Only the walls to the right count.
        ("or tiles[y][x] == '#'", "or (tiles[y][x] == '#' and x >= player['pos'][0])"),
        # The edge is checked on one side only: the left edge wraps round to the right.
        ("0 <= y < len(tiles) and 0 <= x < len(tiles[y])", "y < len(tiles) and x < len(tiles[y])"),
    ],
    "pydg-04-camera": [
        # Not clamped.
        (_CAM_RET, "    return (px - VIEW_W // 2, py - VIEW_H // 2)\n"),
        # Clamped to the wrong end.
        ("len(tiles[0]) - VIEW_W)", "len(tiles[0]))"),
        # Never follows.
        (_CAM_RET, "    return (0, 0)\n"),
        # Follows the wrong coordinate.
        ("clamp(px - VIEW_W // 2", "clamp(py - VIEW_W // 2"),
        # Drawn without the camera subtracted.
        ("ctx.fill_rect((x - cam_x) * TILE, (y - cam_y) * TILE, TILE, TILE)", "ctx.fill_rect(x * TILE, y * TILE, TILE, TILE)"),
        # Camera subtracted from the map but not the player.
        ("    draw_tile(*player['pos'], '#4fd1c5')\n",
         "    ctx.fill_style = '#4fd1c5'\n    ctx.fill_rect(player['pos'][0] * TILE, player['pos'][1] * TILE, TILE, TILE)\n"),
        # The view size is a float.
        ("VIEW_W = WIDTH // TILE", "VIEW_W = WIDTH / TILE"),
        # Not zoomed in.
        ("TILE = 32", "TILE = 16"),
        # The last row in view is cut off.
        ("tiles[cam_y:cam_y + VIEW_H]", "tiles[cam_y:cam_y + VIEW_H - 1]"),
        # enumerate counts from 0, so every row is drawn in the wrong place.
        ("enumerate(tiles[cam_y:cam_y + VIEW_H], cam_y)", "enumerate(tiles[cam_y:cam_y + VIEW_H])"),
    ],
    "pydg-05-rooms": [
        # Rooms are never thrown away.
        (_ROOM_CHECK, ""),
        # Rooms run into the border, to the right and at the bottom, and at the left.
        ("rng.randint(1, MAP_W - w - 1)", "rng.randint(1, MAP_W - w)"),
        ("rng.randint(1, MAP_H - h - 1)", "rng.randint(1, MAP_H - h)"),
        ("rng.randint(1, MAP_W - w - 1)", "rng.randint(0, MAP_W - w - 1)"),
        # The list of rooms is not emptied for the next level.
        ("    rooms = []\n    for", "    for"),
        # ... or is, but into a local variable: no `global rooms`.
        ("    global tiles, rooms\n", "    global tiles\n"),
        # Row and column swapped when carving.
        ("grid[y][x] = '.'", "grid[x][y] = '.'"),
        # [row] * MAP_H is ONE row repeated, so every row is edited at once.
        ("grid = [['#'] * MAP_W for _ in range(MAP_H)]", "grid = [['#'] * MAP_W] * MAP_H"),
        # Rows are strings, which cannot be edited.
        ("grid = [['#'] * MAP_W for _ in range(MAP_H)]", "grid = ['#' * MAP_W for _ in range(MAP_H)]"),
        # The rows are never joined into strings, or never stored.
        ("    tiles = [''.join(row) for row in grid]\n", "    tiles = grid\n"),
        ("    tiles = [''.join(row) for row in grid]\n", ""),
        # The player is not put in a room.
        ("    player['pos'] = rooms[0].center\n", ""),
        # The centre is outside the room.
        ("return (self.x + self.w // 2, self.y + self.h // 2)", "return (self.x + self.w, self.y + self.h)"),
        # Gives up with two rooms.
        ("if len(rooms) == 8:", "if len(rooms) == 2:"),
        # `or` for `and`: every room seems to overlap, so almost none are placed.
        (_INTERSECTS,
         "        return (self.x <= other.x + other.w or other.x <= self.x + self.w\n"
         "                or self.y <= other.y + other.h or other.y <= self.y + self.h)"),
        # The seed is ignored: a new Random() is different every time.
        ("rng = random.Random(seed)", "rng = random.Random()"),
        # Always the same dungeon.
        ("rng = random.Random(seed)", "rng = random.Random(7)"),
    ],
    "pydg-06-corridors": [
        # The last room is never joined (and the assert that would notice is gone).
        ((_CORRIDORS, _CORRIDORS.replace("pairwise(rooms)", "pairwise(rooms[:-1])")), (_ASSERT, "")),
        # Every other room is skipped.
        ((_CORRIDORS, _CORRIDORS.replace("pairwise(rooms)", "pairwise(rooms[::2])")), (_ASSERT, "")),
        # No vertical stretch.
        ((_VERTICAL, ""), (_ASSERT, "")),
        # The vertical stretch is in the wrong column.
        (("grid[y][bx] = '.'", "grid[y][ax] = '.'"), (_ASSERT, "")),
        # No corridors at all.
        ((_CORRIDORS, ""), (_ASSERT, "")),
        # A flood fill that floods the walls too.
        (("if step not in reached and not is_wall(*step):", "if step not in reached and in_map(*step):"), (_ASSERT, "")),
        # A flood fill that only goes right and down.
        (("for dx, dy in KEYS.values():", "for dx, dy in [(1, 0), (0, 1)]:"), (_ASSERT, "")),
        # A flood fill that never spreads.
        (("            if step not in reached and not is_wall(*step):", "            if False:"), (_ASSERT, "")),
    ],
    "pydg-07-stairs": [
        # The stairs are in the player's room, under the player.
        ("    stairs = rooms[-1].center\n", "    stairs = rooms[0].center\n"),
        # In any room, the first included.
        ("    stairs = rooms[-1].center\n", "    stairs = rng.choice(rooms).center\n"),
        # x and y swapped.
        ("    stairs = rooms[-1].center\n", "    stairs = rooms[-1].center[::-1]\n"),
        # Deeper, but the same level.
        ("        depth += 1\n        generate()\n", "        depth += 1\n"),
        # A new level at the same depth.
        ("        depth += 1\n        generate()\n", "        generate()\n"),
        # The depth is not shown.
        ("    ctx.fill_text(f'Depth: {depth}', 8, 20)\n", ""),
        # The stairs are not drawn.
        ("    draw_tile(*stairs, '#b794f4')\n", ""),
        # depth += 1 without `global depth`: UnboundLocalError.
        ("    global depth\n", ""),
        # The stairs are made in a local variable: no `global stairs`.
        ("    global tiles, rooms, stairs\n", "    global tiles, rooms\n"),
        # `is` for `==` on two tuples built apart.
        ("if player['pos'] == stairs:", "if player['pos'] is stairs:"),
    ],
    "pydg-08-enemies": [
        # The enemies move before the player does.
        ((_ON_STAIRS, "    end_turn()\n" + _ON_STAIRS.replace("    end_turn()\n", ""))),
        # A step into a wall is a turn.
        (_WALL_RETURN, "    if is_wall(nx, ny):\n        end_turn()\n        return\n"),
        # They move on the clock, not on the player's turn.
        ("def frame(dt):\n    draw()", "def frame(dt):\n    enemies_act()\n    draw()"),
        # They walk through walls.
        (_ACT, "(sx, sy) == (0, 0) or (nx, ny) == player['pos']"),
        # They walk onto the player.
        (_ACT, "(sx, sy) == (0, 0) or is_wall(nx, ny)"),
        # They run away.
        ("clamp(dx, -1, 1), clamp(dy, -1, 1)", "-clamp(dx, -1, 1), -clamp(dy, -1, 1)"),
        # They start in the player's room.
        ("    for room in rooms[1:]:\n        spot", "    for room in rooms:\n        spot"),
        # One may start on the stairs.
        ("        if spot != stairs:\n", "        if True:\n"),
        # They are not drawn.
        ("    for e in enemies:\n        draw_tile(*e['pos'], '#f56565')\n", ""),
        # The list is made in a local variable: no `global enemies`.
        ("    global tiles, rooms, stairs, enemies\n", "    global tiles, rooms, stairs\n"),
    ],
    "pydg-09-bump": [
        # A dead enemy stays in the list.
        ("        if target['hp'] <= 0:\n            enemies.remove(target)\n", ""),
        # Dead only below zero.
        ("target['hp'] <= 0", "target['hp'] < 0"),
        # The player hits and then walks onto the tile.
        ("        end_turn()\n        return\n    player['pos'] = (nx, ny)", "        end_turn()\n    player['pos'] = (nx, ny)"),
        # Hitting is not a turn.
        ("        end_turn()\n        return\n    player['pos'] = (nx, ny)", "        return\n    player['pos'] = (nx, ny)"),
        # The enemy beside the player never hits.
        (_ATTACK, ""),
        # Enemies hit from three tiles away.
        ("abs(dx) + abs(dy) == 1", "abs(dx) + abs(dy) <= 3"),
        # A dead enemy gets its turn.
        (_BUMP,
         "        target['hp'] -= PLAYER_DAMAGE\n        end_turn()\n        if target['hp'] <= 0:\n"
         "            enemies.remove(target)\n        return\n"),
        # No hp for enemies.
        ("{'pos': spot, 'hp': 4}", "{'pos': spot}"),
        # The health is not shown.
        ("    ctx.fill_text(f\"HP: {player['hp']}/{player['max_hp']}\", 8, 40)\n", ""),
        # The wrong damage.
        ("PLAYER_DAMAGE = 2", "PLAYER_DAMAGE = 3"),
    ],
    "pydg-10-fog": [
        # Everything is visible.
        ("def visible(x, y):\n", "def visible(x, y):\n    return True\n"),
        # Walls do not block sight.
        ("        if is_wall(cx, cy):\n            return False\n", ""),
        # The radius is not squared.
        ("> RADIUS * RADIUS", "> RADIUS"),
        # The fog is not updated as the player moves.
        ("    enemies_act()\n    update_fog()\n", "    enemies_act()\n"),
        # The fog survives into the next level.
        (_SEEN_RESET, "    update_fog()\n"),
        # Seen tiles are not drawn.
        (_DIM, ""),
        # Remembered tiles look like visible ones.
        ("'#262c37' if ch == '#' else '#1c2230'", "'#4a5568' if ch == '#' else '#2d3748'"),
        # Unseen tiles are drawn too.
        ("            if visible(x, y):\n", "            if True:\n"),
        # seen |= re-binds the name, so it needs `global seen`: UnboundLocalError.
        ("def update_fog():\n    global seen\n", "def update_fog():\n"),
        # The memory is replaced, not added to.
        ("    seen |= {(x, y)", "    seen = {(x, y)"),
        # Only the walls are remembered, or nothing is: update_fog never runs in generate.
        (_SEEN_RESET, "    seen = set()\n"),
    ],
    "pydg-11-potions": [
        # Healing past the maximum.
        ("min(player['max_hp'], player['hp'] + 5)", "player['hp'] + 5"),
        # Heals the wrong amount.
        ("min(player['max_hp'], player['hp'] + 5)", "min(player['max_hp'], player['hp'] + 3)"),
        # Drinking with none left.
        ("    if potions == 0:\n        return\n", ""),
        # Drinking is free.
        (_DRINK, "    player['hp'] = min(player['max_hp'], player['hp'] + 5)\n"),
        # A potion that stays where it was.
        ("        items.remove(pos)\n", ""),
        # Picked up but not counted.
        ("        potions += 1\n", ""),
        # The count is not shown.
        ("    ctx.fill_text(f'Potions: {potions}', 8, 60)\n", ""),
        # Potions are not drawn.
        (_POTION_DRAW, ""),
        # potions += 1 without `global potions`: UnboundLocalError.
        ("def pick_up():\n    global potions\n", "def pick_up():\n"),
        # No key for drinking.
        ("        case 'h':\n            drink()\n", ""),
    ],
    "pydg-12-gameover": [
        # Never ends.
        ("    if player['hp'] <= 0:\n        state = 'over'\n", ""),
        # Dead only below zero.
        ("    if player['hp'] <= 0:", "    if player['hp'] < 0:"),
        # hp is checked before the enemies have hit.
        (_END_TURN, "    if player['hp'] <= 0:\n        state = 'over'\n    enemies_act()\n    update_fog()\n"),
        # state is re-bound in end_turn without `global`: a quiet local, and the game never ends.
        ("def end_turn():\n    global state\n", "def end_turn():\n"),
        # Keys still work after the end.
        (_OVER_GUARD, ""),
        # Enter restarts in the middle of a game.
        ("case 'Enter' if state == 'over':", "case 'Enter':"),
        # Restart leaves the health, the depth, the potions, the level, the state behind.
        ("    player['hp'] = player['max_hp']\n    potions = 0\n", "    potions = 0\n"),
        ("    depth = 1\n    player['hp']", "    player['hp']"),
        ("    potions = 0\n    state = 'playing'\n    generate()", "    state = 'playing'\n    generate()"),
        ("    state = 'playing'\n    generate()", "    state = 'playing'"),
        ("    state = 'playing'\n    generate()", "    generate()"),
        # ... or the state is set in a local variable: state is not on restart's `global` line.
        ("    global depth, potions, state\n", "    global depth, potions\n"),
        # Says nothing.
        ("        ctx.fill_text('Game over', 150, 160)\n", ""),
    ],
}

#: Right programs written another way, which the check must still pass.
OTHER_WAYS: dict[str, list[tuple]] = {
    "pydg-02-turns": [
        # A table that is a dict.get with a default.
        ("    if key in KEYS:\n        dx, dy = KEYS[key]\n", "    if key in KEYS:\n        dx, dy = KEYS.get(key, (0, 0))\n"),
        ("(x + dx, y + dy)", "(player['pos'][0] + dx, player['pos'][1] + dy)"),
    ],
    "pydg-03-walls": [
        ("    return not in_map(x, y) or tiles[y][x] == '#'", "    return not in_map(x, y) or tiles[y][x] != '.'"),
        ("    return 0 <= y < len(tiles) and 0 <= x < len(tiles[y])",
         "    return y in range(len(tiles)) and x in range(len(tiles[y]))"),
    ],
    "pydg-04-camera": [
        ("    return max(lo, min(hi, v))", "    return lo if v < lo else hi if v > hi else v"),
        ("VIEW_W // 2", "(VIEW_W + 1) // 2"),
    ],
    "pydg-05-rooms": [
        ("rng.randint(4, 9)", "rng.randint(3, 8)"),
        # random's module-level functions instead of a Random(seed): the seed is ignored.
        ("rng = random.Random(seed)", "rng = random"),
        ("rng.randint(1, MAP_W - w - 1)", "rng.randrange(1, MAP_W - w)"),
        ("for _ in range(60):", "for _ in range(200):"),
        # Rooms that touch edge to edge but never overlap.
        (_INTERSECTS,
         "        return (self.x < other.x + other.w and other.x < self.x + self.w\n"
         "                and self.y < other.y + other.h and other.y < self.y + self.h)"),
        # Rooms as dicts.
        tuple(_ROOM_DICTS),
        # ''.join of a list comprehension, and the grid made with a different comprehension.
        ("grid = [['#'] * MAP_W for _ in range(MAP_H)]", "grid = [list('#' * MAP_W) for _ in range(MAP_H)]"),
        ("    tiles = [''.join(row) for row in grid]\n", "    tiles = list(map(''.join, grid))\n"),
    ],
    "pydg-06-corridors": [
        # A list for the flood fill, with pop(0): slow for a big map, but right.
        (("    todo = deque([start])\n", "    todo = [start]\n"), ("todo.popleft()", "todo.pop(0)")),
        # A stack: depth first reaches the same tiles.
        ("todo.popleft()", "todo.pop()"),
        # Vertical first, then horizontal.
        ("    for x in range(min(ax, bx), max(ax, bx) + 1):\n        grid[ay][x] = '.'\n"
         "    for y in range(min(ay, by), max(ay, by) + 1):\n        grid[y][bx] = '.'\n",
         "    for y in range(min(ay, by), max(ay, by) + 1):\n        grid[y][ax] = '.'\n"
         "    for x in range(min(ax, bx), max(ax, bx) + 1):\n        grid[by][x] = '.'\n"),
        # Every room joined to the first one.
        (_CORRIDORS, "    for b in rooms[1:]:\n        dig_corridor(grid, rooms[0].center, b.center)\n"),
        # Dug from the other end.
        ("dig_corridor(grid, a.center, b.center)", "dig_corridor(grid, b.center, a.center)"),
        # zip instead of pairwise.
        ("pairwise(rooms)", "zip(rooms, rooms[1:])"),
        (_CORRIDORS, "    for i in range(1, len(rooms)):\n        dig_corridor(grid, rooms[i - 1].center, rooms[i].center)\n"),
        # A flood fill that stays on the tile type instead of asking is_wall.
        ("not is_wall(*step)", "in_map(*step) and tiles[step[1]][step[0]] == '.'"),
        # The flood fill returns a frozenset.
        ("    return reached", "    return frozenset(reached)"),
    ],
    "pydg-07-stairs": [
        # Any room but the first.
        ("    stairs = rooms[-1].center\n", "    stairs = rng.choice(rooms[1:]).center\n"),
        ("    stairs = rooms[-1].center\n", "    stairs = rooms[len(rooms) // 2].center\n"),
    ],
    "pydg-08-enemies": [
        ("abs(dx) >= abs(dy)", "abs(dx) > abs(dy)"),
        # Enemies may not stack: a plain for over a list, and a different clamp.
        ("clamp(dx, -1, 1), clamp(dy, -1, 1)", "(dx > 0) - (dx < 0), (dy > 0) - (dy < 0)"),
    ],
    "pydg-09-bump": [
        ("            enemies.remove(target)\n", "            enemies[:] = [e for e in enemies if e is not target]\n"),
        ("    return next((e for e in enemies if e['pos'] == pos), None)",
         "    for e in enemies:\n        if e['pos'] == pos:\n            return e\n    return None"),
    ],
    "pydg-10-fog": [
        # Square vision.
        ("> RADIUS * RADIUS", "> RADIUS ** 2"),
        ("if dx * dx + dy * dy > RADIUS * RADIUS:", "if max(abs(dx), abs(dy)) > RADIUS:"),
        # floor instead of round.
        ("round(px + dx * i / steps)", "px + dx * i // steps"),
        # update() needs no `global`.
        (("def update_fog():\n    global seen\n", "def update_fog():\n"),
         ("    seen |= {(x, y)", "    seen.update({(x, y)"),
         ("if in_map(x, y) and visible(x, y)}", "if in_map(x, y) and visible(x, y)})")),
    ],
    "pydg-11-potions": [
        ("        items.remove(pos)\n", "        items.pop(items.index(pos))\n"),
        ("    items = [room.random_tile(rng) for room in rooms[1:] if rng.random() < 0.6]\n",
         "    items = []\n    for room in rooms[1:]:\n        if rng.random() < 0.6:\n            items.append(room.random_tile(rng))\n"),
        # if / elif instead of match.
        (_MATCH_11,
         "    if key == 'h':\n        drink()\n    elif key in KEYS:\n        move(*KEYS[key])\n"),
    ],
    "pydg-12-gameover": [
        # if / elif instead of match.
        (_MATCH,
         "    if key == 'Enter' and state == 'over':\n        restart()\n    elif state == 'over':\n        return\n"
         "    elif key == 'h':\n        drink()\n    elif key in KEYS:\n        move(*KEYS[key])\n"),
        # Restart: generate first, the rest after.
        ("    depth = 1\n    player['hp'] = player['max_hp']\n    potions = 0\n    state = 'playing'\n    generate()\n",
         "    generate()\n    depth = 1\n    player['hp'] = player['max_hp']\n    potions = 0\n    state = 'playing'\n"),
    ],
}

#: Steps whose player and enemies can be dataclasses instead of dicts.
DATACLASS_STEPS = [s.id for s in STEPS[1:12]]
#: Steps whose generator can draw from the random module instead of a Random(seed).
MODULE_RANDOM_STEPS = [s.id for s in STEPS[4:12]]


def _as_dataclasses(code: str) -> str:
    """The same program with the player (and the enemies) as dataclasses, not dicts."""
    types = {"pos": "tuple", "hp": "int", "max_hp": "int"}
    classes = ""
    fields = re.search(r"player = \{(.*)\}", code)
    assert fields, "no player"
    keys = re.findall(r"'(\w+)':", fields.group(1))
    classes += "@dataclass\nclass Player:\n" + "".join(f"    {k}: {types[k]}\n" for k in keys) + "\n\n"
    code = code.replace(fields.group(0), "player = Player(" + re.sub(r"'(\w+)': ", r"\1=", fields.group(1)) + ")")
    enemy = re.search(r"enemies\.append\(\{(.*)\}\)", code)
    if enemy:
        keys = re.findall(r"'(\w+)':", enemy.group(1))
        classes += "@dataclass\nclass Enemy:\n" + "".join(f"    {k}: {types[k]}\n" for k in keys) + "\n\n"
        code = code.replace(enemy.group(0), "enemies.append(Enemy(" + re.sub(r"'(\w+)': ", r"\1=", enemy.group(1)) + "))")
    code = re.sub(r"\b(player|e|target)\['(\w+)'\]", r"\1.\2", code)
    code = code.replace("\ntiles = ", "\n" + classes + "tiles = ", 1)
    assert "Player" in code and "['pos']" not in code
    return "from dataclasses import dataclass\n" + code


def _with_module_random(code: str) -> str:
    made = code.replace("rng = random.Random(seed)", "rng = random")
    assert made != code
    return made


class TestShape:
    def test_ids_unique_numbered_and_titled(self) -> None:
        ids = [s.id for s in STEPS]
        assert len(ids) == len(set(ids))
        assert len(STEPS) == 13
        for n, s in enumerate(STEPS, 1):
            assert re.fullmatch(rf"pydg-{n:02d}-[a-z-]+", s.id), s.id
            assert s.title
            assert len(s.teaches) > 120, s.id
            assert s.goal.endswith("."), s.id

    def test_they_are_python_steps_on_their_own_track(self) -> None:
        assert {s.track for s in STEPS} == {"Dungeon (Python)"}
        assert {s.language for s in STEPS} == {"python"}
        assert all(s.kind == "canvas" for s in STEPS)

    @pytest.mark.skipif(not _REGISTERED, reason="PYDUNGEON_STEPS is not in canvas/__init__.py STEPS yet")
    def test_they_are_registered_together(self) -> None:
        ids = [s.id for s in ALL_STEPS]
        first = ids.index(STEPS[0].id)
        assert ids[first:first + len(STEPS)] == [s.id for s in STEPS]

    def test_each_step_starts_where_the_last_one_finished(self) -> None:
        for before, after in zip(STEPS, STEPS[1:]):
            assert after.starter == before.solution, after.id

    def test_only_the_last_step_is_open(self) -> None:
        assert [s.id for s in STEPS if not s.check] == [STEPS[-1].id]

    def test_every_program_is_python_that_compiles_and_uses_the_library(self) -> None:
        for s in STEPS:
            for code in (s.starter, s.solution):
                compile(code, s.id, "exec")
                assert "from canvas import" in code, s.id
                assert "\r" not in code and code.endswith("\n"), s.id
                assert "ctx.fillStyle" not in code and "requestAnimationFrame" not in code

    def test_every_mistake_and_other_way_names_a_real_step(self) -> None:
        for step_id in list(MISTAKES) + list(OTHER_WAYS) + DATACLASS_STEPS + MODULE_RANDOM_STEPS:
            assert step_id in BY_ID, step_id

    def test_every_checked_step_has_a_real_mistake(self) -> None:
        for s in STEPS:
            if s.check:
                assert MISTAKES.get(s.id), f"{s.id} has no mistake the check is held against"

    def test_the_hints_are_written(self) -> None:
        for s in STEPS:
            if s.check:
                assert s.hint, s.id

    def test_the_goals_name_what_the_checks_read(self) -> None:
        names = {
            "pydg-01-map": ["TILE", "tiles"],
            "pydg-02-turns": ["player", "pos", "KEYS", "on_key_down"],
            "pydg-03-walls": ["in_map", "is_wall", "move"],
            "pydg-04-camera": ["TILE", "VIEW_W", "VIEW_H", "camera"],
            "pydg-05-rooms": ["Room", "generate", "tiles", "rooms", "center", "intersects"],
            "pydg-06-corridors": ["flood", "dig_corridor"],
            "pydg-07-stairs": ["stairs", "depth"],
            "pydg-08-enemies": ["enemies", "pos", "end_turn", "enemies_act"],
            "pydg-09-bump": ["hp", "max_hp", "PLAYER_DAMAGE", "ENEMY_DAMAGE"],
            "pydg-10-fog": ["RADIUS", "seen", "visible", "update_fog"],
            "pydg-11-potions": ["items", "potions", "max_hp", "match"],
            "pydg-12-gameover": ["state", "restart"],
        }
        for step_id, wanted in names.items():
            for name in wanted:
                assert name in BY_ID[step_id].goal, f"{step_id}: the goal does not say {name}"

    def test_the_python_way_is_what_gets_taught(self) -> None:
        text = " ".join(s.teaches for s in STEPS)
        for word in ("tuple", "@dataclass", "@property", "any(", "random.Random(seed)", "randint", "cannot be changed", "[['#'] * MAP_W] * MAP_H", "TypeError",
                     "pairwise", "range(min(a, b), max(a, b) + 1)", "deque", "popleft", "pop(0)", "set", "|=",
                     "global", "UnboundLocalError", "enumerate", "slic", "tiles[-1]", "match", "f-string",
                     "unpack", "list comprehension", "next("):
            assert word in text, word

    def test_the_goals_say_which_names_the_player_may_reassign(self) -> None:
        # The checks assign these names (tiles, player pos, enemies, items, seen ...): the
        # solutions keep them all as plain top-level names.
        last = STEPS[-2].solution
        for name in ("tiles", "rooms", "player", "stairs", "enemies", "items", "seen", "depth", "potions", "state"):
            assert re.search(rf"^{name} = ", last, re.M), name


class TestChecks:
    def test_every_solution_passes_its_check(self) -> None:
        for s in STEPS:
            if not s.check:
                continue
            got = run_py_check(s.solution, s.check)
            assert got.passed, f"{s.id}: {got.message}"

    def test_every_starter_fails_its_check(self) -> None:
        for s in STEPS:
            if not s.check:
                continue
            got = run_py_check(s.starter, s.check)
            assert not got.passed, s.id
            assert got.message, s.id

    def test_real_mistakes_fail(self) -> None:
        for step_id, swaps in MISTAKES.items():
            s = _by_id(step_id)
            for change in swaps:
                got = run_py_check(_swap(s.solution, change), s.check)
                assert not got.passed, f"{step_id}: the check let this mistake through: {_label(change)!r}"
                assert got.message, step_id

    def test_other_right_answers_pass(self) -> None:
        for step_id, ways in OTHER_WAYS.items():
            s = _by_id(step_id)
            for change in ways:
                got = run_py_check(_swap(s.solution, change), s.check)
                assert got.passed, f"{step_id}: {_label(change)!r}: {got.message}"

    def test_a_dataclass_player_and_enemy_pass_wherever_they_are_a_dict(self) -> None:
        for step_id in DATACLASS_STEPS:
            s = _by_id(step_id)
            got = run_py_check(_as_dataclasses(s.solution), s.check)
            assert got.passed, f"{step_id}: {got.message}"

    def test_module_level_random_passes_wherever_the_generator_uses_a_random_instance(self) -> None:
        for step_id in MODULE_RANDOM_STEPS:
            s = _by_id(step_id)
            got = run_py_check(_with_module_random(s.solution), s.check)
            assert got.passed, f"{step_id}: {got.message}"

    def test_the_checks_say_what_to_fix_not_just_that_it_failed(self) -> None:
        rooms = _by_id("pydg-05-rooms")
        got = run_py_check(_swap(rooms.solution, ("grid = [['#'] * MAP_W for _ in range(MAP_H)]", "grid = ['#' * MAP_W for _ in range(MAP_H)]")), rooms.check)
        assert "TypeError" in got.message and "item assignment" in got.message and "line" in got.message
        got = run_py_check(_swap(rooms.solution, ("grid = [['#'] * MAP_W for _ in range(MAP_H)]", "grid = [['#'] * MAP_W] * MAP_H")), rooms.check)
        assert "wall all the way" in got.message and "MAP_H" in got.message
        got = run_py_check(_swap(rooms.solution, (_ROOM_CHECK, "")), rooms.check)
        assert "overlap" in got.message
        got = run_py_check(_swap(rooms.solution, ("rng = random.Random(seed)", "rng = random.Random()")), rooms.check)
        assert "seed" in got.message

        walls = _by_id("pydg-03-walls")
        got = run_py_check(_swap(walls.solution, ("    return not in_map(x, y) or tiles[y][x] == '#'", "    return tiles[y][x] == '#'")), walls.check)
        assert "tiles[-1]" in got.message or "IndexError" in got.message

        stairs = _by_id("pydg-07-stairs")
        got = run_py_check(_swap(stairs.solution, ("    global depth\n", "")), stairs.check)
        assert "UnboundLocalError" in got.message and "line" in got.message

        fog = _by_id("pydg-10-fog")
        got = run_py_check(_swap(fog.solution, ("def update_fog():\n    global seen\n", "def update_fog():\n")), fog.check)
        assert "UnboundLocalError" in got.message

        over = _by_id("pydg-12-gameover")
        got = run_py_check(_swap(over.solution, ("def end_turn():\n    global state\n", "def end_turn():\n")), over.check)
        assert "global state" in got.message

    def test_a_crash_is_reported_with_its_line(self) -> None:
        s = STEPS[0]
        got = run_py_check(s.starter + "\nnope()\n", s.check)
        assert not got.passed
        assert "nope" in got.message and "line" in got.message

    def test_an_endless_loop_is_reported_not_waited_on(self) -> None:
        s = STEPS[0]
        got = run_py_check(s.starter + "\nwhile True:\n    pass\n", s.check)
        assert not got.passed
        assert "loop that never ends" in got.message

    def test_the_open_step_always_passes(self) -> None:
        if not _REGISTERED:
            pytest.skip("not registered yet")
        got = check_step(STEPS[-1].id, "")
        assert got is not None and got.passed

    @pytest.mark.skipif(not _REGISTERED, reason="PYDUNGEON_STEPS is not in canvas/__init__.py STEPS yet")
    def test_check_step_runs_a_python_step_through_the_python_harness(self) -> None:
        s = STEPS[2]
        assert check_step(s.id, s.solution).passed
        assert not check_step(s.id, s.starter).passed
