"""Predict the output, in Dart: the snippets, and what Dart really prints.

The same rules as tests/test_predict.py, applied to the Dart set on its
own. It imports DART_PUZZLES directly rather than going through
`predict.PUZZLES`, so these hold whether or not the set has been added to
the Predict screen yet — and once it has, the checks that look at the
whole collection make sure it went in cleanly: no id taken twice, and the
family reporting Dart as its language.

The load-bearing test is the one that runs each snippet, and it runs the
same way round as the rest of predict. The answer is whatever Dart does,
so what can go wrong is the hand-typed copy, or a snippet edited until it
no longer shows what its explanation says. Running it is what catches
both. It is skipped when the Dart SDK is not on the PATH, since there is
then nothing to ask.
"""

from __future__ import annotations

import unittest

from code_coach.engine import dart_available, run_code
from code_coach.kata.predict import PUZZLES, language_of, predict_families
from code_coach.kata.predict_dart import DART_PUZZLES

FAMILY = "Dart"


class DartPuzzleTests(unittest.TestCase):
    @unittest.skipUnless(dart_available(), "the Dart SDK is not on PATH")
    def test_dart_agrees_with_every_written_answer(self) -> None:
        for p in DART_PUZZLES:
            with self.subTest(puzzle=p.id):
                stdout, stderr, code = run_code(p.code, language="dart")
                self.assertEqual(code, 0, (stderr or stdout)[:300])
                self.assertEqual(
                    stdout.rstrip("\n"), p.expect,
                    f"{p.id}: Dart prints {stdout.rstrip()!r} "
                    f"and the file says {p.expect!r}")

    def test_every_snippet_prints_something(self) -> None:
        """A puzzle whose answer is the empty string asks nothing."""
        for p in DART_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.expect.strip())

    def test_every_puzzle_explains_itself(self) -> None:
        for p in DART_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.name.strip())
                self.assertTrue(p.why.strip())
                self.assertEqual(p.family, FAMILY)
                self.assertEqual(p.language, "dart")
                self.assertIn("print(", p.code)

    def test_every_snippet_is_a_whole_short_program(self) -> None:
        """Dart will not run a bare statement, so each one needs a main —
        and short enough to hold in your head at once, which is the
        point of the mode."""
        for p in DART_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertIn("void main() {", p.code)
                lines = len(p.code.splitlines())
                self.assertGreaterEqual(lines, 4)
                self.assertLessEqual(lines, 12)

    def test_the_answer_is_not_sitting_in_the_snippet(self) -> None:
        """Only when the whole answer appears verbatim, which is the case
        that gives it away. Short answers are exempt, as in the Python
        and JavaScript sets."""
        for p in DART_PUZZLES:
            with self.subTest(puzzle=p.id):
                if len(p.expect) < 8:
                    continue
                self.assertNotIn(p.expect, p.code)

    def test_every_puzzle_is_named_once(self) -> None:
        ids = [p.id for p in DART_PUZZLES]
        self.assertEqual(sorted(ids), sorted(set(ids)))

    def test_no_id_is_taken_from_another_set(self) -> None:
        """Checked against the registered puzzles without the Dart ones,
        so it means the same thing before and after they are added."""
        mine = {p.id for p in DART_PUZZLES}
        others = {p.id for p in PUZZLES if p.language != "dart"}
        self.assertFalse(mine & others)

    def test_the_family_is_not_claimed_by_another_language(self) -> None:
        """A family never mixes languages. If "Dart" is already on the
        Predict screen, it has to be these puzzles that put it there."""
        if FAMILY in predict_families():
            self.assertEqual(language_of(FAMILY), "dart")


class DartLevelTests(unittest.TestCase):
    """The order the set is read in, least surprising first."""

    def test_every_level_is_in_range(self) -> None:
        for p in DART_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertIn(p.level, (1, 2, 3, 4, 5))

    def test_the_family_is_not_all_one_level(self) -> None:
        self.assertGreater(len({p.level for p in DART_PUZZLES}), 1)

    def test_the_file_is_written_least_surprising_first(self) -> None:
        """The screen sorts by level anyway. This asks the file to read
        in the same order, so the order it was written in and the order
        it is shown in are one order."""
        levels = [p.level for p in DART_PUZZLES]
        self.assertEqual(levels, sorted(levels))


if __name__ == "__main__":
    unittest.main()
