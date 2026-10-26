"""SQL data pack, part 4: Upsert (`UPSERTS`).

INSERT OR REPLACE, INSERT OR IGNORE, ON CONFLICT DO NOTHING and ON CONFLICT(...) DO UPDATE SET ... excluded.x: which row
is left, what a REPLACE forgets, what an upsert keeps, and what `changes()` says. All statements succeed (a script that
failed would stop the driver), so every conflict is handled by one of the clauses.
"""

from __future__ import annotations

from ._model import Maker
from ._sql_model import fit, max_
from ._sqldata_model import Col, Script, Table


def ups(s: Script, t: Table, sql: str, rows: list[tuple], target: tuple, sets, where=None, cols=None, mode: str = "abort") -> int:
    """An INSERT ... ON CONFLICT: its SQL line and the model's work, row by row. `sets` is {col: fn(old, excluded)} or None
    (DO NOTHING), `where` fn(old, excluded)."""
    names = cols or t.names

    def go() -> int:
        n = 0
        for r in rows:
            n += t.insert(dict(zip(names, r)), mode, (target, sets, where))
        return n
    return s.dml(sql, go)


def _kv(rng, n: int = 2, third: str | None = None, name: str = "kv"):
    """kv(k TEXT PRIMARY KEY, v INT [, extra column]) holding n rows; the words used as keys."""
    ws = rng.sample("abcd", 4)
    s = Script()
    cols = [Col("k", "TEXT", pk=True), Col("v")]
    rows = [(ws[i], rng.randint(1, 9)) for i in range(n)]
    if third == "note":
        cols.append(Col("note", "TEXT"))
        rows = [r + (rng.choice(["x", "y", "z"]),) for r in rows]
    if third == "default":
        cols.append(Col("note", "TEXT", default="n/a"))
        rows = [r + (rng.choice(["x", "y", "z"]),) for r in rows]
    t = s.create(Table(name, cols), rows)
    return s, t, ws


def _n(rng, lo: int = 1, hi: int = 9) -> int:
    return rng.randint(lo, hi)


# ── 4. Upsert ───────────────────────────────────────────────────────────

def p_replace(rng):
    s, t, ws = _kv(rng)
    n = _n(rng)
    s.insert(t, [(ws[0], n)], mode="replace")
    return s.item(f"SELECT v FROM kv WHERE k = '{ws[0]}';", t.one("v", lambda r: r["k"] == ws[0]), "OR REPLACE deletes the old row with the same key and inserts the new one: the value is the new one.")


def p_ignore(rng):
    s, t, ws = _kv(rng)
    old = t.rows[0]["v"]
    s.insert(t, [(ws[0], _n(rng))], mode="ignore")
    return s.item(f"SELECT v FROM kv WHERE k = '{ws[0]}';", old, "OR IGNORE silently skips the new row when the key exists: the old value stays.")


def p_do_nothing(rng):
    s, t, ws = _kv(rng)
    n = _n(rng)
    s.insert_sql(f"INSERT INTO kv VALUES ('{ws[0]}',{n}) ON CONFLICT DO NOTHING;", t, [(ws[0], n)], mode="ignore")
    return s.item(f"SELECT v FROM kv WHERE k = '{ws[0]}';", t.one("v", lambda r: r["k"] == ws[0]), "ON CONFLICT DO NOTHING skips the row that collides, so the old value is kept.")


def p_do_update(rng):
    s, t, ws = _kv(rng)
    n = _n(rng)
    ups(s, t, f"INSERT INTO kv VALUES ('{ws[0]}',{n}) ON CONFLICT(k) DO UPDATE SET v = excluded.v;", [(ws[0], n)], ("k",),
        {"v": lambda o, e: e["v"]})
    return s.item(f"SELECT v FROM kv WHERE k = '{ws[0]}';", t.one("v", lambda r: r["k"] == ws[0]), "excluded.v is the value the INSERT tried to add; DO UPDATE writes it into the existing row.")


def p_add(rng):
    s, t, ws = _kv(rng)
    n = _n(rng)
    ups(s, t, f"INSERT INTO kv VALUES ('{ws[0]}',{n}) ON CONFLICT(k) DO UPDATE SET v = v + excluded.v;", [(ws[0], n)], ("k",),
        {"v": lambda o, e: o["v"] + e["v"]})
    return s.item(f"SELECT v FROM kv WHERE k = '{ws[0]}';", t.one("v", lambda r: r["k"] == ws[0]), "v is the stored value and excluded.v the new one: the upsert adds them.")


def p_new_key(rng):
    s, t, ws = _kv(rng)
    n = _n(rng)
    ups(s, t, f"INSERT INTO kv VALUES ('{ws[2]}',{n}) ON CONFLICT(k) DO UPDATE SET v = v + excluded.v;", [(ws[2], n)], ("k",),
        {"v": lambda o, e: o["v"] + e["v"]})
    return s.item("SELECT SUM(v) FROM kv;", sum(t.col("v")), "No row has the key, so there is no conflict: the row is simply inserted.")


def _tally(rng):
    s = Script()
    t = s.create(Table("c", [Col("k", "TEXT", pk=True), Col("n")]))
    ks = [rng.choice("abc") for _ in range(5)]
    rows = [(k, 1) for k in ks]
    sql = "INSERT INTO c VALUES " + ",".join(f"('{k}',1)" for k in ks) + " ON CONFLICT(k) DO UPDATE SET n = n + 1;"
    ups(s, t, sql, rows, ("k",), {"n": lambda o, e: o["n"] + 1})
    return s, t, ks


def p_tally(rng):
    s, t, ks = _tally(rng)
    k = rng.choice(ks)
    return s.item(f"SELECT n FROM c WHERE k = '{k}';", t.one("n", lambda r: r["k"] == k), "Each repeat of a key hits the conflict and adds 1, so n counts how many times the key appeared.")


def p_tally_keys(rng):
    s, t, ks = _tally(rng)
    return s.item("SELECT COUNT(*) FROM c;", len(t.rows), "One row per different key is left, however often it appeared.")


def p_tally_max(rng):
    s, t, ks = _tally(rng)
    return s.item("SELECT MAX(n) FROM c;", max_(t.col("n")), "The most frequent key has the biggest counter.")


def p_max(rng):
    s, t, ws = _kv(rng)
    n = _n(rng)
    ups(s, t, f"INSERT INTO kv VALUES ('{ws[0]}',{n}) ON CONFLICT(k) DO UPDATE SET v = MAX(v, excluded.v);", [(ws[0], n)], ("k",),
        {"v": lambda o, e: max(o["v"], e["v"])})
    return s.item(f"SELECT v FROM kv WHERE k = '{ws[0]}';", t.one("v", lambda r: r["k"] == ws[0]), "MAX(v, excluded.v) keeps the bigger of the old and new value.")


def p_min(rng):
    s, t, ws = _kv(rng)
    n = _n(rng)
    ups(s, t, f"INSERT INTO kv VALUES ('{ws[0]}',{n}) ON CONFLICT(k) DO UPDATE SET v = MIN(v, excluded.v);", [(ws[0], n)], ("k",),
        {"v": lambda o, e: min(o["v"], e["v"])})
    return s.item(f"SELECT v FROM kv WHERE k = '{ws[0]}';", t.one("v", lambda r: r["k"] == ws[0]), "MIN(v, excluded.v) keeps the smaller of the old and new value.")


def p_where_greater(rng):
    s, t, ws = _kv(rng)
    n = _n(rng)
    ups(s, t, f"INSERT INTO kv VALUES ('{ws[0]}',{n}) ON CONFLICT(k) DO UPDATE SET v = excluded.v WHERE excluded.v > v;",
        [(ws[0], n)], ("k",), {"v": lambda o, e: e["v"]}, lambda o, e: e["v"] > o["v"])
    return s.item(f"SELECT v FROM kv WHERE k = '{ws[0]}';", t.one("v", lambda r: r["k"] == ws[0]), "The WHERE on DO UPDATE decides whether the update happens: only a bigger new value replaces the old one.")


def p_where_null(rng):
    s = Script()
    t = s.create(Table("kv", [Col("k", "TEXT", pk=True), Col("v")]), [("a", None), ("b", _n(rng))])
    n, key = _n(rng), rng.choice("ab")
    ups(s, t, f"INSERT INTO kv VALUES ('{key}',{n}) ON CONFLICT(k) DO UPDATE SET v = excluded.v WHERE v IS NULL;",
        [(key, n)], ("k",), {"v": lambda o, e: e["v"]}, lambda o, e: o["v"] is None)
    return s.item(f"SELECT v FROM kv WHERE k = '{key}';", t.one("v", lambda r: r["k"] == key), "The new value is only written where the old one is NULL; a filled value is kept.")


def p_replace_multi(rng):
    s, t, ws = _kv(rng, 0)
    a, b = _n(rng), _n(rng)
    s.insert(t, [(ws[0], a), (ws[0], b)], mode="replace")
    return s.item(f"SELECT v FROM kv WHERE k = '{ws[0]}';", t.one("v", lambda r: r["k"] == ws[0]), "Rows are inserted one after the other: the second REPLACEs the first, so the last value wins.")


def p_ignore_multi(rng):
    s, t, ws = _kv(rng, 0)
    a, b = _n(rng), _n(rng)
    s.insert(t, [(ws[0], a), (ws[0], b)], mode="ignore")
    return s.item(f"SELECT v FROM kv WHERE k = '{ws[0]}';", t.one("v", lambda r: r["k"] == ws[0]), "The second row collides with the first and is ignored, so the first value wins.")


def p_replace_forgets(rng):
    s, t, ws = _kv(rng, 2, "note")
    n = _n(rng)
    s.insert(t, [(ws[0], n)], ["k", "v"], "replace")
    return s.item(f"SELECT COALESCE(note, 'none') FROM kv WHERE k = '{ws[0]}';", (t.one("note", lambda r: r["k"] == ws[0]) or "none"), "REPLACE deletes the whole old row, so the column the INSERT did not mention starts again as NULL.")


def p_replace_default(rng):
    s, t, ws = _kv(rng, 2, "default")
    s.insert(t, [(ws[0], _n(rng))], ["k", "v"], "replace")
    return s.item(f"SELECT note FROM kv WHERE k = '{ws[0]}';", t.one("note", lambda r: r["k"] == ws[0]), "REPLACE builds a brand new row, so the column left out gets its DEFAULT again.")


def p_update_keeps(rng):
    s, t, ws = _kv(rng, 1, "note")
    n = _n(rng)
    ups(s, t, f"INSERT INTO kv(k,v) VALUES ('{ws[0]}',{n}) ON CONFLICT(k) DO UPDATE SET v = excluded.v;", [(ws[0], n)], ("k",),
        {"v": lambda o, e: e["v"]}, cols=["k", "v"])
    return s.item(f"SELECT note FROM kv WHERE k = '{ws[0]}';", t.one("note", lambda r: r["k"] == ws[0]), "DO UPDATE only changes the columns in its SET: the note is kept (unlike REPLACE).")


def p_update_two(rng):
    s, t, ws = _kv(rng, 1, "note")
    n = _n(rng)
    ups(s, t, f"INSERT INTO kv(k,v) VALUES ('{ws[0]}',{n}) ON CONFLICT(k) DO UPDATE SET v = excluded.v, note = 'seen';", [(ws[0], n)], ("k",),
        {"v": lambda o, e: e["v"], "note": lambda o, e: "seen"}, cols=["k", "v"])
    return s.item(f"SELECT note FROM kv WHERE k = '{ws[0]}';", t.one("note", lambda r: r["k"] == ws[0]), "The SET list can write several columns, including a fixed text.")


def p_count_replace(rng):
    s, t, ws = _kv(rng, rng.randint(1, 2))
    s.insert(t, [(ws[0], _n(rng)), (ws[3], _n(rng))], mode="replace")
    return s.item("SELECT COUNT(*) FROM kv;", len(t.rows), "One key was replaced (still one row) and one key was new (one more row).")


def _em(rng, n: int | None = None):
    """u(id INTEGER PRIMARY KEY, email TEXT UNIQUE) with rows (1,'a'), (2,'b')..."""
    s = Script()
    n = n or rng.randint(3, 4)
    t = s.create(Table("u", [Col("id", "INTEGER", pk=True), Col("e", "TEXT", unique=True)]), [(i + 1, "abcdef"[i]) for i in range(n)])
    return s, t


def p_replace_email(rng):
    s, t = _em(rng)
    e = rng.choice("abc")
    s.insert(t, [(9, e)], mode="replace")
    return s.item("SELECT COUNT(*) FROM u;", len(t.rows), f"The new row collides with the old row that has email '{e}', so OR REPLACE deletes that row: one out, one in.")


def p_replace_email_id(rng):
    s, t = _em(rng)
    e, k = rng.choice("abc"), rng.randint(6, 9)
    s.insert(t, [(k, e)], mode="replace")
    return s.item(f"SELECT id FROM u WHERE e = '{e}';", t.one("id", lambda r: r["e"] == e), "The old row with that email is deleted and the new row holds the email now, with its own id.")


def p_replace_two(rng):
    s, t = _em(rng, rng.randint(3, 5))
    i, j = rng.sample(range(1, len(t.rows) + 1), 2)
    s.insert(t, [(i, "abcdef"[j - 1])], mode="replace")
    return s.item("SELECT COUNT(*) FROM u;", len(t.rows), "The new row collides with TWO old rows (one by id, one by email); both are deleted before it goes in.")


def p_replace_auto_id(rng):
    s, t = _em(rng)
    e = rng.choice("abc")
    s.dml(f"INSERT OR REPLACE INTO u(e) VALUES ('{e}');", lambda: t.insert({"e": e}, "replace"))
    return s.item(f"SELECT id FROM u WHERE e = '{e}';", t.one("id", lambda r: r["e"] == e), "The new row gets a fresh id (highest + 1), and the old row with that email is deleted.")


def p_update_or_replace(rng):
    s, t = _em(rng)
    k = len(t.rows)
    e = rng.choice("abc")
    s.dml(f"UPDATE OR REPLACE u SET e = '{e}' WHERE id = {k};", lambda: t.update({"e": lambda r: e}, lambda r: r["id"] == k, "replace"))
    return s.item("SELECT COUNT(*) FROM u;", len(t.rows), "UPDATE OR REPLACE deletes the other row that already holds that email (unless it is the row itself).")


def p_composite(rng):
    s = Script()
    t = s.create(Table("t", [Col("a"), Col("b"), Col("n")], unique=[("a", "b")]), [(1, 1, 1), (1, 2, 1)])
    a, b = rng.choice([(1, 1), (1, 2), (2, 1)])
    ups(s, t, f"INSERT INTO t VALUES ({a},{b},1) ON CONFLICT(a,b) DO UPDATE SET n = n + 1;", [(a, b, 1)], ("a", "b"),
        {"n": lambda o, e: o["n"] + 1})
    return s.item(f"SELECT n FROM t WHERE a = {a} AND b = {b};", t.one("n", lambda r: r["a"] == a and r["b"] == b), "The pair (a, b) is the key: a pair that exists gets n + 1, a new pair is inserted with n = 1.")


def p_composite_rows(rng):
    s = Script()
    t = s.create(Table("t", [Col("a"), Col("b"), Col("n")], unique=[("a", "b")]), [(1, 1, 1), (1, 2, 1)])
    a, b = rng.choice([(1, 1), (1, 2), (2, 1), (2, 2)])
    ups(s, t, f"INSERT INTO t VALUES ({a},{b},1) ON CONFLICT(a,b) DO UPDATE SET n = n + 1;", [(a, b, 1)], ("a", "b"),
        {"n": lambda o, e: o["n"] + 1})
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Only an unseen pair makes a new row; a pair that exists is updated in place.")


def p_changes_update(rng):
    s, t, ws = _kv(rng)
    ups(s, t, f"INSERT INTO kv VALUES ('{ws[0]}',5) ON CONFLICT(k) DO UPDATE SET v = excluded.v;", [(ws[0], 5)], ("k",), {"v": lambda o, e: e["v"]})
    return s.item("SELECT changes();", s.changes, "An upsert that updates a row counts as 1 change.")


def p_changes_nothing(rng):
    s, t, ws = _kv(rng)
    s.insert_sql(f"INSERT INTO kv VALUES ('{ws[0]}',5) ON CONFLICT DO NOTHING;", t, [(ws[0], 5)], mode="ignore")
    return s.item("SELECT changes();", s.changes, "DO NOTHING changed no row, so changes() is 0.")


def p_changes_replace(rng):
    s, t, ws = _kv(rng)
    s.insert(t, [(ws[0], 5)], mode="replace")
    return s.item("SELECT changes();", s.changes, "A REPLACE counts the new row only (1); the deleted old row is not counted.")


def p_changes_where_false(rng):
    s, t, ws = _kv(rng)
    low = t.rows[0]["v"] - 1
    ups(s, t, f"INSERT INTO kv VALUES ('{ws[0]}',{low}) ON CONFLICT(k) DO UPDATE SET v = excluded.v WHERE excluded.v > v;",
        [(ws[0], low)], ("k",), {"v": lambda o, e: e["v"]}, lambda o, e: e["v"] > o["v"])
    return s.item("SELECT changes();", s.changes, "The new value is smaller, so the DO UPDATE WHERE is false and nothing changes.")


def p_changes_ignore_multi(rng):
    s, t, ws = _kv(rng, 2)
    rows = [(ws[0], 1), (ws[2], 2), (ws[3], 3)]
    s.insert(t, rows, mode="ignore")
    return s.item("SELECT changes();", s.changes, "OR IGNORE skips the row whose key exists; the other two are inserted.")


def p_excluded_expr(rng):
    s, t, ws = _kv(rng)
    n = _n(rng)
    ups(s, t, f"INSERT INTO kv VALUES ('{ws[0]}',{n}) ON CONFLICT(k) DO UPDATE SET v = excluded.v * 2;", [(ws[0], n)], ("k",),
        {"v": lambda o, e: e["v"] * 2})
    return s.item(f"SELECT v FROM kv WHERE k = '{ws[0]}';", t.one("v", lambda r: r["k"] == ws[0]), "The SET value is an expression on excluded.v: the new value doubled.")


def p_diff(rng):
    s, t, ws = _kv(rng)
    n = _n(rng)
    ups(s, t, f"INSERT INTO kv VALUES ('{ws[0]}',{n}) ON CONFLICT(k) DO UPDATE SET v = excluded.v - v;", [(ws[0], n)], ("k",),
        {"v": lambda o, e: e["v"] - o["v"]})
    return s.item(f"SELECT v FROM kv WHERE k = '{ws[0]}';", t.one("v", lambda r: r["k"] == ws[0]), "new - old: excluded.v is the incoming value, v the stored one.")


def p_text_concat(rng):
    s = Script()
    t = s.create(Table("kv", [Col("k", "TEXT", pk=True), Col("s", "TEXT")]), [("a", "x")])
    w = rng.choice(["y", "z", "q"])
    ups(s, t, f"INSERT INTO kv VALUES ('a','{w}') ON CONFLICT(k) DO UPDATE SET s = s || ',' || excluded.s;", [("a", w)], ("k",),
        {"s": lambda o, e: o["s"] + "," + e["s"]})
    return s.item("SELECT s FROM kv;", t.col("s")[0], "The upsert glues the new text onto the old one with a comma.")


def p_null_add(rng):
    s = Script()
    t = s.create(Table("kv", [Col("k", "TEXT", pk=True), Col("v")]), [("a", None)])
    n = _n(rng)
    ups(s, t, f"INSERT INTO kv VALUES ('a',{n}) ON CONFLICT(k) DO UPDATE SET v = v + excluded.v;", [("a", n)], ("k",),
        {"v": lambda o, e: None if o["v"] is None else o["v"] + e["v"]})
    return s.item("SELECT v FROM kv;", t.col("v")[0], "NULL + anything is NULL: the stored NULL swallows the new value.")


def p_null_coalesce(rng):
    s = Script()
    t = s.create(Table("kv", [Col("k", "TEXT", pk=True), Col("v")]), [("a", None)])
    n = _n(rng)
    ups(s, t, f"INSERT INTO kv VALUES ('a',{n}) ON CONFLICT(k) DO UPDATE SET v = COALESCE(v,0) + excluded.v;", [("a", n)], ("k",),
        {"v": lambda o, e: (o["v"] or 0) + e["v"]})
    return s.item("SELECT v FROM kv;", t.col("v")[0], "COALESCE turns the stored NULL into 0 first, so the new value gets added to 0.")


def p_null_unique(rng):
    s = Script()
    t = s.create(Table("t", [Col("a", "INT", unique=True)]))
    vs = [rng.choice([None, 1, 2]) for _ in range(6)]
    s.insert(t, [(v,) for v in vs], mode="replace")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "NULLs never collide in a UNIQUE column, so every NULL row stays; a repeated number replaces its earlier copy.")


def p_do_nothing_many(rng):
    s = Script()
    t = s.create(Table("t", [Col("a", "INT", unique=True)]))
    vs = [rng.randint(1, 4) for _ in range(6)]
    s.insert_sql("INSERT INTO t VALUES " + ",".join(f"({v})" for v in vs) + " ON CONFLICT DO NOTHING;", t, [(v,) for v in vs], mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Every repeated value is skipped, so the table holds each different value once.")


def p_replace_select(rng):
    s, t, ws = _kv(rng, 2)
    u = s.create(Table("w", [Col("k", "TEXT"), Col("v")]), [(ws[0], _n(rng)), (ws[3], _n(rng))])
    s.insert_sql("INSERT OR REPLACE INTO kv SELECT k, v FROM w;", t, [(r["k"], r["v"]) for r in u.rows], mode="replace")
    return s.item("SELECT SUM(v) FROM kv;", sum(t.col("v")), "Rows copied from w replace the kv rows with the same key and add the new keys.")


def p_twice(rng):
    s, t, ws = _kv(rng, 1)
    ups(s, t, f"INSERT INTO kv VALUES ('{ws[0]}',1),('{ws[0]}',1) ON CONFLICT(k) DO UPDATE SET v = v + 1;", [(ws[0], 1), (ws[0], 1)], ("k",),
        {"v": lambda o, e: o["v"] + 1})
    return s.item("SELECT v FROM kv;", t.col("v")[0], "The row is in the table already and the INSERT lists the same key twice; each copy hits the conflict and adds 1.")


def p_ts(rng):
    s = Script()
    t = s.create(Table("kv", [Col("k", "TEXT", pk=True), Col("v", "TEXT"), Col("t")]), [("a", "o", 5)])
    ts = rng.randint(2, 9)
    ups(s, t, f"INSERT INTO kv VALUES ('a','n',{ts}) ON CONFLICT(k) DO UPDATE SET v = excluded.v, t = excluded.t WHERE excluded.t > t;",
        [("a", "n", ts)], ("k",), {"v": lambda o, e: e["v"], "t": lambda o, e: e["t"]}, lambda o, e: e["t"] > o["t"])
    return s.item("SELECT v FROM kv;", t.col("v")[0], "The new value 'n' replaces 'o' only when its timestamp is later than the stored 5.")


UPSERTS: list[Maker] = [fit(f) for f in (
    p_replace, p_ignore, p_do_nothing, p_do_update, p_add, p_new_key, p_tally, p_tally_keys, p_tally_max, p_max, p_min,
    p_where_greater, p_where_null, p_replace_multi, p_ignore_multi, p_replace_forgets, p_replace_default, p_update_keeps,
    p_update_two, p_count_replace, p_replace_email, p_replace_email_id, p_replace_two, p_replace_auto_id,
    p_update_or_replace, p_composite, p_composite_rows, p_changes_update, p_changes_nothing, p_changes_replace,
    p_changes_where_false, p_changes_ignore_multi, p_excluded_expr, p_diff, p_text_concat, p_null_add, p_null_coalesce,
    p_null_unique, p_do_nothing_many, p_replace_select, p_twice, p_ts)]
