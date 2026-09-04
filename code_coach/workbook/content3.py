"""Pages 33 onwards: pairs, grids, searching and ordering.

Where the earlier list pages walk one list and do one thing to each item,
these are the next step in every direction: two lists at once, a list of
lists, counting rather than showing, and stopping early because you found
what you came for.

All seven languages, because everything here stays inside what C can do
without pretending — fixed arrays and a count beside them. Splitting text and
looking things up by key come later, on pages that name the languages with
those types.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page
from code_coach.workbook.content2 import WORKBOOK_LANGUAGES


# Positional-only up to the shape, so a shape argument can share a name
# with one of these without colliding — page 44 passes n= for the times
# table, which is exactly the clash this prevents.
def _ex(
    page_id: str, n: int, prompt: str, shape: str, /, **args
) -> Exercise:
    return Exercise(
        id=f"{page_id}-{n:02d}", prompt=prompt, shape=shape, args=args
    )


def _page(page_id, number, name, teaches, example, exercises) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(exercises),
        languages=WORKBOOK_LANGUAGES,
    )


def _list(items) -> str:
    return ", ".join(str(n) for n in items)


# ── 33. Two pieces of text ───────────────────────────────────

_JOINS = (
    ("hello", "world"),
    ("good", "morning"),
    ("code", "coach"),
    ("black", "coffee"),
    ("open", "the door"),
    ("first", "second"),
    ("red", "car"),
    ("keep", "going"),
    ("one", "more"),
    ("almost", "there"),
    ("last", "line"),
    ("all", "done"),
    ("green", "light"),
    ("start", "again"),
    ("two", "words"),
    ("cold", "morning"),
    ("hold", "on"),
    ("the", "answer"),
    ("write", "it down"),
    ("very", "last"),
)

_P33 = _page(
    "join-words",
    33,
    "Two pieces of text",
    "Building one line out of two variables and a space.",
    "The space is the whole exercise. It is not in either word, so you have "
    "to put it there — and forgetting it gives you helloworld, which is the "
    "commonest small bug in anything that prints a sentence.",
    [
        _ex(
            "join-words",
            i + 1,
            f'Put "{one}" in one variable and "{two}" in another, then print '
            f"them on one line with a single space between them.",
            "join_words",
            word1=one,
            word2=two,
        )
        for i, (one, two) in enumerate(_JOINS)
    ],
)


# ── 34. Trading places ───────────────────────────────────────

_SWAPS = (
    (3, 8),
    (1, 2),
    (10, 20),
    (99, 1),
    (7, 7),
    (0, 5),
    (42, 24),
    (100, 200),
    (6, 3),
    (15, 51),
    (2, 9),
    (8, 0),
    (4, 11),
    (25, 75),
    (1, 1),
    (60, 6),
    (13, 31),
    (0, 0),
    (500, 5),
    (18, 81),
)

_P34 = _page(
    "swap",
    34,
    "Trading places",
    "Getting two variables to exchange what they hold.",
    "Assigning one to the other loses a value: by the time you write the "
    "second line the original is already gone. You need somewhere to put one "
    "of them first. One pair here holds the same number twice, which works "
    "either way and tells you nothing — the other eleven will.",
    [
        _ex(
            "swap",
            i + 1,
            f"Put {one} in a and {two} in b. Swap them over, then print a and "
            f"then b.",
            "swap_print",
            value1=one,
            value2=two,
        )
        for i, (one, two) in enumerate(_SWAPS)
    ],
)


# ── 35. How many, not which ──────────────────────────────────

_COUNTS = (
    ([3, 8, 12, 7], "n > 5", "are more than 5"),
    ([1, 2, 3, 4, 5, 6], "n % 2 == 0", "divide exactly by 2"),
    ([10, 15, 20, 25], "n % 10 == 0", "divide exactly by 10"),
    ([4, 9, 16, 25, 36], "n > 15", "are more than 15"),
    ([2, 5, 8, 11], "n % 2 == 1", "are odd"),
    ([100, 50, 200, 25], "n >= 100", "are 100 or more"),
    ([1, 3, 5, 7], "n > 100", "are more than 100"),
    ([12, 18, 24, 30], "n % 4 == 0", "divide exactly by 4"),
    ([6, 7, 8, 9, 10], "n < 8", "are less than 8"),
    ([33, 44, 55, 66], "n % 11 == 0", "divide exactly by 11"),
    ([5, 5, 5, 5], "n == 5", "are exactly 5"),
    ([2, 4, 6, 8, 10, 12], "n > 4", "are more than 4"),
    ([14, 21, 28, 35], "n % 7 == 0", "divide exactly by 7"),
    ([9, 19, 29, 39], "n > 25", "are more than 25"),
    ([2, 3, 5, 7, 11, 13], "n < 6", "are less than 6"),
    ([20, 40, 60, 80], "n % 3 == 0", "divide exactly by 3"),
    ([16, 32, 64], "n >= 32", "are 32 or more"),
    ([1, 1, 2, 1, 3], "n == 1", "are exactly 1"),
    ([45, 90, 135], "n % 9 == 0", "divide exactly by 9"),
    ([8, 16, 24, 32, 40], "n > 20", "are more than 20"),
)

_P35 = _page(
    "count-matches",
    35,
    "How many, not which",
    "Counting the ones that qualify instead of printing them.",
    "Nearly page 24, and different in the one way that matters: the counter "
    "lives outside the loop and only one line comes out at the end. One of "
    "these counts nothing at all and must still print a number — 0 is an "
    "answer, and a program that prints nothing there is a program that has "
    "not answered.",
    [
        _ex(
            "count-matches",
            i + 1,
            f"Put the numbers {_list(items)} in a list. Print how many of "
            f"them {described}.",
            "count_matches",
            items=items,
            cond=cond,
        )
        for i, (items, cond, described) in enumerate(_COUNTS)
    ],
)


# ── 36. Two lists in step ────────────────────────────────────

_PAIRS = (
    ([1, 2, 3], [10, 20, 30], "x + y", "the two added"),
    ([5, 6], [1, 2], "x * y", "the two multiplied"),
    ([10, 20, 30], [1, 2, 3], "x - y", "the first minus the second"),
    ([2, 4, 6, 8], [1, 1, 1, 1], "x + y", "the two added"),
    ([3, 3, 3], [1, 2, 3], "x * y", "the two multiplied"),
    ([100, 200], [50, 100], "x - y", "the first minus the second"),
    ([7, 8, 9], [2, 2, 2], "x % y", "the remainder of the first over the second"),
    ([1, 2], [100, 200], "x + y", "the two added"),
    ([9, 8, 7, 6], [1, 2, 3, 4], "x + y", "the two added"),
    ([4, 5, 6], [4, 5, 6], "x * y", "the two multiplied"),
    ([50, 40, 30], [5, 4, 3], "x - y", "the first minus the second"),
    ([11, 22, 33], [10, 20, 30], "x - y", "the first minus the second"),
    ([8, 16, 24], [2, 4, 6], "x + y", "the two added"),
    ([9, 9], [3, 9], "x * y", "the two multiplied"),
    ([60, 70, 80], [10, 10, 10], "x - y", "the first minus the second"),
    ([15, 25, 35], [4, 5, 6], "x % y", "the remainder of the first over the second"),
    ([1, 2, 3, 4, 5], [5, 4, 3, 2, 1], "x + y", "the two added"),
    ([12, 24], [12, 12], "x - y", "the first minus the second"),
    ([2, 3, 4], [10, 100, 1000], "x * y", "the two multiplied"),
    ([21, 33, 45], [7, 11, 15], "x % y", "the remainder of the first over the second"),
)

_P36 = _page(
    "two-lists",
    36,
    "Two lists in step",
    "Walking two lists together, position by position.",
    "You cannot use the loop that hands you the items here, because it only "
    "hands you one list's. You need the positions instead, and then to reach "
    "into both lists with the same one — which is the first time the index "
    "has been worth having since page 23.",
    [
        _ex(
            "two-lists",
            i + 1,
            f"Put {_list(xs)} in one list and {_list(ys)} in another. Going "
            f"through them together, print {described} for each position.",
            "two_lists",
            xs=xs,
            ys=ys,
            expr=expr,
        )
        for i, (xs, ys, expr, described) in enumerate(_PAIRS)
    ],
)


# ── 37. A list of lists ──────────────────────────────────────

_GRIDS = (
    ([[1, 2], [3, 4]], "v", "each number"),
    ([[1, 2, 3], [4, 5, 6]], "v", "each number"),
    ([[10, 20], [30, 40], [50, 60]], "v", "each number"),
    ([[1, 1], [2, 2]], "v * 10", "each number times 10"),
    ([[5, 6], [7, 8]], "v + 1", "each number plus 1"),
    ([[2, 4], [6, 8], [10, 12]], "v", "each number"),
    ([[3, 3, 3], [4, 4, 4]], "v * v", "each number times itself"),
    ([[9, 8], [7, 6]], "v - 5", "each number minus 5"),
    ([[1, 2], [3, 4], [5, 6], [7, 8]], "v", "each number"),
    ([[100, 200], [300, 400]], "v % 7", "the remainder of each divided by 7"),
    ([[0, 1], [1, 0]], "v + 5", "each number plus 5"),
    ([[12, 15, 18], [21, 24, 27]], "v % 6", "the remainder of each divided by 6"),
    ([[2, 3], [5, 7]], "v", "each number"),
    ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], "v", "each number"),
    ([[6, 6], [6, 6]], "v * 3", "each number times 3"),
    ([[20, 30], [40, 50]], "v - 10", "each number minus 10"),
    ([[1, 4], [9, 16], [25, 36]], "v + 2", "each number plus 2"),
    ([[8, 7, 6], [5, 4, 3]], "v * 2", "each number doubled"),
    ([[11, 22], [33, 44], [55, 66]], "v % 5", "the remainder of each divided by 5"),
    ([[10, 10, 10], [1, 2, 3]], "v", "each number"),
)

_P37 = _page(
    "grid",
    37,
    "A list of lists",
    "A loop inside a loop, over rows and then over what is in them.",
    "Page 11 nested two counting loops; this nests two list loops, and the "
    "inner one is over whatever the outer one just handed you. The shape is "
    "the same and the thing being visited is not — which is the whole reason "
    "a grid is easy once loops are.",
    [
        _ex(
            "grid",
            i + 1,
            f"Make a list holding {len(rows)} lists: "
            + "; ".join(_list(r) for r in rows)
            + f". Print {described} in it.",
            "grid_print",
            rows=rows,
            expr=expr,
        )
        for i, (rows, expr, described) in enumerate(_GRIDS)
    ],
)


# ── 38. The smallest one ─────────────────────────────────────

_MINS = (
    [3, 9, 4],
    [10, 2, 8, 5],
    [7],
    [1, 2, 3, 4, 5],
    [5, 4, 3, 2, 1],
    [100, 99, 101],
    [12, 12, 12],
    [45, 3, 45, 60],
    [88, 12, 90, 33, 2],
    [6, 6, 7],
    [250, 40, 60, 240],
    [1, 100, 10, 1000, 11],
    [8, 3, 11, 6],
    [40, 41, 39],
    [2, 2, 5],
    [77, 7, 707],
    [15, 30, 45, 5],
    [9, 8, 7, 6, 5, 4],
    [300, 30, 3],
    [21, 34, 13, 55],
)

_P38 = _page(
    "list-min",
    38,
    "The smallest one",
    "The same carry-the-best-so-far loop, pointed the other way.",
    "One character different from page 26 and worth writing out anyway, "
    "because the version you can write without thinking is the one you have "
    "written. Starting from the first item still matters for the same reason "
    "it did there.",
    [
        _ex(
            "list-min",
            i + 1,
            f"Put the numbers {_list(items)} in a list. Work out the smallest "
            f"one with a loop and print it.",
            "list_min",
            items=items,
        )
        for i, items in enumerate(_MINS)
    ],
)


# ── 39. Backwards through a list ─────────────────────────────

_REVERSED = (
    [1, 2, 3],
    [10, 20, 30, 40],
    [5],
    [7, 8],
    [1, 2, 3, 4, 5, 6],
    [100, 200, 300],
    [9, 9, 1],
    [2, 4, 8, 16, 32],
    [11, 22],
    [3, 1, 4, 1, 5],
    [60, 50, 40, 30],
    [1, 10, 100, 1000],
    [4, 5, 6, 7],
    [90, 80],
    [1, 1, 2, 3, 5],
    [12],
    [25, 50, 75, 100],
    [8, 6, 4, 2],
    [13, 26, 39, 52, 65],
    [7, 14, 21],
)

_P39 = _page(
    "list-reverse",
    39,
    "Backwards through a list",
    "Visiting a list from the last position to the first.",
    "The loop that hands you the items goes one way only, so this needs "
    "positions and a countdown. The last position is one less than the "
    "length, which is page 23's sentence again — and getting it wrong here "
    "either skips the last item or reaches past the end.",
    [
        _ex(
            "list-reverse",
            i + 1,
            f"Put the numbers {_list(items)} in a list. Print them from the "
            f"last one to the first.",
            "list_reverse",
            items=items,
        )
        for i, items in enumerate(_REVERSED)
    ],
)


# ── 40. Where is it ──────────────────────────────────────────

_FINDS = (
    ([10, 20, 30], 20),
    ([5, 6, 7, 8], 5),
    ([1, 2, 3, 4], 4),
    ([9, 8, 7, 6, 5], 7),
    ([100, 200, 300], 300),
    ([4, 4, 4], 4),
    ([12, 15, 18, 21], 18),
    ([2, 4, 6, 8, 10], 10),
    ([33, 11, 22], 11),
    ([7, 1, 7, 1], 1),
    ([50, 60, 70, 80, 90], 50),
    ([1, 3, 5, 7, 9, 11], 9),
    ([15, 25, 35], 35),
    ([2, 4, 6, 8], 2),
    ([9, 18, 27, 36], 27),
    ([60, 50, 40], 50),
    ([3, 6, 9, 12, 15], 15),
    ([8, 8, 9], 9),
    ([100, 10, 1000], 10),
    ([5, 15, 25, 35, 45], 25),
)

_P40 = _page(
    "find-index",
    40,
    "Where is it",
    "Searching, and stopping the moment you have found it.",
    "Print the position, not the number — you already know the number, it is "
    "in the question. Two of these hold the value twice and want the first "
    "one, which is what the stopping is for: a loop that carries on finds the "
    "second as well and prints it too.",
    [
        _ex(
            "find-index",
            i + 1,
            f"Put the numbers {_list(items)} in a list. Print the position of "
            f"the first {target} in it, counting from 0.",
            "find_index",
            items=items,
            target=target,
        )
        for i, (items, target) in enumerate(_FINDS)
    ],
)


MORE_PAGES_3: tuple[Page, ...] = (
    _P33,
    _P34,
    _P35,
    _P36,
    _P37,
    _P38,
    _P39,
    _P40,
)
