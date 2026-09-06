"""The rest of what the Rust solutions reach for.

After the Rust tier and its top-up page, the measure said thirty-six of
sixty-four and named the remainder. It was a long tail of small things
rather than another missing idea, which is the shape a gap has when it is
nearly closed: min and last and enumerate, the entry variant that builds a
collection, the getters that hand back something you can change, and the
character tests that every parsing problem opens with.

Three pages, grouped so each is about something rather than being a list.
Walking with an index and looking at neighbours. Maps whose values change
after they are in. Text turning into numbers and back.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("rust",)

SHAPES: tuple[Shape, ...] = (
    Shape("rust_iter_more", "the index, the neighbours, and the ends"),
    Shape("rust_map_more", "values that change after they are in"),
    Shape("rust_text_more", "characters, digits, and text that is a number"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _ints(items) -> str:
    return ", ".join(str(n) for n in items)


# ── 92. Index, neighbours, ends ──────────────────────────────


def _iter_more(a: dict) -> str:
    return _lines(
        "fn main() {",
        f"    let items = vec![{_ints(a['values'])}];",
        "    let labelled: Vec<String> = items.iter()",
        "        .enumerate()",
        '        .map(|(i, n)| format!("{}:{}", i, n))',
        "        .collect();",
        '    println!("{}", labelled.join(" "));',
        '    println!("{}", items.iter().min().copied().unwrap_or(0));',
        '    println!("{}", items.iter().last().copied().unwrap_or(0));',
        "    // windows hands out overlapping slices, so n values give",
        "    // n - 1 pairs rather than n / 2.",
        "    let pairs: Vec<String> = items.windows(2)",
        "        .map(|w| (w[0] + w[1]).to_string())",
        "        .collect();",
        '    println!("{}", pairs.join(" "));',
        "}",
    )


# ── 93. Values that change once they are in ──────────────────


def _map_more(a: dict) -> str:
    pairs = a["pairs"]
    entries = ", ".join(f"('{k}', {v})" for k, v in pairs)
    key = a["key"]
    return _lines(
        "use std::collections::HashMap;",
        "",
        "fn main() {",
        "    let mut groups: HashMap<char, Vec<i32>> = HashMap::new();",
        f"    for (k, v) in [{entries}] {{",
        "        // or_insert_with builds the empty Vec only when the key",
        "        // is new. or_insert(Vec::new()) would build one every",
        "        // time round and throw most of them away.",
        "        groups.entry(k).or_insert_with(Vec::new).push(v);",
        "    }",
        "    let mut keys: Vec<char> = groups.keys().copied().collect();",
        "    keys.sort();",
        "    let shown: Vec<String> = keys.iter()",
        '        .map(|k| format!("{}{}", k, groups[k].len()))',
        "        .collect();",
        '    println!("{}", shown.join(" "));',
        f"    println!(\"{{}}\", groups.contains_key(&'{key}'));",
        f"    if let Some(list) = groups.get_mut(&'{key}') {{",
        f"        list.push({a['added']});",
        "    }",
        f"    println!(\"{{}}\", groups[&'{key}'].len());",
        f"    println!(\"{{}}\", groups[&'{key}'].last().copied().unwrap_or(0));",
        f"    println!(\"{{}}\", groups.get(&'{a['absent']}').is_some());",
        "}",
    )


# ── 94. Characters, digits, numbers ──────────────────────────


def _text_more(a: dict) -> str:
    text, number, back = a["text"], a["number"], a["back"]
    return _lines(
        "fn main() {",
        f'    let text = "{text}";',
        "    let digits: String = text.chars()",
        "        .filter(|c| c.is_ascii_digit())",
        "        .collect();",
        '    println!("{}", digits);',
        "    // to_digit returns Option, so filter_map drops the letters",
        "    // and unwraps the numbers in one step.",
        "    let total: u32 = text.chars()",
        "        .filter_map(|c| c.to_digit(10))",
        "        .sum();",
        '    println!("{}", total);',
        f'    let n: i32 = "{number}".parse().unwrap();',
        '    println!("{}", (-n).abs());',
        "    // saturating_sub stops at zero instead of wrapping round to",
        "    // a very large number, which is what plain subtraction on an",
        "    // unsigned type would do.",
        f"    let short: usize = {back};",
        f'    println!("{{}}", short.saturating_sub({a["take"]}));',
        "}",
    )


_BUILDERS = {
    "rust_iter_more": _iter_more,
    "rust_map_more": _map_more,
    "rust_text_more": _text_more,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out in Python from the arguments."""
    a = args
    if shape == "rust_iter_more":
        values = list(a["values"])
        if len(values) < 3:
            raise ValueError("windows of two needs at least three to be a walk")
        if values[0] == min(values):
            raise ValueError(
                "the smallest must not be first, or min is the same answer "
                "as reading the front"
            )
        if values[-1] == values[0]:
            raise ValueError("last must differ from first")
        pairs = [values[i] + values[i + 1] for i in range(len(values) - 1)]
        return NL.join([
            " ".join(f"{i}:{n}" for i, n in enumerate(values)),
            str(min(values)),
            str(values[-1]),
            " ".join(str(n) for n in pairs),
        ])
    if shape == "rust_map_more":
        pairs = [tuple(p) for p in a["pairs"]]
        key, added, absent = a["key"], a["added"], a["absent"]
        groups: dict = {}
        for k, v in pairs:
            groups.setdefault(k, []).append(v)
        if key not in groups:
            raise ValueError("the key changed must be in the map")
        if absent in groups:
            raise ValueError(
                "the second lookup must miss, or is_some is true on every "
                "row and the page never shows the other answer"
            )
        if max(len(v) for v in groups.values()) < 2:
            raise ValueError(
                "some key must repeat, or or_insert_with never finds an "
                "existing Vec to push onto"
            )
        if added in groups[key]:
            raise ValueError(
                "the pushed value must be new to that key, or the last "
                "element could have been there already and the row would "
                "pass without get_mut having done anything"
            )
        before = " ".join(f"{k}{len(groups[k])}" for k in sorted(groups))
        return NL.join([
            before, "true", str(len(groups[key]) + 1), str(added), "false",
        ])
    if shape == "rust_text_more":
        text, number, back, take = (a["text"], a["number"], a["back"],
                                    a["take"])
        digits = "".join(c for c in text if c.isdigit())
        if not digits:
            raise ValueError("the text must hold a digit")
        if digits == text:
            raise ValueError(
                "the text must hold something that is not a digit, or the "
                "filter is doing nothing"
            )
        if not number.lstrip("-").isdigit():
            raise ValueError("parse is given something it can read")
        if take <= back:
            raise ValueError(
                "the subtraction must go below zero, or saturating_sub is "
                "indistinguishable from ordinary subtraction"
            )
        return NL.join([
            digits,
            str(sum(int(c) for c in digits)),
            str(abs(int(number))),
            "0",
        ])
    raise KeyError(shape)
