"""Practice pages: earlier ideas again, with different numbers.

Pages 1 to 56 each introduce something. These do not. Every one takes a shape
you have already met and gives you twelve more of it with fresh values,
because meeting an idea once is not the same as being able to write it
without thinking, and the second kind is the only kind worth having.

They sit after the teaching pages rather than beside them for one dull
reason: the examples on the teaching pages refer to each other by number
("page 22 added a list up", "page 23's sentence again"), and interleaving
would make every one of those references wrong. Each page here says which one
it drills instead.

No new shapes, so nothing here needs a new emitter — which is what makes this
the cheap half of the workbook to grow. The expensive half is having ideas.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page
from code_coach.workbook.content2 import WORKBOOK_LANGUAGES

NOT_C = ("python", "javascript", "typescript", "dart", "cpp", "rust")


def _page(
    page_id: str,
    number: int,
    name: str,
    drills: str,
    example: str,
    shape: str,
    rows,
    languages=WORKBOOK_LANGUAGES,
) -> Page:
    """One practice page. `rows` is (prompt, args) per exercise."""
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=drills,
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
        languages=languages,
        tier="practice",
    )


def _list(items) -> str:
    return ", ".join(str(n) for n in items)


_AGAIN = (
    "Nothing new here. The same shape as before with different values, "
    "which is the half that turns knowing it into being able to write it."
)


# ── 57. Printing again ───────────────────────────────────────

_P57 = _page(
    "printing-more",
    57,
    "Printing again",
    "More practice on page 1.",
    _AGAIN + " Twelve lines, and by the end your fingers should be finding "
    "the quotes without you looking.",
    "print_text",
    [
        (f'Print the line "{t}".', {"text": t})
        for t in (
            "ready when you are",
            "second time round",
            "still here",
            "no thinking required",
            "again from the top",
            "one line at a time",
            "quiet please",
            "keep it going",
            "nearly warmed up",
            "steady hands",
            "one to go",
            "and out",
        )
    ],
)


# ── 58. Sums again ───────────────────────────────────────────

_P58 = _page(
    "arithmetic-more",
    58,
    "Sums again",
    "More practice on page 2, with more terms.",
    _AGAIN + " Several of these have three numbers in them, so the order the "
    "machine works in starts to matter — it does the multiplying before the "
    "adding, whatever order you read it in.",
    "print_expr",
    [
        (f"Print the answer to {label}.", {"expr": expr})
        for label, expr in (
            ("14 + 27", "14 + 27"),
            ("83 - 45", "83 - 45"),
            ("6 + 9 + 12", "6 + 9 + 12"),
            ("100 - 33 - 21", "100 - 33 - 21"),
            ("2 + 3 * 4", "2 + 3 * 4"),
            ("5 * 6 - 10", "5 * 6 - 10"),
            ("250 + 250", "250 + 250"),
            ("77 - 7 - 7", "77 - 7 - 7"),
            ("9 + 9 * 9", "9 + 9 * 9"),
            ("1000 - 1", "1000 - 1"),
            ("11 * 3 + 4", "11 * 3 + 4"),
            ("60 - 15 * 2", "60 - 15 * 2"),
        )
    ],
)


# ── 59. Remainders again ─────────────────────────────────────

_P59 = _page(
    "multiply-more",
    59,
    "Remainders again",
    "More practice on page 3.",
    _AGAIN + " The remainder is the bit that will not fit — 23 divided by 4 "
    "is 5 with 3 left over, and it is that 3 you are printing.",
    "print_expr",
    [
        (f"Print {label}.", {"expr": expr})
        for label, expr in (
            ("what is left over when 23 is divided by 4", "23 % 4"),
            ("what is left over when 58 is divided by 9", "58 % 9"),
            ("the answer to 13 times 8", "13 * 8"),
            ("what is left over when 200 is divided by 30", "200 % 30"),
            ("the answer to 15 times 15", "15 * 15"),
            ("what is left over when 77 is divided by 11", "77 % 11"),
            ("what is left over when 5 is divided by 8", "5 % 8"),
            ("the answer to 21 times 5", "21 * 5"),
            ("what is left over when 365 is divided by 7", "365 % 7"),
            ("the answer to 7 times 7 times 7", "7 * 7 * 7"),
            ("what is left over when 99 is divided by 25", "99 % 25"),
            ("the answer to 40 times 6 minus 40", "40 * 6 - 40"),
        )
    ],
)


# ── 60. Variables again ──────────────────────────────────────

_P60 = _page(
    "variables-more",
    60,
    "Variables again",
    "More practice on page 4.",
    _AGAIN + " The name is doing real work now: read the line out loud and it "
    "should say what it means, which a bare number never does.",
    "let_print",
    [
        (
            f"Put {value} in a variable called {name}, then print {described}.",
            {"name": name, "value": value, "expr": expr},
        )
        for name, value, expr, described in (
            ("total", 240, "total - 40", "total minus 40"),
            ("count", 17, "count + 3", "count plus 3"),
            ("price", 12, "price * 4", "price times 4"),
            ("n", 64, "n % 7", "what is left over when n is divided by 7"),
            ("score", 88, "score - 88", "score minus itself"),
            ("width", 25, "width * width", "width times itself"),
            ("start", 500, "start - 250", "start minus 250"),
            ("n", 6, "n * n * n", "n cubed"),
            ("stock", 144, "stock % 12", "what is left over when stock is divided by 12"),
            ("hours", 9, "hours * 60", "hours times 60"),
            ("n", 31, "n + n + n", "n added to itself twice"),
            ("gap", 75, "gap - 100", "gap minus 100"),
        )
    ],
)


# ── 61. Two values again ─────────────────────────────────────

_P61 = _page(
    "two-values-more",
    61,
    "Two values again",
    "More practice on page 5.",
    _AGAIN + " Two names in scope and a result made from both, which is the "
    "shape of nearly every function you will ever write.",
    "let2_print",
    [
        (
            f"Put {v1} in {n1} and {v2} in {n2}, then print {described}.",
            {
                "name1": n1,
                "value1": v1,
                "name2": n2,
                "value2": v2,
                "expr": expr,
            },
        )
        for n1, v1, n2, v2, expr, described in (
            ("a", 13, "b", 4, "a * b", "a times b"),
            ("cost", 85, "paid", 100, "paid - cost", "paid minus cost"),
            ("x", 7, "y", 11, "x * y + x", "x times y, plus x"),
            ("rows", 6, "cols", 9, "rows * cols", "rows times cols"),
            ("a", 90, "b", 45, "a % b", "what is left over when a is divided by b"),
            ("first", 21, "second", 21, "first + second", "first plus second"),
            ("big", 300, "small", 12, "big - small", "big minus small"),
            ("a", 5, "b", 5, "a * b * b", "a times b twice"),
            ("miles", 26, "each", 2, "miles * each", "miles times each"),
            ("a", 47, "b", 10, "a % b", "what is left over when a is divided by b"),
            ("start", 8, "step", 7, "start + step + step", "start plus two steps"),
            ("n", 100, "m", 3, "n - m * m", "n minus m squared"),
        )
    ],
)


# ── 62. First loops again ────────────────────────────────────

_P62 = _page(
    "first-loop-more",
    62,
    "Counting loops again",
    "More practice on page 6.",
    _AGAIN + " The counter still starts at 0 and still stops before the "
    "count. If that has stopped catching you out, this page is doing its job.",
    "for_print",
    [
        (
            f"Loop {count} times. Each time round, print {described}.",
            {"count": count, "expr": expr},
        )
        for count, expr, described in (
            (6, "i", "the counter"),
            (9, "i", "the counter"),
            (4, "i * 4", "the counter times 4"),
            (7, "i + 7", "the counter plus 7"),
            (5, "i * i", "the counter times itself"),
            (3, "i * 100", "the counter times 100"),
            (8, "i * 2 + 1", "the counter doubled, plus 1"),
            (10, "i", "the counter"),
            (6, "i % 4", "what is left over when the counter is divided by 4"),
            (5, "50 - i", "50 minus the counter"),
            (4, "i * i * i", "the counter cubed"),
            (12, "i * 3", "the counter times 3"),
        )
    ],
)


# ── 63. Ranges again ─────────────────────────────────────────

_P63 = _page(
    "ranges-more",
    63,
    "Ranges again",
    "More practice on page 7.",
    _AGAIN + " Both ends are printed here, unlike page 6's loop. Knowing "
    "which of the two you have written is the whole skill.",
    "for_range_print",
    [
        (
            f"For every number from {lo} to {hi}, print {described}.",
            {"lo": lo, "hi": hi, "expr": expr},
        )
        for lo, hi, expr, described in (
            (4, 11, "i", "the number"),
            (20, 26, "i", "the number"),
            (1, 8, "i * 5", "the number times 5"),
            (7, 14, "i - 6", "the number minus 6"),
            (1, 6, "i * i", "the number times itself"),
            (30, 36, "i", "the number"),
            (2, 9, "i * 12", "the number times 12"),
            (1, 5, "100 - i", "100 minus the number"),
            (11, 20, "i % 5", "what is left over when the number is divided by 5"),
            (1, 7, "i + i + i", "the number added to itself twice"),
            (50, 55, "i - 50", "the number minus 50"),
            (3, 12, "i * 9", "the number times 9"),
        )
    ],
)


# ── 64. Running totals again ─────────────────────────────────

_P64 = _page(
    "totals-more",
    64,
    "Totals again",
    "More practice on page 8.",
    _AGAIN + " Start it at 0 before the loop, add inside, print after. Three "
    "lines in three different places, and putting any of them one step out "
    "gives a wrong answer that looks reasonable.",
    "for_sum",
    [
        (
            f"Add up {described} from {lo} to {hi}, then print the total.",
            {"lo": lo, "hi": hi, "expr": expr},
        )
        for lo, hi, expr, described in (
            (1, 25, "i", "each number"),
            (1, 8, "i * i", "each number times itself"),
            (5, 20, "i", "each number"),
            (1, 15, "i * 4", "each number times 4"),
            (1, 7, "i * i * i", "each number cubed"),
            (10, 30, "i", "each number"),
            (1, 12, "i + 5", "each number plus 5"),
            (2, 11, "i * 7", "each number times 7"),
            (1, 40, "i", "each number"),
            (1, 9, "i * 11", "each number times 11"),
            (3, 13, "i % 3", "the remainder of each number divided by 3"),
            (1, 100, "i * 2", "each number doubled"),
        )
    ],
)


# ── 65. Decisions in loops again ─────────────────────────────

_P65 = _page(
    "filtering-more",
    65,
    "Filtering again",
    "More practice on page 9.",
    _AGAIN + " Fewer lines come out than the loop goes round, and one of "
    "these prints nothing at all — which is still a correct program.",
    "for_if_print",
    [
        (
            f"Go through every number from {lo} to {hi}. Print {out} whenever "
            f"it {cond_text}.",
            {"lo": lo, "hi": hi, "cond": cond, "expr": expr},
        )
        for lo, hi, cond, expr, cond_text, out in (
            (1, 40, "i % 8 == 0", "i", "divides exactly by 8", "the number"),
            (1, 25, "i % 9 == 0", "i", "divides exactly by 9", "the number"),
            (1, 30, "i % 2 == 1", "i", "is odd", "the number"),
            (10, 40, "i % 15 == 0", "i", "divides exactly by 15", "the number"),
            (1, 20, "i > 17", "i", "is bigger than 17", "the number"),
            (1, 50, "i % 20 == 0", "i * 3", "divides exactly by 20", "the number times 3"),
            (1, 12, "i % 13 == 0", "i", "divides exactly by 13", "the number"),
            (1, 18, "i % 3 == 2", "i", "leaves 2 over when divided by 3", "the number"),
            (5, 35, "i % 7 == 0", "i", "divides exactly by 7", "the number"),
            (1, 16, "i % 2 == 0", "i * i", "is even", "the number times itself"),
            (1, 60, "i % 25 == 0", "i", "divides exactly by 25", "the number"),
            (1, 22, "i < 4", "i", "is under 4", "the number"),
        )
    ],
)


# ── 66. Counting down again ──────────────────────────────────

_P66 = _page(
    "countdown-more",
    66,
    "Counting down again",
    "More practice on page 10.",
    _AGAIN + " Start high, stop low, step backwards. Get one of the three "
    "wrong and you print nothing at all, which is at least loud.",
    "for_down",
    [
        (
            f"Count down from {hi} to {lo}. Print {described} each time.",
            {"lo": lo, "hi": hi, "expr": expr},
        )
        for lo, hi, expr, described in (
            (1, 8, "i", "the number"),
            (1, 15, "i", "the number"),
            (0, 6, "i", "the number"),
            (1, 9, "i * 3", "the number times 3"),
            (4, 12, "i", "the number"),
            (1, 7, "i * i", "the number times itself"),
            (20, 30, "i", "the number"),
            (1, 6, "i * 20", "the number times 20"),
            (1, 10, "i + 40", "the number plus 40"),
            (5, 11, "i - 5", "the number minus 5"),
            (1, 5, "i * i * i", "the number cubed"),
            (1, 25, "i % 6", "what is left over when the number is divided by 6"),
        )
    ],
)


# ── 67. Nested loops again ───────────────────────────────────

_P67 = _page(
    "nested-more",
    67,
    "Loops inside loops again",
    "More practice on page 11.",
    _AGAIN + " The line count is the two multiplied together, which is worth "
    "keeping in mind the first time you nest a loop over something big.",
    "for_nested",
    [
        (
            f"Loop the outer number from 1 to {rows}. For each one, loop the "
            f"inner number from 1 to {cols} and print {described}.",
            {"rows": rows, "cols": cols, "expr": expr},
        )
        for rows, cols, expr, described in (
            (3, 3, "i + j", "the two added together"),
            (2, 7, "i * j", "the two multiplied together"),
            (4, 4, "i * j", "the two multiplied together"),
            (5, 3, "i + j", "the two added together"),
            (3, 6, "i * 100 + j", "the outer number times 100, plus the inner one"),
            (2, 2, "i - j", "the outer number minus the inner one"),
            (6, 2, "i * j", "the two multiplied together"),
            (3, 4, "i * i + j * j", "each squared, added together"),
            (4, 5, "i + j", "the two added together"),
            (2, 8, "i * j", "the two multiplied together"),
            (5, 4, "i * 10 - j", "the outer number times 10, minus the inner one"),
            (3, 5, "i * j * 2", "the two multiplied, doubled"),
        )
    ],
)


# ── 68. Values in sentences again ────────────────────────────

_P68 = _page(
    "say-value-more",
    68,
    "Values in sentences again",
    "More practice on page 12.",
    _AGAIN + " Reach for the way your language drops a value into a string "
    "rather than gluing pieces together with a plus sign.",
    "say_value",
    [
        (
            f'Print one line: the word "{label}", then a colon and a space, '
            f"then the answer to {expr}.",
            {"label": label, "expr": expr},
        )
        for label, expr in (
            ("total", "45 + 55"),
            ("left", "200 - 120"),
            ("items", "12 * 6"),
            ("spare", "50 % 8"),
            ("width", "9 * 9"),
            ("days", "365 - 100"),
            ("cost", "25 * 4"),
            ("rest", "1000 % 13"),
            ("sum", "7 + 8 + 9"),
            ("gap", "144 - 44"),
            ("size", "16 * 16"),
            ("share", "97 % 6"),
        )
    ],
)


# ── 69. Quotes again ─────────────────────────────────────────

_P69 = _page(
    "quotes-more",
    69,
    "Quotes again",
    "More practice on page 14.",
    _AGAIN + " Every one of these ends the string early if you forget the "
    "backslash, which is why it is worth a second page.",
    "quoted_text",
    [
        (f"Print this line, with its double quotes: '{t}'.", {"text": t})
        for t in (
            'She wrote "done" and closed it.',
            'The label said "fragile".',
            'He asked "why" twice.',
            'It returns "ok" or nothing.',
            'The header is "Content-Type".',
            'Say "please" first.',
            'The default is "none".',
            'It printed "hello world" and stopped.',
            'Choose "yes" or "no".',
            'The word is "necessary", with one c.',
            'It failed with "timed out".',
            'Type "exit" to leave.',
        )
    ],
)


# ── 70. Only when, again ─────────────────────────────────────

_P70 = _page(
    "only-when-more",
    70,
    "Only when, again",
    "More practice on page 15.",
    _AGAIN + " Half of these still print nothing, and nothing is still the "
    "right answer.",
    "if_print",
    [
        (
            f'Put {value} in {name}. Print "{text}" only if {name} '
            f"{cond_text}.",
            {"name": name, "value": value, "cond": cond, "text": text},
        )
        for name, value, cond, cond_text, text in (
            ("n", 12, "n > 10", "is more than 10", "over"),
            ("n", 4, "n > 10", "is more than 10", "over"),
            ("size", 100, "size >= 100", "is 100 or more", "large"),
            ("size", 99, "size >= 100", "is 100 or more", "large"),
            ("left", 0, "left == 0", "is exactly 0", "none left"),
            ("left", 7, "left == 0", "is exactly 0", "none left"),
            ("n", 21, "n % 7 == 0", "divides exactly by 7", "sevens"),
            ("n", 20, "n % 7 == 0", "divides exactly by 7", "sevens"),
            ("depth", 3, "depth < 5", "is under 5", "shallow"),
            ("depth", 40, "depth < 5", "is under 5", "shallow"),
            ("n", 64, "n % 8 == 0", "divides exactly by 8", "eights"),
            ("n", 63, "n % 8 == 0", "divides exactly by 8", "eights"),
        )
    ],
)


# ── 71. This or that, again ──────────────────────────────────

_P71 = _page(
    "either-or-more",
    71,
    "This or that, again",
    "More practice on page 16.",
    _AGAIN + " Exactly one line comes out every time, whatever the value is. "
    "That is what the else is for.",
    "if_else_print",
    [
        (
            f'Put {value} in {name}. Print "{yes}" if {name} {cond_text}, '
            f'and "{no}" if it does not.',
            {
                "name": name,
                "value": value,
                "cond": cond,
                "yes": yes,
                "no": no,
            },
        )
        for name, value, cond, cond_text, yes, no in (
            ("n", 33, "n > 30", "is more than 30", "over", "under"),
            ("n", 8, "n > 30", "is more than 30", "over", "under"),
            ("mark", 71, "mark >= 70", "is 70 or more", "merit", "plain"),
            ("mark", 69, "mark >= 70", "is 70 or more", "merit", "plain"),
            ("n", 100, "n % 4 == 0", "divides exactly by 4", "quarters", "not quarters"),
            ("n", 102, "n % 4 == 0", "divides exactly by 4", "quarters", "not quarters"),
            ("left", 1, "left > 0", "is more than 0", "some", "none"),
            ("left", 0, "left > 0", "is more than 0", "some", "none"),
            ("year", 2026, "year >= 2000", "is 2000 or later", "modern", "old"),
            ("year", 1985, "year >= 2000", "is 2000 or later", "modern", "old"),
            ("n", 45, "n % 2 == 1", "is odd", "odd", "even"),
            ("n", 46, "n % 2 == 1", "is odd", "odd", "even"),
        )
    ],
)


# ── 72. While loops again ────────────────────────────────────

_P72 = _page(
    "while-loop-more",
    72,
    "While loops again",
    "More practice on page 19.",
    _AGAIN + " Start it, test it, move it. Forgetting the third is still the "
    "way to write a loop that never ends.",
    "while_count",
    [
        (
            f"Using a while loop rather than a for loop, print {described} "
            f"for every number from {lo} to {hi}.",
            {"lo": lo, "hi": hi, "expr": expr},
        )
        for lo, hi, expr, described in (
            (1, 7, "i", "the number"),
            (4, 12, "i", "the number"),
            (1, 9, "i * 6", "the number times 6"),
            (1, 5, "i * i", "the number times itself"),
            (20, 27, "i", "the number"),
            (1, 11, "i + 20", "the number plus 20"),
            (2, 10, "i * 15", "the number times 15"),
            (1, 6, "100 - i", "100 minus the number"),
            (7, 16, "i - 7", "the number minus 7"),
            (1, 13, "i % 5", "what is left over when the number is divided by 5"),
            (1, 8, "i * i * i", "the number cubed"),
            (30, 38, "i", "the number"),
        )
    ],
)


# ── 73. Lists again ──────────────────────────────────────────

_P73 = _page(
    "lists-more",
    73,
    "Lists again",
    "More practice on page 21.",
    _AGAIN + " No index anywhere: the loop hands you the things themselves.",
    "list_loop",
    [
        (
            f"Put the numbers {_list(items)} in a list, then print {described}.",
            {"items": items, "expr": expr},
        )
        for items, expr, described in (
            ([14, 25, 36], "n", "each one"),
            ([2, 3, 5, 7, 11], "n", "each one"),
            ([100, 250, 400], "n - 100", "each one minus 100"),
            ([8, 16, 32], "n * 2", "each one doubled"),
            ([9, 18, 27, 36], "n % 9", "the remainder of each one divided by 9"),
            ([5, 10], "n * n", "each one times itself"),
            ([21, 42, 63], "n + 9", "each one plus 9"),
            ([1, 4, 9, 16, 25], "n", "each one"),
            ([60, 30, 15], "n * 3", "each one times 3"),
            ([7], "n * 100", "each one times 100"),
            ([12, 24, 36, 48], "n % 10", "the last digit of each one"),
            ([1000, 500], "n - 499", "each one minus 499"),
        )
    ],
)


# ── 74. List totals again ────────────────────────────────────

_P74 = _page(
    "list-total-more",
    74,
    "List totals again",
    "More practice on page 22.",
    _AGAIN + " The same running total as page 8, pointed at a list instead "
    "of a range.",
    "list_sum",
    [
        (
            f"Put the numbers {_list(items)} in a list, add them all up, and "
            f"print the total.",
            {"items": items},
        )
        for items in (
            [14, 26, 30],
            [1, 2, 4, 8, 16, 32],
            [100, 100, 100],
            [7, 14, 21, 28],
            [45],
            [12, 34, 56, 78],
            [5, 5, 5, 5, 5, 5],
            [250, 250, 500],
            [3, 6, 9, 12, 15, 18],
            [11, 111],
            [40, 30, 20, 10, 5],
            [2, 4, 6, 8, 10, 12, 14],
        )
    ],
)


# ── 75. Filtering lists again ────────────────────────────────

_P75 = _page(
    "list-filter-more",
    75,
    "Filtering lists again",
    "More practice on page 24.",
    _AGAIN + " One of these matches nothing, and a filter that matches "
    "nothing is still a working filter.",
    "list_filter",
    [
        (
            f"Put the numbers {_list(items)} in a list. Print only the ones "
            f"that {described}.",
            {"items": items, "cond": cond},
        )
        for items, cond, described in (
            ([14, 21, 35, 8], "n % 7 == 0", "divide exactly by 7"),
            ([5, 12, 19, 26], "n > 15", "are more than 15"),
            ([60, 45, 30, 15], "n % 30 == 0", "divide exactly by 30"),
            ([1, 2, 3], "n > 50", "are more than 50"),
            ([8, 16, 24, 32], "n % 16 == 0", "divide exactly by 16"),
            ([99, 100, 101], "n % 2 == 0", "are even"),
            ([13, 26, 39, 52], "n % 13 == 0", "divide exactly by 13"),
            ([4, 8, 15, 16, 23, 42], "n < 16", "are less than 16"),
            ([200, 400, 600], "n >= 400", "are 400 or more"),
            ([9, 18, 27], "n % 2 == 1", "are odd"),
            ([1, 10, 100, 1000], "n > 99", "are more than 99"),
            ([6, 12, 18, 24, 30], "n % 12 == 0", "divide exactly by 12"),
        )
    ],
)


# ── 76. Building lists again ─────────────────────────────────

_P76 = _page(
    "list-build-more",
    76,
    "Building lists again",
    "More practice on page 25.",
    _AGAIN + " Fill it in one loop, read it back in another. Once it exists "
    "you can do anything with it.",
    "list_build",
    [
        (
            f"Start with an empty list. Loop from {lo} to {hi}, adding "
            f"{described} to the list each time. Then print every item in it.",
            {"lo": lo, "hi": hi, "expr": expr},
        )
        for lo, hi, expr, described in (
            (1, 6, "i * 6", "the number times 6"),
            (2, 8, "i * i", "the number times itself"),
            (1, 5, "i + 50", "the number plus 50"),
            (10, 15, "i - 9", "the number minus 9"),
            (1, 4, "i * 25", "the number times 25"),
            (3, 9, "i * 2", "the number doubled"),
            (1, 7, "100 - i", "100 minus the number"),
            (1, 3, "i * i * i * i", "the number to the fourth"),
            (5, 12, "i % 4", "the remainder of the number divided by 4"),
            (1, 8, "i * 11", "the number times 11"),
            (20, 25, "i * 2", "the number doubled"),
            (1, 9, "i + i", "the number added to itself"),
        )
    ],
)


# ── 77. Functions again ──────────────────────────────────────

_P77 = _page(
    "function-args-more",
    77,
    "Functions with a value, again",
    "More practice on page 28.",
    _AGAIN + " The name in the brackets only exists inside the function, and "
    "stands for whatever the caller hands it.",
    "func_arg",
    [
        (
            f"Write a function called {name} that takes a number and prints "
            f"{described}. Call it with " + ", then ".join(str(v) for v in calls) + ".",
            {"name": name, "param": "n", "expr": expr, "calls": calls},
        )
        for name, expr, described, calls in (
            ("quad", "n * 4", "the number times 4", [3, 25]),
            ("less5", "n - 5", "the number minus 5", [12, 5]),
            ("sixty", "n * 60", "the number times 60", [2, 7]),
            ("sq", "n * n", "the number times itself", [11, 12, 13]),
            ("half", "n % 2", "the remainder when divided by 2", [7, 100]),
            ("plus99", "n + 99", "the number plus 99", [1, 901]),
            ("dozen", "n * 12", "the number times 12", [3, 10]),
            ("digit", "n % 10", "the last digit", [123, 90]),
            ("thrice", "n * 3", "the number times 3", [15, 33]),
            ("back", "100 - n", "100 minus the number", [1, 99]),
            ("cube", "n * n * n", "the number cubed", [3, 5]),
            ("odd", "n * 2 + 1", "twice the number plus 1", [0, 7, 20]),
        )
    ],
)


# ── 78. Returning again ──────────────────────────────────────

_P78 = _page(
    "function-returns-more",
    78,
    "Returning a value, again",
    "More practice on page 29.",
    _AGAIN + " The printing lives at the call, not in the function — which "
    "is why the function can be used for anything else too.",
    "func_return",
    [
        (
            f"Write a function called {name} that takes a number and returns "
            f"{described}. Print the result of calling it with "
            + ", then ".join(str(v) for v in calls)
            + ".",
            {"name": name, "param": "n", "expr": expr, "calls": calls},
        )
        for name, expr, described, calls in (
            ("sixx", "n * 6", "the number times 6", [4, 12]),
            ("minus7", "n - 7", "the number minus 7", [20, 7]),
            ("sq", "n * n", "the number times itself", [9, 15]),
            ("hundred", "n * 100", "the number times 100", [3, 8]),
            ("rest9", "n % 9", "the remainder when divided by 9", [40, 81]),
            ("plusone", "n + 1", "the number plus 1", [0, 999]),
            ("twice", "n + n", "the number added to itself", [17, 50]),
            ("cube", "n * n * n", "the number cubed", [4, 6]),
            ("half10", "n % 10", "the last digit", [456, 70]),
            ("nine", "n * 9", "the number times 9", [5, 11]),
            ("down", "1000 - n", "1000 minus the number", [1, 500]),
            ("sqplus", "n * n + n", "the number squared plus itself", [3, 8]),
        )
    ],
)


# ── 79. Characters again ─────────────────────────────────────

_P79 = _page(
    "string-loop-more",
    79,
    "One character at a time, again",
    "More practice on page 31.",
    _AGAIN + " A string behaves like a list of characters when you loop over "
    "it, which is the same loop pointed somewhere new.",
    "str_loop",
    [
        (f'Print each character of the word "{w}" on its own line.', {"word": w})
        for w in (
            "again",
            "loop",
            "chars",
            "up",
            "practice",
            "word",
            "x",
            "middle",
            "steady",
            "nearly",
            "last",
            "end",
        )
    ],
)


# ── 80. Labelling again ──────────────────────────────────────

_P80 = _page(
    "label-each-more",
    80,
    "A word for each one, again",
    "More practice on page 41.",
    _AGAIN + " One line out for every item in, which is what makes this "
    "different from filtering.",
    "label_each",
    [
        (
            f"Put the numbers {_list(items)} in a list. For each one print "
            f'"{yes}" if it {described}, and "{no}" if it does not.',
            {"items": items, "cond": cond, "yes": yes, "no": no},
        )
        for items, cond, described, yes, no in (
            ([4, 7, 10, 13], "n % 2 == 0", "divides by 2", "even", "odd"),
            ([100, 20, 300, 40], "n >= 100", "is 100 or more", "big", "small"),
            ([9, 18, 20, 27], "n % 9 == 0", "divides by 9", "nines", "no"),
            ([1, 2, 3, 4, 5], "n > 3", "is more than 3", "high", "low"),
            ([14, 21, 28, 30], "n % 7 == 0", "divides by 7", "sevens", "no"),
            ([0, 5, 0, 5], "n == 0", "is 0", "zero", "not zero"),
            ([11, 22, 33, 44], "n % 11 == 0", "divides by 11", "yes", "no"),
            ([6, 60, 600], "n > 100", "is more than 100", "large", "small"),
            ([2, 4, 5, 8], "n % 4 == 0", "divides by 4", "quarters", "no"),
            ([15, 25, 35], "n % 5 == 0", "divides by 5", "fives", "no"),
            ([1, 3, 5, 7, 9], "n % 2 == 1", "is odd", "odd", "even"),
            ([50, 49, 51], "n == 50", "is exactly 50", "fifty", "other"),
        )
    ],
)


PRACTICE_PAGES: tuple[Page, ...] = (
    _P57,
    _P58,
    _P59,
    _P60,
    _P61,
    _P62,
    _P63,
    _P64,
    _P65,
    _P66,
    _P67,
    _P68,
    _P69,
    _P70,
    _P71,
    _P72,
    _P73,
    _P74,
    _P75,
    _P76,
    _P77,
    _P78,
    _P79,
    _P80,
)
