"""JavaScript intermediate pages 141-150: the object model underneath, and
coercion.

reduceRight. A labelled break. Object.defineProperty. The prototype
chain reached directly rather than through class. The type checks,
including typeof null. Radix conversion. URL and encodeURIComponent.
Sparse arrays. arguments against rest. And coercion.

Page 150 is the one JavaScript gets mocked for, taught straight: the
minus sign has one job so a string becomes a number, and the plus sign
has two so joining text wins. Once you know which operators are
overloaded, none of it is arbitrary.
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


# ── 141. Folding from the other end ──────────────────────────

_RIGHTS = (
    ("a", "b", "c"),
    ("x", "y", "z"),
    ("one", "two"),
    ("do", "re", "mi"),
    ("red", "blue"),
    ("n", "o", "d", "e"),
    ("first", "last"),
    ("up", "down"),
    ("a", "b", "c", "d"),
    ("in", "out"),
    ("left", "right"),
    ("p", "q", "r"),
    ("d", "e", "f"),
    ("u", "v", "w"),
    ("three", "four"),
    ("la", "ti", "do"),
    ("gold", "tin"),
    ("l", "i", "s", "t"),
    ("front", "back"),
    ("near", "far"),
)

_P141 = _page(
    "js-reduce-right",
    141,
    "Folding from the other end",
    "reduceRight, and when the direction changes the answer.",
    "reduce walks left to right and reduceRight walks right to left. For "
    "addition that makes no difference, which is why the two lines here "
    "join strings instead - and come out reversed. Reach for it when the "
    "operation is not symmetric: composing functions, building a nested "
    "structure from a flat list, or unwinding something that was built "
    "left to right. Most of the time reduce is the one you want.",
    "js_reduce_right",
    [
        (
            "Set words to ["
            + ", ".join(repr(w) for w in words)
            + "], const. Log words reduced from an empty string by adding "
            "each letter on, then the same with reduceRight.",
            {"words": words},
        )
        for words in _RIGHTS
    ],
)


# ── 142. Leaving two loops at once ───────────────────────────

_BREAKS = (
    (3, 4, "done"),
    (4, 6, "finished"),
    (3, 2, "stopped"),
    (5, 9, "out"),
    (4, 8, "ended"),
    (3, 6, "over"),
    (5, 12, "complete"),
    (4, 3, "halted"),
    (6, 20, "closed"),
    (3, 5, "left"),
    (5, 15, "past it"),
    (4, 10, "away"),
    (5, 7, "wrapped up"),
    (6, 10, "all done"),
    (4, 5, "broken out"),
    (7, 20, "that is enough"),
    (3, 7, "stepped out"),
    (5, 11, "leaving now"),
    (6, 14, "quit early"),
    (4, 9, "no further"),
)

_P142 = _page(
    "js-labelled-break",
    142,
    "Leaving two loops at once",
    "A label, and break with a name.",
    "A plain break leaves the loop it is in, which is no use when you "
    "want out of both. The usual workarounds are a flag checked by the "
    "outer loop, or wrapping the pair in a function and returning - both "
    "of which say less than a label does. Putting a name before the "
    "outer for, and breaking to that name, leaves both at once. Labels "
    "work with continue too. They are the one respectable use of "
    "anything resembling a goto.",
    "js_labelled_break",
    [
        (
            "Write a for loop labelled outer, looping i from 1 to "
            + str(limit)
            + ", with an inner loop over j the same range. When i times j "
            "is greater than "
            + str(stop)
            + ", break out of the outer loop; otherwise log a template "
            "literal of i and j. After both, log "
            + repr(done)
            + ".",
            {"limit": limit, "stop": stop, "done": done},
        )
        for limit, stop, done in _BREAKS
    ],
)


# ── 143. A property with the rules spelled out ───────────────

_DESCRIPTORS = (
    ("ada", "secret", 42, 99),
    ("sam", "token", 7, 13),
    ("kim", "code", 3, 8),
    ("jo", "key", 19, 21),
    ("max", "id", 8, 80),
    ("eve", "stamp", 55, 5),
    ("abe", "ref", 12, 24),
    ("ida", "slot", 64, 32),
    ("ben", "mark", 5, 50),
    ("rey", "seal", 30, 3),
    ("finn", "hidden", 21, 12),
    ("nell", "inner", 9, 90),
    ("gus", "secret", 51, 77),
    ("hal", "token", 9, 18),
    ("ivy", "code", 4, 16),
    ("jan", "key", 23, 46),
    ("kit", "id", 11, 110),
    ("lee", "stamp", 66, 6),
    ("mia", "ref", 14, 28),
    ("noa", "slot", 72, 36),
)

_P143 = _page(
    "js-define-property",
    143,
    "A property with the rules spelled out",
    "Object.defineProperty, writable and enumerable.",
    "Every property has a descriptor behind it, and normally all the "
    "flags are true. defineProperty lets you set them. writable false "
    "means the assignment on the next line is ignored without a word - "
    "in strict mode it throws, which is better. enumerable false keeps "
    "it out of Object.keys, out of JSON.stringify and out of a for...in, "
    "while `in` still finds it. This is how library authors hide "
    "bookkeeping on objects you are given.",
    "js_define_property",
    [
        (
            "Set thing to a const object with name "
            + repr(name)
            + ". Use Object.defineProperty to add "
            + repr(hidden)
            + " with the value "
            + str(v)
            + ", enumerable false and writable false. Then try assigning "
            + str(attempt)
            + " to it. Log the value, then Object.keys joined with ', ', "
            "then whether "
            + repr(hidden)
            + " is in thing.",
            {
                "name": name,
                "hidden": hidden,
                "value": v,
                "attempt": attempt,
            },
        )
        for name, hidden, v, attempt in _DESCRIPTORS
    ],
)


# ── 144. The object behind the object ────────────────────────

_PROTOS = (
    ("greet", "hello", "name", "ada"),
    ("speak", "woof", "breed", "collie"),
    ("describe", "round", "colour", "red"),
    ("report", "working", "task", "mixing"),
    ("where", "on disk", "path", "tmp"),
    ("start", "vroom", "fuel", "petrol"),
    ("read", "bytes", "source", "file"),
    ("write", "written", "target", "screen"),
    ("play", "strum", "tune", "blues"),
    ("move", "travelling", "mode", "bus"),
    ("tick", "counting", "unit", "seconds"),
    ("apply_it", "changed", "kind", "blur"),
    ("hail", "good day", "name", "finn"),
    ("call", "moo", "breed", "friesian"),
    ("outline", "square", "colour", "teal"),
    ("state", "resting", "task", "waiting"),
    ("locate", "in memory", "path", "cache"),
    ("crank", "clatter", "fuel", "diesel"),
    ("scan", "characters", "source", "stream"),
    ("emit", "printed", "target", "console"),
)

_P144 = _page(
    "js-prototype",
    144,
    "The object behind the object",
    "Object.create, hasOwn, and getPrototypeOf.",
    "Every object has another object behind it, and a property not found "
    "on the first is looked for there. Object.create makes one with the "
    "prototype you choose, which is what class has been doing all along "
    "in page 92's clothing. Two things worth seeing: the method is "
    "callable but is not the object's own, so Object.keys does not list "
    "it and hasOwn says false. That difference is why a for...in loop "
    "over an object can surprise you.",
    "js_prototype",
    [
        (
            "Set base to a const object with a method "
            + method
            + " returning "
            + repr(says)
            + ". Make thing with Object.create of base and give it a "
            + field
            + " of "
            + repr(value)
            + ". Log the method's result, then Object.keys joined with "
            "', ', then Object.hasOwn of thing and "
            + repr(method)
            + ", then whether the prototype of thing is base.",
            {
                "method": method,
                "says": says,
                "field": field,
                "value": value,
            },
        )
        for method, says, field, value in _PROTOS
    ],
)


# ── 145. Asking what something is ────────────────────────────

_TYPES = (
    ("42", "number"),
    ('"text"', "string"),
    ("true", "boolean"),
    ("undefined", "undefined"),
    ("(() => 1)", "function"),
    ("Symbol()", "symbol"),
    ("10n", "bigint"),
    ("{}", "object"),
    ("new Date()", "object"),
    ("/x/", "object"),
    ("NaN", "number"),
    ("new Map()", "object"),
    ("null", "object"),
    ("[]", "object"),
    ("0.5", "number"),
    ("false", "boolean"),
    ("new Set()", "object"),
    ("(function () {})", "function"),
    ("5n", "bigint"),
    ("Symbol.iterator", "symbol"),
)

_P145 = _page(
    "js-type-checks",
    145,
    "Asking what something is",
    "typeof, Array.isArray, instanceof, and typeof null.",
    "typeof is nearly useless on objects: an array, a date, a regex and a "
    "Map all answer 'object', so the first line here tells you almost "
    "nothing and Array.isArray exists because of it. Then typeof null is "
    "'object', which is a bug from 1995 that can never be fixed because "
    "too much code depends on it. instanceof asks about the prototype "
    "chain instead, which is more useful and fails across frames and "
    "worker boundaries. Use typeof for primitives and isArray or "
    "instanceof for the rest.",
    "js_type_checks",
    [
        (
            "Log typeof of an empty array, then Array.isArray of one, "
            "then typeof null, then whether an empty array is an instance "
            "of Array, then typeof "
            + sample
            + ".",
            {"sample": sample, "expected": expected},
        )
        for sample, expected in _TYPES
    ],
)


# ── 146. The same number in another base ─────────────────────

_RADIXES = (
    (255, "ff"),
    (10, "a"),
    (64, "40"),
    (7, "7"),
    (128, "80"),
    (100, "64"),
    (31, "1f"),
    (200, "c8"),
    (1, "1"),
    (170, "aa"),
    (63, "3f"),
    (4095, "fff"),
    (511, "1ff"),
    (32, "20"),
    (15, "f"),
    (250, "fa"),
    (4096, "1000"),
    (85, "55"),
    (192, "c0"),
    (1023, "3ff"),
)

_P146 = _page(
    "js-radix",
    146,
    "The same number in another base",
    "toString with a radix, and parseInt with one.",
    "toString takes a base from 2 to 36, so one number can be written "
    "binary, hex or octal without any arithmetic on your part - and it "
    "hands back a string, with no 0x or 0b on the front. parseInt with a "
    "second argument reads one back. Always pass that second argument: "
    "without it, a string starting with 0x is read as hex and everything "
    "else as decimal, which is the sort of rule that turns into a bug "
    "when a leading zero appears in real data.",
    "js_radix",
    [
        (
            "Set value to "
            + str(value)
            + ", const. Log its toString in base 2, then base 16, then "
            "base 8. Then log parseInt of "
            + repr(hexed)
            + " in base 16.",
            {"value": value, "hex": hexed},
        )
        for value, hexed in _RADIXES
    ],
)


# ── 147. A web address, parsed and escaped ───────────────────

_URLS = (
    ("a b&c", "https://example.com/path?x=1&y=2", "y"),
    ("one two", "https://example.org/page?a=5&b=6", "b"),
    ("x=y&z", "http://localhost:8765/api?lang=python&page=3", "lang"),
    ("hello world", "https://docs.example.com/find?q=maps&n=10", "q"),
    ("p&q", "https://shop.example.net/cart?id=42&qty=2", "id"),
    ("a?b", "https://api.example.io/v2?key=abc&fmt=json", "fmt"),
    ("m n", "http://blog.example.uk/posts?tag=code&sort=new", "tag"),
    ("s&t&u", "https://files.example.co/list?dir=up&show=all", "show"),
    ("q r", "https://cdn.example.dev/asset?v=3&type=png", "type"),
    ("k&l", "http://test.example.me/run?case=one&loud=yes", "case"),
    ("y z", "https://mail.example.info/box?folder=in&page=1", "folder"),
    ("c&d", "https://news.example.tv/story?id=99&full=true", "full"),
    ("d e&f", "https://example.com/page?x=3&y=4", "x"),
    ("three four", "https://example.org/list?a=7&b=8", "a"),
    ("p=q&r", "http://localhost:5173/api?lang=js&page=5", "page"),
    ("good day", "https://docs.example.com/seek?q=arrays&n=20", "n"),
    ("s&t", "https://shop.example.net/bag?id=77&qty=3", "qty"),
    ("c?d", "https://api.example.io/v3?key=xyz&fmt=csv", "key"),
    ("u v", "http://blog.example.uk/notes?tag=js&sort=old", "sort"),
    ("w&x&y", "https://files.example.co/dir?dir=down&show=few", "dir"),
)

_P147 = _page(
    "js-url",
    147,
    "A web address, parsed and escaped",
    "encodeURIComponent, and the URL object.",
    "encodeURIComponent escapes everything that would change the meaning "
    "of a URL - a space becomes %20, an ampersand becomes %26 - which is "
    "why you must run every value through it before putting it in a "
    "query string. Its cousin encodeURI escapes less and is for a whole "
    "URL, not a piece of one. The URL object then does the parsing side, "
    "with searchParams for the query, so you never split on question "
    "marks and ampersands yourself.",
    "js_url",
    [
        (
            "Set raw to "
            + repr(raw)
            + ", const, and log it encoded as a URI component. Then make "
            "a URL from "
            + repr(address)
            + " and log its hostname, then its searchParams get for "
            + repr(key)
            + ".",
            {"raw": raw, "address": address, "key": key},
        )
        for raw, address, key in _URLS
    ],
)


# ── 148. An array with a hole in it ──────────────────────────

_SPARSE = (
    (1, 3, 2),
    (5, 9, 3),
    (10, 30, 2),
    (7, 21, 4),
    (2, 6, 5),
    (4, 12, 2),
    (100, 300, 3),
    (8, 24, 2),
    (11, 33, 6),
    (3, 9, 7),
    (6, 18, 2),
    (12, 36, 4),
    (2, 6, 3),
    (6, 18, 4),
    (15, 45, 2),
    (9, 27, 5),
    (3, 9, 6),
    (5, 15, 3),
    (200, 600, 2),
    (14, 42, 3),
)

_P148 = _page(
    "js-sparse",
    148,
    "An array with a hole in it",
    "A missing element, which is not the same as undefined.",
    "Leaving a gap in an array literal makes a hole, and a hole is not a "
    "slot holding undefined - it is no slot at all. Reading it gives "
    "undefined, which is why the difference is easy to miss, but "
    "Object.keys skips the index entirely and map leaves the hole alone "
    "rather than calling your function on it. So the length says three "
    "and the keys say two. Holes come up in real code from delete on an "
    "array element, and are a good reason never to use delete that way.",
    "js_sparse",
    [
        (
            "Set holes to a const array literal holding "
            + str(first)
            + ", then a gap, then "
            + str(last)
            + ". Log its length, then the item at index 1, then the "
            "length of it mapped through multiplying by "
            + str(times)
            + ", then Object.keys joined with ', '.",
            {"first": first, "last": last, "times": times},
        )
        for first, last, times in _SPARSE
    ],
)


# ── 149. Every argument, the old way and the new ─────────────

_ARGUMENTS = (
    ("countOld", "countNew", "joinAll", (1, 2, 3)),
    ("howManyOld", "howManyNew", "listThem", (5, 6)),
    ("sizeOld", "sizeNew", "showAll", (10, 20, 30)),
    ("totalOld", "totalNew", "asText", (7, 8, 9, 10)),
    ("lenOld", "lenNew", "spellOut", (2, 4)),
    ("tallyOld", "tallyNew", "render", (11, 22, 33)),
    ("numOld", "numNew", "printAll", (1, 1, 1)),
    ("gotOld", "gotNew", "asLine", (100, 200)),
    ("takenOld", "takenNew", "asList", (3, 6, 9)),
    ("readOld", "readNew", "asJoined", (12, 24, 36, 48)),
    ("sawOld", "sawNew", "asOne", (5, 10, 15)),
    ("heldOld", "heldNew", "asString", (9, 8)),
    ("tallyOldWay", "tallyNewWay", "joinUp", (2, 3, 4)),
    ("countedOld", "countedNew", "listOut", (7, 8)),
    ("widthOld", "widthNew", "showEach", (15, 25, 35)),
    ("sumOld", "sumNew", "asWords", (6, 7, 8, 9)),
    ("spanOld", "spanNew", "spellIt", (3, 5)),
    ("markOld", "markNew", "drawAll", (12, 24, 36)),
    ("seenOld", "seenNew", "writeAll", (2, 2, 2)),
    ("keptOld", "keptNew", "asRow", (300, 400)),
)

_P149 = _page(
    "js-arguments",
    149,
    "Every argument, the old way and the new",
    "arguments, rest parameters, and why an arrow has no arguments.",
    "arguments is an array-like object every ordinary function gets for "
    "free, holding whatever it was called with. It is not an array, so "
    "map and join are not on it, and it does not exist inside an arrow "
    "function at all - which is why the arrow here uses rest. Rest "
    "parameters give you a real array and say in the signature that the "
    "function takes any number of things, which arguments never did. "
    "There is no reason to write arguments in new code.",
    "js_arguments",
    [
        (
            "Write "
            + old
            + "() with no parameters, returning arguments.length. Write "
            + modern
            + "(...values) returning values.length. Set "
            + arrow
            + " to an arrow taking rest values and returning them joined "
            "with ', '. Log all three called with "
            + _seq(given)
            + ".",
            {
                "old": old,
                "modern": modern,
                "arrow": arrow,
                "given": given,
            },
        )
        for old, modern, arrow, given in _ARGUMENTS
    ],
)


# ── 150. What the plus sign decides to do ────────────────────

_COERCIONS = (
    ("5", 2, 1),
    ("10", 3, 5),
    ("42", 2, 0),
    ("7", 4, 9),
    ("100", 1, 2),
    ("8", 3, 7),
    ("20", 5, 3),
    ("9", 6, 4),
    ("15", 5, 8),
    ("30", 10, 6),
    ("64", 4, 11),
    ("12", 7, 20),
    ("6", 3, 2),
    ("11", 4, 6),
    ("50", 3, 1),
    ("8", 5, 10),
    ("200", 2, 3),
    ("9", 4, 8),
    ("25", 6, 4),
    ("14", 7, 5),
)

_P150 = _page(
    "js-coercion",
    150,
    "What the plus sign decides to do",
    "Minus converting, plus joining, and the object that becomes text.",
    "The minus sign has exactly one meaning, so a string with digits in "
    "it is converted to a number and the answer is arithmetic. The plus "
    "sign has two, and joining text wins whenever either side is a "
    "string - so the same pair of values gives 3 on one line and '52' on "
    "the next. A boolean converts to 1 or 0, which is why the third line "
    "works. And the fourth is the famous one: an empty array becomes an "
    "empty string, an object becomes '[object Object]', and joining them "
    "gives that. None of it is arbitrary once you know which operators "
    "are overloaded - but this is why the rule is to convert on purpose "
    "with Number() and String().",
    "js_coercion",
    [
        (
            "Log the string "
            + repr(digits)
            + " minus "
            + str(taken)
            + ", then the same string plus "
            + str(taken)
            + ", then "
            + str(plain)
            + " plus true, then an empty array plus an empty object.",
            {"digits": digits, "taken": taken, "plain": plain},
        )
        for digits, taken, plain in _COERCIONS
    ],
)


JS_PAGES_7: tuple[Page, ...] = (
    _P141,
    _P142,
    _P143,
    _P144,
    _P145,
    _P146,
    _P147,
    _P148,
    _P149,
    _P150,
)
