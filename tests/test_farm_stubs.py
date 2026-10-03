"""The farm's libraries - Python, JavaScript and Dart - against a fake farm.

A Farm program runs as a real python, node or dart process and talks to
the farm over its stdin and stdout, one line per drone command (see
code_coach/farm/protocol.py). Here a small driver stands in for the farm:
it runs what render.prepare() describes in an empty folder, answers every
command from a canned table, and records what it was asked.

Each library is held to the same promises, in its own language's terms:

- commands go down the pipe under the game's Python names, with the game's
  own values: useItem(Items.WeirdSubstance, 3) in JavaScript is
  use_item ["Items.Weird_Substance", 3], as it is in Python and Dart;
- answers come back as the language's own values: an entity compares equal
  to Entities.Bush, a cost is indexed by an item, a companion unpacks;
- print and quick_print send text already formatted the language's way;
- {"e": ...} raises FarmError, which a program can catch, and which, not
  caught, ends it with __error__: the message, the line it happened on and
  the file it is in (by name - a program of one file is "main");
- any other crash reports the player's line and file too;
- {"stop": true} ends the program there and then, quietly.

Dart takes about two seconds to start, so its programs are few, each
covering a lot, and they run side by side.
"""

from __future__ import annotations

import json
import keyword
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from code_coach.engine import dart_path
from code_coach.farm import data, protocol
from code_coach.farm.stubs import render
from code_coach.farm.stubs.render import LANGUAGES, prepare

HAS_NODE = shutil.which("node") is not None
HAS_DART = dart_path() is not None
STUBS = Path(render.__file__).resolve().parent

GROUPS = {
    "Entities": data.ENTITIES,
    "Items": data.ITEMS,
    "Grounds": data.GROUNDS,
    "Unlocks": tuple(data.UNLOCKS),
    "Hats": data.HATS,
}


# ── The fake farm ───────────────────────────────────────────────────────

#: An answer that is not a line: the fake farm closes the pipe instead.
CLOSE = object()

ANSWERS: dict[str, Any] = {
    "harvest": True, "can_harvest": True, "plant": True, "move": True, "swap": True,
    "use_item": True, "unlock": True, "can_move": True,
    "get_entity_type": "Entities.Bush",
    "get_ground_type": "Grounds.Soil",
    "get_cost": {"Items.Hay": 5},
    "get_companion": ["Entities.Carrot", [3, 5]],
    "measure": [2, 4],
    "get_pos_x": 7, "get_pos_y": 2, "get_world_size": 3,
    "num_items": 12, "num_unlocked": 1,
    "get_time": 1.5, "get_tick_count": 3, "get_water": 0.25, "random": 0.5,
}


def canned(name: str, args: list) -> Any:
    """The fake farm's answer: pet_the_piggy is refused, do_a_flip stops the
    program, min/max/abs are worked out, and the rest come from ANSWERS."""
    if name == "pet_the_piggy":
        return protocol.refuse("nope")
    if name == "do_a_flip":
        return protocol.STOP
    if name in ("min", "max"):
        values = args[0] if len(args) == 1 and isinstance(args[0], list) else args
        return protocol.answer(min(values) if name == "min" else max(values))
    if name == "abs":
        return protocol.answer(abs(args[0]))
    return protocol.answer(ANSWERS.get(name))


@dataclass
class Run:
    calls: list[tuple[str, list]]
    output: list[str]
    stderr: str
    code: int | None
    timed_out: bool

    def said(self) -> list[str]:
        """Everything sent with quick_print, in order."""
        return [args[0] for name, args in self.calls if name == "quick_print"]

    def printed(self) -> list[str]:
        return [args[0] for name, args in self.calls if name == "print"]

    def error(self) -> list | None:
        """The [message, line, file] of the crash report, if there was one."""
        return next((args for name, args in self.calls if name == "__error__"), None)

    def explain(self) -> str:
        return f"exit {self.code}; calls {self.calls}; output {self.output}; stderr {self.stderr[-2000:]}"


def _kill(proc: subprocess.Popen) -> None:
    """Stop the program and anything it started: on Windows python.exe in a
    venv and Flutter's dart.bat each run the real program as a child."""
    if proc.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
    else:
        proc.kill()


def write_files(folder: str, files: dict[str, str]) -> None:
    """What prepare() says to write, as the runner writes it: a path may
    name a folder to make first."""
    for name, text in files.items():
        target = Path(folder, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")


def drive(language: str, code: str | dict[str, str], answers: Callable[[str, list], Any] = canned,
          *, limit: float = 30.0, entry: str = "main") -> Run:
    """Run a program - one file, or {name: code} run from entry - to the end
    against the fake farm."""
    files, argv, _ = prepare(language, code, entry)
    with tempfile.TemporaryDirectory(prefix="farm-stubs-", ignore_cleanup_errors=True) as folder:
        write_files(folder, files)
        proc = subprocess.Popen(argv, cwd=folder, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        timed_out = threading.Event()

        def give_up() -> None:
            timed_out.set()
            _kill(proc)

        watchdog = threading.Timer(limit, give_up)
        watchdog.daemon = True
        watchdog.start()
        # Read stderr alongside, so a program that writes a lot of it can
        # never block on a full pipe while this waits on stdout.
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
                if name == "__error__":  # the library's own: it does not wait
                    continue
                reply = answers(name, args)
                try:
                    if reply is CLOSE:
                        proc.stdin.close()
                    else:
                        proc.stdin.write((reply + "\n").encode("utf-8"))
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
    stderr = b"".join(errors).decode("utf-8", "replace")
    return Run(calls, output, stderr, code, timed_out.is_set())


def drive_all(language: str, *codes: str | dict[str, str], limit: float = 30.0) -> list[Run]:
    """Several programs at once: each one mostly waits for its process to start."""
    with ThreadPoolExecutor(len(codes)) as pool:
        return list(pool.map(lambda code: drive(language, code, limit=limit), codes))


def ends_when_killed(language: str, code: str) -> bool:
    """Whether killing the process prepare() names ends the program.

    The program sends one command, then keeps busy. Once that command has
    arrived the program is certainly running, and the process is killed the
    way a runner stops a program, with Popen.kill. Its output must then end.
    It would not if the real program were a child of the process killed -
    Flutter's dart.bat starts dart.exe that way - still running, and still
    holding the pipe open. (The busy loops give up after 20 seconds, so a
    program left behind by a failure here does not spin for ever.)
    """
    files, argv, _ = prepare(language, code)
    with tempfile.TemporaryDirectory(prefix="farm-stubs-", ignore_cleanup_errors=True) as folder:
        write_files(folder, files)
        proc = subprocess.Popen(argv, cwd=folder, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        watchdog = threading.Timer(60, _kill, (proc,))
        watchdog.daemon = True
        watchdog.start()
        try:
            proc.stdout.readline()  # the one command: it is running now
            proc.stdin.write((protocol.answer(None) + "\n").encode("utf-8"))
            proc.stdin.flush()
            time.sleep(0.2)
            proc.kill()
            ended = threading.Event()
            threading.Thread(target=lambda: (proc.stdout.read(), ended.set()), daemon=True).start()
            return ended.wait(10)
        finally:
            watchdog.cancel()
            _kill(proc)
            proc.wait()
            for pipe in (proc.stdin, proc.stdout):
                try:
                    pipe.close()
                except OSError:
                    pass


# ── One story, told in each language ────────────────────────────────────

#: How every language's story opens, on the wire.
OPENING = [
    ("move", ["North"]),
    ("move", ["East"]),
    ("move", ["South"]),
    ("move", ["West"]),
    ("plant", ["Entities.Bush"]),
    ("use_item", ["Items.Weird_Substance", 3]),
]

PYTHON_STORY = """\
move(North)
move(East)
move(South)
move(West)
plant(Entities.Bush)
use_item(Items.Weird_Substance, 3)
quick_print(get_entity_type() == Entities.Bush, get_entity_type() == Entities.Tree)
cost = get_cost(Entities.Carrot)
quick_print(cost[Items.Hay])
kind, (x, y) = get_companion()
quick_print(kind == Entities.Carrot, x, y)
quick_print(measure() == (2, 4))
quick_print(min([3, 1, 2]), max(4, 9))
print(1, "a")
try:
    pet_the_piggy()
except FarmError as error:
    quick_print("caught", error)
do_a_flip()
quick_print("after the stop")
"""

JS_STORY = """\
move(North);
move(East);
move(South);
move(West);
plant(Entities.Bush);
useItem(Items.WeirdSubstance, 3);
quickPrint(getEntityType() === Entities.Bush, getEntityType() === Entities.Tree);
const cost = getCost(Entities.Carrot);
quickPrint(cost[Items.Hay]);
const [kind, [x, y]] = getCompanion();
quickPrint(kind === Entities.Carrot, x, y);
const [mx, my] = measure();
quickPrint(mx, my);
quickPrint(min([3, 1, 2]), max(4, 9));
print(1, "a");
console.log("log", [1, 2]);
quickPrint(range(3), range(1, 7, 2), range(3, 0, -1));
quickPrint(Hats.DinosaurHat, [...Grounds].join("/"));
try {
  petThePiggy();
} catch (error) {
  quickPrint(error instanceof FarmError, error.message);
}
doAFlip();
quickPrint("after the stop");
"""

DART_STORY = """\
void main() {
  move(north);
  move(east);
  move(south);
  move(west);
  plant(Entities.bush);
  useItem(Items.weirdSubstance, 3);
  quickPrint('${getEntityType() == Entities.bush} ${getEntityType() == Entities.tree}');
  final cost = getCost(Entities.carrot)!;
  quickPrint(cost[Items.hay]);
  final (kind, (x, y)) = getCompanion()!;
  quickPrint('${kind == Entities.carrot} $x $y');
  final (mx, my) = measure() as (int, int);
  quickPrint('$mx $my');
  quickPrint('${min([3, 1, 2])} ${max(4, 9)}');
  print('x 1');
  quickPrint('${range(3)} ${range(1, 7, 2)} ${range(3, 0, -1)}');
  quickPrint('${Hats.dinosaurHat.wire} ${getGroundType() == Grounds.soil}');
  try {
    petThePiggy();
  } on FarmError catch (error) {
    quickPrint('caught ${error.message}');
  }
  doAFlip();
  quickPrint('after the stop');
}
"""


class _Story:
    """What every language's story must show. Each subclass runs its STORY
    once (in setUpClass, as `story`) and says what it should have said."""

    LANGUAGE = ""
    SAID: list[str] = []
    PRINTED: list[str] = []
    #: Sends one command, then keeps busy for 20 seconds without another.
    BUSY = ""
    story: Run

    def test_commands_go_by_their_game_names(self) -> None:
        run = self.story
        self.assertFalse(run.timed_out, run.explain())
        self.assertEqual(run.calls[:len(OPENING)], OPENING, run.explain())
        self.assertIn(("get_cost", ["Entities.Carrot"]), run.calls)
        self.assertIn(("min", [[3, 1, 2]]), run.calls)
        self.assertIn(("max", [4, 9]), run.calls)

    def test_answers_come_back_as_the_languages_own_values(self) -> None:
        # Enum equality, a cost indexed by an item, a companion and a
        # measurement unpacked, min and max, range, a caught FarmError -
        # each reported with quick_print, in order. "after the stop" is not
        # among them: the farm stopped the program before it got there.
        self.assertEqual(self.story.said(), self.SAID, self.story.explain())

    def test_print_sends_the_text_formatted(self) -> None:
        self.assertEqual(self.story.printed(), self.PRINTED, self.story.explain())

    def test_stop_ends_the_program_quietly(self) -> None:
        run = self.story
        self.assertEqual(run.calls[-1], ("do_a_flip", []), run.explain())
        self.assertEqual(run.code, 0, run.explain())
        self.assertIsNone(run.error())
        self.assertEqual(run.output, [])

    def test_killing_the_process_ends_the_program(self) -> None:
        # How a runner stops a loop that never asks the farm anything.
        self.assertTrue(ends_when_killed(self.LANGUAGE, self.BUSY),
                        "the program outlived the process that was killed")


class PythonTests(_Story, unittest.TestCase):
    LANGUAGE = "python"
    SAID = ["True False", "5", "True 3 5", "True", "1 9", "caught nope"]
    PRINTED = ["1 a"]
    BUSY = "import time\nquick_print('go')\nend = time.time() + 20\nwhile time.time() < end:\n    pass\n"

    @classmethod
    def setUpClass(cls) -> None:
        cls.story, cls.refused, cls.crashed = drive_all(
            "python",
            PYTHON_STORY,
            "move(North)\npet_the_piggy()\nquick_print('never')\n",
            "move(North)\n\nundefined_name()\n",
        )

    def test_an_uncaught_farm_error_reports_your_line(self) -> None:
        run = self.refused
        self.assertEqual(run.error(), ["nope", 2, "main"], run.explain())
        self.assertEqual(run.code, 1)
        self.assertEqual(run.said(), [])

    def test_a_crash_reports_your_line(self) -> None:
        run = self.crashed
        self.assertEqual(run.error(), ["NameError: name 'undefined_name' is not defined", 3, "main"],
                         run.explain())
        self.assertEqual(run.code, 1)

    def test_a_closed_pipe_ends_the_program_quietly(self) -> None:
        run = drive("python", "move(North)\nquick_print('never')\n",
                    lambda name, args: CLOSE)
        self.assertEqual(run.calls, [("move", ["North"])], run.explain())
        self.assertEqual(run.code, 0, run.explain())


@unittest.skipUnless(HAS_NODE, "needs node")
class JavaScriptTests(_Story, unittest.TestCase):
    LANGUAGE = "javascript"
    SAID = [
        "true false", "5", "true 3 5", "2 4", "1 9",
        "log [ 1, 2 ]",  # console.log is quick_print, in console.log's own format
        "0,1,2 1,3,5 3,2,1",
        "Hats.Dinosaur_Hat Grounds.Grassland/Grounds.Soil",
        "true nope",
    ]
    PRINTED = ["1 a"]
    BUSY = "quickPrint('go');\nconst end = Date.now() + 20000;\nwhile (Date.now() < end) {}\n"

    @classmethod
    def setUpClass(cls) -> None:
        names = [f.js for f in protocol.FUNCTIONS]
        cls.story, cls.refused, cls.crashed, cls.broken, cls.later, cls.names = drive_all(
            "javascript",
            JS_STORY,
            "function tend() {\n  petThePiggy();\n}\nmove(North);\ntend();\nquickPrint('never');\n",
            "move(North);\n\nundefinedName();\n",
            "move(North);\nlet x = ;\n",
            "setTimeout(() => {\n  petThePiggy();\n}, 0);\n",
            f"const names = {json.dumps(names)};\n"
            "quickPrint(names.filter((n) => typeof globalThis[n] !== 'function').join(','));\n"
            "quickPrint(JSON.stringify({ North, East, South, West, Entities, Items, Grounds, Unlocks, Hats }));\n",
        )

    def test_an_uncaught_farm_error_reports_your_line(self) -> None:
        run = self.refused
        self.assertEqual(run.error(), ["nope", 2, "main"], run.explain())
        self.assertEqual(run.code, 1)
        self.assertEqual(run.said(), [])

    def test_a_crash_reports_your_line(self) -> None:
        run = self.crashed
        self.assertEqual(run.error(), ["ReferenceError: undefinedName is not defined", 3, "main"], run.explain())
        self.assertEqual(run.code, 1)

    def test_a_syntax_error_reports_your_line_before_anything_runs(self) -> None:
        run = self.broken
        self.assertEqual(run.calls, [("__error__", ["SyntaxError: Unexpected token ';'", 2, "main"])],
                         run.explain())
        self.assertEqual(run.code, 1)

    def test_a_crash_in_a_timer_is_reported_too(self) -> None:
        self.assertEqual(self.later.error(), ["nope", 2, "main"], self.later.explain())

    def test_every_name_is_a_global(self) -> None:
        missing, values = self.names.said()
        self.assertEqual(missing, "", "functions missing")
        expected: dict[str, Any] = {d: d for d in data.DIRECTIONS}
        for title, members in GROUPS.items():
            expected[title] = {protocol.js_member(m): f"{title}.{m}" for m in members}
        self.assertEqual(json.loads(values), expected)

    def test_a_closed_pipe_ends_the_program_quietly(self) -> None:
        run = drive("javascript", "move(North);\nquickPrint('never');\n",
                    lambda name, args: CLOSE)
        self.assertEqual(run.calls, [("move", ["North"])], run.explain())
        self.assertEqual(run.code, 0, run.explain())


@unittest.skipUnless(HAS_DART, "needs dart")
class DartTests(_Story, unittest.TestCase):
    LANGUAGE = "dart"
    SAID = [
        "true false", "5", "true 3 5", "2 4", "1 9",
        "[0, 1, 2] [1, 3, 5] [3, 2, 1]",
        "Hats.Dinosaur_Hat true",
        "caught nope",
    ]
    PRINTED = ["x 1"]
    BUSY = ("void main() {\n  quickPrint('go');\n  final watch = Stopwatch()..start();\n"
            "  while (watch.elapsedMilliseconds < 20000) {}\n}\n")

    @classmethod
    def setUpClass(cls) -> None:
        cls.story, cls.refused, cls.crashed = drive_all(
            "dart",
            DART_STORY,
            "void tend() {\n  petThePiggy();\n}\n\nvoid main() {\n  move(north);\n  tend();\n"
            "  quickPrint('never');\n}\n",
            "void main() {\n  final rows = [1, 2, 3];\n  move(north);\n  quickPrint(rows[5]);\n}\n",
            limit=120.0,
        )

    def test_the_library_compiles_without_a_word(self) -> None:
        # Anything the compiler says about the library itself - a warning
        # included - would land in front of the player on every run.
        self.assertEqual(self.story.stderr.strip(), "", self.story.explain())

    def test_an_uncaught_farm_error_reports_your_line(self) -> None:
        run = self.refused
        self.assertEqual(run.error(), ["nope", 2, "main"], run.explain())
        self.assertEqual(run.code, 1)
        self.assertEqual(run.said(), [])

    def test_a_crash_reports_your_line(self) -> None:
        run = self.crashed
        message, line, file = run.error() or ["", 0, ""]
        self.assertTrue(message.startswith("RangeError"), run.explain())
        self.assertEqual(line, 4, run.explain())
        self.assertEqual(file, "main", run.explain())
        self.assertEqual(run.calls[0], ("move", ["North"]))
        self.assertEqual(run.code, 1)


# ── The files themselves ────────────────────────────────────────────────

#: Words a Dart enum value cannot be called: the reserved words, and the
#: names every enum already has.
DART_FORBIDDEN = {
    "assert", "break", "case", "catch", "class", "const", "continue", "default", "do",
    "else", "enum", "extends", "false", "final", "finally", "for", "if", "in", "is",
    "new", "null", "rethrow", "return", "super", "switch", "this", "throw", "true",
    "try", "var", "void", "while", "with",
    "values", "index", "hashCode", "runtimeType", "noSuchMethod", "toString",
}


class RenderTests(unittest.TestCase):
    def test_prepare_describes_each_language(self) -> None:
        # The library first; then the rest of the farm's files and the player's.
        cases = {
            # The game's own language: the interpreter, with your files in files/.
            "original": (["farm_lang.py", "files/main.py"], ["-u", "farm_lang.py", "main"], "files/main.py"),
            "python": (["farm/farm_api.py", "main.py"], ["-u", "farm/farm_api.py", "main"], "main.py"),
            "javascript": (["farm_api.cjs", "package.json", "main.js"], ["farm_api.cjs", "main"], "main.js"),
            "dart": (["farm_api.dart", "runner.dart", "main.dart"], ["run", "runner.dart"], "main.dart"),
        }
        self.assertEqual(tuple(cases), LANGUAGES)
        for language, (names, args, code_name) in cases.items():
            if (language == "javascript" and not HAS_NODE) or (language == "dart" and not HAS_DART):
                continue
            with self.subTest(language=language):
                files, argv, where = prepare(language, "one\ntwo\n")
                self.assertEqual(sorted(files), sorted(names))
                self.assertEqual(argv[1:], args)
                self.assertTrue(Path(argv[0]).is_file(), argv[0])
                self.assertEqual(where, {"main": code_name})
                self.assertIn("NAMES-START", files[names[0]])
                # The player's file keeps every line where they wrote it.
                self.assertEqual(files[code_name].splitlines()[1:], ["two"])
                self.assertTrue(files[code_name].splitlines()[0].endswith("one"))
        with self.assertRaises(ValueError):
            prepare("cobol", "")

    def test_python_names_are_the_games_own(self) -> None:
        namespace: dict[str, Any] = {"__name__": "farm_api_under_test"}
        exec(compile(render.library("python"), "farm_api.py", "exec"), namespace)
        self.assertEqual(namespace["DIRECTIONS"], list(data.DIRECTIONS))
        self.assertEqual(namespace["GROUPS"], {t: list(m) for t, m in GROUPS.items()})
        api = namespace["_api"]()
        for f in protocol.FUNCTIONS:
            self.assertTrue(callable(api[f.py]), f.py)
        self.assertEqual(str(api["Items"].Weird_Substance), "Items.Weird_Substance")

    def test_dart_names_are_every_name_in_data(self) -> None:
        source = render.library("dart")
        for d in data.DIRECTIONS:
            self.assertIn(f"  {protocol.dart_member(d)}('{d}')", source)
        for title, members in GROUPS.items():
            for m in members:
                self.assertIn(f"  {protocol.dart_member(m)}('{title}.{m}')", source)

    def test_dart_has_every_command_under_its_wire_name(self) -> None:
        # The Dart functions are written by hand, to give each its type, so
        # this holds them to protocol.FUNCTIONS: each is declared under its
        # Dart name and sends its Python name. print is dart:core's own,
        # which the zone in runFarmProgram sends as 'print'.
        source = (STUBS / "farm_api.dart").read_text(encoding="utf-8")
        self.assertIn("_call('print', [line])", source)
        for f in protocol.FUNCTIONS:
            if f.dart == "print":
                continue
            with self.subTest(function=f.dart):
                declared = re.search(rf"(?m)^(?!//)\S[^\n]*\b{f.dart}\(", source)
                self.assertIsNotNone(declared, f"no top-level {f.dart}() in farm_api.dart")
                sent = re.compile(r"\b(?:_call|_extreme)\('(\w+)'").search(source, declared.end())
                self.assertEqual(sent and sent.group(1), f.py)

    def test_every_name_can_be_spelled_in_every_language(self) -> None:
        identifier = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
        for title, members in {"Directions": data.DIRECTIONS, **GROUPS}.items():
            with self.subTest(group=title):
                py = list(members)
                js = [protocol.js_member(m) for m in members]
                dart = [protocol.dart_member(m) for m in members]
                for spelled in (py, js, dart):
                    self.assertEqual(len(set(spelled)), len(spelled), f"two names collide: {spelled}")
                    for name in spelled:
                        self.assertRegex(name, identifier)
                self.assertFalse([n for n in py if keyword.iskeyword(n)])
                self.assertFalse(DART_FORBIDDEN & set(dart), "not allowed as a Dart enum value")


if __name__ == "__main__":
    unittest.main()
