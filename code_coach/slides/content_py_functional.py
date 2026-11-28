"""Functional Tools: a passive deck. Outputs were worked out by hand; the oracle test runs the code."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 101

DECK = Deck(
    id="py-functional",
    title="Functional Tools",
    language="python",
    blurb="Treat functions as values: map, filter, reduce, sort keys, partial, closures, a call-counting decorator, caching and composition.",
    slides=(
        Slide(
            title="Functions are values",
            text="A function is an object like any other. You can store it in a variable, put it in a tuple, and call it later by whatever name holds it.",
            code=r"""def shout(s):
    return s.upper() + "!"

f = shout
print(f("hi"))
for fn in (shout, str.title, len):
    print(fn("hi"))""",
            output="HI!\nHI!\nHi\n2",
            point="shout is the function; shout(...) is calling it.",
        ),
        Slide(
            title="map",
            text="map(fn, items) applies fn to every item and gives the results lazily. Wrap it in list() to see them. With two lists it passes one item from each.",
            code=r"""print(list(map(str.upper, ["a", "b"])))
print(list(map(lambda n: n * n, [1, 2, 3])))
print(list(map(pow, [2, 3], [3, 2])))
m = map(abs, [-1, 2])
print(next(m))""",
            output="['A', 'B']\n[1, 4, 9]\n[8, 9]\n1",
            point="map transforms every item; it is lazy until you consume it.",
        ),
        Slide(
            title="filter",
            text="filter(fn, items) keeps the items for which fn says True. Passing None as fn keeps the truthy items, throwing away 0, empty strings and empty lists.",
            code=r"""print(list(filter(lambda n: n % 2 == 0, [1, 2, 3, 4, 5, 6])))
print(list(filter(None, [0, 1, "", "a", [], [2]])))""",
            output="[2, 4, 6]\n[1, 'a', [2]]",
            point="filter(None, xs) drops everything falsy.",
        ),
        Slide(
            title="functools.reduce",
            text="reduce folds a list into one value by combining the running result with the next item. A third argument is the starting value, which also covers an empty list.",
            code=r"""from functools import reduce
print(reduce(lambda a, b: a + b, [1, 2, 3, 4]))
print(reduce(lambda a, b: a * b, [1, 2, 3, 4], 1))
print(reduce(lambda a, b: a + b, [], 0))""",
            output="10\n24\n0",
            point="reduce(f, xs, start) is an accumulator loop in one call.",
        ),
        Slide(
            title="lambda as a sort key",
            text="A lambda is a tiny nameless function, handy for key=. The key says what to sort by, and the items themselves stay unchanged.",
            code=r"""words = ["pear", "fig", "banana"]
print(sorted(words, key=lambda w: len(w)))
print(sorted(words, key=lambda w: w[-1]))""",
            output="['fig', 'pear', 'banana']\n['banana', 'fig', 'pear']",
            point="key=lambda x: ... decides the order without changing the data.",
        ),
        Slide(
            title="itemgetter and attrgetter",
            text="operator.itemgetter(i) builds a function that fetches item i, and attrgetter('name') fetches an attribute. They are neat, fast replacements for simple lambdas.",
            code=r"""from operator import itemgetter, attrgetter
from collections import namedtuple
P = namedtuple("P", "name age")
people = [P("ann", 30), P("bo", 25)]
print(sorted(people, key=attrgetter("age")))
print(max(people, key=itemgetter(1)).name)""",
            output="[P(name='bo', age=25), P(name='ann', age=30)]\nann",
            point="itemgetter(1) is the same as lambda t: t[1].",
        ),
        Slide(
            title="functools.partial",
            text="partial fixes some arguments of a function and hands back a new function that waits for the rest. It is a quick way to make specialised versions.",
            code=r"""from functools import partial
def power(base, exp):
    return base ** exp
square = partial(power, exp=2)
cube = partial(power, exp=3)
print(square(7))
print(cube(2))""",
            output="49\n8",
            point="partial(f, x) is f with some arguments already filled in.",
        ),
        Slide(
            title="Sort by two things",
            text="Make the key a tuple and Python compares the first part, then the second only on a tie. Negate a number to sort that part in the opposite direction.",
            code=r"""people = [("bo", 25), ("ann", 30), ("cy", 25)]
print(sorted(people, key=lambda p: (p[1], p[0])))
print(sorted(people, key=lambda p: (-p[1], p[0])))""",
            output="[('bo', 25), ('cy', 25), ('ann', 30)]\n[('ann', 30), ('bo', 25), ('cy', 25)]",
            point="key=lambda p: (main, tiebreak), negating numbers to flip.",
        ),
        Slide(
            title="min and max with key",
            text="min and max accept key= too, so you can ask for the shortest word or the one with the biggest last letter. If two items tie, the first one wins.",
            code=r"""words = ["kiwi", "fig", "banana", "plum"]
print(min(words, key=len))
print(max(words, key=len))
print(max(words, key=lambda w: w[-1]))
print(max(["ab", "cd"], key=len))""",
            output="fig\nbanana\nplum\nab",
            point="max(items, key=f) returns the item, not the key value.",
        ),
        Slide(
            title="any and all with a generator",
            text="any is True if at least one item passes and all is True only if every item does. Feeding them a generator lets them stop at the first deciding item. Empty input gives all True and any False.",
            code=r"""nums = [2, 4, 7]
print(any(n % 2 == 1 for n in nums))
print(all(n % 2 == 0 for n in nums))
print(all([]), any([]))""",
            output="True\nFalse\nTrue False",
            point="any(cond for x in xs) / all(cond for x in xs) read like English.",
        ),
        Slide(
            title="Closures: configurable functions",
            text="A function defined inside another can remember the outer function's variables. Each call to the outer one builds a new function with its own remembered value.",
            code=r"""def multiplier(k):
    def times(x):
        return x * k
    return times

double = multiplier(2)
triple = multiplier(3)
print(double(5), triple(5))""",
            output="10 15",
            point="A closure is a function that carries its settings with it.",
        ),
        Slide(
            title="A decorator that counts calls",
            text="A decorator takes a function and returns a wrapped version. Here the wrapper counts how many times it ran. The @counted line is shorthand for add = counted(add).",
            code=r"""def counted(fn):
    def wrapper(*args):
        wrapper.calls += 1
        return fn(*args)
    wrapper.calls = 0
    return wrapper
@counted
def add(a, b): return a + b
print(add(1, 2), add(3, 4))
print(add.calls)""",
            output="3 7\n2",
            point="@decorator adds behaviour around a function without editing it.",
        ),
        Slide(
            title="functools.cache",
            text="@cache remembers the answer for each set of arguments. A repeated call returns the stored result without running the body again, as the counter shows.",
            code=r"""from functools import cache
calls = 0
@cache
def square(n):
    global calls
    calls += 1
    return n * n
print(square(4), square(4), square(5))
print(calls)""",
            output="16 16 25\n2",
            point="@cache only suits functions whose result depends on arguments alone.",
        ),
        Slide(
            title="Composing functions",
            text="Composing means feeding one function's result into another. A small compose helper returns a new function, and the order you pass the two functions in matters.",
            code=r"""def compose(f, g):
    return lambda x: f(g(x))
inc = lambda x: x + 1
double = lambda x: x * 2
print(compose(inc, double)(5))
print(compose(double, inc)(5))""",
            output="11\n12",
            point="compose(f, g)(x) means f(g(x)): g runs first.",
        ),
        Slide(
            title="Why comprehensions read better",
            text="map and filter work, but nesting them with lambdas gets hard to read. A comprehension says the same thing in one left-to-right line.",
            code=r"""nums = [1, 2, 3, 4, 5, 6]
print(list(map(lambda n: n * n, filter(lambda n: n % 2 == 0, nums))))
print([n * n for n in nums if n % 2 == 0])""",
            output="[4, 16, 36]\n[4, 16, 36]",
            point="Prefer a comprehension unless you already have a named function.",
        ),
    ),
)
