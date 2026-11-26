"""The Python crashes, held to the rules every crash keeps.

The load-bearing test is `test_the_engine_says_exactly_this`: the message
and line each crash records are what Python 3 printed, read through
`engine_report`, which takes the message from the bottom of the traceback
and the line from its last frame (inside the function, not at the call).

The Errors screen shows only the crashes in the language picked at the top
(web/src/components/Errors.tsx), so these are what a Python learner sees.
"""

from __future__ import annotations

import functools
import unittest

from code_coach.engine import run_code
from code_coach.errors import crash, crashes, engine_report
from code_coach.errors.content_python import PY_CRASHES as FIRST
from code_coach.errors.content_python2 import PY_CRASHES_2

#: Both Python sets: the family "Python" holds them together.
PY_CRASHES = FIRST + PY_CRASHES_2


@functools.lru_cache(maxsize=None)
def _run(code: str) -> tuple[str, str, int]:
    return run_code(code, language="python")


class ShapeTests(unittest.TestCase):
    def test_they_are_one_python_family(self) -> None:
        self.assertGreaterEqual(len(PY_CRASHES), 12)
        for c in PY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertEqual(c.family, "Python")
                self.assertEqual(c.language, "python")
                self.assertTrue(c.id.startswith("err-py-"))

    def test_they_are_registered(self) -> None:
        for c in PY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertIs(crash(c.id), c)
        ids = [c.id for c in crashes()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_message_repeats(self) -> None:
        messages = [c.message for c in PY_CRASHES]
        self.assertEqual(len(messages), len(set(messages)))

    def test_they_are_short_enough_to_hold_in_your_head(self) -> None:
        for c in PY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertLessEqual(len(c.numbered), 10)
                self.assertGreaterEqual(len(c.numbered), 2)

    def test_the_ranking_was_done(self) -> None:
        for group in (FIRST, PY_CRASHES_2):
            levels = [c.level for c in group]
            self.assertEqual(levels, sorted(levels))
        levels = [c.level for c in PY_CRASHES]
        self.assertGreater(len(set(levels)), 2)
        for level in levels:
            self.assertIn(level, range(1, 6))

    def test_the_blamed_line_is_a_real_line(self) -> None:
        for c in PY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertGreaterEqual(c.line, 1)
                self.assertLessEqual(c.line, len(c.numbered))
                self.assertTrue(c.numbered[c.line - 1][1].strip())

    def test_the_message_is_the_bottom_line_alone(self) -> None:
        for c in PY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertNotIn("\n", c.message)
                self.assertNotIn('.py"', c.message)
                self.assertRegex(c.message, r"^\w+(Error|Exception): ")


class ParserTests(unittest.TestCase):
    TRACEBACK = (
        "Traceback (most recent call last):\n"
        '  File "C:\\Temp\\tmp1.py", line 5, in <module>\n'
        "    print(average([]))\n"
        '  File "C:\\Temp\\tmp1.py", line 2, in average\n'
        "    return sum(numbers) / len(numbers)\n"
        "           ~~~~~~~~~~~~~^~~~~~~~~~~~~~\n"
        "ZeroDivisionError: division by zero\n"
    )

    def test_it_reads_from_the_bottom(self) -> None:
        from unittest import mock

        with mock.patch("code_coach.engine.run_code", return_value=("", self.TRACEBACK, 1)):
            self.assertEqual(engine_report("x", "python"), ("ZeroDivisionError: division by zero", 2))

    def test_a_program_that_works_reports_nothing(self) -> None:
        self.assertEqual(engine_report("print(1)", "python"), ("", 0))


class EngineTests(unittest.TestCase):
    def test_the_engine_says_exactly_this(self) -> None:
        for c in PY_CRASHES:
            with self.subTest(crash=c.id):
                message, line = engine_report(c.code, "python")
                self.assertEqual(message, c.message)
                self.assertEqual(line, c.line)

    def test_every_one_actually_crashes_and_is_not_a_typo_of_python(self) -> None:
        for c in PY_CRASHES:
            with self.subTest(crash=c.id):
                _out, err, exit_code = _run(c.code)
                self.assertNotEqual(exit_code, 0)
                self.assertNotIn("SyntaxError", err)
                self.assertNotIn("IndentationError", err)


class ChoiceTests(unittest.TestCase):
    def test_the_choices_are_fair(self) -> None:
        for c in PY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertGreaterEqual(len(c.choices), 4)
                self.assertIn(c.meaning, c.choices)
                self.assertNotIn(c.meaning, c.decoys)
                self.assertEqual(len(set(c.decoys)), len(c.decoys))
                self.assertEqual(list(c.choices), sorted(c.choices))
                self.assertGreater(len(c.fix), 120)

    def test_length_gives_nothing_away(self) -> None:
        """Neither always the longest nor never: either is a tell."""
        longest = sum(len(c.meaning) > max(len(d) for d in c.decoys) for c in PY_CRASHES)
        self.assertLessEqual(longest, len(PY_CRASHES) // 2)
        self.assertGreater(longest, 0)


class RouteTests(unittest.TestCase):
    def _check(self, crash_id: str, line: int, meaning: str):
        from code_coach.api import server
        from code_coach.api.schemas import ErrorCheckRequest

        return server.error_check(ErrorCheckRequest(crash_id=crash_id, line=line, meaning=meaning))

    def test_they_are_served_as_python_without_the_answers(self) -> None:
        from code_coach.api import server

        family = next(f for f in server.error_list()["families"] if f["name"] == "Python")
        self.assertEqual({r["id"] for r in family["crashes"]}, {c.id for c in PY_CRASHES})
        for row in family["crashes"]:
            with self.subTest(crash=row["id"]):
                self.assertEqual(row["language"], "python")
                for hidden in ("line", "meaning", "fix"):
                    self.assertNotIn(hidden, row)

    def test_right_wrong_line_and_wrong_reading(self) -> None:
        for c in PY_CRASHES:
            with self.subTest(crash=c.id):
                self.assertTrue(self._check(c.id, c.line, c.meaning).passed)
                other = 1 if c.line != 1 else 2
                wrong_line = self._check(c.id, other, c.meaning)
                self.assertFalse(wrong_line.passed)
                self.assertFalse(wrong_line.line_right)
                wrong_reading = self._check(c.id, c.line, c.decoys[0])
                self.assertFalse(wrong_reading.passed)
                self.assertFalse(wrong_reading.meaning_right)


if __name__ == "__main__":
    unittest.main()
