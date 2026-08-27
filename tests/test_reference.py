"""The cheat sheets, and the flashcards drawn from them.

A reference card is only worth having if it is dense, ordered and correct, so
these check the properties that make it that: the most-used section first, no
line repeated, every entry carrying a note, and nothing on it that a keyboard
cannot type.
"""

from __future__ import annotations

import unittest

from code_coach.reference import languages_with_sheets, sheet_for
from code_coach.typing.keys import ALL_KEYS


TYPEABLE = (
    {k.char for k in ALL_KEYS}
    | {k.shifted for k in ALL_KEYS}
    | {" ", "\n"}
)


class CoverageTests(unittest.TestCase):
    def test_there_are_sheets(self) -> None:
        self.assertTrue(languages_with_sheets())

    def test_the_working_languages_have_one(self) -> None:
        for language in ("python", "javascript", "typescript", "dart"):
            with self.subTest(language=language):
                self.assertIsNotNone(sheet_for(language))

    def test_an_unknown_language_gets_nothing_rather_than_the_wrong_one(
        self,
    ) -> None:
        """Handing a Rust student the Python sheet would be worse than an
        honest gap."""
        self.assertIsNone(sheet_for("cobol"))

    def test_a_sheet_is_worth_opening(self) -> None:
        for language in languages_with_sheets():
            sheet = sheet_for(language)
            entries = sum(len(s.entries) for s in sheet.sections)
            with self.subTest(language=language):
                self.assertGreaterEqual(len(sheet.sections), 5)
                self.assertGreaterEqual(entries, 40)


class ShapeTests(unittest.TestCase):
    def test_the_first_section_is_the_first_minute(self) -> None:
        """Most-used first is the whole ordering principle: the top of the
        card is what you reach for before anything else."""
        for language in languages_with_sheets():
            with self.subTest(language=language):
                self.assertEqual(
                    sheet_for(language).sections[0].name, "The first minute"
                )

    def test_every_section_says_what_it_is(self) -> None:
        for language in languages_with_sheets():
            for section in sheet_for(language).sections:
                with self.subTest(language=language, section=section.name):
                    self.assertTrue(section.name.strip())
                    self.assertGreater(len(section.blurb), 15)
                    self.assertTrue(section.entries)

    def test_every_entry_carries_a_note(self) -> None:
        """The note is the flashcard's prompt, so an entry without one is a
        line you can read and never be tested on."""
        for language in languages_with_sheets():
            for section in sheet_for(language).sections:
                for entry in section.entries:
                    with self.subTest(language=language, code=entry.code[:30]):
                        self.assertTrue(entry.code.strip())
                        self.assertTrue(entry.note.strip())

    def test_a_note_is_shorter_than_the_prose_elsewhere(self) -> None:
        """This is a card, not a lesson. A note that runs on belongs in the
        lore or the lesson instead."""
        for language in languages_with_sheets():
            for section in sheet_for(language).sections:
                for entry in section.entries:
                    with self.subTest(language=language, code=entry.code[:30]):
                        self.assertLessEqual(len(entry.note), 90)

    def test_no_line_appears_twice_outside_the_summary(self) -> None:
        """The first section is deliberately a greatest hits, so a line there
        may also live in the section it properly belongs to. Anywhere else, a
        repeat is padding."""
        for language in languages_with_sheets():
            seen: dict[str, str] = {}
            for section in sheet_for(language).sections:
                for entry in section.entries:
                    before = seen.get(entry.code)
                    summary = "The first minute" in (before or "", section.name)
                    with self.subTest(language=language, code=entry.code[:30]):
                        self.assertTrue(
                            before is None or summary,
                            f"{entry.code!r} is in both {before} and {section.name}",
                        )
                    seen[entry.code] = section.name

    def test_no_line_appears_twice_within_one_section(self) -> None:
        for language in languages_with_sheets():
            for section in sheet_for(language).sections:
                codes = [e.code for e in section.entries]
                with self.subTest(language=language, section=section.name):
                    self.assertEqual(len(codes), len(set(codes)))

    def test_every_line_can_be_typed(self) -> None:
        """It is a reference for a keyboard, so a curly quote or an em dash in
        the code would be a line nobody can reproduce."""
        for language in languages_with_sheets():
            for section in sheet_for(language).sections:
                for entry in section.entries:
                    stray = sorted(set(entry.code) - TYPEABLE)
                    with self.subTest(language=language, code=entry.code[:30]):
                        self.assertEqual(stray, [])

    def test_entries_are_lines_not_paragraphs(self) -> None:
        """A card entry is glanceable. Anything longer is a snippet, and the
        fundamentals bank is where snippets live."""
        for language in languages_with_sheets():
            for section in sheet_for(language).sections:
                for entry in section.entries:
                    with self.subTest(language=language, code=entry.code[:30]):
                        self.assertLessEqual(len(entry.code.splitlines()), 6)


class EndpointTests(unittest.TestCase):
    def test_it_serves_the_language_being_practised(self) -> None:
        import tempfile
        from pathlib import Path

        from code_coach.api import server
        from code_coach.progress.store import ProgressStore

        real = server._store
        try:
            server._store = ProgressStore(Path(tempfile.mkdtemp()) / "p.json")
            for language in ("python", "javascript", "typescript", "dart"):
                progress = server._store.load()
                progress.language = language
                server._store.save(progress)
                payload = server.reference()
                with self.subTest(language=language):
                    self.assertTrue(payload["has_sheet"])
                    self.assertEqual(payload["language"], language)
                    self.assertTrue(payload["sections"])
        finally:
            server._store = real

    def test_a_language_without_a_sheet_says_so(self) -> None:
        import tempfile
        from pathlib import Path

        from code_coach.api import server
        from code_coach.progress.store import ProgressStore

        real = server._store
        try:
            server._store = ProgressStore(Path(tempfile.mkdtemp()) / "p.json")
            progress = server._store.load()
            progress.language = "rust"
            server._store.save(progress)
            payload = server.reference()
            self.assertFalse(payload["has_sheet"])
            self.assertEqual(payload["sections"], [])
        finally:
            server._store = real


if __name__ == "__main__":
    unittest.main()
