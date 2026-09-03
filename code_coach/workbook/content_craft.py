"""Intermediate pages 179-188: checking your work, and the fixes.

Two pages on assert and on writing a test you call yourself, which is
roughly where code stops being hopeful and starts being checked.

Then the fixes for things earlier pages deliberately showed going wrong.
Page 113 made a shallow copy and watched both lists grow; deepcopy is
the answer. Page 111 shared one list between every call; default_factory
is the answer. Page 105 taught __str__ and left __repr__ out; here is
the difference and why a list of your objects prints the other one. And
an error raised inside an except loses where it came from unless you say
`from`.

Python only, same as 81-178.
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


# ── 179. A check that stops when it is wrong ─────────────────

_ASSERTS = (
    ("double", ("n",), "n * 2", ((3,), 6), 7, "double(3) should be 6"),
    ("square", ("n",), "n * n", ((4,), 16), 8, "square(4) should be 16"),
    ("add", ("a", "b"), "a + b", ((2, 3), 5), 6, "add(2, 3) should be 5"),
    ("times", ("a", "b"), "a * b", ((3, 4), 12), 7, "times(3, 4) should be 12"),
    ("half", ("n",), "n // 2", ((9,), 4), 5, "half(9) should be 4"),
    ("rest", ("n", "d"), "n % d", ((17, 5), 2), 3, "rest(17, 5) should be 2"),
    ("thrice", ("n",), "n * 3", ((5,), 15), 12, "thrice(5) should be 15"),
    ("less", ("n",), "n - 1", ((10,), 9), 10, "less(10) should be 9"),
    ("area", ("w", "h"), "w * h", ((3, 4), 12), 14, "area(3, 4) should be 12"),
    ("total", ("a", "b"), "a + b", ((10, 20), 30), 31, "total should be 30"),
    ("cube", ("n",), "n * n * n", ((3,), 27), 9, "cube(3) should be 27"),
    ("gap", ("a", "b"), "a - b", ((9, 4), 5), 6, "gap(9, 4) should be 5"),
)

_P179 = _page(
    "assert-use",
    179,
    "A check that stops when it is wrong",
    "assert, and the message that comes after the comma.",
    "assert says nothing at all when it is right, and stops the program "
    "when it is not - which is exactly the behaviour you want from a "
    "check. The part after the comma is the message, and writing a useful "
    "one is the whole difference between a failure you can read and one "
    "you have to go and investigate. One warning: Python throws asserts "
    "away entirely when run with -O, so they are for catching your own "
    "mistakes during development, never for checking a user's input.",
    "assert_use",
    [
        (
            "Write "
            + func
            + "("
            + ", ".join(params)
            + ") returning "
            + expr
            + ". Assert that calling it with "
            + ", ".join(repr(v) for v in good[0])
            + " equals "
            + repr(good[1])
            + ", then print "
            + repr(passed_msg)
            + ". Then in a try, assert the same call equals "
            + repr(wrong)
            + " with the message "
            + repr(message)
            + ", and print the caught problem.",
            {
                "func": func,
                "params": params,
                "expr": expr,
                "good": good,
                "wrong": wrong,
                "message": message,
                "passed": passed_msg,
            },
        )
        for func, params, expr, good, wrong, message in _ASSERTS
        for passed_msg in ("first check passed",)
    ],
)


# ── 180. A test you write and call yourself ──────────────────

_TESTS = (
    ("add", ("a", "b"), "a + b", (((2, 3), 5), ((0, 0), 0), ((-1, 1), 0))),
    ("times", ("a", "b"), "a * b", (((3, 4), 12), ((5, 0), 0), ((1, 9), 9))),
    ("double", ("n",), "n * 2", (((3,), 6), ((0,), 0), ((-4,), -8))),
    ("square", ("n",), "n * n", (((4,), 16), ((0,), 0), ((3,), 9))),
    ("half", ("n",), "n // 2", (((9,), 4), ((8,), 4), ((0,), 0))),
    ("rest", ("n", "d"), "n % d", (((17, 5), 2), ((20, 4), 0), ((7, 3), 1))),
    ("gap", ("a", "b"), "a - b", (((9, 4), 5), ((4, 9), -5), ((5, 5), 0))),
    ("area", ("w", "h"), "w * h", (((3, 4), 12), ((1, 1), 1), ((0, 7), 0))),
    ("cube", ("n",), "n * n * n", (((3,), 27), ((1,), 1), ((2,), 8))),
    ("bigger", ("a", "b"), "a if a > b else b", (((4, 9), 9), ((12, 3), 12), ((5, 5), 5))),
    ("thrice", ("n",), "n * 3", (((5,), 15), ((0,), 0), ((-2,), -6))),
    ("less", ("n",), "n - 1", (((10,), 9), ((1,), 0), ((0,), -1))),
)

_P180 = _page(
    "test-function",
    180,
    "A test you write and call yourself",
    "A function full of asserts, and what a test actually is.",
    "This is a real test. Not a smaller version of one, not a warm-up - a "
    "function whose name starts with test_, containing asserts, that "
    "fails loudly and says nothing when it passes. pytest and unittest "
    "add ways to find and run these and to report them nicely, but the "
    "thing being run is what you are writing here. Notice the cases "
    "chosen: an ordinary one, a zero, and a negative. Bugs live at the "
    "edges, not in the middle.",
    "test_function",
    [
        (
            "Write "
            + func
            + "("
            + ", ".join(params)
            + ") returning "
            + expr
            + ". Then write test_"
            + func
            + "() asserting "
            + ", ".join(
                f"{func}(" + ", ".join(repr(v) for v in got) + f") == {want!r}"
                for got, want in cases
            )
            + ". Call it, then print "
            + repr("test_" + func + " passed")
            + ".",
            {
                "func": func,
                "params": params,
                "expr": expr,
                "cases": cases,
                "passed": "test_" + func + " passed",
            },
        )
        for func, params, expr, cases in _TESTS
    ],
)


# ── 181. The two ways an object turns into text ──────────────

_REPRS = (
    ("Point", (("x", "int"), ("y", "int")), (2, 3), "({self.x}, {self.y})"),
    ("Size", (("width", "int"), ("height", "int")), (10, 4),
     "{self.width} by {self.height}"),
    ("Span", (("low", "int"), ("high", "int")), (3, 17),
     "{self.low}..{self.high}"),
    ("Pair", (("left", "int"), ("right", "int")), (7, 8),
     "{self.left} and {self.right}"),
    ("Room", (("floor", "int"), ("number", "int")), (3, 12),
     "floor {self.floor} room {self.number}"),
    ("Score", (("points", "int"), ("bonus", "int")), (40, 7),
     "{self.points} plus {self.bonus}"),
    ("Grid", (("rows", "int"), ("cols", "int")), (8, 9),
     "{self.rows}x{self.cols}"),
    ("Trip", (("miles", "int"), ("hours", "int")), (120, 3),
     "{self.miles} miles in {self.hours}"),
    ("Gap", (("start", "int"), ("end", "int")), (7, 31),
     "{self.start} to {self.end}"),
    ("Tank", (("full", "int"), ("used", "int")), (60, 22),
     "{self.used} of {self.full}"),
    ("Wall", (("bricks", "int"), ("rows", "int")), (90, 6),
     "{self.bricks} in {self.rows}"),
    ("Bill", (("price", "int"), ("people", "int")), (45, 3),
     "{self.price} split {self.people}"),
)

_P181 = _page(
    "repr-vs-str",
    181,
    "The two ways an object turns into text",
    "__str__ for people, __repr__ for you.",
    "__str__ is what print shows: whatever reads best. __repr__ is what "
    "you want when you are debugging - unambiguous, and ideally something "
    "you could paste back into Python. The line that catches people is "
    "the third one here: printing a list does not use __str__ on the "
    "items, it uses __repr__, so a list of objects with only __str__ "
    "defined is a screen of angle brackets and hex. Define __repr__ "
    "first; if you only ever write one, write that one.",
    "repr_vs_str",
    [
        (
            "Write a class "
            + cls
            + " storing "
            + " and ".join(n for n, _ in fields)
            + ", with a __str__ returning the f-string "
            + repr(shown)
            + " and a __repr__ returning an f-string like "
            + cls
            + "("
            + ", ".join(n + "=" for n, _ in fields)
            + ") with each value shown by !r. Make thing holding "
            + _seq(values)
            + ", then print thing, print repr of thing, and print a list "
            "holding thing.",
            {"cls": cls, "fields": fields, "values": values, "shown": shown},
        )
        for cls, fields, values, shown in _REPRS
    ],
)


# ── 182. The copy that goes all the way down ─────────────────

_DEEPS = (
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

_P182 = _page(
    "deepcopy-use",
    182,
    "The copy that goes all the way down",
    "copy.deepcopy, and what page 113 was missing.",
    "Page 113 made a copy of a list of lists, changed the inner list, and "
    "found both had changed - because the copy held the same inner list, "
    "not a copy of it. deepcopy is the fix: it copies every level, so "
    "nothing is shared. Run these and compare the two numbers. The reason "
    "it is not the default is that it is slower and can be surprising on "
    "big object graphs, so reach for it when you know you have nesting "
    "and know you want it separate.",
    "deepcopy_use",
    [
        (
            "Import deepcopy from copy. Set inner to ["
            + _seq(inner)
            + "] and outer to [inner]. Make shallow with list(outer) and "
            "deep with deepcopy(outer). Append "
            + repr(added)
            + " to inner, then print the length of shallow[0] and of "
            "deep[0].",
            {"inner": inner, "added": added},
        )
        for inner, added in _DEEPS
    ],
)


# ── 183. One generator handing on to another ─────────────────

_YIELDS = (
    ((1, 2), (3,)),
    ((1,), (2, 3)),
    ((10, 20), (30, 40)),
    ((5,), (6,)),
    ((1, 2, 3), (4,)),
    ((7, 8), (9, 10, 11)),
    ((0,), (1, 2)),
    ((100,), (200, 300)),
    ((2, 4), (6, 8)),
    ((11,), (22, 33)),
    ((1, 1), (2, 2)),
    ((9, 8), (7,)),
)

_P183 = _page(
    "yield-from",
    183,
    "One generator handing on to another",
    "yield from, instead of a loop that only forwards.",
    "Without it you write for n in firsts(): yield n, which is three "
    "words of ceremony around one idea. yield from says hand on "
    "everything that one produces, and it is how you build a generator "
    "out of smaller generators - walking a tree, chaining sources, "
    "flattening a level. It also passes values back the other way for "
    "generators that receive them, which you will not need for a long "
    "time and should know exists.",
    "yield_from",
    [
        (
            "Write firsts() yielding "
            + " and ".join(str(n) for n in first)
            + ", and seconds() yielding "
            + " and ".join(str(n) for n in second)
            + ". Write both() that yields from firsts() and then from "
            "seconds(). Loop over both() printing each value.",
            {"first": first, "second": second},
        )
        for first, second in _YIELDS
    ],
)


# ── 184. Runs of the same thing, once it is sorted ───────────

_GROUPS = (
    ("ant", "ape", "bee", "bat", "cow"),
    ("cat", "cow", "dog", "duck", "eel"),
    ("red", "rose", "blue", "black"),
    ("mint", "moss", "nut", "oak"),
    ("sun", "sky", "moon", "mist"),
    ("iron", "ice", "oak", "olive"),
    ("pear", "plum", "fig", "fern"),
    ("wolf", "wren", "yak", "yew"),
    ("east", "elm", "fern", "fig"),
    ("gold", "grey", "hill", "hawk"),
    ("lake", "lily", "moth", "mole"),
    ("tea", "toad", "urn", "user"),
)

_P184 = _page(
    "groupby-use",
    184,
    "Runs of the same thing, once it is sorted",
    "itertools.groupby, and the sort it quietly requires.",
    "groupby only groups things that are next to each other. Hand it "
    "unsorted data and you get several small groups with the same key "
    "instead of one big one, which is the single most common groupby bug "
    "and it fails silently. So the sort is not tidiness, it is required, "
    "and it must use the same key. Note also that each group is a "
    "one-shot iterator - list() it before moving on, or it is gone.",
    "groupby_use",
    [
        (
            "Import groupby from itertools. Set words to ["
            + _seq(words)
            + "], sort it with key=lambda w: w[0], then loop over groupby "
            "with the same key, printing the letter and list(group).",
            {"words": words},
        )
        for words in _GROUPS
    ],
)


# ── 185. A record that cannot be changed ─────────────────────

_FROZEN = (
    ("Box", ("a", "b"), 1),
    ("Crate", ("first", "second"), 2),
    ("Bag", ("red", "blue"), 7),
    ("Case", ("one", "two"), 3),
    ("Bin", ("left", "right"), 4),
    ("Tray", ("top", "bottom"), 5),
    ("Pack", ("north", "south"), 6),
    ("Cart", ("mon", "tue"), 8),
    ("Shelf", ("up", "down"), 9),
    ("Rack", ("in", "out"), 10),
    ("Drawer", ("front", "back"), 11),
    ("Chest", ("old", "new"), 12),
)

_P185 = _page(
    "frozen-dataclass",
    185,
    "A record that cannot be changed",
    "frozen=True, and field(default_factory=list).",
    "Two fixes in one page. default_factory calls list once per object, "
    "so each gets its own - which is the proper answer to page 111, and a "
    "plain items: list = [] in a dataclass is refused outright for "
    "exactly that reason. frozen=True stops assignment after building, so "
    "the object is a value rather than something that changes under you. "
    "Note what frozen does not do: the list inside is still a list, and "
    "appending to it works. Frozen is one level deep.",
    "frozen_dataclass",
    [
        (
            "Import dataclass and field from dataclasses. Write a "
            "dataclass "
            + cls
            + " with frozen=True, a field name hinted str and a field "
            "items hinted list defaulting to field(default_factory=list). "
            "Make first as "
            + cls
            + "("
            + repr(names[0])
            + ") and second as "
            + cls
            + "("
            + repr(names[1])
            + "), append "
            + repr(added)
            + " to first.items, then print the length of each one's "
            "items. Then in a try set first.name to "
            + repr(names[1])
            + " and print the type name of whatever it raises.",
            {"cls": cls, "names": names, "added": added},
        )
        for cls, names, added in _FROZEN
    ],
)


# ── 186. Text against the bytes it becomes ───────────────────

_BYTES = (
    "café",
    "naïve",
    "hello",
    "über",
    "façade",
    "jalapeño",
    "résumé",
    "piñata",
    "Zürich",
    "crème",
    "señor",
    "fiancée",
)

_P186 = _page(
    "bytes-use",
    186,
    "Text against the bytes it becomes",
    "encode and decode, and why the two lengths differ.",
    "A string is characters; a file or a socket carries bytes. encode "
    "turns one into the other and decode turns it back, and utf-8 is the "
    "answer to which encoding unless someone tells you otherwise. Every "
    "word here has an accented letter, so the two lengths come out "
    "different - one character, two bytes. That gap is the whole reason "
    "encodings exist, and the reason a program that assumes one byte per "
    "character breaks the moment it meets a name with an accent in it.",
    "bytes_use",
    [
        (
            "Set text to "
            + repr(word)
            + " and raw to text encoded as utf-8. Print the length of "
            "text, then the length of raw, then raw decoded back.",
            {"text": word},
        )
        for word in _BYTES
    ],
)


# ── 187. Noticing the lists were different lengths ───────────

_STRICTS = (
    ((1, 2, 3), (10, 20)),
    ((1, 2), (10, 20, 30)),
    ((5, 6, 7, 8), (50, 60)),
    ((1,), (10, 20)),
    ((9, 8), (90,)),
    ((1, 2, 3), (10,)),
    ((4, 5), (40, 50, 60)),
    ((7,), (70, 80, 90)),
    ((2, 4, 6), (20, 40)),
    ((3, 6), (30,)),
    ((1, 2, 3, 4), (10, 20, 30)),
    ((8, 9), (80, 90, 100)),
)

_P187 = _page(
    "zip-strict",
    187,
    "Noticing the lists were different lengths",
    "zip with strict=True, instead of silently stopping short.",
    "Plain zip stops at the shorter list and says nothing, which is "
    "sometimes what you want and is otherwise a bug that quietly drops "
    "your data. strict=True makes it raise instead. Watch the output: the "
    "pairs it managed print first, and the complaint comes after - zip "
    "does not look ahead, it discovers the problem when one side runs "
    "out. If the lists should be the same length, say so; if they should "
    "not, plain zip is honest.",
    "zip_strict",
    [
        (
            "Set first to ["
            + _seq(one)
            + "] and second to ["
            + _seq(two)
            + "]. In a try, loop over zip of the two with strict=True, "
            "unpacking into a and b and printing both. Catch ValueError "
            "and print "
            + repr("lengths differ")
            + ".",
            {"first": one, "second": two, "complaint": "lengths differ"},
        )
        for one, two in _STRICTS
    ],
)


# ── 188. A new error that remembers the old one ──────────────

_CHAINS = (
    ("ConfigError", "bad number", ("12", "abc")),
    ("SettingError", "not a count", ("7", "many")),
    ("InputError", "expected digits", ("100", "ten")),
    ("ParseError", "cannot read that", ("42", "x")),
    ("FieldError", "bad value", ("5", "five")),
    ("LoadError", "not numeric", ("88", "eighty")),
    ("ValueProblem", "unreadable", ("3", "three")),
    ("BadSetting", "wanted a number", ("60", "sixty")),
    ("ReadError", "no good", ("1", "one")),
    ("NumberError", "not a number", ("999", "lots")),
    ("EntryError", "bad entry", ("21", "twentyone!")),
    ("DataError", "bad data", ("8", "eight")),
)

_P188 = _page(
    "raise-from",
    188,
    "A new error that remembers the old one",
    "raise ... from, and __cause__.",
    "Catching a low-level error and raising your own is right - callers "
    "should not have to know you used int(). But raising a new one inside "
    "an except throws away where it came from unless you say from. With "
    "it, the original is kept on __cause__ and printed under a line "
    "saying 'The above exception was the direct cause', which is the "
    "difference between a traceback that explains itself and one that "
    "starts halfway through the story. Print __cause__'s type and see it "
    "is still there.",
    "raise_from",
    [
        (
            "Write an exception class "
            + error
            + " with just pass. Write load(value) returning int(value) in "
            "a try, and on ValueError raising "
            + error
            + "("
            + repr(message)
            + ") from the caught problem. Loop text over ["
            + _seq(values)
            + "], printing load(text) in a try, and in an except for "
            + error
            + " printing the problem and then the type name of its "
            "__cause__.",
            {"error": error, "message": message, "values": values},
        )
        for error, message, values in _CHAINS
    ],
)


CRAFT_PAGES: tuple[Page, ...] = (
    _P179,
    _P180,
    _P181,
    _P182,
    _P183,
    _P184,
    _P185,
    _P186,
    _P187,
    _P188,
)
