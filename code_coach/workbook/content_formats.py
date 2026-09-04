"""Intermediate pages 269-278: formats, archives, and text that looks the same.

difflib for how alike two things are. graphlib, which works out what has
to happen before what. heapq used as an actual heap. Then three formats
Python ships whole - zip, gzip and ini - plus catching what print would
have shown, string.Template, unicode normalisation, and the enums that
are also numbers or strings.

Page 277 is the sequel to 258: two strings that look identical on screen,
are not equal, and both are correct spellings of the same word.

Python only, same as 81-268.
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


# ── 269. How alike two pieces of text are ────────────────────

_DIFFS = (
    ("the quick brown fox", "the quick red fox", "appel", ("apple", "apply", "ape")),
    ("hello world", "hello there", "wrold", ("world", "word", "wold")),
    ("one two three", "one two four", "thre", ("three", "there", "threw")),
    ("red green blue", "red green gold", "gren", ("green", "grey", "greed")),
    ("north by south", "north by west", "sout", ("south", "shout", "scout")),
    ("open the door", "open the window", "widow", ("window", "widow", "wind")),
    ("salt and pepper", "salt and sugar", "peper", ("pepper", "paper", "piper")),
    ("iron and gold", "iron and tin", "gld", ("gold", "geld", "glad")),
    ("first second third", "first second last", "secnd", ("second", "send", "sound")),
    ("cat sat on mat", "cat sat on rug", "amt", ("mat", "man", "mad")),
    ("morning noon night", "morning noon dusk", "nite", ("night", "nite", "nine")),
    ("left right centre", "left right middle", "centr", ("centre", "center", "cent")),
    ("the slow brown dog", "the slow red dog", "brwn", ("brown", "brawn", "born")),
    ("good morning all", "good morning sam", "mornng", ("morning", "morning star", "moaning")),
    ("four five six", "four five seven", "fiev", ("five", "hive", "file")),
    ("teal plum amber", "teal plum gold", "plmu", ("plum", "plume", "plus")),
    ("east by west", "east by north", "wets", ("west", "wets", "welt")),
    ("shut the gate", "shut the door", "gaet", ("gate", "gaze", "late")),
    ("tin and lead", "tin and zinc", "led", ("lead", "led", "led on")),
    ("third fourth fifth", "third fourth last", "forth", ("fourth", "forth", "front")),
)

_P269 = _page(
    "difflib-use",
    269,
    "How alike two pieces of text are",
    "SequenceMatcher.ratio, and get_close_matches.",
    "ratio gives a number from 0 to 1 for how similar two sequences are, "
    "which is how you tell a small typo from a different word. "
    "get_close_matches is the useful shortcut built on it: hand it a "
    "misspelling and a list of real words and it ranks them, which is "
    "how a command-line tool says 'did you mean'. The same module "
    "produces unified diffs, which is where git's output comes from.",
    "difflib_use",
    [
        (
            "Import difflib. Set first to "
            + repr(first)
            + " and second to "
            + repr(second)
            + ". Make a SequenceMatcher with None and the two, print its "
            "ratio rounded to 2, then print get_close_matches of "
            + repr(typo)
            + " against ["
            + _seq(options)
            + "].",
            {
                "first": first,
                "second": second,
                "typo": typo,
                "options": options,
            },
        )
        for first, second, typo, options in _DIFFS
    ],
)


# ── 270. What has to happen before what ──────────────────────

_GRAPHS = (
    ((("cake", ("batter",)), ("batter", ("eggs", "flour"))), "eggs", "cake"),
    ((("app", ("lib",)), ("lib", ("core",))), "core", "app"),
    ((("deploy", ("build",)), ("build", ("test",))), "test", "deploy"),
    ((("dinner", ("sauce",)), ("sauce", ("onion", "stock"))), "onion", "dinner"),
    ((("report", ("data",)), ("data", ("query",))), "query", "report"),
    ((("house", ("walls",)), ("walls", ("bricks",))), "bricks", "house"),
    ((("cup", ("tea",)), ("tea", ("water", "leaves"))), "water", "cup"),
    ((("site", ("pages",)), ("pages", ("text",))), "text", "site"),
    ((("bread", ("dough",)), ("dough", ("yeast", "flour"))), "yeast", "bread"),
    ((("film", ("edit",)), ("edit", ("footage",))), "footage", "film"),
    ((("release", ("sign",)), ("sign", ("compile",))), "compile", "release"),
    ((("meal", ("pasta",)), ("pasta", ("eggs", "flour"))), "flour", "meal"),
    ((("stew", ("stock",)), ("stock", ("bones", "water"))), "bones", "stew"),
    ((("tool", ("steel",)), ("steel", ("iron",))), "iron", "tool"),
    ((("ship", ("hull",)), ("hull", ("plate",))), "plate", "ship"),
    ((("supper", ("gravy",)), ("gravy", ("juices", "flour"))), "juices", "supper"),
    ((("chart", ("counts",)), ("counts", ("survey",))), "survey", "chart"),
    ((("barn", ("frame",)), ("frame", ("timber",))), "timber", "barn"),
    ((("brew", ("malt",)), ("malt", ("barley", "water"))), "barley", "brew"),
    ((("album", ("tracks",)), ("tracks", ("takes",))), "takes", "album"),
)

_P270 = _page(
    "graphlib-use",
    270,
    "What has to happen before what",
    "graphlib.TopologicalSorter, for dependencies.",
    "Given what each thing depends on, a topological sort produces an "
    "order in which nothing comes before what it needs. That is how a "
    "build system decides what to compile first, how a package manager "
    "orders installs, and how a spreadsheet decides which cells to "
    "recalculate. Writing it yourself is a known-tricky bit of code, and "
    "it has been in the standard library since 3.9. It also raises if "
    "the dependencies form a cycle, which is the other thing you want.",
    "graphlib_use",
    [
        (
            "Import TopologicalSorter from graphlib. Set graph to "
            + ", ".join(f"{k!r}: [" + _seq(v) + "]" for k, v in graph)
            + ", set order to the list of its static_order, and print it. "
            "Then print whether "
            + repr(before)
            + " comes before "
            + repr(after)
            + " in it.",
            {"graph": graph, "before": before, "after": after},
        )
        for graph, before, after in _GRAPHS
    ],
)


# ── 271. A heap you push and pop yourself ────────────────────

_HEAPS = (
    (5, 1, 9, 3),
    (10, 2, 8, 4),
    (7, 7, 3, 1),
    (100, 50, 75, 25),
    (2, 4, 6, 8),
    (9, 8, 7, 6),
    (1, 3, 5, 7, 9),
    (42, 7, 99, 13),
    (6, 2, 11, 4),
    (15, 3, 27, 9),
    (88, 12, 45, 30),
    (4, 16, 8, 2),
    (14, 5, 19, 7),
    (12, 3, 9, 5),
    (8, 8, 4, 2),
    (200, 60, 90, 30),
    (3, 6, 9, 12),
    (11, 10, 9, 8),
    (2, 4, 6, 8, 10),
    (51, 8, 90, 14),
)

_P271 = _page(
    "heapq-real",
    271,
    "A heap you push and pop yourself",
    "heappush and heappop, and what a heap actually is.",
    "Page 203 used heapq through nsmallest. This is the thing itself: a "
    "list kept in an order where the smallest is always at the front, so "
    "pushing and popping are cheap and you never sort. The last line "
    "prints the rest sorted on purpose - print the heap raw and it looks "
    "shuffled, because a heap is not a sorted list and only promises "
    "about position 0. This is the right structure for a queue where the "
    "most urgent thing goes next.",
    "heapq_real",
    [
        (
            "Import heapq. Start heap as an empty list and heappush each "
            "of "
            + _seq(items)
            + " onto it. Print two heappops, then the rest sorted.",
            {"items": items},
        )
        for items in _HEAPS
    ],
)


# ── 272. Several files in one ────────────────────────────────

_ZIPS = (
    ("bundle.zip", (("one.txt", "hello"), ("two.txt", "world"))),
    ("pack.zip", (("a.txt", "first"), ("b.txt", "second"))),
    ("notes.zip", (("mon.txt", "meeting"), ("tue.txt", "review"))),
    ("data.zip", (("north.csv", "rows"), ("south.csv", "more"))),
    ("site.zip", (("index.html", "page"), ("style.css", "rules"))),
    ("logs.zip", (("app.log", "started"), ("db.log", "connected"))),
    ("docs.zip", (("read.md", "start here"), ("more.md", "and then"))),
    ("keys.zip", (("pub.txt", "public"), ("note.txt", "not secret"))),
    ("code.zip", (("main.py", "print"), ("util.py", "helpers"))),
    ("text.zip", (("sky.txt", "blue"), ("sea.txt", "green"))),
    ("book.zip", (("one.md", "chapter one"), ("two.md", "chapter two"))),
    ("mix.zip", (("red.txt", "warm"), ("blue.txt", "cool"))),
    ("crate.zip", (("three.txt", "morning"), ("four.txt", "evening"))),
    ("sack.zip", (("c.txt", "third"), ("d.txt", "fourth"))),
    ("diary.zip", (("thu.txt", "review"), ("fri.txt", "release"))),
    ("counts.zip", (("east.csv", "totals"), ("west.csv", "spares"))),
    ("page.zip", (("home.html", "front"), ("main.css", "styles"))),
    ("trace.zip", (("web.log", "ready"), ("api.log", "listening"))),
    ("guide.zip", (("start.md", "begin here"), ("next.md", "and next"))),
    ("keys2.zip", (("cert.txt", "public"), ("hint.txt", "not secret"))),
)

_P272 = _page(
    "zipfile-use",
    272,
    "Several files in one",
    "zipfile, writing entries without touching the disk twice.",
    "A zip is a folder in a file, and Python reads and writes them "
    "without any external tool. writestr puts an entry in directly from "
    "a string, so you never have to write a temporary file just to add "
    "it - which is the trick worth taking away. namelist gives what is "
    "inside, read gives one entry's bytes. Note the with blocks: an "
    "archive left unclosed is an archive that is quietly truncated.",
    "zipfile_use",
    [
        (
            "Import tempfile, zipfile and Path from pathlib. In a "
            "TemporaryDirectory, set archive to "
            + repr(archive)
            + " under it. Open it for writing and writestr "
            + " and ".join(f"{n!r} holding {t!r}" for n, t in files)
            + ". Open it again and print the sorted namelist, then read "
            + repr(files[0][0])
            + " and decode it as utf-8.",
            {"archive": archive, "files": files},
        )
        for archive, files in _ZIPS
    ],
)


# ── 273. The same bytes, smaller ─────────────────────────────

_GZIPS = (
    "hello hello hello hello",
    "the same line over and over and over",
    "aaaaaaaaaaaaaaaaaaaaaaaa",
    "one two one two one two one two",
    "compress me compress me compress me",
    "north south north south north south",
    "red green blue red green blue red",
    "data data data data data data",
    "repeat repeat repeat repeat repeat",
    "a b a b a b a b a b a b a b a b",
    "the quick fox the quick fox the quick fox",
    "line one line one line one line one",
    "morning morning morning morning",
    "the same words again and again and again",
    "bbbbbbbbbbbbbbbbbbbbbbbb",
    "three four three four three four three",
    "squeeze me squeeze me squeeze me",
    "east west east west east west",
    "teal plum amber teal plum amber teal",
    "counts counts counts counts counts",
)

_P273 = _page(
    "gzip-use",
    273,
    "The same bytes, smaller",
    "gzip.compress and decompress, and why the bytes are not printed.",
    "gzip squeezes bytes by noticing repetition, which is why every "
    "string here repeats itself. Two things worth knowing. It works on "
    "bytes, not text, so encode first as always. And the compressed "
    "output embeds a timestamp: compress the same data twice in the "
    "same second and the bytes match, do it a second apart and they do "
    "not. So comparing or hashing compressed files to decide whether "
    "their contents match is unreliable - compare what comes back out, "
    "as the last line here does, and pass mtime=0 when you need the "
    "output itself to be reproducible.",
    "gzip_use",
    [
        (
            "Import gzip. Set text to "
            + repr(text)
            + ", raw to it encoded as utf-8, and squeezed to "
            "gzip.compress of raw. Print the length of raw, then the "
            "decompressed text, then whether the decompressed bytes equal "
            "raw.",
            {"text": text},
        )
        for text in _GZIPS
    ],
)


# ── 274. An ini file read properly ───────────────────────────

_INIS = (
    ("server", "host", "localhost", "port", 8080),
    ("database", "name", "records", "timeout", 30),
    ("app", "mode", "release", "workers", 4),
    ("cache", "path", "tmp", "size", 256),
    ("mail", "sender", "noreply", "retries", 3),
    ("log", "level", "info", "keep", 7),
    ("api", "version", "v2", "limit", 100),
    ("ui", "theme", "dark", "width", 80),
    ("build", "target", "release", "jobs", 8),
    ("queue", "name", "main", "depth", 500),
    ("auth", "realm", "internal", "expiry", 3600),
    ("store", "region", "eu-west", "shards", 12),
    ("server", "host", "127.0.0.1", "port", 5173),
    ("database", "name", "entries", "timeout", 60),
    ("app", "mode", "debug", "workers", 8),
    ("cache", "path", "scratch", "size", 512),
    ("mail", "sender", "postbox", "retries", 5),
    ("log", "level", "warn", "keep", 14),
    ("api", "version", "v3", "limit", 250),
    ("ui", "theme", "light", "width", 120),
)

_P274 = _page(
    "configparser-use",
    274,
    "An ini file read properly",
    "configparser, and getint rather than int of a string.",
    "The ini format - sections in square brackets, keys and values under "
    "them - is everywhere, and parsing it by hand goes wrong on "
    "comments, on values containing equals signs, and on continuation "
    "lines. configparser knows all of it. Note getint rather than "
    "int(parser[...][...]): everything comes back as text otherwise, and "
    "asking the parser to convert gives a clearer error when the value "
    "is not a number. read_string is what makes this testable.",
    "configparser_use",
    [
        (
            "Import configparser. Set text to an ini document with a "
            "section ["
            + section
            + "] holding "
            + key
            + " = "
            + value
            + " and "
            + number_key
            + " = "
            + str(number)
            + ", each line ending in a newline. Read it with "
            "read_string, then print the "
            + key
            + ", then getint of "
            + number_key
            + ", then the sections list.",
            {
                "section": section,
                "key": key,
                "value": value,
                "number_key": number_key,
                "number": number,
            },
        )
        for section, key, value, number_key, number in _INIS
    ],
)


# ── 275. Catching what print would have shown ────────────────

_REDIRECTS = (
    ("captured", "back to normal"),
    ("into the buffer", "onto the screen"),
    ("hidden line", "visible line"),
    ("collected", "printed"),
    ("not shown yet", "shown now"),
    ("held", "released"),
    ("stored away", "out loud"),
    ("quiet", "loud"),
    ("inside", "outside"),
    ("saved", "displayed"),
    ("caught", "free"),
    ("buffered", "flushed"),
    ("taken aside", "back in the open"),
    ("into the sink", "onto the page"),
    ("unseen line", "seen line"),
    ("gathered", "spoken"),
    ("waiting still", "waiting no more"),
    ("kept", "let go"),
    ("tucked away", "out in front"),
    ("hushed", "clear"),
)

_P275 = _page(
    "stringio-redirect",
    275,
    "Catching what print would have shown",
    "io.StringIO with contextlib.redirect_stdout.",
    "A StringIO is a file that lives in memory, so anything that writes "
    "to a file can write to it instead - which is how you test code that "
    "prints, without changing the code to return a string. "
    "redirect_stdout points print at it for the length of the with "
    "block. Notice the first message appears only because it was pulled "
    "back out of the buffer afterwards; while the block was running it "
    "went nowhere near the screen.",
    "stringio_redirect",
    [
        (
            "Import contextlib and io. Make buffer an io.StringIO. In a "
            "with over contextlib.redirect_stdout(buffer), print "
            + repr(hidden)
            + ". After the block, print the buffer's value stripped, then "
            "print "
            + repr(after)
            + ".",
            {"hidden": hidden, "after": after},
        )
        for hidden, after in _REDIRECTS
    ],
)


# ── 276. Filling in a template safely ────────────────────────

_TEMPLATES = (
    ("Hello $name, you are $age", "name", "ada", "age", 36),
    ("$name lives in $city", "name", "sam", "city", 0),
    ("$who scored $points", "who", "kim", "points", 90),
    ("$item costs $pence", "item", "apple", "pence", 45),
    ("$word has $count letters", "word", "sky", "count", 3),
    ("$metal is number $atomic", "metal", "iron", "atomic", 26),
    ("$song runs $seconds", "song", "alive", "seconds", 245),
    ("$team has $points", "team", "reds", "points", 41),
    ("$book has $pages", "book", "dune", "pages", 412),
    ("$room is on $floor", "room", "attic", "floor", 4),
    ("$tool weighs $weight", "tool", "saw", "weight", 3),
    ("$trip is $miles long", "trip", "north", "miles", 120),
    ("Hello $name, you are $age", "name", "finn", "age", 27),
    ("$name lives in $city", "name", "ida", "city", 0),
    ("$who scored $points", "who", "kit", "points", 82),
    ("$item costs $pence", "item", "kiwi", "pence", 55),
    ("$word has $count letters", "word", "moon", "count", 4),
    ("$metal melts at $degrees", "metal", "tin", "degrees", 232),
    ("$song runs $seconds", "song", "art", "seconds", 224),
    ("$team has $points", "team", "blues", "points", 12),
)

_P276 = _page(
    "template-use",
    276,
    "Filling in a template safely",
    "string.Template, substitute and safe_substitute.",
    "An f-string runs arbitrary expressions, which is exactly wrong when "
    "the template text came from a user or a config file - that is a "
    "way to run code you did not write. Template only replaces $names "
    "and can do nothing else, which makes it safe for text you did not "
    "author. substitute raises when a name is missing; safe_substitute "
    "leaves the $name sitting there, which the second line shows. Pick "
    "the one that matches whether a gap is a bug.",
    "template_use",
    [
        (
            "Import Template from string. Make greeting a Template of "
            + repr(text)
            + ". Print it substituted with "
            + first
            + "="
            + repr(first_value)
            + " and "
            + second
            + "="
            + repr(second_value)
            + ", then print safe_substitute with only "
            + first
            + " given.",
            {
                "template": text,
                "first": first,
                "first_value": first_value,
                "second": second,
                "second_value": second_value,
            },
        )
        for text, first, first_value, second, second_value in _TEMPLATES
    ],
)


# ── 277. Two spellings of the same letter ────────────────────

_NORMALS = (
    "café",
    "naïve",
    "über",
    "façade",
    "jalapeño",
    "résumé",
    "piñata",
    "Zürich",
    "crème",
    "señor",
    "fiancée",
    "Málaga",
    "hôtel",
    "Köln",
    "garçon",
    "mañana",
    "smörgås",
    "tête",
    "año",
    "Angström",
)

_P277 = _page(
    "normalize-use",
    277,
    "Two spellings of the same letter",
    "unicodedata.normalize, NFC and NFD.",
    "An accented letter can be stored as one character, or as the plain "
    "letter followed by a combining accent - two different strings that "
    "draw identically on screen and compare as unequal. That is why the "
    "same name typed on a Mac and on Windows can fail to match. "
    "normalize converts between the forms: NFC composes, NFD takes "
    "apart. Normalise to NFC before comparing or storing text, in the "
    "same breath as the casefold of page 258.",
    "normalize_use",
    [
        (
            "Import unicodedata. Set composed to "
            + repr(word)
            + " and decomposed to the NFD normalisation of it. Print the "
            "length of each, then whether they are equal, then whether "
            "the NFC of decomposed equals composed.",
            {"word": word},
        )
        for word in _NORMALS
    ],
)


# ── 278. An enum that is also a number or a string ───────────

_MIXED = (
    ("Level", "LOW", "HIGH", "Mode", "READ", "read", "WRITE", "write"),
    ("Rank", "JUNIOR", "SENIOR", "Colour", "RED", "red", "BLUE", "blue"),
    ("Speed", "SLOW", "FAST", "Suit", "SPADES", "spades", "HEARTS", "hearts"),
    ("Size", "SMALL", "LARGE", "State", "OPEN", "open", "SHUT", "shut"),
    ("Grade", "PASS", "MERIT", "Way", "NORTH", "north", "SOUTH", "south"),
    ("Tier", "FREE", "PAID", "Face", "HEADS", "heads", "TAILS", "tails"),
    ("Phase", "EARLY", "LATE", "Kind", "TEXT", "text", "BINARY", "binary"),
    ("Depth", "SHALLOW", "DEEP", "Turn", "LEFT", "left", "RIGHT", "right"),
    ("Heat", "COOL", "WARM", "Step", "MIX", "mix", "BAKE", "bake"),
    ("Band", "NARROW", "WIDE", "Sort", "ASC", "asc", "DESC", "desc"),
    ("Load", "LIGHT", "HEAVY", "Zone", "INNER", "inner", "OUTER", "outer"),
    ("Cost", "CHEAP", "DEAR", "Form", "SHORT", "short", "LONG", "long"),
    ("Depth_", "SHALLOW", "DEEP", "Access", "FETCH", "fetch", "STORE", "store"),
    ("Placing", "FIRST", "LAST", "Shade", "TEAL", "teal", "PLUM", "plum"),
    ("Pace", "CRAWL", "SPRINT", "Night", "THU", "thu", "FRI", "fri"),
    ("Weight_", "LIGHT", "HEAVY", "Gate", "AJAR", "ajar", "BARRED", "barred"),
    ("Standing", "JUNIOR", "SENIOR", "Bearing", "EAST", "east", "WEST", "west"),
    ("Plan", "TRIAL", "FULL", "Coin", "FRONT", "front", "BACK", "back"),
    ("Stage_", "EARLY", "LATE", "Styling", "PLAIN", "plain", "RICH", "rich"),
    ("Volume_", "QUIET", "LOUD", "Order__", "UP", "up", "DOWN", "down"),
)

_P278 = _page(
    "int-str-enum",
    278,
    "An enum that is also a number or a string",
    "IntEnum and StrEnum, and the comparison that then just works.",
    "A plain Enum member is not equal to its value, which is correct and "
    "occasionally inconvenient - especially at the edges of a program, "
    "where a value arrives from JSON or a database as a bare string. "
    "IntEnum members really are integers and StrEnum members really are "
    "strings, so they compare and sort and serialise like one while "
    "still having a name. The cost is that the type system stops "
    "protecting you from comparing against any old string.",
    "int_str_enum",
    [
        (
            "Import IntEnum and StrEnum from enum. Write "
            + number_cls
            + " as an IntEnum with "
            + low
            + " = 1 and "
            + high
            + " = 2, and "
            + text_cls
            + " as a StrEnum with "
            + first
            + " = "
            + repr(first_value)
            + " and "
            + second
            + " = "
            + repr(second_value)
            + ". Print whether "
            + high
            + " is greater than "
            + low
            + ", then "
            + high
            + " plus 1, then whether "
            + first
            + " equals "
            + repr(first_value)
            + ".",
            {
                "number_cls": number_cls,
                "low": low,
                "high": high,
                "text_cls": text_cls,
                "first": first,
                "first_value": first_value,
                "second": second,
                "second_value": second_value,
            },
        )
        for (
            number_cls,
            low,
            high,
            text_cls,
            first,
            first_value,
            second,
            second_value,
        ) in _MIXED
    ],
)


FORMAT_PAGES: tuple[Page, ...] = (
    _P269,
    _P270,
    _P271,
    _P272,
    _P273,
    _P274,
    _P275,
    _P276,
    _P277,
    _P278,
)
