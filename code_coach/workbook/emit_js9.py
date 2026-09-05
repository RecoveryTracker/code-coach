"""JavaScript: the library calls the solutions use and the pages did not.

The same audit that found TypeScript missing its runtime found JavaScript
missing a smaller, sharper piece of one. Across three thousand two hundred
JavaScript answers the workbook had never called Math.max, Math.min or
Math.floor, never used pop, shift, delete or values, and never written
repeat or reverse.

Five pages rather than ten, because JavaScript already had Map, Set, and
most of the array methods. This is the top-up, not a tier.

Nothing prints a bare array. Node renders one as `[ 1, 2, 3 ]`, spaces and
all, and these answers are compared as text.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_math", "the number functions, and spreading into them"),
    Shape("js_array_ends", "the four ends, and what each hands back"),
    Shape("js_array_order", "sorting, and the default that is wrong"),
    Shape("js_map_views", "deleting from a Map, and looking at it"),
    Shape("js_string_build", "repeat, pad, split, join"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return "[" + ", ".join(str(n) for n in items) + "]"


def _strs(items) -> str:
    return "[" + ", ".join(f'"{s}"' for s in items) + "]"


# ── 161. Math ────────────────────────────────────────────────


def _math(a: dict) -> str:
    return _lines(
        f"const items = {_nums(a['values'])};",
        "console.log(Math.max(...items));",
        "console.log(Math.min(...items));",
        f"console.log(Math.floor({a['over']} / {a['under']}));",
        f"console.log(Math.abs({a['negative']}));",
    )


# ── 162. The four ends ───────────────────────────────────────


def _array_ends(a: dict) -> str:
    return _lines(
        f"const items = {_nums(a['values'])};",
        f"const grown = items.push({a['pushed']});",
        "console.log(grown);",
        "const last = items.pop();",
        "console.log(last);",
        "const first = items.shift();",
        "console.log(first);",
        f"items.unshift({a['front']});",
        'console.log(items.join(" "));',
    )


# ── 163. Sorting ─────────────────────────────────────────────


def _array_order(a: dict) -> str:
    if a["want"] == "numbers":
        return _lines(
            f"const items = {_nums(a['values'])};",
            "// sort with no comparator compares as text, so 10 sorts",
            "// before 9 and always has.",
            "const lexical = [...items].sort();",
            'console.log(lexical.join(" "));',
            "const proper = [...items].sort((x, y) => x - y);",
            'console.log(proper.join(" "));',
            "console.log([...proper].reverse().join(\" \"));",
        )
    return _lines(
        f"const words = {_strs(a['words'])};",
        "const order = [...words].sort(",
        "  (x, y) => x.length - y.length || x.localeCompare(y),",
        ");",
        'console.log(order.join(" "));',
        'console.log([...order].reverse().join(" "));',
    )


# ── 164. Map views ───────────────────────────────────────────


def _map_views(a: dict) -> str:
    pairs = a["pairs"]
    sets = [f'ages.set("{k}", {v});' for k, v in pairs]
    return _lines(
        "const ages = new Map();",
        *sets,
        f'console.log(ages.delete("{a["dropped"]}"));',
        f'console.log(ages.delete("{a["absent"]}"));',
        "console.log(ages.size);",
        "const values = [...ages.values()];",
        "console.log(values.reduce((sum, n) => sum + n, 0));",
        'console.log([...ages.keys()].sort().join(" "));',
    )


# ── 165. Strings ─────────────────────────────────────────────


def _string_build(a: dict) -> str:
    return _lines(
        f'const unit = "{a["unit"]}";',
        f"console.log(unit.repeat({a['times']}));",
        f'console.log("{a["word"]}".padStart({a["width"]}, "."));',
        f'const parts = "{a["text"]}".split("{a["sep"]}");',
        'console.log(parts.join("-"));',
        "console.log(parts.length);",
    )


_BUILDERS = {
    "js_math": _math,
    "js_array_ends": _array_ends,
    "js_array_order": _array_order,
    "js_map_views": _map_views,
    "js_string_build": _string_build,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out in Python, from the data rather than the JavaScript."""
    a = args
    if shape == "js_math":
        values = list(a["values"])
        over, under, negative = a["over"], a["under"], a["negative"]
        if under == 0:
            raise ValueError("dividing by zero is a different lesson")
        if negative >= 0:
            raise ValueError("abs of a positive number shows nothing")
        if over % under == 0:
            raise ValueError(
                "the division must not come out whole, or floor is "
                "indistinguishable from doing nothing"
            )
        return NL.join([
            str(max(values)), str(min(values)),
            str(over // under), str(abs(negative)),
        ])
    if shape == "js_array_ends":
        values = list(a["values"])
        if len(values) < 2:
            raise ValueError("popping and shifting needs more than one")
        after = values + [a["pushed"]]
        grown = len(after)
        last = after.pop()
        first = after.pop(0)
        after.insert(0, a["front"])
        return NL.join([
            str(grown), str(last), str(first),
            " ".join(str(n) for n in after),
        ])
    if shape == "js_array_order":
        if a["want"] == "numbers":
            values = list(a["values"])
            lexical = sorted(values, key=str)
            proper = sorted(values)
            if lexical == proper:
                raise ValueError(
                    "the default sort must differ from the numeric one, or "
                    "the page does not show the trap it is about"
                )
            return NL.join([
                " ".join(str(n) for n in lexical),
                " ".join(str(n) for n in proper),
                " ".join(str(n) for n in reversed(proper)),
            ])
        words = list(a["words"])
        order = sorted(words, key=lambda w: (len(w), w))
        if order == words:
            raise ValueError("the words must not already be in order")
        if len({len(w) for w in words}) < 2:
            raise ValueError("the words must differ in length")
        return NL.join([" ".join(order), " ".join(reversed(order))])
    if shape == "js_map_views":
        pairs = [tuple(p) for p in a["pairs"]]
        table = dict(pairs)
        if len(table) != len(pairs):
            raise ValueError("a repeated key would hide one of the sets")
        dropped, absent = a["dropped"], a["absent"]
        if dropped not in table:
            raise ValueError("the deleted key must have been there")
        if absent in table:
            raise ValueError(
                "the second delete must miss, or both calls return true "
                "and the page never shows what delete reports"
            )
        del table[dropped]
        if not table:
            raise ValueError("deleting everything leaves nothing to view")
        return NL.join([
            "true", "false", str(len(table)),
            str(sum(table.values())), " ".join(sorted(table)),
        ])
    if shape == "js_string_build":
        unit, times = a["unit"], a["times"]
        word, width = a["word"], a["width"]
        text, sep = a["text"], a["sep"]
        if times < 2:
            raise ValueError("repeating once is not repeating")
        if width <= len(word):
            raise ValueError("the width must exceed the word")
        if sep not in text:
            raise ValueError("the separator must be in the text")
        parts = text.split(sep)
        return NL.join([
            unit * times, word.rjust(width, "."),
            "-".join(parts), str(len(parts)),
        ])
    raise KeyError(shape)
