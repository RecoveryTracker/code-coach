"""TypeScript-only shapes, second batch: narrowing properly, and types
that compute.

The rest of narrowing - the `in` operator, instanceof, and a type guard
you write yourself. unknown, which is any with the safety left on. keyof
and index signatures. Generic constraints. Then the part of TypeScript
that is its own small language: mapped types, conditional types with
infer, and satisfies.

Every page still prints something, because a type that is never used at
run time is a type that cannot be checked twice.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q
from code_coach.workbook.emit_ts import check_type_name

LANGUAGES: tuple[str, ...] = ("typescript",)

SHAPES: tuple[Shape, ...] = (
    Shape("ts_narrow_in", "telling two shapes apart by a key"),
    Shape("ts_type_guard", "a check the compiler believes"),
    Shape("ts_unknown", "a value you have to ask about first"),
    Shape("ts_keyof", "the keys of a type, as a type"),
    Shape("ts_constraint", "a generic that demands something"),
    Shape("ts_mapped", "a type built from every key of another"),
    Shape("ts_conditional", "a type that chooses, and one that unwraps"),
    Shape("ts_enum", "an enum, and the union that usually beats it"),
    Shape("ts_overload", "one function, two signatures"),
    Shape("ts_satisfies", "checked against a type without becoming it"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(str(n) for n in items)


def _narrow_in(a: dict) -> str:
    check_type_name(a["first_cls"])
    check_type_name(a["second_cls"])
    return _lines(
        f"interface {a['first_cls']} {{",
        f"  {a['first_field']}: string;",
        "}",
        "",
        f"interface {a['second_cls']} {{",
        f"  {a['second_field']}: string;",
        "}",
        "",
        f"function {a['func']}"
        f"(thing: {a['first_cls']} | {a['second_cls']}): string {{",
        f'  if ("{a["first_field"]}" in thing) {{',
        f"    return thing.{a['first_field']};",
        "  }",
        f"  return thing.{a['second_field']};",
        "}",
        "",
        f"console.log({a['func']}({{ {a['first_field']}: "
        f"{_q(a['first_says'])} }}));",
        f"console.log({a['func']}({{ {a['second_field']}: "
        f"{_q(a['second_says'])} }}));",
    )


def _type_guard(a: dict) -> str:
    check_type_name(a["first_cls"])
    check_type_name(a["second_cls"])
    return _lines(
        f"interface {a['first_cls']} {{",
        f"  {a['first_field']}: number;",
        "}",
        "",
        f"interface {a['second_cls']} {{",
        f"  {a['second_field']}: number;",
        "}",
        "",
        f"function {a['guard']}"
        f"(thing: {a['first_cls']} | {a['second_cls']}): "
        f"thing is {a['first_cls']} {{",
        f"  return (thing as {a['first_cls']})."
        f"{a['first_field']} !== undefined;",
        "}",
        "",
        f"function {a['func']}"
        f"(thing: {a['first_cls']} | {a['second_cls']}): string {{",
        f"  if ({a['guard']}(thing)) {{",
        f"    return `{a['first_field']} ${{thing.{a['first_field']}}}`;",
        "  }",
        f"  return `{a['second_field']} ${{thing.{a['second_field']}}}`;",
        "}",
        "",
        f"console.log({a['func']}({{ {a['first_field']}: "
        f"{a['values'][0]} }}));",
        f"console.log({a['func']}({{ {a['second_field']}: "
        f"{a['values'][1]} }}));",
    )


def _unknown(a: dict) -> str:
    return _lines(
        f"function {a['func']}(value: unknown): number {{",
        '  if (typeof value === "string") {',
        "    return value.length;",
        "  }",
        "  if (Array.isArray(value)) {",
        "    return value.length;",
        "  }",
        f"  return {a['fallback']};",
        "}",
        "",
        f"console.log({a['func']}({_q(a['word'])}));",
        f"console.log({a['func']}([{_nums(a['items'])}]));",
        f"console.log({a['func']}({a['number']}));",
    )


def _keyof(a: dict) -> str:
    return _lines(
        f"interface {a['table']} {{",
        "  [name: string]: number;",
        "}",
        "",
        f"interface {a['cls']} {{",
        f"  {a['first']}: string;",
        f"  {a['second']}: number;",
        "}",
        "",
        f"type Field = keyof {a['cls']};",
        "",
        f"const scores: {a['table']} = {{ {a['name']}: {a['number']} }};",
        f"const field: Field = {_q(a['second'])};",
        "",
        f"function pick(thing: {a['cls']}, key: Field): string | number {{",
        "  return thing[key];",
        "}",
        "",
        f"console.log(scores.{a['name']});",
        "console.log(field);",
        f"console.log(pick({{ {a['first']}: {_q(a['other'])}, "
        f"{a['second']}: {a['number']} }}, {_q(a['first'])}));",
    )


def _constraint(a: dict) -> str:
    return _lines(
        f"function {a['func']}<T extends {{ length: number }}>"
        "(a: T, b: T): T {",
        "  return a.length >= b.length ? a : b;",
        "}",
        "",
        f"console.log({a['func']}({_q(a['long'])}, {_q(a['short'])}));",
        f"console.log({a['func']}([{_nums(a['many'])}], "
        f"[{_nums(a['few'])}]).length);",
    )


def _mapped(a: dict) -> str:
    return _lines(
        f"interface {a['cls']} {{",
        f"  {a['first']}: string;",
        f"  {a['second']}: number;",
        "}",
        "",
        "type Flags<T> = { [K in keyof T]: boolean };",
        f"type {a['cls']}Flags = Flags<{a['cls']}>;",
        "",
        f"const set: {a['cls']}Flags = {{ {a['first']}: true, "
        f"{a['second']}: false }};",
        "",
        f"console.log(set.{a['first']});",
        f"console.log(set.{a['second']});",
        'console.log(Object.keys(set).sort().join(", "));',
    )


def _conditional(a: dict) -> str:
    return _lines(
        "type Unwrap<T> = T extends Array<infer U> ? U : T;",
        "",
        "type Inner = Unwrap<number[]>;",
        "type Plain = Unwrap<string>;",
        "",
        f"const inner: Inner = {a['number']};",
        f"const plain: Plain = {_q(a['word'])};",
        "",
        "console.log(inner);",
        "console.log(plain);",
        f"console.log(inner + {a['added']});",
    )


def _enum(a: dict) -> str:
    return _lines(
        f"enum {a['cls']} {{",
        f"  {a['first_name']} = {_q(a['first_value'])},",
        f"  {a['second_name']} = {_q(a['second_value'])},",
        "}",
        "",
        f"type {a['alias']} = {_q(a['first_value'])} | "
        f"{_q(a['second_value'])};",
        "",
        f"const chosen: {a['cls']} = {a['cls']}.{a['first_name']};",
        f"const plain: {a['alias']} = {_q(a['first_value'])};",
        "",
        "console.log(chosen);",
        f"console.log({a['cls']}.{a['second_name']});",
        "console.log(plain);",
        "console.log(chosen === plain);",
    )


def _overload(a: dict) -> str:
    return _lines(
        f"function {a['func']}(value: number): number;",
        f"function {a['func']}(value: string): string;",
        f"function {a['func']}(value: number | string): number | string {{",
        '  if (typeof value === "number") {',
        f"    return value * {a['times']};",
        "  }",
        "  return value.toUpperCase();",
        "}",
        "",
        f"console.log({a['func']}({a['number']}));",
        f"console.log({a['func']}({_q(a['word'])}));",
    )


def _satisfies(a: dict) -> str:
    return _lines(
        "type Config = Record<string, string | number>;",
        "",
        "const settings = {",
        f"  {a['text_key']}: {_q(a['text_value'])},",
        f"  {a['number_key']}: {a['number_value']},",
        "} satisfies Config;",
        "",
        f"console.log(settings.{a['text_key']}.toUpperCase());",
        f"console.log(settings.{a['number_key']} + {a['added']});",
    )


_TS = {
    "ts_narrow_in": _narrow_in,
    "ts_type_guard": _type_guard,
    "ts_unknown": _unknown,
    "ts_keyof": _keyof,
    "ts_constraint": _constraint,
    "ts_mapped": _mapped,
    "ts_conditional": _conditional,
    "ts_enum": _enum,
    "ts_overload": _overload,
    "ts_satisfies": _satisfies,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "typescript":
        return None
    return _TS[shape](args)


# ── What each of them prints ─────────────────────────────────


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "ts_narrow_in":
        lines = [a["first_says"], a["second_says"]]
    elif shape == "ts_type_guard":
        first, second = a["values"]
        lines = [
            f"{a['first_field']} {first}",
            f"{a['second_field']} {second}",
        ]
    elif shape == "ts_unknown":
        lines = [
            str(len(a["word"])),
            str(len(a["items"])),
            # A number is neither, so the fallback is what comes back.
            str(a["fallback"]),
        ]
    elif shape == "ts_keyof":
        lines = [str(a["number"]), a["second"], a["other"]]
    elif shape == "ts_constraint":
        if len(a["long"]) <= len(a["short"]):
            raise ValueError("the first word must be the longer one")
        if len(a["many"]) <= len(a["few"]):
            raise ValueError("the first array must be the longer one")
        lines = [a["long"], str(len(a["many"]))]
    elif shape == "ts_mapped":
        lines = [
            "true",
            "false",
            ", ".join(sorted((a["first"], a["second"]))),
        ]
    elif shape == "ts_conditional":
        lines = [
            str(a["number"]),
            a["word"],
            str(a["number"] + a["added"]),
        ]
    elif shape == "ts_enum":
        # A string enum member is its value at run time, so it compares
        # equal to the plain string - which the last line shows.
        lines = [
            a["first_value"],
            a["second_value"],
            a["first_value"],
            "true",
        ]
    elif shape == "ts_overload":
        lines = [str(a["number"] * a["times"]), a["word"].upper()]
    elif shape == "ts_satisfies":
        lines = [
            a["text_value"].upper(),
            str(a["number_value"] + a["added"]),
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
