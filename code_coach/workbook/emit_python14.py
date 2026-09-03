"""Python-only shapes, fourteenth batch: the rest of itertools, and the
dataclass you did not know you had.

Five itertools pages, each one a loop you would otherwise write badly:
every combination of two lists, two lists of different lengths walked
together, an endless sequence cut short, a run taken from the front, and
consecutive pairs.

Then what a dataclass gives you beyond __init__ - asdict, astuple,
replace, ordering and __post_init__ - an Enum that numbers itself and
can carry a method, a generic function whose hint actually says
something, and a thread pool whose map hands results back in order.

Determinism: pool.map preserves input order regardless of which thread
finished first, and nothing here prints from inside a worker.
"""

from __future__ import annotations

import itertools

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("product_use", "every combination of two lists"),
    Shape("zip_longest_use", "two lists of different lengths, together"),
    Shape("islice_cycle", "an endless sequence, cut short"),
    Shape("takewhile_drop", "the run at the front, and the rest"),
    Shape("pairwise_use", "each item with the one after it"),
    Shape("dataclass_tools", "asdict, astuple and replace"),
    Shape("dataclass_order", "ordering, and work after __init__"),
    Shape("enum_auto", "an enum that numbers itself"),
    Shape("typevar_generic", "a hint that says same type in, same out"),
    Shape("threadpool_map", "several at once, in order"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(repr(n) for n in items)


def _words(items) -> str:
    return ", ".join(_q(w) for w in items)


def _python(shape: str, a: dict) -> str:
    if shape == "product_use":
        return _lines(
            "from itertools import product",
            "",
            "first = [" + _nums(a["first"]) + "]",
            "second = [" + _words(a["second"]) + "]",
            "",
            "print(list(product(first, second)))",
        )
    if shape == "zip_longest_use":
        return _lines(
            "from itertools import zip_longest",
            "",
            "first = [" + _nums(a["first"]) + "]",
            "second = [" + _nums(a["second"]) + "]",
            "",
            f"for a, b in zip_longest(first, second, fillvalue={a['fill']!r}):",
            "    print(a, b)",
        )
    if shape == "islice_cycle":
        return _lines(
            "from itertools import cycle, islice",
            "",
            "colours = [" + _words(a["items"]) + "]",
            "",
            f"for colour in islice(cycle(colours), {a['take']}):",
            "    print(colour)",
        )
    if shape == "takewhile_drop":
        return _lines(
            "from itertools import dropwhile, takewhile",
            "",
            "numbers = [" + _nums(a["items"]) + "]",
            "",
            f"print(list(takewhile(lambda n: {a['test']}, numbers)))",
            f"print(list(dropwhile(lambda n: {a['test']}, numbers)))",
        )
    if shape == "pairwise_use":
        return _lines(
            "from itertools import pairwise",
            "",
            "numbers = [" + _nums(a["items"]) + "]",
            "",
            "for first, second in pairwise(numbers):",
            "    print(second - first)",
        )
    if shape == "dataclass_tools":
        fields = [f"    {n}: {t}" for n, t in a["fields"]]
        made = ", ".join(repr(v) for v in a["values"])
        first_field = a["fields"][0][0]
        return _lines(
            "from dataclasses import asdict, astuple, dataclass, replace",
            "",
            "",
            "@dataclass",
            f"class {a['cls']}:",
            *fields,
            "",
            "",
            f"thing = {a['cls']}({made})",
            f"moved = replace(thing, {first_field}={a['changed']!r})",
            "",
            "print(asdict(thing))",
            "print(astuple(thing))",
            "print(moved)",
        )
    if shape == "dataclass_order":
        return _lines(
            "from dataclasses import dataclass",
            "",
            "",
            "@dataclass(order=True)",
            f"class {a['cls']}:",
            f"    {a['first_field']}: int",
            f"    {a['second_field']}: str",
            "",
            "    def __post_init__(self):",
            f"        self.{a['second_field']} = self.{a['second_field']}.title()",
            "",
            "",
            f"first = {a['cls']}({a['low'][0]!r}, {_q(a['low'][1])})",
            f"second = {a['cls']}({a['high'][0]!r}, {_q(a['high'][1])})",
            "",
            "print(first < second)",
            f"print(first.{a['second_field']})",
            f"print(sorted([second, first])[0].{a['second_field']})",
        )
    if shape == "enum_auto":
        members = [f"    {n} = auto()" for n in a["members"]]
        return _lines(
            "from enum import Enum, auto",
            "",
            "",
            f"class {a['cls']}(Enum):",
            *members,
            "",
            f"    def {a['method']}(self):",
            "        return self.name.title()",
            "",
            "",
            f"print({a['cls']}.{a['members'][0]}.value)",
            f"print({a['cls']}.{a['members'][-1]}.value)",
            f"print({a['cls']}.{a['members'][1]}.{a['method']}())",
        )
    if shape == "typevar_generic":
        return _lines(
            "from typing import TypeVar",
            "",
            'T = TypeVar("T")',
            "",
            "",
            f"def {a['name']}(items: list[T]) -> T:",
            "    return items[0]",
            "",
            "",
            f"print({a['name']}([" + _nums(a["numbers"]) + "]))",
            f"print({a['name']}([" + _words(a["words"]) + "]))",
        )
    if shape == "threadpool_map":
        return _lines(
            "from concurrent.futures import ThreadPoolExecutor",
            "",
            "",
            "def work(n):",
            f"    return {a['expr']}",
            "",
            "",
            f"with ThreadPoolExecutor(max_workers={a['workers']}) as pool:",
            "    results = list(pool.map(work, [" + _nums(a["items"]) + "]))",
            "",
            "print(results)",
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
    if shape == "product_use":
        lines = [repr(list(itertools.product(a["first"], a["second"])))]
    elif shape == "zip_longest_use":
        pairs = itertools.zip_longest(
            a["first"], a["second"], fillvalue=a["fill"]
        )
        lines = [f"{x} {y}" for x, y in pairs]
    elif shape == "islice_cycle":
        cycled = itertools.islice(itertools.cycle(a["items"]), a["take"])
        lines = list(cycled)
    elif shape == "takewhile_drop":
        def test(n):
            return value(a["test"], {"n": n, **_TOOLS})

        taken = list(itertools.takewhile(test, a["items"]))
        dropped = list(itertools.dropwhile(test, a["items"]))
        if not taken or len(taken) == len(a["items"]):
            # The page is about stopping partway; a run that takes all or
            # nothing shows nothing.
            raise ValueError("takewhile must stop partway through")
        lines = [repr(taken), repr(dropped)]
    elif shape == "pairwise_use":
        items = list(a["items"])
        lines = [str(b - x) for x, b in itertools.pairwise(items)]
    elif shape == "dataclass_tools":
        names = [n for n, _ in a["fields"]]
        held = dict(zip(names, a["values"]))
        moved = dict(held)
        moved[names[0]] = a["changed"]
        inside = ", ".join(f"{n}={moved[n]!r}" for n in names)
        lines = [
            repr(held),
            repr(tuple(a["values"])),
            f"{a['cls']}({inside})",
        ]
    elif shape == "dataclass_order":
        lines = ["True", a["low"][1].title(), a["low"][1].title()]
        if a["low"][0] >= a["high"][0]:
            raise ValueError("the first card must sort below the second")
    elif shape == "enum_auto":
        # auto() starts at 1 and counts up in the order written.
        lines = [
            "1",
            str(len(a["members"])),
            a["members"][1].title(),
        ]
    elif shape == "typevar_generic":
        lines = [str(a["numbers"][0]), a["words"][0]]
    elif shape == "threadpool_map":
        lines = [
            repr([value(a["expr"], {"n": n, **_TOOLS}) for n in a["items"]])
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
