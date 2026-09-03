"""Python-only shapes, fifteenth batch: more surprises, and the last few tools.

Three more things that are not bugs but read like them: round does not
round half up, sort returns None, and lstrip takes a set of characters
rather than a prefix. Each one costs somebody an afternoon roughly once.

Then nonlocal and global, dict views that keep up with the dict,
suppress, a database that lives in memory, match with real patterns
rather than the literals of page 169, and a generic class.

Determinism: every query orders its rows explicitly, and nothing here
depends on dict ordering beyond insertion order, which is guaranteed.
"""

from __future__ import annotations

import sqlite3

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("round_bankers", "rounding that does not go the way you learnt"),
    Shape("divmod_base", "both halves of a division, and other bases"),
    Shape("sort_vs_sorted", "sorting in place against making a sorted one"),
    Shape("nonlocal_global", "reaching out to a name defined further up"),
    Shape("dict_views", "a view that keeps up with the dict"),
    Shape("strip_affix", "taking a prefix off, and the trap next to it"),
    Shape("suppress_use", "an error you have decided not to care about"),
    Shape("sqlite_memory", "a database with no file"),
    Shape("match_structure", "matching the shape, not just the value"),
    Shape("generic_class", "a class that says what it holds"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(repr(n) for n in items)


def _python(shape: str, a: dict) -> str:
    if shape == "round_bankers":
        shows = []
        for number, digits in a["values"]:
            if digits is None:
                shows.append(f"print(round({number!r}))")
            else:
                shows.append(f"print(round({number!r}, {digits}))")
        return _lines(*shows)
    if shape == "divmod_base":
        return _lines(
            f"print(divmod({a['top']!r}, {a['bottom']!r}))",
            f"print(int({_q(a['hex'])}, 16))",
            f"print(int({_q(a['binary'])}, 2))",
        )
    if shape == "sort_vs_sorted":
        return _lines(
            "numbers = [" + _nums(a["items"]) + "]",
            "made = sorted(numbers)",
            "",
            "print(numbers)",
            "print(made)",
            "",
            "numbers.sort()",
            "print(numbers)",
            "print(numbers.sort())",
        )
    if shape == "nonlocal_global":
        return _lines(
            f"{a['counter']} = 0",
            "",
            "",
            "def outer():",
            "    total = 0",
            "",
            "    def inner(n):",
            "        nonlocal total",
            "        total += n",
            "",
            *[f"    inner({n!r})" for n in a["added"]],
            "    return total",
            "",
            "",
            "def bump():",
            f"    global {a['counter']}",
            f"    {a['counter']} += 1",
            "",
            "",
            "print(outer())",
            *["bump()" for _ in range(a["bumps"])],
            f"print({a['counter']})",
        )
    if shape == "dict_views":
        pairs = ", ".join(f"{_q(k)}: {v!r}" for k, v in a["pairs"])
        return _lines(
            "prices = {" + pairs + "}",
            "keys = prices.keys()",
            "",
            "print(sorted(keys))",
            f"prices[{_q(a['added'][0])}] = {a['added'][1]!r}",
            "print(sorted(keys))",
            "print(len(keys))",
        )
    if shape == "strip_affix":
        return _lines(
            "name = " + _q(a["name"]),
            "",
            f"print(name.removeprefix({_q(a['prefix'])}))",
            f"print(name.removesuffix({_q(a['suffix'])}))",
            f"print(name.lstrip({_q(a['prefix'])}))",
        )
    if shape == "suppress_use":
        pairs = ", ".join(f"{_q(k)}: {v!r}" for k, v in a["pairs"])
        return _lines(
            "from contextlib import suppress",
            "",
            "prices = {" + pairs + "}",
            "",
            "with suppress(KeyError):",
            f"    print(prices[{_q(a['pairs'][0][0])}])",
            f"    print(prices[{_q(a['missing'])}])",
            f"    print({_q(a['unreached'])})",
            "",
            f"print({_q(a['after'])})",
        )
    if shape == "sqlite_memory":
        rows = ", ".join(
            "(" + _q(n) + ", " + repr(v) + ")" for n, v in a["rows"]
        )
        return _lines(
            "import sqlite3",
            "",
            'db = sqlite3.connect(":memory:")',
            f'db.execute("CREATE TABLE {a["table"]} '
            f'(name TEXT, {a["column"]} INTEGER)")',
            f'db.executemany("INSERT INTO {a["table"]} VALUES (?, ?)", '
            f"[{rows}])",
            "",
            f'for name, {a["column"]} in db.execute(',
            f'    "SELECT name, {a["column"]} FROM {a["table"]} '
            f'ORDER BY name"',
            "):",
            f'    print(name, {a["column"]})',
        )
    if shape == "match_structure":
        return _lines(
            f"def {a['func']}(data):",
            "    match data:",
            f'        case {{"kind": {_q(a["kind"])}, '
            f'{_q(a["key"])}: found}}:',
            f'            return f"{a["kind"]} {{found}}"',
            "        case [first, second]:",
            '            return f"pair {first} {second}"',
            "        case _:",
            f"            return {_q(a['fallback'])}",
            "",
            "",
            f'print({a["func"]}({{"kind": {_q(a["kind"])}, '
            f"{_q(a['key'])}: {a['found']!r}}}))",
            f"print({a['func']}([{_nums(a['pair'])}]))",
            f"print({a['func']}({a['other']!r}))",
        )
    if shape == "generic_class":
        return _lines(
            "from typing import Generic, TypeVar",
            "",
            'T = TypeVar("T")',
            "",
            "",
            f"class {a['cls']}(Generic[T]):",
            "    def __init__(self, item: T) -> None:",
            "        self.item = item",
            "",
            f"    def {a['method']}(self) -> T:",
            "        return self.item",
            "",
            "",
            f"print({a['cls']}({a['number']!r}).{a['method']}())",
            f"print({a['cls']}({_q(a['word'])}).{a['method']}())",
        )
    raise KeyError(shape)


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "python":
        return None
    return _python(shape, args)


# ── What each of them prints ─────────────────────────────────


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "round_bankers":
        for number, digits in a["values"]:
            lines.append(
                repr(round(number) if digits is None else round(number, digits))
            )
    elif shape == "divmod_base":
        lines = [
            repr(divmod(a["top"], a["bottom"])),
            str(int(a["hex"], 16)),
            str(int(a["binary"], 2)),
        ]
    elif shape == "sort_vs_sorted":
        items = list(a["items"])
        ordered = sorted(items)
        if items == ordered:
            # Then nothing moved and the page shows nothing.
            raise ValueError("the list must start unsorted")
        # sorted leaves the original alone; sort changes it and returns None.
        lines = [repr(items), repr(ordered), repr(ordered), "None"]
    elif shape == "nonlocal_global":
        lines = [str(sum(a["added"])), str(a["bumps"])]
    elif shape == "dict_views":
        held = dict(a["pairs"])
        before = sorted(held)
        held[a["added"][0]] = a["added"][1]
        after = sorted(held)
        if before == after:
            raise ValueError("the added key must be new")
        lines = [repr(before), repr(after), str(len(held))]
    elif shape == "strip_affix":
        name = a["name"]
        lines = [
            name.removeprefix(a["prefix"]),
            name.removesuffix(a["suffix"]),
            name.lstrip(a["prefix"]),
        ]
        if lines[0] == lines[2]:
            # The page exists to show lstrip doing something different.
            raise ValueError("lstrip must differ from removeprefix here")
    elif shape == "suppress_use":
        lines = [str(dict(a["pairs"])[a["pairs"][0][0]]), a["after"]]
    elif shape == "sqlite_memory":
        db = sqlite3.connect(":memory:")
        db.execute(f"CREATE TABLE {a['table']} (name TEXT, n INTEGER)")
        db.executemany(
            f"INSERT INTO {a['table']} VALUES (?, ?)", list(a["rows"])
        )
        lines = [
            f"{name} {n}"
            for name, n in db.execute(
                f"SELECT name, n FROM {a['table']} ORDER BY name"
            )
        ]
        db.close()
    elif shape == "match_structure":
        lines = [
            f"{a['kind']} {a['found']}",
            f"pair {a['pair'][0]} {a['pair'][1]}",
            a["fallback"],
        ]
    elif shape == "generic_class":
        lines = [str(a["number"]), a["word"]]
    else:
        raise KeyError(shape)
    return NL.join(lines)
