"""The second Canvas track: Breakout.

Dodge taught the loop, time, keys, lists and boxes. Breakout keeps all of
that and adds what it did not need: circles, a velocity with two parts,
bouncing, collision between a circle and a box, lives, a grid built with
two loops, the mouse (and the page-pixels-are-not-canvas-pixels trap),
winning, and steering the ball with where it lands on the paddle.

Same rules as Dodge: each step's starter is the step before, finished; a
check plays the program and never reads it.
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

_KEYS = """
const keys = new Set();
addEventListener('keydown', (e) => keys.add(e.key));
addEventListener('keyup', (e) => keys.delete(e.key));
"""

_BG = """  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
"""

_DRAW_BALL = """
  ctx.fillStyle = 'white';
  ctx.beginPath();
  ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);
  ctx.fill();
"""

_MOVE_BALL = """  ball.x += ball.vx * dt;
  ball.y += ball.vy * dt;
"""

_SIDE_WALLS = """
  if (ball.x - ball.r < 0) {
    ball.x = ball.r;
    ball.vx = Math.abs(ball.vx);
  }
  if (ball.x + ball.r > canvas.width) {
    ball.x = canvas.width - ball.r;
    ball.vx = -Math.abs(ball.vx);
  }
  if (ball.y - ball.r < 0) {
    ball.y = ball.r;
    ball.vy = Math.abs(ball.vy);
  }
"""

_FLOOR = """  if (ball.y + ball.r > canvas.height) {
    ball.y = canvas.height - ball.r;
    ball.vy = -Math.abs(ball.vy);
  }
"""

_MOVE_PADDLE = """
  if (keys.has('ArrowLeft')) paddle.x -= paddle.speed * dt;
  if (keys.has('ArrowRight')) paddle.x += paddle.speed * dt;
  paddle.x = Math.max(0, Math.min(canvas.width - paddle.w, paddle.x));
"""

_DRAW_PADDLE = """
  ctx.fillStyle = '#4fd1c5';
  ctx.fillRect(paddle.x, paddle.y, paddle.w, paddle.h);
"""

_HITS_RECT = """
function hitsRect(b, r) {
  const cx = Math.max(r.x, Math.min(b.x, r.x + r.w));
  const cy = Math.max(r.y, Math.min(b.y, r.y + r.h));
  return (b.x - cx) ** 2 + (b.y - cy) ** 2 < b.r ** 2;
}
"""

_PADDLE_BOUNCE = """
  if (ball.vy > 0 && hitsRect(ball, paddle)) {
    ball.y = paddle.y - ball.r;
    ball.vy = -Math.abs(ball.vy);
  }
"""

_PADDLE_AIM = """
  if (ball.vy > 0 && hitsRect(ball, paddle)) {
    const speed = Math.hypot(ball.vx, ball.vy);
    const offset = (ball.x - (paddle.x + paddle.w / 2)) / (paddle.w / 2);
    const angle = Math.max(-1, Math.min(1, offset)) * (Math.PI / 3);
    ball.vx = speed * Math.sin(angle);
    ball.vy = -speed * Math.cos(angle);
    ball.y = paddle.y - ball.r;
  }
"""

_LOSE_BALL = """
  if (ball.y - ball.r > canvas.height) {
    lives -= 1;
    if (lives === 0) state = 'over';
    else serve();
  }
"""

_SERVE = """
function serve() {
  ball.x = 240;
  ball.y = 200;
  ball.vx = 180;
  ball.vy = -180;
}
"""

_BRICKS = """
const bricks = [];
for (let row = 0; row < 5; row++) {
  for (let col = 0; col < 8; col++) {
    bricks.push({ x: 16 + col * 56, y: 30 + row * 22, w: 50, h: 16, alive: true });
  }
}
"""

_DRAW_BRICKS = """
  ctx.fillStyle = '#f6ad55';
  for (const b of bricks) {
    if (b.alive) ctx.fillRect(b.x, b.y, b.w, b.h);
  }
"""

_BREAK = """
  for (const b of bricks) {
    if (b.alive && hitsRect(ball, b)) {
      b.alive = false;
      ball.vy = -ball.vy;
      score += 10;
      break;
    }
  }
"""

_MOUSE = """
canvas.addEventListener('mousemove', (e) => {
  const box = canvas.getBoundingClientRect();
  const mouseX = (e.clientX - box.left) * (canvas.width / box.width);
  paddle.x = Math.max(0, Math.min(canvas.width - paddle.w, mouseX - paddle.w / 2));
});
"""

_TEXT_LIVES = """
  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText(`Lives: ${lives}`, 390, 20);
  if (state === 'over') {
    ctx.font = '32px monospace';
    ctx.fillText('Game over', 150, 200);
  }
"""

_TEXT_SCORE = """
  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText(`Score: ${score}`, 10, 20);
  ctx.fillText(`Lives: ${lives}`, 390, 20);
  if (state === 'over') {
    ctx.font = '32px monospace';
    ctx.fillText('Game over', 150, 200);
  }
"""

_TEXT_WIN = _TEXT_SCORE + """  if (state === 'won') {
    ctx.font = '32px monospace';
    ctx.fillText('You win!', 170, 200);
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


_B0 = _program("", "", "")

_BALL = "const ball = { x: 240, y: 160, r: 8 };\n"
_BALL_V = "const ball = { x: 240, y: 160, r: 8, vx: 180, vy: -180 };\n"
_PADDLE = "const paddle = { x: 200, y: 296, w: 80, h: 10, speed: 360 };\n"
_PLAY_STATE = "let lives = 3;\nlet state = 'playing';\n"

_B1 = _program(_BALL, "", _DRAW_BALL)
_B2 = _program(_BALL_V, _MOVE_BALL, _DRAW_BALL)
_B3 = _program(_BALL_V, _MOVE_BALL + _SIDE_WALLS + _FLOOR, _DRAW_BALL)
_B4 = _program(
    _BALL_V + _PADDLE, _MOVE_PADDLE + _MOVE_BALL + _SIDE_WALLS + _FLOOR,
    _DRAW_BALL + _DRAW_PADDLE, _KEYS,
)
_B5 = _program(
    _BALL_V + _PADDLE, _MOVE_PADDLE + _MOVE_BALL + _SIDE_WALLS + _PADDLE_BOUNCE,
    _DRAW_BALL + _DRAW_PADDLE, _KEYS + _HITS_RECT,
)
_B6 = _program(
    _BALL_V + _PADDLE + _PLAY_STATE,
    "  if (state !== 'playing') return;\n" + _MOVE_PADDLE + _MOVE_BALL
    + _SIDE_WALLS + _PADDLE_BOUNCE + _LOSE_BALL,
    _DRAW_BALL + _DRAW_PADDLE + _TEXT_LIVES, _KEYS + _HITS_RECT + _SERVE,
)
_B7 = _program(
    _BALL_V + _PADDLE + _PLAY_STATE,
    "  if (state !== 'playing') return;\n" + _MOVE_PADDLE + _MOVE_BALL
    + _SIDE_WALLS + _PADDLE_BOUNCE + _LOSE_BALL,
    _DRAW_BRICKS + _DRAW_BALL + _DRAW_PADDLE + _TEXT_LIVES,
    _BRICKS + _KEYS + _HITS_RECT + _SERVE,
)
_B8 = _program(
    _BALL_V + _PADDLE + _PLAY_STATE + "let score = 0;\n",
    "  if (state !== 'playing') return;\n" + _MOVE_PADDLE + _MOVE_BALL
    + _SIDE_WALLS + _PADDLE_BOUNCE + _BREAK + _LOSE_BALL,
    _DRAW_BRICKS + _DRAW_BALL + _DRAW_PADDLE + _TEXT_SCORE,
    _BRICKS + _KEYS + _HITS_RECT + _SERVE,
)
_B9 = _program(
    _BALL_V + _PADDLE + _PLAY_STATE + "let score = 0;\n",
    "  if (state !== 'playing') return;\n" + _MOVE_PADDLE + _MOVE_BALL
    + _SIDE_WALLS + _PADDLE_BOUNCE + _BREAK + _LOSE_BALL,
    _DRAW_BRICKS + _DRAW_BALL + _DRAW_PADDLE + _TEXT_SCORE,
    _BRICKS + _KEYS + _MOUSE + _HITS_RECT + _SERVE,
)
_WIN = "  if (bricks.every((b) => !b.alive)) state = 'won';\n"
_B10 = _program(
    _BALL_V + _PADDLE + _PLAY_STATE + "let score = 0;\n",
    "  if (state !== 'playing') return;\n" + _MOVE_PADDLE + _MOVE_BALL
    + _SIDE_WALLS + _PADDLE_BOUNCE + _BREAK + _WIN + _LOSE_BALL,
    _DRAW_BRICKS + _DRAW_BALL + _DRAW_PADDLE + _TEXT_WIN,
    _BRICKS + _KEYS + _MOUSE + _HITS_RECT + _SERVE,
)
_B11 = _program(
    _BALL_V + _PADDLE + _PLAY_STATE + "let score = 0;\n",
    "  if (state !== 'playing') return;\n" + _MOVE_PADDLE + _MOVE_BALL
    + _SIDE_WALLS + _PADDLE_AIM + _BREAK + _WIN + _LOSE_BALL,
    _DRAW_BRICKS + _DRAW_BALL + _DRAW_PADDLE + _TEXT_WIN,
    _BRICKS + _KEYS + _MOUSE + _HITS_RECT + _SERVE,
)


BREAKOUT_STEPS: tuple[Step, ...] = (
    Step(
        id="breakout-01-ball",
        track="Breakout",
        title="A ball is a circle",
        teaches=(
            "There is no fillCircle. A circle is a path: beginPath() starts "
            "a new one, arc(x, y, radius, startAngle, endAngle) traces round "
            "a centre, and fill() paints what was traced. Angles are in "
            "radians, and a full turn is Math.PI * 2. Unlike a rectangle, a "
            "circle is placed by its centre, not its corner. Leave out "
            "beginPath and the next fill repaints every arc since the last "
            "one - the classic smeared trail."
        ),
        goal="Make const ball = { x: 240, y: 160, r: 8 } and draw it each frame as a filled circle, after the background.",
        starter=_B0,
        solution=_B1,
        check="""
expect(typeof ball === "object" && ball !== null, "Make an object called ball: const ball = { x: 240, y: 160, r: 8 };");
cc.frames(1);
const arc = cc.arcs().find((a) => near(a.x, ball.x, 0.01) && near(a.y, ball.y, 0.01) && a.r === ball.r);
expect(arc, "Draw the ball each frame: ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2) inside draw().");
const names = cc.drawn().map((c) => c.name);
const at = names.lastIndexOf("arc");
expect(names.lastIndexOf("beginPath", at) !== -1, "Call ctx.beginPath() before the arc, so each frame's circle is a new path.");
expect(names.indexOf("fill", at) > at, "An arc on its own is only an outline in waiting - call ctx.fill() after it.");
""",
        hint="ctx.fillStyle = 'white'; ctx.beginPath(); ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2); ctx.fill();",
    ),
    Step(
        id="breakout-02-velocity",
        track="Breakout",
        title="A velocity has two parts",
        teaches=(
            "In Dodge things moved along one line. A ball moves on both at "
            "once, so its velocity is two numbers: vx, pixels a second to "
            "the right, and vy, pixels a second DOWN (y grows downwards, so "
            "a negative vy goes up). Each frame, x moves by vx * dt and y "
            "by vy * dt. Equal parts make a 45 degree diagonal."
        ),
        goal="Give the ball vx: 180 and vy: -180, and move it by its velocity times dt every frame - up and to the right.",
        starter=_B1,
        solution=_B2,
        check="""
expect(ball.vx === 180 && ball.vy === -180, "Give the ball vx: 180 and vy: -180.");
const x0 = ball.x;
const y0 = ball.y;
cc.frames(30);
expect(near(ball.x - x0, 90, 4), `In half a second the ball moved ${Math.round(ball.x - x0)} pixels across; at vx 180 it should move 90. Use ball.vx * dt.`);
expect(near(ball.y - y0, -90, 4), `In half a second the ball moved ${Math.round(ball.y - y0)} pixels down; at vy -180 it should move 90 UP, so y goes down by 90.`);
""",
        hint="In update: ball.x += ball.vx * dt; ball.y += ball.vy * dt;",
    ),
    Step(
        id="breakout-03-walls",
        track="Breakout",
        title="Bounce off the walls",
        teaches=(
            "A bounce off a side wall flips vx; off the top or bottom, vy. "
            "But flipping alone is not enough: by the time you notice, the "
            "ball is already a little way into the wall, and if it is still "
            "in there next frame it flips again and sticks, shivering. So "
            "put it back on the edge as well, and set the direction rather "
            "than flip it: vx = -Math.abs(vx) off the right wall always "
            "means 'going left', however many frames it takes to get out."
        ),
        goal="Keep the ball inside all four edges: when its edge crosses a wall, put it back on the wall and send it the other way.",
        starter=_B2,
        solution=_B3,
        check="""
for (let i = 1; i <= 600; i++) {
  cc.frames(1);
  const inside = ball.x - ball.r >= -0.01 && ball.x + ball.r <= canvas.width + 0.01
    && ball.y - ball.r >= -0.01 && ball.y + ball.r <= canvas.height + 0.01;
  expect(inside, `After ${i} frames the ball is at x ${Math.round(ball.x)}, y ${Math.round(ball.y)} - partly through a wall. When it crosses an edge, put it back on the edge as well as turning it round.`);
}
expect(Math.abs(ball.vx) === 180 && Math.abs(ball.vy) === 180, "A bounce should change the ball's direction, not its speed.");
""",
        hint="if (ball.x + ball.r > canvas.width) { ball.x = canvas.width - ball.r; ball.vx = -Math.abs(ball.vx); } and the same idea for the other three.",
    ),
    Step(
        id="breakout-04-paddle",
        track="Breakout",
        title="A paddle",
        teaches=(
            "The paddle is Dodge's player turned on its side: a box, a Set "
            "of held keys, speed times dt, and a clamp so it stays on the "
            "screen. A box is placed by its top-left corner, so its right "
            "edge is x + w, and the right-most it can go is canvas.width - "
            "w. Nothing new to learn here - that is the point. The parts "
            "you have already built come with you."
        ),
        goal="Add const paddle = { x: 200, y: 296, w: 80, h: 10, speed: 360 }, move it with the arrow keys, keep it on the canvas, and draw it.",
        starter=_B3,
        solution=_B4,
        check="""
expect(typeof paddle === "object" && paddle !== null && paddle.w === 80 && paddle.speed === 360, "Make const paddle = { x: 200, y: 296, w: 80, h: 10, speed: 360 };");
const x0 = paddle.x;
cc.press("ArrowRight");
cc.frames(30);
cc.release("ArrowRight");
expect(near(paddle.x - x0, 180, 8), `Half a second of ArrowRight moved the paddle ${Math.round(paddle.x - x0)} pixels; at speed 360 it should be about 180.`);
cc.press("ArrowRight");
cc.frames(120);
cc.release("ArrowRight");
expect(near(paddle.x, canvas.width - paddle.w, 0.01), "The paddle should stop with its right edge on the canvas edge.");
cc.press("ArrowLeft");
cc.frames(120);
cc.release("ArrowLeft");
expect(near(paddle.x, 0, 0.01), "The paddle should stop at the left edge too.");
expect(cc.rects().some((r) => near(r.x, paddle.x, 0.01) && r.y === paddle.y && r.w === paddle.w && r.h === paddle.h), "Draw the paddle every frame.");
""",
        hint="The same three lines as Dodge's player: two if (keys.has(...)) and one Math.max(0, Math.min(...)).",
    ),
    Step(
        id="breakout-05-paddle-bounce",
        track="Breakout",
        title="A circle meets a box",
        teaches=(
            "Box against box was two overlaps. Circle against box is: find "
            "the point of the box nearest the circle's centre - clamp the "
            "centre's x into the box's left and right, and its y into its "
            "top and bottom - and the circle touches the box if that point "
            "is closer than the radius. Treating the ball as a box instead "
            "makes it bounce off thin air near the corners. Only bounce "
            "when the ball is coming down (vy > 0), or it can catch on the "
            "paddle and rattle. The floor stops bouncing now: miss, and the "
            "ball is gone."
        ),
        goal="Write hitsRect(ball, box) the circle way. When the ball is moving down and hits the paddle, send it up and sit it on top of the paddle. Take the floor bounce out.",
        starter=_B4,
        solution=_B5,
        check="""
ball.x = paddle.x + paddle.w / 2;
ball.y = paddle.y - 30;
ball.vx = 0;
ball.vy = 180;
cc.frames(12);
expect(ball.vy < 0, "The ball fell onto the middle of the paddle and did not bounce. When it is moving down (vy > 0) and hits the paddle, make vy negative.");
expect(ball.y + ball.r <= paddle.y + 0.01, "After the bounce the ball should sit on top of the paddle, not inside it: ball.y = paddle.y - ball.r.");
ball.x = paddle.x - 7;
ball.y = paddle.y - 7;
ball.vx = 0;
ball.vy = 30;
cc.frames(1);
expect(ball.vy > 0, "The ball bounced off empty space just past the paddle's corner. That is the box test; a circle only touches when the nearest point of the box is closer than the radius.");
paddle.x = 0;
ball.x = 400;
ball.y = 250;
ball.vx = 0;
ball.vy = 180;
cc.frames(60);
expect(ball.y > canvas.height, "The ball missed the paddle and bounced off the floor. Take the floor bounce out - a miss is a miss.");
""",
        hint="const cx = Math.max(r.x, Math.min(b.x, r.x + r.w)); the same for cy; then compare (b.x - cx) ** 2 + (b.y - cy) ** 2 with b.r ** 2.",
    ),
    Step(
        id="breakout-06-lives",
        track="Breakout",
        title="Three lives",
        teaches=(
            "A ball below the bottom edge is a lost life. Take one off, "
            "and if there are any left, serve a new ball from the middle, "
            "going up; if not, the game is over. serve() is a function of "
            "its own because the start of the game will want it too. Only "
            "count the loss once the whole ball is gone (its top below the "
            "bottom), and draw the lives so the player knows."
        ),
        goal="Add let lives = 3 and let state = 'playing'. A ball fully below the bottom costs a life and serves a new one from x 240, y 200, going up; at 0 lives, state is 'over' and 'Game over' is on the screen. Show the lives.",
        starter=_B5,
        solution=_B6,
        check="""
expect(typeof lives === "number" && lives === 3, "Start with let lives = 3;");
expect(typeof state === "string" && state === "playing", "Keep what the game is doing in let state = 'playing';");
const drop = () => {
  paddle.x = 0;
  ball.x = 400;
  ball.y = 280;
  ball.vx = 0;
  ball.vy = 300;
  cc.frames(30);
};
drop();
expect(lives === 2, `Losing a ball should cost one life; lives is ${lives}.`);
expect(ball.y < canvas.height && ball.vy < 0, "After a lost ball, serve a new one: back in the middle, going up.");
expect(cc.texts().some((t) => t.includes("2")), "Show the lives on the screen - it should say 2 now.");
drop();
drop();
expect(lives === 0 && state === "over", `Three lost balls should end the game: lives is ${lives}, state is '${state}'.`);
expect(cc.texts().some((t) => /game over/i.test(t)), "When the game is over, say so on the screen.");
""",
        hint="if (ball.y - ball.r > canvas.height) { lives -= 1; if (lives === 0) state = 'over'; else serve(); }",
    ),
    Step(
        id="breakout-07-bricks",
        track="Breakout",
        title="A wall of bricks",
        teaches=(
            "Forty bricks are not typed out; they are made by two loops, "
            "one inside the other. The outer loop counts rows, the inner "
            "one columns, and each brick's position is worked out from its "
            "row and column: x = left + col * (width + gap). Give each one "
            "alive: true now - breaking a brick will just flip it, and draw "
            "will skip the dead ones."
        ),
        goal="Build const bricks with 5 rows of 8: each { x: 16 + col * 56, y: 30 + row * 22, w: 50, h: 16, alive: true }. Draw every alive brick.",
        starter=_B6,
        solution=_B7,
        check="""
expect(typeof bricks !== "undefined" && Array.isArray(bricks), "Make an array called bricks.");
expect(bricks.length === 40, `There are ${bricks.length} bricks; 5 rows of 8 is 40. One loop for rows, one inside it for columns.`);
const places = new Set(bricks.map((b) => b.x + "," + b.y));
expect(places.size === 40, "Some bricks are on top of each other - x should come from the column and y from the row.");
expect(new Set(bricks.map((b) => b.y)).size === 5 && new Set(bricks.map((b) => b.x)).size === 8, "The bricks should make a grid: 5 different heights, 8 different lefts.");
for (const b of bricks) {
  expect(b.x >= 0 && b.x + b.w <= canvas.width && b.alive === true, "Every brick should start alive and fully on the canvas.");
}
cc.frames(1);
const drawn = cc.rects();
expect(bricks.every((b) => drawn.some((r) => r.x === b.x && r.y === b.y && r.w === b.w && r.h === b.h)), "Draw every alive brick each frame.");
""",
        hint="for (let row = 0; row < 5; row++) { for (let col = 0; col < 8; col++) { bricks.push({ ... }); } }",
    ),
    Step(
        id="breakout-08-break",
        track="Breakout",
        title="Breaking bricks",
        teaches=(
            "Each frame, check the ball against every alive brick with the "
            "same hitsRect as the paddle. On a hit: the brick dies, the "
            "ball turns round (flip vy), the score goes up - and the loop "
            "stops with break. Without the break, a ball touching two "
            "bricks at once flips twice and carries straight on through."
        ),
        goal="Add let score = 0. When the ball hits an alive brick, set its alive to false, flip ball.vy, add 10 to the score and stop checking for this frame. Show the score.",
        starter=_B7,
        solution=_B8,
        check="""
expect(typeof score === "number" && score === 0, "Start with let score = 0;");
const target = bricks[bricks.length - 1];
ball.x = target.x + target.w / 2;
ball.y = target.y + target.h + 20;
ball.vx = 0;
ball.vy = -180;
cc.frames(15);
expect(target.alive === false, "The ball flew into the bottom-right brick and the brick is still there. On a hit, set the brick's alive to false.");
expect(bricks.filter((b) => b.alive).length === 39, "Exactly one brick should break.");
expect(ball.vy > 0, "After breaking a brick the ball should bounce back down.");
expect(score === 10, `A brick is worth 10; the score is ${score}.`);
expect(cc.texts().some((t) => t.includes("10")), "Show the score on the screen.");
""",
        hint="for (const b of bricks) { if (b.alive && hitsRect(ball, b)) { b.alive = false; ball.vy = -ball.vy; score += 10; break; } }",
    ),
    Step(
        id="breakout-09-mouse",
        track="Breakout",
        title="Steer with the mouse",
        teaches=(
            "A mouse event tells you where the pointer is in PAGE pixels: "
            "e.clientX counts from the window's left edge. The canvas "
            "starts somewhere on the page, and is often drawn bigger or "
            "smaller than its 480 pixels. So: take off where the canvas "
            "starts (getBoundingClientRect().left), then scale by "
            "canvas.width / rect.width. Skip either step and the paddle "
            "drifts away from the pointer as soon as the page is resized. "
            "Keep the arrow keys too."
        ),
        goal="On mousemove over the canvas, put the paddle's centre under the pointer, in canvas pixels, clamped to the canvas.",
        starter=_B8,
        solution=_B9,
        check="""
cc.pointer(300, 200);
cc.frames(1);
const centre = paddle.x + paddle.w / 2;
expect(near(centre, 300, 1), `The pointer is over x 300 of the canvas, but the paddle's centre is at ${Math.round(centre)}. The event is in page pixels: subtract rect.left, then multiply by canvas.width / rect.width.`);
cc.pointer(5, 200);
cc.frames(1);
expect(near(paddle.x, 0, 0.01), "With the pointer near the left edge, the paddle should stop at 0, not hang off the canvas.");
cc.pointer(478, 200);
cc.frames(1);
expect(near(paddle.x, canvas.width - paddle.w, 0.01), "With the pointer near the right edge, the paddle should stop at the canvas edge.");
""",
        hint="const box = canvas.getBoundingClientRect(); const mouseX = (e.clientX - box.left) * (canvas.width / box.width);",
    ),
    Step(
        id="breakout-10-win",
        track="Breakout",
        title="Winning",
        teaches=(
            "Losing was already there; winning is the other way out. The "
            "game is won when no brick is alive - bricks.every((b) => "
            "!b.alive) asks exactly that. Set the state, and update stops "
            "just as it does after losing."
        ),
        goal="When every brick is broken, set state to 'won' and put 'You win!' on the screen.",
        starter=_B9,
        solution=_B10,
        check="""
for (const b of bricks.slice(0, -1)) b.alive = false;
cc.frames(1);
expect(state === "playing", "The game is not won while one brick is still standing.");
const target = bricks[bricks.length - 1];
ball.x = target.x + target.w / 2;
ball.y = target.y + target.h + 20;
ball.vx = 0;
ball.vy = -180;
cc.frames(15);
expect(target.alive === false, "The last brick should break.");
expect(state === "won", `With every brick broken the game should be won; state is '${state}'.`);
expect(cc.texts().some((t) => /win/i.test(t)), "Tell the player they won.");
""",
        hint="After the brick loop: if (bricks.every((b) => !b.alive)) state = 'won';",
    ),
    Step(
        id="breakout-11-aim",
        track="Breakout",
        title="Aim with the paddle",
        teaches=(
            "If the paddle only flips vy, the ball's angle never changes "
            "and the player cannot aim. Real Breakout sends the ball off at "
            "an angle that depends on where it lands: the middle sends it "
            "straight up, the ends send it off to that side. Work out how "
            "far from the middle it hit, as -1 to 1; turn that into an "
            "angle (up to 60 degrees, Math.PI / 3); keep the speed the same "
            "- Math.hypot(vx, vy) - and split it: vx = speed * "
            "Math.sin(angle), vy = -speed * Math.cos(angle)."
        ),
        goal="When the ball hits the paddle, send it off at an angle set by where it landed - left end left, middle straight up, right end right - at the same speed.",
        starter=_B10,
        solution=_B11,
        check="""
const land = (offset) => {
  paddle.x = 200;
  ball.x = paddle.x + paddle.w / 2 + offset * (paddle.w / 2);
  ball.y = paddle.y - 30;
  ball.vx = 0;
  ball.vy = Math.hypot(180, 180);
  for (let i = 0; i < 30 && ball.vy > 0; i++) cc.frames(1);
  expect(ball.vy < 0, "The ball should bounce off the paddle.");
  expect(near(Math.hypot(ball.vx, ball.vy), Math.hypot(180, 180), 1), "Aiming should change the ball's direction, not its speed - work out speed = Math.hypot(vx, vy) first and keep it.");
  return ball.vx;
};
const left = land(-0.9);
const middle = land(0);
const right = land(0.9);
expect(left < -100, `Landing near the left end sent the ball off with vx ${Math.round(left)}; it should go well to the left.`);
expect(right > 100, `Landing near the right end sent the ball off with vx ${Math.round(right)}; it should go well to the right.`);
expect(Math.abs(middle) < 10, `Landing in the middle sent the ball off with vx ${Math.round(middle)}; it should go almost straight up.`);
""",
        hint="const offset = (ball.x - (paddle.x + paddle.w / 2)) / (paddle.w / 2); const angle = offset * (Math.PI / 3);",
    ),
    Step(
        id="breakout-12-yours",
        track="Breakout",
        title="Now it's yours",
        teaches=(
            "A second whole game, and most of it was parts you already had. "
            "Ideas, easier first: bricks in different colours by row, worth "
            "more near the top; bricks that take two hits; the ball "
            "speeding up a little on every paddle hit; a level made from "
            "strings like '##.##.##'; Enter to play again; a power-up that "
            "falls from a broken brick and widens the paddle when caught; "
            "two balls at once (make ball an array)."
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_B11,
        solution=_B11,
        check="",
    ),
)
