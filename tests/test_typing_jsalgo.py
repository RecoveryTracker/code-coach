"""JavaScript Algorithm Code, the typing set in code_coach/typing/snippets_jsalgo.py.

Held to the rules tests/test_typing_jsnode_music_cooking.py keeps for every
themed JavaScript set, reused rather than copied: every character on the
keyboard, a note on every line, lengths inside the JavaScript pool's range,
nothing repeated from that pool or any other set, every line parses in Node,
and every block runs in Node and prints exactly the answer written down for
it, worked out by hand before Node was asked.
"""

from __future__ import annotations

import unittest

from tests.test_typing_jsnode_music_cooking import _ALL_BLOCKS, _ALL_LINES, _BlockRules, _LineRules

from code_coach.typing.snippets_jsalgo import JSALGO_BLOCKS, JSALGO_LINES, JSALGO_PRINTS


class JsalgoLinesTests(_LineRules, unittest.TestCase):
    LINES = JSALGO_LINES
    OTHER = _ALL_LINES


class JsalgoBlocksTests(_BlockRules, unittest.TestCase):
    BLOCKS = JSALGO_BLOCKS
    OTHER = _ALL_BLOCKS
    PRINTS = JSALGO_PRINTS


class RegistrationTests(unittest.TestCase):
    def test_registered_beside_javascript_lore(self) -> None:
        from code_coach.typing.drills import BESIDE_LORE, THEMES, THEMES_BY_ID

        theme = THEMES_BY_ID["jsalgo"]
        self.assertEqual((theme.name, theme.language), ("JavaScript Algorithm Code", "javascript"))
        self.assertEqual((theme.passages, theme.blocks), (JSALGO_LINES, JSALGO_BLOCKS))
        self.assertIn("jsalgo", BESIDE_LORE["javascript"])
        mine = {p.text for p in JSALGO_LINES}
        for other in THEMES:
            if other.id != "jsalgo":
                self.assertEqual({p.text for p in other.passages} & mine, set(), other.id)


if __name__ == "__main__":
    unittest.main()
