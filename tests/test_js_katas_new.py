"""The new JavaScript content, held to the same rules as every kata.

Two tuples: "Fix the bug: JavaScript" (js_bugs.py) and the third set of
"JavaScript" katas (js_katas3.py). Every JavaScript string here is run
through the real JS driver against the Python oracle - an answer that
was only read is an answer that has not been checked.
"""

from __future__ import annotations

import inspect
import unittest

from code_coach.engine import run_code
from code_coach.kata import Kata, harness, judge
from code_coach.kata.js_bugs import JS_BUGS
from code_coach.kata.js_katas3 import JS_KATAS_3
from tests.test_kata import _is_edge

FAMILIES = {"Fix the bug: JavaScript": JS_BUGS, "JavaScript": JS_KATAS_3}


def _all() -> tuple[Kata, ...]:
    return JS_BUGS + JS_KATAS_3


def _run(k: Kata, code: str):
    out, err, exit_code = run_code(harness(k, code), language="javascript")
    return judge(k, out, err, exit_code)


class ShapeTests(unittest.TestCase):
    """What can be checked by reading."""

    def test_each_family_has_some_and_is_in_the_right_file(self) -> None:
        for family, found in FAMILIES.items():
            with self.subTest(family=family):
                self.assertGreaterEqual(len(found), 5)
                for k in found:
                    self.assertEqual(k.family, family, k.id)
                    self.assertEqual(k.language, "javascript", k.id)
                    self.assertFalse(k.mutates, k.id)

    def test_ids_follow_the_family(self) -> None:
        for k in JS_BUGS:
            self.assertTrue(k.id.startswith("js-bug-"), k.id)
        for k in JS_KATAS_3:
            self.assertTrue(k.id.startswith("js-") and not k.id.startswith("js-bug-"), k.id)

    def test_ids_and_names_are_unique_across_every_kata(self) -> None:
        from code_coach.kata import katas

        mine = {k.id for k in _all()}
        others = [k for k in katas() if k.id not in mine]
        ids = [k.id for k in others] + [k.id for k in _all()]
        names = [k.name for k in others] + [k.name for k in _all()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(names), len(set(names)))

    def test_the_signature_matches_the_oracle(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                self.assertEqual(len(inspect.signature(k.solve).parameters), len(k.params))
                for case in k.cases:
                    self.assertEqual(len(case), len(k.params))

    def test_the_shown_answer_is_javascript_and_defines_the_function(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                shown = k.reference()
                self.assertIn(f"function {k.name}(", shown)
                self.assertNotIn("def ", shown)
                self.assertEqual(k.signature, f"function {k.name}({', '.join(k.params)}) {{")

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
                    got = k.answer(args)
                    self.assertEqual(got, want, f"{k.id}{args}")
                    self.assertEqual(isinstance(got, bool), isinstance(want, bool))
                if not k.edge_note:
                    self.assertTrue(
                        any(any(_is_edge(a) for a in args) for args, _ in k.checks),
                        f"{k.id}: no hand-written answer on an awkward input")

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
        for k in JS_KATAS_3:
            with self.subTest(kata=k.id):
                self.assertEqual((k.start, k.bug), ("", ""))
        for k in JS_BUGS:
            with self.subTest(kata=k.id):
                self.assertIn(f"function {k.name}(", k.start)
                self.assertTrue(k.bug.strip())
                self.assertNotEqual(k.start.strip(), k.js_answer.strip())

    def test_the_new_katas_do_not_repeat_the_existing_ones(self) -> None:
        from code_coach.kata import katas

        mine = {k.id for k in _all()}
        existing = {k.js_answer.strip() for k in katas("JavaScript") if k.id not in mine}
        for k in JS_KATAS_3:
            self.assertNotIn(k.js_answer.strip(), existing, k.id)


class RunTests(unittest.TestCase):
    """Every JavaScript string, run through the driver against the oracle."""

    def test_every_worked_answer_passes_every_case(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                outcome = _run(k, k.reference())
                self.assertEqual(outcome.broke, "", k.id)
                failed = [(r.args, r.got, r.want, r.error, r.changed)
                          for r in outcome.results if not r.passed]
                self.assertEqual(failed, [], k.id)

    def test_a_broken_start_really_is_broken(self) -> None:
        for k in JS_BUGS:
            with self.subTest(kata=k.id):
                outcome = _run(k, k.start)
                # It has to run: a start with a syntax error teaches the
                # parser, not the bug.
                self.assertEqual(outcome.broke, "", k.id)
                self.assertFalse(outcome.passed, f"{k.id} passes as given")
                self.assertTrue(any(r.passed for r in outcome.results),
                                f"{k.id}: the bug should hide on some inputs")


if __name__ == "__main__":
    unittest.main()
