"""A Canvas track after Asteroids: Tower defense.

The other games had one thing moving under your hands. Here nothing is: the
creeps walk a road on their own, and you only decide where towers go. That
asks for new things - a path that is data (a list of waypoints) rather than
a drawing; a walker that turns corners without losing speed or jittering;
the mouse turned into a tile (page pixels to canvas pixels to a column and a
row) and a tile that may or may not be built on; a range that is a circle; a
rule for choosing among several targets; a reload counted in seconds; shots
that home on a target that may die on the way; money with one door in and
one door out; waves as a list and a small state machine; and lives.

Same rules as the others: each step's starter is the step before, finished;
a check plays the program (frames stepped, clicks dispatched on the canvas)
and never reads it. The checks build their own situations by writing into
the top-level names the goals list (creeps, towers, shots, money, lives,
wave, state...), and run the key ones at 30 frames a second as well as 60.
"""

from __future__ import annotations

from code_coach.canvas.content import Step


def _edit(code: str, old: str, new: str) -> str:
    """One change to a program; the text it replaces must be there exactly once."""
    assert code.count(old) == 1, old
    return code.replace(old, new)


# ── The programs, each one the step before plus one change ───────────────
_P0 = """const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');

function update(dt) {
}

function draw() {
  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
}

let last = 0;
function loop(time) {
  const dt = (time - last) / 1000;
  last = time;
  update(dt);
  draw();
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
"""

# 1. The path.
_P1 = _edit(_P0, "function update(dt) {\n", """const TILE = 40;

// The road, as the centre of each tile it turns at: column * TILE + TILE / 2.
const path = [
  { x: 20, y: 60 },
  { x: 380, y: 60 },
  { x: 380, y: 220 },
  { x: 140, y: 220 },
  { x: 140, y: 300 },
];

function update(dt) {
""")
_P1 = _edit(_P1, "function draw() {\n", """function drawPath() {
  ctx.strokeStyle = '#3b4252';
  ctx.lineWidth = TILE;
  ctx.lineCap = 'square';
  ctx.beginPath();
  ctx.moveTo(path[0].x, path[0].y);
  for (const p of path.slice(1)) ctx.lineTo(p.x, p.y);
  ctx.stroke();
}

function draw() {
""")
_P1 = _edit(
    _P1,
    "  ctx.fillRect(0, 0, canvas.width, canvas.height);\n",
    "  ctx.fillRect(0, 0, canvas.width, canvas.height);\n  drawPath();\n",
)

# 2. A creep walks the path.
_P2 = _edit(_P1, "function update(dt) {\n", """function makeCreep() {
  return { x: path[0].x, y: path[0].y, next: 1, dist: 0, speed: 80 };
}

let creeps = [makeCreep()];

// Walk speed * dt pixels along the path, turning each corner on the way.
function moveCreep(c, dt) {
  let left = c.speed * dt;
  while (left > 0 && c.next < path.length) {
    const p = path[c.next];
    const d = Math.hypot(p.x - c.x, p.y - c.y);
    if (d <= left) {
      c.x = p.x;
      c.y = p.y;
      c.next++;
      c.dist += d;
      left -= d;
    } else {
      c.x += ((p.x - c.x) / d) * left;
      c.y += ((p.y - c.y) / d) * left;
      c.dist += left;
      left = 0;
    }
  }
}

function update(dt) {
  for (const c of creeps) moveCreep(c, dt);
  creeps = creeps.filter((c) => c.next < path.length);
""")
_P2 = _edit(_P2, "function draw() {\n", """function drawCreep(c) {
  ctx.fillStyle = '#f6ad55';
  ctx.beginPath();
  ctx.arc(c.x, c.y, 12, 0, Math.PI * 2);
  ctx.fill();
}

function draw() {
""")
_P2 = _edit(_P2, "  drawPath();\n}", "  drawPath();\n  for (const c of creeps) drawCreep(c);\n}")

# 3. Health bars; the dead leave.
_P3 = _edit(
    _P2,
    "function makeCreep() {\n  return { x: path[0].x, y: path[0].y, next: 1, dist: 0, speed: 80 };\n}",
    "function makeCreep(hp = 10) {\n"
    "  return { x: path[0].x, y: path[0].y, next: 1, dist: 0, speed: 80, hp, maxHp: hp };\n}",
)
_P3 = _edit(
    _P3,
    "creeps = creeps.filter((c) => c.next < path.length);",
    "creeps = creeps.filter((c) => c.hp > 0 && c.next < path.length);",
)
_P3 = _edit(_P3, "function drawCreep(c) {", "const BAR_W = 24;\n\nfunction drawCreep(c) {")
_P3 = _edit(_P3, "  ctx.fill();\n}\n", """  ctx.fill();
  const x = c.x - BAR_W / 2;
  ctx.fillStyle = '#742a2a';
  ctx.fillRect(x, c.y - 24, BAR_W, 4);
  ctx.fillStyle = '#68d391';
  ctx.fillRect(x, c.y - 24, (BAR_W * Math.max(0, c.hp)) / c.maxHp, 4);
}
""")

# 4. Creeps come on a timer.
_P4 = _edit(_P3, "let creeps = [makeCreep()];\n", """let creeps = [];

const SPAWN_EVERY = 1.5;
let spawnTimer = 0;

function spawnCreep() {
  creeps.push(makeCreep());
}
""")
_P4 = _edit(_P4, "function update(dt) {\n", """function update(dt) {
  spawnTimer += dt;
  if (spawnTimer >= SPAWN_EVERY) {
    spawnTimer -= SPAWN_EVERY;
    spawnCreep();
  }
""")

# 5. A click on a free tile builds a tower.
_P5 = _edit(_P4, "function update(dt) {\n", """let towers = [];

function tileAt(x, y) {
  return { col: Math.floor(x / TILE), row: Math.floor(y / TILE) };
}

// A tile is road when its centre lies on one of the path's straight pieces.
function onPath(col, row) {
  const x = col * TILE + TILE / 2;
  const y = row * TILE + TILE / 2;
  for (let i = 0; i < path.length - 1; i++) {
    const a = path[i];
    const b = path[i + 1];
    if (x >= Math.min(a.x, b.x) && x <= Math.max(a.x, b.x) && y >= Math.min(a.y, b.y) && y <= Math.max(a.y, b.y)) return true;
  }
  return false;
}

function towerAt(col, row) {
  return towers.find((t) => t.col === col && t.row === row);
}

function makeTower(col, row) {
  return { col, row, x: col * TILE + TILE / 2, y: row * TILE + TILE / 2 };
}

canvas.addEventListener('click', (e) => {
  const box = canvas.getBoundingClientRect();
  const x = (e.clientX - box.left) * (canvas.width / box.width);
  const y = (e.clientY - box.top) * (canvas.height / box.height);
  const { col, row } = tileAt(x, y);
  if (onPath(col, row) || towerAt(col, row)) return;
  towers.push(makeTower(col, row));
});

function update(dt) {
""")
_P5 = _edit(_P5, "function draw() {\n", """function drawTower(t) {
  ctx.fillStyle = '#63b3ed';
  ctx.fillRect(t.x - 14, t.y - 14, 28, 28);
}

function draw() {
""")
_P5 = _edit(
    _P5, "  drawPath();\n  for (const c", "  drawPath();\n  for (const t of towers) drawTower(t);\n  for (const c"
)

# 6. Range, and the first creep in it.
_P6 = _edit(
    _P5,
    "{ col, row, x: col * TILE + TILE / 2, y: row * TILE + TILE / 2 }",
    "{ col, row, x: col * TILE + TILE / 2, y: row * TILE + TILE / 2, range: 120 }",
)
_P6 = _edit(_P6, "function update(dt) {\n", """// The creep in range that has walked furthest along the path.
function findTarget(t) {
  let best = null;
  for (const c of creeps) {
    if (Math.hypot(c.x - t.x, c.y - t.y) > t.range) continue;
    if (!best || c.dist > best.dist) best = c;
  }
  return best;
}

function update(dt) {
""")
_P6 = _edit(_P6, "  ctx.fillRect(t.x - 14, t.y - 14, 28, 28);\n}", """  ctx.fillRect(t.x - 14, t.y - 14, 28, 28);
  const target = findTarget(t);
  if (target) {
    ctx.strokeStyle = '#f6e05e';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(t.x, t.y);
    ctx.lineTo(target.x, target.y);
    ctx.stroke();
  }
}""")

# 7. A reload, counted in seconds.
_P7 = _edit(_P6, "range: 120 }", "range: 120, damage: 2, rate: 0.5, reload: 0 }")
_P7 = _edit(_P7, "function update(dt) {\n", """// Count the reload down with dt; when it is ready, fire at the first creep in range.
function updateTower(t, dt) {
  t.reload = Math.max(0, t.reload - dt);
  if (t.reload > 0) return;
  const target = findTarget(t);
  if (!target) return;
  target.hp -= t.damage;
  t.reload = t.rate;
}

function update(dt) {
""")
_P7 = _edit(
    _P7,
    "  for (const c of creeps) moveCreep(c, dt);\n",
    "  for (const c of creeps) moveCreep(c, dt);\n  for (const t of towers) updateTower(t, dt);\n",
)

# 8. Shots that fly and home.
_P8 = _edit(_P7, "let towers = [];\n", "let towers = [];\nlet shots = [];\n")
_P8 = _edit(
    _P8,
    "  target.hp -= t.damage;\n",
    "  shots.push({ x: t.x, y: t.y, target, speed: 300, damage: t.damage });\n",
)
_P8 = _edit(_P8, "function update(dt) {\n", """// Fly straight at the target's current position, so a moving target is followed.
function moveShot(s, dt) {
  const dx = s.target.x - s.x;
  const dy = s.target.y - s.y;
  const d = Math.hypot(dx, dy);
  const step = s.speed * dt;
  if (d <= step) {
    s.target.hp -= s.damage;
    s.done = true;
  } else {
    s.x += (dx / d) * step;
    s.y += (dy / d) * step;
  }
}

function update(dt) {
""")
_P8 = _edit(
    _P8,
    "  for (const t of towers) updateTower(t, dt);\n",
    "  for (const t of towers) updateTower(t, dt);\n  for (const s of shots) moveShot(s, dt);\n",
)
_P8 = _edit(
    _P8,
    "  creeps = creeps.filter((c) => c.hp > 0 && c.next < path.length);\n",
    "  creeps = creeps.filter((c) => c.hp > 0 && c.next < path.length);\n"
    "  shots = shots.filter((s) => !s.done && creeps.includes(s.target));\n",
)
_P8 = _edit(_P8, "function draw() {\n", """function drawShot(s) {
  ctx.fillStyle = '#f6e05e';
  ctx.beginPath();
  ctx.arc(s.x, s.y, 4, 0, Math.PI * 2);
  ctx.fill();
}

function draw() {
""")
_P8 = _edit(
    _P8,
    "  for (const c of creeps) drawCreep(c);\n}",
    "  for (const c of creeps) drawCreep(c);\n  for (const s of shots) drawShot(s);\n}",
)

# 9. Money: a reward in, a price out.
_P9 = _edit(
    _P8,
    "speed: 80, hp, maxHp: hp };",
    "speed: 80, hp, maxHp: hp, reward: 5 };",
)
_P9 = _edit(_P9, "let towers = [];\n", "let towers = [];\nlet money = 100;\nconst TOWER_COST = 50;\n")
_P9 = _edit(
    _P9,
    "  if (onPath(col, row) || towerAt(col, row)) return;\n  towers.push(makeTower(col, row));\n",
    "  if (onPath(col, row) || towerAt(col, row) || money < TOWER_COST) return;\n"
    "  money -= TOWER_COST;\n  towers.push(makeTower(col, row));\n",
)
_P9 = _edit(
    _P9,
    "  creeps = creeps.filter((c) => c.hp > 0 && c.next < path.length);\n",
    """  // A creep is paid for once, here, on the frame it is taken out.
  const alive = [];
  for (const c of creeps) {
    if (c.hp <= 0) money += c.reward;
    else if (c.next < path.length) alive.push(c);
  }
  creeps = alive;
""",
)
_P9 = _edit(
    _P9,
    "  for (const s of shots) drawShot(s);\n}",
    """  for (const s of shots) drawShot(s);
  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText(`$${money}`, 10, 20);
}""",
)

# 10. Waves.
_P10 = _edit(
    _P9,
    "function spawnCreep() {\n  creeps.push(makeCreep());\n}\n",
    """function spawnCreep(hp) {
  creeps.push(makeCreep(hp));
}

function startWave() {
  wave++;
  toSpawn = waves[wave - 1].count;
  spawnTimer = SPAWN_EVERY;
  state = 'wave';
}

function updateWaves(dt) {
  if (state === 'countdown') {
    countdown -= dt;
    if (countdown <= 0) startWave();
  } else if (state === 'wave') {
    spawnTimer += dt;
    if (toSpawn > 0 && spawnTimer >= SPAWN_EVERY) {
      spawnTimer -= SPAWN_EVERY;
      toSpawn--;
      spawnCreep(waves[wave - 1].hp);
    }
    // The wave is over when nothing is left to spawn and nothing is still walking.
    if (toSpawn === 0 && creeps.length === 0) {
      if (wave === waves.length) {
        state = 'won';
      } else {
        state = 'countdown';
        countdown = GAP;
      }
    }
  }
}
""",
)
_P10 = _edit(
    _P10,
    "const SPAWN_EVERY = 1.5;\nlet spawnTimer = 0;\n",
    """const SPAWN_EVERY = 1.5;
const GAP = 5;
let waves = [
  { count: 5, hp: 10 },
  { count: 8, hp: 16 },
  { count: 12, hp: 24 },
];
let wave = 0;
let state = 'countdown';
let countdown = 3;
let toSpawn = 0;
let spawnTimer = 0;
""",
)
_P10 = _edit(
    _P10,
    """  spawnTimer += dt;
  if (spawnTimer >= SPAWN_EVERY) {
    spawnTimer -= SPAWN_EVERY;
    spawnCreep();
  }
""",
    "  updateWaves(dt);\n",
)
_P10 = _edit(
    _P10,
    "  ctx.fillText(`$${money}`, 10, 20);\n}",
    """  ctx.fillText(`$${money}`, 10, 20);
  ctx.fillText(`Wave ${wave}/${waves.length}`, 90, 20);
  if (state === 'countdown') ctx.fillText(`Next wave in ${Math.ceil(countdown)}`, 160, 310);
  if (state === 'won') {
    ctx.font = '32px monospace';
    ctx.fillText('You win!', 170, 170);
  }
}""",
)

# 11. Lives, game over, and starting again.
_P11 = _edit(_P10, "let money = 100;\n", "let money = 100;\nlet lives = 10;\n")
_P11 = _edit(_P11, "function update(dt) {\n", """function reset() {
  creeps = [];
  towers = [];
  shots = [];
  money = 100;
  lives = 10;
  wave = 0;
  state = 'countdown';
  countdown = 3;
  toSpawn = 0;
  spawnTimer = 0;
}

addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && state === 'over') reset();
});

function update(dt) {
  if (state === 'over') return;
""")
_P11 = _edit(
    _P11,
    "    else if (c.next < path.length) alive.push(c);\n  }\n  creeps = alive;\n",
    """    else if (c.next < path.length) alive.push(c);
    else lives = Math.max(0, lives - 1);
  }
  creeps = alive;
  if (lives <= 0) state = 'over';
""",
)
_P11 = _edit(
    _P11,
    "  ctx.fillText(`Wave ${wave}/${waves.length}`, 90, 20);\n",
    "  ctx.fillText(`Wave ${wave}/${waves.length}`, 90, 20);\n  ctx.fillText(`Lives: ${lives}`, 220, 20);\n",
)
_P11 = _edit(
    _P11,
    "    ctx.fillText('You win!', 170, 170);\n  }\n",
    """    ctx.fillText('You win!', 170, 170);
  }
  if (state === 'over') {
    ctx.font = '32px monospace';
    ctx.fillText('Game over', 150, 160);
    ctx.font = '16px monospace';
    ctx.fillText('Enter to play again', 160, 190);
  }
""",
)


# ── Helpers the checks share ─────────────────────────────────────────────
# Written in JavaScript, put in front of a check's own lines.
_H = r"""
const click = (x, y) => {
  const el = document.querySelector("canvas");
  const box = el.getBoundingClientRect();
  const sx = box.width / el.width;
  const sy = box.height / el.height;
  el.dispatchEvent(new MouseEvent("click", { clientX: box.left + x * sx, clientY: box.top + y * sy, offsetX: x * sx, offsetY: y * sy, bubbles: true }));
};
const clickTile = (col, row) => click(col * 40 + 20, row * 40 + 20);
// A quiet board: no creeps, no towers, no shots, and nothing about to spawn.
const quiet = () => {
  spawnTimer = -1e9;
  creeps = [];
  towers = [];
  if (typeof shots !== "undefined") shots = [];
};
// A creep that stands still where the check puts it.
const still = (x, y, hp, dist) => {
  const c = makeCreep();
  c.x = x;
  c.y = y;
  c.speed = 0;
  c.hp = hp;
  c.maxHp = hp;
  c.dist = dist === undefined ? 0 : dist;
  return c;
};
"""


TOWER_STEPS: tuple[Step, ...] = (
    Step(
        id="td-01-path",
        track="Tower defense",
        title="A path is a list of points",
        teaches=(
            "A tower defense game is a road and things that walk along it. "
            "The road is not a picture, it is data: a list of points, called "
            "waypoints, and everything else - where creeps walk, which tiles "
            "are taken, what to draw - is worked out from that list. Put "
            "each point at the centre of a tile: column * TILE + TILE / 2. A "
            "tile is TILE pixels square (40 here, so the canvas is 12 tiles "
            "across and 8 down). Drawing the road is then one line through "
            "the points: beginPath, moveTo the first, lineTo each of the "
            "others, stroke - with a lineWidth as thick as a tile, so it "
            "reads as a road and not a wire."
        ),
        goal="Add const TILE = 40 and const path, an array of { x, y } points: (20, 60), (380, 60), (380, 220), (140, 220), (140, 300). Draw the road every frame as one line through them, lineWidth TILE.",
        starter=_P0,
        solution=_P1,
        check=r"""
expect(typeof TILE === "number" && TILE === 40, "Add const TILE = 40; - the size of one square of the grid, in pixels.");
expect(typeof path !== "undefined" && Array.isArray(path), "Make an array called path: const path = [{ x: 20, y: 60 }, ...];");
const want = [[20, 60], [380, 60], [380, 220], [140, 220], [140, 300]];
expect(path.length === want.length, `path has ${path.length} points; the road has ${want.length} - the start, three corners and the end. List each one.`);
for (let i = 0; i < want.length; i++) {
  expect(path[i] && path[i].x === want[i][0] && path[i].y === want[i][1], `path[${i}] should be { x: ${want[i][0]}, y: ${want[i][1]} }. Points go at the CENTRE of a tile: column * TILE + TILE / 2, row * TILE + TILE / 2 (column 0, row 1 is x 20, y 60).`);
}
cc.frames(1);
const calls = cc.drawn();
expect(calls.some((c) => c.name === "stroke"), "Draw the road as a line: beginPath, moveTo the first point, lineTo each of the others, then stroke - every frame, inside draw().");
expect(calls.some((c) => c.name === "moveTo" && c.args[0] === 20 && c.args[1] === 60), "Start the line at the first point: ctx.moveTo(path[0].x, path[0].y).");
for (let i = 1; i < want.length; i++) {
  expect(calls.some((c) => c.name === "lineTo" && c.args[0] === want[i][0] && c.args[1] === want[i][1]), `The road never goes through (${want[i][0]}, ${want[i][1]}). Draw a lineTo for every point after the first - a loop over the array does it.`);
}
const lw = document.querySelector("canvas").getContext("2d").lineWidth;
expect(lw >= 32 && lw <= 48, `The road is ${lw} pixels wide; make it about a tile: ctx.lineWidth = TILE.`);
""",
        hint="ctx.lineWidth = TILE; ctx.beginPath(); ctx.moveTo(path[0].x, path[0].y); for (const p of path.slice(1)) ctx.lineTo(p.x, p.y); ctx.stroke();",
    ),
    Step(
        id="td-02-walk",
        track="Tower defense",
        title="Walk the path",
        teaches=(
            "A creep walks toward its next waypoint, path[creep.next]. Each "
            "frame it may cover speed * dt pixels: pixels a second times "
            "seconds, never a fixed number a frame, or the same creep is "
            "slow on a slow screen. To aim, take the vector to the waypoint "
            "and divide by its length d, which gives a direction of length "
            "1. The trap is the corner. If the waypoint is closer than this "
            "frame's step, walking the whole step overshoots, and next frame "
            "the creep turns round and overshoots back: a jitter. So when "
            "the waypoint is within reach, snap onto it, move next on to the "
            "following one, and spend what is left of the step going the "
            "new way - a while loop does that. Keep dist as well, how far "
            "along the road the creep has walked: towers will want it."
        ),
        goal="Add makeCreep(), returning { x, y, next: 1, dist: 0, speed: 80 } standing on path[0], and let creeps = [makeCreep()]. Every frame move each creep speed * dt along the path - onto each waypoint, never past it, then on toward the next one (next goes up) - adding what it walks to dist. Remove a creep that has passed the last waypoint. Draw each creep as a circle.",
        starter=_P1,
        solution=_P2,
        check=r"""
const ROAD = [[20, 60], [380, 60], [380, 220], [140, 220], [140, 300]];
const roadDist = (px, py) => {
  let best = Infinity;
  for (let i = 0; i < ROAD.length - 1; i++) {
    const [ax, ay] = ROAD[i];
    const [bx, by] = ROAD[i + 1];
    const vx = bx - ax;
    const vy = by - ay;
    const t = Math.max(0, Math.min(1, ((px - ax) * vx + (py - ay) * vy) / (vx * vx + vy * vy)));
    best = Math.min(best, Math.hypot(px - (ax + t * vx), py - (ay + t * vy)));
  }
  return best;
};
const along = (d) => {
  for (let i = 0; i < ROAD.length - 1; i++) {
    const [ax, ay] = ROAD[i];
    const [bx, by] = ROAD[i + 1];
    const len = Math.hypot(bx - ax, by - ay);
    if (d <= len) return [ax + ((bx - ax) * d) / len, ay + ((by - ay) * d) / len];
    d -= len;
  }
  return ROAD[ROAD.length - 1];
};
expect(typeof makeCreep === "function", "Write function makeCreep() that returns a new creep: { x, y, next: 1, dist: 0, speed: 80 }, standing on path[0].");
expect(typeof creeps !== "undefined" && Array.isArray(creeps) && creeps.length === 1, "Start with one creep: let creeps = [makeCreep()];");
const c = creeps[0];
expect(near(c.x, 20, 0.5) && near(c.y, 60, 0.5), "A new creep stands on the first point of the path: x 20, y 60. Copy path[0].x and path[0].y.");
expect(c.next === 1 && c.dist === 0 && typeof c.speed === "number" && c.speed > 0, "A new creep has next: 1 (the waypoint it is walking to), dist: 0 and a speed in pixels a second, 80.");
const v = c.speed;
cc.frames(1);
expect(cc.arcs().some((a) => near(a.x, c.x, 1.5) && near(a.y, c.y, 1.5)), "Draw each creep every frame as a circle: ctx.arc(c.x, c.y, 12, 0, Math.PI * 2), then fill().");
const back = () => {
  c.x = 20;
  c.y = 60;
  c.next = 1;
  c.dist = 0;
  if (!creeps.includes(c)) creeps.push(c);
};
// Walk for some seconds at a frame rate; the creep must be on the road after every frame.
const walk = (seconds, fps) => {
  const n = Math.round(seconds * fps);
  for (let i = 0; i < n; i++) {
    cc.frames(1, 1000 / fps);
    expect(creeps.includes(c), `The creep disappeared after ${(i / fps).toFixed(1)} seconds, long before the end of the road.`);
    expect(roadDist(c.x, c.y) <= 0.5, `The creep left the road: it is at (${c.x.toFixed(1)}, ${c.y.toFixed(1)}) at ${((i + 1) / fps).toFixed(2)} seconds. Walking the whole step past a waypoint overshoots it - snap onto the waypoint when it is within reach.`);
  }
};
back();
cc.frames(120);
expect(near(c.x, 20 + 2 * v, 3) && near(c.y, 60, 1), `After 2 seconds at ${v} pixels a second the creep should be at x ${20 + 2 * v}, y 60; it is at (${c.x.toFixed(1)}, ${c.y.toFixed(1)}). Move it speed * dt each frame.`);
back();
cc.frames(60, 1000 / 30);
expect(near(c.x, 20 + 2 * v, 3), `On a slower screen (30 frames a second) the creep is at x ${c.x.toFixed(1)} after 2 seconds; it should be at ${20 + 2 * v} just the same. Move speed * dt, not a fixed amount a frame.`);
for (const fps of [60, 30]) {
  back();
  walk(7, fps);
  const [ex, ey] = along(7 * v);
  expect(Math.hypot(c.x - ex, c.y - ey) <= 7, `After 7 seconds at ${fps} frames a second the creep should be at about (${ex.toFixed(0)}, ${ey.toFixed(0)}), after two corners; it is at (${c.x.toFixed(1)}, ${c.y.toFixed(1)}). At a waypoint, set next to the following one and keep walking.`);
  expect(near(c.dist, 7 * v, 7), `dist should be how far the creep has walked, about ${7 * v} after 7 seconds; it is ${c.dist}. Add each piece of the walk to dist.`);
}
back();
c.x = 370;
cc.frames(1, 1000);
expect(roadDist(c.x, c.y) <= 0.5 && c.next >= 2, `One very long frame (a second) pushed the creep off the road to (${c.x.toFixed(1)}, ${c.y.toFixed(1)}). If the waypoint is closer than the step, put the creep on it and turn - never walk past.`);
for (const fps of [60, 30]) {
  back();
  cc.frames(Math.ceil(((840 + 40) / v) * fps), 1000 / fps);
  expect(!creeps.includes(c), `After walking the whole road at ${fps} frames a second the creep is still in creeps. Once next is past the last waypoint, take it out of the array.`);
}
""",
        hint="let left = c.speed * dt; while (left > 0 && c.next < path.length) { const p = path[c.next]; const d = Math.hypot(p.x - c.x, p.y - c.y); if (d <= left) { snap to p, c.next++, c.dist += d, left -= d } else { move left towards p; left = 0 } }",
    ),
    Step(
        id="td-03-health",
        track="Tower defense",
        title="Health bars",
        teaches=(
            "A creep has hp, its health now, and maxHp, what it started "
            "with. The bar over its head is the fraction hp / maxHp times the "
            "bar's full width, drawn on top of a darker bar of full width. "
            "Draw it from the creep's own x and y every frame, so it walks "
            "along with it. Clamp it at zero: a creep on -3 hp must not "
            "draw a bar of negative width. Dying is just a filter: keep the "
            "creeps with hp above zero, and every other part of the game "
            "can lower hp without worrying about removing anyone."
        ),
        goal="Give makeCreep() hp and maxHp, both 10. Draw a bar above each creep: a dark one BAR_W wide (const BAR_W = 24) and a green one on top of it, BAR_W * hp / maxHp wide. Remove creeps whose hp is 0 or less.",
        starter=_P2,
        solution=_P3,
        check=r"""
expect(typeof creeps !== "undefined" && creeps.length >= 1, "The creep from the last step should still be there at the start.");
const c = creeps[0];
expect(c.hp === 10 && c.maxHp === 10, "A new creep has hp: 10 and maxHp: 10. Give makeCreep() both.");
c.speed = 0;
const bars = () => cc.rects().filter((r) => r.h <= 8 && r.y >= c.y - 40 && r.y + r.h <= c.y && r.x + r.w >= c.x - 16 && r.x <= c.x + 16);
cc.frames(1);
const widths = bars().map((r) => r.w);
expect(widths.length >= 1, "Draw a health bar above each creep: a thin rectangle (4 pixels tall) a little above its circle, with fillRect.");
const full = Math.max(...widths);
expect(full >= 16 && full <= 48, `The health bar is ${full} pixels wide at full health; make it about as wide as the creep, BAR_W = 24.`);
c.hp = 5;
cc.frames(1);
expect(bars().some((r) => near(r.w, full / 2, 1.5)), `At 5 of 10 hp the green part of the bar should be half as wide as at full health (${full / 2} pixels): BAR_W * hp / maxHp.`);
c.hp = 3;
cc.frames(1);
expect(bars().some((r) => near(r.w, full * 0.3, 1.5)), `At 3 of 10 hp the bar should be ${(full * 0.3).toFixed(1)} pixels wide.`);
c.hp = 10;
c.speed = 80;
cc.frames(60);
expect(creeps.includes(c) && c.x > 60, "The creep should be walking again.");
expect(bars().length >= 1, "The bar should follow the creep: draw it from the creep's current x and y every frame.");
c.hp = 1;
cc.frames(2);
expect(creeps.includes(c), "A creep with 1 hp left is still alive.");
c.hp = 0;
cc.frames(1);
expect(!creeps.includes(c), "A creep with 0 hp should be taken out of creeps. Keep only the ones with hp > 0.");
const d = makeCreep();
creeps.push(d);
d.hp = -4;
cc.frames(1);
expect(!creeps.includes(d), "A creep below 0 hp is dead as well.");
""",
        hint="ctx.fillRect(x, c.y - 24, BAR_W * Math.max(0, c.hp) / c.maxHp, 4);   and   creeps = creeps.filter((c) => c.hp > 0 && c.next < path.length);",
    ),
    Step(
        id="td-04-spawn",
        track="Tower defense",
        title="Send them in",
        teaches=(
            "Spawning on a timer is the Snake tick again: add each frame's "
            "dt to spawnTimer, and when it holds a whole SPAWN_EVERY, take "
            "SPAWN_EVERY off it (not zero: the leftover keeps the rhythm "
            "exact) and spawn one creep. All creeps walk at the same speed, "
            "so they arrive in a column, 1.5 seconds and 120 pixels apart. "
            "A setInterval would spawn them too, but a timer you advance "
            "with dt stops when the game stops and can be changed, "
            "restarted and reset - which a wave system will need."
        ),
        goal="Start with no creeps: let creeps = []. Add const SPAWN_EVERY = 1.5, let spawnTimer = 0 and spawnCreep(), which pushes a makeCreep(). Add dt to spawnTimer every frame, and every SPAWN_EVERY seconds spawn one creep.",
        starter=_P3,
        solution=_P4,
        check=r"""
expect(typeof spawnCreep === "function", "Write function spawnCreep() that pushes a new creep, makeCreep(), onto creeps.");
expect(typeof SPAWN_EVERY === "number" && SPAWN_EVERY === 1.5, "Add const SPAWN_EVERY = 1.5; - the seconds between creeps.");
expect(typeof spawnTimer === "number", "Keep the time since the last creep in let spawnTimer = 0;");
expect(Array.isArray(creeps) && creeps.length === 0, "The game starts with no creeps: let creeps = [];");
cc.frames(80);
expect(creeps.length === 0, `${creeps.length} creep(s) after 1.3 seconds; the first should come after 1.5 seconds (SPAWN_EVERY), not before.`);
cc.frames(15);
expect(creeps.length === 1, `${creeps.length} creep(s) after 1.6 seconds; there should be exactly one, spawned at 1.5.`);
expect(Math.hypot(creeps[0].x - 20, creeps[0].y - 60) < 25, "A new creep starts at the beginning of the path, path[0] - this one is already far from it.");
cc.frames(277);
expect(creeps.length === 4, `${creeps.length} creeps after 6.2 seconds; one every 1.5 seconds makes 4 (at 1.5, 3, 4.5 and 6).`);
expect(new Set(creeps).size === 4, "Each spawn should make a new creep: push makeCreep(), not the same object again.");
for (let i = 0; i < creeps.length - 1; i++) {
  const gap = creeps[i].dist - creeps[i + 1].dist;
  expect(near(gap, SPAWN_EVERY * creeps[0].speed, 8), `Creeps should walk in a column ${SPAWN_EVERY * creeps[0].speed} pixels apart (1.5 seconds at speed ${creeps[0].speed}); these are ${gap.toFixed(0)} apart.`);
}
creeps = [];
spawnTimer = 0;
cc.frames(186, 1000 / 30);
expect(creeps.length === 4, `On a slower screen (30 frames a second) there are ${creeps.length} creeps after 6.2 seconds; there should still be 4. Count time with dt, not frames.`);
""",
        hint="spawnTimer += dt; if (spawnTimer >= SPAWN_EVERY) { spawnTimer -= SPAWN_EVERY; spawnCreep(); }",
    ),
    Step(
        id="td-05-build",
        track="Tower defense",
        title="Click a tile",
        teaches=(
            "The mouse gives page pixels; the game wants a tile. That is "
            "two conversions. Page to canvas: subtract the canvas's left "
            "and top (getBoundingClientRect), then multiply by canvas.width "
            "/ rect.width, because the canvas may be drawn bigger or smaller "
            "than its 480 pixels. Canvas to tile: Math.floor(x / TILE) - "
            "floor, not round, or the right half of every tile belongs to "
            "its neighbour. A tower may go on a tile only if it is not "
            "road and not already taken. A tile is road when its centre "
            "lies on one of the path's straight pieces; testing the "
            "waypoints alone would miss every tile between two of them."
        ),
        goal="Add let towers = [], tileAt(x, y) returning { col, row } for a point in canvas pixels, onPath(col, row), and a click listener on the canvas. A click on a tile that is neither road nor already a tower pushes a tower { col, row, x, y } onto towers (x and y its centre). Draw each tower as a square inside its tile.",
        starter=_P4,
        solution=_P5,
        check=_H + r"""
expect(typeof tileAt === "function", "Write function tileAt(x, y) that returns { col, row } for a point in canvas pixels.");
const T = (x, y) => { const r = tileAt(x, y); return r ? r.col + "," + r.row : "none"; };
expect(T(0, 0) === "0,0" && T(39.9, 39.9) === "0,0", "The top-left tile is column 0, row 0: x from 0 up to (not including) 40, and the same for y.");
expect(T(40, 40) === "1,1" && T(130, 250) === "3,6", `tileAt(130, 250) should be column 3, row 6 (Math.floor(x / TILE)); it says ${T(130, 250)}.`);
expect(T(479, 319) === "11,7", `The bottom-right corner is column 11, row 7; tileAt says ${T(479, 319)}.`);
expect(typeof onPath === "function", "Write function onPath(col, row) that says whether a tile is part of the road.");
for (const [col, row] of [[0, 1], [4, 1], [9, 1], [9, 3], [9, 5], [6, 5], [3, 5], [3, 6], [3, 7]]) {
  expect(onPath(col, row) === true, `Column ${col}, row ${row} is road, but onPath says no. A tile is road when its centre is on a straight piece of the path - including the tiles BETWEEN two waypoints.`);
}
for (const [col, row] of [[0, 0], [5, 2], [4, 2], [10, 1], [10, 3], [9, 6], [3, 4], [2, 5], [11, 7]]) {
  expect(onPath(col, row) === false, `Column ${col}, row ${row} is not road, but onPath says yes.`);
}
expect(Array.isArray(towers) && towers.length === 0, "Start with no towers: let towers = [];");
quiet();
clickTile(5, 3);
expect(towers.length === 1, "A click on a free tile (column 5, row 3) should build a tower: push one onto towers. (The click event's clientX and clientY are page pixels: take away the canvas's left and top, and scale by canvas.width / rect.width.)");
expect(towers[0].col === 5 && towers[0].row === 3 && towers[0].x === 220 && towers[0].y === 140, "The tower is on column 5, row 3 and its x, y are the tile's centre: 220, 140.");
click(119.9, 83);
click(120, 83);
click(479, 319);
clickTile(10, 3);
clickTile(5, 3);
const got = towers.map((t) => t.col + "," + t.row).sort().join(" ");
expect(got === ["10,3", "11,7", "2,2", "3,2", "5,3"].sort().join(" "), `Towers are on [${got}]; clicks at x 119.9 and 120 are in columns 2 and 3 (use Math.floor, not Math.round), the bottom-right corner is column 11, row 7, and a second click on a tower's tile builds nothing.`);
const before = towers.length;
for (const [col, row] of [[0, 1], [4, 1], [9, 1], [9, 3], [9, 5], [6, 5], [3, 5], [3, 6], [3, 7]]) clickTile(col, row);
expect(towers.length === before, "A click on the road must not build: a tower there would block the creeps' way and look wrong. Check onPath first.");
cc.frames(1);
const inTile = (col, row) => cc.rects().some((r) => r.w >= 16 && r.h >= 16 && r.x >= col * 40 && r.x + r.w <= col * 40 + 40 && r.y >= row * 40 && r.y + r.h <= row * 40 + 40);
for (const [col, row] of [[5, 3], [2, 2], [11, 7]]) {
  expect(inTile(col, row), `Draw every tower as a square inside its tile - nothing is drawn in column ${col}, row ${row}.`);
}
""",
        hint="const x = (e.clientX - box.left) * (canvas.width / box.width);   const { col, row } = tileAt(x, y);   if (onPath(col, row) || towerAt(col, row)) return;",
    ),
    Step(
        id="td-06-target",
        track="Tower defense",
        title="Range and the first target",
        teaches=(
            "A tower sees a circle: a creep is in range when its distance "
            "from the tower, Math.hypot(dx, dy), is at most the range. "
            "Testing |dx| and |dy| on their own sees a square whose corners "
            "reach too far, and comparing dx * dx + dy * dy needs range * "
            "range to match. Several creeps can be in range at once, so a "
            "tower needs a rule for choosing. The usual one is the first: "
            "the creep that has walked furthest along the path, which is "
            "what dist is for. 'Nearest' feels natural, but it has the "
            "tower shoot a straggler while the leaders walk away. Return "
            "null when there is nothing in range."
        ),
        goal="Give every tower range: 120. Write findTarget(tower), which returns the creep within range of the tower that has the largest dist, or null when there is none. Draw a yellow line from each tower to its target.",
        starter=_P5,
        solution=_P6,
        check=_H + r"""
expect(Array.isArray(towers), "The towers array from the last step should still be there.");
quiet();
clickTile(5, 3);
expect(towers.length === 1, "Building a tower with a click should still work.");
const t = towers[0];
expect(typeof t.range === "number" && t.range > 0, "Give every tower a range: range: 120, in pixels. Put it in makeTower().");
expect(typeof findTarget === "function", "Write function findTarget(tower) that returns the creep it should shoot, or null.");
const R = t.range;
const near1 = still(t.x + R * 0.8, t.y, 10, 100);
const far1 = still(t.x + R + 10, t.y, 10, 900);
creeps = [near1, far1];
expect(findTarget(t) === near1, "A creep just outside the range (range + 10 away) must not be chosen, however far along it is. A creep is in range when Math.hypot(dx, dy) <= range.");
const corner = still(t.x + R * 0.8, t.y + R * 0.8, 10, 100);
creeps = [corner];
expect(!findTarget(t), "A creep at 0.8 range across and 0.8 range down is 1.13 ranges away - out of range. Range is a circle: compare the distance, Math.hypot(dx, dy), with range, not dx and dy one by one.");
creeps = [];
expect(!findTarget(t), "With no creeps there is no target: return null.");
const lead = still(t.x - R * 0.9, t.y, 10, 500);
const back = still(t.x + R * 0.3, t.y, 10, 100);
creeps = [back, lead];
expect(findTarget(t) === lead, "Two creeps in range: the tower should shoot the one that has walked furthest (the larger dist), not the nearest one to the tower.");
creeps = [lead, back];
expect(findTarget(t) === lead, "The creep that has walked furthest is the target whichever order they are in the array - compare dist.");
const mid = still(t.x, t.y - R * 0.5, 10, 300);
creeps = [lead, mid, back];
expect(findTarget(t) === lead, "With three in range the largest dist wins.");
creeps = [back, still(t.x + R * 0.99, t.y, 10, 50)];
expect(findTarget(t) && findTarget(t).dist >= 50, "A creep right at the edge of the range, just inside it, is in range.");
creeps = [near1];
cc.frames(1);
const calls = cc.drawn();
const i = calls.findIndex((c) => c.name === "moveTo" && near(c.args[0], t.x, 1) && near(c.args[1], t.y, 1));
expect(i >= 0 && calls.slice(i).some((c) => c.name === "lineTo" && near(c.args[0], near1.x, 1) && near(c.args[1], near1.y, 1)), "Draw a line from the tower to its target: beginPath, moveTo(tower.x, tower.y), lineTo(target.x, target.y), stroke.");
creeps = [far1];
cc.frames(1);
expect(!cc.drawn().some((c) => c.name === "moveTo" && near(c.args[0], t.x, 1) && near(c.args[1], t.y, 1)), "A tower with no target in range should not draw a line.");
""",
        hint="if (Math.hypot(c.x - t.x, c.y - t.y) > t.range) continue;   if (!best || c.dist > best.dist) best = c;",
    ),
    Step(
        id="td-07-cooldown",
        track="Tower defense",
        title="Fire rate",
        teaches=(
            "A tower that fires every frame is a machine gun, and one that "
            "fires every N frames is a different tower on a faster screen. "
            "Give it a reload: the seconds until it may fire again. Each "
            "frame take dt off it, never below zero; when it is zero and "
            "there is a target, fire and set it back to the rate. Only "
            "resetting it when it fires means a tower with nothing to shoot "
            "is ready the moment something comes into range. For now a hit "
            "is instant: the target simply loses the tower's damage. Only "
            "the target is hit, not everything in range."
        ),
        goal="Give every tower damage: 2, rate: 0.5 (seconds between shots) and reload: 0. Each frame take dt off reload, not going below 0. When it is 0 and findTarget finds a creep, take damage off that creep's hp and set reload to rate.",
        starter=_P6,
        solution=_P7,
        check=_H + r"""
expect(Array.isArray(towers), "The towers array from the last step should still be there.");
for (const fps of [60, 30]) {
  quiet();
  clickTile(5, 3);
  expect(towers.length === 1, "Building a tower with a click should still work.");
  const t = towers[0];
  expect(typeof t.damage === "number" && t.damage > 0 && typeof t.rate === "number" && typeof t.reload === "number", "Give every tower damage: 2, rate: 0.5 and reload: 0 - put them in makeTower().");
  t.rate = 0.5;
  t.reload = 0;
  const c = still(t.x + 60, t.y, 1000, 100);
  const other = still(t.x - 60, t.y, 1000, 10);
  creeps = [other, c];
  cc.frames(1, 1000 / fps);
  expect(c.hp < 1000, "A tower whose reload is 0, with a creep in range, should fire at once: take damage off the target's hp.");
  let hits = 1;
  for (let i = 1; i < 3 * fps; i++) {
    const hp = c.hp;
    cc.frames(1, 1000 / fps);
    if (c.hp < hp) hits++;
  }
  expect(hits >= 5 && hits <= 7, `At ${fps} frames a second the tower hit ${hits} times in 3 seconds; with a rate of 0.5 seconds it should be 6 or 7. Count the reload down with dt, not frames.`);
  expect(near(c.hp, 1000 - hits * t.damage, 0.001), `Each hit should take exactly damage (${t.damage}) off the hp; ${hits} hits left it on ${c.hp}.`);
  expect(other.hp === 1000, "The creep nearer to the tower but behind the leader lost hp: only the target (the one that has walked furthest) is hit.");
}
""",
        hint="t.reload = Math.max(0, t.reload - dt); if (t.reload > 0) return; const target = findTarget(t); if (!target) return; target.hp -= t.damage; t.reload = t.rate;",
    ),
    Step(
        id="td-08-shots",
        track="Tower defense",
        title="Shots that home",
        teaches=(
            "An instant hit is hard to read. A shot is a small object that "
            "flies: { x, y, target, speed, damage }. Each frame it heads "
            "straight for where its target is now, speed * dt along the "
            "line. It is aimed again every frame, so it homes - it bends "
            "after a creep going round a corner. When it is within one "
            "step of the target it lands: the damage is dealt and the "
            "shot is gone. It must also go when the target dies or walks "
            "off the end first; test creeps.includes(shot.target), or it "
            "flies on toward a spot where nothing is, and a hit on a dead "
            "creep is a hit on nothing."
        ),
        goal="Add let shots = []. A tower that fires now pushes a shot { x, y, target, speed: 300, damage } starting at the tower, instead of an instant hit. Each frame every shot moves speed * dt toward its target's current position; when it arrives it takes damage off the target's hp and is removed. A shot whose target is no longer in creeps is removed too. Draw each shot as a small circle.",
        starter=_P7,
        solution=_P8,
        check=_H + r"""
expect(typeof shots !== "undefined" && Array.isArray(shots), "Add let shots = [];");
for (const fps of [60, 30]) {
  quiet();
  const c = still(250, 50, 10, 50);
  creeps = [c];
  shots.push({ x: 50, y: 50, target: c, speed: 200, damage: 3 });
  const s = shots[0];
  cc.frames(fps / 2, 1000 / fps);
  expect(near(s.x, 150, 6) && near(s.y, 50, 2), `At ${fps} frames a second a shot of speed 200 should have flown 100 pixels in half a second, to x 150; it is at (${s.x.toFixed(1)}, ${s.y.toFixed(1)}). Move it speed * dt.`);
  expect(c.hp === 10, "The shot has not arrived yet; the creep should not have lost hp.");
  cc.frames(Math.round(fps * 0.6), 1000 / fps);
  expect(c.hp === 7, `The shot should have landed after a second: damage 3 off 10 hp leaves 7; the creep has ${c.hp}.`);
  expect(shots.length === 0, "A shot that has landed must be removed from shots (it hit once).");
}
quiet();
const h = still(250, 50, 10, 50);
creeps = [h];
shots.push({ x: 50, y: 50, target: h, speed: 200, damage: 3 });
const hs = shots[0];
cc.frames(15);
h.y = 250;
cc.frames(30);
expect(near(hs.x, 160, 8) && near(hs.y, 130, 8), `The creep moved and the shot should have turned after it, to about (160, 130); it is at (${hs.x.toFixed(1)}, ${hs.y.toFixed(1)}). Aim at the target's current x and y every frame.`);
cc.frames(70);
expect(h.hp === 7 && shots.length === 0, "The shot should have caught the creep and landed, once.");
quiet();
const d = still(250, 50, 10, 50);
creeps = [d];
shots.push({ x: 50, y: 50, target: d, speed: 200, damage: 3 });
cc.frames(5);
d.hp = 0;
cc.frames(2);
expect(shots.length === 0, "The target died while the shot was flying, and the shot is still there. Remove shots whose target is no longer in creeps.");
quiet();
const e = still(250, 50, 10, 50);
creeps = [e];
shots.push({ x: 50, y: 50, target: e, speed: 200, damage: 3 });
cc.frames(5);
e.next = path.length;
cc.frames(2);
expect(shots.length === 0, "The target left the game (walked off the end) and the shot is still flying. Remove shots whose target is no longer in creeps.");
quiet();
const g = still(250, 50, 10, 50);
creeps = [g];
shots.push({ x: 100, y: 50, target: g, speed: 200, damage: 3 });
cc.frames(1);
expect(cc.arcs().some((a) => near(a.x, shots[0].x, 2) && near(a.y, shots[0].y, 2) && a.r < 8), "Draw each shot as a small circle (radius under 8) at its x and y.");
quiet();
clickTile(5, 3);
const t = towers[0];
t.reload = 0;
const target = still(t.x + 60, t.y, 10, 100);
creeps = [target];
cc.frames(1);
expect(shots.length === 1 && shots[0].target === target, "A tower that fires should push a shot with the creep as its target.");
expect(target.hp === 10, "The creep lost hp the moment the tower fired. The damage should land when the shot arrives.");
cc.frames(20);
expect(target.hp === 10 - t.damage && shots.length === 0, `After the shot has had time to arrive the creep should be on ${10 - t.damage} hp and the shot gone; hp is ${target.hp} and there are ${shots.length} shots.`);
""",
        hint="shots.push({ x: t.x, y: t.y, target, speed: 300, damage: t.damage });   in moveShot: if (d <= step) { s.target.hp -= s.damage; s.done = true; } else { move step towards the target }",
    ),
    Step(
        id="td-09-money",
        track="Tower defense",
        title="Money",
        teaches=(
            "Money is a number with two doors. In: a creep that dies pays "
            "its reward. Out: a tower costs TOWER_COST, and without enough "
            "money the click does nothing. Decide before you spend, so a "
            "refused click (on the road, on a tower, too poor) costs "
            "nothing. And pay the reward in one place only, where dead "
            "creeps are taken out of the game. Pay it when a shot lands "
            "instead and two shots arriving on the same frame both find a "
            "dead creep and both pay. A creep that walks off the end is "
            "taken out too but nobody killed it: only hp <= 0 pays."
        ),
        goal="Add let money = 100, const TOWER_COST = 50 and reward: 5 on every creep. Building costs TOWER_COST; with less money than that a click builds nothing. A creep removed because its hp ran out adds its reward to money, once; one that walked off the end pays nothing. Write the money on the screen.",
        starter=_P8,
        solution=_P9,
        check=_H + r"""
expect(typeof money === "number" && money === 100, "Start with let money = 100;");
expect(typeof TOWER_COST === "number" && TOWER_COST === 50, "Add const TOWER_COST = 50; - what a tower costs.");
cc.frames(1);
expect(cc.texts().some((t) => t.includes("100")), "Write the money on the screen, for instance `$${money}` - it should show 100 at the start.");
quiet();
clickTile(5, 3);
expect(towers.length === 1 && money === 50, `A tower should cost TOWER_COST: money should be 50 after the first, and is ${money}.`);
clickTile(4, 1);
clickTile(5, 3);
expect(money === 50, `A click that builds nothing (on the road, or on a tower) must cost nothing; money is ${money}. Check the tile first, then spend.`);
clickTile(7, 3);
expect(towers.length === 2 && money === 0, `A second tower takes the last of the money: 2 towers and money 0; there are ${towers.length} and money is ${money}.`);
clickTile(2, 2);
expect(towers.length === 2 && money === 0, `With no money a click must not build, and money must not go below 0: ${towers.length} towers, money ${money}.`);
cc.frames(1);
expect(cc.texts().some((t) => t.includes("0")), "The screen should show the money.");
quiet();
money = 0;
const dead = still(200, 100, 5, 0);
dead.reward = 7;
dead.hp = 0;
creeps = [dead];
cc.frames(1);
expect(money === 7 && creeps.length === 0, `A creep that dies should pay its reward (7 here) and be removed: money is ${money}.`);
cc.frames(5);
expect(money === 7, `The reward was paid again after the creep was gone: money is ${money}. Pay it once, where the dead are taken out.`);
quiet();
money = 0;
const pair = still(200, 100, 5, 0);
pair.reward = 7;
creeps = [pair];
shots.push({ x: 200, y: 100, target: pair, speed: 300, damage: 10 });
shots.push({ x: 200, y: 100, target: pair, speed: 300, damage: 10 });
cc.frames(3);
expect(money === 7, `Two shots landed on one creep on the same frame and money is ${money}; the creep is paid for once (7), however many shots killed it.`);
quiet();
money = 0;
const ran = still(140, 290, 10, 800);
ran.reward = 7;
ran.speed = 80;
ran.next = path.length - 1;
creeps = [ran];
cc.frames(30);
expect(creeps.length === 0 && money === 0, `A creep that walked off the end was not killed and should pay nothing; money is ${money}.`);
quiet();
money = 100;
clickTile(5, 3);
const t = towers[0];
const prey = still(t.x + 60, t.y, 1, 100);
prey.maxHp = 1;
prey.reward = 4;
creeps = [prey];
cc.frames(60);
expect(creeps.length === 0 && money === 54, `A tower killed a creep worth 4 with 50 left in the bank: money should be 54, it is ${money}.`);
""",
        hint="if (c.hp <= 0) money += c.reward; else if (c.next < path.length) alive.push(c);   and   if (onPath(col, row) || towerAt(col, row) || money < TOWER_COST) return; money -= TOWER_COST;",
    ),
    Step(
        id="td-10-waves",
        track="Tower defense",
        title="Waves",
        teaches=(
            "A wave is data: how many creeps, how tough. Keep them in a "
            "list, waves, with a number, wave, for the one running. The "
            "game becomes a small state machine. 'countdown' waits, taking "
            "dt off countdown. 'wave' spawns toSpawn creeps, one per "
            "SPAWN_EVERY, then waits for the last to be dead or gone. After "
            "the final wave it is 'won'. Starting a wave is one function. "
            "The thing to get right is when a wave ends: not when its last "
            "creep is spawned, but when nothing is left to spawn and "
            "nothing is still walking."
        ),
        goal="Replace the endless spawning. Add let waves = [{ count: 5, hp: 10 }, { count: 8, hp: 16 }, { count: 12, hp: 24 }], let wave = 0, let state = 'countdown', let countdown = 3, let toSpawn = 0 and const GAP = 5. When countdown reaches 0, wave goes up by one and that wave's count creeps, each with that wave's hp, are spawned one per SPAWN_EVERY. When all are spawned and none are left, the next countdown (GAP seconds) starts; after the last wave state is 'won'. Write the wave and the countdown on the screen, and 'You win!' when won.",
        starter=_P9,
        solution=_P10,
        check=_H + r"""
expect(typeof waves !== "undefined" && Array.isArray(waves) && typeof wave === "number" && typeof state === "string" && typeof countdown === "number" && typeof toSpawn === "number", "Add let waves (a list of { count, hp }), let wave = 0, let state = 'countdown', let countdown = 3 and let toSpawn = 0.");
expect(wave === 0 && state === "countdown" && countdown > 0, `The game starts with wave 0, state 'countdown' and a few seconds on the clock; wave is ${wave}, state is '${state}', countdown is ${countdown}.`);
expect(creeps.length === 0, "No creeps before the first wave.");
cc.frames(1);
expect(cc.texts().some((t) => /wave/i.test(t)), "Write the wave on the screen, for instance `Wave ${wave}/${waves.length}`, and 'Next wave in 3' during a countdown.");
waves = [{ count: 2, hp: 5 }, { count: 3, hp: 9 }];
towers = [];
// Play until cond() or max frames; note every creep the first time it is seen.
let seen = new Map();
let peak = 0;
const play = (cond, max, fps) => {
  let n = 0;
  while (!cond() && n < max) {
    cc.frames(1, 1000 / fps);
    n++;
    peak = Math.max(peak, creeps.length);
    for (const c of creeps) if (!seen.has(c)) seen.set(c, { hp: c.hp, at: cc.time });
  }
  return n;
};
const c0 = countdown;
const t0 = cc.time;
play(() => wave === 1, 60 * (c0 + 3), 60);
expect(wave === 1 && state === "wave", `The countdown ran out and wave should be 1 with state 'wave'; wave is ${wave}, state is '${state}'.`);
expect(near((cc.time - t0) / 1000, c0, 0.1), `The first wave should start ${c0} seconds in; it started after ${((cc.time - t0) / 1000).toFixed(2)}. Take dt off countdown each frame.`);
cc.frames(1);
expect(cc.texts().some((t) => /wave\s*1/i.test(t)), "Write the wave number on the screen: Wave 1.");
play(() => state !== "wave", 60 * 40, 60);
expect(state === "countdown" && wave === 1, `After the first wave state should be 'countdown' with wave still 1; state is '${state}', wave ${wave}. (A wave is over when everything is spawned AND nothing is left walking.)`);
expect(creeps.length === 0, "The next countdown started while creeps were still on the road: a wave ends only when none are left.");
expect(seen.size === 2 && peak === 2, `Wave 1 should send 2 creeps; ${seen.size} were spawned.`);
const hps1 = [...seen.values()];
expect(hps1.every((s) => s.hp === 5), "Wave 1's creeps should have the wave's hp (5): makeCreep(waves[wave - 1].hp).");
expect(near((hps1[1].at - hps1[0].at) / 1000, SPAWN_EVERY, 0.1), `The creeps of a wave come one per SPAWN_EVERY (${SPAWN_EVERY} seconds); these were ${((hps1[1].at - hps1[0].at) / 1000).toFixed(2)} apart.`);
expect(countdown > 1, `A new countdown of GAP seconds should start between waves; it is ${countdown}.`);
cc.frames(1);
expect(cc.texts().some((t) => /wave/i.test(t)), "Keep the wave on the screen during the countdown.");
seen = new Map();
peak = 0;
const c1 = countdown;
const t1 = cc.time;
play(() => wave === 2, 30 * (c1 + 3), 30);
expect(wave === 2 && state === "wave", `The second wave should start; wave is ${wave}, state is '${state}'.`);
expect(near((cc.time - t1) / 1000, c1, 0.15), `At 30 frames a second the second wave started after ${((cc.time - t1) / 1000).toFixed(2)} seconds instead of ${c1.toFixed(2)}. Count the countdown with dt, not frames.`);
play(() => state !== "wave", 30 * 40, 30);
expect(seen.size === 3 && peak === 3, `Wave 2 should send 3 creeps; ${seen.size} were spawned.`);
expect([...seen.values()].every((s) => s.hp === 9), "Wave 2's creeps should have hp 9, from waves[1].");
expect(state === "won" && wave === 2, `After the last wave state should be 'won'; it is '${state}' with wave ${wave}.`);
cc.frames(300);
expect(wave === 2 && creeps.length === 0 && state === "won", "Once the game is won nothing else should spawn.");
expect(cc.texts().some((t) => /win/i.test(t)), "Say 'You win!' on the screen when the game is won.");
""",
        hint="if (toSpawn === 0 && creeps.length === 0) { if (wave === waves.length) state = 'won'; else { state = 'countdown'; countdown = GAP; } }",
    ),
    Step(
        id="td-11-lives",
        track="Tower defense",
        title="Lives and game over",
        teaches=(
            "Every creep that walks off the end costs a life. The subtle "
            "part is that it costs one life, once: if the creep stays in "
            "the array, the check that notices it fires every frame and ten "
            "lives are gone in a sixth of a second. Take the creep out as "
            "the life is taken. At zero the game is over - a state, like "
            "in Snake: update stops and the screen says so. Restarting is "
            "a function that puts every variable back as it was at the "
            "start - the lists, the money, the lives, the wave, the clock "
            "- and miss one and the second game plays differently from the "
            "first. Enter does it, but only when the game is over."
        ),
        goal="Add let lives = 10. A creep that reaches the end of the path costs one life, once, and is removed; at 0 lives state becomes 'over', everything stops, and the screen says 'Game over'. Enter, only when the game is over, calls reset(), which puts creeps, towers, shots, money, lives, wave, state, countdown, toSpawn and spawnTimer back as they were at the start. Write the lives on the screen.",
        starter=_P10,
        solution=_P11,
        check=_H + r"""
expect(typeof lives === "number" && lives > 0, "Add let lives = 10;");
const L0 = lives;
const M0 = money;
const C0 = countdown;
cc.frames(1);
expect(cc.texts().some((t) => /live/i.test(t) && t.includes(String(L0))), "Write the lives on the screen, for instance `Lives: ${lives}`.");
// Hold the first wave off while the check sets things up.
countdown = 1000;
const runner = (hp) => {
  const c = still(140, 290, hp, 800);
  c.speed = 80;
  c.next = path.length - 1;
  return c;
};
creeps = [runner(10)];
cc.frames(40);
expect(creeps.length === 0, "A creep that walked off the end should be removed from creeps.");
expect(lives === L0 - 1, `One creep reached the end: lives should go from ${L0} to ${L0 - 1}; it is ${lives}. It costs one life, once - remove the creep as you take the life.`);
cc.frames(60);
expect(lives === L0 - 1, `Lives kept dropping after the creep was gone (${lives}). Take a life once per creep.`);
const killed = runner(10);
killed.next = path.length;
killed.hp = 0;
creeps = [killed];
cc.frames(40);
expect(lives === L0 - 1, `A creep that was killed on the last step cost a life (lives is ${lives}). Only living creeps hurt.`);
clickTile(5, 3);
expect(towers.length === 1, "Building a tower with a click should still work.");
const marker = money;
cc.press("Enter");
expect(towers.length === 1 && money === marker && lives === L0 - 1, "Enter in the middle of a game restarted it. Only restart when state is 'over'.");
wave = 2;
toSpawn = 4;
spawnTimer = 0.7;
lives = 1;
creeps = [runner(10)];
cc.frames(40);
expect(lives === 0 && state === "over", `The last life is gone and state should be 'over'; lives is ${lives} and state is '${state}'.`);
expect(cc.texts().some((t) => /game over/i.test(t)), "When the game is over, say so on the screen: Game over.");
const walker = still(20, 60, 10, 0);
walker.speed = 80;
creeps = [walker];
cc.frames(60);
expect(walker.x === 20 && walker.y === 60, "After game over everything should stop - the creeps are still walking.");
expect(wave === 2 && toSpawn === 4, "Nothing about the waves should change after game over.");
shots.push({ x: 10, y: 10, target: still(10, 10, 5, 0), speed: 100, damage: 1 });
cc.press("ArrowLeft");
expect(state === "over", "A key other than Enter restarted the game. Only Enter should.");
cc.press("Enter");
expect(state === "countdown" && wave === 0, `Pressing Enter after game over should start again: state 'countdown' and wave 0; state is '${state}' and wave ${wave}.`);
expect(lives === L0 && money === M0, `A new game starts with ${L0} lives and ${M0} money; there are ${lives} and ${money}.`);
expect(creeps.length === 0 && towers.length === 0 && shots.length === 0, `A new game starts with no creeps, towers or shots; there are ${creeps.length}, ${towers.length} and ${shots.length}.`);
expect(toSpawn === 0 && spawnTimer === 0, `A new game starts with toSpawn 0 and spawnTimer 0; they are ${toSpawn} and ${spawnTimer}.`);
expect(near(countdown, C0, 0.01), `The new game's countdown should be back at ${C0}; it is ${countdown}.`);
const t2 = cc.time;
let n = 0;
while (wave === 0 && n < 60 * 20) {
  cc.frames(1, 1000 / 30);
  n++;
}
expect(wave === 1 && near((cc.time - t2) / 1000, C0, 0.15), `The first wave of the new game should come after ${C0} seconds; wave is ${wave} after ${((cc.time - t2) / 1000).toFixed(2)}.`);
cc.frames(3, 1000 / 30);
expect(creeps.length === 1 && creeps[0].hp === waves[0].hp, "The new game's first wave should send its first creep.");
""",
        hint="else lives = Math.max(0, lives - 1);  if (lives <= 0) state = 'over';  and at the top of update: if (state === 'over') return;   and reset() sets everything back.",
    ),
    Step(
        id="td-12-yours",
        track="Tower defense",
        title="Now it's yours",
        teaches=(
            "A whole tower defense: a road that is data, walkers, health, "
            "a mouse that picks tiles, targeting, reloads, homing shots, "
            "money, waves and lives. Ideas, easier first: balance it (can "
            "you win? can anyone?); sell a tower for half its price; draw "
            "each tower's range when the mouse is over it; Enter to "
            "restart after winning too; a second tower type that is slow "
            "and hits hard, or one that slows creeps; creeps that are "
            "faster or tougher or that pay more; a button to call the "
            "next wave early; upgrading a tower; and a second map, which "
            "is only a different path array."
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_P11,
        solution=_P11,
        check="",
    ),
)
