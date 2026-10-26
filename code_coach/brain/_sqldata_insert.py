"""SQL data pack, part 3: Insert & Default (`INSERTS`).

Multi-row VALUES, INSERT ... SELECT (UNION, DISTINCT, GROUP BY, LIMIT, an aggregate that always yields one row), omitted
columns (DEFAULT or NULL; an explicit NULL beats a DEFAULT), DEFAULT VALUES, INTEGER PRIMARY KEY ids, column affinity
(`'5'` into an INT column), CREATE TABLE AS, `changes()` and `last_insert_rowid()`.
"""

from __future__ import annotations

from ._model import Maker
from ._sql_model import (count_col, fit, max_, sum_, type_of, words)
from ._sqldata_model import Col, Script, Table, base


def _k(rng, lo: int = 2, hi: int = 6) -> int:
    return rng.randint(lo, hi)


def _dt(rng, n: int = 0, d: int | None = None, name: str = "t", not_null: bool = False):
    """t(a INT, b INT DEFAULT d [NOT NULL]) with `n` rows given a (so b is the default)."""
    d = d if d is not None else rng.randint(2, 9)
    s = Script()
    t = s.create(Table(name, [Col("a"), Col("b", "INT", default=d, not_null=not_null)]))
    return s, t, d


def _src(rng, n: int = 5, lo: int = 1, hi: int = 9, distinct: bool = False):
    """u(x INT) with n values."""
    vals = rng.sample(range(lo, hi + 1), n) if distinct else [rng.randint(lo, hi) for _ in range(n)]
    s = Script()
    u = s.create(Table("u", [Col("x")]), [(v,) for v in vals])
    return s, u


# ── 3. Insert & Default ─────────────────────────────────────────────────

def i_multi_sum(rng):
    s, t = base(rng, 3, mode="plain")
    vs = [(rng.randint(1, 9),) for _ in range(3)]
    s.insert(t, vs)
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "One INSERT with several value lists adds one row for each.")


def i_multi_count(rng):
    s, t = base(rng, rng.randint(3, 5))
    s.insert(t, [(rng.randint(1, 9),) for _ in range(rng.randint(2, 3))], ["a"])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The table had its first rows, and every value list of the new INSERT adds one more.")


def i_select_where(rng):
    s, u = _src(rng)
    t = s.create(Table("t", [Col("a")]))
    m = _k(rng, 3, 6)
    rows = [(r["x"],) for r in u.rows if r["x"] > m]
    s.insert_sql(f"INSERT INTO t SELECT x FROM u WHERE x > {m};", t, rows)
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "INSERT ... SELECT copies the rows the SELECT returns: here the x above the limit.")


def i_select_expr(rng):
    s, t = base(rng, 3, mode="plain")
    k = _k(rng)
    s.insert_sql(f"INSERT INTO t SELECT a * {k} FROM t;", t, [(r["a"] * k,) for r in list(t.rows)])
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "The SELECT reads the old rows, and the multiplied copies are added next to them.")


def i_self_double(rng):
    s, t = base(rng, rng.randint(3, 5))
    s.insert_sql("INSERT INTO t(a) SELECT a FROM t;", t, [(r["a"],) for r in list(t.rows)], ["a"])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The SELECT is read before the INSERT adds anything, so every row is copied once and the count doubles.")


def i_default_sum(rng):
    s, t, d = _dt(rng)
    m = rng.randint(2, 3)
    s.insert(t, [(rng.randint(1, 9),) for _ in range(m)], ["a"])
    return s.item("SELECT SUM(b) FROM t;", sum(t.col("b")), "b was left out of the INSERT, so every new row gets its DEFAULT.")


def i_default_one(rng):
    s, t, d = _dt(rng)
    s.insert(t, [(1,)], ["a"])
    s.insert(t, [(2, d + 3)])
    return s.item("SELECT b FROM t WHERE a = 1;", t.one("b", lambda r: r["a"] == 1), "Row 1 left b out and got the DEFAULT; the other row gave its own b.")


def i_omit_null(rng):
    s = Script()
    t = s.create(Table("t", [Col("a"), Col("b")]))
    s.insert(t, [(rng.randint(1, 9),) for _ in range(rng.randint(2, 4))], ["a"])
    s.insert(t, [(rng.randint(1, 9), rng.randint(1, 9))])
    return s.item("SELECT COUNT(b) FROM t;", count_col(t.col("b")), "A column with no DEFAULT is NULL when left out, and COUNT(b) skips NULLs.")


def i_explicit_null(rng):
    s, t, d = _dt(rng)
    s.insert(t, [(1,)], ["a"])
    s.insert(t, [(2, None)])
    return s.item("SELECT SUM(b) FROM t;", sum_(t.col("b")), "An omitted column takes the DEFAULT, but an explicit NULL stays NULL: only row 1 has a b.")


def i_default_values(rng):
    s = Script()
    d1, d2 = rng.randint(2, 9), rng.randint(2, 9)
    t = s.create(Table("t", [Col("a", "INT", default=d1), Col("b", "INT", default=d2)]))
    n = rng.randint(1, 3)
    for _ in range(n):
        s.dml("INSERT INTO t DEFAULT VALUES;", lambda: t.insert({}))
    return s.item("SELECT SUM(a + b) FROM t;", sum(r["a"] + r["b"] for r in t.rows), "DEFAULT VALUES inserts a row where every column takes its DEFAULT.")


def i_default_values_id(rng):
    s = Script()
    d = rng.randint(2, 9)
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True), Col("a", "INT", default=d)]))
    n = rng.randint(2, 4)
    for _ in range(n):
        s.dml("INSERT INTO t DEFAULT VALUES;", lambda: t.insert({}))
    return s.item("SELECT SUM(id + a) FROM t;", sum(r["id"] + r["a"] for r in t.rows), "Each row gets the next id (1, 2, 3 ...) and the DEFAULT for a.")


def i_text_default(rng):
    s = Script()
    t = s.create(Table("t", [Col("a"), Col("s", "TEXT", default=rng.choice(["new", "open", "todo"]))]))
    n = rng.randint(2, 4)
    s.insert(t, [(i + 1,) for i in range(n)], ["a"])
    s.insert(t, [(n + 1, "done")])
    return s.item(f"SELECT COUNT(*) FROM t WHERE s = '{t.col_of('s').default}';", t.col("s").count(t.col_of("s").default), "Only the rows that left s out got the DEFAULT; the 'done' row gave its own.")


def i_negative_default(rng):
    s, t, d = _dt(rng, d=-rng.randint(1, 5))
    s.insert(t, [(rng.randint(1, 9),) for _ in range(3)], ["a"])
    return s.item("SELECT SUM(b) FROM t;", sum(t.col("b")), "A DEFAULT can be a negative number; every row without b gets it.")


def i_not_null_default(rng):
    s, t, d = _dt(rng, not_null=True)
    s.insert(t, [(rng.randint(1, 9),) for _ in range(3)], ["a"])
    return s.item("SELECT SUM(b) FROM t;", sum(t.col("b")), "NOT NULL is happy: the omitted column takes its DEFAULT, never NULL.")


def i_auto_id(rng):
    s, t = base(rng, rng.randint(3, 5))
    s.insert(t, [(rng.randint(1, 9),)], ["a"])
    return s.item("SELECT MAX(id) FROM t;", max_(t.col("id")), "An INTEGER PRIMARY KEY you leave out becomes the highest id plus one.")


def i_null_id(rng):
    s, t = base(rng, rng.randint(3, 5))
    s.insert(t, [(None, rng.randint(1, 9))])
    return s.item("SELECT MAX(id) FROM t;", max_(t.col("id")), "Giving NULL for an INTEGER PRIMARY KEY is the same as leaving it out: SQLite picks the next id.")


def i_explicit_id_then_auto(rng):
    s, t = base(rng, 3)
    k = rng.randint(8, 20)
    s.insert(t, [(k, rng.randint(1, 9))])
    s.insert(t, [(rng.randint(1, 9),)], ["a"])
    return s.item("SELECT MAX(id) FROM t;", max_(t.col("id")), "After the row with a big explicit id, the next automatic id is that id plus one.")


def i_union_dedupe(rng):
    s, u = _src(rng, 3, 1, 5)
    v = s.create(Table("v", [Col("x")]), [(rng.randint(1, 5),) for _ in range(3)])
    t = s.create(Table("t", [Col("a")]))
    rows = sorted({r["x"] for r in u.rows} | {r["x"] for r in v.rows})
    s.insert_sql("INSERT INTO t SELECT x FROM u UNION SELECT x FROM v;", t, [(x,) for x in rows])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "UNION removes duplicates, so each different x is inserted once.")


def i_union_all(rng):
    s, u = _src(rng, rng.randint(2, 4), 1, 5)
    v = s.create(Table("v", [Col("x")]), [(rng.randint(1, 5),) for _ in range(rng.randint(2, 4))])
    t = s.create(Table("t", [Col("a")]))
    rows = [r["x"] for r in u.rows] + [r["x"] for r in v.rows]
    s.insert_sql("INSERT INTO t SELECT x FROM u UNION ALL SELECT x FROM v;", t, [(x,) for x in rows])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "UNION ALL keeps every row of both tables, duplicates included.")


def i_limit(rng):
    s, u = _src(rng, 5, distinct=True)
    t = s.create(Table("t", [Col("a")]))
    top = sorted((r["x"] for r in u.rows), reverse=True)[:2]
    s.insert_sql("INSERT INTO t SELECT x FROM u ORDER BY x DESC LIMIT 2;", t, [(x,) for x in top])
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "ORDER BY ... LIMIT 2 chooses the two biggest x, and only those are inserted.")


def i_distinct(rng):
    s, u = _src(rng, 6, 1, 4)
    t = s.create(Table("t", [Col("a")]))
    s.insert_sql("INSERT INTO t SELECT DISTINCT x FROM u;", t, [(x,) for x in sorted({r["x"] for r in u.rows})])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "DISTINCT collapses repeated x values before they are inserted.")


def i_group(rng):
    s, u = _src(rng, 6, 1, 4)
    t = s.create(Table("t", [Col("x"), Col("n")]))
    counts: dict = {}
    for r in u.rows:
        counts[r["x"]] = counts.get(r["x"], 0) + 1
    s.insert_sql("INSERT INTO t SELECT x, COUNT(*) FROM u GROUP BY x;", t, sorted(counts.items()))
    return s.item("SELECT MAX(n) FROM t;", max_(t.col("n")), "One row per different x is inserted, holding how often x occurs; the biggest count is asked.")


def i_agg_empty(rng):
    s, t = base(rng, rng.randint(3, 5), mode="plain")
    s.insert_sql("INSERT INTO t SELECT MAX(a) FROM t WHERE a > 99;", t, [(None,)])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "An aggregate with no GROUP BY always returns one row, even over no rows (MAX is NULL): so one NULL row is inserted.")


def i_agg_empty_count_col(rng):
    s, t = base(rng, rng.randint(3, 5), mode="plain")
    s.insert_sql("INSERT INTO t SELECT MAX(a) FROM t WHERE a > 99;", t, [(None,)])
    return s.item("SELECT COUNT(a) FROM t;", count_col(t.col("a")), "The extra row is NULL, and COUNT(a) does not count a NULL: still the original rows.")


def i_sum_row(rng):
    s, t = base(rng, 3, mode="plain")
    total = sum(t.col("a"))
    s.insert_sql("INSERT INTO t SELECT SUM(a) FROM t;", t, [(total,)])
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "The new row holds the old total, so the new total is twice the old one.")


def i_max_plus(rng):
    s, t = base(rng, 4, mode="plain")
    top = max(t.col("a"))
    s.insert_sql("INSERT INTO t SELECT MAX(a) + 1 FROM t;", t, [(top + 1,)])
    return s.item("SELECT MAX(a) FROM t;", max_(t.col("a")), "The inserted row is one more than the old maximum, so it is the new maximum.")


def i_not_in_guard(rng):
    s, t = base(rng, 3, 1, 6, mode="plain", distinct=True)
    u = s.create(Table("u", [Col("x")]), [(v,) for v in rng.sample(range(1, 7), 3)])
    have = set(t.col("a"))
    s.insert_sql("INSERT INTO t SELECT x FROM u WHERE x NOT IN (SELECT a FROM t);", t, [(r["x"],) for r in u.rows if r["x"] not in have])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Only the x values that t does not hold yet are copied: no value ends up twice.")


def i_join(rng):
    s, u = _src(rng, 3, distinct=True)
    v = s.create(Table("v", [Col("x")]), [(x,) for x in rng.sample(range(1, 10), 3)])
    t = s.create(Table("t", [Col("a")]))
    both = [(r["x"],) for r in u.rows if r["x"] in v.col("x")]
    s.insert_sql("INSERT INTO t SELECT u.x FROM u JOIN v ON u.x = v.x;", t, both)
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Only the x values found in both tables survive the join and are inserted (0 if none match).")


def i_recursive(rng):
    s = Script()
    t = s.create(Table("t", [Col("a")]))
    k = rng.randint(3, 8)
    s.insert_sql(f"INSERT INTO t WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM c WHERE x<{k}) SELECT x FROM c;", t,
                 [(i,) for i in range(1, k + 1)])
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "The recursive WITH produces 1, 2, 3 ... up to the limit, and INSERT adds them all.")


def i_values_expr(rng):
    s, t = base(rng, 2, mode="plain")
    a, b, c = _k(rng), _k(rng), _k(rng)
    s.insert_sql(f"INSERT INTO t VALUES ({a}+{b}*{c});", t, [(a + b * c,)])
    return s.item("SELECT MAX(a) FROM t;", max_(t.col("a")), "VALUES takes expressions; * goes before +. The new value is compared with the old rows.")


def i_values_subq(rng):
    s, t = base(rng, rng.randint(3, 5), mode="plain")
    n = len(t.rows)
    s.insert_sql("INSERT INTO t VALUES ((SELECT COUNT(*) FROM t));", t, [(n,)])
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "The new row holds the number of rows there were before it was added.")


def i_concat_text(rng):
    s = Script()
    t = s.create(Table("t", [Col("n", "TEXT")]))
    a, b = words(rng, 2)
    s.insert_sql(f"INSERT INTO t VALUES ('{a}' || '{b}');", t, [(a + b,)])
    return s.item("SELECT n FROM t;", t.col("n")[0], "|| glues the two words into one value before it is stored.")


def i_order_columns(rng):
    s = Script()
    t = s.create(Table("t", [Col("a"), Col("b")]))
    x, y = rng.sample(range(1, 10), 2)
    s.insert_sql(f"INSERT INTO t(b, a) VALUES ({x}, {y});", t, [(x, y)], ["b", "a"])
    return s.item("SELECT a FROM t;", t.col("a")[0], "Values are matched to the columns in the order the list names them: b first, then a.")


def i_positional(rng):
    s = Script()
    u = s.create(Table("u", [Col("b"), Col("a")]), [tuple(rng.sample(range(1, 10), 2))])
    t = s.create(Table("t", [Col("a"), Col("b")]))
    s.insert_sql("INSERT INTO t SELECT * FROM u;", t, [(u.rows[0]["b"], u.rows[0]["a"])])
    return s.item("SELECT a FROM t;", t.col("a")[0], "Without a column list the copy is by position, not by name: u's first column (b) lands in t's first column (a).")


def i_text_to_int(rng):
    s = Script()
    t = s.create(Table("t", [Col("a")]))
    v = rng.randint(1, 99)
    s.insert_sql(f"INSERT INTO t VALUES ('{v}');", t, [(str(v),)])
    return s.item("SELECT typeof(a) FROM t;", type_of(t.col("a")[0]), "An INT column converts text that looks like a whole number into an integer.")


def i_text_stays(rng):
    s = Script()
    t = s.create(Table("t", [Col("a")]))
    w = words(rng, 1)[0]
    s.insert_sql(f"INSERT INTO t VALUES ('{w}');", t, [(w,)])
    return s.item("SELECT typeof(a) FROM t;", type_of(t.col("a")[0]), "Text that is not a number cannot be converted, so SQLite stores it as text anyway.")


def i_real_to_int(rng):
    s = Script()
    t = s.create(Table("t", [Col("a")]))
    v = rng.choice([2.0, 3.0, 5.0, 2.5, 4.5, 7.25])
    s.insert_sql(f"INSERT INTO t VALUES ({v!r});", t, [(v,)])
    why = "A real with no fraction (2.0) is stored as the integer 2 in an INT column; 2.5 stays real."
    return s.item("SELECT typeof(a) FROM t;", type_of(t.col("a")[0]), why)


def i_int_to_text(rng):
    s = Script()
    t = s.create(Table("t", [Col("n", "TEXT")]))
    v = rng.randint(1, 99)
    s.insert_sql(f"INSERT INTO t VALUES ({v});", t, [(v,)])
    return s.item("SELECT typeof(n) FROM t;", type_of(t.col("n")[0]), "A TEXT column turns a number into text when it stores it.")


def i_leading_zero(rng):
    s = Script()
    t = s.create(Table("t", [Col("a")]))
    v = rng.randint(1, 9)
    s.insert_sql(f"INSERT INTO t VALUES ('00{v}');", t, [("00" + str(v),)])
    return s.item("SELECT a FROM t;", t.col("a")[0], "The INT column turns the text '00k' into the number k, so the zeros are gone.")


def i_leading_zero_text(rng):
    s = Script()
    t = s.create(Table("t", [Col("a", "TEXT")]))
    v = rng.randint(1, 9)
    s.insert_sql(f"INSERT INTO t VALUES ('00{v}');", t, [("00" + str(v),)])
    return s.item("SELECT a FROM t;", t.col("a")[0], "A TEXT column keeps the text exactly as given, zeros included.")


def i_changes_multi(rng):
    s, t = base(rng, 2, mode="plain")
    n = rng.randint(2, 4)
    s.insert(t, [(rng.randint(1, 9),) for _ in range(n)])
    return s.item("SELECT changes();", s.changes, "changes() is the number of rows the last INSERT added.")


def i_changes_select(rng):
    s, u = _src(rng)
    t = s.create(Table("t", [Col("a")]))
    m = _k(rng, 3, 6)
    s.insert_sql(f"INSERT INTO t SELECT x FROM u WHERE x > {m};", t, [(r["x"],) for r in u.rows if r["x"] > m])
    return s.item("SELECT changes();", s.changes, "INSERT ... SELECT reports the rows it copied (0 when nothing matched).")


def i_last_rowid(rng):
    s, t = base(rng, rng.randint(2, 4))
    n = rng.randint(2, 3)
    s.insert(t, [(rng.randint(1, 9),) for _ in range(n)], ["a"])
    return s.item("SELECT last_insert_rowid();", s.last_rowid, "last_insert_rowid() is the id of the last row inserted: with several rows, the final one.")


def i_last_rowid_explicit(rng):
    s, t = base(rng, 3)
    k = rng.randint(10, 30)
    s.insert(t, [(k, rng.randint(1, 9))])
    return s.item("SELECT last_insert_rowid();", s.last_rowid, "For an INTEGER PRIMARY KEY the rowid is the id you gave.")


def i_ctas(rng):
    s, t = base(rng, 6, mode="plain")
    m = _k(rng, 3, 6)
    s.run(f"CREATE TABLE u AS SELECT a FROM t WHERE a > {m};")
    return s.item("SELECT COUNT(*) FROM u;", sum(1 for v in t.col("a") if v > m), "CREATE TABLE ... AS SELECT makes a new table holding the rows of the query.")


def i_ctas_snapshot(rng):
    s, t = base(rng, rng.randint(3, 5), mode="plain")
    s.run("CREATE TABLE u AS SELECT a FROM t;")
    n = len(t.rows)
    s.insert(t, [(rng.randint(1, 9),) for _ in range(2)])
    return s.item("SELECT COUNT(*) FROM u;", n, "The new table is a copy made at that moment: later inserts into t do not reach it.")


def i_copy_star(rng):
    s, t = base(rng, 5, mode="plain")
    m = _k(rng, 3, 6)
    u = s.create(Table("u", [Col("a")]))
    s.insert_sql(f"INSERT INTO u SELECT * FROM t WHERE a > {m};", u, [(v,) for v in t.col("a") if v > m])
    return s.item("SELECT SUM(a) FROM u;", sum_(u.col("a")) if u.rows else None, "Only the rows above the limit were copied into u; the answer is their sum (NULL if none).")


INSERTS: list[Maker] = [fit(f) for f in (
    i_multi_sum, i_multi_count, i_select_where, i_select_expr, i_self_double, i_default_sum, i_default_one, i_omit_null,
    i_explicit_null, i_default_values, i_default_values_id, i_text_default, i_negative_default, i_not_null_default,
    i_auto_id, i_null_id, i_explicit_id_then_auto, i_union_dedupe, i_union_all, i_limit, i_distinct, i_group, i_agg_empty,
    i_agg_empty_count_col, i_sum_row, i_max_plus, i_not_in_guard, i_join, i_recursive, i_values_expr, i_values_subq,
    i_concat_text, i_order_columns, i_positional, i_text_to_int, i_text_stays, i_real_to_int, i_int_to_text,
    i_leading_zero, i_leading_zero_text, i_changes_multi, i_changes_select, i_last_rowid, i_last_rowid_explicit, i_ctas,
    i_ctas_snapshot, i_copy_star)]
