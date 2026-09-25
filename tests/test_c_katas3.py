"""The second Fix the bug: C set and the Change it: C drills, held to the same rules.

The rules are the ones in test_c_katas.py (for the bugs) and
test_dart_katas.py (for Change it), run against C_BUGS_2 and C_MODIFY
only, so this file passes whether or not the sets are registered yet.
"""

from __future__ import annotations

import dataclasses
import difflib
import inspect
import os
import shutil
import subprocess
import tempfile
import unittest

from code_coach.engine import c_available, run_code
from code_coach.kata import MARKER, judge
from code_coach.kata import c_harness as ch
from code_coach.kata.c_bugs2 import C_BUGS_2
from code_coach.kata.c_modify import C_MODIFY
from tests.test_c_katas import NEEDS_C, WARNINGS
from tests.test_kata import _is_edge

BUGS = "Fix the bug: C"
MODIFY = "Change it: C"
FAMILIES = {BUGS: C_BUGS_2, MODIFY: C_MODIFY}
MINE = C_BUGS_2 + C_MODIFY
MAX_CHANGED_LINES = 6


def _run(k, code: str, *, oracle=None):
    """Run C code for a kata, judged by its oracle (or another one)."""
    judged = k if oracle is None else dataclasses.replace(k, solve=oracle)
    out, err, rc = run_code(ch.harness(judged, code), language="c")
    if ch.missing(judged, out, err):
        return None
    return judge(judged, ch.unpack(judged, out, err, rc, MARKER), err, rc)


class ShapeTests(unittest.TestCase):
    """What can be checked by reading."""

    def test_each_set_has_six_and_is_in_the_right_family(self) -> None:
        prefixes = {BUGS: "c-bug-", MODIFY: "c-change-"}
        for family, found in FAMILIES.items():
            with self.subTest(family=family):
                self.assertEqual(len(found), 6)
                for k in found:
                    self.assertEqual(k.family, family, k.id)
                    self.assertEqual(k.language, "c", k.id)
                    self.assertTrue(k.id.startswith(prefixes[family]), k.id)

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

        mine = {k.id for k in MINE}
        # Every other kata, whether or not Dart or C is installed, and not
        # counting these sets twice once they are registered.
        others = {k.id: k for k in
                  katas() + DART_KATAS + DART_KATAS_2 + DART_BUGS + DART_BUGS_2
                  + DART_MODIFY + DART_MODIFY_2 + C_KATAS + C_BUGS
                  if k.id not in mine}
        everything = list(others.values()) + list(MINE)
        ids = [k.id for k in everything]
        names = [k.name for k in everything]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(names), len(set(names)))

    def test_every_kata_is_typed_in_what_the_driver_supports(self) -> None:
        params = {"int", "long long", "double", "bool", "char", "string",
                  "int[]", "string[]"}
        returns = {"int", "long long", "double", "bool", "char", "string", "int[]"}
        for k in MINE:
            with self.subTest(kata=k.id):
                self.assertEqual(len(k.types), len(k.params))
                self.assertTrue(set(k.types) <= params)
                self.assertIn(k.returns, returns)
                self.assertEqual(
                    len(inspect.signature(k.solve).parameters), len(k.params))
                if k.before is not None:
                    self.assertEqual(
                        len(inspect.signature(k.before).parameters), len(k.params))
                for case in k.cases:
                    self.assertEqual(len(case), len(k.params))

    def test_start_and_answer_open_on_the_signature(self) -> None:
        for k in MINE:
            with self.subTest(kata=k.id):
                sig = ch.signature(k)
                self.assertIn(sig, k.start)
                self.assertIn(sig, k.reference())
                self.assertNotIn("def ", k.reference())

    def test_the_answers_are_indented_by_two_or_four(self) -> None:
        for k in MINE:
            with self.subTest(kata=k.id):
                for line in (k.reference() + "\n" + k.start).splitlines():
                    indent = len(line) - len(line.lstrip(" "))
                    self.assertNotIn("\t", line)
                    self.assertTrue(indent % 2 == 0, line)

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

    def test_a_hand_written_answer_lands_on_an_awkward_input(self) -> None:
        for k in MINE:
            with self.subTest(kata=k.id):
                self.assertTrue(any(_is_edge(a) for args, _ in k.checks for a in args))

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
        for k in C_BUGS_2:
            with self.subTest(kata=k.id):
                self.assertTrue(k.start.strip() and k.bug.strip() and k.c_answer.strip())
                self.assertNotEqual(k.start.strip(), k.c_answer.strip())
                self.assertEqual((k.was, k.after, k.change), ("", "", ""))
                self.assertIsNone(k.before)
        for k in C_MODIFY:
            with self.subTest(kata=k.id):
                self.assertTrue(k.was.strip() and k.change.strip() and k.after.strip())
                self.assertIsNotNone(k.before)
                self.assertEqual(k.reference(), k.after.strip())
                self.assertEqual(k.bug, "")


class ChangeItShapeTests(unittest.TestCase):
    """The Change it rules that need no run."""

    def test_some_cases_keep_their_answer_and_some_change(self) -> None:
        for k in C_MODIFY:
            with self.subTest(kata=k.id):
                same = [c for c in k.cases if k.before(*c) == k.solve(*c)]
                moved = [c for c in k.cases if k.before(*c) != k.solve(*c)]
                self.assertTrue(same, f"{k.id}: every answer changes")
                self.assertTrue(moved, f"{k.id}: no answer changes")

    def test_the_answer_is_a_few_lines_from_the_start(self) -> None:
        for k in C_MODIFY:
            with self.subTest(kata=k.id):
                diff = difflib.unified_diff(
                    k.start.strip().splitlines(), k.after.strip().splitlines(),
                    lineterm="", n=0)
                changed = [line for line in diff
                           if line[:1] in "+-" and not line.startswith(("+++", "---"))]
                self.assertLessEqual(len(changed), MAX_CHANGED_LINES, k.id)
                self.assertGreater(len(changed), 0, k.id)


@unittest.skipUnless(c_available(), NEEDS_C)
class RunTests(unittest.TestCase):
    """Every C string, compiled and run against the oracle."""

    def test_every_worked_answer_passes_every_case(self) -> None:
        for k in MINE:
            with self.subTest(kata=k.id):
                outcome = _run(k, k.reference())
                self.assertIsNotNone(outcome, f"{k.id}: function not found")
                self.assertEqual(outcome.broke, "", k.id)
                failed = [(r.args, r.got, r.want, r.error)
                          for r in outcome.results if not r.passed]
                self.assertEqual(failed, [], k.id)

    def test_a_broken_start_really_is_broken(self) -> None:
        for k in C_BUGS_2:
            with self.subTest(kata=k.id):
                outcome = _run(k, k.start)
                self.assertIsNotNone(outcome, f"{k.id}: function not found")
                self.assertEqual(outcome.broke, "", k.id)
                self.assertFalse(any(r.error for r in outcome.results),
                                 f"{k.id}: the start errors or crashes")
                self.assertFalse(outcome.passed, f"{k.id} passes as given")
                self.assertTrue(any(r.passed for r in outcome.results),
                                f"{k.id}: the bug should hide on some inputs")

    def test_a_change_it_start_works_for_yesterday(self) -> None:
        for k in C_MODIFY:
            with self.subTest(kata=k.id):
                outcome = _run(k, k.start, oracle=k.before)
                self.assertIsNotNone(outcome, f"{k.id}: function not found")
                self.assertEqual(outcome.broke, "", k.id)
                self.assertTrue(outcome.passed, f"{k.id}: the start is not right "
                                                f"for the old requirement")

    def test_a_change_it_start_fails_today(self) -> None:
        for k in C_MODIFY:
            with self.subTest(kata=k.id):
                outcome = _run(k, k.start)
                self.assertIsNotNone(outcome, f"{k.id}: function not found")
                self.assertEqual(outcome.broke, "", k.id)
                self.assertFalse(any(r.error for r in outcome.results), k.id)
                self.assertFalse(outcome.passed, k.id)


@unittest.skipUnless(shutil.which("clang"), "needs clang for the warning check")
class WarningTests(unittest.TestCase):
    """Every start and every answer, compiled with every warning on, says nothing."""

    def test_every_start_and_answer_compiles_without_a_warning(self) -> None:
        clang = shutil.which("clang")
        with tempfile.TemporaryDirectory() as tmp:
            for k in MINE:
                for label, code in (("start", k.start), ("answer", k.reference())):
                    with self.subTest(kata=k.id, code=label):
                        path = os.path.join(tmp, f"{k.id}-{label}.c")
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(code + "\n")
                        done = subprocess.run([clang, *WARNINGS, path],
                                              capture_output=True, text=True, timeout=60)
                        self.assertEqual(done.returncode, 0, done.stderr)
                        self.assertEqual(done.stderr.strip(), "", k.id)


if __name__ == "__main__":
    unittest.main()
