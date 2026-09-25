"""Katas in Ruby: the same rules as every kata, run through Ruby.

Two families, each in its own file:

  "Ruby"                write the method - the Enumerable way
  "Fix the bug: Ruby"   the method arrives written and wrong

The worked answers live in dicts beside the katas (RUBY_ANSWERS and
RUBY_BUG_ANSWERS) until the Kata record has a field for them. Every one
is run through the Ruby driver against the Python oracle. Without Ruby
the run tests are skipped; the ones that only read the content still run.
"""

from __future__ import annotations

import inspect
import unittest

from code_coach.engine import run_code
from code_coach.kata import Kata, judge, katas
from code_coach.kata import ruby_harness as rh
from code_coach.kata.ruby_bugs import RUBY_BUG_ANSWERS, RUBY_BUGS
from code_coach.kata.ruby_katas import RUBY_ANSWERS, RUBY_KATAS
from tests.test_kata import _is_edge

WRITE = "Ruby"
BUGS = "Fix the bug: Ruby"
FAMILIES = {WRITE: RUBY_KATAS, BUGS: RUBY_BUGS}
ANSWERS = {**RUBY_ANSWERS, **RUBY_BUG_ANSWERS}


def _ruby_runs() -> bool:
    try:
        return run_code("puts 6 * 7", language="ruby")[0].strip() == "42"
    except Exception:  # noqa: BLE001 - no Ruby is a skip, not a failure
        return False


HAS_RUBY = _ruby_runs()
NEEDS_RUBY = "needs Ruby"


def _all() -> tuple[Kata, ...]:
    return RUBY_KATAS + RUBY_BUGS


def _run(k: Kata, code: str):
    out, err, code_ = run_code(rh.harness(k, code), language="ruby")
    return judge(k, out, rh.tidy(err), code_)


class ShapeTests(unittest.TestCase):
    """What can be checked by reading."""

    def test_each_family_has_its_katas_in_the_right_file(self) -> None:
        self.assertEqual(len(RUBY_KATAS), 10)
        self.assertEqual(len(RUBY_BUGS), 6)
        for family, found in FAMILIES.items():
            for k in found:
                with self.subTest(kata=k.id):
                    self.assertEqual(k.family, family)
                    self.assertEqual(k.language, "ruby")
                    self.assertTrue(k.id.startswith(
                        "rb-bug-" if family == BUGS else "rb-"))
        for k in RUBY_KATAS:
            self.assertFalse(k.id.startswith("rb-bug-"), k.id)

    def test_every_kata_has_exactly_one_answer(self) -> None:
        self.assertEqual(set(RUBY_ANSWERS), {k.id for k in RUBY_KATAS})
        self.assertEqual(set(RUBY_BUG_ANSWERS), {k.id for k in RUBY_BUGS})

    def test_ids_and_names_are_unique_across_every_kata(self) -> None:
        others = [k for k in katas() if k.language != "ruby"]
        ids = [k.id for k in others] + [k.id for k in _all()]
        names = [k.name for k in others] + [k.name for k in _all()]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(names), len(set(names)))

    def test_answers_and_starts_are_ruby_and_define_the_method(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                for code in filter(None, (ANSWERS[k.id], k.start)):
                    self.assertIn(f"def {k.name}(", code)
                    self.assertNotIn("function ", code)
                    self.assertNotIn(":\n", code.splitlines()[0] + "\n")
                    self.assertTrue(code.rstrip().endswith("end"))

    def test_the_parameters_match_the_oracle(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                self.assertEqual(
                    len(inspect.signature(k.solve).parameters), len(k.params))
                for case in k.cases:
                    self.assertEqual(len(case), len(k.params))

    def test_every_kata_says_what_it_needs_to(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                self.assertTrue(k.brief and k.example and k.hint)
                self.assertFalse(k.mutates)

    def test_the_oracle_agrees_with_answers_typed_by_a_person(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                self.assertTrue(k.checks, f"{k.id} has no hand-written answer")
                for args, want in k.checks:
                    self.assertIn(tuple(args), [tuple(c) for c in k.cases])
                    got = k.answer(args)
                    self.assertEqual(got, want, f"{k.id}{args}")
                    self.assertEqual(isinstance(got, bool), isinstance(want, bool))
                self.assertTrue(
                    any(_is_edge(a) for args, _ in k.checks for a in args),
                    f"{k.id}: no hand-written answer lands on an awkward input")

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

    def test_the_oracle_does_not_change_its_arguments(self) -> None:
        import copy

        for k in _all():
            with self.subTest(kata=k.id):
                for case in k.cases:
                    kept = copy.deepcopy(case)
                    k.solve(*case)
                    self.assertEqual(case, kept)

    def test_each_family_reads_easiest_first_and_is_not_all_one_level(self) -> None:
        for family, found in FAMILIES.items():
            levels = [k.level for k in found]
            with self.subTest(family=family):
                self.assertEqual(levels, sorted(levels))
                self.assertGreater(len(set(levels)), 1)
                self.assertTrue(all(1 <= lv <= 5 for lv in levels))

    def test_only_the_bug_family_starts_filled(self) -> None:
        for k in RUBY_KATAS:
            with self.subTest(kata=k.id):
                self.assertEqual((k.start, k.bug), ("", ""))
        for k in RUBY_BUGS:
            with self.subTest(kata=k.id):
                self.assertTrue(k.start.strip() and k.bug.strip())
                self.assertNotEqual(k.start.strip(), ANSWERS[k.id].strip())


@unittest.skipUnless(HAS_RUBY, NEEDS_RUBY)
class RunTests(unittest.TestCase):
    """Every Ruby string, run against the oracle."""

    def test_every_worked_answer_passes_every_case(self) -> None:
        for k in _all():
            with self.subTest(kata=k.id):
                outcome = _run(k, ANSWERS[k.id])
                self.assertEqual(outcome.broke, "", k.id)
                failed = [(r.args, r.got, r.want, r.error, r.changed)
                          for r in outcome.results if not r.passed]
                self.assertEqual(failed, [], k.id)

    def test_a_broken_start_really_is_broken(self) -> None:
        for k in RUBY_BUGS:
            with self.subTest(kata=k.id):
                outcome = _run(k, k.start)
                # It has to run: a start that does not parse teaches the
                # parser, not the bug.
                self.assertEqual(outcome.broke, "", k.id)
                self.assertFalse(outcome.passed, f"{k.id} passes as given")
                self.assertTrue(any(r.passed for r in outcome.results),
                                f"{k.id}: the bug should hide on some inputs")


if __name__ == "__main__":
    unittest.main()
