"""Predict the output, in C: the snippets, and what C really prints.

The same rules as tests/test_predict.py, applied to the C set on its own.
It imports C_PUZZLES directly rather than going through `predict.PUZZLES`,
so these hold whether or not the set has been added to the Predict screen
yet — and once it has, the checks that look at the whole collection make
sure it went in cleanly: no id taken twice, and the family reporting C as
its language.

The load-bearing test is the one that runs each snippet. In C it has a
partner: a program with undefined behaviour can print the written answer
today and something else under the next compiler, so passing the run is
not enough. Each snippet also has to compile cleanly with the warnings
turned up, which is where a compiler says most of what it notices about
code that is not well-defined.

The engine compiles C with gcc or clang (`-std=c17`), and falls back to
MSVC on Windows. The engine has no `c_available()` helper, so the check
lives here: the run is skipped when none of the three is found, and the
warnings check when there is no gcc or clang to ask.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest

from code_coach.engine import msvc_available, run_code
from code_coach.kata.predict import PUZZLES, language_of, predict_families
from code_coach.kata.predict_c import C_PUZZLES

FAMILY = "C"

#: The compiler the engine would pick, in the engine's order.
_GCC_OR_CLANG = next(
    (c for c in ("gcc", "clang") if shutil.which(c)), None)


def c_available() -> bool:
    return _GCC_OR_CLANG is not None or msvc_available()


class CPuzzleTests(unittest.TestCase):
    @unittest.skipUnless(c_available(), "no C compiler (gcc, clang or MSVC)")
    def test_c_agrees_with_every_written_answer(self) -> None:
        for p in C_PUZZLES:
            with self.subTest(puzzle=p.id):
                stdout, stderr, code = run_code(p.code, language="c")
                self.assertEqual(code, 0, (stderr or stdout)[:300])
                self.assertEqual(
                    stdout.rstrip("\n"), p.expect,
                    f"{p.id}: C prints {stdout.rstrip()!r} "
                    f"and the file says {p.expect!r}")

    @unittest.skipUnless(_GCC_OR_CLANG, "no gcc or clang to ask for warnings")
    def test_every_snippet_compiles_without_a_warning(self) -> None:
        """The engine's flags plus -Wall -Wextra -pedantic. The engine
        discards a successful build's warnings, so a run that passes
        says nothing about them."""
        for p in C_PUZZLES:
            with self.subTest(puzzle=p.id):
                fd, path = tempfile.mkstemp(suffix=".c")
                try:
                    with os.fdopen(fd, "w", encoding="utf-8") as f:
                        f.write(p.code)
                    built = subprocess.run(
                        [_GCC_OR_CLANG, "-std=c17", "-Wall", "-Wextra",
                         "-pedantic", "-fsyntax-only", path],
                        capture_output=True, text=True, timeout=60)
                finally:
                    os.unlink(path)
                self.assertEqual(built.returncode, 0, built.stderr[:300])
                self.assertEqual(built.stderr.strip(), "", built.stderr[:300])

    def test_every_snippet_prints_something(self) -> None:
        """A puzzle whose answer is the empty string asks nothing."""
        for p in C_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.expect.strip())

    def test_every_puzzle_explains_itself(self) -> None:
        for p in C_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.name.strip())
                self.assertTrue(p.why.strip())
                self.assertEqual(p.family, FAMILY)
                self.assertEqual(p.language, "c")
                self.assertIn("printf(", p.code)

    def test_every_snippet_is_a_whole_short_program(self) -> None:
        """C needs an include and a main before it can print anything, so
        the cap is four lines above the Dart sets' twelve — the same
        amount of program, plus the ceremony."""
        for p in C_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.code.startswith("#include <stdio.h>\n"))
                self.assertIn("int main(void) {", p.code)
                lines = len(p.code.splitlines())
                self.assertGreaterEqual(lines, 5)
                self.assertLessEqual(lines, 16)

    def test_the_answer_is_not_sitting_in_the_snippet(self) -> None:
        """Only when the whole answer appears verbatim, which is the case
        that gives it away. Short answers are exempt, as in the other
        sets."""
        for p in C_PUZZLES:
            with self.subTest(puzzle=p.id):
                if len(p.expect) < 8:
                    continue
                self.assertNotIn(p.expect, p.code)

    def test_every_puzzle_is_named_once(self) -> None:
        ids = [p.id for p in C_PUZZLES]
        self.assertEqual(sorted(ids), sorted(set(ids)))

    def test_no_id_is_taken_from_another_set(self) -> None:
        """Checked against the registered puzzles without the C ones, so
        it means the same thing before and after they are added."""
        mine = {p.id for p in C_PUZZLES}
        others = {p.id for p in PUZZLES if p.language != "c"}
        self.assertFalse(mine & others)

    def test_the_family_is_not_claimed_by_another_language(self) -> None:
        """A family never mixes languages. If "C" is already on the
        Predict screen, it has to be these puzzles that put it there."""
        if FAMILY in predict_families():
            self.assertEqual(language_of(FAMILY), "c")


class CLevelTests(unittest.TestCase):
    """The order the set is read in, least surprising first."""

    def test_every_level_is_in_range(self) -> None:
        for p in C_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertIn(p.level, (1, 2, 3, 4, 5))

    def test_the_family_is_not_all_one_level(self) -> None:
        self.assertGreater(len({p.level for p in C_PUZZLES}), 1)

    def test_the_file_is_written_least_surprising_first(self) -> None:
        levels = [p.level for p in C_PUZZLES]
        self.assertEqual(levels, sorted(levels))


if __name__ == "__main__":
    unittest.main()
