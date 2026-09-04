"""TypeScript-only shapes, fifth batch: shapes that carry positions, and
unions you can take apart.

Variadic tuples give a type to the first-and-the-rest pattern. A `this`
return type makes a chain work in a subclass without every method being
overridden. Extract and Exclude do set arithmetic on unions, which is the
half of the utility types people never reach for. And declaration merging
is the thing that surprises everyone once and then never again.

Two house rules show up repeatedly in here and are worth stating.

Nothing prints a raw array or object, because node renders one with spaces
inside the brackets and Python's repr does not, and the expected output is
computed in Python. Everything is joined or counted first.

No emitted identifier may be one a row supplies. A row on the previous
batch named its function `longer` and collided with a const the emitter
declared, which cost twenty exercises' worth of compile. The locals here
are deliberately awkward: `made_here`, `held_here`.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q
from code_coach.workbook.emit_ts import check_type_name

LANGUAGES: tuple[str, ...] = ("typescript",)

SHAPES: tuple[Shape, ...] = (
    Shape("ts_variadic_tuple", "a tuple of the first one and the rest"),
    Shape("ts_this_return", "a method chain that survives inheritance"),
    Shape("ts_accessor", "a getter and setter with types"),
    Shape("ts_rest_params", "optional and rest parameters, typed"),
    Shape("ts_two_generics", "two type parameters at once"),
    Shape("ts_extract_exclude", "set arithmetic on a union"),
    Shape("ts_non_nullable", "a union with the nothings taken out"),
    Shape("ts_typed_entries", "walking an object without losing its types"),
    Shape("ts_private_field", "a field nobody outside can reach"),
    Shape("ts_declaration_merge", "two interfaces of the same name"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(str(n) for n in items)


def _words(items) -> str:
    return ", ".join(_q(w) for w in items)


# ── 121. Variadic tuples ─────────────────────────────────────


def _variadic_tuple(a: dict) -> str:
    return _lines(
        "type Headed = [number, ...number[]];",
        "",
        f"function {a['head_fn']}(values: Headed): number {{",
        "  const [first] = values;",
        "  return first;",
        "}",
        "",
        f"function {a['rest_fn']}(values: Headed): number {{",
        "  const [, ...rest] = values;",
        "  return rest.length;",
        "}",
        "",
        f"const held_here: Headed = [{_nums(a['items'])}];",
        f"console.log({a['head_fn']}(held_here));",
        f"console.log({a['rest_fn']}(held_here));",
        "console.log(held_here.length);",
    )


# ── 122. this as a return type ───────────────────────────────


def _this_return(a: dict) -> str:
    check_type_name(a["base"])
    check_type_name(a["sub"])
    return _lines(
        f"class {a['base']} {{",
        "  protected total = 0;",
        "",
        f"  {a['first']}(by: number): this {{",
        "    this.total += by;",
        "    return this;",
        "  }",
        "",
        "  value(): number {",
        "    return this.total;",
        "  }",
        "}",
        "",
        f"class {a['sub']} extends {a['base']} {{",
        f"  {a['second']}(by: number): this {{",
        "    this.total *= by;",
        "    return this;",
        "  }",
        "}",
        "",
        f"const made_here = new {a['sub']}()",
        f"  .{a['first']}({a['added']})",
        f"  .{a['second']}({a['times']})",
        f"  .{a['first']}({a['added']});",
        "",
        "console.log(made_here.value());",
        f"console.log(new {a['sub']}().{a['first']}"
        f"({a['added']}).value());",
    )


# ── 123. Getters and setters ─────────────────────────────────


def _accessor(a: dict) -> str:
    check_type_name(a["cls"])
    return _lines(
        f"class {a['cls']} {{",
        f"  private stored = {a['start']};",
        "",
        f"  get {a['field']}(): number {{",
        "    return this.stored;",
        "  }",
        "",
        f"  set {a['field']}(value: number) {{",
        "    this.stored = value < 0 ? 0 : value;",
        "  }",
        "}",
        "",
        f"const made_here = new {a['cls']}();",
        f"console.log(made_here.{a['field']});",
        f"made_here.{a['field']} = {a['setting']};",
        f"console.log(made_here.{a['field']});",
        f"made_here.{a['field']} = -{a['negative']};",
        f"console.log(made_here.{a['field']});",
    )


# ── 124. Optional and rest parameters ────────────────────────


def _rest_params(a: dict) -> str:
    return _lines(
        f"function {a['func']}(label: string, sep?: string, "
        "...values: number[]): string {",
        f"  const joiner = sep ?? {_q(a['default_sep'])};",
        "  return label + joiner + values.join(joiner);",
        "}",
        "",
        f"console.log({a['func']}({_q(a['label'])}));",
        f"console.log({a['func']}({_q(a['label'])}, "
        f"{_q(a['sep'])}, {_nums(a['items'])}));",
        f"console.log({a['func']}({_q(a['label'])}, undefined, "
        f"{_nums(a['items'])}));",
    )


# ── 125. Two type parameters ─────────────────────────────────


def _two_generics(a: dict) -> str:
    return _lines(
        "function pair_up<A, B>(first: A, second: B): [A, B] {",
        "  return [first, second];",
        "}",
        "",
        f"const held_here = pair_up({_q(a['word'])}, {a['number']});",
        "",
        "console.log(held_here[0]);",
        "console.log(held_here[1]);",
        "console.log(typeof held_here[0]);",
        "console.log(typeof held_here[1]);",
    )


# ── 126. Extract and Exclude ─────────────────────────────────


def _extract_exclude(a: dict) -> str:
    check_type_name(a["type_name"])
    members = " | ".join(_q(m) for m in a["members"])
    keep = " | ".join(_q(m) for m in a["kept"])
    return _lines(
        f"type {a['type_name']} = {members};",
        f"type Kept = Extract<{a['type_name']}, {keep}>;",
        f"type Dropped = Exclude<{a['type_name']}, {keep}>;",
        "",
        f"const kept_one: Kept = {_q(a['kept'][0])};",
        f"const dropped_one: Dropped = {_q(a['dropped_shown'])};",
        "",
        "console.log(kept_one);",
        "console.log(dropped_one);",
    )


# ── 127. NonNullable ─────────────────────────────────────────


def _non_nullable(a: dict) -> str:
    check_type_name(a["type_name"])
    return _lines(
        f'type {a["type_name"]} = "{a["first"]}" | "{a["second"]}"'
        " | null | undefined;",
        f"type Solid = NonNullable<{a['type_name']}>;",
        "",
        f"function {a['func']}(value: {a['type_name']}): Solid {{",
        f"  return value ?? {_q(a['first'])};",
        "}",
        "",
        f"console.log({a['func']}({_q(a['second'])}));",
        f"console.log({a['func']}(null));",
        f"console.log({a['func']}(undefined));",
    )


# ── 128. Typed entries ───────────────────────────────────────


def _typed_entries(a: dict) -> str:
    pairs = ", ".join(f"{k}: {v}" for k, v in a["entries"])
    return _lines(
        f"const held_here = {{ {pairs} }} as const;",
        "",
        "type Key = keyof typeof held_here;",
        "",
        "const keys = Object.keys(held_here) as Key[];",
        "let total = 0;",
        "for (const key of keys) {",
        "  total += held_here[key];",
        "}",
        "",
        'console.log(keys.join(", "));',
        "console.log(total);",
        f"console.log(held_here.{a['entries'][0][0]});",
    )


# ── 129. Private fields ──────────────────────────────────────


def _private_field(a: dict) -> str:
    check_type_name(a["cls"])
    return _lines(
        f"class {a['cls']} {{",
        f"  #{a['field']}: number;",
        "",
        "  constructor(start: number) {",
        f"    this.#{a['field']} = start;",
        "  }",
        "",
        f"  {a['method']}(by: number): number {{",
        f"    this.#{a['field']} += by;",
        f"    return this.#{a['field']};",
        "  }",
        "",
        "  peek(): number {",
        f"    return this.#{a['field']};",
        "  }",
        "}",
        "",
        f"const made_here = new {a['cls']}({a['start']});",
        f"console.log(made_here.{a['method']}({a['added']}));",
        "console.log(made_here.peek());",
        "console.log(Object.keys(made_here).length);",
    )


# ── 130. Declaration merging ─────────────────────────────────


def _declaration_merge(a: dict) -> str:
    check_type_name(a["cls"])
    return _lines(
        f"interface {a['cls']} {{",
        f"  {a['first']}: string;",
        "}",
        "",
        f"interface {a['cls']} {{",
        f"  {a['second']}: number;",
        "}",
        "",
        f"const held_here: {a['cls']} = {{",
        f"  {a['first']}: {_q(a['first_value'])},",
        f"  {a['second']}: {a['second_value']},",
        "};",
        "",
        f"console.log(held_here.{a['first']});",
        f"console.log(held_here.{a['second']});",
        "console.log(Object.keys(held_here).length);",
    )


_BUILDERS = {
    "ts_variadic_tuple": _variadic_tuple,
    "ts_this_return": _this_return,
    "ts_accessor": _accessor,
    "ts_rest_params": _rest_params,
    "ts_two_generics": _two_generics,
    "ts_extract_exclude": _extract_exclude,
    "ts_non_nullable": _non_nullable,
    "ts_typed_entries": _typed_entries,
    "ts_private_field": _private_field,
    "ts_declaration_merge": _declaration_merge,
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
    if shape == "ts_variadic_tuple":
        if len(a["items"]) < 2:
            raise ValueError("the rest must have something in it")
        lines = [
            str(a["items"][0]),
            str(len(a["items"]) - 1),
            str(len(a["items"])),
        ]
    elif shape == "ts_this_return":
        chained = ((0 + a["added"]) * a["times"]) + a["added"]
        lines = [str(chained), str(a["added"])]
    elif shape == "ts_accessor":
        lines = [str(a["start"]), str(a["setting"]), "0"]
    elif shape == "ts_rest_params":
        joined = a["sep"].join(str(n) for n in a["items"])
        default_joined = a["default_sep"].join(str(n) for n in a["items"])
        lines = [
            a["label"] + a["default_sep"],
            a["label"] + a["sep"] + joined,
            a["label"] + a["default_sep"] + default_joined,
        ]
    elif shape == "ts_two_generics":
        lines = [a["word"], str(a["number"]), "string", "number"]
    elif shape == "ts_extract_exclude":
        kept = set(a["kept"])
        if not kept.issubset(set(a["members"])):
            raise ValueError("the kept members must be in the union")
        if a["dropped_shown"] in kept:
            raise ValueError("the dropped member must not be a kept one")
        if a["dropped_shown"] not in a["members"]:
            raise ValueError("the dropped member must be in the union")
        lines = [a["kept"][0], a["dropped_shown"]]
    elif shape == "ts_non_nullable":
        lines = [a["second"], a["first"], a["first"]]
    elif shape == "ts_typed_entries":
        keys = [k for k, _ in a["entries"]]
        lines = [
            ", ".join(keys),
            str(sum(v for _, v in a["entries"])),
            str(a["entries"][0][1]),
        ]
    elif shape == "ts_private_field":
        after = a["start"] + a["added"]
        # A # field is not an own enumerable property, so Object.keys
        # sees nothing at all - which is the point of the last line.
        lines = [str(after), str(after), "0"]
    elif shape == "ts_declaration_merge":
        lines = [a["first_value"], str(a["second_value"]), "2"]
    else:
        raise KeyError(shape)
    return NL.join(lines)
