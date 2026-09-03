"""Intermediate pages 131-140: the shapes data comes in.

Up to here almost everything has been a number, a string, a list or a
dict on its own. Real data is shaped: a record with named fields, a set
you want the overlap of, a dict with a list behind every name, a lump of
JSON that arrived as text. These ten pages are about recognising the
shape and reaching for the thing that fits it.

One rule runs through the block and is worth keeping outside it: a set
has no order and neither does a dict you did not sort, so nothing here
prints one raw. Everything goes through sorted, and json.dumps is always
given sort_keys.

Python only, same as 81-130.
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


def _seq(items) -> str:
    return ", ".join(repr(v) for v in items)


# ── 131. A tuple that knows its own names ────────────────────

_NAMED = (
    ("Point", "spot", (("x", "int"), ("y", "int")), (2, 3)),
    ("Size", "size", (("width", "int"), ("height", "int")), (10, 4)),
    ("Pair", "pair", (("left", "int"), ("right", "int")), (7, 8)),
    ("Song", "song", (("name", "str"), ("seconds", "int")), ("Alive", 245)),
    ("Player", "player", (("name", "str"), ("score", "int")), ("ada", 90)),
    ("Span", "span", (("low", "int"), ("high", "int")), (3, 17)),
    ("City", "city", (("name", "str"), ("people", "int")), ("Kyoto", 1463)),
    ("Card", "card", (("suit", "str"), ("rank", "int")), ("spades", 11)),
    ("Room", "room", (("floor", "int"), ("number", "int")), (3, 12)),
    ("Step", "step", (("label", "str"), ("order", "int")), ("mix", 2)),
    ("Coin", "coin", (("face", "str"), ("worth", "int")), ("heads", 25)),
    ("Track", "track", (("artist", "str"), ("year", "int")), ("Bowie", 1977)),
)

_P131 = _page(
    "namedtuple-use",
    131,
    "A tuple that knows its own names",
    "NamedTuple: a record you can also index and unpack.",
    "This looks like the dataclass from page 124 and prints like one, but "
    "it is a tuple underneath - so spot.x and spot[0] are the same value, "
    "and it unpacks into two variables the way any pair does. The trade "
    "is that a tuple cannot be changed after it is made, which is often "
    "exactly what you want for a record. Reach for NamedTuple when the "
    "thing is a value; reach for a dataclass when it has a life of its "
    "own.",
    "namedtuple_use",
    [
        (
            "Import NamedTuple from typing. Write a NamedTuple "
            + cls
            + " with fields "
            + " and ".join(f"{n} hinted {t}" for n, t in fields)
            + ". Make one called "
            + var
            + " holding "
            + _seq(values)
            + ". Print its "
            + fields[0][0]
            + " by name, then the value at position 1, then "
            + var
            + " itself.",
            {"cls": cls, "var": var, "fields": fields, "values": values},
        )
        for cls, var, fields, values in _NAMED
    ],
)


# ── 132. Sets that combine ───────────────────────────────────

_SETS = (
    ((1, 2, 3), (3, 4)),
    ((5, 6), (6, 7, 8)),
    ((1, 2, 3, 4), (2, 4)),
    ((10, 20), (20, 30)),
    ((1,), (1, 2)),
    ((7, 8, 9), (9,)),
    ((2, 4, 6), (1, 2, 3)),
    ((11, 12, 13), (14, 15)),
    ((1, 3, 5, 7), (5, 7, 9)),
    ((100, 200), (200, 300, 400)),
    ((0, 1), (1, 2, 3)),
    ((21, 22, 23), (22,)),
)

_P132 = _page(
    "set-maths",
    132,
    "Sets that combine",
    "Union, intersection and difference, with | & and -.",
    "Page 86 used a set to throw duplicates away. This is the other half "
    "of why they exist: | is everything in either, & is only what is in "
    "both, and - is what the first has that the second does not. Each of "
    "these would be a loop with a condition, and each is one character "
    "instead. Note that every line prints sorted(...) - a set has no "
    "order, so printing one raw is asking for output you cannot rely on.",
    "set_maths",
    [
        (
            "Set first to the set {"
            + _seq(left)
            + "} and second to {"
            + _seq(right)
            + "}. Print sorted of: the two joined with |, then the two "
            "with &, then first minus second.",
            {"left": left, "right": right},
        )
        for left, right in _SETS
    ],
)


# ── 133. Every other one, and backwards ──────────────────────

_SLICES = (
    ((1, 2, 3, 4, 5, 6), ((None, None, 2), (1, None, 2), (None, None, -1))),
    ((10, 20, 30, 40, 50), ((None, 3, None), (2, None, None), (None, None, -1))),
    ((1, 2, 3, 4, 5, 6, 7, 8), ((None, None, 3), (1, 6, 2), (None, None, -2))),
    ((5, 4, 3, 2, 1), ((None, None, -1), (None, 2, None), (1, 4, None))),
    ((2, 4, 6, 8), ((None, None, 2), (None, None, -1), (1, None, None))),
    ((1, 2, 3), ((None, None, -1), (None, 2, None), (None, None, 2))),
    ((9, 8, 7, 6, 5, 4), ((2, 5, None), (None, None, 2), (None, None, -1))),
    ((11, 22, 33, 44), ((None, None, -1), (1, 3, None), (None, None, 3))),
    ((1, 2, 3, 4, 5), ((1, None, 2), (None, -1, None), (None, None, -1))),
    ((7, 14, 21, 28, 35), ((None, 2, None), (None, None, -2), (3, None, None))),
    ((0, 1, 2, 3, 4, 5), ((None, None, 2), (None, None, -3), (2, 5, 2))),
    ((6, 5, 4, 3), ((None, None, -1), (None, None, 2), (1, None, None))),
)

_P133 = _page(
    "slice-step",
    133,
    "Every other one, and backwards",
    "The third number in a slice, and what a negative one does.",
    "Page 55 took a run out of the middle with two numbers. The third is "
    "the step: 2 takes every other one, 3 every third. Leave the first "
    "two out entirely and you get the whole thing, so [::2] is every "
    "other item of all of it. A negative step walks the other way, which "
    "makes [::-1] the shortest reverse in the language and a thing you "
    "will read in other people's code constantly.",
    "slice_step",
    [
        (
            "Set numbers to ["
            + _seq(items)
            + "]. Print three slices of it: "
            + ", then ".join(
                "["
                + ("" if s[0] is None else str(s[0]))
                + ":"
                + ("" if s[1] is None else str(s[1]))
                + ("" if s[2] is None else ":" + str(s[2]))
                + "]"
                for s in specs
            )
            + ".",
            {"items": items, "specs": specs},
        )
        for items, specs in _SLICES
    ],
)


# ── 134. A dict in one line ──────────────────────────────────

_DICT_COMPS = (
    (("ant", "bee", "cow"), ("ant", "cow")),
    (("apple", "fig"), ("apple", "fig")),
    (("red", "green", "blue"), ("green", "red")),
    (("one", "three"), ("three", "one")),
    (("sun", "moon", "star"), ("moon", "star")),
    (("cat", "kitten"), ("kitten", "cat")),
    (("iron", "gold"), ("iron", "gold")),
    (("north", "east"), ("north", "east")),
    (("mint", "rosemary"), ("rosemary", "mint")),
    (("do", "re", "mi"), ("do", "mi")),
    (("lake", "mountain"), ("mountain", "lake")),
    (("wren", "sparrow"), ("sparrow", "wren")),
)

_P134 = _page(
    "dict-comp",
    134,
    "A dict in one line",
    "The comprehension from page 82, making a dict instead of a list.",
    "Same shape as the list comprehension, with a colon in it: the part "
    "before the colon is the key and the part after is the value. That is "
    "the entire difference. Building a lookup table this way is one line "
    "instead of four, and it reads as what it is - a value worked out for "
    "every key.",
    "dict_comp",
    [
        (
            "Set words to ["
            + _seq(words)
            + "]. Build lengths as a dict comprehension mapping each word "
            "to its length, then print the length stored for "
            + ", then ".join(repr(k) for k in keys)
            + ".",
            {"words": words, "keys": keys},
        )
        for words, keys in _DICT_COMPS
    ],
)


# ── 135. Ordering by the value, not the key ──────────────────

_BY_VALUE = (
    ((("ada", 90), ("sam", 7), ("kim", 41)), True),
    ((("red", 12), ("blue", 9), ("green", 30)), False),
    ((("nails", 120), ("screws", 40), ("bolts", 75)), True),
    ((("mon", 2), ("tue", 14), ("wed", 8)), False),
    ((("north", 6), ("south", 19), ("east", 1)), True),
    ((("iron", 26), ("gold", 79), ("tin", 50)), False),
    ((("apple", 3), ("pear", 12), ("fig", 7)), True),
    ((("kyoto", 1463), ("oslo", 709), ("lima", 998)), False),
    ((("front", 4), ("back", 55), ("side", 20)), True),
    ((("do", 1), ("re", 9), ("mi", 5)), False),
    ((("salt", 11), ("pepper", 22), ("sugar", 3)), True),
    ((("bowie", 1977), ("kate", 1985), ("brian", 1970)), False),
)

_P135 = _page(
    "sort-by-value",
    135,
    "Ordering by the value, not the key",
    "sorted over items, with a key that reaches into the pair.",
    "A dict sorted plainly gives you its keys in order, which is rarely "
    "the question. items() hands you pairs, and a key function that "
    "returns pair[1] sorts by the second half of each - the score, the "
    "count, the price. reverse=True turns a ranking upside down. This is "
    "page 94's key function pointed at a dict, and it is one of the most "
    "useful four lines in the language.",
    "sort_by_value",
    [
        (
            "Set scores to a dict of "
            + ", ".join(f"{k!r}: {v!r}" for k, v in pairs)
            + ". Loop over sorted of scores.items() with a key function "
            "returning pair[1]"
            + (", reverse=True" if reverse else "")
            + ", unpacking into name and score, and print name and score "
            "on one line.",
            {"pairs": pairs, "reverse": reverse},
        )
        for pairs, reverse in _BY_VALUE
    ],
)


# ── 136. A list behind every name ────────────────────────────

_GROUPED = (
    ((("red", (3, 4)), ("blue", (10,))), ("red", "blue")),
    ((("mon", (1, 2, 3)), ("tue", (4,))), ("tue", "mon")),
    ((("east", (5, 5)), ("west", (2, 8))), ("east", "west")),
    ((("ada", (90, 10)), ("sam", (7,))), ("ada", "sam")),
    ((("a", (1,)), ("b", (2, 3))), ("b", "a")),
    ((("front", (4, 4, 4)), ("back", (5,))), ("front", "back")),
    ((("iron", (26,)), ("gold", (79, 1))), ("gold", "iron")),
    ((("do", (1, 2)), ("re", (3, 4))), ("do", "re")),
    ((("north", (6, 1)), ("south", (19,))), ("south", "north")),
    ((("salt", (11,)), ("pepper", (22, 8))), ("pepper", "salt")),
    ((("apple", (3, 3)), ("pear", (12,))), ("apple", "pear")),
    ((("left", (7, 8, 9)), ("right", (1,))), ("right", "left")),
)

_P136 = _page(
    "dict-of-lists",
    136,
    "A list behind every name",
    "Nested data: reaching through a dict into the list it holds.",
    "This is the shape page 127 built with defaultdict, now being read "
    "rather than made. teams[name] is a list, so it does everything a "
    "list does - sum it, count it, loop it - and the only new idea is "
    "that the thing you got out of the dict was not a number. Most real "
    "data is nested like this, and getting comfortable reaching one level "
    "in is most of the battle.",
    "dict_of_lists",
    [
        (
            "Set teams to a dict of "
            + ", ".join(f"{k!r}: [" + _seq(v) + "]" for k, v in groups)
            + ". Loop over the names ["
            + _seq(order)
            + "], printing each name and the sum of its list on one line.",
            {"groups": groups, "order": order},
        )
        for groups, order in _GROUPED
    ],
)


# ── 137. Text in, data out ───────────────────────────────────

_JSON = (
    (("name", "ada"), ("age", 36)),
    (("city", "Kyoto"), ("people", 1463)),
    (("title", "Dune"), ("pages", 412)),
    (("artist", "Bowie"), ("year", 1977)),
    (("colour", "red"), ("count", 12)),
    (("host", "example"), ("port", 8080)),
    (("word", "sky"), ("length", 3)),
    (("team", "reds"), ("score", 41)),
    (("suit", "spades"), ("rank", 11)),
    (("day", "mon"), ("hours", 8)),
    (("metal", "gold"), ("number", 79)),
    (("song", "Alive"), ("seconds", 245)),
)

_P137 = _page(
    "json-round",
    137,
    "Text in, data out",
    "json.loads and json.dumps, and why sort_keys matters.",
    "JSON arrives as one long string and is useless until it is a dict. "
    "loads turns text into data; dumps turns data back into text. The "
    "second is where people get bitten - a dict keeps its insertion "
    "order, so the same data can come out as two different strings and "
    "your diff lights up over nothing. sort_keys=True fixes the order "
    "once and for all. Watch the last line of each: the keys come back "
    "alphabetical, not in the order they went in.",
    "json_round",
    [
        (
            "Import json. Set text to the JSON string for "
            + ", ".join(f"{k!r}: {v!r}" for k, v in pairs)
            + " (in single quotes, so the double quotes inside are fine). "
            "Load it into data, print the value for "
            + " and then ".join(repr(k) for k, _ in pairs)
            + ", then print data dumped back out with sort_keys=True.",
            {"pairs": pairs},
        )
        for pairs in _JSON
    ],
)


# ── 138. Cleaning text up ────────────────────────────────────

_TIDY = (
    ("  Hello World  ", "World", "there", "Hello"),
    ("  Ada Lovelace ", "Ada", "Grace", "Ada"),
    (" RED alert  ", "alert", "warning", "RED"),
    ("  Tokyo Bay ", "Bay", "Tower", "Tokyo"),
    (" Open The Door  ", "Door", "Window", "Open"),
    ("  Cold Water ", "Cold", "Hot", "Cold"),
    (" First Light  ", "Light", "Dark", "First"),
    ("  Long Road ", "Road", "Path", "Long"),
    (" Blue Sky  ", "Sky", "Sea", "Blue"),
    ("  Iron Gate ", "Gate", "Bridge", "Iron"),
    (" Night Train  ", "Train", "Bus", "Night"),
    ("  Green Hill ", "Hill", "Valley", "Green"),
)

_P138 = _page(
    "text-tidy",
    138,
    "Cleaning text up",
    "strip, lower, replace and startswith, one after another.",
    "Text that came from a person or a file is almost never the text you "
    "want: it has spaces on the ends, the wrong case, and a word in it "
    "that has to go. These four methods handle most of that, and the "
    "thing to notice is that none of them change the string - each hands "
    "back a new one, which is why clean = raw.strip() has to store the "
    "result. Calling raw.strip() and expecting raw to change is one of "
    "the most common early mistakes there is.",
    "text_tidy",
    [
        (
            "Set raw to "
            + repr(raw)
            + ", spaces and all. Set clean to raw stripped. Print clean "
            "lowered, then clean with "
            + repr(old)
            + " replaced by "
            + repr(new)
            + ", then whether clean starts with "
            + repr(prefix)
            + ".",
            {"raw": raw, "old": old, "new": new, "prefix": prefix},
        )
        for raw, old, new, prefix in _TIDY
    ],
)


# ── 139. The choice that fits on one line ────────────────────

_TERNARY = (
    ((7, 10), "n % 2 == 0", "even", "odd"),
    ((3, 12), "n > 10", "big", "small"),
    ((0, 5), "n == 0", "zero", "something"),
    ((-4, 9), "n < 0", "below", "above"),
    ((15, 8), "n % 5 == 0", "fives", "not fives"),
    ((100, 3), "n >= 50", "high", "low"),
    ((6, 7), "n % 3 == 0", "thirds", "not thirds"),
    ((1, 2), "n == 1", "one", "more"),
    ((20, 21), "n % 2 == 0", "even", "odd"),
    ((9, 4), "n > 5", "over", "under"),
    ((11, 10), "n % 10 == 0", "round", "ragged"),
    ((2, 30), "n < 10", "digit", "bigger"),
)

_P139 = _page(
    "ternary",
    139,
    "The choice that fits on one line",
    "value if condition else value, as an expression.",
    "The if on page 15 is a statement: it runs one of two blocks. This is "
    "an expression: it produces one of two values, so it can go anywhere "
    "a value can - inside print, inside a list comprehension, as the "
    "right-hand side of an assignment. Read it left to right and it is "
    "almost English. Keep them short; a conditional expression with "
    "another one inside it is a puzzle, not code.",
    "ternary",
    [
        (
            "Loop n over ["
            + _seq(values)
            + "], printing "
            + repr(yes)
            + " if "
            + cond
            + " and otherwise "
            + repr(no)
            + ", using a conditional expression on one line.",
            {"values": values, "cond": cond, "yes": yes, "no": no},
        )
        for values, cond, yes, no in _TERNARY
    ],
)


# ── 140. Two lists into one dict ─────────────────────────────

_ZIPPED = (
    (("ada", "sam", "kim"), (90, 7, 41), ("ada", "kim")),
    (("red", "blue"), (12, 9), ("blue", "red")),
    (("mon", "tue", "wed"), (2, 14, 8), ("wed", "mon")),
    (("apple", "pear"), (3, 12), ("apple", "pear")),
    (("iron", "gold"), (26, 79), ("gold", "iron")),
    (("north", "south"), (6, 19), ("north", "south")),
    (("do", "re", "mi"), (1, 9, 5), ("re", "mi")),
    (("front", "back"), (4, 55), ("back", "front")),
    (("salt", "pepper"), (11, 22), ("pepper", "salt")),
    (("kyoto", "oslo"), (1463, 709), ("oslo", "kyoto")),
    (("left", "right"), (7, 1), ("left", "right")),
    (("bowie", "kate"), (1977, 1985), ("kate", "bowie")),
)

_P140 = _page(
    "zip-to-dict",
    140,
    "Two lists into one dict",
    "dict of zip: the names and the values, joined up.",
    "Page 89 walked two lists together in a loop. Hand the same zip to "
    "dict and you get a lookup table instead - the first list becomes the "
    "keys and the second the values. Data very often arrives as two "
    "parallel lists like this, a header row and a data row being the "
    "obvious case, and this is the one line that turns them into "
    "something you can ask questions of.",
    "zip_to_dict",
    [
        (
            "Set names to ["
            + _seq(names)
            + "] and scores to ["
            + _seq(scores)
            + "]. Build pairs as a dict of zip of the two, then print the "
            "value stored for "
            + ", then ".join(repr(k) for k in lookups)
            + ".",
            {"names": names, "scores": scores, "lookups": lookups},
        )
        for names, scores, lookups in _ZIPPED
    ],
)


SHAPE_PAGES: tuple[Page, ...] = (
    _P131,
    _P132,
    _P133,
    _P134,
    _P135,
    _P136,
    _P137,
    _P138,
    _P139,
    _P140,
)
