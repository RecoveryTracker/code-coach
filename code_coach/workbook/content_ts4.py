"""TypeScript pages 111-120: the type system meeting real code.

Pages 101-110 computed types. These use them where they pay: readonly for
what must not change, ?? for the value that might not be there, implements
for a class that promises a shape, and a brand for two numbers that must
never be swapped.

Page 115 is the one people want long before they meet it. TypeScript types
are structural, so a UserId and an OrderId that are both numbers are the
same type - you can hand one to the other's function all day and nothing
complains. Intersecting with a phantom brand gives them separate identities
and costs nothing at run time, because the brand never exists there.

Page 118 is the other keeper: a type that mentions itself describes JSON, a
tree, or a nested list in one line.
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


# ── 111. A field the compiler will not let you change ────────

_READONLY = (
    ("Runner", "name", "finn", "score", 82, 90),
    ("Volume", "title", "ubik", "pages", 224, 300),
    ("Town", "name", "ripon", "people", 17, 20),
    ("Track_", "title", "art", "seconds", 224, 240),
    ("Ore", "name", "tin", "melting", 232, 250),
    ("Berth", "name", "cabin", "floor", 5, 6),
    ("Blade", "name", "plane", "weight", 7, 9),
    ("Side", "name", "blues", "points", 12, 20),
    ("Coord", "label", "origin", "distance", 0, 12),
    ("Extent", "label", "banner", "width", 64, 96),
    ("Duo", "label", "pair", "left", 11, 15),
    ("Reach", "label", "span", "high", 47, 60),
    ("Result", "label", "final", "points", 72, 80),
    ("Journey", "label", "leg", "miles", 180, 200),
    ("Board", "label", "grid", "rows", 6, 8),
    ("Barrel", "label", "cask", "litres", 90, 100),
    ("Token", "face", "front", "worth", 20, 25),
    ("Note", "pitch", "middle c", "octave", 4, 5),
    ("Stage_", "label", "stir", "order", 3, 4),
    ("Crate", "label", "small", "depth", 5, 7),
)

_P111 = _page(
    "ts-readonly",
    111,
    "A field the compiler will not let you change",
    "readonly, which is checked at compile time and gone at run time.",
    "readonly is a promise to the compiler, not a lock on the object. "
    "Assigning to the readonly field below stops compiling; the ordinary "
    "field beside it does not. Nothing guards it at run time - the "
    "JavaScript that comes out has no idea - which is exactly why it costs "
    "nothing to use everywhere.",
    "ts_readonly",
    [
        (
            f"Write an interface {cls} with a readonly {fixed} string and an "
            f"ordinary {loose} number. Make one holding "
            f'"{fixed_value}" and {loose_value}, change {loose} to '
            f"{changed}, then print both fields.",
            {
                "cls": cls,
                "fixed": fixed,
                "fixed_value": fixed_value,
                "loose": loose,
                "loose_value": loose_value,
                "changed": changed,
            },
        )
        for cls, fixed, fixed_value, loose, loose_value, changed in _READONLY
    ],
)


# ── 112. A value that might not be there ─────────────────────

_NULLS = (
    ("Profile", "nickname", "greet_it", "finn", "friend"),
    ("Entry_", "caption", "label_it", "morning", "untitled"),
    ("Setting", "override", "value_of", "fast", "default"),
    ("Record_", "note", "note_on", "checked", "no note"),
    ("Person_", "title", "address_to", "doctor", "no title"),
    ("Track_", "album", "album_of", "low", "unreleased"),
    ("Town", "county", "county_of", "yorkshire", "unknown"),
    ("Blade", "brand", "brand_of", "stanley", "unbranded"),
    ("Volume", "series", "series_of", "valis", "standalone"),
    ("Ore", "symbol", "symbol_of", "sn", "none"),
    ("Berth", "deck", "deck_of", "upper", "unassigned"),
    ("Side", "league", "league_of", "second", "friendly"),
    ("Coord", "system", "system_of", "grid", "unspecified"),
    ("Extent", "units", "units_of", "pixels", "unitless"),
    ("Result", "referee", "referee_of", "kit", "unofficial"),
    ("Journey", "route", "route_of", "coastal", "direct"),
    ("Board", "theme", "theme_of", "wooden", "plain"),
    ("Barrel", "cooper", "cooper_of", "ida", "unknown maker"),
    ("Note", "lyric", "lyric_of", "hello", "instrumental"),
    ("Crate", "stamp", "stamp_of", "fragile", "unmarked"),
)

_P112 = _page(
    "ts-strict-null",
    112,
    "A value that might not be there",
    "Optional fields, and ?? for the value to use when there is none.",
    "An optional field is string | undefined, and the compiler will not let "
    "you use it as a string until you have dealt with the undefined. ?? "
    "supplies the fallback and narrows in one move. Note the third line "
    "below: a field explicitly set to undefined takes the fallback too, "
    "which is the difference between ?? and ||, since || would also swallow "
    "an empty string.",
    "ts_strict_null",
    [
        (
            f"Write an interface {cls} with an optional {field} string. "
            f'Write {func} returning it or "{fallback}" when it is absent. '
            f'Print the result for one holding "{present}", for an empty '
            f"object, and for one whose {field} is undefined.",
            {
                "cls": cls,
                "field": field,
                "func": func,
                "present": present,
                "fallback": fallback,
            },
        )
        for cls, field, func, present, fallback in _NULLS
    ],
)


# ── 113. A class promising to match an interface ─────────────

_IMPLEMENTS = (
    ("Speaks", "Cow", "speak", "moo", "legs", 4),
    ("Rolls", "Barrow", "roll_on", "trundle", "wheels", 1),
    ("Cuts", "Saw_", "cut_it", "across the grain", "teeth", 24),
    ("Holds", "Crate_", "hold_it", "twelve bottles", "depth", 5),
    ("Sounds", "Drum", "sound_it", "thud", "skins", 2),
    ("Floats", "Barge", "float_it", "on the canal", "metres", 22),
    ("Grinds", "Mill", "grind_it", "into flour", "stones", 2),
    ("Lifts", "Crane", "lift_it", "high up", "tonnes", 8),
    ("Weighs", "Scales", "weigh_it", "to the gram", "pans", 2),
    ("Marks", "Chalk", "mark_it", "in white", "sticks", 12),
    ("Burns", "Kiln", "burn_it", "at red heat", "hours", 9),
    ("Chills", "Cellar", "chill_it", "underground", "degrees", 8),
    ("Sifts", "Sieve", "sift_it", "through mesh", "holes", 400),
    ("Binds", "Glue", "bind_it", "with glue", "grams", 50),
    ("Pours", "Jug", "pour_it", "steadily", "litres", 2),
    ("Sews", "Needle", "sew_it", "in small stitches", "eyes", 1),
    ("Digs", "Spade", "dig_it", "into clay", "inches", 11),
    ("Rings", "Bell", "ring_it", "clear", "notes", 3),
    ("Prints", "Press", "print_it", "in black", "plates", 4),
    ("Steers", "Tiller", "steer_it", "to port", "arms", 1),
)

_P113 = _page(
    "ts-implements",
    113,
    "A class promising to match an interface",
    "implements, which checks the class rather than describing it.",
    "extends inherits behaviour; implements only promises a shape. The "
    "class gets nothing from the interface - it writes every member itself "
    "- but the compiler now checks that it did, and says so at the class "
    "rather than at the first place someone used it wrongly. A class can "
    "implement several interfaces and extend only one thing.",
    "ts_implements",
    [
        (
            f"Write an interface {iface} with a {method} returning a string "
            f"and a readonly {field} number. Write a class {cls} that "
            f'implements it, returning "{says}" and holding {number}. Assign '
            f"one to a {iface} and print both.",
            {
                "iface": iface,
                "cls": cls,
                "method": method,
                "says": says,
                "field": field,
                "number": number,
            },
        )
        for iface, cls, method, says, field, number in _IMPLEMENTS
    ],
)


# ── 114. A lookup that cannot ask for a missing key ──────────

_PICKS = (
    ("runner", (("name", "finn"), ("score", 82)), "name", "score"),
    ("volume", (("title", "ubik"), ("pages", 224)), "pages", "title"),
    ("town", (("name", "ripon"), ("people", 17)), "name", "people"),
    ("track", (("title", "art"), ("seconds", 224)), "seconds", "title"),
    ("ore", (("name", "tin"), ("melting", 232)), "name", "melting"),
    ("berth", (("name", "cabin"), ("floor", 5)), "floor", "name"),
    ("blade", (("name", "plane"), ("weight", 7)), "name", "weight"),
    ("side", (("name", "blues"), ("points", 12)), "points", "name"),
    ("coord", (("label", "origin"), ("distance", 0)), "label", "distance"),
    ("extent", (("label", "banner"), ("width", 64)), "width", "label"),
    ("duo", (("label", "pair"), ("left", 11)), "label", "left"),
    ("reach", (("label", "span"), ("high", 47)), "high", "label"),
    ("result", (("label", "final"), ("points", 72)), "label", "points"),
    ("journey", (("label", "leg"), ("miles", 180)), "miles", "label"),
    ("board", (("label", "grid"), ("rows", 6)), "label", "rows"),
    ("barrel", (("label", "cask"), ("litres", 90)), "litres", "label"),
    ("token", (("face", "front"), ("worth", 20)), "face", "worth"),
    ("note", (("pitch", "middle c"), ("octave", 4)), "octave", "pitch"),
    ("stage", (("label", "stir"), ("order", 3)), "label", "order"),
    ("crate", (("label", "small"), ("depth", 5)), "depth", "label"),
)

_P114 = _page(
    "ts-keyof-generic",
    114,
    "A lookup that cannot ask for a missing key",
    "K extends keyof T, and a return type of T[K].",
    "This is the signature worth memorising. K extends keyof T means the "
    "key has to be one the object really has, so a typo stops compiling "
    "rather than returning undefined. T[K] means the answer has the type of "
    "that particular field - ask for the name and you get a string, ask for "
    "the count and you get a number, from one function.",
    "ts_keyof_generic",
    [
        (
            "Write pick<T, K extends keyof T>(thing: T, key: K): T[K]. Make "
            f"a const {const} holding "
            + ", ".join(f"{k} = {v!r}" for k, v in entries)
            + f'. Print picking "{first}" and then "{second}".',
            {
                "const_name": const,
                "entries": entries,
                "first_key": first,
                "second_key": second,
            },
        )
        for const, entries, first, second in _PICKS
    ],
)


# ── 115. Two numbers that are not interchangeable ────────────

_BRANDS = (
    ("UserId", "user", "OrderId", "order", "user_label", "user", 41),
    ("OrderId", "order", "CartId", "cart", "order_label", "order", 108),
    ("PageId", "page", "PostId", "post", "page_label", "page", 7),
    ("RoomId", "room", "DeskId", "desk", "room_label", "room", 214),
    ("TrackId", "track", "AlbumId", "album", "track_label", "track", 9),
    ("TownId", "town", "ShireId", "shire", "town_label", "town", 17),
    ("BladeId", "blade", "HandleId", "handle", "blade_label", "blade", 3),
    ("SideId", "side", "LeagueId", "league", "side_label", "side", 12),
    ("CrateId", "crate", "PalletId", "pallet", "crate_label", "crate", 55),
    ("NoteId", "note", "BarId", "bar", "note_label", "note", 4),
    ("SeatId", "seat", "RowId", "row", "seat_label", "seat", 22),
    ("PassId", "pass", "GateId", "gate", "pass_label", "pass", 88),
    ("JobId", "job", "TaskId", "task", "job_label", "job", 31),
    ("LeafId", "leaf", "TwigId", "twig", "leaf_label", "leaf", 6),
    ("CaskId", "cask", "VatId", "vat", "cask_label", "cask", 90),
    ("OreId", "ore", "SeamId", "seam", "ore_label", "ore", 232),
    ("PathId", "path", "RouteId", "route", "path_label", "path", 180),
    ("SlotId", "slot", "BayId", "bay", "slot_label", "slot", 14),
    ("TokenId", "token", "KeyId", "key", "token_label", "token", 20),
    ("StageId", "stage", "SceneId", "scene", "stage_label", "stage", 3),
)

_P115 = _page(
    "ts-branded",
    115,
    "Two numbers that are not interchangeable",
    "A brand, which gives a number an identity the type system respects.",
    "TypeScript types are structural: two things with the same shape are "
    "the same type. So a UserId and an OrderId that are both number can be "
    "passed to each other's functions all day and nothing complains, which "
    "is a real bug waiting to happen. Intersecting with a phantom property "
    "gives them separate identities. The brand never exists at run time - "
    "the last line proves it is still an ordinary number - and it costs "
    "nothing but the cast at the boundary.",
    "ts_branded",
    [
        (
            f"Write {first_type} and {second_type} as number intersected "
            f"with a readonly brand. Write a function that casts a number to "
            f"{first_type} and a {func} that takes one and returns "
            f'"{label} " and the value. Print calling it with {number}, then '
            f"print that value plus 1 to show it is still a number.",
            {
                "first_type": first_type,
                "first_brand": first_brand,
                "second_type": second_type,
                "second_brand": second_brand,
                "func": func,
                "label": label,
                "number": number,
            },
        )
        for (
            first_type,
            first_brand,
            second_type,
            second_brand,
            func,
            label,
            number,
        ) in _BRANDS
    ],
)


# ── 116. A filter the compiler learns from ───────────────────

_FILTERS = (
    (("finn", None, "ida"), "toUpperCase"),
    (("teal", "plum", None), "toUpperCase"),
    ((None, "oak", "ash"), "toUpperCase"),
    (("thu", None, "fri", None), "toUpperCase"),
    (("tin", "lead", None, "zinc"), "toUpperCase"),
    (("MORNING", None, "EVENING"), "toLowerCase"),
    ((None, "RIPON", "OSLO"), "toLowerCase"),
    (("KIWI", "PLUM", None), "toLowerCase"),
    (("UBIK", None, "VALIS"), "toLowerCase"),
    ((None, "ART", "SONS"), "toLowerCase"),
    (("cabin", None, "hold"), "toUpperCase"),
    (("plane", "chisel", None), "toUpperCase"),
    ((None, "blues", "whites"), "toUpperCase"),
    (("la", None, "ti", "do"), "toUpperCase"),
    (("near", "far", None), "toUpperCase"),
    (("EAST", None, "WEST"), "toLowerCase"),
    ((None, "UP", "DOWN"), "toLowerCase"),
    (("FIRST", "SECOND", None), "toLowerCase"),
    (("SHUT", None, "OPEN"), "toLowerCase"),
    ((None, "SOFT", "LOUD"), "toLowerCase"),
)

_P116 = _page(
    "ts-filter-guard",
    116,
    "A filter the compiler learns from",
    "A type predicate, so filter narrows the array's type as well.",
    "filter with an ordinary boolean callback gives you back the type you "
    "started with - still (string | null)[], still refusing to let you call "
    "a string method. Declare the callback as `value is string` and the "
    "compiler narrows the result to string[]. Same code at run time, "
    "entirely different at compile time, which is why the last line below "
    "is allowed to shout.",
    "ts_filter_guard",
    [
        (
            "Write is_present(value: string | null): value is string. Make a "
            "(string | null)[] holding "
            + ", ".join("null" if v is None else f'"{v}"' for v in items)
            + f", filter it into a string[], then print the length, the "
            f"entries joined, and them again with {method} applied.",
            {"items": items, "method": method},
        )
        for items, method in _FILTERS
    ],
)


# ── 117. A mapped type that renames as it goes ───────────────

_REMAPS = (
    ("Runner", "name", "score", "finn", 82, "the_"),
    ("Volume", "title", "pages", "ubik", 224, "the_"),
    ("Town", "name", "people", "ripon", 17, "the_"),
    ("Track_", "title", "seconds", "art", 224, "my_"),
    ("Ore", "name", "melting", "tin", 232, "my_"),
    ("Berth", "name", "floor", "cabin", 5, "my_"),
    ("Blade", "name", "weight", "plane", 7, "own_"),
    ("Side", "name", "points", "blues", 12, "own_"),
    ("Coord", "label", "distance", "origin", 0, "own_"),
    ("Extent", "label", "width", "banner", 64, "raw_"),
    ("Duo", "label", "left", "pair", 11, "raw_"),
    ("Reach", "label", "high", "span", 47, "raw_"),
    ("Result", "label", "points", "final", 72, "old_"),
    ("Journey", "label", "miles", "leg", 180, "old_"),
    ("Board", "label", "rows", "grid", 6, "old_"),
    ("Barrel", "label", "litres", "cask", 90, "new_"),
    ("Token", "face", "worth", "front", 20, "new_"),
    ("Note", "pitch", "octave", "middle c", 4, "new_"),
    ("Stage_", "label", "order", "stir", 3, "any_"),
    ("Crate", "label", "depth", "small", 5, "any_"),
)

_P117 = _page(
    "ts-key-remap",
    117,
    "A mapped type that renames as it goes",
    "`as` inside a mapped type, with a template literal for the new key.",
    "Page 96 mapped every key to a new value type. This renames the keys "
    "themselves: the `as` clause takes a template literal type and the "
    "result has prefixed keys carrying the original types. It is how "
    "getters get generated - name becomes getName - without writing either "
    "list twice.",
    "ts_key_remap",
    [
        (
            f"Write an interface {cls} with a string {first} and a number "
            f"{second}. Write Prefixed<T> mapping every key K to "
            f'`{prefix}${{K}}` with the same type. Make a '
            f'Prefixed<{cls}> holding "{first_value}" and {second_value}, '
            f"then print both fields and how many keys it has.",
            {
                "cls": cls,
                "first": first,
                "second": second,
                "first_value": first_value,
                "second_value": second_value,
                "prefix": prefix,
            },
        )
        for cls, first, second, first_value, second_value, prefix in _REMAPS
    ],
)


# ── 118. A type that mentions itself ─────────────────────────

_TREES = (
    ("total_of", (1, (2, 3), (4, (5,))), 7),
    ("total_of", ((1, 2), (3, 4)), 11),
    ("add_up", (1, 2, (3,)), 6),
    ("add_up", ((1, (2, (3, (4,)))),), 9),
    ("deep_sum", (10, (20, 30), 40), 12),
    ("deep_sum", (((1,), (2,)), 3), 15),
    ("total_of", (5, (5, (5, (5,)))), 20),
    ("total_of", ((7,), (8,), (9,)), 3),
    ("add_up", (1, (1, 1), ((1, 1),)), 8),
    ("add_up", ((100,), 200, (300, (400,))), 42),
    ("deep_sum", ((2, 4), (6, (8, 10))), 16),
    ("deep_sum", (0, (1, (2, (3, (4,))))), 21),
    ("total_of", ((6, 7), (8, 9)), 5),
    ("add_up", (2, (4, 6), (8, (10,))), 13),
    ("deep_sum", (((3,), (6,)), 9), 27),
    ("total_of", (11, (22, (33,))), 44),
    ("add_up", ((5, 10), (15, (20, 25))), 30),
    ("deep_sum", (1, (3, (5, (7, (9,))))), 2),
    ("total_of", ((12,), (24,), (36,)), 48),
    ("add_up", ((2,), 4, (6, (8, (10,)))), 14),
)

_P118 = _page(
    "ts-recursive-type",
    118,
    "A type that mentions itself",
    "A recursive type alias, and the recursive function that walks it.",
    "`type Nested = number | Nested[]` is legal and describes an "
    "arbitrarily deep list of numbers in one line. The same shape types "
    "JSON, and trees, and anything else that contains itself. The function "
    "that walks it narrows on typeof and recurses - the type and the code "
    "have the same shape, which is usually the sign you have described the "
    "data properly.",
    "ts_recursive_type",
    [
        (
            f"Write `type Nested = number | Nested[]` and a {func} that "
            f"returns a number unchanged and sums an array by recursing. "
            f"Print it for {tree} and then for the plain number {plain}.",
            {"func": func, "tree": tree, "plain": plain},
        )
        for func, tree, plain in _TREES
    ],
)


# ── 119. A tagged union driving a state change ───────────────

_REDUCERS = (
    ("Counter_", "step", "add", "take", "clear", 0, 5, 2),
    ("Tally", "apply_to", "gain", "lose", "reset", 10, 7, 3),
    ("Score_", "score_it", "award", "deduct", "restart", 0, 12, 4),
    ("Level_", "shift", "climb", "fall", "ground", 1, 6, 2),
    ("Fuel", "burn", "fill", "spend", "empty", 60, 20, 15),
    ("Stock", "move_it", "receive", "ship", "zero", 100, 40, 25),
    ("Purse", "spend_it", "earn", "pay", "broke", 50, 30, 20),
    ("Depth_", "dive", "descend", "ascend", "surface", 0, 40, 10),
    ("Heat_", "warm_it", "raise", "cool", "cold", 20, 15, 5),
    ("Volume__", "turn_it", "louder", "softer", "mute", 5, 4, 3),
    ("Distance", "travel", "advance", "retreat", "home", 0, 25, 10),
    ("Weight__", "load_it", "add_on", "take_off", "bare", 0, 18, 6),
    ("Water", "pour_it", "fill_up", "draw_off", "dry", 90, 35, 15),
    ("Charge", "power_it", "charge_up", "drain", "flat", 80, 15, 45),
    ("Pace_", "run_it", "quicken", "slacken", "still", 6, 8, 3),
    ("Height_", "raise_it", "up_by", "down_by", "floor", 0, 30, 12),
    ("Balance", "settle", "credit", "debit", "square", 200, 75, 50),
    ("Count__", "count_it", "more", "fewer", "none", 0, 9, 4),
    ("Angle", "turn_by", "clockwise", "widdershins", "north", 0, 90, 45),
    ("Pressure", "press", "pump", "bleed", "slack", 30, 20, 10),
)

_P119 = _page(
    "ts-reducer",
    119,
    "A tagged union driving a state change",
    "A discriminated union of actions, and the switch that consumes it.",
    "This is the shape every state library uses. Each action is an object "
    "with a literal kind, and the union of them is the only thing the "
    "reducer accepts. Inside each case the compiler knows which members "
    "exist - the reset action has no `by` and asking for one there does not "
    "compile. Page 106's never in the default would make it exhaustive too.",
    "ts_reducer",
    [
        (
            f'Write an Action union of {{ kind: "{up}"; by: number }}, '
            f'{{ kind: "{down}"; by: number }} and {{ kind: "{reset}" }}, '
            f"and a {func} over a state holding a total. Start at {start}, "
            f"apply {up} by {plus}, then {down} by {minus}, then {reset}, "
            f"printing the total after each.",
            {
                "type_name": type_name,
                "func": func,
                "up": up,
                "down": down,
                "reset": reset,
                "start": start,
                "plus": plus,
                "minus": minus,
            },
        )
        for type_name, func, up, down, reset, start, plus, minus in _REDUCERS
    ],
)


# ── 120. A list nobody can push to ───────────────────────────

_READONLY_ARRAYS = (
    ("readings", "with_one_more", (1, 2, 3), 4),
    ("counts", "extended", (10, 20), 30),
    ("scores", "plus_one", (82, 37, 4), 55),
    ("pages", "appended", (224, 261), 190),
    ("people", "grown", (17, 709), 998),
    ("points", "added_to", (12, 55), 33),
    ("weights", "with_extra", (7, 2), 4),
    ("floors", "one_up", (5, 2), 1),
    ("seconds", "longer", (224, 207), 386),
    ("depths", "deeper", (2, 40), 15),
    ("widths", "wider", (3, 30), 12),
    ("heights", "taller", (5, 50), 25),
    ("hours", "with_another", (9, 5), 4),
    ("sizes", "bigger", (1, 9), 5),
    ("costs", "dearer", (4, 40), 22),
    ("speeds", "faster", (1, 20), 11),
    ("tallies", "counted_on", (6, 21), 13),
    ("spans", "stretched", (2, 22), 9),
    ("loads", "heavier", (5, 50), 28),
    ("melting", "hotter", (232, 327), 419),
)

_P120 = _page(
    "ts-readonly-array",
    120,
    "A list nobody can push to",
    "readonly number[], and why a function should ask for one.",
    "A readonly array has no push, no pop and no sort - the mutating "
    "methods are simply not on the type. Take one as a parameter and you "
    "have told every caller you will not touch their array, and the "
    "compiler holds you to it. Building a new one with a spread is still "
    "fine, and gives back an ordinary array. This is the cheapest "
    "documentation in the language.",
    "ts_readonly_array",
    [
        (
            f"Make a readonly number[] called {const} holding "
            + ", ".join(str(n) for n in items)
            + f". Write {func} taking a readonly number[] and returning a "
            f"new array with {added} on the end. Print the original length, "
            f"the new length, and the last entry of the new one.",
            {
                "const_name": const,
                "func": func,
                "items": items,
                "added": added,
            },
        )
        for const, func, items, added in _READONLY_ARRAYS
    ],
)


TS_PAGES_4: tuple[Page, ...] = (
    _P111,
    _P112,
    _P113,
    _P114,
    _P115,
    _P116,
    _P117,
    _P118,
    _P119,
    _P120,
)
