"""Predict the output: read the code, say what it prints.

The katas ask you to write a function. This asks the other question, and
it is the one that finds out whether you know what the language actually
does rather than what you meant it to do. Every snippet here is short,
correct Python, and does something most people get wrong the first time.

Codewars and freeCodeCamp do not have this, and neither could easily:
the payoff is being wrong and then watching it happen, and that needs a
tracer. This app has one, so a wrong guess can be followed by stepping
through the same snippet and seeing the shared list, the loop variable
that outlived its loop, the generator that was already empty.

The expected output is written out by hand and a test runs each snippet
to check Python agrees. That is the opposite way round from the katas —
there the reference computes the answer and a person checks it; here the
answer is whatever Python does, and the person's copy is what catches a
snippet that has stopped demonstrating what its explanation claims.

That check has already paid for itself. A puzzle about small-integer
caching was written from memory as `a = 256; b = 256; c = 257; d = 257`
printing `True False`. Python prints `True True`: two constants in one
code object are folded into one value, so the snippet demonstrated
nothing except that the author had not run it. It is not in the file.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Puzzle:
    """A snippet, what it prints, and why that surprises people."""

    id: str
    name: str
    family: str
    #: The whole program. Short enough to hold in your head at once.
    code: str
    #: Exactly what it prints, typed out by a person.
    expect: str
    #: What is going on, shown after you have answered either way. A
    #: wrong guess with no explanation teaches only that you were wrong.
    why: str


def _p(**kw) -> Puzzle:
    return Puzzle(**kw)


# ── Mutation and aliasing ────────────────────────────────────

MUTATION: tuple[Puzzle, ...] = (
    _p(
        id="predict-default-list",
        name="The basket that remembers",
        family="Mutation",
        code=(
            "def add(item, basket=[]):\n"
            "    basket.append(item)\n"
            "    return basket\n"
            "\n"
            "print(add(1))\n"
            "print(add(2))"
        ),
        expect="[1]\n[1, 2]",
        why=(
            "The default is built once, when the def is executed, not "
            "once per call. Every call that does not pass a basket gets "
            "the same list — the one made when the function was defined. "
            "The fix is a default of None and a new list inside."
        ),
    ),
    _p(
        id="predict-repeated-row",
        name="Three rows, or one row three times",
        family="Mutation",
        code=(
            "grid = [[0] * 2] * 3\n"
            "grid[0][0] = 9\n"
            "print(grid)"
        ),
        expect="[[9, 0], [9, 0], [9, 0]]",
        why=(
            "The inner multiplication makes one list. The outer one "
            "makes three references to that same list, not three lists, "
            "so writing through any of them is visible through all "
            "three. A comprehension builds a new row each time."
        ),
    ),
    _p(
        id="predict-alias",
        name="Two names, one list",
        family="Mutation",
        code=(
            "a = [1, 2]\n"
            "b = a\n"
            "b.append(3)\n"
            "print(a, b)"
        ),
        expect="[1, 2, 3] [1, 2, 3]",
        why=(
            "Assignment never copies. `b = a` gives the same list a "
            "second name, so appending through one is appending through "
            "both. `b = a[:]` or `list(a)` is a copy."
        ),
    ),
    _p(
        id="predict-string-copy",
        name="The same two names, with text",
        family="Mutation",
        code=(
            's = "abc"\n'
            "t = s\n"
            's += "d"\n'
            "print(s, t)"
        ),
        expect="abcd abc",
        why=(
            "The same assignment as the list, and the opposite result, "
            "because a string cannot be changed. `s += 'd'` makes a new "
            "string and points `s` at it, leaving `t` where it was. "
            "Which of the two behaviours you get depends entirely on "
            "whether the type can be modified in place."
        ),
    ),
    _p(
        id="predict-sort-returns",
        name="What sort hands back",
        family="Mutation",
        code=(
            "nums = [3, 1, 2]\n"
            "print(nums.sort(), sorted(nums))"
        ),
        expect="None [1, 2, 3]",
        why=(
            "`sort` changes the list and returns None, which is the "
            "convention for every method that modifies in place. "
            "`sorted` leaves the original alone and returns a new list. "
            "Writing `nums = nums.sort()` throws the list away."
        ),
    ),
)


# ── Truthiness and defaults ──────────────────────────────────

TRUTH: tuple[Puzzle, ...] = (
    _p(
        id="predict-or-default",
        name="The empty list that vanishes",
        family="Truthiness",
        code=(
            "def show(items=None):\n"
            '    items = items or ["nothing"]\n'
            "    return items\n"
            "\n"
            "print(show([]), show([1]))"
        ),
        expect="['nothing'] [1]",
        why=(
            "`or` falls through on anything falsy, and an empty list is "
            "falsy — so a caller who passed an empty list on purpose "
            "gets the default instead. `if items is None` asks the "
            "question that was meant."
        ),
    ),
    _p(
        id="predict-is-equal",
        name="Equal, and not the same",
        family="Truthiness",
        code=(
            "a = [1, 2]\n"
            "b = [1, 2]\n"
            "print(a == b, a is b)"
        ),
        expect="True False",
        why=(
            "`==` asks whether they hold the same values and `is` asks "
            "whether they are the same object. Two lists written out "
            "separately are two objects. `is` is for None and for "
            "identity, never for comparing values."
        ),
    ),
    _p(
        id="predict-bool-is-int",
        name="True, counted",
        family="Truthiness",
        code=(
            "flags = [True, False, True, True]\n"
            "print(sum(flags), True + True, isinstance(True, int))"
        ),
        expect="3 2 True",
        why=(
            "bool is a subclass of int, and True is 1. Summing booleans "
            "counts them, which is occasionally useful and occasionally "
            "the reason a function returning 1 passes a test that wanted "
            "True."
        ),
    ),
    _p(
        id="predict-chained",
        name="Comparisons in a chain",
        family="Truthiness",
        code="print(1 < 2 < 3, (1 < 2) < 3, 2 < 3 > 1)",
        expect="True True True",
        why=(
            "The first is a chain and means `1 < 2 and 2 < 3`. The "
            "second is not: the brackets make it `True < 3`, and True is "
            "1, so it asks whether 1 is less than 3. They agree here by "
            "luck rather than by meaning the same thing."
        ),
    ),
)


# ── Sequences ────────────────────────────────────────────────

SEQUENCES: tuple[Puzzle, ...] = (
    _p(
        id="predict-late-binding",
        name="The loop variable that outlived the loop",
        family="Sequences",
        code=(
            "makers = [lambda: i for i in range(3)]\n"
            "print([m() for m in makers])"
        ),
        expect="[2, 2, 2]",
        why=(
            "Each lambda looks up `i` when it is called, not when it was "
            "made, and by then the loop has finished and left `i` at 2. "
            "`lambda i=i: i` captures the value at the time instead."
        ),
    ),
    _p(
        id="predict-generator-once",
        name="The generator that was already empty",
        family="Sequences",
        code=(
            "nums = (n for n in range(3))\n"
            "print(sum(nums), sum(nums))"
        ),
        expect="3 0",
        why=(
            "A generator is consumed as it is read. The first sum walks "
            "it to the end and the second finds nothing left, which is "
            "zero rather than an error. A list comprehension — square "
            "brackets — can be read as often as you like."
        ),
    ),
    _p(
        id="predict-one-tuple",
        name="The comma that makes a tuple",
        family="Sequences",
        code='print(type(("a")).__name__, type(("a",)).__name__, len(("a", )))',
        expect="str tuple 1",
        why=(
            "Brackets do not make a tuple; the comma does. `('a')` is "
            "just a bracketed string. This is why a one-item tuple is "
            "written with a trailing comma and why forgetting it turns a "
            "tuple into whatever was inside it."
        ),
    ),
    _p(
        id="predict-slice-past-end",
        name="Slicing past the end",
        family="Sequences",
        code=(
            "nums = [1, 2, 3]\n"
            "print(nums[1:99], nums[99:], nums[-1], nums[::-1])"
        ),
        expect="[2, 3] [] 3 [3, 2, 1]",
        why=(
            "A slice clamps to the ends and never raises, while an index "
            "past the end does. That difference is why a slice is the "
            "safe way to take the first n of something that might be "
            "shorter than n."
        ),
    ),
    _p(
        id="predict-dict-order",
        name="What order a dict comes back in",
        family="Sequences",
        code=(
            'd = {"b": 1, "a": 2}\n'
            'd["c"] = 3\n'
            'del d["b"]\n'
            'd["b"] = 4\n'
            "print(list(d))"
        ),
        expect="['a', 'c', 'b']",
        why=(
            "Since 3.7 a dict keeps the order things were first put in, "
            "not sorted order. Deleting a key and putting it back puts "
            "it at the end, because it is being inserted again."
        ),
    ),
)


PUZZLES: tuple[Puzzle, ...] = MUTATION + TRUTH + SEQUENCES


def puzzles(family: str | None = None) -> tuple[Puzzle, ...]:
    if family is None:
        return PUZZLES
    return tuple(p for p in PUZZLES if p.family == family)


def puzzle(puzzle_id: str) -> Puzzle | None:
    return next((p for p in PUZZLES if p.id == puzzle_id), None)


def predict_families() -> tuple[str, ...]:
    seen: list[str] = []
    for p in PUZZLES:
        if p.family not in seen:
            seen.append(p.family)
    return tuple(seen)
