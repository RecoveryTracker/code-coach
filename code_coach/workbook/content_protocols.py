"""Intermediate pages 199-208: more protocols, and waiting properly.

Four more dunders, which between them are most of what makes a class you
wrote feel like a type Python shipped: __call__ so it can be called,
__getitem__ and __len__ so it can be indexed and measured, and a
property with a setter so plain assignment can run code. Before them,
functools.wraps, which repairs something page 117 quietly broke and did
not mention.

Then heapq and bisect, total_ordering, a comprehension with two fors,
and async and await - where the point is not speed but that waiting for
one thing should not stop everything else.

Python only, same as 81-198.
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


# ── 199. A decorator that does not lose the name ─────────────

_WRAPS = (
    ("double", "n * 2", "func(n) + 1", 5),
    ("square", "n * n", "func(n) + 10", 4),
    ("triple", "n * 3", "func(n) * 2", 3),
    ("half", "n // 2", "func(n) + 100", 9),
    ("negate", "-n", "func(n) - 1", 7),
    ("add_one", "n + 1", "func(n) * 3", 6),
    ("cube", "n * n * n", "func(n) + 5", 2),
    ("tenth", "n // 10", "func(n) + 2", 95),
    ("twice", "n + n", "func(n) * 10", 8),
    ("less", "n - 1", "func(n) * 4", 11),
    ("scale", "n * 5", "func(n) - 3", 4),
    ("shift", "n + 100", "func(n) // 2", 50),
)

_P199 = _page(
    "wraps-use",
    199,
    "A decorator that does not lose the name",
    "functools.wraps, and what page 117 quietly broke.",
    "Page 117 wrapped a function in another one, and the wrapping "
    "replaced it entirely - so the name, the docstring and the signature "
    "all became the wrapper's. Print __name__ on a decorated function "
    "without wraps and you get 'wrapper', which breaks help(), breaks "
    "debuggers, and makes tracebacks lie about which function you are "
    "in. @wraps(func) copies all of it across. It is one line, and there "
    "is no good reason to write a decorator without it.",
    "wraps_use",
    [
        (
            "Import wraps from functools. Write louder(func) whose inner "
            "wrapper(n) is decorated with @wraps(func) and returns "
            + wrap
            + ". Decorate "
            + name
            + "(n) - which returns "
            + expr
            + " - with @louder. Print the result of calling it with "
            + repr(call)
            + ", then print its __name__.",
            {"name": name, "expr": expr, "wrap": wrap, "call": call},
        )
        for name, expr, wrap, call in _WRAPS
    ],
)


# ── 200. An object you can call like a function ──────────────

# Expressions are written in terms of the field's own name; the emitter
# rewrites them to self.<field>, so the same string can be evaluated for
# the expected output where there is no self.
_CALLABLES = (
    ("Adder", "amount", 5, "n + amount", 10),
    ("Scaler", "factor", 3, "n * factor", 7),
    ("Shifter", "by", 100, "n - by", 250),
    ("Repeater", "times", 4, "n * times", 6),
    ("Capper", "top", 50, "n if n < top else top", 90),
    ("Floorer", "floor", 10, "n if n > floor else floor", 3),
    ("Splitter", "parts", 4, "n // parts", 40),
    ("Modder", "by", 7, "n % by", 45),
    ("Doubler", "extra", 1, "n * 2 + extra", 9),
    ("Offset", "start", 1000, "start + n", 24),
    ("Shrinker", "amount", 8, "n - amount", 20),
    ("Power", "exp", 2, "n ** exp", 5),
)

_P200 = _page(
    "call-dunder",
    200,
    "An object you can call like a function",
    "__call__, and the line between a function and an object.",
    "With __call__ defined, thing(10) works - the object is callable, "
    "and callable() says so. Why bother, when a closure from page 118 "
    "carries a value too? Because an object can also be inspected, "
    "printed, compared and changed, and a closure cannot. Reach for it "
    "when a function needs configuration and a life of its own; reach "
    "for a plain function when it does not.",
    "call_dunder",
    [
        (
            "Write a class "
            + cls
            + " whose __init__ takes and stores "
            + field
            + ", and a __call__ taking n that returns "
            + expr.replace(field, "self." + field)
            + ". Make thing holding "
            + repr(held)
            + ", print the result of calling thing with "
            + repr(call)
            + ", then print callable(thing).",
            {
                "cls": cls,
                "field": field,
                "held": held,
                "expr": expr,
                "call": call,
            },
        )
        for cls, field, held, expr, call in _CALLABLES
    ],
)


# ── 201. A class that indexes and measures ───────────────────

_SEQUENCES = (
    ("Deck", (1, 2, 3)),
    ("Row", (10, 20, 30, 40)),
    ("Stack", (5, 6)),
    ("Bag", (7, 8, 9)),
    ("Line", (100, 200)),
    ("Train", (1, 1, 2, 3, 5)),
    ("Shelf", (4, 8, 12)),
    ("Rack", (11, 22, 33, 44)),
    ("Queue", (2, 4)),
    ("Chain", (9, 8, 7, 6)),
    ("Belt", (3, 6, 9)),
    ("Strip", (1, 3, 5, 7, 9)),
)

_P201 = _page(
    "getitem-len",
    201,
    "A class that indexes and measures",
    "__len__ and __getitem__, and what you get for free.",
    "Two methods, and your class starts behaving like a list: len() "
    "works, square brackets work, negative indexes work because you "
    "handed the position straight to a list that already understands "
    "them - and, quietly, so does looping. list(thing) on the last line "
    "never touched __iter__ from page 177, because Python will fall back "
    "to calling __getitem__ with 0, 1, 2 until it runs out. Answer the "
    "questions the language asks and it does the rest.",
    "getitem_len",
    [
        (
            "Write a class "
            + cls
            + " whose __init__ stores items, with __len__ returning the "
            "length of items and __getitem__ taking position and "
            "returning items at that position. Make thing holding ["
            + _seq(items)
            + "], then print its length, its first item, its last item "
            "with -1, and list(thing).",
            {"cls": cls, "items": items},
        )
        for cls, items in _SEQUENCES
    ],
)


# ── 202. Assignment that runs code ───────────────────────────

_SETTERS = (
    ("Person", "ada", "  grace hopper  "),
    ("Person", "sam", "  alan turing "),
    ("User", "kim", " barbara liskov  "),
    ("Author", "hume", "  mary shelley "),
    ("Player", "finn", " ada lovelace  "),
    ("Guest", "rey", "  katherine johnson "),
    ("Member", "jo", " grace murray  "),
    ("Client", "max", "  tim berners lee "),
    ("Owner", "eve", " margaret hamilton  "),
    ("Staff", "abe", "  edsger dijkstra "),
    ("Pupil", "ida", " donald knuth  "),
    ("Coach", "ben", "  barbara jordan "),
)

_P202 = _page(
    "property-setter",
    202,
    "Assignment that runs code",
    "A property setter, so thing.name = x can do work.",
    "Page 141 made a property you could read. This one you can also "
    "write to, and the setter runs on the way in - here stripping the "
    "spaces and fixing the capitals, so the object cannot hold a messy "
    "value even if the caller hands it one. The pattern is a plain "
    "attribute first, then a property the day it needs checking or "
    "cleaning, and no caller has to change. Note the underscore on "
    "_name: the property is name, so the storage needs its own.",
    "property_setter",
    [
        (
            "Write a class "
            + cls
            + " whose __init__ stores name as self._name, a property name "
            "returning it, and a name setter storing value stripped and "
            "title-cased. Make thing with "
            + repr(first)
            + " and print its name. Then assign "
            + repr(second)
            + " to thing.name and print it again.",
            {"cls": cls, "first": first, "second": second},
        )
        for cls, first, second in _SETTERS
    ],
)


# ── 203. The few smallest, without sorting it all ────────────

_HEAPS = (
    ((7, 2, 9, 4, 1), 3, 2),
    ((10, 30, 20, 50, 40), 2, 3),
    ((5, 3, 8, 1), 2, 2),
    ((100, 25, 75, 50), 3, 1),
    ((9, 8, 7, 6, 5, 4), 4, 2),
    ((1, 2, 3, 4, 5), 2, 2),
    ((42, 7, 99, 13), 2, 3),
    ((6, 6, 2, 9), 3, 2),
    ((15, 3, 27, 9, 21), 3, 3),
    ((88, 12, 45), 2, 2),
    ((4, 16, 8, 2), 3, 1),
    ((11, 5, 17, 3, 23), 4, 2),
)

_P203 = _page(
    "heapq-use",
    203,
    "The few smallest, without sorting it all",
    "heapq.nsmallest and nlargest.",
    "Sorting a million numbers to look at three of them is work you did "
    "not need. These keep only as many as you asked for while walking "
    "the data once, which matters at size and not at all here - the "
    "reason to learn it now is that the call says what you meant. heapq "
    "also underlies priority queues, where you always want the smallest "
    "thing next and never the whole order.",
    "heapq_use",
    [
        (
            "Import heapq. Set numbers to ["
            + _seq(items)
            + "], then print heapq.nsmallest of "
            + str(small)
            + " of it, and heapq.nlargest of "
            + str(large)
            + ".",
            {"items": items, "small": small, "large": large},
        )
        for items, small, large in _HEAPS
    ],
)


# ── 204. Putting something in and keeping it sorted ──────────

_BISECTS = (
    ((1, 3, 5, 7), 4, 5),
    ((10, 20, 30), 25, 30),
    ((2, 4, 6, 8), 5, 6),
    ((1, 2, 3), 0, 2),
    ((5, 15, 25), 20, 25),
    ((100, 200), 150, 200),
    ((1, 4, 9, 16), 8, 9),
    ((3, 6, 9), 7, 9),
    ((11, 22, 33), 27, 33),
    ((2, 3, 5, 7), 6, 7),
    ((1, 10, 100), 50, 100),
    ((4, 8, 12, 16), 10, 12),
)

_P204 = _page(
    "bisect-use",
    204,
    "Putting something in and keeping it sorted",
    "bisect.insort, and bisect_left for finding the place.",
    "insort puts a value where it belongs in an already-sorted list, so "
    "the list never has to be sorted again. bisect_left tells you where "
    "something is or would go, by halving the range rather than walking "
    "it - the binary search you would otherwise write, and get slightly "
    "wrong. The whole module rests on one condition you must keep: the "
    "list has to be sorted already, and nothing checks that for you.",
    "bisect_use",
    [
        (
            "Import bisect. Set numbers to ["
            + _seq(items)
            + "], insort "
            + repr(added)
            + " into it, then print numbers and bisect_left of numbers "
            "for "
            + repr(find)
            + ".",
            {"items": items, "added": added, "find": find},
        )
        for items, added, find in _BISECTS
    ],
)


# ── 205. One comparison, and the rest for free ───────────────

_ORDERINGS = (
    ("Card", "rank", (3, 9)),
    ("Player", "score", (41, 90)),
    ("Book", "pages", (204, 412)),
    ("City", "people", (709, 1463)),
    ("Song", "seconds", (173, 245)),
    ("Metal", "number", (26, 79)),
    ("Room", "floor", (1, 4)),
    ("Tool", "weight", (3, 8)),
    ("Task", "order", (1, 3)),
    ("Team", "points", (12, 41)),
    ("Word", "length", (3, 8)),
    ("Trip", "miles", (40, 120)),
)

_P205 = _page(
    "total-ordering",
    205,
    "One comparison, and the rest for free",
    "@total_ordering, which fills in the other four.",
    "Write __eq__ and __lt__ and this decorator works out >, <=, >= and "
    "!= from them, which saves four methods that could each be wrong in "
    "their own way. The cost is a little speed on each comparison, which "
    "almost never matters. Write the four by hand only when you have "
    "measured that it does - and if you find yourself writing them all, "
    "check first whether a dataclass with order=True already does what "
    "you want.",
    "total_ordering",
    [
        (
            "Import total_ordering from functools. Write a class "
            + cls
            + " decorated with it, storing "
            + field
            + ", with __eq__ and __lt__ both comparing self."
            + field
            + " to other."
            + field
            + ". Make first with "
            + repr(values[0])
            + " and second with "
            + repr(values[1])
            + ", then print first < second, first >= second, and first != "
            "second.",
            {"cls": cls, "field": field, "values": values},
        )
        for cls, field, values in _ORDERINGS
    ],
)


# ── 206. A comprehension with two fors ───────────────────────

_NESTED = (
    ((1, 2), (3, 4)),
    ((1, 2, 3), (4, 5, 6)),
    ((10, 20), (30,)),
    ((5,), (6, 7)),
    ((1, 1), (2, 2), (3, 3)),
    ((2, 4), (6, 8), (10, 12)),
    ((7, 8, 9), (10,)),
    ((100,), (200, 300)),
    ((1, 2), (3, 4), (5, 6)),
    ((9,), (8,), (7,)),
    ((11, 22), (33, 44)),
    ((3, 6, 9), (12, 15)),
)

_P206 = _page(
    "nested-comp",
    206,
    "A comprehension with two fors",
    "Flattening, and the order the fors go in.",
    "Two fors in one comprehension read left to right in exactly the "
    "order you would write the nested loops - outer first, inner second. "
    "That is the only thing to remember, and it is the thing people get "
    "backwards, because the expression at the front uses the innermost "
    "name and the eye wants to read it first. Flattening a list of lists "
    "is the common use, and past two levels a loop is kinder to whoever "
    "reads it.",
    "nested_comp",
    [
        (
            "Set rows to ["
            + ", ".join("[" + _seq(r) + "]" for r in rows)
            + "]. Build flat as a comprehension with a for over rows and "
            "a for over each row, then print flat and its sum.",
            {"rows": rows},
        )
        for rows in _NESTED
    ],
)


# ── 207. async and await, in order ───────────────────────────

_ASYNCS = (
    ("n * 2", (3, 5)),
    ("n * n", (4, 6)),
    ("n + 100", (1, 2)),
    ("n // 2", (10, 21)),
    ("n * 10", (7, 8)),
    ("n - 1", (50, 99)),
    ("n * n * n", (2, 3)),
    ("n + n", (11, 12)),
    ("n % 7", (30, 45)),
    ("n * 3", (9, 14)),
    ("n + 1", (0, 41)),
    ("n // 3", (27, 40)),
)

_P207 = _page(
    "async-basic",
    207,
    "async and await, in order",
    "async def, await, and asyncio.run.",
    "An async def is a coroutine: calling it does nothing at all until "
    "something awaits it, which is the first surprise. await runs it and "
    "waits for the answer, and asyncio.run starts the whole machine from "
    "ordinary code. This page awaits one thing then the other, so it is "
    "no faster than plain functions - and that is the honest starting "
    "point. Async buys nothing until something is actually waiting on "
    "the world, and buys a great deal then.",
    "async_basic",
    [
        (
            "Import asyncio. Write an async def work(n) returning "
            + expr
            + ". Write an async def main() that awaits work("
            + repr(values[0])
            + ") into first and work("
            + repr(values[1])
            + ") into second, printing each. Run it with asyncio.run.",
            {"expr": expr, "values": values},
        )
        for expr, values in _ASYNCS
    ],
)


# ── 208. Several at once, results in order ───────────────────

_GATHERS = (
    ("n * n", (2, 3, 4)),
    ("n * 2", (1, 5, 9)),
    ("n + 10", (0, 7, 20)),
    ("n // 2", (9, 21, 33)),
    ("n * 100", (1, 2, 3)),
    ("n - 5", (10, 20, 30)),
    ("n * n * n", (1, 2, 3)),
    ("n % 4", (7, 14, 21)),
    ("n + n", (6, 8, 10)),
    ("n * 7", (2, 4, 6)),
    ("n // 10", (55, 99, 120)),
    ("n + 1", (99, 199, 299)),
)

_P208 = _page(
    "async-gather",
    208,
    "Several at once, results in order",
    "asyncio.gather, and the guarantee it makes about order.",
    "gather starts all of them and waits for the lot, which is where "
    "async finally pays: three things that each wait on the network take "
    "as long as the slowest, not as long as all three added up. The "
    "guarantee worth knowing is that results come back in the order you "
    "passed the coroutines, never the order they finished - so you can "
    "match them up to what you asked for. Printing the whole list "
    "afterwards, rather than as they land, is the habit that keeps "
    "output readable.",
    "async_gather",
    [
        (
            "Import asyncio. Write an async def work(n) returning "
            + expr
            + ". Write an async def main() awaiting asyncio.gather of "
            "work called with "
            + ", ".join(repr(v) for v in values)
            + " into results, then printing results. Run it with "
            "asyncio.run.",
            {"expr": expr, "values": values},
        )
        for expr, values in _GATHERS
    ],
)


PROTOCOL_PAGES: tuple[Page, ...] = (
    _P199,
    _P200,
    _P201,
    _P202,
    _P203,
    _P204,
    _P205,
    _P206,
    _P207,
    _P208,
)
