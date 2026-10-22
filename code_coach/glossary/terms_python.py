"""Words that only Python has (or that mean something different there): None, list, tuple, dict, set,
range, ==/is, f-strings, comprehensions, lambda, self, with ..."""

from __future__ import annotations

from .entry import Entry, py

TERMS: list[Entry] = [
    *py(
        "none",
        "None",
        "Python's value for 'nothing here'. It is what a function gives back when it returns nothing.",
        see=("falsy", "identity", "return"),
        priority=70,
        aka=("nonetype", "null", "nil"),
        detect=(r"\bNone\b",),
        rules=(
            "There is only one None, and it is falsy.",
            "Test for it with 'is None' (or 'is not None'), not with ==.",
            "None is not 0, not '' and not []: None == 0 is False.",
            "A function with no return statement gives None - a common cause of 'None' showing up in output.",
        ),
        example="""
            x = None
            print(x is None, bool(x), x == 0, type(x).__name__)
        """,
        out="True False False NoneType",
    ),
    *py(
        "list",
        "List",
        "An ordered collection of items that you can change, written in square brackets: [3, 1, 2].",
        see=("index", "mutable", "tuple", "comprehension"),
        priority=40,
        aka=("lists", "array", "arrays"),
        detect=(r"(?:[=(,:]|\breturn|\bin|^)\s*\[|\blist\(",),
        rules=(
            "Items keep their order and are numbered from 0; the items can be of different types.",
            "Common methods: append(x), pop(), insert(i, x), remove(x), sort(), reverse().",
            "An empty list [] is falsy.",
            "Changing a list changes it for every name that points at it.",
        ),
        example="""
            nums = [3, 1, 2]
            nums.append(4)
            nums.sort()
            print(nums, len(nums))
        """,
        out="[1, 2, 3, 4] 4",
    ),
    *py(
        "tuple",
        "Tuple",
        "An ordered collection like a list, but it cannot be changed once made. It is written with round brackets: (3, 4).",
        see=("list", "immutable", "unpacking"),
        priority=45,
        aka=("tuples",),
        detect=(
            r"=\s*\([^()\n]*,[^()\n]*\)",
            r"\btuple\(",
            r"\bin\s+\([^()\n]*,[^()\n]*\)\s*:",
            r"\breturn\s+[^\n(\[{]*,",
        ),
        rules=(
            "It is the commas that make a tuple: (1,) is a tuple of one item, but (1) is just the number 1.",
            "You can index and loop over one, but not assign to an item.",
            "Because it cannot change, a tuple can be a dict key; a list cannot.",
            "A function that returns 'two values' is returning one tuple.",
        ),
        example="""
            point = (3, 4)
            x, y = point
            print(point, x + y, (1,), type((1)).__name__)
        """,
        out="(3, 4) 7 (1,) int",
    ),
    *py(
        "dict",
        "Dictionary",
        "A collection of key: value pairs. You look up a value by its key, the way you look up a word in a dictionary.",
        see=("key", "value", "mutable"),
        priority=45,
        aka=("dict", "dictionaries", "map", "hash map", "mapping", "hashmap"),
        detect=(r"\{[^{}\n]*:[^{}\n]*\}", r"\bdict\(", r"\.(?:items|keys|values|get)\("),
        rules=(
            "Keys are unique and must be immutable (strings, numbers, tuples). Values can be anything.",
            "d[key] raises a KeyError if the key is missing; d.get(key, default) does not.",
            "A dict remembers the order its keys were added in.",
            "{} is an empty dict, not an empty set (use set()). Looping over a dict gives its keys.",
        ),
        example="""
            prices = {"apple": 3, "pear": 5}
            prices["fig"] = 9
            print(prices["apple"], prices.get("kiwi", 0), len(prices))
        """,
        out="3 0 3",
    ),
    *py(
        "key",
        "Key",
        "In a dict, the label you look an item up by. Each key goes with exactly one value.",
        see=("dict", "value"),
        priority=40,
        aka=("keys", "key-value", "key value pair"),
        detect=(r"\{[^{}\n]*:[^{}\n]*\}", r"\.(?:items|keys)\(",),
        rules=(
            "Keys in one dict are unique: setting an existing key replaces its value.",
            "d.items() gives (key, value) pairs; d.keys() the keys; d.values() the values.",
            "'k' in d asks whether k is a KEY, not a value.",
        ),
        example="""
            d = {"a": 1, "b": 2}
            for k, v in d.items():
                print(k, v)
            print("a" in d, 2 in d)
        """,
        out="a 1\nb 2\nTrue False",
    ),
    *py(
        "set",
        "Set",
        "A collection of unique items with no order. Adding something already in it changes nothing.",
        see=("list", "dict", "in-operator"),
        priority=45,
        aka=("sets", "frozenset"),
        detect=(r"\bset\(", r"\{[^{}:\n]+\}", r"\.(?:add|discard|union|intersection)\("),
        rules=(
            "Duplicates vanish: {1, 2, 2, 3} has three items.",
            "'x in s' is fast, much faster than 'x in a_list' on big data.",
            "Combine with | (union), & (both) and - (difference).",
            "Items cannot be indexed, and the empty set is set() because {} is an empty dict.",
        ),
        example="""
            s = {1, 2, 2, 3}
            print(len(s), 2 in s, sorted(s | {9}))
        """,
        out="3 True [1, 2, 3, 9]",
    ),
    *py(
        "range",
        "range",
        "A built-in that produces a sequence of whole numbers, mostly to drive a for loop.",
        see=("loop", "off-by-one", "iterable"),
        priority=55,
        aka=("range()",),
        detect=(r"\brange\(",),
        rules=(
            "range(n) gives 0, 1, ... n - 1: the stop number is never included.",
            "range(start, stop) and range(start, stop, step) set where to begin and how far to jump; a negative step counts down.",
            "range(0) is empty, so a loop over it runs zero times. The number of items is stop - start (when step is 1).",
            "list(range(3)) shows the numbers.",
        ),
        example="""
            print(list(range(3)), list(range(2, 8, 2)), list(range(5, 0, -2)), len(range(0)))
        """,
        out="[0, 1, 2] [2, 4, 6] [5, 3, 1] 0",
    ),
    *py(
        "equality",
        "Equality (==)",
        "== asks whether two values are equal - the same contents - and gives True or False.",
        see=("identity", "comparison", "type-conversion"),
        priority=65,
        aka=("==", "!=", "equal", "equals", "equal to", "not equal"),
        detect=(r"(?<![=!<>])==(?!=)|!=",),
        rules=(
            "It compares contents: [1, 2] == [1, 2] is True even for two separate lists.",
            "1 == 1.0 is True, and True == 1 is True; but '1' == 1 is False (no conversion between text and numbers).",
            "!= is the opposite of ==.",
            "A single = is assignment; mixing them up is a very common bug.",
        ),
        example="""
            print(1 == 1.0, "1" == 1, [1, 2] == [1, 2], True == 1)
        """,
        out="True False True True",
    ),
    *py(
        "identity",
        "Identity (is)",
        "'a is b' asks whether two names point at the very same object in memory - not just equal contents.",
        see=("equality", "none", "reference"),
        priority=75,
        aka=("is", "is not", "same object", "id"),
        detect=(r"\bis\s+(?:not\s+)?\w",),
        rules=(
            "Two equal lists made separately are two objects: == is True, is is False.",
            "Use 'is None' and 'is not None' to test for None; use == for everything else.",
            "Do not use 'is' on numbers or strings: Python sometimes shares small ones, so the answer can surprise you.",
        ),
        example="""
            a = [1, 2]
            b = [1, 2]
            print(a == b, a is b, a is a, None is None)
        """,
        out="True False True True",
    ),
    *py(
        "instance",
        "Object (instance)",
        "One thing made from a class. Every object has its own copy of the data, and shares the class's methods.",
        see=("class", "self", "method"),
        priority=40,
        aka=("object", "objects", "instances", "instantiate"),
        detect=(r"\b[A-Z][A-Za-z0-9]*\(",),
        rules=(
            "Dog('Rex') and Dog('Fido') are two separate objects of the same class.",
            "In Python almost everything - numbers, strings, functions - is an object.",
            "isinstance(x, Dog) asks whether x is a Dog.",
        ),
        example="""
            class Dog:
                pass
            a = Dog()
            b = Dog()
            print(type(a).__name__, a is b, isinstance(a, Dog))
        """,
        out="Dog False True",
    ),
    *py(
        "self",
        "self",
        "The first parameter of a method: the object the method was called on, so the method can reach that object's data.",
        see=("class", "method", "instance"),
        priority=55,
        aka=("self.",),
        detect=(r"\bself\b",),
        rules=(
            "Python passes it for you: dog.speak() works like Dog.speak(dog).",
            "self.name = name stores data on this object; plain name = name would only make a local variable.",
            "'self' is a convention, not a keyword, but everyone uses it.",
        ),
        example="""
            class Counter:
                def __init__(self):
                    self.n = 0
                def add(self):
                    self.n += 1
            c = Counter()
            c.add()
            c.add()
            print(c.n)
        """,
        out="2",
    ),
    *py(
        "comprehension",
        "Comprehension",
        "A one-line way to build a list, dict or set from another collection: [n * n for n in nums if n > 1].",
        see=("list", "loop", "iterable"),
        priority=70,
        aka=("list comprehension", "dict comprehension", "set comprehension", "generator expression"),
        detect=(
            r"\[[^\[\]\n]*\bfor\b[^\[\]\n]*\bin\b",
            r"\{[^{}\n]*\bfor\b[^{}\n]*\bin\b",
            r"\([^()\n]*\bfor\b[^()\n]*\bin\b",
        ),
        rules=(
            "Read it as: [what to keep, for each item in something, if a test passes].",
            "The 'if' at the end is optional and filters items out.",
            "Square brackets build a list, braces a set or dict; round brackets make a lazy generator expression.",
            "The loop variable stays inside the comprehension.",
        ),
        example="""
            nums = [1, 2, 3, 4]
            print([n * n for n in nums if n % 2 == 0], {n: n * 2 for n in nums[:2]})
        """,
        out="[4, 16] {1: 2, 2: 4}",
    ),
    *py(
        "lambda",
        "lambda",
        "A small function with no name, written in one line: lambda x: x * 2.",
        see=("function", "callback", "return"),
        priority=60,
        aka=("anonymous function", "lambda function", "arrow function"),
        detect=(r"\blambda\b",),
        rules=(
            "The part after the colon is one expression, and its value is returned automatically.",
            "No statements are allowed inside one: no assignment, no if block (a conditional expression is fine).",
            "Mostly used for short callbacks, such as sorted(items, key=lambda s: len(s)).",
        ),
        example="""
            double = lambda x: x * 2
            print(double(4), sorted(["bb", "a"], key=lambda s: len(s)))
        """,
        out="8 ['a', 'bb']",
    ),
    *py(
        "f-string",
        "f-string",
        "A string with an f in front of the quote. Anything in { } is worked out and put into the text.",
        see=("string", "concatenation", "type-conversion"),
        priority=55,
        aka=("formatted string", "f string"),
        detect=(r"raw:\b[fF][rR]?[\"']|\b[rR][fF][\"']",),
        rules=(
            "Any expression works inside the braces: {n * 2}, {name.upper()}, {len(items)}.",
            "A format after a colon controls the look: {x:.2f} is two decimals, {x:>5} right-aligns in 5 characters.",
            "Write {{ or }} to show a literal brace. No str() is needed for numbers.",
        ),
        example="""
            name = "Ana"
            n = 3
            print(f"{name} has {n * 2} apples, {3.14159:.2f}, {{ok}}")
        """,
        out="Ana has 6 apples, 3.14, {ok}",
    ),
    *py(
        "star-args",
        "*args and **kwargs",
        "A * in a function's parameters collects extra positional arguments into a tuple; ** collects extra named ones into a dict. "
        "In a call, * and ** spread a list or dict back out.",
        see=("parameter", "argument", "unpacking"),
        priority=60,
        aka=("*args", "**kwargs", "args", "kwargs", "star", "splat", "spread", "rest parameter", "varargs"),
        detect=(r"\bdef\b[^\n]*\*\w", r"[(,]\s*\*\*?[A-Za-z_\[(]"),
        rules=(
            "def f(*args, **kwargs) accepts any arguments at all.",
            "print(*[1, 2, 3]) is the same as print(1, 2, 3).",
            "The names args and kwargs are conventions; the * and ** are what matters.",
        ),
        example="""
            def show(*args, **kwargs):
                print(args, kwargs)
            show(1, 2, a=3)
            print(*[4, 5, 6])
        """,
        out="(1, 2) {'a': 3}\n4 5 6",
    ),
    *py(
        "print",
        "print()",
        "The function that shows values on the screen. It is how a program talks to you.",
        see=("function", "return", "string"),
        priority=25,
        aka=("print()", "output", "display"),
        detect=(r"\bprint\(",),
        rules=(
            "Several values are separated by a space: print('a', 1) shows a 1.",
            "sep= and end= change the separator and the ending: print('x', 'y', sep='-', end='!').",
            "print gives back None and does not return what it shows (see return value).",
        ),
        example="""
            print("a", 1, True)
            print("x", "y", sep="-", end="!\\n")
        """,
        out="a 1 True\nx-y!",
    ),
    *py(
        "len",
        "len()",
        "A built-in that counts the items in a collection, or the characters in a string.",
        see=("index", "string", "off-by-one"),
        priority=25,
        aka=("len()", "length"),
        detect=(r"\blen\(",),
        rules=(
            "len('farm') is 4, len([1, 2]) is 2, len({}) is 0.",
            "The last valid index is len(x) - 1.",
            "len(5) is a TypeError: a number has no length.",
        ),
        example="""
            print(len("farm"), len([1, 2]), len({}), len(range(5)))
        """,
        out="4 2 0 5",
    ),
    *py(
        "with",
        "with",
        "A statement that sets something up, runs an indented block, and then always cleans up - most often for files.",
        see=("exception", "indentation"),
        priority=45,
        aka=("context manager", "with open"),
        detect=(r"\bwith\b",),
        rules=(
            "with open('a.txt') as f: opens a file and closes it afterwards, even if the block raises an error.",
            "The name after 'as' is only available while you are using the thing.",
        ),
        example="""
            import io
            with io.StringIO("hello\\nworld") as f:
                print(f.readline().strip())
            print(f.closed)
        """,
        out="hello\nTrue",
    ),
    *py(
        "in-operator",
        "in",
        "The word in asks 'is this inside that?' and gives True or False. (A for loop uses the same word for a different job.)",
        see=("set", "dict", "string"),
        priority=50,
        aka=("not in", "membership", "contains"),
        detect=(r"\bnot\s+in\b", r"\b(?:if|elif|while|and|or|assert)\b[^\n:]*\sin\s"),
        rules=(
            "In a list, tuple or set it looks for an item; in a string it looks for a piece of text; in a dict it looks at the KEYS.",
            "'x not in y' is the opposite.",
            "On a set or dict it is fast; on a long list it checks one item after another.",
        ),
        example="""
            print("a" in "farm", 3 in [1, 2], "k" in {"k": 1}, 4 not in [1, 2])
        """,
        out="True False True True",
    ),
    *py(
        "pass",
        "pass",
        "A statement that does nothing. It fills a spot where Python needs a line but you have nothing to put yet.",
        see=("function", "indentation"),
        priority=25,
        detect=(r"\bpass\b",),
        rules=(
            "A block cannot be empty: def f(): with nothing under it is a syntax error, and pass fixes that.",
            "It is a placeholder, so a function containing only pass returns None.",
        ),
        example="""
            def todo():
                pass
            print(todo())
        """,
        out="None",
    ),
    *py(
        "assert",
        "assert",
        "A statement that checks something you believe is true. If it is false, the program stops with an AssertionError.",
        see=("exception", "condition"),
        priority=35,
        detect=(r"\bassert\b",),
        rules=(
            "assert condition, 'message' - the message is shown when the condition is falsy.",
            "Great for checking your own assumptions and for small tests.",
        ),
        example="""
            try:
                assert 1 + 1 == 3, "math broke"
            except AssertionError as e:
                print(e)
        """,
        out="math broke",
    ),
    *py(
        "enumerate-zip",
        "enumerate and zip",
        "enumerate gives each item together with its position; zip walks several collections side by side.",
        see=("for-loop", "iterable", "unpacking"),
        priority=40,
        aka=("enumerate", "zip"),
        detect=(r"\b(?:enumerate|zip)\(",),
        rules=(
            "for i, item in enumerate(items): gives i = 0, 1, 2 ... without managing a counter yourself.",
            "zip stops at the shortest collection.",
        ),
        example="""
            for i, ch in enumerate("ab"):
                print(i, ch)
            print(list(zip([1, 2], "ab")))
        """,
        out="0 a\n1 b\n[(1, 'a'), (2, 'b')]",
    ),
]
