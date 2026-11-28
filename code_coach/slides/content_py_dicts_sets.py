"""Dicts and Sets in Depth: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 42

DECK = Deck(
    id="py-dicts-sets",
    title="Dicts and Sets in Depth",
    language="python",
    blurb="Building, reading, merging and grouping dicts, plus what sets are good at.",
    slides=(
        Slide(
            title="Four ways to make a dict",
            text="Curly braces are the usual way. dict(x=1) takes keyword names, dict can take a list of pairs, and dict.fromkeys gives every key the same starting value. An empty {} is a dict, not a set.",
            code=r"""a = {"x": 1, "y": 2}
b = dict(x=1, y=2)
c = dict([("x", 1), ("y", 2)])
d = dict.fromkeys("ab", 0)
print(a == b == c)
print(d)
print({})""",
            output="True\n{'a': 0, 'b': 0}\n{}",
            point="All these forms build the same kind of dict; {} alone is an empty dict.",
        ),
        Slide(
            title="get and setdefault",
            text="get looks a key up without failing: it gives None, or a default you choose. setdefault gives the value if the key exists, and otherwise stores the default and gives that.",
            code=r"""d = {"a": 1}
print(d.get("a"), d.get("z"), d.get("z", 0))
print(d.setdefault("b", 5))
print(d.setdefault("a", 99))
print(d)""",
            output="1 None 0\n5\n1\n{'a': 1, 'b': 5}",
            point="get never changes the dict; setdefault adds the key when it is missing.",
        ),
        Slide(
            title="keys, values and items",
            text="These three give live views of the dict. Wrap them in list() to see the contents. A view follows later changes to the dict, so it is not a frozen copy.",
            code=r"""d = {"a": 1, "b": 2}
print(list(d))
print(list(d.keys()), list(d.values()))
print(list(d.items()))
ks = d.keys()
d["c"] = 3
print(list(ks))""",
            output="['a', 'b']\n['a', 'b'] [1, 2]\n[('a', 1), ('b', 2)]\n['a', 'b', 'c']",
            point="Looping over a dict gives its keys; .items() gives (key, value) pairs.",
        ),
        Slide(
            title="Insertion order",
            text="A dict remembers the order in which keys were first added. Changing a value keeps the key where it was; deleting a key and adding it again puts it at the end.",
            code=r"""d = {}
d["z"] = 1
d["a"] = 2
d["m"] = 3
print(list(d))
d["z"] = 10
print(list(d))
del d["a"]
d["a"] = 0
print(list(d))""",
            output="['z', 'a', 'm']\n['z', 'a', 'm']\n['z', 'm', 'a']",
            point="Keys come out in the order they were first inserted.",
        ),
        Slide(
            title="update and the | merge",
            text="a | b makes a new dict with everything from both, and the right side wins when a key is in both. update does the same merge but changes a in place. {**b, 'x': 0} is the older spelling.",
            code=r"""a = {"x": 1, "y": 2}
b = {"y": 20, "z": 30}
print(a | b)
a.update(b)
print(a)
print({**b, "x": 0})""",
            output="{'x': 1, 'y': 20, 'z': 30}\n{'x': 1, 'y': 20, 'z': 30}\n{'y': 20, 'z': 30, 'x': 0}",
            point="In a merge, the later dict wins any clash.",
        ),
        Slide(
            title="Dict comprehensions",
            text="A dict comprehension builds a dict in one line: {key: value for item in things}. Add an if at the end to keep only some items. Swapping keys and values is a one-liner too.",
            code=r"""words = ["hi", "hello", "yo"]
print({w: len(w) for w in words})
print({w: len(w) for w in words if len(w) > 2})
d = {"a": 1, "b": 2}
print({v: k for k, v in d.items()})""",
            output="{'hi': 2, 'hello': 5, 'yo': 2}\n{'hello': 5}\n{1: 'a', 2: 'b'}",
            point="{k: v for ...} builds a dict; swap with {v: k for k, v in d.items()}.",
        ),
        Slide(
            title="pop, popitem and del",
            text="pop(key) removes a key and gives back its value, and with a second argument it will not fail if the key is missing. popitem removes and returns the LAST pair added. del removes a key and gives nothing back.",
            code=r"""d = {"a": 1, "b": 2, "c": 3}
print(d.pop("a"))
print(d.pop("zz", "none"))
print(d.popitem())
del d["b"]
print(d)""",
            output="1\nnone\n('c', 3)\n{}",
            point="pop(key, default) is the safe way to remove a key that might be missing.",
        ),
        Slide(
            title="KeyError vs get",
            text="Reading a key that is not there with d[key] raises a KeyError. get returns None instead, and 'in' checks for a key without reading it. Choose d[key] when a missing key is a real bug.",
            code=r"""d = {"a": 1}
try:
    print(d["b"])
except KeyError:
    print("KeyError")
print(d.get("b"))
print("b" in d)""",
            output="KeyError\nNone\nFalse",
            point="d[key] fails loudly; d.get(key) stays quiet. Pick on purpose.",
        ),
        Slide(
            title="Nested dicts",
            text="A dict value can itself be a dict or a list, so you chain the brackets to dig in. Use get with an empty dict to safely go one level deeper, and setdefault to create a level when it is missing.",
            code=r"""users = {"ann": {"age": 30, "tags": ["a", "b"]}}
print(users["ann"]["age"])
users["ann"]["tags"].append("c")
print(users["ann"]["tags"])
print(users.get("bob", {}).get("age"))
users.setdefault("bob", {})["age"] = 5
print(users["bob"])""",
            output="30\n['a', 'b', 'c']\nNone\n{'age': 5}",
            point="Chain brackets to dig down; get(key, {}) protects against a missing level.",
        ),
        Slide(
            title="Keys must be hashable",
            text="A key must be something that can never change, so Python can find it fast. A tuple works; a list does not, and trying raises a TypeError. The same rule applies to the items of a set.",
            code=r"""d = {}
d[(1, 2)] = "tuple ok"
print(d)
try:
    d[[1, 2]] = "list"
except TypeError as e:
    print(type(e).__name__)""",
            output="{(1, 2): 'tuple ok'}\nTypeError",
            point="Numbers, strings and tuples can be keys; lists, dicts and sets cannot.",
        ),
        Slide(
            title="Set operations",
            text="| joins two sets (union), & keeps what both have (intersection), - keeps what only the left has, and ^ keeps what is in exactly one. A set has no order, so the examples print sorted lists.",
            code=r"""a = {1, 2, 3}
b = {3, 4}
print(sorted(a | b))
print(sorted(a & b))
print(sorted(a - b))
print(sorted(a ^ b))
print(2 in a, {1, 2} <= a)""",
            output="[1, 2, 3, 4]\n[3]\n[1, 2]\n[1, 2, 4]\nTrue True",
            point="| union, & both, - only the left, ^ one side only, <= is 'subset of'.",
        ),
        Slide(
            title="Set comprehensions and dedupe",
            text="set(list) throws away repeats, which is the quickest way to remove duplicates. A set comprehension builds a set with the same shape as a list one, but with curly braces.",
            code=r"""nums = [3, 1, 3, 2, 1]
print(sorted(set(nums)))
print(sorted({n * 10 for n in nums}))
print(len({x * x for x in [-2, 2, 3]}))
print(set())""",
            output="[1, 2, 3]\n[10, 20, 30]\n2\nset()",
            point="set(items) removes duplicates; {} is a dict, so an empty set is set().",
        ),
        Slide(
            title="frozenset",
            text="A frozenset is a set that can never change. Because it cannot change it is hashable, so it can be a dict key or sit inside another set. Methods that change it, like add, do not exist.",
            code=r"""f = frozenset([1, 2, 2])
print(sorted(f), len(f))
d = {f: "ok"}
print(d[frozenset([2, 1])])
try:
    f.add(3)
except AttributeError:
    print("frozen")""",
            output="[1, 2] 2\nok\nfrozen",
            point="Need a set as a dict key? Use a frozenset.",
        ),
        Slide(
            title="Grouping with defaultdict(list)",
            text="A defaultdict makes a fresh default value the first time you touch a missing key, so you can append straight away. Here list is the default. Note that merely reading a missing key also creates it.",
            code=r"""from collections import defaultdict
groups = defaultdict(list)
for w in ["ant", "bee", "ape", "bat"]:
    groups[w[0]].append(w)
print(dict(groups))
print(groups["zzz"])
print(len(groups))""",
            output="{'a': ['ant', 'ape'], 'b': ['bee', 'bat']}\n[]\n3",
            point="defaultdict(list) lets you group with no 'if key not in' checks.",
        ),
        Slide(
            title="Counting",
            text="By hand, get(key, 0) + 1 counts items. Counter does it for you and has most_common. Ties keep the order the items first appeared in, and a Counter answers 0 for anything it never saw.",
            code=r"""from collections import Counter
text = "abracadabra"
counts = {}
for ch in text:
    counts[ch] = counts.get(ch, 0) + 1
print(counts)
c = Counter(text)
print(c.most_common(2))
print(c["z"])""",
            output="{'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1}\n[('a', 5), ('b', 2)]\n0",
            point="Counter(items) counts everything; .most_common(n) gives the top n.",
        ),
    ),
)
