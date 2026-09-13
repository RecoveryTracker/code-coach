"""The run ceiling, and the two ways changing it could go wrong.

The suite raises the timeout for its own runs, because three seconds is
right for a person waiting at a screen and wrong for a machine starting
thousands of processes back to back. Twice in hour-long runs a program
that finishes in a third of a second was reported as a possible infinite
loop, and a suite that fails at random is one you stop believing.

Raising it could go wrong in two directions and this file watches both.

It must not leak into the app. If the student-facing ceiling quietly
became fifteen seconds, a `while True` would lock the screen for fifteen
seconds and nothing would say so - the change would be invisible until
someone hit it.

And it must not disable the guard. A ceiling that is never reached is
the same as no ceiling, so the killer itself is tested directly: a real
infinite loop still has to die.
"""

from __future__ import annotations

import time
import unittest

from code_coach.engine import (
    DART_TIMEOUT_SECONDS,
    RUN_TIMEOUT_SECONDS,
    TIMEOUT_ENV,
    default_timeout,
    run_code,
)


class CeilingTests(unittest.TestCase):
    """What each caller gets, with and without the override."""

    def setUp(self) -> None:
        import os

        self.env = os.environ
        self.previous = self.env.get(TIMEOUT_ENV)

    def tearDown(self) -> None:
        if self.previous is None:
            self.env.pop(TIMEOUT_ENV, None)
        else:
            self.env[TIMEOUT_ENV] = self.previous

    def test_the_app_still_gives_a_student_three_seconds(self) -> None:
        """The one that stops this being a quiet change to the app.

        With nothing set - which is how the server runs - the ceiling is
        what it always was. If this ever reads fifteen, someone has made
        the screen hang five times longer on a runaway loop and the only
        notice anybody gets is this test.
        """
        self.env.pop(TIMEOUT_ENV, None)
        self.assertEqual(default_timeout(), 3.0)
        self.assertEqual(default_timeout(), RUN_TIMEOUT_SECONDS)

    def test_the_suite_is_running_with_room(self) -> None:
        """And the fixture that grants it is actually in effect. Without
        this, the whole arrangement could be switched off by a rename
        and the flake would simply come back."""
        self.assertGreaterEqual(default_timeout(), 15.0)

    def test_a_slow_language_keeps_its_own_larger_ceiling(self) -> None:
        """Dart compiles before it runs and that cost is nothing to do
        with the student's loop. The override must not shrink it."""
        self.env[TIMEOUT_ENV] = "15"
        self.assertEqual(default_timeout("dart"), DART_TIMEOUT_SECONDS)
        self.assertGreater(DART_TIMEOUT_SECONDS, 15.0)

    def test_the_override_can_only_raise(self) -> None:
        """It exists to stop false timeouts. A value below the floor
        would manufacture them instead, which is the exact failure it
        was added to end, so it is refused rather than honoured."""
        self.env[TIMEOUT_ENV] = "0.1"
        self.assertEqual(default_timeout(), RUN_TIMEOUT_SECONDS)

    def test_nonsense_is_ignored_rather_than_fatal(self) -> None:
        """A typo in an environment variable should not stop the app
        running student code."""
        for bad in ("", "   ", "soon", "3s", "-1"):
            with self.subTest(value=bad):
                self.env[TIMEOUT_ENV] = bad
                self.assertGreaterEqual(default_timeout(), RUN_TIMEOUT_SECONDS)


class GuardTests(unittest.TestCase):
    """The ceiling still has to be a ceiling.

    These pass an explicit timeout rather than leaning on the default,
    so they take a second rather than fifteen. What they establish is
    that the killer works at whatever number it is handed - and the
    tests above establish what number each caller hands it.
    """

    def test_an_infinite_loop_is_killed(self) -> None:
        started = time.time()
        out, err, code = run_code("while True:\n    pass", timeout=1.0)
        took = time.time() - started
        self.assertEqual(code, 124)
        self.assertIn("timed out", err)
        # Killed near its ceiling rather than merely eventually.
        self.assertLess(took, 10.0, f"took {took:.1f}s to kill a 1s ceiling")

    def test_a_loop_that_prints_forever_is_killed_too(self) -> None:
        """The output cap and the clock are separate guards and a
        runaway print exercises both. This one used to be the way to
        hang the old runner: it never blocks, so it never looks stuck."""
        out, err, code = run_code(
            "while True:\n    print('x')", timeout=1.0)
        self.assertEqual(code, 124)
        self.assertLess(len(out), 200_000)

    def test_an_ordinary_program_is_not_killed(self) -> None:
        """The other half. A guard that fails everything is not a guard,
        and this is the shape of the false positive the whole change is
        about - a short program under a short ceiling."""
        out, err, code = run_code("print(sum(range(1000)))", timeout=1.0)
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), "499500")


if __name__ == "__main__":
    unittest.main()
