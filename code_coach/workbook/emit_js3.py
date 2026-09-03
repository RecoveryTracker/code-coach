"""JavaScript-only shapes, third batch: the class machinery, and the traps
that come from JavaScript being JavaScript.

slice against splice, which is the mutation question in one page.
Generators. Getters and setters. Static members. extends and super.
Symbol.iterator. Named groups in a regular expression. Then three pages
that are pure JavaScript: how numbers come out of strings, what counts
as true, and what happens to this when a method is passed around.

Same rule as before: nothing prints a raw array or object, because Node
puts spaces inside the brackets. Everything goes through join.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_slice_splice", "the one that copies and the one that cuts"),
    Shape("js_generator", "a function that hands values back as it goes"),
    Shape("js_getter_setter", "a field that runs code"),
    Shape("js_static", "something the class owns rather than the object"),
    Shape("js_extends", "a class built on another, and super"),
    Shape("js_iterator", "making your own class work in for...of"),
    Shape("js_regex", "named groups, and replacing by pattern"),
    Shape("js_number_parse", "getting a number out of a string"),
    Shape("js_truthy", "what counts as true"),
    Shape("js_bind", "this, and what happens when you lose it"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(str(n) for n in items)


def _in_regex(gap: str) -> str:
    """The separator, safe to drop inside a regex literal.

    A regex literal is delimited by slashes, so an unescaped slash in the
    pattern ends it early and everything after is a syntax error. Node
    says so immediately; reading the data never would.
    """
    return gap.replace("/", "\\/")


def _js(shape: str, a: dict) -> str:
    if shape == "js_slice_splice":
        return _lines(
            "const numbers = [" + _nums(a["items"]) + "];",
            f"const taken = numbers.slice({a['start']}, {a['stop']});",
            "",
            'console.log(taken.join(", "));',
            'console.log(numbers.join(", "));',
            "",
            f"const cut = numbers.splice({a['start']}, {a['count']});",
            'console.log(cut.join(", "));',
            'console.log(numbers.join(", "));',
        )
    if shape == "js_generator":
        return _lines(
            f"function* {a['name']}(limit) {{",
            "  for (let n = 1; n <= limit; n += 1) {",
            f"    yield {a['expr']};",
            "  }",
            "}",
            "",
            f"for (const n of {a['name']}({a['limit']})) {{",
            "  console.log(n);",
            "}",
        )
    if shape == "js_getter_setter":
        return _lines(
            f"class {a['cls']} {{",
            f"  constructor({a['field']}) {{",
            f"    this._{a['field']} = {a['field']};",
            "  }",
            "",
            f"  get {a['field']}() {{",
            f"    return this._{a['field']};",
            "  }",
            "",
            f"  set {a['field']}(value) {{",
            f"    this._{a['field']} = value * {a['times']};",
            "  }",
            "}",
            "",
            f"const thing = new {a['cls']}({a['start']});",
            f"console.log(thing.{a['field']});",
            f"thing.{a['field']} = {a['given']};",
            f"console.log(thing.{a['field']});",
        )
    if shape == "js_static":
        made = "\n".join(f"new {a['cls']}();" for _ in range(a["times"]))
        return _lines(
            f"class {a['cls']} {{",
            f"  static {a['field']} = 0;",
            "",
            "  constructor() {",
            f"    {a['cls']}.{a['field']} += 1;",
            "  }",
            "",
            f"  static {a['method']}() {{",
            f"    return {a['cls']}.{a['field']};",
            "  }",
            "}",
            "",
            made,
            f"console.log({a['cls']}.{a['method']}());",
            f"console.log({a['cls']}.{a['field']});",
        )
    if shape == "js_extends":
        return _lines(
            f"class {a['base']} {{",
            "  constructor(name) {",
            "    this.name = name;",
            "  }",
            "",
            f"  {a['method']}() {{",
            f"    return `${{this.name}} {a['base_says']}`;",
            "  }",
            "}",
            "",
            f"class {a['sub']} extends {a['base']} {{",
            f"  {a['method']}() {{",
            f"    return `${{super.{a['method']}()}} {a['sub_says']}`;",
            "  }",
            "}",
            "",
            f"console.log(new {a['base']}({_q(a['names'][0])})"
            f".{a['method']}());",
            f"console.log(new {a['sub']}({_q(a['names'][1])})"
            f".{a['method']}());",
        )
    if shape == "js_iterator":
        return _lines(
            f"class {a['cls']} {{",
            "  constructor(limit) {",
            "    this.limit = limit;",
            "  }",
            "",
            "  *[Symbol.iterator]() {",
            "    for (let n = 1; n <= this.limit; n += 1) {",
            f"      yield {a['expr']};",
            "    }",
            "  }",
            "}",
            "",
            f'console.log([...new {a["cls"]}({a["limit"]})].join(", "));',
            f"for (const n of new {a['cls']}({a['smaller']})) {{",
            "  console.log(n);",
            "}",
        )
    if shape == "js_regex":
        return _lines(
            f"const text = {_q(a['text'])};",
            f"const pattern = /(?<{a['first']}>\\w+){_in_regex(a['gap'])}"
            f"(?<{a['second']}>\\d+)/;",
            "const found = text.match(pattern);",
            "",
            f"console.log(found.groups.{a['first']});",
            f"console.log(found.groups.{a['second']});",
            f'console.log(text.replace(/\\d+/, {_q(a["instead"])}));',
        )
    if shape == "js_number_parse":
        return _lines(
            f"console.log(parseInt({_q(a['mixed'])}));",
            f"console.log(Number({_q(a['mixed'])}));",
            'console.log(Number(""));',
            f"console.log(({a['left']} + {a['right']}).toFixed(2));",
        )
    if shape == "js_truthy":
        shows = [f"console.log(Boolean({v}));" for v in a["values"]]
        return _lines(*shows)
    if shape == "js_bind":
        return _lines(
            f"const {a['name']} = {{",
            f"  {a['field']}: {a['value']},",
            f"  {a['method']}() {{",
            f"    return this.{a['field']};",
            "  },",
            "};",
            "",
            f"const loose = {a['name']}.{a['method']};",
            f"const bound = {a['name']}.{a['method']}.bind({a['name']});",
            "",
            f"console.log({a['name']}.{a['method']}());",
            "console.log(loose());",
            "console.log(bound());",
            f"console.log({a['name']}.{a['method']}"
            f".call({{ {a['field']}: {a['other']} }}));",
        )
    raise KeyError(shape)


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "javascript":
        return None
    return _js(shape, args)


# ── What each of them prints ─────────────────────────────────

_TOOLS = {"sum": sum, "len": len, "max": max, "min": min, "abs": abs}

# What Boolean() says about each of these, written out rather than worked
# out, because the whole page is that the answers are not guessable.
_TRUTH = {
    "0": "false",
    '""': "false",
    '"0"': "true",
    "[]": "true",
    "{}": "true",
    "null": "false",
    "undefined": "false",
    "NaN": "false",
    "-1": "true",
    '" "': "true",
    "1": "true",
    "[0]": "true",
}


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "js_slice_splice":
        items = list(a["items"])
        taken = items[a["start"] : a["stop"]]
        if not taken:
            raise ValueError("the slice must take something")
        lines = [
            ", ".join(str(n) for n in taken),
            # slice copied, so the original is untouched.
            ", ".join(str(n) for n in items),
        ]
        cut = items[a["start"] : a["start"] + a["count"]]
        left = items[: a["start"]] + items[a["start"] + a["count"] :]
        if not cut or not left:
            raise ValueError("the splice must cut some and leave some")
        lines.append(", ".join(str(n) for n in cut))
        lines.append(", ".join(str(n) for n in left))
    elif shape == "js_generator":
        lines = [
            str(value(a["expr"], {"n": n, **_TOOLS}))
            for n in range(1, a["limit"] + 1)
        ]
    elif shape == "js_getter_setter":
        lines = [str(a["start"]), str(a["given"] * a["times"])]
    elif shape == "js_static":
        lines = [str(a["times"]), str(a["times"])]
    elif shape == "js_extends":
        first, second = a["names"]
        lines = [
            f"{first} {a['base_says']}",
            f"{second} {a['base_says']} {a['sub_says']}",
        ]
    elif shape == "js_iterator":
        whole = [
            str(value(a["expr"], {"n": n, **_TOOLS}))
            for n in range(1, a["limit"] + 1)
        ]
        lines = [", ".join(whole)]
        lines += [
            str(value(a["expr"], {"n": n, **_TOOLS}))
            for n in range(1, a["smaller"] + 1)
        ]
    elif shape == "js_regex":
        word, number = a["text"].split(a["gap_plain"])
        lines = [word, number, word + a["gap_plain"] + a["instead"]]
    elif shape == "js_number_parse":
        digits = ""
        for ch in a["mixed"]:
            if ch.isdigit():
                digits += ch
            else:
                break
        if not digits or a["mixed"].isdigit():
            raise ValueError("the string must start with digits and go wrong")
        total = a["left"] + a["right"]
        lines = [digits, "NaN", "0", f"{total:.2f}"]
    elif shape == "js_truthy":
        lines = [_TRUTH[v] for v in a["values"]]
        if len(set(lines)) < 2:
            raise ValueError("the page must show both answers")
    elif shape == "js_bind":
        # loose() lost its object: this is not the object any more, so the
        # field is undefined.
        lines = [
            str(a["value"]),
            "undefined",
            str(a["value"]),
            str(a["other"]),
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
