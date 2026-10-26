"""SQL data pack, part 6: View Says (`VIEWS`) and Transaction Rollback (`TXNS`).

View Says: a VIEW is a saved query, not a saved result. The model answers a view question from the table rows as they are
at the END of the script (a view is live). Transaction Rollback: BEGIN / COMMIT / ROLLBACK, SAVEPOINT / ROLLBACK TO / RELEASE;
`Script` keeps a stack of snapshots. Every script with a BEGIN has a `COMMIT;` after its setup (the runner's Python opens a
transaction by itself at the first INSERT; see `_sqldata_model`).
"""

from __future__ import annotations

from ._model import Maker
from ._sql_model import Retry, count_col, count_distinct, fit, max_, min_, sum_, words
from ._sqldata_model import Col, Script, Table, base, base_named
from ._sqldata_update import _k, upd


#: A newline (a query that starts with WITH goes on two lines, so the LAST line of a script starts with SELECT).
NL = chr(10)


def _vals(t: Table, name: str = "a") -> list:
    return t.col(name)


# ── 7. View Says ────────────────────────────────────────────────────────

def w_count_insert(rng):
    s, t = base(rng, 4, mode="plain")
    m = _k(rng, 3, 6)
    s.run(f"CREATE VIEW v AS SELECT a FROM t WHERE a > {m};")
    s.insert(t, [(rng.randint(1, 9),) for _ in range(3)])
    return s.item("SELECT COUNT(*) FROM v;", sum(1 for x in _vals(t) if x > m), "A view is a saved query, run again each time: rows inserted later show up in it.")


def w_count_update(rng):
    s, t = base(rng, 5, mode="plain")
    m = _k(rng, 3, 6)
    s.run(f"CREATE VIEW v AS SELECT a FROM t WHERE a > {m};")
    s.dml(f"UPDATE t SET a = a + 5 WHERE a <= {m};", lambda: t.update({"a": lambda r: r["a"] + 5}, lambda r: r["a"] <= m))
    return s.item("SELECT COUNT(*) FROM v;", sum(1 for x in _vals(t) if x > m), "The UPDATE lifted every row above the limit, so the view now shows all of them.")


def w_count_delete(rng):
    s, t = base(rng, 5, mode="plain")
    m = _k(rng, 3, 6)
    s.run(f"CREATE VIEW v AS SELECT a FROM t WHERE a > {m};")
    s.dml(f"DELETE FROM t WHERE a > {m};", lambda: t.delete(lambda r: r["a"] > m))
    return s.item("SELECT COUNT(*) FROM v;", sum(1 for x in _vals(t) if x > m), "The rows the view would show were deleted from the table, so the view is empty.")


def w_sum_even(rng):
    s, t = base(rng, 4, mode="plain")
    s.run("CREATE VIEW v AS SELECT a FROM t WHERE a % 2 = 0;")
    s.insert(t, [(rng.randint(1, 9),) for _ in range(2)])
    return s.item("SELECT SUM(a) FROM v;", sum_([x for x in _vals(t) if x % 2 == 0]), "The view keeps the even numbers; the two new rows are included if they are even.")


def w_agg_sum(rng):
    s, t = base(rng, 3, mode="plain")
    s.run("CREATE VIEW v AS SELECT SUM(a) AS s FROM t;")
    s.insert(t, [(rng.randint(1, 9),)])
    return s.item("SELECT s FROM v;", sum(_vals(t)), "The view is worked out when asked: the SUM includes the row inserted after the view was created.")


def w_agg_max(rng):
    s, t = base(rng, 4, mode="plain")
    s.run("CREATE VIEW v AS SELECT MAX(a) AS m FROM t;")
    s.insert(t, [(rng.randint(1, 12),)])
    return s.item("SELECT m FROM v;", max_(_vals(t)), "The maximum is read from the table now, not when the view was made.")


def w_agg_count_delete(rng):
    s, t = base(rng, 5, mode="plain")
    s.run("CREATE VIEW v AS SELECT COUNT(*) AS n FROM t;")
    m = _k(rng, 3, 6)
    s.dml(f"DELETE FROM t WHERE a > {m};", lambda: t.delete(lambda r: r["a"] > m))
    return s.item("SELECT n FROM v;", len(t.rows), "The count is taken after the DELETE, so it is the number of rows left.")


def w_expr(rng):
    s, t = base(rng, 4, mode="plain")
    s.run("CREATE VIEW v AS SELECT a * 2 AS d FROM t;")
    k = _k(rng)
    upd(s, t, f"UPDATE t SET a = a + {k};", {"a": lambda r: r["a"] + k})
    return s.item("SELECT SUM(d) FROM v;", sum(x * 2 for x in _vals(t)), "d is doubled from the CURRENT a, so the UPDATE changes the view's numbers.")


def w_alias(rng):
    s, t = base(rng, 4, mode="plain")
    s.run("CREATE VIEW v(x) AS SELECT a FROM t;")
    s.insert(t, [(rng.randint(1, 9),)])
    return s.item("SELECT SUM(x) FROM v;", sum(_vals(t)), "The view renames its column to x, and still reads every row of t, the new one too.")


def w_view_on_view(rng):
    s, t = base(rng, 5, mode="plain")
    lo, hi = sorted(rng.sample(range(2, 9), 2))
    s.run(f"CREATE VIEW v1 AS SELECT a FROM t WHERE a > {lo};")
    s.run(f"CREATE VIEW v2 AS SELECT a FROM v1 WHERE a < {hi};")
    s.insert(t, [(rng.randint(1, 9),) for _ in range(2)])
    return s.item("SELECT COUNT(*) FROM v2;", sum(1 for x in _vals(t) if lo < x < hi), "v2 reads v1, which reads t: every new row has to pass both filters.")


def w_top1(rng):
    s = Script()
    ws = words(rng, 3)
    t = s.create(Table("t", [Col("n", "TEXT"), Col("a")]), [(w, v) for w, v in zip(ws, rng.sample(range(1, 10), 3))])
    s.run("CREATE VIEW v AS SELECT n FROM t ORDER BY a DESC LIMIT 1;")
    s.insert(t, [("new", 10)])
    return s.item("SELECT n FROM v;", max(t.rows, key=lambda r: r["a"])["n"], "A new row with a bigger a (10) becomes the top row, so the view now shows its name.")


def w_distinct(rng):
    s, t = base(rng, 4, 1, 5, mode="plain")
    s.run("CREATE VIEW v AS SELECT DISTINCT a FROM t;")
    s.insert(t, [(rng.randint(1, 5),) for _ in range(2)])
    return s.item("SELECT COUNT(*) FROM v;", count_distinct(_vals(t)), "DISTINCT in the view counts each value once, however many times it was inserted.")


def _grp(rng, n: int = 5):
    s = Script()
    gs = [rng.choice("xyz") for _ in range(n)]
    t = s.create(Table("t", [Col("g", "TEXT"), Col("a")]), [(g, rng.randint(1, 9)) for g in gs])
    return s, t


def w_group_count(rng):
    s, t = _grp(rng, 4)
    s.run("CREATE VIEW v AS SELECT g, SUM(a) AS s FROM t GROUP BY g;")
    s.insert(t, [("w", 1)])
    return s.item("SELECT COUNT(*) FROM v;", len({r["g"] for r in t.rows}), "The new group 'w' makes one more row in the grouped view.")


def w_group_sum(rng):
    s, t = _grp(rng, 4)
    g = rng.choice("xyz")
    s.run("CREATE VIEW v AS SELECT g, SUM(a) AS s FROM t GROUP BY g;")
    k = rng.randint(1, 9)
    s.insert(t, [(g, k)])
    tot = sum_([r["a"] for r in t.rows if r["g"] == g])
    return s.item(f"SELECT s FROM v WHERE g = '{g}';", tot, "The group's sum is recomputed with the new row inside.")


def w_ctas_stays(rng):
    s, t = base(rng, 4, mode="plain")
    n = len(t.rows)
    s.run("CREATE TABLE c AS SELECT a FROM t;")
    s.insert(t, [(rng.randint(1, 9),) for _ in range(2)])
    return s.item("SELECT COUNT(*) FROM c;", n, "CREATE TABLE ... AS SELECT is a COPY made once: it does not follow t.")


def w_view_grows(rng):
    s, t = base(rng, 4, mode="plain")
    s.run("CREATE TABLE c AS SELECT a FROM t;")
    s.run("CREATE VIEW v AS SELECT a FROM t;")
    s.insert(t, [(rng.randint(1, 9),) for _ in range(2)])
    return s.item("SELECT COUNT(*) FROM v;", len(t.rows), "The view follows t (six rows now); the copy c would still have four.")


def w_copy_vs_view_diff(rng):
    s, t = base(rng, 3, mode="plain")
    n = len(t.rows)
    s.run("CREATE TABLE c AS SELECT a FROM t;")
    s.run("CREATE VIEW v AS SELECT a FROM t;")
    s.insert(t, [(rng.randint(1, 9),) for _ in range(rng.randint(2, 3))])
    return s.item("SELECT (SELECT COUNT(*) FROM v) - (SELECT COUNT(*) FROM c);", len(t.rows) - n, "The view has all the rows, the copy only the first ones: the difference is the new rows.")


def w_join(rng):
    s = Script()
    n = rng.randint(3, 4)
    t = s.create(Table("t", [Col("id")]), [(i + 1,) for i in range(n)])
    first = rng.sample(range(1, n + 1), 2)
    u = s.create(Table("u", [Col("id")]), [(i,) for i in sorted(first)])
    s.run("CREATE VIEW v AS SELECT t.id FROM t JOIN u ON t.id = u.id;")
    k = rng.randint(1, n + 1)
    s.insert(u, [(k,)])
    ids = set(t.col("id"))
    return s.item("SELECT COUNT(*) FROM v;", sum(1 for x in u.col("id") if x in ids), "The view joins t and u again each time: a new u row counts if t has its id (a repeated u id counts again).")


def w_left_null(rng):
    s = Script()
    t = s.create(Table("t", [Col("id")]), [(1,), (2,), (3,)])
    u = s.create(Table("u", [Col("id"), Col("b")]))
    s.run("CREATE VIEW v AS SELECT b FROM t LEFT JOIN u USING(id);")
    rows = [(rng.randint(1, 4), rng.randint(1, 9)) for _ in range(3)]
    s.insert(u, rows)
    n = sum(max(1, sum(1 for r in u.rows if r["id"] == x)) for x in t.col("id"))
    return s.item("SELECT COUNT(*) FROM v;", n, "Every t row appears at least once (with NULL when u has no partner), and once more for each extra partner in u; the id 4 matches nothing.")


def w_cte(rng):
    s, t = base(rng, 5, mode="plain")
    m = _k(rng, 3, 6)
    s.dml("DELETE FROM t WHERE a = 1;", lambda: t.delete(lambda r: r["a"] == 1))
    return s.item(f"WITH s AS (SELECT a FROM t WHERE a > {m}){NL}SELECT COUNT(*) FROM s;", sum(1 for x in _vals(t) if x > m), "A WITH query is a temporary name for a SELECT, run on the table as it is now.")


def w_cte_twice(rng):
    s, t = base(rng, rng.randint(3, 4), mode="plain")
    return s.item("WITH s AS (SELECT a FROM t)" + NL + "SELECT COUNT(*) FROM s AS x, s AS y;", len(t.rows) ** 2, "The same CTE is used twice and every row pairs with every row: n times n.")


def w_cte_shadow(rng):
    s, t = base(rng, 5, mode="plain")
    return s.item("WITH t AS (SELECT 1 AS a)" + NL + "SELECT COUNT(*) FROM t;", 1, "The WITH name t hides the real table t inside this query: it has just one row.")


def w_cte_recursive(rng):
    s = Script()
    k = rng.randint(3, 8)
    return s.item(f"WITH RECURSIVE c(i) AS (SELECT 1 UNION ALL SELECT i+1 FROM c WHERE i<{k}){NL}SELECT SUM(i) FROM c;", k * (k + 1) // 2, "The recursive CTE builds 1, 2, 3 ... up to the limit; the query adds them up.")


def w_drop_create(rng):
    s, t = base(rng, 5, mode="plain")
    m = _k(rng, 3, 6)
    s.run("CREATE VIEW v AS SELECT a FROM t;")
    s.run("DROP VIEW v;")
    s.run(f"CREATE VIEW v AS SELECT a FROM t WHERE a > {m};")
    return s.item("SELECT COUNT(*) FROM v;", sum(1 for x in _vals(t) if x > m), "The old view was dropped; the new definition (with the filter) is the one that counts.")


def w_if_not_exists(rng):
    s, t = base(rng, 5, mode="plain")
    m = _k(rng, 3, 6)
    s.run(f"CREATE VIEW v AS SELECT a FROM t WHERE a > {m};")
    s.run("CREATE VIEW IF NOT EXISTS v AS SELECT a FROM t;")
    return s.item("SELECT COUNT(*) FROM v;", sum(1 for x in _vals(t) if x > m), "The second CREATE does nothing because v exists: the first definition (with the filter) stays.")


def w_temp(rng):
    s, t = base(rng, 4, mode="plain")
    s.run("CREATE TEMP VIEW v AS SELECT a FROM t WHERE a > 3;")
    s.insert(t, [(rng.randint(1, 9),)])
    return s.item("SELECT COUNT(*) FROM v;", sum(1 for x in _vals(t) if x > 3), "A TEMP view behaves the same while the connection lives: it follows the table.")


def w_text_like(rng):
    s = Script()
    ws = words(rng, 3)
    t = s.create(Table("t", [Col("n", "TEXT")]), [(w,) for w in ws])
    letter = rng.choice(ws)[0]
    s.run(f"CREATE VIEW v AS SELECT n FROM t WHERE n LIKE '{letter}%';")
    s.insert(t, [(letter + "zz",)])
    return s.item("SELECT COUNT(*) FROM v;", sum(1 for x in t.col("n") if x.lower().startswith(letter)), "The new name starts with the same letter, so it appears in the view.")


def w_case_label(rng):
    s, t = base(rng, 5, mode="plain")
    m = _k(rng, 3, 6)
    s.run(f"CREATE VIEW v AS SELECT CASE WHEN a > {m} THEN 'hi' ELSE 'lo' END AS g FROM t;")
    s.dml(f"UPDATE t SET a = {m + 1} WHERE a <= {m};", lambda: t.update({"a": lambda r: m + 1}, lambda r: r["a"] <= m))
    return s.item("SELECT COUNT(*) FROM v WHERE g = 'hi';", len(t.rows), "After the UPDATE every a is above the limit, so every row is labelled 'hi'.")


def w_where_on_view(rng):
    s, t = base(rng, 5, mode="plain")
    m, k = _k(rng, 2, 4), _k(rng, 5, 7)
    s.run(f"CREATE VIEW v AS SELECT a FROM t WHERE a > {m};")
    s.insert(t, [(rng.randint(1, 9),) for _ in range(2)])
    return s.item(f"SELECT COUNT(*) FROM v WHERE a < {k};", sum(1 for x in _vals(t) if m < x < k), "The view's filter and the query's filter both apply.")


def w_view_nulls(rng):
    s, t = base(rng, 5, nulls=1, mode="plain")
    s.run("CREATE VIEW v AS SELECT a FROM t;")
    s.insert(t, [(None,)])
    return s.item("SELECT COUNT(a) FROM v;", count_col(_vals(t)), "Both NULL rows are in the view, and COUNT(a) skips NULLs: only the real numbers are counted.")


def w_order_offset(rng):
    s, t = base(rng, 4, distinct=True, mode="plain")
    s.run("CREATE VIEW v AS SELECT a FROM t;")
    low = rng.randint(1, 3)
    s.dml(f"INSERT INTO t VALUES ({low});", lambda: t.insert({"a": low}))
    vals = sorted(x for x in _vals(t))
    if len(set(vals)) != len(vals):
        raise Retry
    return s.item("SELECT a FROM v ORDER BY a LIMIT 1 OFFSET 1;", vals[1], "OFFSET 1 skips the smallest value, so the second smallest is returned (the new row counts).")


def w_subq_avg(rng):
    s, t = base(rng, 4, mode="plain")
    s.run("CREATE VIEW v AS SELECT a FROM t WHERE a > (SELECT AVG(a) FROM t);")
    s.insert(t, [(rng.randint(10, 20),)])
    avg = sum(_vals(t)) / len(t.rows)
    return s.item("SELECT COUNT(*) FROM v;", sum(1 for x in _vals(t) if x > avg), "The average is recomputed with the big new row inside, so the threshold moves and fewer rows pass.")


def w_window(rng):
    s, t = base(rng, 4, distinct=True, mode="plain")
    s.run("CREATE VIEW v AS SELECT a, ROW_NUMBER() OVER (ORDER BY a DESC) AS r FROM t;")
    big = rng.randint(10, 15)
    s.dml(f"INSERT INTO t VALUES ({big});", lambda: t.insert({"a": big}))
    return s.item("SELECT a FROM v WHERE r = 1;", max_(_vals(t)), "Row number 1 (largest first) is recomputed from the current rows: the new big value.")


def w_union(rng):
    s = Script()
    t = s.create(Table("t", [Col("a")]), [(v,) for v in rng.sample(range(1, 7), 3)])
    u = s.create(Table("u", [Col("a")]), [(v,) for v in rng.sample(range(1, 7), 3)])
    s.run("CREATE VIEW v AS SELECT a FROM t UNION SELECT a FROM u;")
    k = rng.randint(1, 8)
    s.insert(u, [(k,)])
    return s.item("SELECT COUNT(*) FROM v;", len(set(_vals(t)) | set(_vals(u))), "UNION removes duplicates between the tables, so each different a counts once.")


def w_min_after_delete(rng):
    s, t = base(rng, 5, distinct=True, mode="plain")
    s.run("CREATE VIEW v AS SELECT MIN(a) AS m FROM t;")
    low = min(_vals(t))
    s.dml(f"DELETE FROM t WHERE a = {low};", lambda: t.delete(lambda r: r["a"] == low))
    return s.item("SELECT m FROM v;", min_(_vals(t)), "With the smallest row deleted, the view reports the next smallest.")


def w_in_view_delete(rng):
    s, t = base(rng, 6, mode="plain")
    m = _k(rng, 3, 6)
    s.run(f"CREATE VIEW v AS SELECT a FROM t WHERE a > {m};")
    s.dml("DELETE FROM t WHERE a IN (SELECT a FROM v);", lambda: t.delete(lambda r: r["a"] > m))
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A view can be used inside another statement: every row the view would show is deleted from t.")


def w_instead_of(rng):
    s = Script()
    t = s.create(Table("t", [Col("a")]), [(rng.randint(1, 9),)])
    s.run("CREATE VIEW v AS SELECT a FROM t;")
    s.run("CREATE TRIGGER g INSTEAD OF INSERT ON v BEGIN INSERT INTO t VALUES (NEW.a); END;")
    x = rng.randint(1, 9)
    s.dml(f"INSERT INTO v VALUES ({x});", lambda: t.insert({"a": x}))
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A view cannot be inserted into directly, so the INSTEAD OF trigger runs and inserts the row into t.")


def w_count_star_vs_col(rng):
    s, t = base(rng, 4, nulls=1, mode="plain")
    s.run("CREATE VIEW v AS SELECT a FROM t;")
    s.insert(t, [(None,), (rng.randint(1, 9),)])
    return s.item("SELECT COUNT(*) FROM v;", len(t.rows), "COUNT(*) counts rows, NULL ones included; the view shows every row of t.")


def w_not_in_view(rng):
    s, t = base(rng, 4, mode="plain")
    m = _k(rng, 3, 6)
    s.run(f"CREATE VIEW h AS SELECT a FROM t WHERE a > {m};")
    s.insert(t, [(rng.randint(1, 9),) for _ in range(2)])
    return s.item("SELECT COUNT(*) FROM t WHERE a NOT IN (SELECT a FROM h);", sum(1 for x in _vals(t) if x <= m), "The rows the view does not show are the ones at or below the limit; the view includes the new rows.")


def w_view_after_update_all(rng):
    s, t = base(rng, 4, mode="plain")
    s.run("CREATE VIEW v AS SELECT SUM(a) AS s FROM t;")
    k = _k(rng)
    upd(s, t, f"UPDATE t SET a = a * {k};", {"a": lambda r: r["a"] * k})
    return s.item("SELECT s FROM v;", sum(_vals(t)), "The view's SUM is worked out after the UPDATE multiplied every row.")


def w_view_subquery_in(rng):
    s, t = base(rng, 5, mode="plain")
    m = _k(rng, 3, 6)
    s.run(f"CREATE VIEW v AS SELECT a FROM t WHERE a > {m};")
    s.dml("UPDATE t SET a = 0 WHERE a IN (SELECT a FROM v);", lambda: t.update({"a": lambda r: 0}, lambda r: r["a"] > m))
    return s.item("SELECT COUNT(*) FROM v;", 0, "Every row the view showed was set to 0, so now no row passes its filter.")


VIEWS: list[Maker] = [fit(f) for f in (
    w_count_insert, w_count_update, w_count_delete, w_sum_even, w_agg_sum, w_agg_max, w_agg_count_delete, w_expr, w_alias,
    w_view_on_view, w_top1, w_distinct, w_group_count, w_group_sum, w_ctas_stays, w_view_grows, w_copy_vs_view_diff, w_join,
    w_left_null, w_cte, w_cte_twice, w_cte_shadow, w_cte_recursive, w_drop_create, w_if_not_exists, w_temp, w_text_like,
    w_case_label, w_where_on_view, w_view_nulls, w_order_offset, w_subq_avg, w_window, w_union, w_min_after_delete,
    w_in_view_delete, w_instead_of, w_count_star_vs_col, w_not_in_view, w_view_after_update_all, w_view_subquery_in)]


# ── 8. Transaction Rollback ─────────────────────────────────────────────

def _tx(rng, n: int | None = None, lo: int = 1, hi: int = 9, pk: bool = False, **kw):
    """t(a INT) filled and COMMITted: the state a transaction starts from."""
    s, t = base(rng, n or rng.randint(2, 5), lo, hi, mode="plain" if not pk else "ids", **kw)
    s.commit_setup()
    return s, t


def _ins(s: Script, t: Table, rng, n: int = 1) -> list[int]:
    vs = [rng.randint(1, 9) for _ in range(n)]
    s.insert(t, [(v,) for v in vs])
    return vs


def x_rollback_update(rng):
    s, t = _tx(rng)
    k = _k(rng)
    s.begin()
    upd(s, t, f"UPDATE t SET a = a + {k};", {"a": lambda r: r["a"] + k})
    s.rollback()
    return s.item("SELECT SUM(a) FROM t;", sum(_vals(t)), "ROLLBACK undoes everything since BEGIN: the sum is the original one.")


def x_commit_update(rng):
    s, t = _tx(rng)
    k = _k(rng)
    s.begin()
    upd(s, t, f"UPDATE t SET a = a + {k};", {"a": lambda r: r["a"] + k})
    s.commit()
    return s.item("SELECT SUM(a) FROM t;", sum(_vals(t)), "COMMIT makes the change permanent.")


def x_rollback_insert(rng):
    s, t = _tx(rng)
    s.begin()
    _ins(s, t, rng, 2)
    s.rollback()
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The two inserted rows were rolled back, so only the original rows are there.")


def x_commit_insert(rng):
    s, t = _tx(rng)
    s.begin()
    _ins(s, t, rng, 2)
    s.commit()
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The transaction was committed, so the two new rows stay.")


def x_rollback_delete(rng):
    s, t = _tx(rng)
    s.begin()
    s.dml("DELETE FROM t;", lambda: t.delete())
    s.rollback()
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Even a DELETE of every row is undone by ROLLBACK.")


def x_commit_delete(rng):
    s, t = _tx(rng)
    m = _k(rng, 3, 6)
    s.begin()
    s.dml(f"DELETE FROM t WHERE a > {m};", lambda: t.delete(lambda r: r["a"] > m))
    s.commit()
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The committed DELETE stays.")


def x_open_txn_sees(rng):
    s, t = _tx(rng)
    k = _k(rng)
    s.begin()
    upd(s, t, f"UPDATE t SET a = a + {k};", {"a": lambda r: r["a"] + k})
    return s.item("SELECT SUM(a) FROM t;", sum(_vals(t)), "No COMMIT or ROLLBACK yet: the connection itself still sees its own changes.")


def x_savepoint_rollback(rng):
    s, t = _tx(rng)
    s.savepoint("s")
    _ins(s, t, rng)
    s.rollback_to("s")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "ROLLBACK TO s undoes what happened after SAVEPOINT s.")


def x_savepoint_release(rng):
    s, t = _tx(rng)
    s.savepoint("s")
    _ins(s, t, rng)
    s.release("s")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "RELEASE just forgets the savepoint; the changes stay.")


def x_two_sp_inner(rng):
    s, t = _tx(rng)
    s.begin()
    s.savepoint("a")
    _ins(s, t, rng)
    s.savepoint("b")
    _ins(s, t, rng)
    s.rollback_to("b")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Only the insert after savepoint b is undone; the one after a stays.")


def x_two_sp_outer(rng):
    s, t = _tx(rng)
    s.begin()
    s.savepoint("a")
    _ins(s, t, rng)
    s.savepoint("b")
    _ins(s, t, rng)
    s.rollback_to("a")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Rolling back to the outer savepoint a undoes both inserts.")


def x_rollback_to_then_more(rng):
    s, t = _tx(rng)
    s.begin()
    s.savepoint("s")
    upd(s, t, "UPDATE t SET a = 0;", {"a": lambda r: 0})
    s.rollback_to("s")
    _ins(s, t, rng)
    s.commit()
    return s.item("SELECT SUM(a) FROM t;", sum(_vals(t)), "The UPDATE to 0 is undone, the later INSERT and the COMMIT are kept.")


def x_rollback_to_twice(rng):
    s, t = _tx(rng)
    s.savepoint("s")
    _ins(s, t, rng)
    s.rollback_to("s")
    _ins(s, t, rng)
    s.rollback_to("s")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "ROLLBACK TO keeps the savepoint, so a second ROLLBACK TO s undoes the second insert as well.")


def x_release_then_rollback(rng):
    s, t = _tx(rng)
    s.begin()
    s.savepoint("s")
    _ins(s, t, rng)
    s.release("s")
    s.rollback()
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "RELEASE inside a transaction does not commit; the final ROLLBACK still undoes everything.")


def x_commit_then_rollback(rng):
    s, t = _tx(rng)
    s.begin()
    _ins(s, t, rng)
    s.commit()
    s.begin()
    _ins(s, t, rng)
    s.rollback()
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The first transaction was committed (kept); only the second one was rolled back.")


def x_two_txns(rng):
    s, t = _tx(rng)
    k = _k(rng)
    s.begin()
    upd(s, t, "UPDATE t SET a = a * 2;", {"a": lambda r: r["a"] * 2})
    s.rollback()
    s.begin()
    upd(s, t, f"UPDATE t SET a = a + {k};", {"a": lambda r: r["a"] + k})
    s.commit()
    return s.item("SELECT SUM(a) FROM t;", sum(_vals(t)), "The doubling was rolled back; only the +k transaction counts.")


def _bank(rng):
    s = Script()
    t = s.create(Table("t", [Col("id"), Col("bal")]), [(1, rng.randint(5, 9)), (2, rng.randint(1, 4))])
    s.commit_setup()
    return s, t


def x_transfer_commit(rng):
    s, t = _bank(rng)
    x = rng.randint(1, 4)
    s.begin()
    upd(s, t, f"UPDATE t SET bal = bal - {x} WHERE id = 1;", {"bal": lambda r: r["bal"] - x}, lambda r: r["id"] == 1)
    upd(s, t, f"UPDATE t SET bal = bal + {x} WHERE id = 2;", {"bal": lambda r: r["bal"] + x}, lambda r: r["id"] == 2)
    s.commit()
    return s.item("SELECT bal FROM t WHERE id = 2;", t.one("bal", lambda r: r["id"] == 2), "Both updates were committed, so account 2 received the money.")


def x_transfer_rollback(rng):
    s, t = _bank(rng)
    x = rng.randint(1, 4)
    s.begin()
    upd(s, t, f"UPDATE t SET bal = bal - {x} WHERE id = 1;", {"bal": lambda r: r["bal"] - x}, lambda r: r["id"] == 1)
    upd(s, t, f"UPDATE t SET bal = bal + {x} WHERE id = 2;", {"bal": lambda r: r["bal"] + x}, lambda r: r["id"] == 2)
    s.rollback()
    return s.item("SELECT bal FROM t WHERE id = 1;", t.one("bal", lambda r: r["id"] == 1), "The whole transfer was rolled back, so account 1 still has its original balance.")


def x_transfer_total(rng):
    s, t = _bank(rng)
    x = rng.randint(1, 4)
    s.begin()
    upd(s, t, f"UPDATE t SET bal = bal - {x} WHERE id = 1;", {"bal": lambda r: r["bal"] - x}, lambda r: r["id"] == 1)
    upd(s, t, f"UPDATE t SET bal = bal + {x} WHERE id = 2;", {"bal": lambda r: r["bal"] + x}, lambda r: r["id"] == 2)
    s.commit()
    return s.item("SELECT SUM(bal) FROM t;", sum(_vals(t, "bal")), "Money moved, none created: the total is the same before and after the transfer.")


def x_half_transfer(rng):
    s, t = _bank(rng)
    x = rng.randint(1, 4)
    s.begin()
    upd(s, t, f"UPDATE t SET bal = bal - {x} WHERE id = 1;", {"bal": lambda r: r["bal"] - x}, lambda r: r["id"] == 1)
    s.commit()
    return s.item("SELECT SUM(bal) FROM t;", sum(_vals(t, "bal")), "Only the withdrawal was committed (no matching deposit): the total dropped by x.")


def x_changes_after_rollback(rng):
    s, t = _tx(rng)
    s.begin()
    s.dml("DELETE FROM t;", lambda: t.delete())
    s.rollback()
    return s.item("SELECT changes();", s.changes, "changes() still reports the last DELETE (all the rows); a ROLLBACK does not reset it.")


def x_id_reuse(rng):
    s = Script()
    n = rng.randint(2, 5)
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True), Col("a")]), [(i + 1, rng.randint(1, 9)) for i in range(n)])
    s.commit_setup()
    s.begin()
    s.insert(t, [(7,)], ["a"])
    s.rollback()
    s.insert(t, [(8,)], ["a"])
    return s.item("SELECT MAX(id) FROM t;", max_(t.col("id")), "The rolled-back row never existed, so its id is free again for the next insert.")


def x_autoinc_rollback(rng):
    s = Script()
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True, autoinc=True), Col("a")]), [(rng.randint(1, 9),) for _ in range(rng.randint(2, 4))], ["a"])
    s.commit_setup()
    s.begin()
    s.insert(t, [(7,)], ["a"])
    s.rollback()
    s.insert(t, [(8,)], ["a"])
    return s.item("SELECT MAX(id) FROM t;", max_(t.col("id")), "AUTOINCREMENT keeps its counter in a table, and the rollback undoes that too: the rolled-back id is reused.")


def x_sp_no_begin(rng):
    s, t = _tx(rng)
    s.savepoint("s")
    _ins(s, t, rng, 2)
    s.rollback_to("s")
    s.release("s")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A SAVEPOINT works without BEGIN: the two inserts are undone, then the savepoint is released.")


def x_begin_words(rng):
    s, t = _tx(rng)
    w = rng.choice(["BEGIN TRANSACTION", "BEGIN IMMEDIATE", "BEGIN DEFERRED", "BEGIN EXCLUSIVE"])
    s.begin(w)
    _ins(s, t, rng)
    s.rollback()
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "All the BEGIN spellings start a transaction; ROLLBACK ends it and undoes the insert.")


def x_end_words(rng):
    s, t = _tx(rng)
    w = rng.choice(["END", "END TRANSACTION", "COMMIT TRANSACTION"])
    s.begin()
    _ins(s, t, rng)
    s.commit(w)
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "END is another name for COMMIT: the insert is kept.")


def x_partial(rng):
    s, t = _tx(rng)
    k = _k(rng)
    s.begin()
    upd(s, t, f"UPDATE t SET a = a + {k};", {"a": lambda r: r["a"] + k})
    s.savepoint("s")
    upd(s, t, "UPDATE t SET a = 0;", {"a": lambda r: 0})
    s.rollback_to("s")
    s.commit()
    return s.item("SELECT SUM(a) FROM t;", sum(_vals(t)), "ROLLBACK TO s undoes only the zeroing; the +k update before the savepoint is committed.")


def x_rollback_all_after_sp(rng):
    s, t = _tx(rng)
    s.begin()
    _ins(s, t, rng)
    s.savepoint("s")
    _ins(s, t, rng)
    s.rollback()
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A plain ROLLBACK ends the whole transaction, savepoints and all.")


def x_nested_release(rng):
    s, t = _tx(rng)
    s.begin()
    s.savepoint("a")
    s.savepoint("b")
    _ins(s, t, rng)
    s.release("b")
    s.rollback_to("a")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Releasing b keeps its changes inside a; rolling back to a then undoes them anyway.")


def x_sp_delete(rng):
    s, t = _tx(rng)
    s.begin()
    s.savepoint("s")
    s.dml("DELETE FROM t WHERE a > 3;", lambda: t.delete(lambda r: r["a"] > 3))
    s.rollback_to("s")
    return s.item("SELECT SUM(a) FROM t;", sum(_vals(t)), "The DELETE happened after the savepoint, so it is undone.")


def x_insert_select(rng):
    s, t = _tx(rng, 3)
    s.begin()
    s.insert_sql("INSERT INTO t SELECT a FROM t;", t, [(r["a"],) for r in list(t.rows)], ["a"])
    s.rollback()
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The copy of every row was rolled back with the rest of the transaction.")


def x_upsert(rng):
    s = Script()
    t = s.create(Table("kv", [Col("k", "TEXT", pk=True), Col("v")]), [("a", rng.randint(1, 9)), ("b", rng.randint(1, 9))])
    s.commit_setup()
    k, n = rng.choice("ab"), rng.randint(1, 9)
    s.begin()
    s.dml(f"INSERT INTO kv VALUES ('{k}',{n}) ON CONFLICT(k) DO UPDATE SET v = v + excluded.v;",
          lambda: t.insert({"k": k, "v": n}, "abort", (("k",), {"v": lambda o, e: o["v"] + e["v"]}, None)))
    s.rollback()
    return s.item("SELECT SUM(v) FROM kv;", sum(t.col("v")), "The upsert added to v inside the transaction, and the ROLLBACK put the old value back.")


def x_replace(rng):
    s = Script()
    t = s.create(Table("kv", [Col("k", "TEXT", pk=True), Col("v")]), [("a", rng.randint(1, 9)), ("b", rng.randint(1, 9))])
    s.commit_setup()
    s.begin()
    s.insert(t, [(rng.choice("ab"), rng.randint(1, 9))], mode="replace")
    s.rollback()
    return s.item("SELECT SUM(v) FROM kv;", sum(_vals(t, "v")), "The REPLACE (delete + insert) is undone as one, so both original rows are back.")


def x_same_name(rng):
    s, t = _tx(rng)
    s.begin()
    s.savepoint("s")
    _ins(s, t, rng)
    s.savepoint("s")
    _ins(s, t, rng)
    s.rollback_to("s")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Two savepoints share the name s; ROLLBACK TO goes to the most recent one, so only the second insert is undone.")


def x_commit_after_sp(rng):
    s, t = _tx(rng)
    s.begin()
    _ins(s, t, rng)
    s.savepoint("s")
    _ins(s, t, rng)
    s.rollback_to("s")
    s.commit()
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The insert before the savepoint is kept by the COMMIT; the one after it was undone.")


def x_alter_rollback(rng):
    s, t = _tx(rng)
    s.begin()
    s.run("ALTER TABLE t ADD COLUMN b INT;")
    s.rollback()
    return s.item("SELECT COUNT(*) FROM pragma_table_info('t');", len(t.cols), "In SQLite even ALTER TABLE is part of the transaction: the rollback removes the new column.")


def x_drop_rollback(rng):
    s, t = _tx(rng)
    s.begin()
    s.run("DROP TABLE t;")
    s.rollback()
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "DROP TABLE is rolled back too: the table and all its rows are back.")


def x_text(rng):
    s, t = base_named(rng, 3)
    s.commit_setup()
    k = rng.randint(1, 3)
    s.begin()
    s.dml(f"UPDATE t SET n = UPPER(n) WHERE id = {k};", lambda: t.update({"n": lambda r: r["n"].upper()}, lambda r: r["id"] == k))
    s.rollback()
    return s.item(f"SELECT n FROM t WHERE id = {k};", t.one("n", lambda r: r["id"] == k), "The upper-casing was rolled back, so the name is as it was.")


def x_sum_two_inserts(rng):
    s, t = _tx(rng)
    s.begin()
    _ins(s, t, rng)
    s.savepoint("s")
    _ins(s, t, rng)
    s.release("s")
    s.commit()
    return s.item("SELECT SUM(a) FROM t;", sum(_vals(t)), "Both inserts are kept: RELEASE did not undo anything and COMMIT made them permanent.")


def x_rollback_twice_ok(rng):
    s, t = _tx(rng)
    s.begin()
    _ins(s, t, rng)
    s.rollback()
    s.begin()
    _ins(s, t, rng)
    s.rollback()
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Two transactions, both rolled back: nothing was ever kept.")


def x_update_rollback_to_value(rng):
    s, t = _tx(rng, rng.randint(3, 5), pk=True)
    k = rng.randint(1, len(t.rows))
    s.begin()
    upd(s, t, f"UPDATE t SET a = 0 WHERE id = {k};", {"a": lambda r: 0}, lambda r: r["id"] == k)
    s.rollback()
    return s.item(f"SELECT a FROM t WHERE id = {k};", t.one("a", lambda r: r["id"] == k), "The row got 0 inside the transaction, but ROLLBACK brought its old value back.")


def x_savepoint_update(rng):
    s, t = _tx(rng)
    k = _k(rng)
    s.savepoint("s")
    upd(s, t, f"UPDATE t SET a = a + {k};", {"a": lambda r: r["a"] + k})
    s.release("s")
    return s.item("SELECT SUM(a) FROM t;", sum(_vals(t)), "RELEASE keeps what the savepoint section did.")


TXNS: list[Maker] = [fit(f) for f in (
    x_rollback_update, x_commit_update, x_rollback_insert, x_commit_insert, x_rollback_delete, x_commit_delete,
    x_open_txn_sees, x_savepoint_rollback, x_savepoint_release, x_two_sp_inner, x_two_sp_outer, x_rollback_to_then_more,
    x_rollback_to_twice, x_release_then_rollback, x_commit_then_rollback, x_two_txns, x_transfer_commit, x_transfer_rollback,
    x_transfer_total, x_half_transfer, x_changes_after_rollback, x_id_reuse, x_autoinc_rollback, x_sp_no_begin, x_begin_words,
    x_end_words, x_partial, x_rollback_all_after_sp, x_nested_release, x_sp_delete, x_insert_select, x_upsert, x_replace,
    x_same_name, x_commit_after_sp, x_alter_rollback, x_drop_rollback, x_text, x_sum_two_inserts, x_rollback_twice_ok, x_update_rollback_to_value,
    x_savepoint_update)]
