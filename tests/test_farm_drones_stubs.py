"""Megafarm: the libraries' side of more drones, against a fake farm.

A drone is a new process of the same program, started in drone mode: the
environment variable FARM_DRONE holds {"fn", "args", "globals"} (see
code_coach/farm/protocol.py). The fake farm here does with spawn_drone
what the real one does, one drone at a time: it starts the drone there and
then - same folder, same command, FARM_DRONE added - runs it to its end,
and only then answers the spawn with the drone's handle. wait_for is
answered with what the drone sent back in __return__.

Each library is held to the same promises, in its own language's terms:

- spawn_drone goes down the pipe as [name, [args...], {globals}]: Python's
  globals are the ones that can travel and never the farm's own names;
  JavaScript and Dart send {};
- only a function declared at the top level can be spawned - a nested
  function, a lambda, a closure is refused with FarmError before anything
  reaches the farm;
- a drone runs its one function and nothing else: the program's own
  top-level harvest() never reaches the farm from a drone;
- its arguments (and Python's globals) arrive as the program's own values;
- what it returns goes back as __return__, wired: Entities.Bush is
  "Entities.Bush";
- wait_for hands that back as the language's own value again;
- an error inside a drone reports the player's line.

Dart takes the better part of a second to start, so its programs are few
and run side by side.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable

from code_coach.farm import protocol
from code_coach.farm.stubs.render import dart_functions, dart_runner, prepare
from tests.test_farm_stubs import HAS_DART, HAS_NODE, Run, _kill, canned

#: Where the runner tells a JavaScript drone TypeScript's compiler is.
TYPESCRIPT = Path(__file__).resolve().parents[1] / "web" / "node_modules" / "typescript" / "lib" / "typescript.js"


# ── The fake farm, with drones ──────────────────────────────────────────


def _run(argv: list[str], folder: str, env: dict[str, str],
         answers: Callable[[str, list], str], limit: float) -> Run:
    """One process of the program against the fake farm, to its end."""
    proc = subprocess.Popen(argv, cwd=folder, env=env, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timed_out = threading.Event()

    def give_up() -> None:
        timed_out.set()
        _kill(proc)

    watchdog = threading.Timer(limit, give_up)
    watchdog.daemon = True
    watchdog.start()
    errors: list[bytes] = []
    drain = threading.Thread(target=lambda: errors.append(proc.stderr.read()), daemon=True)
    drain.start()
    calls: list[tuple[str, list]] = []
    output: list[str] = []
    try:
        for raw in proc.stdout:
            line = raw.decode("utf-8", "replace").rstrip("\r\n")
            request = protocol.decode_request(line)
            if request is None:
                output.append(line)
                continue
            calls.append(request)
            name, args = request
            if name in ("__error__", "__return__"):  # the library's own: no answer
                continue
            try:
                proc.stdin.write((answers(name, args) + "\n").encode("utf-8"))
                proc.stdin.flush()
            except OSError:
                pass  # it has already gone
        code = proc.wait(timeout=limit)
    finally:
        watchdog.cancel()
        _kill(proc)
        drain.join(timeout=10)
        for pipe in (proc.stdin, proc.stdout, proc.stderr):
            try:
                pipe.close()
            except OSError:
                pass
    return Run(calls, output, b"".join(errors).decode("utf-8", "replace"), code, timed_out.is_set())


def returned(run: Run) -> list | None:
    """The [value] a drone sent back in __return__, if it sent one."""
    return next((args for name, args in run.calls if name == "__return__"), None)


def names(run: Run) -> list[str]:
    return [name for name, _ in run.calls]


def farm(language: str, code: str, *, job: dict[str, Any] | None = None,
         typescript: bool = True, limit: float = 90.0) -> tuple[Run, list[Run]]:
    """Run a program - or, given a job, one drone of it - against the fake
    farm. Returns that run, and the drones it spawned, in order."""
    files, argv, _ = prepare(language, code)
    with tempfile.TemporaryDirectory(prefix="farm-drones-", ignore_cleanup_errors=True) as folder:
        for name, text in files.items():
            Path(folder, name).write_text(text, encoding="utf-8")
        env = dict(os.environ)
        env.pop("FARM_DRONE", None)
        env.pop("FARM_TS", None)
        if typescript:
            env["FARM_TS"] = str(TYPESCRIPT)
        drones: list[Run] = []

        def answers(name: str, args: list) -> str:
            if name == "spawn_drone":
                fn, given, snapshot = args
                order = {"fn": fn, "args": given, "globals": snapshot}
                drones.append(_run(argv, folder, dict(env, FARM_DRONE=json.dumps(order)), answers, limit))
                return protocol.answer(len(drones))
            if name == "wait_for":
                back = returned(drones[args[0] - 1])
                return protocol.answer(back[0] if back else None)
            if name == "has_finished":
                return protocol.answer(True)
            if name == "num_drones":
                return protocol.answer(1 + len(drones))
            if name == "max_drones":
                return protocol.answer(4)
            return canned(name, args)

        if job is not None:
            env = dict(env, FARM_DRONE=json.dumps(job))
        run = _run(argv, folder, env, answers, limit)
    return run, drones


def farm_all(language: str, *jobs: tuple[str, dict[str, Any] | None]) -> list[tuple[Run, list[Run]]]:
    """Several at once, each (code, job): each one mostly waits for its process to start."""
    with ThreadPoolExecutor(len(jobs)) as pool:
        return list(pool.map(lambda pair: farm(language, pair[0], job=pair[1]), jobs))


def line_of(code: str, text: str) -> int:
    """The number of the line of code that is exactly text."""
    return code.splitlines().index(text) + 1


def job(fn: str, args: list | None = None, snapshot: dict | None = None) -> dict[str, Any]:
    return {"fn": fn, "args": args or [], "globals": snapshot or {}}


# ── Python ──────────────────────────────────────────────────────────────

PYTHON = """\
size = 3
crop = Entities.Carrot
rows = [1, 2]
costs = {Items.Hay: 5}
nothing = None
thing = object()
group = Entities
import math


def work(n, kind, extra=size):
    rows.append(n)
    quick_print(n, kind == Entities.Bush, extra, crop == Entities.Carrot, rows, costs[Items.Hay], nothing)
    return Entities.Bush


def broken():
    x = 1
    return x + undefined_name


def outer():
    def inner():
        pass
    return inner


if True:
    def tucked_away():
        pass


def refuse_all():
    for f in (outer(), lambda: 1, print, tucked_away, "work"):
        try:
            spawn_drone(f)
        except FarmError as error:
            quick_print(error)
    try:
        spawn_drone(work, thing)
    except FarmError as error:
        quick_print(error)


harvest()
refuse_all()
handle = spawn_drone(work, 7, Entities.Bush)
quick_print(handle, wait_for(handle) == Entities.Bush, num_drones(), max_drones(), has_finished(handle))
"""

PY_REFUSED = "spawn_drone needs a function defined at the top level of your program, like def harvest_column():"

#: The globals PYTHON's spawn sends. Not thing (an object), group (the
#: farm's Entities), math, the functions, the farm's own names or
#: __builtins__: only what JSON holds.
PY_GLOBALS = {"size": 3, "crop": "Entities.Carrot", "rows": [1, 2], "costs": {"Items.Hay": 5}, "nothing": None}


class PythonDroneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Each drone gets the globals a spawn would send: work's default
        # value reads size as it is defined.
        (cls.main, cls.drones), (cls.broken, _), (cls.lost, _), (cls.odd, _) = farm_all(
            "python",
            (PYTHON, None),
            (PYTHON, job("broken", [], PY_GLOBALS)),
            (PYTHON, job("nowhere", [], PY_GLOBALS)),
            (PYTHON, job("outer", [], PY_GLOBALS)),
        )

    def test_spawn_sends_the_name_the_arguments_and_the_globals_that_travel(self) -> None:
        spawns = [args for name, args in self.main.calls if name == "spawn_drone"]
        self.assertEqual(spawns, [["work", [7, "Entities.Bush"], PY_GLOBALS]], self.main.explain())

    def test_only_a_top_level_function_can_be_spawned(self) -> None:
        # A nested function, a lambda, the farm's print, a def inside an if
        # (a drone, running only the definitions, would not have it), a
        # string; then a function with an argument that cannot travel.
        said = self.main.said()
        self.assertEqual(said[:5], [PY_REFUSED] * 5, self.main.explain())
        self.assertEqual(said[5], "spawn_drone can only hand a drone numbers, text, lists, "
                                  "dictionaries and the game's values.")

    def test_the_drone_runs_only_its_function(self) -> None:
        self.assertEqual(len(self.drones), 1, self.main.explain())
        drone = self.drones[0]
        # The top-level harvest() is the program's, not the drone's.
        self.assertEqual(names(self.main)[0], "harvest")
        self.assertNotIn("harvest", names(drone), drone.explain())
        self.assertEqual(drone.code, 0, drone.explain())
        self.assertEqual(drone.output, [])

    def test_arguments_and_globals_arrive_as_your_own_values(self) -> None:
        # kind is Entities.Bush again; extra defaulted to the global size,
        # which was there before the def ran; rows is still a list - it took
        # the append - and costs is still indexed by an item.
        self.assertEqual(self.drones[0].said(), ["7 True 3 True [1, 2, 7] 5 None"], self.drones[0].explain())

    def test_the_drone_sends_back_what_it_returned(self) -> None:
        drone = self.drones[0]
        self.assertEqual(drone.calls[-1], ("__return__", ["Entities.Bush"]), drone.explain())

    def test_wait_for_hands_back_your_own_value(self) -> None:
        self.assertEqual(self.main.said()[-1], "1 True 2 4 True", self.main.explain())
        self.assertEqual(self.main.code, 0, self.main.explain())

    def test_an_error_in_a_drone_reports_your_line(self) -> None:
        run = self.broken
        line = line_of(PYTHON, "    return x + undefined_name")
        self.assertEqual(run.calls, [("__error__", ["NameError: name 'undefined_name' is not defined", line])],
                         run.explain())
        self.assertEqual(run.code, 1)

    def test_a_drone_without_its_function_says_so(self) -> None:
        self.assertEqual(self.lost.error(), [
            "This drone was to run nowhere(), but your program defines no function of that name at its top level.",
            0], self.lost.explain())

    def test_a_drone_can_only_hand_back_what_can_travel(self) -> None:
        message, _line = self.odd.error() or ["", 0]
        self.assertTrue(message.startswith("outer() returned a function, which a drone can't hand back"),
                        self.odd.explain())


# ── JavaScript ──────────────────────────────────────────────────────────

JS = """\
"use strict";
const size = 3;
const crop = Entities.Carrot;
const rows = [1, -2, `three`, { [Items.Hay]: 5 }];
let later = getWorldSize();
const work = (n, kind) => {
  quickPrint(n, kind === Entities.Bush, size, crop, rows.length, rows[3][Items.Hay], typeof later);
  return Entities.Bush;
};
function broken() {
  const x = 1;
  return x + undefinedName;
}
function outer() {
  function inner() {}
  return inner;
}
class Thing {}
harvest();
for (const f of [outer(), () => 1, Thing, "work", function () {}]) {
  try {
    spawnDrone(f);
  } catch (error) {
    quickPrint(error instanceof FarmError, error.message);
  }
}
const handle = spawnDrone(work, 7, Entities.Bush);
quickPrint(handle, waitFor(handle) === Entities.Bush, numDrones(), maxDrones(), hasFinished(handle));
"""

JS_REFUSED = ("true spawnDrone needs a function declared at the top level of your program, "
              "like function harvestColumn() { ... }")


@unittest.skipUnless(HAS_NODE, "needs node")
@unittest.skipUnless(TYPESCRIPT.is_file(), "needs TypeScript in web/node_modules")
class JavaScriptDroneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (cls.main, cls.drones), (cls.broken, _), (cls.lost, _) = farm_all(
            "javascript",
            (JS, None),
            (JS, job("broken")),
            (JS, job("nowhere")),
        )

    def test_spawn_sends_the_name_and_the_arguments(self) -> None:
        spawns = [args for name, args in self.main.calls if name == "spawn_drone"]
        self.assertEqual(spawns, [["work", [7, "Entities.Bush"], {}]], self.main.explain())

    def test_only_a_top_level_function_can_be_spawned(self) -> None:
        # A nested function, an arrow with no name, a class, a string, and
        # an anonymous function.
        self.assertEqual(self.main.said()[:5], [JS_REFUSED] * 5, self.main.explain())

    def test_the_drone_runs_only_its_definitions_and_its_function(self) -> None:
        self.assertEqual(len(self.drones), 1, self.main.explain())
        drone = self.drones[0]
        self.assertEqual(names(self.main)[:2], ["get_world_size", "harvest"])
        # Neither the harvest() nor the getWorldSize() of the top level.
        self.assertNotIn("harvest", names(drone), drone.explain())
        self.assertNotIn("get_world_size", names(drone), drone.explain())
        self.assertEqual(drone.code, 0, drone.explain())

    def test_plain_declarations_are_there_and_the_rest_are_not(self) -> None:
        # size, crop and rows were written out plainly, so the drone has them;
        # later came from a command, so it has no later at all.
        self.assertEqual(self.drones[0].said(), ["7 true 3 Entities.Carrot 4 5 undefined"],
                         self.drones[0].explain())

    def test_the_drone_sends_back_what_it_returned(self) -> None:
        self.assertEqual(returned(self.drones[0]), ["Entities.Bush"], self.drones[0].explain())

    def test_wait_for_hands_back_the_value(self) -> None:
        self.assertEqual(self.main.said()[-1], "1 true 2 4 true", self.main.explain())
        self.assertEqual(self.main.code, 0, self.main.explain())

    def test_an_error_in_a_drone_reports_your_line(self) -> None:
        # The statements around it were blanked, not removed: the line is still yours.
        run = self.broken
        line = line_of(JS, "  return x + undefinedName;")
        self.assertEqual(run.calls, [("__error__", ["ReferenceError: undefinedName is not defined", line])],
                         run.explain())
        self.assertEqual(run.code, 1)

    def test_a_drone_without_its_function_says_so(self) -> None:
        self.assertEqual(self.lost.error(), [
            "This drone was to run nowhere(), but your program declares no function of that name at its "
            "top level.", 0], self.lost.explain())

    def test_a_drone_needs_to_be_told_where_typescript_is(self) -> None:
        run, _ = farm("javascript", JS, job=job("work", [1, "Entities.Bush"]), typescript=False)
        message, _line = run.error() or ["", 0]
        self.assertIn("FARM_TS", message, run.explain())
        self.assertNotIn("harvest", names(run))


# ── Dart ────────────────────────────────────────────────────────────────

#: Besides the drones, a few declarations that are not functions, or not
#: top-level ones, and look a little like them - runner.dart lists every
#: top-level function, and must still compile.
DART = """\
import 'dart:math' as math;

// void commented() {}
const size = 3;
final rows = [1, 2];
final greeting = 'void inString() { ${rows.map((r) { return '}'; })} }';
final made = maker(1);
int counter = cond() ? maker(1) : maker(2);
typedef IntOp = int Function(int);
extension type Meters(int value) {}
class Box {
  static void stat() {}
}
int get answer => 42;
set answer(int v) {}

bool cond() => true;
int maker(int n) => n;

Entities work(int n, Entities kind, List<int> more) {
  quickPrint('$n ${kind == Entities.bush} $size ${rows.length} ${more.length} ${more.first + 1}');
  return Entities.bush;
}

int broken() {
  final xs = [1];
  return xs[5];
}

T pick<T>(List<T> xs) => xs.first;
(int, int) pos() => (1, 2);
math.Point<int> origin() => const math.Point(0, 0);

void main() {
  harvest();
  void inner() {}
  for (final Function f in [inner, () => 1, print, Box.stat, _hidden]) {
    try {
      spawnDrone(f);
    } on FarmError catch (error) {
      quickPrint(error.message);
    }
  }
  final handle = spawnDrone(work, [7, Entities.bush, [1, 2]])!;
  quickPrint('$handle ${waitFor(handle) == Entities.bush} ${numDrones()} ${maxDrones()} ${hasFinished(handle)}');
}

void _hidden() {}
"""

DART_REFUSED = ("spawnDrone needs a function declared at the top level of your program, "
                "like void harvestColumn() { ... }")


@unittest.skipUnless(HAS_DART, "needs dart")
class DartDroneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (cls.main, cls.drones), (cls.broken, _), (cls.lost, _) = farm_all(
            "dart",
            (DART, None),
            (DART, job("broken")),
            (DART, job("nowhere")),
        )

    def test_the_runner_compiles_without_a_word(self) -> None:
        self.assertEqual(self.main.stderr.strip(), "", self.main.explain())

    def test_spawn_sends_the_name_and_the_arguments(self) -> None:
        spawns = [args for name, args in self.main.calls if name == "spawn_drone"]
        self.assertEqual(spawns, [["work", [7, "Entities.Bush", [1, 2]], {}]], self.main.explain())

    def test_only_a_top_level_function_can_be_spawned(self) -> None:
        # A local function, a closure, dart:core's print, a static method -
        # its toString reads like a top-level function's - and a private one.
        said = self.main.said()
        self.assertEqual(said[:4], [DART_REFUSED] * 4, self.main.explain())
        self.assertTrue(said[4].startswith("spawnDrone needs a function whose name does not start with _"),
                        self.main.explain())

    def test_the_drone_runs_only_its_function(self) -> None:
        self.assertEqual(len(self.drones), 1, self.main.explain())
        drone = self.drones[0]
        self.assertEqual(names(self.main)[0], "harvest")
        self.assertNotIn("harvest", names(drone), drone.explain())
        self.assertEqual(drone.code, 0, drone.explain())

    def test_arguments_arrive_as_your_own_values(self) -> None:
        # Entities.bush again, and [1, 2] as a List<int>, which work() asks for.
        self.assertEqual(self.drones[0].said(), ["7 true 3 2 2 2"], self.drones[0].explain())

    def test_the_drone_sends_back_what_it_returned(self) -> None:
        self.assertEqual(returned(self.drones[0]), ["Entities.Bush"], self.drones[0].explain())

    def test_wait_for_hands_back_your_own_value(self) -> None:
        self.assertEqual(self.main.said()[-1], "1 true 2 4 true", self.main.explain())
        self.assertEqual(self.main.code, 0, self.main.explain())

    def test_an_error_in_a_drone_reports_your_line(self) -> None:
        run = self.broken
        message, line = run.error() or ["", 0]
        self.assertTrue(message.startswith("RangeError"), run.explain())
        self.assertEqual(line, line_of(DART, "  return xs[5];"), run.explain())
        self.assertNotIn("harvest", names(run))
        self.assertEqual(run.code, 1)

    def test_a_drone_without_its_function_says_so(self) -> None:
        self.assertEqual(self.lost.error(), [
            "This drone was to run nowhere(), but your program declares no function of that name at its "
            "top level.", 0], self.lost.explain())


# ── Finding Dart's top-level functions ──────────────────────────────────


class DartRunnerTests(unittest.TestCase):
    def test_every_top_level_function_and_nothing_else(self) -> None:
        self.assertEqual(dart_functions(DART), ["cond", "maker", "work", "broken", "pick", "pos", "origin"])

    def test_comments_strings_and_bodies_hide_nothing_and_show_nothing(self) -> None:
        code = (
            "/* void a() {} /* nested */ void b() {} */\n"
            "final s = r'void c() {}' '''\n void d() {}\n''' \"${f(() { return '}'; })}\";\n"
            "void real() {\n  void inner() {}\n}\n"
            "external void ext();\n"
            "Future<void> later() async {}\n"
            "Iterable<int> gen() sync* {}\n"
            "void Function(int)? maybe() => null;\n"
            "noType() {}\n"
            "void _private() {}\n"
            "void main() {}\n"
        )
        self.assertEqual(dart_functions(code), ["real", "later", "gen", "maybe", "noType"])

    def test_the_runner_lists_them_for_the_drones(self) -> None:
        runner = dart_runner("void a() {}\nvoid b$c() {}\nvoid main() {}\n")
        self.assertIn("farm.runFarmProgram(program.main, drones: {\n"
                      "  'a': program.a,\n"
                      "  'b\\$c': program.b$c,\n"
                      "});", runner)


if __name__ == "__main__":
    unittest.main()
