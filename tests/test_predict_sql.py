"""Predict the output, in SQL: the rules of tests/test_predict_dart2.py
applied to SQL_PUZZLES on its own (imported directly, so these hold
before the set is registered on the Predict screen).

The load-bearing test runs each script through the real SQLite runner
and compares with the hand-worked answer.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code
from code_coach.kata.predict import PUZZLES, language_of, predict_families
from code_coach.kata.predict_sql import SQL_PUZZLES

FAMILY = "SQL"


class SqlPuzzleTests(unittest.TestCase):
    def test_sqlite_agrees_with_every_written_answer(self) -> None:
        for p in SQL_PUZZLES:
            with self.subTest(puzzle=p.id):
                stdout, stderr, code = run_code(p.code, language="sql")
                self.assertEqual(code, 0, (stderr or stdout)[:300])
                got = "\n".join(l.rstrip() for l in stdout.strip().splitlines())
                self.assertEqual(
                    got, p.expect,
                    f"{p.id}: SQLite prints {got!r} and the file says {p.expect!r}")

    def test_the_script_is_one_statement_so_only_the_table_prints(self) -> None:
        for p in SQL_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertEqual(p.code.strip().rstrip(";").count(";"), 0)
                self.assertNotIn("affected", p.expect)

    def test_every_puzzle_explains_itself(self) -> None:
        for p in SQL_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.name.strip())
                self.assertTrue(p.why.strip())
                self.assertTrue(p.expect.strip())
                self.assertEqual(p.family, FAMILY)
                self.assertEqual(p.language, "sql")
                self.assertIn("SELECT", p.code)

    def test_every_snippet_is_short(self) -> None:
        for p in SQL_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertLessEqual(len(p.code.splitlines()), 14)

    def test_the_set_is_fifteen_puzzles_with_sql_ids(self) -> None:
        self.assertEqual(len(SQL_PUZZLES), 15)
        for p in SQL_PUZZLES:
            self.assertTrue(p.id.startswith("predict-sql-"))

    def test_ids_are_unique_and_not_taken_elsewhere(self) -> None:
        ids = [p.id for p in SQL_PUZZLES]
        self.assertEqual(len(ids), len(set(ids)))
        others = {p.id for p in PUZZLES if p not in SQL_PUZZLES}
        self.assertFalse(set(ids) & others)

    def test_a_multi_row_answer_has_an_order_by(self) -> None:
        for p in SQL_PUZZLES:
            with self.subTest(puzzle=p.id):
                if len(p.expect.splitlines()) > 3:
                    self.assertIn("ORDER BY", p.code)

    def test_the_family_is_not_claimed_by_another_language(self) -> None:
        if FAMILY in predict_families():
            self.assertEqual(language_of(FAMILY), "sql")


class SqlLevelTests(unittest.TestCase):
    def test_every_level_is_in_range_and_spread(self) -> None:
        levels = {p.level for p in SQL_PUZZLES}
        self.assertEqual(levels, {1, 2, 3, 4, 5})

    def test_the_file_is_written_least_surprising_first(self) -> None:
        levels = [p.level for p in SQL_PUZZLES]
        self.assertEqual(levels, sorted(levels))


if __name__ == "__main__":
    unittest.main()


# -- Marking: a SQL answer is its rows' values -----------------------------------------------------------------

from code_coach.kata.predict_sql import sql_rows, sql_same  # noqa: E402


class MarkingTests(unittest.TestCase):
    """Typing a result table's header, dash line and column alignment is not the question: only the values are."""

    def setUp(self) -> None:
        self.expect = {p.id: p.expect for p in SQL_PUZZLES}

    def test_every_expect_marks_itself_right(self) -> None:
        for p in SQL_PUZZLES:
            self.assertTrue(sql_same(p.expect, p.expect), p.id)

    def test_the_values_alone_are_enough_and_the_header_is_optional(self) -> None:
        e = self.expect["predict-sql-count-null"]
        self.assertTrue(sql_same("4 2", e))
        self.assertTrue(sql_same("n m\n4 2", e))
        self.assertTrue(sql_same("  4    2  \n\n", e), "spacing and blank lines are not the question")

    def test_a_wrong_value_or_a_missing_row_still_fails(self) -> None:
        e = self.expect["predict-sql-count-null"]
        self.assertFalse(sql_same("4 3", e))
        self.assertFalse(sql_same("2 4", e), "column order is the question")
        r = self.expect["predict-sql-running-sum"]
        self.assertTrue(sql_same("1 4 4\n2 5 14\n2 5 14\n3 1 15", r))
        self.assertFalse(sql_same("1 4 4\n2 5 9\n2 5 14\n3 1 15", r), "the peer-inclusive running sum is the trap")
        self.assertFalse(sql_same("1 4 4\n2 5 14\n3 1 15", r), "a row left out")

    def test_no_rows_is_blank_or_the_runners_words(self) -> None:
        e = self.expect["predict-sql-not-in-null"]
        self.assertEqual(sql_rows(e), [])
        self.assertTrue(sql_same("", e))
        self.assertTrue(sql_same("(no rows)", e))
        self.assertFalse(sql_same("1", e))


class RouteTests(unittest.TestCase):
    """The puzzles are registered, served under SQL, and the server marks a values-only answer right."""

    def test_sql_puzzles_are_served_and_marked_by_their_values(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import PredictCheckRequest
        from code_coach.kata.predict import PUZZLES

        self.assertTrue({p.id for p in SQL_PUZZLES} <= {p.id for p in PUZZLES}, "registered in Predict")
        listed = server.predict_list()
        sql_families = [f for f in listed["families"] if f["language"] == "sql"]
        self.assertTrue(sql_families, "a SQL family is offered")
        ok = server.predict_check(PredictCheckRequest(puzzle_id="predict-sql-count-null", guess="4 2"))
        self.assertTrue(ok.passed)
        bad = server.predict_check(PredictCheckRequest(puzzle_id="predict-sql-count-null", guess="4 3"))
        self.assertFalse(bad.passed)
        # the other languages are still marked line by line, exactly
        other = next(p for p in PUZZLES if p.language == "python")
        self.assertTrue(server.predict_check(PredictCheckRequest(puzzle_id=other.id, guess=other.expect)).passed)
