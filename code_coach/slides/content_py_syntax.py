"""Python Syntax: a passive deck. Outputs were worked out by hand; the oracle test runs the code."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 20

DECK = Deck(
    id="py-syntax",
    title="Python Syntax",
    language="python",
    blurb="The shapes of everyday Python: blocks, branches, loops, functions, comprehensions, errors and classes.",
    slides=(
        Slide(
            title="Indentation makes blocks",
            text="Python has no curly braces. The lines pushed in under a colon belong to that block, and the block ends when the indentation goes back.",
            code=r"""if 3 > 2:
    print("yes")
    print("inside")
print("outside")""",
            output="yes\ninside\noutside",
            point="Four spaces in = inside the block.",
        ),
        Slide(
            title="Variables and assignment",
            text="A name = value line gives a value a name. You can assign several names at once, and swap two with one line.",
            code=r"""a, b = 1, 2
x = y = 0
a, b = b, a
print(a, b, x, y)""",
            output="2 1 0 0",
            point="a, b = b, a swaps with no helper variable.",
        ),
        Slide(
            title="if / elif / else",
            text="Python checks the conditions from the top and runs the first block whose condition is true. else runs when none of them were.",
            code=r"""score = 72
if score >= 90:
    print("great")
elif score >= 70:
    print("ok")
else:
    print("low")""",
            output="ok",
            point="Only one branch runs - the first that matches.",
        ),
        Slide(
            title="for loops",
            text="for repeats a block once per item. range(3) gives 0, 1, 2 - it stops before 3 - and a list gives its items in order.",
            code=r"""for i in range(3):
    print(i)
for fruit in ["fig", "pear"]:
    print(fruit)""",
            output="0\n1\n2\nfig\npear",
            point="range(n) counts from 0 up to n - 1.",
        ),
        Slide(
            title="while, break and continue",
            text="while repeats as long as its condition is true. continue skips to the next round; break leaves the loop right away.",
            code=r"""n = 0
while True:
    n += 1
    if n == 2:
        continue
    if n > 4:
        break
    print(n)""",
            output="1\n3\n4",
            point="continue = skip this round, break = stop the loop.",
        ),
        Slide(
            title="Functions",
            text="def defines a function; return hands a value back. A default argument is used when the caller leaves it out, and a keyword argument names which one it sets.",
            code=r"""def greet(name, greeting="Hello"):
    return greeting + ", " + name

print(greet("Ann"))
print(greet("Bo", greeting="Hi"))""",
            output="Hello, Ann\nHi, Bo",
            point="Defaults make arguments optional.",
        ),
        Slide(
            title="f-strings",
            text="Put an f before a string and anything in {braces} is worked out and put in. After a colon you can say how to show it: .2f means two decimals.",
            code=r"""name = "Ann"
n = 3
print(f"{name} has {n} cats")
print(f"{n * 2} and {n / 2:.2f}")""",
            output="Ann has 3 cats\n6 and 1.50",
            point="f-strings are the easy way to build text from values.",
        ),
        Slide(
            title="List comprehensions",
            text="A comprehension builds a list in one line: an expression, a for, and optionally an if to filter.",
            code=r"""squares = [n * n for n in range(5)]
evens = [n for n in range(10) if n % 2 == 0]
print(squares)
print(evens)""",
            output="[0, 1, 4, 9, 16]\n[0, 2, 4, 6, 8]",
            point="[expression for item in items if condition]",
        ),
        Slide(
            title="Slicing [a:b:c]",
            text="A slice takes part of a list or string: start, stop (not included) and step. Leave a part out to mean 'from the start' or 'to the end'; a step of -1 goes backwards.",
            code=r"""nums = [0, 1, 2, 3, 4, 5, 6]
print(nums[2:5])
print(nums[::2])
print(nums[-3:])
print(nums[::-1])""",
            output="[2, 3, 4]\n[0, 2, 4, 6]\n[4, 5, 6]\n[6, 5, 4, 3, 2, 1, 0]",
            point="[start:stop:step] - stop is never included.",
        ),
        Slide(
            title="Unpacking and *rest",
            text="Unpacking splits a sequence into names. A name with a star soaks up everything that is left over, as a list.",
            code=r"""first, *rest = [10, 20, 30, 40]
print(first)
print(rest)
a, *mid, z = "hello"
print(mid)""",
            output="10\n[20, 30, 40]\n['e', 'l', 'l']",
            point="*name collects the leftovers into a list.",
        ),
        Slide(
            title="try / except / finally",
            text="Code in try runs until something goes wrong. An error of the kind named in except is caught and handled; finally always runs, error or not.",
            code=r"""try:
    n = int("abc")
except ValueError:
    print("not a number")
finally:
    print("done")""",
            output="not a number\ndone",
            point="Catch the specific error you expect, not everything.",
        ),
        Slide(
            title="with: tidy up automatically",
            text="with opens something, runs a block, and closes it for you afterwards, even after an error. Files work this way; here an in-memory stand-in plays the file so nothing touches the disk.",
            code=r"""import io
with io.StringIO("a\nb\n") as f:
    for line in f:
        print(line.strip())""",
            output="a\nb",
            point="with open(...) as f: closes the file for you.",
        ),
        Slide(
            title="Classes",
            text="A class is a blueprint for objects. __init__ runs when you make one, self is the object itself, and a method is a function that belongs to the class.",
            code=r"""class Dog:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return self.name + " says woof"

rex = Dog("Rex")
print(rex.speak())""",
            output="Rex says woof",
            point="self is how a method reaches its own object's data.",
        ),
        Slide(
            title="lambda",
            text="A lambda is a tiny nameless function written on one line: the inputs, a colon, then the value it returns. It is often handed to sorted() as a key.",
            code=r"""double = lambda x: x * 2
print(double(4))
words = ["pear", "fig", "apple"]
print(sorted(words, key=lambda w: len(w)))""",
            output="8\n['fig', 'pear', 'apple']",
            point="lambda args: expression - one expression, no statements.",
        ),
        Slide(
            title="Imports",
            text="import brings in a module of ready-made tools. Use module.name to reach inside it, or from module import name to take just one thing.",
            code=r"""import math
from collections import Counter
print(math.sqrt(16))
print(Counter("aab")["a"])""",
            output="4.0\n2",
            point="Python ships with a big standard library - import it.",
        ),
    ),
)
