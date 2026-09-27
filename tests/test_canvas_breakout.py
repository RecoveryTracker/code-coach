"""Canvas: the Breakout track.

Held to the same three things as Dodge (test_canvas.py): each solution
passes its check, each starter fails it, and the mistakes people really
make at that step fail it too - here: a circle with no beginPath, a bounce
that flips but leaves the ball in the wall, the box test for a circle, a
lost life with no new serve, the mouse read in page pixels.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.canvas import run_check
from code_coach.canvas.content_breakout import BREAKOUT_STEPS

HAS_NODE = shutil.which("node") is not None


def _step(step_id: str):
    return next(s for s in BREAKOUT_STEPS if s.id == step_id)


def _swap(code: str, old: str, new: str) -> str:
    assert code.count(old) >= 1, old
    return code.replace(old, new)


MISTAKES: dict[str, list[tuple[str, str]]] = {
    "breakout-01-ball": [
        ("  ctx.beginPath();\n", ""),
        ("  ctx.fill();\n", "  ctx.stroke();\n"),
    ],
    "breakout-02-velocity": [
        ("  ball.y += ball.vy * dt;\n", "  ball.y -= ball.vy * dt;\n"),
    ],
    "breakout-03-walls": [
        # Turned round, but left partly inside the wall.
        ("    ball.x = canvas.width - ball.r;\n    ball.vx = -Math.abs(ball.vx);",
         "    ball.vx = -ball.vx;"),
    ],
    "breakout-05-paddle-bounce": [
        # The ball treated as a box: bounces off the air by the corners.
        ("  const cx = Math.max(r.x, Math.min(b.x, r.x + r.w));\n"
         "  const cy = Math.max(r.y, Math.min(b.y, r.y + r.h));\n"
         "  return (b.x - cx) ** 2 + (b.y - cy) ** 2 < b.r ** 2;",
         "  return b.x + b.r > r.x && b.x - b.r < r.x + r.w && b.y + b.r > r.y && b.y - b.r < r.y + r.h;"),
    ],
    "breakout-06-lives": [
        ("    else serve();\n", ""),
    ],
    "breakout-07-bricks": [
        ("x: 16 + col * 56, y: 30 + row * 22", "x: 16 + row * 56, y: 30 + row * 22"),
    ],
    "breakout-08-break": [
        ("      ball.vy = -ball.vy;\n", ""),
    ],
    "breakout-09-mouse": [
        ("  const mouseX = (e.clientX - box.left) * (canvas.width / box.width);",
         "  const mouseX = e.offsetX;"),
        ("  const mouseX = (e.clientX - box.left) * (canvas.width / box.width);",
         "  const mouseX = e.clientX - box.left;"),
    ],
    "breakout-10-win": [
        ("bricks.every((b) => !b.alive)", "bricks.some((b) => !b.alive)"),
    ],
    "breakout-11-aim": [
        # An angle, but the speed not kept.
        ("    ball.vx = speed * Math.sin(angle);\n    ball.vy = -speed * Math.cos(angle);",
         "    ball.vx = offset * 250;\n    ball.vy = -Math.abs(ball.vy);"),
    ],
}

OTHER_WAYS: dict[str, list[tuple[str, str]]] = {
    "breakout-05-paddle-bounce": [
        ("  return (b.x - cx) ** 2 + (b.y - cy) ** 2 < b.r ** 2;",
         "  return Math.hypot(b.x - cx, b.y - cy) < b.r;"),
    ],
    "breakout-09-mouse": [
        ("canvas.addEventListener('mousemove', (e) => {", "addEventListener('pointermove', (e) => {"),
    ],
    "breakout-07-bricks": [
        ("const bricks = [];\nfor (let row = 0; row < 5; row++) {\n  for (let col = 0; col < 8; col++) {\n"
         "    bricks.push({ x: 16 + col * 56, y: 30 + row * 22, w: 50, h: 16, alive: true });\n  }\n}",
         "const bricks = Array.from({ length: 40 }, (_, i) => ({\n"
         "  x: 16 + (i % 8) * 56, y: 30 + Math.floor(i / 8) * 22, w: 50, h: 16, alive: true,\n}));"),
    ],
}


class ShapeTests(unittest.TestCase):
    def test_ids_are_unique_and_named_for_the_track(self) -> None:
        ids = [s.id for s in BREAKOUT_STEPS]
        self.assertEqual(len(ids), len(set(ids)))
        for s in BREAKOUT_STEPS:
            with self.subTest(step=s.id):
                self.assertTrue(s.id.startswith("breakout-"))
                self.assertEqual(s.track, "Breakout")
                self.assertGreater(len(s.teaches), 120)
                self.assertTrue(s.goal.endswith("."))

    def test_each_step_starts_where_the_last_one_finished(self) -> None:
        for before, after in zip(BREAKOUT_STEPS, BREAKOUT_STEPS[1:]):
            with self.subTest(step=after.id):
                self.assertEqual(after.starter, before.solution)

    def test_only_the_last_step_is_open(self) -> None:
        self.assertEqual([s.id for s in BREAKOUT_STEPS if not s.check], [BREAKOUT_STEPS[-1].id])

    def test_every_mistake_names_a_real_step(self) -> None:
        ids = {s.id for s in BREAKOUT_STEPS}
        self.assertLessEqual(set(MISTAKES) | set(OTHER_WAYS), ids)


@unittest.skipUnless(HAS_NODE, "needs node")
class CheckTests(unittest.TestCase):
    def test_every_solution_passes_and_every_starter_fails(self) -> None:
        for s in BREAKOUT_STEPS:
            if not s.check:
                continue
            with self.subTest(step=s.id):
                good = run_check(s.solution, s.check)
                self.assertTrue(good.passed, good.message)
                bad = run_check(s.starter, s.check)
                self.assertFalse(bad.passed)
                self.assertTrue(bad.message)

    def test_real_mistakes_fail(self) -> None:
        for step_id, swaps in MISTAKES.items():
            s = _step(step_id)
            for old, new in swaps:
                with self.subTest(step=step_id, change=new[:40] or old[:40]):
                    got = run_check(_swap(s.solution, old, new), s.check)
                    self.assertFalse(got.passed, "the check let this mistake through")

    def test_other_right_answers_pass(self) -> None:
        for step_id, swaps in OTHER_WAYS.items():
            s = _step(step_id)
            for old, new in swaps:
                with self.subTest(step=step_id, change=new[:40]):
                    got = run_check(_swap(s.solution, old, new), s.check)
                    self.assertTrue(got.passed, got.message)


if __name__ == "__main__":
    unittest.main()
