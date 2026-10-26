"""Hand-built models of what SQL (SQLite) does, for the SQL packs (the sibling of `_model.py`, `_dart_model.py`, `_c_model.py`).

Nothing here asks SQLite anything: a table is a list of tuples, NULL is `None`, a condition is a Python function that may
answer `None` ("unknown": three-valued logic), `WHERE` keeps only the rows where it is `True`, `/` between two integers
cuts toward zero and gives NULL for a zero divisor, `COUNT(col)` skips NULLs, `AVG` of nothing is NULL, a join is a loop,
a window is a sort and a walk. tests/sql_oracle.py then runs every item in a fresh in-memory SQLite (Python's own
sqlite3) and compares (the oracle rule), so a wrong model is a failing test.

THE ITEM CONVENTION (the same rule in `tests/sql_oracle.run_sql`, in "Run it" - `POST /api/brain/run` with language `sql`
goes through the Gotchas runner's SQLite driver - and in the `check` field):

* the program is `item.check`, or the prompt when `check` is empty; it is a complete SQL script: `CREATE TABLE ...;`
  `INSERT INTO t VALUES (1,'a'),(2,'b');` and so on, ending with the query that is asked about;
* statements end with `;` and no `;` appears inside a string;
* the VALUE is what the driver prints for the LAST statement that returns rows: each row as its columns joined with `|`,
  the rows joined with `; `, NULL written `NULL`, text bare, an integer as digits, a real the way Python's `repr` writes
  it (`2.0`, `3.5`, `0.30000000000000004`). An answer is almost always ONE value (a number, a word, `NULL`): the answer
  format has no spaces to get wrong. A query that returns no rows prints nothing, so it is never an answer;
* SQLite semantics (not PostgreSQL's): `7 / 2` is `3`, `x / 0` is NULL, `||` with NULL is NULL, NULLs sort first, `LIKE`
  ignores case for ASCII, `COUNT(*)` counts rows, `typeof()` exists, window functions work (3.25+).

`Tbl(name, cols, rows)` makes the `CREATE TABLE` and `INSERT` lines; `sql_item(tables, query, answer, why)` builds the
Item (the answer a Python value, a list of row tuples, or an already printed string). Templates are plain functions
`(rng) -> Item`; `fit(f)` re-rolls a template that comes out longer than 220 characters or 10 lines (`raise Retry` to
re-roll for any other reason).
"""

from __future__ import annotations

import random
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Callable, Iterable

from ._model import WORDS, Maker, tdiv, tmod
from .items import Item

NULL = None


class Retry(Exception):
    """The random data does not suit the template (a tie where the answer must be unique...): roll again."""


# ── Printing, as the driver does ────────────────────────────────────────

def show(v: Any) -> str:
    """One value as the driver prints it."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, float):
        return repr(v)
    return str(v)


def render(rows: Iterable[tuple]) -> str:
    """The rows of the last SELECT: columns joined with `|`, rows with `; `."""
    return "; ".join("|".join(show(v) for v in row) for row in rows)


def lit(v: Any) -> str:
    """SQL source for a value."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, str):
        return "'" + v.replace("'", "''") + "'"
    if isinstance(v, float):
        return repr(v)
    return str(v)


class Tbl:
    """A table: its lines of SQL and its rows for the model."""

    def __init__(self, name: str, cols: list[tuple[str, str]], rows: list[tuple]) -> None:
        self.name, self.cols, self.rows = name, cols, [tuple(r) for r in rows]

    def ddl(self) -> str:
        return f"CREATE TABLE {self.name}({', '.join(f'{c} {t}' for c, t in self.cols)});"

    def ins(self) -> str:
        return f"INSERT INTO {self.name} VALUES " + ",".join("(" + ",".join(lit(v) for v in r) + ")" for r in self.rows) + ";"

    def lines(self) -> list[str]:
        return [self.ddl(), self.ins()]

    def i(self, col: str) -> int:
        return [c for c, _ in self.cols].index(col)

    def col(self, col: str) -> list:
        k = self.i(col)
        return [r[k] for r in self.rows]


def sql_item(tables: list[Tbl], query: str, answer: Any, why: str) -> Item:
    """The Item for a script: the tables' lines, then the query; `answer` a value, a list of row tuples, or text."""
    prompt = "\n".join([ln for t in tables for ln in t.lines()] + [query])
    if isinstance(answer, str):
        text = answer
    elif isinstance(answer, list):
        text = render(answer)
    else:
        text = show(answer)
    return Item(prompt, text, why)


def fit(build: Callable[[random.Random], Item]) -> Maker:
    """A template that re-rolls (up to 80 times) when its item is over 220 characters or 10 lines, or `raise Retry`s."""
    def make(rng: random.Random) -> Item:
        for _ in range(80):
            try:
                item = build(rng)
            except Retry:
                continue
            if len(item.prompt) <= 220 and item.prompt.count("\n") <= 9 and item.answer:
                return item
        raise AssertionError(f"template {build.__name__} never fits in 220 characters / 10 lines")
    make.__name__ = "sql_" + build.__name__.lstrip("_")
    return make


# ── Random data ─────────────────────────────────────────────────────────

def ints(rng: random.Random, n: int, lo: int = 1, hi: int = 9) -> list[int]:
    """n different ints."""
    return rng.sample(range(lo, hi + 1), n)


def words(rng: random.Random, n: int) -> list[str]:
    """n different short lower-case words."""
    return rng.sample([w for w in WORDS if len(w) <= 5], n)


def with_nulls(rng: random.Random, values: list, how_many: int = 1) -> list:
    """The values with `how_many` of them replaced by NULL."""
    out = list(values)
    for k in rng.sample(range(len(out)), how_many):
        out[k] = None
    return out


# ── Three-valued logic ──────────────────────────────────────────────────

def t_not(a):
    return None if a is None else (not a)


def t_and(a, b):
    if a is False or b is False:
        return False
    if a is None or b is None:
        return None
    return True


def t_or(a, b):
    if a is True or b is True:
        return True
    if a is None or b is None:
        return None
    return False


def _cmp(op: str, a, b):
    if a is None or b is None:
        return None
    return {"=": a == b, "<>": a != b, "<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op]


def eq(a, b): return _cmp("=", a, b)
def ne(a, b): return _cmp("<>", a, b)
def lt(a, b): return _cmp("<", a, b)
def gt(a, b): return _cmp(">", a, b)
def le(a, b): return _cmp("<=", a, b)
def ge(a, b): return _cmp(">=", a, b)


def between(x, lo, hi):
    return t_and(ge(x, lo), le(x, hi))


def is_null(x) -> bool:
    return x is None


def in_list(x, xs: list):
    """x IN (xs): NULL when x is NULL (and the list is not empty), or when no match was found but a NULL was in the list."""
    if not xs:
        return False
    if x is None:
        return None
    if any(v is not None and v == x for v in xs):
        return True
    return None if any(v is None for v in xs) else False


def not_in(x, xs: list):
    return t_not(in_list(x, xs))


def like(s, pattern: str):
    """s LIKE pattern: `%` any run, `_` one character, ASCII letters ignore case; NULL gives NULL."""
    if s is None:
        return None
    text, pat = s.lower(), pattern.lower()

    def match(i: int, j: int) -> bool:
        if j == len(pat):
            return i == len(text)
        if pat[j] == "%":
            return any(match(k, j + 1) for k in range(i, len(text) + 1))
        if i < len(text) and (pat[j] == "_" or pat[j] == text[i]):
            return match(i + 1, j + 1)
        return False

    return match(0, 0)


def where(rows: list, pred: Callable[[tuple], Any]) -> list:
    """WHERE: only the rows for which the condition is True (False and unknown both drop a row)."""
    return [r for r in rows if pred(r) is True]


# ── Aggregates ──────────────────────────────────────────────────────────

def count_star(rows: list) -> int:
    return len(rows)


def count_col(values: list) -> int:
    return sum(1 for v in values if v is not None)


def count_distinct(values: list) -> int:
    return len({v for v in values if v is not None})


def sum_(values: list):
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    total = 0
    for v in vals:
        total += v
    return total


def total_(values: list) -> float:
    s = sum_(values)
    return 0.0 if s is None else float(s)


def avg_(values: list):
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    total = 0
    for v in vals:
        total += v
    return total / len(vals)


def min_(values: list):
    vals = [v for v in values if v is not None]
    return min(vals) if vals else None


def max_(values: list):
    vals = [v for v in values if v is not None]
    return max(vals) if vals else None


def group(rows: list, key: Callable[[tuple], Any]) -> dict:
    """GROUP BY: {key: rows}, in the order the keys first appear (NULL is a group of its own)."""
    out: dict = {}
    for r in rows:
        out.setdefault(key(r), []).append(r)
    return out


# ── Ordering ────────────────────────────────────────────────────────────

def order_by(rows: list, *keys: tuple[Callable[[tuple], Any], bool]) -> list:
    """ORDER BY key [DESC], ...: each key is (function, descending). NULLs are the SMALLEST values: first when ascending,
    last when descending. Python's sort is stable, like keeping ties in table order (SQLite does not promise it: items
    avoid ties)."""
    out = list(rows)
    for fn, desc in reversed(keys):
        out.sort(key=lambda r: (fn(r) is not None, fn(r) if fn(r) is not None else 0), reverse=desc)
    return out


def no_ties(rows: list, fn: Callable[[tuple], Any]) -> None:
    """Refuse (Retry) data where two rows tie on an ordering key, so the answer does not depend on the engine's tie order."""
    keys = [fn(r) for r in rows]
    if len(set(keys)) != len(keys):
        raise Retry


# ── Joins ───────────────────────────────────────────────────────────────

def cross(left: list, right: list) -> list[tuple]:
    return [l + r for l in left for r in right]


def inner(left: list, right: list, on: Callable[[tuple, tuple], Any]) -> list[tuple]:
    return [l + r for l in left for r in right if on(l, r) is True]


def left_join(left: list, right: list, on: Callable[[tuple, tuple], Any], right_width: int) -> list[tuple]:
    out = []
    for l in left:
        hit = [r for r in right if on(l, r) is True]
        out.extend(l + r for r in hit) if hit else out.append(l + (None,) * right_width)
    return out


# ── Windows ─────────────────────────────────────────────────────────────

def row_number(rows: list, key: Callable[[tuple], Any], desc: bool = False) -> list[tuple]:
    """(row, ROW_NUMBER() OVER (ORDER BY key)) for each row, in the window's order."""
    ordered = order_by(rows, (key, desc))
    return [(r, i + 1) for i, r in enumerate(ordered)]


def rank_dense(rows: list, key: Callable[[tuple], Any], desc: bool = False) -> list[tuple]:
    """(row, RANK(), DENSE_RANK()) in the window's order: ties share a rank; RANK skips after a tie, DENSE_RANK does not."""
    ordered = order_by(rows, (key, desc))
    out, rank, dense = [], 0, 0
    for i, r in enumerate(ordered):
        if i == 0 or key(r) != key(ordered[i - 1]):
            rank, dense = i + 1, dense + 1
        out.append((r, rank, dense))
    return out


def running_sum(rows: list, order: Callable[[tuple], Any], value: Callable[[tuple], Any], desc: bool = False) -> list[tuple]:
    """(row, SUM(value) OVER (ORDER BY order)) in the window's order. The default frame is RANGE: a row's PEERS (rows with
    the same order key) are all included, so tied rows share one running total."""
    ordered = order_by(rows, (order, desc))
    out = []
    for r in ordered:
        peers_through = [x for x in ordered if (order(x) <= order(r) if not desc else order(x) >= order(r))]
        out.append((r, sum_([value(x) for x in peers_through])))
    return out


# ── Scalar functions ────────────────────────────────────────────────────

def sql_div(a, b):
    """a / b: two integers divide and cut toward zero; a zero divisor gives NULL."""
    if a is None or b is None or b == 0:
        return None
    if isinstance(a, int) and isinstance(b, int):
        return tdiv(a, b)
    return a / b


def sql_mod(a, b):
    """a % b for integers: the sign of the dividend; a zero divisor gives NULL."""
    if a is None or b is None or b == 0:
        return None
    return tmod(a, b)


def sql_round(x, digits: int = 0) -> float:
    """ROUND(x, digits): always a real, halves away from zero (the data in items never sits on a half but for .5)."""
    q = Decimal(1).scaleb(-digits)
    return float(Decimal(repr(float(x))).quantize(q, rounding=ROUND_HALF_UP))


def concat(a, b):
    """a || b: NULL if either is NULL, numbers become text."""
    if a is None or b is None:
        return None
    return show(a) + show(b)


def substr(s: str, start: int, length: int | None = None) -> str:
    """SUBSTR(s, start[, length]): 1-based; a negative start counts from the end (kept within the string here)."""
    assert start != 0 and abs(start) <= len(s), "keep SUBSTR inside the string"
    i = start - 1 if start > 0 else len(s) + start
    return s[i:] if length is None else s[i:i + length]


def instr(s: str, t: str) -> int:
    """INSTR(s, t): the 1-based position of the first t in s, 0 when absent."""
    for i in range(len(s) - len(t) + 1):
        if s[i:i + len(t)] == t:
            return i + 1
    return 0


def type_of(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool) or isinstance(v, int):
        return "integer"
    if isinstance(v, float):
        return "real"
    return "text"


def coalesce(*vals):
    for v in vals:
        if v is not None:
            return v
    return None


def nullif(a, b):
    return None if (a is not None and b is not None and a == b) else a
