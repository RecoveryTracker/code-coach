"""TypeScript-only shapes, sixth batch: reading types off things that
already exist, and the escape hatches.

Parameters and ReturnType read a function's own types back out. instanceof
narrows between classes the way typeof narrows between primitives. Optional
chaining short-circuits a whole expression, including a call and an index.
And `as unknown as` is the double assertion that gets round the compiler
entirely, which is on a page here precisely so it can be labelled as the
last resort it is.

Page 135's Result is the one to keep. A generic discriminated union with an
ok flag gives you errors as values rather than exceptions, and the compiler
will not let you read the value until you have checked the flag.

House rules, same as the last batch: nothing prints a raw array or object,
because node renders one with spaces and the expected output is computed in
Python; and no emitted identifier may be one a row supplies, so the locals
here are `made_here` and `held_here`.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q
from code_coach.workbook.emit_ts import check_type_name

LANGUAGES: tuple[str, ...] = ("typescript",)

SHAPES: tuple[Shape, ...] = (
    Shape("ts_parameters", "a function's argument types, read back out"),
    Shape("ts_instanceof", "telling two classes apart"),
    Shape("ts_optional_chain", "a whole expression that gives up early"),
    Shape("ts_double_assert", "the escape hatch, and why it is one"),
    Shape("ts_result_type", "errors as values, checked before they are read"),
    Shape("ts_omit_override", "changing one field's type"),
    Shape("ts_template_keys", "an index signature with a shaped key"),
    Shape("ts_generic_impl", "a generic class matching a generic interface"),
    Shape("ts_class_typeof", "the type of the class itself"),
    Shape("ts_deep_conditional", "a conditional type that recurses"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(str(n) for n in items)


# ── 131. Parameters and ReturnType ───────────────────────────


def _parameters(a: dict) -> str:
    return _lines(
        f"function {a['func']}(word: string, count: number): string {{",
        "  return word.repeat(count);",
        "}",
        "",
        f"type Args = Parameters<typeof {a['func']}>;",
        f"type Made = ReturnType<typeof {a['func']}>;",
        "",
        f"const held_here: Args = [{_q(a['word'])}, {a['count']}];",
        f"const made_here: Made = {a['func']}(...held_here);",
        "",
        "console.log(made_here);",
        "console.log(held_here[1]);",
        "console.log(made_here.length);",
    )


# ── 132. instanceof ──────────────────────────────────────────


def _instanceof(a: dict) -> str:
    check_type_name(a["first"])
    check_type_name(a["second"])
    return _lines(
        f"class {a['first']} {{",
        f"  constructor(readonly {a['first_field']}: string) {{}}",
        "}",
        "",
        f"class {a['second']} {{",
        f"  constructor(readonly {a['second_field']}: number) {{}}",
        "}",
        "",
        f"function {a['func']}(thing: {a['first']} | {a['second']}): "
        "string {",
        f"  if (thing instanceof {a['first']}) {{",
        f"    return thing.{a['first_field']};",
        "  }",
        f"  return String(thing.{a['second_field']});",
        "}",
        "",
        f"console.log({a['func']}(new {a['first']}"
        f"({_q(a['first_value'])})));",
        f"console.log({a['func']}(new {a['second']}({a['second_value']})));",
    )


# ── 133. Optional chaining ───────────────────────────────────


def _optional_chain(a: dict) -> str:
    return _lines(
        f"interface {a['cls']} {{",
        f"  {a['field']}?: {{",
        f"    {a['inner']}: string;",
        "    count?: () => number;",
        "  };",
        "}",
        "",
        f"const full: {a['cls']} = {{",
        f"  {a['field']}: {{",
        f"    {a['inner']}: {_q(a['value'])},",
        f"    count: () => {a['number']},",
        "  },",
        "};",
        f"const bare: {a['cls']} = {{}};",
        "",
        f"console.log(full.{a['field']}?.{a['inner']} ?? "
        f"{_q(a['missing'])});",
        f"console.log(bare.{a['field']}?.{a['inner']} ?? "
        f"{_q(a['missing'])});",
        f"console.log(full.{a['field']}?.count?.() ?? 0);",
        f"console.log(bare.{a['field']}?.count?.() ?? 0);",
    )


# ── 134. The double assertion ────────────────────────────────


def _double_assert(a: dict) -> str:
    check_type_name(a["cls"])
    return _lines(
        f"interface {a['cls']} {{",
        f"  {a['field']}: number;",
        "}",
        "",
        f"const loose: unknown = {{ {a['field']}: {a['number']} }};",
        "",
        f"const held_here = loose as {a['cls']};",
        f"const forced = {a['number']} as unknown as {a['cls']};",
        "",
        f"console.log(held_here.{a['field']});",
        "console.log(typeof forced);",
        f"console.log(forced.{a['field']} === undefined);",
    )


# ── 135. Result ──────────────────────────────────────────────


def _result_type(a: dict) -> str:
    return _lines(
        "type Result<T> = { ok: true; value: T } "
        "| { ok: false; why: string };",
        "",
        f"function {a['func']}(value: number): Result<number> {{",
        f"  if (value < {a['limit']}) {{",
        f"    return {{ ok: false, why: {_q(a['why'])} }};",
        "  }",
        # The row's expr is a whole expression over `value`, because the
        # expected-output side evaluates it as one. Prefixing `value` here
        # would emit `value value * 2`.
        f"  return {{ ok: true, value: {a['expr']} }};",
        "}",
        "",
        f"function {a['reader']}(made: Result<number>): string {{",
        # `=== true` rather than a bare truthiness test. Narrowing a
        # boolean discriminant by truthiness alone needs strictNullChecks,
        # and this workbook's tsc runs without --strict, so `if (made.ok)`
        # leaves `made` un-narrowed and reading `why` below fails to
        # compile. The explicit comparison narrows in either mode.
        "  if (made.ok === true) {",
        "    return String(made.value);",
        "  }",
        "  return made.why;",
        "}",
        "",
        f"console.log({a['reader']}({a['func']}({a['good']})));",
        f"console.log({a['reader']}({a['func']}({a['bad']})));",
    )


# ── 136. Omit to change one field ────────────────────────────


def _omit_override(a: dict) -> str:
    check_type_name(a["cls"])
    return _lines(
        f"interface {a['cls']} {{",
        f"  {a['kept']}: string;",
        f"  {a['changed']}: number;",
        "}",
        "",
        f'type Restated = Omit<{a["cls"]}, "{a["changed"]}"> & {{',
        f"  {a['changed']}: string;",
        "};",
        "",
        "const held_here: Restated = {",
        f"  {a['kept']}: {_q(a['kept_value'])},",
        f"  {a['changed']}: {_q(a['changed_value'])},",
        "};",
        "",
        f"console.log(held_here.{a['kept']});",
        f"console.log(held_here.{a['changed']});",
        f"console.log(typeof held_here.{a['changed']});",
    )


# ── 137. Template literal keys ───────────────────────────────


def _template_keys(a: dict) -> str:
    # Each line already ends in its comma, so these join on the newline
    # alone - joining on ",\n" as well gives every line two.
    entries = "\n".join(
        f"  {a['prefix']}{name}: {number}," for name, number in a["entries"]
    )
    first_name = a["entries"][0][0]
    return _lines(
        f'type Keyed = {{ [key in `{a["prefix"]}${{string}}`]?: number }};',
        "",
        "const held_here: Keyed = {",
        entries.rstrip(","),
        "};",
        "",
        f"console.log(held_here.{a['prefix']}{first_name} ?? 0);",
        "console.log(Object.keys(held_here).length);",
        'console.log(Object.keys(held_here).join(", "));',
    )


# ── 138. A generic class matching a generic interface ────────


def _generic_impl(a: dict) -> str:
    check_type_name(a["iface"])
    check_type_name(a["cls"])
    return _lines(
        f"interface {a['iface']}<T> {{",
        f"  {a['method']}(): T;",
        "}",
        "",
        f"class {a['cls']}<T> implements {a['iface']}<T> {{",
        "  constructor(private readonly held: T) {}",
        "",
        f"  {a['method']}(): T {{",
        "    return this.held;",
        "  }",
        "}",
        "",
        f"const worded: {a['iface']}<string> = "
        f"new {a['cls']}({_q(a['word'])});",
        f"const counted: {a['iface']}<number> = "
        f"new {a['cls']}({a['number']});",
        "",
        f"console.log(worded.{a['method']}());",
        f"console.log(counted.{a['method']}());",
        f"console.log(typeof counted.{a['method']}());",
    )


# ── 139. The type of the class itself ────────────────────────


def _class_typeof(a: dict) -> str:
    check_type_name(a["cls"])
    return _lines(
        f"class {a['cls']} {{",
        f"  static readonly {a['static_field']} = "
        f"{_q(a['static_value'])};",
        "",
        f"  constructor(readonly {a['field']}: number) {{}}",
        "}",
        "",
        f"function build_one(maker: typeof {a['cls']}, value: number): "
        f"{a['cls']} {{",
        "  return new maker(value);",
        "}",
        "",
        f"const made_here = build_one({a['cls']}, {a['number']});",
        "",
        f"console.log(made_here.{a['field']});",
        f"console.log({a['cls']}.{a['static_field']});",
        f"console.log(made_here instanceof {a['cls']});",
    )


# ── 140. A conditional type that recurses ────────────────────


def _deep_conditional(a: dict) -> str:
    return _lines(
        "type Flat<T> = T extends readonly (infer Inner)[] "
        "? Flat<Inner> : T;",
        "",
        f"const held_here: Flat<number[][][]> = {a['number']};",
        f"const worded: Flat<string[][]> = {_q(a['word'])};",
        "",
        f"function {a['func']}(value: Flat<number[][]>): number {{",
        f"  return {a['expr']};",
        "}",
        "",
        "console.log(held_here);",
        "console.log(worded);",
        f"console.log({a['func']}({a['number']}));",
    )


_BUILDERS = {
    "ts_parameters": _parameters,
    "ts_instanceof": _instanceof,
    "ts_optional_chain": _optional_chain,
    "ts_double_assert": _double_assert,
    "ts_result_type": _result_type,
    "ts_omit_override": _omit_override,
    "ts_template_keys": _template_keys,
    "ts_generic_impl": _generic_impl,
    "ts_class_typeof": _class_typeof,
    "ts_deep_conditional": _deep_conditional,
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
    if shape == "ts_parameters":
        if a["count"] < 1:
            raise ValueError("repeat must produce something")
        made = a["word"] * a["count"]
        lines = [made, str(a["count"]), str(len(made))]
    elif shape == "ts_instanceof":
        lines = [a["first_value"], str(a["second_value"])]
    elif shape == "ts_optional_chain":
        lines = [a["value"], a["missing"], str(a["number"]), "0"]
    elif shape == "ts_double_assert":
        # The forced value is a number wearing the interface's name, so
        # typeof is still number and the field is not there.
        lines = [str(a["number"]), "number", "true"]
    elif shape == "ts_result_type":
        if a["good"] < a["limit"]:
            raise ValueError("the good value must pass the check")
        if a["bad"] >= a["limit"]:
            raise ValueError("the bad value must fail the check")
        lines = [str(value(a["expr"], {"value": a["good"]})), a["why"]]
    elif shape == "ts_omit_override":
        lines = [a["kept_value"], a["changed_value"], "string"]
    elif shape == "ts_template_keys":
        names = [f"{a['prefix']}{n}" for n, _ in a["entries"]]
        lines = [
            str(a["entries"][0][1]),
            str(len(names)),
            ", ".join(names),
        ]
    elif shape == "ts_generic_impl":
        lines = [a["word"], str(a["number"]), "number"]
    elif shape == "ts_class_typeof":
        lines = [str(a["number"]), a["static_value"], "true"]
    elif shape == "ts_deep_conditional":
        lines = [
            str(a["number"]),
            a["word"],
            str(value(a["expr"], {"value": a["number"]})),
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
