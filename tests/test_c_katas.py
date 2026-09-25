"""Katas in C: the same rules as every kata, run through the C driver.

Two families, each in its own file:

  "C"                 write the function - arrays with a length, strings
                      up to '\\0', list results written into `out`
  "Fix the bug: C"    the function arrives written and wrong

Kata has no field for a C answer yet, so the worked answers sit beside
the katas in C_ANSWERS and C_BUG_ANSWERS, keyed by id. Every one is
compiled and run against the Python oracle, and compiled once more with
every warning turned on, because an answer that teaches C should not be
one the compiler complains about.

C needs a compiler. Without one the tests that run C are skipped; the
ones that only read the content still run.
"""

from __future__ import annotations

import inspect
import os
import shutil
import subprocess
import tempfile
import unittest

from code_coach.engine import c_available, run_code
from code_coach.kata import MARKER, Kata, judge
from code_coach.kata import c_harness as ch
from code_coach.kata.c_bugs import C_BUG_ANSWERS, C_BUGS
from code_coach.kata.c_katas import C_ANSWERS, C_KATAS
from tests.test_kata import _is_edge

WRITE = "C"
BUGS = "Fix the bug: C"
FAMILIES = {WRITE: C_KATAS, BUGS: C_BUGS}
ANSWERS = {**C_ANSWERS, **C_BUG_ANSWERS}
NEEDS_C = "needs a C compiler (gcc, clang or MSVC)"
WARNINGS = ("-std=c17", "-Wall", "-Wextra", "-pedantic", "-fsyntax-only")


def _all() -> tuple[Kata, ...]:
    return C_KATAS + C_BUGS


def _run(k: Kata, code: str):
    out, err, rc = run_code(ch.harness(k, code), language="c")
    if ch.missing(k, out, err):
        return None
    return judge(k, ch.unpack(k, out, err, rc, MARKER), err, rc)


class ShapeTests(unittest.TestCase):
    """What can be checked by reading."""

    def test_each_family_has_some_and_is_in_the_right_file(self) -> None:
        self.assertEqual(len(C_KATAS), 8)
        self.assertEqual(len(C_BUGS), 6)
        for family, found in FAMILIES.items():
            for k in found:
                with self.subTest(kata=k.id):
                    self.assertEqual(k.family, family)
                    self.assertEqual(k.language, "c")
                    self.assertTrue(k.id.startswith("c-"))

    def test_ids_and_names_are_unique_across_every_kata(self) -> None:
        from code_coach.kata import katas
        from code_coach.kata.dart_bugs import DART_BUGS
        from code_coach.kata.dart_bugs2 import DART_BUGS_2
        from code_coach.kata.dart_katas import DART_KATAS
        from code_coach.kata.dart_katas2 import DART_KATAS_2
        from code_coach.kata.dart_modify import DART_MODIFY
        from code_coach.kata.dart_modify2 import DART_MODIFY_2

        # katas() leaves Dart out on a machine without it; count it anyway.
        dart = (DART_KATAS + DART_KATAS_2 + DART_BUGS + DART_BUGS_2
                + DART_MODIFY + DART_MODIFY_2)
        others = {k.id: k for k in katas() + dart if k.language != "c"}.values()
        ids = [k.id for k in others] + [k.id for k in _all()]
        names = [k.name for k in others] + [k.name for k in _all()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(names), len(set(names)))

    def test_every_kata_has_an_answer_and_no_answer_is_spare(self) -> None:
        self.assertEqual(set(C_ANSWERS), {k.id for k in C_KATAS})
        self.assertEqual(set(C_BUG_ANSWERS), {k.id for k in C_BUGS})

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
                self.assertIn(sig, ANSWERS[k.id])
                if k.start:
                    self.assertIn(sig, k.start)

    def test_the_answers_are_indented_by_two_or_four(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                for line in ANSWERS[k.id].splitlines():
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

    def test_each_family_reads_easiest_first_and_is_not_all_one_level(self) -> None:
        for family, found in FAMILIES.items():
            levels = [k.level for k in found]
            with self.subTest(family=family):
                self.assertEqual(levels, sorted(levels))
                self.assertGreater(len(set(levels)), 1)
                self.assertTrue(all(1 <= lv <= 5 for lv in levels))

    def test_only_the_bug_family_starts_filled(self) -> None:
        for k in C_KATAS:
            with self.subTest(kata=k.id):
                self.assertEqual((k.start, k.bug), ("", ""))
        for k in C_BUGS:
            with self.subTest(kata=k.id):
                self.assertTrue(k.start.strip() and k.bug.strip())
                self.assertNotEqual(k.start.strip(), C_BUG_ANSWERS[k.id].strip())


@unittest.skipUnless(c_available(), NEEDS_C)
class RunTests(unittest.TestCase):
    """Every C string, compiled and run against the oracle."""

    def test_every_worked_answer_passes_every_case(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                outcome = _run(k, ANSWERS[k.id])
                self.assertIsNotNone(outcome, f"{k.id}: function not found")
                self.assertEqual(outcome.broke, "", k.id)
                failed = [(r.args, r.got, r.want, r.error)
                          for r in outcome.results if not r.passed]
                self.assertEqual(failed, [], k.id)

    def test_a_broken_start_really_is_broken(self) -> None:
        for k in C_BUGS:
            with self.subTest(kata=k.id):
                outcome = _run(k, k.start)
                self.assertIsNotNone(outcome, f"{k.id}: function not found")
                # It has to compile and run: no crash, no compile error.
                self.assertEqual(outcome.broke, "", k.id)
                self.assertFalse(any(r.error for r in outcome.results),
                                 f"{k.id}: the start errors or crashes")
                self.assertFalse(outcome.passed, f"{k.id} passes as given")
                self.assertTrue(any(r.passed for r in outcome.results),
                                f"{k.id}: the bug should hide on some inputs")


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
                        f.write(ANSWERS[k.id])
                    done = subprocess.run([clang, *WARNINGS, path],
                                          capture_output=True, text=True, timeout=60)
                    self.assertEqual(done.returncode, 0, done.stderr)
                    self.assertEqual(done.stderr.strip(), "", k.id)


if __name__ == "__main__":
    unittest.main()
