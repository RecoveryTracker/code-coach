"""The game-code bug hunts, held to the rules every hunt keeps.

The same rules as tests/test_bughunt.py and tests/test_bughunt_js3.py -
the bug is real, it hides, the report is true, there is a line to find,
the explanation is fair - run over JS_GAME_HUNTS directly, so the set is
checked on its own whether or not it has been added to the collection
yet. The route checks patch it into the collection for their duration.
"""

from __future__ import annotations

import contextlib
import unittest
from unittest import mock

import code_coach.bughunt as bughunt_module
from code_coach.bughunt import hunt, run_cases, try_input
from code_coach.bughunt.content_jsgame import GAME, JS_GAME_HUNTS

#: Below this there is nothing to locate - the same floor as the others.
MIN_LINES = 8

HUNTS = JS_GAME_HUNTS


def _others() -> tuple:
    return tuple(h for h in bughunt_module.hunts() if h not in HUNTS)


@contextlib.contextmanager
def _registered():
    """The collection as it will be once the set is registered."""
    real = bughunt_module._all

    def with_mine():
        have = {h.id for h in real()}
        return (*real(), *(h for h in HUNTS if h.id not in have))

    with mock.patch.object(bughunt_module, "_all", with_mine):
        yield


class CollectionTests(unittest.TestCase):

    def test_there_are_twelve_to_twenty_javascript_hunts(self) -> None:
        self.assertGreaterEqual(len(HUNTS), 12)
        self.assertLessEqual(len(HUNTS), 20)
        for h in HUNTS:
            with self.subTest(hunt=h.id):
                self.assertEqual((h.family, h.language), (GAME, "javascript"))
                self.assertTrue(h.id.startswith("hunt-jsg-"))

    def test_ids_are_unique_and_new(self) -> None:
        ids = [h.id for h in HUNTS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertFalse({h.id for h in _others()} & set(ids),
                         "an id is already used")

    def test_they_read_easiest_first_and_are_not_all_one_level(self) -> None:
        levels = [h.level for h in HUNTS]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)

    def test_every_hunt_says_everything_it_needs_to(self) -> None:
        for h in HUNTS:
            with self.subTest(hunt=h.id):
                for text in (h.title, h.report, h.cause, h.lesson, h.hint):
                    self.assertTrue(text.strip())

    def test_nothing_needs_a_browser(self) -> None:
        for h in HUNTS:
            with self.subTest(hunt=h.id):
                for word in ("document", "window", "requestAnimationFrame"):
                    self.assertNotIn(word, h.start)


class TheOracleTests(unittest.TestCase):

    def test_the_oracle_agrees_with_answers_worked_out_by_hand(self) -> None:
        for h in HUNTS:
            with self.subTest(hunt=h.id):
                self.assertTrue(h.checks, f"{h.id} has no hand-written answer")
                for args, want in h.checks:
                    self.assertEqual(h.answer(args), want, f"{h.id}{args}")

    def test_the_report_is_one_of_the_hand_checked_inputs(self) -> None:
        for h in HUNTS:
            with self.subTest(hunt=h.id):
                self.assertIn(tuple(h.reported), [tuple(a) for a, _ in h.checks])


class TheBugIsRealTests(unittest.TestCase):

    def test_the_fixed_program_passes_every_case(self) -> None:
        for h in HUNTS:
            with self.subTest(hunt=h.id):
                outcome = run_cases(h, h.fixed)
                self.assertEqual(outcome.broke, "", h.id)
                failed = [r.args for r in outcome.results if not r.passed]
                self.assertEqual(failed, [], f"{h.id}: {failed}")

    def test_the_broken_program_fails_some_case(self) -> None:
        for h in HUNTS:
            with self.subTest(hunt=h.id):
                self.assertFalse(run_cases(h, h.start).passed, h.id)


class TheBugHidesTests(unittest.TestCase):

    def test_some_cases_pass_on_the_broken_program(self) -> None:
        for h in HUNTS:
            with self.subTest(hunt=h.id):
                outcome = run_cases(h, h.start)
                self.assertEqual(outcome.broke, "", h.id)
                passing = [r for r in outcome.results if r.passed]
                self.assertTrue(passing, f"{h.id}: every input shows the bug")


class TheReportIsTrueTests(unittest.TestCase):

    def test_the_reported_input_reproduces_the_bug(self) -> None:
        for h in HUNTS:
            with self.subTest(hunt=h.id):
                self.assertTrue(try_input(h, h.reported).reproduced, h.id)

    def test_a_passing_input_does_not_count_as_reproducing(self) -> None:
        for h in HUNTS:
            outcome = run_cases(h, h.start)
            fine = next(r.args for r in outcome.results if r.passed)
            with self.subTest(hunt=h.id, args=fine):
                self.assertFalse(try_input(h, tuple(fine)).reproduced)

    def test_the_missing_velocity_comes_back_as_nan(self) -> None:
        """NaN has no JSON spelling and arrives as null - the coin is not
        somewhere else, it is nowhere."""
        h = next(h for h in HUNTS if h.id == "hunt-jsg-coins-vanish")
        self.assertEqual(try_input(h, h.reported).got, [[None, None]])

    def test_the_lost_this_is_a_crash_not_a_wrong_number(self) -> None:
        h = next(h for h in HUNTS if h.id == "hunt-jsg-score-screen-crash")
        attempt = try_input(h, h.reported)
        self.assertTrue(attempt.reproduced)
        self.assertIn("TypeError", attempt.error)

    def test_no_hunt_changes_what_it_was_handed(self) -> None:
        """survivors copies the list before culling it; a fix that
        spliced the caller's array would be caught by the driver."""
        for h in HUNTS:
            with self.subTest(hunt=h.id):
                outcome = run_cases(h, h.fixed)
                self.assertFalse(any(r.changed for r in outcome.results))


class ThereIsSomethingToLocateTests(unittest.TestCase):

    def test_the_program_is_long_enough_to_search(self) -> None:
        for h in HUNTS:
            with self.subTest(hunt=h.id):
                self.assertGreaterEqual(len(h.lines), MIN_LINES)

    def test_the_fix_changes_one_line_in_place(self) -> None:
        for h in HUNTS:
            with self.subTest(hunt=h.id):
                before = h.start.rstrip("\n").split("\n")
                after = h.fixed.rstrip("\n").split("\n")
                self.assertEqual(len(before), len(after))
                self.assertEqual(len(h.bug_lines), 1)

    def test_the_bug_line_is_not_blank(self) -> None:
        for h in HUNTS:
            for n in h.bug_lines:
                with self.subTest(hunt=h.id, line=n):
                    self.assertTrue(h.lines[n - 1].strip())

    def test_the_cause_is_in_a_helper_not_the_called_function(self) -> None:
        """The report is about the function you call; the bug line sits
        above that function's definition, in something it uses."""
        for h in HUNTS:
            with self.subTest(hunt=h.id):
                start = next(i + 1 for i, line in enumerate(h.lines)
                             if line.startswith(f"function {h.name}("))
                self.assertTrue(all(n < start for n in h.bug_lines))


class TheExplanationIsFairTests(unittest.TestCase):

    def test_the_cause_is_not_among_the_decoys(self) -> None:
        for h in HUNTS:
            with self.subTest(hunt=h.id):
                self.assertNotIn(h.cause, h.decoys)
                self.assertGreaterEqual(len(set(h.decoys)), 2)
                self.assertEqual(len(h.choices), len(set(h.decoys)) + 1)


class RouteTests(unittest.TestCase):

    def test_listed_under_their_family_without_the_answers(self) -> None:
        from code_coach.api.server import bughunt_list

        with _registered():
            served = bughunt_list()
        family = next(f for f in served["families"] if f["name"] == GAME)
        self.assertEqual([e["id"] for e in family["hunts"]],
                         [h.id for h in HUNTS])
        for entry in family["hunts"]:
            with self.subTest(hunt=entry["id"]):
                self.assertEqual(entry["language"], "javascript")
                for leaked in ("fixed", "cause", "lesson", "bug_lines",
                               "reported", "solve"):
                    self.assertNotIn(leaked, entry)

    def test_findable_and_the_line_and_cause_are_marked(self) -> None:
        from code_coach.api.schemas import BugHuntCauseRequest, BugHuntLineRequest
        from code_coach.api.server import bughunt_cause, bughunt_line

        with _registered():
            for h in HUNTS:
                with self.subTest(hunt=h.id):
                    self.assertIs(hunt(h.id), h)
                    right = bughunt_line(
                        BugHuntLineRequest(hunt_id=h.id, line=h.bug_lines[0]))
                    self.assertTrue(right.right)
                    hit = bughunt_cause(
                        BugHuntCauseRequest(hunt_id=h.id, cause=h.cause))
                    self.assertTrue(hit.right)
                    miss = bughunt_cause(
                        BugHuntCauseRequest(hunt_id=h.id, cause=h.decoys[0]))
                    self.assertFalse(miss.right)


if __name__ == "__main__":
    unittest.main()
