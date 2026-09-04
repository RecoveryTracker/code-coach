"""JavaScript intermediate pages 91-100: objects, classes, and the traps.

Methods and this. Classes. Promises and await. throw and catch. for...of
against Object.entries. Then the three that catch everyone: sort
comparing numbers as text unless you tell it not to, JSON round trips,
and the two kinds of nothing.

Page 96 is the one to read twice. [10, 9, 100].sort() gives 10, 100, 9,
because the default comparison turns everything into a string first -
and it is not a bug, it is documented, and it has bitten every
JavaScript programmer at least once.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

JAVASCRIPT = ("javascript",)


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
        languages=JAVASCRIPT,
        tier="intermediate",
    )


def _seq(items) -> str:
    return ", ".join(str(v) for v in items)


# ── 91. An object with a function in it ──────────────────────

_METHODS = (
    ("box", "width", 5, "area", 3),
    ("tank", "litres", 60, "doubled", 2),
    ("shelf", "books", 7, "stacked", 4),
    ("plot", "metres", 12, "scaled", 3),
    ("batch", "items", 9, "packed", 5),
    ("wall", "bricks", 90, "rows", 2),
    ("trip", "miles", 40, "returned", 2),
    ("bill", "pence", 45, "shared", 3),
    ("grid", "rows", 8, "cells", 9),
    ("song", "seconds", 30, "repeats", 4),
    ("card", "rank", 11, "worth", 10),
    ("team", "players", 11, "squads", 3),
    ("crate", "depth", 8, "volume", 4),
    ("barrel", "litres", 90, "tripled", 3),
    ("rack", "books", 11, "stacked", 5),
    ("field", "metres", 25, "scaled", 4),
    ("pallet", "items", 14, "packed", 6),
    ("stack", "bricks", 144, "rows", 12),
    ("run", "miles", 60, "returned", 2),
    ("tab", "pence", 96, "shared", 8),
)

_P91 = _page(
    "js-object-method",
    91,
    "An object with a function in it",
    "A method, and what this refers to.",
    "An object can hold a function as easily as a number, and inside it "
    "this means the object the method was called on. That last part is "
    "the important bit and the source of endless trouble: this is "
    "decided by how the function is called, not where it was written, so "
    "pulling a method out into a variable and calling it later loses "
    "the object. An arrow function does not get its own this, which is "
    "why an arrow is wrong here and right inside a callback.",
    "js_object_method",
    [
        (
            "Set "
            + name
            + " to a const object with "
            + field
            + " of "
            + str(v)
            + " and a method "
            + method
            + " that returns this."
            + field
            + " times "
            + str(times)
            + ". Log the "
            + field
            + ", then the result of calling the method.",
            {
                "name": name,
                "field": field,
                "value": v,
                "method": method,
                "times": times,
            },
        )
        for name, field, v, method, times in _METHODS
    ],
)


# ── 92. A class, and the word new ────────────────────────────

_CLASSES = (
    ("Box", "width", "height", (3, 4), "area"),
    ("Grid", "rows", "cols", (8, 9), "cells"),
    ("Trip", "miles", "trips", (40, 3), "total"),
    ("Wall", "rows", "bricks", (6, 15), "count"),
    ("Batch", "packs", "each", (5, 12), "items"),
    ("Room", "length", "width", (7, 5), "floor"),
    ("Bill", "price", "people", (45, 3), "whole"),
    ("Sheet", "lines", "words", (10, 8), "size"),
    ("Deck", "suits", "ranks", (4, 13), "cards"),
    ("Shelf", "levels", "books", (3, 20), "stock"),
    ("Field", "long_side", "short_side", (30, 20), "area"),
    ("Crate", "layers", "boxes", (4, 6), "holds"),
    ("Plot", "width", "depth", (9, 7), "area"),
    ("Board", "rows", "cols", (6, 7), "cells"),
    ("Run", "miles", "laps", (60, 4), "total"),
    ("Stack", "rows", "bricks", (12, 12), "count"),
    ("Pallet", "packs", "each", (7, 9), "items"),
    ("Hall", "length", "width", (20, 15), "floor"),
    ("Tab", "price", "people", (96, 8), "whole"),
    ("Page", "lines", "words", (24, 9), "size"),
)

_P92 = _page(
    "js-class",
    92,
    "A class, and the word new",
    "class, constructor, and methods on the prototype.",
    "The syntax looks like other languages and the machinery underneath "
    "is not: a JavaScript class is a nicer way of writing the prototype "
    "system that was always there, and methods live on the prototype "
    "rather than on each object. That mostly does not matter until it "
    "does. What matters now is that new builds an object, constructor "
    "fills it in, and forgetting new is an error rather than something "
    "that quietly half-works.",
    "js_class",
    [
        (
            "Write a class "
            + cls
            + " whose constructor takes "
            + first
            + " and "
            + second
            + " and stores both on this, and a method "
            + method
            + " returning the two multiplied. Make thing with new and "
            + _seq(values)
            + ". Log thing."
            + first
            + ", then the method's result.",
            {
                "cls": cls,
                "first": first,
                "second": second,
                "values": values,
                "method": method,
            },
        )
        for cls, first, second, values, method in _CLASSES
    ],
)


# ── 93. Waiting for something that is not ready ──────────────

_ASYNCS = (
    ("work", 2, (3, 5)),
    ("fetchIt", 10, (1, 2)),
    ("load", 3, (4, 6)),
    ("compute", 5, (2, 8)),
    ("scale", 4, (7, 9)),
    ("double", 2, (11, 12)),
    ("triple", 3, (5, 10)),
    ("expand", 6, (2, 3)),
    ("grow", 7, (1, 4)),
    ("stretch", 8, (2, 5)),
    ("boost", 9, (3, 6)),
    ("lift", 100, (1, 2)),
    ("gather", 2, (6, 7)),
    ("readIt", 3, (2, 5)),
    ("prepare", 4, (8, 9)),
    ("resolve", 1, (3, 12)),
    ("widen", 5, (4, 11)),
    ("quadruple", 2, (13, 14)),
    ("shrink", 6, (7, 8)),
    ("settle", 3, (9, 10)),
)

_P93 = _page(
    "js-async",
    93,
    "Waiting for something that is not ready",
    "async, await, and Promise.all.",
    "An async function always returns a promise, even when its body "
    "returns a plain number - which is why the caller has to await it. "
    "await unwraps one, and it can only be used inside an async "
    "function, which is why there is a main here at all. The last part "
    "matters most: awaiting two things one after the other takes as long "
    "as both, while Promise.all starts them together and takes as long "
    "as the slower. Results come back in the order you asked, not the "
    "order they finished.",
    "js_async",
    [
        (
            "Write an async function "
            + name
            + "(n) returning n times "
            + str(times)
            + ". Write an async main that awaits it for "
            + str(values[0])
            + " into first and "
            + str(values[1])
            + " into second, logging each. Then await Promise.all of the "
            "same two calls into both, and log both joined with ', '. "
            "Call main.",
            {"name": name, "times": times, "values": values},
        )
        for name, times, values in _ASYNCS
    ],
)


# ── 94. Throwing something and catching it ───────────────────

_THROWS = (
    ("n < 0", "negative", (5, -3, 8)),
    ("n == 0", "zero found", (3, 0, 9)),
    ("n > 100", "too big", (50, 200, 99)),
    ("n % 2 == 1", "not even", (4, 7, 10)),
    ("n < 10", "too small", (12, 4, 30)),
    ("n > 60", "out of range", (12, 90, 33)),
    ("n == 13", "unlucky", (5, 13, 8)),
    ("n < 1", "underflow", (6, 0, 11)),
    ("n > 255", "overflow", (200, 300, 10)),
    ("n % 5 == 0", "bad step", (3, 10, 7)),
    ("n < -5", "far too low", (1, -9, 2)),
    ("n > 1000", "enormous", (10, 2000, 30)),
    ("n < -20", "far below", (4, -30, 9)),
    ("n == 7", "seven is out", (3, 7, 11)),
    ("n > 500", "much too big", (100, 900, 400)),
    ("n % 2 == 0", "not odd", (7, 8, 13)),
    ("n < 5", "too few", (9, 2, 40)),
    ("n > 30", "too wide", (18, 55, 22)),
    ("n % 3 == 0", "thirds not allowed", (4, 9, 11)),
    ("n > 999", "past the limit", (50, 1500, 300)),
)

_P94 = _page(
    "js-throw-catch",
    94,
    "Throwing something and catching it",
    "throw new Error, and reading problem.message.",
    "JavaScript lets you throw any value at all - a string, a number, "
    "anything - and you should throw an Error anyway, because an Error "
    "carries a stack trace and a string does not. Catching gets you the "
    "thrown thing, and .message is the text you gave it. Note there is "
    "no way to catch only one kind, as page 148 did in the other book: "
    "you catch everything and then check what you got.",
    "js_throw_catch",
    [
        (
            "Write check(n) that throws a new Error "
            + repr(message)
            + " when "
            + test.replace("==", "===")
            + ", and otherwise returns n. Loop n over ["
            + _seq(values)
            + "] with for...of, logging check(n) in a try and the caught "
            "problem's message in a catch.",
            {"test": test, "message": message, "values": values},
        )
        for test, message, values in _THROWS
    ],
)


# ── 95. Walking an object's keys and values ──────────────────

_ENTRIES = (
    (("ada", 90), ("sam", 7), ("kim", 41)),
    (("red", 12), ("blue", 9), ("green", 30)),
    (("mon", 8), ("tue", 6), ("wed", 7)),
    (("iron", 26), ("gold", 79)),
    (("north", 6), ("south", 19), ("east", 1)),
    (("apple", 3), ("pear", 12), ("fig", 7)),
    (("saw", 3), ("axe", 8)),
    (("sky", 3), ("sea", 3), ("sun", 9)),
    (("one", 1), ("two", 2), ("six", 6)),
    (("salt", 11), ("pepper", 22)),
    (("front", 4), ("back", 55), ("side", 20)),
    (("do", 1), ("re", 2), ("mi", 3)),
    (("finn", 82), ("kit", 4), ("ida", 37)),
    (("gold", 19), ("tin", 7), ("lead", 30)),
    (("thu", 5), ("fri", 9), ("sat", 4)),
    (("oak", 12), ("ash", 31)),
    (("up", 6), ("down", 21), ("across", 2)),
    (("kiwi", 5), ("plum", 21), ("sloe", 9)),
    (("saw", 4), ("plane", 7)),
    (("la", 6), ("ti", 14), ("do", 2)),
)

_P95 = _page(
    "js-for-of",
    95,
    "Walking an object's keys and values",
    "Object.entries with for...of, and destructuring in the loop.",
    "for...of walks values; for...in walks keys and also picks up "
    "inherited ones, which is why it is almost never what you want. "
    "Object.entries turns an object into an array of [key, value] pairs, "
    "and destructuring in the loop header pulls them apart in the same "
    "line. Object.keys and Object.values are the other two, and modern "
    "JavaScript keeps string keys in insertion order, so the output is "
    "the order you wrote them.",
    "js_for_of",
    [
        (
            "Set scores to a const object of "
            + ", ".join(f"{k}: {v}" for k, v in pairs)
            + ". Loop over Object.entries of it with for...of, "
            "destructuring name and score, and log a template literal of "
            "both. Then log Object.keys joined with ', '.",
            {"pairs": pairs},
        )
        for pairs in _ENTRIES
    ],
)


# ── 96. Sorting numbers, which needs telling ─────────────────

_SORTS = (
    (10, 9, 100),
    (2, 10, 1),
    (5, 40, 300),
    (9, 80, 700),
    (1, 20, 3),
    (11, 2, 30),
    (7, 70, 8),
    (4, 44, 400),
    (6, 60, 7),
    (12, 3, 120),
    (8, 90, 100),
    (15, 2, 150),
    (20, 3, 100),
    (9, 80, 1000),
    (5, 50, 6),
    (2, 19, 200),
    (30, 4, 300),
    (6, 60, 9),
    (13, 2, 130),
    (14, 5, 140),
)

_P96 = _page(
    "js-sort-numbers",
    96,
    "Sorting numbers, which needs telling",
    "Why sort() alone is wrong, and the compare function that fixes it.",
    "sort with no arguments turns every item into a string and sorts "
    "those, so 10 comes before 9 because '1' comes before '9'. That is "
    "documented behaviour, not a bug, and it is the single most "
    "surprising thing in the language for someone arriving from "
    "elsewhere. The fix is a compare function returning a negative "
    "number, zero or a positive one - so (a, b) => a - b sorts upward "
    "and b - a sorts down. Note sort changes the array in place, which "
    "is why each line here sorts a fresh copy.",
    "js_sort_numbers",
    [
        (
            "Set numbers to ["
            + _seq(items)
            + "], const. Log a copy of it sorted with no compare function "
            "and joined with ', '. Then a copy sorted with a compare "
            "function that subtracts b from a, joined. Then one sorted "
            "the other way round, joined.",
            {"items": items},
        )
        for items in _SORTS
    ],
)


# ── 97. An object turned into text and back ──────────────────

_JSONS = (
    (("name", "ada"), ("age", 36)),
    (("city", "kyoto"), ("people", 1463)),
    (("metal", "iron"), ("number", 26)),
    (("book", "dune"), ("pages", 412)),
    (("song", "alive"), ("seconds", 245)),
    (("team", "reds"), ("points", 41)),
    (("tool", "saw"), ("weight", 3)),
    (("room", "attic"), ("floor", 4)),
    (("word", "sky"), ("length", 3)),
    (("trip", "north"), ("miles", 120)),
    (("task", "mix"), ("order", 2)),
    (("user", "sam"), ("score", 90)),
    (("name", "finn"), ("age", 27)),
    (("city", "oslo"), ("people", 709)),
    (("metal", "tin"), ("number", 50)),
    (("book", "ubik"), ("pages", 224)),
    (("song", "art"), ("seconds", 224)),
    (("team", "blues"), ("points", 12)),
    (("tool", "plane"), ("weight", 7)),
    (("word", "moon"), ("length", 4)),
)

_P97 = _page(
    "js-json",
    97,
    "An object turned into text and back",
    "JSON.stringify and JSON.parse, and what does not survive.",
    "stringify turns an object into text and parse turns it back, which "
    "is how data crosses every network boundary you will meet. What does "
    "not survive is worth knowing early: functions and undefined are "
    "dropped entirely, a Date becomes a string and stays a string on the "
    "way back, and Map and Set come out as empty objects. So a round "
    "trip gives you plain data, never the same objects - which is also "
    "the cheap way to deep copy something made only of plain data.",
    "js_json",
    [
        (
            "Set data to a const object of "
            + ", ".join(f"{k}: {v!r}" for k, v in pairs)
            + ". Set text to JSON.stringify of it and back to JSON.parse "
            "of text. Log text, then back."
            + pairs[0][0]
            + ", then whether text equals JSON.stringify of back.",
            {"pairs": pairs},
        )
        for pairs in _JSONS
    ],
)


# ── 98. A function that remembers ────────────────────────────

_CLOSURES = (
    (0, (3, 4)),
    (10, (1, 2)),
    (100, (5, 5)),
    (0, (10, 20, 30)),
    (5, (5, 5, 5)),
    (50, (25, 25)),
    (1, (1, 1, 1)),
    (0, (7, 8)),
    (20, (2, 3, 4)),
    (0, (100, 200)),
    (7, (7, 7)),
    (0, (1, 2, 3, 4)),
    (0, (6, 7)),
    (20, (3, 4)),
    (200, (10, 10)),
    (0, (15, 25, 35)),
    (9, (9, 9, 9)),
    (75, (12, 13)),
    (2, (2, 2, 2)),
    (0, (11, 12, 13, 14)),
)

_P98 = _page(
    "js-closure",
    98,
    "A function that remembers",
    "A closure over a let, and the state it keeps.",
    "The inner function keeps hold of total after make has returned, so "
    "each call carries on from where the last one left off. That is a "
    "closure, and it is how JavaScript did private state for twenty "
    "years before classes had it. Two of them made from the same "
    "function do not share anything - each call to make creates its own "
    "total, which is the part worth checking your understanding "
    "against.",
    "js_closure",
    [
        (
            "Write make(start) that sets a let total to start and returns "
            "a function taking n which adds n to total and returns it. "
            "Set add to make("
            + str(start)
            + "), then log add called with "
            + " and then ".join(str(n) for n in adds)
            + ".",
            {"start": start, "adds": adds},
        )
        for start, adds in _CLOSURES
    ],
)


# ── 99. The two kinds of nothing ─────────────────────────────

_NOTHINGS = (
    ("ada", "middleName", "age"),
    ("sam", "nickname", "score"),
    ("kim", "title", "rank"),
    ("jo", "suffix", "level"),
    ("max", "alias", "count"),
    ("eve", "handle", "total"),
    ("abe", "prefix", "size"),
    ("ida", "label", "weight"),
    ("ben", "tag", "height"),
    ("rey", "note", "depth"),
    ("finn", "code", "width"),
    ("nell", "mark", "length"),
    ("gus", "middleName", "age"),
    ("hal", "nickname", "score"),
    ("ivy", "title", "rank"),
    ("jan", "suffix", "level"),
    ("kit", "alias", "count"),
    ("lee", "handle", "total"),
    ("mia", "prefix", "size"),
    ("noa", "label", "weight"),
)

_P99 = _page(
    "js-null-undefined",
    99,
    "The two kinds of nothing",
    "null against undefined, and == against ===.",
    "undefined means nobody ever set it; null means somebody set it to "
    "nothing on purpose. Keeping that distinction is the whole reason "
    "both exist. Now the third and fourth lines: null == undefined is "
    "true, because loose equality converts before comparing, and null "
    "=== undefined is false, because strict equality checks the type "
    "first. That gap is why the rule is to use === everywhere, with one "
    "famous exception - x == null is a neat way to catch both at once.",
    "js_null_undefined",
    [
        (
            "Set missing to a const object with name "
            + repr(name)
            + " and "
            + field
            + " set to null. Log whether "
            + field
            + " is strictly null, then whether "
            + absent
            + " is strictly undefined, then the two compared with double "
            "equals, then with triple equals.",
            {"name": name, "field": field, "absent": absent},
        )
        for name, field, absent in _NOTHINGS
    ],
)


# ── 100. Asking an array a question ──────────────────────────

_QUESTIONS = (
    ((1, 2, 3, 4, 5, 6), "n % 2 == 0", 3),
    ((5, 10, 15, 20), "n > 12", 10),
    ((1, 3, 5, 8, 9), "n % 2 == 0", 5),
    ((2, 4, 7, 8), "n % 2 == 1", 4),
    ((10, 20, 25, 30), "n % 10 == 5", 20),
    ((1, 2, 3, 100), "n > 50", 2),
    ((7, 14, 15, 21), "n % 7 == 0", 15),
    ((3, 6, 7, 9), "n % 3 == 0", 7),
    ((11, 22, 23, 44), "n % 11 == 0", 23),
    ((2, 3, 5, 6), "n % 2 == 0", 5),
    ((4, 8, 9, 16), "n % 4 == 0", 9),
    ((1, 5, 10, 12), "n >= 10", 5),
    ((2, 4, 5, 8, 10, 12), "n % 2 == 0", 5),
    ((6, 12, 18, 24), "n > 15", 9),
    ((3, 7, 9, 12, 13), "n % 2 == 0", 8),
    ((5, 9, 12, 15), "n % 2 == 1", 6),
    ((15, 25, 30, 45), "n % 15 == 0", 22),
    ((2, 3, 4, 200), "n > 100", 7),
    ((8, 16, 20, 24), "n % 8 == 0", 13),
    ((5, 10, 11, 20), "n % 5 == 0", 14),
)

_P100 = _page(
    "js-find-some-every",
    100,
    "Asking an array a question",
    "find, some, every and includes.",
    "find gives the first item that matches, or undefined - not its "
    "position, which is findIndex. some asks whether any match and every "
    "asks whether all of them do, and both stop as soon as they know the "
    "answer. includes is the plain one: is this exact value in there. "
    "Every array here is built so some is true and every is false, "
    "because a page where both said the same thing would teach you "
    "nothing about the difference.",
    "js_find_some_every",
    [
        (
            "Set numbers to ["
            + _seq(items)
            + "], const. Log numbers.find with an arrow testing "
            + test.replace("==", "===")
            + ", then .some with the same test, then .every with it, then "
            "whether the array includes "
            + str(looked_for)
            + ".",
            {"items": items, "test": test, "looked_for": looked_for},
        )
        for items, test, looked_for in _QUESTIONS
    ],
)


JS_PAGES_2: tuple[Page, ...] = (
    _P91,
    _P92,
    _P93,
    _P94,
    _P95,
    _P96,
    _P97,
    _P98,
    _P99,
    _P100,
)
