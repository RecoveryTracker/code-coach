"""SQL core pack, part 1: Row Count, NULL Logic and Group Result.

Every answer is worked out by hand with `_sql_model.py` (three-valued logic, WHERE keeping only the True rows, aggregates
that skip NULLs, groups), and tests/test_brain_packs.py runs every script in a fresh in-memory SQLite (tests/sql_oracle.py).
A prompt is the whole script - the tables, their rows, then the query that is asked about - and the answer is what the last
SELECT returns, as the driver prints it (one value: a number, a word, NULL).
"""

from __future__ import annotations

import random
from typing import Callable

from ._model import Maker
from ._sql_model import (NULL, Retry, Tbl, avg_, between, count_col, count_distinct, count_star, eq, fit, ge, group, gt,
                         in_list, ints, le, like, lt, max_, min_, ne, not_in, sql_item, sum_, t_and, t_not, t_or,
                         where, with_nulls, words, lit)


# ── 1. Row Count ────────────────────────────────────────────────────────

def _table_t(rng: random.Random, n: int = 6) -> Tbl:
    """t(a INT, b TEXT): small ints with repeats and one NULL, short words with repeats and one NULL."""
    a = with_nulls(rng, [rng.randint(1, 9) for _ in range(n)])
    pool = words(rng, 4)
    b = with_nulls(rng, [rng.choice(pool) for _ in range(n)])
    return Tbl("t", [("a", "INT"), ("b", "TEXT")], list(zip(a, b)))


def _count_where(cond: Callable[[random.Random, Tbl], tuple[str, Callable, str]]) -> Maker:
    def build(rng: random.Random):
        t = _table_t(rng)
        sql, pred, why = cond(rng, t)
        n = count_star(where(t.rows, pred))
        return sql_item([t], f"SELECT COUNT(*) FROM t WHERE {sql};", n, why)
    build.__name__ = cond.__name__
    return fit(build)


def _k(rng: random.Random) -> int:
    return rng.randint(3, 7)


def _letter(t: Tbl, rng: random.Random) -> str:
    return rng.choice([w for w in t.col("b") if w][:])[0]


def c_gt(rng, t):
    k = _k(rng)
    return f"a > {k}", lambda r: gt(r[0], k), "A NULL is not greater than anything, so its row is left out."


def c_le(rng, t):
    k = _k(rng)
    return f"a <= {k}", lambda r: le(r[0], k), "A comparison with NULL is unknown, and WHERE keeps only the true rows."


def c_eq(rng, t):
    k = rng.choice([v for v in t.col("a") if v is not None])
    return f"a = {k}", lambda r: eq(r[0], k), "Only the rows whose a equals the number match."


def c_ne(rng, t):
    k = rng.choice([v for v in t.col("a") if v is not None])
    return f"a <> {k}", lambda r: ne(r[0], k), "<> is also unknown for NULL, so the NULL row is not counted either."


def c_and(rng, t):
    lo, hi = sorted(rng.sample(range(2, 9), 2))
    return f"a >= {lo} AND a <= {hi}", lambda r: t_and(ge(r[0], lo), le(r[0], hi)), "Both conditions must be true; NULL makes them unknown."


def c_between(rng, t):
    lo, hi = sorted(rng.sample(range(2, 9), 2))
    return f"a BETWEEN {lo} AND {hi}", lambda r: between(r[0], lo, hi), "BETWEEN includes both ends and never matches NULL."


def c_not_between(rng, t):
    lo, hi = sorted(rng.sample(range(2, 9), 2))
    return f"a NOT BETWEEN {lo} AND {hi}", lambda r: t_not(between(r[0], lo, hi)), "NOT of an unknown is still unknown, so NULL is not counted."


def c_in(rng, t):
    xs = rng.sample(range(1, 10), 3)
    return f"a IN ({', '.join(map(str, xs))})", lambda r: in_list(r[0], xs), "IN matches the listed values."


def c_not_in(rng, t):
    xs = rng.sample(range(1, 10), 2)
    return f"a NOT IN ({', '.join(map(str, xs))})", lambda r: not_in(r[0], xs), "NOT IN is unknown for a NULL a, so that row is left out."


def c_in_null(rng, t):
    xs = rng.sample(range(1, 10), 2)
    return f"a IN ({xs[0]}, {xs[1]}, NULL)", lambda r: in_list(r[0], xs + [None]), "A NULL in the list never matches anything: only the listed numbers count."


def c_not_in_null(rng, t):
    x = rng.randint(1, 9)
    return f"a NOT IN ({x}, NULL)", lambda r: not_in(r[0], [x, None]), "a NOT IN (x, NULL) is never true: every row is false or unknown."


def c_is_null(rng, t):
    return "a IS NULL", lambda r: r[0] is None, "IS NULL is the way to find NULLs."


def c_is_not_null(rng, t):
    return "a IS NOT NULL", lambda r: r[0] is not None, "Every row that has a number."


def c_eq_null(rng, t):
    return "a = NULL", lambda r: eq(r[0], None), "Comparing with NULL is always unknown, so no row matches."


def c_b_null(rng, t):
    return "b IS NULL", lambda r: r[1] is None, "Only the row with no text."


def c_b_not_null(rng, t):
    return "b IS NOT NULL", lambda r: r[1] is not None, "Every row that has text."


def c_b_eq(rng, t):
    w = rng.choice([v for v in t.col("b") if v])
    return f"b = {lit(w)}", lambda r: eq(r[1], w), "Equal text matches; a NULL never does."


def c_b_ne(rng, t):
    w = rng.choice([v for v in t.col("b") if v])
    return f"b <> {lit(w)}", lambda r: ne(r[1], w), "A NULL b is unknown for <>, so it is not counted."


def c_like_start(rng, t):
    ch = _letter(t, rng)
    return f"b LIKE '{ch}%'", lambda r: like(r[1], ch + "%"), "% matches any run of characters: the text must start with the letter."


def c_like_end(rng, t):
    ch = rng.choice([w for w in t.col("b") if w])[-1]
    return f"b LIKE '%{ch}'", lambda r: like(r[1], "%" + ch), "The text must end with the letter."


def c_like_second(rng, t):
    ch = rng.choice([w for w in t.col("b") if w])[1]
    return f"b LIKE '_{ch}%'", lambda r: like(r[1], "_" + ch + "%"), "_ matches exactly one character: the second letter must match."


def c_like_has(rng, t):
    ch = rng.choice([w for w in t.col("b") if w])[2]
    return f"b LIKE '%{ch}%'", lambda r: like(r[1], "%" + ch + "%"), "% on both sides: the letter may be anywhere."


def c_like_case(rng, t):
    ch = _letter(t, rng).upper()
    return f"b LIKE '{ch}%'", lambda r: like(r[1], ch + "%"), "In SQLite LIKE ignores case for ASCII letters, so the capital matches too."


def c_not_like(rng, t):
    ch = _letter(t, rng)
    return f"b NOT LIKE '{ch}%'", lambda r: t_not(like(r[1], ch + "%")), "NOT LIKE is unknown for NULL: that row is not counted."


def c_or_null(rng, t):
    k = _k(rng)
    return f"a > {k} OR a IS NULL", lambda r: t_or(gt(r[0], k), r[0] is None), "The OR adds the NULL row back: unknown OR true is true."


def c_and_text(rng, t):
    k = _k(rng)
    return f"a > {k} AND b IS NOT NULL", lambda r: t_and(gt(r[0], k), r[1] is not None), "Both conditions must hold."


def c_precedence(rng, t):
    lo, hi = sorted(rng.sample(range(2, 9), 2))
    return (f"a < {lo} OR a > {hi} AND b IS NOT NULL",
            lambda r: t_or(lt(r[0], lo), t_and(gt(r[0], hi), r[1] is not None)),
            "AND binds tighter than OR: it is a < lo, or (a > hi and b is not NULL).")


def c_not(rng, t):
    k = _k(rng)
    return f"NOT (a > {k})", lambda r: t_not(gt(r[0], k)), "NOT of unknown is unknown, so the NULL row stays out."


def c_even(rng, t):
    return "a % 2 = 0", lambda r: eq(None if r[0] is None else r[0] % 2, 0), "% is the remainder: even numbers leave 0."


def c_odd(rng, t):
    return "a % 2 = 1", lambda r: eq(None if r[0] is None else r[0] % 2, 1), "Odd numbers leave a remainder of 1."


def c_arith(rng, t):
    k = rng.randint(8, 14)
    return f"a * 2 > {k}", lambda r: gt(None if r[0] is None else r[0] * 2, k), "The arithmetic is done first; NULL times 2 is still NULL."


def c_length(rng, t):
    n = rng.choice([len(w) for w in t.col("b") if w])
    return f"LENGTH(b) = {n}", lambda r: eq(None if r[1] is None else len(r[1]), n), "LENGTH counts the characters; LENGTH(NULL) is NULL."


def c_self_eq(rng, t):
    return "a = a", lambda r: eq(r[0], r[0]), "a = a is true for every number, but unknown for NULL."


def c_unknown(rng, t):
    k = _k(rng)
    return f"(a > {k}) IS NULL", lambda r: gt(r[0], k) is None, "The comparison is unknown exactly when a is NULL."


def c_b_in(rng, t):
    ws = rng.sample([v for v in set(t.col("b")) if v], 2)
    return f"b IN ({lit(ws[0])}, {lit(ws[1])})", lambda r: in_list(r[1], ws), "Text equal to either listed word."


def c_b_not_in(rng, t):
    ws = rng.sample([v for v in set(t.col("b")) if v], 2)
    return f"b NOT IN ({lit(ws[0])}, {lit(ws[1])})", lambda r: not_in(r[1], ws), "NOT IN leaves out NULL: the answer is rows with other text."


def c_both(rng, t):
    return "a IS NOT NULL AND b IS NOT NULL", lambda r: r[0] is not None and r[1] is not None, "Only rows with no NULL at all."


def c_not_null_expr(rng, t):
    return "NOT (a IS NULL)", lambda r: r[0] is not None, "Same as a IS NOT NULL."


def c_text_cmp(rng, t):
    w = rng.choice([v for v in t.col("b") if v])
    return f"b > {lit(w)}", lambda r: gt(r[1], w), "Text compares in dictionary order; NULL is not greater than anything."


COUNT_CONDS = [c_gt, c_le, c_eq, c_ne, c_and, c_between, c_not_between, c_in, c_not_in, c_in_null, c_not_in_null, c_is_null,
               c_is_not_null, c_eq_null, c_b_null, c_b_not_null, c_b_eq, c_b_ne, c_like_start, c_like_end, c_like_second,
               c_like_has, c_like_case, c_not_like, c_or_null, c_and_text, c_precedence, c_not, c_even, c_odd, c_arith,
               c_length, c_self_eq, c_unknown, c_b_in, c_b_not_in, c_both, c_not_null_expr, c_text_cmp]

COUNT: list[Maker] = [_count_where(c) for c in COUNT_CONDS]


def _distinct_a(rng: random.Random):
    t = _table_t(rng)
    return sql_item([t], "SELECT COUNT(DISTINCT a) FROM t;", count_distinct(t.col("a")), "DISTINCT counts each value once, and COUNT ignores NULL.")


def _distinct_b(rng: random.Random):
    t = _table_t(rng)
    return sql_item([t], "SELECT COUNT(DISTINCT b) FROM t;", count_distinct(t.col("b")), "Each different word once; the NULL is not counted.")


def _count_all(rng: random.Random):
    t = _table_t(rng)
    return sql_item([t], "SELECT COUNT(*) FROM t;", count_star(t.rows), "COUNT(*) counts rows, NULLs or not.")


def _count_where_distinct(rng: random.Random):
    t = _table_t(rng)
    k = _k(rng)
    n = count_distinct([r[0] for r in where(t.rows, lambda r: gt(r[0], k))])
    return sql_item([t], f"SELECT COUNT(DISTINCT a) FROM t WHERE a > {k};", n, "First the rows with a > k are kept, then each different a is counted once.")


COUNT += [fit(_distinct_a), fit(_distinct_b), fit(_count_all), fit(_count_where_distinct)]


# ── 2. NULL Logic ───────────────────────────────────────────────────────

def _scalar(query: str, answer, why: str) -> Maker:
    """A table-free question: `SELECT <expression>;`."""
    def build(rng: random.Random):
        return sql_item([], query, answer, why)
    build.__name__ = "scalar_" + query[7:30]
    return fit(build)


def _scalar_k(make: Callable[[random.Random], tuple[str, object, str]]) -> Maker:
    def build(rng: random.Random):
        query, answer, why = make(rng)
        return sql_item([], query, answer, why)
    build.__name__ = make.__name__
    return fit(build)


def _n_eq(rng):
    return "SELECT NULL = NULL;", NULL, "Comparing NULL with anything, even NULL, is unknown: NULL."


def _n_is(rng):
    return "SELECT NULL IS NULL;", 1, "IS NULL is the real test: it is true (1)."


def _n_or_true(rng):
    return "SELECT NULL OR 1;", 1, "Unknown OR true is true: one true side is enough."


def _n_and_false(rng):
    return "SELECT NULL AND 0;", 0, "Unknown AND false is false: one false side is enough."


def _n_and_true(rng):
    return "SELECT NULL AND 1;", NULL, "Unknown AND true could be either: it stays unknown."


def _n_or_false(rng):
    return "SELECT NULL OR 0;", NULL, "Unknown OR false could be either: it stays unknown."


def _n_not(rng):
    return "SELECT NOT NULL;", NULL, "The opposite of unknown is unknown."


def _n_plus(rng):
    k = rng.randint(2, 9)
    return f"SELECT NULL + {k};", NULL, "Any arithmetic with NULL gives NULL."


def _n_concat(rng):
    w = words(rng, 1)[0]
    return f"SELECT NULL || '{w}';", NULL, "|| with a NULL is NULL, not the other text."


def _n_coalesce(rng):
    k = rng.randint(2, 9)
    return f"SELECT COALESCE(NULL, NULL, {k});", k, "COALESCE gives the first value that is not NULL."


def _n_ifnull(rng):
    w = words(rng, 1)[0]
    return f"SELECT IFNULL(NULL, '{w}');", w, "IFNULL(x, y) is y when x is NULL."


def _n_nullif_same(rng):
    k = rng.randint(2, 9)
    return f"SELECT NULLIF({k}, {k});", NULL, "NULLIF gives NULL when the two values are equal."


def _n_nullif_diff(rng):
    a, b = ints(rng, 2, 2, 9)
    return f"SELECT NULLIF({a}, {b});", a, "NULLIF gives the first value when they differ."


def _n_gt(rng):
    k = rng.randint(2, 9)
    return f"SELECT {k} > NULL;", NULL, "A comparison with NULL is unknown."


def _n_in_miss(rng):
    a, b = ints(rng, 2, 2, 9)
    return f"SELECT {a} IN ({b}, NULL);", NULL, "No match, but the NULL might have matched: unknown."


def _n_in_hit(rng):
    a = rng.randint(2, 9)
    return f"SELECT {a} IN ({a}, NULL);", 1, "A real match is enough: true."


def _n_not_in_null(rng):
    a, b = ints(rng, 2, 2, 9)
    return f"SELECT {a} NOT IN ({b}, NULL);", NULL, "NOT of unknown is unknown: NOT IN with a NULL in the list never says yes."


def _n_typeof(rng):
    return "SELECT typeof(NULL);", "null", "typeof(NULL) is the word null."


def _n_case(rng):
    return "SELECT CASE WHEN NULL THEN 'yes' ELSE 'no' END;", "no", "A NULL condition is not true, so the ELSE runs."


def _n_zero_eq(rng):
    return "SELECT 0 = NULL;", NULL, "Zero is not special: it is still unknown."


NULL_SCALARS = [_n_eq, _n_is, _n_or_true, _n_and_false, _n_and_true, _n_or_false, _n_not, _n_plus, _n_concat, _n_coalesce,
                _n_ifnull, _n_nullif_same, _n_nullif_diff, _n_gt, _n_in_miss, _n_in_hit, _n_not_in_null, _n_typeof, _n_case,
                _n_zero_eq]


def _nums_table(rng: random.Random, name: str = "t", n: int = 5, nulls: int = 1) -> Tbl:
    vals = with_nulls(rng, ints(rng, n, 1, 9), nulls)
    return Tbl(name, [("a", "INT")], [(v,) for v in vals])


def _null_count_diff(rng):
    t = _table_t(rng)
    return sql_item([t], "SELECT COUNT(*) - COUNT(b) FROM t;", count_star(t.rows) - count_col(t.col("b")), "COUNT(b) skips the NULLs, COUNT(*) does not: the difference is the number of NULLs.")


def _null_count_col(rng):
    t = _table_t(rng)
    return sql_item([t], "SELECT COUNT(a) FROM t;", count_col(t.col("a")), "COUNT(a) counts only the rows where a is not NULL.")


def _null_avg(rng):
    t = _nums_table(rng)
    return sql_item([t], "SELECT AVG(a) FROM t;", avg_(t.col("a")), "AVG ignores NULLs: it divides by the number of values, not rows. A real number, so it shows a decimal point.")


def _null_sum(rng):
    t = _nums_table(rng)
    return sql_item([t], "SELECT SUM(a) FROM t;", sum_(t.col("a")), "SUM skips the NULL.")


def _null_sum_empty(rng):
    t = _nums_table(rng)
    return sql_item([t], "SELECT SUM(a) FROM t WHERE a > 9;", NULL, "SUM of no rows is NULL, not 0.")


def _null_count_empty(rng):
    t = _nums_table(rng)
    return sql_item([t], "SELECT COUNT(a) FROM t WHERE a > 9;", 0, "COUNT of no rows is 0.")


def _null_sum_coalesce(rng):
    t = _nums_table(rng)
    return sql_item([t], "SELECT COALESCE(SUM(a), 0) FROM t WHERE a > 9;", 0, "SUM of nothing is NULL and COALESCE turns it into 0.")


def _null_total_empty(rng):
    t = _nums_table(rng)
    return sql_item([t], "SELECT TOTAL(a) FROM t WHERE a > 9;", 0.0, "TOTAL is SUM that gives 0.0 (a real) for no rows.")


def _null_avg_coalesce(rng):
    t = _nums_table(rng)
    vals = [0 if v is None else v for v in t.col("a")]
    return sql_item([t], "SELECT AVG(COALESCE(a, 0)) FROM t;", avg_(vals), "COALESCE turns the NULL into 0 first, so it now counts in the average.")


def _null_max(rng):
    t = _table_t(rng)
    return sql_item([t], "SELECT MAX(b) FROM t;", max_(t.col("b")), "MAX skips NULL and picks the last word in dictionary order.")


def _null_min(rng):
    t = _nums_table(rng)
    return sql_item([t], "SELECT MIN(a) FROM t;", min_(t.col("a")), "MIN skips NULL.")


def _null_max_of_nulls(rng):
    t = _nums_table(rng)
    return sql_item([t], "SELECT MAX(a) FROM t WHERE a IS NULL;", NULL, "MAX of only NULLs is NULL.")


def _null_where_null(rng):
    t = _nums_table(rng)
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE a = NULL;", 0, "a = NULL is never true.")


def _null_not_in_sub(rng):
    t = _nums_table(rng)
    u = Tbl("u", [("x", "INT")], [(v,) for v in ints(rng, 3, 1, 9)])
    hits = where(t.rows, lambda r: not_in(r[0], [x for (x,) in u.rows]))
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE a NOT IN (SELECT x FROM u);", count_star(hits), "u has no NULLs, so NOT IN works; but the NULL in t is unknown and left out.")


def _null_not_in_sub_null(rng):
    t = _nums_table(rng, nulls=0)
    xs = with_nulls(rng, ints(rng, 3, 1, 9))
    u = Tbl("u", [("x", "INT")], [(v,) for v in xs])
    n = count_star(where(t.rows, lambda r: not_in(r[0], xs)))
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE a NOT IN (SELECT x FROM u);", n, "u contains a NULL, so NOT IN is never true for a number that is not in u: it is unknown.")


def _null_arith_row(rng):
    t = Tbl("t", [("a", "INT"), ("b", "INT")], [(rng.randint(1, 9), None), (rng.randint(1, 9), rng.randint(1, 9))])
    return sql_item([t], "SELECT a + b FROM t LIMIT 1;", NULL, "The first row has a NULL b, so a + b is NULL.")


def _null_ifnull_row(rng):
    t = _table_t(rng)
    i = t.col("b").index(None)
    a = t.rows[i][0]
    if a is None or t.col("a").count(a) > 1:
        raise Retry
    return sql_item([t], f"SELECT IFNULL(b, 'none') FROM t WHERE a = {a};", "none", "The row with that a has no text: IFNULL gives the fallback.")


def _null_distinct_b(rng):
    t = _table_t(rng)
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT DISTINCT b FROM t);", len(set(t.col("b"))), "DISTINCT treats NULL as one value, so the NULL row counts as one row.")


def _null_group_nulls(rng):
    t = _table_t(rng)
    t = Tbl("t", t.cols, [(a, b) for a, b in t.rows])
    groups = group(t.rows, lambda r: r[1])
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT b FROM t GROUP BY b);", len(groups), "GROUP BY puts all the NULLs into one group of their own.")


def _null_case(rng):
    t = _nums_table(rng)
    k = rng.randint(3, 6)
    n = sum(1 for (a,) in t.rows if gt(a, k) is True)
    return sql_item([t], f"SELECT SUM(CASE WHEN a > {k} THEN 1 ELSE 0 END) FROM t;", n, "The CASE gives 0 for the NULL row (the condition is not true), so SUM counts only a > k.")


def _null_count_ratio(rng):
    t = _nums_table(rng, nulls=2)
    return sql_item([t], "SELECT COUNT(*) - COUNT(a) FROM t;", count_star(t.rows) - count_col(t.col("a")), "The number of rows where a is NULL.")


def _null_sum_plus(rng):
    t = _nums_table(rng)
    k = rng.randint(2, 9)
    return sql_item([t], f"SELECT SUM(a) + {k} FROM t WHERE a > 9;", NULL, "SUM of nothing is NULL, and NULL + k is NULL.")


NULLS: list[Maker] = ([_scalar_k(f) for f in NULL_SCALARS] + [fit(f) for f in (
    _null_count_diff, _null_count_col, _null_avg, _null_sum, _null_sum_empty, _null_count_empty, _null_sum_coalesce,
    _null_total_empty, _null_avg_coalesce, _null_max, _null_min, _null_max_of_nulls, _null_where_null, _null_not_in_sub,
    _null_not_in_sub_null, _null_arith_row, _null_ifnull_row, _null_distinct_b, _null_group_nulls, _null_case,
    _null_count_ratio, _null_sum_plus)])


# ── 3. Group Result ─────────────────────────────────────────────────────

def _orders(rng: random.Random, n: int = 6) -> Tbl:
    """o(who TEXT, amt INT): three customers, amounts that make the groups' totals all different."""
    for _ in range(100):
        names = words(rng, 3)
        rows = [(rng.choice(names), rng.randint(1, 9)) for _ in range(n)]
        if len({r[0] for r in rows}) == 3:
            return Tbl("o", [("who", "TEXT"), ("amt", "INT")], rows)
    raise Retry


def _groups(t: Tbl) -> dict:
    return group(t.rows, lambda r: r[0])


def _unique_top(values: list[tuple]) -> None:
    """Retry unless the biggest of the (key, value) pairs is alone."""
    best = max(v for _, v in values)
    if sum(1 for _, v in values if v == best) != 1:
        raise Retry


def _g_top_count(rng):
    t = _orders(rng)
    g = {k: len(v) for k, v in _groups(t).items()}
    _unique_top(list(g.items()))
    return sql_item([t], "SELECT COUNT(*) FROM o GROUP BY who ORDER BY COUNT(*) DESC LIMIT 1;", max(g.values()), "Each customer is a group; the biggest group's row count comes first.")


def _g_top_name(rng):
    t = _orders(rng)
    g = {k: sum_([r[1] for r in v]) for k, v in _groups(t).items()}
    _unique_top(list(g.items()))
    top = max(g, key=g.get)
    return sql_item([t], "SELECT who FROM o GROUP BY who ORDER BY SUM(amt) DESC LIMIT 1;", top, "The groups are ordered by their totals, biggest first: the first one's name.")


def _g_top_sum(rng):
    t = _orders(rng)
    g = {k: sum_([r[1] for r in v]) for k, v in _groups(t).items()}
    return sql_item([t], "SELECT MAX(s) FROM (SELECT SUM(amt) AS s FROM o GROUP BY who);", max(g.values()), "The inner query gives one total per customer; MAX picks the biggest.")


def _g_having_count(rng):
    t = _orders(rng)
    k = rng.randint(1, 2)
    n = sum(1 for v in _groups(t).values() if len(v) > k)
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT who FROM o GROUP BY who HAVING COUNT(*) > {k});", n, "HAVING keeps the groups with more than k rows; the outer query counts them.")


def _g_having_sum(rng):
    t = _orders(rng)
    k = rng.randint(6, 12)
    n = sum(1 for v in _groups(t).values() if sum_([r[1] for r in v]) > k)
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT who FROM o GROUP BY who HAVING SUM(amt) > {k});", n, "HAVING tests each group's total; the outer query counts the groups that pass.")


def _g_one_group_sum(rng):
    t = _orders(rng)
    who = rng.choice(list(_groups(t)))
    s = sum_([r[1] for r in _groups(t)[who]])
    return sql_item([t], f"SELECT SUM(amt) FROM o GROUP BY who HAVING who = {lit(who)};", s, "HAVING who = x keeps one group; its total is the answer.")


def _g_one_group_count(rng):
    t = _orders(rng)
    who = rng.choice(list(_groups(t)))
    return sql_item([t], f"SELECT COUNT(*) FROM o WHERE who = {lit(who)};", len(_groups(t)[who]), "One customer's rows.")


def _g_where_then_group(rng):
    t = _orders(rng)
    k = rng.randint(3, 6)
    g = group(where(t.rows, lambda r: gt(r[1], k)), lambda r: r[0])
    if not g:
        raise Retry
    counts = {key: len(v) for key, v in g.items()}
    _unique_top(list(counts.items()))
    return sql_item([t], f"SELECT COUNT(*) FROM o WHERE amt > {k} GROUP BY who ORDER BY COUNT(*) DESC LIMIT 1;", max(counts.values()), "WHERE removes rows BEFORE they are grouped, so the groups are smaller.")


def _g_number_of_groups(rng):
    t = _orders(rng)
    return sql_item([t], "SELECT COUNT(DISTINCT who) FROM o;", len(_groups(t)), "One group per different customer.")


def _g_min_per_group(rng):
    t = _orders(rng)
    who = rng.choice(list(_groups(t)))
    m = min_([r[1] for r in _groups(t)[who]])
    return sql_item([t], f"SELECT MIN(amt) FROM o GROUP BY who HAVING who = {lit(who)};", m, "The smallest amount inside that one group.")


def _g_max_per_group(rng):
    t = _orders(rng)
    who = rng.choice(list(_groups(t)))
    m = max_([r[1] for r in _groups(t)[who]])
    return sql_item([t], f"SELECT MAX(amt) FROM o WHERE who = {lit(who)};", m, "The biggest amount of that customer.")


def _g_sum_of_counts(rng):
    t = _orders(rng)
    k = rng.randint(1, 2)
    s = sum_([len(v) for v in _groups(t).values() if len(v) > k])
    if s is None:
        raise Retry
    return sql_item([t], f"SELECT SUM(c) FROM (SELECT COUNT(*) AS c FROM o GROUP BY who HAVING c > {k});", s, "The groups with more than k rows, and the sum of their sizes.")


def _g_avg_group(rng):
    t = _orders(rng)
    who = rng.choice(list(_groups(t)))
    vals = [r[1] for r in _groups(t)[who]]
    return sql_item([t], f"SELECT AVG(amt) FROM o WHERE who = {lit(who)};", avg_(vals), "The average of that customer's amounts: a real number, so it shows a decimal point.")


def _g_smallest_group(rng):
    t = _orders(rng)
    g = {k: len(v) for k, v in _groups(t).items()}
    low = min(g.values())
    if list(g.values()).count(low) != 1:
        raise Retry
    return sql_item([t], "SELECT MIN(c) FROM (SELECT COUNT(*) AS c FROM o GROUP BY who);", low, "One count per customer; MIN picks the smallest.")


def _g_second(rng):
    t = _orders(rng)
    g = {k: sum_([r[1] for r in v]) for k, v in _groups(t).items()}
    if len(set(g.values())) != 3:
        raise Retry
    second = sorted(g.values())[1]
    return sql_item([t], "SELECT SUM(amt) FROM o GROUP BY who ORDER BY SUM(amt) LIMIT 1 OFFSET 1;", second, "The totals in rising order; OFFSET 1 skips the smallest and LIMIT 1 takes the next.")


def _g_having_who(rng):
    t = _orders(rng)
    g = _groups(t)
    k = rng.randint(2, 3)
    names = sorted(w for w, v in g.items() if len(v) >= k)
    if len(names) != 1:
        raise Retry
    return sql_item([t], f"SELECT who FROM o GROUP BY who HAVING COUNT(*) >= {k};", names[0], "Only one customer has k or more rows.")


def _g_group_total_all(rng):
    t = _orders(rng)
    return sql_item([t], "SELECT SUM(s) FROM (SELECT SUM(amt) AS s FROM o GROUP BY who);", sum_(t.col("amt")), "The group totals add back up to the grand total.")


def _g_two_keys(rng):
    names = words(rng, 2)
    rows = [(rng.choice(names), rng.choice("xy"), rng.randint(1, 9)) for _ in range(6)]
    t = Tbl("o", [("who", "TEXT"), ("k", "TEXT"), ("amt", "INT")], rows)
    n = len(group(rows, lambda r: (r[0], r[1])))
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT who, k FROM o GROUP BY who, k);", n, "One group for each different pair of who and k.")


def _g_count_distinct_in_group(rng):
    t = _orders(rng)
    who = rng.choice(list(_groups(t)))
    n = len({r[1] for r in _groups(t)[who]})
    return sql_item([t], f"SELECT COUNT(DISTINCT amt) FROM o WHERE who = {lit(who)};", n, "How many different amounts that customer has.")


def _g_null_group(rng):
    t = _orders(rng)
    rows = list(t.rows)
    rows[rng.randrange(len(rows))] = (None, rng.randint(1, 9))
    t = Tbl("o", t.cols, rows)
    g = group(rows, lambda r: r[0])
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT who FROM o GROUP BY who);", len(g), "NULL is a group too, so it counts as one more.")


def _g_having_avg(rng):
    t = _orders(rng)
    k = rng.randint(3, 6)
    n = sum(1 for v in _groups(t).values() if avg_([r[1] for r in v]) > k)
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT who FROM o GROUP BY who HAVING AVG(amt) > {k});", n, "HAVING can test any aggregate: here the average of each group.")


def _g_max_count_rows(rng):
    t = _orders(rng)
    g = {k: len(v) for k, v in _groups(t).items()}
    return sql_item([t], "SELECT MAX(c) FROM (SELECT COUNT(*) AS c FROM o GROUP BY who);", max(g.values()), "The size of the biggest group.")


def _g_range(rng):
    t = _orders(rng)
    who = rng.choice(list(_groups(t)))
    vals = [r[1] for r in _groups(t)[who]]
    return sql_item([t], f"SELECT MAX(amt) - MIN(amt) FROM o WHERE who = {lit(who)};", max(vals) - min(vals), "The spread of that customer's amounts.")


def _g_where_count_groups(rng):
    t = _orders(rng)
    k = rng.randint(3, 7)
    n = len(group(where(t.rows, lambda r: gt(r[1], k)), lambda r: r[0]))
    if n == 0:
        raise Retry
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT who FROM o WHERE amt > {k} GROUP BY who);", n, "How many customers have at least one amount above k.")


def _g_sum_filtered_group(rng):
    t = _orders(rng)
    who = rng.choice(list(_groups(t)))
    k = rng.randint(2, 5)
    s = sum_([r[1] for r in _groups(t)[who] if r[1] > k])
    if s is None:
        raise Retry
    return sql_item([t], f"SELECT SUM(amt) FROM o WHERE who = {lit(who)} AND amt > {k};", s, "Only that customer's amounts above k are added.")


def _g_count_vs_sum(rng):
    t = _orders(rng)
    who = rng.choice(list(_groups(t)))
    rows = _groups(t)[who]
    return sql_item([t], f"SELECT SUM(amt) - COUNT(*) FROM o WHERE who = {lit(who)};", sum_([r[1] for r in rows]) - len(rows), "The total minus the number of rows.")


GROUPS: list[Maker] = [fit(f) for f in (
    _g_top_count, _g_top_name, _g_top_sum, _g_having_count, _g_having_sum, _g_one_group_sum, _g_one_group_count,
    _g_where_then_group, _g_number_of_groups, _g_min_per_group, _g_max_per_group, _g_sum_of_counts, _g_avg_group,
    _g_smallest_group, _g_second, _g_having_who, _g_group_total_all, _g_two_keys, _g_count_distinct_in_group, _g_null_group,
    _g_having_avg, _g_max_count_rows, _g_range, _g_where_count_groups, _g_sum_filtered_group, _g_count_vs_sum)]


def _g_sum_of_big_groups(rng):
    t = _orders(rng)
    big = [w for w, v in _groups(t).items() if len(v) > 1]
    if not big:
        raise Retry
    s = sum_([r[1] for r in t.rows if r[0] in big])
    return sql_item([t], "SELECT SUM(amt) FROM o WHERE who IN (SELECT who FROM o GROUP BY who HAVING COUNT(*) > 1);", s, "The subquery finds the customers with more than one row; their amounts are added.")


def _g_order_min(rng):
    t = _orders(rng)
    g = {k: min_([r[1] for r in v]) for k, v in _groups(t).items()}
    if list(g.values()).count(min(g.values())) != 1:
        raise Retry
    return sql_item([t], "SELECT who FROM o GROUP BY who ORDER BY MIN(amt) LIMIT 1;", min(g, key=g.get), "The groups are ordered by their smallest amount: the first one's name.")


def _g_order_max_tie(rng):
    t = _orders(rng)
    g = {k: max_([r[1] for r in v]) for k, v in _groups(t).items()}
    best = sorted(g, key=lambda k: (-g[k], k))[0]
    return sql_item([t], "SELECT who FROM o GROUP BY who ORDER BY MAX(amt) DESC, who LIMIT 1;", best, "Biggest maximum first; a tie is broken by name in dictionary order.")


def _g_above_avg(rng):
    t = _orders(rng)
    avg = avg_(t.col("amt"))
    return sql_item([t], "SELECT COUNT(*) FROM o WHERE amt > (SELECT AVG(amt) FROM o);", sum(1 for _, a in t.rows if a > avg), "The subquery gives the average of all amounts; the rows above it are counted.")


def _g_two_columns(rng):
    t = _orders(rng)
    g = {k: len(v) for k, v in _groups(t).items()}
    _unique_top(list(g.items()))
    top = max(g, key=g.get)
    return sql_item([t], "SELECT who, COUNT(*) FROM o GROUP BY who ORDER BY 2 DESC LIMIT 1;", [(top, g[top])], "ORDER BY 2 sorts by the second column. Two columns print with a | between them.")


def _g_first_name_sum(rng):
    t = _orders(rng)
    g = _groups(t)
    first = sorted(g)[0]
    return sql_item([t], "SELECT SUM(amt) FROM o GROUP BY who ORDER BY who LIMIT 1;", sum_([r[1] for r in g[first]]), "The groups are in dictionary order of the name: the first group's total.")


def _g_subquery_where(rng):
    t = _orders(rng)
    k = rng.randint(6, 12)
    n = sum(1 for v in _groups(t).values() if sum_([r[1] for r in v]) > k)
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT who, SUM(amt) AS s FROM o GROUP BY who) WHERE s > {k};", n, "The subquery makes one row per customer with its total; the outer WHERE filters those rows.")


def _g_smallest_max(rng):
    t = _orders(rng)
    g = {k: max_([r[1] for r in v]) for k, v in _groups(t).items()}
    return sql_item([t], "SELECT MAX(amt) FROM o GROUP BY who ORDER BY MAX(amt) LIMIT 1;", min(g.values()), "One maximum per customer, in rising order: the first is the smallest of them.")


def _g_having_min(rng):
    t = _orders(rng)
    k = rng.randint(2, 5)
    n = sum(1 for v in _groups(t).values() if min_([r[1] for r in v]) > k)
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT who FROM o GROUP BY who HAVING MIN(amt) > {k});", n, "MIN(amt) > k means every amount in the group is above k.")


def _g_having_two(rng):
    t = _orders(rng)
    k = rng.randint(4, 7)
    n = sum(1 for v in _groups(t).values() if max_([r[1] for r in v]) > k and len(v) > 1)
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT who FROM o GROUP BY who HAVING MAX(amt) > {k} AND COUNT(*) > 1);", n, "HAVING may combine tests: a big maximum and more than one row.")


def _g_avg_of_counts(rng):
    t = _orders(rng)
    counts = [len(v) for v in _groups(t).values()]
    return sql_item([t], "SELECT AVG(c) FROM (SELECT COUNT(*) AS c FROM o GROUP BY who);", avg_(counts), "The group sizes average out to the rows divided by the groups: a real number.")


def _g_distinct_pairs(rng):
    t = _orders(rng)
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT DISTINCT who, amt FROM o);", len(set(t.rows)), "Each different pair of who and amt counts once.")


def _g_sum_of_squares(rng):
    t = _orders(rng)
    return sql_item([t], "SELECT SUM(c * c) FROM (SELECT COUNT(*) AS c FROM o GROUP BY who);", sum(len(v) ** 2 for v in _groups(t).values()), "One count per customer, squared, then added.")


def _g_having_equal_count(rng):
    t = _orders(rng)
    k = rng.randint(1, 3)
    hits = [v for v in _groups(t).values() if len(v) == k]
    if len(hits) != 1:
        raise Retry
    return sql_item([t], f"SELECT SUM(amt) FROM o GROUP BY who HAVING COUNT(*) = {k};", sum_([r[1] for r in hits[0]]), "Only one customer has exactly k rows: its total.")


def _g_min_total(rng):
    t = _orders(rng)
    totals = [sum_([r[1] for r in v]) for v in _groups(t).values()]
    return sql_item([t], "SELECT MIN(s) FROM (SELECT SUM(amt) AS s FROM o GROUP BY who);", min(totals), "One total per customer; MIN picks the smallest.")


GROUPS += [fit(f) for f in (
    _g_sum_of_big_groups, _g_order_min, _g_order_max_tie, _g_above_avg, _g_two_columns, _g_first_name_sum, _g_subquery_where,
    _g_smallest_max, _g_having_min, _g_having_two, _g_avg_of_counts, _g_distinct_pairs, _g_sum_of_squares,
    _g_having_equal_count, _g_min_total)]
