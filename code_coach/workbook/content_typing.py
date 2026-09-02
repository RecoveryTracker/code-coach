"""Intermediate pages 121-130: saying what you mean.

Ten pages that add no new capability at all. Every one of them writes a
program you could already have written on page 100, with the intent said
out loud: a hint that says what a function wants, a dataclass instead of
a hand-written __init__, a dict that already knows what a missing key
should be, a format spec instead of hoping the number looks right.

That is not a small thing. It is roughly the difference between code
that works and code someone else can pick up.

Python only, same as 81-120.
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


def _nums(items) -> str:
    return ", ".join(repr(n) for n in items)


def _call(values) -> str:
    return "(" + ", ".join(repr(v) for v in values) + ")"


# ── 121. Saying what goes in and what comes out ──────────────

_HINTED = (
    ("add", (("a", "int"), ("b", "int")), "int", "a + b", ((2, 3), (10, 4))),
    ("times", (("a", "int"), ("b", "int")), "int", "a * b", ((3, 4), (6, 7))),
    (
        "minus",
        (("first", "int"), ("second", "int")),
        "int",
        "first - second",
        ((10, 3), (5, 9)),
    ),
    ("double", (("n", "int"),), "int", "n * 2", ((7,), (21,))),
    ("square", (("n", "int"),), "int", "n * n", ((6,), (9,))),
    (
        "total",
        (("a", "int"), ("b", "int"), ("c", "int")),
        "int",
        "a + b + c",
        ((1, 2, 3), (10, 20, 30)),
    ),
    (
        "bigger",
        (("a", "int"), ("b", "int")),
        "int",
        "a if a > b else b",
        ((4, 9), (12, 3)),
    ),
    ("half", (("n", "int"),), "int", "n // 2", ((9,), (20,))),
    (
        "rest",
        (("n", "int"), ("d", "int")),
        "int",
        "n % d",
        ((17, 5), (20, 4)),
    ),
    (
        "shift",
        (("n", "int"), ("by", "int")),
        "int",
        "n + by",
        ((5, 3), (100, 25)),
    ),
    (
        "area",
        (("w", "int"), ("h", "int")),
        "int",
        "w * h",
        ((3, 4), (8, 5)),
    ),
    ("thrice", (("n", "int"),), "int", "n * 3", ((4,), (11,))),
)

_P121 = _page(
    "type-hint-func",
    121,
    "Saying what goes in and what comes out",
    "Annotating what a function takes and what it returns.",
    "A colon after an argument says what that argument is meant to be, "
    "and the arrow before the colon on the def line says what comes back. "
    "Python does not check a word of it - hand a string to something "
    "hinted int and it will happily try - so a hint is a note to the next "
    "reader, and to your editor, which will underline the mistake before "
    "you ever run it. Write these and notice that nothing about the "
    "output changed. That is the point: the program is the same, and now "
    "it says what it meant.",
    "type_hint_func",
    [
        (
            "Write a function "
            + name
            + " taking "
            + " and ".join(f"{n} hinted {t}" for n, t in params)
            + ", returning "
            + ret
            + ", whose body returns "
            + expr
            + ". Print the result of calling it with "
            + ", then ".join(_call(c) for c in calls)
            + ".",
            {
                "name": name,
                "params": params,
                "ret": ret,
                "expr": expr,
                "calls": calls,
            },
        )
        for name, params, ret, expr, calls in _HINTED
    ],
)


# ── 122. A hint for a list, and for the answer ───────────────

_LIST_HINTED = (
    ("total", "numbers", "int", "int", "sum(numbers)", ([1, 2, 3], [10, 20])),
    ("how_many", "numbers", "int", "int", "len(numbers)", ([4, 5, 6], [7])),
    ("largest", "numbers", "int", "int", "max(numbers)", ([3, 9, 4], [10, 2])),
    ("smallest", "numbers", "int", "int", "min(numbers)", ([3, 9, 4], [10, 2])),
    (
        "spread",
        "numbers",
        "int",
        "int",
        "max(numbers) - min(numbers)",
        ([1, 9], [4, 4, 10]),
    ),
    (
        "twice_over",
        "numbers",
        "int",
        "int",
        "sum(numbers) * 2",
        ([1, 2], [5, 5]),
    ),
    (
        "ends",
        "numbers",
        "int",
        "int",
        "numbers[0] + numbers[-1]",
        ([1, 2, 3], [10, 5]),
    ),
    (
        "mean_floor",
        "numbers",
        "int",
        "int",
        "sum(numbers) // len(numbers)",
        ([2, 4, 6], [10, 15]),
    ),
    (
        "count_words",
        "words",
        "str",
        "int",
        "len(words)",
        (["ant", "bee"], ["cat"]),
    ),
    (
        "one_short",
        "numbers",
        "int",
        "int",
        "sum(numbers) - 1",
        ([3, 4], [9, 9]),
    ),
    ("last", "numbers", "int", "int", "numbers[-1]", ([1, 2, 3], [8, 4])),
    ("second", "numbers", "int", "int", "numbers[1]", ([5, 6, 7], [1, 2, 3])),
)

_P122 = _page(
    "type-hint-list",
    122,
    "A hint for a list, and for the answer",
    "Hinting what a list holds, not just that it is a list.",
    "list[int] says a list of whole numbers; list[str] says a list of "
    "text. The part in brackets is the useful half - list on its own tells "
    "the reader almost nothing they could not have guessed. Same rule as "
    "the page before: nothing is enforced, everything is documented.",
    "type_hint_list",
    [
        (
            "Write a function "
            + name
            + " taking "
            + param
            + " hinted list["
            + elem
            + "] and returning "
            + ret
            + ", whose body returns "
            + expr
            + ". Print the result for ["
            + _nums(lists[0])
            + "], then for ["
            + _nums(lists[1])
            + "].",
            {
                "name": name,
                "param": param,
                "elem": elem,
                "ret": ret,
                "expr": expr,
                "lists": lists,
            },
        )
        for name, param, elem, ret, expr, lists in _LIST_HINTED
    ],
)


# ── 123. A value that is allowed to be missing ───────────────

_OPTIONAL = (
    ("label", "name", "unknown", ("ada", None, "grace")),
    ("greet", "who", "friend", (None, "sam")),
    ("city_of", "city", "nowhere", ("kyoto", None)),
    ("title_or", "title", "untitled", (None, "dune", None)),
    ("nickname", "given", "nobody", ("finn", None)),
    ("colour", "shade", "plain", (None, "red", "blue")),
    ("team_of", "team", "free agent", ("reds", None)),
    ("show", "text", "empty", (None, "hello")),
    ("author", "who", "anonymous", ("hume", None, "kant")),
    ("pick", "choice", "default", (None, "left")),
    ("host_of", "host", "localhost", ("example", None)),
    ("word_or", "word", "blank", (None, "sky", None)),
)

_P123 = _page(
    "optional-hint",
    123,
    "A value that is allowed to be missing",
    "str | None, and checking for None before using the value.",
    "str | None says: this is text, or it is nothing, and both are fine. "
    "That vertical bar is what turns a crash into a decision - you have "
    "said out loud that None can arrive, so the reader knows to look for "
    "the check, and the checker will complain if you forgot it. Use `is "
    "None`, not `== None`, for the reason page 112 gave: you are asking "
    "about the object, not the value.",
    "optional_hint",
    [
        (
            "Write a function "
            + name
            + " taking "
            + param
            + " hinted str | None and returning str. If "
            + param
            + " is None, return "
            + repr(missing)
            + "; otherwise return "
            + param
            + ". Print the result of calling it with "
            + ", then ".join(repr(v) for v in values)
            + ".",
            {
                "name": name,
                "param": param,
                "missing": missing,
                "values": values,
            },
        )
        for name, param, missing, values in _OPTIONAL
    ],
)


# ── 124. The class with nothing but fields ───────────────────

_DATACLASSES = (
    ("Point", "spot", (("x", "int"), ("y", "int")), (2, 3)),
    ("Size", "size", (("width", "int"), ("height", "int")), (10, 4)),
    ("Book", "book", (("title", "str"), ("pages", "int")), ("Dune", 412)),
    ("Song", "song", (("name", "str"), ("seconds", "int")), ("Alive", 245)),
    ("Coin", "coin", (("face", "str"), ("worth", "int")), ("heads", 25)),
    ("Player", "player", (("name", "str"), ("score", "int")), ("ada", 90)),
    ("Range", "span", (("low", "int"), ("high", "int")), (3, 17)),
    ("City", "city", (("name", "str"), ("people", "int")), ("Kyoto", 1463)),
    ("Card", "card", (("suit", "str"), ("rank", "int")), ("spades", 11)),
    ("Step", "step", (("label", "str"), ("order", "int")), ("mix", 2)),
    ("Room", "room", (("floor", "int"), ("number", "int")), (3, 12)),
    ("Track", "track", (("artist", "str"), ("year", "int")), ("Bowie", 1977)),
)

_P124 = _page(
    "dataclass-basic",
    124,
    "The class with nothing but fields",
    "@dataclass: __init__ and a readable print, written for you.",
    "Page 101 wrote a class that only held values, and __init__ took ten "
    "lines to say each name twice. The decorator writes that for you from "
    "the field list. It also writes __repr__, which is why printing the "
    "object gives you the class name and every field instead of the "
    "0x7f9 nonsense. Watch the last line of each: that is the free one.",
    "dataclass_basic",
    [
        (
            "Import dataclass from dataclasses. Write a dataclass "
            + cls
            + " with fields "
            + " and ".join(f"{n} hinted {t}" for n, t in fields)
            + ". Make one called "
            + var
            + " holding "
            + ", ".join(repr(v) for v in values)
            + ", print each field, then print "
            + var
            + " itself.",
            {"cls": cls, "var": var, "fields": fields, "values": values},
        )
        for cls, var, fields, values in _DATACLASSES
    ],
)


# ── 125. A dataclass that also does something ────────────────

_DATACLASS_METHODS = (
    ("Box", (("width", "int", 3), ("height", "int", 4)), "area", "width * height"),
    ("Rect", (("side", "int", 6), ("other", "int", 5)), "perimeter",
     "2 * (side + other)"),
    ("Span", (("low", "int", 4), ("high", "int", 19)), "size", "high - low"),
    ("Pair", (("first", "int", 7), ("second", "int", 8)), "total",
     "first + second"),
    ("Cube", (("side", "int", 3), ("count", "int", 2)), "volume",
     "side * side * side * count"),
    ("Score", (("points", "int", 40), ("bonus", "int", 7)), "final",
     "points + bonus"),
    ("Split", (("whole", "int", 25), ("parts", "int", 4)), "each",
     "whole // parts"),
    ("Tank", (("full", "int", 60), ("used", "int", 22)), "left",
     "full - used"),
    ("Grid", (("rows", "int", 8), ("cols", "int", 9)), "cells", "rows * cols"),
    ("Trip", (("miles", "int", 120), ("hours", "int", 3)), "speed",
     "miles // hours"),
    ("Wall", (("bricks", "int", 90), ("rows", "int", 6)), "per_row",
     "bricks // rows"),
    ("Bill", (("price", "int", 45), ("people", "int", 3)), "share",
     "price // people"),
)

_P125 = _page(
    "dataclass-method",
    125,
    "A dataclass that also does something",
    "Methods live in a dataclass exactly as they do in any class.",
    "Nothing special here, which is the lesson: a dataclass is a class. "
    "The decorator only wrote __init__ and __repr__ for you; everything "
    "else - methods, self, the lot - works the way pages 102 to 110 "
    "already showed. Fields at the top, blank line, then the method.",
    "dataclass_method",
    [
        (
            "Import dataclass from dataclasses. Write a dataclass "
            + cls
            + " with fields "
            + " and ".join(f"{n} hinted {t}" for n, t, _ in fields)
            + ", and a method "
            + method
            + " taking only self that returns "
            + expr
            + " using self for each field. Make one called thing holding "
            + ", ".join(repr(v) for _, _, v in fields)
            + ", print the method's result, then print thing itself.",
            {"cls": cls, "fields": fields, "method": method, "expr": expr},
        )
        for cls, fields, method, expr in _DATACLASS_METHODS
    ],
)


# ── 126. A dict that starts at zero ──────────────────────────

_DD_COUNT = (
    (("ant", "bee", "ant"), ("ant", "bee", "cow")),
    (("red", "red", "red", "blue"), ("red", "blue", "green")),
    (("a", "b", "c", "a"), ("a", "c", "z")),
    (("cat", "dog", "cat", "cat"), ("cat", "dog", "fox")),
    (("one", "two", "two"), ("two", "one", "six")),
    (("x", "y", "x", "y", "x"), ("x", "y", "w")),
    (("mon", "tue", "mon"), ("mon", "wed")),
    (("pear", "plum", "pear", "fig"), ("pear", "fig", "date")),
    (("up", "down", "up", "up"), ("up", "down", "left")),
    (("north", "south", "north"), ("north", "east")),
    (("do", "re", "mi", "do", "re", "do"), ("do", "re", "fa")),
    (("salt", "pepper", "salt"), ("salt", "sugar")),
)

_P126 = _page(
    "defaultdict-count",
    126,
    "A dict that starts at zero",
    "defaultdict(int), and why the missing key does not crash.",
    "A plain dict raises KeyError the moment you touch a key it has not "
    "seen, so counting means checking first every single time. Hand "
    "defaultdict a function - int, which called with nothing gives 0 - and "
    "it runs that for any key you read that is not there, stores the "
    "result, and carries on. Every page here asks for one key that was "
    "never in the list. That line printing 0 instead of stopping the "
    "program is the whole feature.",
    "defaultdict_count",
    [
        (
            "Import defaultdict from collections. Set words to ["
            + ", ".join(repr(w) for w in words)
            + "]. Make counts a defaultdict(int), loop over words adding one "
            "to counts for each, then print the count for "
            + ", then ".join(repr(k) for k in keys)
            + ".",
            {"words": words, "keys": keys},
        )
        for words, keys in _DD_COUNT
    ],
)


# ── 127. Piling things up by key ─────────────────────────────

_DD_GROUP = (
    (("ant", "ape", "bee"), ("a", "b", "c")),
    (("cat", "cow", "dog", "duck"), ("c", "d", "e")),
    (("red", "rose", "blue"), ("r", "b", "g")),
    (("mint", "moss", "nut"), ("m", "n", "p")),
    (("sun", "sky", "moon"), ("s", "m", "t")),
    (("iron", "ice", "oak"), ("i", "o", "u")),
    (("pear", "plum", "fig"), ("p", "f", "q")),
    (("wolf", "wren", "yak"), ("w", "y", "z")),
    (("east", "elm", "fern"), ("e", "f", "g")),
    (("gold", "grey", "hill"), ("g", "h", "j")),
    (("lake", "lily", "moth"), ("l", "m", "k")),
    (("tea", "toad", "urn"), ("t", "u", "v")),
)

_P127 = _page(
    "defaultdict-group",
    127,
    "Piling things up by key",
    "defaultdict(list), for collecting rather than counting.",
    "Same idea as the page before with a different starting value: list "
    "called with nothing gives an empty list, so reading a key you have "
    "never used hands you one to append to. Grouping is four lines and no "
    "checks. The last key on each of these was never a first letter of "
    "anything - print it and you get [], made on the spot, and now really "
    "in the dict.",
    "defaultdict_group",
    [
        (
            "Import defaultdict from collections. Set words to ["
            + ", ".join(repr(w) for w in words)
            + "]. Make groups a defaultdict(list), loop over words appending "
            "each word to the group for its first letter, then print the "
            "group for "
            + ", then ".join(repr(k) for k in keys)
            + ".",
            {"words": words, "keys": keys},
        )
        for words, keys in _DD_GROUP
    ],
)


# ── 128. Asking for a key that might not be there ────────────

_GETS = (
    ("prices", (("apple", 3), ("pear", 5)), ("apple", "plum"), 0),
    ("ages", (("ada", 36), ("sam", 41)), ("sam", "kim"), 0),
    ("stock", (("nails", 120), ("screws", 40)), ("screws", "bolts"), 0),
    ("scores", (("red", 12), ("blue", 9)), ("red", "blue", "green"), 0),
    ("counts", (("a", 2), ("b", 7)), ("b", "z"), 0),
    ("depths", (("well", 30), ("pond", 4)), ("pond", "sea"), 1),
    ("floors", (("east", 6), ("west", 9)), ("west", "north"), 1),
    ("sizes", (("small", 2), ("large", 8)), ("large", "huge"), 0),
    ("miles", (("home", 0), ("work", 14)), ("work", "gym"), 0),
    ("years", (("bowie", 1977), ("kate", 1985)), ("kate", "brian"), 1900),
    ("seats", (("front", 4), ("back", 5)), ("back", "roof"), 0),
    ("keys", (("c", 1), ("g", 8)), ("g", "f"), 0),
)

_P128 = _page(
    "dict-get-default",
    128,
    "Asking for a key that might not be there",
    "dict.get with a fallback, instead of a KeyError.",
    "Square brackets say the key must be there; get says it might not, "
    "and here is what to use if it is not. The difference matters more "
    "than it looks - get quietly hides a typo in a key name, which is "
    "exactly what you want when the key is genuinely optional and exactly "
    "what you do not want when it is not. Reach for brackets by default "
    "and get when a missing key is a real possibility.",
    "dict_get_default",
    [
        (
            "Set "
            + name
            + " to a dict of "
            + ", ".join(f"{k!r}: {v!r}" for k, v in pairs)
            + ". Print the result of get for "
            + ", then ".join(repr(k) for k in lookups)
            + ", each with a fallback of "
            + repr(default)
            + ".",
            {
                "name": name,
                "pairs": pairs,
                "lookups": lookups,
                "default": default,
            },
        )
        for name, pairs, lookups, default in _GETS
    ],
)


# ── 129. How a number looks when printed ─────────────────────

_FORMATS = (
    (1234567, (",", ">12,")),
    (42, ("5", "05")),
    (3.14159, (".2f", ".4f")),
    (1234.5678, (",.2f", ".1f")),
    (7, ("03", "<4")),
    (0.25, (".0%", ".1%")),
    (999, (",", "06")),
    (2.5, (".1f", ".3f")),
    (1000000, (",", "e")),
    (12, ("+", "+04")),
    (98.6, (".1f", ".0f")),
    (1234, (">8", "08")),
)

_P129 = _page(
    "format-number",
    129,
    "How a number looks when printed",
    "The format spec after the colon inside an f-string.",
    "Everything after the colon inside the braces is a spec, and it is a "
    "small language of its own: a comma groups thousands, .2f fixes two "
    "decimal places, a number sets a width, 0 pads with zeros instead of "
    "spaces, > and < push the value right or left inside that width. They "
    "combine, in that order. This is how a column of numbers stops "
    "looking like a mess, and it beats writing your own padding every "
    "time.",
    "format_number",
    [
        (
            "Set value to "
            + repr(value)
            + ". Print it "
            + ("twice" if len(specs) == 2 else "once")
            + " with an f-string, using the format spec "
            + ", then ".join(repr(s) for s in specs)
            + " after the colon.",
            {"value": value, "specs": specs},
        )
        for value, specs in _FORMATS
    ],
)


# ── 130. Columns that line up ────────────────────────────────

_ROWS = (
    ((("apple", 3), ("pear", 12), ("fig", 7)), 8, 4),
    ((("nails", 120), ("screws", 40)), 10, 5),
    ((("ada", 90), ("sam", 7), ("kim", 41)), 6, 4),
    ((("red", 12), ("blue", 9), ("green", 103)), 7, 5),
    ((("mon", 2), ("tue", 14)), 5, 3),
    ((("north", 6), ("south", 19), ("east", 1)), 9, 4),
    ((("iron", 26), ("gold", 79)), 6, 3),
    ((("do", 1), ("re", 2), ("mi", 3)), 4, 2),
    ((("kyoto", 1463), ("oslo", 709)), 8, 6),
    ((("front", 4), ("back", 55)), 7, 4),
    ((("bowie", 1977), ("kate", 1985), ("brian", 1970)), 8, 6),
    ((("salt", 1), ("pepper", 22), ("sugar", 333)), 9, 5),
)

_P130 = _page(
    "format-row",
    130,
    "Columns that line up",
    "Padding text left and numbers right, in one f-string.",
    "Text reads better pushed left and numbers read better pushed right, "
    "which is why < and > exist and why a table made this way is legible "
    "at a glance. Give the name a width wide enough for the longest one "
    "and the number a width wide enough for the biggest, and every row "
    "lands in the same place. Twelve of these and you will never reach "
    "for a spaces-times-something trick again.",
    "format_row",
    [
        (
            "Set rows to a list of pairs: "
            + ", ".join(f"({n!r}, {c!r})" for n, c in rows)
            + ". Loop over rows unpacking each into name and count, and "
            "print each with an f-string that pads name left in a width of "
            + str(wide)
            + " and count right in a width of "
            + str(num)
            + ".",
            {"rows": rows, "wide": wide, "num": num},
        )
        for rows, wide, num in _ROWS
    ],
)


TYPING_PAGES: tuple[Page, ...] = (
    _P121,
    _P122,
    _P123,
    _P124,
    _P125,
    _P126,
    _P127,
    _P128,
    _P129,
    _P130,
)
