"""The Canvas track after Breakout: a side-on Platformer.

Dodge taught the loop, time, keys and boxes; Breakout added velocity,
bouncing and the mouse. A platformer adds the thing both left out: the world
pushes back. Gravity is an acceleration, a jump is only allowed from the
ground, running has momentum, the level is a grid of tiles, and a tile
collision is settled one axis at a time (x, then y) or the player snags on
every corner. Then the details that make it feel good (one-way platforms,
coyote time, a short hop), coins, a goal with a respawn, and a camera.

Same rules as the other tracks: each step's starter is the step before,
finished; a check plays the program (keys held, frames stepped) and never
reads it. The checks that need a level build their own by writing into
`level`, so they do not depend on the map the learner drew.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

_SETUP = """const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');
"""

_LOOP = """
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

_LOOP_CAPPED = _LOOP.replace(
    "const dt = (time - last) / 1000;",
    "const dt = Math.min((time - last) / 1000, 1 / 30);",
)

_KEYS = """
const keys = new Set();
addEventListener('keydown', (e) => keys.add(e.key));
addEventListener('keyup', (e) => keys.delete(e.key));
"""

_BG = """  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
"""


def _build_level() -> list[str]:
    """30 x 10 tiles: ground with a pit, two one-way ledges, a wall, coins, a flag."""
    g = [["."] * 30 for _ in range(10)]

    def put(row: int, first: int, last: int, ch: str) -> None:
        for col in range(first, last + 1):
            g[row][col] = ch

    put(9, 0, 29, "#")
    put(9, 11, 13, ".")
    for row in range(10):
        g[row][0] = "#"
        g[row][29] = "#"
    put(7, 4, 7, "=")
    put(5, 9, 12, "=")
    put(7, 17, 18, "#")
    put(8, 17, 18, "#")
    put(6, 21, 24, "=")
    for row, col in ((6, 5), (6, 6), (4, 10), (4, 11), (8, 15), (5, 22), (5, 23), (8, 25)):
        g[row][col] = "o"
    g[8][27] = "F"
    return ["".join(r) for r in g]


_LEVEL = "const level = [\n" + "".join(f"  '{row}',\n" for row in _build_level()) + "];\n"

# ── State ────────────────────────────────────────────────────────────
_C_GRAVITY = "const GRAVITY = 1800;\n"
_C_FLOOR = "const FLOOR = 288;\n"
_C_JUMP = "const JUMP = 620;\n"
_C_RUN = "const ACCEL = 1600;\nconst FRICTION = 1400;\nconst MAX_SPEED = 220;\n"
_C_TILE = "const TILE = 32;\n"
_C_FALL = "const MAX_FALL = 900;\n"
_C_FEEL = "const COYOTE = 0.1;\nconst JUMP_CUT = 200;\n"
_PLAYER = "const player = { x: 64, y: 0, w: 24, h: 30, vx: 0, vy: 0, onGround: false };\n"
_PLAYER_FEEL = "const player = { x: 64, y: 0, w: 24, h: 30, vx: 0, vy: 0, onGround: false, coyote: 0 };\n"

_COINS = """
const coins = [];
for (let row = 0; row < level.length; row++) {
  for (let col = 0; col < level[row].length; col++) {
    if (level[row][col] === 'o') {
      coins.push({ x: col * TILE + TILE / 2, y: row * TILE + TILE / 2, taken: false });
    }
  }
}
let score = 0;
"""

_GOAL_STATE = "const START = { x: 64, y: 258 };\nlet state = 'playing';\n"
_CAMERA_STATE = "const camera = { x: 0 };\n"

# ── Update ───────────────────────────────────────────────────────────
_JUMP = """  if ((keys.has('ArrowUp') || keys.has(' ')) && player.onGround) {
    player.vy = -JUMP;
    player.onGround = false;
  }
"""

_JUMP_FEEL = """  const jumpHeld = keys.has('ArrowUp') || keys.has(' ');
  if (player.onGround) player.coyote = COYOTE;
  else player.coyote -= dt;
  if (jumpHeld && player.coyote > 0) {
    player.vy = -JUMP;
    player.coyote = 0;
  }
  if (!jumpHeld && player.vy < -JUMP_CUT) player.vy = -JUMP_CUT;
"""

_RUN = """  const dir = (keys.has('ArrowRight') ? 1 : 0) - (keys.has('ArrowLeft') ? 1 : 0);
  if (dir !== 0) {
    player.vx += dir * ACCEL * dt;
  } else if (player.vx > 0) {
    player.vx = Math.max(0, player.vx - FRICTION * dt);
  } else if (player.vx < 0) {
    player.vx = Math.min(0, player.vx + FRICTION * dt);
  }
  player.vx = Math.max(-MAX_SPEED, Math.min(MAX_SPEED, player.vx));
"""

_MOVE_FREE = "  player.x += player.vx * dt;\n"

_PHYS_FLOOR = """  player.vy += GRAVITY * dt;
  player.y += player.vy * dt;
  player.onGround = false;
  if (player.y + player.h >= FLOOR) {
    player.y = FLOOR - player.h;
    player.vy = 0;
    player.onGround = true;
  }
"""

_CALL_Y = "  moveY(dt);\n"
_CALL_XY = "  moveX(dt);\n  moveY(dt);\n"

_COIN_UPDATE = """  for (const c of coins) {
    if (c.taken) continue;
    const dx = Math.abs(c.x - (player.x + player.w / 2));
    const dy = Math.abs(c.y - (player.y + player.h / 2));
    if (dx < 8 + player.w / 2 && dy < 8 + player.h / 2) {
      c.taken = true;
      score += 1;
    }
  }
"""

_GOAL_UPDATE = """  if (player.y > canvas.height + 100) respawn();
  if (touches('F')) state = 'won';
"""

_STOP = "  if (state !== 'playing') return;\n"

_CAMERA_UPDATE = """  const target = player.x + player.w / 2 - canvas.width / 2;
  camera.x = Math.max(0, Math.min(level[0].length * TILE - canvas.width, target));
"""

# ── Functions ────────────────────────────────────────────────────────
_FN_TILES = """
function tileAt(col, row) {
  if (col < 0 || col >= level[0].length) return '#';
  if (row < 0 || row >= level.length) return '.';
  return level[row][col];
}

function solidAt(col, row) {
  return tileAt(col, row) === '#';
}

function overlapsSolid() {
  const left = Math.floor(player.x / TILE);
  const right = Math.ceil((player.x + player.w) / TILE) - 1;
  const top = Math.floor(player.y / TILE);
  const bottom = Math.ceil((player.y + player.h) / TILE) - 1;
  for (let row = top; row <= bottom; row++) {
    for (let col = left; col <= right; col++) {
      if (solidAt(col, row)) return true;
    }
  }
  return false;
}
"""

_FN_MOVEY = """
function moveY(dt) {
  player.vy += GRAVITY * dt;
  player.y += player.vy * dt;
  player.onGround = false;
  if (overlapsSolid()) {
    if (player.vy > 0) {
      player.y = Math.floor((player.y + player.h) / TILE) * TILE - player.h;
      player.onGround = true;
    } else {
      player.y = Math.floor(player.y / TILE) * TILE + TILE;
    }
    player.vy = 0;
  }
}
"""

_FN_MOVEX = """
function moveX(dt) {
  player.x += player.vx * dt;
  if (overlapsSolid()) {
    if (player.vx > 0) {
      player.x = Math.floor((player.x + player.w) / TILE) * TILE - player.w;
    } else {
      player.x = Math.floor(player.x / TILE) * TILE + TILE;
    }
    player.vx = 0;
  }
}
"""

_FN_MOVEY_FALL = _FN_MOVEY.replace(
    "  player.vy += GRAVITY * dt;\n",
    "  player.vy += GRAVITY * dt;\n  player.vy = Math.min(player.vy, MAX_FALL);\n",
)

_FN_ONEWAY = """
function oneWayRow(prevBottom) {
  const left = Math.floor(player.x / TILE);
  const right = Math.ceil((player.x + player.w) / TILE) - 1;
  const bottom = player.y + player.h;
  const row = Math.floor(bottom / TILE);
  if (prevBottom > row * TILE) return -1;
  for (let col = left; col <= right; col++) {
    if (tileAt(col, row) === '=') return row;
  }
  return -1;
}
"""

_FN_MOVEY_ONEWAY = """
function moveY(dt) {
  const prevBottom = player.y + player.h;
  player.vy += GRAVITY * dt;
  player.vy = Math.min(player.vy, MAX_FALL);
  player.y += player.vy * dt;
  player.onGround = false;
  if (overlapsSolid()) {
    if (player.vy > 0) {
      player.y = Math.floor((player.y + player.h) / TILE) * TILE - player.h;
      player.onGround = true;
    } else {
      player.y = Math.floor(player.y / TILE) * TILE + TILE;
    }
    player.vy = 0;
  } else if (player.vy > 0) {
    const row = oneWayRow(prevBottom);
    if (row !== -1) {
      player.y = row * TILE - player.h;
      player.vy = 0;
      player.onGround = true;
    }
  }
}
"""

_FN_GOAL = """
function respawn() {
  player.x = START.x;
  player.y = START.y;
  player.vx = 0;
  player.vy = 0;
}

function touches(ch) {
  const left = Math.floor(player.x / TILE);
  const right = Math.ceil((player.x + player.w) / TILE) - 1;
  const top = Math.floor(player.y / TILE);
  const bottom = Math.ceil((player.y + player.h) / TILE) - 1;
  for (let row = top; row <= bottom; row++) {
    for (let col = left; col <= right; col++) {
      if (tileAt(col, row) === ch) return true;
    }
  }
  return false;
}
"""

# ── Draw ─────────────────────────────────────────────────────────────
_DRAW_FLOOR = """  ctx.fillStyle = '#2d3748';
  ctx.fillRect(0, FLOOR, canvas.width, canvas.height - FLOOR);
"""

_DRAW_PLAYER = """  ctx.fillStyle = '#4fd1c5';
  ctx.fillRect(player.x, player.y, player.w, player.h);
"""

_DRAW_TILES = """  for (let row = 0; row < level.length; row++) {
    for (let col = 0; col < level[row].length; col++) {
      if (level[row][col] === '#') {
        ctx.fillStyle = '#4a5568';
        ctx.fillRect(col * TILE, row * TILE, TILE, TILE);
      }
    }
  }
"""

_DRAW_TILES_ONEWAY = """  for (let row = 0; row < level.length; row++) {
    for (let col = 0; col < level[row].length; col++) {
      const ch = level[row][col];
      if (ch === '#') {
        ctx.fillStyle = '#4a5568';
        ctx.fillRect(col * TILE, row * TILE, TILE, TILE);
      } else if (ch === '=') {
        ctx.fillStyle = '#a0aec0';
        ctx.fillRect(col * TILE, row * TILE, TILE, 8);
      }
    }
  }
"""

_DRAW_TILES_FLAG = """  for (let row = 0; row < level.length; row++) {
    for (let col = 0; col < level[row].length; col++) {
      const ch = level[row][col];
      if (ch === '#') {
        ctx.fillStyle = '#4a5568';
        ctx.fillRect(col * TILE, row * TILE, TILE, TILE);
      } else if (ch === '=') {
        ctx.fillStyle = '#a0aec0';
        ctx.fillRect(col * TILE, row * TILE, TILE, 8);
      } else if (ch === 'F') {
        ctx.fillStyle = '#fc8181';
        ctx.fillRect(col * TILE + 14, row * TILE, 4, TILE);
      }
    }
  }
"""

_DRAW_COINS = """  ctx.fillStyle = '#f6e05e';
  for (const c of coins) {
    if (c.taken) continue;
    ctx.beginPath();
    ctx.arc(c.x, c.y, 8, 0, Math.PI * 2);
    ctx.fill();
  }
"""

_HUD = """  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText(`Coins: ${score}`, 10, 20);
"""

_WIN_TEXT = """  if (state === 'won') {
    ctx.font = '32px monospace';
    ctx.fillText('You made it!', 140, 160);
  }
"""

_CAM_ON = "  ctx.save();\n  ctx.translate(-camera.x, 0);\n"
_CAM_OFF = "  ctx.restore();\n"


def _program(state: str, update: str, draw: str, extra: str = "") -> str:
    """One whole program: setup, the game's state, update, draw, the loop."""
    return (
        _SETUP + "\n" + state + extra
        + "\nfunction update(dt) {\n" + update + "}\n"
        + "\nfunction draw() {\n" + _BG + draw + "}\n"
        + _LOOP
    )


def _with_loop(code: str, loop: str) -> str:
    assert _LOOP in code
    return code.replace(_LOOP, loop)


_P0 = _program("", "", "")

_P1 = _program(
    _C_GRAVITY + _C_FLOOR + _PLAYER, _PHYS_FLOOR, _DRAW_FLOOR + _DRAW_PLAYER,
)
_P2 = _program(
    _C_GRAVITY + _C_FLOOR + _C_JUMP + _PLAYER, _JUMP + _PHYS_FLOOR,
    _DRAW_FLOOR + _DRAW_PLAYER, _KEYS,
)
_P3 = _program(
    _C_GRAVITY + _C_FLOOR + _C_JUMP + _C_RUN + _PLAYER,
    _JUMP + _RUN + _MOVE_FREE + _PHYS_FLOOR,
    _DRAW_FLOOR + _DRAW_PLAYER, _KEYS,
)
_P4 = _program(
    _C_GRAVITY + _C_FLOOR + _C_JUMP + _C_RUN + _C_TILE + _LEVEL + _PLAYER,
    _JUMP + _RUN + _MOVE_FREE + _PHYS_FLOOR,
    _DRAW_TILES + _DRAW_PLAYER, _KEYS,
)
_STATE_T = _C_GRAVITY + _C_JUMP + _C_RUN + _C_TILE + _LEVEL + _PLAYER
_P5 = _program(
    _STATE_T, _JUMP + _RUN + _MOVE_FREE + _CALL_Y,
    _DRAW_TILES + _DRAW_PLAYER, _KEYS + _FN_TILES + _FN_MOVEY,
)
_P6 = _program(
    _STATE_T, _JUMP + _RUN + _CALL_XY,
    _DRAW_TILES + _DRAW_PLAYER, _KEYS + _FN_TILES + _FN_MOVEX + _FN_MOVEY,
)
_STATE_F = _C_GRAVITY + _C_JUMP + _C_RUN + _C_TILE + _C_FALL + _LEVEL + _PLAYER
_P7 = _with_loop(
    _program(
        _STATE_F, _JUMP + _RUN + _CALL_XY,
        _DRAW_TILES + _DRAW_PLAYER,
        _KEYS + _FN_TILES + _FN_MOVEX + _FN_MOVEY_FALL,
    ),
    _LOOP_CAPPED,
)
_P8 = _with_loop(
    _program(
        _STATE_F, _JUMP + _RUN + _CALL_XY,
        _DRAW_TILES_ONEWAY + _DRAW_PLAYER,
        _KEYS + _FN_TILES + _FN_ONEWAY + _FN_MOVEX + _FN_MOVEY_ONEWAY,
    ),
    _LOOP_CAPPED,
)
_STATE_FEEL = _C_GRAVITY + _C_JUMP + _C_FEEL + _C_RUN + _C_TILE + _C_FALL + _LEVEL + _PLAYER_FEEL
_FNS = _KEYS + _FN_TILES + _FN_ONEWAY + _FN_MOVEX + _FN_MOVEY_ONEWAY
_P9 = _with_loop(
    _program(
        _STATE_FEEL, _JUMP_FEEL + _RUN + _CALL_XY,
        _DRAW_TILES_ONEWAY + _DRAW_PLAYER, _FNS,
    ),
    _LOOP_CAPPED,
)
_P10 = _with_loop(
    _program(
        _STATE_FEEL, _JUMP_FEEL + _RUN + _CALL_XY + _COIN_UPDATE,
        _DRAW_TILES_ONEWAY + _DRAW_COINS + _DRAW_PLAYER + _HUD,
        _FNS + _COINS,
    ),
    _LOOP_CAPPED,
)
_P11 = _with_loop(
    _program(
        _STATE_FEEL + _GOAL_STATE,
        _STOP + _JUMP_FEEL + _RUN + _CALL_XY + _COIN_UPDATE + _GOAL_UPDATE,
        _DRAW_TILES_FLAG + _DRAW_COINS + _DRAW_PLAYER + _HUD + _WIN_TEXT,
        _FNS + _COINS + _FN_GOAL,
    ),
    _LOOP_CAPPED,
)
_P12 = _with_loop(
    _program(
        _STATE_FEEL + _GOAL_STATE + _CAMERA_STATE,
        _STOP + _JUMP_FEEL + _RUN + _CALL_XY + _COIN_UPDATE + _GOAL_UPDATE + _CAMERA_UPDATE,
        _CAM_ON + _DRAW_TILES_FLAG + _DRAW_COINS + _DRAW_PLAYER + _CAM_OFF + _HUD + _WIN_TEXT,
        _FNS + _COINS + _FN_GOAL,
    ),
    _LOOP_CAPPED,
)

# The checks that need a level write their own into `level`, so they do not
# depend on the map the learner drew. clear() is open air over a solid floor
# (row 9, y 288); put() lays tiles in a row; place() drops the player somewhere.
_W = """
const W = level[0].length;
const open = ".".repeat(W);
const clear = () => {
  for (let r = 0; r < level.length; r++) level[r] = open;
  level[level.length - 1] = "#".repeat(W);
};
const put = (r, from, to, ch) => {
  level[r] = level[r].slice(0, from) + ch.repeat(to - from + 1) + level[r].slice(to + 1);
};
const place = (x, y) => {
  player.x = x;
  player.y = y;
  player.vx = 0;
  player.vy = 0;
};
const tap = (key) => {
  cc.press(key);
  cc.frames(1);
  cc.release(key);
};
"""

_STEP1_CHECK = """
expect(typeof player === "object" && player !== null && typeof player.vy === "number", "Make an object called player: const player = { x: 64, y: 0, w: 24, h: 30, vx: 0, vy: 0, onGround: false };");
player.y = 0;
player.vy = 0;
cc.frames(30);
expect(near(player.vy, 900, 25), `After half a second of falling, vy is ${Math.round(player.vy)}. Gravity is an acceleration - 1800 pixels a second, every second - so vy should be about 900. Each frame: player.vy += GRAVITY * dt.`);
expect(near(player.y, 225, 15), `After half a second the player is at y ${Math.round(player.y)}; it should have fallen to about 225. After changing vy, move y by player.vy * dt.`);
player.y = 0;
player.vy = 0;
cc.frames(15, 1000 / 30);
expect(near(player.vy, 900, 25), `The same half second at 30 frames a second gave vy ${Math.round(player.vy)}, not 900. Gravity has to be GRAVITY * dt: a slow screen then falls at the same speed, instead of getting a fixed nudge per frame.`);
cc.frames(120);
expect(near(player.y + player.h, 288, 0.5), `The player's feet are at y ${Math.round(player.y + player.h)}. It should land on the floor at y 288 and stay there: if the feet reach FLOOR, put them on it.`);
expect(near(player.vy, 0, 1) && player.onGround === true, "Standing on the floor, vy should be 0 and onGround true.");
player.y = 100;
player.vy = 0;
cc.frames(1);
expect(player.onGround === false, "In the air, onGround must be false. Set it to false every frame, then true only when the floor catches the player.");
expect(cc.rects().some((r) => near(r.x, player.x, 0.01) && near(r.y, player.y, 0.01) && r.w === player.w && r.h === player.h), "Draw the player every frame.");
"""

_STEP2_CHECK = """
const tap = (key) => {
  cc.press(key);
  cc.frames(1);
  cc.release(key);
};
cc.frames(90);
const y0 = player.y;
tap("ArrowUp");
expect(player.vy < -500, `Pressing ArrowUp on the ground should launch the player upward; vy is ${Math.round(player.vy)}. y grows downward, so an upward speed is negative: player.vy = -JUMP.`);
let top = player.y;
for (let i = 0; i < 120 && player.vy < 0; i++) {
  cc.frames(1);
  top = Math.min(top, player.y);
}
expect(near(y0 - top, 104, 12), `The jump rose ${Math.round(y0 - top)} pixels; with a take-off speed of 620 and gravity 1800 it should rise about 104.`);
cc.frames(120);
expect(player.onGround === true, "After a jump the player should land and be onGround again.");
tap(" ");
expect(player.vy < -500, "The space bar should jump too: check keys.has(' ') as well as keys.has('ArrowUp').");
cc.frames(120);
tap("ArrowUp");
cc.frames(10);
tap("ArrowUp");
expect(player.vy > -400, `The player jumped again in mid-air (vy is ${Math.round(player.vy)}). Only jump when player.onGround is true - and set it false when you take off.`);
cc.frames(120);
cc.frames(30);
expect(near(player.vy, 0, 1), "With no key pressed the player should stay on the floor.");
"""

_STEP3_CHECK = """
cc.frames(90);
player.x = 100;
player.vx = 0;
cc.press("ArrowRight");
cc.frames(6);
expect(near(player.vx, 160, 20), `After a tenth of a second of holding ArrowRight the speed is ${Math.round(player.vx)}. Running should build up (ACCEL = 1600 pixels a second per second, so about 160 here) rather than jump to top speed.`);
cc.frames(60);
expect(near(player.vx, 220, 0.5), `Held for a second, the speed is ${Math.round(player.vx)}. It should stop growing at MAX_SPEED, 220: clamp vx to between -220 and 220.`);
cc.release("ArrowRight");
cc.frames(1);
expect(player.vx > 100 && player.vx < 220, `One frame after letting go the speed is ${Math.round(player.vx)}. Friction should slow the player down over a moment, not stop or ignore it.`);
cc.frames(60);
expect(near(player.vx, 0, 0.5), `A second after letting go the speed is ${player.vx}. Friction should bring it to exactly 0 and stop there, not leave it creeping or push it backwards.`);
player.x = 300;
cc.press("ArrowLeft");
cc.frames(60);
expect(near(player.vx, -220, 0.5), `Held left for a second, the speed is ${Math.round(player.vx)}; it should be -220.`);
cc.release("ArrowLeft");
cc.frames(60);
expect(near(player.vx, 0, 0.5), "Friction should stop the player after running left as well.");
player.vx = 200;
cc.frames(6);
const sixtyFps = player.vx;
player.vx = 200;
cc.frames(3, 1000 / 30);
expect(near(sixtyFps, player.vx, 4), `A tenth of a second of friction left ${Math.round(sixtyFps)} at 60 frames a second but ${Math.round(player.vx)} at 30. Take away FRICTION * dt each frame - not a fixed fraction of the speed per frame, which depends on the frame rate.`);
"""

_STEP4_CHECK = """
expect(typeof TILE === "number" && TILE === 32, "Make const TILE = 32; one tile is 32 by 32 pixels.");
expect(Array.isArray(level) && level.length === 10 && level.every((r) => typeof r === "string"), "Make const level: an array of 10 strings, one for each row of tiles.");
expect(level.every((r) => r.length === level[0].length) && level[0].length >= 30, "Every row must be the same length, and at least 30 tiles wide (the canvas is only 15 tiles across).");
cc.frames(1);
const squares = cc.rects().filter((r) => r.w === TILE && r.h === TILE);
const drawnAt = new Set(squares.map((r) => r.x + "," + r.y));
let solids = 0;
for (let row = 0; row < level.length; row++) {
  for (let col = 0; col < level[row].length; col++) {
    if (level[row][col] !== "#") continue;
    solids++;
    expect(drawnAt.has(col * TILE + "," + row * TILE), `The '#' at column ${col}, row ${row} is not drawn at x ${col * TILE}, y ${row * TILE}. A tile's corner is column * TILE across and row * TILE down.`);
  }
}
expect(solids >= 20, "Put some solid tiles in the map: a floor of '#' along the bottom row, and a few more.");
expect(squares.length === solids, `The map has ${solids} '#' tiles but ${squares.length} tile-sized squares were drawn. Draw a square only where the map says '#'.`);
const was = level[2];
level[2] = was.slice(0, 5) + "#" + was.slice(6);
cc.frames(1);
expect(cc.rects().some((r) => r.x === 160 && r.y === 64 && r.w === TILE && r.h === TILE), "Draw from level every frame, so that changing the map changes the picture.");
level[2] = was;
"""

_STEP5_CHECK = _W + """
clear();
place(100, 0);
cc.frames(90);
expect(near(player.y + player.h, 288, 0.5) && player.onGround === true, `Dropped onto the floor row, the player's feet are at y ${Math.round(player.y + player.h)} (onGround ${player.onGround}). It should stand on the top of the floor tiles, y 288.`);
put(6, 2, 6, "#");
put(6, 8, 12, "#");
place(100, 0);
cc.frames(60);
expect(near(player.y + player.h, 192, 0.5) && player.onGround === true, `Over a platform of tiles the player's feet ended at y ${Math.round(player.y + player.h)}; it should land on top of it, at y 192 (row 6).`);
place(8 * 32 - 24, 0);
cc.frames(90);
expect(near(player.y + player.h, 288, 0.5), `The player fell right beside the platform, touching its edge but not over it, and stopped at y ${Math.round(player.y + player.h)}. A box that only touches a tile does not overlap it: take the last column from Math.ceil(right / TILE) - 1, not Math.floor.`);
clear();
put(5, 3, 4, "#");
place(100, 258);
cc.frames(10);
tap("ArrowUp");
let minY = player.y;
for (let i = 0; i < 60; i++) {
  cc.frames(1);
  minY = Math.min(minY, player.y);
}
expect(minY >= 192 - 0.01, `Jumping up into a tile overhead, the player's top reached y ${Math.round(minY)}, inside the tile (its underside is at y 192). Moving up into a tile should stop the head against it and set vy to 0.`);
expect(near(player.y + player.h, 288, 0.5), "After bumping its head the player should drop back to the floor.");
clear();
level[level.length - 1] = open;
place(100, 250);
cc.frames(30);
expect(player.y > 300, "The player is standing on thin air over a gap in the floor. The tiles are the floor now: take out the flat FLOOR line and let the map hold the player up.");
"""

_STEP6_CHECK = _W + """
clear();
put(6, 10, 10, "#");
put(7, 10, 10, "#");
put(8, 10, 10, "#");
place(200, 258);
cc.frames(20);
cc.press("ArrowRight");
cc.frames(90);
cc.release("ArrowRight");
expect(near(player.x + player.w, 320, 0.5), `Running right into a wall, the player's right edge ended at x ${Math.round(player.x + player.w)}. It should stop flush against the wall, at 320: move along x, and if that overlaps a tile put the edge on the tile's edge and zero vx.`);
expect(player.onGround === true && near(player.y + player.h, 288, 0.5), "Pressed against the wall, the player should still be standing on the floor. Standing on a tile is not touching it from the side.");
cc.press("ArrowLeft");
cc.frames(30);
cc.release("ArrowLeft");
expect(player.x < 250, "After touching the wall the player should be able to walk away from it again.");
place(296, 175);
cc.press("ArrowRight");
cc.frames(90);
cc.release("ArrowRight");
expect(player.x + player.w <= 320.01, "The player went into the wall.");
expect(near(player.y + player.h, 288, 0.5) && player.onGround === true, `Falling while pushing against the wall, the player ended at y ${Math.round(player.y + player.h)} instead of reaching the floor: it is stuck to the wall. Move and fix x on its own first, then move and fix y.`);
"""

_STEP7_CHECK = _W + """
clear();
put(6, 2, 8, "#");
place(100, 40);
cc.frames(3, 400);
cc.frames(120);
expect(player.onGround === true && near(player.y + player.h, 192, 0.5), `After three very long frames (a tab left in the background) the player's feet are at y ${Math.round(player.y + player.h)} - it fell straight through a one-tile platform. Cap dt at 1 / 30 so a long frame is still a short step.`);
clear();
level[level.length - 1] = open;
place(100, 0);
cc.frames(180);
expect(player.vy <= 901 && player.vy > 850, `After a long fall the speed is ${Math.round(player.vy)}. A fall should top out at MAX_FALL, 900 pixels a second: after gravity, vy = Math.min(vy, MAX_FALL).`);
clear();
place(100, 0);
cc.frames(120);
expect(player.onGround === true && near(player.y + player.h, 288, 0.5), "Normal play should work as before: the player should land on the floor.");
"""

_STEP8_CHECK = _W + """
clear();
put(7, 2, 8, "=");
place(100, 100);
cc.frames(60);
expect(player.onGround === true && near(player.y + player.h, 224, 0.5), `Dropped onto a '=' ledge from above, the player's feet are at y ${Math.round(player.y + player.h)}. It should land on top, at y 224 (row 7).`);
cc.frames(30);
expect(player.onGround === true && near(player.y + player.h, 224, 0.5), `Standing on the ledge for half a second, the player's feet are at y ${Math.round(player.y + player.h)}. The ledge should hold the player up: if the feet were at or above the top last frame and are past it now, land.`);
place(100, 258);
cc.frames(10);
tap("ArrowUp");
let lowest = 999;
for (let i = 0; i < 120; i++) {
  cc.frames(1);
  lowest = Math.min(lowest, player.y + player.h);
}
expect(lowest < 224 - 10, "Jumping from underneath the ledge, the player did not get above it: a '=' tile must let the player pass up through it.");
expect(player.onGround === true && near(player.y + player.h, 224, 0.5), `After jumping up through the ledge the player should land on top of it (feet at y 224); they are at y ${Math.round(player.y + player.h)}.`);
clear();
put(5, 2, 8, "=");
place(100, 258);
cc.frames(10);
tap("ArrowUp");
cc.frames(120);
expect(near(player.y + player.h, 288, 0.5), `A jump that peaks inside a ledge should not grab the player and lift them onto it: the feet were below its top last frame, so it must let them fall back to the floor (they are at y ${Math.round(player.y + player.h)}).`);
clear();
put(8, 9, 10, "=");
place(200, 258);
cc.frames(20);
cc.press("ArrowRight");
cc.frames(60);
cc.release("ArrowRight");
expect(player.x > 360, `A '=' tile at the player's own height must not block: only the walls ('#') do. The player stopped at x ${Math.round(player.x)}.`);
"""

_STEP9_CHECK = _W + """
expect(typeof player.coyote === "number", "Keep a timer on the player: coyote, in seconds.");
clear();
place(100, 258);
cc.frames(30);
const y1 = player.y;
tap("ArrowUp");
let tapTop = player.y;
for (let i = 0; i < 90 && player.vy < 0; i++) {
  cc.frames(1);
  tapTop = Math.min(tapTop, player.y);
}
expect(y1 - tapTop < 60, `A quick tap of the jump key rose ${Math.round(y1 - tapTop)} pixels. Letting go while still rising should cut the jump short: if the key is up and vy is faster than -JUMP_CUT, set vy to -JUMP_CUT.`);
cc.frames(120);
const y2 = player.y;
cc.press("ArrowUp");
let holdTop = player.y;
for (let i = 0; i < 40; i++) {
  cc.frames(1);
  holdTop = Math.min(holdTop, player.y);
}
cc.release("ArrowUp");
expect(y2 - holdTop > 90, `Holding the jump key rose only ${Math.round(y2 - holdTop)} pixels. A held key should still give the full jump, about 104.`);
const offLedge = () => {
  clear();
  level[level.length - 1] = "#".repeat(6) + ".".repeat(W - 6);
  place(140, 258);
  cc.frames(10);
  cc.press("ArrowRight");
  for (let n = 0; player.onGround && n < 120; n++) cc.frames(1);
  cc.release("ArrowRight");
};
offLedge();
expect(player.onGround === false, "The player should walk off the end of the floor and start to fall.");
cc.frames(3);
tap("ArrowUp");
expect(player.vy < -400, `The jump key was pressed 0.05 seconds after running off the ledge and nothing happened (vy ${Math.round(player.vy)}). Coyote time: keep a short timer, set to COYOTE (0.1) on the ground and counted down in the air, and allow the jump while it is above 0.`);
offLedge();
cc.frames(18);
tap("ArrowUp");
expect(player.vy > 0, `A jump 0.3 seconds after leaving the ledge should not work, but vy is ${Math.round(player.vy)}. The window is only a tenth of a second.`);
clear();
place(100, 258);
cc.frames(10);
tap("ArrowUp");
cc.frames(4);
tap("ArrowUp");
expect(player.vy > -540, `A second press in mid-air jumped again (vy ${Math.round(player.vy)}). Using up the coyote time - set it to 0 when you jump - stops a double jump.`);
"""

_STEP10_CHECK = _W + """
expect(Array.isArray(coins) && coins.length >= 3, "Make const coins = [] and fill it with a coin for each 'o' in the map (put at least three 'o' in your level).");
expect(typeof score === "number" && score === 0, "Start with let score = 0;");
cc.frames(1);
const total = coins.length;
expect(cc.arcs().length === total, `There are ${total} coins in the list but ${cc.arcs().length} circles drawn. Draw every coin that has not been collected, as a filled circle.`);
cc.frames(30);
expect(score === 0, `The score is ${score} without the player having touched a coin: collect only the ones the player overlaps.`);
const at = (c) => {
  player.x = c.x - player.w / 2;
  player.y = c.y - player.h / 2;
  player.vx = 0;
  player.vy = 0;
};
const a = coins[0];
const b = coins[1];
at(a);
cc.frames(1);
expect(score === 1, `The player is on top of a coin but the score is ${score}. Add 1 when the player overlaps a coin.`);
expect(cc.arcs().length === total - 1, "A collected coin should disappear: stop drawing it.");
cc.frames(10);
expect(score === 1, `The score is ${score}: a coin counts once. Mark it taken (or remove it) the moment it is collected.`);
at(b);
cc.frames(1);
expect(score === 2, `After a second coin the score is ${score}; it should be 2.`);
expect(cc.texts().some((t) => t.includes("2")), "Show the score on the screen - it should say 2 now.");
"""

_STEP11_CHECK = _W + """
expect(typeof state === "string" && state === "playing", "Keep what the game is doing in let state = 'playing';");
expect(typeof START === "object" && START !== null && typeof START.x === "number" && typeof START.y === "number", "Make const START = { x: 64, y: 258 }; where the player begins and comes back to.");
clear();
place(300, 258);
cc.frames(60);
expect(state === "playing" && near(player.x, 300, 1), "A player standing on the floor should not be sent back to the start.");
level[level.length - 1] = open;
place(300, 250);
let came = false;
for (let i = 0; i < 300 && !came; i++) {
  const before = player.y;
  cc.frames(1);
  if (player.y < before - 30) came = true;
}
expect(came, "The player fell out of the bottom of the world and never came back. When it is well below the canvas (y over canvas.height + 100), respawn it.");
expect(near(player.x, START.x, 1) && near(player.y, START.y, 1), `The respawn put the player at ${Math.round(player.x)}, ${Math.round(player.y)}; it should be at START (${START.x}, ${START.y}).`);
expect(near(player.vy, 0, 100), `The respawned player is still falling at ${Math.round(player.vy)}. Reset vx and vy to 0 as well as the position.`);
clear();
put(8, 10, 10, "F");
place(100, 258);
cc.frames(5);
expect(state === "playing", "The game is won only when the player touches the flag ('F').");
place(10 * 32 + 4, 258);
cc.frames(3);
expect(state === "won", `The player is standing in the flag's tile but state is '${state}'. When the player overlaps an 'F' tile, set state to 'won'.`);
expect(cc.texts().some((t) => /made it|win|goal/i.test(t)), "When the game is won, say so on the screen.");
const x0 = player.x;
cc.press("ArrowRight");
cc.frames(15);
cc.release("ArrowRight");
expect(near(player.x, x0, 0.01), "Once the game is won the player should stop moving: return from update when state is not 'playing'.");
"""

_STEP12_CHECK = _W + """
expect(typeof camera === "object" && camera !== null && typeof camera.x === "number", "Make const camera = { x: 0 }; how far along the level the screen is.");
const placed = () => {
  let dx = 0;
  const stack = [];
  const out = [];
  for (const c of cc.drawn()) {
    if (c.name === "save") stack.push(dx);
    else if (c.name === "restore") dx = stack.length ? stack.pop() : 0;
    else if (c.name === "translate") dx += c.args[0];
    else if (c.name === "fillRect") out.push({ kind: "rect", x: c.args[0] + dx, y: c.args[1], w: c.args[2], h: c.args[3] });
    else if (c.name === "fillText") out.push({ kind: "text", x: c.args[1] + dx, y: c.args[2], text: String(c.args[0]) });
  }
  return out;
};
clear();
place(64, 258);
cc.frames(2);
expect(near(camera.x, 0, 0.5), `At the left end of the level the camera is at ${Math.round(camera.x)}. It should stop at 0 rather than scroll into empty space.`);
place(468, 258);
cc.frames(2);
expect(near(camera.x, 240, 3), `With the player in the middle of the level the camera is at ${Math.round(camera.x)}. Put the player's centre in the middle of the screen: camera.x = player.x + player.w / 2 - canvas.width / 2.`);
const me = placed().find((r) => r.kind === "rect" && r.w === player.w && r.h === player.h);
expect(me && near(me.x, player.x - camera.x, 1), `The player is drawn at screen x ${me ? Math.round(me.x) : "nowhere"}; it should be at player.x - camera.x, ${Math.round(player.x - camera.x)}. Shift everything you draw left by the camera: ctx.translate(-camera.x, 0).`);
expect(placed().some((r) => r.kind === "rect" && r.w === TILE && r.h === TILE && near(r.y, 288, 0.01) && near(r.x, 640 - camera.x, 0.5)), "The tiles should scroll with the camera too: a floor tile in column 20 should be drawn at 640 - camera.x.");
place(900, 258);
cc.frames(2);
expect(near(camera.x, level[0].length * TILE - canvas.width, 0.5), `At the right end of the level the camera is at ${Math.round(camera.x)}; it should stop at the level's width minus the canvas's, ${level[0].length * TILE - canvas.width}.`);
const off = placed().filter((t) => t.kind === "text" && (t.x < -1 || t.x > canvas.width));
expect(off.length === 0, "The score is drawn off the screen when the camera has scrolled. Text for the player to read goes after ctx.restore(), so it stays put.");
"""


PLATFORMER_STEPS: tuple[Step, ...] = (
    Step(
        id="plat-01-gravity",
        track="Platformer",
        title="Gravity pulls",
        teaches=(
            "Gravity is not a speed, it is an acceleration: it changes the "
            "speed, every second, by the same amount. So each frame does two "
            "things in this order: vy += GRAVITY * dt, then y += vy * dt. "
            "Multiply by dt both times and the fall takes the same real time "
            "on any screen. Leave dt off the first and a 30 frames a second "
            "screen falls at half the pull of a 60 one. A floor is just a "
            "line the feet may not cross: when they do, put them on it, "
            "zero vy, and note that the player is standing (onGround)."
        ),
        goal="Add GRAVITY = 1800, FLOOR = 288 and const player = { x: 64, y: 0, w: 24, h: 30, vx: 0, vy: 0, onGround: false }. Pull the player down with gravity, stop its feet on the floor, set onGround, and draw both.",
        starter=_P0,
        solution=_P1,
        check=_STEP1_CHECK,
        hint="vy += GRAVITY * dt; y += vy * dt; onGround = false; then if y + h >= FLOOR: y = FLOOR - h, vy = 0, onGround = true.",
    ),
    Step(
        id="plat-02-jump",
        track="Platformer",
        title="Jump from the ground only",
        teaches=(
            "A jump is a single instant: set vy to a big upward number "
            "(negative, because y grows downwards) and let gravity do the "
            "rest. It rises while vy is negative, slows, turns, and comes "
            "down on its own. The height is JUMP squared over twice "
            "gravity, so 620 gives about 100 pixels. The rule that makes "
            "it a platformer: only jump while onGround. Without it, holding "
            "the key flies. When you take off, say you are no longer on the "
            "ground, so the next frame cannot jump again."
        ),
        goal="Add JUMP = 620 and a keys Set. When ArrowUp or the space bar is held and the player is onGround, set vy to -JUMP.",
        starter=_P1,
        solution=_P2,
        check=_STEP2_CHECK,
        hint="if ((keys.has('ArrowUp') || keys.has(' ')) && player.onGround) { player.vy = -JUMP; player.onGround = false; }",
    ),
    Step(
        id="plat-03-run",
        track="Platformer",
        title="Running with momentum",
        teaches=(
            "Setting vx straight to a speed feels like a cursor. Real "
            "running has weight: holding a direction ACCELERATES vx "
            "(vx += dir * ACCEL * dt), letting go lets friction take speed "
            "away (also times dt), and a clamp stops it at MAX_SPEED. "
            "Friction must stop at zero: subtract it, but never let it push "
            "vx past 0 or the player shuffles backwards forever. Do not "
            "multiply vx by 0.9 each frame: that is a different friction "
            "at every frame rate. Then x += vx * dt, as always."
        ),
        goal="Add ACCEL = 1600, FRICTION = 1400, MAX_SPEED = 220. Arrow keys accelerate vx, no key slows it to exactly 0, vx stays within the maximum, and x moves by vx * dt.",
        starter=_P2,
        solution=_P3,
        check=_STEP3_CHECK,
        hint="dir is -1, 0 or 1. If dir, vx += dir * ACCEL * dt; else vx = Math.max(0, vx - FRICTION * dt) (and the mirror for negative); then clamp.",
    ),
    Step(
        id="plat-04-tilemap",
        track="Platformer",
        title="A level made of strings",
        teaches=(
            "A level is not a list of rectangles you type out; it is a grid "
            "you can SEE in the code. An array of strings, one per row, one "
            "character per tile: '#' solid, '.' air. level[row][col] reads a "
            "tile, and a tile's pixel position is col * TILE across and row "
            "* TILE down. Draw the map by looping over rows and columns, "
            "reading it live each frame, so editing the map edits the game. "
            "Add more symbols as you need them: '=' for ledges, 'o' for "
            "coins, 'F' for the flag. For now only '#' is drawn."
        ),
        goal="Add const TILE = 32 and const level: 10 strings of at least 30 characters, '#' for solid and '.' for air, with a floor along the bottom row. Draw a square for every '#' instead of the old flat floor.",
        starter=_P3,
        solution=_P4,
        check=_STEP4_CHECK,
        hint="for (let row ...) for (let col ...) if (level[row][col] === '#') ctx.fillRect(col * TILE, row * TILE, TILE, TILE);",
    ),
    Step(
        id="plat-05-floor",
        track="Platformer",
        title="Land on tiles",
        teaches=(
            "To collide with a grid you do not test the player against every "
            "tile: you work out which tiles the player's box covers. Left "
            "column is floor(x / TILE); the right one is ceil((x + w) / "
            "TILE) - 1, the -1 because a box ending exactly on a tile "
            "boundary does not touch the next tile. Same for rows. Then "
            "move on one axis and, if it now overlaps a solid tile, put it "
            "back on the edge: falling, the feet go on the top of the tile "
            "(onGround); rising, the head goes under it. Zero vy either way. "
            "Tiles are the floor now, so the FLOOR constant goes."
        ),
        goal="Replace FLOOR with tiles. Write tileAt, solidAt and overlapsSolid, then moveY(dt): gravity, move y, and if it overlaps a solid tile put the feet on top (onGround) or the head underneath, and zero vy.",
        starter=_P4,
        solution=_P5,
        check=_STEP5_CHECK,
        hint="After y += vy * dt: if (overlapsSolid()) { if (vy > 0) { y = Math.floor((y + h) / TILE) * TILE - h; onGround = true; } else { y = Math.floor(y / TILE) * TILE + TILE; } vy = 0; }",
    ),
    Step(
        id="plat-06-walls",
        track="Platformer",
        title="Walls: one axis at a time",
        teaches=(
            "Moving sideways collides with tiles too, but do not move x and "
            "y together and then try to untangle the overlap: you cannot "
            "tell which way you hit the tile, and the player snags on "
            "corners or sticks to walls it is only brushing. Move on ONE "
            "axis, fix that axis, then do the other. x first: move, and if "
            "it overlaps a tile put the edge back flush (the right edge on "
            "the tile's left side, or the left edge on its right) and zero "
            "vx. Then y as before. Each test then only has one thing it "
            "could mean."
        ),
        goal="Add moveX(dt): move x by vx * dt and if that overlaps a solid tile put the player flush against it and zero vx. Each frame call moveX then moveY.",
        starter=_P5,
        solution=_P6,
        check=_STEP6_CHECK,
        hint="Same shape as moveY: x += vx * dt; if (overlapsSolid()) { if (vx > 0) x = Math.floor((x + w) / TILE) * TILE - w; else x = Math.floor(x / TILE) * TILE + TILE; vx = 0; }",
    ),
    Step(
        id="plat-07-fast",
        track="Platformer",
        title="Nothing tunnels",
        teaches=(
            "Collision only looks at where the player ends up each frame. "
            "If a frame moves it further than a tile is thick, it lands "
            "past the tile and never notices: tunnelling. It happens "
            "when the browser stalls (a hidden tab can deliver a 400 ms "
            "frame) or when something is simply fast. Two cheap fixes: cap "
            "dt so no frame is ever long, Math.min(dt, 1 / 30), and cap the "
            "fall speed (terminal velocity, 900 here) so one frame is at "
            "most a few tiles. Real games also split a frame into smaller "
            "steps; for tiles this big, the caps are enough."
        ),
        goal="Cap dt at 1 / 30 in the loop, and add MAX_FALL = 900: after gravity, vy is never more than that.",
        starter=_P6,
        solution=_P7,
        check=_STEP7_CHECK,
        hint="In loop: const dt = Math.min((time - last) / 1000, 1 / 30); in moveY, after gravity: player.vy = Math.min(player.vy, MAX_FALL);",
    ),
    Step(
        id="plat-08-oneway",
        track="Platformer",
        title="One-way ledges",
        teaches=(
            "A '=' ledge is solid from above only: jump up through it, land "
            "on it. So it is not in solidAt, and it is not a wall. It "
            "catches the player on the way DOWN, and only if the feet were "
            "at or above its top on the previous frame: prevBottom <= "
            "top. Without that, a jump that peaks inside the ledge would "
            "snap the player up onto it. Use <=, not <: a player already "
            "standing has its feet exactly at the top, and with < the "
            "ledge lets go of them the next frame and they fall through."
        ),
        goal="Make '=' tiles one-way: no blocking from the side or below, but landing on one when moving down with the feet at or above its top last frame. Draw them as a thin bar.",
        starter=_P7,
        solution=_P8,
        check=_STEP8_CHECK,
        hint="Remember prevBottom = y + h before moving. After the solid test, else if vy > 0: find the row the feet are in, and if prevBottom <= row * TILE and that tile is '=', stand on it.",
    ),
    Step(
        id="plat-09-feel",
        track="Platformer",
        title="A jump that forgives",
        teaches=(
            "Two small things separate a platformer that feels fair from "
            "one that feels cheap. Coyote time: for a tenth of a second "
            "after running off a ledge you can still jump, because people "
            "press a hair late. Keep a timer, refill it to COYOTE while "
            "onGround, count it down in the air, and jump while it is above "
            "0 - and set it to 0 on the jump, or you get a double jump. "
            "Variable height: let go of the key while rising and the jump "
            "is cut short (vy limited to -JUMP_CUT). Tap for a hop, hold "
            "for the full height."
        ),
        goal="Add COYOTE = 0.1, JUMP_CUT = 200 and player.coyote. Allow a jump while coyote is above 0 (and use it up), and when the jump key is up and vy is faster than -JUMP_CUT, set vy to -JUMP_CUT.",
        starter=_P8,
        solution=_P9,
        check=_STEP9_CHECK,
        hint="onGround ? coyote = COYOTE : coyote -= dt. Jump if held && coyote > 0, then coyote = 0. If !held && vy < -JUMP_CUT, vy = -JUMP_CUT.",
    ),
    Step(
        id="plat-10-coins",
        track="Platformer",
        title="Coins",
        teaches=(
            "The map already says where things are, so build the coins "
            "from it: loop over the level once at the start, and for every "
            "'o' push a coin object at the middle of that tile (col * TILE "
            "+ TILE / 2). The map then keeps being the level's whole "
            "description. Each frame, for every coin not yet taken, test it "
            "against the player's box; on a hit mark it taken and add to "
            "the score. The taken flag is what makes a coin count once: "
            "without it you would collect it again on every frame you "
            "stand in it, sixty times a second."
        ),
        goal="Put at least three 'o' in your map. Build const coins from them ({ x, y, taken: false } at each tile's middle), let score = 0; collect a coin the player overlaps (once), draw the others as circles, and show the score.",
        starter=_P9,
        solution=_P10,
        check=_STEP10_CHECK,
        hint="Collect when Math.abs(c.x - centreX) < 8 + player.w / 2 and the same for y. Then c.taken = true; score += 1. Draw only if !c.taken.",
    ),
    Step(
        id="plat-11-goal",
        track="Platformer",
        title="A flag, and starting over",
        teaches=(
            "A game needs an end and a way back. The flag is one more map "
            "symbol, 'F': ask whether the player's box covers a tile with "
            "that character, and set state to 'won'. Falling out of the "
            "world is the other: the map has a pit, and below the bottom "
            "there is nothing to land on, so when the player is far below "
            "the canvas put it back at START. Reset the speed as well as "
            "the position, or it arrives still falling at full speed. "
            "Both are decided at the end of update, and once the game is "
            "won update does nothing."
        ),
        goal="Add const START = { x: 64, y: 258 } and let state = 'playing'. Below canvas.height + 100, respawn at START with no speed. Touching an 'F' tile sets state to 'won', stops the game, and says 'You made it!'.",
        starter=_P10,
        solution=_P11,
        check=_STEP11_CHECK,
        hint="touches(ch) loops over the tiles the player covers, like overlapsSolid. At the end of update: if (player.y > canvas.height + 100) respawn(); if (touches('F')) state = 'won';",
    ),
    Step(
        id="plat-12-camera",
        track="Platformer",
        title="A camera",
        teaches=(
            "The level is twice as wide as the screen, so something has to "
            "decide which part you see. That is the camera: one number, "
            "how far along the level the left edge of the screen is. Aim "
            "it so the player's CENTRE is in the middle of the screen "
            "(player.x + player.w / 2 - canvas.width / 2) and clamp it to "
            "0 and the level's width minus the screen's, so it never shows "
            "past the ends. To draw, shift the whole world left by the "
            "camera: ctx.save(), ctx.translate(-camera.x, 0), draw, "
            "ctx.restore(). The score is not part of the world: draw it "
            "after the restore."
        ),
        goal="Add const camera = { x: 0 } following the player's centre, clamped to the level. Draw the tiles, coins and player translated by -camera.x, and the text after ctx.restore().",
        starter=_P11,
        solution=_P12,
        check=_STEP12_CHECK,
        hint="camera.x = Math.max(0, Math.min(level[0].length * TILE - canvas.width, player.x + player.w / 2 - canvas.width / 2)); ctx.translate(-camera.x, 0);",
    ),
    Step(
        id="plat-13-yours",
        track="Platformer",
        title="Now it's yours",
        teaches=(
            "A whole platformer, and every part of it is something you "
            "can change. Ideas, easier first: more levels as more arrays "
            "of strings, switched when you reach the flag; a timer; "
            "spikes ('^') that respawn you; holding Down to drop through "
            "a ledge; a double jump; a jump buffer (a press just BEFORE "
            "landing still counts); enemies that walk back and forth and "
            "turn at walls; moving platforms; a camera that eases toward "
            "the player instead of locking to it."
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_P12,
        solution=_P12,
        check="",
    ),
)
