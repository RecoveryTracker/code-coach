"""Gotchas, SQL: SQLite in memory, last SELECT printed `a|b; c|d`; portability notes are in langs.py (`sql`)."""

from __future__ import annotations

from .items import Item, make

q = make("sql")

ITEMS: tuple[Item, ...] = (
    q("null-counts", r'''
        CREATE TABLE t (v INTEGER);
        INSERT INTO t VALUES (1), (NULL), (3);
        SELECT COUNT(*), COUNT(v), SUM(v),
               (SELECT COUNT(*) FROM t WHERE v <> 1)
        FROM t;
    ''', "3|2|4|1", ["3|3|4|2", "3|2|4|2", "2|2|4|1"],
      "COUNT(column) skips NULLs, and NULL <> 1 is neither true nor false",
      """`COUNT(*)` counts rows, `COUNT(v)` counts only the non-NULL values, and `SUM` ignores NULL. The `WHERE
      v <> 1` test on the NULL row is unknown, not true, so only the row with 3 passes."""),

    q("integer-division-and-affinity", r'''
        SELECT 7 / 2, 7 / 2.0, -7 / 2, -7 % 3, '5' + '5', '5' || '5';
    ''', "3|3.5|-3|-1|10|55", ["3.5|3.5|-3.5|2|55|10", "3|3.5|-4|2|10|55", "3|3.5|-3|-1|55|10"],
      "Integer division truncates in SQLite, and + is numeric while || is text",
      """With two integers `/` does integer division and truncates toward zero, so -7 / 2 is -3 and -7 % 3 is
      -1. One decimal operand makes the result decimal. `+` always converts both sides to numbers, so '5' + '5'
      is 10; only `||` joins text."""),

    q("text-versus-number-order", r'''
        SELECT '10' < '9', 10 < 9, '10' < 9;
    ''', "1|0|0", ["0|0|0", "1|0|1", "0|0|1"],
      "Text compares character by character, and any number sorts before any text",
      """Two texts compare like a dictionary: '1' comes before '9', so '10' < '9' is true. Two numbers compare by
      value. A number versus a literal text is never converted here: every number sorts before every text, so
      '10' < 9 is false."""),
)
