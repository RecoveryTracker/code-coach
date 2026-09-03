"""Intermediate pages 279-288: precision, parsing and the rest of the toolkit.

Named groups and a lookahead, the two regex features worth knowing past
page 149. strptime, for text that has to become a date. calendar.
Decimal's quantize, which is the only honest way to round money. json
with a default for the types it does not know. Writing csv. More of
pathlib. Four more itertools. And the dataclass that makes you name your
arguments.

Python only, same as 81-278.
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


# ── 279. Capture groups with names ───────────────────────────

_NAMED = (
    ("ada:36", "name", "age", ":"),
    ("sam:41", "who", "years", ":"),
    ("kyoto=1463", "city", "people", "="),
    ("oslo=709", "place", "count", "="),
    ("iron-26", "metal", "number", "-"),
    ("gold-79", "element", "atomic", "-"),
    ("dune#412", "book", "pages", "#"),
    ("alive#245", "song", "seconds", "#"),
    ("reds/41", "team", "points", "/"),
    ("saw/3", "tool", "weight", "/"),
    ("sky|3", "word", "length", r"\|"),
    ("north|120", "trip", "miles", r"\|"),
)

_P279 = _page(
    "regex-named",
    279,
    "Capture groups with names",
    "(?P<name>...), groupdict, and re.compile.",
    "Page 150 pulled pieces out by number, which works until you add a "
    "group in the middle and every number shifts. Naming them fixes "
    "that, and groupdict hands the whole lot back as a dict ready to "
    "use. The other habit here is re.compile: a pattern you use more "
    "than once should be compiled once, both because it is faster and "
    "because it gives the pattern a name at the top of the file instead "
    "of burying it in a call.",
    "regex_named",
    [
        (
            "Import re. Compile a raw-string pattern with a named group "
            + repr(first)
            + " of word characters, then "
            + gap.replace("\\", "")
            + ", then a named group "
            + repr(second)
            + " of digits. Search "
            + repr(text)
            + " with it into found, then print the two groups by name and "
            "found.groupdict().",
            {"text": text, "first": first, "second": second, "gap": gap},
        )
        for text, first, second, gap in _NAMED
    ],
)


# ── 280. Matching only when something follows ────────────────

_LOOKAHEADS = (
    ("50 dollars and 20 pounds", "dollars"),
    ("30 miles and 12 hours", "miles"),
    ("15 apples and 9 pears", "apples"),
    ("8 metres and 4 feet", "metres"),
    ("100 grams and 7 ounces", "grams"),
    ("60 minutes and 24 hours", "minutes"),
    ("12 pages and 3 chapters", "pages"),
    ("45 pence and 2 pounds", "pence"),
    ("18 degrees and 5 knots", "degrees"),
    ("90 seconds and 6 rounds", "seconds"),
    ("25 litres and 11 gallons", "litres"),
    ("40 words and 3 lines", "words"),
)

_P280 = _page(
    "regex-lookahead",
    280,
    "Matching only when something follows",
    "A lookahead, which checks without consuming.",
    "(?= ...) says what must come next without making it part of the "
    "match - so the number is found only when the right word follows it, "
    "and the word itself is not returned. Each line here has two numbers "
    "and only one comes back. This is how you match a thing by its "
    "context rather than its own shape, which is most of what makes "
    "regular expressions worth the trouble. There is a negative form "
    "too, (?! ...), for what must not follow.",
    "regex_lookahead",
    [
        (
            "Import re. Compile a raw-string pattern of one or more "
            "digits followed by a lookahead for a space and "
            + repr(unit)
            + ". Print its findall over "
            + repr(text)
            + ".",
            {"text": text, "unit": unit},
        )
        for text, unit in _LOOKAHEADS
    ],
)


# ── 281. Text turned into a date ─────────────────────────────

_PARSES = (
    ("2026-09-02", "%Y-%m-%d", "%d/%m/%Y"),
    ("2026-01-01", "%Y-%m-%d", "%d/%m/%Y"),
    ("02/09/2026", "%d/%m/%Y", "%Y-%m-%d"),
    ("14/01/1977", "%d/%m/%Y", "%Y-%m-%d"),
    ("1985-08-16", "%Y-%m-%d", "%d-%m-%Y"),
    ("20261225", "%Y%m%d", "%d/%m/%Y"),
    ("19690720", "%Y%m%d", "%Y-%m-%d"),
    ("03-15-2026", "%m-%d-%Y", "%Y-%m-%d"),
    ("12-31-2000", "%m-%d-%Y", "%d/%m/%Y"),
    ("2024.02.29", "%Y.%m.%d", "%d/%m/%Y"),
    ("2010.11.11", "%Y.%m.%d", "%Y-%m-%d"),
    ("05/11/2026", "%d/%m/%Y", "%Y%m%d"),
)

_P281 = _page(
    "strptime-use",
    281,
    "Text turned into a date",
    "strptime, which is strftime backwards.",
    "strftime turns a date into text; strptime turns text into a date, "
    "using the same pattern language. Getting the pattern wrong raises "
    "rather than guessing, which is what you want - a date library that "
    "guesses will read 03/04 as March in one place and April in another. "
    "Two of these read an American month-first format and print it back "
    "the other way round, which is the entire argument for storing dates "
    "in ISO form and formatting only at the edges.",
    "strptime_use",
    [
        (
            "Import datetime from datetime. Set text to "
            + repr(text)
            + " and when to strptime of it with "
            + repr(reads)
            + ". Print when.year, then strftime with "
            + repr(shows)
            + ", then the isoformat of its date.",
            {"text": text, "reads": reads, "shows": shows},
        )
        for text, reads, shows in _PARSES
    ],
)


# ── 282. How long a month is ─────────────────────────────────

_CALENDARS = (
    (2026, 9, 2, 2024),
    (2026, 2, 14, 2024),
    (2024, 2, 29, 2024),
    (2025, 2, 28, 2025),
    (2026, 1, 1, 2000),
    (2026, 12, 25, 1900),
    (2000, 2, 15, 2000),
    (1900, 2, 15, 1900),
    (2026, 4, 30, 2028),
    (2026, 6, 15, 2100),
    (1977, 1, 14, 1976),
    (1985, 8, 16, 1984),
)

_P282 = _page(
    "calendar-use",
    282,
    "How long a month is",
    "calendar.monthrange, isleap and weekday.",
    "monthrange hands back two numbers: which weekday the month starts "
    "on, and how many days it has - so you never write the thirty-days-"
    "hath-September table again. isleap knows the real rule, which is "
    "not simply every four years: 2000 was a leap year and 1900 was not, "
    "and two of these pages check exactly that. weekday counts from 0 "
    "for Monday, which is worth remembering because other systems start "
    "on Sunday.",
    "calendar_use",
    [
        (
            "Import calendar. Print monthrange of "
            + str(year)
            + " and "
            + str(month)
            + ", then isleap of "
            + str(leap_year)
            + ", then weekday of "
            + str(year)
            + ", "
            + str(month)
            + " and "
            + str(day)
            + ".",
            {
                "year": year,
                "month": month,
                "day": day,
                "leap_year": leap_year,
            },
        )
        for year, month, day, leap_year in _CALENDARS
    ],
)


# ── 283. Rounding money the way you meant ────────────────────

# Every value has an even digit before the trailing 5, so half-even
# rounds down and half-up rounds up. The emitter raises if a value is
# chosen where the two rules agree.
_QUANTIZE = (
    "2.665",
    "1.225",
    "3.445",
    "0.005",
    "5.885",
    "7.205",
    "9.065",
    "4.425",
    "6.845",
    "2.025",
    "8.605",
    "1.445",
)

_P283 = _page(
    "decimal-quantize",
    283,
    "Rounding money the way you meant",
    "quantize, and choosing the rounding rule out loud.",
    "Page 219 showed round doing half-to-even, and page 190 showed "
    "Decimal keeping the digits you wrote. Together they give the honest "
    "answer for money: quantize to two places and say which rule you "
    "want. The first line here is half-to-even and the second is "
    "half-up, and they differ on every value on this page. Now watch the "
    "third line, which rounds the plain float. It matches the first on "
    "half of these pages and the second on the other half, and you "
    "cannot tell which from looking at the digits - because the float "
    "was never exactly the number you typed, so it falls on whichever "
    "side of the halfway point the binary approximation happens to "
    "land. That unpredictability, not the rounding rule, is the reason "
    "money uses Decimal.",
    "decimal_quantize",
    [
        (
            "Import ROUND_HALF_UP and Decimal from decimal. Set value to "
            "Decimal of "
            + repr(text)
            + ". Print it quantized to Decimal('0.01'), then quantized "
            "again with rounding=ROUND_HALF_UP, then round of the plain "
            "float "
            + text
            + " to 2 places.",
            {"value": text},
        )
        for text in _QUANTIZE
    ],
)


# ── 284. Encoding a type json does not know ──────────────────

_ENCODES = (
    ((2026, 9, 2), "name", "ada", "cannot encode that"),
    ((2026, 1, 1), "who", "sam", "unknown type"),
    ((1977, 1, 14), "artist", "bowie", "cannot encode that"),
    ((1985, 8, 16), "singer", "kate", "unknown type"),
    ((2000, 12, 31), "label", "millennium", "not serialisable"),
    ((1969, 7, 20), "event", "landing", "cannot encode that"),
    ((2024, 2, 29), "note", "leap day", "unknown type"),
    ((2026, 3, 15), "city", "kyoto", "not serialisable"),
    ((2026, 12, 25), "holiday", "christmas", "cannot encode that"),
    ((2010, 11, 11), "code", "eleven", "unknown type"),
    ((1990, 6, 5), "place", "oslo", "not serialisable"),
    ((2026, 4, 10), "task", "review", "cannot encode that"),
)

_P284 = _page(
    "json-default",
    284,
    "Encoding a type json does not know",
    "json.dumps with default, for everything that is not a basic type.",
    "json knows dicts, lists, strings, numbers, booleans and None, and "
    "raises on anything else - a date, a Decimal, one of your own "
    "objects. The default argument is a function it calls for whatever "
    "it cannot handle, so you decide the representation. Note the raise "
    "at the end of the function: without it, a type you did not think "
    "about returns None and lands silently in the output, which is worse "
    "than the error.",
    "json_default",
    [
        (
            "Import json and date from datetime. Write encode(value) "
            "returning value.isoformat() when isinstance says it is a "
            "date, and otherwise raising TypeError "
            + repr(complaint)
            + ". Set data to a dict with 'when' as date("
            + ", ".join(str(n) for n in when)
            + ") and "
            + repr(key)
            + " as "
            + repr(name)
            + ", then print json.dumps of it with default=encode and "
            "sort_keys=True.",
            {"when": when, "key": key, "name": name, "complaint": complaint},
        )
        for when, key, name, complaint in _ENCODES
    ],
)


# ── 285. Writing a table out ─────────────────────────────────

_WRITES = (
    (("name", "ada"), ("score", 90)),
    (("city", "kyoto"), ("people", 1463)),
    (("metal", "iron"), ("number", 26)),
    (("book", "dune"), ("pages", 412)),
    (("song", "alive"), ("seconds", 245)),
    (("team", "reds"), ("points", 41)),
    (("tool", "saw"), ("weight", 3)),
    (("room", "attic"), ("floor", 4)),
    (("word", "sky"), ("length", 3)),
    (("trip", "north"), ("miles", 120)),
    (("task", "mix"), ("order", 2)),
    (("user", "sam"), ("age", 41)),
)

_P285 = _page(
    "csv-write",
    285,
    "Writing a table out",
    "csv.DictWriter, and the line terminator worth setting.",
    "DictWriter is the other half of page 193: give it the field names "
    "and hand it dicts, and it writes the header and quotes anything "
    "that needs it. One detail bites everyone: csv writes \\r\\n by "
    "default, because that is what the format says, and on a machine "
    "that already ends lines with \\n you get a blank line between every "
    "row. Setting lineterminator, or opening the file with newline='', "
    "is the fix.",
    "csv_write",
    [
        (
            "Import csv and io. Make buffer an io.StringIO and writer a "
            "DictWriter over it with fieldnames "
            + " and ".join(repr(k) for k, _ in row)
            + " and lineterminator of a newline. Write the header, then "
            "the row "
            + ", ".join(f"{k!r}: {v!r}" for k, v in row)
            + ", then print the buffer's value stripped.",
            {"row": row},
        )
        for row in _WRITES
    ],
)


# ── 286. A path's pieces, suffix and relative form ───────────

_MOREPATHS = (
    ("home/ada/notes.txt", ".md", "home"),
    ("home/sam/report.pdf", ".txt", "home"),
    ("work/code/main.py", ".pyi", "work"),
    ("var/log/api.log", ".old", "var"),
    ("music/bowie/heroes.mp3", ".flac", "music"),
    ("photos/2026/trip.jpg", ".png", "photos"),
    ("docs/letters/bank.docx", ".pdf", "docs"),
    ("data/raw/readings.csv", ".json", "data"),
    ("src/tests/test_all.py", ".bak", "src"),
    ("site/static/style.css", ".scss", "site"),
    ("build/dist/app.zip", ".tar", "build"),
    ("backup/monday/dump.sql", ".gz", "backup"),
)

_P286 = _page(
    "path-parts-more",
    286,
    "A path's pieces, suffix and relative form",
    "with_suffix, parts and relative_to.",
    "with_suffix swaps the extension without any string surgery, and it "
    "handles the no-extension case correctly, which the obvious "
    "split-on-a-dot does not. parts gives every segment as a tuple, "
    "which is how you look at a path structurally rather than by "
    "counting slashes. relative_to strips a known prefix and raises if "
    "the path is not under it - a check worth having when a filename "
    "came from outside your program.",
    "path_parts_more",
    [
        (
            "Import Path from pathlib. Set path to Path of "
            + repr(text)
            + ". Print the name of it with the suffix changed to "
            + repr(suffix)
            + ", then its parts, then it relative to "
            + repr(root)
            + ".",
            {"path": text, "suffix": suffix, "root": root},
        )
        for text, suffix, root in _MOREPATHS
    ],
)


# ── 287. count, compress and filterfalse ─────────────────────

_MORE_ITER = (
    (10, 5, 4, "abcd", (1, 0, 1, 0), (1, 2, 3, 4), "n % 2"),
    (0, 3, 5, "hello", (1, 1, 0, 0, 1), (1, 2, 3, 4, 5), "n > 2"),
    (100, 10, 3, "abc", (0, 1, 1), (10, 15, 20), "n % 5 == 0"),
    (1, 1, 6, "python", (1, 0, 1, 0, 1, 0), (2, 4, 6, 7), "n % 2 == 0"),
    (7, 7, 4, "code", (1, 1, 0, 1), (1, 3, 5, 8), "n % 2"),
    (50, 25, 3, "red", (0, 1, 0), (5, 10, 15), "n > 7"),
    (2, 2, 5, "north", (1, 0, 0, 1, 1), (1, 2, 3, 4, 5), "n < 3"),
    (0, 100, 4, "gold", (1, 1, 1, 0), (12, 15, 18), "n % 3 == 0"),
    (9, 9, 3, "sky", (0, 0, 1), (7, 14, 21), "n % 7 == 0"),
    (5, 5, 5, "salt", (1, 0, 1, 1), (2, 3, 4, 5), "n % 2 == 1"),
    (1000, 500, 3, "iron", (1, 1, 0, 0), (6, 12, 18), "n > 10"),
    (3, 4, 4, "left", (0, 1, 1, 0), (1, 4, 9, 16), "n < 5"),
)

_P287 = _page(
    "itertools-more",
    287,
    "count, compress and filterfalse",
    "Three more from itertools, and what each replaces.",
    "count is an endless range with a start and a step, so it needs "
    "islice around it exactly as cycle did on page 211. compress picks "
    "items using a second sequence of yes-or-no values, which is what "
    "you want when the decision was already made somewhere else. "
    "filterfalse is filter with the test inverted, so you can keep the "
    "condition readable rather than writing not in front of it.",
    "itertools_more",
    [
        (
            "Import compress, count, filterfalse and islice from "
            "itertools. Print the list of islice over count from "
            + str(start)
            + " by "
            + str(step)
            + ", taking "
            + str(take)
            + ". Then the list of compress over "
            + repr(letters)
            + " with ["
            + ", ".join(str(n) for n in picks)
            + "]. Then the list of filterfalse with a lambda testing "
            + test
            + " over ["
            + _seq(numbers)
            + "].",
            {
                "start": start,
                "step": step,
                "take": take,
                "letters": letters,
                "picks": picks,
                "numbers": numbers,
                "test": test,
            },
        )
        for start, step, take, letters, picks, numbers, test in _MORE_ITER
    ],
)


# ── 288. Arguments that must be named ────────────────────────

_KWONLY = (
    ("Point", "x", "y", 0, 2, 5, "y must be named"),
    ("Size", "width", "height", 1, 10, 4, "height must be named"),
    ("Span", "low", "high", 0, 3, 17, "high must be named"),
    ("Score", "points", "bonus", 0, 40, 7, "bonus must be named"),
    ("Room", "floor", "number", 1, 3, 12, "number must be named"),
    ("Trip", "miles", "hours", 1, 120, 3, "hours must be named"),
    ("Grid", "rows", "cols", 1, 8, 9, "cols must be named"),
    ("Tank", "full", "used", 0, 60, 22, "used must be named"),
    ("Bill", "price", "people", 1, 45, 3, "people must be named"),
    ("Wall", "bricks", "rows", 1, 90, 6, "rows must be named"),
    ("Gap", "start", "end", 0, 7, 31, "end must be named"),
    ("Pair", "left", "right", 0, 7, 8, "right must be named"),
)

_P288 = _page(
    "dataclass-kwonly",
    288,
    "Arguments that must be named",
    "KW_ONLY, and slots on a dataclass.",
    "A field after KW_ONLY can only be passed by name, which stops "
    "Thing(2, 5) - two bare numbers whose meaning nobody can read at the "
    "call site, and which silently swap if anyone reorders the fields. "
    "Making them named is a small unkindness that buys real safety on "
    "anything with more than two arguments. slots=True is the dataclass "
    "form of page 231, and comes almost free while you are here.",
    "dataclass_kwonly",
    [
        (
            "Import KW_ONLY and dataclass from dataclasses. Write a "
            "dataclass "
            + cls
            + " with slots=True, "
            + first
            + " hinted int, then _ hinted KW_ONLY, then "
            + second
            + " hinted int defaulting to "
            + repr(fallback)
            + ". Make thing with "
            + repr(given)
            + " and "
            + second
            + "="
            + repr(named)
            + ", and print it. Then in a try build it with two bare "
            "numbers, catching TypeError and printing "
            + repr(complaint)
            + ".",
            {
                "cls": cls,
                "first": first,
                "second": second,
                "fallback": fallback,
                "given": given,
                "named": named,
                "complaint": complaint,
            },
        )
        for cls, first, second, fallback, given, named, complaint in _KWONLY
    ],
)


PRECISION_PAGES: tuple[Page, ...] = (
    _P279,
    _P280,
    _P281,
    _P282,
    _P283,
    _P284,
    _P285,
    _P286,
    _P287,
    _P288,
)
