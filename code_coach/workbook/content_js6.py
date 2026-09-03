"""JavaScript intermediate pages 131-140: newer methods, bigger numbers,
and the order things happen in.

at() with a negative index. The copying array methods that took until
2023 to arrive. The two isNaNs, which disagree. BigInt. yield*. for
await...of. Object.fromEntries. matchAll. Then the event loop, where a
promise callback always beats a zero-millisecond timer. And finally.

Page 139 is the one that turns up in interviews and, more usefully,
explains why a console.log you added seems to happen in the wrong order.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

JAVASCRIPT = ("javascript",)


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
        languages=JAVASCRIPT,
        tier="intermediate",
    )


def _seq(items) -> str:
    return ", ".join(str(v) for v in items)


# ── 131. Counting from the end ───────────────────────────────

_ATS = (
    ((10, 20, 30, 40), "javascript", 1),
    ((5, 6, 7), "node", 0),
    ((1, 2, 3, 4, 5), "array", 2),
    ((100, 200, 300), "string", 1),
    ((9, 8, 7, 6), "method", 0),
    ((11, 22, 33), "value", 2),
    ((2, 4, 6, 8), "index", 3),
    ((15, 25, 35), "length", 1),
    ((7, 14, 21, 28), "number", 2),
    ((3, 6, 9), "object", 0),
    ((12, 24, 36, 48), "symbol", 1),
    ((50, 60, 70), "return", 2),
)

_P131 = _page(
    "js-at",
    131,
    "Counting from the end",
    "at(), which takes a negative index where brackets do not.",
    "numbers[-1] is not the last item - it is a property called '-1', "
    "which does not exist, so you get undefined. That is why JavaScript "
    "spent twenty years writing numbers[numbers.length - 1], which the "
    "last line here still does. at() takes a negative index properly, "
    "and works on strings too. It is the smallest possible feature and a "
    "genuine relief.",
    "js_at",
    [
        (
            "Set numbers to ["
            + _seq(items)
            + "] and word to "
            + repr(word)
            + ", both const. Log numbers.at of -1, then numbers.at of "
            + str(index)
            + ", then word.at of -1, then the last item of numbers using "
            "brackets and length.",
            {"items": items, "word": word, "index": index},
        )
        for items, word, index in _ATS
    ],
)


# ── 132. Sorting and reversing without damage ────────────────

_IMMUTABLES = (
    ((3, 1, 2), 99),
    ((5, 4, 9, 1), 0),
    ((10, 2, 8), 50),
    ((7, 3, 5), 12),
    ((100, 50, 75), 1),
    ((2, 1), 8),
    ((9, 8, 7, 6), 4),
    ((4, 12, 8, 1), 20),
    ((33, 11, 22), 7),
    ((6, 5, 4, 3), 30),
    ((15, 3, 27), 9),
    ((88, 12, 45), 60),
)

_P132 = _page(
    "js-immutable-array",
    132,
    "Sorting and reversing without damage",
    "toSorted, toReversed and with, which copy rather than change.",
    "sort, reverse and splice all damage the array they are given, which "
    "page 101 showed and which has caused more quiet bugs than any other "
    "part of the language. These three do the same jobs and hand back a "
    "new array instead - with() being the one that replaces a single "
    "item by position. The last line proves the original survived all "
    "three. They are recent, so very old runtimes will not have them; "
    "everything current does.",
    "js_immutable_array",
    [
        (
            "Set numbers to ["
            + _seq(items)
            + "], const. Make sorted with toSorted and a numeric compare, "
            "reversed with toReversed, and changed with the first item "
            "replaced by "
            + str(replacement)
            + " using with. Log all three joined with ', ', then numbers "
            "itself.",
            {"items": items, "replacement": replacement},
        )
        for items, replacement in _IMMUTABLES
    ],
)


# ── 133. The two isNaNs, and the safe limit ──────────────────

_CHECKS = (
    ("abc", 5, 5.5),
    ("hello", 10, 2.5),
    ("x", 0, 0.5),
    ("twelve", 100, 99.9),
    ("n/a", 7, 7.25),
    ("none", 42, 41.5),
    ("many", 1, 1.5),
    ("zero", 64, 63.75),
    ("word", 3, 3.3),
    ("text", 256, 255.5),
    ("empty", 12, 12.5),
    ("value", 9, 8.5),
)

_P133 = _page(
    "js-number-checks",
    133,
    "The two isNaNs, and the safe limit",
    "Number.isNaN against the global isNaN, and MAX_SAFE_INTEGER.",
    "The two isNaNs ask different questions. Number.isNaN asks whether "
    "this value is the NaN value, so a string is simply not, and the "
    "answer is false. The global isNaN converts first and asks whether "
    "the result is NaN, so a word gives true. The global one is almost "
    "never what you meant. Then the last line: past MAX_SAFE_INTEGER, "
    "adding one and adding two give the same number, because a double "
    "has run out of precision. That is when you reach for BigInt.",
    "js_number_checks",
    [
        (
            "Log Number.isNaN of "
            + repr(text)
            + ", then the global isNaN of the same string, then "
            "Number.isInteger of "
            + str(whole)
            + ", then of "
            + str(fraction)
            + ", then whether MAX_SAFE_INTEGER plus 1 equals "
            "MAX_SAFE_INTEGER plus 2.",
            {"text": text, "whole": whole, "fraction": fraction},
        )
        for text, whole, fraction in _CHECKS
    ],
)


# ── 134. Numbers past what a double can hold ─────────────────

_BIGINTS = (
    (9007199254740991, 2),
    (9007199254740993, 4),
    (12345678901234567890, 10),
    (99999999999999999999, 1),
    (2**63, 8),
    (10**20, 5),
    (9007199254740992, 3),
    (123456789012345678, 22),
    (2**70, 6),
    (10**25, 7),
    (555555555555555555555, 9),
    (2**80, 11),
)

_P134 = _page(
    "js-bigint",
    134,
    "Numbers past what a double can hold",
    "BigInt, the n suffix, and why it will not mix.",
    "Every ordinary JavaScript number is a double, so whole numbers stop "
    "being exact past about nine thousand million million - which page "
    "133 just demonstrated. A BigInt is exact at any size, written with "
    "an n on the end. The catch is deliberate: mixing a BigInt and a "
    "Number in arithmetic throws a TypeError rather than quietly "
    "converting, because converting would lose the precision you asked "
    "for. Convert on purpose or not at all.",
    "js_bigint",
    [
        (
            "Set big to the BigInt "
            + str(value)
            + ", const. Log big plus "
            + str(added)
            + " as a BigInt, converted to a string. Then log typeof big. "
            "Then in a try log big plus the ordinary number "
            + str(added)
            + ", catching the problem and logging its constructor's name.",
            {"value": value, "added": added},
        )
        for value, added in _BIGINTS
    ],
)


# ── 135. One generator handing on to another ─────────────────

_DELEGATES = (
    (0, (1, 2), 3),
    (10, (20, 30), 40),
    (1, (2, 3, 4), 5),
    (100, (200,), 300),
    (5, (6, 7), 8),
    (0, (9, 8), 7),
    (2, (4, 6), 8),
    (11, (22, 33), 44),
    (1, (1, 1), 1),
    (7, (14, 21), 28),
    (3, (6, 9, 12), 15),
    (50, (60,), 70),
)

_P135 = _page(
    "js-yield-star",
    135,
    "One generator handing on to another",
    "yield*, which passes every value through.",
    "yield* hands on everything another generator produces, which is how "
    "you build one out of several - walking a tree, chaining sources, "
    "flattening a level at a time. Without it you write a for...of loop "
    "whose whole body is a yield, which works and says less. It "
    "delegates to anything iterable, not only generators, so yield* on "
    "an array works too.",
    "js_yield_star",
    [
        (
            "Write a generator inner yielding "
            + " and ".join(str(n) for n in inner)
            + ". Write a generator outer that yields "
            + str(first)
            + ", then delegates to inner with yield*, then yields "
            + str(last)
            + ". Log outer spread into an array and joined with ', '.",
            {"first": first, "inner": inner, "last": last},
        )
        for first, inner, last in _DELEGATES
    ],
)


# ── 136. Waiting on each value in turn ───────────────────────

_AWAITS = (
    ("ticks", "n * 2", 3),
    ("counts", "n * n", 4),
    ("steps", "n + 10", 3),
    ("beats", "n * 5", 4),
    ("pulses", "n + 1", 5),
    ("marks", "n * 3", 3),
    ("rows", "n * 100", 3),
    ("items", "n + n", 4),
    ("frames", "n * 7", 3),
    ("bars", "n - 1", 5),
    ("blips", "n * 4", 4),
    ("waves", "n + 5", 3),
)

_P136 = _page(
    "js-for-await",
    136,
    "Waiting on each value in turn",
    "An async generator, and for await...of.",
    "An async generator is both things at once: it yields values like "
    "page 102's generator, and each one may take time to arrive. for "
    "await...of waits for each in turn, which is what you want for lines "
    "from a file, rows from a database, or pages from an API - anything "
    "arriving in a stream rather than all at once. Note it only works "
    "inside an async function, and that it is deliberately one at a "
    "time: for all of them together you want Promise.all.",
    "js_for_await",
    [
        (
            "Write an async generator "
            + name
            + "(limit) that loops n from 1 to limit yielding "
            + expr
            + ". Write an async main that uses for await...of over "
            + name
            + "("
            + str(limit)
            + "), logging each value, and call main.",
            {"name": name, "expr": expr, "limit": limit},
        )
        for name, expr, limit in _AWAITS
    ],
)


# ── 137. An object taken apart and rebuilt ───────────────────

_ENTRIES = (
    ((("ada", 90), ("sam", 7)), 2),
    ((("red", 12), ("blue", 9)), 3),
    ((("mon", 8), ("tue", 6)), 5),
    ((("iron", 26), ("gold", 79)), 2),
    ((("north", 6), ("south", 19)), 10),
    ((("apple", 3), ("pear", 12)), 4),
    ((("saw", 3), ("axe", 8)), 6),
    ((("sky", 3), ("sea", 9)), 7),
    ((("one", 1), ("two", 2)), 100),
    ((("salt", 11), ("pepper", 22)), 3),
    ((("front", 4), ("back", 55)), 2),
    ((("do", 1), ("re", 2)), 9),
)

_P137 = _page(
    "js-from-entries",
    137,
    "An object taken apart and rebuilt",
    "Object.entries out, map in the middle, Object.fromEntries back.",
    "Objects have no map of their own, so the way to transform one is to "
    "turn it into pairs, use the array methods you already know, and "
    "turn it back. fromEntries also takes a Map directly, which is the "
    "neatest way to convert one - and it is the exact inverse of "
    "entries, so the round trip gives you what you started with. Note "
    "the destructuring in the map's parameter list, pulling key and "
    "value out of each pair.",
    "js_from_entries",
    [
        (
            "Set scores to a const object of "
            + ", ".join(f"{k}: {v}" for k, v in pairs)
            + ". Take Object.entries into pairs, then build changed with "
            "Object.fromEntries of pairs mapped so each value is "
            "multiplied by "
            + str(times)
            + ", destructuring key and value in the parameter list. Log "
            "pairs.length, then changed."
            + pairs[0][0]
            + ", then changed's keys sorted and joined with ', '.",
            {"pairs": pairs, "times": times},
        )
        for pairs, times in _ENTRIES
    ],
)


# ── 138. Every match, with its groups ────────────────────────

_MATCHES = (
    ("a1 b22 c333", "#"),
    ("x5 y50 z500", "*"),
    ("p7 q77 r777", "?"),
    ("m2 n22 o222", "-"),
    ("d4 e44 f444", "+"),
    ("g9 h99 i999", "="),
    ("s3 t33 u333", "~"),
    ("j6 k66 l666", "^"),
    ("v1 w11 y111", "%"),
    ("b8 c88 d888", "@"),
    ("e5 f55 g555", "!"),
    ("h2 i22 j222", "&"),
)

_P138 = _page(
    "js-matchall",
    138,
    "Every match, with its groups",
    "matchAll, the g flag, and why match alone is not enough.",
    "match with a g flag gives you the matched text and throws the "
    "groups away; match without g gives you the groups of the first "
    "match only. matchAll gives you every match with its groups intact, "
    "which is what you nearly always wanted - and it returns an iterator, "
    "so it needs spreading before you can use array methods on it. It "
    "insists on the g flag and throws without one, which is a kindness. "
    "replace needs g too, or it changes only the first.",
    "js_matchall",
    [
        (
            "Set text to "
            + repr(text)
            + ", const. Spread text.matchAll of a global regex matching a "
            "letter followed by a captured run of digits into found. Log "
            "found.length, then its first capture group from each match "
            "joined with ', ', then text with every run of digits "
            "replaced by "
            + repr(instead)
            + ".",
            {"text": text, "instead": instead},
        )
        for text, instead in _MATCHES
    ],
)


# ── 139. What runs before what ───────────────────────────────

_ORDERS = (
    ("first", "last", "promise", "timeout"),
    ("start", "end", "micro", "macro"),
    ("one", "two", "then", "later"),
    ("open", "close", "resolved", "delayed"),
    ("begin", "finish", "queued", "scheduled"),
    ("top", "bottom", "microtask", "task"),
    ("a", "b", "c", "d"),
    ("here", "there", "soon", "afterwards"),
    ("now", "still now", "next tick", "next turn"),
    ("sync one", "sync two", "async one", "async two"),
    ("in", "out", "promised", "timed"),
    ("up", "down", "fast", "slow"),
)

_P139 = _page(
    "js-microtask",
    139,
    "What runs before what",
    "Microtasks before timers, and why both come after the last line.",
    "Neither callback runs where it is written. Both are scheduled, and "
    "the rest of the current code finishes first - which is why the two "
    "plain logs come out before either. Then the promise callback runs, "
    "because promise callbacks are microtasks and the queue of those is "
    "emptied before anything else. Only then does the timer fire, even "
    "though it asked for zero milliseconds. This is the whole "
    "explanation for a console.log that seems to happen in the wrong "
    "order.",
    "js_microtask",
    [
        (
            "Log "
            + repr(first)
            + ". Then schedule a setTimeout of 0 that logs "
            + repr(timer)
            + ". Then a resolved Promise whose then logs "
            + repr(promise)
            + ". Then log "
            + repr(last)
            + ".",
            {
                "first": first,
                "last": last,
                "promise": promise,
                "timer": timer,
            },
        )
        for first, last, promise, timer in _ORDERS
    ],
)


# ── 140. The block that runs either way ──────────────────────

_FINALLIES = (
    ("n < 0", "negative", 5, -1, "ok", "caught", "cleanup"),
    ("n == 0", "zero", 3, 0, "fine", "handled", "tidy"),
    ("n > 100", "too big", 50, 200, "good", "rescued", "closing"),
    ("n % 2 == 1", "odd", 4, 7, "even", "odd found", "done"),
    ("n < 10", "small", 12, 4, "big enough", "too small", "finished"),
    ("n > 60", "over", 12, 90, "under", "over the line", "released"),
    ("n == 13", "unlucky", 5, 13, "safe", "unlucky", "closed"),
    ("n < 1", "under one", 6, 0, "positive", "not positive", "swept"),
    ("n > 255", "overflow", 200, 300, "in range", "out of range", "reset"),
    ("n % 5 == 0", "fifth", 3, 10, "not a fifth", "a fifth", "cleared"),
    ("n < -5", "far under", 1, -9, "near", "far", "ended"),
    ("n > 1000", "enormous", 10, 2000, "normal", "enormous", "shut"),
)

_P140 = _page(
    "js-finally",
    140,
    "The block that runs either way",
    "finally, and catch without naming what it caught.",
    "finally runs whichever way the function leaves - after a return, "
    "after a caught throw, even after an uncaught one on its way out. "
    "That is what makes it right for closing and releasing, and the "
    "output here shows the cleanup line printing before each returned "
    "value, because the return is handed back only once finally is done. "
    "The catch takes no name here, which is allowed when you do not need "
    "the error, and says plainly that you are not ignoring anything you "
    "meant to look at.",
    "js_finally",
    [
        (
            "Write check(n) with a try that throws a new Error "
            + repr(message)
            + " when "
            + test.replace("==", "===")
            + " and otherwise returns "
            + repr(fine)
            + ", a catch taking no binding that returns "
            + repr(caught)
            + ", and a finally that logs "
            + repr(always)
            + ". Log check of "
            + str(good)
            + ", then of "
            + str(bad)
            + ".",
            {
                "test": test,
                "message": message,
                "good": good,
                "bad": bad,
                "fine": fine,
                "caught": caught,
                "always": always,
            },
        )
        for test, message, good, bad, fine, caught, always in _FINALLIES
    ],
)


JS_PAGES_6: tuple[Page, ...] = (
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
