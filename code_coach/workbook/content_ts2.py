"""TypeScript intermediate pages 91-100: narrowing properly, and types
that compute.

The rest of narrowing - the in operator, and a type guard you write
yourself. unknown, which is any with the safety left on. keyof and index
signatures. Generic constraints. Then the part of TypeScript that is its
own small language running at compile time: mapped types, conditional
types with infer, and satisfies.

Page 100 is the one worth knowing about soonest. satisfies checks a
value against a type without widening it to that type, which is the
thing every config object has always wanted.
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


# ── 91. Telling two shapes apart by a key ────────────────────

_INS = (
    ("Dog", "bark", "Cat", "meow", "speak", "woof", "miaow"),
    ("Car", "wheels", "Boat", "sails", "describe", "four", "two"),
    ("Article", "words", "Picture", "pixels", "show", "many", "millions"),
    ("Note", "pitch", "Rest", "silence", "play", "high", "none"),
    ("Row", "cells", "Header", "title", "render", "three", "top"),
    ("Doc", "bytes", "Folder", "children", "tell", "large", "several"),
    ("Post", "body", "Draft", "outline", "read", "written", "sketched"),
    ("Task", "doing", "Done", "finished", "state_of", "in hand", "complete"),
    ("Order", "items", "Quote", "estimate", "sum_up", "listed", "guessed"),
    ("Live", "stream", "Recorded", "tape", "source_of", "now", "earlier"),
    ("Local", "path", "Remote", "url", "locate", "on disk", "over there"),
    ("Fresh", "picked", "Frozen", "stored", "label", "today", "last year"),
)

_P91 = _page(
    "ts-narrow-in",
    91,
    "Telling two shapes apart by a key",
    "The in operator, which narrows a union of object types.",
    "typeof only distinguishes the primitives, so it is no help between "
    "two interfaces - they are both objects. The in operator asks "
    "whether a key exists, and TypeScript treats that as narrowing: "
    "inside the if it knows which one it has, and after it knows the "
    "other. This is the lightweight version of the discriminated union "
    "from page 90, and worth preferring when you cannot add a tag field "
    "because the data comes from somewhere you do not control.",
    "ts_narrow_in",
    [
        (
            "Write interfaces "
            + first_cls
            + " with "
            + first_field
            + " as string and "
            + second_cls
            + " with "
            + second_field
            + " as string. Write "
            + func
            + " taking one of the two and returning a string, using an in "
            "check on "
            + repr(first_field)
            + " to return that field, otherwise the other. Log it with "
            + repr(first_says)
            + ", then with "
            + repr(second_says)
            + ".",
            {
                "first_cls": first_cls,
                "first_field": first_field,
                "second_cls": second_cls,
                "second_field": second_field,
                "func": func,
                "first_says": first_says,
                "second_says": second_says,
            },
        )
        for (
            first_cls,
            first_field,
            second_cls,
            second_field,
            func,
            first_says,
            second_says,
        ) in _INS
    ],
)


# ── 92. A check the compiler believes ────────────────────────

_GUARDS = (
    ("Fish", "swim", "Bird", "fly", "isFish", "move", (5, 9)),
    ("Car", "wheels", "Plane", "wings", "isCar", "travel", (4, 2)),
    ("Book", "pages", "Film", "minutes", "isBook", "consume", (412, 120)),
    ("Song", "beats", "Poem", "lines", "isSong", "perform", (120, 14)),
    ("Cup", "millilitres", "Plate", "diameter", "isCup", "serve", (250, 30)),
    ("Coin", "value", "Note", "amount", "isCoin", "spend", (50, 500)),
    ("Stair", "steps", "Ramp", "slope", "isStair", "climb", (12, 5)),
    ("Bike", "gears", "Cart", "loads", "isBike", "ride", (21, 3)),
    ("Well", "depth", "Pond", "area", "isWell", "measure", (30, 400)),
    ("Bulb", "watts", "Candle", "hours", "isBulb", "light_it", (60, 8)),
    ("Rope", "metres", "Chain", "links", "isRope", "reach", (25, 60)),
    ("Drum", "skins", "Flute", "holes", "isDrum", "sound_it", (2, 6)),
)

_P92 = _page(
    "ts-type-guard",
    92,
    "A check the compiler believes",
    "A predicate returning `thing is Type`, and what that promises.",
    "Sometimes the check is too complicated for the compiler to follow, "
    "so you tell it: a return type of `thing is Fish` says that when this "
    "function returns true, treat the argument as a Fish from here on. "
    "The important part is that TypeScript takes your word for it. If "
    "the body is wrong, nothing complains and the narrowing is simply a "
    "lie - which makes a type guard a small, sharp tool to write "
    "carefully and to reach for only when narrowing will not happen on "
    "its own.",
    "ts_type_guard",
    [
        (
            "Write interfaces "
            + first_cls
            + " with a number "
            + first_field
            + " and "
            + second_cls
            + " with a number "
            + second_field
            + ". Write "
            + guard
            + " taking one of the two, returning that it is a "
            + first_cls
            + ", whose body casts and checks the field is not undefined. "
            "Write "
            + func
            + " that uses it to return a template literal of the field "
            "name and value for whichever it is. Log it with "
            + str(values[0])
            + ", then with "
            + str(values[1])
            + ".",
            {
                "first_cls": first_cls,
                "first_field": first_field,
                "second_cls": second_cls,
                "second_field": second_field,
                "guard": guard,
                "func": func,
                "values": values,
            },
        )
        for (
            first_cls,
            first_field,
            second_cls,
            second_field,
            guard,
            func,
            values,
        ) in _GUARDS
    ],
)


# ── 93. A value you have to ask about first ──────────────────

_UNKNOWNS = (
    ("lengthOf", "hello", (1, 2, 3), 42, 0),
    ("sizeOf", "world", (5, 6), 7, 0),
    ("countOf", "typescript", (1, 1, 1, 1), 100, 0),
    ("measure", "ada", (2, 4, 6), 9, 0),
    ("howBig", "sam", (10,), 3, 0),
    ("extentOf", "kim", (1, 2), 55, 0),
    ("widthOf", "node", (7, 8, 9), 12, 0),
    ("depthOf", "code", (3,), 64, 0),
    ("spanOf", "python", (4, 5, 6, 7), 21, 0),
    ("reachOf", "rust", (11, 22), 8, 0),
    ("scaleOf", "dart", (2, 3, 5), 30, 0),
    ("countIt", "java", (9,), 15, 0),
)

_P93 = _page(
    "ts-unknown",
    93,
    "A value you have to ask about first",
    "unknown, which is any with the checking left switched on.",
    "any switches the type system off for that value: every property "
    "access compiles and every one of them might blow up at run time. "
    "unknown says the same thing about what you know and the opposite "
    "about what you may do - nothing at all, until you have narrowed it. "
    "That makes it the right type for anything arriving from outside: "
    "parsed JSON, a caught error, a value from an untyped library. Reach "
    "for unknown by default and any essentially never.",
    "ts_unknown",
    [
        (
            "Write "
            + func
            + "(value: unknown) returning a number: the length when "
            "typeof says string, the length when Array.isArray says so, "
            "and otherwise "
            + str(fallback)
            + ". Log it with "
            + repr(word)
            + ", then with ["
            + _seq(items)
            + "], then with "
            + str(number)
            + ".",
            {
                "func": func,
                "word": word,
                "items": items,
                "number": number,
                "fallback": fallback,
            },
        )
        for func, word, items, number, fallback in _UNKNOWNS
    ],
)


# ── 94. The keys of a type, as a type ────────────────────────

_KEYOFS = (
    ("Scores", "Person", "name", "age", "ada", "kim", 41),
    ("Counts", "Book", "title", "pages", "dune", "ilium", 412),
    ("Totals", "City", "name", "people", "kyoto", "oslo", 709),
    ("Tallies", "Song", "title", "seconds", "alive", "kooks", 173),
    ("Sums", "Metal", "name", "number", "iron", "gold", 79),
    ("Marks", "Room", "name", "floor", "attic", "hall", 1),
    ("Weights", "Tool", "name", "weight", "saw", "axe", 8),
    ("Points", "Team", "name", "score", "reds", "blues", 12),
    ("Miles", "Trip", "name", "distance", "north", "south", 40),
    ("Orders", "Task", "name", "step", "mix", "bake", 3),
    ("Sizes", "Item", "name", "qty", "bolt", "nut", 24),
    ("Lengths", "Note", "name", "words", "first", "second", 9),
)

_P94 = _page(
    "ts-keyof",
    94,
    "The keys of a type, as a type",
    "keyof, and an index signature for keys you cannot list.",
    "keyof Person is the type 'name' | 'age' - the key names as a union "
    "of literal types, worked out from the interface rather than written "
    "twice. A function taking keyof Person can then only be passed a "
    "real key, and a typo is caught where it is written. An index "
    "signature is the other direction, for an object whose keys are not "
    "known in advance, which is what a lookup table is. Between them "
    "they cover both kinds of object.",
    "ts_keyof",
    [
        (
            "Write an interface "
            + table
            + " with a string index signature giving numbers, and an "
            "interface "
            + cls
            + " with "
            + first
            + " as string and "
            + second
            + " as number. Make Field a type alias for keyof "
            + cls
            + ". Set scores typed "
            + table
            + " holding "
            + name
            + " as "
            + str(number)
            + ", and field typed Field to "
            + repr(second)
            + ". Write pick(thing, key: Field) returning string or "
            "number. Log the score, then field, then pick on an object "
            "holding "
            + repr(other)
            + " and "
            + str(number)
            + ", asked for "
            + repr(first)
            + ".",
            {
                "table": table,
                "cls": cls,
                "first": first,
                "second": second,
                "name": name,
                "other": other,
                "number": number,
            },
        )
        for table, cls, first, second, name, other, number in _KEYOFS
    ],
)


# ── 95. A generic that demands something ─────────────────────

_CONSTRAINTS = (
    ("longest", "hello", "hi", (1, 2, 3), (1,)),
    ("bigger", "typescript", "ts", (5, 6, 7, 8), (5, 6)),
    ("widest", "javascript", "js", (1, 1, 1), (1,)),
    ("longer", "python", "py", (2, 4, 6, 8), (2,)),
    ("greater", "workbook", "book", (9, 8, 7), (9,)),
    ("larger", "exercise", "task", (3, 6, 9, 12), (3, 6)),
    ("fuller", "language", "code", (10, 20, 30), (10,)),
    ("deeper", "compiler", "tool", (4, 8), (4,)),
    ("broader", "keyboard", "keys", (11, 22, 33), (11, 22)),
    ("taller", "mountain", "hill", (7, 14, 21), (7,)),
    ("heavier", "elephant", "mouse", (100, 200), (100,)),
    ("wider", "horizon", "edge", (6, 12, 18, 24), (6, 12)),
)

_P95 = _page(
    "ts-constraint",
    95,
    "A generic that demands something",
    "T extends, so the function can use what it was promised.",
    "A bare T could be anything, so nothing can be done with it - not "
    "even .length. T extends { length: number } says T is still whatever "
    "you pass, but it must have a length, and now the body can read one. "
    "Both calls here work because a string has a length and so does an "
    "array, and each keeps its own type coming back: the first line "
    "prints a string and the second reads a number off an array. That is "
    "the difference between a constraint and simply typing the parameter "
    "as { length: number }.",
    "ts_constraint",
    [
        (
            "Write "
            + func
            + "<T extends an object with a number length>(a: T, b: T) "
            "returning T, whose body returns whichever has the longer "
            "length. Log it called with "
            + repr(long)
            + " and "
            + repr(short)
            + ", then the length of it called with ["
            + _seq(many)
            + "] and ["
            + _seq(few)
            + "].",
            {
                "func": func,
                "long": long,
                "short": short,
                "many": many,
                "few": few,
            },
        )
        for func, long, short, many, few in _CONSTRAINTS
    ],
)


# ── 96. A type built from every key of another ───────────────

_MAPPED = (
    ("User", "name", "age"),
    ("Book", "title", "pages"),
    ("City", "place", "people"),
    ("Song", "track", "seconds"),
    ("Metal", "element", "number"),
    ("Room", "label", "floor"),
    ("Tool", "kind", "weight"),
    ("Team", "side", "points"),
    ("Trip", "route", "miles"),
    ("Task", "step", "order"),
    ("Item", "code", "qty"),
    ("Note", "heading", "words"),
)

_P96 = _page(
    "ts-mapped",
    96,
    "A type built from every key of another",
    "A mapped type: for each key of T, a property of some other type.",
    "{ [K in keyof T]: boolean } reads as: for every key in T, a "
    "property of that name holding a boolean. That is how Partial, "
    "Readonly and Required from page 89 are written - they are ordinary "
    "mapped types, not compiler magic. Deriving beats declaring for the "
    "same reason as before: add a field to the interface and the mapped "
    "type follows, while a hand-written copy quietly falls behind.",
    "ts_mapped",
    [
        (
            "Write an interface "
            + cls
            + " with "
            + first
            + " as string and "
            + second
            + " as number. Write a generic type Flags that maps every key "
            "of its parameter to a boolean, and apply it to "
            + cls
            + ". Make set of that type with "
            + first
            + " true and "
            + second
            + " false, then log both and the sorted keys joined with "
            "', '.",
            {"cls": cls, "first": first, "second": second},
        )
        for cls, first, second in _MAPPED
    ],
)


# ── 97. A type that chooses, and one that unwraps ────────────

_CONDITIONALS = (
    (5, "text", 2),
    (10, "hello", 5),
    (7, "world", 3),
    (100, "ada", 1),
    (42, "sam", 8),
    (3, "kim", 9),
    (64, "node", 6),
    (12, "code", 4),
    (21, "rust", 7),
    (9, "dart", 11),
    (55, "java", 5),
    (18, "go", 2),
)

_P97 = _page(
    "ts-conditional",
    97,
    "A type that chooses, and one that unwraps",
    "T extends X ? A : B, and infer for the part you want out.",
    "A conditional type is an if for types: if T is an array of "
    "something, give me that something, otherwise give me T back "
    "unchanged. infer names the part being matched so you can return it "
    "- so Unwrap<number[]> is number and Unwrap<string> is string, both "
    "worked out at compile time with nothing running. This is how "
    "Awaited, ReturnType and Parameters are written, and it is where "
    "TypeScript stops being annotations and starts being a language.",
    "ts_conditional",
    [
        (
            "Write a generic type Unwrap that, when its parameter extends "
            "an Array of something inferred, gives that something, and "
            "otherwise gives the parameter. Make Inner from Unwrap of a "
            "number array and Plain from Unwrap of string. Set inner to "
            + str(number)
            + " and plain to "
            + repr(word)
            + ", each with its type. Log both, then inner plus "
            + str(added)
            + ".",
            {"number": number, "word": word, "added": added},
        )
        for number, word, added in _CONDITIONALS
    ],
)


# ── 98. An enum, and the union that usually beats it ─────────

_ENUMS = (
    ("Colour", "Red", "red", "Blue", "blue", "Shade"),
    ("Mode", "Read", "read", "Write", "write", "Access"),
    ("State", "Open", "open", "Shut", "shut", "Position"),
    ("Level", "Low", "low", "High", "high", "Height"),
    ("Sort", "Asc", "asc", "Desc", "desc", "Order"),
    ("Kind", "Text", "text", "Binary", "binary", "Format"),
    ("Turn", "Left", "left", "Right", "right", "Way"),
    ("Size", "Small", "small", "Large", "large", "Scale"),
    ("Face", "Heads", "heads", "Tails", "tails", "Side"),
    ("Step", "Mix", "mix", "Bake", "bake", "Stage"),
    ("Tier", "Free", "free", "Paid", "paid", "Plan"),
    ("Speed", "Slow", "slow", "Fast", "fast", "Rate"),
)

_P98 = _page(
    "ts-enum",
    98,
    "An enum, and the union that usually beats it",
    "A string enum, and the plain union that does nearly the same job.",
    "An enum is one of the few TypeScript features that emits real code "
    "- everything else disappears at compile time. A string enum member "
    "is its string at run time, which the last line proves by comparing "
    "one to a plain string and getting true. Given that, a union of "
    "string literals does almost the same work with nothing emitted, no "
    "import needed, and better narrowing. Use an enum when you want the "
    "names to exist at run time; use a union the rest of the time.",
    "ts_enum",
    [
        (
            "Write a string enum "
            + cls
            + " with "
            + first_name
            + " as "
            + repr(first_value)
            + " and "
            + second_name
            + " as "
            + repr(second_value)
            + ", and a type "
            + alias
            + " that is one of those two strings. Set chosen to the enum's "
            + first_name
            + " and plain to "
            + repr(first_value)
            + " typed as "
            + alias
            + ". Log chosen, the enum's "
            + second_name
            + ", plain, and whether chosen equals plain.",
            {
                "cls": cls,
                "first_name": first_name,
                "first_value": first_value,
                "second_name": second_name,
                "second_value": second_value,
                "alias": alias,
            },
        )
        for (
            cls,
            first_name,
            first_value,
            second_name,
            second_value,
            alias,
        ) in _ENUMS
    ],
)


# ── 99. One function, two signatures ─────────────────────────

_OVERLOADS = (
    ("make", 5, 2, "ada"),
    ("build", 7, 3, "sam"),
    ("form", 4, 10, "kim"),
    ("shape_it", 9, 5, "jo"),
    ("cast", 6, 4, "max"),
    ("mint", 8, 2, "eve"),
    ("press", 3, 7, "abe"),
    ("draw", 11, 2, "ida"),
    ("mould", 12, 3, "ben"),
    ("carve", 2, 9, "rey"),
    ("forge", 10, 5, "finn"),
    ("weave", 1, 8, "nell"),
)

_P99 = _page(
    "ts-overload",
    99,
    "One function, two signatures",
    "Overloads, and the implementation nobody can call directly.",
    "Two signatures above one implementation say: a number in gives a "
    "number out, a string in gives a string out - which a single "
    "signature taking number | string could not promise, since it would "
    "have to say the answer is one or the other. The implementation "
    "signature is not callable from outside; only the overloads are. "
    "Reach for this when the return type genuinely depends on the "
    "argument type, and prefer a generic when it does not.",
    "ts_overload",
    [
        (
            "Write "
            + func
            + " with two overload signatures - number to number and "
            "string to string - and an implementation taking number or "
            "string that returns the value times "
            + str(times)
            + " when typeof says number, and upper-cased otherwise. Log "
            "it called with "
            + str(number)
            + ", then with "
            + repr(word)
            + ".",
            {"func": func, "number": number, "times": times, "word": word},
        )
        for func, number, times, word in _OVERLOADS
    ],
)


# ── 100. Checked against a type without becoming it ──────────

_SATISFIES = (
    ("host", "local", "port", 8080, 1),
    ("name", "ada", "age", 36, 1),
    ("city", "kyoto", "people", 1463, 100),
    ("mode", "safe", "level", 3, 2),
    ("title", "dune", "pages", 412, 8),
    ("region", "eu", "shards", 12, 4),
    ("theme", "dark", "size", 14, 2),
    ("label", "first", "order", 1, 9),
    ("kind", "text", "width", 80, 20),
    ("route", "north", "miles", 120, 30),
    ("team", "reds", "points", 41, 5),
    ("tool", "saw", "weight", 3, 7),
)

_P100 = _page(
    "ts-satisfies",
    100,
    "Checked against a type without becoming it",
    "satisfies, which validates and then gets out of the way.",
    "Annotating settings as Config would check it and then widen every "
    "value to string | number, so calling toUpperCase on the host would "
    "be refused. Leaving the annotation off keeps the narrow types and "
    "checks nothing. satisfies does both: the object is checked against "
    "Config, and the variable keeps the exact types that were inferred - "
    "so the first line calls a string method and the second does "
    "arithmetic, both on the same object. This is the right tool for "
    "nearly every configuration object you will write.",
    "ts_satisfies",
    [
        (
            "Make Config a type alias for a Record of string to string or "
            "number. Set settings, const, to an object with "
            + text_key
            + " of "
            + repr(text_value)
            + " and "
            + number_key
            + " of "
            + str(number_value)
            + ", followed by satisfies Config. Log the "
            + text_key
            + " upper-cased, then the "
            + number_key
            + " plus "
            + str(added)
            + ".",
            {
                "text_key": text_key,
                "text_value": text_value,
                "number_key": number_key,
                "number_value": number_value,
                "added": added,
            },
        )
        for text_key, text_value, number_key, number_value, added in _SATISFIES
    ],
)


TS_PAGES_2: tuple[Page, ...] = (
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
