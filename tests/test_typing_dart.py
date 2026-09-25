"""Dart's history and in-use passages have to be typeable and worth typing.

The same guards `test_typing` puts on every served target, applied to the
new Dart prose directly so they hold before the passages are registered.
"""

from __future__ import annotations

import unittest

from code_coach.typing import langhistory, langlore
from code_coach.typing.drills import UNTYPEABLE
from code_coach.typing.keys import BY_CHAR
from code_coach.typing.langhistory_dart import DART_IN_USE, DART_STORY

NEW = DART_STORY + DART_IN_USE

# The sibling history passages set the length range these should sit in.
_SIBLINGS = (
    langhistory.PYTHON_STORY
    + langhistory.PYTHON_IN_USE
    + langhistory.JAVASCRIPT_STORY
    + langhistory.JAVASCRIPT_IN_USE
)


class DartHistoryTests(unittest.TestCase):
    def test_there_is_enough_of_each(self) -> None:
        self.assertGreaterEqual(len(DART_STORY), 10)
        self.assertGreaterEqual(len(DART_IN_USE), 10)

    def test_every_character_is_on_the_keyboard(self) -> None:
        for passage in NEW:
            for char in passage.text:
                self.assertNotIn(char, UNTYPEABLE, passage.text)
                self.assertIn(char, BY_CHAR, f"{char!r} in {passage.text!r}")

    def test_passages_are_single_lines_without_stray_spaces(self) -> None:
        for passage in NEW:
            self.assertNotIn("\n", passage.text)
            self.assertEqual(passage.text, passage.text.strip())
            self.assertNotIn("  ", passage.text, passage.text)

    def test_lengths_match_the_sibling_history(self) -> None:
        lengths = [len(p.text) for p in _SIBLINGS]
        low, high = min(lengths), max(lengths)
        for passage in NEW:
            self.assertGreaterEqual(len(passage.text), low, passage.text)
            self.assertLessEqual(len(passage.text), high, passage.text)

    def test_no_duplicates_here_or_against_the_existing_lore(self) -> None:
        texts = [p.text for p in NEW]
        self.assertEqual(len(texts), len(set(texts)))
        existing = {p.text for p in langlore.DART + _SIBLINGS}
        self.assertFalse(existing & set(texts))

    def test_every_passage_names_a_source(self) -> None:
        for passage in NEW:
            self.assertTrue(passage.source.strip(), passage.text)
            self.assertTrue(
                any(w in passage.source for w in ("Dart", "Flutter")),
                passage.source,
            )


if __name__ == "__main__":
    unittest.main()
