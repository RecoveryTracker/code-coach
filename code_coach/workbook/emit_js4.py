"""JavaScript-only shapes, fourth batch: flattening, copying, and the
modern operators.

flat and flatMap. Object spread against Object.assign. structuredClone,
which is the deep copy JavaScript went twenty-five years without. The
string padding methods. Set operations, which JavaScript makes you write
yourself. Dates, where the month counts from zero. An Error subclass.
Promise chaining with then and catch. Array.from. And the logical
assignment operators, where ??= and ||= disagree about zero.

Same rule throughout: nothing prints a raw array or object.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_flat", "an array of arrays, flattened"),
    Shape("js_object_spread", "two objects merged, and who wins"),
    Shape("js_structured_clone", "a copy that goes all the way down"),
    Shape("js_string_pad", "padding, trimming and replacing all of them"),
    Shape("js_set_ops", "union and overlap, written by hand"),
    Shape("js_date", "a date, and the month that counts from zero"),
    Shape("js_error_class", "an error type of your own"),
    Shape("js_promise_then", "promises chained, and the catch at the end"),
    Shape("js_array_from", "making an array out of something else"),
    Shape("js_logical_assign", "assigning only when you need to"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return ", ".join(str(n) for n in items)


def _js(shape: str, a: dict) -> str:
    if shape == "js_flat":
        rows = ", ".join("[" + _nums(r) + "]" for r in a["rows"])
        return _lines(
            "const rows = [" + rows + "];",
            "",
            'console.log(rows.flat().join(", "));',
            f"console.log(rows.flatMap((row) => row.map((n) => "
            f'{a["expr"]})).join(", "));',
            "console.log(rows.length);",
        )
    if shape == "js_object_spread":
        first = ", ".join(f"{k}: {_q(v)}" for k, v in a["defaults"])
        second = ", ".join(f"{k}: {_q(v)}" for k, v in a["chosen"])
        return _lines(
            "const defaults = { " + first + " };",
            "const chosen = { " + second + " };",
            "const merged = { ...defaults, ...chosen };",
            "",
            f"console.log(merged.{a['chosen'][0][0]});",
            f"console.log(merged.{a['only_default']});",
            'console.log(Object.keys(merged).sort().join(", "));',
        )
    if shape == "js_structured_clone":
        return _lines(
            "const inner = [" + _nums(a["inner"]) + "];",
            "const outer = { items: inner };",
            "const shallow = { ...outer };",
            "const deep = structuredClone(outer);",
            "",
            f"inner.push({a['added']});",
            "",
            "console.log(shallow.items.length);",
            "console.log(deep.items.length);",
        )
    if shape == "js_string_pad":
        return _lines(
            f"const word = {_q(a['short'])};",
            "",
            f"console.log(word.padStart({a['width']}, {_q(a['filler'])}));",
            f'console.log({_q(a["name"])}.padEnd({a["wide"]}, '
            f'{_q(a["dots"])}) + "|");',
            f'console.log({_q(a["spaced"])}.trim() + "|");',
            f"console.log({_q(a['joined'])}.replaceAll("
            f"{_q(a['from_'])}, {_q(a['to'])}));",
        )
    if shape == "js_set_ops":
        return _lines(
            "const first = new Set([" + _nums(a["first"]) + "]);",
            "const second = new Set([" + _nums(a["second"]) + "]);",
            "const union = new Set([...first, ...second]);",
            "const shared = [...first].filter((n) => second.has(n));",
            "",
            'console.log([...union].join(", "));',
            'console.log(shared.join(", "));',
            f"console.log(first.has({a['looked_for']}));",
        )
    if shape == "js_date":
        y, m, d = a["when"]
        return _lines(
            f"const when = new Date(Date.UTC({y}, {m}, {d}));",
            "",
            "console.log(when.toISOString());",
            "console.log(when.getUTCFullYear());",
            "console.log(when.getUTCMonth());",
            "console.log(when.getUTCDate());",
        )
    if shape == "js_error_class":
        return _lines(
            f"class {a['cls']} extends Error {{",
            "  constructor(message) {",
            "    super(message);",
            f'    this.name = "{a["cls"]}";',
            "  }",
            "}",
            "",
            "try {",
            f"  throw new {a['cls']}({_q(a['message'])});",
            "} catch (problem) {",
            "  console.log(problem.message);",
            "  console.log(problem.name);",
            f"  console.log(problem instanceof {a['cls']});",
            "  console.log(problem instanceof Error);",
            "}",
        )
    if shape == "js_promise_then":
        return _lines(
            "function work(n) {",
            f"  return Promise.resolve({a['expr']});",
            "}",
            "",
            f"work({a['start']})",
            f"  .then((n) => {a['next']})",
            "  .then((n) => {",
            "    console.log(n);",
            "    return n;",
            "  })",
            f"  .then(() => Promise.reject(new Error({_q(a['stopped'])})))",
            "  .catch((problem) => console.log(problem.message));",
        )
    if shape == "js_array_from":
        return _lines(
            f'console.log(Array.from({_q(a["word"])}).join(", "));',
            f"console.log(Array.from({{ length: {a['count']} }}, "
            f'(_, i) => {a["expr"]}).join(", "));',
            f"console.log(Array.of({a['one']}).length);",
        )
    if shape == "js_logical_assign":
        return _lines(
            "let missing = null;",
            f"missing ??= {a['fallback']};",
            "let zero = 0;",
            f"zero ??= {a['fallback']};",
            "let empty = 0;",
            f"empty ||= {a['fallback']};",
            f"let held = {a['held']};",
            f"held &&= {a['replacement']};",
            "",
            "console.log(missing);",
            "console.log(zero);",
            "console.log(empty);",
            "console.log(held);",
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
    if shape == "js_flat":
        flat = [n for row in a["rows"] for n in row]
        changed = [value(a["expr"], {"n": n, **_TOOLS}) for n in flat]
        lines = [
            ", ".join(str(n) for n in flat),
            ", ".join(str(n) for n in changed),
            str(len(a["rows"])),
        ]
    elif shape == "js_object_spread":
        merged = {**dict(a["defaults"]), **dict(a["chosen"])}
        lines = [
            dict(a["chosen"])[a["chosen"][0][0]],
            dict(a["defaults"])[a["only_default"]],
            ", ".join(sorted(merged)),
        ]
    elif shape == "js_structured_clone":
        grown = len(a["inner"]) + 1
        # The spread copied one level, so it still shares the inner array.
        lines = [str(grown), str(len(a["inner"]))]
    elif shape == "js_string_pad":
        padded = a["short"].rjust(a["width"], a["filler"])
        if len(a["short"]) >= a["width"]:
            raise ValueError("padStart must actually pad")
        lines = [
            padded,
            a["name"].ljust(a["wide"], a["dots"]) + "|",
            a["spaced"].strip() + "|",
            a["joined"].replace(a["from_"], a["to"]),
        ]
    elif shape == "js_set_ops":
        union: list[int] = []
        for n in list(a["first"]) + list(a["second"]):
            if n not in union:
                union.append(n)
        shared = [n for n in a["first"] if n in a["second"]]
        if not shared:
            raise ValueError("the two sets must overlap")
        lines = [
            ", ".join(str(n) for n in union),
            ", ".join(str(n) for n in shared),
            "true" if a["looked_for"] in a["first"] else "false",
        ]
    elif shape == "js_date":
        y, m, d = a["when"]
        # Month is zero-based going in and coming out, which is the page.
        lines = [
            f"{y:04d}-{m + 1:02d}-{d:02d}T00:00:00.000Z",
            str(y),
            str(m),
            str(d),
        ]
    elif shape == "js_error_class":
        lines = [a["message"], a["cls"], "true", "true"]
    elif shape == "js_promise_then":
        made = value(a["expr"], {"n": a["start"], **_TOOLS})
        after = value(a["next"], {"n": made, **_TOOLS})
        lines = [str(after), a["stopped"]]
    elif shape == "js_array_from":
        letters = ", ".join(a["word"])
        built = [
            value(a["expr"], {"i": i, **_TOOLS}) for i in range(a["count"])
        ]
        lines = [letters, ", ".join(str(n) for n in built), "1"]
    elif shape == "js_logical_assign":
        # ??= only fills in null and undefined, so the zero survives it;
        # ||= treats zero as empty and replaces it. That pair is the page.
        lines = [
            str(a["fallback"]),
            "0",
            str(a["fallback"]),
            str(a["replacement"]),
        ]
    else:
        raise KeyError(shape)
    return NL.join(lines)
