"""The second JavaScript crash set and the third JavaScript predict set.

The rules of test_errors.py / test_errors_dart2.py applied to
JS_CRASHES_2, and those of test_predict.py / test_predict_dart2.py
applied to JS_PUZZLES_3 — both imported directly, so these hold before
and after they are registered. The load-bearing checks run every
program: each crash's message and line are what Node reported through
`engine_report`, and each puzzle prints exactly its written answer.
"""

from __future__ import annotations

import contextlib
import functools
import unittest
from unittest import mock

import code_coach.errors as errors_module
import code_coach.kata.predict as predict_module
from code_coach.engine import run_code
from code_coach.errors import crash, crashes, engine_report
from code_coach.errors.content import MISSING, NAMES, WRONG_KIND
from code_coach.errors.content_js2 import JS_CRASHES_2
from code_coach.kata.predict import PUZZLES, language_of, predict_families
from code_coach.kata.predict_js import JS_PUZZLES
from code_coach.kata.predict_js2 import JS_PUZZLES_2
from code_coach.kata.predict_js3 import JS_PUZZLES_3

JS_FIRST = MISSING + NAMES + WRONG_KIND
JS_CRASH_FAMILIES = {c.family for c in JS_FIRST}
JS_PREDICT_FAMILIES = {p.family for p in JS_PUZZLES}


@functools.lru_cache(maxsize=None)
def _report(code: str) -> tuple[str, int]:
    return engine_report(code, "javascript")


@functools.lru_cache(maxsize=None)
def _run(code: str) -> tuple[str, str, int]:
    return run_code(code, language="javascript")


def _with_mine(base: tuple) -> tuple:
    have = {c.id for c in base}
    return (*base, *(c for c in JS_CRASHES_2 if c.id not in have))


@contextlib.contextmanager
def _registered():
    """crashes() and PUZZLES as they will be once both sets are
    registered."""
    real_crashes = crashes

    def with_mine(family: str | None = None):
        everything = _with_mine(real_crashes())
        if family is not None:
            everything = tuple(c for c in everything if c.family == family)
        return tuple(sorted(everything, key=lambda c: c.level))

    have = {p.id for p in PUZZLES}
    puzzles = (*PUZZLES, *(p for p in JS_PUZZLES_3 if p.id not in have))
    with mock.patch.object(errors_module, "crashes", with_mine), \
            mock.patch.object(predict_module, "PUZZLES", puzzles):
        yield


# ── Errors ──────────────────────────────────────────────────


class CrashShapeTests(unittest.TestCase):
    def test_there_are_six_all_javascript_in_existing_families(self) -> None:
        self.assertEqual(len(JS_CRASHES_2), 6)
        for c in JS_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertEqual(c.language, "javascript")
                self.assertIn(c.family, JS_CRASH_FAMILIES)

    def test_ids_are_unique_and_new(self) -> None:
        ids = [c.id for c in JS_CRASHES_2]
        self.assertEqual(len(ids), len(set(ids)))
        taken = {c.id for c in crashes() if c not in JS_CRASHES_2}
        self.assertFalse(taken & set(ids))

    def test_no_message_repeats_the_first_set(self) -> None:
        old = {c.message for c in JS_FIRST}
        for c in JS_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertNotIn(c.message, old)

    def test_they_are_short_enough_to_hold_in_your_head(self) -> None:
        for c in JS_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertLessEqual(len(c.numbered), 10)
                self.assertGreaterEqual(len(c.numbered), 2)

    def test_the_ranking_was_done(self) -> None:
        levels = [c.level for c in JS_CRASHES_2]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)
        for level in levels:
            self.assertIn(level, range(1, 6))

    def test_the_blamed_line_is_a_real_line(self) -> None:
        for c in JS_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertGreaterEqual(c.line, 1)
                self.assertLessEqual(c.line, len(c.numbered))

    def test_the_message_is_one_line(self) -> None:
        for c in JS_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertNotIn("\n", c.message)
                self.assertNotIn("    at ", c.message)


class CrashEngineTests(unittest.TestCase):
    def test_the_engine_says_exactly_this(self) -> None:
        for c in JS_CRASHES_2:
            with self.subTest(crash=c.id):
                message, line = _report(c.code)
                self.assertEqual(
                    message, c.message, f"{c.id}: node says {message!r}")
                self.assertEqual(
                    line, c.line, f"{c.id}: node blames line {line}")

    def test_every_one_actually_crashes(self) -> None:
        for c in JS_CRASHES_2:
            with self.subTest(crash=c.id):
                _out, _err, exit_code = _run(c.code)
                self.assertNotEqual(exit_code, 0, f"{c.id} does not crash")


class CrashChoiceTests(unittest.TestCase):
    def test_the_choices_are_fair(self) -> None:
        for c in JS_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertGreaterEqual(len(c.choices), 3)
                self.assertIn(c.meaning, c.choices)
                self.assertNotIn(c.meaning, c.decoys)
                self.assertEqual(len(set(c.decoys)), len(c.decoys))
                self.assertEqual(list(c.choices), sorted(c.choices))

    def test_the_answer_is_not_the_longest_one(self) -> None:
        def longest(pool):
            return [c for c in pool
                    if len(c.meaning) > max(len(d) for d in c.decoys)]

        mine = longest(JS_CRASHES_2)
        self.assertLessEqual(
            len(mine), len(JS_CRASHES_2) // 2,
            "the right reading is the longest option too often: "
            + ", ".join(c.id for c in mine))
        everything = _with_mine(crashes())
        self.assertLessEqual(len(longest(everything)), len(everything) // 2)

    def test_every_one_says_what_to_do(self) -> None:
        for c in JS_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertGreater(len(c.fix), 120)
                self.assertTrue(c.name.strip())


class CrashRouteTests(unittest.TestCase):
    def _check(self, crash_id: str, line: int, meaning: str):
        from code_coach.api import server
        from code_coach.api.schemas import ErrorCheckRequest

        return server.error_check(
            ErrorCheckRequest(crash_id=crash_id, line=line, meaning=meaning))

    def test_served_without_the_answer(self) -> None:
        from code_coach.api import server

        with _registered():
            served = server.error_list()
        rows = {row["id"]: (f["name"], row)
                for f in served["families"] for row in f["crashes"]}
        for c in JS_CRASHES_2:
            with self.subTest(crash=c.id):
                family, row = rows[c.id]
                self.assertEqual(family, c.family)
                self.assertNotIn("line", row)
                self.assertNotIn("meaning", row)
                self.assertNotIn("fix", row)
                self.assertIn("message", row)

    def test_findable_and_marked_by_halves(self) -> None:
        with _registered():
            for c in JS_CRASHES_2:
                with self.subTest(crash=c.id):
                    self.assertIs(crash(c.id), c)
                    self.assertTrue(self._check(c.id, c.line, c.meaning).passed)
                    other = 1 if c.line != 1 else 2
                    wrong_line = self._check(c.id, other, c.meaning)
                    self.assertFalse(wrong_line.passed)
                    self.assertFalse(wrong_line.line_right)
                    self.assertTrue(wrong_line.meaning_right)
                    wrong_reading = self._check(c.id, c.line, c.decoys[0])
                    self.assertFalse(wrong_reading.passed)
                    self.assertTrue(wrong_reading.line_right)
                    self.assertFalse(wrong_reading.meaning_right)


# ── Predict ─────────────────────────────────────────────────


class PuzzleTests(unittest.TestCase):
    def test_node_agrees_with_every_written_answer(self) -> None:
        for p in JS_PUZZLES_3:
            with self.subTest(puzzle=p.id):
                stdout, stderr, code = _run(p.code)
                self.assertEqual(code, 0, (stderr or stdout)[:300])
                self.assertEqual(
                    stdout.rstrip("\n"), p.expect,
                    f"{p.id}: node prints {stdout.rstrip()!r} "
                    f"and the file says {p.expect!r}")

    def test_there_are_eight_in_the_javascript_families(self) -> None:
        self.assertEqual(len(JS_PUZZLES_3), 8)
        for p in JS_PUZZLES_3:
            with self.subTest(puzzle=p.id):
                self.assertEqual(p.language, "javascript")
                self.assertIn(p.family, JS_PREDICT_FAMILIES)
                self.assertIn(p.family, predict_families())
                self.assertEqual(language_of(p.family), "javascript")

    def test_every_puzzle_explains_itself(self) -> None:
        for p in JS_PUZZLES_3:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.expect.strip())
                self.assertTrue(p.name.strip())
                self.assertTrue(p.why.strip())
                self.assertIn("console.log", p.code)
                self.assertLessEqual(len(p.code.splitlines()), 12)

    def test_the_answer_is_not_sitting_in_the_snippet(self) -> None:
        for p in JS_PUZZLES_3:
            with self.subTest(puzzle=p.id):
                if len(p.expect) < 8:
                    continue
                self.assertNotIn(p.expect, p.code)

    def test_ids_are_unique_and_new(self) -> None:
        mine = [p.id for p in JS_PUZZLES_3]
        self.assertEqual(len(mine), len(set(mine)))
        others = {p.id for p in PUZZLES if p not in JS_PUZZLES_3}
        self.assertFalse(set(mine) & others)

    def test_no_snippet_repeats_an_earlier_set(self) -> None:
        old = {p.code for p in JS_PUZZLES + JS_PUZZLES_2}
        for p in JS_PUZZLES_3:
            with self.subTest(puzzle=p.id):
                self.assertNotIn(p.code, old)

    def test_the_file_is_written_least_surprising_first(self) -> None:
        levels = [p.level for p in JS_PUZZLES_3]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)
        for level in levels:
            self.assertIn(level, (1, 2, 3, 4, 5))

    def test_registered_they_are_checked_by_the_route(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import PredictCheckRequest

        with _registered():
            for family in predict_families():
                levels = [p.level for p in predict_module.puzzles(family)]
                self.assertEqual(levels, sorted(levels))
            for p in JS_PUZZLES_3:
                with self.subTest(puzzle=p.id):
                    right = server.predict_check(
                        PredictCheckRequest(puzzle_id=p.id, guess=p.expect))
                    self.assertTrue(right.passed)
                    self.assertTrue(right.why.strip())
                    wrong = server.predict_check(PredictCheckRequest(
                        puzzle_id=p.id, guess=p.expect + " and then some"))
                    self.assertFalse(wrong.passed)


if __name__ == "__main__":
    unittest.main()
