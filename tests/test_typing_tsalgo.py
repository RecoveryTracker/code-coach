"""TypeScript Algorithm Code, the typing set in code_coach/typing/snippets_tsalgo.py.

The same guards the Python, JavaScript and Dart themed sets keep: every
character on the keyboard, a note on everything, no stray whitespace,
lengths inside the TypeScript pool's range, nothing already in TypeScript
Code or in any other theme. A single TypeScript statement cannot be compiled
on its own, so the lines are held to what they contain; the blocks are whole
programs, and each is compiled with `tsc --strict` and run, then held to the
answer written down for it, worked out by hand.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code, typescript_available
from code_coach.typing.drills import THEMES, THEMES_BY_ID
from code_coach.typing.keys import BY_CHAR
from code_coach.typing.snippets_tsalgo import TSALGO_BLOCKS, TSALGO_LINES, TSALGO_PRINTS

_PREFIX = "TypeScript · "


def _typeable(text: str) -> bool:
    return all(ch in BY_CHAR or ch in " \n" for ch in text)


class LineTests(unittest.TestCase):
    def test_enough_tidy_lines_with_notes(self) -> None:
        self.assertGreaterEqual(len(TSALGO_LINES), 55)
        pool = THEMES_BY_ID["tscode"].passages
        high = max(len(p.text) for p in pool)
        for p in TSALGO_LINES:
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

    def test_nothing_repeats_here_or_in_typescript_code(self) -> None:
        texts = [p.text for p in TSALGO_LINES]
        self.assertEqual(len(texts), len(set(texts)))
        pool = {p.text for p in THEMES_BY_ID["tscode"].passages}
        self.assertEqual(pool & set(texts), set())

    def test_nothing_repeats_in_any_other_theme(self) -> None:
        mine = {p.text for p in TSALGO_LINES}
        for other in THEMES:
            if other.id != "tsalgo":
                with self.subTest(theme=other.id):
                    self.assertEqual({p.text for p in other.passages} & mine, set())


class BlockTests(unittest.TestCase):
    def test_every_block_has_an_answer_and_a_sane_shape(self) -> None:
        notes = [p.source[len(_PREFIX):] for p in TSALGO_BLOCKS]
        self.assertGreaterEqual(len(notes), 10)
        self.assertEqual(len(notes), len(set(notes)))
        self.assertEqual(set(notes), set(TSALGO_PRINTS))
        for p in TSALGO_BLOCKS:
            lines = [ln for ln in p.text.splitlines() if ln.strip()]
            with self.subTest(block=p.source):
                self.assertTrue(p.source.startswith(_PREFIX))
                self.assertTrue(_typeable(p.text))
                self.assertGreaterEqual(len(lines), 4)
                self.assertLessEqual(len(lines), 12)
                self.assertIn("console.log(", p.text)
                for line in p.text.splitlines():
                    self.assertEqual(line, line.rstrip())
                    self.assertEqual((len(line) - len(line.lstrip(" "))) % 2, 0, line)

    @unittest.skipUnless(typescript_available(), "TypeScript is not installed")
    def test_every_block_prints_what_was_worked_out(self) -> None:
        for p in TSALGO_BLOCKS:
            note = p.source[len(_PREFIX):]
            with self.subTest(block=note):
                out, err, rc = run_code(p.text, language="typescript")
                self.assertEqual(rc, 0, (out + err)[-400:])
                self.assertEqual(out.replace("\r\n", "\n").rstrip("\n"), TSALGO_PRINTS[note])


class RegistrationTests(unittest.TestCase):
    def test_registered_beside_javascript_lore_and_served_once(self) -> None:
        from code_coach.typing.drills import BESIDE_LORE

        theme = THEMES_BY_ID["tsalgo"]
        self.assertEqual(
            (theme.language, theme.passages, theme.blocks), ("typescript", TSALGO_LINES, TSALGO_BLOCKS)
        )
        self.assertIn("tsalgo", BESIDE_LORE["javascript"])
        mine = {p.text for p in TSALGO_LINES}
        for other in THEMES:
            if other.id != "tsalgo":
                self.assertEqual({p.text for p in other.passages} & mine, set(), other.id)


if __name__ == "__main__":
    unittest.main()
