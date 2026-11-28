"""Lists in Depth: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 41

DECK = Deck(
    id="py-lists",
    title="Lists in Depth",
    language="python",
    blurb="Slicing, changing, sorting and copying lists, and the traps that catch everyone once.",
    slides=(
        Slide(
            title="Indexing, even backwards",
            text="Positions start at 0. A negative position counts from the end, so -1 is the last item. A slice [a:b] makes a new list from a up to, but not including, b.",
            code=r"""a = [10, 20, 30, 40]
print(a[0], a[-1])
print(a[-2])
print(len(a))
print(a[1:3])""",
            output="10 40\n30\n4\n[20, 30]",
            point="a[-1] is the last item; a[1:3] stops before position 3.",
        ),
        Slide(
            title="Slices with a step",
            text="A slice can take every second item with a step, or go backwards with a step of -1. A slice that runs past the end never fails; it just gives what exists, even an empty list.",
            code=r"""a = [0, 1, 2, 3, 4, 5]
print(a[2:])
print(a[:-2])
print(a[::2])
print(a[::-1])
print(a[10:])""",
            output="[2, 3, 4, 5]\n[0, 1, 2, 3]\n[0, 2, 4]\n[5, 4, 3, 2, 1, 0]\n[]",
            point="Slices are forgiving: out-of-range ends are trimmed, not errors.",
        ),
        Slide(
            title="Slice assignment",
            text="You can assign to a slice to replace that stretch with any number of items. An empty slice like a[1:1] is a gap, so assigning there inserts. del with a step removes every second item.",
            code=r"""a = [1, 2, 3, 4, 5]
a[1:3] = [9]
print(a)
a[1:1] = [7, 8]
print(a)
del a[::2]
print(a)""",
            output="[1, 9, 4, 5]\n[1, 7, 8, 9, 4, 5]\n[7, 9, 5]",
            point="a[i:j] = items replaces that stretch, and the list may grow or shrink.",
        ),
        Slide(
            title="append vs extend vs +",
            text="append adds ONE thing, even if it is a list. extend adds each item of another list. The + operator makes a brand-new list and leaves both originals alone.",
            code=r"""a = [1, 2]
a.append([3, 4])
print(a)
b = [1, 2]
b.extend([3, 4])
print(b)
print(b + [5])
print(b)""",
            output="[1, 2, [3, 4]]\n[1, 2, 3, 4]\n[1, 2, 3, 4, 5]\n[1, 2, 3, 4]",
            point="append puts the whole thing in as one item; extend spreads it out.",
        ),
        Slide(
            title="insert, remove, pop, del",
            text="insert(i, x) puts x at position i. remove(x) deletes the first item equal to x. pop() removes and returns the last item, or the one at a position you give. del a[i] removes by position.",
            code=r"""a = [5, 6, 7, 6]
a.insert(0, 4)
a.remove(6)
print(a)
print(a.pop())
print(a.pop(0))
del a[0]
print(a)""",
            output="[4, 5, 7, 6]\n6\n4\n[7]",
            point="remove works by value, del by position, and pop gives the item back.",
        ),
        Slide(
            title="index and count",
            text="index(x) gives the position of the first x, and a second argument says where to start looking. count(x) tells how many there are. If x is missing, index raises a ValueError.",
            code=r"""a = [3, 1, 3, 2]
print(a.index(3))
print(a.index(3, 1))
print(a.count(3))
try:
    a.index(9)
except ValueError:
    print("not found")""",
            output="0\n2\n2\nnot found",
            point="index fails loudly when the item is absent; check with 'in' first.",
        ),
        Slide(
            title="sort vs sorted",
            text="sorted(a) returns a new sorted list and leaves a alone. a.sort() sorts a itself and returns None, so writing a = a.sort() wipes your list. The key= option decides what to compare.",
            code=r"""a = [3, 1, 2]
b = sorted(a)
print(a, b)
r = a.sort()
print(a, r)
print(sorted(["b", "A", "c"], key=str.lower))""",
            output="[3, 1, 2] [1, 2, 3]\n[1, 2, 3] None\n['A', 'b', 'c']",
            point="sort() changes the list and returns None; sorted() returns a new list.",
        ),
        Slide(
            title="reverse vs reversed",
            text="a.reverse() flips the list itself and returns None. reversed(a) leaves a alone and gives a one-pass walker over it backwards, which list() turns into a real list.",
            code=r"""a = [1, 2, 3]
print(list(reversed(a)))
print(a)
print(a.reverse())
print(a)""",
            output="[3, 2, 1]\n[1, 2, 3]\nNone\n[3, 2, 1]",
            point="Methods that change a list in place return None.",
        ),
        Slide(
            title="The [[0]*2]*2 trap",
            text="Multiplying a list of lists repeats the SAME inner list, not copies of it, so changing one row changes them all. Build each row separately with a comprehension instead.",
            code=r"""bad = [[0] * 2] * 2
bad[0][0] = 1
print(bad)
good = [[0] * 2 for _ in range(2)]
good[0][0] = 1
print(good)""",
            output="[[1, 0], [1, 0]]\n[[1, 0], [0, 0]]",
            point="Never write [[0]*n]*m for a grid; use [[0]*n for _ in range(m)].",
        ),
        Slide(
            title="Copying: shallow vs deep",
            text="a[:] and list(a) make a new outer list, but any inner lists are still shared. copy.deepcopy copies everything all the way down, so later changes to the original do not leak in.",
            code=r"""import copy
a = [[1], [2]]
s = a[:]
d = copy.deepcopy(a)
a[0].append(9)
print(s)
print(d)
print(list(a) == a, list(a) is a)""",
            output="[[1, 9], [2]]\n[[1], [2]]\nTrue False",
            point="A shallow copy shares the inner lists; deepcopy does not.",
        ),
        Slide(
            title="'in' checks one by one",
            text="'x in a_list' looks at the items one at a time until it finds x, so a long list is slow to search. A set finds items almost instantly, so for many lookups convert to a set first.",
            code=r"""a = [1, 2, 3]
print(2 in a)
print(5 in a)
s = set(a)
print(2 in s)""",
            output="True\nFalse\nTrue",
            point="Many 'in' checks on a big list? Make a set once and ask that.",
        ),
        Slide(
            title="min, max, sum",
            text="These work on any list of numbers. max and min accept a key= function to decide what 'biggest' means. max of an empty list is an error unless you give default=, and sum can start from a number you choose.",
            code=r"""a = [4, 9, 2]
print(min(a), max(a), sum(a))
print(max(a, key=lambda x: -x))
print(max([], default=0))
print(sum([1, 2], 10))
print(sum([]))""",
            output="2 9 15\n2\n0\n13\n0",
            point="Give max/min a default= so an empty list does not crash.",
        ),
        Slide(
            title="Unpacking with *",
            text="A starred name collects whatever is left over into a list, whichever end it is on. In the other direction, a star in a list literal spreads another list out in place.",
            code=r"""first, *rest = [1, 2, 3, 4]
print(first, rest)
*init, last = [1, 2, 3]
print(init, last)
a, *mid, z = "wxyz"
print(mid)
print([0, *rest, 9])""",
            output="1 [2, 3, 4]\n[1, 2] 3\n['x', 'y']\n[0, 2, 3, 4, 9]",
            point="*name soaks up the extras; [*a, *b] joins lists.",
        ),
        Slide(
            title="A list as a stack",
            text="A stack is last in, first out, like a pile of plates. append puts a plate on top and pop() takes the top one off. stack[-1] peeks at the top, and an empty list is false.",
            code=r"""stack = []
stack.append("a")
stack.append("b")
print(stack.pop())
print(stack[-1])
print(stack)
print(not stack)""",
            output="b\na\n['a']\nFalse",
            point="append and pop() at the end are fast: a list is a perfect stack.",
        ),
        Slide(
            title="enumerate start= and zip",
            text="enumerate counts as you loop, and start= picks the first number. zip walks several lists side by side and stops as soon as the shortest one runs out, quietly ignoring the rest.",
            code=r"""for i, c in enumerate("xy", start=1):
    print(i, c)
print(list(zip([1, 2, 3], "ab")))
print(list(zip("ab", [1, 2], [True, False])))""",
            output="1 x\n2 y\n[(1, 'a'), (2, 'b')]\n[('a', 1, True), ('b', 2, False)]",
            point="zip stops at the shortest input; leftovers are dropped silently.",
        ),
    ),
)
