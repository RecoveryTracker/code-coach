"""JavaScript intermediate pages 101-110: the class machinery, and the
traps that come from JavaScript being JavaScript.

slice against splice. Generators. Getters and setters. Static members.
extends and super. Symbol.iterator. Named groups. Then three pages that
could not be about any other language: how a number comes out of a
string, what counts as true, and what happens to this when a method is
passed around without its object.

Pages 108, 109 and 110 are the ones to sit with. None of them is a bug -
all three are documented, deliberate, and the reason JavaScript has the
reputation it does.
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


# ── 101. The one that copies and the one that cuts ───────────

_SLICES = (
    ((1, 2, 3, 4, 5), 1, 3, 2),
    ((10, 20, 30, 40), 1, 3, 1),
    ((5, 6, 7, 8, 9), 2, 4, 2),
    ((1, 2, 3, 4), 0, 2, 1),
    ((11, 22, 33, 44, 55), 1, 4, 3),
    ((2, 4, 6, 8), 1, 3, 2),
    ((9, 8, 7, 6, 5), 0, 3, 2),
    ((100, 200, 300, 400), 2, 4, 1),
    ((1, 3, 5, 7, 9), 1, 2, 1),
    ((12, 24, 36, 48), 0, 3, 2),
    ((7, 14, 21, 28, 35), 2, 5, 2),
    ((3, 6, 9, 12), 1, 4, 3),
    ((2, 4, 6, 8, 10), 1, 3, 2),
    ((15, 25, 35, 45), 1, 3, 1),
    ((6, 7, 8, 9, 10), 2, 4, 2),
    ((5, 6, 7, 8), 0, 2, 1),
    ((13, 26, 39, 52, 65), 1, 4, 3),
    ((3, 6, 9, 12), 1, 3, 2),
    ((11, 10, 9, 8, 7), 0, 3, 2),
    ((500, 600, 700, 800), 2, 4, 1),
)

_P101 = _page(
    "js-slice-splice",
    101,
    "The one that copies and the one that cuts",
    "slice leaves the array alone; splice changes it.",
    "These two have almost the same name and opposite manners. slice "
    "takes a start and a stop and hands back a copy, leaving the "
    "original exactly as it was - which the second line here proves. "
    "splice takes a start and a count, removes those items from the "
    "array itself, and gives you back what it removed. The fourth line "
    "shows the original shorter than it started. If you only remember "
    "one thing: splice is the one that damages.",
    "js_slice_splice",
    [
        (
            "Set numbers to ["
            + _seq(items)
            + "], const. Take a slice from "
            + str(start)
            + " to "
            + str(stop)
            + " into taken, and log it joined with ', ', then numbers "
            "joined. Then splice "
            + str(count)
            + " items from position "
            + str(start)
            + " into cut, and log cut joined, then numbers joined again.",
            {"items": items, "start": start, "stop": stop, "count": count},
        )
        for items, start, stop, count in _SLICES
    ],
)


# ── 102. A function that hands values back as it goes ────────

_GENERATORS = (
    ("countUp", "n * 2", 4),
    ("squares", "n * n", 4),
    ("tens", "n * 10", 3),
    ("plusOne", "n + 1", 5),
    ("triples", "n * 3", 4),
    ("hundreds", "n * 100", 3),
    ("doubled", "n + n", 4),
    ("cubes", "n * n * n", 3),
    ("fives", "n * 5", 4),
    ("less", "n - 1", 5),
    ("sevens", "n * 7", 3),
    ("halves", "n * 50", 4),
    ("countOn", "n * 4", 4),
    ("cubesOf", "n * n * n", 4),
    ("twenties", "n * 20", 3),
    ("plusTwo", "n + 2", 5),
    ("quads", "n * 4", 4),
    ("thousands", "n * 1000", 3),
    ("tripled", "n + n + n", 4),
    ("nines", "n * 9", 3),
)

_P102 = _page(
    "js-generator",
    102,
    "A function that hands values back as it goes",
    "function* and yield, and why the star is on the function.",
    "A generator does not run when you call it - it hands back an object "
    "that runs a piece at a time, stopping at each yield until something "
    "asks for the next value. for...of does that asking. The star goes "
    "on the function keyword, not the name, and yield is only legal "
    "inside one. This is the same idea as page 114 in the Python book, "
    "and JavaScript's version is what async/await is built out of "
    "underneath.",
    "js_generator",
    [
        (
            "Write a generator function "
            + name
            + "(limit) that loops n from 1 up to and including limit, "
            "yielding "
            + expr
            + " each time. Loop over "
            + name
            + "("
            + str(limit)
            + ") with for...of, logging each value.",
            {"name": name, "expr": expr, "limit": limit},
        )
        for name, expr, limit in _GENERATORS
    ],
)


# ── 103. A field that runs code ──────────────────────────────

_ACCESSORS = (
    ("Box", "width", 5, 10, 2),
    ("Tank", "litres", 60, 20, 3),
    ("Shelf", "books", 7, 5, 4),
    ("Plot", "metres", 12, 6, 5),
    ("Batch", "items", 9, 3, 10),
    ("Wall", "bricks", 90, 15, 2),
    ("Trip", "miles", 40, 25, 4),
    ("Bill", "pence", 45, 11, 3),
    ("Grid", "rows", 8, 7, 6),
    ("Song", "seconds", 30, 12, 5),
    ("Card", "rank", 11, 4, 7),
    ("Team", "players", 11, 9, 2),
    ("Crate", "depth", 8, 12, 3),
    ("Barrel", "litres", 90, 30, 4),
    ("Rack", "books", 11, 6, 5),
    ("Field", "metres", 25, 9, 2),
    ("Pallet", "items", 14, 4, 7),
    ("Stack", "bricks", 144, 20, 3),
    ("Run", "miles", 60, 35, 5),
    ("Tab", "pence", 96, 13, 4),
)

_P103 = _page(
    "js-getter-setter",
    103,
    "A field that runs code",
    "get and set, and the underscore that holds the real value.",
    "A getter is read like a field and runs like a method, and a setter "
    "runs on assignment - so thing.width = 10 can check, clean or "
    "convert on the way in, which this one does by doubling. The value "
    "has to live somewhere else, conventionally an underscore name, "
    "because a getter that returned this.width would call itself "
    "forever. That infinite loop is the mistake everyone makes once. "
    "Modern JavaScript has real private fields with a hash, which is "
    "better when you can use it.",
    "js_getter_setter",
    [
        (
            "Write a class "
            + cls
            + " whose constructor stores "
            + field
            + " as this._"
            + field
            + ", with a getter "
            + field
            + " returning it and a setter storing the value times "
            + str(times)
            + ". Make thing with "
            + str(start)
            + " and log its "
            + field
            + ". Then assign "
            + str(given)
            + " to it and log it again.",
            {
                "cls": cls,
                "field": field,
                "start": start,
                "given": given,
                "times": times,
            },
        )
        for cls, field, start, given, times in _ACCESSORS
    ],
)


# ── 104. Something the class owns ────────────────────────────

_STATICS = (
    ("Counter", "made", "howMany", 3),
    ("Widget", "built", "total", 5),
    ("Ticket", "issued", "count", 2),
    ("Session", "opened", "howMany", 4),
    ("Node", "created", "total", 6),
    ("Card", "dealt", "count", 1),
    ("Job", "queued", "howMany", 3),
    ("User", "signedUp", "total", 2),
    ("Order", "placed", "count", 7),
    ("File", "made", "howMany", 4),
    ("Task", "started", "total", 8),
    ("Guest", "arrived", "count", 3),
    ("Gadget", "made", "howMany", 4),
    ("Drone", "built", "total", 6),
    ("Pass", "issued", "count", 3),
    ("Link", "opened", "howMany", 5),
    ("Leaf", "created", "total", 7),
    ("Hand", "dealt", "count", 2),
    ("Batch", "queued", "howMany", 4),
    ("Member", "signedUp", "total", 3),
)

_P104 = _page(
    "js-static",
    104,
    "Something the class owns",
    "static fields and methods, which belong to the class itself.",
    "A static field lives on the class, not on each object, so every "
    "object shares one copy - which is how you count how many have been "
    "made. A static method is called on the class the same way, and "
    "inside it this means the class rather than an object. Note that a "
    "static method cannot see an object's fields, because there is no "
    "object involved: reach for one when the work belongs to the type "
    "rather than to any one thing of that type.",
    "js_static",
    [
        (
            "Write a class "
            + cls
            + " with a static field "
            + field
            + " set to 0, a constructor that adds one to it, and a static "
            "method "
            + method
            + " returning it. Build "
            + str(times)
            + " of them with new, then log the method's result and the "
            "field directly.",
            {"cls": cls, "field": field, "method": method, "times": times},
        )
        for cls, field, method, times in _STATICS
    ],
)


# ── 105. A class built on another, and super ─────────────────

_EXTENDS = (
    ("Animal", "Dog", "speak", "makes a sound", "- woof", ("cat", "rex")),
    ("Shape", "Circle", "describe", "has edges", "- round", ("box", "ring")),
    ("Worker", "Baker", "report", "is working", "- baking", ("sam", "ada")),
    ("Store", "Disk", "where", "keeps things", "- on disk", ("mem", "ssd")),
    ("Engine", "Petrol", "start", "turns over", "- vroom", ("one", "two")),
    ("Reader", "Csv", "read", "reads bytes", "- and commas", ("raw", "rows")),
    ("Writer", "Console", "write", "writes out", "- to screen", ("a", "b")),
    ("Sender", "Email", "send", "sends it", "- by mail", ("x", "y")),
    ("Player", "Guitar", "play", "makes music", "- strum", ("jo", "kim")),
    ("Vehicle", "Bus", "move", "travels", "- with seats", ("van", "coach")),
    ("Timer", "Alarm", "tick", "counts time", "- and rings", ("t1", "t2")),
    ("Filter", "Blur", "apply", "changes it", "- softly", ("f1", "f2")),
    ("Animal", "Cow", "speak", "makes a sound", "- moo", ("hen", "bess")),
    ("Shape", "Square", "describe", "has edges", "- four", ("dot", "box")),
    ("Worker", "Smith", "report", "is working", "- hammering", ("kim", "lee")),
    ("Store", "Tape", "where", "keeps things", "- on tape", ("ram", "reel")),
    ("Engine", "Diesel", "start", "turns over", "- clatter", ("three", "four")),
    ("Reader", "Json", "read", "reads bytes", "- and braces", ("txt", "obj")),
    ("Sender", "Post", "send", "sends it", "- by van", ("p", "q")),
    ("Player", "Drum", "play", "makes music", "- thud", ("mo", "ned")),
)

_P105 = _page(
    "js-extends",
    105,
    "A class built on another, and super",
    "extends, and calling the version you inherited.",
    "extends says this class is a kind of that one, and a method with "
    "the same name replaces the inherited one. super.method() calls the "
    "version you replaced, which is how you add to behaviour rather than "
    "throwing it away - the second line here shows the parent's sentence "
    "with the child's ending on it. If the subclass has a constructor it "
    "must call super() before touching this, and JavaScript will stop "
    "you if you forget.",
    "js_extends",
    [
        (
            "Write a class "
            + base
            + " whose constructor stores name and whose "
            + method
            + " returns a template literal of the name and "
            + repr(base_says)
            + ". Write "
            + sub
            + " extending it, with "
            + method
            + " returning super's result then "
            + repr(sub_says)
            + ". Log the method on a new "
            + base
            + " called "
            + repr(names[0])
            + ", then on a new "
            + sub
            + " called "
            + repr(names[1])
            + ".",
            {
                "base": base,
                "sub": sub,
                "method": method,
                "base_says": base_says,
                "sub_says": sub_says,
                "names": names,
            },
        )
        for base, sub, method, base_says, sub_says, names in _EXTENDS
    ],
)


# ── 106. Making your own class work in for...of ──────────────

_ITERABLES = (
    ("Range", "n", 4, 3),
    ("Doubles", "n * 2", 4, 2),
    ("Squares", "n * n", 4, 3),
    ("Tens", "n * 10", 3, 2),
    ("Steps", "n + 1", 5, 3),
    ("Triples", "n * 3", 4, 2),
    ("Hundreds", "n * 100", 3, 2),
    ("Sums", "n + n", 4, 3),
    ("Cubes", "n * n * n", 3, 2),
    ("Fives", "n * 5", 4, 3),
    ("Less", "n - 1", 5, 2),
    ("Sevens", "n * 7", 3, 2),
    ("Counting", "n", 5, 2),
    ("Quads", "n * 4", 4, 3),
    ("Cubed", "n * n * n", 4, 2),
    ("Twenties", "n * 20", 3, 2),
    ("Paces", "n + 2", 5, 3),
    ("Nines", "n * 9", 4, 2),
    ("Thousands", "n * 1000", 3, 2),
    ("Trebles", "n + n + n", 4, 3),
)

_P106 = _page(
    "js-iterator",
    106,
    "Making your own class work in for...of",
    "Symbol.iterator, written as a generator method.",
    "for...of does not work on any old object - it works on anything "
    "with a Symbol.iterator method, which is why arrays, strings, Maps "
    "and Sets all work and a plain object does not. Give your class one "
    "and it joins them: for...of walks it, and the spread operator works "
    "too, which the first line uses. Writing it as a generator method - "
    "the star before the brackets - saves implementing next() and done "
    "by hand. This is page 177 of the Python book in JavaScript's "
    "clothing.",
    "js_iterator",
    [
        (
            "Write a class "
            + cls
            + " whose constructor stores limit, and a generator method "
            "for Symbol.iterator that loops n from 1 to limit yielding "
            + expr
            + ". Log a new "
            + cls
            + "("
            + str(limit)
            + ") spread into an array and joined with ', '. Then loop "
            "over a new "
            + cls
            + "("
            + str(smaller)
            + ") with for...of, logging each.",
            {
                "cls": cls,
                "expr": expr,
                "limit": limit,
                "smaller": smaller,
            },
        )
        for cls, expr, limit, smaller in _ITERABLES
    ],
)


# ── 107. Named groups, and replacing by pattern ──────────────

_REGEXES = (
    ("ada:36", "name", "age", ":", "??"),
    ("sam:41", "who", "years", ":", "##"),
    ("kyoto=1463", "city", "people", "=", "many"),
    ("oslo=709", "place", "count", "=", "some"),
    ("iron-26", "metal", "number", "-", "NN"),
    ("gold-79", "element", "atomic", "-", "XX"),
    ("dune#412", "book", "pages", "#", "lots"),
    ("alive#245", "song", "seconds", "#", "mins"),
    ("reds/41", "team", "points", "/", "pts"),
    ("saw/3", "tool", "weight", "/", "kg"),
    ("sky+3", "word", "length", r"\+", "len"),
    ("north+120", "trip", "miles", r"\+", "far"),
    ("finn:27", "name", "age", ":", "??"),
    ("ida:44", "who", "years", ":", "##"),
    ("ripon=17", "city", "people", "=", "many"),
    ("lima=998", "place", "count", "=", "some"),
    ("tin-50", "metal", "number", "-", "NN"),
    ("ubik#224", "book", "pages", "#", "lots"),
    ("blues/12", "team", "points", "/", "pts"),
    ("moon+4", "word", "length", r"\+", "len"),
)

_P107 = _page(
    "js-regex",
    107,
    "Named groups, and replacing by pattern",
    "A regex literal, match with named groups, and replace.",
    "JavaScript writes a regular expression between slashes rather than "
    "in a string, so there is no doubling of backslashes - one of the "
    "few places its syntax is kinder than Python's. Named groups use the "
    "same (?<name>...) and land on found.groups. replace with a pattern "
    "changes only the first match unless the pattern carries a g flag, "
    "which is the thing to remember: /\\d+/ replaces once, /\\d+/g "
    "replaces all.",
    "js_regex",
    [
        (
            "Set text to "
            + repr(text)
            + ", const. Make a regex literal with a named group "
            + repr(first)
            + " of word characters, then "
            + gap.replace("\\", "")
            + ", then a named group "
            + repr(second)
            + " of digits. Match text against it into found, and log the "
            "two groups. Then log text with the digits replaced by "
            + repr(instead)
            + ".",
            {
                "text": text,
                "first": first,
                "second": second,
                "gap": gap,
                "gap_plain": gap.replace("\\", ""),
                "instead": instead,
            },
        )
        for text, first, second, gap, instead in _REGEXES
    ],
)


# ── 108. Getting a number out of a string ────────────────────

_PARSES = (
    ("42px", 0.1, 0.2),
    ("30cm", 1.1, 2.2),
    ("7kg", 0.3, 0.6),
    ("100%", 0.7, 0.2),
    ("15mm", 2.5, 1.25),
    ("60s", 0.1, 0.7),
    ("12em", 3.3, 1.1),
    ("500ms", 0.2, 0.4),
    ("8bit", 1.5, 2.25),
    ("24fps", 0.6, 0.3),
    ("64kb", 4.4, 2.2),
    ("90deg", 0.8, 0.15),
    ("36px", 0.5, 0.25),
    ("48cm", 1.2, 2.4),
    ("9kg", 0.4, 0.8),
    ("75%", 0.9, 0.3),
    ("20mm", 3.5, 1.75),
    ("90s", 0.2, 0.9),
    ("14em", 2.2, 1.1),
    ("250ms", 0.6, 0.15),
)

_P108 = _page(
    "js-number-parse",
    108,
    "Getting a number out of a string",
    "parseInt against Number, and the empty string.",
    "parseInt reads digits from the front and stops at the first thing "
    "that is not one, so '42px' gives 42 - which is either exactly what "
    "you wanted or a bug that hides a typo for months. Number is strict "
    "and gives NaN for the same string. Then the third line: Number('') "
    "is 0, not NaN, so an empty form field quietly becomes zero. "
    "toFixed on the last line rounds and hands back a string, which is "
    "why it is right for display and wrong for arithmetic.",
    "js_number_parse",
    [
        (
            "Log parseInt of "
            + repr(mixed)
            + ", then Number of the same string, then Number of an empty "
            "string, then "
            + str(left)
            + " plus "
            + str(right)
            + " with toFixed(2).",
            {"mixed": mixed, "left": left, "right": right},
        )
        for mixed, left, right in _PARSES
    ],
)


# ── 109. What counts as true ─────────────────────────────────

_TRUTHY = (
    ("0", '""', '"0"', "[]"),
    ('""', "[]", "{}", "null"),
    ("0", "-1", "NaN", '" "'),
    ("null", "undefined", "1", "[]"),
    ('"0"', "0", "{}", "NaN"),
    ("[]", "[0]", '""', "1"),
    ("undefined", '" "', "0", "{}"),
    ("NaN", "1", '""', "[0]"),
    ("-1", "0", "null", '"0"'),
    ("{}", "null", '" "', "0"),
    ("[0]", "NaN", "-1", '""'),
    ("1", "undefined", "[]", "0"),
    ("0", "null", '" "', "[0]"),
    ('""', "1", "NaN", "{}"),
    ("undefined", "[]", "-1", '"0"'),
    ("NaN", "{}", "0", '" "'),
    ("[0]", "undefined", '""', "1"),
    ('" "', "0", "[]", "null"),
    ("1", "NaN", '"0"', "-1"),
    ("{}", "[0]", "undefined", '""'),
)

_P109 = _page(
    "js-truthy",
    109,
    "What counts as true",
    "The falsy values, and everything else.",
    "There are exactly six falsy values: false, 0, empty string, null, "
    "undefined and NaN. Everything else is truthy, and the ones that "
    "catch people are on this page. An empty array is truthy. An empty "
    "object is truthy. The string '0' is truthy, though the number 0 is "
    "not. A string of one space is truthy. This is why if (items.length) "
    "is right and if (items) is not, and why page 89's ?? exists "
    "alongside ||.",
    "js_truthy",
    [
        (
            "Log Boolean of each of "
            + ", then ".join(values)
            + ".",
            {"values": values},
        )
        for values in _TRUTHY
    ],
)


# ── 110. this, and what happens when you lose it ─────────────

_BINDS = (
    ("counter", "total", 5, "show", 99),
    ("box", "width", 12, "size", 40),
    ("tank", "litres", 60, "level", 7),
    ("shelf", "books", 9, "count", 21),
    ("bill", "pence", 45, "amount", 100),
    ("trip", "miles", 120, "distance", 3),
    ("team", "players", 11, "howMany", 5),
    ("song", "seconds", 245, "length", 60),
    ("card", "rank", 11, "value", 2),
    ("grid", "rows", 8, "height", 30),
    ("batch", "items", 24, "size", 6),
    ("room", "floor", 4, "level", 1),
    ("tally", "total", 8, "show", 55),
    ("crate", "depth", 15, "size", 60),
    ("barrel", "litres", 90, "level", 9),
    ("rack", "books", 12, "count", 30),
    ("tab", "pence", 96, "amount", 250),
    ("run", "miles", 180, "distance", 4),
    ("squad", "players", 15, "howMany", 7),
    ("track", "seconds", 386, "length", 90),
)

_P110 = _page(
    "js-bind",
    110,
    "this, and what happens when you lose it",
    "bind and call, and the method that forgot its object.",
    "this is decided when a function is called, not where it was "
    "written. Pull a method out into a variable and call it on its own "
    "and this is no longer the object, so the field comes back "
    "undefined - the second line here, and the single most common "
    "JavaScript bug there is. It happens constantly when passing a "
    "method as a callback. bind makes a copy with this fixed for good; "
    "call runs it once with a this you choose. An arrow function avoids "
    "the whole problem by not having its own this at all.",
    "js_bind",
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
            + " returning this."
            + field
            + ". Set loose to the method pulled out on its own, and bound "
            "to it bound to "
            + name
            + ". Log the method called properly, then loose(), then "
            "bound(), then the method called with call on an object whose "
            + field
            + " is "
            + str(other)
            + ".",
            {
                "name": name,
                "field": field,
                "value": v,
                "method": method,
                "other": other,
            },
        )
        for name, field, v, method, other in _BINDS
    ],
)


JS_PAGES_3: tuple[Page, ...] = (
    _P101,
    _P102,
    _P103,
    _P104,
    _P105,
    _P106,
    _P107,
    _P108,
    _P109,
    _P110,
)
