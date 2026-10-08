"""The fourth Canvas track: Snake.

Dodge and Breakout moved things smoothly, a little each frame. Snake moves
in jumps on a grid, so it needs what they did not: tile coordinates (a
cell is a column and a row, not pixels), a snake that is an array of cells,
a fixed timestep (movement on a tick, however fast frames come), a
direction that waits for the next tick and cannot turn back on itself,
food on a free cell, growth by keeping the tail, wall and self collision,
a score, and game over with a restart.

Same rules as the others: each step's starter is the step before,
finished; a check plays the program and never reads it.
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

_BG = """  ctx.fillStyle = '#10141f';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
"""

_GRID = """const CELL = 20;
const COLS = canvas.width / CELL;
const ROWS = canvas.height / CELL;
"""

_DRAW_CELL = """
function drawCell(col, row, color) {
  ctx.fillStyle = color;
  ctx.fillRect(col * CELL, row * CELL, CELL - 1, CELL - 1);
}
"""

_SNAKE = "let snake = [{ x: 12, y: 8 }, { x: 11, y: 8 }, { x: 10, y: 8 }];\n"
_DRAW_SNAKE = """  for (const s of snake) drawCell(s.x, s.y, '#68d391');
"""
_DRAW_FOOD = """  drawCell(food.x, food.y, '#fc8181');
"""

_TIME_STATE = """let dir = { x: 1, y: 0 };
let acc = 0;
const TICK = 0.12;
"""
_NEXT_DIR = "let nextDir = { x: 1, y: 0 };\n"

_TICK_UPDATE = """  acc += dt;
  while (acc >= TICK) {
    acc -= TICK;
    step();
  }
"""
_GUARD = "  if (state !== 'playing') return;\n"

_STEP3 = """
function step() {
  const head = { x: snake[0].x + dir.x, y: snake[0].y + dir.y };
  snake.unshift(head);
  snake.pop();
}
"""

_STEP4 = """
function step() {
  dir = nextDir;
  const head = { x: snake[0].x + dir.x, y: snake[0].y + dir.y };
  snake.unshift(head);
  snake.pop();
}
"""

_TURNS = """
const TURNS = {
  ArrowUp: { x: 0, y: -1 },
  ArrowDown: { x: 0, y: 1 },
  ArrowLeft: { x: -1, y: 0 },
  ArrowRight: { x: 1, y: 0 },
};
"""

_KEYS4 = """addEventListener('keydown', (e) => {
  if (TURNS[e.key]) nextDir = TURNS[e.key];
});
"""

_KEYS5 = """addEventListener('keydown', (e) => {
  const turn = TURNS[e.key];
  if (!turn) return;
  if (turn.x === -dir.x && turn.y === -dir.y) return;
  nextDir = turn;
});
"""

_KEYS11 = """addEventListener('keydown', (e) => {
  const turn = TURNS[e.key];
  if (turn && !(turn.x === -dir.x && turn.y === -dir.y)) nextDir = turn;
  if (e.key === 'Enter' && state === 'over') reset();
});
"""

_SPAWN = """
function spawnFood() {
  const free = [];
  for (let y = 0; y < ROWS; y++) {
    for (let x = 0; x < COLS; x++) {
      if (!snake.some((s) => s.x === x && s.y === y)) free.push({ x, y });
    }
  }
  food = free[Math.floor(Math.random() * free.length)];
}
spawnFood();
"""

_STEP7 = """
function step() {
  dir = nextDir;
  const head = { x: snake[0].x + dir.x, y: snake[0].y + dir.y };
  snake.unshift(head);
  if (head.x === food.x && head.y === food.y) spawnFood();
  else snake.pop();
}
"""

_STEP8 = """
function step() {
  dir = nextDir;
  const head = { x: snake[0].x + dir.x, y: snake[0].y + dir.y };
  if (head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS) {
    state = 'over';
    return;
  }
  snake.unshift(head);
  if (head.x === food.x && head.y === food.y) spawnFood();
  else snake.pop();
}
"""

_STEP9 = """
function step() {
  dir = nextDir;
  const head = { x: snake[0].x + dir.x, y: snake[0].y + dir.y };
  const eating = head.x === food.x && head.y === food.y;
  const body = eating ? snake : snake.slice(0, -1);
  const hitWall = head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS;
  const hitSelf = body.some((s) => s.x === head.x && s.y === head.y);
  if (hitWall || hitSelf) {
    state = 'over';
    return;
  }
  snake.unshift(head);
  if (eating) spawnFood();
  else snake.pop();
}
"""

_STEP10 = """
function step() {
  dir = nextDir;
  const head = { x: snake[0].x + dir.x, y: snake[0].y + dir.y };
  const eating = head.x === food.x && head.y === food.y;
  const body = eating ? snake : snake.slice(0, -1);
  const hitWall = head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS;
  const hitSelf = body.some((s) => s.x === head.x && s.y === head.y);
  if (hitWall || hitSelf) {
    state = 'over';
    return;
  }
  snake.unshift(head);
  if (eating) {
    score += 10;
    spawnFood();
  } else {
    snake.pop();
  }
}
"""

_RESET = """
function reset() {
  snake = [{ x: 12, y: 8 }, { x: 11, y: 8 }, { x: 10, y: 8 }];
  dir = { x: 1, y: 0 };
  nextDir = { x: 1, y: 0 };
  acc = 0;
  score = 0;
  state = 'playing';
  spawnFood();
}
"""

_TEXT_OVER = """  if (state === 'over') {
    ctx.fillStyle = 'white';
    ctx.font = '32px monospace';
    ctx.fillText('Game over', 150, 170);
  }
"""

_TEXT_SCORE = """  ctx.fillStyle = 'white';
  ctx.font = '16px monospace';
  ctx.fillText(`Score: ${score}`, 10, 20);
"""

_TEXT_OVER_RESTART = """  if (state === 'over') {
    ctx.fillStyle = 'white';
    ctx.font = '32px monospace';
    ctx.fillText('Game over', 150, 170);
    ctx.font = '16px monospace';
    ctx.fillText('Enter to play again', 160, 200);
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


_STATE3 = _GRID + _SNAKE + _TIME_STATE
_STATE4 = _STATE3 + _NEXT_DIR
_STATE6 = _STATE4 + "let food;\n"
_STATE8 = _STATE6 + "let state = 'playing';\n"
_STATE10 = _STATE8 + "let score = 0;\n"

_P0 = _program("", "", "")
_P1 = _program(_GRID, "", "  drawCell(3, 2, '#4fd1c5');\n", _DRAW_CELL)
_P2 = _program(_GRID + _SNAKE, "", _DRAW_SNAKE, _DRAW_CELL)
_P3 = _program(_STATE3, _TICK_UPDATE, _DRAW_SNAKE, _DRAW_CELL + _STEP3)
_P4 = _program(_STATE4, _TICK_UPDATE, _DRAW_SNAKE, _DRAW_CELL + _TURNS + _KEYS4 + _STEP4)
_P5 = _program(_STATE4, _TICK_UPDATE, _DRAW_SNAKE, _DRAW_CELL + _TURNS + _KEYS5 + _STEP4)
_P6 = _program(
    _STATE6, _TICK_UPDATE, _DRAW_FOOD + _DRAW_SNAKE,
    _DRAW_CELL + _TURNS + _KEYS5 + _SPAWN + _STEP4,
)
_P7 = _program(
    _STATE6, _TICK_UPDATE, _DRAW_FOOD + _DRAW_SNAKE,
    _DRAW_CELL + _TURNS + _KEYS5 + _SPAWN + _STEP7,
)
_P8 = _program(
    _STATE8, _GUARD + _TICK_UPDATE, _DRAW_FOOD + _DRAW_SNAKE + _TEXT_OVER,
    _DRAW_CELL + _TURNS + _KEYS5 + _SPAWN + _STEP8,
)
_P9 = _program(
    _STATE8, _GUARD + _TICK_UPDATE, _DRAW_FOOD + _DRAW_SNAKE + _TEXT_OVER,
    _DRAW_CELL + _TURNS + _KEYS5 + _SPAWN + _STEP9,
)
_P10 = _program(
    _STATE10, _GUARD + _TICK_UPDATE,
    _DRAW_FOOD + _DRAW_SNAKE + _TEXT_SCORE + _TEXT_OVER,
    _DRAW_CELL + _TURNS + _KEYS5 + _SPAWN + _STEP10,
)
_P11 = _program(
    _STATE10, _GUARD + _TICK_UPDATE,
    _DRAW_FOOD + _DRAW_SNAKE + _TEXT_SCORE + _TEXT_OVER_RESTART,
    _DRAW_CELL + _TURNS + _KEYS11 + _SPAWN + _STEP10 + _RESET,
)

# Shared by the checks that play the snake: put it somewhere, and wait for
# one move however the learner keeps time.
_H = """
const at = () => snake[0].x + "," + snake[0].y;
const tick = () => {
  const before = at();
  for (let i = 0; i < 30 && at() === before; i++) cc.frames(1);
};
const place = (cells, d) => {
  snake = cells.map(([x, y]) => ({ x, y }));
  dir = { x: d[0], y: d[1] };
  if (typeof nextDir !== "undefined") nextDir = { x: d[0], y: d[1] };
  if (typeof state !== "undefined") state = "playing";
};
const headIs = (x, y) => snake[0].x === x && snake[0].y === y;
const onSnake = (c) => snake.some((s) => s.x === c.x && s.y === c.y);
"""


SNAKE_STEPS: tuple[Step, ...] = (
    Step(
        id="snake-01-tiles",
        track="Snake",
        title="Tiles, not pixels",
        teaches=(
            "Snake lives on a grid, so think in tiles: a cell is a column "
            "and a row, and only when you draw does it become pixels - "
            "column * CELL, row * CELL. Keep one CELL size and work the "
            "number of columns and rows out from the canvas (COLS = "
            "canvas.width / CELL) rather than typing 24 and 16, and a "
            "different size later is a one-line change. Everything else "
            "in the game is whole numbers: you cannot be at column 3.4."
        ),
        goal="Add const CELL = 20, COLS and ROWS worked out from the canvas, and drawCell(col, row, color), which fills one tile. Draw a tile at column 3, row 2 each frame.",
        starter=_P0,
        solution=_P1,
        check="""
expect(typeof CELL === "number" && CELL === 20, "Add const CELL = 20; - the size of one tile in pixels.");
expect(COLS === 24 && ROWS === 16, `The grid is ${typeof COLS === "number" ? COLS : "?"} by ${typeof ROWS === "number" ? ROWS : "?"}; a 480 by 320 canvas of 20 pixel tiles is 24 by 16. Work them out: canvas.width / CELL.`);
expect(typeof drawCell === "function", "Write function drawCell(col, row, color) that fills one tile.");
drawCell(7, 4, "orange");
const r = cc.rects().find((q) => q.x === 140 && q.y === 80);
expect(r, "drawCell(7, 4, ...) should fill a tile at pixel x 140, y 80: column * CELL, row * CELL.");
expect(r.w >= CELL - 2 && r.w <= CELL && r.h >= CELL - 2 && r.h <= CELL, "A tile should be about CELL pixels across (CELL - 1 leaves a thin line between tiles).");
cc.frames(1);
expect(cc.rects().some((q) => q.x === 60 && q.y === 40), "Draw a tile at column 3, row 2 each frame: drawCell(3, 2, ...) inside draw(), after the background.");
""",
        hint="function drawCell(col, row, color) { ctx.fillStyle = color; ctx.fillRect(col * CELL, row * CELL, CELL - 1, CELL - 1); }",
    ),
    Step(
        id="snake-02-snake",
        track="Snake",
        title="A snake is an array of cells",
        teaches=(
            "The snake is a list of cells, head first: snake[0] is the "
            "head, the last one the tail, and each cell is { x, y } in "
            "tiles. Nothing else is stored - no direction per segment, no "
            "pixels. Drawing is a loop over the list; moving will be "
            "adding a cell at the front and taking one off the back. "
            "Declare it with let, not const, because starting a new game "
            "will want to give it a new array."
        ),
        goal="Make let snake with three cells, head first: { x: 12, y: 8 }, { x: 11, y: 8 }, { x: 10, y: 8 }. Draw every cell each frame, and take out the test tile.",
        starter=_P1,
        solution=_P2,
        check=_H + """
expect(typeof snake !== "undefined" && Array.isArray(snake), "Make an array called snake: let snake = [{ x: 12, y: 8 }, ...];");
expect(snake.length === 3, `The snake has ${snake.length} cells; start it with 3.`);
expect(headIs(12, 8), "The head is snake[0], and it starts at column 12, row 8 (in tiles, not pixels).");
expect(snake[1].x === 11 && snake[1].y === 8 && snake[2].x === 10 && snake[2].y === 8, "The body trails behind the head, to the left: { x: 11, y: 8 } then { x: 10, y: 8 }.");
cc.frames(1);
const drawn = cc.rects();
for (const s of snake) {
  expect(drawn.some((q) => q.x === s.x * CELL && q.y === s.y * CELL), `Draw every cell of the snake each frame - there is nothing at column ${s.x}, row ${s.y}. A loop over the array does it.`);
}
""",
        hint="for (const s of snake) drawCell(s.x, s.y, '#68d391'); inside draw().",
    ),
    Step(
        id="snake-03-tick",
        track="Snake",
        title="Move on a tick",
        teaches=(
            "A snake that jumped a cell every frame would race on a fast "
            "screen and crawl on a slow one. Give it its own clock: add "
            "each frame's dt to an accumulator, and while the accumulator "
            "holds a whole TICK, take TICK off it and step once. Taking "
            "off TICK (rather than zeroing it) keeps the leftover, so the "
            "average speed is right however long frames take. A step puts "
            "a new head on the front, one cell along dir, and takes the "
            "tail off the back: the snake slides without changing length."
        ),
        goal="Add let dir = { x: 1, y: 0 }, let acc = 0 and const TICK = 0.12. Every TICK seconds of accumulated dt, step the snake one cell along dir: a new head on the front, the tail off the back.",
        starter=_P2,
        solution=_P3,
        check=_H + """
expect(Array.isArray(snake) && snake.length === 3, "Start with the three-cell snake.");
cc.frames(1);
expect(snake[0].x === 12 && snake[0].y === 8, "The snake moved in the very first frame. It should move once per tick - every 0.12 seconds - not once per frame.");
cc.frames(59);
const moved = snake[0].x - 12;
expect(moved >= 7 && moved <= 9, `After one second the head moved ${moved} cells along; a tick every 0.12 seconds is about 8. Add dt to acc each frame, and step while acc >= TICK.`);
expect(snake[0].y === 8, "Heading right (dir { x: 1, y: 0 }), the head's row should not change.");
const x1 = snake[0].x;
cc.frames(30, 1000 / 30);
const moved2 = snake[0].x - x1;
expect(moved2 >= 7 && moved2 <= 9, `On a slower screen (30 frames a second) the head moved ${moved2} cells in a second; it should still be about 8. Count time with dt, not frames.`);
expect(snake.length === 3, `The snake is ${snake.length} cells long now; it should slide, not grow - take the tail off after adding a head.`);
for (let i = 0; i < snake.length - 1; i++) {
  const gap = Math.abs(snake[i].x - snake[i + 1].x) + Math.abs(snake[i].y - snake[i + 1].y);
  expect(gap === 1, "Each cell should sit right next to the one before it - add the new head with unshift, and take the tail with pop.");
}
""",
        hint="acc += dt; while (acc >= TICK) { acc -= TICK; step(); }   and step(): snake.unshift(newHead); snake.pop();",
    ),
    Step(
        id="snake-04-steer",
        track="Snake",
        title="Steer on the tick",
        teaches=(
            "A key press should not move the snake - the tick does. The "
            "key only records what you want: nextDir. At the start of "
            "each step the snake adopts it (dir = nextDir) and moves. "
            "That is why the snake turns on a grid line instead of "
            "halfway between cells, and why a key pressed any time in "
            "the last tick counts. A table from key name to direction, "
            "TURNS, keeps the handler to one line."
        ),
        goal="Add let nextDir and arrow-key input: a key sets nextDir, and step() copies nextDir into dir before it moves, so the snake turns on the tick.",
        starter=_P3,
        solution=_P4,
        check=_H + """
place([[12, 8], [11, 8], [10, 8]], [1, 0]);
cc.press("ArrowDown");
tick();
expect(headIs(12, 9), `After pressing ArrowDown the head should step down a row, to column 12, row 9; it is at ${at()}. y grows downwards, so down is { x: 0, y: 1 }.`);
cc.press("ArrowLeft");
tick();
expect(headIs(11, 9), `After ArrowLeft the head should step left, to column 11, row 9; it is at ${at()}.`);
cc.press("ArrowUp");
tick();
expect(headIs(11, 8), `After ArrowUp the head should step up, to column 11, row 8; it is at ${at()}. Up is { x: 0, y: -1 }.`);
cc.press("ArrowRight");
tick();
expect(headIs(12, 8), `After ArrowRight the head should step right, to column 12, row 8; it is at ${at()}.`);
expect(snake.length === 3, "Turning should not change the snake's length.");
""",
        hint="const TURNS = { ArrowUp: { x: 0, y: -1 }, ... }; addEventListener('keydown', (e) => { if (TURNS[e.key]) nextDir = TURNS[e.key]; });  and dir = nextDir; at the top of step().",
    ),
    Step(
        id="snake-05-no-reverse",
        track="Snake",
        title="No turning back",
        teaches=(
            "Heading right, pressing left would put the new head on the "
            "snake's own neck: an instant death the player never chose. "
            "So ignore a turn that is the exact opposite of the way the "
            "snake is going: turn.x === -dir.x && turn.y === -dir.y. "
            "Compare with dir, the direction the snake LAST MOVED, not "
            "with nextDir. Compare with nextDir and a quick Up then Left "
            "slips through: Left is fine against Up, and the snake "
            "reverses on the next tick."
        ),
        goal="Ignore a key that would turn the snake straight back on itself, judged against dir, the direction it last moved in, not against nextDir.",
        starter=_P4,
        solution=_P5,
        check=_H + """
place([[12, 8], [11, 8], [10, 8]], [1, 0]);
cc.press("ArrowLeft");
tick();
expect(headIs(13, 8), `Heading right, ArrowLeft was obeyed and the head is at ${at()} - on top of the body. Ignore a turn that is exactly opposite to dir.`);
place([[12, 8], [11, 8], [10, 8]], [1, 0]);
cc.press("ArrowUp");
cc.press("ArrowLeft");
tick();
expect(headIs(12, 7), `Up then Left within one tick sent the head to ${at()}. Left is the opposite of the way the snake LAST MOVED (right), so it is still ignored - compare with dir, not nextDir.`);
cc.press("ArrowLeft");
tick();
expect(headIs(11, 7), `After moving up, a turn to the left is allowed; the head is at ${at()} and should be at column 11, row 7.`);
""",
        hint="if (turn.x === -dir.x && turn.y === -dir.y) return;  before nextDir = turn;",
    ),
    Step(
        id="snake-06-food",
        track="Snake",
        title="Food on a free cell",
        teaches=(
            "Pick a random column and row, and sometimes it is under the "
            "snake. You could keep guessing until it is free - but a "
            "long snake makes that slow, and there is a neater way: "
            "collect every free cell into a list, then choose one from "
            "it. Math.floor(Math.random() * list.length) is an index "
            "that is always inside the list. It also runs once and cannot "
            "loop for ever. Call it at the start, and again whenever the "
            "food is eaten."
        ),
        goal="Add let food and spawnFood(): list every free cell, choose one at random with Math.random, and call it once at the start. Draw the food.",
        starter=_P5,
        solution=_P6,
        check=_H + """
expect(typeof spawnFood === "function", "Write function spawnFood() that puts a new { x, y } into food.");
expect(typeof food === "object" && food !== null, "Call spawnFood() when the game starts, so there is food to find.");
const legal = (f) => f && Number.isInteger(f.x) && Number.isInteger(f.y) && f.x >= 0 && f.x < COLS && f.y >= 0 && f.y < ROWS;
expect(legal(food), "Food is a whole-number cell inside the grid: x from 0 to COLS - 1, y from 0 to ROWS - 1.");
expect(!onSnake(food), "The first food landed on the snake.");
cc.frames(1);
expect(cc.rects().some((q) => q.x === food.x * CELL && q.y === food.y * CELL), "Draw the food each frame, in its own colour.");
const top = [];
for (let y = 0; y < 8; y++) for (let x = 0; x < COLS; x++) top.push([x, y]);
place(top, [1, 0]);
const seen = new Set();
for (let i = 0; i < 200; i++) {
  spawnFood();
  expect(legal(food), `Food landed at column ${food && food.x}, row ${food && food.y} - outside the grid. A random column is Math.floor(Math.random() * COLS), never COLS itself.`);
  expect(!onSnake(food), "With the snake filling the top half of the grid, food landed on it. Only choose from the cells the snake is not on.");
  seen.add(food.x + "," + food.y);
}
expect(seen.size > 20, "The food keeps landing in the same few places - choose with Math.random.");
""",
        hint="Loop over every y and x, push { x, y } into free when no snake cell matches, then food = free[Math.floor(Math.random() * free.length)];",
    ),
    Step(
        id="snake-07-grow",
        track="Snake",
        title="Eat and grow",
        teaches=(
            "Growing is the cheapest trick in the game: a step normally "
            "adds a head AND removes the tail. When the new head lands on "
            "the food, skip the removal. The snake is one cell longer, "
            "and the tail has not moved. Then call spawnFood() - after "
            "the new head is on the snake, so the new food cannot land "
            "on it. Compare cells by x and y; two objects with the same "
            "numbers are still two different objects."
        ),
        goal="When the new head lands on the food, keep the tail (the snake grows by one) and call spawnFood(). Otherwise drop the tail as before.",
        starter=_P6,
        solution=_P7,
        check=_H + """
place([[10, 8], [9, 8], [8, 8]], [1, 0]);
food = { x: 11, y: 8 };
tick();
expect(headIs(11, 8), `The head should step onto the food at column 11; it is at ${at()}.`);
expect(snake.length === 4, `The snake ate and is ${snake.length} cells long; it should be 4. When the head lands on the food, do not remove the tail.`);
expect(snake[3].x === 8 && snake[3].y === 8, "A snake that grows keeps its tail where it was; only the head moves.");
expect(!(food.x === 11 && food.y === 8) && !onSnake(food), "After eating, call spawnFood() so there is new food, and not under the snake.");
food = { x: 0, y: 0 };
tick();
expect(snake.length === 4, `A step that does not eat should leave the length alone; the snake is ${snake.length} now. Take the tail off unless it ate.`);
expect(headIs(12, 8), "The snake should keep moving after it eats.");
""",
        hint="snake.unshift(head); if (head.x === food.x && head.y === food.y) spawnFood(); else snake.pop();",
    ),
    Step(
        id="snake-08-walls",
        track="Snake",
        title="Hit the wall",
        teaches=(
            "The grid has columns 0 to COLS - 1, so the first column off "
            "the edge is COLS itself, and the check is >= COLS, not > "
            "COLS: get that off by one and the snake slides one cell "
            "into the wall before it dies. Work out the new head first, "
            "test it, and only then add it to the snake - a snake never "
            "drawn off the grid needs no cleaning up. Put what the game "
            "is doing in let state = 'playing'; update stops when it "
            "is not."
        ),
        goal="Add let state = 'playing'. If the new head would be off the grid, set state to 'over' without moving the snake, stop updating, and write 'Game over' on the screen.",
        starter=_P7,
        solution=_P8,
        check=_H + """
expect(typeof state === "string" && state === "playing", "Keep what the game is doing in let state = 'playing';");
const inside = (c) => c.x >= 0 && c.x < COLS && c.y >= 0 && c.y < ROWS;
const walls = [
  ["right", [[22, 8], [21, 8], [20, 8]], [1, 0]],
  ["left", [[1, 8], [2, 8], [3, 8]], [-1, 0]],
  ["top", [[12, 1], [12, 2], [12, 3]], [0, -1]],
  ["bottom", [[12, 14], [12, 13], [12, 12]], [0, 1]],
];
for (const [name, cells, d] of walls) {
  place(cells, d);
  food = { x: 0, y: 15 };
  tick();
  expect(state === "playing", `Moving onto the ${name} edge cell is still legal, but the game ended there. The edge cells are 0 and COLS - 1 (or ROWS - 1): the wall is one step further.`);
  tick();
  expect(state === "over", `The snake ran into the ${name} wall and state is '${state}'. When the new head is off the grid (x < 0, x >= COLS, y < 0 or y >= ROWS), set state to 'over'.`);
  expect(inside(snake[0]), `The head is at column ${snake[0].x}, row ${snake[0].y} - outside the grid. Test the new head before adding it to the snake.`);
}
const frozen = JSON.stringify(snake);
cc.frames(60);
expect(JSON.stringify(snake) === frozen, "After game over the snake should stop moving.");
expect(cc.texts().some((t) => /game over/i.test(t)), "When the game is over, say so on the screen.");
""",
        hint="if (head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS) { state = 'over'; return; }  and  if (state !== 'playing') return;  at the top of update.",
    ),
    Step(
        id="snake-09-self",
        track="Snake",
        title="Don't bite yourself",
        teaches=(
            "The new head dies if it lands on any cell of the body: "
            "snake.some((s) => s.x === head.x && s.y === head.y). There "
            "is one cell to be careful of: the tail. On an ordinary step "
            "the tail moves away as the head arrives, so chasing your own "
            "tail is safe, and a snake that dies there feels cheated. "
            "When the snake eats, the tail stays - and then that cell "
            "does count. So test against the whole body only when eating; "
            "otherwise leave the last cell out with slice(0, -1)."
        ),
        goal="If the new head lands on the snake's own body, the game is over. The tail cell does not count unless the snake is eating, because it is about to move away.",
        starter=_P8,
        solution=_P9,
        check=_H + """
place([[12, 8], [11, 8], [10, 8]], [1, 0]);
food = { x: 20, y: 12 };
tick();
expect(state === "playing" && headIs(13, 8), "A snake just moving along ended the game. Test the new head against the body before it is added, or the head always finds itself.");
place([[5, 5], [6, 5], [6, 6], [5, 6], [4, 6]], [0, 1]);
food = { x: 20, y: 12 };
tick();
expect(state === "over", `The head turned down into its own body at column 5, row 6 and state is '${state}'. If the new head is on a snake cell, set state to 'over'.`);
place([[5, 5], [6, 5], [6, 6], [5, 6]], [0, 1]);
food = { x: 20, y: 12 };
tick();
expect(state === "playing" && headIs(5, 6) && snake.length === 4, `The head stepped into the cell the tail was leaving, and the game ended. The tail moves away on the same step, so it is safe - leave the last cell out when testing, unless the snake is eating (then the tail stays).`);
""",
        hint="const eating = ...; const body = eating ? snake : snake.slice(0, -1); then body.some((s) => s.x === head.x && s.y === head.y)",
    ),
    Step(
        id="snake-10-score",
        track="Snake",
        title="Keep score",
        teaches=(
            "A score is a number that changes in exactly one place: here, "
            "the branch of step() where the snake eats. Put the addition "
            "anywhere else - in the tick itself, say - and it counts "
            "time, not food. Drawing text needs a font and a colour and "
            "a position, then fillText. Template literals make the "
            "message in one go: `Score: ${score}`. The text goes in "
            "draw(), every frame, so it always shows the latest number."
        ),
        goal="Add let score = 0. Eating food adds 10 to it. Write the score on the screen.",
        starter=_P9,
        solution=_P10,
        check=_H + """
expect(typeof score === "number" && score === 0, "Start with let score = 0;");
cc.frames(1);
expect(cc.texts().some((t) => /score/i.test(t) && t.includes("0")), "Show the score on the screen from the start: it should say Score: 0.");
place([[10, 8], [9, 8], [8, 8]], [1, 0]);
food = { x: 11, y: 8 };
tick();
expect(score === 10, `One piece of food is worth 10; the score is ${score}.`);
cc.frames(1);
expect(cc.texts().some((t) => t.includes("10")), "Show the new score on the screen.");
food = { x: 0, y: 0 };
tick();
expect(score === 10, `A step that eats nothing scored: the score is ${score}. Only eating adds to it.`);
""",
        hint="In step(): if (eating) { score += 10; spawnFood(); } and ctx.fillText(`Score: ${score}`, 10, 20); in draw().",
    ),
    Step(
        id="snake-11-restart",
        track="Snake",
        title="Play again",
        teaches=(
            "A restart is a function that puts every piece of the game "
            "back as it was at the start: the snake, dir AND nextDir "
            "(leave nextDir pointing up and the new snake turns up on "
            "its first step), the score, the state - and new food. Miss "
            "one and the second game plays differently from the first. "
            "Hook it to Enter, but only when the game is over: Enter "
            "in the middle of a game, or any other key at all, should "
            "not wipe it. Keep the starting values in one place."
        ),
        goal="When the game is over, Enter starts again: put snake, dir, nextDir, acc, score and state back as they began, and spawn new food. Enter does nothing during a game.",
        starter=_P10,
        solution=_P11,
        check=_H + """
place([[12, 1], [12, 2], [12, 3]], [0, -1]);
food = { x: 20, y: 12 };
score = 30;
cc.press("Enter");
expect(score === 30 && headIs(12, 1), "Enter in the middle of a game restarted it. Only restart when state is 'over'.");
tick();
tick();
expect(state === "over", "The snake should have hit the top wall.");
cc.press("ArrowLeft");
expect(state === "over", "A key other than Enter restarted the game. Only Enter should.");
cc.press("Enter");
expect(state === "playing", `Pressing Enter after game over should start a new game; state is '${state}'.`);
expect(score === 0, `A new game should start with a score of 0; it is ${score}.`);
expect(snake.length === 3 && headIs(12, 8), "A new game starts with the three-cell snake, head at column 12, row 8.");
expect(!onSnake(food), "The new food should not be on the new snake.");
tick();
expect(headIs(13, 8), `The new snake should set off to the right, from column 12 to 13; its head is at ${at()}. Put dir and nextDir back to { x: 1, y: 0 }.`);
""",
        hint="function reset() { snake = [...]; dir = { x: 1, y: 0 }; nextDir = { x: 1, y: 0 }; acc = 0; score = 0; state = 'playing'; spawnFood(); }",
    ),
    Step(
        id="snake-12-yours",
        track="Snake",
        title="Now it's yours",
        teaches=(
            "A whole game on a grid, with its own clock. Ideas, easier "
            "first: speed up a little every time it eats (make TICK a "
            "let); walls that wrap round to the other side; a best score "
            "kept in localStorage; P to pause; a second kind of food "
            "worth more that vanishes; WASD as well as the arrows; a "
            "queue of two turns, so two quick presses both count; "
            "obstacles; and a win when the snake fills the board - what "
            "does spawnFood do when there is no free cell?"
        ),
        goal="No check here - change anything. Run it, play it, break it, fix it.",
        starter=_P11,
        solution=_P11,
        check="",
    ),
)
