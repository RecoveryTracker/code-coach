"""JavaScript intermediate pages 81-90: the start of its own book.

Python's intermediate tier ran to two hundred pages on the argument that
one language done properly beats six done thinly. It has that depth now,
so JavaScript starts its own.

These are numbered from 81 because that is where JavaScript's book is
up to - the shared beginner and practice tiers end at 80. Python uses
those same numbers for different pages, which is fine: a reader is in
one book at a time, and the pages refer to each other by number, so each
book has to be numbered as itself.

The ten here are the ones a JavaScript beginner meets first and hardest:
template literals, the three array methods everything is built from,
destructuring, spread, arrows, defaults, optional chaining, and the two
collections that are not objects and arrays.
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


# ── 81. A value inside a backtick string ─────────────────────

_TEMPLATES = (
    ("ada", 36, 1),
    ("sam", 41, 1),
    ("kim", 29, 5),
    ("jo", 17, 3),
    ("max", 50, 10),
    ("eve", 22, 2),
    ("abe", 64, 1),
    ("ida", 38, 7),
    ("ben", 45, 5),
    ("rey", 19, 1),
    ("finn", 27, 4),
    ("nell", 33, 2),
)

_P81 = _page(
    "js-template",
    81,
    "A value inside a backtick string",
    "Template literals, and ${} for anything at all.",
    "Backticks rather than quotes, and ${} holds any expression - a "
    "variable, a sum, a function call. This replaces the string joining "
    'with plus signs that JavaScript made everyone do for years, and it '
    "reads far better for it. Two things worth knowing now: a backtick "
    "string can run across several lines without any escaping, and the "
    "braces are not optional - $name on its own is just those characters.",
    "js_template",
    [
        (
            "Set name to "
            + repr(name)
            + " and age to "
            + str(age)
            + ", both const. Log a template literal saying name, ' is ' "
            "and age. Then log one saying name, ' will be ' and age plus "
            + str(ahead)
            + ".",
            {"name": name, "age": age, "ahead": ahead},
        )
        for name, age, ahead in _TEMPLATES
    ],
)


# ── 82. A new array with each item changed ───────────────────

_MAPS = (
    ((1, 2, 3, 4), "n * 2"),
    ((5, 6, 7), "n * n"),
    ((10, 20, 30), "n + 1"),
    ((1, 2, 3), "n * 10"),
    ((9, 8, 7), "n - 1"),
    ((2, 4, 6, 8), "n + 5"),
    ((1, 3, 5), "n * n * n"),
    ((100, 200), "n + 50"),
    ((7, 14, 21), "n * 2"),
    ((3, 6, 9, 12), "n * 3"),
    ((11, 22), "n + 100"),
    ((4, 8, 12, 16), "n - 4"),
)

_P82 = _page(
    "js-map",
    82,
    "A new array with each item changed",
    "Array.map, which hands back a new array.",
    "map runs your function on every item and collects the answers into "
    "a new array - the original is untouched, which is the whole point "
    "and the difference from a for loop that pushes. The function gets "
    "the item, and if you ask for them, its index and the whole array "
    "too. Note the length is printed: map always gives you exactly as "
    "many items as it was given, which filter does not.",
    "js_map",
    [
        (
            "Set numbers to ["
            + _seq(items)
            + "], const. Set changed to numbers.map with an arrow taking "
            "n and returning "
            + expr
            + ". Log changed joined with ', ', then its length.",
            {"items": items, "expr": expr},
        )
        for items, expr in _MAPS
    ],
)


# ── 83. Only the items that qualify ──────────────────────────

_FILTERS = (
    ((1, 2, 3, 4, 5, 6), "n % 2 == 0"),
    ((1, 2, 3, 4, 5), "n > 2"),
    ((10, 15, 20, 25), "n % 10 == 0"),
    ((1, 2, 3, 4, 5, 6, 7), "n % 3 == 0"),
    ((5, 10, 15, 20), "n < 15"),
    ((2, 3, 5, 7, 8), "n % 2 == 1"),
    ((100, 50, 200, 25), "n >= 100"),
    ((1, 4, 9, 16, 25), "n > 8"),
    ((3, 6, 9, 12, 15), "n % 2 == 0"),
    ((11, 22, 33, 44), "n % 4 == 0"),
    ((1, 2, 3, 8, 13), "n < 5"),
    ((6, 7, 8, 9, 10), "n % 3 == 1"),
)

_P83 = _page(
    "js-filter",
    83,
    "Only the items that qualify",
    "Array.filter, and the test that decides.",
    "filter keeps the items your function says yes to, so the new array "
    "is shorter - print the length and you can see how many survived. "
    "The test must return true or false, and JavaScript's truthiness "
    "rules mean nearly anything counts as one of those, which is worth "
    "being careful about: an empty string and a zero are both falsy, so "
    "a filter on a value rather than a comparison will drop them.",
    "js_filter",
    [
        (
            "Set numbers to ["
            + _seq(items)
            + "], const. Set kept to numbers.filter with an arrow taking "
            "n and testing "
            + test.replace("==", "===")
            + ". Log kept joined with ', ', then its length.",
            {"items": items, "test": test},
        )
        for items, test in _FILTERS
    ],
)


# ── 84. An array folded down to one value ────────────────────

_REDUCES = (
    ((1, 2, 3, 4), "sum + n", 0),
    ((5, 10, 15), "sum + n", 0),
    ((2, 3, 4), "sum * n", 1),
    ((1, 2, 3, 4, 5), "sum + n", 100),
    ((10, 20, 30), "sum + n", 0),
    ((2, 2, 2), "sum * n", 1),
    ((7, 8, 9), "sum + n", 0),
    ((1, 10, 100), "sum + n", 0),
    ((3, 3, 3, 3), "sum + n", 0),
    ((4, 5), "sum * n", 2),
    ((6, 12, 18), "sum + n", 0),
    ((9, 1, 5), "sum + n", 50),
)

_P84 = _page(
    "js-reduce",
    84,
    "An array folded down to one value",
    "Array.reduce, the starting value, and what happens without one.",
    "reduce takes the running answer and the next item and hands back "
    "the new running answer, over and over, until one value is left. The "
    "second argument is where it starts, and giving it is not optional in "
    "practice: leave it out and reduce uses the first item as the start, "
    "which is what the second line here does deliberately - and which "
    "throws on an empty array. Pass a starting value and an empty array "
    "gives you that value, which is almost always what you wanted.",
    "js_reduce",
    [
        (
            "Set numbers to ["
            + _seq(items)
            + "], const. Set total to numbers.reduce with an arrow taking "
            "sum and n returning "
            + step
            + ", starting at "
            + str(start)
            + ". Log total. Then log numbers.reduce with an arrow taking "
            "best and n that keeps whichever is larger, with no starting "
            "value.",
            {"items": items, "step": step, "start": start},
        )
        for items, step, start in _REDUCES
    ],
)


# ── 85. Pulling names out of an object and an array ──────────

_DESTRUCTURES = (
    ("x", "y", (2, 3), (10, 20)),
    ("width", "height", (10, 4), (5, 6)),
    ("low", "high", (3, 17), (1, 2)),
    ("left", "right", (7, 8), (30, 40)),
    ("points", "bonus", (40, 7), (11, 22)),
    ("floor", "room", (3, 12), (8, 9)),
    ("miles", "hours", (120, 3), (60, 40)),
    ("rows", "cols", (8, 9), (2, 3)),
    ("full", "used", (60, 22), (15, 25)),
    ("price", "people", (45, 3), (7, 7)),
    ("start", "end", (7, 31), (100, 200)),
    ("first", "last", (1, 9), (4, 5)),
)

_P85 = _page(
    "js-destructure",
    85,
    "Pulling names out of an object and an array",
    "Destructuring, for objects by name and arrays by position.",
    "Braces on the left take fields out of an object by name; square "
    "brackets take items out of an array by position. That difference is "
    "the thing to hold on to, because the syntax looks alike. Both save "
    "the row of const x = point.x lines that otherwise start every "
    "function, and both work in a parameter list, which is where you "
    "will see them most.",
    "js_destructure",
    [
        (
            "Set point to an object with "
            + first
            + " of "
            + str(values[0])
            + " and "
            + second
            + " of "
            + str(values[1])
            + ". Destructure both names out of it. Then destructure head "
            "and tail out of the array ["
            + _seq(pair)
            + "]. Log "
            + first
            + " plus "
            + second
            + ", then head plus tail, then a template literal of "
            + first
            + " and tail.",
            {
                "first": first,
                "second": second,
                "values": values,
                "pair": pair,
            },
        )
        for first, second, values, pair in _DESTRUCTURES
    ],
)


# ── 86. Three dots, spreading and collecting ─────────────────

_SPREADS = (
    ((1, 2), (3, 4)),
    ((10, 20), (30,)),
    ((5,), (6, 7)),
    ((1, 1), (2, 2)),
    ((7, 8, 9), (10,)),
    ((100,), (200, 300)),
    ((2, 4), (6, 8)),
    ((11, 12), (13, 14)),
    ((0,), (1, 2)),
    ((21, 22), (23,)),
    ((3, 6), (9, 12)),
    ((9,), (8, 7)),
)

_P86 = _page(
    "js-spread",
    86,
    "Three dots, spreading and collecting",
    "The spread that opens an array up, and the rest that gathers.",
    "The same three dots do opposite things depending on where they are. "
    "In an array or a call they spread one thing out into many. In a "
    "parameter list they collect many into one array. Reading which is "
    "which comes down to whether you are building something or "
    "receiving something. Spread is also the usual way to copy an array "
    "or an object - and it is a shallow copy, exactly as page 113 warned "
    "in the other book.",
    "js_spread",
    [
        (
            "Set first to ["
            + _seq(one)
            + "] and second to ["
            + _seq(two)
            + "], const. Set joined to an array spreading both. Write "
            "total(...numbers) that reduces them to a sum starting at 0. "
            "Log joined joined with ', ', then total called with joined "
            "spread out.",
            {"first": one, "second": two},
        )
        for one, two in _SPREADS
    ],
)


# ── 87. A function without the word function ─────────────────

_ARROWS = (
    ("double", "n * 2", 5, "add", "a + b", (2, 3)),
    ("square", "n * n", 4, "times", "a * b", (3, 4)),
    ("less_two", "n - 2", 9, "minus", "a - b", (10, 3)),
    ("triple", "n * 3", 7, "total", "a + b", (10, 20)),
    ("negate", "-n", 6, "gap", "a - b", (9, 4)),
    ("plus_five", "n + 5", 95, "area", "a * b", (3, 4)),
    ("cube", "n * n * n", 3, "sum_two", "a + b", (7, 8)),
    ("less", "n - 1", 11, "power", "a ** b", (2, 5)),
    ("more", "n + 1", 41, "rest", "a % b", (17, 5)),
    ("scale", "n * 5", 4, "join_up", "a + b", (20, 4)),
    ("shift", "n + 100", 50, "spread_of", "a - b", (4, 9)),
    ("twice", "n + n", 8, "product", "a * b", (12, 3)),
)

_P87 = _page(
    "js-arrow",
    87,
    "A function without the word function",
    "Arrow functions, and the implied return.",
    "An arrow with an expression after it returns that expression - no "
    "braces, no return. Put braces in and you are back to writing return "
    "yourself, which is the single most common confusion here: "
    "(n) => { n * 2 } returns nothing at all. The other difference is "
    "invisible until it bites - an arrow does not get its own this, "
    "which is exactly why it works inside a method where a plain "
    "function would not.",
    "js_arrow",
    [
        (
            "Set "
            + one_name
            + " to an arrow taking n and returning "
            + one_expr
            + ", const. Set "
            + two_name
            + " to an arrow taking a and b and returning "
            + two_expr.replace("**", "to the power of")
            + ". Log "
            + one_name
            + " of "
            + str(one_call)
            + ", then "
            + two_name
            + " of "
            + _seq(two_call)
            + ".",
            {
                "one_name": one_name,
                "one_expr": one_expr,
                "one_call": one_call,
                "two_name": two_name,
                "two_expr": two_expr,
                "two_call": two_call,
            },
        )
        for one_name, one_expr, one_call, two_name, two_expr, two_call in _ARROWS
    ],
)


# ── 88. An argument you can leave out ────────────────────────

_DEFAULTS = (
    ("greet", "greeting", "hello", "ada", "sam", "hi"),
    ("welcome", "word", "welcome", "kim", "jo", "hey"),
    ("call", "label", "dear", "max", "eve", "hi"),
    ("tag", "prefix", "mr", "abe", "ida", "dr"),
    ("hail", "shout", "hello", "ben", "rey", "oi"),
    ("name_it", "title", "sir", "finn", "nell", "lord"),
    ("meet", "phrase", "hello", "ann", "bo", "yo"),
    ("open", "word", "welcome", "cal", "dee", "enter"),
    ("mark", "sign", "note", "eli", "fay", "flag"),
    ("say", "start", "hello", "gus", "hal", "howdy"),
    ("call_out", "word", "hey", "ivy", "jan", "psst"),
    ("address", "title", "dear", "kit", "lee", "esteemed"),
)

_P88 = _page(
    "js-default-params",
    88,
    "An argument you can leave out",
    "A default in the parameter list, and when it applies.",
    "A default is used when the argument is undefined - which means when "
    "it was not passed, and also when it was passed as undefined on "
    "purpose. It is not used for null, or for an empty string, or for "
    "zero, which is the trap: pass 0 to a parameter defaulting to 10 and "
    "you get 0, but pass nothing and you get 10. That is usually right "
    "and occasionally a surprise. Defaults can also refer to earlier "
    "parameters, which is more useful than it sounds.",
    "js_default_params",
    [
        (
            "Write "
            + name
            + "(who, "
            + param
            + ") with "
            + param
            + " defaulting to "
            + repr(fallback)
            + ", returning a template literal of "
            + param
            + " then a space then who. Log it called with just "
            + repr(first)
            + ", then with "
            + repr(second)
            + " and "
            + repr(given)
            + ".",
            {
                "name": name,
                "param": param,
                "fallback": fallback,
                "first": first,
                "second": second,
                "given": given,
            },
        )
        for name, param, fallback, first, second, given in _DEFAULTS
    ],
)


# ── 89. Reaching for something that may not be there ─────────

_CHAINS = (
    ("ada", "city", "kyoto", "sam", "unknown", "age", 0),
    ("kim", "town", "oslo", "jo", "nowhere", "score", 0),
    ("max", "street", "high", "eve", "none", "count", 1),
    ("abe", "region", "north", "ida", "unset", "rank", 0),
    ("ben", "county", "kent", "rey", "unknown", "years", 18),
    ("finn", "village", "elm", "nell", "missing", "total", 0),
    ("ann", "city", "lima", "bo", "unknown", "level", 1),
    ("cal", "district", "west", "dee", "none", "size", 0),
    ("eli", "borough", "south", "fay", "unset", "weight", 10),
    ("gus", "parish", "east", "hal", "unknown", "height", 0),
    ("ivy", "ward", "central", "jan", "missing", "depth", 5),
    ("kit", "zone", "inner", "lee", "none", "width", 0),
)

_P89 = _page(
    "js-optional-chain",
    89,
    "Reaching for something that may not be there",
    "?. for the reach, and ?? for the fallback.",
    "Reaching two levels into an object that might only have one used to "
    "mean a chain of ands. ?. stops and gives undefined the moment "
    "something is missing, rather than throwing. ?? then supplies a "
    "fallback - and it is not the same as ||, which is the reason it "
    "exists: || falls back on any falsy value, so an empty string or a "
    "zero would be replaced, while ?? only falls back on null or "
    "undefined. Watch the third line, where zero is a real answer.",
    "js_optional_chain",
    [
        (
            "Set found to an object with name "
            + repr(name)
            + " and home holding "
            + field
            + " of "
            + repr(value)
            + ". Set missing to an object with only name "
            + repr(other)
            + ". Log found.home reached optionally for "
            + field
            + ", then missing.home the same way with "
            + repr(fallback)
            + " as the fallback, then missing."
            + number_field
            + " with "
            + str(number)
            + " as the fallback.",
            {
                "name": name,
                "field": field,
                "value": value,
                "other": other,
                "fallback": fallback,
                "number_field": number_field,
                "number": number,
            },
        )
        for name, field, value, other, fallback, number_field, number in _CHAINS
    ],
)


# ── 90. Map and Set, which are not objects and arrays ────────

_COLLECTIONS = (
    ((1, 2, 2, 3), (("ada", 90), ("sam", 7))),
    ((5, 5, 6), (("kim", 41), ("jo", 12))),
    ((1, 1, 1, 2), (("max", 50), ("eve", 22))),
    ((10, 20, 20, 30), (("abe", 64), ("ida", 38))),
    ((7, 7, 8, 9), (("ben", 45), ("rey", 19))),
    ((2, 4, 4, 6), (("finn", 27), ("nell", 33))),
    ((3, 3, 3), (("ann", 15), ("bo", 60))),
    ((11, 22, 11), (("cal", 8), ("dee", 71))),
    ((9, 8, 8, 7), (("eli", 34), ("fay", 26))),
    ((100, 100, 200), (("gus", 55), ("hal", 44))),
    ((1, 2, 3, 3), (("ivy", 90), ("jan", 11))),
    ((6, 6, 12), (("kit", 77), ("lee", 23))),
)

_P90 = _page(
    "js-map-set",
    90,
    "Map and Set, which are not objects and arrays",
    "new Set for uniqueness, new Map for keys that are not strings.",
    "A plain object turns every key into a string, has whatever it "
    "inherited from Object on it, and cannot tell you its size without "
    "counting. A Map takes any value as a key, remembers insertion "
    "order, and has .size. A Set is the same idea for membership - "
    "duplicates simply do not go in, which is what the first line shows. "
    "Both need spreading into an array before you can use array methods "
    "on them, which the last line does.",
    "js_map_set",
    [
        (
            "Set seen to a new Set of ["
            + _seq(items)
            + "], and scores to a new Map of the pairs "
            + " and ".join(f"[{k!r}, {v}]" for k, v in pairs)
            + ". Log seen.size, then scores.get of "
            + repr(pairs[0][0])
            + ", then seen spread into an array and joined with ', '.",
            {"items": items, "pairs": pairs},
        )
        for items, pairs in _COLLECTIONS
    ],
)


JS_PAGES: tuple[Page, ...] = (
    _P81,
    _P82,
    _P83,
    _P84,
    _P85,
    _P86,
    _P87,
    _P88,
    _P89,
    _P90,
)
