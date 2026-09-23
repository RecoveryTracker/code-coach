"""Change it: the four things a modify drill has to be.

A modify drill is easy to get subtly wrong in a way that still looks
fine on screen. Start from broken code and it is a Fix the bug drill
wearing the wrong name. Start from code that already does the new thing
and there is nothing to do. Ask only about the new behaviour and a
rewrite that throws the old behaviour away passes - the opposite of
what a team needs. Make the answer a rewrite and it is a kata in
disguise.

So each of those is a rule, checked by running the code rather than
reading it, through the same driver a student's code goes through.
"""

from __future__ import annotations

import dataclasses
import difflib
import unittest

from code_coach.engine import run_code
from code_coach.kata import harness, judge, katas
from code_coach.kata.modify import JAVASCRIPT, MODIFY, PYTHON

#: How many lines the model answer may add or remove, counted from the
#: start. Modify means edit: the largest change here is FizzBuzz growing
#: two new tests, which is four added lines. A drill needing much more
#: than that has stopped being a change and started being a rewrite.
MAX_CHANGED_LINES = 5

FAMILIES = (PYTHON, JAVASCRIPT)


def _run(k, code: str, *, oracle=None):
    """Run code through the kata driver, judged against an oracle.

    With no oracle it is judged against the drill's new requirement.
    Passing `before` judges it against the old one instead - the same
    kata with a different truth, which is all "the old requirement"
    means.
    """
    judged = dataclasses.replace(k, solve=oracle) if oracle else k
    out, err, code_ = run_code(harness(judged, code), language=k.language)
    return judge(judged, out, err, code_)


def _drills():
    return tuple(k for k in katas() if k.family in FAMILIES)


class RegisteredTests(unittest.TestCase):

    def test_every_drill_is_registered(self) -> None:
        """Written and not wired up is the failure that has cost this
        project the most time. Every drill in the file has to be one
        the app serves."""
        served = {k.id for k in katas()}
        for k in MODIFY:
            with self.subTest(drill=k.id):
                self.assertIn(k.id, served)

    def test_both_languages_have_some(self) -> None:
        for family in FAMILIES:
            with self.subTest(family=family):
                self.assertGreaterEqual(
                    len([k for k in _drills() if k.family == family]), 4)

    def test_every_drill_says_what_it_does_now_and_what_changed(self) -> None:
        """The screen shows what the program does today above the
        request, and the change once you pass. A drill missing either
        is a request with no context, or a pass with no lesson."""
        for k in _drills():
            with self.subTest(drill=k.id):
                self.assertTrue(k.was.strip())
                self.assertTrue(k.change.strip())
                self.assertTrue(k.start.strip())
                self.assertTrue(k.after.strip())
                self.assertIsNotNone(k.before)


class TheStartWorksTests(unittest.TestCase):
    """Rule one: you are changing working code, not fixing broken code."""

    def test_the_start_passes_every_case_under_the_old_requirement(self) -> None:
        for k in _drills():
            with self.subTest(drill=k.id):
                outcome = _run(k, k.start, oracle=k.before)
                self.assertEqual(outcome.broke, "", k.id)
                failed = [r.args for r in outcome.results if not r.passed]
                self.assertEqual(
                    failed, [],
                    f"{k.id}: the starting code is meant to be right for "
                    f"what it did before, and fails {failed[:3]}")


class ThereIsAChangeTests(unittest.TestCase):
    """Rule two: the request asks for something the code does not do."""

    def test_the_start_fails_the_new_requirement(self) -> None:
        for k in _drills():
            with self.subTest(drill=k.id):
                outcome = _run(k, k.start)
                self.assertFalse(
                    outcome.passed,
                    f"{k.id}: the starting code already does the new thing")

    def test_the_model_answer_passes_the_new_requirement(self) -> None:
        """And the answer shown is one that has been seen to pass."""
        for k in _drills():
            with self.subTest(drill=k.id):
                self.assertEqual(k.reference().strip(), k.after.strip())
                outcome = _run(k, k.reference())
                self.assertEqual(outcome.broke, "", k.id)
                failed = [
                    (r.args, r.got, r.want)
                    for r in outcome.results if not r.passed
                ]
                self.assertEqual(failed, [], f"{k.id}: {failed[:2]}")


class KeepWhatWorkedTests(unittest.TestCase):
    """Rule three: some cases have the same answer before and after.

    Without these, a rewrite that forgets the old behaviour entirely
    would pass - handle only the new case and the drill never notices.
    On a team that is the change that breaks something nobody asked
    you to touch, which is the habit this family exists to build.
    """

    def test_every_drill_has_cases_the_change_must_not_break(self) -> None:
        for k in _drills():
            with self.subTest(drill=k.id):
                kept = [
                    case for case in k.cases
                    if k.before(*case) == k.solve(*case)
                ]
                changed = [
                    case for case in k.cases
                    if k.before(*case) != k.solve(*case)
                ]
                self.assertTrue(kept, f"{k.id}: nothing the change must keep")
                self.assertTrue(changed, f"{k.id}: nothing the change alters")

    def test_breaking_the_old_behaviour_fails(self) -> None:
        """The rule above, shown to bite: a version that handles the new
        case and gets every old one wrong must not pass."""
        k = next(d for d in _drills() if d.id == "mod-greet")
        only_new = (
            "def greet(name):\n"
            "    return \"Hello, friend!\"\n"
        )
        outcome = _run(k, only_new)
        self.assertFalse(outcome.passed)


class TheChangeIsSmallTests(unittest.TestCase):
    """Rule four: modifying means editing, not rewriting."""

    def test_the_answer_is_a_few_lines_from_the_start(self) -> None:
        for k in _drills():
            with self.subTest(drill=k.id):
                diff = difflib.unified_diff(
                    k.start.strip().splitlines(),
                    k.after.strip().splitlines(),
                    lineterm="", n=0,
                )
                changed = [
                    line for line in diff
                    if line[:1] in "+-" and not line.startswith(("+++", "---"))
                ]
                self.assertLessEqual(
                    len(changed), MAX_CHANGED_LINES,
                    f"{k.id} changes {len(changed)} lines: {changed}")
                self.assertGreater(len(changed), 0, k.id)


class ServedTests(unittest.TestCase):
    """What reaches the screen: the context before, the lesson after."""

    def test_the_list_carries_what_it_does_now(self) -> None:
        from code_coach.api.server import kata_list

        listed = {
            entry["id"]: entry
            for family in kata_list()["families"]
            for entry in family["katas"]
        }
        for k in _drills():
            with self.subTest(drill=k.id):
                self.assertEqual(listed[k.id]["was"], k.was)
                self.assertEqual(listed[k.id]["start"], k.start)

    def test_the_change_is_sent_only_once_it_passes(self) -> None:
        """Like the name of a bug: reading it before you have found it
        yourself would give the drill away."""
        from code_coach.api.schemas import KataCheckRequest
        from code_coach.api.server import kata_check

        k = next(d for d in _drills() if d.id == "mod-grade")
        wrong = kata_check(KataCheckRequest(kata_id=k.id, code=k.start))
        self.assertFalse(wrong.passed)
        self.assertEqual(wrong.change, "")
        right = kata_check(KataCheckRequest(kata_id=k.id, code=k.after))
        self.assertTrue(right.passed)
        self.assertEqual(right.change, k.change)


if __name__ == "__main__":
    unittest.main()
