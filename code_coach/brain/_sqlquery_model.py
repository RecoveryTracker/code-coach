"""Extra hand-built SQL models for the SQL deeper queries pack (`pack_sqlquery.py`): set operations, LIKE with ESCAPE and
GLOB, SQLite's date functions on fixed dates, multi-key ordering with explicit NULL placement, recursive series.

Like `_sql_model.py`, nothing here asks SQLite anything: tests/sql_oracle.py runs every item in a fresh in-memory SQLite and
compares, so a wrong model here is a failing test (never "fix" the oracle).
"""

from __future__ import annotations

import datetime as dt
from typing import Any, Callable

from ._sql_model import Tbl, show  # noqa: F401  (re-exported for the template files)


# ── Set operations (rows are tuples; for UNION / INTERSECT / EXCEPT two NULLs ARE the same row) ──

def u_all(a: list[tuple], b: list[tuple]) -> list[tuple]:
    """a UNION ALL b: every row of both."""
    return list(a) + list(b)


def distinct(rows: list[tuple]) -> list[tuple]:
    """The different rows (NULL equals NULL here), in order of first appearance."""
    out: list[tuple] = []
    for r in rows:
        if r not in out:
            out.append(r)
    return out


def u(a: list[tuple], b: list[tuple]) -> list[tuple]:
    """a UNION b: the different rows of both."""
    return distinct(list(a) + list(b))


def inter(a: list[tuple], b: list[tuple]) -> list[tuple]:
    """a INTERSECT b: the different rows that are in both."""
    return [r for r in distinct(a) if r in b]


def exc(a: list[tuple], b: list[tuple]) -> list[tuple]:
    """a EXCEPT b: the different rows of a that are not in b."""
    return [r for r in distinct(a) if r not in b]


def col1(values: list) -> list[tuple]:
    """A column of values as one-column rows."""
    return [(v,) for v in values]


def sort_rows(rows: list[tuple]) -> list[tuple]:
    """ORDER BY every column ascending, NULL smallest (the order a compound SELECT is printed in is not promised: items
    that print rows always add an ORDER BY)."""
    return sorted(rows, key=lambda r: tuple((v is not None, v if v is not None else 0) for v in r))


# ── Ordering with explicit NULL placement ───────────────────────────────

def order2(rows: list, *keys: tuple) -> list:
    """ORDER BY with several keys. Each key is (fn, desc) or (fn, desc, nulls) with nulls "first" / "last"; by default NULLs
    are the smallest value (first when ascending, last when descending). Ties keep the table's order (items avoid
    depending on that)."""
    out = list(rows)
    for key in reversed(keys):
        fn, desc = key[0], key[1]
        nulls = key[2] if len(key) > 2 else ("last" if desc else "first")
        if desc:
            out.sort(key=lambda r, fn=fn, nulls=nulls: _desc_key(fn(r), nulls))
        else:
            out.sort(key=lambda r, fn=fn, nulls=nulls: _asc_key(fn(r), nulls))
    return out


def _asc_key(v: Any, nulls: str):
    if v is None:
        return (0, 0) if nulls == "first" else (2, 0)
    return (1, v)


class _Rev:
    """A value that sorts in reverse (for descending order of any comparable)."""

    def __init__(self, v: Any) -> None:
        self.v = v

    def __lt__(self, other: "_Rev") -> bool:
        return other.v < self.v

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _Rev) and self.v == other.v


def _desc_key(v: Any, nulls: str):
    if v is None:
        return (0, 0) if nulls == "first" else (2, 0)
    return (1, _Rev(v))


def dense_ranks(values: list, desc: bool = False) -> list[int]:
    """DENSE_RANK() for each value (ties share a rank, no gaps)."""
    order = sorted(set(values), reverse=desc)
    return [order.index(v) + 1 for v in values]


def ranks(values: list, desc: bool = False) -> list[int]:
    """RANK() for each value (ties share a rank, then it skips)."""
    return [1 + sum(1 for w in values if (w > v if desc else w < v)) for v in values]


# ── Pattern matching ────────────────────────────────────────────────────

def like_esc(s: str | None, pattern: str, esc: str) -> bool | None:
    """s LIKE pattern ESCAPE esc: `%`, `_`, ASCII case ignored; esc makes the next character a plain one."""
    if s is None:
        return None
    text = s.lower()
    toks: list[tuple[str, str]] = []
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if c == esc and i + 1 < len(pattern):
            toks.append(("lit", pattern[i + 1].lower()))
            i += 2
            continue
        toks.append(("any" if c == "%" else "one" if c == "_" else "lit", c.lower()))
        i += 1

    def match(ti: int, pi: int) -> bool:
        if pi == len(toks):
            return ti == len(text)
        kind, c = toks[pi]
        if kind == "any":
            return any(match(k, pi + 1) for k in range(ti, len(text) + 1))
        if ti < len(text) and (kind == "one" or c == text[ti]):
            return match(ti + 1, pi + 1)
        return False

    return match(0, 0)


def glob(s: str | None, pattern: str) -> bool | None:
    """s GLOB pattern: `*` any run, `?` one character, `[a-c]` / `[xyz]` a set, `[^a-c]` not in the set; CASE-SENSITIVE."""
    if s is None:
        return None

    def parse(p: str) -> list[tuple]:
        toks, i = [], 0
        while i < len(p):
            c = p[i]
            if c == "*":
                toks.append(("any",))
            elif c == "?":
                toks.append(("one",))
            elif c == "[":
                j = p.index("]", i + 1)
                body = p[i + 1:j]
                neg = body.startswith("^")
                if neg:
                    body = body[1:]
                chars: set[str] = set()
                k = 0
                while k < len(body):
                    if k + 2 < len(body) and body[k + 1] == "-":
                        chars.update(chr(x) for x in range(ord(body[k]), ord(body[k + 2]) + 1))
                        k += 3
                    else:
                        chars.add(body[k])
                        k += 1
                toks.append(("set", neg, chars))
                i = j
            else:
                toks.append(("lit", c))
            i += 1
        return toks

    toks = parse(pattern)

    def match(ti: int, pi: int) -> bool:
        if pi == len(toks):
            return ti == len(s)
        t = toks[pi]
        if t[0] == "any":
            return any(match(k, pi + 1) for k in range(ti, len(s) + 1))
        if ti >= len(s):
            return False
        ch = s[ti]
        if t[0] == "one" or (t[0] == "lit" and t[1] == ch) or (t[0] == "set" and ((ch in t[2]) != t[1])):
            return match(ti + 1, pi + 1)
        return False

    return match(0, 0)


# ── Dates (fixed literals only; SQLite's date(), strftime() and julianday()) ────────

def D(text: str) -> dt.date:
    return dt.date.fromisoformat(text)


def iso(d: dt.date) -> str:
    return d.isoformat()


def add_days(d: dt.date, n: int) -> dt.date:
    return d + dt.timedelta(days=n)


def add_months(d: dt.date, n: int) -> dt.date:
    """date(d, 'N months'): the month moves, the day number stays, and a day that does not exist overflows into the next
    month (2024-01-31 + 1 month is 2024-02-31, which SQLite normalizes to 2024-03-02)."""
    total = d.year * 12 + (d.month - 1) + n
    y, m = divmod(total, 12)
    return dt.date(y, m + 1, 1) + dt.timedelta(days=d.day - 1)


def add_years(d: dt.date, n: int) -> dt.date:
    """date(d, 'N years') is 12*N months (so 2024-02-29 + 1 year overflows to 2025-03-01)."""
    return add_months(d, 12 * n)


def start_of_month(d: dt.date) -> dt.date:
    return d.replace(day=1)


def start_of_year(d: dt.date) -> dt.date:
    return d.replace(month=1, day=1)


def weekday_w(d: dt.date) -> int:
    """strftime('%w'): 0 is Sunday ... 6 is Saturday."""
    return (d.weekday() + 1) % 7


def next_weekday(d: dt.date, w: int) -> dt.date:
    """date(d, 'weekday N'): the same day when it already is weekday N, otherwise the next one."""
    return d + dt.timedelta(days=(w - weekday_w(d)) % 7)


def day_of_year(d: dt.date) -> int:
    return d.timetuple().tm_yday


def week_of_year(d: dt.date) -> int:
    """strftime('%W'): week 00-53, weeks start on Monday, days before the first Monday are week 00."""
    return int(d.strftime("%W"))


def days_between(a: dt.date, b: dt.date) -> int:
    """julianday(b) - julianday(a), as a whole number of days."""
    return (b - a).days


def last_day_of_month(d: dt.date) -> dt.date:
    """date(d, 'start of month', '+1 month', '-1 day')."""
    return add_days(add_months(start_of_month(d), 1), -1)


def rand_date(rng, lo: str = "2023-01-01", hi: str = "2025-12-31") -> dt.date:
    a, b = D(lo), D(hi)
    return a + dt.timedelta(days=rng.randint(0, (b - a).days))


# ── Recursion ───────────────────────────────────────────────────────────

def recursive(seed: Any, step: Callable[[Any], Any | None]) -> list:
    """What a recursive CTE builds: the seed, then each step of the last row, until the step gives None (a WHERE that fails)."""
    out = [seed]
    while True:
        nxt = step(out[-1])
        if nxt is None:
            return out
        out.append(nxt)
