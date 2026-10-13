"""Python Canvas: the harness itself, in a child process.

The library a Python program imports (`from canvas import ...`) and the two
ways it is run: a check plays the program by hand (run_py_check), and the
preview steps it a frame at a time over a line protocol (the session
registry behind /api/pycanvas). Both are held here to numbers worked out by
hand - 0.25 s a frame for 3 frames is 0.75 s - or by the stdlib in this
process (the seeded random numbers), never to what the harness printed.

Every test runs a real child process (`python -I -u`), so the file takes a
few seconds; the content tests are in test_canvas_pydodge.py.
"""

from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import time

import pytest

from code_coach.canvas import run_py_check
from code_coach.canvas.pyharness import session as pysession
from code_coach.canvas.pyharness.session import PyRegistry, Unknown


def play(code: str, check: str):
    return run_py_check(code, check)


def passes(code: str, check: str) -> None:
    got = play(code, check)
    assert got.passed, got.message


def pid_alive(pid: int) -> bool:
    try:
        import psutil

        return psutil.pid_exists(pid)
    except ImportError:  # pragma: no cover - psutil is not a dependency
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True).stdout
        return str(pid) in out


def gone(pid: int, within: float = 5.0) -> bool:
    deadline = time.time() + within
    while time.time() < deadline:
        if not pid_alive(pid):
            return True
        time.sleep(0.05)
    return not pid_alive(pid)


# ---------------------------------------------------------------- drawing


def test_ctx_calls_are_recorded_in_order_with_the_state_they_were_made_in() -> None:
    code = """
from canvas import ctx

ctx.fill_style = 'red'
ctx.stroke_style = 'blue'
ctx.line_width = 3
ctx.font = '16px monospace'
ctx.text_align = 'center'
ctx.text_baseline = 'top'
ctx.global_alpha = 0.5
ctx.fill_rect(1, 2, 3, 4)
ctx.fill_style = 'green'
ctx.arc(10, 20, 5, 0, 6.28)
ctx.fill_text('hi', 7, 8)
"""
    check = """
d = cc.drawn()
expect([c['name'] for c in d] == ['fill_rect', 'arc', 'fill_text'], d)
a, b, c = d
expect(a['args'] == [1, 2, 3, 4] and a['fill'] == 'red' and a['stroke'] == 'blue', a)
expect(b['args'] == [10, 20, 5, 0, 6.28, False] and b['fill'] == 'green' and b['stroke'] == 'blue', b)
expect(c['args'] == ['hi', 7, 8], c)
for call in d:
    expect(call['line_width'] == 3 and call['font'] == '16px monospace', call)
    expect(call['text_align'] == 'center' and call['text_baseline'] == 'top' and call['alpha'] == 0.5, call)
"""
    passes(code, check)


def test_a_fresh_context_has_the_browsers_defaults() -> None:
    code = "from canvas import ctx\nctx.fill_rect(0, 0, 1, 1)\n"
    check = """
c = cc.drawn()[0]
expect(c['fill'] == '#000000' and c['stroke'] == '#000000', c)
expect(c['line_width'] == 1 and c['font'] == '10px sans-serif', c)
expect(c['text_align'] == 'start' and c['text_baseline'] == 'alphabetic' and c['alpha'] == 1, c)
expect(WIDTH == 480 and HEIGHT == 320, (WIDTH, HEIGHT))
"""
    passes(code, check)


def test_save_and_restore_bring_the_styles_back() -> None:
    code = """
from canvas import ctx

ctx.fill_style = 'red'
ctx.save()
ctx.fill_style = 'blue'
ctx.line_width = 9
ctx.fill_rect(0, 0, 1, 1)
ctx.restore()
ctx.fill_rect(0, 0, 2, 2)
ctx.restore()
"""
    check = """
d = cc.drawn()
expect([c['name'] for c in d] == ['save', 'fill_rect', 'restore', 'fill_rect', 'restore'], d)
expect(d[1]['fill'] == 'blue' and d[1]['line_width'] == 9, d[1])
expect(d[3]['fill'] == 'red' and d[3]['line_width'] == 1, d[3])
"""
    passes(code, check)


def test_rects_arcs_and_texts_read_what_was_drawn_this_frame_only() -> None:
    code = """
from canvas import ctx, on_frame

n = 0

def loop(dt):
    global n
    n += 1
    ctx.fill_style = 'tomato'
    ctx.fill_rect(n, 0, 10, 20)
    if n == 1:
        ctx.arc(5, 6, 7, 0, 1)
        ctx.fill_text('first', 0, 0)
    ctx.stroke_rect(99, 99, 9, 9)

on_frame(loop)
"""
    check = """
expect(cc.rects() == [], 'nothing before the first frame')
cc.frames(1)
expect(cc.rects() == [{'x': 1, 'y': 0, 'w': 10, 'h': 20, 'fill': 'tomato'}], cc.rects())
expect(cc.arcs() == [{'x': 5, 'y': 6, 'r': 7, 'fill': 'tomato'}], cc.arcs())
expect(cc.texts() == ['first'], cc.texts())
cc.frames(1)
expect(cc.rects() == [{'x': 2, 'y': 0, 'w': 10, 'h': 20, 'fill': 'tomato'}], cc.rects())
expect(cc.arcs() == [] and cc.texts() == [], 'the first frame\\'s drawing is not in the second')
"""
    passes(code, check)


def test_top_level_drawing_is_there_until_the_first_frame() -> None:
    code = "from canvas import ctx\nctx.fill_rect(5, 6, 7, 8)\n"
    passes(code, "expect(cc.rects()[0]['x'] == 5, cc.rects())\ncc.frames(1)\nexpect(cc.rects() == [], cc.rects())")


def test_a_call_with_a_non_finite_number_is_ignored_like_a_real_canvas() -> None:
    code = """
from canvas import ctx

ctx.fill_rect(float('nan'), 0, 1, 1)
ctx.fill_rect(0, float('inf'), 1, 1)
ctx.fill_rect(1, 2, 3, 4)
"""
    passes(code, "expect(cc.rects() == [{'x': 1, 'y': 2, 'w': 3, 'h': 4, 'fill': '#000000'}], cc.rects())")


def test_measure_text_estimates_six_tenths_of_the_font_size_a_character() -> None:
    code = """
from canvas import ctx

ctx.font = '20px monospace'
w = ctx.measure_text('abcde')
"""
    passes(code, "expect(near(g.w, 5 * 20 * 0.6, 1e-9), g.w)")


def test_a_camel_case_name_is_told_its_snake_case_one() -> None:
    got = play("from canvas import ctx\nctx.fillStyle = 'red'\n", "pass")
    assert not got.passed
    assert "on line 2" in got.message
    assert "ctx.fill_style" in got.message
    got = play("from canvas import ctx\nctx.fillRect(0, 0, 1, 1)\n", "pass")
    assert "ctx.fill_rect" in got.message


def test_wrong_kinds_of_argument_are_errors_that_name_the_argument() -> None:
    got = play("from canvas import ctx\n\nctx.fill_rect(10, 'tall', 5, 5)\n", "pass")
    assert not got.passed
    assert "line 3" in got.message and "fill_rect" in got.message and "y is 'tall'" in got.message
    got = play("from canvas import ctx\nctx.fill_style = 12\n", "pass")
    assert "fill_style must be text" in got.message
    got = play("from canvas import ctx\nctx.global_alpha = 2\n", "pass")
    assert "between 0" in got.message


# ------------------------------------------------------------------ time


def test_frames_advance_dt_exactly() -> None:
    code = """
from canvas import on_frame, now

dts = []
seen = []

def loop(dt):
    dts.append(dt)
    seen.append(now())

on_frame(loop)
"""
    check = """
cc.frames(3, 0.25)
expect(g.dts == [0.25, 0.25, 0.25], g.dts)
expect(g.seen == [0.25, 0.5, 0.75], g.seen)
expect(cc.time == 0.75, cc.time)
cc.frames(2, 0.5)
expect(cc.time == 1.75 and g.dts[-2:] == [0.5, 0.5], (cc.time, g.dts))
"""
    passes(code, check)


def test_the_default_frame_is_a_sixtieth_of_a_second() -> None:
    code = "from canvas import on_frame\ndts = []\non_frame(dts.append)\n"
    check = """
cc.frames(60)
expect(len(g.dts) == 60 and all(d == 1 / 60 for d in g.dts), g.dts[:3])
expect(near(cc.time, 1.0, 1e-9), cc.time)
"""
    passes(code, check)


def test_on_frame_functions_run_in_the_order_they_were_registered_and_work_as_a_decorator() -> None:
    code = """
from canvas import on_frame

order = []

@on_frame
def first(dt):
    order.append('first')

@on_frame
def second(dt):
    order.append('second')
"""
    passes(code, "cc.frames(2)\nexpect(g.order == ['first', 'second', 'first', 'second'], g.order)")


def test_after_fires_on_the_frame_its_game_time_arrives() -> None:
    code = """
from canvas import after

fired = []
after(0.5, lambda: fired.append('half'))
after(1.0, lambda: fired.append('one'))
"""
    check = """
cc.frames(29)
expect(g.fired == [], g.fired)
cc.frames(1)
expect(g.fired == ['half'], g.fired)
cc.frames(29)
expect(g.fired == ['half'], g.fired)
cc.frames(1)
expect(g.fired == ['half', 'one'], g.fired)
cc.frames(120)
expect(g.fired == ['half', 'one'], 'after() fires once')
"""
    passes(code, check)


def test_every_repeats_and_cancel_stops_it() -> None:
    code = """
from canvas import every, cancel

count = 0
other = 0

def tick():
    global count
    count += 1

def tock():
    global other
    other += 1

tid = every(0.25, tick)
every(0.5, tock)
"""
    check = """
cc.frames(60)
expect(g.count == 4 and g.other == 2, (g.count, g.other))
import canvas
canvas.cancel(g.tid)
cc.frames(60)
expect(g.count == 4 and g.other == 4, (g.count, g.other))
"""
    passes(code, check)


def test_a_timer_is_on_game_time_not_the_wall_clock() -> None:
    # One long frame passes a timer; many short ones inside it do not.
    code = "from canvas import after\nhits = []\nafter(5, lambda: hits.append(1))\n"
    check = """
cc.frames(1, 4.9)
expect(g.hits == [], g.hits)
cc.frames(1, 0.1)
expect(g.hits == [1], g.hits)
"""
    passes(code, check)


def test_a_timer_made_inside_a_frame_counts_from_then() -> None:
    code = """
from canvas import on_frame, after, now

log = []
started = []

def loop(dt):
    if not started:
        started.append(now())
        after(0.5, lambda: log.append(now()))

on_frame(loop)
"""
    check = """
cc.frames(40, 0.0625)
expect(g.started == [0.0625], g.started)
expect(g.log == [0.5625], g.log)
"""
    passes(code, check)


def test_bad_timers_are_errors() -> None:
    got = play("from canvas import after\nafter(1, print())\n", "pass")
    assert "after() needs a function" in got.message
    got = play("from canvas import every\nevery(0, print)\n", "pass")
    assert "more than 0" in got.message
    got = play("from canvas import on_frame\non_frame(print())\n", "pass")
    assert "pass the function itself" in got.message


# ----------------------------------------------------------------- input


def test_held_keys_and_key_events() -> None:
    code = """
from canvas import keys, on_key_down, on_key_up

downs = []
ups = []
on_key_down(downs.append)
on_key_up(ups.append)
"""
    check = """
import canvas
expect(len(canvas.keys) == 0, canvas.keys)
cc.press('ArrowLeft')
cc.press('A')
expect(canvas.keys == {'ArrowLeft', 'a'}, canvas.keys)
expect(g.downs == ['ArrowLeft', 'a'], g.downs)
cc.release('ArrowLeft')
expect(canvas.keys == {'a'} and g.ups == ['ArrowLeft'], (canvas.keys, g.ups))
cc.release('a')
expect(not canvas.keys, canvas.keys)
"""
    passes(code, check)


def test_the_keys_a_frame_sees_are_the_ones_held_at_that_frame() -> None:
    code = """
from canvas import keys, on_frame

log = []
on_frame(lambda dt: log.append(sorted(keys)))
"""
    check = """
cc.frames(1)
cc.press(' ')
cc.frames(2)
cc.press('Enter')
cc.frames(1)
cc.release(' ')
cc.release('Enter')
cc.frames(1)
expect(g.log == [[], [' '], [' '], [' ', 'Enter'], []], g.log)
"""
    passes(code, check)


def test_click_and_pointer_are_canvas_pixels() -> None:
    code = """
from canvas import mouse, on_click

clicks = []
on_click(lambda x, y: clicks.append((x, y, mouse.x, mouse.y)))
"""
    check = """
import canvas
expect((canvas.mouse.x, canvas.mouse.y) == (0, 0), canvas.mouse)
cc.pointer(30, 40)
expect((canvas.mouse.x, canvas.mouse.y) == (30, 40), canvas.mouse)
cc.click(123, 77)
expect(g.clicks == [(123, 77, 123, 77)], g.clicks)
"""
    passes(code, check)


# ---------------------------------------------------------------- random


def test_random_is_seeded_the_same_every_time() -> None:
    random.seed(20260926)
    first = [random.random() for _ in range(3)]
    ints = None
    random.seed(20260926)
    ints = [random.randint(0, 1000) for _ in range(3)]
    code = """
import random

xs = [random.random() for _ in range(3)]
"""
    check = f"expect(g.xs == {first!r}, g.xs)"
    passes(code, check)
    # ... and again: a run is not luck.
    passes(code, check)
    code2 = "import random\nxs = [random.randint(0, 1000) for _ in range(3)]\n"
    passes(code2, f"expect(g.xs == {ints!r}, g.xs)")


def test_another_seed_gives_other_numbers_and_the_seed_is_ours_to_set() -> None:
    code = "import random\nx = random.random()\n"
    random.seed(7)
    want = random.random()
    got = run_py_check(code, f"expect(g.x == {want!r}, g.x)", seed=7)
    assert got.passed, got.message
    got = run_py_check(code, f"expect(g.x == {want!r}, g.x)")
    assert not got.passed


def test_the_seed_in_the_driver_is_the_one_the_server_names() -> None:
    from pathlib import Path

    text = (Path(pysession.__file__).parent / "driver.py").read_text(encoding="utf-8")
    assert f"SEED = {pysession.SEED}" in text


# ---------------------------------------------------------------- errors


def test_a_crash_at_the_top_is_reported_with_the_learners_line() -> None:
    code = "from canvas import ctx\n\n\nx = 1\nprint(nope)\n"
    got = play(code, "pass")
    assert not got.passed
    assert got.message.startswith("Your code threw on line 5: NameError")
    assert "nope" in got.message


def test_a_crash_in_a_frame_is_reported_with_its_line() -> None:
    code = """from canvas import on_frame

n = 0

def loop(dt):
    global n
    n += 1
    if n == 3:
        1 / 0

on_frame(loop)
"""
    got = play(code, "cc.frames(2)\ncc.frames(5)")
    assert not got.passed
    assert got.message == "Your code threw on line 9: ZeroDivisionError: division by zero"


def test_a_crash_in_a_key_handler_and_a_timer_are_reported_too() -> None:
    got = play("from canvas import on_key_down\n\ndef h(key):\n    raise ValueError(key)\n\non_key_down(h)\n",
               "cc.press('x')")
    assert got.message == "Your code threw on line 4: ValueError: x"
    got = play("from canvas import after\n\ndef t():\n    {}['k']\n\nafter(0.1, t)\n", "cc.frames(10)")
    assert got.message == "Your code threw on line 4: KeyError: 'k'"


def test_a_syntax_error_is_reported_with_its_line() -> None:
    got = play("from canvas import ctx\n\nif True print(1)\n", "pass")
    assert not got.passed
    assert got.message.startswith("Your code threw on line 3: SyntaxError")


def test_an_error_in_the_library_points_at_the_learners_line() -> None:
    code = "from canvas import ctx\n\n\n\nctx.arc(1, 1, -5, 0, 1)\n"
    got = play(code, "pass")
    assert got.message.startswith("Your code threw on line 5: ValueError"), got.message


def test_exit_is_refused_and_input_does_not_hang() -> None:
    got = play("import sys\nsys.exit(0)\n", "pass")
    assert "called exit()" in got.message
    got = play("x = input('? ')\n", "pass")
    assert "input() cannot be used" in got.message and "line 1" in got.message


def test_an_endless_loop_is_reported_not_waited_on() -> None:
    started = time.time()
    got = play("from canvas import ctx\n\nwhile True:\n    pass\n", "pass")
    assert not got.passed
    assert "loop that never ends" in got.message
    assert time.time() - started < 8


def test_an_endless_loop_in_a_frame_is_reported_too() -> None:
    code = "from canvas import on_frame\n\ndef loop(dt):\n    while True:\n        pass\n\non_frame(loop)\n"
    started = time.time()
    got = play(code, "cc.frames(3)")
    assert not got.passed and "loop that never ends" in got.message
    assert time.time() - started < 8


def test_a_loop_that_swallows_the_stop_is_ended_anyway() -> None:
    code = """
while True:
    try:
        while True:
            pass
    except BaseException:
        pass
"""
    started = time.time()
    got = play(code, "pass")
    assert not got.passed and "loop that never ends" in got.message
    assert time.time() - started < 12


def test_an_endless_check_is_reported_by_the_parent() -> None:
    got = run_py_check("x = 1\n", "while True:\n    pass\n", timeout=3)
    assert not got.passed
    assert "check ran out of time" in got.message or "loop that never ends" in got.message


# ------------------------------------------------- the names, and the walls


def test_the_library_names_are_not_there_unless_you_import_them() -> None:
    got = play("ctx.fill_rect(0, 0, 1, 1)\n", "pass")
    assert got.message.startswith("Your code threw on line 1: NameError")
    assert "'ctx'" in got.message
    got = play("print(WIDTH)\n", "pass")
    assert "NameError" in got.message


def test_the_harness_is_not_importable_and_star_import_gives_only_the_library() -> None:
    got = play("import driver\n", "pass")
    assert "ModuleNotFoundError" in got.message
    got = play("import session\n", "pass")
    assert "ModuleNotFoundError" in got.message
    code = "from canvas import *\nnames = sorted(n for n in dir() if not n.startswith('_'))\n"
    want = sorted(["ctx", "WIDTH", "HEIGHT", "keys", "mouse", "random", "now", "on_frame", "on_key_down",
                   "on_key_up", "on_click", "after", "every", "cancel"])
    passes(code, f"expect(g.names == {want!r}, g.names)")


def test_the_check_runs_in_an_empty_folder_with_a_bare_environment() -> None:
    os.environ["CC_TEST_SECRET"] = "hunter2"
    try:
        check = """
import os
expect(os.listdir('.') == [], os.listdir('.'))
expect('CC_TEST_SECRET' not in os.environ, 'the server environment leaked in')
expect(set(k.upper() for k in os.environ) <= {'SYSTEMROOT', 'PYTHONIOENCODING', 'TEMP', 'TMP'}, sorted(os.environ))
"""
        passes("x = 1\n", check)
    finally:
        del os.environ["CC_TEST_SECRET"]


def test_print_is_caught_and_does_not_disturb_the_verdict() -> None:
    code = "print('hello')\nimport sys\nsys.stdout.write('{\"passed\": false}\\n')\nsys.stderr.write('oops\\n')\n"
    passes(code, "expect(True, '')")


def test_g_reads_and_sets_the_learners_own_names() -> None:
    code = """
from canvas import on_frame

player = {'x': 1}
enemies = [1, 2, 3]
seen = []

def loop(dt):
    seen.append(len(enemies))
    player['x'] += 1

on_frame(loop)
"""
    check = """
cc.frames(1)
expect(g.player['x'] == 2 and g.enemies == [1, 2, 3], g.player)
g.enemies = []
g.player['x'] = 100
cc.frames(1)
expect(g.seen == [3, 0], g.seen)
expect(g.player['x'] == 101, g.player)
expect('player' in g and 'nothing' not in g and not hasattr(g, 'nothing'), 'membership')
"""
    passes(code, check)


def test_a_name_the_program_never_made_fails_with_that_name() -> None:
    got = play("x = 1\n", "g.player['x']")
    assert not got.passed
    assert "`player`" in got.message


def test_expect_fails_with_its_message_and_a_broken_check_is_not_the_learners_fault() -> None:
    got = play("x = 1\n", "expect(g.x == 2, 'x should be 2, it is %d' % g.x)")
    assert (got.passed, got.message) == (False, "x should be 2, it is 1")
    got = play("x = 1\n", "\n\nundefined_thing()")
    assert not got.passed
    assert got.message.startswith("The check could not run: NameError") and "check line 3" in got.message


def test_near_is_numbers_within_a_distance() -> None:
    passes("x = 1\n", "expect(near(10, 12, 2) and not near(10, 12.5, 2) and not near('a', 1, 5) and not near(True, 1, 5), 'near')")


# ------------------------------------------------- the preview's sessions

CODE_COUNTER = """
from canvas import ctx, on_frame, keys, on_key_down, on_click, mouse, now

x = 0
log = []
ctx.fill_style = 'tomato'
ctx.fill_rect(100, 80, 40, 40)
print('started')

def loop(dt):
    global x
    x += 1
    ctx.fill_rect(x, 0, 1, 1)
    if 'ArrowRight' in keys:
        ctx.fill_text('right', x, 5)

def down(key):
    print('down', key)

def click(cx, cy):
    print('click', cx, cy, mouse.x, mouse.y)

on_frame(loop)
on_key_down(down)
on_click(click)
"""


@pytest.fixture()
def reg():
    registry = PyRegistry(step_seconds=0.6)
    yield registry
    registry.close_all()


def pid_of(registry: PyRegistry, session_id: str) -> int:
    return registry._sessions[session_id].pid


def test_start_runs_the_top_level_and_returns_what_it_drew_and_printed(reg) -> None:
    got = reg.start("s", CODE_COUNTER)
    assert got["session"] and got["error"] is None
    assert got["logs"] == ["started"]
    assert got["calls"] == [[
        "fill_rect", [100, 80, 40, 40], "tomato", "#000000",
        {"lineWidth": 1, "font": "10px sans-serif", "textAlign": "start",
         "textBaseline": "alphabetic", "globalAlpha": 1},
    ]]


def test_steps_run_frames_in_lockstep_and_return_every_frames_calls(reg) -> None:
    sid = reg.start("s", CODE_COUNTER)["session"]
    one = reg.step(sid)
    assert [c[1] for c in one["calls"]] == [[1, 0, 1, 1]]
    three = reg.step(sid, frames=3)
    assert [c[1] for c in three["calls"]] == [[2, 0, 1, 1], [3, 0, 1, 1], [4, 0, 1, 1]]
    assert one["error"] is None and three["logs"] == []


def test_dt_is_the_programs_dt(reg) -> None:
    code = "from canvas import on_frame, now, ctx\non_frame(lambda dt: ctx.fill_text(f'{dt} {now()}', 0, 0))\n"
    sid = reg.start("s", code)["session"]
    got = reg.step(sid, frames=2, dt=0.0625)
    assert [c[1][0] for c in got["calls"]] == ["0.0625 0.0625", "0.0625 0.125"]
    got = reg.step(sid)
    assert got["calls"][0][1][0] == f"{1 / 60} {0.125 + 1 / 60}"


def test_held_keys_events_and_clicks_reach_the_program(reg) -> None:
    sid = reg.start("s", CODE_COUNTER)["session"]
    got = reg.step(sid, keys=["ArrowRight"],
                   events=[{"type": "keydown", "key": "ArrowRight"}, {"type": "click", "x": 12.5, "y": 30}])
    assert got["logs"] == ["down ArrowRight", "click 12.5 30.0 12.5 30.0"]
    names = [c[0] for c in got["calls"]]
    assert names == ["fill_rect", "fill_text"]
    # The page says what is held: an empty list lets go of the key, whatever events came before.
    got = reg.step(sid, keys=[], events=[{"type": "keydown", "key": "ArrowRight"}])
    assert [c[0] for c in got["calls"]] == ["fill_rect"]


def test_the_keys_the_page_sends_are_the_whole_truth_each_step(reg) -> None:
    code = "from canvas import keys, on_frame, ctx\non_frame(lambda dt: ctx.fill_text(','.join(sorted(keys)), 0, 0))\n"
    sid = reg.start("s", code)["session"]
    assert reg.step(sid, keys=["b", "A"])["calls"][0][1][0] == "a,b"
    assert reg.step(sid, keys=["b"])["calls"][0][1][0] == "b"
    assert reg.step(sid, keys=[])["calls"][0][1][0] == ""


def test_mouse_moves_set_the_pointer(reg) -> None:
    code = "from canvas import mouse, on_frame, ctx\non_frame(lambda dt: ctx.fill_text(f'{mouse.x},{mouse.y}', 0, 0))\n"
    sid = reg.start("s", code)["session"]
    got = reg.step(sid, events=[{"type": "mousemove", "x": 3, "y": 4}, {"type": "mousemove", "x": 5.5, "y": 6}])
    assert got["calls"][0][1][0] == "5.5,6.0"


def test_a_reply_says_what_the_program_still_wants(reg) -> None:
    def wants(code: str):
        got = reg.start("s", code)
        return got["frames"], got["input"]

    assert wants("x = 1\n") == (False, False)  # nothing registered: the page can stop asking
    assert wants("from canvas import on_frame\non_frame(print)\n") == (True, False)
    assert wants("from canvas import on_click\non_click(print)\n") == (False, True)
    assert wants("from canvas import on_key_up\non_key_up(print)\n") == (False, True)
    assert wants("from canvas import every\nevery(1, print)\n") == (True, False)
    # A timer that has fired and is gone no longer wants frames.
    sid = reg.start("s", "from canvas import after\nafter(0.1, print)\n")["session"]
    assert reg.step(sid, frames=1, dt=0.05)["frames"] is True
    assert reg.step(sid, frames=2, dt=0.05)["frames"] is False


def test_two_sessions_do_not_share_anything(reg) -> None:
    a = reg.start("s", CODE_COUNTER)["session"]
    b = reg.start("s", CODE_COUNTER)["session"]
    reg.step(a, frames=5)
    assert [c[1] for c in reg.step(b)["calls"]] == [[1, 0, 1, 1]]
    assert pid_of(reg, a) != pid_of(reg, b)


def test_a_crash_in_a_step_is_reported_once_with_its_line_and_the_game_stops(reg) -> None:
    code = """from canvas import on_frame, ctx

n = 0

def loop(dt):
    global n
    n += 1
    ctx.fill_rect(n, 0, 1, 1)
    if n == 3:
        undefined_name

on_frame(loop)
"""
    sid = reg.start("s", code)["session"]
    pid = pid_of(reg, sid)
    assert reg.step(sid, frames=2)["error"] is None
    bad = reg.step(sid, frames=5)
    assert bad["error"]["line"] == 10 and "NameError" in bad["error"]["message"]
    assert [c[1] for c in bad["calls"]] == [[3, 0, 1, 1]]  # what it drew before it fell over
    again = reg.step(sid)
    assert again["calls"] == [] and again["error"] == bad["error"]
    assert gone(pid), "a finished program's process should not linger"


def test_a_program_that_cannot_start_has_no_session_and_its_process_is_gone(reg) -> None:
    got = reg.start("s", "from canvas import ctx\n\nctx.fill_rect(1, 2, 3)\n")
    assert got["session"] == ""
    assert got["error"]["line"] == 3 and "TypeError" in got["error"]["message"]
    assert len(reg) == 0
    got = reg.start("s", "x = (1,\n")
    assert got["session"] == "" and "SyntaxError" in got["error"]["message"] and got["error"]["line"] in (1, 2)


def test_an_endless_loop_at_the_top_is_reported_within_the_limit(reg) -> None:
    started = time.time()
    got = reg.start("s", "from canvas import ctx\nwhile True:\n    pass\n")
    assert got["session"] == ""
    assert "loop that never ends" in got["error"]["message"] and got["error"]["line"] in (2, 3)
    assert time.time() - started < 6


def test_an_endless_loop_in_a_frame_is_stopped_and_the_process_ends(reg) -> None:
    code = "from canvas import on_frame\n\ndef loop(dt):\n    while True:\n        pass\n\non_frame(loop)\n"
    sid = reg.start("s", code)["session"]
    pid = pid_of(reg, sid)
    started = time.time()
    got = reg.step(sid)
    assert "loop that never ends" in got["error"]["message"] and got["error"]["line"] in (4, 5)
    assert time.time() - started < 6
    assert gone(pid)


def test_a_blocking_sleep_is_ended_by_the_watchdogs_second_stage(reg) -> None:
    code = ("import time\nfrom canvas import on_frame\n\ndef loop(dt):\n"
            "    try:\n        time.sleep(60)\n    except BaseException:\n        time.sleep(60)\n\n"
            "on_frame(loop)\n")
    sid = reg.start("s", code)["session"]
    pid = pid_of(reg, sid)
    started = time.time()
    got = reg.step(sid)
    assert "loop that never ends" in got["error"]["message"]
    assert time.time() - started < 0.6 + 1.0 + 2.0  # its limit, the driver's grace, some slack
    assert gone(pid)


def test_the_parent_kills_a_child_that_stays_silent_too_long() -> None:
    session = pysession.PySession("x", "s", step_seconds=30)
    try:
        code = "import time\nfrom canvas import on_frame\non_frame(lambda dt: time.sleep(60))\n"
        assert session.start(code)["error"] is None
        pid = session.pid
        started = time.time()
        got = session.request({"op": "step", "frames": 1}, wait=0.5)
        assert "loop that never ends" in got["error"]["message"]
        assert time.time() - started < 5
        assert gone(pid)
    finally:
        session.close()


def test_print_and_stderr_come_back_as_logs_and_are_capped(reg) -> None:
    code = """import sys
from canvas import on_frame

def loop(dt):
    print('a', 1)
    sys.stderr.write('warn\\n')
    for i in range(500):
        print(i)

on_frame(loop)
"""
    sid = reg.start("s", code)["session"]
    logs = reg.step(sid)["logs"]
    assert logs[:2] == ["a 1", "warn"]
    assert len(logs) == 201 and logs[-1] == "... 302 more lines not shown"


def test_stop_ends_the_process_and_deletes_the_folder(reg) -> None:
    sid = reg.start("s", CODE_COUNTER)["session"]
    session = reg._sessions[sid]
    pid, folder = session.pid, session._dir
    assert pid_alive(pid) and folder.exists()
    reg.stop(sid)
    assert gone(pid) and not folder.exists()
    with pytest.raises(Unknown):
        reg.step(sid)
    with pytest.raises(Unknown):
        reg.stop(sid)


def test_the_session_runs_in_its_own_empty_folder_with_a_bare_environment(reg) -> None:
    os.environ["CC_TEST_SECRET"] = "hunter2"
    try:
        code = ("import os\nfrom canvas import ctx\n"
                "ctx.fill_text(repr((os.listdir('.'), 'CC_TEST_SECRET' in os.environ, os.getcwd())), 0, 0)\n")
        got = reg.start("s", code)
        listing, leaked, cwd = eval(got["calls"][0][1][0])  # noqa: S307 - our own repr, from our own child
        assert listing == [] and leaked is False
        assert os.path.basename(cwd) == "work"
        assert os.path.basename(os.path.dirname(cwd)).startswith("cc-pycanvas-")
    finally:
        del os.environ["CC_TEST_SECRET"]


def test_idle_sessions_are_reaped_on_an_injected_clock() -> None:
    now = [1000.0]
    registry = PyRegistry(idle_seconds=60, clock=lambda: now[0])
    try:
        quiet = registry.start("s", CODE_COUNTER)["session"]
        busy = registry.start("s", CODE_COUNTER)["session"]
        pids = [pid_of(registry, quiet), pid_of(registry, busy)]
        now[0] += 45
        registry.step(busy)  # used: its idle clock starts again
        now[0] += 30  # quiet: 75 s idle; busy: 30 s
        assert registry.reap() == [quiet]
        assert registry.ids() == [busy]
        assert gone(pids[0]) and pid_alive(pids[1])
        with pytest.raises(Unknown):
            registry.step(quiet)
        now[0] += 61
        with pytest.raises(Unknown):
            registry.step(busy)  # stepping reaps first: it was idle too long
        assert gone(pids[1])
        assert len(registry) == 0
    finally:
        registry.close_all()


def test_the_oldest_session_is_evicted_when_there_are_too_many() -> None:
    now = [0.0]
    registry = PyRegistry(max_sessions=2, clock=lambda: now[0])
    try:
        a = registry.start("s", CODE_COUNTER)["session"]
        now[0] += 1
        b = registry.start("s", CODE_COUNTER)["session"]
        now[0] += 1
        registry.step(a)  # a was used more recently than b
        now[0] += 1
        pid_a, pid_b = pid_of(registry, a), pid_of(registry, b)
        c = registry.start("s", CODE_COUNTER)["session"]
        assert sorted(registry.ids()) == sorted([a, c])
        assert gone(pid_b) and pid_alive(pid_a)
        with pytest.raises(Unknown):
            registry.step(b)
    finally:
        registry.close_all()


def test_close_all_leaves_no_process_behind() -> None:
    registry = PyRegistry()
    ids = [registry.start("s", CODE_COUNTER)["session"] for _ in range(3)]
    pids = [pid_of(registry, i) for i in ids]
    folders = [registry._sessions[i]._dir for i in ids]
    registry.close_all()
    assert all(gone(p) for p in pids)
    assert not any(f.exists() for f in folders)
    assert len(registry) == 0


def test_folders_a_killed_server_left_behind_are_swept_but_recent_ones_are_not() -> None:
    import tempfile
    from pathlib import Path

    root = Path(tempfile.gettempdir())
    old = Path(tempfile.mkdtemp(prefix="cc-pycanvas-"))
    fresh = Path(tempfile.mkdtemp(prefix="cc-pycanvas-"))
    other = Path(tempfile.mkdtemp(prefix="not-ours-"))
    try:
        two_hours_ago = time.time() - 7200
        os.utime(old, (two_hours_ago, two_hours_ago))
        os.utime(other, (two_hours_ago, two_hours_ago))
        swept = pysession.sweep_stale()
        assert old.name in swept and not old.exists()
        assert fresh.exists() and other.exists()
        assert all(name.startswith("cc-pycanvas-") for name in swept) and root.exists()
    finally:
        for folder in (old, fresh, other):
            pysession.remove_folder(folder)


def test_a_child_whose_server_is_gone_ends_by_itself() -> None:
    proc = subprocess.Popen(
        pysession.child_command("serve"), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        env=pysession.child_env(), creationflags=pysession.child_flags(),
    )
    proc.stdin.write((json.dumps({"op": "start", "code": "x = 1\n"}) + "\n").encode())
    proc.stdin.flush()
    assert proc.stdout.readline().startswith(b"\x1ePY")
    proc.stdin.close()  # what the child sees when the server dies
    assert proc.wait(timeout=10) == 0


def test_stray_output_cannot_pose_as_an_answer(reg) -> None:
    code = ("import os, sys\nfrom canvas import on_frame\n"
            "os.write(1, b'{\"calls\": [1], \"logs\": [], \"error\": null}\\n')\n"
            "on_frame(lambda dt: None)\n")
    got = reg.start("s", code)
    assert got["error"] is None and got["calls"] == []
    assert reg.step(got["session"])["calls"] == []


# ------------------------------------------------------------ the routes


@pytest.fixture()
def clean_registry():
    yield pysession.REGISTRY
    pysession.REGISTRY.close_all()


def test_routes_start_step_stop(clean_registry) -> None:
    from code_coach.api.schemas import PyCanvasEvent, PyCanvasStartRequest, PyCanvasStepRequest, PyCanvasStopRequest
    from code_coach.api.server import pycanvas_start, pycanvas_step, pycanvas_stop

    first = pycanvas_start(PyCanvasStartRequest(step_id="pydodge-04-loop", code=CODE_COUNTER))
    sid = first["session"]
    assert sid and first["calls"][0][0] == "fill_rect"
    got = pycanvas_step(PyCanvasStepRequest(
        session=sid, frames=2, dt=0.05, keys=["ArrowRight"],
        events=[PyCanvasEvent(type="click", x=1, y=2)]))
    assert got["error"] is None and got["logs"] == ["click 1.0 2.0 1.0 2.0"]
    assert [c[0] for c in got["calls"]] == ["fill_rect", "fill_text", "fill_rect", "fill_text"]
    assert pycanvas_stop(PyCanvasStopRequest(session=sid)) == {"ok": True}
    assert len(pysession.REGISTRY) == 0


def test_routes_say_404_for_a_session_that_is_not_there(clean_registry) -> None:
    from fastapi import HTTPException

    from code_coach.api.schemas import PyCanvasStepRequest, PyCanvasStopRequest
    from code_coach.api.server import pycanvas_step, pycanvas_stop

    with pytest.raises(HTTPException) as err:
        pycanvas_step(PyCanvasStepRequest(session="nope"))
    assert err.value.status_code == 404 and "Press Run" in err.value.detail
    with pytest.raises(HTTPException) as err:
        pycanvas_stop(PyCanvasStopRequest(session="nope"))
    assert err.value.status_code == 404


def test_start_refuses_an_unknown_step_and_a_javascript_one(clean_registry) -> None:
    from fastapi import HTTPException

    from code_coach.api.schemas import PyCanvasStartRequest
    from code_coach.api.server import pycanvas_start

    with pytest.raises(HTTPException) as err:
        pycanvas_start(PyCanvasStartRequest(step_id="no-such-step", code="x = 1"))
    assert err.value.status_code == 404
    with pytest.raises(HTTPException) as err:
        pycanvas_start(PyCanvasStartRequest(step_id="dodge-01-square", code="x = 1"))
    assert err.value.status_code == 400
    assert len(pysession.REGISTRY) == 0


def test_the_step_request_is_bounded() -> None:
    from pydantic import ValidationError

    from code_coach.api.schemas import PyCanvasStepRequest

    for bad in ({"frames": 0}, {"frames": 1000}, {"dt": 0}, {"dt": 5}, {"keys": ["a"] * 100},
                {"events": [{"type": "nonsense"}]}):
        with pytest.raises(ValidationError):
            PyCanvasStepRequest(session="x", **bad)
    PyCanvasStepRequest(session="x", frames=120, dt=0.1)


def test_the_list_names_each_steps_language() -> None:
    from code_coach.api.server import canvas_list

    steps = canvas_list()["steps"]
    by_id = {s["id"]: s["language"] for s in steps}
    assert by_id["dodge-01-square"] == "javascript"
    assert by_id["pydodge-01-square"] == "python"
    assert {s["language"] for s in steps} == {"javascript", "python"}


def test_check_goes_to_the_python_harness_for_a_python_step() -> None:
    from code_coach.api.schemas import CanvasCheckRequest
    from code_coach.api.server import canvas_check
    from code_coach.canvas import step

    first = step("pydodge-01-square")
    bad = canvas_check(CanvasCheckRequest(step_id=first.id, code=first.starter))
    assert bad.passed is False and "40 by 40" in bad.message
    good = canvas_check(CanvasCheckRequest(step_id=first.id, code=first.solution))
    assert good.passed is True


def test_sys_executable_is_what_runs_the_child() -> None:
    assert pysession.child_command("serve")[:4] == [sys.executable, "-I", "-u", "-X"]
