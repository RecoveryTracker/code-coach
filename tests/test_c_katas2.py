"""The second shelf of C katas, held to the same rules as the first.

Each worked answer rides on its Kata as `c_answer`. Every one is
compiled and run against the Python oracle through the C driver, and
compiled once more with every warning on. Without a compiler the run
tests skip; the reading tests still run.
"""

from __future__ import annotations

import inspect
import os
import shutil
import subprocess
import tempfile
import unittest

from code_coach.engine import c_available
from code_coach.kata import Kata
from code_coach.kata import c_harness as ch
from code_coach.kata.c_katas2 import C_ANSWERS_2, C_KATAS_2
from tests.test_c_katas import NEEDS_C, WARNINGS, WRITE, _run
from tests.test_kata import _is_edge

EARLIER = ("c-array-sum", "c-string-length", "c-max-or-zero", "c-digit-sum",
           "c-reverse-into", "c-clamp-into", "c-reads-both-ways", "c-count-words")


def _all() -> tuple[Kata, ...]:
    return C_KATAS_2


class ShapeTests(unittest.TestCase):
    """What can be checked by reading."""

    def test_ten_of_them_all_in_the_write_family(self) -> None:
        self.assertEqual(len(C_KATAS_2), 10)
        for k in C_KATAS_2:
            with self.subTest(kata=k.id):
                self.assertEqual(k.family, WRITE)
                self.assertEqual(k.language, "c")
                self.assertTrue(k.id.startswith("c-"))
                self.assertNotIn(k.id, EARLIER)

    def test_ids_and_names_are_unique_across_every_kata(self) -> None:
        from code_coach.kata import katas
        from code_coach.kata.c_bugs import C_BUGS
        from code_coach.kata.c_katas import C_KATAS
        from code_coach.kata.dart_bugs import DART_BUGS
        from code_coach.kata.dart_bugs2 import DART_BUGS_2
        from code_coach.kata.dart_katas import DART_KATAS
        from code_coach.kata.dart_katas2 import DART_KATAS_2
        from code_coach.kata.dart_modify import DART_MODIFY
        from code_coach.kata.dart_modify2 import DART_MODIFY_2

        dart = (DART_KATAS + DART_KATAS_2 + DART_BUGS + DART_BUGS_2
                + DART_MODIFY + DART_MODIFY_2)
        others = {k.id: k for k in katas() + dart if k.language != "c"}.values()
        every = list(others) + list(C_KATAS + C_BUGS + C_KATAS_2)
        ids = [k.id for k in every]
        names = [k.name for k in every]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(names), len(set(names)))

    def test_every_kata_carries_its_answer_and_none_is_spare(self) -> None:
        self.assertEqual(set(C_ANSWERS_2), {k.id for k in C_KATAS_2})
        for k in C_KATAS_2:
            with self.subTest(kata=k.id):
                self.assertEqual(k.c_answer, C_ANSWERS_2[k.id])

    def test_every_kata_is_typed_in_what_the_driver_supports(self) -> None:
        params = {"int", "long long", "double", "bool", "char", "string",
                  "int[]", "string[]"}
        returns = {"int", "long long", "double", "bool", "char", "string", "int[]"}
        for k in _all():
            with self.subTest(kata=k.id):
                self.assertEqual(len(k.types), len(k.params))
                self.assertTrue(set(k.types) <= params)
                self.assertIn(k.returns, returns)
                self.assertEqual(
                    len(inspect.signature(k.solve).parameters), len(k.params))
                for case in k.cases:
                    self.assertEqual(len(case), len(k.params))

    def test_the_answer_opens_on_the_signature_the_learner_sees(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                sig = ch.signature(k)
                self.assertIn(k.name, sig)
                self.assertIn(sig, k.c_answer)

    def test_the_answers_are_indented_by_two_or_four(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                for line in k.c_answer.splitlines():
                    indent = len(line) - len(line.lstrip(" "))
                    self.assertNotIn("\t", line)
                    self.assertTrue(indent % 2 == 0, line)

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

    def test_a_hand_written_answer_lands_on_an_awkward_input(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                self.assertTrue(any(_is_edge(a) for args, _ in k.checks for a in args))

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

    def test_reads_easiest_first_and_is_not_all_one_level(self) -> None:
        levels = [k.level for k in C_KATAS_2]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)
        self.assertTrue(all(1 <= lv <= 5 for lv in levels))

    def test_none_starts_filled(self) -> None:
        for k in C_KATAS_2:
            with self.subTest(kata=k.id):
                self.assertEqual((k.start, k.bug), ("", ""))


@unittest.skipUnless(c_available(), NEEDS_C)
class RunTests(unittest.TestCase):
    """Every answer, compiled and run against the oracle."""

    def test_every_worked_answer_passes_every_case(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                outcome = _run(k, k.c_answer)
                self.assertIsNotNone(outcome, f"{k.id}: function not found")
                self.assertEqual(outcome.broke, "", k.id)
                failed = [(r.args, r.got, r.want, r.error)
                          for r in outcome.results if not r.passed]
                self.assertEqual(failed, [], k.id)


@unittest.skipUnless(shutil.which("clang"), "needs clang for the warning check")
class WarningTests(unittest.TestCase):
    """Every answer, compiled with every warning on, says nothing."""

    def test_every_answer_compiles_without_a_warning(self) -> None:
        clang = shutil.which("clang")
        with tempfile.TemporaryDirectory() as tmp:
            for k in _all():
                with self.subTest(kata=k.id):
                    path = os.path.join(tmp, f"{k.id}.c")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(k.c_answer)
                    done = subprocess.run([clang, *WARNINGS, path],
                                          capture_output=True, text=True, timeout=60)
                    self.assertEqual(done.returncode, 0, done.stderr)
                    self.assertEqual(done.stderr.strip(), "", k.id)


if __name__ == "__main__":
    unittest.main()
