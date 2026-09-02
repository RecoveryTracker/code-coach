"""Pages 12 onwards: text, conditions, while loops, lists and functions.

Where pages 1 to 11 are arithmetic and counting loops, these are the parts
that look different in every language — a list, a string method, a function
signature. Every one of them is offered in all seven the workbook covers,
with each language's answer written the way that language actually does it
rather than the way the others do.

Same rule as before — one new idea per page, a dozen goes at it, and nothing
on a page needs anything a later page introduces. The order is roughly the
order you would need them: say something about a value, decide, repeat until
done, hold many values, then name a piece of work so you can reuse it.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

# Everywhere the workbook runs. These pages started as Python, JavaScript and
# Dart, because a list and a string are genuinely different objects in C and
# writing them for seven looked like it would mean faking something. It did
# not: `emit_more_native` answers each one the way that language actually
# would, which is worth more than the shortcut would have been.
WORKBOOK_LANGUAGES = (
    "python",
    "javascript",
    "typescript",
    "dart",
    "c",
    "cpp",
    "rust",
)


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


# ── 12. A value inside a sentence ────────────────────────────

_SAY = (
    ("score", "3 + 4"),
    ("total", "10 + 25"),
    ("left", "20 - 8"),
    ("answer", "6 * 7"),
    ("count", "100 - 1"),
    ("age", "40 + 2"),
    ("cost", "3 * 15"),
    ("spare", "17 % 5"),
    ("year", "2000 + 26"),
    ("lines", "12 * 12"),
    ("gap", "88 - 46"),
    ("share", "1000 % 7"),
)

_P12 = _page(
    "say-value",
    12,
    "A value inside a sentence",
    "Putting a worked-out number in the middle of a line of text.",
    "Every language here has a way to drop a value into a string rather than "
    "gluing pieces together, and it is the way you should reach for. Sticking "
    "text and numbers together with a plus sign is the thing that goes wrong "
    "later, because it means different things depending on what is on each "
    "side.",
    [
        _ex(
            "say-value",
            i + 1,
            f'Print one line: the word "{label}", then a colon and a space, '
            f"then the answer to {expr}.",
            "say_value",
            label=label,
            expr=expr,
        )
        for i, (label, expr) in enumerate(_SAY)
    ],
)


# ── 13. Saying it again ──────────────────────────────────────

_REPEATS = (
    (3, "hello"),
    (5, "again"),
    (2, "twice over"),
    (4, "keep going"),
    (6, "steady"),
    (3, "one more time"),
    (7, "seven of these"),
    (2, "short"),
    (8, "eight lines"),
    (4, "no counter needed"),
    (5, "same every time"),
    (10, "ten"),
)

_P13 = _page(
    "repeat",
    13,
    "Saying it again",
    "A loop whose body ignores the counter.",
    "The loop still counts, but nothing inside it uses the count — the "
    "counter is only there to say how many times. That is worth meeting on "
    "its own, because up to now every loop body has used i and it is easy to "
    "think it has to.",
    [
        _ex(
            "repeat",
            i + 1,
            f'Print the line "{text}" {count} times.',
            "repeat_text",
            count=count,
            text=text,
        )
        for i, (count, text) in enumerate(_REPEATS)
    ],
)


# ── 14. Quotes inside quotes ─────────────────────────────────

_QUOTED = (
    'She said "hello".',
    'He shouted "stop" and it stopped.',
    'The sign read "no entry".',
    'It is spelled "necessary".',
    'Type "yes" to continue.',
    'The file is called "notes.txt".',
    'They call it "the hard part".',
    'Press "q" to quit.',
    'The answer is "it depends".',
    'A string is "text in quotes".',
    'Reply "ok" when you are done.',
    'The error said "not found".',
)

_P14 = _page(
    "quotes",
    14,
    "Quotes inside quotes",
    "Getting a quotation mark into a string that quotation marks delimit.",
    "The moment you write a double quote inside a double-quoted string, the "
    "string ends there and the rest is nonsense. A backslash in front of it "
    "says you meant the character rather than the end. This is the single "
    "most common way a beginner's line stops compiling.",
    [
        _ex(
            "quotes",
            i + 1,
            f"Print this line, with its double quotes: '{text}'.",
            "quoted_text",
            text=text,
        )
        for i, text in enumerate(_QUOTED)
    ],
)


# ── 15. Only when ────────────────────────────────────────────

_ONLY_WHEN = (
    ("n", 7, "n > 5", "is more than 5", "big"),
    ("n", 3, "n > 5", "is more than 5", "big"),
    ("age", 20, "age >= 18", "is 18 or more", "allowed"),
    ("age", 15, "age >= 18", "is 18 or more", "allowed"),
    ("count", 0, "count == 0", "is exactly 0", "empty"),
    ("count", 4, "count == 0", "is exactly 0", "empty"),
    ("temp", 31, "temp > 30", "is above 30", "hot"),
    ("temp", 12, "temp > 30", "is above 30", "hot"),
    ("n", 8, "n % 2 == 0", "divides exactly by 2", "even"),
    ("n", 9, "n % 2 == 0", "divides exactly by 2", "even"),
    ("stock", 2, "stock < 5", "is under 5", "running low"),
    ("stock", 40, "stock < 5", "is under 5", "running low"),
)

_P15 = _page(
    "only-when",
    15,
    "Only when",
    "Running a line only if something is true.",
    "Half of these print nothing at all, and that is the exercise. A "
    "condition that does not hold means the body never runs, so the right "
    "answer really is an empty screen — which is worth seeing on purpose "
    "here rather than being puzzled by later.",
    [
        _ex(
            "only-when",
            i + 1,
            f'Put {value} in {name}. Print "{text}" only if {name} '
            f"{cond_text}.",
            "if_print",
            name=name,
            value=value,
            cond=cond,
            text=text,
        )
        for i, (name, value, cond, cond_text, text) in enumerate(_ONLY_WHEN)
    ],
)


# ── 16. This or that ─────────────────────────────────────────

_EITHER = (
    ("n", 7, "n > 5", "is more than 5", "big", "small"),
    ("n", 2, "n > 5", "is more than 5", "big", "small"),
    ("age", 20, "age >= 18", "is 18 or more", "adult", "child"),
    ("score", 45, "score >= 50", "is 50 or more", "pass", "fail"),
    ("score", 80, "score >= 50", "is 50 or more", "pass", "fail"),
    ("n", 10, "n % 2 == 0", "divides exactly by 2", "even", "odd"),
    ("n", 7, "n % 2 == 0", "divides exactly by 2", "even", "odd"),
    ("stock", 0, "stock > 0", "is more than 0", "in stock", "sold out"),
    ("stock", 9, "stock > 0", "is more than 0", "in stock", "sold out"),
    ("hour", 21, "hour < 12", "is under 12", "morning", "afternoon"),
    ("speed", 70, "speed > 60", "is over 60", "too fast", "fine"),
    ("balance", -5, "balance < 0", "is below 0", "overdrawn", "in credit"),
)

_P16 = _page(
    "either-or",
    16,
    "This or that",
    "Two outcomes, exactly one of which happens.",
    "The else branch runs when the condition does not, so exactly one line "
    "comes out no matter what the value is. Writing two separate ifs would "
    "usually work and is worse: they can both run, or neither, and nothing "
    "in the code says they were meant to be a pair.",
    [
        _ex(
            "either-or",
            i + 1,
            f'Put {value} in {name}. Print "{yes}" if {name} {cond_text}, '
            f'and "{no}" if it does not.',
            "if_else_print",
            name=name,
            value=value,
            cond=cond,
            yes=yes,
            no=no,
        )
        for i, (name, value, cond, cond_text, yes, no) in enumerate(_EITHER)
    ],
)


# ── 17. Which is bigger ──────────────────────────────────────

_BIGGER = (
    ("a", 6, "b", 9),
    ("a", 14, "b", 3),
    ("left", 25, "right", 25),
    ("first", 100, "second", 99),
    ("x", 7, "y", 70),
    ("home", 2, "away", 1),
    ("a", 0, "b", 5),
    ("cost", 45, "budget", 40),
    ("north", 88, "south", 91),
    ("a", 12, "b", 12),
    ("high", 300, "low", 30),
    ("start", 17, "finish", 4),
)

_P17 = _page(
    "bigger",
    17,
    "Which is bigger",
    "Comparing two values and keeping one of them.",
    "Two of these are a tie, and what your code does then is a decision you "
    "are making whether you notice or not. Both branches give the same "
    "answer here, which is exactly why it is easy to write the comparison "
    "the wrong way round and never find out.",
    [
        _ex(
            "bigger",
            i + 1,
            f"Put {v1} in {n1} and {v2} in {n2}. Print whichever of the two "
            f"is bigger.",
            "bigger_print",
            name1=n1,
            value1=v1,
            name2=n2,
            value2=v2,
        )
        for i, (n1, v1, n2, v2) in enumerate(_BIGGER)
    ],
)


# ── 18. Two conditions at once ───────────────────────────────

_BOTH = (
    ("n", 7, "n > 5", "n < 10", "and", "is over 5 and under 10", "yes", "no"),
    ("n", 12, "n > 5", "n < 10", "and", "is over 5 and under 10", "yes", "no"),
    ("age", 30, "age >= 18", "age < 65", "and", "is 18 or more and under 65", "working age", "not working age"),
    ("age", 70, "age >= 18", "age < 65", "and", "is 18 or more and under 65", "working age", "not working age"),
    ("n", 4, "n == 0", "n > 100", "or", "is 0 or over 100", "extreme", "ordinary"),
    ("n", 0, "n == 0", "n > 100", "or", "is 0 or over 100", "extreme", "ordinary"),
    ("temp", 35, "temp < 0", "temp > 30", "or", "is below 0 or above 30", "uncomfortable", "fine"),
    ("temp", 18, "temp < 0", "temp > 30", "or", "is below 0 or above 30", "uncomfortable", "fine"),
    ("n", 15, "n % 3 == 0", "n % 5 == 0", "and", "divides by both 3 and 5", "fizzbuzz", "neither"),
    ("n", 9, "n % 3 == 0", "n % 5 == 0", "and", "divides by both 3 and 5", "fizzbuzz", "neither"),
    ("stock", 0, "stock <= 0", "stock > 500", "or", "is 0 or under, or over 500", "check it", "carry on"),
    ("score", 55, "score >= 50", "score <= 70", "and", "is between 50 and 70", "middling", "not middling"),
)

_P18 = _page(
    "both-conditions",
    18,
    "Two conditions at once",
    "Joining two tests into one with and, or or.",
    "And needs both to hold; or needs at least one. The trap is reading them "
    "the way English uses them — \"numbers over 5 and under 10\" is one range "
    "in English and two conditions joined by and in code, while \"over 100 or "
    "exactly 0\" is two separate cases. Say which you mean out loud before "
    "you type it.",
    [
        _ex(
            "both-conditions",
            i + 1,
            f'Put {value} in {name}. Print "{yes}" when {name} {cond_text}, '
            f'and "{no}" otherwise.',
            "and_or_print",
            name=name,
            value=value,
            left=left,
            op=op,
            right=right,
            yes=yes,
            no=no,
        )
        for i, (name, value, left, right, op, cond_text, yes, no) in enumerate(_BOTH)
    ],
)


# ── 19. Looping until you stop ───────────────────────────────

_WHILE = (
    (1, 5, "i", "the number"),
    (1, 10, "i", "the number"),
    (3, 7, "i", "the number"),
    (1, 6, "i * 2", "the number doubled"),
    (0, 4, "i", "the number"),
    (1, 8, "i * i", "the number times itself"),
    (10, 15, "i", "the number"),
    (1, 5, "i * 10", "the number times 10"),
    (2, 9, "i + 100", "the number plus 100"),
    (1, 12, "i * 3", "the number times 3"),
    (5, 11, "i - 5", "the number minus 5"),
    (1, 7, "i % 3", "what is left over when the number is divided by 3"),
)

_P19 = _page(
    "while-loop",
    19,
    "Looping until you stop",
    "A while loop, where moving the counter on is your job.",
    "A for loop moves its counter for you. A while loop does not, so the "
    "three parts — start it, test it, move it — are three separate lines you "
    "have to remember. Forget the third one and it runs for ever, which is "
    "the first infinite loop nearly everyone writes.",
    [
        _ex(
            "while-loop",
            i + 1,
            f"Using a while loop rather than a for loop, print {described} "
            f"for every number from {lo} to {hi}.",
            "while_count",
            lo=lo,
            hi=hi,
            expr=expr,
        )
        for i, (lo, hi, expr, described) in enumerate(_WHILE)
    ],
)


# ── 20. Totting up with while ────────────────────────────────

_WHILE_SUM = (
    (1, 10, "i", "each number"),
    (1, 5, "i", "each number"),
    (1, 20, "i", "each number"),
    (1, 6, "i * i", "each number times itself"),
    (1, 9, "i * 2", "each number doubled"),
    (4, 12, "i", "each number"),
    (1, 7, "i * 10", "each number times 10"),
    (1, 15, "i + 1", "each number plus 1"),
    (2, 8, "i * 3", "each number times 3"),
    (1, 30, "i", "each number"),
    (5, 10, "i * i", "each number times itself"),
    (1, 11, "i % 4", "the remainder of each number divided by 4"),
)

_P20 = _page(
    "while-total",
    20,
    "Totting up with while",
    "Two things changing at once: the counter and the total.",
    "The counter and the total both live outside the loop and both change "
    "inside it, and they change for different reasons. Getting the increment "
    "inside the same block as the addition is the whole exercise — put it in "
    "the wrong place and you either never finish or only count once.",
    [
        _ex(
            "while-total",
            i + 1,
            f"Using a while loop, add up {described} from {lo} to {hi} and "
            f"print the total.",
            "while_sum",
            lo=lo,
            hi=hi,
            expr=expr,
        )
        for i, (lo, hi, expr, described) in enumerate(_WHILE_SUM)
    ],
)


# ── 21. A list of things ─────────────────────────────────────

_LIST_LOOP = (
    ([3, 5, 8], "n", "each one"),
    ([1, 2, 3, 4], "n", "each one"),
    ([10, 20, 30], "n", "each one"),
    ([4, 7, 1], "n * 2", "each one doubled"),
    ([5, 15, 25], "n + 1", "each one plus 1"),
    ([2, 4, 6, 8], "n * n", "each one times itself"),
    ([100, 200], "n - 50", "each one minus 50"),
    ([9, 3, 7, 1], "n * 10", "each one times 10"),
    ([12, 18], "n % 5", "the remainder of each one divided by 5"),
    ([6], "n", "each one"),
    ([11, 22, 33, 44], "n + n", "each one added to itself"),
    ([7, 14, 21], "n - 7", "each one minus 7"),
)

_P21 = _page(
    "lists",
    21,
    "A list of things",
    "Holding several values in one name, and visiting each.",
    "Up to now a variable has held one value. A list holds as many as you "
    "like, and the loop over it does not count — it hands you the items "
    "themselves, one at a time. Notice that there is no i anywhere: you "
    "asked for the things, not for their positions.",
    [
        _ex(
            "lists",
            i + 1,
            f"Put the numbers {', '.join(str(n) for n in items)} in a list, "
            f"then print {described}.",
            "list_loop",
            items=items,
            expr=expr,
        )
        for i, (items, expr, described) in enumerate(_LIST_LOOP)
    ],
)


# ── 22. Adding a list up ─────────────────────────────────────

_LIST_SUM = (
    [3, 5, 8],
    [1, 2, 3, 4, 5],
    [10, 20, 30],
    [7],
    [100, 250, 300],
    [2, 4, 6, 8, 10],
    [15, 15, 15],
    [1, 1, 2, 3, 5, 8],
    [40, 60],
    [9, 9, 9, 9],
    [12, 8, 30, 50],
    [11, 22, 33, 44, 55],
)

_P22 = _page(
    "list-total",
    22,
    "Adding a list up",
    "The running total again, over a list instead of a range.",
    "Exactly the pattern from page 8, with the loop pointed at a list. That "
    "is the point of the page: the shape of the answer does not change when "
    "the thing you are looping over changes, and noticing that saves you "
    "learning it twice.",
    [
        _ex(
            "list-total",
            i + 1,
            f"Put the numbers {', '.join(str(n) for n in items)} in a list, "
            f"add them all up, and print the total.",
            "list_sum",
            items=items,
        )
        for i, items in enumerate(_LIST_SUM)
    ],
)


# ── 23. Reaching into a list ─────────────────────────────────

_LIST_INDEX = (
    ([10, 20, 30], [0]),
    ([10, 20, 30], [2]),
    ([5, 6, 7, 8], [0, 3]),
    ([1, 2, 3, 4, 5], [2]),
    ([9, 8, 7], [1, 0]),
    ([100, 200, 300, 400], [3, 0]),
    ([4, 5], [1]),
    ([11, 22, 33, 44, 55], [0, 2, 4]),
    ([2, 4, 8, 16], [2]),
    ([7, 14, 21, 28], [3, 1]),
    ([1, 3, 5, 7, 9], [4]),
    ([6, 12, 18], [1, 1]),
)

_P23 = _page(
    "list-index",
    23,
    "Reaching into a list",
    "Getting one item by its position.",
    "Positions start at 0, so the first item is at 0 and the last one is at "
    "one less than the length. Every off-by-one bug you will ever write comes "
    "from this sentence, and a page of it is cheaper than finding out in "
    "anger later.",
    [
        _ex(
            "list-index",
            i + 1,
            f"Put the numbers {', '.join(str(n) for n in items)} in a list. "
            + (
                f"Print the item at position {picks[0]}."
                if len(picks) == 1
                else "Print the items at positions "
                + ", ".join(str(k) for k in picks)
                + ", in that order."
            ),
            "list_index",
            items=items,
            indexes=picks,
        )
        for i, (items, picks) in enumerate(_LIST_INDEX)
    ],
)


# ── 24. Only the ones that qualify ───────────────────────────

_LIST_FILTER = (
    ([3, 8, 12, 7], "n > 5", "are more than 5"),
    ([1, 2, 3, 4, 5, 6], "n % 2 == 0", "divide exactly by 2"),
    ([10, 15, 20, 25], "n % 10 == 0", "divide exactly by 10"),
    ([4, 9, 16, 25, 36], "n > 15", "are more than 15"),
    ([2, 5, 8, 11], "n % 2 == 1", "are odd"),
    ([100, 50, 200, 25], "n >= 100", "are 100 or more"),
    ([7, 14, 21, 28, 35], "n % 14 == 0", "divide exactly by 14"),
    ([1, 3, 5, 7], "n > 100", "are more than 100"),
    ([12, 18, 24, 30], "n % 4 == 0", "divide exactly by 4"),
    ([6, 7, 8, 9, 10], "n < 8", "are less than 8"),
    ([33, 44, 55, 66], "n % 11 == 0", "divide exactly by 11"),
    ([2, 4, 6, 8, 10, 12], "n > 4", "are more than 4"),
)

_P24 = _page(
    "list-filter",
    24,
    "Only the ones that qualify",
    "A decision inside a loop over a list.",
    "One of these prints nothing, because nothing in the list qualifies. "
    "That is not a broken program — a filter that matches nothing is a "
    "perfectly good filter, and code that assumes there will always be at "
    "least one result is how a crash gets written.",
    [
        _ex(
            "list-filter",
            i + 1,
            f"Put the numbers {', '.join(str(n) for n in items)} in a list. "
            f"Print only the ones that {described}.",
            "list_filter",
            items=items,
            cond=cond,
        )
        for i, (items, cond, described) in enumerate(_LIST_FILTER)
    ],
)


# ── 25. Building a list as you go ────────────────────────────

_LIST_BUILD = (
    (1, 5, "i", "the number"),
    (1, 4, "i * 2", "the number doubled"),
    (1, 6, "i * i", "the number times itself"),
    (2, 6, "i + 10", "the number plus 10"),
    (1, 3, "i * 100", "the number times 100"),
    (5, 9, "i", "the number"),
    (1, 7, "i * 3", "the number times 3"),
    (0, 4, "i + 1", "the number plus 1"),
    (1, 5, "i * i * i", "the number cubed"),
    (10, 14, "i - 10", "the number minus 10"),
    (1, 8, "i % 3", "the remainder of the number divided by 3"),
    (3, 8, "i * 5", "the number times 5"),
)

_P25 = _page(
    "list-build",
    25,
    "Building a list as you go",
    "Starting with an empty list and adding to it.",
    "Two loops: one to fill the list, one to read it back. You could print "
    "inside the first loop and get the same output, and the reason not to is "
    "that once the list exists you can do anything with it — sort it, count "
    "it, pass it somewhere — instead of only being able to have printed it.",
    [
        _ex(
            "list-build",
            i + 1,
            f"Start with an empty list. Loop from {lo} to {hi}, adding "
            f"{described} to the list each time. Then print every item in it.",
            "list_build",
            lo=lo,
            hi=hi,
            expr=expr,
        )
        for i, (lo, hi, expr, described) in enumerate(_LIST_BUILD)
    ],
)


# ── 26. The biggest one ──────────────────────────────────────

_LIST_MAX = (
    [3, 9, 4],
    [10, 2, 8, 5],
    [7],
    [1, 2, 3, 4, 5],
    [5, 4, 3, 2, 1],
    [100, 99, 101],
    [12, 12, 12],
    [0, 45, 3, 45],
    [88, 12, 90, 33, 2],
    [6, 6, 7],
    [250, 40, 60, 240],
    [1, 100, 10, 1000, 11],
)

_P26 = _page(
    "list-max",
    26,
    "The biggest one",
    "Carrying the best answer so far through a loop.",
    "Start with the first item as the best, then replace it whenever you "
    "meet something better. Starting from zero instead looks like it works "
    "until the list is all negative numbers, which is the kind of bug that "
    "sits in a program for years.",
    [
        _ex(
            "list-max",
            i + 1,
            f"Put the numbers {', '.join(str(n) for n in items)} in a list. "
            f"Work out the biggest one with a loop and print it.",
            "list_max",
            items=items,
        )
        for i, items in enumerate(_LIST_MAX)
    ],
)


# ── 27. Naming a piece of work ───────────────────────────────

_FUNC_PRINT = (
    ("greet", "hello", 1),
    ("greet", "hello", 3),
    ("shout", "STOP", 2),
    ("sign", "this way", 4),
    ("banner", "welcome", 1),
    ("tick", "ok", 5),
    ("line", "----", 3),
    ("warn", "careful", 2),
    ("done", "finished", 1),
    ("beat", "thump", 6),
    ("nudge", "your turn", 2),
    ("echo", "again", 4),
)

_P27 = _page(
    "functions",
    27,
    "Naming a piece of work",
    "Writing a function, and calling it.",
    "Defining a function runs nothing. It gives a name to some lines, and "
    "they only happen when something calls that name — which is why a "
    "program with a definition and no call prints nothing at all and looks "
    "broken.",
    [
        _ex(
            "functions",
            i + 1,
            f'Write a function called {name} that prints "{text}". '
            f"Call it {times} time{'s' if times != 1 else ''}.",
            "func_print",
            name=name,
            text=text,
            times=times,
        )
        for i, (name, text, times) in enumerate(_FUNC_PRINT)
    ],
)


# ── 28. Functions that take a value ──────────────────────────

_FUNC_ARG = (
    ("twice", "n", "n * 2", "the number doubled", [3, 5]),
    ("addten", "n", "n + 10", "the number plus 10", [1, 90]),
    ("square", "n", "n * n", "the number times itself", [4, 7, 9]),
    ("half", "n", "n % 2", "the remainder when divided by 2", [8, 9]),
    ("triple", "n", "n * 3", "the number times 3", [2, 11, 100]),
    ("less", "n", "n - 1", "the number minus 1", [10, 1]),
    ("hundreds", "n", "n * 100", "the number times 100", [3, 7]),
    ("nextodd", "n", "n * 2 + 1", "twice the number plus 1", [0, 4, 10]),
    ("shrink", "n", "n - 5", "the number minus 5", [50, 5]),
    ("cube", "n", "n * n * n", "the number cubed", [2, 3, 4]),
    ("tens", "n", "n % 10", "the last digit", [47, 130]),
    ("both", "n", "n + n", "the number added to itself", [6, 21]),
)

_P28 = _page(
    "function-args",
    28,
    "Functions that take a value",
    "A function that does its job on whatever it is handed.",
    "The name in the brackets stands for whatever the caller passes, and it "
    "only exists inside the function. That is the whole reason a function is "
    "worth writing: one set of lines, working on a different value each time "
    "you call it.",
    [
        _ex(
            "function-args",
            i + 1,
            f"Write a function called {name} that takes a number and prints "
            f"{described}. Call it with "
            + ", then ".join(str(v) for v in calls)
            + ".",
            "func_arg",
            name=name,
            param=param,
            expr=expr,
            calls=calls,
        )
        for i, (name, param, expr, described, calls) in enumerate(_FUNC_ARG)
    ],
)


# ── 29. Functions that hand something back ───────────────────

_FUNC_RETURN = (
    ("twice", "n", "n * 2", "the number doubled", [3, 5]),
    ("square", "n", "n * n", "the number times itself", [4, 6]),
    ("addone", "n", "n + 1", "the number plus 1", [9, 99]),
    ("tenx", "n", "n * 10", "the number times 10", [1, 7, 12]),
    ("takeaway", "n", "n - 3", "the number minus 3", [10, 3]),
    ("cube", "n", "n * n * n", "the number cubed", [2, 5]),
    ("rest", "n", "n % 7", "the remainder when divided by 7", [20, 49]),
    ("plusself", "n", "n + n", "the number added to itself", [8, 40]),
    ("fivex", "n", "n * 5", "the number times 5", [3, 11, 20]),
    ("backone", "n", "n - 1", "the number minus 1", [1, 1000]),
    ("squareplus", "n", "n * n + 1", "the number squared, plus 1", [3, 7]),
    ("hundredless", "n", "100 - n", "100 minus the number", [40, 99]),
)

_P29 = _page(
    "function-returns",
    29,
    "Functions that hand something back",
    "Returning a value instead of printing it.",
    "A function that prints has made its mind up about what happens to the "
    "answer. A function that returns hands it back and lets the caller "
    "decide, which is why almost everything you use is written that way. Note "
    "that the printing has moved out to where the call is.",
    [
        _ex(
            "function-returns",
            i + 1,
            f"Write a function called {name} that takes a number and returns "
            f"{described}. Print the result of calling it with "
            + ", then ".join(str(v) for v in calls)
            + ".",
            "func_return",
            name=name,
            param=param,
            expr=expr,
            calls=calls,
        )
        for i, (name, param, expr, described, calls) in enumerate(_FUNC_RETURN)
    ],
)


# ── 30. How long is it ───────────────────────────────────────

_WORDS = (
    "hello",
    "a",
    "workbook",
    "typing",
    "characters",
    "no",
    "programming",
    "keyboard",
    "yes",
    "repetition",
    "code",
    "practice",
)

_P30 = _page(
    "string-length",
    30,
    "How long is it",
    "Asking a string how many characters it holds.",
    "A string knows its own length and you never count it yourself. Worth "
    "noticing: the length is a count of characters, so the last position is "
    "one less than it — the same off-by-one as page 23, wearing different "
    "clothes.",
    [
        _ex(
            "string-length",
            i + 1,
            f'Print how many characters are in the word "{word}".',
            "str_length",
            word=word,
        )
        for i, word in enumerate(_WORDS)
    ],
)


# ── 31. One character at a time ──────────────────────────────

_LOOP_WORDS = (
    "hi",
    "cat",
    "code",
    "loop",
    "typing",
    "a",
    "keys",
    "string",
    "yes",
    "letters",
    "work",
    "done",
)

_P31 = _page(
    "string-loop",
    31,
    "One character at a time",
    "Looping over a string the way you loop over a list.",
    "A string behaves like a list of characters when you loop over it, which "
    "is the same loop you already know pointed at something new. That is "
    "worth a page because it is the moment loops stop being about numbers.",
    [
        _ex(
            "string-loop",
            i + 1,
            f'Print each character of the word "{word}" on its own line.',
            "str_loop",
            word=word,
        )
        for i, word in enumerate(_LOOP_WORDS)
    ],
)


# ── 32. Asking a string to do something ──────────────────────

_UPPER_WORDS = (
    "hello",
    "shout",
    "quiet",
    "loud",
    "code coach",
    "workbook",
    "yes",
    "keyboard",
    "practice makes it easy",
    "done",
    "one more",
    "finished",
)

_P32 = _page(
    "string-upper",
    32,
    "Asking a string to do something",
    "Calling a method on a value.",
    "The string is not changed — it hands back a new one in capitals and the "
    "original is exactly as it was. Strings work that way everywhere, and "
    "expecting the change to stick is a bug people write once and remember "
    "for ever.",
    [
        _ex(
            "string-upper",
            i + 1,
            f'Print the word "{word}" in capital letters.',
            "str_upper",
            word=word,
        )
        for i, word in enumerate(_UPPER_WORDS)
    ],
)


MORE_PAGES: tuple[Page, ...] = (
    _P12,
    _P13,
    _P14,
    _P15,
    _P16,
    _P17,
    _P18,
    _P19,
    _P20,
    _P21,
    _P22,
    _P23,
    _P24,
    _P25,
    _P26,
    _P27,
    _P28,
    _P29,
    _P30,
    _P31,
    _P32,
)
