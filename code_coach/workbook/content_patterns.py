"""Intermediate pages 149-158: patterns in text, and work not done twice.

Four pages of regular expressions, because they are the tool everybody
eventually needs and most people only half learn - enough to write one
that nearly works and not enough to fix it.

Then recursion into nested data, and the two ways to stop a recursive
function redoing work: a dict you keep yourself, then the one line that
replaces it. **kwargs, which is the half page 93 left out. Numbers in
other bases. And reduce, which is the fold that sum and max are already
doing.

Python only, same as 81-148.
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


def _nested_text(item) -> str:
    """The nested data written as Python would write it.

    Built rather than repr'd: repr of a one-item tuple carries a trailing
    comma, and the prompt has to read exactly like the answer.
    """
    if isinstance(item, tuple):
        return "[" + ", ".join(_nested_text(x) for x in item) + "]"
    return repr(item)


# ── 149. Finding the first match ─────────────────────────────

_SEARCHES = (
    ("order 1234 shipped", r"\d+"),
    ("room 7 is open", r"\d+"),
    ("total: 4550 units", r"\d+"),
    ("call 555 now", r"\d+"),
    ("ada wrote 1843", r"\d+"),
    ("track 09 playing", r"\d+"),
    ("hello world", r"w\w+"),
    ("the quick fox", r"q\w+"),
    ("red green blue", r"g\w+"),
    ("iron and gold", r"g\w+"),
    ("north by south", r"s\w+"),
    ("salt and pepper", r"p\w+"),
    ("invoice 8842 paid", r"\d+"),
    ("desk 3 is free", r"\d+"),
    ("count: 9017 items", r"\d+"),
    ("dial 999 today", r"\d+"),
    ("grace wrote 1959", r"\d+"),
    ("side 02 playing", r"\d+"),
    ("morning light", r"l\w+"),
    ("the brown dog", r"b\w+"),
)

_P149 = _page(
    "regex-search",
    149,
    "Finding the first match",
    "re.search, group and start.",
    "A regular expression is a small language for describing shapes of "
    "text. \\d means a digit and + means one or more, so \\d+ is a run of "
    "digits - the point being that you did not have to say how many or "
    "where. search hands back a match object for the first one it finds, "
    "or None if there is none, which is why real code checks before "
    "calling group. Always write the pattern as a raw string, r\"...\", "
    "or the backslashes get eaten before re ever sees them.",
    "regex_search",
    [
        (
            "Import re. Set text to "
            + repr(text)
            + ". Search it with the raw-string pattern "
            + pattern
            + " into found, then print found.group() and found.start().",
            {"text": text, "pattern": pattern},
        )
        for text, pattern in _SEARCHES
    ],
)


# ── 150. Capturing the pieces you wanted ─────────────────────

_GROUPS = (
    ("ada:36", r"(\w+):(\d+)"),
    ("sam:41", r"(\w+):(\d+)"),
    ("kyoto=1463", r"(\w+)=(\d+)"),
    ("oslo=709", r"(\w+)=(\d+)"),
    ("bowie 1977", r"(\w+) (\d+)"),
    ("kate 1985", r"(\w+) (\d+)"),
    ("width-30", r"(\w+)-(\d+)"),
    ("height-12", r"(\w+)-(\d+)"),
    ("iron/26", r"(\w+)/(\d+)"),
    ("gold/79", r"(\w+)/(\d+)"),
    ("track#9", r"(\w+)#(\d+)"),
    ("room#404", r"(\w+)#(\d+)"),
    ("finn:27", r"(\w+):(\d+)"),
    ("ida:44", r"(\w+):(\d+)"),
    ("ripon=17", r"(\w+)=(\d+)"),
    ("lima=998", r"(\w+)=(\d+)"),
    ("eno 1975", r"(\w+) (\d+)"),
    ("byrne 1980", r"(\w+) (\d+)"),
    ("depth-55", r"(\w+)-(\d+)"),
    ("copper/29", r"(\w+)/(\d+)"),
)

_P150 = _page(
    "regex-groups",
    150,
    "Capturing the pieces you wanted",
    "Brackets in a pattern, and group(1) and group(2).",
    "Matching is rarely the point - you want the parts. Round brackets "
    "mark a piece to keep, and they are numbered from 1 in the order "
    "their opening bracket appears. group() with no number is still the "
    "whole match, which is worth remembering when group(1) surprises "
    "you. This is the pattern for pulling a name and a number out of a "
    "line of a log or a config file, which is most of what regular "
    "expressions get used for.",
    "regex_groups",
    [
        (
            "Import re. Set text to "
            + repr(text)
            + ". Search it with the raw-string pattern "
            + pattern
            + " into found, then print group 1 and group 2.",
            {"text": text, "pattern": pattern},
        )
        for text, pattern in _GROUPS
    ],
)


# ── 151. Every match, not just the first ─────────────────────

_FINDALLS = (
    ("a1 b22 c333", r"\d+"),
    ("x5 y50 z500", r"\d+"),
    ("one 1 two 2 three 3", r"\d+"),
    ("roads 4 and 44", r"\d+"),
    ("port 80 and 443", r"\d+"),
    ("in 1977 and 1985", r"\d+"),
    ("red green blue", r"\w+"),
    ("salt and pepper", r"\w+"),
    ("cat cot cut", r"c.t"),
    ("bat bet bit", r"b.t"),
    ("aa ab ac", r"a\w"),
    ("do re mi", r"\w\w"),
    ("d4 e55 f666", r"\d+"),
    ("p6 q60 r600", r"\d+"),
    ("four 4 five 5 six 6", r"\d+"),
    ("lanes 3 and 33", r"\d+"),
    ("port 22 and 8080", r"\d+"),
    ("gold tin lead", r"\w+"),
    ("hat hot hut", r"h.t"),
    ("la ti do", r"\w\w"),
)

_P151 = _page(
    "regex-findall",
    151,
    "Every match, not just the first",
    "re.findall, and the list of strings it gives back.",
    "search stops at the first one; findall keeps going and hands back a "
    "plain list of strings - not match objects, so no group calls, just "
    "the text. Note that everything comes back as a string even when it "
    "is obviously a number, because re works on text and has no opinion "
    "about what the text means. int() is your job.",
    "regex_findall",
    [
        (
            "Import re. Set text to "
            + repr(text)
            + ", then print re.findall with the raw-string pattern "
            + pattern
            + " over it.",
            {"text": text, "pattern": pattern},
        )
        for text, pattern in _FINDALLS
    ],
)


# ── 152. Replacing by pattern ────────────────────────────────

_SUBS = (
    ("one 1 two 2", r"\d", "#"),
    ("a1 b2 c3", r"\d", "*"),
    ("call 555 1234", r"\d+", "NUMBER"),
    ("room 7 floor 3", r"\d+", "N"),
    ("red green blue", r"green", "gold"),
    ("salt and pepper", r"and", "or"),
    ("cat cot cut", r"c.t", "pet"),
    ("bat bet bit", r"b.t", "ball"),
    ("too   many   spaces", r"\s+", " "),
    ("tabs\tand\tgaps", r"\s+", " "),
    ("keep-the-dashes", r"-", " "),
    ("dots.between.words", r"\.", " "),
    ("four 4 five 5", r"\d", "#"),
    ("d4 e5 f6", r"\d", "*"),
    ("dial 999 8080", r"\d+", "NUMBER"),
    ("desk 3 floor 9", r"\d+", "N"),
    ("gold tin lead", r"tin", "zinc"),
    ("hat hot hut", r"h.t", "cap"),
    ("wide    open    spaces", r"\s+", " "),
    ("keep_the_bars", r"_", " "),
)

_P152 = _page(
    "regex-sub",
    152,
    "Replacing by pattern",
    "re.sub, for replacing things you cannot spell out in advance.",
    "replace on a string needs the exact text; sub needs only the shape "
    "of it, which is the difference between removing one known word and "
    "removing every number. Two of these collapse runs of whitespace with "
    "\\s+ into a single space, which is the single most useful sub there "
    "is for text that came from somewhere else. Like everything in "
    "Python's strings, it hands back a new one.",
    "regex_sub",
    [
        (
            "Import re. Set text to "
            + repr(text)
            + ", then print re.sub with the raw-string pattern "
            + pattern
            + " replacing matches with "
            + repr(into)
            + ".",
            {"text": text, "pattern": pattern, "into": into},
        )
        for text, pattern, into in _SUBS
    ],
)


# ── 153. A function that calls itself on the inside ──────────

_NESTED = (
    ("total", (1, (2, 3), (4, (5,)))),
    ("total", ((1, 2), (3, 4))),
    ("add_up", (1, 2, (3,))),
    ("add_up", ((1, (2, (3, (4,)))),)),
    ("deep_sum", (10, (20, 30), 40)),
    ("deep_sum", (((1,), (2,)), 3)),
    ("total", (5, (5, (5, (5,))))),
    ("total", ((7,), (8,), (9,))),
    ("add_up", (1, (1, 1), ((1, 1),))),
    ("add_up", ((100,), 200, (300, (400,)))),
    ("deep_sum", ((2, 4), (6, (8, 10)))),
    ("deep_sum", (0, (1, (2, (3, (4,)))))),
    ("total", (6, (7, 8), (9, (10,)))),
    ("total", ((5, 6), (7, 8))),
    ("add_up", (4, 5, (6,))),
    ("add_up", ((9, (8, (7, (6,)))),)),
    ("deep_sum", (50, (60, 70), 80)),
    ("deep_sum", (((4,), (5,)), 6)),
    ("total", (3, (3, (3, (3,))))),
    ("add_up", ((11,), 22, (33, (44,)))),
)

_P153 = _page(
    "recurse-nested",
    153,
    "A function that calls itself on the inside",
    "Recursion where the nesting is in the data, not in a countdown.",
    "Page 97 called a function on a smaller number. This calls it on a "
    "smaller piece of the data, which is what recursion is actually for: "
    "the list holds lists, and nobody knows how deep. isinstance asks "
    "whether this item is itself a list - if it is, hand it to the same "
    "function and add up whatever comes back. There is no loop that could "
    "do this without you writing your own stack, which is the honest test "
    "of when recursion earns its place.",
    "recurse_nested",
    [
        (
            "Write "
            + name
            + "(items) returning 0 plus, for each item, either "
            + name
            + " of the item when isinstance says it is a list, or the item "
            "itself. Print "
            + name
            + " of "
            + _nested_text(nested)
            + ".",
            {"name": name, "nested": nested},
        )
        for name, nested in _NESTED
    ],
)


# ── 154. Remembering answers in a dict ───────────────────────

_MEMOS = (
    (10, 15),
    (12, 18),
    (8, 20),
    (14, 16),
    (11, 22),
    (9, 25),
    (13, 17),
    (7, 24),
    (16, 19),
    (6, 21),
    (15, 23),
    (5, 26),
    (17, 27),
    (18, 28),
    (4, 29),
    (19, 14),
    (3, 13),
    (20, 12),
    (2, 11),
    (21, 10),
)

_P154 = _page(
    "memo-dict",
    154,
    "Remembering answers in a dict",
    "Memoisation by hand: check the cache, compute, store, return.",
    "Plain recursive fibonacci works out fib(8) over and over - the same "
    "answer, hundreds of times, and it gets exponentially worse. A dict "
    "outside the function fixes it: if the answer is already there, hand "
    "it back; otherwise work it out once and keep it. Try these without "
    "the cache at 30 or so and you will feel the difference. This is the "
    "closure idea from page 118 turned into something useful - state "
    "that outlives the call.",
    "memo_dict",
    [
        (
            "Set cache to an empty dict. Write fib(n) returning n when n "
            "is under 2, otherwise storing fib(n - 1) + fib(n - 2) in "
            "cache under n if it is not already there, and returning "
            "cache[n]. Print fib of "
            + " and then ".join(str(v) for v in values)
            + ".",
            {"values": values},
        )
        for values in _MEMOS
    ],
)


# ── 155. The same idea, as one line ──────────────────────────

_CACHED = (
    (20, 30),
    (25, 35),
    (22, 32),
    (28, 34),
    (24, 31),
    (26, 36),
    (21, 33),
    (27, 38),
    (23, 37),
    (29, 40),
    (19, 39),
    (18, 41),
    (31, 42),
    (32, 43),
    (33, 44),
    (34, 45),
    (35, 46),
    (36, 47),
    (37, 48),
    (38, 49),
)

_P155 = _page(
    "lru-cache-use",
    155,
    "The same idea, as one line",
    "@lru_cache, which is page 154 written for you.",
    "One import and one line above the def, and the cache from the page "
    "before disappears - same answers, none of the bookkeeping. It is a "
    "decorator, exactly the shape page 117 built by hand, which is worth "
    "sitting with for a second: the thing you wrote from scratch is the "
    "thing the standard library ships. The catch is that arguments have "
    "to be hashable, so a function taking a list cannot use it, and the "
    "cache holds everything it has seen until you call cache_clear.",
    "lru_cache_use",
    [
        (
            "Import lru_cache from functools. Write fib(n) decorated with "
            "@lru_cache, returning n when n is under 2 and otherwise "
            "fib(n - 1) + fib(n - 2). Print fib of "
            + " and then ".join(str(v) for v in values)
            + ".",
            {"values": values},
        )
        for values in _CACHED
    ],
)


# ── 156. As many named arguments as you like ─────────────────

_KWARGS = (
    ("describe", (("name", "ada"), ("age", 36))),
    ("describe", (("city", "kyoto"), ("people", 1463))),
    ("show", (("title", "dune"), ("pages", 412))),
    ("show", (("artist", "bowie"), ("year", 1977))),
    ("report", (("colour", "red"), ("count", 12))),
    ("report", (("metal", "gold"), ("number", 79))),
    ("record", (("team", "reds"), ("score", 41))),
    ("record", (("day", "mon"), ("hours", 8))),
    ("listing", (("suit", "spades"), ("rank", 11))),
    ("listing", (("word", "sky"), ("length", 3))),
    ("details", (("host", "example"), ("port", 8080))),
    ("details", (("song", "alive"), ("seconds", 245))),
    ("describe", (("name", "finn"), ("age", 27))),
    ("describe", (("city", "oslo"), ("people", 709))),
    ("show", (("title", "ubik"), ("pages", 224))),
    ("show", (("artist", "kate"), ("year", 1985))),
    ("report", (("colour", "teal"), ("count", 30))),
    ("record", (("team", "blues"), ("score", 12))),
    ("listing", (("word", "moon"), ("length", 4))),
    ("details", (("host", "local"), ("port", 5173))),
)

_P156 = _page(
    "kwargs-use",
    156,
    "As many named arguments as you like",
    "**kwargs: the star-args of page 93, with names attached.",
    "One star collects the positional arguments into a tuple; two stars "
    "collect the named ones into a dict, keys being the names as strings. "
    "That is the entire difference. It is how a function accepts options "
    "it was not written knowing about, and how wrappers pass arguments "
    "through to whatever they wrap without caring what they are. Note "
    "these print in sorted order rather than the order they were passed - "
    "the dict does keep insertion order, but relying on the caller's "
    "spelling order is a promise you should not make.",
    "kwargs_use",
    [
        (
            "Write "
            + name
            + " taking **details, looping over sorted(details) and "
            "printing each key and its value on one line. Call it with "
            + ", ".join(f"{k}={v!r}" for k, v in pairs)
            + ".",
            {"name": name, "pairs": pairs},
        )
        for name, pairs in _KWARGS
    ],
)


# ── 157. The same number, three ways ─────────────────────────

_BASES = (
    (255, 8),
    (10, 8),
    (64, 8),
    (7, 8),
    (128, 8),
    (100, 8),
    (31, 8),
    (200, 8),
    (1, 8),
    (170, 8),
    (63, 8),
    (256, 16),
    (12, 8),
    (48, 8),
    (99, 8),
    (5, 8),
    (192, 8),
    (33, 8),
    (240, 8),
    (511, 16),
)

_P157 = _page(
    "number-bases",
    157,
    "The same number, three ways",
    "bin and hex, and the b format spec that pads.",
    "A number has no base - 255 and 0xff and 0b11111111 are the same "
    "value written differently, and bin and hex give you the written "
    "form as a string with a 0b or 0x on the front. When you want the "
    "digits without the prefix, and padded to a fixed width, that is the "
    "b format spec from page 129 doing it. Worth knowing the moment you "
    "touch a colour, a permission bit, or anything that came off a wire.",
    "number_bases",
    [
        (
            "Set value to "
            + repr(value)
            + ". Print bin of it, then hex of it, then it formatted with "
            "an f-string using the spec 0"
            + str(width)
            + "b.",
            {"value": value, "width": width},
        )
        for value, width in _BASES
    ],
)


# ── 158. Folding a list down to one value ────────────────────

_REDUCES = (
    ((1, 2, 3, 4), "a * b"),
    ((2, 3, 4), "a * b"),
    ((1, 2, 3, 4, 5), "a + b"),
    ((10, 20, 30), "a + b"),
    ((5, 3, 9, 1), "a if a > b else b"),
    ((5, 3, 9, 1), "a if a < b else b"),
    ((2, 2, 2, 2), "a * b"),
    ((100, 5), "a - b"),
    ((1, 10, 100), "a + b"),
    ((7, 2, 3), "a * b"),
    ((12, 4, 2), "a - b"),
    ((6, 11, 4, 8), "a if a > b else b"),
    ((2, 3, 5), "a * b"),
    ((4, 5, 6), "a * b"),
    ((2, 4, 6, 8), "a + b"),
    ((15, 25, 35), "a + b"),
    ((8, 2, 11, 4), "a if a > b else b"),
    ((8, 2, 11, 4), "a if a < b else b"),
    ((3, 3, 3, 3), "a * b"),
    ((200, 30, 5), "a - b"),
)

_P158 = _page(
    "reduce-use",
    158,
    "Folding a list down to one value",
    "functools.reduce, and what sum and max are underneath.",
    "reduce takes the first two items, hands them to your function, then "
    "takes that answer and the next item, and keeps going until there is "
    "one value left. sum is reduce with addition; max is reduce with "
    "pick-the-bigger, and two of these write exactly that. It is worth "
    "meeting once so the pattern is familiar - and then, in Python, worth "
    "reaching for sum and max instead, because they say what they mean "
    "and reduce makes the reader work it out.",
    "reduce_use",
    [
        (
            "Import reduce from functools. Set numbers to ["
            + _seq(items)
            + "], then print reduce over it with a lambda taking a and b "
            "that returns "
            + expr
            + ".",
            {"items": items, "expr": expr},
        )
        for items, expr in _REDUCES
    ],
)


PATTERN_PAGES: tuple[Page, ...] = (
    _P149,
    _P150,
    _P151,
    _P152,
    _P153,
    _P154,
    _P155,
    _P156,
    _P157,
    _P158,
)
