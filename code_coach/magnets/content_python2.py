"""More Python code magnets: the shapes a Python course reaches next.

The same rules as content_python.py: each line keeps its indentation, which
is half the clue, and the expected output was typed by a person and is held
to what Python prints by tests/test_magnets_python.py.

Between them: enumerate and zip, a comprehension with a filter, a while
loop with break and else, sorting by a key, a recursive function, a
dataclass, inheritance with super(), raising your own error, *args and
**kwargs, a property, dict and set comprehensions, and a class that knows
how to print itself.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m

FAMILY = "Python"

PY_MAGNETS_2: tuple[Magnet, ...] = (
    _m(
        id="magnet-py-enumerate",
        plan=(
            ("The list to number", 1),
            ("Number each one from 1", 2),
            ("Say how many there were", 1),
        ),
        level=1,
        name="Numbering a list with enumerate",
        family=FAMILY,
        language="python",
        note=(
            "`enumerate` hands back each item with its position, so the loop "
            "can unpack both at once. `start=1` makes the count begin at 1 "
            "instead of 0, which is how people number lists. The last print "
            "sits at the left margin, so it runs once, after the loop, not "
            "once per item."
        ),
        code=(
            "tasks = [\"wash\", \"dry\", \"fold\"]\n"
            "for number, task in enumerate(tasks, start=1):\n"
            "    print(f\"{number}. {task}\")\n"
            "print(len(tasks), \"tasks\")"
        ),
        expect="1. wash\n2. dry\n3. fold\n3 tasks",
    ),
    _m(
        id="magnet-py-zip",
        plan=(
            ("Two lists that line up", 2),
            ("Walk them side by side", 3),
            ("Report the total", 1),
        ),
        level=1,
        name="Walking two lists together with zip",
        family=FAMILY,
        language="python",
        note=(
            "`zip` pairs the first item of one list with the first of the "
            "other, then the seconds, and so on, stopping at the shorter. "
            "The total has to be set to 0 before the loop starts adding to "
            "it, and the line that adds is indented under the for, so it "
            "runs once per pair."
        ),
        code=(
            "items = [\"tea\", \"cake\"]\n"
            "prices = [2, 3]\n"
            "total = 0\n"
            "for item, price in zip(items, prices):\n"
            "    total += price\n"
            "print(\"total\", total)"
        ),
        expect="total 5",
    ),
    _m(
        id="magnet-py-comprehension",
        plan=(
            ("Some numbers", 1),
            ("Keep the even ones, squared", 1),
            ("Keep the odd ones as they are", 1),
            ("Show both", 2),
        ),
        level=2,
        name="Comprehensions with a filter",
        family=FAMILY,
        language="python",
        note=(
            "A comprehension reads like a sentence: the value to make, then "
            "the for, then an if that decides what gets in. Each one needs "
            "`nums` to exist already, so the list has to come first; the two "
            "comprehensions do not depend on each other and can go either "
            "way round."
        ),
        code=(
            "nums = [1, 2, 3, 4, 5, 6]\n"
            "evens = [n * n for n in nums if n % 2 == 0]\n"
            "odds = [n for n in nums if n % 2]\n"
            "print(evens)\n"
            "print(odds)"
        ),
        expect="[4, 16, 36]\n[1, 3, 5]",
    ),
    _m(
        id="magnet-py-while-else",
        plan=(
            ("What to look for, and where", 2),
            ("Look at each one until it is found", 5),
            ("When it never turned up", 2),
        ),
        level=3,
        name="A search with while, break and else",
        family=FAMILY,
        language="python",
        note=(
            "A loop's `else` runs only when the loop finished without a "
            "`break` - here, when the number was never found. `i += 1` has to "
            "be the last line in the loop body, after the check, or the first "
            "item is skipped. The else lines up with the while, not with the "
            "if inside it."
        ),
        code=(
            "nums = [4, 8, 15, 16]\n"
            "i = 0\n"
            "while i < len(nums):\n"
            "    if nums[i] == 15:\n"
            "        print(\"found at\", i)\n"
            "        break\n"
            "    i += 1\n"
            "else:\n"
            "    print(\"not there\")"
        ),
        expect="found at 2",
    ),
    _m(
        id="magnet-py-sort-key",
        plan=(
            ("Some people with ages", 1),
            ("Youngest first", 1),
            ("Oldest name, longest name", 2),
            ("Show them", 3),
        ),
        level=2,
        name="Sorting and picking by a key",
        family=FAMILY,
        language="python",
        note=(
            "`key=` tells sorted, max and min what to compare: here the age, "
            "`p[1]`, rather than the whole pair. `sorted` makes a new list "
            "and leaves `people` alone. Each print needs the name it prints "
            "to have been made first, which is the only thing that fixes the "
            "order here."
        ),
        code=(
            "people = [(\"Ann\", 31), (\"Bo\", 25), (\"Cyrus\", 40)]\n"
            "by_age = sorted(people, key=lambda p: p[1])\n"
            "oldest = max(people, key=lambda p: p[1])\n"
            "longest = max(people, key=lambda p: len(p[0]))\n"
            "print([name for name, age in by_age])\n"
            "print(oldest[0])\n"
            "print(longest[0])"
        ),
        expect="['Bo', 'Ann', 'Cyrus']\nCyrus\nCyrus",
    ),
    _m(
        id="magnet-py-recursion",
        plan=(
            ("Open the function", 1),
            ("Stop at the smallest case", 2),
            ("Otherwise lean on a smaller one", 1),
            ("Try it", 2),
        ),
        level=3,
        name="A function that calls itself",
        family=FAMILY,
        language="python",
        note=(
            "Every recursive function needs a case it can answer without "
            "calling itself - here n of 1 or less - and it has to be checked "
            "FIRST. Put the recursive return above it and the function never "
            "stops: it calls itself until Python gives up with a "
            "RecursionError."
        ),
        code=(
            "def factorial(n):\n"
            "    if n <= 1:\n"
            "        return 1\n"
            "    return n * factorial(n - 1)\n"
            "print(factorial(5))\n"
            "print(factorial(1))"
        ),
        expect="120\n1",
    ),
    _m(
        id="magnet-py-dataclass",
        plan=(
            ("Bring in the decorator", 1),
            ("A point with two numbers", 4),
            ("A method that measures it", 2),
            ("Make one and use it", 2),
        ),
        level=3,
        name="A dataclass",
        family=FAMILY,
        language="python",
        note=(
            "`@dataclass` writes `__init__` and `__repr__` for you from the "
            "fields listed in the class, so `Point(3, 4)` just works and "
            "printing it shows its fields. The import has to come first, and "
            "the decorator line goes directly above the class it decorates."
        ),
        code=(
            "from dataclasses import dataclass\n"
            "@dataclass\n"
            "class Point:\n"
            "    x: int\n"
            "    y: int\n"
            "    def length(self):\n"
            "        return (self.x ** 2 + self.y ** 2) ** 0.5\n"
            "p = Point(3, 4)\n"
            "print(p, p.length())"
        ),
        expect="Point(x=3, y=4) 5.0",
    ),
    _m(
        id="magnet-py-inheritance",
        plan=(
            ("A general animal", 5),
            ("A dog that adds to it", 4),
            ("Make a dog and hear it", 1),
        ),
        level=4,
        name="Inheritance and super()",
        family=FAMILY,
        language="python",
        note=(
            "`class Dog(Animal)` makes Dog a kind of Animal: it gets every "
            "method Animal has, and can replace some. Dog's `speak` calls "
            "`super().speak()` to get Animal's sentence and adds to it. The "
            "parent class has to be defined before the child that names it, "
            "because the class line runs and looks Animal up straight away."
        ),
        code=(
            "class Animal:\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n"
            "    def speak(self):\n"
            "        return self.name + \" makes a sound\"\n"
            "class Dog(Animal):\n"
            "    def speak(self):\n"
            "        base = super().speak()\n"
            "        return base + \", and it is a bark\"\n"
            "print(Dog(\"Rex\").speak())"
        ),
        expect="Rex makes a sound, and it is a bark",
    ),
    _m(
        id="magnet-py-raise",
        plan=(
            ("An error of your own", 2),
            ("A function that refuses bad input", 4),
            ("Call it, and catch the refusal", 4),
        ),
        level=4,
        name="Raising your own error",
        family=FAMILY,
        language="python",
        note=(
            "A class that inherits from Exception is a new kind of error you "
            "can raise and catch by name. `raise` stops the function on the "
            "spot - the return below it never runs for a negative number. "
            "`except TooCold as e` catches only that kind, and `e` is the "
            "error itself, so printing it prints its message."
        ),
        code=(
            "class TooCold(Exception):\n"
            "    pass\n"
            "def kelvin(celsius):\n"
            "    if celsius < -273.15:\n"
            "        raise TooCold(f\"{celsius} is below absolute zero\")\n"
            "    return celsius + 273.15\n"
            "try:\n"
            "    print(kelvin(-300))\n"
            "except TooCold as e:\n"
            "    print(\"no:\", e)"
        ),
        expect="no: -300 is below absolute zero",
    ),
    _m(
        id="magnet-py-args-kwargs",
        plan=(
            ("A function that takes any number of things", 4),
            ("Call it with a few of each", 2),
        ),
        level=4,
        name="*args and **kwargs",
        family=FAMILY,
        language="python",
        note=(
            "`*args` gathers every extra positional argument into a tuple, "
            "and `**kwargs` gathers every extra named one into a dict. So "
            "the first call's args is (1, 2, 3) and its kwargs is "
            "{'sep': '-'}. Inside, they are an ordinary tuple and dict: "
            "`sum(args)`, `kwargs.get(...)`."
        ),
        code=(
            "def report(label, *args, **kwargs):\n"
            "    sep = kwargs.get(\"sep\", \" \")\n"
            "    shown = sep.join(str(a) for a in args)\n"
            "    print(label, shown, \"=\", sum(args))\n"
            "report(\"sum\", 1, 2, 3, sep=\"-\")\n"
            "report(\"two\", 5, 6)"
        ),
        expect="sum 1-2-3 = 6\ntwo 5 6 = 11",
    ),
    _m(
        id="magnet-py-property",
        plan=(
            ("A temperature kept in Celsius", 3),
            ("Read it in Fahrenheit like a field", 3),
            ("Make one and read both", 2),
        ),
        level=5,
        name="A property",
        family=FAMILY,
        language="python",
        note=(
            "`@property` turns a method into something read like a field: "
            "`t.fahrenheit`, no brackets. It is worked out every time it is "
            "read, from the one value really stored, so the two can never "
            "disagree. The decorator sits directly above the def it changes, "
            "inside the class."
        ),
        code=(
            "class Temp:\n"
            "    def __init__(self, celsius):\n"
            "        self.celsius = celsius\n"
            "    @property\n"
            "    def fahrenheit(self):\n"
            "        return self.celsius * 9 / 5 + 32\n"
            "t = Temp(100)\n"
            "print(t.celsius, t.fahrenheit)"
        ),
        expect="100 212.0",
    ),
    _m(
        id="magnet-py-set-dict-comprehension",
        plan=(
            ("Some words", 1),
            ("Each word with its length", 1),
            ("The first letters, once each", 1),
            ("Show them", 2),
        ),
        level=5,
        name="Dict and set comprehensions",
        family=FAMILY,
        language="python",
        note=(
            "Braces make a dict comprehension when there is a `key: value`, "
            "and a set comprehension when there is just a value. A set keeps "
            "each thing once, so 'apple' and 'avocado' give one 'a'. Sets "
            "have no order, which is why it is sorted before it is printed."
        ),
        code=(
            "words = [\"apple\", \"bean\", \"avocado\"]\n"
            "lengths = {w: len(w) for w in words}\n"
            "firsts = {w[0] for w in words}\n"
            "print(lengths)\n"
            "print(sorted(firsts))"
        ),
        expect="{'apple': 5, 'bean': 4, 'avocado': 7}\n['a', 'b']",
    ),
    _m(
        id="magnet-py-repr",
        plan=(
            ("A card with a rank and a suit", 4),
            ("How it prints", 2),
            ("A hand of two", 2),
        ),
        level=5,
        name="A class that prints itself",
        family=FAMILY,
        language="python",
        note=(
            "`print(card)` asks for `__str__`; a list of cards prints each "
            "one with `__repr__`. Defining only `__repr__` covers both, "
            "because `__str__` falls back to it. Without it a card prints as "
            "something like <__main__.Card object at 0x...>."
        ),
        code=(
            "class Card:\n"
            "    def __init__(self, rank, suit):\n"
            "        self.rank = rank\n"
            "        self.suit = suit\n"
            "    def __repr__(self):\n"
            "        return f\"{self.rank}{self.suit}\"\n"
            "hand = [Card(\"A\", \"s\"), Card(10, \"h\")]\n"
            "print(hand, hand[0])"
        ),
        expect="[As, 10h] As",
    ),
)

# Least surprising first, as every set is shown.
PY_MAGNETS_2 = tuple(sorted(PY_MAGNETS_2, key=lambda m: m.level))
