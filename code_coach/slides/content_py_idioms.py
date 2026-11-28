"""Pythonic Idioms: a passive deck. Outputs were worked out by hand; the oracle test runs the code."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 75

DECK = Deck(
    id="py-idioms",
    title="Pythonic Idioms",
    language="python",
    blurb="The short, natural ways Python programmers write everyday things.",
    slides=(
        Slide(
            title="Swap with tuple unpacking",
            text="No temporary variable needed: build a pair on the right, then unpack it into the names on the left.",
            code=r"""a, b = 1, 2
a, b = b, a
print(a, b)""",
            output="2 1",
            point="a, b = b, a",
        ),
        Slide(
            title="enumerate, not range(len())",
            text="When you need each item and its position, enumerate hands you both. start= chooses the first number.",
            code=r"""for i, c in enumerate("ab", start=1):
    print(i, c)""",
            output="1 a\n2 b",
            point="for i, x in enumerate(items):",
        ),
        Slide(
            title="zip to walk two lists",
            text="zip pairs up the items at the same position in two lists, and stops at the shorter one. No index needed.",
            code=r"""nums = [1, 2, 3]
names = ["a", "b", "c"]
for n, s in zip(nums, names):
    print(n, s)""",
            output="1 a\n2 b\n3 c",
            point="for x, y in zip(xs, ys):",
        ),
        Slide(
            title="dict.get with a default",
            text="d[key] raises an error for a missing key. d.get(key, default) gives you the default instead, and leaves the dict alone.",
            code=r"""d = {"a": 1}
print(d.get("a", 0), d.get("z", 0))
print(d)""",
            output="1 0\n{'a': 1}",
            point="d.get(key, fallback) never raises.",
        ),
        Slide(
            title="any, all and sum",
            text="any is true if at least one item passes, all if every item passes. sum can add up a generator, so you need not build a list first.",
            code=r"""nums = [2, 4, 5]
print(any(n % 2 == 1 for n in nums))
print(all(n > 0 for n in nums))
print(sum(n * n for n in nums))""",
            output="True\nTrue\n45",
            point="Feed any, all and sum a generator, no list needed.",
        ),
        Slide(
            title="sorted with key=",
            text="key= is a function that says what to sort BY. len sorts by length. reverse=True flips the order. The original list is untouched.",
            code=r"""words = ["pear", "fig", "apple"]
print(sorted(words, key=len))
print(sorted(words, key=len, reverse=True))""",
            output="['fig', 'pear', 'apple']\n['apple', 'pear', 'fig']",
            point="sorted(items, key=function)",
        ),
        Slide(
            title="join, not +=",
            text="Gluing strings together in a loop with += makes many throwaway strings. Collect the pieces and join them once with a separator.",
            code=r"""print(", ".join(["a", "b", "c"]))
print("-".join(str(n) for n in range(3)))""",
            output="a, b, c\n0-1-2",
            point="separator.join(pieces)",
        ),
        Slide(
            title="Comprehensions over map and filter",
            text="A comprehension says the same as map plus filter, but reads like plain English and needs no lambda.",
            code=r"""nums = [1, 2, 3, 4]
print(list(map(lambda n: n * 2, filter(lambda n: n % 2 == 0, nums))))
print([n * 2 for n in nums if n % 2 == 0])""",
            output="[4, 8]\n[4, 8]",
            point="[change(x) for x in xs if keep(x)]",
        ),
        Slide(
            title="Unpacking with *rest",
            text="A starred name soaks up whatever is left over, as a list. It can sit at the front, middle or end.",
            code=r"""first, *rest = [1, 2, 3]
print(first, rest)
*init, last = [1, 2, 3]
print(init, last)""",
            output="1 [2, 3]\n[1, 2] 3",
            point="first, *rest = items splits head from tail.",
        ),
        Slide(
            title="Conditional expression",
            text="'A if test else B' is a value, so it fits inside an assignment or a print without a full if statement.",
            code=r"""n = 7
print("odd" if n % 2 else "even")
label = "big" if n > 5 else "small"
print(label)""",
            output="odd\nbig",
            point="value_if_true if test else value_if_false",
        ),
        Slide(
            title="with for resources",
            text="with closes things for you when its block ends. Files work the same way, as in with open(name) as f. Here a text buffer stands in for a file.",
            code=r"""import io
with io.StringIO("a\nb\n") as f:
    lines = f.read().split()
print(f.closed)
print(lines)""",
            output="True\n['a', 'b']",
            point="Anything that needs closing belongs in a with.",
        ),
        Slide(
            title="Ask forgiveness (EAFP)",
            text="Rather than check whether text is a number first, just try the conversion and handle the failure. It is shorter and cannot go stale between the check and the use.",
            code=r"""def to_int(s):
    try:
        return int(s)
    except ValueError:
        return None
print(to_int("12"), to_int("x"))""",
            output="12 None",
            point="Try it, and catch the specific error if it fails.",
        ),
        Slide(
            title="if not items",
            text="Empty containers count as false, so you need not compare their length or compare with []. Just test the list itself.",
            code=r"""items = []
if not items:
    print("empty")
items.append(1)
if items:
    print("has", len(items))""",
            output="empty\nhas 1",
            point="if items: / if not items: beats len(items) == 0.",
        ),
        Slide(
            title="f-strings",
            text="Put an f before the quotes and write values inside braces. After a colon you can format them: .2f for two decimals, 03d for three digits padded with zeros.",
            code=r"""name = "Ann"
n = 3
print(f"{name} has {n} items")
print(f"{3.14159:.2f} {n:03d}")""",
            output="Ann has 3 items\n3.14 003",
            point='f"{value:format}" replaces +, str() and %.',
        ),
        Slide(
            title="The walrus operator :=",
            text=":= assigns a value and gives it back in one step. It saves repeating a calculation in a comprehension, or a read before a while loop.",
            code=r"""data = [1, 2, 3, 4, 5]
print([y for x in data if (y := x * x) > 5])
chunks = iter([3, 2, 0, 9])
while (n := next(chunks)) != 0:
    print(n)""",
            output="[9, 16, 25]\n3\n2",
            point="(name := expression) assigns and uses at once.",
        ),
    ),
)
