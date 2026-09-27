"""JavaScript: working with data.

Almost everything a JavaScript program does with an API response is one of
ten moves over an array of objects: find one, ask a yes-no question of all
of them, add up a field, pick the biggest, count, group, sort, format,
report a tally, and chain several of those into a "top three". The earlier
pages taught each method on bare numbers and words; these pages drill them
on the shape the data actually arrives in.

Every program starts with the same kind of literal, an array of small
objects, so the part that changes from exercise to exercise is the data and
the question rather than the scaffolding.

Nothing prints a bare array or object. Node renders those as `[ 1, 2 ]` and
`{ a: 1 }`, spaces and all, and these answers are compared as text.
"""

from __future__ import annotations

from code_coach.workbook.complexity import Cost
from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_data_find", "the first object that matches, and where it is"),
    Shape("js_data_some_every", "yes-no questions about a whole list"),
    Shape("js_data_sum", "adding up one field"),
    Shape("js_data_max", "the object with the biggest field"),
    Shape("js_data_tally", "counting how many of each value"),
    Shape("js_data_group", "an object of arrays, keyed by a field"),
    Shape("js_data_sort", "sorting a copy by text, by number, by both"),
    Shape("js_data_format", "each object turned into a line of text"),
    Shape("js_data_entries", "a tally printed in order"),
    Shape("js_data_top", "filter, sort, slice, map: a top-three report"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── Rendering the data ───────────────────────────────────────


def _num(x) -> str:
    """A number exactly as JavaScript would print it.

    Only ints and floats that are not whole are allowed in: Python prints
    4.0 where JavaScript prints 4, and catching that here is cheaper than
    finding it as one failed exercise.
    """
    if isinstance(x, bool):
        raise ValueError("a bool is not a number here")
    if isinstance(x, float) and x.is_integer():
        raise ValueError(f"write {x} as an int, or it prints differently")
    return repr(x)


def _val(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        if '"' in v or "\\" in v:
            raise ValueError("keep the data free of quotes and backslashes")
        return f'"{v}"'
    return _num(v)


def _data(var: str, items) -> list[str]:
    rows = [
        "  { " + ", ".join(f"{k}: {_val(v)}" for k, v in item.items()) + " },"
        for item in items
    ]
    return [f"const {var} = [", *rows, "];"]


def _item_var(var: str) -> str:
    """The loop variable: the first letter of the list's name."""
    return var[0]


# ── 1. find and findIndex ────────────────────────────────────


def _find(a: dict) -> str:
    v, f, x = a["var"], a["field"], _item_var(a["var"])
    return _lines(
        *_data(v, a["items"]),
        f"const found = {v}.find(({x}) => {x}.{f} > {a['over']});",
        "console.log(found.name);",
        f"console.log({v}.findIndex(({x}) => {x}.{f} > {a['over']}));",
        f'console.log({v}.findIndex(({x}) => {x}.name === "{a["absent"]}"));',
    )


# ── 2. some and every ────────────────────────────────────────


def _some_every(a: dict) -> str:
    v, f, flag, x = a["var"], a["field"], a["flag"], _item_var(a["var"])
    return _lines(
        *_data(v, a["items"]),
        f"console.log({v}.some(({x}) => {x}.{f} >= {a['limit']}));",
        f"console.log({v}.every(({x}) => {x}.{flag}));",
        f'console.log({v}.some(({x}) => {x}.name === "{a["target"]}"));',
    )


# ── 3. Summing a field ───────────────────────────────────────


def _sum(a: dict) -> str:
    v, x = a["var"], _item_var(a["var"])
    if a["want"] == "qty":
        step = f"sum + {x}.price * {x}.qty"
    else:
        step = f"sum + {x}.price"
    shown = "total.toFixed(2)" if a["want"] == "money" else "total"
    return _lines(
        *_data(v, a["items"]),
        f"const total = {v}.reduce((sum, {x}) => {step}, 0);",
        f"console.log({shown});",
    )


# ── 4. The biggest ───────────────────────────────────────────


def _max(a: dict) -> str:
    v, f, x = a["var"], a["field"], _item_var(a["var"])
    op = ">" if a["want"] == "max" else "<"
    return _lines(
        *_data(v, a["items"]),
        f"const best = {v}.reduce((top, {x}) => ({x}.{f} {op} top.{f} ? {x} : top));",
        f"console.log(`${{best.name}} ${{best.{f}}}`);",
    )


# ── 5. A tally ───────────────────────────────────────────────


def _tally(a: dict) -> str:
    v, f, x = a["var"], a["field"], _item_var(a["var"])
    return _lines(
        *_data(v, a["items"]),
        "const counts = {};",
        f"for (const {x} of {v}) {{",
        f"  counts[{x}.{f}] = (counts[{x}.{f}] ?? 0) + 1;",
        "}",
        *(f'console.log(counts["{k}"] ?? 0);' for k in a["ask"]),
    )


# ── 6. Grouping ──────────────────────────────────────────────


def _group(a: dict) -> str:
    v, f, x = a["var"], a["field"], _item_var(a["var"])
    return _lines(
        *_data(v, a["items"]),
        "const groups = {};",
        f"for (const {x} of {v}) {{",
        f"  if (!groups[{x}.{f}]) groups[{x}.{f}] = [];",
        f"  groups[{x}.{f}].push({x}.name);",
        "}",
        "for (const key of Object.keys(groups).sort()) {",
        '  console.log(`${key}: ${groups[key].join(", ")}`);',
        "}",
    )


# ── 7. Sorting ───────────────────────────────────────────────


def _sort(a: dict) -> str:
    v, f = a["var"], a.get("field")
    want = a["want"]
    if want == "text":
        compare = "(a, b) => a.name.localeCompare(b.name)"
    elif want == "number":
        compare = f"(a, b) => b.{f} - a.{f}"
    else:
        g = a["by"]
        compare = f"(a, b) => a.{g}.localeCompare(b.{g}) || b.{f} - a.{f}"
    return _lines(
        *_data(v, a["items"]),
        f"const sorted = [...{v}].sort({compare});",
        'console.log(sorted.map((x) => x.name).join(", "));',
        f"console.log({v}[0].name);",
    )


# ── 8. Formatting ────────────────────────────────────────────


def _format(a: dict) -> str:
    v, x = a["var"], _item_var(a["var"])
    if a["want"] == "qty":
        line = (f"`${{{x}.qty}} x ${{{x}.name}}: "
                f"$${{({x}.price * {x}.qty).toFixed(2)}}`")
    else:
        line = f"`${{{x}.name}}: $${{{x}.price.toFixed(2)}}`"
    return _lines(
        *_data(v, a["items"]),
        f"const lines = {v}.map(({x}) => {line});",
        'console.log(lines.join("\\n"));',
    )


# ── 9. A tally, printed in order ─────────────────────────────


def _entries(a: dict) -> str:
    v, f, x = a["var"], a["field"], _item_var(a["var"])
    if a["want"] == "keys":
        compare = "(a, b) => a[0].localeCompare(b[0])"
    else:
        compare = "(a, b) => b[1] - a[1] || a[0].localeCompare(b[0])"
    return _lines(
        *_data(v, a["items"]),
        "const counts = {};",
        f"for (const {x} of {v}) {{",
        f"  counts[{x}.{f}] = (counts[{x}.{f}] ?? 0) + 1;",
        "}",
        f"const rows = Object.entries(counts).sort({compare});",
        "for (const [key, n] of rows) {",
        "  console.log(`${key}: ${n}`);",
        "}",
    )


# ── 10. Chaining ─────────────────────────────────────────────


def _top(a: dict) -> str:
    v, f, x = a["var"], a["field"], _item_var(a["var"])
    return _lines(
        *_data(v, a["items"]),
        f"const report = {v}",
        f"  .filter(({x}) => {x}.price <= {a['budget']})",
        f"  .sort((a, b) => b.{f} - a.{f})",
        f"  .slice(0, {a['n']})",
        f"  .map(({x}, i) => `${{i + 1}}. ${{{x}.name}} (${{{x}.{f}}})`);",
        'console.log(report.join("\\n"));',
    )


_BUILDERS = {
    "js_data_find": _find,
    "js_data_some_every": _some_every,
    "js_data_sum": _sum,
    "js_data_max": _max,
    "js_data_tally": _tally,
    "js_data_group": _group,
    "js_data_sort": _sort,
    "js_data_format": _format,
    "js_data_entries": _entries,
    "js_data_top": _top,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


# ── What each should print, worked out in Python ─────────────


def _money(x) -> str:
    # Python's .2f and JavaScript's toFixed(2) agree on every double that is
    # not exactly halfway between two cents, and data written to the cent
    # never is.
    return f"{x:.2f}"


def _names(items) -> list[str]:
    names = [i["name"] for i in items]
    if len(set(names)) != len(names):
        raise ValueError("names must be unique, or the output is ambiguous")
    return names


def expected_output(shape: str, args: dict, value=None) -> str:
    a = args
    items = list(a["items"])
    if len(items) < 3:
        raise ValueError("a list of fewer than three is not data")
    for item in items:
        for v in item.values():
            _val(v)  # refuses anything that would print differently
    if shape == "js_data_find":
        f, over = a["field"], a["over"]
        hits = [i for i, it in enumerate(items) if it[f] > over]
        if len(hits) < 2:
            raise ValueError("two must match, or 'the first' means nothing")
        if a["absent"] in _names(items):
            raise ValueError("the absent name must be absent")
        return NL.join([items[hits[0]]["name"], str(hits[0]), "-1"])
    if shape == "js_data_some_every":
        f, flag = a["field"], a["flag"]
        _names(items)
        return NL.join([
            str(any(i[f] >= a["limit"] for i in items)).lower(),
            str(all(i[flag] for i in items)).lower(),
            str(any(i["name"] == a["target"] for i in items)).lower(),
        ])
    if shape == "js_data_sum":
        total = 0
        for i in items:
            total = total + (i["price"] * i["qty"] if a["want"] == "qty"
                             else i["price"])
        if a["want"] == "money":
            return _money(total)
        if not isinstance(total, int):
            raise ValueError("a plain total must be whole, or use money")
        return str(total)
    if shape == "js_data_max":
        f = a["field"]
        values = [i[f] for i in items]
        pick = max(values) if a["want"] == "max" else min(values)
        if values.count(pick) != 1:
            raise ValueError("the winner must be unique")
        if values.index(pick) == 0:
            raise ValueError("the winner must not be first, or no loop is needed")
        best = items[values.index(pick)]
        return f"{best['name']} {_num(best[f])}"
    if shape == "js_data_tally":
        f = a["field"]
        counts: dict[str, int] = {}
        for i in items:
            counts[i[f]] = counts.get(i[f], 0) + 1
        if max(counts.values()) < 2:
            raise ValueError("something must repeat, or nothing is counted")
        if all(k in counts for k in a["ask"]):
            raise ValueError("ask for one missing value, to show the ?? 0")
        return NL.join(str(counts.get(k, 0)) for k in a["ask"])
    if shape == "js_data_group":
        f = a["field"]
        _names(items)
        groups: dict[str, list[str]] = {}
        for i in items:
            groups.setdefault(i[f], []).append(i["name"])
        if len(groups) < 2 or max(len(g) for g in groups.values()) < 2:
            raise ValueError("two groups, and one with more than one in it")
        return NL.join(f"{k}: {', '.join(groups[k])}" for k in sorted(groups))
    if shape == "js_data_sort":
        names = _names(items)
        for n in names:
            if not (n.isascii() and n.islower() and n.isalpha()):
                raise ValueError("plain lowercase names, so localeCompare "
                                 "and code-point order agree")
        want, f = a["want"], a.get("field")
        if want == "text":
            order = sorted(items, key=lambda i: i["name"])
        elif want == "number":
            if len({i[f] for i in items}) != len(items):
                raise ValueError("no ties when sorting by one number")
            order = sorted(items, key=lambda i: -i[f])
        else:
            g = a["by"]
            keys = [(i[g], i[f]) for i in items]
            if len(set(keys)) != len(keys):
                raise ValueError("no ties on both fields")
            if len({i[g] for i in items}) == len(items):
                raise ValueError("the first field must tie somewhere, or "
                                 "the second one never decides anything")
            order = sorted(items, key=lambda i: (i[g], -i[f]))
        if order == items:
            raise ValueError("the data must not already be in order")
        return NL.join([", ".join(i["name"] for i in order), names[0]])
    if shape == "js_data_format":
        if a["want"] == "qty":
            return NL.join(
                f"{i['qty']} x {i['name']}: ${_money(i['price'] * i['qty'])}"
                for i in items)
        return NL.join(f"{i['name']}: ${_money(i['price'])}" for i in items)
    if shape == "js_data_entries":
        f = a["field"]
        counts = {}
        for i in items:
            counts[i[f]] = counts.get(i[f], 0) + 1
        for k in counts:
            if not (k.isascii() and k.islower() and k.isalpha()):
                raise ValueError("plain lowercase keys")
        if a["want"] == "keys":
            rows = sorted(counts.items())
        else:
            rows = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
            if rows == sorted(counts.items()):
                raise ValueError("by-count must differ from alphabetical")
        if len(rows) < 2 or max(counts.values()) < 2:
            raise ValueError("two keys, and a count above one")
        return NL.join(f"{k}: {n}" for k, n in rows)
    if shape == "js_data_top":
        f, budget, n = a["field"], a["budget"], a["n"]
        _names(items)
        kept = [i for i in items if i["price"] <= budget]
        if len(kept) <= n:
            raise ValueError("more must pass the filter than the slice keeps")
        if len({i[f] for i in kept}) != len(kept):
            raise ValueError("no ties among the kept, so the order is certain")
        if max(items, key=lambda i: i[f])["price"] <= budget:
            raise ValueError("the best overall must be filtered out, or the "
                             "filter changes nothing")
        top = sorted(kept, key=lambda i: -i[f])[:n]
        return NL.join(f"{k + 1}. {i['name']} ({_num(i[f])})"
                       for k, i in enumerate(top))
    raise KeyError(shape)


# ── Complexity notes ─────────────────────────────────────────

NOTES: dict[str, Cost] = {
    "js_data_find": Cost(
        "O(n)",
        "Linear in the length of the list, n. find and findIndex walk from "
        "the front and stop at the first match, so a match near the start "
        "is cheap — but a miss, like the name that is not there, has to "
        "look at every object before it can say -1."),
    "js_data_some_every": Cost(
        "O(n)",
        "Linear in the length of the list, n, at worst. some stops at the "
        "first yes and every stops at the first no, so each only walks the "
        "whole list when the answer is the boring one."),
    "js_data_sum": Cost(
        "O(n)",
        "Linear in the number of objects, n: reduce visits each one once "
        "and does one addition there. The running total is a single number "
        "however long the list gets."),
    "js_data_max": Cost(
        "O(n)",
        "Linear in the number of objects, n: one pass, keeping whichever "
        "is bigger so far. Sorting to take the first would also work and "
        "costs n log n to answer a question one pass already answers."),
    "js_data_tally": Cost(
        "O(n)",
        "Linear in the number of objects, n. Each one is a single lookup "
        "and a single write on the counts object, which takes about the "
        "same time however many keys it holds."),
    "js_data_group": Cost(
        "O(n + k log k)",
        "Building the groups is linear in the number of objects, n: one "
        "lookup and one push each. Printing them sorts the k distinct keys, "
        "and k is at most n and usually far smaller."),
    "js_data_sort": Cost(
        "O(n log n)",
        "n log n in the number of objects, n: that is what sorting costs, "
        "and the comparator runs about that many times. Copying first with "
        "the spread is one more linear pass, which the sort outweighs."),
    "js_data_format": Cost(
        "O(n)",
        "Linear in the number of objects, n: map builds one string per "
        "object and join walks them once more. The lines are short, so "
        "their length is not what grows."),
    "js_data_entries": Cost(
        "O(n + k log k)",
        "Counting is linear in the number of objects, n. Object.entries "
        "then produces one pair per distinct value, k of them, and sorting "
        "those costs k log k — small, because k is how many kinds there "
        "are, not how many things."),
    "js_data_top": Cost(
        "O(n log n)",
        "The sort is the expensive step: n log n in however many survive "
        "the filter, which is at most the whole list, n. filter, slice and "
        "map are each one linear pass or less. Filtering before sorting is "
        "what keeps the sort small."),
}


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)
