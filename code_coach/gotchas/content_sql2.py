"""Gotchas, SQL (second deck): more SQLite traps. Same rules as content_sql.py; the last SELECT prints."""

from __future__ import annotations

from .items import Item, make

q = make("sql")

ITEMS: tuple[Item, ...] = (
    # ── NULL ───────────────────────────────────────────────────────────────
    q("equals-null", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (NULL), (NULL);
        SELECT (SELECT COUNT(*) FROM t WHERE v = NULL),
               (SELECT COUNT(*) FROM t WHERE v IS NULL),
               (SELECT COUNT(*) FROM t WHERE NOT (v = NULL));
    ''', "0|2|0", ["2|2|0", "0|2|1", "0|1|0"],
      "= NULL is never true, and neither is its negation",
      """Comparing anything to NULL with `=` gives NULL (unknown), and a WHERE keeps only rows where the test is
      true. `NOT NULL` is still NULL, so the third count is 0 as well. Only `IS NULL` finds the two NULL rows."""),

    q("not-in-with-null", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (2), (3);
        SELECT COUNT(*) FROM t WHERE v NOT IN (1, NULL);
    ''', "0", ["2", "3", "1"],
      "NOT IN a list that contains NULL can never be true",
      """`v NOT IN (1, NULL)` means `v <> 1 AND v <> NULL`. The second part is NULL for every row, so the whole
      test is false for 1 and unknown for 2 and 3, and no row passes."""),

    q("in-with-null-list", r'''
        SELECT 1 IN (1, NULL), 2 IN (1, NULL),
               2 NOT IN (1, NULL), 1 NOT IN (1, NULL);
    ''', "1|NULL|NULL|0", ["1|0|1|0", "1|0|0|0", "1|NULL|1|0"],
      "A match makes IN true, but a miss next to a NULL is unknown, not false",
      """`1 IN (1, NULL)` finds its match, so it is 1. `2 IN (1, NULL)` found nothing, but the NULL might have been
      a 2, so the answer is NULL, and `NOT` of NULL is NULL. `1 NOT IN (...)` is plainly 0."""),

    q("null-arithmetic", r'''
        SELECT 1 + NULL, 'a' || NULL, NULL = NULL, NULL IS NULL,
               COALESCE(NULL, 0) + 1;
    ''', "NULL|NULL|NULL|1|1", ["NULL|a|1|1|1", "1|a|1|1|1", "NULL|NULL|1|1|NULL"],
      "NULL poisons arithmetic and ||, and NULL = NULL is NULL",
      """Almost every operator returns NULL when an input is NULL, including `+` and `||`, so `'a' || NULL` is
      NULL, not 'a'. `NULL = NULL` is NULL too; `IS NULL` is the test that answers 1. COALESCE swaps NULL for 0
      before the addition."""),

    q("is-operator-null-safe", r'''
        SELECT NULL IS NULL, NULL = NULL, 1 IS NULL,
               NULL IS NOT 1, 2 IS 2;
    ''', "1|NULL|0|1|1", ["1|1|0|1|1", "1|NULL|0|NULL|1", "NULL|NULL|0|1|1"],
      "IS and IS NOT compare like = and <> but treat NULL as a value",
      """`IS` is a null-safe equality in SQLite: `NULL IS NULL` is true and `NULL IS NOT 1` is true, and neither
      ever returns NULL. Plain `NULL = NULL` still gives NULL."""),

    q("avg-ignores-null", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (10), (NULL), (20);
        SELECT AVG(v), SUM(v) / COUNT(*), AVG(COALESCE(v, 0)) FROM t;
    ''', "15.0|10|10.0", ["10.0|15|10.0", "15.0|15.0|15.0", "15.0|10.0|10.0"],
      "AVG skips NULL rows, and SUM / COUNT(*) is integer division",
      """AVG divides by the 2 non-NULL values, giving 15.0. `SUM(v) / COUNT(*)` is 30 / 3 with both sides
      integers, so it is the integer 10. Turning NULL into 0 first makes AVG count all three rows."""),

    q("empty-aggregates", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (2);
        SELECT SUM(v), TOTAL(v), COUNT(v), MAX(v), AVG(v)
        FROM t WHERE v > 100;
    ''', "NULL|0.0|0|NULL|NULL", ["0|0.0|0|0|0", "0|0|0|NULL|NULL", "NULL|0.0|0|NULL|0"],
      "On no rows SUM, MAX and AVG are NULL, and only COUNT is 0",
      """An aggregate over zero rows still returns one row. `COUNT` gives 0, but `SUM`, `MAX` and `AVG` have
      nothing to work with and return NULL. `TOTAL` is the variant that returns the float 0.0 instead."""),

    q("group-by-null-order", r'''
        CREATE TABLE t (g TEXT);
        INSERT INTO t VALUES ('a'), (NULL), ('a'), (NULL), ('b');
        SELECT g, COUNT(*) FROM t GROUP BY g ORDER BY g;
    ''', "NULL|2; a|2; b|1", ["a|2; b|1", "a|2; b|1; NULL|2", "NULL|1; NULL|1; a|2; b|1"],
      "GROUP BY puts all NULLs in one group, and NULL sorts first",
      """For grouping, NULLs count as equal to each other, so the two NULL rows make one group of 2. When sorting
      ascending SQLite treats NULL as smaller than every value, so that group comes first."""),

    q("count-distinct-null", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (NULL), (NULL), (1), (2);
        SELECT COUNT(DISTINCT v), COUNT(*)
        FROM (SELECT DISTINCT v FROM t);
    ''', "2|3", ["3|3", "2|2", "3|2"],
      "DISTINCT keeps one NULL row, but COUNT(DISTINCT v) never counts it",
      """The inner `SELECT DISTINCT v` collapses the rows to 1, NULL and 2, so `COUNT(*)` sees 3 rows. Counting
      the column skips the NULL, so only 1 and 2 are counted."""),

    q("order-by-null-desc", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (2), (NULL), (1), (3);
        SELECT v FROM t ORDER BY v DESC;
    ''', "3; 2; 1; NULL", ["NULL; 3; 2; 1", "NULL; 1; 2; 3", "1; 2; 3; NULL"],
      "NULL is the smallest value, so DESC puts it last",
      """SQLite sorts NULL below every other value. Ascending it comes first and descending it comes last, the
      opposite of some other databases. `NULLS FIRST` or `NULLS LAST` overrides it."""),

    q("count-case-else-zero", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (2), (3), (4);
        SELECT COUNT(CASE WHEN v > 2 THEN 1 ELSE 0 END),
               COUNT(CASE WHEN v > 2 THEN 1 END),
               SUM(CASE WHEN v > 2 THEN 1 ELSE 0 END) FROM t;
    ''', "4|2|2", ["2|2|2", "4|4|2", "2|4|4"],
      "COUNT counts non-NULL values, and 0 is not NULL",
      """With `ELSE 0` the CASE never returns NULL, so `COUNT` counts all four rows. Without an ELSE the missing
      branches are NULL and are skipped, which gives 2. `SUM` adds the 1s and 0s, so it is also 2."""),

    q("max-scalar-with-null", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (NULL), (3);
        SELECT MAX(1, NULL, 3), MIN(2, 3), (SELECT MAX(v) FROM t);
    ''', "NULL|2|3", ["3|2|3", "NULL|2|NULL", "3|3|3"],
      "MAX with several arguments is NULL if any is; the aggregate skips NULLs",
      """`MAX(a, b, c)` with more than one argument is a scalar function, and it returns NULL as soon as one
      argument is NULL. The single-argument `MAX(v)` is the aggregate, and it ignores NULL rows."""),

    q("exists-select-null", r'''
        SELECT EXISTS (SELECT 1 WHERE 0),
               EXISTS (SELECT NULL),
               EXISTS (SELECT 1 WHERE 1);
    ''', "0|1|1", ["0|0|1", "0|NULL|1", "NULL|1|1"],
      "EXISTS asks whether a row came back, not whether it holds a value",
      """`SELECT NULL` returns one row that happens to contain NULL, so EXISTS is true. Only a query with no
      rows at all, like the one filtered by `WHERE 0`, gives false."""),

    q("not-in-versus-not-exists", r'''
        CREATE TABLE a (id INTEGER);
        CREATE TABLE b (x INTEGER);
        INSERT INTO a VALUES (1), (2), (3);
        INSERT INTO b VALUES (1), (NULL);
        SELECT (SELECT COUNT(*) FROM a WHERE id NOT IN (SELECT x FROM b)),
               (SELECT COUNT(*) FROM a WHERE NOT EXISTS
                  (SELECT 1 FROM b WHERE b.x = a.id));
    ''', "0|2", ["2|2", "2|0", "0|0"],
      "A NULL in the subquery wrecks NOT IN but not NOT EXISTS",
      """`id NOT IN (1, NULL)` is never true, so the first query finds nothing. `NOT EXISTS` checks whether a
      matching row exists, and the NULL row never matches, so 2 and 3 are found."""),

    # ── Numbers and types ──────────────────────────────────────────────────
    q("divide-by-zero-is-null", r'''
        SELECT 1 / 0, 1.0 / 0, 5 % 0, 0 / 0;
    ''', "NULL|NULL|NULL|NULL", ["0|0|0|0", "NULL|Inf|NULL|NULL", "NULL|NULL|0|0"],
      "SQLite divides by zero to NULL; it raises no error",
      """Where most databases stop with an error, SQLite quietly returns NULL for division or remainder by zero,
      integer or float, including 0 / 0. The statement runs on, and the NULL spreads into whatever uses it."""),

    q("float-printing", r'''
        SELECT 0.1 + 0.2, 10 / 4.0, 5.0, 1.0 * 3, 2e3, 6 / 3;
    ''', "0.30000000000000004|2.5|5.0|3.0|2000.0|2", ["0.3|2.5|5|3|2000|2",
      "0.30000000000000004|2.5|5|3|2000|2.0", "0.3|2.5|5.0|3.0|2000.0|2.0"],
      "Floats keep their .0, and 0.1 + 0.2 is not 0.3",
      """Any value written with a decimal point or an exponent is a float, so `5.0` stays 5.0 and `1.0 * 3` is
      3.0. 0.1 + 0.2 shows the usual binary rounding. `6 / 3` has two integers, so its result is the integer 2."""),

    q("rounding", r'''
        SELECT ROUND(2.5), ROUND(-2.5), ROUND(3.14159, 2), ROUND(2),
               ROUND(0.5), TYPEOF(ROUND(2));
    ''', "3.0|-3.0|3.14|2.0|1.0|real", ["2.0|-2.0|3.14|2|0.0|integer",
      "3|-3|3.14|2|1|integer", "2.0|-3.0|3.14|2.0|0.0|real"],
      "ROUND rounds halves away from zero and always returns a float",
      """SQLite does not use banker's rounding: 2.5 goes to 3 and -2.5 to -3, and 0.5 to 1. The result of ROUND is
      a float even for an integer input, so it prints with .0."""),

    q("integer-overflow-to-real", r'''
        SELECT 9223372036854775807 + 1, 9223372036854775807 * 2,
               TYPEOF(9223372036854775807 + 1), 9223372036854775807 + 0;
    ''', "9.223372036854776e+18|1.8446744073709552e+19|real|9223372036854775807",
      ["-9223372036854775808|-2|integer|9223372036854775807",
       "9223372036854775808|18446744073709551614|integer|9223372036854775807",
       "NULL|NULL|NULL|9223372036854775807"],
      "Integer overflow turns into a float instead of wrapping",
      """A 64-bit integer cannot hold the sum, so SQLite redoes the arithmetic in floating point and returns
      9.223372036854776e+18. It never wraps around and it is not an error. Adding 0 stays within range, so that
      one stays an integer."""),

    q("typeof-expressions", r'''
        SELECT TYPEOF(1), TYPEOF(1.0), TYPEOF('1'), TYPEOF(NULL),
               TYPEOF(1 + 1.0), TYPEOF(10 / 2), TYPEOF(10 / 4.0),
               TYPEOF(x'00'), TYPEOF('1' + 1);
    ''', "integer|real|text|null|real|integer|real|blob|integer",
      ["integer|real|text|null|real|real|real|blob|text",
       "integer|integer|text|null|real|integer|real|blob|integer",
       "integer|real|text|null|real|integer|real|text|text"],
      "The type follows the value, and the operator decides the result type",
      """Integer with float gives a float, integer with integer an integer, and `/` follows that rule too, so 10 /
      2 is the integer 5. The `+` operator turns the text '1' into a number, so `'1' + 1` is the integer 2."""),

    q("percent-order-of-operations", r'''
        SELECT 1 / 3 * 100, 100 * 1 / 3, 100.0 * 1 / 3, 100 * 1.0 / 3;
    ''', "0|33|33.333333333333336|33.333333333333336", ["33|33|33|33",
      "0|33|33.3|33.3", "33.333333333333336|33|33.333333333333336|33"],
      "Integer division happens wherever it falls, left to right",
      """`1 / 3 * 100` divides first, and with two integers 1 / 3 is 0, so the whole thing is 0. `100 * 1 / 3`
      multiplies first, then truncates 100 / 3 to 33. A single float anywhere before the division keeps the
      fraction."""),

    q("count-star-division", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (2), (3), (4), (5);
        SELECT COUNT(*) / 2, COUNT(*) / 2.0, COUNT(*) * 1.0 / 2, COUNT(*) % 2
        FROM t;
    ''', "2|2.5|2.5|1", ["2.5|2.5|2.5|1", "3|2.5|2.5|1", "2|2|2.5|1"],
      "COUNT returns an integer, so dividing by an integer truncates",
      """`COUNT(*)` is the integer 5, and 5 / 2 is 2. Writing 2.0, or multiplying by 1.0 first, turns the division
      into a float division and gives 2.5."""),

    q("cast-results", r'''
        SELECT CAST('12abc' AS INTEGER), CAST('abc' AS INTEGER),
               CAST(3.9 AS INTEGER), CAST(-3.9 AS INTEGER),
               CAST('3.7' AS INTEGER), CAST(5 AS TEXT) || '!';
    ''', "12|0|3|-3|3|5!", ["12|NULL|4|-4|4|5!", "NULL|0|3|-3|3|5!", "12|0|4|-4|4|!"],
      "CAST reads a leading number, truncates floats, and never fails",
      """Casting text takes as many leading characters as look like a number and ignores the rest, giving 0 if
      there are none. Casting a float to INTEGER cuts off the fraction toward zero instead of rounding."""),

    q("sum-of-text-numbers", r'''
        CREATE TABLE t (v TEXT);
        INSERT INTO t VALUES ('1'), ('2'), ('x');
        SELECT SUM(v), TYPEOF(SUM(v)), SUM(v + 0), TYPEOF(SUM(v + 0)) FROM t;
    ''', "3.0|real|3|integer", ["3|integer|3|integer", "NULL|null|3|integer", "3.0|real|3.0|real"],
      "SUM gives a float if any input is not already an integer",
      """The column holds text, and SUM returns a float (3.0) whenever an input is not a plain integer, even if
      the text looks like one; 'x' counts as 0. Adding 0 to each value first turns them into integers, and then
      SUM stays integer."""),

    # ── Type affinity and comparisons ──────────────────────────────────────
    q("affinity-on-insert", r'''
        CREATE TABLE t (a INTEGER, b TEXT, c NUMERIC, d);
        INSERT INTO t VALUES ('42', 42, '3.0', '42');
        SELECT TYPEOF(a), TYPEOF(b), TYPEOF(c), c, TYPEOF(d) FROM t;
    ''', "integer|text|integer|3|text", ["text|integer|real|3.0|text",
      "integer|text|real|3.0|text", "integer|integer|integer|3|integer"],
      "The column's affinity converts values as they are stored",
      """An INTEGER column turns '42' into the integer 42, and a TEXT column turns 42 into '42'. NUMERIC turns
      '3.0' into the integer 3 because that loses nothing. A column declared with no type has no affinity and
      keeps the text as it came."""),

    q("numeric-affinity-mixed", r'''
        CREATE TABLE t (n NUMERIC);
        INSERT INTO t VALUES ('3.0'), ('4.5'), ('x'), ('007');
        SELECT GROUP_CONCAT(n || ':' || TYPEOF(n), ' ')
        FROM (SELECT n FROM t ORDER BY rowid);
    ''', "3:integer 4.5:real x:text 7:integer", ["3.0:real 4.5:real x:text 007:text",
      "3:integer 4.5:real x:text 007:integer", "3.0:text 4.5:text x:text 007:text"],
      "NUMERIC affinity converts what looks like a number and keeps the rest",
      """'3.0' and '007' are numeric text, so they become the integers 3 and 7; '4.5' becomes a real. 'x' cannot
      be converted and stays text. The leading zeros are gone because the stored value is the number."""),

    q("mixed-type-order", r'''
        CREATE TABLE t (v);
        INSERT INTO t VALUES ('b'), (2), (NULL), ('a'), (10), (1.5);
        SELECT v FROM t ORDER BY v;
    ''', "NULL; 1.5; 2; 10; a; b", ["NULL; 1.5; 10; 2; a; b", "1.5; 2; 10; NULL; a; b",
      "NULL; a; b; 1.5; 2; 10"],
      "In one column NULL < numbers < text, each sorted its own way",
      """A column with no declared type can hold anything. SQLite orders NULLs first, then numbers by value (so 10
      comes after 2), then text alphabetically."""),

    q("text-column-sorting", r'''
        CREATE TABLE t (v TEXT);
        INSERT INTO t VALUES ('9'), ('10'), ('100');
        SELECT MAX(v), MIN(v), MAX(v + 0), MIN(CAST(v AS INTEGER)) FROM t;
    ''', "9|10|100|9", ["100|9|100|9", "9|10|100|10", "100|10|100|9"],
      "A TEXT column compares as text, so '9' beats '100'",
      """The values are strings, so they are compared character by character: '9' is the biggest and '10' the
      smallest. Adding 0 or casting makes them numbers, and then 100 is the maximum and 9 the minimum."""),

    q("column-affinity-comparison", r'''
        CREATE TABLE t (i INTEGER, s TEXT, n);
        INSERT INTO t VALUES (1, '1', '1');
        SELECT i = '1', s = 1, n = 1, i = s, s = n, 1 = '1' FROM t;
    ''', "1|1|0|1|1|0", ["1|1|1|1|1|0", "0|0|0|0|1|0", "1|1|0|0|1|1"],
      "Comparisons convert only when a column's affinity says so",
      """The INTEGER column converts the text '1' it is compared with, and the TEXT column turns the 1 into text,
      so those match. Column `n` has no affinity and stores '1' as text, so against a plain 1 it is false, and so
      are two bare literals, which have no affinity."""),

    q("string-equality-details", r'''
        SELECT 'abc' = 'abc ', 'abc' = 'ABC',
               'abc' = 'ABC' COLLATE NOCASE, 'abc' = 'abc ' COLLATE RTRIM;
    ''', "0|0|1|1", ["1|0|1|1", "0|1|1|1", "0|0|0|1"],
      "Text equality is exact unless a collation says otherwise",
      """By default case matters and so does a trailing space. `COLLATE NOCASE` ignores ASCII case, and `COLLATE
      RTRIM` ignores trailing spaces, so those two become true."""),

    q("binary-sort-uppercase-first", r'''
        CREATE TABLE t (name TEXT);
        INSERT INTO t VALUES ('apple'), ('Banana'), ('cherry'), ('Avocado');
        SELECT name FROM t ORDER BY name;
    ''', "Avocado; Banana; apple; cherry", ["apple; Avocado; Banana; cherry",
      "Avocado; apple; Banana; cherry", "Banana; Avocado; apple; cherry"],
      "The default collation compares bytes, so capitals sort before lower case",
      """In ASCII every capital letter comes before every lower-case one, so 'Banana' sorts before 'apple'.
      Adding `COLLATE NOCASE` would give the dictionary order people expect."""),

    q("like-is-case-blind", r'''
        SELECT 'Apple' LIKE 'apple', 'Apple' GLOB 'apple',
               'Apple' LIKE 'a%', 'Apple' LIKE '_PPLE', 'Apple' = 'apple';
    ''', "1|0|1|1|0", ["0|0|0|0|0", "1|1|1|1|1", "1|0|1|0|0"],
      "LIKE ignores ASCII case, but GLOB and = do not",
      """For ASCII letters `LIKE` is case-insensitive in SQLite, and `_` stands for exactly one character. `GLOB`
      is case-sensitive, and `=` compares exactly."""),

    q("like-underscore-wildcard", r'''
        CREATE TABLE t (v TEXT);
        INSERT INTO t VALUES ('a_b'), ('axb'), ('ab'), ('a%b');
        SELECT (SELECT COUNT(*) FROM t WHERE v LIKE 'a_b'),
               (SELECT COUNT(*) FROM t WHERE v LIKE 'a\_b' ESCAPE '\'),
               (SELECT COUNT(*) FROM t WHERE v LIKE 'a%b');
    ''', "3|1|4", ["1|1|4", "3|3|2", "1|1|2"],
      "_ and % are wildcards in LIKE unless escaped",
      """The pattern `a_b` matches 'a_b', 'axb' and 'a%b', because `_` is any single character. With an ESCAPE
      character the underscore is literal and only 'a_b' remains. `a%b` matches all four, since `%` can also
      match nothing."""),

    # ── Grouping, joins and sets ───────────────────────────────────────────
    q("where-before-having", r'''
        CREATE TABLE t (g TEXT, v INTEGER);
        INSERT INTO t VALUES ('a', 1), ('a', 2), ('b', 3), ('b', 4);
        SELECT g, SUM(v) FROM t WHERE v > 1
        GROUP BY g HAVING SUM(v) > 2 ORDER BY g;
    ''', "b|7", ["a|3; b|7", "a|2; b|7", "b|4"],
      "WHERE filters rows before they are grouped, HAVING filters the groups",
      """The `WHERE v > 1` runs first and drops the row with 1, so group a is left with only the 2. Its sum is 2,
      which fails `HAVING SUM(v) > 2`, and only group b survives with 3 + 4."""),

    q("left-join-where-or-on", r'''
        CREATE TABLE a (id INTEGER);
        CREATE TABLE b (aid INTEGER, x TEXT);
        INSERT INTO a VALUES (1), (2), (3);
        INSERT INTO b VALUES (1, 'y'), (3, 'n');
        SELECT (SELECT COUNT(*) FROM a LEFT JOIN b ON b.aid = a.id
                WHERE b.x = 'y'),
               (SELECT COUNT(*) FROM a LEFT JOIN b
                ON b.aid = a.id AND b.x = 'y');
    ''', "1|3", ["3|3", "1|1", "2|3"],
      "A WHERE on the right table throws away the unmatched rows a LEFT JOIN made",
      """Unmatched rows have NULL in every column of `b`, and `NULL = 'y'` is not true, so the WHERE removes them
      and the join behaves like an inner join. Putting the same test in the ON clause keeps all three rows."""),

    q("join-multiplies-sums", r'''
        CREATE TABLE a (id INTEGER, amt INTEGER);
        CREATE TABLE b (aid INTEGER);
        INSERT INTO a VALUES (1, 10), (2, 20);
        INSERT INTO b VALUES (1), (1), (2);
        SELECT SUM(a.amt), COUNT(DISTINCT a.id), COUNT(*)
        FROM a JOIN b ON b.aid = a.id;
    ''', "40|2|3", ["30|2|3", "30|2|2", "40|3|3"],
      "A join repeats the parent row once per match, so its sums grow",
      """Row 1 of `a` matches two rows of `b`, so its 10 is added twice: 10 + 10 + 20 = 40, not 30. `COUNT(*)`
      counts the three joined rows, while `COUNT(DISTINCT a.id)` still sees only two parents."""),

    q("left-join-count-star", r'''
        CREATE TABLE a (id INTEGER);
        CREATE TABLE b (aid INTEGER);
        INSERT INTO a VALUES (1), (2), (3);
        INSERT INTO b VALUES (1), (1);
        SELECT a.id, COUNT(*), COUNT(b.aid) FROM a
        LEFT JOIN b ON b.aid = a.id GROUP BY a.id ORDER BY a.id;
    ''', "1|2|2; 2|1|0; 3|1|0", ["1|2|2; 2|0|0; 3|0|0", "1|2|2; 2|1|1; 3|1|1",
      "1|2|2; 2|0|0; 3|1|0"],
      "COUNT(*) counts the NULL-padded row, COUNT(column) does not",
      """A parent with no match still produces one joined row, padded with NULLs. `COUNT(*)` counts that row, so
      it says 1, while `COUNT(b.aid)` skips the NULL and says 0. To count children, count a column of `b`."""),

    q("distinct-whole-row", r'''
        CREATE TABLE t (a INTEGER, b INTEGER);
        INSERT INTO t VALUES (1, 1), (1, 2), (2, 1), (1, 1);
        SELECT (SELECT COUNT(*) FROM (SELECT DISTINCT a, b FROM t)),
               (SELECT COUNT(DISTINCT a) FROM t),
               (SELECT COUNT(DISTINCT b) FROM t);
    ''', "3|2|2", ["3|3|3", "2|2|2", "4|2|2"],
      "SELECT DISTINCT compares the whole row, not each column",
      """`SELECT DISTINCT a, b` removes only exact duplicate pairs, so (1,1) appears once and three rows remain.
      `COUNT(DISTINCT a)` looks at one column at a time: a has two different values, and so does b."""),

    q("limit-comma-order", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (5), (3), (8), (1), (9);
        SELECT v FROM t ORDER BY v LIMIT 2, 1;
    ''', "5", ["3; 5", "1; 3", "3"],
      "In LIMIT a, b the first number is the offset, the second the count",
      """`LIMIT 2, 1` is shorthand for `LIMIT 1 OFFSET 2`: skip two rows, take one. The sorted values are 1, 3, 5,
      8, 9, so the answer is 5. People read it as 'take 2, skip 1' and get it backwards."""),

    q("limit-negative-and-zero", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (2), (3), (4), (5);
        SELECT (SELECT COUNT(*) FROM (SELECT v FROM t LIMIT -1 OFFSET 2)),
               (SELECT COUNT(*) FROM (SELECT v FROM t LIMIT 0)),
               (SELECT COUNT(*) FROM (SELECT v FROM t LIMIT 10 OFFSET 4));
    ''', "3|0|1", ["0|0|1", "3|5|1", "3|0|0"],
      "A negative LIMIT means no limit; OFFSET past the end leaves what is left",
      """`LIMIT -1` is SQLite's way to say 'all rows', which is how you use an OFFSET without a count: 5 rows
      minus 2 skipped leaves 3. `LIMIT 0` returns nothing, and `LIMIT 10 OFFSET 4` just returns the one row
      that is left."""),

    # ── Window functions ───────────────────────────────────────────────────
    q("rank-with-ties", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (10), (20), (20), (30);
        SELECT v, RANK() OVER (ORDER BY v), DENSE_RANK() OVER (ORDER BY v)
        FROM t ORDER BY v;
    ''', "10|1|1; 20|2|2; 20|2|2; 30|4|3", ["10|1|1; 20|2|2; 20|2|2; 30|3|3",
      "10|1|1; 20|2|2; 20|3|2; 30|4|3", "10|1|1; 20|2|2; 20|2|2; 30|4|4"],
      "RANK skips numbers after a tie, DENSE_RANK does not",
      """Both 20s share rank 2. `RANK` then jumps to 4 because two rows already hold rank 2, leaving a gap.
      `DENSE_RANK` gives the next distinct value the next number, 3."""),

    q("running-total-peers", r'''
        CREATE TABLE t (g INTEGER, v INTEGER);
        INSERT INTO t VALUES (1, 10), (2, 20), (2, 30), (3, 40);
        SELECT g, v, SUM(v) OVER (ORDER BY g) FROM t ORDER BY g, v;
    ''', "1|10|10; 2|20|60; 2|30|60; 3|40|100", ["1|10|10; 2|20|30; 2|30|60; 3|40|100",
      "1|10|100; 2|20|100; 2|30|100; 3|40|100", "1|10|10; 2|20|50; 2|30|50; 3|40|40"],
      "A running SUM includes every row that ties on the ORDER BY value",
      """The default frame is `RANGE ... CURRENT ROW`, which ends at the last peer: all rows with the same `g`.
      Both rows with g = 2 therefore show 10 + 20 + 30 = 60. To count strictly row by row, order by a unique
      column or write `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`."""),

    q("rows-frame-moving-sum", r'''
        CREATE TABLE t (id INTEGER, v INTEGER);
        INSERT INTO t VALUES (1, 1), (2, 2), (3, 3), (4, 4);
        SELECT SUM(v) OVER (ORDER BY id
                            ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)
        FROM t ORDER BY id;
    ''', "1; 3; 5; 7", ["1; 3; 6; 10", "3; 5; 7; 4", "1; 2; 3; 4"],
      "A ROWS frame looks only at the neighbouring rows it names",
      """Each row adds itself and the one just before it: 1, 1+2, 2+3, 3+4. The first row has no predecessor, so
      the frame is just itself. Without the frame clause the sum would keep growing from the start."""),

    q("lag-defaults", r'''
        CREATE TABLE t (id INTEGER, v INTEGER);
        INSERT INTO t VALUES (1, 5), (2, 7), (3, 12);
        SELECT v - LAG(v) OVER (ORDER BY id),
               LAG(v, 1, 0) OVER (ORDER BY id) FROM t ORDER BY id;
    ''', "NULL|0; 2|5; 5|7", ["5|0; 2|5; 5|7", "NULL|NULL; 2|5; 5|7", "NULL|0; 2|7; 5|12"],
      "LAG of the first row is NULL unless you give it a default",
      """`LAG(v)` reads the previous row's value; there is none for the first row, so it is NULL and the
      subtraction is NULL too. The third argument of `LAG(v, 1, 0)` supplies 0 instead."""),

    q("ntile-uneven", r'''
        CREATE TABLE t (id INTEGER);
        INSERT INTO t VALUES (1), (2), (3), (4), (5);
        SELECT NTILE(2) OVER (ORDER BY id) FROM t ORDER BY id;
    ''', "1; 1; 1; 2; 2", ["1; 1; 2; 2; 2", "1; 2; 1; 2; 1", "1; 1; 1; 1; 2"],
      "NTILE gives the bigger buckets to the first tiles",
      """Five rows cannot be split evenly in two. NTILE puts the extra row in the first bucket, so it gets three
      rows and the second gets two."""),

    # ── Subqueries, CASE and functions ─────────────────────────────────────
    q("scalar-subquery-first-row", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (7), (3), (9);
        SELECT (SELECT v FROM t ORDER BY v DESC),
               (SELECT v FROM t WHERE v > 100);
    ''', "9|NULL", ["7|NULL", "9|0", "3|NULL"],
      "A scalar subquery uses its first row, and no row at all means NULL",
      """SQLite does not complain when a subquery used as a value returns several rows: it just takes the first
      one, which after the ORDER BY is 9. A subquery that returns no rows is NULL, not 0 or an error."""),

    q("case-first-true-branch", r'''
        SELECT CASE WHEN 5 > 1 THEN 'a' WHEN 5 > 3 THEN 'b' ELSE 'c' END,
               CASE 5 WHEN 5.0 THEN 'eq' ELSE 'ne' END,
               CASE WHEN NULL THEN 1 ELSE 2 END,
               CASE 3 WHEN NULL THEN 'n' ELSE 'o' END,
               CASE WHEN 0 THEN 1 END;
    ''', "a|eq|2|o|NULL", ["b|eq|2|o|NULL", "a|ne|2|o|NULL", "a|eq|2|n|NULL"],
      "CASE stops at the first true branch, and NULL is never true",
      """Both of the first conditions are true, but the first one wins. `5 = 5.0` is true, and `WHEN NULL` never
      matches, even against NULL, so the ELSE branch runs. With no ELSE and no match the result is NULL."""),

    q("empty-string-is-not-null", r'''
        SELECT COALESCE('', 'x'), COALESCE(NULLIF('', ''), 'x'),
               IFNULL(NULL, 'y'), NULLIF(5, 6), NULLIF(5, 5),
               '' IS NULL, LENGTH('');
    ''', "|x|y|5|NULL|0|0", ["x|x|y|5|NULL|0|0", "|x|y|NULL|5|0|0", "|x|y|5|NULL|1|0"],
      "An empty string is a value, so COALESCE keeps it; NULLIF turns it into NULL",
      """`COALESCE` only skips NULLs, and '' is not NULL, so the first result is the empty string. `NULLIF('',
      '')` returns NULL when its two arguments are equal, which is the usual way to treat empty as missing.
      `NULLIF(5, 6)` returns the first argument unchanged."""),

    q("substr-is-one-based", r'''
        SELECT SUBSTR('hello', 2, 3), SUBSTR('hello', 0, 3),
               SUBSTR('hello', -3), SUBSTR('hello', -3, 2),
               SUBSTR('hello', 2);
    ''', "ell|he|llo|ll|ello", ["ell|hel|llo|ll|ello", "llo|hel|llo|ll|llo",
      "ell|he|hel|he|ello"],
      "SUBSTR counts from 1, and a start of 0 still uses up one of the characters",
      """Position 1 is the first letter, so (2, 3) gives 'ell'. Position 0 does not exist, but it still occupies
      one place in the count, so (0, 3) gives only 'he'. A negative start counts back from the end of the
      string."""),

    q("union-chain-order", r'''
        SELECT (SELECT COUNT(*) FROM (SELECT 1 UNION SELECT 1
                                      UNION ALL SELECT 1)),
               (SELECT COUNT(*) FROM (SELECT 1 UNION ALL SELECT 1
                                      UNION SELECT 1)),
               (SELECT COUNT(*) FROM (SELECT 1 UNION ALL SELECT 1));
    ''', "2|1|2", ["1|1|2", "3|1|2", "2|1|1"],
      "A chain of UNIONs is evaluated left to right, and UNION removes duplicates",
      """In the first chain `1 UNION 1` collapses to one row, and then `UNION ALL` adds another, giving 2. In
      the second, the two rows from `UNION ALL` are deduplicated by the final `UNION`, leaving 1. A plain
      `UNION ALL` keeps both."""),

    q("except-removes-duplicates", r'''
        CREATE TABLE a (x INTEGER);
        CREATE TABLE b (x INTEGER);
        INSERT INTO a VALUES (1), (1), (2), (3);
        INSERT INTO b VALUES (3);
        SELECT x FROM a EXCEPT SELECT x FROM b ORDER BY x;
    ''', "1; 2", ["1; 1; 2", "1; 1; 2; 3", "2"],
      "EXCEPT, like UNION and INTERSECT, returns each row only once",
      """Set operators work on sets, not bags. The two 1s in `a` collapse to a single row, and the 3 is removed
      because `b` has it. Only `UNION ALL` keeps duplicates."""),

    q("correlated-department-average", r'''
        CREATE TABLE emp (name TEXT, dept TEXT, sal INTEGER);
        INSERT INTO emp VALUES ('Ann', 'x', 10), ('Bob', 'x', 12),
          ('Cy', 'y', 100), ('Di', 'y', 90), ('Ed', 'y', 95);
        SELECT name FROM emp e WHERE sal >
          (SELECT AVG(sal) FROM emp WHERE dept = e.dept) ORDER BY name;
    ''', "Bob; Cy", ["Cy; Di; Ed", "Bob; Cy; Ed", "Ann; Bob; Cy"],
      "A correlated subquery is re-run for each outer row with that row's values",
      """For each employee the inner query averages only that employee's own department: 11 for x and 95 for y.
      Bob (12) and Cy (100) beat their own department's average. Comparing with the company-wide average of
      61.4 would have picked Cy, Di and Ed."""),

    q("self-join-manager", r'''
        CREATE TABLE emp (id INTEGER, name TEXT, mgr INTEGER);
        INSERT INTO emp VALUES (1, 'Ann', NULL), (2, 'Bob', 1),
                               (3, 'Cy', 2);
        SELECT e.name, m.name FROM emp e LEFT JOIN emp m ON e.mgr = m.id
        ORDER BY e.id;
    ''', "Ann|NULL; Bob|Ann; Cy|Bob", ["Bob|Ann; Cy|Bob", "Ann|Bob; Bob|Cy; Cy|NULL",
      "Ann|Ann; Bob|Ann; Cy|Bob"],
      "In a self join the left alias is the employee and the right one the boss",
      """Each row `e` looks up its manager `m` by id. Ann has no manager, and `mgr = id` is never true for NULL,
      so the LEFT JOIN keeps her with a NULL boss. An inner join would have dropped her row."""),

    q("group-concat-details", r'''
        CREATE TABLE t (x TEXT);
        INSERT INTO t VALUES ('b'), (NULL), ('a'), ('b');
        SELECT GROUP_CONCAT(x), GROUP_CONCAT(DISTINCT x),
               GROUP_CONCAT(x, '-')
        FROM (SELECT x FROM t ORDER BY x);
    ''', "a,b,b|a,b|a-b-b", ["NULL,a,b,b|a,b|a-b-b", "a, b, b|a, b|a-b-b", "a,b,b|a,b|a,b,b"],
      "GROUP_CONCAT joins with a comma, with no space, and skips NULLs",
      """The default separator is a plain `,`. NULL values are left out rather than shown. `DISTINCT` removes the
      repeated 'b', and a second argument replaces the separator, except that `DISTINCT` cannot be combined with
      one."""),

    # ── Changing data ──────────────────────────────────────────────────────
    q("update-uses-old-values", r'''
        CREATE TABLE t (a INTEGER, b INTEGER);
        INSERT INTO t VALUES (1, 2);
        UPDATE t SET a = b, b = a;
        SELECT a, b FROM t;
    ''', "2|1", ["2|2", "1|2", "1|1"],
      "Every assignment in one UPDATE reads the row as it was before the statement",
      """The right-hand sides are all evaluated against the old row, so `a = b` takes 2 and `b = a` takes the old
      1. The two values swap. In a language with ordinary assignments the second line would see the new a."""),

    q("replace-resets-other-columns", r'''
        CREATE TABLE t (id INTEGER PRIMARY KEY, a TEXT, b TEXT DEFAULT 'd');
        INSERT INTO t VALUES (1, 'x', 'keep');
        REPLACE INTO t (id, a) VALUES (1, 'z');
        SELECT id, a, b FROM t;
    ''', "1|z|d", ["1|z|keep", "1|z|NULL", "1|x|keep"],
      "REPLACE deletes the old row and inserts a new one, so unlisted columns reset",
      """On a key conflict REPLACE removes the existing row and inserts the new one from scratch. The column `b`
      was not mentioned, so it gets its DEFAULT 'd' and the old 'keep' is lost. An UPDATE would have left it
      alone."""),

    q("upsert-excluded", r'''
        CREATE TABLE t (k TEXT PRIMARY KEY, n INTEGER);
        INSERT INTO t VALUES ('a', 1);
        INSERT INTO t VALUES ('a', 10), ('b', 5)
          ON CONFLICT (k) DO UPDATE SET n = n + excluded.n;
        SELECT k, n FROM t ORDER BY k;
    ''', "a|11; b|5", ["a|10; b|5", "a|1; b|5", "a|2; b|5"],
      "In an upsert, a bare n is the stored value and excluded.n is the rejected one",
      """Row 'a' conflicts, so the UPDATE runs: the stored n (1) plus the rejected row's n (10) makes 11. Row 'b'
      has no conflict and is inserted as it is."""),

    q("rowid-reuse-autoincrement", r'''
        CREATE TABLE p (id INTEGER PRIMARY KEY, v TEXT);
        CREATE TABLE q (id INTEGER PRIMARY KEY AUTOINCREMENT, v TEXT);
        INSERT INTO p (v) VALUES ('a'), ('b'), ('c');
        INSERT INTO q (v) VALUES ('a'), ('b'), ('c');
        DELETE FROM p WHERE id = 3;
        DELETE FROM q WHERE id = 3;
        INSERT INTO p (v) VALUES ('d');
        INSERT INTO q (v) VALUES ('d');
        SELECT (SELECT MAX(id) FROM p), (SELECT MAX(id) FROM q);
    ''', "3|4", ["4|4", "3|3", "4|3"],
      "Without AUTOINCREMENT a freed top id is reused; with it, ids only go up",
      """A plain INTEGER PRIMARY KEY gets one more than the current largest id, so after deleting 3 the next row
      is 3 again. AUTOINCREMENT remembers the largest id ever handed out, so the new row is 4."""),

    q("bare-column-with-max", r'''
        CREATE TABLE t (name TEXT, score INTEGER);
        INSERT INTO t VALUES ('a', 5), ('b', 9), ('c', 7);
        SELECT name, MAX(score) FROM t UNION ALL
        SELECT name, MIN(score) FROM t;
    ''', "b|9; a|5", ["a|9; a|5", "c|9; a|5", "b|9; c|5"],
      "A plain column next to one MAX or MIN comes from the row that won",
      """SQLite has a special rule: with exactly one `MAX()` or `MIN()` in the query, any other column is taken
      from the row that holds the maximum or minimum. Standard SQL would reject this, and other databases give
      an error or an arbitrary row."""),

    q("concat-binds-tighter-than-math", r'''
        SELECT 1 || 2 + 3, 2 * 3 || 4, 'a' || 1 + 2;
    ''', "15|68|2", ["15|64|2", "15|68|a3", "123|68|2"],
      "|| ranks above * and +, and the text it makes is read as a number",
      """`||` binds more tightly than the arithmetic operators. `1 || 2 + 3` is '12' + 3 = 15, `2 * 3 || 4` is
      2 * 34 = 68, and `'a' || 1 + 2` is 'a1' + 2, where the text 'a1' counts as 0, giving 2."""),

    q("date-arithmetic-month-overflow", r'''
        SELECT STRFTIME('%Y-%m-%d', '2024-01-31', '+1 month'),
               STRFTIME('%Y-%m-%d', '2023-01-31', '+1 month'),
               STRFTIME('%Y-%m-%d', '2024-03-31', 'start of month',
                        '+1 month', '-1 day'),
               STRFTIME('%w', '2024-03-15');
    ''', "2024-03-02|2023-03-03|2024-03-31|5", ["2024-02-29|2023-02-28|2024-03-31|5",
      "2024-02-29|2023-02-28|2024-04-30|4", "2024-03-02|2023-03-03|2024-04-01|5"],
      "+1 month on the 31st overflows into the next month; %w counts Sunday as 0",
      """SQLite adds a month to the month number and then normalises, so 31 January plus one month is a non-
      existent 31 February, which rolls over to 2 March (2024) or 3 March (2023). `start of month`, `+1 month`,
      `-1 day` is the safe way to reach the last day. March 15, 2024 was a Friday, and `%w` numbers Friday 5."""),

    q("recursive-cte-union-stops", r'''
        WITH RECURSIVE c (n) AS (
          SELECT 0 UNION SELECT (n + 1) % 3 FROM c
        )
        SELECT COUNT(*), SUM(n) FROM c;
    ''', "3|3", ["3|6", "1|0", "4|3"],
      "A recursive UNION drops rows it has already seen, which ends the loop",
      """The recursion would cycle 0, 1, 2, 0, 1, 2 forever, but UNION discards a repeated row and the
      queue runs dry after 0, 1, 2. That is three rows adding up to 3. With UNION ALL it would never stop."""),

    q("check-passes-on-null", r'''
        CREATE TABLE t (v INTEGER CHECK (v > 0));
        INSERT OR IGNORE INTO t VALUES (NULL), (-1), (5);
        SELECT COUNT(*), SUM(v) FROM t;
    ''', "2|5", ["1|5", "3|4", "2|NULL"],
      "A CHECK only rejects a row when the test is false, so NULL gets through",
      """`NULL > 0` is NULL, not false, and a CHECK constraint fails only on false. The NULL row is therefore
      stored, as is 5, while -1 fails the check and `OR IGNORE` quietly skips it."""),

    q("order-by-alias-wins", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (2), (3);
        SELECT 0 - v AS v FROM t ORDER BY v;
    ''', "-3; -2; -1", ["-1; -2; -3", "1; 2; 3", "3; 2; 1"],
      "In ORDER BY, a result alias beats a table column of the same name",
      """The output column is named `v` and so is the table's column. ORDER BY looks at the result aliases
      first, so it sorts the negated values: -3, -2, -1. Sorting by the table's v would have printed -1 first."""),
)
