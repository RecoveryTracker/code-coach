"""Comprehensions and Generators: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 55

DECK = Deck(
    id="py-comprehensions",
    title="Comprehensions and Generators",
    language="python",
    blurb="Building lists in one line, then producing values lazily, one at a time, with generators.",
    slides=(
        Slide(
            title="List comprehensions",
            text="[expression for item in things] builds a list in one line. It does the same as a loop that appends, just shorter. Read it as: give me this expression, for each item.",
            code=r"""squares = [n * n for n in range(5)]
print(squares)
print([c.upper() for c in "abc"])
loop = []
for n in range(5):
    loop.append(n * n)
print(loop == squares)""",
            output="[0, 1, 4, 9, 16]\n['A', 'B', 'C']\nTrue",
            point="A comprehension is a loop-and-append squeezed into one expression.",
        ),
        Slide(
            title="Dict and set comprehensions",
            text="Change the brackets and you change the result. Curly braces with key: value make a dict, and curly braces with a single expression make a set.",
            code=r"""print({n: n * n for n in range(3)})
print(sorted({len(w) for w in ["a", "bb", "cc"]}))
print({c for c in "aab"} == {"a", "b"})""",
            output="{0: 0, 1: 1, 2: 4}\n[1, 2]\nTrue",
            point="[...] list, {k: v ...} dict, {...} set.",
        ),
        Slide(
            title="Filtering with if",
            text="An if at the END of a comprehension keeps only the items that pass. Items that fail are skipped completely, so the result can be shorter than the input.",
            code=r"""nums = [1, 2, 3, 4, 5, 6]
print([n for n in nums if n % 2 == 0])
print([n for n in nums if n > 2 and n < 5])""",
            output="[2, 4, 6]\n[3, 4]",
            point="'for x in xs if cond' filters: items that fail are dropped.",
        ),
        Slide(
            title="if-else in the value",
            text="An if-else placed BEFORE the for is a conditional expression: it chooses what each item becomes, and nothing is dropped. An if placed after the for filters instead. Mixing the two up is a classic slip.",
            code=r"""nums = [1, 2, 3, 4]
print(["even" if n % 2 == 0 else "odd" for n in nums])
print([n if n > 2 else 0 for n in nums])
print([n for n in nums if n > 2])""",
            output="['odd', 'even', 'odd', 'even']\n[0, 0, 3, 4]\n[3, 4]",
            point="if-else before the for changes values; a lone if after it removes items.",
        ),
        Slide(
            title="Nested comprehensions",
            text="Two for parts run like nested loops, with the first for as the outer loop. That is the classic way to flatten a list of lists. A comprehension inside a comprehension keeps the rows.",
            code=r"""grid = [[1, 2], [3, 4], [5]]
flat = [x for row in grid for x in row]
print(flat)
print([[x * 2 for x in row] for row in grid])
print([(a, b) for a in "xy" for b in (1, 2)])""",
            output="[1, 2, 3, 4, 5]\n[[2, 4], [6, 8], [10]]\n[('x', 1), ('x', 2), ('y', 1), ('y', 2)]",
            point="Read the for parts left to right, like nested loops, outer first.",
        ),
        Slide(
            title="Generator expressions",
            text="Use round brackets instead of square ones and you get a generator: it does not build the list, it makes each value only when asked. Pass it straight to a function like sum, with no extra brackets.",
            code=r"""gen = (n * n for n in range(3))
print(type(gen).__name__)
print(list(gen))
print(sum(n * n for n in range(4)))""",
            output="generator\n[0, 1, 4]\n14",
            point="(x for ...) is a lazy recipe for values, not a finished list.",
        ),
        Slide(
            title="Lazy: nothing runs until asked",
            text="A generator does no work when it is created. Each call to next runs it just far enough to produce one value. That is what lazy means.",
            code=r"""def noisy(n):
    print("making", n)
    return n
gen = (noisy(n) for n in range(2))
print("created")
print(next(gen))""",
            output="created\nmaking 0\n0",
            point="Creating a generator costs nothing; the work happens as you pull values.",
        ),
        Slide(
            title="yield: a generator function",
            text="A function with yield in it is a generator function. Calling it does not run the body; it gives you a generator. Each yield hands out one value, and for loops and list() collect them.",
            code=r"""def count_up(n):
    for i in range(1, n + 1):
        yield i
print(list(count_up(3)))
for x in count_up(2):
    print(x)""",
            output="[1, 2, 3]\n1\n2",
            point="yield gives a value out and remembers where it was.",
        ),
        Slide(
            title="yield pauses the function",
            text="At each yield the function freezes, with all its variables, and the loop gets the value. When the loop asks for the next one, the function resumes right after the yield. Watch the lines interleave.",
            code=r"""def two():
    print("start")
    yield 1
    print("middle")
    yield 2
    print("end")
for v in two():
    print("got", v)""",
            output="start\ngot 1\nmiddle\ngot 2\nend",
            point="A generator runs in bursts, pausing at every yield.",
        ),
        Slide(
            title="next() and StopIteration",
            text="next(it) pulls one value. When there are none left it raises StopIteration, which is how a for loop knows to stop. Give next a second argument and you get that instead of an error.",
            code=r"""it = iter([10, 20])
print(next(it))
print(next(it))
print(next(it, "done"))
try:
    next(it)
except StopIteration:
    print("StopIteration")""",
            output="10\n20\ndone\nStopIteration",
            point="next(it, default) is the safe way to take one value.",
        ),
        Slide(
            title="Generators are one-shot",
            text="A generator can be read once. After it has run out, it stays empty, and a second list() of it gives []. A list keeps its items, so you can read it again and again.",
            code=r"""g = (n for n in range(3))
print(list(g))
print(list(g))
nums = [0, 1, 2]
print(list(nums), list(nums))""",
            output="[0, 1, 2]\n[]\n[0, 1, 2] [0, 1, 2]",
            point="Need the values twice? Make a list, or build a fresh generator.",
        ),
        Slide(
            title="sum, any and all",
            text="These three read a generator and need no list. any stops at the first True and all stops at the first False. any of nothing is False, and all of nothing is True.",
            code=r"""nums = [3, 8, 5]
print(sum(n for n in nums if n > 4))
print(any(n > 7 for n in nums))
print(all(n > 4 for n in nums))
print(any([]), all([]))""",
            output="13\nTrue\nFalse\nFalse True",
            point="any/all/sum over a generator: short, and no big temporary list.",
        ),
        Slide(
            title="yield from",
            text="yield from followed by another iterable passes along each of its items in turn. It replaces a small for loop that just yields every item, and it is neat for flattening.",
            code=r"""def both(a, b):
    yield from a
    yield from b
print(list(both([1, 2], "xy")))
def flat(rows):
    for r in rows:
        yield from r
print(list(flat([[1], [2, 3]])))""",
            output="[1, 2, 'x', 'y']\n[1, 2, 3]",
            point="yield from xs means: yield every item of xs.",
        ),
        Slide(
            title="Infinite generators and islice",
            text="Because values are made on demand, a generator can go on forever, as long as you take only some. itertools.islice cuts out a piece of any iterable, like a slice for generators.",
            code=r"""from itertools import islice
def naturals():
    n = 1
    while True:
        yield n
        n += 1
print(list(islice(naturals(), 4)))
print(list(islice(naturals(), 2, 5)))""",
            output="[1, 2, 3, 4]\n[3, 4, 5]",
            point="An endless generator is fine if you only ever take a few values.",
        ),
        Slide(
            title="Why generators save memory",
            text="A list of a million numbers keeps them all in memory at once. A generator keeps only its current place and makes one value at a time, so it stays tiny however long the stream is. It can also stop early without doing the rest of the work.",
            code=r"""total = sum(n for n in range(1_000_000))
print(total)
first = next(n for n in range(10**12) if n % 7 == 3)
print(first)""",
            output="499999500000\n3",
            point="For a big or endless stream, a generator beats a list.",
        ),
    ),
)
