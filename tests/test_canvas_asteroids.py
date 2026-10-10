"""Canvas: the Asteroids track.

Held to the same three things as the other tracks: each solution passes its
check, each starter fails it, and the mistakes people really make at that
step fail it too - here: turning by degrees or per frame, thrust added to
the position instead of the velocity, sin for x and cos for y, friction as a
number per frame (or a fixed amount taken away), a wrap that only knows
about one edge, bullets that never expire, a cooldown (or protection)
counted in frames, a square collision test instead of a circle, a rock that
splits without being removed, and lives lost on every frame of the
invulnerability.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.canvas import run_check
from code_coach.canvas.content_asteroids import ASTEROIDS_STEPS

HAS_NODE = shutil.which("node") is not None


def _step(step_id: str):
    return next(s for s in ASTEROIDS_STEPS if s.id == step_id)


def _swap(code: str, old: str, new: str) -> str:
    assert code.count(old) >= 1, old
    return code.replace(old, new)


THRUST_LINES = (
    "    ship.vx += Math.cos(ship.angle) * THRUST * dt;\n"
    "    ship.vy += Math.sin(ship.angle) * THRUST * dt;"
)
WRAP_BODY = (
    "  if (o.x < -o.r) o.x = canvas.width + o.r;\n"
    "  else if (o.x > canvas.width + o.r) o.x = -o.r;\n"
    "  if (o.y < -o.r) o.y = canvas.height + o.r;\n"
    "  else if (o.y > canvas.height + o.r) o.y = -o.r;\n"
)
OVERLAP = "  return Math.hypot(a.x - b.x, a.y - b.y) < a.r + b.r;"
TWO_PIECES = (
    "    rocks.push(makeRock(rk.x, rk.y, rk.size - 1));\n"
    "    rocks.push(makeRock(rk.x, rk.y, rk.size - 1));"
)
BLINK = "  if (ship.invuln <= 0 || Math.floor(ship.invuln * 10) % 2 === 0) drawShip();\n"

MISTAKES: dict[str, list[tuple[str, str]]] = {
    "ast-01-turn": [
        # Degrees where radians are needed.
        ("const TURN = 4;", "const TURN = 230;"),
        # A turn per frame: right at 60 a second, wrong at 30.
        ("  ship.angle += turn * TURN * dt;", "  ship.angle += turn * 0.07;"),
        # Left and right the wrong way round.
        ("const turn = (keys.has('ArrowRight') ? 1 : 0) - (keys.has('ArrowLeft') ? 1 : 0);",
         "const turn = (keys.has('ArrowLeft') ? 1 : 0) - (keys.has('ArrowRight') ? 1 : 0);"),
        # Drawn without turning.
        ("  ctx.rotate(ship.angle);\n", ""),
        # Drawn about the corner of the canvas, not the ship.
        ("  ctx.translate(ship.x, ship.y);\n", ""),
    ],
    "ast-02-thrust": [
        # Thrust moves the ship directly: no glide, no velocity.
        (THRUST_LINES,
         "    ship.x += Math.cos(ship.angle) * THRUST * dt;\n"
         "    ship.y += Math.sin(ship.angle) * THRUST * dt;"),
        # Sin for x and cos for y.
        (THRUST_LINES,
         "    ship.vx += Math.sin(ship.angle) * THRUST * dt;\n"
         "    ship.vy += Math.cos(ship.angle) * THRUST * dt;"),
        # Thrust per frame, not per second.
        (THRUST_LINES,
         "    ship.vx += Math.cos(ship.angle) * THRUST / 60;\n"
         "    ship.vy += Math.sin(ship.angle) * THRUST / 60;"),
        # Always thrusting.
        ("  if (keys.has('ArrowUp')) {", "  if (true) {"),
        # Velocity never moves the ship.
        ("  ship.x += ship.vx * dt;\n  ship.y += ship.vy * dt;\n", ""),
    ],
    "ast-03-friction": [
        # A fraction per frame: depends on the frame rate.
        ("  const damp = Math.pow(DRAG, dt);", "  const damp = 0.99;"),
        # Only x is slowed: the ship's direction drifts.
        ("  ship.vy *= damp;\n", ""),
        # A fixed amount taken away, not a fraction.
        ("  ship.vx *= damp;\n  ship.vy *= damp;",
         "  const sp = Math.hypot(ship.vx, ship.vy);\n"
         "  const k = Math.max(0, sp - 40 * dt) / (sp || 1);\n"
         "  ship.vx *= k;\n  ship.vy *= k;"),
        # No friction at all.
        ("  ship.vx *= damp;\n  ship.vy *= damp;\n", ""),
    ],
    "ast-04-wrap": [
        # A single if per axis: only the right and bottom edges.
        (WRAP_BODY,
         "  if (o.x > canvas.width + o.r) o.x = -o.r;\n"
         "  if (o.y > canvas.height + o.r) o.y = -o.r;\n"),
        # JavaScript's % keeps the sign: a negative never comes back.
        (WRAP_BODY, "  o.x %= canvas.width;\n  o.y %= canvas.height;\n"),
        # Only the x axis.
        ("  if (o.y < -o.r) o.y = canvas.height + o.r;\n  else if (o.y > canvas.height + o.r) o.y = -o.r;\n", ""),
        # Sent to the wrong place.
        ("else if (o.x > canvas.width + o.r) o.x = -o.r;",
         "else if (o.x > canvas.width + o.r) o.x = canvas.width;"),
        # Never called.
        ("  wrap(ship);\n", ""),
    ],
    "ast-05-bullets": [
        # Sin for x and cos for y.
        ("    vx: ship.vx + c * BULLET_SPEED,\n    vy: ship.vy + s * BULLET_SPEED,",
         "    vx: ship.vx + s * BULLET_SPEED,\n    vy: ship.vy + c * BULLET_SPEED,"),
        # The ship's own velocity is dropped.
        ("    vx: ship.vx + c * BULLET_SPEED,\n    vy: ship.vy + s * BULLET_SPEED,",
         "    vx: c * BULLET_SPEED,\n    vy: s * BULLET_SPEED,"),
        # Born in the corner, not at the nose.
        ("    x: ship.x + c * ship.r,\n    y: ship.y + s * ship.r,", "    x: 0,\n    y: 0,"),
        # Bullets leave the screen for good.
        ("    wrap(b);\n", ""),
        # Moved by a fixed step per frame.
        ("    b.x += b.vx * dt;", "    b.x += b.vx / 60;"),
        # Never drawn.
        ("    ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);\n", ""),
    ],
    "ast-06-gun": [
        # Bullets never expire.
        ("  for (let i = bullets.length - 1; i >= 0; i--) {\n"
         "    if (bullets[i].life <= 0) bullets.splice(i, 1);\n  }\n", ""),
        # Life counted in frames.
        ("    b.life -= dt;", "    b.life -= BULLET_LIFE / 60;"),
        # Cooldown counted in frames.
        ("  if (cooldown > 0) cooldown -= dt;", "  if (cooldown > 0) cooldown -= COOLDOWN / 15;"),
        # No cooldown: a bullet every frame.
        ("    cooldown = COOLDOWN;\n", ""),
        # Bullets that die too soon.
        ("const BULLET_LIFE = 1;", "const BULLET_LIFE = 0.3;"),
    ],
    "ast-07-rocks": [
        # Rocks leave and never return.
        ("    wrap(rk);\n", ""),
        # Spin and drift counted per frame.
        ("    rk.angle += rk.spin * dt;", "    rk.angle += rk.spin / 60;"),
        ("    rk.x += rk.vx * dt;", "    rk.x += rk.vx / 60;"),
        # Every rock the same size.
        ("rocks.push(makeRock(x, y, 2 + Math.floor(Math.random() * 2)));",
         "rocks.push(makeRock(x, y, 3));"),
        # Rocks can start on the ship.
        ("    } while (Math.hypot(x - ship.x, y - ship.y) < 120);", "    } while (false);"),
        # Every rock drifts the same way.
        ("  const heading = Math.random() * Math.PI * 2;", "  const heading = 1;"),
        # Drawn without their spin.
        ("    ctx.rotate(rk.angle);\n", ""),
    ],
    "ast-08-shoot": [
        # A square, not a circle.
        (OVERLAP,
         "  return Math.abs(a.x - b.x) < a.r + b.r && Math.abs(a.y - b.y) < a.r + b.r;"),
        # Every rock treated as one big one.
        ("< a.r + b.r;", "< a.r + 40;"),
        # The bullet survives its hit.
        ("        bullets.splice(i, 1);\n", ""),
        # The rock survives its hit.
        ("        rocks.splice(j, 1);\n", ""),
        # The same score whatever the size.
        ("        score += POINTS[rocks[j].size];", "        score += 10;"),
        # One bullet keeps going and breaks several rocks.
        ("        break;\n", ""),
        # The score is never shown.
        ("  ctx.fillText(`Score: ${score}`, 10, 20);\n", ""),
    ],
    "ast-09-split": [
        # The parent stays behind.
        ("  rocks.splice(j, 1);\n  if (rk.size > 1) {", "  if (rk.size > 1) {"),
        # The pieces are as big as the rock.
        ("makeRock(rk.x, rk.y, rk.size - 1)", "makeRock(rk.x, rk.y, rk.size)"),
        # Small rocks split too (into size 0).
        ("  if (rk.size > 1) {", "  if (rk.size > 0) {"),
        # Only one piece.
        (TWO_PIECES, "    rocks.push(makeRock(rk.x, rk.y, rk.size - 1));"),
        # Born in the corner.
        ("makeRock(rk.x, rk.y, rk.size - 1)", "makeRock(0, 0, rk.size - 1)"),
        # The same piece twice: they fly together.
        (TWO_PIECES,
         "    const piece = makeRock(rk.x, rk.y, rk.size - 1);\n    rocks.push(piece, piece);"),
    ],
    "ast-10-lives": [
        # A life lost on every frame of the protection.
        ("  if (ship.invuln <= 0 && rocks.some", "  if (rocks.some"),
        # Protection counted in frames.
        ("  if (ship.invuln > 0) ship.invuln -= dt;", "  if (ship.invuln > 0) ship.invuln -= 1 / 60;"),
        # Square test against the rocks.
        (OVERLAP,
         "  return Math.abs(a.x - b.x) < a.r + b.r && Math.abs(a.y - b.y) < a.r + b.r;"),
        # Never put back in the middle.
        ("  ship.x = canvas.width / 2;\n  ship.y = canvas.height / 2;\n", ""),
        # Comes back still flying.
        ("  ship.vx = 0;\n  ship.vy = 0;\n  ship.angle = -Math.PI / 2;\n  ship.invuln = INVULN;",
         "  ship.angle = -Math.PI / 2;\n  ship.invuln = INVULN;"),
        # No protection.
        ("  ship.invuln = INVULN;\n", ""),
        # Protection that never ends, or ends at once.
        ("const INVULN = 2;", "const INVULN = 20;"),
        ("const INVULN = 2;", "const INVULN = 0.2;"),
        # Protected but not blinking.
        (BLINK, "  drawShip();\n"),
        # Lives not shown.
        ("  ctx.fillText(`Lives: ${lives}`, 10, 40);\n", ""),
    ],
    "ast-11-over": [
        # Enter restarts a game in progress.
        ("if (e.key === 'Enter' && state === 'over') reset();",
         "if (e.key === 'Enter') reset();"),
        # Any key restarts.
        ("if (e.key === 'Enter' && state === 'over') reset();",
         "if (state === 'over') reset();"),
        # A reset that forgets things.
        ("  score = 0;\n  lives = 3;", "  lives = 3;"),
        ("  score = 0;\n  lives = 3;", "  score = 0;"),
        ("  bullets.length = 0;\n", ""),
        ("  rocks.length = 0;\n", ""),
        ("  cooldown = 0;\n", ""),
        ("  ship.vx = 0;\n  ship.vy = 0;\n  ship.angle = -Math.PI / 2;\n  ship.invuln = 0;",
         "  ship.angle = -Math.PI / 2;\n  ship.invuln = 0;"),
        # The game never stops.
        ("  if (state !== 'playing') return;\n", ""),
        ("    state = 'over';\n    return;\n", "    return;\n"),
        # One life too many.
        ("  if (lives <= 0) {", "  if (lives < 0) {"),
        # No message.
        ("    ctx.fillText('Game over', 150, 150);\n", ""),
    ],
}

OTHER_WAYS: dict[str, list[tuple[str, str]]] = {
    # Two ifs instead of the subtraction.
    "ast-01-turn": [
        ("  const turn = (keys.has('ArrowRight') ? 1 : 0) - (keys.has('ArrowLeft') ? 1 : 0);\n"
         "  ship.angle += turn * TURN * dt;\n",
         "  if (keys.has('ArrowRight')) ship.angle += TURN * dt;\n"
         "  if (keys.has('ArrowLeft')) ship.angle -= TURN * dt;\n"),
        ("const TURN = 4;", "const TURN = 3.5;"),
    ],
    "ast-02-thrust": [
        (THRUST_LINES,
         "    const push = THRUST * dt;\n"
         "    ship.vx += push * Math.cos(ship.angle);\n"
         "    ship.vy += push * Math.sin(ship.angle);"),
    ],
    # Continuous decay, written a different way; and a linear approximation.
    "ast-03-friction": [
        ("  const damp = Math.pow(DRAG, dt);", "  const damp = Math.exp(-0.7 * dt);"),
        ("  const damp = Math.pow(DRAG, dt);", "  const damp = 1 - 0.7 * dt;"),
    ],
    # The modulo way.
    "ast-04-wrap": [
        (WRAP_BODY,
         "  o.x = ((o.x % canvas.width) + canvas.width) % canvas.width;\n"
         "  o.y = ((o.y % canvas.height) + canvas.height) % canvas.height;\n"),
    ],
    "ast-05-bullets": [
        ("if (e.key === ' ') fire();", "if (e.code === 'Space') fire();"),
    ],
    "ast-06-gun": [
        ("const COOLDOWN = 0.25;", "const COOLDOWN = 0.3;"),
        ("const BULLET_LIFE = 1;", "const BULLET_LIFE = 1.2;"),
        ("  if (cooldown > 0) cooldown -= dt;", "  cooldown = Math.max(0, cooldown - dt);"),
    ],
    # The distance by hand.
    "ast-07-rocks": [
        ("Math.hypot(x - ship.x, y - ship.y) < 120",
         "Math.sqrt((x - ship.x) ** 2 + (y - ship.y) ** 2) < 120"),
    ],
    # Squared distances, no square root.
    "ast-08-shoot": [
        (OVERLAP,
         "  const dx = a.x - b.x;\n  const dy = a.y - b.y;\n  const reach = a.r + b.r;\n"
         "  return dx * dx + dy * dy < reach * reach;"),
    ],
    "ast-09-split": [
        (TWO_PIECES,
         "    for (let n = 0; n < 2; n++) rocks.push(makeRock(rk.x, rk.y, rk.size - 1));"),
    ],
    "ast-10-lives": [
        ("rocks.some((rk) => overlap(ship, rk))", "rocks.find((rk) => overlap(ship, rk))"),
    ],
    "ast-11-over": [
        ("if (e.key === 'Enter' && state === 'over') reset();",
         "if (state === 'over' && e.code === 'Enter') reset();"),
    ],
}


class ShapeTests(unittest.TestCase):
    def test_ids_are_unique_and_named_for_the_track(self) -> None:
        ids = [s.id for s in ASTEROIDS_STEPS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(ASTEROIDS_STEPS), 12)
        for n, s in enumerate(ASTEROIDS_STEPS, 1):
            with self.subTest(step=s.id):
                self.assertTrue(s.id.startswith(f"ast-{n:02d}-"))
                self.assertEqual(s.track, "Asteroids")
                self.assertGreater(len(s.teaches), 120)
                self.assertTrue(s.goal.endswith("."))
                self.assertTrue(s.hint or not s.check)

    def test_each_step_starts_where_the_last_one_finished(self) -> None:
        for before, after in zip(ASTEROIDS_STEPS, ASTEROIDS_STEPS[1:]):
            with self.subTest(step=after.id):
                self.assertEqual(after.starter, before.solution)

    def test_only_the_last_step_is_open(self) -> None:
        self.assertEqual(
            [s.id for s in ASTEROIDS_STEPS if not s.check], [ASTEROIDS_STEPS[-1].id]
        )

    def test_every_mistake_names_a_real_step(self) -> None:
        ids = {s.id for s in ASTEROIDS_STEPS}
        self.assertLessEqual(set(MISTAKES) | set(OTHER_WAYS), ids)

    def test_every_checked_step_has_a_mistake(self) -> None:
        for s in ASTEROIDS_STEPS:
            if s.check:
                with self.subTest(step=s.id):
                    self.assertTrue(MISTAKES.get(s.id))


@unittest.skipUnless(HAS_NODE, "needs node")
class CheckTests(unittest.TestCase):
    def test_every_solution_passes_and_every_starter_fails(self) -> None:
        for s in ASTEROIDS_STEPS:
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
