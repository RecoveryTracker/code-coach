"""Bug Hunt: the rules that make a hunt honest, and the routes that run it.

A hunt can look fine on screen and be worthless, in a few specific
ways, and each is a rule here:

* the bug is not real - the broken program passes everything, or the
  fixed one does not;
* the bug does not hide - every input shows it, so "reproduce" is a
  button you press rather than a thing you work out;
* the report is not true - the input it describes does not show the bug;
* there is nothing to locate - a program so short the answer is the
  only line, or a fix that rewrites half of it so "the line" means
  nothing;
* the explanation gives itself away - the cause repeated in the decoys.

All of it is checked by running code through the same driver a
student's goes through, and the oracle is held to answers a person
worked out by hand.
"""

from __future__ import annotations

import unittest

from code_coach.bughunt import (
    BadInput,
    hunt,
    hunt_families,
    hunts,
    parse_args,
    run_cases,
    try_input,
)

#: Below this there is nothing to locate. The shortest hunt here is ten
#: lines, with a helper and a constant to look past.
MIN_LINES = 8


def _runnable():
    """The hunts this machine can run. Dart comes with Flutter and is not
    everywhere; without it the Dart hunts are skipped rather than failed."""
    from code_coach.engine import dart_available

    return tuple(h for h in hunts() if h.language != "dart" or dart_available())


class CollectionTests(unittest.TestCase):

    def test_every_language_has_some(self) -> None:
        from code_coach.engine import dart_available

        want = {"Python", "JavaScript"} | ({"Dart"} if dart_available() else set())
        self.assertEqual(set(hunt_families()), want)
        for family in hunt_families():
            with self.subTest(family=family):
                self.assertGreaterEqual(len(hunts(family)), 3)

    def test_ids_are_unique_and_findable(self) -> None:
        ids = [h.id for h in hunts()]
        self.assertEqual(len(ids), len(set(ids)))
        for h in hunts():
            with self.subTest(hunt=h.id):
                self.assertIs(hunt(h.id), h)

    def test_a_family_reads_easiest_first_and_is_not_all_one_level(self) -> None:
        for family in hunt_families():
            levels = [h.level for h in hunts(family)]
            with self.subTest(family=family):
                self.assertEqual(levels, sorted(levels))
                self.assertGreater(len(set(levels)), 1)

    def test_every_hunt_says_everything_it_needs_to(self) -> None:
        for h in hunts():
            with self.subTest(hunt=h.id):
                for text in (h.title, h.report, h.cause, h.lesson, h.hint):
                    self.assertTrue(text.strip())


class TheOracleTests(unittest.TestCase):
    """The oracle decides everything, so it answers to a person."""

    def test_the_oracle_agrees_with_answers_worked_out_by_hand(self) -> None:
        for h in hunts():
            with self.subTest(hunt=h.id):
                self.assertTrue(h.checks, f"{h.id} has no hand-written answer")
                for args, want in h.checks:
                    self.assertEqual(h.answer(args), want, f"{h.id}{args}")

    def test_the_report_is_one_of_the_hand_checked_inputs(self) -> None:
        """The reported input is the one everything turns on, so it is
        the one a person has to have worked out."""
        for h in hunts():
            with self.subTest(hunt=h.id):
                self.assertIn(tuple(h.reported), [tuple(a) for a, _ in h.checks])


class TheBugIsRealTests(unittest.TestCase):

    def test_the_fixed_program_passes_every_case(self) -> None:
        for h in _runnable():
            with self.subTest(hunt=h.id):
                outcome = run_cases(h, h.fixed)
                self.assertEqual(outcome.broke, "", h.id)
                failed = [r.args for r in outcome.results if not r.passed]
                self.assertEqual(failed, [], f"{h.id}: {failed}")

    def test_the_broken_program_fails_some_case(self) -> None:
        for h in _runnable():
            with self.subTest(hunt=h.id):
                self.assertFalse(run_cases(h, h.start).passed, h.id)


class TheBugHidesTests(unittest.TestCase):
    """Some cases pass on the broken program.

    Without them any input reproduces the bug, and the first step is a
    button. With them you have to think about what the report is
    telling you - and the fix is also held to keeping them right, so a
    fix that patches the symptom and breaks what worked fails.
    """

    def test_some_cases_pass_on_the_broken_program(self) -> None:
        for h in _runnable():
            with self.subTest(hunt=h.id):
                outcome = run_cases(h, h.start)
                passing = [r for r in outcome.results if r.passed]
                self.assertTrue(passing, f"{h.id}: every input shows the bug")

    def test_a_fix_that_only_patches_the_symptom_fails(self) -> None:
        """Shown once, on the hunt built for it: asking last_page for
        one page further on fixes seven results and breaks three."""
        h = hunt("hunt-last-page")
        patched = h.start.replace(
            "return page(items, page_count(items))",
            "return page(items, page_count(items) + 1)",
        )
        self.assertNotEqual(patched, h.start)
        outcome = run_cases(h, patched)
        self.assertFalse(outcome.passed)
        seven = next(r for r in outcome.results if r.args == ([1, 2, 3, 4, 5, 6, 7],))
        self.assertTrue(seven.passed, "the symptom patch should fix the report")


class TheReportIsTrueTests(unittest.TestCase):

    def test_the_reported_input_reproduces_the_bug(self) -> None:
        for h in _runnable():
            with self.subTest(hunt=h.id):
                self.assertTrue(try_input(h, h.reported).reproduced, h.id)

    def test_a_passing_input_does_not_count_as_reproducing(self) -> None:
        """Any input that shows the bug counts - and one that does not
        must not, or the step says "found it" for nothing."""
        for h in _runnable():
            outcome = run_cases(h, h.start)
            fine = next(r.args for r in outcome.results if r.passed)
            with self.subTest(hunt=h.id, args=fine):
                self.assertFalse(try_input(h, tuple(fine)).reproduced)


class ThereIsSomethingToLocateTests(unittest.TestCase):

    def test_the_program_is_long_enough_to_search(self) -> None:
        for h in hunts():
            with self.subTest(hunt=h.id):
                self.assertGreaterEqual(len(h.lines), MIN_LINES)

    def test_the_fix_changes_one_or_two_lines_in_place(self) -> None:
        """Same number of lines, one or two of them different. That is
        what lets the line to click be computed from the fix rather than
        typed in, so the two can never disagree."""
        for h in hunts():
            with self.subTest(hunt=h.id):
                before = h.start.rstrip("\n").split("\n")
                after = h.fixed.rstrip("\n").split("\n")
                self.assertEqual(len(before), len(after))
                self.assertIn(len(h.bug_lines), (1, 2))

    def test_the_bug_line_is_not_blank(self) -> None:
        for h in hunts():
            for n in h.bug_lines:
                with self.subTest(hunt=h.id, line=n):
                    self.assertTrue(h.lines[n - 1].strip())


class TheExplanationIsFairTests(unittest.TestCase):

    def test_the_cause_is_not_among_the_decoys(self) -> None:
        for h in hunts():
            with self.subTest(hunt=h.id):
                self.assertNotIn(h.cause, h.decoys)
                self.assertGreaterEqual(len(set(h.decoys)), 2)
                self.assertEqual(len(h.choices), len(set(h.decoys)) + 1)


class ParseArgsTests(unittest.TestCase):

    def test_it_reads_what_people_type(self) -> None:
        self.assertEqual(parse_args("100", 1), (100,))
        self.assertEqual(parse_args("[1, 2, 3]", 1), ([1, 2, 3],))
        self.assertEqual(parse_args('"flour", true', 2), ("flour", True))
        self.assertEqual(parse_args("'flour', True", 2), ("flour", True))
        self.assertEqual(parse_args("None", 1), (None,))

    def test_the_wrong_number_of_arguments_says_so(self) -> None:
        with self.assertRaises(BadInput) as caught:
            parse_args("1, 2", 1, "average")
        self.assertIn("average takes 1 argument", str(caught.exception))

    def test_code_is_never_run(self) -> None:
        """literal_eval reads literals and nothing else."""
        for text in ("__import__('os').getcwd()", "print(1)", "open('x')"):
            with self.subTest(text=text):
                with self.assertRaises(BadInput):
                    parse_args(text, 1)

    def test_a_value_the_function_cannot_take_is_refused_not_marked(self) -> None:
        with self.assertRaises(BadInput):
            try_input(hunt("hunt-free-shipping"), ("text",))


class RouteTests(unittest.TestCase):

    def test_the_list_carries_no_answers(self) -> None:
        """The fixed program is the whole answer in one field - the easy
        one to leave in by accident."""
        from code_coach.api.server import bughunt_list

        for family in bughunt_list()["families"]:
            for entry in family["hunts"]:
                with self.subTest(hunt=entry["id"]):
                    for leaked in ("fixed", "cause", "lesson", "bug_lines",
                                   "reported", "solve"):
                        self.assertNotIn(leaked, entry)
                    found = hunt(entry["id"])
                    self.assertNotIn(found.fixed, entry.values())

    def test_trying_an_input_reports_what_it_gave(self) -> None:
        from code_coach.api.schemas import BugHuntTryRequest
        from code_coach.api.server import bughunt_try

        got = bughunt_try(BugHuntTryRequest(hunt_id="hunt-free-shipping", args="[100]"))
        self.assertTrue(got.reproduced)
        self.assertEqual((got.got, got.want), (107, 100))
        self.assertEqual(got.call, "order_total([100])")
        bad = bughunt_try(BugHuntTryRequest(hunt_id="hunt-free-shipping", args="oops"))
        self.assertFalse(bad.reproduced)
        self.assertTrue(bad.problem)

    def test_the_line_and_cause_are_marked_without_being_given_away(self) -> None:
        from code_coach.api.schemas import BugHuntCauseRequest, BugHuntLineRequest
        from code_coach.api.server import bughunt_cause, bughunt_line

        h = hunt("hunt-last-page")
        right = bughunt_line(BugHuntLineRequest(hunt_id=h.id, line=h.bug_lines[0]))
        wrong = bughunt_line(BugHuntLineRequest(hunt_id=h.id, line=16))
        self.assertTrue(right.right)
        self.assertFalse(wrong.right)
        self.assertIsNone(wrong.reveal, "a wrong guess must not reveal the line")
        shown = bughunt_line(BugHuntLineRequest(hunt_id=h.id, line=0))
        self.assertEqual(shown.reveal, list(h.bug_lines))

        miss = bughunt_cause(BugHuntCauseRequest(hunt_id=h.id, cause=h.decoys[0]))
        self.assertFalse(miss.right)
        self.assertIsNone(miss.reveal)
        hit = bughunt_cause(BugHuntCauseRequest(hunt_id=h.id, cause=h.cause))
        self.assertTrue(hit.right)

    def test_the_fix_is_marked_and_counted_only_when_it_passes(self) -> None:
        from code_coach.api.schemas import BugHuntFixRequest
        from code_coach.api.server import _store, bughunt_fix

        h = hunt("hunt-js-weekend")
        broken = bughunt_fix(BugHuntFixRequest(hunt_id=h.id, code=h.start))
        self.assertFalse(broken.passed)
        self.assertEqual((broken.cause, broken.lesson), ("", ""))
        self.assertEqual(_store.load().bughunt_counts().get(h.id, 0), 0)

        fixed = bughunt_fix(BugHuntFixRequest(hunt_id=h.id, code=h.fixed))
        self.assertTrue(fixed.passed)
        self.assertEqual(fixed.cause, h.cause)
        self.assertEqual(fixed.done, 1)
        self.assertEqual(_store.load().bughunt_counts()[h.id], 1)

    def test_an_unknown_hunt_is_a_404(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.server import bughunt_answer

        with self.assertRaises(HTTPException) as caught:
            bughunt_answer(hunt_id="no-such-hunt")
        self.assertEqual(caught.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
