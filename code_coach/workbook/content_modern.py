"""Intermediate pages 169-178: newer syntax, and the protocols.

The first half is syntax most tutorials still do not reach - match, the
walrus, dict merging with a bar - together with partial and itemgetter,
which have been in the standard library forever and get skipped anyway.

The second half takes the protocol idea seriously. Pages 144 and 145
wrote __eq__ and __lt__ so that == and sorted would work on your own
objects. Here it is __iter__, so a for loop works, and __hash__, so a
set works. The lesson under all four is one lesson: you are not adding
methods for callers to call, you are answering questions the language
already knows how to ask.

Python only, same as 81-168.
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


# ── 169. Matching a value against several cases ──────────────

_MATCHES = (
    ("describe", ((0, "zero"), (1, "one")), "many", (0, 1, 5)),
    ("name_it", ((1, "single"), (2, "double")), "lots", (1, 2, 9)),
    ("size_of", ((10, "ten"), (20, "twenty")), "other", (10, 20, 30)),
    ("colour", ((1, "red"), (2, "green"), (3, "blue")), "unknown", (2, 3, 7)),
    ("day", ((6, "saturday"), (7, "sunday")), "weekday", (6, 7, 3)),
    ("coin", ((1, "penny"), (5, "nickel")), "note", (1, 5, 50)),
    ("floor", ((0, "ground"), (1, "first")), "upstairs", (0, 1, 4)),
    ("state", ((0, "off"), (1, "on")), "broken", (0, 1, 2)),
    ("rank", ((1, "gold"), (2, "silver"), (3, "bronze")), "nothing",
     (1, 3, 8)),
    ("suit", ((1, "spades"), (2, "hearts")), "unknown", (2, 1, 4)),
    ("speed", ((0, "stopped"), (1, "crawling")), "moving", (0, 1, 60)),
    ("count", ((0, "none"), (1, "one")), "several", (0, 1, 12)),
)

_P169 = _page(
    "match-stmt",
    169,
    "Matching a value against several cases",
    "match and case, and the underscore that catches the rest.",
    "This is not a switch, though it looks like one - match can pull "
    "apart lists, dicts and objects, and these pages only use the "
    "simplest form of it. Two things to know now: case _ is the catch-all "
    "and goes last, and a bare name in a case pattern does not compare "
    "against that variable, it captures into it, which is the surprise "
    "that bites everyone once. Matching against literals, as here, has no "
    "such trap.",
    "match_stmt",
    [
        (
            "Write "
            + name
            + "(value) using match on value, with a case for each of "
            + ", ".join(f"{w!r} returning {label!r}" for w, label in cases)
            + ", and a case _ returning "
            + repr(otherwise)
            + ". Loop n over ["
            + _seq(values)
            + "] printing "
            + name
            + "(n).",
            {
                "name": name,
                "cases": cases,
                "otherwise": otherwise,
                "values": values,
            },
        )
        for name, cases, otherwise, values in _MATCHES
    ],
)


# ── 170. Naming a value in the middle of a test ──────────────

_WALRUS = (
    ((1, 2, 3, 4, 5, 6), "doubled", "n * 2", 6),
    ((1, 2, 3, 4, 5), "squared", "n * n", 9),
    ((10, 20, 30), "half", "n // 2", 7),
    ((3, 6, 9, 12), "tripled", "n * 3", 20),
    ((5, 10, 15, 20), "less", "n - 4", 8),
    ((2, 4, 6, 8), "cubed", "n * n * n", 60),
    ((7, 14, 21), "plus", "n + 10", 20),
    ((100, 200, 300), "tenth", "n // 10", 15),
    ((1, 3, 5, 7, 9), "doubled", "n * 2", 10),
    ((4, 8, 12, 16), "quarter", "n // 4", 2),
    ((11, 22, 33), "squared", "n * n", 500),
    ((6, 12, 18, 24), "third", "n // 3", 5),
)

_P170 = _page(
    "walrus",
    170,
    "Naming a value in the middle of a test",
    "The walrus, for when you need the value you just tested.",
    "Without it you work the value out, store it, then test the "
    "variable - three lines where the middle one exists only because the "
    "if could not hold a name. The walrus assigns and produces the value "
    "at once, so the test and the name happen together. Keep the "
    "brackets: without them the precedence is not what you want. And "
    "keep it small - a walrus buried inside a long condition is exactly "
    "the sort of clever that costs someone an afternoon.",
    "walrus",
    [
        (
            "Set numbers to ["
            + _seq(items)
            + "]. Loop n over it, and using a walrus inside the if, set "
            + name
            + " to "
            + expr
            + " and print it when it is greater than "
            + str(limit)
            + ".",
            {"items": items, "name": name, "expr": expr, "limit": limit},
        )
        for items, name, expr, limit in _WALRUS
    ],
)


# ── 171. A function with an argument already filled in ───────

_PARTIALS = (
    ("scale", "factor", "n", "factor * n", (2, 3), ("double", "triple"), 7),
    ("add_to", "base", "n", "base + n", (10, 100), ("plus_ten", "plus_hundred"), 5),
    ("power", "exp", "n", "n ** exp", (2, 3), ("square", "cube"), 4),
    ("shift", "by", "n", "n - by", (1, 5), ("less_one", "less_five"), 20),
    ("split_by", "parts", "n", "n // parts", (2, 4), ("halve", "quarter"), 40),
    ("repeat", "times", "n", "n * times", (5, 10), ("five_x", "ten_x"), 3),
    ("over", "top", "n", "top - n", (100, 50), ("from_hundred", "from_fifty"), 20),
    ("stack", "high", "n", "high * n", (6, 9), ("six_up", "nine_up"), 8),
    ("step", "size", "n", "n + size", (25, 50), ("small", "big"), 100),
    ("cut", "off", "n", "n % off", (7, 10), ("mod_seven", "mod_ten"), 43),
    ("grow", "rate", "n", "n * rate", (3, 4), ("triple", "quadruple"), 11),
    ("drop", "amount", "n", "n - amount", (2, 8), ("minus_two", "minus_eight"), 30),
)

_P171 = _page(
    "partial-use",
    171,
    "A function with an argument already filled in",
    "functools.partial, for making a specific function out of a general one.",
    "partial hands back a new function with some arguments already "
    "supplied, so one general function becomes several specific ones "
    "without writing any of them. This is the same idea as the closure on "
    "page 118 - a function carrying a value - said in one line and with "
    "no def. Handy anywhere something wants a function of one argument "
    "and yours takes two, which is most callbacks and every sort key.",
    "partial_use",
    [
        (
            "Import partial from functools. Write "
            + func
            + "("
            + first
            + ", "
            + second
            + ") returning "
            + expr
            + ". Make "
            + names[0]
            + " and "
            + names[1]
            + " as partials of it with "
            + first
            + " fixed to "
            + repr(fixed[0])
            + " and "
            + repr(fixed[1])
            + ". Print each called with "
            + repr(call)
            + ".",
            {
                "func": func,
                "first": first,
                "second": second,
                "expr": expr,
                "fixed": fixed,
                "names": names,
                "call": call,
            },
        )
        for func, first, second, expr, fixed, names, call in _PARTIALS
    ],
)


# ── 172. Sorting by a position, without a lambda ─────────────

_GETTERS = (
    ((("ada", 90), ("sam", 7), ("kim", 41)), 1),
    ((("red", 12), ("blue", 9), ("green", 30)), 1),
    ((("nails", 120), ("screws", 40), ("bolts", 75)), 1),
    ((("mon", 2), ("tue", 14), ("wed", 8)), 1),
    ((("iron", 26), ("gold", 79), ("tin", 50)), 1),
    ((("apple", 3), ("pear", 12), ("fig", 7)), 1),
    ((("kyoto", 1463), ("oslo", 709), ("lima", 998)), 1),
    ((("front", 4), ("back", 55), ("side", 20)), 1),
    ((("zeta", 1), ("alpha", 2), ("mu", 3)), 0),
    ((("wren", 5), ("ant", 9), ("moth", 2)), 0),
    ((("north", 6), ("south", 19), ("east", 1)), 0),
    ((("salt", 11), ("pepper", 22), ("sugar", 3)), 0),
)

_P172 = _page(
    "itemgetter-sort",
    172,
    "Sorting by a position, without a lambda",
    "operator.itemgetter, which says the same thing more plainly.",
    "key=itemgetter(1) and key=lambda pair: pair[1] do exactly the same "
    "job, and the first says what it means without making the reader "
    "parse a function definition. It is also faster, though that is "
    "rarely the reason to pick it. Change the number to 0 and you sort by "
    "the name instead, which the last four of these do - same call, "
    "different column.",
    "itemgetter_sort",
    [
        (
            "Import itemgetter from operator. Set rows to ["
            + ", ".join(f"({n!r}, {v!r})" for n, v in rows)
            + "]. Loop over sorted of rows with key=itemgetter("
            + str(index)
            + "), unpacking into name and score, and print both on one "
            "line.",
            {"rows": rows, "index": index},
        )
        for rows, index in _GETTERS
    ],
)


# ── 173. Adding and taking from both ends ────────────────────

_DEQUES = (
    ((1, 2, 3), 4, 0),
    ((10, 20), 30, 5),
    ((7,), 8, 6),
    ((2, 4, 6), 8, 0),
    ((100, 200), 300, 50),
    ((1, 1, 1), 2, 0),
    ((5, 6, 7), 9, 4),
    ((11, 22), 33, 1),
    ((3, 6), 9, 0),
    ((8, 16, 24), 32, 4),
    ((15, 25), 35, 5),
    ((9, 8, 7), 6, 10),
)

_P173 = _page(
    "deque-use",
    173,
    "Adding and taking from both ends",
    "collections.deque, and why a list is the wrong queue.",
    "A list is fine at its right-hand end and slow at its left, because "
    "removing the first item shuffles everything else down one. A deque "
    "is built for both ends: append and pop on the right, appendleft and "
    "popleft on the left, all cheap however long it gets. Use it whenever "
    "you have a queue, a sliding window, or a history you trim from one "
    "end - and a plain list whenever you do not.",
    "deque_use",
    [
        (
            "Import deque from collections. Make queue a deque of ["
            + _seq(items)
            + "], append "
            + repr(right)
            + " and appendleft "
            + repr(left)
            + ". Print the list of it, then popleft, then pop, then the "
            "list of it again.",
            {"items": items, "right": right, "left": left},
        )
        for items, right, left in _DEQUES
    ],
)


# ── 174. Rows turned into columns ────────────────────────────

_GRIDS = (
    (((1, 2, 3), (4, 5, 6)),),
    (((1, 2), (3, 4)),),
    (((1, 2), (3, 4), (5, 6)),),
    (((10, 20, 30), (40, 50, 60)),),
    (((1, 2, 3, 4), (5, 6, 7, 8)),),
    (((7, 8), (9, 10), (11, 12)),),
    (((0, 1), (2, 3)),),
    (((2, 4, 6), (8, 10, 12)),),
    (((1, 1), (2, 2), (3, 3)),),
    (((5, 10), (15, 20)),),
    (((9, 8, 7), (6, 5, 4)),),
    (((100, 200), (300, 400), (500, 600)),),
)

_P174 = _page(
    "transpose",
    174,
    "Rows turned into columns",
    "zip with a star, which is the whole transpose.",
    "The star unpacks the list of rows into separate arguments, so zip "
    "sees each row as its own list and pairs them up position by "
    "position - which is exactly a transpose. It is worth staring at "
    "until it clicks, because star-unpacking a collection into a call is "
    "the idea, and transposing is only the first use you will find for "
    "it. Note what comes back: tuples, not lists, because that is what "
    "zip makes.",
    "transpose",
    [
        (
            "Set rows to ["
            + ", ".join("[" + _seq(r) + "]" for r in grid)
            + "]. Loop over zip of star rows, printing each column.",
            {"rows": grid},
        )
        for (grid,) in _GRIDS
    ],
)


# ── 175. Two dicts joined, and who wins ──────────────────────

_MERGES = (
    ((("a", 1), ("b", 2)), (("b", 20), ("c", 30))),
    ((("x", 5), ("y", 6)), (("y", 60), ("z", 70))),
    ((("red", 1), ("blue", 2)), (("blue", 9), ("green", 3))),
    ((("one", 1),), (("two", 2), ("three", 3))),
    ((("mon", 2), ("tue", 3)), (("tue", 30),)),
    ((("iron", 26),), (("gold", 79), ("iron", 260))),
    ((("a", 1), ("b", 2), ("c", 3)), (("c", 33),)),
    ((("north", 1), ("south", 2)), (("east", 3), ("west", 4))),
    ((("salt", 11),), (("salt", 110), ("pepper", 22))),
    ((("do", 1), ("re", 2)), (("re", 22), ("mi", 3))),
    ((("front", 4),), (("back", 5),)),
    ((("apple", 3), ("pear", 12)), (("fig", 7),)),
)

_P175 = _page(
    "dict-merge",
    175,
    "Two dicts joined, and who wins",
    "The bar operator on dicts, and which side takes precedence.",
    "first | second gives a new dict with everything from both, and where "
    "they share a key the right-hand one wins - which is the whole "
    "question, and the reason the order reads as defaults on the left and "
    "overrides on the right. Neither original is changed. Several of "
    "these have a key in both; find it in the output and check which "
    "value survived.",
    "dict_merge",
    [
        (
            "Set first to a dict of "
            + ", ".join(f"{k!r}: {v!r}" for k, v in one)
            + " and second to "
            + ", ".join(f"{k!r}: {v!r}" for k, v in two)
            + ". Set merged to first | second, then loop over "
            "sorted(merged) printing each key and its value.",
            {"first": one, "second": two},
        )
        for one, two in _MERGES
    ],
)


# ── 176. What __name__ actually holds ────────────────────────

_MAINS = (
    "running",
    "started",
    "here we go",
    "main called",
    "hello",
    "begin",
    "go",
    "doing the work",
    "off we go",
    "at the top",
    "entry point",
    "away",
)

_P176 = _page(
    "name-main",
    176,
    "What __name__ actually holds",
    "The if that goes at the bottom of nearly every Python file.",
    "You have seen this line and probably copied it. Here is what it "
    "does: Python sets __name__ to the string \"__main__\" in the file "
    "you ran, and to the module's own name in every file that was "
    "imported. So the guard means run this only when I am the program, "
    "not when someone imports me for a function. Print __name__ and see "
    "it for yourself - the whole mystery is one string. Without the "
    "guard, importing your file runs it.",
    "name_main",
    [
        (
            "Write main() printing "
            + repr(message)
            + ". Then print __name__, and after it write the standard "
            'guard - if __name__ == "__main__" - calling main().',
            {"message": message},
        )
        for message in _MAINS
    ],
)


# ── 177. A class a for loop can walk ─────────────────────────

_ITERS = (
    ("Countdown", 3, 1),
    ("Countdown", 5, 1),
    ("Backwards", 4, 1),
    ("Evens", 10, 2),
    ("Evens", 8, 2),
    ("Steps", 9, 3),
    ("Steps", 12, 4),
    ("Down", 6, 2),
    ("Down", 7, 3),
    ("Ticker", 5, 5),
    ("Ticker", 20, 10),
    ("Countdown", 2, 1),
)

_P177 = _page(
    "iter-protocol",
    177,
    "A class a for loop can walk",
    "__iter__, and yielding from inside it.",
    "A for loop does not need a list - it needs something that answers "
    "__iter__. Write that method and your own class works in a for loop, "
    "in a comprehension, in list(), everywhere. Making it a generator "
    "with yield is the easy way: the method hands back an iterator "
    "without you writing __next__ or raising StopIteration by hand. "
    "This is pages 114 and 144 meeting - a generator, used to answer a "
    "protocol.",
    "iter_protocol",
    [
        (
            "Write a class "
            + cls
            + " whose __init__ stores start, and whose __iter__ sets n to "
            "self.start and, while n is above 0, yields n and then "
            "subtracts "
            + str(step)
            + ". Loop over "
            + cls
            + "("
            + str(start)
            + ") printing each value.",
            {"cls": cls, "start": start, "step": step},
        )
        for cls, start, step in _ITERS
    ],
)


# ── 178. Objects that can live in a set ──────────────────────

_HASHES = (
    ("Point", (("x", "int"), ("y", "int")), ((1, 2), (1, 2), (3, 4))),
    ("Point", (("x", "int"), ("y", "int")), ((0, 0), (1, 1), (2, 2))),
    ("Pair", (("left", "int"), ("right", "int")), ((5, 6), (5, 6), (5, 6))),
    ("Size", (("width", "int"), ("height", "int")), ((10, 4), (4, 10))),
    ("Card", (("suit", "str"), ("rank", "int")),
     (("spades", 11), ("spades", 11), ("hearts", 11))),
    ("Room", (("floor", "int"), ("number", "int")),
     ((3, 12), (3, 12), (2, 12), (2, 12))),
    ("Coin", (("face", "str"), ("worth", "int")),
     (("heads", 25), ("tails", 25))),
    ("Step", (("label", "str"), ("order", "int")),
     (("mix", 2), ("mix", 2), ("bake", 3))),
    ("Point", (("x", "int"), ("y", "int")), ((7, 7), (7, 7), (7, 8), (8, 7))),
    ("Pair", (("left", "int"), ("right", "int")), ((1, 2), (2, 1))),
    ("City", (("name", "str"), ("people", "int")),
     (("kyoto", 1463), ("kyoto", 1463))),
    ("Size", (("width", "int"), ("height", "int")),
     ((2, 3), (2, 3), (2, 3), (9, 9))),
)

_P178 = _page(
    "hash-dunder",
    178,
    "Objects that can live in a set",
    "__hash__ alongside __eq__, and why one without the other fails.",
    "Page 144 gave a class __eq__ - and quietly made it unusable in a "
    "set, because defining __eq__ sets __hash__ to None unless you write "
    "one. That is deliberate: a set finds things by hash first and only "
    "then checks equality, so two objects that are equal must hash the "
    "same or the set will hold both. Hashing a tuple of the same fields "
    "you compared is the standard answer, and it is what a frozen "
    "dataclass writes for you. Count the output: equal ones collapse.",
    "hash_dunder",
    [
        (
            "Write a class "
            + cls
            + " whose __init__ takes and stores "
            + " and ".join(n for n, _ in fields)
            + ", an __eq__ comparing every field, and a __hash__ returning "
            "hash of a tuple of the same fields. Build a set of "
            + ", ".join(
                cls + "(" + ", ".join(repr(v) for v in p) + ")"
                for p in points
            )
            + " and print how many it holds.",
            {"cls": cls, "fields": fields, "points": points},
        )
        for cls, fields, points in _HASHES
    ],
)


MODERN_PAGES: tuple[Page, ...] = (
    _P169,
    _P170,
    _P171,
    _P172,
    _P173,
    _P174,
    _P175,
    _P176,
    _P177,
    _P178,
)
