"""The Farmer Was Replaced as a language of its own (id "tfwr"): Free mode can
run and explain a program pasted from the game.

Running is on a throwaway farm. The one thing that matters most here is that
it never touches the player's saved farm, so that has its own tests.
"""

from __future__ import annotations

import unittest
from unittest import mock

from code_coach.api import server
from code_coach.api.schemas import ExplainRequest, VisualizeRequest
from code_coach.engine import run_code
from code_coach.farm import data, scratch
from code_coach.farm.explain_farm import explain_farm
from code_coach.farm.runner import HOST, save_path
from code_coach.languages import LANGUAGES, get_language, languages_payload

SAMPLE = (
    "def sweep():\n"
    "    for x in range(get_world_size()):\n"
    "        for y in range(get_world_size()):\n"
    "            if can_harvest():\n"
    "                harvest()\n"
    "            elif get_ground_type() != Grounds.Soil:\n"
    "                till()\n"
    "            move(North)\n"
    "        move(East)\n"
    "\n"
    "sweep()\n"
    "plant(Entities.Pumpkin)\n"
    "swap(East)\n"
    "n = num_items(Items.Hay)\n"
    "quick_print(n)\n"
)


def run(code: str, **kwargs) -> tuple[str, str, int]:
    return run_code(code, language="tfwr", **kwargs)


def line_of(result: dict, source_start: str) -> dict:
    for item in result["lines"]:
        if item["source"].startswith(source_start):
            return item
    raise AssertionError(f"no gloss for a line starting {source_start!r}: {[i['source'] for i in result['lines']]}")


class RegistrationTests(unittest.TestCase):
    def test_it_is_registered_and_available(self) -> None:
        lang = get_language("tfwr")
        self.assertEqual(lang.id, "tfwr")
        self.assertEqual(lang.name, "The Farmer Was Replaced")
        self.assertTrue(lang.available)
        self.assertEqual(lang.monaco, "python")
        self.assertEqual(lang.extension, "py")
        self.assertTrue(lang.note)
        self.assertEqual(sum(1 for x in LANGUAGES if x.id == "tfwr"), 1)

    def test_it_claims_exactly_a_runner_and_an_explainer(self) -> None:
        """Nothing else is true of it, and the other modes key off these claims."""
        self.assertEqual(set(get_language("tfwr").ready), {"runner", "explainer"})

    def test_the_other_modes_really_have_nothing_for_it(self) -> None:
        from code_coach.leetcode.bank import has_own_bank
        from code_coach.reference import sheet_for
        from code_coach.workbook import has_workbook

        self.assertFalse(has_workbook("tfwr"))
        self.assertIsNone(sheet_for("tfwr"))
        self.assertFalse(has_own_bank("tfwr"))

    def test_the_picker_gets_it(self) -> None:
        entry = next(x for x in languages_payload() if x["id"] == "tfwr")
        self.assertTrue(entry["available"])
        self.assertEqual(entry["ready"], ["runner", "explainer"])
        self.assertIn("tfwr", [x.id for x in server.languages()])

    def test_tracing_is_not_offered(self) -> None:
        progress = server._store.load()
        progress.language = "tfwr"
        server._store.save(progress)
        got = server.visualize(VisualizeRequest(code="harvest()\n"))
        self.assertFalse(got.ok)

    def test_the_session_says_it_can_explain_but_not_trace(self) -> None:
        progress = server._store.load()
        progress.language = "tfwr"
        server._store.save(progress)
        session = server.practice_current()
        self.assertEqual(session.language, "tfwr")
        self.assertTrue(session.can_explain)
        self.assertFalse(session.can_visualize)


class ScratchWorldTests(unittest.TestCase):
    def test_everything_is_researched_on_the_biggest_field(self) -> None:
        world = scratch.make_world()
        for name in data.all_function_names():
            self.assertTrue(world.has_function(name), name)
        self.assertEqual(world.unlocked_features(), set(data.LANGUAGE_FEATURES))
        self.assertEqual((world.w, world.h), data.FARM_SIZES[-1])
        for item in data.ITEMS:
            if item != "Power":
                self.assertGreaterEqual(world.items[item], 100_000, item)


class RunTests(unittest.TestCase):
    def test_print_is_stdout(self) -> None:
        out, err, code = run('print("hi")\nquick_print(3, "x")\n')
        self.assertEqual(out, "hi\n3 x\n")
        self.assertEqual((err, code), ("", 0))

    def test_a_program_that_does_nothing_says_nothing(self) -> None:
        self.assertEqual(run("x = 5\n"), ("", "", 0))
        self.assertEqual(run(""), ("", "", 0))

    def test_a_loop_of_moves_and_harvests_runs_on_the_scratch_farm(self) -> None:
        out, err, code = run("for i in range(3):\n    move(North)\n    harvest()\nprint(get_pos_y())\n")
        self.assertEqual((err, code), ("", 0))
        lines = out.splitlines()
        self.assertEqual(lines[0], "3")
        self.assertRegex(lines[-1], r"^-- done: \d+ ticks, harvested \d+ hay --$")

    def test_plant_and_harvest_are_summarised(self) -> None:
        code = "till()\nplant(Entities.Carrot)\nwhile not can_harvest():\n    pass\nharvest()\n"
        out, err, status = run(code)
        self.assertEqual((err, status), ("", 0))
        self.assertRegex(out.strip(), r"^-- done: \d+ ticks, harvested 1 carrot --$")

    def test_the_summary_line_is_last_and_only_on_success(self) -> None:
        out, _err, _ = run('harvest()\nprint("a")\n')
        self.assertTrue(out.startswith("a\n"))
        self.assertTrue(out.rstrip().endswith("--"))
        out, err, status = run('print("a")\nmove(7)\n')
        self.assertEqual(out, "a\n")
        self.assertEqual(status, 1)
        self.assertNotIn("done", out + err)

    def test_the_summary_wording(self) -> None:
        done = scratch.Scratch(ticks=123, changes={"Pumpkin": 12, "Hay": 3, "Water": 9, "Wood": -4})
        self.assertEqual(scratch._summary_line(done), "-- done: 123 ticks, harvested 12 pumpkin, 3 hay --")
        self.assertEqual(scratch._summary_line(scratch.Scratch(ticks=1)), "-- done: 1 tick --")
        self.assertEqual(scratch._summary_line(scratch.Scratch()), "")

    def test_an_infinite_loop_is_stopped_with_a_clear_message(self) -> None:
        out, err, status = run('print("start")\nwhile True:\n    harvest()\n', timeout=1.5)
        self.assertEqual(status, 124)
        self.assertEqual(out, "start\n")
        self.assertIn("Stopped after 1.5 seconds", err)
        self.assertIn("while True", err)

    def test_the_command_cap_stops_it_too(self) -> None:
        with mock.patch.object(scratch, "MAX_COMMANDS", 200):
            out, err, status = run("while True:\n    harvest()\n")
        self.assertEqual(status, 124)
        self.assertIn("200 drone commands", err)
        self.assertNotIn("done", out)

    def test_an_empty_loop_is_stopped_as_well(self) -> None:
        _out, err, status = run("while True:\n    pass\n", timeout=1.5)
        self.assertEqual(status, 124)
        self.assertIn("Stopped", err)

    def test_the_game_refusing_something_reports_the_line(self) -> None:
        out, err, status = run("harvest()\nmove(7)\n")
        self.assertEqual(status, 1)
        self.assertEqual(out, "")
        self.assertIn("move() needs a direction", err)
        self.assertTrue(err.endswith("(line 2)"), err)

    def test_a_name_error_is_called_one(self) -> None:
        _out, err, status = run("a = 1\nb = nothing_here + a\n")
        self.assertEqual(status, 1)
        self.assertIn("NameError", err)
        self.assertIn("nothing_here", err)
        self.assertIn("(line 2)", err)

    def test_a_syntax_error_has_its_line(self) -> None:
        _out, err, status = run("harvest()\nprint(\n")
        self.assertEqual(status, 1)
        self.assertIn("SyntaxError", err)
        self.assertIn("(line", err)

    def test_what_the_language_lacks_is_refused_before_anything_runs(self) -> None:
        out, err, status = run('print("never")\nsquares = [i * i for i in range(3)]\n')
        self.assertEqual(status, 1)
        self.assertEqual(out, "")
        self.assertIn("isn't part of the game's language", err)
        self.assertIn("(line 2)", err)

    def test_functions_and_globals_work(self) -> None:
        out, err, status = run("count = 0\ndef bump(n):\n    return n + 1\nprint(bump(count))\n")
        self.assertEqual((out.splitlines()[0], err, status), ("1", "", 0))


class TheSavedFarmIsNeverTouchedTests(unittest.TestCase):
    PROGRAM = "till()\nplant(Entities.Carrot)\nfor i in range(5):\n    move(East)\n    harvest()\nprint(num_items(Items.Hay))\n"

    def test_no_save_is_made_where_there_was_none(self) -> None:
        self.assertFalse(save_path().exists())
        out, err, status = run(self.PROGRAM)
        self.assertEqual((err, status), ("", 0), out)
        self.assertFalse(save_path().exists())

    def test_an_existing_save_and_the_live_farm_are_unchanged(self) -> None:
        world = HOST._load()
        world.items["Hay"] = 7
        world.x = 0
        HOST.save()
        path = save_path()
        before_bytes, before_mtime = path.read_bytes(), path.stat().st_mtime_ns
        before_world = world.to_json()
        before_files = {k: dict(v) for k, v in HOST.files.items()}

        out, err, status = run(self.PROGRAM)

        self.assertEqual((err, status), ("", 0), out)
        self.assertEqual(path.read_bytes(), before_bytes)
        self.assertEqual(path.stat().st_mtime_ns, before_mtime)
        self.assertEqual(HOST._load().to_json(), before_world)
        self.assertEqual(HOST.files, before_files)
        self.assertIsNone(HOST.run)
        # And the run itself did not see the seven hay: it is a farm of its own.
        self.assertGreater(int(out.splitlines()[0]), 1000)

    def test_nothing_in_a_run_even_asks_where_the_save_is(self) -> None:
        def refuse() -> None:
            raise AssertionError("a scratch run looked for the saved farm")

        with mock.patch("code_coach.farm.runner.save_path", refuse):
            _out, err, status = run(self.PROGRAM)
            explain_farm(self.PROGRAM)
        self.assertEqual((err, status), ("", 0))

    def test_every_run_starts_from_the_same_fresh_farm(self) -> None:
        first = run("harvest()\nprint(get_time())\n")
        second = run("harvest()\nprint(get_time())\n")
        self.assertEqual(first, second)


class ExplainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ran = scratch.run_program(SAMPLE)
        cls.result = explain_farm(SAMPLE, ran=cls.ran)

    def test_the_shape_is_the_other_explainers(self) -> None:
        r = self.result
        self.assertTrue(r["ok"])
        self.assertEqual(set(r), {"ok", "summary", "lines", "output_notes", "error_note"})
        self.assertTrue(r["summary"])
        for item in r["lines"]:
            self.assertEqual(set(item), {"line", "source", "depth", "text"})
        lines = [i["line"] for i in r["lines"]]
        self.assertEqual(lines, sorted(lines))

    def test_the_games_commands_are_glossed(self) -> None:
        r = self.result
        self.assertIn("ripe", line_of(r, "if can_harvest()")["text"])
        self.assertIn("destroyed", line_of(r, "harvest()")["text"])
        self.assertIn("soil", line_of(r, "till()")["text"])
        move = line_of(r, "move(North)")["text"]
        self.assertIn("north", move)
        self.assertIn("wraps round", move)
        self.assertIn("east", line_of(r, "move(East)")["text"])
        self.assertIn("pumpkin", line_of(r, "plant(Entities.Pumpkin)")["text"])
        self.assertIn("east", line_of(r, "swap(East)")["text"])
        self.assertIn("output only", line_of(r, "quick_print(n)")["text"])
        self.assertIn("hay", line_of(r, "n = num_items")["text"])

    def test_loops_over_the_farm_are_in_farm_terms(self) -> None:
        r = self.result
        self.assertIn("each column", line_of(r, "for x in range(get_world_size())")["text"])
        inner = line_of(r, "for y in range(get_world_size())")["text"]
        self.assertIn("each row", inner)
        self.assertIn("every square", inner)

    def test_your_own_functions_and_branches(self) -> None:
        r = self.result
        self.assertIn("your own function `sweep()`", line_of(r, "def sweep")["text"])
        self.assertIn("runs your function `sweep`", line_of(r, "sweep()")["text"])
        self.assertIn("isn't soil", line_of(r, "elif get_ground_type()")["text"])

    def test_depth_follows_the_nesting(self) -> None:
        r = self.result
        depths = {i["source"]: i["depth"] for i in r["lines"]}
        self.assertEqual(depths["def sweep():"], 0)
        self.assertEqual(depths["for x in range(get_world_size()):"], 1)
        self.assertEqual(depths["for y in range(get_world_size()):"], 2)
        self.assertEqual(depths["if can_harvest():"], 3)
        self.assertEqual(depths["harvest()"], 4)
        self.assertEqual(depths["move(East)"], 2)

    def test_the_real_run_is_reported(self) -> None:
        notes = " ".join(self.result["output_notes"])
        self.assertIn(f"{self.ran.ticks} ticks", notes)
        self.assertIn("ended on square", notes)
        self.assertIn("22 by 22", notes)
        self.assertIn("practice farm", notes)
        self.assertIn("It printed: ", notes)
        self.assertIsNone(self.result["error_note"])

    def test_the_summary_names_the_commands(self) -> None:
        summary = self.result["summary"]
        for word in ("1 function", "loops", "move", "harvest"):
            self.assertIn(word, summary)

    def test_it_runs_the_program_itself_when_not_given_a_run(self) -> None:
        r = explain_farm("print(1 + 1)\nharvest()\n")
        self.assertTrue(any(n.startswith("It printed: 2") for n in r["output_notes"]), r["output_notes"])
        self.assertIn("harvested", " ".join(r["output_notes"]))

    def test_a_run_that_stopped_on_an_error_names_the_line(self) -> None:
        r = explain_farm("harvest()\nok = foo(1)\n")
        self.assertIn("NameError", r["error_note"])
        self.assertIn("line 2", r["error_note"])
        self.assertIn("foo", r["error_note"])

    def test_an_unknown_name_is_flagged_and_a_known_one_is_not(self) -> None:
        r = explain_farm("def mine():\n    pass\nmine()\nfoo(3)\nharvest()\nplant(Entities.Pumpkin)\n")
        self.assertIn("Heads-up", line_of(r, "foo(3)")["text"])
        self.assertIn("not a game command", line_of(r, "foo(3)")["text"])
        for source in ("mine()", "harvest()", "plant(Entities.Pumpkin)"):
            self.assertNotIn("Heads-up", line_of(r, source)["text"], source)

    def test_a_game_word_that_does_not_exist_is_flagged(self) -> None:
        r = explain_farm("plant(Entities.Pumkin)\n")
        self.assertIn("Heads-up", line_of(r, "plant(")["text"])
        self.assertIn("Pumkin", line_of(r, "plant(")["text"])

    def test_ordinary_python_the_game_lacks_is_said_so(self) -> None:
        r = explain_farm("x = str(3)\n")
        self.assertIn("ordinary Python", line_of(r, "x = str(3)")["text"])

    def test_a_syntax_error_is_said_with_its_line(self) -> None:
        r = explain_farm("harvest()\nprint(\n")
        self.assertTrue(r["ok"])
        self.assertEqual(r["lines"], [])
        self.assertIn("syntax error", r["summary"])
        self.assertIn("SyntaxError", r["error_note"])
        self.assertIn("line", r["error_note"])

    def test_what_the_language_refuses_is_said_plainly(self) -> None:
        r = explain_farm("squares = [i * i for i in range(3)]\n")
        self.assertIn("isn't part of the game's language", r["error_note"])
        self.assertIn("refused", r["error_note"])
        self.assertIn("The game refuses this", line_of(r, "squares =")["text"])

    def test_a_loop_that_never_ends_is_told_so(self) -> None:
        code = "while True:\n    harvest()\n"
        r = explain_farm(code, ran=scratch.run_program(code, seconds=1.0))
        self.assertIn("never finished", " ".join(r["output_notes"]))
        self.assertIn("never finishes", r["summary"])
        self.assertIn("nothing inside it can end it", line_of(r, "while True")["text"])

    def test_a_while_loop_with_a_break_says_so(self) -> None:
        r = explain_farm("while True:\n    break\n")
        self.assertIn("`break`", line_of(r, "while True")["text"])

    def test_assigning_in_a_function_warns_about_the_missing_global(self) -> None:
        r = explain_farm("count = 0\ndef bump():\n    count = count + 1\nbump()\n")
        self.assertIn("new local", line_of(r, "count = count + 1")["text"])

    def test_blank_and_comment_only_programs(self) -> None:
        self.assertEqual(explain_farm("  \n")["lines"], [])
        r = explain_farm("# todo\n")
        self.assertTrue(r["ok"])
        self.assertEqual([i["line"] for i in r["lines"]], [1])

    def test_every_game_command_has_some_gloss(self) -> None:
        """None of the commands falls through to 'calls `name`'."""
        import ast

        from code_coach.farm.explain_farm import _Reader
        from code_coach.farm.protocol import FUNCTIONS

        for f in FUNCTIONS:
            args = ", ".join(["North"] * sum(1 for p in f.params if not p.startswith("*") and "=" not in p))
            with self.subTest(command=f.py):
                tree = ast.parse(f"{f.py}({args})\n")
                walker = _Reader(tree, [f"{f.py}({args})"])
                walker.body(tree.body, 0)
                self.assertNotIn("calls `", walker.items[0]["text"])
                self.assertNotIn("not one of the game's commands", walker.items[0]["text"])


class RouteTests(unittest.TestCase):
    def test_explain_route_reads_the_farm_language(self) -> None:
        progress = server._store.load()
        progress.language = "tfwr"
        server._store.save(progress)
        got = server.explain(ExplainRequest(code="move(North)\nharvest()\n"))
        self.assertTrue(got.ok)
        self.assertIn("north", got.lines[0].text)
        self.assertEqual([item.line for item in got.lines], [1, 2])
        self.assertTrue(any("ticks" in note for note in got.output_notes))

    def test_python_still_goes_to_the_python_explainer(self) -> None:
        got = server.explain(ExplainRequest(code="print(1)\n"))
        self.assertTrue(got.ok)
        self.assertNotIn("drone", got.summary)

    def test_free_mode_runs_it_through_the_same_engine(self) -> None:
        """The evaluate route runs whatever language is stored through run_code."""
        progress = server._store.load()
        progress.language = "tfwr"
        server._store.save(progress)
        out, err, status = run_code("print(42)\n", language=progress.language)
        self.assertEqual((out, err, status), ("42\n", "", 0))


if __name__ == "__main__":
    unittest.main()
