"""Python-only shapes, eleventh batch: checking your work, and the fixes.

Two pages on assert and on writing a test you call yourself, which is
where most people's code stops being hopeful and starts being checked.

Then the fixes for things earlier pages showed going wrong: deepcopy for
the shallow copy of page 113, default_factory for the mutable default of
page 111, __repr__ for the half of page 105 that got left out, and
raise-from for an error that would otherwise lose where it came from.
Plus yield from, groupby with the sort it needs, bytes against text, and
zip's strict flag.

Determinism: nothing prints an exception's own message text where the
wording is Python's rather than ours - the messages here are all ours,
and where a type name is printed it is printed as a name.
"""

from __future__ import annotations

import copy
from itertools import groupby

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("assert_use", "a check that stops the program when it is wrong"),
    Shape("test_function", "a test you write and call yourself"),
    Shape("repr_vs_str", "the two ways an object turns into text"),
    Shape("deepcopy_use", "the copy that goes all the way down"),
    Shape("yield_from", "one generator handing on to another"),
    Shape("groupby_use", "runs of the same thing, once it is sorted"),
    Shape("frozen_dataclass", "a record that cannot be changed"),
    Shape("bytes_use", "text against the bytes it becomes"),
    Shape("zip_strict", "noticing that the lists were different lengths"),
    Shape("raise_from", "a new error that remembers the old one"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _lit(v) -> str:
    return _q(v) if isinstance(v, str) else repr(v)


def _nums(items) -> str:
    return ", ".join(repr(n) for n in items)


def _words(items) -> str:
    return ", ".join(_q(w) for w in items)


def _python(shape: str, a: dict) -> str:
    if shape == "assert_use":
        good_in = ", ".join(_lit(v) for v in a["good"][0])
        return _lines(
            f"def {a['func']}({', '.join(a['params'])}):",
            f"    return {a['expr']}",
            "",
            "",
            f"assert {a['func']}({good_in}) == {a['good'][1]!r}",
            f"print({_q(a['passed'])})",
            "",
            "try:",
            f"    assert {a['func']}({good_in}) == {a['wrong']!r}, "
            f"{_q(a['message'])}",
            "except AssertionError as problem:",
            "    print(problem)",
        )
    if shape == "test_function":
        checks = [
            f"    assert {a['func']}(" + ", ".join(_lit(v) for v in args) + f") == {want!r}"
            for args, want in a["cases"]
        ]
        return _lines(
            f"def {a['func']}({', '.join(a['params'])}):",
            f"    return {a['expr']}",
            "",
            "",
            f"def test_{a['func']}():",
            *checks,
            "",
            "",
            f"test_{a['func']}()",
            f"print({_q(a['passed'])})",
        )
    if shape == "repr_vs_str":
        names = [n for n, _ in a["fields"]]
        made = ", ".join(_lit(v) for v in a["values"])
        plain = a["shown"]
        detailed = (
            a["cls"] + "(" + ", ".join(f"{n}={{self.{n}!r}}" for n in names) + ")"
        )
        return _lines(
            f"class {a['cls']}:",
            f"    def __init__(self, {', '.join(names)}):",
            *[f"        self.{n} = {n}" for n in names],
            "",
            "    def __str__(self):",
            f'        return f"{plain}"',
            "",
            "    def __repr__(self):",
            f'        return f"{detailed}"',
            "",
            "",
            f"thing = {a['cls']}({made})",
            "print(thing)",
            "print(repr(thing))",
            "print([thing])",
        )
    if shape == "deepcopy_use":
        return _lines(
            "from copy import deepcopy",
            "",
            "inner = [" + _nums(a["inner"]) + "]",
            "outer = [inner]",
            "shallow = list(outer)",
            "deep = deepcopy(outer)",
            "",
            f"inner.append({a['added']!r})",
            "",
            "print(len(shallow[0]))",
            "print(len(deep[0]))",
        )
    if shape == "yield_from":
        return _lines(
            "def firsts():",
            *[f"    yield {n!r}" for n in a["first"]],
            "",
            "",
            "def seconds():",
            *[f"    yield {n!r}" for n in a["second"]],
            "",
            "",
            "def both():",
            "    yield from firsts()",
            "    yield from seconds()",
            "",
            "",
            "for n in both():",
            "    print(n)",
        )
    if shape == "groupby_use":
        return _lines(
            "from itertools import groupby",
            "",
            "words = [" + _words(a["words"]) + "]",
            "words.sort(key=lambda w: w[0])",
            "",
            "for letter, group in groupby(words, key=lambda w: w[0]):",
            "    print(letter, list(group))",
        )
    if shape == "frozen_dataclass":
        return _lines(
            "from dataclasses import dataclass, field",
            "",
            "",
            "@dataclass(frozen=True)",
            f"class {a['cls']}:",
            "    name: str",
            "    items: list = field(default_factory=list)",
            "",
            "",
            f"first = {a['cls']}({_q(a['names'][0])})",
            f"second = {a['cls']}({_q(a['names'][1])})",
            f"first.items.append({a['added']!r})",
            "",
            "print(len(first.items))",
            "print(len(second.items))",
            "",
            "try:",
            f"    first.name = {_q(a['names'][1])}",
            "except Exception as problem:",
            "    print(type(problem).__name__)",
        )
    if shape == "bytes_use":
        return _lines(
            "text = " + _q(a["text"]),
            'raw = text.encode("utf-8")',
            "",
            "print(len(text))",
            "print(len(raw))",
            'print(raw.decode("utf-8"))',
        )
    if shape == "zip_strict":
        return _lines(
            "first = [" + _nums(a["first"]) + "]",
            "second = [" + _nums(a["second"]) + "]",
            "",
            "try:",
            "    for a, b in zip(first, second, strict=True):",
            "        print(a, b)",
            "except ValueError:",
            f"    print({_q(a['complaint'])})",
        )
    if shape == "raise_from":
        return _lines(
            f"class {a['error']}(Exception):",
            "    pass",
            "",
            "",
            "def load(value):",
            "    try:",
            "        return int(value)",
            "    except ValueError as problem:",
            f"        raise {a['error']}({_q(a['message'])}) from problem",
            "",
            "",
            "for text in [" + _words(a["values"]) + "]:",
            "    try:",
            "        print(load(text))",
            f"    except {a['error']} as problem:",
            "        print(problem)",
            "        print(type(problem.__cause__).__name__)",
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
    if shape == "assert_use":
        # The passing assert says nothing; the failing one says our message.
        lines = [a["passed"], a["message"]]
    elif shape == "test_function":
        for got, want in a["cases"]:
            names = dict(zip(a["params"], got))
            if value(a["expr"], {**names, **_TOOLS}) != want:
                raise ValueError(f"test case is wrong: {got} -> {want}")
        lines = [a["passed"]]
    elif shape == "repr_vs_str":
        names = [n for n, _ in a["fields"]]
        held = dict(zip(names, a["values"]))
        plain = a["shown"]
        for n in names:
            plain = plain.replace("{self." + n + "}", str(held[n]))
        detailed = (
            a["cls"] + "(" + ", ".join(f"{n}={held[n]!r}" for n in names) + ")"
        )
        lines = [plain, detailed, "[" + detailed + "]"]
    elif shape == "deepcopy_use":
        grown = len(a["inner"]) + 1
        # The shallow copy shares the inner list; the deep one does not.
        lines = [str(grown), str(len(a["inner"]))]
    elif shape == "yield_from":
        lines = [str(n) for n in list(a["first"]) + list(a["second"])]
    elif shape == "groupby_use":
        words = sorted(a["words"], key=lambda w: w[0])
        for letter, group in groupby(words, key=lambda w: w[0]):
            lines.append(f"{letter} {list(group)!r}")
    elif shape == "frozen_dataclass":
        lines = ["1", "0", "FrozenInstanceError"]
    elif shape == "bytes_use":
        text = a["text"]
        lines = [str(len(text)), str(len(text.encode("utf-8"))), text]
    elif shape == "zip_strict":
        pairs = list(zip(a["first"], a["second"]))
        lines = [f"{x} {y}" for x, y in pairs]
        lines.append(a["complaint"])
    elif shape == "raise_from":
        for text in a["values"]:
            try:
                lines.append(str(int(text)))
            except ValueError:
                lines.append(a["message"])
                lines.append("ValueError")
    else:
        raise KeyError(shape)
    return NL.join(lines)


def check_shallow(inner, added) -> None:
    """Kept honest: the deep copy really does not see the append."""
    outer = [list(inner)]
    deep = copy.deepcopy(outer)
    outer[0].append(added)
    if len(deep[0]) != len(inner):
        raise AssertionError("deepcopy shared the inner list")
