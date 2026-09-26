"""Predict the output, in Ruby: the snippets, and what Ruby really prints.

The same rules as tests/test_predict.py, applied to the Ruby set on its
own. It imports RUBY_PUZZLES directly rather than going through
`predict.PUZZLES`, so these hold whether or not the set has been added to
the Predict screen yet — and once it has, the checks that look at the
whole collection make sure it went in cleanly: no id taken twice, and the
family reporting Ruby as its language.

The load-bearing test is the one that runs each snippet. It has already
caught one: `defined?(String)` was written down as "expression", and
Ruby says "constant". The run is skipped, not failed, on a machine
without Ruby.
"""

from __future__ import annotations

import unittest

from code_coach.engine import ruby_available, run_code
from code_coach.kata.predict import PUZZLES, language_of, predict_families
from code_coach.kata.predict_ruby import RUBY_PUZZLES

FAMILY = "Ruby"
#: Any of Ruby's three ways to print.
PRINTS = ("puts", "print", "p ", "p(")


class RubyPuzzleTests(unittest.TestCase):
    @unittest.skipUnless(ruby_available(), "Ruby is not installed")
    def test_ruby_agrees_with_every_written_answer(self) -> None:
        for p in RUBY_PUZZLES:
            with self.subTest(puzzle=p.id):
                stdout, stderr, code = run_code(p.code, language="ruby")
                self.assertEqual(code, 0, (stderr or stdout)[:300])
                self.assertEqual(
                    stdout.replace("\r\n", "\n").rstrip("\n"), p.expect,
                    f"{p.id}: Ruby prints {stdout.rstrip()!r} "
                    f"and the file says {p.expect!r}")

    @unittest.skipUnless(ruby_available(), "Ruby is not installed")
    def test_nothing_is_said_on_stderr(self) -> None:
        """A snippet that prints a warning beside its answer is showing
        the reader something the answer box does not ask about."""
        for p in RUBY_PUZZLES:
            with self.subTest(puzzle=p.id):
                _, stderr, _ = run_code(p.code, language="ruby")
                self.assertEqual(stderr.strip(), "")

    def test_every_snippet_prints_something(self) -> None:
        """A puzzle whose answer is the empty string asks nothing."""
        for p in RUBY_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.expect.strip())

    def test_every_puzzle_explains_itself(self) -> None:
        for p in RUBY_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.name.strip())
                self.assertTrue(p.why.strip())
                self.assertEqual(p.family, FAMILY)
                self.assertEqual(p.language, "ruby")
                self.assertTrue(any(word in p.code for word in PRINTS))

    def test_every_snippet_is_short(self) -> None:
        for p in RUBY_PUZZLES:
            with self.subTest(puzzle=p.id):
                lines = len(p.code.splitlines())
                self.assertGreaterEqual(lines, 3)
                self.assertLessEqual(lines, 12)

    def test_the_answer_is_not_sitting_in_the_snippet(self) -> None:
        """Only when the whole answer appears verbatim, which is the case
        that gives it away. Short answers are exempt, as in the other
        sets."""
        for p in RUBY_PUZZLES:
            with self.subTest(puzzle=p.id):
                if len(p.expect) < 8:
                    continue
                self.assertNotIn(p.expect, p.code)

    def test_there_are_twelve(self) -> None:
        self.assertEqual(len(RUBY_PUZZLES), 12)

    def test_every_puzzle_is_named_once(self) -> None:
        ids = [p.id for p in RUBY_PUZZLES]
        self.assertEqual(sorted(ids), sorted(set(ids)))

    def test_no_id_is_taken_from_another_set(self) -> None:
        """Checked against the registered puzzles without the Ruby ones,
        so it means the same thing before and after they are added."""
        mine = {p.id for p in RUBY_PUZZLES}
        others = {p.id for p in PUZZLES if p.language != "ruby"}
        self.assertFalse(mine & others)

    def test_the_family_is_not_claimed_by_another_language(self) -> None:
        if FAMILY in predict_families():
            self.assertEqual(language_of(FAMILY), "ruby")


class RubyLevelTests(unittest.TestCase):
    """The order the set is read in, least surprising first."""

    def test_every_level_is_in_range(self) -> None:
        for p in RUBY_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertIn(p.level, (1, 2, 3, 4, 5))

    def test_the_family_is_not_all_one_level(self) -> None:
        self.assertGreater(len({p.level for p in RUBY_PUZZLES}), 1)

    def test_the_file_is_written_least_surprising_first(self) -> None:
        levels = [p.level for p in RUBY_PUZZLES]
        self.assertEqual(levels, sorted(levels))


if __name__ == "__main__":
    unittest.main()
