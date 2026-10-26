"""SQL deeper queries, part 5: CTE Chain.

`WITH ...` queries: one CTE, several CTEs that read each other, a CTE with a column list or VALUES, a CTE that hides a table of the
same name, and `WITH RECURSIVE` series, countdowns, factorials, Fibonacci, tree walks and graph reachability with small bounds.
The answer is the final value; a recursive CTE is a Python loop (`recursive` in `_sqlquery_model.py`).
"""

from __future__ import annotations

import random
from typing import Callable

from ._model import Maker
from ._sql_model import Retry, Tbl, avg_, fit, sql_round
from ._sql_model import sql_item as _sql_item
from ._sqlquery_model import recursive

CTE: list[Maker] = []


def _break(query: str) -> str:
    """Put the main SELECT of a WITH query on its own (last) line: an item's last line must start with SELECT (the SQL shape
    test), and the CTEs read better above it. The main SELECT is the first one outside every bracket."""
    depth = 0
    for i, ch in enumerate(query):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 0 and query.startswith(" SELECT ", i):
            return query[:i] + chr(10) + query[i + 1:]
    return query


def sql_item(tables, query, answer, why):
    """`_sql_model.sql_item` with the main SELECT of the WITH query moved to its own line."""
    return _sql_item(tables, _break(query), answer, why)


def reg(f: Callable) -> Callable:
    CTE.append(fit(f))
    return f


def _t(rng: random.Random, n: int = 5, lo: int = 1, hi: int = 12) -> Tbl:
    return Tbl("t", [("a", "INT")], [(x,) for x in rng.sample(range(lo, hi + 1), n)])


def _e(rng: random.Random, n: int = 6) -> Tbl:
    s = rng.sample(range(1, 10), n)
    d = [rng.choice("xyz") for _ in range(n)]
    if len(set(d)) < 2:
        raise Retry
    return Tbl("e", [("d", "TEXT"), ("s", "INT")], list(zip(d, s)))


def _o(rng: random.Random, n: int = 6) -> Tbl:
    return Tbl("o", [("c", "INT"), ("v", "INT")], [(rng.randint(1, 3), rng.randint(1, 9)) for _ in range(n)])


def _tree(rng: random.Random, n: int = 6) -> Tbl:
    return Tbl("e", [("id", "INT"), ("b", "INT")], [(1, None)] + [(i, rng.randint(1, i - 1)) for i in range(2, n + 1)])


def A(t: Tbl) -> list:
    return t.col("a")


def _sums(o: Tbl) -> dict:
    out: dict = {}
    for c, v in o.rows:
        out[c] = out.get(c, 0) + v
    return out


# ── Plain CTEs ──────────────────────────────────────────────────────────

@reg
def one_cte_count(rng):
    t = _t(rng)
    k = rng.randint(4, 9)
    return sql_item([t], f"WITH big AS (SELECT a FROM t WHERE a > {k}) SELECT COUNT(*) FROM big;", sum(1 for a in A(t) if a > k), "The CTE is a named subquery: big holds the rows above k, and the query counts them.")


@reg
def one_cte_sum(rng):
    t = _t(rng)
    k = rng.randint(4, 9)
    v = [a for a in A(t) if a <= k]
    if not v:
        raise Retry
    return sql_item([t], f"WITH small AS (SELECT a FROM t WHERE a <= {k}) SELECT SUM(a) FROM small;", sum(v), "Add up the rows the CTE kept.")


@reg
def cte_avg_compare(rng):
    t = _t(rng)
    m = avg_(A(t))
    return sql_item([t], "WITH m AS (SELECT AVG(a) v FROM t) SELECT COUNT(*) FROM t, m WHERE a > m.v;", sum(1 for a in A(t) if a > m), "The CTE m is a one-row table holding the average; joining it lets every row compare with it.")


@reg
def two_ctes_diff(rng):
    t = _t(rng, 6)
    k = rng.randint(4, 9)
    hi = sum(1 for a in A(t) if a > k)
    return sql_item([t], f"WITH hi AS (SELECT a FROM t WHERE a > {k}), lo AS (SELECT a FROM t WHERE a <= {k}) SELECT (SELECT COUNT(*) FROM hi) - (SELECT COUNT(*) FROM lo);",
                    hi - (len(A(t)) - hi), "Two CTEs split the rows; the difference of their sizes.")


@reg
def cte_reads_cte(rng):
    t = _t(rng)
    return sql_item([t], "WITH d AS (SELECT a * 2 x FROM t), p AS (SELECT x + 1 y FROM d) SELECT SUM(y) FROM p;", sum(a * 2 + 1 for a in A(t)), "p reads d: double each value, then add one, then add everything up.")


@reg
def cte_column_list(rng):
    t = _t(rng)
    return sql_item([t], "WITH c(x) AS (SELECT a * 2 FROM t) SELECT MAX(x) FROM c;", 2 * max(A(t)), "The names in parentheses after the CTE name become its columns.")


@reg
def cte_values(rng):
    xs = rng.sample(range(1, 7), 3)
    rows = ",".join(f"({x})" for x in xs)
    return sql_item([], f"WITH n(i) AS (VALUES {rows}) SELECT SUM(i * i) FROM n;", sum(x * x for x in xs), "VALUES makes a table of constants; the query adds up their squares.")


@reg
def cte_used_twice(rng):
    t = _t(rng)
    k = rng.randint(4, 9)
    v = [a for a in A(t) if a > k]
    if not v:
        raise Retry
    return sql_item([t], f"WITH c AS (SELECT a FROM t WHERE a > {k}) SELECT COUNT(*) + SUM(a) FROM c;", len(v) + sum(v), "A CTE can be read as often as you like: its count plus its sum.")


@reg
def cte_self_join(rng):
    t = _t(rng, 5)
    k = rng.randint(4, 9)
    v = [a for a in A(t) if a > k]
    n = sum(1 for x in v for y in v if x < y)
    return sql_item([t], f"WITH c AS (SELECT a FROM t WHERE a > {k}) SELECT COUNT(*) FROM c x JOIN c y ON x.a < y.a;", n, "The CTE joined with itself: pairs of its rows where the first is smaller.")


@reg
def cte_hides_table(rng):
    t = _t(rng)
    x, y = rng.sample(range(20, 60), 2)
    return sql_item([t], f"WITH t(a) AS (VALUES ({x}),({y})) SELECT SUM(a) FROM t;", x + y, "The CTE named t hides the real table t: the query adds the two VALUES, not the table's rows.")


@reg
def cte_second_largest(rng):
    t = _t(rng, 6)
    return sql_item([t], "WITH r AS (SELECT a, (SELECT COUNT(*) FROM t y WHERE y.a > t.a) k FROM t) SELECT a FROM r WHERE k = 1;", sorted(A(t))[-2], "r tags each value with how many are bigger; k = 1 is the second largest.")


@reg
def cte_row_number(rng):
    t = _t(rng, 6)
    n = rng.randint(2, 4)
    return sql_item([t], f"WITH r AS (SELECT a, ROW_NUMBER() OVER (ORDER BY a DESC) n FROM t) SELECT a FROM r WHERE n = {n};", sorted(A(t), reverse=True)[n - 1], "A window function runs inside the CTE, and the main query filters on its number.")


@reg
def cte_top3_sum(rng):
    t = _t(rng, 6)
    return sql_item([t], "WITH top AS (SELECT a FROM t ORDER BY a DESC LIMIT 3) SELECT SUM(a) FROM top;", sum(sorted(A(t))[-3:]), "The CTE keeps the three biggest values; the query adds them.")


@reg
def cte_third_largest(rng):
    t = _t(rng, 6)
    return sql_item([t], "WITH top AS (SELECT a FROM t ORDER BY a DESC LIMIT 3) SELECT MIN(a) FROM top;", sorted(A(t))[-3], "The smallest of the three biggest is the third biggest.")


@reg
def cte_nested_avg(rng):
    t = _t(rng, 6)
    top = max(A(t))
    rest = [a for a in A(t) if a < top]
    return sql_item([t], "WITH r AS (SELECT a FROM t WHERE a < (SELECT MAX(a) FROM t)) SELECT ROUND(AVG(a), 2) FROM r;", sql_round(sum(rest) / len(rest), 2), "r is everything below the maximum; its average, rounded.")


# ── CTEs over groups ────────────────────────────────────────────────────

@reg
def multi_order_customers(rng):
    o = _o(rng)
    cnt: dict = {}
    for c, _ in o.rows:
        cnt[c] = cnt.get(c, 0) + 1
    return sql_item([o], "WITH c AS (SELECT c, COUNT(*) n FROM o GROUP BY c) SELECT COUNT(*) FROM c WHERE n > 1;", sum(1 for n in cnt.values() if n > 1), "The CTE has one row per customer with the number of orders; count those with more than one.")


@reg
def spread_of_totals(rng):
    o = _o(rng)
    s = _sums(o).values()
    return sql_item([o], "WITH c AS (SELECT c, SUM(v) s FROM o GROUP BY c) SELECT MAX(s) - MIN(s) FROM c;", max(s) - min(s), "One total per customer; the gap between the biggest and the smallest.")


@reg
def avg_of_totals(rng):
    o = _o(rng)
    s = list(_sums(o).values())
    return sql_item([o], "WITH c AS (SELECT c, SUM(v) s FROM o GROUP BY c) SELECT ROUND(AVG(s), 2) FROM c;", sql_round(sum(s) / len(s), 2), "The average of the per-customer totals (not of the orders).")


@reg
def two_ctes_chain(rng):
    o = _o(rng, 6)
    k = rng.randint(5, 12)
    sm = _sums(o)
    big = [c for c in sm if sm[c] > k]
    if not big:
        raise Retry
    return sql_item([o], f"WITH s AS (SELECT c, SUM(v) t FROM o GROUP BY c), b AS (SELECT c FROM s WHERE t > {k}) SELECT SUM(c) FROM b;",
                    sum(big), "s totals each customer; b keeps those with a total above k; the query adds up their ids.")


@reg
def dept_top_total(rng):
    e = _e(rng)
    tot: dict = {}
    for d, s in e.rows:
        tot[d] = tot.get(d, 0) + s
    best = max(tot.values())
    top = [d for d, v in tot.items() if v == best]
    if len(top) != 1:
        raise Retry
    return sql_item([e], "WITH s AS (SELECT d, SUM(s) v FROM e GROUP BY d), m AS (SELECT MAX(v) x FROM s) SELECT d FROM s, m WHERE v = x;", top[0], "s has a total per department, m has the biggest total, and the join finds whose it is.")


@reg
def groups_over_overall(rng):
    e = _e(rng)
    overall = avg_([s for _, s in e.rows])
    g: dict = {}
    for d, s in e.rows:
        g.setdefault(d, []).append(s)
    n = sum(1 for v in g.values() if avg_(v) > overall)
    return sql_item([e], "WITH g AS (SELECT d, AVG(s) v FROM e GROUP BY d) SELECT COUNT(*) FROM g WHERE v > (SELECT AVG(s) FROM e);", n, "Departments whose average beats the overall average.")


@reg
def dept_sizes(rng):
    e = _e(rng, 7)
    g: dict = {}
    for d, _ in e.rows:
        g[d] = g.get(d, 0) + 1
    return sql_item([e], "WITH c AS (SELECT d, COUNT(*) n FROM e GROUP BY d) SELECT MAX(n) FROM c;", max(g.values()), "The size of the biggest department.")


@reg
def share_of_top_dept(rng):
    e = _e(rng)
    tot: dict = {}
    for d, s in e.rows:
        tot[d] = tot.get(d, 0) + s
    return sql_item([e], "WITH s AS (SELECT d, SUM(s) v FROM e GROUP BY d) SELECT MAX(v) * 100 / (SELECT SUM(v) FROM s) FROM s;",
                    max(tot.values()) * 100 // sum(tot.values()), "The biggest total as a whole percent of all totals (integer division).")


# ── WITH RECURSIVE: series ──────────────────────────────────────────────

def _count_up(start: int, step: int, k: int) -> list:
    return recursive(start, lambda i: i + step if i < k else None)


@reg
def rec_count(rng):
    k = rng.randint(4, 9)
    return sql_item([], f"WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < {k}) SELECT COUNT(*) FROM n;", k, "The seed row is 1; each round adds i + 1 while i < k, so there are k rows.")


@reg
def rec_sum(rng):
    k = rng.randint(4, 9)
    return sql_item([], f"WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < {k}) SELECT SUM(i) FROM n;", sum(_count_up(1, 1, k)), "The numbers 1 to k added up.")


@reg
def rec_squares(rng):
    k = rng.randint(3, 6)
    return sql_item([], f"WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < {k}) SELECT SUM(i * i) FROM n;", sum(i * i for i in _count_up(1, 1, k)), "The squares of 1 to k, added up.")


@reg
def rec_step_last(rng):
    step, k = rng.randint(2, 4), rng.randint(10, 20)
    return sql_item([], f"WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + {step} FROM n WHERE i < {k}) SELECT MAX(i) FROM n;", max(_count_up(1, step, k)),
                    "The test i < k is checked before each new row, so the last value can overshoot k.")


@reg
def rec_step_count(rng):
    step, k = rng.randint(2, 4), rng.randint(10, 20)
    return sql_item([], f"WITH RECURSIVE n(i) AS (SELECT 0 UNION ALL SELECT i + {step} FROM n WHERE i < {k}) SELECT COUNT(*) FROM n;", len(_count_up(0, step, k)), "Count the rows: 0, then steps of the given size until i reaches k.")


@reg
def rec_even_sum(rng):
    k = rng.randint(6, 10)
    return sql_item([], f"WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < {k}) SELECT SUM(i) FROM n WHERE i % 2 = 0;", sum(i for i in _count_up(1, 1, k) if i % 2 == 0), "The recursion builds 1 to k; the final WHERE keeps the even ones.")


@reg
def rec_countdown(rng):
    k = rng.randint(4, 8)
    r = recursive(k, lambda i: i - 1 if i > 0 else None)
    return sql_item([], f"WITH RECURSIVE n(i) AS (SELECT {k} UNION ALL SELECT i - 1 FROM n WHERE i > 0) SELECT COUNT(*) FROM n;", len(r), "Counting down from k while i > 0 also produces the 0: k + 1 rows.")


@reg
def rec_second_last(rng):
    k = rng.randint(4, 8)
    r = _count_up(1, 1, k)
    return sql_item([], f"WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < {k}) SELECT i FROM n ORDER BY i DESC LIMIT 1 OFFSET 1;", r[-2], "Sorted from the top, skip one row: the second biggest.")


@reg
def rec_doubling_last(rng):
    k = rng.choice([20, 30, 50, 70, 100])
    r = recursive(1, lambda i: i * 2 if i < k else None)
    return sql_item([], f"WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i * 2 FROM n WHERE i < {k}) SELECT MAX(i) FROM n;", r[-1], "Powers of two: the first one that is not below k is the last row.")


@reg
def rec_doubling_count(rng):
    k = rng.choice([20, 30, 50, 70, 100])
    r = recursive(1, lambda i: i * 2 if i < k else None)
    return sql_item([], f"WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i * 2 FROM n WHERE i < {k}) SELECT COUNT(*) FROM n;", len(r), "How many powers of two it takes to reach k.")


@reg
def rec_power(rng):
    b, k = rng.randint(2, 4), rng.randint(2, 5)
    return sql_item([], f"WITH RECURSIVE p(i, v) AS (SELECT 0, 1 UNION ALL SELECT i + 1, v * {b} FROM p WHERE i < {k}) SELECT v FROM p WHERE i = {k};", b ** k, "Two columns travel together: the exponent and the running product.")


@reg
def rec_factorial(rng):
    k = rng.randint(3, 7)
    f = 1
    for i in range(2, k + 1):
        f *= i
    return sql_item([], f"WITH RECURSIVE f(n, p) AS (SELECT 1, 1 UNION ALL SELECT n + 1, p * (n + 1) FROM f WHERE n < {k}) SELECT p FROM f WHERE n = {k};", f, "n counts up while p multiplies by n + 1: k factorial.")


@reg
def rec_fibonacci(rng):
    k = rng.randint(4, 12)
    a, b = 0, 1
    for _ in range(k - 1):
        a, b = b, a + b
    return sql_item([], f"WITH RECURSIVE f(i, a, b) AS (SELECT 1, 0, 1 UNION ALL SELECT i + 1, b, a + b FROM f WHERE i < {k}) SELECT a FROM f WHERE i = {k};", a, "Each row keeps two neighbours of the Fibonacci sequence; row i holds the i-th number (row 1 is 0).")


@reg
def rec_triangular(rng):
    k = rng.randint(4, 10)
    return sql_item([], f"WITH RECURSIVE t(i, s) AS (SELECT 1, 1 UNION ALL SELECT i + 1, s + i + 1 FROM t WHERE i < {k}) SELECT s FROM t WHERE i = {k};", k * (k + 1) // 2, "A running total carried along: 1 + 2 + ... + k.")


@reg
def rec_collatz(rng):
    k = rng.randint(3, 12)
    r = recursive((k, 0), lambda p: None if p[0] == 1 else ((p[0] // 2 if p[0] % 2 == 0 else 3 * p[0] + 1), p[1] + 1))
    return sql_item([], f"WITH RECURSIVE c(n, s) AS (SELECT {k}, 0 UNION ALL SELECT CASE WHEN n % 2 = 0 THEN n / 2 ELSE 3 * n + 1 END, s + 1 FROM c WHERE n <> 1) SELECT MAX(s) FROM c;",
                    r[-1][1], "Halve an even number, triple-plus-one an odd one, until 1: the number of steps it took.")


@reg
def rec_digit_sum(rng):
    k = rng.randint(100, 999)
    return sql_item([], f"WITH RECURSIVE d(n, s) AS (SELECT {k}, 0 UNION ALL SELECT n / 10, s + n % 10 FROM d WHERE n > 0) SELECT MAX(s) FROM d;", sum(map(int, str(k))), "n % 10 is the last digit, n / 10 drops it: the sum of the digits.")


@reg
def rec_gcd(rng):
    g = rng.randint(2, 6)
    a, b = g * rng.randint(2, 6), g * rng.randint(2, 6)
    if a == b:
        raise Retry
    r = recursive((a, b), lambda p: (p[1], p[0] % p[1]) if p[1] > 0 else None)
    return sql_item([], f"WITH RECURSIVE g(a, b) AS (SELECT {a}, {b} UNION ALL SELECT b, a % b FROM g WHERE b > 0) SELECT a FROM g WHERE b = 0;", r[-1][0], "Euclid's algorithm: replace (a, b) by (b, a % b) until b is 0; a is the greatest common divisor.")


@reg
def rec_string(rng):
    ch = rng.choice("abcxyz")
    k = rng.randint(3, 6)
    return sql_item([], f"WITH RECURSIVE s(t, i) AS (SELECT '{ch}', 1 UNION ALL SELECT t || '{ch}', i + 1 FROM s WHERE i < {k}) SELECT t FROM s WHERE i = {k};", ch * k, "Each round glues one more letter on.")


@reg
def rec_limit(rng):
    k = rng.randint(4, 8)
    return sql_item([], f"WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n LIMIT {k}) SELECT SUM(i) FROM n;", k * (k + 1) // 2, "No WHERE would run forever, but LIMIT stops the recursion after k rows.")


@reg
def rec_join_table(rng):
    t = _t(rng, 5, 1, 10)
    k = rng.randint(4, 8)
    return sql_item([t], f"WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < {k}) SELECT COUNT(*) FROM n JOIN t ON t.a = n.i;", sum(1 for a in A(t) if 1 <= a <= k), "The generated numbers 1..k joined to the table: its values inside that range.")


@reg
def rec_missing(rng):
    t = _t(rng, 4, 1, 7)
    k = 7
    return sql_item([t], f"WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < {k}) SELECT COUNT(*) FROM n WHERE i NOT IN (SELECT a FROM t);", k - len(A(t)), "A series makes the gaps visible: the numbers 1 to 7 that the table does not have.")


@reg
def rec_expand_rows(rng):
    t = Tbl("t", [("a", "INT")], [(x,) for x in rng.sample(range(1, 5), 3)])
    return sql_item([t], "WITH RECURSIVE r(x) AS (SELECT a FROM t UNION ALL SELECT x - 1 FROM r WHERE x > 1) SELECT COUNT(*) FROM r;", sum(A(t)), "Each starting value a is counted down to 1, giving a rows: the total is the sum of a.")


# ── WITH RECURSIVE: trees and graphs ────────────────────────────────────

@reg
def rec_depth(rng):
    t = _tree(rng)
    k = rng.randint(2, 6)
    p = dict(t.rows)
    path = recursive(k, lambda i: p[i] if p[i] is not None else None)
    return sql_item([t], f"WITH RECURSIVE up(x) AS (SELECT {k} UNION ALL SELECT b FROM e JOIN up ON id = x WHERE b IS NOT NULL) SELECT COUNT(*) FROM up;", len(path),
                    "Walk from the employee up through each boss to the top: the number of people on the way, the start included.")


@reg
def rec_path_sum(rng):
    t = _tree(rng)
    k = rng.randint(2, 6)
    p = dict(t.rows)
    path = recursive(k, lambda i: p[i] if p[i] is not None else None)
    return sql_item([t], f"WITH RECURSIVE up(x) AS (SELECT {k} UNION ALL SELECT b FROM e JOIN up ON id = x WHERE b IS NOT NULL) SELECT SUM(x) FROM up;", sum(path), "The ids along the chain of bosses, added up.")


@reg
def rec_subtree(rng):
    t = _tree(rng, 6)
    k = rng.randint(1, 3)
    seen, stack = [k], [k]
    while stack:
        x = stack.pop()
        for i, b in t.rows:
            if b == x:
                seen.append(i)
                stack.append(i)
    return sql_item([t], f"WITH RECURSIVE d(x) AS (SELECT {k} UNION ALL SELECT id FROM e JOIN d ON b = x) SELECT COUNT(*) FROM d;", len(seen), "Walk down: the employee, their reports, their reports' reports...")


@reg
def rec_subtree_sum(rng):
    t = _tree(rng, 6)
    k = rng.randint(1, 3)
    seen, stack = [k], [k]
    while stack:
        x = stack.pop()
        for i, b in t.rows:
            if b == x:
                seen.append(i)
                stack.append(i)
    return sql_item([t], f"WITH RECURSIVE d(x) AS (SELECT {k} UNION ALL SELECT id FROM e JOIN d ON b = x) SELECT SUM(x) FROM d;", sum(seen), "The ids of everyone under (and including) the starting employee.")


def _edges(rng: random.Random) -> Tbl:
    return Tbl("g", [("a", "INT"), ("b", "INT")], [(rng.randint(1, 5), rng.randint(1, 5)) for _ in range(6)])


def _reach(edges: list, start: int) -> set:
    seen, todo = {start}, [start]
    while todo:
        x = todo.pop()
        for a, b in edges:
            if a == x and b not in seen:
                seen.add(b)
                todo.append(b)
    return seen


@reg
def rec_reachable(rng):
    g = _edges(rng)
    return sql_item([g], "WITH RECURSIVE r(x) AS (SELECT 1 UNION SELECT b FROM g JOIN r ON a = x) SELECT COUNT(*) FROM r;", len(_reach(g.rows, 1)), "With UNION (not UNION ALL) a place already seen is not added again, so even loops end: count the places reachable from 1.")


@reg
def rec_reachable_sum(rng):
    g = _edges(rng)
    return sql_item([g], "WITH RECURSIVE r(x) AS (SELECT 1 UNION SELECT b FROM g JOIN r ON a = x) SELECT SUM(x) FROM r;", sum(_reach(g.rows, 1)), "The places reachable from 1 (1 itself included), added up.")


@reg
def rec_unreachable(rng):
    g = _edges(rng)
    r = _reach(g.rows, 1)
    return sql_item([g], "WITH RECURSIVE r(x) AS (SELECT 1 UNION SELECT b FROM g JOIN r ON a = x) SELECT COUNT(*) FROM g WHERE a NOT IN (SELECT x FROM r);",
                    sum(1 for a, _ in g.rows if a not in r), "Edges that start at a place the walk from 1 never reaches.")
