"""SQL data pack, part 2: After Delete (`DELETES`).

DELETE with WHERE, subqueries, NULL traps (`NOT IN` with a NULL, `= NULL`, `<>`), duplicates removal, id reuse (rowid and
AUTOINCREMENT), `changes()`, empty aggregates and foreign keys (self-referencing, so one table keeps the prompt short).
"""

from __future__ import annotations

from ._model import Maker
from ._sql_model import (Retry, between, count_distinct, eq, fit, gt, in_list, like, lt, max_, min_, ne, not_in, t_and,
                         t_or)
from ._sqldata_model import Col, Script, Table, base, base_named
from ._sqldata_update import _k, _pair, dele


def _nonempty(t: Table) -> None:
    """Refuse (Retry) a table the DELETE emptied, when the question is about what is left."""
    if not t.rows:
        raise Retry


def d_where_count(rng):
    s, t = base(rng, 6, pk=False)
    m = _k(rng, 3, 7)
    dele(s, t, f"DELETE FROM t WHERE a > {m};", lambda r: gt(r["a"], m))
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The rows with a above the limit are gone; the rest are counted.")


def d_where_sum(rng):
    s, t = base(rng, 6, pk=False)
    m = _k(rng, 3, 6)
    dele(s, t, f"DELETE FROM t WHERE a < {m};", lambda r: lt(r["a"], m))
    _nonempty(t)
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "Only the rows that were not deleted are added up.")


def d_all(rng):
    s, t = base(rng, rng.randint(3, 6), pk=False)
    dele(s, t, "DELETE FROM t;")
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "DELETE with no WHERE removes every row; the table itself stays, empty.")


def d_all_then_insert(rng):
    s, t = base(rng, 4, mode="plain")
    dele(s, t, "DELETE FROM t;")
    s.insert(t, [(v,) for v in rng.sample(range(10, 20), 2)])
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "The old rows were all deleted first, so only the two new rows are added.")


def d_empty_agg(rng):
    s, t = base(rng, 5, pk=False)
    dele(s, t, "DELETE FROM t;")
    q = rng.choice([("SUM(a)", None, "SUM of no rows is NULL, not 0."), ("MAX(a)", None, "MAX of no rows is NULL."),
                    ("COUNT(a)", 0, "COUNT of no rows is 0 (the one aggregate that is not NULL)."),
                    ("COALESCE(SUM(a), 0)", 0, "SUM of no rows is NULL, and COALESCE replaces it with 0."),
                    ("TOTAL(a)", 0.0, "TOTAL is SUM that gives 0.0 instead of NULL for no rows.")])
    return s.item(f"SELECT {q[0]} FROM t;", q[1], q[2])


def d_max_row(rng):
    s, t = base(rng, 5, pk=False)
    top = max(t.col("a"))
    dele(s, t, "DELETE FROM t WHERE a = (SELECT MAX(a) FROM t);", lambda r: eq(r["a"], top))
    _nonempty(t)
    return s.item("SELECT MAX(a) FROM t;", max_(t.col("a")), "Every row holding the biggest value goes (ties too), so MAX is now the next one down.")


def d_min_row(rng):
    s, t = base(rng, 5, pk=False)
    low = min(t.col("a"))
    dele(s, t, "DELETE FROM t WHERE a = (SELECT MIN(a) FROM t);", lambda r: eq(r["a"], low))
    _nonempty(t)
    return s.item("SELECT MIN(a) FROM t;", min_(t.col("a")), "Every row holding the smallest value goes, so MIN moves up to the next value.")


def d_below_avg(rng):
    s, t = base(rng, 5, pk=False)
    avg = sum(t.col("a")) / len(t.rows)
    dele(s, t, "DELETE FROM t WHERE a < (SELECT AVG(a) FROM t);", lambda r: lt(r["a"], avg))
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The average is worked out once, before any row goes; the rows below it are deleted.")


def _with_x(rng, xs: list, n: int = 5):
    s, t = base(rng, n, mode="plain")
    u = s.create(Table("u", [Col("x")]), [(x,) for x in xs])
    return s, t, u


def d_not_in_null(rng):
    s, t, u = _with_x(rng, [rng.randint(1, 9), None], rng.randint(4, 6))
    xs = u.col("x")
    dele(s, t, "DELETE FROM t WHERE a NOT IN (SELECT x FROM u);", lambda r: not_in(r["a"], xs))
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A NULL in the list makes NOT IN never true, so nothing is deleted.")


def d_not_in_clean(rng):
    s, t, u = _with_x(rng, rng.sample(range(1, 10), 2))
    xs = u.col("x")
    dele(s, t, "DELETE FROM t WHERE a NOT IN (SELECT x FROM u);", lambda r: not_in(r["a"], xs))
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Without a NULL in the list, NOT IN works as expected: the rows not listed are deleted.")


def d_in_subq(rng):
    s, t, u = _with_x(rng, rng.sample(range(1, 10), 3))
    xs = u.col("x")
    dele(s, t, "DELETE FROM t WHERE a IN (SELECT x FROM u);", lambda r: in_list(r["a"], xs))
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "The rows whose a appears in u are deleted.")


def d_ne_null(rng):
    s, t = base(rng, 5, nulls=1, pk=False)
    k = rng.choice([v for v in t.col("a") if v is not None])
    dele(s, t, f"DELETE FROM t WHERE a <> {k};", lambda r: ne(r["a"], k))
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "<> is unknown for the NULL row, so it survives along with the rows equal to k.")


def d_eq_null(rng):
    s, t = base(rng, rng.randint(4, 6), nulls=1, pk=False)
    dele(s, t, "DELETE FROM t WHERE a = NULL;", lambda r: eq(r["a"], None))
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "a = NULL is never true: nothing is deleted.")


def d_is_null(rng):
    s, t = base(rng, rng.randint(5, 7), nulls=rng.randint(1, 2), pk=False)
    dele(s, t, "DELETE FROM t WHERE a IS NULL;", lambda r: r["a"] is None)
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "IS NULL finds the empty rows and removes them.")


def d_not_null(rng):
    s, t = base(rng, rng.randint(5, 7), nulls=rng.randint(1, 3), pk=False)
    dele(s, t, "DELETE FROM t WHERE a IS NOT NULL;", lambda r: r["a"] is not None)
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Every row with a value goes; only the NULL rows are left.")


def d_like(rng):
    s, t = base_named(rng, 5)
    letter = rng.choice(t.col("n"))[1]
    dele(s, t, f"DELETE FROM t WHERE n LIKE '%{letter}%';", lambda r: like(r["n"], f"%{letter}%"))
    _nonempty(t)
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Every name that contains the letter anywhere is deleted.")


def d_text_case(rng):
    s = Script()
    w = rng.choice(["ab", "cd", "ef", "go", "ox"])
    others = rng.sample(["kit", "net", "pad", "zip"], 2)
    t = s.create(Table("t", [Col("n", "TEXT")]), [(w,), (w.upper(),)] + [(o,) for o in others])
    if rng.random() < 0.5:
        dele(s, t, f"DELETE FROM t WHERE n = '{w}';", lambda r: eq(r["n"], w))
        why = "= compares text exactly, so only the lower-case row matches; the upper-case one stays."
    else:
        dele(s, t, f"DELETE FROM t WHERE n LIKE '{w}';", lambda r: like(r["n"], w))
        why = "LIKE ignores the case of letters, so both the lower-case and the upper-case row go."
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), why)


def d_between(rng):
    s, t = base(rng, 6, pk=False)
    lo, hi = sorted(rng.sample(range(2, 9), 2))
    dele(s, t, f"DELETE FROM t WHERE a BETWEEN {lo} AND {hi};", lambda r: between(r["a"], lo, hi))
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "BETWEEN includes both ends, so those rows are all deleted.")


def d_or(rng):
    s, t = base(rng, 6, pk=False)
    m, m2 = rng.randint(2, 4), rng.randint(6, 8)
    dele(s, t, f"DELETE FROM t WHERE a < {m} OR a > {m2};", lambda r: t_or(lt(r["a"], m), gt(r["a"], m2)))
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A row goes if either end matches; the middle values stay.")


def d_text_lt(rng):
    s, t = base_named(rng, 5)
    dele(s, t, "DELETE FROM t WHERE n < 'm';", lambda r: lt(r["n"], "m"))
    _nonempty(t)
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Text compares alphabetically: every name that sorts before 'm' is deleted.")


def d_parity(rng):
    s, t = base(rng, 6)
    dele(s, t, "DELETE FROM t WHERE id % 2 = 0;", lambda r: eq(r["id"] % 2, 0))
    return s.item("SELECT SUM(a) FROM t;", sum(t.col("a")), "id % 2 = 0 picks the even ids; the odd ones stay and are added.")


def d_exists(rng):
    s, t, u = _pair(rng, rng.randint(1, 2), rng.randint(3, 4), False)
    ids = u.col("id")
    dele(s, t, "DELETE FROM t WHERE EXISTS (SELECT 1 FROM u WHERE u.id = t.id);", lambda r: r["id"] in ids)
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A row goes when u has a row with the same id.")


def d_not_exists(rng):
    s, t, u = _pair(rng, rng.randint(1, 2), 3, False)
    ids = u.col("id")
    dele(s, t, "DELETE FROM t WHERE NOT EXISTS (SELECT 1 FROM u WHERE u.id = t.id);", lambda r: r["id"] not in ids)
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A row goes when u has NO row with its id; the matched ones stay.")


def d_dedupe(rng):
    s, t = base(rng, 6, 1, 4, pk=False)
    firsts: dict = {}
    for r in t.rows:
        firsts.setdefault(r["a"], r["id"])
    keep = set(firsts.values())
    dele(s, t, "DELETE FROM t WHERE id NOT IN (SELECT MIN(id) FROM t GROUP BY a);", lambda r: r["id"] not in keep)
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Keeping the lowest id of every value removes the duplicates: one row per different a is left.")


def d_keep_newest(rng):
    s = Script()
    gs = [rng.choice("xyz") for _ in range(6)]
    t = s.create(Table("t", [Col("id"), Col("g", "TEXT")]), [(i + 1, g) for i, g in enumerate(gs)])
    newest: dict = {}
    for r in t.rows:
        newest[r["g"]] = r["id"]
    keep = set(newest.values())
    dele(s, t, "DELETE FROM t WHERE id NOT IN (SELECT MAX(id) FROM t GROUP BY g);", lambda r: r["id"] not in keep)
    return s.item("SELECT SUM(id) FROM t;", sum(t.col("id")), "Only the highest id of each group g survives; the answer adds those ids.")


def d_top_two(rng):
    s, t = base(rng, 5, distinct=True)
    ids = [r["id"] for r in sorted(t.rows, key=lambda r: -r["a"])[:2]]
    dele(s, t, "DELETE FROM t WHERE id IN (SELECT id FROM t ORDER BY a DESC LIMIT 2);", lambda r: r["id"] in ids)
    return s.item("SELECT MAX(a) FROM t;", max_(t.col("a")), "The subquery picks the rows of the two biggest values; the third biggest is now on top.")


def d_oldest(rng):
    s, t = base(rng, rng.randint(4, 6))
    low = min(t.col("id"))
    dele(s, t, "DELETE FROM t WHERE id = (SELECT MIN(id) FROM t);", lambda r: r["id"] == low)
    return s.item("SELECT MIN(id) FROM t;", min_(t.col("id")), "The row with the lowest id is deleted, so the next id is now the lowest.")


def d_window(rng):
    s, t = base(rng, rng.randint(4, 7))
    ids = [r["id"] for r in sorted(t.rows, key=lambda r: r["id"])[1:3]]
    dele(s, t, "DELETE FROM t WHERE id IN (SELECT id FROM t ORDER BY id LIMIT 2 OFFSET 1);", lambda r: r["id"] in ids)
    return s.item("SELECT SUM(id) FROM t;", sum(t.col("id")), "LIMIT 2 OFFSET 1 skips the first id and takes the next two (2 and 3), which are deleted.")


def d_rowid_reuse(rng):
    n = rng.randint(3, 5)
    s, t = base(rng, n)
    s.dml(f"DELETE FROM t WHERE id = {n};", lambda: t.delete(lambda r: r["id"] == n))
    s.insert(t, [(rng.randint(1, 9),)], ["a"])
    return s.item("SELECT MAX(id) FROM t;", max_(t.col("id")), "An INTEGER PRIMARY KEY row gets max(id)+1; with the top id gone, the new row takes that id again.")


def d_rowid_gap(rng):
    n = rng.randint(4, 6)
    s, t = base(rng, n)
    k = rng.randint(2, n - 1)
    s.dml(f"DELETE FROM t WHERE id = {k};", lambda: t.delete(lambda r: r["id"] == k))
    s.insert(t, [(rng.randint(1, 9),)], ["a"])
    return s.item("SELECT MAX(id) FROM t;", max_(t.col("id")), "The new id is max(id)+1; the gap left by the deleted middle id is not refilled.")


def d_all_restart(rng):
    s, t = base(rng, 4)
    dele(s, t, "DELETE FROM t;")
    s.insert(t, [(rng.randint(1, 9),)], ["a"])
    return s.item("SELECT id FROM t;", t.col("id")[0], "With the table empty, max(id)+1 starts again at 1.")


def _auto(rng, n: int):
    s = Script()
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True, autoinc=True), Col("a")]), [(rng.randint(1, 9),) for _ in range(n)], ["a"])
    return s, t


def d_autoinc_last(rng):
    n = rng.randint(3, 5)
    s, t = _auto(rng, n)
    s.dml(f"DELETE FROM t WHERE id = {n};", lambda: t.delete(lambda r: r["id"] == n))
    s.insert(t, [(rng.randint(1, 9),)], ["a"])
    return s.item("SELECT MAX(id) FROM t;", max_(t.col("id")), "AUTOINCREMENT never reuses an id, even one that was deleted: the new row is one past the old top id.")


def d_autoinc_all(rng):
    s, t = _auto(rng, rng.randint(3, 4))
    dele(s, t, "DELETE FROM t;")
    s.insert(t, [(rng.randint(1, 9),)], ["a"])
    return s.item("SELECT id FROM t;", t.col("id")[0], "AUTOINCREMENT remembers the highest id ever used, so the counter goes on after the deleted rows.")


def d_changes(rng):
    s, t = base(rng, 6, pk=False)
    m = _k(rng, 3, 7)
    dele(s, t, f"DELETE FROM t WHERE a > {m};", lambda r: gt(r["a"], m))
    return s.item("SELECT changes();", s.changes, "changes() is the number of rows the last DELETE removed.")


def d_changes_all(rng):
    s, t = base(rng, rng.randint(4, 7), pk=False)
    dele(s, t, "DELETE FROM t;")
    return s.item("SELECT changes();", s.changes, "Even a DELETE with no WHERE reports how many rows it removed.")


def d_changes_none(rng):
    s, t = base(rng, rng.randint(4, 6), pk=False)
    dele(s, t, "DELETE FROM t WHERE a > 50;", lambda r: gt(r["a"], 50))
    return s.item("SELECT changes();", s.changes, "No row matches, so 0 rows were deleted.")


def d_twice_max(rng):
    s, t = base(rng, 6, distinct=True, pk=False)
    for _ in range(2):
        top = max(t.col("a"))
        dele(s, t, "DELETE FROM t WHERE a = (SELECT MAX(a) FROM t);", lambda r, top=top: eq(r["a"], top))
    return s.item("SELECT MAX(a) FROM t;", max_(t.col("a")), "Each DELETE removes the current biggest row, so after two the third biggest is on top.")


def d_dup_values(rng):
    s, t = base(rng, 6, 1, 4, pk=False)
    counts = {v: t.col("a").count(v) for v in t.col("a")}
    dele(s, t, "DELETE FROM t WHERE a IN (SELECT a FROM t GROUP BY a HAVING COUNT(*) > 1);", lambda r: counts[r["a"]] > 1)
    _nonempty(t)
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Every value that appears more than once is deleted from all its rows; only the values seen once remain.")


def d_distinct_after(rng):
    s, t = base(rng, 6, pk=False)
    m = _k(rng, 3, 6)
    dele(s, t, f"DELETE FROM t WHERE a > {m};", lambda r: gt(r["a"], m))
    _nonempty(t)
    return s.item("SELECT COUNT(DISTINCT a) FROM t;", count_distinct(t.col("a")), "After the DELETE the query counts the different values still in the table.")


def d_above_min(rng):
    s, t = base(rng, 5, pk=False)
    k = _k(rng, 2, 4)
    low = min(t.col("a"))
    dele(s, t, f"DELETE FROM t WHERE a > (SELECT MIN(a) FROM t) + {k};", lambda r: gt(r["a"], low + k))
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "Rows more than k above the smallest value are deleted.")


def d_and_text(rng):
    s = Script()
    vals = [rng.randint(1, 9) for _ in range(5)]
    tags = [rng.choice(["x", "y", None]) for _ in range(5)]
    t = s.create(Table("t", [Col("a"), Col("b", "TEXT")]), list(zip(vals, tags)))
    m = _k(rng, 3, 6)
    dele(s, t, f"DELETE FROM t WHERE a > {m} AND b <> 'x';", lambda r: t_and(gt(r["a"], m), ne(r["b"], "x")))
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "A row needs both a big a and a b that is surely not 'x'; a NULL b is unknown, so that row stays.")


def _tree(rng):
    """Rows of t(id, boss): 1 is the root and every other row reports to an earlier one."""
    return [(1, None)] + [(i, rng.randint(1, i - 1)) for i in range(2, 5)]


def _descend(rows, k):
    """k and everybody who reports to k, directly or not."""
    gone = {k}
    grew = True
    while grew:
        grew = False
        for i, boss in rows:
            if boss in gone and i not in gone:
                gone.add(i)
                grew = True
    return gone


def _fk(rng, action: str, pragma: bool):
    s = Script()
    if pragma:
        s.run("PRAGMA foreign_keys=ON;")
    rows = _tree(rng)
    t = s.create(Table("t", [Col("id", "INTEGER", pk=True), Col("b", f"REFERENCES t ON DELETE {action}")]), rows)
    return s, t, rows


def d_cascade(rng):
    s, t, rows = _fk(rng, "CASCADE", True)
    k = rng.randint(1, 4)
    gone = _descend(rows, k)
    dele(s, t, f"DELETE FROM t WHERE id = {k};", lambda r: r["id"] in gone)
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "With foreign keys ON, ON DELETE CASCADE also deletes the rows that point at a deleted row, and the rows pointing at those.")


def d_cascade_off(rng):
    s, t, rows = _fk(rng, "CASCADE", False)
    k = rng.randint(1, 4)
    dele(s, t, f"DELETE FROM t WHERE id = {k};", lambda r: r["id"] == k)
    return s.item("SELECT COUNT(*) FROM t;", len(t.rows), "SQLite ignores foreign keys unless PRAGMA foreign_keys=ON is run: only the one row is deleted.")


def d_set_null(rng):
    s, t, rows = _fk(rng, "SET NULL", True)
    k = rng.randint(1, 4)
    kids = {i for i, b in rows if b == k}
    dele(s, t, f"DELETE FROM t WHERE id = {k};", lambda r: r["id"] == k)
    for r in t.rows:
        if r["id"] in kids:
            r["b"] = None
    nulls = sum(1 for r in t.rows if r["b"] is None)
    return s.item("SELECT COUNT(*) FROM t WHERE b IS NULL;", nulls, "ON DELETE SET NULL keeps the children but empties their link; a row that already had no boss counts too.")


DELETES: list[Maker] = [fit(f) for f in (
    d_where_count, d_where_sum, d_all, d_all_then_insert, d_empty_agg, d_max_row, d_min_row, d_below_avg, d_not_in_null,
    d_not_in_clean, d_in_subq, d_ne_null, d_eq_null, d_is_null, d_not_null, d_like, d_text_case, d_between, d_or,
    d_text_lt, d_parity, d_exists, d_not_exists, d_dedupe, d_keep_newest, d_top_two, d_oldest, d_window, d_rowid_reuse,
    d_rowid_gap, d_all_restart, d_autoinc_last, d_autoinc_all, d_changes, d_changes_all, d_changes_none, d_twice_max,
    d_dup_values, d_distinct_after, d_above_min, d_and_text, d_cascade, d_cascade_off, d_set_null)]
