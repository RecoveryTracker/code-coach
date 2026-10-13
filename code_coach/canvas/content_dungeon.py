"""The Dungeon track: a turn-based roguelike on a grid of tiles.

The other tracks run on a clock. A roguelike does not: nothing happens until
you press a key, and then everything happens once - you move, then each enemy
moves. A key press is the unit of time, not a frame. The track builds, in order:
a map made of strings, a player that steps one tile per key press, walls, a
camera, a seeded-random dungeon of rooms joined by corridors, stairs, enemies
that take their turn after yours, fighting, fog of war, potions, and game over.

The checks never look at a particular layout. The level generator is checked on
its properties - rooms inside the map and not overlapping, every floor tile
reachable (the check floods the map itself), the player and the stairs in
different rooms - over thirty seeds the check supplies, so any correct
generator passes. Same rules as the other tracks: each step's starter is the
step before, finished; a check plays the program and never reads it.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

_SETUP = """const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');
"""

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

_CLAMP = """function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}
"""

_WALLS = """function inMap(x, y) {
  return y >= 0 && y < map.length && x >= 0 && x < map[y].length;
}

function isWall(x, y) {
  return !inMap(x, y) || map[y][x] === '#';
}
"""

_ROOM_HELPERS = """function intersects(a, b) {
  return a.x <= b.x + b.w && b.x <= a.x + a.w && a.y <= b.y + b.h && b.y <= a.y + a.h;
}

function center(room) {
  return { x: room.x + Math.floor(room.w / 2), y: room.y + Math.floor(room.h / 2) };
}
"""

_TUNNEL = """function tunnel(grid, a, b) {
  for (let x = Math.min(a.x, b.x); x <= Math.max(a.x, b.x); x++) grid[a.y][x] = '.';
  for (let y = Math.min(a.y, b.y); y <= Math.max(a.y, b.y); y++) grid[y][b.x] = '.';
}
"""

_RANDOM_TILE = """function randomTile(room) {
  return {
    x: room.x + Math.floor(Math.random() * room.w),
    y: room.y + Math.floor(Math.random() * room.h),
  };
}
"""

_VISIBLE = """function visible(x, y) {
  const dx = x - player.x;
  const dy = y - player.y;
  if (dx * dx + dy * dy > RADIUS * RADIUS) return false;
  const steps = Math.max(Math.abs(dx), Math.abs(dy));
  for (let i = 1; i < steps; i++) {
    const cx = Math.round(player.x + (dx * i) / steps);
    const cy = Math.round(player.y + (dy * i) / steps);
    if (isWall(cx, cy)) return false;
  }
  return true;
}

function updateFog() {
  for (let y = player.y - RADIUS; y <= player.y + RADIUS; y++) {
    for (let x = player.x - RADIUS; x <= player.x + RADIUS; x++) {
      if (inMap(x, y) && visible(x, y)) seen.add(x + ',' + y);
    }
  }
}
"""

_ENEMY_AT = """function enemyAt(x, y) {
  return enemies.find((e) => e.x === x && e.y === y);
}
"""

_PICKUP = """function pickUp() {
  const found = items.find((i) => i.x === player.x && i.y === player.y);
  if (!found) return;
  items = items.filter((i) => i !== found);
  potions += 1;
}

function drink() {
  if (potions === 0) return;
  potions -= 1;
  player.hp = Math.min(player.maxHp, player.hp + 5);
  endTurn();
}
"""

_RESTART = """function restart() {
  depth = 1;
  player.hp = player.maxHp;
  potions = 0;
  state = 'playing';
  generate();
}
"""

_KEYS = """const KEYS = {
  ArrowUp: { x: 0, y: -1 },
  ArrowDown: { x: 0, y: 1 },
  ArrowLeft: { x: -1, y: 0 },
  ArrowRight: { x: 1, y: 0 },
};
"""

_LOOP = """function loop() {
  draw();
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
"""


def _consts(n: int) -> str:
    lines = ["const TILE = %d;" % (32 if n >= 4 else 16)]
    if n >= 4:
        lines += ["const VIEW_W = canvas.width / TILE;", "const VIEW_H = canvas.height / TILE;"]
    if n >= 5:
        lines += ["const MAP_W = 50;", "const MAP_H = 30;"]
    if n >= 9:
        lines += ["const PLAYER_DAMAGE = 2;", "const ENEMY_DAMAGE = 1;"]
    if n >= 10:
        lines += ["const RADIUS = 6;"]
    return "\n".join(lines) + "\n"


def _state(n: int) -> str:
    if n >= 5:
        lines = ["let map = [];", "let rooms = [];"]
    else:
        lines = ["let map = [", *("  '%s'," % row for row in _HAND_MAP), "];"]
    if n >= 2:
        if n >= 9:
            lines.append("let player = { x: 1, y: 1, hp: 10, maxHp: 10 };")
        else:
            lines.append("let player = { x: 1, y: 1 };")
    if n >= 7:
        lines.append("let stairs = { x: 0, y: 0 };")
    if n >= 8:
        lines.append("let enemies = [];")
    if n >= 11:
        lines.append("let items = [];")
    if n >= 7:
        lines.append("let depth = 1;")
    if n >= 11:
        lines.append("let potions = 0;")
    if n >= 10:
        lines.append("let seen = new Set();")
    if n >= 12:
        lines.append("let state = 'playing';")
    if n >= 4:
        lines += ["let camX = 0;", "let camY = 0;"]
    return "\n".join(lines) + "\n"


def _generate(n: int) -> str:
    s = "function generate() {\n"
    s += "  const grid = Array.from({ length: MAP_H }, () => Array(MAP_W).fill('#'));\n"
    s += "  rooms = [];\n"
    s += """  for (let tries = 0; tries < 60 && rooms.length < 8; tries++) {
    const w = 4 + Math.floor(Math.random() * 6);
    const h = 4 + Math.floor(Math.random() * 4);
    const room = {
      x: 1 + Math.floor(Math.random() * (MAP_W - w - 1)),
      y: 1 + Math.floor(Math.random() * (MAP_H - h - 1)),
      w,
      h,
    };
    if (rooms.some((r) => intersects(room, r))) continue;
    rooms.push(room);
    for (let y = room.y; y < room.y + room.h; y++) {
      for (let x = room.x; x < room.x + room.w; x++) grid[y][x] = '.';
    }
  }
"""
    if n >= 6:
        s += """  for (let i = 1; i < rooms.length; i++) {
    tunnel(grid, center(rooms[i - 1]), center(rooms[i]));
  }
"""
    s += "  map = grid.map((row) => row.join(''));\n"
    s += """  const start = center(rooms[0]);
  player.x = start.x;
  player.y = start.y;
"""
    if n >= 7:
        s += """  const end = center(rooms[rooms.length - 1]);
  stairs = { x: end.x, y: end.y };
"""
    if n >= 8:
        hp = ", hp: 4" if n >= 9 else ""
        s += """  enemies = [];
  for (const room of rooms.slice(1)) {
    const spot = randomTile(room);
    if (spot.x !== stairs.x || spot.y !== stairs.y) {
      enemies.push({ x: spot.x, y: spot.y%s });
    }
  }
""" % hp
    if n >= 11:
        s += """  items = [];
  for (const room of rooms.slice(1)) {
    if (Math.random() < 0.6) items.push(randomTile(room));
  }
"""
    if n >= 10:
        s += """  seen = new Set();
  updateFog();
"""
    return s + "}\n"


def _enemies_act(n: int) -> str:
    attack = ""
    if n >= 9:
        attack = """    if (Math.abs(dx) + Math.abs(dy) === 1) {
      player.hp -= ENEMY_DAMAGE;
      continue;
    }
"""
    s = """function enemiesAct() {
  for (const e of enemies) {
    const dx = player.x - e.x;
    const dy = player.y - e.y;
""" + attack + """    const stepX = Math.sign(dx);
    const stepY = Math.sign(dy);
    const tries = Math.abs(dx) >= Math.abs(dy) ? [[stepX, 0], [0, stepY]] : [[0, stepY], [stepX, 0]];
    for (const [sx, sy] of tries) {
      const x = e.x + sx;
      const y = e.y + sy;
      if ((sx === 0 && sy === 0) || isWall(x, y) || (x === player.x && y === player.y)) continue;
      e.x = x;
      e.y = y;
      break;
    }
  }
}

function endTurn() {
  enemiesAct();
"""
    if n >= 10:
        s += "  updateFog();\n"
    if n >= 12:
        s += "  if (player.hp <= 0) state = 'over';\n"
    return s + "}\n"


def _move(n: int) -> str:
    s = """function move(dx, dy) {
  const x = player.x + dx;
  const y = player.y + dy;
  if (isWall(x, y)) return;
"""
    if n >= 9:
        s += """  const target = enemyAt(x, y);
  if (target) {
    target.hp -= PLAYER_DAMAGE;
    if (target.hp <= 0) enemies = enemies.filter((e) => e !== target);
    endTurn();
    return;
  }
"""
    s += """  player.x = x;
  player.y = y;
"""
    if n >= 11:
        s += "  pickUp();\n"
    if n >= 7:
        s += """  if (x === stairs.x && y === stairs.y) {
    depth += 1;
    generate();
"""
        if n >= 8:
            s += "    return;\n"
        s += "  }\n"
    if n >= 8:
        s += "  endTurn();\n"
    return s + "}\n"


def _keydown(n: int) -> str:
    if n == 2:
        return """addEventListener('keydown', (e) => {
  if (e.repeat) return;
  const d = KEYS[e.key];
  if (d) {
    player.x += d.x;
    player.y += d.y;
  }
});
"""
    s = "addEventListener('keydown', (e) => {\n  if (e.repeat) return;\n"
    if n >= 12:
        s += """  if (state === 'over') {
    if (e.key === 'Enter') restart();
    return;
  }
"""
    if n >= 11:
        s += "  if (e.key === 'h') drink();\n"
    s += "  const d = KEYS[e.key];\n  if (d) move(d.x, d.y);\n});\n"
    return s


def _draw(n: int) -> str:
    cam = n >= 4
    fog = n >= 10
    s = """function drawTile(x, y, color) {
  ctx.fillStyle = color;
  ctx.fillRect(%s, TILE, TILE);
}

function draw() {
  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
""" % ("(x - camX) * TILE, (y - camY) * TILE" if cam else "x * TILE, y * TILE")
    if cam:
        s += """  camX = clamp(player.x - Math.floor(VIEW_W / 2), 0, map[0].length - VIEW_W);
  camY = clamp(player.y - Math.floor(VIEW_H / 2), 0, map.length - VIEW_H);
"""
    rows = "camY" if cam else "0"
    rows_end = "camY + VIEW_H" if cam else "map.length"
    cols = "camX" if cam else "0"
    cols_end = "camX + VIEW_W" if cam else "map[y].length"
    s += "  for (let y = %s; y < %s; y++) {\n" % (rows, rows_end)
    s += "    for (let x = %s; x < %s; x++) {\n" % (cols, cols_end)
    if fog:
        s += """      if (visible(x, y)) drawTile(x, y, map[y][x] === '#' ? '#4a5568' : '#2d3748');
      else if (seen.has(x + ',' + y)) drawTile(x, y, map[y][x] === '#' ? '#262c37' : '#1c2230');
"""
    else:
        s += "      drawTile(x, y, map[y][x] === '#' ? '#4a5568' : '#2d3748');\n"
    s += "    }\n  }\n"
    if n >= 7:
        if fog:
            s += "  if (seen.has(stairs.x + ',' + stairs.y)) drawTile(stairs.x, stairs.y, '#b794f4');\n"
        else:
            s += "  drawTile(stairs.x, stairs.y, '#b794f4');\n"
    if n >= 11:
        s += "  for (const i of items) if (visible(i.x, i.y)) drawTile(i.x, i.y, '#f6e05e');\n"
    if n >= 8:
        if fog:
            s += "  for (const e of enemies) if (visible(e.x, e.y)) drawTile(e.x, e.y, '#f56565');\n"
        else:
            s += "  for (const e of enemies) drawTile(e.x, e.y, '#f56565');\n"
    if n >= 2:
        s += "  drawTile(player.x, player.y, '#4fd1c5');\n"
    if n >= 7:
        s += "  ctx.fillStyle = 'white';\n  ctx.font = '16px monospace';\n"
        s += "  ctx.fillText(`Depth: ${depth}`, 8, 20);\n"
        if n >= 9:
            s += "  ctx.fillText(`HP: ${player.hp}/${player.maxHp}`, 8, 40);\n"
        if n >= 11:
            s += "  ctx.fillText(`Potions: ${potions}`, 8, 60);\n"
    if n >= 12:
        s += """  if (state === 'over') {
    ctx.font = '32px monospace';
    ctx.fillText('Game over', 150, 160);
    ctx.font = '16px monospace';
    ctx.fillText('Enter to play again', 150, 190);
  }
"""
    return s + "}\n"


def _game(n: int) -> str:
    """The whole program as it stands when step n is finished (0: the empty start)."""
    if n == 0:
        return "\n".join([
            _SETUP,
            "function draw() {\n  ctx.fillStyle = '#10141f';\n"
            "  ctx.fillRect(0, 0, canvas.width, canvas.height);\n}\n",
            _LOOP,
        ])
    blocks = [_SETUP, _consts(n), _state(n)]
    if n >= 2:
        blocks.append(_KEYS)
    if n >= 4:
        blocks.append(_CLAMP)
    if n >= 3:
        blocks.append(_WALLS)
    if n >= 5:
        blocks.append(_ROOM_HELPERS)
    if n >= 6:
        blocks.append(_TUNNEL)
    if n >= 8:
        blocks.append(_RANDOM_TILE)
    if n >= 5:
        blocks.append(_generate(n))
    if n >= 10:
        blocks.append(_VISIBLE)
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
        blocks.append(_keydown(n))
    blocks.append(_draw(n))
    if n >= 5:
        blocks.append("generate();\n")
    blocks.append(_LOOP)
    return "\n".join(blocks)


_P = [_game(i) for i in range(13)]

# ── Shared by the checks ────────────────────────────────────────────────
# press: one key press the way a turn-based game wants it - down, up, and a
# frame so a game that reads input in its loop sees it too.
_PRESS = """
const press = (key) => {
  cc.press(key);
  cc.release(key);
  cc.frames(1);
};
const at = () => player.x + "," + player.y;
"""

# arena: the learner's map with the same size, replaced by open floor (plus a
# wall ring and any walls the check names), so the check controls the scene.
_ARENA = """
const arena = (walls, border) => {
  const w = map[0].length;
  const h = map.length;
  const rows = [];
  for (let y = 0; y < h; y++) {
    let row = "";
    for (let x = 0; x < w; x++) {
      const edge = border && (x === 0 || y === 0 || x === w - 1 || y === h - 1);
      const wall = (walls || []).some((c) => c[0] === x && c[1] === y);
      row += edge || wall ? "#" : ".";
    }
    rows.push(row);
  }
  map = rows;
};
"""

# What was drawn where, with a camera (steps 4 on).
_DRAWN = """
const drawnAt = () => {
  const found = new Map();
  for (const r of cc.rects()) found.set(r.x + "," + r.y, r);
  return found;
};
const tileFill = (tx, ty) => {
  const r = drawnAt().get((tx - camX) * TILE + "," + (ty - camY) * TILE);
  return r && r.w >= TILE - 1 ? r.fill : undefined;
};
"""

# The generator's checks: a seeded random of the check's own, properties of a
# level, and a flood fill that is the check's, not the learner's.
_LEVELS = """
const seed = (n) => {
  let s = n >>> 0;
  Math.random = () => {
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
};
const inRoom = (p, r) => p.x >= r.x && p.x < r.x + r.w && p.y >= r.y && p.y < r.y + r.h;
const roomOf = (p) => rooms.findIndex((r) => inRoom(p, r));
const floors = () => {
  const out = [];
  for (let y = 0; y < map.length; y++) for (let x = 0; x < map[y].length; x++) if (map[y][x] === ".") out.push([x, y]);
  return out;
};
const reach = (sx, sy) => {
  const got = new Set([sx + "," + sy]);
  const todo = [[sx, sy]];
  while (todo.length) {
    const [x, y] = todo.pop();
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const nx = x + dx;
      const ny = y + dy;
      if (ny < 0 || ny >= map.length || nx < 0 || nx >= map[ny].length) continue;
      if (map[ny][nx] !== "." || got.has(nx + "," + ny)) continue;
      got.add(nx + "," + ny);
      todo.push([nx, ny]);
    }
  }
  return got;
};
const checkRooms = (tag) => {
  const W = map[0].length;
  const H = map.length;
  expect(Array.isArray(rooms) && rooms.length >= 3, `${tag}: generate() made ${Array.isArray(rooms) ? rooms.length : 0} rooms; a level should have several (keep trying to place them until there are a handful).`);
  for (const r of rooms) {
    expect([r.x, r.y, r.w, r.h].every(Number.isInteger) && r.w >= 2 && r.h >= 2, `${tag}: every room is { x, y, w, h } - whole numbers, at least 2 tiles each way.`);
    expect(r.x >= 1 && r.y >= 1 && r.x + r.w <= W - 1 && r.y + r.h <= H - 1, `${tag}: a room at x ${r.x}, y ${r.y}, ${r.w} by ${r.h} runs into the edge of the ${W} by ${H} map. Keep a wall all round the edge: x from 1 to MAP_W - w - 1, y from 1 to MAP_H - h - 1.`);
    for (let y = r.y; y < r.y + r.h; y++) {
      for (let x = r.x; x < r.x + r.w; x++) {
        expect(map[y][x] === ".", `${tag}: the room at x ${r.x}, y ${r.y} is not all floor - column ${x}, row ${y} is '${map[y][x]}'.`);
      }
    }
  }
  for (let i = 0; i < rooms.length; i++) {
    for (let j = i + 1; j < rooms.length; j++) {
      const a = rooms[i];
      const b = rooms[j];
      const overlap = a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
      expect(!overlap, `${tag}: two rooms overlap (x ${a.x}, y ${a.y}, ${a.w} by ${a.h} and x ${b.x}, y ${b.y}, ${b.w} by ${b.h}). Throw a room away if it intersects one already placed.`);
    }
  }
  for (let x = 0; x < W; x++) expect(map[0][x] === "#" && map[H - 1][x] === "#", `${tag}: the top and bottom rows of the map should be wall all the way along.`);
  for (let y = 0; y < H; y++) expect(map[y][0] === "#" && map[y][W - 1] === "#", `${tag}: the first and last column of the map should be wall all the way down.`);
};
"""


DUNGEON_STEPS: tuple[Step, ...] = (
    Step(
        id="dg-01-map",
        track="Dungeon",
        title="A map made of strings",
        teaches=(
            "A roguelike map is just text: each row is a string, each "
            "character a tile - '#' is wall, '.' is floor. map[y][x] is the "
            "tile in row y, column x, with the ROW first: map[y] picks the "
            "row and [x] picks the character in it. Swap them and you read a "
            "different tile, or crash on a map that is wider than it is "
            "tall. Drawing is two loops - rows, then the characters of each "
            "row - and one fillRect per tile at x * TILE, y * TILE. Take the "
            "sizes from the map itself (map.length, map[y].length) rather "
            "than typing 30 and 20 into the loops."
        ),
        goal="Add const TILE = 16 and let map, an array of 20 strings of 30 characters each: '#' all round the edge, a few walls inside, and floor at column 1, row 1. Draw every tile each frame, walls and floor in different colours.",
        starter=_P[0],
        solution=_P[1],
        check="""
expect(typeof TILE === "number" && TILE === 16, "Add const TILE = 16; - the size of one tile in pixels.");
expect(typeof map !== "undefined" && Array.isArray(map) && map.length === 20, "Make let map an array of 20 strings - one string per row.");
for (let y = 0; y < 20; y++) {
  expect(typeof map[y] === "string" && map[y].length === 30, `Row ${y} of the map should be a string of exactly 30 characters (a 30 by 20 map of 16 pixel tiles fills the 480 by 320 canvas).`);
  expect(/^[#.]+$/.test(map[y]), `Row ${y} has a character that is not '#' or '.'.`);
}
for (let x = 0; x < 30; x++) expect(map[0][x] === "#" && map[19][x] === "#", "The top and bottom rows should be wall all the way along.");
for (let y = 0; y < 20; y++) expect(map[y][0] === "#" && map[y][29] === "#", "The first and last column should be wall all the way down.");
expect(map[1][1] === ".", "Column 1, row 1 should be floor - the player will start there. map[1][1] is the second character of the second string.");
let inner = 0;
for (let y = 1; y < 19; y++) for (let x = 1; x < 29; x++) if (map[y][x] === "#") inner++;
expect(inner >= 5, "Put a few walls inside the map too - a pillar, a short wall - so there is something to walk round.");
cc.frames(1);
const drawn = new Map();
for (const r of cc.rects()) drawn.set(r.x + "," + r.y, r);
const wallFills = new Set();
const floorFills = new Set();
for (let y = 0; y < 20; y++) {
  for (let x = 0; x < 30; x++) {
    const r = drawn.get(x * TILE + "," + y * TILE);
    expect(r && r.w >= TILE - 1 && r.h >= TILE - 1, `The tile at column ${x}, row ${y} is not drawn. It belongs at pixel x ${x * TILE}, y ${y * TILE}: fillRect(x * TILE, y * TILE, TILE, TILE), once for every character of every row.`);
    (map[y][x] === "#" ? wallFills : floorFills).add(r.fill);
  }
}
for (const f of wallFills) expect(!floorFills.has(f), "Walls and floor are drawn in the same colour. Set fillStyle by what the character is: '#' one colour, '.' another.");
""",
        hint="for (let y = 0; y < map.length; y++) for (let x = 0; x < map[y].length; x++) { ctx.fillStyle = map[y][x] === '#' ? '#4a5568' : '#2d3748'; ctx.fillRect(x * TILE, y * TILE, TILE, TILE); }",
    ),
    Step(
        id="dg-02-turns",
        track="Dungeon",
        title="One key press, one step",
        teaches=(
            "The player is two whole numbers - a column and a row - and is "
            "drawn like any other tile. Movement is turn-based: a key press "
            "is the unit of time, not a frame. So the keydown handler moves "
            "the player once, right there, and nothing in the frame loop "
            "moves anything. Holding a key makes the browser send keydown "
            "again and again with e.repeat set to true; ignore those, or "
            "holding ArrowRight would sprint across the dungeon instead of "
            "taking one step. A table from key name to { x, y } keeps the "
            "handler short."
        ),
        goal="Add let player = { x: 1, y: 1 } and draw it as a tile in its own colour. Each arrow key press moves the player one tile; holding a key (repeated keydown events, e.repeat) does not move it again.",
        starter=_P[1],
        solution=_P[2],
        check=_PRESS + """
expect(typeof player !== "undefined" && typeof player === "object" && player !== null, "Make an object called player: let player = { x: 1, y: 1 }; - a column and a row, in tiles.");
expect(player.x === 1 && player.y === 1, "The player starts at column 1, row 1.");
cc.frames(1);
const drawn = new Map();
for (const r of cc.rects()) drawn.set(r.x + "," + r.y, r);
let floorFill;
for (let y = 0; y < map.length && !floorFill; y++) {
  for (let x = 0; x < map[y].length; x++) {
    if (map[y][x] === "." && !(x === 1 && y === 1)) {
      floorFill = drawn.get(x * TILE + "," + y * TILE)?.fill;
      break;
    }
  }
}
const me = drawn.get(player.x * TILE + "," + player.y * TILE);
expect(me && me.fill !== floorFill, "Draw the player after the map, as a tile in a colour of its own: fillRect(player.x * TILE, player.y * TILE, TILE, TILE).");
press("ArrowRight");
expect(at() === "2,1", `ArrowRight should move the player one tile right, to column 2, row 1; it is at ${at()}. The player's x and y are in tiles, so add 1, not TILE.`);
press("ArrowDown");
expect(at() === "2,2", `ArrowDown should move the player one tile down, to column 2, row 2; it is at ${at()}. y grows downwards.`);
press("ArrowLeft");
expect(at() === "1,2", `ArrowLeft should move the player one tile left; it is at ${at()}.`);
press("ArrowUp");
expect(at() === "1,1", `ArrowUp should move the player one tile up; it is at ${at()}.`);
cc.frames(60);
expect(at() === "1,1", "The player moves on its own. In a turn-based game nothing happens until a key is pressed.");
cc.press("ArrowRight");
cc.frames(30);
cc.release("ArrowRight");
expect(at() === "2,1", `Holding ArrowRight for half a second left the player at ${at()}. A press is one step, however long the key stays down - do the step in the keydown handler, not once per frame.`);
for (let i = 0; i < 5; i++) document.dispatchEvent(new KeyboardEvent("keydown", { key: "ArrowDown", repeat: true, bubbles: true }));
expect(at() === "2,1", `Auto-repeated keydown events (the browser sends them while a key is held down, with e.repeat true) moved the player to ${at()}. Start the handler with: if (e.repeat) return;`);
""",
        hint="const KEYS = { ArrowUp: { x: 0, y: -1 }, ... }; addEventListener('keydown', (e) => { if (e.repeat) return; const d = KEYS[e.key]; if (d) { player.x += d.x; player.y += d.y; } });",
    ),
    Step(
        id="dg-03-walls",
        track="Dungeon",
        title="Walls stop you",
        teaches=(
            "Before the player steps, look at where the step would land: if "
            "that tile is a wall, the step does not happen. The question "
            "'is this tile a wall' is asked so often it earns a function, "
            "isWall(x, y). Make it say yes for anything off the map as "
            "well, and the edge needs no special case - but ask whether "
            "the tile is on the map BEFORE you read map[y][x], because "
            "map[-1] is undefined and undefined[x] is a crash. And mind the "
            "order again: map[y][x], never map[x][y]. A step into a wall "
            "does nothing at all - it is not a turn, which will matter "
            "when the monsters arrive."
        ),
        goal="Work out the tile the player would step onto, and only move there if it is on the map and is not a wall. Write inMap(x, y) and isWall(x, y) to ask.",
        starter=_P[2],
        solution=_P[3],
        check=_PRESS + _ARENA + """
const W = map[0].length;
const H = map.length;
arena([[10, 3]], false);
const tries = [
  ["ArrowRight", 9, 3, "right of"], ["ArrowLeft", 11, 3, "left of"],
  ["ArrowDown", 10, 2, "above"], ["ArrowUp", 10, 4, "below"],
];
for (const [key, x, y, where] of tries) {
  player.x = x;
  player.y = y;
  press(key);
  expect(at() === x + "," + y, `The player stood ${where} a wall tile and walked into it (it is at ${at()}). Look at the tile you would step onto, and stay put if it is '#'.`);
}
player.x = 3;
player.y = 10;
press("ArrowRight");
expect(at() === "4,10", `With a wall only at column 10, row 3, the player at column 3, row 10 should be free to step right - it is at ${at()}. Is the map read as map[y][x], row first?`);
player.x = 9;
player.y = 4;
press("ArrowRight");
expect(at() === "10,4", `The tile beside a wall (column 10, row 4) is open floor but the player was stopped. Check only the tile it is stepping onto.`);
arena([], false);
const corner = [
  [0, 0, "ArrowLeft"], [0, 0, "ArrowUp"], [W - 1, H - 1, "ArrowRight"], [W - 1, H - 1, "ArrowDown"],
  [W - 1, 0, "ArrowRight"], [W - 1, 0, "ArrowUp"], [0, H - 1, "ArrowLeft"], [0, H - 1, "ArrowDown"],
];
for (const [x, y, key] of corner) {
  player.x = x;
  player.y = y;
  press(key);
  expect(at() === x + "," + y, `At column ${x}, row ${y} the player walked off the edge of the map with ${key} (it is at ${at()}). Anything off the map counts as a wall - and check that before reading map[y][x].`);
}
player.x = 0;
player.y = 0;
press("ArrowRight");
press("ArrowDown");
expect(at() === "1,1", `Along the edge the player should still move freely; it is at ${at()}.`);
""",
        hint="function isWall(x, y) { return !inMap(x, y) || map[y][x] === '#'; }  and in move: if (isWall(x, y)) return;",
    ),
    Step(
        id="dg-04-camera",
        track="Dungeon",
        title="A camera that follows",
        teaches=(
            "Most dungeons are bigger than the screen. A camera is just "
            "the tile in the top-left corner of what you can see: camX and "
            "camY. Draw only the tiles from camX to camX + VIEW_W (and the "
            "same for rows) and put each one on screen at (x - camX) * "
            "TILE - subtract the camera from EVERY position you draw, the "
            "player included. To follow the player, put them in the middle "
            "of the view: camX = player.x - half the view. Then clamp, so "
            "near an edge the camera stops instead of showing the empty "
            "nothing beyond the map: between 0 and map width - VIEW_W. "
            "Zoom in to 32 pixel tiles and the 30 by 20 map no longer fits."
        ),
        goal="Make TILE 32 and add VIEW_W and VIEW_H (tiles that fit across and down the canvas), and let camX and camY. Each frame centre the camera on the player, clamped so it never leaves the map, and draw only the tiles in view at (x - camX) * TILE, (y - camY) * TILE.",
        starter=_P[3],
        solution=_P[4],
        check=_PRESS + _ARENA + _DRAWN + """
expect(typeof TILE !== "undefined" && TILE === 32, "Zoom in: const TILE = 32; - then a 480 by 320 canvas shows 15 by 10 tiles.");
expect(typeof VIEW_W === "number" && typeof VIEW_H === "number" && VIEW_W === 15 && VIEW_H === 10, "Add const VIEW_W = canvas.width / TILE and VIEW_H = canvas.height / TILE: how many tiles fit across and down (15 and 10).");
expect(typeof camX === "number" && typeof camY === "number", "Keep the camera in let camX and let camY - the tile at the top-left of the view.");
arena([], false);
const W = map[0].length;
const H = map.length;
const place = (x, y) => {
  player.x = x;
  player.y = y;
  cc.frames(1);
};
place(1, 1);
expect(camX === 0 && camY === 0, `Near the top-left corner the camera is at ${camX}, ${camY}; it should stop at 0, 0 rather than show what is beyond the map. Clamp it: Math.max(0, Math.min(map width - VIEW_W, ...)).`);
place(W - 2, H - 2);
expect(camX === W - VIEW_W && camY === H - VIEW_H, `Near the bottom-right corner the camera is at ${camX}, ${camY}; it should stop at ${W - VIEW_W}, ${H - VIEW_H} (the map's size minus the view's) so the map's edge sits at the edge of the screen.`);
place(Math.floor(W / 2), Math.floor(H / 2));
expect(Math.abs(player.x - camX - (VIEW_W - 1) / 2) <= 1, `In the middle of the map the player is at column ${player.x} and the camera's left edge at ${camX}: the player should be in the middle of the view, about ${(VIEW_W - 1) / 2} tiles in. camX = player.x - Math.floor(VIEW_W / 2).`);
expect(Math.abs(player.y - camY - (VIEW_H - 1) / 2) <= 1, `In the middle of the map the player is at row ${player.y} and the camera's top edge at ${camY}: the player should be in the middle of the view. camY = player.y - Math.floor(VIEW_H / 2).`);
arena([[player.x + 2, player.y]], false);
cc.frames(1);
const floorFill = tileFill(player.x - 2, player.y);
const wallFill = tileFill(player.x + 2, player.y);
const playerFill = tileFill(player.x, player.y);
expect(floorFill !== undefined && wallFill !== undefined && playerFill !== undefined, "A tile near the player is not drawn where the camera says it should be: draw tile (x, y) at ((x - camX) * TILE, (y - camY) * TILE) - for the map AND the player.");
expect(wallFill !== floorFill && playerFill !== floorFill, "The wall, the floor and the player should be three different colours.");
for (let y = camY; y < camY + VIEW_H; y++) {
  for (let x = camX; x < camX + VIEW_W; x++) {
    expect(tileFill(x, y) !== undefined, `The tile at column ${x}, row ${y} is in view but not drawn at ((x - camX) * TILE, (y - camY) * TILE).`);
  }
}
place(W - 2, H - 2);
press("ArrowLeft");
expect(camX <= W - VIEW_W && camX >= 0 && camY === H - VIEW_H, "The camera should keep following as the player moves.");
""",
        hint="camX = clamp(player.x - Math.floor(VIEW_W / 2), 0, map[0].length - VIEW_W); and draw with (x - camX) * TILE.",
    ),
    Step(
        id="dg-05-rooms",
        track="Dungeon",
        title="Rooms, placed at random",
        teaches=(
            "A dungeon built by hand is the same dungeon every time. A "
            "generator builds a new one: start with a map that is all wall, "
            "then try to place rooms. Pick a random size and position; if "
            "the new room overlaps one already placed, throw it away and "
            "try again; otherwise carve it out, turning its tiles into "
            "floor. Stop after a fixed number of tries, not when you have "
            "'enough' rooms, so a bad run cannot loop for ever. Build the "
            "map as a grid of arrays - strings cannot be changed in place "
            "- and join each row into a string at the end. Keep a wall "
            "round the edge: a room's x runs from 1 to MAP_W - w - 1. "
            "Math.random here is seeded by Code Coach, so the same game is "
            "replayed every time you press Check."
        ),
        goal="Replace the hand-made map with function generate(): it sets map (a MAP_W by MAP_H grid, 50 by 30, as strings) and rooms (each { x, y, w, h }, at least 3, none overlapping, none touching the edge) by trying rooms at random, and puts the player in the centre of rooms[0]. Call it once to start.",
        starter=_P[4],
        solution=_P[5],
        check=_PRESS + _LEVELS + """
expect(typeof generate === "function", "Write function generate() that builds a whole level and is called once at the start.");
expect(typeof MAP_W === "number" && typeof MAP_H === "number" && MAP_W === 50 && MAP_H === 30, "Add const MAP_W = 50; and const MAP_H = 30; - the size of the dungeon in tiles.");
expect(Array.isArray(rooms), "Keep the rooms in let rooms = [] - each one { x, y, w, h }: the top-left tile and the size in tiles.");
for (let s = 1; s <= 30; s++) {
  seed(s * 7919);
  generate();
  expect(Array.isArray(map) && map.length === MAP_H && map.every((row) => typeof row === "string" && row.length === MAP_W), "After generate(), map should be MAP_H strings of MAP_W characters each.");
  checkRooms("Level " + s);
  expect(inRoom(player, rooms[0]) && map[player.y][player.x] === ".", `Level ${s}: the player is at column ${player.x}, row ${player.y}, not inside the first room. Put the player in the centre of rooms[0].`);
}
cc.frames(1);
""",
        hint="Loop 60 tries: pick w, h, x, y; if (rooms.some((r) => intersects(room, r))) continue; rooms.push(room); then set its tiles in grid to '.'. At the end map = grid.map((row) => row.join(''));",
    ),
    Step(
        id="dg-06-corridors",
        track="Dungeon",
        title="Corridors join the rooms",
        teaches=(
            "Rooms alone are islands. Join them with corridors, and the "
            "simplest scheme that always works is to dig from the centre "
            "of each room to the centre of the one before it: along a "
            "row to the right column, then along that column to the other "
            "room. Every room is linked to the previous one, so every room "
            "is linked to every other - the whole level is one piece. Dig "
            "with Math.min and Math.max so it does not matter which end "
            "is left or above. A corridor that passes through a room "
            "changes nothing; it is floor already."
        ),
        goal="After placing the rooms, dig a corridor from the centre of each room to the centre of the previous one: a horizontal stretch then a vertical one, turning tiles to floor. Every floor tile on the map must be reachable from every other.",
        starter=_P[5],
        solution=_P[6],
        check=_PRESS + _LEVELS + """
expect(typeof generate === "function" && Array.isArray(rooms), "Keep generate() and rooms from the last step.");
for (let s = 1; s <= 30; s++) {
  seed(s * 104729);
  generate();
  checkRooms("Level " + s);
  const all = floors();
  const got = reach(player.x, player.y);
  expect(got.size === all.length, `Level ${s}: ${all.length - got.size} of the ${all.length} floor tiles cannot be reached from the player - some rooms are cut off from the rest. Join every room to the one before it.`);
  expect(all.length > rooms.reduce((n, r) => n + r.w * r.h, 0), `Level ${s}: there is no floor outside the rooms - dig corridors between them.`);
}
cc.frames(1);
""",
        hint="for (let i = 1; i < rooms.length; i++) tunnel(grid, center(rooms[i - 1]), center(rooms[i]));  where tunnel digs a row of '.' then a column of '.'",
    ),
    Step(
        id="dg-07-stairs",
        track="Dungeon",
        title="Stairs down",
        teaches=(
            "A level needs a way out. Put the stairs in a different room "
            "from the player - the last room in the list is easy to "
            "pick, and rooms[0] and the last are different rooms as long "
            "as there are two. When the player steps onto them, the "
            "dungeon gets deeper: add 1 to depth and call generate() "
            "again. That one call is the whole new level, because "
            "generate() builds everything from nothing - which is why it "
            "is worth keeping every piece of a level inside it. Show the "
            "depth as text, so you can see you are getting somewhere."
        ),
        goal="Add let stairs and let depth = 1. generate() puts the stairs on the centre of a room that is not the player's. Draw them in their own colour, and show 'Depth: 1' as text. Stepping onto the stairs adds 1 to depth and generates a new level.",
        starter=_P[6],
        solution=_P[7],
        check=_PRESS + _LEVELS + _DRAWN + """
expect(typeof stairs === "object" && stairs !== null && typeof depth === "number", "Add let stairs = { x, y } and let depth = 1.");
expect(depth === 1, "A game starts at depth 1.");
const sound = (tag) => {
  expect(Number.isInteger(stairs.x) && Number.isInteger(stairs.y) && map[stairs.y][stairs.x] === ".", `${tag}: the stairs are at column ${stairs.x}, row ${stairs.y}, which is not a floor tile.`);
  expect(roomOf(stairs) !== -1, `${tag}: the stairs are not inside a room.`);
  expect(roomOf(stairs) !== roomOf(player), `${tag}: the stairs are in the same room as the player. Put them in a different room - the last one in the list.`);
  expect(!(stairs.x === player.x && stairs.y === player.y), `${tag}: the player starts on the stairs.`);
};
for (let s = 1; s <= 20; s++) {
  seed(s * 3331);
  generate();
  sound("Level " + s);
}
const dirs = [["ArrowRight", 1, 0], ["ArrowLeft", -1, 0], ["ArrowDown", 0, 1], ["ArrowUp", 0, -1]];
const besideStairs = () => {
  for (const [key, dx, dy] of dirs) {
    const nx = stairs.x - dx;
    const ny = stairs.y - dy;
    if (map[ny][nx] === ".") {
      player.x = nx;
      player.y = ny;
      return key;
    }
  }
  throw new Error("no floor beside the stairs");
};
seed(4242);
generate();
depth = 1;
const key = besideStairs();
cc.frames(1);
const floorFill = (() => {
  for (let y = camY; y < camY + VIEW_H; y++) {
    for (let x = camX; x < camX + VIEW_W; x++) {
      if (map[y][x] === "." && !(x === player.x && y === player.y) && !(x === stairs.x && y === stairs.y)) return tileFill(x, y);
    }
  }
})();
expect(tileFill(stairs.x, stairs.y) !== undefined && tileFill(stairs.x, stairs.y) !== floorFill, "Draw the stairs as a tile in a colour of their own, after the map.");
expect(cc.texts().some((t) => /depth/i.test(t) && t.includes("1")), "Write the depth on the screen: 'Depth: 1'.");
for (const [k, dx, dy] of dirs) {
  const tx = player.x + dx;
  const ty = player.y + dy;
  if (map[ty][tx] === "." && !(tx === stairs.x && ty === stairs.y)) {
    const before = map.join("|");
    press(k);
    expect(depth === 1 && map.join("|") === before, "Stepping somewhere that is not the stairs changed the level. Only the stairs go down.");
    break;
  }
}
const before = map.join("|");
besideStairs();
press(key);
expect(depth === 2, `The player stepped onto the stairs and depth is ${depth}; it should be 2.`);
expect(map.join("|") !== before, "Depth went up but the level is the same. Call generate() as well, to build a new one.");
checkRooms("The new level");
sound("The new level");
expect(inRoom(player, rooms[0]), "On a new level the player should start in its first room, not where the stairs were.");
cc.frames(1);
expect(cc.texts().some((t) => /depth/i.test(t) && t.includes("2")), "The depth on the screen should now say 2.");
""",
        hint="In generate: const end = center(rooms[rooms.length - 1]); stairs = { x: end.x, y: end.y };  In move: if (x === stairs.x && y === stairs.y) { depth += 1; generate(); }",
    ),
    Step(
        id="dg-08-enemies",
        track="Dungeon",
        title="The monsters take their turn",
        teaches=(
            "In a roguelike the world waits for you. Nothing else moves "
            "until the player does something that takes a turn - and "
            "then each enemy takes exactly one turn too. That is the "
            "whole trick: put 'everyone else's turn' in one function "
            "(endTurn) and call it at the end of the player's move. Two "
            "details decide whether it feels fair. A step into a wall is "
            "not a turn, so it must return before endTurn. And the enemies "
            "move after the player, so they react to where you ARE. To "
            "chase, move one tile along whichever axis is further away, "
            "and if a wall is in the way try the other axis. They stop "
            "next to you - the player's tile is not theirs to step on."
        ),
        goal="Add let enemies, an array of { x, y }: generate() puts one on a random tile of every room except the first (never on the stairs), and they are drawn in their own colour. After every step the player takes, each enemy moves one tile (up, down, left or right) toward the player, never into a wall or onto the player. A step into a wall is not a turn.",
        starter=_P[7],
        solution=_P[8],
        check=_PRESS + _ARENA + _LEVELS + _DRAWN + """
expect(typeof enemies !== "undefined" && Array.isArray(enemies), "Add let enemies = [] - each enemy is { x, y }.");
for (let s = 1; s <= 20; s++) {
  seed(s * 6151);
  generate();
  expect(enemies.length >= 1, `Level ${s} has no enemies. Put one on a random tile of every room except the player's.`);
  for (const e of enemies) {
    expect(Number.isInteger(e.x) && Number.isInteger(e.y) && map[e.y][e.x] === ".", `Level ${s}: an enemy at column ${e.x}, row ${e.y} is not on a floor tile.`);
    expect(!inRoom(e, rooms[0]), `Level ${s}: an enemy starts in the player's own room - leave the first room empty.`);
    expect(!(e.x === stairs.x && e.y === stairs.y), `Level ${s}: an enemy starts on the stairs.`);
  }
}
const setup = (px, py, list, walls) => {
  arena(walls || [], true);
  player.x = px;
  player.y = py;
  enemies = list.map((c) => ({ x: c[0], y: c[1] }));
};
const dist = (e) => Math.abs(e.x - player.x) + Math.abs(e.y - player.y);
setup(10, 10, [[15, 10]]);
press("ArrowUp");
expect(at() === "10,9", `The player should have stepped up to column 10, row 9; it is at ${at()}.`);
let e = enemies[0];
expect(Math.abs(e.x - 15) + Math.abs(e.y - 10) === 1, `After the player's step the enemy should have moved exactly one tile - up, down, left or right. It was at column 15, row 10 and is at ${e.x}, ${e.y}.`);
expect(dist(e) === 5, `The enemy should have moved toward the player (distance 6 before its move, 5 after) but it is ${dist(e)} away.`);
setup(10, 10, [[15, 10]]);
cc.frames(120);
expect(enemies[0].x === 15 && enemies[0].y === 10, "The enemy moved while the player did nothing. In a turn-based game they only move after the player does.");
setup(1, 10, [[6, 10]]);
press("ArrowLeft");
expect(at() === "1,10" && enemies[0].x === 6 && enemies[0].y === 10, "The player walked into a wall, which is not a turn - but the enemy moved. Return from the move before the enemies act.");
setup(10, 10, [[15, 12]], [[11, 10]]);
press("ArrowRight");
expect(at() === "10,10" && enemies[0].x === 15 && enemies[0].y === 12, "Bumping into an inner wall is not a turn either - the enemy moved.");
setup(10, 10, [[12, 10]]);
press("ArrowRight");
expect(at() === "11,10", `The player should have stepped right to column 11; it is at ${at()}.`);
e = enemies[0];
expect(e.x === 12 && e.y === 10, `The enemy was two tiles away and the player stepped toward it. It should wait next to the player at column 12, row 10; it is at ${e.x}, ${e.y}. Enemies move AFTER the player, and never onto the player's tile.`);
setup(5, 5, [[20, 12]]);
for (let i = 0; i < 60 && dist(enemies[0]) > 3; i++) {
  press(i % 2 === 0 ? "ArrowRight" : "ArrowLeft");
  e = enemies[0];
  expect(map[e.y][e.x] === ".", `Turn ${i + 1}: the enemy is on column ${e.x}, row ${e.y}, which is not floor.`);
  expect(!(e.x === player.x && e.y === player.y), `Turn ${i + 1}: the enemy is on the player's tile.`);
}
expect(dist(enemies[0]) <= 3, `After 60 turns the enemy is still ${dist(enemies[0])} tiles from the player, who barely moved. It should have walked right up.`);
const column = [];
for (let y = 6; y <= 14; y++) column.push([12, y]);
setup(8, 10, [[16, 10], [16, 12]], column);
for (let i = 0; i < 60; i++) {
  press(i % 2 === 0 ? "ArrowUp" : "ArrowDown");
  for (const en of enemies) {
    expect(map[en.y] !== undefined && map[en.y][en.x] === ".", `Turn ${i + 1}: an enemy walked into column ${en.x}, row ${en.y}, which is a wall or off the map. Enemies are blocked by walls: test the tile before stepping.`);
    expect(!(en.x === player.x && en.y === player.y), `Turn ${i + 1}: an enemy is on the player's tile.`);
  }
}
setup(10, 10, [[12, 10]]);
cc.frames(1);
const foe = tileFill(12, 10);
expect(foe !== undefined && foe !== tileFill(11, 10) && foe !== tileFill(13, 10), "Draw each enemy as a tile in a colour of its own, after the map.");
""",
        hint="In endTurn(): for each enemy, dx = player.x - e.x, dy = player.y - e.y; try the axis with the larger distance first; step only if !isWall(x, y) and it is not the player's tile. Call endTurn() last in move().",
    ),
    Step(
        id="dg-09-bump",
        track="Dungeon",
        title="Bump to attack",
        teaches=(
            "Roguelikes have no attack button: you fight by walking into "
            "the enemy. In move(), before stepping, look for an enemy on "
            "the tile you are heading for. If there is one, you hit it "
            "instead of moving: subtract the damage from its hp, and if "
            "that leaves 0 or less, take it out of the array - a dead "
            "enemy left in the list keeps chasing and hitting you. A "
            "bump is a turn, so the enemies respond; and an enemy "
            "already next to you does not need to move any more, it hits. "
            "Keep the numbers - 2 damage from you, 1 from them, 4 hp and "
            "10 hp - as named constants so tuning the game is one edit."
        ),
        goal="Give enemies hp: 4 and the player hp: 10, maxHp: 10; add PLAYER_DAMAGE = 2 and ENEMY_DAMAGE = 1. Walking into an enemy hits it instead of moving (and takes a turn); at 0 hp it is removed. An enemy next to the player hits instead of moving. Show 'HP: 10/10' as text.",
        starter=_P[8],
        solution=_P[9],
        check=_PRESS + _ARENA + _LEVELS + """
expect(typeof PLAYER_DAMAGE === "number" && typeof ENEMY_DAMAGE === "number" && PLAYER_DAMAGE === 2 && ENEMY_DAMAGE === 1, "Add const PLAYER_DAMAGE = 2; and const ENEMY_DAMAGE = 1;");
expect(player.hp === 10 && player.maxHp === 10, "The player has hp: 10 and maxHp: 10: let player = { x: 1, y: 1, hp: 10, maxHp: 10 };");
seed(5);
generate();
expect(enemies.length >= 1 && enemies.every((en) => en.hp === 4), "Every enemy should be created with hp: 4.");
const setup = (list, hp) => {
  arena([], true);
  player.x = 10;
  player.y = 10;
  player.hp = hp;
  enemies = list.map((c) => ({ x: c[0], y: c[1], hp: 4 }));
};
setup([[11, 10]], 10);
press("ArrowRight");
expect(at() === "10,10", `Walking into an enemy should hit it, not move onto it; the player is at ${at()}.`);
expect(enemies.length === 1 && enemies[0].hp === 2, `One hit does 2 damage: an enemy with 4 hp should have 2 left. ${enemies.length ? "It has " + enemies[0].hp + "." : "It is gone."}`);
expect(player.hp === 9, `Hitting an enemy is a turn, and the enemy next to the player hits back for 1: hp should be 9; it is ${player.hp}.`);
press("ArrowRight");
expect(enemies.length === 0, `The second hit leaves the enemy at 0 hp, and it should be removed from enemies; the list still has ${enemies.length}. enemies = enemies.filter((e) => e !== target).`);
expect(player.hp === 9, `A dead enemy should not hit back, but the player's hp is ${player.hp}.`);
expect(at() === "10,10", "Killing an enemy should not move the player into its tile on the same step.");
press("ArrowRight");
expect(at() === "11,10", `With the enemy gone, the way is clear: the player should step to column 11; it is at ${at()}.`);
setup([[15, 10]], 10);
press("ArrowUp");
expect(player.hp === 10, `An enemy five tiles away hurt the player (hp is ${player.hp}). Only an enemy next to the player attacks.`);
setup([[12, 10]], 10);
press("ArrowDown");
expect(player.hp === 10, `An enemy two tiles away hurt the player (hp is ${player.hp}). It should step closer; it attacks on a later turn.`);
setup([[11, 10], [10, 9]], 10);
press("ArrowRight");
expect(player.hp === 8, `Two enemies are next to the player and each should hit once per turn: hp 10 should be 8; it is ${player.hp}.`);
setup([[11, 10]], 10);
cc.frames(1);
expect(cc.texts().some((t) => /hp/i.test(t) && t.includes("10")), "Show the player's health as text, like 'HP: 10/10'.");
player.hp = 4;
cc.frames(1);
expect(cc.texts().some((t) => /hp/i.test(t) && t.includes("4")), "The health on the screen should follow player.hp.");
""",
        hint="In move(): const target = enemyAt(x, y); if (target) { target.hp -= PLAYER_DAMAGE; if (target.hp <= 0) enemies = enemies.filter((e) => e !== target); endTurn(); return; }",
    ),
    Step(
        id="dg-10-fog",
        track="Dungeon",
        title="Fog of war",
        teaches=(
            "A dungeon you can see all of has no mystery. Fog of war keeps "
            "two things: what you can see RIGHT NOW (a pure function of "
            "where you stand) and what you have SEEN (a memory that only "
            "grows). A tile is visible if it is within RADIUS tiles - "
            "dx * dx + dy * dy <= RADIUS * RADIUS, no square root needed - "
            "and no wall is in the way. To test that, walk along the line "
            "from the player to the tile and give up at the first wall. "
            "After every turn add the visible tiles to a Set of 'x,y' "
            "keys. Draw visible tiles bright, remembered ones dimmer, and "
            "the rest not at all; monsters only show while in sight."
        ),
        goal="Add const RADIUS = 6, let seen = new Set(), visible(x, y) (within RADIUS and no wall in the line between) and updateFog() (adds every visible tile as the string x + ',' + y). Update it after each turn and when a level is generated (starting from an empty set). Draw visible tiles bright, seen ones in a darker colour (set fillStyle - not globalAlpha), unseen ones not at all.",
        starter=_P[9],
        solution=_P[10],
        check=_PRESS + _ARENA + _LEVELS + _DRAWN + """
expect(typeof visible === "function" && typeof updateFog === "function", "Write function visible(x, y) and function updateFog().");
expect(typeof RADIUS === "number" && RADIUS === 6, "Add const RADIUS = 6;");
expect(typeof seen !== "undefined" && seen instanceof Set, "Keep what the player has seen in let seen = new Set() - one 'x,y' string for each tile.");
const setup = (px, py, walls) => {
  arena(walls || [], true);
  player.x = px;
  player.y = py;
  enemies = [];
  seen = new Set();
  updateFog();
};
setup(10, 10);
for (const [x, y] of [[10, 10], [12, 10], [10, 12], [8, 9], [10, 14], [7, 10]]) {
  expect(visible(x, y) === true, `The tile at column ${x}, row ${y} is a few tiles from the player in an empty room and should be visible. A tile is visible when dx * dx + dy * dy <= RADIUS * RADIUS.`);
}
for (const [x, y] of [[20, 10], [10, 19], [30, 10], [1, 1], [10, 25]]) {
  expect(visible(x, y) === false, `The tile at column ${x}, row ${y} is far from the player (more than RADIUS tiles) and should not be visible - the fog is not doing anything.`);
}
expect(seen.has("10,10") && seen.has("12,10") && seen.has("10,14"), "updateFog() should add the visible tiles to seen as 'x,y' strings - e.g. '10,10'.");
expect(!seen.has("20,10") && seen.size < 200, "updateFog() added tiles that are far away. Only what is visible goes into seen.");
setup(10, 10, [[13, 10]]);
expect(visible(12, 10) === true && visible(13, 10) === true, "You can see right up to a wall, and the wall itself.");
expect(visible(15, 10) === false && visible(16, 10) === false, "A tile behind a wall is hidden: walls block sight. Walk the line from the player to the tile, and stop at the first wall.");
expect(visible(10, 14) === true && visible(10, 6) === true, "A wall to the east should not hide tiles to the north and south.");
setup(5, 10);
for (let i = 0; i < 12; i++) press("ArrowRight");
expect(at() === "17,10", `The player should have walked to column 17; it is at ${at()}.`);
expect(seen.has("22,10"), "The fog should lift as the player walks: after each turn, call updateFog() so what is now visible is added to seen.");
expect(seen.has("5,10") && seen.has("8,10") && !visible(5, 10), "Tiles the player has walked away from should stay in seen - the map is remembered.");
expect(!seen.has("30,10") && !seen.has("40,10") && seen.size < map.length * map[0].length / 2, "Most of the map should still be unseen.");
setup(5, 5);
cc.frames(1);
const nearFloor = tileFill(6, 5);
const nearWall = tileFill(0, 5);
expect(nearFloor !== undefined && nearWall !== undefined && nearFloor !== nearWall, "Visible tiles are drawn in colours - the floor and the wall different - at (x - camX) * TILE.");
const far = tileFill(14, 8);
expect(far === undefined || (far !== nearFloor && far !== nearWall), "A tile the player has never seen is drawn like one in plain sight. Draw only what is visible, or seen before.");
player.x = 13;
updateFog();
cc.frames(1);
const remembered = tileFill(6, 5);
expect(remembered !== undefined, "A tile seen earlier but out of sight now should still be drawn, as a memory.");
expect(remembered !== nearFloor, "Remembered tiles should look different from visible ones: draw them in a darker colour (a different fillStyle).");
for (let s = 1; s <= 3; s++) {
  seed(s * 211);
  for (let i = 0; i < 600; i++) seen.add("stale" + i);
  generate();
  expect(seen.size < 200 && seen.has(player.x + "," + player.y), "A new level should start with a fresh fog: seen = new Set(), then updateFog() once the player is placed.");
}
""",
        hint="function visible(x, y) { ... if (dx * dx + dy * dy > RADIUS * RADIUS) return false; then step along the line with Math.round and return false at a wall ... }",
    ),
    Step(
        id="dg-11-potions",
        track="Dungeon",
        title="Potions",
        teaches=(
            "Items are the same idea as enemies without the brain: an "
            "array of { x, y }, spawned by generate(), drawn, and "
            "collected by walking onto them - find the one under the player "
            "and take it out of the list. What you hold is not an object "
            "yet, just a count: let potions = 0, shown as text. Drinking "
            "(press H) spends one, heals by 5, and takes a turn - but "
            "clamp the healing: Math.min(player.maxHp, player.hp + 5), or "
            "hp climbs past the maximum. And with no potions, H does "
            "nothing at all: no healing, no negative count, no turn."
        ),
        goal="Add let items (array of { x, y }), let potions = 0. generate() scatters potions on floor tiles of the rooms but not the first; they are drawn (while visible) in their own colour. Walking onto one picks it up: it leaves items and potions goes up by 1. Pressing h drinks one: hp goes up by 5, never past maxHp, and it takes a turn; with none left, h does nothing. Show 'Potions: N' as text.",
        starter=_P[10],
        solution=_P[11],
        check=_PRESS + _ARENA + _LEVELS + _DRAWN + """
expect(typeof items !== "undefined" && Array.isArray(items) && typeof potions === "number", "Add let items = [] (each { x, y }) and let potions = 0.");
for (let s = 1; s <= 20; s++) {
  seed(s * 977);
  generate();
  expect(items.length >= 1, `Level ${s} has no potions. Scatter a few on random tiles of the rooms.`);
  for (const it of items) {
    expect(Number.isInteger(it.x) && Number.isInteger(it.y) && map[it.y][it.x] === ".", `Level ${s}: a potion at column ${it.x}, row ${it.y} is not on a floor tile.`);
    expect(!(it.x === player.x && it.y === player.y), `Level ${s}: a potion is under the player at the start.`);
  }
}
const setup = (list, hp, count, foes) => {
  arena([], true);
  player.x = 10;
  player.y = 10;
  player.hp = hp;
  enemies = (foes || []).map((c) => ({ x: c[0], y: c[1], hp: 4 }));
  items = list.map((c) => ({ x: c[0], y: c[1] }));
  potions = count;
  seen = new Set();
  updateFog();
};
setup([[11, 10]], 10, 0);
press("ArrowRight");
expect(items.length === 0, "The player stepped onto a potion and it is still in items. Pick it up: take it out of the list.");
expect(potions === 1, `Picking up a potion should make potions 1; it is ${potions}.`);
setup([[15, 10]], 10, 0);
press("ArrowUp");
expect(items.length === 1 && potions === 0, "A potion the player has not walked onto was picked up.");
setup([], 3, 2);
press("h");
expect(player.hp === 8 && potions === 1, `Drinking at 3 hp should heal 5 (to 8) and use one potion (1 left); hp is ${player.hp}, potions ${potions}.`);
press("h");
expect(player.hp === 10, `Drinking at 8 hp should stop at the maximum, 10 - not climb to ${player.hp}. Math.min(player.maxHp, player.hp + 5).`);
expect(potions === 0, `Both potions are drunk; potions is ${potions}.`);
player.hp = 5;
press("h");
expect(player.hp === 5 && potions === 0, `With no potions, h should do nothing; hp is ${player.hp} and potions ${potions}.`);
setup([], 5, 1, [[15, 10]]);
press("h");
expect(enemies[0].x !== 15 || enemies[0].y !== 10, "Drinking a potion is a turn: the enemy should have moved.");
setup([], 5, 0, [[15, 10]]);
press("h");
expect(enemies[0].x === 15 && enemies[0].y === 10, "With no potion to drink, h is not a turn - the enemy moved.");
setup([], 5, 3);
cc.frames(1);
expect(cc.texts().some((t) => /potion/i.test(t) && t.includes("3")), "Show the potions you carry as text, like 'Potions: 3'.");
setup([[12, 10]], 10, 0);
cc.frames(1);
const potionFill = tileFill(12, 10);
expect(potionFill !== undefined && potionFill !== tileFill(11, 10) && potionFill !== tileFill(13, 10), "Draw each potion (while it is in sight) as a tile in a colour of its own, after the map.");
""",
        hint="function pickUp() { const found = items.find((i) => i.x === player.x && i.y === player.y); if (!found) return; items = items.filter((i) => i !== found); potions += 1; }",
    ),
    Step(
        id="dg-12-gameover",
        track="Dungeon",
        title="Game over, and again",
        teaches=(
            "You will die, so the game needs an ending and a way back. "
            "state is 'playing' or 'over'; when hp reaches 0 it becomes "
            "'over', the screen says so, and the game stops listening to "
            "everything except Enter. Restarting means undoing "
            "everything that changed over a run: depth back to 1, hp back "
            "to full, no potions, state back to 'playing', and a new level - "
            "and because generate() builds a whole level (rooms, stairs, "
            "enemies, items, fog) one call does most of it. Check hp at "
            "the end of the turn, after the enemies have acted. Enter must "
            "do nothing in the middle of a game."
        ),
        goal="Add let state = 'playing'. When the player's hp reaches 0 at the end of a turn, state becomes 'over' and the screen says 'Game over'. While it is over, only Enter does anything: it starts again at depth 1 with full hp and no potions on a new level.",
        starter=_P[11],
        solution=_P[12],
        check=_PRESS + _ARENA + _LEVELS + """
expect(typeof state === "string" && state === "playing", "Keep what the game is doing in let state = 'playing';");
const setup = (hp) => {
  arena([], true);
  player.x = 10;
  player.y = 10;
  player.hp = hp;
  enemies = [{ x: 11, y: 10, hp: 4 }];
  items = [];
  potions = 2;
  depth = 3;
  seen = new Set();
  updateFog();
};
setup(5);
press("ArrowRight");
expect(state === "playing", `The player is at ${player.hp} hp and the game is '${state}' - it should go on.`);
setup(1);
press("ArrowRight");
expect(player.hp <= 0, `The enemy should have hit the player down to ${player.hp}.`);
expect(state === "over", `The player is at ${player.hp} hp and state is '${state}'. At the end of the turn, if hp <= 0 then state = 'over'.`);
cc.frames(1);
expect(cc.texts().some((t) => /game over/i.test(t)), "When the game is over, write 'Game over' on the screen.");
const frozen = at() + "|" + JSON.stringify(enemies) + "|" + potions + "|" + depth;
press("ArrowLeft");
press("ArrowUp");
press("h");
cc.frames(30);
expect(at() + "|" + JSON.stringify(enemies) + "|" + potions + "|" + depth === frozen, "After game over the dungeon should be frozen: the arrow keys and h do nothing.");
press("Enter");
expect(state === "playing", `Enter after game over should start a new game; state is '${state}'.`);
expect(player.hp === player.maxHp, `A new game starts at full health (${player.maxHp}); hp is ${player.hp}.`);
expect(depth === 1, `A new game starts at depth 1; depth is ${depth}.`);
expect(potions === 0, `A new game starts with no potions; potions is ${potions}.`);
expect(map.join("|").includes("#") && rooms.length >= 3 && inRoom(player, rooms[0]), "A new game needs a new level: call generate().");
expect(!enemies.some((e) => e.hp === 2), "The old enemies are still there. A restart builds the whole level again.");
cc.frames(1);
expect(!cc.texts().some((t) => /game over/i.test(t)), "'Game over' is still on the screen after the restart.");
depth = 2;
const level = map.join("|");
press("Enter");
expect(depth === 2 && map.join("|") === level && state === "playing", "Enter in the middle of a game restarted it. Only restart when state is 'over'.");
""",
        hint="In endTurn(): if (player.hp <= 0) state = 'over';  In keydown: if (state === 'over') { if (e.key === 'Enter') restart(); return; }",
    ),
    Step(
        id="dg-13-yours",
        track="Dungeon",
        title="Now it's yours",
        teaches=(
            "A whole roguelike: a map of tiles, a turn instead of a clock, "
            "a generator, enemies that chase, fog, items, and an ending. "
            "Ideas, easiest first: enemies that start sleeping and wake "
            "when you are within five tiles; WASD as well as the arrows; "
            "a message line ('You hit the goblin'); enemies that get "
            "tougher with depth; a second kind of monster; a sword that "
            "raises PLAYER_DAMAGE; waiting a turn with the space bar; "
            "a minimap; rooms joined by corridors that can bend; a "
            "high score of the deepest level reached, kept in localStorage."
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_P[12],
        solution=_P[12],
        check="",
    ),
)
