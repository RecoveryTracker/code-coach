"""The Python Algorithm and Python Classes typing sets obey the same rules
as the four themed Python sets in tests/test_typing_python_themes.py.

The rules are that file's, reused rather than copied: every character on
the keyboard, a note on every line, lengths inside the existing Python
pool's range, nothing repeated from that pool or from any other set, every
line valid Python, and every block run in the real interpreter and held to
the answer written down for it - worked out by hand before Python was asked.
"""

from __future__ import annotations

import unittest

from tests.test_typing_python_themes import _ALL_BLOCKS, _ALL_LINES, _BlockRules, _LineRules

from code_coach.typing.snippets_pyalgo import PYALGO_BLOCKS, PYALGO_LINES, PYALGO_PRINTS
from code_coach.typing.snippets_pyclass import PYCLASS_BLOCKS, PYCLASS_LINES, PYCLASS_PRINTS


class PyalgoLinesTests(_LineRules, unittest.TestCase):
    LINES = PYALGO_LINES
    OTHER = PYCLASS_LINES + _ALL_LINES


class PyalgoBlocksTests(_BlockRules, unittest.TestCase):
    BLOCKS = PYALGO_BLOCKS
    OTHER = PYCLASS_BLOCKS + _ALL_BLOCKS
    PRINTS = PYALGO_PRINTS


class PyclassLinesTests(_LineRules, unittest.TestCase):
    LINES = PYCLASS_LINES
    OTHER = PYALGO_LINES + _ALL_LINES


class PyclassBlocksTests(_BlockRules, unittest.TestCase):
    BLOCKS = PYCLASS_BLOCKS
    OTHER = PYALGO_BLOCKS + _ALL_BLOCKS
    PRINTS = PYCLASS_PRINTS


class RegistrationTests(unittest.TestCase):
    def test_registered_beside_python_lore(self) -> None:
        from code_coach.typing.drills import BESIDE_LORE, THEMES_BY_ID

        for theme_id, name, lines, blocks in (
            ("pyalgo", "Python Algorithm Code", PYALGO_LINES, PYALGO_BLOCKS),
            ("pyclass", "Python Classes and Types", PYCLASS_LINES, PYCLASS_BLOCKS),
        ):
            with self.subTest(theme=theme_id):
                theme = THEMES_BY_ID[theme_id]
                self.assertEqual((theme.name, theme.language), (name, "python"))
                self.assertEqual(theme.passages, lines)
                self.assertEqual(theme.blocks, blocks)
                self.assertIn(theme_id, BESIDE_LORE["python"])

    def test_no_other_theme_serves_their_lines(self) -> None:
        from code_coach.typing.drills import THEMES

        mine = {p.text for p in PYALGO_LINES + PYCLASS_LINES}
        for theme in THEMES:
            if theme.id in ("pyalgo", "pyclass"):
                continue
            with self.subTest(theme=theme.id):
                self.assertEqual({p.text for p in theme.passages} & mine, set())


if __name__ == "__main__":
    unittest.main()
