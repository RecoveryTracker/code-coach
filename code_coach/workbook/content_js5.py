"""JavaScript intermediate pages 121-130: scope, and the object model.

var against let in a loop - the closure bug that made let necessary, and
still the best one-page argument for never writing var again. Hoisting
and the temporal dead zone. Sorting objects. Grouping with reduce. Rest
and defaults when destructuring. Tagged templates. Symbol. WeakMap.
Proxy. And Object.freeze, which is shallow and silent.

Page 121 is the important one. Everything after it is the object model
that most JavaScript work never touches directly and every library you
use is built out of.
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


# ── 121. The loop variable every closure shared ──────────────

# Twelve different counts: the only thing that varies on this page is
# how far the loop runs, so a repeated count is a repeated exercise.
_LOOPS = (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18,
          19, 20, 21)

_P121 = _page(
    "js-var-let",
    121,
    "The loop variable every closure shared",
    "var is one binding for the whole loop; let is a fresh one each time.",
    "Both loops look identical and print different things. var makes one "
    "variable for the entire loop, so all three functions closed over "
    "the same one and see the value it finished at - which is why the "
    "first line is the same number three times. let makes a new binding "
    "every turn, so each function has its own. This exact bug, usually "
    "with setTimeout inside the loop, is why let was added to the "
    "language, and it is the reason never to write var again.",
    "js_var_let",
    [
        (
            "Make an empty array withVar. Loop i with var from 0 while it "
            "is under "
            + str(count)
            + ", pushing an arrow returning i. Do the same into withLet "
            "using let for j. Log each array mapped through calling its "
            "functions and joined with ', '.",
            {"count": count},
        )
        for count in _LOOPS
    ],
)


# ── 122. A name used before it exists ────────────────────────

_HOISTS = (
    ("early", "later", 1, 2),
    ("first", "second", 5, 10),
    ("one", "two", 7, 14),
    ("top", "bottom", 3, 9),
    ("before", "after", 2, 4),
    ("head", "tail", 11, 22),
    ("left", "right", 6, 12),
    ("start", "end", 8, 16),
    ("old", "fresh", 100, 200),
    ("low", "high", 1, 99),
    ("near", "far", 20, 40),
    ("in_first", "in_second", 13, 26),
    ("sooner", "afterwards", 3, 6),
    ("front", "rear", 4, 8),
    ("three", "four", 9, 18),
    ("upper", "lower", 5, 15),
    ("prior", "post", 7, 21),
    ("nose", "tail", 12, 24),
    ("inner", "outer", 14, 28),
    ("opening", "closing", 10, 30),
)

_P122 = _page(
    "js-hoisting",
    122,
    "A name used before it exists",
    "var hoisted to undefined; let in the temporal dead zone.",
    "A var declaration is moved to the top of its function, but the "
    "assignment is not - so the name exists and holds undefined, and "
    "typeof says so without complaint. A let is also known to the "
    "engine, but reading it before the line that declares it throws a "
    "ReferenceError: that gap is called the temporal dead zone, and it "
    "exists precisely so this is an error rather than a silent "
    "undefined. Silence is the thing to be afraid of here, not the "
    "throw.",
    "js_hoisting",
    [
        (
            "Log typeof "
            + early
            + " before declaring it, then declare it with var as "
            + str(first)
            + ". Then in a try log "
            + later
            + ", catching the problem and logging its constructor's name, "
            "and after the try declare "
            + later
            + " with let as "
            + str(second)
            + ". Finally log "
            + later
            + ".",
            {
                "early": early,
                "later": later,
                "first": first,
                "second": second,
            },
        )
        for early, later, first, second in _HOISTS
    ],
)


# ── 123. Sorting things by one of their fields ───────────────

_PEOPLE = (
    ("score", (("ada", 90), ("sam", 7), ("kim", 41))),
    ("points", (("blues", 41), ("greens", 12), ("reds", 30))),
    ("pages", (("dune", 412), ("ilium", 780), ("solaris", 204))),
    ("people", (("kyoto", 1463), ("oslo", 709), ("lima", 998))),
    ("seconds", (("alive", 245), ("heroes", 371), ("kooks", 173))),
    ("number", (("iron", 26), ("gold", 79), ("tin", 50))),
    ("floor", (("attic", 4), ("cellar", 0), ("hall", 1))),
    ("weight", (("saw", 3), ("axe", 8), ("file", 1))),
    ("count", (("apple", 12), ("fig", 3), ("pear", 7))),
    ("order", (("mix", 2), ("bake", 3), ("weigh", 1))),
    ("length", (("sky", 3), ("mountain", 8), ("lake", 4))),
    ("miles", (("north", 120), ("south", 40), ("east", 75))),
    ("score", (("finn", 82), ("kit", 4), ("ida", 37))),
    ("points", (("whites", 23), ("ambers", 55), ("violets", 9))),
    ("pages", (("ubik", 261), ("valis", 190), ("maze", 224))),
    ("people", (("ripon", 17), ("oslo", 709), ("lima", 998))),
    ("seconds", (("art", 224), ("sons", 207), ("warszawa", 386))),
    ("melting", (("tin", 232), ("lead", 327), ("gold", 1064))),
    ("depth", (("shallow", 2), ("middle", 40), ("deep", 15))),
    ("count", (("kiwi", 21), ("plum", 5), ("sloe", 13))),
)

_P123 = _page(
    "js-sort-objects",
    123,
    "Sorting things by one of their fields",
    "A compare function that reaches into the object.",
    "Page 96's compare function subtracted two numbers; this one "
    "subtracts a field out of two objects, which is the form you will "
    "write most often. Sorting by text is the awkward half: subtraction "
    "is meaningless on strings, so you compare and return -1 or 1. "
    "localeCompare is the proper answer for names a person will read, "
    "because it knows about accents and about the order letters come in "
    "outside English. Note both sorts work on copies, since sort "
    "damages.",
    "js_sort_objects",
    [
        (
            "Set people to a const array of objects, each with a name and "
            "a "
            + field
            + ": "
            + ", ".join(f"{n!r} with {v}" for n, v in rows)
            + ". Sort a copy by "
            + field
            + " with a subtracting compare function into byField, and a "
            "copy by name with a compare returning -1 or 1 into byName. "
            "Log each mapped to its names and joined with ', '.",
            {"field": field, "rows": rows},
        )
        for field, rows in _PEOPLE
    ],
)


# ── 124. reduce that builds an object ────────────────────────

_GROUPINGS = (
    (("ant", "ape", "bee", "bat"), "a"),
    (("cat", "cow", "dog", "duck"), "c"),
    (("red", "rose", "blue", "black"), "b"),
    (("mint", "moss", "nut", "oak"), "m"),
    (("sun", "sky", "moon", "mist"), "s"),
    (("iron", "ice", "oak", "olive"), "i"),
    (("pear", "plum", "fig", "fern"), "p"),
    (("wolf", "wren", "yak", "yew"), "w"),
    (("east", "elm", "fern", "fig"), "e"),
    (("gold", "grey", "hill", "hawk"), "g"),
    (("lake", "lily", "moth", "mole"), "l"),
    (("tea", "toad", "urn", "user"), "t"),
    (("fox", "fig", "owl", "oak"), "f"),
    (("hen", "hog", "ibex", "imp"), "h"),
    (("jade", "jet", "kelp", "kite"), "j"),
    (("newt", "nest", "otter", "oak"), "n"),
    (("rye", "reed", "sage", "sorrel"), "r"),
    (("vine", "vole", "wasp", "willow"), "v"),
    (("acorn", "ash", "birch", "bramble"), "b"),
    (("dove", "deer", "elm", "elder"), "e"),
)

_P124 = _page(
    "js-reduce-group",
    124,
    "reduce that builds an object",
    "An object as the starting value, and returning it each time.",
    "reduce is not only for adding up numbers - start it with an empty "
    "object and it becomes the standard way to group things. Two details "
    "make or break it. The running object must be returned from every "
    "turn, or the next one receives undefined; and the key must be "
    "created before it is pushed to, which is what ?? does here. Newer "
    "runtimes have Object.groupBy, which does exactly this page in one "
    "call.",
    "js_reduce_group",
    [
        (
            "Set words to ["
            + _seq(words)
            + "], const. Reduce it into an object starting from an empty "
            "one: take each word's first letter as the key, make the key "
            "an empty array if it is missing, push the word, and return "
            "the object. Log its keys sorted and joined with ', ', then "
            "the group for "
            + repr(letter)
            + " joined.",
            {"words": words, "letter": letter},
        )
        for words, letter in _GROUPINGS
    ],
)


# ── 125. The rest of the object, and a default ───────────────

_RESTS = (
    ((("host", "local"), ("port", "8080"), ("mode", "safe")), "debug", "off"),
    ((("name", "ada"), ("city", "kyoto"), ("role", "dev")), "team", "none"),
    ((("theme", "dark"), ("font", "mono"), ("size", "large")), "accent", "blue"),
    ((("lang", "en"), ("units", "metric"), ("zone", "utc")), "region", "eu"),
    ((("sort", "name"), ("order", "up"), ("limit", "ten")), "filter", "all"),
    ((("shell", "bash"), ("editor", "vi"), ("pager", "less")), "prompt", "plain"),
    ((("codec", "utf8"), ("newline", "lf"), ("bom", "no")), "locale", "c"),
    ((("cache", "on"), ("retries", "three"), ("delay", "one")), "backoff", "none"),
    ((("format", "csv"), ("header", "yes"), ("quote", "all")), "escape", "slash"),
    ((("level", "info"), ("target", "file"), ("rotate", "daily")), "keep", "seven"),
    ((("engine", "v8"), ("gc", "auto"), ("heap", "large")), "threads", "one"),
    ((("scheme", "https"), ("depth", "one"), ("agent", "bot")), "timeout", "thirty"),
    ((("host", "remote"), ("port", "5173"), ("mode", "fast")), "trace", "off"),
    ((("name", "finn"), ("city", "oslo"), ("role", "ops")), "squad", "none"),
    ((("theme", "light"), ("font", "sans"), ("size", "small")), "accent", "teal"),
    ((("lang", "fr"), ("units", "imperial"), ("zone", "cet")), "region", "us"),
    ((("sort", "date"), ("order", "down"), ("limit", "five")), "filter", "some"),
    ((("shell", "zsh"), ("editor", "emacs"), ("pager", "more")), "prompt", "rich"),
    ((("codec", "ascii"), ("newline", "crlf"), ("bom", "yes")), "locale", "en"),
    ((("cache", "off"), ("retries", "one"), ("delay", "two")), "backoff", "linear"),
)

_P125 = _page(
    "js-destructure-rest",
    125,
    "The rest of the object, and a default",
    "Rest in a destructuring, and a default for a key that is missing.",
    "Three dots on the left of a destructuring collect everything you "
    "did not name into a new object - which is how you take one field "
    "out and pass the remainder on, without changing the original. A "
    "default fills in for a key that is missing or undefined, exactly as "
    "a parameter default does on page 88, with the same rule about zero "
    "and empty strings not counting as missing. Both work in a parameter "
    "list too, which is where you will meet them most.",
    "js_destructure_rest",
    [
        (
            "Set settings to a const object of "
            + ", ".join(f"{k}: {v!r}" for k, v in pairs)
            + ". Destructure "
            + pairs[0][0]
            + " and a rest called rest out of it, and separately "
            "destructure "
            + absent
            + " with a default of "
            + repr(fallback)
            + ". Log "
            + pairs[0][0]
            + ", then rest's keys sorted and joined with ', ', then "
            + absent
            + ".",
            {"pairs": pairs, "absent": absent, "fallback": fallback},
        )
        for pairs, absent, fallback in _RESTS
    ],
)


# ── 126. A template literal handed to a function ─────────────

_TAGGED = (
    ("shout", "hello ", " aged ", "!", "ada", 36, "|", " :: ", ","),
    ("wrap", "name ", " year ", ".", "sam", 41, "/", " -- ", ";"),
    ("mark", "who ", " count ", "?", "kim", 12, "*", " => ", "+"),
    ("show", "city ", " people ", "", "kyoto", 1463, "-", " | ", ","),
    ("tag", "metal ", " number ", "", "iron", 26, "+", " : ", "-"),
    ("note", "book ", " pages ", ".", "dune", 412, "~", " >> ", ","),
    ("label", "song ", " seconds ", "", "alive", 245, "=", " ~ ", "/"),
    ("say", "team ", " points ", "!", "reds", 41, "#", " -> ", ","),
    ("emit", "tool ", " weight ", "", "saw", 3, "%", " . ", "-"),
    ("print_it", "word ", " length ", "", "sky", 3, "&", " ; ", "+"),
    ("give", "trip ", " miles ", ".", "north", 120, "^", " , ", ";"),
    ("form", "task ", " order ", "", "mix", 2, "!", " = ", ","),
    ("holler", "greet ", " aged ", "!", "finn", 27, "|", " :: ", ","),
    ("frame", "who ", " year ", ".", "ida", 44, "/", " -- ", ";"),
    ("stamp_it", "person ", " count ", "?", "kit", 15, "*", " => ", "+"),
    ("render", "town ", " people ", "", "ripon", 17, "-", " | ", ","),
    ("badge", "metal ", " melts ", "", "tin", 232, "+", " : ", "-"),
    ("caption", "book ", " pages ", ".", "ubik", 224, "~", " >> ", ","),
    ("banner", "track ", " seconds ", "", "art", 224, "=", " ~ ", "/"),
    ("shout_it", "side ", " points ", "!", "blues", 12, "#", " -> ", ","),
)

_P126 = _page(
    "js-tagged-template",
    126,
    "A template literal handed to a function",
    "A tag function, strings.raw, and the values in between.",
    "Put a function name in front of a backtick string and it is called "
    "with the literal pieces as the first argument and the interpolated "
    "values as the rest. So the function sees the template before it is "
    "assembled and can do anything it likes with it - escape the values, "
    "translate the text, build a database query safely. strings.raw is "
    "the text exactly as written, before backslash escapes are "
    "processed. There is always one more string piece than there are "
    "values.",
    "js_tagged_template",
    [
        (
            "Write "
            + name
            + "(strings, ...values) returning strings.raw joined with "
            + repr(between)
            + ", then "
            + repr(gap)
            + ", then the values joined with "
            + repr(comma)
            + ". Set first to "
            + repr(first)
            + " and second to "
            + str(second)
            + ". Log "
            + name
            + " tagged onto a template literal reading "
            + repr(before)
            + ", first, "
            + repr(middle)
            + ", second, "
            + repr(after)
            + ".",
            {
                "name": name,
                "before": before,
                "middle": middle,
                "after": after,
                "first": first,
                "second": second,
                "between": between,
                "gap": gap,
                "comma": comma,
            },
        )
        for name, before, middle, after, first, second, between, gap, comma in _TAGGED
    ],
)


# ── 127. A key that cannot collide ───────────────────────────

_SYMBOLS = (
    ("id", "ada", 7),
    ("token", "sam", 42),
    ("secret", "kim", 3),
    ("handle", "jo", 19),
    ("marker", "max", 8),
    ("tag", "eve", 55),
    ("ref", "abe", 12),
    ("slot", "ida", 64),
    ("code", "ben", 5),
    ("stamp", "rey", 30),
    ("hidden", "finn", 21),
    ("inner", "nell", 9),
    ("badge", "gus", 11),
    ("ticket", "hal", 63),
    ("private", "ivy", 4),
    ("label", "jan", 27),
    ("pointer", "kit", 9),
    ("seal", "lee", 72),
    ("keyed", "mia", 16),
    ("bucket", "noa", 48),
)

_P127 = _page(
    "js-symbol",
    127,
    "A key that cannot collide",
    "Symbol, and the key Object.keys does not show you.",
    "Every symbol is unique, even two made with the same description, so "
    "a symbol used as a key can never clash with anybody else's key on "
    "the same object - which is the point when you are attaching "
    "something to an object you do not own. Symbol keys are skipped by "
    "Object.keys, by JSON.stringify and by a for...in loop, so the third "
    "line here shows only name. That is privacy by obscurity rather than "
    "real privacy: Object.getOwnPropertySymbols will still find it.",
    "js_symbol",
    [
        (
            "Set key to a Symbol described as "
            + repr(label)
            + ", const. Set thing to an object with name "
            + repr(name)
            + " and the symbol as a computed key holding "
            + str(v)
            + ". Log the value under the symbol, then typeof key, then "
            "Object.keys of thing joined with ', ', then key.toString().",
            {"label": label, "name": name, "value": v},
        )
        for label, name, v in _SYMBOLS
    ],
)


# ── 128. Data kept beside an object, not on it ───────────────

_WEAKS = (
    ("Account", "balance", 50),
    ("Session", "token", 7),
    ("Player", "score", 90),
    ("Record", "version", 3),
    ("Node", "depth", 12),
    ("Ticket", "seat", 41),
    ("Order", "total", 250),
    ("File", "size", 1024),
    ("Task", "priority", 5),
    ("Widget", "serial", 88),
    ("Room", "capacity", 30),
    ("Batch", "count", 24),
    ("Ledger", "balance", 75),
    ("Link", "token", 9),
    ("Runner", "score", 82),
    ("Entry", "version", 5),
    ("Leaf", "depth", 16),
    ("Pass", "seat", 27),
    ("Basket", "total", 480),
    ("Page", "size", 2048),
)

_P128 = _page(
    "js-weakmap",
    128,
    "Data kept beside an object, not on it",
    "WeakMap, for private data and for caches that let go.",
    "The value is stored in the WeakMap with the object as its key, so "
    "it is not a field on the object at all - Object.keys finds nothing, "
    "and nothing outside this module can reach it. The weak part is the "
    "other half: the WeakMap does not keep the object alive, so when the "
    "object is collected the entry goes with it. That makes it right for "
    "a cache keyed on objects, which a normal Map would turn into a "
    "memory leak. Private class fields with a hash are the modern way to "
    "do the privacy part.",
    "js_weakmap",
    [
        (
            "Make a const WeakMap called secrets. Write a class "
            + cls
            + " whose constructor takes "
            + field
            + " and sets it in secrets under this, with a getter "
            + field
            + " returning secrets.get(this). Make thing with "
            + str(v)
            + " and log its "
            + field
            + ", then whether secrets has thing, then the number of "
            "Object.keys on thing.",
            {"cls": cls, "field": field, "value": v},
        )
        for cls, field, v in _WEAKS
    ],
)


# ── 129. An object that answers for another ──────────────────

_PROXIES = (
    ("known", 5, "missing", "not here"),
    ("host", 8080, "port", "unset"),
    ("name", 1, "title", "no title"),
    ("size", 42, "colour", "unknown"),
    ("count", 7, "total", "none"),
    ("score", 90, "rank", "unranked"),
    ("width", 30, "height", "not given"),
    ("year", 1977, "month", "unknown"),
    ("level", 3, "grade", "ungraded"),
    ("depth", 12, "breadth", "not set"),
    ("rows", 8, "cols", "unspecified"),
    ("start", 1, "end", "open"),
    ("present", 9, "absent", "not there"),
    ("host", 5173, "scheme", "unset"),
    ("label", 2, "caption", "no caption"),
    ("depth", 55, "shade", "unknown"),
    ("tally", 12, "sum", "none"),
    ("points", 82, "place", "unplaced"),
    ("across", 40, "down", "not given"),
    ("year", 1985, "day", "unknown"),
)

_P129 = _page(
    "js-proxy",
    129,
    "An object that answers for another",
    "A Proxy with a get trap, standing in front of a real object.",
    "A Proxy wraps an object and lets you intercept the basic "
    "operations - reading a key, writing one, checking whether it "
    "exists. The get trap here turns a missing key into a message "
    "instead of undefined, which is a two-line version of what "
    "validation libraries and reactive frameworks do underneath. Reach "
    "for it rarely: it is slower than a plain object and it makes code "
    "surprising, which is exactly what it is for and exactly why it "
    "should be obvious where one is in use.",
    "js_proxy",
    [
        (
            "Set target to a const object with "
            + field
            + " of "
            + str(v)
            + ". Wrap it in a Proxy called guarded whose get trap returns "
            "the value when the key is in the object and otherwise "
            + repr(fallback)
            + ". Log guarded."
            + field
            + ", then guarded."
            + absent
            + ".",
            {
                "field": field,
                "value": v,
                "absent": absent,
                "fallback": fallback,
            },
        )
        for field, v, absent, fallback in _PROXIES
    ],
)


# ── 130. Frozen, one level deep, and quietly ─────────────────

_FREEZES = (
    ("mode", "safe", "unsafe", ("a", "b")),
    ("level", "info", "debug", ("one", "two")),
    ("theme", "dark", "light", ("red", "blue")),
    ("state", "open", "shut", ("x", "y")),
    ("kind", "text", "binary", ("p", "q")),
    ("sort", "name", "date", ("up", "down")),
    ("host", "local", "remote", ("dev", "prod")),
    ("format", "csv", "json", ("head", "body")),
    ("region", "eu", "us", ("north", "south")),
    ("tier", "free", "paid", ("basic", "extra")),
    ("shell", "bash", "zsh", ("run", "stop")),
    ("codec", "utf8", "ascii", ("in", "out")),
    ("mode", "fast", "slow", ("c", "d")),
    ("level", "warn", "error", ("three", "four")),
    ("theme", "sepia", "mono", ("green", "amber")),
    ("state", "locked", "free", ("m", "n")),
    ("kind", "audio", "video", ("r", "s")),
    ("sort", "size", "kind", ("first", "last")),
    ("host", "staging", "live", ("test", "real")),
    ("format", "yaml", "toml", ("top", "foot")),
)

_P130 = _page(
    "js-freeze",
    130,
    "Frozen, one level deep, and quietly",
    "Object.freeze, and the two things it does not do.",
    "freeze stops fields being added, removed or changed on that object "
    "- and nothing else. The assignment on the second line fails "
    "silently rather than throwing, because this file is not in strict "
    "mode; put 'use strict' at the top and the same line throws, which "
    "is a good argument for strict mode. And the array inside was never "
    "frozen, so pushing to it works, which the third line shows. Deep "
    "freezing means walking the whole object yourself.",
    "js_freeze",
    [
        (
            "Set settings to a frozen const object with "
            + field
            + " of "
            + repr(value)
            + " and tags holding just "
            + repr(tags[0])
            + ". Try assigning "
            + repr(attempt)
            + " to the "
            + field
            + ", and push "
            + repr(tags[1])
            + " onto tags. Then log the "
            + field
            + ", the tags joined with ', ', and whether the object is "
            "frozen.",
            {
                "field": field,
                "value": value,
                "attempt": attempt,
                "tags": tags,
            },
        )
        for field, value, attempt, tags in _FREEZES
    ],
)


JS_PAGES_5: tuple[Page, ...] = (
    _P121,
    _P122,
    _P123,
    _P124,
    _P125,
    _P126,
    _P127,
    _P128,
    _P129,
    _P130,
)
