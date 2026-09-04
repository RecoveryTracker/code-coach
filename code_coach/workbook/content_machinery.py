"""Intermediate pages 249-258: the machinery under the machinery.

A descriptor, which is what @property is made of. ChainMap, for choices
in front of defaults. ExitStack, for however many context managers there
turn out to be. Globbing a real temporary directory. Environment
variables. Then math.prod and the counting functions, batched and
starmap, a NamedTuple with a default, a generator you can send values
into, and casefold - which is lower() for anyone whose text is not only
English.

Python only, same as 81-248.
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


# ── 249. What a property is made of ──────────────────────────

_DESCRIPTORS = (
    ("Positive", "Order", "count", 0, 5, -1, "must be positive"),
    ("NotBelow", "Basket", "items", 0, 3, -2, "cannot be negative"),
    ("AtLeastOne", "Batch", "size", 1, 10, 0, "needs at least one"),
    ("Positive", "Tank", "litres", 0, 60, -5, "must be positive"),
    ("Sensible", "Room", "floor", 0, 4, -1, "no floors below zero"),
    ("AtLeastOne", "Team", "players", 1, 11, 0, "a team needs players"),
    ("Positive", "Bill", "pence", 0, 450, -50, "must be positive"),
    ("NotBelow", "Shelf", "books", 0, 7, -3, "cannot be negative"),
    ("Sensible", "Trip", "miles", 0, 120, -10, "no negative distance"),
    ("AtLeastOne", "Grid", "rows", 1, 8, 0, "needs at least one row"),
    ("Positive", "Score", "points", 0, 40, -4, "must be positive"),
    ("NotBelow", "Stock", "units", 0, 25, -1, "cannot be negative"),
    ("Positive", "Crate", "count", 0, 8, -2, "must be positive"),
    ("NotBelow", "Pallet", "items", 0, 6, -4, "cannot be negative"),
    ("AtLeastOne", "Run", "size", 1, 14, 0, "needs at least one"),
    ("Positive", "Barrel", "litres", 0, 90, -9, "must be positive"),
    ("Sensible", "Berth", "floor", 0, 5, -2, "no floors below zero"),
    ("AtLeastOne", "Side", "players", 1, 15, 0, "a side needs players"),
    ("Positive", "Purse", "pence", 0, 500, -60, "must be positive"),
    ("NotBelow", "Rack", "books", 0, 12, -5, "cannot be negative"),
)

_P249 = _page(
    "descriptor-use",
    249,
    "What a property is made of",
    "__get__, __set__ and __set_name__, on a class of their own.",
    "A property is a descriptor with the plumbing hidden. Writing one "
    "yourself is worth doing once, because it explains how attribute "
    "access really works and it is reusable: this guard is written once "
    "and can then protect a field on any class, where a property has to "
    "be written again for every one. __set_name__ is the neat part - "
    "Python tells the descriptor what name it was given, so it can pick "
    "its own storage without being told twice.",
    "descriptor_use",
    [
        (
            "Write a class "
            + guard
            + " with __set_name__ storing '_' plus name, a __get__ "
            "returning that attribute from obj, and a __set__ that raises "
            "ValueError "
            + repr(complaint)
            + " when the value is below "
            + repr(floor)
            + " and otherwise stores it. Write "
            + cls
            + " with "
            + field
            + " set to a "
            + guard
            + "() and an __init__ that assigns it. Make thing with "
            + repr(good)
            + " and print its "
            + field
            + ", then in a try set it to "
            + repr(bad)
            + " and print the caught problem.",
            {
                "guard": guard,
                "cls": cls,
                "field": field,
                "floor": floor,
                "good": good,
                "bad": bad,
                "complaint": complaint,
            },
        )
        for guard, cls, field, floor, good, bad, complaint in _DESCRIPTORS
    ],
)


# ── 250. Choices in front of defaults ────────────────────────

_CHAINS = (
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
    ((("colour", "teal"), ("size", "small")), (("size", "huge"),), "colour"),
    ((("mode", "fast"), ("level", "warn")), (("level", "error"),), "mode"),
    ((("host", "remote"), ("port", "5173")), (("port", "8765"),), "host"),
    ((("theme", "light"), ("font", "serif")), (("font", "sans"),), "theme"),
    ((("sort", "date"), ("order", "down")), (("order", "up"),), "sort"),
    ((("shell", "zsh"), ("editor", "nano")), (("editor", "emacs"),), "shell"),
    ((("region", "us"), ("tier", "paid")), (("tier", "free"),), "region"),
    ((("lang", "fr"), ("units", "imperial")), (("units", "metric"),), "lang"),
)

_P250 = _page(
    "chainmap-use",
    250,
    "Choices in front of defaults",
    "ChainMap, which looks in each dict in turn.",
    "Settings almost always come in layers: what the user asked for, "
    "then a config file, then the built-in defaults. The usual answer is "
    "to merge them into one dict, which copies everything and loses "
    "which layer a value came from. ChainMap keeps them separate and "
    "searches in order, so the first map wins and nothing is copied - "
    "and a later change to the defaults still shows through. Note the "
    "length counts each key once, not once per map.",
    "chainmap_use",
    [
        (
            "Import ChainMap from collections. Set defaults to "
            + ", ".join(f"{k!r}: {v!r}" for k, v in defaults)
            + " and chosen to "
            + ", ".join(f"{k!r}: {v!r}" for k, v in chosen)
            + ". Make settings a ChainMap of chosen then defaults, and "
            "print settings for "
            + repr(chosen[0][0])
            + ", then for "
            + repr(only_default)
            + ", then its length.",
            {
                "defaults": defaults,
                "chosen": chosen,
                "only_default": only_default,
            },
        )
        for defaults, chosen, only_default in _CHAINS
    ],
)


# ── 251. However many there turn out to be ───────────────────

_STACKS = (
    ("a", "b", "c"),
    ("one", "two"),
    ("red", "green", "blue"),
    ("first", "second", "third"),
    ("in", "out"),
    ("x", "y", "z"),
    ("north", "south"),
    ("do", "re", "mi"),
    ("top", "middle", "bottom"),
    ("left", "right"),
    ("start", "middle", "end"),
    ("open", "read", "close"),
    ("d", "e", "f"),
    ("three", "four"),
    ("teal", "plum", "amber"),
    ("fourth", "fifth", "sixth"),
    ("over", "under"),
    ("p", "q", "r"),
    ("east", "west"),
    ("la", "ti", "do"),
)

_P251 = _page(
    "exitstack-use",
    251,
    "However many there turn out to be",
    "ExitStack, for a number of context managers known only at run time.",
    "A with statement needs you to know how many things you are opening "
    "when you write it. ExitStack does not: enter_context adds one to "
    "the pile at any point, and leaving the block closes all of them. "
    "Read the output - they close in reverse order, exactly as nested "
    "with blocks would, because the last thing opened may depend on the "
    "first. This is the answer to opening a list of files whose length "
    "you do not know.",
    "exitstack_use",
    [
        (
            "Import ExitStack and contextmanager from contextlib. Write "
            "step(name) decorated with contextmanager, printing 'open ' "
            "and name, yielding name in a try, and printing 'close ' and "
            "name in a finally. In a with ExitStack() as stack, build "
            "names by entering step for each of "
            + _seq(names)
            + ". After the block, print names.",
            {"names": names},
        )
        for names in _STACKS
    ],
)


# ── 252. Finding files by pattern ────────────────────────────

_GLOBS = (
    (("one.txt", "two.txt", "three.md"), "*.txt"),
    (("a.py", "b.py", "notes.md"), "*.py"),
    (("data.csv", "more.csv", "readme.txt"), "*.csv"),
    (("main.py", "test.py", "setup.cfg"), "*.py"),
    (("first.log", "second.log", "config.ini"), "*.log"),
    (("alpha.json", "beta.json", "gamma.xml"), "*.json"),
    (("north.md", "south.md", "map.png"), "*.md"),
    (("red.css", "blue.css", "index.html"), "*.css"),
    (("one.dat", "two.dat", "three.bin"), "*.dat"),
    (("sky.jpg", "sea.jpg", "notes.txt"), "*.jpg"),
    (("run.sh", "stop.sh", "readme.md"), "*.sh"),
    (("a.yaml", "b.yaml", "c.toml"), "*.yaml"),
    (("four.txt", "five.txt", "six.md"), "*.txt"),
    (("c.py", "d.py", "plan.md"), "*.py"),
    (("counts.csv", "totals.csv", "notes.txt"), "*.csv"),
    (("server.py", "client.py", "setup.toml"), "*.py"),
    (("third.log", "fourth.log", "prefs.ini"), "*.log"),
    (("delta.json", "gamma.json", "sigma.xml"), "*.json"),
    (("east.md", "west.md", "chart.png"), "*.md"),
    (("teal.css", "plum.css", "page.html"), "*.css"),
)

_P252 = _page(
    "path-glob",
    252,
    "Finding files by pattern",
    "Path.glob, and a temporary directory to try it in.",
    "glob matches file names against a pattern, where a star stands for "
    "any run of characters - so *.txt is every text file in that folder. "
    "Two things worth knowing. It hands back a generator, not a list, so "
    "it is cheap on a huge folder and has to be wrapped in list() or "
    "sorted() to look at twice. And the order is whatever the filesystem "
    "gives, which differs between machines, so sort it if the order "
    "matters at all - this page does.",
    "path_glob",
    [
        (
            "Import tempfile and Path from pathlib. In a with over "
            "tempfile.TemporaryDirectory() as folder, set root to Path of "
            "folder, write 'x' into each of "
            + _seq(files)
            + " under it, then set found to the sorted names matching "
            "root.glob("
            + repr(pattern)
            + ") and print it. Then print how many entries root.glob('*') "
            "finds.",
            {"files": files, "pattern": pattern},
        )
        for files, pattern in _GLOBS
    ],
)


# ── 253. Settings from outside the program ───────────────────

_ENVIRONS = (
    ("APP_MODE", "test", "APP_MISSING", "default"),
    ("LOG_LEVEL", "debug", "LOG_FILE", "none"),
    ("DB_HOST", "localhost", "DB_PASSWORD", "unset"),
    ("PORT", "8765", "TIMEOUT", "30"),
    ("REGION", "eu-west", "ZONE", "unknown"),
    ("THEME", "dark", "ACCENT", "blue"),
    ("CACHE_DIR", "tmp", "CACHE_SIZE", "0"),
    ("USER_ROLE", "admin", "USER_TEAM", "none"),
    ("BUILD_MODE", "release", "BUILD_TAG", "dev"),
    ("LOCALE", "en_GB", "CURRENCY", "GBP"),
    ("WORKERS", "4", "QUEUE", "main"),
    ("API_VERSION", "v2", "API_KEY", "missing"),
    ("APP_STAGE", "live", "APP_ABSENT", "default"),
    ("LOG_FORMAT", "json", "LOG_PATH", "none"),
    ("DB_PORT", "5432", "DB_SECRET", "unset"),
    ("UI_PORT", "5173", "UI_TIMEOUT", "60"),
    ("ZONE", "us-east", "RACK", "unknown"),
    ("ACCENT", "teal", "CONTRAST", "normal"),
    ("TEMP_DIR", "scratch", "TEMP_SIZE", "0"),
    ("USER_TEAM", "core", "USER_SHIFT", "none"),
)

_P253 = _page(
    "environ-use",
    253,
    "Settings from outside the program",
    "os.environ, and reading one that is not there.",
    "Environment variables are how a program is told about the world it "
    "is running in without changing its code - which host, which mode, "
    "which key. os.environ behaves like a dict, so everything from page "
    "128 applies: square brackets raise when it is missing, and get with "
    "a fallback does not. Reach for get, because a program that dies on "
    "a missing optional setting is worse than one that carries on. And "
    "never put a secret in your source instead.",
    "environ_use",
    [
        (
            "Import os. Set os.environ["
            + repr(name)
            + "] to "
            + repr(value)
            + ". Print it back, then print os.environ.get of "
            + repr(missing)
            + " with a fallback of "
            + repr(fallback)
            + ", then whether "
            + repr(missing)
            + " is in os.environ.",
            {
                "name": name,
                "value": value,
                "missing": missing,
                "fallback": fallback,
            },
        )
        for name, value, missing, fallback in _ENVIRONS
    ],
)


# ── 254. Multiplying a list, and counting arrangements ───────

_PRODUCTS = (
    ((1, 2, 3, 4), 5, 2),
    ((2, 3, 5), 6, 3),
    ((1, 1, 7), 4, 2),
    ((10, 10), 8, 2),
    ((3, 3, 3), 7, 3),
    ((2, 2, 2, 2), 10, 2),
    ((5, 4), 6, 2),
    ((1, 9, 2), 9, 4),
    ((6, 7), 5, 3),
    ((2, 5, 10), 12, 2),
    ((4, 4, 4), 8, 4),
    ((11, 3), 7, 2),
    ((2, 3, 4, 5), 6, 2),
    ((3, 4, 6), 7, 3),
    ((2, 2, 8), 5, 2),
    ((15, 15), 9, 2),
    ((4, 4, 4), 8, 3),
    ((3, 3, 3, 3), 11, 2),
    ((6, 5), 7, 2),
    ((2, 10, 3), 10, 4),
)

_P254 = _page(
    "math-prod",
    254,
    "Multiplying a list, and counting arrangements",
    "math.prod, comb and perm.",
    "prod is sum for multiplication, and it exists so you stop writing "
    "the three-line loop with a total starting at 1. comb counts how "
    "many ways you can choose that many things when the order does not "
    "matter, and perm counts them when it does - which is why perm is "
    "always the larger. If those two words have ever blurred together, "
    "the arithmetic here separates them: combinations for a hand of "
    "cards, permutations for a podium.",
    "math_prod",
    [
        (
            "Import math. Set numbers to ["
            + _seq(items)
            + "], then print math.prod of it, then math.comb of "
            + str(total)
            + " and "
            + str(take)
            + ", then math.perm of the same two.",
            {"items": items, "total": total, "take": take},
        )
        for items, total, take in _PRODUCTS
    ],
)


# ── 255. Fixed-size chunks, and arguments already in tuples ──

_BATCHES = (
    ((1, 2, 3, 4, 5), 2, ((2, 3), (3, 2))),
    ((1, 2, 3, 4, 5, 6), 3, ((2, 4), (5, 2))),
    ((10, 20, 30, 40), 2, ((10, 2), (3, 3))),
    ((1, 2, 3), 2, ((2, 5), (4, 2))),
    ((1, 2, 3, 4, 5, 6, 7), 3, ((3, 3), (2, 6))),
    ((5, 6, 7, 8), 3, ((7, 2), (2, 7))),
    ((1, 1, 1, 1, 1), 2, ((9, 2), (2, 9))),
    ((2, 4, 6, 8, 10), 4, ((4, 3), (3, 4))),
    ((9, 8, 7), 2, ((5, 3), (3, 5))),
    ((1, 2, 3, 4, 5, 6, 7, 8), 4, ((6, 2), (2, 8))),
    ((11, 22, 33), 3, ((8, 2), (2, 5))),
    ((3, 6, 9, 12, 15), 2, ((11, 2), (2, 10))),
    ((2, 3, 4, 5, 6), 2, ((3, 4), (4, 3))),
    ((2, 3, 4, 5, 6, 7), 3, ((3, 5), (6, 2))),
    ((15, 25, 35, 45), 2, ((11, 2), (4, 3))),
    ((4, 5, 6), 2, ((3, 6), (5, 2))),
    ((2, 3, 4, 5, 6, 7, 8), 3, ((4, 3), (2, 7))),
    ((6, 7, 8, 9), 3, ((8, 2), (2, 8))),
    ((2, 2, 2, 2, 2), 2, ((10, 2), (2, 10))),
    ((3, 6, 9, 12, 15), 4, ((5, 3), (3, 5))),
)

_P255 = _page(
    "batched-starmap",
    255,
    "Fixed-size chunks, and arguments already in tuples",
    "itertools.batched, and starmap for pairs you already have.",
    "batched cuts a sequence into chunks of a fixed size, with the last "
    "one short if it does not divide evenly - which is exactly what you "
    "want for paging, or for sending a thousand rows a hundred at a "
    "time. starmap is map for when the arguments are already sitting in "
    "tuples: map would pass each tuple as one argument, starmap spreads "
    "it out, which is the same star as page 174. Both save a loop that "
    "is easy to write with an off-by-one.",
    "batched_starmap",
    [
        (
            "Import batched and starmap from itertools. Set numbers to ["
            + _seq(items)
            + "], then print a list of each batched chunk of size "
            + str(size)
            + " as a list, then the list of starmap of pow over "
            + ", ".join(f"({x}, {y})" for x, y in pairs)
            + ".",
            {"items": items, "size": size, "pairs": pairs},
        )
        for items, size, pairs in _BATCHES
    ],
)


# ── 256. A record with a default and a replace ───────────────

_DEFAULTS = (
    ("Point", "x", "y", 0, 2, 5),
    ("Size", "width", "height", 1, 10, 4),
    ("Span", "low", "high", 0, 3, 17),
    ("Score", "points", "bonus", 0, 40, 7),
    ("Room", "floor", "number", 1, 3, 12),
    ("Trip", "miles", "hours", 1, 120, 3),
    ("Grid", "rows", "cols", 1, 8, 9),
    ("Tank", "full", "used", 0, 60, 22),
    ("Bill", "price", "people", 1, 45, 3),
    ("Wall", "bricks", "rows", 1, 90, 6),
    ("Gap", "start", "end", 0, 7, 31),
    ("Pair", "left", "right", 0, 7, 8),
    ("Coord", "x", "y", 0, 7, 9),
    ("Extent", "width", "height", 1, 64, 48),
    ("Reach", "low", "high", 0, 11, 47),
    ("Result", "points", "bonus", 0, 72, 9),
    ("Berth", "floor", "number", 1, 5, 14),
    ("Journey", "miles", "hours", 1, 180, 4),
    ("Board", "rows", "cols", 1, 6, 7),
    ("Barrel", "full", "used", 0, 90, 34),
)

_P256 = _page(
    "namedtuple-defaults",
    256,
    "A record with a default and a replace",
    "A NamedTuple default, plus _replace and _asdict.",
    "A field with a default can be left out when you build one, so the "
    "common case is short. _replace makes a new record with one field "
    "different, which is how you change something that cannot be "
    "changed - the same move as replace on page 214. _asdict hands it "
    "over as a plain dict for JSON or printing. The underscores are "
    "there so these names cannot collide with a field you called "
    "replace, which is a nice piece of thinking ahead.",
    "namedtuple_defaults",
    [
        (
            "Import NamedTuple from typing. Write "
            + cls
            + " with "
            + first
            + " hinted int and "
            + second
            + " hinted int defaulting to "
            + repr(fallback)
            + ". Make thing with just "
            + repr(given)
            + ", and moved as thing._replace with "
            + second
            + "="
            + repr(changed)
            + ". Print thing, then moved, then thing._asdict().",
            {
                "cls": cls,
                "first": first,
                "second": second,
                "fallback": fallback,
                "given": given,
                "changed": changed,
            },
        )
        for cls, first, second, fallback, given, changed in _DEFAULTS
    ],
)


# ── 257. A generator you can hand values back to ─────────────

_SENDS = (
    ((3, 4), "closed"),
    ((10, 20, 30), "done"),
    ((1, 1, 1), "finished"),
    ((5,), "stopped"),
    ((100, 200), "closed"),
    ((7, 7, 7, 7), "over"),
    ((2, 4, 8), "ended"),
    ((9, 1), "shut"),
    ((11, 22, 33), "closed"),
    ((6, 6), "done"),
    ((50, 25, 25), "complete"),
    ((1, 2, 3, 4), "finished"),
    ((5, 6), "closed"),
    ((15, 25, 35), "done"),
    ((2, 2, 2), "finished"),
    ((8,), "stopped"),
    ((300, 400), "sealed"),
    ((9, 9, 9, 9), "over"),
    ((3, 6, 12), "ended"),
    ((11, 3), "shut"),
)

_P257 = _page(
    "generator-send",
    257,
    "A generator you can hand values back to",
    "send, and the yield that is also an expression.",
    "Page 114 used yield to hand values out. It works the other way too: "
    "n = yield total means the yield produces whatever send passes in, "
    "so the generator becomes something you can talk to rather than only "
    "listen to. next() is needed first, to run it up to the first yield "
    "and get it ready - send before that is an error. This is the "
    "machinery under async, and it is worth meeting once even if you "
    "never write one on purpose.",
    "generator_send",
    [
        (
            "Write totaller() with total = 0 and a while True that sets n "
            "to yield total and adds n to total. Make machine, print "
            "next(machine), then print the result of sending "
            + " and then ".join(str(n) for n in sends)
            + ". Close it and print "
            + repr(done)
            + ".",
            {"sends": sends, "done": done},
        )
        for sends, done in _SENDS
    ],
)


# ── 258. Comparing text from more than one language ──────────

# Each row relies on the German sharp s: lower() leaves it alone, and
# casefold turns it into ss. The emitter raises if a row does not show
# lower failing where casefold succeeds.
_FOLDS = (
    ("STRASSE", "strasse", "Straße"),
    ("FUSSBALL", "fussball", "Fußball"),
    ("WEISS", "weiss", "weiß"),
    ("GROSS", "gross", "groß"),
    ("HEISS", "heiss", "heiß"),
    ("FUSS", "fuss", "Fuß"),
    ("SCHLOSS", "schloss", "Schloß"),
    ("PREUSSEN", "preussen", "Preußen"),
    ("GRUSS", "gruss", "Gruß"),
    ("SPASS", "spass", "Spaß"),
    ("MASSE", "masse", "Maße"),
    ("BUSSE", "busse", "Buße"),
    ("MASS", "mass", "Maß"),
    ("STRASSEN", "strassen", "Straßen"),
    ("GIESSEN", "giessen", "Gießen"),
    ("SCHLIESSEN", "schliessen", "schließen"),
    ("AUSSEN", "aussen", "außen"),
    ("REISSEN", "reissen", "reißen"),
    ("BLOSS", "bloss", "bloß"),
    ("SCHOSS", "schoss", "Schoß"),
)

_P258 = _page(
    "casefold-compare",
    258,
    "Comparing text from more than one language",
    "casefold, which lower() is not a substitute for.",
    "Comparing text case-insensitively by calling lower() on both sides "
    "works for English and quietly fails elsewhere. The German sharp s "
    "is the clearest example: it has no capital, and its case-folded "
    "form is two letters, ss. lower() leaves it alone, so the second "
    "line here comes out False even though the two words are the same "
    "word. casefold knows the rule, and the third line is True. Use "
    "casefold whenever you are comparing rather than displaying.",
    "casefold_compare",
    [
        (
            "Set first to "
            + repr(upper)
            + ", second to "
            + repr(plain)
            + " and third to "
            + repr(special)
            + ". Print whether first lowered equals second, then whether "
            "third lowered equals second, then whether third casefolded "
            "equals second casefolded.",
            {"upper": upper, "plain": plain, "special": special},
        )
        for upper, plain, special in _FOLDS
    ],
)


MACHINERY_PAGES: tuple[Page, ...] = (
    _P249,
    _P250,
    _P251,
    _P252,
    _P253,
    _P254,
    _P255,
    _P256,
    _P257,
    _P258,
)
