"""SQL deeper queries, part 2: Set Operation.

UNION, UNION ALL, INTERSECT and EXCEPT over small one- and two-column tables: counts, sums and the first row, with duplicates and
NULLs (for these operators two NULLs are the SAME row), SQLite's left-to-right order of a chain of them, and what they do that
IN / NOT IN do not. Answers by hand with `_sqlquery_model.py` (`u_all`, `u`, `inter`, `exc`).
"""

from __future__ import annotations

import random
from typing import Callable

from ._model import Maker
from ._sql_model import NULL, Retry, Tbl, fit, in_list, sql_item, sql_round, with_nulls
from ._sqlquery_model import exc, inter, sort_rows, u, u_all

SETS: list[Maker] = []


def reg(f: Callable) -> Callable:
    SETS.append(fit(f))
    return f


def _ab(rng: random.Random, n: int = 5, nulls: int = 0, null_in: str = "ab", lo: int = 1, hi: int = 8, names: str = "ab") -> tuple[Tbl, Tbl]:
    """Two one-column tables of small ints (some repeated); `nulls` NULLs go into the tables named in `null_in`."""
    out = []
    for name in names:
        v = [rng.randint(lo, hi) for _ in range(n)]
        if nulls and name in null_in:
            v = with_nulls(rng, v, nulls)
        out.append(Tbl(name, [("v", "INT")], [(x,) for x in v]))
    return out[0], out[1]


def R(t: Tbl) -> list[tuple]:
    return list(t.rows)


UNION = "SELECT v FROM a UNION SELECT v FROM b"
UNION_ALL = "SELECT v FROM a UNION ALL SELECT v FROM b"
INTERSECT = "SELECT v FROM a INTERSECT SELECT v FROM b"
EXCEPT = "SELECT v FROM a EXCEPT SELECT v FROM b"


def _nonempty(rows: list) -> None:
    if not rows:
        raise Retry


# ── Counting ────────────────────────────────────────────────────────────

@reg
def count_union(rng):
    a, b = _ab(rng)
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({UNION});", len(u(R(a), R(b))), "UNION keeps each different value once, across both tables.")


@reg
def count_union_all(rng):
    a, b = _ab(rng)
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({UNION_ALL});", len(u_all(R(a), R(b))), "UNION ALL keeps every row of both tables, repeats and all.")


@reg
def count_intersect(rng):
    a, b = _ab(rng)
    r = inter(R(a), R(b))
    _nonempty(r)
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({INTERSECT});", len(r), "INTERSECT keeps the values found in both tables, each one once.")


@reg
def count_except(rng):
    a, b = _ab(rng)
    r = exc(R(a), R(b))
    _nonempty(r)
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({EXCEPT});", len(r), "EXCEPT keeps the different values of a that b does not have.")


@reg
def count_except_reverse(rng):
    a, b = _ab(rng)
    r = exc(R(b), R(a))
    _nonempty(r)
    return sql_item([a, b], "SELECT COUNT(*) FROM (SELECT v FROM b EXCEPT SELECT v FROM a);", len(r), "EXCEPT is not symmetric: this is what b has and a lacks.")


@reg
def removed_by_union(rng):
    a, b = _ab(rng)
    r = [v for (v,) in u_all(R(a), R(b))]
    return sql_item([a, b], f"SELECT COUNT(*) - COUNT(DISTINCT v) FROM ({UNION_ALL});", len(r) - len(set(r)), "All the rows minus the different values: the rows UNION would have thrown away.")


@reg
def union_one_table(rng):
    a, _ = _ab(rng)
    return sql_item([a], "SELECT COUNT(*) FROM (SELECT v FROM a UNION SELECT v FROM a);", len(u(R(a), R(a))), "UNION also removes repeats inside one table: it is the different values of a.")


@reg
def intersect_self(rng):
    a, _ = _ab(rng)
    return sql_item([a], "SELECT COUNT(*) FROM (SELECT v FROM a INTERSECT SELECT v FROM a);", len(inter(R(a), R(a))), "A table intersected with itself is its different values.")


@reg
def except_self(rng):
    a, _ = _ab(rng)
    return sql_item([a], "SELECT COUNT(*) FROM (SELECT v FROM a EXCEPT SELECT v FROM a);", 0, "Nothing is in a that a does not have: no rows, so COUNT is 0.")


@reg
def distinct_of_union_all(rng):
    a, b = _ab(rng)
    return sql_item([a, b], f"SELECT COUNT(DISTINCT v) FROM ({UNION_ALL});", len(u(R(a), R(b))), "DISTINCT on top of UNION ALL gives the same count as UNION.")


# ── Sums and extremes ───────────────────────────────────────────────────

@reg
def sum_union(rng):
    a, b = _ab(rng)
    return sql_item([a, b], f"SELECT SUM(v) FROM ({UNION});", sum(v for (v,) in u(R(a), R(b))), "Each different value is added once.")


@reg
def sum_union_all(rng):
    a, b = _ab(rng)
    return sql_item([a, b], f"SELECT SUM(v) FROM ({UNION_ALL});", sum(v for (v,) in u_all(R(a), R(b))), "Every row counts, so repeated values are added again.")


@reg
def sum_intersect(rng):
    a, b = _ab(rng)
    r = inter(R(a), R(b))
    _nonempty(r)
    return sql_item([a, b], f"SELECT SUM(v) FROM ({INTERSECT});", sum(v for (v,) in r), "The shared values, each added once.")


@reg
def sum_except(rng):
    a, b = _ab(rng)
    r = exc(R(a), R(b))
    _nonempty(r)
    return sql_item([a, b], f"SELECT SUM(v) FROM ({EXCEPT});", sum(v for (v,) in r), "The values only a has, each added once.")


@reg
def max_except(rng):
    a, b = _ab(rng)
    r = exc(R(a), R(b))
    _nonempty(r)
    return sql_item([a, b], f"SELECT MAX(v) FROM ({EXCEPT});", max(v for (v,) in r), "The biggest value that a has and b does not.")


@reg
def min_intersect(rng):
    a, b = _ab(rng)
    r = inter(R(a), R(b))
    _nonempty(r)
    return sql_item([a, b], f"SELECT MIN(v) FROM ({INTERSECT});", min(v for (v,) in r), "The smallest value found in both tables.")


@reg
def avg_union_vs_all(rng):
    a, b = _ab(rng, n=4)
    r = [v for (v,) in u_all(R(a), R(b))]
    return sql_item([a, b], f"SELECT ROUND(AVG(v), 2) FROM ({UNION_ALL});", sql_round(sum(r) / len(r), 2), "UNION ALL keeps repeats, so they weigh in the average.")


@reg
def avg_union(rng):
    a, b = _ab(rng, n=4)
    r = [v for (v,) in u(R(a), R(b))]
    return sql_item([a, b], f"SELECT ROUND(AVG(v), 2) FROM ({UNION});", sql_round(sum(r) / len(r), 2), "UNION keeps each value once, so repeats do not weigh in.")


# ── NULLs ───────────────────────────────────────────────────────────────

@reg
def null_union_count(rng):
    a, b = _ab(rng, nulls=1)
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({UNION});", len(u(R(a), R(b))), "For UNION two NULLs are the same row, so NULL counts once among the different values.")


@reg
def null_union_count_col(rng):
    a, b = _ab(rng, nulls=1)
    return sql_item([a, b], f"SELECT COUNT(v) FROM ({UNION});", sum(1 for (v,) in u(R(a), R(b)) if v is not None), "COUNT(v) skips the NULL row that UNION kept.")


@reg
def null_intersect(rng):
    a, b = _ab(rng, nulls=1)
    r = inter(R(a), R(b))
    _nonempty(r)
    if (None,) not in r:
        raise Retry
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({INTERSECT});", len(r), "INTERSECT treats NULL as equal to NULL, so the NULL row is in both and is kept.")


@reg
def null_except(rng):
    a, b = _ab(rng, nulls=1)
    r = exc(R(a), R(b))
    _nonempty(r)
    if (None,) not in R(a) or (None,) not in R(b):
        raise Retry
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({EXCEPT});", len(r), "EXCEPT also matches NULL with NULL, so the NULL row of a is removed.")


@reg
def null_except_kept(rng):
    a, b = _ab(rng, nulls=1, null_in="a")
    r = exc(R(a), R(b))
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({EXCEPT});", len(r), "b has no NULL, so the NULL row of a stays in the result.")


@reg
def null_not_in_vs_except(rng):
    a, b = _ab(rng, nulls=1, null_in="b")
    return sql_item([a, b], "SELECT COUNT(*) FROM a WHERE v NOT IN (SELECT v FROM b);", 0, "b holds a NULL, so NOT IN is never true. (EXCEPT would not be fooled.)")


@reg
def null_except_not_fooled(rng):
    a, b = _ab(rng, nulls=1, null_in="b")
    r = exc(R(a), R(b))
    _nonempty(r)
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({EXCEPT});", len(r), "EXCEPT is not fooled by the NULL in b: it just removes the values b has.")


@reg
def null_first(rng):
    a, b = _ab(rng, nulls=1)
    return sql_item([a, b], f"SELECT v FROM ({UNION}) ORDER BY v LIMIT 1;", NULL, "NULL sorts first, and UNION kept one NULL row: it is the first row.")


@reg
def null_count_all(rng):
    a, b = _ab(rng, nulls=1)
    n = sum(1 for (v,) in u_all(R(a), R(b)) if v is None)
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({UNION_ALL}) WHERE v IS NULL;", n, "UNION ALL keeps every NULL row, from both tables.")


# ── Ordering, limits and chains ─────────────────────────────────────────

@reg
def union_order_limit(rng):
    a, b = _ab(rng)
    rows = sorted(v for (v,) in u(R(a), R(b)))
    _nonempty(rows[2:3])
    return sql_item([a, b], f"{UNION} ORDER BY v LIMIT 1 OFFSET 2;", rows[2], "ORDER BY and LIMIT apply to the whole union: the third smallest different value.")


@reg
def union_desc_offset(rng):
    a, b = _ab(rng)
    rows = sorted((v for (v,) in u(R(a), R(b))), reverse=True)
    _nonempty(rows[1:2])
    return sql_item([a, b], f"{UNION} ORDER BY v DESC LIMIT 1 OFFSET 1;", rows[1], "The second biggest different value of the two tables together.")


@reg
def union_all_offset(rng):
    a, b = _ab(rng)
    rows = sorted(v for (v,) in u_all(R(a), R(b)))
    return sql_item([a, b], f"{UNION_ALL} ORDER BY v LIMIT 1 OFFSET 2;", rows[2], "With UNION ALL the repeats stay, so the third row can repeat the second.")


@reg
def chain_left_to_right_except(rng):
    a, b = _ab(rng, n=4, hi=6)
    k = rng.randint(1, 6)
    r = exc(u(R(a), R(b)), [(k,)])
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({UNION} EXCEPT SELECT {k});", len(r), "A chain runs left to right: (a UNION b) first, then EXCEPT the single row.")


@reg
def chain_left_to_right_intersect(rng):
    a, b = _ab(rng, n=4, hi=6)
    k = rng.randint(1, 6)
    left = inter(u(R(a), R(b)), [(k,)])
    wrong = u(R(a), inter(R(b), [(k,)]))
    if len(left) == len(wrong):
        raise Retry
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({UNION} INTERSECT SELECT {k});", len(left),
                    "SQLite has no precedence between set operators: (a UNION b) INTERSECT the row, left to right.")


@reg
def chain_intersect_then_union(rng):
    a, b = _ab(rng, n=4, hi=6)
    k = rng.randint(1, 6)
    left = u(inter(R(a), R(b)), [(k,)])
    wrong = inter(R(a), u(R(b), [(k,)]))
    if len(left) == len(wrong):
        raise Retry
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({INTERSECT} UNION SELECT {k});", len(left), "(a INTERSECT b) first, then UNION the single row.")


@reg
def chain_except_then_union(rng):
    a, b = _ab(rng, n=4, hi=6)
    k = rng.randint(1, 6)
    r = u(exc(R(a), R(b)), [(k,)])
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({EXCEPT} UNION SELECT {k});", len(r), "(a EXCEPT b) first, then UNION the single row.")


@reg
def chain_three_union(rng):
    a, b = _ab(rng, n=4)
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({UNION} UNION SELECT v + 10 FROM a);", len(u(u(R(a), R(b)), [(v + 10,) for (v,) in R(a)])), "The third SELECT gives the values of a plus 10, none of which is in the first two.")


@reg
def const_union(rng):
    x, y, z = rng.sample(range(1, 9), 3)
    return sql_item([], f"SELECT COUNT(*) FROM (SELECT {x} UNION SELECT {x} UNION SELECT {y} UNION SELECT {z});", 3, "Four rows come in, but {x} twice is one row: three different values.".replace("{x}", str(x)))


@reg
def const_mixed_all_then_union(rng):
    x, y = rng.sample(range(1, 9), 2)
    return sql_item([], f"SELECT COUNT(*) FROM (SELECT {x} UNION ALL SELECT {x} UNION SELECT {y});", 2, "UNION at the end removes the repeats of everything before it: {x} and {y}.".replace("{x}", str(x)).replace("{y}", str(y)))


@reg
def const_mixed_union_then_all(rng):
    x, y = rng.sample(range(1, 9), 2)
    return sql_item([], f"SELECT COUNT(*) FROM (SELECT {x} UNION SELECT {x} UNION ALL SELECT {y} UNION ALL SELECT {y});", 3, "The first UNION leaves one {x}; the later UNION ALL steps add both {y} rows.".replace("{x}", str(x)).replace("{y}", str(y)))


@reg
def const_int_text(rng):
    x = rng.randint(1, 9)
    return sql_item([], f"SELECT COUNT(*) FROM (SELECT {x} UNION SELECT '{x}');", 2, "The number and the text are different values, so UNION keeps both.")


@reg
def const_int_real(rng):
    x = rng.randint(1, 9)
    return sql_item([], f"SELECT COUNT(*) FROM (SELECT {x} UNION SELECT {x}.0);", 1, "An integer and a real with the same value are equal, so UNION keeps one row.")


@reg
def const_first_name(rng):
    x, y = rng.sample(range(1, 30), 2)
    return sql_item([], f"SELECT MAX(x) FROM (SELECT {x} AS x UNION SELECT {y} AS y);", max(x, y), "The column is named by the first SELECT: x. Both values live in it.")


# ── Two-column rows and tagged rows ─────────────────────────────────────

def _pq(rng: random.Random) -> tuple[Tbl, Tbl]:
    def one(name):
        return Tbl(name, [("x", "INT"), ("y", "INT")], [(rng.randint(1, 3), rng.randint(1, 3)) for _ in range(3)])
    return one("p"), one("q")


@reg
def pair_union(rng):
    p, q = _pq(rng)
    return sql_item([p, q], "SELECT COUNT(*) FROM (SELECT x, y FROM p UNION SELECT x, y FROM q);", len(u(R(p), R(q))), "A row is the same only when BOTH columns match.")


@reg
def pair_intersect(rng):
    p, q = _pq(rng)
    r = inter(R(p), R(q))
    _nonempty(r)
    return sql_item([p, q], "SELECT COUNT(*) FROM (SELECT x, y FROM p INTERSECT SELECT x, y FROM q);", len(r), "Only whole (x, y) pairs found in both tables count.")


@reg
def pair_except(rng):
    p, q = _pq(rng)
    r = exc(R(p), R(q))
    _nonempty(r)
    return sql_item([p, q], "SELECT COUNT(*) FROM (SELECT x, y FROM p EXCEPT SELECT x, y FROM q);", len(r), "The different pairs of p that q does not have.")


@reg
def pair_swapped(rng):
    p, q = _pq(rng)
    r = inter(R(p), [(y, x) for x, y in R(q)])
    _nonempty(r)
    return sql_item([p, q], "SELECT COUNT(*) FROM (SELECT x, y FROM p INTERSECT SELECT y, x FROM q);", len(r), "The second SELECT swaps the columns of q before comparing.")


@reg
def pair_first_row(rng):
    p, q = _pq(rng)
    rows = sort_rows(u(R(p), R(q)))
    return sql_item([p, q], "SELECT x*10+y FROM p UNION SELECT x*10+y FROM q ORDER BY 1 DESC LIMIT 1;",
                    rows[-1][0] * 10 + rows[-1][1], "ORDER BY 1 sorts the whole union by its first column, x*10+y: the biggest comes first.")


@reg
def tagged_union(rng):
    a, b = _ab(rng)
    n = len(u([("a", v) for (v,) in R(a)], [("b", v) for (v,) in R(b)]))
    return sql_item([a, b], "SELECT COUNT(*) FROM (SELECT 'a', v FROM a UNION SELECT 'b', v FROM b);", n, "The tag makes the rows from a and b different, so only repeats inside each table go.")


@reg
def tagged_same(rng):
    a, b = _ab(rng)
    n = len(u([("t", v) for (v,) in R(a)], [("t", v) for (v,) in R(b)]))
    return sql_item([a, b], "SELECT COUNT(*) FROM (SELECT 't', v FROM a UNION SELECT 't', v FROM b);", n, "The same tag on both sides changes nothing: it is the plain union of the values.")


# ── IN / NOT IN against the set operators ───────────────────────────────

@reg
def count_in_vs_intersect(rng):
    a, b = _ab(rng)
    bs = [v for (v,) in R(b)]
    n = sum(1 for (v,) in R(a) if in_list(v, bs) is True)
    _nonempty([n])
    return sql_item([a, b], "SELECT COUNT(*) FROM a WHERE v IN (SELECT v FROM b);", n, "IN counts every ROW of a that has a match, repeats included (INTERSECT would count values).")


@reg
def count_not_in(rng):
    a, b = _ab(rng)
    bs = [v for (v,) in R(b)]
    n = sum(1 for (v,) in R(a) if in_list(v, bs) is False)
    return sql_item([a, b], "SELECT COUNT(*) FROM a WHERE v NOT IN (SELECT v FROM b);", n, "NOT IN counts every row of a without a match, repeats included (EXCEPT would count values).")


@reg
def sum_not_in(rng):
    a, b = _ab(rng)
    bs = [v for (v,) in R(b)]
    vals = [v for (v,) in R(a) if in_list(v, bs) is False]
    _nonempty(vals)
    return sql_item([a, b], "SELECT SUM(v) FROM a WHERE v NOT IN (SELECT v FROM b);", sum(vals), "Every a row with no match is added, repeats included.")


@reg
def not_in_repeats(rng):
    a, b = _ab(rng)
    bs = [v for (v,) in R(b)]
    vals = [v for (v,) in R(a) if in_list(v, bs) is False]
    _nonempty(vals)
    return sql_item([a, b], "SELECT COUNT(*) - COUNT(DISTINCT v) FROM a WHERE v NOT IN (SELECT v FROM b);", len(vals) - len(set(vals)), "NOT IN keeps every unmatched ROW: the gap is how many of them are repeats.")


# ── Text sets ───────────────────────────────────────────────────────────

def _words(rng: random.Random) -> tuple[Tbl, Tbl]:
    pool = ["fig", "plum", "pear", "lime", "date", "kiwi", "apple", "grape", "melon"]
    out = []
    for name in "ab":
        out.append(Tbl(name, [("v", "TEXT")], [(w,) for w in rng.sample(pool, 3)]))
    return out[0], out[1]


@reg
def text_intersect_first(rng):
    a, b = _words(rng)
    r = inter(R(a), R(b))
    _nonempty(r)
    return sql_item([a, b], f"{INTERSECT} ORDER BY v LIMIT 1;", min(v for (v,) in r), "Of the words in both tables, the one that sorts first.")


@reg
def text_except_last(rng):
    a, b = _words(rng)
    r = exc(R(a), R(b))
    _nonempty(r)
    return sql_item([a, b], f"{EXCEPT} ORDER BY v DESC LIMIT 1;", max(v for (v,) in r), "Of the words only a has, the one that sorts last.")


@reg
def text_case_union(rng):
    w = rng.choice(["fig", "plum", "pear", "lime"])
    a = Tbl("a", [("v", "TEXT")], [(w,), ("kiwi",)])
    b = Tbl("b", [("v", "TEXT")], [(w.upper(),), ("kiwi",)])
    return sql_item([a, b], f"SELECT COUNT(*) FROM ({UNION});", 3, "Text is compared exactly: {w} and {W} are different, so only kiwi is merged.".replace("{w}", w).replace("{W}", w.upper()))


@reg
def text_lower_union(rng):
    w = rng.choice(["fig", "plum", "pear", "lime"])
    a = Tbl("a", [("v", "TEXT")], [(w,), ("kiwi",)])
    b = Tbl("b", [("v", "TEXT")], [(w.upper(),), ("kiwi",)])
    return sql_item([a, b], "SELECT COUNT(*) FROM (SELECT LOWER(v) FROM a UNION SELECT LOWER(v) FROM b);", 2, "After LOWER the words match, so the union is just two words.")


@reg
def text_total_length(rng):
    a, b = _words(rng)
    r = u(R(a), R(b))
    return sql_item([a, b], f"SELECT SUM(LENGTH(v)) FROM ({UNION});", sum(len(v) for (v,) in r), "The letters of each different word, added up.")
