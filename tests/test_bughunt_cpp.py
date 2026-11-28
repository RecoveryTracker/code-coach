"""The C++ hunts (code_coach/bughunt/content_cpp.py), held to the same rules.

Each hunt has hand-written oracle answers (`checks`) and a hand-worked WRONG
answer the broken program must give for the reported input (BROKEN_GOT
below); the real C++ compiler runs both. Skipped when no C++ compiler is
installed.
"""

from __future__ import annotations

import unittest

from code_coach.bughunt import hunts, run_cases, try_input
from code_coach.bughunt.content_cpp import CPP_HUNTS
from code_coach.engine import cpp_available

MIN_LINES = 8

#: What the broken program returns for the reported input, worked out by
#: hand from how C behaves - not copied from a run.
BROKEN_GOT = {
    # present(0) is false, so the match at 0 is reported as missing: -1.
    "hunt-cpp-find-npos": -1,
    # A is 4; B sets 3 then falls into C's 2 and breaks: 4 + 2.
    "hunt-cpp-switch-break": 6,
    # the doubling lands on a copy, so the plain total survives: 1 + 2 + 3.
    "hunt-cpp-vector-by-value": 6,
    # seen[w] inserts w first, so count(w) is always 1: both words repeat.
    "hunt-cpp-map-brackets": 2,
    # names sorted descending: cy, bob, ana - so the first is cy.
    "hunt-cpp-sort-wrong-field": "cy",
    # 0 - 1 wraps to the biggest size_t, not < 1; the empty loop leaves 0.
    "hunt-cpp-size-minus-one": 0,
}

ALL = CPP_HUNTS


def setUpModule() -> None:
    if not cpp_available():
        raise unittest.SkipTest("no C++ compiler is installed")

def _runs():
    return ALL


class CollectionTests(unittest.TestCase):

    def test_there_are_six_cpp_hunts(self) -> None:
        self.assertGreaterEqual(len(CPP_HUNTS), 6)
        for h in CPP_HUNTS:
            self.assertEqual((h.family, h.language), ("C++", "cpp"))
            self.assertTrue(h.id.startswith("hunt-cpp-"), h.id)
            self.assertEqual(len(h.types), len(h.params), h.id)
            self.assertTrue(h.returns, h.id)

    def test_ids_are_unique_and_new(self) -> None:
        ids = [h.id for h in ALL]
        self.assertEqual(len(ids), len(set(ids)))
        for h in ALL:
            others = [o for o in hunts() if o.id == h.id and o is not h]
            self.assertEqual(others, [], f"{h.id} is already used")
        from code_coach.bughunt import _all
        from code_coach.bughunt.content_ruby import RUBY_HUNTS
        from code_coach.bughunt.content_c import C_HUNTS
        from code_coach.bughunt.content_rust import RUST_HUNTS
        from code_coach.bughunt.content10 import RUST_HUNTS_2
        self.assertFalse({h.id for h in RUBY_HUNTS + RUST_HUNTS + RUST_HUNTS_2 + C_HUNTS} & set(ids))
        self.assertTrue(set(ids) <= {h.id for h in _all()})

    def test_levels_are_spread_and_each_language_reads_easiest_first(self) -> None:
        levels = [h.level for h in CPP_HUNTS]
        self.assertEqual(levels, sorted(levels))
        self.assertTrue({1, 4} <= set(levels))
        self.assertTrue(set(levels) <= {1, 2, 3, 4})

    def test_every_hunt_says_everything_it_needs_to(self) -> None:
        for h in ALL:
            with self.subTest(hunt=h.id):
                for text in (h.title, h.report, h.cause, h.lesson, h.hint):
                    self.assertTrue(text.strip())

    def test_every_hunt_has_a_hand_worked_wrong_answer(self) -> None:
        self.assertTrue({h.id for h in ALL} <= set(BROKEN_GOT))


class TheOracleTests(unittest.TestCase):

    def test_the_oracle_agrees_with_answers_worked_out_by_hand(self) -> None:
        for h in ALL:
            with self.subTest(hunt=h.id):
                self.assertTrue(h.checks, f"{h.id} has no hand-written answer")
                for args, want in h.checks:
                    self.assertEqual(h.answer(args), want, f"{h.id}{args}")

    def test_the_report_is_one_of_the_hand_checked_inputs(self) -> None:
        for h in ALL:
            with self.subTest(hunt=h.id):
                self.assertIn(tuple(h.reported), [tuple(a) for a, _ in h.checks])

    def test_the_reported_answer_differs_from_the_hand_worked_wrong_one(self) -> None:
        for h in ALL:
            with self.subTest(hunt=h.id):
                self.assertNotEqual(h.answer(h.reported), BROKEN_GOT[h.id])


class TheBugIsRealTests(unittest.TestCase):

    def test_the_fixed_program_passes_every_case(self) -> None:
        for h in _runs():
            with self.subTest(hunt=h.id):
                outcome = run_cases(h, h.fixed)
                self.assertEqual(outcome.broke, "", h.id)
                failed = [r.args for r in outcome.results if not r.passed]
                self.assertEqual(failed, [], f"{h.id}: {failed}")

    def test_the_broken_program_fails_some_case(self) -> None:
        for h in _runs():
            with self.subTest(hunt=h.id):
                outcome = run_cases(h, h.start)
                self.assertEqual(outcome.broke, "", h.id)
                self.assertFalse(outcome.passed, h.id)

    def test_the_broken_program_gives_the_hand_worked_wrong_answer(self) -> None:
        for h in _runs():
            with self.subTest(hunt=h.id):
                outcome = run_cases(h, h.start, (h.reported,))
                self.assertEqual(outcome.broke, "", h.id)
                self.assertEqual(outcome.results[0].got, BROKEN_GOT[h.id])


class TheBugHidesTests(unittest.TestCase):

    def test_some_cases_pass_on_the_broken_program(self) -> None:
        for h in _runs():
            with self.subTest(hunt=h.id):
                outcome = run_cases(h, h.start)
                passing = [r for r in outcome.results if r.passed]
                self.assertTrue(passing, f"{h.id}: every input shows the bug")


class TheReportIsTrueTests(unittest.TestCase):

    def test_the_reported_input_reproduces_the_bug(self) -> None:
        for h in _runs():
            with self.subTest(hunt=h.id):
                self.assertTrue(try_input(h, h.reported).reproduced, h.id)

    def test_a_passing_input_does_not_count_as_reproducing(self) -> None:
        for h in _runs():
            outcome = run_cases(h, h.start)
            fine = next(r.args for r in outcome.results if r.passed)
            with self.subTest(hunt=h.id, args=fine):
                self.assertFalse(try_input(h, tuple(fine)).reproduced)


class ThereIsSomethingToLocateTests(unittest.TestCase):

    def test_the_program_is_long_enough_to_search(self) -> None:
        for h in ALL:
            with self.subTest(hunt=h.id):
                self.assertGreaterEqual(len(h.lines), MIN_LINES)

    def test_the_fix_changes_one_or_two_lines_in_place(self) -> None:
        for h in ALL:
            with self.subTest(hunt=h.id):
                before = h.start.rstrip("\n").split("\n")
                after = h.fixed.rstrip("\n").split("\n")
                self.assertEqual(len(before), len(after))
                self.assertIn(len(h.bug_lines), (1, 2))

    def test_the_bug_line_is_not_blank(self) -> None:
        for h in ALL:
            for n in h.bug_lines:
                with self.subTest(hunt=h.id, line=n):
                    self.assertTrue(h.lines[n - 1].strip())


class TheExplanationIsFairTests(unittest.TestCase):

    def test_the_cause_is_not_among_the_decoys(self) -> None:
        for h in ALL:
            with self.subTest(hunt=h.id):
                self.assertNotIn(h.cause, h.decoys)
                self.assertGreaterEqual(len(set(h.decoys)), 2)
                self.assertEqual(len(h.choices), len(set(h.decoys)) + 1)


if __name__ == "__main__":
    unittest.main()
