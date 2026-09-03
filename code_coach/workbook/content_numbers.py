"""Intermediate pages 189-198: numbers that lie, and the shapes of a design.

Arithmetic first, because the surprise is real and everybody meets it:
0.1 + 0.2 is not 0.3, and no amount of care in your code changes that.
Then Decimal, which is the answer whenever the numbers are money, and
the parts of math worth knowing. Then random, which is only useful once
you know that seeding it makes it repeat.

The rest is design. A base class that refuses to be built. A Protocol
that names a shape without demanding anyone inherit from it. A context
manager written as one decorated function rather than a class. Ordering
by two things in opposite directions. And the method resolution order
that decides which parent wins.

Python only, same as 81-188.
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


# ── 189. Arithmetic that misses by a hair ────────────────────

# Every pair checked to actually miss; the emitter raises if one lands
# exactly, because then the page would teach the opposite of what it says.
_FLOATS = (
    (0.1, 0.2, 0.3),
    (0.1, 1.3, 1.4),
    (0.1, 3.7, 3.8),
    (0.1, 5.8, 5.9),
    (0.1, 8.2, 8.3),
    (0.2, 3.7, 3.9),
    (0.3, 1.6, 1.9),
    (0.3, 8.8, 9.1),
    (0.4, 6.9, 7.3),
    (0.6, 8.7, 9.3),
    (0.8, 5.6, 6.4),
    (1.1, 3.7, 4.8),
)

_P189 = _page(
    "float-trap",
    189,
    "Arithmetic that misses by a hair",
    "Why 0.1 + 0.2 is not 0.3, and what to use instead of ==.",
    "This is not a bug in Python. A float is a binary fraction, and 0.1 "
    "cannot be written exactly in binary any more than a third can be "
    "written exactly in decimal - so the number stored is very slightly "
    "off, and adding two of them lands very slightly off. Every language "
    "with floats does this. The rule that follows is simple and "
    "absolute: never compare floats with ==. isclose asks whether they "
    "are near enough, which is the question you actually had.",
    "float_trap",
    [
        (
            "Import isclose from math. Set first to "
            + repr(one)
            + " and second to "
            + repr(two)
            + ". Print their sum, then whether the sum == "
            + repr(target)
            + ", then whether isclose says the sum and "
            + repr(target)
            + " are close.",
            {"first": one, "second": two, "target": target},
        )
        for one, two, target in _FLOATS
    ],
)


# ── 190. The numbers you use for money ───────────────────────

_DECIMALS = (
    ("0.1", "0.2", "0.3"),
    ("1.10", "2.20", "3.30"),
    ("0.10", "0.70", "0.80"),
    ("19.99", "0.01", "20.00"),
    ("0.30", "0.60", "0.90"),
    ("2.40", "1.50", "3.90"),
    ("0.20", "0.40", "0.60"),
    ("9.99", "0.11", "10.10"),
    ("4.10", "2.30", "6.40"),
    ("0.60", "8.70", "9.30"),
    ("12.34", "0.66", "13.00"),
    ("0.80", "5.60", "6.40"),
)

_P190 = _page(
    "decimal-money",
    190,
    "The numbers you use for money",
    "Decimal, built from strings, and why the string matters.",
    "Decimal stores digits the way you wrote them, so it adds the way "
    "you expect and the comparison that failed on page 189 succeeds "
    "here. The third line of each proves the point by doing the same sum "
    "in floats. Build it from a string, always - Decimal(0.1) copies the "
    "float's error in, which is the one way to get this wrong. Anything "
    "that is money, or that someone will audit, wants this type.",
    "decimal_money",
    [
        (
            "Import Decimal from decimal. Set first to Decimal of "
            + repr(one)
            + " and second to Decimal of "
            + repr(two)
            + ", both from strings. Print the sum, then whether it equals "
            "Decimal of "
            + repr(target)
            + ", then whether the same sum done in floats equals "
            + repr(float(target))
            + ".",
            {"first": one, "second": two, "target": target},
        )
        for one, two, target in _DECIMALS
    ],
)


# ── 191. Floor, ceil and the two square roots ────────────────

_MATHS = (
    (3.7, 16),
    (2.1, 25),
    (9.9, 10),
    (-1.5, 100),
    (0.4, 49),
    (7.5, 30),
    (12.01, 144),
    (-4.2, 2),
    (5.5, 81),
    (100.9, 1000),
    (0.001, 64),
    (-0.5, 7),
)

_P191 = _page(
    "math-basics",
    191,
    "Floor, ceil and the two square roots",
    "math.floor, math.ceil and math.isqrt.",
    "floor goes down and ceil goes up, and the thing to watch is what "
    "they do to negatives: floor(-1.5) is -2, not -1, because down means "
    "down. That is also why // on a negative surprises people - it "
    "floors. isqrt is the integer square root: it gives you a whole "
    "number and never a float, so there is no rounding error to worry "
    "about, which math.sqrt cannot promise.",
    "math_basics",
    [
        (
            "Import math. Set value to "
            + repr(value)
            + " and whole to "
            + repr(whole)
            + ". Print math.floor of value, then math.ceil of value, then "
            "math.isqrt of whole.",
            {"value": value, "whole": whole},
        )
        for value, whole in _MATHS
    ],
)


# ── 192. Random numbers that repeat on purpose ───────────────

_RANDOMS = (
    (1, 6, 5),
    (42, 10, 4),
    (7, 100, 3),
    (2026, 6, 6),
    (0, 20, 5),
    (99, 50, 4),
    (13, 6, 3),
    (5, 12, 6),
    (777, 100, 3),
    (314, 10, 5),
    (8, 8, 4),
    (2, 52, 5),
)

_P192 = _page(
    "random-seed",
    192,
    "Random numbers that repeat on purpose",
    "random.seed, and why a test can use random numbers at all.",
    "Seeding sets the starting point, and from the same start the same "
    "numbers come out - which sounds like it defeats the purpose and is "
    "in fact what makes random usable. A bug that only happens on some "
    "inputs is reproducible if you seeded; unreproducible if you did "
    "not. Both lists here are drawn after the same seed, so they match. "
    "One warning: this is fine for tests and games and wrong for "
    "anything security-related, where you want the secrets module.",
    "random_seed",
    [
        (
            "Import random. Seed it with "
            + repr(seed)
            + ", then build first as a list of "
            + str(many)
            + " randint(1, "
            + str(top)
            + ") values. Seed it with "
            + repr(seed)
            + " again and build second the same way. Print first, then "
            "whether first == second.",
            {"seed": seed, "top": top, "many": many},
        )
        for seed, top, many in _RANDOMS
    ],
)


# ── 193. A table that arrived as text ────────────────────────

_CSVS = (
    (("name", "score"), ("ada", 90), ("sam", 7)),
    (("city", "people"), ("kyoto", 1463), ("oslo", 709)),
    (("metal", "number"), ("iron", 26), ("gold", 79)),
    (("book", "pages"), ("dune", 412), ("ilium", 780)),
    (("day", "hours"), ("mon", 8), ("tue", 6)),
    (("team", "points"), ("reds", 41), ("blues", 12)),
    (("fruit", "count"), ("apple", 3), ("pear", 12)),
    (("tool", "weight"), ("saw", 3), ("axe", 8)),
    (("word", "length"), ("sky", 3), ("lake", 4)),
    (("room", "floor"), ("attic", 4), ("hall", 1)),
    (("song", "seconds"), ("alive", 245), ("kooks", 173)),
    (("colour", "count"), ("red", 12), ("blue", 9)),
)

_P193 = _page(
    "csv-read",
    193,
    "A table that arrived as text",
    "csv.DictReader, and why you do not split on commas yourself.",
    "Splitting on commas works right up until a field contains a comma "
    "inside quotes, and then it fails in a way that corrupts data "
    "quietly. The csv module knows the rules. DictReader takes the first "
    "row as the names and hands every row back as a dict, so you ask for "
    "columns by name instead of counting positions. io.StringIO lets a "
    "string stand in for a file, which is exactly how you test code that "
    "reads files without writing any.",
    "csv_read",
    [
        (
            "Import csv and io. Set text to the CSV lines "
            + " then ".join(
                repr(",".join(str(c) for c in row)) for row in rows
            )
            + ", each ending in a newline. Make a DictReader over "
            "io.StringIO of it, then loop the rows printing "
            + repr(rows[0][0])
            + " and "
            + repr(rows[0][1])
            + " on one line.",
            {"rows": rows},
        )
        for rows in _CSVS
    ],
)


# ── 194. A class that refuses to be built ────────────────────

_ABCS = (
    ("Shape", "Circle", "area", "round", "cannot build the base"),
    ("Animal", "Dog", "speak", "woof", "base refused"),
    ("Store", "Disk", "save", "saved", "no bare Store"),
    ("Reader", "FileReader", "read", "text", "abstract"),
    ("Sender", "Email", "send", "sent", "cannot build Sender"),
    ("Worker", "Baker", "work", "baking", "base refused"),
    ("Source", "Stream", "fetch", "data", "no bare Source"),
    ("Writer", "Console", "write", "written", "abstract"),
    ("Player", "Guitar", "play", "strum", "cannot build Player"),
    ("Engine", "Petrol", "start", "vroom", "base refused"),
    ("Payment", "Card", "charge", "charged", "no bare Payment"),
    ("Report", "Summary", "render", "rendered", "abstract"),
)

_P194 = _page(
    "abstract-base",
    194,
    "A class that refuses to be built",
    "ABC and @abstractmethod, and the TypeError you want.",
    "An abstract base says every subclass must provide this method, and "
    "Python enforces it: try to build the base itself, or a subclass "
    "that forgot the method, and you get a TypeError at that moment "
    "rather than an AttributeError somewhere far away later. That "
    "distance is the whole value. Use it when you genuinely have several "
    "implementations of one idea - and not for a base class with one "
    "subclass, which is just ceremony.",
    "abstract_base",
    [
        (
            "Import ABC and abstractmethod from abc. Write "
            + base
            + " inheriting ABC with an abstractmethod "
            + method
            + "(self). Write "
            + sub
            + " inheriting it, with "
            + method
            + " returning "
            + repr(answer)
            + ". Print the result of calling it on a "
            + sub
            + ". Then in a try build a bare "
            + base
            + ", catching TypeError and printing "
            + repr(refused)
            + ".",
            {
                "base": base,
                "sub": sub,
                "method": method,
                "answer": answer,
                "refused": refused,
            },
        )
        for base, sub, method, answer, refused in _ABCS
    ],
)


# ── 195. A shape named without inheritance ───────────────────

_PROTOCOLS = (
    ("Speaker", "speak", "Dog", "Cat", ("woof", "meow")),
    ("Named", "name_of", "Book", "Song", ("dune", "alive")),
    ("Greeter", "greet", "English", "French", ("hello", "bonjour")),
    ("Counter", "label", "One", "Two", ("first", "second")),
    ("Renderer", "render", "Text", "Html", ("plain", "marked up")),
    ("Loader", "load", "Disk", "Memory", ("from disk", "from memory")),
    ("Sizer", "size_of", "Small", "Large", ("small", "large")),
    ("Colour", "shade", "Red", "Blue", ("red", "blue")),
    ("Mover", "move", "Walk", "Run", ("walking", "running")),
    ("Signer", "sign", "Ink", "Digital", ("ink", "digital")),
    ("Cooker", "cook", "Bake", "Fry", ("baked", "fried")),
    ("Timer", "when", "Now", "Later", ("now", "later")),
)

_P195 = _page(
    "protocol-shape",
    195,
    "A shape named without inheritance",
    "typing.Protocol: structural typing, or duck typing written down.",
    "Page 194's base class demands that you inherit from it. A Protocol "
    "demands nothing - any class with a method of the right name and "
    "shape satisfies it, and neither class here mentions the Protocol at "
    "all. That is duck typing, which Python always had, finally written "
    "somewhere a type checker can read it. Note that nothing is enforced "
    "at runtime: the Protocol is a promise to your reader and your "
    "checker, and the program runs the same without it.",
    "protocol_shape",
    [
        (
            "Import Protocol from typing. Write a Protocol "
            + proto
            + " with "
            + method
            + "(self) -> str as its only member. Write "
            + first
            + " and "
            + second
            + ", neither inheriting anything, each with "
            + method
            + " returning "
            + repr(answers[0])
            + " and "
            + repr(answers[1])
            + ". Write speak(thing: "
            + proto
            + ") -> None printing the result, and call it with one of "
            "each.",
            {
                "proto": proto,
                "method": method,
                "first": first,
                "second": second,
                "answers": answers,
            },
        )
        for proto, method, first, second, answers in _PROTOCOLS
    ],
)


# ── 196. A context manager as one function ───────────────────

_CTXS = (
    ("opened", "open", "working", "close"),
    ("session", "start", "querying", "stop"),
    ("timer", "tick", "counting", "tock"),
    ("door", "opening", "inside", "closing"),
    ("job", "begin", "doing it", "end"),
    ("lock", "locked", "critical", "unlocked"),
    ("file_like", "opened file", "reading", "closed file"),
    ("trace", "enter", "middle", "exit"),
    ("bank", "connect", "transfer", "disconnect"),
    ("stage", "lights up", "the play", "lights down"),
    ("tunnel", "in", "through", "out"),
    ("kettle", "on", "boiling", "off"),
)

_P196 = _page(
    "contextmanager-fn",
    196,
    "A context manager as one function",
    "@contextmanager, and the yield that splits it in two.",
    "Page 116 wrote __enter__ and __exit__ on a class. This does the "
    "same job in one function: everything before the yield is the "
    "entering, everything after is the leaving, and the yield is where "
    "the with body runs. The try/finally around the yield is not "
    "optional decoration - without it, an error inside the with skips "
    "your cleanup entirely. Reach for this whenever the class would have "
    "held no state, which is most of the time.",
    "contextmanager_fn",
    [
        (
            "Import contextmanager from contextlib. Write "
            + name
            + "() decorated with it, printing "
            + repr(opening)
            + ", then in a try yielding, and in a finally printing "
            + repr(closing)
            + ". Use it in a with that prints "
            + repr(inside)
            + ".",
            {
                "name": name,
                "opening": opening,
                "inside": inside,
                "closing": closing,
            },
        )
        for name, opening, inside, closing in _CTXS
    ],
)


# ── 197. Ordering by two things, opposite directions ─────────

_TWO_WAYS = (
    ((("ada", 90), ("sam", 90), ("kim", 41)),),
    ((("red", 12), ("blue", 12), ("green", 30)),),
    ((("mon", 8), ("tue", 8), ("wed", 3)),),
    ((("iron", 26), ("gold", 26), ("tin", 50)),),
    ((("apple", 3), ("pear", 12), ("fig", 3)),),
    ((("north", 6), ("south", 6), ("east", 1)),),
    ((("do", 5), ("re", 9), ("mi", 5)),),
    ((("saw", 3), ("axe", 8), ("file", 3)),),
    ((("reds", 41), ("blues", 41), ("greens", 12)),),
    ((("sky", 3), ("sea", 3), ("sun", 9)),),
    ((("one", 1), ("two", 2), ("six", 2)),),
    ((("alpha", 7), ("beta", 7), ("gamma", 7)),),
)

_P197 = _page(
    "sort-two-ways",
    197,
    "Ordering by two things, opposite directions",
    "A tuple key with a minus on one half.",
    "reverse=True turns the whole sort around, which is no good when you "
    "want the score highest-first but the names still A to Z. Negating "
    "the number does it: -score sorts descending while name stays "
    "ascending, in one key. Every page here has a tie on the number so "
    "you can watch the name break it. The trick only works on numbers - "
    "for text going the other way you need two passes, relying on the "
    "sort being stable.",
    "sort_two_ways",
    [
        (
            "Set rows to ["
            + ", ".join(f"({n!r}, {v!r})" for n, v in rows)
            + "]. Loop over sorted of rows with key=lambda r: (-r[1], "
            "r[0]), unpacking into name and score, and print both on one "
            "line.",
            {"rows": rows},
        )
        for (rows,) in _TWO_WAYS
    ],
)


# ── 198. Which parent wins ───────────────────────────────────

_MROS = (
    ("Base", "Left", "Right", "Both"),
    ("Animal", "Swimmer", "Flyer", "Duck"),
    ("Thing", "Red", "Blue", "Purple"),
    ("Shape", "Round", "Flat", "Disc"),
    ("Store", "Cached", "Remote", "Client"),
    ("Node", "Named", "Sized", "Item"),
    ("Worker", "Fast", "Careful", "Good"),
    ("Source", "Local", "Network", "Mixed"),
    ("Writer", "Buffered", "Timed", "Logger"),
    ("Engine", "Petrol", "Electric", "Hybrid"),
    ("Reader", "Text", "Binary", "Universal"),
    ("Sender", "Email", "Sms", "Notifier"),
)

_P198 = _page(
    "mro-order",
    198,
    "Which parent wins",
    "__mro__, and the order Python looks in.",
    "With two parents, which one provides a method both define? Python "
    "answers with the method resolution order - the exact list it walks, "
    "and you can print it. Read the output: the class itself, then the "
    "first parent, then the second, then the shared grandparent, then "
    "object. Left to right, and never a class before something it "
    "inherits from. This is what super() actually follows, which is why "
    "super() is not the same as 'my parent' once more than one is "
    "involved.",
    "mro_order",
    [
        (
            "Write "
            + top
            + " with pass, then "
            + left
            + " and "
            + right
            + " both inheriting it, then "
            + bottom
            + " inheriting "
            + left
            + " and "
            + right
            + " in that order. Print a list of the __name__ of every class "
            "in "
            + bottom
            + ".__mro__.",
            {"top": top, "left": left, "right": right, "bottom": bottom},
        )
        for top, left, right, bottom in _MROS
    ],
)


NUMBER_PAGES: tuple[Page, ...] = (
    _P189,
    _P190,
    _P191,
    _P192,
    _P193,
    _P194,
    _P195,
    _P196,
    _P197,
    _P198,
)
