"""Canvas: the Python Tower defense steps and their checks.

Like the JavaScript Tower defense (test_canvas_towers.py), but the program is
Python and the check plays it in a child process. A check is held to three
things: the step's own solution passes, its starter (the step before,
finished) does not, and the mistakes people really make at that step fail it
too - moving per frame instead of per second, overshooting (or never turning
at) a waypoint, a road of waypoint tiles only, building on the road, the
nearest target instead of the furthest along, `max()` with no `default=`, a
reload counted in frames, a shot that flies on after its target dies, a reward
paid twice, a wave that ends too soon, lives lost every frame a creep sits at
the end, removing from a list while a `for` walks it, a `global` line that is
missing a name (UnboundLocalError - or, in restart(), silence), a wave plan
that restart() forgets. A check that let those through would be checking
nothing.

Creeps, towers and shots may be dataclasses or dicts; the checks work with
both, and so do these tests (`_as_dicts` rewrites every solution with dicts).
The tests look steps up by id in their own module, so they need no
registration in canvas/__init__.py.
"""

from __future__ import annotations

import re

import pytest

from code_coach.canvas import STEPS as ALL_STEPS
from code_coach.canvas import check_step, run_py_check
from code_coach.canvas.content_pytowers import PYTOWERS_STEPS as STEPS

BY_ID = {s.id: s for s in STEPS}

_REGISTERED = all(s.id in {a.id for a in ALL_STEPS} for s in STEPS)


def _swap(code: str, old: str, new: str) -> str:
    assert code.count(old) >= 1, old
    return code.replace(old, new)


def _swaps(code: str, entry) -> str:
    """Apply one mistake or one other way: a single (old, new), or a list of them made together."""
    for old, new in (entry if isinstance(entry, list) else [entry]):
        code = _swap(code, old, new)
    return code


def _label(entry) -> str:
    old, new = (entry if isinstance(entry, list) else [entry])[-1]
    return (new or old)[:60]


# -- Pieces of the solutions the mistakes cut out ---------------------------------

_DRAW_ROAD_LOOP = "    for point in path[1:]:\n        ctx.line_to(*point)\n"
_CREEPS_FILTER_2 = "    creeps = [c for c in creeps if c.leg < len(path)]\n"
_CREEPS_FILTER = "    creeps = [c for c in creeps if c.hp > 0 and c.leg < len(path)]\n"
_SPAWN_BLOCK = (
    "    spawn_timer += dt\n    if spawn_timer >= SPAWN_EVERY:\n"
    "        spawn_timer -= SPAWN_EVERY\n        spawn_creep()\n"
)
_TILE_AT = "    return int(x // TILE), int(y // TILE)\n"
_PATH_TILES = "path_tiles = set()\nfor a, b in zip(path, path[1:]):\n    path_tiles |= tiles_between(a, b)\n"
_BUILD_GUARD = "    if (col, row) in path_tiles or taken:\n"
_PICK = "    return max(in_range, key=lambda c: c.dist, default=None)\n"
_RANGE_TEST = "math.dist((c.x, c.y), (t.x, t.y)) <= t.range"
_RELOAD = "    t.reload = max(0, t.reload - dt)\n"
_SHOT_FILTER = "not s.done and s.target in creeps"
_CLICK_GUARD_9 = (
    "    if (col, row) in path_tiles or taken or money < TOWER_COST:\n        return\n    money -= TOWER_COST\n"
)
_PAY = "    money += sum(c.reward for c in creeps if c.hp <= 0)\n"
_WAVE_END = "        if not queue and not creeps:\n"
_SPAWN_ONE = "        if queue and spawn_timer >= SPAWN_EVERY:\n            spawn_timer -= SPAWN_EVERY\n            spawn_creep(queue.pop(0))\n"
_WON = "            if wave == len(waves):\n                state = 'won'\n            else:\n                state = 'countdown'\n                countdown = GAP\n"
_GLOBAL_RESTART = "    global creeps, towers, shots, money, lives, wave, state, countdown, queue, spawn_timer, plan\n"
_LIVES_LINE = "sum(1 for c in creeps if c.hp > 0 and c.leg >= len(path))"

#: Wrong programs, each a real mistake at that step, that the check must fail.
#: An entry is one (what to find in the solution, what to put there instead),
#: or a list of those, made together.
MISTAKES: dict[str, list] = {
    "pytd-01-path": [
        # Tile corners, not tile centres.
        ("path = [(20, 60), (380, 60)", "path = [(0, 40), (380, 60)"),
        # The last piece of road is left out.
        (_DRAW_ROAD_LOOP, "    for point in path[1:-1]:\n        ctx.line_to(*point)\n"),
        ("(140, 220), (140, 300)]", "(140, 220)]"),
        # A hairline, not a road.
        ("ctx.line_width = TILE", "ctx.line_width = 2"),
        # Never stroked, or never drawn.
        ("    ctx.stroke()\n", ""),
        ("    draw_road()\n", ""),
        ("TILE = 40", "TILE = 20"),
    ],
    "pytd-02-walk": [
        # A step per frame: right at 60 a second, wrong at 30.
        ("    left = c.speed * dt\n", "    left = c.speed / 60\n"),
        # Stops at the first waypoint and never turns.
        ("            c.leg += 1\n            c.dist += d\n            left -= d\n", "            c.dist += d\n            left = 0\n"),
        # Overshoots the waypoint instead of snapping onto it.
        ("        if d <= left:\n", "        if d < 0.5:\n"),
        # dist is never added up.
        ("            c.dist += left\n", ""),
        # Walks off the end and stays in the game.
        (_CREEPS_FILTER_2, "    pass\n"),
        # Re-binding creeps without saying global: UnboundLocalError.
        ("    global creeps\n", ""),
        # Born in the middle of the canvas; drawn in the corner.
        ("    return Creep(*path[0])", "    return Creep(240, 160)"),
        ("    ctx.arc(c.x, c.y, 12, 0, math.tau)\n", "    ctx.arc(0, 0, 12, 0, math.tau)\n"),
    ],
    "pytd-03-health": [
        # The bar never shrinks.
        ("BAR_W * max(0, c.hp) / c.max_hp", "BAR_W"),
        # Pixels of bar = hp, not a fraction of the bar.
        ("BAR_W * max(0, c.hp) / c.max_hp", "c.hp"),
        # A creep on exactly 0 hp lives on; the dead are never taken out.
        ("c.hp > 0 and c.leg < len(path)", "c.hp >= 0 and c.leg < len(path)"),
        ("c.hp > 0 and c.leg < len(path)", "c.leg < len(path)"),
        # The bar stays where the creep was born.
        ("x = c.x - BAR_W / 2", "x = path[0][0] - BAR_W / 2"),
        # Removing from a list while a for walks it: the next creep is skipped.
        (_CREEPS_FILTER,
         "    for c in creeps:\n        if c.hp <= 0 or c.leg >= len(path):\n            creeps.remove(c)\n"),
    ],
    "pytd-04-spawn": [
        # One creep every frame.
        (_SPAWN_BLOCK, "    spawn_creep()\n"),
        # A creep every 90 frames: right at 60 a second, wrong at 30.
        (_SPAWN_BLOCK, "    spawn_timer += 1\n    if spawn_timer >= 90:\n        spawn_timer = 0\n        spawn_creep()\n"),
        # The timer is never taken down.
        ("        spawn_timer -= SPAWN_EVERY\n", ""),
        # The same creep pushed again and again; born in the middle of the screen.
        ("    creeps.append(make_creep())", "    creeps.append(creeps[0] if creeps else make_creep())"),
        ("    creeps.append(make_creep())", "    creeps.append(Creep(240, 160))"),
        # spawn_timer re-bound without global: UnboundLocalError.
        ("    global creeps, spawn_timer\n", "    global creeps\n"),
        ("SPAWN_EVERY = 1.5", "SPAWN_EVERY = 3"),
    ],
    "pytd-05-build": [
        # Nearest tile boundary, not the tile the point is in.
        (_TILE_AT, "    return round(x / TILE), round(y / TILE)\n"),
        # Row and column the wrong way round.
        (_TILE_AT, "    return int(y // TILE), int(x // TILE)\n"),
        # Builds on the road.
        (_BUILD_GUARD, "    if taken:\n"),
        # Builds twice on one tile.
        (_BUILD_GUARD, "    if (col, row) in path_tiles:\n"),
        # Only the waypoint tiles count as road.
        (_PATH_TILES, "path_tiles = {tile_at(*p) for p in path}\n"),
        # The last tile of each piece of road is left out.
        ("for col in range(min(col1, col2), max(col1, col2) + 1)", "for col in range(min(col1, col2), max(col1, col2))"),
        # Never listens for clicks.
        ("on_click(click)\n", ""),
        # Not on the tile's centre.
        ("    return Tower(col, row, col * TILE + TILE / 2, row * TILE + TILE / 2)", "    return Tower(col, row, col * TILE, row * TILE)"),
        # Never drawn.
        ("    ctx.fill_rect(t.x - 14, t.y - 14, 28, 28)\n", "    pass\n"),
    ],
    "pytd-06-target": [
        # The nearest to the tower, not the furthest along.
        (_PICK, "    return min(in_range, key=lambda c: math.dist((c.x, c.y), (t.x, t.y)), default=None)\n"),
        # The last one in the list; the first one in the list.
        (_PICK, "    return in_range[-1] if in_range else None\n"),
        (_PICK, "    return in_range[0] if in_range else None\n"),
        # The one that has walked least.
        (_PICK, "    return min(in_range, key=lambda c: c.dist, default=None)\n"),
        # max() of an empty list: ValueError.
        (_PICK, "    return max(in_range, key=lambda c: c.dist)\n"),
        # Range as a square.
        (_RANGE_TEST, "abs(c.x - t.x) <= t.range and abs(c.y - t.y) <= t.range"),
        # Squared distance against an unsquared range; an unsquared one against a squared range.
        (_RANGE_TEST, "(c.x - t.x) ** 2 + (c.y - t.y) ** 2 <= t.range"),
        (_RANGE_TEST, "math.dist((c.x, c.y), (t.x, t.y)) <= t.range * t.range"),
        # No line drawn.
        ("        ctx.line_to(target.x, target.y)\n", ""),
    ],
    "pytd-07-cooldown": [
        # Reload counted in frames: right at 60 a second, wrong at 30.
        (_RELOAD, "    t.reload = max(0, t.reload - 1 / 60)\n"),
        # No reload at all.
        ("    t.reload = t.rate\n", ""),
        # The reload never counts down.
        (_RELOAD, ""),
        # Hits everything in range, not just the target.
        ("    target.hp -= t.damage\n",
         "    for c in creeps:\n        if math.dist((c.x, c.y), (t.x, t.y)) <= t.range:\n            c.hp -= t.damage\n"),
        # update never calls update_tower.
        ("    for t in towers:\n        update_tower(t, dt)\n", ""),
    ],
    "pytd-08-shots": [
        # Still an instant hit.
        ("    shots.append(Shot(t.x, t.y, target, t.damage))\n", "    target.hp -= t.damage\n"),
        # Aimed once, when it is fired.
        ("    dx, dy = s.target.x - s.x, s.target.y - s.y\n",
         "    if not hasattr(s, 'aim'):\n        s.aim = (s.target.x, s.target.y)\n    dx, dy = s.aim[0] - s.x, s.aim[1] - s.y\n"),
        # A step per frame.
        ("    step = s.speed * dt\n", "    step = s.speed / 60\n"),
        # Never removed after it lands: it hits again every frame.
        (_SHOT_FILTER, "s.target in creeps"),
        # Keeps flying after its target has gone.
        (_SHOT_FILTER, "not s.done"),
        # Re-binding shots without global: UnboundLocalError.
        ("    global creeps, shots, spawn_timer\n", "    global creeps, spawn_timer\n"),
        # A trail list shared by every shot (dataclass refuses it).
        ("trail: list = field(default_factory=list)", "trail: list = []"),
        # A trail that grows for ever, or is never written.
        ("    del s.trail[:-6]\n", ""),
        ("    s.trail.append((s.x, s.y))\n", ""),
        # Never drawn.
        ("    ctx.arc(s.x, s.y, 4, 0, math.tau)\n", "    ctx.arc(0, 0, 4, 0, math.tau)\n"),
    ],
    "pytd-09-money": [
        # A tower is free.
        ("    money -= TOWER_COST\n", ""),
        # Builds with no money.
        ("    if (col, row) in path_tiles or taken or money < TOWER_COST:\n", "    if (col, row) in path_tiles or taken:\n"),
        # Takes the money before looking at the tile.
        (_CLICK_GUARD_9,
         "    money -= TOWER_COST\n    if (col, row) in path_tiles or taken or money < 0:\n        return\n"),
        # The reward is a number in the code, not the creep's own.
        ("sum(c.reward for c in creeps if c.hp <= 0)", "sum(5 for c in creeps if c.hp <= 0)"),
        # An escape pays too.
        ("sum(c.reward for c in creeps if c.hp <= 0)", "sum(c.reward for c in creeps if c.hp <= 0 or c.leg >= len(path))"),
        # Paid when each shot lands: two shots on one creep pay twice.
        [("def move_shot(s, dt):\n", "def move_shot(s, dt):\n    global money\n"),
         ("        s.target.hp -= s.damage\n", "        s.target.hp -= s.damage\n        if s.target.hp <= 0:\n            money += s.target.reward\n"),
         (_PAY, "")],
        # Paid after the dead are already gone.
        [(_PAY, ""), (_CREEPS_FILTER, _CREEPS_FILTER + _PAY)],
        # Never shown.
        ("    ctx.fill_text(f'${money}', 10, 20)\n", ""),
        # click re-binds money without global: UnboundLocalError.
        ("def click(x, y):\n    global money\n", "def click(x, y):\n"),
    ],
    "pytd-10-waves": [
        # The wave ends when its last creep is spawned, not when it is gone.
        (_WAVE_END, "        if not queue:\n"),
        # The whole wave at once.
        (_SPAWN_ONE, "        while queue:\n            spawn_creep(queue.pop(0))\n"),
        # Every wave as tough as the first; one creep too many.
        ("        yield [hp] * count\n", "        yield [10] * count\n"),
        ("        yield [hp] * count\n", "        yield [hp] * (count + 1)\n"),
        # A countdown counted in frames.
        ("        countdown -= dt\n", "        countdown -= 1 / 60\n"),
        # The countdown is not set again between waves.
        ("                countdown = GAP\n", ""),
        # Nothing ever says the game is won: next() runs off the end of the plan.
        (_WON, "            state = 'countdown'\n            countdown = GAP\n"),
        ("        ctx.fill_text('You win!', 170, 170)\n", ""),
        ("    ctx.fill_text(f'Wave {wave}/{len(waves)}', 90, 20)\n", ""),
        # queue re-bound without global: it is quietly local, so nothing is ever sent.
        ("    global wave, queue, spawn_timer, state\n", "    global wave, spawn_timer, state\n"),
        # A fresh generator every wave: every wave is the first.
        ("    queue = next(plan)\n", "    queue = next(wave_plan())\n"),
    ],
    "pytd-11-lives": [
        # The creep stays at the end, so a life goes every frame.
        (_CREEPS_FILTER, "    creeps = [c for c in creeps if c.hp > 0]\n"),
        # The game runs on after game over.
        ("    if state == 'over':\n        return\n", ""),
        # The game is never over.
        ("    if lives <= 0:\n        state = 'over'\n", ""),
        # A creep killed at the last step still costs a life.
        (_LIVES_LINE, "sum(1 for c in creeps if c.leg >= len(path))"),
        # Enter restarts a game that is not over; so does any key.
        ("    if key == 'Enter' and state == 'over':\n", "    if key == 'Enter':\n"),
        ("    if key == 'Enter' and state == 'over':\n", "    if state == 'over':\n"),
        # A restart that leaves something behind.
        ("    creeps = []\n    towers = []\n", "    towers = []\n"),
        ("    towers = []\n    shots = []\n", "    shots = []\n"),
        ("    shots = []\n    money = 100\n", "    money = 100\n"),
        ("    money = 100\n    lives = 10\n", "    lives = 10\n"),
        ("    lives = 10\n    wave = 0\n", "    wave = 0\n"),
        ("    wave = 0\n    state = 'countdown'\n", "    state = 'countdown'\n"),
        ("    countdown = 3\n    queue = []\n", "    queue = []\n"),
        ("    queue = []\n    spawn_timer = 0\n", "    spawn_timer = 0\n"),
        ("    spawn_timer = 0\n    plan = wave_plan()\n", "    plan = wave_plan()\n"),
        # The wave plan is not made again: the second game carries on from the first.
        ("    spawn_timer = 0\n    plan = wave_plan()\n", "    spawn_timer = 0\n"),
        # A global line missing a name: restart() runs, and quietly does nothing for it.
        ("state, countdown, queue", "countdown, queue"),
        ("money, lives, wave", "lives, wave"),
        (", spawn_timer, plan\n", ", spawn_timer\n"),
        # Lives and the message never shown.
        ("    ctx.fill_text(f'Lives: {lives}', 220, 20)\n", ""),
        ("        ctx.fill_text('Game over', 150, 160)\n", ""),
    ],
}

#: Right programs written another way, which the check must still pass. Each
#: is one (old, new) swap, or a list of swaps made together.
OTHER_WAYS: dict[str, list] = {
    "pytd-01-path": [
        # Waypoints as lists, not tuples.
        ("path = [(20, 60), (380, 60), (380, 220), (140, 220), (140, 300)]",
         "path = [[20, 60], [380, 60], [380, 220], [140, 220], [140, 300]]"),
    ],
    "pytd-02-walk": [
        # Snap onto the waypoint and lose what is left of the step.
        ("            left -= d\n", "            left = 0\n"),
        # math.dist for the distance.
        ("d = math.hypot(px - c.x, py - c.y)", "d = math.dist((px, py), (c.x, c.y))"),
        # Change the list in place: no global needed.
        [("    global creeps\n", ""), (_CREEPS_FILTER_2, "    creeps[:] = [c for c in creeps if c.leg < len(path)]\n")],
        # Creeps compared by value, not identity.
        ("@dataclass(eq=False)\nclass Creep", "@dataclass\nclass Creep"),
    ],
    "pytd-03-health": [
        [("    global creeps\n", ""), (_CREEPS_FILTER, "    creeps[:] = [c for c in creeps if c.hp > 0 and c.leg < len(path)]\n")],
        (_CREEPS_FILTER, "    creeps = list(filter(lambda c: c.hp > 0 and c.leg < len(path), creeps))\n"),
        ("BAR_W * max(0, c.hp) / c.max_hp", "c.hp / c.max_hp * BAR_W if c.hp > 0 else 0"),
    ],
    "pytd-04-spawn": [
        # A plain timer reset instead of carrying the remainder: sloppier, but still one every 1.5 seconds.
        ("        spawn_timer -= SPAWN_EVERY\n", "        spawn_timer = 0\n"),
    ],
    "pytd-05-build": [
        (_TILE_AT, "    return divmod(x, TILE)[0], divmod(y, TILE)[0]\n"),
        (_TILE_AT, "    return int(x / TILE), int(y / TILE)\n"),
        # Tiles worked out with plain loops.
        (_PATH_TILES,
         "path_tiles = set()\nfor (x1, y1), (x2, y2) in zip(path, path[1:]):\n"
         "    col1, row1 = tile_at(x1, y1)\n    col2, row2 = tile_at(x2, y2)\n"
         "    for col in range(min(col1, col2), max(col1, col2) + 1):\n"
         "        for row in range(min(row1, row2), max(row1, row2) + 1):\n"
         "            path_tiles.add((col, row))\n"),
        (_PATH_TILES, "path_tiles = set().union(*(tiles_between(a, b) for a, b in zip(path, path[1:])))\n"),
    ],
    "pytd-06-target": [
        # Sorted, biggest first.
        (_PICK, "    return sorted(in_range, key=lambda c: c.dist, reverse=True)[0] if in_range else None\n"),
        (_RANGE_TEST, "math.hypot(c.x - t.x, c.y - t.y) <= t.range"),
    ],
    "pytd-07-cooldown": [
        # The reload is allowed to go below zero.
        (_RELOAD, "    t.reload -= dt\n"),
    ],
    "pytd-08-shots": [
        # A hit when it is close enough, not when it is exactly there.
        ("    if d <= step:\n", "    if d <= max(step, 6):\n"),
        ("@dataclass(eq=False)\nclass Creep", "@dataclass\nclass Creep"),
    ],
    "pytd-09-money": [
        # A loop instead of sum().
        (_PAY, "    for c in creeps:\n        if c.hp <= 0:\n            money += c.reward\n"),
    ],
    "pytd-10-waves": [
        # No generator: the wave's tuple is looked up by number.
        ("    queue = next(plan)\n", "    count, hp = waves[wave - 1]\n    queue = [hp] * count\n"),
        (_SPAWN_ONE, "        while queue and spawn_timer >= SPAWN_EVERY:\n            spawn_timer -= SPAWN_EVERY\n            spawn_creep(queue.pop(0))\n"),
        ("            spawn_creep(queue.pop(0))\n", "            spawn_creep(queue.pop())\n"),
    ],
    "pytd-11-lives": [
        # Empty the lists in place instead of re-binding them.
        (_GLOBAL_RESTART + "    creeps = []\n    towers = []\n    shots = []\n",
         "    global money, lives, wave, state, countdown, queue, spawn_timer, plan\n"
         "    creeps.clear()\n    towers.clear()\n    shots.clear()\n"),
    ],
}


def _as_dicts(code: str) -> str:
    """The same program with creeps, towers and shots dicts, not dataclasses: c['x'] for c.x."""

    def factory(m: re.Match[str]) -> str:
        fields = re.findall(r"^    (\w+): \w+(?: = (.*?))?(?:  # .*)?$", m.group(2), re.M)
        params = ", ".join(
            (f"{n}=None" if d.startswith("field(") else f"{n}={d}") if d else n for n, d in fields
        )
        body = ", ".join(
            f"'{n}': [] if {n} is None else {n}" if d.startswith("field(") else f"'{n}': {n}" for n, d in fields
        )
        return f"def {m.group(1)}({params}):\n    return {{{body}}}\n"

    made = re.sub(r"@dataclass(?:\(eq=False\))?\nclass (\w+):\n((?:    .+\n)+)", factory, code)
    made = re.sub(r"from dataclasses import dataclass(?:, field)?\n", "", made)
    fields = "x|y|leg|dist|speed|hp|max_hp|reward|col|row|range|damage|rate|reload|done|trail|target"
    made = re.sub(rf"\b(c|t|s|target)\.({fields})\b", r"\1['\2']", made)
    made = re.sub(rf"\]\.({fields})\b", r"]['\1']", made)
    assert "@dataclass" not in made
    return made


class TestShape:
    def test_ids_unique_numbered_and_titled(self) -> None:
        ids = [s.id for s in STEPS]
        assert len(ids) == len(set(ids))
        assert len(STEPS) == 12
        for n, s in enumerate(STEPS, 1):
            assert re.fullmatch(rf"pytd-{n:02d}-[a-z-]+", s.id), s.id
            assert s.title
            assert len(s.teaches) > 120, s.id
            assert s.goal.endswith("."), s.id

    def test_they_are_python_steps_on_their_own_track(self) -> None:
        assert {s.track for s in STEPS} == {"Tower defense (Python)"}
        assert {s.language for s in STEPS} == {"python"}
        assert all(s.kind == "canvas" for s in STEPS)

    @pytest.mark.skipif(not _REGISTERED, reason="PYTOWERS_STEPS is not in canvas/__init__.py STEPS yet")
    def test_they_are_registered_after_the_other_python_tracks(self) -> None:
        ids = [s.id for s in ALL_STEPS]
        first = ids.index(STEPS[0].id)
        assert ids[first:first + len(STEPS)] == [s.id for s in STEPS]
        order = [s.track for s in ALL_STEPS]
        assert order.index("Dodge (Python)") < order.index("Tower defense (Python)")
        assert order.index("To-do") < order.index("Tower defense (Python)")

    def test_each_step_starts_where_the_last_one_finished(self) -> None:
        for before, after in zip(STEPS, STEPS[1:]):
            assert after.starter == before.solution, after.id

    def test_only_the_last_step_is_open(self) -> None:
        assert [s.id for s in STEPS if not s.check] == [STEPS[-1].id]

    def test_every_program_is_python_that_compiles_and_uses_the_library(self) -> None:
        for s in STEPS:
            for code in (s.starter, s.solution):
                compile(code, s.id, "exec")
                assert "from canvas import" in code, s.id
                assert "ctx.fillStyle" not in code and "requestAnimationFrame" not in code
                assert "\r" not in code and not code.endswith("\n\n")
            if s.check:
                compile(s.check, s.id + " check", "exec")

    def test_every_mistake_and_other_way_names_a_real_step(self) -> None:
        for step_id in list(MISTAKES) + list(OTHER_WAYS):
            assert step_id in BY_ID, step_id

    def test_every_checked_step_has_a_real_mistake(self) -> None:
        for s in STEPS:
            if s.check:
                assert MISTAKES.get(s.id), f"{s.id} has no mistake the check is held against"

    def test_the_hints_are_written(self) -> None:
        for s in STEPS:
            if s.check:
                assert s.hint, s.id

    def test_the_goals_name_what_the_checks_read(self) -> None:
        names = {
            "pytd-01-path": ["TILE", "path", "line_width"],
            "pytd-02-walk": ["Creep", "make_creep", "creeps", "leg", "dist", "speed", "global creeps"],
            "pytd-03-health": ["hp", "max_hp", "BAR_W"],
            "pytd-04-spawn": ["SPAWN_EVERY", "spawn_timer", "spawn_creep", "global"],
            "pytd-05-build": ["towers", "Tower", "make_tower", "tile_at", "path_tiles", "on_click"],
            "pytd-06-target": ["range", "find_target", "default="],
            "pytd-07-cooldown": ["damage", "rate", "reload", "update_tower"],
            "pytd-08-shots": ["shots", "Shot", "trail", "done", "move_shot", "field(default_factory=list)",
                              "global shots"],
            "pytd-09-money": ["money", "TOWER_COST", "reward", "global money"],
            "pytd-10-waves": ["waves", "wave", "state", "countdown", "queue", "GAP", "wave_plan", "next(plan)"],
            "pytd-11-lives": ["lives", "restart", "plan", "global", "'over'"],
        }
        for step_id, wanted in names.items():
            for name in wanted:
                assert name in BY_ID[step_id].goal, f"{step_id}: the goal does not say {name}"

    def test_the_python_way_is_what_gets_taught(self) -> None:
        text = " ".join(s.teaches for s in STEPS)
        for word in ("@dataclass", "eq=False", "default_factory", "zip(path, path[1:])", "math.hypot", "math.dist",
                     "//", "divmod", "|=", "set", "any(", "default=None", "list comprehension", "UnboundLocalError",
                     "creeps.remove(c)", "yield", "next(plan)", "global", "f-string", "max(", "min(", "key=lambda"):
            assert word in text, word

    def test_the_timing_sensitive_checks_run_at_30_and_60_frames_a_second(self) -> None:
        for step_id in ("pytd-02-walk", "pytd-04-spawn", "pytd-07-cooldown", "pytd-08-shots", "pytd-10-waves"):
            check = BY_ID[step_id].check
            assert "30" in check and "60" in check, step_id


class TestChecks:
    def test_every_solution_passes_its_check(self) -> None:
        for s in STEPS:
            if not s.check:
                continue
            got = run_py_check(s.solution, s.check)
            assert got.passed, f"{s.id}: {got.message}"

    def test_every_starter_fails_its_check(self) -> None:
        for s in STEPS:
            if not s.check:
                continue
            got = run_py_check(s.starter, s.check)
            assert not got.passed, s.id
            assert got.message, s.id

    def test_real_mistakes_fail(self) -> None:
        for step_id, entries in MISTAKES.items():
            s = BY_ID[step_id]
            for entry in entries:
                got = run_py_check(_swaps(s.solution, entry), s.check)
                assert not got.passed, f"{step_id}: the check let this mistake through: {_label(entry)!r}"
                assert got.message, step_id

    def test_other_right_answers_pass(self) -> None:
        for step_id, entries in OTHER_WAYS.items():
            s = BY_ID[step_id]
            for entry in entries:
                got = run_py_check(_swaps(s.solution, entry), s.check)
                assert got.passed, f"{step_id}: {_label(entry)!r}: {got.message}"

    def test_dicts_pass_wherever_the_entities_are_dataclasses(self) -> None:
        for s in STEPS:
            if not s.check:
                continue
            code = _as_dicts(s.solution)
            if s is not STEPS[0]:  # step 1 has no entities yet
                assert code != s.solution
            got = run_py_check(code, s.check)
            assert got.passed, f"{s.id}: {got.message}"

    def test_dict_mistakes_fail_too(self) -> None:
        # The dict form of a few mistakes that hang on a field's name: the check reads both forms alike.
        for step_id, entry in (
            ("pytd-03-health", (_CREEPS_FILTER,
                                "    for c in creeps:\n        if c.hp <= 0 or c.leg >= len(path):\n"
                                "            creeps.remove(c)\n")),
            ("pytd-06-target", (_PICK, "    return min(in_range, key=lambda c: c.dist, default=None)\n")),
            ("pytd-08-shots", ("    del s.trail[:-6]\n", "")),
            ("pytd-09-money", ("sum(c.reward for c in creeps if c.hp <= 0)", "sum(c.reward for c in creeps)")),
        ):
            s = BY_ID[step_id]
            got = run_py_check(_as_dicts(_swaps(s.solution, entry)), s.check)
            assert not got.passed, step_id

    def test_the_checks_say_what_to_fix_not_just_that_it_failed(self) -> None:
        walk = BY_ID["pytd-02-walk"]
        got = run_py_check(_swap(walk.solution, "    left = c.speed * dt\n", "    left = c.speed / 60\n"), walk.check)
        assert "30 frames a second" in got.message
        got = run_py_check(_swap(walk.solution, "        if d <= left:\n", "        if d < 0.5:\n"), walk.check)
        assert "overshoots" in got.message
        got = run_py_check(_swap(walk.solution, "    global creeps\n", ""), walk.check)
        assert "UnboundLocalError" in got.message and "line" in got.message

        health = BY_ID["pytd-03-health"]
        got = run_py_check(_swap(health.solution, _CREEPS_FILTER,
                                 "    for c in creeps:\n        if c.hp <= 0 or c.leg >= len(path):\n"
                                 "            creeps.remove(c)\n"), health.check)
        assert "skips" in got.message and "new list" in got.message

        build = BY_ID["pytd-05-build"]
        got = run_py_check(_swap(build.solution, _PATH_TILES, "path_tiles = {tile_at(*p) for p in path}\n"), build.check)
        assert "BETWEEN" in got.message
        got = run_py_check(_swap(build.solution, _TILE_AT, "    return round(x / TILE), round(y / TILE)\n"), build.check)
        assert "round" in got.message

        target = BY_ID["pytd-06-target"]
        got = run_py_check(_swap(target.solution, _PICK, "    return max(in_range, key=lambda c: c.dist)\n"), target.check)
        assert "default=None" in got.message
        got = run_py_check(_swap(target.solution, _PICK,
                                 "    return min(in_range, key=lambda c: math.dist((c.x, c.y), (t.x, t.y)), default=None)\n"),
                           target.check)
        assert "furthest" in got.message

        shots = BY_ID["pytd-08-shots"]
        got = run_py_check(_swap(shots.solution, "trail: list = field(default_factory=list)", "trail: list = []"),
                           shots.check)
        assert "mutable default" in got.message

        money = BY_ID["pytd-09-money"]
        got = run_py_check(_swap(money.solution, "def click(x, y):\n    global money\n", "def click(x, y):\n"),
                           money.check)
        assert "UnboundLocalError" in got.message

        lives = BY_ID["pytd-11-lives"]
        got = run_py_check(_swap(lives.solution, "state, countdown, queue", "countdown, queue"), lives.check)
        assert "global line" in got.message
        got = run_py_check(_swap(lives.solution, "    spawn_timer = 0\n    plan = wave_plan()\n", "    spawn_timer = 0\n"),
                           lives.check)
        assert "wave_plan()" in got.message

    def test_a_crash_is_reported_with_its_line(self) -> None:
        s = STEPS[0]
        got = run_py_check(s.starter + "\nnope()\n", s.check)
        assert not got.passed
        assert "nope" in got.message and "line" in got.message

    def test_an_endless_loop_is_reported_not_waited_on(self) -> None:
        s = STEPS[0]
        got = run_py_check(s.starter + "\nwhile True:\n    pass\n", s.check)
        assert not got.passed
        assert "loop that never ends" in got.message

    @pytest.mark.skipif(not _REGISTERED, reason="PYTOWERS_STEPS is not in canvas/__init__.py STEPS yet")
    def test_the_open_step_always_passes(self) -> None:
        got = check_step(STEPS[-1].id, "")
        assert got is not None and got.passed

    @pytest.mark.skipif(not _REGISTERED, reason="PYTOWERS_STEPS is not in canvas/__init__.py STEPS yet")
    def test_check_step_runs_a_python_step_through_the_python_harness(self) -> None:
        s = STEPS[3]
        assert check_step(s.id, s.solution).passed
        assert not check_step(s.id, s.starter).passed
