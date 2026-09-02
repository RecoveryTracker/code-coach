"""Python-only shapes, third batch: objects.

A class is the first thing in this book that is not a value or a function —
it is a shape for making things, and the thing it makes carries its own data
around with it. So these shapes are longer than the earlier ones, and that is
the lesson rather than an accident: the ceremony is what you are learning.

Expressions in these are written in terms of the field names, and the emitter
turns those into `self.name` where they appear in a method body. The exercise
data stays readable that way — "size * size" rather than
"self.size * self.size" — and the expected output can evaluate the same
expression with the field values bound directly.
"""

from __future__ import annotations

import re

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("class_init", "a class that holds its own data"),
    Shape("class_two", "two objects of the same class, each with its own"),
    Shape("class_method", "a function that belongs to the object"),
    Shape("class_method_arg", "a method that is also handed something"),
    Shape("class_repr", "deciding what your object looks like printed"),
    Shape("dataclass_use", "the same class, most of it written for you"),
    Shape("class_attr", "one value shared by every instance"),
    Shape("inherit_use", "a class that starts from another one"),
    Shape("override", "replacing a method you inherited"),
    Shape("super_call", "extending the parent rather than replacing it"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _selfify(expr: str, fields) -> str:
    """`size * size` becomes `self.size * self.size`.

    Word boundaries, so a field called `n` does not rewrite the `n` inside
    another name.
    """
    out = expr
    for name in fields:
        out = re.sub(rf"\b{re.escape(name)}\b", f"self.{name}", out)
    return out


def _lit(v) -> str:
    return _q(v) if isinstance(v, str) else repr(v)


def _init(fields) -> list[str]:
    params = ", ".join(fields)
    return [f"    def __init__(self, {params}):"] + [
        f"        self.{f} = {f}" for f in fields
    ]


def _python(shape: str, a: dict) -> str:
    if shape == "class_init":
        fields = [f for f, _ in a["fields"]]
        made = ", ".join(_lit(v) for _, v in a["fields"])
        return _lines(
            f"class {a['cls']}:",
            *_init(fields),
            "",
            f"thing = {a['cls']}({made})",
            *[f"print(thing.{f})" for f in a["reads"]],
        )
    if shape == "class_two":
        fields = a["fields"]
        one = ", ".join(_lit(v) for v in a["values1"])
        two = ", ".join(_lit(v) for v in a["values2"])
        return _lines(
            f"class {a['cls']}:",
            *_init(fields),
            "",
            f"first = {a['cls']}({one})",
            f"second = {a['cls']}({two})",
            *[
                f"print({'first' if which == 0 else 'second'}.{f})"
                for which, f in a["reads"]
            ],
        )
    if shape == "class_method":
        fields = [f for f, _ in a["fields"]]
        made = ", ".join(_lit(v) for _, v in a["fields"])
        return _lines(
            f"class {a['cls']}:",
            *_init(fields),
            "",
            f"    def {a['method']}(self):",
            f"        return {_selfify(a['expr'], fields)}",
            "",
            f"thing = {a['cls']}({made})",
            f"print(thing.{a['method']}())",
        )
    if shape == "class_method_arg":
        fields = [f for f, _ in a["fields"]]
        made = ", ".join(_lit(v) for _, v in a["fields"])
        calls = [f"print(thing.{a['method']}({v}))" for v in a["calls"]]
        return _lines(
            f"class {a['cls']}:",
            *_init(fields),
            "",
            f"    def {a['method']}(self, {a['param']}):",
            f"        return {_selfify(a['expr'], fields)}",
            "",
            f"thing = {a['cls']}({made})",
            *calls,
        )
    if shape == "class_repr":
        fields = [f for f, _ in a["fields"]]
        made = ", ".join(_lit(v) for _, v in a["fields"])
        inside = ", ".join("{self." + f + "}" for f in fields)
        return _lines(
            f"class {a['cls']}:",
            *_init(fields),
            "",
            "    def __repr__(self):",
            f'        return f"{a["cls"]}({inside})"',
            "",
            f"thing = {a['cls']}({made})",
            "print(thing)",
        )
    if shape == "dataclass_use":
        made = ", ".join(_lit(v) for _, _, v in a["fields"])
        return _lines(
            "from dataclasses import dataclass",
            "",
            "",
            "@dataclass",
            f"class {a['cls']}:",
            *[f"    {f}: {t}" for f, t, _ in a["fields"]],
            "",
            "",
            f"thing = {a['cls']}({made})",
            "print(thing)",
        )
    if shape == "class_attr":
        shared, shared_value = a["shared"]
        return _lines(
            f"class {a['cls']}:",
            f"    {shared} = {_lit(shared_value)}",
            "",
            f"    def __init__(self, {a['field']}):",
            f"        self.{a['field']} = {a['field']}",
            "",
            f"first = {a['cls']}({_lit(a['values'][0])})",
            f"second = {a['cls']}({_lit(a['values'][1])})",
            f"print(first.{shared})",
            f"print(second.{shared})",
            f"print(first.{a['field']})",
            f"print(second.{a['field']})",
        )
    if shape == "inherit_use":
        return _lines(
            f"class {a['base']}:",
            f"    def __init__(self, {a['field']}):",
            f"        self.{a['field']} = {a['field']}",
            "",
            f"    def {a['method']}(self):",
            f'        return {_q(a["prefix"])} + self.{a["field"]}',
            "",
            "",
            f"class {a['sub']}({a['base']}):",
            "    pass",
            "",
            "",
            f"thing = {a['sub']}({_q(a['value'])})",
            f"print(thing.{a['field']})",
            f"print(thing.{a['method']}())",
        )
    if shape == "override":
        return _lines(
            f"class {a['base']}:",
            f"    def {a['method']}(self):",
            f"        return {_q(a['base_says'])}",
            "",
            "",
            f"class {a['sub']}({a['base']}):",
            f"    def {a['method']}(self):",
            f"        return {_q(a['sub_says'])}",
            "",
            "",
            f"print({a['base']}().{a['method']}())",
            f"print({a['sub']}().{a['method']}())",
        )
    if shape == "super_call":
        return _lines(
            f"class {a['base']}:",
            f"    def __init__(self, {a['base_field']}):",
            f"        self.{a['base_field']} = {a['base_field']}",
            "",
            "",
            f"class {a['sub']}({a['base']}):",
            f"    def __init__(self, {a['base_field']}, {a['sub_field']}):",
            f"        super().__init__({a['base_field']})",
            f"        self.{a['sub_field']} = {a['sub_field']}",
            "",
            "",
            f"thing = {a['sub']}({_lit(a['values'][0])}, {_lit(a['values'][1])})",
            f"print(thing.{a['base_field']})",
            f"print(thing.{a['sub_field']})",
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
    if shape == "class_init":
        held = dict(a["fields"])
        lines = [str(held[f]) for f in a["reads"]]
    elif shape == "class_two":
        both = (
            dict(zip(a["fields"], a["values1"])),
            dict(zip(a["fields"], a["values2"])),
        )
        lines = [str(both[which][f]) for which, f in a["reads"]]
    elif shape == "class_method":
        held = dict(a["fields"])
        lines = [str(value(a["expr"], held))]
    elif shape == "class_method_arg":
        held = dict(a["fields"])
        lines = [
            str(value(a["expr"], {**held, a["param"]: v})) for v in a["calls"]
        ]
    elif shape == "class_repr":
        inside = ", ".join(str(v) for _, v in a["fields"])
        lines = [f"{a['cls']}({inside})"]
    elif shape == "dataclass_use":
        inside = ", ".join(f"{f}={v!r}" for f, _, v in a["fields"])
        lines = [f"{a['cls']}({inside})"]
    elif shape == "class_attr":
        shared, shared_value = a["shared"]
        lines = [
            str(shared_value),
            str(shared_value),
            str(a["values"][0]),
            str(a["values"][1]),
        ]
    elif shape == "inherit_use":
        lines = [a["value"], a["prefix"] + a["value"]]
    elif shape == "override":
        lines = [a["base_says"], a["sub_says"]]
    elif shape == "super_call":
        lines = [str(a["values"][0]), str(a["values"][1])]
    else:
        raise KeyError(shape)
    return NL.join(lines)
