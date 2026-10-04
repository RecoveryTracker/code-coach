"""Simulation: the libraries' side of simulate(), against a fake farm.

simulate(filename, sim_unlocks, sim_items, sim_globals, seed, speedup) runs
one of the player's files as a new program on a fresh farm of its own, and
answers with the game seconds it took (see code_coach/farm/protocol.py).
The farm starts that program - an ordinary run of the file, not a drone -
with its starting globals in the environment variable FARM_GLOBALS. The
fake farm here answers each simulate with the next of SECONDS, and starts a
program with FARM_GLOBALS when a test says so.

Each library is held to the same promises, in its own language's terms:

- simulate goes down the pipe as six arguments in wire form. The unlocks
  are a whole group - the list of all of its members - or a list of them,
  or a dictionary of levels, {"Unlocks.Speed": 2}; the items are
  {"Items.Carrot": 10000}; the globals are {"name": value}, a game value by
  its name, a group as the list of its members and a tuple as a list.
  (JavaScript: only the farm's own groups become lists - a copy of one, or
  an iterable object of the program's own, is a dictionary as ever.)
- the answer comes back as a number the program can do sums with;
- a program started with FARM_GLOBALS has them before its first line runs,
  as the language's own values - a game name back as Entities.Carrot, a
  list still a list: Python as globals of the file it runs, JavaScript as
  globals every file reads, Dart as simGlobals['name'];
- a drone of a simulated program starts from its own globals: Python's are
  the copy it was spawned with, JavaScript's its declarations and the
  simulation's starting globals.

Dart takes the better part of a second to start, so it has two programs,
run side by side.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable

from code_coach.farm import data, protocol
from code_coach.farm.stubs.render import prepare
from tests.test_farm_drones_stubs import TYPESCRIPT, _run, job, returned
from tests.test_farm_stubs import HAS_DART, HAS_NODE, Run, canned, write_files

#: What the fake farm answers each simulate with, in turn: the game seconds.
#: 3 is a whole number on the wire, which Dart reads as an int.
SECONDS = (12.5, 3, 0.25, 1)

#: A whole group, as it goes down the pipe: every one of its members.
ALL_UNLOCKS = [f"Unlocks.{name}" for name in data.UNLOCKS]
ALL_HATS = [f"Hats.{name}" for name in data.HATS]

#: The globals a simulation starts with, as FARM_GLOBALS holds them.
STARTING: dict[str, Any] = {"a": 13, "crop": "Entities.Carrot", "rows": [1, 2], "costs": {"Items.Hay": 5},
                            "label": "x", "where": "North"}


# ── The fake farm ───────────────────────────────────────────────────────


def simulated(language: str, code: str | dict[str, str], *, entry: str = "main",
              starting: dict[str, Any] | None = None, drone: dict[str, Any] | None = None,
              limit: float = 90.0) -> Run:
    """Run a program - one file, or {name: code} run from entry - against the
    fake farm, which answers each simulate with the next of SECONDS. Given
    starting, it is a simulation's program, and FARM_GLOBALS holds them;
    given drone as well, it is one of that program's drones."""
    files, argv, _ = prepare(language, code, entry)
    with tempfile.TemporaryDirectory(prefix="farm-simulate-", ignore_cleanup_errors=True) as folder:
        write_files(folder, files)
        env = {k: v for k, v in os.environ.items() if k not in ("FARM_DRONE", "FARM_GLOBALS", "FARM_TS")}
        if starting is not None:
            env["FARM_GLOBALS"] = json.dumps(starting)
        if drone is not None:
            env["FARM_DRONE"] = json.dumps(drone)
            env["FARM_TS"] = str(TYPESCRIPT)
        seconds = iter(SECONDS)

        def answers(name: str, args: list) -> str:
            return protocol.answer(next(seconds)) if name == "simulate" else canned(name, args)

        return _run(argv, folder, env, answers, limit)


def at_once(*runs: Callable[[], Run]) -> list[Run]:
    """Several programs side by side: each one mostly waits for its process to start."""
    with ThreadPoolExecutor(len(runs)) as pool:
        return list(pool.map(lambda run: run(), runs))


def simulations(run: Run) -> list[list]:
    """The arguments of every simulate the program sent, in order."""
    return [args for name, args in run.calls if name == "simulate"]


# ── Python ──────────────────────────────────────────────────────────────

PY_CALLS = """\
first = simulate("f1", Unlocks, {Items.Carrot: 10000, Items.Hay: 50},
                 {"a": 13, "crop": Entities.Carrot, "rows": [1, North], "costs": {Items.Hay: 5}, "pos": (3, 5)},
                 0, 64)
second = simulate("f1", [Unlocks.Speed, Unlocks.Expand], {}, {}, -1, 1)
third = simulate("f2", {Unlocks.Speed: 2, Unlocks.Expand: -1}, {Items.Gold: 1}, {"every": Hats}, 7, 0.5)
quick_print(first * 2, second + 1, third)
"""

PY_WIRE = [
    ["f1", ALL_UNLOCKS, {"Items.Carrot": 10000, "Items.Hay": 50},
     {"a": 13, "crop": "Entities.Carrot", "rows": [1, "North"], "costs": {"Items.Hay": 5}, "pos": [3, 5]}, 0, 64],
    ["f1", ["Unlocks.Speed", "Unlocks.Expand"], {}, {}, -1, 1],
    ["f2", {"Unlocks.Speed": 2, "Unlocks.Expand": -1}, {"Items.Gold": 1}, {"every": ALL_HATS}, 7, 0.5],
]

#: A simulation's program, the file f1: it reads its starting globals from a
#: function of its own as well as from its top level.
PY_STARTED = """\
def bump():
    return a + 1


rows.append(3)
quick_print(bump(), crop == Entities.Carrot, rows, costs[Items.Hay], label, where == North, __name__)
"""

PY_DRONE = """\
def work():
    return [a, "b" in globals()]


harvest()
"""


class PythonSimulateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.calls, cls.started, cls.drone = at_once(
            lambda: simulated("python", PY_CALLS),
            # Python's own __names__ are never a simulation's to set.
            lambda: simulated("python", {"f1": PY_STARTED}, entry="f1", starting=dict(STARTING, __name__="nope")),
            # FARM_GLOBALS says a is 13, and there is a b; the drone was spawned with a = 1, and no b.
            lambda: simulated("python", PY_DRONE, starting={"a": 13, "b": 2}, drone=job("work", [], {"a": 1})),
        )

    def test_simulate_sends_six_arguments_in_wire_form(self) -> None:
        # Unlocks, the whole group, is every unlock; a list of them; a
        # dictionary of levels. Items and globals by their game names.
        self.assertEqual(simulations(self.calls), PY_WIRE, self.calls.explain())

    def test_the_answer_is_a_number(self) -> None:
        self.assertEqual(self.calls.said(), ["25.0 4 0.25"], self.calls.explain())
        self.assertEqual(self.calls.code, 0, self.calls.explain())

    def test_starting_globals_are_globals_of_the_file_it_runs(self) -> None:
        # A game name is a game value again; a list is still a list, and takes the append.
        run = self.started
        self.assertEqual(run.said(), ["14 True [1, 2, 3] 5 x True __main__"], run.explain())
        self.assertEqual(run.code, 0, run.explain())

    def test_a_drone_of_a_simulation_has_the_globals_it_was_spawned_with(self) -> None:
        # Its globals are the spawning drone's copy, the starting ones among
        # them as they were then - not FARM_GLOBALS over again.
        run = self.drone
        self.assertEqual(returned(run), [[1, False]], run.explain())
        self.assertNotIn(("harvest", []), run.calls)


# ── JavaScript ──────────────────────────────────────────────────────────

JS_CALLS = """\
const first = simulate("f1", Unlocks, { [Items.Carrot]: 10000, [Items.Hay]: 50 },
  { a: 13, crop: Entities.Carrot, rows: [1, North], costs: { [Items.Hay]: 5 } }, 0, 64);
const second = simulate("f1", [Unlocks.Speed, Unlocks.Expand], {}, {}, -1, 1);
const third = simulate("f2", { [Unlocks.Speed]: 2, [Unlocks.Expand]: -1 }, { [Items.Gold]: 1 }, { every: Hats }, 7, 0.5);
const mine = { x: 1, *[Symbol.iterator]() { yield 1; } };
const fourth = simulate("f1", new Map([[Unlocks.Speed, 1]]), new Map(),
  { copy: { ...Grounds }, mine, seen: new Set([North]) }, 0, 1);
quickPrint(first * 2, second + 1, third, fourth, typeof first);
"""

JS_WIRE = [
    ["f1", ALL_UNLOCKS, {"Items.Carrot": 10000, "Items.Hay": 50},
     {"a": 13, "crop": "Entities.Carrot", "rows": [1, "North"], "costs": {"Items.Hay": 5}}, 0, 64],
    ["f1", ["Unlocks.Speed", "Unlocks.Expand"], {}, {}, -1, 1],
    ["f2", {"Unlocks.Speed": 2, "Unlocks.Expand": -1}, {"Items.Gold": 1}, {"every": ALL_HATS}, 7, 0.5],
]

#: A copy of a group is the program's own object, and so is an object that
#: can be iterated: dictionaries, both. A Map is a dictionary, a Set a list.
JS_OWN_OBJECTS = ["f1", {"Unlocks.Speed": 1}, {},
                  {"copy": {protocol.js_member(m): f"Grounds.{m}" for m in data.GROUNDS},
                   "mine": {"x": 1}, "seen": ["North"]}, 0, 1]

#: A simulation's program, the file f1, and a file it imports, which reads a
#: starting global at its top level - before f1's first line has run.
JS_STARTED = {
    "f1": """\
import { bump, early } from "./tools.js";
rows.push(3);
quickPrint(bump(), early, crop === Entities.Carrot, rows.join(","), costs[Items.Hay], label, where === North);
""",
    "tools": "export const early = a * 2;\nexport function bump() {\n  return a + 1;\n}\n",
}

JS_DRONE = """\
const own = 2;
function work() {
  return [a, own, typeof label];
}
harvest();
"""


@unittest.skipUnless(HAS_NODE, "needs node")
class JavaScriptSimulateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.calls, cls.started, cls.read_only = at_once(
            lambda: simulated("javascript", JS_CALLS),
            lambda: simulated("javascript", JS_STARTED, entry="f1", starting=STARTING),
            lambda: simulated("javascript", 'quickPrint("never");\n', starting={"undefined": 1}),
        )

    def test_simulate_sends_six_arguments_in_wire_form(self) -> None:
        self.assertEqual(simulations(self.calls)[:3], JS_WIRE, self.calls.explain())

    def test_only_the_farms_own_groups_go_as_lists(self) -> None:
        self.assertEqual(simulations(self.calls)[3], JS_OWN_OBJECTS, self.calls.explain())

    def test_the_answer_is_a_number(self) -> None:
        self.assertEqual(self.calls.said(), ["25 4 0.25 1 number"], self.calls.explain())
        self.assertEqual(self.calls.code, 0, self.calls.explain())

    def test_starting_globals_are_globals_every_file_reads(self) -> None:
        run = self.started
        self.assertEqual(run.said(), ["14 26 true 1,2,3 5 x true"], run.explain())
        self.assertEqual(run.code, 0, run.explain())

    def test_a_global_javascript_will_not_change_is_refused_before_anything_runs(self) -> None:
        run = self.read_only
        self.assertEqual(run.calls, [("__error__", [
            "A simulation can't start with a global called undefined: JavaScript doesn't let it change.",
            0, ""])], run.explain())
        self.assertEqual(run.code, 1)

    @unittest.skipUnless(TYPESCRIPT.is_file(), "needs TypeScript in web/node_modules")
    def test_a_drone_of_a_simulation_has_its_starting_globals_too(self) -> None:
        # Its own declarations, and the simulation's starting globals; not
        # the top level's harvest().
        run = simulated("javascript", JS_DRONE, starting=STARTING, drone=job("work"))
        self.assertEqual(returned(run), [[13, 2, "string"]], run.explain())
        self.assertNotIn(("harvest", []), run.calls)


# ── Dart ────────────────────────────────────────────────────────────────

DART_CALLS = """\
void main() {
  final first = simulate('f1', Unlocks.values, {Items.carrot: 10000, Items.hay: 50},
      {'a': 13, 'crop': Entities.carrot, 'rows': [1, north], 'costs': {Items.hay: 5}, 'pos': (3, 5),
       'label': 'x', 'on': true, 'none': null}, 0, 64);
  final second = simulate('f1', [Unlocks.speed, Unlocks.expand], {}, {}, -1, 1);
  final third = simulate('f2', {Unlocks.speed: 2, Unlocks.expand: -1}, {Items.gold: 1}, {'every': Hats.values}, 7, 0.5);
  quickPrint('${first * 2} ${second + 1} $third ${simGlobals.isEmpty}');
}
"""

DART_WIRE = [
    ["f1", ALL_UNLOCKS, {"Items.Carrot": 10000, "Items.Hay": 50},
     {"a": 13, "crop": "Entities.Carrot", "rows": [1, "North"], "costs": {"Items.Hay": 5}, "pos": [3, 5],
      "label": "x", "on": True, "none": None}, 0, 64],
    ["f1", ["Unlocks.Speed", "Unlocks.Expand"], {}, {}, -1, 1],
    ["f2", {"Unlocks.Speed": 2, "Unlocks.Expand": -1}, {"Items.Gold": 1}, {"every": ALL_HATS}, 7, 0.5],
]

#: A simulation's program, the file f1, and a file it imports: both read
#: simGlobals.
DART_STARTED = {
    "f1": """\
import 'tools.dart';

void main() {
  final crop = simGlobals['crop'];
  final rows = simGlobals['rows'] as List<int>;
  final costs = simGlobals['costs'] as Map;
  quickPrint('${bump()} ${crop == Entities.carrot} ${crop is Entities} ${rows.first + 1} $rows '
      '${costs[Items.hay]} ${simGlobals['label']} ${simGlobals['where'] == north}');
}
""",
    "tools": "int bump() => (simGlobals['a'] as int) + 1;\n",
}


@unittest.skipUnless(HAS_DART, "needs dart")
class DartSimulateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.calls, cls.started = at_once(
            lambda: simulated("dart", DART_CALLS, limit=120.0),
            lambda: simulated("dart", DART_STARTED, entry="f1", starting=STARTING, limit=120.0),
        )

    def test_the_library_compiles_without_a_word(self) -> None:
        for run in (self.calls, self.started):
            self.assertEqual(run.stderr.strip(), "", run.explain())

    def test_simulate_sends_six_arguments_in_wire_form(self) -> None:
        # Unlocks.values is every unlock; a list of them; a map of levels.
        # Enum keys and values by their game names, a record as a list.
        self.assertEqual(simulations(self.calls), DART_WIRE, self.calls.explain())

    def test_the_answer_is_a_double(self) -> None:
        # 3 arrives as an int and is a double all the same. And with no
        # FARM_GLOBALS, simGlobals is there, and empty.
        self.assertEqual(self.calls.said(), ["25.0 4.0 0.25 true"], self.calls.explain())
        self.assertEqual(self.calls.code, 0, self.calls.explain())

    def test_starting_globals_are_in_sim_globals(self) -> None:
        # An enum value is the enum again; a list is a List<int>.
        run = self.started
        self.assertEqual(run.said(), ["14 true true 2 [1, 2] 5 x true"], run.explain())
        self.assertEqual(run.code, 0, run.explain())


if __name__ == "__main__":
    unittest.main()
