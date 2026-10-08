"""The "From blank" Canvas track: build a whole small project yourself.

Every other Canvas track hands you the previous step's finished code and
asks for one change. This one hands you nothing: a spec and a check. Each
project is ONE step whose starter is only the two setup lines, whose goal is
a full spec (numbered requirements, with the names and numbers the check
reads), and whose check plays what you built.

The steps are independent: a starter is NOT the previous solution. The
checks play the program rather than read it, and read only the names the
spec states (left, right, ball, score.left...) - everything else about how it
is written is yours, so any structure that behaves right passes.

Projects: Pong for two, a Flappy-style gap game, Memory cards (clicks),
a falling-blocks stacker, and an open step.
"""

from __future__ import annotations

from code_coach.canvas.content import Step

_SETUP = """const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');
"""

_BLANK = _SETUP + "\n// Your game goes here.\n"

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

# ── 1. Pong for two ──────────────────────────────────────────────────────

_PONG = _SETUP + """
const left = { x: 20, y: 130, w: 10, h: 60, speed: 300 };
const right = { x: 450, y: 130, w: 10, h: 60, speed: 300 };
const ball = { x: 240, y: 160, r: 8, vx: 220, vy: 140 };
const score = { left: 0, right: 0 };

const keys = new Set();
addEventListener('keydown', (e) => {
  keys.add(e.key);
  if (e.key === 'r') resetMatch();
});
addEventListener('keyup', (e) => keys.delete(e.key));

function serve(direction) {
  ball.x = 240;
  ball.y = 160;
  ball.vx = 220 * direction;
  ball.vy = 140;
}

function resetMatch() {
  score.left = 0;
  score.right = 0;
  left.y = 130;
  right.y = 130;
  serve(1);
}

function hitsRect(b, p) {
  const cx = Math.max(p.x, Math.min(b.x, p.x + p.w));
  const cy = Math.max(p.y, Math.min(b.y, p.y + p.h));
  return (b.x - cx) ** 2 + (b.y - cy) ** 2 < b.r ** 2;
}

function movePaddle(p, up, down, dt) {
  if (keys.has(up)) p.y -= p.speed * dt;
  if (keys.has(down)) p.y += p.speed * dt;
  p.y = Math.max(0, Math.min(canvas.height - p.h, p.y));
}

function update(dt) {
  movePaddle(left, 'w', 's', dt);
  movePaddle(right, 'ArrowUp', 'ArrowDown', dt);

  ball.x += ball.vx * dt;
  ball.y += ball.vy * dt;
  if (ball.y - ball.r < 0) {
    ball.y = ball.r;
    ball.vy = Math.abs(ball.vy);
  }
  if (ball.y + ball.r > canvas.height) {
    ball.y = canvas.height - ball.r;
    ball.vy = -Math.abs(ball.vy);
  }
  if (ball.vx < 0 && hitsRect(ball, left)) {
    ball.x = left.x + left.w + ball.r;
    ball.vx = Math.abs(ball.vx);
  }
  if (ball.vx > 0 && hitsRect(ball, right)) {
    ball.x = right.x - ball.r;
    ball.vx = -Math.abs(ball.vx);
  }
  if (ball.x + ball.r < 0) {
    score.right += 1;
    serve(-1);
  }
  if (ball.x - ball.r > canvas.width) {
    score.left += 1;
    serve(1);
  }
}

function draw() {
  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#4fd1c5';
  ctx.fillRect(left.x, left.y, left.w, left.h);
  ctx.fillRect(right.x, right.y, right.w, right.h);
  ctx.fillStyle = 'white';
  ctx.beginPath();
  ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);
  ctx.fill();
  ctx.font = '24px monospace';
  ctx.fillText(`${score.left} : ${score.right}`, 210, 36);
}
""" + _LOOP

_PONG_CHECK = r"""
const cv = document.querySelector("canvas");
const W = cv.width;
const H = cv.height;
expect(typeof left === "object" && left !== null, "Requirement 2: make the left paddle an object called left: const left = { x: 20, y: 130, w: 10, h: 60, speed: 300 };");
expect(typeof right === "object" && right !== null, "Requirement 2: make the right paddle an object called right: const right = { x: 450, y: 130, w: 10, h: 60, speed: 300 };");
expect(near(left.x, 20, 0.01) && near(left.y, 130, 0.01) && left.w === 10 && left.h === 60, `Requirement 2: left starts at x 20, y 130, 10 wide and 60 tall; yours is x ${left.x}, y ${left.y}, w ${left.w}, h ${left.h}.`);
expect(near(right.x, 450, 0.01) && near(right.y, 130, 0.01) && right.w === 10 && right.h === 60, `Requirement 2: right starts at x 450, y 130, 10 wide and 60 tall; yours is x ${right.x}, y ${right.y}, w ${right.w}, h ${right.h}.`);
expect(typeof ball === "object" && ball !== null, "Requirement 4: make the ball an object called ball: { x: 240, y: 160, r: 8, vx, vy }.");
expect(near(ball.x, 240, 0.01) && near(ball.y, 160, 0.01) && ball.r === 8, `Requirement 4: the ball starts at x 240, y 160 with r 8; yours is x ${ball.x}, y ${ball.y}, r ${ball.r}.`);
expect(typeof ball.vx === "number" && Math.abs(ball.vx) > 100 && typeof ball.vy === "number", "Requirement 4: the ball needs a velocity - vx (about 220) and vy - so that it starts moving.");
expect(typeof score === "object" && score !== null && score.left === 0 && score.right === 0, "Requirement 6: keep the points in score.left and score.right, both starting at 0: const score = { left: 0, right: 0 };");

cc.frames(2);
const first = cc.rects();
expect(first.length >= 3 && first[0].x <= 0 && first[0].y <= 0 && first[0].w >= W && first[0].h >= H, "Requirement 1: every frame starts with a dark background over the whole canvas - ctx.fillRect(0, 0, canvas.width, canvas.height) - before anything else is drawn (and the loop must be running: requestAnimationFrame).");
const drawnBox = (p) => cc.rects().some((r) => near(r.x, p.x, 0.01) && near(r.y, p.y, 0.01) && r.w === p.w && r.h === p.h);
expect(drawnBox(left), "Requirement 2: draw the left paddle every frame as a filled rectangle: ctx.fillRect(left.x, left.y, left.w, left.h).");
expect(drawnBox(right), "Requirement 2: draw the right paddle every frame as a filled rectangle: ctx.fillRect(right.x, right.y, right.w, right.h).");
expect(cc.arcs().some((a) => near(a.x, ball.x, 0.01) && near(a.y, ball.y, 0.01) && a.r === ball.r), "Requirement 4: draw the ball every frame as a filled circle: beginPath(), ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2), fill().");

const put = (x, y, vx, vy) => { ball.x = x; ball.y = y; ball.vx = vx; ball.vy = vy; };
const hold = (key, n, dt) => { cc.press(key); cc.frames(n, dt); cc.release(key); };
const slow = 1000 / 30;
const reset = () => { left.y = 130; right.y = 130; put(240, 160, 0, 0); };

reset();
hold("w", 6, slow);
expect(near(left.y, 70, 8), `Requirement 3: holding w for a fifth of a second (at 30 frames a second) moved the left paddle from y 130 to ${Math.round(left.y)}; at speed 300 it should reach about 70. Move by speed * dt, with dt in seconds, while 'w' is held.`);
expect(near(right.y, 130, 0.01), "Requirement 3: w moved the right paddle too. w and s belong to left only.");
reset();
hold("s", 6, slow);
expect(near(left.y, 190, 8), `Requirement 3: holding s for a fifth of a second moved the left paddle from y 130 to ${Math.round(left.y)}; it should reach about 190.`);
reset();
hold("ArrowUp", 12);
expect(near(right.y, 70, 8), `Requirement 3: holding ArrowUp for a fifth of a second moved the right paddle from y 130 to ${Math.round(right.y)}; it should reach about 70.`);
expect(near(left.y, 130, 0.01), "Requirement 3: ArrowUp moved the left paddle too. The arrows belong to right only.");
reset();
hold("ArrowDown", 12);
expect(near(right.y, 190, 8), `Requirement 3: holding ArrowDown for a fifth of a second moved the right paddle from y 130 to ${Math.round(right.y)}; it should reach about 190.`);
reset();
hold("w", 120);
expect(near(left.y, 0, 0.01), `Requirement 3: after two seconds of w the left paddle is at y ${Math.round(left.y)}; it should stop with its top on the canvas edge, y 0.`);
hold("s", 120);
expect(near(left.y, H - left.h, 0.01), `Requirement 3: after two seconds of s the left paddle is at y ${Math.round(left.y)}; it should stop with its bottom on the canvas edge, y ${H - left.h}.`);
hold("ArrowUp", 120);
expect(near(right.y, 0, 0.01), "Requirement 3: the right paddle should stop at the top edge too (y 0).");
hold("ArrowDown", 120);
expect(near(right.y, H - right.h, 0.01), "Requirement 3: the right paddle should stop at the bottom edge too.");

reset();
put(240, 25, 0, -300);
cc.frames(10);
expect(ball.vy > 0, "Requirement 5: the ball hit the top edge and did not turn round. When ball.y - ball.r goes below 0, send it down.");
expect(ball.y - ball.r >= -0.01, "Requirement 5: after the bounce the ball is still partly above the canvas. Put it back on the edge as well as turning it round.");
put(240, H - 25, 0, 300);
cc.frames(10);
expect(ball.vy < 0, "Requirement 5: the ball hit the bottom edge and did not turn round. When ball.y + ball.r goes past the bottom, send it up.");
put(240, 100, 0, 250);
for (let i = 1; i <= 200; i++) {
  cc.frames(1);
  expect(ball.y - ball.r >= -0.01 && ball.y + ball.r <= H + 0.01, `Requirement 5: after ${i} frames the ball is at y ${Math.round(ball.y)} - partly through the top or bottom. Put it back on the edge as well as turning it round.`);
}
expect(near(Math.abs(ball.vy), 250, 0.5), "Requirement 5: a bounce should change the ball's direction, not its speed.");

reset();
put(left.x + left.w + 30, left.y + left.h / 2, -250, 0);
cc.frames(20);
expect(ball.vx > 0, "Requirement 5: the ball ran straight into the left paddle and kept going. When it reaches the paddle, send it back to the right (vx > 0).");
expect(ball.x - ball.r >= left.x + left.w - 0.5, "Requirement 5: after bouncing off the left paddle the ball is still inside it. Sit it on the paddle's face as well as turning it round, so it cannot flip again next frame.");
reset();
put(right.x - 30, right.y + right.h / 2, 250, 0);
cc.frames(20);
expect(ball.vx < 0, "Requirement 5: the ball ran straight into the right paddle and kept going. When it reaches the paddle, send it back to the left (vx < 0).");
expect(ball.x + ball.r <= right.x + 0.5, "Requirement 5: after bouncing off the right paddle the ball is still inside it.");

const total = () => score.left + score.right;
const point = (x, vx) => {
  reset();
  put(x, 20, vx, 0);
  const before = total();
  for (let i = 0; i < 90 && total() === before; i++) cc.frames(1);
  return before;
};
let before = point(60, -300);
expect(total() === before + 1, `Requirement 5/6: a ball sent along the top, well clear of the paddle, should miss it and give a point; the points added are ${total() - before}. A paddle only stops the ball where the paddle actually is.`);
expect(score.right === 1 && score.left === 0, `Requirement 6: the ball went off the LEFT edge, so the right player scores: score.right 1, score.left 0. Yours is score.left ${score.left}, score.right ${score.right}.`);
expect(near(ball.x, 240, 6) && near(ball.y, 160, 6), `Requirement 7: after a point the ball is served from the centre (x 240, y 160); it is at x ${Math.round(ball.x)}, y ${Math.round(ball.y)}.`);
expect(ball.vx < 0, "Requirement 7: after the left player loses a point, the ball is served towards the left player (vx < 0).");
cc.frames(10);
expect(total() === before + 1, "Requirement 6: one miss should be one point. Is the ball still off the edge after the point, scoring again every frame?");
before = point(420, 300);
expect(score.left === 1 && score.right === 1, `Requirement 6: the ball went off the RIGHT edge, so the left player scores. Yours is score.left ${score.left}, score.right ${score.right}.`);
expect(near(ball.x, 240, 6) && near(ball.y, 160, 6), "Requirement 7: after a point on the right the ball is served from the centre too.");
expect(ball.vx > 0, "Requirement 7: after the right player loses a point, the ball is served towards the right player (vx > 0).");

reset();
score.left = 3;
score.right = 7;
cc.frames(1);
const words = cc.texts().join(" ");
expect(/3/.test(words) && /7/.test(words), `Requirement 6: draw both scores as text every frame - with 3 and 7 it should show both numbers; the text on screen is "${words}".`);

score.left = 3;
score.right = 7;
left.y = 0;
right.y = 260;
put(100, 50, 0, 0);
cc.press("r");
cc.frames(1);
cc.release("r");
expect(score.left === 0 && score.right === 0, "Requirement 8: pressing r should start a new match with both scores back at 0.");
expect(near(left.y, 130, 0.01) && near(right.y, 130, 0.01), "Requirement 8: pressing r should put both paddles back at y 130.");
expect(near(ball.x, 240, 6) && near(ball.y, 160, 6), "Requirement 8: pressing r should serve the ball from the centre.");
"""

# ── 2. A Flappy-style gap game ───────────────────────────────────────────

_FLAPPY = _SETUP + """
const bird = { x: 100, y: 160, r: 12, vy: 0 };
const pipes = [];
let spawnTimer = 0;
let score = 0;
let state = 'playing';

addEventListener('keydown', (e) => {
  if (e.key !== ' ') return;
  if (state === 'playing') bird.vy = -300;
  else restart();
});

function restart() {
  bird.y = 160;
  bird.vy = 0;
  pipes.length = 0;
  spawnTimer = 0;
  score = 0;
  state = 'playing';
}

function spawnPipe() {
  pipes.push({ x: canvas.width, w: 50, gapY: 30 + Math.random() * 150, gapH: 110, passed: false });
}

function hitsRect(rx, ry, rw, rh) {
  const cx = Math.max(rx, Math.min(bird.x, rx + rw));
  const cy = Math.max(ry, Math.min(bird.y, ry + rh));
  return (bird.x - cx) ** 2 + (bird.y - cy) ** 2 < bird.r ** 2;
}

function update(dt) {
  if (state !== 'playing') return;
  bird.vy += 900 * dt;
  bird.y += bird.vy * dt;
  if (bird.y - bird.r < 0 || bird.y + bird.r > canvas.height) state = 'over';

  spawnTimer += dt;
  if (spawnTimer >= 1.5) {
    spawnTimer -= 1.5;
    spawnPipe();
  }
  for (const p of pipes) {
    p.x -= 150 * dt;
    if (!p.passed && p.x + p.w < bird.x) {
      p.passed = true;
      score += 1;
    }
    if (hitsRect(p.x, 0, p.w, p.gapY) || hitsRect(p.x, p.gapY + p.gapH, p.w, canvas.height)) {
      state = 'over';
    }
  }
  while (pipes.length && pipes[0].x + pipes[0].w < 0) pipes.shift();
}

function draw() {
  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#68d391';
  for (const p of pipes) {
    ctx.fillRect(p.x, 0, p.w, p.gapY);
    ctx.fillRect(p.x, p.gapY + p.gapH, p.w, canvas.height - (p.gapY + p.gapH));
  }
  ctx.fillStyle = '#f6e05e';
  ctx.beginPath();
  ctx.arc(bird.x, bird.y, bird.r, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = 'white';
  ctx.font = '20px monospace';
  ctx.fillText(`Score: ${score}`, 10, 26);
  if (state === 'over') {
    ctx.font = '32px monospace';
    ctx.fillText('Game over', 150, 150);
    ctx.font = '16px monospace';
    ctx.fillText('Press Space to play again', 140, 180);
  }
}
""" + _LOOP

_FLAPPY_CHECK = r"""
const cv = document.querySelector("canvas");
const W = cv.width;
const H = cv.height;
expect(typeof bird === "object" && bird !== null, "Requirement 2: make the bird an object called bird: const bird = { x: 100, y: 160, r: 12, vy: 0 };");
expect(near(bird.x, 100, 0.01) && near(bird.y, 160, 0.01) && bird.r === 12 && bird.vy === 0, `Requirement 2: the bird starts as { x: 100, y: 160, r: 12, vy: 0 }; yours is x ${bird.x}, y ${bird.y}, r ${bird.r}, vy ${bird.vy}.`);
expect(typeof pipes !== "undefined" && Array.isArray(pipes) && pipes.length === 0, "Requirement 4: keep the pipes in an array called pipes, empty at the start (the first pipe comes after 1.5 seconds).");
expect(typeof score === "number" && score === 0, "Requirement 5: keep the score in let score = 0;");
expect(typeof state === "string" && state === "playing", "Requirement 6: keep what the game is doing in let state = 'playing';");

cc.frames(2);
const first = cc.rects();
expect(first.length >= 1 && first[0].x <= 0 && first[0].y <= 0 && first[0].w >= W && first[0].h >= H, "Requirement 1: every frame starts with a dark background over the whole canvas - ctx.fillRect(0, 0, canvas.width, canvas.height) (and the loop must be running: requestAnimationFrame).");
expect(cc.arcs().some((a) => near(a.x, bird.x, 0.01) && near(a.y, bird.y, 0.01) && a.r === bird.r), "Requirement 2: draw the bird every frame as a filled circle: ctx.arc(bird.x, bird.y, bird.r, 0, Math.PI * 2) then fill().");

// Gravity and the flap, at 30 frames a second so that dt matters.
bird.y = 160;
bird.vy = 0;
cc.frames(15, 1000 / 30);
expect(near(bird.y - 160, 112, 14), `Requirement 2: in half a second of falling from y 160 the bird moved ${Math.round(bird.y - 160)} pixels down; gravity of 900 pixels a second, a second should make it about 112. Add 900 * dt to vy, and vy * dt to y.`);
const falling = bird.y;
cc.press(" ");
cc.frames(1);
cc.release(" ");
expect(bird.vy < -250 && bird.vy > -330, `Requirement 3: a flap should SET vy to -300 (the bird was falling fast, so adding to it is not enough); one frame after the flap vy is ${Math.round(bird.vy)}.`);
cc.frames(4);
expect(bird.y < falling, "Requirement 3: after a flap the bird should rise.");

// Pipes: fly through the middle of every gap for 15 seconds.
const fly = (n, dt) => {
  for (let i = 0; i < n; i++) {
    const p = pipes.find((q) => q.x + q.w > bird.x - bird.r - 2);
    bird.y = p ? p.gapY + p.gapH / 2 : 160;
    bird.vy = 0;
    cc.frames(1, dt);
  }
};
bird.y = 160;
bird.vy = 0;
const seen = new Map();
let lastScore = score;
while (cc.time < 15000) {
  fly(1);
  expect(state === "playing", `Requirement 6: the game ended at ${(cc.time / 1000).toFixed(1)} seconds although the bird was flown through the middle of every gap. The bird should only die by touching a pipe, the floor or the ceiling - and only a pipe that is really at the bird.`);
  for (const q of pipes) if (!seen.has(q)) seen.set(q, { t: cc.time, x: q.x });
  expect(score - lastScore <= 1, `Requirement 5: the score jumped by ${score - lastScore} in a single frame. Count each pipe once - remember which pipes the bird has already passed.`);
  lastScore = score;
}
const born = [...seen.values()];
expect(born.length >= 8, `Requirement 4: ${born.length} pipes appeared in 15 seconds; one every 1.5 seconds makes about 9. Add dt to a timer and, at 1.5, take 1.5 off and push a new pipe.`);
expect(near(born[0].t, 1500, 70), `Requirement 4: the first pipe appeared at ${Math.round(born[0].t)} ms; it should come after 1.5 seconds.`);
for (let i = 1; i < born.length; i++) {
  expect(near(born[i].t - born[i - 1].t, 1500, 40), `Requirement 4: pipes should arrive every 1.5 seconds; pipe ${i + 1} came ${Math.round(born[i].t - born[i - 1].t)} ms after the one before.`);
}
expect(born.every((b) => near(b.x, 480, 6)), "Requirement 4: a new pipe starts at the right edge of the canvas, x = canvas.width.");
const seenPipes = [...seen.keys()];
expect(seenPipes.every((p) => p.w === 50 && p.gapH === 110), "Requirement 4: every pipe is 50 wide with a gap 110 tall: { x, w: 50, gapY, gapH: 110, passed: false }.");
expect(seenPipes.every((p) => p.gapY >= 29.99 && p.gapY <= 180.01), "Requirement 4: the top of the gap, gapY, should be between 30 and 180, so the gap is always fully on the canvas.");
expect(new Set(seenPipes.map((p) => Math.round(p.gapY))).size >= 4, "Requirement 4: the gaps should be at random heights - Math.random() - not all in the same place.");
expect(pipes.length <= 5, `Requirement 4: there are ${pipes.length} pipes in the list, some long gone off the left edge. Take them out of the array once they have left the canvas.`);
expect(score >= 7 && score <= 8, `Requirement 5: the bird flew through about 8 pipes and the score is ${score}. Add 1 once for each pipe the bird gets past.`);
const tail = pipes[pipes.length - 1];
const tailX = tail.x;
fly(15, 1000 / 30);
expect(near(tailX - tail.x, 75, 6), `Requirement 4: in half a second (at 30 frames a second) a pipe moved ${Math.round(tailX - tail.x)} pixels left; at 150 pixels a second it should be 75. Move by 150 * dt.`);
expect(state === "playing", "Requirement 6: the game should still be going.");
fly(1);
expect(cc.texts().some((t) => t.includes(String(score))), `Requirement 5: draw the score as text every frame - it should show ${score} now.`);
const shown = pipes.find((p) => p.x > 0 && p.x + p.w < W);
expect(shown, "Requirement 4: there should be a pipe on the canvas to look at.");
const rs = cc.rects();
expect(rs.some((r) => near(r.x, shown.x, 0.01) && r.y === 0 && r.w === shown.w && near(r.h, shown.gapY, 0.01)), "Requirement 4: draw the top half of each pipe: x, 0, w, gapY.");
expect(rs.some((r) => near(r.x, shown.x, 0.01) && near(r.y, shown.gapY + shown.gapH, 0.01) && r.y + r.h >= H - 0.01), "Requirement 4: draw the bottom half of each pipe: from gapY + gapH down to the bottom of the canvas.");

// Hitting things.
const setPipe = (x, gapY) => {
  pipes.length = 0;
  pipes.push({ x, w: 50, gapY, gapH: 110, passed: false });
};
const place = (y) => { bird.y = y; bird.vy = 0; };
const again = () => {
  cc.press(" ");
  cc.frames(1);
  cc.release(" ");
};
setPipe(bird.x + 120, 200);
place(100);
cc.frames(2);
expect(state === "playing", "Requirement 6: the game ended while the nearest pipe was still 120 pixels away. A pipe only counts when it overlaps the bird across as well as up and down.");
setPipe(bird.x - 200, 200);
place(100);
cc.frames(2);
expect(state === "playing", "Requirement 6: the game ended because of a pipe that is already behind the bird. A pipe behind the bird is harmless.");
setPipe(bird.x - 25, 200);
place(255);
cc.frames(2);
expect(state === "playing", "Requirement 6: the bird is in the middle of the gap, and the game ended. Inside the gap it is safe.");
setPipe(bird.x - 25, 200);
place(100);
cc.frames(2);
expect(state === "over", "Requirement 6: the bird is inside the top half of a pipe and the game carried on. Touching a pipe ends the game: state = 'over'.");
expect(cc.texts().some((t) => /game over/i.test(t)), "Requirement 6: when the game is over, put 'Game over' on the screen.");
const overY = bird.y;
const overX = pipes.map((p) => p.x).join(",");
const overScore = score;
cc.frames(30);
expect(near(bird.y, overY, 0.01) && pipes.map((p) => p.x).join(",") === overX && score === overScore, "Requirement 6: once the game is over nothing should move - the bird, the pipes and the score all stay where they were. Start update() with: if (state !== 'playing') return;");
cc.press(" ");
cc.frames(1);
cc.release(" ");
expect(state === "playing", "Requirement 7: pressing Space after a game over should start again: state back to 'playing'.");
expect(near(bird.y, 160, 2.5), `Requirement 7: a new game starts with the bird back at y 160 (and the Space that restarts it must not also flap); the bird is at y ${Math.round(bird.y)}.`);
expect(Math.abs(bird.vy) < 40, `Requirement 7: a new game starts with the bird at rest (vy 0); its vy is ${Math.round(bird.vy)}.`);
expect(pipes.length === 0, "Requirement 7: a new game starts with no pipes - empty the array, or the one that ended the last game ends this one too.");
expect(score === 0, `Requirement 7: a new game starts with the score back at 0; it is ${score}.`);
expect(!cc.texts().some((t) => /game over/i.test(t)), "Requirement 7: 'Game over' is still on the screen after restarting.");

setPipe(bird.x - 25, 200);
place(302);
cc.frames(2);
expect(state === "over", "Requirement 6: the bird is inside the bottom half of a pipe and the game carried on.");
again();
place(H - 5);
cc.frames(2);
expect(state === "over", "Requirement 6: touching the floor ends the game too.");
again();
place(5);
cc.frames(2);
expect(state === "over", "Requirement 6: touching the ceiling ends the game too.");
again();
expect(state === "playing", "Requirement 7: Space should start a new game each time the game is over.");
"""

# ── 3. Memory cards ──────────────────────────────────────────────────────

_MEMORY = _SETUP + """
const values = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5];
for (let i = values.length - 1; i > 0; i--) {
  const j = Math.floor(Math.random() * (i + 1));
  [values[i], values[j]] = [values[j], values[i]];
}

const cards = [];
for (let i = 0; i < values.length; i++) {
  const col = i % 4;
  const row = Math.floor(i / 4);
  cards.push({ x: 30 + col * 110, y: 20 + row * 100, w: 90, h: 80, value: values[i], faceUp: false, matched: false });
}

let first = null;
let locked = false;
let state = 'playing';

canvas.addEventListener('click', (e) => {
  if (locked || state !== 'playing') return;
  const box = canvas.getBoundingClientRect();
  const x = (e.clientX - box.left) * (canvas.width / box.width);
  const y = (e.clientY - box.top) * (canvas.height / box.height);
  const card = cards.find((c) => !c.faceUp && x >= c.x && x < c.x + c.w && y >= c.y && y < c.y + c.h);
  if (!card) return;
  card.faceUp = true;
  if (!first) {
    first = card;
    return;
  }
  const second = card;
  const a = first;
  first = null;
  if (a.value === second.value) {
    a.matched = true;
    second.matched = true;
    if (cards.every((c) => c.matched)) state = 'won';
  } else {
    locked = true;
    setTimeout(() => {
      a.faceUp = false;
      second.faceUp = false;
      locked = false;
    }, 800);
  }
});

function draw() {
  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.font = '36px monospace';
  for (const c of cards) {
    ctx.fillStyle = c.faceUp ? '#f6e05e' : '#2d3a5a';
    ctx.fillRect(c.x, c.y, c.w, c.h);
    if (c.faceUp) {
      ctx.fillStyle = '#10141f';
      ctx.fillText(String(c.value), c.x + 36, c.y + 52);
    }
  }
  if (state === 'won') {
    ctx.fillStyle = 'white';
    ctx.font = '32px monospace';
    ctx.fillText('You win!', 170, 316);
  }
}

function loop() {
  draw();
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
"""

_MEMORY_CHECK = r"""
const cv = document.querySelector("canvas");
expect(typeof cards !== "undefined" && Array.isArray(cards) && cards.length === 12, "Requirement 1: make an array called cards with 12 cards, in a grid of 4 columns by 3 rows.");
const want = new Set();
for (let row = 0; row < 3; row++) for (let col = 0; col < 4; col++) want.add((30 + col * 110) + "," + (20 + row * 100));
const got = new Set(cards.map((c) => c.x + "," + c.y));
expect(got.size === 12 && [...want].every((p) => got.has(p)), "Requirement 1: the cards make a grid: x = 30 + col * 110 and y = 20 + row * 100, for columns 0 to 3 and rows 0 to 2.");
expect(cards.every((c) => c.w === 90 && c.h === 80), "Requirement 1: every card is 90 wide and 80 tall (w: 90, h: 80).");
expect(cards.every((c) => c.faceUp === false && c.matched === false), "Requirement 1: every card starts face down and unmatched: faceUp: false, matched: false.");
const counts = {};
for (const c of cards) counts[c.value] = (counts[c.value] || 0) + 1;
expect([0, 1, 2, 3, 4, 5].every((v) => counts[v] === 2) && Object.keys(counts).length === 6, "Requirement 2: each card has a value, and the values 0 to 5 each appear on exactly two cards - 6 pairs.");
const order = cards.slice().sort((a, b) => a.y - b.y || a.x - b.x).map((c) => c.value).join("");
expect(order !== "001122334455" && order !== "012345012345", "Requirement 2: the values should be shuffled - the cards are dealt in order. Shuffle them with Math.random().");
expect(typeof state === "string" && state === "playing", "Requirement 6: keep what the game is doing in let state = 'playing';");

const click = (x, y) => {
  const el = document.querySelector("canvas");
  const box = el.getBoundingClientRect();
  const sx = box.width / el.width;
  const sy = box.height / el.height;
  el.dispatchEvent(new MouseEvent("click", { clientX: box.left + x * sx, clientY: box.top + y * sy, offsetX: x * sx, offsetY: y * sy, bubbles: true }));
};
const tap = (c) => click(c.x + c.w / 2, c.y + c.h / 2);
const up = () => cards.filter((c) => c.faceUp).length;
const labels = () => cc.texts().map((t) => t.trim());
const fillOf = (c) => {
  const hits = cc.rects().filter((r) => r.x === c.x && r.y === c.y && r.w === c.w && r.h === c.h);
  return hits.length ? hits[hits.length - 1].fill : null;
};

cc.frames(2);
const first = cc.rects();
expect(first.length >= 13, "Requirement 3: every frame, draw a dark background and then each card as a rectangle - 13 rectangles in all.");
expect(cards.every((c) => fillOf(c) !== null), "Requirement 3: draw every card each frame as a rectangle at its own x, y, w and h (a requestAnimationFrame loop that keeps redrawing).");
for (let v = 0; v < 6; v++) expect(!labels().includes(String(v)), "Requirement 3: a face-down card must not show its value. Write the value only for cards with faceUp true.");

click(125, 60);
click(5, 5);
click(470, 310);
cc.frames(1);
expect(up() === 0, "Requirement 4: a click in the gap between cards, or outside the grid, should do nothing. (The click arrives in page pixels - the canvas may be drawn bigger than 480 wide - so subtract getBoundingClientRect().left and scale by canvas.width / rect.width.)");

const byValue = {};
for (const c of cards) (byValue[c.value] = byValue[c.value] || []).push(c);
const pairs = [0, 1, 2, 3, 4, 5].map((v) => byValue[v]);
const a = pairs[0][0];
const b = pairs[1][0];
const other = pairs[2][0];

tap(a);
cc.frames(1);
expect(a.faceUp === true, "Requirement 4: clicking the middle of a face-down card should turn it face up - set its faceUp to true. (The click arrives in page pixels, not canvas pixels: subtract getBoundingClientRect().left and scale by canvas.width / rect.width.)");
expect(up() === 1, "Requirement 4: one click should turn over exactly one card.");
expect(labels().includes(String(a.value)), "Requirement 3: a face-up card shows its value - write it on the card with fillText.");
expect(fillOf(a) !== fillOf(other), "Requirement 3: a face-up card should be drawn in a different colour from a face-down one.");
tap(a);
cc.frames(1);
expect(a.faceUp === true && a.matched === false && up() === 1, "Requirement 4: clicking a card that is already face up does nothing - it must not turn it back over or count as the second card (a card does not match itself).");

tap(b);
cc.frames(1);
expect(a.faceUp && b.faceUp && up() === 2, "Requirement 5: two different cards are showing, so both should stay face up for a moment so the player can see them.");
expect(!a.matched && !b.matched, "Requirement 5: cards with different values must not be matched.");
cc.frames(10);
tap(other);
cc.frames(26);
expect(a.faceUp && b.faceUp, "Requirement 5: the two different cards flipped back before 800 ms had passed. Leave them face up for 800 ms - setTimeout is the tool.");
expect(!other.faceUp, "Requirement 5: while two different cards are showing, clicks should do nothing - a third card turned over.");
cc.frames(30);
expect(!a.faceUp && !b.faceUp, "Requirement 5: after 800 ms the two different cards should flip back face down.");
expect(up() === 0 && !a.matched && !b.matched, "Requirement 5: after a mismatch, nothing should be left face up or matched.");

tap(a);
tap(pairs[0][1]);
cc.frames(1);
expect(a.matched === true && pairs[0][1].matched === true, "Requirement 5: two cards with the same value are a match - set matched to true on both.");
expect(a.faceUp && pairs[0][1].faceUp, "Requirement 5: matched cards stay face up.");
expect(state === "playing", "Requirement 6: one pair found does not win - the game is won only when every card is matched.");
cc.frames(80);
expect(a.faceUp && pairs[0][1].faceUp && up() === 2, "Requirement 5: matched cards must stay face up for good, not flip back.");
tap(pairs[1][0]);
cc.frames(1);
expect(pairs[1][0].faceUp, "Requirement 5: after a match the player can go straight on - the next click should turn a card over.");
tap(a);
cc.frames(1);
expect(a.faceUp && up() === 3, "Requirement 4: clicking a card that is already matched does nothing.");
tap(pairs[1][1]);
cc.frames(1);
expect(pairs[1][0].matched && pairs[1][1].matched, "Requirement 5: the second pair should match too - a click on a matched card must not count as a pick.");
tap(pairs[2][0]);
tap(pairs[2][1]);
tap(pairs[3][0]);
tap(pairs[3][1]);
tap(pairs[4][0]);
tap(pairs[4][1]);
cc.frames(1);
expect(cards.filter((c) => c.matched).length === 10, `Requirement 5: five pairs should be matched now; ${cards.filter((c) => c.matched).length / 2} are.`);
expect(state === "playing", "Requirement 6: one pair is still hidden, so the game is not won yet.");
expect(!cc.texts().some((t) => /win/i.test(t)), "Requirement 6: do not say 'You win!' until the last pair is found.");
tap(pairs[5][0]);
tap(pairs[5][1]);
cc.frames(1);
expect(state === "won", `Requirement 6: with every card matched the game is won; state is '${state}'.`);
expect(cc.texts().some((t) => /you win/i.test(t)), "Requirement 6: put 'You win!' on the screen when the game is won.");
"""

# ── 4. A falling-blocks stacker ─────────────────────────────────────────

_STACKER = _SETUP + """
const COLS = 10;
const ROWS = 20;
const CELL = 16;
const LEFT = 160;

const grid = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
const piece = { col: 4, row: 0 };
let timer = 0;
let score = 0;
let state = 'playing';

function fits(col, row) {
  for (let dr = 0; dr < 2; dr++) {
    for (let dc = 0; dc < 2; dc++) {
      const c = col + dc;
      const r = row + dr;
      if (c < 0 || c >= COLS || r >= ROWS || grid[r][c]) return false;
    }
  }
  return true;
}

function spawn() {
  piece.col = 4;
  piece.row = 0;
  if (!fits(piece.col, piece.row)) state = 'over';
}

function clearLines() {
  for (let r = ROWS - 1; r >= 0; r--) {
    if (grid[r].every((v) => v)) {
      grid.splice(r, 1);
      grid.unshift(Array(COLS).fill(0));
      score += 10;
      r++;
    }
  }
}

function lock() {
  for (let dr = 0; dr < 2; dr++) {
    for (let dc = 0; dc < 2; dc++) grid[piece.row + dr][piece.col + dc] = 1;
  }
  clearLines();
  spawn();
}

function stepDown() {
  if (fits(piece.col, piece.row + 1)) piece.row += 1;
  else lock();
}

function restart() {
  for (const row of grid) row.fill(0);
  score = 0;
  timer = 0;
  state = 'playing';
  piece.col = 4;
  piece.row = 0;
}

addEventListener('keydown', (e) => {
  if (state === 'over') {
    if (e.key === 'Enter') restart();
    return;
  }
  if (e.key === 'ArrowLeft' && fits(piece.col - 1, piece.row)) piece.col -= 1;
  if (e.key === 'ArrowRight' && fits(piece.col + 1, piece.row)) piece.col += 1;
  if (e.key === 'ArrowDown') {
    while (fits(piece.col, piece.row + 1)) piece.row += 1;
    lock();
  }
});

function update(dt) {
  if (state !== 'playing') return;
  timer += dt;
  if (timer >= 0.5) {
    timer -= 0.5;
    stepDown();
  }
}

function cell(col, row) {
  ctx.fillRect(LEFT + col * CELL, row * CELL, CELL - 1, CELL - 1);
}

function draw() {
  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#1a2236';
  ctx.fillRect(LEFT, 0, COLS * CELL, ROWS * CELL);
  ctx.fillStyle = '#f6ad55';
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      if (grid[r][c]) cell(c, r);
    }
  }
  ctx.fillStyle = '#4fd1c5';
  for (let dr = 0; dr < 2; dr++) {
    for (let dc = 0; dc < 2; dc++) cell(piece.col + dc, piece.row + dr);
  }
  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText(`Score: ${score}`, 10, 22);
  if (state === 'over') {
    ctx.font = '24px monospace';
    ctx.fillText('Game over', 190, 150);
    ctx.font = '12px monospace';
    ctx.fillText('Press Enter to play again', 180, 175);
  }
}
""" + _LOOP

_STACKER_CHECK = r"""
const cv = document.querySelector("canvas");
const W = cv.width;
expect(typeof grid !== "undefined" && Array.isArray(grid) && grid.length === 20 && grid.every((r) => Array.isArray(r) && r.length === 10), "Requirement 1: make grid, an array of 20 rows each holding 10 cells, read as grid[row][col].");
expect(grid.every((r) => r.every((v) => !v)), "Requirement 1: the grid starts empty - every cell 0.");
expect(typeof piece === "object" && piece !== null && piece.col === 4 && piece.row === 0, "Requirement 2: keep the falling piece in piece = { col, row }, its top-left cell, starting at col 4, row 0.");
expect(typeof score === "number" && score === 0, "Requirement 7: keep the score in let score = 0;");
expect(typeof state === "string" && state === "playing", "Requirement 8: keep what the game is doing in let state = 'playing';");

const cells = () => grid.map((r) => r.map((v) => (v ? 1 : 0)));
const total = () => cells().flat().reduce((x, y) => x + y, 0);
const clearGrid = () => { for (const r of grid) r.fill(0); };
const tap = (key, frames = 1) => { cc.press(key); cc.frames(frames); cc.release(key); };
const rowText = (r) => JSON.stringify(cells()[r]);

// Gravity: one row every half second.
cc.frames(28);
expect(piece.row === 0, `Requirement 3: after 0.47 seconds the piece is on row ${piece.row}; it should still be on row 0 - it moves down one row every 0.5 seconds.`);
cc.frames(5);
expect(piece.row === 1, `Requirement 3: after 0.55 seconds the piece should be on row 1; it is on row ${piece.row}. Add dt to a timer, and every 0.5 seconds take 0.5 off it and move down one row.`);
cc.frames(30);
expect(piece.row === 2, `Requirement 3: after 1.05 seconds the piece should be on row 2; it is on row ${piece.row}.`);

// Left and right.
piece.col = 4;
tap("ArrowLeft");
expect(piece.col === 3, `Requirement 4: one press of ArrowLeft should move the piece one column left, from 4 to 3; it is at ${piece.col}.`);
tap("ArrowRight");
expect(piece.col === 4, `Requirement 4: one press of ArrowRight should move the piece one column right; it is at ${piece.col}.`);
for (let i = 0; i < 7; i++) tap("ArrowLeft");
expect(piece.col === 0, `Requirement 4: the piece should stop at the left wall, col 0; after 7 presses it is at col ${piece.col}.`);
for (let i = 0; i < 12; i++) tap("ArrowRight");
expect(piece.col === 8, `Requirement 4: the piece is 2 cells wide, so the right wall stops it at col 8; after 12 presses it is at col ${piece.col}.`);
piece.col = 4;
for (let r = 0; r < 20; r++) grid[r][6] = 1;
tap("ArrowRight");
expect(piece.col === 4, "Requirement 4: the piece should not move into a filled cell - there is a wall of filled cells just to its right and it went through.");
tap("ArrowLeft");
expect(piece.col === 3, "Requirement 4: moving the other way, where nothing is in the way, should still work.");
clearGrid();

// Drop and lock.
piece.col = 4;
piece.row = 0;
tap("ArrowDown", 2);
expect(grid[18][4] && grid[18][5] && grid[19][4] && grid[19][5], `Requirement 5/6: ArrowDown should drop the piece all the way down and lock it into the grid: cells (row 18, 19) x (col 4, 5) should be 1. Rows 18 and 19 are ${rowText(18)} and ${rowText(19)}.`);
expect(total() === 4, `Requirement 6: a piece locks as exactly 4 filled cells; the grid has ${total()}.`);
expect(piece.col === 4 && piece.row <= 1, `Requirement 6: after locking, a new piece starts at col 4, row 0; it is at col ${piece.col}, row ${piece.row}.`);
expect(state === "playing", "Requirement 6: nothing is wrong yet - the game should still be playing.");
piece.col = 4;
piece.row = 0;
tap("ArrowDown", 2);
expect(grid[16][4] && grid[16][5] && grid[17][4] && grid[17][5] && total() === 8, `Requirement 6: the second piece should land ON the first one, in rows 16 and 17, not fall through it. The grid holds ${total()} filled cells.`);
clearGrid();

// Full rows.
const score0 = score;
for (const c of [0, 1, 2, 3, 4, 5, 8, 9]) grid[19][c] = 1;
grid[17][0] = 1;
piece.col = 6;
piece.row = 0;
tap("ArrowDown", 2);
expect(score - score0 === 10, `Requirement 7: a full row was made and the score went up by ${score - score0}; it should go up by 10 for each cleared row.`);
expect(rowText(19) === JSON.stringify([0, 0, 0, 0, 0, 0, 1, 1, 0, 0]), `Requirement 7: the full bottom row should be removed and everything above should drop one row, so the bottom row now holds only the top half of the block that completed it (cells 6 and 7). Row 19 is ${rowText(19)}.`);
expect(rowText(18) === JSON.stringify([1, 0, 0, 0, 0, 0, 0, 0, 0, 0]), `Requirement 7: the cell that was on row 17 should have dropped to row 18. Row 18 is ${rowText(18)}.`);
expect(total() === 3, `Requirement 7: after the clear there should be 3 filled cells; the grid has ${total()}.`);
clearGrid();

const score1 = score;
for (const r of [18, 19]) for (let c = 0; c < 10; c++) if (c !== 4 && c !== 5) grid[r][c] = 1;
piece.col = 4;
piece.row = 0;
tap("ArrowDown", 2);
expect(total() === 0, `Requirement 7: two full rows were made at once and ${total()} cells are left; both rows should be cleared. If you remove rows in a loop, take care not to skip the one that drops into the place of the row you just removed.`);
expect(score - score1 === 20, `Requirement 7: clearing two rows at once should add 20 to the score; it added ${score - score1}.`);
clearGrid();

const score2 = score;
for (const c of [0, 1, 5, 6, 7, 8, 9]) grid[19][c] = 1;
piece.col = 2;
piece.row = 0;
tap("ArrowDown", 2);
expect(score === score2 && total() === 11, `Requirement 7: the bottom row still has a hole (col 4), so it is not full and must stay. The score changed by ${score - score2} and the grid has ${total()} filled cells (should be 11).`);
clearGrid();
cc.frames(1);
expect(cc.texts().some((t) => t.includes(String(score))), `Requirement 9: draw the score as text every frame - it should show ${score}.`);

// Drawing.
const lay = cc.rects();
expect(lay.length >= 1 && lay[0].x <= 0 && lay[0].y <= 0 && lay[0].w >= W, "Requirement 9: every frame starts with a dark background over the whole canvas (and the loop must be running: requestAnimationFrame).");
grid[19][0] = 1;
grid[19][9] = 1;
piece.col = 4;
piece.row = 3;
cc.frames(1);
const hasCell = (c, r) => cc.rects().some((q) => q.x >= 160 + c * 16 - 0.01 && q.x <= 160 + c * 16 + 2 && q.y >= r * 16 - 0.01 && q.y <= r * 16 + 2 && q.w >= 14 && q.w <= 16 && q.h >= 14 && q.h <= 16);
expect(hasCell(0, 19) && hasCell(9, 19), "Requirement 1: draw every filled cell of the grid as a square, 16 pixels (15 leaves a gap) at x 160 + col * 16, y row * 16 - the corners (col 0 and col 9, row 19) are missing.");
expect(hasCell(piece.col, piece.row) && hasCell(piece.col + 1, piece.row) && hasCell(piece.col, piece.row + 1) && hasCell(piece.col + 1, piece.row + 1), "Requirement 9: draw the falling piece's four cells every frame, the same size and place as the grid's cells.");
clearGrid();

// The end.
grid[0][4] = 1;
piece.col = 0;
piece.row = 0;
tap("ArrowDown", 2);
expect(state === "over", `Requirement 8: a new piece has no room to start - col 4, row 0 is already filled - so the game is over; state is '${state}'.`);
cc.frames(1);
expect(cc.texts().some((t) => /game over/i.test(t)), "Requirement 8: put 'Game over' on the screen when the game is over.");
const frozen = rowText(19) + rowText(18) + piece.col + "," + piece.row;
tap("ArrowLeft");
tap("ArrowRight");
tap("ArrowDown", 2);
cc.frames(60);
expect(frozen === rowText(19) + rowText(18) + piece.col + "," + piece.row, "Requirement 8: once the game is over nothing should move: no gravity, no keys.");
cc.press("Enter");
cc.frames(1);
cc.release("Enter");
expect(state === "playing", "Requirement 8: Enter after a game over should start again: state back to 'playing'.");
expect(total() === 0 && score === 0, `Requirement 8: a new game starts with an empty grid (${total()} filled) and score 0 (it is ${score}).`);
expect(piece.col === 4 && piece.row <= 1, "Requirement 8: a new game starts with the piece at col 4, row 0.");
expect(!cc.texts().some((t) => /game over/i.test(t)), "Requirement 8: 'Game over' is still on the screen after restarting.");
"""

# ── 5. Your own game ────────────────────────────────────────────────────

_OPEN_TEACHES = (
    "Nothing to match here and no check: start from the two setup lines and "
    "build any small canvas game you like, from nothing, the way the four "
    "projects before it asked. Some ideas, roughly easiest first: Snake "
    "(a list of cells, a direction, eat to grow); Pong against the computer "
    "(its paddle follows the ball, a little late); Asteroids-lite (a ship "
    "that turns and thrusts, rocks that drift and wrap round the edges); "
    "Whack-a-mole with the mouse and a countdown; Simon (a growing "
    "sequence of coloured pads to repeat); the Chrome dinosaur (jump over "
    "cactuses that come faster and faster); Space Invaders; a platformer "
    "with one screen and a jump; Minesweeper on a grid; Conway's Game of "
    "Life with a click to toggle cells; a top-down maze with a key and a "
    "door. Start with one square that moves, then add a thing at a time - "
    "the same order every project here was built in."
)


BLANK_STEPS: tuple[Step, ...] = (
    Step(
        id="blank-01-pong",
        track="From blank",
        title="Pong for two",
        teaches=(
            "No starter and no steps: a spec and a check that plays what you "
            "build. Break it down the way the earlier tracks did. Game "
            "loop with dt first; then the two paddles and a Set of held "
            "keys (e.key is 'w', 's', 'ArrowUp', 'ArrowDown'); then the ball "
            "and its four edges; then the bounce off a paddle, which only "
            "counts where the paddle is; then going off the sides, which is "
            "a point and a serve rather than a bounce. Keep the names the "
            "spec gives - the check reads those, and nothing else."
        ),
        goal=(
            "Build Pong for two players from a blank page. The names and numbers below are what the check reads; the rest is yours. "
            "1) Redraw every frame (requestAnimationFrame, with dt in seconds): first a dark background over the whole canvas, then everything below. "
            "2) Two paddles kept in `left` and `right`, each { x, y, w: 10, h: 60, speed: 300 }: `left` at x 20 and `right` at x 450, both at y 130. Draw each as a filled rectangle. "
            "3) The keys 'w' and 's' move `left` up and down at its speed, and 'ArrowUp' and 'ArrowDown' move `right`; neither paddle can leave the canvas. "
            "4) The ball is kept in `ball` = { x: 240, y: 160, r: 8, vx, vy }, drawn as a filled circle, starting with a vx of about 220 and some vy. "
            "5) The ball bounces off the top and bottom edges, and off a paddle where the paddle actually is - each time it ends up heading away. "
            "6) When the ball goes fully off the left edge the right player scores, and off the right edge the left player scores: keep the points in `score.left` and `score.right` (both start at 0) and draw them as text. "
            "7) After each point the ball is served from x 240, y 160, towards the player who just lost it. "
            "8) Pressing 'r' starts a new match: both scores 0, both paddles back at y 130, the ball served from the centre."
        ),
        starter=_BLANK,
        solution=_PONG,
        check=_PONG_CHECK,
        hint=(
            "One function can move both paddles: movePaddle(p, upKey, downKey, dt). "
            "Test the ball against a paddle only while it is heading towards it (vx < 0 for left), "
            "and put it on the paddle's face when it bounces."
        ),
    ),
    Step(
        id="blank-02-flappy",
        track="From blank",
        title="A Flappy-style gap game",
        teaches=(
            "A second whole game from nothing. The new parts: gravity is an "
            "acceleration - add to vy each frame, then move by vy - and a "
            "flap sets vy rather than adding to it, or a falling bird barely "
            "notices. Pipes are an array you push to on a timer and trim as "
            "they leave; each is two rectangles round a gap; and a pipe "
            "should add to the score once, so it needs to remember it has "
            "been passed. The bird is a circle and a pipe half is a box: "
            "the circle-against-box test from Breakout is the same here."
        ),
        goal=(
            "Build a Flappy-style game from a blank page. The names and numbers below are what the check reads; the rest is yours. "
            "1) Redraw every frame (requestAnimationFrame, dt in seconds), a dark background first. "
            "2) The bird is `bird` = { x: 100, y: 160, r: 12, vy: 0 }, drawn as a filled circle. Gravity adds 900 to vy every second, and y moves by vy * dt. "
            "3) Space (e.key ' ') flaps: it sets vy to -300 (sets it, rather than adding to it). "
            "4) `pipes` is an array, empty at the start. Every 1.5 seconds a pipe is pushed in at x = canvas.width: { x, w: 50, gapY, gapH: 110, passed: false }, where gapY, the top of the gap, is random from 30 to 180. Draw each pipe as two rectangles (from the top down to gapY, and from gapY + gapH to the bottom of the canvas). Pipes move left at 150 pixels a second and leave the array once they are off the left edge. "
            "5) `score` (starts at 0) goes up by 1, once, for each pipe the bird gets past; draw it as text. "
            "6) `state` starts as 'playing'. It becomes 'over' when the bird touches a pipe, the floor or the ceiling; after that nothing moves and 'Game over' is on the screen. "
            "7) Space while the game is over starts again: bird back at y 160 with vy 0 (that press does not also flap), no pipes, score 0, state 'playing'."
        ),
        starter=_BLANK,
        solution=_FLAPPY,
        check=_FLAPPY_CHECK,
        hint=(
            "Each frame: vy += 900 * dt; y += vy * dt. A pipe half is hit when the circle's nearest point on the box is "
            "closer than r - the same hitsRect as Breakout, called twice per pipe."
        ),
    ),
    Step(
        id="blank-03-memory",
        track="From blank",
        title="Memory cards",
        teaches=(
            "This one is driven by the mouse, and by time. A click event "
            "gives page pixels, so work out where it is in canvas pixels "
            "first (subtract rect.left, scale by canvas.width / rect.width), "
            "then find which card holds that point. The rules are a small "
            "state machine: no card picked, one picked, or two different "
            "cards showing while a timer runs - and during that last state "
            "clicks must be ignored. setTimeout(fn, 800) runs fn once, later; "
            "keep the two cards in variables so fn can turn them back. "
            "Shuffle with Fisher-Yates: for i from the end down to 1, swap "
            "item i with a random item from 0 to i."
        ),
        goal=(
            "Build a Memory card game from a blank page. The names and numbers below are what the check reads; the rest is yours. "
            "1) `cards` is an array of 12 cards in a grid of 4 columns by 3 rows: { x: 30 + col * 110, y: 20 + row * 100, w: 90, h: 80, value, faceUp: false, matched: false }. "
            "2) The values 0 to 5 each appear on exactly two cards, and they are shuffled. "
            "3) Redraw every frame (requestAnimationFrame): a dark background, then each card as a rectangle - face down in one colour with no text, face up in another colour with its value written on it (fillText). "
            "4) A click on the canvas turns a face-down card face up. Clicks between cards or outside the grid, and clicks on a card that is already face up, do nothing. (Work out the click's place in canvas pixels - the canvas may be drawn bigger than 480 wide.) "
            "5) When the second card is turned: equal values - both get matched: true and stay face up; different values - both stay face up for 800 ms and then turn back down (setTimeout is the tool for that). While two different cards are showing, clicks do nothing. "
            "6) `state` starts as 'playing'; when every card is matched it becomes 'won' and 'You win!' is on the screen."
        ),
        starter=_BLANK,
        solution=_MEMORY,
        check=_MEMORY_CHECK,
        hint=(
            "canvas.addEventListener('click', (e) => { ... }) - find the card with cards.find((c) => !c.faceUp && x >= c.x && "
            "x < c.x + c.w && y >= c.y && y < c.y + c.h). Remember the first pick in a variable; on a mismatch set a locked flag, "
            "setTimeout to turn both back and unlock."
        ),
    ),
    Step(
        id="blank-04-stacker",
        track="From blank",
        title="Falling blocks",
        teaches=(
            "A small Tetris with one kind of piece, a 2 by 2 square, so "
            "there is no rotation - the parts are the board and the rules "
            "around it. The board is a grid you read as grid[row][col]; "
            "the falling piece is NOT in the grid, only its top-left cell "
            "is kept, and it is written into the grid when it lands (it "
            "locks). One function, fits(col, row), that asks 'would the "
            "piece be inside the walls and on empty cells there?' answers "
            "every question: can it move left, right, down, can a new one "
            "start. A full row is removed and an empty row put on the top, "
            "so everything above drops - careful removing rows while "
            "counting through them, because the next row takes the place "
            "of the one you removed."
        ),
        goal=(
            "Build a falling-blocks stacker from a blank page. The names and numbers below are what the check reads; the rest is yours. "
            "1) `grid` is 20 rows of 10 cells read as grid[row][col], 0 for empty and 1 for filled, and starts empty. Redraw every frame (requestAnimationFrame, dt in seconds), a dark background first, and draw each filled cell as a square 16 pixels wide (15 leaves a gap) at x 160 + col * 16, y row * 16. "
            "2) There is one kind of piece, a 2 by 2 square, kept in `piece` = { col, row } - its top-left cell. A new piece starts at col 4, row 0; draw its four cells. "
            "3) Every 0.5 seconds the piece moves down one row. "
            "4) ArrowLeft and ArrowRight move it one column for each key press, never into a wall or a filled cell. "
            "5) ArrowDown drops it all the way down at once. "
            "6) A piece that cannot move down any further (the floor, or a filled cell below) locks: its four cells become 1 in the grid, full rows are cleared, and a new piece starts. "
            "7) A full row (all 10 cells filled) is removed and everything above it drops one row; `score` (starts at 0) goes up by 10 for each row removed, and is drawn as text. "
            "8) `state` starts as 'playing'. If a new piece starts on filled cells, state becomes 'over' and 'Game over' is on the screen; nothing moves after that until Enter, which starts again with an empty grid, score 0 and state 'playing'."
        ),
        starter=_BLANK,
        solution=_STACKER,
        check=_STACKER_CHECK,
        hint=(
            "function fits(col, row) { for each of the 2x2 cells: outside the walls or the floor, or grid[r][c] already 1 -> return false } "
            "and use it for every move. To clear: if (grid[r].every((v) => v)) { grid.splice(r, 1); grid.unshift(Array(10).fill(0)); }"
        ),
    ),
    Step(
        id="blank-05-yours",
        track="From blank",
        title="Your own game",
        teaches=_OPEN_TEACHES,
        goal="No check here - build whatever you like. Run it, play it, break it, fix it.",
        starter=_BLANK,
        solution=_BLANK,
        check="",
    ),
)
