"""Three more projects, where the answer is a shape rather than a value.

The first three were about rules interacting. These are about output
that has to look like something: a column that lines up, a running
total that refuses, an answer in the same notation it was asked in.

`format_sum` is freeCodeCamp's arithmetic formatter and is the hardest
thing in the kata set, not because any rule is difficult but because
there are seven of them and four are about spacing. It is also the only
kata whose answer contains newlines, which is worth meeting once: the
marker compares the whole string, so a column one space out is a
failure and looks like one.

`ledger` is the shape every bank and every inventory has underneath —
apply in order, refuse what would go below zero, and carry on rather
than stopping. Getting it wrong usually means refusing everything after
the first refusal, or letting the balance go negative on the entry that
was supposed to be refused.

`roman_add` is the two Roman katas joined up. Doing it by working in
numbers in the middle is the point: converting there and back is easier
than adding numerals directly, and noticing that is most of the lesson.
"""

from __future__ import annotations

from code_coach.kata import Kata


def _format_sum(problems: list) -> str:
    if not problems:
        return ""
    if len(problems) > 5:
        return "too many problems"
    tops, bottoms, dashes, answers = [], [], [], []
    for problem in problems:
        left, sign, right = problem.split()
        if sign not in ("+", "-"):
            return "operator must be + or -"
        if not (left.isdigit() and right.isdigit()):
            return "numbers must only contain digits"
        if len(left) > 4 or len(right) > 4:
            return "numbers cannot be more than four digits"
        width = max(len(left), len(right)) + 2
        tops.append(left.rjust(width))
        bottoms.append(sign + right.rjust(width - 1))
        dashes.append("-" * width)
        total = int(left) + int(right) if sign == "+" else int(left) - int(right)
        answers.append(str(total).rjust(width))
    return "\n".join(
        "    ".join(row) for row in (tops, bottoms, dashes, answers)
    )


def _ledger(entries: list) -> list:
    balance = 0
    out = []
    for label, amount in entries:
        if balance + amount < 0:
            out.append(f"{label}: refused")
            continue
        balance += amount
        out.append(f"{label}: {balance}")
    return out


def _roman_add(one: str, two: str) -> str:
    worth = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

    def read(text: str) -> int:
        total = 0
        for i, c in enumerate(text):
            here = worth[c]
            after = worth[text[i + 1]] if i + 1 < len(text) else 0
            total += -here if here < after else here
        return total

    table = (
        (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
        (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
        (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
    )
    n = read(one) + read(two)
    out = []
    for value, letters in table:
        while n >= value:
            out.append(letters)
            n -= value
    return "".join(out)


PROJECTS2: tuple[Kata, ...] = (
    Kata(
        id="format-sum",
        level=5,
        name="format_sum",
        brief=(
            "Lay the problems out in columns the way you would on paper: "
            "the first number, then the sign and the second number below "
            "it, then dashes, then the answer. Right-align them, with two "
            "spaces before the longest number and four spaces between "
            "columns. No problems gives an empty string. Refuse with "
            "'too many problems' past five, 'operator must be + or -', "
            "'numbers must only contain digits', or 'numbers cannot be "
            "more than four digits'."
        ),
        params=("problems",),
        family="Projects",
        example="format_sum(['1 + 1']) is '  1\\n+ 1\\n---\\n  2'",
        hint=(
            "Build four lists — tops, bottoms, dashes, answers — and join "
            "each into a line at the end. The width of a column is the "
            "longer number plus two, and every check has to happen before "
            "any of the laying out."
        ),
        cases=(
            (["3 + 855", "3801 - 2", "45 + 43", "123 + 49"],),
            (["1 + 1"],),
            ([],),
            (["1 + 2", "1 + 2", "1 + 2", "1 + 2", "1 + 2", "1 + 2"],),
            (["1 * 2"],),
            (["10 + a"],),
            (["12345 + 1"],),
            (["9 - 9"],),
            (["100 - 1000"],),
            (["5 + 5", "10 - 5"],),
        ),
        solve=_format_sum,
        checks=(
            ((([],)), ""),
            (((["1 + 1"],)), "  1\n+ 1\n---\n  2"),
            (((["9 - 9"],)), "  9\n- 9\n---\n  0"),
            (((["1 * 2"],)), "operator must be + or -"),
            (((["10 + a"],)), "numbers must only contain digits"),
            (((["12345 + 1"],)), "numbers cannot be more than four digits"),
            (((["1 + 2", "1 + 2", "1 + 2", "1 + 2", "1 + 2", "1 + 2"],)),
             "too many problems"),
        ),
    ),
    Kata(
        id="ledger",
        level=3,
        name="ledger",
        brief=(
            "Apply each entry in order and report the balance after it, "
            "as 'label: balance'. An entry that would take the balance "
            "below zero is refused — report 'label: refused', leave the "
            "balance alone, and carry on with the rest. Each entry is a "
            "pair of a label and an amount."
        ),
        params=("entries",),
        family="Projects",
        example='ledger([["in", 100], ["out", -30]]) is ["in: 100", "out: 70"]',
        hint=(
            "Test the balance you would end up with, not the one you have. "
            "And a refusal is not the end — the entries after it still "
            "apply."
        ),
        cases=(
            ([["in", 100], ["out", -30]],),
            ([],),
            ([["out", -1]],),
            ([["in", 0]],),
            ([["in", 5], ["out", -10]],),
            ([["in", 5], ["out", -5]],),
            ([["in", 1], ["in", 1], ["out", -3], ["in", 1]],),
            ([["only", -5]],),
            ([["a", 10], ["b", -10], ["c", -1]],),
            ([["in", 1000000]],),
        ),
        solve=_ledger,
        checks=(
            ((([],)), []),
            ((([["out", -1]],)), ["out: refused"]),
            ((([["in", 0]],)), ["in: 0"]),
            ((([["in", 5], ["out", -5]],)), ["in: 5", "out: 0"]),
            ((([["in", 1], ["in", 1], ["out", -3], ["in", 1]],)),
             ["in: 1", "in: 2", "out: refused", "in: 3"]),
        ),
    ),
    Kata(
        id="roman-add",
        level=3,
        name="roman_add",
        brief=(
            "Add two Roman numerals and answer in Roman. Four is IV and "
            "nine is IX, going in and coming out."
        ),
        params=("one", "two"),
        family="Projects",
        example="roman_add('IV', 'VI') is 'X'",
        hint=(
            "Do not try to add the numerals. Read both into numbers, add "
            "those, and write the total back out — noticing that is most "
            "of the exercise."
        ),
        cases=(
            ("I", "I"), ("IV", "VI"), ("MCMXCIV", "VI"), ("I", "MMM"),
            ("X", "X"), ("IX", "I"), ("L", "L"), ("III", "IV"),
            ("MMM", "CMXCIX"), ("V", "V"),
        ),
        solve=_roman_add,
        checks=(
            (("I", "I"), "II"),
            (("IV", "VI"), "X"),
            (("IX", "I"), "X"),
            (("L", "L"), "C"),
            (("MCMXCIV", "VI"), "MM"),
            (("MMM", "CMXCIX"), "MMMCMXCIX"),
        ),
    ),
)
