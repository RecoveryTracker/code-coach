"""Code magnets for game code, in JavaScript.

The shapes every small game is made of, one per puzzle: a loop that
runs a number of ticks, a clamp, movement scaled by the frame time, a
box-against-box collision test, wrap-around at the screen edge, a level
read out of strings, dead enemies filtered away, a Set of held keys, a
state machine in a table, sprite-sheet arithmetic, a class of entities
that update themselves, a fixed-step accumulator, and a loop driven by
a timer that keeps its `this`.

Two orderings matter more in game code than elsewhere. The state has to
exist before the loop that updates it — a `const` or a `class` used
above its line is a ReferenceError, not a different right answer — and
the update has to happen before the draw, or every frame shows where
things were a frame ago. Function declarations are hoisted, so a helper
can sit above or below the loop that calls it, and the marker, which
runs the program, accepts either.

Everything runs in plain Node, with console.log standing in for the
canvas. The expected output beside each was typed out by a person and
is held to what Node prints by tests/test_magnets_jsgame.py.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m

GAME = "Game code"


JS_GAME_MAGNETS: tuple[Magnet, ...] = (
    _m(
        id="magnet-jsg-tick-loop",
        plan=(
            ("Place the player and give it a speed", 2),
            ("Move the player one step", 3),
            ("Run three ticks and report each one", 4),
            ("Say the loop has finished", 1),
        ),
        level=1,
        name="A loop of three ticks",
        family=GAME,
        note=(
            "The smallest game loop: state that lives outside the loop, "
            "an update that changes it, and the loop that calls the "
            "update once per tick. The report goes after the update in "
            "the loop body — the other way round and every line shows "
            "where the player was a tick ago. `update` is a function "
            "declaration, so it can go above or below the loop."
        ),
        code=(
            "let x = 0;\n"
            "const speed = 2;\n"
            "function update() {\n"
            "  x += speed;\n"
            "}\n"
            "for (let tick = 1; tick <= 3; tick++) {\n"
            "  update();\n"
            '  console.log("tick", tick, "x", x);\n'
            "}\n"
            'console.log("done");'
        ),
        expect="tick 1 x 2\ntick 2 x 4\ntick 3 x 6\ndone",
    ),
    _m(
        id="magnet-jsg-clamp-health",
        plan=(
            ("Keep a number between two limits", 3),
            ("Start with some health and a maximum", 2),
            ("Heal past the top", 2),
            ("Take a hit past the bottom", 2),
        ),
        level=1,
        name="Health that stays in range",
        family=GAME,
        note=(
            "A clamp is Math.max against the floor inside Math.min "
            "against the ceiling. Every change to health goes through "
            "it, so a big heal stops at the maximum and a big hit stops "
            "at zero instead of going negative. The heal has to come "
            "before the hit — the hit is worked out from whatever the "
            "heal left behind."
        ),
        code=(
            "function clamp(v, lo, hi) {\n"
            "  return Math.min(hi, Math.max(lo, v));\n"
            "}\n"
            "let hp = 80;\n"
            "const MAX_HP = 100;\n"
            "hp = clamp(hp + 50, 0, MAX_HP);\n"
            'console.log("healed to", hp);\n'
            "hp = clamp(hp - 130, 0, MAX_HP);\n"
            'console.log("hit down to", hp);'
        ),
        expect="healed to 100\nhit down to 0",
    ),
    _m(
        id="magnet-jsg-velocity-dt",
        plan=(
            ("A ball with a position and a velocity", 1),
            ("Move anything by its velocity over time", 4),
            ("Four frames of a quarter second each", 4),
            ("Show where the ball ended up", 1),
        ),
        level=2,
        name="Moving by velocity times time",
        family=GAME,
        note=(
            "Velocity is units per second and dt is how many seconds "
            "the frame took, so velocity times dt is how far to go this "
            "frame. Four quarter-second frames make a second, and the "
            "ball ends one second's worth of velocity from where it "
            "started. `dt` is a const, so it has to be declared above "
            "the loop that reads it."
        ),
        code=(
            "const ball = { x: 0, y: 0, vx: 120, vy: -60 };\n"
            "function update(e, dt) {\n"
            "  e.x += e.vx * dt;\n"
            "  e.y += e.vy * dt;\n"
            "}\n"
            "const dt = 0.25;\n"
            "for (let f = 0; f < 4; f++) {\n"
            "  update(ball, dt);\n"
            "}\n"
            "console.log(ball.x, ball.y);"
        ),
        expect="120 -60",
    ),
    _m(
        id="magnet-jsg-aabb",
        plan=(
            ("Test two boxes for overlap", 4),
            ("A player and two coins", 2),
            ("Check each coin against the player", 3),
        ),
        level=2,
        name="Box against box",
        family=GAME,
        note=(
            "Axis-aligned boxes overlap when each one starts before the "
            "other ends, on both axes — four comparisons joined with &&. "
            "The return is split over two lines, and the && at the end "
            "of the first is what keeps it one expression. The player "
            "ends at x = 12 and the second coin starts there, so they "
            "touch without overlapping and it is missed."
        ),
        code=(
            "function overlaps(a, b) {\n"
            "  return a.x < b.x + b.w && a.x + a.w > b.x &&\n"
            "    a.y < b.y + b.h && a.y + a.h > b.y;\n"
            "}\n"
            "const player = { x: 4, y: 4, w: 8, h: 8 };\n"
            "const coins = [{ x: 10, y: 10, w: 4, h: 4 }, { x: 12, y: 0, w: 4, h: 4 }];\n"
            "for (const coin of coins) {\n"
            '  console.log(coin.x, overlaps(player, coin) ? "collected" : "missed");\n'
            "}"
        ),
        expect="10 collected\n12 missed",
    ),
    _m(
        id="magnet-jsg-wrap",
        plan=(
            ("The width of the screen", 1),
            ("Bring any position back onto the screen", 3),
            ("A starting place and three moves", 2),
            ("Make each move and wrap it", 4),
        ),
        level=2,
        name="Off one edge and on at the other",
        family=GAME,
        note=(
            "JavaScript's % keeps the sign of the left side, so -2 % 10 "
            "is -2 and a plain remainder would leave the ship off the "
            "left of the screen. Adding the width and taking the "
            "remainder again always lands in 0 to 9. Each move starts "
            "from where the last one wrapped to, which is why the order "
            "of the moves shows in the output."
        ),
        code=(
            "const WIDTH = 10;\n"
            "function wrap(x) {\n"
            "  return ((x % WIDTH) + WIDTH) % WIDTH;\n"
            "}\n"
            "let x = 1;\n"
            "const steps = [-3, -9, 15];\n"
            "for (const dx of steps) {\n"
            "  x = wrap(x + dx);\n"
            "  console.log(x);\n"
            "}"
        ),
        expect="8\n9\n4",
    ),
    _m(
        id="magnet-jsg-tile-map",
        plan=(
            ("A level drawn as strings", 1),
            ("Nothing found yet", 2),
            ("Visit every tile, row by row", 6),
            ("Report what the level holds", 1),
        ),
        level=2,
        name="Reading a level out of strings",
        family=GAME,
        note=(
            "A level typed as strings is a grid you can read with "
            "`rows[y][x]`: the outer loop picks the row, the inner one "
            "walks along it. y is outside and x inside because that is "
            "how the strings are laid out — each string is one row. The "
            "two closing braces differ only by indent, and the inner "
            "one has to close before the outer."
        ),
        code=(
            'const rows = ["#####", "#P.C#", "#####"];\n'
            "let player = null;\n"
            "let coins = 0;\n"
            "for (let y = 0; y < rows.length; y++) {\n"
            "  for (let x = 0; x < rows[y].length; x++) {\n"
            '    if (rows[y][x] === "P") player = { x, y };\n'
            '    if (rows[y][x] === "C") coins++;\n'
            "  }\n"
            "}\n"
            "console.log(player, coins);"
        ),
        expect="{ x: 1, y: 1 } 1",
    ),
    _m(
        id="magnet-jsg-filter-dead",
        plan=(
            ("Three enemies with some health", 1),
            ("Damage every enemy", 3),
            ("Hit them all and count", 2),
            ("Keep only the living and name them", 2),
        ),
        level=3,
        name="Clearing away the dead",
        family=GAME,
        note=(
            "filter builds a new array of the ones that pass and leaves "
            "the old one alone, so the result has to be assigned back — "
            "which is why the list is `let`. The count before the "
            "cleanup still includes the dead: they are only gone once "
            "the filter's result has replaced the list. Removing from an "
            "array while looping over it skips items; filtering after "
            "the loop never does."
        ),
        code=(
            'let enemies = [{ name: "bat", hp: 2 }, { name: "orc", hp: 5 }, { name: "imp", hp: 1 }];\n'
            "function hitAll(list, damage) {\n"
            "  for (const e of list) e.hp -= damage;\n"
            "}\n"
            "hitAll(enemies, 2);\n"
            'console.log("alive before cleanup:", enemies.length);\n'
            "enemies = enemies.filter((e) => e.hp > 0);\n"
            'console.log("alive after:", enemies.map((e) => e.name).join(", "));'
        ),
        expect="alive before cleanup: 3\nalive after: orc",
    ),
    _m(
        id="magnet-jsg-held-keys",
        plan=(
            ("Remember which keys are down", 1),
            ("Update that memory on every key event", 4),
            ("Work out a direction from it", 1),
            ("Press both arrows and look", 3),
            ("Let go of one and look again", 2),
        ),
        level=3,
        name="A Set of held keys",
        family=GAME,
        note=(
            "Games do not act on key events one at a time; they keep a "
            "Set of what is held and read it every frame. A Set ignores "
            "a repeated keydown, and subtracting two booleans gives -1, "
            "0 or 1. `dir` is an arrow stored in a const, so unlike a "
            "function declaration it does not exist until its line has "
            "run — it has to sit above the first call."
        ),
        code=(
            "const held = new Set();\n"
            "function onKey(type, key) {\n"
            '  if (type === "down") held.add(key);\n'
            "  else held.delete(key);\n"
            "}\n"
            'const dir = () => held.has("ArrowRight") - held.has("ArrowLeft");\n'
            'onKey("down", "ArrowLeft");\n'
            'onKey("down", "ArrowRight");\n'
            "console.log(dir(), held.size);\n"
            'onKey("up", "ArrowRight");\n'
            "console.log(dir(), held.size);"
        ),
        expect="0 2\n-1 1",
    ),
    _m(
        id="magnet-jsg-state-machine",
        plan=(
            ("Which events each state answers to", 4),
            ("Start standing still", 1),
            ("Move to the next state and say so", 4),
            ("Land, jump, then land", 3),
        ),
        level=3,
        name="A state machine in a table",
        family=GAME,
        note=(
            "Each state lists the events it responds to and where they "
            "lead. An event a state does not list looks up undefined, "
            "and `?? state` keeps the state where it was — landing while "
            "standing still does nothing, rather than needing its own "
            "if. The table and the starting state are consts and lets, "
            "so they go above the first event."
        ),
        code=(
            "const transitions = {\n"
            '  idle: { jump: "air" },\n'
            '  air: { land: "idle" },\n'
            "};\n"
            'let state = "idle";\n'
            "function send(event) {\n"
            "  state = transitions[state][event] ?? state;\n"
            '  console.log(event, "->", state);\n'
            "}\n"
            'send("land");\n'
            'send("jump");\n'
            'send("land");'
        ),
        expect="land -> idle\njump -> air\nland -> idle",
    ),
    _m(
        id="magnet-jsg-sprite-sheet",
        plan=(
            ("The shape of the sprite sheet", 2),
            ("Find a frame on the sheet", 5),
            ("Look up three frames", 3),
        ),
        level=3,
        name="Finding a frame on the sheet",
        family=GAME,
        note=(
            "A sprite sheet is a grid of frames read left to right, top "
            "to bottom. The remainder of the frame number by the column "
            "count is the column, and the floored quotient is the row — "
            "JavaScript's / never rounds, so the Math.floor is what "
            "makes frame 6 land in row 1 rather than row 1.5. Both "
            "sizes are consts and have to be declared first."
        ),
        code=(
            "const COLS = 4;\n"
            "const SIZE = 16;\n"
            "function frameRect(frame) {\n"
            "  const sx = (frame % COLS) * SIZE;\n"
            "  const sy = Math.floor(frame / COLS) * SIZE;\n"
            "  return `${sx},${sy}`;\n"
            "}\n"
            "for (const frame of [1, 4, 6]) {\n"
            "  console.log(frame, frameRect(frame));\n"
            "}"
        ),
        expect="1 16,0\n4 0,16\n6 32,16",
    ),
    _m(
        id="magnet-jsg-entity-class",
        plan=(
            ("Say what a ship holds", 6),
            ("Move a ship by its speed", 3),
            ("Close the class", 1),
            ("Build a fleet and step it once", 2),
        ),
        level=4,
        name="Entities that update themselves",
        family=GAME,
        note=(
            "Each kind of thing in the game is a class with its own "
            "update, and the loop only has to call update on each one. "
            "A class is not hoisted the way a function is: `new Ship` "
            "above the class is a ReferenceError, so the whole class — "
            "constructor, method and its closing brace — goes first. "
            "The constructor has to set speed before update can use it."
        ),
        code=(
            "class Ship {\n"
            "  constructor(name, speed) {\n"
            "    this.name = name;\n"
            "    this.x = 0;\n"
            "    this.speed = speed;\n"
            "  }\n"
            "  update(dt) {\n"
            "    this.x += this.speed * dt;\n"
            "  }\n"
            "}\n"
            'const fleet = [new Ship("red", 4), new Ship("blue", 6)];\n'
            "for (const s of fleet) { s.update(0.5); console.log(s.name, s.x); }"
        ),
        expect="red 2\nblue 3",
    ),
    _m(
        id="magnet-jsg-fixed-step",
        plan=(
            ("The step size and what is saved up", 3),
            ("Spend saved time a step at a time", 7),
            ("Three uneven frames, then the tally", 2),
        ),
        level=4,
        name="A fixed step from uneven frames",
        family=GAME,
        note=(
            "Physics that runs in fixed steps behaves the same on every "
            "machine. Each frame's time is added to an accumulator, and "
            "whole steps are taken out of it while there is enough; the "
            "remainder waits for the next frame. The subtraction goes "
            "inside the while — outside, the loop never ends — and the "
            "tally is printed after the frames have run."
        ),
        code=(
            "const STEP = 10;\n"
            "let acc = 0;\n"
            "let updates = 0;\n"
            "function frame(elapsed) {\n"
            "  acc += elapsed;\n"
            "  while (acc >= STEP) {\n"
            "    acc -= STEP;\n"
            "    updates++;\n"
            "  }\n"
            "}\n"
            "[16, 16, 3].forEach(frame);\n"
            "console.log(updates, acc);"
        ),
        expect="3 5",
    ),
    _m(
        id="magnet-jsg-timer-loop",
        plan=(
            ("A game that counts its frames", 2),
            ("Draw a frame, then ask for the next", 7),
            ("Close the class", 1),
            ("Start the game and carry on", 2),
        ),
        level=4,
        name="A loop that keeps its this",
        family=GAME,
        note=(
            "The loop is a function that queues itself with setTimeout. "
            "It is an arrow, so `this` inside it is still the game — a "
            "plain function would get the timer as its `this`. The first "
            "tick runs straight away and the rest are queued, which is "
            "why \"started\" lands between frame 1 and frame 2. The arrow "
            "is a const, so it has to be defined before `tick()` calls it."
        ),
        code=(
            "class Game {\n"
            "  frame = 0;\n"
            "  start() {\n"
            "    const tick = () => {\n"
            '      console.log("frame", ++this.frame);\n'
            "      if (this.frame < 3) setTimeout(tick, 0);\n"
            "    };\n"
            "    tick();\n"
            "  }\n"
            "}\n"
            "new Game().start();\n"
            'console.log("started");'
        ),
        expect="frame 1\nstarted\nframe 2\nframe 3",
    ),
)
