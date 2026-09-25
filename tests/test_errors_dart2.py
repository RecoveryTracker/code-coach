"""The second set of Dart crashes, held to the same rules as the first.

`test_errors_dart.py` and `test_errors.py`, applied to DART_CRASHES_2
before it is registered in `crashes()`. `engine_report` reads Dart now,
so the load-bearing check goes straight through it: the message and
line each crash records are what `dart run` printed.
"""

from __future__ import annotations

import contextlib
import functools
import unittest
from unittest import mock

import code_coach.errors as errors_module
from code_coach.engine import dart_available, run_code
from code_coach.errors import crash, crashes, engine_report
from code_coach.errors.content_dart2 import DART_CRASHES_2


@functools.lru_cache(maxsize=None)
def _run(code: str) -> tuple[str, str, int]:
    return run_code(code, language="dart")


@functools.lru_cache(maxsize=None)
def _report(code: str) -> tuple[str, int]:
    return engine_report(code, "dart")


def _with_mine(base: tuple) -> tuple:
    have = {c.id for c in base}
    return (*base, *(c for c in DART_CRASHES_2 if c.id not in have))


@contextlib.contextmanager
def _registered():
    """crashes() and crash_families() as they will be once DART_CRASHES_2
    is registered."""
    real_crashes, real_families = crashes, errors_module.crash_families

    def with_mine(family: str | None = None):
        everything = _with_mine(real_crashes())
        if family is not None:
            everything = tuple(c for c in everything if c.family == family)
        return tuple(sorted(everything, key=lambda c: c.level))

    def families_with_mine():
        seen = list(real_families())
        return (*seen, "Dart") if "Dart" not in seen else tuple(seen)

    with mock.patch.object(errors_module, "crashes", with_mine), \
            mock.patch.object(errors_module, "crash_families",
                              families_with_mine):
        yield


class ShapeTests(unittest.TestCase):
    def test_there_are_six_and_all_dart(self) -> None:
        self.assertEqual(len(DART_CRASHES_2), 6)
        for c in DART_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertEqual(c.family, "Dart")
                self.assertEqual(c.language, "dart")

    def test_ids_are_unique_and_new(self) -> None:
        ids = [c.id for c in DART_CRASHES_2]
        self.assertEqual(len(ids), len(set(ids)))
        from code_coach.errors.content_dart import DART_CRASHES

        # Everything else registered - this set is registered too now.
        taken = {c.id for c in crashes() if c not in DART_CRASHES_2} | {c.id for c in DART_CRASHES}
        self.assertFalse(taken & set(ids))

    def test_no_message_repeats_an_existing_one(self) -> None:
        """A second set that re-asks the first set's question teaches
        nothing new."""
        from code_coach.errors.content_dart import DART_CRASHES

        old = {c.message for c in DART_CRASHES}
        for c in DART_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertNotIn(c.message, old)

    def test_every_one_is_a_program(self) -> None:
        for c in DART_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertIn("void main()", c.code)

    def test_they_are_short_enough_to_hold_in_your_head(self) -> None:
        for c in DART_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertLessEqual(len(c.numbered), 10)
                self.assertGreaterEqual(len(c.numbered), 2)

    def test_the_ranking_was_done(self) -> None:
        levels = [c.level for c in DART_CRASHES_2]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)
        for level in levels:
            self.assertIn(level, range(1, 6))

    def test_the_blamed_line_is_a_real_line(self) -> None:
        for c in DART_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertGreaterEqual(c.line, 1)
                self.assertLessEqual(c.line, len(c.numbered))

    def test_the_message_is_one_line(self) -> None:
        for c in DART_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertNotIn("\n", c.message)
                self.assertNotIn("#0 ", c.message)
                self.assertNotIn("Unhandled exception", c.message)


@unittest.skipUnless(dart_available(), "dart is not on PATH")
class EngineTests(unittest.TestCase):
    def test_the_engine_says_exactly_this(self) -> None:
        for c in DART_CRASHES_2:
            with self.subTest(crash=c.id):
                message, line = _report(c.code)
                self.assertEqual(
                    message, c.message, f"{c.id}: dart says {message!r}")
                self.assertEqual(
                    line, c.line, f"{c.id}: dart blames line {line}")

    def test_it_crashed_running_not_compiling(self) -> None:
        """Exit 255 and "Unhandled exception:" first — a compile error
        is 254 and a different lesson."""
        for c in DART_CRASHES_2:
            with self.subTest(crash=c.id):
                _out, err, exit_code = _run(c.code)
                first = next(
                    (t.strip() for t in err.splitlines() if t.strip()), "")
                self.assertEqual(first, "Unhandled exception:", err)
                self.assertEqual(exit_code, 255, err)


class ChoiceTests(unittest.TestCase):
    def test_there_is_something_to_choose_between(self) -> None:
        for c in DART_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertGreaterEqual(len(c.choices), 3)

    def test_the_answer_is_among_them(self) -> None:
        for c in DART_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertIn(c.meaning, c.choices)

    def test_the_decoys_are_not_the_answer(self) -> None:
        for c in DART_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertNotIn(c.meaning, c.decoys)
                self.assertEqual(len(set(c.decoys)), len(c.decoys))

    def test_the_order_gives_nothing_away(self) -> None:
        for c in DART_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertEqual(list(c.choices), sorted(c.choices))

    def test_the_answer_is_not_the_longest_one(self) -> None:
        def longest(pool):
            return [c for c in pool
                    if len(c.meaning) > max(len(d) for d in c.decoys)]

        mine = longest(DART_CRASHES_2)
        self.assertLessEqual(
            len(mine), len(DART_CRASHES_2) // 2,
            "the right reading is the longest option too often: "
            + ", ".join(c.id for c in mine))
        everything = _with_mine(crashes())
        self.assertLessEqual(len(longest(everything)), len(everything) // 2)

    def test_every_one_says_what_to_do(self) -> None:
        for c in DART_CRASHES_2:
            with self.subTest(crash=c.id):
                self.assertGreater(len(c.fix), 120)
                self.assertTrue(c.name.strip())


class RouteTests(unittest.TestCase):
    def _list(self):
        from code_coach.api import server

        return server.error_list()

    def _check(self, crash_id: str, line: int, meaning: str):
        from code_coach.api import server
        from code_coach.api.schemas import ErrorCheckRequest

        return server.error_check(
            ErrorCheckRequest(crash_id=crash_id, line=line, meaning=meaning))

    def test_they_are_served_in_the_dart_family(self) -> None:
        with _registered():
            served = self._list()
        dart = next(f for f in served["families"] if f["name"] == "Dart")
        ids = {row["id"] for row in dart["crashes"]}
        self.assertTrue({c.id for c in DART_CRASHES_2} <= ids)
        for row in dart["crashes"]:
            self.assertEqual(row["language"], "dart")

    def test_every_one_is_findable_by_id(self) -> None:
        with _registered():
            for c in DART_CRASHES_2:
                with self.subTest(crash=c.id):
                    self.assertIs(crash(c.id), c)

    def test_the_answer_does_not_ride_along(self) -> None:
        with _registered():
            served = self._list()
        mine = {c.id for c in DART_CRASHES_2}
        dart = next(f for f in served["families"] if f["name"] == "Dart")
        for row in dart["crashes"]:
            if row["id"] not in mine:
                continue
            with self.subTest(crash=row["id"]):
                self.assertNotIn("line", row)
                self.assertNotIn("meaning", row)
                self.assertNotIn("fix", row)
                self.assertIn("message", row)

    def test_the_right_answer_passes(self) -> None:
        with _registered():
            for c in DART_CRASHES_2:
                with self.subTest(crash=c.id):
                    got = self._check(c.id, c.line, c.meaning)
                    self.assertTrue(got.passed)
                    self.assertTrue(got.fix)

    def test_the_wrong_line_does_not(self) -> None:
        with _registered():
            for c in DART_CRASHES_2:
                with self.subTest(crash=c.id):
                    other = 1 if c.line != 1 else 2
                    got = self._check(c.id, other, c.meaning)
                    self.assertFalse(got.passed)
                    self.assertFalse(got.line_right)
                    self.assertTrue(got.meaning_right)

    def test_the_wrong_reading_does_not(self) -> None:
        with _registered():
            for c in DART_CRASHES_2:
                with self.subTest(crash=c.id):
                    got = self._check(c.id, c.line, c.decoys[0])
                    self.assertFalse(got.passed)
                    self.assertTrue(got.line_right)
                    self.assertFalse(got.meaning_right)


if __name__ == "__main__":
    unittest.main()
