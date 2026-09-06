"""Pages 92-94: the rest of what the Rust solutions reach for.

After the tier and its top-up, the measure said thirty-six of sixty-four
and named what was left. A long tail of small things rather than a missing
idea, which is what a nearly-closed gap looks like.

Three pages, grouped so each is about something. The index and the
neighbours and the ends. Maps whose values change after they are in. Text
that turns into numbers.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

RUST_ONLY = ("rust",)


def _page(page_id, number, name, teaches, example, shape, rows) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(
            Exercise(
                id=f"{page_id}-{i + 1:02d}",
                prompt=prompt,
                shape=shape,
                args=args,
            )
            for i, (prompt, args) in enumerate(rows)
        ),
        languages=RUST_ONLY,
        tier="intermediate",
    )


def _seq(items) -> str:
    return ", ".join(str(n) for n in items)


# ── 92. Index, neighbours, ends ──────────────────────────────
#
# No list starts with its own smallest, so min is never the same answer
# as reading the front.

_WALKS = (
    (3, 1, 4, 2), (5, 2, 8, 3), (9, 4, 6, 1), (7, 3, 5, 2),
    (6, 1, 9, 4), (8, 2, 7, 5), (4, 1, 6, 3), (9, 5, 2, 7),
    (5, 3, 8, 1), (7, 2, 6, 4), (3, 1, 5, 9, 2), (8, 4, 2, 6, 3),
    (6, 2, 9, 1, 5), (9, 3, 7, 2, 4), (5, 1, 8, 3, 6),
    (7, 4, 1, 9, 2), (4, 2, 6, 1, 8), (8, 3, 9, 2, 5),
    (6, 1, 4, 7, 3), (9, 2, 5, 1, 8),
)

WALK_PAGE = _page(
    "rust-iter-more", 92, "The index, the neighbours, and the ends",
    "enumerate pairs each item with its position and hands both over at "
    "once, which is why the closure destructures a tuple. windows gives "
    "overlapping slices, so n items make n minus one pairs rather than "
    "half as many — chunks is the one that splits without overlapping. min "
    "and last both return Option, because a sequence might be empty.",
    "items.windows(2) gives overlapping pairs, so four values make three "
    "of them — chunks(2) would make two and share nothing",
    "rust_iter_more",
    tuple(
        (f"Take {{{_seq(v)}}}. Print each value with its index as i:n on "
         f"one line, then the smallest, then the last, then the sum of "
         f"each neighbouring pair using windows.",
         {"values": list(v)})
        for v in _WALKS
    ),
)


# ── 93. Values that change once they are in ──────────────────

_GROUPS = (
    ((("a", 1), ("b", 2), ("a", 3)), "a", 9, "z"),
    ((("x", 4), ("y", 5), ("x", 6)), "x", 1, "q"),
    ((("m", 2), ("n", 7), ("m", 8)), "m", 3, "w"),
    ((("p", 5), ("q", 1), ("p", 2)), "p", 7, "k"),
    ((("c", 3), ("d", 9), ("c", 4)), "c", 6, "v"),
    ((("e", 8), ("f", 2), ("e", 5)), "e", 4, "j"),
    ((("g", 1), ("h", 6), ("g", 7)), "g", 2, "u"),
    ((("i", 9), ("k", 3), ("i", 1)), "i", 8, "t"),
    ((("l", 4), ("m", 8), ("l", 6)), "l", 5, "s"),
    ((("n", 2), ("o", 5), ("n", 9)), "n", 1, "r"),
    ((("a", 6), ("b", 1), ("b", 4)), "b", 3, "y"),
    ((("c", 7), ("d", 2), ("d", 9)), "d", 5, "x"),
    ((("e", 1), ("f", 8), ("f", 3)), "f", 6, "w"),
    ((("g", 5), ("h", 4), ("h", 7)), "h", 2, "v"),
    ((("i", 3), ("j", 9), ("j", 1)), "j", 8, "u"),
    ((("k", 8), ("l", 2), ("l", 6)), "l", 4, "t"),
    ((("m", 4), ("n", 7), ("n", 3)), "n", 9, "s"),
    ((("o", 9), ("p", 1), ("p", 5)), "p", 7, "r"),
    ((("q", 2), ("r", 6), ("r", 8)), "r", 1, "z"),
    ((("s", 7), ("t", 3), ("t", 2)), "t", 6, "y"),
)

MAP_PAGE = _page(
    "rust-map-more", 93, "Values that change once they are in",
    "or_insert_with takes a function and calls it only when the key is "
    "new, so the empty Vec is built once rather than built and discarded "
    "on every repeat. get_mut hands back a reference you can change "
    "through, which get does not — and the borrow checker allows exactly "
    "one of those at a time, which is the whole reason there are two "
    "methods rather than one.",
    "groups.entry(k).or_insert_with(Vec::new).push(v); — the function is "
    "not called when the key is already there",
    "rust_map_more",
    tuple(
        (f"Group those pairs into a HashMap<char, Vec<i32>> with "
         f"or_insert_with. Print each key and how many it holds, then "
         f"whether '{key}' is present, then push {added} through get_mut "
         f"and print the new length and the last value, then whether "
         f"'{absent}' is there.",
         {"pairs": [list(p) for p in pairs], "key": key,
          "added": added, "absent": absent})
        for pairs, key, added, absent in _GROUPS
    ),
)


# ── 94. Text that is a number ────────────────────────────────

_TEXTS = (
    ("a1b2", "42", 3, 10), ("x9y8", "-17", 2, 7), ("no7go8", "100", 4, 9),
    ("room402", "-5", 1, 6), ("k3l5", "88", 2, 8), ("z6a2", "-64", 3, 11),
    ("p1q9", "256", 5, 12), ("m4n7", "-9", 2, 5), ("b8c3", "31", 4, 10),
    ("d2e6", "-77", 1, 4), ("f5g1", "12", 3, 9), ("h9i4", "-45", 2, 6),
    ("j3k8", "60", 5, 13), ("l7m2", "-3", 1, 8), ("n6o9", "144", 4, 11),
    ("q1r5", "-28", 2, 7), ("s8t4", "19", 3, 10), ("u2v7", "-51", 1, 5),
    ("w4x6", "73", 5, 12), ("y9z1", "-6", 2, 9),
)

TEXT_PAGE = _page(
    "rust-text-more", 94, "Characters, digits, and text that is a number",
    "to_digit returns Option because not every character is one, so "
    "filter_map drops the letters and unwraps the numbers in a single "
    "pass. parse needs to know the type it is aiming at and returns Result "
    "rather than the number. saturating_sub stops at zero where ordinary "
    "subtraction on an unsigned type wraps round to something enormous, "
    "which is a bug that looks like a working program.",
    "text.chars().filter_map(|c| c.to_digit(10)).sum::<u32>() — filter and "
    "unwrap at once, because to_digit already returns the Option",
    "rust_text_more",
    tuple(
        (f"From {t!r} collect the digits into a String and print it, then "
         f"their total using to_digit. Then parse {n!r}, print the "
         f"absolute value of its negation, then print {b} saturating_sub "
         f"{k}, which cannot go below zero.",
         {"text": t, "number": n, "back": b, "take": k})
        for t, n, b, k in _TEXTS
    ),
)


RUST3_PAGES: tuple[Page, ...] = (WALK_PAGE, MAP_PAGE, TEXT_PAGE)
