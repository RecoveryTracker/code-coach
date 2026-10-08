"""Canvas: the Snake track.

Held to the same three things as Dodge and Breakout: each solution passes
its check, each starter fails it, and the mistakes people really make at
that step fail it too - here: moving every frame (or by counting frames)
instead of per tick, never removing the tail, a 180 degree reversal (and
the Up-then-Left slip), food on the snake, an off-by-one wall test, a tail
that counts as a collision, scoring on every tick, a restart that leaves
nextDir behind.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.canvas import run_check
from code_coach.canvas.content_snake import SNAKE_STEPS

HAS_NODE = shutil.which("node") is not None


def _step(step_id: str):
    return next(s for s in SNAKE_STEPS if s.id == step_id)


def _swap(code: str, old: str, new: str) -> str:
    assert code.count(old) >= 1, old
    return code.replace(old, new)


_TICK_BLOCK = "  acc += dt;\n  while (acc >= TICK) {\n    acc -= TICK;\n    step();\n  }\n"
_WALL_TEST = "head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS"

MISTAKES: dict[str, list[tuple[str, str]]] = {
    "snake-01-tiles": [
        ("const COLS = canvas.width / CELL;", "const COLS = canvas.width;"),
        ("ctx.fillRect(col * CELL, row * CELL,", "ctx.fillRect(row * CELL, col * CELL,"),
    ],
    "snake-02-snake": [
        # Only the head is drawn.
        ("  for (const s of snake) drawCell(s.x, s.y, '#68d391');",
         "  drawCell(snake[0].x, snake[0].y, '#68d391');"),
        # Pixels, not tiles.
        ("{ x: 12, y: 8 }, { x: 11, y: 8 }, { x: 10, y: 8 }];\n",
         "{ x: 240, y: 160 }, { x: 220, y: 160 }, { x: 200, y: 160 }];\n"),
    ],
    "snake-03-tick": [
        # One step per frame.
        (_TICK_BLOCK, "  step();\n"),
        # Time kept by counting frames: right at 60 a second, wrong at 30.
        (_TICK_BLOCK, "  update.n = (update.n || 0) + 1;\n  if (update.n % 7 === 0) step();\n"),
        # The tail never leaves.
        ("  snake.unshift(head);\n  snake.pop();", "  snake.unshift(head);"),
    ],
    "snake-04-steer": [
        # Up is down.
        ("ArrowUp: { x: 0, y: -1 }", "ArrowUp: { x: 0, y: 1 }"),
        ("  dir = nextDir;\n", ""),
    ],
    "snake-05-no-reverse": [
        # No protection at all.
        ("  if (turn.x === -dir.x && turn.y === -dir.y) return;\n", ""),
        # Judged against nextDir: Up then Left slips through.
        ("turn.x === -dir.x && turn.y === -dir.y", "turn.x === -nextDir.x && turn.y === -nextDir.y"),
    ],
    "snake-06-food": [
        # Any cell, snake or not.
        ("      if (!snake.some((s) => s.x === x && s.y === y)) free.push({ x, y });",
         "      free.push({ x, y });"),
        # Off by one: lets the food land one column past the grid.
        ("for (let x = 0; x < COLS; x++) {\n      if", "for (let x = 0; x <= COLS; x++) {\n      if"),
    ],
    "snake-07-grow": [
        # Always grows.
        ("  else snake.pop();\n", ""),
        # Never grows.
        ("spawnFood();\n  else snake.pop();", "spawnFood();\n  snake.pop();"),
    ],
    "snake-08-walls": [
        ("head.x >= COLS", "head.x > COLS"),
        ("head.y >= ROWS", "head.y > ROWS"),
        ("head.x >= COLS", "head.x >= COLS - 1"),
        # Moves into the wall, then notices.
        ("  if (head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS) {\n    state = 'over';\n    return;\n  }\n  snake.unshift(head);",
         "  snake.unshift(head);\n  if (head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS) {\n    state = 'over';\n    return;\n  }"),
    ],
    "snake-09-self": [
        # The tail counts even though it is moving away.
        ("  const body = eating ? snake : snake.slice(0, -1);\n", "  const body = snake;\n"),
        # The head finds itself.
        ("  const hitSelf = body.some((s) => s.x === head.x && s.y === head.y);\n  if (hitWall || hitSelf) {\n    state = 'over';\n    return;\n  }\n  snake.unshift(head);",
         "  snake.unshift(head);\n  const hitSelf = snake.some((s) => s.x === head.x && s.y === head.y);\n  if (hitWall || hitSelf) {\n    state = 'over';\n    return;\n  }"),
    ],
    "snake-10-score": [
        # Scores on every step that does not eat.
        ("    score += 10;\n    spawnFood();\n  } else {\n    snake.pop();",
         "    spawnFood();\n  } else {\n    score += 10;\n    snake.pop();"),
        # Never shown.
        ("  ctx.fillText(`Score: ${score}`, 10, 20);\n", ""),
    ],
    "snake-11-restart": [
        ("  nextDir = { x: 1, y: 0 };\n  acc = 0;", "  acc = 0;"),
        ("  score = 0;\n  state = 'playing';\n  spawnFood();\n}", "  state = 'playing';\n  spawnFood();\n}"),
        ("if (e.key === 'Enter' && state === 'over') reset();", "if (e.key === 'Enter') reset();"),
        ("if (e.key === 'Enter' && state === 'over') reset();", "if (state === 'over') reset();"),
    ],
}

OTHER_WAYS: dict[str, list[tuple[str, str]]] = {
    # A timer instead of an accumulator.
    "snake-03-tick": [
        (_TICK_BLOCK,
         "  if (!update.started) {\n    update.started = true;\n    setInterval(step, TICK * 1000);\n  }\n"),
    ],
    "snake-05-no-reverse": [
        ("turn.x === -dir.x && turn.y === -dir.y", "turn.x + dir.x === 0 && turn.y + dir.y === 0"),
    ],
    # Guess until it is free.
    "snake-06-food": [
        ("  const free = [];\n  for (let y = 0; y < ROWS; y++) {\n    for (let x = 0; x < COLS; x++) {\n"
         "      if (!snake.some((s) => s.x === x && s.y === y)) free.push({ x, y });\n    }\n  }\n"
         "  food = free[Math.floor(Math.random() * free.length)];",
         "  do {\n    food = { x: Math.floor(Math.random() * COLS), y: Math.floor(Math.random() * ROWS) };\n"
         "  } while (snake.some((s) => s.x === food.x && s.y === food.y));"),
    ],
    "snake-08-walls": [
        (_WALL_TEST, "!(head.x >= 0 && head.x < COLS && head.y >= 0 && head.y < ROWS)"),
    ],
    "snake-09-self": [
        ("  const body = eating ? snake : snake.slice(0, -1);\n",
         "  const body = snake.slice(0, eating ? snake.length : -1);\n"),
    ],
}


class ShapeTests(unittest.TestCase):
    def test_ids_are_unique_and_named_for_the_track(self) -> None:
        ids = [s.id for s in SNAKE_STEPS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(SNAKE_STEPS), 12)
        for i, s in enumerate(SNAKE_STEPS, start=1):
            with self.subTest(step=s.id):
                self.assertTrue(s.id.startswith(f"snake-{i:02d}-"))
                self.assertEqual(s.track, "Snake")
                self.assertGreater(len(s.teaches), 120)
                self.assertTrue(s.goal.endswith("."))
                if s.check:
                    self.assertTrue(s.hint)

    def test_each_step_starts_where_the_last_one_finished(self) -> None:
        for before, after in zip(SNAKE_STEPS, SNAKE_STEPS[1:]):
            with self.subTest(step=after.id):
                self.assertEqual(after.starter, before.solution)

    def test_only_the_last_step_is_open(self) -> None:
        self.assertEqual([s.id for s in SNAKE_STEPS if not s.check], [SNAKE_STEPS[-1].id])

    def test_every_mistake_names_a_real_step(self) -> None:
        ids = {s.id for s in SNAKE_STEPS}
        self.assertLessEqual(set(MISTAKES) | set(OTHER_WAYS), ids)

    def test_every_checked_step_has_a_mistake(self) -> None:
        checked = {s.id for s in SNAKE_STEPS if s.check}
        self.assertEqual(checked - set(MISTAKES), set())


@unittest.skipUnless(HAS_NODE, "needs node")
class CheckTests(unittest.TestCase):
    def test_every_solution_passes_and_every_starter_fails(self) -> None:
        for s in SNAKE_STEPS:
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
