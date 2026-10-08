"""Canvas: the Platformer track.

Held to the same three things as the other tracks: each solution passes its
check, each starter fails it, and the mistakes people really make at that
step fail it too - here: gravity per frame instead of per second, a jump
while airborne, friction that depends on the frame rate, a tile test that
counts touching as overlapping, x and y moved together so the player sticks
to walls, tunnelling through a thin tile after a long frame, a one-way ledge
that lets go of a standing player (< for <=), a coyote timer never used up,
a coin that counts every frame.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.canvas import run_check
from code_coach.canvas.content_platformer import PLATFORMER_STEPS

HAS_NODE = shutil.which("node") is not None


def _step(step_id: str):
    return next(s for s in PLATFORMER_STEPS if s.id == step_id)


def _swap(code: str, old: str, new: str) -> str:
    assert code.count(old) >= 1, old
    return code.replace(old, new)


RIGHT_EDGE = "  const right = Math.ceil((player.x + player.w) / TILE) - 1;"
BOTTOM_EDGE = "  const bottom = Math.ceil((player.y + player.h) / TILE) - 1;"

MISTAKES: dict[str, list[tuple[str, str]]] = {
    "plat-01-gravity": [
        # Gravity per frame, not per second: right at 60 fps, wrong at 30.
        ("  player.vy += GRAVITY * dt;\n", "  player.vy += 30;\n"),
        # onGround set true on landing but never cleared.
        ("  player.onGround = false;\n", ""),
    ],
    "plat-02-jump": [
        # Jump while airborne.
        (" && player.onGround) {", ") {"),
        ("    player.vy = -JUMP;\n", "    player.vy = JUMP;\n"),
    ],
    "plat-03-run": [
        # Friction as a fraction per frame: depends on the frame rate.
        ("    player.vx = Math.max(0, player.vx - FRICTION * dt);",
         "    player.vx *= 0.9;"),
        # No top speed.
        ("  player.vx = Math.max(-MAX_SPEED, Math.min(MAX_SPEED, player.vx));\n", ""),
        # Speed set, not built up.
        ("    player.vx += dir * ACCEL * dt;", "    player.vx = dir * MAX_SPEED;"),
    ],
    "plat-04-tilemap": [
        # Row and column swapped.
        ("ctx.fillRect(col * TILE, row * TILE, TILE, TILE);",
         "ctx.fillRect(row * TILE, col * TILE, TILE, TILE);"),
        # Every tile drawn, air included.
        ("if (level[row][col] === '#') {", "if (level[row][col] !== 'x') {"),
    ],
    "plat-05-floor": [
        # Touching counts as overlapping: hovers beside a platform's edge.
        (RIGHT_EDGE, "  const right = Math.floor((player.x + player.w) / TILE);"),
        # A head bump treated as a landing.
        ("    if (player.vy > 0) {", "    if (true) {"),
    ],
    "plat-06-walls": [
        # Standing exactly on a tile counts as touching it from the side.
        (BOTTOM_EDGE, "  const bottom = Math.floor((player.y + player.h) / TILE);"),
        # Both axes moved, then y settled first: sticks to walls.
        ("  moveX(dt);\n  moveY(dt);\n",
         "  player.x += player.vx * dt;\n  player.y += player.vy * dt;\n  moveY(0);\n  moveX(0);\n"),
    ],
    "plat-07-fast": [
        # No cap on a long frame: tunnels through thin tiles.
        ("const dt = Math.min((time - last) / 1000, 1 / 30);", "const dt = (time - last) / 1000;"),
        # A cap that is too generous.
        ("1 / 30);", "0.25);"),
        # No terminal velocity.
        ("  player.vy = Math.min(player.vy, MAX_FALL);\n", ""),
    ],
    "plat-08-oneway": [
        # < for <=: lets go of a player who is already standing on it.
        ("  if (prevBottom > row * TILE) return -1;", "  if (prevBottom >= row * TILE) return -1;"),
        # Grabs a player whose feet were already below the top.
        ("  if (prevBottom > row * TILE) return -1;\n", ""),
        # Anything that is not air is a wall.
        ("  return tileAt(col, row) === '#';", "  return tileAt(col, row) !== '.';"),
    ],
    "plat-09-feel": [
        # The coyote time is never used up: a double jump.
        ("    player.coyote = 0;\n", ""),
        # A window so long it is a free air jump.
        ("const COYOTE = 0.1;", "const COYOTE = 0.5;"),
        # The jump is always cut, held or not.
        ("  if (!jumpHeld && player.vy < -JUMP_CUT)", "  if (player.vy < -JUMP_CUT)"),
    ],
    "plat-10-coins": [
        # A coin is never marked taken: counts every frame, never disappears.
        ("      c.taken = true;\n", ""),
        # Collected without touching.
        ("    if (dx < 8 + player.w / 2 && dy < 8 + player.h / 2) {", "    if (true) {"),
        # Taken coins still drawn.
        ("    if (c.taken) continue;\n    ctx.beginPath();", "    ctx.beginPath();"),
    ],
    "plat-11-goal": [
        # Respawns while standing on the floor.
        ("  if (player.y > canvas.height + 100) respawn();", "  if (player.y > 100) respawn();"),
        # Comes back still falling.
        ("  player.vx = 0;\n  player.vy = 0;\n}", "  player.vx = 0;\n}"),
        # Keeps playing after winning.
        ("  if (state !== 'playing') return;\n", ""),
    ],
    "plat-12-camera": [
        # Scrolls the wrong way.
        ("ctx.translate(-camera.x, 0);", "ctx.translate(camera.x, 0);"),
        # Not clamped at the left end.
        ("Math.max(0, Math.min(level[0].length * TILE - canvas.width, target))",
         "Math.min(level[0].length * TILE - canvas.width, target)"),
        # Aims the player's corner, not its centre.
        ("player.x + player.w / 2 - canvas.width / 2", "player.x - canvas.width / 2"),
        # The score drawn inside the scrolling world.
        ("  ctx.restore();\n", ""),
    ],
}

OTHER_WAYS: dict[str, list[tuple[str, str]]] = {
    "plat-03-run": [
        ("    player.vx = Math.max(0, player.vx - FRICTION * dt);",
         "    player.vx -= Math.min(player.vx, FRICTION * dt);"),
    ],
    "plat-05-floor": [
        # A tiny shrink of the box instead of ceil(...) - 1.
        (RIGHT_EDGE, "  const right = Math.floor((player.x + player.w - 0.001) / TILE);"),
        (BOTTOM_EDGE, "  const bottom = Math.floor((player.y + player.h - 0.001) / TILE);"),
    ],
    "plat-07-fast": [
        ("1 / 30);", "1 / 20);"),
    ],
    "plat-09-feel": [
        ("const COYOTE = 0.1;", "const COYOTE = 0.12;"),
    ],
    "plat-11-goal": [
        ("  if (player.y > canvas.height + 100) respawn();",
         "  if (player.y > level.length * TILE) respawn();"),
    ],
}


class ShapeTests(unittest.TestCase):
    def test_ids_are_unique_and_named_for_the_track(self) -> None:
        ids = [s.id for s in PLATFORMER_STEPS]
        self.assertEqual(len(ids), len(set(ids)))
        for n, s in enumerate(PLATFORMER_STEPS, 1):
            with self.subTest(step=s.id):
                self.assertTrue(s.id.startswith(f"plat-{n:02d}-"))
                self.assertEqual(s.track, "Platformer")
                self.assertGreater(len(s.teaches), 120)
                self.assertTrue(s.goal.endswith("."))
                self.assertTrue(s.hint or not s.check)

    def test_each_step_starts_where_the_last_one_finished(self) -> None:
        for before, after in zip(PLATFORMER_STEPS, PLATFORMER_STEPS[1:]):
            with self.subTest(step=after.id):
                self.assertEqual(after.starter, before.solution)

    def test_only_the_last_step_is_open(self) -> None:
        self.assertEqual(
            [s.id for s in PLATFORMER_STEPS if not s.check], [PLATFORMER_STEPS[-1].id]
        )

    def test_every_mistake_names_a_real_step(self) -> None:
        ids = {s.id for s in PLATFORMER_STEPS}
        self.assertLessEqual(set(MISTAKES) | set(OTHER_WAYS), ids)

    def test_every_checked_step_has_a_mistake(self) -> None:
        for s in PLATFORMER_STEPS:
            if s.check:
                with self.subTest(step=s.id):
                    self.assertTrue(MISTAKES.get(s.id))

    def test_the_map_is_a_rectangle_of_known_tiles(self) -> None:
        import re

        rows = re.findall(r"^  '([^']*)',$", _step("plat-04-tilemap").solution, re.M)
        self.assertEqual(len(rows), 10)
        self.assertEqual({len(r) for r in rows}, {30})
        self.assertLessEqual(set("".join(rows)), set("#.=oF"))


@unittest.skipUnless(HAS_NODE, "needs node")
class CheckTests(unittest.TestCase):
    def test_every_solution_passes_and_every_starter_fails(self) -> None:
        for s in PLATFORMER_STEPS:
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

    def test_a_check_is_the_same_on_a_slow_screen(self) -> None:
        # The step-1 check runs a long fall at 30 frames a second; the same
        # program must still pass when it is the only thing that changes.
        s = _step("plat-01-gravity")
        got = run_check(s.solution, s.check.replace("1000 / 30", "1000 / 20").replace("15, ", "10, "))
        self.assertTrue(got.passed, got.message)


if __name__ == "__main__":
    unittest.main()
