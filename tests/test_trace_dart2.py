"""The second set of Dart moments, held to the rules of
tests/test_trace_dart.py and tests/test_trace.py.

Imported directly, before registration. The route tests patch
`traces()` to include them, the way it will once they are registered.
"""

from __future__ import annotations

import contextlib
import functools
import unittest
from unittest import mock

import code_coach.trace as trace_module
from code_coach.engine import dart_available
from code_coach.trace import one_trace, traces, value_at
from code_coach.trace.content_dart import DART_TRACES
from code_coach.trace.content_dart2 import DART_TRACES_2


@functools.lru_cache(maxsize=None)
def _traced(code: str, at_line: int, occurrence: int, variable: str) -> str:
    return value_at(code, at_line, occurrence, variable, "dart")


@contextlib.contextmanager
def _registered():
    real = traces

    def with_mine(family: str | None = None):
        base = real()
        have = {t.id for t in base}
        everything = (*base, *(t for t in DART_TRACES_2 if t.id not in have))
        if family is not None:
            everything = tuple(t for t in everything if t.family == family)
        return tuple(sorted(everything, key=lambda t: t.level))

    with mock.patch.object(trace_module, "traces", with_mine):
        yield


class ShapeTests(unittest.TestCase):
    def test_there_are_six(self) -> None:
        self.assertEqual(len(DART_TRACES_2), 6)

    def test_all_dart_and_one_family(self) -> None:
        for t in DART_TRACES_2:
            with self.subTest(trace=t.id):
                self.assertEqual(t.language, "dart")
                self.assertEqual(t.family, "Dart")
                self.assertTrue(t.code.startswith("void main() {"))

    def test_ids_are_unique_and_new(self) -> None:
        ids = [t.id for t in DART_TRACES_2]
        self.assertEqual(len(ids), len(set(ids)))
        # Everything else registered - this set is registered too now.
        taken = {t.id for t in traces() if t not in DART_TRACES_2} | {t.id for t in DART_TRACES}
        self.assertFalse(taken & set(ids))

    def test_no_program_repeats_an_existing_one(self) -> None:
        old = {t.code for t in DART_TRACES}
        for t in DART_TRACES_2:
            with self.subTest(trace=t.id):
                self.assertNotIn(t.code, old)

    def test_short_enough_to_follow_by_hand(self) -> None:
        for t in DART_TRACES_2:
            with self.subTest(trace=t.id):
                self.assertLessEqual(len(t.numbered), 10)

    def test_the_line_asked_about_is_a_real_line(self) -> None:
        for t in DART_TRACES_2:
            with self.subTest(trace=t.id):
                self.assertGreaterEqual(t.at_line, 1)
                self.assertLessEqual(t.at_line, len(t.numbered))
                self.assertGreaterEqual(t.occurrence, 1)

    def test_the_ranking_was_done(self) -> None:
        levels = [t.level for t in DART_TRACES_2]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)


@unittest.skipUnless(dart_available(), "Dart SDK not on PATH")
class TracerTests(unittest.TestCase):
    def test_the_tracer_says_exactly_this(self) -> None:
        for t in DART_TRACES_2:
            with self.subTest(trace=t.id):
                got = _traced(t.code, t.at_line, t.occurrence, t.variable)
                self.assertEqual(
                    got, t.expect, f"{t.id}: the tracer says {got!r}")

    def test_the_moment_exists(self) -> None:
        for t in DART_TRACES_2:
            with self.subTest(trace=t.id):
                got = _traced(t.code, t.at_line, t.occurrence, t.variable)
                self.assertTrue(
                    got,
                    f"{t.id}: nothing is reported for {t.variable} at "
                    f"line {t.at_line} (time {t.occurrence})")

    def test_a_moment_that_never_happens_gives_nothing(self) -> None:
        t = DART_TRACES_2[0]
        self.assertEqual(
            value_at(t.code, t.at_line, 99, t.variable, t.language), "")


class QuestionTests(unittest.TestCase):
    def test_a_straight_line_question_says_no_time(self) -> None:
        straight = [t for t in DART_TRACES_2 if t.occurrence == 1]
        self.assertTrue(straight)
        for t in straight:
            with self.subTest(trace=t.id):
                self.assertNotIn("time", t.question)

    def test_a_loop_question_says_which_time(self) -> None:
        repeated = [t for t in DART_TRACES_2 if t.occurrence > 1]
        self.assertTrue(repeated)
        for t in repeated:
            with self.subTest(trace=t.id):
                self.assertIn("time", t.question)
                self.assertIn(t.variable, t.question)


class ChoiceTests(unittest.TestCase):
    def test_there_is_something_to_choose_between(self) -> None:
        for t in DART_TRACES_2:
            with self.subTest(trace=t.id):
                self.assertGreaterEqual(len(t.choices), 3)

    def test_the_answer_is_among_them_and_not_a_decoy(self) -> None:
        for t in DART_TRACES_2:
            with self.subTest(trace=t.id):
                self.assertIn(t.expect, t.choices)
                self.assertNotIn(t.expect, t.decoys)
                self.assertEqual(len(set(t.decoys)), len(t.decoys))

    def test_the_order_gives_nothing_away(self) -> None:
        for t in DART_TRACES_2:
            with self.subTest(trace=t.id):
                self.assertEqual(list(t.choices), sorted(t.choices))

    def test_every_one_explains_itself(self) -> None:
        for t in DART_TRACES_2:
            with self.subTest(trace=t.id):
                self.assertGreater(len(t.why), 150)


class RouteTests(unittest.TestCase):
    def _check(self, trace_id: str, answer: str):
        from code_coach.api import server
        from code_coach.api.schemas import TraceCheckRequest

        return server.trace_check(
            TraceCheckRequest(trace_id=trace_id, answer=answer))

    def test_they_are_listed_in_the_dart_family(self) -> None:
        from code_coach.api import server

        with _registered():
            served = server.trace_list()
        dart = [f for f in served["families"] if f["name"] == "Dart"]
        self.assertEqual(len(dart), 1)
        ids = {row["id"] for row in dart[0]["traces"]}
        self.assertTrue({t.id for t in DART_TRACES_2} <= ids)
        for row in dart[0]["traces"]:
            self.assertEqual(row["language"], "dart")
            self.assertNotIn("expect", row)

    def test_every_one_is_findable_by_id(self) -> None:
        with _registered():
            for t in DART_TRACES_2:
                with self.subTest(trace=t.id):
                    self.assertIs(one_trace(t.id), t)

    def test_the_right_answer_passes(self) -> None:
        with _registered():
            for t in DART_TRACES_2:
                with self.subTest(trace=t.id):
                    self.assertTrue(self._check(t.id, t.expect).passed)

    def test_a_wrong_answer_does_not(self) -> None:
        with _registered():
            for t in DART_TRACES_2:
                for decoy in t.decoys:
                    with self.subTest(trace=t.id, decoy=decoy):
                        got = self._check(t.id, decoy)
                        self.assertFalse(got.passed)
                        self.assertEqual(got.expect, t.expect)


if __name__ == "__main__":
    unittest.main()
