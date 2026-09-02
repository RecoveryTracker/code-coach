"""The pages themselves.

Nine pages, twelve exercises each. Every page is one new idea and eleven more
goes at it, and every page's idea is the page before it plus one thing.

Ordering rule: a page never needs anything a later page introduces. So the
loops arrive after variables, the running total after loops, and the decision
inside the loop last — by which point the loop itself is not the hard part
any more, which is the only reason the decision can be.

Division is missing on purpose. Whether `7 / 2` is 3 or 3.5 is a different
answer in half these languages, and a workbook exercise with two right
answers is a bad exercise. Remainder behaves the same everywhere as long as
both sides are positive, and every exercise here keeps them positive.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page
from code_coach.workbook.content2 import MORE_PAGES
from code_coach.workbook.content3 import MORE_PAGES_3
from code_coach.workbook.content4 import MORE_PAGES_4
from code_coach.workbook.content5 import MORE_PAGES_5
from code_coach.workbook.content_intermediate import INTERMEDIATE_PAGES
from code_coach.workbook.content_practice import PRACTICE_PAGES


# Positional-only up to the shape, so a shape argument can share a name
# with one of these without colliding — page 44 passes n= for the times
# table, which is exactly the clash this prevents.
def _ex(
    page_id: str, n: int, prompt: str, shape: str, /, **args
) -> Exercise:
    return Exercise(
        id=f"{page_id}-{n:02d}", prompt=prompt, shape=shape, args=args
    )


# ── 1. Printing ──────────────────────────────────────────────

_TEXTS = (
    "hello",
    "hello world",
    "Code Coach",
    "ready",
    "one line",
    "typing this out",
    "again",
    "and again",
    "no shortcuts",
    "muscle memory",
    "last one",
    "done",
)

_P1 = Page(
    id="printing",
    number=1,
    name="Printing",
    teaches="Getting a line of text onto the screen.",
    example=(
        "Every exercise here is the same one line with different words in it. "
        "That is deliberate — by the twelfth you should be typing it without "
        "looking."
    ),
    exercises=tuple(
        # Quoted and closed with a full stop, because "Print this exactly:
        # hello." leaves you wondering whether the full stop is part of it.
        _ex(
            "printing",
            i + 1,
            f'Print the line "{text}".',
            "print_text",
            text=text,
        )
        for i, text in enumerate(_TEXTS)
    ),
)


# ── 2. Adding and taking away ────────────────────────────────

_SUMS = (
    ("3 + 4", "3 + 4"),
    ("10 + 25", "10 + 25"),
    ("9 - 2", "9 - 2"),
    ("100 - 37", "100 - 37"),
    ("12 + 8", "12 + 8"),
    ("64 - 15", "64 - 15"),
    ("7 + 7 + 7", "7 + 7 + 7"),
    ("50 - 20 - 5", "50 - 20 - 5"),
    ("18 + 24", "18 + 24"),
    ("200 - 99", "200 - 99"),
    ("6 + 11 - 4", "6 + 11 - 4"),
    ("31 - 12 + 6", "31 - 12 + 6"),
)

_P2 = Page(
    id="arithmetic",
    number=2,
    name="Adding and taking away",
    teaches="Printing the result of a sum instead of a fixed piece of text.",
    example=(
        "Same one line as page 1, except what goes inside is worked out first. "
        "Do not print the sum as text — print what it comes to."
    ),
    exercises=tuple(
        _ex("arithmetic", i + 1, f"Print the answer to {label}.", "print_expr", expr=expr)
        for i, (label, expr) in enumerate(_SUMS)
    ),
)


# ── 3. Times and what is left over ───────────────────────────

_P3 = Page(
    id="multiply",
    number=3,
    name="Times, and what is left over",
    teaches=(
        "Multiplying, and the remainder operator — the one that answers "
        "\"what is left after dividing\"."
    ),
    example=(
        "The remainder of 17 divided by 5 is 2, because 5 goes into 17 three "
        "times with 2 to spare. In every language on this list that is written "
        "17 % 5."
    ),
    exercises=(
        _ex("multiply", 1, "Print the answer to 7 times 6.", "print_expr", expr="7 * 6"),
        _ex("multiply", 2, "Print the answer to 12 times 12.", "print_expr", expr="12 * 12"),
        _ex("multiply", 3, "Print what is left over when 17 is divided by 5.", "print_expr", expr="17 % 5"),
        _ex("multiply", 4, "Print what is left over when 100 is divided by 7.", "print_expr", expr="100 % 7"),
        _ex("multiply", 5, "Print the answer to 9 times 8.", "print_expr", expr="9 * 8"),
        _ex("multiply", 6, "Print what is left over when 45 is divided by 6.", "print_expr", expr="45 % 6"),
        _ex("multiply", 7, "Print the answer to 25 times 4.", "print_expr", expr="25 * 4"),
        _ex("multiply", 8, "Print what is left over when 30 is divided by 4.", "print_expr", expr="30 % 4"),
        _ex("multiply", 9, "Print the answer to 3 times 4 plus 5.", "print_expr", expr="3 * 4 + 5"),
        _ex("multiply", 10, "Print what is left over when 99 is divided by 10.", "print_expr", expr="99 % 10"),
        _ex("multiply", 11, "Print the answer to 6 times 7 minus 12.", "print_expr", expr="6 * 7 - 12"),
        _ex("multiply", 12, "Print what is left over when 1000 is divided by 3.", "print_expr", expr="1000 % 3"),
    ),
)


# ── 4. Holding a value ───────────────────────────────────────

_ONE_VALUE = (
    ("n", 8, "n + 5", "n plus 5"),
    ("n", 20, "n - 3", "n minus 3"),
    ("count", 6, "count * 2", "count times 2"),
    ("x", 15, "x + x", "x plus itself"),
    ("total", 100, "total - 45", "total minus 45"),
    ("n", 7, "n * n", "n times itself"),
    ("price", 30, "price * 3", "price times 3"),
    ("n", 19, "n % 4", "what is left over when n is divided by 4"),
    ("start", 5, "start + 10", "start plus 10"),
    ("n", 12, "n * 5 - 2", "n times 5, minus 2"),
    ("size", 9, "size * size", "size times itself"),
    ("n", 47, "n % 10", "what is left over when n is divided by 10"),
)

_P4 = Page(
    id="variables",
    number=4,
    name="Holding a value",
    teaches="Putting a number in a variable first, then using it.",
    example=(
        "Two lines now instead of one: give the value a name, then print "
        "something worked out from that name. The point is the name — the "
        "answer would be the same without it, and every page after this one "
        "needs it."
    ),
    exercises=tuple(
        _ex(
            "variables",
            i + 1,
            f"Put {value} in a variable called {name}, then print {described}.",
            "let_print",
            name=name,
            value=value,
            expr=expr,
        )
        for i, (name, value, expr, described) in enumerate(_ONE_VALUE)
    ),
)


# ── 5. Two values ────────────────────────────────────────────

_TWO_VALUES = (
    ("a", 6, "b", 7, "a * b", "a times b"),
    ("a", 12, "b", 30, "a + b", "a plus b"),
    ("width", 4, "height", 9, "width * height", "width times height"),
    ("total", 90, "spent", 35, "total - spent", "total minus spent"),
    ("a", 8, "b", 3, "a - b", "a minus b"),
    ("x", 5, "y", 5, "x * y + x", "x times y, plus x"),
    ("first", 14, "second", 6, "first + second", "first plus second"),
    ("n", 23, "d", 5, "n % d", "what is left over when n is divided by d"),
    ("a", 11, "b", 2, "a * b - 1", "a times b, minus 1"),
    ("hours", 7, "rate", 20, "hours * rate", "hours times rate"),
    ("a", 100, "b", 64, "a - b", "a minus b"),
    ("n", 17, "m", 4, "n % m + m", "the remainder of n divided by m, plus m"),
)

_P5 = Page(
    id="two-values",
    number=5,
    name="Two values",
    teaches="Two variables, and a result worked out from both of them.",
    example=(
        "Three lines. Nothing new except that there are two names in scope "
        "instead of one — but that is the shape every real function has, so "
        "it is worth a page of its own."
    ),
    exercises=tuple(
        _ex(
            "two-values",
            i + 1,
            f"Put {v1} in {n1} and {v2} in {n2}, then print {described}.",
            "let2_print",
            name1=n1,
            value1=v1,
            name2=n2,
            value2=v2,
            expr=expr,
        )
        for i, (n1, v1, n2, v2, expr, described) in enumerate(_TWO_VALUES)
    ),
)


# ── 6. Your first loop ───────────────────────────────────────

_FIRST_LOOP = (
    (5, "i", "the counter"),
    (3, "i", "the counter"),
    (8, "i", "the counter"),
    (5, "i + 1", "the counter plus 1"),
    (4, "i + 1", "the counter plus 1"),
    (6, "i * 2", "the counter times 2"),
    (5, "i * 2", "the counter times 2"),
    (4, "i * 10", "the counter times 10"),
    (5, "i * i", "the counter times itself"),
    (7, "i + 100", "the counter plus 100"),
    (3, "i * 5 + 1", "the counter times 5, plus 1"),
    (6, "i % 3", "what is left over when the counter is divided by 3"),
)

_P6 = Page(
    id="first-loop",
    number=6,
    name="Your first loop",
    teaches="Doing the same thing a fixed number of times.",
    example=(
        "The counter starts at 0 and stops before the count, so looping 5 "
        "times gives you 0, 1, 2, 3, 4 — five lines, and the last one is 4, "
        "not 5. That off-by-one is the whole page. Get it wrong once here "
        "rather than in an interview."
    ),
    exercises=tuple(
        _ex(
            "first-loop",
            i + 1,
            f"Loop {count} times. Each time round, print {described}.",
            "for_print",
            count=count,
            expr=expr,
        )
        for i, (count, expr, described) in enumerate(_FIRST_LOOP)
    ),
)


# ── 7. Choosing where it starts and stops ────────────────────

_RANGES = (
    (3, 9, "i", "the number"),
    (1, 5, "i", "the number"),
    (10, 20, "i", "the number"),
    (1, 10, "i * 2", "the number doubled"),
    (5, 10, "i * i", "the number times itself"),
    (0, 6, "i * 3", "the number times 3"),
    (2, 8, "i + 10", "the number plus 10"),
    (1, 12, "i * 7", "the number times 7"),
    (20, 25, "i - 20", "the number minus 20"),
    (1, 6, "i * i * i", "the number cubed"),
    (4, 12, "i % 4", "what is left over when the number is divided by 4"),
    (1, 9, "i * 11", "the number times 11"),
)

_P7 = Page(
    id="ranges",
    number=7,
    name="Choosing where it starts and stops",
    teaches="A loop over a range you pick, ends included.",
    example=(
        "\"From 3 to 9\" means 3 and 9 are both printed — seven lines, not "
        "six. Page 6's loop stopped before its limit; this one stops after "
        "it. Knowing which one you have written is most of the job."
    ),
    exercises=tuple(
        _ex(
            "ranges",
            i + 1,
            f"For every number from {lo} to {hi}, print {described}.",
            "for_range_print",
            lo=lo,
            hi=hi,
            expr=expr,
        )
        for i, (lo, hi, expr, described) in enumerate(_RANGES)
    ),
)


# ── 8. Keeping a running total ───────────────────────────────

_SUMMING = (
    (1, 10, "i", "each number"),
    (1, 5, "i", "each number"),
    (1, 100, "i", "each number"),
    (1, 10, "i * i", "each number times itself"),
    (1, 20, "i * 2", "each number doubled"),
    (5, 15, "i", "each number"),
    (1, 6, "i * i * i", "each number cubed"),
    (1, 12, "i + 1", "each number plus 1"),
    (10, 20, "i * 3", "each number times 3"),
    (1, 9, "i * 10", "each number times 10"),
    (2, 8, "i % 3", "the remainder of each number divided by 3"),
    (1, 50, "i", "each number"),
)

_P8 = Page(
    id="totals",
    number=8,
    name="Keeping a running total",
    teaches="A variable that survives the loop and collects as it goes.",
    example=(
        "Start the total at 0 *before* the loop, add to it inside, and print "
        "it *after*. Declaring it inside the loop is the classic mistake: it "
        "gets wiped every time round and you print the last value instead of "
        "the sum."
    ),
    exercises=tuple(
        _ex(
            "totals",
            i + 1,
            f"Add up {described} from {lo} to {hi}, then print the total.",
            "for_sum",
            lo=lo,
            hi=hi,
            expr=expr,
        )
        for i, (lo, hi, expr, described) in enumerate(_SUMMING)
    ),
)


# ── 9. A decision inside the loop ────────────────────────────

_FILTERED = (
    (1, 20, "i % 3 == 0", "i", "divides exactly by 3", "the number"),
    (1, 20, "i % 2 == 0", "i", "is even", "the number"),
    (1, 20, "i % 2 == 1", "i", "is odd", "the number"),
    (1, 30, "i % 5 == 0", "i", "divides exactly by 5", "the number"),
    (1, 15, "i > 10", "i", "is bigger than 10", "the number"),
    (1, 20, "i % 4 == 0", "i * 2", "divides exactly by 4", "the number doubled"),
    (1, 25, "i % 10 == 0", "i", "divides exactly by 10", "the number"),
    (1, 12, "i % 2 == 0", "i * i", "is even", "the number times itself"),
    (5, 25, "i % 7 == 0", "i", "divides exactly by 7", "the number"),
    (1, 20, "i % 6 == 0", "i", "divides exactly by 6", "the number"),
    (1, 40, "i % 11 == 0", "i", "divides exactly by 11", "the number"),
    (1, 20, "i % 3 == 1", "i", "leaves 1 over when divided by 3", "the number"),
)

_P9 = Page(
    id="filtering",
    number=9,
    name="A decision inside the loop",
    teaches="Running the body only some of the time.",
    example=(
        "The loop still visits every number. What changes is that only some "
        "of them get printed — so the number of lines out is smaller than the "
        "number of times round. That gap is the idea."
    ),
    exercises=tuple(
        _ex(
            "filtering",
            i + 1,
            f"Go through every number from {lo} to {hi}. Print {out} "
            f"whenever it {cond_text}.",
            "for_if_print",
            lo=lo,
            hi=hi,
            cond=cond,
            expr=expr,
        )
        for i, (lo, hi, cond, expr, cond_text, out) in enumerate(_FILTERED)
    ),
)


# ── 10. Counting down ────────────────────────────────────────

_COUNTDOWN = (
    (1, 5, "i", "the number"),
    (1, 10, "i", "the number"),
    (0, 4, "i", "the number"),
    (1, 6, "i * 2", "the number doubled"),
    (5, 15, "i", "the number"),
    (1, 8, "i * i", "the number times itself"),
    (10, 20, "i", "the number"),
    (1, 5, "i * 10", "the number times 10"),
    (1, 12, "i + 100", "the number plus 100"),
    (3, 9, "i - 3", "the number minus 3"),
    (1, 7, "i * 3", "the number times 3"),
    (1, 20, "i % 5", "what is left over when the number is divided by 5"),
)

_P10 = Page(
    id="countdown",
    number=10,
    name="Counting down",
    teaches="The same loop, running the other way.",
    example=(
        "Start at the top, stop at the bottom, and step backwards instead of "
        "forwards. Three things change and getting any one of them wrong "
        "gives you either nothing at all or a loop that never stops — which "
        "is why this gets a page rather than a footnote."
    ),
    exercises=tuple(
        _ex(
            "countdown",
            i + 1,
            f"Count down from {hi} to {lo}. Print {described} each time.",
            "for_down",
            lo=lo,
            hi=hi,
            expr=expr,
        )
        for i, (lo, hi, expr, described) in enumerate(_COUNTDOWN)
    ),
)


# ── 11. A loop inside a loop ─────────────────────────────────

_NESTED = (
    (2, 3, "i * j", "the two multiplied together"),
    (3, 3, "i * j", "the two multiplied together"),
    (2, 4, "i + j", "the two added together"),
    (3, 2, "i * j", "the two multiplied together"),
    (4, 2, "i + j", "the two added together"),
    (2, 5, "i * j", "the two multiplied together"),
    (3, 4, "i * 10 + j", "the outer number times 10, plus the inner one"),
    (5, 2, "i - j", "the outer number minus the inner one"),
    (2, 6, "i * j", "the two multiplied together"),
    (4, 3, "i * i + j", "the outer number squared, plus the inner one"),
    (3, 5, "i + j", "the two added together"),
    (4, 4, "i * j", "the two multiplied together"),
)

_P11 = Page(
    id="nested",
    number=11,
    name="A loop inside a loop",
    teaches="Every step of the outer loop runs the whole inner one.",
    example=(
        "An outer loop of 3 wrapped round an inner loop of 4 prints twelve "
        "lines, not seven. That multiplication is the idea, and it is also "
        "why a nested loop over a big list is the thing that quietly makes a "
        "program too slow."
    ),
    exercises=tuple(
        _ex(
            "nested",
            i + 1,
            f"Loop the outer number from 1 to {rows}. For each one, loop the "
            f"inner number from 1 to {cols} and print {described}.",
            "for_nested",
            rows=rows,
            cols=cols,
            expr=expr,
        )
        for i, (rows, cols, expr, described) in enumerate(_NESTED)
    ),
)


_FIRST: tuple[Page, ...] = (
    _P1,
    _P2,
    _P3,
    _P4,
    _P5,
    _P6,
    _P7,
    _P8,
    _P9,
    _P10,
    _P11,
)

# Pages 12 onwards are Python, JavaScript and Dart only, and say so
# themselves — see content2 for why.
# Teaching pages first, then the practice pages that rework their shapes.
# The practice pages sit at the end rather than beside the ones they drill
# because the teaching examples refer to each other by number, and
# interleaving would make every one of those references wrong.
PAGES: tuple[Page, ...] = (
    _FIRST
    + MORE_PAGES
    + MORE_PAGES_3
    + MORE_PAGES_4
    + MORE_PAGES_5
    + PRACTICE_PAGES
    + INTERMEDIATE_PAGES
)
