"""JavaScript intermediate pages 111-120: flattening, copying, and the
modern operators.

flat and flatMap. Object spread. structuredClone, which is the deep copy
JavaScript went twenty-five years without. Padding and trimming. Set
operations, which JavaScript still makes you write yourself. Dates,
where the month counts from zero. An Error subclass. Promise chaining.
Array.from. And the logical assignment operators, where ??= and ||=
disagree about zero.

Page 113 is the sequel to page 86: spread copies one level, and the day
your object has an array inside it, that is not enough.
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


# ── 111. An array of arrays, flattened ───────────────────────

_FLATS = (
    (((1, 2), (3, 4), (5,)), "n * 2"),
    (((1, 2), (3,)), "n * 10"),
    (((5, 6), (7, 8)), "n + 1"),
    (((1,), (2,), (3,)), "n * n"),
    (((10, 20), (30, 40)), "n + 5"),
    (((2, 4), (6, 8), (10,)), "n * 3"),
    (((9, 8), (7,)), "n - 1"),
    (((1, 1), (2, 2), (3, 3)), "n * 100"),
    (((11, 22), (33,)), "n + 9"),
    (((4, 8), (12, 16)), "n * 5"),
    (((3,), (6, 9)), "n + n"),
    (((7, 14), (21, 28)), "n * 2"),
)

_P111 = _page(
    "js-flat",
    111,
    "An array of arrays, flattened",
    "flat, and flatMap for when you were about to flatten anyway.",
    "flat pulls the inner arrays up one level - and only one, unless you "
    "pass it a depth or Infinity. flatMap is map followed by one flat, "
    "which sounds like a small saving and turns out to be the shape of a "
    "great deal of real work: take each thing, produce several from it, "
    "and end up with one list rather than a list of lists. Note the last "
    "line: rows itself is untouched, because neither method changes what "
    "it was given.",
    "js_flat",
    [
        (
            "Set rows to ["
            + ", ".join("[" + _seq(r) + "]" for r in rows)
            + "], const. Log rows flattened and joined with ', '. Then "
            "log flatMap over rows, mapping each row's items through "
            + expr
            + ", joined. Then log rows.length.",
            {"rows": rows, "expr": expr},
        )
        for rows, expr in _FLATS
    ],
)


# ── 112. Two objects merged, and who wins ────────────────────

_MERGES = (
    ((("colour", "red"), ("size", "medium")), (("size", "large"),), "colour"),
    ((("mode", "safe"), ("level", "info")), (("level", "debug"),), "mode"),
    ((("host", "local"), ("port", "8080")), (("port", "9000"),), "host"),
    ((("theme", "dark"), ("font", "mono")), (("font", "serif"),), "theme"),
    ((("sort", "name"), ("order", "up")), (("order", "down"),), "sort"),
    ((("shell", "bash"), ("editor", "vi")), (("editor", "nano"),), "shell"),
    ((("region", "eu"), ("tier", "free")), (("tier", "paid"),), "region"),
    ((("lang", "en"), ("units", "metric")), (("units", "imperial"),), "lang"),
    ((("codec", "utf8"), ("newline", "lf")), (("newline", "crlf"),), "codec"),
    ((("depth", "one"), ("style", "plain")), (("style", "rich"),), "depth"),
    ((("cache", "on"), ("retries", "three")), (("retries", "one"),), "cache"),
    ((("format", "csv"), ("header", "yes")), (("header", "no"),), "format"),
)

_P112 = _page(
    "js-object-spread",
    112,
    "Two objects merged, and who wins",
    "Object spread, and the right-hand side taking precedence.",
    "Spreading two objects into a new one gives you everything from "
    "both, and where they share a key the later one wins - which is why "
    "defaults go on the left and choices on the right. Neither original "
    "is changed. Object.assign does the same job but writes into its "
    "first argument, so Object.assign(defaults, chosen) quietly damages "
    "defaults, which is the reason spread is now the usual way. Note "
    "the keys are sorted before printing, because insertion order is not "
    "what this page is about.",
    "js_object_spread",
    [
        (
            "Set defaults to a const object of "
            + ", ".join(f"{k}: {v!r}" for k, v in defaults)
            + " and chosen to "
            + ", ".join(f"{k}: {v!r}" for k, v in chosen)
            + ". Make merged by spreading defaults then chosen. Log "
            "merged."
            + chosen[0][0]
            + ", then merged."
            + only_default
            + ", then its keys sorted and joined with ', '.",
            {
                "defaults": defaults,
                "chosen": chosen,
                "only_default": only_default,
            },
        )
        for defaults, chosen, only_default in _MERGES
    ],
)


# ── 113. A copy that goes all the way down ───────────────────

_CLONES = (
    ((1, 2), 3),
    ((5,), 9),
    ((1, 2, 3), 4),
    ((10, 20), 30),
    ((7, 7), 7),
    ((0,), 1),
    ((4, 8, 12), 16),
    ((2, 4), 6),
    ((100,), 200),
    ((3, 6, 9), 12),
    ((11, 22), 33),
    ((1,), 2),
)

_P113 = _page(
    "js-structured-clone",
    113,
    "A copy that goes all the way down",
    "structuredClone, and what spread does not copy.",
    "Page 86 used spread to copy an object, and this is the limit of "
    "that: spread copies the top level, so an array inside is the same "
    "array, and changing it changes both copies. The two numbers here "
    "differ for exactly that reason. structuredClone copies every level, "
    "and unlike the old JSON round-trip trick it keeps Dates, Maps and "
    "Sets intact. It cannot copy functions, which will throw rather than "
    "silently drop them.",
    "js_structured_clone",
    [
        (
            "Set inner to ["
            + _seq(inner)
            + "] and outer to an object with items set to inner. Make "
            "shallow by spreading outer, and deep with structuredClone of "
            "it. Push "
            + str(added)
            + " onto inner, then log the length of shallow.items and of "
            "deep.items.",
            {"inner": inner, "added": added},
        )
        for inner, added in _CLONES
    ],
)


# ── 114. Padding, trimming and replacing all of them ─────────

_PADS = (
    ("7", 3, "0", "ada", 6, ".", "  spaced  ", "a-b-c", "-", "+"),
    ("9", 4, "0", "sam", 5, "_", "  gap  ", "x_y_z", "_", "-"),
    ("1", 3, "0", "kim", 7, "*", " edge ", "1.2.3", ".", "/"),
    ("42", 5, "0", "jo", 4, "-", "  wide  ", "a b c", " ", ","),
    ("5", 2, "0", "max", 6, "+", " trim ", "p:q:r", ":", ";"),
    ("8", 4, " ", "eve", 5, "=", "  pad  ", "one-two", "-", "="),
    ("3", 3, "0", "abe", 8, ".", " side ", "a,b,c", ",", "|"),
    ("6", 5, "0", "ida", 6, "~", "  room  ", "x/y/z", "/", "-"),
    ("2", 4, "0", "ben", 7, "-", " space ", "a=b=c", "=", ":"),
    ("4", 3, "0", "rey", 5, ".", "  free  ", "l|m|n", "|", "-"),
    ("11", 5, "0", "finn", 8, "_", " left ", "u.v.w", ".", "-"),
    ("0", 3, "0", "nell", 6, "+", "  both  ", "s;t;u", ";", ","),
)

_P114 = _page(
    "js-string-pad",
    114,
    "Padding, trimming and replacing all of them",
    "padStart, padEnd, trim and replaceAll.",
    "padStart is how you get 007 out of 7, and it takes the total width "
    "you want rather than how many characters to add - which is the "
    "thing people get backwards. padEnd does the other side, and the "
    "bars printed here are so you can see where the padding ends. trim "
    "takes whitespace off both ends and nothing out of the middle. "
    "replaceAll is the one that saves you: plain replace on a string "
    "changes only the first match, which page 107 already showed.",
    "js_string_pad",
    [
        (
            "Set word to "
            + repr(short)
            + ", const. Log it padded at the start to width "
            + str(width)
            + " with "
            + repr(filler)
            + ". Then log "
            + repr(name)
            + " padded at the end to "
            + str(wide)
            + " with "
            + repr(dots)
            + ", followed by a bar. Then "
            + repr(spaced)
            + " trimmed, followed by a bar. Then "
            + repr(joined)
            + " with every "
            + repr(from_)
            + " replaced by "
            + repr(to)
            + ".",
            {
                "short": short,
                "width": width,
                "filler": filler,
                "name": name,
                "wide": wide,
                "dots": dots,
                "spaced": spaced,
                "joined": joined,
                "from_": from_,
                "to": to,
            },
        )
        for short, width, filler, name, wide, dots, spaced, joined, from_, to in _PADS
    ],
)


# ── 115. Union and overlap, written by hand ──────────────────

_SETS = (
    ((1, 2, 3), (3, 4), 2),
    ((5, 6), (6, 7, 8), 5),
    ((1, 2, 3, 4), (2, 4), 3),
    ((10, 20), (20, 30), 10),
    ((7, 8, 9), (9,), 8),
    ((2, 4, 6), (4, 8), 6),
    ((11, 12), (12, 13), 11),
    ((1, 3, 5), (5, 7), 3),
    ((100, 200), (200, 300), 100),
    ((21, 22, 23), (22,), 23),
    ((3, 6, 9), (6, 12), 9),
    ((15, 25), (25, 35), 15),
)

_P115 = _page(
    "js-set-ops",
    115,
    "Union and overlap, written by hand",
    "Spreading two Sets together, and filtering with has.",
    "JavaScript's Set has no union or intersection method, which is a "
    "genuine gap - so you build them. Spreading both into a new Set "
    "gives the union, because the Set drops the duplicates on the way "
    "in. The overlap is a filter using has, which is fast because that "
    "is what a Set is for; the same filter against an array would search "
    "it every time. Newer runtimes are adding real union and "
    "intersection methods, and this is what they will replace.",
    "js_set_ops",
    [
        (
            "Set first to a new Set of ["
            + _seq(one)
            + "] and second to a new Set of ["
            + _seq(two)
            + "]. Make union by spreading both into a new Set, and shared "
            "by filtering first's items for the ones second has. Log the "
            "union spread and joined with ', ', then shared joined, then "
            "whether first has "
            + str(looked_for)
            + ".",
            {"first": one, "second": two, "looked_for": looked_for},
        )
        for one, two, looked_for in _SETS
    ],
)


# ── 116. A date, and the month that counts from zero ─────────

_DATES = (
    (2026, 8, 2),
    (2026, 0, 1),
    (1977, 0, 14),
    (1985, 7, 16),
    (2000, 11, 31),
    (1969, 6, 20),
    (2026, 2, 15),
    (2024, 1, 29),
    (2010, 10, 11),
    (1990, 5, 5),
    (2026, 11, 25),
    (2026, 3, 10),
)

_P116 = _page(
    "js-date",
    116,
    "A date, and the month that counts from zero",
    "Date.UTC, toISOString, and the month nobody expects.",
    "The month is zero-based going in and coming out: month 8 is "
    "September, and getUTCMonth on a September date gives 8. The day is "
    "one-based. Nobody has ever found this reasonable and it is never "
    "going to change. Two other habits worth taking: build dates with "
    "Date.UTC rather than the local constructor, so the machine's time "
    "zone cannot move the answer, and use toISOString for anything "
    "stored or compared.",
    "js_date",
    [
        (
            "Set when to a new Date from Date.UTC of "
            + str(year)
            + ", "
            + str(month)
            + " and "
            + str(day)
            + ", const. Log its toISOString, then its UTC full year, then "
            "its UTC month, then its UTC date.",
            {"when": (year, month, day)},
        )
        for year, month, day in _DATES
    ],
)


# ── 117. An error type of your own ───────────────────────────

_ERRORS = (
    ("NotFound", "no such thing"),
    ("BadInput", "that will not do"),
    ("Timeout", "took too long"),
    ("Refused", "not allowed"),
    ("Missing", "nothing there"),
    ("TooLarge", "over the limit"),
    ("Conflict", "already exists"),
    ("Unreadable", "cannot parse that"),
    ("Empty", "nothing to do"),
    ("Locked", "someone else has it"),
    ("Expired", "past its date"),
    ("Unknown", "no idea what that is"),
)

_P117 = _page(
    "js-error-class",
    117,
    "An error type of your own",
    "extends Error, setting name, and instanceof.",
    "Since there is no way to catch one type as page 94 noted, catching "
    "means checking - and instanceof is how. Extending Error gives you a "
    "stack trace for free; setting this.name in the constructor is the "
    "part people forget, and without it the error prints as a plain "
    "Error and is that much harder to spot in a log. Note both "
    "instanceof checks are true: your error is a NotFound and also an "
    "Error, which is what lets a caller be as specific as it likes.",
    "js_error_class",
    [
        (
            "Write a class "
            + cls
            + " extending Error, whose constructor passes message to "
            "super and sets this.name to "
            + repr(cls)
            + ". In a try, throw a new one with "
            + repr(message)
            + ". Catch it and log the message, then the name, then "
            "whether it is an instance of "
            + cls
            + ", then whether it is an instance of Error.",
            {"cls": cls, "message": message},
        )
        for cls, message in _ERRORS
    ],
)


# ── 118. Promises chained, and the catch at the end ──────────

_PROMISES = (
    ("n * 2", 5, "n + 1", "stopped"),
    ("n * 3", 4, "n + 2", "gave up"),
    ("n + 10", 1, "n * 2", "failed"),
    ("n * n", 3, "n - 1", "broken"),
    ("n * 5", 2, "n + 5", "halted"),
    ("n + 100", 7, "n * 2", "no good"),
    ("n * 4", 6, "n + 3", "aborted"),
    ("n - 1", 20, "n * 3", "cancelled"),
    ("n * 10", 8, "n + 7", "stopped"),
    ("n + n", 9, "n * 2", "refused"),
    ("n * 7", 3, "n - 2", "ended"),
    ("n + 50", 5, "n * 2", "quit"),
)

_P118 = _page(
    "js-promise-then",
    118,
    "Promises chained, and the catch at the end",
    "then returning a value, and one catch for the whole chain.",
    "Whatever a then returns becomes the value the next then receives, "
    "so a chain is a pipeline. Return a promise and the chain waits for "
    "it, which is why the rejection here stops everything after it. One "
    "catch at the end covers every step before it - and a step that "
    "forgets to return leaves the next one with undefined, which is the "
    "commonest mistake in this style. async and await from page 93 are "
    "this same machinery written to read like ordinary code.",
    "js_promise_then",
    [
        (
            "Write work(n) returning a resolved promise of "
            + expr
            + ". Call it with "
            + str(start)
            + ", then a then returning "
            + next_step
            + ", then a then that logs its value and returns it, then a "
            "then returning a rejected promise with an Error "
            + repr(stopped)
            + ", then a catch logging the problem's message.",
            {
                "expr": expr,
                "start": start,
                "next": next_step,
                "stopped": stopped,
            },
        )
        for expr, start, next_step, stopped in _PROMISES
    ],
)


# ── 119. Making an array out of something else ───────────────

_FROMS = (
    ("abc", 4, "i * 2", 7),
    ("hello", 3, "i + 1", 9),
    ("code", 5, "i * i", 1),
    ("map", 4, "i * 10", 42),
    ("set", 3, "i + 5", 3),
    ("node", 6, "i * 3", 8),
    ("red", 4, "i * i * i", 12),
    ("blue", 5, "i + 100", 6),
    ("sky", 3, "i * 7", 5),
    ("iron", 4, "i + i", 11),
    ("gold", 5, "i * 4", 2),
    ("lake", 3, "i * 9", 21),
)

_P119 = _page(
    "js-array-from",
    119,
    "Making an array out of something else",
    "Array.from with a string and with a length, and Array.of.",
    "Array.from turns anything iterable into a real array - a string "
    "into its characters, a Set or a Map into a list, a NodeList in a "
    "browser into something you can map over. The second form is the "
    "useful trick: an object with just a length, plus a function, builds "
    "a numbered array of any size, which is JavaScript's nearest thing "
    "to a range. Array.of exists because Array(7) makes a seven-hole "
    "array rather than an array holding 7.",
    "js_array_from",
    [
        (
            "Log Array.from of "
            + repr(word)
            + " joined with ', '. Then Array.from of an object with "
            "length "
            + str(count)
            + " and a function taking an ignored first argument and i, "
            "returning "
            + expr
            + ", joined. Then the length of Array.of("
            + str(one)
            + ").",
            {"word": word, "count": count, "expr": expr, "one": one},
        )
        for word, count, expr, one in _FROMS
    ],
)


# ── 120. Assigning only when you need to ─────────────────────

_ASSIGNS = (
    (5, 3),
    (10, 7),
    (1, 9),
    (100, 2),
    (42, 8),
    (7, 4),
    (99, 6),
    (25, 5),
    (50, 11),
    (3, 12),
    (64, 1),
    (8, 20),
)

_P120 = _page(
    "js-logical-assign",
    120,
    "Assigning only when you need to",
    "??=, ||= and &&=, and the zero that tells them apart.",
    "??= assigns only when the current value is null or undefined. ||= "
    "assigns whenever the current value is falsy, which includes zero "
    "and the empty string. The second and third lines here start from "
    "the same 0 and end up different, which is the entire point: reach "
    "for ??= when zero is a real value, and ||= only when any falsy "
    "value should be replaced. &&= is the other way round, assigning "
    "only when there is already something there - useful for updating a "
    "value that may not exist yet without creating it.",
    "js_logical_assign",
    [
        (
            "Set missing to null with let and use ??= to give it "
            + str(fallback)
            + ". Set zero to 0 and use ??= with the same value. Set empty "
            "to 0 and use ||= with it. Set held to "
            + str(held)
            + " and use &&= to give it "
            + str(replacement)
            + ". Log all four in that order.",
            {
                "fallback": fallback,
                "held": held,
                "replacement": replacement,
            },
        )
        for fallback, replacement in _ASSIGNS
        for held in (fallback + replacement,)
    ],
)


JS_PAGES_4: tuple[Page, ...] = (
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
