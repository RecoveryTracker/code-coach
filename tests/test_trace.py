"""Stopping the program mid-run.

The load-bearing test is `test_the_tracer_says_exactly_this`: every
expected value is checked against what the tracer reports, so a moment
whose answer has quietly stopped being true fails here rather than
marking somebody wrong.

The second one worth its keep is `test_the_moment_exists`. A puzzle
asking about the fourth time round a loop that goes round three times
has no answer at all, and the failure mode without this test is a
question that can never be got right.
"""

from __future__ import annotations

import unittest

from code_coach.trace import (
    _nth,
    one_trace,
    render,
    trace_families,
    traces,
    value_at,
)


class ShapeTests(unittest.TestCase):
    def test_there_are_some_in_every_family(self) -> None:
        self.assertGreaterEqual(len(traces()), 8)
        for family in trace_families():
            with self.subTest(family=family):
                self.assertGreaterEqual(len(traces(family)), 3)

    def test_ids_are_unique(self) -> None:
        ids = [t.id for t in traces()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_one_is_findable_by_id(self) -> None:
        for t in traces():
            with self.subTest(trace=t.id):
                self.assertIs(one_trace(t.id), t)

    def test_short_enough_to_follow_by_hand(self) -> None:
        """The whole exercise is holding the program in your head. A
        program you have to scroll is a different exercise."""
        for t in traces():
            with self.subTest(trace=t.id):
                self.assertLessEqual(len(t.numbered), 10)

    def test_the_line_asked_about_is_a_real_line(self) -> None:
        for t in traces():
            with self.subTest(trace=t.id):
                self.assertGreaterEqual(t.at_line, 1)
                self.assertLessEqual(t.at_line, len(t.numbered))
                self.assertGreaterEqual(t.occurrence, 1)

    def test_the_ranking_was_done(self) -> None:
        for family in trace_families():
            with self.subTest(family=family):
                levels = [t.level for t in traces(family)]
                self.assertEqual(levels, sorted(levels))
                self.assertGreater(len(set(levels)), 1)


from code_coach.engine import dart_available


class TracerTests(unittest.TestCase):
    def test_the_tracer_says_exactly_this(self) -> None:
        """The one everything rests on."""
        for t in traces():
            if t.language == "dart" and not dart_available():
                continue  # Dart comes with Flutter; skipped, not failed
            with self.subTest(trace=t.id):
                got = value_at(
                    t.code, t.at_line, t.occurrence, t.variable, t.language)
                self.assertEqual(
                    got, t.expect,
                    f"{t.id}: the tracer says {got!r}")

    def test_the_moment_exists(self) -> None:
        """A line that is never reached, or a loop that does not go
        round that many times, is a question with no answer."""
        for t in traces():
            if t.language == "dart" and not dart_available():
                continue  # Dart comes with Flutter; skipped, not failed
            with self.subTest(trace=t.id):
                got = value_at(
                    t.code, t.at_line, t.occurrence, t.variable, t.language)
                self.assertTrue(
                    got,
                    f"{t.id}: nothing is reported for {t.variable} at "
                    f"line {t.at_line} (time {t.occurrence})")

    def test_a_moment_that_never_happens_gives_nothing(self) -> None:
        """The other half: value_at has to say so rather than guess."""
        t = traces()[0]
        self.assertEqual(
            value_at(t.code, t.at_line, 99, t.variable, t.language), "")
        self.assertEqual(
            value_at(t.code, t.at_line, 1, "nosuchvariable", t.language), "")


class RenderTests(unittest.TestCase):
    """The notation the answers are written in, which has to match what
    the screen shows or the right answer looks wrong."""

    def test_primitives(self) -> None:
        self.assertEqual(render({"k": "prim", "t": "int", "v": 7}, {}), "7")
        self.assertEqual(
            render({"k": "prim", "t": "str", "v": "hi"}, {}), "'hi'")
        self.assertEqual(
            render({"k": "prim", "t": "bool", "v": True}, {}), "true")
        self.assertEqual(
            render({"k": "prim", "t": "none", "v": None}, {}), "null")

    def test_a_list(self) -> None:
        heap = {"1": {"k": "list", "items": [
            {"k": "prim", "t": "int", "v": 1},
            {"k": "prim", "t": "int", "v": 2},
        ]}}
        self.assertEqual(render({"k": "ref", "id": 1}, heap), "[1, 2]")

    def test_an_object_uses_unquoted_keys(self) -> None:
        """Which is how JavaScript writes them, and how the programs in
        the puzzles write them."""
        heap = {"1": {"k": "dict", "pairs": [
            [{"k": "prim", "t": "str", "v": "total"},
             {"k": "prim", "t": "int", "v": 120}],
        ]}}
        self.assertEqual(
            render({"k": "ref", "id": 1}, heap), "{ total: 120 }")

    def test_an_empty_object(self) -> None:
        heap = {"1": {"k": "dict", "pairs": []}}
        self.assertEqual(render({"k": "ref", "id": 1}, heap), "{}")


class QuestionTests(unittest.TestCase):
    def test_the_ordinal_is_right_including_the_teens(self) -> None:
        self.assertEqual(
            [_nth(n) for n in (1, 2, 3, 4, 11, 12, 13, 21, 112)],
            ["1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st",
             "112th"])

    def test_a_straight_line_question_says_no_time(self) -> None:
        """Saying "for the 1st time" about a line that runs once reads
        as though something repeats, which is the exact confusion the
        wording exists to avoid."""
        straight = [t for t in traces() if t.occurrence == 1]
        self.assertTrue(straight)
        for t in straight:
            with self.subTest(trace=t.id):
                self.assertNotIn("time", t.question)

    def test_a_loop_question_says_which_time(self) -> None:
        repeated = [t for t in traces() if t.occurrence > 1]
        self.assertTrue(repeated, "no puzzle asks about a loop")
        for t in repeated:
            with self.subTest(trace=t.id):
                self.assertIn("time", t.question)
                self.assertIn(t.variable, t.question)


class ChoiceTests(unittest.TestCase):
    def test_there_is_something_to_choose_between(self) -> None:
        for t in traces():
            with self.subTest(trace=t.id):
                self.assertGreaterEqual(len(t.choices), 3)

    def test_the_answer_is_among_them_and_not_a_decoy(self) -> None:
        for t in traces():
            with self.subTest(trace=t.id):
                self.assertIn(t.expect, t.choices)
                self.assertNotIn(t.expect, t.decoys)
                self.assertEqual(len(set(t.decoys)), len(t.decoys))

    def test_the_order_gives_nothing_away(self) -> None:
        for t in traces():
            with self.subTest(trace=t.id):
                self.assertEqual(list(t.choices), sorted(t.choices))

    def test_every_one_explains_itself(self) -> None:
        for t in traces():
            with self.subTest(trace=t.id):
                self.assertGreater(len(t.why), 150)


class RouteTests(unittest.TestCase):
    def _list(self):
        from code_coach.api import server

        return server.trace_list()

    def _check(self, trace_id: str, answer: str):
        from code_coach.api import server
        from code_coach.api.schemas import TraceCheckRequest

        return server.trace_check(
            TraceCheckRequest(trace_id=trace_id, answer=answer))

    def test_the_list_is_grouped_and_complete(self) -> None:
        served = self._list()
        self.assertEqual(
            [f["name"] for f in served["families"]], list(trace_families()))
        self.assertEqual(
            sum(len(f["traces"]) for f in served["families"]), len(traces()))

    def test_the_answer_does_not_ride_along(self) -> None:
        served = self._list()
        for family in served["families"]:
            for row in family["traces"]:
                with self.subTest(trace=row["id"]):
                    self.assertNotIn("expect", row)
                    self.assertNotIn("why", row)
                    self.assertIn("question", row)
                    self.assertIn("choices", row)

    def test_the_right_answer_passes(self) -> None:
        for t in traces():
            with self.subTest(trace=t.id):
                got = self._check(t.id, t.expect)
                self.assertTrue(got.passed)
                self.assertTrue(got.why)

    def test_a_wrong_answer_does_not(self) -> None:
        for t in traces():
            for decoy in t.decoys:
                with self.subTest(trace=t.id, decoy=decoy):
                    got = self._check(t.id, decoy)
                    self.assertFalse(got.passed)
                    self.assertEqual(got.expect, t.expect)
                    self.assertTrue(got.why)

    def test_an_unknown_one_is_a_404(self) -> None:
        from fastapi import HTTPException

        with self.assertRaises(HTTPException) as caught:
            self._check("no-such-trace", "1")
        self.assertEqual(caught.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
