"""JavaScript: building a game.

A game written from scratch is a handful of small structures, over and over:
one object holding the state, a loop that updates it a tick at a time, a set
of held keys, a table of which mode leads to which, an array of entities
that are updated and culled, a timer, a map, a random number generator that
can be replayed, a score, and classes for the things on screen. None of it
needs a browser to practise, so every program here runs in plain node and
prints what the game would have drawn.

Everything is whole numbers on purpose. Game time is counted in milliseconds
rather than seconds, because adding 0.1 ten times does not make 1, and a
page about spawn timers is not the place to meet that.

Nothing prints a bare array or object. Node renders those as `[ 1, 2 ]` and
`{ a: 1 }`, spaces and all, and these answers are compared as text.
"""

from __future__ import annotations

from code_coach.workbook.complexity import Cost
from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("jsb_state", "one object holding the whole game"),
    Shape("jsb_loop", "a fixed-step update loop"),
    Shape("jsb_input", "movement from a set of held keys"),
    Shape("jsb_fsm", "game modes as a table of transitions"),
    Shape("jsb_entities", "updating every entity, removing the dead"),
    Shape("jsb_spawn", "a spawn timer that counts milliseconds"),
    Shape("jsb_tiles", "a tile map written as strings"),
    Shape("jsb_rng", "a seeded random generator that repeats"),
    Shape("jsb_combo", "score, combo multiplier and high score"),
    Shape("jsb_classes", "game objects as classes that override update"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)

#: The transition table every state-machine exercise types out.
MODES: dict[str, dict[str, str]] = {
    "menu": {"start": "playing"},
    "playing": {"pause": "paused", "die": "gameover"},
    "paused": {"resume": "playing", "quit": "menu"},
    "gameover": {"restart": "menu"},
}

#: Arrow keys and which way each one moves, as (dx, dy). Screen y grows
#: downwards, so up is minus.
ARROWS: dict[str, tuple[int, int]] = {
    "ArrowLeft": (-1, 0),
    "ArrowRight": (1, 0),
    "ArrowUp": (0, -1),
    "ArrowDown": (0, 1),
}

#: Park-Miller: small enough that seed * 16807 stays below 2**53, so a
#: JavaScript number holds every product exactly.
MODULUS = 2147483647
MULTIPLIER = 16807


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── Rendering values ─────────────────────────────────────────


def _int(x) -> str:
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f"{x!r}: whole numbers only on these pages")
    return str(x)


def _str(s: str) -> str:
    if not isinstance(s, str) or '"' in s or "\\" in s or "`" in s or "${" in s:
        raise ValueError(f"{s!r}: keep strings plain")
    return f'"{s}"'


def _item_var(var: str) -> str:
    return var[0]


# ── 1. The state object ──────────────────────────────────────


def _state(a: dict) -> str:
    return _lines(
        f"const state = {{ player: {_str(a['player'])}, "
        f"score: {_int(a['score'])}, lives: {_int(a['lives'])} }};",
        f"state.score += {_int(a['gain'])};",
        f"state.lives -= {_int(a['lost'])};",
        "console.log(`${state.player}: ${state.score} points, "
        "${state.lives} lives`);",
        'console.log(state.lives > 0 ? "still playing" : "game over");',
    )


# ── 2. The update loop ───────────────────────────────────────


def _loop(a: dict) -> str:
    if a["want"] == "wrap":
        step = f"  s.x = (s.x + s.speed) % {_int(a['width'])};"
    else:
        step = "  s.x += s.speed;"
    return _lines(
        f"const state = {{ x: {_int(a['x'])}, speed: {_int(a['speed'])}, "
        "ticks: 0 };",
        "function update(s) {",
        step,
        "  s.ticks += 1;",
        "}",
        f"for (let i = 0; i < {_int(a['ticks'])}; i++) update(state);",
        "console.log(`after ${state.ticks} ticks x is ${state.x}`);",
    )


# ── 3. Held keys ─────────────────────────────────────────────


def _input(a: dict) -> str:
    step = _int(a["step"])
    held = ", ".join(_str(k) for k in a["held"])
    return _lines(
        f"const held = new Set([{held}]);",
        *([f"held.delete({_str(a['release'])});"] if a.get("release") else []),
        f"const player = {{ x: {_int(a['x'])}, y: {_int(a['y'])} }};",
        f'if (held.has("ArrowLeft")) player.x -= {step};',
        f'if (held.has("ArrowRight")) player.x += {step};',
        f'if (held.has("ArrowUp")) player.y -= {step};',
        f'if (held.has("ArrowDown")) player.y += {step};',
        "console.log(`x ${player.x}, y ${player.y}`);",
    )


# ── 4. A state machine ───────────────────────────────────────


def _fsm(a: dict) -> str:
    rows = [
        f"  {mode}: {{ "
        + ", ".join(f'{ev}: "{to}"' for ev, to in table.items())
        + " },"
        for mode, table in MODES.items()
    ]
    events = ", ".join(_str(e) for e in a["events"])
    return _lines(
        "const next = {",
        *rows,
        "};",
        'let mode = "menu";',
        f"for (const event of [{events}]) {{",
        "  mode = next[mode][event] ?? mode;",
        "  console.log(mode);",
        "}",
    )


# ── 5. Entities in an array ──────────────────────────────────


def _entities(a: dict) -> str:
    v, x = a["var"], _item_var(a["var"])
    rows = [f"  {{ name: {_str(n)}, hp: {_int(hp)} }}," for n, hp in a["items"]]
    return _lines(
        f"const {v} = [",
        *rows,
        "];",
        f"for (const {x} of {v}) {x}.hp -= {_int(a['damage'])};",
        f"const alive = {v}.filter(({x}) => {x}.hp > 0);",
        f'console.log(alive.map(({x}) => {x}.name).join(", "));',
        f"console.log(`${{{v}.length - alive.length}} removed`);",
    )


# ── 6. A spawn timer ─────────────────────────────────────────


def _spawn(a: dict) -> str:
    every = _int(a["every"])
    return _lines(
        f"const dt = {_int(a['dt'])};",
        "let timer = 0;",
        "let spawned = 0;",
        f"for (let frame = 0; frame < {_int(a['frames'])}; frame++) {{",
        "  timer += dt;",
        f"  if (timer >= {every}) {{ timer -= {every}; spawned += 1; }}",
        "}",
        "console.log(`${spawned} spawned, ${timer} ms left over`);",
    )


# ── 7. A tile map ────────────────────────────────────────────


def _tiles(a: dict) -> str:
    col, row = a["check"]
    return _lines(
        "const map = [",
        *(f"  {_str(r)}," for r in a["rows"]),
        "];",
        'const y = map.findIndex((line) => line.includes("@"));',
        'const x = map[y].indexOf("@");',
        "console.log(`player at column ${x}, row ${y}`);",
        'console.log([...map.join("")].filter((c) => c === "#").length);',
        f'console.log(map[{_int(row)}][{_int(col)}] !== "#");',
    )


# ── 8. Seeded random numbers ─────────────────────────────────


def _rng(a: dict) -> str:
    head = [
        f"let seed = {_int(a['seed'])};",
        "function next() {",
        f"  seed = (seed * {MULTIPLIER}) % {MODULUS};",
        "  return seed;",
        "}",
    ]
    n = _int(a["count"])
    if a["want"] == "pick":
        v = a["var"]
        return _lines(
            f"const {v} = [{', '.join(_str(s) for s in a['choices'])}];",
            *head,
            "const picks = [];",
            f"for (let i = 0; i < {n}; i++) picks.push({v}[next() % {v}.length]);",
            'console.log(picks.join(" "));',
        )
    return _lines(
        *head,
        "const rolls = [];",
        f"for (let i = 0; i < {n}; i++) rolls.push((next() % {_int(a['sides'])}) + 1);",
        'console.log(rolls.join(" "));',
    )


# ── 9. Score and combos ──────────────────────────────────────


def _combo(a: dict) -> str:
    return _lines(
        "let score = 0;",
        "let combo = 0;",
        f"for (const shot of {_str(a['shots'])}) {{",
        '  combo = shot === "h" ? combo + 1 : 0;',
        f"  score += {_int(a['points'])} * Math.min(combo, {_int(a['cap'])});",
        "}",
        f"console.log(`score ${{score}}, high score ${{Math.max(score, "
        f"{_int(a['high'])})}}`);",
    )


# ── 10. Classes ──────────────────────────────────────────────


def _classes(a: dict) -> str:
    made = ", ".join(
        f"new {kind}({_str(name)}, {_int(x)})" for kind, name, x in a["world"])
    return _lines(
        "class Entity {",
        "  constructor(name, x) { this.name = name; this.x = x; }",
        "  update() {}",
        "}",
        f"class Player extends Entity {{ update() {{ this.x += {_int(a['run'])}; }} }}",
        f"class Enemy extends Entity {{ update() {{ this.x -= {_int(a['chase'])}; }} }}",
        f"const world = [{made}];",
        f"for (let tick = 0; tick < {_int(a['ticks'])}; tick++) "
        "for (const e of world) e.update();",
        'console.log(world.map((e) => `${e.name} ${e.x}`).join(", "));',
    )


_BUILDERS = {
    "jsb_state": _state,
    "jsb_loop": _loop,
    "jsb_input": _input,
    "jsb_fsm": _fsm,
    "jsb_entities": _entities,
    "jsb_spawn": _spawn,
    "jsb_tiles": _tiles,
    "jsb_rng": _rng,
    "jsb_combo": _combo,
    "jsb_classes": _classes,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


# ── What each should print, worked out in Python ─────────────


def _unique(names) -> None:
    if len(set(names)) != len(names):
        raise ValueError("names must be unique, or the output is ambiguous")


def expected_output(shape: str, args: dict, value=None) -> str:
    a = args
    if shape == "jsb_state":
        score = a["score"] + a["gain"]
        lives = a["lives"] - a["lost"]
        if lives < 0 or a["gain"] <= 0:
            raise ValueError("lives never go below zero, and points are won")
        return NL.join([
            f"{a['player']}: {score} points, {lives} lives",
            "still playing" if lives > 0 else "game over",
        ])
    if shape == "jsb_loop":
        x = a["x"]
        for _ in range(a["ticks"]):
            if a["want"] == "wrap":
                x = (x + a["speed"]) % a["width"]
            else:
                x = x + a["speed"]
        if a["want"] == "wrap":
            if a["x"] + a["speed"] * a["ticks"] < a["width"]:
                raise ValueError("a wrapping run must actually wrap")
            if a["x"] < 0 or a["speed"] < 0:
                raise ValueError("% of a negative differs between languages")
        return f"after {a['ticks']} ticks x is {x}"
    if shape == "jsb_input":
        held = list(a["held"])
        for k in held:
            if k not in ARROWS:
                raise ValueError(f"{k} is not an arrow key")
        keys = set(held)
        if a.get("release"):
            if a["release"] not in keys:
                raise ValueError("release a key that is held")
            keys.discard(a["release"])
        x, y = a["x"], a["y"]
        for k in keys:
            dx, dy = ARROWS[k]
            x += dx * a["step"]
            y += dy * a["step"]
        return f"x {x}, y {y}"
    if shape == "jsb_fsm":
        mode, seen = "menu", []
        for event in a["events"]:
            mode = MODES[mode].get(event, mode)
            seen.append(mode)
        if len(a["events"]) < 3:
            raise ValueError("three events at least")
        return NL.join(seen)
    if shape == "jsb_entities":
        names = [n for n, _ in a["items"]]
        _unique(names)
        alive = [n for n, hp in a["items"] if hp - a["damage"] > 0]
        removed = len(names) - len(alive)
        if not alive or not removed:
            raise ValueError("some survive and some are removed")
        return NL.join([", ".join(alive), f"{removed} removed"])
    if shape == "jsb_spawn":
        timer = spawned = 0
        for _ in range(a["frames"]):
            timer += a["dt"]
            if timer >= a["every"]:
                timer -= a["every"]
                spawned += 1
        if spawned < 2:
            raise ValueError("two spawns at least, or the timer never resets")
        if a["dt"] >= a["every"]:
            raise ValueError("a frame must be shorter than the spawn gap")
        return f"{spawned} spawned, {timer} ms left over"
    if shape == "jsb_tiles":
        rows = list(a["rows"])
        if len({len(r) for r in rows}) != 1:
            raise ValueError("every row the same width")
        if "".join(rows).count("@") != 1:
            raise ValueError("exactly one player")
        if set("".join(rows)) - set("#.@$"):
            raise ValueError("only # . @ and $ on the map")
        where = [(r.index("@"), y) for y, r in enumerate(rows) if "@" in r][0]
        walls = "".join(rows).count("#")
        col, row = a["check"]
        if not (0 <= row < len(rows) and 0 <= col < len(rows[0])):
            raise ValueError("check a cell on the map")
        return NL.join([
            f"player at column {where[0]}, row {where[1]}",
            str(walls),
            "true" if rows[row][col] != "#" else "false",
        ])
    if shape == "jsb_rng":
        seed = a["seed"]
        if not 0 < seed < MODULUS:
            raise ValueError("a Park-Miller seed is 1 to 2147483646")
        out = []
        for _ in range(a["count"]):
            seed = seed * MULTIPLIER % MODULUS
            if a["want"] == "pick":
                out.append(a["choices"][seed % len(a["choices"])])
            else:
                out.append(str(seed % a["sides"] + 1))
        return " ".join(out)
    if shape == "jsb_combo":
        shots = a["shots"]
        if set(shots) - {"h", "x"}:
            raise ValueError("shots are h for a hit and x for a miss")
        score = combo = 0
        for shot in shots:
            combo = combo + 1 if shot == "h" else 0
            score += a["points"] * min(combo, a["cap"])
        return f"score {score}, high score {max(score, a['high'])}"
    if shape == "jsb_classes":
        world = list(a["world"])
        _unique([n for _, n, _ in world])
        kinds = {k for k, _, _ in world}
        if not {"Player", "Enemy"} <= kinds or kinds - {"Player", "Enemy", "Entity"}:
            raise ValueError("a Player and an Enemy at least, nothing else")
        moves = {"Player": a["run"], "Enemy": -a["chase"], "Entity": 0}
        return ", ".join(
            f"{n} {x + moves[k] * a['ticks']}" for k, n, x in world)
    raise KeyError(shape)


# ── Complexity notes ─────────────────────────────────────────

NOTES: dict[str, Cost] = {
    "jsb_state": Cost(
        "O(1)",
        "Constant: a handful of reads and writes on one object, whatever "
        "the numbers in it are. A real game's state is bigger, but reading "
        "one field off it costs the same however many fields it has."),
    "jsb_loop": Cost(
        "O(n)",
        "Linear in the number of ticks, n: update runs once per tick and "
        "does the same small amount of work each time. That is why a game "
        "keeps update cheap — it runs sixty times a second, forever."),
    "jsb_input": Cost(
        "O(1)",
        "Constant: four has checks on the set, and a set answers has in "
        "about the same time however many keys are held. An array would "
        "have to be searched for each key instead."),
    "jsb_fsm": Cost(
        "O(n)",
        "Linear in the number of events, n: each one is two object "
        "lookups, next[mode] and then [event]. The table's size does not "
        "matter, which is the point of using a table instead of a chain "
        "of ifs."),
    "jsb_entities": Cost(
        "O(n)",
        "Linear in the number of entities, n: one pass to update them and "
        "one more for filter to build the list of survivors. Two linear "
        "passes are still linear."),
    "jsb_spawn": Cost(
        "O(n)",
        "Linear in the number of frames, n: one addition and one "
        "comparison per frame. How often something spawns does not change "
        "the cost of checking whether it is time."),
    "jsb_tiles": Cost(
        "O(rows × cols)",
        "Finding the player and counting walls each look at every tile "
        "once, rows × cols of them. Checking one cell is constant: "
        "map[row][col] goes straight there."),
    "jsb_rng": Cost(
        "O(n)",
        "Linear in how many numbers are drawn, n: each is one multiply and "
        "one remainder. The generator remembers a single number, the seed, "
        "which is also all it takes to replay the same run."),
    "jsb_combo": Cost(
        "O(n)",
        "Linear in the number of shots, n: each one updates the combo and "
        "the score once. The high score is one comparison at the end, "
        "not another pass."),
    "jsb_classes": Cost(
        "O(t × n)",
        "t ticks times n entities: every tick calls update on every "
        "entity once. Which update runs — Player's, Enemy's or Entity's — "
        "is decided by the object itself, at no extra cost."),
}


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)
