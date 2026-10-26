"""SQL words, part 1: reading data - SELECT, WHERE, NULL and three-valued logic, the operators (LIKE, IN, BETWEEN),
aggregates, GROUP BY / HAVING, ORDER BY / LIMIT, joins, subqueries and the set operators.

SQL is the fifth glossary language (added 2026-10-23) and means SQLite's SQL (the same engine the Brain Drills and
"Run it" use; PostgreSQL has no glossary). An example is a complete script; what it prints is the rows of its LAST
statement that returns rows, columns joined by `|`, rows by `; `, NULL written NULL (tests/sql_oracle.py). Every
example and every runnable rule is run for real by tests/test_glossary.py."""

from __future__ import annotations

from .entry import Entry, sql

TERMS: list[Entry] = [
    *sql(
        "select",
        "SELECT",
        "The statement that reads data. SELECT names the columns or calculations you want, FROM names the table. The answer is a new table of rows; the stored table is not changed.",
        see=("where-clause", "alias", "order-by", "table"),
        priority=30,
        aka=("select statement", "from", "from clause", "select clause", "projection", "columns", "select *", "star", "read data", "retrieve", "fetch rows", "expression", "operator", "function"),
        detect=(r"(?i)\bselect\b",),
        rules=(
            r"SELECT * means every column; SELECT price * 2 calculates a new value for each row.",
            r"A SELECT needs no FROM when it only calculates: SELECT 1 + 1.",
            r"Without ORDER BY the rows come back in no promised order.",
            r"Keywords are not case-sensitive (select = SELECT); every statement ends with a semicolon.",
        ),
        example=r"""
            CREATE TABLE t (id INTEGER, name TEXT);
            INSERT INTO t VALUES (1, 'ann'), (2, 'bob');
            SELECT name, id * 10 FROM t ORDER BY id;
        """,
        out=r"ann|10; bob|20",
    ),
    *sql(
        "alias",
        "Alias (AS)",
        "AS gives a column or table a temporary name for one query: SELECT price * 2 AS double_price. A table alias (FROM employees e) is needed when the same table appears twice.",
        see=("select", "self-join", "order-by", "join"),
        priority=30,
        aka=("as", "aliases", "column alias", "table alias", "correlation name", "label"),
        detect=(r"(?i)\bas\s+[a-z_]\w*\s*(?:,|\bfrom\b|\border\b|\bwhere\b|$)",),
        rules=(
            r"The alias is the column's name in the result and can be used in ORDER BY (and GROUP BY).",
            r"AS is optional: SELECT price * 2 double_price works, but writing AS is clearer.",
            r"A table alias lets you write e.name instead of employees.name, and is the only way to tell two copies of one table apart.",
        ),
        example=r"""
            CREATE TABLE t (a INTEGER);
            INSERT INTO t VALUES (2), (5);
            SELECT a * 2 AS doubled FROM t ORDER BY doubled DESC;
        """,
        out=r"10; 4",
    ),
    *sql(
        "distinct",
        "DISTINCT",
        "SELECT DISTINCT removes duplicate rows from the result, so each different row appears once. All NULLs count as the same value here.",
        see=("select", "group-by", "union", "count"),
        priority=50,
        aka=("duplicate", "duplicates", "duplicate rows", "unique values", "remove duplicates", "dedupe", "deduplicate", "distinct values", "no duplicates"),
        detect=(r"(?i)\bdistinct\b",),
        rules=(
            r"DISTINCT looks at the whole selected row, not one column: SELECT DISTINCT a, b keeps each different (a, b) pair.",
            r"COUNT(DISTINCT c) counts different non-NULL values.",
            r"A join can produce duplicate rows (one row matching two); DISTINCT hides them, but fix the join if it is the cause.",
            r"UNION removes duplicates like DISTINCT; UNION ALL keeps them.",
        ),
        example=r"""
            CREATE TABLE t (c TEXT);
            INSERT INTO t VALUES ('a'), ('b'), ('a'), (NULL), (NULL);
            SELECT COUNT(*), COUNT(DISTINCT c) FROM (SELECT DISTINCT c FROM t);
        """,
        out=r"3|2",
    ),
    *sql(
        "where-clause",
        "WHERE",
        "WHERE keeps only the rows for which its condition is TRUE. Rows where it is FALSE or NULL (unknown) are dropped. It filters before any grouping.",
        see=("having", "null", "three-valued-logic", "logical-operators", "like-operator"),
        priority=45,
        aka=("where", "filtering", "condition", "predicate", "row filter", "where condition", "search condition", "comparison"),
        detect=(r"(?i)\bwhere\b",),
        rules=(
            r"Comparisons: = (one equals sign), <> or !=, <, <=, >, >=; combine with AND, OR, NOT.",
            r"A row with NULL in the compared column is dropped by n > 3 and by n <= 3 alike.",
            r"WHERE cannot use aggregate functions (COUNT, SUM...): that is the job of HAVING.",
            r"WHERE runs before GROUP BY; HAVING runs after.",
        ),
        example=r"""
            CREATE TABLE t (n INTEGER);
            INSERT INTO t VALUES (1), (5), (NULL), (8);
            SELECT COUNT(*) FROM t WHERE n > 3;
        """,
        out=r"2",
    ),
    *sql(
        "logical-operators",
        "AND, OR, NOT",
        "AND, OR and NOT combine conditions. AND needs both true, OR needs at least one, NOT flips. AND is done before OR, so use brackets.",
        see=("where-clause", "three-valued-logic", "in-operator", "between"),
        priority=40,
        aka=("and", "or", "not", "logical operator", "logical operators", "boolean operators", "and or", "combine conditions", "precedence", "and/or"),
        detect=(r"(?i)\b(?:and|or)\b[^;\n]{0,60}\b(?:and|or)\b",),
        rules=(
            r"a OR b AND c means a OR (b AND c).",
            r"NOT binds looser than comparison: NOT 1 = 2 is NOT (1 = 2), which is true.",
            r"With NULLs the rules are three-valued: NULL AND 0 is 0, NULL OR 1 is 1, but NULL AND 1 and NULL OR 0 stay NULL.",
        ),
        example=r"""
            SELECT 1 OR 0 AND 0, (1 OR 0) AND 0, NOT 1 = 2;
        """,
        out=r"1|0|1",
    ),
    *sql(
        "null",
        "NULL",
        "NULL means unknown or missing - not zero and not an empty string. Any calculation or comparison with NULL gives NULL, even NULL = NULL.",
        see=("is-null", "three-valued-logic", "coalesce", "count"),
        priority=50,
        aka=("nulls", "null value", "missing value", "unknown", "missing", "no value", "nullable", "null values"),
        detect=(r"(?i)\bnull\b",),
        rules=(
            r"NULL = NULL is NULL, not true: test with IS NULL.",
            r"Arithmetic and || with NULL give NULL: 1 + NULL and 'a' || NULL are NULL.",
            r"Aggregates skip NULLs (except COUNT(*)); DISTINCT and GROUP BY treat all NULLs as one group.",
            r"ORDER BY puts NULLs first when ascending in SQLite.",
        ),
        example=r"""
            SELECT NULL = NULL, NULL IS NULL, 1 + NULL, NULL || 'a', typeof(NULL);
        """,
        out=r"NULL|1|NULL|NULL|null",
    ),
    *sql(
        "three-valued-logic",
        "Three-valued logic",
        "SQL conditions have three answers: TRUE, FALSE and UNKNOWN (NULL). WHERE keeps only TRUE, so a row whose condition is UNKNOWN is dropped just like a FALSE one.",
        see=("null", "where-clause", "logical-operators", "not-in"),
        priority=45,
        aka=("three valued logic", "3vl", "unknown", "truth table", "ternary logic", "null logic", "true false unknown", "tri-state"),
        rules=(
            r"NULL AND 0 is 0 (false wins), NULL AND 1 is NULL; NULL OR 1 is 1 (true wins), NULL OR 0 is NULL; NOT NULL is NULL.",
            r"So NOT (x = 5) does not select the rows x = 5 skipped when x is NULL.",
            r"CASE WHEN treats UNKNOWN like false.",
        ),
        example=r"""
            SELECT NULL AND 0, NULL AND 1, NULL OR 1, NULL OR 0, NOT NULL;
        """,
        out=r"0|NULL|1|NULL|NULL",
    ),
    *sql(
        "is-null",
        "IS NULL",
        "IS NULL and IS NOT NULL are the correct ways to ask whether a value is missing. Writing = NULL never matches anything.",
        see=("null", "coalesce", "where-clause", "left-join"),
        priority=50,
        aka=("is not null", "null check", "check for null", "null handling", "null-handling", "handle null", "handling nulls", "testing for null", "null test", "not null check"),
        detect=(r"(?i)\bis\s+(?:not\s+)?null\b|[=<>]\s*null\b",),
        rules=(
            r"x = NULL and x <> NULL are always NULL (never true), so WHERE x = NULL returns nothing.",
            r"IS also works as an equality that understands NULL: NULL IS NULL is 1, 1 IS 1 is 1, 1 IS NULL is 0.",
            r"A LEFT JOIN's unmatched rows are found with WHERE right.id IS NULL.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (1), (NULL), (3);
            SELECT (SELECT COUNT(*) FROM t WHERE v = NULL), (SELECT COUNT(*) FROM t WHERE v IS NULL), 1 IS 1, NULL IS NULL;
        """,
        out=r"0|1|1|1",
    ),
    *sql(
        "coalesce",
        "COALESCE",
        "COALESCE(a, b, c, ...) returns the first value that is not NULL. IFNULL(a, b) is the two-argument form. Use them to give missing values a default.",
        see=("null", "is-null", "nullif", "sum"),
        priority=55,
        aka=("ifnull", "coalesce function", "default for null", "replace null", "null replacement", "nvl", "fallback value", "first non-null"),
        detect=(r"(?i)\b(?:coalesce|ifnull)\s*\(",),
        rules=(
            r"COALESCE(NULL, NULL, 7) is 7; if every argument is NULL the result is NULL.",
            r"Typical: COALESCE(SUM(x), 0) turns 'no rows' (NULL) into 0.",
            r"Arguments after the first non-NULL one are not evaluated.",
        ),
        example=r"""
            SELECT COALESCE(NULL, NULL, 7), IFNULL(NULL, 'x'), COALESCE(4, 9);
        """,
        out=r"7|x|4",
    ),
    *sql(
        "nullif",
        "NULLIF",
        "NULLIF(a, b) returns NULL if a equals b, otherwise a. It turns a placeholder value, like an empty string or 0, into a real NULL.",
        see=("coalesce", "null", "integer-division", "case-expression"),
        priority=50,
        aka=("null if", "nullif function", "empty string to null", "convert to null"),
        detect=(r"(?i)\bnullif\s*\(",),
        rules=(
            r"NULLIF(5, 5) is NULL, NULLIF(5, 6) is 5.",
            r"It guards a division: x / NULLIF(y, 0) is NULL instead of an error in databases where dividing by zero fails (SQLite already gives NULL for x / 0).",
            r"It is the opposite of COALESCE: one makes NULLs, the other removes them.",
        ),
        example=r"""
            SELECT NULLIF(5, 5), NULLIF(5, 6), NULLIF('', '');
        """,
        out=r"NULL|5|NULL",
    ),
    *sql(
        "like-operator",
        "LIKE",
        "LIKE matches text against a pattern: % stands for any run of characters (including none) and _ for exactly one character. In SQLite it ignores upper/lower case for plain English letters.",
        see=("glob", "where-clause", "in-operator", "string-function"),
        priority=55,
        aka=("like", "pattern matching", "wildcard", "wildcards", "text search", "starts with", "contains", "ends with", "not like", "percent sign", "underscore wildcard", "escape"),
        detect=(r"(?i)\blike\s+'",),
        rules=(
            r"'Apple' LIKE 'a%' is true (case ignored for ASCII letters); 'cat' LIKE 'c_t' is true; 'ct' LIKE 'c_t' is false.",
            r"To match a real % or _ , choose an escape character: LIKE 'a!%' ESCAPE '!'.",
            r"x LIKE 'abc' with no wildcard is a (case-insensitive) equality; NULL LIKE anything is NULL.",
            r"A leading % ('%son') cannot use an index and is slow on big tables.",
        ),
        example=r"""
            SELECT 'Apple' LIKE 'a%', 'cat' LIKE 'c_t', 'ct' LIKE 'c_t', 'a%' LIKE 'a!%' ESCAPE '!';
        """,
        out=r"1|1|0|1",
    ),
    *sql(
        "glob",
        "GLOB",
        "GLOB is LIKE's case-sensitive cousin with Unix wildcards: * for any run of characters, ? for one character, [a-c] for a range.",
        see=("like-operator", "where-clause", "string-function"),
        priority=50,
        aka=("glob operator", "case sensitive match", "case-sensitive match", "shell pattern", "wildcard match"),
        detect=(r"(?i)\bglob\s+'",),
        rules=(
            r"'Apple' GLOB 'a*' is false but 'Apple' GLOB 'A*' is true: the case matters.",
            r"[a-c] matches one of those letters and [^0-9] anything but a digit.",
            r"GLOB is SQLite's own operator; other databases do not have it.",
        ),
        example=r"""
            SELECT 'Apple' GLOB 'a*', 'Apple' GLOB 'A*', 'cat' GLOB 'c[a-b]t', 'cat' GLOB 'c?t';
        """,
        out=r"0|1|1|1",
    ),
    *sql(
        "in-operator",
        "IN",
        "x IN (a, b, c) is true when x equals any value in the list; it is a shorter way to write several ORs. The list can also be a subquery.",
        see=("not-in", "subquery", "between", "where-clause"),
        priority=55,
        aka=("in", "in list", "in clause", "membership", "in operator", "one of", "value in a list"),
        detect=(r"(?i)\bin\s*\(",),
        rules=(
            r"3 IN (1, 2, 3) is 1 (true); 5 IN (1, 2, 3) is 0.",
            r"If the list has no match but contains NULL, the answer is NULL, not false.",
            r"x IN (SELECT ...) tests against the rows a subquery returns.",
        ),
        example=r"""
            SELECT 3 IN (1, 2, 3), 5 IN (1, 2, 3), 5 NOT IN (1, 2, 3), NULL IN (1, 2);
        """,
        out=r"1|0|1|NULL",
    ),
    *sql(
        "not-in",
        "NOT IN and NULL",
        "x NOT IN (list) is never TRUE when the list contains a NULL: a value that is not found gives NULL (unknown), not true. One NULL in a subquery makes NOT IN return nothing.",
        see=("in-operator", "exists", "null", "three-valued-logic"),
        priority=60,
        aka=("not in", "not in null", "not in trap", "not in subquery", "null trap", "anti join", "anti-join", "missing rows"),
        detect=(r"(?i)\bnot\s+in\s*\(",),
        rules=(
            r"5 NOT IN (1, NULL) is NULL, so WHERE drops the row; 1 NOT IN (1, NULL) is false.",
            r"Safer: NOT EXISTS (SELECT 1 ...), or add WHERE col IS NOT NULL inside the subquery.",
            r"The same list without the NULL works as expected: 5 NOT IN (1, 2) is true.",
        ),
        example=r"""
            SELECT 5 NOT IN (1, 2), 5 NOT IN (1, NULL), 1 NOT IN (1, NULL);
        """,
        out=r"1|NULL|0",
    ),
    *sql(
        "between",
        "BETWEEN",
        "x BETWEEN low AND high is true when x is at least low and at most high - both ends are included.",
        see=("in-operator", "where-clause", "logical-operators", "date-function"),
        priority=55,
        aka=("between and", "range", "range check", "inclusive range", "not between", "from to"),
        detect=(r"(?i)\bbetween\b",),
        rules=(
            r"It is inclusive: 5 BETWEEN 1 AND 5 is true.",
            r"The order matters: 5 BETWEEN 6 AND 1 is false (it means >= 6 AND <= 1).",
            r"It works for text and dates too: 'b' BETWEEN 'a' AND 'c'. With a NULL on any side the answer is NULL.",
        ),
        example=r"""
            SELECT 5 BETWEEN 1 AND 5, 5 BETWEEN 6 AND 1, 'b' BETWEEN 'a' AND 'c', 0 BETWEEN 1 AND 5;
        """,
        out=r"1|0|1|0",
    ),
    *sql(
        "count",
        "COUNT",
        "COUNT(*) counts rows. COUNT(column) counts the rows where that column is not NULL. COUNT(DISTINCT column) counts different non-NULL values.",
        see=("aggregate-function", "null", "sum", "group-by"),
        priority=60,
        aka=("count(*)", "count star", "count function", "counting rows", "number of rows", "row count", "how many"),
        detect=(r"(?i)\bcount\s*\(",),
        rules=(
            r"COUNT(*) counts every row, NULLs included; COUNT(v) skips rows where v is NULL.",
            r"On an empty table COUNT(*) is 0 (not NULL), unlike SUM, AVG, MIN and MAX.",
            r"With GROUP BY, COUNT is done per group.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (1), (NULL), (1);
            SELECT COUNT(*), COUNT(v), COUNT(DISTINCT v) FROM t;
        """,
        out=r"3|2|1",
    ),
    *sql(
        "sum",
        "SUM",
        "SUM(column) adds up the non-NULL values. If there are no rows (or only NULLs) the answer is NULL, not 0; TOTAL(column) gives 0.0 instead.",
        see=("aggregate-function", "coalesce", "average", "count"),
        priority=50,
        aka=("total", "sum function", "add up", "adding values", "total()"),
        detect=(r"(?i)\b(?:sum|total)\s*\(",),
        rules=(
            r"SUM of integers is an integer; SUM of a real is a real.",
            r"SUM over no rows is NULL: wrap it, COALESCE(SUM(x), 0), when you need 0.",
            r"NULLs are ignored, not treated as 0.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (NULL);
            SELECT SUM(v), TOTAL(v), COALESCE(SUM(v), 0) FROM t;
        """,
        out=r"NULL|0.0|0",
    ),
    *sql(
        "average",
        "AVG",
        "AVG(column) is the mean of the non-NULL values. It always gives a real number, and rows with NULL are left out of both the sum and the count.",
        see=("sum", "count", "integer-division", "aggregate-function"),
        priority=50,
        aka=("avg", "mean", "average function", "averages"),
        detect=(r"(?i)\bavg\s*\(",),
        rules=(
            r"AVG of 2 and 4 is 3.0 (real); a NULL row does not count in the denominator.",
            r"SUM(v) / COUNT(*) is NOT the same: integer division, and COUNT(*) includes NULL rows.",
            r"AVG over no rows is NULL.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (2), (4), (NULL);
            SELECT AVG(v), SUM(v) / COUNT(*), SUM(v) * 1.0 / COUNT(*) FROM t;
        """,
        out=r"3.0|2|2.0",
    ),
    *sql(
        "min-max",
        "MIN and MAX",
        "MIN(column) and MAX(column) give the smallest and largest non-NULL value, for numbers, text or dates. With several arguments, MIN(a, b, c) is an ordinary function that compares them.",
        see=("aggregate-function", "group-by", "order-by", "null"),
        priority=50,
        aka=("min", "max", "minimum", "maximum", "smallest", "largest", "highest", "lowest", "greatest", "least", "biggest"),
        detect=(r"(?i)\b(?:min|max)\s*\(",),
        rules=(
            r"NULLs are skipped; over no rows the answer is NULL.",
            r"MIN(4, 2, 9) with more than one argument is a scalar function working on one row.",
            r"The row holding the maximum is not returned by MAX; find it with ORDER BY ... DESC LIMIT 1 or a subquery.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (5), (NULL), (2);
            SELECT MIN(v), MAX(v), MIN(4, 2, 9) FROM t;
        """,
        out=r"2|5|2",
    ),
    *sql(
        "aggregate-function",
        "Aggregate function",
        "A function that squashes many rows into one value: COUNT, SUM, AVG, MIN, MAX, GROUP_CONCAT. With GROUP BY it gives one value per group.",
        see=("group-by", "having", "count", "null"),
        priority=50,
        aka=("aggregate", "aggregates", "aggregation", "aggregate functions", "group function", "summarize", "group_concat", "aggregate query"),
        rules=(
            r"Aggregates ignore NULLs, except COUNT(*).",
            r"They cannot be used in WHERE (the rows are not grouped yet): use HAVING.",
            r"Selecting a plain column next to an aggregate without GROUP BY is accepted by SQLite but the column's value is arbitrary; other databases reject it.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (1), (2), (5);
            SELECT COUNT(*), SUM(v), MIN(v), MAX(v) FROM t;
        """,
        out=r"3|8|1|5",
    ),
    *sql(
        "group-by",
        "GROUP BY",
        "GROUP BY sorts the rows into groups that share the same value(s) and gives one result row per group, so aggregate functions are worked out per group.",
        see=("having", "aggregate-function", "where-clause", "order-by"),
        priority=60,
        aka=("grouping", "group", "groups", "group by", "group rows", "per group", "for each", "group by clause"),
        detect=(r"(?i)\bgroup\s+by\b",),
        rules=(
            r"Every selected column should be in the GROUP BY list or inside an aggregate (SQLite does not insist, but the value would be arbitrary).",
            r"All NULLs form one group.",
            r"Groups come out in no promised order: add ORDER BY.",
            r"WHERE removes rows before grouping; HAVING removes groups afterwards.",
        ),
        example=r"""
            CREATE TABLE t (g TEXT, v INTEGER);
            INSERT INTO t VALUES ('a', 1), ('a', 2), ('b', 5);
            SELECT g, SUM(v) FROM t GROUP BY g ORDER BY g;
        """,
        out=r"a|3; b|5",
    ),
    *sql(
        "having",
        "HAVING",
        "HAVING filters the groups made by GROUP BY, after the aggregates are worked out. WHERE filters single rows before grouping.",
        see=("group-by", "where-clause", "aggregate-function", "count"),
        priority=60,
        aka=("having clause", "where vs having", "filter groups", "group filter", "having count"),
        detect=(r"(?i)\bhaving\b",),
        rules=(
            r"Use WHERE for conditions on a row's own columns, HAVING for conditions on COUNT, SUM, AVG and the like.",
            r"HAVING SUM(v) > 4 is allowed; WHERE SUM(v) > 4 is an error.",
            r"Filtering with WHERE first is faster: it shrinks the data before grouping.",
        ),
        example=r"""
            CREATE TABLE t (g TEXT, v INTEGER);
            INSERT INTO t VALUES ('a', 1), ('a', 2), ('b', 5);
            SELECT g FROM t GROUP BY g HAVING SUM(v) > 4;
        """,
        out=r"b",
    ),
    *sql(
        "order-by",
        "ORDER BY",
        "ORDER BY sorts the result: ascending by default, DESC for descending. Several keys break ties. Without it the row order is not promised.",
        see=("limit", "null", "group-by", "window-function"),
        priority=55,
        aka=("sorting", "sort", "sort order", "order", "ascending", "descending", "asc", "desc", "sorted", "tie", "ties", "nulls first", "nulls last", "ordering", "collate"),
        detect=(r"(?i)\border\s+by\b",),
        rules=(
            r"In SQLite NULL counts as the smallest value: first when ascending, last when descending (NULLS FIRST / NULLS LAST can say it outright).",
            r"Rows with equal keys come out in any order: add a second key (ORDER BY score DESC, name) for a stable answer.",
            r"Text sorts by character code, so 'B' comes before 'a' unless you add COLLATE NOCASE.",
            r"You may order by an alias or by column number (ORDER BY 2).",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (3), (NULL), (1), (2);
            SELECT v FROM t ORDER BY v;
        """,
        out=r"NULL; 1; 2; 3",
    ),
    *sql(
        "limit",
        "LIMIT",
        "LIMIT n returns at most n rows. Combined with ORDER BY it gives 'the top n'; without ORDER BY it returns any n rows.",
        see=("offset", "order-by", "min-max", "select"),
        priority=55,
        aka=("top", "first n rows", "top n", "limit clause", "fetch first", "row limit", "top rows"),
        detect=(r"(?i)\blimit\s+\d+",),
        rules=(
            r"ORDER BY ... DESC LIMIT 1 is the row with the biggest value (MAX, with its whole row).",
            r"LIMIT 0 returns nothing; a negative LIMIT means no limit in SQLite.",
            r"If fewer rows exist than the limit, you simply get fewer.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (5), (1), (4), (2);
            SELECT v FROM t ORDER BY v DESC LIMIT 2;
        """,
        out=r"5; 4",
    ),
    *sql(
        "offset",
        "OFFSET",
        "OFFSET m after LIMIT skips the first m rows: LIMIT 2 OFFSET 1 gives rows 2 and 3 of the ordered result. It is how paging works.",
        see=("limit", "order-by", "select"),
        priority=50,
        aka=("skip", "paging", "pagination", "page", "skip rows", "limit offset", "offset clause"),
        detect=(r"(?i)\boffset\s+\d+",),
        rules=(
            r"OFFSET only means something with ORDER BY; otherwise 'the first rows' are arbitrary.",
            r"The short form LIMIT 1, 2 means OFFSET 1, LIMIT 2: the OFFSET comes first, which surprises people.",
            r"Big offsets are slow: the database still walks past all the skipped rows.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (5), (1), (4), (2);
            SELECT v FROM t ORDER BY v DESC LIMIT 2 OFFSET 1;
        """,
        out=r"4; 2",
    ),
    *sql(
        "join",
        "JOIN",
        "A JOIN combines rows from two tables by matching a column, given in ON. The type of join decides what happens to rows with no match.",
        see=("inner-join", "left-join", "cross-join", "self-join", "alias"),
        priority=55,
        aka=("joins", "join tables", "combine tables", "join on", "on clause", "on", "foreign key join", "using", "natural join", "multiple tables", "join condition", "full join", "right join"),
        detect=(r"(?i)\bjoin\b",),
        rules=(
            r"JOIN alone means INNER JOIN. The ON condition says which rows pair up (users.id = orders.user_id).",
            r"If one row matches two, it appears twice in the result: joins can multiply rows.",
            r"Rows whose key is NULL never match anything, not even another NULL.",
            r"Give tables short aliases and prefix the columns (o.amount) when both tables have a column of that name.",
        ),
        example=r"""
            CREATE TABLE u (id INTEGER, name TEXT);
            CREATE TABLE o (uid INTEGER, amt INTEGER);
            INSERT INTO u VALUES (1, 'ann'), (2, 'bob');
            INSERT INTO o VALUES (1, 10), (1, 20), (3, 5);
            SELECT name, amt FROM u JOIN o ON u.id = o.uid ORDER BY amt;
        """,
        out=r"ann|10; ann|20",
    ),
    *sql(
        "inner-join",
        "INNER JOIN",
        "An INNER JOIN keeps only the pairs of rows that match: a row with no partner in the other table is dropped from the result.",
        see=("join", "left-join", "cross-join", "exists"),
        priority=50,
        aka=("inner", "inner join", "matching rows only", "join intersection", "plain join"),
        detect=(r"(?i)\binner\s+join\b",),
        rules=(
            r"Users with no orders, and orders with no user (bad ids), both vanish.",
            r"The same result can be written with WHERE: FROM u, o WHERE u.id = o.uid (the old comma style).",
            r"Order of the tables does not change an inner join's rows.",
        ),
        example=r"""
            CREATE TABLE u (id INTEGER, name TEXT);
            CREATE TABLE o (uid INTEGER, amt INTEGER);
            INSERT INTO u VALUES (1, 'ann'), (2, 'bob');
            INSERT INTO o VALUES (1, 10), (1, 20), (3, 5);
            SELECT COUNT(*) FROM u INNER JOIN o ON u.id = o.uid;
        """,
        out=r"2",
    ),
    *sql(
        "left-join",
        "LEFT JOIN",
        "A LEFT JOIN keeps every row of the left table; where the right table has no match, its columns are NULL. Filtering the right table in WHERE can silently turn it back into an inner join.",
        see=("join", "inner-join", "is-null", "exists"),
        priority=55,
        aka=("left outer join", "outer join", "left", "keep all rows", "unmatched rows", "left join where trap", "outer"),
        detect=(r"(?i)\bleft\s+(?:outer\s+)?join\b",),
        rules=(
            r"A user with no orders still appears once, with NULL in the order columns.",
            r"Find the unmatched rows with WHERE o.uid IS NULL (an anti-join).",
            r"Trap: WHERE o.amt > 5 drops the NULL rows; put the filter in ON (... AND o.amt > 5) to keep the left rows.",
            r"COUNT(o.uid) counts matches, COUNT(*) counts the NULL row as one.",
        ),
        example=r"""
            CREATE TABLE u (id INTEGER, name TEXT);
            CREATE TABLE o (uid INTEGER, amt INTEGER);
            INSERT INTO u VALUES (1, 'ann'), (2, 'bob');
            INSERT INTO o VALUES (1, 10), (1, 20), (3, 5);
            SELECT name, amt FROM u LEFT JOIN o ON u.id = o.uid ORDER BY name, amt;
        """,
        out=r"ann|10; ann|20; bob|NULL",
    ),
    *sql(
        "cross-join",
        "CROSS JOIN",
        "A CROSS JOIN pairs every row of one table with every row of the other, so 2 rows and 3 rows give 6. There is no ON condition.",
        see=("join", "inner-join", "select"),
        priority=50,
        aka=("cartesian product", "cartesian", "product", "all combinations", "comma join", "every combination", "cross product"),
        detect=(r"(?i)\bcross\s+join\b",),
        rules=(
            r"The result has rows(a) x rows(b) rows - it grows fast.",
            r"Forgetting the join condition in the old comma style (FROM a, b) makes a cross join by accident.",
            r"Useful for building all combinations, like every size with every colour.",
        ),
        example=r"""
            CREATE TABLE a (x INTEGER);
            CREATE TABLE b (y INTEGER);
            INSERT INTO a VALUES (1), (2);
            INSERT INTO b VALUES (10), (20), (30);
            SELECT COUNT(*) FROM a CROSS JOIN b;
        """,
        out=r"6",
    ),
    *sql(
        "self-join",
        "Self join",
        "Joining a table to itself, using two aliases for the same table, to relate rows of one table to each other - for example an employee to their manager.",
        see=("join", "alias", "inner-join", "left-join"),
        priority=45,
        aka=("self-join", "join itself", "join to itself", "hierarchy", "manager", "same table twice", "parent child", "pair", "pairs of rows"),
        rules=(
            r"The aliases are required: FROM e w JOIN e b ON w.boss = b.id.",
            r"Use LEFT JOIN to keep rows with no partner (the top boss has none).",
            r"Pairs of rows from one table: add a.id < b.id to avoid each pair twice.",
        ),
        example=r"""
            CREATE TABLE e (id INTEGER, name TEXT, boss INTEGER);
            INSERT INTO e VALUES (1, 'ann', NULL), (2, 'bob', 1), (3, 'cy', 1);
            SELECT w.name, b.name FROM e w JOIN e b ON w.boss = b.id ORDER BY w.name;
        """,
        out=r"bob|ann; cy|ann",
    ),
    *sql(
        "subquery",
        "Subquery",
        "A SELECT written inside another statement, in brackets. It can give one value (compared with >), a list (used with IN), or a table (used in FROM).",
        see=("correlated-subquery", "exists", "in-operator", "cte"),
        priority=50,
        aka=("subqueries", "nested query", "inner query", "sub-select", "subselect", "scalar subquery", "query in a query", "derived table", "inline view"),
        detect=(r"(?i)\(\s*select\b",),
        rules=(
            r"A scalar subquery must return one column and at most one row; zero rows gives NULL.",
            r"It runs first (once) when it does not mention the outer query's columns.",
            r"A subquery in FROM needs its result treated as a table and may be given an alias.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (1), (5), (9);
            SELECT v FROM t WHERE v > (SELECT AVG(v) FROM t);
        """,
        out=r"9",
    ),
    *sql(
        "correlated-subquery",
        "Correlated subquery",
        "A subquery that uses a column of the outer query, so it is worked out again for each outer row. Example: each row compared with the biggest value in its own group.",
        see=("subquery", "exists", "window-function", "group-by"),
        priority=50,
        aka=("correlated", "correlated subqueries", "per row subquery", "outer reference", "dependent subquery", "row by row subquery"),
        rules=(
            r"The outer table needs an alias so the inner query can refer to it: WHERE grp = x.grp.",
            r"It can be slow on big tables because it runs once per outer row; a join or window function is often faster.",
            r"EXISTS subqueries are nearly always correlated.",
        ),
        example=r"""
            CREATE TABLE s (grp TEXT, v INTEGER);
            INSERT INTO s VALUES ('a', 1), ('a', 5), ('b', 2), ('b', 3);
            SELECT grp, v FROM s x WHERE v = (SELECT MAX(v) FROM s WHERE grp = x.grp) ORDER BY grp;
        """,
        out=r"a|5; b|3",
    ),
    *sql(
        "exists",
        "EXISTS",
        "EXISTS (subquery) is true if the subquery returns at least one row, false if it returns none. NOT EXISTS finds the rows with no match.",
        see=("subquery", "correlated-subquery", "not-in", "left-join"),
        priority=55,
        aka=("not exists", "exists subquery", "does it exist", "existence", "semi join", "anti join"),
        detect=(r"(?i)\bexists\s*\(",),
        rules=(
            r"What the subquery selects does not matter (SELECT 1 is the habit); only whether a row comes back.",
            r"It is never NULL: unlike NOT IN, NOT EXISTS is safe when the other table has NULLs.",
            r"It usually mentions the outer row: WHERE o.uid = u.id.",
        ),
        example=r"""
            CREATE TABLE u (id INTEGER, name TEXT);
            CREATE TABLE o (uid INTEGER, amt INTEGER);
            INSERT INTO u VALUES (1, 'ann'), (2, 'bob');
            INSERT INTO o VALUES (1, 10), (3, 5);
            SELECT name FROM u WHERE NOT EXISTS (SELECT 1 FROM o WHERE o.uid = u.id);
        """,
        out=r"bob",
    ),
    *sql(
        "union",
        "UNION",
        "UNION stacks the rows of two SELECTs into one result and removes duplicates. Both must have the same number of columns; the names come from the first.",
        see=("union-all", "intersect", "except", "distinct"),
        priority=55,
        aka=("combine results", "stack results", "union operator", "set operation", "set operations", "compound select", "merge results"),
        detect=(r"(?i)\bunion\b",),
        rules=(
            r"UNION behaves like UNION ALL followed by DISTINCT, so it is slower.",
            r"ORDER BY goes once, at the very end, and applies to the whole result.",
            r"Columns are matched by position, not by name.",
        ),
        example=r"""
            SELECT 1 UNION SELECT 1 UNION SELECT 2 ORDER BY 1;
        """,
        out=r"1; 2",
    ),
    *sql(
        "union-all",
        "UNION ALL",
        "UNION ALL stacks two results and keeps every row, duplicates included. It is faster than UNION because it skips the duplicate removal.",
        see=("union", "distinct", "recursive-cte"),
        priority=55,
        aka=("union all", "keep duplicates", "append results", "concatenate results"),
        detect=(r"(?i)\bunion\s+all\b",),
        rules=(
            r"Use it when duplicates do not matter or cannot happen.",
            r"The row count is the sum of both: 2 rows UNION ALL 3 rows is 5.",
            r"Recursive CTEs are built with UNION ALL.",
        ),
        example=r"""
            SELECT (SELECT COUNT(*) FROM (SELECT 1 UNION ALL SELECT 1)), (SELECT COUNT(*) FROM (SELECT 1 UNION SELECT 1));
        """,
        out=r"2|1",
    ),
    *sql(
        "intersect",
        "INTERSECT",
        "INTERSECT returns the rows that appear in both results (without duplicates).",
        see=("union", "except", "in-operator", "inner-join"),
        priority=50,
        aka=("intersection", "in both", "common rows", "rows in both"),
        detect=(r"(?i)\bintersect\b",),
        rules=(
            r"Columns are compared by position; NULLs count as equal here.",
            r"The same result usually comes from an inner join or IN.",
            r"SQLite works through UNION, INTERSECT and EXCEPT from left to right with equal precedence - add brackets via subqueries when mixing.",
        ),
        example=r"""
            CREATE TABLE a (x INTEGER);
            CREATE TABLE b (x INTEGER);
            INSERT INTO a VALUES (1), (2), (3);
            INSERT INTO b VALUES (2), (3), (4);
            SELECT x FROM a INTERSECT SELECT x FROM b ORDER BY x;
        """,
        out=r"2; 3",
    ),
    *sql(
        "except",
        "EXCEPT",
        "EXCEPT returns the rows of the first result that are NOT in the second (without duplicates). The order matters: a EXCEPT b differs from b EXCEPT a.",
        see=("union", "intersect", "not-in", "left-join"),
        priority=50,
        aka=("minus", "difference", "set difference", "in first but not second", "subtract rows"),
        detect=(r"(?i)\bexcept\b",),
        rules=(
            r"Compared by position; NULLs count as equal.",
            r"Like NOT IN but safe with NULLs, and it removes duplicates.",
            r"Other databases call it MINUS (Oracle); SQLite uses EXCEPT.",
        ),
        example=r"""
            CREATE TABLE a (x INTEGER);
            CREATE TABLE b (x INTEGER);
            INSERT INTO a VALUES (1), (2), (3);
            INSERT INTO b VALUES (2), (3), (4);
            SELECT x FROM a EXCEPT SELECT x FROM b;
        """,
        out=r"1",
    ),
]
