"""Canvas: the "Debug it" track.

Each step hands over a small, mostly working program with ONE bug. The suite
holds each step to: ids unique, only the last step open, every buggy starter
runs without throwing and draws something, FAILS its check with a message
that describes the symptom (not the cause), differs from its solution by a
small change, every solution passes, each plausible half-fix still fails, and
other valid fixes pass - the check plays the program at several frame rates
and reads only the names the goal states.
"""

from __future__ import annotations

import difflib
import re
import shutil
import unittest

from code_coach.canvas import run_check
from code_coach.canvas.content_debug import DEBUG_STEPS

HAS_NODE = shutil.which("node") is not None

# A change is a list of (old, new) swaps applied together to the BUGGY
# starter (a half-fix or another fix is a change to the program as handed
# over); each entry is (label, [swaps]).
Change = tuple[str, list[tuple[str, str]]]

#: A starter and its solution may differ by this many changed lines at most.
DIFF_LIMIT = 10


def _step(step_id: str):
    return next(s for s in DEBUG_STEPS if s.id == step_id)


def _apply(code: str, swaps: list[tuple[str, str]]) -> str:
    for old, new in swaps:
        assert code.count(old) == 1, old
        code = code.replace(old, new)
    return code


def _changed_lines(a: str, b: str) -> int:
    diff = difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=0)
    return sum(1 for line in diff if line[:1] in "+-" and not line.startswith(("+++", "---")))


# The names the check reads: the goal must name each one, in backticks.
NAMED_IN_SPEC: dict[str, list[str]] = {
    "dbg-01-frame-rate": ["square"],
    "dbg-02-extra-heart": ["lives"],
    "dbg-03-ghost-trails": ["player"],
    "dbg-04-near-miss": ["player", "spike", "touching"],
    "dbg-05-frozen-enemy": ["enemies"],
    "dbg-06-lights-out": ["lamps", "lit"],
    "dbg-07-sticky-keys": ["player"],
    "dbg-08-late-spawns": ["spawned"],
    "dbg-09-rich-coin": ["player", "coins", "score"],
    "dbg-10-life": ["grid"],
}

# Words that name the CAUSE. The goal and the failure message say what is
# wrong to look at, never where or why.
CAUSE_WORDS: dict[str, list[str]] = {
    "dbg-01-frame-rate": [r"\bdt\b", "delta"],
    "dbg-02-extra-heart": ["<=", "off-by-one", "loop"],
    "dbg-03-ghost-trails": ["clearRect", "clear"],
    "dbg-04-near-miss": ["<=", "less than"],
    "dbg-05-frozen-enemy": ["splice", "index", "skip"],
    "dbg-06-lights-out": [r"\bvar\b", "closure", r"\blet\b"],
    "dbg-07-sticky-keys": ["keyup"],
    "dbg-08-late-spawns": ["reset", "subtract", "spawnTimer"],
    "dbg-09-rich-coin": ["taken", "flag"],
    "dbg-10-life": ["copy", "alias", "reference", "slice", "same array"],
}

MISTAKES: dict[str, list[Change]] = {
    "dbg-01-frame-rate": [
        ("dt is used but the speed is still 4 pixels",
         [("square.x += square.speed;", "square.x += square.speed * dt;")]),
        ("the speed is 240 but still added per frame",
         [("speed: 4 }", "speed: 240 }")]),
        ("dt is capped at 60 Hz, so a slow screen is still slow",
         [("square.x += square.speed;", "square.x += 240 * Math.min(dt, 1 / 60);")]),
        ("tuned for 60 Hz only",
         [("square.x += square.speed;", "square.x += square.speed * (1 / 60) * 60;")]),
    ],
    "dbg-02-extra-heart": [
        ("lives starts one lower so the display looks right",
         [("let lives = 3;", "let lives = 2;")]),
        ("the extra square is hidden only at zero",
         [("for (let i = 0; i <= lives; i++) {", "for (let i = 0; i <= lives && lives > 0; i++) {")]),
        ("one too few now",
         [("for (let i = 0; i <= lives; i++) {", "for (let i = 1; i < lives; i++) {")]),
    ],
    "dbg-03-ghost-trails": [
        ("cleared after the square is drawn",
         [("  ctx.fillRect(player.x, player.y, player.size, player.size);\n}",
           "  ctx.fillRect(player.x, player.y, player.size, player.size);\n  ctx.clearRect(0, 0, canvas.width, canvas.height);\n}")]),
        ("the background is painted over the square",
         [("  ctx.fillStyle = 'tomato';\n  ctx.fillRect(player.x, player.y, player.size, player.size);\n}",
           "  ctx.fillStyle = 'tomato';\n  ctx.fillRect(player.x, player.y, player.size, player.size);\n"
           "  ctx.fillStyle = '#10141f';\n  ctx.fillRect(0, 0, canvas.width, canvas.height);\n}")]),
        ("only the top strip of the canvas is cleared",
         [("function draw() {\n", "function draw() {\n  ctx.clearRect(0, 0, canvas.width, 100);\n")]),
        ("only a thin strip behind the square is cleared",
         [("function draw() {\n", "function draw() {\n  ctx.clearRect(player.x - 10, player.y, 10, player.size);\n")]),
    ],
    "dbg-04-near-miss": [
        ("only the x edges are fixed",
         [("a.x <= b.x + b.w && a.x + a.w >= b.x && a.y <= b.y + b.h && a.y + a.h >= b.y",
           "a.x < b.x + b.w && a.x + a.w > b.x && a.y <= b.y + b.h && a.y + a.h >= b.y")]),
        ("only the y edges are fixed",
         [("a.x <= b.x + b.w && a.x + a.w >= b.x && a.y <= b.y + b.h && a.y + a.h >= b.y",
           "a.x <= b.x + b.w && a.x + a.w >= b.x && a.y < b.y + b.h && a.y + a.h > b.y")]),
        ("the boxes are shrunk so touching misses (but so does a small overlap)",
         [("a.x <= b.x + b.w && a.x + a.w >= b.x && a.y <= b.y + b.h && a.y + a.h >= b.y",
           "a.x < b.x + b.w - 4 && a.x + a.w > b.x + 4 && a.y < b.y + b.h - 4 && a.y + a.h > b.y + 4")]),
        ("only x is compared",
         [("a.x <= b.x + b.w && a.x + a.w >= b.x && a.y <= b.y + b.h && a.y + a.h >= b.y",
           "a.x < b.x + b.w && a.x + a.w > b.x")]),
    ],
    "dbg-05-frozen-enemy": [
        ("for...of still skips when an item is removed",
         [("  for (let i = 0; i < enemies.length; i++) {\n    const e = enemies[i];\n    e.y += e.speed * dt;\n"
           "    if (e.y > canvas.height) enemies.splice(i, 1);\n  }",
           "  for (const e of enemies) {\n    e.y += e.speed * dt;\n"
           "    if (e.y > canvas.height) enemies.splice(enemies.indexOf(e), 1);\n  }")]),
        ("forEach still skips when an item is removed",
         [("  for (let i = 0; i < enemies.length; i++) {\n    const e = enemies[i];\n    e.y += e.speed * dt;\n"
           "    if (e.y > canvas.height) enemies.splice(i, 1);\n  }",
           "  enemies.forEach((e, i) => {\n    e.y += e.speed * dt;\n"
           "    if (e.y > canvas.height) enemies.splice(i, 1);\n  });")]),
        ("it stops at the first removal, so only one leaves a frame",
         [("if (e.y > canvas.height) enemies.splice(i, 1);", "if (e.y > canvas.height) { enemies.splice(i, 1); break; }")]),
        ("backwards, but removal is put off by 200 px",
         [("  for (let i = 0; i < enemies.length; i++) {\n    const e = enemies[i];", "  for (let i = enemies.length - 1; i >= 0; i--) {\n    const e = enemies[i];"),
          ("if (e.y > canvas.height) enemies.splice", "if (e.y > canvas.height + 200) enemies.splice")]),
    ],
    "dbg-06-lights-out": [
        ("i declared with let before the loop is still one variable",
         [("for (var i = 0;", "let i;\nfor (i = 0;")]),
        ("i copied inside the callback is copied too late",
         [("    lit = i;", "    const n = i;\n    lit = n;")]),
        ("every timer lights the last lamp",
         [("    lit = i;", "    lit = lamps.length - 1;")]),
    ],
    "dbg-07-sticky-keys": [
        ("any key up lets go of both",
         [("  if (e.key === 'ArrowRight') held.right = false;\n", "  held.left = false;\n  held.right = false;\n")]),
        ("the left key is released under a name that never comes",
         [("  if (e.key === 'ArrowRight') held.right = false;\n",
           "  if (e.key === 'Left') held.left = false;\n  if (e.key === 'ArrowRight') held.right = false;\n")]),
        ("a typo makes a new property and leaves the flag alone",
         [("  if (e.key === 'ArrowRight') held.right = false;\n",
           "  if (e.key === 'ArrowLeft') held.lef = false;\n  if (e.key === 'ArrowRight') held.right = false;\n")]),
    ],
    "dbg-08-late-spawns": [
        ("the timer is never reset, so it spawns every frame",
         [("    spawnTimer = 0;\n", "")]),
        ("the wrong amount is subtracted",
         [("    spawnTimer = 0;\n", "    spawnTimer -= 1.2;\n")]),
        ("dt is subtracted instead of the interval",
         [("    spawnTimer = 0;\n", "    spawnTimer -= dt;\n")]),
    ],
    "dbg-09-rich-coin": [
        ("score is set, not added to",
         [("      score += 10;", "      score = 10;")]),
        ("break leaves the coin still paying every frame",
         [("      coin.taken = true;\n", "      coin.taken = true;\n      break;\n")]),
        ("tuned to the frame count of the first coin",
         [("      score += 10;", "      score += 10 / 30;")]),
    ],
    "dbg-10-life": [
        ("slice copies the outside only: the rows are shared",
         [("  const next = grid;\n", "  const next = grid.slice();\n")]),
        ("spread copies the outside only too",
         [("  const next = grid;\n", "  const next = [...grid];\n")]),
        ("fill puts the same row in every slot",
         [("  const next = grid;\n", "  const next = Array(ROWS).fill(Array(COLS).fill(0));\n")]),
        ("a real copy, but it never becomes the grid",
         [("  const next = grid;\n", "  const next = grid.map((row) => row.slice());\n"), ("  grid = next;\n", "")]),
    ],
}

OTHER_WAYS: dict[str, list[Change]] = {
    "dbg-01-frame-rate": [
        ("speed kept at 4 and scaled to a per-second one",
         [("square.x += square.speed;", "square.x += square.speed * 60 * dt;")]),
        ("a hard-coded speed per second",
         [("square.x += square.speed;", "square.x += 240 * dt;")]),
        ("the time since the last frame read from the clock",
         [("function update(dt) {\n  square.x += square.speed;",
           "let before = performance.now();\nfunction update() {\n  const now = performance.now();\n  square.x += 240 * ((now - before) / 1000);\n  before = now;")]),
    ],
    "dbg-02-extra-heart": [
        ("less than",
         [("i <= lives", "i < lives")]),
        ("counting from 1",
         [("for (let i = 0; i <= lives; i++) {\n    ctx.fillRect(12 + i * 28, 12, 20, 20);",
           "for (let i = 1; i <= lives; i++) {\n    ctx.fillRect(12 + (i - 1) * 28, 12, 20, 20);")]),
        ("a while loop",
         [("  for (let i = 0; i <= lives; i++) {\n    ctx.fillRect(12 + i * 28, 12, 20, 20);\n  }",
           "  let shown = 0;\n  while (shown < lives) {\n    ctx.fillRect(12 + shown * 28, 12, 20, 20);\n    shown += 1;\n  }")]),
    ],
    "dbg-03-ghost-trails": [
        ("background at the start of draw",
         [("function draw() {\n", "function draw() {\n  ctx.fillStyle = '#10141f';\n  ctx.fillRect(0, 0, canvas.width, canvas.height);\n")]),
        ("clearRect over the whole canvas",
         [("function draw() {\n", "function draw() {\n  ctx.clearRect(0, 0, canvas.width, canvas.height);\n")]),
        ("clearRect and then the background",
         [("function draw() {\n",
           "function draw() {\n  ctx.clearRect(0, 0, canvas.width, canvas.height);\n  ctx.fillStyle = '#10141f';\n  ctx.fillRect(0, 0, canvas.width, canvas.height);\n")]),
    ],
    "dbg-04-near-miss": [
        ("the no-overlap cases ruled out instead",
         [("a.x <= b.x + b.w && a.x + a.w >= b.x && a.y <= b.y + b.h && a.y + a.h >= b.y",
           "!(a.x + a.w <= b.x || b.x + b.w <= a.x || a.y + a.h <= b.y || b.y + b.h <= a.y)")]),
        ("distance between the centres",
         [("a.x <= b.x + b.w && a.x + a.w >= b.x && a.y <= b.y + b.h && a.y + a.h >= b.y",
           "Math.abs(a.x + a.w / 2 - (b.x + b.w / 2)) < (a.w + b.w) / 2 && Math.abs(a.y + a.h / 2 - (b.y + b.h / 2)) < (a.h + b.h) / 2")]),
    ],
    "dbg-05-frozen-enemy": [
        ("loop backwards",
         [("  for (let i = 0; i < enemies.length; i++) {\n    const e = enemies[i];", "  for (let i = enemies.length - 1; i >= 0; i--) {\n    const e = enemies[i];")]),
        ("step back after removing",
         [("enemies.splice(i, 1);", "{\n      enemies.splice(i, 1);\n      i--;\n    }")]),
        ("move first, then filter",
         [("  for (let i = 0; i < enemies.length; i++) {\n    const e = enemies[i];\n    e.y += e.speed * dt;\n"
           "    if (e.y > canvas.height) enemies.splice(i, 1);\n  }",
           "  for (const e of enemies) e.y += e.speed * dt;\n  enemies = enemies.filter((e) => e.y <= canvas.height);")]),
        ("filter first, then move",
         [("  for (let i = 0; i < enemies.length; i++) {\n    const e = enemies[i];\n    e.y += e.speed * dt;\n"
           "    if (e.y > canvas.height) enemies.splice(i, 1);\n  }",
           "  enemies = enemies.filter((e) => e.y <= canvas.height);\n  for (const e of enemies) e.y += e.speed * dt;")]),
    ],
    "dbg-06-lights-out": [
        ("let in the loop",
         [("for (var i = 0;", "for (let i = 0;")]),
        ("forEach gives each callback its own index",
         [("for (var i = 0; i < lamps.length; i++) {\n  setTimeout(() => {\n    lit = i;\n  }, (i + 1) * 1000);\n}",
           "lamps.forEach((lamp, n) => {\n  setTimeout(() => {\n    lit = n;\n  }, (n + 1) * 1000);\n});")]),
        ("a function that takes the number",
         [("for (var i = 0; i < lamps.length; i++) {\n  setTimeout(() => {\n    lit = i;\n  }, (i + 1) * 1000);\n}",
           "function light(n) {\n  setTimeout(() => {\n    lit = n;\n  }, (n + 1) * 1000);\n}\nfor (var i = 0; i < lamps.length; i++) light(i);")]),
        ("an immediately called function",
         [("  setTimeout(() => {\n    lit = i;\n  }, (i + 1) * 1000);",
           "  (function (n) {\n    setTimeout(() => {\n      lit = n;\n    }, (n + 1) * 1000);\n  })(i);")]),
    ],
    "dbg-07-sticky-keys": [
        ("a table of key names",
         [("  if (e.key === 'ArrowRight') held.right = false;\n",
           "  const side = { ArrowLeft: 'left', ArrowRight: 'right' }[e.key];\n  if (side) held[side] = false;\n")]),
        ("else if",
         [("  if (e.key === 'ArrowRight') held.right = false;\n",
           "  if (e.key === 'ArrowLeft') held.left = false;\n  else if (e.key === 'ArrowRight') held.right = false;\n")]),
    ],
    "dbg-08-late-spawns": [
        ("keep the remainder with %",
         [("    spawnTimer = 0;\n", "    spawnTimer %= 1;\n")]),
        ("catch up with a while loop",
         [("  if (spawnTimer >= 1) {\n    spawn();\n    spawnTimer = 0;\n  }",
           "  while (spawnTimer >= 1) {\n    spawn();\n    spawnTimer -= 1;\n  }")]),
        ("a timer on the clock instead",
         [("  spawnTimer += dt;\n  if (spawnTimer >= 1) {\n    spawn();\n    spawnTimer = 0;\n  }\n", ""),
          ("function update(dt) {", "setInterval(spawn, 1000);\n\nfunction update(dt) {")]),
    ],
    "dbg-09-rich-coin": [
        ("the taken test is put second",
         [("    if (overlaps(player, coin)) {", "    if (overlaps(player, coin) && !coin.taken) {")]),
        ("skip a coin that has been taken",
         [("    if (overlaps(player, coin)) {", "    if (coin.taken) continue;\n    if (overlaps(player, coin)) {")]),
        ("the coin is moved off the screen",
         [("      coin.taken = true;\n", "      coin.taken = true;\n      coin.x = -100;\n")]),
        ("taken coins are filtered out of the list",
         [("const coins = [", "let coins = ["),
          ("      coin.taken = true;\n    }\n  }\n}", "      coin.taken = true;\n    }\n  }\n  coins = coins.filter((c) => !c.taken);\n}")]),
    ],
    "dbg-10-life": [
        ("each row copied with map and spread",
         [("  const next = grid;\n", "  const next = grid.map((row) => [...row]);\n")]),
        ("a JSON round trip",
         [("  const next = grid;\n", "  const next = JSON.parse(JSON.stringify(grid));\n")]),
        ("Array.from on the rows",
         [("  const next = grid;\n", "  const next = Array.from(grid, (row) => Array.from(row));\n")]),
        ("a fresh empty grid, every cell written",
         [("  const next = grid;\n", "  const next = Array.from({ length: ROWS }, () => Array(COLS).fill(0));\n")]),
    ],
}

# A starter must run and draw before the check ever looks at it.
SMOKE = """
cc.frames(120);
expect(cc.drawn().length > 0, "The program drew nothing.");
"""


class ShapeTests(unittest.TestCase):
    def test_ids_are_unique_and_named_for_the_track(self) -> None:
        ids = [s.id for s in DEBUG_STEPS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len({s.title for s in DEBUG_STEPS}), len(DEBUG_STEPS))
        self.assertEqual(len(DEBUG_STEPS), 11)
        for n, s in enumerate(DEBUG_STEPS, start=1):
            with self.subTest(step=s.id):
                self.assertTrue(re.fullmatch(rf"dbg-{n:02d}-[a-z0-9-]+", s.id), s.id)
                self.assertEqual(s.track, "Debug it")
                self.assertEqual(s.language, "javascript")
                self.assertGreater(len(s.teaches), 120)
                self.assertTrue(s.goal.endswith("."))
                self.assertEqual(s.kind, "canvas")

    def test_only_the_last_step_is_open(self) -> None:
        self.assertEqual([s.id for s in DEBUG_STEPS if not s.check], [DEBUG_STEPS[-1].id])
        self.assertEqual(DEBUG_STEPS[-1].id, "dbg-11-break-your-own")

    def test_the_open_step_suggests_planting_bugs(self) -> None:
        open_step = DEBUG_STEPS[-1]
        self.assertGreater(len(open_step.teaches), 400)
        self.assertGreaterEqual(open_step.teaches.count(";"), 6)
        self.assertIn("friend", open_step.teaches + open_step.goal)
        self.assertEqual(open_step.starter, open_step.solution)
        self.assertIn("requestAnimationFrame", open_step.starter)

    def test_every_checked_step_has_a_hint_and_names_what_the_check_reads(self) -> None:
        for step_id, names in NAMED_IN_SPEC.items():
            s = _step(step_id)
            with self.subTest(step=step_id):
                self.assertTrue(s.hint)
                for name in names:
                    self.assertIn(f"`{name}`", s.goal)

    def test_the_goal_says_what_is_wrong_not_where(self) -> None:
        for step_id, words in CAUSE_WORDS.items():
            s = _step(step_id)
            for word in words:
                with self.subTest(step=step_id, word=word):
                    self.assertIsNone(re.search(word, s.goal), f"the goal gives away the cause: {word}")

    def test_every_checked_step_has_a_mistake_list(self) -> None:
        checked = {s.id for s in DEBUG_STEPS if s.check}
        self.assertEqual(set(NAMED_IN_SPEC), checked)
        self.assertEqual(set(CAUSE_WORDS), checked)
        for step_id in checked:
            with self.subTest(step=step_id):
                self.assertGreaterEqual(len(MISTAKES[step_id]), 2)
                self.assertGreaterEqual(len(OTHER_WAYS[step_id]), 1)
        ids = {s.id for s in DEBUG_STEPS}
        self.assertLessEqual(set(MISTAKES) | set(OTHER_WAYS), ids)

    def test_starters_are_their_own_buggy_programs_one_small_change_from_the_solution(self) -> None:
        for s in DEBUG_STEPS[:-1]:
            with self.subTest(step=s.id):
                self.assertNotEqual(s.starter, s.solution)
                changed = _changed_lines(s.starter, s.solution)
                self.assertGreater(changed, 0)
                self.assertLessEqual(changed, DIFF_LIMIT, "a starter should be one bug away from its solution")
                self.assertIn("const canvas = document.querySelector('canvas');", s.starter)
                self.assertIn("requestAnimationFrame", s.starter)
        # Independent steps: no starter is another step's solution.
        solutions = {s.solution for s in DEBUG_STEPS}
        for s in DEBUG_STEPS[:-1]:
            self.assertNotIn(s.starter, solutions)
        self.assertEqual(len({s.starter for s in DEBUG_STEPS}), len(DEBUG_STEPS))


@unittest.skipUnless(HAS_NODE, "needs node")
class CheckTests(unittest.TestCase):
    def test_every_solution_passes(self) -> None:
        for s in DEBUG_STEPS:
            if not s.check:
                continue
            with self.subTest(step=s.id):
                good = run_check(s.solution, s.check)
                self.assertTrue(good.passed, good.message)

    def test_every_buggy_starter_runs_and_draws_before_the_check(self) -> None:
        for s in DEBUG_STEPS:
            with self.subTest(step=s.id):
                got = run_check(s.starter, SMOKE)
                self.assertTrue(got.passed, got.message)

    def test_every_buggy_starter_fails_with_a_symptom(self) -> None:
        for s in DEBUG_STEPS:
            if not s.check:
                continue
            with self.subTest(step=s.id):
                bad = run_check(s.starter, s.check)
                self.assertFalse(bad.passed)
                self.assertGreater(len(bad.message), 40)
                self.assertNotIn("Your code threw", bad.message)
                self.assertNotIn("The check could not run", bad.message)
                for word in CAUSE_WORDS[s.id]:
                    self.assertIsNone(re.search(word, bad.message), f"the message names the cause ({word}): {bad.message}")

    def test_half_fixes_still_fail_and_say_what_is_wrong(self) -> None:
        for step_id, changes in MISTAKES.items():
            s = _step(step_id)
            for label, swaps in changes:
                with self.subTest(step=step_id, mistake=label):
                    got = run_check(_apply(s.starter, swaps), s.check)
                    self.assertFalse(got.passed, "the check let this half-fix through")
                    self.assertGreater(len(got.message), 20)
                    self.assertNotIn("Your code threw", got.message)

    def test_other_valid_fixes_pass(self) -> None:
        for step_id, changes in OTHER_WAYS.items():
            s = _step(step_id)
            for label, swaps in changes:
                with self.subTest(step=step_id, way=label):
                    got = run_check(_apply(s.starter, swaps), s.check)
                    self.assertTrue(got.passed, got.message)

    def test_the_timing_steps_are_played_at_more_than_one_frame_rate(self) -> None:
        for step_id in NAMED_IN_SPEC:
            if step_id in {"dbg-02-extra-heart", "dbg-04-near-miss", "dbg-10-life"}:
                continue  # nothing in these depends on the frame rate
            with self.subTest(step=step_id):
                check = _step(step_id).check
                self.assertIn("30", check)
                self.assertTrue("60" in check or "fps" in check)


if __name__ == "__main__":
    unittest.main()
