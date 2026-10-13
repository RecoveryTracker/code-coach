"""Canvas: the Dungeon track.

Held to the same three things as the other tracks: each solution passes its
check, each starter fails it, and the mistakes people really make at that
step fail it too - here: indexing the map as map[x][y], a missing or
off-by-one wall test at the edge, moving on every frame a key is down (or on
auto-repeat) instead of once per press, a camera that is not clamped or not
subtracted when drawing, rooms that overlap or run into the border, rooms
that are not all joined, stairs that share the player's room or do not
regenerate the level, enemies that act before the player, on a bumped wall or
on a timer, enemies that walk through walls or onto the player, an attack
that leaves a dead enemy on the map, fog that shows everything (or ignores
walls, or is not remembered), healing past max hp, and a game over that is
not final or a restart that leaves something behind.

The generator's checks are about properties, never layouts, so OTHER_WAYS
holds different but correct generators too.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.canvas import run_check
from code_coach.canvas.content_dungeon import DUNGEON_STEPS

HAS_NODE = shutil.which("node") is not None


def _step(step_id: str):
    return next(s for s in DUNGEON_STEPS if s.id == step_id)


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


_KEYDOWN_2 = (
    "addEventListener('keydown', (e) => {\n"
    "  if (e.repeat) return;\n"
    "  const d = KEYS[e.key];\n"
    "  if (d) {\n"
    "    player.x += d.x;\n"
    "    player.y += d.y;\n"
    "  }\n"
    "});\n"
)
# The keys held down in a set and the player moved on every frame they are down.
_HELD = (
    "const held = new Set();\n"
    "addEventListener('keydown', (e) => held.add(e.key));\n"
    "addEventListener('keyup', (e) => held.delete(e.key));\n"
    "(function tick() {\n"
    "  for (const k of held) if (KEYS[k]) { player.x += KEYS[k].x; player.y += KEYS[k].y; }\n"
    "  requestAnimationFrame(tick);\n"
    "})();\n"
)
_CAM_X = "  camX = clamp(player.x - Math.floor(VIEW_W / 2), 0, map[0].length - VIEW_W);\n"
_CAM_Y = "  camY = clamp(player.y - Math.floor(VIEW_H / 2), 0, map.length - VIEW_H);\n"
_ROOM_CHECK = "    if (rooms.some((r) => intersects(room, r))) continue;\n"
_TUNNEL_LOOP = (
    "  for (let i = 1; i < rooms.length; i++) {\n"
    "    tunnel(grid, center(rooms[i - 1]), center(rooms[i]));\n"
    "  }\n"
)
_VERTICAL = "  for (let y = Math.min(a.y, b.y); y <= Math.max(a.y, b.y); y++) grid[y][b.x] = '.';\n"
_MOVE_STEP_8 = "  player.x = x;\n  player.y = y;\n"
_STAIRS_BLOCK = "    depth += 1;\n    generate();\n"
_ENEMY_GUARD = "(sx === 0 && sy === 0) || isWall(x, y) || (x === player.x && y === player.y)"
_ATTACK = (
    "    if (Math.abs(dx) + Math.abs(dy) === 1) {\n"
    "      player.hp -= ENEMY_DAMAGE;\n"
    "      continue;\n"
    "    }\n"
)
_BUMP_TURN = "    endTurn();\n    return;\n  }\n  player.x = x;"
_DIM_ROW = "      else if (seen.has(x + ',' + y)) drawTile(x, y, map[y][x] === '#' ? '#262c37' : '#1c2230');\n"
_OVER_GUARD = (
    "  if (state === 'over') {\n"
    "    if (e.key === 'Enter') restart();\n"
    "    return;\n"
    "  }\n"
)

MISTAKES: dict[str, list[tuple]] = {
    "dg-01-map": [
        # Row and column swapped when reading the map.
        ("map[y][x] === '#' ? '#4a5568'", "map[x][y] === '#' ? '#4a5568'"),
        # Off by one: the last row, or the last column, is never drawn.
        ("y < map.length; y++", "y < map.length - 1; y++"),
        ("x < map[y].length; x++", "x < map[y].length - 1; x++"),
        # Pixels swapped.
        ("ctx.fillRect(x * TILE, y * TILE, TILE, TILE);", "ctx.fillRect(y * TILE, x * TILE, TILE, TILE);"),
        # Walls and floor the same colour.
        ("'#4a5568' : '#2d3748'", "'#4a5568' : '#4a5568'"),
        # A map whose rows are one character short.
        ("'#............#...............#',", "'#............#..............#',"),
    ],
    "dg-02-turns": [
        # Auto-repeat moves the player again.
        ("  if (e.repeat) return;\n", ""),
        # Moves on every frame the key is down.
        (_KEYDOWN_2, _HELD),
        # Pixels, not tiles.
        ("    player.x += d.x;\n", "    player.x += d.x * TILE;\n"),
        # Up is down.
        ("ArrowUp: { x: 0, y: -1 }", "ArrowUp: { x: 0, y: 1 }"),
        # x and y swapped.
        ("    player.x += d.x;\n    player.y += d.y;\n", "    player.x += d.y;\n    player.y += d.x;\n"),
        # The player is never drawn.
        ("  drawTile(player.x, player.y, '#4fd1c5');\n", ""),
    ],
    "dg-03-walls": [
        # Walls do not stop anyone.
        ("  if (isWall(x, y)) return;\n", ""),
        # Walls do, the edge of the map does not.
        ("  return !inMap(x, y) || map[y][x] === '#';",
         "  return map[y] !== undefined && map[y][x] === '#';"),
        # map[x][y]
        ("|| map[y][x] === '#';", "|| map[x][y] === '#';"),
        # Off by one at the right edge.
        ("x < map[y].length;", "x <= map[y].length;"),
        # Off by one at the bottom edge.
        ("y < map.length &&", "y <= map.length &&"),
        # Only the walls to the right count.
        ("  return !inMap(x, y) || map[y][x] === '#';",
         "  return !inMap(x, y) || (map[y][x] === '#' && x >= player.x);"),
    ],
    "dg-04-camera": [
        # Not clamped.
        (_CAM_X, "  camX = player.x - Math.floor(VIEW_W / 2);\n"),
        (_CAM_Y, "  camY = player.y - Math.floor(VIEW_H / 2);\n"),
        # Clamped to the wrong end.
        ("0, map[0].length - VIEW_W);", "0, map[0].length);"),
        # Never follows.
        (_CAM_X, "  camX = 0;\n"),
        # Follows the wrong coordinate.
        (_CAM_X, "  camX = clamp(player.y - Math.floor(VIEW_W / 2), 0, map[0].length - VIEW_W);\n"),
        # Drawn without the camera subtracted.
        ("ctx.fillRect((x - camX) * TILE, (y - camY) * TILE, TILE, TILE);",
         "ctx.fillRect(x * TILE, y * TILE, TILE, TILE);"),
        # Camera subtracted from the map but not the player.
        ("  drawTile(player.x, player.y, '#4fd1c5');\n",
         "  ctx.fillStyle = '#4fd1c5';\n  ctx.fillRect(player.x * TILE, player.y * TILE, TILE, TILE);\n"),
    ],
    "dg-05-rooms": [
        # Rooms are never thrown away.
        (_ROOM_CHECK, ""),
        # Rooms run into the border, to the right and at the bottom.
        ("(MAP_W - w - 1)", "(MAP_W - w)"),
        ("(MAP_H - h - 1)", "(MAP_H - h)"),
        # The list of rooms is not emptied for the next level.
        ("  rooms = [];\n  for", "  for"),
        # Row and column swapped when carving.
        ("grid[y][x] = '.';", "grid[x][y] = '.';"),
        # The player is not put in a room.
        ("  player.x = start.x;\n  player.y = start.y;\n", ""),
        # Gives up with two rooms.
        ("rooms.length < 8;", "rooms.length < 2;"),
    ],
    "dg-06-corridors": [
        # The last room is never joined.
        ("for (let i = 1; i < rooms.length; i++) {\n    tunnel", "for (let i = 1; i < rooms.length - 1; i++) {\n    tunnel"),
        # Every other room is skipped.
        ("for (let i = 1; i < rooms.length; i++) {\n    tunnel", "for (let i = 1; i < rooms.length; i += 2) {\n    tunnel"),
        # No vertical stretch.
        (_VERTICAL, ""),
        # The vertical stretch is in the wrong column.
        ("grid[y][b.x] = '.';", "grid[y][a.x] = '.';"),
        # No corridors at all.
        (_TUNNEL_LOOP, ""),
    ],
    "dg-07-stairs": [
        # The stairs are in the player's room, under the player.
        ("  const end = center(rooms[rooms.length - 1]);\n", "  const end = center(rooms[0]);\n"),
        # In any room, the first included.
        ("  const end = center(rooms[rooms.length - 1]);\n",
         "  const end = center(rooms[Math.floor(Math.random() * rooms.length)]);\n"),
        # x and y swapped.
        ("stairs = { x: end.x, y: end.y };", "stairs = { x: end.y, y: end.x };"),
        # Deeper, but the same level.
        (_STAIRS_BLOCK, "    depth += 1;\n"),
        # A new level at the same depth.
        (_STAIRS_BLOCK, "    generate();\n"),
        # The depth is not shown.
        ("  ctx.fillText(`Depth: ${depth}`, 8, 20);\n", ""),
        # The stairs are not drawn.
        ("  drawTile(stairs.x, stairs.y, '#b794f4');\n", ""),
    ],
    "dg-08-enemies": [
        # The enemies move before the player does.
        ((_MOVE_STEP_8, "  endTurn();\n" + _MOVE_STEP_8),
         ("    return;\n  }\n  endTurn();\n}", "    return;\n  }\n}")),
        # A step into a wall is a turn.
        ("  if (isWall(x, y)) return;\n", "  if (isWall(x, y)) {\n    endTurn();\n    return;\n  }\n"),
        # They move on the clock, not on the player's turn.
        ("function loop() {\n  draw();", "function loop() {\n  enemiesAct();\n  draw();"),
        # They walk through walls.
        (_ENEMY_GUARD, "(sx === 0 && sy === 0) || (x === player.x && y === player.y)"),
        # They walk onto the player.
        (_ENEMY_GUARD, "(sx === 0 && sy === 0) || isWall(x, y)"),
        # They run away.
        ("const stepX = Math.sign(dx);", "const stepX = -Math.sign(dx);"),
        # They start in the player's room.
        ("  for (const room of rooms.slice(1)) {\n    const spot", "  for (const room of rooms) {\n    const spot"),
        # They are not drawn.
        ("  for (const e of enemies) drawTile(e.x, e.y, '#f56565');\n", ""),
    ],
    "dg-09-bump": [
        # A dead enemy stays in the list.
        ("    if (target.hp <= 0) enemies = enemies.filter((e) => e !== target);\n", ""),
        # Dead only below zero.
        ("target.hp <= 0", "target.hp < 0"),
        # The player hits and then walks onto the tile.
        (_BUMP_TURN, "  }\n  player.x = x;"),
        # Hitting is not a turn.
        (_BUMP_TURN, "    return;\n  }\n  player.x = x;"),
        # The enemy beside the player never hits.
        (_ATTACK, ""),
        # Enemies hit from three tiles away.
        ("Math.abs(dx) + Math.abs(dy) === 1", "Math.abs(dx) + Math.abs(dy) <= 3"),
        # A dead enemy gets its turn.
        ("    target.hp -= PLAYER_DAMAGE;\n    if (target.hp <= 0) enemies = enemies.filter((e) => e !== target);\n    endTurn();\n",
         "    target.hp -= PLAYER_DAMAGE;\n    endTurn();\n    if (target.hp <= 0) enemies = enemies.filter((e) => e !== target);\n"),
        # No hp for enemies.
        ("enemies.push({ x: spot.x, y: spot.y, hp: 4 });", "enemies.push({ x: spot.x, y: spot.y });"),
        # The health is not shown.
        ("  ctx.fillText(`HP: ${player.hp}/${player.maxHp}`, 8, 40);\n", ""),
    ],
    "dg-10-fog": [
        # Everything is visible.
        ("function visible(x, y) {\n", "function visible(x, y) {\n  return true;\n"),
        # Walls do not block sight.
        ("    if (isWall(cx, cy)) return false;\n", "    if (cx < 0) return false;\n"),
        # The radius is not squared.
        ("dx * dx + dy * dy > RADIUS * RADIUS", "dx * dx + dy * dy > RADIUS"),
        # The fog is not updated as the player moves.
        ("  enemiesAct();\n  updateFog();\n", "  enemiesAct();\n"),
        # The fog survives into the next level.
        ("  seen = new Set();\n  updateFog();\n}", "  updateFog();\n}"),
        # Seen tiles are not drawn.
        (_DIM_ROW, ""),
        # Remembered tiles look like visible ones.
        ("'#262c37' : '#1c2230'", "'#4a5568' : '#2d3748'"),
        # Unseen tiles are drawn too.
        ("      if (visible(x, y)) drawTile(x, y,", "      if (true) drawTile(x, y,"),
    ],
    "dg-11-potions": [
        # Healing past the maximum.
        ("Math.min(player.maxHp, player.hp + 5)", "player.hp + 5"),
        # Heals the wrong amount.
        ("Math.min(player.maxHp, player.hp + 5)", "Math.min(player.maxHp, player.hp + 3)"),
        # Drinking with none left.
        ("  if (potions === 0) return;\n", ""),
        # Drinking is free.
        ("  player.hp = Math.min(player.maxHp, player.hp + 5);\n  endTurn();\n",
         "  player.hp = Math.min(player.maxHp, player.hp + 5);\n"),
        # A potion that stays where it was.
        ("  items = items.filter((i) => i !== found);\n", ""),
        # Picked up but not counted.
        ("  potions += 1;\n", ""),
        # The count is not shown.
        ("  ctx.fillText(`Potions: ${potions}`, 8, 60);\n", ""),
    ],
    "dg-12-gameover": [
        # Never ends.
        ("  if (player.hp <= 0) state = 'over';\n", ""),
        # Keys still work after the end.
        (_OVER_GUARD, "  if (e.key === 'Enter' && state === 'over') restart();\n"),
        # Enter restarts in the middle of a game.
        (_OVER_GUARD, "  if (e.key === 'Enter') restart();\n  if (state === 'over') return;\n"),
        # Restart leaves the health, the depth, the potions, the level behind.
        ("  player.hp = player.maxHp;\n", ""),
        ("  depth = 1;\n  player.hp", "  player.hp"),
        ("  potions = 0;\n  state = 'playing';", "  state = 'playing';"),
        ("  state = 'playing';\n  generate();\n}", "  state = 'playing';\n}"),
        ("  state = 'playing';\n  generate();\n}", "  generate();\n}"),
        # Says nothing.
        ("    ctx.fillText('Game over', 150, 160);\n", ""),
    ],
}

OTHER_WAYS: dict[str, list[tuple]] = {
    "dg-02-turns": [
        ("    player.x += d.x;\n    player.y += d.y;\n",
         "    Object.assign(player, { x: player.x + d.x, y: player.y + d.y });\n"),
    ],
    "dg-03-walls": [
        ("  return !inMap(x, y) || map[y][x] === '#';", "  return !inMap(x, y) || map[y].charAt(x) === '#';"),
        ("  return y >= 0 && y < map.length && x >= 0 && x < map[y].length;",
         "  return map[y] !== undefined && map[y][x] !== undefined;"),
    ],
    "dg-04-camera": [
        ("  return Math.max(lo, Math.min(hi, v));", "  return v < lo ? lo : v > hi ? hi : v;"),
        ("Math.floor(VIEW_W / 2)", "Math.ceil(VIEW_W / 2)"),
    ],
    "dg-05-rooms": [
        ("4 + Math.floor(Math.random() * 6)", "3 + Math.floor(Math.random() * 7)"),
        ("  const start = center(rooms[0]);\n",
         "  const start = { x: rooms[0].x + 1, y: rooms[0].y + 1 };\n"),
    ],
    "dg-06-corridors": [
        # Every room joined to the first one.
        (_TUNNEL_LOOP,
         "  for (let i = 1; i < rooms.length; i++) {\n    tunnel(grid, center(rooms[0]), center(rooms[i]));\n  }\n"),
        # The corridor dug from the other end.
        ("tunnel(grid, center(rooms[i - 1]), center(rooms[i]));",
         "tunnel(grid, center(rooms[i]), center(rooms[i - 1]));"),
    ],
    "dg-07-stairs": [
        ("  const end = center(rooms[rooms.length - 1]);\n",
         "  const end = center(rooms[1 + Math.floor(Math.random() * (rooms.length - 1))]);\n"),
    ],
    "dg-08-enemies": [
        ("Math.abs(dx) >= Math.abs(dy)", "Math.abs(dx) > Math.abs(dy)"),
    ],
    "dg-09-bump": [
        ("    if (target.hp <= 0) enemies = enemies.filter((e) => e !== target);\n",
         "    if (target.hp <= 0) enemies.splice(enemies.indexOf(target), 1);\n"),
    ],
    "dg-10-fog": [
        # Square vision.
        ("dx * dx + dy * dy > RADIUS * RADIUS", "Math.max(Math.abs(dx), Math.abs(dy)) > RADIUS"),
        ("Math.round(player.x + (dx * i) / steps)", "Math.floor(player.x + (dx * i) / steps)"),
    ],
    "dg-11-potions": [
        ("  items = items.filter((i) => i !== found);\n", "  items.splice(items.indexOf(found), 1);\n"),
    ],
    "dg-12-gameover": [
        ("  depth = 1;\n  player.hp = player.maxHp;\n  potions = 0;\n  state = 'playing';\n  generate();\n",
         "  generate();\n  depth = 1;\n  player.hp = player.maxHp;\n  potions = 0;\n  state = 'playing';\n"),
    ],
}


class ShapeTests(unittest.TestCase):
    def test_ids_are_unique_and_named_for_the_track(self) -> None:
        ids = [s.id for s in DUNGEON_STEPS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(DUNGEON_STEPS), 13)
        for i, s in enumerate(DUNGEON_STEPS, start=1):
            with self.subTest(step=s.id):
                self.assertTrue(s.id.startswith(f"dg-{i:02d}-"))
                self.assertEqual(s.track, "Dungeon")
                self.assertGreater(len(s.teaches), 120)
                self.assertTrue(s.goal.endswith("."))
                if s.check:
                    self.assertTrue(s.hint)

    def test_each_step_starts_where_the_last_one_finished(self) -> None:
        for before, after in zip(DUNGEON_STEPS, DUNGEON_STEPS[1:]):
            with self.subTest(step=after.id):
                self.assertEqual(after.starter, before.solution)

    def test_only_the_last_step_is_open(self) -> None:
        self.assertEqual([s.id for s in DUNGEON_STEPS if not s.check], [DUNGEON_STEPS[-1].id])

    def test_every_mistake_names_a_real_step(self) -> None:
        ids = {s.id for s in DUNGEON_STEPS}
        self.assertLessEqual(set(MISTAKES) | set(OTHER_WAYS), ids)

    def test_every_checked_step_has_a_mistake(self) -> None:
        checked = {s.id for s in DUNGEON_STEPS if s.check}
        self.assertEqual(checked - set(MISTAKES), set())

    def test_the_program_is_plain_text_with_unix_line_endings(self) -> None:
        for s in DUNGEON_STEPS:
            with self.subTest(step=s.id):
                self.assertNotIn("\r", s.solution)
                self.assertTrue(s.solution.endswith("\n"))


@unittest.skipUnless(HAS_NODE, "needs node")
class CheckTests(unittest.TestCase):
    def test_every_solution_passes_and_every_starter_fails(self) -> None:
        for s in DUNGEON_STEPS:
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
            for change in swaps:
                with self.subTest(step=step_id, change=_label(change)):
                    got = run_check(_swap(s.solution, change), s.check)
                    self.assertFalse(got.passed, "the check let this mistake through")

    def test_other_right_answers_pass(self) -> None:
        for step_id, swaps in OTHER_WAYS.items():
            s = _step(step_id)
            for change in swaps:
                with self.subTest(step=step_id, change=_label(change)):
                    got = run_check(_swap(s.solution, change), s.check)
                    self.assertTrue(got.passed, got.message)


if __name__ == "__main__":
    unittest.main()
