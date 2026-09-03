"""JavaScript intermediate pages 151-160: privacy, precision, and functions
that return functions.

Real private fields. Number.EPSILON, which is this book's answer to the
float page in the Python one. String.raw. seal against freeze.
Memoisation with a Map. Currying. fill. A class that decides how it
converts. Deep equality written out, because JavaScript still ships
none. And returning this.

Page 152 is the same arithmetic as Python's page 189, in a language
whose only number type is the one that gets it wrong.
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


# ── 151. A field nothing outside the class can reach ─────────

_PRIVATES = (
    ("Account", "balance", "add", 50, 25),
    ("Basket", "total", "put", 10, 5),
    ("Tank", "litres", "pour", 60, 20),
    ("Score", "points", "award", 40, 7),
    ("Shelf", "books", "stack", 9, 3),
    ("Meter", "reading", "advance", 100, 15),
    ("Wallet", "pence", "deposit", 450, 50),
    ("Batch", "items", "include", 24, 6),
    ("Queue", "waiting", "join_it", 3, 4),
    ("Store", "stock", "receive", 80, 12),
    ("Timer", "seconds", "extend", 30, 90),
    ("Track", "metres", "run_on", 400, 200),
)

_P151 = _page(
    "js-private-field",
    151,
    "A field nothing outside the class can reach",
    "A # field, which is private in the language rather than by custom.",
    "An underscore in front of a name was only ever a request. A hash is "
    "enforced: reaching for thing.#balance from outside is a syntax "
    "error, not a runtime one, so it cannot even be attempted "
    "dynamically. It is not a property either, which is why Object.keys "
    "finds nothing and JSON.stringify leaves it out. This is what page "
    "128 used a WeakMap for, done properly, and it is the right answer "
    "in any runtime new enough to have it.",
    "js_private_field",
    [
        (
            "Write a class "
            + cls
            + " with a private field "
            + field
            + ", a constructor that sets it, a getter returning it, and a "
            "method "
            + method
            + " that adds n to it and returns the new value. Make thing "
            "with "
            + str(start)
            + ", log its "
            + field
            + ", then the result of "
            + method
            + " with "
            + str(added)
            + ", then how many Object.keys it has.",
            {
                "cls": cls,
                "field": field,
                "method": method,
                "start": start,
                "added": added,
            },
        )
        for cls, field, method, start, added in _PRIVATES
    ],
)


# ── 152. Comparing floats without === ────────────────────────

# Chosen so the sum really does miss, and misses by less than one
# epsilon; the emitter checks both.
_FLOATS = (
    (0.1, 0.2, 0.3),
    (0.1, 0.7, 0.8),
    (0.2, 0.4, 0.6),
    (0.2, 0.7, 0.9),
    (0.3, 0.6, 0.9),
    (0.02, 0.21, 0.23),
    (0.05, 0.12, 0.17),
    (0.07, 0.59, 0.66),
    (0.11, 0.57, 0.68),
    (0.17, 0.8, 0.97),
    (0.25, 0.42, 0.67),
    (0.32, 0.59, 0.91),
)

_P152 = _page(
    "js-epsilon",
    152,
    "Comparing floats without ===",
    "Number.EPSILON, and why 0.1 + 0.2 is not 0.3 here either.",
    "JavaScript has one number type and it is a double, so this is the "
    "same arithmetic as the Python book's page 189 with no way to opt "
    "out. The first line prints the sum in full and you can see the "
    "error. Number.EPSILON is the smallest gap between 1 and the next "
    "double, and comparing the difference against it is the standard "
    "way to ask whether two floats are near enough. For money, use whole "
    "pence in an integer, or a decimal library.",
    "js_epsilon",
    [
        (
            "Set total to "
            + str(left)
            + " plus "
            + str(right)
            + ", const. Log total, then whether it is strictly equal to "
            + str(target)
            + ", then whether the absolute difference between them is "
            "less than Number.EPSILON.",
            {"left": left, "right": right, "target": target},
        )
        for left, right, target in _FLOATS
    ],
)


# ── 153. A string with the backslashes left alone ────────────

_RAWS = (
    (r"C:\Users\new", "a\tb", 3),
    (r"C:\temp\note", "x\ny", 3),
    (r"D:\work\report", "p\tq", 3),
    (r"\\server\share", "a\\b", 3),
    (r"C:\bin\node", "1\t2", 3),
    (r"E:\data\raw", "m\nn", 3),
    (r"C:\logs\app", "u\tv", 3),
    (r"F:\media\clip", "g\\h", 3),
    (r"C:\src\main", "k\tl", 3),
    (r"G:\backup\old", "s\nt", 3),
    (r"C:\docs\note", "w\tx", 3),
    (r"H:\cache\tmp", "y\\z", 3),
)

_P153 = _page(
    "js-string-raw",
    153,
    "A string with the backslashes left alone",
    "String.raw, and what an escape sequence costs in length.",
    "In an ordinary string a backslash starts an escape, so \\t is one "
    "tab character and a Windows path needs every backslash doubled. "
    "String.raw as a tag on a template literal - which is page 126's "
    "machinery - hands back the text exactly as written, backslashes "
    "intact. The lengths make the difference concrete: the escaped "
    "string is shorter than it looks, because the two characters you "
    "typed became one.",
    "js_string_raw",
    [
        (
            "Set path to String.raw tagged onto a template literal "
            "holding "
            + repr(raw)
            + ", const. Log path, then its length, then the length of the "
            "ordinary string "
            + repr(escaped)
            + ".",
            {
                "raw": raw,
                "escaped": escaped,
                "escaped_value": escaped,
            },
        )
        for raw, escaped, _ in _RAWS
    ],
)


# ── 154. Sealed, which is not the same as frozen ─────────────

_SEALS = (
    ("name", "ada", "age", 36, 37, "extra"),
    ("title", "dune", "pages", 412, 500, "isbn"),
    ("city", "kyoto", "people", 1463, 1500, "region"),
    ("metal", "iron", "number", 26, 27, "symbol"),
    ("song", "alive", "seconds", 245, 250, "album"),
    ("team", "reds", "points", 41, 44, "league"),
    ("tool", "saw", "weight", 3, 4, "brand"),
    ("room", "attic", "floor", 4, 5, "wing"),
    ("word", "sky", "length", 3, 6, "origin"),
    ("trip", "north", "miles", 120, 130, "route"),
    ("task", "mix", "order", 2, 3, "owner"),
    ("user", "sam", "score", 90, 95, "rank"),
)

_P154 = _page(
    "js-seal",
    154,
    "Sealed, which is not the same as frozen",
    "Object.seal: change what is there, add nothing, delete nothing.",
    "freeze on page 130 stopped everything. seal is the middle setting: "
    "existing fields can still be assigned to, but nothing can be added "
    "and nothing deleted. All three attempts here happen without a "
    "complaint - the change works, the addition vanishes, the delete "
    "does nothing - which is the pattern for this whole corner of the "
    "language and the reason to check with isSealed rather than assume. "
    "Strict mode turns the two silent failures into throws.",
    "js_seal",
    [
        (
            "Set thing to a sealed const object with "
            + keep
            + " of "
            + repr(kept)
            + " and "
            + change
            + " of "
            + str(before)
            + ". Assign "
            + str(after)
            + " to the "
            + change
            + ", assign 1 to a new "
            + extra
            + ", and delete the "
            + keep
            + ". Then log the "
            + change
            + ", the "
            + extra
            + ", the "
            + keep
            + ", and whether the object is sealed.",
            {
                "keep": keep,
                "kept": kept,
                "change": change,
                "before": before,
                "after": after,
                "extra": extra,
            },
        )
        for keep, kept, change, before, after, extra in _SEALS
    ],
)


# ── 155. Answers remembered in a Map ─────────────────────────

_MEMOS = (10, 12, 15, 8, 20, 11, 14, 9, 16, 13, 18, 7)

_P155 = _page(
    "js-memo-map",
    155,
    "Answers remembered in a Map",
    "A Map outside the function, checked before the work is done.",
    "Plain recursive fibonacci computes the same value over and over and "
    "gets exponentially worse. A Map outside the function fixes it: ask "
    "whether the answer is known, work it out only if not, keep it. The "
    "size printed afterwards shows exactly how many were stored - one "
    "for every n from 2 up to the one you asked for, each computed once. "
    "A Map rather than an object because its keys stay numbers, and "
    "because size is free.",
    "js_memo_map",
    [
        (
            "Make a const Map called cache. Write fib(n) returning n when "
            "it is under 2, otherwise setting cache for n to fib of n "
            "minus 1 plus fib of n minus 2 when the cache does not have "
            "it, and returning the cached value. Log fib of "
            + str(wanted)
            + ", then cache.size.",
            {"wanted": wanted},
        )
        for wanted in _MEMOS
    ],
)


# ── 156. A function that returns a function ──────────────────

_CURRIES = (
    ("add", "a + b", "addFive", 5, 3, (2, 10)),
    ("times", "a * b", "double", 2, 7, (3, 4)),
    ("power", "a ** b", "twoTo", 2, 5, (3, 2)),
    ("minus", "a - b", "fromTen", 10, 3, (20, 5)),
    ("scale", "a * b", "triple", 3, 6, (4, 5)),
    ("shift", "a + b", "plusHundred", 100, 4, (1, 2)),
    ("rest_of", "a % b", "modSeven", 7, 3, (17, 5)),
    ("stack", "a * b", "byFour", 4, 8, (6, 6)),
    ("drop", "a - b", "fromFifty", 50, 12, (30, 10)),
    ("join_up", "a + b", "plusOne", 1, 41, (9, 9)),
    ("grow", "a * b", "byTen", 10, 12, (5, 5)),
    ("cut", "a - b", "fromHundred", 100, 45, (60, 20)),
)

_P156 = _page(
    "js-curry",
    156,
    "A function that returns a function",
    "Currying, and why two arrows in a row read the way they do.",
    "(a) => (b) => a + b is a function taking a and returning a function "
    "taking b - so calling it once gives you a specialised function, and "
    "calling it twice gives you the answer. The inner function closes "
    "over a, which is page 98 doing the work. This is how you build "
    "add-five out of add without writing another function, and it is the "
    "shape a great deal of functional JavaScript is written in, "
    "including most middleware.",
    "js_curry",
    [
        (
            "Set "
            + name
            + " to an arrow taking a and returning an arrow taking b that "
            "returns "
            + expr.replace("**", "a to the power of b").replace(
                "a a to the power of b b", "a to the power of b"
            )
            + ", const. Set "
            + fixed_name
            + " to "
            + name
            + " called with "
            + str(fixed)
            + ". Log "
            + fixed_name
            + " called with "
            + str(call)
            + ", then "
            + name
            + " called with "
            + str(other[0])
            + " and then "
            + str(other[1])
            + ".",
            {
                "name": name,
                "expr": expr,
                "fixed_name": fixed_name,
                "fixed": fixed,
                "call": call,
                "other": other,
            },
        )
        for name, expr, fixed_name, fixed, call, other in _CURRIES
    ],
)


# ── 157. An array made and filled in one go ──────────────────

_FILLS = (
    (4, 0, (1, 2, 3, 4), 9, 1, 3),
    (3, 1, (5, 6, 7), 0, 0, 2),
    (5, 7, (1, 1, 1, 1, 1), 2, 2, 4),
    (4, 2, (10, 20, 30, 40), 5, 0, 2),
    (3, 9, (2, 4, 6), 8, 1, 3),
    (6, 0, (1, 2, 3, 4, 5, 6), 7, 3, 5),
    (4, 5, (9, 8, 7, 6), 1, 1, 4),
    (3, 3, (11, 22, 33), 44, 0, 1),
    (5, 1, (2, 3, 5, 7, 11), 0, 2, 5),
    (4, 8, (12, 24, 36, 48), 6, 0, 3),
    (3, 4, (100, 200, 300), 50, 1, 2),
    (6, 2, (1, 3, 5, 7, 9, 11), 0, 2, 6),
)

_P157 = _page(
    "js-fill",
    157,
    "An array made and filled in one go",
    "new Array(n).fill, and fill with a start and a stop.",
    "new Array(4) makes four holes, which page 148 showed map skips - so "
    "it is useless until fill puts something in every slot. That pair is "
    "the standard way to make an array of a known size. Array.from with "
    "a length and a function is the other way and gives you the index, "
    "which fill does not. fill also takes a start and a stop for "
    "overwriting part of an existing array, in place, which is what the "
    "third line does.",
    "js_fill",
    [
        (
            "Make zeros as a new Array of "
            + str(count)
            + " filled with "
            + str(filler)
            + ". Make counted with Array.from of an object with that "
            "length, mapping to the index. Make patched by filling ["
            + _seq(items)
            + "] with "
            + str(patch)
            + " from "
            + str(start)
            + " to "
            + str(stop)
            + ". Log all three joined with ', '.",
            {
                "count": count,
                "filler": filler,
                "items": items,
                "patch": patch,
                "start": start,
                "stop": stop,
            },
        )
        for count, filler, items, patch, start, stop in _FILLS
    ],
)


# ── 158. An object that decides how it converts ──────────────

_PRIMITIVES = (
    ("Money", "pence", 250, "p"),
    ("Length", "metres", 12, "m"),
    ("Weight", "grams", 500, "g"),
    ("Time", "seconds", 90, "s"),
    ("Angle", "degrees", 45, " deg"),
    ("Size", "bytes", 1024, "B"),
    ("Speed", "knots", 18, "kn"),
    ("Heat", "celsius", 21, "C"),
    ("Volume", "litres", 60, "L"),
    ("Power", "watts", 750, "W"),
    ("Depth", "metres", 30, "m"),
    ("Load", "kilos", 80, "kg"),
)

_P158 = _page(
    "js-to-primitive",
    158,
    "An object that decides how it converts",
    "toString and valueOf, and which one gets asked.",
    "When an object has to become something simpler, JavaScript asks it. "
    "A template literal wants text, so toString is called and you get "
    "the readable form. Arithmetic wants a number, so valueOf is called "
    "and you get the raw one - which is why the same object prints two "
    "different things two lines apart. Defining both is how a value type "
    "behaves sensibly in either place, and Symbol.toPrimitive lets you "
    "take over the decision entirely.",
    "js_to_primitive",
    [
        (
            "Write a class "
            + cls
            + " whose constructor stores "
            + field
            + ", with a toString returning a template literal of the "
            "field then "
            + repr(suffix)
            + ", and a valueOf returning the field. Make thing with "
            + str(v)
            + ". Log it inside a template literal, then thing plus 0, "
            "then String of thing.",
            {"cls": cls, "field": field, "value": v, "suffix": suffix},
        )
        for cls, field, v, suffix in _PRIMITIVES
    ],
)


# ── 159. Equality written out by hand ────────────────────────

_DEEPS = (
    ("x", 1, "y", 2),
    ("a", 5, "b", 6),
    ("count", 10, "total", 20),
    ("width", 3, "height", 4),
    ("first", 7, "second", 8),
    ("low", 1, "high", 9),
    ("rows", 8, "cols", 9),
    ("miles", 40, "hours", 2),
    ("price", 45, "many", 3),
    ("start", 0, "end", 31),
    ("left", 11, "right", 22),
    ("points", 41, "bonus", 7),
)

_P159 = _page(
    "js-deep-equal",
    159,
    "Equality written out by hand",
    "Recursion over keys, because === compares identity.",
    "Two objects with the same contents are not equal in JavaScript - "
    "=== asks whether they are the same object, which the second line "
    "shows coming out false. There is no built-in deep comparison, so "
    "every codebase either writes this or pulls in a library for it. The "
    "version here is the honest minimum and still incomplete: it does "
    "not handle arrays properly, or Dates, or Maps, or a key holding "
    "undefined. Knowing where it stops is more useful than the function.",
    "js_deep_equal",
    [
        (
            "Write same(a, b) returning true when they are strictly "
            "equal, false when either is not an object or is null, false "
            "when their key counts differ, and otherwise whether every "
            "key matches recursively. Log same on two separate objects "
            "each holding "
            + field
            + " of "
            + str(value)
            + ", then those two compared with triple equals, then same on "
            "two objects each holding "
            + field
            + " of an object holding "
            + inner
            + " of "
            + str(deep)
            + ".",
            {
                "field": field,
                "value": value,
                "inner": inner,
                "deep": deep,
            },
        )
        for field, value, inner, deep in _DEEPS
    ],
)


# ── 160. Returning this, over and over ───────────────────────

_CHAINS = (
    ("Builder", "add", "build", ("a", "b", "c"), "-"),
    ("Path", "step", "render", ("home", "ada", "notes"), "/"),
    ("Query", "where", "text", ("id", "name", "age"), " and "),
    ("Line", "part", "join_up", ("one", "two"), " "),
    ("Recipe", "then_do", "read", ("weigh", "mix", "bake"), " then "),
    ("Route", "via", "show", ("north", "east"), " to "),
    ("Chain", "link", "out", ("x", "y", "z"), "+"),
    ("Song", "bar", "play", ("do", "re", "mi"), " "),
    ("Deck", "card", "list_it", ("ace", "king"), ", "),
    ("Trail", "mark", "print_it", ("start", "middle", "end"), " > "),
    ("Stack", "put", "flatten", ("first", "second"), "|"),
    ("Note", "line_of", "write_out", ("top", "bottom"), "\\n"),
)

_P160 = _page(
    "js-chaining",
    160,
    "Returning this, over and over",
    "A fluent interface, which is one return statement away.",
    "A method that ends with return this hands the object back, so the "
    "next call can start where the last one stopped - and a whole "
    "sequence reads as one sentence. That is all a fluent or builder "
    "interface is, and it is why jQuery and a hundred query builders "
    "look the way they do. The cost is that every method must return "
    "this, so a method that forgets ends the chain with undefined and an "
    "error that points at the wrong line.",
    "js_chaining",
    [
        (
            "Write a class "
            + cls
            + " whose constructor sets parts to an empty array, a method "
            + method
            + " that pushes its argument and returns this, and a method "
            + finish
            + " returning the parts joined with "
            + repr(between)
            + ". Log a new one with "
            + method
            + " called for "
            + ", ".join(repr(p) for p in parts)
            + " in a chain, ending with "
            + finish
            + ".",
            {
                "cls": cls,
                "method": method,
                "finish": finish,
                "parts": parts,
                "between": between,
            },
        )
        for cls, method, finish, parts, between in _CHAINS
    ],
)


JS_PAGES_8: tuple[Page, ...] = (
    _P151,
    _P152,
    _P153,
    _P154,
    _P155,
    _P156,
    _P157,
    _P158,
    _P159,
    _P160,
)
