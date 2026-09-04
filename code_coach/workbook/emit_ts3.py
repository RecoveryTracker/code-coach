"""TypeScript-only shapes, third batch: the type system as a tool you use
rather than a thing you satisfy.

Where the second batch narrowed values, these mostly compute types. `as
const` freezes a literal so its type is the value rather than the kind of
thing it is. Template literal types build strings at compile time. Indexed
access reads a field's type out of a shape. `never` turns a forgotten case
into a compile error rather than a silent fallthrough at three in the
morning. Assertion functions narrow and throw in one move.

Two of these are worth the page on their own. The exhaustive switch (page
106) is the single most useful trick in the language: add a member to a
union and every switch that forgot it stops compiling. And the assertion
function (page 109) is the one people write by hand for years without
knowing the compiler will follow it.

Every page prints. A type that never reaches run time is a type the suite
can only check once, and checking twice is the point of this workbook.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q
from code_coach.workbook.emit_ts import check_type_name, _check_name

LANGUAGES: tuple[str, ...] = ("typescript",)

SHAPES: tuple[Shape, ...] = (
    Shape("ts_as_const", "a literal frozen into its own type"),
    Shape("ts_template_type", "a type built out of string pieces"),
    Shape("ts_indexed_access", "borrowing a field's type by name"),
    Shape("ts_record_type", "a table typed by its keys and values"),
    Shape("ts_function_type", "a function's shape, written down once"),
    Shape("ts_never_exhaustive", "a switch that cannot forget a case"),
    Shape("ts_abstract_class", "a base that refuses to be built"),
    Shape("ts_generic_default", "a type parameter with a fallback"),
    Shape("ts_assert_fn", "a check the compiler narrows on"),
    Shape("ts_awaited", "the type inside a promise"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(str(n) for n in items)


def _words(items) -> str:
    return ", ".join(_q(w) for w in items)


# ── 101. as const ────────────────────────────────────────────


def _as_const(a: dict) -> str:
    check_type_name(a["type_name"])
    return _lines(
        f"const {a['const_name']} = "
        f"[{_words(a['members'])}] as const;",
        "",
        f"type {a['type_name']} = (typeof {a['const_name']})[number];",
        "",
        f"const chosen: {a['type_name']} = {_q(a['chosen'])};",
        "",
        f"console.log({a['const_name']}.length);",
        f"console.log({a['const_name']}[0]);",
        "console.log(chosen);",
    )


# ── 102. Template literal types ──────────────────────────────


def _template_type(a: dict) -> str:
    check_type_name(a["type_name"])
    return _lines(
        f'type {a["type_name"]} = `{a["prefix"]}${{string}}`;',
        "",
        f"const {a['const_name']}: {a['type_name']} = "
        f"{_q(a['prefix'] + a['tail'])};",
        "",
        f"function {a['func']}(name: string): {a['type_name']} {{",
        f'  return `{a["prefix"]}${{name}}`;',
        "}",
        "",
        f"console.log({a['const_name']});",
        f"console.log({a['func']}({_q(a['made'])}));",
    )


# ── 103. Indexed access types ────────────────────────────────


def _indexed_access(a: dict) -> str:
    check_type_name(a["cls"])
    return _lines(
        f"interface {a['cls']} {{",
        f"  {a['text_field']}: string;",
        f"  {a['number_field']}: number;",
        "}",
        "",
        f'type Named = {a["cls"]}["{a["text_field"]}"];',
        f'type Counted = {a["cls"]}["{a["number_field"]}"];',
        "",
        f"const label: Named = {_q(a['text_value'])};",
        f"const total: Counted = {a['number_value']};",
        "",
        "console.log(label);",
        "console.log(total);",
        "console.log(typeof total);",
    )


# ── 104. Record ──────────────────────────────────────────────


def _record_type(a: dict) -> str:
    pairs = ", ".join(f"{k}: {v}" for k, v in a["entries"])
    keys = " | ".join(_q(k) for k, _ in a["entries"])
    return _lines(
        f"type Key = {keys};",
        "",
        f"const {a['const_name']}: Record<Key, number> = "
        f"{{ {pairs} }};",
        "",
        f"function {a['func']}(key: Key): number {{",
        f"  return {a['const_name']}[key];",
        "}",
        "",
        f"console.log({a['func']}({_q(a['asked'])}));",
        f"console.log(Object.keys({a['const_name']}).length);",
    )


# ── 105. Function types ──────────────────────────────────────


def _function_type(a: dict) -> str:
    check_type_name(a["type_name"])
    return _lines(
        f"type {a['type_name']} = (value: number) => number;",
        "",
        f"const {a['first_name']}: {a['type_name']} = "
        f"(value) => {a['first_expr']};",
        f"const {a['second_name']}: {a['type_name']} = "
        f"(value) => {a['second_expr']};",
        "",
        f"function apply_to(fn: {a['type_name']}, value: number): number {{",
        "  return fn(value);",
        "}",
        "",
        f"console.log(apply_to({a['first_name']}, {a['number']}));",
        f"console.log(apply_to({a['second_name']}, {a['number']}));",
    )


# ── 106. never and the exhaustive switch ─────────────────────


def _never_exhaustive(a: dict) -> str:
    check_type_name(a["type_name"])
    members = " | ".join(_q(m) for m, _ in a["cases"])
    body = []
    for member, says in a["cases"]:
        body.append(f"    case {_q(member)}:")
        body.append(f"      return {_q(says)};")
    return _lines(
        f"type {a['type_name']} = {members};",
        "",
        f"function {a['func']}(value: {a['type_name']}): string {{",
        "  switch (value) {",
        *body,
        "    default: {",
        "      const missed: never = value;",
        "      return missed;",
        "    }",
        "  }",
        "}",
        "",
        *[
            f"console.log({a['func']}({_q(member)}));"
            for member, _ in a["cases"]
        ],
    )


# ── 107. Abstract classes ────────────────────────────────────


def _abstract_class(a: dict) -> str:
    check_type_name(a["base"])
    check_type_name(a["sub"])
    return _lines(
        f"abstract class {a['base']} {{",
        f"  abstract {a['method']}(): string;",
        "",
        "  describe(): string {",
        f"    return `{a['label']} ${{this.{a['method']}()}}`;",
        "  }",
        "}",
        "",
        f"class {a['sub']} extends {a['base']} {{",
        f"  {a['method']}(): string {{",
        f"    return {_q(a['says'])};",
        "  }",
        "}",
        "",
        f"const thing = new {a['sub']}();",
        f"console.log(thing.{a['method']}());",
        "console.log(thing.describe());",
        f"console.log(thing instanceof {a['base']});",
    )


# ── 108. Generic defaults ────────────────────────────────────


def _generic_default(a: dict) -> str:
    check_type_name(a["cls"])
    return _lines(
        f"class {a['cls']}<T = string> {{",
        "  constructor(private readonly value: T) {}",
        "",
        "  get(): T {",
        "    return this.value;",
        "  }",
        "}",
        "",
        f"const plain = new {a['cls']}({_q(a['text'])});",
        f"const counted = new {a['cls']}<number>({a['number']});",
        "",
        "console.log(plain.get());",
        "console.log(counted.get());",
        "console.log(typeof plain.get());",
    )


# ── 109. Assertion functions ─────────────────────────────────


def _assert_fn(a: dict) -> str:
    _check_name(a["func"])
    return _lines(
        f"function {a['func']}(value: unknown): asserts value is number {{",
        '  if (typeof value !== "number") {',
        f"    throw new Error({_q(a['complaint'])});",
        "  }",
        "}",
        "",
        f"function {a['user']}(value: unknown): number {{",
        f"  {a['func']}(value);",
        f"  return {a['expr']};",
        "}",
        "",
        f"console.log({a['user']}({a['number']}));",
        "try {",
        f"  {a['user']}({_q(a['bad'])});",
        "} catch (caught) {",
        "  console.log((caught as Error).message);",
        "}",
    )


# ── 110. Awaited ─────────────────────────────────────────────


def _awaited(a: dict) -> str:
    check_type_name(a["type_name"])
    return _lines(
        f"async function {a['func']}(value: number): Promise<number> {{",
        f"  return {a['expr']};",
        "}",
        "",
        f"type {a['type_name']} = Awaited<ReturnType<typeof {a['func']}>>;",
        "",
        "async function main(): Promise<void> {",
        f"  const first: {a['type_name']} = await {a['func']}"
        f"({a['values'][0]});",
        f"  const second: {a['type_name']} = await {a['func']}"
        f"({a['values'][1]});",
        "  console.log(first);",
        "  console.log(second);",
        "  console.log(typeof first);",
        "}",
        "",
        "main();",
    )


_BUILDERS = {
    "ts_as_const": _as_const,
    "ts_template_type": _template_type,
    "ts_indexed_access": _indexed_access,
    "ts_record_type": _record_type,
    "ts_function_type": _function_type,
    "ts_never_exhaustive": _never_exhaustive,
    "ts_abstract_class": _abstract_class,
    "ts_generic_default": _generic_default,
    "ts_assert_fn": _assert_fn,
    "ts_awaited": _awaited,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    if build is None:
        return None
    return build(args)


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "ts_as_const":
        if a["chosen"] not in a["members"]:
            # The whole point is that the type is the members themselves,
            # so a value outside them would not compile.
            raise ValueError("the chosen value must be one of the members")
        lines = [str(len(a["members"])), a["members"][0], a["chosen"]]
    elif shape == "ts_template_type":
        lines = [a["prefix"] + a["tail"], a["prefix"] + a["made"]]
    elif shape == "ts_indexed_access":
        lines = [a["text_value"], str(a["number_value"]), "number"]
    elif shape == "ts_record_type":
        keys = [k for k, _ in a["entries"]]
        if a["asked"] not in keys:
            raise ValueError("the key asked for must be in the record")
        found = dict(a["entries"])[a["asked"]]
        lines = [str(found), str(len(keys))]
    elif shape == "ts_function_type":
        first = value(a["first_expr"], {"value": a["number"]})
        second = value(a["second_expr"], {"value": a["number"]})
        if first == second:
            raise ValueError("the two functions must differ")
        lines = [str(first), str(second)]
    elif shape == "ts_never_exhaustive":
        if len(a["cases"]) < 2:
            raise ValueError("a switch needs more than one case")
        lines = [says for _, says in a["cases"]]
    elif shape == "ts_abstract_class":
        lines = [a["says"], f"{a['label']} {a['says']}", "true"]
    elif shape == "ts_generic_default":
        lines = [a["text"], str(a["number"]), "string"]
    elif shape == "ts_assert_fn":
        lines = [
            str(value(a["expr"], {"value": a["number"]})),
            a["complaint"],
        ]
    elif shape == "ts_awaited":
        lines = [
            str(value(a["expr"], {"value": a["values"][0]})),
            str(value(a["expr"], {"value": a["values"][1]})),
            "number",
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
