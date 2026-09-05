"""Pages 161-165: the JavaScript top-up.

The audit found JavaScript in the best shape of the seven languages and
still missing a sharp little set: Math.max, Math.min and Math.floor, pop
and shift, delete and values, repeat and reverse. Three thousand two
hundred answers and none of them.

Five pages rather than a tier, because Map, Set and most of the array
methods were already here. This is what was left.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

JS_ONLY = ("javascript",)


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
        languages=JS_ONLY,
        tier="advanced",
    )


def _seq(items) -> str:
    return ", ".join(str(n) for n in items)


def _wordlist(items) -> str:
    return ", ".join(f'"{w}"' for w in items)


def _pairs_text(pairs) -> str:
    return ", ".join(f"{k}={v}" for k, v in pairs)


# ── 161. Math ────────────────────────────────────────────────

_MATHS = (
    ((3, 9, 2), 7, 2, -5), ((1, 7, 4), 9, 4, -3), ((5, 2, 8), 11, 3, -8),
    ((6, 3, 9), 13, 5, -2), ((2, 8, 1), 17, 6, -7), ((7, 1, 5), 19, 4, -1),
    ((9, 2, 6), 23, 7, -9), ((4, 8, 2), 25, 6, -4), ((1, 6, 3), 29, 8, -6),
    ((8, 3, 7), 31, 9, -5), ((2, 9, 5), 37, 5, -3), ((5, 4, 8), 41, 6, -8),
    ((3, 7, 1), 43, 8, -2), ((6, 2, 4), 47, 9, -7), ((1, 5, 9), 53, 7, -1),
    ((7, 4, 2), 59, 8, -9), ((9, 1, 8), 61, 9, -4), ((2, 6, 4), 67, 8, -6),
    ((4, 1, 7), 71, 9, -5), ((8, 5, 2), 73, 8, -3),
)

MATH_PAGE = _page(
    "js-math", 161, "The number functions, and spreading into them",
    "Math.max takes arguments, not an array, so an array has to be spread "
    "into it — and on a very large array that is what breaks, because it "
    "becomes that many arguments at once. floor rounds toward negative "
    "infinity rather than toward zero, which only shows up once a negative "
    "number turns up.",
    "Math.max(...items) spreads the array into arguments; Math.max(items) "
    "gives NaN and no warning",
    "js_math",
    tuple(
        (f"From {{{_seq(v)}}} print the largest, then the smallest, then "
         f"the floor of {o} / {u}, then the absolute value of {neg}.",
         {"values": list(v), "over": o, "under": u, "negative": neg})
        for v, o, u, neg in _MATHS
    ),
)


# ── 162. The four ends ───────────────────────────────────────

_ENDS = (
    ((3, 1, 4), 9, 7), ((2, 7, 1), 5, 8), ((9, 4, 6), 2, 3),
    ((5, 5, 3), 8, 1), ((1, 2, 3), 4, 6), ((8, 3, 7), 1, 9),
    ((6, 1, 9), 4, 2), ((4, 8, 2), 6, 5), ((7, 2, 6), 3, 4),
    ((1, 5, 9), 2, 7), ((2, 4, 6), 8, 3), ((5, 1, 7), 9, 6),
    ((3, 9, 2), 5, 8), ((8, 2, 4), 7, 1), ((6, 3, 1), 4, 9),
    ((4, 7, 5), 1, 2), ((9, 6, 2), 3, 5), ((1, 3, 5), 6, 4),
    ((7, 4, 8), 2, 6), ((2, 9, 1), 8, 3),
)

ENDS_PAGE = _page(
    "js-array-ends", 162, "The four ends, and what each hands back",
    "push and unshift return the new length, which is easy to miss because "
    "nobody uses it. pop and shift return the element itself, or undefined "
    "when the array was empty. shift and unshift have to move everything "
    "else along, so they cost the length of the array where push and pop "
    "cost nothing.",
    "const grown = items.push(9); — push returns the length, not the "
    "array and not the item",
    "js_array_ends",
    tuple(
        (f"Start with {{{_seq(v)}}}. push {p} and print what push returned, "
         f"then pop and print it, then shift and print that, then unshift "
         f"{f} and print the array space separated.",
         {"values": list(v), "pushed": p, "front": f})
        for v, p, f in _ENDS
    ),
)


# ── 163. Sorting ─────────────────────────────────────────────

_NUMBER_SORTS = (
    (9, 10, 2), (10, 9, 1), (3, 20, 4), (100, 9, 5), (2, 11, 3),
    (30, 4, 7), (9, 100, 8), (12, 3, 6), (5, 40, 9), (11, 2, 8),
)

_WORD_SORTS = (
    ("pear", "fig", "banana", "kiwi"),
    ("cat", "elephant", "dog", "bee"),
    ("red", "yellow", "blue", "cyan"),
    ("one", "seven", "two", "eleven"),
    ("north", "up", "east", "down"),
    ("iron", "tin", "copper", "zinc"),
    ("oak", "willow", "elm", "cedar"),
    ("mars", "io", "venus", "titan"),
    ("salt", "pepper", "bay", "clove"),
    ("rook", "pawn", "bishop", "king"),
)

ORDER_PAGE = _page(
    "js-array-order", 163, "Sorting, and the default that is wrong",
    "sort with no comparator turns every element into text first, so 10 "
    "comes before 9, and it has done since the beginning. It also sorts in "
    "place and returns the same array, which is why these spread into a "
    "copy first. reverse is in place too, and for the same reason.",
    "[...items].sort() gives 10 before 9; [...items].sort((x, y) => x - y) "
    "is what was meant",
    "js_array_order",
    tuple(
        (f"Sort {{{_seq(v)}}} with the bare sort, then with a numeric "
         f"comparator, then print the numeric one reversed. Three lines, "
         f"and the first two differ.",
         {"values": list(v), "want": "numbers"})
        for v in _NUMBER_SORTS
    ) + tuple(
        (f"Sort {{{_wordlist(w)}}} by length, alphabetically where lengths "
         f"tie, then print it reversed.",
         {"words": list(w), "want": "words"})
        for w in _WORD_SORTS
    ),
)


# ── 164. Map views ───────────────────────────────────────────

_VIEWS = (
    ((("ann", 30), ("bob", 25), ("cy", 5)), "bob", "dan"),
    ((("red", 4), ("blue", 7), ("green", 2)), "blue", "pink"),
    ((("one", 1), ("two", 2), ("three", 3)), "two", "four"),
    ((("cat", 9), ("dog", 5), ("emu", 3)), "dog", "fox"),
    ((("north", 1), ("south", 2), ("east", 3)), "south", "west"),
    ((("iron", 26), ("tin", 50), ("zinc", 30)), "tin", "gold"),
    ((("oak", 3), ("elm", 6), ("ash", 9)), "elm", "yew"),
    ((("salt", 2), ("pepper", 8), ("bay", 4)), "bay", "dill"),
    ((("rook", 5), ("pawn", 1), ("king", 7)), "pawn", "queen"),
    ((("mars", 4), ("venus", 2), ("io", 1)), "io", "pluto"),
    ((("ann", 12), ("bea", 8), ("cal", 4)), "bea", "dee"),
    ((("red", 1), ("blue", 9), ("jade", 5)), "jade", "rose"),
    ((("cat", 2), ("dog", 4), ("fox", 6)), "fox", "owl"),
    ((("up", 3), ("down", 7), ("left", 5)), "left", "right"),
    ((("gold", 79), ("lead", 82), ("iron", 26)), "lead", "tin"),
    ((("elm", 2), ("fir", 5), ("yew", 8)), "fir", "oak"),
    ((("bay", 1), ("dill", 3), ("sage", 5)), "sage", "mint"),
    ((("pawn", 2), ("rook", 6), ("bishop", 4)), "rook", "knight"),
    ((("io", 5), ("titan", 7), ("rhea", 3)), "titan", "dione"),
    ((("ann", 21), ("cy", 9), ("bob", 15)), "cy", "eve"),
)

VIEWS_PAGE = _page(
    "js-map-views", 164, "Deleting from a Map, and looking at it",
    "delete returns whether there was anything to delete, which is more "
    "than an array gives you. keys, values and entries are iterators rather "
    "than arrays, so they get spread before anything array-shaped happens "
    "to them — and each one walks in insertion order, which a plain object "
    "does not promise for every kind of key.",
    "ages.delete(k) returns true the first time and false the second; "
    "[...ages.values()] is how you get a real array out",
    "js_map_views",
    tuple(
        (f"Build a Map holding {_pairs_text(ps)}. delete {d!r} and print "
         f"what it returned, then delete {absent!r} which is not there and "
         f"print that, then the size, then the total of the values, then "
         f"the remaining keys sorted.",
         {"pairs": [list(p) for p in ps], "dropped": d, "absent": absent})
        for ps, d, absent in _VIEWS
    ),
)


# ── 165. Strings ─────────────────────────────────────────────

_STRINGS = (
    ("ab", 3, "hi", 5, "a,b,c", ","),
    ("xy", 4, "go", 6, "one two three", " "),
    ("-", 5, "up", 4, "x-y-z", "-"),
    ("ab", 2, "cat", 6, "red,blue", ","),
    ("=", 6, "dog", 7, "up down", " "),
    ("no", 3, "yes", 5, "1:2:3", ":"),
    ("z", 7, "end", 6, "cat,dog,emu", ","),
    ("qp", 2, "on", 5, "north south", " "),
    ("*", 4, "run", 7, "p|q|r", "|"),
    ("mn", 3, "it", 4, "salt,bay", ","),
    ("ab", 5, "top", 6, "a;b;c", ";"),
    ("xy", 2, "in", 5, "left right", " "),
    (".", 8, "out", 7, "1-2-3", "-"),
    ("pq", 3, "at", 4, "iron,tin", ","),
    ("+", 6, "off", 6, "x y z", " "),
    ("rs", 4, "by", 5, "a.b.c", "."),
    ("~", 5, "far", 7, "oak,elm", ","),
    ("tu", 2, "up", 4, "one|two", "|"),
    ("#", 7, "low", 6, "3:4:5", ":"),
    ("vw", 3, "to", 5, "bay,dill", ","),
)

STRING_PAGE = _page(
    "js-string-build", 165, "Repeat, pad, split, join",
    "repeat builds a run, padStart lines a column up and takes the "
    "character to pad with, and split and join are the pair that turns text "
    "into an array and back. padStart counts the total width it wants, not "
    "how much padding to add, which is the part people get backwards.",
    '"hi".padStart(5, ".") gives "...hi" — five wide in total, three dots',
    "js_string_build",
    tuple(
        (f"Print {u!r} repeated {t} times, then {w!r} padded on the left "
         f"with dots to width {n}, then {txt!r} split on {sep!r} and "
         f"rejoined with dashes, then how many parts there were.",
         {"unit": u, "times": t, "word": w, "width": n,
          "text": txt, "sep": sep})
        for u, t, w, n, txt, sep in _STRINGS
    ),
)


JS9_PAGES: tuple[Page, ...] = (
    MATH_PAGE, ENDS_PAGE, ORDER_PAGE, VIEWS_PAGE, STRING_PAGE,
)
