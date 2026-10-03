"""Import: a program of several files, against a fake farm.

A program is one or more named files, and one of them - the entry - runs.
The files import each other with each language's own syntax (see
code_coach/farm/stubs/render.py):

- Python: import tools, from tools import harvest_column, import tools as t
- JavaScript: ES modules - import { harvestColumn } from "./tools.js"
- Dart: import 'tools.dart';

Each library is held to the same promises, in its own language's terms:

- a function of another file, called from the entry, sends its commands
  under the game's names, just as the entry's own would;
- a file imports another, which imports a third, and every one of them sees
  the farm's names without importing anything;
- an error in a file is reported as [message, its line, its name], whether
  it happens in a function called from elsewhere or while the file is
  being imported;
- a file that does not compile is reported the same way - Dart's compiler,
  which runs before the library can say anything, says it on stderr as
  tools.dart:LINE:COL: Error: ...;
- (Python) a file of the player's called json or random is theirs, and the
  library, which imports Python's own json, is none the worse for it;
- a drone can be spawned with a function from another file. It goes on
  the wire by its name when the entry imports it by that name, and as
  tools.row - the file's name and its own - when it is reached some other
  way; and a drone running it runs the entry's imports, which run the
  imported files' top level, as any import does.

The fake farm is the one in test_farm_stubs.py, and the one with drones in
test_farm_drones_stubs.py. Dart takes the better part of a second to
start, so its programs are few and run side by side.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from code_coach.farm.stubs.render import dart_runner, js_lead, prepare
from tests.test_farm_drones_stubs import TYPESCRIPT, farm, farm_all, job, names, returned
from tests.test_farm_stubs import HAS_DART, HAS_NODE, drive, drive_all

#: Every command a program of three files sends on its way to its output:
#: two harvests and moves in another file's function, which asks a third
#: file's function where the drone is.
COLUMN_OF_TWO = [
    ("harvest", []), ("move", ["North"]),
    ("harvest", []), ("move", ["North"]),
    ("get_pos_x", []), ("get_pos_y", []),
]


# ── What prepare() makes of several files ───────────────────────────────


def _runtime(language: str) -> bool:
    return {"python": True, "javascript": HAS_NODE, "dart": HAS_DART}[language]


class PrepareTests(unittest.TestCase):
    TWO = {"main": "first\nsecond\n", "tools": "third\nfourth\n"}

    def test_every_file_is_written_where_it_says_and_keeps_its_lines(self) -> None:
        extension = {"python": ".py", "javascript": ".js", "dart": ".dart"}
        for language, ext in extension.items():
            if not _runtime(language):
                continue
            with self.subTest(language=language):
                files, _argv, where = prepare(language, self.TWO)
                self.assertEqual(where, {"main": f"main{ext}", "tools": f"tools{ext}"})
                for name, code in self.TWO.items():
                    written = files[where[name]].splitlines()
                    self.assertTrue(written[0].endswith(code.splitlines()[0]), written)
                    self.assertEqual(written[1:], code.splitlines()[1:])

    def test_one_string_is_one_file_called_main(self) -> None:
        _files, argv, where = prepare("python", "harvest()\n")
        self.assertEqual(where, {"main": "main.py"})
        self.assertEqual(argv[-1], "main")

    def test_the_entry_is_the_file_that_runs(self) -> None:
        self.assertEqual(prepare("python", self.TWO, "tools")[1][-1], "tools")
        if HAS_NODE:
            self.assertEqual(prepare("javascript", self.TWO, "tools")[1][-1], "tools")
        runner = dart_runner(self.TWO, "tools")
        self.assertIn("import 'tools.dart' as program;\n", runner)
        self.assertIn("import 'main.dart' as program_main;\n", runner)

    def test_javascript_files_are_es_modules_that_hand_over_their_names(self) -> None:
        if not HAS_NODE:
            self.skipTest("needs node")
        files, _argv, _where = prepare("javascript", self.TWO)
        self.assertEqual(files["package.json"].strip(), '{"type": "module"}')
        self.assertTrue(files["tools.js"].startswith(js_lead("tools")))
        self.assertNotIn("\n", js_lead("tools"))

    def test_names_a_file_cannot_have(self) -> None:
        for bad in ["Tools", "2go", "my-file", "a.b", "", "café", "farm_api", "runner", "package"]:
            with self.subTest(name=bad), self.assertRaises(ValueError):
                prepare("python", {"main": "", bad: ""})
        with self.assertRaises(ValueError):
            prepare("python", {"main": ""}, "tools")
        with self.assertRaises(ValueError):
            prepare("python", "harvest()\n", "tools")

    def test_dart_drones_can_reach_every_file_and_the_entry_wins_a_name(self) -> None:
        runner = dart_runner({
            "main": "void main() {}\nvoid helper() {}\n",
            "tools": "void helper() {}\nint column() => 1;\n",
            "aaa": "void column2() {}\n",
        })
        self.assertIn("import 'farm_api.dart' as farm;\n"
                      "import 'main.dart' as program;\n"
                      "import 'aaa.dart' as program_aaa;\n"
                      "import 'tools.dart' as program_tools;\n", runner)
        self.assertIn("drones: {\n"
                      "  'helper': program.helper,\n"
                      "  'column2': program_aaa.column2,\n"
                      "  'tools.helper': program_tools.helper,\n"
                      "  'column': program_tools.column,\n"
                      "});", runner)


# ── Python ──────────────────────────────────────────────────────────────

PY_STORY = {
    "main": """\
import tools
from tools import harvest_column
import tools as t
from records import Spot

harvest_column(2)
quick_print(tools.SIZE, t.SIZE, tools.corner(), __name__, tools.__name__, Spot(1, 2))
""",
    "tools": """\
from shapes import corner
SIZE = 3


def harvest_column(n):
    for _ in range(n):
        harvest()
        move(North)
    return corner()
""",
    "shapes": """\
def corner():
    return get_pos_x(), get_pos_y()
""",
    # A dataclass needs its module where Python keeps modules, in sys.modules.
    "records": """\
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Spot:
    x: int
    y: int
""",
}

#: Files named like Python's own modules - and a third that imports Python's
#: math, one of them, and uses the farm's random(), which it never imported.
PY_SHADOWS = {
    "main": """\
import json
import random
from json import VALUE
import mathlike

quick_print(json.VALUE, VALUE, random.pick(), mathlike.floor_of(2.5), mathlike.roll())
move(North)
""",
    "json": "VALUE = 'my json'\n",
    "random": "def pick():\n    return 'my random'\n",
    "mathlike": """\
import math
import json


def floor_of(x):
    return math.floor(x), json.VALUE


def roll():
    return random()
""",
}

PY_TEND = {
    "main": "from tools import tend\nmove(North)\ntend()\n",
    "tools": "def tend():\n    x = 1\n    return x + nothing_here\n",
}

PY_REFUSED = {
    "main": "import tools\nmove(North)\ntools.tend()\n",
    "tools": "def tend():\n    pet_the_piggy()\n",
}

PY_BROKEN = {
    "main": "move(North)\nimport tools\nquick_print('never')\n",
    "tools": "x = 1\ndef broken(:\n    pass\n",
}

PY_IMPORT_CRASH = {
    "main": "import tools\nquick_print('never')\n",
    "tools": "move(North)\nundefined_thing\n",
}

PY_DRONES = {
    "main": """\
from tools import column
from tools import row as sideways
import tools

harvest()
first = spawn_drone(column, 2)
quick_print(wait_for(first))
second = spawn_drone(sideways)
quick_print(wait_for(second))
third = spawn_drone(tools.column, 1)
try:
    spawn_drone(tools.make_column())
except FarmError as error:
    quick_print(error)
""",
    "tools": """\
import shapes
quick_print("tools ran")


def column(n):
    for _ in range(n):
        harvest()
        move(North)
    return shapes.corner()


def row():
    move(East)
    return "row done"


def make_column():
    def column():
        pass
    return column
""",
    "shapes": "def corner():\n    return get_pos_x(), get_pos_y()\n",
}

PY_REFUSAL = "spawn_drone needs a function defined at the top level of your program, like def harvest_column():"


class PythonImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.story, cls.shadows, cls.tend, cls.refused, cls.broken, cls.import_crash = drive_all(
            "python", PY_STORY, PY_SHADOWS, PY_TEND, PY_REFUSED, PY_BROKEN, PY_IMPORT_CRASH)
        cls.main, cls.drones = farm("python", PY_DRONES)

    def test_a_function_from_another_file_sends_its_commands(self) -> None:
        run = self.story
        self.assertEqual(run.calls[:len(COLUMN_OF_TWO)], COLUMN_OF_TWO, run.explain())
        self.assertEqual(run.code, 0, run.explain())

    def test_files_import_files_and_see_the_farm_without_importing_it(self) -> None:
        # tools imported shapes; tools.corner is shapes' corner; the entry is
        # __main__, the others are named for their files.
        self.assertEqual(self.story.said(), ["3 3 (7, 2) __main__ tools Spot(x=1, y=2)"], self.story.explain())

    def test_a_file_named_like_pythons_own_module_is_yours(self) -> None:
        # The library's own commands still go down the pipe as JSON - it has
        # Python's json - while every file of yours that imports json gets
        # yours. Python's math is still Python's, and random() the farm's.
        run = self.shadows
        self.assertEqual(run.said(), ["my json my json my random (2, 'my json') 0.5"], run.explain())
        self.assertIn(("random", []), run.calls)
        self.assertEqual(run.calls[-1], ("move", ["North"]), run.explain())
        self.assertEqual(run.code, 0, run.explain())

    def test_an_error_in_another_file_names_that_file_and_its_line(self) -> None:
        run = self.tend
        self.assertEqual(run.calls[0], ("move", ["North"]))
        self.assertEqual(run.error(), ["NameError: name 'nothing_here' is not defined", 3, "tools"], run.explain())
        self.assertEqual(run.code, 1)

    def test_a_refusal_in_another_file_names_that_file_and_its_line(self) -> None:
        self.assertEqual(self.refused.error(), ["nope", 2, "tools"], self.refused.explain())

    def test_a_file_that_does_not_compile_names_itself_and_its_line(self) -> None:
        run = self.broken
        self.assertEqual(run.calls[0], ("move", ["North"]), run.explain())
        message, line, file = run.error() or ["", 0, ""]
        self.assertTrue(message.startswith("SyntaxError: "), run.explain())
        self.assertIn("(tools.py, line 2)", message)
        self.assertEqual((line, file), (2, "tools"), run.explain())
        self.assertEqual(run.said(), [])

    def test_an_error_while_a_file_is_imported_names_that_file(self) -> None:
        run = self.import_crash
        self.assertEqual(run.error(), ["NameError: name 'undefined_thing' is not defined", 2, "tools"],
                         run.explain())

    def test_a_drone_runs_a_function_imported_from_another_file(self) -> None:
        spawns = [args for name, args in self.main.calls if name == "spawn_drone"]
        # By name when the entry has it under its own name - however it was
        # reached - and by file when it has it under another; globals as ever.
        self.assertEqual(spawns, [["column", [2], {}], ["tools.row", [], {"first": 1}],
                                  ["column", [1], {"first": 1, "second": 2}]], self.main.explain())
        first, second, third = self.drones
        # Each drone imports tools, which runs its top level; none runs the
        # entry's harvest().
        self.assertEqual(first.calls[0], ("quick_print", ["tools ran"]), first.explain())
        self.assertEqual(first.calls[1:-1], COLUMN_OF_TWO, first.explain())
        self.assertEqual(returned(first), [[7, 2]])
        self.assertEqual(names(second), ["quick_print", "move", "__return__"], second.explain())
        self.assertEqual(returned(second), ["row done"])
        self.assertEqual(names(third).count("harvest"), 1, third.explain())

    def test_wait_for_and_a_nested_function_from_another_file(self) -> None:
        said = self.main.said()
        self.assertEqual(said, ["tools ran", "(7, 2)", "row done", PY_REFUSAL], self.main.explain())
        self.assertEqual(self.main.code, 0, self.main.explain())


# ── JavaScript ──────────────────────────────────────────────────────────

JS_STORY = {
    "main": """\
import { harvestColumn, SIZE } from "./tools.js";
import * as tools from "./tools.js";
import { corner as where } from "./shapes.js";

harvestColumn(2);
quickPrint(SIZE, tools.SIZE, where().join(","));
""",
    "tools": """\
import { corner } from "./shapes.js";
export const SIZE = 3;
export function harvestColumn(n) {
  for (const i of range(n)) {
    harvest();
    move(North);
  }
  return corner();
}
""",
    "shapes": """\
export function corner() {
  return [getPosX(), getPosY()];
}
""",
}

JS_TEND = {
    "main": 'import { tend } from "./tools.js";\nmove(North);\ntend();\n',
    "tools": "export function tend() {\n  const x = 1;\n  return x + nothingHere;\n}\n",
}

JS_REFUSED = {
    "main": 'import * as tools from "./tools.js";\nmove(North);\ntools.tend();\n',
    "tools": "export function tend() {\n  petThePiggy();\n}\n",
}

JS_BROKEN = {
    "main": 'import { ok } from "./tools.js";\nok();\n',
    "tools": "export function ok() {}\nlet x = ;\n",
}

JS_IMPORT_CRASH = {
    "main": 'import "./tools.js";\nquickPrint("never");\n',
    "tools": "move(North);\nundefinedThing;\n",
}

#: Real ES modules want the .js: "./tools" is a file that is not there.
JS_NO_EXTENSION = {
    "main": 'move(North);\nimport { ok } from "./tools";\n',
    "tools": "export function ok() {}\n",
}

JS_NO_EXPORT = {
    "main": 'import { nope } from "./tools.js";\nmove(North);\n',
    "tools": "export function ok() {}\n",
}

JS_DRONES = {
    "main": """\
import { column, row as sideways } from "./tools.js";
import * as tools from "./tools.js";
export const LIMIT = 2;

harvest();
const first = spawnDrone(column, 2);
quickPrint(waitFor(first).join(","));
const second = spawnDrone(sideways);
quickPrint(waitFor(second));
const third = spawnDrone(tools.column, 1);
try {
  spawnDrone(tools.makeColumn());
} catch (error) {
  quickPrint(error.message);
}
""",
    # tools imports the file that runs, which imports tools: a drone's copy
    # of it - definitions only - is what tools gets.
    "tools": """\
import { corner } from "./shapes.js";
import { LIMIT } from "./main.js";
quickPrint("tools ran");
export function column(n) {
  for (const i of range(n)) {
    harvest();
    move(North);
  }
  return corner();
}
export function row() {
  move(East);
  return `row ${LIMIT}`;
}
export function makeColumn() {
  return function column() {};
}
""",
    "shapes": JS_STORY["shapes"],
}

JS_REFUSAL = "spawnDrone needs a function declared at the top level of your program, like function harvestColumn() { ... }"


def _no_module_hooks(folder: str) -> dict[str, str]:
    """An environment in which Node has no module.registerHooks, as before
    Node 22.15: a file Node loads first takes it away."""
    script = Path(folder, "no_hooks.cjs")
    script.write_text('delete require("module").registerHooks;\n', encoding="utf-8")
    # NODE_OPTIONS reads a backslash as an escape: the path goes with slashes.
    return {"NODE_OPTIONS": f'--require "{script.as_posix()}"'}


@unittest.skipUnless(HAS_NODE, "needs node")
class JavaScriptImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (cls.story, cls.tend, cls.refused, cls.broken, cls.import_crash, cls.no_extension,
         cls.no_export) = drive_all("javascript", JS_STORY, JS_TEND, JS_REFUSED, JS_BROKEN, JS_IMPORT_CRASH,
                                    JS_NO_EXTENSION, JS_NO_EXPORT)

    def test_a_function_from_another_file_sends_its_commands(self) -> None:
        run = self.story
        self.assertEqual(run.calls[:len(COLUMN_OF_TWO)], COLUMN_OF_TWO, run.explain())
        self.assertEqual(run.code, 0, run.explain())

    def test_files_import_files_and_see_the_farm_without_importing_it(self) -> None:
        self.assertEqual(self.story.said(), ["3 3 7,2"], self.story.explain())

    def test_an_error_in_another_file_names_that_file_and_its_line(self) -> None:
        run = self.tend
        self.assertEqual(run.calls[0], ("move", ["North"]))
        self.assertEqual(run.error(), ["ReferenceError: nothingHere is not defined", 3, "tools"], run.explain())
        self.assertEqual(run.code, 1)

    def test_a_refusal_in_another_file_names_that_file_and_its_line(self) -> None:
        self.assertEqual(self.refused.error(), ["nope", 2, "tools"], self.refused.explain())

    def test_a_file_that_does_not_compile_names_itself_and_its_line(self) -> None:
        # Nothing runs: a module that does not compile stops the whole program.
        run = self.broken
        self.assertEqual(run.calls, [("__error__", ["SyntaxError: Unexpected token ';'", 2, "tools"])],
                         run.explain())
        self.assertEqual(run.code, 1)

    def test_an_error_while_a_file_is_imported_names_that_file(self) -> None:
        run = self.import_crash
        self.assertEqual(run.calls, [("move", ["North"]),
                                     ("__error__", ["ReferenceError: undefinedThing is not defined", 2, "tools"])],
                         run.explain())

    def test_an_import_without_its_extension_says_what_to_write(self) -> None:
        # Imports come before anything runs, wherever they are written.
        run = self.no_extension
        self.assertEqual(len(run.calls), 1, run.explain())
        message, line, file = run.error() or ["", 0, ""]
        self.assertIn("Cannot find module 'tools' imported from main.js", message)
        self.assertIn('Did you mean to import "./tools.js"?', message)
        self.assertEqual((line, file), (2, "main"), run.explain())

    def test_an_import_of_a_name_not_exported_names_the_line(self) -> None:
        self.assertEqual(self.no_export.calls, [("__error__", [
            "SyntaxError: The requested module './tools.js' does not provide an export named 'nope'", 1, "main"])],
            self.no_export.explain())


@unittest.skipUnless(HAS_NODE, "needs node")
@unittest.skipUnless(TYPESCRIPT.is_file(), "needs TypeScript in web/node_modules")
class JavaScriptImportDroneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main, cls.drones = farm("javascript", JS_DRONES)

    def test_spawn_sends_the_name_a_drone_finds_it_by(self) -> None:
        # By name when the entry has it under its own name - however it was
        # reached - and by file when it has it under another.
        spawns = [args for name, args in self.main.calls if name == "spawn_drone"]
        self.assertEqual(spawns, [["column", [2], {}], ["tools.row", [], {}], ["column", [1], {}]],
                         self.main.explain())

    def test_a_drone_runs_a_function_imported_from_another_file(self) -> None:
        first, second, third = self.drones
        # Each drone imports tools, which runs its top level; none runs the
        # entry's harvest(), though tools imports the entry back.
        self.assertEqual(first.calls[0], ("quick_print", ["tools ran"]), first.explain())
        self.assertEqual(first.calls[1:-1], COLUMN_OF_TWO, first.explain())
        self.assertEqual(returned(first), [[7, 2]])
        self.assertEqual(names(second), ["quick_print", "move", "__return__"], second.explain())
        # LIMIT, a plain export of the entry, is in the drone's copy of it.
        self.assertEqual(returned(second), ["row 2"])
        self.assertEqual(names(third).count("harvest"), 1, third.explain())
        for drone in self.drones:
            self.assertEqual(drone.code, 0, drone.explain())

    def test_wait_for_and_a_nested_function_of_the_same_name(self) -> None:
        self.assertEqual(self.main.said(), ["tools ran", "7,2", "row 2", JS_REFUSAL], self.main.explain())
        self.assertEqual(self.main.code, 0, self.main.explain())

    def test_without_module_hooks_a_drone_still_runs(self) -> None:
        # Node before 22.15 has no module hooks: the drone's copy of the
        # entry - definitions only, so not its harvestColumn(2) - is a file
        # of its own beside the others.
        with tempfile.TemporaryDirectory(prefix="farm-no-hooks-", ignore_cleanup_errors=True) as folder:
            run, _ = farm("javascript", JS_STORY, job=job("tools.harvestColumn", [1]),
                          extra_env=_no_module_hooks(folder))
        self.assertEqual(run.calls[:-1], COLUMN_OF_TWO[:2] + COLUMN_OF_TWO[4:], run.explain())
        self.assertEqual(returned(run), [[7, 2]], run.explain())


# ── Dart ────────────────────────────────────────────────────────────────

DART_STORY = {
    "main": """\
import 'tools.dart';

void main() {
  harvestColumn(2);
  quickPrint('$size ${corner()}');
  final drone = spawnDrone(harvestColumn, [1])!;
  quickPrint('${waitFor(drone)}');
}
""",
    "tools": """\
import 'shapes.dart';
export 'shapes.dart' show corner;

const size = 3;

(int, int) harvestColumn(int n) {
  for (final _ in range(n)) {
    harvest();
    move(north);
  }
  return corner();
}
""",
    "shapes": "(int, int) corner() => (getPosX(), getPosY());\n",
}

DART_TEND = {
    "main": "import 'tools.dart';\n\nvoid main() {\n  move(north);\n  tend();\n}\n",
    "tools": "void tend() {\n  final xs = [1];\n  quickPrint('${xs[5]}');\n}\n",
}

DART_BROKEN = {
    "main": "import 'tools.dart';\n\nvoid main() {\n  tend();\n}\n",
    "tools": "void tend() {\n  harvest()\n}\n",
}


@unittest.skipUnless(HAS_DART, "needs dart")
class DartImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        (cls.main, cls.drones), (cls.tend, _), (cls.broken, _) = farm_all(
            "dart", (DART_STORY, None), (DART_TEND, None), (DART_BROKEN, None))

    def test_the_program_compiles_without_a_word(self) -> None:
        self.assertEqual(self.main.stderr.strip(), "", self.main.explain())

    def test_a_function_from_another_file_sends_its_commands(self) -> None:
        run = self.main
        self.assertEqual(run.calls[:len(COLUMN_OF_TWO)], COLUMN_OF_TWO, run.explain())

    def test_files_import_files_and_see_the_farm_without_importing_it(self) -> None:
        self.assertEqual(self.main.said(), ["3 (7, 2)", "[7, 2]"], self.main.explain())
        self.assertEqual(self.main.code, 0, self.main.explain())

    def test_a_drone_runs_a_function_from_another_file(self) -> None:
        spawns = [args for name, args in self.main.calls if name == "spawn_drone"]
        self.assertEqual(spawns, [["harvestColumn", [1], {}]], self.main.explain())
        (drone,) = self.drones
        self.assertEqual(drone.calls[:-1], COLUMN_OF_TWO[:2] + COLUMN_OF_TWO[4:], drone.explain())
        self.assertEqual(returned(drone), [[7, 2]], drone.explain())

    def test_an_error_in_another_file_names_that_file_and_its_line(self) -> None:
        run = self.tend
        message, line, file = run.error() or ["", 0, ""]
        self.assertTrue(message.startswith("RangeError"), run.explain())
        self.assertEqual((line, file), (3, "tools"), run.explain())
        self.assertEqual(run.calls[0], ("move", ["North"]))
        self.assertEqual(run.code, 1)

    def test_a_file_that_does_not_compile_is_named_on_stderr(self) -> None:
        # The compiler stops the program before the library could say a
        # word: the runner reads this line instead.
        run = self.broken
        self.assertEqual(run.calls, [], run.explain())
        self.assertNotEqual(run.code, 0)
        self.assertRegex(run.stderr, r"(?m)^tools\.dart:2:\d+: Error: ")


if __name__ == "__main__":
    unittest.main()
