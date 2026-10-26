"""SQL deeper queries, part 8: Multi-key Order.

ORDER BY two or more keys with ties, mixed ASC / DESC, NULL placement (NULLs are smallest; NULLS FIRST / LAST), LIMIT / OFFSET after
ordering (including `LIMIT 2, 1`), DISTINCT with ORDER BY, ordering by expressions, positions and aggregates, and window ranking
over ties (ROW_NUMBER, RANK, DENSE_RANK, LAG, FIRST_VALUE, a running sum) including the top N per group. Every query that picks a row
orders by keys that decide it completely. The model is `order2` in `_sqlquery_model.py`.
"""

from __future__ import annotations

import random
from typing import Callable

from ._model import Maker
from ._sql_model import NULL, Retry, Tbl, fit, sql_item
from ._sqlquery_model import dense_ranks, order2, ranks

ORDER: list[Maker] = []


def reg(f: Callable) -> Callable:
    ORDER.append(fit(f))
    return f


LETTERS = "abcdefgh"
N, G, S = 0, 1, 2  # column positions of t(n, g, s)


def _t(rng: random.Random, n: int = 6, null_g: int = 0, null_s: int = 0, tied_s: bool = False, unique_gs: bool = True) -> Tbl:
    """t(n TEXT, g INT, s INT): distinct one-letter names, a group 1-3 and a score; optionally NULLs and tied scores."""
    names = rng.sample(LETTERS, n)
    rows = [(names[i], rng.randint(1, 3), rng.randint(1, 5 if tied_s else 9)) for i in range(n)]
    if unique_gs and len({(r[G], r[S]) for r in rows}) != n:
        raise Retry
    rows = [list(r) for r in rows]
    for k in rng.sample(range(n), null_g):
        rows[k][G] = None
    for k in rng.sample(range(n), null_s):
        rows[k][S] = None
    return Tbl("t", [("n", "TEXT"), ("g", "INT"), ("s", "INT")], [tuple(r) for r in rows])


def _need_unique(rows: list, *keys) -> None:
    """Refuse data where the ordering keys leave a tie (the engine's order for ties is not promised)."""
    ks = [tuple(k(r) for k in keys) for r in rows]
    if len(set(ks)) != len(ks):
        raise Retry


def _g(r): return r[G]
def _s(r): return r[S]
def _n(r): return r[N]


# ── Two keys, four direction mixes ──────────────────────────────────────

@reg
def asc_asc_first(rng):
    t = _t(rng)
    rows = order2(t.rows, (_g, False), (_s, False))
    return sql_item([t], "SELECT n FROM t ORDER BY g, s LIMIT 1;", rows[0][N], "g decides first; s only breaks ties inside the same g.")


@reg
def asc_desc_offset(rng):
    t = _t(rng)
    k = rng.randint(1, 3)
    rows = order2(t.rows, (_g, False), (_s, True))
    return sql_item([t], f"SELECT n FROM t ORDER BY g, s DESC LIMIT 1 OFFSET {k};", rows[k][N], "Smallest g first, and within one g the biggest s first. OFFSET skips the first rows.")


@reg
def desc_asc_offset(rng):
    t = _t(rng)
    k = rng.randint(1, 3)
    rows = order2(t.rows, (_g, True), (_s, False))
    return sql_item([t], f"SELECT n FROM t ORDER BY g DESC, s LIMIT 1 OFFSET {k};", rows[k][N], "Biggest g first; inside a g the smallest s comes first.")


@reg
def desc_desc_offset(rng):
    t = _t(rng)
    k = rng.randint(1, 3)
    rows = order2(t.rows, (_g, True), (_s, True))
    return sql_item([t], f"SELECT n FROM t ORDER BY g DESC, s DESC LIMIT 1 OFFSET {k};", rows[k][N], "Both keys descending.")


@reg
def s_before_g(rng):
    t = _t(rng)
    _need_unique(t.rows, _s, _g)
    rows = order2(t.rows, (_s, False), (_g, False))
    k = rng.randint(0, 2)
    return sql_item([t], f"SELECT n FROM t ORDER BY s, g LIMIT 1 OFFSET {k};", rows[k][N], "Now s is the main key and g only breaks ties.")


@reg
def whole_order_asc_desc(rng):
    t = _t(rng, 5)
    rows = order2(t.rows, (_g, False), (_s, True))
    return sql_item([t], "SELECT GROUP_CONCAT(n, '' ORDER BY g, s DESC) FROM t;", "".join(r[N] for r in rows), "ORDER BY inside GROUP_CONCAT lays out the whole order as one word: g up, s down.")


@reg
def whole_order_desc_asc(rng):
    t = _t(rng, 5)
    rows = order2(t.rows, (_g, True), (_s, False))
    return sql_item([t], "SELECT GROUP_CONCAT(n, '' ORDER BY g DESC, s) FROM t;", "".join(r[N] for r in rows), "g down, and s up inside each g.")


@reg
def whole_order_desc_desc(rng):
    t = _t(rng, 5)
    rows = order2(t.rows, (_g, True), (_s, True))
    return sql_item([t], "SELECT GROUP_CONCAT(n, '' ORDER BY g DESC, s DESC) FROM t;", "".join(r[N] for r in rows), "Both keys down: exactly the reverse of g, s.")


@reg
def last_row_via_desc(rng):
    t = _t(rng)
    rows = order2(t.rows, (_g, False), (_s, False))
    return sql_item([t], "SELECT n FROM t ORDER BY g DESC, s DESC LIMIT 1;", rows[-1][N], "Reversing every key gives the LAST row of the g, s order.")


@reg
def tie_break_by_name(rng):
    t = _t(rng, 6, tied_s=True, unique_gs=False)
    rows = order2(t.rows, (_s, True), (_n, False))
    return sql_item([t], "SELECT n FROM t ORDER BY s DESC, n LIMIT 1;", rows[0][N], "Several rows share the top s; the name breaks the tie, a before b.")


@reg
def tie_break_name_desc(rng):
    t = _t(rng, 6, tied_s=True, unique_gs=False)
    rows = order2(t.rows, (_s, False), (_n, True))
    return sql_item([t], "SELECT n FROM t ORDER BY s, n DESC LIMIT 1;", rows[0][N], "The smallest s may be shared; among those, the name sorted backwards decides.")


@reg
def sum_first_three(rng):
    t = _t(rng)
    rows = order2(t.rows, (_g, False), (_s, True))[:3]
    return sql_item([t], "SELECT SUM(s) FROM (SELECT s FROM t ORDER BY g, s DESC LIMIT 3);", sum(r[S] for r in rows), "The inner query keeps the first three rows of the order; the outer adds their s.")


@reg
def sum_g_of_first(rng):
    t = _t(rng)
    rows = order2(t.rows, (_s, True), (_g, False))[:3]
    _need_unique(t.rows, _s, _g)
    return sql_item([t], "SELECT SUM(g) FROM (SELECT g FROM t ORDER BY s DESC, g LIMIT 3);", sum(r[G] for r in rows), "The three highest-scoring rows (by s), and the sum of their groups.")


@reg
def top3_alphabetical(rng):
    t = _t(rng, 6, unique_gs=False)
    _need_unique(t.rows, _s)
    top = order2(t.rows, (_s, True))[:3]
    return sql_item([t], "SELECT n FROM (SELECT n, s FROM t ORDER BY s DESC LIMIT 3) ORDER BY n LIMIT 1;", min(r[N] for r in top), "Take the three best by s first, then sort those alphabetically.")


# ── NULL placement ──────────────────────────────────────────────────────

@reg
def null_first_default(rng):
    t = _t(rng, 6, null_g=1)
    rows = order2(t.rows, (_g, False), (_s, False))
    _need_unique(t.rows, _g, _s)
    return sql_item([t], "SELECT n FROM t ORDER BY g, s LIMIT 1;", rows[0][N], "NULL is smaller than every number, so ascending puts the NULL row first.")


@reg
def null_last_desc(rng):
    t = _t(rng, 6, null_g=1)
    rows = order2(t.rows, (_g, True), (_s, False))
    _need_unique(t.rows, _g, _s)
    return sql_item([t], "SELECT n FROM t ORDER BY g DESC, s LIMIT 1 OFFSET 5;", rows[5][N], "Descending, NULL comes last: the sixth and final row is the NULL one.")


@reg
def nulls_last_asc(rng):
    t = _t(rng, 6, null_g=1)
    rows = order2(t.rows, (_g, False, "last"), (_s, False))
    _need_unique(t.rows, _g, _s)
    return sql_item([t], "SELECT n FROM t ORDER BY g NULLS LAST, s LIMIT 1;", rows[0][N], "NULLS LAST moves the NULL row to the end, so the smallest real g leads.")


@reg
def nulls_first_desc(rng):
    t = _t(rng, 6, null_g=1)
    rows = order2(t.rows, (_g, True, "first"), (_s, False))
    _need_unique(t.rows, _g, _s)
    return sql_item([t], "SELECT n FROM t ORDER BY g DESC NULLS FIRST, s LIMIT 1;", rows[0][N], "Descending would put NULL last; NULLS FIRST overrides that.")


@reg
def nulls_last_offset(rng):
    t = _t(rng, 6, null_g=1)
    k = rng.randint(3, 5)
    rows = order2(t.rows, (_g, False, "last"), (_s, True))
    _need_unique(t.rows, _g, _s)
    return sql_item([t], f"SELECT n FROM t ORDER BY g NULLS LAST, s DESC LIMIT 1 OFFSET {k};", rows[k][N], "Real groups first with s falling, the NULL group at the very end.")


@reg
def null_second_key(rng):
    t = _t(rng, 6, null_s=1)
    rows = order2(t.rows, (_g, False), (_s, False))
    _need_unique(t.rows, _g, _s)
    k = rng.randint(0, 2)
    return sql_item([t], f"SELECT n FROM t ORDER BY g, s LIMIT 1 OFFSET {k};", rows[k][N], "A NULL s sorts first inside its own g.")


@reg
def null_second_key_desc(rng):
    t = _t(rng, 6, null_s=1)
    rows = order2(t.rows, (_g, False), (_s, True))
    _need_unique(t.rows, _g, _s)
    k = rng.randint(0, 2)
    return sql_item([t], f"SELECT n FROM t ORDER BY g, s DESC LIMIT 1 OFFSET {k};", rows[k][N], "With s descending, a NULL s sorts last inside its g.")


@reg
def null_value_returned(rng):
    t = _t(rng, 5, null_s=1)
    return sql_item([t], "SELECT s FROM t ORDER BY s LIMIT 1;", NULL, "The smallest 'value' is the NULL: it comes out first.")


@reg
def null_count_first_three(rng):
    t = _t(rng, 6, null_g=2)
    rows = order2(t.rows, (_g, False))
    n = sum(1 for r in rows[:3] if r[G] is None)
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT g FROM t ORDER BY g LIMIT 3) WHERE g IS NULL;", n, "NULLs fill the first places of an ascending order.")


# ── LIMIT, OFFSET and DISTINCT ──────────────────────────────────────────

@reg
def limit_comma(rng):
    t = _t(rng)
    k = rng.randint(1, 3)
    rows = order2(t.rows, (_g, False), (_s, False))
    return sql_item([t], f"SELECT n FROM t ORDER BY g, s LIMIT {k}, 1;", rows[k][N], "LIMIT a, b means OFFSET a, LIMIT b: the first number is the rows skipped.")


@reg
def limit_minus_one(rng):
    t = _t(rng)
    k = rng.randint(2, 4)
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT n FROM t ORDER BY g, s LIMIT -1 OFFSET {k});", len(t.rows) - k, "A negative LIMIT means no limit: everything after the skipped rows.")


@reg
def offset_median(rng):
    t = _t(rng, 5)
    _need_unique(t.rows, _s)
    rows = order2(t.rows, (_s, False))
    return sql_item([t], "SELECT s FROM t ORDER BY s LIMIT 1 OFFSET (SELECT COUNT(*) / 2 FROM t);", rows[2][S], "Five rows: skip COUNT(*) / 2 = 2 and take the next one: the middle value.")


@reg
def distinct_g_desc(rng):
    t = _t(rng, 7, unique_gs=False)
    gs = sorted({r[G] for r in t.rows}, reverse=True)
    if len(gs) < 2:
        raise Retry
    return sql_item([t], "SELECT DISTINCT g FROM t ORDER BY g DESC LIMIT 1 OFFSET 1;", gs[1], "DISTINCT first, so the second row is the second DIFFERENT g, not a repeat.")


@reg
def distinct_pairs_count(rng):
    t = _t(rng, 7, tied_s=True, unique_gs=False)
    k = rng.randint(1, 3)
    pairs = sorted({(r[G], r[S]) for r in t.rows})
    n = len(pairs[k:])
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT DISTINCT g, s FROM t ORDER BY g, s LIMIT -1 OFFSET {k});", n, "The different (g, s) pairs in order, minus the skipped ones.")


@reg
def distinct_pair_value(rng):
    t = _t(rng, 7, tied_s=True, unique_gs=False)
    pairs = sorted({(r[G], r[S]) for r in t.rows})
    k = rng.randint(1, min(3, len(pairs) - 1))
    return sql_item([t], f"SELECT s FROM (SELECT DISTINCT g, s FROM t) ORDER BY g, s LIMIT 1 OFFSET {k};", pairs[k][1], "The k-th different pair in order; we read its s.")


# ── Ordering by something else ──────────────────────────────────────────

@reg
def by_expression_mod(rng):
    t = _t(rng, 6, unique_gs=False)
    _need_unique(t.rows, lambda r: (r[S] % 3, r[S]))
    rows = order2(t.rows, (lambda r: r[S] % 3, False), (_s, False))
    k = rng.randint(0, 2)
    return sql_item([t], f"SELECT n FROM t ORDER BY s % 3, s LIMIT 1 OFFSET {k};", rows[k][N], "First the remainder after dividing by 3, then s itself.")


@reg
def by_distance(rng):
    t = _t(rng, 6, unique_gs=False)
    c = rng.randint(3, 7)
    _need_unique(t.rows, lambda r: (abs(r[S] - c), r[S]))
    rows = order2(t.rows, (lambda r: abs(r[S] - c), False), (_s, False))
    return sql_item([t], f"SELECT n FROM t ORDER BY ABS(s - {c}), s LIMIT 1;", rows[0][N], f"The row whose s is closest to {c}; on a tie the smaller s wins.")


@reg
def by_case_priority(rng):
    t = _t(rng, 6)
    pri = rng.randint(1, 3)
    rows = order2(t.rows, (lambda r: 0 if r[G] == pri else 1, False), (_s, True))
    k = rng.randint(0, 2)
    return sql_item([t], f"SELECT n FROM t ORDER BY CASE WHEN g = {pri} THEN 0 ELSE 1 END, s DESC LIMIT 1 OFFSET {k};", rows[k][N], f"CASE puts group {pri} first; inside each part the biggest s leads.")


@reg
def by_position(rng):
    t = _t(rng, 6)
    k = rng.randint(0, 2)
    return sql_item([t], f"SELECT s * 10 + g FROM t ORDER BY 1 LIMIT 1 OFFSET {k};", sorted(r[S] * 10 + r[G] for r in t.rows)[k], "ORDER BY 1 sorts by the first column of the result, here s * 10 + g.")


@reg
def by_name_length(rng):
    names = rng.sample(["fig", "kiwi", "plum", "apple", "grape", "lime", "melon", "peach", "pear", "date"], 5)
    t = Tbl("t", [("w", "TEXT")], [(w,) for w in names])
    rows = sorted(names, key=lambda w: (len(w), w))
    k = rng.randint(0, 3)
    return sql_item([t], f"SELECT w FROM t ORDER BY LENGTH(w), w LIMIT 1 OFFSET {k};", rows[k], "Shortest word first; words of the same length go alphabetically.")


@reg
def by_name_length_desc(rng):
    names = rng.sample(["fig", "kiwi", "plum", "apple", "grape", "lime", "melon", "peach", "pear", "date"], 5)
    t = Tbl("t", [("w", "TEXT")], [(w,) for w in names])
    rows = sorted(sorted(names), key=lambda w: -len(w))
    k = rng.randint(0, 3)
    return sql_item([t], f"SELECT w FROM t ORDER BY LENGTH(w) DESC, w LIMIT 1 OFFSET {k};", rows[k], "Longest first; the same lengths still go alphabetically (a stays ascending).")


@reg
def by_case_text(rng):
    names = rng.sample(["fig", "Fig", "kiwi", "Kiwi", "plum", "Plum", "date", "Lime"], 5)
    t = Tbl("t", [("w", "TEXT")], [(w,) for w in names])
    k = rng.randint(0, 2)
    return sql_item([t], f"SELECT w FROM t ORDER BY w LIMIT 1 OFFSET {k};", sorted(names)[k], "Text sorts by character code: every capital letter comes before every lower-case one.")


@reg
def by_case_text_nocase(rng):
    names = rng.sample(["fig", "Date", "kiwi", "Kiwi", "plum", "Plum", "date", "Lime", "lime"], 5)
    if len({w.lower() for w in names}) != 5:
        raise Retry
    t = Tbl("t", [("w", "TEXT")], [(w,) for w in names])
    k = rng.randint(0, 2)
    return sql_item([t], f"SELECT w FROM t ORDER BY w COLLATE NOCASE LIMIT 1 OFFSET {k};", sorted(names, key=str.lower)[k], "NOCASE ignores the letter case when sorting.")


# ── Aggregates in ORDER BY ──────────────────────────────────────────────

def _groups(t: Tbl) -> dict:
    out: dict = {}
    for r in t.rows:
        out.setdefault(r[G], []).append(r)
    return out


@reg
def groups_by_sum(rng):
    t = _t(rng, 7, unique_gs=False)
    gs = _groups(t)
    sums = {g: sum(r[S] for r in v) for g, v in gs.items()}
    order = sorted(gs, key=lambda g: (-sums[g], g))
    return sql_item([t], "SELECT g FROM t GROUP BY g ORDER BY SUM(s) DESC, g LIMIT 1;", order[0], "Groups ranked by their total; a tie in the total would be broken by g.")


@reg
def groups_by_count_tie(rng):
    t = _t(rng, 6, unique_gs=False)
    gs = _groups(t)
    order = sorted(gs, key=lambda g: (-len(gs[g]), -g))
    return sql_item([t], "SELECT g FROM t GROUP BY g ORDER BY COUNT(*) DESC, g DESC LIMIT 1;", order[0], "The biggest group; if two are the same size, the bigger g comes first.")


@reg
def groups_by_spread(rng):
    t = _t(rng, 7, unique_gs=False)
    gs = _groups(t)
    spread = {g: max(r[S] for r in v) - min(r[S] for r in v) for g, v in gs.items()}
    order = sorted(gs, key=lambda g: (spread[g], g))
    return sql_item([t], "SELECT g FROM t GROUP BY g ORDER BY MAX(s) - MIN(s), g LIMIT 1;", order[0], "The group whose scores are the most alike (smallest spread).")


@reg
def second_group_by_max(rng):
    t = _t(rng, 7, unique_gs=False)
    gs = _groups(t)
    if len(gs) < 2:
        raise Retry
    order = sorted(gs, key=lambda g: (-max(r[S] for r in gs[g]), g))
    return sql_item([t], "SELECT g FROM t GROUP BY g ORDER BY MAX(s) DESC, g LIMIT 1 OFFSET 1;", order[1], "Groups ordered by their best score: the runner-up.")


# ── Window functions over ties ──────────────────────────────────────────

def _pick(rng: random.Random, t: Tbl):
    return rng.choice(t.rows)


@reg
def win_row_number(rng):
    t = _t(rng)
    r = _pick(rng, t)
    rows = order2(t.rows, (_g, False), (_s, True))
    return sql_item([t], f"SELECT rn FROM (SELECT n, ROW_NUMBER() OVER (ORDER BY g, s DESC) rn FROM t) WHERE n = '{r[N]}';", rows.index(r) + 1, "The row's place in the g, s DESC order, counting from 1.")


@reg
def win_rank_ties(rng):
    t = _t(rng, 6, tied_s=True, unique_gs=False)
    r = _pick(rng, t)
    rk = ranks([x[S] for x in t.rows], desc=True)
    return sql_item([t], f"SELECT rk FROM (SELECT n, RANK() OVER (ORDER BY s DESC) rk FROM t) WHERE n = '{r[N]}';", rk[t.rows.index(r)], "Tied rows share a rank, and the next rank skips the places the tie used.")


@reg
def win_dense_rank_ties(rng):
    t = _t(rng, 6, tied_s=True, unique_gs=False)
    r = _pick(rng, t)
    rk = dense_ranks([x[S] for x in t.rows], desc=True)
    return sql_item([t], f"SELECT rk FROM (SELECT n, DENSE_RANK() OVER (ORDER BY s DESC) rk FROM t) WHERE n = '{r[N]}';", rk[t.rows.index(r)], "DENSE_RANK also shares ties but never skips: 1, 1, 2.")


@reg
def win_rank_partition(rng):
    t = _t(rng, 5, tied_s=True, unique_gs=False)
    r = _pick(rng, t)
    mates = [x[S] for x in t.rows if x[G] == r[G]]
    rk = 1 + sum(1 for v in mates if v > r[S])
    return sql_item([t], f"SELECT rk FROM (SELECT n, RANK() OVER (PARTITION BY g ORDER BY s DESC) rk FROM t) WHERE n = '{r[N]}';", rk, "The rank counts only inside the row's own g: one plus the number of bigger scores there.")


@reg
def win_top_two_sum(rng):
    t = _t(rng, 5, unique_gs=True)
    total = 0
    for v in _groups(t).values():
        total += sum(sorted((x[S] for x in v), reverse=True)[:2])
    return sql_item([t], "SELECT SUM(s) FROM (SELECT s, ROW_NUMBER() OVER (PARTITION BY g ORDER BY s DESC) r FROM t) WHERE r <= 2;", total, "Top two per g: number the rows inside each g from the best score, keep numbers 1 and 2, add up.")


@reg
def win_second_in_group(rng):
    t = _t(rng, 4, unique_gs=True)
    gs = _groups(t)
    cands = [g for g, v in gs.items() if len(v) >= 2]
    if not cands:
        raise Retry
    g = rng.choice(cands)
    second = sorted(gs[g], key=lambda r: -r[S])[1]
    return sql_item([t], f"SELECT n FROM (SELECT n, g, RANK() OVER (PARTITION BY g ORDER BY s DESC) r FROM t) WHERE g = {g} AND r = 2;", second[N], "The second best row of that group.")


@reg
def win_winners_with_ties(rng):
    t = _t(rng, 5, tied_s=True, unique_gs=False)
    n = 0
    for v in _groups(t).values():
        top = max(r[S] for r in v)
        n += sum(1 for r in v if r[S] == top)
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT RANK() OVER (PARTITION BY g ORDER BY s DESC) r FROM t) WHERE r = 1;", n, "RANK 1 goes to every row that ties for the best score, so there can be more winners than groups.")


@reg
def win_row_number_winners(rng):
    t = _t(rng, 5, tied_s=True, unique_gs=False)
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT ROW_NUMBER() OVER (PARTITION BY g ORDER BY s DESC) r FROM t) WHERE r = 1;", len(_groups(t)), "ROW_NUMBER never ties: exactly one row per group gets 1.")


@reg
def win_dense_two(rng):
    t = _t(rng, 5, tied_s=True, unique_gs=False)
    n = 0
    for v in _groups(t).values():
        order = sorted({r[S] for r in v}, reverse=True)
        if len(order) >= 2:
            n += sum(1 for r in v if r[S] == order[1])
    if n == 0:
        raise Retry
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT DENSE_RANK() OVER (PARTITION BY g ORDER BY s DESC) r FROM t) WHERE r = 2;", n, "Rows holding each group's second DIFFERENT score (ties included).")


@reg
def win_lag_name(rng):
    t = _t(rng, 6)
    rows = order2(t.rows, (_g, False), (_s, False))
    k = rng.randint(0, len(rows) - 1)
    ans = rows[k - 1][N] if k else NULL
    return sql_item([t], f"SELECT p FROM (SELECT n, LAG(n) OVER (ORDER BY g, s) p FROM t) WHERE n = '{rows[k][N]}';", ans, "LAG looks one row back in the window's order; the first row has nothing before it, so NULL.")


@reg
def win_lead_name(rng):
    t = _t(rng, 6)
    rows = order2(t.rows, (_g, False), (_s, True))
    k = rng.randint(0, len(rows) - 1)
    ans = rows[k + 1][N] if k + 1 < len(rows) else NULL
    return sql_item([t], f"SELECT x FROM (SELECT n, LEAD(n) OVER (ORDER BY g, s DESC) x FROM t) WHERE n = '{rows[k][N]}';", ans, "LEAD looks one row forward; the last row has nothing after it, so NULL.")


@reg
def win_running_total(rng):
    t = _t(rng, 6)
    rows = order2(t.rows, (_g, False), (_s, False))
    k = rng.randint(1, len(rows) - 1)
    return sql_item([t], f"SELECT rt FROM (SELECT n, SUM(s) OVER (ORDER BY g, s) rt FROM t) WHERE n = '{rows[k][N]}';", sum(r[S] for r in rows[:k + 1]), "A running total in the g, s order: this row plus every row before it.")


@reg
def win_first_in_group(rng):
    t = _t(rng, 4)
    r = _pick(rng, t)
    best = max((x for x in t.rows if x[G] == r[G]), key=lambda x: x[S])
    return sql_item([t], f"SELECT f FROM (SELECT n, FIRST_VALUE(n) OVER (PARTITION BY g ORDER BY s DESC) f FROM t) WHERE n = '{r[N]}';", best[N], "FIRST_VALUE is the name of the best-scoring row in the row's own g.")


@reg
def win_count_before(rng):
    t = _t(rng, 6)
    rows = order2(t.rows, (_g, True), (_s, False))
    r = _pick(rng, t)
    return sql_item([t], f"SELECT c FROM (SELECT n, COUNT(*) OVER (ORDER BY g DESC, s) c FROM t) WHERE n = '{r[N]}';", rows.index(r) + 1, "COUNT(*) over an ordered window counts the rows up to and including this one.")
