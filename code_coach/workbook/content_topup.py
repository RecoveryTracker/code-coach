"""One page each for the calls the language tiers left behind.

After the C, C++, Rust and Dart tiers landed, the coverage measure was run
again rather than assumed. Each language had gone from almost nothing to
most of the way, and each had a short named remainder. These are those
remainders, one page per language.

The Dart one is the least comfortable to write. Those pages taught null
safety at length, covered ?? and ??=, and never once used !, which is the
operator for the case where you know something the compiler cannot prove.
The solution bank uses it constantly.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page


def _page(page_id, number, name, teaches, example, shape, rows,
          language) -> Page:
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
        languages=(language,),
        tier="intermediate",
    )


def _seq(items) -> str:
    return ", ".join(str(n) for n in items)


# ── C: realloc, memcmp, atoi ─────────────────────────────────

_C_ROWS = (
    ((3, 1, 4), 2, "42"), ((2, 7, 1), 3, "17"), ((9, 4, 6), 1, "-8"),
    ((5, 5, 3), 2, "100"), ((1, 2, 3), 4, "7"), ((8, 3, 7), 2, "-25"),
    ((6, 1, 9), 3, "64"), ((4, 8, 2), 1, "9"), ((7, 2, 6), 2, "-3"),
    ((1, 5, 9), 3, "256"), ((2, 4, 6), 2, "11"), ((5, 1, 7), 1, "-60"),
    ((3, 9, 2), 4, "88"), ((8, 2, 4), 2, "5"), ((6, 3, 1), 3, "-14"),
    ((4, 7, 5), 1, "33"), ((9, 6, 2), 2, "70"), ((1, 3, 5), 3, "-1"),
    ((7, 4, 8), 2, "12"), ((2, 9, 1), 1, "45"),
)

C_PAGE = _page(
    "c-more", 89, "Growing memory, comparing it, reading a number",
    "realloc may move the block, so its answer replaces the pointer you "
    "gave it — keeping the old one is how you end up holding an address "
    "that is no longer yours and still looks fine. memcmp compares bytes "
    "and returns a sign rather than a boolean. atoi reads a number out of "
    "text and cannot tell you it failed, which is why strtol exists.",
    "items = realloc(items, grown * sizeof(int)); — assign it back, always, "
    "because the block you had may not be there any more",
    "c_more",
    tuple(
        (f"Allocate {len(v)} ints, copy {{{_seq(v)}}} in, then realloc to "
         f"{len(v) + e} and zero the new slots. Print them, then whether "
         f"the first {len(v)} still match the source, then atoi of "
         f"\"{t}\".",
         {"values": list(v), "extra": e, "text": t})
        for v, e, t in _C_ROWS
    ),
    "c",
)


# ── C++: insert, clear, append, compare ──────────────────────

_CPP_ROWS = (
    ((3, 1, 4), 1, 9, "code", "coach"), ((2, 7, 1), 2, 5, "up", "town"),
    ((9, 4, 6), 1, 2, "sea", "side"), ((5, 5, 3), 2, 8, "note", "book"),
    ((1, 2, 3), 1, 4, "sun", "rise"), ((8, 3, 7), 2, 1, "back", "pack"),
    ((6, 1, 9), 1, 4, "foot", "path"), ((4, 8, 2), 2, 6, "rail", "road"),
    ((7, 2, 6), 1, 3, "moon", "light"), ((1, 5, 9), 2, 7, "key", "board"),
    ((2, 4, 6), 1, 8, "day", "break"), ((5, 1, 7), 2, 9, "over", "flow"),
    ((3, 9, 2), 1, 5, "under", "line"), ((8, 2, 4), 2, 6, "life", "time"),
    ((6, 3, 1), 1, 7, "hand", "made"), ((4, 7, 5), 2, 2, "fire", "wood"),
    ((9, 6, 2), 1, 8, "snow", "fall"), ((1, 3, 5), 2, 4, "water", "mark"),
    ((7, 4, 8), 1, 6, "type", "face"), ((2, 9, 1), 2, 3, "grand", "stand"),
)

CPP_PAGE = _page(
    "cpp-more", 91, "Inserting, clearing, and comparing strings",
    "insert takes an iterator rather than an index, which is why it is "
    "written begin() plus a number, and it moves everything after the "
    "position along. clear empties the vector and keeps the capacity, so "
    "the memory is still held. compare returns a sign like strcmp rather "
    "than a boolean, so the test is against zero.",
    "items.insert(items.begin() + 2, 9); — an iterator, not an index, and "
    "everything from position two moves up one",
    "cpp_more",
    tuple(
        (f"Insert {val} at position {at} of {{{_seq(v)}}} and print the "
         f"result. Then append \"{tail}\" to \"{head}\", print it, print "
         f"whether compare says it equals \"{head}{tail}\", then clear the "
         f"vector and print its size.",
         {"values": list(v), "at": at, "value": val,
          "head": head, "tail": tail})
        for v, at, val, head, tail in _CPP_ROWS
    ),
    "cpp",
)


# ── Rust: into_iter, is_none, get, take ──────────────────────

_RUST_ROWS = (
    ((3, 1, 4), 5, 2), ((2, 7, 1), 4, 2), ((9, 4, 6), 3, 1),
    ((5, 5, 3), 6, 2), ((1, 2, 3), 3, 2), ((8, 3, 7), 7, 1),
    ((6, 1, 9), 4, 2), ((4, 8, 2), 5, 1), ((7, 2, 6), 3, 2),
    ((1, 5, 9), 8, 2), ((2, 4, 6), 3, 1), ((5, 1, 7), 9, 2),
    ((3, 9, 2), 4, 1), ((8, 2, 4), 6, 2), ((6, 3, 1), 3, 2),
    ((4, 7, 5), 5, 1), ((9, 6, 2), 7, 2), ((1, 3, 5), 4, 2),
    ((7, 4, 8), 3, 1), ((2, 9, 1), 6, 2),
)

RUST_PAGE = _page(
    "rust-more", 91, "Consuming an iterator, and asking politely",
    "into_iter hands over the values and consumes what it walked; iter "
    "borrows and leaves it usable. That single choice is most of what "
    "ownership feels like in practice. get returns Option rather than "
    "panicking the way indexing does, so an index past the end is a value "
    "you handle rather than a crash. take stops the chain early and is "
    "lazy, so it costs only what it yields.",
    "items.clone().into_iter() — the clone is there because into_iter "
    "consumes, and items is wanted again on the next line",
    "rust_more",
    tuple(
        (f"Double {{{_seq(v)}}} through into_iter and print the result. "
         f"Then print whether get({at}) is none, the sum of the first "
         f"{take} through take, and the length, which iter left intact.",
         {"values": list(v), "at": at, "take": take})
        for v, at, take in _RUST_ROWS
    ),
    "rust",
)


# ── Dart: the null-assertion operator ────────────────────────

_DART_ROWS = (
    ((("ann", 30), ("bob", 25), ("cy", 5)), "ann", 2),
    ((("red", 4), ("blue", 7), ("green", 2)), "blue", 2),
    ((("one", 1), ("two", 2), ("three", 3)), "three", 1),
    ((("cat", 9), ("dog", 5), ("emu", 3)), "dog", 2),
    ((("north", 1), ("south", 2), ("east", 3)), "east", 2),
    ((("iron", 26), ("tin", 50), ("zinc", 30)), "tin", 1),
    ((("oak", 3), ("elm", 6), ("ash", 9)), "elm", 2),
    ((("salt", 2), ("pepper", 8), ("bay", 4)), "bay", 2),
    ((("rook", 5), ("pawn", 1), ("king", 7)), "pawn", 1),
    ((("mars", 4), ("venus", 2), ("io", 1)), "venus", 2),
    ((("ann", 12), ("bea", 8), ("cal", 4)), "cal", 2),
    ((("red", 1), ("blue", 9), ("jade", 5)), "jade", 1),
    ((("cat", 2), ("dog", 4), ("fox", 6)), "fox", 2),
    ((("up", 3), ("down", 7), ("left", 5)), "down", 2),
    ((("gold", 79), ("lead", 82), ("iron", 26)), "gold", 1),
    ((("elm", 2), ("fir", 5), ("yew", 8)), "yew", 2),
    ((("bay", 1), ("dill", 3), ("sage", 5)), "dill", 2),
    ((("pawn", 2), ("rook", 6), ("bishop", 4)), "rook", 1),
    ((("io", 5), ("titan", 7), ("rhea", 3)), "titan", 2),
    ((("ann", 21), ("cy", 9), ("bob", 15)), "bob", 2),
)

DART_PAGE = _page(
    "dart-more", 91, "The operator for knowing better than the compiler",
    "The null-safety pages covered ?? and ??=, which supply a value when "
    "there is not one. ! is the other move: it asserts there is one. It is "
    "a promise rather than a check, and a wrong promise throws at the exact "
    "line where you said it could not happen — which is the good case, "
    "because the alternative is a null travelling somewhere it will fail "
    "much later and less clearly.",
    "print(ages['ann']!); — the lookup is int? and the ! says you know "
    "this key is there, on your word rather than the compiler's",
    "dart_more",
    tuple(
        (f"Build a Map<String, int> from those pairs, then print "
         f"ages['{key}'] with ! because you know it is there. Then make a "
         f"list of the values with List.from, print the first {take} with "
         f"take, then the length.",
         {"pairs": [list(p) for p in pairs], "key": key, "take": take})
        for pairs, key, take in _DART_ROWS
    ),
    "dart",
)


TOPUP_PAGES: tuple[Page, ...] = (C_PAGE, CPP_PAGE, RUST_PAGE, DART_PAGE)
