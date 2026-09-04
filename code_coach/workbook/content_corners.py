"""Intermediate pages 239-248: sets, types written down, and the newer corners.

A set comprehension and a frozen set. Counter doing arithmetic. TypedDict
and Literal, which describe a shape of data rather than a class.
cached_property. base64. Time zones, and the difference between a
datetime that knows where it is and one that does not.

Then three things most people never meet at all: except*, which catches
out of a group of errors raised together; __init_subclass__, which lets a
base class notice that someone inherited from it; and inspect.signature,
which reads a function's own shape back out of it.

Python only, same as 81-238.
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


# ── 239. A set built in one line, and a frozen one ───────────

# Each list has two words sharing a first letter, so the set visibly
# collapses; the emitter raises if one ever does not.
_SETS = (
    ("ant", "ape", "bee"),
    ("cat", "cow", "dog"),
    ("red", "rose", "blue"),
    ("mint", "moss", "nut"),
    ("sun", "sky", "moon"),
    ("iron", "ice", "oak"),
    ("pear", "plum", "fig"),
    ("wolf", "wren", "yak"),
    ("east", "elm", "fern"),
    ("gold", "grey", "hill"),
    ("lake", "lily", "moth"),
    ("tea", "toad", "urn"),
    ("owl", "oak", "fox"),
    ("hen", "hog", "ibex"),
    ("jade", "jet", "kelp"),
    ("newt", "nest", "otter"),
    ("rye", "reed", "sage"),
    ("vine", "vole", "wasp"),
    ("acorn", "ash", "birch"),
    ("dove", "deer", "elm"),
)

_P239 = _page(
    "set-comp-frozen",
    239,
    "A set built in one line, and a frozen one",
    "A set comprehension, and frozenset for when it must be hashable.",
    "Braces instead of brackets makes a set rather than a list, so the "
    "duplicates disappear on the way in - two of these words share a "
    "first letter, and the printed set is shorter than the list because "
    "of it. A frozenset is a set that cannot be changed, and being "
    "unchangeable makes it hashable, which is why the last line can put "
    "one inside another set. A normal set cannot go in a set, for the "
    "same reason a list cannot be a dict key.",
    "set_comp_frozen",
    [
        (
            "Set words to ["
            + _seq(words)
            + "] and firsts to a set comprehension of each word's first "
            "letter. Print sorted(firsts). Then make frozen a frozenset "
            "of firsts, print sorted(frozen), and print the length of a "
            "set containing frozen.",
            {"words": words},
        )
        for words in _SETS
    ],
)


# ── 240. Counters added, subtracted and overlapped ───────────

_COUNTERS = (
    ("aabbc", "abbd"),
    ("hello", "world"),
    ("aaab", "abbb"),
    ("mississippi", "missouri"),
    ("abcabc", "abc"),
    ("xxyy", "yyzz"),
    ("banana", "bandana"),
    ("aabb", "bbcc"),
    ("python", "typhoon"),
    ("cccdd", "ddeee"),
    ("letter", "better"),
    ("aaa", "aab"),
    ("aabbcc", "abccd"),
    ("morning", "evening"),
    ("aaac", "accc"),
    ("tennessee", "tenacious"),
    ("abcabcabc", "abcabc"),
    ("ppqq", "qqrr"),
    ("sandal", "scandal"),
    ("ccdd", "ddee"),
)

_P240 = _page(
    "counter-math",
    240,
    "Counters added, subtracted and overlapped",
    "Counter arithmetic: plus, minus, and the ampersand.",
    "A Counter is not just a dict of counts, it does arithmetic. Adding "
    "two adds their counts. Subtracting takes one from the other and - "
    "this is the part to notice - drops anything that would go to zero "
    "or below, so the result never has negative counts. The ampersand "
    "keeps the smaller count of each thing in both, which is the "
    "overlap. Comparing two documents, or working out what a recipe "
    "still needs, is one line of this.",
    "counter_math",
    [
        (
            "Import Counter from collections. Set first to a Counter of "
            + repr(one)
            + " and second to a Counter of "
            + repr(two)
            + ". Print the sorted items of the two added, then of first "
            "minus second, then of first and second with the ampersand.",
            {"first": one, "second": two},
        )
        for one, two in _COUNTERS
    ],
)


# ── 241. A dict whose keys are written down ──────────────────

_TYPED = (
    ("Person", "age", "ada", 36, ("read", "write")),
    ("City", "people", "kyoto", 1463, ("north", "south")),
    ("Book", "pages", "dune", 412, ("draft", "final")),
    ("Song", "seconds", "alive", 245, ("play", "pause")),
    ("Metal", "number", "iron", 26, ("solid", "liquid")),
    ("Room", "floor", "attic", 4, ("open", "closed")),
    ("Tool", "weight", "saw", 3, ("sharp", "blunt")),
    ("Team", "points", "reds", 41, ("home", "away")),
    ("Word", "length", "sky", 3, ("upper", "lower")),
    ("Trip", "miles", "north", 120, ("fast", "slow")),
    ("Task", "order", "mix", 2, ("todo", "done")),
    ("User", "score", "sam", 90, ("admin", "guest")),
    ("Runner", "score", "finn", 82, ("fetch", "store")),
    ("Town", "people", "ripon", 17, ("east", "west")),
    ("Volume", "pages", "ubik", 224, ("proof", "print")),
    ("Track_", "seconds", "art", 224, ("start", "stop")),
    ("Ore", "melting", "tin", 232, ("cold", "molten")),
    ("Berth", "floor", "cabin", 5, ("free", "taken")),
    ("Blade", "weight", "plane", 7, ("keen", "dull")),
    ("Side", "points", "blues", 12, ("first", "second")),
)

_P241 = _page(
    "typed-dict",
    241,
    "A dict whose keys are written down",
    "TypedDict and Literal, for data that is a dict but has a shape.",
    "A lot of real data arrives as a dict - from JSON, from a database "
    "row - and turning it into a class is often more ceremony than it is "
    "worth. TypedDict says which keys it has and what each holds, so a "
    "checker catches a misspelt key while it stays an ordinary dict at "
    "runtime. Literal narrows a value to a fixed few: not any string, "
    "one of these. Neither does anything when the program runs, which is "
    "the point - all the work happens before you run it.",
    "typed_dict",
    [
        (
            "Import Literal and TypedDict from typing. Write a TypedDict "
            + cls
            + " with name hinted str and "
            + field
            + " hinted int. Set mode, hinted Literal of "
            + repr(modes[0])
            + " and "
            + repr(modes[1])
            + ", to the first. Set person, hinted "
            + cls
            + ", to a dict of name "
            + repr(name)
            + " and "
            + field
            + " "
            + repr(value)
            + ". Print the name, the "
            + field
            + ", and mode.",
            {
                "cls": cls,
                "field": field,
                "name": name,
                "value": value,
                "modes": modes,
            },
        )
        for cls, field, name, value, modes in _TYPED
    ],
)


# ── 242. Worked out once, then remembered ────────────────────

_CACHED = (
    ("Table", "total", (1, 2, 3)),
    ("Sheet", "sum_of", (10, 20, 30)),
    ("Ledger", "balance", (5, 5, 5, 5)),
    ("Report", "amount", (7, 14)),
    ("Basket", "price", (3, 12, 7)),
    ("Sheet", "total", (100, 200)),
    ("Board", "score", (9, 8, 7)),
    ("Stack", "height", (2, 4, 6, 8)),
    ("Batch", "count", (11, 22, 33)),
    ("Run", "distance", (5, 15, 25)),
    ("Bill", "owed", (45, 55)),
    ("Log", "size", (1, 1, 1, 1, 1)),
    ("Sheet_", "total", (2, 3, 4)),
    ("Column", "sum_of", (15, 25, 35)),
    ("Book_", "balance", (6, 6, 6, 6)),
    ("Notice", "amount", (8, 16)),
    ("Crate", "price", (4, 14, 9)),
    ("Panel", "score", (11, 10, 9)),
    ("Tier", "height", (3, 6, 9, 12)),
    ("Round_", "count", (12, 24, 36)),
)

_P242 = _page(
    "cached-property",
    242,
    "Worked out once, then remembered",
    "@cached_property, and the counter that proves it.",
    "A property from page 141 runs its method every single time you read "
    "it, which is right when the answer can change and wasteful when it "
    "cannot. cached_property runs once and stores the result on the "
    "object, so every read after the first is free. The counter here is "
    "the proof: the value is read twice and calls comes out as 1. The "
    "catch follows directly - if the underlying data changes, the cached "
    "answer is stale, so use it only where the answer will not move.",
    "cached_property",
    [
        (
            "Import cached_property from functools. Write a class "
            + cls
            + " whose __init__ stores rows and sets calls to 0, with a "
            "cached_property "
            + name
            + " that adds one to self.calls and returns the sum of rows. "
            "Make table holding ["
            + _seq(rows)
            + "], print its "
            + name
            + " twice, then print table.calls.",
            {"cls": cls, "name": name, "rows": rows},
        )
        for cls, name, rows in _CACHED
    ],
)


# ── 243. Bytes written as safe characters ────────────────────

_B64 = (
    "hello",
    "code coach",
    "ada lovelace",
    "python",
    "workbook",
    "the quick fox",
    "kyoto",
    "fingerprint",
    "one two three",
    "base sixty four",
    "a longer piece of text",
    "encode me",
    "morning",
    "code coach workbook",
    "grace hopper",
    "typescript",
    "exercise",
    "the slow dog",
    "ripon",
    "digest",
)

_P243 = _page(
    "base64-use",
    243,
    "Bytes written as safe characters",
    "base64, and what it is and is not for.",
    "base64 rewrites arbitrary bytes using 64 characters that survive "
    "being put in an email, a URL or a JSON string - which is the whole "
    "job. It is not encryption and hides nothing; anyone can decode it, "
    "as the second line does. The output is always a multiple of four "
    "characters, padded with equals signs if need be, which the third "
    "line checks. Note again that it takes bytes, so text is encoded "
    "first.",
    "base64_use",
    [
        (
            "Import base64. Set text to "
            + repr(word)
            + " and encoded to the b64encode of it as utf-8 bytes. Print "
            "encoded decoded as ascii, then the b64decode of it back to "
            "text, then the length of encoded modulo 4.",
            {"text": word},
        )
        for word in _B64
    ],
)


# ── 244. A time that knows where it is ───────────────────────

_TIMES = (
    ((2026, 9, 2, 12), 9),
    ((2026, 1, 1, 0), 5),
    ((2026, 6, 15, 18), -8),
    ((2000, 12, 31, 23), 1),
    ((1977, 1, 14, 6), 10),
    ((2026, 3, 15, 9), -5),
    ((2026, 7, 4, 15), 2),
    ((1985, 8, 16, 20), 8),
    ((2026, 11, 5, 7), -3),
    ((2026, 4, 10, 13), 5),
    ((2024, 2, 29, 11), 3),
    ((2026, 12, 25, 8), -7),
    ((2026, 5, 4, 14), 9),
    ((2026, 2, 28, 6), 5),
    ((2026, 7, 20, 17), -8),
    ((1999, 12, 31, 22), 1),
    ((1959, 3, 9, 8), 10),
    ((2026, 10, 15, 11), -5),
    ((2028, 2, 29, 16), 2),
    ((1980, 4, 21, 19), 8),
)

_P244 = _page(
    "aware-datetime",
    244,
    "A time that knows where it is",
    "tzinfo, astimezone, and the naive datetime that knows nothing.",
    "A datetime with no tzinfo is naive: it says 12 o'clock and cannot "
    "tell you where. Two naive times from different places compare as if "
    "they were the same clock, which is how meetings get missed and logs "
    "get sorted wrong. Attach a timezone and it becomes aware, and "
    "astimezone converts to another - the same instant, a different "
    "wall clock, which is why both isoformats end differently. Store "
    "times in UTC and convert when you show them.",
    "aware_datetime",
    [
        (
            "Import datetime, timedelta and timezone from datetime. Set "
            "naive to datetime("
            + ", ".join(str(n) for n in when)
            + ", 0), utc to naive with tzinfo replaced by timezone.utc, "
            "and far to utc converted with astimezone to a timezone of "
            + str(offset)
            + " hours. Print utc's isoformat, far's isoformat, then "
            "naive.tzinfo.",
            {"when": when, "offset": offset},
        )
        for when, offset in _TIMES
    ],
)


# ── 245. Several errors at once ──────────────────────────────

_GROUPS = (
    ("two problems", "bad value", "missing key", "value", "key"),
    ("both failed", "not a number", "no such id", "number", "id"),
    ("errors", "out of range", "unknown field", "range", "field"),
    ("trouble", "bad input", "absent", "input", "absent"),
    ("failures", "wrong type", "no entry", "type", "entry"),
    ("issues", "too small", "not found", "small", "found"),
    ("problems", "unreadable", "gone", "unreadable", "gone"),
    ("faults", "empty value", "missing name", "empty", "name"),
    ("both", "negative", "no key", "negative", "key"),
    ("collected", "bad format", "absent id", "format", "id"),
    ("several", "invalid", "unknown", "invalid", "unknown"),
    ("group", "bad data", "no record", "data", "record"),
    ("two faults", "bad figure", "absent key", "figure", "key"),
    ("both broke", "not numeric", "no such row", "numeric", "row"),
    ("errors here", "past the end", "unknown column", "end", "column"),
    ("bother", "bad entry", "vanished", "entry", "vanished"),
    ("breakages", "wrong shape", "no record", "shape", "record"),
    ("snags", "too few", "not present", "few", "present"),
    ("faults here", "unparsable", "removed", "unparsable", "removed"),
    ("defects", "blank value", "missing label", "blank", "label"),
)

_P245 = _page(
    "exception-group",
    245,
    "Several errors at once",
    "ExceptionGroup and except*, for work that fails in more than one way.",
    "Ordinary try/except handles one error, because raising one stops "
    "everything. But when several things ran together - a batch, a "
    "gather from page 208 - more than one can fail, and you want all of "
    "them rather than whichever was first. An ExceptionGroup carries "
    "them, and except* with a star catches the ones of a type out of the "
    "group and leaves the rest for the next clause. Note both clauses "
    "run here; that is the difference from ordinary except.",
    "exception_group",
    [
        (
            "Write work() raising an ExceptionGroup "
            + repr(label)
            + " holding a ValueError "
            + repr(value_message)
            + " and a KeyError "
            + repr(key_message)
            + ". Call it in a try, with an except* for ValueError "
            "printing "
            + repr(value_label)
            + " and the number of exceptions in the group, and an "
            "except* for KeyError printing "
            + repr(key_label)
            + " and the same.",
            {
                "label": label,
                "value_message": value_message,
                "key_message": key_message,
                "value_label": value_label,
                "key_label": key_label,
            },
        )
        for label, value_message, key_message, value_label, key_label in _GROUPS
    ],
)


# ── 246. A base class that notices its children ──────────────

_SUBCLASSES = (
    ("Plugin", ("Alpha", "Beta")),
    ("Handler", ("Json", "Xml")),
    ("Shape", ("Circle", "Square")),
    ("Reader", ("Csv", "Tsv")),
    ("Writer", ("Console", "File")),
    ("Rule", ("Length", "Format")),
    ("Command", ("Start", "Stop")),
    ("Codec", ("Utf8", "Latin1")),
    ("Store", ("Memory", "Disk")),
    ("Filter", ("Blur", "Sharpen")),
    ("Task", ("Build", "Deploy")),
    ("Check", ("Fast", "Deep")),
    ("Adapter", ("Gamma", "Delta")),
    ("Parser", ("Yaml", "Toml")),
    ("Figure", ("Ring", "Oblong")),
    ("Scanner", ("Tabs", "Commas")),
    ("Printer", ("Screen_", "Paper")),
    ("Test_", ("Length_", "Shape_")),
    ("Order_", ("Begin", "Halt")),
    ("Encoder", ("Ascii", "Unicode")),
)

_P246 = _page(
    "init-subclass",
    246,
    "A base class that notices its children",
    "__init_subclass__, which runs when someone inherits.",
    "This runs once per subclass, at the moment the subclass is defined "
    "- not when one is built. It is how a base class keeps a register of "
    "everything that inherits from it, which is the usual way a plugin "
    "system works: import the module and the classes announce "
    "themselves. It is also the polite alternative to a metaclass, which "
    "is the older way to do this and much harder to read. Always call "
    "super().__init_subclass__ so anything further up still runs.",
    "init_subclass",
    [
        (
            "Write a class "
            + base
            + " with a class attribute registry set to an empty list, and "
            "an __init_subclass__(cls, **kwargs) that calls "
            "super().__init_subclass__(**kwargs) and appends cls.__name__ "
            "to "
            + base
            + ".registry. Write "
            + " and ".join(children)
            + " inheriting it with pass, then print "
            + base
            + ".registry.",
            {"base": base, "children": children},
        )
        for base, children in _SUBCLASSES
    ],
)


# ── 247. Reading a function's own shape ──────────────────────

_SIGNATURES = (
    ("greet", ("name", "greeting='hello'", "times=1"), "greeting"),
    ("send", ("to", "subject='none'", "copies=0"), "to"),
    ("draw", ("shape", "colour='red'", "width=1"), "shape"),
    ("open_it", ("path", "mode='r'", "buffering=1"), "path"),
    ("scale", ("value", "factor=2", "offset=0"), "value"),
    ("report", ("rows", "title='report'", "limit=10"), "title"),
    ("connect", ("host", "port=8080", "retries=3"), "host"),
    ("write_it", ("text", "end='n'", "flush=0"), "text"),
    ("build", ("target", "mode='fast'", "jobs=4"), "target"),
    ("sort_by", ("items", "key='name'", "reverse=0"), "key"),
    ("wrap_it", ("text", "width=70", "indent=0"), "text"),
    ("fetch", ("url", "timeout=30", "tries=2"), "url"),
    ("hail", ("name", "greeting='morning'", "times=2"), "greeting"),
    ("post", ("to", "subject='blank'", "copies=1"), "to"),
    ("sketch", ("shape", "colour='teal'", "width=2"), "shape"),
    ("read_it", ("path", "mode='rb'", "buffering=8"), "path"),
    ("stretch", ("value", "factor=3", "offset=1"), "value"),
    ("summarise", ("rows", "title='summary'", "limit=25"), "title"),
    ("dial", ("host", "port=5173", "retries=4"), "host"),
    ("emit", ("text", "end='t'", "flush=1"), "text"),
)

_P247 = _page(
    "signature-use",
    247,
    "Reading a function's own shape",
    "inspect.signature, and what a program can know about itself.",
    "A function carries its own parameter list, and inspect hands it "
    "back as something you can print or walk. This is how argument "
    "checking, dependency injection, automatic command-line builders and "
    "half the decorators you have used know what they are wrapping - and "
    "it is also why @wraps on page 199 matters, since without it "
    "signature reports the wrapper's shape instead. Printing it is a "
    "quick way to check what a function you did not write expects.",
    "signature_use",
    [
        (
            "Import inspect. Write "
            + name
            + "("
            + ", ".join(params)
            + ") returning "
            + first
            + ". Print str of inspect.signature of it, then the list of "
            "its parameters.",
            {"name": name, "params": params, "first": first},
        )
        for name, params, first in _SIGNATURES
    ],
)


# ── 248. An object saved and brought back ────────────────────

_PICKLES = (
    ("ada", (1, 2, 3)),
    ("sam", (10, 20)),
    ("kim", (5,)),
    ("kyoto", (1463, 709)),
    ("iron", (26, 79)),
    ("dune", (412, 780)),
    ("reds", (41, 12, 30)),
    ("saw", (3, 8, 1)),
    ("sky", (3, 4)),
    ("north", (120, 40)),
    ("mix", (2, 3, 1)),
    ("alive", (245, 173)),
    ("finn", (2, 3, 4)),
    ("kit", (15, 25)),
    ("ida", (9,)),
    ("ripon", (17, 709)),
    ("tin", (50, 82)),
    ("ubik", (224, 261)),
    ("blues", (12, 55, 33)),
    ("plane", (7, 2, 4)),
)

_P248 = _page(
    "pickle-round",
    248,
    "An object saved and brought back",
    "pickle.dumps and loads, and when not to use them.",
    "pickle turns almost any Python object into bytes and back, nested "
    "structures and all, with no schema to write. That convenience is "
    "also the warning: loading a pickle can run arbitrary code, so never "
    "unpickle anything that came from somewhere you do not trust, and "
    "the format is Python-only and version-fragile, so it is wrong for "
    "anything another program or a later you has to read. For those, "
    "use JSON from page 137. For a cache you wrote an hour ago, pickle "
    "is exactly right.",
    "pickle_round",
    [
        (
            "Import pickle. Set data to a dict of name "
            + repr(name)
            + " and scores ["
            + _seq(scores)
            + "]. Dump it to raw, load it back into back, then print "
            "back's name, back's scores, and whether back == data.",
            {"name": name, "scores": scores},
        )
        for name, scores in _PICKLES
    ],
)


CORNER_PAGES: tuple[Page, ...] = (
    _P239,
    _P240,
    _P241,
    _P242,
    _P243,
    _P244,
    _P245,
    _P246,
    _P247,
    _P248,
)
