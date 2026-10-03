"""Farm: the game's own language (Original), held to the game's rules.

The interpreter (code_coach/farm/stubs/farm_lang.py) is run here as the
farm runs it - a real process, one line per command - against a fake farm
that records each command and the ticks the language spent before it.
The costs are the wiki's own examples where it gives them:
`return 27 + len([1,2,3])` is 5 ticks; `list(range(20))` then
`insert(3, 30)` is 40. Scopes are the game's (x += 1 in a function makes a
local), and what isn't the game's language is refused on its line.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from code_coach.farm import data
from code_coach.farm.protocol import FUNCTIONS, MARK

LANG = Path(__file__).resolve().parent.parent / "code_coach" / "farm" / "stubs" / "farm_lang.py"


def rendered() -> str:
    """farm_lang.py with its names filled in, as the runner writes it."""
    from code_coach.farm.stubs.render import library

    return library("original")


def run(files: dict[str, str], entry: str = "main", answers=None, env: dict | None = None):
    """Run a program; returns (requests [(name, args, ticks)], exit code)."""
    answers = answers or (lambda name, args: None)
    with tempfile.TemporaryDirectory() as work:
        Path(work, "farm_lang.py").write_text(rendered(), encoding="utf-8")
        Path(work, "files").mkdir()
        for name, code in files.items():
            Path(work, "files", name + ".py").write_text(code, encoding="utf-8")
        proc = subprocess.Popen(
            [sys.executable, "-u", "farm_lang.py", entry], cwd=work,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=dict(os.environ, PYTHONIOENCODING="utf-8", **(env or {})),
        )
        requests = []
        for raw in iter(proc.stdout.readline, b""):
            line = raw.decode("utf-8").rstrip("\r\n")
            if not line.startswith(MARK):
                continue
            body = json.loads(line[len(MARK):])
            name, args, ticks = body["f"], body.get("a", []), body.get("t", 0)
            requests.append((name, args, ticks))
            if name in ("__error__", "__return__"):
                continue
            reply = answers(name, args)
            if isinstance(reply, dict) and set(reply) <= {"e", "stop"} and reply:
                text = json.dumps(reply)  # a refusal or a stop, sent as it is
            else:
                text = json.dumps({"r": reply})
            proc.stdin.write((text + "\n").encode())
            proc.stdin.flush()
        proc.wait(timeout=20)
        return requests, proc.returncode


def ticks_before(requests, name: str) -> int:
    """The language ticks spent up to and including the first `name` command."""
    total = 0
    for req, _args, t in requests:
        total += t
        if req == name:
            return total
    raise AssertionError(f"no {name} in {requests}")


def printed(requests) -> list[str]:
    return [args[0] for name, args, _t in requests if name in ("print", "quick_print")]


def error(requests):
    for name, args, _t in requests:
        if name == "__error__":
            return args
    return None


class TickCostTests(unittest.TestCase):
    def cost(self, code: str) -> int:
        requests, _ = run({"main": code + "harvest()\n"})
        self.assertIsNone(error(requests), error(requests))
        return ticks_before(requests, "harvest")

    def test_the_wikis_own_examples(self) -> None:
        # Operation Costs: return 27 + len([1,2,3]) costs 5 (+ the def's own tick).
        self.assertEqual(self.cost("def f():\n    return 27 + len([1,2,3])\nf()\n"), 1 + 5)
        # Execution Details: list(range(20)) then insert(3, 30) costs 40.
        self.assertEqual(self.cost("my_list = list(range(20))\nmy_list.insert(3, 30)\n"), 40)

    def test_operators_cost_one_and_unary_and_variables_are_free(self) -> None:
        self.assertEqual(self.cost("x = 1 + 2\n"), 1)
        self.assertEqual(self.cost("x = -5\ny = not True\nz = x\n"), 0)
        self.assertEqual(self.cost("x = 1 < 2 and 3 > 2\n"), 3)

    def test_if_costs_one_and_else_is_free(self) -> None:
        self.assertEqual(self.cost("if True:\n    x = 1\nelse:\n    x = 2\n"), 1)
        self.assertEqual(self.cost("if False:\n    x = 1\nelif True:\n    x = 2\n"), 2)

    def test_loops_cost_one_to_start_and_pass_one_each(self) -> None:
        self.assertEqual(self.cost("for i in range(3):\n    pass\n"), 1 + 1 + 3)
        self.assertEqual(self.cost("i = 0\nwhile i < 3:\n    i += 1\n"), 1 + 4 + 3)

    def test_calling_through_a_variable_costs_one(self) -> None:
        self.assertEqual(self.cost("def f():\n    pass\nf()\n"), 1 + 1)
        self.assertEqual(self.cost("def f():\n    pass\ng = f\ng()\n"), 1 + 1 + 1)

    def test_literals_and_lookups(self) -> None:
        self.assertEqual(self.cost("x = []\n"), 1)
        self.assertEqual(self.cost("x = [1, 2, 3]\n"), 3)
        self.assertEqual(self.cost("x = (1, 2)\n"), 1)
        self.assertEqual(self.cost("x = {1: 2, 3: 4}\n"), 3)
        self.assertEqual(self.cost("d = {'abcdefghijklmnop': 1}\nx = d['abcdefghijklmnop']\n"), 2 + 2)
        self.assertEqual(self.cost("x = [5, 6, 7]\ny = x[1]\n"), 3 + 1)
        self.assertEqual(self.cost("x = [5, 6, 7]\ny = 7 in x\n"), 3 + 3)
        self.assertEqual(self.cost("x = [1, 2] + [3]\n"), 2 + 1 + 3)

    def test_a_long_computation_sends_its_time_on_its_own(self) -> None:
        requests, _ = run({"main": "for i in range(3000):\n    pass\nharvest()\n"})
        self.assertGreaterEqual(sum(1 for name, _a, _t in requests if name == "__ticks__"), 2)
        self.assertEqual(ticks_before(requests, "harvest"), 1 + 1 + 3000)


class LanguageTests(unittest.TestCase):
    def test_assignment_in_a_function_makes_a_local(self) -> None:
        code = "x = 1\ndef f():\n    x += 1\n    quick_print(x)\nf()\nquick_print(x)\n"
        requests, _ = run({"main": code})
        self.assertEqual(printed(requests), ["2", "1"])

    def test_functions_read_globals_and_lists_are_shared(self) -> None:
        code = "items = [1]\ndef add():\n    items.append(2)\nadd()\nquick_print(items)\n"
        requests, _ = run({"main": code})
        self.assertEqual(printed(requests), ["[1, 2]"])

    def test_values_print_the_way_the_game_prints_them(self) -> None:
        code = "quick_print(5 / 1, 7 // 2, 2.5, [1, 'a'], (1, 2), Entities.Bush, None, True)\n"
        requests, _ = run({"main": code})
        self.assertEqual(printed(requests), ["5 3 2.5 [1, 'a'] (1, 2) Entities.Bush None True"])

    def test_what_isnt_the_games_language_is_refused_on_its_line(self) -> None:
        for code, line, words in (
            ("x = 1\ny = [i for i in range(3)]\n", 2, "comprehension"),
            ("f = lambda: 1\n", 1, "lambda"),
            ("def f():\n    global x\n", 2, "global"),
            ("try:\n    harvest()\nexcept:\n    pass\n", 1, "try"),
            ("class A:\n    pass\n", 1, "class"),
            ("x = f'{1}'\n", 1, "f-string"),
            ("def f(*a):\n    pass\n", 1, "plain parameters"),
            ("move(direction=North)\n", 1, "keyword"),
        ):
            with self.subTest(code=code):
                requests, code_ = run({"main": code})
                err = error(requests)
                self.assertIsNotNone(err)
                self.assertIn(words, err[0])
                self.assertEqual(err[1], line)
                self.assertEqual(code_, 1)
                self.assertNotIn("harvest", [r[0] for r in requests])

    def test_an_unknown_name_is_reported_on_its_line(self) -> None:
        requests, _ = run({"main": "harvest()\n\nharvst()\n"})
        self.assertEqual(error(requests)[:2], ["harvst isn't defined.", 3])

    def test_a_farm_refusal_stops_the_program_on_the_calls_line(self) -> None:
        answers = lambda name, args: {"e": "move() isn't unlocked yet - research Expand."} if name == "move" else None  # noqa: E731
        requests, _ = run({"main": "harvest()\nmove(North)\nharvest()\n"}, answers=answers)
        err = error(requests)
        self.assertEqual((err[1], err[2]), (2, "main"))
        self.assertIn("Expand", err[0])
        self.assertEqual([r[0] for r in requests].count("harvest"), 1)

    def test_results_come_back_as_the_games_values(self) -> None:
        answers = {
            "get_entity_type": "Entities.Bush",
            "get_companion": ["Entities.Carrot", [3, 5]],
            "get_cost": {"Items.Hay": 5},
        }
        code = (
            "if get_entity_type() == Entities.Bush:\n"
            "    quick_print('bush')\n"
            "kind, (x, y) = get_companion()\n"
            "quick_print(kind, x, y)\n"
            "quick_print(get_cost(Entities.Carrot)[Items.Hay])\n"
        )
        requests, _ = run({"main": code}, answers=lambda n, a: answers.get(n))
        self.assertEqual(printed(requests), ["bush", "Entities.Carrot 3 5", "5"])


class ImportTests(unittest.TestCase):
    def test_import_runs_a_file_once_and_gives_its_globals(self) -> None:
        files = {
            "main": "import utils\nimport utils\nutils.go()\nquick_print(utils.N, __name__)\n",
            "utils": "N = 3\nquick_print('loading', __name__)\ndef go():\n    harvest()\n",
        }
        requests, _ = run(files)
        self.assertEqual(printed(requests), ["loading utils", "3 __main__"])
        self.assertIn("harvest", [r[0] for r in requests])

    def test_from_import_and_star(self) -> None:
        files = {
            "main": "from utils import go\nfrom more import *\ngo()\nquick_print(K)\n",
            "utils": "def go():\n    harvest()\n",
            "more": "K = 7\n",
        }
        requests, _ = run(files)
        self.assertEqual(printed(requests), ["7"])

    def test_an_error_in_an_imported_file_names_it(self) -> None:
        files = {"main": "import utils\nutils.broken()\n", "utils": "def broken():\n    x = 1\n    nope()\n"}
        requests, _ = run(files)
        err = error(requests)
        self.assertEqual((err[1], err[2]), (3, "utils"))


class DroneModeTests(unittest.TestCase):
    def test_a_drone_runs_only_its_function_with_args_and_globals(self) -> None:
        files = {"main": "base = 1\nharvest()\ndef add(n):\n    return base + n\n"}
        job = {"fn": "add", "args": [41], "globals": {"base": 1}}
        requests, code = run(files, env={"FARM_DRONE": json.dumps(job)})
        self.assertNotIn("harvest", [r[0] for r in requests])
        self.assertEqual(requests[-1][:2], ("__return__", [42]))
        self.assertEqual(code, 0)

    def test_spawn_sends_the_functions_name_and_the_globals(self) -> None:
        files = {"main": "size = 3\ndef col():\n    harvest()\nspawn_drone(col)\n"}
        requests, _ = run(files, answers=lambda n, a: 1 if n == "spawn_drone" else None)
        spawn = next(args for name, args, _t in requests if name == "spawn_drone")
        self.assertEqual(spawn[0], "col")
        self.assertEqual(spawn[2], {"size": 3})


class OriginalRunTests(unittest.TestCase):
    """Original through the real farm, as the Run button runs it."""

    def host(self, **levels):
        import time as _time  # noqa: F401 - kept local: only these tests wait on runs

        from code_coach.farm.runner import FarmHost

        h = FarmHost()
        h.warp = 0
        world = h._load()
        for name, level in levels.items():
            world.unlocks[name] = level
        if levels.get("Expand"):
            world.width, world.height = data.FARM_SIZES[levels["Expand"]]
            world._fill()
        world.advance(5)
        return h

    def finish(self, h, timeout=60.0):
        import time

        deadline = time.monotonic() + timeout
        while h.run and h.run.status in ("starting", "running"):
            if time.monotonic() > deadline:
                h.stop_run(wait=True)
                raise AssertionError("the program did not finish")
            time.sleep(0.02)
        return h.run.status

    def test_the_first_program(self) -> None:
        h = self.host()
        self.assertTrue(h.start("original", "harvest()\n")["ok"])
        self.assertEqual(self.finish(h), "done", h.run.error)
        self.assertEqual(h._load().items["Hay"], 1)

    def test_the_language_is_unlocked_step_by_step(self) -> None:
        h = self.host()
        got = h.start("original", "while True:\n    harvest()\n")
        self.assertFalse(got["ok"])
        self.assertEqual(got["violations"][0]["feature"], "while")

    def test_operations_take_game_time_in_original_and_not_in_python(self) -> None:
        levels = dict(Loops=1, Speed=1, Expand=2, Debug=1, Timing=1, Variables=1, Operators=1)
        code = "start = get_time()\nfor i in range(400):\n    pass\nquick_print(get_time() - start)\n"
        seconds = {}
        for language in ("original", "python"):
            h = self.host(**levels)
            self.assertTrue(h.start(language, code)["ok"])
            self.assertEqual(self.finish(h), "done", h.run.error)
            out = [line["text"] for line in h.output if line["kind"] == "out"]
            seconds[language] = float(out[-1])
        # 402 ticks at 600 a second (Speed 1): about two thirds of a second.
        self.assertAlmostEqual(seconds["original"], 402 / 600, places=2)
        self.assertEqual(seconds["python"], 0)

    def test_files_import_each_other(self) -> None:
        h = self.host(Loops=1, Speed=1, Expand=2, Functions=1, Variables=1, Import=1)
        h.file_op("original", "add", "rows")
        h.keep_code("original", "def column():\n    for i in range(get_world_size()):\n        harvest()\n        move(North)\n", "rows")
        got = h.start("original", "import rows\nrows.column()\nmove(East)\nrows.column()\n", "main")
        self.assertTrue(got["ok"], got)
        self.assertEqual(self.finish(h), "done", h.run.error)
        self.assertEqual(h._load().items["Hay"], 6)

    def test_megafarm_drones(self) -> None:
        h = self.host(Loops=1, Speed=1, Expand=2, Senses=1, Functions=1, Variables=1, Debug=1, Megafarm=1)
        code = (
            "def column():\n"
            "    for i in range(get_world_size()):\n"
            "        harvest()\n"
            "        move(North)\n"
            "    return get_pos_x()\n"
            "d = spawn_drone(column)\n"
            "move(East)\n"
            "column()\n"
            "quick_print(wait_for(d))\n"
        )
        got = h.start("original", code)
        self.assertTrue(got["ok"], got)
        self.assertEqual(self.finish(h), "done", h.run.error)
        self.assertEqual(h._load().items["Hay"], 6)
        self.assertEqual([line["text"] for line in h.output if line["kind"] == "out"], ["0"])


if __name__ == "__main__":
    unittest.main()
