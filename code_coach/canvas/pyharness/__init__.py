"""Python Canvas: the learner's Python runs on the server, a frame at a time.

    lib/canvas.py   what a program imports: `from canvas import ctx, on_frame, keys ...`
    driver.py       the child process (python -I -u): `serve` for the preview, `check` for a check
    session.py      sessions and the registry behind /api/pycanvas (limits, idle reaping)
    check.py        run_py_check: play a step's Python check in a child process

Nothing in here imports driver.py or lib/canvas.py: they are for the child.
"""
