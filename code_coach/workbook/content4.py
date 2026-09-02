"""Pages 41 onwards: labelling, stepping, tables and two-argument work.

The loop itself stops getting harder here; what it does each time round gets
a job of its own. A decision that produces a word, a total that shows its
working, a line with three values in it, a function that takes two things.

All seven languages, same as pages 33 to 40.
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


# ── 41. A word for each one ──────────────────────────────────

_LABELS = (
    ([1, 2, 3, 4], "n % 2 == 0", "divides by 2", "even", "odd"),
    ([7, 3, 9, 12], "n > 5", "is more than 5", "big", "small"),
    ([10, 5, 20, 1], "n >= 10", "is 10 or more", "high", "low"),
    ([0, 1, 0, 1], "n == 0", "is 0", "off", "on"),
    ([15, 8, 30, 4], "n % 5 == 0", "divides by 5", "fives", "not fives"),
    ([2, 4, 6], "n > 100", "is more than 100", "huge", "ordinary"),
    ([50, 60, 40, 70], "n >= 50", "is 50 or more", "pass", "fail"),
    ([3, 6, 9, 12, 15], "n % 3 == 0", "divides by 3", "threes", "no"),
    ([1, 100, 2, 200], "n < 10", "is under 10", "small", "large"),
    ([8, 8, 9], "n == 8", "is exactly 8", "eight", "other"),
    ([21, 22, 23, 24], "n % 2 == 1", "is odd", "odd", "even"),
    ([5, 10, 15, 20, 25], "n > 12", "is more than 12", "over", "under"),
)

_P41 = _page(
    "label-each",
    41,
    "A word for each one",
    "A decision inside the loop that always produces something.",
    "Page 24 printed the ones that qualified and skipped the rest. This "
    "prints a word for every item, so the number of lines out matches the "
    "number of items in — and the else branch is what makes that true.",
    [
        _ex(
            "label-each",
            i + 1,
            f'Put the numbers {_list(items)} in a list. For each one print '
            f'"{yes}" if it {described}, and "{no}" if it does not.',
            "label_each",
            items=items,
            cond=cond,
            yes=yes,
            no=no,
        )
        for i, (items, cond, described, yes, no) in enumerate(_LABELS)
    ],
)


# ── 42. The total as it grows ────────────────────────────────

_RUNNING = (
    [1, 2, 3],
    [10, 20, 30],
    [5, 5, 5, 5],
    [1, 1, 1, 1, 1],
    [100, 50, 25],
    [2, 4, 8, 16],
    [7],
    [3, 0, 3, 0],
    [11, 22, 33],
    [1, 2, 3, 4, 5, 6],
    [40, 30, 20, 10],
    [9, 1, 9, 1, 9],
)

_P42 = _page(
    "running-total",
    42,
    "The total as it grows",
    "Printing inside the loop instead of after it.",
    "Page 22 added a list up and printed one number. Move that print inside "
    "the loop and you get the total after every step instead — same three "
    "lines, one of them indented differently. Where a line sits is as much "
    "of the program as what it says.",
    [
        _ex(
            "running-total",
            i + 1,
            f"Put the numbers {_list(items)} in a list. Add them up one at a "
            f"time, printing the total after each one.",
            "running_total",
            items=items,
        )
        for i, items in enumerate(_RUNNING)
    ],
)


# ── 43. Counting in twos ─────────────────────────────────────

_STEPS = (
    (1, 10, 2, "i", "the number"),
    (0, 20, 5, "i", "the number"),
    (2, 12, 2, "i", "the number"),
    (1, 15, 3, "i", "the number"),
    (10, 50, 10, "i", "the number"),
    (1, 9, 4, "i * 2", "the number doubled"),
    (3, 30, 3, "i", "the number"),
    (0, 12, 4, "i + 1", "the number plus 1"),
    (5, 25, 5, "i * 2", "the number doubled"),
    (1, 20, 6, "i", "the number"),
    (2, 20, 9, "i * 10", "the number times 10"),
    (1, 7, 2, "i * i", "the number times itself"),
)

_P43 = _page(
    "step-loop",
    43,
    "Counting in twos",
    "A loop that moves by something other than one.",
    "The step decides which numbers you land on, and the end is a limit "
    "rather than a promise: counting from 1 to 10 in twos stops at 9, "
    "because 11 is past the end. Expecting to land on the last number is the "
    "mistake this page is for.",
    [
        _ex(
            "step-loop",
            i + 1,
            f"Count from {lo} to {hi} in steps of {step}, printing "
            f"{described} each time.",
            "step_loop",
            lo=lo,
            hi=hi,
            step=step,
            expr=expr,
        )
        for i, (lo, hi, step, expr, described) in enumerate(_STEPS)
    ],
)


# ── 44. Times tables ─────────────────────────────────────────

_TABLES = (
    (3, 5),
    (2, 10),
    (7, 4),
    (5, 6),
    (9, 3),
    (4, 8),
    (6, 6),
    (12, 5),
    (11, 4),
    (8, 7),
    (10, 10),
    (1, 12),
)

_P44 = _page(
    "times-table",
    44,
    "Times tables",
    "A line of text with three values worked into it.",
    "Two of the three change every time round and one does not, which is the "
    "only thing making this harder than page 12. Get the spaces right — the "
    "line is a sentence and a missing space around the x is the sort of "
    "thing you stop seeing after the third read.",
    [
        _ex(
            "times-table",
            i + 1,
            f'Print the {n} times table from 1 to {upto}, one line each, '
            f'reading like "{n} x 1 = {n}".',
            "times_table",
            n=n,
            upto=upto,
        )
        for i, (n, upto) in enumerate(_TABLES)
    ],
)


# ── 45. Adding up a grid ─────────────────────────────────────

_GRID_SUMS = (
    [[1, 2], [3, 4]],
    [[1, 1, 1], [1, 1, 1]],
    [[10, 20], [30, 40]],
    [[5]],
    [[2, 4], [6, 8], [10, 12]],
    [[100, 200], [300, 400]],
    [[7, 7, 7]],
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    [[0, 0], [0, 5]],
    [[9, 1], [8, 2], [7, 3]],
    [[25, 25], [25, 25]],
    [[11, 12, 13], [14, 15, 16]],
)

_P45 = _page(
    "grid-sum",
    45,
    "Adding up a grid",
    "One total, two loops.",
    "The total goes outside both loops. Put it between them and you get one "
    "total per row instead, which is a perfectly good program and not this "
    "one — and the two look almost identical on the page.",
    [
        _ex(
            "grid-sum",
            i + 1,
            f"Make a list holding {len(rows)} lists: "
            + "; ".join(_list(r) for r in rows)
            + ". Add up every number in it and print the total.",
            "grid_sum",
            rows=rows,
        )
        for i, rows in enumerate(_GRID_SUMS)
    ],
)


# ── 46. Two things in, one out ───────────────────────────────

_TWO_ARG = (
    ("add", "a", "b", "a + b", "the two added", [(3, 4), (10, 20)]),
    ("times", "a", "b", "a * b", "the two multiplied", [(6, 7), (2, 50)]),
    ("gap", "a", "b", "a - b", "the first minus the second", [(10, 3), (100, 1)]),
    ("both", "a", "b", "a + b + a", "the two added, plus the first again", [(1, 2), (5, 5)]),
    ("scale", "a", "b", "a * b + 1", "the two multiplied, plus 1", [(3, 3), (4, 5)]),
    ("rest", "a", "b", "a % b", "the remainder of the first over the second", [(17, 5), (100, 7)]),
    ("bigger", "a", "b", "a * 2 + b", "twice the first plus the second", [(3, 1), (10, 10)]),
    ("less", "a", "b", "a - b - b", "the first minus the second twice", [(20, 5), (9, 2)]),
    ("sum3", "a", "b", "a + b + 3", "the two added, plus 3", [(1, 1), (40, 2)]),
    ("area", "a", "b", "a * b", "the two multiplied", [(4, 9), (12, 12)]),
    ("half", "a", "b", "(a + b) % 10", "the last digit of the two added", [(7, 9), (25, 30)]),
    ("mix", "a", "b", "a * 10 + b", "the first times 10, plus the second", [(3, 4), (9, 9)]),
)

_P46 = _page(
    "func-two",
    46,
    "Two things in, one out",
    "A function that takes two values rather than one.",
    "Nothing new in the idea — a second name in the brackets — and it is "
    "worth its own page because the order of the two is now something you "
    "can get wrong. Two of these subtract, so passing them the other way "
    "round gives an answer that looks fine and is not.",
    [
        _ex(
            "func-two",
            i + 1,
            f"Write a function called {name} that takes two numbers and "
            f"returns {described}. Print the result of calling it with "
            + " and then ".join(f"{x} and {y}" for x, y in calls)
            + ".",
            "func_two",
            name=name,
            param1=p1,
            param2=p2,
            expr=expr,
            calls=calls,
        )
        for i, (name, p1, p2, expr, described, calls) in enumerate(_TWO_ARG)
    ],
)


# ── 47. A function that answers in words ─────────────────────

_WORDS = (
    ("size", "n", "n > 10", "is more than 10", "big", "small", [5, 50]),
    ("parity", "n", "n % 2 == 0", "divides by 2", "even", "odd", [4, 7]),
    ("sign", "n", "n < 0", "is below 0", "negative", "positive", [-3, 8]),
    ("grade", "n", "n >= 50", "is 50 or more", "pass", "fail", [49, 50, 90]),
    ("stock", "n", "n > 0", "is more than 0", "in stock", "sold out", [0, 3]),
    ("age", "n", "n >= 18", "is 18 or more", "adult", "child", [17, 18]),
    ("temp", "n", "n > 30", "is above 30", "hot", "fine", [31, 12]),
    ("full", "n", "n == 0", "is exactly 0", "empty", "has some", [0, 9]),
    ("speed", "n", "n > 60", "is over 60", "too fast", "legal", [70, 60]),
    ("fives", "n", "n % 5 == 0", "divides by 5", "yes", "no", [10, 11, 25]),
    ("tiny", "n", "n < 3", "is under 3", "tiny", "not tiny", [1, 3]),
    ("round", "n", "n % 100 == 0", "divides by 100", "round", "awkward", [200, 250]),
)

_P47 = _page(
    "func-word",
    47,
    "A function that answers in words",
    "Returning one of two words instead of a number.",
    "Two returns, and the first one that runs ends the function — so the "
    "second is only reached when the condition did not hold. That is why no "
    "else is needed here, and noticing it is the point: a return is a way "
    "out, not just a way to hand something back.",
    [
        _ex(
            "func-word",
            i + 1,
            f'Write a function called {name} that takes a number and returns '
            f'"{yes}" if it {described} and "{no}" if it does not. Print the '
            f"result of calling it with " + ", then ".join(str(v) for v in calls) + ".",
            "func_word",
            name=name,
            param=param,
            cond=cond,
            yes=yes,
            no=no,
            calls=calls,
        )
        for i, (name, param, cond, described, yes, no, calls) in enumerate(_WORDS)
    ],
)


# ── 48. One character out of a word ──────────────────────────

_CHARS = (
    ("hello", 0),
    ("hello", 4),
    ("workbook", 3),
    ("typing", 1),
    ("code", 2),
    ("keyboard", 0),
    ("practice", 7),
    ("letters", 5),
    ("repeat", 2),
    ("finished", 4),
    ("almost", 1),
    ("done", 3),
)

_P48 = _page(
    "char-at",
    48,
    "One character out of a word",
    "Reaching into a string by position, the way you reach into a list.",
    "A string is a list of characters when you index it, which is page 23's "
    "idea pointed at something new. Positions start at 0 here too, so the "
    "last character of a five-letter word is at 4 — and asking for 5 is the "
    "same mistake in different clothes.",
    [
        _ex(
            "char-at",
            i + 1,
            f'Print the character at position {index} of the word "{word}", '
            f"counting from 0.",
            "char_at",
            word=word,
            index=index,
        )
        for i, (word, index) in enumerate(_CHARS)
    ],
)


MORE_PAGES_4: tuple[Page, ...] = (
    _P41,
    _P42,
    _P43,
    _P44,
    _P45,
    _P46,
    _P47,
    _P48,
)
