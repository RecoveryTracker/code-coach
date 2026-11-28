"""SQL (SQLite) code magnets.

Ten short scripts of at most twelve lines, in the shapes where the order of
SQL statements, and of the clauses inside one, decides the result: a table
before the rows it holds, the rows before the SELECT that reads them, an
UPDATE or DELETE before or after the query that shows its effect, the clauses
of one SELECT in their fixed order (spread over lines, so a wrong order does
not parse), a JOIN's ON after its table, a transaction that hides an insert,
a CTE before the query that uses it, INSERT ... SELECT copying rows, and a
view that reads live data.

The marker runs what you arranged through the app's SQLite runner
(`code_coach/sql_runner.py`) and compares what it printed with `expect`,
exactly. The runner prints every statement: "-1 row(s) affected." for a
CREATE (and for BEGIN / ROLLBACK), "N row(s) affected." for an INSERT, UPDATE
or DELETE, and a SELECT as a padded table with a header and a dash line.
Statements are separated by a blank line. Statements are split on `;`, so a
statement may run over several lines and only its last line ends in `;`.

Every `expect` was worked out by hand and is held to the real runner by
tests/test_magnets_sql.py. The table names avoid `users` and `orders`, which
the runner preloads.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m

FAMILY = "SQL"


def _code(*lines: str) -> str:
    return "\n".join(lines)


def _out(*blocks: str) -> str:
    return "\n\n".join(blocks)


CREATED = "-1 row(s) affected."


SQL_MAGNETS: tuple[Magnet, ...] = (
    _m(
        id="magnet-sql-create-insert-select",
        plan=(
            ("Make the table", 1),
            ("Add two rows", 2),
            ("Read them back", 1),
        ),
        level=1,
        name="Create, fill, read",
        family=FAMILY,
        language="sql",
        note=(
            "A table has to exist before anything can go into it, and the rows "
            "have to be in it before a SELECT can show them. Put the SELECT "
            "first and SQLite says there is no such table; put an INSERT above "
            "the CREATE and it says the same. The two INSERTs keep the order "
            "they are written in, so cat is listed before bird."
        ),
        code=_code(
            "CREATE TABLE pets (name TEXT, legs INTEGER);",
            "INSERT INTO pets VALUES ('cat', 4);",
            "INSERT INTO pets VALUES ('bird', 2);",
            "SELECT name, legs FROM pets;",
        ),
        expect=_out(
            CREATED,
            "1 row(s) affected.",
            "1 row(s) affected.",
            "name  legs\n----  ----\ncat   4\nbird  2",
        ),
    ),
    _m(
        id="magnet-sql-update-then-select",
        plan=(
            ("Make the table", 1),
            ("Add a row", 1),
            ("Change it", 1),
            ("Read the result", 1),
        ),
        level=1,
        name="An UPDATE before the SELECT",
        family=FAMILY,
        language="sql",
        note=(
            "A SELECT shows the table as it is at that moment. Run it above the "
            "UPDATE and it still shows 5 apples; run it below and it shows 9. "
            "Nothing errors either way, which is what makes this one worth "
            "getting right: the wrong order is a query that runs and tells you "
            "the old number."
        ),
        code=_code(
            "CREATE TABLE stock (item TEXT, qty INTEGER);",
            "INSERT INTO stock VALUES ('apple', 5);",
            "UPDATE stock SET qty = 9 WHERE item = 'apple';",
            "SELECT item, qty FROM stock;",
        ),
        expect=_out(
            CREATED,
            "1 row(s) affected.",
            "1 row(s) affected.",
            "item   qty\n-----  ---\napple  9",
        ),
    ),
    _m(
        id="magnet-sql-select-clause-order",
        plan=(
            ("Make the table", 1),
            ("Fill it", 1),
            ("Choose the columns and the table", 2),
            ("Filter, sort, then cut it short", 3),
        ),
        level=2,
        name="Clauses of one SELECT in order",
        family=FAMILY,
        language="sql",
        note=(
            "One SELECT has a fixed clause order: SELECT, FROM, WHERE, then "
            "ORDER BY, then LIMIT. Any other order does not parse, so SQLite "
            "stops with a syntax error instead of guessing. The order also "
            "tells you what happens when: WHERE throws rows out first, ORDER BY "
            "sorts what is left, and LIMIT keeps only the top two of that."
        ),
        code=_code(
            "CREATE TABLE scores (player TEXT, pts INTEGER);",
            "INSERT INTO scores VALUES ('ann', 7), ('bo', 3), ('cy', 9), ('di', 5);",
            "SELECT player, pts",
            "FROM scores",
            "WHERE pts > 4",
            "ORDER BY pts DESC",
            "LIMIT 2;",
        ),
        expect=_out(
            CREATED,
            "4 row(s) affected.",
            "player  pts\n------  ---\ncy      9\nann     7",
        ),
    ),
    _m(
        id="magnet-sql-group-having",
        plan=(
            ("Make the table", 1),
            ("Fill it", 1),
            ("Pick what to show", 1),
            ("Which table", 1),
            ("Group the rows", 1),
            ("Keep big groups and sort", 2),
        ),
        level=2,
        name="GROUP BY, then HAVING, then ORDER BY",
        family=FAMILY,
        language="sql",
        note=(
            "GROUP BY collapses rows into one per region, and HAVING filters "
            "those groups, so HAVING can only come after the GROUP BY it "
            "judges; ORDER BY comes last of all. Written in any other order the "
            "statement does not parse. North adds up to 16 and east to 20, "
            "while south's 7 is thrown out by HAVING."
        ),
        code=_code(
            "CREATE TABLE sales (region TEXT, amount INTEGER);",
            "INSERT INTO sales VALUES ('north', 10), ('south', 4), ('north', 6), ('south', 3), ('east', 20);",
            "SELECT region, SUM(amount) AS total",
            "FROM sales",
            "GROUP BY region",
            "HAVING total > 10",
            "ORDER BY total;",
        ),
        expect=_out(
            CREATED,
            "5 row(s) affected.",
            "region  total\n------  -----\nnorth   16\neast    20",
        ),
    ),
    _m(
        id="magnet-sql-delete-between-counts",
        plan=(
            ("Make the table", 1),
            ("Fill it", 1),
            ("Count what is there", 1),
            ("Remove the finished tasks", 1),
            ("Count again", 1),
        ),
        level=3,
        name="A DELETE between two counts",
        family=FAMILY,
        language="sql",
        note=(
            "The two counts differ only by their column name, and the DELETE has "
            "to sit between them for the story to make sense: 4 rows at the "
            "start, 2 once the finished tasks are gone. Move the DELETE above "
            "the first count and both counts say 2. Nothing fails, the "
            "numbers are just quietly wrong."
        ),
        code=_code(
            "CREATE TABLE tasks (id INTEGER, done INTEGER);",
            "INSERT INTO tasks VALUES (1, 1), (2, 0), (3, 1), (4, 0);",
            "SELECT COUNT(*) AS at_start FROM tasks;",
            "DELETE FROM tasks WHERE done = 1;",
            "SELECT COUNT(*) AS at_end FROM tasks;",
        ),
        expect=_out(
            CREATED,
            "4 row(s) affected.",
            "at_start\n--------\n4",
            "2 row(s) affected.",
            "at_end\n------\n2",
        ),
    ),
    _m(
        id="magnet-sql-join-on",
        plan=(
            ("Two tables", 2),
            ("Rows for each", 2),
            ("Choose the columns", 1),
            ("Join the tables on the shared id", 3),
            ("Sort the result", 1),
        ),
        level=3,
        name="A JOIN with its ON",
        family=FAMILY,
        language="sql",
        note=(
            "Both tables must exist before either is filled, and both must be "
            "filled before the SELECT. Inside the query, the ON belongs "
            "directly after the JOIN it describes, which is after FROM: put ON "
            "first and SQLite cannot parse it. The two CREATEs are "
            "independent, and so are the two INSERTs, as long as each follows its "
            "own table."
        ),
        code=_code(
            "CREATE TABLE authors (id INTEGER, name TEXT);",
            "CREATE TABLE books (title TEXT, author_id INTEGER);",
            "INSERT INTO authors VALUES (1, 'Orwell'), (2, 'Austen');",
            "INSERT INTO books VALUES ('Emma', 2), ('1984', 1), ('Persuasion', 2);",
            "SELECT books.title, authors.name",
            "FROM books",
            "JOIN authors",
            "ON authors.id = books.author_id",
            "ORDER BY books.title;",
        ),
        expect=_out(
            CREATED,
            CREATED,
            "2 row(s) affected.",
            "3 row(s) affected.",
            "title       name\n----------  ------\n1984        Orwell\nEmma        Austen\nPersuasion  Austen",
        ),
    ),
    _m(
        id="magnet-sql-rollback",
        plan=(
            ("Make the table", 1),
            ("Open a transaction", 1),
            ("A draft row, taken back", 2),
            ("A row that stays", 1),
            ("Read the table", 1),
        ),
        level=4,
        name="A transaction that undoes an insert",
        family=FAMILY,
        language="sql",
        note=(
            "Everything between BEGIN and ROLLBACK is undone, so the draft "
            "row never shows. Order is the whole puzzle: the draft insert has to "
            "sit inside the BEGIN and ROLLBACK pair, and the final insert "
            "has to come after the ROLLBACK, or it is rolled back with the draft "
            "and the table ends up empty. Insert the draft outside the pair and "
            "it stays."
        ),
        code=_code(
            "CREATE TABLE notes (txt TEXT);",
            "BEGIN;",
            "INSERT INTO notes VALUES ('draft');",
            "ROLLBACK;",
            "INSERT INTO notes VALUES ('final');",
            "SELECT txt FROM notes;",
        ),
        expect=_out(
            CREATED,
            CREATED,
            "1 row(s) affected.",
            CREATED,
            "1 row(s) affected.",
            "txt\n-----\nfinal",
        ),
    ),
    _m(
        id="magnet-sql-cte-before-query",
        plan=(
            ("Make the table", 1),
            ("Fill it", 1),
            ("Name a query to reuse", 1),
            ("Query that name", 2),
            ("Keep the big ones, biggest first", 2),
        ),
        level=4,
        name="A WITH clause before its query",
        family=FAMILY,
        language="sql",
        note=(
            "A CTE is a named query that exists only for the statement it "
            "begins, so the WITH line has to open the statement and the SELECT "
            "that uses `totals` has to follow it. Put that SELECT first and "
            "there is no `totals` yet: no such table. Inside the SELECT the usual "
            "order still holds, with WHERE before ORDER BY. Oslo's two trips add "
            "to 20, Rome's to 35, and Pisa's 14 is dropped."
        ),
        code=_code(
            "CREATE TABLE trips (city TEXT, km INTEGER);",
            "INSERT INTO trips VALUES ('Oslo', 12), ('Rome', 30), ('Oslo', 8), ('Rome', 5), ('Pisa', 14);",
            "WITH totals AS (SELECT city, SUM(km) AS km_total FROM trips GROUP BY city)",
            "SELECT city, km_total",
            "FROM totals",
            "WHERE km_total > 15",
            "ORDER BY km_total DESC;",
        ),
        expect=_out(
            CREATED,
            "5 row(s) affected.",
            "city  km_total\n----  --------\nRome  35\nOslo  20",
        ),
    ),
    _m(
        id="magnet-sql-insert-select-copy",
        plan=(
            ("Two tables", 2),
            ("Fill the source", 1),
            ("Copy the ops rows across", 3),
            ("Read the copy", 1),
        ),
        level=5,
        name="INSERT ... SELECT copying rows",
        family=FAMILY,
        language="sql",
        note=(
            "INSERT ... SELECT copies whatever the SELECT finds at that moment. "
            "Run it before the source table is filled and it copies nothing: "
            "0 rows affected, and the final read shows no rows, with no error "
            "at all. The SELECT part is a clause chain of its own (SELECT, "
            "FROM, WHERE) that continues the INSERT line above it. The two "
            "CREATEs can go in either order."
        ),
        code=_code(
            "CREATE TABLE staff (name TEXT, team TEXT);",
            "CREATE TABLE ops (name TEXT);",
            "INSERT INTO staff VALUES ('Ada', 'ops'), ('Bo', 'dev'), ('Cy', 'ops');",
            "INSERT INTO ops SELECT name",
            "FROM staff",
            "WHERE team = 'ops';",
            "SELECT name FROM ops ORDER BY name DESC;",
        ),
        expect=_out(
            CREATED,
            CREATED,
            "3 row(s) affected.",
            "2 row(s) affected.",
            "name\n----\nCy\nAda",
        ),
    ),
    _m(
        id="magnet-sql-view-reads-live",
        plan=(
            ("Make the table", 1),
            ("First rows", 1),
            ("A saved query over the table", 1),
            ("More rows", 1),
            ("Read through the view", 1),
        ),
        level=5,
        name="A view that reads live data",
        family=FAMILY,
        language="sql",
        note=(
            "A view stores a query, not rows, so it must exist before you "
            "SELECT from it: read it first and you get no such table. Because "
            "it reads live, the second INSERT can go before or after the "
            "CREATE VIEW and the rug still shows up, as long as it lands before the "
            "final SELECT. Put that SELECT above the second INSERT and the "
            "rug is missing."
        ),
        code=_code(
            "CREATE TABLE prices (item TEXT, cents INTEGER);",
            "INSERT INTO prices VALUES ('pen', 150), ('ink', 900), ('pad', 450);",
            "CREATE VIEW pricey AS SELECT item, cents FROM prices WHERE cents > 400;",
            "INSERT INTO prices VALUES ('pin', 50), ('rug', 5000);",
            "SELECT item, cents FROM pricey ORDER BY cents;",
        ),
        expect=_out(
            CREATED,
            "3 row(s) affected.",
            CREATED,
            "2 row(s) affected.",
            "item  cents\n----  -----\npad   450\nink   900\nrug   5000",
        ),
    ),
)
