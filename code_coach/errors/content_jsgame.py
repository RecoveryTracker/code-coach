"""JavaScript crashes from game code.

The same rules as `content.py`: every message and line was copied from
what Node printed through `engine_report`, and
tests/test_errors_jsgame.py holds them to it. They get a family of
their own, because they are the crashes a game meets and a web form
does not — a tile loop that runs one row past the map, a grid written
to outside its bounds, a Set treated like an array, an entity removed
from the list the loop is still walking, `this` lost inside a timer
or a method handed over as a callback, a flood fill with no memory of
where it has been, and requestAnimationFrame asked for where there is
no browser to supply it.
"""

from __future__ import annotations

from code_coach.errors import Crash, _c

GAME = "Game code"


JS_GAME_CRASHES: tuple[Crash, ...] = (
    _c(
        id="err-jsg-no-animation-frame",
        level=1,
        name="A browser loop run outside the browser",
        family=GAME,
        code=(
            "let frame = 0;\n"
            "function loop() {\n"
            "  frame++;\n"
            "  requestAnimationFrame(loop);\n"
            "}\n"
            "loop();"
        ),
        message="ReferenceError: requestAnimationFrame is not defined",
        line=4,
        meaning="Nothing called requestAnimationFrame exists here",
        decoys=(
            "loop is not defined yet when requestAnimationFrame is called",
            "requestAnimationFrame needs a number of milliseconds as well",
            "frame is not defined inside the function",
        ),
        fix=(
            "requestAnimationFrame is part of the browser, not of "
            "JavaScript: a page gets it from `window`, and Node, which "
            "has no screen to draw on, does not have it at all. The "
            "message names the one missing thing. Keep the game's logic "
            "in functions that take a dt and can run anywhere, and let "
            "only the browser's start-up code call "
            "requestAnimationFrame — or use setTimeout(loop, 16) when "
            "running it in Node."
        ),
    ),
    _c(
        id="err-jsg-row-past-the-map",
        level=1,
        name="One row more than the map has",
        family=GAME,
        code=(
            'const map = ["..#", "#.."];\n'
            "let walls = 0;\n"
            "for (let y = 0; y <= map.length; y++) {\n"
            "  for (const ch of map[y]) {\n"
            '    if (ch === "#") walls++;\n'
            "  }\n"
            "}\n"
            "console.log(walls);"
        ),
        message="TypeError: map[y] is not iterable",
        line=4,
        meaning="map[y] was undefined, and for...of cannot walk it",
        decoys=(
            "A string cannot be looped over with for...of, only an array can",
            "walls is a const and cannot be added to",
            "The map has a row with no walls in it",
        ),
        fix=(
            "The map has two rows, 0 and 1, and `y <= map.length` also "
            "runs y = 2. map[2] is undefined, and for...of can walk a "
            "string or an array but not undefined — so the message "
            "names the expression that turned up empty, on the line "
            "that tried to walk it. The real mistake is a line above, in "
            "the loop header: `y < map.length`."
        ),
    ),
    _c(
        id="err-jsg-player-not-made-yet",
        level=2,
        name="Updating the player before it exists",
        family=GAME,
        code=(
            "function update() {\n"
            "  player.x += 1;\n"
            "}\n"
            "update();\n"
            "const player = { x: 0, y: 0 };\n"
            "console.log(player.x);"
        ),
        message="ReferenceError: Cannot access 'player' before initialization",
        line=2,
        meaning="player is declared, but its line had not run yet",
        decoys=(
            "player has no property called x",
            "update cannot be called before it is defined",
            "A const object's properties cannot be changed",
        ),
        fix=(
            "The name player exists for the whole file — that is why it "
            "is not 'is not defined' — but a const cannot be touched "
            "until its line has run, and the first update ran on line 4, "
            "before line 5. The message blames the line that reached for "
            "it. Create the game's state first, then start the loop; "
            "starting a loop is the last thing a game's setup does."
        ),
    ),
    _c(
        id="err-jsg-grid-out-of-bounds",
        level=2,
        name="Writing to a tile below the grid",
        family=GAME,
        code=(
            "const grid = [\n"
            '  [".", "."],\n'
            '  [".", "."],\n'
            "];\n"
            "const px = 1, py = 2;\n"
            'grid[py][px] = "@";\n'
            "console.log(grid[py][px]);"
        ),
        message="TypeError: Cannot set properties of undefined (setting '1')",
        line=6,
        meaning="grid[py] was undefined: there is no row 2",
        decoys=(
            "Column 1 is past the end of the row",
            "A const array cannot have its items changed",
            "The @ is a string and the grid holds numbers",
        ),
        fix=(
            "'setting '1'' is the column: something was asked to take a "
            "value at index 1, and that something was undefined. The "
            "grid has rows 0 and 1, so grid[2] is undefined before the "
            "[px] is ever reached. Check both coordinates against the "
            "grid before writing — `py >= 0 && py < grid.length` for "
            "the row, then the same for the column against that row."
        ),
    ),
    _c(
        id="err-jsg-set-has-no-map",
        level=2,
        name="Mapping over the held keys",
        family=GAME,
        code=(
            'const held = new Set(["a", "d"]);\n'
            "const names = held.map((k) => k.toUpperCase());\n"
            "console.log(names);"
        ),
        message="TypeError: held.map is not a function",
        line=2,
        meaning="A Set has no map method; only arrays do",
        decoys=(
            "toUpperCase does not exist on single letters",
            "The Set was empty, so there was nothing to map",
            "held is const, so it cannot be mapped over",
        ),
        fix=(
            "A Set is the right thing to keep held keys in, but it is "
            "not an array: it has add, has, delete, size and forEach, "
            "and none of map, filter or indexOf. 'x.map is not a "
            "function' means x is not an array. Spread it into one "
            "first — `[...held].map(...)` — or use Array.from(held, fn)."
        ),
    ),
    _c(
        id="err-jsg-splice-counted-length",
        level=3,
        name="Removing enemies from a counted loop",
        family=GAME,
        code=(
            "const enemies = [{ hp: 0 }, { hp: 5 }, { hp: 0 }];\n"
            "const count = enemies.length;\n"
            "for (let i = 0; i < count; i++) {\n"
            "  if (enemies[i].hp <= 0) enemies.splice(i, 1);\n"
            "}\n"
            "console.log(enemies.length);"
        ),
        message="TypeError: Cannot read properties of undefined (reading 'hp')",
        line=4,
        meaning="enemies[i] was undefined: the index ran past the shortened array",
        decoys=(
            "One of the enemies was created without an hp",
            "splice cannot be called on a const array",
            "An hp of 0 counts as undefined when compared with <= in JavaScript",
        ),
        fix=(
            "The loop counted three enemies before it started, but two "
            "splices shrank the array to one, so by i = 2 there is no "
            "enemy there and reading its hp throws. Removing from an "
            "array while walking it forwards also skips the item after "
            "each removal. Filter instead — `enemies = enemies.filter(e "
            "=> e.hp > 0)` — or walk backwards from the end."
        ),
    ),
    _c(
        id="err-jsg-this-in-timer",
        level=3,
        name="A timer that lost the enemy",
        family=GAME,
        code=(
            "class Enemy {\n"
            "  constructor() {\n"
            "    this.pos = { x: 0, y: 0 };\n"
            "  }\n"
            "  start() {\n"
            "    setTimeout(function () { this.pos.x += 1; }, 0);\n"
            "  }\n"
            "}\n"
            "new Enemy().start();"
        ),
        message="TypeError: Cannot read properties of undefined (reading 'x')",
        line=6,
        meaning="this.pos was undefined, because this was not the enemy",
        decoys=(
            "The enemy's pos has no x property",
            "setTimeout was given 0 and never ran the callback",
            "The constructor had not finished when start was called",
        ),
        fix=(
            "It was reading 'x', so the thing before .x — this.pos — "
            "was undefined. The constructor did set pos, so `this` "
            "cannot be the enemy: a plain `function` passed to "
            "setTimeout is called by the timer, and its `this` is "
            "whatever the timer makes it. Use an arrow — `setTimeout(() "
            "=> { this.pos.x += 1; }, 0)` — which keeps the `this` of "
            "the method around it."
        ),
    ),
    _c(
        id="err-jsg-method-as-callback",
        level=4,
        name="A method handed to the timer",
        family=GAME,
        code=(
            "class Game {\n"
            "  constructor() { this.frame = 0; }\n"
            "  update() { this.frame++; }\n"
            "  tick() { this.update(); }\n"
            "  run() { setTimeout(this.tick, 0); }\n"
            "}\n"
            "new Game().run();"
        ),
        message="TypeError: this.update is not a function",
        line=4,
        meaning="tick ran with a this that was not the game",
        decoys=(
            "update is defined after tick, so tick cannot see it",
            "update needs to be marked static to be called",
            "run should have called tick with brackets",
        ),
        fix=(
            "`this.tick` hands setTimeout the function on its own, "
            "without the game it came from, and when the timer calls it "
            "`this` is the timer. The timer has no update, so the "
            "message blames line 4, inside tick, though the mistake is "
            "on line 5. Pass an arrow that calls the method on the "
            "game — `setTimeout(() => this.tick(), 0)` — or bind it "
            "once in the constructor."
        ),
    ),
    _c(
        id="err-jsg-flood-fill-forever",
        level=4,
        name="A flood fill with no memory",
        family=GAME,
        code=(
            'const map = ["...", "...", "..."];\n'
            "function fill(x, y) {\n"
            "  if (y < 0 || y >= map.length || x < 0 || x >= map[y].length) return 0;\n"
            "  return 1 + fill(x + 1, y) + fill(x - 1, y) + fill(x, y + 1) + fill(x, y - 1);\n"
            "}\n"
            "console.log(fill(1, 1));"
        ),
        message="RangeError: Maximum call stack size exceeded",
        line=2,
        meaning="fill kept calling itself and never got back out",
        decoys=(
            "The map is too big to fill",
            "The bounds check lets a tile outside the map through",
            "A function cannot call itself four times in one line",
        ),
        fix=(
            "Every call adds a frame to the stack until it returns, and "
            "these never do: stepping right and then left comes back to "
            "the same tile, which steps right again, forever. The line "
            "blamed is the function itself, because the stack ran out "
            "on the way into yet another call. A flood fill has to "
            "remember where it has been — a Set of \"x,y\" strings, "
            "checked first — so that each tile is filled once."
        ),
    ),
)
