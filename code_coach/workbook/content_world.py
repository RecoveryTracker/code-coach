"""Intermediate pages 159-168: files, dates, and the itertools shelf.

The first pages in this book where the program touches something outside
itself. Paths first, taken apart and built up, because a path is just a
value and treating it as one is most of what pathlib is for. Then a file
written and read back - inside a TemporaryDirectory, which is not a
teaching dodge but the right habit: it cleans up even when something
raises, and nothing lands in the folder you happened to run from.

Then dates, which are their own small world of traps, and four things
from the standard library that already do what you were about to write a
loop for.

Python only, same as 81-158.
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


# ── 159. A path taken apart ──────────────────────────────────

_PATHS = (
    "home/ada/notes.txt",
    "home/sam/report.pdf",
    "work/code/main.py",
    "work/code/tests.py",
    "music/bowie/heroes.mp3",
    "music/kate/hounds.flac",
    "photos/2026/trip.jpg",
    "photos/2025/garden.png",
    "docs/letters/bank.docx",
    "docs/notes/todo.md",
    "data/raw/readings.csv",
    "data/clean/readings.json",
)

_P159 = _page(
    "path-parts",
    159,
    "A path taken apart",
    "pathlib: name, suffix, stem and parent.",
    "A path is a value, not a string you chop up with split - that is the "
    "whole idea of pathlib. name is the last piece, suffix is the "
    "extension with its dot, stem is the name without it, and parent is "
    "everything above. Notice what parent prints: pathlib hands back your "
    "operating system's separator, so on Windows the slashes you typed "
    "come out as backslashes. It understood the path rather than storing "
    "your text.",
    "path_parts",
    [
        (
            "Import Path from pathlib. Set path to Path of "
            + repr(text)
            + ", then print its name, its suffix, its stem and its parent.",
            {"path": text},
        )
        for text in _PATHS
    ],
)


# ── 160. A path built with a slash ───────────────────────────

_BUILT = (
    ("home", "ada", "notes.txt"),
    ("home", "sam", "report.pdf"),
    ("work", "code", "main.py"),
    ("var", "log", "api.log"),
    ("music", "bowie", "heroes.mp3"),
    ("photos", "2026", "trip.jpg"),
    ("docs", "letters", "bank.docx"),
    ("data", "raw", "readings.csv"),
    ("src", "tests", "test_all.py"),
    ("backup", "monday", "dump.sql"),
    ("site", "static", "style.css"),
    ("build", "dist", "app.zip"),
)

_P160 = _page(
    "path-build",
    160,
    "A path built with a slash",
    "Joining paths with /, instead of gluing strings together.",
    "The slash operator is overloaded on Path objects, so folder / name "
    "reads exactly like the path it makes and gets the separator right on "
    "every operating system. This is the fix for the oldest bug in file "
    "handling: gluing strings and ending up with two slashes, or none. "
    "Only the left-hand side has to be a Path - after that, plain strings "
    "join on happily.",
    "path_build",
    [
        (
            "Import Path from pathlib. Build path as Path of "
            + repr(pieces[0])
            + " joined with / to "
            + " and then ".join(repr(p) for p in pieces[1:])
            + ". Print path, then its name, then its parent.",
            {"pieces": pieces},
        )
        for pieces in _BUILT
    ],
)


# ── 161. Writing a file and reading it back ──────────────────

_FILES = (
    ("notes.txt", ("hello", "world")),
    ("todo.txt", ("wash up", "write code")),
    ("names.txt", ("ada", "sam", "kim")),
    ("colours.txt", ("red", "green", "blue")),
    ("days.txt", ("mon", "tue")),
    ("cities.txt", ("kyoto", "oslo", "lima")),
    ("metals.txt", ("iron", "gold")),
    ("song.txt", ("alive", "heroes", "kooks")),
    ("fruit.txt", ("apple", "pear", "fig")),
    ("teams.txt", ("reds", "blues")),
    ("tools.txt", ("saw", "axe", "file")),
    ("words.txt", ("sky", "lake")),
)

_P161 = _page(
    "file-write-read",
    161,
    "Writing a file and reading it back",
    "write_text and read_text, inside a temporary directory.",
    "Two methods and no open, no close, no with - write_text and "
    "read_text do the whole thing for text that fits in memory, which is "
    "most text. The with around them is for the temporary directory, not "
    "the file: it makes a folder, hands you the name, and deletes the "
    "whole thing on the way out even if something raised. Get into this "
    "habit early. A program that scatters scratch files into whatever "
    "folder it was run from is a program someone will come to dislike.",
    "file_write_read",
    [
        (
            "Import tempfile and Path from pathlib. In a with over "
            "tempfile.TemporaryDirectory() as folder, set path to Path of "
            "folder / "
            + repr(name)
            + ", write the lines "
            + " and ".join(repr(line) for line in lines)
            + " to it each ending in a newline, then print the text read "
            "back and stripped, and whether the path exists.",
            {"name": name, "lines": lines},
        )
        for name, lines in _FILES
    ],
)


# ── 162. A file's lines, one at a time ───────────────────────

_LINE_FILES = (
    ("notes.txt", ("hello", "world"), "upper"),
    ("names.txt", ("ada", "sam"), "upper"),
    ("SHOUT.txt", ("LOUD", "NOISE"), "lower"),
    ("CAPS.txt", ("RED", "BLUE"), "lower"),
    ("cities.txt", ("kyoto", "oslo", "lima"), "upper"),
    ("metals.txt", ("iron", "gold"), "title"),
    ("fruit.txt", ("apple", "pear", "fig"), "title"),
    ("LOUD.txt", ("MON", "TUE"), "lower"),
    ("tools.txt", ("saw", "axe"), "upper"),
    ("teams.txt", ("reds", "blues"), "title"),
    ("words.txt", ("sky", "lake", "hill"), "upper"),
    ("BIG.txt", ("ONE", "TWO", "THREE"), "lower"),
)

_P162 = _page(
    "file-lines",
    162,
    "A file's lines, one at a time",
    "splitlines, and why it beats split on a newline.",
    "read_text gives you one long string; splitlines cuts it into the "
    "lines without leaving the newline characters attached, which is the "
    "difference between it and split. It also does not hand you a "
    "spurious empty last line the way splitting on a newline does when "
    "the file ends with one - and a text file should end with one. Small "
    "detail, and the source of a great deal of confusion about why "
    "there is an extra blank at the end.",
    "file_lines",
    [
        (
            "Import tempfile and Path from pathlib. In a with over "
            "tempfile.TemporaryDirectory() as folder, set path to Path of "
            "folder / "
            + repr(name)
            + " and write the lines "
            + " and ".join(repr(line) for line in lines)
            + " each ending in a newline. Then loop over the text read "
            "back and splitlines, printing each line with ."
            + method
            + "() called on it.",
            {"name": name, "lines": lines, "method": method},
        )
        for name, lines, method in _LINE_FILES
    ],
)


# ── 163. A date, and the ways to print it ────────────────────

_DATES = (
    ((2026, 9, 2), "%d/%m/%Y"),
    ((2026, 1, 1), "%d/%m/%Y"),
    ((1977, 1, 14), "%d/%m/%Y"),
    ((1985, 8, 16), "%d-%m-%Y"),
    ((2000, 12, 31), "%d-%m-%Y"),
    ((1969, 7, 20), "%Y%m%d"),
    ((2026, 3, 15), "%Y%m%d"),
    ((1843, 10, 1), "%m/%d/%Y"),
    ((2024, 2, 29), "%m/%d/%Y"),
    ((1990, 6, 5), "%Y.%m.%d"),
    ((2010, 11, 11), "%Y.%m.%d"),
    ((2026, 12, 25), "%d/%m/%y"),
)

_P163 = _page(
    "date-format",
    163,
    "A date, and the ways to print it",
    "date, isoformat, and strftime with a numeric pattern.",
    "isoformat gives you the one format the whole world agrees on - "
    "year, month, day, biggest first, which sorts correctly as plain "
    "text. That last part is why it is worth defaulting to. strftime "
    "gives you anything else, with %d %m %Y standing for the pieces. "
    "Every pattern here is numeric on purpose: %A and %B print the day "
    "and month by name, and the name they print depends on the machine's "
    "locale, which is a lovely way to get a bug you cannot reproduce.",
    "date_format",
    [
        (
            "Import date from datetime. Set day to date("
            + ", ".join(str(n) for n in parts)
            + "), then print its isoformat, then strftime with "
            + repr(spec)
            + ", then its year.",
            {"day": parts, "spec": spec},
        )
        for parts, spec in _DATES
    ],
)


# ── 164. Days between, and days ahead ────────────────────────

_DELTAS = (
    ((2026, 1, 1), (2026, 3, 15), 30),
    ((2026, 9, 2), (2026, 12, 25), 7),
    ((2024, 1, 1), (2024, 3, 1), 60),
    ((2025, 1, 1), (2025, 3, 1), 60),
    ((2026, 6, 1), (2026, 6, 30), 14),
    ((2000, 1, 1), (2000, 12, 31), 100),
    ((1977, 1, 14), (1977, 12, 25), 21),
    ((2026, 2, 1), (2026, 3, 1), 45),
    ((2026, 10, 1), (2027, 1, 1), 90),
    ((1985, 8, 16), (1986, 8, 16), 365),
    ((2026, 4, 10), (2026, 5, 10), 1),
    ((2026, 11, 5), (2026, 11, 30), 10),
)

_P164 = _page(
    "date-delta",
    164,
    "Days between, and days ahead",
    "Subtracting dates, and adding a timedelta.",
    "Two dates subtract into a timedelta, and asking it for .days gives "
    "you the count - no month lengths, no leap years, no arithmetic you "
    "have to get right. Adding a timedelta moves a date, and it rolls "
    "over the end of a month and the end of a year on its own. Two of "
    "these span a February: one leap, one not. Do not do this by hand, "
    "ever. People have been getting it wrong for fifty years.",
    "date_delta",
    [
        (
            "Import date and timedelta from datetime. Set start to date("
            + ", ".join(str(n) for n in start)
            + ") and end to date("
            + ", ".join(str(n) for n in end)
            + "). Print the days in end minus start, then the isoformat "
            "of start plus a timedelta of "
            + str(ahead)
            + " days.",
            {"start": start, "end": end, "ahead": ahead},
        )
        for start, end, ahead in _DELTAS
    ],
)


# ── 165. Several lists walked as one ─────────────────────────

_CHAINS = (
    ((1, 2), (3, 4)),
    ((10, 20, 30), (40,)),
    ((1,), (2, 3, 4)),
    ((5, 5), (5, 5)),
    ((7, 8, 9), (10, 11)),
    ((100,), (200, 300)),
    ((1, 3), (2, 4)),
    ((11, 12), (13, 14, 15)),
    ((0,), (1, 2)),
    ((21, 22, 23), (24,)),
    ((2, 4, 6), (8, 10)),
    ((99,), (98, 97)),
)

_P165 = _page(
    "chain-use",
    165,
    "Several lists walked as one",
    "itertools.chain, instead of adding lists together to loop them.",
    "chain hands back the items of one list and then the next, without "
    "building a joined list in memory - which matters when the lists are "
    "large and matters not at all when they are these. Reach for it when "
    "you want to loop over several things in a row; reach for + when you "
    "actually want a new list. Saying which one you meant is the point.",
    "chain_use",
    [
        (
            "Import chain from itertools. Set first to ["
            + _seq(a)
            + "] and second to ["
            + _seq(b)
            + "], then print list of chain over the two.",
            {"first": a, "second": b},
        )
        for a, b in _CHAINS
    ],
)


# ── 166. The running total, already written ──────────────────

_ACCUMULATES = (
    (1, 2, 3, 4),
    (10, 20, 30),
    (5, 5, 5, 5),
    (1, 1, 1, 1, 1),
    (2, 4, 6, 8),
    (100, 200, 300),
    (7, 3, 9),
    (1, 2, 4, 8, 16),
    (12, 8, 4),
    (3, 6, 9, 12),
    (50, 25, 25),
    (1, 10, 100, 1000),
)

_P166 = _page(
    "accumulate-use",
    166,
    "The running total, already written",
    "itertools.accumulate, which is page 42 in one call.",
    "Page 42 printed the total as it grew, with a variable outside the "
    "loop. accumulate is that, handed back as a sequence: the first item, "
    "then the first two added, then the first three. Useful whenever you "
    "want the shape of something over time - a balance, a distance, a "
    "cumulative count - rather than only where it ended up.",
    "accumulate_use",
    [
        (
            "Import accumulate from itertools. Set numbers to ["
            + _seq(items)
            + "], then print list of accumulate over it.",
            {"items": items},
        )
        for items in _ACCUMULATES
    ],
)


# ── 167. Every pair, without the nested loop ─────────────────

_COMBOS = (
    ((1, 2, 3), 2),
    ((1, 2, 3, 4), 2),
    ((5, 6, 7), 2),
    ((1, 2, 3, 4), 3),
    ((10, 20, 30), 2),
    ((1, 2, 3, 4, 5), 4),
    ((2, 4, 6), 2),
    ((7, 8, 9, 10), 3),
    ((1, 2), 2),
    ((3, 6, 9, 12), 2),
    ((11, 22, 33), 3),
    ((1, 2, 3, 4, 5), 2),
)

_P167 = _page(
    "combinations-use",
    167,
    "Every pair, without the nested loop",
    "itertools.combinations, and what it leaves out.",
    "A nested loop over the same list gives you every pair twice and "
    "every item paired with itself. combinations gives you each group "
    "once, in the order the items came, and never an item with itself - "
    "which is almost always what you meant by 'every pair'. Ask for 3 and "
    "you get every trio. The order is fixed and documented, so the output "
    "is something you can test against.",
    "combinations_use",
    [
        (
            "Import combinations from itertools. Set items to ["
            + _seq(items)
            + "], then print list of combinations of it taken "
            + str(take)
            + " at a time.",
            {"items": items, "take": take},
        )
        for items, take in _COMBOS
    ],
)


# ── 168. The top few, in order ───────────────────────────────

_COMMON = (
    (("ant", "bee", "ant", "cow", "ant", "bee"), 2),
    (("red", "red", "red", "blue", "blue", "green"), 2),
    (("a", "a", "a", "a", "b", "b", "c"), 3),
    (("mon", "mon", "mon", "tue", "tue", "wed"), 2),
    (("do", "do", "re", "re", "re", "mi"), 2),
    (("iron", "iron", "iron", "gold"), 2),
    (("up", "up", "up", "up", "down", "down", "left"), 3),
    (("salt", "salt", "pepper"), 2),
    (("cat", "cat", "cat", "dog", "dog", "fox"), 3),
    (("x", "x", "x", "x", "x", "y", "y", "z"), 3),
    (("north", "north", "south"), 2),
    (("one", "one", "one", "two", "two", "three"), 3),
)

_P168 = _page(
    "most-common-use",
    168,
    "The top few, in order",
    "Counter.most_common, for a ranking rather than a count.",
    "Page 119 counted; this ranks. most_common hands back pairs, "
    "commonest first, and a number limits it to the top few - which "
    "beats sorting the whole thing to look at three of it. One warning "
    "worth carrying: when two items tie, which comes first is not "
    "something you should rely on. Every page here is built without ties "
    "on purpose, and if your real data can tie, sort by count and then "
    "by name so the answer cannot wobble.",
    "most_common_use",
    [
        (
            "Import Counter from collections. Set words to ["
            + _seq(words)
            + "], make counts a Counter of it, then loop over "
            "counts.most_common("
            + str(top)
            + ") unpacking into word and many, printing both on one line.",
            {"words": words, "top": top},
        )
        for words, top in _COMMON
    ],
)


WORLD_PAGES: tuple[Page, ...] = (
    _P159,
    _P160,
    _P161,
    _P162,
    _P163,
    _P164,
    _P165,
    _P166,
    _P167,
    _P168,
)
