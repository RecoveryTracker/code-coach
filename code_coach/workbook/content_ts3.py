"""TypeScript pages 101-110: the type system as a tool rather than a tax.

The first twenty TypeScript pages taught you to describe values. These ten
teach you to compute with the descriptions: freeze a literal so its type is
the value, build a string type out of pieces, read a field's type back out
of a shape, and make the compiler refuse a switch that forgot a case.

Page 106 is the one to take away. `never` has no values, so assigning
something to it only compiles when the compiler has already proved nothing
can reach that line. Add a member to the union and every switch that does
not handle it stops compiling - which turns a class of three-in-the-morning
bug into a red squiggle at lunchtime.

Naming, as ever: a top-level type here shares a namespace with the DOM
globals and an interface merges with them rather than shadowing them, so
none of the names below is one of those.
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


def _words(items) -> str:
    return ", ".join(f'"{w}"' for w in items)


# ── 101. A literal frozen into its own type ──────────────────

_AS_CONST = (
    ("colours", "Colour", ("red", "green", "blue"), "green"),
    ("sizes", "Sizing", ("small", "medium", "large"), "large"),
    ("modes", "Mode", ("read", "write"), "read"),
    ("suits", "Suit", ("spades", "hearts", "clubs", "diamonds"), "hearts"),
    ("days", "Day", ("mon", "tue", "wed"), "wed"),
    ("states", "Standing", ("ready", "running", "done"), "running"),
    ("levels", "Level", ("low", "high"), "high"),
    ("turns", "Turn", ("left", "right"), "left"),
    ("faces", "Face", ("heads", "tails"), "tails"),
    ("tiers", "Tier", ("free", "paid"), "paid"),
    ("steps", "Stepping", ("weigh", "mix", "bake"), "mix"),
    ("winds", "Bearing", ("north", "south", "east", "west"), "east"),
    ("metals", "Ore", ("tin", "lead", "zinc"), "lead"),
    ("shades", "Shade", ("teal", "plum", "amber"), "amber"),
    ("nights", "Night", ("thu", "fri", "sat"), "fri"),
    ("paces", "Pace", ("crawl", "walk", "sprint"), "walk"),
    ("gates", "Gate", ("shut", "ajar", "open"), "ajar"),
    ("ranks", "Placing", ("first", "second", "third"), "third"),
    ("forms", "Styling", ("plain", "rich"), "rich"),
    ("tones", "Tone", ("soft", "loud"), "soft"),
)

_P101 = _page(
    "ts-as-const",
    101,
    "A literal frozen into its own type",
    "as const, which makes the type the value rather than its kind.",
    "Without as const, that array is string[] and every entry is just a "
    "string. With it, the array is readonly and each entry's type is the "
    "exact word it holds - so (typeof colours)[number] is "
    '"red" | "green" | "blue" and nothing else will assign to it. Two '
    "characters buy you a union you would otherwise write out by hand and "
    "keep in step by hand.",
    "ts_as_const",
    [
        (
            f"Put the words {_words(members)} in a const called {const} and "
            f"freeze it with as const. Make a type {type_name} from its "
            f'entries, declare a {type_name} holding "{chosen}", then print '
            f"the length, the first entry, and your value.",
            {
                "const_name": const,
                "type_name": type_name,
                "members": members,
                "chosen": chosen,
            },
        )
        for const, type_name, members, chosen in _AS_CONST
    ],
)


# ── 102. A type built out of string pieces ───────────────────

_TEMPLATES = (
    ("Greeting", "hello, ", "world", "greet_it", "ada", "opening"),
    ("Pathed", "/api/", "users", "route_to", "orders", "endpoint"),
    ("Prefixed", "on", "Click", "handler_for", "Change", "event_name"),
    ("Tagged", "v", "1.0", "version_of", "2.0", "release"),
    ("Scoped", "app:", "start", "signal_for", "stop", "topic"),
    ("Keyed", "user_", "id", "field_for", "name", "column"),
    ("Namespaced", "core.", "load", "call_to", "save", "action"),
    ("Flagged", "--", "verbose", "flag_for", "quiet", "option"),
    ("Marked", "id-", "001", "label_for", "002", "marker"),
    ("Titled", "Mr ", "Hopper", "address_to", "Lovelace", "greeting"),
    ("Routed", "https://", "example.com", "url_for", "example.org", "link"),
    ("Framed", "[", "note", "wrap_it", "warning", "boxed"),
    ("Suffixed", "get", "Name", "getter_for", "Age", "accessor"),
    ("Themed", "theme-", "dark", "theme_for", "light", "class_name"),
    ("Sized", "size:", "large", "size_for", "small", "token"),
    ("Dated", "2026-", "09-04", "date_for", "12-25", "stamp"),
    ("Counted", "count-", "one", "count_for", "two", "tally"),
    ("Zoned", "zone/", "north", "zone_for", "south", "area"),
    ("Piped", "in|", "left", "pipe_for", "right", "channel"),
    ("Coded", "err_", "404", "code_for", "500", "status_text"),
)

_P102 = _page(
    "ts-template-type",
    102,
    "A type built out of string pieces",
    "Template literal types: backticks in a type position.",
    "The same backtick syntax you use for strings works in a type, and "
    '`"on${string}"` means any string starting with on. It is how libraries '
    "type things like onClick and onChange without listing every event: the "
    "compiler checks the shape of the string rather than its exact value.",
    "ts_template_type",
    [
        (
            f'Write a type {type_name} for any string starting "{prefix}". '
            f"Declare a {const} of that type holding "
            f'"{prefix}{tail}", write {func} that takes a name and returns '
            f"the prefixed string, then print the const and the result of "
            f'calling it with "{made}".',
            {
                "type_name": type_name,
                "prefix": prefix,
                "tail": tail,
                "func": func,
                "made": made,
                "const_name": const,
            },
        )
        for type_name, prefix, tail, func, made, const in _TEMPLATES
    ],
)


# ── 103. Borrowing a field's type by name ────────────────────

_INDEXED = (
    ("Runner", "name", "score", "finn", 82),
    ("Volume", "title", "pages", "ubik", 224),
    ("Town", "name", "people", "ripon", 17),
    ("Track_", "title", "seconds", "art", 224),
    ("Ore", "name", "melting", "tin", 232),
    ("Berth", "name", "floor", "cabin", 5),
    ("Blade", "name", "weight", "plane", 7),
    ("Side", "name", "points", "blues", 12),
    ("Coord", "label", "distance", "origin", 0),
    ("Extent", "label", "width", "banner", 64),
    ("Duo", "label", "left", "pair", 11),
    ("Reach", "label", "high", "span", 47),
    ("Result", "label", "points", "final", 72),
    ("Journey", "label", "miles", "leg", 180),
    ("Board", "label", "rows", "grid", 6),
    ("Barrel", "label", "litres", "cask", 90),
    ("Token", "face", "worth", "front", 20),
    ("Note", "pitch", "octave", "middle c", 4),
    ("Stage_", "label", "order", "stir", 3),
    ("Crate", "label", "depth", "small", 5),
)

_P103 = _page(
    "ts-indexed-access",
    103,
    "Borrowing a field's type by name",
    'Reading a type out of another type with Thing["field"].',
    "Types are indexable the way values are. If the interface says the "
    "field is a number then Thing[\"count\"] is number, and it stays number "
    "when someone changes the interface. Writing the type out again by hand "
    "is how the two drift apart.",
    "ts_indexed_access",
    [
        (
            f"Write an interface {cls} with a string {text_field} and a "
            f"number {number_field}. Make two types by indexing into it, "
            f'declare a {text_field} of "{text_value}" and a '
            f"{number_field} of {number_value} using them, then print both "
            f"and the typeof the number.",
            {
                "cls": cls,
                "text_field": text_field,
                "number_field": number_field,
                "text_value": text_value,
                "number_value": number_value,
            },
        )
        for cls, text_field, number_field, text_value, number_value in _INDEXED
    ],
)


# ── 104. A table typed by its keys and values ────────────────

_RECORDS = (
    ("scores", "score_for", (("finn", 82), ("kit", 4), ("ida", 37)), "kit"),
    ("counts", "count_for", (("kiwi", 5), ("plum", 21)), "plum"),
    ("melting", "melting_of", (("tin", 232), ("lead", 327)), "tin"),
    ("pages", "pages_of", (("ubik", 224), ("valis", 261)), "valis"),
    ("people", "people_in", (("ripon", 17), ("oslo", 709)), "oslo"),
    ("points", "points_for", (("blues", 12), ("whites", 55)), "whites"),
    ("weights", "weight_of", (("plane", 7), ("chisel", 2)), "plane"),
    ("floors", "floor_of", (("cabin", 5), ("hold", 2)), "hold"),
    ("seconds", "seconds_of", (("art", 224), ("sons", 207)), "sons"),
    ("depths", "depth_of", (("shallow", 2), ("deep", 40)), "deep"),
    ("widths", "width_of", (("narrow", 3), ("wide", 30)), "narrow"),
    ("heights", "height_of", (("low", 5), ("high", 50)), "high"),
    ("ranks", "rank_of", (("first", 1), ("second", 2), ("third", 3)), "third"),
    ("hours", "hours_on", (("thu", 9), ("fri", 5)), "thu"),
    ("sizes", "size_of", (("small", 1), ("large", 9)), "large"),
    ("costs", "cost_of", (("cheap", 4), ("dear", 40)), "cheap"),
    ("speeds", "speed_of", (("crawl", 1), ("sprint", 20)), "sprint"),
    ("tallies", "tally_of", (("in", 6), ("out", 21)), "out"),
    ("spans", "span_of", (("short", 2), ("long", 22)), "short"),
    ("loads", "load_of", (("light", 5), ("heavy", 50)), "heavy"),
)

_P104 = _page(
    "ts-record-type",
    104,
    "A table typed by its keys and values",
    "Record<Key, Value>, and a key type that is a union of the real keys.",
    "Record<K, V> is the type of an object used as a lookup table. Make K a "
    "union of the actual keys rather than string and the compiler knows "
    "which lookups can fail - asking for a key that is not in the union "
    "stops compiling, instead of handing you undefined at run time.",
    "ts_record_type",
    [
        (
            "Write a Key type that is a union of "
            + ", ".join(f'"{k}"' for k, _ in entries)
            + f". Make a Record<Key, number> called {const} holding "
            + ", ".join(f"{k} = {v}" for k, v in entries)
            + f". Write {func} that looks a key up in it, then print the "
            f'result for "{asked}" and how many keys the table has.',
            {
                "const_name": const,
                "func": func,
                "entries": entries,
                "asked": asked,
            },
        )
        for const, func, entries, asked in _RECORDS
    ],
)


# ── 105. A function's shape, written down once ───────────────

_FUNCTION_TYPES = (
    ("Change", "double_it", "value * 2", "add_ten", "value + 10", 7),
    ("Step", "triple_it", "value * 3", "less_two", "value - 2", 9),
    ("Shift", "quad_it", "value * 4", "plus_five", "value + 5", 6),
    ("Scale_", "halve_it", "value * 5", "minus_one", "value - 1", 8),
    ("Adjust", "square_it", "value * value", "add_one", "value + 1", 5),
    ("Alter", "sixx", "value * 6", "less_three", "value - 3", 11),
    ("Amend", "tenx", "value * 10", "plus_two", "value + 2", 4),
    ("Bend", "cube_it", "value * value * value", "add_four", "value + 4", 3),
    ("Warp", "sevenx", "value * 7", "less_five", "value - 5", 12),
    ("Tweak", "eightx", "value * 8", "plus_nine", "value + 9", 2),
    ("Nudge", "ninex", "value * 9", "less_seven", "value - 7", 15),
    ("Turn_", "elevenx", "value * 11", "plus_six", "value + 6", 10),
    ("Twist", "twelvex", "value * 12", "less_four", "value - 4", 14),
    ("Skew", "twentyx", "value * 20", "plus_three", "value + 3", 13),
    ("Flex", "fiftyx", "value * 50", "less_eight", "value - 8", 16),
    ("Morph", "hundredx", "value * 100", "plus_seven", "value + 7", 1),
    ("Sway", "fifteenx", "value * 15", "less_nine", "value - 9", 17),
    ("Veer", "twentyfivex", "value * 25", "plus_eight", "value + 8", 18),
    ("Tilt", "thirtyx", "value * 30", "less_six", "value - 6", 19),
    ("Lean", "fortyx", "value * 40", "plus_eleven", "value + 11", 20),
)

_P105 = _page(
    "ts-function-type",
    105,
    "A function's shape, written down once",
    "A type alias for a function, and the inference it buys you.",
    "Write the signature once as a type and every function you declare with "
    "it gets its parameter types for free - notice the arrows below have no "
    "annotations on value at all. It is also what lets a function take "
    "another function as an argument without spelling the shape out again "
    "at the call site.",
    "ts_function_type",
    [
        (
            f"Write a type {type_name} for a function taking a number and "
            f"returning a number. Declare {first} as {first_expr} and "
            f"{second} as {second_expr} using it, write apply_to that takes "
            f"one of them and a number, then print applying each to "
            f"{number}.",
            {
                "type_name": type_name,
                "first_name": first,
                "first_expr": first_expr,
                "second_name": second,
                "second_expr": second_expr,
                "number": number,
            },
        )
        for type_name, first, first_expr, second, second_expr, number in (
            _FUNCTION_TYPES
        )
    ],
)


# ── 106. A switch that cannot forget a case ──────────────────

_EXHAUSTIVE = (
    ("Signal", "act_on", (("stop", "halt"), ("go", "move"))),
    ("Mode", "run_as", (("read", "reading"), ("write", "writing"))),
    ("Turn_", "steer", (("left", "port"), ("right", "starboard"))),
    ("Face", "call_it", (("heads", "the queen"), ("tails", "the shield"))),
    ("Level", "grade", (("low", "quiet"), ("high", "loud"))),
    ("Gate", "state_of", (("shut", "closed"), ("open", "wide"))),
    ("Tier", "price_of", (("free", "nothing"), ("paid", "something"))),
    ("Pace", "speed_of", (("crawl", "slow"), ("sprint", "fast"))),
    (
        "Standing",
        "report",
        (("ready", "waiting"), ("running", "working"), ("done", "finished")),
    ),
    (
        "Shade",
        "describe",
        (("teal", "blue green"), ("plum", "dark red"), ("amber", "orange")),
    ),
    (
        "Stepping",
        "instruct",
        (("weigh", "on the scales"), ("mix", "in the bowl"),
         ("bake", "in the oven")),
    ),
    (
        "Bearing",
        "point_to",
        (("north", "up"), ("south", "down"), ("east", "right"),
         ("west", "left")),
    ),
    ("Night", "plan_for", (("thu", "quiet"), ("fri", "busy"))),
    ("Ore", "melt_at", (("tin", "low"), ("lead", "higher"))),
    ("Styling", "render_as", (("plain", "text"), ("rich", "marked up"))),
    ("Tone", "play_at", (("soft", "gently"), ("loud", "hard"))),
    (
        "Placing",
        "award",
        (("first", "gold"), ("second", "silver"), ("third", "bronze")),
    ),
    ("Access_", "allow", (("fetch", "reading"), ("store", "writing"))),
    ("Weight_", "carry", (("light", "one hand"), ("heavy", "two hands"))),
    (
        "Season_",
        "expect",
        (("spring", "rain"), ("summer", "sun"), ("autumn", "wind"),
         ("winter", "snow")),
    ),
)

_P106 = _page(
    "ts-never-exhaustive",
    106,
    "A switch that cannot forget a case",
    "never, and the default branch that makes a switch exhaustive.",
    "never is the type with no values, so `const missed: never = value` "
    "only compiles when the compiler has already proved nothing can reach "
    "that line. Handle every member and the default is unreachable and it "
    "compiles. Add a member to the union later and every switch that forgot "
    "it fails to compile, which is the cheapest bug report you will ever "
    "get. This is the most useful single trick in the language.",
    "ts_never_exhaustive",
    [
        (
            f"Write a type {type_name} that is the union of "
            + ", ".join(f'"{m}"' for m, _ in cases)
            + f". Write {func} with a switch returning "
            + ", ".join(f'"{s}"' for _, s in cases)
            + ". Add a default branch assigning the value to a never, then "
            "print the result for every member in turn.",
            {"type_name": type_name, "func": func, "cases": cases},
        )
        for type_name, func, cases in _EXHAUSTIVE
    ],
)


# ── 107. A base that refuses to be built ─────────────────────

_ABSTRACTS = (
    ("Creature", "Cow", "speak", "moo", "it says"),
    ("Figure", "Ring", "outline", "round", "the shape is"),
    ("Hand", "Smith", "work", "forging", "the trade is"),
    ("Vault", "Tape", "keep", "on tape", "stored"),
    ("Engine_", "Diesel", "start_it", "clatter", "it goes"),
    ("Scanner", "Lines", "read_it", "line by line", "reading"),
    ("Poster", "Letter", "send_it", "by post", "sent"),
    ("Player_", "Drum", "play_it", "thud", "the sound is"),
    ("Vessel", "Barge", "float_it", "on the canal", "it floats"),
    ("Spring", "River", "fetch_it", "fresh water", "drawn"),
    ("Printer", "Paper", "write_it", "on paper", "written"),
    ("Grinder", "Mill", "grind_it", "into flour", "ground"),
    ("Lifter", "Crane", "lift_it", "high up", "lifted"),
    ("Cutter", "Saw_", "cut_it", "across the grain", "cut"),
    ("Binder", "Glue", "bind_it", "with glue", "bound"),
    ("Sifter", "Sieve", "sift_it", "through mesh", "sifted"),
    ("Warmer", "Kiln", "heat_it", "in the kiln", "heated"),
    ("Cooler", "Cellar", "chill_it", "in the cellar", "chilled"),
    ("Weigher", "Scales", "weigh_it", "on the scales", "weighed"),
    ("Marker", "Chalk", "mark_it", "in chalk", "marked"),
)

_P107 = _page(
    "ts-abstract-class",
    107,
    "A base that refuses to be built",
    "abstract, for a class that is a promise rather than a thing.",
    "An abstract class cannot be instantiated and an abstract method has no "
    "body - the subclass has to supply one. What you get over an interface "
    "is shared code: describe below is written once in the base and every "
    "subclass has it. Use an interface when you only want the shape, and an "
    "abstract class when you also want to hand something down.",
    "ts_abstract_class",
    [
        (
            f"Write an abstract class {base} with an abstract {method} "
            f"returning a string, and a concrete describe that puts "
            f'"{label}" in front of it. Write {sub} extending it and '
            f'returning "{says}". Build one and print the method, the '
            f"description, and whether it is an instance of {base}.",
            {
                "base": base,
                "sub": sub,
                "method": method,
                "says": says,
                "label": label,
            },
        )
        for base, sub, method, says, label in _ABSTRACTS
    ],
)


# ── 108. A type parameter with a fallback ────────────────────

_DEFAULTS = (
    ("Holder", "morning", 51),
    ("Keeper", "evening", 27),
    ("Sleeve", "words", 44),
    ("Pocket", "notes", 15),
    ("Niche", "finn", 82),
    ("Chest", "ida", 37),
    ("Depot", "kit", 4),
    ("Sack", "teal", 30),
    ("Crate_", "plum", 21),
    ("Basket_", "amber", 33),
    ("Carton", "oak", 12),
    ("Casket", "ash", 31),
    ("Hamper", "tin", 50),
    ("Locker", "lead", 82),
    ("Pouch", "zinc", 30),
    ("Satchel", "kiwi", 5),
    ("Trunk", "sloe", 9),
    ("Vessel_", "ripon", 17),
    ("Wallet", "oslo", 709),
    ("Cradle", "lima", 998),
)

_P108 = _page(
    "ts-generic-default",
    108,
    "A type parameter with a fallback",
    "A default on a generic, so the common case needs no angle brackets.",
    "<T = string> means callers who do not care get string and callers who "
    "do can say otherwise. It is the same idea as a default argument, one "
    "level up, and it is why you can write Array without always writing "
    "Array<something>. Note the first line below has no type argument at "
    "all and still ends up holding a string.",
    "ts_generic_default",
    [
        (
            f"Write a class {cls}<T = string> holding one readonly value "
            f"with a get method. Build one with no type argument holding "
            f'"{text}" and one with <number> holding {number}, then print '
            f"both values and the typeof the first.",
            {"cls": cls, "text": text, "number": number},
        )
        for cls, text, number in _DEFAULTS
    ],
)


# ── 109. A check the compiler narrows on ─────────────────────

_ASSERTS = (
    ("must_be_number", "use_it", "value * 2", 21, "seven", "not a number"),
    ("assert_number", "double_up", "value * 3", 14, "many", "expected a number"),
    ("check_number", "scale_it", "value * 4", 8, "lots", "that is not numeric"),
    ("ensure_number", "raise_it", "value + 10", 32, "none", "a number please"),
    ("insist_number", "lower_it", "value - 5", 40, "some", "numbers only"),
    ("demand_number", "square_it", "value * value", 9, "few", "not numeric"),
    ("need_number", "cube_it", "value * value * value", 4, "several", "wanted a number"),
    ("want_number", "add_one", "value + 1", 99, "plenty", "give me a number"),
    ("verify_number", "halve_it", "value * 5", 12, "loads", "must be numeric"),
    ("confirm_number", "tenx_it", "value * 10", 7, "heaps", "a number is needed"),
    ("test_number", "add_fifty", "value + 50", 25, "scores", "not a number at all"),
    ("prove_number", "less_ten", "value - 10", 60, "dozens", "numbers, please"),
    ("assure_number", "sixx_it", "value * 6", 11, "handfuls", "expected numeric"),
    ("expect_number", "sevenx_it", "value * 7", 6, "piles", "that will not do"),
    ("require_number", "eightx_it", "value * 8", 5, "stacks", "a number was wanted"),
    ("settle_number", "ninex_it", "value * 9", 3, "bundles", "not a number given"),
    ("fix_number", "add_hundred", "value + 100", 45, "clusters", "numeric only"),
    ("hold_number", "less_twenty", "value - 20", 75, "batches", "wanted numeric"),
    ("bind_number", "twelvex_it", "value * 12", 13, "sets", "a number, not text"),
    ("pin_number", "add_five", "value + 5", 18, "groups", "no, a number"),
)

_P109 = _page(
    "ts-assert-fn",
    109,
    "A check the compiler narrows on",
    "asserts value is number: a guard that throws instead of returning.",
    "A type guard returns a boolean you have to test. An assertion function "
    "returns nothing and narrows everything after the call - so the line "
    "after it can do arithmetic on an unknown, because the only way to "
    "reach that line is past the throw. People write this function for "
    "years without the asserts keyword and wonder why the compiler still "
    "complains on the next line.",
    "ts_assert_fn",
    [
        (
            f"Write {func} taking an unknown and declared asserts value is "
            f'number, throwing "{complaint}" when it is not. Write {user} '
            f"that calls it and then returns {expr}. Print the result for "
            f'{number}, then call it with "{bad}" in a try and print the '
            f"caught message.",
            {
                "func": func,
                "user": user,
                "expr": expr,
                "number": number,
                "bad": bad,
                "complaint": complaint,
            },
        )
        for func, user, expr, number, bad, complaint in _ASSERTS
    ],
)


# ── 110. The type inside a promise ───────────────────────────

_AWAITED = (
    ("Doubled", "double_later", "value * 2", (7, 11)),
    ("Tripled", "triple_later", "value * 3", (5, 9)),
    ("Quadded", "quad_later", "value * 4", (6, 8)),
    ("Raised", "raise_later", "value + 10", (3, 40)),
    ("Lowered", "lower_later", "value - 5", (20, 55)),
    ("Squared", "square_later", "value * value", (4, 12)),
    ("Cubed_", "cube_later", "value * value * value", (2, 5)),
    ("Bumped", "bump_later", "value + 1", (99, 41)),
    ("Fived", "five_later", "value * 5", (7, 13)),
    ("Tenned", "ten_later", "value * 10", (6, 14)),
    ("Sixed", "six_later", "value * 6", (8, 15)),
    ("Sevened", "seven_later", "value * 7", (9, 16)),
    ("Eighted", "eight_later", "value * 8", (3, 17)),
    ("Nined", "nine_later", "value * 9", (4, 18)),
    ("Elevened", "eleven_later", "value * 11", (5, 19)),
    ("Twelved", "twelve_later", "value * 12", (6, 20)),
    ("Twentied", "twenty_later", "value * 20", (2, 21)),
    ("Hundreded", "hundred_later", "value * 100", (1, 22)),
    ("Halved", "half_later", "value + 50", (10, 23)),
    ("Shifted", "shift_later", "value - 2", (30, 24)),
)

_P110 = _page(
    "ts-awaited",
    110,
    "The type inside a promise",
    "Awaited and ReturnType, reading a type off a function you already have.",
    "ReturnType<typeof fn> is whatever the function returns, which for an "
    "async function is Promise<something>. Awaited unwraps that, so you get "
    "the type you actually hold after the await. Both are derived rather "
    "than written down, so they follow the function when it changes - "
    "which is the whole argument for computing types instead of repeating "
    "them.",
    "ts_awaited",
    [
        (
            f"Write an async {func} taking a number and returning {expr}. "
            f"Make a type {type_name} using Awaited and ReturnType of it. "
            f"In an async main, await it for {values[0]} and {values[1]} "
            f"into that type, then print both and the typeof the first.",
            {
                "type_name": type_name,
                "func": func,
                "expr": expr,
                "values": values,
            },
        )
        for type_name, func, expr, values in _AWAITED
    ],
)


TS_PAGES_3: tuple[Page, ...] = (
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
