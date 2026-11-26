"""Dart Algorithm Code, the typing set in code_coach/typing/snippets_dartalgo.py.

The same guards the Python and JavaScript themed sets keep: every character
on the keyboard, a note on everything, no stray whitespace, lengths inside
the Dart pool's range, nothing already in Dart Code. Dart cannot parse a
single statement on its own, so the lines are held to what they contain;
the blocks are whole programs, and each is run in Dart and held to the
answer written down for it, worked out by hand.
"""

from __future__ import annotations

import unittest

from code_coach.engine import dart_available, run_code
from code_coach.typing.drills import THEMES, THEMES_BY_ID
from code_coach.typing.keys import BY_CHAR
from code_coach.typing.snippets_dartalgo import DARTALGO_BLOCKS, DARTALGO_LINES, DARTALGO_PRINTS

_PREFIX = "Dart · "


def _typeable(text: str) -> bool:
    return all(ch in BY_CHAR or ch in " \n" for ch in text)


class LineTests(unittest.TestCase):
    def test_enough_tidy_lines_with_notes(self) -> None:
        self.assertGreaterEqual(len(DARTALGO_LINES), 55)
        pool = THEMES_BY_ID["dartcode"].passages
        high = max(len(p.text) for p in pool)
        for p in DARTALGO_LINES:
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

    def test_nothing_repeats_here_or_in_dart_code(self) -> None:
        texts = [p.text for p in DARTALGO_LINES]
        self.assertEqual(len(texts), len(set(texts)))
        pool = {p.text for p in THEMES_BY_ID["dartcode"].passages}
        self.assertEqual(pool & set(texts), set())


class BlockTests(unittest.TestCase):
    def test_every_block_has_an_answer_and_a_sane_shape(self) -> None:
        notes = [p.source[len(_PREFIX):] for p in DARTALGO_BLOCKS]
        self.assertGreaterEqual(len(notes), 8)
        self.assertEqual(len(notes), len(set(notes)))
        self.assertEqual(set(notes), set(DARTALGO_PRINTS))
        for p in DARTALGO_BLOCKS:
            lines = [ln for ln in p.text.splitlines() if ln.strip()]
            with self.subTest(block=p.source):
                self.assertTrue(p.source.startswith(_PREFIX))
                self.assertTrue(_typeable(p.text))
                self.assertGreaterEqual(len(lines), 4)
                self.assertLessEqual(len(lines), 12)
                self.assertIn("void main()", p.text)
                for line in p.text.splitlines():
                    self.assertEqual(line, line.rstrip())
                    self.assertEqual((len(line) - len(line.lstrip(" "))) % 2, 0, line)

    @unittest.skipUnless(dart_available(), "Dart is not installed")
    def test_every_block_prints_what_was_worked_out(self) -> None:
        for p in DARTALGO_BLOCKS:
            note = p.source[len(_PREFIX):]
            with self.subTest(block=note):
                out, err, rc = run_code(p.text, language="dart")
                self.assertEqual(rc, 0, err[-300:])
                self.assertEqual(out.replace("\r\n", "\n").rstrip("\n"), DARTALGO_PRINTS[note])


class RegistrationTests(unittest.TestCase):
    def test_registered_beside_dart_lore_and_served_once(self) -> None:
        from code_coach.typing.drills import BESIDE_LORE

        theme = THEMES_BY_ID["dartalgo"]
        self.assertEqual((theme.language, theme.passages, theme.blocks), ("dart", DARTALGO_LINES, DARTALGO_BLOCKS))
        self.assertIn("dartalgo", BESIDE_LORE["dart"])
        mine = {p.text for p in DARTALGO_LINES}
        for other in THEMES:
            if other.id != "dartalgo":
                self.assertEqual({p.text for p in other.passages} & mine, set(), other.id)


if __name__ == "__main__":
    unittest.main()
