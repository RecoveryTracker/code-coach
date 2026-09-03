"""Python-only shapes, seventh batch: the parts of a class you had not met,
and errors you named yourself.

Pages 101-110 built a class out of __init__, methods and inheritance.
This is the rest of it: a property that looks like a field and runs like
a method, methods that belong to the class rather than to one object,
and the two dunders that let Python's own == and sorted work on things
you wrote.

Then errors. Page 98 caught one and page 99 raised one; here you name
your own exception type, and meet the four-part try that most people
never finish learning - the else that runs when nothing went wrong, and
the finally that runs either way.
"""

from __future__ import annotations

import re

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("property_use", "a field that is really a method"),
    Shape("static_method", "a method that needs no object"),
    Shape("class_counter", "a method that belongs to the class"),
    Shape("eq_dunder", "teaching == what equal means"),
    Shape("lt_dunder", "teaching sorted how to order them"),
    Shape("custom_error", "an exception type of your own"),
    Shape("try_else_finally", "the two halves of try most people skip"),
    Shape("error_hierarchy", "one except catching a whole family"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _lit(v) -> str:
    return _q(v) if isinstance(v, str) else repr(v)


def _selfify(expr: str, fields) -> str:
    out = expr
    for name in fields:
        out = re.sub(rf"\b{re.escape(name)}\b", f"self.{name}", out)
    return out


def _init(cls: str, fields) -> list[str]:
    """The __init__ every one of these classes starts with."""
    names = [n for n, _ in fields]
    args = ", ".join(names)
    body = [f"        self.{n} = {n}" for n in names]
    return [f"class {cls}:", f"    def __init__(self, {args}):", *body]


def _python(shape: str, a: dict) -> str:
    if shape == "property_use":
        names = [n for n, _ in a["fields"]]
        made = ", ".join(_lit(v) for _, v in a["fields"])
        return _lines(
            *_init(a["cls"], a["fields"]),
            "",
            "    @property",
            f"    def {a['name']}(self):",
            f"        return {_selfify(a['expr'], names)}",
            "",
            "",
            f"thing = {a['cls']}({made})",
            f"print(thing.{a['name']})",
        )
    if shape == "static_method":
        calls = [
            f"print({a['cls']}.{a['name']}(" + ", ".join(_lit(v) for v in c) + "))"
            for c in a["calls"]
        ]
        params = ", ".join(a["params"])
        return _lines(
            f"class {a['cls']}:",
            "    @staticmethod",
            f"    def {a['name']}({params}):",
            f"        return {a['expr']}",
            "",
            "",
            *calls,
        )
    if shape == "class_counter":
        # The method and the counter share a namespace: name them the same
        # and the def quietly replaces the attribute, which fails later and
        # somewhere else.
        if a["name"] == "made":
            raise ValueError("class_counter method cannot be called 'made'")
        makes = [f"{a['cls']}()" for _ in range(a["times"])]
        return _lines(
            f"class {a['cls']}:",
            f"    made = {a['start']!r}",
            "",
            "    def __init__(self):",
            f"        {a['cls']}.made += 1",
            "",
            "    @classmethod",
            f"    def {a['name']}(cls):",
            "        return cls.made",
            "",
            "",
            *[f"{m}" for m in makes],
            f"print({a['cls']}.{a['name']}())",
        )
    if shape == "eq_dunder":
        names = [n for n, _ in a["fields"]]
        left = ", ".join(_lit(v) for v in a["left"])
        right = ", ".join(_lit(v) for v in a["right"])
        same = " and ".join(
            f"self.{n} == other.{n}" for n in names
        )
        return _lines(
            *_init(a["cls"], a["fields"]),
            "",
            "    def __eq__(self, other):",
            f"        return {same}",
            "",
            "",
            f"first = {a['cls']}({left})",
            f"second = {a['cls']}({right})",
            "print(first == second)",
            "print(first is second)",
        )
    if shape == "lt_dunder":
        made = ", ".join(
            f"{a['cls']}({_lit(n)}, {v!r})" for n, v in a["things"]
        )
        return _lines(
            *_init(a["cls"], (("name", "str"), (a["by"], "int"))),
            "",
            "    def __lt__(self, other):",
            f"        return self.{a['by']} < other.{a['by']}",
            "",
            "",
            f"things = [{made}]",
            "for thing in sorted(things):",
            "    print(thing.name)",
        )
    if shape == "custom_error":
        return _lines(
            f"class {a['error']}(Exception):",
            "    pass",
            "",
            "",
            "def check(n):",
            f"    if {a['cond']}:",
            f"        raise {a['error']}({_q(a['message'])})",
            "    return n",
            "",
            "",
            "for n in [" + ", ".join(repr(v) for v in a["values"]) + "]:",
            "    try:",
            "        print(check(n))",
            f"    except {a['error']} as problem:",
            "        print(problem)",
        )
    if shape == "try_else_finally":
        return _lines(
            "for n in [" + ", ".join(repr(v) for v in a["values"]) + "]:",
            "    try:",
            f"        result = {a['expr']}",
            f"    except {a['error']}:",
            f"        print({_q(a['failed'])})",
            "    else:",
            "        print(result)",
            "    finally:",
            f"        print({_q(a['always'])})",
        )
    if shape == "error_hierarchy":
        return _lines(
            f"class {a['base']}(Exception):",
            "    pass",
            "",
            "",
            f"class {a['sub']}({a['base']}):",
            "    pass",
            "",
            "",
            "def check(n):",
            f"    if {a['worse']}:",
            f"        raise {a['sub']}({_q(a['sub'])})",
            f"    if {a['bad']}:",
            f"        raise {a['base']}({_q(a['base'])})",
            "    return n",
            "",
            "",
            "for n in [" + ", ".join(repr(v) for v in a["values"]) + "]:",
            "    try:",
            "        print(check(n))",
            f"    except {a['sub']}:",
            f"        print({_q(a['sub_label'])})",
            f"    except {a['base']}:",
            f"        print({_q(a['base_label'])})",
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
    if shape == "property_use":
        held = {n: v for n, v in a["fields"]}
        lines = [str(value(a["expr"], {**held, **_TOOLS}))]
    elif shape == "static_method":
        lines = [
            str(value(a["expr"], {**dict(zip(a["params"], c)), **_TOOLS}))
            for c in a["calls"]
        ]
    elif shape == "class_counter":
        lines = [str(a["start"] + a["times"])]
    elif shape == "eq_dunder":
        same = list(a["left"]) == list(a["right"])
        # Equal, and still two different objects: that is the whole page.
        lines = [str(same), "False"]
    elif shape == "lt_dunder":
        ordered = sorted(a["things"], key=lambda pair: pair[1])
        lines = [name for name, _ in ordered]
    elif shape == "custom_error":
        for n in a["values"]:
            if value(a["cond"], {"n": n, **_TOOLS}):
                lines.append(a["message"])
            else:
                lines.append(str(n))
    elif shape == "try_else_finally":
        for n in a["values"]:
            try:
                lines.append(str(value(a["expr"], {"n": n, **_TOOLS})))
            except ZeroDivisionError:
                lines.append(a["failed"])
            lines.append(a["always"])
    elif shape == "error_hierarchy":
        for n in a["values"]:
            # The subclass is tested first, exactly as the excepts are
            # ordered: put the base first and it would swallow both.
            if value(a["worse"], {"n": n, **_TOOLS}):
                lines.append(a["sub_label"])
            elif value(a["bad"], {"n": n, **_TOOLS}):
                lines.append(a["base_label"])
            else:
                lines.append(str(n))
    else:
        raise KeyError(shape)
    return NL.join(lines)
