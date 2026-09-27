"""Pages 198-207: JavaScript, building a game.

The pieces a game written from scratch is made of, one per page: the state
object, the update loop, held keys, a state machine for the modes, an array
of entities, a spawn timer, a tile map, a seeded random generator, scoring
with combos, and classes for the things on screen. No canvas and no DOM:
each program is the part of the game that decides what happens, run in
plain node, printing what the screen would have shown.

Numbered after the game-math pages (188-197, content_jsgame), so this tuple
has to be registered after JSGAME_PAGES for the book to stay in order.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

JS_ONLY = ("javascript",)


def _page(page_id, number, name, teaches, example, shape, rows) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(
            Exercise(
                id=f"{page_id}-{i + 1:02d}",
                prompt=prompt,
                shape=shape,
                args=args,
            )
            for i, (prompt, args) in enumerate(rows)
        ),
        languages=JS_ONLY,
        tier="intermediate",
    )


def _and(words) -> str:
    words = list(words)
    return ", ".join(words[:-1]) + " and " + words[-1] if len(words) > 1 else words[0]


# ── 198. The game state object ───────────────────────────────

_STATES = (
    ("ana", 0, 3, 150, 1),
    ("bo", 200, 3, 50, 3),
    ("cal", 40, 5, 120, 2),
    ("dee", 0, 1, 10, 1),
    ("eli", 990, 2, 10, 0),
    ("fay", 75, 4, 25, 1),
    ("gus", 300, 2, 700, 2),
    ("hal", 0, 9, 1, 4),
    ("ivy", 1200, 3, 300, 1),
    ("jo", 5, 3, 5, 3),
    ("kai", 64, 6, 36, 5),
    ("lu", 0, 2, 1000, 1),
    ("max", 450, 1, 50, 0),
    ("ned", 18, 7, 82, 7),
    ("ola", 250, 3, 250, 2),
    ("pip", 9, 10, 91, 3),
    ("rio", 777, 3, 223, 3),
    ("sky", 30, 4, 70, 2),
    ("tam", 100, 2, 400, 1),
    ("uma", 1, 1, 99, 1),
)

STATE_PAGE = _page(
    "js-build-state", 198, "Building a game: one object holds the game",
    "A game is mostly bookkeeping: who the player is, how many points they "
    "have, how many lives are left. Keep all of it in one object, usually "
    "called state, and every other part of the game reads from it and "
    "writes to it. That is the whole trick — the screen is only a picture "
    "of this object. Change a field with += and -=, read it back with a "
    "dot, and a ternary (condition ? a : b) turns a number into a message. "
    "Later, saving the game is just saving this one object.",
    "const state = { player: \"ana\", score: 0, lives: 3 }; state.score += "
    "150; state.lives -= 1; then state.lives > 0 ? \"still playing\" : "
    "\"game over\" is \"still playing\"",
    "jsb_state",
    tuple(
        (f"Keep the game in one object with player {p}, score {s} and lives "
         f"{l}. Add {g} to the score and take {d} off the lives, then print "
         f"the player, the score and the lives as '{p}: 10 points, 2 "
         f"lives', and on the next line still playing, or game over if no "
         f"lives are left.",
         {"player": p, "score": s, "lives": l, "gain": g, "lost": d})
        for p, s, l, g, d in _STATES
    ),
)


# ── 199. A fixed-step update loop ────────────────────────────

_LOOPS = (
    ("move", 0, 3, 10, None),
    ("move", 2, 5, 4, None),
    ("move", 10, -2, 3, None),
    ("wrap", 0, 3, 10, 20),
    ("move", 100, 7, 6, None),
    ("wrap", 5, 4, 5, 16),
    ("move", -8, 2, 8, None),
    ("wrap", 18, 1, 5, 20),
    ("move", 0, 12, 12, None),
    ("wrap", 3, 7, 9, 32),
    ("move", 50, -5, 20, None),
    ("wrap", 0, 9, 7, 40),
    ("move", 1, 1, 60, None),
    ("wrap", 30, 6, 4, 32),
    ("move", 7, 3, 15, None),
    ("wrap", 0, 11, 11, 50),
    ("move", 64, -4, 16, None),
    ("wrap", 12, 5, 30, 64),
    ("move", 0, 9, 9, None),
    ("wrap", 9, 10, 3, 25),
)

LOOP_PAGE = _page(
    "js-build-loop", 199, "Building a game: the update loop",
    "A game is a loop: update the state a little, draw it, repeat. In a "
    "browser, requestAnimationFrame calls you about sixty times a second, "
    "and each call is one tick. Here a plain for loop stands in for it, so "
    "you can run a hundred ticks instantly and check where things ended "
    "up. Put the per-tick work in one function, update(s), that changes "
    "the state it is given and returns nothing; the loop only decides how "
    "many times to call it. Counting ticks in the state is a cheap way to "
    "know how long the game has run. A screen that wraps, where walking "
    "off the right edge brings you back on the left, is x = (x + speed) "
    "% width.",
    "function update(s) { s.x += s.speed; s.ticks += 1; } then for (let i "
    "= 0; i < 10; i++) update(state); moves x from 0 to 30 at speed 3",
    "jsb_loop",
    tuple(
        ((f"A state object starts with x {x}, speed {sp} and ticks 0. Write "
          f"an update function that adds the speed to x and counts one "
          f"tick, call it {n} times in a loop, then print it as after 5 "
          f"ticks x is 12."
          if want == "move" else
          f"A state object starts with x {x}, speed {sp} and ticks 0 on a "
          f"screen {w} wide. Write an update function that adds the speed "
          f"to x, wrapping back to the left edge by taking the remainder "
          f"by {w}, and counts one tick; call it {n} times in a loop, then "
          f"print it as after 5 ticks x is 12."),
         {"want": want, "x": x, "speed": sp, "ticks": n,
          **({"width": w} if w else {})})
        for want, x, sp, n, w in _LOOPS
    ),
)


# ── 200. Input as a set of held keys ─────────────────────────

_L, _R, _U, _D = "ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"
_INPUTS = (
    ((_R,), None, 5, 5, 1),
    ((_R, _U), None, 5, 5, 2),
    ((_L, _D), None, 10, 0, 3),
    ((_L, _R), None, 4, 4, 5),
    ((_U, _D, _R), None, 0, 0, 1),
    ((_R, _U), _U, 8, 8, 2),
    ((_L,), None, 3, 7, 4),
    ((_D, _L), _D, 20, 20, 5),
    ((_U,), None, 6, 6, 6),
    ((_L, _R, _U), _L, 0, 10, 2),
    ((_D,), None, 12, 1, 3),
    ((_U, _L), None, 15, 15, 10),
    ((_R, _D), _R, 2, 2, 7),
    ((_L, _U, _R, _D), None, 9, 9, 3),
    ((_R, _D), None, 0, 0, 8),
    ((_U, _R, _L), _R, 30, 30, 4),
    ((_D, _U), _U, 1, 1, 9),
    ((_L, _D), None, 50, 40, 10),
    ((_R,), None, -5, 3, 5),
    ((_U, _L, _D), _D, 7, 7, 1),
)

INPUT_PAGE = _page(
    "js-build-input", 200, "Building a game: held keys in a set",
    "Keyboard events arrive one at a time — keydown when a key goes down, "
    "keyup when it comes up — but a game wants to ask, every tick, which "
    "keys are held right now. So keydown adds the key's name to a Set and "
    "keyup deletes it, and the update reads the set with has. A set never "
    "holds the same key twice, however long it is held. Here the set is "
    "filled directly instead of by events. Screen y grows downwards, so "
    "ArrowUp subtracts from y. Holding left and right together cancels "
    "out, with no special case needed.",
    "const held = new Set([\"ArrowRight\"]); if "
    "(held.has(\"ArrowRight\")) player.x += 2; moves the player 2 to the "
    "right, and held.delete(\"ArrowRight\") is the key being let go",
    "jsb_input",
    tuple(
        (f"The held keys are {_and(held)}"
         + (f", and then {rel} is released" if rel else "")
         + f". Starting the player at x {x}, y {y}, move {step} left, "
         f"right, up or down for each arrow key still held, with up "
         f"making y smaller, then print the position as x 1, y 2.",
         {"held": held, "x": x, "y": y, "step": step,
          **({"release": rel} if rel else {})})
        for held, rel, x, y, step in _INPUTS
    ),
)


# ── 201. A state machine ─────────────────────────────────────

_EVENTS = (
    ("start", "pause", "resume", "die"),
    ("start", "die", "restart"),
    ("pause", "start", "pause", "quit"),
    ("start", "pause", "die", "resume", "die"),
    ("start", "start", "die", "start", "restart"),
    ("restart", "start", "pause", "pause", "resume"),
    ("start", "pause", "quit", "start", "die"),
    ("die", "start", "resume", "pause", "resume", "die"),
    ("start", "die", "resume", "restart", "start"),
    ("quit", "pause", "start", "quit", "pause"),
    ("start", "pause", "resume", "pause", "resume", "pause"),
    ("start", "die", "start", "pause", "restart", "start"),
    ("resume", "start", "resume"),
    ("start", "pause", "quit", "quit", "start", "pause"),
    ("start", "die", "die", "restart", "restart"),
    ("pause", "die", "start", "restart", "die"),
    ("start", "resume", "pause", "start", "quit"),
    ("start", "pause", "resume", "die", "restart", "start", "die"),
    ("restart", "quit", "resume", "start"),
    ("start", "quit", "die", "restart", "start", "pause"),
)

FSM_PAGE = _page(
    "js-build-fsm", 201, "Building a game: menus, pausing and game over",
    "A game is always in one mode — on the menu, playing, paused, or game "
    "over — and each mode reacts to different things: pressing start on "
    "the menu begins a game, pressing it while playing does nothing. "
    "Instead of a tangle of ifs, write the rules as a table: an object "
    "whose keys are modes, and inside each, which event leads to which "
    "mode. Then one line runs the whole machine: next[mode][event] is the "
    "new mode, or undefined if that event means nothing here, and ?? mode "
    "keeps the old one. The table used on this page: menu goes to playing "
    "on start; playing goes to paused on pause and to gameover on die; "
    "paused goes to playing on resume and to menu on quit; gameover goes "
    "to menu on restart.",
    "const next = { menu: { start: \"playing\" }, playing: { pause: "
    "\"paused\", die: \"gameover\" }, ... }; mode = next[mode][event] ?? "
    "mode; turns menu into playing on start and leaves it on menu for pause",
    "jsb_fsm",
    tuple(
        (f"Using the menu, playing, paused and gameover table, start in menu "
         f"and apply the events {_and(events)} in that order, printing the "
         f"mode after each one. An event the current mode has no rule for "
         f"leaves the mode as it was.",
         {"events": events})
        for events in _EVENTS
    ),
)


# ── 202. Entities in an array ────────────────────────────────

_ENTITIES = (
    ("enemies", 2, (("bat", 3), ("rat", 1), ("orc", 5))),
    ("enemies", 3, (("imp", 3), ("ogre", 10), ("slug", 2), ("wolf", 4))),
    ("bullets", 1, (("b1", 1), ("b2", 3), ("b3", 1), ("b4", 2))),
    ("asteroids", 4, (("big", 9), ("mid", 4), ("small", 2), ("huge", 12))),
    ("slimes", 1, (("red", 2), ("blue", 1), ("green", 1), ("gold", 3))),
    ("zombies", 5, (("zed", 6), ("zack", 5), ("zoe", 11), ("zia", 3), ("zog", 7))),
    ("enemies", 10, (("boss", 50), ("minion", 10), ("guard", 15))),
    ("ghosts", 2, (("boo", 2), ("wisp", 1), ("shade", 4), ("spook", 3))),
    ("bullets", 2, (("left", 2), ("right", 5), ("up", 1))),
    ("enemies", 6, (("crab", 7), ("eel", 6), ("shark", 20), ("squid", 5))),
    ("asteroids", 3, (("a1", 3), ("a2", 8), ("a3", 4), ("a4", 1), ("a5", 9))),
    ("slimes", 2, (("tiny", 1), ("small", 2), ("big", 8))),
    ("zombies", 1, (("walker", 2), ("crawler", 1), ("runner", 1), ("brute", 9))),
    ("ghosts", 7, (("poltergeist", 14), ("phantom", 7), ("specter", 8))),
    ("enemies", 4, (("goblin", 4), ("troll", 12), ("kobold", 3), ("dragon", 40))),
    ("bullets", 3, (("fast", 1), ("slow", 6), ("heavy", 9), ("light", 2))),
    ("asteroids", 5, (("rock", 5), ("comet", 6), ("dust", 1), ("moon", 30))),
    ("slimes", 3, (("jelly", 4), ("goo", 3), ("ooze", 7), ("blob", 2), ("drip", 5))),
    ("zombies", 8, (("mort", 8), ("rot", 9), ("gore", 16))),
    ("enemies", 1, (("fly", 1), ("ant", 2), ("bee", 1), ("wasp", 3), ("moth", 1))),
)

ENTITIES_PAGE = _page(
    "js-build-entities", 202, "Building a game: an array of entities",
    "Everything that moves or can be hit — enemies, bullets, coins — is an "
    "entity, a small object, and they all live in one array. Every tick "
    "the game walks the array and updates each one; for...of hands you the "
    "real object, so changing e.hp changes the one in the array. Then the "
    "dead ones have to go. Removing items from an array while looping over "
    "it skips things, so instead filter builds a new array of only the "
    "ones that are still alive, and the game carries on with that. The "
    "difference in length is how many were removed.",
    "for (const e of enemies) e.hp -= 2; const alive = enemies.filter((e) "
    "=> e.hp > 0); keeps an enemy with hp 3 and drops one with hp 1",
    "jsb_entities",
    tuple(
        (f"Given {v} "
         + ", ".join(f"{n} (hp {hp})" for n, hp in items)
         + f", take {d} hp off every one, keep only those with hp above "
         f"zero, print their names separated by commas, then print how many "
         f"were removed followed by the word removed.",
         {"var": v, "damage": d, "items": items})
        for v, d, items in _ENTITIES
    ),
)


# ── 203. Spawning with a timer ───────────────────────────────

_SPAWNS = (
    (16, 500, 120),
    (16, 1000, 200),
    (20, 300, 50),
    (33, 1000, 100),
    (10, 250, 101),
    (16, 400, 60),
    (25, 200, 30),
    (40, 600, 45),
    (17, 1000, 180),
    (50, 750, 40),
    (16, 2000, 300),
    (12, 100, 26),
    (30, 450, 61),
    (20, 1500, 240),
    (8, 64, 33),
    (16, 800, 129),
    (45, 900, 70),
    (33, 500, 91),
    (11, 330, 95),
    (60, 1000, 55),
)

SPAWN_PAGE = _page(
    "js-build-spawn", 203, "Building a game: spawning on a timer",
    "Every frame the game is told how much time passed since the last "
    "one, dt, short for delta time. To spawn an enemy every half second, "
    "add dt to a timer each frame and, when the timer reaches 500, spawn "
    "and subtract 500. Subtract, rather than setting the timer back to "
    "zero: the few milliseconds past 500 belong to the next wait, and "
    "throwing them away makes spawns slowly drift late. Time is counted in "
    "whole milliseconds here, because adding 0.1 seconds ten times does "
    "not quite make 1 in floating point.",
    "timer += dt; if (timer >= 500) { timer -= 500; spawned += 1; } with "
    "dt 16 spawns on frame 32, with 12 ms already counted toward the next",
    "jsb_spawn",
    tuple(
        (f"Frames are {dt} ms apart. Run {frames} frames, and whenever the "
         f"timer reaches {every} ms, spawn one enemy and take {every} off "
         f"the timer. Then print how many spawned and how many ms are left "
         f"over, as 2 spawned, 40 ms left over.",
         {"dt": dt, "every": every, "frames": frames})
        for dt, every, frames in _SPAWNS
    ),
)


# ── 204. A tile map as strings ───────────────────────────────

_MAPS = (
    (("#####", "#.@.#", "#####"), (1, 1)),
    (("######", "#@...#", "#.##.#", "######"), (2, 2)),
    (("#####", "#...#", "#.#.#", "#..@#", "#####"), (2, 2)),
    (("#######", "#..$..#", "#.@...#", "#######"), (3, 1)),
    (("####", "#@.#", "#..#", "####"), (0, 0)),
    (("########", "#......#", "#.####.#", "#.....@#", "########"), (1, 2)),
    (("#####", "#$#@#", "#...#", "#####"), (2, 1)),
    (("######", "#....#", "#.#..#", "#..#@#", "######"), (3, 3)),
    (("#####", "##@##", "#...#", "#####"), (1, 1)),
    (("#######", "#.....#", "#.###.#", "#.#@#.#", "#.....#", "#######"), (3, 2)),
    (("#####", "#..$#", "#.#.#", "#@..#", "#####"), (3, 1)),
    (("######", "#.#..#", "#.#.@#", "#....#", "######"), (2, 1)),
    (("#####", "#@#.#", "#.#.#", "#...#", "#####"), (3, 1)),
    (("####", "#..#", "#.@#", "####"), (3, 2)),
    (("########", "#@.....#", "########"), (7, 1)),
    (("#####", "#...#", "#.@.#", "#...#", "#####"), (2, 3)),
    (("######", "#$..$#", "#.##.#", "#..@.#", "######"), (4, 1)),
    (("###", "#@#", "#.#", "###"), (1, 2)),
    (("#######", "#.#.#.#", "#.....#", "#.#@#.#", "#######"), (2, 1)),
    (("######", "##..##", "#..@.#", "##..##", "######"), (1, 1)),
)

TILES_PAGE = _page(
    "js-build-tiles", 204, "Building a game: a tile map as strings",
    "Many games are built on a grid, and the easiest way to draw one "
    "while you write it is as text: an array of strings, one per row, one "
    "character per tile. Here # is a wall, . is floor, $ is a coin and @ "
    "is the player. map[row][col] is one tile — row first, because the "
    "array is a list of rows — and a string can be indexed like an array. "
    "findIndex finds the row the player is on and indexOf finds the "
    "column inside it. A tile is walkable when it is not a wall, which is "
    "the question collision asks before every move.",
    "with const map = [\"#####\", \"#.@.#\", \"#####\"], map.findIndex((line) "
    "=> line.includes(\"@\")) is row 1, map[1].indexOf(\"@\") is column 2, "
    "and map[1][1] !== \"#\" is true",
    "jsb_tiles",
    tuple(
        (f"The map rows are "
         + ", ".join(f"'{r}'" for r in rows)
         + f", where # is a wall. Print the player's position as player at "
         f"column 1, row 2, then how many walls there are, then true or "
         f"false for whether the tile at column {c}, row {r} is not a wall.",
         {"rows": rows, "check": (c, r)})
        for rows, (c, r) in _MAPS
    ),
)


# ── 205. A seeded random generator ───────────────────────────

_RNGS = (
    ("dice", 42, 5, 6, None, None),
    ("dice", 1, 6, 6, None, None),
    ("pick", 7, 5, None, "tiles", ("grass", "rock", "water")),
    ("dice", 2024, 4, 20, None, None),
    ("pick", 99, 4, None, "enemies", ("bat", "rat", "orc", "imp")),
    ("dice", 12345, 8, 4, None, None),
    ("pick", 3, 6, None, "loot", ("coin", "gem", "key")),
    ("dice", 777, 5, 10, None, None),
    ("pick", 2025, 5, None, "rooms", ("hall", "cave", "vault", "shop", "pit")),
    ("dice", 31337, 6, 2, None, None),
    ("pick", 500, 4, None, "colors", ("red", "green", "blue")),
    ("dice", 8, 7, 8, None, None),
    ("pick", 123, 6, None, "tiles", ("sand", "tree", "wall", "door")),
    ("dice", 65536, 5, 12, None, None),
    ("pick", 4242, 5, None, "weather", ("sun", "rain", "fog", "snow")),
    ("dice", 1000, 6, 100, None, None),
    ("pick", 11, 4, None, "enemies", ("slime", "ghost")),
    ("dice", 424242, 5, 6, None, None),
    ("pick", 60, 5, None, "loot", ("sword", "shield", "potion", "arrow", "bomb")),
    ("dice", 9001, 4, 3, None, None),
)

RNG_PAGE = _page(
    "js-build-rng", 205, "Building a game: random numbers that repeat",
    "Math.random gives different numbers every run, which makes a bug "
    "that only shows up on one level impossible to see twice. A seeded "
    "generator fixes that: it is a tiny formula that turns the last "
    "number into the next, so starting from the same seed always gives "
    "the same sequence — the same level, the same drops — and sharing the "
    "seed shares the level. This page uses Park-Miller, one of the "
    "oldest: seed = seed * 16807 % 2147483647. Its products stay small "
    "enough for a JavaScript number to hold exactly. To roll a die, take "
    "the remainder by the number of sides and add one; to pick from a "
    "list, use the remainder by its length as the index.",
    "let seed = 42; function next() { seed = (seed * 16807) % 2147483647; "
    "return seed; } then (next() % 6) + 1 is 1, and the next four rolls "
    "are 2, 6, 6 and 3 — every time",
    "jsb_rng",
    tuple(
        ((f"Using the generator seed = seed * 16807 % 2147483647 starting "
          f"from seed {seed}, roll {n} dice with {sides} sides, each the "
          f"next value's remainder by {sides} plus one, and print the "
          f"rolls separated by spaces."
          if want == "dice" else
          f"Using the generator seed = seed * 16807 % 2147483647 starting "
          f"from seed {seed}, pick {n} {v} from {_and(choices)}, each "
          f"using the next value's remainder by the list's length as the "
          f"index, and print the picks separated by spaces."),
         {"want": want, "seed": seed, "count": n,
          **({"sides": sides} if want == "dice" else
             {"var": v, "choices": choices})})
        for want, seed, n, sides, v, choices in _RNGS
    ),
)


# ── 206. Score, high score and combos ────────────────────────

_COMBOS = (
    ("hhxhhh", 10, 4, 100),
    ("hhhhhh", 10, 4, 500),
    ("hxhxhx", 5, 3, 10),
    ("hhhxhh", 20, 2, 150),
    ("xxhhh", 50, 5, 200),
    ("hhhhhhhh", 1, 3, 20),
    ("hhxxhhhx", 10, 5, 90),
    ("hhhhh", 100, 10, 1000),
    ("xhhhhx", 25, 2, 100),
    ("hhhxhhhxhhh", 10, 3, 200),
    ("hxhhxhhh", 15, 4, 50),
    ("hhhhhhhhhh", 5, 4, 180),
    ("xxxh", 30, 3, 40),
    ("hhxhhxhhxhh", 10, 2, 400),
    ("hhhhxhhhh", 20, 5, 300),
    ("hhhhhhx", 7, 6, 150),
    ("hxxhhhhh", 12, 3, 100),
    ("hhhhhhhhhhhh", 2, 8, 100),
    ("hhxhhhhhx", 40, 4, 1000),
    ("hhhxhhhhhh", 10, 4, 180),
)

_SHOT_WORDS = {"h": "hit", "x": "miss"}

COMBO_PAGE = _page(
    "js-build-combo", 206, "Building a game: score, combos and high score",
    "Scoring rewards doing well several times in a row. A combo counts "
    "hits in a row: each hit adds one, and a miss sets it back to zero. "
    "Each hit scores its points times the combo, so the third hit in a row "
    "is worth three times the first — but capped with Math.min, or a long "
    "streak breaks the game. A miss scores nothing, which falls out on its "
    "own: the combo is zero, and anything times zero is zero. The high "
    "score is whichever is bigger, this game's score or the old best, "
    "which is Math.max.",
    "for hit, hit, miss, hit at 10 points capped at 4: combo goes 1, 2, "
    "0, 1 and score goes 10, 30, 30, 40; then Math.max(40, 100) keeps the "
    "old high score of 100",
    "jsb_combo",
    tuple(
        (f"The shots go {', '.join(_SHOT_WORDS[s] for s in shots)}. Each hit "
         f"raises the combo by one and scores {pts} times the combo, with "
         f"the multiplier capped at {cap}; a miss resets the combo to zero. "
         f"Print the score and the high score, which was {high} before this "
         f"game, as score 40, high score 100.",
         {"shots": shots, "points": pts, "cap": cap, "high": high})
        for shots, pts, cap, high in _COMBOS
    ),
)


# ── 207. Classes for game objects ────────────────────────────

_P, _E, _N = "Player", "Enemy", "Entity"
_CLASSES = (
    (2, 1, 3, ((_P, "hero", 0), (_E, "bat", 9), (_N, "rock", 5))),
    (1, 1, 5, ((_P, "ana", 0), (_E, "orc", 10))),
    (3, 2, 4, ((_E, "rat", 20), (_P, "bo", 2), (_N, "tree", 7))),
    (5, 1, 2, ((_P, "kid", 10), (_E, "imp", 12), (_E, "elf", 30))),
    (1, 3, 6, ((_N, "sign", 4), (_P, "cy", 0), (_E, "ghost", 25))),
    (4, 4, 3, ((_P, "max", -5), (_E, "wolf", 15), (_N, "bush", 0))),
    (2, 5, 2, ((_E, "shark", 40), (_E, "eel", 10), (_P, "diver", 0))),
    (7, 2, 4, ((_P, "racer", 0), (_N, "cone", 14), (_E, "cop", 50))),
    (1, 1, 10, ((_P, "snail", 0), (_E, "bird", 8), (_N, "leaf", 3))),
    (3, 3, 5, ((_P, "link", 1), (_E, "moblin", 30), (_E, "keese", 16), (_N, "pot", 9))),
    (6, 2, 3, ((_P, "sonic", 0), (_E, "crab", 20), (_N, "ring", 5))),
    (2, 7, 2, ((_E, "rocket", 40), (_P, "pilot", 3), (_N, "cloud", 11))),
    (10, 5, 1, ((_P, "dash", 0), (_E, "slow", 5))),
    (1, 2, 7, ((_N, "wall", 0), (_P, "ant", 2), (_E, "beetle", 30))),
    (4, 1, 6, ((_P, "mario", 0), (_E, "goomba", 20), (_E, "koopa", 35), (_N, "pipe", 12))),
    (2, 2, 8, ((_P, "fox", 5), (_E, "hound", 40), (_N, "fence", 20))),
    (3, 6, 2, ((_E, "arrow", 18), (_P, "archer", 0), (_N, "target", 30))),
    (8, 3, 3, ((_P, "jet", 0), (_E, "drone", 60), (_N, "tower", 25))),
    (1, 4, 4, ((_P, "tank", 0), (_E, "mine", 12), (_N, "crate", 6))),
    (5, 5, 5, ((_P, "red", 0), (_E, "blue", 50), (_N, "flag", 25))),
)

CLASSES_PAGE = _page(
    "js-build-classes", 207, "Building a game: classes for game objects",
    "Once there are several kinds of thing on screen, a class keeps each "
    "kind's data and behaviour together. Entity is the base: every entity "
    "has a name and an x, set in the constructor, and an update that does "
    "nothing. Player extends Entity and overrides update to move right; "
    "Enemy extends it and overrides update to move left. The game loop "
    "does not care which is which — it calls e.update() on everything in "
    "the array, and each object runs its own version. That is the whole "
    "idea: adding a new kind of thing means a new class, not a new if in "
    "the loop.",
    "class Player extends Entity { update() { this.x += 2; } } — then new "
    "Player(\"hero\", 0) is at x 6 after three updates, while a plain new "
    "Entity(\"rock\", 5) stays at 5",
    "jsb_classes",
    tuple(
        (f"Write a class Entity with a name, an x and an update that does "
         f"nothing, a Player whose update moves {run} right, and an Enemy "
         f"whose update moves {chase} left. Make "
         + _and(f"{kind} {name} at {x}" for kind, name, x in world)
         + f", update them all {ticks} times, and print each name and x "
         f"separated by commas, as ana 5, orc 8.",
         {"run": run, "chase": chase, "ticks": ticks, "world": world})
        for run, chase, ticks, world in _CLASSES
    ),
)


JSBUILD_PAGES: tuple[Page, ...] = (
    STATE_PAGE,
    LOOP_PAGE,
    INPUT_PAGE,
    FSM_PAGE,
    ENTITIES_PAGE,
    SPAWN_PAGE,
    TILES_PAGE,
    RNG_PAGE,
    COMBO_PAGE,
    CLASSES_PAGE,
)
