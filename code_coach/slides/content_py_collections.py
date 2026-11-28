"""collections and itertools: a passive deck. Outputs were worked out by hand; the oracle test runs the code."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 100

DECK = Deck(
    id="py-collections",
    title="collections and itertools",
    language="python",
    blurb="The standard-library containers and iterator tools that replace a lot of hand-written loops: Counter, defaultdict, deque, groupby, product and friends.",
    slides=(
        Slide(
            title="Counter: most_common",
            text="Counter counts anything you give it. most_common(n) lists the n biggest counts, and a missing key simply counts as 0 instead of raising an error.",
            code=r"""from collections import Counter
c = Counter("abracadabra")
print(c.most_common(2))
print(c["z"])""",
            output="[('a', 5), ('b', 2)]\n0",
            point="Counter(items).most_common(k) answers 'what shows up most?'.",
        ),
        Slide(
            title="Counter arithmetic",
            text="Counters can be added and subtracted. Subtraction drops anything that falls to zero or below. Two words are anagrams when their Counters are equal.",
            code=r"""from collections import Counter
a, b = Counter("aab"), Counter("abc")
print(sorted((a + b).items()))
print(sorted((a - b).items()))
print(Counter("listen") == Counter("silent"))""",
            output="[('a', 3), ('b', 2), ('c', 1)]\n[('a', 1)]\nTrue",
            point="Counter equality is the quickest anagram check.",
        ),
        Slide(
            title="defaultdict: group items",
            text="A defaultdict creates a missing value for you the first time you touch a key. With list as the factory, grouping becomes one line per item.",
            code=r"""from collections import defaultdict
groups = defaultdict(list)
for w in ["apple", "bee", "avocado", "bat"]:
    groups[w[0]].append(w)
print(dict(groups))""",
            output="{'a': ['apple', 'avocado'], 'b': ['bee', 'bat']}",
            point="defaultdict(list) means no 'if key not in d' check.",
        ),
        Slide(
            title="deque: appendleft and rotate",
            text="A deque is fast at both ends. appendleft adds at the front. rotate(k) shifts every item k places to the right, and a negative k shifts left, wrapping around.",
            code=r"""from collections import deque
d = deque([1, 2, 3, 4])
d.appendleft(0)
d.rotate(2)
print(list(d))
d.rotate(-1)
print(list(d))""",
            output="[3, 4, 0, 1, 2]\n[4, 0, 1, 2, 3]",
            point="Both ends of a deque are O(1); a list is slow at the front.",
        ),
        Slide(
            title="deque: maxlen keeps the last few",
            text="Give a deque a maxlen and it throws away the oldest item whenever a new one would not fit. It is perfect for 'the last 3 things I saw'.",
            code=r"""from collections import deque
d = deque(maxlen=3)
for n in range(5):
    d.append(n)
print(list(d))
print(d)""",
            output="[2, 3, 4]\ndeque([2, 3, 4], maxlen=3)",
            point="deque(maxlen=k) is a sliding window that forgets by itself.",
        ),
        Slide(
            title="namedtuple",
            text="A namedtuple is a tuple whose spots have names. You can read a field by name or by position, and unpack it like any tuple.",
            code=r"""from collections import namedtuple
Point = namedtuple("Point", "x y")
p = Point(3, 4)
print(p.x, p[1])
print(p)
x, y = p
print(x + y)""",
            output="3 4\nPoint(x=3, y=4)\n7",
            point="namedtuple gives readable fields without writing a class.",
        ),
        Slide(
            title="OrderedDict.move_to_end: an LRU idea",
            text="An OrderedDict remembers order and can move a key to the end. Treat the front as 'least recently used': touch a key to move it back, and popitem(last=False) evicts the oldest.",
            code=r"""from collections import OrderedDict
cache = OrderedDict(a=1, b=2, c=3)
cache.move_to_end("a")
print(list(cache))
cache.popitem(last=False)
print(list(cache))""",
            output="['b', 'c', 'a']\n['c', 'a']",
            point="move_to_end on use + popitem(last=False) on overflow = an LRU cache.",
        ),
        Slide(
            title="ChainMap: layered lookups",
            text="A ChainMap looks a key up in several dicts, in order, and uses the first one that has it. It does not copy, so later changes to a layer show through.",
            code=r"""from collections import ChainMap
defaults = {"color": "red", "size": 1}
mine = {"size": 5}
cfg = ChainMap(mine, defaults)
print(cfg["size"], cfg["color"])
mine["color"] = "blue"
print(cfg["color"])""",
            output="5 red\nblue",
            point="ChainMap(overrides, defaults) is settings with fallbacks.",
        ),
        Slide(
            title="count and cycle with islice",
            text="count() and cycle() never stop, so you cut them with islice(iterator, n), which takes just the first n items. Without islice, list() would run forever.",
            code=r"""from itertools import count, cycle, islice
print(list(islice(count(10, 5), 4)))
print(list(islice(cycle("ab"), 5)))""",
            output="[10, 15, 20, 25]\n['a', 'b', 'a', 'b', 'a']",
            point="Endless iterators are safe as long as islice limits them.",
        ),
        Slide(
            title="accumulate: running totals",
            text="accumulate yields the running total of a list. Give it another function, like max, and it keeps a running version of that instead.",
            code=r"""from itertools import accumulate
print(list(accumulate([1, 2, 3, 4])))
print(list(accumulate([3, 1, 4, 1, 5], max)))""",
            output="[1, 3, 6, 10]\n[3, 3, 4, 4, 5]",
            point="accumulate is the prefix-sum pattern in one call.",
        ),
        Slide(
            title="product: every combination of choices",
            text="product pairs every item of one list with every item of the next, like nested loops. repeat=n uses the same list n times.",
            code=r"""from itertools import product
print(list(product("ab", [1, 2])))
print(len(list(product(range(3), repeat=2))))""",
            output="[('a', 1), ('a', 2), ('b', 1), ('b', 2)]\n9",
            point="product(a, b) is a double for-loop without the nesting.",
        ),
        Slide(
            title="permutations vs combinations",
            text="Permutations care about order, so ('a','b') and ('b','a') are different. Combinations ignore order, so each group appears once. The second argument is the group size.",
            code=r"""from itertools import permutations, combinations
print(list(permutations("abc", 2)))
print(list(combinations("abc", 2)))""",
            output="[('a', 'b'), ('a', 'c'), ('b', 'a'), ('b', 'c'), ('c', 'a'), ('c', 'b')]\n[('a', 'b'), ('a', 'c'), ('b', 'c')]",
            point="Does order matter? Yes: permutations. No: combinations.",
        ),
        Slide(
            title="groupby needs sorted input",
            text="groupby groups only neighbouring equal items, so the same key can come back later as a new group. Sort first if you want each key to appear once.",
            code=r"""from itertools import groupby
data = "aabbbac"
for key, run in groupby(data):
    print(key, len(list(run)))
print([k for k, _ in groupby(sorted(data))])""",
            output="a 2\nb 3\na 1\nc 1\n['a', 'b', 'c']",
            point="groupby splits runs; sort first to group everything.",
        ),
        Slide(
            title="chain and pairwise",
            text="chain walks several iterables as if they were one. pairwise gives each item together with the next one, which is handy for gaps and differences (Python 3.10+).",
            code=r"""from itertools import chain, pairwise
print(list(chain([1, 2], (3,), "ab")))
print(list(pairwise([1, 4, 9, 16])))
print([b - a for a, b in pairwise([1, 4, 9, 16])])""",
            output="[1, 2, 3, 'a', 'b']\n[(1, 4), (4, 9), (9, 16)]\n[3, 5, 7]",
            point="pairwise(xs) replaces the xs[i], xs[i + 1] index loop.",
        ),
        Slide(
            title="zip_longest: do not lose the extras",
            text="zip stops at the shortest list and silently drops the rest. zip_longest keeps going and fills the gaps with None, or with the fillvalue you choose.",
            code=r"""from itertools import zip_longest
print(list(zip([1, 2, 3], "ab")))
print(list(zip_longest([1, 2, 3], "ab")))
print(list(zip_longest([1, 2, 3], "ab", fillvalue=0)))""",
            output="[(1, 'a'), (2, 'b')]\n[(1, 'a'), (2, 'b'), (3, None)]\n[(1, 'a'), (2, 'b'), (3, 0)]",
            point="zip drops extras; zip_longest pads them.",
        ),
    ),
)
