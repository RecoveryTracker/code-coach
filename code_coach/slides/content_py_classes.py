"""Classes and Objects: a passive deck. Outputs were worked out by hand; the oracle test runs the code."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 60

DECK = Deck(
    id="py-classes",
    title="Classes and Objects",
    language="python",
    blurb="Blueprints and the things built from them: attributes, methods, inheritance, properties and printing.",
    slides=(
        Slide(
            title="A class and an instance",
            text="A class is a blueprint; calling it builds an instance. __init__ runs on the new object, and self is that object, so self.name = name stores an attribute on it.",
            code=r"""class Dog:
    def __init__(self, name):
        self.name = name
d = Dog("Rex")
print(d.name)
print(type(d).__name__)""",
            output="Rex\nDog",
            point="Dog(...) builds an object; self is the object being built.",
        ),
        Slide(
            title="Methods",
            text="A function inside a class is a method. Python passes the object in as the first argument, self, so a method can read and change the object's own attributes.",
            code=r"""class Counter:
    def __init__(self):
        self.n = 0
    def bump(self):
        self.n += 1
c = Counter()
c.bump()
c.bump()
print(c.n)""",
            output="2",
            point="c.bump() is the same as Counter.bump(c).",
        ),
        Slide(
            title="Class vs instance attributes",
            text="An attribute set in the class body is shared by every instance. Assigning to it through one instance creates that instance's own copy and leaves the class value alone.",
            code=r"""class Dog:
    legs = 4
a = Dog()
b = Dog()
b.legs = 3
print(a.legs, b.legs, Dog.legs)""",
            output="4 3 4",
            point="Class attributes are shared defaults; self.x = ... makes it personal.",
        ),
        Slide(
            title="The shared mutable trap",
            text="A list in the class body is ONE list shared by every instance. Appending through any instance changes it for all of them. Create lists in __init__ instead.",
            code=r"""class Bag:
    items = []
a = Bag()
b = Bag()
a.items.append("x")
print(b.items)""",
            output="['x']",
            point="Never put a list or dict in the class body for per-object data.",
        ),
        Slide(
            title="Inheritance",
            text="A class can be built on another by naming it in brackets. The child gets all the parent's methods for free and can add its own.",
            code=r"""class Animal:
    def speak(self):
        return "..."
class Dog(Animal):
    pass
print(Dog().speak())""",
            output="...",
            point="class Child(Parent) means Child is-a Parent.",
        ),
        Slide(
            title="super().__init__",
            text="If a child defines its own __init__, the parent's one no longer runs by itself. Call super().__init__(...) to let the parent set up its part first.",
            code=r"""class Animal:
    def __init__(self, name):
        self.name = name
class Dog(Animal):
    def __init__(self, name):
        super().__init__(name)
        self.tricks = []
d = Dog("Rex")
print(d.name, d.tricks)""",
            output="Rex []",
            point="super() reaches the parent's version of a method.",
        ),
        Slide(
            title="Overriding a method",
            text="If a child defines a method with the same name as the parent's, the child's version wins for child objects. Parent objects keep using their own.",
            code=r"""class Animal:
    def speak(self):
        return "..."
class Dog(Animal):
    def speak(self):
        return "Woof"
print(Animal().speak(), Dog().speak())""",
            output="... Woof",
            point="Same name, nearest class wins.",
        ),
        Slide(
            title="isinstance and issubclass",
            text="isinstance asks whether an object belongs to a class, parents included. issubclass asks the same about two classes, and the answer only goes one way.",
            code=r"""class A:
    pass
class B(A):
    pass
b = B()
print(isinstance(b, A), isinstance(b, B))
print(issubclass(B, A), issubclass(A, B))""",
            output="True True\nTrue False",
            point="A child is also its parent's type, never the reverse.",
        ),
        Slide(
            title="Composition: has-a",
            text="Instead of inheriting, an object can simply hold another object in an attribute and pass work along to it. Use inheritance for 'is a', composition for 'has a'.",
            code=r"""class Engine:
    def start(self):
        return "vroom"
class Car:
    def __init__(self):
        self.engine = Engine()
    def start(self):
        return self.engine.start()
print(Car().start())""",
            output="vroom",
            point="A Car has an Engine; it is not an Engine.",
        ),
        Slide(
            title="@property",
            text="A property is a method you read like an attribute, with no brackets. It is handy for a value worked out from others, so it can never go out of date.",
            code=r"""class Rect:
    def __init__(self, w, h):
        self.w = w
        self.h = h
    @property
    def area(self):
        return self.w * self.h
print(Rect(3, 4).area)""",
            output="12",
            point="@property: a method that looks like a plain attribute.",
        ),
        Slide(
            title="A property setter that checks",
            text="Add @name.setter to run code when someone assigns to the property. Here a bad value is fixed on the way in; a setter could also raise an error instead.",
            code=r"""class P:
    @property
    def age(self):
        return self._a
    @age.setter
    def age(self, v):
        self._a = max(v, 0)
p = P()
p.age = -5
print(p.age)""",
            output="0",
            point="Setters let you guard an attribute without changing how it is used.",
        ),
        Slide(
            title="@classmethod: another constructor",
            text="A class method receives the class itself (cls) instead of an object. It is the usual way to offer a second way of building an object.",
            code=r"""class Pt:
    def __init__(self, x, y):
        self.x, self.y = x, y
    @classmethod
    def from_text(cls, s):
        x, y = s.split(",")
        return cls(int(x), int(y))
p = Pt.from_text("3,4")
print(p.x, p.y)""",
            output="3 4",
            point="Pt.from_text(...) builds a Pt without going through __init__ by hand.",
        ),
        Slide(
            title="@staticmethod",
            text="A static method gets neither the object nor the class. It is an ordinary function that lives in the class because it belongs with it. Call it on the class or an instance.",
            code=r"""class Math:
    @staticmethod
    def double(n):
        return n * 2
print(Math.double(4))
print(Math().double(5))""",
            output="8\n10",
            point="No self, no cls: just a function filed under a class.",
        ),
        Slide(
            title="Private by convention: _name",
            text="Python has no truly private attributes. A leading underscore is a polite note that says 'internal, please do not touch'. Nothing stops you from reading it.",
            code=r"""class Acct:
    def __init__(self):
        self._bal = 5
a = Acct()
print(a._bal)
print(hasattr(a, "bal"))""",
            output="5\nFalse",
            point="_name means 'internal'; it is a habit, not a lock.",
        ),
        Slide(
            title="__repr__ vs __str__",
            text="print() shows an object using __str__, meant for readers. repr() and lists use __repr__, meant for programmers. Define __repr__ first; it is also used when no __str__ exists.",
            code=r"""class P:
    def __repr__(self):
        return "P(repr)"
    def __str__(self):
        return "a P"
p = P()
print(p)
print(repr(p))
print([p])""",
            output="a P\nP(repr)\n[P(repr)]",
            point="__str__ is for people, __repr__ is for debugging.",
        ),
    ),
)
