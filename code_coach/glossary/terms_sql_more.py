"""SQL words, part 4: the words the SQL data and query packs added - FILTER, GROUP_CONCAT, changes(), collation and
ISO dates. Examples as in terms_sql_query.py."""

from __future__ import annotations

from .entry import Entry, sql

TERMS: list[Entry] = [
    *sql(
        "aggregate-filter",
        "FILTER",
        "AGG(...) FILTER (WHERE condition) makes an aggregate count only the rows that meet a condition, so one query can give a total and a conditional count side by side.",
        see=("aggregate-function", "case-expression", "group-by", "count"),
        priority=50,
        aka=("filter", "filter clause", "filter where", "conditional aggregate", "conditional count", "count if", "sum if"),
        detect=(r"(?i)\bfilter\s*\(\s*where\b",),
        rules=(
            r"COUNT(*) FILTER (WHERE v > 1) counts only rows with v > 1; plain COUNT(*) counts all in the group.",
            r"The same can be written SUM(CASE WHEN v > 1 THEN 1 ELSE 0 END), which works in every database.",
            r"Needs SQLite 3.30 or newer.",
        ),
        example=r"""
            CREATE TABLE t (g TEXT, v INTEGER);
            INSERT INTO t VALUES ('a', 1), ('a', 5), ('b', 2);
            SELECT g, COUNT(*) FILTER (WHERE v > 1), COUNT(*) FROM t GROUP BY g ORDER BY g;
        """,
        out=r"a|1|2; b|1|1",
    ),
    *sql(
        "group-concat",
        "GROUP_CONCAT",
        "GROUP_CONCAT(col, separator) is an aggregate that joins the values of a group into one piece of text, skipping NULLs. The default separator is a comma.",
        see=("aggregate-function", "group-by", "concatenation", "order-by"),
        priority=50,
        aka=("group concat", "group_concat", "string_agg", "join values", "list of values", "string aggregate", "listagg"),
        detect=(r"(?i)\bgroup_concat\s*\(",),
        rules=(
            r"The order of the joined values is not promised: sort in a subquery first, as in the example.",
            r"NULL values are left out; with no rows the answer is NULL.",
            r"GROUP_CONCAT(DISTINCT col) removes repeats (then no separator argument is allowed).",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (3), (1), (2), (NULL);
            SELECT GROUP_CONCAT(v, '-') FROM (SELECT v FROM t ORDER BY v);
        """,
        out=r"1-2-3",
    ),
    *sql(
        "rows-affected",
        "Rows changed (changes())",
        "After an INSERT, UPDATE or DELETE, changes() says how many rows that statement changed. It is how a program checks that the WHERE matched what it expected.",
        see=("update", "delete", "insert", "where-clause"),
        priority=45,
        aka=("changes", "changes()", "rows changed", "rowcount", "row count changed", "affected rows", "number of rows changed", "how many rows changed", "total_changes", "rows updated"),
        detect=(r"(?i)\b(?:total_)?changes\s*\(\s*\)",),
        rules=(
            r"changes() counts the rows of the most recent INSERT, UPDATE or DELETE; 0 means the WHERE matched nothing.",
            r"A SELECT does not change it.",
            r"Rows changed by a trigger are not included.",
        ),
        example=r"""
            CREATE TABLE t (n INTEGER);
            INSERT INTO t VALUES (1), (2), (3);
            UPDATE t SET n = n + 1 WHERE n > 1;
            SELECT changes();
        """,
        out=r"2",
    ),
    *sql(
        "collation",
        "Collation (COLLATE)",
        "A collation is the rule for comparing and sorting text. The default, BINARY, compares character codes and is case-sensitive; COLLATE NOCASE ignores the case of English letters.",
        see=("order-by", "like-operator", "glob", "string-function"),
        priority=45,
        aka=("collate", "case sensitivity", "case-sensitivity", "case insensitive", "case-insensitive", "nocase", "binary collation", "sort rule", "text comparison rule", "case sensitive"),
        detect=(r"(?i)\bcollate\s+\w+",),
        rules=(
            r"'a' = 'A' is false by default, true with COLLATE NOCASE.",
            r"BINARY order puts every capital before every lower-case letter: 'B' < 'a' is true, but false with NOCASE.",
            r"LIKE ignores case for English letters whatever the collation; GLOB always respects it.",
            r"Put COLLATE NOCASE on the column in CREATE TABLE to make it the column's habit.",
        ),
        example=r"""
            SELECT 'a' = 'A', 'a' = 'A' COLLATE NOCASE, 'B' < 'a', 'B' < 'a' COLLATE NOCASE;
        """,
        out=r"0|1|1|0",
    ),
    *sql(
        "iso-date",
        "ISO date text",
        "SQLite has no date type: dates are text, and the format YYYY-MM-DD (ISO 8601) is the one that works, because comparing it as text also orders it by time.",
        see=("date-function", "between", "order-by", "collation"),
        priority=45,
        aka=("iso 8601", "iso date", "date format", "date as text", "text-comparison", "text comparison", "date comparison", "compare dates", "yyyy-mm-dd", "date text"),
        rules=(
            r"'2024-03-15' < '2024-12-01' is true because the year, month and day are fixed-width, most significant first.",
            r"'2024-3-15' (no zero) breaks this: as text it is bigger than '2024-12-01'.",
            r"Always write two-digit months and days; BETWEEN '2024-01-01' AND '2024-01-31' then works for ranges.",
        ),
        example=r"""
            SELECT '2024-03-15' < '2024-12-01', '2024-3-15' < '2024-12-01';
        """,
        out=r"1|0",
    ),
]
