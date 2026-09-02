"""Python-only shapes: the intermediate tier.

The beginner tier is written for seven languages, which is what keeps it
honest and also what caps how deep it can go — an exercise has to be one
question in all of them, so nothing can print a dict or a set or a boolean,
and nothing can use a feature the others have no answer for.

This tier drops that. One language means one emitter instead of seven, so
depth is cheap, and it means output can be whatever Python actually prints:
a list looks like a list, True looks like True. That is most of what makes
these worth writing.

JavaScript comes later, page by page, wherever a page has a real JavaScript
answer rather than a translated one. `Page.languages` already carries that,
so a page gains a language by naming it — nothing here has to change.

The determinism rule still applies, for a different reason: an exercise has
one expected output, so nothing may print something Python itself does not
order. Sets are sorted before printing; dicts are iterated only where
insertion order is the order (which it has been since 3.7) and never
otherwise.
"""

from __future__ import annotations

from dataclasses import dataclass

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("fmt_value", "telling an f-string how to print a number"),
    Shape("comprehension", "building a list in one expression"),
    Shape("comprehension_if", "a comprehension that leaves things out"),
    Shape("dict_get", "asking a dict for a key that may not be there"),
    Shape("dict_items", "walking a dict's keys and values together"),
    Shape("unique_sorted", "throwing duplicates away"),
    Shape("tuple_unpack", "pulling several values out at once"),
    Shape("enumerate_loop", "the position and the item, together"),
    Shape("zip_loop", "two lists walked as one"),
    Shape("sorted_key", "ordering by something other than the value"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


@dataclass(frozen=True)
class _Args:
    """Only here to make the emitter read as prose rather than a["..."]."""


def _nums(items) -> str:
    return "[" + ", ".join(repr(n) for n in items) + "]"


def _strs(items) -> str:
    return "[" + ", ".join(_q(w) for w in items) + "]"


def _dict(pairs) -> str:
    return "{" + ", ".join(f"{_q(k)}: {v!r}" for k, v in pairs) + "}"


def _python(shape: str, a: dict) -> str:
    if shape == "fmt_value":
        return (
            'print(f"'
            + a["label"]
            + ": {"
            + repr(a["value"])
            + ":"
            + a["spec"]
            + '}")'
        )
    if shape == "comprehension":
        return _lines(
            f"nums = [{a['expr']} for i in range({a['lo']}, {a['hi']} + 1)]",
            "print(nums)",
        )
    if shape == "comprehension_if":
        return _lines(
            f"nums = [{a['expr']} for i in range({a['lo']}, {a['hi']} + 1)"
            f" if {a['cond']}]",
            "print(nums)",
        )
    if shape == "dict_get":
        return _lines(
            f"table = {_dict(a['pairs'])}",
            f"print(table.get({_q(a['key'])}, {a['default']!r}))",
        )
    if shape == "dict_items":
        return _lines(
            f"table = {_dict(a['pairs'])}",
            "for key, value in table.items():",
            '    print(f"{key}: {value}")',
        )
    if shape == "unique_sorted":
        return _lines(
            f"nums = {_nums(a['items'])}",
            "print(sorted(set(nums)))",
        )
    if shape == "tuple_unpack":
        names = ", ".join(a["names"])
        values = ", ".join(repr(v) for v in a["values"])
        prints = [f"print({n})" for n in a["names"]]
        return _lines(f"{names} = ({values})", *prints)
    if shape == "enumerate_loop":
        return _lines(
            f"words = {_strs(a['words'])}",
            "for i, word in enumerate(words):",
            '    print(f"{i} {word}")',
        )
    if shape == "zip_loop":
        return _lines(
            f"xs = {_nums(a['xs'])}",
            f"ys = {_nums(a['ys'])}",
            "for x, y in zip(xs, ys):",
            f"    print({a['expr']})",
        )
    if shape == "sorted_key":
        return _lines(
            f"words = {_strs(a['words'])}",
            f"for word in sorted(words, key={a['key']}):",
            "    print(word)",
        )
    raise KeyError(shape)


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "python":
        return None
    return _python(shape, args)


# ── What each of them prints ─────────────────────────────────
#
# Worked out with Python's own semantics, which is the point of a
# single-language tier: `print(sorted(set(nums)))` really does print a list,
# and what a list looks like is now something an exercise may depend on.


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "fmt_value":
        lines = [a["label"] + ": " + format(a["value"], a["spec"])]
    elif shape == "comprehension":
        built = [value(a["expr"], {"i": i}) for i in range(a["lo"], a["hi"] + 1)]
        lines = [repr(built)]
    elif shape == "comprehension_if":
        built = [
            value(a["expr"], {"i": i})
            for i in range(a["lo"], a["hi"] + 1)
            if value(a["cond"], {"i": i})
        ]
        lines = [repr(built)]
    elif shape == "dict_get":
        table = dict(a["pairs"])
        lines = [str(table.get(a["key"], a["default"]))]
    elif shape == "dict_items":
        lines = [f"{k}: {v}" for k, v in a["pairs"]]
    elif shape == "unique_sorted":
        lines = [repr(sorted(set(a["items"])))]
    elif shape == "tuple_unpack":
        lines = [str(v) for v in a["values"]]
    elif shape == "enumerate_loop":
        lines = [f"{i} {w}" for i, w in enumerate(a["words"])]
    elif shape == "zip_loop":
        lines = [
            str(value(a["expr"], {"x": x, "y": y}))
            for x, y in zip(a["xs"], a["ys"])
        ]
    elif shape == "sorted_key":
        key = len if a["key"] == "len" else None
        lines = list(sorted(a["words"], key=key))
    else:
        raise KeyError(shape)
    return NL.join(lines)
