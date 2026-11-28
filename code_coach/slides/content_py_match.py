"""Pattern Matching and Enums: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 88

DECK = Deck(
    id="py-match",
    title="Pattern Matching and Enums",
    language="python",
    blurb="match/case from literals to class patterns, and enum for named constants (match needs Python 3.10+).",
    slides=(
        Slide(
            title="match and case basics",
            text="match looks at one value and runs the first case that fits it. It needs Python 3.10 or newer.",
            code=r"""cmd = "go"
match cmd:
    case "go":
        print("going")
    case "stop":
        print("stopping")""",
            output="going",
            point="match picks the first case whose pattern fits; the rest are skipped.",
        ),
        Slide(
            title="Literal patterns",
            text="A number, a string or None written in a case matches a value equal to it. If nothing matches, the match simply does nothing.",
            code=r"""def kind(x):
    match x:
        case 0:
            return "zero"
        case "hi":
            return "greeting"
        case None:
            return "nothing"
    return "other"
print(kind(0), kind("hi"), kind(None), kind(7))""",
            output="zero greeting nothing other",
            point="No case matched? Control just falls out of the match.",
        ),
        Slide(
            title="The wildcard _",
            text="The underscore matches anything and throws it away. Put it last as the 'otherwise' case.",
            code=r"""def reply(code):
    match code:
        case 200:
            return "ok"
        case 404:
            return "missing"
        case _:
            return "unknown"
print(reply(200), reply(404), reply(500))""",
            output="ok missing unknown",
            point="case _ is the else of a match.",
        ),
        Slide(
            title="Capture patterns",
            text="A plain name in a pattern matches anything and keeps the value under that name. Here a pair is split into x and y.",
            code=r"""point = (3, 4)
match point:
    case (0, 0):
        print("origin")
    case (x, y):
        print("x =", x, "y =", y)""",
            output="x = 3 y = 4",
            point="A bare name in a case is a capture, not a comparison.",
        ),
        Slide(
            title="OR patterns with |",
            text="Join several patterns with | and the case matches if any one of them fits.",
            code=r"""def kind(day):
    match day:
        case "sat" | "sun":
            return "weekend"
        case _:
            return "weekday"
print(kind("sun"), kind("mon"))""",
            output="weekend weekday",
            point="a | b means: either pattern will do.",
        ),
        Slide(
            title="Guards with if",
            text="Add an if after a pattern for an extra test. The case matches only when the pattern fits and the guard is true.",
            code=r"""def sign(n):
    match n:
        case 0:
            return "zero"
        case x if x < 0:
            return "negative"
        case _:
            return "positive"
print(sign(-5), sign(0), sign(8))""",
            output="negative zero positive",
            point="pattern if condition: both must hold.",
        ),
        Slide(
            title="Sequence patterns with *rest",
            text="A list pattern matches a list or tuple of that shape. A starred name soaks up the remaining items as a list.",
            code=r"""def head(items):
    match items:
        case []:
            return "empty"
        case [x]:
            return "one: " + str(x)
        case [first, *rest]:
            return str(first) + " then " + str(len(rest)) + " more"
print(head([]), head([7]), head([1, 2, 3]), sep="; ")""",
            output="empty; one: 7; 1 then 2 more",
            point="[first, *rest] splits a sequence into head and tail.",
        ),
        Slide(
            title="Mapping patterns",
            text="A dict pattern checks that the keys exist and pulls out values. Extra keys in the data are ignored.",
            code=r"""def show(d):
    match d:
        case {"type": "dog", "name": n}:
            return "dog " + n
        case {"type": t}:
            return "other " + t
    return "?"
print(show({"type": "dog", "name": "Rex", "age": 3}))
print(show({"type": "cat"}), show({}))""",
            output="dog Rex\nother cat ?",
            point="Mapping patterns match on the keys you name and ignore the rest.",
        ),
        Slide(
            title="Class patterns with a dataclass",
            text="Point(x=0, y=y) checks that the value is a Point and looks inside its fields. It reads very naturally with dataclasses.",
            code=r"""from dataclasses import dataclass
@dataclass
class Point:
    x: int
    y: int
match Point(0, 5):
    case Point(x=0, y=y):
        print("on the y axis at", y)
    case Point(x=x, y=y):
        print("elsewhere")""",
            output="on the y axis at 5",
            point="Class patterns test the type and the attributes at once.",
        ),
        Slide(
            title="Matching on type",
            text="A class name with empty brackets matches any value of that type. It is the match way to write isinstance.",
            code=r"""def describe(x):
    match x:
        case int():
            return "int"
        case str():
            return "str"
        case list():
            return "list"
    return "other"
print(describe(3), describe("a"), describe([1]), describe(2.5))""",
            output="int str list other",
            point="int() in a case means: is this an int?",
        ),
        Slide(
            title="Enum basics: name and value",
            text="An Enum is a fixed set of named constants. Each member has a name and a value, and you can look one up by either.",
            code=r"""from enum import Enum
class Color(Enum):
    RED = 1
    GREEN = 2
print(Color.RED)
print(Color.RED.name, Color.RED.value)
print(Color(2))
print(Color["GREEN"] is Color.GREEN)""",
            output="Color.RED\nRED 1\nColor.GREEN\nTrue",
            point="Color(2) looks up by value; Color['GREEN'] looks up by name.",
        ),
        Slide(
            title="Iterating an Enum",
            text="Looping over the Enum class gives every member in the order it was written. len() counts them.",
            code=r"""from enum import Enum
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
for c in Color:
    print(c.name, c.value)
print(len(Color), list(Color)[0])""",
            output="RED 1\nGREEN 2\nBLUE 3\n3 Color.RED",
            point="Iterate the class itself to visit all members.",
        ),
        Slide(
            title="auto() picks the values",
            text="When the values do not matter, auto() numbers the members 1, 2, 3 for you. A member is not equal to its plain number.",
            code=r"""from enum import Enum, auto
class Step(Enum):
    FIRST = auto()
    SECOND = auto()
    THIRD = auto()
print([s.value for s in Step])
print(Step.SECOND == Step.SECOND, Step.FIRST == 1)""",
            output="[1, 2, 3]\nTrue False",
            point="A plain Enum member never equals a bare number.",
        ),
        Slide(
            title="IntEnum and StrEnum",
            text="IntEnum members are real ints, so they compare with numbers. StrEnum members are real strings (StrEnum needs Python 3.11 or newer).",
            code=r"""from enum import IntEnum, StrEnum
class Level(IntEnum):
    LOW = 1
    HIGH = 3
class Mode(StrEnum):
    FAST = "fast"
print(Level.LOW < Level.HIGH, Level.HIGH == 3)
print(Mode.FAST == "fast", Mode.FAST.upper())""",
            output="True True\nTrue FAST",
            point="IntEnum and StrEnum behave like int and str but keep their names.",
        ),
        Slide(
            title="An Enum inside a match",
            text="Write enum members with their class name, like Light.RED, and match compares against them. A dotted name is a value, not a capture.",
            code=r"""from enum import Enum
class Light(Enum):
    RED = 1
    GREEN = 2
light = Light.GREEN
match light:
    case Light.RED:
        print("stop")
    case Light.GREEN:
        print("go")""",
            output="go",
            point="Use the dotted name Light.RED; a bare RED would capture.",
        ),
    ),
)
