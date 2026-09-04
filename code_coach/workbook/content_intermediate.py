"""The intermediate tier: real Python, built on everything before it.

The beginner pages teach the parts every language has. These teach the parts
Python has — the ones you reach for daily and have to know without looking,
and the ones that make code written by someone who knows the language look
different from code written by someone who has only translated into it.

Python only, for now. JavaScript joins page by page wherever a page has a
real JavaScript answer rather than a translated one.

Nothing here is new *reasoning*: a comprehension is the loop from page 25
written in one line, zip is page 36's two lists, sorted-by-key is page 26's
best-so-far handed to somebody else. Saying so on each page is deliberate —
the point is that the ideas were already yours and this is the notation.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

PYTHON = ("python",)


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
        languages=PYTHON,
        tier="intermediate",
    )


def _list(items) -> str:
    return ", ".join(str(n) for n in items)


def _words(items) -> str:
    return ", ".join(f'"{w}"' for w in items)


# ── 81. Telling an f-string how to print ─────────────────────

_FORMATS = (
    ("pi", 3.14159, ".2f", "to 2 decimal places"),
    ("share", 0.5, ".2f", "to 2 decimal places"),
    ("rate", 1.0 / 3, ".3f", "to 3 decimal places"),
    ("total", 1234.5678, ".1f", "to 1 decimal place"),
    ("price", 9.999, ".2f", "to 2 decimal places"),
    ("tiny", 0.000123, ".4f", "to 4 decimal places"),
    ("big", 98765.4321, ".0f", "with no decimal places"),
    ("half", 0.125, ".3f", "to 3 decimal places"),
    ("third", 2.0 / 3, ".2f", "to 2 decimal places"),
    ("score", 87.5, ".1f", "to 1 decimal place"),
    ("ratio", 1.618034, ".4f", "to 4 decimal places"),
    ("cost", 20.0, ".2f", "to 2 decimal places"),
    ("euler", 2.718281828, ".3f", "to 3 decimal places"),
    ("gravity", 9.80665, ".2f", "to 2 decimal places"),
    ("mile", 1.609344, ".3f", "to 3 decimal places"),
    ("sevenths", 5.0 / 7, ".4f", "to 4 decimal places"),
    ("bill", 47.371, ".2f", "to 2 decimal places"),
    ("huge", 12345.6789, ".0f", "with no decimal places"),
    ("small", 0.004567, ".3f", "to 3 decimal places"),
    ("ninths", 8.0 / 9, ".1f", "to 1 decimal place"),
)

_P81 = _page(
    "fmt-value",
    81,
    "Telling an f-string how to print",
    "A format spec, so a number comes out the way you meant.",
    "Page 12 dropped a value into a line. This says how it should look when "
    "it lands: the bit after the colon inside the braces. Two decimal places "
    "is the one you will type most, and it rounds rather than chopping — "
    "9.999 to two places is 10.00, not 9.99.",
    "fmt_value",
    [
        (
            f'Print one line reading "{label}: " followed by {value!r} '
            f"{described}.",
            {"label": label, "value": value, "spec": spec},
        )
        for label, value, spec, described in _FORMATS
    ],
)


# ── 82. A list in one line ───────────────────────────────────

_COMPREHENSIONS = (
    (1, 5, "i", "each number"),
    (1, 6, "i * i", "each number squared"),
    (1, 10, "i * 2", "each number doubled"),
    (3, 8, "i", "each number"),
    (1, 4, "i * 100", "each number times 100"),
    (1, 7, "i + 10", "each number plus 10"),
    (2, 9, "i * i * i", "each number cubed"),
    (1, 5, "i % 3", "the remainder of each divided by 3"),
    (10, 15, "i - 10", "each number minus 10"),
    (1, 8, "i * 11", "each number times 11"),
    (1, 3, "i * i + 1", "each number squared, plus 1"),
    (5, 12, "i * 5", "each number times 5"),
    (1, 7, "i", "each number"),
    (1, 5, "i * i", "each number squared"),
    (1, 8, "i * 3", "each number times 3"),
    (4, 10, "i", "each number"),
    (1, 6, "i * 50", "each number times 50"),
    (1, 9, "i + 20", "each number plus 20"),
    (1, 4, "i * i * i", "each number cubed"),
    (20, 26, "i - 20", "each number minus 20"),
)

_P82 = _page(
    "comprehension",
    82,
    "A list in one line",
    "The build-a-list loop from page 25, written as one expression.",
    "Exactly page 25: start empty, loop, add. Python writes it as one line "
    "and calls it a comprehension. Read it right to left the first few times "
    "— where the numbers come from, then what happens to each — and note "
    "that the whole list is printed at once, so you see it as Python sees it.",
    "comprehension",
    [
        (
            f"Using a comprehension, build a list of {described} from {lo} to "
            f"{hi}, then print the list.",
            {"lo": lo, "hi": hi, "expr": expr},
        )
        for lo, hi, expr, described in _COMPREHENSIONS
    ],
)


# ── 83. Leaving things out ───────────────────────────────────

_FILTERED = (
    (1, 20, "i", "i % 3 == 0", "divide by 3"),
    (1, 20, "i", "i % 2 == 0", "are even"),
    (1, 30, "i", "i % 10 == 0", "divide by 10"),
    (1, 15, "i * i", "i % 2 == 1", "are odd"),
    (1, 12, "i", "i > 8", "are more than 8"),
    (1, 25, "i", "i % 7 == 0", "divide by 7"),
    (1, 10, "i * 3", "i < 5", "are under 5"),
    (1, 40, "i", "i % 13 == 0", "divide by 13"),
    (1, 9, "i", "i % 4 == 1", "leave 1 over when divided by 4"),
    (1, 18, "i * 2", "i % 6 == 0", "divide by 6"),
    (1, 12, "i", "i > 100", "are more than 100"),
    (1, 16, "i", "i % 5 == 0", "divide by 5"),
    (1, 24, "i", "i % 4 == 0", "divide by 4"),
    (1, 22, "i", "i % 2 == 1", "are odd"),
    (1, 45, "i", "i % 15 == 0", "divide by 15"),
    (1, 12, "i * i", "i % 3 == 0", "divide by 3"),
    (1, 14, "i", "i > 10", "are more than 10"),
    (1, 35, "i", "i % 11 == 0", "divide by 11"),
    (1, 10, "i * 4", "i < 4", "are under 4"),
    (1, 16, "i", "i % 6 == 2", "leave 2 over when divided by 6"),
)

_P83 = _page(
    "comprehension-if",
    83,
    "Leaving things out",
    "A comprehension with a condition on the end.",
    "Page 24's filter, one line. The condition goes last and decides what "
    "gets in; the expression at the front decides what it turns into. One of "
    "these keeps nothing at all and prints an empty list, which is a list.",
    "comprehension_if",
    [
        (
            f"Using a comprehension, build a list of the numbers from {lo} to "
            f"{hi} that {described}"
            + (f", each turned into {expr}" if expr != "i" else "")
            + ", then print it.",
            {"lo": lo, "hi": hi, "expr": expr, "cond": cond},
        )
        for lo, hi, expr, cond, described in _FILTERED
    ],
)


# ── 84. Asking for a key that may not be there ───────────────

_GETS = (
    ((("ann", 30), ("bob", 25)), "ann", 0),
    ((("ann", 30), ("bob", 25)), "cat", 0),
    ((("red", 1), ("green", 2)), "green", -1),
    ((("red", 1), ("green", 2)), "blue", -1),
    ((("one", 1), ("two", 2), ("three", 3)), "three", 99),
    ((("one", 1), ("two", 2), ("three", 3)), "four", 99),
    ((("cat", 4), ("bird", 2)), "bird", 0),
    ((("cat", 4), ("bird", 2)), "fish", 0),
    ((("x", 7),), "x", 100),
    ((("x", 7),), "y", 100),
    ((("start", 1), ("end", 99)), "end", 50),
    ((("start", 1), ("end", 99)), "middle", 50),
    ((("dog", 4), ("cow", 2)), "dog", 0),
    ((("dog", 4), ("cow", 2)), "pig", 0),
    ((("gold", 1), ("silver", 2)), "silver", -1),
    ((("gold", 1), ("silver", 2)), "bronze", -1),
    ((("june", 6), ("july", 7), ("may", 5)), "may", 88),
    ((("june", 6), ("july", 7), ("may", 5)), "april", 88),
    ((("tea", 2), ("coffee", 6)), "coffee", 0),
    ((("tea", 2), ("coffee", 6)), "juice", 0),
)

_P84 = _page(
    "dict-get",
    84,
    "Asking for a key that may not be there",
    "get, and the value to fall back on.",
    "Page 52 looked a key up and assumed it was there. Square brackets on a "
    "missing key stop the program; get hands back the fallback instead. "
    "These come in pairs — one key that is there and one that is not — and "
    "the point is that both print something.",
    "dict_get",
    [
        (
            "Build a table holding "
            + ", ".join(f'"{k}" = {v}' for k, v in pairs)
            + f'. Print what is stored under "{key}", falling back to '
            f"{default} if it is not there.",
            {"pairs": list(pairs), "key": key, "default": default},
        )
        for pairs, key, default in _GETS
    ],
)


# ── 85. Keys and values together ─────────────────────────────

_ITEMS = (
    (("ann", 30), ("bob", 25)),
    (("red", 1), ("green", 2), ("blue", 3)),
    (("one", 1), ("two", 2)),
    (("cat", 4), ("bird", 2), ("fish", 0)),
    (("monday", 1), ("friday", 5)),
    (("x", 10),),
    (("small", 1), ("medium", 5), ("large", 10)),
    (("a", 100), ("b", 200)),
    (("north", 0), ("east", 90), ("south", 180), ("west", 270)),
    (("first", 1), ("second", 2), ("third", 3)),
    (("apple", 3), ("pear", 8)),
    (("start", 0), ("end", 99)),
    (("dog", 4), ("cow", 2)),
    (("gold", 1), ("silver", 2), ("bronze", 3)),
    (("four", 4), ("five", 5)),
    (("tea", 2), ("coffee", 6), ("water", 0)),
    (("june", 6), ("december", 12)),
    (("solo", 9),),
    (("low", 1), ("mid", 50), ("high", 99)),
    (("p", 11), ("q", 22)),
)

_P85 = _page(
    "dict-items",
    85,
    "Keys and values together",
    "Looping over a dict and getting both at once.",
    "items() hands you a pair each time round, and the two names before the "
    "in split it apart — the same unpacking as page 87, met early. The order "
    "is the order you put things in, which Python has guaranteed since 3.7 "
    "and is worth knowing you can rely on.",
    "dict_items",
    [
        (
            "Build a table holding "
            + ", ".join(f'"{k}" = {v}' for k, v in pairs)
            + '. Print one line per entry, reading "key: value".',
            {"pairs": list(pairs)},
        )
        for pairs in _ITEMS
    ],
)


# ── 86. Throwing duplicates away ─────────────────────────────

_DUPES = (
    [3, 1, 3, 2, 1],
    [5, 5, 5, 5],
    [1, 2, 3],
    [10, 20, 10, 30, 20],
    [7],
    [4, 3, 2, 1, 4, 3, 2, 1],
    [100, 50, 100, 50, 25],
    [9, 9, 8, 7, 8],
    [1, 1, 2, 2, 3, 3, 4],
    [42, 17, 42],
    [6, 5, 4, 3, 2, 1],
    [12, 12, 11, 13, 11, 14],
    [8, 2, 8, 5, 2],
    [3, 3, 3],
    [4, 5, 6, 7],
    [30, 40, 30, 50, 40],
    [15],
    [9, 8, 7, 9, 8, 7],
    [200, 100, 200, 100, 75],
    [1, 1, 2, 3, 2, 4],
)

_P86 = _page(
    "unique-sorted",
    86,
    "Throwing duplicates away",
    "A set keeps one of each — and gives up the order doing it.",
    "A set holds each value once, which is exactly what you want and comes "
    "at a price: it has no order at all, and printing one directly gives you "
    "whatever order it felt like. So sort it back into a list before "
    "printing. That is not a workaround; it is the honest way to say what "
    "you actually wanted.",
    "unique_sorted",
    [
        (
            f"Put the numbers {_list(items)} in a list. Print the different "
            f"values it holds, in order, with no repeats.",
            {"items": items},
        )
        for items in _DUPES
    ],
)


# ── 87. Several values at once ───────────────────────────────

_UNPACKS = (
    (("a", "b"), (1, 2)),
    (("x", "y"), (10, 20)),
    (("first", "second", "third"), (1, 2, 3)),
    (("lo", "hi"), (0, 100)),
    (("a", "b", "c"), (7, 8, 9)),
    (("width", "height"), (30, 40)),
    (("one", "two"), (11, 22)),
    (("r", "g", "b"), (255, 128, 0)),
    (("start", "end"), (5, 50)),
    (("a", "b"), (99, 1)),
    (("day", "month", "year"), (1, 9, 2026)),
    (("left", "right"), (3, 3)),
    (("p", "q"), (4, 5)),
    (("lo", "hi"), (12, 90)),
    (("red", "green", "blue"), (10, 20, 30)),
    (("top", "bottom"), (0, 200)),
    (("x", "y", "z"), (2, 4, 6)),
    (("rows", "cols"), (8, 12)),
    (("hour", "minute"), (9, 45)),
    (("a", "b", "c"), (100, 200, 300)),
)

_P87 = _page(
    "tuple-unpack",
    87,
    "Several values at once",
    "Unpacking: one line that names several things.",
    "The names on the left and the values on the right, matched up in order. "
    "This is what page 34's swap was really using — a, b = b, a builds a "
    "pair and takes it apart again, which is why it needs no temporary.",
    "tuple_unpack",
    [
        (
            f"In one line, set {', '.join(names)} to {', '.join(str(v) for v in values)} "
            f"respectively. Then print each of them, in that order.",
            {"names": list(names), "values": list(values)},
        )
        for names, values in _UNPACKS
    ],
)


# ── 88. The position and the item ────────────────────────────

_ENUMERATES = (
    ["red", "green", "blue"],
    ["one", "two"],
    ["a", "b", "c", "d"],
    ["monday", "tuesday", "wednesday"],
    ["first"],
    ["north", "south", "east", "west"],
    ["cat", "dog"],
    ["do", "re", "mi", "fa", "so"],
    ["yes", "no"],
    ["alpha", "beta", "gamma"],
    ["up", "down", "left", "right"],
    ["start", "middle", "end"],
    ["gold", "silver", "bronze"],
    ["four", "five"],
    ["w", "x", "y", "z"],
    ["thursday", "friday", "saturday"],
    ["only"],
    ["spring", "summer", "autumn", "winter"],
    ["tea", "coffee"],
    ["la", "ti", "do"],
)

_P88 = _page(
    "enumerate-loop",
    88,
    "The position and the item",
    "enumerate, so you stop counting by hand.",
    "You have written this by hand: a counter beside the loop, incremented "
    "at the bottom, forgotten once. enumerate hands you both and cannot "
    "forget. It counts from 0, like everything else that counts.",
    "enumerate_loop",
    [
        (
            f"Put the words {_words(words)} in a list. Print one line per "
            f"word, reading the position, a space, then the word.",
            {"words": words},
        )
        for words in _ENUMERATES
    ],
)


# ── 89. Two lists walked as one ──────────────────────────────

_ZIPS = (
    ([1, 2, 3], [10, 20, 30], "x + y", "the two added"),
    ([5, 6], [2, 3], "x * y", "the two multiplied"),
    ([10, 20, 30], [1, 2, 3], "x - y", "the first minus the second"),
    ([2, 4, 6, 8], [1, 1, 1, 1], "x + y", "the two added"),
    ([7, 8, 9], [2, 2, 2], "x % y", "the remainder of the first over the second"),
    ([100, 200], [50, 100], "x - y", "the first minus the second"),
    ([3, 3, 3], [1, 2, 3], "x * y", "the two multiplied"),
    ([1, 2], [100, 200], "x + y", "the two added"),
    ([9, 8, 7, 6], [1, 2, 3, 4], "x * y", "the two multiplied"),
    ([50, 40, 30], [5, 4, 3], "x - y", "the first minus the second"),
    ([4, 5, 6], [4, 5, 6], "x + y", "the two added"),
    ([11, 22, 33], [10, 20, 30], "x - y", "the first minus the second"),
    ([4, 5, 6], [40, 50, 60], "x + y", "the two added"),
    ([7, 8], [3, 4], "x * y", "the two multiplied"),
    ([90, 80, 70], [9, 8, 7], "x - y", "the first minus the second"),
    ([3, 6, 9, 12], [2, 2, 2, 2], "x + y", "the two added"),
    ([19, 23, 29], [5, 5, 5], "x % y", "the remainder of the first over the second"),
    ([500, 250], [100, 50], "x - y", "the first minus the second"),
    ([2, 2, 2], [4, 5, 6], "x * y", "the two multiplied"),
    ([15, 25, 35], [4, 6, 8], "x + y", "the two added"),
)

_P89 = _page(
    "zip-loop",
    89,
    "Two lists walked as one",
    "zip, instead of an index into both.",
    "Page 36 did this with positions because that was all you had. zip hands "
    "you a pair from each list at a time, so the index disappears and with it "
    "every chance of reaching past the end of the shorter one — zip simply "
    "stops when the first list runs out.",
    "zip_loop",
    [
        (
            f"Put {_list(xs)} in one list and {_list(ys)} in another. Using "
            f"zip, print {described} for each pair.",
            {"xs": xs, "ys": ys, "expr": expr},
        )
        for xs, ys, expr, described in _ZIPS
    ],
)


# ── 90. Ordering by something else ───────────────────────────

_SORTS = (
    ["banana", "fig", "apple"],
    ["one", "three", "to"],
    ["a", "bbb", "cc"],
    ["red", "green", "blue"],
    ["do", "re", "mi"],
    ["python", "go", "rust"],
    ["short", "much longer", "mid"],
    ["x", "yy", "zzz", "w"],
    ["cat", "horse", "ox"],
    ["north", "up", "east"],
    ["hello", "hi", "hey"],
    ["alpha", "be", "gamma", "pi"],
    ["elephant", "ant", "otter"],
    ["four", "a", "three"],
    ["zz", "y", "xxx"],
    ["gold", "tin", "silver"],
    ["la", "ti", "solfa"],
    ["java", "c", "kotlin"],
    ["brief", "considerably longer", "middling"],
    ["dd", "e", "fff", "cccc"],
)

_P90 = _page(
    "sorted-key",
    90,
    "Ordering by something else",
    "sorted with a key, when the natural order is not the one you want.",
    "sorted puts words in alphabetical order. Hand it a key and it orders by "
    "whatever that says instead — here, how long each one is. Two words the "
    "same length keep the order they came in, which is worth relying on and "
    "is called a stable sort.",
    "sorted_key",
    [
        (
            f"Put the words {_words(words)} in a list. Print them one per "
            f"line, shortest first.",
            {"words": words, "key": "len"},
        )
        for words in _SORTS
    ],
)


INTERMEDIATE_PAGES: tuple[Page, ...] = (
    _P81,
    _P82,
    _P83,
    _P84,
    _P85,
    _P86,
    _P87,
    _P88,
    _P89,
    _P90,
)
