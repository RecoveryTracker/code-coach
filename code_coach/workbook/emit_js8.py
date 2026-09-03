"""JavaScript-only shapes, eighth batch: privacy, precision, and functions
that return functions.

Real private fields with a hash. Number.EPSILON, which is the JavaScript
answer to the float page in the other book. String.raw. Object.seal
against freeze. Memoisation with a Map. Currying. fill. A class that
decides for itself how it converts to a string and to a number. Deep
equality written out, because JavaScript still has none. And returning
this, which is all a fluent interface is.
"""

from __future__ import annotations

import json

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_private_field", "a field nothing outside the class can reach"),
    Shape("js_epsilon", "comparing floats without ==="),
    Shape("js_string_raw", "a string with the backslashes left alone"),
    Shape("js_seal", "sealed, which is not the same as frozen"),
    Shape("js_memo_map", "answers remembered in a Map"),
    Shape("js_curry", "a function that returns a function"),
    Shape("js_fill", "an array made and filled in one go"),
    Shape("js_to_primitive", "an object that decides how it converts"),
    Shape("js_deep_equal", "equality written out by hand"),
    Shape("js_chaining", "returning this, over and over"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(str(n) for n in items)


def _words(items) -> str:
    return ", ".join(_q(w) for w in items)


def _js_string(text: str) -> str:
    """A JavaScript string literal, control characters and all.

    _q only wraps the text in quotes, which is fine until the text holds
    a newline: a line terminator inside a string literal is a syntax
    error, and a literal tab is legal but has no business in emitted
    source. JSON string syntax is a subset of JavaScript's, so this is
    exactly right and already escapes both.
    """
    return json.dumps(text)


def _private_field(a: dict) -> str:
    return _lines(
        f"class {a['cls']} {{",
        f"  #{a['field']};",
        "",
        f"  constructor({a['field']}) {{",
        f"    this.#{a['field']} = {a['field']};",
        "  }",
        "",
        f"  get {a['field']}() {{",
        f"    return this.#{a['field']};",
        "  }",
        "",
        f"  {a['method']}(n) {{",
        f"    this.#{a['field']} += n;",
        f"    return this.#{a['field']};",
        "  }",
        "}",
        "",
        f"const thing = new {a['cls']}({a['start']});",
        f"console.log(thing.{a['field']});",
        f"console.log(thing.{a['method']}({a['added']}));",
        "console.log(Object.keys(thing).length);",
    )


def _epsilon(a: dict) -> str:
    return _lines(
        f"const total = {a['left']} + {a['right']};",
        "",
        "console.log(total);",
        f"console.log(total === {a['target']});",
        f"console.log(Math.abs(total - {a['target']}) < Number.EPSILON);",
    )


def _string_raw(a: dict) -> str:
    return _lines(
        f"const path = String.raw`{a['raw']}`;",
        "",
        "console.log(path);",
        "console.log(path.length);",
        f"console.log({_js_string(a['escaped'])}.length);",
    )


def _seal(a: dict) -> str:
    return _lines(
        f"const thing = Object.seal({{ {a['keep']}: {_q(a['kept'])}, "
        f"{a['change']}: {a['before']} }});",
        "",
        f"thing.{a['change']} = {a['after']};",
        f"thing.{a['extra']} = 1;",
        f"delete thing.{a['keep']};",
        "",
        f"console.log(thing.{a['change']});",
        f"console.log(thing.{a['extra']});",
        f"console.log(thing.{a['keep']});",
        "console.log(Object.isSealed(thing));",
    )


def _memo_map(a: dict) -> str:
    return _lines(
        "const cache = new Map();",
        "",
        "function fib(n) {",
        "  if (n < 2) {",
        "    return n;",
        "  }",
        "  if (!cache.has(n)) {",
        "    cache.set(n, fib(n - 1) + fib(n - 2));",
        "  }",
        "  return cache.get(n);",
        "}",
        "",
        f"console.log(fib({a['wanted']}));",
        "console.log(cache.size);",
    )


def _curry(a: dict) -> str:
    return _lines(
        f"const {a['name']} = (a) => (b) => {a['expr']};",
        f"const {a['fixed_name']} = {a['name']}({a['fixed']});",
        "",
        f"console.log({a['fixed_name']}({a['call']}));",
        f"console.log({a['name']}({a['other'][0]})({a['other'][1]}));",
    )


def _fill(a: dict) -> str:
    return _lines(
        f"const zeros = new Array({a['count']}).fill({a['filler']});",
        f"const counted = Array.from({{ length: {a['count']} }}, "
        "(_, i) => i);",
        f"const patched = [{_nums(a['items'])}].fill({a['patch']}, "
        f"{a['start']}, {a['stop']});",
        "",
        'console.log(zeros.join(", "));',
        'console.log(counted.join(", "));',
        'console.log(patched.join(", "));',
    )


def _to_primitive(a: dict) -> str:
    return _lines(
        f"class {a['cls']} {{",
        f"  constructor({a['field']}) {{",
        f"    this.{a['field']} = {a['field']};",
        "  }",
        "",
        "  toString() {",
        f"    return `${{this.{a['field']}}}{a['suffix']}`;",
        "  }",
        "",
        "  valueOf() {",
        f"    return this.{a['field']};",
        "  }",
        "}",
        "",
        f"const thing = new {a['cls']}({a['value']});",
        "console.log(`${thing}`);",
        "console.log(thing + 0);",
        "console.log(String(thing));",
    )


def _deep_equal(a: dict) -> str:
    return _lines(
        "function same(a, b) {",
        "  if (a === b) {",
        "    return true;",
        "  }",
        '  if (typeof a !== "object" || typeof b !== "object") {',
        "    return false;",
        "  }",
        "  if (a === null || b === null) {",
        "    return false;",
        "  }",
        "  const keys = Object.keys(a);",
        "  if (keys.length !== Object.keys(b).length) {",
        "    return false;",
        "  }",
        "  return keys.every((key) => same(a[key], b[key]));",
        "}",
        "",
        f"console.log(same({{ {a['field']}: {a['value']} }}, "
        f"{{ {a['field']}: {a['value']} }}));",
        f"console.log({{ {a['field']}: {a['value']} }} === "
        f"{{ {a['field']}: {a['value']} }});",
        f"console.log(same({{ {a['field']}: {{ {a['inner']}: "
        f"{a['deep']} }} }}, {{ {a['field']}: {{ {a['inner']}: "
        f"{a['deep']} }} }}));",
    )


def _chaining(a: dict) -> str:
    calls = "".join(f".{a['method']}({_q(p)})" for p in a["parts"])
    return _lines(
        f"class {a['cls']} {{",
        "  constructor() {",
        "    this.parts = [];",
        "  }",
        "",
        f"  {a['method']}(part) {{",
        "    this.parts.push(part);",
        "    return this;",
        "  }",
        "",
        f"  {a['finish']}() {{",
        f"    return this.parts.join({_q(a['between'])});",
        "  }",
        "}",
        "",
        f"console.log(new {a['cls']}(){calls}.{a['finish']}());",
    )


_JS = {
    "js_private_field": _private_field,
    "js_epsilon": _epsilon,
    "js_string_raw": _string_raw,
    "js_seal": _seal,
    "js_memo_map": _memo_map,
    "js_curry": _curry,
    "js_fill": _fill,
    "js_to_primitive": _to_primitive,
    "js_deep_equal": _deep_equal,
    "js_chaining": _chaining,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "javascript":
        return None
    return _JS[shape](args)


# ── What each of them prints ─────────────────────────────────

_TOOLS = {"sum": sum, "len": len, "max": max, "min": min, "abs": abs}


def _js_number(value: float) -> str:
    """A float printed the way Node prints it.

    Both languages use the shortest representation that round-trips, so
    Python's repr and JavaScript's default agree - except that Python
    writes a trailing .0 on a whole number and JavaScript does not.
    """
    if value == int(value):
        return str(int(value))
    return repr(value)


def _fib(n: int) -> int:
    first, second = 0, 1
    for _ in range(n):
        first, second = second, first + second
    return first


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "js_private_field":
        lines = [
            str(a["start"]),
            str(a["start"] + a["added"]),
            # A private field is not a property, so Object.keys sees none.
            "0",
        ]
    elif shape == "js_epsilon":
        total = a["left"] + a["right"]
        if total == a["target"]:
            raise ValueError(
                f"{a['left']} + {a['right']} is exactly {a['target']}"
            )
        if abs(total - a["target"]) >= 2.220446049250313e-16:
            raise ValueError("the gap must be inside one epsilon")
        lines = [_js_number(total), "false", "true"]
    elif shape == "js_string_raw":
        lines = [
            a["raw"],
            str(len(a["raw"])),
            str(len(a["escaped_value"])),
        ]
    elif shape == "js_seal":
        # Sealed lets you change what is there and refuses to add or
        # remove, all without complaint.
        lines = [
            str(a["after"]),
            "undefined",
            a["kept"],
            "true",
        ]
    elif shape == "js_memo_map":
        wanted = a["wanted"]
        if wanted < 3:
            raise ValueError("the cache must end up holding something")
        # Every n from 2 up to the one asked for is stored once.
        lines = [str(_fib(wanted)), str(wanted - 1)]
    elif shape == "js_curry":
        first = value(a["expr"], {"a": a["fixed"], "b": a["call"], **_TOOLS})
        second = value(
            a["expr"],
            {"a": a["other"][0], "b": a["other"][1], **_TOOLS},
        )
        lines = [str(first), str(second)]
    elif shape == "js_fill":
        count = a["count"]
        zeros = [a["filler"]] * count
        counted = list(range(count))
        patched = list(a["items"])
        for i in range(a["start"], a["stop"]):
            patched[i] = a["patch"]
        if patched == list(a["items"]):
            raise ValueError("the fill must change something")
        lines = [
            ", ".join(str(n) for n in zeros),
            ", ".join(str(n) for n in counted),
            ", ".join(str(n) for n in patched),
        ]
    elif shape == "js_to_primitive":
        text = f"{a['value']}{a['suffix']}"
        # A template literal asks for a string; + 0 asks for a number.
        lines = [text, str(a["value"]), text]
    elif shape == "js_deep_equal":
        lines = ["true", "false", "true"]
    elif shape == "js_chaining":
        lines = [a["between"].join(a["parts"])]
    else:
        raise KeyError(shape)
    return NL.join(lines)
