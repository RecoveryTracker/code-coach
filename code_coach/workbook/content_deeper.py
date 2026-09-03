"""Intermediate pages 219-228: more surprises, and the last few tools.

Three more behaviours that are not bugs but read like them. round does
not round half up, it rounds half to even. sort returns None, so
`numbers = numbers.sort()` throws your list away. And lstrip takes a set
of characters rather than a prefix, so it will happily eat further into
the word than you meant.

Then nonlocal and global, dict views that keep up with the dict,
suppress, a database with no file, match against real patterns rather
than the literals of page 169, and a class that says what it holds.

Python only, same as 81-218.
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


# ── 219. Rounding that does not go the way you learnt ────────

_ROUNDS = (
    ((0.5, None), (1.5, None), (2.5, None), (2.675, 2)),
    ((3.5, None), (4.5, None), (5.5, None), (1.005, 2)),
    ((0.5, None), (2.5, None), (4.5, None), (2.345, 2)),
    ((6.5, None), (7.5, None), (8.5, None), (0.125, 2)),
    ((1.5, None), (2.5, None), (3.5, None), (1.115, 2)),
    ((10.5, None), (11.5, None), (12.5, None), (3.145, 2)),
    ((0.5, None), (1.5, None), (100.5, None), (2.675, 2)),
    ((9.5, None), (8.5, None), (7.5, None), (0.335, 2)),
    ((2.5, None), (3.5, None), (20.5, None), (1.045, 2)),
    ((5.5, None), (6.5, None), (0.5, None), (2.225, 2)),
    ((13.5, None), (14.5, None), (1.5, None), (4.155, 2)),
    ((0.5, None), (99.5, None), (98.5, None), (1.265, 2)),
)

_P219 = _page(
    "round-bankers",
    219,
    "Rounding that does not go the way you learnt",
    "Round half to even, and why the two-decimal case is worse.",
    "round(0.5) is 0 and round(1.5) is 2. That is not a bug: Python "
    "rounds a half to the nearest even number, because always rounding "
    "halves up biases a long column of figures upward. The fourth line "
    "of each is a different problem - 2.675 is not really 2.675 in "
    "binary, as page 189 showed, so rounding it to two places gives 2.67 "
    "and no rounding rule can save it. For money, use Decimal, which has "
    "a quantize that does exactly what you ask.",
    "round_bankers",
    [
        (
            "Print round of "
            + ", then round of ".join(
                repr(n) if d is None else f"{n!r} to {d} places"
                for n, d in values
            )
            + ".",
            {"values": values},
        )
        for values in _ROUNDS
    ],
)


# ── 220. Both halves of a division, and other bases ──────────

_DIVMODS = (
    (17, 5, "ff", "1010"),
    (20, 3, "1a", "1111"),
    (100, 7, "ff", "1000"),
    (9, 2, "10", "101"),
    (45, 6, "2b", "11011"),
    (7, 7, "7f", "1001"),
    (123, 10, "abc", "110"),
    (64, 8, "40", "1000000"),
    (31, 4, "1f", "11111"),
    (250, 16, "fa", "11111010"),
    (81, 9, "51", "1010001"),
    (13, 5, "d", "1101"),
)

_P220 = _page(
    "divmod-base",
    220,
    "Both halves of a division, and other bases",
    "divmod, and int with a base.",
    "divmod hands back the quotient and the remainder together, which is "
    "the pair you almost always want - seconds into minutes and seconds, "
    "items into full boxes and a leftover - and it does the division "
    "once instead of twice. int with a second argument reads a string "
    "written in that base, so int('ff', 16) is 255. That is how you take "
    "a colour or a permission bitmask from text into a number, and it is "
    "the other direction from the bin and hex of page 157.",
    "divmod_base",
    [
        (
            "Print divmod of "
            + repr(top)
            + " and "
            + repr(bottom)
            + ", then int of "
            + repr(hexed)
            + " in base 16, then int of "
            + repr(binary)
            + " in base 2.",
            {"top": top, "bottom": bottom, "hex": hexed, "binary": binary},
        )
        for top, bottom, hexed, binary in _DIVMODS
    ],
)


# ── 221. Sorting in place, or making a sorted one ────────────

_SORTS = (
    (3, 1, 2),
    (5, 4, 9, 1),
    (10, 2, 8),
    (7, 7, 3),
    (100, 50, 75),
    (2, 1),
    (9, 8, 7, 6),
    (4, 12, 8, 1),
    (33, 11, 22),
    (6, 5, 4, 3, 2),
    (15, 3, 27, 9),
    (88, 12, 45),
)

_P221 = _page(
    "sort-vs-sorted",
    221,
    "Sorting in place, or making a sorted one",
    "list.sort changes and returns None; sorted leaves it and returns.",
    "sorted takes anything and hands back a new list, leaving the "
    "original alone. sort works only on a list, changes it where it "
    "stands, and returns None - which is the trap: numbers = "
    "numbers.sort() replaces your list with None, and Python will not "
    "warn you. The last line here prints that None on purpose. The rule "
    "runs through the language: methods that change a thing in place "
    "return nothing, so you cannot chain them by accident.",
    "sort_vs_sorted",
    [
        (
            "Set numbers to ["
            + _seq(items)
            + "] and made to sorted(numbers). Print numbers, then made. "
            "Then call numbers.sort(), print numbers again, and print the "
            "result of calling numbers.sort().",
            {"items": items},
        )
        for items in _SORTS
    ],
)


# ── 222. Reaching out to a name defined further up ───────────

_SCOPES = (
    ("count", (3, 4), 2),
    ("tally", (1, 2, 3), 3),
    ("total", (10, 20), 1),
    ("hits", (5,), 4),
    ("runs", (2, 2, 2), 2),
    ("score", (7, 8), 5),
    ("seen", (100,), 1),
    ("marks", (4, 5, 6), 2),
    ("visits", (9, 1), 3),
    ("times", (6, 6), 6),
    ("steps", (11, 22), 2),
    ("goes", (1, 1, 1, 1), 1),
)

_P222 = _page(
    "nonlocal-global",
    222,
    "Reaching out to a name defined further up",
    "nonlocal for the enclosing function, global for the module.",
    "Assigning to a name inside a function makes it local, even if a "
    "name like it exists outside - which is why total += n fails with an "
    "UnboundLocalError until you say nonlocal. nonlocal reaches to the "
    "enclosing function; global reaches all the way to the module. Note "
    "that only assignment needs them: reading an outer name has always "
    "worked. Use nonlocal sparingly and global almost never, because a "
    "function that changes things outside itself is hard to test.",
    "nonlocal_global",
    [
        (
            "Set "
            + counter
            + " to 0 at the top. Write outer() with total = 0 and an "
            "inner(n) that declares total nonlocal and adds n to it; call "
            "inner with "
            + " and ".join(str(n) for n in added)
            + ", then return total. Write bump() that declares "
            + counter
            + " global and adds one. Print outer(), call bump() "
            + str(bumps)
            + " times, then print "
            + counter
            + ".",
            {"counter": counter, "added": added, "bumps": bumps},
        )
        for counter, added, bumps in _SCOPES
    ],
)


# ── 223. A view that keeps up with the dict ──────────────────

_VIEWS = (
    ((("apple", 3), ("pear", 5)), ("plum", 7)),
    ((("ada", 36), ("sam", 41)), ("kim", 29)),
    ((("red", 12), ("blue", 9)), ("green", 30)),
    ((("mon", 8), ("tue", 6)), ("wed", 7)),
    ((("iron", 26), ("gold", 79)), ("tin", 50)),
    ((("do", 1), ("re", 2)), ("mi", 3)),
    ((("north", 6), ("south", 19)), ("east", 1)),
    ((("saw", 3), ("axe", 8)), ("file", 1)),
    ((("sky", 3), ("sea", 3)), ("sun", 9)),
    ((("front", 4), ("back", 55)), ("side", 20)),
    ((("one", 1), ("two", 2)), ("six", 6)),
    ((("salt", 11), ("pepper", 22)), ("sugar", 3)),
)

_P223 = _page(
    "dict-views",
    223,
    "A view that keeps up with the dict",
    "keys() is a live view, not a copy.",
    "keys(), values() and items() do not hand you a list - they hand you "
    "a window onto the dict, and the window shows whatever is there now. "
    "Add a key after taking the view and the view has it too, which is "
    "the thing to notice in the output. This is usually what you want "
    "and occasionally a nasty surprise: change a dict while looping over "
    "its keys and Python raises rather than quietly misbehaving. If you "
    "need a snapshot, ask for list(prices.keys()).",
    "dict_views",
    [
        (
            "Set prices to a dict of "
            + ", ".join(f"{k!r}: {v!r}" for k, v in pairs)
            + " and keys to prices.keys(). Print sorted(keys), then add "
            + repr(added[0])
            + " with the value "
            + repr(added[1])
            + " to prices, then print sorted(keys) again and len(keys).",
            {"pairs": pairs, "added": added},
        )
        for pairs, added in _VIEWS
    ],
)


# ── 224. Taking a prefix off, and the trap next to it ────────

# Every one picked so lstrip really does differ from removeprefix - the
# character after the prefix is itself in the prefix, so lstrip keeps
# eating. The emitter raises if a pair ever fails to differ.
_AFFIXES = (
    ("test_example.py", "test_", ".py"),
    ("test_setup.py", "test_", ".py"),
    ("tmp_path.txt", "tmp_", ".txt"),
    ("old_output.log", "old_", ".log"),
    ("dev_env.ini", "dev_", ".ini"),
    ("raw_args.csv", "raw_", ".csv"),
    ("new_entry.md", "new_", ".md"),
    ("bin_index.dat", "bin_", ".dat"),
    ("src_server.py", "src_", ".py"),
    ("web_entry.html", "web_", ".html"),
    ("doc_output.md", "doc_", ".md"),
    ("app_params.json", "app_", ".json"),
)

_P224 = _page(
    "strip-affix",
    224,
    "Taking a prefix off, and the trap next to it",
    "removeprefix and removesuffix, against what lstrip really does.",
    "removeprefix takes off exactly that prefix, once, and leaves the "
    "string alone if it is not there. lstrip looks like it does the same "
    "and does not: its argument is a set of characters, and it keeps "
    "eating from the left while the next character is any of them. "
    "Compare the first and third lines of each - lstrip has chewed "
    "further into the name than you asked. This is one of the most "
    "common bugs in file-handling code, and it was the reason "
    "removeprefix was added.",
    "strip_affix",
    [
        (
            "Set name to "
            + repr(text)
            + ". Print name with the prefix "
            + repr(prefix)
            + " removed, then with the suffix "
            + repr(suffix)
            + " removed, then name.lstrip("
            + repr(prefix)
            + ") - and compare it with the first.",
            {"name": text, "prefix": prefix, "suffix": suffix},
        )
        for text, prefix, suffix in _AFFIXES
    ],
)


# ── 225. An error you have decided not to care about ─────────

_SUPPRESS = (
    ((("apple", 3), ("pear", 5)), "plum", "never reached", "carried on"),
    ((("ada", 36), ("sam", 41)), "kim", "skipped", "still going"),
    ((("red", 12),), "blue", "not printed", "done"),
    ((("mon", 8), ("tue", 6)), "sun", "no", "after the block"),
    ((("iron", 26),), "gold", "unreachable", "finished"),
    ((("do", 1), ("re", 2)), "fa", "nope", "next"),
    ((("north", 6),), "west", "never", "onwards"),
    ((("saw", 3), ("axe", 8)), "drill", "skipped", "end"),
    ((("sky", 3),), "cloud", "not here", "moving on"),
    ((("front", 4), ("back", 5)), "roof", "no chance", "out"),
    ((("one", 1),), "nine", "unseen", "over"),
    ((("salt", 11), ("pepper", 22)), "sugar", "missed", "past it"),
)

_P225 = _page(
    "suppress-use",
    225,
    "An error you have decided not to care about",
    "contextlib.suppress, and what it costs you.",
    "suppress is try/except/pass written so the reader can see the "
    "decision. The important part is what it does not do: it does not "
    "carry on to the next line inside the block - the error still stops "
    "the block dead, which is why the third print never happens. Only "
    "the lines after the with keep going. Use it for errors you have "
    "genuinely decided are fine, and never as a way of making a problem "
    "you do not understand go quiet.",
    "suppress_use",
    [
        (
            "Import suppress from contextlib. Set prices to a dict of "
            + ", ".join(f"{k!r}: {v!r}" for k, v in pairs)
            + ". In a with suppress(KeyError), print prices for "
            + repr(pairs[0][0])
            + ", then for "
            + repr(missing)
            + ", then "
            + repr(unreached)
            + ". After the block print "
            + repr(after)
            + ".",
            {
                "pairs": pairs,
                "missing": missing,
                "unreached": unreached,
                "after": after,
            },
        )
        for pairs, missing, unreached, after in _SUPPRESS
    ],
)


# ── 226. A database with no file ─────────────────────────────

_TABLES = (
    ("people", "age", (("ada", 36), ("sam", 41))),
    ("cities", "people", (("kyoto", 1463), ("oslo", 709))),
    ("metals", "number", (("iron", 26), ("gold", 79))),
    ("books", "pages", (("dune", 412), ("ilium", 780))),
    ("songs", "seconds", (("alive", 245), ("kooks", 173))),
    ("teams", "points", (("reds", 41), ("blues", 12))),
    ("tools", "weight", (("saw", 3), ("axe", 8))),
    ("rooms", "floor", (("attic", 4), ("hall", 1))),
    ("fruit", "count", (("apple", 3), ("pear", 12))),
    ("days", "hours", (("mon", 8), ("tue", 6))),
    ("words", "length", (("sky", 3), ("lake", 4))),
    ("trips", "miles", (("north", 120), ("south", 40))),
)

_P226 = _page(
    "sqlite-memory",
    226,
    "A database with no file",
    "sqlite3 with :memory:, and parameters instead of string joining.",
    "Python ships a whole SQL database, and connecting to :memory: gives "
    "you one that exists only while the program runs - ideal for "
    "learning and for tests. Two habits worth taking from this page. The "
    "question marks are parameters: never build SQL by joining strings "
    "with user input, which is how injection happens. And the ORDER BY "
    "is not decoration - without it a database is free to hand rows back "
    "in any order it likes.",
    "sqlite_memory",
    [
        (
            "Import sqlite3 and connect to ':memory:' as db. Create a "
            "table "
            + table
            + " with name TEXT and "
            + column
            + " INTEGER, then executemany an INSERT with question-mark "
            "parameters for "
            + ", ".join(f"({n!r}, {v!r})" for n, v in rows)
            + ". Loop over a SELECT of name and "
            + column
            + " ordered by name, printing both on one line.",
            {"table": table, "column": column, "rows": rows},
        )
        for table, column, rows in _TABLES
    ],
)


# ── 227. Matching the shape, not just the value ──────────────

_PATTERNS = (
    ("describe", "circle", "r", 5, (1, 2), 42, "unknown"),
    ("name_it", "square", "side", 4, (3, 4), 99, "no idea"),
    ("shape_of", "box", "width", 10, (5, 6), 7, "unknown"),
    ("tell", "line", "length", 12, (7, 8), 0, "nothing"),
    ("kind_of", "dot", "size", 1, (9, 10), 55, "unknown"),
    ("label", "ring", "radius", 8, (2, 3), 11, "no match"),
    ("show", "disc", "across", 20, (4, 5), 33, "unknown"),
    ("read", "gap", "span", 6, (6, 7), 21, "none"),
    ("check", "arc", "degrees", 90, (8, 9), 13, "unknown"),
    ("sort_it", "cube", "edge", 3, (1, 1), 77, "no clue"),
    ("scan", "star", "points", 5, (2, 4), 66, "unknown"),
    ("pick", "wheel", "spokes", 16, (3, 6), 88, "not known"),
)

_P227 = _page(
    "match-structure",
    227,
    "Matching the shape, not just the value",
    "match against a dict pattern and a list pattern.",
    "Page 169 matched literals, which is the least of what match can do. "
    "A dict pattern checks the keys it names and ignores any others, "
    "binding what it finds to a name. A list pattern checks the length "
    "and unpacks in one move. That is the real reason match exists: not "
    "as a switch, but for asking what shape is this and pulling the "
    "pieces out in the same breath, which is otherwise a stack of ifs "
    "with isinstance and len in them.",
    "match_structure",
    [
        (
            "Write "
            + func
            + "(data) matching data: a case for a dict with 'kind' equal "
            "to "
            + repr(kind)
            + " and "
            + repr(key)
            + " bound to found, returning an f-string of "
            + repr(kind)
            + " and found; a case for a two-item list binding first and "
            "second, returning an f-string 'pair first second'; and a "
            "case _ returning "
            + repr(fallback)
            + ". Print it called with that dict holding "
            + repr(found)
            + ", then with ["
            + _seq(pair)
            + "], then with "
            + repr(other)
            + ".",
            {
                "func": func,
                "kind": kind,
                "key": key,
                "found": found,
                "pair": pair,
                "other": other,
                "fallback": fallback,
            },
        )
        for func, kind, key, found, pair, other, fallback in _PATTERNS
    ],
)


# ── 228. A class that says what it holds ─────────────────────

_BOXES = (
    ("Box", "get", 5, "hello"),
    ("Holder", "item_of", 42, "world"),
    ("Wrapper", "unwrap", 7, "text"),
    ("Cell", "value_of", 100, "data"),
    ("Slot", "read", 1, "ada"),
    ("Case", "open_it", 9, "sam"),
    ("Store", "fetch", 12, "kim"),
    ("Bag", "take", 33, "red"),
    ("Crate", "peek", 8, "blue"),
    ("Tin", "inside", 64, "gold"),
    ("Pack", "contents", 21, "iron"),
    ("Jar", "pour", 3, "salt"),
)

_P228 = _page(
    "generic-class",
    228,
    "A class that says what it holds",
    "Generic[T], so a container's type travels with it.",
    "Page 217 put a TypeVar on a function. This puts one on a class, so "
    "Box[int] and Box[str] are different types to a checker while being "
    "one class at runtime. The payoff is that get() is known to return "
    "whatever went in, rather than Any - so a mistake two hundred lines "
    "later is caught where it is written. Nothing here changes what the "
    "program does; both boxes work exactly as they would with no hints "
    "at all.",
    "generic_class",
    [
        (
            "Import Generic and TypeVar from typing and set T to TypeVar "
            "of 'T'. Write a class "
            + cls
            + " inheriting Generic[T], whose __init__ takes item hinted T "
            "and stores it, with a method "
            + method
            + "(self) -> T returning it. Print "
            + cls
            + "("
            + repr(number)
            + ")."
            + method
            + "() and "
            + cls
            + "("
            + repr(word)
            + ")."
            + method
            + "().",
            {"cls": cls, "method": method, "number": number, "word": word},
        )
        for cls, method, number, word in _BOXES
    ],
)


DEEPER_PAGES: tuple[Page, ...] = (
    _P219,
    _P220,
    _P221,
    _P222,
    _P223,
    _P224,
    _P225,
    _P226,
    _P227,
    _P228,
)
