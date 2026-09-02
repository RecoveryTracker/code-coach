"""Pages 49 onwards: text that comes apart, and things found by name.

The first pages that are not offered in every language. C has no split and no
map, and the honest C answer to either is a week of memory management rather
than one exercise — so these name the six languages that have the types, and
C's ramp ends at page 48 with everything it can genuinely do.

Nothing here iterates a map. Rust's HashMap has a deliberately unpredictable
order and the others differ from each other, so every exercise looks up keys
it names. Print what you asked for, not what the container felt like giving.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

# Everything but C — see the note above and in emit_more4.
NOT_C = ("python", "javascript", "typescript", "dart", "cpp", "rust")


def _ex(
    page_id: str, n: int, prompt: str, shape: str, /, **args
) -> Exercise:
    return Exercise(
        id=f"{page_id}-{n:02d}", prompt=prompt, shape=shape, args=args
    )


def _page(page_id, number, name, teaches, example, exercises) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(exercises),
        languages=NOT_C,
    )


# ── 49. Cutting a sentence up ────────────────────────────────

_SENTENCES = (
    "one two three",
    "hello world",
    "the quick brown fox",
    "a b c d",
    "code coach workbook",
    "keep going you are doing fine",
    "red green blue",
    "morning",
    "type it out again",
    "practice makes it easy",
    "up down left right",
    "last one now",
)

_P49 = _page(
    "split-words",
    49,
    "Cutting a sentence up",
    "Turning one string into a list of its words.",
    "The separator is what you split on and it does not survive: split "
    "\"a b c\" on spaces and you get three pieces with no spaces in them. One "
    "of these is a single word with no spaces at all, which still gives you a "
    "list — of one — and that is worth seeing.",
    [
        _ex(
            "split-words",
            i + 1,
            f'Split the sentence "{s}" on its spaces and print each word on '
            f"its own line.",
            "split_words",
            sentence=s,
        )
        for i, s in enumerate(_SENTENCES)
    ],
)


# ── 50. How many words ───────────────────────────────────────

_COUNT_SENTENCES = (
    "one two three",
    "hello world",
    "the quick brown fox jumps",
    "a",
    "code coach",
    "counting the words in this line",
    "up down",
    "one two three four five six",
    "just here",
    "how many words is this",
    "seven",
    "a b c d e f g",
)

_P50 = _page(
    "count-words",
    50,
    "How many words",
    "Asking the list you just made how long it is.",
    "Two steps that people try to do in one: cut it up, then count the "
    "pieces. Counting spaces and adding one gets the same answer here and "
    "stops being the same answer the moment there are two spaces together.",
    [
        _ex(
            "count-words",
            i + 1,
            f'Split the sentence "{s}" on its spaces and print how many words '
            f"it has.",
            "count_words",
            sentence=s,
        )
        for i, s in enumerate(_COUNT_SENTENCES)
    ],
)


# ── 51. Putting it back together ─────────────────────────────

_JOINS = (
    (["one", "two", "three"], " "),
    (["a", "b", "c"], "-"),
    (["hello", "world"], " "),
    (["red", "green", "blue"], ", "),
    (["2026", "09", "01"], "/"),
    (["code", "coach"], " "),
    (["x", "y"], "+"),
    (["up", "down", "left", "right"], " "),
    (["one"], " "),
    (["a", "b", "c", "d"], ""),
    (["first", "second", "third"], " then "),
    (["end", "of", "the", "list"], "."),
)

_P51 = _page(
    "join-list",
    51,
    "Putting it back together",
    "One line out of a list, with something between the pieces.",
    "The separator goes between the pieces, not after each one — so three "
    "words take two separators, not three. Building it by hand with a loop is "
    "where the trailing one creeps in, and one of these joins with nothing at "
    "all, which is a separator too.",
    [
        _ex(
            "join-list",
            i + 1,
            "Put the words "
            + ", ".join(f'"{w}"' for w in words)
            + " in a list, then print them as one line with "
            + (
                "nothing between them."
                if sep == ""
                else f'"{sep}" between them.'
            ),
            "join_list",
            words=words,
            sep=sep,
        )
        for i, (words, sep) in enumerate(_JOINS)
    ],
)


# ── 52. Looking something up ─────────────────────────────────

_TABLES = (
    ((("ann", 30), ("bob", 25)), ["ann"]),
    ((("ann", 30), ("bob", 25)), ["bob"]),
    ((("red", 1), ("green", 2), ("blue", 3)), ["green"]),
    ((("one", 1), ("two", 2), ("three", 3)), ["one", "three"]),
    ((("cat", 4), ("bird", 2)), ["bird", "cat"]),
    ((("small", 10), ("large", 90)), ["large"]),
    ((("a", 100), ("b", 200), ("c", 300)), ["c", "a"]),
    ((("monday", 1), ("friday", 5)), ["friday"]),
    ((("x", 7),), ["x"]),
    ((("north", 0), ("south", 180)), ["south", "north"]),
    ((("apple", 3), ("pear", 8), ("plum", 5)), ["pear"]),
    ((("start", 1), ("end", 99)), ["start", "end", "start"]),
)

_P52 = _page(
    "map-lookup",
    52,
    "Looking something up",
    "A container you reach into by name rather than by position.",
    "A list answers \"what is at 3\". A map answers \"what is stored under "
    "this name\", which is what you actually want most of the time — nobody "
    "remembers that the price is at position 4. The names are the point; "
    "there is no order to rely on and none of these asks for one.",
    [
        _ex(
            "map-lookup",
            i + 1,
            "Build a table holding "
            + ", ".join(f'"{k}" = {v}' for k, v in pairs)
            + ". Print the value stored under "
            + ", then ".join(f'"{k}"' for k in keys)
            + ".",
            "map_lookup",
            pairs=list(pairs),
            keys=keys,
        )
        for i, (pairs, keys) in enumerate(_TABLES)
    ],
)


# ── 53. Filling a table in a loop ────────────────────────────

_BUILDS = (
    (5, "i * i", "its square", [3]),
    (5, "i * i", "its square", [5, 1]),
    (10, "i * i", "its square", [7]),
    (6, "i * 2", "double it", [4]),
    (8, "i * 2", "double it", [8, 2]),
    (4, "i * 10", "it times 10", [3]),
    (12, "i * i", "its square", [12, 6]),
    (7, "i + 100", "it plus 100", [5]),
    (9, "i * i * i", "it cubed", [4]),
    (5, "i * 3", "it times 3", [2, 5]),
    (10, "i % 4", "the remainder when divided by 4", [9]),
    (6, "i * i", "its square", [1, 2, 3]),
)

_P53 = _page(
    "map-build",
    53,
    "Filling a table in a loop",
    "Putting things into a map as you go, then asking for one back.",
    "The loop writes every key and you only read one or two of them, which "
    "is the shape of every lookup table ever built: pay once to fill it, then "
    "answer instantly for ever. Note that the key is the number itself, not a "
    "position — nothing here counts from 0.",
    [
        _ex(
            "map-build",
            i + 1,
            f"Build a table by looping from 1 to {upto}, storing each number "
            f"with {described}. Then print what is stored under "
            + ", then ".join(str(k) for k in keys)
            + ".",
            "map_build",
            upto=upto,
            expr=expr,
            keys=keys,
        )
        for i, (upto, expr, described, keys) in enumerate(_BUILDS)
    ],
)


# ── 54. Is it in there ───────────────────────────────────────

_CONTAINS = (
    ("workbook", "book", "yes", "no"),
    ("workbook", "cook", "yes", "no"),
    ("keyboard", "board", "found", "missing"),
    ("keyboard", "beard", "found", "missing"),
    ("practice", "act", "yes", "no"),
    ("practice", "cat", "yes", "no"),
    ("typing", "ping", "in there", "not in there"),
    ("typing", "pong", "in there", "not in there"),
    ("hello world", "o w", "yes", "no"),
    ("hello world", "ow", "yes", "no"),
    ("repetition", "pet", "found", "missing"),
    ("repetition", "pit", "found", "missing"),
)

_P54 = _page(
    "str-contains",
    54,
    "Is it in there",
    "Asking whether one piece of text appears inside another.",
    "These come in pairs on purpose — one that is in there and one that very "
    "nearly is. \"cook\" is not in \"workbook\" even though every letter of it "
    "is, because the piece has to appear in one run. Reading it and being "
    "sure is the exercise.",
    [
        _ex(
            "str-contains",
            i + 1,
            f'Print "{yes}" if "{piece}" appears anywhere inside "{word}", '
            f'and "{no}" if it does not.',
            "str_contains",
            word=word,
            piece=piece,
            yes=yes,
            no=no,
        )
        for i, (word, piece, yes, no) in enumerate(_CONTAINS)
    ],
)


# ── 55. A piece out of the middle ────────────────────────────

_SLICES = (
    ("workbook", 0, 4),
    ("workbook", 4, 8),
    ("keyboard", 3, 8),
    ("practice", 0, 3),
    ("practice", 5, 8),
    ("typing", 1, 4),
    ("repetition", 2, 6),
    ("hello", 1, 3),
    ("characters", 0, 4),
    ("characters", 4, 10),
    ("workbook", 2, 6),
    ("finished", 0, 6),
)

_P55 = _page(
    "str-slice",
    55,
    "A piece out of the middle",
    "Taking a run of characters, from one position up to another.",
    "The first number is where you start and the second is where you stop — "
    "and you stop *before* it, so 0 to 4 gives you four characters, not five. "
    "Same off-by-one as every other page that counts from 0, in the place it "
    "surprises people most.",
    [
        _ex(
            "str-slice",
            i + 1,
            f'Print the characters of "{word}" from position {start} up to '
            f"but not including position {end}.",
            "str_slice",
            word=word,
            start=start,
            end=end,
        )
        for i, (word, start, end) in enumerate(_SLICES)
    ],
)


# ── 56. Where does it start ──────────────────────────────────

_FINDS = (
    ("workbook", "book"),
    ("workbook", "work"),
    ("keyboard", "board"),
    ("practice", "act"),
    ("typing", "ping"),
    ("repetition", "pet"),
    ("hello world", "world"),
    ("hello world", "o"),
    ("characters", "act"),
    ("finished", "shed"),
    ("morning", "ing"),
    ("coffee", "ff"),
)

_P56 = _page(
    "str-find",
    56,
    "Where does it start",
    "The position a piece of text begins at.",
    "Page 40 found a number in a list; this finds text inside text, and "
    "hands back the position the same way. One of these looks for a single "
    "letter that appears twice — you get the first, which is the same "
    "stopping-early rule wearing different clothes.",
    [
        _ex(
            "str-find",
            i + 1,
            f'Print the position where "{piece}" starts inside "{word}", '
            f"counting from 0.",
            "str_find",
            word=word,
            piece=piece,
        )
        for i, (word, piece) in enumerate(_FINDS)
    ],
)


MORE_PAGES_5: tuple[Page, ...] = (
    _P49,
    _P50,
    _P51,
    _P52,
    _P53,
    _P54,
    _P55,
    _P56,
)
