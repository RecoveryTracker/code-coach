"""Forms in Dart: the same rules as every kata, run through `dart run`.

Three families, each in its own file:

  "Dart"                write the function - collections, strings, maps,
                        null safety, the shapes Flutter code is made of
  "Fix the bug: Dart"   the function arrives written and wrong
  "Change it: Dart"     the function is right for yesterday; change it

The oracle is Python, as for every kata: the answers are numbers,
strings, lists, maps and booleans, which mean the same in both. What is
Dart is the worked answer, the start, and the run - every Dart string
here is compiled and run against the oracle, because an answer that was
only read is an answer that has not been checked.

Dart comes with Flutter and is not on every machine. Without it the
tests that run Dart are skipped rather than failed; the ones that only
read the content still run.
"""

from __future__ import annotations

import difflib
import inspect
import unittest

from code_coach.engine import dart_available, run_code
from code_coach.kata import Kata, harness, judge
from code_coach.kata.dart_bugs import DART_BUGS
from code_coach.kata.dart_katas import DART_KATAS
from code_coach.kata.dart_modify import DART_MODIFY
from tests.test_kata import _is_edge

WRITE = "Dart"
BUGS = "Fix the bug: Dart"
MODIFY = "Change it: Dart"
FAMILIES = {WRITE: DART_KATAS, BUGS: DART_BUGS, MODIFY: DART_MODIFY}
#: Same limit as the Python and JavaScript Change it drills.
MAX_CHANGED_LINES = 6
NEEDS_DART = "needs dart (it comes with Flutter)"


def _all() -> tuple[Kata, ...]:
    return DART_KATAS + DART_BUGS + DART_MODIFY


def _run(k: Kata, code: str, *, oracle=None):
    """Run Dart code for a kata, judged by its oracle (or another one)."""
    judged = k if oracle is None else Kata(
        id=k.id, name=k.name, brief=k.brief, params=k.params, cases=k.cases,
        solve=oracle, language="dart", types=k.types, returns=k.returns)
    out, err, code_ = run_code(harness(judged, code), language="dart")
    return judge(judged, out, err, code_)


class ShapeTests(unittest.TestCase):
    """What can be checked by reading."""

    def test_each_family_has_some_and_is_in_the_right_file(self) -> None:
        for family, found in FAMILIES.items():
            with self.subTest(family=family):
                self.assertGreaterEqual(len(found), 5, family)
                for k in found:
                    self.assertEqual(k.family, family, k.id)
                    self.assertEqual(k.language, "dart", k.id)

    def test_ids_and_names_are_unique_across_every_kata(self) -> None:
        from code_coach.kata import katas

        others = [k for k in katas() if k.language != "dart"]
        ids = [k.id for k in others] + [k.id for k in _all()]
        names = [k.name for k in others] + [k.name for k in _all()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(names), len(set(names)))

    def test_every_kata_is_typed(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                self.assertEqual(len(k.types), len(k.params))
                self.assertTrue(k.returns)
                self.assertEqual(
                    len(inspect.signature(k.solve).parameters), len(k.params))
                for case in k.cases:
                    self.assertEqual(len(case), len(k.params))

    def test_the_shown_answer_is_dart_and_defines_the_function(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                shown = k.reference()
                self.assertIn(f"{k.returns} {k.name}(", shown)
                self.assertNotIn("def ", shown)
                self.assertNotIn("function ", shown)

    def test_every_kata_says_what_it_needs_to(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                self.assertTrue(k.brief and k.example and k.hint)

    def test_the_oracle_agrees_with_answers_typed_by_a_person(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                self.assertTrue(k.checks, f"{k.id} has no hand-written answer")
                for args, want in k.checks:
                    self.assertIn(tuple(args), [tuple(c) for c in k.cases])
                    self.assertEqual(k.answer(args), want, f"{k.id}{args}")

    def test_the_cases_reach_an_edge(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                edges = sum(1 for case in k.cases for arg in case if _is_edge(arg))
                if not edges:
                    self.assertGreater(len(k.edge_note.split()), 6, k.id)

    def test_the_answers_are_not_all_the_same(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                self.assertGreater(len({repr(a) for a in k.expected()}), 1)

    def test_each_family_reads_easiest_first_and_is_not_all_one_level(self) -> None:
        for family, found in FAMILIES.items():
            levels = [k.level for k in found]
            with self.subTest(family=family):
                self.assertEqual(levels, sorted(levels))
                self.assertGreater(len(set(levels)), 1)
                self.assertTrue(all(1 <= lv <= 5 for lv in levels))

    def test_only_the_bug_and_change_families_start_filled(self) -> None:
        for k in DART_KATAS:
            with self.subTest(kata=k.id):
                self.assertEqual((k.start, k.bug), ("", ""))
        for k in DART_BUGS:
            with self.subTest(kata=k.id):
                self.assertIn(f"{k.returns} {k.name}(", k.start)
                self.assertTrue(k.bug.strip())
        for k in DART_MODIFY:
            with self.subTest(kata=k.id):
                self.assertIn(f"{k.returns} {k.name}(", k.start)
                self.assertTrue(k.was.strip() and k.change.strip() and k.after.strip())
                self.assertIsNotNone(k.before)


class ChangeItShapeTests(unittest.TestCase):
    """The Change it rules that need no run."""

    def test_some_cases_keep_their_answer_and_some_change(self) -> None:
        for k in DART_MODIFY:
            with self.subTest(kata=k.id):
                same = [c for c in k.cases if k.before(*c) == k.solve(*c)]
                moved = [c for c in k.cases if k.before(*c) != k.solve(*c)]
                self.assertTrue(same, f"{k.id}: every answer changes")
                self.assertTrue(moved, f"{k.id}: no answer changes")

    def test_the_answer_is_a_few_lines_from_the_start(self) -> None:
        for k in DART_MODIFY:
            with self.subTest(kata=k.id):
                diff = difflib.unified_diff(
                    k.start.strip().splitlines(), k.after.strip().splitlines(),
                    lineterm="", n=0)
                changed = [line for line in diff
                           if line[:1] in "+-" and not line.startswith(("+++", "---"))]
                self.assertLessEqual(len(changed), MAX_CHANGED_LINES, k.id)
                self.assertGreater(len(changed), 0, k.id)


@unittest.skipUnless(dart_available(), NEEDS_DART)
class RunTests(unittest.TestCase):
    """Every Dart string, compiled and run against the oracle."""

    def _passes(self, k: Kata, code: str) -> None:
        outcome = _run(k, code)
        self.assertEqual(outcome.broke, "", k.id)
        failed = [(r.args, r.got, r.want, r.error) for r in outcome.results if not r.passed]
        self.assertEqual(failed, [], k.id)

    def test_every_worked_answer_passes_every_case(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                self._passes(k, k.reference())

    def test_a_broken_start_really_is_broken(self) -> None:
        for k in DART_BUGS:
            with self.subTest(kata=k.id):
                outcome = _run(k, k.start)
                # It has to run: a start that does not compile teaches
                # the compiler, not the bug.
                self.assertEqual(outcome.broke, "", k.id)
                self.assertFalse(outcome.passed, f"{k.id} passes as given")
                self.assertTrue(any(r.passed for r in outcome.results),
                                f"{k.id}: the bug should hide on some inputs")

    def test_a_change_it_start_works_for_yesterday(self) -> None:
        for k in DART_MODIFY:
            with self.subTest(kata=k.id):
                outcome = _run(k, k.start, oracle=k.before)
                self.assertEqual(outcome.broke, "", k.id)
                self.assertTrue(outcome.passed, f"{k.id}: the start is not right "
                                                f"for the old requirement")

    def test_a_change_it_start_fails_today(self) -> None:
        for k in DART_MODIFY:
            with self.subTest(kata=k.id):
                self.assertFalse(_run(k, k.start).passed, k.id)


if __name__ == "__main__":
    unittest.main()
