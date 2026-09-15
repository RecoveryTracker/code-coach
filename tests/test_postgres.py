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
        """Whatever the picker claims has to actually be there.

        This pinned the claim to exactly {"runner"} while that was the
        truth, and then failed the moment the pages landed — which was
        testing the content rather than the rule. What it means to say
        is that a claim in the picker is a promise, and opening an empty
        screen is what a broken one looks like. So each claim is now
        checked against the thing it claims.
        """
        from code_coach.languages import LANGUAGES
        from code_coach.workbook import pages

        entry = next(x for x in LANGUAGES if x.id == "postgresql")
        claims = set(entry.ready)
        self.assertIn("runner", claims)

        has_pages = bool(pages("postgresql"))
        self.assertEqual(
            "workbook" in claims, has_pages,
            "the picker and the workbook disagree about whether there "
            "are pages")

        from code_coach.typing.drills import THEMES

        has_theme = any(t.id == "postgresqlcode" for t in THEMES)
        self.assertEqual(
            "typing" in claims, has_theme,
            "the picker and the typing themes disagree about whether "
            "there is material to type")

        # The ones it genuinely does not have. Listed rather than
        # derived, so adding a claim means the thing has to arrive with
        # it — but only for the two that have not arrived. This said
        # "typing" too, which was true when it was written and became a
        # test of the content rather than of the rule the moment the
        # snippets landed.
        for absent in ("fundamentals", "reference"):
            self.assertNotIn(absent, claims)


if __name__ == "__main__":
    unittest.main()


@unittest.skipUnless(HAS_SERVER, WHY_NOT)
class WorkbookTests(unittest.TestCase):
    """Every page's reference query, run against the real database.

    This is the load-bearing test of the PostgreSQL pages, and it is
    load-bearing in a particular way: the expected output is computed in
    Python from a hand-written mirror of the rows, and the query is
    executed by PostgreSQL. Two genuinely different implementations, so
    agreement means something — where "the query, compared against what
    the query returned" would mean nothing at all and would pass just as
    happily with every answer wrong.

    It has already earned its keep twice. It caught that a sequence is
    not rolled back, so every RETURNING exercise was handing back a
    different id each go and could not have an answer; and it caught two
    exercises where the item name had been passed where the price
    belonged, on a page where fourteen of sixteen never printed the
    price and hid it.
    """

    def _exercises(self):
        from code_coach.workbook import pages

        return [(page, ex) for page in pages("postgresql")
                for ex in page.exercises]

    def test_there_are_pages(self) -> None:
        from code_coach.workbook import pages

        found = pages("postgresql")
        self.assertGreaterEqual(len(found), 7)
        for page in found:
            with self.subTest(page=page.id):
                self.assertGreaterEqual(len(page.exercises), 10)

    def test_every_reference_returns_what_is_expected(self) -> None:
        from code_coach.engine import run_code

        for page, ex in self._exercises():
            with self.subTest(exercise=ex.id):
                query = ex.answer("postgresql")
                self.assertTrue(query, f"{ex.id} has no reference query")
                out, err, code = run_code(query, language="postgresql")
                self.assertEqual(code, 0, f"{query}\n{err}")
                self.assertEqual(
                    out.strip(), ex.expect.strip(),
                    f"{ex.id}: {query}")

    def test_the_mirror_matches_the_real_rows(self) -> None:
        """The Python copy of the data has to be the data.

        Everything above rests on it, and it is written out by hand — so
        if the schema in tools/get_postgres.py ever changes and this does
        not, every expectation silently describes a database that is not
        there.
        """
        from code_coach.engine import run_code
        from code_coach.workbook.emit_pg import USERS, pg_text

        out, err, code = run_code(
            "SELECT id, name, city, age, email, active, joined, tags, "
            "profile FROM users ORDER BY id;",
            language="postgresql")
        self.assertEqual(code, 0, err)
        lines = out.strip().splitlines()[2:]   # past header and rule
        self.assertEqual(len(lines), len(USERS))
        for row, user in zip(lines, USERS):
            with self.subTest(user=user["id"]):
                for field in ("name", "city", "age", "joined"):
                    self.assertIn(pg_text(user[field]), row)

    def test_a_write_page_gives_the_same_id_every_go(self) -> None:
        """The RETURNING page is only answerable because the sequence is
        put back at the start of each run. Without that the id climbs,
        and an exercise whose answer changes every time cannot be
        practised — which is the whole point of the mode."""
        from code_coach.engine import run_code
        from code_coach.workbook import pages

        page = next(p for p in pages("postgresql") if p.id == "pg-returning")
        query = page.exercises[0].answer("postgresql")
        seen = set()
        for _ in range(3):
            out, err, code = run_code(query, language="postgresql")
            self.assertEqual(code, 0, err)
            seen.add(out.strip())
        self.assertEqual(len(seen), 1, f"the answer changed between goes: {seen}")

    def test_the_pages_are_only_the_differences(self) -> None:
        """If a page here teaches plain SELECT or GROUP BY, it belongs in
        the SQL pages and is twenty exercises of something already
        taught."""
        from code_coach.workbook import pages

        names = " ".join(p.name.lower() for p in pages("postgresql"))
        for already_taught in ("group by", "join", "order by"):
            self.assertNotIn(already_taught, names)
