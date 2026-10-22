"""Gotchas, SQL (third deck): SQLite 3.45 through python's sqlite3; portability notes are in langs.py (`sql`).

New angles on the first two decks: three-valued logic and operator quirks, number and text conversions, scalar
string functions, constraints and keys, joins beyond the basics, window frames, recursive CTEs and strftime on
fixed dates (never the clock). Each card ends with ONE select, always ordered when it returns several rows.
"""

from __future__ import annotations

from .items import Item, make

q = make("sql")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking ──────────────────────────────────────────────────────
    q("three-valued-and-or-not", r'''
        SELECT 1 AND NULL, 0 AND NULL, 1 OR NULL, 0 OR NULL, NOT NULL,
               NULL AND NULL, NOT 1 = 2;
    ''', "NULL|0|1|NULL|NULL|NULL|1", ["0|0|1|0|1|0|1", "NULL|NULL|1|NULL|NULL|NULL|0",
                                       "NULL|0|NULL|1|NULL|NULL|1"],
      "A false AND anything is false and a true OR anything is true, even with NULL; otherwise NULL wins",
      """NULL means 'unknown'. `0 AND NULL` is false because no value of the unknown could make it true, and
      `1 OR NULL` is true for the same reason. `1 AND NULL` and `0 OR NULL` depend on the unknown, so they are NULL,
      like `NOT NULL`. `NOT` binds looser than `=`, so `NOT 1 = 2` is `NOT (1 = 2)`: 1."""),

    q("chained-comparison-compares-the-boolean", r'''
        SELECT 1 < 2 < 3, 3 > 2 > 1, 5 = 5 = 1, 2 = 2 = 2;
    ''', "1|0|1|0", ["1|1|1|1", "1|0|0|0", "1|1|1|0"],
      "a < b < c is (a < b) < c: the first comparison's 0 or 1 is compared with c",
      """SQL has no chained comparisons. `3 > 2 > 1` is `(3 > 2) > 1`, which is `1 > 1`: false. The same happens with
      `=`: `5 = 5 = 1` is `1 = 1`, true, while `2 = 2 = 2` is `1 = 2`, false."""),

    q("hex-and-real-literals", r'''
        SELECT 0x10, 0xFF + 1, TYPEOF(0x10), 1e3, TYPEOF(1e3), .5 + .5, 5. + 1,
               -0x10;
    ''', "16|256|integer|1000.0|real|1.0|6.0|-16", ["16|256|text|1000|integer|1|6|-16",
                                                     "16|256|integer|1000|real|1.0|6.0|-16",
                                                     "10|256|integer|1000.0|real|1.0|6.0|-16"],
      "A 0x literal is an integer, and any literal with an exponent or a point is a real",
      """`0x10` is the integer 16 and prints as such. `1e3` has an exponent, so it is a real number and prints as
      1000.0. `.5` and `5.` are valid real literals, and adding reals gives reals: 1.0 and 6.0."""),

    q("distinct-inside-aggregates", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (1), (2);
        SELECT SUM(v), SUM(DISTINCT v), AVG(v), AVG(DISTINCT v),
               COUNT(DISTINCT v) FROM t;
    ''', "4|3|1.3333333333333333|1.5|2", ["4|4|1.3333333333333333|1.3333333333333333|2",
                                         "4|3|1.5|1.5|2", "4|3|1.3333333333333333|1.5|3"],
      "DISTINCT inside an aggregate removes repeated values before the function is applied",
      """`SUM(v)` adds 1 + 1 + 2, but `SUM(DISTINCT v)` adds only 1 and 2. In the same way `AVG(DISTINCT v)` averages
      the two distinct values, 1.5, while `AVG(v)` is 4 / 3."""),

    q("iif-coalesce-nullif-guards", r'''
        SELECT IIF(NULL, 'y', 'n'), IIF(0, 'y', 'n'), IIF('0', 'y', 'n'),
               IIF('a', 'y', 'n'), COALESCE(NULL, 0, 5), 10 / NULLIF(0, 0),
               COALESCE(NULLIF('', ''), 'blank'), IIF('2abc', 'y', 'n');
    ''', "n|n|n|n|0|NULL|blank|y", ["n|n|y|y|0|NULL|blank|y", "n|n|n|n|5|NULL|blank|y", "n|n|n|n|0|0|blank|n"],
      "A condition is true when it is a non-zero number; text counts as the number it starts with",
      """`IIF` tests its first argument as a number: NULL, 0, '0' and 'a' (which reads as 0) are all false, while '2abc'
      reads as 2 and is true. `COALESCE` returns the first non-NULL value, and 0 is not NULL. `NULLIF(0, 0)` is NULL,
      which turns a division by zero into a NULL result."""),

    q("explicit-null-overrides-default", r'''
        CREATE TABLE t (a INTEGER DEFAULT 5, b TEXT DEFAULT 'x');
        INSERT INTO t (a, b) VALUES (NULL, NULL);
        INSERT INTO t DEFAULT VALUES;
        INSERT INTO t (b) VALUES (NULL);
        SELECT a, b FROM t ORDER BY rowid;
    ''', "NULL|NULL; 5|x; 5|NULL", ["5|x; 5|x; 5|x", "NULL|NULL; 5|x; NULL|NULL", "5|NULL; 5|x; 5|NULL"],
      "DEFAULT is used only for a column that is left out; writing NULL stores NULL",
      """The first insert names both columns and gives NULL for each, so NULL is stored. `DEFAULT VALUES` leaves out
      every column, so both defaults apply. The third insert leaves out `a`, which gets 5, and gives NULL for
      `b` explicitly."""),

    q("update-from-empty-subquery-sets-null", r'''
        CREATE TABLE t (k INTEGER, v TEXT);
        CREATE TABLE u (k INTEGER, w TEXT);
        INSERT INTO t VALUES (1, 'old'), (2, 'old');
        INSERT INTO u VALUES (1, 'new');
        UPDATE t SET v = (SELECT w FROM u WHERE u.k = t.k);
        SELECT k, v FROM t ORDER BY k;
    ''', "1|new; 2|NULL", ["1|new; 2|old", "1|new", "1|new; 2|"],
      "A scalar subquery with no rows is NULL, so an UPDATE with no match overwrites the value with NULL",
      """The subquery finds a row only for k = 1. For k = 2 it returns nothing, which counts as NULL, and the
      `SET` assigns that NULL instead of leaving the old value. Add `WHERE k IN (SELECT k FROM u)` to touch only the
      matching rows."""),

    # ── Medium ───────────────────────────────────────────────────────────
    q("row-values-compare-lexicographically", r'''
        SELECT (1, 2) < (1, 3), (2, 1) > (1, 9), (1, NULL) = (1, NULL),
               (1, 2) IN (VALUES (1, 2), (3, 4)), (1, 2) = (1, 2);
    ''', "1|1|NULL|1|1", ["1|0|NULL|1|1", "1|1|1|1|1", "1|1|NULL|0|1"],
      "Row values compare element by element from the left; a NULL inside makes an equality unknown",
      """`(2, 1) > (1, 9)` is decided by the first elements alone: 2 is greater than 1. `(1, NULL) = (1, NULL)` is
      unknown, because the second pair cannot be shown equal, so the result is NULL. `IN` with a `VALUES` list
      matches whole rows."""),

    q("text-to-number-in-arithmetic", r'''
        SELECT 'abc' + 1, '3abc' + 1, '1e2' + 0, '0x10' + 0, ' 5' + 0,
               TYPEOF(+'5'), '5' + 0 = 5;
    ''', "1|4|100.0|0|5|text|1", ["error|4|100.0|0|5|text|1", "1|4|100|16|5|integer|1", "1|4|100.0|0|5|integer|1"],
      "Arithmetic reads the leading number of a text, 0 if there is none, and unary plus changes nothing",
      """`'abc'` has no leading number, so it counts as 0; `'3abc'` counts as 3. `'1e2'` reads as the real number 100.0,
      and `'0x10'` as 0, since hex is not parsed from text. A leading space is ignored. Unary `+` does not convert, so
      `+'5'` is still text."""),

    q("modulo-sign-and-floats", r'''
        SELECT 5 % -3, -5 % 3, -5 % -3, 5.5 % 2, TYPEOF(5.5 % 2), 7 % 2.5;
    ''', "2|-2|-2|1.0|real|1.0", ["2|1|-2|1.5|real|1.5", "-1|1|-2|1.0|real|1.0", "2|-2|-2|1.5|real|1.0"],
      "% takes the sign of the dividend, and on reals it first drops the fractions, then returns a real",
      """The remainder follows the left operand, so `-5 % 3` is -2 and `5 % -3` is 2. When either side is a real,
      both are cut to integers first: 5.5 % 2 is 5 % 2, which is 1, written as the real 1.0. The same cut turns
      `7 % 2.5` into `7 % 2`."""),

    q("cast-text-to-integer-edges", r'''
        SELECT CAST(' 12' AS INTEGER), CAST('1e3' AS INTEGER), CAST(1e3 AS INTEGER),
               CAST('0x1A' AS INTEGER), CAST(2.5 AS TEXT), CAST(x'41' AS TEXT),
               CAST('9223372036854775808' AS INTEGER), CAST('-7.9' AS INTEGER);
    ''', "12|1|1000|0|2.5|A|9223372036854775807|-7", ["12|1000|1000|26|2.5|A|9223372036854775807|-7",
                                                     "12|1|1000|0|2.5|41|9223372036854775807|-8",
                                                     "12|1|1000|0|2.5|A|-9223372036854775808|-7"],
      "Casting text to an integer reads only the leading digits; numbers are cut toward zero",
      """`CAST('1e3' AS INTEGER)` stops at the `e` and gives 1, but casting the real number 1e3 gives 1000. Hex text is
      not parsed, so it gives 0. A blob cast to text is read as text: `x'41'` is "A". Text too large for 64 bits
      clamps to the largest integer, and `-7.9` is truncated to -7."""),

    q("round-negative-digits-and-halves", r'''
        SELECT ROUND(1234.5678, -2), ROUND(2.675, 2), ROUND(1.005, 2), ROUND(-0.5),
               ROUND(5.5), ROUND(6.5), ROUND(1234.5678, 1);
    ''', "1235.0|2.67|1.0|-1.0|6.0|7.0|1234.6", ["1200.0|2.68|1.01|0.0|6.0|6.0|1234.6",
                                                 "1235.0|2.68|1.01|-1.0|6.0|7.0|1234.6",
                                                 "1235.0|2.67|1.0|-1.0|6.0|6.0|1234.6"],
      "ROUND ignores negative digit counts, rounds halves away from zero, and uses the stored binary value",
      """A negative number of digits is treated as 0, so 1234.5678 becomes 1235.0, not 1200. Halves go away from zero,
      so 5.5 gives 6.0 and 6.5 gives 7.0 (not 6.0). 2.675 and 1.005 are really stored a hair below those decimals,
      so they round down to 2.67 and 1.0."""),

    q("scalar-max-text-beats-number", r'''
        SELECT MAX(5, 'a'), MIN(5, 'a'), MAX(10, '9'), MIN(10, '9'), MAX('B', 'a'),
               TYPEOF(MAX(1, 2.0));
    ''', "a|5|9|10|a|real", ["5|a|10|9|a|real", "a|5|10|9|a|real", "a|5|9|10|B|integer"],
      "With several arguments, text sorts after every number, so MAX picks the text",
      """Between values of different types, SQLite orders numbers before text. `MAX(5, 'a')` is therefore "a", and
      `MAX(10, '9')` is the text "9", even though 10 is numerically bigger. Two texts compare as bytes, so lower-case
      "a" beats "B". `MAX(1, 2.0)` returns 2.0, a real."""),

    q("string-function-edge-cases", r'''
        SELECT INSTR('hello', 'l'), INSTR('hello', 'z'), INSTR('abc', ''),
               REPLACE('aaa', 'aa', 'b'), REPLACE('abc', '', 'x'),
               TRIM('xxhixx', 'x'), LTRIM('0042', '0'), RTRIM('a.0.0', '.0'),
               UPPER('abC'), LENGTH(12.50);
    ''', "3|0|1|ba|abc|hi|42|a|ABC|4", ["3|0|0|ba|abc|hi|42|a|ABC|5", "3|0|1|bb|xaxbxcx|hi|42|a|ABC|4",
                                       "3|-1|1|ba|abc|hi|42|a.|ABC|4"],
      "INSTR is 1-based (0 if absent), REPLACE with an empty pattern does nothing, TRIM takes a set",
      """`INSTR` returns the position of the first match, counting from 1, and 0 if there is none. `REPLACE` scans left to
      right without overlap, so "aaa" gives "ba". `TRIM`, `LTRIM` and `RTRIM` remove any of the listed characters, in
      any order. A number is turned into text first: 12.50 is "12.5", which has 4 characters."""),

    q("length-of-numbers-blobs-and-nulls", r'''
        SELECT LENGTH(123.0), LENGTH(12345), LENGTH(x'0102'), LENGTH(NULL),
               LENGTH(CHAR(233)), LENGTH(HEX(CHAR(233))), UNICODE('A'),
               CHAR(72, 105), UNICODE('');
    ''', "5|5|2|NULL|1|4|65|Hi|NULL", ["3|5|2|0|1|4|65|Hi|NULL", "5|5|2|NULL|2|4|65|Hi|NULL",
                                       "5|5|2|NULL|1|2|65|Hi|0"],
      "LENGTH counts characters in text, bytes in a blob, and the printed form of a number",
      """123.0 is written "123.0", which is 5 characters. A blob's length is its byte count, and NULL has no length.
      `CHAR(233)` is a single character, but its UTF-8 form is two bytes, which `HEX` shows as 4 hex digits.
      `UNICODE('')` has no first character, so it is NULL."""),

    q("printf-conversions", r'''
        SELECT PRINTF('%d|%s|%05.1f|%x|%5s|%-5s|%c', 3.99, 1.0, 3.14159, 255, 'ab',
                      'ab', 65);
    ''', "3|1.0|003.1|ff|   ab|ab   |6", ["4|1|003.1|FF|   ab|ab   |A", "3|1.0|003.1|ff|ab   |   ab|6",
                                          "3|1.0|3.1|ff|   ab|ab   |A"],
      "printf cuts a real for %d, shows 1.0 for %s, and %c uses the first character of the argument's text",
      """`%d` cuts 3.99 down to 3, and `%s` prints the real as the text "1.0". `%05.1f` pads with zeros to width 5. Widths
      pad on the left, and `-` pads on the right. `%c` prints the first character of its argument as text, and the
      text of 65 starts with 6."""),

    q("glob-sets-and-case", r'''
        SELECT 'abc' GLOB 'a*', 'Abc' GLOB 'a*', 'b2' GLOB '[a-c][0-9]',
               'b2' GLOB '[^a][0-9]', 'a*c' GLOB 'a[*]c', 'ab' GLOB 'a?',
               'abc' GLOB 'a?';
    ''', "1|0|1|1|1|1|0", ["1|1|1|1|1|1|0", "1|0|1|0|1|1|0", "1|0|1|1|0|1|1"],
      "GLOB is case-sensitive, [..] is a set or range, [^..] negates it, and ? is exactly one character",
      """Unlike `LIKE`, `GLOB` does not ignore case, so 'Abc' does not match 'a*'. `[a-c]` is a range of characters,
      `[^a]` any character except a, and `[*]` is a literal star. `?` stands for exactly one character, so 'ab' fits
      'a?' and 'abc' does not."""),

    q("between-order-and-strings", r'''
        SELECT 'b' BETWEEN 'a' AND 'c', 'B' BETWEEN 'a' AND 'c',
               'abc' BETWEEN 'a' AND 'b', 5 BETWEEN 10 AND 1,
               5 NOT BETWEEN 10 AND 1, 2 BETWEEN 1 AND 1 + 1;
    ''', "1|0|1|0|1|1", ["1|1|1|0|1|1", "1|0|0|0|1|1", "1|0|1|1|0|1"],
      "BETWEEN does not swap its bounds, and text is compared byte by byte, with uppercase first",
      """`x BETWEEN a AND b` means `x >= a AND x <= b`. With the bounds reversed nothing is between, so
      `5 BETWEEN 10 AND 1` is false. 'B' sorts before 'a', so it falls outside 'a' to 'c'. 'abc' is greater than 'a'
      and still less than 'b', so it is inside."""),

    q("in-empty-list-is-always-false", r'''
        SELECT 1 IN (), NULL IN (), 1 NOT IN (), NULL NOT IN (),
               1 IN (SELECT 1 WHERE 0);
    ''', "0|0|1|1|0", ["0|NULL|1|NULL|0", "0|0|1|NULL|0", "0|0|0|1|0"],
      "IN with an empty list is false and NOT IN is true, even for NULL",
      """With nothing to compare against, there is no unknown: `IN ()` is plainly false and `NOT IN ()` plainly true,
      even when the left side is NULL. A subquery that returns no rows behaves the same way. (SQLite accepts the
      empty list; most databases do not.)"""),

    q("alias-usable-in-where-and-having", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (2), (3), (4);
        SELECT v * 2 AS d FROM t WHERE d > 4 ORDER BY d;
    ''', "6; 8", ["2; 3", "8", "2; 4; 6; 8"],
      "SQLite lets a WHERE clause use an alias defined in the select list; standard SQL does not",
      """The condition `d > 4` is evaluated as `v * 2 > 4`, so the rows 3 and 4 survive and show their doubled values.
      This is a SQLite extension: in most databases the alias is not visible in `WHERE` and the query fails."""),

    q("having-without-group-by", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (2), (3), (4);
        SELECT (SELECT COUNT(*) FROM
                  (SELECT COUNT(*) FROM t HAVING COUNT(*) > 5)),
               (SELECT COUNT(*) FROM
                  (SELECT COUNT(*) FROM t HAVING COUNT(*) > 3)),
               (SELECT COUNT(*) FROM (SELECT SUM(v) FROM t WHERE v > 100)),
               (SELECT COUNT(*) FROM
                  (SELECT SUM(v) FROM t WHERE v > 100 GROUP BY v));
    ''', "0|1|1|0", ["1|1|1|1", "0|1|0|0", "0|1|1|1"],
      "Without GROUP BY an aggregate query always returns one row; with GROUP BY and no rows, none",
      """An aggregate with no GROUP BY treats the whole table as a single group, so `HAVING` keeps or drops that one
      row (4 > 3 keeps it). Even with no matching rows, `SUM(v)` produces one row of NULL. With `GROUP BY v` there are
      no groups at all, so no row comes out."""),

    q("unique-allows-many-nulls", r'''
        CREATE TABLE t (v TEXT UNIQUE);
        INSERT OR IGNORE INTO t VALUES ('a'), ('a'), (NULL), (NULL);
        SELECT COUNT(*), COUNT(v) FROM t;
    ''', "3|1", ["2|1", "4|2", "1|1"],
      "UNIQUE rejects a repeated value but treats each NULL as different; OR IGNORE skips the bad rows",
      """The second 'a' breaks the UNIQUE rule and is skipped by `OR IGNORE`, while both NULLs are accepted, because
      two NULLs are never considered equal. That leaves three rows, of which only one has a non-NULL value."""),

    q("int-primary-key-allows-null", r'''
        CREATE TABLE t (id INT PRIMARY KEY, v TEXT);
        CREATE TABLE u (id INTEGER PRIMARY KEY, v TEXT);
        INSERT INTO t VALUES (NULL, 'a'), (NULL, 'b');
        INSERT INTO u VALUES (NULL, 'a'), (NULL, 'b');
        SELECT (SELECT COUNT(id) FROM t), (SELECT COUNT(id) FROM u),
               (SELECT MAX(id) FROM u);
    ''', "0|2|2", ["2|2|2", "0|0|0", "0|2|NULL"],
      "Only the exact type name INTEGER makes a primary key the rowid; INT PRIMARY KEY accepts NULL",
      """Only `INTEGER PRIMARY KEY` becomes an alias of the rowid, which assigns numbers 1, 2 when you insert NULL.
      A column declared `INT PRIMARY KEY` is an ordinary column with a unique index, and SQLite (unlike most
      databases) allows NULL in it, so the two NULL ids are kept as NULL."""),

    q("integer-primary-key-null-picks-max-plus-one", r'''
        CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT);
        INSERT INTO t VALUES (5, 'a');
        INSERT INTO t VALUES (NULL, 'b');
        INSERT INTO t (v) VALUES ('c');
        INSERT INTO t VALUES (3, 'd');
        INSERT INTO t (v) VALUES ('e');
        SELECT GROUP_CONCAT(id, ',') FROM (SELECT id FROM t ORDER BY v);
    ''', "5,6,7,3,8", ["1,2,3,4,5", "5,1,2,3,4", "5,6,7,3,4"],
      "A NULL or missing INTEGER PRIMARY KEY gets one more than the largest id so far, not a free number",
      """After the explicit id 5, the next automatic ids are 6 and 7. Inserting the explicit id 3 afterwards does not
      lower the maximum, so the following automatic id is 8, and the gap below 5 is never filled."""),

    q("ctas-drops-constraints", r'''
        CREATE TABLE a (id INTEGER PRIMARY KEY, v TEXT NOT NULL);
        INSERT INTO a VALUES (1, 'x');
        CREATE TABLE b AS SELECT * FROM a;
        INSERT INTO b VALUES (NULL, NULL), (1, 'y'), (1, 'z');
        SELECT COUNT(*), COUNT(id), COUNT(v) FROM b;
    ''', "4|3|3", ["1|1|1", "2|1|1", "4|4|4"],
      "CREATE TABLE AS SELECT copies the rows but none of the keys or NOT NULL rules",
      """The new table has the same column names but no `PRIMARY KEY` and no `NOT NULL`, so inserting a NULL id,
      a NULL value and a repeated id all succeed. That gives the original row plus three: four rows, with three
      non-NULL ids and three non-NULL values."""),

    q("delete-duplicates-keeping-the-first", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (1), (NULL), (NULL), (2), (1);
        DELETE FROM t WHERE rowid NOT IN (SELECT MIN(rowid) FROM t GROUP BY v);
        SELECT COUNT(*), COUNT(v), SUM(v) FROM t;
    ''', "3|2|3", ["4|3|4", "3|2|4", "6|4|5"],
      "GROUP BY puts all NULLs in one group, so the dedupe keeps a single NULL row too",
      """The subquery returns the smallest rowid of each group: one row each for 1, NULL and 2. The `DELETE` removes every
      other row. Although NULLs are never equal in a comparison, `GROUP BY` collects them into one group, so
      only one NULL row survives."""),

    q("returning-shows-the-stored-row", r'''
        CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT DEFAULT 'd',
                        n INTEGER DEFAULT 5);
        INSERT INTO t DEFAULT VALUES;
        INSERT INTO t (v) VALUES (NULL) RETURNING id, v, n;
    ''', "2|NULL|5", ["2|d|5", "1|NULL|5", "2|NULL|NULL"],
      "RETURNING reports the row as stored, with generated ids and defaults filled in",
      """The first insert took id 1, so the second gets id 2. The explicit NULL for `v` is stored as NULL and does not
      trigger the default, but `n` was left out and gets its default 5. `RETURNING` shows these final values."""),

    q("using-merges-the-join-column", r'''
        CREATE TABLE a (id INTEGER, x TEXT);
        CREATE TABLE b (id INTEGER, y TEXT);
        INSERT INTO a VALUES (1, 'p');
        INSERT INTO b VALUES (1, 'q');
        SELECT * FROM a JOIN b USING (id);
    ''', "1|p|q", ["1|p|1|q", "1|p", "p|q"],
      "USING (col) joins on that column and shows it once in SELECT *; ON would show both",
      """With `USING (id)` the two `id` columns are merged into one, so `SELECT *` returns three columns. A join written
      as `ON a.id = b.id` would keep both ids and return four."""),

    q("natural-join-matches-every-shared-column", r'''
        CREATE TABLE a (id INTEGER, name TEXT);
        CREATE TABLE b (id INTEGER, name TEXT, x TEXT);
        INSERT INTO a VALUES (1, 'p'), (2, 'q');
        INSERT INTO b VALUES (1, 'p', 'm'), (2, 'z', 'n');
        SELECT COUNT(*),
               (SELECT COUNT(*) FROM a JOIN b ON a.id = b.id)
        FROM a NATURAL JOIN b;
    ''', "1|2", ["2|2", "1|1", "2|1"],
      "NATURAL JOIN joins on all columns with the same name, not only the key you had in mind",
      """Both tables have `id` and `name`, so the natural join requires both to be equal. Only the row (1, 'p') matches
      in both, giving 1, while joining on `id` alone matches both rows. Adding a column to a table can silently
      change a natural join."""),

    q("cross-join-and-self-join-pair-counts", r'''
        CREATE TABLE a (id INTEGER);
        CREATE TABLE b (x INTEGER);
        INSERT INTO a VALUES (1), (2), (3);
        INSERT INTO b VALUES (1), (2), (3), (4);
        SELECT (SELECT COUNT(*) FROM a CROSS JOIN b),
               (SELECT COUNT(*) FROM a, a AS a2 WHERE a.id < a2.id),
               (SELECT COUNT(*) FROM a JOIN a AS a2 ON a.id <> a2.id),
               (SELECT COUNT(*) FROM a JOIN a AS a2);
    ''', "12|3|6|9", ["7|3|6|9", "12|6|3|9", "12|3|6|6"],
      "A join with no condition pairs every row with every row; < counts each pair once, <> twice",
      """`a CROSS JOIN b` gives 3 x 4 = 12 rows. Joining a table to itself with `a.id < a2.id` counts each unordered pair
      once (3), whereas `<>` counts both orders (6), and no condition at all gives 3 x 3 = 9, including each
      row with itself."""),

    q("order-by-nulls-last-and-collate", r'''
        CREATE TABLE t (v TEXT);
        INSERT INTO t VALUES ('b'), ('A'), ('c'), (NULL), ('D');
        SELECT v FROM t ORDER BY v COLLATE NOCASE DESC NULLS LAST;
    ''', "D; c; b; A; NULL", ["NULL; D; c; b; A", "c; b; D; A; NULL", "D; A; c; b; NULL"],
      "COLLATE NOCASE compares letters ignoring case, and NULLS LAST overrides where NULL sorts",
      """Ignoring case the order from high to low is D, c, b, A. Without `COLLATE NOCASE` the uppercase letters would
      sort before the lowercase ones. NULL counts as the smallest value, so it would come last in a descending
      sort anyway; `NULLS LAST` makes that explicit, and `NULLS FIRST` would do the opposite."""),

    q("order-by-column-number", r'''
        CREATE TABLE t (a INTEGER, b INTEGER);
        INSERT INTO t VALUES (1, 30), (2, 10), (3, 20);
        SELECT b, a FROM t ORDER BY 2 DESC, 1;
    ''', "20|3; 10|2; 30|1", ["10|2; 20|3; 30|1", "30|1; 20|3; 10|2", "20|3; 30|1; 10|2"],
      "ORDER BY 2 means the second column of the select list, not of the table",
      """The select list is `b, a`, so position 2 is `a`. Sorting by `a` descending gives the rows with a = 3, 2, 1, which
      are the pairs (20, 3), (10, 2) and (30, 1). Sorting by the second column of the table would use `b`."""),

    # ── Windows, CTEs and dates ─────────────────────────────────────────────
    q("row-number-top-one-per-group", r'''
        CREATE TABLE s (g TEXT, v INTEGER);
        INSERT INTO s VALUES ('a', 3), ('a', 9), ('b', 4), ('b', 1), ('c', 7);
        SELECT g, v FROM (
          SELECT g, v, ROW_NUMBER() OVER (PARTITION BY g ORDER BY v DESC) AS rn
          FROM s)
        WHERE rn = 1 ORDER BY g;
    ''', "a|9; b|4; c|7", ["a|3; b|1; c|7", "a|9; b|4", "a|9; a|3; b|4; b|1; c|7"],
      "A window function cannot be filtered in the same query's WHERE, so wrap it in a subquery",
      """`PARTITION BY g` restarts the numbering for each group, and `ORDER BY v DESC` gives the largest value number 1.
      The filter `rn = 1` must be applied outside the subquery, since windows are computed after `WHERE`. The result
      is the top value per group."""),

    q("last-value-default-frame", r'''
        CREATE TABLE t (id INTEGER, v INTEGER);
        INSERT INTO t VALUES (1, 10), (2, 20), (3, 30);
        SELECT LAST_VALUE(v) OVER (ORDER BY id),
               LAST_VALUE(v) OVER (ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING
                                   AND UNBOUNDED FOLLOWING)
        FROM t ORDER BY id;
    ''', "10|30; 20|30; 30|30", ["30|30; 30|30; 30|30", "10|10; 20|10; 30|10", "10|30; 20|20; 30|30"],
      "The default window frame ends at the current row, so LAST_VALUE returns the current row's own value",
      """With an `ORDER BY` the default frame runs from the first row to the current one, and the last value in that frame
      is the current row itself: 10, 20, 30. Widening the frame to include the following rows makes `LAST_VALUE`
      return the true last value, 30, for every row."""),

    q("nth-value-grows-with-the-frame", r'''
        CREATE TABLE t (id INTEGER, v INTEGER);
        INSERT INTO t VALUES (1, 10), (2, 20), (3, 30);
        SELECT NTH_VALUE(v, 2) OVER (ORDER BY id),
               FIRST_VALUE(v) OVER (ORDER BY id DESC),
               LEAD(v, 2, -1) OVER (ORDER BY id)
        FROM t ORDER BY id;
    ''', "NULL|30|30; 20|30|-1; 20|30|-1", ["20|30|30; 20|30|-1; 20|30|-1", "NULL|10|30; 20|10|-1; 20|10|-1",
                                            "NULL|30|30; 20|30|30; 30|30|-1"],
      "The default frame ends at the current row, so NTH_VALUE is NULL until the n-th row is reached",
      """For the first row the frame holds just one row, so there is no second value yet. Later frames include the
      second row, whose value is 20. `FIRST_VALUE` over a descending order is the largest id's value, 30, and
      `LEAD(v, 2, -1)` looks two rows ahead, returning the default -1 when there is no such row."""),

    q("percent-rank-and-cume-dist", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (10), (20), (20), (30);
        SELECT v, ROUND(PERCENT_RANK() OVER (ORDER BY v), 2),
               CUME_DIST() OVER (ORDER BY v)
        FROM t ORDER BY v;
    ''', "10|0.0|0.25; 20|0.33|0.75; 20|0.33|0.75; 30|1.0|1.0",
      ["10|0.0|0.25; 20|0.33|0.5; 20|0.67|0.75; 30|1.0|1.0", "10|0.25|0.25; 20|0.5|0.75; 20|0.5|0.75; 30|1.0|1.0",
       "10|0.0|0.0; 20|0.33|0.5; 20|0.33|0.5; 30|1.0|1.0"],
      "PERCENT_RANK is (rank - 1) / (rows - 1); CUME_DIST is the share of rows up to and including the ties",
      """The two 20s share rank 2, so their `PERCENT_RANK` is (2 - 1) / (4 - 1) = 0.33. `CUME_DIST` counts every row
      with a value up to and including the current one, ties included: 3 of 4 rows are at most 20, so 0.75 for both."""),

    q("range-frame-uses-values-not-rows", r'''
        CREATE TABLE t (g INTEGER);
        INSERT INTO t VALUES (1), (2), (4), (5);
        SELECT g,
          COUNT(*) OVER (ORDER BY g RANGE BETWEEN 1 PRECEDING AND CURRENT ROW),
          COUNT(*) OVER (ORDER BY g ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)
        FROM t ORDER BY g;
    ''', "1|1|1; 2|2|2; 4|1|2; 5|2|2", ["1|1|1; 2|2|2; 4|2|2; 5|2|2", "1|1|1; 2|1|2; 4|1|2; 5|1|2",
                                        "1|1|1; 2|2|2; 4|1|1; 5|2|2"],
      "RANGE looks at the values of the ORDER BY column; ROWS counts physical neighbours",
      """`RANGE BETWEEN 1 PRECEDING` includes rows whose g is within 1 below the current value. For g = 4 no row has g = 3,
      so only the row itself counts, and the answer is 1. `ROWS BETWEEN 1 PRECEDING` simply includes the previous
      row, so g = 4 sees g = 2 and counts 2."""),

    q("window-sees-only-filtered-rows", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (2), (3), (4);
        SELECT v, COUNT(*) OVER (), SUM(v) OVER () FROM t WHERE v > 2 ORDER BY v;
    ''', "3|2|7; 4|2|7", ["3|4|10; 4|4|10", "3|1|3; 4|2|7", "3|2|3; 4|2|4"],
      "Window functions are computed after WHERE, so they only see the rows that passed the filter",
      """The rows with v <= 2 are removed first, so the empty `OVER ()` window contains only 3 and 4: two rows
      adding up to 7, repeated on each output row."""),

    q("window-over-grouped-rows", r'''
        CREATE TABLE t (g TEXT, v INTEGER);
        INSERT INTO t VALUES ('a', 1), ('a', 2), ('b', 3);
        SELECT g, SUM(v), SUM(SUM(v)) OVER (),
               ROUND(100.0 * SUM(v) / SUM(SUM(v)) OVER ())
        FROM t GROUP BY g ORDER BY g;
    ''', "a|3|6|50.0; b|3|6|50.0", ["a|3|3|100.0; b|3|3|100.0", "a|3|6|50.0; b|3|6|100.0",
                                    "a|1|6|17.0; b|3|6|50.0"],
      "A window runs after GROUP BY, so it can sum the group totals",
      """`GROUP BY` first reduces the table to one row per group (a: 3, b: 3). Then `SUM(SUM(v)) OVER ()` adds those
      group totals, 6, on every row, which gives each group a 50% share."""),

    q("recursive-factorial-overflows-to-real", r'''
        WITH RECURSIVE f (n, p) AS (
          SELECT 1, 1 UNION ALL SELECT n + 1, p * (n + 1) FROM f WHERE n < 21
        )
        SELECT n, p, TYPEOF(p) FROM f WHERE n IN (20, 21) ORDER BY n;
    ''', "20|2432902008176640000|integer; 21|5.109094217170944e+19|real",
      ["20|2432902008176640000|integer; 21|51090942171709440000|integer",
       "20|2432902008176640000|integer; 21|-4249290049419214848|integer",
       "20|2.43290200817664e+18|real; 21|5.109094217170944e+19|real"],
      "When integer multiplication overflows, SQLite continues in floating point instead of wrapping",
      """20! is 2432902008176640000, which still fits in a 64-bit integer. 21! is about 5.1 x 10^19, which does not, so
      SQLite converts that product to a real number and the type changes to real; it does not wrap around to a negative
      number or fail."""),

    q("limit-stops-an-endless-recursive-cte", r'''
        WITH RECURSIVE c (n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM c LIMIT 5)
        SELECT COUNT(*), SUM(n), MAX(n) FROM c;
    ''', "5|15|5", ["5|15|6", "4|10|4", "6|21|6"],
      "A LIMIT inside a recursive CTE stops the recursion once enough rows exist",
      """Without a stopping condition the recursion would go on forever. The `LIMIT 5` inside the CTE makes SQLite stop
      generating rows after the fifth, which is the row with n = 5."""),

    q("recursive-cte-splits-a-string", r'''
        WITH RECURSIVE s (i, w, rest) AS (
          SELECT 0, '', 'a,bb,c' || ','
          UNION ALL
          SELECT i + 1, SUBSTR(rest, 1, INSTR(rest, ',') - 1),
                 SUBSTR(rest, INSTR(rest, ',') + 1)
          FROM s WHERE rest <> ''
        )
        SELECT GROUP_CONCAT(w, '|') FROM (SELECT w FROM s WHERE i > 0 ORDER BY i);
    ''', "a|bb|c", ["a|bb|c|", "|a|bb|c", "a,bb,c"],
      "Each pass cuts off the text before the next comma and keeps the rest for the next pass",
      """The trailing comma added to the text makes every item end with a comma, so `INSTR` always finds one. Each row
      takes the part before it as `w` and passes the remainder on, until nothing is left. The seed row has an empty
      `w`, which the outer filter `i > 0` removes."""),

    q("strftime-weekday-and-year-modifiers", r'''
        SELECT STRFTIME('%Y-%m-%d', '2024-03-15', 'weekday 0'),
               STRFTIME('%Y-%m-%d', '2024-02-29', '+1 year'),
               STRFTIME('%j', '2024-12-31'),
               STRFTIME('%Y-%m-%d', '2024-03-15', 'start of year',
                        '+1 year', '-1 day');
    ''', "2024-03-17|2025-03-01|366|2024-12-31", ["2024-03-10|2025-02-28|365|2024-12-31",
                                                   "2024-03-17|2025-02-28|366|2024-12-31",
                                                   "2024-03-17|2025-03-01|366|2025-12-31"],
      "'weekday 0' moves forward to the next Sunday, and +1 year from 29 February overflows into March",
      """The modifier `weekday 0` advances to the next Sunday, or stays if the day already is one: 15 March 2024 is a
      Friday, so the date becomes the 17th. Adding a year to 29 February 2024 gives the non-existent 29 February 2025,
      which normalises to 1 March. 2024 is a leap year, so 31 December is day 366."""),

    q("strftime-epoch-and-differences", r'''
        SELECT STRFTIME('%s', '1970-01-02'),
               TYPEOF(STRFTIME('%s', '1970-01-02')),
               (STRFTIME('%s', '2024-03-01')
                - STRFTIME('%s', '2024-02-01')) / 86400,
               STRFTIME('%W', '2024-01-07'),
               STRFTIME('%H:%M', '2024-01-01 13:45:10');
    ''', "86400|text|29|01|13:45", ["86400|integer|29|01|13:45", "86400|text|28|01|13:45",
                                    "86400|text|29|53|13:45"],
      "strftime always returns text, but text that looks like a number takes part in arithmetic",
      """`%s` gives the Unix time, 86400 seconds for the second day, as text. Subtracting two such texts converts them to
      numbers, and dividing by 86400 gives the 29 days of February 2024. `%W` is the week of the year counted from
      the first Monday, so 7 January is still week 01."""),
)
