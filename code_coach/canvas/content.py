"""The Canvas track: one small game, built a step at a time.

The game is Dodge - a square at the bottom, red squares falling, move out
of the way. It is small enough to finish in an evening and has every part
a bigger game has: drawing, a loop, time, input, a list of things, spawning,
collision, score and a restart.

Each step starts from the one before it, finished, and asks for one change.
So `starter` is the previous step's `solution`, and the check for a step
fails on its starter - the suite holds every step to both.

A check is the body of an async function the harness runs after your code
has loaded (see harness.js). It gets `cc` (frames, press, release, rects,
texts), `expect(ok, message)` and `near(a, b, within)`, and reads your
top-level names - player, enemies, state - directly. Checks play the game
rather than read the code, so any way of writing it that works, passes.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Step:
    id: str
    title: str
    #: What the step is about, for someone who has not met it before.
    teaches: str
    #: The one thing to change, said so it can be checked.
    goal: str
    starter: str
    solution: str
    #: Empty for the last step, which is yours to take anywhere.
    check: str
    #: One nudge, shown when asked for.
    hint: str = ""
    track: str = "Dodge"
    #: A game already written, loaded before your code - for tracks where
    #: you program a world rather than build one (Farm). Empty for the rest.
    world: str = ""
    #: For a step on a web page instead of a canvas (the To-do track): the
    #: page's <body>, and the stylesheet it is drawn with. Empty for the rest.
    html: str = ""
    css: str = ""

    @property
    def kind(self) -> str:
        """'dom' for a step on a web page, checked in the browser; else 'canvas'."""
        return "dom" if self.html else "canvas"


_SETUP = """const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');
"""

_S1 = _SETUP + """
ctx.fillStyle = 'tomato';
ctx.fillRect(100, 80, 40, 40);
"""

_S2 = _SETUP + """
ctx.fillStyle = '#10141f';
ctx.fillRect(0, 0, canvas.width, canvas.height);

ctx.fillStyle = 'tomato';
ctx.fillRect(100, 80, 40, 40);
"""

_S3 = _SETUP + """
const player = { x: 100, y: 260, size: 32 };

ctx.fillStyle = '#10141f';
ctx.fillRect(0, 0, canvas.width, canvas.height);

ctx.fillStyle = '#4fd1c5';
ctx.fillRect(player.x, player.y, player.size, player.size);
"""

_S4 = _SETUP + """
const player = { x: 100, y: 260, size: 32 };

function update() {
  player.x += 2;
}

function draw() {
  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = '#4fd1c5';
  ctx.fillRect(player.x, player.y, player.size, player.size);
}

function loop() {
  update();
  draw();
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
"""

_DRAW_PLAYER = """function draw() {
  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = '#4fd1c5';
  ctx.fillRect(player.x, player.y, player.size, player.size);
}
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

_S5 = _SETUP + """
const player = { x: 100, y: 260, size: 32, speed: 240 };

function update(dt) {
  player.x += player.speed * dt;
}

""" + _DRAW_PLAYER + _LOOP

_KEYS = """
const keys = new Set();
addEventListener('keydown', (e) => keys.add(e.key));
addEventListener('keyup', (e) => keys.delete(e.key));
"""

_S6 = _SETUP + """
const player = { x: 100, y: 260, size: 32, speed: 240 };
""" + _KEYS + """
function update(dt) {
  if (keys.has('ArrowLeft')) player.x -= player.speed * dt;
  if (keys.has('ArrowRight')) player.x += player.speed * dt;
}

""" + _DRAW_PLAYER + _LOOP

_S7 = _SETUP + """
const player = { x: 100, y: 260, size: 32, speed: 240 };
""" + _KEYS + """
function update(dt) {
  if (keys.has('ArrowLeft')) player.x -= player.speed * dt;
  if (keys.has('ArrowRight')) player.x += player.speed * dt;
  player.x = Math.max(0, Math.min(canvas.width - player.size, player.x));
}

""" + _DRAW_PLAYER + _LOOP

_DRAW_ENEMIES = """function draw() {
  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = '#4fd1c5';
  ctx.fillRect(player.x, player.y, player.size, player.size);

  ctx.fillStyle = '#f56565';
  for (const e of enemies) ctx.fillRect(e.x, e.y, e.size, e.size);
}
"""

_MOVE_PLAYER = """  if (keys.has('ArrowLeft')) player.x -= player.speed * dt;
  if (keys.has('ArrowRight')) player.x += player.speed * dt;
  player.x = Math.max(0, Math.min(canvas.width - player.size, player.x));
"""

_S8 = _SETUP + """
const player = { x: 100, y: 260, size: 32, speed: 240 };
let enemies = [{ x: 200, y: 0, size: 24, speed: 150 }];
""" + _KEYS + """
function update(dt) {
""" + _MOVE_PLAYER + """
  for (const e of enemies) e.y += e.speed * dt;
}

""" + _DRAW_ENEMIES + _LOOP

_SPAWN = """
  spawnTimer += dt;
  if (spawnTimer >= 1) {
    spawnTimer -= 1;
    enemies.push({ x: Math.random() * (canvas.width - 24), y: -24, size: 24, speed: 150 });
  }
  for (const e of enemies) e.y += e.speed * dt;
  enemies = enemies.filter((e) => e.y < canvas.height);
"""

_S9 = _SETUP + """
const player = { x: 100, y: 260, size: 32, speed: 240 };
let enemies = [];
let spawnTimer = 0;
""" + _KEYS + """
function update(dt) {
""" + _MOVE_PLAYER + _SPAWN + """}

""" + _DRAW_ENEMIES + _LOOP

_OVERLAPS = """
function overlaps(a, b) {
  return a.x < b.x + b.size && b.x < a.x + a.size &&
         a.y < b.y + b.size && b.y < a.y + a.size;
}
"""

_S10 = _SETUP + """
const player = { x: 100, y: 260, size: 32, speed: 240 };
let enemies = [];
let spawnTimer = 0;
let state = 'playing';
""" + _KEYS + _OVERLAPS + """
function update(dt) {
  if (state !== 'playing') return;
""" + _MOVE_PLAYER + _SPAWN + """
  if (enemies.some((e) => overlaps(player, e))) state = 'over';
}

""" + _DRAW_ENEMIES + _LOOP

_S11 = _SETUP + """
const player = { x: 100, y: 260, size: 32, speed: 240 };
let enemies = [];
let spawnTimer = 0;
let state = 'playing';
let score = 0;
""" + _KEYS + _OVERLAPS + """
function update(dt) {
  if (state !== 'playing') return;
""" + _MOVE_PLAYER + _SPAWN + """
  score += dt;
  if (enemies.some((e) => overlaps(player, e))) state = 'over';
}

function draw() {
  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = '#4fd1c5';
  ctx.fillRect(player.x, player.y, player.size, player.size);

  ctx.fillStyle = '#f56565';
  for (const e of enemies) ctx.fillRect(e.x, e.y, e.size, e.size);

  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText(`Score: ${Math.floor(score)}`, 10, 22);
}
""" + _LOOP

_S12 = _SETUP + """
const player = { x: 100, y: 260, size: 32, speed: 240 };
let enemies = [];
let spawnTimer = 0;
let state = 'playing';
let score = 0;

const keys = new Set();
addEventListener('keydown', (e) => {
  keys.add(e.key);
  if (e.key === 'Enter' && state === 'over') restart();
});
addEventListener('keyup', (e) => keys.delete(e.key));

function restart() {
  player.x = 100;
  enemies = [];
  spawnTimer = 0;
  score = 0;
  state = 'playing';
}
""" + _OVERLAPS + """
function update(dt) {
  if (state !== 'playing') return;
""" + _MOVE_PLAYER + _SPAWN + """
  score += dt;
  if (enemies.some((e) => overlaps(player, e))) state = 'over';
}

function draw() {
  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = '#4fd1c5';
  ctx.fillRect(player.x, player.y, player.size, player.size);

  ctx.fillStyle = '#f56565';
  for (const e of enemies) ctx.fillRect(e.x, e.y, e.size, e.size);

  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText(`Score: ${Math.floor(score)}`, 10, 22);

  if (state === 'over') {
    ctx.font = '32px monospace';
    ctx.fillText('Game over', 150, 150);
    ctx.font = '16px monospace';
    ctx.fillText('Press Enter to play again', 130, 180);
  }
}
""" + _LOOP


STEPS: tuple[Step, ...] = (
    Step(
        id="dodge-01-square",
        title="A square on the screen",
        teaches=(
            "A <canvas> is a grid of pixels you paint with JavaScript. You "
            "ask it for a 2d context - ctx - and every drawing call goes "
            "through that. x counts from the left edge and y counts DOWN "
            "from the top, so (0, 0) is the top-left corner, not the "
            "bottom. This canvas is 480 wide and 320 tall. fillStyle sets "
            "the colour for what you draw next, and fillRect(x, y, width, "
            "height) paints a rectangle whose top-left corner is at x, y."
        ),
        goal="Draw a 40 by 40 square with its top-left corner at x 100, y 80, in any colour.",
        starter=_SETUP + "\n// Your square here.\n",
        solution=_S1,
        check="""
const hit = cc.rects().some((r) => r.x === 100 && r.y === 80 && r.w === 40 && r.h === 40);
expect(hit, "There is no 40 by 40 square at x 100, y 80 yet. fillRect takes x, y, width, height - in that order.");
""",
        hint="ctx.fillStyle = 'tomato'; then ctx.fillRect(100, 80, 40, 40);",
    ),
    Step(
        id="dodge-02-background",
        title="Paint the background first",
        teaches=(
            "The canvas is painted in order, like layers of paint: whatever "
            "you draw later covers whatever was there. So a scene is drawn "
            "back to front - background first, then the things on it. "
            "canvas.width and canvas.height are the canvas's size, so "
            "fillRect(0, 0, canvas.width, canvas.height) covers all of it "
            "without you writing 480 and 320 into your code."
        ),
        goal="Fill the whole canvas with a dark colour, then draw the square from step 1 on top of it in a different colour.",
        starter=_S1,
        solution=_S2,
        check="""
const rects = cc.rects();
expect(rects.length >= 2, "Draw two things: the background, then the square.");
const bg = rects[0];
expect(bg.x === 0 && bg.y === 0 && bg.w >= 480 && bg.h >= 320, "The first thing drawn should cover the whole canvas: fillRect(0, 0, canvas.width, canvas.height).");
const sq = rects.slice(1).find((r) => r.x === 100 && r.y === 80 && r.w === 40 && r.h === 40);
expect(sq, "The square at x 100, y 80 has to be drawn after the background, or the background paints over it.");
expect(sq.fill !== bg.fill, "The square is the same colour as the background, so you cannot see it. Set fillStyle again before drawing the square.");
""",
        hint="Two pairs of lines: fillStyle + fillRect for the background, then fillStyle + fillRect for the square.",
    ),
    Step(
        id="dodge-03-player",
        title="The player is an object",
        teaches=(
            "A game keeps what it knows about each thing in an object. The "
            "player's position and size go in one place - player.x, "
            "player.y, player.size - and everything that draws or moves "
            "the player reads from there. Change player.x and the next "
            "drawing is somewhere else; nothing else has to know."
        ),
        goal="Make const player = { x: 100, y: 260, size: 32 } and draw the player as a square using its fields, on the background. The old square can go.",
        starter=_S2,
        solution=_S3,
        check="""
expect(typeof player === "object" && player !== null, "Make an object called player: const player = { x: 100, y: 260, size: 32 };");
expect(player.x === 100 && player.y === 260 && player.size === 32, "player should start with x 100, y 260 and size 32.");
const drawn = cc.rects().some((r) => r.x === player.x && r.y === player.y && r.w === player.size && r.h === player.size);
expect(drawn, "Draw the player from its own fields: ctx.fillRect(player.x, player.y, player.size, player.size).");
""",
        hint="ctx.fillRect(player.x, player.y, player.size, player.size);",
    ),
    Step(
        id="dodge-04-loop",
        title="The game loop",
        teaches=(
            "A game is a picture redrawn about 60 times a second. "
            "requestAnimationFrame(loop) asks the browser to call loop just "
            "before the next frame; loop moves things (update), paints the "
            "whole scene again (draw), and asks for the frame after that. "
            "Forget to ask again and the game runs exactly one frame. "
            "Forget to paint the background each frame and every old "
            "square stays on screen, smeared into a line."
        ),
        goal="Put the drawing in a draw() function, add update() that moves the player 2 pixels right, and a loop() that calls both and asks for the next frame.",
        starter=_S3,
        solution=_S4,
        check="""
const x0 = player.x;
cc.frames(10);
expect(player.x !== x0, "The player has not moved after 10 frames. Change player.x inside a function that requestAnimationFrame calls, and call requestAnimationFrame(loop) once to start it.");
expect(near(player.x - x0, 20, 0.001), `After 10 frames the player moved ${player.x - x0} pixels; it should be 20 - two a frame. Does loop ask for the next frame every time?`);
const rects = cc.rects();
expect(rects.length > 0 && rects[0].x === 0 && rects[0].y === 0 && rects[0].w >= 480 && rects[0].h >= 320, "Each frame should start by painting the background again, or the old squares stay on screen as a smear.");
expect(rects.some((r) => r.x === player.x && r.y === player.y), "Each frame should draw the player where it is now.");
""",
        hint="function loop() { update(); draw(); requestAnimationFrame(loop); } and one requestAnimationFrame(loop); at the bottom to start it.",
    ),
    Step(
        id="dodge-05-delta-time",
        title="Speed in pixels a second",
        teaches=(
            "Moving 2 pixels a frame means the game runs twice as fast on a "
            "120 Hz screen as on a 60 Hz one. The fix is delta time. "
            "requestAnimationFrame passes loop a timestamp in milliseconds; "
            "the difference from the last one, divided by 1000, is dt - "
            "the seconds since the last frame (about 0.0167 at 60 frames a "
            "second). Move by speed * dt and speed means pixels a second, "
            "whatever the frame rate."
        ),
        goal="Give player a speed of 240. loop(time) works out dt in seconds and passes it to update(dt), which moves the player right by player.speed * dt.",
        starter=_S4,
        solution=_S5,
        check="""
expect(player.speed === 240, "Give player a speed of 240 - pixels a second: { x: 100, y: 260, size: 32, speed: 240 }.");
let x0 = player.x;
cc.frames(30, 1000 / 30);
const slow = player.x - x0;
x0 = player.x;
cc.frames(60, 1000 / 60);
const fast = player.x - x0;
expect(near(fast, 240, 5), `In one second at 60 frames a second the player moved ${Math.round(fast)} pixels; at speed 240 it should move 240. Move by player.speed * dt, with dt in seconds.`);
expect(near(slow, 240, 9), `In one second at 30 frames a second the player moved ${Math.round(slow)} pixels, and at 60 it moved ${Math.round(fast)}. With delta time both are 240: the frame rate stops mattering.`);
""",
        hint="let last = 0; then in loop(time): const dt = (time - last) / 1000; last = time; update(dt);",
    ),
    Step(
        id="dodge-06-keys",
        title="Arrow keys",
        teaches=(
            "Key events arrive once, when a key goes down and when it comes "
            "up - but a game wants to know, every frame, what is held right "
            "now. So keep a Set of held keys: add e.key on keydown, delete "
            "it on keyup, and in update ask keys.has('ArrowLeft'). Click "
            "the game before pressing keys, so it has the keyboard."
        ),
        goal="Stop the automatic movement. Keep a Set of held keys, and in update move the player left while ArrowLeft is held and right while ArrowRight is held, at player.speed.",
        starter=_S5,
        solution=_S6,
        check="""
const x0 = player.x;
cc.frames(30);
expect(near(player.x, x0, 0.01), "The player moves on its own. It should stand still until an arrow key is held.");
cc.press("ArrowRight");
cc.frames(30);
cc.release("ArrowRight");
const right = player.x - x0;
expect(near(right, 120, 6), `Holding ArrowRight for half a second moved the player ${Math.round(right)} pixels; it should be about 120 (240 a second). Keep a Set of held keys: add on keydown, delete on keyup, and check it in update.`);
const x1 = player.x;
cc.frames(30);
expect(near(player.x, x1, 0.01), "The player kept going after ArrowRight was let go. Delete the key from the set on keyup.");
cc.press("ArrowLeft");
cc.frames(30);
cc.release("ArrowLeft");
expect(near(x1 - player.x, 120, 6), "ArrowLeft should move the player left at the same speed.");
""",
        hint="const keys = new Set(); addEventListener('keydown', (e) => keys.add(e.key)); and the same with keyup and delete.",
    ),
    Step(
        id="dodge-07-clamp",
        title="Stay on the screen",
        teaches=(
            "Nothing stops player.x going to -500 or 5000; the canvas just "
            "stops showing it. Clamping keeps a number inside a range: "
            "Math.max(low, Math.min(high, x)) is x, unless x is below low "
            "(then low) or above high (then high). The player's x is its "
            "left edge, so the right-most it can go is canvas.width - "
            "player.size."
        ),
        goal="After moving, clamp player.x so the player never leaves the canvas on either side.",
        starter=_S6,
        solution=_S7,
        check="""
cc.press("ArrowRight");
cc.frames(180);
cc.release("ArrowRight");
expect(near(player.x, canvas.width - player.size, 0.01), `After three seconds of ArrowRight the player is at x ${Math.round(player.x)}. It should stop with its right edge on the canvas edge: x = canvas.width - player.size.`);
cc.press("ArrowLeft");
cc.frames(180);
cc.release("ArrowLeft");
expect(near(player.x, 0, 0.01), `After three seconds of ArrowLeft the player is at x ${Math.round(player.x)}. It should stop at 0.`);
""",
        hint="player.x = Math.max(0, Math.min(canvas.width - player.size, player.x));",
    ),
    Step(
        id="dodge-08-enemy",
        title="Something falls",
        teaches=(
            "One enemy could be one more object, but a game has many, so "
            "they go in an array from the start. Every frame, update moves "
            "each one and draw paints each one - a for...of loop in both. "
            "Enemies fall, so it is their y that grows."
        ),
        goal="Add let enemies = [{ x: 200, y: 0, size: 24, speed: 150 }]. Each frame, move every enemy down by its speed * dt and draw it in its own colour.",
        starter=_S7,
        solution=_S8,
        check="""
expect(typeof enemies !== "undefined" && Array.isArray(enemies) && enemies.length >= 1, "Make an array called enemies with one enemy in it: { x: 200, y: 0, size: 24, speed: 150 }.");
const e = enemies[0];
const y0 = e.y;
cc.frames(60);
expect(near(e.y - y0, 150, 5), `In one second the enemy fell ${Math.round(e.y - y0)} pixels; at speed 150 it should fall 150. Move every enemy down by e.speed * dt.`);
expect(cc.rects().some((r) => near(r.x, e.x, 0.01) && near(r.y, e.y, 0.01) && r.w === e.size), "Draw every enemy each frame, after the background.");
""",
        hint="In update: for (const e of enemies) e.y += e.speed * dt;  In draw: for (const e of enemies) ctx.fillRect(e.x, e.y, e.size, e.size);",
    ),
    Step(
        id="dodge-09-spawn",
        title="Spawn on a timer",
        teaches=(
            "A timer in a game is a number you add dt to. When it passes "
            "the interval, something happens and you take the interval "
            "off (rather than setting it to 0, which throws away the few "
            "milliseconds over and makes the rhythm drift). Things that "
            "have left the screen should leave the array too, or it grows "
            "forever: enemies = enemies.filter(...) keeps only the ones "
            "still on screen. That is why enemies is let, not const."
        ),
        goal="Start with no enemies. Every second, push a new one at a random x across the canvas, just above the top (y -24). Remove enemies once they fall past the bottom.",
        starter=_S8,
        solution=_S9,
        check="""
const seen = new Set(enemies);
for (let i = 0; i < 10 * 60; i++) {
  cc.frames(1);
  for (const e of enemies) seen.add(e);
}
expect(seen.size >= 9 && seen.size <= 12, `In ten seconds ${seen.size} enemies appeared (counting any you started with); one a second makes about ten. Add dt to a timer, and when it reaches 1, take 1 off and push a new enemy.`);
for (const e of seen) {
  expect(e.x >= 0 && e.x + e.size <= canvas.width, "Every enemy should start fully across the canvas: x from 0 to canvas.width - size. Math.random() * (canvas.width - 24) does it.");
}
expect(enemies.length <= 4, `There are ${enemies.length} enemies in the list, some long gone past the bottom. Remove them: enemies = enemies.filter((e) => e.y < canvas.height);`);
""",
        hint="let spawnTimer = 0; then in update: spawnTimer += dt; if (spawnTimer >= 1) { spawnTimer -= 1; enemies.push({ ... }); }",
    ),
    Step(
        id="dodge-10-collision",
        title="Hit!",
        teaches=(
            "Two boxes overlap when they overlap on x AND on y. On x: a's "
            "left edge is left of b's right edge (a.x < b.x + b.size) and "
            "b's left edge is left of a's right edge (b.x < a.x + a.size). "
            "The same for y. Use < rather than <=, so boxes that only touch "
            "edges do not count. A state variable says what the game is "
            "doing - 'playing' or 'over' - and update does nothing once it "
            "is over."
        ),
        goal="Add let state = 'playing' and a function overlaps(a, b). When any enemy overlaps the player, set state to 'over'; once it is over, update stops moving anything.",
        starter=_S9,
        solution=_S10,
        check="""
expect(typeof state !== "undefined" && state === "playing", "Keep what the game is doing in a variable: let state = 'playing';");
enemies.length = 0;
enemies.push({ x: player.x + 200, y: player.y, size: 24, speed: 0 });
enemies.push({ x: player.x + player.size, y: player.y, size: 24, speed: 0 });
cc.frames(2);
expect(state === "playing", "The game ended with no enemy overlapping the player - one only touches its right edge. Use < in overlaps, and check x and y both.");
enemies.length = 0;
enemies.push({ x: player.x + 8, y: player.y - 8, size: 24, speed: 0 });
cc.frames(2);
expect(state === "over", "An enemy is sitting on the player and the game carried on. When any enemy overlaps the player, set state = 'over'.");
const x = player.x;
cc.press("ArrowRight");
cc.frames(30);
cc.release("ArrowRight");
expect(near(player.x, x, 0.01), "The player still moves after the game is over. Start update with: if (state !== 'playing') return;");
""",
        hint="if (enemies.some((e) => overlaps(player, e))) state = 'over';",
    ),
    Step(
        id="dodge-11-score",
        title="Score",
        teaches=(
            "In Dodge you score by surviving, so the score is time: add dt "
            "while playing. fillText(text, x, y) writes on the canvas in "
            "the current fillStyle and font; y is the text's baseline, so "
            "text at y 0 is off the top. Show Math.floor(score) - whole "
            "seconds - not 3.1666666."
        ),
        goal="Add let score = 0, add dt to it each frame while playing, and write it in the top-left corner each frame with fillText.",
        starter=_S10,
        solution=_S11,
        check="""
expect(typeof score === "number", "Keep the score in a variable: let score = 0;");
enemies.length = 0;
const s0 = score;
cc.frames(60);
expect(near(score - s0, 1, 0.05), `One second of play added ${(score - s0).toFixed(2)} to the score; it should add 1. Add dt to it in update.`);
cc.frames(60);
expect(cc.texts().some((t) => t.includes(String(Math.floor(score)))), `Write the score on the screen every frame with fillText - it should show ${Math.floor(score)} now.`);
""",
        hint="ctx.fillStyle = 'white'; ctx.font = '16px monospace'; ctx.fillText(`Score: ${Math.floor(score)}`, 10, 22);",
    ),
    Step(
        id="dodge-12-restart",
        title="Game over, and again",
        teaches=(
            "A finished game says it is over and lets you go again. The "
            "restart puts back everything that changed during play - "
            "position, enemies, timers, score, state - which is exactly "
            "the list of your let variables and the player's fields. "
            "Keys that do something once (Enter to restart) belong in the "
            "keydown handler, not in the held-keys set."
        ),
        goal="When the game is over, write 'Game over' on the screen. Pressing Enter then starts a new game: player back to x 100, no enemies, score 0, state 'playing'.",
        starter=_S11,
        solution=_S12,
        check="""
enemies.length = 0;
cc.frames(30);
enemies.push({ x: player.x, y: player.y, size: 24, speed: 0 });
cc.frames(2);
expect(state === "over", "Put an enemy on the player and the game should end - that part is from step 10.");
expect(cc.texts().some((t) => /game over/i.test(t)), "When the game is over, write 'Game over' on the screen.");
cc.press("Enter");
cc.frames(2);
cc.release("Enter");
expect(state === "playing", "Pressing Enter after a game over should start a new game: state back to 'playing'. Clear the enemies too, or the one on the player ends it again at once.");
expect(score < 0.1, "A new game starts with the score back at 0.");
expect(enemies.length <= 1, "A new game starts with no enemies - empty the list.");
expect(!cc.texts().some((t) => /game over/i.test(t)), "'Game over' is still on the screen after the restart.");
""",
        hint="In keydown: if (e.key === 'Enter' && state === 'over') restart();  and restart() sets everything back.",
    ),
    Step(
        id="dodge-13-yours",
        title="Now it's yours",
        teaches=(
            "That is a whole game: loop, time, input, a list of things, "
            "spawning, collision, score and restart. Every bigger game is "
            "more of the same parts. Some things to try, roughly easiest "
            "first: make enemies fall faster as the score goes up; give "
            "enemies different sizes and speeds; three lives instead of "
            "one; a high score kept in a variable across restarts; a pause "
            "on P (another state); dodging on both axes with ArrowUp and "
            "ArrowDown; coins to collect that add to the score."
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_S12,
        solution=_S12,
        check="",
    ),
)
