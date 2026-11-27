"""C Algorithm Code, the typing set in code_coach/typing/snippets_calgo.py.

The same guards the Python, JavaScript and Dart themed sets keep: every
character on the keyboard, a note on everything, no stray whitespace, lengths
inside the C pool's range, nothing already in C Code. C cannot parse a single
statement on its own, so the lines are held to what they contain; the blocks
are whole programs, and each is built warning-free under strict flags, run,
and held to the answer written down for it, worked out by hand.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from code_coach.engine import c_available, run_code
from code_coach.typing.drills import THEMES, THEMES_BY_ID
from code_coach.typing.keys import BY_CHAR
from code_coach.typing.snippets_calgo import CALGO_BLOCKS, CALGO_LINES, CALGO_PRINTS

_PREFIX = "C · "
_COMPILER = shutil.which("clang") or shutil.which("gcc")


def _typeable(text: str) -> bool:
    return all(ch in BY_CHAR or ch in " \n" for ch in text)


class LineTests(unittest.TestCase):
    def test_enough_tidy_lines_with_notes(self) -> None:
        self.assertGreaterEqual(len(CALGO_LINES), 55)
        pool = THEMES_BY_ID["ccode"].passages
        high = max(len(p.text) for p in pool)
        for p in CALGO_LINES:
            with self.subTest(line=p.text):
                self.assertTrue(_typeable(p.text) and _typeable(p.source))
                self.assertNotIn("\n", p.text)
                self.assertNotIn("  ", p.text)
                self.assertEqual(p.text, p.text.strip())
                self.assertNotIn("//", p.text, "a comment is not code to type")
                self.assertNotIn("/*", p.text, "a comment is not code to type")
                self.assertTrue(p.source.strip())
                self.assertGreaterEqual(len(p.text), 9)
                self.assertLessEqual(len(p.text), high)

    def test_nothing_repeats_here_or_in_c_code(self) -> None:
        texts = [p.text for p in CALGO_LINES]
        self.assertEqual(len(texts), len(set(texts)))
        pool = {p.text for p in THEMES_BY_ID["ccode"].passages}
        self.assertEqual(pool & set(texts), set())

    def test_the_c_escapes_are_real_backslashes(self) -> None:
        # a "\0" written in a plain Python string would be a NUL byte, not what a person types
        for p in CALGO_LINES:
            self.assertNotIn("\x00", p.text)
            self.assertNotIn("\n", p.text)
        self.assertTrue(any("'\\0'" in p.text for p in CALGO_LINES))
        self.assertTrue(any("(x > y) - (x < y)" in p.text for p in CALGO_LINES))
        self.assertTrue(any("int counts[26] = { 0 };" in p.text for p in CALGO_LINES))
        self.assertTrue(any("lo + (hi - lo) / 2" in p.text for p in CALGO_LINES))


class BlockTests(unittest.TestCase):
    def test_every_block_has_an_answer_and_a_sane_shape(self) -> None:
        notes = [p.source[len(_PREFIX):] for p in CALGO_BLOCKS]
        self.assertGreaterEqual(len(notes), 10)
        self.assertEqual(len(notes), len(set(notes)))
        self.assertEqual(set(notes), set(CALGO_PRINTS))
        for p in CALGO_BLOCKS:
            lines = [ln for ln in p.text.splitlines() if ln.strip()]
            with self.subTest(block=p.source):
                self.assertTrue(p.source.startswith(_PREFIX))
                self.assertTrue(_typeable(p.text))
                self.assertGreaterEqual(len(lines), 4)
                self.assertLessEqual(len(lines), 14)
                self.assertIn("int main(void)", p.text)
                self.assertIn("return 0;", p.text)
                self.assertIn("#include <stdio.h>", p.text)
                for line in p.text.splitlines():
                    self.assertEqual(line, line.rstrip())
                    self.assertEqual((len(line) - len(line.lstrip(" "))) % 4, 0, line)
                    self.assertLessEqual(len(line), 90, line)

    def test_nothing_unportable_in_a_block(self) -> None:
        for p in CALGO_BLOCKS:
            with self.subTest(block=p.source):
                self.assertNotIn("%p", p.text)
                self.assertNotIn("//", p.text)
                self.assertNotIn("/*", p.text)
                self.assertNotIn("rand", p.text)
                self.assertNotIn("scanf", p.text)

    @unittest.skipUnless(c_available(), "no C compiler is installed")
    def test_every_block_prints_what_was_worked_out(self) -> None:
        for p in CALGO_BLOCKS:
            note = p.source[len(_PREFIX):]
            with self.subTest(block=note):
                out, err, rc = run_code(p.text, language="c")
                self.assertEqual(rc, 0, err[-300:])
                self.assertEqual(out.replace("\r\n", "\n").rstrip("\n"), CALGO_PRINTS[note])

    @unittest.skipUnless(_COMPILER, "neither clang nor gcc is on PATH")
    def test_every_block_builds_warning_free_under_strict_flags(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            for i, p in enumerate(CALGO_BLOCKS):
                with self.subTest(block=p.source):
                    src = Path(folder) / f"block{i}.c"
                    src.write_text(p.text + "\n", encoding="utf-8", newline="\n")
                    built = subprocess.run(
                        [_COMPILER, "-std=c11", "-Wall", "-Wextra", "-pedantic", "-Werror",
                         "-fsyntax-only", str(src)],
                        capture_output=True, text=True, timeout=60, cwd=folder,
                    )
                    self.assertEqual((built.returncode, built.stderr.strip()), (0, ""))


class RegistrationTests(unittest.TestCase):
    def test_registered_beside_c_lore_and_served_once(self) -> None:
        from code_coach.typing.drills import BESIDE_LORE

        theme = THEMES_BY_ID["calgo"]
        self.assertEqual((theme.language, theme.passages, theme.blocks), ("c", CALGO_LINES, CALGO_BLOCKS))
        self.assertIn("calgo", BESIDE_LORE["clang"])
        mine = {p.text for p in CALGO_LINES}
        for other in THEMES:
            if other.id != "calgo":
                self.assertEqual({p.text for p in other.passages} & mine, set(), other.id)


if __name__ == "__main__":
    unittest.main()
