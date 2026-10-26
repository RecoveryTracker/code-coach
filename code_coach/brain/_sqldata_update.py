"""SQL data pack, part 1: After Update (`UPDATES`) and After Delete (`DELETES`).

Every script is `CREATE TABLE`, `INSERT`, one or two changing statements, and a final SELECT; the answer is worked out by
hand with `_sqldata_model.py` (the `Table` of dict rows: `update`, `delete`) and held to real SQLite by the oracle.
"""

from __future__ import annotations

import random

from ._model import Maker
from ._sql_model import (Retry, between, count_col, count_distinct, eq, fit, gt, in_list, like, lt, max_, ne,
                         sql_div, sql_mod, sum_, t_and, t_not, t_or)
from ._sqldata_model import Col, Script, Table, base, base_named, nz


def upd(s: Script, t: Table, sql: str, sets: dict, where=None, mode: str = "abort") -> int:
    """An UPDATE: its SQL line and the model's work on it."""
    return s.dml(sql, lambda: t.update(sets, where, mode))


def dele(s: Script, t: Table, sql: str, where=None) -> int:
    return s.dml(sql, lambda: t.delete(where))


def _k(rng: random.Random, lo: int = 2, hi: int = 6) -> int:
    return rng.randint(lo, hi)


# ── 1. After Update ─────────────────────────────────────────────────────

def u_add_where(rng):
    s, t = base(rng)
    k, m = _k(rng), _k(rng, 3, 6)
    upd(s, t, f"UPDATE t SET a = a + {k} WHERE a > {m};", {"a": lambda r: r["a"] + k}, lambda r: gt(r["a"], m))
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "Only the rows with a above the limit get the number added; the others keep their value.")


def u_all_rows(rng):
    s, t = base(rng)
    k = _k(rng)
    upd(s, t, f"UPDATE t SET a = a * {k};", {"a": lambda r: r["a"] * k})
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "With no WHERE, an UPDATE changes every row: the sum is multiplied.")


def u_zero_small(rng):
    s, t = base(rng)
    m = _k(rng, 3, 6)
    upd(s, t, f"UPDATE t SET a = 0 WHERE a < {m};", {"a": lambda r: 0}, lambda r: lt(r["a"], m))
    return s.item("SELECT COUNT(*) FROM t WHERE a = 0;", t.col("a").count(0), "The rows below the limit were set to 0, and no row had 0 before.")


def u_null_count(rng):
    s, t = base(rng)
    m = _k(rng, 3, 6)
    upd(s, t, f"UPDATE t SET a = NULL WHERE a > {m};", {"a": lambda r: None}, lambda r: gt(r["a"], m))
    return s.item("SELECT COUNT(a) FROM t;", count_col(t.col("a")), "Setting a to NULL leaves those rows in the table, but COUNT(a) skips NULLs.")


def u_null_sum(rng):
    s, t = base(rng)
    k = rng.randint(1, 5)
    upd(s, t, f"UPDATE t SET a = NULL WHERE id = {k};", {"a": lambda r: None}, lambda r: eq(r["id"], k))
    return s.item("SELECT SUM(a) FROM t;", sum_(t.col("a")), "SUM adds only the values that are not NULL, so the nulled row drops out.")


def u_one_row(rng):
    s, t = base(rng)
    k, d = rng.randint(1, 5), _k(rng)
    upd(s, t, f"UPDATE t SET a = a + {d} WHERE id = {k};", {"a": lambda r: r["a"] + d}, lambda r: eq(r["id"], k))
    return s.item(f"SELECT a FROM t WHERE id = {k};", t.one("a", lambda r: eq(r["id"], k)), "The WHERE picks one row, and the new value is its old value plus the number.")


def _two(rng, n: int = 4):
    """t(id INTEGER PRIMARY KEY, a INT, b INT), small values."""
    s = Script()
    rows = [(i + 1, rng.randint(1, 9), rng.randint(1, 9)) for i in range(n)]
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True), Col("a"), Col("b")]), rows)
    return s, t


def u_swap(rng):
    s, t = _two(rng)
    k = rng.randint(1, 4)
    upd(s, t, "UPDATE t SET a = b, b = a;", {"a": lambda r: r["b"], "b": lambda r: r["a"]})
    return s.item(f"SELECT a FROM t WHERE id = {k};", t.one("a", lambda r: eq(r["id"], k)), "Every right-hand side is read from the row as it was before the UPDATE, so a and b swap.")


def u_set_uses_old(rng):
    s, t = _two(rng)
    k = rng.randint(1, 4)
    upd(s, t, "UPDATE t SET a = a + 1, b = a * 2;", {"a": lambda r: r["a"] + 1, "b": lambda r: r["a"] * 2})
    return s.item(f"SELECT b FROM t WHERE id = {k};", t.one("b", lambda r: eq(r["id"], k)), "b = a * 2 uses the OLD a: the a + 1 in the same SET has not happened yet.")


def u_case_set(rng):
    s, t = base(rng)
    m = _k(rng, 3, 6)
    upd(s, t, f"UPDATE t SET a = CASE WHEN a > {m} THEN a - {m} ELSE 0 END;", {"a": lambda r: r["a"] - m if r["a"] > m else 0})
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "Each row gets its own CASE result: the excess over the limit, or 0.")


def u_case_label(rng):
    s = Script()
    vals = [rng.randint(1, 9) for _ in range(5)]
    t = s.create(Table("t", [Col("a"), Col("g", "TEXT")]), [(v, None) for v in vals])
    m = _k(rng, 3, 6)
    upd(s, t, f"UPDATE t SET g = CASE WHEN a > {m} THEN 'hi' ELSE 'lo' END;", {"g": lambda r: "hi" if r["a"] > m else "lo"})
    return s.item("SELECT COUNT(*) FROM t WHERE g = 'hi';", t.col("g").count("hi"), "Every row is labelled 'hi' or 'lo' by the CASE; then the 'hi' ones are counted.")


def u_null_add(rng):
    s, t = base(rng, nulls=1)
    k = _k(rng)
    upd(s, t, f"UPDATE t SET a = a + {k};", {"a": lambda r: nz(r["a"], lambda v: v + k)})
    return s.item("SELECT SUM(a) FROM t;", sum_(t.col("a")), "NULL + k is NULL, so the NULL row stays NULL and SUM skips it.")


def u_coalesce_inc(rng):
    s, t = base(rng, nulls=1)
    k = _k(rng)
    upd(s, t, f"UPDATE t SET a = COALESCE(a, 0) + {k};", {"a": lambda r: (r["a"] or 0) + k})
    return s.item("SELECT SUM(a) FROM t;", sum_(t.col("a")), "COALESCE turns the NULL into 0 first, so even that row gets the number added.")


def u_eq_null(rng):
    s, t = base(rng, rng.randint(4, 6), nulls=1)
    upd(s, t, "UPDATE t SET a = 0 WHERE a = NULL;", {"a": lambda r: 0}, lambda r: eq(r["a"], None))
    return s.item("SELECT COUNT(a) FROM t;", count_col(t.col("a")), "a = NULL is never true, so the UPDATE touches nothing and the NULL stays.")


def u_is_null_fill(rng):
    s, t = base(rng, nulls=1)
    k = _k(rng)
    upd(s, t, f"UPDATE t SET a = {k} WHERE a IS NULL;", {"a": lambda r: k}, lambda r: r["a"] is None)
    return s.item("SELECT SUM(a) FROM t;", sum_(t.col("a")), "IS NULL finds the empty row and fills it, so SUM now counts it.")


def u_ne_null(rng):
    s, t = base(rng, nulls=1)
    k = rng.choice([v for v in t.col("a") if v is not None])
    upd(s, t, f"UPDATE t SET a = 0 WHERE a <> {k};", {"a": lambda r: 0}, lambda r: ne(r["a"], k))
    return s.item("SELECT SUM(a) FROM t;", sum_(t.col("a")), "<> is unknown for the NULL row, so it is not zeroed (it is still NULL); only the rows equal to k add anything.")


def u_not_flag(rng):
    s = Script()
    vals = [rng.randint(0, 1) for _ in range(5)]
    vals[rng.randrange(5)] = None
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True), Col("done")]), [(i + 1, v) for i, v in enumerate(vals)])
    upd(s, t, "UPDATE t SET done = NOT done;", {"done": lambda r: nz(r["done"], lambda v: 1 - v)})
    return s.item("SELECT SUM(done) FROM t;", sum_(t.col("done")), "NOT flips 0 and 1, and NOT NULL is still NULL.")


def u_concat(rng):
    s, t = base_named(rng)
    m, k = _k(rng, 3, 6), rng.randint(1, 5)
    upd(s, t, f"UPDATE t SET n = n || '!' WHERE a > {m};", {"n": lambda r: r["n"] + "!"}, lambda r: gt(r["a"], m))
    return s.item(f"SELECT n FROM t WHERE id = {k};", t.one("n", lambda r: eq(r["id"], k)), "|| glues the '!' on, but only for the rows the WHERE let through.")


def u_capitalize(rng):
    s, t = base_named(rng, 3)
    k = rng.randint(1, 3)
    upd(s, t, f"UPDATE t SET n = UPPER(SUBSTR(n,1,1)) || SUBSTR(n,2) WHERE id = {k};",
        {"n": lambda r: r["n"][0].upper() + r["n"][1:]}, lambda r: eq(r["id"], k))
    return s.item(f"SELECT n FROM t WHERE id = {k};", t.one("n", lambda r: eq(r["id"], k)), "The first letter is made upper case and glued to the rest of the word.")


def u_substr(rng):
    s, t = base_named(rng, 4)
    k = rng.randint(1, 4)
    upd(s, t, "UPDATE t SET n = SUBSTR(n, 1, 2);", {"n": lambda r: r["n"][:2]})
    return s.item(f"SELECT n FROM t WHERE id = {k};", t.one("n", lambda r: eq(r["id"], k)), "Every name is cut to its first two letters.")


def u_length(rng):
    s, t = base_named(rng)
    upd(s, t, "UPDATE t SET a = LENGTH(n);", {"a": lambda r: len(r["n"])})
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "a becomes the number of letters in n; the sum adds those lengths.")


def u_replace_fn(rng):
    s, t = base_named(rng, 4)
    hit = [r for r in t.rows if "a" in r["n"]]
    if not hit:
        raise Retry
    k = rng.choice(hit)["id"]
    upd(s, t, "UPDATE t SET n = REPLACE(n, 'a', 'o');", {"n": lambda r: r["n"].replace("a", "o")})
    return s.item(f"SELECT n FROM t WHERE id = {k};", t.one("n", lambda r: eq(r["id"], k)), "REPLACE swaps every 'a' in the name for an 'o'.")


def u_like_where(rng):
    s, t = base_named(rng)
    letter = rng.choice(t.col("n"))[0]
    upd(s, t, f"UPDATE t SET a = 0 WHERE n LIKE '{letter}%';", {"a": lambda r: 0}, lambda r: like(r["n"], letter + "%"))
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "Names that start with the letter get a = 0; the others keep their number.")


def u_subq_const(rng):
    s, t = base(rng)
    k = rng.randint(1, 5)
    top = max(t.col("a"))
    upd(s, t, f"UPDATE t SET a = (SELECT MAX(a) FROM t) WHERE id = {k};", {"a": lambda r: top}, lambda r: eq(r["id"], k))
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "The subquery finds the biggest a once, and the chosen row is set to it.")


def u_subq_count(rng):
    s, t = base(rng)
    m = _k(rng, 3, 6)
    n = len(t.rows)
    upd(s, t, f"UPDATE t SET a = (SELECT COUNT(*) FROM t) WHERE a > {m};", {"a": lambda r: n}, lambda r: gt(r["a"], m))
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "The subquery counts the rows (the count does not change), and each row above the limit becomes that count.")


def u_above_avg(rng):
    s, t = base(rng)
    avg = sum(t.col("a")) / len(t.rows)
    upd(s, t, "UPDATE t SET a = a + 10 WHERE a > (SELECT AVG(a) FROM t);", {"a": lambda r: r["a"] + 10}, lambda r: gt(r["a"], avg))
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "The average is worked out first from the old values; every row above it gets 10 more.")


def u_min_once(rng):
    s, t = base(rng)
    low = min(t.col("a"))
    upd(s, t, "UPDATE t SET a = a + (SELECT MIN(a) FROM t);", {"a": lambda r: r["a"] + low})
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "The subquery is worked out once, before any row changes: every row gets the same old minimum added.")


def _pair(rng, matched: int = 2, n: int = 4, b: bool = True):
    """t(id INT, a INT) and u(id INT, b INT) (or just u(id INT)) holding `matched` of t's ids."""
    s, t = base(rng, n, pk=False)
    ids = sorted(rng.sample(range(1, n + 1), matched))
    if b:
        u = s.create(Table("u", [Col("id"), Col("b")]), [(i, rng.randint(2, 9)) for i in ids])
    else:
        u = s.create(Table("u", [Col("id")]), [(i,) for i in ids])
    return s, t, u


def u_corr_missing(rng):
    s, t, u = _pair(rng, rng.randint(1, 2), rng.randint(3, 4))
    bs = {r["id"]: r["b"] for r in u.rows}
    upd(s, t, "UPDATE t SET a = (SELECT b FROM u WHERE u.id = t.id);", {"a": lambda r: bs.get(r["id"])})
    return s.item("SELECT COUNT(a) FROM t;", count_col(t.col("a")), "A row with no match in u gets NULL from the subquery, so only the matched rows still have an a.")


def u_update_from(rng):
    s, t, u = _pair(rng)
    bs = {r["id"]: r["b"] for r in u.rows}
    upd(s, t, "UPDATE t SET a = u.b FROM u WHERE t.id = u.id;", {"a": lambda r: bs[r["id"]]}, lambda r: r["id"] in bs)
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "UPDATE ... FROM only touches the rows that find a match; the others keep their a.")


def u_in_subq(rng):
    s, t = base(rng, 4)
    xs = rng.sample(range(1, 7), 2)
    s.create(Table("u", [Col("x")]), [(x,) for x in xs])
    upd(s, t, "UPDATE t SET a = 0 WHERE id IN (SELECT x FROM u);", {"a": lambda r: 0}, lambda r: in_list(r["id"], xs))
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "The ids listed in u are zeroed; an x that matches no id does nothing.")


def u_exists_corr(rng):
    s, t, u = _pair(rng, 2, 3, False)
    ids = {r["id"] for r in u.rows}
    upd(s, t, "UPDATE t SET a = a * 2 WHERE EXISTS (SELECT 1 FROM u WHERE u.id = t.id);", {"a": lambda r: r["a"] * 2}, lambda r: r["id"] in ids)
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "EXISTS is true for the rows that have a partner in u; only those are doubled.")


def u_twice(rng):
    s, t = base(rng)
    m = _k(rng, 4, 7)
    for _ in range(2):
        upd(s, t, f"UPDATE t SET a = a + 1 WHERE a < {m};", {"a": lambda r: r["a"] + 1}, lambda r: lt(r["a"], m))
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "The same UPDATE runs twice, and the second run sees the first run's results: small rows go up twice.")


def u_order_matters(rng):
    s, t = base(rng)
    m = _k(rng, 3, 6)
    upd(s, t, f"UPDATE t SET a = a * 2 WHERE a > {m};", {"a": lambda r: r["a"] * 2}, lambda r: gt(r["a"], m))
    upd(s, t, f"UPDATE t SET a = a - {m} WHERE a > {m};", {"a": lambda r: r["a"] - m}, lambda r: gt(r["a"], m))
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "The second UPDATE looks at the doubled values, so more rows pass its WHERE.")


def u_changes_matched(rng):
    s, t = base(rng)
    m = _k(rng, 3, 6)
    upd(s, t, f"UPDATE t SET a = a WHERE a > {m};", {"a": lambda r: r["a"]}, lambda r: gt(r["a"], m))
    return s.item("SELECT changes();", s.changes, "changes() counts the rows the WHERE matched, even though no value actually changed.")


def u_changes_none(rng):
    s, t = base(rng, rng.randint(4, 6))
    upd(s, t, "UPDATE t SET a = 0 WHERE a > 99;", {"a": lambda r: 0}, lambda r: gt(r["a"], 99))
    return s.item("SELECT changes();", s.changes, "No row has a above 99, so the UPDATE changed 0 rows.")


def u_changes_all(rng):
    s, t = base(rng, rng.randint(4, 7))
    upd(s, t, "UPDATE t SET a = a + 1;", {"a": lambda r: r["a"] + 1})
    return s.item("SELECT changes();", s.changes, "An UPDATE with no WHERE changes every row, so changes() is the row count.")


def u_int_div(rng):
    s, t = base(rng)
    upd(s, t, "UPDATE t SET a = a / 2;", {"a": lambda r: sql_div(r["a"], 2)})
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "Integer division drops the remainder: 7 / 2 is 3.")


def u_mod(rng):
    s, t = base(rng)
    k = _k(rng, 2, 4)
    upd(s, t, f"UPDATE t SET a = a % {k};", {"a": lambda r: sql_mod(r["a"], k)})
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "% keeps the remainder after dividing by the number.")


def u_distinct_mod(rng):
    s, t = base(rng, 6)
    k = _k(rng, 2, 4)
    upd(s, t, f"UPDATE t SET a = a % {k};", {"a": lambda r: sql_mod(r["a"], k)})
    return s.item("SELECT COUNT(DISTINCT a) FROM t;", count_distinct(t.col("a")), "After a % k only remainders are left, and the query counts the different ones.")


def u_min_cap(rng):
    s, t = base(rng)
    m = _k(rng, 3, 6)
    upd(s, t, f"UPDATE t SET a = MIN(a, {m});", {"a": lambda r: min(r["a"], m)})
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "MIN with two arguments caps every value at the limit.")


def u_max_floor(rng):
    s, t = base(rng)
    m = _k(rng, 3, 6)
    upd(s, t, f"UPDATE t SET a = MAX(a, {m});", {"a": lambda r: max(r["a"], m)})
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "MAX with two arguments lifts every value to at least the limit.")


def u_max_null(rng):
    s, t = base(rng, rng.randint(4, 6), nulls=1)
    m = _k(rng, 3, 6)
    upd(s, t, f"UPDATE t SET a = MAX(a, {m});", {"a": lambda r: nz(r["a"], lambda v: max(v, m))})
    return s.item("SELECT COUNT(a) FROM t;", count_col(t.col("a")), "MAX(NULL, m) is NULL (the two-argument MAX gives NULL when an argument is NULL), so the NULL row stays NULL.")


def u_abs(rng):
    s, t = base(rng)
    m = _k(rng, 3, 6)
    upd(s, t, f"UPDATE t SET a = ABS(a - {m});", {"a": lambda r: abs(r["a"] - m)})
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "ABS is the distance from the number, never negative.")


def u_between(rng):
    s, t = base(rng)
    lo, hi = sorted(rng.sample(range(2, 9), 2))
    upd(s, t, f"UPDATE t SET a = 0 WHERE a BETWEEN {lo} AND {hi};", {"a": lambda r: 0}, lambda r: between(r["a"], lo, hi))
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "BETWEEN includes both ends: those rows are zeroed.")


def u_or_and(rng):
    s, t = base(rng)
    m, m2 = rng.randint(2, 4), rng.randint(4, 7)
    k = rng.randint(2, 4)
    upd(s, t, f"UPDATE t SET a = 0 WHERE a < {m} OR a > {m2} AND id > {k};", {"a": lambda r: 0},
        lambda r: t_or(lt(r["a"], m), t_and(gt(r["a"], m2), gt(r["id"], k))))
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "AND binds tighter than OR: it is 'a < m' OR ('a > m2' AND 'id > k').")


def u_not_cond(rng):
    s, t = base(rng, nulls=1)
    m = _k(rng, 3, 6)
    upd(s, t, f"UPDATE t SET a = 0 WHERE NOT (a > {m});", {"a": lambda r: 0}, lambda r: t_not(gt(r["a"], m)))
    return s.item("SELECT SUM(a) FROM t;", sum_(t.col("a")), "NOT of an unknown is unknown, so the NULL row is not zeroed; only the true big rows are summed.")


def u_text_number(rng):
    s, t = base(rng)
    upd(s, t, "UPDATE t SET a = a || '0';", {"a": lambda r: str(r["a"]) + "0"})
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "a || '0' is text like '50', but the INT column turns it back into the number 50.")


def u_plus_id(rng):
    s, t = base(rng)
    upd(s, t, "UPDATE t SET a = a + id;", {"a": lambda r: r["a"] + r["id"]})
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "A SET can use other columns of the same row: each row adds its own id.")


def u_other_col(rng):
    s, t = _two(rng, 5)
    m = _k(rng, 3, 6)
    upd(s, t, f"UPDATE t SET b = a * 2 WHERE a > {m};", {"b": lambda r: r["a"] * 2}, lambda r: gt(r["a"], m))
    return s.item("SELECT SUM(b) FROM t;", sum(t.col("b")), "Only b changes, and only on the rows above the limit.")


def u_set_pk(rng):
    s, t = base(rng)
    k = rng.randint(1, 5)
    upd(s, t, f"UPDATE t SET id = id + 10 WHERE id = {k};", {"id": lambda r: r["id"] + 10}, lambda r: eq(r["id"], k))
    return s.item("SELECT MAX(id) FROM t;", max_(t.col("id")), "A primary key can be updated like any column: that row now has the biggest id.")


UPDATES: list[Maker] = [fit(f) for f in (
    u_add_where, u_all_rows, u_zero_small, u_null_count, u_null_sum, u_one_row, u_swap, u_set_uses_old, u_case_set,
    u_case_label, u_null_add, u_coalesce_inc, u_eq_null, u_is_null_fill, u_ne_null, u_not_flag, u_concat, u_capitalize,
    u_substr, u_length, u_replace_fn, u_like_where, u_subq_const, u_subq_count, u_above_avg, u_min_once, u_corr_missing,
    u_update_from, u_in_subq, u_exists_corr, u_twice, u_order_matters, u_changes_matched, u_changes_none, u_changes_all,
    u_int_div, u_mod, u_distinct_mod, u_min_cap, u_max_floor, u_max_null, u_abs, u_between, u_or_and, u_not_cond,
    u_text_number, u_plus_id, u_other_col, u_set_pk)]
