"""JavaScript-only shapes, fifth batch: scope, and the parts of the object
model nobody shows you first.

var against let in a loop, which is the closure bug that made let
necessary. Hoisting and the temporal dead zone. Sorting objects.
Grouping with reduce. Rest and defaults in object destructuring. Tagged
templates. Symbol. WeakMap. Proxy. And Object.freeze, which is both
shallow and silent.

Nothing prints a raw array or object, and every set of keys is sorted
before printing.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_var_let", "the loop variable every closure shared"),
    Shape("js_hoisting", "a name used before it exists"),
    Shape("js_sort_objects", "sorting things by one of their fields"),
    Shape("js_reduce_group", "reduce that builds an object"),
    Shape("js_destructure_rest", "the rest of the object, and a default"),
    Shape("js_tagged_template", "a template literal handed to a function"),
    Shape("js_symbol", "a key that cannot collide"),
    Shape("js_weakmap", "data kept beside an object, not on it"),
    Shape("js_proxy", "an object that answers for another"),
    Shape("js_freeze", "frozen, one level deep, and quietly"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(str(n) for n in items)


def _words(items) -> str:
    return ", ".join(_q(w) for w in items)


def _js(shape: str, a: dict) -> str:
    return _JS[shape](a)


def _var_let(a: dict) -> str:
    return _lines(
        "const withVar = [];",
        f"for (var i = 0; i < {a['count']}; i += 1) {{",
        "  withVar.push(() => i);",
        "}",
        "",
        "const withLet = [];",
        f"for (let j = 0; j < {a['count']}; j += 1) {{",
        "  withLet.push(() => j);",
        "}",
        "",
        'console.log(withVar.map((f) => f()).join(", "));',
        'console.log(withLet.map((f) => f()).join(", "));',
    )


def _hoisting(a: dict) -> str:
    return _lines(
        f"console.log(typeof {a['early']});",
        f"var {a['early']} = {a['first']};",
        "",
        "try {",
        f"  console.log({a['later']});",
        "} catch (problem) {",
        "  console.log(problem.constructor.name);",
        "}",
        f"let {a['later']} = {a['second']};",
        "",
        f"console.log({a['later']});",
    )


def _sort_objects(a: dict) -> str:
    made = ",\n".join(
        f'  {{ name: {_q(n)}, {a["field"]}: {v} }}' for n, v in a["rows"]
    )
    return _lines(
        "const people = [",
        made + ",",
        "];",
        "",
        f"const byField = [...people].sort((a, b) => a.{a['field']} - "
        f"b.{a['field']});",
        "const byName = [...people].sort((a, b) => (a.name < b.name ? -1 : 1));",
        "",
        'console.log(byField.map((p) => p.name).join(", "));',
        'console.log(byName.map((p) => p.name).join(", "));',
    )


def _reduce_group(a: dict) -> str:
    return _lines(
        "const words = [" + _words(a["words"]) + "];",
        "const grouped = words.reduce((held, word) => {",
        "  const key = word[0];",
        "  held[key] = held[key] ?? [];",
        "  held[key].push(word);",
        "  return held;",
        "}, {});",
        "",
        'console.log(Object.keys(grouped).sort().join(", "));',
        f'console.log(grouped[{_q(a["letter"])}].join(", "));',
    )


def _destructure_rest(a: dict) -> str:
    pairs = ", ".join(f"{k}: {_q(v)}" for k, v in a["pairs"])
    return _lines(
        "const settings = { " + pairs + " };",
        f"const {{ {a['pairs'][0][0]}, ...rest }} = settings;",
        f"const {{ {a['absent']} = {_q(a['fallback'])} }} = settings;",
        "",
        f"console.log({a['pairs'][0][0]});",
        'console.log(Object.keys(rest).sort().join(", "));',
        f"console.log({a['absent']});",
    )


def _tagged_template(a: dict) -> str:
    return _lines(
        f"function {a['name']}(strings, ...values) {{",
        f'  return strings.raw.join({_q(a["between"])}) + '
        f'{_q(a["gap"])} + values.join({_q(a["comma"])});',
        "}",
        "",
        f"const first = {_q(a['first'])};",
        f"const second = {a['second']};",
        f"console.log({a['name']}`{a['before']}${{first}}"
        f"{a['middle']}${{second}}{a['after']}`);",
    )


def _symbol(a: dict) -> str:
    return _lines(
        f"const key = Symbol({_q(a['label'])});",
        f"const thing = {{ name: {_q(a['name'])}, [key]: {a['value']} }};",
        "",
        "console.log(thing[key]);",
        "console.log(typeof key);",
        'console.log(Object.keys(thing).join(", "));',
        "console.log(key.toString());",
    )


def _weakmap(a: dict) -> str:
    return _lines(
        "const secrets = new WeakMap();",
        "",
        f"class {a['cls']} {{",
        f"  constructor({a['field']}) {{",
        f"    secrets.set(this, {a['field']});",
        "  }",
        "",
        f"  get {a['field']}() {{",
        "    return secrets.get(this);",
        "  }",
        "}",
        "",
        f"const thing = new {a['cls']}({a['value']});",
        f"console.log(thing.{a['field']});",
        "console.log(secrets.has(thing));",
        "console.log(Object.keys(thing).length);",
    )


def _proxy(a: dict) -> str:
    return _lines(
        f"const target = {{ {a['field']}: {a['value']} }};",
        "const guarded = new Proxy(target, {",
        "  get(held, key) {",
        f"    return key in held ? held[key] : {_q(a['fallback'])};",
        "  },",
        "});",
        "",
        f"console.log(guarded.{a['field']});",
        f"console.log(guarded.{a['absent']});",
    )


def _freeze(a: dict) -> str:
    return _lines(
        f"const settings = Object.freeze({{ {a['field']}: {_q(a['value'])}, "
        f"tags: [{_q(a['tags'][0])}] }});",
        "",
        f"settings.{a['field']} = {_q(a['attempt'])};",
        f"settings.tags.push({_q(a['tags'][1])});",
        "",
        f"console.log(settings.{a['field']});",
        'console.log(settings.tags.join(", "));',
        "console.log(Object.isFrozen(settings));",
    )


_JS = {
    "js_var_let": _var_let,
    "js_hoisting": _hoisting,
    "js_sort_objects": _sort_objects,
    "js_reduce_group": _reduce_group,
    "js_destructure_rest": _destructure_rest,
    "js_tagged_template": _tagged_template,
    "js_symbol": _symbol,
    "js_weakmap": _weakmap,
    "js_proxy": _proxy,
    "js_freeze": _freeze,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "javascript":
        return None
    return _js(shape, args)


# ── What each of them prints ─────────────────────────────────


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "js_var_let":
        count = a["count"]
        if count < 2:
            raise ValueError("the loop must run more than once")
        # var has one binding for the whole loop, so every closure sees
        # the value it finished at. let makes a fresh one each time.
        lines = [
            ", ".join(str(count) for _ in range(count)),
            ", ".join(str(n) for n in range(count)),
        ]
    elif shape == "js_hoisting":
        lines = ["undefined", "ReferenceError", str(a["second"])]
    elif shape == "js_sort_objects":
        by_field = sorted(a["rows"], key=lambda row: row[1])
        by_name = sorted(a["rows"], key=lambda row: row[0])
        if [n for n, _ in by_field] == [n for n, _ in by_name]:
            raise ValueError("the two orders must differ")
        lines = [
            ", ".join(n for n, _ in by_field),
            ", ".join(n for n, _ in by_name),
        ]
    elif shape == "js_reduce_group":
        held: dict[str, list[str]] = {}
        for word in a["words"]:
            held.setdefault(word[0], []).append(word)
        if a["letter"] not in held:
            raise ValueError("the letter asked for must have a group")
        if len(held[a["letter"]]) < 2:
            raise ValueError("that group must hold more than one word")
        lines = [
            ", ".join(sorted(held)),
            ", ".join(held[a["letter"]]),
        ]
    elif shape == "js_destructure_rest":
        kept = [k for k, _ in a["pairs"][1:]]
        lines = [
            a["pairs"][0][1],
            ", ".join(sorted(kept)),
            a["fallback"],
        ]
    elif shape == "js_tagged_template":
        # strings.raw is the literal text either side of each hole.
        chunks = [a["before"], a["middle"], a["after"]]
        lines = [
            a["between"].join(chunks)
            + a["gap"]
            + a["comma"].join([a["first"], str(a["second"])])
        ]
    elif shape == "js_symbol":
        # A symbol key is skipped by Object.keys, which is the point.
        lines = [
            str(a["value"]),
            "symbol",
            "name",
            f"Symbol({a['label']})",
        ]
    elif shape == "js_weakmap":
        lines = [str(a["value"]), "true", "0"]
    elif shape == "js_proxy":
        lines = [str(a["value"]), a["fallback"]]
    elif shape == "js_freeze":
        # The assignment is ignored without complaint; the array inside
        # was never frozen at all.
        lines = [
            a["value"],
            ", ".join(a["tags"]),
            "true",
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
