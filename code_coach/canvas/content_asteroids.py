"""A Canvas track after Platformer: Asteroids.

The other tracks moved things in straight lines along x and y. Asteroids is
the one about angles: a ship has a heading, in radians, and everything that
follows is cos and sin of it - thrust pushes along the heading, a bullet
leaves along it, a drawing is turned by it. On top of that sit the pieces
that make it feel like space: velocity that keeps going when you let go,
friction that does not depend on the frame rate, a screen that wraps round
on every edge, a gun with a cooldown, bullets that expire, rocks that drift
and spin, circle against circle collision, rocks that split in two, lives
with a short invulnerability, and a game over you can restart from.

Same rules as the others: each step's starter is the step before,
finished; a check plays the program (keys held, frames stepped) and never
reads it. The checks build their own situations by writing into the
top-level names the goals list (ship, bullets, rocks, score, lives, state).
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

_BG = """  ctx.fillStyle = '#080b14';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
"""

# ── State ────────────────────────────────────────────────────────────
_SHIP = "const ship = { x: 240, y: 160, angle: -Math.PI / 2, vx: 0, vy: 0, r: 12 };\n"
_SHIP_LIVES = (
    "const ship = { x: 240, y: 160, angle: -Math.PI / 2, vx: 0, vy: 0, r: 12, invuln: 0 };\n"
)
_C_TURN = "const TURN = 4;\n"
_C_THRUST = "const THRUST = 160;\n"
_C_DRAG = "const DRAG = 0.5;\n"
_C_BULLETS_FIRST = "const BULLET_SPEED = 360;\nconst bullets = [];\n"
_C_GUN = (
    "const BULLET_SPEED = 360;\nconst BULLET_LIFE = 1;\nconst COOLDOWN = 0.25;\n"
    "let cooldown = 0;\nconst bullets = [];\n"
)
_C_ROCKS = "const rocks = [];\n"
_C_SCORE = "const POINTS = { 1: 100, 2: 50, 3: 20 };\nlet score = 0;\n"
_C_LIVES = "const INVULN = 2;\nlet lives = 3;\n"
_C_STATE = "let state = 'playing';\n"

_KEYS = """
const keys = new Set();
addEventListener('keydown', (e) => keys.add(e.key));
addEventListener('keyup', (e) => keys.delete(e.key));
"""

# ── Update ───────────────────────────────────────────────────────────
_GUARD = "  if (state !== 'playing') return;\n"

_U_TURN = """  const turn = (keys.has('ArrowRight') ? 1 : 0) - (keys.has('ArrowLeft') ? 1 : 0);
  ship.angle += turn * TURN * dt;
"""

_U_THRUST = """  if (keys.has('ArrowUp')) {
    ship.vx += Math.cos(ship.angle) * THRUST * dt;
    ship.vy += Math.sin(ship.angle) * THRUST * dt;
  }
"""

_U_DRAG = """  const damp = Math.pow(DRAG, dt);
  ship.vx *= damp;
  ship.vy *= damp;
"""

_U_MOVE = """  ship.x += ship.vx * dt;
  ship.y += ship.vy * dt;
"""

_U_WRAP = "  wrap(ship);\n"

_U_BULLETS_FIRST = """  for (const b of bullets) {
    b.x += b.vx * dt;
    b.y += b.vy * dt;
    wrap(b);
  }
"""

_U_GUN = """  if (cooldown > 0) cooldown -= dt;
  if (keys.has(' ') && cooldown <= 0) {
    fire();
    cooldown = COOLDOWN;
  }
"""

_U_BULLETS = """  for (const b of bullets) {
    b.x += b.vx * dt;
    b.y += b.vy * dt;
    b.life -= dt;
    wrap(b);
  }
  for (let i = bullets.length - 1; i >= 0; i--) {
    if (bullets[i].life <= 0) bullets.splice(i, 1);
  }
"""

_U_ROCKS = """  for (const rk of rocks) {
    rk.x += rk.vx * dt;
    rk.y += rk.vy * dt;
    rk.angle += rk.spin * dt;
    wrap(rk);
  }
"""

_U_HIT = "  hitRocks();\n"

_U_SHIP_HIT = """  if (ship.invuln > 0) ship.invuln -= dt;
  if (ship.invuln <= 0 && rocks.some((rk) => overlap(ship, rk))) loseLife();
"""

# ── Functions ────────────────────────────────────────────────────────
_FN_DRAW_SHIP = """
function drawShip() {
  ctx.save();
  ctx.translate(ship.x, ship.y);
  ctx.rotate(ship.angle);
  ctx.strokeStyle = '#e2e8f0';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(ship.r, 0);
  ctx.lineTo(-ship.r, -ship.r * 0.7);
  ctx.lineTo(-ship.r * 0.5, 0);
  ctx.lineTo(-ship.r, ship.r * 0.7);
  ctx.closePath();
  ctx.stroke();
  ctx.restore();
}
"""

_FN_WRAP = """
function wrap(o) {
  if (o.x < -o.r) o.x = canvas.width + o.r;
  else if (o.x > canvas.width + o.r) o.x = -o.r;
  if (o.y < -o.r) o.y = canvas.height + o.r;
  else if (o.y > canvas.height + o.r) o.y = -o.r;
}
"""

_FN_FIRE_FIRST = """
function fire() {
  const c = Math.cos(ship.angle);
  const s = Math.sin(ship.angle);
  bullets.push({
    x: ship.x + c * ship.r,
    y: ship.y + s * ship.r,
    vx: ship.vx + c * BULLET_SPEED,
    vy: ship.vy + s * BULLET_SPEED,
    r: 2,
  });
}

addEventListener('keydown', (e) => {
  if (e.key === ' ') fire();
});
"""

_FN_FIRE = """
function fire() {
  const c = Math.cos(ship.angle);
  const s = Math.sin(ship.angle);
  bullets.push({
    x: ship.x + c * ship.r,
    y: ship.y + s * ship.r,
    vx: ship.vx + c * BULLET_SPEED,
    vy: ship.vy + s * BULLET_SPEED,
    r: 2,
    life: BULLET_LIFE,
  });
}
"""

_FN_ROCKS = """
function makeRock(x, y, size) {
  const heading = Math.random() * Math.PI * 2;
  const speed = 20 + Math.random() * 40;
  const shape = [];
  for (let i = 0; i < 10; i++) shape.push(0.75 + Math.random() * 0.45);
  return {
    x,
    y,
    vx: Math.cos(heading) * speed,
    vy: Math.sin(heading) * speed,
    angle: Math.random() * Math.PI * 2,
    spin: (Math.random() - 0.5) * 2,
    size,
    r: size * 14,
    shape,
  };
}

function spawnRocks(n) {
  for (let i = 0; i < n; i++) {
    let x, y;
    do {
      x = Math.random() * canvas.width;
      y = Math.random() * canvas.height;
    } while (Math.hypot(x - ship.x, y - ship.y) < 120);
    rocks.push(makeRock(x, y, 2 + Math.floor(Math.random() * 2)));
  }
}
spawnRocks(4);
"""

_FN_OVERLAP = """
function overlap(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y) < a.r + b.r;
}
"""

_FN_HIT_SHOOT = _FN_OVERLAP + """
function hitRocks() {
  for (let i = bullets.length - 1; i >= 0; i--) {
    for (let j = rocks.length - 1; j >= 0; j--) {
      if (overlap(bullets[i], rocks[j])) {
        score += POINTS[rocks[j].size];
        rocks.splice(j, 1);
        bullets.splice(i, 1);
        break;
      }
    }
  }
}
"""

_FN_HIT_SPLIT = _FN_OVERLAP + """
function breakRock(j) {
  const rk = rocks[j];
  rocks.splice(j, 1);
  if (rk.size > 1) {
    rocks.push(makeRock(rk.x, rk.y, rk.size - 1));
    rocks.push(makeRock(rk.x, rk.y, rk.size - 1));
  }
}

function hitRocks() {
  for (let i = bullets.length - 1; i >= 0; i--) {
    for (let j = rocks.length - 1; j >= 0; j--) {
      if (overlap(bullets[i], rocks[j])) {
        score += POINTS[rocks[j].size];
        breakRock(j);
        bullets.splice(i, 1);
        break;
      }
    }
  }
}
"""

_FN_LOSE_LIFE = """
function loseLife() {
  lives -= 1;
  ship.x = canvas.width / 2;
  ship.y = canvas.height / 2;
  ship.vx = 0;
  ship.vy = 0;
  ship.angle = -Math.PI / 2;
  ship.invuln = INVULN;
}
"""

_FN_LOSE_LIFE_OVER = """
function loseLife() {
  lives -= 1;
  if (lives <= 0) {
    state = 'over';
    return;
  }
  ship.x = canvas.width / 2;
  ship.y = canvas.height / 2;
  ship.vx = 0;
  ship.vy = 0;
  ship.angle = -Math.PI / 2;
  ship.invuln = INVULN;
}

function reset() {
  ship.x = canvas.width / 2;
  ship.y = canvas.height / 2;
  ship.vx = 0;
  ship.vy = 0;
  ship.angle = -Math.PI / 2;
  ship.invuln = 0;
  cooldown = 0;
  bullets.length = 0;
  rocks.length = 0;
  spawnRocks(4);
  score = 0;
  lives = 3;
  state = 'playing';
}

addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && state === 'over') reset();
});
"""

# ── Draw ─────────────────────────────────────────────────────────────
_D_SHIP = "  drawShip();\n"
_D_SHIP_BLINK = (
    "  if (ship.invuln <= 0 || Math.floor(ship.invuln * 10) % 2 === 0) drawShip();\n"
)

_D_BULLETS = """  ctx.fillStyle = '#fbd38d';
  for (const b of bullets) {
    ctx.beginPath();
    ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
    ctx.fill();
  }
"""

_D_ROCKS = """  ctx.strokeStyle = '#a0aec0';
  ctx.lineWidth = 2;
  for (const rk of rocks) {
    ctx.save();
    ctx.translate(rk.x, rk.y);
    ctx.rotate(rk.angle);
    ctx.beginPath();
    rk.shape.forEach((k, i) => {
      const a = (i / rk.shape.length) * Math.PI * 2;
      const px = Math.cos(a) * rk.r * k;
      const py = Math.sin(a) * rk.r * k;
      if (i === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    });
    ctx.closePath();
    ctx.stroke();
    ctx.restore();
  }
"""

_D_SCORE = """  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText(`Score: ${score}`, 10, 20);
"""

_D_LIVES = "  ctx.fillText(`Lives: ${lives}`, 10, 40);\n"

_D_OVER = """  if (state === 'over') {
    ctx.fillStyle = 'white';
    ctx.font = '32px monospace';
    ctx.fillText('Game over', 150, 150);
    ctx.font = '16px monospace';
    ctx.fillText(`Score: ${score} - Enter to play again`, 110, 180);
  }
"""


def _program(state: str, update: str, draw: str, extra: str = "") -> str:
    """One whole program: setup, the game's state, update, draw, the loop."""
    return (
        _SETUP + "\n" + state + extra
        + "\nfunction update(dt) {\n" + update + "}\n"
        + "\nfunction draw() {\n" + _BG + draw + "}\n"
        + _LOOP
    )


_STATE1 = _SHIP + _C_TURN
_STATE2 = _STATE1 + _C_THRUST
_STATE3 = _STATE2 + _C_DRAG
_STATE5 = _STATE3 + _C_BULLETS_FIRST
_STATE6 = _STATE3 + _C_GUN
_STATE7 = _STATE6 + _C_ROCKS
_STATE8 = _STATE7 + _C_SCORE
_STATE10 = _STATE8.replace(_SHIP, _SHIP_LIVES) + _C_LIVES
_STATE11 = _STATE10 + _C_STATE

_SHIP_UPDATE_1 = _U_TURN
_SHIP_UPDATE_2 = _U_TURN + _U_THRUST + _U_MOVE
_SHIP_UPDATE_3 = _U_TURN + _U_THRUST + _U_DRAG + _U_MOVE
_SHIP_UPDATE_4 = _SHIP_UPDATE_3 + _U_WRAP

_P0 = _program("", "", "")
_P1 = _program(_STATE1, _SHIP_UPDATE_1, _D_SHIP, _KEYS + _FN_DRAW_SHIP)
_P2 = _program(_STATE2, _SHIP_UPDATE_2, _D_SHIP, _KEYS + _FN_DRAW_SHIP)
_P3 = _program(_STATE3, _SHIP_UPDATE_3, _D_SHIP, _KEYS + _FN_DRAW_SHIP)
_P4 = _program(_STATE3, _SHIP_UPDATE_4, _D_SHIP, _KEYS + _FN_DRAW_SHIP + _FN_WRAP)
_P5 = _program(
    _STATE5, _SHIP_UPDATE_4 + _U_BULLETS_FIRST, _D_BULLETS + _D_SHIP,
    _KEYS + _FN_DRAW_SHIP + _FN_WRAP + _FN_FIRE_FIRST,
)
_P6 = _program(
    _STATE6, _SHIP_UPDATE_4 + _U_GUN + _U_BULLETS, _D_BULLETS + _D_SHIP,
    _KEYS + _FN_DRAW_SHIP + _FN_WRAP + _FN_FIRE,
)
_UPDATE_7 = _SHIP_UPDATE_4 + _U_GUN + _U_BULLETS + _U_ROCKS
_EXTRA_7 = _KEYS + _FN_DRAW_SHIP + _FN_WRAP + _FN_FIRE + _FN_ROCKS
_P7 = _program(_STATE7, _UPDATE_7, _D_ROCKS + _D_BULLETS + _D_SHIP, _EXTRA_7)
_P8 = _program(
    _STATE8, _UPDATE_7 + _U_HIT, _D_ROCKS + _D_BULLETS + _D_SHIP + _D_SCORE,
    _EXTRA_7 + _FN_HIT_SHOOT,
)
_P9 = _program(
    _STATE8, _UPDATE_7 + _U_HIT, _D_ROCKS + _D_BULLETS + _D_SHIP + _D_SCORE,
    _EXTRA_7 + _FN_HIT_SPLIT,
)
_P10 = _program(
    _STATE10, _UPDATE_7 + _U_HIT + _U_SHIP_HIT,
    _D_ROCKS + _D_BULLETS + _D_SHIP_BLINK + _D_SCORE + _D_LIVES,
    _EXTRA_7 + _FN_HIT_SPLIT + _FN_LOSE_LIFE,
)
_P11 = _program(
    _STATE11, _GUARD + _UPDATE_7 + _U_HIT + _U_SHIP_HIT,
    _D_ROCKS + _D_BULLETS + _D_SHIP_BLINK + _D_SCORE + _D_LIVES + _D_OVER,
    _EXTRA_7 + _FN_HIT_SPLIT + _FN_LOSE_LIFE_OVER,
)

# Shared by the checks. They build their own situations by writing into the
# learner's top-level names, so they do not depend on where the game put things.
_H = """
const stage = (x = 240, y = 160, angle = 0) => {
  ship.x = x;
  ship.y = y;
  ship.vx = 0;
  ship.vy = 0;
  ship.angle = angle;
  if (typeof state !== "undefined") state = "playing";
  if (typeof bullets !== "undefined") bullets.length = 0;
  if (typeof rocks !== "undefined") rocks.length = 0;
  if (typeof ship.invuln === "number") ship.invuln = 0;
};
const speed = () => Math.hypot(ship.vx, ship.vy);
const rock = (x, y, size) => {
  const rk = makeRock(x, y, size);
  rk.vx = 0;
  rk.vy = 0;
  rk.spin = 0;
  rk.angle = 0.5;
  rocks.push(rk);
  return rk;
};
const shoot = () => {
  cc.frames(20);
  bullets.length = 0;
  cc.press(" ");
  cc.frames(1);
  cc.release(" ");
  expect(bullets.length >= 1, "Holding Space should put a bullet into the bullets array.");
  const b = bullets[bullets.length - 1];
  b.vx = 0;
  b.vy = 0;
  return b;
};
"""


ASTEROIDS_STEPS: tuple[Step, ...] = (
    Step(
        id="ast-01-turn",
        track="Asteroids",
        title="A ship that turns",
        teaches=(
            "Asteroids is a game about angles. The ship does not have a "
            "'left' and a 'right' velocity - it has a heading, one number "
            "in radians: 0 points right, and because y grows downwards, a "
            "positive angle turns clockwise and straight up is -Math.PI / "
            "2. A full circle is 2 * Math.PI, about 6.28, so 'turn 4 a "
            "second' means about two thirds of a circle. Never degrees: "
            "Math.cos, Math.sin and ctx.rotate all want radians. To draw a "
            "turned ship, move the origin to the ship with ctx.translate "
            "and then ctx.rotate by the heading; draw the nose along +x and "
            "the rest follows. Wrap it in ctx.save() and ctx.restore() so "
            "the turn does not leak into everything drawn afterwards."
        ),
        goal="Make const ship = { x: 240, y: 160, angle: -Math.PI / 2, vx: 0, vy: 0, r: 12 } and const TURN = 4. Draw it each frame as a triangle: ctx.translate(ship.x, ship.y), ctx.rotate(ship.angle), nose along +x. ArrowRight turns it clockwise and ArrowLeft anticlockwise at TURN radians a second. The check reads ship.",
        starter=_P0,
        solution=_P1,
        check=_H + """
expect(typeof ship === "object" && ship !== null, "Make const ship = { x, y, angle, vx, vy, r } to hold the ship.");
expect(near(ship.x, 240, 1) && near(ship.y, 160, 1), "The ship starts in the middle of the canvas: x 240, y 160.");
expect(typeof ship.angle === "number" && near(Math.cos(ship.angle), 0, 0.02) && near(Math.sin(ship.angle), -1, 0.02), "The ship starts pointing up. Angles are in radians, 0 points right and y grows downwards, so up is -Math.PI / 2.");
cc.frames(1);
expect(cc.drawn().some((c) => c.name === "translate" && near(c.args[0], ship.x, 0.5) && near(c.args[1], ship.y, 0.5)), "Draw the ship each frame: ctx.translate(ship.x, ship.y) moves the origin to the ship, so the ship can be drawn around (0, 0).");
expect(cc.drawn().filter((c) => c.name === "lineTo").length >= 2 && cc.drawn().some((c) => c.name === "stroke" || c.name === "fill"), "Draw the ship as a triangle: ctx.moveTo the nose, ctx.lineTo the other corners, then ctx.stroke() or ctx.fill().");
const nose = cc.drawn().find((c) => c.name === "moveTo");
expect(nose && nose.args[0] > 0 && near(nose.args[1], 0, 0.5), "Start the triangle at the nose, out along the +x axis: ctx.moveTo(ship.r, 0). ctx.rotate turns +x to face the heading.");
ship.angle = 1.2;
cc.frames(1);
expect(cc.drawn().some((c) => c.name === "rotate" && near(c.args[0], 1.2, 0.01)), "Turn the drawing to face the heading: ctx.rotate(ship.angle), after the translate and before the lines.");
stage(240, 160, 0);
cc.press("ArrowRight");
cc.frames(30);
cc.release("ArrowRight");
const half = ship.angle;
expect(half > 1 && half < 4, `Holding ArrowRight for half a second turned the ship ${half.toFixed(2)} radians; about 2 is right (TURN is 4 radians a second). Angles are radians - a full circle is 2 * Math.PI, about 6.28 - not degrees.`);
stage(240, 160, 0);
cc.press("ArrowRight");
cc.frames(15, 1000 / 30);
cc.release("ArrowRight");
expect(near(ship.angle, half, 0.1), `At 30 frames a second, half a second of ArrowRight turned the ship ${ship.angle.toFixed(2)} radians, but at 60 it turned ${half.toFixed(2)}. The turn per frame is TURN * dt, so the speed does not depend on the frame rate.`);
stage(240, 160, 0);
cc.press("ArrowLeft");
cc.frames(30);
cc.release("ArrowLeft");
expect(ship.angle < -1 && ship.angle > -4, `ArrowLeft should turn the ship the other way (anticlockwise: a smaller angle); the angle is ${ship.angle.toFixed(2)} after half a second.`);
stage(240, 160, 0);
cc.press("ArrowLeft");
cc.press("ArrowRight");
cc.frames(20);
expect(near(ship.angle, 0, 0.01), "Holding both arrows should cancel out and leave the ship pointing the same way.");
cc.release("ArrowLeft");
cc.release("ArrowRight");
const still = ship.angle;
cc.frames(20);
expect(near(ship.angle, still, 0.0001), "The ship kept turning after the keys were let go. It should only turn while an arrow is held.");
""",
        hint="const turn = (keys.has('ArrowRight') ? 1 : 0) - (keys.has('ArrowLeft') ? 1 : 0); ship.angle += turn * TURN * dt;   and in drawShip: ctx.save(); ctx.translate(ship.x, ship.y); ctx.rotate(ship.angle); ... ctx.restore();",
    ),
    Step(
        id="ast-02-thrust",
        track="Asteroids",
        title="Thrust along the heading",
        teaches=(
            "Thrust pushes the ship the way it faces, and 'the way it "
            "faces' is two numbers: Math.cos(angle) is how far along x, "
            "Math.sin(angle) how far along y. Cos goes with x and sin with "
            "y - swap them and the ship flies sideways. The push changes "
            "the VELOCITY (vx, vy), in pixels per second, not the position: "
            "every frame, position += velocity * dt. That one change is "
            "what makes it feel like space - let go of the key and the "
            "ship keeps gliding, because velocity stays until something "
            "changes it. Acceleration is in pixels per second PER second, "
            "so it is THRUST * dt, like gravity in the Platformer."
        ),
        goal="Add const THRUST = 160. While ArrowUp is held, add Math.cos(ship.angle) * THRUST * dt to ship.vx and the sin version to ship.vy. Every frame, move the ship by its velocity: x += vx * dt, y += vy * dt. The check reads ship.",
        starter=_P1,
        solution=_P2,
        check=_H + """
stage(240, 160, 0);
cc.frames(30);
expect(near(ship.vx, 0, 0.01) && near(ship.vy, 0, 0.01) && near(ship.x, 240, 0.5), "With no key held the ship should sit still: only ArrowUp pushes it.");
cc.press("ArrowUp");
cc.frames(30);
cc.release("ArrowUp");
const v60 = ship.vx;
expect(v60 > 30 && v60 < 200, `Facing right and holding ArrowUp for half a second, vx is ${v60.toFixed(1)}; about 80 is right (THRUST is 160 pixels per second, every second). Thrust adds to the velocity (ship.vx, ship.vy), it does not move the ship directly.`);
expect(near(ship.vy, 0, 0.5), `Facing right, thrust should push straight right, but vy is ${ship.vy.toFixed(1)}. x uses Math.cos(ship.angle) and y uses Math.sin(ship.angle).`);
const x1 = ship.x;
cc.frames(30);
expect(ship.x - x1 > 20 && near(ship.x - x1, ship.vx * 0.5, 2), "After you let go, the ship should keep gliding at the speed it had: every frame position += velocity * dt, whether or not a key is held.");
stage(240, 160, -Math.PI / 2);
cc.press("ArrowUp");
cc.frames(30);
cc.release("ArrowUp");
expect(near(ship.vx, 0, 0.5) && ship.vy < -30, `Facing up, thrust should push the ship up (vy negative, vx near 0); vx is ${ship.vx.toFixed(1)} and vy is ${ship.vy.toFixed(1)}. If they look swapped, you used sin for x and cos for y.`);
stage(240, 160, Math.PI);
cc.press("ArrowUp");
cc.frames(30);
cc.release("ArrowUp");
expect(ship.vx < -30 && near(ship.vy, 0, 0.5), `Facing left, thrust should push the ship left (vx negative); vx is ${ship.vx.toFixed(1)}.`);
stage(240, 160, 1);
cc.press("ArrowUp");
cc.frames(30);
cc.release("ArrowUp");
expect(speed() > 30 && near(Math.atan2(ship.vy, ship.vx), 1, 0.03), `Facing a heading of 1 radian, the ship should accelerate along (Math.cos(1), Math.sin(1)); its velocity points at ${Math.atan2(ship.vy, ship.vx).toFixed(2)} radians.`);
stage(240, 160, 0);
cc.press("ArrowUp");
cc.frames(15, 1000 / 30);
cc.release("ArrowUp");
expect(near(ship.vx, v60, 2.5), `At 30 frames a second, half a second of thrust gave vx ${ship.vx.toFixed(1)} but at 60 it gave ${v60.toFixed(1)}. Thrust per frame is THRUST * dt, so the frame rate does not matter.`);
""",
        hint="if (keys.has('ArrowUp')) { ship.vx += Math.cos(ship.angle) * THRUST * dt; ship.vy += Math.sin(ship.angle) * THRUST * dt; }   then   ship.x += ship.vx * dt; ship.y += ship.vy * dt;",
    ),
    Step(
        id="ast-03-friction",
        track="Asteroids",
        title="A little friction",
        teaches=(
            "Real space has no friction, but a game with none is nearly "
            "impossible to fly: you can never stop, and every mistake "
            "stays forever. A touch of drag gives the ship a top speed and "
            "lets it settle. The trap is how: 'vx *= 0.99' each frame "
            "slows a 60 fps screen twice as fast as a 30 fps one. Say "
            "instead what fraction of the speed is KEPT after one whole "
            "second (DRAG = 0.5 keeps half), and scale it to this frame "
            "with Math.pow(DRAG, dt). Multiply BOTH vx and vy by the same "
            "number: friction slows the ship, it does not turn it. A "
            "fraction also never reverses the ship, which taking away a "
            "fixed amount would."
        ),
        goal="Add const DRAG = 0.5, the fraction of its speed the ship keeps after one second. Each frame, before moving, multiply ship.vx and ship.vy by Math.pow(DRAG, dt). The check reads ship.",
        starter=_P2,
        solution=_P3,
        check=_H + """
stage(240, 160, 0);
ship.vx = 100;
ship.vy = -40;
const s0 = speed();
cc.frames(60);
const r1 = speed() / s0;
expect(r1 > 0.25 && r1 < 0.85, `After a second of coasting the ship has ${(r1 * 100).toFixed(0)}% of its speed. Friction should take a good part of it - but not all - in a second: keep a fraction each second, Math.pow(DRAG, dt).`);
expect(near(Math.atan2(ship.vy, ship.vx), Math.atan2(-40, 100), 0.02), "Friction slows the ship without turning it: multiply vx and vy by the same factor.");
const s1 = speed();
cc.frames(60);
expect(near(speed() / s1, r1, 0.08), "Friction should take the same fraction of the speed every second - a big speed loses more than a small one. Taking away a fixed amount makes the ship stop dead, or even roll backwards.");
stage(240, 160, 0);
ship.vx = 100;
ship.vy = -40;
cc.frames(30, 1000 / 30);
expect(near(speed() / s0, r1, 0.05), `After a second at 30 frames a second the ship kept ${(100 * speed() / s0).toFixed(0)}% of its speed, but at 60 it kept ${(r1 * 100).toFixed(0)}%. Use dt: Math.pow(DRAG, dt), not a number per frame.`);
stage(240, 160, 0);
ship.vx = 100;
cc.frames(600);
expect(ship.vx >= -0.001 && ship.vx < 1, `After ten seconds of coasting vx is ${ship.vx.toFixed(2)}; friction should bring the ship almost to a halt, never push it backwards.`);
stage(240, 160, 0);
cc.press("ArrowUp");
cc.frames(480);
const s8 = speed();
cc.frames(240);
const s12 = speed();
cc.release("ArrowUp");
expect(s8 > 100 && s8 < 400, `Holding ArrowUp for 8 seconds the ship reaches ${s8.toFixed(0)} pixels a second. Thrust against friction should settle around 230.`);
expect(s12 < s8 * 1.05, "Thrust against friction should level out at a top speed, but the ship is still speeding up after 8 seconds.");
""",
        hint="const damp = Math.pow(DRAG, dt); ship.vx *= damp; ship.vy *= damp;   (after the thrust, before ship.x += ...)",
    ),
    Step(
        id="ast-04-wrap",
        track="Asteroids",
        title="Round the edges",
        teaches=(
            "In Asteroids the screen is a doughnut: fly off one edge and "
            "you come in on the opposite one. That is four cases, not "
            "two - off the left, right, top AND bottom - and a function "
            "that only knows about the right and bottom edges is the "
            "classic bug: the ship leaves on the left and is lost for "
            "ever. Give it a margin of the thing's own radius, so it "
            "disappears completely before it reappears (test x < -r, not "
            "x < 0), and write it once as wrap(o) taking anything with "
            "x, y and r. Bullets and rocks will use it too. (The modulo "
            "operator can do it, but JavaScript's % keeps the sign: "
            "-5 % 480 is -5, so a negative needs ((x % w) + w) % w.)"
        ),
        goal="Write wrap(o): an object that goes off one edge comes in on the opposite one, on all four edges, once it is fully off (past its radius o.r). Call wrap(ship) each frame after moving. The check reads ship.",
        starter=_P3,
        solution=_P4,
        check=_H + """
expect(typeof wrap === "function", "Write function wrap(o) that moves o to the opposite edge when it has left the canvas.");
stage(470, 160, 0);
ship.vx = 300;
cc.frames(20);
expect(ship.x < 200 && ship.x > -40 && near(ship.y, 160, 3), `The ship flew off the right edge and is at x ${ship.x.toFixed(0)}; it should come back in from the left. When o.x is past canvas.width + o.r, put it at -o.r.`);
stage(10, 160, 0);
ship.vx = -300;
cc.frames(20);
expect(ship.x > 300 && ship.x < 520 && near(ship.y, 160, 3), `The ship flew off the left edge and is at x ${ship.x.toFixed(0)}; it should come back in from the right. Every edge needs its own case - not only x > canvas.width.`);
stage(240, 10, 0);
ship.vy = -300;
cc.frames(20);
expect(ship.y > 170 && ship.y < 340 && near(ship.x, 240, 3), `The ship flew off the top and is at y ${ship.y.toFixed(0)}; it should come back in from the bottom.`);
stage(240, 310, 0);
ship.vy = 300;
cc.frames(20);
expect(ship.y < 150 && ship.y > -40 && near(ship.x, 240, 3), `The ship flew off the bottom and is at y ${ship.y.toFixed(0)}; it should come back in from the top.`);
stage(100, 100, 0);
ship.vx = 50;
cc.frames(12);
expect(ship.x > 100 && ship.x < 115 && near(ship.y, 100, 1), "A ship in the middle of the screen must not be moved by wrap - only one that has gone off an edge.");
""",
        hint="if (o.x < -o.r) o.x = canvas.width + o.r; else if (o.x > canvas.width + o.r) o.x = -o.r;   and the same for y with canvas.height.",
    ),
    Step(
        id="ast-05-bullets",
        track="Asteroids",
        title="Fire along the heading",
        teaches=(
            "A bullet leaves the nose in the direction the ship faces, so "
            "it is the thrust trick again: (Math.cos(angle), Math.sin("
            "angle)) times a speed. Start it at the nose, ship.r along the "
            "heading, so it does not appear in the middle of the hull. And "
            "ADD the ship's own velocity: a bullet fired while flying "
            "sideways keeps drifting sideways, as it would in space, and "
            "it is why shooting from a fast ship feels so different. "
            "Bullets are objects in an array, moved every frame like "
            "everything else, and they wrap like everything else. Each "
            "has a radius r (just 2) so wrap(o) and, later, collision can "
            "treat it as a small circle."
        ),
        goal="Add const BULLET_SPEED = 360 and const bullets = []. Pressing Space adds a bullet { x, y, vx, vy, r: 2 } at the ship's nose, flying along the heading at BULLET_SPEED plus the ship's own velocity. Move and wrap the bullets every frame and draw each as a small circle. The check reads ship and bullets.",
        starter=_P4,
        solution=_P5,
        check=_H + """
expect(Array.isArray(bullets), "Keep the bullets in an array: const bullets = [];");
const fireAt = (angle, vx, vy, x = 240, y = 160) => {
  stage(x, y, angle);
  ship.vx = vx;
  ship.vy = vy;
  cc.press(" ");
  cc.release(" ");
  expect(bullets.length === 1, `Pressing Space should add exactly one bullet to bullets; there are ${bullets.length}.`);
  return bullets[0];
};
const first = fireAt(0, 0, 0);
expect(Math.hypot(first.x - ship.x, first.y - ship.y) <= ship.r + 8 && first.x > ship.x, "The bullet should start at the ship's nose, ship.r pixels along the heading: ship.x + Math.cos(ship.angle) * ship.r.");
for (const a of [0, 1, 2.5, -Math.PI / 2]) {
  const b = fireAt(a, 0, 0);
  const along = (b.vx * Math.cos(a) + b.vy * Math.sin(a)) / (Math.hypot(b.vx, b.vy) || 1);
  expect(along > 0.999, `Facing ${a.toFixed(2)} radians, the bullet flew off along (${b.vx.toFixed(0)}, ${b.vy.toFixed(0)}). A heading is (Math.cos(angle), Math.sin(angle)): cos for x, sin for y.`);
  expect(Math.hypot(b.vx, b.vy) > 200, "The bullet should be fast - BULLET_SPEED is 360 pixels a second.");
}
const moving = fireAt(-Math.PI / 2, 80, 0);
expect(near(moving.vx, 80, 5) && moving.vy < -200, `Fired straight up from a ship moving right at 80, the bullet should still drift right at 80 (it has the ship's velocity as well as its own); its velocity is (${moving.vx.toFixed(0)}, ${moving.vy.toFixed(0)}).`);
const f = fireAt(0, 0, 0);
const x0 = f.x;
cc.frames(8, 1000 / 30);
expect(near(f.x, x0 + f.vx * (8 / 30), 3), `After a quarter of a second at 30 frames a second the bullet is at x ${f.x.toFixed(0)}, not ${(x0 + f.vx * 8 / 30).toFixed(0)}. Move it by velocity * dt.`);
const g = fireAt(0, 0, 0);
const gx = g.x;
cc.frames(16);
expect(near(g.x, gx + g.vx * (16 / 60), 3), "At 60 frames a second the bullet is not where velocity * dt puts it.");
cc.frames(1);
expect(cc.arcs().some((a) => near(a.x, g.x, 1) && near(a.y, g.y, 1)), "Draw each bullet as a small circle: ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2) then ctx.fill().");
const edge = fireAt(0, 0, 0, 460, 160);
cc.frames(6);
expect(edge.x < 150 && edge.x > -30, `A bullet fired off the right edge is at x ${edge.x.toFixed(0)}; bullets wrap round the screen too - call wrap(b).`);
const top = fireAt(-Math.PI / 2, 0, 0, 240, 20);
cc.frames(6);
expect(top.y > 200 && top.y < 340, `A bullet fired off the top is at y ${top.y.toFixed(0)}; it should come in from the bottom.`);
""",
        hint="bullets.push({ x: ship.x + c * ship.r, y: ship.y + s * ship.r, vx: ship.vx + c * BULLET_SPEED, vy: ship.vy + s * BULLET_SPEED, r: 2 });   with c = Math.cos(ship.angle) and s = Math.sin(ship.angle).",
    ),
    Step(
        id="ast-06-gun",
        track="Asteroids",
        title="A gun that cools, bullets that expire",
        teaches=(
            "Two problems with the last step. A bullet that wraps round "
            "for ever fills the sky and the array: give each one a life "
            "in seconds, take dt off every frame, and remove it at zero. "
            "Remove while looping BACKWARDS (for i from length - 1 down), "
            "or splicing shifts the next bullet into the gap and it is "
            "skipped. And a Space bar that fires on every key event is "
            "either one shot per press or a firehose. A gun wants a "
            "COOLDOWN: a number of seconds left before it can fire again, "
            "counted down with dt and set when you fire. Count it in "
            "seconds, never in frames - 15 frames is a quarter of a "
            "second at 60 fps and half a second at 30."
        ),
        goal="Add const BULLET_LIFE = 1, const COOLDOWN = 0.25 and let cooldown = 0. A bullet gets life: BULLET_LIFE, loses dt a frame, and is removed at 0. Holding Space fires when cooldown is 0, then sets it to COOLDOWN; it counts down by dt. The check reads ship and bullets.",
        starter=_P5,
        solution=_P6,
        check=_H + """
stage();
cc.press(" ");
cc.frames(1);
cc.release(" ");
expect(bullets.length === 1, `Pressing Space for a frame should fire a bullet; there are ${bullets.length}.`);
cc.frames(2);
cc.press(" ");
cc.frames(1);
cc.release(" ");
expect(bullets.length === 1, "A second tap a few frames later fired again. The gun needs time to cool down: COOLDOWN seconds between shots, however the key is pressed.");
const seen = new Set();
const hold = (n, dt) => {
  seen.clear();
  stage();
  cc.frames(20);
  cc.press(" ");
  for (let i = 0; i < n; i++) {
    cc.frames(1, dt);
    for (const b of bullets) seen.add(b);
  }
  cc.release(" ");
  return seen.size;
};
const n60 = hold(120);
expect(n60 >= 6 && n60 <= 10, `Holding Space for two seconds fired ${n60} bullets; with a cooldown of 0.25 seconds it should be about 8. Holding the key should keep firing, one shot every COOLDOWN seconds.`);
const n30 = hold(60, 1000 / 30);
expect(n30 >= 6 && n30 <= 10, `At 30 frames a second, two seconds of holding Space fired ${n30} bullets (60 frames a second fired ${n60}). Count the cooldown down in seconds - subtract dt - not in frames.`);
const count = seen.size;
cc.frames(30);
for (const b of bullets) seen.add(b);
expect(seen.size === count, "The gun kept firing after Space was let go.");
const expiry = (dt, early, late) => {
  stage();
  cc.frames(20);
  cc.press(" ");
  cc.frames(1, dt);
  cc.release(" ");
  const b = bullets[0];
  expect(b, "Holding Space should fire a bullet.");
  cc.frames(early, dt);
  expect(bullets.includes(b), "A bullet vanished before its second was up. BULLET_LIFE is 1 second.");
  cc.frames(late, dt);
  expect(!bullets.includes(b), "A bullet was still flying about 1.4 seconds after it was fired. Give each bullet a life, take dt off it every frame, and remove it when it reaches 0.");
};
expiry(undefined, 36, 48);
expiry(1000 / 30, 17, 24);
""",
        hint="if (cooldown > 0) cooldown -= dt; if (keys.has(' ') && cooldown <= 0) { fire(); cooldown = COOLDOWN; }   and   b.life -= dt;   then loop backwards: if (bullets[i].life <= 0) bullets.splice(i, 1);",
    ),
    Step(
        id="ast-07-rocks",
        track="Asteroids",
        title="Rocks that drift and spin",
        teaches=(
            "The rocks are bullets with more to them: a position, a "
            "velocity, and a spin - radians per second, added to the "
            "angle each frame, so it too is spin * dt. Each is born by one "
            "function, makeRock(x, y, size), with the randomness in it: "
            "a random heading and speed (and, once again, cos and sin "
            "turn a heading and a speed into vx and vy), a random spin, "
            "and a size from 1 to 3 that sets the radius, r = size * 14. "
            "The outline is a ring of ten points at slightly different "
            "distances from the centre, picked once and kept, so a rock "
            "turns as a lumpy shape rather than reshuffling every frame. "
            "Spawn them away from the ship - a do { } while loop picks "
            "again until the spot is far enough."
        ),
        goal="Add const rocks = []; makeRock(x, y, size), which returns { x, y, vx, vy, angle, spin, size, r: size * 14, shape } with random velocity (20 to 60 pixels a second) and spin; and spawnRocks(n), which pushes n rocks of size 2 or 3 at least 120 pixels from the ship. Call spawnRocks(4) at the start. Each frame move, spin and wrap the rocks, and draw them with translate and rotate. The check reads ship, rocks, makeRock and spawnRocks.",
        starter=_P6,
        solution=_P7,
        check=_H + """
expect(typeof makeRock === "function", "Write function makeRock(x, y, size) that returns a new rock object.");
expect(typeof spawnRocks === "function", "Write function spawnRocks(n) that adds n rocks to the rocks array.");
expect(Array.isArray(rocks) && rocks.length >= 3, "Call spawnRocks(4) when the game starts, so there are rocks to shoot.");
for (const rk of rocks) {
  expect(Math.hypot(rk.x - ship.x, rk.y - ship.y) >= 100, "A rock started right next to the ship. Choose a spot, and while it is within 120 pixels of the ship choose again (a do { } while loop).");
}
rocks.length = 0;
spawnRocks(30);
expect(rocks.length === 30, `spawnRocks(30) made ${rocks.length} rocks.`);
for (const rk of rocks) {
  expect(["x", "y", "vx", "vy", "angle", "spin", "size", "r"].every((k) => Number.isFinite(rk[k])), "Every rock needs numbers x, y, vx, vy, angle, spin, size and r.");
  expect(near(rk.r, rk.size * 14, 0.5), `A rock of size ${rk.size} has radius ${rk.r}; the radius is size * 14.`);
  expect(Math.hypot(rk.x - ship.x, rk.y - ship.y) >= 100, "A rock started right next to the ship.");
}
const sizes = new Set(rocks.map((rk) => rk.size));
expect(sizes.size >= 2 && [...sizes].every((s) => s >= 1 && s <= 3 && Number.isInteger(s)), "spawnRocks should make rocks of random sizes - 2 or 3 - using Math.random.");
const speeds = rocks.map((rk) => Math.hypot(rk.vx, rk.vy));
expect(speeds.every((s) => s > 8 && s < 120), "Rocks drift slowly: a speed of 20 to 60 pixels a second.");
expect(new Set(rocks.map((rk) => Math.round(rk.vx))).size >= 15 && new Set(rocks.map((rk) => Math.round(Math.atan2(rk.vy, rk.vx) * 2))).size >= 6, "Every rock should drift its own way: choose a random heading and a random speed, then vx = Math.cos(heading) * speed and vy = Math.sin(heading) * speed.");
expect(rocks.some((rk) => Math.abs(rk.spin) > 0.1) && rocks.every((rk) => Math.abs(rk.spin) < 4), "Rocks spin: give each a random spin (radians a second), a small number either way.");
rocks.length = 0;
const rk = makeRock(100, 100, 3);
rocks.push(rk);
rk.vx = 60;
rk.vy = -30;
rk.spin = 2;
rk.angle = 0;
cc.frames(30, 1000 / 30);
expect(near(rk.x, 160, 1.5) && near(rk.y, 70, 1.5), `A rock with vx 60 and vy -30 should be at (160, 70) after a second; it is at (${rk.x.toFixed(1)}, ${rk.y.toFixed(1)}). x += vx * dt and y += vy * dt, every frame.`);
expect(near(rk.angle, 2, 0.05), `A rock spinning at 2 radians a second should have turned 2 radians after a second; its angle is ${rk.angle.toFixed(2)}. angle += spin * dt.`);
rk.x = 100;
rk.y = 100;
rk.angle = 0;
cc.frames(60);
expect(near(rk.x, 160, 1.5) && near(rk.angle, 2, 0.05), "At 60 frames a second the rock is not where velocity * dt and spin * dt put it.");
cc.frames(1);
expect(cc.drawn().some((c) => c.name === "translate" && near(c.args[0], rk.x, 1.5) && near(c.args[1], rk.y, 1.5)) && cc.drawn().some((c) => c.name === "rotate" && near(c.args[0], rk.angle, 0.05)), "Draw each rock with ctx.save(), ctx.translate(rk.x, rk.y), ctx.rotate(rk.angle), the outline around (0, 0), then ctx.restore().");
const edge = (x, y, vx, vy) => {
  rk.x = x;
  rk.y = y;
  rk.vx = vx;
  rk.vy = vy;
  rk.spin = 0;
  cc.frames(60);
};
edge(470, 160, 60, 0);
expect(rk.x < 150 && rk.x > -2 * rk.r, `A rock drifted off the right edge and is at x ${rk.x.toFixed(0)}; rocks wrap round the screen: call wrap(rk).`);
edge(10, 160, -60, 0);
expect(rk.x > 350 && rk.x < 480 + 2 * rk.r, `A rock drifted off the left edge and is at x ${rk.x.toFixed(0)}; it should come back in from the right.`);
edge(240, 10, 0, -60);
expect(rk.y > 250 && rk.y < 320 + 2 * rk.r, `A rock drifted off the top and is at y ${rk.y.toFixed(0)}; it should come back in from the bottom.`);
edge(240, 310, 0, 60);
expect(rk.y < 100 && rk.y > -2 * rk.r, `A rock drifted off the bottom and is at y ${rk.y.toFixed(0)}; it should come back in from the top.`);
""",
        hint="rk.x += rk.vx * dt; rk.y += rk.vy * dt; rk.angle += rk.spin * dt; wrap(rk);   and makeRock: const heading = Math.random() * Math.PI * 2; const speed = 20 + Math.random() * 40;",
    ),
    Step(
        id="ast-08-shoot",
        track="Asteroids",
        title="Shoot a rock",
        teaches=(
            "Two circles overlap when the distance between their centres "
            "is less than the sum of their radii: Math.hypot(dx, dy) < "
            "a.r + b.r. That is not the same as comparing x and y "
            "separately, which tests a SQUARE around each circle: a bullet "
            "near the corner of that square is miles from a round rock yet "
            "counts as a hit. Use each thing's own radius, so a small rock "
            "is harder to hit than a big one. A hit removes BOTH the "
            "bullet and the rock and scores - more for smaller, harder "
            "rocks. Test every bullet against every rock, loop backwards "
            "because you splice, and break after a hit: the bullet is "
            "gone, and one bullet breaks one rock."
        ),
        goal="Write overlap(a, b), true when two circles (objects with x, y and r) overlap. Each frame, when a bullet overlaps a rock, remove both and add POINTS[rock.size] to score (const POINTS = { 1: 100, 2: 50, 3: 20 }, let score = 0). One bullet breaks at most one rock. Write the score on the screen. The check reads ship, bullets, rocks, score and makeRock.",
        starter=_P7,
        solution=_P8,
        check=_H + """
expect(typeof score === "number" && score === 0, "Start with let score = 0;");
const trial = (size, dx, dy) => {
  stage(100, 160, 0);
  const b = shoot();
  const rk = rock(300, 160, size);
  b.x = rk.x + dx;
  b.y = rk.y + dy;
  const before = score;
  cc.frames(1);
  return { rockGone: !rocks.includes(rk), bulletGone: !bullets.includes(b), gained: score - before };
};
let t = trial(3, 40, 0);
expect(t.rockGone, "A bullet 40 pixels from the centre of a big rock (radius 42) should hit it. They overlap when the distance between the centres is less than the two radii added together.");
expect(t.bulletGone, "A bullet that hit a rock should be removed too.");
expect(t.gained === 20, `Breaking a big rock is worth 20 points; the score went up by ${t.gained}.`);
t = trial(3, 33, 33);
expect(!t.rockGone && !t.bulletGone && t.gained === 0, "A bullet at the corner of a big rock's bounding square, about 47 pixels from its centre, should miss. Test the distance Math.hypot(dx, dy) against the radii, not x and y one at a time.");
t = trial(1, 30, 0);
expect(!t.rockGone && t.gained === 0, "A bullet 30 pixels from a small rock (radius 14) should miss. Use each rock's own radius: a.r + b.r.");
t = trial(1, 10, 0);
expect(t.rockGone && t.bulletGone, "A bullet 10 pixels from the centre of a small rock should hit it.");
expect(t.gained === 100, `A small rock is worth 100 points; the score went up by ${t.gained}.`);
t = trial(2, 20, 0);
expect(t.rockGone && t.bulletGone && t.gained === 50, `A medium rock is worth 50 points; the score went up by ${t.gained} (rock gone: ${t.rockGone}).`);
stage(100, 160, 0);
const b = shoot();
rock(300, 160, 3);
rock(300, 160, 3);
b.x = 310;
b.y = 160;
const before = score;
cc.frames(1);
expect(rocks.length === 1 && score - before === 20, `Two rocks lay under one bullet: it should break one and be used up. ${rocks.length} are left and the score went up by ${score - before}. Break out of the loop after a hit.`);
cc.frames(1);
expect(cc.texts().some((s) => /score/i.test(s) && s.includes(String(score))), `Write the score on the screen: it should say Score: ${score}.`);
""",
        hint="Math.hypot(a.x - b.x, a.y - b.y) < a.r + b.r   then in hitRocks: score += POINTS[rocks[j].size]; rocks.splice(j, 1); bullets.splice(i, 1); break;",
    ),
    Step(
        id="ast-09-split",
        track="Asteroids",
        title="Rocks break in two",
        teaches=(
            "A hit rock does not just vanish: a big one breaks into two "
            "medium ones, a medium into two small, and a small one is "
            "gone. The order matters. Take the parent OUT of the array "
            "first (splice), then, if it was bigger than the smallest "
            "size, push two children one size smaller at its position. "
            "Forget the removal and the parent stays behind to be hit "
            "again, forever. Let makeRock do the rest - it gives each "
            "child its own random heading, speed and spin, so the two "
            "fly apart on their own. Because the loop that found the hit "
            "stops at once (the break), pushing onto the array while "
            "scanning it is safe here."
        ),
        goal="When a bullet breaks a rock of size above 1, also add two rocks of size - 1 at its position, made with makeRock. A rock of size 1 just disappears. The score and the one-bullet-one-rock rule stay as they were. The check reads ship, bullets, rocks, score and makeRock.",
        starter=_P8,
        solution=_P9,
        check=_H + """
const smash = (size) => {
  stage(100, 160, 0);
  const b = shoot();
  const parent = rock(300, 160, size);
  b.x = 310;
  b.y = 160;
  const before = score;
  cc.frames(1);
  return { parent, gained: score - before };
};
let s = smash(3);
expect(!rocks.includes(s.parent), "The rock that was hit is still in the rocks array. Take it out (splice) before adding its pieces.");
expect(rocks.length === 2, `Breaking a big rock should leave exactly two pieces; there are ${rocks.length} rocks.`);
expect(rocks.every((c) => c.size === 2 && near(c.r, 28, 0.5)), "The pieces of a big rock (size 3) are medium (size 2, radius 28): makeRock(rk.x, rk.y, rk.size - 1).");
expect(rocks.every((c) => Math.hypot(c.x - 300, c.y - 160) < 30), "The pieces should start where the rock was broken.");
expect(Math.hypot(rocks[0].vx - rocks[1].vx, rocks[0].vy - rocks[1].vy) > 2, "The two pieces should fly apart: each one needs its own random velocity (makeRock gives it one).");
expect(s.gained === 20, `A big rock is still worth 20 points; the score went up by ${s.gained}.`);
s = smash(2);
expect(!rocks.includes(s.parent) && rocks.length === 2 && rocks.every((c) => c.size === 1 && near(c.r, 14, 0.5)), `Breaking a medium rock should leave two small ones (size 1, radius 14); there are ${rocks.length} rocks.`);
expect(s.gained === 50, `A medium rock is worth 50 points; the score went up by ${s.gained}.`);
s = smash(1);
expect(rocks.length === 0, `A small rock breaks into nothing; ${rocks.length} rocks are left.`);
expect(s.gained === 100, `A small rock is worth 100 points; the score went up by ${s.gained}.`);
stage(100, 160, 0);
const b = shoot();
rock(300, 160, 3);
b.x = 310;
b.y = 160;
cc.frames(1);
cc.frames(30);
expect(rocks.length === 2, `The pieces should drift on without breaking again; ${rocks.length} rocks are left.`);
""",
        hint="function breakRock(j) { const rk = rocks[j]; rocks.splice(j, 1); if (rk.size > 1) { rocks.push(makeRock(rk.x, rk.y, rk.size - 1)); rocks.push(makeRock(rk.x, rk.y, rk.size - 1)); } }",
    ),
    Step(
        id="ast-10-lives",
        track="Asteroids",
        title="Lives and a second chance",
        teaches=(
            "A ship touching a rock is the same circle test as before, "
            "ship against rock. What is new is the aftermath. Losing a "
            "life puts the ship back in the middle, stopped, and then "
            "protects it: a short invulnerability, a number of seconds "
            "left that counts down with dt, during which rocks cannot "
            "hurt it. Without that, a rock drifting over the respawn point "
            "takes a life EVERY FRAME and three lives are gone in a "
            "twentieth of a second. Flashing the ship while it is "
            "protected tells the player why nothing is happening; "
            "Math.floor(invuln * 10) % 2 flips every tenth of a second. "
            "Count the protection in seconds, not frames, or it lasts "
            "twice as long on a slow screen."
        ),
        goal="Add let lives = 3, const INVULN = 2 and invuln: 0 on the ship. When the ship overlaps a rock and ship.invuln is 0 or less: lose a life, put the ship back in the middle, stopped and pointing up, and set ship.invuln to INVULN. It counts down by dt, and the ship blinks while it is above 0. Write the lives on the screen. The check reads ship, rocks, lives and makeRock.",
        starter=_P9,
        solution=_P10,
        check=_H + """
expect(typeof lives === "number" && lives === 3, "Start with let lives = 3;");
expect(typeof ship.invuln === "number", "Give the ship a number of seconds of protection: ship.invuln, starting at 0.");
cc.frames(1);
expect(cc.texts().some((s) => /live/i.test(s) && s.includes("3")), "Write the lives on the screen from the start: it should say Lives: 3.");
stage(100, 100, 0);
rock(250, 100, 3);
cc.frames(10);
expect(lives === 3, "A rock 150 pixels away cost a life. The ship and a rock touch when the distance between their centres is less than the two radii added together.");
stage(100, 100, 0);
rock(140, 140, 3);
cc.frames(2);
expect(lives === 3, "A rock whose bounding square touches the ship's, but whose circle does not (about 57 pixels away, radii 12 + 42), cost a life. Use the distance, Math.hypot, not x and y separately.");
stage(100, 100, 0);
ship.vx = 40;
const rk = rock(130, 100, 3);
cc.frames(1, 1000 / 60);
expect(lives === 2, `The ship touched a rock and lives is ${lives}; it should be 2.`);
expect(near(ship.x, canvas.width / 2, 1) && near(ship.y, canvas.height / 2, 1), "After a hit the ship goes back to the middle of the canvas.");
expect(near(ship.vx, 0, 0.5) && near(ship.vy, 0, 0.5), "After a hit the ship starts again standing still: vx and vy back to 0.");
expect(near(Math.sin(ship.angle), -1, 0.02), "After a hit the ship points up again: angle -Math.PI / 2.");
expect(ship.invuln > 1 && ship.invuln <= 3, `After a hit the ship should be protected for INVULN (2) seconds; ship.invuln is ${ship.invuln}.`);
cc.frames(1);
expect(cc.texts().some((s) => /live/i.test(s) && s.includes("2")), "Show the new number of lives on the screen.");
rk.x = canvas.width / 2;
rk.y = canvas.height / 2;
cc.frames(30, 1000 / 30);
expect(lives === 2, `A rock sat on the respawned ship for a second and lives went down to ${lives}. While ship.invuln is above 0, rocks must not hurt it - otherwise a life goes every frame.`);
let shown = 0;
let hidden = 0;
for (let i = 0; i < 20; i++) {
  cc.frames(1);
  if (cc.drawn().some((c) => c.name === "rotate" && near(c.args[0], ship.angle, 0.001))) shown++;
  else hidden++;
}
expect(shown >= 1 && hidden >= 1, "While the ship is protected it should blink: drawn on some frames and not on others (for example when Math.floor(ship.invuln * 10) % 2 is 0).");
cc.frames(30, 1000 / 30);
expect(lives === 1, `After the protection ran out (2 seconds) the rock still on top of the ship should cost another life; lives is ${lives}. Count ship.invuln down in seconds with dt, not in frames.`);
expect(ship.invuln > 0, "Every life lost starts the protection again.");
""",
        hint="if (ship.invuln > 0) ship.invuln -= dt; if (ship.invuln <= 0 && rocks.some((rk) => overlap(ship, rk))) loseLife();   and loseLife sets lives -= 1, the ship back to the middle with vx = vy = 0, and ship.invuln = INVULN.",
    ),
    Step(
        id="ast-11-over",
        track="Asteroids",
        title="Game over, play again",
        teaches=(
            "When the last life goes, the game stops being a simulation "
            "and becomes a screen. Keep what the game is doing in one "
            "word, state: 'playing' or 'over'. update stops at once when "
            "it is not 'playing' - no flying, firing or drifting rocks - "
            "and draw adds the 'Game over' message. A restart is a "
            "function that puts EVERY piece back: the ship (position, "
            "speed, heading, protection), the gun's cooldown, the "
            "bullets and rocks (empty the arrays, then spawn new rocks - "
            "forget and the old ones are still out there), the score and "
            "the lives. Miss one and the second game plays differently "
            "from the first. Bind it to Enter, and only when the game is "
            "over."
        ),
        goal="Add let state = 'playing'. When lives reaches 0, set state to 'over' and stop updating the game (draw 'Game over' on the screen). Write reset(), which puts the ship, cooldown, bullets, rocks (4 new ones), score, lives and state back as they began; Enter calls it, but only when the game is over. The check reads ship, bullets, rocks, score, lives and state.",
        starter=_P10,
        solution=_P11,
        check=_H + """
expect(typeof state === "string" && state === "playing", "Keep what the game is doing in let state = 'playing';");
stage(100, 100, -Math.PI / 2);
score = 50;
lives = 3;
cc.press("Enter");
cc.frames(2);
expect(score === 50 && lives === 3 && state === "playing", "Enter in the middle of a game restarted it. Only restart when state is 'over'.");
cc.press(" ");
cc.frames(1);
cc.release(" ");
expect(bullets.length === 1, "Fire a bullet before dying: Space should still work while the game is on.");
cc.frames(7);
ship.vx = 20;
ship.vy = -10;
lives = 1;
const rk = rock(130, 100, 3);
cc.frames(1);
expect(lives === 0, `The ship hit a rock on its last life and lives is ${lives}; it should be 0.`);
expect(state === "over", `With no lives left state is '${state}'; it should be 'over'.`);
cc.frames(1);
expect(cc.texts().some((s) => /game over/i.test(s)), "When the game is over, say so on the screen.");
const before = [rk.x, ship.x, ship.angle, bullets.length];
rk.vx = 60;
cc.press("ArrowLeft");
cc.press("ArrowUp");
cc.press(" ");
cc.frames(30);
cc.release("ArrowLeft");
cc.release("ArrowUp");
cc.release(" ");
expect(rk.x === before[0] && ship.x === before[1] && ship.angle === before[2] && bullets.length === before[3], "After game over everything should freeze: no flying, no turning, no firing, no drifting rocks. Return from update when state is not 'playing'.");
cc.press("ArrowRight");
cc.frames(2);
cc.release("ArrowRight");
expect(state === "over", "A key other than Enter restarted the game. Only Enter should.");
cc.press("Enter");
expect(state === "playing", `Pressing Enter after game over should start a new game; state is '${state}'.`);
expect(score === 0 && lives === 3, `A new game starts with a score of 0 and 3 lives; they are ${score} and ${lives}.`);
expect(bullets.length === 0, "A new game should start with no bullets in the air: empty the bullets array.");
expect(rocks.length === 4, `A new game starts with 4 new rocks (the old ones gone); there are ${rocks.length}. Empty the rocks array, then spawnRocks(4).`);
expect(rocks.every((r) => Math.hypot(r.x - ship.x, r.y - ship.y) >= 100), "The new rocks should start well away from the ship.");
expect(near(ship.x, canvas.width / 2, 1) && near(ship.y, canvas.height / 2, 1) && near(ship.vx, 0, 0.5) && near(ship.vy, 0, 0.5), "A new game starts with the ship still, in the middle.");
expect(near(Math.sin(ship.angle), -1, 0.02), "A new game starts with the ship pointing up.");
cc.press(" ");
cc.frames(1);
cc.release(" ");
expect(bullets.length === 1, "In the new game Space should fire at once: put cooldown back to 0 too.");
cc.frames(30);
expect(lives === 3 && state === "playing", "The new game should not start with the ship already hit.");
""",
        hint="function reset() { ship.x = canvas.width / 2; ...; cooldown = 0; bullets.length = 0; rocks.length = 0; spawnRocks(4); score = 0; lives = 3; state = 'playing'; }   and  if (e.key === 'Enter' && state === 'over') reset();",
    ),
    Step(
        id="ast-12-yours",
        track="Asteroids",
        title="Now it's yours",
        teaches=(
            "A whole arcade game on angles. Ideas, easier first: draw a "
            "flame behind the ship while ArrowUp is held; a new wave of "
            "bigger rocks when the last one goes; a hyperspace key that "
            "jumps to a random spot; a small saucer that crosses the "
            "screen and shoots back, aimed with Math.atan2(dy, dx) - the "
            "inverse of cos and sin; an extra life every 10000 points; a "
            "best score kept in localStorage; rocks that shatter into "
            "sparks; sound with the Web Audio API; and a gamepad. "
            "Or make the ship turn at the speed you hold the key: what "
            "does that do to the feel?"
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_P11,
        solution=_P11,
        check="",
    ),
)
