"""SQL data pack, part 5: Constraint Quiet (`CONSTRAINTS`) and Alter & Default (`ALTERS`).

Constraint Quiet: UNIQUE, PRIMARY KEY, NOT NULL and CHECK with `OR IGNORE`, so a row that breaks a rule is skipped and
the script goes on; the question is how many rows (or which value) survived. Alter & Default: ALTER TABLE ADD COLUMN with a
DEFAULT, RENAME, DROP COLUMN, CREATE TABLE IF NOT EXISTS, and what `pragma_table_info` says about the columns.
"""

from __future__ import annotations

from ._model import Maker
from ._sql_model import Retry, count_col, fit, max_, type_of, words
from ._sqldata_model import Col, Script, Table, base


def _ints(rng, n: int, lo: int = 1, hi: int = 4) -> list[int]:
    return [rng.randint(lo, hi) for _ in range(n)]


def _quiet(rng, cols, rows, *, unique=(), checks=(), cols_in=None) -> tuple[Script, Table]:
    """A table, then ONE `INSERT OR IGNORE` of the rows."""
    s = Script()
    t = s.create(Table("t", cols, unique=unique, checks=checks))
    s.insert(t, rows, cols_in, "ignore")
    return s, t


# ── 5. Constraint Quiet ─────────────────────────────────────────────────

def c_unique_count(rng):
    s, t = _quiet(rng, [Col("a", "INT", unique=True)], [(v,) for v in _ints(rng, 6)])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "UNIQUE allows each value once; OR IGNORE skips the repeats, so the table holds the different values.")


def c_unique_first(rng):
    s = Script()
    t = s.create(Table("t", [Col("a", "INT", unique=True), Col("b", "TEXT")]))
    x, y = rng.sample("pqrst", 2)
    s.insert(t, [(1, x), (1, y), (2, "z")], mode="ignore")
    return s.item("SELECT b FROM t WHERE a = 1;", t.one("b", lambda r: r["a"] == 1), "The first row with a = 1 is kept; the later one breaks UNIQUE and is skipped.")


def c_unique_sum(rng):
    s, t = _quiet(rng, [Col("a", "INT", unique=True)], [(v,) for v in _ints(rng, 6, 1, 5)])
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "Each different value is added once, because the repeats were skipped.")


def c_pk_text(rng):
    s = Script()
    t = s.create(Table("t", [Col("k", "TEXT", pk=True), Col("v")]))
    ks = [rng.choice("abc") for _ in range(5)]
    s.insert(t, [(k, i + 1) for i, k in enumerate(ks)], mode="ignore")
    return s.item("SELECT SUM(v) FROM t;", sum(t.col("v")), "Only the first row of each key is kept (a PRIMARY KEY is unique); v is the row number, so those are added.")


def c_pk_int(rng):
    s = Script()
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True), Col("v", "TEXT")]))
    ids = _ints(rng, 5, 1, 4)
    s.insert(t, [(i, "x") for i in ids], mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Explicit ids that are already taken are skipped by OR IGNORE.")


def c_notnull(rng):
    vals = [rng.randint(1, 9) if rng.random() < 0.6 else None for _ in range(6)]
    s, t = _quiet(rng, [Col("a", "INT", not_null=True)], [(v,) for v in vals])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A NULL breaks NOT NULL, so those rows are skipped.")


def c_notnull_sum(rng):
    vals = [rng.randint(1, 9) if rng.random() < 0.6 else None for _ in range(6)]
    s, t = _quiet(rng, [Col("a", "INT", not_null=True)], [(v,) for v in vals])
    if not t.rows:
        raise Retry
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "Only the rows with a number were stored; the sum adds those.")


def c_check_pos(rng):
    vals = [rng.randint(-3, 5) for _ in range(6)]
    s, t = _quiet(rng, [Col("a", "INT", check=("a > 0", lambda r: None if r["a"] is None else r["a"] > 0))], [(v,) for v in vals])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "CHECK (a > 0) rejects 0 and negative numbers; OR IGNORE skips them.")


def c_check_null(rng):
    vals = [rng.randint(-3, 5) for _ in range(4)] + [None, None]
    rng.shuffle(vals)
    s, t = _quiet(rng, [Col("a", "INT", check=("a > 0", lambda r: None if r["a"] is None else r["a"] > 0))], [(v,) for v in vals])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A CHECK only fails when it is FALSE. For NULL it is unknown, so NULL rows pass.")


def c_check_range(rng):
    vals = [rng.randint(0, 9) for _ in range(6)]
    s, t = _quiet(rng, [Col("a", "INT", check=("a BETWEEN 2 AND 6", lambda r: 2 <= r["a"] <= 6))], [(v,) for v in vals])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "BETWEEN 2 AND 6 includes both ends; the rest are skipped.")


def c_check_two(rng):
    rows = [tuple(rng.sample(range(1, 7), 2)) for _ in range(5)]
    s = Script()
    t = s.create(Table("t", [Col("a"), Col("b")], checks=[("a < b", lambda r: r["a"] < r["b"])]))
    s.insert(t, rows, mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A table CHECK can compare two columns: only the rows with a below b are stored.")


def c_check_in(rng):
    vals = [rng.choice("xyz") for _ in range(6)]
    s, t = _quiet(rng, [Col("s", "TEXT", check=("s IN ('x','y')", lambda r: r["s"] in ("x", "y")))], [(v,) for v in vals])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Only 'x' and 'y' are allowed; every 'z' row is skipped.")


def c_check_len(rng):
    ws = words(rng, 5)
    s, t = _quiet(rng, [Col("n", "TEXT", check=("LENGTH(n) <= 3", lambda r: len(r["n"]) <= 3))], [(w,) for w in ws])
    if not t.rows:
        raise Retry
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Only names of at most 3 letters pass the CHECK.")


def c_check_even(rng):
    vals = _ints(rng, 6, 1, 9)
    s, t = _quiet(rng, [Col("a", "INT", check=("a % 2 = 0", lambda r: r["a"] % 2 == 0))], [(v,) for v in vals])
    if not t.rows:
        raise Retry
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "a % 2 = 0 keeps only the even numbers; the odd rows are skipped.")


def c_check_bool(rng):
    vals = [rng.randint(0, 2) for _ in range(6)]
    s, t = _quiet(rng, [Col("done", "INT", check=("done IN (0,1)", lambda r: None if r["done"] is None else r["done"] in (0, 1)))], [(v,) for v in vals])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A flag column that must be 0 or 1 turns the 2s away.")


def c_check_max(rng):
    vals = [rng.randint(1, 15) for _ in range(6)]
    s, t = _quiet(rng, [Col("a", "INT", check=("a < 10", lambda r: r["a"] < 10))], [(v,) for v in vals])
    if not t.rows:
        raise Retry
    return s.item("SELECT MAX(a) FROM t;", max_(t.col("a")), "Values of 10 or more are skipped, so the biggest stored value is below 10.")


def c_combo(rng):
    vals = [rng.choice([None, -1, 1, 2, 3]) for _ in range(7)]
    s, t = _quiet(rng, [Col("a", "INT", not_null=True, unique=True, check=("a > 0", lambda r: None if r["a"] is None else r["a"] > 0))], [(v,) for v in vals])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A row must be not NULL, positive AND new; any single failure skips it.")


def c_unique_nulls(rng):
    vals = [None, None, rng.randint(1, 3), None, rng.randint(1, 3)]
    s, t = _quiet(rng, [Col("a", "INT", unique=True)], [(v,) for v in vals])
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "UNIQUE treats every NULL as different, so any number of NULL rows is fine; only the repeated numbers are skipped.")


def c_pk_text_null(rng):
    s = Script()
    t = s.create(Table("t", [Col("k", "TEXT", pk=True), Col("v")]))
    ks = [None, None] + [rng.choice("ab") for _ in range(rng.randint(2, 4))]
    rng.shuffle(ks)
    s.insert(t, [(k, i + 1) for i, k in enumerate(ks)], mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A TEXT PRIMARY KEY may hold NULL in SQLite (an old quirk), and NULLs never collide; a repeated text key does.")


def c_composite(rng):
    rows = [(rng.randint(1, 2), rng.randint(1, 2)) for _ in range(6)]
    s = Script()
    t = s.create(Table("t", [Col("a"), Col("b")], unique=[("a", "b")]))
    s.insert(t, rows, mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "UNIQUE(a, b) is about the PAIR: a pair may appear once, though a or b alone may repeat.")


def c_nocase(rng):
    s = Script()
    t = s.create(Table("t", [Col("n", "TEXT", unique=True, nocase=True)]))
    w = rng.choice(["ab", "kit", "net", "zip"])
    s.insert(t, [(w,), (w.upper(),), ("q",)], mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "COLLATE NOCASE makes 'ab' and 'AB' the same value, so the second collides.")


def c_case_sensitive(rng):
    s = Script()
    t = s.create(Table("t", [Col("n", "TEXT", unique=True)]))
    w = rng.choice(["ab", "kit", "net", "zip"])
    s.insert(t, [(w,), (w.upper(),), ("q",)], mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "By default text is compared exactly, so 'ab' and 'AB' are two different values.")


def c_int_text(rng):
    s = Script()
    t = s.create(Table("t", [Col("a", "INT", unique=True)]))
    v = rng.randint(1, 9)
    s.insert(t, [(v,), (str(v),), (v + 1,)], mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The text '5' is turned into the number 5 by the INT column, so it collides with the 5 already there.")


def c_int_real(rng):
    s = Script()
    t = s.create(Table("t", [Col("a", "INT", unique=True)]))
    v = rng.randint(1, 9)
    s.insert(t, [(v,), (float(v),), (v + 1,)], mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "2.0 is stored as the integer 2 in an INT column, so it collides with the 2 already there.")


def c_auto_ids(rng):
    s = Script()
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True), Col("v", "TEXT")]))
    n = rng.randint(3, 5)
    s.insert(t, [(w,) for w in words(rng, n)], ["v"], "ignore")
    return s.item("SELECT MAX(id) FROM t;", max_(t.col("id")), "Left out, the id is assigned 1, 2, 3 ... one per stored row.")


def c_explicit_then_auto(rng):
    s = Script()
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True), Col("v", "TEXT")]))
    k = rng.randint(5, 20)
    s.insert(t, [(k, "a")], mode="ignore")
    s.insert(t, [("b",)], ["v"], "ignore")
    return s.item("SELECT MAX(id) FROM t;", max_(t.col("id")), "The automatic id is the biggest id so far plus one.")


def c_skipped_no_id(rng):
    s = Script()
    n = rng.randint(2, 4)
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True), Col("v", "TEXT")]), [(i + 1, "abcd"[i]) for i in range(n)])
    s.insert(t, [(rng.randint(1, n), "x")], mode="ignore")
    s.insert(t, [("y",)], ["v"], "ignore")
    return s.item("SELECT MAX(id) FROM t;", max_(t.col("id")), "The skipped row used no id: the next new row is one past the highest id.")


def c_changes(rng):
    s, t = _quiet(rng, [Col("a", "INT", unique=True)], [(v,) for v in _ints(rng, 6)])
    return s.item("SELECT changes();", s.changes, "changes() counts the rows that were really inserted; the skipped ones do not count.")


def c_rejected(rng):
    s, t = _quiet(rng, [Col("a", "INT", unique=True)], [(v,) for v in _ints(rng, 6)])
    return s.item("SELECT 6 - COUNT(*) FROM t;", 6 - len(t.rows), "Six rows were tried; the count says how many stayed, so the rest were skipped.")


def c_last_rowid(rng):
    s = Script()
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True), Col("v", "TEXT", unique=True)]))
    n = rng.randint(2, 4)
    s.insert(t, [(w,) for w in "abcd"[:n]], ["v"], "abort")
    s.insert(t, [(rng.choice("abcd"[:n]),)], ["v"], "ignore")
    return s.item("SELECT last_insert_rowid();", s.last_rowid, "The last INSERT was skipped, so last_insert_rowid() still says the id of the row before it.")


def c_update_ignore(rng):
    s = Script()
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True), Col("a", "INT", unique=True)]), [(1, 5), (2, 6), (3, 7)])
    k = rng.randint(1, 3)
    x = rng.choice([5, 6, 7, 8, 9])
    s.dml(f"UPDATE OR IGNORE t SET a = {x} WHERE id = {k};", lambda: t.update({"a": lambda r: x}, lambda r: r["id"] == k, "ignore"))
    return s.item(f"SELECT a FROM t WHERE id = {k};", t.one("a", lambda r: r["id"] == k), "If the new value is already taken by another row, UPDATE OR IGNORE leaves this row unchanged.")


def c_update_ignore_check(rng):
    s = Script()
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True), Col("a", "INT", check=("a > 0", lambda r: None if r["a"] is None else r["a"] > 0))]), [(1, 3), (2, 5)])
    d = rng.randint(1, 6)
    s.dml(f"UPDATE OR IGNORE t SET a = a - {d} WHERE id = 1;", lambda: t.update({"a": lambda r: r["a"] - d}, lambda r: r["id"] == 1, "ignore"))
    return s.item("SELECT a FROM t WHERE id = 1;", t.one("a", lambda r: r["id"] == 1), "If the new a is 0 or less the CHECK fails and the row keeps its old value 3.")


def c_update_ignore_notnull(rng):
    s = Script()
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True), Col("a", "INT", not_null=True)]), [(1, 3), (2, 5), (3, 8)])
    k = rng.randint(1, 3)
    s.dml(f"UPDATE OR IGNORE t SET a = NULL WHERE id = {k};", lambda: t.update({"a": lambda r: None}, lambda r: r["id"] == k, "ignore"))
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "Setting a NOT NULL column to NULL fails, and OR IGNORE keeps the old value: nothing changes.")


def c_partial_unique(rng):
    s = Script()
    t = s.create(Table("t", [Col("e", "TEXT"), Col("act", "INT")],
                       partial=[(("e",), "act = 1", lambda r: None if r["act"] is None else r["act"] == 1)]))
    rows = [(rng.choice("ab"), rng.randint(0, 1)) for _ in range(rng.randint(4, 6))]
    s.insert(t, rows, mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The unique index only covers rows with act = 1: two such rows with the same e collide, rows with act = 0 never do.")


def c_unique_index(rng):
    s = Script()
    t = s.create(Table("t", [Col("a")]))
    s.run("CREATE UNIQUE INDEX ix ON t(a);", lambda: t.unique.append(("a",)))
    s.insert(t, [(v,) for v in _ints(rng, 6)], mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A UNIQUE INDEX enforces the same rule as UNIQUE: each value once.")


def c_default_notnull(rng):
    s = Script()
    d = rng.randint(1, 9)
    t = s.create(Table("t", [Col("a"), Col("b", "INT", not_null=True, default=d)]))
    s.insert(t, [(1, None), (2, rng.randint(1, 9))], mode="ignore")
    s.insert(t, [(3,)] * rng.randint(1, 2), ["a"], "ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "An explicit NULL breaks NOT NULL (the DEFAULT is only for a column left out), so row 1 is skipped; the other rows pass.")


def c_empty_text(rng):
    s = Script()
    t = s.create(Table("t", [Col("n", "TEXT", not_null=True)]))
    vs = [rng.choice(["a", "", None, "b"]) for _ in range(5)]
    s.insert(t, [(v,) for v in vs], mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The empty text '' is a value, not NULL, so NOT NULL lets it in; only the NULL rows are skipped.")


def c_nonempty_check(rng):
    s = Script()
    t = s.create(Table("t", [Col("n", "TEXT", check=("n <> ''", lambda r: None if r["n"] is None else r["n"] != ""))]))
    vs = [rng.choice(["a", "", None, "b"]) for _ in range(5)]
    s.insert(t, [(v,) for v in vs], mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "CHECK (n <> '') rejects the empty text but not NULL (the check is unknown there).")


def c_two_batches(rng):
    s = Script()
    t = s.create(Table("t", [Col("a", "INT", unique=True)]))
    s.insert(t, [(v,) for v in rng.sample(range(1, 7), 3)], mode="ignore")
    s.insert(t, [(v,) for v in rng.sample(range(1, 7), 3)], mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The second batch only adds the values the first one did not contain.")


def c_insert_select(rng):
    s = Script()
    u = s.create(Table("u", [Col("x")]), [(v,) for v in _ints(rng, 5)])
    t = s.create(Table("t", [Col("a", "INT", unique=True)]))
    s.insert_sql("INSERT OR IGNORE INTO t SELECT x FROM u;", t, [(r["x"],) for r in u.rows], mode="ignore")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "INSERT OR IGNORE ... SELECT skips copies of values already stored.")


CONSTRAINTS: list[Maker] = [fit(f) for f in (
    c_unique_count, c_unique_first, c_unique_sum, c_pk_text, c_pk_int, c_notnull, c_notnull_sum, c_check_pos, c_check_null,
    c_check_range, c_check_two, c_check_in, c_check_len, c_check_even, c_check_bool, c_check_max, c_combo, c_unique_nulls,
    c_pk_text_null, c_composite, c_nocase, c_case_sensitive, c_int_text, c_int_real, c_auto_ids, c_explicit_then_auto,
    c_skipped_no_id, c_changes, c_rejected, c_last_rowid, c_update_ignore, c_update_ignore_check, c_update_ignore_notnull,
    c_partial_unique, c_unique_index, c_default_notnull, c_empty_text, c_nonempty_check, c_two_batches, c_insert_select)]


# ── 6. Alter & Default ──────────────────────────────────────────────────

def _add(s: Script, t: Table, decl: str, col: Col) -> None:
    s.run(f"ALTER TABLE {t.name} ADD COLUMN {decl};", lambda: t.add_column(col))


def _d(rng) -> int:
    return rng.randint(2, 9)


def a_default_sum(rng):
    s, t = base(rng, 4)
    d = _d(rng)
    _add(s, t, f"b INT DEFAULT {d}", Col("b", "INT", default=d))
    return s.item("SELECT SUM(b) FROM t;", sum(t.col("b")), "ADD COLUMN with a DEFAULT: the old rows show that default too.")


def a_no_default(rng):
    s, t = base(rng, rng.randint(3, 5))
    _add(s, t, "b INT", Col("b"))
    return s.item("SELECT COUNT(b) FROM t;", count_col(t.col("b")), "Without a DEFAULT the new column is NULL in the old rows, and COUNT(b) skips NULLs.")


def a_is_null(rng):
    s, t = base(rng, rng.randint(3, 5))
    _add(s, t, "b INT", Col("b"))
    return s.item("SELECT COUNT(*) FROM t WHERE b IS NULL;", sum(1 for v in t.col("b") if v is None), "Every old row has NULL in the new column.")


def a_text_default(rng):
    s, t = base(rng, 3)
    k = rng.randint(1, 3)
    _add(s, t, "s TEXT DEFAULT 'new'", Col("s", "TEXT", default="new"))
    return s.item(f"SELECT s FROM t WHERE id = {k};", t.one("s", lambda r: r["id"] == k), "The DEFAULT text fills the new column of every old row.")


def a_default_len(rng):
    s, t = base(rng, 3)
    w = rng.choice(["new", "todo", "open", "x"])
    _add(s, t, f"s TEXT DEFAULT '{w}'", Col("s", "TEXT", default=w))
    return s.item("SELECT SUM(LENGTH(s)) FROM t;", sum(len(v) for v in t.col("s")), "Each of the three rows gets the DEFAULT text, and its letters are counted.")


def a_insert_omit(rng):
    s, t = base(rng, rng.randint(2, 4))
    d = _d(rng)
    _add(s, t, f"b INT DEFAULT {d}", Col("b", "INT", default=d))
    s.insert(t, [(rng.randint(1, 9),)], ["a"])
    return s.item(f"SELECT COUNT(*) FROM t WHERE b = {d};", t.col("b").count(d), "Old rows and the new row (which left b out) all have the DEFAULT.")


def a_insert_explicit_null(rng):
    s, t = base(rng, rng.randint(2, 4))
    d = _d(rng)
    _add(s, t, f"b INT DEFAULT {d}", Col("b", "INT", default=d))
    s.insert(t, [(len(t.rows) + 1, 5, None)])
    return s.item("SELECT COUNT(b) FROM t;", count_col(t.col("b")), "The explicit NULL beats the DEFAULT: the new row's b is NULL, and COUNT(b) skips it.")


def a_update_after(rng):
    s, t = base(rng, 4)
    _add(s, t, "b INT DEFAULT 0", Col("b", "INT", default=0))
    m = rng.randint(3, 6)
    s.dml(f"UPDATE t SET b = 1 WHERE a > {m};", lambda: t.update({"b": lambda r: 1}, lambda r: r["a"] > m))
    return s.item("SELECT SUM(b) FROM t;", sum(t.col("b")), "A flag column starts at 0 for every old row and is set to 1 for the big rows.")


def a_counter(rng):
    s, t = base(rng, rng.randint(2, 4))
    _add(s, t, "n INT DEFAULT 0", Col("n", "INT", default=0))
    for _ in range(2):
        s.dml("UPDATE t SET n = n + 1;", lambda: t.update({"n": lambda r: r["n"] + 1}))
    return s.item("SELECT SUM(n) FROM t;", sum(t.col("n")), "The new counter starts at 0 in every row; two UPDATEs add 1 to each row twice.")


def a_not_null_default(rng):
    s, t = base(rng, 3)
    d = _d(rng)
    _add(s, t, f"b INT NOT NULL DEFAULT {d}", Col("b", "INT", not_null=True, default=d))
    return s.item("SELECT SUM(b) FROM t;", sum(t.col("b")), "A NOT NULL column can be added when it has a non-NULL DEFAULT; the old rows get it.")


def a_two_cols(rng):
    s, t = base(rng, 3)
    d, e = _d(rng), _d(rng)
    _add(s, t, f"b INT DEFAULT {d}", Col("b", "INT", default=d))
    _add(s, t, f"c INT DEFAULT {e}", Col("c", "INT", default=e))
    return s.item("SELECT SUM(b + c) FROM t;", sum(r["b"] + r["c"] for r in t.rows), "Both new columns get their own DEFAULT in all three rows.")


def a_coalesce(rng):
    s, t = base(rng, rng.randint(3, 5))
    _add(s, t, "b INT", Col("b"))
    return s.item("SELECT SUM(COALESCE(b, 10)) FROM t;", 10 * len(t.rows), "COALESCE replaces each NULL in the new column with 10.")


def a_real_type(rng):
    s, t = base(rng, 2)
    d = rng.randint(1, 5)
    _add(s, t, f"b REAL DEFAULT {d}", Col("b", "REAL", default=d))
    return s.item("SELECT typeof(b) FROM t WHERE id = 1;", type_of(t.col("b")[0]), "A REAL column stores its whole-number DEFAULT as a real number.")


def a_text_type(rng):
    s, t = base(rng, 2)
    d = rng.randint(1, 5)
    _add(s, t, f"b TEXT DEFAULT {d}", Col("b", "TEXT", default=d))
    return s.item("SELECT typeof(b) FROM t WHERE id = 1;", type_of(t.col("b")[0]), "A TEXT column turns its numeric DEFAULT into text.")


def a_rename_col(rng):
    s, t = base(rng, 4)
    s.run("ALTER TABLE t RENAME COLUMN a TO x;", lambda: t.rename_column("a", "x"))
    return s.item("SELECT SUM(x) FROM t;", sum(t.col("x")), "RENAME COLUMN keeps all the data; only the name changes.")


def a_rename_insert(rng):
    s, t = base(rng, 3)
    s.run("ALTER TABLE t RENAME COLUMN a TO x;", lambda: t.rename_column("a", "x"))
    s.insert(t, [(rng.randint(1, 9),)], ["x"])
    return s.item("SELECT SUM(x) FROM t;", sum(t.col("x")), "After the rename the new INSERT must use the new name, and its value joins the old data.")


def a_rename_twice(rng):
    s, t = base(rng, 3)
    s.run("ALTER TABLE t RENAME COLUMN a TO x;", lambda: t.rename_column("a", "x"))
    s.run("ALTER TABLE t RENAME COLUMN x TO y;", lambda: t.rename_column("x", "y"))
    return s.item("SELECT MAX(y) FROM t;", max_(t.col("y")), "The column is a, then x, then y: always the same data.")


def a_rename_table(rng):
    s, t = base(rng, rng.randint(3, 5))
    s.run("ALTER TABLE t RENAME TO u;", lambda: setattr(t, "name", "u"))
    return s.item("SELECT COUNT(*) FROM u;", len(t.rows), "RENAME TO changes the table's name and keeps its rows.")


def a_rename_table_insert(rng):
    s, t = base(rng, rng.randint(2, 4))
    s.run("ALTER TABLE t RENAME TO u;", lambda: setattr(t, "name", "u"))
    s.insert(t, [(rng.randint(1, 9),)], ["a"])
    return s.item("SELECT COUNT(*) FROM u;", len(t.rows), "The old rows are in u now, and the INSERT into u adds one more.")


def a_rename_view(rng):
    s, t = base(rng, 5, mode="plain")
    m = rng.randint(3, 6)
    s.run(f"CREATE VIEW v AS SELECT a FROM t WHERE a > {m};")
    s.run("ALTER TABLE t RENAME COLUMN a TO x;", lambda: t.rename_column("a", "x"))
    return s.item("SELECT COUNT(*) FROM v;", sum(1 for v in t.col("x") if v > m), "SQLite rewrites the view when a column is renamed, so the view still works.")


def a_drop_sum(rng):
    s = Script()
    t = s.create(Table("t", [Col("a"), Col("b")]), [(rng.randint(1, 9), rng.randint(1, 9)) for _ in range(4)])
    s.run("ALTER TABLE t DROP COLUMN b;", lambda: t.drop_column("b"))
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "DROP COLUMN removes b and its data; a is untouched.")


def a_drop_readd(rng):
    s = Script()
    t = s.create(Table("t", [Col("a"), Col("b")]), [(rng.randint(1, 9), rng.randint(1, 9)) for _ in range(3)])
    s.run("ALTER TABLE t DROP COLUMN b;", lambda: t.drop_column("b"))
    s.run("ALTER TABLE t ADD COLUMN b INT DEFAULT 0;", lambda: t.add_column(Col("b", "INT", default=0)))
    return s.item("SELECT SUM(b) FROM t;", sum(t.col("b")), "The old b values were destroyed by DROP COLUMN; the new b starts from its DEFAULT.")


def a_count_cols(rng):
    s, t = base(rng, 2)
    for nm in ["b", "c"][:rng.randint(1, 2)]:
        _add(s, t, f"{nm} INT", Col(nm))
    return s.item("SELECT COUNT(*) FROM pragma_table_info('t');", len(t.cols), "pragma_table_info lists one row per column: the two it started with plus the added ones.")


def a_count_after_drop(rng):
    s = Script()
    n = rng.randint(3, 5)
    t = s.create(Table("t", [Col(c) for c in "abcde"[:n]]), [tuple(range(1, n + 1))])
    k = rng.choice("abcde"[:n])
    s.run(f"ALTER TABLE t DROP COLUMN {k};", lambda: t.drop_column(k))
    return s.item("SELECT COUNT(*) FROM pragma_table_info('t');", len(t.cols), "One column fewer than the table was created with.")


def a_name_at(rng):
    s, t = base(rng, 2)
    _add(s, t, "b INT", Col("b"))
    k = rng.randint(0, 2)
    return s.item(f"SELECT name FROM pragma_table_info('t') WHERE cid = {k};", t.names[k], "Columns are numbered from 0 in the order they were created; ADD COLUMN goes last.")


def a_name_renamed(rng):
    s, t = base(rng, 2)
    s.run("ALTER TABLE t RENAME COLUMN a TO x;", lambda: t.rename_column("a", "x"))
    return s.item("SELECT name FROM pragma_table_info('t') WHERE cid = 1;", t.names[1], "Column 1 is the second one (id is 0): it is x after the rename.")


def a_last_col(rng):
    s, t = base(rng, 2)
    _add(s, t, "b INT", Col("b"))
    _add(s, t, "c INT", Col("c"))
    return s.item("SELECT name FROM pragma_table_info('t') ORDER BY cid DESC LIMIT 1;", t.names[-1], "The newest column is the last one.")


def a_col_type(rng):
    s, t = base(rng, 2)
    typ = rng.choice(["TEXT", "REAL", "INT"])
    _add(s, t, f"b {typ}", Col("b", typ))
    return s.item("SELECT type FROM pragma_table_info('t') WHERE name = 'b';", typ, "pragma_table_info shows the declared type exactly as it was written.")


def a_if_not_exists(rng):
    s, t = base(rng, rng.randint(3, 5))
    s.run("CREATE TABLE IF NOT EXISTS t(id INT, a INT);")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "IF NOT EXISTS does nothing when the table is there: its rows are still in place.")


def a_if_not_exists_cols(rng):
    s, t = base(rng, 3)
    s.run("CREATE TABLE IF NOT EXISTS t(x INT, y INT, z INT);")
    return s.item("SELECT COUNT(*) FROM pragma_table_info('t');", len(t.cols), "The existing table is left alone, so the new three-column definition is ignored.")


def a_drop_create(rng):
    s, t = base(rng, 4, mode="plain")
    s.run("DROP TABLE t;")
    s.run("CREATE TABLE t(a INT);")
    return s.item("SELECT COUNT(*) FROM t;", 0, "DROP TABLE throws the data away; the new table of the same name starts empty.")


def a_drop_create_insert(rng):
    s, t = base(rng, 4, mode="plain")
    s.run("DROP TABLE t;")
    t2 = s.create(Table("t", [Col("a")]))
    s.insert(t2, [(v,) for v in rng.sample(range(10, 20), 2)])
    return s.item("SELECT SUM(a) FROM t;", sum(t2.col("a")), "Only the two rows inserted after the new CREATE are there.")


def a_drop_if_exists(rng):
    s, t = base(rng, rng.randint(3, 5))
    s.run("DROP TABLE IF EXISTS gone;")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "IF EXISTS turns the drop of a missing table into a quiet no-op.")


def a_star_view(rng):
    s, t = base(rng, 2)
    s.run("CREATE VIEW v AS SELECT * FROM t;")
    _add(s, t, "b INT", Col("b"))
    return s.item("SELECT COUNT(*) FROM pragma_table_info('v');", len(t.cols), "A view with SELECT * is expanded each time it is used, so it sees the new column too.")


def a_insert_select_default(rng):
    s, t = base(rng, 3)
    d = _d(rng)
    _add(s, t, f"b INT DEFAULT {d}", Col("b", "INT", default=d))
    s.insert_sql("INSERT INTO t(a) SELECT a FROM t;", t, [(r["a"],) for r in list(t.rows)], ["a"])
    return s.item("SELECT SUM(b) FROM t;", sum(t.col("b")), "The copied rows leave b out, so they get the DEFAULT as well: six rows with it.")


def a_rename_keeps(rng):
    s, t = base(rng, 4)
    s.run("ALTER TABLE t RENAME COLUMN a TO x;", lambda: t.rename_column("a", "x"))
    k = rng.randint(1, 4)
    return s.item(f"SELECT x FROM t WHERE id = {k};", t.one("x", lambda r: r["id"] == k), "The renamed column holds the same value in every row.")


def a_flag(rng):
    s, t = base(rng, 5)
    _add(s, t, "done INT DEFAULT 0", Col("done", "INT", default=0))
    m = rng.randint(3, 6)
    s.dml(f"UPDATE t SET done = 1 WHERE a > {m};", lambda: t.update({"done": lambda r: 1}, lambda r: r["a"] > m))
    return s.item("SELECT COUNT(*) FROM t WHERE done = 0;", t.col("done").count(0), "Every row starts with done = 0; the big ones were set to 1, the rest are counted.")


def a_empty_default(rng):
    s, t = base(rng, rng.randint(3, 5))
    _add(s, t, "s TEXT DEFAULT ''", Col("s", "TEXT", default=""))
    return s.item("SELECT COUNT(*) FROM t WHERE s = '';", t.col("s").count(""), "The DEFAULT is the empty text, which is not NULL: every old row equals ''.")


def a_rename_back(rng):
    s, t = base(rng, 4)
    s.run("ALTER TABLE t RENAME COLUMN a TO x;", lambda: t.rename_column("a", "x"))
    s.run("ALTER TABLE t RENAME COLUMN x TO a;", lambda: t.rename_column("x", "a"))
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "Renamed and renamed back: the original name works again, and nothing was lost.")


def a_negative_default(rng):
    s, t = base(rng, 3)
    d = -rng.randint(1, 9)
    _add(s, t, f"b INT DEFAULT {d}", Col("b", "INT", default=d))
    return s.item("SELECT SUM(b) FROM t;", sum(t.col("b")), "The DEFAULT may be negative; each of the three rows gets it.")


def a_drop_keeps_rows(rng):
    s = Script()
    t = s.create(Table("t", [Col("a"), Col("b")]), [(rng.randint(1, 9), rng.randint(1, 9)) for _ in range(rng.randint(3, 5))])
    s.run("ALTER TABLE t DROP COLUMN b;", lambda: t.drop_column("b"))
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Dropping a column changes the shape but removes no rows.")


def a_set_null_after(rng):
    s, t = base(rng, rng.randint(3, 5))
    d = _d(rng)
    _add(s, t, f"b INT DEFAULT {d}", Col("b", "INT", default=d))
    k = rng.randint(1, 4)
    s.dml(f"UPDATE t SET b = NULL WHERE id = {k};", lambda: t.update({"b": lambda r: None}, lambda r: r["id"] == k))
    return s.item("SELECT COUNT(b) FROM t;", count_col(t.col("b")), "The DEFAULT only fills a missing value; an UPDATE can still set b to NULL.")


ALTERS: list[Maker] = [fit(f) for f in (
    a_default_sum, a_no_default, a_is_null, a_text_default, a_default_len, a_insert_omit, a_insert_explicit_null, a_update_after,
    a_counter, a_not_null_default, a_two_cols, a_coalesce, a_real_type, a_text_type, a_rename_col, a_rename_insert, a_rename_twice,
    a_rename_table, a_rename_table_insert, a_rename_view, a_drop_sum, a_drop_readd, a_count_cols, a_count_after_drop, a_name_at,
    a_name_renamed, a_last_col, a_col_type, a_if_not_exists, a_if_not_exists_cols, a_drop_create, a_drop_create_insert,
    a_drop_if_exists, a_star_view, a_insert_select_default, a_rename_keeps, a_flag, a_empty_default, a_rename_back,
    a_negative_default, a_drop_keeps_rows, a_set_null_after)]
