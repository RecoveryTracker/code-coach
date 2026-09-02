"""Python-only shapes, fifth batch: saying what you mean.

Four ideas, all of them about being explicit. Type hints say what a
function expects and returns, without changing what it does. Dataclasses
say the same about a class and hand you __init__ and __repr__ for free —
the ten lines of page 101 in three. defaultdict says what a missing key
should be before anyone asks for one. Format specifiers say how a number
should look on the way out.

None of it is new capability. All of it is the same program with the
intent written down, which is most of what separates code that is read
once from code that is read for years.
"""

from __future__ import annotations

import re

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("type_hint_func", "saying what a function takes and gives back"),
    Shape("type_hint_list", "a hint for a list, and for the answer"),
    Shape("optional_hint", "a value that is allowed to be missing"),
    Shape("dataclass_basic", "a class of plain fields, written short"),
    Shape("dataclass_method", "a dataclass that also does something"),
    Shape("defaultdict_count", "a dict where a missing key starts at zero"),
    Shape("defaultdict_group", "piling things into lists by key"),
    Shape("dict_get_default", "asking for a key that may not be there"),
    Shape("format_number", "deciding how a number is printed"),
    Shape("format_row", "columns that line up"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _lit(v) -> str:
    return _q(v) if isinstance(v, str) else repr(v)


def _selfify(expr: str, fields) -> str:
    """`width * height` becomes `self.width * self.height`."""
    out = expr
    for name in fields:
        out = re.sub(rf"\b{re.escape(name)}\b", f"self.{name}", out)
    return out


def _python(shape: str, a: dict) -> str:
    if shape == "type_hint_func":
        sig = ", ".join(f"{n}: {t}" for n, t in a["params"])
        calls = [
            f"print({a['name']}(" + ", ".join(_lit(v) for v in call) + "))"
            for call in a["calls"]
        ]
        return _lines(
            f"def {a['name']}({sig}) -> {a['ret']}:",
            f"    return {a['expr']}",
            "",
            *calls,
        )
    if shape == "type_hint_list":
        calls = [
            f"print({a['name']}([" + ", ".join(_lit(v) for v in items) + "]))"
            for items in a["lists"]
        ]
        return _lines(
            f"def {a['name']}({a['param']}: list[{a['elem']}]) -> {a['ret']}:",
            f"    return {a['expr']}",
            "",
            *calls,
        )
    if shape == "optional_hint":
        calls = [f"print({a['name']}({_lit(v)}))" for v in a["values"]]
        return _lines(
            f"def {a['name']}({a['param']}: str | None) -> str:",
            f"    if {a['param']} is None:",
            f"        return {_q(a['missing'])}",
            f"    return {a['param']}",
            "",
            *calls,
        )
    if shape == "dataclass_basic":
        fields = [f"    {n}: {t}" for n, t in a["fields"]]
        made = ", ".join(_lit(v) for v in a["values"])
        shows = [f"print({a['var']}.{n})" for n, _ in a["fields"]]
        return _lines(
            "from dataclasses import dataclass",
            "",
            "",
            "@dataclass",
            f"class {a['cls']}:",
            *fields,
            "",
            "",
            f"{a['var']} = {a['cls']}({made})",
            *shows,
            f"print({a['var']})",
        )
    if shape == "dataclass_method":
        names = [n for n, _, _ in a["fields"]]
        fields = [f"    {n}: {t}" for n, t, _ in a["fields"]]
        made = ", ".join(_lit(v) for _, _, v in a["fields"])
        return _lines(
            "from dataclasses import dataclass",
            "",
            "",
            "@dataclass",
            f"class {a['cls']}:",
            *fields,
            "",
            f"    def {a['method']}(self):",
            f"        return {_selfify(a['expr'], names)}",
            "",
            "",
            f"thing = {a['cls']}({made})",
            f"print(thing.{a['method']}())",
            "print(thing)",
        )
    if shape == "defaultdict_count":
        looks = [f"print(counts[{_q(k)}])" for k in a["keys"]]
        return _lines(
            "from collections import defaultdict",
            "",
            "words = [" + ", ".join(_q(w) for w in a["words"]) + "]",
            "counts = defaultdict(int)",
            "for word in words:",
            "    counts[word] += 1",
            "",
            *looks,
        )
    if shape == "defaultdict_group":
        looks = [f"print(groups[{_q(k)}])" for k in a["keys"]]
        return _lines(
            "from collections import defaultdict",
            "",
            "words = [" + ", ".join(_q(w) for w in a["words"]) + "]",
            "groups = defaultdict(list)",
            "for word in words:",
            "    groups[word[0]].append(word)",
            "",
            *looks,
        )
    if shape == "dict_get_default":
        pairs = ", ".join(f"{_q(k)}: {v!r}" for k, v in a["pairs"])
        looks = [
            f"print({a['name']}.get({_q(k)}, {a['default']!r}))"
            for k in a["lookups"]
        ]
        return _lines(f"{a['name']} = {{{pairs}}}", *looks)
    if shape == "format_number":
        shows = ['print(f"{value:' + spec + '}")' for spec in a["specs"]]
        return _lines("value = " + repr(a["value"]), "", *shows)
    if shape == "format_row":
        rows = ", ".join(
            "(" + _q(n) + ", " + repr(c) + ")" for n, c in a["rows"]
        )
        show = (
            '    print(f"{name:<'
            + str(a["wide"])
            + '}{count:>'
            + str(a["num"])
            + '}")'
        )
        return _lines(
            "rows = [" + rows + "]",
            "for name, count in rows:",
            show,
        )
    raise KeyError(shape)


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "python":
        return None
    return _python(shape, args)


# ── What each of them prints ─────────────────────────────────

_TOOLS = {"sum": sum, "len": len, "max": max, "min": min}


def _repr_line(cls: str, pairs) -> str:
    inside = ", ".join(f"{n}={v!r}" for n, v in pairs)
    return f"{cls}({inside})"


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "type_hint_func":
        names = [n for n, _ in a["params"]]
        lines = [
            str(value(a["expr"], dict(zip(names, call))))
            for call in a["calls"]
        ]
    elif shape == "type_hint_list":
        lines = [
            str(value(a["expr"], {a["param"]: list(items), **_TOOLS}))
            for items in a["lists"]
        ]
    elif shape == "optional_hint":
        lines = [a["missing"] if v is None else v for v in a["values"]]
    elif shape == "dataclass_basic":
        names = [n for n, _ in a["fields"]]
        lines = [str(v) for v in a["values"]]
        lines.append(_repr_line(a["cls"], zip(names, a["values"])))
    elif shape == "dataclass_method":
        held = {n: v for n, _, v in a["fields"]}
        lines = [str(value(a["expr"], dict(held)))]
        lines.append(_repr_line(a["cls"], [(n, v) for n, _, v in a["fields"]]))
    elif shape == "defaultdict_count":
        lines = [str(list(a["words"]).count(k)) for k in a["keys"]]
    elif shape == "defaultdict_group":
        groups: dict[str, list] = {}
        for word in a["words"]:
            groups.setdefault(word[0], []).append(word)
        # A missing key is not missing for long: reading it makes an empty
        # list, which is the whole point of the page.
        lines = [repr(groups.get(k, [])) for k in a["keys"]]
    elif shape == "dict_get_default":
        table = dict(a["pairs"])
        lines = [str(table.get(k, a["default"])) for k in a["lookups"]]
    elif shape == "format_number":
        lines = [format(a["value"], spec) for spec in a["specs"]]
    elif shape == "format_row":
        lines = [
            format(n, "<" + str(a["wide"])) + format(c, ">" + str(a["num"]))
            for n, c in a["rows"]
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
