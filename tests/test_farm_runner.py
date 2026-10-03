"""Farm: real programs, run end to end against the real farm.

Each test starts a program the way the Run button does - checked against
what is unlocked, launched as a real process, every command answered by the
World - at "max" warp so nothing waits on the clock, and looks at what it
did to the farm: hay in the barn, a refusal before it ran, an error on the
right line, a Stop that stops.
"""

from __future__ import annotations

import shutil
import time
import unittest

from code_coach.engine import dart_path
from code_coach.farm import runner
from code_coach.farm.runner import FarmHost

HAS_NODE = shutil.which("node") is not None
HAS_DART = dart_path() is not None


def host(**levels: int) -> FarmHost:
    """A fresh farm (in the test's own save folder) with research bought."""
    h = FarmHost()
    h.warp = 0
    world = h._load()
    for name, level in levels.items():
        world.unlocks[name] = level
    if levels.get("Expand"):
        from code_coach.farm import data

        world.width, world.height = data.FARM_SIZES[levels["Expand"]]
        world._fill()
    return h


def finish(h: FarmHost, timeout: float = 60.0) -> str:
    deadline = time.monotonic() + timeout
    while h.run and h.run.status in ("starting", "running"):
        if time.monotonic() > deadline:
            h.stop_run(wait=True)
            raise AssertionError("the program did not finish")
        time.sleep(0.02)
    return h.run.status if h.run else "none"


class PythonRunTests(unittest.TestCase):
    def test_a_first_program_harvests_hay(self) -> None:
        h = host()
        h._load().advance(1)
        started = h.start("python", "harvest()\n")
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h), "done")
        self.assertEqual(h._load().items["Hay"], 1)

    def test_a_loop_before_loops_is_refused_before_it_runs(self) -> None:
        h = host()
        started = h.start("python", "while True:\n    harvest()\n")
        self.assertFalse(started["ok"])
        self.assertEqual(started["violations"][0]["feature"], "while")
        self.assertEqual(started["violations"][0]["line"], 1)
        self.assertIsNone(h.run)

    def test_a_locked_command_stops_the_program_on_its_line(self) -> None:
        h = host(Loops=1)
        started = h.start("python", "harvest()\nmove(North)\n")
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h), "error")
        self.assertIn("Expand", h.run.error)
        self.assertEqual(h.run.error_line, 2)

    def test_a_crash_reports_the_players_line(self) -> None:
        h = host()
        h.start("python", "harvest()\n\nharvst()\n")
        self.assertEqual(finish(h), "error")
        self.assertEqual(h.run.error_line, 3)
        self.assertIn("harvst", h.run.error)

    def test_stop_ends_a_program_that_would_run_for_ever(self) -> None:
        h = host(Loops=1)
        h.start("python", "while True:\n    harvest()\n")
        time.sleep(1.0)
        h.stop_run(wait=True)
        self.assertEqual(h.run.status, "stopped")
        self.assertGreater(h._load().items["Hay"], 5)

    def test_quiet_loops_are_stopped_by_the_watchdog(self) -> None:
        old = runner.SILENT_LIMIT
        runner.SILENT_LIMIT = 1.0
        try:
            h = host(Loops=1)
            h.start("python", "harvest()\nwhile True:\n    pass\n")
            self.assertEqual(finish(h, 20), "error")
            self.assertIn("without giving the drone a single command", h.run.error)
        finally:
            runner.SILENT_LIMIT = old

    def test_prints_reach_the_output(self) -> None:
        h = host(Debug=1)
        h.start("python", "print('hello', 3)\nquick_print('quiet')\n")
        self.assertEqual(finish(h), "done")
        texts = [line["text"] for line in h.output]
        self.assertIn("hello 3", texts)
        self.assertIn("quiet", texts)

    def test_the_farm_and_your_code_are_saved(self) -> None:
        h = host()
        h._load().advance(1)
        h.start("python", "harvest()\n")
        finish(h)
        again = FarmHost()
        self.assertEqual(again._load().items["Hay"], 1)
        self.assertEqual(again.code["python"], "harvest()\n")

    def test_research_can_be_bought(self) -> None:
        h = host()
        h._load().items["Hay"] = 5
        self.assertTrue(h.buy("Loops"))
        self.assertEqual(h._load().level("Loops"), 1)
        names = {u["name"]: u for u in h.unlock_list()}
        self.assertTrue(names["Speed"]["available"])
        self.assertEqual(names["Loops"]["cost"], None)

    def test_a_whole_field_program(self) -> None:
        h = host(Loops=1, Speed=1, Expand=2, Plant=1)
        code = (
            "for i in range(get_world_size()):\n"
            "    for j in range(get_world_size()):\n"
            "        plant(Entities.Bush)\n"
            "        move(North)\n"
            "    move(East)\n"
        )
        h.start("python", code)
        self.assertEqual(finish(h), "done")
        bushes = sum(1 for t in h._load().tiles if t.entity == "Bush")
        self.assertEqual(bushes, 9)


@unittest.skipUnless(HAS_NODE, "needs node")
class JavaScriptRunTests(unittest.TestCase):
    def test_javascript_farms_the_same_field(self) -> None:
        h = host(Loops=1, Speed=1, Expand=2, Plant=1, Senses=1)
        code = (
            "for (const i of range(getWorldSize())) {\n"
            "  for (const j of range(getWorldSize())) {\n"
            "    plant(Entities.Bush);\n"
            "    move(North);\n"
            "  }\n"
            "  move(East);\n"
            "}\n"
        )
        started = h.start("javascript", code)
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h), "done", h.run.error)
        self.assertEqual(sum(1 for t in h._load().tiles if t.entity == "Bush"), 9)

    def test_javascript_errors_name_the_camel_case_function(self) -> None:
        h = host(Loops=1)
        h.start("javascript", "harvest();\nmove(North);\n")
        self.assertEqual(finish(h), "error")
        self.assertIn("move()", h.run.error)
        self.assertEqual(h.run.error_line, 2)


@unittest.skipUnless(HAS_DART, "needs dart")
class DartRunTests(unittest.TestCase):
    def test_dart_farms_the_same_field(self) -> None:
        h = host(Loops=1, Speed=1, Expand=2, Plant=1, Senses=1)
        code = (
            "void main() {\n"
            "  for (final i in range(getWorldSize())) {\n"
            "    for (final j in range(getWorldSize())) {\n"
            "      plant(Entities.bush);\n"
            "      move(north);\n"
            "    }\n"
            "    move(east);\n"
            "  }\n"
            "}\n"
        )
        started = h.start("dart", code)
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h, 120), "done", h.run.error)
        self.assertEqual(sum(1 for t in h._load().tiles if t.entity == "Bush"), 9)

    def test_dart_compile_errors_point_at_the_line(self) -> None:
        h = host()
        h.start("dart", "void main() {\n  harvest()\n}\n")
        self.assertEqual(finish(h, 120), "error")
        self.assertEqual(h.run.error_line, 2)


if __name__ == "__main__":
    unittest.main()
