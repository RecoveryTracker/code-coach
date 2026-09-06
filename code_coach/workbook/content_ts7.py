"""Pages 141-150: the TypeScript library.

A hundred and forty TypeScript pages taught generics, narrowing and
discriminated unions, and across two thousand eight hundred answers never
once wrote `new Map`, called `Math.max`, used `.pop()` or reached for
`Array.from`. The types were covered and the things people put types on
were not.

The cause is structural. TypeScript pages are TypeScript-only, so a student
working that track never reaches the JavaScript pages where Map and Math
were taught. Splitting the tracks split the library out of one of them.

Ten pages, and strict being on is what makes them worth doing in TypeScript
rather than JavaScript. Map.get returns `V | undefined` and pop returns
`T | undefined`, and the compiler will not let either be waved through. So
`?? 0` is not a flourish here, it is the reason the page exists.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

TS_ONLY = ("typescript",)


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
        languages=TS_ONLY,
        tier="intermediate",
    )


def _seq(items) -> str:
    return ", ".join(str(n) for n in items)


def _pairs_text(pairs) -> str:
    return ", ".join(f"{k}={v}" for k, v in pairs)


def _wordlist(items) -> str:
    return ", ".join(f'"{w}"' for w in items)


# ── 141. Map ─────────────────────────────────────────────────
#
# Half the rows look up a key that is not there, so `undefined` is
# something you have watched come back rather than been warned about.

_MAPS = (
    ((("ann", 30), ("bob", 25)), "ann"),
    ((("ann", 30), ("bob", 25)), "cy"),
    ((("red", 4), ("blue", 7), ("green", 2)), "blue"),
    ((("red", 4), ("blue", 7)), "pink"),
    ((("one", 1), ("two", 2), ("three", 3)), "three"),
    ((("one", 1), ("two", 2)), "four"),
    ((("cat", 9), ("dog", 5)), "cat"),
    ((("cat", 9), ("dog", 5)), "bird"),
    ((("north", 1), ("south", 2), ("east", 3)), "east"),
    ((("north", 1), ("south", 2)), "west"),
    ((("iron", 26), ("tin", 50)), "tin"),
    ((("iron", 26), ("tin", 50)), "zinc"),
    ((("oak", 3), ("elm", 6), ("ash", 9)), "elm"),
    ((("oak", 3), ("elm", 6)), "yew"),
    ((("salt", 2), ("pepper", 8)), "salt"),
    ((("salt", 2), ("pepper", 8)), "bay"),
    ((("rook", 5), ("pawn", 1), ("king", 0)), "pawn"),
    ((("rook", 5), ("pawn", 1)), "queen"),
    ((("mars", 4), ("venus", 2)), "venus"),
    ((("mars", 4), ("venus", 2)), "pluto"),
)

MAP_PAGE = _page(
    "ts-map", 141, "A keyed store that admits it might miss",
    "A Map is keyed by anything, not only strings, and it keeps its size "
    "without counting. get returns the value or undefined, and under strict "
    "that union is the type: you cannot use what came back until you have "
    "said what happens when there is nothing there.",
    "const seen = new Map<string, number>(); and seen.get(k) is number | "
    "undefined, not number",
    "ts_map",
    tuple(
        (f"Build a Map<string, number> holding {_pairs_text(ps)}. Look up "
         f'"{look}" and print the value or the word missing, then whether '
         f"the key is there, then the size.",
         {"pairs": [list(p) for p in ps], "look": look})
        for ps, look in _MAPS
    ),
)


# ── 142. Counting with a Map ─────────────────────────────────

_TEXTS = (
    "banana", "mississippi", "letter", "success", "coffee", "balloon",
    "committee", "possess", "running", "little", "bookkeeper", "address",
    "tomorrow", "different", "necessary", "beginning", "parallel",
    "occurred", "access", "sheep",
)

COUNT_PAGE = _page(
    "ts-map-count", 142, "Counting with a Map",
    "The counting idiom, and the reason ?? exists. get hands back undefined "
    "the first time a character appears, so the fallback is what turns that "
    "into a number you can add one to. Every hash-map solution in the bank "
    "is built out of this one line.",
    "counts.set(ch, (counts.get(ch) ?? 0) + 1); — the ?? 0 is what makes "
    "the first sighting work",
    "ts_map_count",
    tuple(
        (f"Count how often each character appears in {t!r} using a "
         f"Map<string, number>. Print them in order of character as "
         f"letter-then-count, space separated.", {"text": t})
        for t in _TEXTS
    ),
)


# ── 143. Set ─────────────────────────────────────────────────

_SETS = (
    ((3, 1, 4, 1, 5), 4, 3), ((2, 7, 2, 8), 8, 7), ((9, 4, 9, 6), 6, 4),
    ((5, 5, 3, 1), 3, 5), ((1, 2, 2, 3), 2, 3), ((8, 3, 8, 7), 7, 3),
    ((6, 1, 6, 9), 9, 1), ((4, 8, 4, 2), 2, 8), ((7, 2, 7, 6), 6, 2),
    ((1, 5, 1, 9), 9, 5), ((2, 4, 4, 8), 8, 2), ((5, 1, 5, 7), 7, 1),
    ((3, 9, 3, 2), 2, 9), ((8, 2, 8, 4), 4, 2), ((6, 3, 6, 1), 1, 3),
    ((4, 7, 4, 5), 5, 7), ((9, 6, 9, 2), 2, 6), ((1, 3, 1, 5), 5, 3),
    ((7, 4, 7, 8), 8, 4), ((2, 9, 2, 1), 1, 9),
)

SET_PAGE = _page(
    "ts-set", 143, "Membership, and nothing twice",
    "A Set built from an array drops the repeats for you, which is the "
    "shortest way to say unique in this language. has is constant where "
    "includes on an array is a scan, and that difference is the whole "
    "reason the solutions reach for one.",
    "const seen = new Set<number>(items); and [...seen] spreads it back "
    "into an array you can sort",
    "ts_set",
    tuple(
        (f"Build a Set from {{{_seq(v)}}}, delete {d}, then print what is "
         f"left in ascending order, the size, and whether {p} is still "
         f"there.", {"values": list(v), "dropped": d, "probe": p})
        for v, d, p in _SETS
    ),
)


# ── 144. Math ────────────────────────────────────────────────

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
    "ts-math", 144, "The number functions, and spreading into them",
    "Math.max takes arguments rather than an array, so an array has to be "
    "spread into it — and on a very large array that spread is what breaks, "
    "because it becomes that many arguments. floor rounds toward negative "
    "infinity rather than toward zero, which matters the moment a negative "
    "number turns up.",
    "Math.max(...items) spreads the array into arguments; Math.max(items) "
    "would be NaN",
    "ts_math",
    tuple(
        (f"From {{{_seq(v)}}} print the largest, then the smallest, then "
         f"the floor of {o} / {u}, then the absolute value of {neg}.",
         {"values": list(v), "over": o, "under": u, "negative": neg})
        for v, o, u, neg in _MATHS
    ),
)


# ── 145. Building an array ───────────────────────────────────

_FILLS = (
    (4, 3), (5, 0), (3, 7), (6, 1), (4, 9), (7, 2), (3, 5), (5, 4),
    (6, 8), (4, 6),
)

_FROMS = (
    (5, 2), (4, 3), (6, 1), (3, 5), (7, 2), (5, 4), (4, 7), (6, 3),
    (3, 9), (5, 6),
)

MAKE_PAGE = _page(
    "ts-array-make", 145, "Building an array of a known length",
    "new Array(n) makes n holes rather than n values, and map skips holes, "
    "so it has to be filled before it is any use. Array.from with a length "
    "object and a function is the one that builds and computes in a single "
    "step, and it is the one the solutions use.",
    "Array.from({ length: n }, (_, i) => i * step) — the second argument "
    "gets the index, which is where the pattern comes from",
    "ts_array_make",
    tuple(
        (f"Make an array of {n} copies of {s} with new Array and fill. "
         f"Print it space separated, then its length.",
         {"n": n, "step": s, "want": "fill"})
        for n, s in _FILLS
    ) + tuple(
        (f"Use Array.from to build {n} values where position i holds "
         f"i * {s}. Print it space separated, then its length.",
         {"n": n, "step": s, "want": "from"})
        for n, s in _FROMS
    ),
)


# ── 146. The four ends ───────────────────────────────────────

_MUTATES = (
    ((3, 1, 4), 9, 7), ((2, 7, 1), 5, 8), ((9, 4, 6), 2, 3),
    ((5, 5, 3), 8, 1), ((1, 2, 3), 4, 6), ((8, 3, 7), 1, 9),
    ((6, 1, 9), 4, 2), ((4, 8, 2), 6, 5), ((7, 2, 6), 3, 4),
    ((1, 5, 9), 2, 7), ((2, 4, 6), 8, 3), ((5, 1, 7), 9, 6),
    ((3, 9, 2), 5, 8), ((8, 2, 4), 7, 1), ((6, 3, 1), 4, 9),
    ((4, 7, 5), 1, 2), ((9, 6, 2), 3, 5), ((1, 3, 5), 6, 4),
    ((7, 4, 8), 2, 6), ((2, 9, 1), 8, 3),
)

MUTATE_PAGE = _page(
    "ts-array-mutate", 146, "The four ends, and what each hands back",
    "push and unshift return the new length; pop and shift return the "
    "element, or undefined when there was not one, which under strict you "
    "have to handle. shift and unshift move everything else along, so they "
    "are linear where push and pop are constant.",
    "const last = items.pop(); makes last number | undefined, and the "
    "compiler will not let you print it without saying which",
    "ts_array_mutate",
    tuple(
        (f"Start with {{{_seq(v)}}}. push {p}, then pop and print what came "
         f"back, then shift and print that, then unshift {f} and print the "
         f"array space separated. Print the word none if a pop or shift "
         f"gives nothing.",
         {"values": list(v), "pushed": p, "front": f})
        for v, p, f in _MUTATES
    ),
)


# ── 147. Sorting ─────────────────────────────────────────────
#
# Every list here holds a number of two digits and a larger single digit,
# because that is the pair that makes the default sort visibly wrong.

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
    "ts-array-order", 147, "Sorting, and the default that is wrong",
    "sort with no comparator turns everything into text first, so 10 comes "
    "before 9 and always has. It also sorts in place, which is why these "
    "start by spreading into a copy. The comparator returns a negative "
    "number, zero or a positive one, and subtraction is the usual way to "
    "produce all three at once.",
    "[...items].sort() puts 10 before 9; [...items].sort((x, y) => x - y) "
    "is what you meant",
    "ts_array_order",
    tuple(
        (f"Sort {{{_seq(v)}}} twice: once with the bare sort and once with "
         f"a numeric comparator. Print each result space separated, and "
         f"notice they differ.", {"values": list(v), "want": "numbers"})
        for v in _NUMBER_SORTS
    ) + tuple(
        (f"Sort {{{_wordlist(w)}}} by length, alphabetically where lengths "
         f"tie. Print it, then print it reversed.",
         {"words": list(w), "want": "words"})
        for w in _WORD_SORTS
    ),
)


# ── 148. Walking a Map ───────────────────────────────────────

_WALKS = (
    (("ann", 30), ("bob", 25), ("cy", 5)),
    (("red", 4), ("blue", 7), ("green", 2)),
    (("one", 1), ("two", 2), ("three", 3)),
    (("cat", 9), ("dog", 5), ("emu", 3)),
    (("north", 1), ("south", 2), ("east", 3)),
    (("iron", 26), ("tin", 50)),
    (("oak", 3), ("elm", 6), ("ash", 9)),
    (("salt", 2), ("pepper", 8), ("bay", 4)),
    (("rook", 5), ("pawn", 1), ("king", 0)),
    (("mars", 4), ("venus", 2), ("io", 1)),
    (("ann", 12), ("bea", 8)),
    (("red", 1), ("blue", 9)),
    (("cat", 2), ("dog", 4), ("fox", 6)),
    (("up", 3), ("down", 7)),
    (("gold", 79), ("lead", 82)),
    (("elm", 2), ("fir", 5), ("yew", 8)),
    (("bay", 1), ("dill", 3)),
    (("pawn", 2), ("rook", 6), ("bishop", 4)),
    (("io", 5), ("titan", 7)),
    (("ann", 21), ("cy", 9), ("bob", 15)),
)

WALK_PAGE = _page(
    "ts-iterate", 148, "Walking a Map",
    "for...of over a Map hands you a two-element array per entry, which "
    "destructures straight into a key and a value. keys, values and entries "
    "give the three views, and each one is an iterator rather than an array "
    "— which is why they get spread before anything array-shaped is done "
    "to them.",
    "for (const [name, age] of ages) — the brackets are destructuring the "
    "pair the Map hands over",
    "ts_iterate",
    tuple(
        (f"Build a Map holding {_pairs_text(ps)}. Walk it with for...of, "
         f"collecting the names and totalling the values. Print the names "
         f"sorted and space separated, then the total, then how many "
         f"values the Map has.", {"pairs": [list(p) for p in ps]})
        for ps in _WALKS
    ),
)


# ── 149. Strings ─────────────────────────────────────────────

_REPEATS = (
    ("ab", 3, "hi", 5), ("xy", 4, "go", 6), ("-", 5, "up", 4),
    ("ab", 2, "cat", 6), ("=", 6, "dog", 7), ("no", 3, "yes", 5),
    ("z", 7, "end", 6), ("qp", 2, "on", 5), ("*", 4, "run", 7),
    ("mn", 3, "it", 4),
)

_SPLITS = (
    ("a,b,c", ",", 3), ("one two three", " ", 3), ("x-y-z", "-", 3),
    ("red,blue", ",", 3), ("up down", " ", 2), ("1:2:3", ":", 3),
    ("cat,dog,emu", ",", 4), ("north south", " ", 5), ("p|q|r", "|", 3),
    ("salt,bay", ",", 4),
)

STRING_PAGE = _page(
    "ts-string", 149, "The string calls worth knowing",
    "repeat builds a run of something, padStart lines a column up and takes "
    "the character to pad with, split turns text into an array and join "
    "turns it back. slice takes a start and an end rather than a length, "
    "and a negative start counts from the far end.",
    'unit.repeat(3) and "hi".padStart(5, ".") gives "...hi" — padStart '
    "counts the total width, not the padding added",
    "ts_string",
    tuple(
        (f"Print {u!r} repeated {t} times, then print {w!r} padded on the "
         f"left with dots to a width of {n}.",
         {"unit": u, "times": t, "word": w, "width": n, "want": "repeat"})
        for u, t, w, n in _REPEATS
    ) + tuple(
        (f"Split {txt!r} on {sep!r}, print the parts joined with dashes, "
         f"then how many parts there were, then the first {c} characters "
         f"of the original.",
         {"text": txt, "sep": sep, "cut": c, "want": "split"})
        for txt, sep, c in _SPLITS
    ),
)


# ── 150. When nothing is a value ─────────────────────────────
#
# Every row stores zero on purpose. That is the one value where ?? and ||
# disagree, so it is the only data that shows what the page is about.

_NULLISH = (
    ("hits", 9), ("count", 1), ("total", 5), ("score", 7), ("size", 3),
    ("depth", 2), ("width", 8), ("age", 4), ("cost", 6), ("rank", 10),
    ("level", 11), ("mass", 12), ("speed", 13), ("heat", 14),
    ("index", 15), ("weight", 16), ("length", 17), ("volume", 18),
    ("height", 19), ("angle", 20),
)

NULLISH_PAGE = _page(
    "ts-nullish", 150, "When nothing is a value",
    "?? falls back only on null and undefined. || falls back on everything "
    "falsy, and zero is falsy, so a real count of zero gets thrown away and "
    "replaced by the default. That is the bug, and it hides for as long as "
    "the number happens never to be zero.",
    "found ?? 9 keeps a stored 0; found || 9 replaces it with 9, and both "
    "look correct until the count reaches zero",
    "ts_nullish",
    tuple(
        (f"Store 0 under {k!r} in a Map<string, number>. Print the lookup "
         f"with ?? {f}, then the same lookup with || {f}, then a lookup of "
         f"a key that is not there with ?? {f}. Two of those three agree.",
         {"key": k, "value": 0, "fallback": f, "absent": "nothing"})
        for k, f in _NULLISH
    ),
)


TS7_PAGES: tuple[Page, ...] = (
    MAP_PAGE,
    COUNT_PAGE,
    SET_PAGE,
    MATH_PAGE,
    MAKE_PAGE,
    MUTATE_PAGE,
    ORDER_PAGE,
    WALK_PAGE,
    STRING_PAGE,
    NULLISH_PAGE,
)
