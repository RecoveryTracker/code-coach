"""Special Methods and Dataclasses: a passive deck. Outputs were worked out by hand; the oracle test runs the code."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 61

DECK = Deck(
    id="py-dunders",
    title="Special Methods and Dataclasses",
    language="python",
    blurb="The double-underscore methods that make your objects work with print, ==, sorting, len, in, + and with, plus dataclasses.",
    slides=(
        Slide(
            title="__repr__: a readable object",
            text="Without __repr__ an object prints as an unhelpful label with a memory address. Define __repr__ to return text that shows what the object holds.",
            code=r"""class Pt:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __repr__(self):
        return f"Pt({self.x}, {self.y})"
print(Pt(1, 2))
print([Pt(1, 2)])""",
            output="Pt(1, 2)\n[Pt(1, 2)]",
            point="Special methods are hooks Python calls for you.",
        ),
        Slide(
            title="__eq__: when == means equal",
            text="Without __eq__, == only asks 'is this the very same object?', so two look-alike objects are different. Define __eq__ to compare what they hold.",
            code=r"""class A:
    def __init__(self, n):
        self.n = n
class B(A):
    def __eq__(self, o):
        return self.n == o.n
print(A(1) == A(1))
print(B(1) == B(1))""",
            output="False\nTrue",
            point="Default == is identity; __eq__ makes it about content.",
        ),
        Slide(
            title="__lt__: sorting your objects",
            text="sorted() and min() compare items with <. If your class defines __lt__, they know how to put its objects in order.",
            code=r"""class V:
    def __init__(self, n):
        self.n = n
    def __lt__(self, o):
        return self.n < o.n
vs = sorted([V(3), V(1), V(2)])
print([v.n for v in vs])""",
            output="[1, 2, 3]",
            point="Give sorted() a __lt__ and it can order anything.",
        ),
        Slide(
            title="__len__",
            text="len(x) calls x.__len__(). Return a whole number and your object works with len, and an empty one counts as false in an if.",
            code=r"""class Hand:
    def __init__(self):
        self.cards = [7, 9, 2]
    def __len__(self):
        return len(self.cards)
print(len(Hand()))""",
            output="3",
            point="len(obj) is really obj.__len__().",
        ),
        Slide(
            title="__getitem__: indexing and looping",
            text="__getitem__ makes obj[i] work. As a bonus, Python can loop over an object that has it, trying 0, 1, 2 and so on until IndexError is raised.",
            code=r"""class Three:
    def __getitem__(self, i):
        if i >= 3:
            raise IndexError
        return i * 10
print(Three()[2])
print(list(Three()))""",
            output="20\n[0, 10, 20]",
            point="Indexing support gives you iteration for free.",
        ),
        Slide(
            title="__contains__: the in operator",
            text="x in obj calls obj.__contains__(x) and expects True or False. Without it Python falls back to looping, which is slower or may not work at all.",
            code=r"""class Evens:
    def __contains__(self, n):
        return n % 2 == 0
print(4 in Evens())
print(5 in Evens())""",
            output="True\nFalse",
            point="Define __contains__ when 'in' can be answered without a loop.",
        ),
        Slide(
            title="__iter__ with a generator",
            text="__iter__ tells a for loop how to walk your object. The simplest way to write it is with yield, which hands out one value at a time.",
            code=r"""class Count:
    def __init__(self, n):
        self.n = n
    def __iter__(self):
        for i in range(self.n):
            yield i
print(list(Count(3)))""",
            output="[0, 1, 2]",
            point="__iter__ plus yield: your object works in any for loop.",
        ),
        Slide(
            title="__add__: the + operator",
            text="a + b calls a.__add__(b). Return a new object and your class can be added just like numbers. Other operators have matching names such as __sub__ and __mul__.",
            code=r"""class V:
    def __init__(self, x):
        self.x = x
    def __add__(self, o):
        return V(self.x + o.x)
print((V(2) + V(5)).x)""",
            output="7",
            point="Operators are method calls in disguise.",
        ),
        Slide(
            title="__bool__: truthiness",
            text="if obj: asks for obj.__bool__(). Return False when your object should count as empty or off. Without __bool__ Python tries __len__, then says true.",
            code=r"""class Box:
    def __init__(self, n):
        self.n = n
    def __bool__(self):
        return self.n > 0
print(bool(Box(0)), bool(Box(2)))""",
            output="False True",
            point="__bool__ decides how your object behaves in an if.",
        ),
        Slide(
            title="__call__: objects you can call",
            text="Define __call__ and an instance can be used like a function: obj(4). It is useful when the function needs to remember settings between calls.",
            code=r"""class Adder:
    def __init__(self, k):
        self.k = k
    def __call__(self, x):
        return x + self.k
add3 = Adder(3)
print(add3(4))""",
            output="7",
            point="obj(...) runs obj.__call__(...).",
        ),
        Slide(
            title="__enter__ and __exit__",
            text="A with block calls __enter__ at the start and __exit__ at the end, even if an error happens inside. That is how files and locks tidy up after themselves.",
            code=r"""class Tag:
    def __enter__(self):
        print("open")
        return self
    def __exit__(self, *args):
        print("close")
with Tag():
    print("inside")""",
            output="open\ninside\nclose",
            point="with = enter, run the block, always exit.",
        ),
        Slide(
            title="@dataclass",
            text="A dataclass writes __init__, __repr__ and __eq__ for you from a list of annotated fields. It removes the boring code from classes that mostly hold data.",
            code=r"""from dataclasses import dataclass
@dataclass
class P:
    x: int
    y: int
print(P(1, 2))
print(P(1, 2) == P(1, 2))""",
            output="P(x=1, y=2)\nTrue",
            point="Fields in, __init__ / __repr__ / __eq__ out.",
        ),
        Slide(
            title="Dataclass defaults and field()",
            text="A field can have a default value. For a list or dict, use field(default_factory=list) so each object gets its own new one; a plain [] is refused.",
            code=r"""from dataclasses import dataclass, field
@dataclass
class T:
    name: str = "new"
    tags: list = field(default_factory=list)
a = T()
a.tags.append("x")
print(a)
print(T().tags)""",
            output="T(name='new', tags=['x'])\n[]",
            point="Mutable default? Use field(default_factory=...).",
        ),
        Slide(
            title="frozen=True and order=True",
            text="frozen=True stops anyone changing a field after creation. order=True adds <, >, <= and >=, comparing the fields in the order they are written.",
            code=r"""from dataclasses import dataclass
@dataclass(frozen=True, order=True)
class V:
    n: int
print(V(1) < V(2))
try:
    V(1).n = 5
except Exception as e:
    print(type(e).__name__)""",
            output="True\nFrozenInstanceError",
            point="frozen = read-only object; order = comparable object.",
        ),
        Slide(
            title="functools.total_ordering",
            text="Writing all of <, <=, > and >= is tedious. With @total_ordering you write __eq__ and just one of them, and Python fills in the rest.",
            code=r"""from functools import total_ordering
@total_ordering
class V:
    def __init__(self, n):
        self.n = n
    def __eq__(self, o):
        return self.n == o.n
    def __lt__(self, o):
        return self.n < o.n
print(V(3) >= V(2), V(1) > V(2))""",
            output="True False",
            point="__eq__ plus one comparison gives you all six.",
        ),
    ),
)
