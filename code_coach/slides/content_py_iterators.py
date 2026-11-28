"""Iterators and Iteration: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 85

DECK = Deck(
    id="py-iterators",
    title="Iterators and Iteration",
    language="python",
    blurb="What a for loop does underneath: iter and next, building your own iterator, laziness, and why iterators run out.",
    slides=(
        Slide(
            title="iter() and next()",
            text="iter() gives you an iterator over any iterable. Each next() hands over the following item and remembers where it stopped.",
            code=r"""it = iter([10, 20, 30])
print(next(it))
print(next(it))
print(next(it))""",
            output="10\n20\n30",
            point="An iterator is a bookmark: next() returns the item at the bookmark and moves it on.",
        ),
        Slide(
            title="What a for loop really does",
            text="A for loop calls iter() once, then calls next() again and again. When next() raises StopIteration the loop quietly ends.",
            code=r"""it = iter("ab")
while True:
    try:
        x = next(it)
    except StopIteration:
        break
    print(x)
print("done")""",
            output="a\nb\ndone",
            point="for x in things: is iter() plus next() until StopIteration.",
        ),
        Slide(
            title="Iterable vs iterator",
            text="An iterable can be looped over, like a list. An iterator is the one-way walker made from it, and it also works as an iterable that returns itself.",
            code=r"""nums = [1, 2]
it = iter(nums)
print(iter(nums) is nums)
print(iter(it) is it)
print(hasattr(nums, "__next__"), hasattr(it, "__next__"))""",
            output="False\nTrue\nFalse True",
            point="Iterables make iterators; an iterator's iter() is itself.",
        ),
        Slide(
            title="Write your own iterator class",
            text="An iterator class needs __iter__ (return self) and __next__ (return the next item, or raise StopIteration when there are no more).",
            code=r"""class Countdown:
    n = 3
    def __iter__(self):
        return self
    def __next__(self):
        if self.n == 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1
print(list(Countdown()))""",
            output="[3, 2, 1]",
            point="__next__ returns a value or raises StopIteration.",
        ),
        Slide(
            title="An iterator is used up",
            text="Once an iterator has handed out everything, it stays empty. A list is different: every loop over it makes a fresh iterator.",
            code=r"""it = iter([1, 2, 3])
print(sum(it))
print(sum(it))
print(list(it))
nums = [1, 2, 3]
print(sum(nums), sum(nums))""",
            output="6\n0\n[]\n6 6",
            point="Loop over an iterator twice and the second time sees nothing.",
        ),
        Slide(
            title="range is not an iterator",
            text="range is an iterable that can be looped over as often as you like. You only get a one-shot iterator when you call iter() on it.",
            code=r"""r = range(3)
print(list(r), list(r))
print(hasattr(r, "__next__"))
it = iter(r)
print(next(it), next(it))
print(len(r), 2 in r)""",
            output="[0, 1, 2] [0, 1, 2]\nFalse\n0 1\n3 True",
            point="range can be reused and measured; its iterator cannot.",
        ),
        Slide(
            title="What reversed() and sorted() return",
            text="sorted() builds a brand-new list. reversed() builds nothing: it returns a small iterator that walks the original backwards.",
            code=r"""nums = [3, 1, 2]
print(type(reversed(nums)).__name__)
print(type(sorted(nums)).__name__)
print(list(reversed(nums)))
print(sorted("cab"))""",
            output="list_reverseiterator\nlist\n[2, 1, 3]\n['a', 'b', 'c']",
            point="sorted() gives a list; reversed() gives an iterator.",
        ),
        Slide(
            title="enumerate and zip are lazy",
            text="enumerate and zip do not build a list up front. They produce one pair at a time, as you ask for it.",
            code=r"""pairs = zip("ab", [1, 2])
print(type(pairs).__name__)
print(next(pairs))
print(list(pairs))
print(list(enumerate("xy", start=1)))""",
            output="zip\n('a', 1)\n[('b', 2)]\n[(1, 'x'), (2, 'y')]",
            point="zip and enumerate are iterators: pairs come out only when asked for.",
        ),
        Slide(
            title="iter(callable, sentinel)",
            text="With two arguments, iter() keeps calling a function with no arguments until it returns the sentinel value, which ends the loop.",
            code=r"""stack = [9, 3, 2, 1]
print(list(iter(stack.pop, 9)))
print(stack)""",
            output="[1, 2, 3]\n[]",
            point="iter(f, stop) calls f() repeatedly and stops when f() returns stop.",
        ),
        Slide(
            title="itertools.tee: copies of an iterator",
            text="tee splits one iterator into several independent ones, so each can be read from the start. Do not use the original afterwards.",
            code=r"""from itertools import tee
a, b = tee(iter([1, 2, 3]))
print(list(a))
print(list(b))
print(list(a))""",
            output="[1, 2, 3]\n[1, 2, 3]\n[]",
            point="tee gives you several readers, but each one is still used up after one pass.",
        ),
        Slide(
            title="A pipeline of generators",
            text="Generators can feed each other. Each stage pulls one item at a time from the stage before it, so nothing is built in bulk.",
            code=r"""def nums():
    yield from range(1, 6)
def squares(xs):
    for x in xs:
        yield x * x
def evens(xs):
    for x in xs:
        if x % 2 == 0:
            yield x
print(list(evens(squares(nums()))))""",
            output="[4, 16]",
            point="Chain small generators like pipes: each handles one item at a time.",
        ),
        Slide(
            title="next(it, default)",
            text="Give next() a second argument and it returns that instead of raising StopIteration when there is nothing left.",
            code=r"""it = iter([1])
print(next(it, "none"))
print(next(it, "none"))
print(next(iter([]), None))""",
            output="1\nnone\nNone",
            point="next(it, default) is the safe way to peek at the first item.",
        ),
        Slide(
            title="Dict views are live",
            text="keys(), values() and items() are views of the dict, not copies, so they show later changes. Adding keys while looping over the dict is an error.",
            code=r"""d = {"a": 1}
keys = d.keys()
d["b"] = 2
print(list(keys))
try:
    for k in d:
        d["c"] = 3
except RuntimeError as e:
    print(type(e).__name__)""",
            output="['a', 'b']\nRuntimeError",
            point="A view follows the dict; do not resize the dict mid-loop.",
        ),
        Slide(
            title="Who consumes iterators",
            text="in, list(), sum(), join() and unpacking all pull items from an iterator. Whatever they take is gone for the next user.",
            code=r"""it = iter("abc")
print("b" in it)
print(list(it))
x, y = iter([1, 2])
print(x, y)
print("-".join(iter("abc")))""",
            output="True\n['c']\n1 2\na-b-c",
            point="Testing 'in' on an iterator eats the items it looked at.",
        ),
        Slide(
            title="Generators are iterators already",
            text="A generator object has __next__ and iter() of it is itself, so you never write the iterator class by hand when a generator will do.",
            code=r"""def gen():
    yield 1
g = gen()
print(iter(g) is g)
print(hasattr(g, "__next__"))
print(next(g))
print(next(g, "end"))""",
            output="True\nTrue\n1\nend",
            point="A generator function is the shortest way to make an iterator.",
        ),
    ),
)
