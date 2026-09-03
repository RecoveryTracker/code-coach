"""JavaScript-only shapes, second batch: objects, classes, and the traps.

Methods and this. Classes. Promises and await. throw and catch. for...of
against Object.entries. Then the three that catch everyone: sort
comparing as text unless you tell it not to, JSON round trips, and the
difference between null and undefined - with == against === underneath
it.

Same rule as the first batch: nothing prints a raw array or object,
because Node renders them with spaces inside the brackets. Everything
goes through join or prints one value at a time.
"""

from __future__ import annotations

import json

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_object_method", "an object with a function in it"),
    Shape("js_class", "a class, and the word new"),
    Shape("js_async", "waiting for something that is not ready"),
    Shape("js_throw_catch", "throwing something and catching it"),
    Shape("js_for_of", "walking an object's keys and values"),
    Shape("js_sort_numbers", "sorting numbers, which needs telling"),
    Shape("js_json", "an object turned into text and back"),
    Shape("js_closure", "a function that remembers"),
    Shape("js_null_undefined", "the two kinds of nothing"),
    Shape("js_find_some_every", "asking an array a question"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(str(n) for n in items)


def _as_js(expr: str) -> str:
    return expr.replace("==", "===")


def _js(shape: str, a: dict) -> str:
    if shape == "js_object_method":
        return _lines(
            f"const {a['name']} = {{",
            f"  {a['field']}: {a['value']},",
            f"  {a['method']}() {{",
            f"    return this.{a['field']} * {a['times']};",
            "  },",
            "};",
            "",
            f"console.log({a['name']}.{a['field']});",
            f"console.log({a['name']}.{a['method']}());",
        )
    if shape == "js_class":
        return _lines(
            f"class {a['cls']} {{",
            f"  constructor({a['first']}, {a['second']}) {{",
            f"    this.{a['first']} = {a['first']};",
            f"    this.{a['second']} = {a['second']};",
            "  }",
            "",
            f"  {a['method']}() {{",
            f"    return this.{a['first']} * this.{a['second']};",
            "  }",
            "}",
            "",
            f"const thing = new {a['cls']}({a['values'][0]}, "
            f"{a['values'][1]});",
            f"console.log(thing.{a['first']});",
            f"console.log(thing.{a['method']}());",
        )
    if shape == "js_async":
        return _lines(
            f"async function {a['name']}(n) {{",
            f"  return n * {a['times']};",
            "}",
            "",
            "async function main() {",
            f"  const first = await {a['name']}({a['values'][0]});",
            f"  const second = await {a['name']}({a['values'][1]});",
            "  console.log(first);",
            "  console.log(second);",
            "  const both = await Promise.all([",
            f"    {a['name']}({a['values'][0]}), {a['name']}({a['values'][1]})",
            "  ]);",
            '  console.log(both.join(", "));',
            "}",
            "",
            "main();",
        )
    if shape == "js_throw_catch":
        return _lines(
            "function check(n) {",
            f"  if ({_as_js(a['test'])}) {{",
            f"    throw new Error({_q(a['message'])});",
            "  }",
            "  return n;",
            "}",
            "",
            "for (const n of [" + _nums(a["values"]) + "]) {",
            "  try {",
            "    console.log(check(n));",
            "  } catch (problem) {",
            "    console.log(problem.message);",
            "  }",
            "}",
        )
    if shape == "js_for_of":
        pairs = ", ".join(f"{k}: {v}" for k, v in a["pairs"])
        return _lines(
            "const scores = { " + pairs + " };",
            "",
            "for (const [name, score] of Object.entries(scores)) {",
            "  console.log(`${name} ${score}`);",
            "}",
            'console.log(Object.keys(scores).join(", "));',
        )
    if shape == "js_sort_numbers":
        return _lines(
            "const numbers = [" + _nums(a["items"]) + "];",
            "",
            'console.log([...numbers].sort().join(", "));',
            "console.log([...numbers].sort((a, b) => a - b)"
            '.join(", "));',
            "console.log([...numbers].sort((a, b) => b - a)"
            '.join(", "));',
        )
    if shape == "js_json":
        pairs = ", ".join(f"{k}: {_q(v)}" if isinstance(v, str) else f"{k}: {v}" for k, v in a["pairs"])
        return _lines(
            "const data = { " + pairs + " };",
            "const text = JSON.stringify(data);",
            "const back = JSON.parse(text);",
            "",
            "console.log(text);",
            f"console.log(back.{a['pairs'][0][0]});",
            "console.log(text === JSON.stringify(back));",
        )
    if shape == "js_closure":
        return _lines(
            "function make(start) {",
            "  let total = start;",
            "  return function (n) {",
            "    total += n;",
            "    return total;",
            "  };",
            "}",
            "",
            f"const add = make({a['start']});",
            *[f"console.log(add({n}));" for n in a["adds"]],
        )
    if shape == "js_null_undefined":
        return _lines(
            f"const missing = {{ name: {_q(a['name'])}, {a['field']}: null }};",
            "",
            f"console.log(missing.{a['field']} === null);",
            f"console.log(missing.{a['absent']} === undefined);",
            f"console.log(missing.{a['field']} == missing.{a['absent']});",
            f"console.log(missing.{a['field']} === missing.{a['absent']});",
        )
    if shape == "js_find_some_every":
        return _lines(
            "const numbers = [" + _nums(a["items"]) + "];",
            "",
            f"console.log(numbers.find((n) => {_as_js(a['test'])}));",
            f"console.log(numbers.some((n) => {_as_js(a['test'])}));",
            f"console.log(numbers.every((n) => {_as_js(a['test'])}));",
            f"console.log(numbers.includes({a['looked_for']}));",
        )
    raise KeyError(shape)


def solution(language: str, shape: str, args: dict) -> str | None:
    if language != "javascript":
        return None
    return _js(shape, args)


# ── What each of them prints ─────────────────────────────────

_TOOLS = {"sum": sum, "len": len, "max": max, "min": min, "abs": abs}


def _js_bool(value: bool) -> str:
    return "true" if value else "false"


def expected_output(shape: str, args: dict, value) -> str:
    a = args
    lines: list[str] = []
    if shape == "js_object_method":
        lines = [str(a["value"]), str(a["value"] * a["times"])]
    elif shape == "js_class":
        first, second = a["values"]
        lines = [str(first), str(first * second)]
    elif shape == "js_async":
        made = [n * a["times"] for n in a["values"]]
        lines = [str(made[0]), str(made[1]), ", ".join(str(n) for n in made)]
    elif shape == "js_throw_catch":
        raised = 0
        for n in a["values"]:
            if value(a["test"], {"n": n, **_TOOLS}):
                lines.append(a["message"])
                raised += 1
            else:
                lines.append(str(n))
        if raised == 0 or raised == len(a["values"]):
            raise ValueError("some must throw and some must not")
    elif shape == "js_for_of":
        lines = [f"{k} {v}" for k, v in a["pairs"]]
        lines.append(", ".join(k for k, _ in a["pairs"]))
    elif shape == "js_sort_numbers":
        items = list(a["items"])
        # Bare sort compares them as text, which is the page.
        as_text = sorted(items, key=str)
        rising = sorted(items)
        falling = sorted(items, reverse=True)
        if as_text == rising:
            raise ValueError("a text sort must differ from a number sort")
        lines = [
            ", ".join(str(n) for n in as_text),
            ", ".join(str(n) for n in rising),
            ", ".join(str(n) for n in falling),
        ]
    elif shape == "js_json":
        data = dict(a["pairs"])
        text = json.dumps(data, separators=(",", ":"))
        lines = [text, str(data[a["pairs"][0][0]]), "true"]
    elif shape == "js_closure":
        total = a["start"]
        for n in a["adds"]:
            total += n
            lines.append(str(total))
    elif shape == "js_null_undefined":
        # null == undefined is true; null === undefined is false. That gap
        # is the whole page.
        lines = ["true", "true", "true", "false"]
    elif shape == "js_find_some_every":
        items = list(a["items"])
        found = [n for n in items if value(a["test"], {"n": n, **_TOOLS})]
        if not found or len(found) == len(items):
            raise ValueError("some must match and some must not")
        lines = [
            str(found[0]),
            _js_bool(True),
            _js_bool(False),
            _js_bool(a["looked_for"] in items),
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
