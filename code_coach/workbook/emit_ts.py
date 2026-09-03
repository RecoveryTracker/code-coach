"""TypeScript-only shapes: the start of TypeScript's own intermediate tier.

The third book. Python went deep first, then JavaScript; TypeScript is
the natural next, because it is JavaScript with the part that catches
mistakes before you run anything.

Worth knowing about these pages: the runner type-checks rather than
merely stripping the types, so an annotation that does not hold stops
the exercise with a compiler error rather than running anyway. That is
the whole point of the language, and it means every page here is checked
twice - once by the compiler and once by comparing what it printed.

Same output rule as the JavaScript book: nothing prints a raw array or
object, because Node puts spaces inside the brackets.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("typescript",)

SHAPES: tuple[Shape, ...] = (
    Shape("ts_annotate", "saying what a variable and a function hold"),
    Shape("ts_interface", "a shape with a name"),
    Shape("ts_union_narrow", "one of two types, and telling them apart"),
    Shape("ts_optional", "a property that might not be there"),
    Shape("ts_tuple", "a fixed pair, and an array that cannot change"),
    Shape("ts_generic_fn", "a function that keeps the type it was given"),
    Shape("ts_generic_class", "a class that holds one type"),
    Shape("ts_literal", "a type that is one of these exact values"),
    Shape("ts_utility", "types built out of another type"),
    Shape("ts_discriminated", "a tag that tells the compiler which one"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(str(n) for n in items)


# A top-level declaration shares a namespace with the ambient globals the
# compiler already knows about, so a function called `opener` or `name`
# is a duplicate identifier rather than a shadowing. Only the ones likely
# to be reached for as a page's function name are listed; the compiler
# catches anything else on the first run.
_TAKEN = frozenset(
    {
        "name",
        "opener",
        "top",
        "self",
        "parent",
        "status",
        "length",
        "origin",
        "closed",
        "event",
        "location",
        "history",
        "screen",
        "frames",
        "navigator",
        "document",
        "window",
    }
)


def _check_name(name: str) -> str:
    if name in _TAKEN:
        raise ValueError(f"{name!r} is already a global in TypeScript")
    return name


# The same problem one level up. An interface declared with the name of a
# global type does not shadow it - it merges with it, so an object
# literal that satisfies your fields is reported as missing the global
# one's. The error names your interface, which makes it confusing.
_TAKEN_TYPES = frozenset(
    {
        "Text",
        "Image",
        "File",
        "Document",
        "Event",
        "Node",
        "Element",
        "Range",
        "Request",
        "Response",
        "Headers",
        "URL",
        "Blob",
        "Comment",
        "Selection",
        "Screen",
        "Location",
        "History",
        "Storage",
        "Worker",
        "Notification",
        "Map",
        "Set",
        "Date",
        "Error",
        "Promise",
        "Proxy",
        "Record",
        "Array",
        "Object",
        "String",
        "Number",
        "Boolean",
        "Symbol",
    }
)


def check_type_name(name: str) -> str:
    if name in _TAKEN_TYPES:
        raise ValueError(f"{name!r} is already a type in TypeScript")
    return name


def _annotate(a: dict) -> str:
    return _lines(
        f"const who: string = {_q(a['name'])};",
        f"const count: number = {a['count']};",
        "",
        f"function {_check_name(a['func'])}(name: string, "
        "times: number): string {",
        "  return `${name} ${times}`;",
        "}",
        "",
        f"console.log({a['func']}(who, count));",
        "console.log(typeof count);",
    )


def _interface(a: dict) -> str:
    return _lines(
        f"interface {a['cls']} {{",
        f"  {a['first']}: number;",
        f"  {a['second']}: number;",
        "}",
        "",
        f"type {a['alias']} = string;",
        "",
        f"const thing: {a['cls']} = {{ {a['first']}: {a['values'][0]}, "
        f"{a['second']}: {a['values'][1]} }};",
        f"const tag: {a['alias']} = {_q(a['tag'])};",
        "",
        f"console.log(thing.{a['first']} + thing.{a['second']});",
        "console.log(tag);",
    )


def _union_narrow(a: dict) -> str:
    return _lines(
        f"function {_check_name(a['func'])}"
        "(value: string | number): string {",
        '  if (typeof value === "number") {',
        f"    return `{a['number_word']} ${{value * {a['times']}}}`;",
        "  }",
        f"  return `{a['text_word']} ${{value.toUpperCase()}}`;",
        "}",
        "",
        f"console.log({a['func']}({a['number']}));",
        f"console.log({a['func']}({_q(a['text'])}));",
    )


def _optional(a: dict) -> str:
    return _lines(
        f"interface {a['cls']} {{",
        f"  {a['always']}: string;",
        f"  {a['maybe']}?: number;",
        "}",
        "",
        f"function describe(thing: {a['cls']}): string {{",
        f"  return `${{thing.{a['always']}}}:"
        f"${{thing.{a['maybe']} ?? {a['fallback']}}}`;",
        "}",
        "",
        f"console.log(describe({{ {a['always']}: {_q(a['value'])}, "
        f"{a['maybe']}: {a['given']} }}));",
        f"console.log(describe({{ {a['always']}: {_q(a['value'])} }}));",
    )


def _tuple(a: dict) -> str:
    return _lines(
        f"const pair: [string, number] = [{_q(a['name'])}, {a['count']}];",
        f"const fixed: readonly number[] = [{_nums(a['items'])}];",
        "",
        "const [who, many] = pair;",
        "",
        "console.log(who);",
        "console.log(many);",
        "console.log(fixed.length);",
    )


def _generic_fn(a: dict) -> str:
    return _lines(
        f"function {_check_name(a['func'])}<T>(items: T[]): T {{",
        "  return items[0];",
        "}",
        "",
        f"console.log({a['func']}<number>([{_nums(a['numbers'])}]));",
        f"console.log({a['func']}<string>"
        f"([{', '.join(_q(w) for w in a['words'])}]));",
    )


def _generic_class(a: dict) -> str:
    return _lines(
        f"class {a['cls']}<T> {{",
        "  constructor(private item: T) {}",
        "",
        f"  {a['method']}(): T {{",
        "    return this.item;",
        "  }",
        "}",
        "",
        f"console.log(new {a['cls']}<number>({a['number']})"
        f".{a['method']}());",
        f"console.log(new {a['cls']}<string>({_q(a['word'])})"
        f".{a['method']}());",
    )


def _literal(a: dict) -> str:
    choices = " | ".join(_q(c) for c in a["choices"])
    return _lines(
        f"type {a['alias']} = {choices};",
        "",
        f"const chosen: {a['alias']} = {_q(a['choices'][0])};",
        f"const sizes = [{_nums(a['items'])}] as const;",
        "",
        "console.log(chosen);",
        "console.log(sizes.length);",
        "console.log(sizes[0]);",
    )


def _utility(a: dict) -> str:
    return _lines(
        f"interface {a['cls']} {{",
        f"  {a['first']}: string;",
        f"  {a['second']}: number;",
        f"  {a['third']}: string;",
        "}",
        "",
        f"type Draft = Partial<{a['cls']}>;",
        f'type JustOne = Pick<{a["cls"]}, "{a["first"]}">;',
        f'type Without = Omit<{a["cls"]}, "{a["third"]}">;',
        "type Counts = Record<string, number>;",
        "",
        f"const draft: Draft = {{ {a['first']}: {_q(a['name'])} }};",
        f"const one: JustOne = {{ {a['first']}: {_q(a['other'])} }};",
        f"const without: Without = {{ {a['first']}: {_q(a['name'])}, "
        f"{a['second']}: {a['number']} }};",
        f"const counts: Counts = {{ {a['name']}: {a['number']} }};",
        "",
        f"console.log(draft.{a['first']});",
        f"console.log(one.{a['first']});",
        f"console.log(without.{a['second']});",
        f"console.log(counts.{a['name']});",
    )


def _discriminated(a: dict) -> str:
    return _lines(
        f"type {a['alias']} =",
        f'  | {{ kind: "{a["first"]}"; {a["first_field"]}: number }}',
        f'  | {{ kind: "{a["second"]}"; {a["second_field"]}: number }};',
        "",
        f"function {a['func']}(thing: {a['alias']}): number {{",
        "  switch (thing.kind) {",
        f'    case "{a["first"]}":',
        f"      return thing.{a['first_field']} * "
        f"thing.{a['first_field']};",
        f'    case "{a["second"]}":',
        f"      return thing.{a['second_field']} * "
        f"{a['second_times']};",
        "  }",
        "}",
        "",
        f'console.log({a["func"]}({{ kind: "{a["first"]}", '
        f'{a["first_field"]}: {a["values"][0]} }}));',
        f'console.log({a["func"]}({{ kind: "{a["second"]}", '
        f'{a["second_field"]}: {a["values"][1]} }}));',
    )


_TS = {
    "ts_annotate": _annotate,
    "ts_interface": _interface,
    "ts_union_narrow": _union_narrow,
    "ts_optional": _optional,
    "ts_tuple": _tuple,
    "ts_generic_fn": _generic_fn,
    "ts_generic_class": _generic_class,
    "ts_literal": _literal,
    "ts_utility": _utility,
    "ts_discriminated": _discriminated,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "typescript":
        return None
    return _TS[shape](args)


# ── What each of them prints ─────────────────────────────────


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "ts_annotate":
        lines = [f"{a['name']} {a['count']}", "number"]
    elif shape == "ts_interface":
        lines = [str(sum(a["values"])), a["tag"]]
    elif shape == "ts_union_narrow":
        lines = [
            f"{a['number_word']} {a['number'] * a['times']}",
            f"{a['text_word']} {a['text'].upper()}",
        ]
    elif shape == "ts_optional":
        lines = [
            f"{a['value']}:{a['given']}",
            # The property is missing, so ?? reaches for the fallback.
            f"{a['value']}:{a['fallback']}",
        ]
    elif shape == "ts_tuple":
        lines = [a["name"], str(a["count"]), str(len(a["items"]))]
    elif shape == "ts_generic_fn":
        lines = [str(a["numbers"][0]), a["words"][0]]
    elif shape == "ts_generic_class":
        lines = [str(a["number"]), a["word"]]
    elif shape == "ts_literal":
        lines = [
            a["choices"][0],
            str(len(a["items"])),
            str(a["items"][0]),
        ]
    elif shape == "ts_utility":
        lines = [a["name"], a["other"], str(a["number"]), str(a["number"])]
    elif shape == "ts_discriminated":
        first, second = a["values"]
        lines = [str(first * first), str(second * a["second_times"])]
    else:
        raise KeyError(shape)
    return NL.join(lines)
