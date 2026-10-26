"""SQL core pack, part 2: Join Count and Order & Limit.

Every answer is worked out by hand with `_sql_model.py` (a join is a loop over pairs, an ordering is a sort with NULL the
smallest value), and tests/test_brain_packs.py runs every script in a fresh in-memory SQLite (tests/sql_oracle.py).
"""

from __future__ import annotations

import random

from ._model import WORDS, Maker
from ._sql_model import (NULL, Retry, Tbl, count_col, count_distinct, cross, eq, fit, gt, inner, ints, left_join, lt,
                         max_, order_by, sql_item, sum_, t_and, t_or, where, with_nulls, words)


# ── 1. Join Count ───────────────────────────────────────────────────────

def _ab(rng: random.Random, dup: bool = True, null_key: bool = False, n_a: int = 4, n_b: int = 5):
    """a(id INT) with different ids, and b(aid INT, v INT) pointing at them: some twice, some stray, maybe a NULL key."""
    ids = ints(rng, n_a, 1, 6)
    a = Tbl("a", [("id", "INT")], [(i,) for i in ids])
    pool = ids[:3] + [rng.randint(7, 9)]
    keys = [rng.choice(pool) for _ in range(n_b)]
    if dup:
        keys[1] = keys[0]
    if null_key:
        keys[rng.randrange(n_b)] = None
    b = Tbl("b", [("aid", "INT"), ("v", "INT")], [(k, rng.randint(1, 9)) for k in keys])
    return a, b


ON = lambda l, r: eq(l[0], r[0])  # noqa: E731  a.id = b.aid


def _j_inner(rng):
    a, b = _ab(rng)
    n = len(inner(a.rows, b.rows, ON))
    return sql_item([a, b], "SELECT COUNT(*) FROM a JOIN b ON a.id = b.aid;", n, "Every pair with a matching id: an a that is matched twice counts twice.")


def _j_left(rng):
    a, b = _ab(rng)
    n = len(left_join(a.rows, b.rows, ON, 2))
    return sql_item([a, b], "SELECT COUNT(*) FROM a LEFT JOIN b ON a.id = b.aid;", n, "A LEFT JOIN keeps every row of a, once for each match, or once with NULLs when it has none.")


def _j_cross(rng):
    a, b = _ab(rng)
    return sql_item([a, b], "SELECT COUNT(*) FROM a CROSS JOIN b;", len(a.rows) * len(b.rows), "A cross join pairs every row of a with every row of b.")


def _j_comma(rng):
    a, b = _ab(rng)
    return sql_item([a, b], "SELECT COUNT(*) FROM a, b;", len(a.rows) * len(b.rows), "A comma between tables is a cross join: rows times rows.")


def _j_comma_where(rng):
    a, b = _ab(rng)
    n = len(inner(a.rows, b.rows, ON))
    return sql_item([a, b], "SELECT COUNT(*) FROM a, b WHERE a.id = b.aid;", n, "A cross join filtered by the matching test is an inner join.")


def _j_anti(rng):
    a, b = _ab(rng)
    rows = left_join(a.rows, b.rows, ON, 2)
    n = sum(1 for r in rows if r[1] is None)
    return sql_item([a, b], "SELECT COUNT(*) FROM a LEFT JOIN b ON a.id = b.aid WHERE b.aid IS NULL;", n, "The a rows with no match get NULLs from b: this counts them.")


def _j_left_where(rng):
    a, b = _ab(rng)
    k = rng.randint(3, 6)
    rows = left_join(a.rows, b.rows, ON, 2)
    n = len(where(rows, lambda r: gt(r[2], k)))
    return sql_item([a, b], f"SELECT COUNT(*) FROM a LEFT JOIN b ON a.id = b.aid WHERE b.v > {k};", n, "The WHERE runs after the join: the unmatched rows have a NULL v, which is not above k, so they vanish.")


def _j_left_on(rng):
    a, b = _ab(rng)
    k = rng.randint(3, 6)
    n = len(left_join(a.rows, b.rows, lambda l, r: t_and(eq(l[0], r[0]), gt(r[1], k)), 2))
    return sql_item([a, b], f"SELECT COUNT(*) FROM a LEFT JOIN b ON a.id = b.aid AND b.v > {k};", n, "A test in ON only decides which rows match; an a with no match still stays, once, with NULLs.")


def _j_count_col(rng):
    a, b = _ab(rng)
    rows = left_join(a.rows, b.rows, ON, 2)
    return sql_item([a, b], "SELECT COUNT(b.aid) FROM a LEFT JOIN b ON a.id = b.aid;", count_col([r[1] for r in rows]), "COUNT(b.aid) skips the NULLs of the unmatched rows: it counts the matches.")


def _j_count_distinct(rng):
    a, b = _ab(rng)
    rows = inner(a.rows, b.rows, ON)
    return sql_item([a, b], "SELECT COUNT(DISTINCT a.id) FROM a JOIN b ON a.id = b.aid;", count_distinct([r[0] for r in rows]), "Each a that has at least one match, counted once.")


def _j_inner_where(rng):
    a, b = _ab(rng)
    k = rng.randint(2, 4)
    rows = inner(a.rows, b.rows, ON)
    return sql_item([a, b], f"SELECT COUNT(*) FROM a JOIN b ON a.id = b.aid WHERE a.id > {k};", len(where(rows, lambda r: gt(r[0], k))), "The join pairs rows up, then WHERE keeps the pairs whose id is above k.")


def _j_null_keys(rng):
    a, b = _ab(rng, null_key=True)
    return sql_item([a, b], "SELECT COUNT(*) FROM a JOIN b ON a.id = b.aid;", len(inner(a.rows, b.rows, ON)), "A NULL key matches nothing, not even another NULL.")


def _j_left_null_keys(rng):
    a, b = _ab(rng, null_key=True)
    return sql_item([a, b], "SELECT COUNT(*) FROM a LEFT JOIN b ON a.id = b.aid;", len(left_join(a.rows, b.rows, ON, 2)), "A NULL key in b matches no a, so that b row is simply not used.")


def _self_ids(rng, n: int = 4) -> Tbl:
    return Tbl("a", [("id", "INT")], [(i,) for i in ints(rng, n, 1, 8)])


def _j_self_lt(rng):
    a = _self_ids(rng)
    n = len(a.rows)
    return sql_item([a], "SELECT COUNT(*) FROM a x JOIN a y ON x.id < y.id;", n * (n - 1) // 2, "Every pair counted once, with the smaller id first.")


def _j_self_ne(rng):
    a = _self_ids(rng)
    n = len(a.rows)
    return sql_item([a], "SELECT COUNT(*) FROM a x JOIN a y ON x.id <> y.id;", n * (n - 1), "Every ordered pair of different rows: both x, y and y, x.")


def _j_self_eq(rng):
    a = _self_ids(rng)
    return sql_item([a], "SELECT COUNT(*) FROM a x JOIN a y ON x.id = y.id;", len(a.rows), "Each row matches only itself, since the ids are all different.")


def _j_self_gap(rng):
    a = _self_ids(rng, 5)
    k = rng.randint(1, 3)
    ids = a.col("id")
    n = sum(1 for x in ids for y in ids if y - x == k)
    return sql_item([a], f"SELECT COUNT(*) FROM a x JOIN a y ON y.id = x.id + {k};", n, "Pairs where the second id is exactly k more than the first.")


def _dup_tables(rng: random.Random):
    ks = [rng.randint(1, 3) for _ in range(4)]
    ms = [rng.randint(1, 3) for _ in range(4)]
    return Tbl("x", [("k", "INT")], [(v,) for v in ks]), Tbl("y", [("k", "INT")], [(v,) for v in ms])


def _j_dups(rng):
    x, y = _dup_tables(rng)
    n = len(inner(x.rows, y.rows, lambda l, r: eq(l[0], r[0])))
    return sql_item([x, y], "SELECT COUNT(*) FROM x JOIN y ON x.k = y.k;", n, "Duplicate keys multiply: a key that is twice in x and three times in y makes six pairs.")


def _j_dups_left(rng):
    x, y = _dup_tables(rng)
    n = len(left_join(x.rows, y.rows, lambda l, r: eq(l[0], r[0]), 1))
    return sql_item([x, y], "SELECT COUNT(*) FROM x LEFT JOIN y ON x.k = y.k;", n, "Every x row appears once per match in y, or once with a NULL.")


def _j_dups_distinct(rng):
    x, y = _dup_tables(rng)
    rows = inner(x.rows, y.rows, lambda l, r: eq(l[0], r[0]))
    return sql_item([x, y], "SELECT COUNT(DISTINCT x.k) FROM x JOIN y ON x.k = y.k;", count_distinct([r[0] for r in rows]), "The pairs repeat keys; DISTINCT counts each key once.")


def _j_using(rng):
    a = Tbl("a", [("id", "INT")], [(i,) for i in ints(rng, 4, 1, 6)])
    b = Tbl("b", [("id", "INT")], [(rng.randint(1, 6),) for _ in range(5)])
    n = len(inner(a.rows, b.rows, ON))
    return sql_item([a, b], "SELECT COUNT(*) FROM a JOIN b USING (id);", n, "USING (id) joins on the column both tables have.")


def _j_natural(rng):
    a = Tbl("a", [("id", "INT")], [(i,) for i in ints(rng, 4, 1, 6)])
    b = Tbl("b", [("id", "INT")], [(rng.randint(1, 6),) for _ in range(5)])
    n = len(inner(a.rows, b.rows, ON))
    return sql_item([a, b], "SELECT COUNT(*) FROM a NATURAL JOIN b;", n, "NATURAL JOIN joins on every column name the tables share: here, id.")


def _j_union(rng):
    a, b = _ab(rng)
    n = len(set(a.col("id")) | set(b.col("aid")))
    return sql_item([a, b], "SELECT COUNT(*) FROM (SELECT id FROM a UNION SELECT aid FROM b);", n, "UNION removes duplicates: each different id once.")


def _j_union_all(rng):
    a, b = _ab(rng)
    return sql_item([a, b], "SELECT COUNT(*) FROM (SELECT id FROM a UNION ALL SELECT aid FROM b);", len(a.rows) + len(b.rows), "UNION ALL keeps every row of both.")


def _j_intersect(rng):
    a, b = _ab(rng)
    n = len(set(a.col("id")) & set(b.col("aid")))
    return sql_item([a, b], "SELECT COUNT(*) FROM (SELECT id FROM a INTERSECT SELECT aid FROM b);", n, "INTERSECT keeps the ids in both, each once.")


def _j_except(rng):
    a, b = _ab(rng)
    n = len(set(a.col("id")) - set(b.col("aid")))
    return sql_item([a, b], "SELECT COUNT(*) FROM (SELECT id FROM a EXCEPT SELECT aid FROM b);", n, "EXCEPT keeps the ids of a that b does not have.")


def _j_three(rng):
    a = _self_ids(rng)
    c = Tbl("c", [("n", "INT")], [(k,) for k in ints(rng, 2, 1, 5)])
    return sql_item([a, c], "SELECT COUNT(*) FROM a x, a y, c;", len(a.rows) ** 2 * len(c.rows), "Three tables cross-joined: the row counts multiply (a twice, c once).")


def _j_left_unmatched_ids(rng):
    a, b = _ab(rng)
    matched = {r[0] for r in b.rows}
    n = sum(1 for (i,) in a.rows if i not in matched)
    return sql_item([a, b], "SELECT COUNT(*) FROM a WHERE id NOT IN (SELECT aid FROM b);", n, "The a rows whose id is nowhere in b (b has no NULL keys here).")


def _j_sum_matches(rng):
    a, b = _ab(rng)
    rows = inner(a.rows, b.rows, ON)
    s = sum_([r[2] for r in rows])
    if s is None:
        raise Retry
    return sql_item([a, b], "SELECT SUM(b.v) FROM a JOIN b ON a.id = b.aid;", s, "Only the b rows that match some a are added.")


def _j_left_sum(rng):
    a, b = _ab(rng)
    rows = left_join(a.rows, b.rows, ON, 2)
    s = sum_([r[2] for r in rows])
    if s is None:
        raise Retry
    return sql_item([a, b], "SELECT SUM(b.v) FROM a LEFT JOIN b ON a.id = b.aid;", s, "The unmatched a rows contribute a NULL, which SUM skips: the same total as the inner join.")


def _j_max_matched(rng):
    a, b = _ab(rng)
    rows = inner(a.rows, b.rows, ON)
    if not rows:
        raise Retry
    return sql_item([a, b], "SELECT MAX(a.id) FROM a JOIN b ON a.id = b.aid;", max_([r[0] for r in rows]), "The biggest id that has a match.")


def _j_exists_count(rng):
    a, b = _ab(rng)
    keys = set(b.col("aid"))
    return sql_item([a, b], "SELECT COUNT(*) FROM a WHERE EXISTS (SELECT 1 FROM b WHERE b.aid = a.id);", sum(1 for (i,) in a.rows if i in keys), "Each a that has at least one b: EXISTS counts it once, however many b rows match.")


def _j_not_exists(rng):
    a, b = _ab(rng, n_a=3, n_b=4)
    keys = set(b.col("aid"))
    return sql_item([a, b], "SELECT COUNT(*) FROM a WHERE NOT EXISTS (SELECT 1 FROM b WHERE b.aid = a.id);", sum(1 for (i,) in a.rows if i not in keys), "The a rows without any b.")


def _j_cross_where(rng):
    a, b = _ab(rng)
    pairs = cross(a.rows, b.rows)
    n = len(where(pairs, lambda r: lt(r[0], r[2])))
    return sql_item([a, b], "SELECT COUNT(*) FROM a, b WHERE a.id < b.v;", n, "Every pair, kept when the a id is below the b value.")


def _j_left_count_star_nomatch(rng):
    a, b = _ab(rng)
    rows = left_join(a.rows, b.rows, ON, 2)
    one = rng.choice([i for (i,) in a.rows])
    n = sum(1 for r in rows if r[0] == one)
    return sql_item([a, b], f"SELECT COUNT(*) FROM a LEFT JOIN b ON a.id = b.aid WHERE a.id = {one};", n, "One a row stays once if it has no match, or once per match.")


def _j_dup_v(rng):
    a, b = _ab(rng)
    rows = inner(a.rows, b.rows, ON)
    k = rng.randint(3, 6)
    n = len(where(rows, lambda r: gt(r[2], k)))
    return sql_item([a, b], f"SELECT COUNT(*) FROM a JOIN b ON a.id = b.aid AND b.v > {k};", n, "For an inner join a test in ON works like a test in WHERE.")


def _j_union_dups(rng):
    x, y = _dup_tables(rng)
    n = len(set(x.col("k")) | set(y.col("k")))
    return sql_item([x, y], "SELECT COUNT(*) FROM (SELECT k FROM x UNION SELECT k FROM y);", n, "UNION lists each different value once.")


def _j_left_dups_matched(rng):
    x, y = _dup_tables(rng)
    rows = left_join(x.rows, y.rows, lambda l, r: eq(l[0], r[0]), 1)
    return sql_item([x, y], "SELECT COUNT(y.k) FROM x LEFT JOIN y ON x.k = y.k;", count_col([r[1] for r in rows]), "COUNT(y.k) counts only the matched pairs.")


def _j_except_all_dups(rng):
    x, y = _dup_tables(rng)
    n = len(set(x.col("k")) - set(y.col("k")))
    return sql_item([x, y], "SELECT COUNT(*) FROM (SELECT k FROM x EXCEPT SELECT k FROM y);", n, "EXCEPT also removes duplicates: each different value of x that y lacks, once.")


def _j_left_or_null(rng):
    a, b = _ab(rng, n_a=3, n_b=4)
    k = rng.randint(3, 6)
    rows = left_join(a.rows, b.rows, ON, 2)
    n = len(where(rows, lambda r: t_or(r[2] is None, gt(r[2], k))))
    return sql_item([a, b], f"SELECT COUNT(*) FROM a LEFT JOIN b ON a.id = b.aid WHERE b.v IS NULL OR b.v > {k};", n, "The unmatched rows (NULL v) are kept by IS NULL, the matched ones by v > k.")


JOINS: list[Maker] = [fit(f) for f in (_j_left_or_null,
    _j_inner, _j_left, _j_cross, _j_comma, _j_comma_where, _j_anti, _j_left_where, _j_left_on, _j_count_col, _j_count_distinct,
    _j_inner_where, _j_null_keys, _j_left_null_keys, _j_self_lt, _j_self_ne, _j_self_eq, _j_self_gap, _j_dups, _j_dups_left,
    _j_dups_distinct, _j_using, _j_natural, _j_union, _j_union_all, _j_intersect, _j_except, _j_three, _j_left_unmatched_ids,
    _j_sum_matches, _j_left_sum, _j_max_matched, _j_exists_count, _j_not_exists, _j_cross_where, _j_left_count_star_nomatch,
    _j_dup_v, _j_union_dups, _j_left_dups_matched, _j_except_all_dups)]


# ── 2. Order & Limit ────────────────────────────────────────────────────

def _t_unique(rng: random.Random, n: int = 6, nulls: int = 1) -> Tbl:
    """t(a INT, b TEXT): different a's (one NULL) and short words."""
    a = with_nulls(rng, ints(rng, n, 1, 20), nulls) if nulls else ints(rng, n, 1, 20)
    b = with_nulls(rng, words(rng, n)) if rng.random() < 0.3 else words(rng, n)
    return Tbl("t", [("a", "INT"), ("b", "TEXT")], list(zip(a, b)))


def _a_order(t: Tbl, desc: bool = False) -> list[tuple]:
    return order_by(t.rows, (lambda r: r[0], desc))


def _o_first(rng):
    t = _t_unique(rng)
    return sql_item([t], "SELECT a FROM t ORDER BY a LIMIT 1;", _a_order(t)[0][0], "NULL counts as the smallest value, so it comes first when sorting up.")


def _o_first_desc(rng):
    t = _t_unique(rng)
    return sql_item([t], "SELECT a FROM t ORDER BY a DESC LIMIT 1;", _a_order(t, True)[0][0], "Sorted down, NULL comes last, so the first row is the biggest number.")


def _o_offset(rng):
    t = _t_unique(rng)
    k = rng.randint(1, 3)
    return sql_item([t], f"SELECT a FROM t ORDER BY a LIMIT 1 OFFSET {k};", _a_order(t)[k][0], "OFFSET skips that many rows first; LIMIT 1 then takes the next one.")


def _o_offset_desc(rng):
    t = _t_unique(rng)
    k = rng.randint(1, 3)
    return sql_item([t], f"SELECT a FROM t ORDER BY a DESC LIMIT 1 OFFSET {k};", _a_order(t, True)[k][0], "Sorted down: skip the biggest k, take the next.")


def _o_b_of_first(rng):
    t = _t_unique(rng, nulls=0)
    return sql_item([t], "SELECT b FROM t ORDER BY a LIMIT 1;", _a_order(t)[0][1], "The b that sits in the row with the smallest a.")


def _o_b_of_second_desc(rng):
    t = _t_unique(rng, nulls=0)
    return sql_item([t], "SELECT b FROM t ORDER BY a DESC LIMIT 1 OFFSET 1;", _a_order(t, True)[1][1], "The row with the second biggest a, and its b.")


def _o_distinct_offset(rng):
    vals = [rng.randint(1, 6) for _ in range(6)]
    t = Tbl("t", [("a", "INT")], [(v,) for v in vals])
    distinct = sorted(set(vals))
    if len(distinct) < 3:
        raise Retry
    return sql_item([t], "SELECT DISTINCT a FROM t ORDER BY a LIMIT 1 OFFSET 1;", distinct[1], "DISTINCT first removes the repeats; then the second smallest value is picked.")


def _o_sum_top3(rng):
    t = _t_unique(rng)
    top = _a_order(t, True)[:3]
    return sql_item([t], "SELECT SUM(a) FROM (SELECT a FROM t ORDER BY a DESC LIMIT 3);", sum_([r[0] for r in top]), "The three biggest values (NULL sorts last, so it is not among them) are added.")


def _o_sum_bottom3(rng):
    t = _t_unique(rng)
    low = _a_order(t)[:3]
    return sql_item([t], "SELECT SUM(a) FROM (SELECT a FROM t ORDER BY a LIMIT 3);", sum_([r[0] for r in low]), "NULL sorts first, so it is one of the three rows; SUM skips it and adds the other two.")


def _o_count_offset(rng):
    t = _t_unique(rng)
    lim, off = rng.randint(2, 4), rng.randint(1, 4)
    n = max(0, min(lim, len(t.rows) - off))
    if n == 0:
        raise Retry
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT a FROM t LIMIT {lim} OFFSET {off});", n, "OFFSET skips rows, LIMIT caps what is left.")


def _o_expr(rng):
    t = _t_unique(rng, nulls=0)
    k = rng.randint(3, 4)
    first = order_by(t.rows, (lambda r: r[0] % k, False), (lambda r: r[0], False))[0]
    return sql_item([t], f"SELECT a FROM t ORDER BY a % {k}, a LIMIT 1;", first[0], "Sorted by the remainder first, and by a itself when the remainders tie.")


def _o_length(rng):
    ws = [w for w in WORDS if len(w) <= 6]
    vals = rng.sample(ws, 4)
    t = Tbl("t", [("b", "TEXT")], [(v,) for v in vals])
    first = order_by(t.rows, (lambda r: len(r[0]), False), (lambda r: r[0], False))[0]
    return sql_item([t], "SELECT b FROM t ORDER BY LENGTH(b), b LIMIT 1;", first[0], "The shortest word first; two words of the same length go in dictionary order.")


def _o_caps(rng):
    ws = words(rng, 4)
    vals = [w.capitalize() if i == 0 else w for i, w in enumerate(ws)]
    rng.shuffle(vals)
    t = Tbl("t", [("b", "TEXT")], [(v,) for v in vals])
    return sql_item([t], "SELECT b FROM t ORDER BY b LIMIT 1;", min(vals), "Capital letters sort before every lower-case letter.")


def _o_numbers_as_text(rng):
    vals = rng.sample(["9", "10", "100", "25", "7", "81"], 4)
    t = Tbl("t", [("b", "TEXT")], [(v,) for v in vals])
    return sql_item([t], "SELECT b FROM t ORDER BY b LIMIT 1;", min(vals), "Text is sorted character by character, so '10' comes before '9'.")


def _o_numbers_cast(rng):
    vals = rng.sample(["9", "10", "100", "25", "7", "81"], 4)
    t = Tbl("t", [("b", "TEXT")], [(v,) for v in vals])
    return sql_item([t], "SELECT b FROM t ORDER BY b + 0 LIMIT 1;", min(vals, key=int), "b + 0 turns the text into a number first, so the numeric order is used.")


def _o_two_keys(rng):
    ws = words(rng, 2)
    rows = [(rng.randint(1, 9), ws[i % 2]) for i in range(5)]
    if len({r[0] for r in rows}) != 5:
        raise Retry
    t = Tbl("t", [("a", "INT"), ("b", "TEXT")], rows)
    first = order_by(rows, (lambda r: r[1], False), (lambda r: r[0], True))[0]
    return sql_item([t], "SELECT a FROM t ORDER BY b, a DESC LIMIT 1;", first[0], "Sorted by b first; inside the same b, the biggest a comes first.")


def _o_nulls_last(rng):
    t = _t_unique(rng)
    vals = sorted(v for v in t.col("a") if v is not None)
    return sql_item([t], "SELECT a FROM t ORDER BY a NULLS LAST LIMIT 1;", vals[0], "NULLS LAST moves the NULL to the end, so the smallest real number comes first.")


def _o_nulls_first_desc(rng):
    t = _t_unique(rng)
    return sql_item([t], "SELECT a FROM t ORDER BY a DESC NULLS FIRST LIMIT 1;", NULL, "NULLS FIRST puts the NULL in front even when sorting down.")


def _o_where_order(rng):
    t = _t_unique(rng)
    k = rng.randint(5, 12)
    rows = order_by(where(t.rows, lambda r: gt(r[0], k)), (lambda r: r[0], False))
    if not rows:
        raise Retry
    return sql_item([t], f"SELECT a FROM t WHERE a > {k} ORDER BY a LIMIT 1;", rows[0][0], "WHERE drops the rows first (NULL too); the smallest a that is left comes first.")


def _o_max_of_limit(rng):
    t = _t_unique(rng)
    return sql_item([t], "SELECT MAX(a) FROM (SELECT a FROM t ORDER BY a LIMIT 3);", max_([r[0] for r in _a_order(t)[:3]]), "The three smallest rows include the NULL; MAX of them is the biggest real one.")


def _o_distinct_b(rng):
    ws = words(rng, 3)
    vals = [rng.choice(ws) for _ in range(6)]
    t = Tbl("t", [("b", "TEXT")], [(v,) for v in vals])
    d = sorted(set(vals))
    return sql_item([t], "SELECT DISTINCT b FROM t ORDER BY b DESC LIMIT 1;", d[-1], "DISTINCT removes repeats; the last word in dictionary order comes first when sorting down.")


def _o_count_distinct_limit(rng):
    vals = [rng.randint(1, 5) for _ in range(7)]
    t = Tbl("t", [("a", "INT")], [(v,) for v in vals])
    first4 = vals[:4]
    return sql_item([t], "SELECT COUNT(DISTINCT a) FROM (SELECT a FROM t LIMIT 4);", len(set(first4)), "LIMIT 4 without ORDER BY keeps the first four rows as stored; then the different values are counted.")


def _o_second_smallest_distinct(rng):
    vals = [rng.randint(1, 5) for _ in range(6)]
    t = Tbl("t", [("a", "INT")], [(v,) for v in vals])
    d = sorted(set(vals))
    if len(d) < 2:
        raise Retry
    return sql_item([t], "SELECT MIN(a) FROM t WHERE a > (SELECT MIN(a) FROM t);", d[1], "The smallest value above the smallest: the second smallest.")


def _o_last_by_desc(rng):
    t = _t_unique(rng, nulls=0)
    return sql_item([t], "SELECT b FROM t ORDER BY a DESC LIMIT 1;", _a_order(t, True)[0][1], "Sorted down by a: the first row has the biggest a.")


def _o_neg(rng):
    vals = ints(rng, 5, -5, 5)
    t = Tbl("t", [("a", "INT")], [(v,) for v in vals])
    return sql_item([t], "SELECT a FROM t ORDER BY a LIMIT 1;", min(vals), "Negative numbers are smaller than positive ones.")


def _o_abs(rng):
    vals = ints(rng, 5, -9, 9)
    if len({abs(v) for v in vals}) != 5:
        raise Retry
    t = Tbl("t", [("a", "INT")], [(v,) for v in vals])
    return sql_item([t], "SELECT a FROM t ORDER BY ABS(a) LIMIT 1;", min(vals, key=abs), "Sorted by the size of the number, ignoring its sign.")


def _o_desc_abs(rng):
    vals = ints(rng, 5, -9, 9)
    if len({abs(v) for v in vals}) != 5:
        raise Retry
    t = Tbl("t", [("a", "INT")], [(v,) for v in vals])
    return sql_item([t], "SELECT a FROM t ORDER BY ABS(a) DESC LIMIT 1;", max(vals, key=abs), "The biggest size first: its sign stays.")


def _o_offset_beyond(rng):
    t = _t_unique(rng)
    k = rng.randint(1, 3)
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT a FROM t ORDER BY a LIMIT -1 OFFSET {k});", len(t.rows) - k, "A negative LIMIT means no limit: everything after the skipped rows.")


def _o_sum_offset(rng):
    t = _t_unique(rng, nulls=0)
    rows = _a_order(t)[1:3]
    return sql_item([t], "SELECT SUM(a) FROM (SELECT a FROM t ORDER BY a LIMIT 2 OFFSET 1);", sum_([r[0] for r in rows]), "Skip the smallest, then take the next two and add them.")


def _o_b_by_len(rng):
    ws = rng.sample([w for w in WORDS if len(w) <= 6], 3)
    lens = [len(w) for w in ws]
    if len(set(lens)) != 3:
        raise Retry
    t = Tbl("t", [("b", "TEXT")], [(w,) for w in ws])
    return sql_item([t], "SELECT b FROM t ORDER BY LENGTH(b) DESC LIMIT 1;", max(ws, key=len), "The longest word first.")


def _o_char(rng):
    ws = rng.sample([w for w in WORDS if len(w) <= 6], 4)
    firsts = [w[-1] for w in ws]
    if len(set(firsts)) != 4:
        raise Retry
    t = Tbl("t", [("b", "TEXT")], [(w,) for w in ws])
    return sql_item([t], "SELECT b FROM t ORDER BY SUBSTR(b, -1) LIMIT 1;", min(ws, key=lambda w: w[-1]), "Sorted by the last letter of each word.")


def _o_count_first_k(rng):
    t = _t_unique(rng)
    return sql_item([t], "SELECT COUNT(a) FROM (SELECT a FROM t ORDER BY a LIMIT 2);", count_col([r[0] for r in _a_order(t)[:2]]), "The two smallest rows include the NULL, which COUNT(a) does not count.")


def _o_row_after_null(rng):
    t = _t_unique(rng)
    return sql_item([t], "SELECT a FROM t ORDER BY a LIMIT 1 OFFSET 1;", _a_order(t)[1][0], "NULL is first, so the second row is the smallest real number.")


ORDERS: list[Maker] = [fit(f) for f in (
    _o_first, _o_first_desc, _o_offset, _o_offset_desc, _o_b_of_first, _o_b_of_second_desc, _o_distinct_offset, _o_sum_top3,
    _o_sum_bottom3, _o_count_offset, _o_expr, _o_length, _o_caps, _o_numbers_as_text, _o_numbers_cast, _o_two_keys,
    _o_nulls_last, _o_nulls_first_desc, _o_where_order, _o_max_of_limit, _o_distinct_b, _o_count_distinct_limit,
    _o_second_smallest_distinct, _o_last_by_desc, _o_neg, _o_abs, _o_desc_abs, _o_offset_beyond, _o_sum_offset, _o_b_by_len,
    _o_char, _o_count_first_k, _o_row_after_null)]


def _o_count_nulls_desc(rng):
    t = _t_unique(rng)
    rows = _a_order(t, True)[:2]
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT a FROM t ORDER BY a DESC LIMIT 2) WHERE a IS NULL;", sum(1 for r in rows if r[0] is None), "Sorted down, the NULL is last: it is not among the first two rows.")


def _o_min_b(rng):
    t = _t_unique(rng)
    return sql_item([t], "SELECT MIN(b) FROM t;", min([w for w in t.col("b") if w]), "MIN of text is the first in dictionary order, and ignores NULL.")


def _o_max_b(rng):
    t = _t_unique(rng)
    return sql_item([t], "SELECT MAX(b) FROM t;", max([w for w in t.col("b") if w]), "MAX of text is the last in dictionary order, and ignores NULL.")


def _o_by_number(rng):
    t = _t_unique(rng)
    return sql_item([t], "SELECT a FROM t ORDER BY 1 DESC LIMIT 1 OFFSET 2;", _a_order(t, True)[2][0], "ORDER BY 1 sorts by the first column; skip the two biggest.")


def _o_alias_null(rng):
    t = _t_unique(rng)
    return sql_item([t], "SELECT a * -1 AS n FROM t ORDER BY n LIMIT 1;", NULL, "The NULL row stays NULL after the multiplication, and NULL sorts first.")


def _o_alias(rng):
    t = _t_unique(rng, nulls=0)
    return sql_item([t], "SELECT a * -1 AS n FROM t ORDER BY n LIMIT 1;", -max(t.col("a")), "Negating turns the biggest a into the smallest n.")


def _o_sum_two_offset(rng):
    t = _t_unique(rng)
    rows = _a_order(t, True)[2:4]
    return sql_item([t], "SELECT SUM(a) FROM (SELECT a FROM t ORDER BY a DESC LIMIT 2 OFFSET 2);", sum_([r[0] for r in rows]), "Skip the two biggest, then add the next two.")


def _o_b_second_desc(rng):
    t = _t_unique(rng)
    ordered = order_by(t.rows, (lambda r: r[1], True))
    return sql_item([t], "SELECT b FROM t ORDER BY b DESC LIMIT 1 OFFSET 1;", ordered[1][1], "Sorted down by text, any NULL is last: the second word from the end of the alphabet.")


def _o_below_third(rng):
    t = _t_unique(rng)
    v = _a_order(t)[2][0]
    if v is None:
        raise Retry
    n = sum(1 for r in t.rows if lt(r[0], v) is True)
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE a < (SELECT a FROM t ORDER BY a LIMIT 1 OFFSET 2);", n, "The subquery is the third row of the sorted list (the NULL is first): the rows below it.")


ORDERS += [fit(f) for f in (_o_count_nulls_desc, _o_min_b, _o_max_b, _o_by_number, _o_alias_null, _o_alias, _o_sum_two_offset,
                            _o_b_second_desc, _o_below_third)]
