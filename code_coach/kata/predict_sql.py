"""Predict the output, in SQL (SQLite's SQL).

Every script is ONE statement: the Predict runner (`engine.run_code(...,
language="sql")`) prints a block for every statement it runs ("-1 row(s)
affected." for a CREATE TABLE), so the tables are built inline with
`WITH t(x) AS (VALUES ...)` and the only output is the result table of
the query. That table is fixed width: a header line, a dashes line, then
one line per row, columns separated by two spaces, NULL printed as NULL,
a real printed as Python prints a float (3.0, 3.5), no trailing spaces.

Each answer was worked out by hand first; the tests then run SQLite and
must agree.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p


SQL_PUZZLES: tuple[Puzzle, ...] = (
    _p(
        id="predict-sql-count-null",
        level=1,
        language="sql",
        name="Counting what is not there",
        family="SQL",
        code=(
            "WITH t(x) AS (VALUES (1), (NULL), (3), (NULL))\n"
            "SELECT COUNT(*) AS n, COUNT(x) AS m FROM t;"
        ),
        expect="n  m\n-  -\n4  2",
        why=(
            "COUNT(*) counts rows; COUNT(x) counts only the rows where x "
            "is not NULL. Every aggregate except COUNT(*) skips NULLs."
        ),
    ),
    _p(
        id="predict-sql-int-division",
        level=1,
        language="sql",
        name="Seven over two",
        family="SQL",
        code="SELECT 7 / 2 AS a, 7 / 2.0 AS b, 7 % 2 AS c;",
        expect="a  b    c\n-  ---  -\n3  3.5  1",
        why=(
            "Two integers divide as integers and the fraction is thrown "
            "away. Make either side a real (2.0) and you get 3.5. % is "
            "the remainder."
        ),
    ),
    _p(
        id="predict-sql-avg-real",
        level=2,
        language="sql",
        name="The average is a real",
        family="SQL",
        code=(
            "WITH t(x) AS (VALUES (1), (2), (3), (6))\n"
            "SELECT SUM(x) AS s, AVG(x) AS a FROM t;"
        ),
        expect="s   a\n--  ---\n12  3.0",
        why=(
            "SUM of integers is an integer, but AVG always gives a real, "
            "so 12 / 4 prints as 3.0 and not 3."
        ),
    ),
    _p(
        id="predict-sql-limit-offset",
        level=2,
        language="sql",
        name="Skip one, take two",
        family="SQL",
        code=(
            "WITH t(x) AS (VALUES (3), (NULL), (1), (2))\n"
            "SELECT x FROM t ORDER BY x LIMIT 2 OFFSET 1;"
        ),
        expect="x\n-\n1\n2",
        why=(
            "SQLite sorts NULL first, so the order is NULL, 1, 2, 3. "
            "OFFSET 1 skips the NULL, and LIMIT 2 takes the next two."
        ),
    ),
    _p(
        id="predict-sql-concat-null",
        level=2,
        language="sql",
        name="Gluing onto nothing",
        family="SQL",
        code=(
            "SELECT 'a' || NULL AS p,\n"
            "       'a' || COALESCE(NULL, '-') AS q;"
        ),
        expect="p     q\n----  --\nNULL  a-",
        why=(
            "Anything joined with NULL by || is NULL. COALESCE swaps a "
            "NULL for the first value that is not, so the second one "
            "joins fine."
        ),
    ),
    _p(
        id="predict-sql-null-compare",
        level=2,
        language="sql",
        name="Not equal to one",
        family="SQL",
        code=(
            "WITH t(x) AS (VALUES (1), (NULL), (3))\n"
            "SELECT x FROM t WHERE x <> 1 ORDER BY x;"
        ),
        expect="x\n-\n3",
        why=(
            "NULL <> 1 is not true, it is NULL (unknown), and WHERE keeps "
            "only rows where the test is true. The NULL row vanishes "
            "from both = 1 and <> 1."
        ),
    ),
    _p(
        id="predict-sql-distinct-null",
        level=2,
        language="sql",
        name="Two nothings",
        family="SQL",
        code=(
            "WITH t(x) AS (VALUES (1), (1), (NULL), (NULL), (2))\n"
            "SELECT DISTINCT x FROM t ORDER BY x;"
        ),
        expect="x\n----\nNULL\n1\n2",
        why=(
            "DISTINCT treats all NULLs as the same value, so they "
            "collapse to one row, and NULL sorts before the numbers."
        ),
    ),
    _p(
        id="predict-sql-like-case",
        level=3,
        language="sql",
        name="LIKE does not care about case",
        family="SQL",
        code=(
            "WITH t(s) AS (VALUES ('Apple'), ('apricot'), ('Banana'))\n"
            "SELECT s, CASE WHEN s LIKE 'a%' THEN 'yes' ELSE 'no' END AS m\n"
            "FROM t ORDER BY s;"
        ),
        expect=(
            "s        m\n"
            "-------  ---\n"
            "Apple    yes\n"
            "Banana   no\n"
            "apricot  yes"
        ),
        why=(
            "LIKE ignores ASCII case, so 'Apple' matches 'a%'. ORDER BY "
            "compares text byte by byte, and capital letters come before "
            "lower case, so 'apricot' sorts last."
        ),
    ),
    _p(
        id="predict-sql-having",
        level=3,
        language="sql",
        name="Filtering the groups",
        family="SQL",
        code=(
            "WITH t(k, v) AS (VALUES ('a', 1), ('a', 5), ('b', 2),\n"
            "                        ('c', 3), ('c', 4), ('c', 9))\n"
            "SELECT k, SUM(v) AS s FROM t\n"
            "GROUP BY k HAVING SUM(v) > 5 ORDER BY k;"
        ),
        expect="k  s\n-  --\na  6\nc  16",
        why=(
            "WHERE filters rows before they are grouped; HAVING filters "
            "the groups after. The sums are a=6, b=2, c=16, so b is "
            "dropped."
        ),
    ),
    _p(
        id="predict-sql-left-join-count",
        level=3,
        language="sql",
        name="The customer with no orders",
        family="SQL",
        code=(
            "WITH u(id, name) AS (VALUES (1, 'Ann'), (2, 'Bo'), (3, 'Cy')),\n"
            "     o(uid, amt) AS (VALUES (1, 10), (1, 5), (3, 7))\n"
            "SELECT name, COUNT(amt) AS n FROM u\n"
            "LEFT JOIN o ON o.uid = u.id GROUP BY name ORDER BY name;"
        ),
        expect="name  n\n----  -\nAnn   2\nBo    0\nCy    1",
        why=(
            "A LEFT JOIN keeps every row from the left table. Bo has no "
            "orders, so the amt side is NULL, and COUNT(amt) skips the "
            "NULL and gives 0. COUNT(*) would have said 1."
        ),
    ),
    _p(
        id="predict-sql-union",
        level=3,
        language="sql",
        name="UNION or UNION ALL",
        family="SQL",
        code=(
            "WITH a(x) AS (VALUES (1), (2), (2)), b(x) AS (VALUES (2), (3))\n"
            "SELECT\n"
            "  (SELECT COUNT(*) FROM (SELECT x FROM a UNION SELECT x FROM b)) AS u,\n"
            "  (SELECT COUNT(*) FROM (SELECT x FROM a UNION ALL SELECT x FROM b)) AS ua;"
        ),
        expect="u  ua\n-  --\n3  5",
        why=(
            "UNION removes duplicates, leaving 1, 2, 3. UNION ALL just "
            "stacks the two lists, so all 3 + 2 = 5 rows stay."
        ),
    ),
    _p(
        id="predict-sql-correlated",
        level=4,
        language="sql",
        name="Above their own average",
        family="SQL",
        code=(
            "WITH e(n, d, s) AS (VALUES ('Ann','x',10), ('Bo','x',20),\n"
            "  ('Cy','y',30), ('Di','y',50), ('Ed','y',40))\n"
            "SELECT n FROM e AS o\n"
            "WHERE s > (SELECT AVG(s) FROM e WHERE d = o.d) ORDER BY n;"
        ),
        expect="n\n--\nBo\nDi",
        why=(
            "The inner query runs once per outer row, with that row's "
            "department. x averages 15, y averages 40. Bo (20) and Di "
            "(50) are above it; Ed is exactly 40, and > is strict."
        ),
    ),
    _p(
        id="predict-sql-left-join-where",
        level=4,
        language="sql",
        name="The WHERE that undid the join",
        family="SQL",
        code=(
            "WITH u(id, name) AS (VALUES (1, 'Ann'), (2, 'Bo'), (3, 'Cy')),\n"
            "     o(uid, amt) AS (VALUES (1, 10), (1, 5), (3, 7))\n"
            "SELECT name, amt FROM u LEFT JOIN o ON o.uid = u.id\n"
            "WHERE amt > 6 ORDER BY name;"
        ),
        expect="name  amt\n----  ---\nAnn   10\nCy    7",
        why=(
            "The LEFT JOIN did make a row for Bo with amt NULL, but WHERE "
            "runs afterwards and NULL > 6 is not true, so that row is "
            "dropped. Ann's 5 goes too. Put the test in ON to keep Bo."
        ),
    ),
    _p(
        id="predict-sql-not-in-null",
        level=5,
        language="sql",
        name="NOT IN and the stray NULL",
        family="SQL",
        code=(
            "WITH a(x) AS (VALUES (1), (2), (3)), b(y) AS (VALUES (1), (NULL))\n"
            "SELECT x FROM a WHERE x NOT IN (SELECT y FROM b) ORDER BY x;"
        ),
        expect="(no rows)",
        why=(
            "x NOT IN (1, NULL) means x <> 1 AND x <> NULL. The second "
            "part is never true (it is NULL), so no row can pass, not "
            "even 2 or 3. One NULL in the list empties the answer."
        ),
    ),
    _p(
        id="predict-sql-running-sum",
        level=5,
        language="sql",
        name="A running total with a tie",
        family="SQL",
        code=(
            "WITH t(d, v) AS (VALUES (1, 4), (2, 5), (2, 5), (3, 1))\n"
            "SELECT d, v, SUM(v) OVER (ORDER BY d) AS r\n"
            "FROM t ORDER BY d;"
        ),
        expect="d  v  r\n-  -  --\n1  4  4\n2  5  14\n2  5  14\n3  1  15",
        why=(
            "With ORDER BY, the default window runs from the start up to "
            "the current row's PEERS, the rows that tie with it. Both "
            "d=2 rows see the whole tie, so both show 4+5+5 = 14, not "
            "9 then 14."
        ),
    ),
)


# -- How a SQL answer is marked -------------------------------------------------------------------------------

def sql_rows(text: str) -> list[list[str]]:
    """The DATA of a result table, as rows of values: the runner's header line and its dash line are left out, so the
    learner types only the rows (one per line, values separated by spaces), and the column alignment never matters.
    `(no rows)` is an empty result."""
    lines = [ln.split() for ln in text.replace("\r\n", "\n").split("\n") if ln.strip()]
    if lines and lines[0] == ["(no", "rows)"]:
        return []
    # a dash line (`-  ---  --`) marks the header above it: drop both
    for k, cells in enumerate(lines):
        if cells and all(set(c) == {"-"} for c in cells):
            return lines[k + 1:]
    return lines


def sql_same(guess: str, expect: str) -> bool:
    """Is the guess the expected table? Compares the rows' values only. A guess may include the header line (and the
    dash line) or leave them out; `(no rows)` and an empty guess both mean no rows."""
    want = sql_rows(expect)
    got = sql_rows(guess)
    header = expect.replace("\r\n", "\n").strip().split("\n")[0].split()
    if got and got[0] == header and want[:1] != [header]:
        got = got[1:]
    return got == want
