"""The farm's language gate: code that uses a part of the language you have
not bought is stopped before it runs, with the line and the unlock it needs.

Every feature, in every language, is held to the same two promises. A
snippet that uses it is stopped at the right line while the feature is
locked - and nothing else in the snippet is flagged, so each case also
proves the gate sees only what is there. Then, the moment the feature is
bought, the same snippet passes.

After those come the programs the gate must never stop: ones that are
legal with the few unlocks you have early on. A false positive blocks a
program that is fine, with no way round it, so these matter most - and
they are where Dart, read without a parser, is most at risk: List<int> is
no comparison, `Entities? e` no conditional, and a block no dictionary.
"""

from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path
from unittest import mock

from code_coach.farm import gate
from code_coach.farm.data import LANGUAGE_FEATURES, UNLOCKS
from code_coach.farm.gate import Violation, check, unlock_for

ALL = frozenset(LANGUAGE_FEATURES)
HAS_JS = shutil.which("node") is not None and gate.TYPESCRIPT.is_dir()


def _dart(body: str) -> str:
    """A Dart program: `body`, which starts on line 2, inside main()."""
    return "void main() {\n" + body + "\n}\n"


# (feature, code, line it is used on, the other features the code uses)
PYTHON = [
    ("while", "harvest()\nwhile True:\n    harvest()\n", 2, ()),
    ("if", "if can_harvest():\n    harvest()\n", 1, ()),
    ("if", "if can_harvest():\n    harvest()\nelif can_harvest():\n    do_a_flip()\n", 3, ()),
    ("if", "harvest() if can_harvest() else do_a_flip()\n", 1, ()),
    ("if", "match get_entity_type():\n    case Entities.Bush:\n        harvest()\n", 1, ()),
    ("if", "print([i for i in range(3) if can_harvest()])\n", 1, ("for", "lists")),
    ("for", "harvest()\nfor i in range(3):\n    harvest()\n", 2, ()),
    ("for", "for x, y in ((0, 1), (1, 0)):\n    harvest()\n", 1, ()),
    ("for", "print(sum(i for i in range(3)))\n", 1, ()),
    ("operators", "print(1 + 2)\n", 1, ()),
    ("operators", "harvest()\nprint(get_pos_x() == 0)\n", 2, ()),
    ("operators", "print(can_harvest() and True)\n", 1, ()),
    ("operators", "print(not can_harvest())\n", 1, ()),
    ("operators", "print(-get_pos_x())\n", 1, ()),
    ("operators", "print(2 ** 3 // 1 % 5)\n", 1, ()),
    ("operators", 'print(f"{get_pos_x() + 1}")\n', 1, ()),
    ("operators", "x = 1\nx += 1\n", 2, ("variables",)),
    ("variables", "harvest()\nx = 3\nprint(x)\n", 2, ()),
    ("variables", "size: int = get_world_size()\n", 1, ()),
    ("variables", "print(n := get_world_size())\n", 1, ()),
    ("variables", "x = 1\nx += 1\n", 2, ("operators",)),
    ("functions", "def go():\n    harvest()\ngo()\n", 1, ()),
    ("functions", "harvest()\ngo = lambda: harvest()\n", 2, ("variables",)),
    ("functions", "class Drone:\n    pass\n", 1, ()),
    ("lists", "print([1, 2])\n", 1, ()),
    ("lists", "print([i for i in range(3)])\n", 1, ("for",)),
    ("lists", "print(list(range(3)))\n", 1, ()),
    ("lists", "print(get_companion()[0])\n", 1, ()),
    ("dicts", "print({Items.Hay: 1})\n", 1, ()),
    ("dicts", "print({1, 2})\n", 1, ()),
    ("dicts", "print(set())\n", 1, ()),
    ("dicts", "print({i: 0 for i in range(3)})\n", 1, ("for",)),
    ("import", "import math\n", 1, ()),
    ("import", "harvest()\nfrom math import sqrt\n", 2, ()),
]

JAVASCRIPT = [
    ("while", "harvest();\nwhile (true) {\n  harvest();\n}\n", 2, ()),
    ("while", "do {\n  harvest();\n} while (canHarvest());\n", 1, ()),
    ("if", "if (canHarvest()) {\n  harvest();\n}\n", 1, ()),
    ("if", "if (canHarvest()) {\n  harvest();\n} else if (canHarvest()) {\n  doAFlip();\n}\n", 3, ()),
    ("if", "canHarvest() ? harvest() : doAFlip();\n", 1, ()),
    ("if", "switch (getEntityType()) {\n  case Entities.Bush:\n    harvest();\n}\n", 1, ()),
    ("for", "harvest();\nfor (const i of range(3)) {\n  harvest();\n}\n", 2, ()),
    ("for", "for (const k in Entities) {\n  harvest();\n}\n", 1, ()),
    ("for", "for (const [x, y] of pairs()) {\n  harvest();\n}\n", 1, ()),
    ("for", "for (let i = 0; i < 3; i++) {\n  harvest();\n}\n", 1, ("variables", "operators")),
    ("operators", "print(1 + 2);\n", 1, ()),
    ("operators", "harvest();\nprint(getPosX() === 0);\n", 2, ()),
    ("operators", "print(canHarvest() && true);\n", 1, ()),
    ("operators", "print(!canHarvest());\n", 1, ()),
    ("operators", "print(-getPosX());\n", 1, ()),
    ("operators", "print(getEntityType() ?? Entities.Grass);\n", 1, ()),
    ("operators", "print(`at ${getPosX() + 1}`);\n", 1, ()),
    ("operators", "x += 1;\n", 1, ("variables",)),
    ("variables", "harvest();\nlet x = 3;\nprint(x);\n", 2, ()),
    ("variables", "const size = getWorldSize();\n", 1, ()),
    ("variables", "x = 3;\n", 1, ()),
    ("variables", "x += 1;\n", 1, ("operators",)),
    ("variables", "x++;\n", 1, ("operators",)),
    ("functions", "function go() {\n  harvest();\n}\ngo();\n", 1, ()),
    ("functions", "const go = () => harvest();\n", 1, ("variables",)),
    ("functions", "[1].forEach(function (x) {\n  print(x);\n});\n", 1, ("lists",)),
    ("functions", "class Drone {}\n", 1, ()),
    ("lists", "print([1, 2]);\n", 1, ()),
    ("lists", "print(getCompanion()[0]);\n", 1, ()),
    ("lists", "print(new Array(3));\n", 1, ()),
    ("dicts", "print({ hay: 1 });\n", 1, ()),
    ("dicts", "print(new Map());\n", 1, ()),
    ("dicts", "print(new Set());\n", 1, ()),
    ("import", "require('fs');\n", 1, ()),
    ("import", "harvest();\nimport('fs');\n", 2, ()),
    ("import", "import fs from 'fs';\n", 1, ()),
]

DART = [
    ("while", _dart("  harvest();\n  while (true) {\n    harvest();\n  }"), 3, ()),
    ("while", _dart("  do {\n    harvest();\n  } while (canHarvest());"), 2, ()),
    ("if", _dart("  if (canHarvest()) {\n    harvest();\n  }"), 2, ()),
    ("if", _dart("  if (canHarvest()) {\n    harvest();\n  } else if (canHarvest()) {\n    doAFlip();\n  }"), 4, ()),
    ("if", _dart("  switch (getEntityType()) {\n    case Entities.bush:\n      harvest();\n  }"), 2, ()),
    ("for", _dart("  harvest();\n  for (final i in range(3)) {\n    harvest();\n  }"), 3, ()),
    ("for", _dart("  for (var i in range(3)) {\n    harvest();\n  }"), 2, ()),
    ("for", _dart("  for (int i in range(3)) {\n    harvest();\n  }"), 2, ()),
    ("for", _dart("  for (var i = 0; i < 3; i++) {\n    harvest();\n  }"), 2, ("variables", "operators")),
    ("operators", _dart("  print(1 + 2);"), 2, ()),
    ("operators", _dart("  harvest();\n  print(getPosX() == 0);"), 3, ()),
    ("operators", _dart("  print(canHarvest() && true);"), 2, ()),
    ("operators", _dart("  print(!canHarvest());"), 2, ()),
    ("operators", _dart("  print(-getPosX());"), 2, ()),
    ("operators", _dart("  print(1 - 1);"), 2, ()),
    ("operators", _dart("  print(7 ~/ 2);"), 2, ()),
    ("operators", _dart("  print(getEntityType() ?? Entities.grass);"), 2, ()),
    ("operators", _dart("  print(getPosX() < getWorldSize());"), 2, ()),
    ("operators", _dart("  print(getPosX() > 1);"), 2, ()),
    ("operators", _dart("  print(getEntityType() is Entities);"), 2, ()),
    ("operators", _dart("  print('at ${getPosX() + 1}');"), 2, ()),
    ("operators", _dart("  size += 1;"), 2, ("variables",)),
    ("variables", _dart("  harvest();\n  var x = 3;\n  print(x);"), 3, ()),
    ("variables", _dart("  final size = getWorldSize();"), 2, ()),
    ("variables", _dart("  int size = getWorldSize();"), 2, ()),
    ("variables", _dart("  int size;"), 2, ()),
    ("variables", _dart("  late int size;"), 2, ()),
    ("variables", _dart("  Entities? e = getEntityType();"), 2, ()),
    ("variables", _dart("  size = 3;"), 2, ()),
    ("variables", _dart("  size += 1;"), 2, ("operators",)),
    ("variables", _dart("  size++;"), 2, ("operators",)),
    ("functions", "void go() {\n  harvest();\n}\n\nvoid main() {\n  go();\n}\n", 1, ()),
    ("functions", _dart("  harvest();\n  void go() {\n    harvest();\n  }\n  go();"), 3, ()),
    ("functions", _dart("  var go = () => harvest();"), 2, ("variables",)),
    ("functions", _dart("  [1].forEach((x) {\n    print(x);\n  });"), 2, ("lists",)),
    ("functions", "int get size => 3;\n\nvoid main() {\n  print(size);\n}\n", 1, ()),
    ("functions", "class Drone {}\n\nvoid main() {\n  harvest();\n}\n", 1, ()),
    ("lists", _dart("  print([1, 2]);"), 2, ()),
    ("lists", _dart("  print(getCompanion()[0]);"), 2, ()),
    ("lists", _dart("  print(List.filled(3, 0));"), 2, ()),
    ("lists", _dart("  print(<int>[]);"), 2, ()),
    ("dicts", _dart("  print({Items.hay: 1});"), 2, ()),
    ("dicts", _dart("  print({1, 2});"), 2, ()),
    ("dicts", _dart("  print(<Items, int>{});"), 2, ()),
    ("dicts", _dart("  print(Map());"), 2, ()),
    ("dicts", _dart("  print(Set<int>());"), 2, ()),
    ("dicts", _dart("  print('${{1: 2}}');"), 2, ()),
    ("import", "import 'dart:math';\n\nvoid main() {\n  harvest();\n}\n", 1, ()),
]

#: A program that uses every feature, for the languages that have each one.
EVERYTHING = {
    "python": (
        "import math\n"
        "def go(n):\n"
        "    xs = [n, {1: 2}]\n"
        "    while xs:\n"
        "        for x in xs:\n"
        "            if x + 1:\n"
        "                harvest()\n"
        "        break\n"
    ),
    "javascript": (
        "const fs = require('fs');\n"
        "function go(n) {\n"
        "  const xs = [n, { a: 2 }];\n"
        "  while (xs) {\n"
        "    for (const x of xs) {\n"
        "      if (x + 1) {\n"
        "        harvest();\n"
        "      }\n"
        "    }\n"
        "    break;\n"
        "  }\n"
        "}\n"
    ),
    "dart": (
        "import 'dart:math';\n"
        "void go(int n) {\n"
        "  var xs = [n, {1: 2}];\n"
        "  while (true) {\n"
        "    for (final x in xs) {\n"
        "      if (n + 1 > 0) {\n"
        "        harvest();\n"
        "      }\n"
        "    }\n"
        "  }\n"
        "}\n"
        "void main() {\n"
        "  go(1);\n"
        "}\n"
    ),
}


class _GateCase(unittest.TestCase):
    language = ""

    def holds(self, feature: str, code: str, line: int, needs: tuple[str, ...]) -> None:
        """Locked: stopped at `line`, and nothing else stopped. Bought: passes."""
        allowed = set(needs)
        found = check(code, self.language, allowed)
        self.assertIn((feature, line), [(v.feature, v.line) for v in found], found)
        self.assertEqual({v.feature for v in found}, {feature}, found)
        for v in found:
            self.assertTrue(v.snippet and v.message, v)
        self.assertEqual(check(code, self.language, allowed | {feature}), [])

    def passes(self, code: str, unlocked: set[str]) -> None:
        self.assertEqual(check(code, self.language, unlocked), [])


class PythonFeatures(_GateCase):
    language = "python"

    def test_each_feature_is_stopped_while_locked_and_passes_once_bought(self):
        for feature, code, line, needs in PYTHON:
            with self.subTest(feature=feature, code=code):
                self.holds(feature, code, line, needs)

    def test_a_dictionary_key_passes_with_dictionaries_bought(self):
        # get_cost() gives a dictionary; a[i] could be that, so it passes.
        code = "print(get_cost(Entities.Carrot)[Items.Hay])\n"
        self.passes(code, {"dicts"})
        [v] = check(code, "python", set())
        self.assertEqual(v.feature, "lists")
        self.assertEqual(v.message, "Indexing with `[ ]` needs Lists or Dictionaries - buy one in the research tree.")

    def test_parameters_and_loop_variables_are_not_variables(self):
        self.passes("def go(times=3):\n    harvest()\n", {"functions"})
        self.passes("print(lambda x: x)\n", {"functions"})
        self.passes("print([x for x in range(3)])\n", {"for", "lists"})
        self.passes("for i in range(3):\n    move(North)\n", {"for"})

    def test_type_annotations_are_not_code(self):
        code = (
            "def at(x: int | None) -> tuple[int, int]:\n"
            "    return (0, 0)\n"
            "where: list[int] = at(None)\n"
        )
        self.passes(code, {"functions", "variables"})


class JavaScriptFeatures(_GateCase):
    language = "javascript"

    def setUp(self):
        if not HAS_JS:
            self.skipTest("needs node and web/node_modules/typescript")

    def test_each_feature_is_stopped_while_locked_and_passes_once_bought(self):
        for feature, code, line, needs in JAVASCRIPT:
            with self.subTest(feature=feature, code=code):
                self.holds(feature, code, line, needs)

    def test_a_dictionary_key_passes_with_dictionaries_bought(self):
        code = "print(getCost(Entities.Carrot)[Items.Hay]);\n"
        self.passes(code, {"dicts"})
        self.assertEqual([v.feature for v in check(code, "javascript", set())], ["lists"])

    def test_parameters_and_loop_variables_are_not_variables(self):
        self.passes("function go(times = 1) {\n  harvest();\n}\n", {"functions"})
        self.passes("for (const i of range(3)) {\n  move(North);\n}\n", {"for"})

    def test_a_catch_binding_is_not_a_variable(self):
        self.passes("try {\n  harvest();\n} catch (e) {\n  doAFlip();\n}\n", set())

    def test_typescript_written_into_javascript_is_a_syntax_error_not_ours(self):
        self.assertEqual(check("let x: number = 1;\nwhile (true) {}\n", "javascript", set()), [])

    def test_without_node_or_typescript_nothing_is_blocked(self):
        code = "while (true) { harvest(); }\n"
        with mock.patch("code_coach.farm.gate.shutil.which", return_value=None):
            self.assertEqual(check(code, "javascript", set()), [])
        with mock.patch.object(gate, "TYPESCRIPT", Path("no/such/typescript")):
            self.assertEqual(check(code, "javascript", set()), [])

    def test_the_helper_answers_null_when_typescript_will_not_load(self):
        done = subprocess.run(
            [shutil.which("node"), str(gate.GATE_JS), "no/such/typescript"],
            input=b"while (true) {}", capture_output=True, timeout=30,
        )
        self.assertEqual(done.stdout.decode().strip(), "null")


class DartFeatures(_GateCase):
    language = "dart"

    def test_each_feature_is_stopped_while_locked_and_passes_once_bought(self):
        for feature, code, line, needs in DART:
            with self.subTest(feature=feature, code=code):
                self.holds(feature, code, line, needs)

    def test_a_dictionary_key_passes_with_dictionaries_bought(self):
        for code in (
            _dart("  print(getCost(Entities.carrot)[Items.hay]);"),
            _dart("  print(getCost(Entities.carrot)?[Items.hay]);"),
        ):
            with self.subTest(code=code):
                self.passes(code, {"dicts"})
                self.assertEqual([v.feature for v in check(code, "dart", set())], ["lists"])

    def test_main_is_the_program_not_a_function(self):
        for code in (
            "void main() {\n  harvest();\n}\n",
            "main() {\n  harvest();\n}\n",
            "void main() => harvest();\n",
            "Future<void> main() async {\n  harvest();\n}\n",
            "void main(List<String> args) {\n  harvest();\n}\n",
        ):
            with self.subTest(code=code):
                self.passes(code, set())

    def test_generic_types_are_not_comparisons(self):
        code = _dart(
            "  List<int> xs = [1, 2, 3];\n"
            "  List<List<int>> grid = [[1], [2]];\n"
            "  Map<Items, num>? costs;\n"
            "  var ys = <int>[];\n"
            "  Set<Entities>? seen;\n"
            "  print(xs[0] + grid[0][0]);\n"
            "  print(List<int>.filled(2, 0));\n"
            "  print(xs is List<int>);"
        )
        found = check(code, "dart", {"variables", "lists"})
        # Only the + on line 7 and the `is` on line 9 are operators.
        self.assertEqual([(v.feature, v.line) for v in found], [("operators", 7), ("operators", 9)])
        self.passes(_dart("  Map<String, List<int>> m = {};\n  print(m);"), {"variables", "dicts"})
        self.passes("T first<T>(List<T> xs) => xs[0];\n" + _dart("  print(first([1]));"), {"functions", "lists"})

    def test_a_nullable_type_is_only_a_variable(self):
        for code in (_dart("  Entities? e = getEntityType();"), _dart("  int? size;")):
            with self.subTest(code=code):
                self.assertEqual([v.feature for v in check(code, "dart", set())], ["variables"])

    def test_blocks_are_not_dictionaries(self):
        self.passes(_dart("  if (canHarvest()) {\n    harvest();\n  } else {\n    doAFlip();\n  }"), {"if"})
        self.passes(_dart("  do {\n    harvest();\n  } while (true);"), {"while"})
        self.passes(_dart("  try {\n    harvest();\n  } catch (e) {\n    doAFlip();\n  } finally {\n    doAFlip();\n  }"), set())
        self.passes(_dart("  {\n    harvest();\n  }"), set())
        self.passes(
            _dart("  switch (getEntityType()) {\n    case Entities.bush: {\n      harvest();\n    }\n    default:\n      doAFlip();\n  }"),
            {"if"},
        )

    def test_a_switch_expression_has_arms_not_functions(self):
        code = _dart("  var n = switch (getEntityType()) { Entities.bush => 1, _ => 0 };\n  print(n);")
        self.passes(code, {"if", "variables"})

    def test_parameters_are_not_variables_lists_or_dictionaries(self):
        self.passes("void go({int times = 1}) {\n  harvest();\n}\n" + _dart("  go();"), {"functions"})
        self.passes("void go([int times = 1]) {\n  harvest();\n}\n" + _dart("  go();"), {"functions"})
        self.passes(
            "class Drone {\n  Drone({this.speed = 1});\n  final int speed;\n}\n" + _dart("  Drone();"),
            {"functions", "variables"},
        )

    def test_a_typedef_is_not_a_variable(self):
        self.passes("typedef Action = void Function({int times});\n" + _dart("  harvest();"), set())

    def test_a_script_tag_is_not_code(self):
        code = "#!/usr/bin/env dart\nvoid main() {\n  while (true) {}\n}\n"
        self.assertEqual([(v.feature, v.line) for v in check(code, "dart", set())], [("while", 3)])

    def test_a_null_assertion_is_not_not(self):
        self.passes(_dart("  print(getEntityType()!);\n  print(getCompanion()![0]);"), {"lists"})

    def test_records_are_free_like_tuples(self):
        self.passes(_dart("  print((getPosX(), getPosY()));"), set())
        # A record type's named fields are in braces, and are no map.
        self.passes(_dart("  ({int x, int y}) at = (x: getPosX(), y: getPosY());\n  print(at);"), {"variables"})
        self.assertEqual(
            [(v.feature, v.line) for v in check(_dart("  (int, int) at;"), "dart", set())], [("variables", 2)])

    def test_a_condition_before_a_bare_statement_is_still_code(self):
        # `if (...) harvest();` - brackets then a name, like a record type - but the
        # condition is code, and its operators count.
        self.passes(_dart("  if (canHarvest()) harvest();\n  while (canHarvest()) harvest();"), {"if", "while"})
        found = check(_dart("  if (getPosX() < 3) harvest();"), "dart", {"if"})
        self.assertEqual([(v.feature, v.line) for v in found], [("operators", 2)])

    def test_a_getter_with_a_block_body_is_a_function(self):
        code = "int get size {\n  return 3;\n}\n" + _dart("  print(size);")
        self.assertEqual([(v.feature, v.line) for v in check(code, "dart", set())], [("functions", 1)])


class ProgramsThatMustPass(unittest.TestCase):
    """Legal with what you have early on: the gate must not stop any of these."""

    def languages(self):
        return ("python", "javascript", "dart") if HAS_JS else ("python", "dart")

    def assertPasses(self, programs: dict[str, str], unlocked: set[str]) -> None:
        for language in self.languages():
            with self.subTest(language=language):
                self.assertEqual(check(programs[language], language, unlocked), [])

    def test_a_while_loop_with_only_loops(self):
        self.assertPasses({
            "python": "while True:\n    harvest()\n",
            "javascript": "while (true) { harvest(); }\n",
            "dart": "void main() {\n  while (true) {\n    harvest();\n  }\n}\n",
        }, {"while"})

    def test_the_farm_loop_with_loops_if_and_for(self):
        self.assertPasses({
            "python": (
                "while True:\n"
                "    for i in range(get_world_size()):\n"
                "        if can_harvest():\n"
                "            harvest()\n"
                "        move(North)\n"
            ),
            "javascript": (
                "while (true) {\n"
                "  for (const i of range(getWorldSize())) {\n"
                "    if (canHarvest()) {\n"
                "      harvest();\n"
                "    }\n"
                "    move(North);\n"
                "  }\n"
                "}\n"
            ),
            "dart": (
                "void main() {\n"
                "  while (true) {\n"
                "    for (final i in range(getWorldSize())) {\n"
                "      if (canHarvest()) {\n"
                "        harvest();\n"
                "      } else {\n"
                "        doAFlip();\n"
                "      }\n"
                "      move(North);\n"
                "    }\n"
                "  }\n"
                "}\n"
            ),
        }, {"while", "if", "for"})

    def test_calls_names_and_negative_numbers_with_nothing(self):
        self.assertPasses({
            "python": (
                "do_a_flip()\n"
                "move(North)\n"
                "plant(Entities.Bush)\n"
                "use_item(Items.Water, 2)\n"
                "print(-1, -2.5, +3, True, None, (1, 2))\n"
                "change_hat(Hats.Straw_Hat)\n"
            ),
            "javascript": (
                "doAFlip();\n"
                "move(North);\n"
                "plant(Entities.Bush);\n"
                "useItem(Items.Water, 2);\n"
                "print(-1, -2.5, +3, true, null, `at`);\n"
                "changeHat(Hats.StrawHat);\n"
            ),
            "dart": _dart(
                "  doAFlip();\n"
                "  move(North);\n"
                "  plant(Entities.bush);\n"
                "  useItem(Items.water, 2);\n"
                "  print(-1);\n"
                "  print(-2.5);\n"
                "  changeHat(Hats.strawHat);"
            ),
        }, set())

    def test_comments_and_strings_are_not_code(self):
        self.assertPasses({
            "python": (
                "# while if + [ { x = 1\n"
                "print('while if + [ { x = 1')\n"
                'print("""for\n[ { def go():""")\n'
            ),
            "javascript": (
                "// while if + [ { x = 1\n"
                "/* for (;;) { x = [1] } */\n"
                "print('while if + [ { x = 1');\n"
                'print("for [ {");\n'
                "print(`while + [ {`);\n"
            ),
            "dart": _dart(
                "  // while if + [ { x = 1\n"
                "  /* for /* nested */ [ { x = 1 */\n"
                "  print('while if + [ {');\n"
                '  print("x = 1 + 2");\n'
                "  print('''for\n[ {''');\n"
                "  print(r'${x + 1}');\n"
                "  print('at $x');"
            ),
        }, set())


class EveryLanguage(unittest.TestCase):
    def languages(self):
        return ("python", "javascript", "dart") if HAS_JS else ("python", "dart")

    def test_syntax_errors_are_left_to_the_run(self):
        broken = {
            "python": ["while True\n    harvest(\n", "x = [1, 2\n"],
            "javascript": ["while (true { harvest(); \n", "x = [1, 2;\n"],
            "dart": [
                "void main() {\n  while (true) {\n    harvest();\n",
                _dart("  print('never closed);"),
                _dart("  /* never closed\n  while (true) {}"),
                _dart("  print('${}');"),
                _dart("  while (true) { ]"),
            ],
        }
        for language in self.languages():
            for code in broken[language]:
                with self.subTest(language=language, code=code):
                    self.assertEqual(check(code, language, set()), [])

    def test_every_feature_is_found_and_named(self):
        for language in self.languages():
            with self.subTest(language=language):
                found = check(EVERYTHING[language], language, set())
                self.assertEqual({v.feature for v in found}, ALL)

    def test_in_source_order_and_once_per_feature_and_line(self):
        programs = {
            "python": "x = 1 + 2 + 3\nwhile True:\n    harvest()\n",
            "javascript": "x = 1 + 2 + 3;\nwhile (true) {\n  harvest();\n}\n",
            "dart": _dart("  x = 1 + 2 + 3;\n  while (true) {\n    harvest();\n  }"),
        }
        for language in self.languages():
            with self.subTest(language=language):
                found = check(programs[language], language, set())
                line = 2 if language == "dart" else 1  # Dart's line 1 is main()
                self.assertEqual(
                    [(v.feature, v.line) for v in found],
                    [("variables", line), ("operators", line), ("while", line + 1)],
                )

    def test_everything_bought_means_nothing_to_check(self):
        for language in self.languages():
            with self.subTest(language=language):
                self.assertEqual(check(EVERYTHING[language], language, set(ALL)), [])

    def test_messages_name_the_unlock(self):
        [v] = check("while True:\n    harvest()\n", "python", set())
        self.assertEqual(
            v, Violation("while", 1, "while True:", "`while` needs Loops - buy it in the research tree."))
        [v] = check("for i in range(3):\n    harvest()\n", "python", set())
        self.assertEqual(v.message, "`for` needs Expand level 2 - buy it in the research tree.")
        [v] = check("if can_harvest():\n    harvest()\n", "python", set())
        self.assertEqual(v.message, "`if` needs Speed - buy it in the research tree.")
        [v] = check("print(1 + 2)\n", "python", set())
        self.assertEqual(v.message, "`+` needs Operators - buy it in the research tree.")
        # Import is in the tree but not built yet, so there is nothing to buy.
        [v] = check("import math\n", "python", set())
        self.assertEqual(v.message, "`import` needs Import, which Code Coach does not have yet.")

    def test_a_long_snippet_is_cut_short(self):
        code = "print(get_pos_x() + get_pos_y() + get_world_size() + get_water())\n"
        [v] = check(code, "python", set())
        self.assertLessEqual(len(v.snippet), gate.SNIPPET_CHARS)
        self.assertTrue(v.snippet.endswith("..."), v.snippet)

    def test_language_names(self):
        self.assertEqual([v.feature for v in check("while True:\n    pass\n", "Python", set())], ["while"])
        with self.assertRaises(ValueError):
            check("x", "cobol", set())


class UnlockFor(unittest.TestCase):
    def test_the_unlock_for_each_feature(self):
        self.assertEqual(unlock_for("while"), ("Loops", 1))
        self.assertEqual(unlock_for("if"), ("Speed", 1))
        self.assertEqual(unlock_for("for"), ("Expand", 2))
        self.assertEqual(unlock_for("operators"), ("Operators", 1))
        self.assertEqual(unlock_for("variables"), ("Variables", 1))
        self.assertEqual(unlock_for("functions"), ("Functions", 1))
        self.assertEqual(unlock_for("lists"), ("Lists", 1))
        self.assertEqual(unlock_for("dicts"), ("Dictionaries", 1))
        self.assertEqual(unlock_for("import"), ("Import", 1))

    def test_it_agrees_with_the_tree(self):
        for feature in LANGUAGE_FEATURES:
            with self.subTest(feature=feature):
                name, level = unlock_for(feature)
                self.assertIn(feature, UNLOCKS[name].features[level])

    def test_an_unknown_feature(self):
        with self.assertRaises(KeyError):
            unlock_for("goto")


if __name__ == "__main__":
    unittest.main()
