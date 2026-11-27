"""Rust Algorithm Code, the typing set in code_coach/typing/snippets_rustalgo.py.

The same guards the Dart and Python themed sets keep: every character on the
keyboard, a note on everything, no stray whitespace, lengths inside the Rust
pool's range, nothing already in Rust Code. Rust cannot compile a single
statement on its own, so the lines are held to what they contain; the blocks
are whole programs, and each is built with rustc, run, and held to the answer
written down for it, worked out by hand.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code, rust_available
from code_coach.typing.drills import THEMES, THEMES_BY_ID
from code_coach.typing.keys import BY_CHAR
from code_coach.typing.snippets_rustalgo import RUSTALGO_BLOCKS, RUSTALGO_LINES, RUSTALGO_PRINTS

_PREFIX = "Rust · "


def _typeable(text: str) -> bool:
    return all(ch in BY_CHAR or ch in " \n" for ch in text)


class LineTests(unittest.TestCase):
    def test_enough_tidy_lines_with_notes(self) -> None:
        self.assertGreaterEqual(len(RUSTALGO_LINES), 55)
        pool = THEMES_BY_ID["rustcode"].passages
        high = max(len(p.text) for p in pool)
        for p in RUSTALGO_LINES:
            with self.subTest(line=p.text):
                self.assertTrue(_typeable(p.text) and _typeable(p.source))
                self.assertNotIn("\n", p.text)
                self.assertNotIn("  ", p.text)
                self.assertEqual(p.text, p.text.strip())
                self.assertFalse(p.text.startswith("//"))
                self.assertNotIn("//", p.text, "a comment is not code to type")
                self.assertTrue(p.source.strip())
                self.assertGreaterEqual(len(p.text), 9)
                self.assertLessEqual(len(p.text), high)

    def test_nothing_repeats_here_or_in_rust_code(self) -> None:
        texts = [p.text for p in RUSTALGO_LINES]
        self.assertEqual(len(texts), len(set(texts)))
        pool = {p.text for p in THEMES_BY_ID["rustcode"].passages}
        self.assertEqual(pool & set(texts), set())


class BlockTests(unittest.TestCase):
    def test_every_block_has_an_answer_and_a_sane_shape(self) -> None:
        notes = [p.source[len(_PREFIX):] for p in RUSTALGO_BLOCKS]
        self.assertGreaterEqual(len(notes), 10)
        self.assertEqual(len(notes), len(set(notes)))
        self.assertEqual(set(notes), set(RUSTALGO_PRINTS))
        for p in RUSTALGO_BLOCKS:
            lines = [ln for ln in p.text.splitlines() if ln.strip()]
            with self.subTest(block=p.source):
                self.assertTrue(p.source.startswith(_PREFIX))
                self.assertTrue(_typeable(p.text))
                self.assertGreaterEqual(len(lines), 4)
                self.assertLessEqual(len(lines), 14)
                self.assertIn("fn main()", p.text)
                for line in p.text.splitlines():
                    self.assertEqual(line, line.rstrip())
                    self.assertEqual((len(line) - len(line.lstrip(" "))) % 4, 0, line)

    @unittest.skipUnless(rust_available(), "Rust is not installed")
    def test_every_block_prints_what_was_worked_out(self) -> None:
        for p in RUSTALGO_BLOCKS:
            note = p.source[len(_PREFIX):]
            with self.subTest(block=note):
                out, err, rc = run_code(p.text, language="rust")
                self.assertEqual(rc, 0, err[-300:])
                self.assertEqual(err.strip(), "", "the block should build without warnings")
                self.assertEqual(out.replace("\r\n", "\n").rstrip("\n"), RUSTALGO_PRINTS[note])


class RegistrationTests(unittest.TestCase):
    def test_registered_beside_rust_lore_and_served_once(self) -> None:
        from code_coach.typing.drills import BESIDE_LORE

        theme = THEMES_BY_ID["rustalgo"]
        self.assertEqual((theme.language, theme.passages, theme.blocks), ("rust", RUSTALGO_LINES, RUSTALGO_BLOCKS))
        self.assertIn("rustalgo", BESIDE_LORE["rust"])
        mine = {p.text for p in RUSTALGO_LINES}
        for other in THEMES:
            if other.id != "rustalgo":
                self.assertEqual({p.text for p in other.passages} & mine, set(), other.id)


if __name__ == "__main__":
    unittest.main()
