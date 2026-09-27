"""Predict the output, in JavaScript, for game code.

A game is one loop run sixty times a second, and most of what goes
wrong in one is arithmetic that is almost right: a position moved by a
speed that forgot the frame time, a wrap-around that works going right
and not going left, a tile coordinate that comes out as -0, two boxes
that touch without overlapping. The rest is JavaScript being itself in
the places a game leans on hardest — a Set of the keys being held, a
string used as a row of tiles that cannot be written to, an array of
entities that forgets to lose its dead ones, and `this` inside a timer.

Everything here runs in plain Node with no page and no canvas, the way
the logic of a game should be testable anyway. Every expected output
was worked out by hand first and then checked against what Node
printed, and tests/test_predict_jsgame.py keeps checking.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p

GAME = "Game code"


JS_GAME_PUZZLES: tuple[Puzzle, ...] = (
    _p(
        id="predict-jsg-ticks-inclusive",
        level=1,
        name="How many ticks is <= 3",
        family=GAME,
        language="javascript",
        code=(
            "const ticks = [];\n"
            "for (let tick = 0; tick <= 3; tick++) ticks.push(tick);\n"
            "let x = 0;\n"
            "for (const t of ticks) x += 2;\n"
            "console.log(ticks.length, x);"
        ),
        expect="4 8",
        why=(
            "Counting from 0 up to and including 3 is four ticks, not "
            "three: 0, 1, 2 and 3. `<=` in a loop header is almost always "
            "one more pass than the number written next to it, and in a "
            "game loop that is one more frame of movement than you "
            "planned. `tick < 3` runs three times."
        ),
    ),
    _p(
        id="predict-jsg-clamp-order",
        level=1,
        name="Keeping a value in range",
        family=GAME,
        language="javascript",
        code=(
            "const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));\n"
            "console.log(clamp(150, 0, 100), clamp(-5, 0, 100), clamp(42, 0, 100));\n"
            "console.log(Math.max(0, Math.min(100, 150)), Math.min(0, Math.max(100, 150)));"
        ),
        expect="100 0 42\n100 0",
        why=(
            "A clamp is a max against the floor inside a min against the "
            "ceiling, or the same two the other way round — both orders "
            "work as long as each limit goes to the right function. The "
            "last call swaps them: max against the ceiling gives 150, "
            "then min against the floor gives 0, whatever went in. Health "
            "clamped that way is always zero."
        ),
    ),
    _p(
        id="predict-jsg-tile-from-pixel",
        level=2,
        name="Which tile is the pixel in",
        family=GAME,
        language="javascript",
        code=(
            "const TILE = 16;\n"
            "const px = 40, py = -1;\n"
            "console.log(px / TILE, Math.floor(px / TILE));\n"
            "console.log(Math.floor(py / TILE), Math.trunc(py / TILE));"
        ),
        expect="2.5 2\n-1 -0",
        why=(
            "JavaScript has no integer division: `/` always gives the "
            "exact answer, so pixel 40 is 2.5 tiles in and `Math.floor` "
            "is what turns it into tile 2. For a pixel left of the map "
            "the two roundings split. floor goes down to tile -1, which "
            "is right; trunc goes towards zero and gives -0, which is "
            "still zero, so a sprite one pixel off the edge is treated "
            "as standing on tile 0. Use floor for tile coordinates."
        ),
    ),
    _p(
        id="predict-jsg-negative-modulo",
        level=2,
        name="Wrapping round the left edge",
        family=GAME,
        language="javascript",
        code=(
            "const W = 10;\n"
            "const a = -1 % W;\n"
            "const b = ((-1 % W) + W) % W;\n"
            "const c = ((-23 % W) + W) % W;\n"
            "console.log(a, b, c, 23 % W);"
        ),
        expect="-1 9 7 3",
        why=(
            "`%` in JavaScript is a remainder, and it keeps the sign of "
            "the number on the left, so -1 % 10 is -1 rather than 9. A "
            "ship that flies off the left edge ends up at x = -1, off "
            "screen, instead of reappearing on the right. Adding the "
            "width and taking the remainder again lands every number, "
            "however negative, in 0 to 9. Python's % already does this; "
            "JavaScript's and C's do not."
        ),
    ),
    _p(
        id="predict-jsg-forgot-dt",
        level=2,
        name="Thirty frames a second, and sixty",
        family=GAME,
        language="javascript",
        code=(
            "function run(fps, useDt) {\n"
            "  let x = 0;\n"
            "  const dt = 1 / fps;\n"
            "  for (let f = 0; f < fps; f++) x += useDt ? 60 * dt : 1;\n"
            "  return Math.round(x);\n"
            "}\n"
            "console.log(run(30, false), run(60, false), run(30, true), run(60, true));"
        ),
        expect="30 60 60 60",
        why=(
            "Each call simulates one second. Moving a fixed amount per "
            "frame means the distance depends on how many frames there "
            "were, so the slow machine covers half the ground. Moving "
            "speed times the frame's duration — 60 units a second times "
            "dt — covers 60 either way. Any number added to a position "
            "every frame should have `* dt` on it."
        ),
    ),
    _p(
        id="predict-jsg-aabb-touching",
        level=2,
        name="Touching is not overlapping",
        family=GAME,
        language="javascript",
        code=(
            "function overlaps(a, b) {\n"
            "  return a.x < b.x + b.w && a.x + a.w > b.x &&\n"
            "         a.y < b.y + b.h && a.y + a.h > b.y;\n"
            "}\n"
            "const player = { x: 0, y: 0, w: 10, h: 10 };\n"
            "const wall = { x: 10, y: 0, w: 10, h: 10 };\n"
            "const coin = { x: 9, y: 9, w: 4, h: 4 };\n"
            "console.log(overlaps(player, wall), overlaps(player, coin));"
        ),
        expect="false true",
        why=(
            "Two boxes overlap when each one starts before the other "
            "ends, on both axes. The player ends at x = 10 and the wall "
            "starts there, and 10 > 10 is false, so standing flush "
            "against a wall is not a collision — which is what lets a "
            "player slide along it. The coin shares a single pixel "
            "corner, from 9 to 10 on each axis, and that is enough."
        ),
    ),
    _p(
        id="predict-jsg-sprite-frames",
        level=2,
        name="Which cell of the sprite sheet",
        family=GAME,
        language="javascript",
        code=(
            "const COLS = 4, SIZE = 32, FRAMES = 6, FRAME_MS = 100;\n"
            "for (const t of [0, 250, 590, 610]) {\n"
            "  const frame = Math.floor(t / FRAME_MS) % FRAMES;\n"
            "  const sx = (frame % COLS) * SIZE;\n"
            "  const sy = Math.floor(frame / COLS) * SIZE;\n"
            "  console.log(t, frame, sx, sy);\n"
            "}"
        ),
        expect="0 0 0 0\n250 2 64 0\n590 5 32 32\n610 0 0 0",
        why=(
            "Time divided by frame length, floored, is how many frames "
            "have gone by; `% FRAMES` loops the animation, which is why "
            "610 ms is back on frame 0. Then the frame number is split "
            "across a grid four wide: the remainder is the column and "
            "the floored quotient is the row. Frame 5 is the second cell "
            "of the second row, 32 pixels in each way."
        ),
    ),
    _p(
        id="predict-jsg-held-keys",
        level=2,
        name="The keys being held",
        family=GAME,
        language="javascript",
        code=(
            "const held = new Set();\n"
            'held.add("ArrowLeft");\n'
            'held.add("ArrowLeft");\n'
            'held.add("ArrowRight");\n'
            'held.delete("arrowright");\n'
            'const dx = held.has("ArrowRight") - held.has("ArrowLeft");\n'
            "console.log(held.size, dx);"
        ),
        expect="2 0",
        why=(
            "A Set keeps one of each, so a key that auto-repeats its "
            "keydown is still one key held. The delete misses because "
            "key names are case-sensitive, and ArrowRight is still in "
            "there. Subtracting two booleans turns them into 1 and 0 "
            "first, so holding both arrows is 1 - 1: standing still, "
            "which is usually what a game wants."
        ),
    ),
    _p(
        id="predict-jsg-string-tiles",
        level=3,
        name="Writing into a row of tiles",
        family=GAME,
        language="javascript",
        code=(
            'const map = ["#..", "#.#"];\n'
            'map[0][1] = "@";\n'
            "console.log(map[0], map[1][2], map[1].length);\n"
            'const row = map[0].split("");\n'
            'row[1] = "@";\n'
            'map[0] = row.join("");\n'
            "console.log(map[0], map[2]?.[0]);"
        ),
        expect="#.. # 3\n#@. undefined",
        why=(
            "A map written as strings is easy to read and to index — "
            "`map[y][x]` is the tile — but strings cannot be changed, "
            "and outside strict mode writing to one of its characters "
            "is ignored without a word. To edit a tile, split the row "
            "into an array and join it back, or keep the map as arrays "
            "from the start. `?.` is the safe way to ask about a row "
            "that is not there."
        ),
    ),
    _p(
        id="predict-jsg-filter-dropped",
        level=3,
        name="The dead enemies that stay",
        family=GAME,
        language="javascript",
        code=(
            'let enemies = [{ n: "bat", hp: 0 }, { n: "orc", hp: 3 }, { n: "imp", hp: 0 }];\n'
            "enemies.filter((e) => e.hp > 0);\n"
            "console.log(enemies.length);\n"
            "enemies = enemies.filter((e) => e.hp > 0);\n"
            'console.log(enemies.length, enemies.map((e) => e.n).join());'
        ),
        expect="3\n1 orc",
        why=(
            "`filter` never changes the array it is called on. It builds "
            "a new one and hands it back, and the first call throws that "
            "away, so all three are still being updated and drawn. The "
            "cull only happens when the result is assigned — which is "
            "also why the list is `let` rather than `const`."
        ),
    ),
    _p(
        id="predict-jsg-float-equals",
        level=3,
        name="Ten steps of a tenth",
        family=GAME,
        language="javascript",
        code=(
            "let t = 0;\n"
            "for (let i = 0; i < 10; i++) t += 0.1;\n"
            "console.log(t === 1, t);\n"
            "console.log(Math.abs(t - 1) < 1e-9);"
        ),
        expect="false 0.9999999999999999\ntrue",
        why=(
            "0.1 has no exact binary form, and ten of them added up "
            "fall a hair short of 1. A door that opens when its timer "
            "`=== 1`, or a platform that stops when its x `=== target`, "
            "never does. Compare within a small tolerance, or use `>=` "
            "so that passing the mark counts."
        ),
    ),
    _p(
        id="predict-jsg-state-table",
        level=3,
        name="A state machine in a table",
        family=GAME,
        language="javascript",
        code=(
            "const next = {\n"
            '  idle: { jump: "air", run: "running" },\n'
            '  running: { stop: "idle", jump: "air" },\n'
            '  air: { land: "idle" },\n'
            "};\n"
            'let state = "idle";\n'
            "const seen = [];\n"
            'for (const ev of ["land", "run", "jump", "jump", "land"]) {\n'
            "  state = next[state][ev] ?? state;\n"
            "  seen.push(state);\n"
            "}\n"
            'console.log(seen.join(" > "));'
        ),
        expect="idle > running > air > air > idle",
        why=(
            "Each state lists only the events it answers to. Landing "
            "while idle, or jumping while already in the air, finds "
            "nothing in the table — undefined — and `?? state` keeps the "
            "state as it was. That is the whole trick of a state "
            "machine: a double jump is not a bug to patch, it is an "
            "entry that is not there."
        ),
    ),
    _p(
        id="predict-jsg-fixed-step",
        level=3,
        name="A fixed step from uneven frames",
        family=GAME,
        language="javascript",
        code=(
            "const STEP = 10;\n"
            "let acc = 0, updates = 0;\n"
            "for (const frame of [16, 16, 3, 27]) {\n"
            "  acc += frame;\n"
            "  while (acc >= STEP) {\n"
            "    acc -= STEP;\n"
            "    updates++;\n"
            "  }\n"
            "}\n"
            "console.log(updates, acc);"
        ),
        expect="6 2",
        why=(
            "The frames are uneven but the physics runs in steps of "
            "exactly 10 ms: time is saved up and spent a step at a time. "
            "16 gives one step and 6 left over, the next 16 makes 22 — "
            "two steps, 2 left — 3 is not enough for any, and 27 on top "
            "of 5 is three more. Six in all, and 2 ms waiting for the "
            "next frame. Same inputs, same steps, on any machine."
        ),
    ),
    _p(
        id="predict-jsg-timer-loop",
        level=3,
        name="A loop run by a timer",
        family=GAME,
        language="javascript",
        code=(
            "let frame = 0;\n"
            "function loop() {\n"
            "  frame++;\n"
            '  console.log("frame", frame);\n'
            "  if (frame < 3) setTimeout(loop, 0);\n"
            "}\n"
            "setTimeout(loop, 0);\n"
            'console.log("started at frame", frame);'
        ),
        expect="started at frame 0\nframe 1\nframe 2\nframe 3",
        why=(
            "A game loop in JavaScript is a function that asks to be "
            "called again, not a `while` — a while loop would never let "
            "the page draw. setTimeout only queues the call, even with "
            "0 ms, so the last line runs first and the frames follow. "
            "In a browser the same shape is written with "
            "requestAnimationFrame."
        ),
    ),
    _p(
        id="predict-jsg-splice-in-loop",
        level=4,
        name="Removing bullets as you go",
        family=GAME,
        language="javascript",
        code=(
            "const bullets = [{ id: 1, age: 9 }, { id: 2, age: 9 }, { id: 3, age: 1 }];\n"
            "for (let i = 0; i < bullets.length; i++) {\n"
            "  if (bullets[i].age > 5) bullets.splice(i, 1);\n"
            "}\n"
            "console.log(bullets.map((b) => b.id));"
        ),
        expect="[ 2, 3 ]",
        why=(
            "Splicing out bullet 1 slides every later bullet down one "
            "place, so bullet 2 moves into index 0 — and the loop has "
            "already moved on to index 1. Two old bullets side by side "
            "and the second one is never looked at. Walk the array "
            "backwards when removing from it, or build a new one with "
            "filter."
        ),
    ),
    _p(
        id="predict-jsg-nan-velocity",
        level=4,
        name="The coin with no vertical speed",
        family=GAME,
        language="javascript",
        code=(
            "const coin = { x: 5, y: 5, vx: 2 };\n"
            "const dt = 0.5;\n"
            "coin.x += coin.vx * dt;\n"
            "coin.y += coin.vy * dt;\n"
            "console.log(coin.x, coin.y, coin.y > 0, coin.y < 0);\n"
            "console.log(coin.y === coin.y, Number.isNaN(coin.y));"
        ),
        expect="6 NaN false false\nfalse true",
        why=(
            "The object was never given a vy, so reading it gives "
            "undefined, and undefined times a number is NaN — no error, "
            "no warning. NaN then spreads through every sum it touches, "
            "and every comparison with it is false, including with "
            "itself, so bounds checks let the coin straight through and "
            "the canvas quietly draws nothing. Give every entity every "
            "field it will be moved by, even when it is 0."
        ),
    ),
    _p(
        id="predict-jsg-this-in-timer",
        level=4,
        name="Whose this, inside the timer",
        family=GAME,
        language="javascript",
        code=(
            "class Player {\n"
            "  constructor() { this.ready = false; this.armed = false; }\n"
            "  spawn() {\n"
            "    setTimeout(function () { this.ready = true; }, 0);\n"
            "    setTimeout(() => { this.armed = true; }, 0);\n"
            "  }\n"
            "}\n"
            "const p = new Player();\n"
            "p.spawn();\n"
            "setTimeout(() => console.log(p.ready, p.armed), 10);"
        ),
        expect="false true",
        why=(
            "A `function` gets its `this` from how it is called, and "
            "setTimeout does not call it on the player. In Node it is "
            "called on the timer object, so `ready` was set on that and "
            "the player never hears about it — no error at all. An arrow "
            "function has no `this` of its own and uses the one from "
            "spawn, which is the player. Callbacks inside a class "
            "should be arrows."
        ),
    ),
)
