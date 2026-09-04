"""TypeScript intermediate pages 81-90: the start of its own book.

The third book. Python went deep first, then JavaScript, and TypeScript
is the natural next one - it is the JavaScript of pages 81-160 with the
part that catches mistakes before anything runs.

Numbered from 81 because that is where TypeScript's own book is up to;
the shared beginner and practice tiers end at 80, exactly as they do for
Python and JavaScript.

Worth knowing while you work through these: the runner type-checks
rather than only stripping the types. An annotation that does not hold
stops the exercise with a compiler error instead of running anyway,
which is the entire reason the language exists.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

TYPESCRIPT = ("typescript",)


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
        languages=TYPESCRIPT,
        tier="intermediate",
    )


def _seq(items) -> str:
    return ", ".join(str(v) for v in items)


# ── 81. Saying what a variable and a function hold ───────────

_ANNOTATIONS = (
    ("ada", 36, "greet"),
    ("sam", 41, "hail"),
    ("kim", 29, "call"),
    ("jo", 17, "name_it"),
    ("max", 50, "say"),
    ("eve", 22, "show"),
    ("abe", 64, "tell"),
    ("ida", 38, "give"),
    ("ben", 45, "mark"),
    ("rey", 19, "note"),
    ("finn", 27, "label"),
    ("nell", 33, "read"),
    ("gus", 31, "greet_it"),
    ("hal", 47, "hail_to"),
    ("ivy", 25, "call_out"),
    ("jan", 52, "title_it"),
    ("kit", 40, "state_it"),
    ("lee", 18, "show_it"),
    ("mia", 61, "tell_of"),
    ("noa", 34, "give_it"),
)

_P81 = _page(
    "ts-annotate",
    81,
    "Saying what a variable and a function hold",
    "A colon and a type, on a variable and on a function.",
    "The syntax is the same everywhere: a colon then the type. On a "
    "parameter it says what may be passed; after the brackets it says "
    "what comes back. TypeScript would work out both of these on its own "
    "- it is very good at that - so annotating a const holding a string "
    "is usually noise. Annotate the edges: parameters, return types, and "
    "anything arriving from outside your program. Note the last line "
    "prints number, because typeof is a JavaScript question and the "
    "types are gone by the time it runs.",
    "ts_annotate",
    [
        (
            "Set who to "
            + repr(name)
            + " annotated as string and count to "
            + str(count)
            + " annotated as number, both const. Write "
            + func
            + "(name: string, times: number) returning a string, whose "
            "body returns a template literal of the two with a space "
            "between. Log it called with who and count, then typeof "
            "count.",
            {"name": name, "count": count, "func": func},
        )
        for name, count, func in _ANNOTATIONS
    ],
)


# ── 82. A shape with a name ──────────────────────────────────

_INTERFACES = (
    ("Point", "x", "y", (2, 3), "Label", "here"),
    ("Size", "width", "height", (10, 4), "Name", "large"),
    ("Span", "low", "high", (3, 17), "Tag", "range"),
    ("Pair", "left", "right", (7, 8), "Note", "both"),
    ("Room", "floor", "number", (3, 12), "Title", "attic"),
    ("Score", "points", "bonus", (40, 7), "Grade", "pass"),
    ("Grid", "rows", "cols", (8, 9), "Kind", "square"),
    ("Trip", "miles", "hours", (120, 3), "Route", "north"),
    ("Tank", "full", "used", (60, 22), "Fuel", "petrol"),
    ("Bill", "price", "people", (45, 3), "Currency", "pence"),
    ("Wall", "bricks", "rows", (90, 6), "Style", "flemish"),
    ("Gap", "start", "end", (7, 31), "Unit", "days"),
    ("Coord", "x", "y", (7, 9), "Caption", "there"),
    ("Extent", "width", "height", (64, 48), "Naming", "wide"),
    ("Reach", "low", "high", (11, 47), "Marker", "span"),
    ("Duo", "left", "right", (11, 12), "Remark", "either"),
    ("Berth", "floor", "number", (5, 14), "Heading", "cabin"),
    ("Result", "points", "bonus", (72, 9), "Banding", "merit"),
    ("Board", "rows", "cols", (6, 7), "Sort_", "oblong"),
    ("Journey", "miles", "hours", (180, 4), "Track_", "south"),
)

_P82 = _page(
    "ts-interface",
    82,
    "A shape with a name",
    "interface for an object shape, type for a name of your own.",
    "An interface describes what an object must have. A type alias gives "
    "any type a name, including a plain string. They overlap almost "
    "entirely, and the working rule is simple: interface for the shape "
    "of an object, type for everything else - unions, tuples, functions, "
    "aliases. Interfaces can be reopened and added to later, which is "
    "occasionally useful and usually not what you want.",
    "ts_interface",
    [
        (
            "Write an interface "
            + cls
            + " with "
            + first
            + " and "
            + second
            + ", both number, and a type alias "
            + alias
            + " for string. Make thing typed as "
            + cls
            + " holding "
            + _seq(values)
            + ", and tag typed as "
            + alias
            + " holding "
            + repr(tag)
            + ". Log the two numbers added, then tag.",
            {
                "cls": cls,
                "first": first,
                "second": second,
                "values": values,
                "alias": alias,
                "tag": tag,
            },
        )
        for cls, first, second, values, alias, tag in _INTERFACES
    ],
)


# ── 83. One of two types, and telling them apart ─────────────

_UNIONS = (
    ("show", "number", "text", 5, 2, "ada"),
    ("render", "digits", "letters", 7, 3, "sam"),
    ("describe", "count", "word", 4, 10, "kim"),
    ("give", "value", "name", 9, 5, "jo"),
    ("label", "amount", "title", 6, 4, "max"),
    ("read", "figure", "phrase", 8, 2, "eve"),
    ("tell", "total", "label", 3, 7, "abe"),
    ("say", "sum", "note", 11, 2, "ida"),
    ("mark", "score", "tag", 12, 3, "ben"),
    ("note_it", "size", "kind", 2, 9, "rey"),
    ("form", "level", "style", 10, 5, "finn"),
    ("check", "rank", "grade", 1, 8, "nell"),
    ("render_it", "number", "text", 6, 3, "gus"),
    ("display", "digits", "letters", 8, 4, "hal"),
    ("explain", "count", "word", 5, 11, "ivy"),
    ("hand_over", "value", "name_of", 10, 6, "jan"),
    ("caption", "amount", "title", 7, 5, "kit"),
    ("recite", "figure", "phrase", 9, 3, "lee"),
    ("report", "total", "label", 4, 8, "mia"),
    ("utter", "sum", "note", 12, 3, "noa"),
)

_P83 = _page(
    "ts-union-narrow",
    83,
    "One of two types, and telling them apart",
    "A union, and narrowing it with typeof.",
    "string | number says the value is one of those, and until you find "
    "out which, TypeScript will only let you do what is safe for both - "
    "so toUpperCase is refused and so is multiplying. A typeof check "
    "narrows it: inside the if the compiler knows it is a number, and "
    "after the if it knows it is a string, with no cast and no help from "
    "you. That narrowing is the single most useful thing the type system "
    "does.",
    "ts_union_narrow",
    [
        (
            "Write "
            + func
            + "(value: string | number) returning a string. When typeof "
            "says it is a number, return a template literal of "
            + repr(number_word)
            + " and the value times "
            + str(times)
            + "; otherwise return one of "
            + repr(text_word)
            + " and the value upper-cased. Log it called with "
            + str(number)
            + ", then with "
            + repr(text)
            + ".",
            {
                "func": func,
                "number_word": number_word,
                "text_word": text_word,
                "number": number,
                "times": times,
                "text": text,
            },
        )
        for func, number_word, text_word, number, times, text in _UNIONS
    ],
)


# ── 84. A property that might not be there ───────────────────

_OPTIONALS = (
    ("Settings", "host", "port", "local", 9000, 8080),
    ("Config", "name", "size", "main", 50, 10),
    ("Options", "mode", "level", "safe", 3, 1),
    ("Params", "target", "depth", "all", 5, 2),
    ("Setup", "region", "count", "eu", 12, 4),
    ("Profile", "user", "age", "ada", 36, 0),
    ("Entry", "label", "order", "first", 7, 1),
    ("Record_", "kind", "score", "test", 90, 50),
    ("Field", "key", "width", "id", 30, 20),
    ("Route", "path", "hops", "home", 4, 1),
    ("Task", "title", "priority", "mix", 9, 5),
    ("Item", "code", "qty", "abc", 24, 1),
    ("Preferences", "host", "port", "remote", 5173, 8765),
    ("Defaults", "name_of", "size", "index", 80, 20),
    ("Choices", "mode", "level", "fast", 4, 2),
    ("Bounds", "target", "depth", "some", 8, 3),
    ("Layout", "region", "count", "us", 16, 5),
    ("Account_", "user", "age", "finn", 27, 0),
    ("Line_", "label", "order", "second", 9, 2),
    ("Slot_", "kind", "score", "live", 95, 60),
)

_P84 = _page(
    "ts-optional",
    84,
    "A property that might not be there",
    "A question mark on a property, and the fallback it forces.",
    "A question mark makes the property optional, so its type is really "
    "number | undefined - and TypeScript will not let you use it as a "
    "number until you have dealt with the undefined. ?? is the neat way, "
    "and it is the JavaScript from page 89 doing the work while the type "
    "system insists you write it. Note optional is not the same as "
    "allowing undefined explicitly: an optional property may be left out "
    "entirely, which is what the second call does.",
    "ts_optional",
    [
        (
            "Write an interface "
            + cls
            + " with "
            + always
            + " as string and an optional "
            + maybe
            + " as number. Write describe(thing) returning a template "
            "literal of the "
            + always
            + ", a colon, and the "
            + maybe
            + " with "
            + str(fallback)
            + " as its fallback. Log it called with both given ("
            + repr(value)
            + " and "
            + str(given)
            + "), then with only the "
            + always
            + ".",
            {
                "cls": cls,
                "always": always,
                "maybe": maybe,
                "value": value,
                "given": given,
                "fallback": fallback,
            },
        )
        for cls, always, maybe, value, given, fallback in _OPTIONALS
    ],
)


# ── 85. A fixed pair, and an array that cannot change ────────

_TUPLES = (
    ("ada", 36, (1, 2, 3)),
    ("sam", 41, (5, 6)),
    ("kim", 29, (7, 8, 9, 10)),
    ("jo", 17, (2, 4)),
    ("max", 50, (1, 1, 1)),
    ("eve", 22, (3, 6, 9)),
    ("abe", 64, (10, 20)),
    ("ida", 38, (4, 8, 12, 16)),
    ("ben", 45, (11,)),
    ("rey", 19, (5, 10, 15)),
    ("finn", 27, (2, 3, 5, 7)),
    ("nell", 33, (100, 200)),
    ("gus", 31, (2, 3, 4)),
    ("hal", 47, (6, 7)),
    ("ivy", 25, (8, 9, 10, 11)),
    ("jan", 52, (3, 5)),
    ("kit", 40, (2, 2, 2)),
    ("lee", 18, (4, 8, 12)),
    ("mia", 61, (15, 25)),
    ("noa", 34, (5, 10, 15, 20)),
)

_P85 = _page(
    "ts-tuple",
    85,
    "A fixed pair, and an array that cannot change",
    "A tuple type, and readonly on an array.",
    "[string, number] is a tuple: exactly two items, in that order, of "
    "those types - which is different from (string | number)[], an array "
    "of any length holding either. Tuples are what a function returning "
    "two things should say. readonly number[] refuses push, pop and "
    "assignment to an index, at compile time only: nothing changes at "
    "run time, and the array is a perfectly ordinary one underneath.",
    "ts_tuple",
    [
        (
            "Set pair to a tuple typed [string, number] holding "
            + repr(name)
            + " and "
            + str(count)
            + ", const. Set fixed to a readonly number array holding ["
            + _seq(items)
            + "]. Destructure who and many out of pair, then log who, "
            "many, and the length of fixed.",
            {"name": name, "count": count, "items": items},
        )
        for name, count, items in _TUPLES
    ],
)


# ── 86. A function that keeps the type it was given ──────────

_GENERIC_FNS = (
    ("firstOf", (1, 2, 3), ("a", "b")),
    ("head", (10, 20), ("red", "green")),
    ("front", (7,), ("mon", "tue")),
    ("startOf", (5, 6, 7), ("do", "re")),
    ("earliest", (100, 200), ("iron", "gold")),
    ("topOf", (9, 8), ("up", "down")),
    ("lead", (1, 1, 2), ("yes", "no")),
    ("startsWith_", (42,), ("north", "south")),
    ("initial", (3, 6, 9), ("left", "right")),
    ("firstItem", (11, 22), ("hot", "cold")),
    ("began", (0, 1), ("sky", "sea")),
    ("peek", (12, 24, 36), ("one", "two")),
    ("firstIn", (4, 5, 6), ("c", "d")),
    ("leadOf", (15, 25), ("gold", "tin")),
    ("openOf", (11,), ("thu", "fri")),
    ("beginOf", (8, 9, 10), ("la", "ti")),
    ("soonest", (300, 400), ("oak", "ash")),
    ("crownOf", (12, 11), ("in", "out")),
    ("foremost", (2, 2, 3), ("on", "off")),
    ("openingOf", (55,), ("east", "west")),
)

_P86 = _page(
    "ts-generic-fn",
    86,
    "A function that keeps the type it was given",
    "A type parameter, so the answer's type follows the argument's.",
    "T is a name for a type you do not know yet. items: T[] and a return "
    "of T say the answer is whatever the array held - so a number array "
    "gives a number and a string array gives a string, and the compiler "
    "knows which without being told twice. Written as any it would "
    "compile and tell you nothing. This is the TypeScript version of the "
    "Python book's page 217, and the reason generics exist at all.",
    "ts_generic_fn",
    [
        (
            "Write "
            + func
            + "<T>(items: T[]) returning T, whose body returns the first "
            "item. Log it called with the type argument number on ["
            + _seq(numbers)
            + "], then with string on ["
            + ", ".join(repr(w) for w in words)
            + "].",
            {"func": func, "numbers": numbers, "words": words},
        )
        for func, numbers, words in _GENERIC_FNS
    ],
)


# ── 87. A class that holds one type ──────────────────────────

_GENERIC_CLASSES = (
    ("Box", "get", 5, "hello"),
    ("Holder", "value", 42, "world"),
    ("Wrapper", "unwrap", 7, "text"),
    ("Cell", "read", 100, "data"),
    ("Slot", "take", 1, "ada"),
    ("Case", "open_it", 9, "sam"),
    ("Store", "fetch", 12, "kim"),
    ("Bag", "out", 33, "red"),
    ("Crate", "peek", 8, "blue"),
    ("Tin", "inside", 64, "gold"),
    ("Pack", "contents", 21, "iron"),
    ("Jar", "pour", 3, "salt"),
    ("Case_", "get", 6, "morning"),
    ("Keeper", "value", 51, "evening"),
    ("Sleeve", "unwrap", 8, "words"),
    ("Pocket", "read_it", 200, "notes"),
    ("Niche", "take", 2, "finn"),
    ("Chest", "open_up", 11, "ida"),
    ("Depot", "fetch", 14, "kit"),
    ("Sack", "out", 44, "teal"),
)

_P87 = _page(
    "ts-generic-class",
    87,
    "A class that holds one type",
    "A generic class, and a parameter property.",
    "Box<number> and Box<string> are different types to the compiler and "
    "one class at run time, so get() is known to give back what went in. "
    "The constructor here uses a parameter property - writing private in "
    "front of the parameter declares the field and assigns it in one "
    "go, which is TypeScript's own shorthand and saves the two lines "
    "every JavaScript constructor writes.",
    "ts_generic_class",
    [
        (
            "Write a class "
            + cls
            + "<T> whose constructor takes a private item of type T, with "
            "a method "
            + method
            + " returning T. Log a new "
            + cls
            + " of number holding "
            + str(number)
            + " with the method called, then one of string holding "
            + repr(word)
            + ".",
            {"cls": cls, "method": method, "number": number, "word": word},
        )
        for cls, method, number, word in _GENERIC_CLASSES
    ],
)


# ── 88. A type that is one of these exact values ─────────────

_LITERALS = (
    ("Mode", ("read", "write"), (1, 2, 3)),
    ("Level", ("low", "high"), (10, 20)),
    ("Colour", ("red", "green", "blue"), (5, 6, 7, 8)),
    ("State", ("open", "shut"), (2, 4)),
    ("Sort", ("asc", "desc"), (9,)),
    ("Kind", ("text", "binary"), (1, 1, 1)),
    ("Turn", ("left", "right"), (3, 6, 9)),
    ("Size", ("small", "large"), (100, 200)),
    ("Face", ("heads", "tails"), (11, 22, 33)),
    ("Way", ("north", "south"), (4, 8)),
    ("Step", ("mix", "bake"), (7, 14, 21)),
    ("Tier", ("free", "paid"), (12, 24, 36, 48)),
    ("Mood", ("calm", "busy"), (2, 3, 4)),
    ("Grade_", ("low", "high"), (15, 25)),
    ("Shade", ("teal", "amber", "plum"), (6, 7, 8, 9)),
    ("Gate", ("open", "shut"), (3, 5)),
    ("Order_", ("up", "down"), (11,)),
    ("Form", ("plain", "rich"), (2, 2, 2)),
    ("Bearing", ("east", "west"), (4, 8, 12)),
    ("Scale_", ("small", "large"), (300, 400)),
)

_P88 = _page(
    "ts-literal",
    88,
    "A type that is one of these exact values",
    "String literal types, and as const.",
    "A literal type is a type with exactly one value in it, and a union "
    "of them is how you say this may only be one of these words. That is "
    "far better than string: a typo is caught where it is written, and "
    "your editor offers the choices. as const on an array makes every "
    "item a literal type and the whole thing readonly, which is how you "
    "get a list of allowed values and a type derived from it without "
    "writing the list twice.",
    "ts_literal",
    [
        (
            "Write a type "
            + alias
            + " that is one of "
            + " or ".join(repr(c) for c in choices)
            + ". Set chosen typed as "
            + alias
            + " to "
            + repr(choices[0])
            + ", and sizes to ["
            + _seq(items)
            + "] with as const. Log chosen, then the length of sizes, "
            "then its first item.",
            {"alias": alias, "choices": choices, "items": items},
        )
        for alias, choices, items in _LITERALS
    ],
)


# ── 89. Types built out of another type ──────────────────────

_UTILITIES = (
    ("User", "name", "age", "email", "ada", "sam", 36),
    ("Book", "title", "pages", "isbn", "dune", "ilium", 412),
    ("City", "name", "people", "country", "kyoto", "oslo", 1463),
    ("Song", "title", "seconds", "album", "alive", "heroes", 245),
    ("Metal", "name", "number", "symbol", "iron", "gold", 26),
    ("Room", "name", "floor", "wing", "attic", "cellar", 4),
    ("Tool", "name", "weight", "brand", "saw", "axe", 3),
    ("Team", "name", "points", "league", "reds", "blues", 41),
    ("Trip", "name", "miles", "route", "north", "south", 120),
    ("Task", "name", "order", "owner", "mix", "bake", 2),
    ("Item", "name", "qty", "code", "bolt", "nut", 24),
    ("Note", "name", "length", "author", "first", "second", 9),
    ("Reader_", "name_of", "age", "email", "finn", "ida", 27),
    ("Volume", "title", "pages", "isbn", "ubik", "valis", 224),
    ("Town", "name_of", "people", "country", "ripon", "oslo", 17),
    ("Track_", "title", "seconds", "album", "art", "sons", 224),
    ("Ore", "name_of", "number", "symbol", "tin", "lead", 50),
    ("Berth", "name_of", "floor", "wing", "cabin", "hold", 5),
    ("Blade", "name_of", "weight", "brand", "plane", "chisel", 7),
    ("Side", "name_of", "points", "league", "blues", "whites", 12),
)

_P89 = _page(
    "ts-utility",
    89,
    "Types built out of another type",
    "Partial, Pick, Omit and Record.",
    "Rather than writing a second interface with the same fields made "
    "optional, derive it. Partial makes every property optional - which "
    "is what a draft or a patch is. Pick keeps only the properties you "
    "name and Omit drops them. Record builds a type of keys to values, "
    "which is what a dictionary is. Deriving matters because the derived "
    "types follow when the original changes, and a second interface "
    "written by hand quietly drifts.",
    "ts_utility",
    [
        (
            "Write an interface "
            + cls
            + " with "
            + first
            + " and "
            + third
            + " as string and "
            + second
            + " as number. Derive Draft as Partial of it, JustOne as Pick "
            "of just "
            + repr(first)
            + ", Without as Omit of "
            + repr(third)
            + ", and Counts as Record of string to number. Make one value "
            "of each - draft with "
            + repr(name)
            + ", one with "
            + repr(other)
            + ", without with "
            + repr(name)
            + " and "
            + str(number)
            + ", counts with "
            + name
            + " set to "
            + str(number)
            + " - and log the four values.",
            {
                "cls": cls,
                "first": first,
                "second": second,
                "third": third,
                "name": name,
                "other": other,
                "number": number,
            },
        )
        for cls, first, second, third, name, other, number in _UTILITIES
    ],
)


# ── 90. A tag that tells the compiler which one ──────────────

_DISCRIMINATED = (
    ("Shape", "circle", "square", "radius", "side", 4, "area", (3, 5)),
    ("Event_", "click", "scroll", "count", "amount", 2, "measure", (4, 6)),
    ("Node_", "leaf", "branch", "depth", "width", 3, "size_of", (5, 7)),
    ("Cell", "empty", "full", "row", "col", 5, "weigh", (2, 8)),
    ("Move", "step", "jump", "paces", "height", 6, "cost", (6, 3)),
    ("Job", "quick", "slow", "seconds", "minutes", 60, "duration", (7, 2)),
    ("Load", "light", "heavy", "kilos", "tonnes", 1000, "mass", (8, 4)),
    ("Path", "flat", "hill", "metres", "climb", 2, "effort", (9, 5)),
    ("Price", "net", "gross", "pence", "pounds", 100, "total", (3, 9)),
    ("Sound", "beep", "tone", "hertz", "seconds", 8, "value_of", (4, 7)),
    ("Room", "single", "double", "beds", "guests", 2, "capacity", (5, 6)),
    ("Draw", "line", "box", "length", "sides", 4, "extent", (6, 8)),
    ("Figure", "round", "oblong", "radius", "side", 5, "area_of", (4, 6)),
    ("Signal", "press", "swipe", "count", "amount", 3, "gauge", (5, 7)),
    ("Twig", "tip", "fork", "depth", "width", 4, "extent_of", (6, 8)),
    ("Tile", "blank", "filled", "row", "col", 6, "weight_of", (3, 9)),
    ("Hop", "stride", "leap", "paces", "height", 7, "cost_of", (7, 4)),
    ("Chore", "brief", "long", "seconds", "minutes", 90, "span_of", (8, 3)),
    ("Weight_", "slight", "vast", "kilos", "tonnes", 500, "mass_of", (9, 5)),
    ("Way_", "level", "steep", "metres", "climb", 3, "toil", (2, 6)),
)

_P90 = _page(
    "ts-discriminated",
    90,
    "A tag that tells the compiler which one",
    "A discriminated union, and a switch that narrows on the tag.",
    "Give every member of a union a literal field with a different "
    "value, and switching on that field narrows the type inside each "
    "case - so the compiler knows the circle has a radius and the square "
    "does not, and refuses the wrong field. This is the shape almost all "
    "well-typed JavaScript data ends up in. The best part is what "
    "happens later: add a third member and every switch missing a case "
    "stops compiling, which is how the type system tells you where the "
    "work is.",
    "ts_discriminated",
    [
        (
            "Write a type "
            + alias
            + " that is either an object with kind "
            + repr(first)
            + " and a number "
            + first_field
            + ", or kind "
            + repr(second)
            + " and a number "
            + second_field
            + ". Write "
            + func
            + "(thing) returning a number, switching on kind: the first "
            "gives the field times itself, the second gives its field "
            "times "
            + str(second_times)
            + ". Log it for the first with "
            + str(values[0])
            + ", then the second with "
            + str(values[1])
            + ".",
            {
                "alias": alias,
                "first": first,
                "second": second,
                "first_field": first_field,
                "second_field": second_field,
                "second_times": second_times,
                "func": func,
                "values": values,
            },
        )
        for (
            alias,
            first,
            second,
            first_field,
            second_field,
            second_times,
            func,
            values,
        ) in _DISCRIMINATED
    ],
)


TS_PAGES: tuple[Page, ...] = (
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
