"""The second Fix the bug: Dart and Change it: Dart sets, held to the same rules.

The rules are the ones in test_dart_katas.py, run against DART_BUGS_2
and DART_MODIFY_2 only, so this file passes whether or not the sets are
registered yet.
"""

from __future__ import annotations

import difflib
import inspect
import unittest

from code_coach.engine import dart_available
from code_coach.kata.dart_bugs2 import DART_BUGS_2
from code_coach.kata.dart_modify2 import DART_MODIFY_2
from tests.test_dart_katas import BUGS, MAX_CHANGED_LINES, MODIFY, NEEDS_DART, _run
from tests.test_kata import _is_edge

FAMILIES = {BUGS: DART_BUGS_2, MODIFY: DART_MODIFY_2}
MINE = DART_BUGS_2 + DART_MODIFY_2


class ShapeTests(unittest.TestCase):
    """What can be checked by reading."""

    def test_each_set_has_some_and_is_in_the_right_family(self) -> None:
        for family, found in FAMILIES.items():
            with self.subTest(family=family):
                self.assertGreaterEqual(len(found), 5)
                for k in found:
                    self.assertEqual(k.family, family, k.id)
                    self.assertEqual(k.language, "dart", k.id)
                    self.assertTrue(k.id.startswith("dart-"), k.id)

    def test_ids_and_names_are_unique_across_every_kata(self) -> None:
        from code_coach.kata import katas
        from code_coach.kata.dart_bugs import DART_BUGS
        from code_coach.kata.dart_katas import DART_KATAS
        from code_coach.kata.dart_katas2 import DART_KATAS_2
        from code_coach.kata.dart_modify import DART_MODIFY

        mine = {k.id for k in MINE}
        # Every other kata, whether or not Dart is installed, and not
        # counting these sets twice once they are registered.
        others = {k.id: k for k in
                  katas() + DART_KATAS + DART_KATAS_2 + DART_BUGS + DART_MODIFY
                  if k.id not in mine}
        everything = list(others.values()) + list(MINE)
        ids = [k.id for k in everything]
        names = [k.name for k in everything]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(names), len(set(names)))

    def test_every_kata_is_typed(self) -> None:
        for k in MINE:
            with self.subTest(kata=k.id):
                self.assertEqual(len(k.types), len(k.params))
                self.assertTrue(k.returns)
                self.assertEqual(
                    len(inspect.signature(k.solve).parameters), len(k.params))
                for case in k.cases:
                    self.assertEqual(len(case), len(k.params))
                if k.before is not None:
                    self.assertEqual(
                        len(inspect.signature(k.before).parameters),
                        len(k.params))

    def test_the_shown_answer_is_dart_and_defines_the_function(self) -> None:
        for k in MINE:
            with self.subTest(kata=k.id):
                shown = k.reference()
                self.assertIn(f"{k.returns} {k.name}(", shown)
                self.assertNotIn("def ", shown)
                self.assertNotIn("function ", shown)

    def test_every_kata_says_what_it_needs_to(self) -> None:
        for k in MINE:
            with self.subTest(kata=k.id):
                self.assertTrue(k.brief and k.example and k.hint)

    def test_the_oracle_agrees_with_answers_typed_by_a_person(self) -> None:
        for k in MINE:
            with self.subTest(kata=k.id):
                self.assertTrue(k.checks, f"{k.id} has no hand-written answer")
                for args, want in k.checks:
                    self.assertIn(tuple(args), [tuple(c) for c in k.cases])
                    self.assertEqual(k.answer(args), want, f"{k.id}{args}")

    def test_the_cases_reach_an_edge(self) -> None:
        for k in MINE:
            with self.subTest(kata=k.id):
                edges = sum(1 for case in k.cases for arg in case if _is_edge(arg))
                if not edges:
                    self.assertGreater(len(k.edge_note.split()), 6, k.id)

    def test_the_answers_are_not_all_the_same(self) -> None:
        for k in MINE:
            with self.subTest(kata=k.id):
                self.assertGreater(len({repr(a) for a in k.expected()}), 1)

    def test_each_set_reads_easiest_first_and_is_not_all_one_level(self) -> None:
        for family, found in FAMILIES.items():
            levels = [k.level for k in found]
            with self.subTest(family=family):
                self.assertEqual(levels, sorted(levels))
                self.assertGreater(len(set(levels)), 1)
                self.assertTrue(all(1 <= lv <= 5 for lv in levels))

    def test_both_sets_start_filled(self) -> None:
        for k in DART_BUGS_2:
            with self.subTest(kata=k.id):
                self.assertIn(f"{k.returns} {k.name}(", k.start)
                self.assertTrue(k.bug.strip())
        for k in DART_MODIFY_2:
            with self.subTest(kata=k.id):
                self.assertIn(f"{k.returns} {k.name}(", k.start)
                self.assertTrue(k.was.strip() and k.change.strip() and k.after.strip())
                self.assertIsNotNone(k.before)


class ChangeItShapeTests(unittest.TestCase):
    """The Change it rules that need no run."""

    def test_some_cases_keep_their_answer_and_some_change(self) -> None:
        for k in DART_MODIFY_2:
            with self.subTest(kata=k.id):
                same = [c for c in k.cases if k.before(*c) == k.solve(*c)]
                moved = [c for c in k.cases if k.before(*c) != k.solve(*c)]
                self.assertTrue(same, f"{k.id}: every answer changes")
                self.assertTrue(moved, f"{k.id}: no answer changes")

    def test_the_answer_is_a_few_lines_from_the_start(self) -> None:
        for k in DART_MODIFY_2:
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

    def _passes(self, k, code: str) -> None:
        outcome = _run(k, code)
        self.assertEqual(outcome.broke, "", k.id)
        failed = [(r.args, r.got, r.want, r.error) for r in outcome.results if not r.passed]
        self.assertEqual(failed, [], k.id)

    def test_every_worked_answer_passes_every_case(self) -> None:
        for k in MINE:
            with self.subTest(kata=k.id):
                self._passes(k, k.reference())

    def test_a_broken_start_really_is_broken(self) -> None:
        for k in DART_BUGS_2:
            with self.subTest(kata=k.id):
                outcome = _run(k, k.start)
                self.assertEqual(outcome.broke, "", k.id)
                self.assertFalse(outcome.passed, f"{k.id} passes as given")
                self.assertTrue(any(r.passed for r in outcome.results),
                                f"{k.id}: the bug should hide on some inputs")

    def test_a_change_it_start_works_for_yesterday(self) -> None:
        for k in DART_MODIFY_2:
            with self.subTest(kata=k.id):
                outcome = _run(k, k.start, oracle=k.before)
                self.assertEqual(outcome.broke, "", k.id)
                self.assertTrue(outcome.passed, f"{k.id}: the start is not right "
                                                f"for the old requirement")

    def test_a_change_it_start_fails_today(self) -> None:
        for k in DART_MODIFY_2:
            with self.subTest(kata=k.id):
                self.assertFalse(_run(k, k.start).passed, k.id)


if __name__ == "__main__":
    unittest.main()
