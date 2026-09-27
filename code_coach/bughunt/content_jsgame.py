"""JavaScript bug hunts in game code.

Thirteen bugs that turn up in the first month of writing a game, each
one a line that is nearly right:

  clamp             the top limit hands back the bottom one, so a big
                    heal leaves the player on 0
  no dt             speed added without the frame time, so falling is
                    fast at one frame rate and right at another
  x % width         keeps the sign, so a ship leaving the left edge
                    never comes back on the right
  row.length - 1    the tile loop stops one short and misses the
                    right-hand wall
  key names         "D" released with Shift held is not "d", and the
                    Set of held keys never lets go
  AABB              one comparison checks y against the other box's x
  rows[x][y]        a string map indexed column first
  frame / FRAME_MS  no Math.floor, so the sprite sheet is read between
                    two cells
  missing vy        undefined times dt is NaN, and the coin vanishes
  ===               ten steps of 0.1 never equal 1
  splice            removing while walking forwards skips a neighbour
  this              a plain function inside forEach in a class
  switch            a case with no return falls into the next one

In every one the report is about the function you call and the cause is
in a helper above it. Everything runs in plain Node — no page, no
canvas — and the same rules hold as for the other hunts, checked by
tests/test_bughunt_jsgame.py: the bug is real, it hides on some inputs,
the report's own input shows it, and the fix changes one line in place.
"""

from __future__ import annotations

from code_coach.bughunt import Hunt

GAME = "Game code"


def _heal(hp: int, amount: int) -> int:
    return max(0, min(100, hp + amount))


def _fall_for(y, vy, dt, frames):
    for _ in range(frames):
        vy = vy + 20 * dt
        y = y + vy * dt
    return y


def _fly_all(xs: list, speed: int) -> list:
    # Python's % already lands in 0..width-1 for a negative number.
    return [(x + speed) % 320 for x in xs]


def _count_walls(rows: list) -> int:
    return sum(row.count("#") for row in rows)


def _direction(events: list) -> int:
    held: set = set()
    for ev in events:
        kind, key = ev.lower().split(":")
        if kind == "down":
            held.add(key)
        else:
            held.discard(key)
    return ("d" in held) - ("a" in held)


def _overlaps(a: dict, b: dict) -> bool:
    return (a["x"] < b["x"] + b["w"] and a["x"] + a["w"] > b["x"]
            and a["y"] < b["y"] + b["h"] and a["y"] + a["h"] > b["y"])


def _coins_touched(player: dict, coins: list) -> list:
    return [c["id"] for c in coins if _overlaps(player, c)]


def _blocked(rows: list, x: int, y: int) -> list:
    def solid(tx: int, ty: int) -> bool:
        if ty < 0 or ty >= len(rows) or tx < 0 or tx >= len(rows[0]):
            return True
        return rows[ty][tx] == "#"

    dirs = (("up", 0, -1), ("down", 0, 1), ("left", -1, 0), ("right", 1, 0))
    return [name for name, dx, dy in dirs if solid(x + dx, y + dy)]


def _sprite_cell(t: int, frames: int) -> list:
    i = (t // 100) % frames
    return [(i % 4) * 32, (i // 4) * 32]


def _positions_after(defs: list, dt, frames: int) -> list:
    out = []
    for d in defs:
        x, y = d["x"], d["y"]
        vx, vy = d.get("vx", 0), d.get("vy", 0)
        for _ in range(frames):
            x += vx * dt
            y += vy * dt
        out.append([x, y])
    return out


def _steps_to_reach(start, target, step) -> int:
    return round((target - start) / step)


def _survivors(enemies: list) -> list:
    return [e["name"] for e in enemies if e["hp"] > 0]


def _final_score(hits: list) -> int:
    return sum(hit["points"] for hit in hits)


_MOVES = {
    "idle": {"run": "running", "jump": "jumping"},
    "running": {"stop": "idle", "jump": "jumping"},
    "jumping": {"land": "idle"},
}


def _replay(events: list) -> list:
    state, seen = "idle", []
    for event in events:
        state = _MOVES[state].get(event, state)
        seen.append(state)
    return seen


JS_GAME_HUNTS: tuple[Hunt, ...] = (
    Hunt(
        id="hunt-jsg-heal-to-zero",
        title="The potion that kills",
        family=GAME,
        language="javascript",
        level=1,
        report="Drinking a big potion at 90 HP left the player on 0 HP. "
               "Small potions heal fine, and taking damage works.",
        name="heal",
        params=("hp", "amount"),
        start=(
            "const MAX_HP = 100;\n"
            "\n"
            "// Keep a value between lo and hi.\n"
            "function clamp(v, lo, hi) {\n"
            "  if (v < lo) return lo;\n"
            "  if (v > hi) return lo;\n"
            "  return v;\n"
            "}\n"
            "\n"
            "function heal(hp, amount) {\n"
            "  return clamp(hp + amount, 0, MAX_HP);\n"
            "}\n"
        ),
        fixed=(
            "const MAX_HP = 100;\n"
            "\n"
            "// Keep a value between lo and hi.\n"
            "function clamp(v, lo, hi) {\n"
            "  if (v < lo) return lo;\n"
            "  if (v > hi) return hi;\n"
            "  return v;\n"
            "}\n"
            "\n"
            "function heal(hp, amount) {\n"
            "  return clamp(hp + amount, 0, MAX_HP);\n"
            "}\n"
        ),
        solve=_heal,
        reported=(90, 25),
        cases=((50, 20), (90, 25), (10, -30), (100, 0), (95, 5), (60, 60)),
        cause="When the value is over the top limit, clamp returns lo "
              "instead of hi, so any heal past 100 comes back as 0.",
        decoys=(
            "hp + amount joins the two as text, so 90 and 25 make 9025.",
            "MAX_HP is declared with const, so heal cannot read it.",
            "The check for v < lo runs first and catches every value.",
        ),
        lesson="A clamp has two limits and two branches, and each branch "
               "must return its own limit. Math.min(hi, Math.max(lo, v)) "
               "says the same thing in one line with less room to swap "
               "them.",
        hint="The report's potion: heal(90, 25). Then a heal that stays "
             "under 100.",
        checks=(((90, 25), 100), ((50, 20), 70), ((10, -30), 0),
                ((60, 60), 100)),
    ),
    Hunt(
        id="hunt-jsg-fall-without-dt",
        title="Falling twice as fast at 60 fps",
        family=GAME,
        language="javascript",
        level=1,
        report="With dt = 0.5, four frames of falling from 0 lands at "
               "y = 100. The physics sheet says two seconds of that "
               "gravity is 50. With dt = 1 it matches the sheet.",
        name="fallFor",
        params=("y", "vy", "dt", "frames"),
        start=(
            "const GRAVITY = 20;\n"
            "\n"
            "function step(body, dt) {\n"
            "  const vy = body.vy + GRAVITY * dt;\n"
            "  return { y: body.y + vy, vy: vy };\n"
            "}\n"
            "\n"
            "function fallFor(y, vy, dt, frames) {\n"
            "  let body = { y: y, vy: vy };\n"
            "  for (let i = 0; i < frames; i++) body = step(body, dt);\n"
            "  return body.y;\n"
            "}\n"
        ),
        fixed=(
            "const GRAVITY = 20;\n"
            "\n"
            "function step(body, dt) {\n"
            "  const vy = body.vy + GRAVITY * dt;\n"
            "  return { y: body.y + vy * dt, vy: vy };\n"
            "}\n"
            "\n"
            "function fallFor(y, vy, dt, frames) {\n"
            "  let body = { y: y, vy: vy };\n"
            "  for (let i = 0; i < frames; i++) body = step(body, dt);\n"
            "  return body.y;\n"
            "}\n"
        ),
        solve=_fall_for,
        reported=(0, 0, 0.5, 4),
        cases=((0, 0, 1, 3), (0, 0, 0.5, 4), (100, -10, 1, 2),
               (0, 0, 0.25, 4), (5, 0, 1, 0)),
        cause="The position moves by the whole velocity each frame, not "
              "velocity times dt, so it only comes out right when dt is 1.",
        decoys=(
            "GRAVITY should be multiplied by dt twice.",
            "The loop runs one frame too many.",
            "step returns a new object, so the body in fallFor never "
            "changes.",
        ),
        lesson="Everything that is a rate - speed, acceleration, spin - "
               "gets multiplied by dt before it is added. Test at two "
               "frame rates: a bug like this is invisible at dt = 1.",
        hint="The report's fall: fallFor(0, 0, 0.5, 4). Then the same "
             "fall with dt = 1.",
        checks=(((0, 0, 0.5, 4), 50), ((0, 0, 1, 3), 120),
                ((100, -10, 1, 2), 140)),
    ),
    Hunt(
        id="hunt-jsg-wrap-left-edge",
        title="Lost off the left of the screen",
        family=GAME,
        language="javascript",
        level=2,
        report="Ships flying left vanish at the left edge instead of "
               "coming back on the right - one at x = 10 moving -30 ends "
               "up at -20. Ships flying right wrap fine.",
        name="flyAll",
        params=("xs", "speed"),
        start=(
            "const WIDTH = 320;\n"
            "\n"
            "// Bring an x position back onto the screen.\n"
            "function wrapX(x) {\n"
            "  return x % WIDTH;\n"
            "}\n"
            "\n"
            "function flyAll(xs, speed) {\n"
            "  return xs.map((x) => wrapX(x + speed));\n"
            "}\n"
        ),
        fixed=(
            "const WIDTH = 320;\n"
            "\n"
            "// Bring an x position back onto the screen.\n"
            "function wrapX(x) {\n"
            "  return ((x % WIDTH) + WIDTH) % WIDTH;\n"
            "}\n"
            "\n"
            "function flyAll(xs, speed) {\n"
            "  return xs.map((x) => wrapX(x + speed));\n"
            "}\n"
        ),
        solve=_fly_all,
        reported=([10, 200], -30),
        cases=(([0, 100], 5), ([310], 20), ([10, 200], -30), ([], -5),
               ([319], -400), ([50], -50)),
        cause="In JavaScript % keeps the sign of the left side, so a "
              "negative x stays negative instead of wrapping to the right.",
        decoys=(
            "map skips the ships that go off screen.",
            "WIDTH should be 319, because positions start at 0.",
            "x + speed joins the numbers as text when speed is negative.",
        ),
        lesson="% is a remainder, not a modulo: -20 % 320 is -20. To wrap "
               "a position that can go negative, add the width and take "
               "the remainder again - ((x % w) + w) % w.",
        hint="The report's ships: flyAll([10, 200], -30). Then fly some "
             "to the right, past 320.",
        checks=((([10, 200], -30), [300, 170]), (([310], 20), [10]),
                (([319], -400), [239]), (([0, 100], 5), [5, 105])),
    ),
    Hunt(
        id="hunt-jsg-right-wall-missing",
        title="The right-hand wall is missing",
        family=GAME,
        language="javascript",
        level=2,
        report="A 3 by 3 room ringed with walls is counted as having 5 "
               "walls. There are 8. The ones it misses are all in the "
               "right-hand column.",
        name="countWalls",
        params=("rows",),
        start=(
            "const WALL = \"#\";\n"
            "\n"
            "// How many walls are in one row of the map.\n"
            "function wallsInRow(row) {\n"
            "  let n = 0;\n"
            "  for (let x = 0; x < row.length - 1; x++) {\n"
            "    if (row[x] === WALL) n++;\n"
            "  }\n"
            "  return n;\n"
            "}\n"
            "\n"
            "function countWalls(rows) {\n"
            "  return rows.reduce((total, row) => total + wallsInRow(row), 0);\n"
            "}\n"
        ),
        fixed=(
            "const WALL = \"#\";\n"
            "\n"
            "// How many walls are in one row of the map.\n"
            "function wallsInRow(row) {\n"
            "  let n = 0;\n"
            "  for (let x = 0; x < row.length; x++) {\n"
            "    if (row[x] === WALL) n++;\n"
            "  }\n"
            "  return n;\n"
            "}\n"
            "\n"
            "function countWalls(rows) {\n"
            "  return rows.reduce((total, row) => total + wallsInRow(row), 0);\n"
            "}\n"
        ),
        solve=_count_walls,
        reported=(["###", "#.#", "###"],),
        cases=(([".#."],), (["#.."],), (["###", "#.#", "###"],), ([],),
               (["..#"],), (["#", "."],)),
        cause="The loop stops at row.length - 1, so the last tile of "
              "every row is never looked at.",
        decoys=(
            "reduce starts at the second row because it is given 0.",
            "=== fails because a row is a string and WALL is a single "
            "character.",
            "The loop starts at 0, which skips the left-hand wall.",
        ),
        lesson="x < row.length visits every index; x < row.length - 1 "
               "stops one short, and x <= row.length goes one past. When "
               "a count is off, test a map with something in the very "
               "last column.",
        hint="The report's room: countWalls([\"###\", \"#.#\", \"###\"]). "
             "Then a row with its only wall in the middle.",
        checks=(((["###", "#.#", "###"],), 8), (([".#."],), 1),
                ((["..#"],), 1), (([],), 0)),
    ),
    Hunt(
        id="hunt-jsg-stuck-key",
        title="Drifting with nothing held",
        family=GAME,
        language="javascript",
        level=2,
        report="Hold D to go right, press Shift to sprint, let go of D, "
               "let go of Shift: the ship keeps drifting right with no "
               "keys held. Without Shift, letting go of D stops it.",
        name="direction",
        params=("events",),
        start=(
            "// Apply one \"down:key\" or \"up:key\" event to the held keys.\n"
            "function applyEvent(held, ev) {\n"
            "  const [type, key] = ev.split(\":\");\n"
            "  if (type === \"down\") held.add(key);\n"
            "  else held.delete(key);\n"
            "}\n"
            "\n"
            "function direction(events) {\n"
            "  const held = new Set();\n"
            "  for (const ev of events) applyEvent(held, ev);\n"
            "  return (held.has(\"d\") ? 1 : 0) - (held.has(\"a\") ? 1 : 0);\n"
            "}\n"
        ),
        fixed=(
            "// Apply one \"down:key\" or \"up:key\" event to the held keys.\n"
            "function applyEvent(held, ev) {\n"
            "  const [type, key] = ev.toLowerCase().split(\":\");\n"
            "  if (type === \"down\") held.add(key);\n"
            "  else held.delete(key);\n"
            "}\n"
            "\n"
            "function direction(events) {\n"
            "  const held = new Set();\n"
            "  for (const ev of events) applyEvent(held, ev);\n"
            "  return (held.has(\"d\") ? 1 : 0) - (held.has(\"a\") ? 1 : 0);\n"
            "}\n"
        ),
        solve=_direction,
        reported=(["down:d", "down:Shift", "up:D", "up:Shift"],),
        cases=((["down:d"],), (["down:a", "down:d"],),
               (["down:a", "up:a"],), (["down:A"],),
               (["down:d", "down:Shift", "up:D", "up:Shift"],), ([],)),
        cause="Key names are compared exactly, and with Shift held D is "
              "reported as \"D\", so deleting \"D\" leaves \"d\" in the set.",
        decoys=(
            "A Set cannot hold the same key twice, so the second keydown "
            "is lost.",
            "Subtracting two booleans gives NaN.",
            "split(\":\") drops the key name when the event has capitals "
            "in it.",
        ),
        lesson="The name a key event reports can change with Shift and "
               "Caps Lock - event.key is \"D\" then. Normalise names once, "
               "as they come in, or track event.code, which names the "
               "physical key and never changes.",
        hint="The report's keys: [\"down:d\", \"down:Shift\", \"up:D\", "
             "\"up:Shift\"]. Then press and release d without Shift.",
        checks=(((["down:d", "down:Shift", "up:D", "up:Shift"],), 0),
                ((["down:d"],), 1), ((["down:A"],), -1),
                ((["down:a", "down:d"],), 0)),
    ),
    Hunt(
        id="hunt-jsg-coin-not-collected",
        title="The coin you walk straight through",
        family=GAME,
        language="javascript",
        level=2,
        report="Walking into the coin at (40, 0) doesn't collect it, and "
               "a coin 10 pixels below the player gets collected from "
               "across the gap. Coins on the diagonal work fine.",
        name="coinsTouched",
        params=("player", "coins"),
        start=(
            "// Do two boxes {x, y, w, h} overlap?\n"
            "function overlaps(a, b) {\n"
            "  return a.x < b.x + b.w && a.x + a.w > b.x &&\n"
            "    a.y < b.y + b.h && a.y + a.h > b.x;\n"
            "}\n"
            "\n"
            "function coinsTouched(player, coins) {\n"
            "  return coins\n"
            "    .filter((coin) => overlaps(player, coin))\n"
            "    .map((coin) => coin.id);\n"
            "}\n"
        ),
        fixed=(
            "// Do two boxes {x, y, w, h} overlap?\n"
            "function overlaps(a, b) {\n"
            "  return a.x < b.x + b.w && a.x + a.w > b.x &&\n"
            "    a.y < b.y + b.h && a.y + a.h > b.y;\n"
            "}\n"
            "\n"
            "function coinsTouched(player, coins) {\n"
            "  return coins\n"
            "    .filter((coin) => overlaps(player, coin))\n"
            "    .map((coin) => coin.id);\n"
            "}\n"
        ),
        solve=_coins_touched,
        reported=({"x": 36, "y": 0, "w": 8, "h": 8},
                  [{"id": "c1", "x": 40, "y": 0, "w": 4, "h": 4}]),
        cases=(
            ({"x": 8, "y": 8, "w": 8, "h": 8},
             [{"id": "c2", "x": 10, "y": 10, "w": 4, "h": 4}]),
            ({"x": 36, "y": 0, "w": 8, "h": 8},
             [{"id": "c1", "x": 40, "y": 0, "w": 4, "h": 4}]),
            ({"x": 0, "y": 0, "w": 10, "h": 10},
             [{"id": "c3", "x": 50, "y": 50, "w": 4, "h": 4}]),
            ({"x": 0, "y": 0, "w": 10, "h": 10},
             [{"id": "c4", "x": 2, "y": 20, "w": 4, "h": 4}]),
            ({"x": 0, "y": 0, "w": 10, "h": 10}, []),
        ),
        cause="The last comparison checks the player's bottom edge "
              "against the coin's x instead of its y.",
        decoys=(
            "The comparisons use < and >, so boxes that share an edge "
            "count as overlapping.",
            "filter runs after map, so the ids are tested instead of the "
            "coins.",
            "The return breaks across two lines, so JavaScript inserts a "
            "semicolon after the first.",
        ),
        lesson="Box collision is four comparisons that look alike, which "
               "is where copy-paste slips in. Write them in pairs - x "
               "with x and w, y with y and h - and test a box off to the "
               "side and one straight below, not only on the diagonal.",
        hint="The report's coin: the player at (36, 0) and a coin at "
             "(40, 0). Then put a coin on the diagonal.",
        checks=(
            (({"x": 36, "y": 0, "w": 8, "h": 8},
              [{"id": "c1", "x": 40, "y": 0, "w": 4, "h": 4}]), ["c1"]),
            (({"x": 0, "y": 0, "w": 10, "h": 10},
              [{"id": "c4", "x": 2, "y": 20, "w": 4, "h": 4}]), []),
            (({"x": 8, "y": 8, "w": 8, "h": 8},
              [{"id": "c2", "x": 10, "y": 10, "w": 4, "h": 4}]), ["c2"]),
        ),
    ),
    Hunt(
        id="hunt-jsg-rows-and-columns",
        title="Walking into walls, stopped by floor",
        family=GAME,
        language="javascript",
        level=2,
        report="In the corridor level, standing at (1, 1), the game says "
               "down is open - it is a wall - and says right is blocked, "
               "though the corridor carries on that way. In a square room "
               "it all looks right.",
        name="blocked",
        params=("rows", "x", "y"),
        start=(
            "const SOLID = \"#\";\n"
            "\n"
            "// The tile at column x, row y; off the map counts as solid.\n"
            "function tileAt(rows, x, y) {\n"
            "  if (y < 0 || y >= rows.length || x < 0 || x >= rows[0].length) return SOLID;\n"
            "  return rows[x][y];\n"
            "}\n"
            "\n"
            "function blocked(rows, x, y) {\n"
            "  const dirs = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };\n"
            "  return Object.keys(dirs).filter((d) => tileAt(rows, x + dirs[d][0], y + dirs[d][1]) === SOLID);\n"
            "}\n"
        ),
        fixed=(
            "const SOLID = \"#\";\n"
            "\n"
            "// The tile at column x, row y; off the map counts as solid.\n"
            "function tileAt(rows, x, y) {\n"
            "  if (y < 0 || y >= rows.length || x < 0 || x >= rows[0].length) return SOLID;\n"
            "  return rows[y][x];\n"
            "}\n"
            "\n"
            "function blocked(rows, x, y) {\n"
            "  const dirs = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };\n"
            "  return Object.keys(dirs).filter((d) => tileAt(rows, x + dirs[d][0], y + dirs[d][1]) === SOLID);\n"
            "}\n"
        ),
        solve=_blocked,
        reported=(["#####", "#...#", "#####"], 1, 1),
        cases=((["###", "#.#", "###"], 1, 1), (["...", "...", "..."], 1, 1),
               (["#####", "#...#", "#####"], 1, 1),
               (["....", "....", "...."], 0, 0),
               (["#####", "#...#", "#####"], 2, 1)),
        cause="rows[x][y] picks the row by x and the column by y. A map "
              "of strings is a list of rows, so it has to be rows[y][x].",
        decoys=(
            "The bounds check compares x against rows[0].length, which is "
            "the number of rows.",
            "Object.keys returns the directions in a random order.",
            "=== cannot compare a character from a string with SOLID.",
        ),
        lesson="A map written as strings is read row first: rows[y] is a "
               "line of the level and rows[y][x] is a tile on it. A "
               "square map with a symmetric layout hides the swap "
               "completely - test on a corridor.",
        hint="The report's corridor: blocked([\"#####\", \"#...#\", "
             "\"#####\"], 1, 1). Then the middle of a 3 by 3 room.",
        checks=(((["#####", "#...#", "#####"], 1, 1), ["up", "down", "left"]),
                ((["###", "#.#", "###"], 1, 1),
                 ["up", "down", "left", "right"]),
                ((["#####", "#...#", "#####"], 2, 1), ["up", "down"]),
                ((["...", "...", "..."], 1, 1), [])),
    ),
    Hunt(
        id="hunt-jsg-half-a-frame",
        title="Half of one frame, half of the next",
        family=GAME,
        language="javascript",
        level=2,
        report="At 250 ms the walk animation is drawn from x = 80 on the "
               "sheet - halfway across a cell, so two frames show at "
               "once. At 200 and 300 ms it is fine.",
        name="spriteCell",
        params=("t", "frames"),
        start=(
            "const FRAME_MS = 100;\n"
            "const COLS = 4;\n"
            "const SIZE = 32;\n"
            "\n"
            "// Which frame of the animation is showing at time t.\n"
            "function frameAt(t, frames) {\n"
            "  return (t / FRAME_MS) % frames;\n"
            "}\n"
            "\n"
            "function spriteCell(t, frames) {\n"
            "  const i = frameAt(t, frames);\n"
            "  return [(i % COLS) * SIZE, Math.floor(i / COLS) * SIZE];\n"
            "}\n"
        ),
        fixed=(
            "const FRAME_MS = 100;\n"
            "const COLS = 4;\n"
            "const SIZE = 32;\n"
            "\n"
            "// Which frame of the animation is showing at time t.\n"
            "function frameAt(t, frames) {\n"
            "  return Math.floor(t / FRAME_MS) % frames;\n"
            "}\n"
            "\n"
            "function spriteCell(t, frames) {\n"
            "  const i = frameAt(t, frames);\n"
            "  return [(i % COLS) * SIZE, Math.floor(i / COLS) * SIZE];\n"
            "}\n"
        ),
        solve=_sprite_cell,
        reported=(250, 6),
        cases=((0, 6), (300, 6), (250, 6), (700, 6), (590, 8), (1000, 4)),
        cause="t / FRAME_MS is not rounded down, so between frames the "
              "frame number has a fraction and the cell is read part way "
              "across.",
        decoys=(
            "% frames should come before the division.",
            "Math.floor(i / COLS) rounds the row the wrong way.",
            "SIZE is multiplied in twice, so every cell is twice as far "
            "along.",
        ),
        lesson="JavaScript's / always gives the exact answer, fraction "
               "and all; there is no integer division. Any count - a "
               "frame number, a tile, a row - needs Math.floor on the "
               "division that makes it.",
        hint="The report's moment: spriteCell(250, 6). Then a time that "
             "is a whole number of frames.",
        checks=(((250, 6), [64, 0]), ((590, 8), [32, 32]),
                ((700, 6), [32, 0]), ((0, 6), [0, 0])),
    ),
    Hunt(
        id="hunt-jsg-coins-vanish",
        title="The coins vanish when the level starts",
        family=GAME,
        language="javascript",
        level=3,
        report="The coins in level 2 disappear the moment it starts. They "
               "are defined with just x and y, because they do not move. "
               "Enemies, which have speeds, move fine.",
        name="positionsAfter",
        params=("defs", "dt", "frames"),
        start=(
            "// Build an entity from the level's definition of it.\n"
            "function makeEntity(def) {\n"
            "  return { x: def.x, y: def.y, vx: def.vx, vy: def.vy };\n"
            "}\n"
            "\n"
            "function move(e, dt) {\n"
            "  e.x += e.vx * dt;\n"
            "  e.y += e.vy * dt;\n"
            "}\n"
            "\n"
            "function positionsAfter(defs, dt, frames) {\n"
            "  const entities = defs.map(makeEntity);\n"
            "  for (let f = 0; f < frames; f++) entities.forEach((e) => move(e, dt));\n"
            "  return entities.map((e) => [e.x, e.y]);\n"
            "}\n"
        ),
        fixed=(
            "// Build an entity from the level's definition of it.\n"
            "function makeEntity(def) {\n"
            "  return { x: def.x, y: def.y, vx: def.vx ?? 0, vy: def.vy ?? 0 };\n"
            "}\n"
            "\n"
            "function move(e, dt) {\n"
            "  e.x += e.vx * dt;\n"
            "  e.y += e.vy * dt;\n"
            "}\n"
            "\n"
            "function positionsAfter(defs, dt, frames) {\n"
            "  const entities = defs.map(makeEntity);\n"
            "  for (let f = 0; f < frames; f++) entities.forEach((e) => move(e, dt));\n"
            "  return entities.map((e) => [e.x, e.y]);\n"
            "}\n"
        ),
        solve=_positions_after,
        reported=([{"x": 10, "y": 5}], 0.5, 2),
        cases=(
            ([{"x": 0, "y": 0, "vx": 2, "vy": 4}], 0.5, 2),
            ([{"x": 10, "y": 5}], 0.5, 2),
            ([{"x": 1, "y": 1, "vx": 2}], 1, 1),
            ([], 1, 3),
            ([{"x": 0, "y": 0, "vx": 0, "vy": -1},
              {"x": 5, "y": 5, "vx": 1, "vy": 0}], 0.25, 4),
        ),
        cause="A definition with no vx or vy gives undefined, and "
              "undefined * dt is NaN, which then spreads into x and y.",
        decoys=(
            "forEach does not change the entities, so move has no effect.",
            "defs.map passes the index as a second argument, which "
            "overwrites y.",
            "0.5 cannot be stored exactly, so the positions drift until "
            "they are too small to see.",
        ),
        lesson="Reading a field that is not there gives undefined, and "
               "arithmetic on undefined gives NaN - silently, with no "
               "error, and NaN wins every sum after it. Default every "
               "number an entity is moved by when the entity is built, "
               "so nothing downstream has to wonder.",
        hint="The report's coin: positionsAfter([{\"x\": 10, \"y\": 5}], "
             "0.5, 2). Then give the coin both speeds, set to 0.",
        checks=((([{"x": 10, "y": 5}], 0.5, 2), [[10, 5]]),
                (([{"x": 0, "y": 0, "vx": 2, "vy": 4}], 0.5, 2), [[2, 4]]),
                (([{"x": 1, "y": 1, "vx": 2}], 1, 1), [[3, 1]])),
    ),
    Hunt(
        id="hunt-jsg-lift-never-stops",
        title="The lift that never stops",
        family=GAME,
        language="javascript",
        level=3,
        report="The lift should take 3 steps of 0.1 to rise from 0 to "
               "0.3. It sails past and only stops when it gives up at "
               "100 steps. Steps of 0.5 stop exactly where they should.",
        name="stepsToReach",
        params=("start", "target", "step"),
        start=(
            "// Has x reached the target?\n"
            "function arrived(x, target) {\n"
            "  return x === target;\n"
            "}\n"
            "\n"
            "function stepsToReach(start, target, step) {\n"
            "  let x = start;\n"
            "  let n = 0;\n"
            "  while (!arrived(x, target) && n < 100) {\n"
            "    x += step;\n"
            "    n++;\n"
            "  }\n"
            "  return n;\n"
            "}\n"
        ),
        fixed=(
            "// Has x reached the target?\n"
            "function arrived(x, target) {\n"
            "  return Math.abs(x - target) < 1e-9;\n"
            "}\n"
            "\n"
            "function stepsToReach(start, target, step) {\n"
            "  let x = start;\n"
            "  let n = 0;\n"
            "  while (!arrived(x, target) && n < 100) {\n"
            "    x += step;\n"
            "    n++;\n"
            "  }\n"
            "  return n;\n"
            "}\n"
        ),
        solve=_steps_to_reach,
        reported=(0, 0.3, 0.1),
        cases=((0, 2, 0.5), (0, 0.3, 0.1), (1, 1, 0.1), (0, 0.2, 0.1),
               (2, 0.5, -0.25), (0, 0.7, 0.1)),
        cause="0.1 + 0.1 + 0.1 is 0.30000000000000004, not 0.3, so === "
              "never sees the lift arrive.",
        decoys=(
            "The loop tests n < 100 before arrived, so it always runs 100 "
            "times.",
            "x += step adds the step as text, making \"00.1\".",
            "while stops only when both conditions are false.",
        ),
        lesson="Sums of decimals are almost never exact in binary, so "
               "=== between floats is a coin toss. Compare within a "
               "small tolerance, or test for having passed the mark "
               "(x >= target) and snap to it.",
        hint="The report's lift: stepsToReach(0, 0.3, 0.1). Then try "
             "steps of 0.5.",
        checks=(((0, 0.3, 0.1), 3), ((0, 2, 0.5), 4), ((1, 1, 0.1), 0),
                ((2, 0.5, -0.25), 6)),
    ),
    Hunt(
        id="hunt-jsg-bat-survives",
        title="One bat too many",
        family=GAME,
        language="javascript",
        level=3,
        report="A bomb takes two bats that were next to each other in the "
               "list down to 0 HP, but one of them is still flying about "
               "afterwards. A single dead bat is always removed.",
        name="survivors",
        params=("enemies",),
        start=(
            "// Take the dead out of the list.\n"
            "function removeDead(list) {\n"
            "  for (let i = 0; i < list.length; i++) {\n"
            "    if (list[i].hp <= 0) list.splice(i, 1);\n"
            "  }\n"
            "}\n"
            "\n"
            "function survivors(enemies) {\n"
            "  const list = enemies.slice();\n"
            "  removeDead(list);\n"
            "  return list.map((e) => e.name);\n"
            "}\n"
        ),
        fixed=(
            "// Take the dead out of the list.\n"
            "function removeDead(list) {\n"
            "  for (let i = list.length - 1; i >= 0; i--) {\n"
            "    if (list[i].hp <= 0) list.splice(i, 1);\n"
            "  }\n"
            "}\n"
            "\n"
            "function survivors(enemies) {\n"
            "  const list = enemies.slice();\n"
            "  removeDead(list);\n"
            "  return list.map((e) => e.name);\n"
            "}\n"
        ),
        solve=_survivors,
        reported=([{"name": "bat1", "hp": 0}, {"name": "bat2", "hp": 0},
                   {"name": "orc", "hp": 4}],),
        cases=(
            ([{"name": "bat1", "hp": 0}, {"name": "orc", "hp": 4}],),
            ([{"name": "orc", "hp": 4}, {"name": "imp", "hp": 1}],),
            ([{"name": "bat1", "hp": 0}, {"name": "bat2", "hp": 0},
              {"name": "orc", "hp": 4}],),
            ([{"name": "bat", "hp": 0}, {"name": "orc", "hp": 4},
              {"name": "imp", "hp": -2}],),
            ([],),
            ([{"name": "a", "hp": 0}, {"name": "b", "hp": 0},
              {"name": "c", "hp": 0}],),
        ),
        cause="splice shifts everything after the removed enemy down one "
              "place, and then i++ steps past the one that moved into its "
              "slot.",
        decoys=(
            "slice copies the enemies, so removeDead changes a different "
            "list from the one that is returned.",
            "hp <= 0 does not match an hp of exactly 0.",
            "splice(i, 1) removes the enemy after i, not the one at i.",
        ),
        lesson="Removing from an array while walking it forwards skips "
               "whatever slides into the gap. Walk it backwards, so the "
               "shift only moves items already visited, or build a new "
               "array with filter.",
        hint="The report's bomb: two dead bats side by side, then an orc. "
             "Then try a dead bat with a live enemy between it and the "
             "next dead one.",
        checks=(
            (([{"name": "bat1", "hp": 0}, {"name": "bat2", "hp": 0},
               {"name": "orc", "hp": 4}],), ["orc"]),
            (([{"name": "bat", "hp": 0}, {"name": "orc", "hp": 4},
               {"name": "imp", "hp": -2}],), ["orc"]),
            (([],), []),
        ),
    ),
    Hunt(
        id="hunt-jsg-score-screen-crash",
        title="The score screen crashes",
        family=GAME,
        language="javascript",
        level=4,
        report="Finishing a level with any hits at all crashes the score "
               "screen. A level with no hits shows a score of 0 fine.",
        name="finalScore",
        params=("hits",),
        start=(
            "class Scoreboard {\n"
            "  constructor() {\n"
            "    this.total = 0;\n"
            "  }\n"
            "  add(hits) {\n"
            "    hits.forEach(function (hit) {\n"
            "      this.total += hit.points;\n"
            "    });\n"
            "  }\n"
            "}\n"
            "\n"
            "function finalScore(hits) {\n"
            "  const board = new Scoreboard();\n"
            "  board.add(hits);\n"
            "  return board.total;\n"
            "}\n"
        ),
        fixed=(
            "class Scoreboard {\n"
            "  constructor() {\n"
            "    this.total = 0;\n"
            "  }\n"
            "  add(hits) {\n"
            "    hits.forEach((hit) => {\n"
            "      this.total += hit.points;\n"
            "    });\n"
            "  }\n"
            "}\n"
            "\n"
            "function finalScore(hits) {\n"
            "  const board = new Scoreboard();\n"
            "  board.add(hits);\n"
            "  return board.total;\n"
            "}\n"
        ),
        solve=_final_score,
        reported=([{"points": 10}],),
        cases=(([],), ([{"points": 10}],),
               ([{"points": 5}, {"points": 20}],)),
        cause="The callback is a plain function, so inside it this is "
              "undefined rather than the scoreboard, and this.total "
              "throws.",
        decoys=(
            "total is set in the constructor, which runs after add.",
            "forEach cannot be used on an array of objects.",
            "hit.points is a string, so += fails on it.",
        ),
        lesson="A plain function gets its own this from however it is "
               "called, and forEach calls it with none - in a class, "
               "that is undefined. Arrow functions have no this of their "
               "own and use the method's, so callbacks inside a class "
               "should be arrows.",
        hint="The report's level: finalScore([{\"points\": 10}]). Then a "
             "level with no hits.",
        checks=((([{"points": 10}],), 10), (([],), 0),
                (([{"points": 5}, {"points": 20}],), 25)),
    ),
    Hunt(
        id="hunt-jsg-run-stops-dead",
        title="Running stops dead on the ground",
        family=GAME,
        language="javascript",
        level=4,
        report="The ground sends 'land' every frame the player touches "
               "it. Once running, the player drops straight back to idle "
               "on the next frame. Jumping and landing work.",
        name="replay",
        params=("events",),
        start=(
            "// The player's next state, given what just happened.\n"
            "function transition(state, event) {\n"
            "  switch (state) {\n"
            "    case \"idle\":\n"
            "      if (event === \"run\") return \"running\";\n"
            "      if (event === \"jump\") return \"jumping\";\n"
            "      return state;\n"
            "    case \"running\":\n"
            "      if (event === \"stop\") return \"idle\";\n"
            "      if (event === \"jump\") return \"jumping\";\n"
            "      // stays running\n"
            "    case \"jumping\":\n"
            "      if (event === \"land\") return \"idle\";\n"
            "      return state;\n"
            "  }\n"
            "}\n"
            "\n"
            "function replay(events) {\n"
            "  let state = \"idle\";\n"
            "  const seen = [];\n"
            "  for (const event of events) {\n"
            "    state = transition(state, event);\n"
            "    seen.push(state);\n"
            "  }\n"
            "  return seen;\n"
            "}\n"
        ),
        fixed=(
            "// The player's next state, given what just happened.\n"
            "function transition(state, event) {\n"
            "  switch (state) {\n"
            "    case \"idle\":\n"
            "      if (event === \"run\") return \"running\";\n"
            "      if (event === \"jump\") return \"jumping\";\n"
            "      return state;\n"
            "    case \"running\":\n"
            "      if (event === \"stop\") return \"idle\";\n"
            "      if (event === \"jump\") return \"jumping\";\n"
            "      return state;\n"
            "    case \"jumping\":\n"
            "      if (event === \"land\") return \"idle\";\n"
            "      return state;\n"
            "  }\n"
            "}\n"
            "\n"
            "function replay(events) {\n"
            "  let state = \"idle\";\n"
            "  const seen = [];\n"
            "  for (const event of events) {\n"
            "    state = transition(state, event);\n"
            "    seen.push(state);\n"
            "  }\n"
            "  return seen;\n"
            "}\n"
        ),
        solve=_replay,
        reported=(["run", "land"],),
        cases=((["jump", "land"],), (["run", "stop"],),
               (["run", "jump", "land"],), (["run", "land"],),
               (["run", "land", "jump"],), ([],)),
        cause="The running case has no return or break at its end, so it "
              "falls through into the jumping case and 'land' sends it "
              "to idle.",
        decoys=(
            "switch compares with ==, so \"running\" matches \"jumping\".",
            "replay reads state before transition has changed it.",
            "The idle case returns state, which ends the switch for "
            "every other case too.",
        ),
        lesson="A case in a switch runs on into the next one unless "
               "something stops it - a comment saying it should stop "
               "does not. End every case with return or break, or keep "
               "the states in a table of allowed moves, where a missing "
               "entry cannot fall anywhere.",
        hint="The report's frames: replay([\"run\", \"land\"]). Then jump "
             "and land.",
        checks=(((["run", "land"],), ["running", "running"]),
                ((["jump", "land"],), ["jumping", "idle"]),
                ((["run", "land", "jump"],),
                 ["running", "running", "jumping"]),
                (([],), [])),
    ),
)
