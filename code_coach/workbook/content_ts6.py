"""TypeScript pages 131-140: reading types off what exists, and the escape
hatches.

Half of these derive a type from something already written down -
Parameters and ReturnType from a function, typeof from a class, Omit from an
interface - so the derived thing follows when the original changes. The
other half are the narrowing and the escape routes: instanceof, optional
chaining, and the double assertion that turns the compiler off entirely.

Page 135 is the keeper. Result<T> is a generic discriminated union with an
ok flag, and the compiler will not let you touch value until you have
checked it. Errors as values rather than exceptions, enforced.

Page 134 is the warning. `as unknown as` will make any type into any other
type, and the exercises prove what you get: a number wearing an interface's
name, whose field is undefined at run time. It is on a page so it can be
labelled, not so it can be used.
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


# ── 131. A function's argument types, read back out ──────────

_PARAMETERS = (
    ("repeat_it", "ab", 3),
    ("echo_it", "no", 4),
    ("say_again", "la", 5),
    ("double_up", "xy", 2),
    ("chant", "ho", 3),
    ("stutter", "b", 6),
    ("drum_it", "ta", 4),
    ("ring_out", "ding", 2),
    ("call_twice", "hi", 2),
    ("beat_out", "tick", 3),
    ("knock_it", "rap", 3),
    ("hum_it", "mm", 5),
    ("tap_it", "tap", 2),
    ("chime", "bong", 2),
    ("peal", "dong", 3),
    ("thrum", "zz", 4),
    ("patter", "pit", 3),
    ("clang", "clan", 2),
    ("whirr", "rr", 6),
    ("buzz_it", "bz", 5),
)

_P131 = _page(
    "ts-parameters",
    131,
    "A function's argument types, read back out",
    "Parameters<typeof fn> and ReturnType<typeof fn>.",
    "Parameters gives you the argument list as a tuple, which you can then "
    "spread back into the call - so a wrapper never repeats the signature "
    "and never drifts from it. Together with ReturnType it means you can "
    "describe a function entirely in terms of a function that already "
    "exists, which is the whole argument for deriving types rather than "
    "writing them twice.",
    "ts_parameters",
    [
        (
            f"Write {func}(word: string, count: number) returning the word "
            f"repeated. Make Args from its Parameters and Made from its "
            f'ReturnType, hold ["{word}", {count}] as Args, spread it into '
            f"the call, then print the result, the count, and the result's "
            f"length.",
            {"func": func, "word": word, "count": count},
        )
        for func, word, count in _PARAMETERS
    ],
)


# ── 132. Telling two classes apart ───────────────────────────

_INSTANCES = (
    ("Named", "Numbered", "label", "count", "tell_of", "finn", 82),
    ("Worded", "Counted_", "text", "total", "read_of", "morning", 51),
    ("Titled_", "Paged", "title", "pages", "show_of", "ubik", 224),
    ("Placed", "Peopled", "place", "people", "state_of", "ripon", 17),
    ("Metalled", "Melted", "metal", "degrees", "give_of", "tin", 232),
    ("Berthed", "Floored", "berth", "floor", "say_of", "cabin", 5),
    ("Bladed", "Weighed_", "blade", "grams", "name_of", "plane", 7),
    ("Sided", "Pointed", "side", "points", "call_of", "blues", 12),
    ("Marked_", "Measured", "mark", "span", "mark_of", "origin", 40),
    ("Banner", "Widened", "banner", "width", "sign_of", "wide", 64),
    ("Paired", "Lefted", "pair", "left", "pair_of", "duo", 11),
    ("Spanned", "Highed", "span", "high", "reach_of", "arch", 47),
    ("Finaled", "Scored_", "final", "points", "end_of", "result", 72),
    ("Legged", "Miled", "leg", "miles", "trip_of", "coast", 180),
    ("Gridded", "Rowed", "grid", "rows", "board_of", "chess", 6),
    ("Casked", "Litred", "cask", "litres", "hold_of", "oak", 90),
    ("Faced", "Worthed", "face", "worth", "coin_of", "front", 20),
    ("Pitched", "Octaved", "pitch", "octave", "note_of", "middle", 4),
    ("Stirred", "Ordered_", "stir", "order", "step_of", "mix", 3),
    ("Smalled", "Depthed", "small", "depth", "crate_of", "box", 5),
)

_P132 = _page(
    "ts-instanceof",
    132,
    "Telling two classes apart",
    "instanceof, which narrows a union of classes.",
    "typeof narrows primitives; instanceof narrows classes. Inside the if "
    "the compiler knows exactly which one you have, so its own fields are "
    "reachable without a cast. This works because a class is a value as "
    "well as a type - which is also why you cannot instanceof an "
    "interface, since an interface has no run time existence at all.",
    "ts_instanceof",
    [
        (
            f"Write a class {first} holding a string {first_field} and a "
            f"class {second} holding a number {second_field}. Write {func} "
            f"taking either, returning the string from one and the number "
            f'as a string from the other. Print it for "{first_value}" and '
            f"for {second_value}.",
            {
                "first": first,
                "second": second,
                "first_field": first_field,
                "second_field": second_field,
                "func": func,
                "first_value": first_value,
                "second_value": second_value,
            },
        )
        for (
            first,
            second,
            first_field,
            second_field,
            func,
            first_value,
            second_value,
        ) in _INSTANCES
    ],
)


# ── 133. A whole expression that gives up early ──────────────

_CHAINS = (
    ("Profile_", "detail", "name", "finn", 82, "nobody"),
    ("Entry__", "body", "text", "morning", 51, "empty"),
    ("Volume_1", "cover", "title", "ubik", 224, "untitled"),
    ("Town__", "records", "name", "ripon", 17, "unknown"),
    ("Ore___", "assay", "metal", "tin", 232, "unassayed"),
    ("Berth__", "plan", "berth", "cabin", 5, "unplanned"),
    ("Blade__", "spec", "blade", "plane", 7, "unspecified"),
    ("Side__", "sheet", "side", "blues", 12, "unlisted"),
    ("Coord__", "origin", "label", "start", 40, "unplaced"),
    ("Extent__", "frame", "label", "banner", 64, "unframed"),
    ("Duo__", "pairing", "label", "pair", 11, "unpaired"),
    ("Reach_1", "arc", "label", "span", 47, "unreached"),
    ("Result_1", "sheet", "label", "final", 72, "unscored"),
    ("Journey__", "route", "label", "leg", 180, "unrouted"),
    ("Board__", "layout", "label", "grid", 6, "unlaid"),
    ("Barrel__", "gauge", "label", "cask", 90, "ungauged"),
    ("Token_1", "stamp", "face", "front", 20, "unstamped"),
    ("Note__", "score", "pitch", "middle", 4, "unwritten"),
    ("Stage_1", "cue", "label", "stir", 3, "uncued"),
    ("Crate_1", "docket", "label", "small", 5, "undocketed"),
)

_P133 = _page(
    "ts-optional-chain",
    133,
    "A whole expression that gives up early",
    "?. on a property, a call and a chain, and how far it short-circuits.",
    "?. does not just guard the one step it is written on - if the left "
    "side is null or undefined the entire rest of the chain is abandoned "
    "and the answer is undefined. ?.() does the same for a call that might "
    "not be there. Pairing it with ?? gives you the fallback in the same "
    "expression, which is the whole pattern in one line.",
    "ts_optional_chain",
    [
        (
            f"Write an interface {cls} with an optional {field} holding a "
            f"required {inner} string and an optional count function. Make "
            f'one with "{value}" and a count returning {number}, and an '
            f"empty one. Print the inner or "
            f'"{missing}" for each, then the count or 0 for each.',
            {
                "cls": cls,
                "field": field,
                "inner": inner,
                "value": value,
                "number": number,
                "missing": missing,
            },
        )
        for cls, field, inner, value, number, missing in _CHAINS
    ],
)


# ── 134. The escape hatch, and why it is one ─────────────────

_DOUBLES = (
    ("Counted__", "count", 82),
    ("Paged_", "pages", 224),
    ("Peopled_", "people", 17),
    ("Melted_", "degrees", 232),
    ("Floored_", "floor", 5),
    ("Weighed__", "grams", 7),
    ("Pointed_", "points", 12),
    ("Measured_", "span", 40),
    ("Widened_", "width", 64),
    ("Lefted_", "left", 11),
    ("Highed_", "high", 47),
    ("Scored__", "score", 72),
    ("Miled_", "miles", 180),
    ("Rowed_", "rows", 6),
    ("Litred_", "litres", 90),
    ("Worthed_", "worth", 20),
    ("Octaved_", "octave", 4),
    ("Ordered__", "order", 3),
    ("Depthed_", "depth", 5),
    ("Timed", "seconds", 224),
)

_P134 = _page(
    "ts-double-assert",
    134,
    "The escape hatch, and why it is one",
    "as unknown as, which will convert anything into anything.",
    "A single `as` only allows casts the compiler thinks plausible. Going "
    "via unknown removes even that check, so any type becomes any other "
    "type and nothing is verified. The exercises show what you actually "
    "get: a number wearing the interface's name, whose typeof is still "
    "number and whose field is undefined. Reach for it at a boundary you "
    "have checked yourself, and nowhere else.",
    "ts_double_assert",
    [
        (
            f"Write an interface {cls} with a number {field}. Make an "
            f"unknown holding a real one and cast it with a single as. Then "
            f"force the plain number {number} into {cls} with as unknown "
            f"as. Print the real field, the typeof the forced one, and "
            f"whether its field is undefined.",
            {"cls": cls, "field": field, "number": number},
        )
        for cls, field, number in _DOUBLES
    ],
)


# ── 135. Errors as values ────────────────────────────────────

_RESULTS = (
    ("halve_it", "read_it", 10, "value * 2", 20, 4, "too small"),
    ("scale_it", "show_it", 5, "value * 3", 12, 2, "below five"),
    ("raise_it", "tell_it", 20, "value + 10", 30, 9, "under twenty"),
    ("grow_it", "state_it", 1, "value * 4", 6, 0, "not positive"),
    ("boost_it", "give_it", 50, "value + 5", 60, 11, "under fifty"),
    ("lift_it", "say_it", 100, "value * 2", 250, 40, "below a hundred"),
    ("push_it", "print_it", 8, "value * 5", 16, 3, "too few"),
    ("bump_it", "read_out", 15, "value + 20", 40, 7, "under fifteen"),
    ("hoist_it", "show_out", 3, "value * 6", 9, 1, "less than three"),
    ("heave_it", "tell_out", 25, "value + 25", 75, 12, "under twenty five"),
    ("rear_it", "state_out", 12, "value * 7", 24, 5, "below twelve"),
    ("hike_it", "give_out", 40, "value + 40", 80, 18, "under forty"),
    ("swell_it", "say_out", 6, "value * 8", 18, 2, "fewer than six"),
    ("build_it", "print_out", 30, "value + 30", 90, 14, "below thirty"),
    ("mount_it", "read_off", 9, "value * 9", 27, 4, "under nine"),
    ("stack_it", "show_off", 60, "value + 60", 120, 22, "below sixty"),
    ("pile_it", "tell_off", 7, "value * 10", 21, 3, "fewer than seven"),
    ("rack_it", "state_off", 45, "value + 45", 135, 19, "under forty five"),
    ("load_it", "give_off", 4, "value * 11", 12, 1, "under four"),
    ("heap_it", "say_off", 70, "value + 70", 140, 33, "below seventy"),
)

_P135 = _page(
    "ts-result-type",
    135,
    "Errors as values, checked before they are read",
    "A generic discriminated union: { ok: true, value } | { ok: false, why }.",
    "This is the shape that makes failure part of the type instead of "
    "something that happens to you. The ok flag is the discriminant, so "
    "inside `if (made.ok)` the compiler knows value exists and outside it "
    "knows why does - and reading value without checking simply does not "
    "compile. Rust calls it Result and builds the language around it; here "
    "it is four words of type and costs nothing.",
    "ts_result_type",
    [
        (
            "Write `type Result<T> = { ok: true; value: T } | "
            f"{{ ok: false; why: string }}`. Write {func} returning a "
            f'failure with "{why}" below {limit} and otherwise {expr}. '
            f"Write {reader} that returns the value as a string or the "
            f"reason. Print it for {good} and for {bad}.",
            {
                "func": func,
                "reader": reader,
                "limit": limit,
                "expr": expr,
                "good": good,
                "bad": bad,
                "why": why,
            },
        )
        for func, reader, limit, expr, good, bad, why in _RESULTS
    ],
)


# ── 136. Changing one field's type ───────────────────────────

_OMITS = (
    ("Runner___", "name", "score", "finn", "eighty two"),
    ("Volume_2", "title", "pages", "ubik", "two hundred"),
    ("Town___", "name", "people", "ripon", "seventeen"),
    ("Track___", "title", "seconds", "art", "three forty"),
    ("Ore_1", "name", "melting", "tin", "two thirty two"),
    ("Berth___", "name", "floor", "cabin", "five"),
    ("Blade___", "name", "weight", "plane", "seven"),
    ("Side___", "name", "points", "blues", "twelve"),
    ("Coord___", "label", "distance", "origin", "forty"),
    ("Extent___", "label", "width", "banner", "sixty four"),
    ("Duo___", "label", "left", "pair", "eleven"),
    ("Reach_2", "label", "high", "span", "forty seven"),
    ("Result_2", "label", "points", "final", "seventy two"),
    ("Journey___", "label", "miles", "leg", "one eighty"),
    ("Board___", "label", "rows", "grid", "six"),
    ("Barrel___", "label", "litres", "cask", "ninety"),
    ("Token_2", "face", "worth", "front", "twenty"),
    ("Note___", "pitch", "octave", "middle", "four"),
    ("Stage_2", "label", "order", "stir", "three"),
    ("Crate_2", "label", "depth", "small", "five"),
)

_P136 = _page(
    "ts-omit-override",
    136,
    "Changing one field's type",
    "Omit the field, then intersect a new version back in.",
    "There is no built-in for changing a field's type, and this two-step is "
    "the idiom: drop it with Omit, add it back with an intersection. It "
    "comes up constantly at boundaries - a date that arrives as a string, "
    "an id that is a number in the database and a string in the URL - and "
    "the point is that every other field still follows the original type.",
    "ts_omit_override",
    [
        (
            f"Write an interface {cls} with a string {kept} and a number "
            f"{changed}. Make a Restated type that omits {changed} and "
            f'intersects a string {changed} back in. Hold "{kept_value}" '
            f'and "{changed_value}" in one, then print both fields and the '
            f"typeof the changed one.",
            {
                "cls": cls,
                "kept": kept,
                "changed": changed,
                "kept_value": kept_value,
                "changed_value": changed_value,
            },
        )
        for cls, kept, changed, kept_value, changed_value in _OMITS
    ],
)


# ── 137. An index signature with a shaped key ────────────────

_TEMPLATE_KEYS = (
    ("score_", (("finn", 82), ("kit", 4))),
    ("count_", (("kiwi", 5), ("plum", 21))),
    ("melt_", (("tin", 232), ("lead", 327))),
    ("pages_", (("ubik", 224), ("valis", 261))),
    ("people_", (("ripon", 17), ("oslo", 709))),
    ("points_", (("blues", 12), ("whites", 55))),
    ("weight_", (("plane", 7), ("chisel", 2))),
    ("floor_", (("cabin", 5), ("hold", 2))),
    ("secs_", (("art", 224), ("sons", 207))),
    ("depth_", (("shallow", 2), ("deep", 40))),
    ("width_", (("narrow", 3), ("wide", 30))),
    ("height_", (("low", 5), ("high", 50))),
    ("hours_", (("thu", 9), ("fri", 5))),
    ("size_", (("small", 1), ("large", 9))),
    ("cost_", (("cheap", 4), ("dear", 40))),
    ("speed_", (("crawl", 1), ("sprint", 20))),
    ("tally_", (("into", 6), ("outof", 21))),
    ("span_", (("short", 2), ("long", 22))),
    ("load_", (("light", 5), ("heavy", 50))),
    ("age_", (("oak", 12), ("ash", 31))),
)

_P137 = _page(
    "ts-template-keys",
    137,
    "An index signature with a shaped key",
    "A mapped type over a template literal, so keys must fit a pattern.",
    "An ordinary index signature accepts any string key at all. Map over a "
    "template literal type instead and only keys of that shape are allowed "
    "- so a table of score_finn and score_kit will not quietly accept a "
    "misspelt total_kit. The optional marker is what lets you supply only "
    "some of the infinitely many keys that match.",
    "ts_template_keys",
    [
        (
            f"Write a Keyed type whose optional keys are any string "
            f'starting "{prefix}", holding numbers. Fill one with '
            + ", ".join(f"{prefix}{n} = {v}" for n, v in entries)
            + ", then print the first value, how many keys there are, and "
            "the keys joined.",
            {"prefix": prefix, "entries": entries},
        )
        for prefix, entries in _TEMPLATE_KEYS
    ],
)


# ── 138. A generic class matching a generic interface ────────

_GENERIC_IMPLS = (
    ("Holds_", "Box_", "get_it", "finn", 82),
    ("Keeps", "Case__", "take", "morning", 51),
    ("Carries", "Crate_3", "fetch", "ubik", 224),
    ("Stores", "Depot__", "draw", "ripon", 17),
    ("Bears", "Sack_", "pull", "tin", 232),
    ("Guards", "Vault_", "yield_it", "cabin", 5),
    ("Cradles", "Cradle_", "lift", "plane", 7),
    ("Grips", "Clamp", "release", "blues", 12),
    ("Wraps", "Sleeve_", "unwrap_it", "origin", 40),
    ("Shelters", "Shed", "let_out", "banner", 64),
    ("Contains", "Jar_", "pour_out", "pair", 11),
    ("Encloses", "Pen", "open_up", "span", 47),
    ("Houses", "Barn_", "bring_out", "final", 72),
    ("Shields", "Shell", "crack", "leg", 180),
    ("Covers", "Lid", "lift_off", "grid", 6),
    ("Binds_", "Band", "loosen", "cask", 90),
    ("Packs", "Parcel_", "unpack", "front", 20),
    ("Nests", "Nest_", "hatch", "middle", 4),
    ("Pockets", "Pouch_", "empty_it", "stir", 3),
    ("Sleeves", "Tube", "slide_out", "small", 5),
)

_P138 = _page(
    "ts-generic-impl",
    138,
    "A generic class matching a generic interface",
    "interface Thing<T>, and a class that implements it for any T.",
    "The type parameter runs all the way through: the interface is generic, "
    "the class is generic, and implements passes its own T along. Notice "
    "that neither construction below says what T is - it is inferred from "
    "the constructor argument, and the interface annotation on the const is "
    "what pins it. This is how every container type in every library is "
    "put together.",
    "ts_generic_impl",
    [
        (
            f"Write an interface {iface}<T> with a {method} returning T, and "
            f"a class {cls}<T> implementing it around one held value. Build "
            f'one holding "{word}" typed as {iface}<string> and one holding '
            f"{number} typed as {iface}<number>, then print both and the "
            f"typeof the number one.",
            {
                "iface": iface,
                "cls": cls,
                "method": method,
                "word": word,
                "number": number,
            },
        )
        for iface, cls, method, word, number in _GENERIC_IMPLS
    ],
)


# ── 139. The type of the class itself ────────────────────────

_CLASS_TYPEOF = (
    ("Runner____", "score", "sport", "running", 82),
    ("Volume_3", "pages", "kind", "novel", 224),
    ("Town____", "people", "county", "yorkshire", 17),
    ("Track____", "seconds", "album", "low", 224),
    ("Ore_2", "melting", "symbol", "sn", 232),
    ("Berth____", "floor", "deck", "upper", 5),
    ("Blade____", "weight", "steel", "carbon", 7),
    ("Side____", "points", "league", "second", 12),
    ("Coord____", "distance", "system", "grid", 40),
    ("Extent____", "width", "units", "pixels", 64),
    ("Duo____", "left", "pairing", "close", 11),
    ("Reach_3", "high", "arc", "wide", 47),
    ("Result_3", "points", "referee", "kit", 72),
    ("Journey____", "miles", "route", "coastal", 180),
    ("Board____", "rows", "theme", "wooden", 6),
    ("Barrel____", "litres", "cooper", "ida", 90),
    ("Token_3", "worth", "metal", "copper", 20),
    ("Note____", "octave", "lyric", "hello", 4),
    ("Stage_3", "order", "cue", "ready", 3),
    ("Crate_4", "depth", "stamp", "fragile", 5),
)

_P139 = _page(
    "ts-class-typeof",
    139,
    "The type of the class itself",
    "typeof Class, which is the constructor rather than an instance.",
    "A class gives you two types with one declaration. Its name is the type "
    "of an instance; `typeof Name` is the type of the class object itself - "
    "the thing you call new on, and the thing the statics live on. A "
    "function that builds instances takes the second, which is how a "
    "factory can be handed a class it has never heard of.",
    "ts_class_typeof",
    [
        (
            f"Write a class {cls} with a static {static_field} of "
            f'"{static_value}" and a constructor taking {field}. Write '
            f"build_one(maker: typeof {cls}, value: number) that news it up. "
            f"Use it with {number}, then print the field, the static, and "
            f"whether the result is an instance of {cls}.",
            {
                "cls": cls,
                "field": field,
                "static_field": static_field,
                "static_value": static_value,
                "number": number,
            },
        )
        for cls, field, static_field, static_value, number in _CLASS_TYPEOF
    ],
)


# ── 140. A conditional type that recurses ────────────────────

_DEEP = (
    ("flatten_it", "value * 2", 7, "finn"),
    ("unwrap_it", "value + 10", 12, "morning"),
    ("dig_out", "value * 3", 5, "ubik"),
    ("peel_it", "value - 4", 20, "ripon"),
    ("strip_it", "value * 4", 6, "tin"),
    ("bare_it", "value + 25", 9, "cabin"),
    ("core_of", "value * 5", 8, "plane"),
    ("inner_of", "value - 2", 30, "blues"),
    ("heart_of", "value * 6", 4, "origin"),
    ("centre_of", "value + 50", 11, "banner"),
    ("pith_of", "value * 7", 3, "pair"),
    ("kernel_of", "value - 7", 40, "span"),
    ("base_of_it", "value * 8", 2, "final"),
    ("root_of_it", "value + 100", 15, "leg"),
    ("seed_of", "value * 9", 5, "grid"),
    ("stone_of", "value - 9", 50, "cask"),
    ("nub_of", "value * 11", 6, "front"),
    ("gist_of", "value + 12", 18, "middle"),
    ("crux_of", "value * 12", 4, "stir"),
    ("nut_of", "value - 11", 60, "small"),
)

_P140 = _page(
    "ts-deep-conditional",
    140,
    "A conditional type that recurses",
    "infer inside a conditional type, applied to its own result.",
    "`T extends readonly (infer Inner)[] ? Flat<Inner> : T` peels one array "
    "layer and then asks the same question again, so number[][][] and "
    "number[] and number all reduce to number. This is where the type "
    "language stops being annotation and starts being a small functional "
    "program - and it is how types like DeepReadonly and DeepPartial are "
    "written.",
    "ts_deep_conditional",
    [
        (
            "Write `type Flat<T> = T extends readonly (infer Inner)[] ? "
            f"Flat<Inner> : T`. Declare a Flat<number[][][]> holding "
            f'{number} and a Flat<string[][]> holding "{word}". Write {func} '
            f"taking a Flat<number[][]> and returning {expr}, then print all "
            f"three.",
            {"func": func, "expr": expr, "number": number, "word": word},
        )
        for func, expr, number, word in _DEEP
    ],
)


TS_PAGES_6: tuple[Page, ...] = (
    _P131,
    _P132,
    _P133,
    _P134,
    _P135,
    _P136,
    _P137,
    _P138,
    _P139,
    _P140,
)
