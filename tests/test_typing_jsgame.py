"""The JavaScript game lines, library lines, blocks and lore obey the rules.

The same guards `test_typing_js_more` puts on its lines and blocks, applied
to `snippets_jsgame` directly so they hold before it is registered as a
theme and after: every character on the keyboard, a note on everything,
lengths inside the range the existing JavaScript pool already uses,
nothing already in that pool, every line parses, and every block runs in
Node. The lore gets the rules `LanguageHistoryTests` puts on the history
passages - the standard, not the facts.
"""

from __future__ import annotations

import datetime
import json
import re
import shutil
import unittest

from code_coach.typing import langhistory
from code_coach.typing.curriculum import (
    MAX_BLOCK_LINES,
    MIN_BLOCK_LINES,
    MIN_LENGTH,
    code_blocks_for,
    code_lines_for,
)
from code_coach.typing.drills import UNTYPEABLE
from code_coach.typing.keys import BY_CHAR
from code_coach.typing.snippets import JAVASCRIPT_CODE
from code_coach.typing.snippets_js_more import (
    JAVASCRIPT_BLOCKS_MORE,
    JAVASCRIPT_LINES_MORE,
)
from code_coach.typing.snippets_jsgame import (
    JSGAME_BLOCKS,
    JSGAME_LIBRARY_LINES,
    JSGAME_LINES,
    JSGAME_LORE,
)
from code_coach.typing.snippets_more import JAVASCRIPT_MORE

LINES = JSGAME_LINES + JSGAME_LIBRARY_LINES

# Every JavaScript line and block already served somewhere. Once this
# module is registered its own passages may be in these pools too, so
# they are taken out by identity before comparing.
_MINE = {id(p) for p in LINES + JSGAME_BLOCKS + JSGAME_LORE}
_EXISTING_LINES = [
    p for p in (
        code_lines_for("javascript", curated=JAVASCRIPT_CODE)
        + code_lines_for("typescript")
        + JAVASCRIPT_LINES_MORE
        + JAVASCRIPT_MORE
    )
    if id(p) not in _MINE
]
_EXISTING_BLOCKS = [
    p for p in code_blocks_for("javascript") + JAVASCRIPT_BLOCKS_MORE
    if id(p) not in _MINE
]

# The history passages the lore should read like.
_SIBLING_LORE = (
    langhistory.PYTHON_STORY
    + langhistory.PYTHON_IN_USE
    + langhistory.JAVASCRIPT_STORY
    + langhistory.JAVASCRIPT_IN_USE
)

_LIBRARIES = ("Phaser", "PixiJS", "Three.js", "Kaplay", "Matter.js", "howler.js")


def _node() -> bool:
    return shutil.which("node") is not None


def _assert_typeable(case: unittest.TestCase, text: str) -> None:
    for char in text:
        if char == "\n":
            continue
        case.assertNotIn(char, UNTYPEABLE, text)
        case.assertIn(char, BY_CHAR, f"{char!r} in {text!r}")


class JavaScriptGameLinesTests(unittest.TestCase):
    def test_there_are_enough(self) -> None:
        self.assertGreaterEqual(len(JSGAME_LINES), 65)
        self.assertGreaterEqual(len(JSGAME_LIBRARY_LINES), 35)

    def test_every_character_is_on_the_keyboard(self) -> None:
        for passage in LINES:
            _assert_typeable(self, passage.text)

    def test_single_lines_without_stray_whitespace(self) -> None:
        for passage in LINES:
            self.assertNotIn("\n", passage.text)
            self.assertNotIn("\t", passage.text)
            self.assertNotIn("  ", passage.text, passage.text)
            self.assertEqual(passage.text, passage.text.strip())

    def test_every_line_says_what_it_does(self) -> None:
        for passage in LINES:
            self.assertTrue(passage.source.strip(), passage.text)
            _assert_typeable(self, passage.source)

    def test_every_library_line_names_its_library(self) -> None:
        for passage in JSGAME_LIBRARY_LINES:
            with self.subTest(line=passage.text):
                self.assertTrue(
                    any(passage.source.startswith(f"{lib}") for lib in _LIBRARIES),
                    passage.source,
                )

    def test_every_library_is_represented(self) -> None:
        sources = " ".join(p.source for p in JSGAME_LIBRARY_LINES)
        for lib in _LIBRARIES:
            self.assertIn(lib, sources)

    def test_lengths_sit_inside_the_existing_range(self) -> None:
        high = max(
            len(p.text) for p in code_lines_for("javascript", curated=JAVASCRIPT_CODE)
        )
        low = max(MIN_LENGTH, 15)
        for passage in LINES:
            self.assertGreaterEqual(len(passage.text), low, passage.text)
            self.assertLessEqual(len(passage.text), high, passage.text)

    def test_no_duplicates_here_or_against_the_existing_pool(self) -> None:
        texts = [p.text for p in LINES]
        self.assertEqual(len(texts), len(set(texts)))
        existing = {p.text for p in _EXISTING_LINES}
        self.assertEqual(existing & set(texts), set())

    @unittest.skipUnless(_node(), "node is not installed")
    def test_every_line_parses(self) -> None:
        """Each line, as the body of an async function. A line that opens a
        block gets its closing braces added, the way it would in a file."""
        from code_coach.engine import run_code

        bodies = []
        for passage in LINES:
            text = passage.text
            opens = text.count("{") - text.count("}")
            bodies.append(text + "\n}" * max(opens, 0))
        program = (
            "const AsyncFunction = (async () => {}).constructor;\n"
            f"const bodies = {json.dumps(bodies)};\n"
            "let bad = 0;\n"
            "for (const body of bodies) {\n"
            "  try { new AsyncFunction(body); }\n"
            "  catch (e) { bad++; console.log('BAD', JSON.stringify(body), e.message); }\n"
            "}\n"
            "console.log('bad=' + bad);\n"
        )
        out, err, rc = run_code(program, language="javascript")
        self.assertEqual(rc, 0, err)
        self.assertIn("bad=0", out, out)


class JavaScriptGameBlocksTests(unittest.TestCase):
    def test_there_are_enough(self) -> None:
        self.assertGreaterEqual(len(JSGAME_BLOCKS), 15)

    def test_every_character_is_on_the_keyboard(self) -> None:
        for passage in JSGAME_BLOCKS:
            _assert_typeable(self, passage.text)

    def test_a_length_a_person_will_finish(self) -> None:
        width = max(
            len(ln) for b in code_blocks_for("javascript")
            for ln in b.text.splitlines()
        )
        for passage in JSGAME_BLOCKS:
            lines = [ln for ln in passage.text.splitlines() if ln.strip()]
            with self.subTest(block=passage.text[:30]):
                self.assertGreaterEqual(len(lines), max(MIN_BLOCK_LINES, 4))
                self.assertLessEqual(len(lines), min(MAX_BLOCK_LINES, 12))
                for line in passage.text.splitlines():
                    self.assertLessEqual(len(line), width, line)

    def test_tidy_and_really_indented(self) -> None:
        for passage in JSGAME_BLOCKS:
            with self.subTest(block=passage.text[:30]):
                self.assertEqual(passage.text, passage.text.strip("\n"))
                self.assertNotIn("\t", passage.text)
                for line in passage.text.splitlines():
                    self.assertEqual(line, line.rstrip())
                    indent = len(line) - len(line.lstrip(" "))
                    self.assertEqual(indent % 2, 0, line)
                self.assertTrue(
                    any(ln.startswith("  ") for ln in passage.text.splitlines())
                )

    def test_no_dom_in_a_block(self) -> None:
        """They run in Node, so a canvas or a window would be a crash."""
        for passage in JSGAME_BLOCKS:
            for word in ("document", "window", "canvas", "ctx."):
                self.assertNotIn(word, passage.text)

    def test_every_note_names_the_language(self) -> None:
        for passage in JSGAME_BLOCKS:
            self.assertTrue(passage.source.startswith("JavaScript · "))
            self.assertTrue(passage.source[len("JavaScript · "):].strip())

    def test_no_duplicates_here_or_against_the_existing_blocks(self) -> None:
        texts = [p.text for p in JSGAME_BLOCKS]
        self.assertEqual(len(texts), len(set(texts)))
        existing = {p.text for p in _EXISTING_BLOCKS}
        self.assertEqual(existing & set(texts), set())

    @unittest.skipUnless(_node(), "node is not installed")
    def test_every_block_runs_in_node(self) -> None:
        from code_coach.engine import run_code

        for passage in JSGAME_BLOCKS:
            first = passage.text.splitlines()[0]
            with self.subTest(block=first):
                out, err, rc = run_code(passage.text, language="javascript")
                self.assertEqual(rc, 0, err)
                self.assertTrue(out.strip(), f"no output from {first}")


class JavaScriptGameLoreTests(unittest.TestCase):
    def test_there_is_enough(self) -> None:
        self.assertGreaterEqual(len(JSGAME_LORE), 30)

    def test_every_character_is_on_the_keyboard(self) -> None:
        for passage in JSGAME_LORE:
            _assert_typeable(self, passage.text)
            _assert_typeable(self, passage.source)

    def test_each_is_one_passage_with_a_source(self) -> None:
        for passage in JSGAME_LORE:
            with self.subTest(text=passage.text[:40]):
                self.assertNotIn("\n", passage.text)
                self.assertNotIn("  ", passage.text)
                self.assertEqual(passage.text, passage.text.strip())
                self.assertTrue(passage.source.strip())

    def test_lengths_match_the_sibling_history(self) -> None:
        lengths = [len(p.text) for p in _SIBLING_LORE]
        low, high = min(lengths), max(lengths)
        for passage in JSGAME_LORE:
            self.assertGreaterEqual(len(passage.text), low, passage.text)
            self.assertLessEqual(len(passage.text), high, passage.text)

    def test_every_claim_is_stated_rather_than_hedged(self) -> None:
        hedges = (
            "reportedly", "apparently", "supposedly", "allegedly",
            "probably", "roughly speaking", "some say", "it is said",
            "rumour", "rumor", "i think", "believed to be",
        )
        for passage in JSGAME_LORE:
            lowered = passage.text.lower()
            for hedge in hedges:
                self.assertNotIn(hedge, lowered, passage.text)

    def test_years_are_plausible_and_in_the_past(self) -> None:
        this_year = datetime.date.today().year
        for passage in JSGAME_LORE:
            # 2048 is a game's name, not a date.
            text = passage.text.replace("wrote 2048", "wrote the game")
            for found in re.findall(r"\b(1[89]\d\d|20\d\d)\b", text):
                self.assertGreaterEqual(int(found), 1990, passage.text)
                self.assertLessEqual(int(found), this_year, passage.text)

    def test_no_duplicates_here_or_against_the_javascript_lore(self) -> None:
        from code_coach.typing import langlore

        texts = [p.text for p in JSGAME_LORE]
        self.assertEqual(len(texts), len(set(texts)))
        existing = {p.text for p in langlore.JAVASCRIPT + _SIBLING_LORE}
        self.assertFalse(existing & set(texts))


class RegistrationTests(unittest.TestCase):
    """Holds before the themes are registered and after. Once they are,
    each theme has to serve exactly this module's material, and sit
    under JavaScript Lore."""

    def test_the_themes_serve_this_module_when_registered(self) -> None:
        from code_coach.typing.drills import BESIDE_LORE, THEMES, THEMES_BY_ID

        ids = [t.id for t in THEMES]
        game = THEMES_BY_ID.get("jsgame")
        if game is not None:
            self.assertEqual(game.language, "javascript")
            self.assertEqual(game.passages, LINES)
            self.assertEqual(game.blocks, JSGAME_BLOCKS)
            self.assertIn("jsgame", BESIDE_LORE["javascript"])
        lore = THEMES_BY_ID.get("jsgamelore")
        if lore is not None:
            self.assertEqual(lore.language, "")
            self.assertEqual(lore.passages, JSGAME_LORE)
            self.assertIn("jsgamelore", BESIDE_LORE["javascript"])
        for theme_id in ("jsgame", "jsgamelore"):
            if theme_id in THEMES_BY_ID:
                at = ids.index("javascript")
                self.assertIn(theme_id, ids[at + 1:at + 5])


if __name__ == "__main__":
    unittest.main()
