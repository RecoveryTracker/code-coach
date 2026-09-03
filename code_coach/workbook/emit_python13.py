"""Python-only shapes, thirteenth batch: more protocols, and waiting properly.

Four more dunders, which between them are most of what makes a class
feel like a built-in type: __call__ so an object can be called, then
__getitem__ and __len__ so it can be indexed and measured, then a
property with a setter so assignment can run code. Plus functools.wraps,
which repairs the decorator page 117 quietly broke.

Then two shelves worth knowing - heapq for the few smallest and bisect
for keeping a list sorted - total_ordering, a comprehension with two
fors, and finally async and await, where the whole idea is that waiting
should not stop everything else.

Determinism: the async pages collect their results and print them
afterwards, so nothing depends on which coroutine got there first.
"""

from __future__ import annotations

import bisect
import heapq
import re

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("wraps_use", "a decorator that does not lose the name"),
    Shape("call_dunder", "an object you can call like a function"),
    Shape("getitem_len", "a class that indexes and measures"),
    Shape("property_setter", "assignment that runs code"),
    Shape("heapq_use", "the few smallest, without sorting it all"),
    Shape("bisect_use", "putting something in and keeping it sorted"),
    Shape("total_ordering", "one comparison, and the rest for free"),
    Shape("nested_comp", "a comprehension with two fors"),
    Shape("async_basic", "async and await, in order"),
    Shape("async_gather", "several at once, results in order"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(repr(n) for n in items)


def _selfify(expr: str, field: str) -> str:
    """`n + amount` becomes `n + self.amount`.

    The expression is stored in terms of the field's own name so the same
    string can be evaluated for the expected output, where there is no
    self to reach through.
    """
    return re.sub(rf"\b{re.escape(field)}\b", f"self.{field}", expr)


def _python(shape: str, a: dict) -> str:
    if shape == "wraps_use":
        return _lines(
            "from functools import wraps",
            "",
            "",
            "def louder(func):",
            "    @wraps(func)",
            "    def wrapper(n):",
            f"        return {a['wrap']}",
            "    return wrapper",
            "",
            "",
            "@louder",
            f"def {a['name']}(n):",
            f"    return {a['expr']}",
            "",
            "",
            f"print({a['name']}({a['call']!r}))",
            f"print({a['name']}.__name__)",
        )
    if shape == "call_dunder":
        return _lines(
            f"class {a['cls']}:",
            f"    def __init__(self, {a['field']}):",
            f"        self.{a['field']} = {a['field']}",
            "",
            "    def __call__(self, n):",
            f"        return {_selfify(a['expr'], a['field'])}",
            "",
            "",
            f"thing = {a['cls']}({a['held']!r})",
            f"print(thing({a['call']!r}))",
            "print(callable(thing))",
        )
    if shape == "getitem_len":
        return _lines(
            f"class {a['cls']}:",
            "    def __init__(self, items):",
            "        self.items = items",
            "",
            "    def __len__(self):",
            "        return len(self.items)",
            "",
            "    def __getitem__(self, position):",
            "        return self.items[position]",
            "",
            "",
            f"thing = {a['cls']}([" + _nums(a["items"]) + "])",
            "print(len(thing))",
            "print(thing[0])",
            "print(thing[-1])",
            "print(list(thing))",
        )
    if shape == "property_setter":
        return _lines(
            f"class {a['cls']}:",
            "    def __init__(self, name):",
            "        self._name = name",
            "",
            "    @property",
            "    def name(self):",
            "        return self._name",
            "",
            "    @name.setter",
            "    def name(self, value):",
            "        self._name = value.strip().title()",
            "",
            "",
            f"thing = {a['cls']}({_q(a['first'])})",
            "print(thing.name)",
            f"thing.name = {_q(a['second'])}",
            "print(thing.name)",
        )
    if shape == "heapq_use":
        return _lines(
            "import heapq",
            "",
            "numbers = [" + _nums(a["items"]) + "]",
            "",
            f"print(heapq.nsmallest({a['small']}, numbers))",
            f"print(heapq.nlargest({a['large']}, numbers))",
        )
    if shape == "bisect_use":
        return _lines(
            "import bisect",
            "",
            "numbers = [" + _nums(a["items"]) + "]",
            f"bisect.insort(numbers, {a['added']!r})",
            "",
            "print(numbers)",
            f"print(bisect.bisect_left(numbers, {a['find']!r}))",
        )
    if shape == "total_ordering":
        return _lines(
            "from functools import total_ordering",
            "",
            "",
            "@total_ordering",
            f"class {a['cls']}:",
            f"    def __init__(self, {a['field']}):",
            f"        self.{a['field']} = {a['field']}",
            "",
            "    def __eq__(self, other):",
            f"        return self.{a['field']} == other.{a['field']}",
            "",
            "    def __lt__(self, other):",
            f"        return self.{a['field']} < other.{a['field']}",
            "",
            "",
            f"first = {a['cls']}({a['values'][0]!r})",
            f"second = {a['cls']}({a['values'][1]!r})",
            "print(first < second)",
            "print(first >= second)",
            "print(first != second)",
        )
    if shape == "nested_comp":
        rows = ", ".join("[" + _nums(r) + "]" for r in a["rows"])
        return _lines(
            "rows = [" + rows + "]",
            "flat = [n for row in rows for n in row]",
            "",
            "print(flat)",
            "print(sum(flat))",
        )
    if shape == "async_basic":
        return _lines(
            "import asyncio",
            "",
            "",
            "async def work(n):",
            f"    return {a['expr']}",
            "",
            "",
            "async def main():",
            f"    first = await work({a['values'][0]!r})",
            f"    second = await work({a['values'][1]!r})",
            "    print(first)",
            "    print(second)",
            "",
            "",
            "asyncio.run(main())",
        )
    if shape == "async_gather":
        calls = ", ".join(f"work({n!r})" for n in a["values"])
        return _lines(
            "import asyncio",
            "",
            "",
            "async def work(n):",
            f"    return {a['expr']}",
            "",
            "",
            "async def main():",
            f"    results = await asyncio.gather({calls})",
            "    print(results)",
            "",
            "",
            "asyncio.run(main())",
        )
    raise KeyError(shape)


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "python":
        return None
    return _python(shape, args)


# ── What each of them prints ─────────────────────────────────

_TOOLS = {"sum": sum, "len": len, "max": max, "min": min, "abs": abs}


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "wraps_use":
        inner = value(a["expr"], {"n": a["call"], **_TOOLS})
        wrapped = value(
            a["wrap"],
            {"func": lambda n: value(a["expr"], {"n": n, **_TOOLS}),
             "n": a["call"], **_TOOLS},
        )
        lines = [str(wrapped), a["name"]]
        if inner == wrapped:
            # Then the decorator changed nothing and the page shows nothing.
            raise ValueError("the wrapper must change the answer")
    elif shape == "call_dunder":
        held = {a["field"]: a["held"], "n": a["call"]}
        lines = [str(value(a["expr"], {**held, **_TOOLS})), "True"]
    elif shape == "getitem_len":
        items = list(a["items"])
        lines = [
            str(len(items)),
            str(items[0]),
            str(items[-1]),
            repr(items),
        ]
    elif shape == "property_setter":
        lines = [a["first"], a["second"].strip().title()]
    elif shape == "heapq_use":
        lines = [
            repr(heapq.nsmallest(a["small"], a["items"])),
            repr(heapq.nlargest(a["large"], a["items"])),
        ]
    elif shape == "bisect_use":
        items = list(a["items"])
        bisect.insort(items, a["added"])
        lines = [repr(items), str(bisect.bisect_left(items, a["find"]))]
    elif shape == "total_ordering":
        first, second = a["values"]
        lines = [
            str(first < second),
            str(first >= second),
            str(first != second),
        ]
    elif shape == "nested_comp":
        flat = [n for row in a["rows"] for n in row]
        lines = [repr(flat), str(sum(flat))]
    elif shape == "async_basic":
        lines = [
            str(value(a["expr"], {"n": n, **_TOOLS})) for n in a["values"]
        ]
    elif shape == "async_gather":
        got = [value(a["expr"], {"n": n, **_TOOLS}) for n in a["values"]]
        lines = [repr(got)]
    else:
        raise KeyError(shape)
    return NL.join(lines)
