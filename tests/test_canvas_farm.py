"""Canvas: the Farm track, where you program a world instead of writing one.

The same three holds as Dodge and Breakout - each solution passes, each
starter fails, and the real mistakes at each step fail - plus the world's
own promises: a wrong direction is named, and a loop that never ends
stops with a message rather than running for ever.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.canvas import run_check
from code_coach.canvas.content_farm import FARM_STEPS

HAS_NODE = shutil.which("node") is not None


def _step(step_id: str):
    return next(s for s in FARM_STEPS if s.id == step_id)


def _swap(code: str, old: str, new: str) -> str:
    assert code.count(old) >= 1, old
    return code.replace(old, new)


MISTAKES: dict[str, list[tuple[str, str]]] = {
    "farm-02-loop": [
        ("i < 12", "i < 11"),
    ],
    "farm-03-nested": [
        # Forgot to move down: the same row six times.
        ("    move('right');\n  }\n  move('down');\n", "    move('right');\n  }\n"),
    ],
    "farm-04-plant": [
        # Harvested straight after planting: nothing had time to grow.
        ("    plant();\n    move('right');", "    plant();\n    harvest();\n    move('right');"),
    ],
    "farm-05-if": [
        ("    if (canHarvest()) harvest();\n", "    harvest();\n"),
    ],
    "farm-06-function": [
        # Only ever goes right and down: fine from the corner, wrong after.
        ("  while (getX() > x) move('left');\n", ""),
    ],
    "farm-07-wrap": [
        # Always the right-hand way round, even when left is shorter.
        ("  if (right <= size / 2) {\n    for (let i = 0; i < right; i++) move('right');\n"
         "  } else {\n    for (let i = 0; i < size - right; i++) move('left');\n  }",
         "  for (let i = 0; i < right; i++) move('right');"),
    ],
    "farm-08-keep-going": [
        # if where while belongs: one round, then stops.
        ("while (numHarvested() < 50) {", "if (numHarvested() < 50) {"),
    ],
    "farm-09-clock": [
        # Correct, but two passes a round: too slow for the clock.
        ("function tend() {\n  if (canHarvest()) harvest();\n  if (isEmpty()) plant();\n}\n",
         "function tend() {\n  if (isEmpty()) plant();\n}\n"
         "function reap() {\n  for (let row = 0; row < 5; row++) {\n    for (let col = 0; col < 5; col++) {\n"
         "      if (canHarvest()) harvest();\n      move('right');\n    }\n    move('down');\n  }\n}\n"),
        ("    move('down');\n  }\n}\n", "    move('down');\n  }\n  reap();\n}\n"),
    ],
}

#: Changes applied together (the clock mistake above is two edits).
TOGETHER = {"farm-09-clock"}

OTHER_WAYS: dict[str, list[tuple[str, str]]] = {
    "farm-03-nested": [
        # Snaking: right along one row, left along the next.
        ("for (let row = 0; row < 6; row++) {\n  for (let col = 0; col < 6; col++) {\n"
         "    harvest();\n    move('right');\n  }\n  move('down');\n}\n",
         "for (let row = 0; row < 6; row++) {\n  const way = row % 2 === 0 ? 'right' : 'left';\n"
         "  for (let col = 0; col < 6; col++) {\n    harvest();\n    if (col < 5) move(way);\n  }\n"
         "  move('down');\n}\n"),
    ],
    "farm-06-function": [
        ("function goTo(x, y) {\n  while (getX() < x) move('right');\n  while (getX() > x) move('left');\n"
         "  while (getY() < y) move('down');\n  while (getY() > y) move('up');\n}\n",
         "function goTo(x, y) {\n  const dx = x - getX();\n  const dy = y - getY();\n"
         "  for (let i = 0; i < Math.abs(dx); i++) move(dx > 0 ? 'right' : 'left');\n"
         "  for (let i = 0; i < Math.abs(dy); i++) move(dy > 0 ? 'down' : 'up');\n}\n"),
    ],
}


class ShapeTests(unittest.TestCase):
    def test_ids_unique_and_named_for_the_track(self) -> None:
        ids = [s.id for s in FARM_STEPS]
        self.assertEqual(len(ids), len(set(ids)))
        for s in FARM_STEPS:
            with self.subTest(step=s.id):
                self.assertTrue(s.id.startswith("farm-"))
                self.assertEqual(s.track, "Farm")
                self.assertIn("__farm.setup(", s.world)
                self.assertGreater(len(s.teaches), 120)
                self.assertTrue(s.goal.endswith("."))

    def test_each_step_starts_where_the_last_one_finished(self) -> None:
        for before, after in zip(FARM_STEPS, FARM_STEPS[1:]):
            with self.subTest(step=after.id):
                self.assertEqual(after.starter, before.solution)

    def test_only_the_last_step_is_open(self) -> None:
        self.assertEqual([s.id for s in FARM_STEPS if not s.check], [FARM_STEPS[-1].id])


@unittest.skipUnless(HAS_NODE, "needs node")
class CheckTests(unittest.TestCase):
    def test_every_solution_passes_and_every_starter_fails(self) -> None:
        for s in FARM_STEPS:
            if not s.check:
                continue
            with self.subTest(step=s.id):
                good = run_check(s.solution, s.check, s.world)
                self.assertTrue(good.passed, good.message)
                bad = run_check(s.starter, s.check, s.world)
                self.assertFalse(bad.passed)
                self.assertTrue(bad.message)

    def test_real_mistakes_fail(self) -> None:
        for step_id, swaps in MISTAKES.items():
            s = _step(step_id)
            if step_id in TOGETHER:
                code = s.solution
                for old, new in swaps:
                    code = _swap(code, old, new)
                changes = [code]
            else:
                changes = [_swap(s.solution, old, new) for old, new in swaps]
            for code in changes:
                with self.subTest(step=step_id, code=code[:60]):
                    got = run_check(code, s.check, s.world)
                    self.assertFalse(got.passed, "the check let this mistake through")

    def test_other_right_answers_pass(self) -> None:
        for step_id, swaps in OTHER_WAYS.items():
            s = _step(step_id)
            for old, new in swaps:
                with self.subTest(step=step_id, change=new[:40]):
                    got = run_check(_swap(s.solution, old, new), s.check, s.world)
                    self.assertTrue(got.passed, got.message)

    def test_the_open_field_can_really_be_farmed(self) -> None:
        last = FARM_STEPS[-1]
        got = run_check(last.solution, "expect(__farm.harvested >= 200 && __farm.wasted === 0, 'no');", last.world)
        self.assertTrue(got.passed, got.message)


@unittest.skipUnless(HAS_NODE, "needs node")
class WorldTests(unittest.TestCase):
    world = FARM_STEPS[0].world

    def test_a_wrong_direction_is_named(self) -> None:
        got = run_check("move('north');", "", self.world)
        self.assertFalse(got.passed)
        self.assertIn("'up', 'down', 'left' and 'right'", got.message)
        self.assertIn("line 1", got.message)

    def test_a_loop_that_never_ends_is_stopped(self) -> None:
        for code in ("while (true) move('right');", "while (!isEmpty()) {}", "for (;;) canHarvest();"):
            with self.subTest(code=code):
                got = run_check(code, "", self.world)
                self.assertFalse(got.passed)
                self.assertTrue(
                    "never ends" in got.message,
                    got.message,
                )

    def test_the_field_wraps(self) -> None:
        got = run_check(
            "move('left'); move('up');",
            "expect(__farm.x === 2 && __farm.y === 2, `at ${__farm.x}, ${__farm.y}`);",
            self.world,
        )
        self.assertTrue(got.passed, got.message)

    def test_questions_are_free_and_actions_cost_a_tick(self) -> None:
        got = run_check(
            "canHarvest(); getX(); getY(); isEmpty(); getSize(); numHarvested(); move('right'); wait();",
            "expect(__farm.ticks === 2, `ticks ${__farm.ticks}`);",
            self.world,
        )
        self.assertTrue(got.passed, got.message)


if __name__ == "__main__":
    unittest.main()
