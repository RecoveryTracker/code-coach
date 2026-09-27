"""Canvas: the Dodge steps, their checks, and the routes that serve them.

A check plays the program in node, so it is held to three things here:
the step's own solution passes, its starter (the step before, finished)
does not, and the mistakes people really make at that step - moving per
frame instead of per second, forgetting keyup, <= in the collision - fail
it too. A check that passed those would be checking nothing.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.canvas import STEPS as ALL_STEPS
from code_coach.canvas import check_step, harness_source, run_check, step
from code_coach.canvas.content import STEPS

HAS_NODE = shutil.which("node") is not None


def _swap(code: str, old: str, new: str) -> str:
    assert code.count(old) >= 1, old
    return code.replace(old, new)


def _by_id(step_id: str):
    found = step(step_id)
    assert found is not None, step_id
    return found


#: Wrong programs, each a real mistake at that step, that the check must fail.
MISTAKES: dict[str, list[tuple[str, str, str]]] = {
    "dodge-02-background": [
        # The square first: the background paints over it.
        ("ctx.fillStyle = '#10141f';\nctx.fillRect(0, 0, canvas.width, canvas.height);\n\n"
         "ctx.fillStyle = 'tomato';\nctx.fillRect(100, 80, 40, 40);\n",
         "", "ctx.fillStyle = 'tomato';\nctx.fillRect(100, 80, 40, 40);\n"
         "ctx.fillStyle = '#10141f';\nctx.fillRect(0, 0, canvas.width, canvas.height);\n"),
    ],
    "dodge-04-loop": [
        ("  ctx.fillStyle = '#10141f';\n  ctx.fillRect(0, 0, canvas.width, canvas.height);\n\n", "", ""),
        ("  requestAnimationFrame(loop);\n}", "", "}"),
    ],
    "dodge-05-delta-time": [
        ("player.x += player.speed * dt;", "", "player.x += 4;"),
        ("const dt = (time - last) / 1000;", "", "const dt = time - last;"),
    ],
    "dodge-06-keys": [
        ("addEventListener('keyup', (e) => keys.delete(e.key));\n", "", ""),
        ("if (keys.has('ArrowRight')) player.x += player.speed * dt;",
         "", "if (keys.has('ArrowRight')) player.x += 2;"),
    ],
    "dodge-07-clamp": [
        ("Math.min(canvas.width - player.size, player.x)", "", "Math.min(canvas.width, player.x)"),
    ],
    "dodge-08-enemy": [
        ("for (const e of enemies) e.y += e.speed * dt;", "", "for (const e of enemies) e.y += 2;"),
        ("  for (const e of enemies) ctx.fillRect(e.x, e.y, e.size, e.size);\n", "", ""),
    ],
    "dodge-09-spawn": [
        ("  enemies = enemies.filter((e) => e.y < canvas.height);\n", "", ""),
        ("x: Math.random() * (canvas.width - 24)", "", "x: Math.random() * canvas.width + 24"),
    ],
    "dodge-10-collision": [
        ("return a.x < b.x + b.size && b.x < a.x + a.size &&",
         "", "return a.x <= b.x + b.size && b.x <= a.x + a.size &&"),
        ("  if (state !== 'playing') return;\n", "", ""),
    ],
    "dodge-11-score": [
        ("  score += dt;\n", "", "  score += 1;\n"),
        ("  ctx.fillText(`Score: ${Math.floor(score)}`, 10, 22);\n", "", ""),
    ],
    "dodge-12-restart": [
        ("  enemies = [];\n  spawnTimer = 0;\n  score = 0;\n", "", "  spawnTimer = 0;\n  score = 0;\n"),
        ("    ctx.fillText('Game over', 150, 150);\n", "", ""),
    ],
}

#: Right programs written another way, which the check must still pass.
OTHER_WAYS: dict[str, list[tuple[str, str]]] = {
    "dodge-06-keys": [
        ("addEventListener('keydown', (e) => keys.add(e.key));\n"
         "addEventListener('keyup', (e) => keys.delete(e.key));",
         "document.addEventListener('keydown', (event) => { keys.add(event.code); });\n"
         "window.addEventListener('keyup', (event) => { keys.delete(event.code); });"),
    ],
    "dodge-07-clamp": [
        ("  player.x = Math.max(0, Math.min(canvas.width - player.size, player.x));\n",
         "  if (player.x < 0) player.x = 0;\n"
         "  if (player.x > canvas.width - player.size) player.x = canvas.width - player.size;\n"),
    ],
    "dodge-04-loop": [
        ("  ctx.fillStyle = '#10141f';\n  ctx.fillRect(0, 0, canvas.width, canvas.height);\n",
         "  ctx.fillStyle = 'black';\n  ctx.fillRect(0, 0, 480, 320);\n"),
    ],
    "dodge-09-spawn": [
        # A plain timer reset instead of carrying the remainder: sloppier,
        # but still one enemy a second, so it passes.
        ("    spawnTimer -= 1;\n", "    spawnTimer = 0;\n"),
    ],
}


class ShapeTests(unittest.TestCase):
    def test_ids_unique_and_titles_present(self) -> None:
        ids = [s.id for s in STEPS]
        self.assertEqual(len(ids), len(set(ids)))
        for s in STEPS:
            with self.subTest(step=s.id):
                self.assertTrue(s.title)
                self.assertGreater(len(s.teaches), 120)
                self.assertTrue(s.goal.endswith("."))

    def test_each_step_starts_where_the_last_one_finished(self) -> None:
        for before, after in zip(STEPS, STEPS[1:]):
            with self.subTest(step=after.id):
                self.assertEqual(after.starter, before.solution)

    def test_only_the_last_step_is_open(self) -> None:
        self.assertEqual([s.id for s in STEPS if not s.check], [STEPS[-1].id])

    def test_every_mistake_and_other_way_names_a_real_step(self) -> None:
        for step_id in list(MISTAKES) + list(OTHER_WAYS):
            self.assertIsNotNone(step(step_id), step_id)

    def test_harness_keeps_its_names_off_the_page(self) -> None:
        # The learner writes `const canvas` and `const ctx`; the harness
        # must not have taken those names at the top level.
        text = harness_source()
        self.assertTrue(text.lstrip().startswith("//"))
        self.assertIn("(function () {", text)
        self.assertIn("W.__cc =", text)


@unittest.skipUnless(HAS_NODE, "needs node")
class CheckTests(unittest.TestCase):
    def test_every_solution_passes_its_check(self) -> None:
        for s in STEPS:
            if not s.check:
                continue
            with self.subTest(step=s.id):
                got = run_check(s.solution, s.check)
                self.assertTrue(got.passed, got.message)

    def test_every_starter_fails_its_check(self) -> None:
        for s in STEPS:
            if not s.check:
                continue
            with self.subTest(step=s.id):
                got = run_check(s.starter, s.check)
                self.assertFalse(got.passed)
                self.assertTrue(got.message)

    def test_real_mistakes_fail(self) -> None:
        for step_id, swaps in MISTAKES.items():
            s = _by_id(step_id)
            for old, _, new in swaps:
                with self.subTest(step=step_id, change=old[:40]):
                    got = run_check(_swap(s.solution, old, new), s.check)
                    self.assertFalse(got.passed, "the check let this mistake through")
                    self.assertTrue(got.message)

    def test_other_right_answers_pass(self) -> None:
        for step_id, swaps in OTHER_WAYS.items():
            s = _by_id(step_id)
            for old, new in swaps:
                with self.subTest(step=step_id, change=old[:40]):
                    got = run_check(_swap(s.solution, old, new), s.check)
                    self.assertTrue(got.passed, got.message)

    def test_a_crash_is_reported_with_its_line(self) -> None:
        s = STEPS[0]
        got = run_check(s.starter + "\nnope();\n", s.check)
        self.assertFalse(got.passed)
        self.assertIn("nope", got.message)
        self.assertIn("line", got.message)

    def test_an_endless_loop_is_reported_not_waited_on(self) -> None:
        s = STEPS[0]
        got = run_check(s.starter + "\nwhile (true) {}\n", s.check)
        self.assertFalse(got.passed)
        self.assertIn("loop that never ends", got.message)

    def test_the_open_step_always_passes(self) -> None:
        got = check_step(STEPS[-1].id, "")
        self.assertIsNotNone(got)
        self.assertTrue(got.passed)


@unittest.skipUnless(HAS_NODE, "needs node")
class RouteTests(unittest.TestCase):
    def test_list_ships_starters_not_solutions(self) -> None:
        from code_coach.api.server import canvas_list

        data = canvas_list()
        self.assertIn("__cc", data["harness"])
        self.assertEqual([s["id"] for s in data["steps"]], [s.id for s in ALL_STEPS])
        for s in data["steps"]:
            self.assertNotIn("solution", s)

    def test_a_pass_is_counted_and_a_fail_is_not(self) -> None:
        from code_coach.api.schemas import CanvasCheckRequest
        from code_coach.api.server import _store, canvas_check

        first = STEPS[0]
        bad = canvas_check(CanvasCheckRequest(step_id=first.id, code=first.starter))
        self.assertFalse(bad.passed)
        self.assertEqual(_store.load().canvas_counts().get(first.id, 0), 0)
        good = canvas_check(CanvasCheckRequest(step_id=first.id, code=first.solution))
        self.assertTrue(good.passed)
        self.assertEqual(good.done, 1)
        self.assertEqual(_store.load().canvas_counts()[first.id], 1)

    def test_answer_is_asked_for(self) -> None:
        from code_coach.api.server import canvas_answer

        self.assertEqual(canvas_answer(STEPS[3].id)["solution"], STEPS[3].solution)


if __name__ == "__main__":
    unittest.main()
