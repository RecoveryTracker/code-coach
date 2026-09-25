"""The second set of Dart write-a-function katas, held to the same rules.

The rules are the ones in test_dart_katas.py, run against DART_KATAS_2
only, so this file passes whether or not the set is registered yet.
"""

from __future__ import annotations

import inspect
import unittest

from code_coach.engine import dart_available
from code_coach.kata.dart_katas2 import DART_KATAS_2
from tests.test_dart_katas import NEEDS_DART, WRITE, _run
from tests.test_kata import _is_edge


class ShapeTests(unittest.TestCase):
    """What can be checked by reading."""

    def test_there_are_some_and_they_are_in_the_right_family(self) -> None:
        self.assertGreaterEqual(len(DART_KATAS_2), 5)
        for k in DART_KATAS_2:
            with self.subTest(kata=k.id):
                self.assertEqual(k.family, WRITE)
                self.assertEqual(k.language, "dart")
                self.assertTrue(k.id.startswith("dart-"))

    def test_ids_and_names_are_unique_across_every_kata(self) -> None:
        from code_coach.kata import katas
        from code_coach.kata.dart_bugs import DART_BUGS
        from code_coach.kata.dart_katas import DART_KATAS
        from code_coach.kata.dart_modify import DART_MODIFY

        mine = {k.id for k in DART_KATAS_2}
        # Every other kata, whether or not Dart is installed, and not
        # counting this set twice once it is registered.
        others = {k.id: k for k in katas() + DART_KATAS + DART_BUGS + DART_MODIFY
                  if k.id not in mine}
        everything = list(others.values()) + list(DART_KATAS_2)
        ids = [k.id for k in everything]
        names = [k.name for k in everything]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(names), len(set(names)))

    def test_every_kata_is_typed(self) -> None:
        for k in DART_KATAS_2:
            with self.subTest(kata=k.id):
                self.assertEqual(len(k.types), len(k.params))
                self.assertTrue(k.returns)
                self.assertEqual(
                    len(inspect.signature(k.solve).parameters), len(k.params))
                for case in k.cases:
                    self.assertEqual(len(case), len(k.params))

    def test_the_shown_answer_is_dart_and_defines_the_function(self) -> None:
        for k in DART_KATAS_2:
            with self.subTest(kata=k.id):
                shown = k.reference()
                self.assertIn(f"{k.returns} {k.name}(", shown)
                self.assertNotIn("def ", shown)
                self.assertNotIn("function ", shown)

    def test_every_kata_says_what_it_needs_to(self) -> None:
        for k in DART_KATAS_2:
            with self.subTest(kata=k.id):
                self.assertTrue(k.brief and k.example and k.hint)

    def test_the_oracle_agrees_with_answers_typed_by_a_person(self) -> None:
        for k in DART_KATAS_2:
            with self.subTest(kata=k.id):
                self.assertTrue(k.checks, f"{k.id} has no hand-written answer")
                for args, want in k.checks:
                    self.assertIn(tuple(args), [tuple(c) for c in k.cases])
                    self.assertEqual(k.answer(args), want, f"{k.id}{args}")

    def test_the_cases_reach_an_edge(self) -> None:
        for k in DART_KATAS_2:
            with self.subTest(kata=k.id):
                edges = sum(1 for case in k.cases for arg in case if _is_edge(arg))
                if not edges:
                    self.assertGreater(len(k.edge_note.split()), 6, k.id)

    def test_the_answers_are_not_all_the_same(self) -> None:
        for k in DART_KATAS_2:
            with self.subTest(kata=k.id):
                self.assertGreater(len({repr(a) for a in k.expected()}), 1)

    def test_reads_easiest_first_and_is_not_all_one_level(self) -> None:
        levels = [k.level for k in DART_KATAS_2]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)
        self.assertTrue(all(1 <= lv <= 5 for lv in levels))

    def test_they_start_empty(self) -> None:
        for k in DART_KATAS_2:
            with self.subTest(kata=k.id):
                self.assertEqual((k.start, k.bug), ("", ""))


@unittest.skipUnless(dart_available(), NEEDS_DART)
class RunTests(unittest.TestCase):
    """Every worked answer, compiled and run against the oracle."""

    def test_every_worked_answer_passes_every_case(self) -> None:
        for k in DART_KATAS_2:
            with self.subTest(kata=k.id):
                outcome = _run(k, k.reference())
                self.assertEqual(outcome.broke, "", k.id)
                failed = [(r.args, r.got, r.want, r.error)
                          for r in outcome.results if not r.passed]
                self.assertEqual(failed, [], k.id)


if __name__ == "__main__":
    unittest.main()
