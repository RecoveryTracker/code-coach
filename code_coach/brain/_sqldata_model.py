"""The model of SQL WRITES (INSERT, UPDATE, DELETE, constraints, ALTER TABLE, transactions) for the `sd_*` activities of
`pack_sqldata.py`: the sibling of `_sql_model.py`, which models what a SELECT reads. Nothing here asks SQLite anything; the
tests (tests/sql_oracle.py through tests/test_brain_packs.py, or `python -m tests.brain_check sqldata`) hold every answer to the
real one.

`Table` keeps its rows as dicts (plus a hidden `_rowid`) and knows its columns' constraints, so `insert`, `update` and
`delete` do what SQLite does: fill omitted columns with their DEFAULT (or NULL), assign a missing INTEGER PRIMARY KEY as
max(rowid)+1 (AUTOINCREMENT never goes back), refuse a NOT NULL, CHECK or UNIQUE violation by skipping the row (`OR IGNORE`),
replacing the old row (`OR REPLACE`) or updating it (upsert). A CHECK fails only when it is FALSE (NULL passes); NULLs never
collide in a UNIQUE column. A statement that would FAIL raises `Aborts`: an item must never depend on an uncaught error (the
driver stops the script there), so a template that hits it is a bug in the template.

`Script` records the SQL lines of an item next to the model's work on them (`run`, `dml`, `insert`) and builds the Item
(`item`). It also keeps `changes` and `last_rowid` (what `changes()` and `last_insert_rowid()` return) and a stack of
snapshots for BEGIN / SAVEPOINT / ROLLBACK [TO] / RELEASE / COMMIT.

A script that uses BEGIN has a `COMMIT;` after the setup: the runner's Python opens a transaction by itself at the first
INSERT, and a BEGIN inside it would fail ("cannot start a transaction within a transaction").
"""

from __future__ import annotations

import copy
import re
from typing import Any, Callable

from ._sql_model import NULL, Retry, Tbl, lit, render, show  # noqa: F401  (re-exported for the templates)
from .items import Item

NODEF: Any = object()


class Aborts(Exception):
    """The statement would fail in SQLite (and the driver would stop): a template must not produce this."""


_INT_RE = re.compile(r"^\s*[+-]?\d+\s*$")


def coerce(typ: str, v: Any) -> Any:
    """What column affinity does to a stored value: INT turns '5' and 5.0 into 5, TEXT turns numbers into text, REAL turns 5 into 5.0."""
    t = typ.upper()
    if v is None:
        return None
    if t in ("INT", "INTEGER"):
        if isinstance(v, str) and _INT_RE.match(v):
            return int(v)
        if isinstance(v, float) and v == int(v):
            return int(v)
        return v
    if t == "TEXT":
        if isinstance(v, float):
            return repr(v)
        if isinstance(v, int):
            return str(v)
        return v
    if t == "REAL":
        return float(v) if isinstance(v, int) else v
    return v


class Col:
    """A column: its type, constraints and DEFAULT; `check` is (sql, fn(row) -> True/False/None) written inline."""

    def __init__(self, name: str, typ: str = "INT", *, pk: bool = False, autoinc: bool = False, unique: bool = False,
                 not_null: bool = False, default: Any = NODEF, nocase: bool = False,
                 check: tuple[str, Callable[[dict], Any]] | None = None) -> None:
        self.name, self.typ, self.pk, self.autoinc, self.unique = name, typ, pk, autoinc, unique
        self.not_null, self.default, self.nocase, self.check = not_null, default, nocase, check

    @property
    def is_rowid(self) -> bool:
        return self.pk and self.typ.upper() == "INTEGER"

    def ddl(self) -> str:
        s = f"{self.name} {self.typ}"
        if self.pk:
            s += " PRIMARY KEY" + (" AUTOINCREMENT" if self.autoinc else "")
        if self.not_null:
            s += " NOT NULL"
        if self.unique:
            s += " UNIQUE"
        if self.nocase:
            s += " COLLATE NOCASE"
        if self.default is not NODEF:
            s += " DEFAULT " + lit(self.default)
        if self.check:
            s += f" CHECK ({self.check[0]})"
        return s


class Table:
    def __init__(self, name: str, cols: list[Col], *, unique: tuple = (), checks: tuple = (), partial: tuple = ()) -> None:
        self.name, self.cols = name, list(cols)
        #: composite UNIQUE(a, b) sets; table-level CHECKs (sql, fn(row)); partial unique indexes (cols, where-sql, fn(row))
        self.unique = [tuple(u) for u in unique]
        self.checks = list(checks)
        self.partial = list(partial)
        self.rows: list[dict] = []
        self.seq = 0
        self.last_rowid: int | None = None

    # ── the SQL ──
    def ddl(self) -> str:
        parts = [c.ddl() for c in self.cols] + [f"UNIQUE({', '.join(u)})" for u in self.unique] \
            + [f"CHECK ({sql})" for sql, _ in self.checks]
        return f"CREATE TABLE {self.name}({', '.join(parts)});"

    def index_lines(self) -> list[str]:
        return [f"CREATE UNIQUE INDEX {self.name}_u{i} ON {self.name}({', '.join(cols)}) WHERE {sql};"
                for i, (cols, sql, _) in enumerate(self.partial)]

    @property
    def names(self) -> list[str]:
        return [c.name for c in self.cols]

    def col_of(self, name: str) -> Col:
        return next(c for c in self.cols if c.name == name)

    @property
    def rowid_col(self) -> Col | None:
        return next((c for c in self.cols if c.is_rowid), None)

    # ── reading (what the final SELECT is worked out from) ──
    def col(self, name: str) -> list:
        return [r[name] for r in self.rows]

    def tuples(self, *names: str) -> list[tuple]:
        names = names or tuple(self.names)
        return [tuple(r[n] for n in names) for r in self.rows]

    def find(self, pred: Callable[[dict], Any]) -> list[dict]:
        return [r for r in self.rows if pred(r) is True]

    def one(self, name: str, pred: Callable[[dict], Any]) -> Any:
        hit = self.find(pred)
        assert len(hit) == 1, "a single-row answer must match exactly one row"
        return hit[0][name]

    # ── unique machinery ──
    def _key(self, cols: tuple, row: dict) -> tuple | None:
        """The index key of a row for these columns (None when a NULL is in it: NULLs never collide)."""
        out = []
        for n in cols:
            v = row[n]
            if v is None:
                return None
            if isinstance(v, str) and self.col_of(n).nocase:
                v = v.lower()
            out.append(v)
        return tuple(out)

    def _unique_sets(self) -> list[tuple[tuple, Callable[[dict], Any] | None]]:
        sets: list = [((c.name,), None) for c in self.cols if (c.unique or c.pk) and not c.is_rowid]
        sets += [(u, None) for u in self.unique]
        sets += [(cols, fn) for cols, _sql, fn in self.partial]
        return sets

    def _conflicts(self, row: dict, ignore: dict | None = None) -> list[tuple[tuple, dict]]:
        found = []
        rc = self.rowid_col
        for other in self.rows:
            if other is ignore:
                continue
            if rc is not None and other[rc.name] == row[rc.name]:
                found.append(((rc.name,), other))
                continue
            for cols, fn in self._unique_sets():
                if fn is not None and not (fn(row) is True and fn(other) is True):
                    continue
                k = self._key(cols, row)
                if k is not None and k == self._key(cols, other):
                    found.append((cols, other))
                    break
        return found

    def _violates(self, row: dict) -> str | None:
        for c in self.cols:
            if c.not_null and row[c.name] is None:
                return "NOT NULL"
            if c.check and c.check[1](row) is False:
                return "CHECK"
        for _sql, fn in self.checks:
            if fn(row) is False:
                return "CHECK"
        return None

    def next_rowid(self) -> int:
        top = max((r["_rowid"] for r in self.rows), default=0)
        rc = self.rowid_col
        if rc is not None and rc.autoinc:
            top = max(top, self.seq)
        return top + 1

    # ── INSERT ──
    def insert(self, vals: dict | None = None, mode: str = "abort", upsert: tuple | None = None) -> int:
        """One row of an INSERT: `vals` the columns given (the rest get their DEFAULT or NULL). mode: abort | ignore |
        replace. `upsert` = (conflict-cols, {col: fn(old, excluded)} or None for DO NOTHING, where fn(old, excluded) or None).
        Returns the number of rows the statement counts in changes() (a skipped row is 0, an upsert update is 1)."""
        vals = vals or {}
        row = {}
        for c in self.cols:
            if c.name in vals:
                row[c.name] = coerce(c.typ, vals[c.name])
            else:
                row[c.name] = None if c.default is NODEF else c.default
        rc = self.rowid_col
        if rc is not None:
            if row[rc.name] is None:
                row[rc.name] = self.next_rowid()
            row["_rowid"] = row[rc.name]
        else:
            row["_rowid"] = self.next_rowid()
        why = self._violates(row)
        if why:
            if mode == "ignore":
                return 0
            raise Aborts(why)
        conflicts = self._conflicts(row)
        if conflicts:
            if upsert is not None:
                cols, sets, where = upsert
                assert len(conflicts) == 1 and conflicts[0][0] == tuple(cols), "the upsert target must be the only conflict"
                old = conflicts[0][1]
                if sets is None:
                    return 0
                if where is not None and where(old, row) is not True:
                    return 0
                new = dict(old)
                for n, fn in sets.items():
                    new[n] = coerce(self.col_of(n).typ, fn(old, row))
                if self._violates(new):
                    raise Aborts("constraint in DO UPDATE")
                old.update(new)
                return 1
            if mode == "ignore":
                return 0
            if mode == "replace":
                dead = {id(o) for _c, o in conflicts}
                self.rows = [r for r in self.rows if id(r) not in dead]
            else:
                raise Aborts("UNIQUE")
        self.rows.append(row)
        self.last_rowid = row["_rowid"]
        if rc is not None and rc.autoinc:
            self.seq = max(self.seq, row["_rowid"])
        return 1

    # ── UPDATE / DELETE ──
    def update(self, sets: dict[str, Callable[[dict], Any]], where: Callable[[dict], Any] | None = None, mode: str = "abort") -> int:
        """UPDATE: every SET value is worked out from the row as it WAS; returns the rows the WHERE matched (changes())."""
        hits = [r for r in self.rows if where is None or where(r) is True]
        n = 0
        for r in hits:
            new = dict(r)
            for k, fn in sets.items():
                new[k] = coerce(self.col_of(k).typ, fn(r))
            rc = self.rowid_col
            if rc is not None:
                if new[rc.name] is None:
                    raise Aborts("datatype mismatch")
                new["_rowid"] = new[rc.name]
            if self._violates(new):
                if mode == "ignore":
                    continue
                raise Aborts("constraint")
            conflicts = self._conflicts(new, ignore=r)
            if conflicts:
                if mode == "ignore":
                    continue
                if mode == "replace":
                    dead = {id(o) for _c, o in conflicts}
                    self.rows = [x for x in self.rows if id(x) not in dead]
                else:
                    raise Aborts("UNIQUE")
            r.update(new)
            n += 1
        return n

    def delete(self, where: Callable[[dict], Any] | None = None) -> int:
        keep = [r for r in self.rows if not (where is None or where(r) is True)]
        n = len(self.rows) - len(keep)
        self.rows = keep
        return n

    # ── ALTER TABLE ──
    def add_column(self, col: Col) -> None:
        self.cols.append(col)
        for r in self.rows:
            r[col.name] = None if col.default is NODEF else coerce(col.typ, col.default)

    def drop_column(self, name: str) -> None:
        self.cols = [c for c in self.cols if c.name != name]
        for r in self.rows:
            r.pop(name)

    def rename_column(self, old: str, new: str) -> None:
        self.col_of(old).name = new
        for r in self.rows:
            r[new] = r.pop(old)

    # ── snapshots (transactions) ──
    def snap(self) -> tuple:
        return copy.deepcopy(self.rows), self.seq

    def restore(self, snap: tuple) -> None:
        self.rows, self.seq = copy.deepcopy(snap[0]), snap[1]


class Script:
    """The lines of an item, the model's state, and the Item at the end."""

    def __init__(self) -> None:
        self.lines: list[str] = []
        self.tables: dict[str, Table] = {}
        self.changes = 0
        self.last_rowid = 0
        self._stack: list[tuple[str, dict]] = []

    # ── building ──
    def run(self, sql: str, fn: Callable[[], Any] | None = None) -> None:
        """A statement that is not a row change (or whose changes() nobody asks about)."""
        self.lines.append(sql)
        if fn:
            fn()

    def dml(self, sql: str, fn: Callable[[], int]) -> int:
        """A row-changing statement: `fn` does it in the model and returns changes()."""
        self.lines.append(sql)
        n = fn()
        self.changes = n
        return n

    def create(self, t: Table, rows: list[tuple] | None = None, cols: list[str] | None = None, mode: str = "abort") -> Table:
        """CREATE TABLE (and its partial indexes), then the INSERT of `rows` (positional, all the columns, or the named `cols`)."""
        self.tables[t.name] = t
        self.lines.append(t.ddl())
        self.lines.extend(t.index_lines())
        if rows:
            self.insert(t, rows, cols, mode)
        return t

    def insert(self, t: Table, rows: list[tuple], cols: list[str] | None = None, mode: str = "abort") -> int:
        names = cols or t.names
        head = "INSERT " + {"abort": "", "ignore": "OR IGNORE ", "replace": "OR REPLACE "}[mode] + f"INTO {t.name}"
        if cols:
            head += f"({','.join(cols)})"
        sql = head + " VALUES " + ",".join("(" + ",".join(lit(v) for v in r) + ")" for r in rows) + ";"
        return self.dml(sql, lambda: self._insert_rows(t, names, rows, mode))

    def insert_sql(self, sql: str, t: Table, rows: list[tuple], cols: list[str] | None = None, mode: str = "abort") -> int:
        """An INSERT whose SQL is written by hand (INSERT ... SELECT, DEFAULT VALUES, upserts): `rows` are the rows it adds,
        worked out by the template, for the columns `cols` (default: all of them)."""
        return self.dml(sql, lambda: self._insert_rows(t, cols or t.names, rows, mode))

    def _insert_rows(self, t: Table, names: list[str], rows: list[tuple], mode: str) -> int:
        n = 0
        for r in rows:
            n += t.insert(dict(zip(names, r)), mode)
            if t.last_rowid is not None:
                self.last_rowid = t.last_rowid
        return n

    def item(self, query: str, answer: Any, why: str) -> Item:
        prompt = "\n".join(self.lines + [query])
        if isinstance(answer, str):
            text = answer
        elif isinstance(answer, list):
            text = render(answer)
        else:
            text = show(answer)
        return Item(prompt, text, why)

    # ── transactions ──
    def _snap(self) -> dict:
        return {n: t.snap() for n, t in self.tables.items()}

    def _restore(self, snap: dict) -> None:
        for n, s in snap.items():
            self.tables[n].restore(s)

    def commit_setup(self) -> None:
        """The `COMMIT;` that ends the setup of a script about transactions (see the module docstring)."""
        self.run("COMMIT;")

    def begin(self, word: str = "BEGIN") -> None:
        self.run(word + ";", lambda: self._stack.append(("", self._snap())))

    def savepoint(self, name: str) -> None:
        self.run(f"SAVEPOINT {name};", lambda: self._stack.append((name, self._snap())))

    def rollback_to(self, name: str) -> None:
        def go() -> None:
            k = max(i for i, (n, _) in enumerate(self._stack) if n == name)
            self._restore(self._stack[k][1])
            del self._stack[k + 1:]
        self.run(f"ROLLBACK TO {name};", go)

    def release(self, name: str) -> None:
        def go() -> None:
            k = max(i for i, (n, _) in enumerate(self._stack) if n == name)
            del self._stack[k:]
        self.run(f"RELEASE {name};", go)

    def commit(self, word: str = "COMMIT") -> None:
        self.run(word + ";", self._stack.clear)

    def rollback(self) -> None:
        def go() -> None:
            self._restore(self._stack[0][1])
            self._stack.clear()
        self.run("ROLLBACK;", go)


# ── Random data and little helpers shared by the templates ──────────────

def nz(v: Any, f: Callable[[Any], Any]) -> Any:
    """f(v) unless v is NULL: arithmetic and functions on NULL give NULL."""
    return None if v is None else f(v)


def base(rng, n: int = 5, lo: int = 1, hi: int = 9, nulls: int = 0, distinct: bool = False, name: str = "t",
         col: str = "a", mode: str = "ids", pk: bool = True) -> tuple[Script, Table]:
    """A script with `t(id INTEGER PRIMARY KEY, a INT)` created and filled with ids 1..n and small random values
    (with `nulls` NULLs; `distinct` for no repeats). mode "plain" leaves the id out: `t(a INT)`; `pk=False` makes the id a
    plain INT (shorter, and no rowid behaviour to think about)."""
    vals = rng.sample(range(lo, hi + 1), n) if distinct else [rng.randint(lo, hi) for _ in range(n)]
    for k in rng.sample(range(n), nulls):
        vals[k] = None
    s = Script()
    if mode == "plain":
        t = s.create(Table(name, [Col(col)]), [(v,) for v in vals])
    else:
        t = s.create(Table(name, [Col("id", "INTEGER" if pk else "INT", pk=pk), Col(col)]),
                     [(i + 1, v) for i, v in enumerate(vals)])
    return s, t


def base_named(rng, n: int = 5, lo: int = 1, hi: int = 9, nulls: int = 0, name: str = "t") -> tuple[Script, Table]:
    """A script with `t(id INTEGER PRIMARY KEY, n TEXT, a INT)`: ids 1..n, distinct short words, small numbers."""
    from ._sql_model import words
    ws = words(rng, n)
    vals = [rng.randint(lo, hi) for _ in range(n)]
    for k in rng.sample(range(n), nulls):
        vals[k] = None
    s = Script()
    t = s.create(Table(name, [Col("id", "INTEGER", pk=True), Col("n", "TEXT"), Col("a")]),
                 [(i + 1, ws[i], vals[i]) for i in range(n)])
    return s, t
