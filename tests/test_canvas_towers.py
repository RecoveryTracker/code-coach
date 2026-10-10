"""Canvas: the Tower defense track.

Held to the same three things as the other tracks: each solution passes its
check, each starter fails it, and the mistakes people really make at that
step fail it too - here: a road of tile corners instead of centres, moving
per frame instead of per second, overshooting (or never turning at) a
waypoint, a health bar that never shrinks, a click that ignores the canvas
scaling or rounds instead of flooring, building on the road, a waypoint-only
road test, range as a square (or squared), the nearest or the last target
instead of the first, a reload counted in frames, a shot that keeps flying
after its target dies, a reward paid twice (or for an escape), a wave that
ends too soon, a countdown counted in frames, lives lost every frame a creep
sits at the end, and a restart that leaves something behind.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.canvas import run_check
from code_coach.canvas.content_towers import TOWER_STEPS

HAS_NODE = shutil.which("node") is not None


def _step(step_id: str):
    return next(s for s in TOWER_STEPS if s.id == step_id)


def _swap(code: str, change: tuple) -> str:
    """Apply one change: (old, new), or a tuple of such pairs applied in turn."""
    pairs = (change,) if isinstance(change[0], str) else change
    for old, new in pairs:
        assert code.count(old) >= 1, old
        code = code.replace(old, new)
    return code


def _label(change: tuple) -> str:
    pair = change if isinstance(change[0], str) else change[0]
    return (pair[1] or pair[0])[:40]


_ON_PATH_LOOP = (
    "  for (let i = 0; i < path.length - 1; i++) {\n"
    "    const a = path[i];\n"
    "    const b = path[i + 1];\n"
    "    if (x >= Math.min(a.x, b.x) && x <= Math.max(a.x, b.x) && y >= Math.min(a.y, b.y) && y <= Math.max(a.y, b.y)) return true;\n"
    "  }\n"
    "  return false;\n"
)
_SPAWN_BLOCK = (
    "  spawnTimer += dt;\n"
    "  if (spawnTimer >= SPAWN_EVERY) {\n"
    "    spawnTimer -= SPAWN_EVERY;\n"
    "    spawnCreep();\n"
    "  }\n"
)
_TARGET_PICK = "    if (!best || c.dist > best.dist) best = c;\n"
_RANGE_TEST = "    if (Math.hypot(c.x - t.x, c.y - t.y) > t.range) continue;\n"
_SHOT_FILTER = "!s.done && creeps.includes(s.target)"
_CLICK_GUARD_9 = "  if (onPath(col, row) || towerAt(col, row) || money < TOWER_COST) return;\n"
_WAVE_END = "    if (toSpawn === 0 && creeps.length === 0) {\n"
_PAY_LOOP = (
    "    if (c.hp <= 0) money += c.reward;\n"
    "    else if (c.next < path.length) alive.push(c);\n"
    "    else lives = Math.max(0, lives - 1);\n"
)

MISTAKES: dict[str, list[tuple]] = {
    "td-01-path": [
        # Tile corners, not tile centres.
        ("{ x: 20, y: 60 },", "{ x: 0, y: 40 },"),
        # The last piece of road is left out.
        ("for (const p of path.slice(1)) ctx.lineTo(p.x, p.y);", "for (const p of path.slice(1, -1)) ctx.lineTo(p.x, p.y);"),
        # A hairline, not a road.
        ("ctx.lineWidth = TILE;", "ctx.lineWidth = 2;"),
        # Never stroked.
        ("  ctx.stroke();\n", ""),
        ("const TILE = 40;", "const TILE = 20;"),
    ],
    "td-02-walk": [
        # A step per frame: right at 60 a second, wrong at 30.
        ("let left = c.speed * dt;", "let left = c.speed / 60;"),
        # Stops at the first waypoint and never turns.
        ("      c.next++;\n      c.dist += d;\n      left -= d;\n", "      c.dist += d;\n      left = 0;\n"),
        # Overshoots the waypoint instead of snapping onto it.
        ("if (d <= left) {", "if (d < 0.5) {"),
        # dist is never added up.
        ("      c.dist += left;\n", ""),
        # Walks off the end and stays in the game.
        ("  creeps = creeps.filter((c) => c.next < path.length);\n", ""),
    ],
    "td-03-health": [
        # The bar never shrinks.
        ("(BAR_W * Math.max(0, c.hp)) / c.maxHp", "BAR_W"),
        # Pixels of bar = hp, not a fraction of the bar.
        ("(BAR_W * Math.max(0, c.hp)) / c.maxHp", "c.hp"),
        # A creep on exactly 0 hp lives on.
        ("c.hp > 0 && c.next < path.length", "c.hp >= 0 && c.next < path.length"),
        ("c.hp > 0 && c.next < path.length", "c.next < path.length"),
        # The bar stays where the creep was born.
        ("const x = c.x - BAR_W / 2;", "const x = path[0].x - BAR_W / 2;"),
    ],
    "td-04-spawn": [
        # One creep every frame.
        (_SPAWN_BLOCK, "  spawnCreep();\n"),
        # A creep every 90 frames: right at 60 a second, wrong at 30.
        (_SPAWN_BLOCK, "  update.n = (update.n || 0) + 1;\n  if (update.n % 90 === 0) spawnCreep();\n"),
        # The timer is never taken down.
        ("    spawnTimer -= SPAWN_EVERY;\n", ""),
        # The same creep pushed again and again.
        ("creeps.push(makeCreep());", "creeps.push(creeps[0] || makeCreep());"),
        # Born in the middle of the screen.
        ("creeps.push(makeCreep());", "creeps.push({ ...makeCreep(), x: 240, y: 160 });"),
    ],
    "td-05-build": [
        # Page pixels used as canvas pixels (the canvas is drawn at twice its size here).
        ("(e.clientX - box.left) * (canvas.width / box.width)", "e.offsetX"),
        ("(e.clientY - box.top) * (canvas.height / box.height)", "e.offsetY"),
        # Nearest tile boundary, not the tile the point is in.
        ("col: Math.floor(x / TILE), row: Math.floor(y / TILE)", "col: Math.round(x / TILE), row: Math.round(y / TILE)"),
        # Builds on the road.
        ("  if (onPath(col, row) || towerAt(col, row)) return;\n", "  if (towerAt(col, row)) return;\n"),
        # Builds twice on one tile.
        ("  if (onPath(col, row) || towerAt(col, row)) return;\n", "  if (onPath(col, row)) return;\n"),
        # Only the waypoint tiles count as road.
        (_ON_PATH_LOOP, "  return path.some((p) => p.x === x && p.y === y);\n"),
    ],
    "td-06-target": [
        # The nearest to the tower, not the furthest along.
        (_TARGET_PICK, "    if (!best || Math.hypot(c.x - t.x, c.y - t.y) < Math.hypot(best.x - t.x, best.y - t.y)) best = c;\n"),
        # The last one in the array.
        (_TARGET_PICK, "    best = c;\n"),
        # The first one in the array.
        (_TARGET_PICK, "    if (!best) best = c;\n"),
        # The one that has walked least.
        (_TARGET_PICK, "    if (!best || c.dist < best.dist) best = c;\n"),
        # Range as a square.
        (_RANGE_TEST, "    if (Math.abs(c.x - t.x) > t.range || Math.abs(c.y - t.y) > t.range) continue;\n"),
        # Squared distance against an unsquared range.
        (_RANGE_TEST, "    if ((c.x - t.x) ** 2 + (c.y - t.y) ** 2 > t.range) continue;\n"),
        # An unsquared distance against a squared range.
        (_RANGE_TEST, "    if (Math.hypot(c.x - t.x, c.y - t.y) > t.range * t.range) continue;\n"),
        # No line drawn.
        ("    ctx.lineTo(target.x, target.y);\n", ""),
    ],
    "td-07-cooldown": [
        # Reload counted in frames: right at 60 a second, wrong at 30.
        ("  t.reload = Math.max(0, t.reload - dt);\n", "  t.reload = Math.max(0, t.reload - 1 / 60);\n"),
        # No reload at all.
        ("  t.reload = t.rate;\n", ""),
        # The reload never counts down.
        ("  t.reload = Math.max(0, t.reload - dt);\n", ""),
        # Hits everything in range, not just the target.
        ("  target.hp -= t.damage;\n", "  for (const c of creeps) if (Math.hypot(c.x - t.x, c.y - t.y) <= t.range) c.hp -= t.damage;\n"),
    ],
    "td-08-shots": [
        # Still an instant hit.
        ("  shots.push({ x: t.x, y: t.y, target, speed: 300, damage: t.damage });\n", "  target.hp -= t.damage;\n"),
        # Aimed once, when it is fired.
        (
            "  const dx = s.target.x - s.x;\n  const dy = s.target.y - s.y;\n",
            "  s.tx = s.tx ?? s.target.x;\n  s.ty = s.ty ?? s.target.y;\n  const dx = s.tx - s.x;\n  const dy = s.ty - s.y;\n",
        ),
        # A step per frame.
        ("const step = s.speed * dt;", "const step = s.speed / 60;"),
        # Never removed after it lands: it hits again every frame.
        (_SHOT_FILTER, "creeps.includes(s.target)"),
        # Keeps flying after its target has gone.
        (_SHOT_FILTER, "!s.done"),
    ],
    "td-09-money": [
        # A tower is free.
        ("  money -= TOWER_COST;\n", ""),
        # Builds with no money.
        (_CLICK_GUARD_9, "  if (onPath(col, row) || towerAt(col, row)) return;\n"),
        # Takes the money before looking at the tile.
        (
            _CLICK_GUARD_9 + "  money -= TOWER_COST;\n",
            "  money -= TOWER_COST;\n  if (onPath(col, row) || towerAt(col, row) || money < 0) return;\n",
        ),
        # The reward is a number in the code, not the creep's own.
        ("if (c.hp <= 0) money += c.reward;", "if (c.hp <= 0) money += 5;"),
        # An escape pays too.
        (
            "    else if (c.next < path.length) alive.push(c);\n",
            "    else if (c.next < path.length) alive.push(c);\n    else money += c.reward;\n",
        ),
        # Paid when each shot lands: two shots on one creep pay twice.
        (
            (
                ("    s.target.hp -= s.damage;\n    s.done = true;\n", "    s.target.hp -= s.damage;\n    if (s.target.hp <= 0) money += s.target.reward;\n    s.done = true;\n"),
                ("money += c.reward;", "money += 0;"),
            )
        ),
        # Never shown.
        ("  ctx.fillText(`$${money}`, 10, 20);\n", ""),
    ],
    "td-10-waves": [
        # The wave ends when its last creep is spawned, not when it is gone.
        (_WAVE_END, "    if (toSpawn === 0) {\n"),
        # The whole wave at once.
        ("if (toSpawn > 0 && spawnTimer >= SPAWN_EVERY) {", "while (toSpawn > 0) {"),
        # Every wave as tough as the first.
        ("spawnCreep(waves[wave - 1].hp);", "spawnCreep(10);"),
        # A countdown counted in frames.
        ("countdown -= dt;", "countdown -= 1 / 60;"),
        # The countdown is not set again between waves.
        ("        countdown = GAP;\n", ""),
        # One creep too many.
        ("toSpawn = waves[wave - 1].count;", "toSpawn = waves[wave - 1].count + 1;"),
        # Nothing ever says the game is won: a wave that does not exist is started.
        (
            "      if (wave === waves.length) {\n        state = 'won';\n      } else {\n        state = 'countdown';\n        countdown = GAP;\n      }\n",
            "      state = 'countdown';\n      countdown = GAP;\n",
        ),
        ("    ctx.fillText('You win!', 170, 170);\n", ""),
        ("  ctx.fillText(`Wave ${wave}/${waves.length}`, 90, 20);\n", ""),
    ],
    "td-11-lives": [
        # The creep stays at the end, so a life goes every frame.
        (
            "    else lives = Math.max(0, lives - 1);\n",
            "    else {\n      lives = Math.max(0, lives - 1);\n      alive.push(c);\n    }\n",
        ),
        # The game runs on after game over.
        ("  if (state === 'over') return;\n", ""),
        # The game is never over.
        ("  if (lives <= 0) state = 'over';\n", ""),
        # A creep killed at the last step still costs a life.
        (
            _PAY_LOOP,
            "    if (c.next >= path.length) lives = Math.max(0, lives - 1);\n"
            "    else if (c.hp <= 0) money += c.reward;\n"
            "    else alive.push(c);\n",
        ),
        # Enter restarts a game that is not over; so does any key.
        ("if (e.key === 'Enter' && state === 'over') reset();", "if (e.key === 'Enter') reset();"),
        ("if (e.key === 'Enter' && state === 'over') reset();", "if (state === 'over') reset();"),
        # A restart that leaves something behind.
        ("  creeps = [];\n  towers = [];\n", "  towers = [];\n"),
        ("  towers = [];\n  shots = [];\n", "  shots = [];\n"),
        ("  shots = [];\n  money = 100;\n", "  money = 100;\n"),
        ("  money = 100;\n  lives = 10;\n", "  lives = 10;\n"),
        ("  lives = 10;\n  wave = 0;\n", "  wave = 0;\n"),
        ("  wave = 0;\n  state = 'countdown';\n", "  state = 'countdown';\n"),
        ("  countdown = 3;\n  toSpawn = 0;\n", "  toSpawn = 0;\n"),
        ("  toSpawn = 0;\n  spawnTimer = 0;\n", "  spawnTimer = 0;\n"),
        ("  toSpawn = 0;\n  spawnTimer = 0;\n", "  toSpawn = 0;\n"),
        # Lives never shown.
        ("  ctx.fillText(`Lives: ${lives}`, 220, 20);\n", ""),
    ],
}

OTHER_WAYS: dict[str, list[tuple]] = {
    # Snap onto the waypoint and lose what is left of the step.
    "td-02-walk": [
        ("      c.dist += d;\n      left -= d;\n", "      c.dist += d;\n      left = 0;\n"),
    ],
    # A timer instead of an accumulator.
    "td-04-spawn": [
        (_SPAWN_BLOCK, "  if (!update.started) {\n    update.started = true;\n    setInterval(spawnCreep, SPAWN_EVERY * 1000);\n  }\n"),
    ],
    # Tiles worked out from the waypoints' tiles.
    "td-05-build": [
        (
            _ON_PATH_LOOP,
            "  for (let i = 0; i < path.length - 1; i++) {\n"
            "    const a = tileAt(path[i].x, path[i].y);\n"
            "    const b = tileAt(path[i + 1].x, path[i + 1].y);\n"
            "    if (col >= Math.min(a.col, b.col) && col <= Math.max(a.col, b.col) && row >= Math.min(a.row, b.row) && row <= Math.max(a.row, b.row)) return true;\n"
            "  }\n"
            "  return false;\n",
        ),
    ],
    # Filter and sort instead of a loop.
    "td-06-target": [
        (
            "  let best = null;\n  for (const c of creeps) {\n" + _RANGE_TEST + _TARGET_PICK + "  }\n  return best;\n",
            "  const inRange = creeps.filter((c) => Math.hypot(c.x - t.x, c.y - t.y) <= t.range);\n"
            "  inRange.sort((a, b) => b.dist - a.dist);\n"
            "  return inRange[0] || null;\n",
        ),
    ],
    # The reload is allowed to go below zero.
    "td-07-cooldown": [
        ("  t.reload = Math.max(0, t.reload - dt);\n", "  t.reload -= dt;\n"),
    ],
    # A hit when it is close enough, not when it is exactly there.
    "td-08-shots": [
        ("if (d <= step) {", "if (d < 6) {"),
    ],
    "td-10-waves": [
        ("if (toSpawn > 0 && spawnTimer >= SPAWN_EVERY) {", "while (toSpawn > 0 && spawnTimer >= SPAWN_EVERY) {"),
    ],
}


class ShapeTests(unittest.TestCase):
    def test_ids_are_unique_and_named_for_the_track(self) -> None:
        ids = [s.id for s in TOWER_STEPS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(TOWER_STEPS), 12)
        for i, s in enumerate(TOWER_STEPS, start=1):
            with self.subTest(step=s.id):
                self.assertTrue(s.id.startswith(f"td-{i:02d}-"))
                self.assertEqual(s.track, "Tower defense")
                self.assertGreater(len(s.teaches), 120)
                self.assertTrue(s.goal.endswith("."))
                if s.check:
                    self.assertTrue(s.hint)

    def test_each_step_starts_where_the_last_one_finished(self) -> None:
        for before, after in zip(TOWER_STEPS, TOWER_STEPS[1:]):
            with self.subTest(step=after.id):
                self.assertEqual(after.starter, before.solution)

    def test_only_the_last_step_is_open(self) -> None:
        self.assertEqual([s.id for s in TOWER_STEPS if not s.check], [TOWER_STEPS[-1].id])

    def test_every_mistake_names_a_real_step(self) -> None:
        ids = {s.id for s in TOWER_STEPS}
        self.assertLessEqual(set(MISTAKES) | set(OTHER_WAYS), ids)

    def test_every_checked_step_has_a_mistake(self) -> None:
        checked = {s.id for s in TOWER_STEPS if s.check}
        self.assertEqual(checked - set(MISTAKES), set())


@unittest.skipUnless(HAS_NODE, "needs node")
class CheckTests(unittest.TestCase):
    def test_every_solution_passes_and_every_starter_fails(self) -> None:
        for s in TOWER_STEPS:
            if not s.check:
                continue
            with self.subTest(step=s.id):
                good = run_check(s.solution, s.check)
                self.assertTrue(good.passed, good.message)
                bad = run_check(s.starter, s.check)
                self.assertFalse(bad.passed)
                self.assertTrue(bad.message)

    def test_real_mistakes_fail(self) -> None:
        for step_id, changes in MISTAKES.items():
            s = _step(step_id)
            for change in changes:
                with self.subTest(step=step_id, change=_label(change)):
                    got = run_check(_swap(s.solution, change), s.check)
                    self.assertFalse(got.passed, "the check let this mistake through")

    def test_other_right_answers_pass(self) -> None:
        for step_id, changes in OTHER_WAYS.items():
            s = _step(step_id)
            for change in changes:
                with self.subTest(step=step_id, change=_label(change)):
                    got = run_check(_swap(s.solution, change), s.check)
                    self.assertTrue(got.passed, got.message)


if __name__ == "__main__":
    unittest.main()
