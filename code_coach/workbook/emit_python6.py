"""Python-only shapes, sixth batch: the shapes data comes in.

A NamedTuple, sets that combine, slices that step, dicts built in one
line and ordered by their values, a dict with a list behind every name,
and JSON going out and coming back. Then two workhorses that belong
nowhere in particular: tidying a string up, and the conditional
expression.

Determinism needs one rule here, and it is a good habit anyway: a set
has no order, so nothing prints a set. Everything goes through sorted
first, and json.dumps is always given sort_keys, which is what you want
in a file anyone has to diff.
"""

from __future__ import annotations

import json

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("namedtuple_use", "a tuple that knows its own field names"),
    Shape("set_maths", "sets joined, overlapped and subtracted"),
    Shape("slice_step", "taking every other one, and going backwards"),
    Shape("dict_comp", "building a dict in one line"),
    Shape("sort_by_value", "ordering a dict by its values"),
    Shape("dict_of_lists", "a list behind every name"),
    Shape("json_round", "text in, data out, and back again"),
    Shape("text_tidy", "trimming, lowering and replacing"),
    Shape("ternary", "the choice that fits on one line"),
    Shape("zip_to_dict", "two lists made into one dict"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _lit(v) -> str:
    return _q(v) if isinstance(v, str) else repr(v)


def _seq(items) -> str:
    return ", ".join(_lit(v) for v in items)


def _slice_text(spec) -> str:
    start, stop, step = spec
    parts = [
        "" if start is None else str(start),
        "" if stop is None else str(stop),
    ]
    if step is not None:
        parts.append(str(step))
    return ":".join(parts)


def _python(shape: str, a: dict) -> str:
    if shape == "namedtuple_use":
        fields = [f"    {n}: {t}" for n, t in a["fields"]]
        first = a["fields"][0][0]
        return _lines(
            "from typing import NamedTuple",
            "",
            "",
            f"class {a['cls']}(NamedTuple):",
            *fields,
            "",
            "",
            f"{a['var']} = {a['cls']}({_seq(a['values'])})",
            f"print({a['var']}.{first})",
            f"print({a['var']}[1])",
            f"print({a['var']})",
        )
    if shape == "set_maths":
        return _lines(
            "first = {" + _seq(a["left"]) + "}",
            "second = {" + _seq(a["right"]) + "}",
            "",
            "print(sorted(first | second))",
            "print(sorted(first & second))",
            "print(sorted(first - second))",
        )
    if shape == "slice_step":
        shows = [
            f"print(numbers[{_slice_text(spec)}])" for spec in a["specs"]
        ]
        return _lines(
            "numbers = [" + _seq(a["items"]) + "]",
            "",
            *shows,
        )
    if shape == "dict_comp":
        looks = [f"print(lengths[{_q(k)}])" for k in a["keys"]]
        return _lines(
            "words = [" + _seq(a["words"]) + "]",
            "lengths = {word: len(word) for word in words}",
            "",
            *looks,
        )
    if shape == "sort_by_value":
        order = ", reverse=True" if a["reverse"] else ""
        pairs = ", ".join(f"{_q(k)}: {v!r}" for k, v in a["pairs"])
        return _lines(
            "scores = {" + pairs + "}",
            "",
            "for name, score in sorted("
            + "scores.items(), key=lambda pair: pair[1]"
            + order
            + "):",
            "    print(name, score)",
        )
    if shape == "dict_of_lists":
        inside = ", ".join(
            f"{_q(k)}: [" + _seq(v) + "]" for k, v in a["groups"]
        )
        return _lines(
            "teams = {" + inside + "}",
            "",
            "for name in [" + _seq(a["order"]) + "]:",
            "    print(name, sum(teams[name]))",
        )
    if shape == "json_round":
        text = json.dumps(dict(a["pairs"]))
        looks = [f"print(data[{_q(k)}])" for k, _ in a["pairs"]]
        return _lines(
            "import json",
            "",
            "text = '" + text + "'",
            "data = json.loads(text)",
            "",
            *looks,
            "print(json.dumps(data, sort_keys=True))",
        )
    if shape == "text_tidy":
        return _lines(
            "raw = " + _q(a["raw"]),
            "clean = raw.strip()",
            "",
            "print(clean.lower())",
            f"print(clean.replace({_q(a['old'])}, {_q(a['new'])}))",
            f"print(clean.startswith({_q(a['prefix'])}))",
        )
    if shape == "ternary":
        return _lines(
            "for n in [" + _seq(a["values"]) + "]:",
            f"    print({_q(a['yes'])} if {a['cond']} else {_q(a['no'])})",
        )
    if shape == "zip_to_dict":
        looks = [f"print(pairs[{_q(k)}])" for k in a["lookups"]]
        return _lines(
            "names = [" + _seq(a["names"]) + "]",
            "scores = [" + _seq(a["scores"]) + "]",
            "pairs = dict(zip(names, scores))",
            "",
            *looks,
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
    if shape == "namedtuple_use":
        names = [n for n, _ in a["fields"]]
        inside = ", ".join(
            f"{n}={v!r}" for n, v in zip(names, a["values"])
        )
        lines = [
            str(a["values"][0]),
            str(a["values"][1]),
            f"{a['cls']}({inside})",
        ]
    elif shape == "set_maths":
        left, right = set(a["left"]), set(a["right"])
        lines = [
            repr(sorted(left | right)),
            repr(sorted(left & right)),
            repr(sorted(left - right)),
        ]
    elif shape == "slice_step":
        items = list(a["items"])
        lines = [repr(items[slice(*spec)]) for spec in a["specs"]]
    elif shape == "dict_comp":
        lines = [str(len(k)) for k in a["keys"]]
    elif shape == "sort_by_value":
        ordered = sorted(
            a["pairs"], key=lambda pair: pair[1], reverse=a["reverse"]
        )
        lines = [f"{k} {v}" for k, v in ordered]
    elif shape == "dict_of_lists":
        held = {k: list(v) for k, v in a["groups"]}
        lines = [f"{name} {sum(held[name])}" for name in a["order"]]
    elif shape == "json_round":
        data = dict(a["pairs"])
        lines = [str(v) for _, v in a["pairs"]]
        lines.append(json.dumps(data, sort_keys=True))
    elif shape == "text_tidy":
        clean = a["raw"].strip()
        lines = [
            clean.lower(),
            clean.replace(a["old"], a["new"]),
            str(clean.startswith(a["prefix"])),
        ]
    elif shape == "ternary":
        lines = [
            a["yes"] if value(a["cond"], {"n": n}) else a["no"]
            for n in a["values"]
        ]
    elif shape == "zip_to_dict":
        table = dict(zip(a["names"], a["scores"]))
        lines = [str(table[k]) for k in a["lookups"]]
    else:
        raise KeyError(shape)
    return NL.join(lines)
