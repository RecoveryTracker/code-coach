"""Canvas: the Python Snake steps and their checks.

Like the JavaScript Snake (test_canvas_snake.py), but the program is Python
and the check plays it in a child process. A check is held to three things:
the step's own solution passes, its starter (the step before, finished) does
not, and the mistakes people really make at that step fail it too - moving
every frame (or by counting frames) instead of per tick, a tick accumulator
that drops the remainder or only ever steps once, a 180 degree reversal (and
the Up-then-Left slip), food on the snake or `random.choice` on a set, `is`
for `==` on tuples, an off-by-one wall test, a tail that counts as a
collision (or does not count when the snake eats), scoring on every tick, a
restart that leaves next_dir behind, a `global` line that is missing a name.
A check that let those through would be checking nothing.

The body may be a list or a deque; the checks work with both, and so do
these tests.
"""

from __future__ import annotations

import re

import pytest

from code_coach.canvas import STEPS as ALL_STEPS
from code_coach.canvas import check_step, run_py_check
from code_coach.canvas.content_pysnake import PYSNAKE_STEPS as STEPS

BY_ID = {s.id: s for s in STEPS}


def _swap(code: str, old: str, new: str) -> str:
    assert code.count(old) >= 1, old
    return code.replace(old, new)


def _by_id(step_id: str):
    return BY_ID[step_id]


_REGISTERED = all(s.id in {a.id for a in ALL_STEPS} for s in STEPS)

_TICK_BLOCK = "    acc += dt\n    while acc >= TICK:\n        acc -= TICK\n        step()\n"
_MOVE = "    snake.appendleft((x + dx, y + dy))\n    snake.pop()\n"
_EAT_BRANCH = "    if head == food:\n        spawn_food()\n    else:\n        snake.pop()\n"
_FREE = "    cells = {(col, row) for col in range(COLS) for row in range(ROWS)}\n    free = cells - set(snake)\n"
_KEY_IF = "    if key in DIRS:\n        next_dir = DIRS[key]\n"
_KEY_REVERSE = "        dx, dy = direction\n        if DIRS[key] != (-dx, -dy):\n            next_dir = DIRS[key]\n"
_WALL = "    if not (0 <= col < COLS and 0 <= row < ROWS):\n        state = 'over'\n        return\n    snake.appendleft(head)\n"
_TAIL = "    occupied = set(snake)\n    if not eating:\n        occupied.discard(snake[-1])\n"
_SCORE_BRANCH = "    if eating:\n        score += 10\n        spawn_food()\n    else:\n        snake.pop()\n"
_MATCH = (
    "    match key:\n        case 'Enter' if state == 'over':\n            reset()\n"
    "        case 'ArrowUp' | 'ArrowDown' | 'ArrowLeft' | 'ArrowRight':\n"
    "            dx, dy = direction\n            if DIRS[key] != (-dx, -dy):\n                next_dir = DIRS[key]\n"
)
_OVER_AGAIN = "        ctx.font = '16px monospace'\n        ctx.fill_text('Press Enter to play again', 120, 200)\n"

#: Wrong programs, each a real mistake at that step, that the check must fail:
#: (what to find in the solution, what to put there instead).
MISTAKES: dict[str, list[tuple[str, str]]] = {
    "pysnake-01-tiles": [
        ("COLS = WIDTH // CELL", "COLS = WIDTH"),
        # / gives 24.0, a float: it equals 24 but is not a whole number.
        ("COLS = WIDTH // CELL", "COLS = WIDTH / CELL"),
        ("ctx.fill_rect(col * CELL, row * CELL,", "ctx.fill_rect(row * CELL, col * CELL,"),
        # The colour argument ignored.
        ("    ctx.fill_style = color\n", ""),
        # The tile first: the background paints over it.
        ("    ctx.fill_style = '#10141f'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n    draw_cell(3, 2, '#4fd1c5')\n",
         "    draw_cell(3, 2, '#4fd1c5')\n    ctx.fill_style = '#10141f'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n"),
    ],
    "pysnake-02-snake": [
        # Only the head is drawn.
        ("    for col, row in snake:\n        draw_cell(col, row, '#68d391')\n",
         "    draw_cell(*snake[0], '#68d391')\n"),
        # Pixels, not tiles.
        ("snake = [(12, 8), (11, 8), (10, 8)]", "snake = [(240, 160), (220, 160), (200, 160)]"),
        # Lists, not tuples.
        ("snake = [(12, 8), (11, 8), (10, 8)]", "snake = [[12, 8], [11, 8], [10, 8]]"),
        # The test tile left in.
        ("    for col, row in snake:\n", "    draw_cell(3, 2, '#4fd1c5')\n    for col, row in snake:\n"),
    ],
    "pysnake-03-tick": [
        # One step per frame.
        (_TICK_BLOCK, "    step()\n"),
        # Time kept by counting frames: right at 60 a second, wrong at 30.
        (_TICK_BLOCK, "    acc += 1\n    if acc % 7 == 0:\n        step()\n"),
        # The remainder thrown away.
        ("        acc -= TICK\n", "        acc = 0\n"),
        # `if`: a long frame holding two ticks only steps once.
        ("    while acc >= TICK:", "    if acc >= TICK:"),
        # The tail never leaves.
        (_MOVE, "    snake.appendleft((x + dx, y + dy))\n"),
        # A list for a cell, not a tuple.
        ("snake.appendleft((x + dx, y + dy))", "snake.appendleft([x + dx, y + dy])"),
        # Re-binding acc without `global`: UnboundLocalError.
        ("    global acc\n", ""),
    ],
    "pysnake-04-steer": [
        # Up is down.
        ("'ArrowUp': (0, -1)", "'ArrowUp': (0, 1)"),
        # direction never follows next_dir.
        ("    direction = next_dir\n", ""),
        # No `global`: the handler quietly sets a local and nothing changes.
        ("    global next_dir\n", ""),
        # Looking a key up without asking: 'q' is a KeyError.
        (_KEY_IF, "    next_dir = DIRS[key]\n"),
    ],
    "pysnake-05-no-reverse": [
        # No protection at all.
        (_KEY_REVERSE, "        next_dir = DIRS[key]\n"),
        # Judged against next_dir: Up then Left slips through.
        ("        dx, dy = direction\n        if DIRS", "        dx, dy = next_dir\n        if DIRS"),
    ],
    "pysnake-06-food": [
        # Any cell, snake or not.
        ("    free = cells - set(snake)\n", "    free = cells\n"),
        # A set is not a sequence: TypeError.
        ("    food = random.choice(sorted(free))\n", "    food = random.choice(free)\n"),
        # Off by one: a column past the grid.
        ("for col in range(COLS) for row", "for col in range(COLS + 1) for row"),
        # Always the same cell.
        ("random.choice(sorted(free))", "sorted(free)[0]"),
        # Never called, so there is no food.
        ("spawn_food()\n\n\ndef step", "def step"),
    ],
    "pysnake-07-grow": [
        # Always grows.
        ("    else:\n        snake.pop()\n", ""),
        # Never grows.
        (_EAT_BRANCH, "    if head == food:\n        spawn_food()\n    snake.pop()\n"),
        # `is` on two separately built tuples.
        ("if head == food:", "if head is food:"),
        # Grows, but the food stays where it was.
        ("    if head == food:\n        spawn_food()\n    else:", "    if head == food:\n        pass\n    else:"),
    ],
    "pysnake-08-walls": [
        ("0 <= col < COLS", "0 <= col <= COLS"),
        ("0 <= row < ROWS", "0 <= row <= ROWS"),
        ("0 <= col < COLS", "0 < col < COLS"),
        # Only the far edges tested.
        ("0 <= col < COLS and 0 <= row < ROWS", "col < COLS and row < ROWS"),
        # Moves into the wall, then notices.
        (_WALL, "    snake.appendleft(head)\n    if not (0 <= col < COLS and 0 <= row < ROWS):\n        state = 'over'\n        return\n"),
        # Never stops updating.
        ("    if state != 'playing':\n        return\n", ""),
        ("        ctx.fill_text('Game over', 150, 170)\n", ""),
        # state re-bound without `global`: a quiet local.
        ("    global direction, state\n", "    global direction\n"),
    ],
    "pysnake-09-self": [
        # The tail counts even though it is moving away.
        (_TAIL, "    occupied = set(snake)\n"),
        # The tail never counts, even when the snake eats and it stays.
        (_TAIL, "    occupied = set(snake)\n    occupied.discard(snake[-1])\n"),
        # The head finds itself.
        ("    occupied = set(snake)\n", "    occupied = set(snake) | {head}\n"),
        # The body forgotten.
        (" or head in occupied", ""),
    ],
    "pysnake-10-score": [
        # Scores on every step that does not eat.
        (_SCORE_BRANCH,
         "    if eating:\n        spawn_food()\n    else:\n        score += 10\n        snake.pop()\n"),
        # Never shown.
        ("    ctx.fill_text(f'Score: {score}', 10, 20)\n", ""),
        ("score += 10", "score += 1"),
        # score re-bound without `global`: UnboundLocalError.
        ("    global direction, state, score\n", "    global direction, state\n"),
    ],
    "pysnake-11-restart": [
        # next_dir left behind (the arrow pressed during game over is still in it).
        ("    next_dir = (1, 0)\n    acc = 0\n    score = 0\n", "    acc = 0\n    score = 0\n"),
        # direction left behind.
        ("    direction = (1, 0)\n    next_dir", "    next_dir"),
        ("    score = 0\n    state = 'playing'\n    spawn_food()", "    state = 'playing'\n    spawn_food()"),
        # `score = 0` makes a quiet local: score is not on the global line.
        ("    global snake, direction, next_dir, acc, score, state\n",
         "    global snake, direction, next_dir, acc, state\n"),
        # Old food kept: it may be on the new snake.
        ("    state = 'playing'\n    spawn_food()\n", "    state = 'playing'\n"),
        # The old snake kept.
        ("    snake = deque(START)\n", ""),
        # The tuple itself, not a deque made from it: no appendleft.
        ("    snake = deque(START)\n", "    snake = START\n"),
        ("case 'Enter' if state == 'over':", "case 'Enter':"),
        ("        case 'Enter' if state == 'over':\n            reset()\n", "        case _ if state == 'over':\n            reset()\n"),
        ("on_key_down(key_down)\n", ""),
        (_OVER_AGAIN, ""),
    ],
}

#: Right programs written another way, which the check must still pass. Each
#: way is a list of swaps made together.
OTHER_WAYS: dict[str, list[list[tuple[str, str]]]] = {
    "pysnake-03-tick": [
        # A timer instead of an accumulator.
        [("from canvas import ctx, WIDTH, HEIGHT, on_frame\n", "from canvas import ctx, WIDTH, HEIGHT, on_frame, every\n"),
         ("def update(dt):\n" + _TICK_BLOCK.replace("    acc += dt\n", "    global acc\n    acc += dt\n", 1),
          "def update(dt):\n    pass\n\n\nevery(TICK, step)\n")],
        # A list body: insert at the front.
        [("from collections import deque\n\n", ""),
         ("snake = deque([(12, 8), (11, 8), (10, 8)])", "snake = [(12, 8), (11, 8), (10, 8)]"),
         ("snake.appendleft((x + dx, y + dy))", "snake.insert(0, (x + dx, y + dy))")],
        # A list body: build a new list by slicing, which re-binds snake.
        [("from collections import deque\n\n", ""),
         ("snake = deque([(12, 8), (11, 8), (10, 8)])", "snake = [(12, 8), (11, 8), (10, 8)]"),
         (_MOVE, "    snake = [(x + dx, y + dy)] + snake[:-1]\n"),
         ("def step():\n", "def step():\n    global snake\n")],
    ],
    "pysnake-04-steer": [
        # if / elif instead of a dict.
        [(_KEY_IF,
          "    if key == 'ArrowUp':\n        next_dir = (0, -1)\n    elif key == 'ArrowDown':\n        next_dir = (0, 1)\n"
          "    elif key == 'ArrowLeft':\n        next_dir = (-1, 0)\n    elif key == 'ArrowRight':\n        next_dir = (1, 0)\n")],
        [(_KEY_IF, "    next_dir = DIRS.get(key, next_dir)\n")],
    ],
    "pysnake-05-no-reverse": [
        [("        dx, dy = direction\n        if DIRS[key] != (-dx, -dy):\n",
          "        tx, ty = DIRS[key]\n        dx, dy = direction\n        if (tx + dx, ty + dy) != (0, 0):\n")],
    ],
    "pysnake-06-food": [
        # Guess until it is free.
        [(_FREE + "    food = random.choice(sorted(free))\n",
          "    while True:\n        food = (random.randrange(COLS), random.randrange(ROWS))\n"
          "        if food not in snake:\n            break\n")],
        # A list comprehension for the free cells.
        [(_FREE + "    food = random.choice(sorted(free))\n",
          "    free = [(col, row) for col in range(COLS) for row in range(ROWS) if (col, row) not in snake]\n"
          "    food = random.choice(free)\n")],
        [("random.choice(sorted(free))", "random.choice(list(free))")],
    ],
    "pysnake-07-grow": [
        [(_EAT_BRANCH, "    if head != food:\n        snake.pop()\n    else:\n        spawn_food()\n")],
    ],
    "pysnake-08-walls": [
        [("    if not (0 <= col < COLS and 0 <= row < ROWS):\n",
          "    if col < 0 or col >= COLS or row < 0 or row >= ROWS:\n")],
        [("    col, row = head\n    if not (0 <= col < COLS and 0 <= row < ROWS):\n",
          "    if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS):\n")],
    ],
    "pysnake-09-self": [
        # A list for the body: slice the tail off.
        [(_TAIL, "    occupied = list(snake) if eating else list(snake)[:-1]\n")],
        [(_TAIL, "    occupied = set(snake) if eating else set(list(snake)[:-1])\n")],
    ],
    "pysnake-10-score": [
        [("f'Score: {score}'", "'Score: ' + str(score)")],
        [("f'Score: {score}'", "'Score: %d' % score")],
    ],
    "pysnake-11-restart": [
        # if / elif instead of match.
        [(_MATCH,
          "    if key == 'Enter':\n        if state == 'over':\n            reset()\n    elif key in DIRS:\n"
          "        dx, dy = direction\n        if DIRS[key] != (-dx, -dy):\n            next_dir = DIRS[key]\n")],
        # Empty the deque and fill it again, in place.
        [("    snake = deque(START)\n", "    snake.clear()\n    snake.extend(START)\n")],
    ],
}


def _with_list_body(code: str) -> str:
    """The same program with its body a plain list: insert(0, cell) for appendleft."""
    made = code.replace("from collections import deque\n", "")
    made = made.replace("deque([(12, 8), (11, 8), (10, 8)])", "[(12, 8), (11, 8), (10, 8)]")
    made = made.replace("deque(START)", "list(START)").replace(".appendleft(", ".insert(0, ")
    assert made != code and "deque" not in made
    return made


#: Steps whose body is a deque: they can swap it for a list.
LIST_BODY_STEPS = [s.id for s in STEPS[2:11]]


class TestShape:
    def test_ids_unique_numbered_and_titled(self) -> None:
        ids = [s.id for s in STEPS]
        assert len(ids) == len(set(ids))
        assert len(STEPS) == 12
        for n, s in enumerate(STEPS, 1):
            assert re.fullmatch(rf"pysnake-{n:02d}-[a-z-]+", s.id), s.id
            assert s.title
            assert len(s.teaches) > 120, s.id
            assert s.goal.endswith("."), s.id

    def test_they_are_python_steps_on_their_own_track(self) -> None:
        assert {s.track for s in STEPS} == {"Snake (Python)"}
        assert {s.language for s in STEPS} == {"python"}
        assert all(s.kind == "canvas" for s in STEPS)

    @pytest.mark.skipif(not _REGISTERED, reason="PYSNAKE_STEPS is not in canvas/__init__.py STEPS yet")
    def test_they_are_registered_after_the_first_python_track(self) -> None:
        ids = [s.id for s in ALL_STEPS]
        first = ids.index(STEPS[0].id)
        assert ids[first:first + len(STEPS)] == [s.id for s in STEPS]
        order = [s.track for s in ALL_STEPS]
        assert order.index("Dodge (Python)") < order.index("Snake (Python)")
        assert order.index("To-do") < order.index("Snake (Python)")

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
        for step_id in list(MISTAKES) + list(OTHER_WAYS) + LIST_BODY_STEPS:
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
            "pysnake-02-snake": ["snake"],
            "pysnake-03-tick": ["direction", "acc", "TICK"],
            "pysnake-04-steer": ["next_dir", "DIRS"],
            "pysnake-06-food": ["food", "spawn_food"],
            "pysnake-08-walls": ["state"],
            "pysnake-10-score": ["score"],
            "pysnake-11-restart": ["reset", "next_dir"],
        }
        for step_id, wanted in names.items():
            for name in wanted:
                assert name in BY_ID[step_id].goal, f"{step_id}: the goal does not say {name}"

    def test_the_python_way_is_what_gets_taught(self) -> None:
        text = " ".join(s.teaches for s in STEPS)
        for word in ("tuple", "hashable", "deque", "appendleft", "set(snake)", "random.choice", "sorted(", "global",
                     "UnboundLocalError", "match", "f-string", "unpack"):
            assert word in text, word


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
            for old, new in swaps:
                got = run_py_check(_swap(s.solution, old, new), s.check)
                assert not got.passed, f"{step_id}: the check let this mistake through: {(new or old)[:60]!r}"
                assert got.message, step_id

    def test_other_right_answers_pass(self) -> None:
        for step_id, ways in OTHER_WAYS.items():
            s = _by_id(step_id)
            for variant in ways:
                code = s.solution
                for old, new in variant:
                    code = _swap(code, old, new)
                got = run_py_check(code, s.check)
                assert got.passed, f"{step_id}: {variant[-1][1][:50]!r}: {got.message}"

    def test_a_list_body_passes_wherever_the_body_is_a_deque(self) -> None:
        for step_id in LIST_BODY_STEPS:
            s = _by_id(step_id)
            got = run_py_check(_with_list_body(s.solution), s.check)
            assert got.passed, f"{step_id}: {got.message}"

    def test_the_checks_say_what_to_fix_not_just_that_it_failed(self) -> None:
        tick = _by_id("pysnake-03-tick")
        got = run_py_check(_swap(tick.solution, _TICK_BLOCK, "    acc += 1\n    if acc % 7 == 0:\n        step()\n"), tick.check)
        assert "30 frames a second" in got.message
        got = run_py_check(_swap(tick.solution, "        acc -= TICK\n", "        acc = 0\n"), tick.check)
        assert "acc -= TICK" in got.message
        got = run_py_check(_swap(tick.solution, "    while acc >= TICK:", "    if acc >= TICK:"), tick.check)
        assert "while acc >= TICK" in got.message
        got = run_py_check(_swap(tick.solution, "    global acc\n", ""), tick.check)
        assert "UnboundLocalError" in got.message and "line" in got.message

        food = _by_id("pysnake-06-food")
        got = run_py_check(_swap(food.solution, "random.choice(sorted(free))", "random.choice(free)"), food.check)
        assert "TypeError" in got.message and "line" in got.message

        grow = _by_id("pysnake-07-grow")
        got = run_py_check(_swap(grow.solution, "if head == food:", "if head is food:"), grow.check)
        assert "==" in got.message

        steer = _by_id("pysnake-04-steer")
        got = run_py_check(_swap(steer.solution, _KEY_IF, "    next_dir = DIRS[key]\n"), steer.check)
        assert "KeyError" in got.message

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

    def test_the_open_step_always_passes(self) -> None:
        if not _REGISTERED:
            pytest.skip("not registered yet")
        got = check_step(STEPS[-1].id, "")
        assert got is not None and got.passed

    @pytest.mark.skipif(not _REGISTERED, reason="PYSNAKE_STEPS is not in canvas/__init__.py STEPS yet")
    def test_check_step_runs_a_python_step_through_the_python_harness(self) -> None:
        s = STEPS[3]
        assert check_step(s.id, s.solution).passed
        assert not check_step(s.id, s.starter).passed
