"""Python-only shapes, twelfth batch: numbers that lie, and the shapes of a design.

The first pages are about arithmetic not doing what school promised -
floats that miss by a hair, Decimal for anything that is money, and the
parts of math worth knowing. Then random, which is only useful once you
understand that seeding it makes it repeat.

The rest is design: a base class that refuses to be built, a Protocol
that names a shape without demanding inheritance, a context manager
written as one decorated function, ordering by two things in opposite
directions, and the method resolution order that decides which parent
wins.

Determinism: the float pages are checked to actually miss - the emitter
raises if a sum happens to come out exact - and random is always seeded.
"""

from __future__ import annotations

import math
import random
from decimal import Decimal

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("float_trap", "arithmetic that misses by a hair"),
    Shape("decimal_money", "the numbers you use for money"),
    Shape("math_basics", "floor, ceil and the two square roots"),
    Shape("random_seed", "random numbers that repeat on purpose"),
    Shape("csv_read", "a table that arrived as text"),
    Shape("abstract_base", "a class that refuses to be built"),
    Shape("protocol_shape", "a shape named without inheritance"),
    Shape("contextmanager_fn", "a context manager as one function"),
    Shape("sort_two_ways", "ordering by two things, opposite directions"),
    Shape("mro_order", "which parent wins"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(repr(n) for n in items)


def _python(shape: str, a: dict) -> str:
    if shape == "float_trap":
        return _lines(
            "from math import isclose",
            "",
            f"first = {a['first']!r}",
            f"second = {a['second']!r}",
            "",
            "print(first + second)",
            f"print(first + second == {a['target']!r})",
            f"print(isclose(first + second, {a['target']!r}))",
        )
    if shape == "decimal_money":
        return _lines(
            "from decimal import Decimal",
            "",
            f"first = Decimal({_q(a['first'])})",
            f"second = Decimal({_q(a['second'])})",
            "",
            "print(first + second)",
            f"print(first + second == Decimal({_q(a['target'])}))",
            f"print(float({a['first']!r}) + float({a['second']!r}) "
            f"== {float(a['target'])!r})",
        )
    if shape == "math_basics":
        return _lines(
            "import math",
            "",
            f"value = {a['value']!r}",
            f"whole = {a['whole']!r}",
            "",
            "print(math.floor(value))",
            "print(math.ceil(value))",
            "print(math.isqrt(whole))",
        )
    if shape == "random_seed":
        return _lines(
            "import random",
            "",
            f"random.seed({a['seed']!r})",
            f"first = [random.randint(1, {a['top']}) for _ in range({a['many']})]",
            "",
            f"random.seed({a['seed']!r})",
            f"second = [random.randint(1, {a['top']}) for _ in range({a['many']})]",
            "",
            "print(first)",
            "print(first == second)",
        )
    if shape == "csv_read":
        rows = "".join(
            ",".join(str(cell) for cell in row) + "\n" for row in a["rows"]
        )
        return _lines(
            "import csv",
            "import io",
            "",
            f"text = {rows!r}",
            "reader = csv.DictReader(io.StringIO(text))",
            "",
            "for row in reader:",
            f"    print(row[{_q(a['rows'][0][0])}], row[{_q(a['rows'][0][1])}])",
        )
    if shape == "abstract_base":
        return _lines(
            "from abc import ABC, abstractmethod",
            "",
            "",
            f"class {a['base']}(ABC):",
            "    @abstractmethod",
            f"    def {a['method']}(self):",
            "        ...",
            "",
            "",
            f"class {a['sub']}({a['base']}):",
            f"    def {a['method']}(self):",
            f"        return {_q(a['answer'])}",
            "",
            "",
            f"print({a['sub']}().{a['method']}())",
            "try:",
            f"    {a['base']}()",
            "except TypeError:",
            f"    print({_q(a['refused'])})",
        )
    if shape == "protocol_shape":
        return _lines(
            "from typing import Protocol",
            "",
            "",
            f"class {a['proto']}(Protocol):",
            f"    def {a['method']}(self) -> str: ...",
            "",
            "",
            f"class {a['first']}:",
            f"    def {a['method']}(self) -> str:",
            f"        return {_q(a['answers'][0])}",
            "",
            "",
            f"class {a['second']}:",
            f"    def {a['method']}(self) -> str:",
            f"        return {_q(a['answers'][1])}",
            "",
            "",
            f"def speak(thing: {a['proto']}) -> None:",
            f"    print(thing.{a['method']}())",
            "",
            "",
            f"speak({a['first']}())",
            f"speak({a['second']}())",
        )
    if shape == "contextmanager_fn":
        return _lines(
            "from contextlib import contextmanager",
            "",
            "",
            "@contextmanager",
            f"def {a['name']}():",
            f"    print({_q(a['opening'])})",
            "    try:",
            "        yield",
            "    finally:",
            f"        print({_q(a['closing'])})",
            "",
            "",
            f"with {a['name']}():",
            f"    print({_q(a['inside'])})",
        )
    if shape == "sort_two_ways":
        rows = ", ".join(
            "(" + _q(n) + ", " + repr(v) + ")" for n, v in a["rows"]
        )
        return _lines(
            "rows = [" + rows + "]",
            "",
            "for name, score in sorted(rows, key=lambda r: (-r[1], r[0])):",
            "    print(name, score)",
        )
    if shape == "mro_order":
        return _lines(
            f"class {a['top']}:",
            "    pass",
            "",
            "",
            f"class {a['left']}({a['top']}):",
            "    pass",
            "",
            "",
            f"class {a['right']}({a['top']}):",
            "    pass",
            "",
            "",
            f"class {a['bottom']}({a['left']}, {a['right']}):",
            "    pass",
            "",
            "",
            f"print([cls.__name__ for cls in {a['bottom']}.__mro__])",
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
    if shape == "float_trap":
        total = a["first"] + a["second"]
        if total == a["target"]:
            # The page exists to show the miss. If a pair lands exactly,
            # it teaches the opposite of what it says.
            raise ValueError(
                f"{a['first']} + {a['second']} is exactly {a['target']}"
            )
        lines = [
            repr(total),
            "False",
            str(math.isclose(total, a["target"])),
        ]
    elif shape == "decimal_money":
        total = Decimal(a["first"]) + Decimal(a["second"])
        floats_agree = float(a["first"]) + float(a["second"]) == float(
            a["target"]
        )
        lines = [
            str(total),
            str(total == Decimal(a["target"])),
            str(floats_agree),
        ]
    elif shape == "math_basics":
        lines = [
            str(math.floor(a["value"])),
            str(math.ceil(a["value"])),
            str(math.isqrt(a["whole"])),
        ]
    elif shape == "random_seed":
        random.seed(a["seed"])
        drawn = [random.randint(1, a["top"]) for _ in range(a["many"])]
        lines = [repr(drawn), "True"]
    elif shape == "csv_read":
        header = a["rows"][0]
        lines = [f"{row[0]} {row[1]}" for row in a["rows"][1:]]
        if len(header) < 2:
            raise ValueError("csv needs at least two columns")
    elif shape == "abstract_base":
        lines = [a["answer"], a["refused"]]
    elif shape == "protocol_shape":
        lines = list(a["answers"])
    elif shape == "contextmanager_fn":
        lines = [a["opening"], a["inside"], a["closing"]]
    elif shape == "sort_two_ways":
        ordered = sorted(a["rows"], key=lambda r: (-r[1], r[0]))
        lines = [f"{n} {v}" for n, v in ordered]
    elif shape == "mro_order":
        lines = [
            repr([a["bottom"], a["left"], a["right"], a["top"], "object"])
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
