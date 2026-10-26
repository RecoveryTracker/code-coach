"""SQL deeper queries, part 1: Aggregate Mix.

COUNT(DISTINCT), SUM / AVG / MIN / MAX with NULLs and mixed filters (CASE inside an aggregate, `FILTER (WHERE ...)`),
GROUP_CONCAT in a fixed order or measured by its length, and aggregates of aggregates. Every answer is worked out by hand with
`_sql_model.py`; tests/sql_oracle.py then holds each script to a fresh in-memory SQLite.
"""

from __future__ import annotations

import random
from typing import Callable

from ._model import Maker, tdiv
from ._sql_model import (NULL, Retry, Tbl, avg_, count_col, count_distinct, fit, max_, min_, sql_div, sql_item, sql_round,
                         sum_, total_, with_nulls)

AGG: list[Maker] = []


def reg(f: Callable) -> Callable:
    """Register a template (wrapped by fit) in the Aggregate Mix pool."""
    AGG.append(fit(f))
    return f


def _vals(rng: random.Random, n: int = 6, lo: int = 1, hi: int = 9, dup: bool = True) -> list[int]:
    """n numbers; with `dup` at least one value is repeated, without it every value is different."""
    if not dup:
        return rng.sample(range(lo, hi + 1), n)
    v = rng.sample(range(lo, hi + 1), n - 2)
    v += [rng.choice(v), rng.choice(v)]
    rng.shuffle(v)
    return v


def _t(rng: random.Random, n: int = 6, nulls: int = 0, dup: bool = True, groups: str = "xyz") -> Tbl:
    """t(g TEXT, a INT): a group letter and a number, with `nulls` NULL numbers."""
    a = _vals(rng, n, dup=dup)
    if nulls:
        a = with_nulls(rng, a, nulls)
    g = [rng.choice(groups) for _ in range(n)]
    if len(set(g)) < 2:
        raise Retry
    return Tbl("t", [("g", "TEXT"), ("a", "INT")], list(zip(g, a)))


def _w(rng: random.Random, n: int = 6, nulls: int = 0) -> Tbl:
    """t(w TEXT): words (some repeated), `nulls` of them NULL."""
    pool = ["fig", "plum", "pear", "lime", "date", "kiwi", "apple", "grape", "melon", "peach", "mango", "berry"]
    w = rng.sample(pool, n - 1)
    w.append(rng.choice(w))
    rng.shuffle(w)
    if nulls:
        w = with_nulls(rng, w, nulls)
    return Tbl("t", [("w", "TEXT")], [(x,) for x in w])


def A(t: Tbl) -> list:
    return t.col("a")


def G(t: Tbl) -> list:
    return t.col("g")


# ── COUNT(DISTINCT ...) ─────────────────────────────────────────────────

@reg
def distinct_count(rng):
    t = _t(rng)
    return sql_item([t], "SELECT COUNT(DISTINCT a) FROM t;", count_distinct(A(t)), "DISTINCT counts each different value once: repeats add nothing.")


@reg
def distinct_null(rng):
    t = _t(rng, nulls=1)
    return sql_item([t], "SELECT COUNT(DISTINCT a) FROM t;", count_distinct(A(t)), "NULL is skipped by COUNT(col), so it is not counted as a value, distinct or not.")


@reg
def dup_surplus(rng):
    t = _t(rng)
    return sql_item([t], "SELECT COUNT(a) - COUNT(DISTINCT a) FROM t;", count_col(A(t)) - count_distinct(A(t)), "All the values minus the different values: how many repeats there are.")


@reg
def distinct_where(rng):
    t = _t(rng, n=7)
    k = rng.randint(3, 6)
    n = count_distinct([g for g, a in t.rows if a is not None and a > k])
    return sql_item([t], f"SELECT COUNT(DISTINCT g) FROM t WHERE a > {k};", n, "WHERE filters the rows first; then the different letters among them are counted.")


@reg
def distinct_case(rng):
    t = _t(rng, n=7)
    k = rng.randint(3, 6)
    n = count_distinct([g if a > k else None for g, a in t.rows])
    return sql_item([t], f"SELECT COUNT(DISTINCT CASE WHEN a > {k} THEN g END) FROM t;", n, "CASE gives NULL for the other rows, and COUNT skips NULL: only the big rows' letters are counted.")


@reg
def distinct_lower(rng):
    pool = ["Fig", "fig", "FIG", "Plum", "plum", "Pear", "pear", "PEAR", "Lime", "lime"]
    w = rng.sample(pool, 6)
    t = Tbl("t", [("w", "TEXT")], [(x,) for x in w])
    n = count_distinct([x.lower() for x in w])
    return sql_item([t], "SELECT COUNT(DISTINCT LOWER(w)) FROM t;", n, "DISTINCT works on the value after LOWER: Fig and fig become one word.")


@reg
def distinct_exact_case(rng):
    pool = ["Fig", "fig", "FIG", "Plum", "plum", "Pear", "pear", "PEAR", "Lime", "lime"]
    w = rng.sample(pool, 6)
    t = Tbl("t", [("w", "TEXT")], [(x,) for x in w])
    return sql_item([t], "SELECT COUNT(DISTINCT w) FROM t;", len(set(w)), "Without LOWER, text is compared exactly: Fig and fig are different values.")


@reg
def distinct_first_letter(rng):
    t = _w(rng)
    n = count_distinct([w[0] for (w,) in t.rows])
    return sql_item([t], "SELECT COUNT(DISTINCT SUBSTR(w, 1, 1)) FROM t;", n, "The first letters, each different letter once.")


@reg
def distinct_pairs(rng):
    t = _t(rng, groups="xy")
    n = len(set(t.rows))
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT DISTINCT g, a FROM t);", n, "DISTINCT on two columns removes a repeated PAIR, not repeated single values.")


@reg
def distinct_concat(rng):
    t = _t(rng, groups="xy", nulls=1)
    n = len({(g, a) for g, a in t.rows if a is not None})
    return sql_item([t], "SELECT COUNT(DISTINCT g || a) FROM t;", n, "g || a is NULL when a is NULL, so that row is skipped; the rest count by different pair.")


@reg
def all_unique(rng):
    dup = rng.random() < 0.5
    t = _t(rng, dup=dup)
    return sql_item([t], "SELECT COUNT(DISTINCT a) = COUNT(*) FROM t;", int(count_distinct(A(t)) == len(t.rows)), "The comparison gives 1 when no value repeats and 0 when one does.")


@reg
def having_distinct(rng):
    t = _t(rng, n=7, groups="xy")
    gs = {}
    for g, a in t.rows:
        gs.setdefault(g, set()).add(a)
    n = sum(1 for s in gs.values() if len(s) > 1)
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT g FROM t GROUP BY g HAVING COUNT(DISTINCT a) > 1);", n, "A letter qualifies only if its rows hold more than one different number.")


# ── SUM / AVG / MIN / MAX, with NULLs and filters ──────────────────────

@reg
def sum_distinct(rng):
    t = _t(rng)
    return sql_item([t], "SELECT SUM(DISTINCT a) FROM t;", sum(set(A(t))), "Each different value is added once.")


@reg
def sum_minus_distinct(rng):
    t = _t(rng)
    return sql_item([t], "SELECT SUM(a) - SUM(DISTINCT a) FROM t;", sum(A(t)) - sum(set(A(t))), "What is left over is the repeated copies, added up.")


@reg
def avg_distinct(rng):
    t = _t(rng)
    s = set(A(t))
    return sql_item([t], "SELECT ROUND(AVG(DISTINCT a), 2) FROM t;", sql_round(sum(s) / len(s), 2), "The average of the different values; ROUND gives a real with two decimals.")


@reg
def avg_skip_null(rng):
    t = _t(rng, nulls=1)
    return sql_item([t], "SELECT ROUND(AVG(a), 2) FROM t;", sql_round(avg_(A(t)), 2), "AVG divides by the number of non-NULL values, not the number of rows.")


@reg
def avg_null_as_zero(rng):
    t = _t(rng, nulls=1)
    v = [0 if a is None else a for a in A(t)]
    return sql_item([t], "SELECT ROUND(AVG(COALESCE(a, 0)), 2) FROM t;", sql_round(sum(v) / len(v), 2), "COALESCE turns the NULL into 0 first, so now it counts in the average.")


@reg
def avg_exact(rng):
    n = 5
    v = _vals(rng, n, 1, 9, dup=False)
    if sum(v) % n:
        raise Retry
    t = Tbl("t", [("a", "INT")], [(x,) for x in v])
    return sql_item([t], "SELECT AVG(a) FROM t;", sum(v) / n, "AVG always gives a real, even when the average is a whole number.")


@reg
def count_minus_count(rng):
    t = _t(rng, nulls=2)
    return sql_item([t], "SELECT COUNT(*) - COUNT(a) FROM t;", len(t.rows) - count_col(A(t)), "COUNT(*) counts rows, COUNT(a) skips NULLs: the difference is the NULLs.")


@reg
def sum_case_count(rng):
    t = _t(rng, nulls=1)
    k = rng.randint(3, 6)
    n = sum(1 for a in A(t) if a is not None and a > k)
    return sql_item([t], f"SELECT SUM(CASE WHEN a > {k} THEN 1 ELSE 0 END) FROM t;", n, "Each row adds 1 or 0; a NULL a is not above k, so it adds 0.")


@reg
def sum_case_value(rng):
    t = _t(rng, nulls=1)
    n = sum(a for g, a in t.rows if g == "x" and a is not None)
    if not any(g == "x" for g in G(t)):
        raise Retry
    return sql_item([t], "SELECT SUM(CASE WHEN g = 'x' THEN a ELSE 0 END) FROM t;", n, "Only the x rows add their a; a NULL a adds nothing at all.")


@reg
def sum_bool(rng):
    t = _t(rng)
    k = rng.randint(3, 6)
    return sql_item([t], f"SELECT SUM(a > {k}) FROM t;", sum(1 for a in A(t) if a > k), "A comparison is 1 or 0, so SUM counts the rows where it is true.")


@reg
def sum_iif_even(rng):
    t = _t(rng)
    return sql_item([t], "SELECT SUM(IIF(a % 2 = 0, a, 0)) FROM t;", sum(a for a in A(t) if a % 2 == 0), "IIF picks a for the even rows and 0 for the odd, so SUM adds only the even ones.")


@reg
def count_filter(rng):
    t = _t(rng, nulls=1)
    k = rng.randint(3, 6)
    n = sum(1 for a in A(t) if a is not None and a > k)
    return sql_item([t], f"SELECT COUNT(*) FILTER (WHERE a > {k}) FROM t;", n, "FILTER (WHERE ...) lets only the rows where the test is true into that one aggregate.")


@reg
def sum_filter(rng):
    t = _t(rng, nulls=1)
    n = [a for g, a in t.rows if g == "x"]
    if not n:
        raise Retry
    return sql_item([t], "SELECT SUM(a) FILTER (WHERE g = 'x') FROM t;", sum_(n), "Only the x rows are added; a NULL among them is skipped.")


@reg
def max_filter(rng):
    t = _t(rng)
    n = [a for g, a in t.rows if g == "y"]
    if not n:
        raise Retry
    return sql_item([t], "SELECT MAX(a) FILTER (WHERE g = 'y') FROM t;", max(n), "The biggest a among the y rows only.")


@reg
def min_filter_first(rng):
    t = _t(rng)
    n = [a for g, a in t.rows if g == "x"]
    if not n:
        raise Retry
    return sql_item([t], "SELECT MIN(a) FILTER (WHERE g = 'x') FROM t;", min(n), "The smallest a among the x rows only.")


@reg
def min_filter_none(rng):
    t = _t(rng)
    return sql_item([t], "SELECT MIN(a) FILTER (WHERE a > 99) FROM t;", NULL, "No row passes the filter, and MIN of nothing is NULL.")


@reg
def total_filter_none(rng):
    t = _t(rng)
    return sql_item([t], "SELECT TOTAL(a) FILTER (WHERE a > 99) FROM t;", total_([]), "TOTAL of nothing is 0.0 (a real), where SUM of nothing would be NULL.")


@reg
def sum_filter_none(rng):
    t = _t(rng)
    return sql_item([t], "SELECT SUM(a) FILTER (WHERE a > 99) FROM t;", NULL, "SUM of no rows is NULL, not 0.")


@reg
def count_col_filter(rng):
    t = _t(rng, nulls=2)
    n = sum(1 for g, a in t.rows if g == "x" and a is not None)
    if not any(g == "x" for g in G(t)):
        raise Retry
    return sql_item([t], "SELECT COUNT(a) FILTER (WHERE g = 'x') FROM t;", n, "Among the x rows, only the ones whose a is not NULL are counted.")


@reg
def min_case(rng):
    t = _t(rng)
    n = [a for g, a in t.rows if g == "x"]
    if not n:
        raise Retry
    return sql_item([t], "SELECT MIN(CASE WHEN g = 'x' THEN a END) FROM t;", min(n), "CASE with no ELSE gives NULL for the other rows, and MIN ignores NULL.")


@reg
def value_range(rng):
    t = _t(rng, nulls=1)
    return sql_item([t], "SELECT MAX(a) - MIN(a) FROM t;", max_(A(t)) - min_(A(t)), "The spread between the biggest and smallest value; NULL is ignored by both.")


@reg
def sum_all_null(rng):
    t = _t(rng, nulls=0)
    rows = [(g, None if g == "z" else a) for g, a in t.rows]
    if not any(g == "z" for g, _ in rows):
        raise Retry
    t = Tbl("t", t.cols, rows)
    return sql_item([t], "SELECT SUM(a) FROM t WHERE g = 'z';", NULL, "Every a in the z rows is NULL, so SUM has no values to add and gives NULL.")


@reg
def total_all_null(rng):
    t = _t(rng, nulls=0)
    rows = [(g, None if g == "z" else a) for g, a in t.rows]
    if not any(g == "z" for g, _ in rows):
        raise Retry
    t = Tbl("t", t.cols, rows)
    return sql_item([t], "SELECT TOTAL(a) FROM t WHERE g = 'z';", 0.0, "TOTAL never gives NULL: with nothing to add it is 0.0.")


@reg
def sum_product(rng):
    a, b = _vals(rng, 5, dup=False), _vals(rng, 5, dup=False)
    b = with_nulls(rng, b, 1)
    t = Tbl("t", [("a", "INT"), ("b", "INT")], list(zip(a, b)))
    return sql_item([t], "SELECT SUM(a * b) FROM t;", sum(x * y for x, y in t.rows if y is not None), "a * b is NULL on the row where b is NULL, and SUM skips it.")


@reg
def sum_int_div(rng):
    t = _t(rng, nulls=1)
    return sql_item([t], "SELECT SUM(a) / COUNT(*) FROM t;", sql_div(sum_(A(t)), len(t.rows)), "Two integers divide as integers; COUNT(*) counts the NULL row too.")


@reg
def sum_real_div(rng):
    t = _t(rng, n=7)
    return sql_item([t], "SELECT ROUND(SUM(a) * 1.0 / COUNT(*), 2) FROM t;", sql_round(sum(A(t)) * 1.0 / len(t.rows), 2), "Multiplying by 1.0 makes the division a real one.")


@reg
def sum_minus_max(rng):
    t = _t(rng)
    return sql_item([t], "SELECT SUM(a) - MAX(a) FROM t;", sum(A(t)) - max(A(t)), "Everything except the biggest value (counted once).")


@reg
def min_max_text(rng):
    t = _t(rng)
    return sql_item([t], "SELECT MIN(a) || '-' || MAX(a) FROM t;", f"{min(A(t))}-{max(A(t))}", "|| joins the two numbers as text with a dash between.")


@reg
def count_nullif(rng):
    t = _t(rng, nulls=1)
    vals = [a for a in A(t) if a is not None]
    k = rng.choice(vals)
    n = sum(1 for a in vals if a != k)
    return sql_item([t], f"SELECT COUNT(NULLIF(a, {k})) FROM t;", n, "NULLIF turns the value k into NULL, and COUNT skips NULL: the rows that are not k are left.")


# ── Text aggregates ─────────────────────────────────────────────────────

@reg
def max_text(rng):
    t = _w(rng)
    return sql_item([t], "SELECT MAX(w) FROM t;", max(w for (w,) in t.rows), "MAX of text is the one that sorts last alphabetically.")


@reg
def min_text(rng):
    t = _w(rng)
    return sql_item([t], "SELECT MIN(w) FROM t;", min(w for (w,) in t.rows), "MIN of text is the one that sorts first alphabetically.")


@reg
def max_length(rng):
    t = _w(rng)
    return sql_item([t], "SELECT MAX(LENGTH(w)) FROM t;", max(len(w) for (w,) in t.rows), "The length of each word first, then the biggest of those.")


@reg
def sum_length(rng):
    t = _w(rng, nulls=1)
    return sql_item([t], "SELECT SUM(LENGTH(w)) FROM t;", sum(len(w) for (w,) in t.rows if w is not None), "LENGTH of NULL is NULL, so that row adds nothing.")


@reg
def concat_length(rng):
    t = _w(rng, nulls=1)
    ws = [w for (w,) in t.rows if w is not None]
    return sql_item([t], "SELECT LENGTH(GROUP_CONCAT(w)) FROM t;", sum(map(len, ws)) + len(ws) - 1, "GROUP_CONCAT joins the non-NULL words with a comma: the letters plus one comma between each pair.")


@reg
def concat_distinct_length(rng):
    t = _w(rng)
    ws = {w for (w,) in t.rows}
    return sql_item([t], "SELECT LENGTH(GROUP_CONCAT(DISTINCT w)) FROM t;", sum(map(len, ws)) + len(ws) - 1, "Each different word once, joined by commas: count the letters and the commas.")


@reg
def concat_ordered(rng):
    t = _w(rng, n=5, nulls=1)
    ws = sorted(w for (w,) in t.rows if w is not None)
    return sql_item([t], "SELECT GROUP_CONCAT(w, '-' ORDER BY w) FROM t;", "-".join(ws), "ORDER BY inside the aggregate fixes the order of the joined words; the NULL is skipped.")


@reg
def concat_numbers(rng):
    t = _t(rng, n=5)
    v = sorted((a for a in A(t)), reverse=True)
    return sql_item([t], "SELECT GROUP_CONCAT(a, '+' ORDER BY a DESC) FROM t;", "+".join(map(str, v)), "The numbers joined as text with a plus between, biggest first.")


@reg
def concat_filter(rng):
    t = _t(rng, n=6)
    k = rng.randint(3, 6)
    v = sorted(a for a in A(t) if a > k)
    if not v:
        raise Retry
    return sql_item([t], f"SELECT LENGTH(GROUP_CONCAT(a, '') FILTER (WHERE a > {k})) FROM t;", len(v), "One character per big number, glued together with nothing between them.")


# ── Aggregates of aggregates ────────────────────────────────────────────

@reg
def spread_of_counts(rng):
    t = _t(rng, n=7)
    counts = {}
    for g in G(t):
        counts[g] = counts.get(g, 0) + 1
    return sql_item([t], "SELECT MAX(c) - MIN(c) FROM (SELECT COUNT(*) c FROM t GROUP BY g);", max(counts.values()) - min(counts.values()), "The inner query gives one count per letter; the outer finds the gap between the biggest and smallest.")


@reg
def mean_of_sums(rng):
    t = _t(rng, n=7)
    sums = {}
    for g, a in t.rows:
        sums[g] = sums.get(g, 0) + a
    return sql_item([t], "SELECT SUM(s) / COUNT(*) FROM (SELECT SUM(a) s FROM t GROUP BY g);", tdiv(sum(sums.values()), len(sums)), "Integer average of the per-letter totals (it divides by the number of letters).")


@reg
def distinct_group_sums(rng):
    t = _t(rng, n=7)
    sums = {}
    for g, a in t.rows:
        sums[g] = sums.get(g, 0) + a
    return sql_item([t], "SELECT COUNT(DISTINCT s) FROM (SELECT SUM(a) s FROM t GROUP BY g);", len(set(sums.values())), "Two letters with the same total count as one distinct total.")
