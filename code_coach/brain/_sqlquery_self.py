"""SQL deeper queries, part 3: Self Join.

One table joined to itself: employee and manager (a boss column pointing at the same table's id), consecutive rows (`b.id =
a.id + 1`), pairs of rows (`a.id < b.id` so each pair is counted once), friends-of-friends, same-city pairs. Every answer is a loop
over pairs (or triples) in Python.
"""

from __future__ import annotations

import random
from typing import Callable

from ._model import Maker
from ._sql_model import Retry, Tbl, fit, sql_item

SELF: list[Maker] = []


def reg(f: Callable) -> Callable:
    SELF.append(fit(f))
    return f


NAMES = ["ann", "bob", "cy", "di", "ed", "flo", "gus", "hal"]


def _emp(rng: random.Random, n: int = 6, dangling: bool = False) -> Tbl:
    """e(id, n, b): employee 1 has no boss; everyone else reports to an earlier employee (one boss id may point nowhere)."""
    names = rng.sample(NAMES, n)
    rows = [(1, names[0], None)]
    for i in range(2, n + 1):
        rows.append((i, names[i - 1], rng.randint(1, i - 1)))
    if dangling:
        k = rng.randrange(1, n)
        rows[k] = (rows[k][0], rows[k][1], 9)
    return Tbl("e", [("id", "INT"), ("n", "TEXT"), ("b", "INT")], rows)


def _emp_ids(rng: random.Random, n: int = 6, dangling: bool = False) -> Tbl:
    """e(id, b): the same shape without names."""
    t = _emp(rng, n, dangling)
    return Tbl("e", [("id", "INT"), ("b", "INT")], [(i, b) for i, _, b in t.rows])


def _emp_sal(rng: random.Random, n: int = 6) -> Tbl:
    t = _emp(rng, n)
    sal = rng.sample(range(1, 10), n)
    return Tbl("e", [("id", "INT"), ("b", "INT"), ("s", "INT")], [(i, b, s) for (i, _, b), s in zip(t.rows, sal)])


def _parent(t: Tbl) -> dict:
    """id -> boss id for any of the e tables."""
    k = t.i("b")
    return {r[0]: r[k] for r in t.rows}


def _pairs_boss(t: Tbl) -> list[tuple]:
    """(employee row, boss row) for every employee whose boss id exists."""
    byid = {r[0]: r for r in t.rows}
    k = t.i("b")
    return [(r, byid[r[k]]) for r in t.rows if r[k] in byid]


# ── Employee and manager ────────────────────────────────────────────────

@reg
def with_a_boss(rng):
    t = _emp_ids(rng, dangling=True)
    return sql_item([t], "SELECT COUNT(*) FROM e JOIN e m ON e.b = m.id;", len(_pairs_boss(t)), "Only employees whose boss id matches a real row survive the join (not the top one, not the dangling one).")


@reg
def boss_name(rng):
    t = _emp(rng, 5)
    r, m = rng.choice(_pairs_boss(t))
    return sql_item([t], f"SELECT m.n FROM e JOIN e m ON e.b = m.id WHERE e.n = '{r[1]}';", m[1], "The second copy of the table (m) is the manager: the row whose id is this employee's boss.")


@reg
def boss_arrow(rng):
    t = _emp(rng, 5)
    r, m = rng.choice(_pairs_boss(t))
    return sql_item([t], f"SELECT e.n || '>' || m.n FROM e JOIN e m ON e.b = m.id WHERE e.id = {r[0]};", f"{r[1]}>{m[1]}", "Employee name, an arrow, then the boss's name.")


@reg
def reports_of(rng):
    t = _emp(rng, 6)
    m = rng.choice(t.rows)
    n = sum(1 for _, bm in _pairs_boss(t) if bm[0] == m[0])
    return sql_item([t], f"SELECT COUNT(*) FROM e JOIN e m ON e.b = m.id WHERE m.n = '{m[1]}';", n, "The joined rows whose manager is this person: one per direct report.")


@reg
def most_reports(rng):
    t = _emp(rng, 6)
    counts: dict = {}
    for _, bm in _pairs_boss(t):
        counts[bm[1]] = counts.get(bm[1], 0) + 1
    best = max(counts.values())
    top = [n for n, c in counts.items() if c == best]
    if len(top) != 1:
        raise Retry
    return sql_item([t], "SELECT m.n FROM e JOIN e m ON e.b = m.id GROUP BY m.id ORDER BY COUNT(*) DESC LIMIT 1;", top[0], "Group the joined rows by manager: the biggest group is the boss with the most reports.")


@reg
def no_reports(rng):
    t = _emp_ids(rng)
    bosses = {b for _, b in t.rows if b is not None}
    return sql_item([t], "SELECT COUNT(*) FROM e m LEFT JOIN e r ON r.b = m.id WHERE r.id IS NULL;", sum(1 for i, _ in t.rows if i not in bosses), "A LEFT JOIN keeps a manager with no report, with NULLs on the r side: those are the people who manage nobody.")


@reg
def grandboss_name(rng):
    t = _emp(rng, 6)
    byid = {r[0]: r for r in t.rows}
    cands = [(r, byid[r[2]], byid[byid[r[2]][2]]) for r in t.rows if r[2] in byid and byid[r[2]][2] in byid]
    if not cands:
        raise Retry
    r, m, g = rng.choice(cands)
    return sql_item([t], f"SELECT g.n FROM e JOIN e m ON e.b = m.id JOIN e g ON m.b = g.id WHERE e.n = '{r[1]}';", g[1], "Two joins: employee to manager, then manager to that manager's manager.")


@reg
def grandboss_rows(rng):
    t = _emp_ids(rng)
    p = _parent(t)
    n = sum(1 for i in p if p[i] in p and p[p[i]] in p)
    return sql_item([t], "SELECT COUNT(*) FROM e JOIN e m ON e.b = m.id JOIN e g ON m.b = g.id;", n, "Counts the employees who have both a boss and a boss's boss.")


@reg
def grandboss_distinct(rng):
    t = _emp_ids(rng, 7)
    p = _parent(t)
    gs = {p[p[i]] for i in p if p[i] in p and p[p[i]] in p}
    if not gs:
        raise Retry
    return sql_item([t], "SELECT COUNT(DISTINCT g.id) FROM e JOIN e m ON e.b = m.id JOIN e g ON m.b = g.id;", len(gs), "Different people who are somebody's boss's boss.")


@reg
def grandchildren(rng):
    t = _emp_ids(rng, 7)
    k = 1
    kids = [i for i, b in t.rows if b == k]
    n = sum(1 for i, b in t.rows if b in kids)
    return sql_item([t], f"SELECT COUNT(*) FROM e a JOIN e c ON c.b = a.id WHERE a.b = {k};", n, "Employees whose boss reports to employee 1: two levels below.")


@reg
def first_report(rng):
    t = _emp(rng, 6)
    m = rng.choice(t.rows)
    kids = sorted(r[1] for r, bm in _pairs_boss(t) if bm[0] == m[0])
    if not kids:
        raise Retry
    return sql_item([t], f"SELECT e.n FROM e JOIN e m ON e.b = m.id WHERE m.n = '{m[1]}' ORDER BY e.n LIMIT 1;", kids[0], "The direct reports of this manager, alphabetically: the first.")


@reg
def siblings_pairs(rng):
    t = _emp_ids(rng, 7)
    n = sum(1 for a in t.rows for c in t.rows if a[1] is not None and a[1] == c[1] and a[0] < c[0])
    return sql_item([t], "SELECT COUNT(*) FROM e a JOIN e c ON a.b = c.b AND a.id < c.id;", n, "Pairs of employees with the same boss; a.id < c.id counts each pair once, and NULL bosses never match.")


@reg
def siblings_ordered(rng):
    t = _emp_ids(rng, 7)
    n = sum(1 for a in t.rows for c in t.rows if a[1] is not None and a[1] == c[1] and a[0] != c[0])
    return sql_item([t], "SELECT COUNT(*) FROM e a JOIN e c ON a.b = c.b AND a.id <> c.id;", n, "<> counts each pair twice (a with c, and c with a).")


@reg
def siblings_with_self(rng):
    t = _emp_ids(rng, 7)
    n = sum(1 for a in t.rows for c in t.rows if a[1] is not None and a[1] == c[1])
    return sql_item([t], "SELECT COUNT(*) FROM e a JOIN e c ON a.b = c.b;", n, "Without a.id <> c.id every employee also pairs with themselves.")


@reg
def richer_than_boss(rng):
    t = _emp_sal(rng)
    n = sum(1 for r, m in _pairs_boss(t) if r[2] > m[2])
    return sql_item([t], "SELECT COUNT(*) FROM e JOIN e m ON e.b = m.id WHERE e.s > m.s;", n, "Compare the employee's s with the manager's s on the same joined row.")


@reg
def sum_boss_pay(rng):
    t = _emp_sal(rng)
    return sql_item([t], "SELECT SUM(m.s) FROM e JOIN e m ON e.b = m.id;", sum(m[2] for _, m in _pairs_boss(t)), "A boss is added once for each report, because there is one joined row per report.")


@reg
def max_pay_gap(rng):
    t = _emp_sal(rng)
    return sql_item([t], "SELECT MAX(m.s - e.s) FROM e JOIN e m ON e.b = m.id;", max(m[2] - r[2] for r, m in _pairs_boss(t)), "The biggest amount a boss earns above a report (can be negative if every report earns more).")


# ── Consecutive rows and pairs of rows ──────────────────────────────────

def _seq(rng: random.Random, n: int = 5, gaps: bool = False, lo: int = 1, hi: int = 9, dup: bool = False) -> Tbl:
    ids = sorted(rng.sample(range(1, n + 3), n)) if gaps else list(range(1, n + 1))
    v = [rng.randint(lo, hi) for _ in ids] if dup else rng.sample(range(lo, hi + 1), n)
    return Tbl("s", [("id", "INT"), ("v", "INT")], list(zip(ids, v)))


def _consec(t: Tbl) -> list[tuple]:
    """(row, next row) for ids that differ by exactly 1."""
    return [(a, b) for a in t.rows for b in t.rows if b[0] == a[0] + 1]


@reg
def rises(rng):
    t = _seq(rng)
    return sql_item([t], "SELECT COUNT(*) FROM s a JOIN s b ON b.id = a.id + 1 WHERE b.v > a.v;", sum(1 for a, b in _consec(t) if b[1] > a[1]), "Each row is paired with the next one: count the steps that go up.")


@reg
def falls(rng):
    t = _seq(rng)
    return sql_item([t], "SELECT COUNT(*) FROM s a JOIN s b ON b.id = a.id + 1 WHERE b.v < a.v;", sum(1 for a, b in _consec(t) if b[1] < a[1]), "Each row is paired with the next one: count the steps that go down.")


@reg
def telescoping(rng):
    t = _seq(rng)
    return sql_item([t], "SELECT SUM(b.v - a.v) FROM s a JOIN s b ON b.id = a.id + 1;", t.rows[-1][1] - t.rows[0][1], "The steps cancel out: the total is last v minus first v.")


@reg
def biggest_jump(rng):
    t = _seq(rng)
    return sql_item([t], "SELECT MAX(b.v - a.v) FROM s a JOIN s b ON b.id = a.id + 1;", max(b[1] - a[1] for a, b in _consec(t)), "The largest single step from one row to the next.")


@reg
def biggest_drop(rng):
    t = _seq(rng)
    return sql_item([t], "SELECT MIN(b.v - a.v) FROM s a JOIN s b ON b.id = a.id + 1;", min(b[1] - a[1] for a, b in _consec(t)), "The most negative step: the biggest fall.")


@reg
def previous_value(rng):
    t = _seq(rng)
    k = rng.randint(2, len(t.rows))
    a = t.rows[k - 2]
    return sql_item([t], f"SELECT a.v FROM s a JOIN s b ON a.id = b.id - 1 WHERE b.id = {k};", a[1], "Row a is the one just before row b: id one lower.")


@reg
def next_value(rng):
    t = _seq(rng)
    k = rng.randint(1, len(t.rows) - 1)
    return sql_item([t], f"SELECT b.v FROM s a JOIN s b ON b.id = a.id + 1 WHERE a.id = {k};", t.rows[k][1], "Row b is the one just after row a.")


@reg
def running_total(rng):
    t = _seq(rng)
    k = rng.randint(2, len(t.rows))
    return sql_item([t], f"SELECT SUM(b.v) FROM s a JOIN s b ON b.id <= a.id WHERE a.id = {k};", sum(v for i, v in t.rows if i <= k), "For row a, b ranges over every row up to it: a running total.")


@reg
def run_ends(rng):
    t = _seq(rng, 5, gaps=True)
    ids = {i for i, _ in t.rows}
    return sql_item([t], "SELECT COUNT(*) FROM s a LEFT JOIN s b ON b.id = a.id + 1 WHERE b.id IS NULL;", sum(1 for i in ids if i + 1 not in ids), "Rows whose next id is missing: where a run of consecutive ids ends (the last row too).")


@reg
def gap_total(rng):
    t = _seq(rng, 5, gaps=True)
    ids = [i for i, _ in t.rows]
    n = sum(1 for i in ids for j in ids if j == i + 1)
    return sql_item([t], "SELECT COUNT(*) FROM s a JOIN s b ON b.id = a.id + 1;", n, "How many neighbouring id pairs exist (a gap in the ids breaks the chain).")


@reg
def total_pairs_even(rng):
    t = _seq(rng, 5, dup=True)
    n = sum(1 for a in t.rows for b in t.rows if a[0] < b[0] and (a[1] + b[1]) % 2 == 0)
    return sql_item([t], "SELECT COUNT(*) FROM s a JOIN s b ON a.id < b.id WHERE (a.v + b.v) % 2 = 0;", n, "Every pair of different rows once, kept when the two values add to an even number.")


@reg
def equal_pairs(rng):
    t = _seq(rng, 6, dup=True, hi=5)
    n = sum(1 for a in t.rows for b in t.rows if a[0] < b[0] and a[1] == b[1])
    return sql_item([t], "SELECT COUNT(*) FROM s a JOIN s b ON a.v = b.v AND a.id < b.id;", n, "Pairs of rows holding the same v: three equal values make three pairs.")


@reg
def dup_values(rng):
    t = _seq(rng, 6, dup=True, hi=5)
    n = len({a[1] for a in t.rows for b in t.rows if a[0] < b[0] and a[1] == b[1]})
    return sql_item([t], "SELECT COUNT(DISTINCT a.v) FROM s a JOIN s b ON a.v = b.v AND a.id < b.id;", n, "The different values that appear in some pair: the values that repeat.")


@reg
def ascending_pairs(rng):
    t = _seq(rng)
    n = sum(1 for a in t.rows for b in t.rows if a[0] < b[0] and a[1] < b[1])
    return sql_item([t], "SELECT COUNT(*) FROM s a JOIN s b ON a.id < b.id WHERE a.v < b.v;", n, "Pairs where the later row has the bigger v.")


@reg
def inversions(rng):
    t = _seq(rng)
    n = sum(1 for a in t.rows for b in t.rows if a[0] < b[0] and a[1] > b[1])
    return sql_item([t], "SELECT COUNT(*) FROM s a JOIN s b ON a.id < b.id WHERE a.v > b.v;", n, "Pairs that are out of order: an earlier row with the bigger v. (A sorted table has none.)")


@reg
def pair_sum_target(rng):
    t = _seq(rng, 6)
    k = rng.randint(6, 14)
    n = sum(1 for a in t.rows for b in t.rows if a[0] < b[0] and a[1] + b[1] == k)
    return sql_item([t], f"SELECT COUNT(*) FROM s a JOIN s b ON a.id < b.id WHERE a.v + b.v = {k};", n, "Pairs of different rows whose values add up to the target.")


@reg
def pair_diff_one(rng):
    t = _seq(rng, 6)
    n = sum(1 for a in t.rows for b in t.rows if a[0] < b[0] and abs(a[1] - b[1]) == 1)
    return sql_item([t], "SELECT COUNT(*) FROM s a JOIN s b ON a.id < b.id WHERE ABS(a.v - b.v) = 1;", n, "Pairs whose values are neighbours on the number line.")


@reg
def biggest_pair_sum(rng):
    t = _seq(rng, 6)
    n = max(a[1] + b[1] for a in t.rows for b in t.rows if a[0] < b[0])
    return sql_item([t], "SELECT MAX(a.v + b.v) FROM s a JOIN s b ON a.id < b.id;", n, "The two biggest values added: the best pair of different rows.")


@reg
def closest_pair(rng):
    t = _seq(rng, 6, dup=True, hi=12)
    n = min(abs(a[1] - b[1]) for a in t.rows for b in t.rows if a[0] < b[0])
    return sql_item([t], "SELECT MIN(ABS(a.v - b.v)) FROM s a JOIN s b ON a.id < b.id;", n, "The smallest difference between any two rows (0 if a value repeats).")


@reg
def has_bigger(rng):
    t = _seq(rng, 6, dup=True, hi=5)
    n = len({a[0] for a in t.rows for b in t.rows if b[1] > a[1]})
    return sql_item([t], "SELECT COUNT(DISTINCT a.id) FROM s a JOIN s b ON b.v > a.v;", n, "Rows that have some bigger row: everyone except the rows holding the maximum.")


@reg
def has_no_smaller(rng):
    t = _seq(rng, 6, dup=True, hi=5)
    n = sum(1 for a in t.rows if not any(b[1] < a[1] for b in t.rows))
    return sql_item([t], "SELECT COUNT(*) FROM s a LEFT JOIN s b ON b.v < a.v WHERE b.id IS NULL;", n, "Rows with no smaller row: the rows that hold the minimum (ties all count).")


@reg
def bigger_than_row(rng):
    t = _seq(rng, 6)
    k = rng.choice(t.rows)
    n = sum(1 for b in t.rows if b[1] > k[1])
    return sql_item([t], f"SELECT COUNT(*) FROM s a JOIN s b ON b.v > a.v WHERE a.id = {k[0]};", n, "How many rows have a bigger v than row a: its place from the top, minus one.")


@reg
def ordered_cross(rng):
    t = _seq(rng, 5, dup=True, hi=6)
    n = sum(1 for a in t.rows for b in t.rows if a[1] < b[1])
    return sql_item([t], "SELECT COUNT(*) FROM s a JOIN s b ON a.v < b.v;", n, "Every ordered pair of rows, with no id test: rows can be paired with equal-valued rows too, but < drops those.")


@reg
def increasing_triples(rng):
    t = _seq(rng, 5)
    n = sum(1 for a in t.rows for b in t.rows for c in t.rows if a[0] < b[0] < c[0] and a[1] < b[1] < c[1])
    return sql_item([t], "SELECT COUNT(*) FROM s a JOIN s b ON a.id < b.id JOIN s c ON b.id < c.id WHERE a.v < b.v AND b.v < c.v;", n, "Three rows in id order whose values keep rising.")


# ── Graphs and groups ───────────────────────────────────────────────────

def _edges(rng: random.Random, n: int = 6, people: int = 4) -> Tbl:
    allp = [(a, b) for a in range(1, people + 1) for b in range(1, people + 1) if a != b]
    return Tbl("f", [("a", "INT"), ("b", "INT")], rng.sample(allp, n))


@reg
def mutual_pairs(rng):
    t = _edges(rng, 7)
    n = sum(1 for x in t.rows for y in t.rows if x[0] == y[1] and x[1] == y[0] and x[0] < x[1])
    return sql_item([t], "SELECT COUNT(*) FROM f x JOIN f y ON x.a = y.b AND x.b = y.a WHERE x.a < x.b;", n, "Two people who point at each other; x.a < x.b counts each mutual pair once.")


@reg
def two_hop(rng):
    t = _edges(rng, 6)
    n = sum(1 for x in t.rows for y in t.rows if x[1] == y[0] and x[0] != y[1])
    return sql_item([t], "SELECT COUNT(*) FROM f x JOIN f y ON x.b = y.a WHERE x.a <> y.b;", n, "Paths a -> b -> c where c is not a again.")


@reg
def two_hop_back(rng):
    t = _edges(rng, 6)
    n = sum(1 for x in t.rows for y in t.rows if x[1] == y[0] and x[0] == y[1])
    return sql_item([t], "SELECT COUNT(*) FROM f x JOIN f y ON x.b = y.a WHERE x.a = y.b;", n, "Paths that come back to where they started: each mutual pair gives two.")


@reg
def two_hop_distinct(rng):
    t = _edges(rng, 6)
    n = len({(x[0], y[1]) for x in t.rows for y in t.rows if x[1] == y[0] and x[0] != y[1]})
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT DISTINCT x.a, y.b FROM f x JOIN f y ON x.b = y.a WHERE x.a <> y.b);", n, "Different (start, end) pairs that some two-step path connects.")


def _people(rng: random.Random, n: int = 5) -> Tbl:
    names = rng.sample(NAMES, n)
    cities = [rng.choice(["ny", "la", "sf"]) for _ in range(n)]
    return Tbl("p", [("n", "TEXT"), ("c", "TEXT")], list(zip(names, cities)))


@reg
def same_city_pairs(rng):
    t = _people(rng)
    n = sum(1 for a in t.rows for b in t.rows if a[1] == b[1] and a[0] < b[0])
    return sql_item([t], "SELECT COUNT(*) FROM p a JOIN p b ON a.c = b.c AND a.n < b.n;", n, "Pairs of different people from the same city; a.n < b.n counts each pair once.")


@reg
def other_city_pairs(rng):
    t = _people(rng)
    n = sum(1 for a in t.rows for b in t.rows if a[1] != b[1] and a[0] < b[0])
    return sql_item([t], "SELECT COUNT(*) FROM p a JOIN p b ON a.c <> b.c AND a.n < b.n;", n, "Pairs from different cities, each pair once.")


@reg
def first_pair_names(rng):
    t = _people(rng)
    pairs = sorted((a[0], b[0]) for a in t.rows for b in t.rows if a[1] == b[1] and a[0] < b[0])
    if not pairs:
        raise Retry
    return sql_item([t], "SELECT a.n || b.n FROM p a JOIN p b ON a.c = b.c AND a.n < b.n ORDER BY a.n, b.n LIMIT 1;", pairs[0][0] + pairs[0][1], "The first same-city pair in alphabetical order, the two names side by side.")


@reg
def lonely_city(rng):
    t = _people(rng, 5)
    n = sum(1 for a in t.rows if not any(b[1] == a[1] and b[0] != a[0] for b in t.rows))
    return sql_item([t], "SELECT COUNT(*) FROM p a LEFT JOIN p b ON a.c = b.c AND a.n <> b.n WHERE b.n IS NULL;", n, "People with no one else in their city: the LEFT JOIN finds no partner.")


@reg
def city_mates_of(rng):
    t = _people(rng, 5)
    k = rng.choice(t.rows)
    n = sum(1 for b in t.rows if b[1] == k[1] and b[0] != k[0])
    return sql_item([t], f"SELECT COUNT(*) FROM p a JOIN p b ON a.c = b.c AND a.n <> b.n WHERE a.n = '{k[0]}';", n, "How many other people live in this person's city.")
