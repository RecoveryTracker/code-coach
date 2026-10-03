"""Farm: Megafarm - several drones at once, end to end.

The game's promise is parallel drones: two drones each harvesting a column
take the game time of one column, not two. These tests run real programs
that spawn drones and check that, plus what spawn_drone, wait_for,
num_drones and max_drones answer, that drones share no memory but get a
copy of the globals (Python) and their arguments, and that one drone's
error ends the run.
"""

from __future__ import annotations

import shutil
import time
import unittest

from code_coach.engine import dart_path
from code_coach.farm import data
from code_coach.farm.runner import FarmHost

HAS_NODE = shutil.which("node") is not None
HAS_DART = dart_path() is not None

LEVELS = dict(Loops=1, Speed=1, Expand=2, Plant=1, Senses=1, Operators=1, Variables=1,
              Functions=1, Lists=1, Debug=1, Timing=1, Megafarm=1)


def host() -> FarmHost:
    h = FarmHost()
    h.warp = 0
    world = h._load()
    for name, level in LEVELS.items():
        world.unlocks[name] = level
    world.width, world.height = data.FARM_SIZES[2]
    world._fill()
    world.advance(5)  # every square's grass ripe
    return h


def finish(h: FarmHost, timeout: float = 90.0) -> str:
    deadline = time.monotonic() + timeout
    while h.run and h.run.status in ("starting", "running"):
        if time.monotonic() > deadline:
            h.stop_run(wait=True)
            raise AssertionError("the program did not finish")
        time.sleep(0.02)
    return h.run.status


def printed(h: FarmHost) -> list[str]:
    return [line["text"] for line in h.output if line["kind"] in ("print", "out")]


PY_COLUMNS = """\
def column():
    for i in range(get_world_size()):
        harvest()
        move(North)
    return get_pos_x()

start = get_time()
other = spawn_drone(column)
move(East)
column()
quick_print(wait_for(other))
quick_print(get_time() - start)
"""


class PythonMegafarmTests(unittest.TestCase):
    def test_two_drones_harvest_two_columns_in_the_time_of_one(self) -> None:
        h = host()
        started = h.start("python", PY_COLUMNS)
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h), "done", h.run.error)
        world = h._load()
        self.assertEqual(world.items["Hay"], 6)
        out = printed(h)
        self.assertEqual(out[0], "0")  # the spawned drone stayed in column 0
        elapsed = float(out[1])
        one = data.ACTION_TICKS / (data.BASE_TICKS_PER_SECOND * data.SPEED_STEP)
        # spawn + move East + 3 harvests + 3 moves, with the other column done alongside:
        # about 8 actions, nowhere near the 14 it would be one drone after the other.
        self.assertLess(elapsed, 9.5 * one)
        self.assertGreater(elapsed, 7.5 * one)

    def test_spawning_past_the_limit_answers_none(self) -> None:
        h = host()
        code = (
            "def rest():\n"
            "    do_a_flip()\n"
            "quick_print(max_drones())\n"
            "a = spawn_drone(rest)\n"
            "b = spawn_drone(rest)\n"
            "quick_print(num_drones())\n"
            "quick_print(b == None)\n"
            "wait_for(a)\n"
            "quick_print(has_finished(a))\n"
        )
        h.start("python", code)
        self.assertEqual(finish(h), "done", h.run.error)
        self.assertEqual(printed(h), ["2", "2", "True", "True"])

    def test_drones_get_arguments_and_a_copy_of_the_globals(self) -> None:
        h = host()
        code = (
            "base = 40\n"
            "def add(n):\n"
            "    return base + n\n"
            "d = spawn_drone(add, 2)\n"
            "quick_print(wait_for(d))\n"
        )
        h.start("python", code)
        self.assertEqual(finish(h), "done", h.run.error)
        self.assertEqual(printed(h), ["42"])

    def test_an_error_in_a_drone_ends_the_run_and_names_the_drone(self) -> None:
        h = host()
        code = (
            "def bad():\n"
            "    till()\n"
            "d = spawn_drone(bad)\n"
            "wait_for(d)\n"
        )
        h.start("python", code)
        self.assertEqual(finish(h), "error")
        self.assertIn("Drone 1", h.run.error)
        self.assertIn("Carrots", h.run.error)
        self.assertEqual(h.run.error_line, 2)

    def test_megafarm_must_be_bought(self) -> None:
        h = host()
        h._load().unlocks["Megafarm"] = 0
        h.start("python", "def f():\n    harvest()\nspawn_drone(f)\n")
        self.assertEqual(finish(h), "error")
        self.assertIn("Megafarm", h.run.error)


@unittest.skipUnless(HAS_NODE, "needs node")
class JavaScriptMegafarmTests(unittest.TestCase):
    def test_javascript_drones_work_side_by_side(self) -> None:
        h = host()
        code = (
            "function column() {\n"
            "  for (const i of range(getWorldSize())) {\n"
            "    harvest();\n"
            "    move(North);\n"
            "  }\n"
            "  return getPosX();\n"
            "}\n"
            "const other = spawnDrone(column);\n"
            "move(East);\n"
            "column();\n"
            "quickPrint(waitFor(other));\n"
        )
        started = h.start("javascript", code)
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h), "done", h.run.error)
        self.assertEqual(h._load().items["Hay"], 6)
        self.assertEqual(printed(h), ["0"])


@unittest.skipUnless(HAS_DART, "needs dart")
class DartMegafarmTests(unittest.TestCase):
    def test_dart_drones_work_side_by_side(self) -> None:
        h = host()
        code = (
            "int column() {\n"
            "  for (final i in range(getWorldSize())) {\n"
            "    harvest();\n"
            "    move(north);\n"
            "  }\n"
            "  return getPosX();\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  final other = spawnDrone(column);\n"
            "  move(east);\n"
            "  column();\n"
            "  quickPrint(waitFor(other!));\n"
            "}\n"
        )
        started = h.start("dart", code)
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h, 180), "done", h.run.error)
        self.assertEqual(h._load().items["Hay"], 6)
        self.assertEqual(printed(h), ["0"])


if __name__ == "__main__":
    unittest.main()
