"""Intermediate pages 229-238: the standard library you reach for at work.

Ten modules that already contain the thing you were about to write.
Logging instead of print, argparse instead of picking through sys.argv,
__slots__ for the class you make a million of, singledispatch instead of
a chain of isinstance, attrgetter, and then statistics, Fraction,
hashlib, urllib.parse and textwrap.

The habit worth taking from the block is smaller than any of them:
before writing a helper, spend one minute checking whether Python
already ships it. It usually does, and its version has had twenty years
of edge cases reported against it.

Python only, same as 81-228.
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


# ── 229. Saying it properly instead of printing it ───────────

_LOGS = (
    ("started up", "disk is filling", "loop ran once"),
    ("connected", "retrying", "packet sent"),
    ("loaded config", "missing key, using default", "parsed line"),
    ("server ready", "slow response", "handled request"),
    ("job queued", "queue is long", "checked queue"),
    ("file opened", "file is large", "read a chunk"),
    ("user signed in", "password is old", "checked session"),
    ("backup begun", "little space left", "copied a file"),
    ("cache warmed", "cache nearly full", "stored an entry"),
    ("import done", "two rows skipped", "read a row"),
    ("listening", "port was busy", "accepted socket"),
    ("shutting down", "work still pending", "closed a handle"),
)

_P229 = _page(
    "logging-use",
    229,
    "Saying it properly instead of printing it",
    "logging, levels, and the one that does not appear.",
    "print has one volume and no way to turn it down. logging gives "
    "every message a level, and setting the level decides which ones "
    "come out - so the same code is quiet in production and talkative "
    "when you are hunting something. The third line of each is a debug "
    "message and it never prints, because the level is INFO. That is not "
    "a bug in your program; it is the whole point. Note the format "
    "string: real logs want a timestamp too.",
    "logging_use",
    [
        (
            "Import logging and sys. Call logging.basicConfig with "
            "stream=sys.stdout, level=logging.INFO and format "
            "'%(levelname)s %(message)s'. Then log info "
            + repr(info)
            + ", warning "
            + repr(warning)
            + ", and debug "
            + repr(debug)
            + " - and notice which one does not appear.",
            {"info": info, "warning": warning, "debug": debug},
        )
        for info, warning, debug in _LOGS
    ],
)


# ── 230. Arguments read for you ──────────────────────────────

_ARGS = (
    ("count", 1, "5", "name", "world"),
    ("size", 10, "42", "label", "default"),
    ("port", 8080, "9000", "host", "localhost"),
    ("retries", 3, "7", "mode", "safe"),
    ("workers", 2, "8", "queue", "main"),
    ("depth", 1, "4", "style", "plain"),
    ("limit", 100, "250", "sort", "name"),
    ("width", 80, "120", "align", "left"),
    ("tries", 5, "2", "level", "info"),
    ("rows", 20, "50", "format", "csv"),
    ("timeout", 30, "60", "scheme", "https"),
    ("skip", 0, "3", "target", "all"),
)

_P230 = _page(
    "argparse-use",
    230,
    "Arguments read for you",
    "argparse, defaults, and parsing a list you supply.",
    "argparse turns a command line into an object with attributes, "
    "converts types, fills in defaults and writes the --help text for "
    "free. The trick used here is worth keeping: parse_args accepts a "
    "list, so you can hand it arguments directly instead of reading the "
    "real command line - which is exactly how you test a program's "
    "argument handling without running it as a program. Only one flag is "
    "given, so the other comes back as its default.",
    "argparse_use",
    [
        (
            "Import argparse. Make a parser, add --"
            + flag
            + " with type=int and default "
            + repr(fallback)
            + ", and add --"
            + word
            + " with default "
            + repr(default)
            + ". Parse the list ['--"
            + flag
            + "', "
            + repr(given)
            + "], then print args."
            + flag
            + " and args."
            + word
            + ".",
            {
                "flag": flag,
                "fallback": fallback,
                "given": given,
                "word": word,
                "default": default,
            },
        )
        for flag, fallback, given, word, default in _ARGS
    ],
)


# ── 231. A class told exactly what it may hold ───────────────

_SLOTS = (
    ("Point", ("x", "y"), (2, 3), "z", "no such attribute"),
    ("Size", ("width", "height"), (10, 4), "depth", "refused"),
    ("Pair", ("left", "right"), (7, 8), "middle", "not allowed"),
    ("Card", ("suit", "rank"), ("spades", 11), "colour", "no such attribute"),
    ("Room", ("floor", "number"), (3, 12), "wing", "refused"),
    ("Span", ("low", "high"), (3, 17), "step", "not allowed"),
    ("Coin", ("face", "worth"), ("heads", 25), "year", "no such attribute"),
    ("Node", ("value", "next_id"), (5, 6), "prev", "refused"),
    ("Grid", ("rows", "cols"), (8, 9), "layers", "not allowed"),
    ("Trip", ("miles", "hours"), (120, 3), "stops", "no such attribute"),
    ("Score", ("points", "bonus"), (40, 7), "penalty", "refused"),
    ("Tank", ("full", "used"), (60, 22), "spare", "not allowed"),
)

_P231 = _page(
    "slots-use",
    231,
    "A class told exactly what it may hold",
    "__slots__, and the attribute it will not let you add.",
    "Normally every object carries a dict of its attributes, which is "
    "why you can bolt a new one on at any time. __slots__ says these are "
    "the only ones: no dict, less memory, faster access, and a typo in "
    "an attribute name becomes an AttributeError instead of a silent new "
    "field - which is the reason to use it even when memory is no "
    "object. The cost is that you cannot add attributes later, and "
    "inheritance gets fiddly. Worth it for the small class you make "
    "millions of.",
    "slots_use",
    [
        (
            "Write a class "
            + cls
            + " with __slots__ of "
            + " and ".join(repr(f) for f in fields)
            + ", and an __init__ storing both. Make thing holding "
            + _seq(values)
            + " and print its "
            + fields[0]
            + ". Then in a try set thing."
            + extra
            + " to 1, catching AttributeError and printing "
            + repr(refused)
            + ".",
            {
                "cls": cls,
                "fields": fields,
                "values": values,
                "extra": extra,
                "refused": refused,
            },
        )
        for cls, fields, values, extra, refused in _SLOTS
    ],
)


# ── 232. One name, different work per type ───────────────────

_DISPATCH = (
    ("describe", "number", "word", 5, "hello", 2.5, "something else"),
    ("show", "int of", "text", 42, "world", 1.5, "no idea"),
    ("render", "counted", "spelled", 7, "seven", 0.5, "unknown"),
    ("label", "digit", "letter", 3, "three", 3.5, "other"),
    ("name_it", "whole", "string", 100, "hundred", 9.5, "not sure"),
    ("tell", "value", "phrase", 1, "one", 4.5, "who knows"),
    ("report", "amount", "note", 12, "twelve", 6.5, "anything else"),
    ("say", "count", "name", 9, "nine", 8.5, "unknown"),
    ("print_it", "integer", "characters", 21, "twentyone", 2.25, "other"),
    ("give", "quantity", "label", 6, "six", 7.75, "no match"),
    ("read", "figure", "word", 15, "fifteen", 5.25, "unhandled"),
    ("check", "number", "text", 33, "thirty", 1.25, "something else"),
)

_P232 = _page(
    "singledispatch-use",
    232,
    "One name, different work per type",
    "functools.singledispatch, instead of a chain of isinstance.",
    "The usual version of this is a function that starts with three ifs "
    "asking isinstance, and grows an if every time a type is added. "
    "singledispatch turns that inside out: the base function is the "
    "fallback, and each type registers its own version - so adding a "
    "type adds code instead of editing code. Note the registered "
    "functions are all called _, because their names never matter; the "
    "hint on the argument is what does the choosing.",
    "singledispatch_use",
    [
        (
            "Import singledispatch from functools. Write "
            + name
            + "(value) decorated with it, returning "
            + repr(fallback)
            + ". Register a version for int returning an f-string of "
            + repr(int_word)
            + " and the value, and one for str the same with "
            + repr(str_word)
            + ". Print it called with "
            + repr(number)
            + ", then "
            + repr(word)
            + ", then "
            + repr(other)
            + ".",
            {
                "name": name,
                "int_word": int_word,
                "str_word": str_word,
                "number": number,
                "word": word,
                "other": other,
                "fallback": fallback,
            },
        )
        for name, int_word, str_word, number, word, other, fallback in _DISPATCH
    ],
)


# ── 233. Sorting by an attribute, plainly ────────────────────

_ATTRS = (
    ("Player", "score", (("ada", 90), ("sam", 7), ("kim", 41))),
    ("City", "people", (("kyoto", 1463), ("oslo", 709), ("lima", 998))),
    ("Book", "pages", (("dune", 412), ("ilium", 780), ("solaris", 204))),
    ("Song", "seconds", (("alive", 245), ("heroes", 371), ("kooks", 173))),
    ("Metal", "number", (("iron", 26), ("gold", 79), ("tin", 50))),
    ("Room", "floor", (("attic", 4), ("cellar", 0), ("hall", 1))),
    ("Tool", "weight", (("saw", 3), ("axe", 8), ("file", 1))),
    ("Fruit", "count", (("apple", 3), ("pear", 12), ("fig", 7))),
    ("Task", "order", (("mix", 2), ("bake", 3), ("weigh", 1))),
    ("Team", "points", (("reds", 41), ("blues", 12), ("greens", 30))),
    ("Word", "length", (("sky", 3), ("mountain", 8), ("lake", 4))),
    ("Trip", "miles", (("north", 120), ("south", 40), ("east", 75))),
)

_P233 = _page(
    "attrgetter-use",
    233,
    "Sorting by an attribute, plainly",
    "operator.attrgetter, which is itemgetter for objects.",
    "Page 172 sorted tuples by position with itemgetter. This is the "
    "same idea for objects: attrgetter('score') is key=lambda thing: "
    "thing.score, said more directly. It also takes several names at "
    "once for a tuple key, and it understands dots, so "
    "attrgetter('home.city') reaches through. Its sibling methodcaller "
    "does the same for a method you want called on each item.",
    "attrgetter_use",
    [
        (
            "Import attrgetter from operator. Write a class "
            + cls
            + " storing name and "
            + field
            + ". Build a list of "
            + ", ".join(f"({n!r}, {v!r})" for n, v in rows)
            + " as "
            + cls
            + " objects, then loop over it sorted with "
            "key=attrgetter("
            + repr(field)
            + "), printing each name and "
            + field
            + ".",
            {"cls": cls, "field": field, "rows": rows},
        )
        for cls, field, rows in _ATTRS
    ],
)


# ── 234. Mean, median and the middle of things ───────────────

_STATS = (
    (2, 4, 4, 4, 5, 5, 7, 9),
    (1, 2, 2, 3, 4),
    (10, 20, 20, 30),
    (5, 5, 5, 9, 11),
    (3, 3, 6, 9, 9, 9),
    (1, 1, 2, 4),
    (7, 7, 8, 10, 13),
    (2, 2, 2, 6, 8),
    (4, 4, 8, 12, 12, 4),
    (1, 3, 3, 5, 8),
    (6, 6, 9, 15),
    (11, 11, 11, 22, 33),
)

_P234 = _page(
    "statistics-use",
    234,
    "Mean, median and the middle of things",
    "The statistics module, and three words that get muddled.",
    "The mean is the average you were taught, and one huge value drags "
    "it around. The median is the middle value once sorted, and does "
    "not - which is why incomes are reported as medians. The mode is the "
    "one that appears most. Python ships all three and a good deal more, "
    "so there is no reason to write sum divided by len again, and it "
    "will tell you when the answer is undefined instead of guessing.",
    "statistics_use",
    [
        (
            "Import statistics. Set numbers to ["
            + _seq(items)
            + "], then print the mean, the median and the mode of it.",
            {"items": items},
        )
        for items in _STATS
    ],
)


# ── 235. Thirds that stay thirds ─────────────────────────────

# Chosen because the float round-trip really does fail for these. Most
# fractions survive it - (1/3) * 3 == 1 is True, the error cancelling by
# luck - which is the point the page makes, and the emitter raises if a
# pair is picked that does not fail.
_FRACTIONS = (
    (15, 22),
    (13, 23),
    (7, 25),
    (14, 25),
    (15, 26),
    (15, 29),
    (29, 35),
    (21, 38),
    (25, 39),
    (31, 39),
    (7, 41),
    (14, 41),
)


_P235 = _page(
    "fraction-use",
    235,
    "Exactly a fraction, not nearly one",
    "Fraction, which keeps the top and bottom instead of a decimal.",
    "A Fraction holds the numerator and denominator as whole numbers and "
    "does the arithmetic exactly, so the first line of each is a clean "
    "whole number and the second is a fraction, not a decimal that "
    "nearly is one. The third line does the same round trip in floats "
    "and comes out False. Here is the part worth carrying: most "
    "fractions survive that trip. (1/3) * 3 == 1 is True, because the "
    "error happens to cancel. Every pair on this page was chosen because "
    "it does not, and you cannot tell which is which by looking - that "
    "unpredictability is the reason to use an exact type rather than to "
    "hope.",
    "fraction_use",
    [
        (
            "Import Fraction from fractions. Set third to Fraction("
            + str(top)
            + ", "
            + str(bottom)
            + "). Print it multiplied by "
            + str(bottom)
            + ", then added to another Fraction("
            + str(top)
            + ", "
            + str(bottom)
            + "), then whether float(third) times "
            + str(bottom)
            + " == "
            + str(top)
            + ".",
            {"top": top, "bottom": bottom},
        )
        for top, bottom in _FRACTIONS
    ],
)


# ── 236. A fingerprint of some text ──────────────────────────

_HASHES = (
    ("hello", 8),
    ("password", 8),
    ("code coach", 10),
    ("ada lovelace", 12),
    ("the quick fox", 8),
    ("workbook", 10),
    ("python", 6),
    ("checksum", 12),
    ("a very long sentence to hash", 8),
    ("kyoto", 10),
    ("2026", 6),
    ("fingerprint", 12),
)

_P236 = _page(
    "hashlib-use",
    236,
    "A fingerprint of some text",
    "hashlib.sha256, hexdigest, and what a hash is for.",
    "A hash turns any amount of data into a fixed-length fingerprint - "
    "sha256 always gives 64 hex characters, whether you hand it a word "
    "or a film. The same input always gives the same digest, which is "
    "the third line here, and that is what makes it useful for checking "
    "a file arrived intact. Note it takes bytes, not text, so you encode "
    "first, as page 186 did. One warning: storing passwords needs a "
    "slow, salted hash from a library built for it, never a bare sha256.",
    "hashlib_use",
    [
        (
            "Import hashlib. Set text to "
            + repr(text)
            + " and digest to the sha256 hexdigest of it encoded as "
            "utf-8. Print the length of digest, then its first "
            + str(show)
            + " characters, then whether hashing the same text again "
            "gives the same digest.",
            {"text": text, "show": show},
        )
        for text, show in _HASHES
    ],
)


# ── 237. A web address taken apart ───────────────────────────

_URLS = (
    "https://example.com/pages/one",
    "http://localhost:8765/api/workbook",
    "https://github.com/python/cpython",
    "https://docs.python.org/3/library/itertools.html",
    "http://127.0.0.1:5173/index.html",
    "https://news.site.org/2026/09/story",
    "ftp://files.example.net/pub/data",
    "https://api.example.com/v2/users",
    "http://example.co.uk/about/team",
    "https://cdn.example.com/assets/logo.png",
    "https://shop.example.com/cart/checkout",
    "http://blog.example.org/posts/first",
)

_P237 = _page(
    "urlparse-use",
    237,
    "A web address taken apart",
    "urlparse, and why you never split a URL yourself.",
    "A URL looks like it has an obvious structure right up until you "
    "meet a port, a username, a query string with a slash in it, or a "
    "fragment. urlparse knows all of the rules and hands back the pieces "
    "by name. The same module has urlencode for building query strings "
    "and quote for escaping - use them, because a URL you assembled with "
    "string joining will break on the first value containing a space or "
    "an ampersand.",
    "urlparse_use",
    [
        (
            "Import urlparse from urllib.parse. Set address to "
            + repr(url)
            + " and parts to urlparse of it, then print parts.scheme, "
            "parts.netloc and parts.path.",
            {"url": url},
        )
        for url in _URLS
    ],
)


# ── 238. Text laid out to a width ────────────────────────────

_WRAPS = (
    ("the quick brown fox jumps over the lazy dog", 20),
    ("a program that scatters scratch files is soon disliked", 24),
    ("never compare two floating point numbers with equals", 22),
    ("a path is a value and not a string you chop up", 18),
    ("read the output and check it says what you claimed", 20),
    ("the sort is not tidiness here, it is required", 16),
    ("write the message someone reading the log can act on", 26),
    ("every language with floats does exactly this", 18),
    ("bugs live at the edges and not in the middle", 15),
    ("printing a list uses repr and not str", 14),
    ("one small method and the built-ins start cooperating", 22),
    ("check whether Python already ships the thing", 17),
)

_P238 = _page(
    "textwrap-use",
    238,
    "Text laid out to a width",
    "textwrap.wrap, for output that has to fit.",
    "Breaking text at a width without cutting a word in half is a small "
    "problem that is annoying to get right, and textwrap has it done. "
    "wrap gives you a list of lines; fill gives you one string with the "
    "newlines already in. The same module has dedent, which strips the "
    "common leading whitespace from a block - which is what you want for "
    "a triple-quoted string indented inside a function, and is worth "
    "remembering the day one of those prints with eight spaces on every "
    "line.",
    "textwrap_use",
    [
        (
            "Import textwrap. Set text to "
            + repr(text)
            + ", then loop over textwrap.wrap of it with width="
            + str(width)
            + ", printing each line.",
            {"text": text, "width": width},
        )
        for text, width in _WRAPS
    ],
)


LIBRARY_PAGES: tuple[Page, ...] = (
    _P229,
    _P230,
    _P231,
    _P232,
    _P233,
    _P234,
    _P235,
    _P236,
    _P237,
    _P238,
)
