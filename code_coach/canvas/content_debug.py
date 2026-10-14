"""The "Debug it" Canvas track: find the one bug and fix it.

Every other Canvas track asks you to write code. This one hands you a small,
mostly working canvas program with ONE bug in it. The goal says what is wrong
in terms of behaviour - what you would see - and never where. You find the
bug, fix it, and the check plays the program and passes only when the
behaviour is right.

The steps are independent, like the From blank track: a starter is that
step's own buggy program, not the previous step's solution. Each starter runs
without throwing and draws something, and looks right at a glance. The bugs
are the ones people really write: movement per frame instead of per second,
an off-by-one, a canvas never cleared, a collision that counts touching
edges, an array changed while it is looped over, a stale `var` in a closure,
a key that never lets go, a timer that drifts, a score counted every frame,
and a "copy" that is the same array.

A check reads only the names the goal states (square, lives, player...) and
plays the program: so many frames at 30, 60 or 120 per second, this key held.
A fix can be written any way that behaves right.
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

_DRAW_ONLY_LOOP = """
function loop() {
  draw();
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
"""

_BG = """  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
"""

_KEYS = """const keys = new Set();
addEventListener('keydown', (e) => keys.add(e.key));
addEventListener('keyup', (e) => keys.delete(e.key));
"""


def _fix(code: str, *swaps: tuple[str, str]) -> str:
    """The solution: the buggy program with its one bug put right."""
    for old, new in swaps:
        assert code.count(old) == 1, old
        code = code.replace(old, new)
    return code


# ── 1. Faster on a fast screen ───────────────────────────────────────────

_RATE = _SETUP + """
const square = { x: 20, y: 140, size: 40, speed: 4 };

function update(dt) {
  square.x += square.speed;
  if (square.x > canvas.width) square.x = -square.size;
}

function draw() {
""" + _BG + """  ctx.fillStyle = 'tomato';
  ctx.fillRect(square.x, square.y, square.size, square.size);
  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText('speed ' + square.speed, 12, 24);
}
""" + _LOOP

_RATE_FIXED = _fix(
    _RATE,
    ("speed: 4 }", "speed: 240 }"),
    ("square.x += square.speed;", "square.x += square.speed * dt;"),
)

_RATE_CHECK = r"""
cc.frames(2);
expect(cc.rects().some((r) => near(r.x, square.x, 0.01) && r.w === square.size), "Nothing is drawn where the square is. The square should be drawn every frame with ctx.fillRect(square.x, square.y, square.size, square.size).");
const half = (fps) => {
  square.x = 20;
  cc.frames(Math.round(fps / 2), 1000 / fps);
  return square.x - 20;
};
const a = half(30);
const b = half(60);
const c = half(120);
const p = (n) => Math.round(n);
expect(Math.max(a, b, c) - Math.min(a, b, c) <= 6, `In half a second the square covered ${p(a)} px on a 30 Hz screen, ${p(b)} px on a 60 Hz screen and ${p(c)} px on a 120 Hz screen. It should cover the same distance whatever the frame rate.`);
expect(near(b, 120, 6), `The square covers the same distance at every frame rate now, but in half a second it moved ${p(b)} px. It should move 240 pixels a second: about 120 px in half a second.`);
"""

# ── 2. One heart too many ────────────────────────────────────────────────

_HEARTS = _SETUP + """
let lives = 3;

addEventListener('keydown', (e) => {
  if (e.key === 'x' && lives > 0) lives -= 1;
});

function draw() {
""" + _BG + """  ctx.fillStyle = 'crimson';
  for (let i = 0; i <= lives; i++) {
    ctx.fillRect(12 + i * 28, 12, 20, 20);
  }
  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText('Press X to lose a life', 12, 60);
}
""" + _DRAW_ONLY_LOOP

_HEARTS_FIXED = _fix(_HEARTS, ("i <= lives", "i < lives"))

_HEARTS_CHECK = r"""
const cv = document.querySelector("canvas");
const W = cv.width;
const shown = () => {
  cc.frames(1);
  return cc.rects().filter((r) => r.w < W / 2).length;
};
expect(lives === 3, `The game should start with 3 lives; yours starts with ${lives}.`);
let n = shown();
expect(n === 3, `With 3 lives left the screen shows ${n} red squares. It should show 3 - one for each life.`);
cc.press("x");
cc.release("x");
n = shown();
expect(lives === 2, "Pressing x should cost one life: 3 lives become 2.");
expect(n === 2, `With 2 lives left the screen shows ${n} red squares. It should show 2.`);
cc.press("x");
cc.release("x");
n = shown();
expect(n === 1, `With 1 life left the screen shows ${n} red squares. It should show 1.`);
cc.press("x");
cc.release("x");
n = shown();
expect(lives === 0, "Three presses of x should leave 0 lives.");
expect(n === 0, `With 0 lives left the screen still shows ${n} red square${n === 1 ? "" : "s"}. With no lives left there should be none.`);
cc.press("x");
cc.release("x");
n = shown();
expect(lives === 0 && n === 0, "At 0 lives another press of x should change nothing: no negative lives, no squares.");
lives = 5;
n = shown();
expect(n === 5, `With 5 lives left the screen shows ${n} red squares. It should show 5.`);
"""

# ── 3. Ghost trails ──────────────────────────────────────────────────────

_TRAILS = _SETUP + """
const player = { x: 60, y: 140, size: 40, speed: 200 };
""" + _KEYS + """
ctx.fillStyle = '#10141f';
ctx.fillRect(0, 0, canvas.width, canvas.height);

function update(dt) {
  if (keys.has('ArrowRight')) player.x += player.speed * dt;
  if (keys.has('ArrowLeft')) player.x -= player.speed * dt;
  player.x = Math.max(0, Math.min(canvas.width - player.size, player.x));
}

function draw() {
  ctx.fillStyle = 'tomato';
  ctx.fillRect(player.x, player.y, player.size, player.size);
}
""" + _LOOP

_TRAILS_FIXED = _fix(
    _TRAILS,
    ("ctx.fillStyle = '#10141f';\nctx.fillRect(0, 0, canvas.width, canvas.height);\n\nfunction update", "function update"),
    ("function draw() {\n  ctx.fillStyle = 'tomato';", "function draw() {\n" + _BG + "  ctx.fillStyle = 'tomato';"),
)

_TRAILS_CHECK = r"""
const cv = document.querySelector("canvas");
const W = cv.width;
// What is on the screen after each frame, in 4 px cells: a filled rectangle
// paints its cells, clearRect empties them.
const cells = new Map();
const cellKey = (x, y) => Math.floor(x / 4) + "," + Math.floor(y / 4);
const paint = (calls) => {
  for (const c of calls) {
    if (c.name !== "fillRect" && c.name !== "clearRect") continue;
    const [x, y, w, h] = c.args;
    for (let gx = Math.floor(x / 4); gx <= Math.floor((x + w) / 4); gx++) {
      for (let gy = Math.floor(y / 4); gy <= Math.floor((y + h) / 4); gy++) {
        const px = gx * 4 + 2;
        const py = gy * 4 + 2;
        if (px < x || px >= x + w || py < y || py >= y + h) continue;
        if (c.name === "clearRect") cells.delete(gx + "," + gy);
        else cells.set(gx + "," + gy, c.fill);
      }
    }
  }
};
cc.frames(3);
const mine = cc.rects().filter((r) => r.w < W / 2);
expect(mine.length >= 1, "The square is not drawn. It should be drawn every frame with ctx.fillRect(player.x, player.y, player.size, player.size).");
const colour = mine[mine.length - 1].fill;
for (const dt of [1000 / 60, 1000 / 30]) {
  cells.clear();
  player.x = 60;
  player.y = 140;
  cc.frames(1, dt);
  paint(cc.drawn());
  const n = Math.round(0.5 / (dt / 1000));
  const s = player.size;
  for (const [key, name, sign] of [["ArrowRight", "right", 1], ["ArrowLeft", "left", -1]]) {
    const from = player.x;
    cc.press(key);
    for (let i = 0; i < n; i++) {
      cc.frames(1, dt);
      paint(cc.drawn());
    }
    cc.release(key);
    const to = player.x;
    expect(sign * (to - from) > 60, `Holding the ${name} arrow for half a second only moved the square from x ${Math.round(from)} to x ${Math.round(to)}. It should move about 100 px.`);
    expect(cells.get(cellKey(to + s / 2, player.y + s / 2)) === colour, "After moving, nothing is painted where the square should be. The square must be visible at its new place.");
    let leftover = 0;
    for (const [k, fill] of cells) {
      if (fill !== colour) continue;
      const [gx, gy] = k.split(",").map(Number);
      const px = gx * 4 + 2;
      const py = gy * 4 + 2;
      if (px < to - 1 || px > to + s + 1 || py < player.y - 1 || py > player.y + s + 1) leftover++;
    }
    expect(leftover === 0, `The square moved ${name} from x ${Math.round(from)} to x ${Math.round(to)} but it is still painted where it used to be: it leaves a smear behind it. Only the square's current place should be painted.`);
  }
}
"""

# ── 4. Hit by a near miss ────────────────────────────────────────────────

_TOUCH = _SETUP + """
const player = { x: 100, y: 140, w: 40, h: 40, speed: 200 };
const spike = { x: 240, y: 140, w: 40, h: 40 };
let touching = false;
""" + _KEYS + """
function overlaps(a, b) {
  return a.x <= b.x + b.w && a.x + a.w >= b.x && a.y <= b.y + b.h && a.y + a.h >= b.y;
}

function update(dt) {
  if (keys.has('ArrowRight')) player.x += player.speed * dt;
  if (keys.has('ArrowLeft')) player.x -= player.speed * dt;
  if (keys.has('ArrowDown')) player.y += player.speed * dt;
  if (keys.has('ArrowUp')) player.y -= player.speed * dt;
  touching = overlaps(player, spike);
}

function draw() {
""" + _BG + """  ctx.fillStyle = '#8892b0';
  ctx.fillRect(spike.x, spike.y, spike.w, spike.h);
  ctx.fillStyle = touching ? 'crimson' : 'skyblue';
  ctx.fillRect(player.x, player.y, player.w, player.h);
}
""" + _LOOP

_TOUCH_FIXED = _fix(
    _TOUCH,
    ("a.x <= b.x + b.w && a.x + a.w >= b.x && a.y <= b.y + b.h && a.y + a.h >= b.y",
     "a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y"),
)

_TOUCH_CHECK = r"""
cc.frames(2);
expect(spike.x === 240 && spike.y === 140 && spike.w === 40 && spike.h === 40, "The spike should stay where it is: x 240, y 140, 40 by 40.");
expect(player.w === 40 && player.h === 40, "The player should stay 40 by 40.");
const test = (x, y, want, where) => {
  player.x = x;
  player.y = y;
  cc.frames(1);
  const got = touching;
  if (want) expect(got === true, `The player is ${where}, sharing some area with the spike, and touching is ${got}. It should be true.`);
  else expect(got === false, `The player is ${where}, and touching is ${got}. It should be false: they do not share any area.`);
};
test(20, 20, false, "far from the spike");
test(20, 140, false, "level with the spike but far to its left");
test(240, 20, false, "straight above the spike but far away");
test(200, 140, false, "standing right next to the spike on its left, edges just touching");
test(280, 140, false, "standing right next to the spike on its right, edges just touching");
test(240, 100, false, "standing right on top of the spike, edges just touching");
test(240, 180, false, "standing right under the spike, edges just touching");
test(200, 100, false, "diagonal to the spike with only corners touching");
test(280, 180, false, "diagonal to the spike with only corners touching");
test(202, 140, true, "overlapping the spike's left side by 2 px");
test(278, 140, true, "overlapping the spike's right side by 2 px");
test(240, 102, true, "overlapping the top of the spike by 2 px");
test(240, 178, true, "overlapping the bottom of the spike by 2 px");
test(240, 140, true, "right on the spike");
test(255, 150, true, "inside the spike's area");
"""

# ── 5. The enemy that froze ──────────────────────────────────────────────

_FROZEN = _SETUP + """
let enemies = [
  { x: 60, y: 20, size: 30, speed: 120 },
  { x: 200, y: 80, size: 30, speed: 120 },
  { x: 340, y: 140, size: 30, speed: 120 },
];

function spawn() {
  enemies.push({ x: 20 + Math.random() * 420, y: -30, size: 30, speed: 120 });
}
setInterval(spawn, 700);

function update(dt) {
  for (let i = 0; i < enemies.length; i++) {
    const e = enemies[i];
    e.y += e.speed * dt;
    if (e.y > canvas.height) enemies.splice(i, 1);
  }
}

function draw() {
""" + _BG + """  ctx.fillStyle = 'tomato';
  for (const e of enemies) ctx.fillRect(e.x, e.y, e.size, e.size);
}
""" + _LOOP

_FROZEN_FIXED = _fix(
    _FROZEN,
    ("  for (let i = 0; i < enemies.length; i++) {\n    const e = enemies[i];",
     "  for (let i = enemies.length - 1; i >= 0; i--) {\n    const e = enemies[i];"),
)

_FROZEN_CHECK = r"""
cc.frames(2);
const H = document.querySelector("canvas").height;
const put = (...list) => enemies.splice(0, enemies.length, ...list.map(([x, y]) => ({ x, y, size: 30, speed: 120 })));
const at = (x) => enemies.find((e) => e.x === x);
for (const dt of [1000 / 60, 1000 / 30]) {
  const step = 120 * (dt / 1000);
  put([40, H + 10], [100, H + 20], [160, H + 30]);
  cc.frames(1, dt);
  expect(enemies.length === 0, `Three enemies were already below the bottom edge, but after a frame ${enemies.length} of them ${enemies.length === 1 ? "is" : "are"} still there. An enemy should be gone as soon as it has fallen off the bottom.`);

  put([40, H + 10], [100, 100], [160, 150]);
  cc.frames(1, dt);
  expect(enemies.length === 2, `One enemy fell off the bottom edge, so two should be left; there are ${enemies.length}.`);
  for (const [x, y] of [[100, 100], [160, 150]]) {
    const e = at(x);
    expect(e && near(e.y, y + step, 0.5), `An enemy was at y ${y} and should have moved ${step.toFixed(1)} px down this frame, but it is at y ${e ? e.y.toFixed(1) : "nowhere"}. An enemy froze for a frame when another enemy left the screen: every enemy should move on every frame.`);
  }

  put([40, 100], [100, H + 10], [160, 150], [220, H + 20], [280, 200]);
  cc.frames(1, dt);
  expect(enemies.length === 3, `Two of five enemies fell off the bottom edge, so three should be left; there are ${enemies.length}.`);
  for (const [x, y] of [[40, 100], [160, 150], [280, 200]]) {
    const e = at(x);
    expect(e && near(e.y, y + step, 0.5), `An enemy was at y ${y} and should have moved ${step.toFixed(1)} px down this frame, but it is at y ${e ? e.y.toFixed(1) : "nowhere"}. Every enemy should move on every frame, even when others leave the screen.`);
  }
}
cc.frames(30);
expect(enemies.every((e) => e.y <= H + 1), "An enemy stayed in the list after falling below the bottom edge.");
"""

# ── 6. The lights that never come on ─────────────────────────────────────

_LAMPS = _SETUP + """
const lamps = [{ x: 140 }, { x: 240 }, { x: 340 }];
let lit = -1;

for (var i = 0; i < lamps.length; i++) {
  setTimeout(() => {
    lit = i;
  }, (i + 1) * 1000);
}

function draw() {
""" + _BG + """  lamps.forEach((lamp, n) => {
    ctx.fillStyle = n === lit ? 'gold' : '#3a3f55';
    ctx.beginPath();
    ctx.arc(lamp.x, 160, 36, 0, Math.PI * 2);
    ctx.fill();
  });
  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText('lit: ' + lit, 12, 24);
}
""" + _DRAW_ONLY_LOOP

_LAMPS_FIXED = _fix(_LAMPS, ("for (var i = 0;", "for (let i = 0;"))

_LAMPS_CHECK = r"""
const lampsOn = () => {
  const arcs = cc.arcs();
  return lamps.map((l) => arcs.filter((a) => near(a.x, l.x, 0.5)).map((a) => a.fill)[0]);
};
const lights = (colours) => {
  // The lamp that is a different colour from the other two, or -1 if all match.
  for (let n = 0; n < 3; n++) {
    const others = colours.filter((_, m) => m !== n);
    if (others[0] === others[1] && colours[n] !== others[0]) return n;
  }
  return -1;
};
cc.frames(30, 1000 / 60);
expect(lit === -1 && lights(lampsOn()) === -1, "Half a second in, no lamp should be lit yet.");
cc.frames(18, 1000 / 30);
expect(lit === 0, `After about 1.1 seconds the first lamp (number 0) should be lit, but the lit lamp is ${lit < 0 ? "none" : lit < 3 ? lit : "number " + lit + " - there is no such lamp, so no lamp is lit at all"}.`);
expect(lights(lampsOn()) === 0, "After about 1.1 seconds the first lamp should be drawn bright and the other two dim.");
cc.frames(30, 1000 / 30);
expect(lit === 1, `After about 2.1 seconds the second lamp (number 1) should be lit, but the lit lamp is ${lit < 0 ? "none" : lit < 3 ? lit : "number " + lit + " - there is no such lamp"}.`);
expect(lights(lampsOn()) === 1, "After about 2.1 seconds the second lamp should be the bright one.");
cc.frames(60, 1000 / 60);
expect(lit === 2, `After about 3.1 seconds the third lamp (number 2) should be lit, but the lit lamp is ${lit < 0 ? "none" : lit < 3 ? lit : "number " + lit + " - there is no such lamp"}.`);
expect(lights(lampsOn()) === 2, "After about 3.1 seconds the third lamp should be the bright one.");
cc.frames(120, 1000 / 60);
expect(lit === 2, "The last lamp should stay lit once it has come on.");
"""

# ── 7. Sticky keys ───────────────────────────────────────────────────────

_STICKY = _SETUP + """
const player = { x: 240, y: 140, size: 40, speed: 220 };
const held = { left: false, right: false };

addEventListener('keydown', (e) => {
  if (e.key === 'ArrowLeft') held.left = true;
  if (e.key === 'ArrowRight') held.right = true;
});
addEventListener('keyup', (e) => {
  if (e.key === 'ArrowRight') held.right = false;
});

function update(dt) {
  if (held.left) player.x -= player.speed * dt;
  if (held.right) player.x += player.speed * dt;
  player.x = Math.max(0, Math.min(canvas.width - player.size, player.x));
}

function draw() {
""" + _BG + """  ctx.fillStyle = 'tomato';
  ctx.fillRect(player.x, player.y, player.size, player.size);
}
""" + _LOOP

_STICKY_FIXED = _fix(
    _STICKY,
    ("  if (e.key === 'ArrowRight') held.right = false;\n",
     "  if (e.key === 'ArrowLeft') held.left = false;\n  if (e.key === 'ArrowRight') held.right = false;\n"),
)

_STICKY_CHECK = r"""
cc.frames(2);
for (const dt of [1000 / 60, 1000 / 30]) {
  const n = Math.round(0.25 / (dt / 1000));
  for (const [key, name, sign] of [["ArrowRight", "right", 1], ["ArrowLeft", "left", -1]]) {
    player.x = 240;
    cc.press(key);
    cc.frames(n, dt);
    cc.release(key);
    const letGo = player.x;
    expect(sign * (letGo - 240) > 30, `Holding the ${name} arrow for a quarter of a second moved the square from x 240 to x ${Math.round(letGo)}. It should move about 55 px.`);
    cc.frames(n, dt);
    expect(near(player.x, letGo, 0.5), `I held the ${name} arrow for a quarter of a second and let go (the square was at x ${Math.round(letGo)}), but it kept going and a quarter of a second later it was at x ${Math.round(player.x)}. It should stop when the key is released.`);
  }
  player.x = 240;
  cc.press("ArrowRight");
  cc.press("ArrowLeft");
  cc.frames(Math.round(0.1 / (dt / 1000)), dt);
  cc.release("ArrowLeft");
  const mid = player.x;
  cc.frames(n, dt);
  const gain = player.x - mid;
  cc.release("ArrowRight");
  expect(gain > 30, `I held both arrows, let go of the left one and kept holding the right one for a quarter of a second, but the square only moved ${Math.round(gain)} px. It should keep moving right while the right arrow is down.`);
  const stop = player.x;
  cc.frames(n, dt);
  expect(near(player.x, stop, 0.5), "After letting go of both arrows the square kept moving.");
}
"""

# ── 8. Spawns that come late ─────────────────────────────────────────────

_DRIFT = _SETUP + """
let enemies = [];
let spawnTimer = 0;
let spawned = 0;

function spawn() {
  enemies.push({ x: 20 + Math.random() * 440, y: 0, size: 24, speed: 60 });
  spawned += 1;
}

function update(dt) {
  spawnTimer += dt;
  if (spawnTimer >= 1) {
    spawn();
    spawnTimer = 0;
  }
  for (const e of enemies) e.y += e.speed * dt;
  enemies = enemies.filter((e) => e.y < canvas.height);
}

function draw() {
""" + _BG + """  ctx.fillStyle = 'tomato';
  for (const e of enemies) ctx.fillRect(e.x, e.y, e.size, e.size);
  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText('spawned: ' + spawned, 12, 24);
}
""" + _LOOP

_DRIFT_FIXED = _fix(_DRIFT, ("    spawnTimer = 0;\n", "    spawnTimer -= 1;\n"))

_DRIFT_CHECK = r"""
cc.frames(2);
expect(typeof spawned === "number", "`spawned` should count every enemy that has appeared.");
const thirty = (fps) => {
  const before = spawned;
  cc.frames(fps * 30, 1000 / fps);
  return spawned - before;
};
const rates = [60, 10 / 3, 30];
const counts = rates.map(thirty);
const label = (fps) => (fps === 60 ? "60 frames a second" : fps === 30 ? "30 frames a second" : "3 frames a second (a slow computer)");
for (let i = 0; i < rates.length; i++) {
  expect(counts[i] >= 29 && counts[i] <= 31, `In 30 seconds at ${label(rates[i])}, ${counts[i]} enemies appeared. It should be one a second, so about 30, whatever the frame rate (the counts were ${counts.join(", ")} at ${rates.map((r) => Math.round(r * 10) / 10).join(", ")} frames a second).`);
}
"""

# ── 9. The coin worth too much ───────────────────────────────────────────

_COINS = _SETUP + """
const player = { x: 40, y: 140, size: 32, speed: 200 };
const coins = [
  { x: 100, y: 60, size: 24, taken: false },
  { x: 240, y: 200, size: 24, taken: false },
  { x: 400, y: 100, size: 24, taken: false },
];
let score = 0;
""" + _KEYS + """
function overlaps(a, b) {
  return a.x < b.x + b.size && a.x + a.size > b.x && a.y < b.y + b.size && a.y + a.size > b.y;
}

function update(dt) {
  if (keys.has('ArrowRight')) player.x += player.speed * dt;
  if (keys.has('ArrowLeft')) player.x -= player.speed * dt;
  if (keys.has('ArrowDown')) player.y += player.speed * dt;
  if (keys.has('ArrowUp')) player.y -= player.speed * dt;
  for (const coin of coins) {
    if (overlaps(player, coin)) {
      score += 10;
      coin.taken = true;
    }
  }
}

function draw() {
""" + _BG + """  for (const coin of coins) {
    if (coin.taken) continue;
    ctx.fillStyle = 'gold';
    ctx.fillRect(coin.x, coin.y, coin.size, coin.size);
  }
  ctx.fillStyle = 'skyblue';
  ctx.fillRect(player.x, player.y, player.size, player.size);
  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText('score: ' + score, 12, 24);
}
""" + _LOOP

_COINS_FIXED = _fix(_COINS, ("    if (overlaps(player, coin)) {", "    if (!coin.taken && overlaps(player, coin)) {"))

_COINS_CHECK = r"""
cc.frames(2);
expect(score === 0, `The score should start at 0; it is ${score}.`);
const spots = coins.map((c) => ({ x: c.x, y: c.y }));
expect(spots.length >= 3, "There should be three coins.");
const standOn = (i, frames, dt) => {
  player.x = spots[i].x;
  player.y = spots[i].y;
  cc.frames(frames, dt);
};
const away = () => {
  player.x = 30;
  player.y = 270;
  cc.frames(2);
};
standOn(0, 30, 1000 / 60);
expect(score === 10, `I stood on the first coin for half a second and the score is ${score}. One coin is worth 10 points, once.`);
away();
expect(score === 10, `I walked away from the coin and the score is ${score}; it should still be 10.`);
standOn(0, 10, 1000 / 60);
expect(score === 10, `I stepped back onto the coin I had already picked up and the score went to ${score}. A coin that has been picked up is worth nothing more; the score should still be 10.`);
away();
standOn(1, 15, 1000 / 30);
expect(score === 20, `I picked up the second coin (standing on it for half a second at 30 frames a second) and the score is ${score}. It should be 20.`);
away();
standOn(2, 1, 1000 / 60);
expect(score === 30, `I touched the third coin for a single frame and the score is ${score}. It should be 30: every coin is worth 10, however long you touch it.`);
away();
cc.frames(30);
expect(score === 30, `Standing in an empty place the score changed to ${score}. It should stay 30.`);
"""

# ── 10. Life goes wrong ──────────────────────────────────────────────────

_LIFE = _SETUP + """
const COLS = 24;
const ROWS = 16;
const CELL = 20;
let grid = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
for (const [r, c] of [[1, 2], [2, 3], [3, 1], [3, 2], [3, 3]]) grid[r][c] = 1;
for (const [r, c] of [[10, 12], [10, 13], [10, 14]]) grid[r][c] = 1;

addEventListener('keydown', (e) => {
  if (e.key === ' ') nextGeneration();
});

function neighbours(r, c) {
  let n = 0;
  for (let dr = -1; dr <= 1; dr++) {
    for (let dc = -1; dc <= 1; dc++) {
      if (dr === 0 && dc === 0) continue;
      const nr = r + dr;
      const nc = c + dc;
      if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS) n += grid[nr][nc];
    }
  }
  return n;
}

function nextGeneration() {
  const next = grid;
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const n = neighbours(r, c);
      next[r][c] = grid[r][c] ? (n === 2 || n === 3 ? 1 : 0) : (n === 3 ? 1 : 0);
    }
  }
  grid = next;
}

function draw() {
""" + _BG + """  ctx.fillStyle = '#4fd1c5';
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      if (grid[r][c]) ctx.fillRect(c * CELL, r * CELL, CELL - 1, CELL - 1);
    }
  }
  ctx.fillStyle = 'white';
  ctx.font = '14px monospace';
  ctx.fillText('Space: next generation', 300, 20);
}
""" + _DRAW_ONLY_LOOP

_LIFE_FIXED = _fix(_LIFE, ("  const next = grid;\n", "  const next = grid.map((row) => row.slice());\n"))

_LIFE_CHECK = r"""
cc.frames(2);
expect(Array.isArray(grid) && Array.isArray(grid[0]) && grid.length >= 10 && grid[0].length >= 10, "`grid` should be an array of rows, each an array of 0 and 1 cells.");
const R = grid.length;
const C = grid[0].length;
const live = (g) => {
  const out = [];
  g.forEach((row, r) => row.forEach((v, c) => { if (v) out.push(`(${r},${c})`); }));
  return out;
};
const life = (g) => g.map((row, r) => row.map((v, c) => {
  let n = 0;
  for (let dr = -1; dr <= 1; dr++) {
    for (let dc = -1; dc <= 1; dc++) {
      if ((dr || dc) && r + dr >= 0 && r + dr < R && c + dc >= 0 && c + dc < C) n += g[r + dr][c + dc] ? 1 : 0;
    }
  }
  return v ? (n === 2 || n === 3 ? 1 : 0) : (n === 3 ? 1 : 0);
}));
const load = (cells) => {
  for (let r = 0; r < R; r++) for (let c = 0; c < C; c++) grid[r][c] = 0;
  for (const [r, c] of cells) grid[r][c] = 1;
};
const snapshot = () => grid.map((row) => row.map((v) => (v ? 1 : 0)));
const space = () => {
  cc.press(" ");
  cc.release(" ");
  cc.frames(1);
};
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const play = (name, cells, generations) => {
  load(cells);
  let want = snapshot();
  for (let g = 1; g <= generations; g++) {
    want = life(want);
    space();
    const got = snapshot();
    expect(same(got, want), `${name}, generation ${g}: the live cells (row,column) should be ${live(want).join(" ")} but they are ${live(got).join(" ")}.`);
  }
};
play("A row of three cells", [[5, 4], [5, 5], [5, 6]], 2);
play("A block of four cells", [[4, 4], [4, 5], [5, 4], [5, 5]], 2);
play("A glider", [[1, 2], [2, 3], [3, 1], [3, 2], [3, 3]], 6);
let seed = 12345;
const rnd = () => (seed = (seed * 48271) % 2147483647) / 2147483647;
const scatter = [];
for (let r = 0; r < R; r++) for (let c = 0; c < C; c++) if (rnd() < 0.35) scatter.push([r, c]);
play("A scatter of cells across the whole grid", scatter, 3);
load([[6, 6], [6, 7], [7, 6]]);
space();
const dots = cc.rects().filter((r) => r.w < 100).length;
expect(dots === live(snapshot()).length, `The grid holds ${live(snapshot()).length} live cells but ${dots} cells are drawn. Every live cell should be drawn as a square, and only live cells.`);
"""

# ── 11. Break your own (open) ────────────────────────────────────────────

_BREAK = _SETUP + """
const player = { x: 220, y: 260, size: 36, speed: 240 };
const keys = new Set();
addEventListener('keydown', (e) => keys.add(e.key));
addEventListener('keyup', (e) => keys.delete(e.key));

let enemies = [];
let spawnTimer = 0;
let score = 0;

function overlaps(a, b) {
  return a.x < b.x + b.size && a.x + a.size > b.x && a.y < b.y + b.size && a.y + a.size > b.y;
}

function update(dt) {
  if (keys.has('ArrowLeft')) player.x -= player.speed * dt;
  if (keys.has('ArrowRight')) player.x += player.speed * dt;
  player.x = Math.max(0, Math.min(canvas.width - player.size, player.x));

  spawnTimer += dt;
  if (spawnTimer >= 0.8) {
    spawnTimer -= 0.8;
    enemies.push({ x: Math.random() * (canvas.width - 24), y: -24, size: 24, speed: 140 });
  }
  for (const e of enemies) e.y += e.speed * dt;
  const before = enemies.length;
  enemies = enemies.filter((e) => e.y < canvas.height && !overlaps(player, e));
  score += enemies.length < before ? 1 : 0;
}

function draw() {
""" + _BG + """  ctx.fillStyle = 'tomato';
  for (const e of enemies) ctx.fillRect(e.x, e.y, e.size, e.size);
  ctx.fillStyle = 'skyblue';
  ctx.fillRect(player.x, player.y, player.size, player.size);
  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText('score: ' + score, 12, 24);
}
""" + _LOOP

_BREAK_TEACHES = (
    "This one has no check, because you write the bugs. The program in the editor works. Plant ONE bug in it that "
    "looks fine at a glance, run it, and write one sentence of what you SEE going wrong - never where. Then hand "
    "the code to a friend (or to yourself next week) with only that sentence. Ideas: make a speed per frame "
    "instead of per second; loop to <= instead of <; draw the background once instead of every frame; make a "
    "collision count touching edges; remove from an array while looping over it forwards; use var in a loop with "
    "a callback; forget one keyup; reset a timer to 0 instead of subtracting; count the score on every frame; "
    "copy an array by writing next = old. The best bug is the one that takes the longest to find and one line to fix."
)

_RATE_TEACHES = (
    "Some bugs only exist on other people's computers. A game that moves a fixed amount every frame runs at "
    "the speed of the screen: 60 Hz here, 120 Hz or 30 Hz there. Speed belongs to time, not to frames - pixels "
    "per second multiplied by the seconds the last frame took (dt). To hunt this class, ask 'what changes if the "
    "loop runs more or less often?' and then really change it: call update(1 / 30) and update(1 / 120) by hand, "
    "or console.log how far the thing moved in one second. Anything that counts frames instead of seconds is the "
    "suspect."
)

_HEARTS_TEACHES = (
    "An off-by-one error is a loop that runs one time too many or too few, or a limit that is one off. "
    "'i <= n' runs n + 1 times; 'i < n' runs n times; counting from 1 instead of 0 shifts everything by one. "
    "The way to hunt it is to test the edges, not the middle: what happens with 0 items, with 1, with the "
    "maximum? Put console.log(i) in the loop and count the lines, or set the variable to 0 and look at the screen. "
    "Bugs that hide in the middle show at the ends."
)

_TRAILS_TEACHES = (
    "A canvas remembers what you paint on it: nothing erases the old picture unless you do. An animation must "
    "begin every frame by painting over the last one - a background fillRect or a clearRect over the whole "
    "canvas - and only then draw the moving things. Painted before the loop it works for the first frame and "
    "smears after that; painted after the things, it hides them. To hunt it, shrink the program: delete code "
    "until only the moving thing and its drawing are left, then read the order of the drawing calls from top to "
    "bottom in the order they happen."
)

_TOUCH_TEACHES = (
    "Comparisons have an edge: < and <= differ exactly when two numbers are equal, and in a game that is the "
    "case where two boxes touch along an edge. Whether touching counts as a hit is a decision, not an accident, "
    "and for a tile game it matters a lot: a player flush against a wall must be able to slide along it. Two "
    "boxes overlap only when they overlap on BOTH axes, by a positive amount. To hunt a collision bug, stop on "
    "the exact numbers: put the boxes at 200 and 240 with width 40, console.log the result of the test, then try "
    "239 and 241, one case at a time."
)

_FROZEN_TEACHES = (
    "Changing an array while you loop over it moves the ground under your feet. When splice removes item i, "
    "everything after it slides down one place, so the loop's next step (i + 1) jumps over the item that moved "
    "into i. The skipped item misses its update for that frame, and when several things leave at once some are "
    "left behind. To hunt it, make the situation happen on purpose - put three enemies past the edge and run "
    "one frame - and console.log the array before and after. Safe ways: loop backwards, build a new array with "
    "filter, or step back after a splice."
)

_LAMPS_TEACHES = (
    "A function remembers the VARIABLE it uses, not the value the variable had when the function was written. "
    "With 'var' there is one i for the whole loop, so every callback made inside it - a timer, a click handler - "
    "reads the same i, and by the time they run the loop has finished and i is the last value. 'let' makes a fresh "
    "i for each turn of the loop. To hunt it, console.log(i) INSIDE the callback and see that every call says "
    "the same number; then ask what the variable was when the callback finally ran, not when you made it."
)

_STICKY_TEACHES = (
    "State that you switch on must be switched off. A held-key table is only as good as its releases: one "
    "forgotten keyup and a key reads as held for ever. These bugs hide because the common path works - you "
    "press the key and it moves - and only the other path is broken. To hunt it, list every state the program "
    "can be in (each key down, each key up, both) and try every transition, not just the first. console.log the "
    "table on keydown and keyup and watch which flag never goes back."
)

_DRIFT_TEACHES = (
    "A timer that counts up and then 'resets to 0' throws away the overshoot. With a frame of 0.3 seconds a "
    "one-second timer reaches 1.2 and the 0.2 vanishes, so the spawns come every 1.2 seconds instead of every "
    "second - invisible at 60 frames a second, obvious on a slow machine. Subtract the interval instead, and "
    "the leftover carries over. To hunt it, count events over a long time (console.log the spawn count after 30 "
    "seconds) and run at an exaggerated frame rate, because a small error multiplied by many repeats becomes visible."
)

_COINS_TEACHES = (
    "A frame is not an event. The update runs sixty times a second, so a condition that stays true for a while - "
    "standing on a coin - is true on many frames in a row, and anything you do inside it happens many times. "
    "Things that should happen once need a way to say 'already done': a flag, removing the thing, or noticing "
    "the change from false to true. To hunt it, console.log inside the branch that changes the score: if it prints "
    "dozens of lines for a single coin you have found a per-frame bug."
)

_LIFE_TEACHES = (
    "In JavaScript, 'const next = grid' does not make a copy; it makes a second name for the same array. "
    "Write into next and you write into grid, so a cellular automaton starts reading cells it has already changed "
    "in this very generation. Worse, slice() and spread copy only the outside: an array of arrays still shares "
    "its rows, and Array(n).fill([]) puts one row in every slot. To hunt it, use a tiny case with a known "
    "answer (a row of three cells must turn into a column of three) and console.log the grid before, after, "
    "and compare with next === grid."
)

# ── the steps ────────────────────────────────────────────────────────────

DEBUG_STEPS: tuple[Step, ...] = (
    Step(
        id="dbg-01-frame-rate",
        track="Debug it",
        title="Faster on a fast screen",
        teaches=_RATE_TEACHES,
        goal=(
            "A red square (`square`, starting at x 20) is meant to glide across the canvas at 240 pixels a second. On the "
            "author's 60 Hz screen it does, but a friend with a 120 Hz screen sees it go twice as fast, and on a slow 30 Hz "
            "screen it crawls at half the speed. Make it cover the same distance in the same time at any frame rate."
        ),
        starter=_RATE,
        solution=_RATE_FIXED,
        check=_RATE_CHECK,
        hint=(
            "Print how far the square moves in one second at different frame rates (call update by hand with different dt "
            "values). A speed is pixels per second only if each frame multiplies it by the seconds that frame took."
        ),
    ),
    Step(
        id="dbg-02-extra-heart",
        track="Debug it",
        title="One heart too many",
        teaches=_HEARTS_TEACHES,
        goal=(
            "The row of red squares in the corner shows how many lives are left (`lives`, which starts at 3, and pressing x "
            "costs one). But the display always shows one square more than the number of lives: 4 squares at 3 lives, and "
            "even at 0 lives there is still a square. Make it show exactly one square per life."
        ),
        starter=_HEARTS,
        solution=_HEARTS_FIXED,
        check=_HEARTS_CHECK,
        hint="Set lives to 0 by hand (or press x three times) and count the squares. How many times does a loop that starts at 0 and ends at lives run?",
    ),
    Step(
        id="dbg-03-ghost-trails",
        track="Debug it",
        title="Ghost trails",
        teaches=_TRAILS_TEACHES,
        goal=(
            "Move the red square (`player`) with the left and right arrows. It should slide across a clean dark background, "
            "but it leaves a smear of red behind it wherever it has been, as if it were painting with a brush. Make "
            "the canvas show only the square's current place."
        ),
        starter=_TRAILS,
        solution=_TRAILS_FIXED,
        check=_TRAILS_CHECK,
        hint="Read the drawing calls in the order they run on every frame. What paints over the old square, and when does it run?",
    ),
    Step(
        id="dbg-04-near-miss",
        track="Debug it",
        title="Hit by a near miss",
        teaches=_TOUCH_TEACHES,
        goal=(
            "The blue square (`player`, moved with the arrows) turns red when it is hit by the grey spike (`spike`); `touching` says "
            "whether it is. But it already turns red when it is only standing flush against the spike, edge to edge, with no "
            "shared area, and that makes the corridor beside the spike impossible to walk. It should count as touching only "
            "when the two squares really overlap."
        ),
        starter=_TOUCH,
        solution=_TOUCH_FIXED,
        check=_TOUCH_CHECK,
        hint="Put the player at x 200 (the spike is at x 240, both 40 wide) and console.log the overlap test. Which comparison is true when two numbers are equal?",
    ),
    Step(
        id="dbg-05-frozen-enemy",
        track="Debug it",
        title="The enemy that froze",
        teaches=_FROZEN_TEACHES,
        goal=(
            "Red squares (`enemies`) fall down the canvas and are removed once they pass the bottom edge. But whenever one "
            "leaves, another square stops dead for a moment - it misses a frame - and when several leave together some "
            "of them hang about below the screen for an extra frame. Every enemy should move on every frame, and "
            "be gone as soon as it is off the bottom."
        ),
        starter=_FROZEN,
        solution=_FROZEN_FIXED,
        check=_FROZEN_CHECK,
        hint="Put three enemies below the bottom edge by hand (push them into the array), run one frame, and print enemies.length. What happens to the index when an item is removed?",
    ),
    Step(
        id="dbg-06-lights-out",
        track="Debug it",
        title="The lights that never come on",
        teaches=_LAMPS_TEACHES,
        goal=(
            "Three grey lamps (`lamps`) should light up one after another: the first after 1 second, the second after 2 "
            "and the third after 3, each time lighting only that lamp (`lit` is the number of the lit lamp, -1 for none). "
            "But all three timers go off and no lamp lights at all; `lit` ends up as a number there is no lamp for. "
            "Make each lamp light at its own time."
        ),
        starter=_LAMPS,
        solution=_LAMPS_FIXED,
        check=_LAMPS_CHECK,
        hint="console.log(i) inside the timer's function. Does it print 0, 1, 2 - or the same number three times?",
    ),
    Step(
        id="dbg-07-sticky-keys",
        track="Debug it",
        title="Sticky keys",
        teaches=_STICKY_TEACHES,
        goal=(
            "The square (`player`) moves left and right while the arrow keys are held and should stop when they are let go. "
            "Let go of the right arrow and it stops. Let go of the left arrow and the square carries on sliding left until "
            "it hits the wall. Make it stop whenever either key is released, and keep moving if one key is released while "
            "the other is still held."
        ),
        starter=_STICKY,
        solution=_STICKY_FIXED,
        check=_STICKY_CHECK,
        hint="console.log the held table every time a key goes down and every time one goes up. Which flag never goes back to false?",
    ),
    Step(
        id="dbg-08-late-spawns",
        track="Debug it",
        title="Spawns that come late",
        teaches=_DRIFT_TEACHES,
        goal=(
            "An enemy is meant to appear once a second (`spawned` counts them). On a fast computer that is just what "
            "happens, but on a slow one - a few frames a second - enemies come noticeably less often, and after "
            "half a minute the count is well short of 30. Make it one enemy a second at any frame rate."
        ),
        starter=_DRIFT,
        solution=_DRIFT_FIXED,
        check=_DRIFT_CHECK,
        hint="Work it through on paper with a frame of 0.3 seconds: the timer goes 0.3, 0.6, 0.9, 1.2 - and then what happens to the 0.2?",
    ),
    Step(
        id="dbg-09-rich-coin",
        track="Debug it",
        title="The coin worth too much",
        teaches=_COINS_TEACHES,
        goal=(
            "Walk the blue square (`player`) onto a gold coin (the `coins`) to collect it: the coin disappears and `score` should go up by "
            "exactly 10. But stand on a coin for a moment and the score races upward, and a coin you have already "
            "collected keeps paying out if you step back onto its spot. Each coin should be worth 10 points, once."
        ),
        starter=_COINS,
        solution=_COINS_FIXED,
        check=_COINS_CHECK,
        hint="console.log('+10') where the score changes, and stand on one coin for a second. How many lines print, and how many should?",
    ),
    Step(
        id="dbg-10-life",
        track="Debug it",
        title="Life goes wrong",
        teaches=_LIFE_TEACHES,
        goal=(
            "This is Conway's Game of Life on a `grid` of rows of 0 and 1 (cells off the edge count as dead): each press of Space "
            "should make the next generation, where a live cell with 2 or 3 live neighbours survives, a dead cell with "
            "exactly 3 is born and everything else is dead or stays dead. But the patterns come out wrong - a row of three "
            "cells should turn into a column of three, and the glider should glide, but they fall apart or grow. "
            "Make every generation follow the rules."
        ),
        starter=_LIFE,
        solution=_LIFE_FIXED,
        check=_LIFE_CHECK,
        hint="Take the smallest case: three cells in a row. Work out its next generation by hand, then print the grid after one Space. Do the live cells change as the scan moves across the grid?",
    ),
    Step(
        id="dbg-11-break-your-own",
        track="Debug it",
        title="Break your own",
        teaches=_BREAK_TEACHES,
        goal="No check here - plant one bug in this working program, run it, and describe only what you see. Then give it to a friend to fix.",
        starter=_BREAK,
        solution=_BREAK,
        check="",
    ),
)
