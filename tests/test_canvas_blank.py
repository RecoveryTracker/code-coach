"""Canvas: the "From blank" track.

Unlike the other tracks these steps are independent: each starter is blank,
not the step before. So the suite holds each project to: ids unique, only the
last step open, every blank starter FAILS its check, every solution passes,
each real mistake fails (with a message that says what is wrong), and other
ways of writing the same behaviour pass - the check plays the program and
reads only the names the spec states.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.canvas import run_check
from code_coach.canvas.content_blank import BLANK_STEPS

HAS_NODE = shutil.which("node") is not None

# A change is a list of (old, new) swaps applied together; each entry is
# (label, [swaps]).
Change = tuple[str, list[tuple[str, str]]]


def _step(step_id: str):
    return next(s for s in BLANK_STEPS if s.id == step_id)


def _apply(code: str, swaps: list[tuple[str, str]]) -> str:
    for old, new in swaps:
        assert code.count(old) >= 1, old
        code = code.replace(old, new)
    return code


# The names the check reads: the goal must name each one, in backticks.
NAMED_IN_SPEC: dict[str, list[str]] = {
    "blank-01-pong": ["left", "right", "ball", "score.left", "score.right"],
    "blank-02-flappy": ["bird", "pipes", "score", "state"],
    "blank-03-memory": ["cards", "state"],
    "blank-04-stacker": ["grid", "piece", "score", "state"],
}

MISTAKES: dict[str, list[Change]] = {
    "blank-01-pong": [
        ("no clamp: paddles leave the canvas",
         [("  p.y = Math.max(0, Math.min(canvas.height - p.h, p.y));\n", "")]),
        ("paddle speed per frame, not per second",
         [("if (keys.has(up)) p.y -= p.speed * dt;", "if (keys.has(up)) p.y -= 5;"),
          ("if (keys.has(down)) p.y += p.speed * dt;", "if (keys.has(down)) p.y += 5;")]),
        ("the paddle test ignores where the paddle is vertically",
         [("  return (b.x - cx) ** 2 + (b.y - cy) ** 2 < b.r ** 2;",
           "  return b.x - b.r < p.x + p.w && b.x + b.r > p.x;")]),
        ("points go to the wrong player",
         [("    score.right += 1;\n    serve(-1);", "    score.left += 1;\n    serve(-1);"),
          ("    score.left += 1;\n    serve(1);", "    score.right += 1;\n    serve(1);")]),
        ("no serve after a point",
         [("    score.right += 1;\n    serve(-1);", "    score.right += 1;")]),
        ("served away from the loser",
         [("    serve(-1);", "    serve(1);")]),
        ("r does not put the paddles back",
         [("  left.y = 130;\n  right.y = 130;\n  serve(1);", "  serve(1);")]),
        ("no bounce off the bottom edge",
         [("    ball.y = canvas.height - ball.r;\n    ball.vy = -Math.abs(ball.vy);\n", "")]),
    ],
    "blank-02-flappy": [
        ("flap adds to vy instead of setting it",
         [("if (state === 'playing') bird.vy = -300;", "if (state === 'playing') bird.vy -= 300;")]),
        ("a pipe is counted every frame once passed",
         [("if (!p.passed && p.x + p.w < bird.x) {", "if (p.x + p.w < bird.x) {")]),
        ("hits any pipe's gap height, wherever the pipe is",
         [("    if (hitsRect(p.x, 0, p.w, p.gapY) || hitsRect(p.x, p.gapY + p.gapH, p.w, canvas.height)) {",
           "    if (bird.y - bird.r < p.gapY || bird.y + bird.r > p.gapY + p.gapH) {")]),
        ("pipes are never removed",
         [("  while (pipes.length && pipes[0].x + pipes[0].w < 0) pipes.shift();\n", "")]),
        ("gravity per frame, not per second",
         [("  bird.vy += 900 * dt;", "  bird.vy += 15;")]),
        ("pipes move per frame, not per second",
         [("    p.x -= 150 * dt;", "    p.x -= 2.5;")]),
        ("everything keeps moving after game over",
         [("  if (state !== 'playing') return;\n  bird.vy", "  bird.vy")]),
        ("restart leaves the old pipes",
         [("  pipes.length = 0;\n  spawnTimer = 0;", "  spawnTimer = 0;")]),
        ("the floor is safe",
         [("if (bird.y - bird.r < 0 || bird.y + bird.r > canvas.height) state = 'over';",
           "if (bird.y - bird.r < 0) state = 'over';")]),
        ("the restart press also flaps",
         [("  else restart();", "  else {\n    restart();\n    bird.vy = -300;\n  }")]),
    ],
    "blank-03-memory": [
        ("mismatch flips back too soon",
         [("    }, 800);", "    }, 100);")]),
        ("a third card can be turned while two are showing",
         [("  if (locked || state !== 'playing') return;", "  if (state !== 'playing') return;")]),
        ("click read in page pixels, not canvas pixels",
         [("  const x = (e.clientX - box.left) * (canvas.width / box.width);",
           "  const x = e.clientX - box.left;"),
          ("  const y = (e.clientY - box.top) * (canvas.height / box.height);",
           "  const y = e.clientY - box.top;")]),
        ("a face-up card can be clicked again and matches itself",
         [("cards.find((c) => !c.faceUp && x >= c.x", "cards.find((c) => x >= c.x")]),
        ("any one match wins",
         [("if (cards.every((c) => c.matched)) state = 'won';", "if (cards.some((c) => c.matched)) state = 'won';")]),
        ("a pair is never marked matched",
         [("    a.matched = true;\n    second.matched = true;\n", "")]),
        ("face-down cards show their value",
         [("    if (c.faceUp) {\n      ctx.fillStyle = '#10141f';", "    {\n      ctx.fillStyle = '#10141f';")]),
        ("not shuffled",
         [("  const j = Math.floor(Math.random() * (i + 1));", "  const j = i;")]),
    ],
    "blank-04-stacker": [
        ("landing ignores filled cells",
         [("if (c < 0 || c >= COLS || r >= ROWS || grid[r][c]) return false;",
           "if (c < 0 || c >= COLS || r >= ROWS) return false;")]),
        ("a full row is zeroed but the rows above stay put",
         [("      grid.splice(r, 1);\n      grid.unshift(Array(COLS).fill(0));\n", "      grid[r].fill(0);\n")]),
        ("a row with any cell filled is cleared",
         [("if (grid[r].every((v) => v)) {", "if (grid[r].some((v) => v)) {")]),
        ("no wall check",
         [("if (c < 0 || c >= COLS || r >= ROWS || grid[r][c]) return false;",
           "if (r >= ROWS || grid[r][c]) return false;")]),
        ("no game over",
         [("  if (!fits(piece.col, piece.row)) state = 'over';\n", "")]),
        ("rows clear but the score does not move",
         [("      score += 10;\n", "")]),
        ("only one row is cleared at a time",
         [("      score += 10;\n      r++;\n", "      score += 10;\n      break;\n")]),
        ("Enter does not restart",
         [("    if (e.key === 'Enter') restart();\n", "")]),
        ("gravity every frame",
         [("  if (timer >= 0.5) {\n    timer -= 0.5;\n    stepDown();\n  }", "  stepDown();")]),
    ],
}

OTHER_WAYS: dict[str, list[Change]] = {
    "blank-01-pong": [
        ("keys by e.code",
         [("keys.add(e.key);", "keys.add(e.code);"),
          ("keys.delete(e.key)", "keys.delete(e.code)"),
          ("movePaddle(left, 'w', 's', dt);", "movePaddle(left, 'KeyW', 'KeyS', dt);")]),
        ("the ball as a box against the paddle",
         [("  return (b.x - cx) ** 2 + (b.y - cy) ** 2 < b.r ** 2;",
           "  return b.x + b.r > p.x && b.x - b.r < p.x + p.w && b.y + b.r > p.y && b.y - b.r < p.y + p.h;")]),
        ("scores with ++",
         [("score.right += 1;", "score.right++;"), ("score.left += 1;", "score.left++;")]),
        ("paddles in an array",
         [("function update(dt) {\n  movePaddle(left, 'w', 's', dt);\n  movePaddle(right, 'ArrowUp', 'ArrowDown', dt);\n",
           "const controls = [[left, 'w', 's'], [right, 'ArrowUp', 'ArrowDown']];\n"
           "function update(dt) {\n  for (const [p, up, down] of controls) movePaddle(p, up, down, dt);\n")]),
    ],
    "blank-02-flappy": [
        ("position before velocity",
         [("  bird.vy += 900 * dt;\n  bird.y += bird.vy * dt;", "  bird.y += bird.vy * dt;\n  bird.vy += 900 * dt;")]),
        ("the bird as a box",
         [("  const cx = Math.max(rx, Math.min(bird.x, rx + rw));\n"
           "  const cy = Math.max(ry, Math.min(bird.y, ry + rh));\n"
           "  return (bird.x - cx) ** 2 + (bird.y - cy) ** 2 < bird.r ** 2;",
           "  return bird.x + bird.r > rx && bird.x - bird.r < rx + rw && bird.y + bird.r > ry && bird.y - bird.r < ry + rh;")]),
        ("pipes spawned by setInterval",
         [("  spawnTimer += dt;\n  if (spawnTimer >= 1.5) {\n    spawnTimer -= 1.5;\n    spawnPipe();\n  }\n", ""),
          ("function update(dt) {",
           "setInterval(() => {\n  if (state === 'playing') spawnPipe();\n}, 1500);\n\nfunction update(dt) {")]),
        ("pipes rebuilt with filter",
         [("const pipes = [];", "let pipes = [];"),
          ("  pipes.length = 0;\n  spawnTimer = 0;", "  pipes = [];\n  spawnTimer = 0;"),
          ("  while (pipes.length && pipes[0].x + pipes[0].w < 0) pipes.shift();",
           "  pipes = pipes.filter((p) => p.x + p.w >= 0);")]),
    ],
    "blank-03-memory": [
        ("listening on the document",
         [("canvas.addEventListener('click', (e) => {", "document.addEventListener('click', (e) => {")]),
        ("the lock worked out from the cards",
         [("  if (locked || state !== 'playing') return;",
           "  if (cards.filter((c) => c.faceUp && !c.matched).length >= 2 || state !== 'playing') return;")]),
        ("shuffled with sort",
         [("for (let i = values.length - 1; i > 0; i--) {\n"
           "  const j = Math.floor(Math.random() * (i + 1));\n"
           "  [values[i], values[j]] = [values[j], values[i]];\n}",
           "values.sort(() => Math.random() - 0.5);")]),
        ("a slower flip back",
         [("    }, 800);", "    }, 900);")]),
    ],
    "blank-04-stacker": [
        ("clearing rows with filter",
         [("function clearLines() {\n"
           "  for (let r = ROWS - 1; r >= 0; r--) {\n"
           "    if (grid[r].every((v) => v)) {\n"
           "      grid.splice(r, 1);\n"
           "      grid.unshift(Array(COLS).fill(0));\n"
           "      score += 10;\n"
           "      r++;\n"
           "    }\n"
           "  }\n"
           "}",
           "function clearLines() {\n"
           "  const kept = grid.filter((row) => !row.every((v) => v));\n"
           "  score += 10 * (ROWS - kept.length);\n"
           "  while (kept.length < ROWS) kept.unshift(Array(COLS).fill(0));\n"
           "  grid.splice(0, ROWS, ...kept);\n"
           "}")]),
        ("gravity by setInterval",
         [("function update(dt) {\n  if (state !== 'playing') return;\n  timer += dt;\n"
           "  if (timer >= 0.5) {\n    timer -= 0.5;\n    stepDown();\n  }\n}",
           "setInterval(() => {\n  if (state === 'playing') stepDown();\n}, 500);\n\nfunction update() {}")]),
        ("a drop that steps down until it locks",
         [("    while (fits(piece.col, piece.row + 1)) piece.row += 1;\n    lock();",
           "    let landed = false;\n    while (!landed) {\n"
           "      if (fits(piece.col, piece.row + 1)) piece.row += 1;\n"
           "      else {\n        lock();\n        landed = true;\n      }\n    }")]),
    ],
}


class ShapeTests(unittest.TestCase):
    def test_ids_are_unique_and_named_for_the_track(self) -> None:
        ids = [s.id for s in BLANK_STEPS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len({s.title for s in BLANK_STEPS}), len(BLANK_STEPS))
        for s in BLANK_STEPS:
            with self.subTest(step=s.id):
                self.assertTrue(s.id.startswith("blank-"))
                self.assertEqual(s.track, "From blank")
                self.assertGreater(len(s.teaches), 120)
                self.assertTrue(s.goal.endswith("."))
                self.assertEqual(s.kind, "canvas")

    def test_only_the_last_step_is_open(self) -> None:
        self.assertEqual([s.id for s in BLANK_STEPS if not s.check], [BLANK_STEPS[-1].id])
        self.assertEqual(BLANK_STEPS[-1].id, "blank-05-yours")

    def test_the_open_step_has_a_brainstorm_list(self) -> None:
        open_step = BLANK_STEPS[-1]
        self.assertGreater(len(open_step.teaches), 400)
        self.assertGreaterEqual(open_step.teaches.count(";"), 6)

    def test_starters_are_blank_and_independent(self) -> None:
        for s in BLANK_STEPS:
            with self.subTest(step=s.id):
                self.assertLess(len(s.starter), 200)
                self.assertIn("const canvas = document.querySelector('canvas');", s.starter)
                self.assertIn("getContext('2d')", s.starter)
                self.assertNotIn("function", s.starter)
                self.assertNotIn("requestAnimationFrame", s.starter)
        self.assertEqual(len({s.starter for s in BLANK_STEPS}), 1)
        for s in BLANK_STEPS[:-1]:
            self.assertNotEqual(s.starter, s.solution)

    def test_each_goal_is_a_numbered_spec_that_names_what_the_check_reads(self) -> None:
        for step_id, names in NAMED_IN_SPEC.items():
            s = _step(step_id)
            with self.subTest(step=step_id):
                self.assertTrue(s.hint)
                numbers = [f"{n}) " for n in range(1, 7)]
                self.assertTrue(all(n in s.goal for n in numbers), "numbered requirements 1) to 6)")
                for name in names:
                    self.assertIn(f"`{name}`", s.goal)

    def test_every_checked_step_has_a_mistake_list(self) -> None:
        checked = {s.id for s in BLANK_STEPS if s.check}
        self.assertEqual(set(NAMED_IN_SPEC), checked)
        for step_id in checked:
            with self.subTest(step=step_id):
                self.assertGreaterEqual(len(MISTAKES[step_id]), 2)
                self.assertGreaterEqual(len(OTHER_WAYS[step_id]), 1)
        ids = {s.id for s in BLANK_STEPS}
        self.assertLessEqual(set(MISTAKES) | set(OTHER_WAYS), ids)


@unittest.skipUnless(HAS_NODE, "needs node")
class CheckTests(unittest.TestCase):
    def test_every_solution_passes(self) -> None:
        for s in BLANK_STEPS:
            if not s.check:
                continue
            with self.subTest(step=s.id):
                good = run_check(s.solution, s.check)
                self.assertTrue(good.passed, good.message)

    def test_every_blank_starter_fails_with_a_message(self) -> None:
        for s in BLANK_STEPS:
            if not s.check:
                continue
            with self.subTest(step=s.id):
                bad = run_check(s.starter, s.check)
                self.assertFalse(bad.passed)
                self.assertTrue(bad.message)
                self.assertNotIn("Your code threw", bad.message)
                self.assertTrue(bad.message.startswith("Requirement"), bad.message)

    def test_real_mistakes_fail_and_say_what_is_wrong(self) -> None:
        for step_id, changes in MISTAKES.items():
            s = _step(step_id)
            for label, swaps in changes:
                with self.subTest(step=step_id, mistake=label):
                    got = run_check(_apply(s.solution, swaps), s.check)
                    self.assertFalse(got.passed, "the check let this mistake through")
                    self.assertTrue(got.message.startswith("Requirement"), got.message)

    def test_other_right_answers_pass(self) -> None:
        for step_id, changes in OTHER_WAYS.items():
            s = _step(step_id)
            for label, swaps in changes:
                with self.subTest(step=step_id, way=label):
                    got = run_check(_apply(s.solution, swaps), s.check)
                    self.assertTrue(got.passed, got.message)


if __name__ == "__main__":
    unittest.main()
