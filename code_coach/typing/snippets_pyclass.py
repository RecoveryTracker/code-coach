"""Python classes and types: the lines a well-built object is made of.

The lines are the parts of a class people actually write: __init__ and
self, dataclasses with defaults and field(), frozen and ordered ones,
properties and setters, classmethods and staticmethods, the dunder methods
that make an object print, compare, add and iterate, inheritance and
super(), abstract base classes, Protocols, Enums, and type hints in the
spelling of Python 3.12 - generics, unions, TypedDict, Literal and Self.

The blocks are whole small classes that print what they do, and the tests
run every one in the real interpreter and hold what it prints to an answer
worked out by hand.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

PYCLASS_LINES: tuple[Passage, ...] = (
    # plain classes
    _s("class BankAccount:", "a class, with nothing inherited but object"),
    _s("def __init__(self, owner: str, balance: int = 0) -> None:", "the constructor"),
    _s("self.owner = owner", "an attribute on this one object"),
    _s("self._balance = balance", "the underscore: private by agreement"),
    _s("def deposit(self, amount: int) -> None:", "a method changes its own object"),
    _s("if amount <= 0: raise ValueError(\"amount must be positive\")", "guarding input"),
    _s("instances: ClassVar[int] = 0", "shared by every instance, not one each"),
    # dataclasses
    _s("from dataclasses import dataclass, field", "the decorator and its helper"),
    _s("@dataclass(frozen=True, slots=True, kw_only=True)", "immutable, lighter, keywords only"),
    _s("@dataclass(order=True)", "writes <, <=, > and >= from the fields"),
    _s("labels: list[str] = field(default_factory=list)", "a fresh list for each one"),
    _s("id: int = field(compare=False, repr=False)", "left out of == and of printing"),
    _s("def __post_init__(self) -> None:", "runs after the generated __init__"),
    _s("moved = dataclasses.replace(point, x=10)", "a copy with one field changed"),
    _s("as_dict = dataclasses.asdict(order)", "fields to a plain dict"),
    # properties
    _s("def celsius(self) -> float: return self._celsius", "the getter under @property"),
    _s("def area(self) -> float:", "the property's getter"),
    _s("@temperature.setter", "what assigning to the property does"),
    _s("return self.width * self.height", "computed every time it is read"),
    _s("@functools.cached_property", "computed once, then stored"),
    # class and static methods
    _s("def from_dict(cls, data: dict[str, Any]) -> Self:", "a classmethod that builds one from a dict"),
    _s("def from_string(cls, text: str) -> Self:", "an alternative constructor"),
    _s("name, age = text.split(\",\")", "pulling the fields out of the text"),
    _s("return cls(name.strip(), int(age))", "cls, so subclasses get themselves"),
    _s("def is_valid_email(text: str) -> bool:", "a staticmethod needs neither self nor cls"),
    # dunders
    _s("def __str__(self) -> str:", "what print() and str() show"),
    _s("return f\"{type(self).__name__}({self.x!r}, {self.y!r})\"", "the usual repr"),
    _s("def __eq__(self, other: object) -> bool:", "what == means"),
    _s("if not isinstance(other, Point): return NotImplemented", "let the other side try"),
    _s("def __hash__(self) -> int:", "so it can go in a set or be a dict key"),
    _s("return hash((self.x, self.y))", "hash the same fields == compares"),
    _s("def __add__(self, other: Vector) -> Vector:", "what + does"),
    _s("def __len__(self) -> int:", "what len() says"),
    _s("def __iter__(self) -> Iterator[int]:", "so a for loop can walk it"),
    _s("yield from self._items", "hand out each item in turn"),
    _s("def __getitem__(self, i: int) -> int:", "square-bracket indexing"),
    _s("def __contains__(self, item: object) -> bool:", "what `in` checks"),
    _s("def __bool__(self) -> bool:", "true or false in an if"),
    _s("def __enter__(self) -> Self:", "the start of a with block"),
    _s("def __exit__(self, *exc: object) -> None:", "and its end, error or not"),
    # inheritance
    _s("class SavingsAccount(Account):", "a kind of Account"),
    _s("super().__init__(owner, balance)", "let the parent set up its part"),
    _s("return super().describe() + f\" at {self.rate:.1%}\"", "extend, not replace"),
    _s("isinstance(acct, Account)", "true for subclasses too"),
    _s("issubclass(SavingsAccount, Account)", "asks about classes, not objects"),
    # abstract classes and protocols
    _s("from abc import ABC, abstractmethod", "for classes that must be finished"),
    _s("class Shape(ABC):", "cannot be made directly"),
    _s("@abstractmethod", "every subclass has to write this"),
    _s("class SupportsArea(Protocol):", "anything with the right methods fits"),
    _s("def total_area(shapes: Iterable[SupportsArea]) -> float:", "structural typing"),
    # enums
    _s("from enum import Enum, auto", "named constants"),
    _s("class Colour(Enum):", "a closed set of values"),
    _s("class Status(StrEnum):", "an enum whose values are strings"),
    _s("Colour[\"RED\"] is Colour.RED", "look one up by name"),
    _s("for colour in Colour: print(colour.name, colour.value)", "every member"),
    # type hints
    _s("def last[T](items: list[T]) -> T | None:", "a generic function, 3.12 style"),
    _s("class Stack[T]:", "a generic class, 3.12 style"),
    _s("type Pair = tuple[int, int]", "a type alias with the type statement"),
    _s("Mode = Literal[\"r\", \"w\", \"a\"]", "only these exact strings"),
    _s("class Movie(TypedDict):", "the shape of a dict, with named keys"),
    _s("def parse(raw: str | bytes) -> dict[str, Any]:", "a union and a generic dict"),
    _s("callback: Callable[[int], str]", "takes an int, returns a str"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"Python · {note}")


PYCLASS_BLOCKS: tuple[Passage, ...] = (
    _b(r"""class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        return self.balance

acct = Account("Ada")
print(acct.deposit(50), acct.deposit(25), acct.owner)""",
       "a class with a method"),
    _b(r"""from dataclasses import dataclass, field

@dataclass
class Order:
    item: str
    qty: int = 1
    tags: list[str] = field(default_factory=list)

a = Order("tea")
b = Order("jam", 3)
a.tags.append("hot")
print(a, b.tags, a == Order("tea", 1, ["hot"]))""",
       "a dataclass with defaults"),
    _b(r"""from dataclasses import dataclass

@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int

versions = [Version(1, 10), Version(1, 2), Version(0, 9)]
print(sorted(versions)[0], max(versions))
print(len({Version(1, 2), Version(1, 2)}))""",
       "a frozen, ordered dataclass"),
    _b(r"""class Rect:
    def __init__(self, w, h):
        self.w, self.h = w, h

    @property
    def area(self):
        return self.w * self.h

r = Rect(3, 4)
r.w = 10
print(r.area)""",
       "a property worked out on read"),
    _b(r"""class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    @classmethod
    def from_text(cls, text):
        x, y = text.split(",")
        return cls(int(x), int(y))

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

print(Point.from_text("3,4"), Point.from_text(" 10 , -2 "))""",
       "a classmethod as a second constructor"),
    _b(r"""class Vector:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        return (self.x, self.y) == (other.x, other.y)

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

print(Vector(1, 2) + Vector(3, 4), Vector(1, 1) == Vector(1, 1))""",
       "operators with dunder methods"),
    _b(r"""class Playlist:
    def __init__(self, *songs):
        self._songs = list(songs)

    def __len__(self):
        return len(self._songs)

    def __iter__(self):
        return iter(self._songs)

    def __contains__(self, song):
        return song in self._songs

p = Playlist("one", "two")
print(len(p), list(p), "two" in p, "six" in p)""",
       "a container with len, iter and in"),
    _b(r"""class Animal:
    def __init__(self, name):
        self.name = name

    def describe(self):
        return f"{self.name} the animal"

class Dog(Animal):
    def describe(self):
        return super().describe() + ", a dog"

print(Dog("Rex").describe(), isinstance(Dog("Bo"), Animal))""",
       "inheritance and super"),
    _b(r"""from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self): ...

class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2

print(Square(3).area(), [type(s).__name__ for s in (Square(1),)])""",
       "an abstract base class"),
    _b(r"""from enum import Enum

class Light(Enum):
    RED = 1
    AMBER = 2
    GREEN = 3

nxt = {Light.RED: Light.GREEN, Light.GREEN: Light.AMBER, Light.AMBER: Light.RED}
state = Light.RED
for _ in range(4):
    state = nxt[state]
print(state, state.name, state.value, Light["GREEN"] is Light.GREEN)""",
       "an enum driving a state machine"),
    _b(r"""class Timer:
    def __enter__(self):
        print("start")
        return self

    def __exit__(self, *exc):
        print("stop")

with Timer() as t:
    print("working", type(t).__name__)""",
       "a context manager class"),
    _b(r"""class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T | None:
        return self._items.pop() if self._items else None

s = Stack[int]()
s.push(1)
s.push(2)
print(s.pop(), s.pop(), s.pop())""",
       "a generic class in the 3.12 spelling"),
)

#: What each block prints, by its note - worked out by hand before Python
#: was asked, and held to the real run by tests/test_typing_python_themes2.py.
PYCLASS_PRINTS: dict[str, str] = {
    "a class with a method": "50 75 Ada",
    "a dataclass with defaults": "Order(item='tea', qty=1, tags=['hot']) [] True",
    "a frozen, ordered dataclass": "Version(major=0, minor=9) Version(major=1, minor=10)\n1",
    "a property worked out on read": "40",
    "a classmethod as a second constructor": "Point(3, 4) Point(10, -2)",
    "operators with dunder methods": "Vector(4, 6) True",
    "a container with len, iter and in": "2 ['one', 'two'] True False",
    "inheritance and super": "Rex the animal, a dog True",
    "an abstract base class": "9 ['Square']",
    "an enum driving a state machine": "Light.GREEN GREEN 3 True",
    "a context manager class": "start\nworking Timer\nstop",
    "a generic class in the 3.12 spelling": "2 1 None",
}
