"""The Dart moments, held to the same rules as tests/test_trace.py.

They are imported directly rather than through `traces()`, so these
checks hold whether or not the family has been registered yet. The
route tests are the exception: they can only run once `one_trace`
can find a Dart moment, and they skip until then.

Tracing Dart starts two VMs and connects a debugger between them, so
it takes a few seconds per program. Each moment is traced once and the
answer is cached for the tests that need it.
"""

from __future__ import annotations

import functools
import unittest

from code_coach.engine import dart_available
from code_coach.trace import one_trace, traces, value_at
from code_coach.trace.content_dart import DART_TRACES


@functools.lru_cache(maxsize=None)
def _traced(code: str, at_line: int, occurrence: int, variable: str) -> str:
    return value_at(code, at_line, occurrence, variable, "dart")


def _registered() -> bool:
    return one_trace(DART_TRACES[0].id) is not None


class ShapeTests(unittest.TestCase):
    def test_there_are_enough(self) -> None:
        self.assertGreaterEqual(len(DART_TRACES), 6)

    def test_all_dart_and_one_family(self) -> None:
        for t in DART_TRACES:
            with self.subTest(trace=t.id):
                self.assertEqual(t.language, "dart")
                self.assertEqual(t.family, "Dart")
                self.assertTrue(t.code.startswith("void main() {"))

    def test_ids_are_unique_including_against_the_others(self) -> None:
        ids = [t.id for t in DART_TRACES]
        self.assertEqual(len(ids), len(set(ids)))
        # Once registered they are part of traces() and cannot be
        # compared with themselves, so only the rest count here.
        others = {t.id for t in traces() if t.language != "dart"}
        self.assertFalse(others & set(ids))

    def test_short_enough_to_follow_by_hand(self) -> None:
        for t in DART_TRACES:
            with self.subTest(trace=t.id):
                self.assertLessEqual(len(t.numbered), 10)

    def test_the_line_asked_about_is_a_real_line(self) -> None:
        for t in DART_TRACES:
            with self.subTest(trace=t.id):
                self.assertGreaterEqual(t.at_line, 1)
                self.assertLessEqual(t.at_line, len(t.numbered))
                self.assertGreaterEqual(t.occurrence, 1)

    def test_the_ranking_was_done(self) -> None:
        levels = [t.level for t in DART_TRACES]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)


@unittest.skipUnless(dart_available(), "Dart SDK not on PATH")
class TracerTests(unittest.TestCase):
    def test_the_tracer_says_exactly_this(self) -> None:
        """The one everything rests on."""
        for t in DART_TRACES:
            with self.subTest(trace=t.id):
                got = _traced(t.code, t.at_line, t.occurrence, t.variable)
                self.assertEqual(
                    got, t.expect, f"{t.id}: the tracer says {got!r}")

    def test_the_moment_exists(self) -> None:
        for t in DART_TRACES:
            with self.subTest(trace=t.id):
                got = _traced(t.code, t.at_line, t.occurrence, t.variable)
                self.assertTrue(
                    got,
                    f"{t.id}: nothing is reported for {t.variable} at "
                    f"line {t.at_line} (time {t.occurrence})")

    def test_a_moment_that_never_happens_gives_nothing(self) -> None:
        t = DART_TRACES[0]
        self.assertEqual(
            value_at(t.code, t.at_line, 99, t.variable, t.language), "")
        self.assertEqual(
            value_at(t.code, t.at_line, 1, "nosuchvariable", t.language), "")


class QuestionTests(unittest.TestCase):
    def test_a_straight_line_question_says_no_time(self) -> None:
        straight = [t for t in DART_TRACES if t.occurrence == 1]
        self.assertTrue(straight)
        for t in straight:
            with self.subTest(trace=t.id):
                self.assertNotIn("time", t.question)

    def test_a_loop_question_says_which_time(self) -> None:
        repeated = [t for t in DART_TRACES if t.occurrence > 1]
        self.assertTrue(repeated, "no Dart moment stops part way round")
        for t in repeated:
            with self.subTest(trace=t.id):
                self.assertIn("time", t.question)
                self.assertIn(t.variable, t.question)


class ChoiceTests(unittest.TestCase):
    def test_there_is_something_to_choose_between(self) -> None:
        for t in DART_TRACES:
            with self.subTest(trace=t.id):
                self.assertGreaterEqual(len(t.choices), 3)

    def test_the_answer_is_among_them_and_not_a_decoy(self) -> None:
        for t in DART_TRACES:
            with self.subTest(trace=t.id):
                self.assertIn(t.expect, t.choices)
                self.assertNotIn(t.expect, t.decoys)
                self.assertEqual(len(set(t.decoys)), len(t.decoys))

    def test_the_order_gives_nothing_away(self) -> None:
        for t in DART_TRACES:
            with self.subTest(trace=t.id):
                self.assertEqual(list(t.choices), sorted(t.choices))

    def test_every_one_explains_itself(self) -> None:
        for t in DART_TRACES:
            with self.subTest(trace=t.id):
                self.assertGreater(len(t.why), 150)


@unittest.skipUnless(_registered(), "Dart moments not registered in traces()")
class RouteTests(unittest.TestCase):
    def _check(self, trace_id: str, answer: str):
        from code_coach.api import server
        from code_coach.api.schemas import TraceCheckRequest

        return server.trace_check(
            TraceCheckRequest(trace_id=trace_id, answer=answer))

    def test_the_family_is_listed(self) -> None:
        from code_coach.api import server

        served = server.trace_list()
        dart = [f for f in served["families"] if f["name"] == "Dart"]
        self.assertEqual(len(dart), 1)
        self.assertEqual(
            {row["id"] for row in dart[0]["traces"]},
            {t.id for t in DART_TRACES})
        for row in dart[0]["traces"]:
            self.assertEqual(row["language"], "dart")
            self.assertNotIn("expect", row)

    def test_the_right_answer_passes(self) -> None:
        for t in DART_TRACES:
            with self.subTest(trace=t.id):
                self.assertTrue(self._check(t.id, t.expect).passed)

    def test_a_wrong_answer_does_not(self) -> None:
        for t in DART_TRACES:
            for decoy in t.decoys:
                with self.subTest(trace=t.id, decoy=decoy):
                    got = self._check(t.id, decoy)
                    self.assertFalse(got.passed)
                    self.assertEqual(got.expect, t.expect)


if __name__ == "__main__":
    unittest.main()
