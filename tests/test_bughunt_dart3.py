"""The third set of Dart bug hunts, held to the rules every hunt keeps.

The same rules as tests/test_bughunt.py - the bug is real, it hides,
the report is true, there is a line to find, the explanation is fair -
run over DART_HUNTS_3 directly, so the set is checked on its own
whether or not it has been added to the collection yet.
"""

from __future__ import annotations

import unittest

from code_coach.bughunt import run_cases, try_input
from code_coach.bughunt.content5 import DART_HUNTS_3
from code_coach.engine import dart_available

#: Below this there is nothing to locate - the same floor as the others.
MIN_LINES = 8

needs_dart = unittest.skipUnless(dart_available(), "dart is not installed")


class CollectionTests(unittest.TestCase):

    def test_there_are_five_dart_hunts(self) -> None:
        self.assertEqual(len(DART_HUNTS_3), 5)
        for h in DART_HUNTS_3:
            with self.subTest(hunt=h.id):
                self.assertEqual((h.family, h.language), ("Dart", "dart"))
                self.assertTrue(h.id.startswith("hunt-dart-"))
                self.assertEqual(len(h.types), len(h.params))
                self.assertTrue(h.returns)

    def test_ids_are_unique_and_new(self) -> None:
        from code_coach.bughunt import hunts
        from code_coach.bughunt.content import JAVASCRIPT_HUNTS, PYTHON_HUNTS
        from code_coach.bughunt.content2 import JAVASCRIPT_HUNTS_2, PYTHON_HUNTS_2
        from code_coach.bughunt.content3 import DART_HUNTS
        from code_coach.bughunt.content4 import DART_HUNTS_2

        ids = [h.id for h in DART_HUNTS_3]
        self.assertEqual(len(ids), len(set(ids)))
        taken = {h.id for h in (PYTHON_HUNTS + PYTHON_HUNTS_2 + JAVASCRIPT_HUNTS
                                + JAVASCRIPT_HUNTS_2 + DART_HUNTS + DART_HUNTS_2)}
        taken |= {h.id for h in hunts()
                  if not any(h is mine for mine in DART_HUNTS_3)}
        self.assertFalse(taken & set(ids), "an id is already used")

    def test_they_read_easiest_first_and_are_not_all_one_level(self) -> None:
        levels = [h.level for h in DART_HUNTS_3]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)

    def test_every_hunt_says_everything_it_needs_to(self) -> None:
        for h in DART_HUNTS_3:
            with self.subTest(hunt=h.id):
                for text in (h.title, h.report, h.cause, h.lesson, h.hint):
                    self.assertTrue(text.strip())


class TheOracleTests(unittest.TestCase):

    def test_the_oracle_agrees_with_answers_worked_out_by_hand(self) -> None:
        for h in DART_HUNTS_3:
            with self.subTest(hunt=h.id):
                self.assertTrue(h.checks, f"{h.id} has no hand-written answer")
                for args, want in h.checks:
                    self.assertEqual(h.answer(args), want, f"{h.id}{args}")

    def test_the_report_is_one_of_the_hand_checked_inputs(self) -> None:
        for h in DART_HUNTS_3:
            with self.subTest(hunt=h.id):
                self.assertIn(tuple(h.reported), [tuple(a) for a, _ in h.checks])


@needs_dart
class TheBugIsRealTests(unittest.TestCase):

    def test_the_fixed_program_passes_every_case(self) -> None:
        for h in DART_HUNTS_3:
            with self.subTest(hunt=h.id):
                outcome = run_cases(h, h.fixed)
                self.assertEqual(outcome.broke, "", h.id)
                failed = [r.args for r in outcome.results if not r.passed]
                self.assertEqual(failed, [], f"{h.id}: {failed}")

    def test_the_broken_program_fails_some_case(self) -> None:
        for h in DART_HUNTS_3:
            with self.subTest(hunt=h.id):
                self.assertFalse(run_cases(h, h.start).passed, h.id)


@needs_dart
class TheBugHidesTests(unittest.TestCase):

    def test_some_cases_pass_on_the_broken_program(self) -> None:
        for h in DART_HUNTS_3:
            with self.subTest(hunt=h.id):
                outcome = run_cases(h, h.start)
                self.assertEqual(outcome.broke, "", h.id)
                passing = [r for r in outcome.results if r.passed]
                self.assertTrue(passing, f"{h.id}: every input shows the bug")


@needs_dart
class TheReportIsTrueTests(unittest.TestCase):

    def test_the_reported_input_reproduces_the_bug(self) -> None:
        for h in DART_HUNTS_3:
            with self.subTest(hunt=h.id):
                self.assertTrue(try_input(h, h.reported).reproduced, h.id)

    def test_a_passing_input_does_not_count_as_reproducing(self) -> None:
        for h in DART_HUNTS_3:
            outcome = run_cases(h, h.start)
            fine = next(r.args for r in outcome.results if r.passed)
            with self.subTest(hunt=h.id, args=fine):
                self.assertFalse(try_input(h, tuple(fine)).reproduced)

    def test_the_map_hunt_fails_by_throwing_and_the_fix_does_not(self) -> None:
        """The remove-while-iterating hunt's report quotes the error, so
        the error has to be the one Dart actually throws."""
        h = next(h for h in DART_HUNTS_3
                 if h.id == "hunt-dart-remove-while-iterating")
        got = try_input(h, h.reported)
        self.assertTrue(got.reproduced)
        self.assertIn("ConcurrentModificationError", got.error)
        fixed = run_cases(h, h.fixed, (h.reported,)).results[0]
        self.assertTrue(fixed.passed)
        self.assertFalse(fixed.changed)

    def test_december_reads_past_the_end(self) -> None:
        """The month hunt's lesson says quarters[12] is a RangeError."""
        h = next(h for h in DART_HUNTS_3 if h.id == "hunt-dart-month-index")
        got = try_input(h, ("2026-12-24",))
        self.assertTrue(got.reproduced)
        self.assertIn("RangeError", got.error)


class ThereIsSomethingToLocateTests(unittest.TestCase):

    def test_the_program_is_long_enough_to_search(self) -> None:
        for h in DART_HUNTS_3:
            with self.subTest(hunt=h.id):
                self.assertGreaterEqual(len(h.lines), MIN_LINES)

    def test_the_fix_changes_one_or_two_lines_in_place(self) -> None:
        for h in DART_HUNTS_3:
            with self.subTest(hunt=h.id):
                before = h.start.rstrip("\n").split("\n")
                after = h.fixed.rstrip("\n").split("\n")
                self.assertEqual(len(before), len(after))
                self.assertIn(len(h.bug_lines), (1, 2))

    def test_the_bug_line_is_not_blank(self) -> None:
        for h in DART_HUNTS_3:
            for n in h.bug_lines:
                with self.subTest(hunt=h.id, line=n):
                    self.assertTrue(h.lines[n - 1].strip())


class TheExplanationIsFairTests(unittest.TestCase):

    def test_the_cause_is_not_among_the_decoys(self) -> None:
        for h in DART_HUNTS_3:
            with self.subTest(hunt=h.id):
                self.assertNotIn(h.cause, h.decoys)
                self.assertGreaterEqual(len(set(h.decoys)), 2)
                self.assertEqual(len(h.choices), len(set(h.decoys)) + 1)


if __name__ == "__main__":
    unittest.main()
