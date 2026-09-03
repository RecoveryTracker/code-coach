"""JavaScript-only shapes: the start of JavaScript's own intermediate tier.

Python got its depth first, on the argument that one language done
properly beats six done thinly. This is the same move for JavaScript,
and these pages are numbered from 81 in JavaScript's own book - the same
numbers Python uses for different pages, which is fine because nobody
reads both books at once.

One rule carried over from the shared tiers, for a different reason.
Node prints an array as [ 1, 2, 3 ], with spaces, and an object as
{ x: 2 } - formatting that is easy to get wrong when writing the
expected output by hand and easy to change between versions. So nothing
here prints a raw array or object: everything goes through join, or
prints one value at a time.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_template", "a value inside a backtick string"),
    Shape("js_map", "a new array with each item changed"),
    Shape("js_filter", "only the items that qualify"),
    Shape("js_reduce", "an array folded down to one value"),
    Shape("js_destructure", "pulling names out of an object and an array"),
    Shape("js_spread", "three dots, spreading and collecting"),
    Shape("js_arrow", "a function without the word function"),
    Shape("js_default_params", "an argument you can leave out"),
    Shape("js_optional_chain", "reaching for something that may not be there"),
    Shape("js_map_set", "Map and Set, which are not objects and arrays"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(str(n) for n in items)


def _as_js(expr: str) -> str:
    """The same test, written the way JavaScript wants it.

    Expressions are stored in a form Python can evaluate for the expected
    output. Only equality differs: Python's == is JavaScript's ===, and
    the loose == is a different operator that this book never wants.
    """
    return expr.replace("==", "===")


def _js(shape: str, a: dict) -> str:
    if shape == "js_template":
        return _lines(
            f"const name = {_q(a['name'])};",
            f"const age = {a['age']};",
            "",
            "console.log(`${name} is ${age}`);",
            f"console.log(`${{name}} will be ${{age + {a['ahead']}}}`);",
        )
    if shape == "js_map":
        return _lines(
            "const numbers = [" + _nums(a["items"]) + "];",
            f"const changed = numbers.map((n) => {a['expr']});",
            "",
            'console.log(changed.join(", "));',
            "console.log(changed.length);",
        )
    if shape == "js_filter":
        return _lines(
            "const numbers = [" + _nums(a["items"]) + "];",
            f"const kept = numbers.filter((n) => {_as_js(a['test'])});",
            "",
            'console.log(kept.join(", "));',
            "console.log(kept.length);",
        )
    if shape == "js_reduce":
        return _lines(
            "const numbers = [" + _nums(a["items"]) + "];",
            f"const total = numbers.reduce((sum, n) => {a['step']}, "
            f"{a['start']});",
            "",
            "console.log(total);",
            "console.log(numbers.reduce((best, n) => (n > best ? n : best)));",
        )
    if shape == "js_destructure":
        return _lines(
            f"const point = {{ {a['first']}: {a['values'][0]}, "
            f"{a['second']}: {a['values'][1]} }};",
            f"const {{ {a['first']}, {a['second']} }} = point;",
            f"const [head, tail] = [{a['pair'][0]}, {a['pair'][1]}];",
            "",
            f"console.log({a['first']} + {a['second']});",
            "console.log(head + tail);",
            f"console.log(`${{{a['first']}}} ${{tail}}`);",
        )
    if shape == "js_spread":
        return _lines(
            "const first = [" + _nums(a["first"]) + "];",
            "const second = [" + _nums(a["second"]) + "];",
            "const joined = [...first, ...second];",
            "",
            "function total(...numbers) {",
            "  return numbers.reduce((sum, n) => sum + n, 0);",
            "}",
            "",
            'console.log(joined.join(", "));',
            "console.log(total(...joined));",
        )
    if shape == "js_arrow":
        return _lines(
            f"const {a['one_name']} = (n) => {a['one_expr']};",
            f"const {a['two_name']} = (a, b) => {a['two_expr']};",
            "",
            f"console.log({a['one_name']}({a['one_call']}));",
            f"console.log({a['two_name']}({a['two_call'][0]}, "
            f"{a['two_call'][1]}));",
        )
    if shape == "js_default_params":
        return _lines(
            f"function {a['name']}(who, {a['param']} = {_q(a['fallback'])}) {{",
            f"  return `${{{a['param']}}} ${{who}}`;",
            "}",
            "",
            f"console.log({a['name']}({_q(a['first'])}));",
            f"console.log({a['name']}({_q(a['second'])}, {_q(a['given'])}));",
        )
    if shape == "js_optional_chain":
        return _lines(
            f"const found = {{ name: {_q(a['name'])}, "
            f"home: {{ {a['field']}: {_q(a['value'])} }} }};",
            f"const missing = {{ name: {_q(a['other'])} }};",
            "",
            f"console.log(found.home?.{a['field']});",
            f"console.log(missing.home?.{a['field']} ?? {_q(a['fallback'])});",
            f"console.log(missing.{a['number_field']} ?? {a['number']});",
        )
    if shape == "js_map_set":
        pairs = ", ".join(f"[{_q(k)}, {v}]" for k, v in a["pairs"])
        return _lines(
            "const seen = new Set([" + _nums(a["items"]) + "]);",
            f"const scores = new Map([{pairs}]);",
            "",
            "console.log(seen.size);",
            f"console.log(scores.get({_q(a['pairs'][0][0])}));",
            'console.log([...seen].join(", "));',
        )
    raise KeyError(shape)


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "javascript":
        return None
    return _js(shape, args)


# ── What each of them prints ─────────────────────────────────

_TOOLS = {"sum": sum, "len": len, "max": max, "min": min, "abs": abs}


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "js_template":
        lines = [
            f"{a['name']} is {a['age']}",
            f"{a['name']} will be {a['age'] + a['ahead']}",
        ]
    elif shape == "js_map":
        changed = [value(a["expr"], {"n": n, **_TOOLS}) for n in a["items"]]
        lines = [", ".join(str(n) for n in changed), str(len(changed))]
    elif shape == "js_filter":
        kept = [n for n in a["items"] if value(a["test"], {"n": n, **_TOOLS})]
        if not kept or len(kept) == len(a["items"]):
            # A filter that keeps everything or nothing shows nothing.
            raise ValueError("the filter must drop some but not all")
        lines = [", ".join(str(n) for n in kept), str(len(kept))]
    elif shape == "js_reduce":
        total = a["start"]
        for n in a["items"]:
            total = value(a["step"], {"sum": total, "n": n})
        lines = [str(total), str(max(a["items"]))]
    elif shape == "js_destructure":
        first, second = a["values"]
        head, tail = a["pair"]
        lines = [str(first + second), str(head + tail), f"{first} {tail}"]
    elif shape == "js_spread":
        joined = list(a["first"]) + list(a["second"])
        lines = [", ".join(str(n) for n in joined), str(sum(joined))]
    elif shape == "js_arrow":
        one = value(a["one_expr"], {"n": a["one_call"], **_TOOLS})
        two = value(
            a["two_expr"],
            {"a": a["two_call"][0], "b": a["two_call"][1], **_TOOLS},
        )
        lines = [str(one), str(two)]
    elif shape == "js_default_params":
        lines = [
            f"{a['fallback']} {a['first']}",
            f"{a['given']} {a['second']}",
        ]
    elif shape == "js_optional_chain":
        # The first reaches through; the second finds nothing and falls back.
        lines = [a["value"], a["fallback"], str(a["number"])]
    elif shape == "js_map_set":
        seen: list[int] = []
        for n in a["items"]:
            if n not in seen:
                seen.append(n)
        if len(seen) == len(a["items"]):
            raise ValueError("the set must collapse a duplicate")
        lines = [
            str(len(seen)),
            str(dict(a["pairs"])[a["pairs"][0][0]]),
            ", ".join(str(n) for n in seen),
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
