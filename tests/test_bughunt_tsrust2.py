"""The second set of TypeScript and Rust bug hunts, held to the same rules.

Run over TS_HUNTS_2 and RUST_HUNTS_2 directly (code_coach/bughunt/content10.py),
so the sets are checked on their own whether or not they are registered in
the collection yet. Each hunt has a hand-written oracle answer
(`checks`) and a hand-worked WRONG answer the broken program must give for
the reported input (BROKEN_GOT below): the real tsc/node and rustc run both.
"""

from __future__ import annotations

import unittest

from code_coach.bughunt import hunts, run_cases, try_input
from code_coach.bughunt.content10 import RUST_HUNTS_2, TS_HUNTS_2
from code_coach.engine import rust_available, typescript_available

MIN_LINES = 8

#: What the broken program returns for the reported input, worked out by
#: hand from how the language behaves - not copied from a run.
BROKEN_GOT = {
    # [10, 9, 1] sorted as text is "1" < "10" < "9"; the first two are 1, 10.
    "hunt-ts-sort-default": [1, 10],
    # slice(0, 3 - 1) of [1..5] is the first two.
    "hunt-ts-slice-end": [1, 2],
    # "" -> Number("") is 0, not NaN, so both boxes count.
    "hunt-ts-number-blank": 2,
    # floor(28.999999999999996) is 28.
    "hunt-ts-money-floor": 28,
    # every over-limit item overwrites found, so the last one (9) wins.
    "hunt-ts-foreach-return": 9,
    # both names push onto the one shared array.
    "hunt-ts-shared-default": [["new", "a", "b"], ["new", "a", "b"]],
    # integer-like keys first, ascending: 2, 10, then b.
    "hunt-ts-key-order": ["2", "10", "b"],
    # 3 / 2 is 1 in integers.
    "hunt-rs-int-average": 1.0,
    # 3 - 5 does not fit, so unwrap_or gives the old stock, 3.
    "hunt-rs-checked-sub": 3,
    # "one", "", "two".
    "hunt-rs-split-space": 3,
    # 0 is not > 0, so it is dropped.
    "hunt-rs-retain-zero": [5],
    # the first 'a' starts at 1 then +1 = 2; the second makes 3.
    "hunt-rs-or-insert": 3,
    # 95 matches 60..=100 first.
    "hunt-rs-match-order": "pass",
    # bytes A9 C3 66 61 63: A9 and C3 are each invalid on their own.
    "hunt-rs-bytes-rev": "��fac",
}


def _runnable(group):
    return tuple(h for h in group)


def setUpModule() -> None:
    if not (typescript_available() or rust_available()):
        raise unittest.SkipTest("neither tsc/node nor rustc is installed")


def _available(h) -> bool:
    return typescript_available() if h.language == "typescript" else rust_available()


ALL = TS_HUNTS_2 + RUST_HUNTS_2


def _runs():
    return tuple(h for h in ALL if _available(h))


class CollectionTests(unittest.TestCase):

    def test_there_are_seven_of_each(self) -> None:
        self.assertGreaterEqual(len(TS_HUNTS_2), 7)
        self.assertGreaterEqual(len(RUST_HUNTS_2), 7)
        for h in TS_HUNTS_2:
            self.assertEqual((h.family, h.language), ("TypeScript", "typescript"))
            self.assertTrue(h.id.startswith("hunt-ts-"), h.id)
        for h in RUST_HUNTS_2:
            self.assertEqual((h.family, h.language), ("Rust", "rust"))
            self.assertTrue(h.id.startswith("hunt-rs-"), h.id)
            self.assertEqual(len(h.types), len(h.params), h.id)
            self.assertTrue(h.returns, h.id)

    def test_ids_are_unique_and_new(self) -> None:
        ids = [h.id for h in ALL]
        self.assertEqual(len(ids), len(set(ids)))
        for h in ALL:
            others = [o for o in hunts() if o.id == h.id and o is not h]
            self.assertEqual(others, [], f"{h.id} is already used")
        from code_coach.bughunt.content_rust import RUST_HUNTS
        from code_coach.bughunt.content_ts import TS_HUNTS
        self.assertFalse({h.id for h in TS_HUNTS + RUST_HUNTS} & set(ids))

    def test_levels_are_spread_and_each_language_reads_easiest_first(self) -> None:
        for group in (TS_HUNTS_2, RUST_HUNTS_2):
            levels = [h.level for h in group]
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
