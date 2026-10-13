"""Canvas: the Python Breakout steps and their checks.

Like the JavaScript Breakout (test_canvas_breakout.py), but the program is
Python and the check plays it in a child process. A check is held to three
things: the step's own solution passes, its starter (the step before,
finished) does not, and the mistakes people really make at that step fail it
too - moving per frame instead of per second, a ball left sitting inside the
paddle, a bounce that always goes straight back, taking bricks out of a list
while a `for` walks it, a hit test on the ball's centre alone, a life lost on
every frame the ball is below the screen, `any(bricks)` for `not bricks`, a
`global` line that is missing a name, a mutable default argument that makes a
second wall of 80 bricks. A check that let those through would be checking
nothing.

Paddle, ball and bricks may be dataclasses or dicts; the checks work with
both, and so do these tests (`_as_dicts` rewrites every solution with dicts).
"""

from __future__ import annotations

import re

import pytest

from code_coach.canvas import STEPS as ALL_STEPS
from code_coach.canvas import check_step, run_py_check
from code_coach.canvas.content_pybreakout import PYBREAKOUT_STEPS as STEPS

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


# -- Pieces of the solutions the mistakes cut out --------------------------------

_BG = "    ctx.fill_style = '#10141f'\n    ctx.fill_rect(0, 0, WIDTH, HEIGHT)\n"
_PADDLE_DRAW = "    ctx.fill_style = '#4fd1c5'\n    ctx.fill_rect(paddle.x, paddle.y, paddle.w, paddle.h)\n"
_CLAMP = "    paddle.x = max(0, min(WIDTH - paddle.w, paddle.x))\n"
_MOUSE = "    if mouse.x != last_mouse_x:\n        last_mouse_x = mouse.x\n        paddle.x = mouse.x - paddle.w / 2\n"
_MOVE_BALL = "    ball.x += ball.vx * dt\n    ball.y += ball.vy * dt\n"
_LEFT_WALL = "    if ball.x - ball.r < 0:\n        ball.x = ball.r\n        ball.vx = math.copysign(ball.vx, 1)\n"
_RIGHT_WALL = "    if ball.x + ball.r > WIDTH:\n        ball.x = WIDTH - ball.r\n        ball.vx = math.copysign(ball.vx, -1)\n"
_TOP_WALL = "    if ball.y - ball.r < 0:\n        ball.y = ball.r\n        ball.vy = math.copysign(ball.vy, 1)\n"
_FLOOR = "    if ball.y + ball.r > HEIGHT:\n        ball.y = HEIGHT - ball.r\n        ball.vy = math.copysign(ball.vy, -1)\n"
_NEAREST = (
    "    nearest_x = max(r.x, min(c.x, r.x + r.w))\n    nearest_y = max(r.y, min(c.y, r.y + r.h))\n"
    "    return math.hypot(c.x - nearest_x, c.y - nearest_y) < c.r\n"
)
_AIM = "        ball.vx = speed * math.sin(angle)\n        ball.vy = -speed * math.cos(angle)\n"
_BRICKS = (
    "bricks = [\n    Brick(16 + col * 56, 30 + row * 22, 50, 16, color)\n"
    "    for row, color in enumerate(ROW_COLORS)\n    for col in range(8)\n]\n"
)
_DRAW_BRICKS = "    for b in bricks:\n        ctx.fill_style = b.color\n        ctx.fill_rect(b.x, b.y, b.w, b.h)\n"
_BREAK = (
    "    hit = [b for b in bricks if hits_rect(ball, b)]\n    if hit:\n"
    "        bricks = [b for b in bricks if b not in hit]\n        ball.vy = -ball.vy\n"
    "        score += 10 * len(hit)\n"
)
_LOSE9 = "    if ball.y - ball.r > HEIGHT:\n        lives -= 1\n        serve()\n"
_LOSE10 = (
    "        lives -= 1\n        if lives == 0:\n            state = 'over'\n        else:\n            serve()\n"
)
_MAKE = (
    "def make_bricks():\n    return [\n        Brick(16 + col * 56, 30 + row * 22, 50, 16, color)\n"
    "        for row, color in enumerate(ROW_COLORS)\n        for col in range(8)\n    ]\n"
)
_MESSAGES_DRAW = (
    "    if state in MESSAGES:\n        ctx.font = '32px monospace'\n"
    "        ctx.fill_text(MESSAGES[state], 150, 200)\n"
)

#: Wrong programs, each a real mistake at that step, that the check must fail.
#: An entry is one (what to find in the solution, what to put there instead),
#: or a list of those, made together.
MISTAKES: dict[str, list] = {
    "pybo-01-paddle": [
        # Width and height the wrong way round.
        ("Paddle(200, 296, 80, 10)", "Paddle(200, 296, 10, 80)"),
        # Drawn first: the background paints over it.
        (_BG + "\n" + _PADDLE_DRAW, _PADDLE_DRAW + "\n" + _BG),
        # Never drawn.
        ("\n" + _PADDLE_DRAW, ""),
        # The colour of the background.
        ("ctx.fill_style = '#4fd1c5'", "ctx.fill_style = '#10141f'"),
        # Drawn once while the program loads, not every frame.
        [("\n" + _PADDLE_DRAW, ""),
         ("on_frame(loop)\n", "ctx.fill_style = '#4fd1c5'\nctx.fill_rect(200, 296, 80, 10)\non_frame(loop)\n")],
    ],
    "pybo-02-keys": [
        # Per frame, not per second.
        [("        paddle.x -= paddle.speed * dt\n", "        paddle.x -= 4\n"),
         ("        paddle.x += paddle.speed * dt\n", "        paddle.x += 4\n")],
        # Speed with no dt: pixels a frame, 360 of them.
        ("paddle.speed * dt", "paddle.speed"),
        # Only one direction.
        ("    if 'ArrowLeft' in keys:\n        paddle.x -= paddle.speed * dt\n", ""),
        # No clamp, or half of one.
        (_CLAMP, "    pass\n"),
        ("max(0, min(WIDTH - paddle.w, paddle.x))", "min(WIDTH - paddle.w, paddle.x)"),
        ("min(WIDTH - paddle.w, paddle.x)", "min(WIDTH, paddle.x)"),
        # A held-key set of your own that is added to and never emptied.
        ("from canvas import ctx, WIDTH, HEIGHT, on_frame, keys\n",
         "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down\n\nkeys = set()\non_key_down(keys.add)\n"),
        # update never calls move_paddle.
        ("    move_paddle(dt)\n", "    pass\n"),
    ],
    "pybo-03-mouse": [
        # The mouse overwrites the keys on every frame.
        [(_MOUSE, "    paddle.x = mouse.x - paddle.w / 2\n"), ("    global last_mouse_x\n", "")],
        # Never remembers where the mouse was: the same thing.
        ("        last_mouse_x = mouse.x\n", ""),
        # The left edge under the pointer, not the centre.
        ("paddle.x = mouse.x - paddle.w / 2", "paddle.x = mouse.x"),
        # No clamp: the paddle hangs off the canvas.
        (_CLAMP, ""),
        # Re-binding without `global`: UnboundLocalError.
        ("    global last_mouse_x\n", ""),
        # Starting from None: the paddle jumps to the left edge as soon as the game starts.
        ("paddle = Paddle(200, 296, 80, 10)\nlast_mouse_x = mouse.x\n",
         "paddle = Paddle(200, 296, 80, 10)\nlast_mouse_x = None\n"),
        # The wrong axis.
        ("paddle.x = mouse.x - paddle.w / 2", "paddle.x = mouse.y - paddle.w / 2"),
    ],
    "pybo-04-ball": [
        # Per frame, not per second.
        (_MOVE_BALL, "    ball.x += 3\n    ball.y -= 3\n"),
        # Up is the wrong way.
        ("ball.y += ball.vy * dt", "ball.y -= ball.vy * dt"),
        # dt written in as a constant: right at 60 frames a second, wrong at 30.
        ("ball.x += ball.vx * dt", "ball.x += ball.vx / 60"),
        ("    ctx.begin_path()\n", ""),
        ("    ctx.fill()\n", "    ctx.stroke()\n"),
        ("ctx.arc(ball.x, ball.y, ball.r,", "ctx.arc(ball.x, ball.y, 4,"),
        # Never moved.
        ("    move_ball(dt)\n", "    pass\n"),
    ],
    "pybo-05-walls": [
        # Turned round, but left partly inside the wall.
        (_RIGHT_WALL, "    if ball.x + ball.r > WIDTH:\n        ball.vx = -ball.vx\n"),
        # Pushed back, never turned: it slides along the wall.
        ("        ball.vx = math.copysign(ball.vx, 1)\n", ""),
        ("        ball.vy = math.copysign(ball.vy, 1)\n", ""),
        # A wall forgotten.
        (_TOP_WALL, ""),
        (_FLOOR, ""),
        (_LEFT_WALL, ""),
        # The bounce changes the speed.
        ("ball.vx = math.copysign(ball.vx, 1)", "ball.vx = abs(ball.vx) * 1.1"),
        # Never called.
        ("    bounce_off_walls()\n", "    pass\n"),
    ],
    "pybo-06-paddle-bounce": [
        # Left inside the paddle: not sat back on top.
        ("        ball.y = paddle.y - ball.r\n", ""),
        # Always straight back, wherever it lands.
        (_AIM, "        ball.vy = -abs(ball.vy)\n"),
        # The angle the wrong way round.
        ("ball.vx = speed * math.sin(angle)", "ball.vx = -speed * math.sin(angle)"),
        # An angle, but the speed not kept.
        (_AIM, "        ball.vx = offset * 250\n        ball.vy = -abs(ball.vy)\n"),
        # Bounces the ball down into the paddle.
        ("ball.vy = -speed * math.cos(angle)", "ball.vy = speed * math.cos(angle)"),
        # The ball as a box: bounces off thin air by the corner.
        (_NEAREST,
         "    return c.x + c.r > r.x and c.x - c.r < r.x + r.w and c.y + c.r > r.y and c.y - c.r < r.y + r.h\n"),
        # Only the centre: the ball sinks in at the edge.
        (_NEAREST, "    return r.x <= c.x <= r.x + r.w and r.y <= c.y <= r.y + r.h\n"),
        # Bounces a ball that is moving up through the paddle.
        ("    if ball.vy > 0 and hits_rect(ball, paddle):", "    if hits_rect(ball, paddle):"),
        # The floor still bounces, so a miss is not a miss.
        (_TOP_WALL, _TOP_WALL + _FLOOR),
    ],
    "pybo-07-bricks": [
        # One brick, forty names for it.
        (_BRICKS, "bricks = [Brick(16, 30, 50, 16)] * 40\n"),
        # Row and column swapped.
        ("Brick(16 + col * 56, 30 + row * 22, 50, 16, color)", "Brick(16 + row * 56, 30 + col * 22, 50, 16, color)"),
        ("enumerate(ROW_COLORS)", "enumerate(ROW_COLORS[:4])"),
        ("for col in range(8)", "for col in range(7)"),
        # Never drawn.
        (_DRAW_BRICKS, ""),
    ],
    "pybo-08-break": [
        # The classic: taking bricks out of the list while a for walks it.
        (_BREAK,
         "    hit = False\n    for b in bricks:\n        if hits_rect(ball, b):\n            bricks.remove(b)\n"
         "            score += 10\n            hit = True\n    if hit:\n        ball.vy = -ball.vy\n"),
        # Stops after the first brick, and the second one turns the ball round again.
        (_BREAK,
         "    for b in bricks[:]:\n        if hits_rect(ball, b):\n            bricks.remove(b)\n"
         "            ball.vy = -ball.vy\n            score += 10\n            break\n"),
        # Turns the ball round once per brick: two bricks, no turn at all.
        (_BREAK,
         "    for b in bricks[:]:\n        if hits_rect(ball, b):\n            bricks.remove(b)\n"
         "            ball.vy = -ball.vy\n            score += 10\n"),
        # The wrong brick.
        ("        bricks = [b for b in bricks if b not in hit]\n", "        bricks.pop()\n"),
        ("        ball.vy = -ball.vy\n", ""),
        ("score += 10 * len(hit)", "score += 10"),
        ("        score += 10 * len(hit)\n", ""),
        ("    ctx.fill_text(f'Score: {score}', 10, 20)\n", ""),
        # The ball's centre only: it tunnels through the corners.
        (_NEAREST, "    return r.x <= c.x <= r.x + r.w and r.y <= c.y <= r.y + r.h\n"),
        # Re-binding without `global`: UnboundLocalError.
        ("    global bricks, score\n", "    global score\n"),
        ("    global bricks, score\n", "    global bricks\n"),
    ],
    "pybo-09-lives": [
        # Never served again.
        ("        serve()\n", ""),
        # No life taken.
        ("        lives -= 1\n", ""),
        ("    global lives\n", ""),
        # Never shown.
        ("    ctx.fill_text(f'Lives: {lives}', 390, 20)\n", ""),
        # A life lost on every frame, not only while the ball is below the screen.
        (_LOSE9, "    lives -= 1\n    if ball.y - ball.r > HEIGHT:\n        serve()\n"),
        # Served going down.
        ("ball.vx, ball.vy = 180, -180", "ball.vx, ball.vy = 180, 180"),
        ("ball.x, ball.y = 240, 200", "ball.x, ball.y = 240, 400"),
    ],
    "pybo-10-win-over": [
        # any() asks the opposite question: true while a brick is standing.
        ("    if not bricks:\n", "    if any(bricks):\n"),
        ("    if not bricks:\n", "    if bricks:\n"),
        # Never over: the last life is just served again.
        (_LOSE10, "        lives -= 1\n        serve()\n"),
        ("if lives == 0:", "if lives == 1:"),
        # update never stops.
        ("    if state != 'playing':\n        return\n", ""),
        # Nothing said.
        ("'won': 'You win!'", "'won': ''"),
        ("'over': 'Game over'", "'over': ''"),
        # state re-bound without `global`: a quiet local.
        ("    global state\n    if not bricks:", "    if not bricks:"),
        ("    global lives, state\n", "    global lives\n"),
    ],
    "pybo-11-restart": [
        ("    bricks = make_bricks()\n", ""),
        ("    score = 0\n    lives = 3\n", "    lives = 3\n"),
        ("    lives = 3\n    state = 'playing'\n", "    state = 'playing'\n"),
        ("    paddle.x = 200\n    serve()\n", "    paddle.x = 200\n"),
        ("    paddle.x = 200\n", ""),
        # state re-bound without `global`: the new game never starts.
        ("    global bricks, score, lives, state\n", "    global bricks, score, lives\n"),
        ("    global bricks, score, lives, state\n", "    global score, lives, state\n"),
        ("    global bricks, score, lives, state\n", "    global bricks, lives, state\n"),
        # Enter in the middle of a game, or any key at all.
        ("    if key == 'Enter' and state != 'playing':", "    if key == 'Enter':"),
        ("    if key == 'Enter' and state != 'playing':", "    if state != 'playing':"),
        # Only after a loss, not a win.
        ("state != 'playing':\n        restart()", "state == 'over':\n        restart()"),
        ("on_key_down(key_down)\n", ""),
        ("        ctx.fill_text('Press Enter to play again', 130, 230)\n", ""),
        # The mutable default argument: one list shared by every call, so the
        # second wall (the restart) is 80 bricks.
        (_MAKE,
         "def make_bricks(grid=[]):\n    for row, color in enumerate(ROW_COLORS):\n        for col in range(8):\n"
         "            grid.append(Brick(16 + col * 56, 30 + row * 22, 50, 16, color))\n    return grid\n"),
    ],
}

#: Right programs written another way, which the check must still pass. Each
#: way is one (old, new), or a list of them made together.
OTHER_WAYS: dict[str, list] = {
    "pybo-01-paddle": [
        ("Paddle(200, 296, 80, 10)", "Paddle(x=200, y=296, w=80, h=10)"),
        ("ctx.fill_style = '#4fd1c5'", "ctx.fill_style = 'orange'"),
    ],
    "pybo-02-keys": [
        # elif: right wins over left, nobody minds.
        ("    if 'ArrowRight' in keys:\n", "    elif 'ArrowRight' in keys:\n"),
        # A clamp written out.
        (_CLAMP,
         "    if paddle.x < 0:\n        paddle.x = 0\n"
         "    if paddle.x > WIDTH - paddle.w:\n        paddle.x = WIDTH - paddle.w\n"),
        # Your own held-key set, kept the right way.
        ("from canvas import ctx, WIDTH, HEIGHT, on_frame, keys\n",
         "from canvas import ctx, WIDTH, HEIGHT, on_frame, on_key_down, on_key_up\n\n"
         "keys = set()\non_key_down(keys.add)\non_key_up(keys.discard)\n"),
    ],
    "pybo-03-mouse": [
        ("paddle.x = mouse.x - paddle.w / 2", "paddle.x = mouse.x - paddle.w // 2"),
        # Mouse first, keys after.
        [(_MOUSE, ""), ("    if 'ArrowLeft' in keys:\n", _MOUSE + "    if 'ArrowLeft' in keys:\n")],
    ],
    "pybo-04-ball": [
        ("math.tau", "2 * math.pi"),
        (_MOVE_BALL, "    ball.x, ball.y = ball.x + ball.vx * dt, ball.y + ball.vy * dt\n"),
    ],
    "pybo-05-walls": [
        # -abs() says the same as copysign.
        [("math.copysign(ball.vx, 1)", "abs(ball.vx)"), ("math.copysign(ball.vx, -1)", "-abs(ball.vx)"),
         ("math.copysign(ball.vy, 1)", "abs(ball.vy)"), ("math.copysign(ball.vy, -1)", "-abs(ball.vy)")],
        # Flip, once the ball is back on the edge.
        [("ball.vx = math.copysign(ball.vx, 1)", "ball.vx = -ball.vx"),
         ("ball.vx = math.copysign(ball.vx, -1)", "ball.vx = -ball.vx"),
         ("ball.vy = math.copysign(ball.vy, 1)", "ball.vy = -ball.vy"),
         ("ball.vy = math.copysign(ball.vy, -1)", "ball.vy = -ball.vy")],
    ],
    "pybo-06-paddle-bounce": [
        # Squares instead of hypot.
        (_NEAREST.splitlines(True)[2],
         "    dx, dy = c.x - nearest_x, c.y - nearest_y\n    return dx * dx + dy * dy < c.r * c.r\n"),
        ("math.radians(60)", "math.pi / 3"),
        # Another formula for the same rule: a sideways share of the speed, the rest goes up.
        ("        angle = max(-1, min(1, offset)) * math.radians(60)\n" + _AIM,
         "        k = max(-1, min(1, offset)) * 0.866\n        ball.vx = speed * k\n"
         "        ball.vy = -math.sqrt(speed ** 2 - ball.vx ** 2)\n"),
        # No clamp on the offset (the ball can only touch the paddle's ends, so it never goes far past 1).
        ("max(-1, min(1, offset))", "offset"),
    ],
    "pybo-07-bricks": [
        # Two plain loops and append.
        (_BRICKS,
         "bricks = []\nfor row, color in enumerate(ROW_COLORS):\n    for col in range(8):\n"
         "        bricks.append(Brick(16 + col * 56, 30 + row * 22, 50, 16, color))\n"),
        # A comprehension with the rows in range().
        (_BRICKS,
         "bricks = [\n    Brick(16 + col * 56, 30 + row * 22, 50, 16, ROW_COLORS[row])\n"
         "    for row in range(5)\n    for col in range(8)\n]\n"),
    ],
    "pybo-08-break": [
        # Change the list in place: no `global bricks` needed.
        [("    global bricks, score\n", "    global score\n"),
         ("        bricks = [b for b in bricks if b not in hit]\n", "        bricks[:] = [b for b in bricks if b not in hit]\n")],
        # remove() is fine in a loop over a COPY of the list.
        (_BREAK,
         "    hit = False\n    for b in bricks[:]:\n        if hits_rect(ball, b):\n            bricks.remove(b)\n"
         "            score += 10\n            hit = True\n    if hit:\n        ball.vy = -ball.vy\n"),
        # any() as the yes-or-no, then the list.
        ("    if hit:\n", "    if any(hits_rect(ball, b) for b in bricks):\n"),
        ("        score += 10 * len(hit)\n", "        score = score + 10 * len(hit)\n"),
    ],
    "pybo-09-lives": [
        ("    ball.x, ball.y = 240, 200\n    ball.vx, ball.vy = 180, -180\n",
         "    ball.x = 240\n    ball.y = 200\n    ball.vx = 180\n    ball.vy = -180\n"),
        ("        lives -= 1\n", "        lives = lives - 1\n"),
    ],
    "pybo-10-win-over": [
        ("    if not bricks:\n", "    if len(bricks) == 0:\n"),
        ("    if not bricks:\n", "    if bricks == []:\n"),
        ("if lives == 0:", "if lives <= 0:"),
        # if / elif for the messages.
        (_MESSAGES_DRAW,
         "    if state == 'over':\n        ctx.font = '32px monospace'\n        ctx.fill_text('Game over', 150, 200)\n"
         "    elif state == 'won':\n        ctx.font = '32px monospace'\n        ctx.fill_text('You win!', 150, 200)\n"),
    ],
    "pybo-11-restart": [
        # Change the list in place.
        [("    global bricks, score, lives, state\n", "    global score, lives, state\n"),
         ("    bricks = make_bricks()\n", "    bricks[:] = make_bricks()\n")],
        # if / elif for the keys.
        ("    if key == 'Enter' and state != 'playing':\n        restart()\n",
         "    if state == 'playing':\n        return\n    if key == 'Enter':\n        restart()\n"),
        # A function that builds its list afresh by loops.
        (_MAKE,
         "def make_bricks():\n    grid = []\n    for row, color in enumerate(ROW_COLORS):\n        for col in range(8):\n"
         "            grid.append(Brick(16 + col * 56, 30 + row * 22, 50, 16, color))\n    return grid\n"),
    ],
}


def _as_dicts(code: str) -> str:
    """The same program with paddle, ball and bricks dicts, not dataclasses: ball['x'] for ball.x."""

    def factory(m: re.Match[str]) -> str:
        fields = re.findall(r"^    (\w+): \w+(?: = (.+))?$", m.group(2), re.M)
        params = ", ".join(f"{name}={default}" if default else name for name, default in fields)
        body = ", ".join(f"'{name}': {name}" for name, _ in fields)
        return f"def {m.group(1)}({params}):\n    return {{{body}}}\n"

    made = re.sub(r"@dataclass\nclass (\w+):\n((?:    .+\n?)+)", factory, code)
    made = made.replace("from dataclasses import dataclass\n", "")
    made = re.sub(r"\b(ball|paddle|b|c|r)\.(x|y|w|h|r|vx|vy|speed|color)\b", r"\1['\2']", made)
    assert made != code and "@dataclass" not in made
    return made


class TestShape:
    def test_ids_unique_numbered_and_titled(self) -> None:
        ids = [s.id for s in STEPS]
        assert len(ids) == len(set(ids))
        assert len(STEPS) == 12
        for n, s in enumerate(STEPS, 1):
            assert re.fullmatch(rf"pybo-{n:02d}-[a-z-]+", s.id), s.id
            assert s.title
            assert len(s.teaches) > 120, s.id
            assert s.goal.endswith("."), s.id

    def test_they_are_python_steps_on_their_own_track(self) -> None:
        assert {s.track for s in STEPS} == {"Breakout (Python)"}
        assert {s.language for s in STEPS} == {"python"}
        assert all(s.kind == "canvas" for s in STEPS)

    @pytest.mark.skipif(not _REGISTERED, reason="PYBREAKOUT_STEPS is not in canvas/__init__.py STEPS yet")
    def test_they_are_registered_after_the_other_python_tracks(self) -> None:
        ids = [s.id for s in ALL_STEPS]
        first = ids.index(STEPS[0].id)
        assert ids[first:first + len(STEPS)] == [s.id for s in STEPS]
        order = [s.track for s in ALL_STEPS]
        assert order.index("Dodge (Python)") < order.index("Breakout (Python)")
        assert order.index("To-do") < order.index("Breakout (Python)")

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
            "pybo-01-paddle": ["paddle", "Paddle"],
            "pybo-02-keys": ["move_paddle", "paddle.speed"],
            "pybo-03-mouse": ["last_mouse_x", "mouse.x"],
            "pybo-04-ball": ["ball", "Ball"],
            "pybo-05-walls": ["bounce_off_walls"],
            "pybo-06-paddle-bounce": ["hits_rect", "bounce_off_paddle"],
            "pybo-07-bricks": ["bricks", "Brick"],
            "pybo-08-break": ["score", "bricks", "break_bricks"],
            "pybo-09-lives": ["lives", "serve"],
            "pybo-10-win-over": ["state", "'won'", "'over'"],
            "pybo-11-restart": ["restart", "make_bricks", "state"],
        }
        for step_id, wanted in names.items():
            for name in wanted:
                assert name in BY_ID[step_id].goal, f"{step_id}: the goal does not say {name}"

    def test_the_python_way_is_what_gets_taught(self) -> None:
        text = " ".join(s.teaches for s in STEPS)
        for word in ("@dataclass", "default_factory", "list comprehension", "enumerate", "math.hypot",
                     "math.copysign", "math.sin", "math.cos", "max(", "min(", "any(", "not bricks", "global",
                     "UnboundLocalError", "f-string", "unpacking", "bricks[:]", "[Brick(16, 30, 50, 16)] * 40",
                     "def f(seen=[])", "math.tau", "mouse.x", "ValueError"):
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
            got = run_py_check(_as_dicts(s.solution), s.check)
            assert got.passed, f"{s.id}: {got.message}"

    def test_dict_mistakes_fail_too(self) -> None:
        # The dict form of a few mistakes that hang on a field's name: the check reads both forms alike.
        for step_id, entry in (
            ("pybo-06-paddle-bounce", (_AIM, "        ball.vy = -abs(ball.vy)\n")),
            ("pybo-08-break", ("        bricks = [b for b in bricks if b not in hit]\n", "        bricks.pop()\n")),
            ("pybo-07-bricks", (_BRICKS, "bricks = [Brick(16, 30, 50, 16)] * 40\n")),
        ):
            s = BY_ID[step_id]
            got = run_py_check(_as_dicts(_swaps(s.solution, entry)), s.check)
            assert not got.passed, step_id

    def test_the_checks_say_what_to_fix_not_just_that_it_failed(self) -> None:
        keys = BY_ID["pybo-02-keys"]
        got = run_py_check(_swap(keys.solution, "paddle.speed * dt", "paddle.speed / 60"), keys.check)
        assert "30 frames a second" in got.message

        mouse = BY_ID["pybo-03-mouse"]
        got = run_py_check(_swap(mouse.solution, "    global last_mouse_x\n", ""), mouse.check)
        assert "UnboundLocalError" in got.message and "line" in got.message
        got = run_py_check(_swap(mouse.solution, _MOUSE, "    paddle.x = mouse.x - paddle.w / 2\n"), mouse.check)
        assert "mouse.x" in got.message

        walls = BY_ID["pybo-05-walls"]
        got = run_py_check(_swap(walls.solution, _RIGHT_WALL, "    if ball.x + ball.r > WIDTH:\n        ball.vx = -ball.vx\n"),
                           walls.check)
        assert "partly through a wall" in got.message

        paddle = BY_ID["pybo-06-paddle-bounce"]
        got = run_py_check(_swap(paddle.solution, _AIM, "        ball.vy = -abs(ball.vy)\n"), paddle.check)
        assert "well to the left" in got.message
        got = run_py_check(_swap(paddle.solution, "        ball.y = paddle.y - ball.r\n", ""), paddle.check)
        assert "ball.y = paddle.y - ball.r" in got.message

        bricks = BY_ID["pybo-07-bricks"]
        got = run_py_check(_swap(bricks.solution, _BRICKS, "bricks = [Brick(16, 30, 50, 16)] * 40\n"), bricks.check)
        assert "forty times" in got.message

        brk = BY_ID["pybo-08-break"]
        got = run_py_check(_swap(brk.solution, _BREAK,
                                 "    hit = False\n    for b in bricks:\n        if hits_rect(ball, b):\n"
                                 "            bricks.remove(b)\n            score += 10\n            hit = True\n"
                                 "    if hit:\n        ball.vy = -ball.vy\n"), brk.check)
        assert "skipped" in got.message
        got = run_py_check(_swap(brk.solution, "    global bricks, score\n", "    global score\n"), brk.check)
        assert "UnboundLocalError" in got.message and "line" in got.message

        lives = BY_ID["pybo-09-lives"]
        got = run_py_check(_swap(lives.solution, "        serve()\n", ""), lives.check)
        assert "every frame" in got.message

        win = BY_ID["pybo-10-win-over"]
        got = run_py_check(_swap(win.solution, "    if not bricks:\n", "    if any(bricks):\n"), win.check)
        assert "not bricks" in got.message

        restart = BY_ID["pybo-11-restart"]
        got = run_py_check(_swap(restart.solution, "    global bricks, score, lives, state\n",
                                 "    global bricks, score, lives\n"), restart.check)
        assert "global state" in got.message

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

    @pytest.mark.skipif(not _REGISTERED, reason="PYBREAKOUT_STEPS is not in canvas/__init__.py STEPS yet")
    def test_the_open_step_always_passes(self) -> None:
        got = check_step(STEPS[-1].id, "")
        assert got is not None and got.passed

    @pytest.mark.skipif(not _REGISTERED, reason="PYBREAKOUT_STEPS is not in canvas/__init__.py STEPS yet")
    def test_check_step_runs_a_python_step_through_the_python_harness(self) -> None:
        s = STEPS[3]
        assert check_step(s.id, s.solution).passed
        assert not check_step(s.id, s.starter).passed
