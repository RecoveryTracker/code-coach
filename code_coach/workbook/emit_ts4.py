"""TypeScript-only shapes, fourth batch: the type system meeting real code.

The third batch computed types. These use them where they earn their keep -
readonly for things that must not change, strict null checks for the mistake
that cost a billion dollars, a class that promises to satisfy an interface,
a key that is guaranteed to exist, and a brand that stops two numbers meaning
different things from being swapped.

Page 115 is the one people meet last and want first. TypeScript is
structurally typed, so a UserId and an OrderId that are both numbers are the
same type and can be passed to each other's functions all day. An
intersection with a phantom property gives them separate identities without
costing anything at run time.

Page 120's recursive type is the other one to know: a type that refers to
itself describes JSON, or a tree, or a nested list, in about four lines.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q
from code_coach.workbook.emit_ts import check_type_name

LANGUAGES: tuple[str, ...] = ("typescript",)

SHAPES: tuple[Shape, ...] = (
    Shape("ts_readonly", "a field the compiler will not let you change"),
    Shape("ts_strict_null", "a value that might not be there"),
    Shape("ts_implements", "a class promising to match an interface"),
    Shape("ts_keyof_generic", "a lookup that cannot ask for a missing key"),
    Shape("ts_branded", "two numbers that are not interchangeable"),
    Shape("ts_filter_guard", "a filter the compiler learns from"),
    Shape("ts_key_remap", "a mapped type that renames as it goes"),
    Shape("ts_recursive_type", "a type that mentions itself"),
    Shape("ts_reducer", "a tagged union driving a state change"),
    Shape("ts_readonly_array", "a list nobody can push to"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(str(n) for n in items)


def _words(items) -> str:
    return ", ".join(_q(w) for w in items)


# ── 111. readonly ────────────────────────────────────────────


def _readonly(a: dict) -> str:
    check_type_name(a["cls"])
    return _lines(
        f"interface {a['cls']} {{",
        f"  readonly {a['fixed']}: string;",
        f"  {a['loose']}: number;",
        "}",
        "",
        f"const thing: {a['cls']} = {{ {a['fixed']}: "
        f"{_q(a['fixed_value'])}, {a['loose']}: {a['loose_value']} }};",
        "",
        f"thing.{a['loose']} = {a['changed']};",
        "",
        f"console.log(thing.{a['fixed']});",
        f"console.log(thing.{a['loose']});",
    )


# ── 112. Strict null checks ──────────────────────────────────


def _strict_null(a: dict) -> str:
    return _lines(
        f"interface {a['cls']} {{",
        f"  {a['field']}?: string;",
        "}",
        "",
        f"function {a['func']}(thing: {a['cls']}): string {{",
        f"  return thing.{a['field']} ?? {_q(a['fallback'])};",
        "}",
        "",
        f"console.log({a['func']}({{ {a['field']}: "
        f"{_q(a['present'])} }}));",
        f"console.log({a['func']}({{}}));",
        f"console.log({a['func']}({{ {a['field']}: undefined }}));",
    )


# ── 113. implements ──────────────────────────────────────────


def _implements(a: dict) -> str:
    check_type_name(a["iface"])
    check_type_name(a["cls"])
    return _lines(
        f"interface {a['iface']} {{",
        f"  {a['method']}(): string;",
        f"  readonly {a['field']}: number;",
        "}",
        "",
        f"class {a['cls']} implements {a['iface']} {{",
        f"  readonly {a['field']} = {a['number']};",
        "",
        f"  {a['method']}(): string {{",
        f"    return {_q(a['says'])};",
        "  }",
        "}",
        "",
        f"const made: {a['iface']} = new {a['cls']}();",
        f"console.log(made.{a['method']}());",
        f"console.log(made.{a['field']});",
    )


# ── 114. A generic keyed by its own object ───────────────────


def _keyof_generic(a: dict) -> str:
    pairs = ", ".join(
        f"{k}: {_q(v) if isinstance(v, str) else v}" for k, v in a["entries"]
    )
    return _lines(
        "function pick<T, K extends keyof T>(thing: T, key: K): T[K] {",
        "  return thing[key];",
        "}",
        "",
        f"const {a['const_name']} = {{ {pairs} }};",
        "",
        f"console.log(pick({a['const_name']}, {_q(a['first_key'])}));",
        f"console.log(pick({a['const_name']}, {_q(a['second_key'])}));",
    )


# ── 115. Branded types ───────────────────────────────────────


def _branded(a: dict) -> str:
    check_type_name(a["first_type"])
    check_type_name(a["second_type"])
    return _lines(
        f'type {a["first_type"]} = number & {{ readonly brand: '
        f'"{a["first_brand"]}" }};',
        f'type {a["second_type"]} = number & {{ readonly brand: '
        f'"{a["second_brand"]}" }};',
        "",
        f"function as_{a['first_brand']}(value: number): "
        f"{a['first_type']} {{",
        f"  return value as {a['first_type']};",
        "}",
        "",
        f"function {a['func']}(id: {a['first_type']}): string {{",
        f"  return `{a['label']} ${{id}}`;",
        "}",
        "",
        f"console.log({a['func']}(as_{a['first_brand']}"
        f"({a['number']})));",
        f"console.log(as_{a['first_brand']}({a['number']}) + 1);",
    )


# ── 116. Filtering with a type guard ─────────────────────────


def _filter_guard(a: dict) -> str:
    items = ", ".join(
        _q(v) if isinstance(v, str) else "null" for v in a["items"]
    )
    return _lines(
        "function is_present(value: string | null): value is string {",
        "  return value !== null;",
        "}",
        "",
        f"const mixed: (string | null)[] = [{items}];",
        "const kept: string[] = mixed.filter(is_present);",
        "",
        "console.log(kept.length);",
        'console.log(kept.join(", "));',
        f"console.log(kept.map((word) => word.{a['method']}()).join(\", \"));",
    )


# ── 117. Key remapping in a mapped type ──────────────────────


def _key_remap(a: dict) -> str:
    check_type_name(a["cls"])
    return _lines(
        f"interface {a['cls']} {{",
        f"  {a['first']}: string;",
        f"  {a['second']}: number;",
        "}",
        "",
        "type Prefixed<T> = {",
        f'  [K in keyof T as `{a["prefix"]}${{string & K}}`]: T[K];',
        "};",
        "",
        f"const thing: Prefixed<{a['cls']}> = {{",
        f"  {a['prefix']}{a['first']}: {_q(a['first_value'])},",
        f"  {a['prefix']}{a['second']}: {a['second_value']},",
        "};",
        "",
        f"console.log(thing.{a['prefix']}{a['first']});",
        f"console.log(thing.{a['prefix']}{a['second']});",
        "console.log(Object.keys(thing).length);",
    )


# ── 118. Recursive types ─────────────────────────────────────


def _recursive_type(a: dict) -> str:
    def render(node) -> str:
        if isinstance(node, tuple):
            return "[" + ", ".join(render(child) for child in node) + "]"
        return str(node)

    return _lines(
        "type Nested = number | Nested[];",
        "",
        f"function {a['func']}(value: Nested): number {{",
        "  if (typeof value === \"number\") {",
        "    return value;",
        "  }",
        # reduce takes its accumulator type from the array's element type,
        # not from the initial value, so without <number> total is Nested
        # here and the addition does not compile.
        f"  return value.reduce<number>((total, part) => total + "
        f"{a['func']}(part), 0);",
        "}",
        "",
        f"console.log({a['func']}({render(a['tree'])}));",
        f"console.log({a['func']}({a['plain']}));",
    )


# ── 119. A tagged union driving a change ─────────────────────


def _reducer(a: dict) -> str:
    check_type_name(a["type_name"])
    return _lines(
        f'type Action = {{ kind: "{a["up"]}"; by: number }}'
        f' | {{ kind: "{a["down"]}"; by: number }}'
        f' | {{ kind: "{a["reset"]}" }};',
        "",
        f"interface {a['type_name']} {{",
        "  total: number;",
        "}",
        "",
        f"function {a['func']}(state: {a['type_name']}, action: Action): "
        f"{a['type_name']} {{",
        "  switch (action.kind) {",
        f'    case "{a["up"]}":',
        "      return { total: state.total + action.by };",
        f'    case "{a["down"]}":',
        "      return { total: state.total - action.by };",
        f'    case "{a["reset"]}":',
        f"      return {{ total: {a['start']} }};",
        "  }",
        "}",
        "",
        f"let state: {a['type_name']} = {{ total: {a['start']} }};",
        f'state = {a["func"]}(state, {{ kind: "{a["up"]}", '
        f"by: {a['plus']} }});",
        "console.log(state.total);",
        f'state = {a["func"]}(state, {{ kind: "{a["down"]}", '
        f"by: {a['minus']} }});",
        "console.log(state.total);",
        f'state = {a["func"]}(state, {{ kind: "{a["reset"]}" }});',
        "console.log(state.total);",
    )


# ── 120. readonly arrays ─────────────────────────────────────


def _readonly_array(a: dict) -> str:
    return _lines(
        f"const {a['const_name']}: readonly number[] = "
        f"[{_nums(a['items'])}];",
        "",
        f"function {a['func']}(values: readonly number[]): number[] {{",
        f"  return [...values, {a['added']}];",
        "}",
        "",
        # Not `longer`: one row's function is called that, and the const
        # would be a duplicate identifier in the same scope.
        f"const grown_list = {a['func']}({a['const_name']});",
        "",
        f"console.log({a['const_name']}.length);",
        "console.log(grown_list.length);",
        "console.log(grown_list[grown_list.length - 1]);",
    )


_BUILDERS = {
    "ts_readonly": _readonly,
    "ts_strict_null": _strict_null,
    "ts_implements": _implements,
    "ts_keyof_generic": _keyof_generic,
    "ts_branded": _branded,
    "ts_filter_guard": _filter_guard,
    "ts_key_remap": _key_remap,
    "ts_recursive_type": _recursive_type,
    "ts_reducer": _reducer,
    "ts_readonly_array": _readonly_array,
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
    if shape == "ts_readonly":
        if a["changed"] == a["loose_value"]:
            raise ValueError("the change must actually change something")
        lines = [a["fixed_value"], str(a["changed"])]
    elif shape == "ts_strict_null":
        lines = [a["present"], a["fallback"], a["fallback"]]
    elif shape == "ts_implements":
        lines = [a["says"], str(a["number"])]
    elif shape == "ts_keyof_generic":
        table = dict(a["entries"])
        for key in (a["first_key"], a["second_key"]):
            if key not in table:
                raise ValueError("the key picked must be in the object")
        lines = [str(table[a["first_key"]]), str(table[a["second_key"]])]
    elif shape == "ts_branded":
        lines = [f"{a['label']} {a['number']}", str(a["number"] + 1)]
    elif shape == "ts_filter_guard":
        kept = [v for v in a["items"] if isinstance(v, str)]
        if len(kept) == len(a["items"]):
            raise ValueError("some entries must be null")
        if not kept:
            raise ValueError("some entries must survive the filter")
        changed = [
            w.upper() if a["method"] == "toUpperCase" else w.lower()
            for w in kept
        ]
        lines = [str(len(kept)), ", ".join(kept), ", ".join(changed)]
    elif shape == "ts_key_remap":
        lines = [a["first_value"], str(a["second_value"]), "2"]
    elif shape == "ts_recursive_type":
        def total(node) -> int:
            if isinstance(node, tuple):
                return sum(total(child) for child in node)
            return int(node)

        if not isinstance(a["tree"], tuple):
            raise ValueError("the tree must actually nest")
        lines = [str(total(a["tree"])), str(a["plain"])]
    elif shape == "ts_reducer":
        after_up = a["start"] + a["plus"]
        lines = [
            str(after_up),
            str(after_up - a["minus"]),
            str(a["start"]),
        ]
    elif shape == "ts_readonly_array":
        lines = [
            str(len(a["items"])),
            str(len(a["items"]) + 1),
            str(a["added"]),
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
