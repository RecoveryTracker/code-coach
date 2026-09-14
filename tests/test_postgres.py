"""The PostgreSQL runner.

Split into what needs a server and what does not. The statement
splitter and the error tidier are ordinary functions and are tested
ordinarily; everything else needs a live PostgreSQL and is skipped
without one, because this project runs on machines that do not have it
and a red suite for a missing optional toolchain trains people to
ignore red.

The load-bearing test is `test_a_change_does_not_outlive_the_go`. The
whole promise of the mode is that practice cannot wreck the data — you
can run an UPDATE with no WHERE, watch it do exactly what it really
does, and start the next exercise from the same place. That promise is
one missing ROLLBACK away from being false, and false quietly: the
first go would look perfect and every go afterwards would be wrong.
"""

from __future__ import annotations

import unittest

from code_coach import pg_server
from code_coach.pg_runner import _split, _tidy_error, run_postgres

HAS_SERVER = pg_server.available() and pg_server.initialised()
WHY_NOT = "no local PostgreSQL — run tools/get_postgres.py"


class SplitTests(unittest.TestCase):
    """Semicolons that end a statement, and semicolons that do not."""

    def test_plain_statements(self) -> None:
        self.assertEqual(
            _split("SELECT 1; SELECT 2;"), ["SELECT 1", "SELECT 2"])

    def test_a_trailing_semicolon_is_optional(self) -> None:
        self.assertEqual(_split("SELECT 1"), ["SELECT 1"])

    def test_blank_statements_are_dropped(self) -> None:
        self.assertEqual(_split(";;  SELECT 1 ;; "), ["SELECT 1"])

    def test_a_semicolon_inside_a_string_is_not_a_split(self) -> None:
        self.assertEqual(
            _split("SELECT 'a;b' AS x;"), ["SELECT 'a;b' AS x"])

    def test_a_doubled_quote_inside_a_string(self) -> None:
        """'' is an escaped quote, not the end of the string — getting
        this wrong splits the rest of the query into fragments."""
        self.assertEqual(
            _split("SELECT 'it''s; fine' AS x;"),
            ["SELECT 'it''s; fine' AS x"])

    def test_a_semicolon_inside_a_quoted_identifier(self) -> None:
        self.assertEqual(
            _split('SELECT 1 AS "od;d";'), ['SELECT 1 AS "od;d"'])

    def test_a_dollar_quoted_body_survives(self) -> None:
        body = "DO $$ BEGIN PERFORM 1; PERFORM 2; END $$;"
        self.assertEqual(_split(body), ["DO $$ BEGIN PERFORM 1; PERFORM 2; END $$"])


class ErrorTests(unittest.TestCase):
    def test_the_psql_prefix_is_taken_off(self) -> None:
        """psql names the script it was reading — stdin — and the line
        number counts the BEGIN the runner added, so it is one past
        what the person wrote. Both are noise."""
        tidied = _tidy_error(
            'psql:<stdin>:3: ERROR:  column "nope" does not exist')
        self.assertNotIn("stdin", tidied)
        self.assertIn("column", tidied)

    def test_nothing_at_all_still_says_something(self) -> None:
        self.assertTrue(_tidy_error(""))


@unittest.skipUnless(HAS_SERVER, WHY_NOT)
class RunnerTests(unittest.TestCase):
    def test_a_select_comes_back_as_a_table(self) -> None:
        out, err, code = run_postgres(
            "SELECT name FROM users WHERE city = 'Denver' ORDER BY name;")
        self.assertEqual(code, 0, err)
        self.assertIn("Alex", out)
        self.assertIn("Casey", out)
        self.assertIn("name", out.splitlines()[0])

    def test_no_rows_says_so_rather_than_nothing(self) -> None:
        out, _err, code = run_postgres(
            "SELECT name FROM users WHERE city = 'Atlantis';")
        self.assertEqual(code, 0)
        self.assertIn("no rows", out)

    def test_null_is_visible(self) -> None:
        """An empty cell and a NULL are different facts, and SQL is
        largely about the difference."""
        out, _err, code = run_postgres(
            "SELECT email FROM users WHERE id = 2;")
        self.assertEqual(code, 0)
        self.assertIn("NULL", out)

    def test_an_error_is_reported_without_a_traceback(self) -> None:
        out, err, code = run_postgres("SELECT nope FROM users;")
        self.assertEqual(code, 1)
        self.assertIn("nope", err)
        self.assertNotIn("Traceback", err)
        self.assertEqual(out, "")

    def test_statements_share_one_session(self) -> None:
        """An INSERT followed by a SELECT is one thought and has to see
        its own work — which a process per statement would not."""
        out, err, code = run_postgres(
            "INSERT INTO orders (user_id, item, price) "
            "VALUES (1, 'Testing', 1.00);"
            " SELECT count(*) AS n FROM orders WHERE item = 'Testing';")
        self.assertEqual(code, 0, err)
        self.assertIn("1", out.splitlines()[-1])

    def test_a_change_does_not_outlive_the_go(self) -> None:
        """The promise the whole mode rests on.

        Run the worst thing a person can run, see that it really did
        it, and then find the data exactly as it was. One missing
        ROLLBACK and the first go looks perfect while every go after it
        is wrong.
        """
        before, _err, _code = run_postgres(
            "SELECT city FROM users WHERE id = 1;")
        self.assertIn("Denver", before)

        during, err, code = run_postgres(
            "UPDATE users SET city = 'Nowhere';"
            " SELECT city FROM users WHERE id = 1;")
        self.assertEqual(code, 0, err)
        self.assertIn("Nowhere", during)

        after, _err, _code = run_postgres(
            "SELECT city FROM users WHERE id = 1;")
        self.assertIn("Denver", after)
        self.assertNotIn("Nowhere", after)

    def test_an_insert_does_not_outlive_the_go_either(self) -> None:
        run_postgres(
            "INSERT INTO orders (user_id, item, price) "
            "VALUES (1, 'Ghost', 1.00);")
        out, _err, _code = run_postgres(
            "SELECT count(*) AS n FROM orders WHERE item = 'Ghost';")
        self.assertIn("0", out.splitlines()[-1])

    def test_an_empty_script_says_what_to_do(self) -> None:
        _out, err, code = run_postgres("   ")
        self.assertEqual(code, 0)
        self.assertIn("write a query", err)


@unittest.skipUnless(HAS_SERVER, WHY_NOT)
class DialectTests(unittest.TestCase):
    """The reason this is not just SQLite with a different name.

    Every one of these is a thing SQLite cannot do, and every one is
    worth a job interview. If these ever stop working, the mode has
    quietly become a worse copy of the SQL one.
    """

    def _ok(self, sql: str) -> str:
        out, err, code = run_postgres(sql)
        self.assertEqual(code, 0, f"{sql}\n{err}")
        return out

    def test_returning(self) -> None:
        out = self._ok(
            "INSERT INTO orders (user_id, item, price) "
            "VALUES (2, 'Cable', 9.99) RETURNING item, price;")
        self.assertIn("Cable", out)
        self.assertIn("9.99", out)

    def test_ilike(self) -> None:
        out = self._ok("SELECT name FROM users WHERE name ILIKE 'a%';")
        self.assertIn("Alex", out)

    def test_cast_syntax(self) -> None:
        self.assertIn("50", self._ok("SELECT '42'::int + 8 AS answer;"))

    def test_generate_series(self) -> None:
        out = self._ok("SELECT n FROM generate_series(1, 4) AS n;")
        self.assertIn("4", out)

    def test_jsonb(self) -> None:
        out = self._ok(
            "SELECT name FROM users WHERE profile->>'plan' = 'pro' "
            "ORDER BY name;")
        self.assertIn("Alex", out)
        self.assertIn("Casey", out)

    def test_arrays(self) -> None:
        out = self._ok(
            "SELECT name FROM users WHERE 'admin' = ANY(tags) ORDER BY name;")
        self.assertIn("Erin", out)

    def test_upsert(self) -> None:
        out = self._ok(
            "INSERT INTO users (id, name) VALUES (1, 'Nope') "
            "ON CONFLICT (id) DO UPDATE SET name = 'Updated' "
            "RETURNING name;")
        self.assertIn("Updated", out)

    def test_window_function(self) -> None:
        out = self._ok(
            "SELECT item, rank() OVER (ORDER BY price DESC) AS r "
            "FROM orders LIMIT 2;")
        self.assertIn("Desk", out)

    def test_a_statement_that_cannot_be_rolled_back_says_so(self) -> None:
        """VACUUM cannot run in a transaction, and the transaction is
        what keeps the data safe. The trade is worth it and the error
        should be PostgreSQL's own words rather than a mystery."""
        _out, err, code = run_postgres("VACUUM users;")
        self.assertEqual(code, 1)
        self.assertIn("transaction", err.lower())


@unittest.skipUnless(HAS_SERVER, WHY_NOT)
class EngineTests(unittest.TestCase):
    def test_run_code_routes_postgresql(self) -> None:
        from code_coach.engine import run_code

        out, err, code = run_code(
            "SELECT 1 AS one;", language="postgresql")
        self.assertEqual(code, 0, err)
        self.assertIn("one", out)

    def test_sql_and_postgresql_are_different_runners(self) -> None:
        """The same query, and only one of them knows ::."""
        from code_coach.engine import run_code

        _out, _err, pg_code = run_code(
            "SELECT '42'::int AS n;", language="postgresql")
        _out2, _err2, sqlite_code = run_code(
            "SELECT '42'::int AS n;", language="sql")
        self.assertEqual(pg_code, 0)
        self.assertEqual(sqlite_code, 1)


class LanguageTests(unittest.TestCase):
    """True without a server, because the entry has to be honest on a
    machine that has not set one up."""

    def test_postgresql_is_offered(self) -> None:
        from code_coach.languages import languages_payload

        entry = next(
            (x for x in languages_payload() if x["id"] == "postgresql"), None)
        self.assertIsNotNone(entry)
        self.assertEqual(entry["name"], "PostgreSQL")

    def test_it_claims_only_what_it_has(self) -> None:
        """It has a runner and nothing else yet — no workbook pages, no
        cheat sheet, no taught course. Claiming otherwise in the picker
        is how somebody opens an empty screen."""
        from code_coach.languages import LANGUAGES

        entry = next(x for x in LANGUAGES if x.id == "postgresql")
        self.assertEqual(set(entry.ready), {"runner"})


if __name__ == "__main__":
    unittest.main()
