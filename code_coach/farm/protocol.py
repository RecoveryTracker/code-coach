"""How a program in Python, JavaScript or Dart talks to the farm.

Your program runs as a real Python, Node or Dart process. The farm runs in
the server. Between them is a pipe, and every drone command is one line
each way:

    program -> farm   (stdout)   "\\x1eCC" + JSON {"f": <name>, "a": [<args>]}
    farm -> program   (stdin)    JSON {"r": <result>}
                             or  JSON {"e": "<message>"}   - raise it
                             or  JSON {"stop": true}      - exit at once, quietly

The command waits for its answer, so a program is exactly as synchronous as
the game's own language. Anything else the program writes to stdout is
shown as output; stderr is read when it ends.

Names on the wire are the game's Python names. A function is "can_harvest";
a value is a string - "North", "Entities.Bush", "Items.Hay", "Grounds.Soil",
"Unlocks.Carrots", "Hats.Dinosaur_Hat". None is null; a tuple is a list.
JavaScript keeps those strings as its values (Entities.Bush === "Entities.Bush",
so a cost dictionary indexes the same way); Dart turns them into enums.

Two calls need a word of their own:

    {"f": "__error__", "a": [message, line, file]}
                                               the program crashed; file is the
                                               name (no extension) of YOUR file
                                               it happened in, "" if unknown,
                                               and line is a line of that file,
                                               or 0. No reply - the program is
                                               ending.
    {"f": "print" / "quick_print", "a": [text]} text already formatted the
                                               way the language prints it.
                                               Answered like any command
                                               (print takes a game second).

get_cost answers {} - never None - for an unlock already at its top level.

More drones (Megafarm). Drones share no memory, as in the game: each one
is a new process of the same program, started in drone mode - the
environment variable FARM_DRONE holds JSON {"fn": name, "args": [...],
"globals": {...}}. In drone mode a library defines the program's
functions WITHOUT running its top-level code, sets the globals it was
given (Python sends a snapshot of its JSON-able globals; JavaScript and
Dart send {} and their globals start from their declarations), calls
fn(*args), and sends

    {"f": "__return__", "a": [value]}   no reply; then exits 0

spawn_drone goes on the wire as ["spawn_drone", [fn_name, [args...], {globals}]]:
only a function at the top level of one of the program's files can be
spawned. fn_name is the name the entry file has it under, or "file.name"
for one in another file. Drone mode runs the entry's definitions and
imports (an imported file runs its top level, as any import does). wait_for
answers with the other drone's return value.

Simulation. simulate(filename, sim_unlocks, sim_items, sim_globals, seed,
speedup) goes on the wire as six arguments: the file's name; the unlocks
as a list of "Unlocks.X" (each at its top level) or a dict
{"Unlocks.X": level} (a negative level meaning the top one) - a whole
group passed as itself (Python's Unlocks, the game's way of saying
everything) goes as the list of its members; the items as {"Items.X": n};
the globals as {"name": value}; a seed (negative for a random one); and the
speedup. The farm runs the file as a new program on a fresh farm and
answers with the game seconds it took. The new program finds its starting
globals in the environment variable FARM_GLOBALS, JSON {"name": value}:
Python, Original and JavaScript set them as globals before the file runs;
Dart, which can't make globals at run time, offers them as simGlobals['name'].

The game's own language ("original", stubs/farm_lang.py) adds "t" to every
line it sends: the ticks its own operations took since the last line. The
farm spends them on the drone's clock before doing the command, and
{"f": "__ticks__", "a": [], "t": n} sends them on their own (answered with
null) when a long computation has no command to carry them.
range() in JavaScript and Dart is the library's own and never reaches the
farm (Python has its own).

`FUNCTIONS` below is the whole API: each Python name, how JavaScript and
Dart spell it, and its parameters. The stubs (stubs/farm_api.*) implement
exactly this table, and tests/test_farm_protocol.py holds them to it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

MARK = "\x1eCC"


@dataclass(frozen=True)
class Function:
    py: str
    js: str
    dart: str
    #: Parameter names, in order; a trailing "=..." means optional with that default.
    params: tuple[str, ...] = ()
    doc: str = ""


FUNCTIONS: tuple[Function, ...] = (
    Function("harvest", "harvest", "harvest", (), "Harvest what is under the drone. Unripe plants are destroyed."),
    Function("can_harvest", "canHarvest", "canHarvest", (), "True if what is under the drone is ripe."),
    Function("plant", "plant", "plant", ("entity",), "Plant an entity under the drone. False if it cannot."),
    Function("move", "move", "move", ("direction",), "Move one square: North, East, South or West. Wraps at the edges."),
    Function("till", "till", "till", (), "Turn grassland into soil, or soil back into grassland."),
    Function("swap", "swap", "swap", ("direction",), "Swap what is under the drone with its neighbour."),
    Function("measure", "measure", "measure", ("direction=None",),
             "Petals of a sunflower, size of a cactus, a pumpkin's id, or the next treasure or apple."),
    Function("get_pos_x", "getPosX", "getPosX", (), "The drone's x: 0 at the West edge."),
    Function("get_pos_y", "getPosY", "getPosY", (), "The drone's y: 0 at the South edge."),
    Function("get_world_size", "getWorldSize", "getWorldSize", (), "How many squares from South to North."),
    Function("get_entity_type", "getEntityType", "getEntityType", (), "What is under the drone, or None."),
    Function("get_ground_type", "getGroundType", "getGroundType", (), "Grassland or Soil."),
    Function("get_time", "getTime", "getTime", (), "Seconds of game time since the farm began."),
    Function("get_tick_count", "getTickCount", "getTickCount", (), "Ticks since this program started."),
    Function("use_item", "useItem", "useItem", ("item", "n=1"), "Use Water, Fertilizer or Weird Substance here."),
    Function("get_water", "getWater", "getWater", (), "The water level under the drone, 0 to 1."),
    Function("do_a_flip", "doAFlip", "doAFlip", (), "The drone does a flip. Takes a second."),
    Function("pet_the_piggy", "petThePiggy", "petThePiggy", (), "Pets the piggy. Takes a second."),
    Function("print", "print", "print", ("*values",), "Write in smoke above the drone. Takes a second."),
    Function("quick_print", "quickPrint", "quickPrint", ("*values",), "Write to the output only. Instant."),
    Function("num_items", "numItems", "numItems", ("item",), "How many of an item you have."),
    Function("get_cost", "getCost", "getCost", ("thing",), "What a plant or the next level of an unlock costs."),
    Function("clear", "clear", "clear", (), "The whole farm back to grass; the drone back to (0, 0)."),
    Function("get_companion", "getCompanion", "getCompanion", (),
             "The companion the plant here wants: (type, (x, y)), or None."),
    Function("unlock", "unlock", "unlock", ("unlock",), "Buy research, as the button would."),
    Function("num_unlocked", "numUnlocked", "numUnlocked", ("thing",), "Levels of an unlock bought; 1 or 0 for others."),
    Function("can_move", "canMove", "canMove", ("direction",), "True if nothing blocks that way."),
    Function("change_hat", "changeHat", "changeHat", ("hat",), "Wear a different hat."),
    Function("set_execution_speed", "setExecutionSpeed", "setExecutionSpeed", ("speed",),
             "Slow the drone down to watch it: 1 is the speed with no upgrades."),
    Function("set_world_size", "setWorldSize", "setWorldSize", ("size",),
             "Shrink the farm (3 or more) for this run. Clears it."),
    Function("random", "random", "random", (), "A random number from 0 up to (not including) 1."),
    Function("min", "min", "min", ("*values",), "The smallest of the values, or of one list."),
    Function("max", "max", "max", ("*values",), "The largest of the values, or of one list."),
    Function("abs", "abs", "abs", ("x",), "The number without its sign."),
    Function("spawn_drone", "spawnDrone", "spawnDrone", ("function", "*args"),
             "Start another drone here, running function(args). Its handle, or None if all are out."),
    Function("num_drones", "numDrones", "numDrones", (), "How many drones are on the farm now."),
    Function("max_drones", "maxDrones", "maxDrones", (), "How many drones you may have at once."),
    Function("has_finished", "hasFinished", "hasFinished", ("drone",), "True once that drone's function has returned."),
    Function("wait_for", "waitFor", "waitFor", ("drone",), "Wait for a drone to finish; its function's return value."),
    Function("simulate", "simulate", "simulate",
             ("filename", "sim_unlocks", "sim_items", "sim_globals", "seed", "speedup"),
             "Run one of your files on a fresh, separate farm; the game seconds it took. "
             "The real farm is untouched."),
)

FUNCTIONS_BY_PY = {f.py: f for f in FUNCTIONS}


def js_member(name: str) -> str:
    """Items.Weird_Substance -> WeirdSubstance: JavaScript spells members in PascalCase."""
    return "".join(part[:1].upper() + part[1:] for part in name.split("_"))


def dart_member(name: str) -> str:
    """Items.Weird_Substance -> weirdSubstance: Dart enum values are lowerCamelCase."""
    pascal = js_member(name)
    return pascal[:1].lower() + pascal[1:]


def encode_request(name: str, args: list[Any]) -> str:
    return MARK + json.dumps({"f": name, "a": args}, separators=(",", ":"))


def decode_request(line: str) -> tuple[str, list[Any]] | None:
    """A command line from a program, or None for an ordinary line of output."""
    if not line.startswith(MARK):
        return None
    body = json.loads(line[len(MARK):])
    return str(body.get("f", "")), list(body.get("a", []))


def answer(result: Any) -> str:
    return json.dumps({"r": result}, separators=(",", ":"))


def refuse(message: str) -> str:
    return json.dumps({"e": message}, separators=(",", ":"))


STOP = json.dumps({"stop": True})
