"""Intermediate pages 209-218: the rest of itertools, and the dataclass
you did not know you had.

Five itertools pages, each replacing a loop that is easy to write badly:
every combination of two lists, two lists of unequal length walked
together, an endless sequence cut short, the run at the front, and
consecutive pairs.

Then the parts of dataclasses beyond __init__ - asdict, astuple,
replace, order and __post_init__ - an Enum that numbers itself, a
generic function whose hint finally says something true, and a thread
pool whose map hands results back in the order you asked for.

Python only, same as 81-208.
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


# ── 209. Every combination of two lists ──────────────────────

_PRODUCTS = (
    ((1, 2), ("a", "b")),
    ((1, 2, 3), ("x", "y")),
    ((0,), ("red", "green", "blue")),
    ((5, 6), ("on", "off")),
    ((1, 2), ("mon", "tue", "wed")),
    ((7,), ("up", "down")),
    ((10, 20), ("small", "large")),
    ((1, 2, 3), ("yes",)),
    ((4, 8), ("iron", "gold")),
    ((2,), ("do", "re", "mi")),
    ((9, 10), ("left", "right")),
    ((3, 6), ("hot", "cold")),
)

_P209 = _page(
    "product-use",
    209,
    "Every combination of two lists",
    "itertools.product, which is a nested loop as one call.",
    "This is exactly the nested loop from page 11, handed back as pairs. "
    "The rightmost list moves fastest, same as the inner loop would - "
    "read the output and you can see it counting. Reach for it when you "
    "want every combination of some options: sizes against colours, "
    "settings against inputs, a small test matrix. Past two lists it "
    "still works and the output gets large very quickly.",
    "product_use",
    [
        (
            "Import product from itertools. Set first to ["
            + _seq(one)
            + "] and second to ["
            + _seq(two)
            + "], then print list of product of the two.",
            {"first": one, "second": two},
        )
        for one, two in _PRODUCTS
    ],
)


# ── 210. Two lists of different lengths, together ────────────

_LONGEST = (
    ((1, 2, 3), (10, 20), 0),
    ((1, 2), (10, 20, 30), 0),
    ((5, 6, 7, 8), (50, 60), 0),
    ((1,), (10, 20), -1),
    ((9, 8), (90,), -1),
    ((1, 2, 3), (10,), 0),
    ((4, 5), (40, 50, 60), 99),
    ((7,), (70, 80, 90), 99),
    ((2, 4, 6), (20, 40), 0),
    ((3, 6), (30,), 0),
    ((1, 2, 3, 4), (10, 20, 30), -1),
    ((8, 9), (80, 90, 100), 0),
)

_P210 = _page(
    "zip-longest-use",
    210,
    "Two lists of different lengths, together",
    "itertools.zip_longest, and the fillvalue.",
    "Page 187 made zip complain when the lengths differed. This is the "
    "other answer: keep going to the end of the longest, and put "
    "something in the gaps. Which of the three you want - stop short, "
    "complain, or fill - is a real decision about your data, and the "
    "only wrong move is not making it. Note the default fillvalue is "
    "None, which is rarely what you want and always worth saying "
    "explicitly.",
    "zip_longest_use",
    [
        (
            "Import zip_longest from itertools. Set first to ["
            + _seq(one)
            + "] and second to ["
            + _seq(two)
            + "]. Loop over zip_longest of the two with fillvalue="
            + repr(fill)
            + ", unpacking into a and b and printing both.",
            {"first": one, "second": two, "fill": fill},
        )
        for one, two, fill in _LONGEST
    ],
)


# ── 211. An endless sequence, cut short ──────────────────────

_CYCLES = (
    (("red", "green", "blue"), 7),
    (("on", "off"), 5),
    (("mon", "tue", "wed"), 8),
    (("do", "re", "mi"), 4),
    (("up", "down"), 6),
    (("iron", "gold"), 5),
    (("a", "b", "c", "d"), 6),
    (("left", "right"), 7),
    (("hot", "cold"), 3),
    (("north", "south", "east", "west"), 9),
    (("yes", "no"), 4),
    (("one", "two", "three"), 5),
)

_P211 = _page(
    "islice-cycle",
    211,
    "An endless sequence, cut short",
    "cycle, which never ends, and islice, which decides where to stop.",
    "cycle repeats its input forever - loop over it directly and the "
    "program never finishes, which is the sort of mistake you make "
    "exactly once. islice takes the first however-many and stops, so the "
    "pair is safe and useful: rotating through colours for a chart, "
    "dealing turns to players, striping table rows. islice also works on "
    "any iterator, which is how you take the first ten lines of "
    "something huge without reading the rest.",
    "islice_cycle",
    [
        (
            "Import cycle and islice from itertools. Set colours to ["
            + _seq(items)
            + "], then loop over islice of cycle of it taking "
            + str(take)
            + ", printing each.",
            {"items": items, "take": take},
        )
        for items, take in _CYCLES
    ],
)


# ── 212. The run at the front, and the rest ──────────────────

_TAKES = (
    ((1, 2, 3, 10, 1, 2), "n < 5"),
    ((2, 4, 6, 7, 8), "n % 2 == 0"),
    ((1, 1, 1, 9, 1), "n == 1"),
    ((10, 20, 5, 30), "n >= 10"),
    ((3, 6, 9, 4, 12), "n % 3 == 0"),
    ((1, 2, 3, 4, 100), "n < 50"),
    ((5, 5, 5, 1, 5), "n == 5"),
    ((100, 90, 80, 5, 70), "n > 50"),
    ((2, 4, 8, 9, 16), "n % 2 == 0"),
    ((1, 3, 5, 2, 7), "n % 2 == 1"),
    ((7, 14, 21, 5, 28), "n % 7 == 0"),
    ((0, 0, 1, 0), "n == 0"),
)

_P212 = _page(
    "takewhile-drop",
    212,
    "The run at the front, and the rest",
    "takewhile and dropwhile, and how they differ from filter.",
    "filter looks at every item. These two look only at the front: "
    "takewhile hands back items until one fails and then stops for good, "
    "dropwhile skips items until one passes and then hands back "
    "everything left. Every list here has a later item that would have "
    "passed the test - find it in the output and notice takewhile never "
    "reached it. That difference is the whole page, and it is why these "
    "are for sorted or structured data, like a header you want to skip.",
    "takewhile_drop",
    [
        (
            "Import dropwhile and takewhile from itertools. Set numbers "
            "to ["
            + _seq(items)
            + "], then print the list of takewhile over it with a lambda "
            "testing "
            + test
            + ", and then the list of dropwhile with the same test.",
            {"items": items, "test": test},
        )
        for items, test in _TAKES
    ],
)


# ── 213. Each item with the one after it ─────────────────────

_PAIRS = (
    (1, 4, 9, 16),
    (0, 5, 15, 30),
    (2, 4, 8, 16, 32),
    (10, 12, 15, 19),
    (100, 90, 70, 40),
    (1, 2, 4, 7, 11),
    (3, 6, 12, 24),
    (5, 5, 10, 20),
    (0, 1, 1, 2, 3, 5),
    (50, 45, 35, 20),
    (7, 14, 28, 56),
    (1, 10, 100, 1000),
)

_P213 = _page(
    "pairwise-use",
    213,
    "Each item with the one after it",
    "itertools.pairwise, for differences and comparisons along a list.",
    "Whenever the question is about neighbours - the gaps between "
    "readings, whether a list is sorted, where something changed - the "
    "hand-written version is a loop over indexes with a careful "
    "off-by-one at the end. pairwise gives you (first, second), (second, "
    "third), and so on, and there is no index to get wrong. A list of n "
    "items gives n minus 1 pairs, which is exactly why the loop was "
    "fiddly.",
    "pairwise_use",
    [
        (
            "Import pairwise from itertools. Set numbers to ["
            + _seq(items)
            + "], then loop over pairwise of it unpacking into first and "
            "second, printing second minus first.",
            {"items": items},
        )
        for items in _PAIRS
    ],
)


# ── 214. asdict, astuple and replace ─────────────────────────

_TOOLS_DATA = (
    ("Point", (("x", "int"), ("y", "int")), (2, 3), 10),
    ("Size", (("width", "int"), ("height", "int")), (10, 4), 25),
    ("Span", (("low", "int"), ("high", "int")), (3, 17), 0),
    ("Pair", (("left", "int"), ("right", "int")), (7, 8), 70),
    ("Room", (("floor", "int"), ("number", "int")), (3, 12), 5),
    ("Score", (("points", "int"), ("bonus", "int")), (40, 7), 99),
    ("Grid", (("rows", "int"), ("cols", "int")), (8, 9), 1),
    ("Trip", (("miles", "int"), ("hours", "int")), (120, 3), 200),
    ("Gap", (("start", "int"), ("end", "int")), (7, 31), 0),
    ("Tank", (("full", "int"), ("used", "int")), (60, 22), 100),
    ("Wall", (("bricks", "int"), ("rows", "int")), (90, 6), 45),
    ("Bill", (("price", "int"), ("people", "int")), (45, 3), 90),
)

_P214 = _page(
    "dataclass-tools",
    214,
    "asdict, astuple and replace",
    "The three functions that come with dataclasses.",
    "asdict turns the object into a plain dict, which is what you want "
    "on the way to JSON. astuple does the same into a tuple. replace "
    "makes a new object with one field different and everything else "
    "kept - which is how you change a frozen record, and a good habit "
    "even on one that is not, because it leaves the original alone. "
    "Between them these are most of what people write by hand before "
    "finding out they exist.",
    "dataclass_tools",
    [
        (
            "Import asdict, astuple, dataclass and replace from "
            "dataclasses. Write a dataclass "
            + cls
            + " with "
            + " and ".join(f"{n} hinted {t}" for n, t in fields)
            + ". Make thing holding "
            + _seq(values)
            + ", and moved as replace of thing with "
            + fields[0][0]
            + "="
            + repr(changed)
            + ". Print asdict of thing, astuple of thing, then moved.",
            {
                "cls": cls,
                "fields": fields,
                "values": values,
                "changed": changed,
            },
        )
        for cls, fields, values, changed in _TOOLS_DATA
    ],
)


# ── 215. Ordering, and work after __init__ ───────────────────

_ORDERED = (
    ("Card", "rank", "name", (3, "three"), (9, "nine")),
    ("Player", "score", "name", (41, "kim"), (90, "ada")),
    ("Book", "pages", "title", (204, "solaris"), (412, "dune")),
    ("City", "people", "name", (709, "oslo"), (1463, "kyoto")),
    ("Song", "seconds", "title", (173, "kooks"), (245, "alive")),
    ("Metal", "number", "name", (26, "iron"), (79, "gold")),
    ("Room", "floor", "name", (1, "hall"), (4, "attic")),
    ("Tool", "weight", "name", (3, "saw"), (8, "axe")),
    ("Task", "order", "label", (1, "weigh"), (3, "bake")),
    ("Team", "points", "name", (12, "blues"), (41, "reds")),
    ("Word", "length", "text", (3, "sky"), (8, "mountain")),
    ("Trip", "miles", "name", (40, "short one"), (120, "long one")),
)

_P215 = _page(
    "dataclass-order",
    215,
    "Ordering, and work after __init__",
    "order=True, and __post_init__ for tidying up.",
    "order=True writes the comparisons for you, and it compares fields "
    "in the order they are declared - so the field you want to sort by "
    "goes first, and that ordering is a design decision rather than an "
    "accident. __post_init__ runs straight after the generated __init__, "
    "which is where anything you cannot express as a default belongs: "
    "cleaning a value, working one out from the others, checking they "
    "make sense together.",
    "dataclass_order",
    [
        (
            "Import dataclass from dataclasses. Write a dataclass "
            + cls
            + " with order=True, "
            + first_field
            + " hinted int then "
            + second_field
            + " hinted str, and a __post_init__ that title-cases self."
            + second_field
            + ". Make first as "
            + cls
            + "("
            + repr(low[0])
            + ", "
            + repr(low[1])
            + ") and second as "
            + cls
            + "("
            + repr(high[0])
            + ", "
            + repr(high[1])
            + "). Print first < second, then first."
            + second_field
            + ", then the "
            + second_field
            + " of the first item of sorted([second, first]).",
            {
                "cls": cls,
                "first_field": first_field,
                "second_field": second_field,
                "low": low,
                "high": high,
            },
        )
        for cls, first_field, second_field, low, high in _ORDERED
    ],
)


# ── 216. An enum that numbers itself ─────────────────────────

_AUTOS = (
    ("Colour", ("RED", "GREEN", "BLUE"), "label"),
    ("State", ("READY", "RUNNING", "DONE"), "label"),
    ("Size", ("SMALL", "MEDIUM", "LARGE"), "shown"),
    ("Day", ("MON", "TUE", "WED"), "shown"),
    ("Rank", ("GOLD", "SILVER", "BRONZE"), "label"),
    ("Phase", ("START", "MIDDLE", "END"), "label"),
    ("Mode", ("READ", "WRITE", "APPEND"), "shown"),
    ("Speed", ("SLOW", "STEADY", "FAST"), "label"),
    ("Level", ("LOW", "MID", "HIGH"), "shown"),
    ("Suit", ("SPADES", "HEARTS", "CLUBS"), "label"),
    ("Turn", ("LEFT", "AHEAD", "RIGHT"), "shown"),
    ("Step", ("WEIGH", "MIX", "BAKE"), "label"),
)

_P216 = _page(
    "enum-auto",
    216,
    "An enum that numbers itself",
    "auto(), and a method on an Enum.",
    "Page 128 gave every member a number by hand, which is fine until "
    "you insert one in the middle and renumber the rest. auto() counts "
    "from 1 in the order written, so there are no numbers to get wrong - "
    "use it whenever the value itself does not matter, and write the "
    "numbers only when something outside your program depends on them. "
    "The other half of this page: an Enum is a class, so it can have "
    "methods, and self inside one is the member.",
    "enum_auto",
    [
        (
            "Import Enum and auto from enum. Write an Enum "
            + cls
            + " with members "
            + ", ".join(members)
            + " each set to auto(), and a method "
            + method
            + "(self) returning self.name title-cased. Print the value of "
            + members[0]
            + ", then the value of "
            + members[-1]
            + ", then "
            + method
            + "() called on "
            + members[1]
            + ".",
            {"cls": cls, "members": members, "method": method},
        )
        for cls, members, method in _AUTOS
    ],
)


# ── 217. A hint that says same type in, same out ─────────────

_GENERICS = (
    ("first_of", (1, 2, 3), ("a", "b")),
    ("head", (10, 20), ("red", "green")),
    ("front", (7,), ("mon", "tue")),
    ("start_of", (5, 6, 7), ("do", "re")),
    ("earliest", (100, 200), ("iron", "gold")),
    ("top_of", (9, 8), ("up", "down")),
    ("lead", (1, 1, 2), ("yes", "no")),
    ("opener", (42,), ("north", "south")),
    ("initial", (3, 6, 9), ("left", "right")),
    ("first_item", (11, 22), ("hot", "cold")),
    ("began", (0, 1), ("sky", "sea")),
    ("peek", (12, 24, 36), ("one", "two")),
)

_P217 = _page(
    "typevar-generic",
    217,
    "A hint that says same type in, same out",
    "TypeVar, so the hint can connect the argument to the answer.",
    "list[int] -> int says this takes whole numbers and gives one back. "
    "But a function returning the first item works on any list, and "
    "hinting it as list[Any] -> Any throws away the useful part. A "
    "TypeVar names a type without saying which: list[T] -> T means "
    "whatever this list holds is what comes back, so a checker knows a "
    "list of strings gives you a string. Both calls here are the same "
    "function, and the hint is true of both.",
    "typevar_generic",
    [
        (
            "Import TypeVar from typing and set T to TypeVar of "
            + repr("T")
            + ". Write "
            + name
            + "(items: list[T]) -> T returning the first item. Print it "
            "called with ["
            + _seq(numbers)
            + "], then with ["
            + _seq(words)
            + "].",
            {"name": name, "numbers": numbers, "words": words},
        )
        for name, numbers, words in _GENERICS
    ],
)


# ── 218. Several at once, in order ───────────────────────────

_POOLS = (
    ("n * n", (1, 2, 3, 4), 3),
    ("n * 2", (5, 6, 7), 2),
    ("n + 100", (1, 2, 3), 3),
    ("n // 2", (10, 20, 30, 40), 4),
    ("n * 10", (1, 3, 5), 2),
    ("n - 1", (9, 8, 7), 3),
    ("n * n * n", (1, 2, 3), 2),
    ("n % 5", (11, 12, 13, 14), 4),
    ("n + n", (2, 4, 6), 3),
    ("n * 3", (7, 8), 2),
    ("n // 10", (100, 250, 375), 3),
    ("n + 1", (0, 41, 99), 2),
)

_P218 = _page(
    "threadpool-map",
    218,
    "Several at once, in order",
    "ThreadPoolExecutor, and the order map promises.",
    "A pool runs the work on several threads at once and map hands the "
    "results back in the order of the input, never the order they "
    "finished - so you can line them up with what you asked for. The "
    "with block waits for everything before letting go. Threads in "
    "Python help when the work is waiting on files or the network, and "
    "not when it is pure calculation, where the global interpreter lock "
    "means you want processes instead. Same interface either way.",
    "threadpool_map",
    [
        (
            "Import ThreadPoolExecutor from concurrent.futures. Write "
            "work(n) returning "
            + expr
            + ". In a with over ThreadPoolExecutor(max_workers="
            + str(workers)
            + ") as pool, set results to the list of pool.map of work "
            "over ["
            + _seq(items)
            + "], then print results.",
            {"expr": expr, "items": items, "workers": workers},
        )
        for expr, items, workers in _POOLS
    ],
)


TOOLKIT_PAGES: tuple[Page, ...] = (
    _P209,
    _P210,
    _P211,
    _P212,
    _P213,
    _P214,
    _P215,
    _P216,
    _P217,
    _P218,
)
