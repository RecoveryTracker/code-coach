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

from code_coach.kata.predict_js import JS_PUZZLES
from code_coach.kata.predict_dart import DART_PUZZLES
from code_coach.kata.predict_js2 import JS_PUZZLES_2
from code_coach.kata.puzzle import Puzzle, _p




# ── Mutation and aliasing ────────────────────────────────────

MUTATION: tuple[Puzzle, ...] = (
    _p(
        id="predict-default-list",
        level=4,
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
        level=3,
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
        level=1,
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
        level=2,
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
        id="predict-remove-while-looping",
        level=3,
        name="Removing as you go",
        family="Mutation",
        code=(
            "nums = [1, 2, 3, 4]\n"
            "for n in nums:\n"
            "    if n % 2 == 0:\n"
            "        nums.remove(n)\n"
            "print(nums)"
        ),
        expect="[1, 3]",
        why=(
            "The loop walks by position while the list is getting "
            "shorter underneath it. Removing 2 shifts everything left, "
            "so the next position holds 4 and 3 is stepped straight "
            "over — which is why 4 survives. Loop over a copy, or build "
            "a new list."
        ),
    ),
    _p(
        id="predict-append-extend",
        level=2,
        name="Append, and extend",
        family="Mutation",
        code=(
            "a = [1]\n"
            "a.append([2, 3])\n"
            "b = [1]\n"
            "b.extend([2, 3])\n"
            "print(a, b)"
        ),
        expect="[1, [2, 3]] [1, 2, 3]",
        why=(
            "`append` adds one thing, whatever it is, so a list goes in "
            "as a single nested item. `extend` adds each item of what it "
            "was given. Both return None, so neither can be chained."
        ),
    ),
    _p(
        id="predict-sort-returns",
        level=2,
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
        level=3,
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
        level=1,
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
        level=2,
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
        id="predict-all-of-nothing",
        level=3,
        name="All of nothing",
        family="Truthiness",
        code="print(all([]), any([]), sum([]), max([1], default=0))",
        expect="True False 0 1",
        why=(
            "`all` of an empty list is True, because there is nothing in "
            "it that is false. `any` is False for the mirror reason. It "
            "reads as a paradox and falls straight out of the "
            "definitions — and it is why an `all(...)` guard passes "
            "cheerfully when the thing it was guarding turned out to be "
            "empty."
        ),
    ),
    _p(
        id="predict-dict-get",
        level=2,
        name="get, and the key that is there",
        family="Truthiness",
        code=(
            'd = {"a": None}\n'
            'print(d.get("a", "fallback"), d.get("b", "fallback"), "a" in d)'
        ),
        expect="None fallback True",
        why=(
            "The default only applies when the key is missing, not when "
            "the value is falsy — a key holding None gives you None. To "
            "ask whether a key exists, use `in`; `get` cannot tell you, "
            "because None is also a value something might legitimately "
            "hold."
        ),
    ),
    _p(
        id="predict-chained",
        level=3,
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
        level=4,
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
        level=3,
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
        level=2,
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
        level=2,
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
        id="predict-print-repr",
        level=2,
        name="Printed, and printed inside something",
        family="Sequences",
        code=(
            'items = ["a", 1, None]\n'
            "print(items)\n"
            "print(*items)"
        ),
        expect="['a', 1, None]\na 1 None",
        why=(
            "Printing a list shows repr for the things inside it, which "
            "is why the string keeps its quotes and None shows as None. "
            "Printing the items themselves uses str, which is the plain "
            "form. The same value has two spellings and a container "
            "always picks the first."
        ),
    ),
    _p(
        id="predict-in-a-dict",
        level=1,
        name="What `in` looks at",
        family="Sequences",
        code=(
            'd = {"a": 1, "b": 2}\n'
            'print("a" in d, 1 in d, 1 in d.values())'
        ),
        expect="True False True",
        why=(
            "`in` on a dict asks about keys, never values, which is why "
            "the middle one is False even though 1 is sitting right "
            "there. Looping over a dict gives you keys for the same "
            "reason. Ask `.values()` when you mean values."
        ),
    ),
    _p(
        id="predict-dict-order",
        level=3,
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


# ── Numbers ──────────────────────────────────────────────────

NUMBERS: tuple[Puzzle, ...] = (
    _p(
        id="predict-negative-division",
        level=3,
        name="Dividing a negative",
        family="Numbers",
        code="print(-7 // 2, -7 % 2, int(-7 / 2), divmod(-7, 2))",
        expect="-4 1 -3 (-4, 1)",
        why=(
            "Floor division rounds towards negative infinity, so -7 // 2 "
            "is -4 rather than -3, and the remainder comes back positive "
            "to match. int() on the true division rounds towards zero "
            "instead, which is where the two disagree. Every language "
            "picks one of these and Python's choice is the one that keeps "
            "`a == (a // b) * b + a % b` true."
        ),
    ),
    _p(
        id="predict-rounding",
        level=3,
        name="Rounding a half",
        family="Numbers",
        code="print(round(0.5), round(1.5), round(2.5), round(-0.5))",
        expect="0 2 2 0",
        why=(
            "Python rounds a half to the nearest even number rather than "
            "always up, so 0.5 and 2.5 both land on an even one. It is "
            "there so that rounding a long column of numbers does not "
            "drift upwards. Use Decimal when you need the school rule."
        ),
    ),
    _p(
        id="predict-float-sum",
        level=2,
        name="A tenth plus two tenths",
        family="Numbers",
        code="print(0.1 + 0.2 == 0.3, 0.1 + 0.2)",
        expect="False 0.30000000000000004",
        why=(
            "Neither 0.1 nor 0.2 can be written exactly in binary, so the "
            "sum is very slightly off and the comparison fails. This is "
            "not a Python quirk — it is how floating point works "
            "everywhere. Compare with math.isclose, or use Decimal for "
            "money."
        ),
    ),
)


# ── Errors and flow ──────────────────────────────────────────

FLOW: tuple[Puzzle, ...] = (
    _p(
        id="predict-finally-return",
        level=3,
        name="The finally that wins",
        family="Errors",
        code=(
            "def pick():\n"
            "    try:\n"
            '        return "try"\n'
            "    finally:\n"
            '        return "finally"\n'
            "\n"
            "print(pick())"
        ),
        expect="finally",
        why=(
            "A return in a finally replaces whatever the try was already "
            "returning, and would swallow an exception on its way past "
            "too. It is almost never what anyone means, which is why "
            "linters warn about it."
        ),
    ),
    _p(
        id="predict-except-order",
        level=2,
        name="Which except catches it",
        family="Errors",
        code=(
            "try:\n"
            '    int("x")\n'
            "except Exception:\n"
            '    print("broad")\n'
            "except ValueError:\n"
            '    print("narrow")'
        ),
        expect="broad",
        why=(
            "The arms are tried in order and the first one that matches "
            "wins. A broad except written first catches everything, and "
            "the specific arm below it can never run. Narrowest first."
        ),
    ),
    _p(
        id="predict-tuple-of-list",
        level=4,
        name="The one that fails and works",
        family="Errors",
        code=(
            "t = ([1], 2)\n"
            "try:\n"
            "    t[0] += [3]\n"
            "except TypeError:\n"
            '    print("TypeError")\n'
            "print(t)"
        ),
        expect="TypeError\n([1, 3], 2)",
        why=(
            "`+=` on a list extends it in place and then assigns the "
            "result back — and assigning into a tuple is the part that "
            "fails. The extension has already happened by then, so the "
            "list really did change and the error is real. Both halves "
            "of that sentence are true at once, which is why this one is "
            "famous."
        ),
    ),
    _p(
        id="predict-shadowed-builtin",
        level=2,
        name="The name you took",
        family="Errors",
        code=(
            "list = [1, 2]\n"
            "try:\n"
            "    made = list((3, 4))\n"
            "except TypeError:\n"
            '    made = "could not"\n'
            "print(made, len(list))"
        ),
        expect="could not 2",
        why=(
            "Assigning to `list` replaced the builtin for the rest of "
            "the scope, so calling it is calling a list, which is not "
            "callable. The same goes for `dict`, `sum`, `id` and `type`, "
            "and the error arrives a long way from the line that caused "
            "it."
        ),
    ),
)


PUZZLES: tuple[Puzzle, ...] = (
    MUTATION + TRUTH + SEQUENCES + NUMBERS + FLOW + JS_PUZZLES
    + JS_PUZZLES_2 + DART_PUZZLES
)


def _offered() -> tuple[Puzzle, ...]:
    """PUZZLES, less the Dart ones on a machine without Dart."""
    from code_coach.engine import dart_available

    if dart_available():
        return PUZZLES
    return tuple(p for p in PUZZLES if p.language != "dart")


def puzzles(family: str | None = None) -> tuple[Puzzle, ...]:
    """Least surprising first, stable within a level."""
    ordered = tuple(sorted(_offered(), key=lambda p: p.level))
    if family is None:
        return ordered
    return tuple(p for p in ordered if p.family == family)


def puzzle(puzzle_id: str) -> Puzzle | None:
    return next((p for p in PUZZLES if p.id == puzzle_id), None)


def predict_families() -> tuple[str, ...]:
    """From the file order, not the sorted one.

    Sorting by level interleaves the families, so reading the families
    off the sorted list would start with whichever family happened to
    hold the least surprising puzzle.
    """
    seen: list[str] = []
    for p in _offered():
        if p.family not in seen:
            seen.append(p.family)
    return tuple(seen)


def language_of(family: str) -> str:
    """Which language a family's snippets are in.

    A family never mixes them: reading JavaScript in a list you opened
    for Python is a worse surprise than any of the puzzles.
    """
    for p in PUZZLES:
        if p.family == family:
            return p.language
    return "python"
