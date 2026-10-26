"""SQL words, part 2: calculations and shaping results - CASE, number and text functions, types, window functions,
CTEs and dates. SQLite semantics throughout (see terms_sql_query.py for how an example's output is written)."""

from __future__ import annotations

from .entry import Entry, sql

TERMS: list[Entry] = [
    *sql(
        "case-expression",
        "CASE",
        "CASE WHEN condition THEN value ... ELSE value END chooses a value row by row, like an if/else inside a query. The first true WHEN wins.",
        see=("coalesce", "three-valued-logic", "select", "nullif"),
        priority=55,
        aka=("case when", "case", "conditional expression", "if else", "iif", "if-else in sql", "switch", "case statement", "else"),
        detect=(r"(?i)\bcase\b[\s\S]{0,80}?\bwhen\b|\biif\s*\(",),
        rules=(
            r"Without an ELSE, a row matching no WHEN gets NULL.",
            r"A WHEN that is NULL (unknown) counts as not true, so a NULL value falls through to ELSE.",
            r"Simple form: CASE x WHEN 1 THEN 'a' WHEN 2 THEN 'b' END compares x with each value.",
            r"IIF(cond, a, b) is the short form of a two-way CASE (SQLite 3.32+).",
        ),
        example=r"""
            CREATE TABLE t (n INTEGER);
            INSERT INTO t VALUES (5), (15), (NULL);
            SELECT n, CASE WHEN n < 10 THEN 'low' WHEN n < 20 THEN 'mid' ELSE 'high' END FROM t ORDER BY n;
        """,
        out=r"NULL|high; 5|low; 15|mid",
    ),
    *sql(
        "integer-division",
        "Integer division",
        "When both sides of / are integers, SQLite divides and throws away the fraction (truncating toward zero): 5 / 2 is 2. Make one side a real to keep the fraction. Dividing by zero gives NULL.",
        see=("modulo", "type-conversion", "round", "average"),
        priority=50,
        aka=("division", "divide", "/", "integer divide", "truncation", "whole number division", "5 / 2", "int division"),
        detect=(r"[\w)]\s*/\s*[\w(]",),
        rules=(
            r"5 / 2 is 2, -7 / 2 is -3 (toward zero), 5 / 2.0 is 2.5, CAST(5 AS REAL) / 2 is 2.5.",
            r"x / 0 is NULL in SQLite (an error in PostgreSQL and most others).",
            r"Percentages and averages go wrong silently: SUM(a) / COUNT(*) on integers loses the fraction; multiply by 1.0 first.",
        ),
        example=r"""
            SELECT 5 / 2, 5 / 2.0, -7 / 2, 5 / 0, CAST(5 AS REAL) / 2;
        """,
        out=r"2|2.5|-3|NULL|2.5",
    ),
    *sql(
        "modulo",
        "Modulo",
        "The % operator gives the remainder of integer division. As in C, its sign follows the left number, and % 0 gives NULL.",
        see=("integer-division", "round", "case-expression"),
        priority=45,
        aka=("remainder", "mod", "%", "modulus", "remainder operator", "even or odd"),
        detect=(r"[\w)]\s*%\s*[\w(]",),
        rules=(
            r"7 % 3 is 1, -7 % 3 is -1, 7 % -3 is 1.",
            r"x % 2 = 0 tests for even; remember -3 % 2 is -1, so test x % 2 <> 0 for odd.",
            r"% works on integers; a real operand is first cut to a whole number.",
        ),
        example=r"""
            SELECT 7 % 3, -7 % 3, 7 % -3, 7 % 0;
        """,
        out=r"1|-1|1|NULL",
    ),
    *sql(
        "round",
        "ROUND and ABS",
        "ROUND(x, n) rounds to n decimals (halves away from zero) and always gives a real number, even ROUND(7) is 7.0. ABS(x) is the size of a number without its sign.",
        see=("integer-division", "type-conversion", "typeof", "average"),
        priority=50,
        aka=("rounding", "abs", "absolute value", "decimal places", "round function", "numeric function", "math function", "floor", "ceiling"),
        detect=(r"(?i)\b(?:round|abs)\s*\(",),
        rules=(
            r"ROUND(2.5) is 3.0 and ROUND(-2.5) is -3.0; ROUND(3.14159, 2) is 3.14.",
            r"The result is a real: its type is real even for a whole number (ROUND(7) prints 7.0).",
            r"ROUND(x) with one argument rounds to a whole number; CAST(x AS INTEGER) truncates instead.",
        ),
        example=r"""
            SELECT ROUND(2.5), ROUND(3.14159, 2), ROUND(-2.5), ROUND(7), ABS(-4);
        """,
        out=r"3.0|3.14|-3.0|7.0|4",
    ),
    *sql(
        "string-function",
        "String functions",
        "Functions that work on text: LENGTH counts characters, UPPER and LOWER change case, TRIM removes spaces from both ends, REPLACE swaps one piece of text for another.",
        see=("substr", "instr", "concatenation", "like-operator"),
        priority=50,
        aka=("string functions", "text function", "text functions", "length", "upper", "lower", "trim", "replace function", "ltrim", "rtrim", "strings", "string", "text", "len", "uppercase", "lowercase"),
        detect=(r"(?i)\b(?:length|upper|lower|trim|ltrim|rtrim|replace)\s*\(",),
        rules=(
            r"LENGTH('hello') is 5; any of them given NULL return NULL.",
            r"TRIM(x) removes spaces; TRIM(x, 'ab') removes those characters from both ends.",
            r"REPLACE('a-b-c', '-', '+') replaces every match, not only the first.",
            r"UPPER and LOWER only change ASCII letters in plain SQLite.",
        ),
        example=r"""
            SELECT LENGTH('hello'), UPPER('abc'), TRIM('  hi  '), REPLACE('a-b-c', '-', '+');
        """,
        out=r"5|ABC|hi|a+b+c",
    ),
    *sql(
        "substr",
        "SUBSTR",
        "SUBSTR(text, start, length) cuts out part of a string. Positions start at 1, not 0; a negative start counts from the end.",
        see=("string-function", "instr", "concatenation"),
        priority=55,
        aka=("substring", "slice", "cut string", "part of a string", "substr function", "left", "right", "extract text"),
        detect=(r"(?i)\bsubstr(?:ing)?\s*\(",),
        rules=(
            r"SUBSTR('hello', 2, 3) is 'ell': start at the 2nd character, take 3.",
            r"With no length it runs to the end: SUBSTR('hello', 4) is 'lo'; SUBSTR('hello', -2) is the last two, 'lo'.",
            r"Position 0 does not exist, so SUBSTR('hello', 0, 2) gives just 'h'.",
        ),
        example=r"""
            SELECT SUBSTR('hello', 2, 3), SUBSTR('hello', -2), SUBSTR('hello', 0, 2), SUBSTR('hello', 4);
        """,
        out=r"ell|lo|h|lo",
    ),
    *sql(
        "instr",
        "INSTR",
        "INSTR(text, piece) gives the position (counting from 1) of the first place piece appears in text, or 0 if it is not there.",
        see=("substr", "string-function", "like-operator"),
        priority=50,
        aka=("position", "find in string", "index of", "locate", "charindex", "find text", "find substring"),
        detect=(r"(?i)\binstr\s*\(",),
        rules=(
            r"INSTR('hello', 'l') is 3 (the first l); INSTR('hello', 'z') is 0, not NULL and not -1.",
            r"Positions are 1-based, matching SUBSTR.",
            r"Case-sensitive; if either argument is NULL the result is NULL.",
        ),
        example=r"""
            SELECT INSTR('hello', 'l'), INSTR('hello', 'z'), SUBSTR('a=b', INSTR('a=b', '=') + 1);
        """,
        out=r"3|0|b",
    ),
    *sql(
        "concatenation",
        "Concatenation (||)",
        "The || operator joins text: 'a' || 'b' is 'ab'. Numbers are turned into text first. If either side is NULL the whole result is NULL. + does not join text.",
        see=("string-function", "null", "type-conversion", "coalesce"),
        priority=50,
        aka=("concat", "join text", "||", "string concatenation", "glue strings", "append text", "string join"),
        detect=(r"\|\|",),
        rules=(
            r"'n=' || 5 is 'n=5'; 'x' || NULL is NULL (wrap in COALESCE(col, '')).",
            r"'1' + '2' is the number 3, because + always means addition.",
            r"|| binds tighter than + and comparison: 'a' || 'b' = 'ab' works as you hope.",
        ),
        example=r"""
            SELECT 'a' || 'b', 'n=' || 5, 'x' || NULL, '1' + '2';
        """,
        out=r"ab|n=5|NULL|3",
    ),
    *sql(
        "type-conversion",
        "Type conversion (CAST)",
        "CAST(x AS INTEGER / REAL / TEXT) converts a value to another type on purpose. SQLite also converts quietly when you mix types, for example '5' + 1.",
        see=("typeof", "type-affinity", "integer-division", "concatenation"),
        priority=50,
        aka=("cast", "type cast", "casting", "convert", "conversion", "implicit conversion", "type coercion", "coercion", "to integer", "to text", "to number"),
        detect=(r"(?i)\bcast\s*\(",),
        rules=(
            r"CAST(3.9 AS INTEGER) is 3 (truncates); CAST('12abc' AS INTEGER) is 12 (reads digits up to the first other character).",
            r"'5' + 1 is 6, and 'abc' + 1 is 1 (the text counts as 0): no error is raised.",
            r"CAST(65 AS TEXT) is the text '65', not the letter A.",
        ),
        example=r"""
            SELECT CAST(3.9 AS INTEGER), CAST('12abc' AS INTEGER), '5' + 1, CAST(65 AS TEXT) || '!';
        """,
        out=r"3|12|6|65!",
    ),
    *sql(
        "typeof",
        "typeof",
        "typeof(x) tells which kind of value SQLite holds: integer, real, text, blob or null. In SQLite the type belongs to each value, not only to the column.",
        see=("type-affinity", "type-conversion", "integer-division", "null"),
        priority=55,
        aka=("type of", "data type", "data types", "storage class", "value type", "column type", "types"),
        detect=(r"(?i)\btypeof\s*\(",),
        rules=(
            r"typeof(1) is integer, typeof(1.0) is real, typeof('a') is text, typeof(NULL) is null.",
            r"typeof(1 / 2.0) is real: any real operand makes the result real; two integers give an integer.",
            r"Use it to find out why a comparison fails: '5' = 5 can be false when the column holds text.",
        ),
        example=r"""
            SELECT typeof(1), typeof(1.0), typeof('a'), typeof(NULL), typeof(1 / 2.0), typeof(x'00');
        """,
        out=r"integer|real|text|null|real|blob",
    ),
    *sql(
        "type-affinity",
        "Type affinity",
        "SQLite's rule for column types: a declared type (INTEGER, TEXT, REAL) is only a preference. It converts a value that looks right on the way in, but any value can still be stored in any column.",
        see=("typeof", "type-conversion", "create-table", "constraint"),
        priority=45,
        aka=("affinity", "column affinity", "flexible typing", "dynamic typing", "manifest typing", "declared type", "integer affinity", "text affinity"),
        rules=(
            r"An INTEGER column stores '42' as the number 42; a TEXT column stores 42 as the text '42'.",
            r"Text that cannot be converted (like 'abc' in an INTEGER column) is stored as text, with no error.",
            r"Other databases reject such a row; in SQLite use CHECK (typeof(col) = 'integer') or a STRICT table to enforce types.",
        ),
        example=r"""
            CREATE TABLE t (i INTEGER, s TEXT);
            INSERT INTO t VALUES ('42', 42);
            SELECT typeof(i), typeof(s), i + 1, s || '!' FROM t;
        """,
        out=r"integer|text|43|42!",
    ),
    *sql(
        "boolean",
        "Boolean",
        "SQLite has no separate true/false type: comparisons give the integer 1 (true) or 0 (false), or NULL when unknown. TRUE and FALSE are just the numbers 1 and 0.",
        see=("three-valued-logic", "where-clause", "case-expression", "typeof"),
        priority=35,
        aka=("bool", "true", "false", "truthy", "falsy", "yes no", "boolean value", "boolean column", "flag"),
        detect=(r"(?i)\b(?:true|false)\b",),
        rules=(
            r"1 < 2 is 1, 2 < 1 is 0, typeof(1 < 2) is integer.",
            r"A boolean column is an INTEGER holding 0 or 1 (add CHECK (flag IN (0, 1)) to enforce it).",
            r"Any non-zero number counts as true in a condition, and NULL is neither true nor false.",
        ),
        example=r"""
            SELECT 1 < 2, 2 < 1, TRUE, NOT TRUE, typeof(1 < 2);
        """,
        out=r"1|0|1|0|integer",
    ),
    *sql(
        "window-function",
        "Window function",
        "A function written FUNC(...) OVER (...) that works out a value for each row from a related set of rows (its window) without squashing them into one row, as GROUP BY would.",
        see=("partition", "row-number", "running-total", "group-by", "lag"),
        priority=60,
        aka=("window functions", "over", "over clause", "analytic function", "windowing", "over()", "window", "frame", "window frame"),
        detect=(r"(?i)\bover\s*\(",),
        rules=(
            r"Every input row stays in the result; the window function adds a column.",
            r"OVER () is the whole table; OVER (PARTITION BY g) a window per group; OVER (ORDER BY x) puts the rows in an order.",
            r"They cannot be used in WHERE or HAVING: filter by wrapping the query in a subquery or CTE.",
            r"Any aggregate (SUM, AVG, COUNT) can be used as a window function.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (10), (20), (30);
            SELECT v, SUM(v) OVER () FROM t ORDER BY v;
        """,
        out=r"10|60; 20|60; 30|60",
    ),
    *sql(
        "row-number",
        "ROW_NUMBER",
        "ROW_NUMBER() OVER (ORDER BY ...) numbers the rows 1, 2, 3... in the given order. Every row gets a different number, even when the sort values tie.",
        see=("rank", "dense-rank", "window-function", "partition"),
        priority=55,
        aka=("row number", "row_number", "numbering rows", "number the rows", "sequence number", "top n per group", "ranking rows"),
        detect=(r"(?i)\brow_number\s*\(",),
        rules=(
            r"With ties, which row gets 2 and which gets 3 is arbitrary: add a tie-breaking key.",
            r"Add PARTITION BY to restart the numbering for each group (top n per group).",
            r"RANK and DENSE_RANK give tied rows the same number; ROW_NUMBER never does.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (30), (10), (20);
            SELECT v, ROW_NUMBER() OVER (ORDER BY v DESC) FROM t ORDER BY 2;
        """,
        out=r"30|1; 20|2; 10|3",
    ),
    *sql(
        "rank",
        "RANK",
        "RANK() OVER (ORDER BY ...) gives tied rows the same rank and then skips numbers: two rows tied at 2 are followed by 4.",
        see=("dense-rank", "row-number", "window-function", "order-by"),
        priority=55,
        aka=("rank function", "ranking", "competition ranking", "rank()"),
        detect=(r"(?i)\brank\s*\(",),
        rules=(
            r"Values 10, 20, 20, 30 rank 1, 2, 2, 4 - there is no 3.",
            r"DENSE_RANK would give 1, 2, 2, 3; ROW_NUMBER 1, 2, 3, 4.",
            r"The first row has rank 1 for the smallest value (use ORDER BY v DESC for the biggest).",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (10), (20), (20), (30);
            SELECT v, RANK() OVER (ORDER BY v) FROM t ORDER BY v;
        """,
        out=r"10|1; 20|2; 20|2; 30|4",
    ),
    *sql(
        "dense-rank",
        "DENSE_RANK",
        "DENSE_RANK() OVER (ORDER BY ...) gives tied rows the same rank like RANK, but never skips: after two rows tied at 2 comes 3.",
        see=("rank", "row-number", "window-function"),
        priority=55,
        aka=("dense rank", "dense_rank", "dense ranking", "rank without gaps", "nth highest"),
        detect=(r"(?i)\bdense_rank\s*\(",),
        rules=(
            r"Values 10, 20, 20, 30 get 1, 2, 2, 3.",
            r"Good for 'the second highest value': filter DENSE_RANK() = 2 in an outer query.",
            r"The number of distinct values equals the last dense rank.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (10), (20), (20), (30);
            SELECT v, DENSE_RANK() OVER (ORDER BY v) FROM t ORDER BY v;
        """,
        out=r"10|1; 20|2; 20|2; 30|3",
    ),
    *sql(
        "partition",
        "PARTITION BY",
        "PARTITION BY splits the rows into separate windows by a column's value, so a window function restarts for each group. Unlike GROUP BY, all rows are kept.",
        see=("window-function", "group-by", "row-number", "running-total"),
        priority=55,
        aka=("partition", "partition by", "per group window", "window per group", "partitioning", "within group"),
        detect=(r"(?i)\bpartition\s+by\b",),
        rules=(
            r"SUM(v) OVER (PARTITION BY g) puts each group's total on every row of that group.",
            r"Combine with ORDER BY inside OVER for running totals and numbering per group.",
            r"Without PARTITION BY the whole result is one window.",
        ),
        example=r"""
            CREATE TABLE s (g TEXT, v INTEGER);
            INSERT INTO s VALUES ('a', 1), ('a', 5), ('b', 2), ('b', 3);
            SELECT g, v, SUM(v) OVER (PARTITION BY g) FROM s ORDER BY g, v;
        """,
        out=r"a|1|6; a|5|6; b|2|5; b|3|5",
    ),
    *sql(
        "running-total",
        "Running total",
        "A total that grows row by row: SUM(v) OVER (ORDER BY ...) adds up everything from the first row to the current one.",
        see=("window-function", "partition", "row-number", "sum"),
        priority=50,
        aka=("cumulative sum", "running sum", "cumulative total", "running", "cumulative", "rolling total", "running count", "moving sum"),
        detect=(r"(?i)\bsum\s*\([^)\n]{0,30}\)\s*over\s*\([^)\n]{0,60}\border\s+by\b",),
        rules=(
            r"The default window includes ties (peers): rows with equal ORDER BY values all show the total including all of them.",
            r"ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW counts strictly row by row, ties or not.",
            r"Add PARTITION BY to restart the total for each group.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (1), (2), (2), (5);
            SELECT v, SUM(v) OVER (ORDER BY v ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS total FROM t ORDER BY v, total;
        """,
        out=r"1|1; 2|3; 2|5; 5|10",
    ),
    *sql(
        "lag",
        "LAG",
        "LAG(col) OVER (ORDER BY ...) gives the value from the PREVIOUS row. LAG(col, n, default) looks n rows back and uses default when there is none.",
        see=("lead", "window-function", "order-by", "coalesce"),
        priority=55,
        aka=("previous row", "lag function", "previous value", "prior row", "difference from previous", "lag()"),
        detect=(r"(?i)\blag\s*\(",),
        rules=(
            r"The first row has no previous row, so LAG gives NULL (or the default you pass).",
            r"v - LAG(v) OVER (ORDER BY id) is the change since the last row.",
            r"The order comes from the OVER clause, not from the final ORDER BY.",
        ),
        example=r"""
            CREATE TABLE t (id INTEGER, v INTEGER);
            INSERT INTO t VALUES (1, 10), (2, 15), (3, 12);
            SELECT id, v - LAG(v) OVER (ORDER BY id) FROM t ORDER BY id;
        """,
        out=r"1|NULL; 2|5; 3|-3",
    ),
    *sql(
        "lead",
        "LEAD",
        "LEAD(col) OVER (ORDER BY ...) gives the value from the NEXT row; LEAD(col, n, default) looks n rows ahead. It is LAG in the other direction.",
        see=("lag", "window-function", "order-by"),
        priority=55,
        aka=("next row", "lead function", "next value", "following row", "lead()"),
        detect=(r"(?i)\blead\s*\(",),
        rules=(
            r"The last row has no next row: LEAD gives NULL, or the default (the third argument).",
            r"LEAD(v, 1, 0) means 'the next v, or 0 at the end'.",
            r"Only meaningful with an ORDER BY inside OVER.",
        ),
        example=r"""
            CREATE TABLE t (id INTEGER, v INTEGER);
            INSERT INTO t VALUES (1, 10), (2, 15), (3, 12);
            SELECT id, LEAD(v, 1, 0) OVER (ORDER BY id) FROM t ORDER BY id;
        """,
        out=r"1|15; 2|12; 3|0",
    ),
    *sql(
        "cte",
        "CTE (WITH)",
        "A common table expression: WITH name AS (SELECT ...) SELECT ... gives a subquery a name for the rest of the statement, which makes long queries readable.",
        see=("recursive-cte", "subquery", "select", "window-function"),
        priority=55,
        aka=("with", "with clause", "common table expression", "named subquery", "temporary result", "cte", "with as", "ctes"),
        detect=(r"(?i)^\s*with\s+(?:recursive\s+)?\w+\s*(?:\([^)]*\))?\s*as\s*\(",),
        rules=(
            r"WITH big AS (SELECT ...) SELECT ... FROM big; the name exists only for that one statement.",
            r"Several CTEs may be listed with commas, and a later one can use an earlier one.",
            r"It is the usual way to filter on a window function's result.",
        ),
        example=r"""
            CREATE TABLE t (v INTEGER);
            INSERT INTO t VALUES (1), (5), (9);
            WITH big AS (SELECT v FROM t WHERE v > 3) SELECT COUNT(*), SUM(v) FROM big;
        """,
        out=r"2|14",
    ),
    *sql(
        "recursive-cte",
        "Recursive CTE",
        "WITH RECURSIVE builds rows by repetition: a starting SELECT, then a SELECT that uses the rows produced so far, joined with UNION ALL, until a condition stops it.",
        see=("cte", "union-all", "self-join", "limit"),
        priority=55,
        aka=("with recursive", "recursive query", "recursion", "recursive", "hierarchy query", "generate series", "series", "tree", "tree traversal", "loop in sql"),
        detect=(r"(?i)\bwith\s+recursive\b",),
        rules=(
            r"Shape: WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < 5) SELECT ... FROM n.",
            r"It stops when the recursive part produces no new rows - without a stopping condition (WHERE i < 5) it never ends.",
            r"Used for number sequences, calendars and walking trees such as employee and manager.",
        ),
        example=r"""
            WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < 5)
            SELECT COUNT(*), SUM(i) FROM n;
        """,
        out=r"5|15",
    ),
    *sql(
        "date-function",
        "Date functions",
        "SQLite keeps dates as text like '2024-03-15' and works on them with date(), time(), datetime(), strftime() and julianday(). Modifiers such as '+1 month' move a date.",
        see=("between", "order-by", "string-function", "type-conversion"),
        priority=50,
        aka=("date", "dates", "time", "datetime", "strftime", "julianday", "timestamp", "date arithmetic", "current_date", "now", "dates and times", "add days", "date format"),
        detect=(r"(?i)\b(?:date|time|datetime|strftime|julianday)\s*\(",),
        rules=(
            r"Dates written YYYY-MM-DD sort and compare correctly as plain text.",
            r"date('2024-03-15', '+1 month') is '2024-04-15'; adding a month to Jan 31 overflows into March: '2024-03-02'.",
            r"strftime('%Y', d) is the year; julianday(a) - julianday(b) is the number of days between.",
            r"'now' gives the current time, so a query using it returns different answers on different days.",
        ),
        example=r"""
            SELECT date('2024-03-15', '+1 month'), strftime('%Y', '2024-03-15'), julianday('2024-03-15') - julianday('2024-03-01'), date('2024-01-31', '+1 month');
        """,
        out=r"2024-04-15|2024|14.0|2024-03-02",
    ),
]
