"""Intermediate pages 141-148: the rest of a class, and errors you named.

Pages 101-110 built a class from __init__, methods and inheritance, and
stopped there. This is the rest of the thing: a property that looks like
a field from outside, methods that belong to the class rather than to
any one object, and the two dunders that let Python's own == and sorted
work on objects you wrote.

Then errors, properly. Page 98 caught one and page 99 raised one. Here
you give an error your own name, meet the else and finally that most
people never finish learning, and see one except catch a whole family.

Python only, same as 81-140.
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


# ── 141. A field that is really a method ─────────────────────

_PROPERTIES = (
    ("Box", (("width", 3), ("height", 4)), "area", "width * height"),
    ("Rect", (("side", 6), ("other", 5)), "perimeter", "2 * (side + other)"),
    ("Span", (("low", 4), ("high", 19)), "size", "high - low"),
    ("Grid", (("rows", 8), ("cols", 9)), "cells", "rows * cols"),
    ("Tank", (("full", 60), ("used", 22)), "left", "full - used"),
    ("Trip", (("miles", 120), ("hours", 3)), "speed", "miles // hours"),
    ("Score", (("points", 40), ("bonus", 7)), "final", "points + bonus"),
    ("Bill", (("price", 45), ("people", 3)), "share", "price // people"),
    ("Wall", (("bricks", 90), ("rows", 6)), "per_row", "bricks // rows"),
    ("Cube", (("side", 3), ("count", 2)), "volume", "side * side * side * count"),
    ("Pay", (("rate", 18), ("hours", 40)), "total", "rate * hours"),
    ("Gap", (("start", 7), ("end", 31)), "length", "end - start"),
    ("Plot", (("width", 9), ("depth", 7)), "area", "width * depth"),
    ("Field", (("side", 12), ("other", 8)), "perimeter", "2 * (side + other)"),
    ("Range", (("low", 11), ("high", 47)), "size", "high - low"),
    ("Board", (("rows", 6), ("cols", 7)), "cells", "rows * cols"),
    ("Barrel", (("full", 90), ("used", 34)), "left", "full - used"),
    ("Run", (("miles", 180), ("hours", 4)), "speed", "miles // hours"),
    ("Wage", (("rate", 22), ("hours", 35)), "total", "rate * hours"),
    ("Stack", (("bricks", 144), ("rows", 12)), "per_row", "bricks // rows"),
)

_P141 = _page(
    "property-use",
    141,
    "A field that is really a method",
    "@property: something you read like a field and compute like a method.",
    "thing.area with no brackets, and yet it ran code to answer. That is "
    "the whole trick, and the reason for it is that a caller should not "
    "have to know or care which of a thing's values are stored and which "
    "are worked out. Start with a plain field; the day it has to be "
    "calculated, a property changes it without touching a single line "
    "that used it. Note the method takes only self and you never call it "
    "with brackets - do, and you get the value's own brackets error.",
    "property_use",
    [
        (
            "Write a class "
            + cls
            + " whose __init__ takes and stores "
            + " and ".join(n for n, _ in fields)
            + ". Give it a property "
            + name
            + " returning "
            + expr
            + " using self for each. Make one called thing holding "
            + _seq([v for _, v in fields])
            + " and print thing."
            + name
            + " with no brackets.",
            {"cls": cls, "fields": fields, "name": name, "expr": expr},
        )
        for cls, fields, name, expr in _PROPERTIES
    ],
)


# ── 142. A method that needs no object ───────────────────────

_STATICS = (
    ("Maths", "add", ("a", "b"), "a + b", ((2, 3), (10, 4))),
    ("Maths", "times", ("a", "b"), "a * b", ((3, 4), (6, 7))),
    ("Convert", "double", ("n",), "n * 2", ((7,), (21,))),
    ("Convert", "half", ("n",), "n // 2", ((9,), (20,))),
    ("Tools", "biggest", ("a", "b"), "max(a, b)", ((4, 9), (12, 3))),
    ("Tools", "gap", ("a", "b"), "abs(a - b)", ((4, 9), (12, 3))),
    ("Shape", "area", ("w", "h"), "w * h", ((3, 4), (8, 5))),
    ("Shape", "around", ("w", "h"), "2 * (w + h)", ((3, 4), (8, 5))),
    ("Count", "rest", ("n", "d"), "n % d", ((17, 5), (20, 4))),
    ("Count", "share", ("n", "d"), "n // d", ((17, 5), (20, 4))),
    ("Money", "total", ("price", "many"), "price * many", ((7, 3), (12, 5))),
    ("Money", "change", ("paid", "cost"), "paid - cost", ((20, 13), (50, 41))),
    ("Maths", "plus", ("a", "b"), "a + b + 1", ((4, 5), (9, 1))),
    ("Maths", "scale", ("a", "b"), "a * b * 2", ((2, 5), (3, 3))),
    ("Convert", "triple", ("n",), "n * 3", ((8,), (14,))),
    ("Convert", "third", ("n",), "n // 3", ((9,), (20,))),
    ("Tools", "smallest", ("a", "b"), "min(a, b)", ((4, 9), (12, 3))),
    ("Tools", "spread", ("a", "b"), "abs(b - a)", ((3, 11), (20, 4))),
    ("Count", "wrap", ("n", "d"), "n % d", ((23, 6), (41, 5))),
    ("Money", "each", ("price", "many"), "price // many", ((90, 4), (25, 5))),
)

_P142 = _page(
    "static-method",
    142,
    "A method that needs no object",
    "@staticmethod: a function that lives in a class for tidiness.",
    "No self, and you call it on the class itself rather than on a thing "
    "you made. It is a plain function that happens to live inside a class "
    "because that is where a reader will look for it. If you find "
    "yourself writing self and never using it, this is what you wanted. "
    "And if a class is nothing but static methods, what you actually "
    "wanted was a module - the class is doing no work.",
    "static_method",
    [
        (
            "Write a class "
            + cls
            + " with a staticmethod "
            + name
            + " taking "
            + " and ".join(params)
            + " and returning "
            + expr
            + ". Print the result of calling it on the class with "
            + ", then ".join("(" + ", ".join(repr(v) for v in c) + ")" for c in calls)
            + ".",
            {
                "cls": cls,
                "name": name,
                "params": params,
                "expr": expr,
                "calls": calls,
            },
        )
        for cls, name, params, expr, calls in _STATICS
    ],
)


# ── 143. A method that belongs to the class ──────────────────

_COUNTERS = (
    ("Widget", "how_many", 0, 3),
    ("Robot", "built", 0, 5),
    ("Ticket", "issued", 0, 2),
    ("Session", "opened", 0, 4),
    ("Node", "count", 0, 6),
    ("Card", "dealt", 0, 1),
    ("Job", "queued", 10, 3),
    ("User", "signed_up", 100, 2),
    ("Order", "placed", 0, 7),
    ("File", "created", 5, 4),
    ("Task", "started", 0, 8),
    ("Guest", "arrived", 20, 3),
    ("Gadget", "how_many", 0, 4),
    ("Drone", "built", 0, 6),
    ("Pass", "issued", 0, 3),
    ("Link", "opened", 0, 5),
    ("Leaf", "count", 0, 7),
    ("Hand", "dealt", 0, 2),
    ("Batch", "queued", 25, 4),
    ("Member", "signed_up", 200, 3),
)

_P143 = _page(
    "class-counter",
    143,
    "A method that belongs to the class",
    "@classmethod, and cls as the thing it is handed.",
    "Page 107 put a value on the class so every object shared it. A "
    "classmethod is the other half: a method handed the class rather "
    "than an object, so it can read and change that shared value without "
    "anyone having made a single thing yet. Notice __init__ counting up "
    "as each one is built, and the classmethod reporting the total "
    "afterwards. cls is to the class what self is to the object - and it "
    "is only a name, but calling it anything else will get you funny "
    "looks.",
    "class_counter",
    [
        (
            "Write a class "
            + cls
            + " with a class attribute made set to "
            + repr(start)
            + ", an __init__ that adds one to "
            + cls
            + ".made, and a classmethod "
            + name
            + " taking cls that returns cls.made. Build "
            + str(times)
            + " of them, then print "
            + cls
            + "."
            + name
            + "().",
            {"cls": cls, "name": name, "start": start, "times": times},
        )
        for cls, name, start, times in _COUNTERS
    ],
)


# ── 144. Teaching == what equal means ────────────────────────

_EQUALS = (
    ("Point", (("x", "int"), ("y", "int")), (2, 3), (2, 3)),
    ("Point", (("x", "int"), ("y", "int")), (2, 3), (2, 4)),
    ("Size", (("width", "int"), ("height", "int")), (10, 4), (10, 4)),
    ("Size", (("width", "int"), ("height", "int")), (10, 4), (4, 10)),
    ("Pair", (("left", "int"), ("right", "int")), (7, 8), (7, 8)),
    ("Pair", (("left", "int"), ("right", "int")), (7, 8), (8, 7)),
    ("Card", (("suit", "str"), ("rank", "int")), ("spades", 11), ("spades", 11)),
    ("Card", (("suit", "str"), ("rank", "int")), ("spades", 11), ("hearts", 11)),
    ("Room", (("floor", "int"), ("number", "int")), (3, 12), (3, 12)),
    ("Room", (("floor", "int"), ("number", "int")), (3, 12), (2, 12)),
    ("Coin", (("face", "str"), ("worth", "int")), ("heads", 25), ("heads", 25)),
    ("Coin", (("face", "str"), ("worth", "int")), ("heads", 25), ("tails", 25)),
    ("Coord", (("x", "int"), ("y", "int")), (7, 9), (7, 9)),
    ("Coord", (("x", "int"), ("y", "int")), (7, 9), (7, 8)),
    ("Extent", (("width", "int"), ("height", "int")), (64, 48), (64, 48)),
    ("Extent", (("width", "int"), ("height", "int")), (64, 48), (48, 64)),
    ("Duo", (("left", "int"), ("right", "int")), (11, 12), (11, 12)),
    ("Duo", (("left", "int"), ("right", "int")), (11, 12), (12, 11)),
    ("Note", (("pitch", "str"), ("octave", "int")), ("C", 4), ("C", 4)),
    ("Note", (("pitch", "str"), ("octave", "int")), ("C", 4), ("G", 4)),
)

_P144 = _page(
    "eq-dunder",
    144,
    "Teaching == what equal means",
    "__eq__, so two separate objects can count as the same value.",
    "Without __eq__, == on two objects asks whether they are the same "
    "object, so two points at (2, 3) come out unequal, which is almost "
    "never what you meant. Writing it says what equal means for your "
    "thing. Watch both lines: == becomes True and `is` stays False, "
    "because they are still two objects - the same distinction page 112 "
    "made, now under your control. A dataclass writes this for you, which "
    "is the other reason to reach for one.",
    "eq_dunder",
    [
        (
            "Write a class "
            + cls
            + " whose __init__ takes and stores "
            + " and ".join(n for n, _ in fields)
            + ", and an __eq__ taking other that returns whether every "
            "field matches. Make first holding "
            + _seq(left)
            + " and second holding "
            + _seq(right)
            + ". Print first == second, then first is second.",
            {"cls": cls, "fields": fields, "left": left, "right": right},
        )
        for cls, fields, left, right in _EQUALS
    ],
)


# ── 145. Teaching sorted how to order them ───────────────────

_ORDERS = (
    ("Player", "score", (("ada", 90), ("sam", 7), ("kim", 41))),
    ("City", "people", (("kyoto", 1463), ("oslo", 709), ("lima", 998))),
    ("Book", "pages", (("dune", 412), ("ilium", 780), ("solaris", 204))),
    ("Song", "seconds", (("alive", 245), ("heroes", 371), ("kooks", 173))),
    ("Runner", "minutes", (("ann", 31), ("bo", 27), ("cal", 44))),
    ("Metal", "number", (("iron", 26), ("gold", 79), ("tin", 50))),
    ("Room", "floor", (("attic", 4), ("cellar", 0), ("hall", 1))),
    ("Tool", "weight", (("saw", 3), ("axe", 8), ("file", 1))),
    ("Fruit", "count", (("apple", 3), ("pear", 12), ("fig", 7))),
    ("Task", "order", (("mix", 2), ("bake", 3), ("weigh", 1))),
    ("Team", "points", (("reds", 41), ("blues", 12), ("greens", 30))),
    ("Word", "length", (("sky", 3), ("mountain", 8), ("lake", 4))),
    ("Runner", "place", (("finn", 3), ("kit", 1), ("ida", 2))),
    ("Town", "people", (("ripon", 17), ("oslo", 709), ("lima", 998))),
    ("Album", "tracks", (("low", 11), ("heroes", 10), ("lodger", 13))),
    ("Track", "seconds", (("warszawa", 386), ("art", 224), ("sons", 207))),
    ("Metal", "melting", (("tin", 232), ("lead", 327), ("gold", 1064))),
    ("Crate", "depth", (("small", 5), ("wide", 50), ("tall", 20))),
    ("Fruit", "count", (("kiwi", 5), ("plum", 21), ("sloe", 9))),
    ("Note", "octave", (("low", 2), ("mid", 4), ("high", 6))),
)

_P145 = _page(
    "lt-dunder",
    145,
    "Teaching sorted how to order them",
    "__lt__, and why sorted then works with no key at all.",
    "sorted does not know how to order things you invented, and says so. "
    "Give the class a __lt__ saying which of two comes first and sorted "
    "works with nothing else added - so do min, max, and the < operator. "
    "One small method, and a pile of built-in machinery starts "
    "cooperating. That is the pattern behind every dunder: you are not "
    "adding a method for callers, you are answering a question Python "
    "already knows how to ask.",
    "lt_dunder",
    [
        (
            "Write a class "
            + cls
            + " whose __init__ takes and stores name and "
            + by
            + ", and a __lt__ taking other that returns whether self."
            + by
            + " is less than other."
            + by
            + ". Build a list of "
            + ", ".join(f"({n!r}, {v!r})" for n, v in things)
            + " as "
            + cls
            + " objects, then loop over sorted of that list printing each "
            "name.",
            {"cls": cls, "by": by, "things": things},
        )
        for cls, by, things in _ORDERS
    ],
)


# ── 146. An error with your own name on it ───────────────────

_CUSTOM = (
    ("TooSmall", "n < 10", "too small", (12, 4, 30)),
    ("TooBig", "n > 100", "too big", (50, 200, 99)),
    ("NotEven", "n % 2 == 1", "not even", (4, 7, 10)),
    ("Negative", "n < 0", "negative", (5, -3, 8)),
    ("ZeroFound", "n == 0", "zero found", (3, 0, 9)),
    ("TooLong", "n > 20", "too long", (15, 44, 2)),
    ("Underflow", "n < 1", "underflow", (6, 0, 11)),
    ("OddOne", "n % 2 == 1", "odd one", (2, 5, 8)),
    ("OutOfRange", "n > 60", "out of range", (12, 90, 33)),
    ("Empty", "n == 0", "empty", (7, 0, 1)),
    ("Overflow", "n > 255", "overflow", (200, 300, 10)),
    ("BadStep", "n % 5 == 0", "bad step", (3, 10, 7)),
    ("TooFew", "n < 5", "too few", (9, 2, 40)),
    ("TooMany", "n > 200", "too many", (80, 400, 150)),
    ("NotOdd", "n % 2 == 0", "not odd", (7, 8, 11)),
    ("BelowZero", "n < 0", "below zero", (4, -6, 12)),
    ("NothingLeft", "n == 0", "nothing left", (5, 0, 14)),
    ("TooWide", "n > 30", "too wide", (18, 55, 7)),
    ("NotThirds", "n % 3 != 0", "not a third", (9, 7, 12)),
    ("PastLimit", "n > 500", "past the limit", (300, 900, 20)),
)

_P146 = _page(
    "custom-error",
    146,
    "An error with your own name on it",
    "Writing an exception class, raising it, and printing what it said.",
    "class Whatever(Exception): pass is a complete, working exception "
    "type - there is genuinely nothing else to write. The value of it is "
    "that callers can catch exactly your problem and nothing else, which "
    "a bare ValueError will never let them do. The message you hand it "
    "comes back when you print the caught object, so say something the "
    "person reading the output can act on.",
    "custom_error",
    [
        (
            "Write an exception class "
            + error
            + " with nothing in it but pass. Write check(n) that raises "
            + error
            + " with the message "
            + repr(message)
            + " if "
            + cond
            + ", and otherwise returns n. Loop n over ["
            + _seq(values)
            + "], printing check(n) inside a try and printing the caught "
            "problem in an except for "
            + error
            + ".",
            {
                "error": error,
                "cond": cond,
                "message": message,
                "values": values,
            },
        )
        for error, cond, message, values in _CUSTOM
    ],
)


# ── 147. The two halves of try most people skip ──────────────

_FINALLY = (
    ("100 // n", "ZeroDivisionError", "cannot divide", "done", (5, 0, 2)),
    ("60 // n", "ZeroDivisionError", "no good", "finished", (3, 0, 6)),
    ("144 // n", "ZeroDivisionError", "divide by zero", "next", (12, 0, 4)),
    ("90 // n", "ZeroDivisionError", "bad divisor", "always", (9, 0, 3)),
    ("50 // n", "ZeroDivisionError", "cannot", "closed", (5, 0, 10)),
    ("81 // n", "ZeroDivisionError", "nope", "tidy", (9, 0, 27)),
    ("64 // n", "ZeroDivisionError", "no divide", "cleanup", (8, 0, 16)),
    ("21 // n", "ZeroDivisionError", "zero given", "over", (7, 0, 3)),
    ("36 // n", "ZeroDivisionError", "cannot divide", "end", (6, 0, 12)),
    ("77 // n", "ZeroDivisionError", "not possible", "after", (7, 0, 11)),
    ("30 // n", "ZeroDivisionError", "no", "shut", (5, 0, 6)),
    ("48 // n", "ZeroDivisionError", "divide failed", "released", (4, 0, 8)),
    ("120 // n", "ZeroDivisionError", "cannot divide", "done", (6, 0, 4)),
    ("45 // n", "ZeroDivisionError", "no good", "finished", (5, 0, 9)),
    ("169 // n", "ZeroDivisionError", "divide by zero", "next", (13, 0, 1)),
    ("72 // n", "ZeroDivisionError", "bad divisor", "always", (8, 0, 6)),
    ("55 // n", "ZeroDivisionError", "cannot", "closed", (5, 0, 11)),
    ("96 // n", "ZeroDivisionError", "nope", "tidy", (12, 0, 8)),
    ("32 // n", "ZeroDivisionError", "no divide", "cleanup", (4, 0, 16)),
    ("63 // n", "ZeroDivisionError", "zero given", "over", (7, 0, 9)),
)

_P147 = _page(
    "try-else-finally",
    147,
    "The two halves of try most people skip",
    "else runs when nothing went wrong; finally runs either way.",
    "Most people learn try and except and stop. else holds the code that "
    "should run only when the try succeeded - keeping it out of the try "
    "means an error raised by that code is not caught by mistake, which "
    "is a genuinely nasty bug to find. finally runs whatever happened, "
    "error or not, which is where closing and releasing belongs. Watch "
    "the middle value in each: the failure line prints, then the finally "
    "line prints anyway.",
    "try_else_finally",
    [
        (
            "Loop n over ["
            + _seq(values)
            + "]. Inside, try setting result to "
            + expr
            + "; on "
            + error
            + " print "
            + repr(failed)
            + "; in an else print result; in a finally print "
            + repr(always)
            + ".",
            {
                "expr": expr,
                "error": error,
                "failed": failed,
                "always": always,
                "values": values,
            },
        )
        for expr, error, failed, always, values in _FINALLY
    ],
)


# ── 148. One except catching a whole family ──────────────────

_FAMILIES = (
    ("Problem", "Worse", "n < 0", "n == 0", "caught Worse", "caught Problem",
     (5, 0, -1)),
    ("Fault", "Fatal", "n < -10", "n < 0", "fatal", "fault", (3, -2, -20)),
    ("BadInput", "Empty", "n == 0", "n < 5", "empty", "bad input", (9, 2, 0)),
    ("Failure", "Crash", "n > 100", "n > 50", "crash", "failure", (10, 60, 200)),
    ("Trouble", "Disaster", "n % 10 == 0", "n % 2 == 0", "disaster",
     "trouble", (3, 4, 10)),
    ("Issue", "Blocker", "n < -5", "n < 0", "blocker", "issue", (1, -1, -9)),
    ("Error", "Severe", "n > 90", "n > 40", "severe", "error", (5, 50, 95)),
    ("Warn", "Alarm", "n == 13", "n % 13 == 0", "alarm", "warn", (5, 26, 13)),
    ("Snag", "Halt", "n < -3", "n < 3", "halt", "snag", (7, 1, -8)),
    ("Glitch", "Meltdown", "n > 999", "n > 99", "meltdown", "glitch",
     (12, 150, 1200)),
    ("Miss", "Gone", "n == -1", "n < 0", "gone", "miss", (4, -2, -1)),
    ("Slip", "Fall", "n < -100", "n < -1", "fall", "slip", (2, -5, -200)),
    ("Problem", "Grave", "n < -20", "n < 0", "grave", "problem", (4, -3, -30)),
    ("Fault", "Broken", "n > 500", "n > 200", "broken", "fault", (10, 300, 900)),
    ("BadInput", "Blank", "n == 0", "n < 3", "blank", "bad input", (8, 1, 0)),
    ("Failure", "Ruin", "n > 1000", "n > 100", "ruin", "failure",
     (50, 400, 2000)),
    ("Trouble", "Crisis", "n % 20 == 0", "n % 5 == 0", "crisis", "trouble",
     (3, 15, 40)),
    ("Issue", "Stopper", "n < -50", "n < -10", "stopper", "issue",
     (2, -20, -80)),
    ("Warn", "Siren", "n == 7", "n % 7 == 0", "siren", "warn", (3, 14, 7)),
    ("Snag", "Jam", "n > 90", "n > 60", "jam", "snag", (10, 70, 95)),
)

_P148 = _page(
    "error-hierarchy",
    148,
    "One except catching a whole family",
    "An exception that inherits, and why except order matters.",
    "An except catches its own type and everything that inherits from "
    "it, which is why except Exception catches nearly everything and why "
    "you should almost never write it. Give your errors a common base and "
    "a caller can choose their level - catch the specific one, or catch "
    "the family. The ordering is the trap: Python takes the first except "
    "that matches, so the specific one must come first. Put the base "
    "first and the specific block below it can never run, and Python will "
    "not warn you.",
    "error_hierarchy",
    [
        (
            "Write an exception class "
            + base
            + ", then "
            + sub
            + " inheriting from it, both with just pass. Write check(n) "
            "raising "
            + sub
            + " if "
            + worse
            + ", raising "
            + base
            + " if "
            + bad
            + ", otherwise returning n. Loop n over ["
            + _seq(values)
            + "] printing check(n) in a try, with an except for "
            + sub
            + " printing "
            + repr(sub_label)
            + " before an except for "
            + base
            + " printing "
            + repr(base_label)
            + ".",
            {
                "base": base,
                "sub": sub,
                "worse": worse,
                "bad": bad,
                "sub_label": sub_label,
                "base_label": base_label,
                "values": values,
            },
        )
        for base, sub, worse, bad, sub_label, base_label, values in _FAMILIES
    ],
)


ADVANCED_PAGES: tuple[Page, ...] = (
    _P141,
    _P142,
    _P143,
    _P144,
    _P145,
    _P146,
    _P147,
    _P148,
)
