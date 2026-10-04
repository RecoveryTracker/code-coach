"""Farm: simulate() - a file run on a fresh farm of its own.

The game's promise for simulations: the starting state is yours to choose
(research, items, globals, a seed), the same seed and start always give the
same run, the answer is the game seconds it took, and the real farm is
left exactly as it was. These tests hold the farm to each of those, end to
end, with programs in the game's own language (Original) and in Python,
JavaScript and Dart.
"""

from __future__ import annotations

import shutil
import time
import unittest

from code_coach.engine import dart_path
from code_coach.farm import data
from code_coach.farm.runner import FarmHost
from code_coach.farm.world import Refusal, World

HAS_NODE = shutil.which("node") is not None
HAS_DART = dart_path() is not None

#: Research the real farm has, so the calling program may use what it needs.
LEVELS = dict(Loops=1, Speed=1, Expand=2, Plant=1, Senses=1, Operators=1, Variables=1, Functions=1,
              Lists=1, Dictionaries=1, Debug=1, Import=1, Megafarm=1, Simulation=1)

#: Prints the hay it starts with (what simulate() gave it), then farms a column.
BENCH = "quick_print(num_items(Items.Hay))\nfor i in range(rows):\n    harvest()\n    move(North)\n"


def host(**levels) -> FarmHost:
    h = FarmHost()
    h.warp = 0
    world = h._load()
    for name, level in (levels or LEVELS).items():
        world.unlocks[name] = level
    world.width, world.height = data.FARM_SIZES[world.level("Expand")]
    world._fill()
    world.advance(5)
    return h


def finish(h: FarmHost, timeout: float = 120.0) -> str:
    deadline = time.monotonic() + timeout
    while h.run and h.run.status in ("starting", "running"):
        if time.monotonic() > deadline:
            h.stop_run(wait=True)
            raise AssertionError("the program did not finish")
        time.sleep(0.02)
    return h.run.status


def out(h: FarmHost) -> list[str]:
    return [line["text"] for line in h.output if line["kind"] in ("out", "print")]


class SetupTests(unittest.TestCase):
    def test_a_list_of_unlocks_means_each_at_its_top_level(self) -> None:
        s = World.simulation_setup(["f", ["Unlocks.Speed", "Unlocks.Grass"], {}, {}, 0, 64])
        self.assertEqual(s["unlocks"], {"Speed": 5, "Grass": 11})
        self.assertEqual(s["speedup"], 64)

    def test_a_dict_sets_levels_and_negative_means_the_top(self) -> None:
        s = World.simulation_setup(["f", {"Unlocks.Speed": 2, "Unlocks.Expand": -1}, None, None, -1, 0])
        self.assertEqual(s["unlocks"], {"Speed": 2, "Expand": 9})
        self.assertEqual((s["seed"], s["speedup"]), (-1, 0.0))

    def test_bad_arguments_are_refused_in_words(self) -> None:
        for args in (
            ["f", [], {}, {}, 0],                                  # five, not six
            ["", [], {}, {}, 0, 1],                               # no file
            ["f", ["Items.Hay"], {}, {}, 0, 1],                   # not an unlock
            ["f", [], {"Unlocks.Speed": 3}, {}, 0, 1],            # not an item
            ["f", [], {"Items.Hay": -1}, {}, 0, 1],               # a negative amount
            ["f", [], {}, [], 0, 1],                              # globals not a dict
            ["f", [], {}, {}, 1.5, 1],                            # a seed that isn't whole
        ):
            with self.subTest(args=args), self.assertRaises(Refusal):
                World.simulation_setup(args)

    def test_a_fresh_farm_with_the_research_and_items_given(self) -> None:
        w = World.for_simulation(World.simulation_setup(["f", ["Unlocks.Expand"], {"Items.Gold": 9}, {}, 3, 0]))
        self.assertEqual((w.w, w.h), data.FARM_SIZES[-1])
        self.assertEqual(w.items["Gold"], 9)
        self.assertEqual(w.time, 0)
        self.assertEqual(w.level("Loops"), 0)

    def test_the_same_seed_makes_the_same_farm(self) -> None:
        setup = World.simulation_setup(["f", ["Unlocks.Expand"], {}, {}, 5, 0])
        a, b = World.for_simulation(setup), World.for_simulation(setup)
        self.assertEqual([t.need for t in a.tiles], [t.need for t in b.tiles])
        self.assertEqual(a.rng.random(), b.rng.random())


class OriginalSimulationTests(unittest.TestCase):
    """Simulations from the game's own language, through the real farm."""

    def start(self, h: FarmHost, main: str, bench: str = BENCH) -> dict:
        h.file_op("original", "add", "bench")
        h.keep_code("original", bench, "bench")
        return h.start("original", main, "main")

    def test_a_simulation_runs_on_its_own_farm_and_answers_with_its_time(self) -> None:
        h = host()
        hay_before = h._load().items["Hay"]
        main = (
            't = simulate("bench", [Unlocks.Expand, Unlocks.Plant, Unlocks.Senses, Unlocks.Debug], {Items.Hay: 5}, {"rows": 3}, 7, 0)\n'
            "quick_print(t)\n"
            "quick_print(num_items(Items.Hay))\n"
        )
        started = self.start(h, main)
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h), "done", h.run.error)
        lines = out(h)
        # The simulated program printed its own hay, with what it was given...
        self.assertEqual(lines[0], "(simulation) 5")
        # ...the caller got the game seconds it took...
        seconds = float(lines[1])
        self.assertGreater(seconds, 0)
        # ...and the real barn never saw any of it.
        self.assertEqual(lines[2], str(int(hay_before)))
        self.assertEqual(h._load().items["Hay"], hay_before)

    def test_the_same_seed_gives_the_same_time(self) -> None:
        h = host()
        main = (
            'a = simulate("bench", Unlocks, {}, {"rows": 6}, 11, 0)\n'
            'b = simulate("bench", Unlocks, {}, {"rows": 6}, 11, 0)\n'
            "quick_print(a == b, a > 0)\n"
        )
        self.start(h, main)
        self.assertEqual(finish(h), "done", h.run.error)
        self.assertEqual(out(h)[-1], "True True")

    def test_it_needs_the_simulation_unlock(self) -> None:
        levels = dict(LEVELS)
        levels["Simulation"] = 0
        h = host(**levels)
        self.start(h, 'simulate("bench", [], {}, {}, 0, 0)\n')
        self.assertEqual(finish(h), "error")
        self.assertIn("Simulation", h.run.error)

    def test_an_error_in_the_simulation_stops_the_caller_and_says_so(self) -> None:
        h = host()
        self.start(h, 'simulate("bench", [], {}, {}, 0, 0)\nquick_print("after")\n',
                   bench="harvest()\nnope()\n")
        self.assertEqual(finish(h), "error")
        self.assertIn("simulation of bench stopped with an error", h.run.error)
        self.assertIn("nope", h.run.error)
        self.assertNotIn("after", out(h))

    def test_an_unknown_file_is_refused(self) -> None:
        h = host()
        self.start(h, 'simulate("nothere", [], {}, {}, 0, 0)\n')
        self.assertEqual(finish(h), "error")
        self.assertIn("nothere", h.run.error)

    def test_stop_ends_the_simulation_too(self) -> None:
        h = host()
        self.start(h, 'simulate("bench", [Unlocks.Loops], {}, {}, 0, 1)\n',
                   bench="while True:\n    do_a_flip()\n")
        deadline = time.monotonic() + 30
        while h.run.sim is None and time.monotonic() < deadline:
            time.sleep(0.05)
        sim = h.run.sim
        self.assertIsNotNone(sim)
        self.assertIsNotNone(h.state()["simulation"])
        h.stop_run(wait=True)
        self.assertEqual(h.run.status, "stopped")
        deadline = time.monotonic() + 10
        while sim.status in ("starting", "running") and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertNotIn(sim.status, ("starting", "running"))


class PythonSimulationTests(unittest.TestCase):
    def test_python_passes_unlocks_whole_and_its_globals_arrive(self) -> None:
        h = host()
        h.file_op("python", "add", "bench")
        h.keep_code("python", BENCH, "bench")
        main = (
            't = simulate("bench", Unlocks, {Items.Hay: 5}, {"rows": 2}, 1, 0)\n'
            "quick_print(t > 0)\n"
        )
        started = h.start("python", main, "main")
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h), "done", h.run.error)
        self.assertEqual(out(h), ["(simulation) 5", "True"])


@unittest.skipUnless(HAS_NODE, "needs node")
class JavaScriptSimulationTests(unittest.TestCase):
    def test_javascript_simulates(self) -> None:
        h = host()
        h.file_op("javascript", "add", "bench")
        h.keep_code("javascript", (
            "quickPrint(numItems(Items.Hay));\n"
            "for (const i of range(rows)) {\n"
            "  harvest();\n"
            "  move(North);\n"
            "}\n"
        ), "bench")
        main = (
            'const t = simulate("bench", Unlocks, {[Items.Hay]: 5}, {rows: 2}, 1, 0);\n'
            "quickPrint(t > 0);\n"
        )
        started = h.start("javascript", main, "main")
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h), "done", h.run.error)
        self.assertEqual(out(h), ["(simulation) 5", "true"])


@unittest.skipUnless(HAS_DART, "needs dart")
class DartSimulationTests(unittest.TestCase):
    def test_dart_simulates_and_reads_sim_globals(self) -> None:
        h = host()
        h.file_op("dart", "add", "bench")
        h.keep_code("dart", (
            "void main() {\n"
            "  final rows = simGlobals['rows'] as int;\n"
            "  quickPrint(numItems(Items.hay));\n"
            "  for (final i in range(rows)) {\n"
            "    harvest();\n"
            "    move(north);\n"
            "  }\n"
            "}\n"
        ), "bench")
        main = (
            "void main() {\n"
            "  final t = simulate('bench', Unlocks.values, {Items.hay: 5}, {'rows': 2}, 1, 0);\n"
            "  quickPrint(t > 0);\n"
            "}\n"
        )
        started = h.start("dart", main, "main")
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h, 240), "done", h.run.error)
        self.assertEqual(out(h), ["(simulation) 5", "true"])


if __name__ == "__main__":
    unittest.main()
