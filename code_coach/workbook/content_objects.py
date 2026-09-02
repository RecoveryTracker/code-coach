"""Intermediate pages 101-110: objects.

The first thing in this book that is neither a value nor a function. A class
is a shape for making things, and the thing it makes carries its own data
with it — which is what lets a program stop passing six variables around
together and start passing one.

Ten pages, in the order the ideas need each other: hold data, hold it twice,
give it behaviour, let the behaviour take an argument, decide what it looks
like printed, get most of that written for you, share one value across all of
them, start from another class, replace what you inherited, extend it
instead.

Python only, same as 81-100.
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


def _fields(pairs) -> str:
    return " and ".join(f"{f} of {v!r}" for f, v in pairs)


# ── 101. A thing that holds its own data ─────────────────────

_INITS = (
    ("Dog", (("name", "rex"), ("age", 3)), ["name", "age"]),
    ("Book", (("title", "dune"), ("pages", 412)), ["title", "pages"]),
    ("Point", (("x", 3), ("y", 8)), ["x", "y"]),
    ("User", (("name", "ann"), ("id", 17)), ["name"]),
    ("Box", (("width", 4), ("height", 9)), ["height", "width"]),
    ("Song", (("title", "one"), ("seconds", 210)), ["seconds"]),
    ("City", (("name", "leeds"), ("people", 800000)), ["name", "people"]),
    ("Card", (("suit", "hearts"), ("rank", 7)), ["rank", "suit"]),
    ("Score", (("player", "bo"), ("points", 42)), ["points"]),
    ("File", (("name", "notes"), ("size", 1024)), ["name", "size"]),
    ("Colour", (("name", "red"), ("code", 255)), ["code"]),
    ("Room", (("number", 12), ("beds", 2)), ["number", "beds"]),
)

_P101 = _page(
    "class-init",
    101,
    "A thing that holds its own data",
    "A class, and the __init__ that fills one in.",
    "self is the object being built, and every self.x = x line is the object "
    "keeping that value for later. The name self is not magic — it is just "
    "the first parameter, and it is called self because everyone calls it "
    "self. Note that __init__ is never called by name; making the object "
    "calls it.",
    "class_init",
    [
        (
            f"Write a class called {cls} whose __init__ takes and stores "
            + " and ".join(f for f, _ in fields)
            + f". Make one with {_fields(fields)}, then print its "
            + " and then its ".join(reads)
            + ".",
            {"cls": cls, "fields": list(fields), "reads": reads},
        )
        for cls, fields, reads in _INITS
    ],
)


# ── 102. Two of them ─────────────────────────────────────────

_TWOS = (
    ("Dog", ["name", "age"], ["rex", 3], ["fido", 7], [(0, "name"), (1, "name")]),
    ("Point", ["x", "y"], [1, 2], [10, 20], [(0, "x"), (1, "x")]),
    ("User", ["name", "id"], ["ann", 1], ["bob", 2], [(0, "id"), (1, "id")]),
    ("Box", ["w", "h"], [3, 4], [30, 40], [(0, "w"), (1, "h")]),
    ("Card", ["suit", "rank"], ["hearts", 7], ["spades", 12], [(1, "suit"), (0, "rank")]),
    ("Song", ["title", "secs"], ["one", 200], ["two", 300], [(0, "title"), (1, "secs")]),
    ("City", ["name", "people"], ["leeds", 800], ["york", 200], [(1, "name"), (1, "people")]),
    ("Score", ["who", "points"], ["bo", 42], ["cy", 17], [(0, "points"), (1, "points")]),
    ("File", ["name", "size"], ["a", 100], ["b", 200], [(0, "name"), (1, "name"), (0, "size")]),
    ("Room", ["number", "beds"], [12, 2], [13, 1], [(0, "beds"), (1, "beds")]),
    ("Colour", ["name", "code"], ["red", 255], ["blue", 16], [(0, "code"), (1, "code")]),
    ("Book", ["title", "pages"], ["dune", 412], ["ubik", 224], [(1, "title"), (0, "pages")]),
)

_P102 = _page(
    "class-two",
    102,
    "Two of them",
    "Two objects from one class, each holding its own values.",
    "The class is written once and makes as many as you like, and what each "
    "one holds is nothing to do with the others. That is the whole reason "
    "this is worth the ceremony — a function cannot remember anything "
    "between calls, and an object is a thing that can.",
    "class_two",
    [
        (
            f"Write a class called {cls} whose __init__ takes and stores "
            + " and ".join(fields)
            + f". Make one with {', '.join(repr(v) for v in v1)} and another "
            f"with {', '.join(repr(v) for v in v2)}. Then print "
            + ", then ".join(
                f"the {'first' if which == 0 else 'second'} one's {f}"
                for which, f in reads
            )
            + ".",
            {
                "cls": cls,
                "fields": fields,
                "values1": v1,
                "values2": v2,
                "reads": reads,
            },
        )
        for cls, fields, v1, v2, reads in _TWOS
    ],
)


# ── 103. Behaviour that belongs to it ────────────────────────

_METHODS = (
    ("Square", (("side", 4),), "area", "side * side", "its area"),
    ("Box", (("w", 3), ("h", 7)), "area", "w * h", "its area"),
    ("Point", (("x", 3), ("y", 4)), "total", "x + y", "x plus y"),
    ("Bag", (("count", 12),), "doubled", "count * 2", "twice the count"),
    ("Rect", (("w", 10), ("h", 4)), "perimeter", "w * 2 + h * 2", "its perimeter"),
    ("Timer", (("seconds", 185),), "minutes", "seconds // 60", "whole minutes"),
    ("Score", (("points", 47),), "tens", "points // 10", "how many tens"),
    ("Cube", (("side", 3),), "volume", "side * side * side", "its volume"),
    ("Pair", (("a", 20), ("b", 8)), "gap", "a - b", "a minus b"),
    ("Basket", (("apples", 7), ("pears", 5)), "total", "apples + pears", "the total fruit"),
    ("Clock", (("minutes", 135),), "spare", "minutes % 60", "the spare minutes"),
    ("Line", (("length", 9),), "half", "length // 2", "half its length"),
)

_P103 = _page(
    "class-method",
    103,
    "Behaviour that belongs to it",
    "A method: a function inside the class, that can see self.",
    "The method takes self and nothing else, and gets at the data through "
    "it. That is the difference from a plain function: it does not need to "
    "be handed the values, because the object it was called on already has "
    "them. Forgetting self in the definition is the error you will meet "
    "most.",
    "class_method",
    [
        (
            f"Write a class called {cls} whose __init__ takes and stores "
            + " and ".join(f for f, _ in fields)
            + f", and a method called {method} returning {described}. Make "
            f"one with {_fields(fields)} and print the result of calling "
            f"{method}.",
            {"cls": cls, "fields": list(fields), "method": method, "expr": expr},
        )
        for cls, fields, method, expr, described in _METHODS
    ],
)


# ── 104. A method you hand something to ──────────────────────

_METHOD_ARGS = (
    ("Counter", (("count", 10),), "add", "n", "count + n", "the count plus n", [5, 90]),
    ("Box", (("size", 4),), "grow", "n", "size * n", "the size times n", [2, 10]),
    ("Score", (("points", 50),), "lose", "n", "points - n", "the points minus n", [10, 50]),
    ("Bag", (("items", 7),), "pack", "n", "items + n", "the items plus n", [3, 0]),
    ("Wall", (("height", 12),), "stack", "n", "height * n", "the height times n", [2, 5]),
    ("Clock", (("minutes", 90),), "after", "n", "minutes + n", "the minutes plus n", [30, 90]),
    ("Line", (("length", 100),), "cut", "n", "length // n", "the length divided by n", [4, 10]),
    ("Pot", (("amount", 25),), "share", "n", "amount % n", "the remainder over n", [4, 7]),
    ("Row", (("seats", 8),), "rows", "n", "seats * n", "the seats times n", [3, 12]),
    ("Tank", (("litres", 60),), "use", "n", "litres - n", "the litres minus n", [15, 60]),
    ("Step", (("size", 3),), "times", "n", "size * n + size", "size times n, plus size", [4, 1]),
    ("Cash", (("pounds", 200),), "split", "n", "pounds // n", "the pounds divided by n", [5, 8]),
)

_P104 = _page(
    "class-method-arg",
    104,
    "A method you hand something to",
    "A method with a parameter of its own, alongside self.",
    "self comes first and everything else after it, and the caller only "
    "passes the everything else — Python fills self in from the object you "
    "called it on. Each of these is called twice, so the object's own value "
    "stays put while what you hand it changes.",
    "class_method_arg",
    [
        (
            f"Write a class called {cls} whose __init__ takes and stores "
            + " and ".join(f for f, _ in fields)
            + f", and a method called {method} taking {param} and returning "
            f"{described}. Make one with {_fields(fields)}, then print the "
            f"result of calling {method} with "
            + " and then ".join(str(v) for v in calls)
            + ".",
            {
                "cls": cls,
                "fields": list(fields),
                "method": method,
                "param": param,
                "expr": expr,
                "calls": calls,
            },
        )
        for cls, fields, method, param, expr, described, calls in _METHOD_ARGS
    ],
)


# ── 105. What it looks like printed ──────────────────────────

_REPRS = (
    ("Point", (("x", 1), ("y", 2))),
    ("Point", (("x", 30), ("y", 40))),
    ("Pair", (("a", 7), ("b", 9))),
    ("Size", (("w", 100), ("h", 250))),
    ("Card", (("rank", 7), ("suit", 3))),
    ("Range", (("lo", 0), ("hi", 99))),
    ("Cell", (("row", 2), ("col", 5))),
    ("Score", (("home", 3), ("away", 1))),
    ("Time", (("hours", 14), ("minutes", 30))),
    ("Vec", (("x", -1), ("y", 4))),
    ("Slot", (("index", 12), ("count", 3))),
    ("Gap", (("start", 5), ("end", 11))),
)

_P105 = _page(
    "class-repr",
    105,
    "What it looks like printed",
    "__repr__, so printing the object says something useful.",
    "Without it, printing an object gives you its class and a memory "
    "address, which tells you nothing you wanted to know. __repr__ is what "
    "print falls back to, and the convention is to make it look like the "
    "code that would build the thing — so you can read it and know exactly "
    "what you have.",
    "class_repr",
    [
        (
            f"Write a class called {cls} whose __init__ takes and stores "
            + " and ".join(f for f, _ in fields)
            + f", and a __repr__ returning it in the form {cls}(first, "
            f"second). Make one with {_fields(fields)} and print it.",
            {"cls": cls, "fields": list(fields)},
        )
        for cls, fields in _REPRS
    ],
)


# ── 106. Most of it written for you ──────────────────────────

_DATACLASSES = (
    ("Point", (("x", "int", 1), ("y", "int", 2))),
    ("User", (("name", "str", "ann"), ("id", "int", 7))),
    ("Box", (("width", "int", 30), ("height", "int", 12))),
    ("Card", (("suit", "str", "hearts"), ("rank", "int", 7))),
    ("Song", (("title", "str", "one"), ("seconds", "int", 210))),
    ("Cell", (("row", "int", 2), ("col", "int", 5))),
    ("Book", (("title", "str", "dune"), ("pages", "int", 412))),
    ("Score", (("home", "int", 3), ("away", "int", 1))),
    ("File", (("name", "str", "notes"), ("size", "int", 1024))),
    ("Room", (("number", "int", 12), ("beds", "int", 2))),
    ("Colour", (("name", "str", "red"), ("code", "int", 255))),
    ("Range", (("lo", "int", 0), ("hi", "int", 99))),
)

_P106 = _page(
    "dataclass",
    106,
    "Most of it written for you",
    "@dataclass: the __init__ and the __repr__, for free.",
    "Exactly page 101 and page 105 in four lines. The types are annotations "
    "and Python does not enforce them — they are there so the decorator "
    "knows what the fields are, and so a reader knows what you meant. Note "
    "the repr you get names the fields, which the hand-written one on page "
    "105 did not.",
    "dataclass_use",
    [
        (
            f"Using @dataclass, write a class called {cls} with fields "
            + " and ".join(f"{f}: {t}" for f, t, _ in fields)
            + ". Make one with "
            + " and ".join(repr(v) for _, _, v in fields)
            + " and print it.",
            {"cls": cls, "fields": list(fields)},
        )
        for cls, fields in _DATACLASSES
    ],
)


# ── 107. One value they all share ────────────────────────────

_SHARED = (
    ("Dog", ("kind", "dog"), "name", ["rex", "fido"]),
    ("Circle", ("sides", 0), "radius", [3, 10]),
    ("User", ("role", "member"), "name", ["ann", "bob"]),
    ("Square", ("sides", 4), "side", [2, 5]),
    ("Card", ("deck", "standard"), "rank", [7, 12]),
    ("Room", ("floor", 2), "number", [12, 13]),
    ("Song", ("format", "mp3"), "title", ["one", "two"]),
    ("Bag", ("colour", "brown"), "items", [3, 9]),
    ("Point", ("dims", 2), "x", [1, 100]),
    ("File", ("system", "ntfs"), "name", ["a", "b"]),
    ("Coin", ("currency", "gbp"), "value", [1, 50]),
    ("Tree", ("kingdom", "plant"), "height", [5, 20]),
)

_P107 = _page(
    "class-attr",
    107,
    "One value they all share",
    "A class attribute: written once, seen by every instance.",
    "It sits directly under the class rather than inside __init__, and every "
    "object gets the same one. Useful for things that are true of the class "
    "rather than the object — and a trap if you ever put a list there, "
    "because then all of them share the same list.",
    "class_attr",
    [
        (
            f"Write a class called {cls} with a class attribute {shared} set "
            f"to {shared_value!r}, and an __init__ taking and storing "
            f"{field}. Make one with {values[0]!r} and another with "
            f"{values[1]!r}. Print each one's {shared}, then each one's "
            f"{field}.",
            {
                "cls": cls,
                "shared": (shared, shared_value),
                "field": field,
                "values": values,
            },
        )
        for cls, (shared, shared_value), field, values in _SHARED
    ],
)


# ── 108. Starting from another class ─────────────────────────

_INHERITS = (
    ("Animal", "Dog", "name", "rex", "describe", "an animal called "),
    ("Shape", "Square", "name", "box", "label", "a shape called "),
    ("User", "Admin", "name", "ann", "greet", "hello, "),
    ("Vehicle", "Car", "model", "mini", "describe", "a vehicle: "),
    ("Item", "Book", "title", "dune", "label", "item: "),
    ("Person", "Student", "name", "bo", "greet", "hi there, "),
    ("Node", "Leaf", "tag", "root", "show", "node "),
    ("File", "Image", "name", "photo", "describe", "a file called "),
    ("Event", "Concert", "title", "one", "label", "event: "),
    ("Place", "City", "name", "leeds", "describe", "a place called "),
    ("Tool", "Hammer", "name", "big", "label", "tool: "),
    ("Message", "Email", "text", "hello", "show", "message: "),
)

_P108 = _page(
    "inherit-use",
    108,
    "Starting from another class",
    "A subclass, and the fact that it gets everything already there.",
    "The subclass body is the word pass and nothing else, and it still has "
    "the __init__ and the method — because it inherited them. That is worth "
    "seeing on its own before anything overrides anything: inheriting is the "
    "default, and changing something is the exception.",
    "inherit_use",
    [
        (
            f"Write a class called {base} whose __init__ takes and stores "
            f"{field}, and a method {method} returning \"{prefix}\" followed "
            f"by the {field}. Then write a class {sub} that inherits from "
            f"{base} and adds nothing. Make a {sub} with {value!r}, then "
            f"print its {field} and the result of calling {method}.",
            {
                "base": base,
                "sub": sub,
                "field": field,
                "value": value,
                "method": method,
                "prefix": prefix,
            },
        )
        for base, sub, field, value, method, prefix in _INHERITS
    ],
)


# ── 109. Replacing what you inherited ────────────────────────

_OVERRIDES = (
    ("Animal", "Dog", "sound", "...", "woof"),
    ("Animal", "Cat", "sound", "...", "meow"),
    ("Shape", "Square", "sides", "unknown", "four"),
    ("User", "Admin", "role", "member", "admin"),
    ("Vehicle", "Car", "wheels", "some", "four"),
    ("Greeter", "Friend", "greet", "hello", "hey"),
    ("Item", "Book", "kind", "thing", "book"),
    ("Node", "Leaf", "kind", "node", "leaf"),
    ("File", "Image", "kind", "file", "image"),
    ("Payment", "Card", "method", "unknown", "card"),
    ("Message", "Email", "channel", "none", "email"),
    ("Store", "Cache", "speed", "normal", "fast"),
)

_P109 = _page(
    "override",
    109,
    "Replacing what you inherited",
    "Writing a method the parent already has.",
    "Same name, different body, and the subclass's wins for its own "
    "objects. The parent is untouched — both are printed here so you can see "
    "that overriding replaces it for the child only, and nothing has been "
    "edited anywhere else.",
    "override",
    [
        (
            f"Write a class {base} with a method {method} returning "
            f'"{base_says}". Write a class {sub} that inherits from {base} '
            f'and replaces {method} to return "{sub_says}". Print the result '
            f"of calling {method} on a {base}, then on a {sub}.",
            {
                "base": base,
                "sub": sub,
                "method": method,
                "base_says": base_says,
                "sub_says": sub_says,
            },
        )
        for base, sub, method, base_says, sub_says in _OVERRIDES
    ],
)


# ── 110. Extending rather than replacing ─────────────────────

_SUPERS = (
    ("Animal", "Dog", "name", "breed", ["rex", "collie"]),
    ("Shape", "Rect", "name", "sides", ["box", 4]),
    ("User", "Admin", "name", "level", ["ann", 9]),
    ("Vehicle", "Car", "model", "doors", ["mini", 3]),
    ("Item", "Book", "title", "pages", ["dune", 412]),
    ("Person", "Student", "name", "year", ["bo", 2]),
    ("File", "Image", "name", "width", ["photo", 800]),
    ("Event", "Concert", "title", "seats", ["one", 500]),
    ("Place", "City", "name", "people", ["leeds", 800000]),
    ("Tool", "Drill", "name", "speed", ["big", 3000]),
    ("Message", "Email", "text", "subject", ["hello", "hi"]),
    ("Node", "Leaf", "tag", "depth", ["root", 7]),
)

_P110 = _page(
    "super-call",
    110,
    "Extending rather than replacing",
    "super(), when the parent's __init__ still needs to run.",
    "The subclass takes more arguments than the parent and hands the "
    "parent's along. Leave the super() line out and the parent's field is "
    "simply never set — the object looks fine until something asks for it. "
    "That is the bug this line exists to prevent, and it is silent.",
    "super_call",
    [
        (
            f"Write a class {base} whose __init__ takes and stores "
            f"{base_field}. Write a class {sub} that inherits from it, takes "
            f"{base_field} and {sub_field}, passes {base_field} up with "
            f"super(), and stores {sub_field} itself. Make a {sub} with "
            f"{values[0]!r} and {values[1]!r}, then print its {base_field} "
            f"and its {sub_field}.",
            {
                "base": base,
                "sub": sub,
                "base_field": base_field,
                "sub_field": sub_field,
                "values": values,
            },
        )
        for base, sub, base_field, sub_field, values in _SUPERS
    ],
)


OBJECT_PAGES: tuple[Page, ...] = (
    _P101,
    _P102,
    _P103,
    _P104,
    _P105,
    _P106,
    _P107,
    _P108,
    _P109,
    _P110,
)
