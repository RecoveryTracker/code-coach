"""TypeScript pages 121-130: positions, unions taken apart, and the two
surprises.

Variadic tuples type the first-and-the-rest pattern you have been writing
untyped for years. A `this` return type is what makes a chain still work
after somebody subclasses your class. Extract and Exclude do set arithmetic
on unions and are the half of the utility types nobody reaches for.

Page 129 and page 130 are the surprises. A # field is genuinely private -
not private-by-convention like the private keyword, which is only a compile
time promise - so it does not show up in Object.keys at all. And two
interfaces with the same name do not collide: they merge, which is
occasionally what you want and is always what happens.
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
    return ", ".join(str(n) for n in items)


# ── 121. A tuple of the first one and the rest ───────────────

_VARIADIC = (
    ("head_of", "rest_count", (5, 6, 7)),
    ("first_of", "tail_size", (10, 20, 30, 40)),
    ("lead_of", "others", (82, 37, 4)),
    ("front_of", "behind", (224, 261, 190)),
    ("start_of", "after", (17, 709, 998)),
    ("top_of", "under", (12, 55, 33, 21)),
    ("opener_of", "closers", (7, 2, 4)),
    ("one_of", "many_of", (5, 2, 1)),
    ("earliest", "later_ones", (224, 207, 386)),
    ("nearest", "further", (2, 40, 15)),
    ("leftmost", "rightward", (3, 30, 12, 9)),
    ("lowest_of", "above", (5, 50, 25)),
    ("primary", "secondary", (9, 5, 4)),
    ("chief_of", "minor", (1, 9, 5)),
    ("root_of", "branches", (4, 40, 22)),
    ("stem_of", "leaves", (1, 20, 11, 6)),
    ("origin_of", "steps", (6, 21, 13)),
    ("source_of", "flows", (2, 22, 9)),
    ("base_of", "layers", (5, 50, 28)),
    ("mouth_of", "reaches", (232, 327, 419)),
)

_P121 = _page(
    "ts-variadic-tuple",
    121,
    "A tuple of the first one and the rest",
    "[number, ...number[]]: a tuple that guarantees a first element.",
    "An array type says nothing about how many there are, so values[0] "
    "might be undefined. A tuple with a rest element says there is at least "
    "one and then any number more - so destructuring the head needs no "
    "check, and the compiler knows it. This is the type of every "
    "non-empty list you have ever written a guard for.",
    "ts_variadic_tuple",
    [
        (
            f"Write `type Headed = [number, ...number[]]`. Write {head} "
            f"returning the first entry and {rest} returning how many come "
            f"after it. Make one holding {_seq(items)}, then print the head, "
            f"the count of the rest, and the whole length.",
            {"head_fn": head, "rest_fn": rest, "items": items},
        )
        for head, rest, items in _VARIADIC
    ],
)


# ── 122. A method chain that survives inheritance ────────────

_THIS_RETURN = (
    ("Tally", "Counter_", "add", "scale", 5, 3),
    ("Meter", "Gauge", "raise", "multiply", 4, 2),
    ("Sum_", "Total_", "plus", "times_by", 7, 3),
    ("Store_", "Depot_", "put", "double_by", 6, 4),
    ("Purse_", "Wallet_", "earn", "grow_by", 9, 2),
    ("Pile", "Stack_", "heap", "repeat_by", 3, 5),
    ("Gauge_", "Dial", "step", "widen_by", 8, 2),
    ("Level__", "Grade_", "climb", "boost_by", 2, 6),
    ("Score__", "Result_", "award", "amplify", 10, 3),
    ("Basket__", "Hamper_", "fill", "stack_by", 5, 4),
    ("Load__", "Cargo", "add_on", "heap_by", 11, 2),
    ("Depth__", "Trench", "sink", "deepen_by", 6, 3),
    ("Reach_", "Span_", "extend", "stretch_by", 4, 5),
    ("Charge_", "Cell_", "feed", "surge_by", 7, 2),
    ("Flow", "Stream_", "pour", "swell_by", 3, 7),
    ("Heat__", "Furnace", "warm", "fan_by", 5, 2),
    ("Pace__", "Runner_", "hurry", "sprint_by", 2, 9),
    ("Tone_", "Chord", "lift", "swell", 6, 2),
    ("Weight___", "Ballast", "load", "pack_by", 8, 3),
    ("Height__", "Tower", "raise_by", "stack_up", 4, 4),
)

_P122 = _page(
    "ts-this-return",
    122,
    "A method chain that survives inheritance",
    "A return type of this, rather than the class's own name.",
    "Return the class's own name and the chain breaks the moment somebody "
    "subclasses you: the first call hands back a base and the subclass "
    "method is no longer there. `this` as a return type means whatever the "
    "receiver actually is, so the chain below alternates a base method and "
    "a subclass method and still compiles. It is one word and it is the "
    "difference between a fluent API that can be extended and one that "
    "cannot.",
    "ts_this_return",
    [
        (
            f"Write {base} with a protected total, a {first} that adds and "
            f"returns this, and a value method. Write {sub} extending it "
            f"with a {second} that multiplies and returns this. Chain "
            f"{first}({added}), {second}({times}), {first}({added}) from a "
            f"new {sub} and print the total, then print a fresh one with "
            f"only {first}({added}).",
            {
                "base": base,
                "sub": sub,
                "first": first,
                "second": second,
                "added": added,
                "times": times,
            },
        )
        for base, sub, first, second, added, times in _THIS_RETURN
    ],
)


# ── 123. A getter and setter with types ──────────────────────

_ACCESSORS = (
    ("Tank_", "litres", 60, 90, 5),
    ("Purse__", "pence", 500, 750, 20),
    ("Shelf_", "books", 12, 30, 3),
    ("Meter_", "reading", 100, 250, 40),
    ("Score___", "points", 72, 95, 10),
    ("Depth___", "metres", 40, 55, 8),
    ("Width", "across", 64, 96, 12),
    ("Height___", "up", 30, 45, 6),
    ("Speed_", "knots", 18, 24, 4),
    ("Heat___", "degrees", 21, 35, 7),
    ("Load___", "kilos", 80, 120, 15),
    ("Volume___", "level", 5, 9, 2),
    ("Charge__", "percent", 80, 95, 25),
    ("Stock_", "units", 25, 60, 9),
    ("Fuel_", "gallons", 12, 20, 3),
    ("Angle_", "degrees_of", 90, 180, 45),
    ("Pace___", "steps", 6, 14, 2),
    ("Reach__", "inches", 11, 22, 5),
    ("Span__", "days", 7, 21, 3),
    ("Weight____", "grams", 750, 900, 50),
)

_P123 = _page(
    "ts-accessor",
    123,
    "A getter and setter with types",
    "get and set, which look like a field and run like a method.",
    "The caller writes thing.litres and thing.litres = 90 as though it were "
    "a plain field, and the setter gets to refuse nonsense on the way in - "
    "here a negative becomes zero. The getter's return type and the "
    "setter's parameter type have to agree, which the compiler enforces. "
    "Reach for this when a field needs a rule but you do not want every "
    "caller to say setLitres.",
    "ts_accessor",
    [
        (
            f"Write a class {cls} with a private store starting at {start} "
            f"and a {field} getter and setter, the setter clamping anything "
            f"below zero to zero. Print it, set it to {setting} and print "
            f"it, then set it to -{negative} and print it.",
            {
                "cls": cls,
                "field": field,
                "start": start,
                "setting": setting,
                "negative": negative,
            },
        )
        for cls, field, start, setting, negative in _ACCESSORS
    ],
)


# ── 124. Optional and rest parameters, typed ─────────────────

_RESTS = (
    ("join_up", "total", ": ", " | ", (1, 2, 3)),
    ("list_out", "items", " = ", ", ", (10, 20)),
    ("render_row", "row", " ", " / ", (5, 6, 7)),
    ("show_all", "values", ": ", " - ", (82, 37)),
    ("write_line", "line", " -> ", " + ", (4, 8, 12)),
    ("draw_row", "cells", " | ", " ; ", (3, 6)),
    ("print_set", "set", " = ", " ", (11, 22, 33)),
    ("emit_row", "out", ": ", " * ", (2, 4)),
    ("say_all", "said", " ", " and ", (7, 14, 21)),
    ("give_row", "given", " -> ", " then ", (9, 18)),
    ("mark_row", "marks", ": ", " . ", (5, 10, 15)),
    ("state_row", "state", " = ", " :: ", (6, 12)),
    ("form_row", "form", " ", " > ", (8, 16, 24)),
    ("build_row", "built", ": ", " < ", (13, 26)),
    ("shape_row", "shape", " -> ", " ~ ", (3, 9, 27)),
    ("frame_row", "frame", " | ", " ^ ", (4, 16)),
    ("stack_row", "stack", " = ", " # ", (5, 25, 125)),
    ("bind_row", "bound", " ", " = ", (6, 36)),
    ("weave_row", "woven", ": ", " % ", (7, 49, 343)),
    ("cast_row", "cast", " -> ", " @ ", (2, 8)),
)

_P124 = _page(
    "ts-rest-params",
    124,
    "Optional and rest parameters, typed",
    "sep?: string and ...values: number[], and the order they must go in.",
    "An optional parameter is that type or undefined, so you have to deal "
    "with the undefined before using it - ?? does that in one move. A rest "
    "parameter collects everything left into an array and must come last, "
    "because nothing could follow it. Note the third call below: passing "
    "undefined explicitly is the same as leaving it out.",
    "ts_rest_params",
    [
        (
            f'Write {func}(label: string, sep?: string, ...values: number[]) '
            f'returning the label and values joined by the separator, '
            f'defaulting to "{default_sep}". Print calling it with just '
            f'"{label}", then with "{sep}" and {_seq(items)}, then with '
            f"undefined and the same numbers.",
            {
                "func": func,
                "label": label,
                "default_sep": default_sep,
                "sep": sep,
                "items": items,
            },
        )
        for func, label, default_sep, sep, items in _RESTS
    ],
)


# ── 125. Two type parameters at once ─────────────────────────

_TWO_GENERICS = (
    ("finn", 82),
    ("ida", 37),
    ("kit", 4),
    ("ubik", 224),
    ("valis", 261),
    ("ripon", 17),
    ("oslo", 709),
    ("tin", 232),
    ("lead", 327),
    ("cabin", 5),
    ("plane", 7),
    ("blues", 12),
    ("teal", 30),
    ("plum", 21),
    ("amber", 33),
    ("oak", 12),
    ("ash", 31),
    ("kiwi", 5),
    ("sloe", 9),
    ("art", 224),
)

_P125 = _page(
    "ts-two-generics",
    125,
    "Two type parameters at once",
    "<A, B> and a tuple return, so both types survive the call.",
    "Both parameters are inferred from the arguments - nothing is written "
    "at the call site - and the tuple return keeps them apart on the way "
    "out. Return an array instead of a tuple and you get (A | B)[], which "
    "loses exactly the information you went to the trouble of capturing. "
    "The last two lines prove the types made it through.",
    "ts_two_generics",
    [
        (
            "Write pair_up<A, B>(first: A, second: B): [A, B]. Call it with "
            f'"{word}" and {number}, then print both entries and the typeof '
            "each.",
            {"word": word, "number": number},
        )
        for word, number in _TWO_GENERICS
    ],
)


# ── 126. Set arithmetic on a union ───────────────────────────

_EXTRACTS = (
    ("Signal_", ("stop", "go", "wait"), ("stop", "go"), "wait"),
    ("Mode_", ("read", "write", "append"), ("read",), "write"),
    ("Shade_", ("teal", "plum", "amber"), ("teal", "plum"), "amber"),
    ("Night_", ("thu", "fri", "sat"), ("fri", "sat"), "thu"),
    ("Ore_", ("tin", "lead", "zinc"), ("tin",), "lead"),
    ("Bearing__", ("north", "south", "east", "west"), ("north", "south"), "east"),
    ("Placing_", ("first", "second", "third"), ("first",), "third"),
    ("Pace____", ("crawl", "walk", "sprint"), ("walk", "sprint"), "crawl"),
    ("Gate__", ("shut", "ajar", "open"), ("open",), "shut"),
    ("Tier_", ("free", "paid", "trial"), ("paid", "trial"), "free"),
    ("Tone__", ("soft", "loud", "silent"), ("soft",), "loud"),
    ("Stage__", ("weigh", "mix", "bake"), ("mix", "bake"), "weigh"),
    ("Standing_", ("ready", "running", "done"), ("done",), "ready"),
    ("Level___", ("low", "mid", "high"), ("low", "mid"), "high"),
    ("Styling_", ("plain", "rich", "raw"), ("rich",), "plain"),
    ("Access__", ("fetch", "store", "purge"), ("fetch", "store"), "purge"),
    ("Weight_____", ("light", "middling", "heavy"), ("heavy",), "light"),
    ("Turn__", ("left", "right", "about"), ("left", "right"), "about"),
    ("Form__", ("short", "long", "medium"), ("short",), "long"),
    ("Season__", ("spring", "summer", "autumn", "winter"), ("spring", "summer"), "winter"),
)

_P126 = _page(
    "ts-extract-exclude",
    126,
    "Set arithmetic on a union",
    "Extract keeps the members that match; Exclude drops them.",
    "These two are the half of the utility types nobody reaches for, and "
    "they are the ones that keep two unions in step. Derive the smaller "
    "union from the bigger one and adding a member in one place updates "
    "both - write them out separately and they drift, which is the same "
    "argument as everywhere else in this tier.",
    "ts_extract_exclude",
    [
        (
            f"Write a type {type_name} that is the union of "
            + ", ".join(f'"{m}"' for m in members)
            + ". Make Kept with Extract for "
            + ", ".join(f'"{k}"' for k in kept)
            + f", and Dropped with Exclude for the same. Declare one of "
            f'each holding "{kept[0]}" and "{dropped}", then print both.',
            {
                "type_name": type_name,
                "members": members,
                "kept": kept,
                "dropped_shown": dropped,
            },
        )
        for type_name, members, kept, dropped in _EXTRACTS
    ],
)


# ── 127. A union with the nothings taken out ─────────────────

_NON_NULL = (
    ("Reply", "yes", "no", "answer_of"),
    ("Choice", "left", "right", "side_of"),
    ("Verdict", "pass", "fail", "outcome_of"),
    ("Weather", "rain", "sun", "sky_of"),
    ("Doorway", "open", "shut", "state_of"),
    ("Signal__", "go", "stop", "light_of"),
    ("Volume____", "soft", "loud", "level_of"),
    ("Tide", "high", "low", "water_of"),
    ("Coin_", "heads", "tails", "face_of"),
    ("Watch", "day", "night", "shift_of"),
    ("Way__", "north", "south", "heading_of"),
    ("Speed__", "fast", "slow", "rate_of"),
    ("Sizing_", "big", "small", "scale_of"),
    ("Cost_", "dear", "cheap", "price_of"),
    ("Order___", "first", "last", "place_of"),
    ("Ground", "wet", "dry", "state_on"),
    ("Air", "warm", "cold", "feel_of"),
    ("Light", "bright", "dim", "glow_of"),
    ("Sound_", "near", "far", "range_of"),
    ("Path_", "up", "down", "slope_of"),
)

_P127 = _page(
    "ts-non-nullable",
    127,
    "A union with the nothings taken out",
    "NonNullable<T>, and the ?? that produces one.",
    "NonNullable<T> is Exclude<T, null | undefined> with a shorter name. "
    "Take the union with the nulls in at the boundary where the value "
    "arrives, hand back the NonNullable version, and everything downstream "
    "stops checking. Doing it the other way round - checking at every use - "
    "is how a codebase ends up with the same guard forty times.",
    "ts_non_nullable",
    [
        (
            f'Write a type {type_name} that is "{first}" | "{second}" | '
            f"null | undefined, and Solid as its NonNullable. Write {func} "
            f'returning the value or "{first}" when it is missing. Print it '
            f'for "{second}", for null, and for undefined.',
            {
                "type_name": type_name,
                "first": first,
                "second": second,
                "func": func,
            },
        )
        for type_name, first, second, func in _NON_NULL
    ],
)


# ── 128. Walking an object without losing its types ──────────

_ENTRIES = (
    (("finn", 82), ("kit", 4), ("ida", 37)),
    (("kiwi", 5), ("plum", 21)),
    (("tin", 232), ("lead", 327)),
    (("ubik", 224), ("valis", 261)),
    (("ripon", 17), ("oslo", 709)),
    (("blues", 12), ("whites", 55)),
    (("plane", 7), ("chisel", 2)),
    (("cabin", 5), ("hold", 2)),
    (("art", 224), ("sons", 207)),
    (("shallow", 2), ("deep", 40)),
    (("narrow", 3), ("wide", 30)),
    (("low", 5), ("high", 50)),
    (("thu", 9), ("fri", 5)),
    (("small", 1), ("large", 9)),
    (("cheap", 4), ("dear", 40)),
    (("crawl", 1), ("sprint", 20)),
    (("into", 6), ("outof", 21)),
    (("short", 2), ("long", 22)),
    (("light", 5), ("heavy", 50)),
    (("oak", 12), ("ash", 31)),
)

_P128 = _page(
    "ts-typed-entries",
    128,
    "Walking an object without losing its types",
    "keyof typeof, and the cast Object.keys needs.",
    "Object.keys returns string[], not the keys of your object - it has to, "
    "because an object can have more properties than its type admits. So "
    "indexing with the result does not compile until you assert it back to "
    "Key[]. That assertion is a claim you are making, and it is sound here "
    "because the object is a literal declared as const two lines above.",
    "ts_typed_entries",
    [
        (
            "Make a const object as const holding "
            + ", ".join(f"{k} = {v}" for k, v in entries)
            + ". Take its keys as `keyof typeof` and add the values up, "
            "then print the keys joined, the total, and the first value.",
            {"entries": entries},
        )
        for entries in _ENTRIES
    ],
)


# ── 129. A field nobody outside can reach ────────────────────

_PRIVATE = (
    ("Tally_", "count", "bump", 0, 5),
    ("Purse___", "pence", "spend_on", 500, 75),
    ("Meter__", "reading", "advance", 100, 25),
    ("Score____", "points", "award_to", 72, 9),
    ("Shelf__", "books", "shelve", 12, 4),
    ("Tank__", "litres", "top_up", 60, 30),
    ("Depth____", "metres", "descend_by", 40, 15),
    ("Load____", "kilos", "pile_on", 80, 20),
    ("Charge___", "percent", "feed_in", 80, 15),
    ("Stock__", "units", "receive_in", 25, 35),
    ("Fuel__", "gallons", "fill_by", 12, 8),
    ("Angle__", "degrees", "turn_by", 90, 45),
    ("Pace_____", "steps", "quicken_by", 6, 8),
    ("Reach___", "inches", "extend_by", 11, 11),
    ("Span___", "days", "lengthen_by", 7, 14),
    ("Heat____", "degrees_c", "warm_by", 21, 14),
    ("Speed___", "knots", "hasten_by", 18, 6),
    ("Height____", "metres_up", "raise_by", 30, 15),
    ("Width_", "across_by", "widen_by", 64, 32),
    ("Volume_____", "level_at", "turn_up", 5, 4),
)

_P129 = _page(
    "ts-private-field",
    129,
    "A field nobody outside can reach",
    "A # field, which is private at run time and not only at compile time.",
    "The private keyword is a promise to the compiler and nothing more - "
    "the field is a perfectly ordinary property once it is JavaScript, and "
    "anyone can reach it. A # field is enforced by the language itself: it "
    "is not a property, so the last line below finds no keys at all. Use # "
    "when the privacy has to be real and private when you only want the "
    "discipline.",
    "ts_private_field",
    [
        (
            f"Write a class {cls} with a #{field} set from the constructor "
            f"and a {method} that adds to it and returns it, plus a peek. "
            f"Build one starting at {start}, print {method}({added}), print "
            f"peek, then print how many keys Object.keys finds on it.",
            {
                "cls": cls,
                "field": field,
                "method": method,
                "start": start,
                "added": added,
            },
        )
        for cls, field, method, start, added in _PRIVATE
    ],
)


# ── 130. Two interfaces of the same name ─────────────────────

_MERGES = (
    ("Runner__", "name", "score", "finn", 82),
    ("Volume______", "title", "pages", "ubik", 224),
    ("Town_", "name", "people", "ripon", 17),
    ("Track__", "title", "seconds", "art", 224),
    ("Ore__", "name", "melting", "tin", 232),
    ("Berth_", "name", "floor", "cabin", 5),
    ("Blade_", "name", "weight", "plane", 7),
    ("Side_", "name", "points", "blues", 12),
    ("Coord_", "label", "distance", "origin", 0),
    ("Extent_", "label", "width", "banner", 64),
    ("Duo_", "label", "left", "pair", 11),
    ("Reach____", "label", "high", "span", 47),
    ("Result__", "label", "points", "final", 72),
    ("Journey_", "label", "miles", "leg", 180),
    ("Board_", "label", "rows", "grid", 6),
    ("Barrel_", "label", "litres", "cask", 90),
    ("Token__", "face", "worth", "front", 20),
    ("Note_", "pitch", "octave", "middle c", 4),
    ("Stage___", "label", "order", "stir", 3),
    ("Crate__", "label", "depth", "small", 5),
)

_P130 = _page(
    "ts-declaration-merge",
    130,
    "Two interfaces of the same name",
    "Declaration merging: interfaces with one name become one interface.",
    "Declare an interface twice and TypeScript does not complain - it adds "
    "the members together, and an object now needs all of them. This is "
    "how you add a property to a library's type from your own code, and it "
    "is also why an interface named after a DOM global merges with it "
    "instead of shadowing it, which is the trap behind half the naming "
    "rules in this book. A type alias refuses the same thing outright.",
    "ts_declaration_merge",
    [
        (
            f"Declare an interface {cls} twice, once with a string {first} "
            f"and once with a number {second}. Make one object satisfying "
            f'both, holding "{first_value}" and {second_value}, then print '
            f"both fields and how many keys it has.",
            {
                "cls": cls,
                "first": first,
                "second": second,
                "first_value": first_value,
                "second_value": second_value,
            },
        )
        for cls, first, second, first_value, second_value in _MERGES
    ],
)


TS_PAGES_5: tuple[Page, ...] = (
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
