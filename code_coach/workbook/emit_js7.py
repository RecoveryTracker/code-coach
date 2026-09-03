"""JavaScript-only shapes, seventh batch: the object model underneath, and
coercion.

reduceRight. A labelled break, which is the only clean way out of nested
loops. Object.defineProperty and what a descriptor controls. The
prototype chain reached directly rather than through class. The type
checks, including typeof null. Radix conversion. URL and
encodeURIComponent. Sparse arrays. arguments against rest. And coercion,
where "5" - 2 and "5" + 2 disagree about what the plus sign is for.

Two things are deliberately absent. toPrecision is not used, because
Python has no formatting that matches it for every value and the
expected output has to be computed rather than hoped at. And nothing
prints a raw array or object.
"""

from __future__ import annotations

import urllib.parse

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_reduce_right", "folding from the other end"),
    Shape("js_labelled_break", "leaving two loops at once"),
    Shape("js_define_property", "a property with the rules spelled out"),
    Shape("js_prototype", "the object behind the object"),
    Shape("js_type_checks", "asking what something is"),
    Shape("js_radix", "the same number in another base"),
    Shape("js_url", "a web address, parsed and escaped"),
    Shape("js_sparse", "an array with a hole in it"),
    Shape("js_arguments", "every argument, the old way and the new"),
    Shape("js_coercion", "what the plus sign decides to do"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(str(n) for n in items)


def _words(items) -> str:
    return ", ".join(_q(w) for w in items)


def _reduce_right(a: dict) -> str:
    return _lines(
        "const words = [" + _words(a["words"]) + "];",
        "",
        'console.log(words.reduce((held, w) => held + w, ""));',
        'console.log(words.reduceRight((held, w) => held + w, ""));',
    )


def _labelled_break(a: dict) -> str:
    return _lines(
        f"outer: for (let i = 1; i <= {a['limit']}; i += 1) {{",
        f"  for (let j = 1; j <= {a['limit']}; j += 1) {{",
        f"    if (i * j > {a['stop']}) {{",
        "      break outer;",
        "    }",
        "    console.log(`${i} ${j}`);",
        "  }",
        "}",
        f"console.log({_q(a['done'])});",
    )


def _define_property(a: dict) -> str:
    return _lines(
        f"const thing = {{ name: {_q(a['name'])} }};",
        f"Object.defineProperty(thing, {_q(a['hidden'])}, {{",
        f"  value: {a['value']},",
        "  enumerable: false,",
        "  writable: false,",
        "});",
        "",
        f"thing.{a['hidden']} = {a['attempt']};",
        "",
        f"console.log(thing.{a['hidden']});",
        'console.log(Object.keys(thing).join(", "));',
        f"console.log({_q(a['hidden'])} in thing);",
    )


def _prototype(a: dict) -> str:
    return _lines(
        "const base = {",
        f"  {a['method']}() {{",
        f"    return {_q(a['says'])};",
        "  },",
        "};",
        "const thing = Object.create(base);",
        f"thing.{a['field']} = {_q(a['value'])};",
        "",
        f"console.log(thing.{a['method']}());",
        'console.log(Object.keys(thing).join(", "));',
        f"console.log(Object.hasOwn(thing, {_q(a['method'])}));",
        "console.log(Object.getPrototypeOf(thing) === base);",
    )


def _type_checks(a: dict) -> str:
    return _lines(
        "console.log(typeof []);",
        "console.log(Array.isArray([]));",
        "console.log(typeof null);",
        "console.log([] instanceof Array);",
        f"console.log(typeof {a['sample']});",
    )


def _radix(a: dict) -> str:
    return _lines(
        f"const value = {a['value']};",
        "",
        "console.log(value.toString(2));",
        "console.log(value.toString(16));",
        "console.log(value.toString(8));",
        f"console.log(parseInt({_q(a['hex'])}, 16));",
    )


def _url(a: dict) -> str:
    return _lines(
        f"const raw = {_q(a['raw'])};",
        "console.log(encodeURIComponent(raw));",
        "",
        f"const url = new URL({_q(a['address'])});",
        "console.log(url.hostname);",
        f"console.log(url.searchParams.get({_q(a['key'])}));",
    )


def _sparse(a: dict) -> str:
    return _lines(
        f"const holes = [{a['first']}, , {a['last']}];",
        "",
        "console.log(holes.length);",
        "console.log(holes[1]);",
        f"console.log(holes.map((n) => n * {a['times']}).length);",
        'console.log(Object.keys(holes).join(", "));',
    )


def _arguments(a: dict) -> str:
    return _lines(
        f"function {a['old']}() {{",
        "  return arguments.length;",
        "}",
        "",
        f"function {a['modern']}(...values) {{",
        "  return values.length;",
        "}",
        "",
        f'const {a["arrow"]} = (...values) => values.join(", ");',
        "",
        f"console.log({a['old']}({_nums(a['given'])}));",
        f"console.log({a['modern']}({_nums(a['given'])}));",
        f"console.log({a['arrow']}({_nums(a['given'])}));",
    )


def _coercion(a: dict) -> str:
    return _lines(
        f'console.log({_q(a["digits"])} - {a["taken"]});',
        f'console.log({_q(a["digits"])} + {a["taken"]});',
        f"console.log({a['plain']} + true);",
        "console.log([] + {});",
    )


_JS = {
    "js_reduce_right": _reduce_right,
    "js_labelled_break": _labelled_break,
    "js_define_property": _define_property,
    "js_prototype": _prototype,
    "js_type_checks": _type_checks,
    "js_radix": _radix,
    "js_url": _url,
    "js_sparse": _sparse,
    "js_arguments": _arguments,
    "js_coercion": _coercion,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "javascript":
        return None
    return _JS[shape](args)


# ── What each of them prints ─────────────────────────────────

# encodeURIComponent leaves these alone; Python's quote does not, so it
# has to be told. Anything outside this set is percent-escaped by both.
_KEPT = "-_.!~*'()"


def _encode_component(raw: str) -> str:
    return urllib.parse.quote(raw, safe=_KEPT)


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "js_reduce_right":
        forward = "".join(a["words"])
        backward = "".join(reversed(a["words"]))
        if forward == backward:
            raise ValueError("the two directions must read differently")
        lines = [forward, backward]
    elif shape == "js_labelled_break":
        broke = False
        for i in range(1, a["limit"] + 1):
            for j in range(1, a["limit"] + 1):
                if i * j > a["stop"]:
                    broke = True
                    break
                lines.append(f"{i} {j}")
            if broke:
                break
        if not broke:
            raise ValueError("the break must actually happen")
        if not lines:
            raise ValueError("the loop must print something first")
        lines.append(a["done"])
    elif shape == "js_define_property":
        # writable: false means the assignment is ignored without a word,
        # and enumerable: false keeps it out of Object.keys while `in`
        # still finds it.
        lines = [str(a["value"]), "name", "true"]
    elif shape == "js_prototype":
        lines = [a["says"], a["field"], "false", "true"]
    elif shape == "js_type_checks":
        lines = ["object", "true", "object", "true", a["expected"]]
    elif shape == "js_radix":
        n = a["value"]
        lines = [f"{n:b}", f"{n:x}", f"{n:o}", str(int(a["hex"], 16))]
    elif shape == "js_url":
        parts = urllib.parse.urlparse(a["address"])
        found = urllib.parse.parse_qs(parts.query)
        if a["key"] not in found:
            raise ValueError(f"{a['key']!r} is not in the query string")
        lines = [
            _encode_component(a["raw"]),
            parts.hostname or "",
            found[a["key"]][0],
        ]
    elif shape == "js_sparse":
        # The hole survives map, so the length is unchanged, and the
        # missing index is simply absent from the keys.
        lines = ["3", "undefined", "3", "0, 2"]
    elif shape == "js_arguments":
        count = str(len(a["given"]))
        lines = [count, count, ", ".join(str(n) for n in a["given"])]
    elif shape == "js_coercion":
        digits, taken = a["digits"], a["taken"]
        # Minus has one meaning, so the string is converted to a number.
        # Plus has two, and joining text wins.
        lines = [
            str(int(digits) - taken),
            digits + str(taken),
            str(a["plain"] + 1),
            "[object Object]",
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
