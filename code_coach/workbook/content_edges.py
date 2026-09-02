"""Intermediate pages 111-120: sharp edges, and the lazy half.

Three pages of Python behaving in ways that surprise people, then seven of
the features that make Python code look like Python.

The sharp edges are deliberately early in this block. They are not advanced;
they are the opposite — things a beginner meets by accident within a month
and then spends an evening on. Meeting them on purpose, in a page that shows
the surprise happening, costs twenty minutes and saves that evening.

Python only, same as 81-110.
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


def _list(items) -> str:
    return ", ".join(repr(n) for n in items)


def _words(items) -> str:
    return ", ".join(f'"{w}"' for w in items)


# ── 111. The default that is not fresh ───────────────────────

_MUTABLE = (
    [1, 2],
    [1, 2, 3],
    [5],
    [7, 8],
    [1, 1, 1],
    [9, 8, 7],
    [2, 4, 6, 8],
    [10, 20],
    [3],
    [1, 2, 3, 4],
    [100, 200],
    [6, 5, 4],
)

_P111 = _page(
    "mutable-default",
    111,
    "The default that is not fresh",
    "Why a list as a default argument is almost always a bug.",
    "The default is worked out once, when the function is defined, and the "
    "same list is reused by every call that does not pass one. So it keeps "
    "what the last call put in it. Run these and watch the list grow across "
    "calls that share nothing else — that is the surprise, and it is why the "
    "fix is to default to None and make the list inside.",
    "mutable_default",
    [
        (
            "Write a function taking an item and a second argument box "
            "defaulting to an empty list, which appends the item to box and "
            "returns box. Call it with "
            + ", then ".join(repr(v) for v in calls)
            + ", printing the result each time.",
            {"name": "collect", "calls": calls},
        )
        for calls in _MUTABLE
    ],
)


# ── 112. The same value, or the same thing ───────────────────

_IDENTITY = (
    ("[1, 2]", "[1, 2]", True, False),
    ("[1, 2]", "[1, 3]", False, False),
    ("256", "256", True, True),
    ("257", "257", True, True),
    ('"hello"', '"hello"', True, True),
    ("[]", "[]", True, False),
    ("(1, 2)", "(1, 2)", True, True),
    ("{}", "{}", True, False),
    ("[3]", "[3]", True, False),
    ("None", "None", True, True),
    ("[1, 2, 3]", "[1, 2, 3]", True, False),
    ("5", "5", True, True),
)

_P112 = _page(
    "is-vs-equals",
    112,
    "The same value, or the same thing",
    "== asks whether they match. is asks whether they are one object.",
    "Two lists holding the same numbers are equal and are not the same "
    "list — change one and the other does not move. Numbers, strings and "
    "tuples come out as the same object, because Python is free to reuse "
    "one and here it does. "
    "That freedom is the point, and it is why you cannot lean on it. Both "
    "257 lines print True in a file like this, where the two literals are "
    "compiled together and share one constant — type the same two lines "
    "into a REPL and you get False, same Python, same numbers. Nothing is "
    "promised. Use `is` for None, where identity is the actual guarantee, "
    "and `==` for everything else.",
    "is_vs_equals",
    [
        (
            f"Set first to {left} and second to {right}. Print whether they "
            f"are equal, then whether they are the same object.",
            {
                "left": left,
                "right": right,
                "equal": equal,
                "identical": identical,
            },
        )
        for left, right, equal, identical in _IDENTITY
    ],
)


# ── 113. A copy that went one level down ─────────────────────

_COPIES = (
    ([1, 2], 3),
    ([5], 6),
    ([1, 2, 3], 4),
    ([9], 1),
    ([7, 7], 7),
    ([1], 2),
    ([4, 5, 6], 7),
    ([10, 20], 30),
    ([0], 1),
    ([2, 4], 6),
    ([1, 1, 1], 1),
    ([8, 9], 10),
)

_P113 = _page(
    "copy-depth",
    113,
    "A copy that went one level down",
    "A shallow copy copies the outer list and shares everything inside it.",
    "Both lengths come out the same, and that is the lesson: the copy has "
    "its own outer list and the very same inner one, so changing the inner "
    "list is visible through both. It is not a bug in list() — it is what "
    "copying one level means, and it is why copy.deepcopy exists.",
    "copy_depth",
    [
        (
            f"Make a list called inner holding {_list(inner)}, and a list "
            f"outer holding just inner. Make a shallow copy of outer with "
            f"list(). Append {added!r} to inner, then print the length of "
            f"outer's first item, then of the copy's first item.",
            {"inner": inner, "added": added},
        )
        for inner, added in _COPIES
    ],
)


# ── 114. Handing values back one at a time ───────────────────

_GENERATORS = (
    (5, "i", "each number"),
    (4, "i * i", "each number squared"),
    (6, "i * 2", "each number doubled"),
    (3, "i * 100", "each number times 100"),
    (7, "i", "each number"),
    (5, "i + 10", "each number plus 10"),
    (4, "i * i * i", "each number cubed"),
    (8, "i % 3", "the remainder of each divided by 3"),
    (5, "i * 11", "each number times 11"),
    (6, "100 - i", "100 minus each number"),
    (3, "i * i + 1", "each number squared, plus 1"),
    (9, "i * 5", "each number times 5"),
)

_P114 = _page(
    "generator",
    114,
    "Handing values back one at a time",
    "yield: a function that produces a sequence without building one.",
    "A function with yield in it does not run when you call it — it hands "
    "back something that runs a bit at a time, each time the loop asks. The "
    "output is identical to building a list and looping over it, and the "
    "difference is that nothing is ever all in memory at once.",
    "generator",
    [
        (
            f"Write a generator function called {name} that takes n and "
            f"yields {described} from 1 to n. Loop over it with n = {upto}, "
            f"printing each value.",
            {"name": name, "expr": expr, "upto": upto},
        )
        for (upto, expr, described), name in zip(
            _GENERATORS,
            (
                "counter",
                "squares",
                "doubles",
                "hundreds",
                "steps",
                "shifted",
                "cubes",
                "thirds",
                "elevens",
                "backwards",
                "plusone",
                "fives",
            ),
        )
    ],
)


# ── 115. Stopping before it runs out ─────────────────────────

_ENDLESS = (
    (3, "i", "each number"),
    (5, "i * i", "each number squared"),
    (4, "i * 3", "each number times 3"),
    (6, "i", "each number"),
    (2, "i * 50", "each number times 50"),
    (5, "i + 100", "each number plus 100"),
    (3, "i * i * i", "each number cubed"),
    (7, "i * 2", "each number doubled"),
    (4, "i % 2", "the remainder of each divided by 2"),
    (5, "i * 7", "each number times 7"),
    (3, "1000 - i", "1000 minus each number"),
    (6, "i * 10", "each number times 10"),
)

_P115 = _page(
    "generator-take",
    115,
    "Stopping before it runs out",
    "A generator with no end, and taking only what you need.",
    "while True inside a generator is not an infinite loop — it is an "
    "endless supply, and it only runs as far as somebody asks. Building this "
    "as a list would never finish. next() takes one value; the loop around "
    "it decides how many you want.",
    "generator_take",
    [
        (
            f"Write a generator function called {name} that counts from 1 "
            f"for ever, yielding {described}. Take the first {take} values "
            f"from it with next(), printing each.",
            {"name": name, "expr": expr, "take": take},
        )
        for (take, expr, described), name in zip(
            _ENDLESS,
            (
                "forever",
                "squares",
                "threes",
                "counting",
                "fifties",
                "hundreds",
                "cubes",
                "doubles",
                "flip",
                "sevens",
                "downfrom",
                "tens",
            ),
        )
    ],
)


# ── 116. Cleanup that happens anyway ─────────────────────────

_CONTEXTS = (
    ("Door", "opening", "walking through", "closing"),
    ("File", "opened", "writing", "closed"),
    ("Lock", "locked", "in the safe part", "unlocked"),
    ("Session", "logged in", "doing work", "logged out"),
    ("Timer", "started", "the timed bit", "stopped"),
    ("Tap", "on", "filling", "off"),
    ("Curtain", "up", "the act", "down"),
    ("Shop", "open", "serving", "shut"),
    ("Engine", "running", "driving", "off"),
    ("Cage", "unlatched", "feeding", "latched"),
    ("Book", "opened", "reading", "shut"),
    ("Line", "connected", "talking", "hung up"),
)

_P116 = _page(
    "context-manager",
    116,
    "Cleanup that happens anyway",
    "with, __enter__ and __exit__.",
    "Three lines out and in this order: enter, the body, exit. The point is "
    "that the exit runs whatever happens in the body — including if it "
    "raises — which is why files and locks are handed to you this way. You "
    "have already met the idea on page 98; this is what it looks like as a "
    "thing you can hand to someone else.",
    "context_manager",
    [
        (
            f"Write a class called {cls} whose __enter__ prints "
            f'"{opening}" and returns self, and whose __exit__ prints '
            f'"{closing}". Use it in a with block whose body prints '
            f'"{inside}".',
            {
                "cls": cls,
                "opening": opening,
                "inside": inside,
                "closing": closing,
            },
        )
        for cls, opening, inside, closing in _CONTEXTS
    ],
)


# ── 117. Wrapping a function ─────────────────────────────────

_DECORATORS = (
    ("double_it", "n * 2", "the number doubled", "func(n) * 2", "doubles the result", [3, 10]),
    ("add_ten", "n + 10", "the number plus 10", "func(n) + 100", "adds 100 to the result", [1, 40]),
    ("square", "n * n", "the number squared", "func(n) + 1", "adds 1 to the result", [4, 9]),
    ("triple", "n * 3", "the number times 3", "func(n) * 10", "times the result by 10", [2, 7]),
    ("halve", "n // 2", "the number halved", "func(n) - 1", "takes 1 off the result", [10, 21]),
    ("negate", "0 - n", "the number negated", "func(n) + 5", "adds 5 to the result", [3, 8]),
    ("tens", "n * 10", "the number times 10", "func(n) % 7", "the remainder of the result over 7", [5, 12]),
    ("plusone", "n + 1", "the number plus 1", "func(n) * func(n)", "squares the result", [3, 6]),
    ("cube", "n * n * n", "the number cubed", "func(n) // 2", "halves the result", [4, 6]),
    ("less", "n - 5", "the number minus 5", "func(n) * 3", "triples the result", [10, 25]),
    ("mod", "n % 6", "the remainder over 6", "func(n) + 60", "adds 60 to the result", [20, 11]),
    ("twice", "n + n", "the number added to itself", "func(n) - n", "takes the number off the result", [9, 4]),
)

_P117 = _page(
    "decorator",
    117,
    "Wrapping a function",
    "A decorator: a function that takes a function and returns a new one.",
    "@loud above a definition means the same as writing the function and "
    "then replacing it with loud(it). The wrapper calls the original and "
    "does something with the answer — so the name still works, and what "
    "happens when you call it has changed. Read the wrapper before the "
    "decorated function; it is where everything happens.",
    "decorator",
    [
        (
            f"Write a decorator called loud whose wrapper takes n and "
            f"{wrap_described}. Write a function {name} taking n and "
            f"returning {described}, decorated with @loud. Print the result "
            f"of calling it with "
            + " and then ".join(str(v) for v in calls)
            + ".",
            {"name": name, "expr": expr, "wrap": wrap, "calls": calls},
        )
        for name, expr, described, wrap, wrap_described, calls in _DECORATORS
    ],
)


# ── 118. Remembering where it was made ───────────────────────

_CLOSURES = (
    ([2, 10], 5, "n * m", "n times m"),
    ([1, 100], 7, "n + m", "n plus m"),
    ([3, 30], 4, "n * m + n", "n times m, plus n"),
    ([10, 20], 3, "n - m", "n minus m"),
    ([5, 50], 2, "n * m * m", "n times m twice"),
    ([7, 70], 10, "n + m + n", "n plus m plus n"),
    ([2, 3], 8, "n * m", "n times m"),
    ([100, 200], 50, "n - m", "n minus m"),
    ([4, 9], 6, "n * m - m", "n times m, minus m"),
    ([11, 22], 2, "n * m", "n times m"),
    ([6, 60], 5, "n % m", "the remainder of n over m"),
    ([8, 80], 4, "n + m * 2", "n plus twice m"),
)

_P118 = _page(
    "closure",
    118,
    "Remembering where it was made",
    "A closure: an inner function that keeps hold of the outer one's value.",
    "make() finishes and returns, and the inner function still knows what n "
    "was — each one keeping its own. That is what a decorator is doing on "
    "page 117, and what makes a function returned from a function useful "
    "rather than a curiosity.",
    "closure",
    [
        (
            f"Write a function make that takes n and returns an inner "
            f"function taking m and returning {described}. Make one with n = "
            f"{outer[0]} and another with n = {outer[1]}, then call each with "
            f"m = {inner} and print both results.",
            {"outer": outer, "inner": inner, "expr": expr},
        )
        for outer, inner, expr, described in _CLOSURES
    ],
)


# ── 119. Counting without the loop ───────────────────────────

_COUNTS = (
    (["a", "b", "a"], ["a", "b"]),
    (["red", "blue", "red", "red"], ["red", "blue"]),
    (["x"], ["x"]),
    (["one", "two", "two", "three", "three", "three"], ["three", "one"]),
    (["cat", "dog", "cat"], ["cat", "dog"]),
    (["up", "up", "up", "down"], ["up", "down"]),
    (["a", "a", "a", "a"], ["a"]),
    (["yes", "no", "yes", "no"], ["yes", "no"]),
    (["p", "q", "r"], ["q", "r", "p"]),
    (["hi", "hi", "bye"], ["bye", "hi"]),
    (["1", "2", "1", "2", "1"], ["1", "2"]),
    (["north", "south", "north", "east", "north"], ["north", "east"]),
)

_P119 = _page(
    "counter-use",
    119,
    "Counting without the loop",
    "Counter, which is the loop from page 35 already written.",
    "Hand it anything you can loop over and it hands back how many of each. "
    "Asking for a key that never appeared gives 0 rather than an error, "
    "which is the whole reason to reach for it instead of a plain dict — no "
    "checking whether the key exists before adding to it.",
    "counter_use",
    [
        (
            f"Put the words {_words(words)} in a list and count them with "
            f"Counter. Print the count for "
            + ", then ".join(f'"{k}"' for k in keys)
            + ".",
            {"words": words, "keys": keys},
        )
        for words, keys in _COUNTS
    ],
)


# ── 120. One thing, then another ─────────────────────────────

_TUPLE_SORTS = (
    ["pear", "fig", "apple", "plum"],
    ["one", "two", "six", "three"],
    ["bb", "a", "cc", "d"],
    ["red", "blue", "pink", "grey"],
    ["do", "re", "mi", "fa"],
    ["go", "rust", "ruby", "c"],
    ["ox", "cat", "cow", "hen"],
    ["up", "in", "out", "off"],
    ["hi", "hey", "yo", "hiya"],
    ["pi", "be", "alpha", "gamma"],
    ["z", "yy", "xx", "w"],
    ["sun", "moon", "star", "sky"],
)

_P120 = _page(
    "sort-tuple-key",
    120,
    "One thing, then another",
    "A key returning a tuple, so ties are broken by the next thing.",
    "sorted compares the tuples left to right: length first, and where two "
    "are the same length it goes on to compare the words themselves. That is "
    "how every multi-column sort works, and it is one pair of brackets more "
    "than page 94.",
    "sort_tuple_key",
    [
        (
            f"Put the words {_words(words)} in a list. Print them one per "
            f"line, shortest first, with equal lengths in alphabetical order.",
            {"words": words},
        )
        for words in _TUPLE_SORTS
    ],
)


EDGE_PAGES: tuple[Page, ...] = (
    _P111,
    _P112,
    _P113,
    _P114,
    _P115,
    _P116,
    _P117,
    _P118,
    _P119,
    _P120,
)
