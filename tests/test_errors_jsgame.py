"""The game-code crash set, held to the rules of tests/test_errors.py.

JS_GAME_CRASHES is imported directly, so these hold before and after it
is registered; the route checks patch it into `crashes()` for their
duration. The load-bearing check runs every program: each crash's
message and line are what Node reported through `engine_report`.
"""

from __future__ import annotations

import contextlib
import functools
import unittest
from unittest import mock

import code_coach.errors as errors_module
from code_coach.engine import run_code
from code_coach.errors import crash, crashes, engine_report
from code_coach.errors.content_jsgame import GAME, JS_GAME_CRASHES


@functools.lru_cache(maxsize=None)
def _report(code: str) -> tuple[str, int]:
    return engine_report(code, "javascript")


def _with_mine(base: tuple) -> tuple:
    have = {c.id for c in base}
    return (*base, *(c for c in JS_GAME_CRASHES if c.id not in have))


def _others() -> tuple:
    return tuple(c for c in crashes() if c not in JS_GAME_CRASHES)


@contextlib.contextmanager
def _registered():
    """crashes() and crash_families() as they will be once the set is
    registered."""
    real_crashes = errors_module.crashes
    real_families = errors_module.crash_families

    def with_mine(family: str | None = None):
        everything = _with_mine(real_crashes())
        if family is not None:
            everything = tuple(c for c in everything if c.family == family)
        return tuple(sorted(everything, key=lambda c: c.level))

    def families_with_mine():
        names = list(real_families())
        if GAME not in names:
            names.append(GAME)
        return tuple(names)

    with mock.patch.object(errors_module, "crashes", with_mine), \
            mock.patch.object(errors_module, "crash_families",
                              families_with_mine):
        yield


class ShapeTests(unittest.TestCase):
    def test_all_javascript_in_one_family(self) -> None:
        self.assertGreaterEqual(len(JS_GAME_CRASHES), 6)
        for c in JS_GAME_CRASHES:
            with self.subTest(crash=c.id):
                self.assertEqual(c.language, "javascript")
                self.assertEqual(c.family, GAME)
                self.assertTrue(c.id.startswith("err-jsg-"))

    def test_ids_are_unique_and_new(self) -> None:
        ids = [c.id for c in JS_GAME_CRASHES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertFalse({c.id for c in _others()} & set(ids))

    def test_no_message_repeats_another_javascript_crash(self) -> None:
        old = {c.message for c in _others() if c.language == "javascript"}
        for c in JS_GAME_CRASHES:
            with self.subTest(crash=c.id):
                self.assertNotIn(c.message, old)

    def test_they_are_short_enough_to_hold_in_your_head(self) -> None:
        for c in JS_GAME_CRASHES:
            with self.subTest(crash=c.id):
                self.assertLessEqual(len(c.numbered), 10)
                self.assertGreaterEqual(len(c.numbered), 2)

    def test_the_ranking_was_done(self) -> None:
        levels = [c.level for c in JS_GAME_CRASHES]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)
        for level in levels:
            self.assertIn(level, range(1, 6))

    def test_the_blamed_line_is_a_real_line(self) -> None:
        for c in JS_GAME_CRASHES:
            with self.subTest(crash=c.id):
                self.assertGreaterEqual(c.line, 1)
                self.assertLessEqual(c.line, len(c.numbered))

    def test_the_message_is_one_line(self) -> None:
        for c in JS_GAME_CRASHES:
            with self.subTest(crash=c.id):
                self.assertNotIn("\n", c.message)
                self.assertNotIn("    at ", c.message)


class EngineTests(unittest.TestCase):
    def test_the_engine_says_exactly_this(self) -> None:
        for c in JS_GAME_CRASHES:
            with self.subTest(crash=c.id):
                message, line = _report(c.code)
                self.assertEqual(
                    message, c.message, f"{c.id}: node says {message!r}")
                self.assertEqual(
                    line, c.line, f"{c.id}: node blames line {line}")

    def test_every_one_actually_crashes(self) -> None:
        for c in JS_GAME_CRASHES:
            with self.subTest(crash=c.id):
                _out, _err, exit_code = run_code(c.code, language="javascript")
                self.assertNotEqual(exit_code, 0, f"{c.id} does not crash")


class ChoiceTests(unittest.TestCase):
    def test_the_choices_are_fair(self) -> None:
        for c in JS_GAME_CRASHES:
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

        mine = longest(JS_GAME_CRASHES)
        self.assertLessEqual(
            len(mine), len(JS_GAME_CRASHES) // 2,
            "the right reading is the longest option too often: "
            + ", ".join(c.id for c in mine))
        everything = _with_mine(_others())
        self.assertLessEqual(len(longest(everything)), len(everything) // 2)

    def test_every_one_says_what_to_do(self) -> None:
        for c in JS_GAME_CRASHES:
            with self.subTest(crash=c.id):
                self.assertGreater(len(c.fix), 120)
                self.assertTrue(c.name.strip())


class RouteTests(unittest.TestCase):
    def _check(self, crash_id: str, line: int, meaning: str):
        from code_coach.api import server
        from code_coach.api.schemas import ErrorCheckRequest

        return server.error_check(
            ErrorCheckRequest(crash_id=crash_id, line=line, meaning=meaning))

    def test_served_as_one_family_without_the_answer(self) -> None:
        from code_coach.api import server

        with _registered():
            served = server.error_list()
        family = next(f for f in served["families"] if f["name"] == GAME)
        self.assertEqual(
            [row["id"] for row in family["crashes"]],
            [c.id for c in JS_GAME_CRASHES])
        for row in family["crashes"]:
            with self.subTest(crash=row["id"]):
                self.assertEqual(row["language"], "javascript")
                self.assertNotIn("line", row)
                self.assertNotIn("meaning", row)
                self.assertNotIn("fix", row)
                self.assertIn("message", row)

    def test_findable_and_marked_by_halves(self) -> None:
        with _registered():
            for c in JS_GAME_CRASHES:
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


if __name__ == "__main__":
    unittest.main()
