"""TypeScript: the library, which the type pages never got to.

The coverage audit against the TypeScript solution bank found the runtime
missing rather than the types. Across two thousand eight hundred TypeScript
answers the workbook had never written `new Map`, never called `Math.max`,
never used `.pop()` and never reached for `Array.from`. A hundred and forty
pages of generics, narrowing and discriminated unions, and none of the
standard library those types are usually wrapped around.

The reason is structural rather than careless. The TypeScript pages are
TypeScript-only, so a student on that track never sees the JavaScript pages
where Map and Math live. Splitting the tracks split the library out of one
of them.

Ten pages, and they lean on the fact that strict is on. Map.get returns
`V | undefined` whether you like it or not, pop returns `T | undefined`,
and the whole point of doing this in TypeScript rather than JavaScript is
that the compiler will not let those be ignored. So `?? 0` and `!` are not
decoration here, they are the page.

Nothing prints a bare array: Node renders one with spaces inside the
brackets, and these answers are compared as text.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("typescript",)

SHAPES: tuple[Shape, ...] = (
    Shape("ts_map", "a keyed store that admits it might miss"),
    Shape("ts_map_count", "counting with a Map"),
    Shape("ts_set", "membership, and nothing twice"),
    Shape("ts_math", "the number functions, and spreading into them"),
    Shape("ts_array_make", "building an array of a known length"),
    Shape("ts_array_mutate", "the four ends, and what each hands back"),
    Shape("ts_array_order", "sorting, and the default that is wrong"),
    Shape("ts_iterate", "walking a Map"),
    Shape("ts_string", "the string calls worth knowing"),
    Shape("ts_nullish", "when nothing is a value"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return "[" + ", ".join(str(n) for n in items) + "]"


def _strs(items) -> str:
    return "[" + ", ".join(f'"{s}"' for s in items) + "]"


# ── 141. Map ─────────────────────────────────────────────────


def _map(a: dict) -> str:
    pairs, look = a["pairs"], a["look"]
    sets = [f'seen.set("{k}", {v});' for k, v in pairs]
    return _lines(
        "const seen = new Map<string, number>();",
        *sets,
        f'const found = seen.get("{look}");',
        "console.log(found === undefined ? \"missing\" : String(found));",
        f'console.log(seen.has("{look}"));',
        "console.log(seen.size);",
    )


# ── 142. Counting with a Map ─────────────────────────────────


def _map_count(a: dict) -> str:
    return _lines(
        f'const text = "{a["text"]}";',
        "const counts = new Map<string, number>();",
        "for (const ch of text) {",
        "  counts.set(ch, (counts.get(ch) ?? 0) + 1);",
        "}",
        "const keys = [...counts.keys()].sort();",
        "const shown = keys.map((k) => k + String(counts.get(k) ?? 0));",
        'console.log(shown.join(" "));',
    )


# ── 143. Set ─────────────────────────────────────────────────


def _set(a: dict) -> str:
    return _lines(
        f"const items = {_nums(a['values'])};",
        "const seen = new Set<number>(items);",
        f"seen.delete({a['dropped']});",
        "const kept = [...seen].sort((x, y) => x - y);",
        'console.log(kept.join(" "));',
        "console.log(seen.size);",
        f"console.log(seen.has({a['probe']}));",
    )


# ── 144. Math ────────────────────────────────────────────────


def _math(a: dict) -> str:
    values = a["values"]
    return _lines(
        f"const items = {_nums(values)};",
        "console.log(Math.max(...items));",
        "console.log(Math.min(...items));",
        f"console.log(Math.floor({a['over']} / {a['under']}));",
        f"console.log(Math.abs({a['negative']}));",
    )


# ── 145. Building an array ───────────────────────────────────


def _array_make(a: dict) -> str:
    n, step = a["n"], a["step"]
    if a["want"] == "fill":
        return _lines(
            f"const filled: number[] = new Array<number>({n}).fill({step});",
            'console.log(filled.join(" "));',
            "console.log(filled.length);",
        )
    return _lines(
        f"const made = Array.from({{ length: {n} }}, (_, i) => i * {step});",
        'console.log(made.join(" "));',
        "console.log(made.length);",
    )


# ── 146. Push, pop, shift, unshift ───────────────────────────


def _array_mutate(a: dict) -> str:
    return _lines(
        f"const items = {_nums(a['values'])};",
        f"items.push({a['pushed']});",
        "// pop is T | undefined under strict, because the array might",
        "// have been empty. The compiler will not let that be ignored.",
        "const last = items.pop();",
        'console.log(last === undefined ? "none" : String(last));',
        "const first = items.shift();",
        'console.log(first === undefined ? "none" : String(first));',
        f"items.unshift({a['front']});",
        'console.log(items.join(" "));',
    )


# ── 147. Sorting ─────────────────────────────────────────────


def _array_order(a: dict) -> str:
    if a["want"] == "numbers":
        return _lines(
            f"const items = {_nums(a['values'])};",
            "// The default sort compares as text, so 10 lands before 9.",
            "const lexical = [...items].sort();",
            'console.log(lexical.join(" "));',
            "const proper = [...items].sort((x, y) => x - y);",
            'console.log(proper.join(" "));',
        )
    return _lines(
        f"const words = {_strs(a['words'])};",
        "const order = [...words].sort(",
        "  (x, y) => x.length - y.length || x.localeCompare(y),",
        ");",
        'console.log(order.join(" "));',
        "const back = [...order].reverse();",
        'console.log(back.join(" "));',
    )


# ── 148. Walking a Map ───────────────────────────────────────


def _iterate(a: dict) -> str:
    pairs = a["pairs"]
    sets = [f'ages.set("{k}", {v});' for k, v in pairs]
    return _lines(
        "const ages = new Map<string, number>();",
        *sets,
        "const names: string[] = [];",
        "let total = 0;",
        "for (const [name, age] of ages) {",
        "  names.push(name);",
        "  total += age;",
        "}",
        'console.log(names.sort().join(" "));',
        "console.log(total);",
        "console.log([...ages.values()].length);",
    )


# ── 149. Strings ─────────────────────────────────────────────


def _string(a: dict) -> str:
    if a["want"] == "repeat":
        return _lines(
            f'const unit = "{a["unit"]}";',
            f"console.log(unit.repeat({a['times']}));",
            f'console.log("{a["word"]}".padStart({a["width"]}, "."));',
        )
    return _lines(
        f'const text = "{a["text"]}";',
        f'const parts = text.split("{a["sep"]}");',
        'console.log(parts.join("-"));',
        "console.log(parts.length);",
        f"console.log(text.slice(0, {a['cut']}));",
    )


# ── 150. When nothing is a value ─────────────────────────────


def _nullish(a: dict) -> str:
    return _lines(
        "const store = new Map<string, number>();",
        f'store.set("{a["key"]}", {a["value"]});',
        "// ?? falls back only on null or undefined. || falls back on",
        "// every falsy value, which includes 0, and that difference is",
        "// where the bug lives when a real count happens to be zero.",
        f'const found = store.get("{a["key"]}");',
        f"console.log(found ?? {a['fallback']});",
        f"console.log(found || {a['fallback']});",
        f'const missing = store.get("{a["absent"]}");',
        f"console.log(missing ?? {a['fallback']});",
    )


_BUILDERS = {
    "ts_map": _map,
    "ts_map_count": _map_count,
    "ts_set": _set,
    "ts_math": _math,
    "ts_array_make": _array_make,
    "ts_array_mutate": _array_mutate,
    "ts_array_order": _array_order,
    "ts_iterate": _iterate,
    "ts_string": _string,
    "ts_nullish": _nullish,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out in Python, from the data rather than the TypeScript.

    The guards mostly ask whether the distinction a page exists for is
    visible in its data. A nullish page whose value is not zero does not
    show the difference between ?? and ||. A sort page whose numbers are
    all one digit does not show that the default sort is wrong.
    """
    a = args
    if shape == "ts_map":
        pairs = [tuple(p) for p in a["pairs"]]
        look = a["look"]
        table = dict(pairs)
        if len(table) != len(pairs):
            raise ValueError("a repeated key would hide one of the sets")
        found = table.get(look)
        return NL.join([
            "missing" if found is None else str(found),
            "true" if look in table else "false",
            str(len(table)),
        ])
    if shape == "ts_map_count":
        text = a["text"]
        if len(set(text)) == len(text):
            raise ValueError(
                "some character must repeat, or every count is one and the "
                "fallback never has anything to add to"
            )
        counts: dict = {}
        for ch in text:
            counts[ch] = counts.get(ch, 0) + 1
        return " ".join(f"{k}{counts[k]}" for k in sorted(counts))
    if shape == "ts_set":
        values, dropped, probe = list(a["values"]), a["dropped"], a["probe"]
        if len(set(values)) == len(values):
            raise ValueError(
                "the input must repeat something, or the Set is doing "
                "nothing a plain array was not already doing"
            )
        if dropped not in set(values):
            raise ValueError("the deleted value must have been there")
        kept = sorted(set(values) - {dropped})
        return NL.join([
            " ".join(str(n) for n in kept),
            str(len(kept)),
            "true" if probe in kept else "false",
        ])
    if shape == "ts_math":
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
    if shape == "ts_array_make":
        n, step = a["n"], a["step"]
        if n < 2:
            raise ValueError("a length of one shows no pattern")
        if a["want"] == "fill":
            return NL.join([" ".join([str(step)] * n), str(n)])
        if step == 0:
            raise ValueError("a step of zero makes every element the same")
        return NL.join([" ".join(str(i * step) for i in range(n)), str(n)])
    if shape == "ts_array_mutate":
        values = list(a["values"])
        if len(values) < 2:
            raise ValueError("popping and shifting needs more than one")
        after = values + [a["pushed"]]
        last = after.pop()
        first = after.pop(0)
        after.insert(0, a["front"])
        return NL.join([
            str(last), str(first), " ".join(str(n) for n in after),
        ])
    if shape == "ts_array_order":
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
            ])
        words = list(a["words"])
        order = sorted(words, key=lambda w: (len(w), w))
        if order == words:
            raise ValueError("the words must not already be in order")
        if len({len(w) for w in words}) < 2:
            raise ValueError("the words must differ in length")
        return NL.join([" ".join(order), " ".join(reversed(order))])
    if shape == "ts_iterate":
        pairs = [tuple(p) for p in a["pairs"]]
        table = dict(pairs)
        if len(table) != len(pairs):
            raise ValueError("a repeated key would hide one of the sets")
        if len(table) < 2:
            raise ValueError("walking one entry is not walking")
        return NL.join([
            " ".join(sorted(table)), str(sum(table.values())),
            str(len(table)),
        ])
    if shape == "ts_string":
        if a["want"] == "repeat":
            unit, times = a["unit"], a["times"]
            word, width = a["word"], a["width"]
            if times < 2:
                raise ValueError("repeating once is not repeating")
            if width <= len(word):
                raise ValueError(
                    "the width must exceed the word, or padStart pads "
                    "nothing and the page shows nothing"
                )
            return NL.join([unit * times, word.rjust(width, ".")])
        text, sep, cut = a["text"], a["sep"], a["cut"]
        if sep not in text:
            raise ValueError("the separator must be in the text")
        parts = text.split(sep)
        if not 0 < cut < len(text):
            raise ValueError("the slice must take part of the text")
        return NL.join(["-".join(parts), str(len(parts)), text[:cut]])
    if shape == "ts_nullish":
        value, fallback = a["value"], a["fallback"]
        if value != 0:
            raise ValueError(
                "the stored value must be zero, or ?? and || agree and the "
                "page is about a difference it never shows"
            )
        if fallback == 0:
            raise ValueError("a fallback of zero is indistinguishable")
        return NL.join([str(value), str(fallback), str(fallback)])
    raise KeyError(shape)
