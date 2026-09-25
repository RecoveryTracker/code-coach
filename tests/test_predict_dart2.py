"""Predict the output, in Dart, second set: the same rules as
tests/test_predict_dart.py, applied to DART_PUZZLES_2 on its own.

It imports the set directly, so these hold whether or not it has been
registered on the Predict screen yet. The load-bearing test runs each
snippet and compares with the hand-typed answer; it is skipped when the
Dart SDK is not on the PATH.
"""

from __future__ import annotations

import unittest

from code_coach.engine import dart_available, run_code
from code_coach.kata.predict import PUZZLES, language_of, predict_families
from code_coach.kata.predict_dart import DART_PUZZLES
from code_coach.kata.predict_dart2 import DART_PUZZLES_2

FAMILY = "Dart"


class DartPuzzle2Tests(unittest.TestCase):
    @unittest.skipUnless(dart_available(), "the Dart SDK is not on PATH")
    def test_dart_agrees_with_every_written_answer(self) -> None:
        for p in DART_PUZZLES_2:
            with self.subTest(puzzle=p.id):
                stdout, stderr, code = run_code(p.code, language="dart")
                self.assertEqual(code, 0, (stderr or stdout)[:300])
                self.assertEqual(
                    stdout.rstrip("\n"), p.expect,
                    f"{p.id}: Dart prints {stdout.rstrip()!r} "
                    f"and the file says {p.expect!r}")

    def test_every_snippet_prints_something(self) -> None:
        """A puzzle whose answer is the empty string asks nothing."""
        for p in DART_PUZZLES_2:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.expect.strip())

    def test_every_puzzle_explains_itself(self) -> None:
        for p in DART_PUZZLES_2:
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
        for p in DART_PUZZLES_2:
            with self.subTest(puzzle=p.id):
                self.assertIn("void main() {", p.code)
                lines = len(p.code.splitlines())
                self.assertGreaterEqual(lines, 4)
                self.assertLessEqual(lines, 12)

    def test_the_answer_is_not_sitting_in_the_snippet(self) -> None:
        """Only when the whole answer appears verbatim, which is the case
        that gives it away. Short answers are exempt, as in the Python
        and JavaScript sets."""
        for p in DART_PUZZLES_2:
            with self.subTest(puzzle=p.id):
                if len(p.expect) < 8:
                    continue
                self.assertNotIn(p.expect, p.code)

    def test_every_puzzle_is_named_once(self) -> None:
        ids = [p.id for p in DART_PUZZLES_2]
        self.assertEqual(sorted(ids), sorted(set(ids)))

    def test_no_id_is_taken_from_another_set(self) -> None:
        """Checked against the registered puzzles without the Dart ones,
        so it means the same thing before and after they are added."""
        mine = {p.id for p in DART_PUZZLES_2}
        others = {p.id for p in PUZZLES if p not in DART_PUZZLES_2}
        self.assertFalse(mine & others)

    def test_no_id_is_taken_from_the_first_dart_set(self) -> None:
        mine = {p.id for p in DART_PUZZLES_2}
        self.assertFalse(mine & {p.id for p in DART_PUZZLES})

    def test_the_family_is_not_claimed_by_another_language(self) -> None:
        """A family never mixes languages. If "Dart" is already on the
        Predict screen, it has to be these puzzles that put it there."""
        if FAMILY in predict_families():
            self.assertEqual(language_of(FAMILY), "dart")


class DartLevel2Tests(unittest.TestCase):
    """The order the set is read in, least surprising first."""

    def test_every_level_is_in_range(self) -> None:
        for p in DART_PUZZLES_2:
            with self.subTest(puzzle=p.id):
                self.assertIn(p.level, (1, 2, 3, 4, 5))

    def test_the_family_is_not_all_one_level(self) -> None:
        self.assertGreater(len({p.level for p in DART_PUZZLES_2}), 1)

    def test_the_file_is_written_least_surprising_first(self) -> None:
        """The screen sorts by level anyway. This asks the file to read
        in the same order, so the order it was written in and the order
        it is shown in are one order."""
        levels = [p.level for p in DART_PUZZLES_2]
        self.assertEqual(levels, sorted(levels))


if __name__ == "__main__":
    unittest.main()
