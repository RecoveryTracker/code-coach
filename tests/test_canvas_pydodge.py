"""Canvas: the Python Dodge steps and their checks.

Like the JavaScript Dodge (test_canvas.py), but the program is Python and
the check plays it in a child process. A check is held to three things: the
step's own solution passes, its starter (the step before, finished) does
not, and the mistakes people really make at that step - moving per frame
instead of per second, a held-key set that is never emptied, `<=` in the
collision, enemies that are never removed - fail it too. A check that let
those through would be checking nothing.
"""

from __future__ import annotations

import re

from code_coach.canvas import STEPS as ALL_STEPS
from code_coach.canvas import check_step, run_py_check, step
from code_coach.canvas.content_pydodge import PYDODGE_STEPS as STEPS


def _swap(code: str, old: str, new: str) -> str:
    assert code.count(old) >= 1, old
    return code.replace(old, new)


def _by_id(step_id: str):
    found = step(step_id)
    assert found is not None, step_id
    return found


_OVERLAPS_LE = (
    "def overlaps(a, b):\n"
    "    return (a['x'] <= b['x'] + b['size'] and b['x'] <= a['x'] + a['size'] and\n"
    "            a['y'] <= b['y'] + b['size'] and b['y'] <= a['y'] + a['size'])\n"
)
_OVERLAPS = (
    "def overlaps(a, b):\n"
    "    return (a['x'] < b['x'] + b['size'] and b['x'] < a['x'] + a['size'] and\n"
    "            a['y'] < b['y'] + b['size'] and b['y'] < a['y'] + a['size'])\n"
)
_CLAMP = "    player['x'] = max(0, min(WIDTH - player['size'], player['x']))\n"
_BACKGROUND = "    ctx.fill_style = '#10141f'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n\n"

#: Wrong programs, each a real mistake at that step, that the check must fail.
MISTAKES: dict[str, list[tuple[str, str, str]]] = {
    "pydodge-02-background": [
        # The square first: the background paints over it.
        ("ctx.fill_style = '#10141f'\nctx.fill_rect(0, 0, WIDTH, HEIGHT)\n\n"
         "ctx.fill_style = 'tomato'\nctx.fill_rect(100, 80, 40, 40)\n",
         "", "ctx.fill_style = 'tomato'\nctx.fill_rect(100, 80, 40, 40)\n"
         "ctx.fill_style = '#10141f'\nctx.fill_rect(0, 0, WIDTH, HEIGHT)\n"),
    ],
    "pydodge-03-player": [
        ("player = {'x': 100, 'y': 260, 'size': 32}", "", "player = {'x': 100, 'y': 260, 'size': 40}"),
    ],
    "pydodge-04-loop": [
        (_BACKGROUND, "", ""),  # no repaint: the old squares smear
        ("on_frame(loop)\n", "", ""),  # never started
        ("on_frame(loop)\n", "", "on_frame(loop())\n"),  # the result of loop, not loop
    ],
    "pydodge-05-delta-time": [
        ("player['x'] += player['speed'] * dt", "", "player['x'] += 4"),
        ("player['x'] += player['speed'] * dt", "", "player['x'] += player['speed']"),
        # dt written in as a constant: right at 60 frames a second, wrong at 30.
        ("player['x'] += player['speed'] * dt", "", "player['x'] += player['speed'] * (1 / 60)"),
    ],
    "pydodge-06-keys": [
        # Moving per frame, not per second.
        ("player['x'] += player['speed'] * dt", "", "player['x'] += 2"),
        # A held-key set of your own that is added to and never emptied.
        ("from canvas import ctx, WIDTH, HEIGHT, on_frame, keys\n", "",
         "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down\n\nkeys = set()\non_key_down(keys.add)\n"),
        # Only one direction.
        ("    if 'ArrowLeft' in keys:\n        player['x'] -= player['speed'] * dt\n", "", ""),
    ],
    "pydodge-07-clamp": [
        ("min(WIDTH - player['size'], player['x'])", "", "min(WIDTH, player['x'])"),
        ("max(0, min(WIDTH - player['size'], player['x']))", "", "min(WIDTH - player['size'], player['x'])"),
    ],
    "pydodge-08-enemy": [
        ("e['y'] += e['speed'] * dt", "", "e['y'] += 2"),
        ("    for e in enemies:\n        ctx.fill_rect(e['x'], e['y'], e['size'], e['size'])\n", "", ""),
    ],
    "pydodge-09-spawn": [
        # Never removed: the list grows forever.
        ("    enemies = [e for e in enemies if e['y'] < HEIGHT]\n", "", ""),
        # Three a second: the timer counts too fast.
        ("    spawn_timer += dt\n", "", "    spawn_timer += dt * 3\n"),
        # Spawning beyond the right edge.
        ("random.uniform(0, WIDTH - 24)", "", "random.uniform(WIDTH, WIDTH + 100)"),
        # Re-binding enemies without saying global: UnboundLocalError.
        ("    global spawn_timer, enemies\n", "", "    global spawn_timer\n"),
        # The timer never reset: after the first second, an enemy every frame.
        ("        spawn_timer -= 1\n", "", ""),
    ],
    "pydodge-10-collision": [
        (_OVERLAPS, "", _OVERLAPS_LE),
        ("    if state != 'playing':\n        return\n", "", ""),
        # x only: forgot the y half.
        ("            a['y'] < b['y'] + b['size'] and b['y'] < a['y'] + a['size'])", "", "            True)"),
        ("        state = 'over'\n", "", "        pass\n"),
    ],
    "pydodge-11-score": [
        ("    score += dt\n", "", "    score += 1\n"),
        ("    ctx.fill_text(f'Score: {int(score)}', 10, 22)\n", "", ""),
    ],
    "pydodge-12-restart": [
        # Enemies not cleared: the one on the player ends the new game at once.
        ("    enemies = []\n    spawn_timer = 0\n", "", "    spawn_timer = 0\n"),
        ("        ctx.fill_text('Game over', 150, 150)\n", "", ""),
        ("    score = 0\n    state = 'playing'\n", "", "    state = 'playing'\n"),
        ("on_key_down(key_down)\n", "", ""),
    ],
}

#: Right programs written another way, which the check must still pass. Each
#: way is a list of swaps made together.
OTHER_WAYS: dict[str, list[list[tuple[str, str]]]] = {
    "pydodge-04-loop": [
        [(_BACKGROUND, "    ctx.fill_style = 'black'\n    ctx.fill_rect(0, 0, 480, 320)\n\n")],
    ],
    "pydodge-06-keys": [
        # Your own held-key set, kept the right way.
        [("from canvas import ctx, WIDTH, HEIGHT, on_frame, keys\n",
          "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down, on_key_up\n\n"
          "keys = set()\non_key_down(keys.add)\non_key_up(keys.discard)\n")],
    ],
    "pydodge-07-clamp": [
        [(_CLAMP,
          "    if player['x'] < 0:\n        player['x'] = 0\n"
          "    if player['x'] > WIDTH - player['size']:\n        player['x'] = WIDTH - player['size']\n")],
    ],
    "pydodge-09-spawn": [
        # A plain timer reset instead of carrying the remainder: sloppier,
        # but still one enemy a second, so it passes.
        [("        spawn_timer -= 1\n", "        spawn_timer = 0\n")],
        # Changing the list in place needs no global for it.
        [("    global spawn_timer, enemies\n", "    global spawn_timer\n"),
         ("    enemies = [e for e in enemies if e['y'] < HEIGHT]\n",
          "    enemies[:] = [e for e in enemies if e['y'] < HEIGHT]\n")],
        [("random.uniform(0, WIDTH - 24)", "random.random() * (WIDTH - 24)")],
    ],
    "pydodge-10-collision": [
        [("    if any(overlaps(player, e) for e in enemies):\n        state = 'over'\n",
          "    for e in enemies:\n        if overlaps(player, e):\n            state = 'over'\n")],
    ],
    "pydodge-11-score": [
        [("f'Score: {int(score)}'", "f'Score: {score:.0f}'")],
        [("f'Score: {int(score)}'", "'Score: ' + str(int(score))")],
    ],
}


def _as_dataclass(code: str) -> str:
    """The same program with its player a @dataclass: player.x for player['x']."""
    made = re.sub(r"player = \{'x': 100, 'y': 260, 'size': 32(, 'speed': 240)?\}",
                  lambda m: ("@dataclass\nclass Player:\n    x: float\n    y: float\n    size: int\n"
                             + ("    speed: float = 240\n" if m.group(1) else "")
                             + "\n\nplayer = Player(100, 260, 32)"), code)
    assert made != code
    return "from dataclasses import dataclass\n" + re.sub(r"player\['(\w+)'\]", r"player.\1", made)


#: Steps whose player is the only thing with fields: they can swap a dict for a dataclass.
DATACLASS_STEPS = [f"pydodge-{n:02d}-{name}" for n, name in
                   ((3, "player"), (4, "loop"), (5, "delta-time"), (6, "keys"), (7, "clamp"))]


class TestShape:
    def test_ids_unique_numbered_and_titled(self) -> None:
        ids = [s.id for s in STEPS]
        assert len(ids) == len(set(ids))
        for n, s in enumerate(STEPS, 1):
            assert re.fullmatch(rf"pydodge-{n:02d}-[a-z-]+", s.id), s.id
            assert s.title
            assert len(s.teaches) > 120, s.id
            assert s.goal.endswith("."), s.id

    def test_they_are_python_steps_on_their_own_track_and_registered(self) -> None:
        assert {s.track for s in STEPS} == {"Dodge (Python)"}
        assert {s.language for s in STEPS} == {"python"}
        assert all(s.kind == "canvas" for s in STEPS)
        assert [s.id for s in ALL_STEPS if s.language == "python"] == [s.id for s in STEPS]
        # The other tracks stay JavaScript, in their own order, ahead of this one.
        order = [s.track for s in ALL_STEPS]
        assert order.index("Dodge") == 0
        assert order.index("To-do") < order.index("Dodge (Python)")

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

    def test_every_mistake_and_other_way_names_a_real_step(self) -> None:
        for step_id in list(MISTAKES) + list(OTHER_WAYS) + DATACLASS_STEPS:
            assert step(step_id) is not None, step_id

    def test_every_checked_step_has_a_real_mistake(self) -> None:
        for s in STEPS:
            if s.check and s.id != "pydodge-01-square":
                assert MISTAKES.get(s.id), f"{s.id} has no mistake the check is held against"

    def test_the_hints_are_written(self) -> None:
        for s in STEPS:
            if s.check:
                assert s.hint, s.id


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
        for step_id, swaps in MISTAKES.items():
            s = _by_id(step_id)
            for old, _, new in swaps:
                got = run_py_check(_swap(s.solution, old, new), s.check)
                assert not got.passed, f"{step_id}: the check let this mistake through: {old[:50]!r}"
                assert got.message, step_id

    def test_other_right_answers_pass(self) -> None:
        for step_id, swaps in OTHER_WAYS.items():
            s = _by_id(step_id)
            for variant in swaps:
                code = s.solution
                for old, new in variant:
                    code = _swap(code, old, new)
                got = run_py_check(code, s.check)
                assert got.passed, f"{step_id}: {variant[0][0][:50]!r}: {got.message}"

    def test_a_dataclass_player_passes_wherever_the_player_is_all_there_is(self) -> None:
        for step_id in DATACLASS_STEPS:
            s = _by_id(step_id)
            got = run_py_check(_as_dataclass(s.solution), s.check)
            assert got.passed, f"{step_id}: {got.message}"

    def test_the_checks_say_what_to_fix_not_just_that_it_failed(self) -> None:
        got = run_py_check(_by_id("pydodge-05-delta-time").solution.replace("* dt", "* (1 / 60)"),
                           _by_id("pydodge-05-delta-time").check)
        assert "30 frames a second" in got.message
        got = run_py_check(_by_id("pydodge-09-spawn").solution.replace("    global spawn_timer, enemies\n", ""),
                           _by_id("pydodge-09-spawn").check)
        assert "UnboundLocalError" in got.message and "line" in got.message

    def test_a_crash_is_reported_with_its_line(self) -> None:
        s = STEPS[0]
        got = run_py_check(s.starter + "\nnope()\n", s.check)
        assert not got.passed
        assert "nope" in got.message and "line 5" in got.message

    def test_an_endless_loop_is_reported_not_waited_on(self) -> None:
        s = STEPS[0]
        got = run_py_check(s.starter + "\nwhile True:\n    pass\n", s.check)
        assert not got.passed
        assert "loop that never ends" in got.message

    def test_the_open_step_always_passes(self) -> None:
        got = check_step(STEPS[-1].id, "")
        assert got is not None and got.passed

    def test_check_step_runs_a_python_step_through_the_python_harness(self) -> None:
        s = STEPS[3]
        assert check_step(s.id, s.solution).passed
        assert not check_step(s.id, s.starter).passed
