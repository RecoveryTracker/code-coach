"""SQL Query Patterns, the typing set in code_coach/typing/snippets_sqlquery.py.

The lines are clause-sized fragments and cannot be run, so they are held to
what they contain: every character on the keyboard, a note on each, no stray
whitespace, nothing already in the SQL pool. The blocks are whole statements,
and each is run in SQLite against the shop in SCHEMA and held to the rows
written down for it, worked out by hand.
"""

from __future__ import annotations

import sqlite3
import unittest

from code_coach.typing.curriculum import code_lines_for
from code_coach.typing.keys import BY_CHAR
from code_coach.typing.snippets import SQL_CODE
from code_coach.typing.snippets_sqlquery import SCHEMA, SQLQUERY_BLOCKS, SQLQUERY_LINES, SQLQUERY_ROWS

_PREFIX = "SQL · "


def _typeable(text: str) -> bool:
    return all(ch in BY_CHAR or ch in " \n" for ch in text)


class LineTests(unittest.TestCase):
    def test_there_are_enough_and_none_repeat(self) -> None:
        self.assertGreaterEqual(len(SQLQUERY_LINES), 55)
        texts = [p.text for p in SQLQUERY_LINES]
        self.assertEqual(len(texts), len(set(texts)))
        pool = {p.text for p in code_lines_for("sql", curated=SQL_CODE)}
        self.assertEqual(pool & set(texts), set())

    def test_tidy_typeable_lines_with_notes(self) -> None:
        for p in SQLQUERY_LINES:
            with self.subTest(line=p.text):
                self.assertTrue(_typeable(p.text) and _typeable(p.source))
                self.assertNotIn("\n", p.text)
                self.assertNotIn("  ", p.text)
                self.assertEqual(p.text, p.text.strip())
                self.assertTrue(p.source.strip())
                self.assertGreaterEqual(len(p.text), 9)
                self.assertLessEqual(len(p.text), 84)


class BlockTests(unittest.TestCase):
    def test_every_block_has_an_answer_and_no_answer_is_stale(self) -> None:
        notes = [p.source[len(_PREFIX):] for p in SQLQUERY_BLOCKS]
        self.assertTrue(all(p.source.startswith(_PREFIX) for p in SQLQUERY_BLOCKS))
        self.assertEqual(len(notes), len(set(notes)))
        self.assertEqual(set(notes), set(SQLQUERY_ROWS))

    def test_a_length_a_person_will_finish(self) -> None:
        for p in SQLQUERY_BLOCKS:
            lines = [ln for ln in p.text.splitlines() if ln.strip()]
            with self.subTest(block=p.source):
                self.assertGreaterEqual(len(lines), 4)
                self.assertLessEqual(len(lines), 12)
                self.assertTrue(_typeable(p.text))
                self.assertNotIn("\t", p.text)
                self.assertTrue(p.text.rstrip().endswith(";"))

    def test_every_block_returns_the_rows_worked_out(self) -> None:
        for p in SQLQUERY_BLOCKS:
            note = p.source[len(_PREFIX):]
            with self.subTest(block=note):
                db = sqlite3.connect(":memory:")
                try:
                    db.executescript(SCHEMA)
                    self.assertEqual(repr(db.execute(p.text).fetchall()), SQLQUERY_ROWS[note])
                finally:
                    db.close()


class RegistrationTests(unittest.TestCase):
    def test_registered_beside_sql_lore(self) -> None:
        from code_coach.typing.drills import BESIDE_LORE, THEMES_BY_ID

        theme = THEMES_BY_ID["sqlquery"]
        self.assertEqual((theme.language, theme.passages, theme.blocks), ("sql", SQLQUERY_LINES, SQLQUERY_BLOCKS))
        self.assertIn("sqlquery", BESIDE_LORE["sql"])


if __name__ == "__main__":
    unittest.main()
