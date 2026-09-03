"""Intermediate pages 259-268: the last corners of Python.

A metaclass, which is the older and heavier answer to what page 246 did
in four lines. weakref. struct, for bytes with a layout. uuid5, which is
the same every time for the same name. Reading an exception without its
traceback, and catching a warning rather than letting it print. shutil.
cmp_to_key, methodcaller, and the dataclass fields that stay out of the
repr and out of the comparison.

These are the corners. Most working Python never needs a metaclass or a
weak reference, and knowing they exist is most of the value - you will
recognise them when you meet them in someone else's code, which is when
they actually turn up.

Python only, same as 81-258.
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


# ── 259. A class that makes classes ──────────────────────────

_METAS = (
    ("Registry", ("Alpha", "Beta")),
    ("Catalogue", ("Json", "Xml")),
    ("Collector", ("Circle", "Square")),
    ("Index", ("Csv", "Tsv")),
    ("Roll", ("Console", "File")),
    ("Book", ("Length", "Format")),
    ("List", ("Start", "Stop")),
    ("Table", ("Utf8", "Latin1")),
    ("Store", ("Memory", "Disk")),
    ("Log", ("Blur", "Sharpen")),
    ("Record", ("Build", "Deploy")),
    ("Sheet", ("Fast", "Deep")),
)

_P259 = _page(
    "metaclass-use",
    259,
    "A class that makes classes",
    "A metaclass, and why __init_subclass__ usually beats it.",
    "A class is itself an object, and its type is a metaclass - normally "
    "type. Give a class one of your own and its __new__ runs as the "
    "class is defined, which is how a registry like this gets filled. "
    "Page 246 did the same job with __init_subclass__ in four lines and "
    "no new concept, which is why that is the modern answer. Learn this "
    "one so you can read a framework that uses it, and then reach for "
    "the simpler thing in your own code.",
    "metaclass_use",
    [
        (
            "Write a metaclass "
            + meta
            + " inheriting type, with a class attribute made set to an "
            "empty list and a __new__(mcls, name, bases, namespace) that "
            "calls super().__new__, appends name to "
            + meta
            + ".made and returns the class. Write "
            + " and ".join(children)
            + " with metaclass="
            + meta
            + " and pass, then print "
            + meta
            + ".made.",
            {"meta": meta, "children": children},
        )
        for meta, children in _METAS
    ],
)


# ── 260. A reference that does not keep it alive ─────────────

_WEAKS = (
    "Thing",
    "Node",
    "Widget",
    "Page",
    "Session",
    "Buffer",
    "Handle",
    "Entry",
    "Frame",
    "Socket",
    "Record",
    "Token",
)

_P260 = _page(
    "weakref-use",
    260,
    "A reference that does not keep it alive",
    "weakref, and what happens when the last real reference goes.",
    "Python keeps an object alive as long as something refers to it, "
    "which is usually what you want and is exactly wrong for a cache: a "
    "cache that keeps things alive is a memory leak with a helpful name. "
    "A weak reference points at an object without counting, so the "
    "object can still be collected - and then calling the reference "
    "gives None rather than a stale object. Watch the second line: the "
    "moment del removes the last real reference, the link goes empty.",
    "weakref_use",
    [
        (
            "Import weakref. Write an empty class "
            + cls
            + " with pass. Make thing, and link as weakref.ref of it. "
            "Print whether link() is thing, then del thing and print "
            "whether link() is None.",
            {"cls": cls},
        )
        for cls in _WEAKS
    ],
)


# ── 261. Numbers packed into bytes with a layout ─────────────

_STRUCTS = (
    ("<hh", (7, 9)),
    ("<ii", (1, 2)),
    ("<hhh", (1, 2, 3)),
    (">hh", (7, 9)),
    ("<bb", (5, 6)),
    ("<i", (66051,)),
    (">i", (66051,)),
    ("<hi", (4, 100)),
    ("<bbbb", (1, 2, 3, 4)),
    (">hhh", (10, 20, 30)),
    ("<ih", (256, 1)),
    ("<hhhh", (1, 1, 1, 1)),
)

_P261 = _page(
    "struct-use",
    261,
    "Numbers packed into bytes with a layout",
    "struct.pack and unpack, and why the format string starts with < or >.",
    "When bytes come off a file or a socket they have a layout someone "
    "else decided, and struct is how you say what it is: h for a "
    "two-byte integer, i for four, and the first character for byte "
    "order. Two of these pages pack the same numbers with < and with > "
    "and the hex comes out reversed - that is endianness, and it is why "
    "you never leave the first character off. unpack always gives a "
    "tuple, even for one value.",
    "struct_use",
    [
        (
            "Import struct. Pack "
            + " and ".join(str(n) for n in values)
            + " with the layout "
            + repr(layout)
            + " into packed. Print its length, then its hex, then the "
            "unpack of it with the same layout.",
            {"layout": layout, "values": values},
        )
        for layout, values in _STRUCTS
    ],
)


# ── 262. An id derived from a name ───────────────────────────

_UUIDS = (
    "example.com",
    "python.org",
    "code.coach",
    "localhost",
    "api.example.com",
    "docs.python.org",
    "shop.example.net",
    "mail.example.org",
    "cdn.example.io",
    "test.example.dev",
    "blog.example.uk",
    "files.example.co",
)

_P262 = _page(
    "uuid5-use",
    262,
    "An id derived from a name",
    "uuid5, which gives the same id for the same name every time.",
    "uuid4 gives a random id, which is right when you want one nobody "
    "can guess. uuid5 gives one worked out from a namespace and a name, "
    "so the same name always gives the same id - on any machine, in any "
    "year. That is what you want when two systems must agree on an id "
    "for the same thing without talking to each other. The first line "
    "here proves it by making the same one twice.",
    "uuid5_use",
    [
        (
            "Import uuid. Make first and second both as uuid5 of "
            "uuid.NAMESPACE_DNS and "
            + repr(name)
            + ". Print whether they are equal, then str of first, then "
            "first.version.",
            {"name": name},
        )
        for name in _UUIDS
    ],
)


# ── 263. The exception line without the traceback ────────────

_BADS = (
    "abc",
    "hello",
    "twelve",
    "one",
    "1.5.2",
    "n/a",
    "none",
    "many",
    "x",
    "3a",
    "--",
    "ten",
)

_P263 = _page(
    "traceback-only",
    263,
    "The exception line without the traceback",
    "traceback.format_exception_only, for the line that matters.",
    "Printing a whole traceback into a log is often too much - pages of "
    "frames when what you wanted was the one line saying what went "
    "wrong. format_exception_only gives you exactly that, as a list of "
    "lines, and the list is nearly always one line long. Its sibling "
    "format_exc gives the whole thing when you do want it. Between them "
    "you can decide how much noise an error makes, rather than taking "
    "whatever Python prints.",
    "traceback_only",
    [
        (
            "Import traceback. In a try, call int on "
            + repr(bad)
            + ". Catch ValueError as problem, set lines to "
            "traceback.format_exception_only of its type and it, then "
            "print the first line stripped and the number of lines.",
            {"bad": bad},
        )
        for bad in _BADS
    ],
)


# ── 264. A warning caught instead of printed ─────────────────

_WARNINGS = (
    ("this is old", "DeprecationWarning"),
    ("use the new one", "DeprecationWarning"),
    ("that may be slow", "UserWarning"),
    ("check the value", "UserWarning"),
    ("going away in v3", "DeprecationWarning"),
    ("not recommended", "UserWarning"),
    ("renamed last year", "DeprecationWarning"),
    ("may lose precision", "UserWarning"),
    ("prefer the other call", "DeprecationWarning"),
    ("this is untested", "UserWarning"),
    ("will be removed", "DeprecationWarning"),
    ("consider the default", "UserWarning"),
)

_P264 = _page(
    "warnings-use",
    264,
    "A warning caught instead of printed",
    "warnings.warn, and catch_warnings for testing that it happened.",
    "A warning is for something that is not an error but that the caller "
    "should know about - a function on its way out, a value that will "
    "lose precision. It goes to standard error and, by default, only "
    "once per place it is raised. catch_warnings with record=True "
    "collects them instead of printing, which is the only sensible way "
    "to test that your code warns when it should. simplefilter('always') "
    "turns off the once-only rule while you look.",
    "warnings_use",
    [
        (
            "Import warnings. In a with over "
            "warnings.catch_warnings(record=True) as caught, call "
            "simplefilter('always') and then warn "
            + repr(message)
            + " as a "
            + category
            + ". Afterwards print how many were caught, the first one's "
            "category name, and its message as a string.",
            {"message": message, "category": category},
        )
        for message, category in _WARNINGS
    ],
)


# ── 265. Copying a file ──────────────────────────────────────

_COPIES = (
    ("one.txt", "two.txt", "hello"),
    ("first.md", "second.md", "notes"),
    ("data.csv", "backup.csv", "rows"),
    ("main.py", "main.bak", "code"),
    ("a.log", "b.log", "entries"),
    ("left.json", "right.json", "values"),
    ("north.txt", "south.txt", "words"),
    ("red.css", "blue.css", "styles"),
    ("in.dat", "out.dat", "numbers"),
    ("sky.txt", "sea.txt", "lines"),
    ("run.sh", "run.old", "script"),
    ("draft.md", "final.md", "text"),
)

_P265 = _page(
    "shutil-copy",
    265,
    "Copying a file",
    "shutil.copy, and reading the folder back.",
    "shutil is the module for whole-file work: copy, move, delete a tree, "
    "find a program on the path. copy takes the contents and the "
    "permission bits; copy2 also takes the timestamps, which matters if "
    "anything downstream looks at them. Doing it by hand - open, read, "
    "write, close - is three lines that are wrong for large files and "
    "for anything that is not plain bytes.",
    "shutil_copy",
    [
        (
            "Import shutil, tempfile and Path from pathlib. In a with "
            "over a TemporaryDirectory as folder, set root to Path of it, "
            "write "
            + repr(text)
            + " into "
            + repr(first)
            + " under root, copy it to "
            + repr(second)
            + " with shutil.copy, then print the second file's text and "
            "the sorted names in root.",
            {"first": first, "second": second, "text": text},
        )
        for first, second, text in _COPIES
    ],
)


# ── 266. An old comparison function, made into a key ─────────

_CMPS = (
    ("ccc", "a", "bb"),
    ("dddd", "aa", "c"),
    ("zzzzz", "y", "xx"),
    ("four", "to", "s"),
    ("aaaa", "bbb", "cc"),
    ("eeeee", "dd", "f"),
    ("mmm", "n", "oo"),
    ("pppp", "q", "rr"),
    ("ssss", "tt", "u"),
    ("vvvvv", "ww", "x"),
    ("yyy", "z", "aa"),
    ("bbbb", "c", "dd"),
)

_P266 = _page(
    "cmp-to-key",
    266,
    "An old comparison function, made into a key",
    "functools.cmp_to_key, for the two-argument comparison.",
    "Older code, and code translated from other languages, sorts with a "
    "function taking two items and returning a negative number, zero or "
    "a positive one. Python's sorted wants a key function taking one "
    "item instead, which is faster and usually clearer. cmp_to_key "
    "bridges the two so you do not have to rewrite the comparison. Reach "
    "for it when you are handed one - and write a key function when you "
    "are starting from nothing.",
    "cmp_to_key_use",
    [
        (
            "Import cmp_to_key from functools. Write compare(a, b) "
            "returning the length of a minus the length of b. Set words "
            "to ["
            + _seq(words)
            + "], then print it sorted with key=cmp_to_key(compare).",
            {"words": words},
        )
        for words in _CMPS
    ],
)


# ── 267. Calling the same method on each of them ─────────────

_CALLERS = (
    (("Ada", "SAM", "Kim"), "banana", "a", "-"),
    (("RED", "Green", "blue"), "hello", "l", "L"),
    (("MON", "Tue", "wed"), "letter", "e", "3"),
    (("Iron", "GOLD", "tin"), "mississippi", "s", "z"),
    (("North", "SOUTH", "east"), "coffee", "f", "p"),
    (("Do", "RE", "mi"), "balloon", "o", "0"),
    (("Saw", "AXE", "file"), "attention", "t", "T"),
    (("Sky", "SEA", "sun"), "success", "c", "k"),
    (("One", "TWO", "six"), "little", "t", "d"),
    (("Salt", "PEPPER", "sugar"), "pepper", "p", "b"),
    (("Left", "RIGHT", "up"), "running", "n", "m"),
    (("Fast", "SLOW", "mid"), "address", "d", "t"),
)

_P267 = _page(
    "methodcaller-use",
    267,
    "Calling the same method on each of them",
    "operator.methodcaller, which itemgetter and attrgetter left out.",
    "attrgetter reaches for an attribute; methodcaller calls a method, "
    "arguments and all, and hands you something you can pass to map or "
    "sorted. The second line here shows the arguments being carried "
    "along: methodcaller('replace', 'a', '-') is a function that "
    "replaces on whatever it is given. It is a lambda you did not have "
    "to write, and it says plainly which method is being called.",
    "methodcaller_use",
    [
        (
            "Import methodcaller from operator. Set words to ["
            + _seq(words)
            + "] and lower to methodcaller of 'lower'. Print a list of "
            "lower applied to each word. Then print methodcaller of "
            "'replace' with "
            + repr(from_)
            + " and "
            + repr(to)
            + ", called on "
            + repr(subject)
            + ".",
            {"words": words, "subject": subject, "from_": from_, "to": to},
        )
        for words, subject, from_, to in _CALLERS
    ],
)


# ── 268. A field kept out of the repr ────────────────────────

_FLAGS = (
    ("User", "ada", "token", ("secret1", "secret2")),
    ("Account", "sam", "password", ("hunter2", "hunter3")),
    ("Client", "kim", "key", ("abc123", "def456")),
    ("Session", "jo", "cookie", ("aaa", "bbb")),
    ("Login", "max", "hash", ("111", "222")),
    ("Node", "alpha", "cache", ("warm", "cold")),
    ("Job", "build", "log_path", ("/tmp/a", "/tmp/b")),
    ("Order", "first", "trace_id", ("t-1", "t-2")),
    ("Record", "row", "checksum", ("aa11", "bb22")),
    ("Entry", "note", "raw", ("x", "y")),
    ("Token", "issued", "value", ("v1", "v2")),
    ("Config", "prod", "secret", ("s1", "s2")),
)

_P268 = _page(
    "dataclass-field-flags",
    268,
    "A field kept out of the repr",
    "field(repr=False, compare=False), and why both matter.",
    "repr=False keeps a value out of the printed form, which is how you "
    "stop a token or a password appearing in every log line and error "
    "report - the commonest way secrets escape. compare=False keeps it "
    "out of the generated __eq__, so two of these count as equal even "
    "though their hidden values differ, which the second line shows. "
    "Think about whether that is what you mean: sometimes it is exactly "
    "right, and sometimes it hides a real difference.",
    "dataclass_field_flags",
    [
        (
            "Import dataclass and field from dataclasses. Write a "
            "dataclass "
            + cls
            + " with name hinted str and "
            + hidden
            + " hinted str set to field(repr=False, compare=False). Make "
            "first as "
            + cls
            + "("
            + repr(name)
            + ", "
            + repr(secrets[0])
            + ") and second with "
            + repr(secrets[1])
            + ". Print first, then whether first == second.",
            {
                "cls": cls,
                "name": name,
                "hidden": hidden,
                "secrets": secrets,
            },
        )
        for cls, name, hidden, secrets in _FLAGS
    ],
)


LAST_PAGES: tuple[Page, ...] = (
    _P259,
    _P260,
    _P261,
    _P262,
    _P263,
    _P264,
    _P265,
    _P266,
    _P267,
    _P268,
)
