"""SQL deeper queries, part 4: Subquery Value.

Subqueries everywhere - in SELECT, in FROM (derived tables), in WHERE, nested, correlated: scalar subquery comparisons, `IN` and
`EXISTS` with NULLs and with empty results, row values, "above its own group's average", second and third highest, customers and
orders. A subquery is a loop over rows in the Python model.
"""

from __future__ import annotations

import random
from typing import Callable

from ._model import Maker, tdiv
from ._sql_model import (NULL, Retry, Tbl, avg_, fit, gt, in_list, sql_item, sql_round,
                         sum_, with_nulls)

SUB: list[Maker] = []


def reg(f: Callable) -> Callable:
    SUB.append(fit(f))
    return f


def _t(rng: random.Random, n: int = 6, nulls: int = 0, lo: int = 1, hi: int = 12, uniq: bool = True) -> Tbl:
    v = rng.sample(range(lo, hi + 1), n) if uniq else [rng.randint(lo, hi) for _ in range(n)]
    if nulls:
        v = with_nulls(rng, v, nulls)
    return Tbl("t", [("a", "INT")], [(x,) for x in v])


def _u(rng: random.Random, n: int = 3, nulls: int = 0, lo: int = 1, hi: int = 12) -> Tbl:
    v = rng.sample(range(lo, hi + 1), n)
    if nulls:
        v = with_nulls(rng, v, nulls)
    return Tbl("u", [("x", "INT")], [(x,) for x in v])


def _e(rng: random.Random, n: int = 6) -> Tbl:
    """e(d, s): a department letter and a salary, every salary different."""
    s = rng.sample(range(1, 13), n)
    d = [rng.choice("xyz") for _ in range(n)]
    if len(set(d)) < 2:
        raise Retry
    return Tbl("e", [("d", "TEXT"), ("s", "INT")], list(zip(d, s)))


def _co(rng: random.Random, n_orders: int = 4) -> tuple[Tbl, Tbl]:
    """c(id): customers 1-3, o(c, v): orders with different amounts; some customers have none, one order may be a stranger's (customer 4)."""
    c = Tbl("c", [("id", "INT")], [(i,) for i in range(1, 4)])
    amts = rng.sample(range(1, 10), n_orders)
    owners = [rng.choice([1, 1, 2, 3, 4]) for _ in range(n_orders)]
    return c, Tbl("o", [("c", "INT"), ("v", "INT")], list(zip(owners, amts)))


def A(t: Tbl) -> list:
    return t.col("a")


# ── Scalar subqueries ───────────────────────────────────────────────────

@reg
def minus_min(rng):
    t = _t(rng)
    k = rng.choice(A(t))
    return sql_item([t], f"SELECT a - (SELECT MIN(a) FROM t) FROM t WHERE a = {k};", k - min(A(t)), "The subquery in the SELECT list is one value: the smallest a.")


@reg
def share_percent(rng):
    t = _t(rng, 5, hi=9)
    k = rng.choice(A(t))
    return sql_item([t], f"SELECT a * 100 / (SELECT SUM(a) FROM t) FROM t WHERE a = {k};", tdiv(k * 100, sum(A(t))), "Integer division: the share of the total, as a whole percent.")


@reg
def range_two_subs(rng):
    t = _t(rng)
    return sql_item([t], "SELECT (SELECT MAX(a) FROM t) - (SELECT MIN(a) FROM t);", max(A(t)) - min(A(t)), "Two scalar subqueries, each one value, then subtracted.")


@reg
def empty_scalar(rng):
    t = _t(rng)
    return sql_item([t], "SELECT COALESCE((SELECT a FROM t WHERE a > 99), -1);", -1, "A scalar subquery that finds no row is NULL, so COALESCE gives -1.")


@reg
def first_row_scalar(rng):
    t = _t(rng)
    return sql_item([t], "SELECT (SELECT a FROM t ORDER BY a DESC);", max(A(t)), "A scalar subquery returning several rows gives the FIRST one in SQLite: the biggest here.")


@reg
def count_above_max(rng):
    t, u = _t(rng), _u(rng)
    m = max(u.col("x"))
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE a > (SELECT MAX(x) FROM u);", sum(1 for a in A(t) if a > m), "Rows of t above the biggest x.")


@reg
def count_equal_min(rng):
    t = _t(rng, 6, hi=5, uniq=False)
    u = _u(rng, 3, hi=5)
    m = min(u.col("x"))
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE a = (SELECT MIN(x) FROM u);", sum(1 for a in A(t) if a == m), "How many rows of t equal the smallest x.")


@reg
def count_between_subs(rng):
    t, u = _t(rng, 7), _u(rng, 3)
    lo, hi = min(u.col("x")), max(u.col("x"))
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE a BETWEEN (SELECT MIN(x) FROM u) AND (SELECT MAX(x) FROM u);", sum(1 for a in A(t) if lo <= a <= hi), "BETWEEN with two scalar subqueries as its ends (the ends count).")


@reg
def above_real_avg(rng):
    t, u = _t(rng), _u(rng, 4)
    m = avg_(u.col("x"))
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE a > (SELECT AVG(x) FROM u);", sum(1 for a in A(t) if a > m), "AVG is a real (it may have a fraction): rows above it.")


@reg
def smallest_above_avg(rng):
    t = _t(rng)
    m = avg_(A(t))
    return sql_item([t], "SELECT a FROM t WHERE a > (SELECT AVG(a) FROM t) ORDER BY a LIMIT 1;", min(a for a in A(t) if a > m), "The rows above average, in order: the first is the smallest of them.")


@reg
def biggest_below_avg(rng):
    t = _t(rng)
    m = avg_(A(t))
    return sql_item([t], "SELECT MAX(a) FROM t WHERE a < (SELECT AVG(a) FROM t);", max(a for a in A(t) if a < m), "The biggest value that is still under the average.")


@reg
def nested_avg(rng):
    t = _t(rng, 6)
    top = max(A(t))
    m = avg_([a for a in A(t) if a < top])
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE a > (SELECT AVG(a) FROM t WHERE a < (SELECT MAX(a) FROM t));", sum(1 for a in A(t) if a > m), "Innermost first: the max, then the average of everything below it, then the rows above that average.")


@reg
def second_highest(rng):
    t = _t(rng)
    return sql_item([t], "SELECT MAX(a) FROM t WHERE a < (SELECT MAX(a) FROM t);", sorted(A(t))[-2], "The biggest value below the biggest: the second highest.")


@reg
def third_highest(rng):
    t = _t(rng)
    return sql_item([t], "SELECT MAX(a) FROM t WHERE a < (SELECT MAX(a) FROM t WHERE a < (SELECT MAX(a) FROM t));", sorted(A(t))[-3], "Two levels of 'below the biggest': the third highest.")


@reg
def in_limit(rng):
    t, u = _t(rng, 6), _u(rng, 4)
    top = sorted(u.col("x"), reverse=True)[:2]
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE a IN (SELECT x FROM u ORDER BY x DESC LIMIT 2);", sum(1 for a in A(t) if a in top), "The subquery is the two biggest x; the rows of t that equal one of them.")


# ── IN, NOT IN and EXISTS: NULLs and empty results ──────────────────────

@reg
def in_with_null(rng):
    t = _t(rng, 6, hi=8)
    u = _u(rng, 4, nulls=1, hi=8)
    xs = u.col("x")
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE a IN (SELECT x FROM u);", sum(1 for a in A(t) if in_list(a, xs) is True), "A NULL in the list does not hurt IN: matching rows are still found.")


@reg
def not_in_without_null(rng):
    t = _t(rng, 6, hi=8)
    u = _u(rng, 4, nulls=1, hi=8)
    xs = [x for x in u.col("x") if x is not None]
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE a NOT IN (SELECT x FROM u WHERE x IS NOT NULL);", sum(1 for a in A(t) if a not in xs), "Filtering the NULL out of the subquery makes NOT IN work as expected.")


@reg
def not_in_empty_with_null_row(rng):
    t = _t(rng, 5, nulls=1)
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE a NOT IN (SELECT a FROM t WHERE a > 99);", len(t.rows), "NOT IN an empty list is true for every row, even the one where a is NULL.")


@reg
def in_empty(rng):
    t = _t(rng, 5, nulls=1)
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE a IN (SELECT a FROM t WHERE a > 99);", 0, "IN an empty list is false for every row.")


@reg
def exists_with_nulls(rng):
    t = _t(rng, 6, nulls=1, hi=8)
    u = _u(rng, 4, nulls=1, hi=8)
    xs = u.col("x")
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE EXISTS (SELECT 1 FROM u WHERE u.x = t.a);", sum(1 for a in A(t) if a is not None and a in xs), "NULL never equals anything, so the NULL rows find no match.")


@reg
def not_exists_nulls(rng):
    t = _t(rng, 6, nulls=1, hi=8)
    u = _u(rng, 4, hi=8)
    xs = u.col("x")
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE NOT EXISTS (SELECT 1 FROM u WHERE u.x = t.a);", sum(1 for a in A(t) if a is None or a not in xs), "The NULL row finds no equal x, so NOT EXISTS is true for it: it is counted.")


@reg
def not_exists_bigger(rng):
    t, u = _t(rng), _u(rng, 3)
    xs = u.col("x")
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE NOT EXISTS (SELECT 1 FROM u WHERE u.x > t.a);", sum(1 for a in A(t) if not any(x > a for x in xs)), "Rows with no bigger x: the rows at or above the biggest x.")


@reg
def row_value_in(rng):
    def two(name, cols):
        return Tbl(name, cols, [(rng.randint(1, 3), rng.randint(1, 3)) for _ in range(4)])
    t = two("t", [("a", "INT"), ("b", "INT")])
    u = two("u", [("x", "INT"), ("y", "INT")])
    n = sum(1 for r in t.rows if r in u.rows)
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE (a, b) IN (SELECT x, y FROM u);", n, "A pair is compared as a pair: both columns must match the same u row.")


@reg
def in_nested(rng):
    t, u = _t(rng, 6), _u(rng, 4)
    m = avg_(A(t))
    xs = [x for x in u.col("x") if x > m]
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE a IN (SELECT x FROM u WHERE x > (SELECT AVG(a) FROM t));", sum(1 for a in A(t) if a in xs), "The x values above t's average, and then the rows of t among them.")


@reg
def in_vs_exists_sum(rng):
    t, u = _t(rng, 6, hi=8), _u(rng, 3, hi=8)
    xs = u.col("x")
    return sql_item([t, u], "SELECT SUM(a) FROM t WHERE a IN (SELECT x FROM u);", sum_([a for a in A(t) if a in xs]) if any(a in xs for a in A(t)) else NULL, "The sum of the rows that have a match (NULL when none does).")


# ── Correlated subqueries ───────────────────────────────────────────────

@reg
def smaller_count(rng):
    t = _t(rng)
    k = rng.choice(A(t))
    return sql_item([t], f"SELECT (SELECT COUNT(*) FROM t y WHERE y.a < x.a) FROM t x WHERE x.a = {k};", sum(1 for a in A(t) if a < k), "For this row, the subquery counts the rows below it.")


@reg
def sum_of_smaller_counts(rng):
    t = _t(rng, 5)
    n = sum(1 for a in A(t) for b in A(t) if b < a)
    return sql_item([t], "SELECT SUM((SELECT COUNT(*) FROM t y WHERE y.a < x.a)) FROM t x;", n, "Each row counts the rows below it; added together that is the number of ordered pairs.")


@reg
def top_two_rows(rng):
    t = _t(rng, 6)
    n = sum(1 for a in A(t) if sum(1 for b in A(t) if b > a) < 2)
    return sql_item([t], "SELECT COUNT(*) FROM t x WHERE (SELECT COUNT(*) FROM t y WHERE y.a > x.a) < 2;", n, "A row qualifies when fewer than two rows are bigger than it: the top two.")


@reg
def median(rng):
    t = _t(rng, 5)
    return sql_item([t], "SELECT a FROM t x WHERE (SELECT COUNT(*) FROM t y WHERE y.a < x.a) = (SELECT COUNT(*) FROM t y WHERE y.a > x.a);", sorted(A(t))[2], "The middle value has as many rows below it as above it.")


@reg
def above_dept_avg(rng):
    t = _e(rng)
    n = 0
    for d, s in t.rows:
        m = avg_([x for dd, x in t.rows if dd == d])
        n += s > m
    return sql_item([t], "SELECT COUNT(*) FROM e x WHERE s > (SELECT AVG(s) FROM e y WHERE y.d = x.d);", n, "For each row the subquery averages its OWN department; rows above that are counted.")


@reg
def dept_max_rows(rng):
    t = _e(rng)
    n = sum(1 for d, s in t.rows if s == max(x for dd, x in t.rows if dd == d))
    return sql_item([t], "SELECT COUNT(*) FROM e x WHERE s = (SELECT MAX(s) FROM e y WHERE y.d = x.d);", n, "One top earner per department: the count equals the number of departments.")


@reg
def dept_min_sum(rng):
    t = _e(rng)
    n = sum(s for d, s in t.rows if s == min(x for dd, x in t.rows if dd == d))
    return sql_item([t], "SELECT SUM(s) FROM e x WHERE s = (SELECT MIN(s) FROM e y WHERE y.d = x.d);", n, "Add up each department's lowest salary.")


@reg
def crowded_rows(rng):
    t = _e(rng)
    n = sum(1 for d, _ in t.rows if sum(1 for dd, _ in t.rows if dd == d) > 1)
    return sql_item([t], "SELECT COUNT(*) FROM e x WHERE (SELECT COUNT(*) FROM e y WHERE y.d = x.d) > 1;", n, "Rows whose department holds more than one person.")


@reg
def top_earner_dept(rng):
    t = _e(rng)
    m = max(s for _, s in t.rows)
    d = [d for d, s in t.rows if s == m][0]
    return sql_item([t], "SELECT d FROM e WHERE s = (SELECT MAX(s) FROM e);", d, "The department of the row with the biggest salary.")


@reg
def groups_above_overall(rng):
    t = _e(rng)
    overall = avg_([s for _, s in t.rows])
    groups: dict = {}
    for d, s in t.rows:
        groups.setdefault(d, []).append(s)
    n = sum(1 for v in groups.values() if avg_(v) > overall)
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT d FROM e GROUP BY d HAVING AVG(s) > (SELECT AVG(s) FROM e));", n, "A department's average compared with the overall average from a subquery.")


@reg
def avg_of_dept_max(rng):
    t = _e(rng)
    groups: dict = {}
    for d, s in t.rows:
        groups.setdefault(d, []).append(s)
    m = [max(v) for v in groups.values()]
    return sql_item([t], "SELECT ROUND(AVG(m), 2) FROM (SELECT MAX(s) m FROM e GROUP BY d);", sql_round(sum(m) / len(m), 2), "The inner query makes one max per department; the outer averages them.")


@reg
def biggest_dept(rng):
    t = _e(rng, 7)
    groups: dict = {}
    for d, s in t.rows:
        groups.setdefault(d, []).append(s)
    return sql_item([t], "SELECT MAX(c) FROM (SELECT COUNT(*) c FROM e GROUP BY d);", max(len(v) for v in groups.values()), "The size of the biggest department.")


@reg
def distinct_depts_over(rng):
    t = _e(rng)
    k = rng.randint(4, 9)
    n = len({d for d, s in t.rows if s > k})
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT DISTINCT d FROM e WHERE s > {k});", n, "A derived table of the departments that have somebody above the line.")


@reg
def derived_filter(rng):
    t = _t(rng, 7)
    lo, hi = sorted(rng.sample(range(2, 11), 2))
    n = sum(1 for a in A(t) if a > lo and a < hi)
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT a FROM t WHERE a > {lo}) WHERE a < {hi};", n, "The inner query keeps a > lo; the outer one narrows it to a < hi.")


# ── Customers and orders ────────────────────────────────────────────────

@reg
def customers_with_big_order(rng):
    c, o = _co(rng)
    k = rng.randint(3, 7)
    ids = {cc for cc, amt in o.rows if amt > k}
    return sql_item([c, o], f"SELECT COUNT(*) FROM c WHERE EXISTS (SELECT 1 FROM o WHERE o.c = c.id AND v > {k});", sum(1 for (i,) in c.rows if i in ids), "Customers that have at least one order above the line.")


@reg
def customers_without_orders(rng):
    c, o = _co(rng)
    ids = {cc for cc, _ in o.rows}
    return sql_item([c, o], "SELECT COUNT(*) FROM c WHERE NOT EXISTS (SELECT 1 FROM o WHERE o.c = c.id);", sum(1 for (i,) in c.rows if i not in ids), "Customers with no order at all.")


@reg
def customers_big_total(rng):
    c, o = _co(rng)
    k = rng.randint(4, 12)
    tot = lambda i: sum_([amt for cc, amt in o.rows if cc == i])  # noqa: E731
    return sql_item([c, o], f"SELECT COUNT(*) FROM c WHERE (SELECT SUM(v) FROM o WHERE o.c = c.id) > {k};", sum(1 for (i,) in c.rows if gt(tot(i), k) is True), "A customer with no orders has a NULL total, and NULL is not above anything.")


@reg
def total_of_known_customers(rng):
    c, o = _co(rng)
    ids = {i for (i,) in c.rows}
    return sql_item([c, o], "SELECT SUM(COALESCE((SELECT SUM(v) FROM o WHERE o.c = c.id), 0)) FROM c;", sum(amt for cc, amt in o.rows if cc in ids), "Orders of customers that do not exist (customer 4) are never visited.")


@reg
def orders_of_customer(rng):
    c, o = _co(rng)
    k = rng.randint(1, 3)
    return sql_item([c, o], f"SELECT (SELECT COUNT(*) FROM o WHERE o.c = c.id) FROM c WHERE id = {k};", sum(1 for cc, _ in o.rows if cc == k), "A correlated count in the SELECT list: this customer's orders.")


@reg
def customer_of_top_order(rng):
    c, o = _co(rng)
    m = max(amt for _, amt in o.rows)
    return sql_item([c, o], "SELECT c FROM o WHERE v = (SELECT MAX(v) FROM o);", [cc for cc, amt in o.rows if amt == m][0], "The customer id on the single biggest order.")


@reg
def customer_of_top_total(rng):
    _, o = _co(rng)
    tot: dict = {}
    for cc, amt in o.rows:
        tot[cc] = tot.get(cc, 0) + amt
    best = max(tot.values())
    top = [cc for cc, v in tot.items() if v == best]
    if len(top) != 1:
        raise Retry
    return sql_item([o], "SELECT c FROM o GROUP BY c HAVING SUM(v) = (SELECT MAX(s) FROM (SELECT SUM(v) s FROM o GROUP BY c));", top[0], "The inner query makes one total per customer; the HAVING keeps the customer whose total is the biggest.")


@reg
def stranger_orders(rng):
    c, o = _co(rng)
    ids = {i for (i,) in c.rows}
    return sql_item([c, o], "SELECT COUNT(*) FROM o WHERE c NOT IN (SELECT id FROM c);", sum(1 for cc, _ in o.rows if cc not in ids), "Orders whose customer id is not in c: the orphans.")
