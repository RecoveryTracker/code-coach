"""Gotchas, Python, the second helping: more programs where the obvious reading is a trap.

Same rules as content_py.py: every answer is held to a real run by tests/test_gotchas_content.py, the
wrong options are real misreads, nothing depends on randomness, the clock or identity, and each program
prints one line (or, with raises=True, dies with the named error having printed nothing). These cards
come after the first module in the deck, so py-score-90 and py-loop-var-list stay first.
"""

from __future__ import annotations

from .items import Item, make

q = make("python")

ITEMS: tuple[Item, ...] = (
    # ── Copies, aliases and what del does ──────────────────────────────────
    q("deepcopy-nested", '''
        import copy
        a = [[1, 2], [3]]
        b = copy.deepcopy(a)
        b[0].append(9)
        print(a, b)
    ''', "[[1, 2], [3]] [[1, 2, 9], [3]]",
      ["[[1, 2, 9], [3]] [[1, 2, 9], [3]]", "[[1, 2], [3]] [[1, 2], [3]]",
       "[[1, 2, 9], [3]] [[1, 2], [3]]"],
      "deepcopy copies the inner lists too",
      """A plain `.copy()` or `list(a)` would share the inner lists, which is why the earlier trap bites.
      `copy.deepcopy` rebuilds every level, so appending to the copy's inner list leaves `a` alone."""),

    q("same-list-twice", '''
        x = [1, 2]
        y = [x, x]
        y[0].append(3)
        print(y)
    ''', "[[1, 2, 3], [1, 2, 3]]", ["[[1, 2, 3], [1, 2]]", "[[1, 2], [1, 2]]", "[[1, 2], [1, 2], 3]"],
      "Two slots, one list",
      """`[x, x]` does not copy anything: both slots hold the very same list object. Changing it through
      `y[0]` changes what `y[1]` shows too, because there is only one list."""),

    q("dict-copy-shallow", '''
        d = {"k": [1]}
        e = dict(d)
        e["k"].append(2)
        e["z"] = 0
        print(d)
    ''', "{'k': [1, 2]}", ["{'k': [1]}", "{'k': [1, 2], 'z': 0}", "{'k': [1], 'z': 0}"],
      "A copied dict still shares its values",
      """`dict(d)` makes a new dict but reuses the same value objects. Adding the key `z` only touches the
      copy, yet the list under `k` is one object seen from both dicts, so the `2` shows up in `d`."""),

    q("tuple-plus-equals-list", '''
        t = ([1], 2)
        try:
            t[0] += [9]
        except TypeError:
            pass
        print(t)
    ''', "([1, 9], 2)", ["([1], 2)", "TypeError", "([1, 9], 2, 9)"],
      "The += runs, then the assignment back into the tuple fails",
      """`t[0] += [9]` first extends the inner list in place, which works, and only then tries to store the
      result back into `t[0]`, which a tuple refuses. The error is real and the change happened anyway."""),

    q("del-name", '''
        a = [1, 2, 3]
        b = a
        del a
        print(b)
    ''', "[1, 2, 3]", ["[]", "NameError", "None"],
      "del removes a name, not the object",
      """`del a` unbinds the name `a` and nothing else. The list is still alive because `b` points at it,
      so printing `b` is fine."""),

    q("del-slice", '''
        a = [1, 2, 3]
        b = a
        del a[:]
        print(b)
    ''', "[]", ["[1, 2, 3]", "NameError", "None"],
      "del on a slice empties the list itself",
      """`del a[:]` deletes every item from the list object, and `b` is that same object, so it is empty
      too. Compare `del a`, which only removes the name."""),

    q("append-vs-extend", '''
        a = [1]
        a.append([2, 3])
        a.extend([4, 5])
        print(len(a))
    ''', "4", ["5", "3", "6"],
      "append adds one item, extend adds each item",
      """`append([2, 3])` adds the whole list as one element, so `a` is `[1, [2, 3]]`. `extend` then adds
      4 and 5 separately, giving four elements in all."""),

    q("remove-first-only", '''
        a = [1, 2, 1, 3]
        a.remove(1)
        print(a)
    ''', "[2, 1, 3]", ["[2, 3]", "[1, 2, 3]", "[2, 1]"],
      "remove deletes only the first match",
      """`list.remove(x)` removes the first item equal to `x` and stops. The second 1 survives; to drop
      them all you need a comprehension or a loop that rebuilds the list."""),

    q("list-plus-equals-string", '''
        a = [1]
        a += "ab"
        print(a)
    ''', "[1, 'a', 'b']", ["[1, 'ab']", "TypeError", "['ab', 1]"],
      "+= on a list takes any iterable",
      """`a += x` means `a.extend(x)` for lists, and a string is an iterable of characters, so each letter is
      added on its own. `a + "ab"` would be a TypeError, but `+=` is more forgiving."""),

    q("list-contains-itself", '''
        a = [1, 2]
        a.append(a)
        print(a)
    ''', "[1, 2, [...]]", ["[1, 2, [1, 2]]", "RecursionError", "[1, 2]"],
      "A list can hold itself",
      """The appended item is the list itself, not a snapshot of it. Python spots the loop when printing and
      shows `[...]` instead of recursing forever."""),

    q("slice-assign-self", '''
        x = [1, 2, 3]
        x[1:] = x
        print(x)
    ''', "[1, 1, 2, 3]", ["[1, 2, 3, 1, 2, 3]", "[1, 1, 1, 1]", "[1, 2, 3]"],
      "The right side is copied before the slice is replaced",
      """Python turns the right-hand side into its own list first, so it is `[1, 2, 3]` no matter what the
      assignment does to `x`. Replacing `x[1:]` with that gives `[1, 1, 2, 3]`."""),

    q("extended-slice-assign", '''
        x = [1, 2, 3, 4]
        x[::2] = [0, 0]
        print(x)
    ''', "[0, 2, 0, 4]", ["[0, 0, 3, 4]", "[0, 0]", "[1, 0, 3, 0]"],
      "A stepped slice assigns to every other item",
      """`x[::2]` is items 0 and 2, so the two zeros land there and the rest stays. A stepped slice must
      receive exactly as many values as it has places, unlike a plain `x[a:b]`."""),

    q("append-returns-none", '''
        a = [1, 2]
        b = a.append(3)
        print(b, a)
    ''', "None [1, 2, 3]", ["[1, 2, 3] [1, 2, 3]", "None [1, 2]", "3 [1, 2, 3]"],
      "Methods that change a list in place return None",
      """`append` changes `a` and returns nothing, so `b` is None. Writing `a = a.append(3)` is a classic
      way to lose a list."""),

    q("list-index-bool", '''
        print("abc"[True], [10, 20][False], [10, 20][True + True - 1])
    ''', "b 10 20", ["a 20 10", "TypeError", "b 20 20"],
      "True and False work as the indexes 1 and 0",
      """`bool` is a subclass of `int`, so `True` is 1 and `False` is 0 anywhere an index is wanted. That
      gives "b", 10, and `True + True - 1` is 1, which is 20."""),

    q("bool-sum", '''
        print(True + True, sum([True, False, True]), True * 5)
    ''', "2 2 5", ["True 2 5", "2 3 5", "TypeError"],
      "Booleans are numbers",
      """`True` is 1 and `False` is 0 in arithmetic, so adding or summing booleans counts the true ones.
      There is no special bool addition that stays a bool."""),

    # ── Classes, inheritance and methods ───────────────────────────────────
    q("class-list-plus-equals", '''
        class A:
            items = []

        a, b = A(), A()
        a.items += [1]
        print(b.items, A.items is a.items)
    ''', "[1] True", ["[] False", "[1] False", "[] True"],
      "+= on a shared class list changes the shared list",
      """`a.items += [1]` reads the class's list, extends it in place, and then stores it on the instance
      as well. The list is still the one object on the class, so `b` sees the 1 and `A.items is a.items`."""),

    q("init-mutable-default", '''
        class Bag:
            def __init__(self, items=[]):
                self.items = items

        a, b = Bag(), Bag()
        a.items.append(1)
        print(b.items)
    ''', "[1]", ["[]", "[1, 1]", "AttributeError"],
      "One default list for every instance",
      """The default `[]` is made once when `def __init__` runs, so every `Bag()` that skips the argument
      gets that same list. The usual fix is `items=None` and then `self.items = items or []`."""),

    q("super-chain-mro", '''
        class A:
            def hi(self): return "A"
        class B(A):
            def hi(self): return "B" + super().hi()
        class C(A):
            def hi(self): return "C" + super().hi()
        class D(B, C):
            def hi(self): return "D" + super().hi()

        print(D().hi())
    ''', "DBCA", ["DBA", "DCBA", "DB"],
      "super() follows the MRO, not just the parent",
      """In `B`, `super()` means "the next class after B in D's method resolution order", which is C, not A.
      The order is D, B, C, A, so every class in the diamond is visited exactly once."""),

    q("diamond-attribute", '''
        class A:
            x = "A"
        class B(A):
            pass
        class C(A):
            x = "C"
        class D(B, C):
            pass

        print(D.x)
    ''', "C", ["A", "B", "AttributeError"],
      "C comes before A in the lookup order",
      """The order is D, B, C, A. `B` does not define `x`, so the search carries on to `C`, which does, and
      it never reaches `A`. Parents are not simply searched depth first."""),

    q("missing-super-init", '''
        class A:
            def __init__(self):
                self.x = 1

        class B(A):
            def __init__(self):
                self.y = 2

        print(hasattr(B(), "x"))
    ''', "False", ["True", "AttributeError", "None"],
      "A subclass __init__ replaces the parent's",
      """Defining `__init__` in `B` means `A.__init__` is never called unless you call it, usually with
      `super().__init__()`. So `x` is never set."""),

    q("property-read-only", '''
        class T:
            def __init__(self):
                self._c = 0

            @property
            def c(self):
                return self._c

        T().c = 5
    ''', "AttributeError", ["0", "5", "TypeError"],
      "A property without a setter is read-only",
      """`@property` alone gives a getter only. Assigning to it raises AttributeError, and the value is not
      silently stored somewhere else.""", raises=True),

    q("property-not-in-dict", '''
        class P:
            def __init__(self):
                self._v = 1

            @property
            def v(self):
                return self._v

        print(P().__dict__)
    ''', "{'_v': 1}", ["{'v': 1}", "{}", "{'_v': 1, 'v': 1}"],
      "A property lives on the class, not in the instance",
      """The instance only stores what `__init__` assigned: `_v`. The name `v` is a descriptor on the
      class, which computes its value when read and adds nothing to `__dict__`."""),

    q("eq-without-hash", '''
        class P:
            def __init__(self, x):
                self.x = x

            def __eq__(self, other):
                return self.x == other.x

        try:
            print(len({P(1), P(1)}))
        except TypeError:
            print("unhashable")
    ''', "unhashable", ["1", "2", "TypeError"],
      "Defining __eq__ alone removes __hash__",
      """When a class defines `__eq__` and not `__hash__`, Python sets `__hash__` to None, so its instances
      cannot go in a set or be dict keys. Add a `__hash__` that matches the equality."""),

    q("ne-follows-eq", '''
        class P:
            def __init__(self, x):
                self.x = x

            def __eq__(self, other):
                return self.x == other.x

        print(P(1) == P(1), P(1) != P(1), P(1) == P(2))
    ''', "True False False", ["False False False", "True True False", "True False True"],
      "!= is derived from __eq__",
      """Python 3 gives `!=` the opposite of `__eq__` for free, so you do not need to write `__ne__`. Without
      any `__eq__`, two separate instances would compare unequal."""),

    q("str-vs-repr-in-list", '''
        class P:
            def __str__(self): return "str"
            def __repr__(self): return "repr"

        print(P(), [P()])
    ''', "str [repr]", ["str [str]", "repr [repr]", "repr [str]"],
      "print uses __str__, containers show __repr__",
      """`print(P())` asks for the friendly `str`, but a list shows its items with `repr`. That is why a
      list of objects often prints their debugging form."""),

    q("class-body-comprehension", '''
        class A:
            x = 2
            ys = [x * i for i in range(3)]

        print(A.ys)
    ''', "NameError", ["[0, 2, 4]", "[0, 0, 0]", "[]"],
      "A comprehension in a class body cannot see the class's names",
      """Only the outermost iterable (`range(3)`) is evaluated in the class scope. The `x * i` runs in its
      own function-like scope, which skips the class body, so `x` is not found.""", raises=True),

    q("method-reads-class-name", '''
        class A:
            n = 3

            def f(self):
                return n

        print(A().f())
    ''', "NameError", ["3", "None", "AttributeError"],
      "Class variables need self. or the class name",
      """Inside a method, a bare `n` looks in the function, then in the module, but never in the class body.
      You must write `self.n` or `A.n`.""", raises=True),

    q("method-missing-self", '''
        class A:
            def f():
                return 1

        print(A().f())
    ''', "TypeError", ["1", "None", "NameError"],
      "Calling a method passes the instance automatically",
      """`A().f()` is really `A.f(the_instance)`, so a method with no parameters gets one argument too many.
      The error says `f()` takes 0 positional arguments but 1 was given.""", raises=True),

    q("init-returns-value", '''
        class A:
            def __init__(self):
                return 1

        print(A())
    ''', "TypeError", ["1", "None", "<A object>"],
      "__init__ must return None",
      """The constructor builds the object for you, so `__init__` only sets it up and may not return a value.
      Returning anything but None raises TypeError when you call `A()`.""", raises=True),

    q("classmethod-subclass", '''
        class A:
            @classmethod
            def make(cls):
                return cls.__name__

        class B(A):
            pass

        print(B.make(), A.make())
    ''', "B A", ["A A", "B B", "make make"],
      "A classmethod receives the class it was called on",
      """`cls` is whichever class you called the method on, not the one that defines it. That is how
      alternative constructors build instances of the subclass."""),

    q("class-attr-after-override", '''
        class A:
            x = 1

        a = A()
        a.x = 2
        A.x = 3
        b = A()
        print(a.x, b.x)
    ''', "2 3", ["3 3", "2 1", "2 2"],
      "An instance attribute hides the class one",
      """`a.x = 2` creates `x` on the instance, which wins from then on. Changing `A.x` later is seen by
      instances that never set their own, like `b`, but not by `a`."""),

    q("dataclass-eq-repr", '''
        from dataclasses import dataclass

        @dataclass
        class P:
            x: int

        print(P(1) == P(1), P(1))
    ''', "True P(x=1)", ["False P(x=1)", "True <P object>", "True 1"],
      "@dataclass writes __eq__ and __repr__ for you",
      """A plain class would compare by identity and print an unhelpful object marker. `@dataclass`
      generates equality over the fields and a readable `P(x=1)`."""),

    q("dataclass-mutable-default", '''
        from dataclasses import dataclass

        @dataclass
        class A:
            xs: list = []

        print(A().xs)
    ''', "ValueError", ["[]", "TypeError", "None"],
      "A dataclass refuses a bare list default",
      """Python would share that one list between all instances, the same trap as a mutable default
      argument, so dataclass raises ValueError on purpose. Use `field(default_factory=list)`.""",
      raises=True),

    # ── Numbers, strings and formatting ────────────────────────────────────
    q("fstring-rounding", '''
        print(f"{2.5:.0f} {3.5:.0f} {0.125:.2f}")
    ''', "2 4 0.12", ["3 4 0.13", "3 3 0.12", "2 3 0.13"],
      "Formatting rounds half to even, like round()",
      """Both `2.5` and `0.125` are exact in binary, so they really are halves, and the format rounds them
      to the even neighbour: 2 and 0.12. `3.5` goes up to 4 for the same reason."""),

    q("round-2675", '''
        print(round(2.675, 2), f"{2.675:.2f}")
    ''', "2.67 2.67", ["2.68 2.68", "2.68 2.67", "2.67 2.68"],
      "2.675 is stored a hair below 2.675",
      """The float nearest to 2.675 is actually 2.67499999999999982236431605997495353221893310546875, so it
      rounds down. Neither `round` nor the format spec is wrong; the decimal was never exactly there."""),

    q("round-negative-digits", '''
        print(round(1234.5678, -2), round(-0.5), round(1.5))
    ''', "1200.0 0 2", ["1200 -1 2", "1234.57 0 2", "1200.0 -1 1"],
      "round() with negative digits, and half to even",
      """A negative second argument rounds to hundreds but keeps the float type, so 1200.0. `round(-0.5)`
      goes to the even neighbour 0, and `round(1.5)` is 2."""),

    q("format-spec-mix", '''
        print(f"{1234567:,} {0.256:.1%} {255:x} {5:03d}")
    ''', "1,234,567 25.6% ff 005", ["1234567 0.3% 255 5", "1,234,567 0.256% FF 005",
                                    "1,234,567 25.6% ff 5"],
      "Format specs: comma, percent, hex and zero padding",
      """`,` groups thousands, `.1%` multiplies by 100 and adds a percent sign, `x` is lowercase hex, and
      `03d` pads to width 3 with zeros. They are easy to confuse until you have used them once."""),

    q("fstring-equals", '''
        x = 5
        print(f"{x=} {x + 1=}")
    ''', "x=5 x + 1=6", ["5 6", "x=5 x=6", "x = 5 x + 1 = 6"],
      "f'{x=}' prints the expression and its value",
      """Adding `=` after an expression prints the source text, an equals sign and the value. It keeps the
      spaces you typed, so `{x + 1=}` shows `x + 1=6`."""),

    q("fstring-braces", '''
        print(f"{{x}}", "{}".format("{}"))
    ''', "{x} {}", ["x {}", "{{x}} {}", "ValueError"],
      "Doubled braces are literal braces",
      """In an f-string, `{{` and `}}` print single braces, so `{{x}}` shows `{x}` and nothing is looked up.
      `"{}".format("{}")` fills the slot with the text `{}`, which is not formatted again."""),

    q("title-apostrophe", '''
        print("it's a dog".title())
    ''', "It'S A Dog", ["It's A Dog", "It's a dog", "IT'S A DOG"],
      "title() capitalises after any non-letter",
      """`str.title()` treats the apostrophe as a word break, so the `s` after it is capitalised too. For
      real title case, use `string.capwords` or handle the cases yourself."""),

    q("split-maxsplit", '''
        print("a,b,c".split(",", 1), "a,b,c".rsplit(",", 1))
    ''', "['a', 'b,c'] ['a,b', 'c']", ["['a', 'b', 'c'] ['a', 'b', 'c']", "['a,b', 'c'] ['a', 'b,c']",
                                      "['a'] ['c']"],
      "The second argument is how many splits, from the left or the right",
      """`split(",", 1)` makes one cut at the first comma, and `rsplit` makes its one cut at the last
      comma. The result has one more piece than the number of splits."""),

    q("count-empty", '''
        print("abc".count(""), "abc".find(""), "abc".index("c"))
    ''', "4 0 2", ["0 -1 2", "3 0 2", "4 -1 2"],
      "An empty string matches between every character",
      """There are four gaps in "abc" (before each letter and after the last), so `count("")` is 4. And
      `find("")` succeeds at position 0 rather than returning -1."""),

    q("negative-step-slices", '''
        s = "abcdef"
        print(s[4:1:-1], s[1:4:-1] or "empty", s[:-4:-1])
    ''', "edc empty fed", ["cde empty fed", "edc bcd def", "edcb empty fedc"],
      "Slice bounds are walked in the step's direction",
      """With a negative step the slice starts at the first index and walks left, stopping before the second
      one: `s[4:1:-1]` is "edc". `s[1:4:-1]` would have to walk left from 1 to reach 4, so it is empty."""),

    q("string-times-negative", '''
        print(len("abc" * -1), len([0] * -3), len("ab" * 0))
    ''', "0 0 0", ["3 3 2", "ValueError", "-3 -3 0"],
      "Repeating a sequence a negative number of times gives empty",
      """`seq * n` with `n` below 1 quietly gives an empty sequence, not an error. This is one reason
      `[0] * n` is safe when `n` happens to be zero or negative."""),

    q("unicode-digits", '''
        print(int("٣"), "٣".isdigit(), "²".isdigit(), "²".isdecimal())
    ''', "3 True True False", ["ValueError", "3 True False False", "3 False True False"],
      "Python reads digits from other scripts",
      """`int()` accepts Arabic-Indic digits like ٣ and gives 3. A superscript `²` counts as `isdigit` but
      not `isdecimal`, and `int("²")` would fail, so checking `isdigit` before `int` is not enough."""),

    q("int-parse-spaces", '''
        print(int(" 42\\n"), float(" 1e2 "), int("1_000"))
    ''', "42 100.0 1000", ["ValueError", "42 1e2 1000", "42 100.0 1"],
      "int() and float() trim whitespace and allow underscores",
      """Surrounding whitespace and newlines are ignored, exponent notation is understood, and underscores
      between digits are allowed, just as in source code. `int("4 2")` would still fail."""),

    q("int-bases", '''
        print(int("0x1f", 16), int("z", 36), 0o10 + 0b11)
    ''', "31 35 11", ["Error", "0 35 11", "31 26 5"],
      "int() takes a base, and literals have prefixes",
      """With base 16 the `0x` prefix is allowed, and base 36 uses the letters up to z as 35. In source,
      `0o10` is eight and `0b11` is three, so they add up to 11."""),

    q("int-of-text-float", '''
        print(int("3.9"))
    ''', "ValueError", ["3", "4", "3.9"],
      "int() will not read a decimal point",
      """`int(3.9)` truncates to 3, but `int("3.9")` is text that is not a whole number, so it raises
      ValueError. Go through float first: `int(float("3.9"))`.""", raises=True),

    q("divmod-negative", '''
        print(divmod(-7, 2), divmod(7, -2), -7 % -3)
    ''', "(-4, 1) (-4, -1) -1", ["(-3, -1) (-3, 1) -1", "(-4, 1) (-3, 1) 2", "(-3, -1) (-4, -1) 2"],
      "Floor division and % keep the sign of the divisor",
      """`//` rounds toward minus infinity and `%` is whatever makes `a == (a // b) * b + a % b` true. The
      remainder therefore takes the sign of the right operand, not of the left one."""),

    q("float-floor-div", '''
        print(7 // 2.0, -7 // 2.0, type(7 // 2.0).__name__)
    ''', "3.0 -4.0 float", ["3 -4 int", "3.0 -3.0 float", "3.5 -3.5 float"],
      "// with a float gives a float, still floored",
      """Floor division does not turn into integer division when one side is a float: it still floors, but
      the result stays a float, `3.0`. And -3.5 floors to -4.0, not to -3.0."""),

    q("bitwise-not", '''
        print(~5, ~-1, -~5)
    ''', "-6 0 6", ["-5 1 5", "-6 1 4", "6 0 -6"],
      "~x is -x - 1",
      """`~` flips every bit, which in two's complement means `-x - 1`. So `~5` is -6, `~-1` is 0, and
      `-~5` is minus minus six, which is 6."""),

    q("shift-and-precedence", '''
        print(1 << 2 + 1, 6 & 3 == 2, 2 ** 3 ^ 1)
    ''', "8 True 9", ["5 False 9", "8 False 8", "5 True 8"],
      "+ binds tighter than <<, and & tighter than ==",
      """`1 << 2 + 1` adds first and shifts by 3. Unlike C, Python's `&` binds tighter than `==`, so `6 & 3`
      is 2 and then `2 == 2` is True. `2 ** 3 ^ 1` is `8 ^ 1`, which is 9."""),

    q("int-float-exact", '''
        print(float(2**53 + 1) == 2**53 + 1, 2**53 == float(2**53))
    ''', "False True", ["True True", "False False", "True False"],
      "Ints and floats are compared exactly",
      """The float nearest to 2**53 + 1 is 2**53, so `float(...)` loses the +1. Python then compares that float
      with the exact int and sees different numbers, while 2**53 itself survives the trip."""),

    q("loop-sum-of-tenths", '''
        total = 0
        for _ in range(10):
            total += 0.1
        print(total == 1.0, 0.1 * 10 == 1.0)
    ''', "False True", ["True True", "False False", "True False"],
      "Adding tenths ten times is not the same as multiplying",
      """Each addition rounds, and the errors pile up to 0.9999999999999999. One multiplication rounds only
      once and lands exactly on 1.0, so the two ways of writing ten tenths disagree. (Even the built-in
      `sum` now compensates for this, so only a hand-written loop shows it.)"""),

    q("floor-ceil-negative", '''
        import math
        print(math.floor(-0.5), math.ceil(-0.5), int(-0.5))
    ''', "-1 0 0", ["0 -1 0", "-1 -1 -1", "-1 0 -1"],
      "floor goes down, int() goes toward zero",
      """`math.floor(-0.5)` is -1 because it always goes down. `ceil` and `int` both give 0, with no minus
      sign, since the result is an integer and integers have no negative zero."""),

    q("negative-zero-float", '''
        print(-0.0, -0.0 == 0.0, str(-0))
    ''', "-0.0 True 0", ["0.0 True 0", "-0.0 False -0", "0.0 False 0"],
      "Floats have a negative zero; ints do not",
      """`-0.0` is a real float value that prints with its sign but compares equal to `0.0`. `-0` is just the
      int 0, so its text has no minus."""),

    q("int-division-types", '''
        print(str(10 / 2), 10 // 2, 2 ** -1, 4 ** 0.5)
    ''', "5.0 5 0.5 2.0", ["5 5 0.5 2", "5.0 5.0 0.5 2.0", "5.0 5 0 2.0"],
      "/ and ** can turn ints into floats",
      """`/` always gives a float, even for an exact split, so `10 / 2` is `5.0`. A negative power gives a
      float, and a fractional power does too, so only `//` stays an int here."""),

    # ── Sorting, dicts, sets and iteration ─────────────────────────────────
    q("sorted-key-stable", '''
        print(sorted(["b", "A", "a", "B"], key=str.lower))
    ''', "['A', 'a', 'b', 'B']", ["['a', 'A', 'b', 'B']", "['A', 'B', 'a', 'b']", "['A', 'a', 'B', 'b']"],
      "Equal keys keep their original order",
      """`sorted` is stable: items whose keys tie stay in the order they came in. "A" came before "a", and
      "b" before "B", so those pairs stay that way instead of being ordered by case."""),

    q("sorted-reverse-stable", '''
        pairs = [("a", 1), ("b", 1), ("c", 2)]
        print(sorted(pairs, key=lambda p: p[1], reverse=True))
    ''', "[('c', 2), ('a', 1), ('b', 1)]", ["[('c', 2), ('b', 1), ('a', 1)]", "[('a', 1), ('b', 1), ('c', 2)]",
                                           "[('b', 1), ('a', 1), ('c', 2)]"],
      "reverse=True does not reverse ties",
      """`reverse=True` keeps equal items in their original order, as if sorting descending and stably, not as
      if reversing the finished list. That is why `a` still comes before `b`."""),

    q("max-key-ties", '''
        print(max(["bb", "aa", "c"], key=len), min(["bb", "aa", "c", "d"], key=len))
    ''', "bb c", ["aa c", "bb d", "aa d"],
      "max and min return the first of equal items",
      """When several items tie for the best key, `max` and `min` hand back the first one they met. "bb" and
      "aa" both have length 2, so "bb" wins; the same goes for "c" and "d"."""),

    q("max-default", '''
        print(max([], default=7), max([0, -1], default=7))
    ''', "7 0", ["7 7", "ValueError", "None 0"],
      "default= is used only for an empty iterable",
      """`max([])` would raise ValueError, so `default` says what to return instead. It is not a floor: a
      non-empty list ignores it entirely."""),

    q("max-of-dict", '''
        d = {"a": 3, "b": 1}
        print(max(d), max(d, key=d.get), max(d.values()))
    ''', "b a 3", ["a a 3", "3 a 3", "b b 1"],
      "max() of a dict looks at its keys",
      """Iterating a dict gives its keys, so `max(d)` compares "a" and "b" as text and picks "b". To find the
      key with the biggest value, pass `key=d.get`."""),

    q("enumerate-start", '''
        print(dict(enumerate("ab", 5)))
    ''', "{5: 'a', 6: 'b'}", ["{0: 'a', 1: 'b'}", "{'a': 5, 'b': 6}", "{5: 'a', 5: 'b'}"],
      "enumerate's second argument is the first index",
      """`enumerate(x, start)` only changes the counter, not which items you get. The pairs are (5, 'a') and
      (6, 'b'), and `dict` turns each pair into a key and value."""),

    q("zip-star-transpose", '''
        m = [[1, 2, 3], [4, 5, 6]]
        print(list(zip(*m)))
    ''', "[(1, 4), (2, 5), (3, 6)]", ["[[1, 4], [2, 5], [3, 6]]", "[(1, 2, 3), (4, 5, 6)]", "[(1, 4), (2, 5)]"],
      "zip(*rows) flips rows into columns, as tuples",
      """`*m` spreads the rows out as separate arguments, so `zip` pairs up their first items, second items and
      so on. It builds tuples, not lists."""),

    q("dict-zip-duplicates", '''
        print(dict(zip("aab", [1, 2, 3])))
    ''', "{'a': 2, 'b': 3}", ["{'a': 1, 'b': 3}", "{'a': 3, 'b': 3}", "{'a': [1, 2], 'b': 3}"],
      "A repeated key keeps its first place and its last value",
      """Pairs are added in order, and the second `('a', 2)` overwrites the value of the existing key. The
      dict never holds two `a`s and nothing is merged into a list."""),

    q("defaultdict-touch", '''
        from collections import defaultdict

        d = defaultdict(int)
        d["a"] += 1
        d["b"]
        print(sorted(d), d.get("c"), len(d))
    ''', "['a', 'b'] None 2", ["['a'] None 1", "['a', 'b', 'c'] 0 3", "['a', 'b'] 0 2"],
      "Reading a missing key in a defaultdict adds it",
      """`d["b"]` calls the factory and inserts the key, even though the value is thrown away. `.get` is
      the exception: it never creates anything and returns None for a missing key."""),

    q("setdefault-returns", '''
        d = {"a": 1}
        print(d.setdefault("a", 9), d.setdefault("b", 9), d)
    ''', "1 9 {'a': 1, 'b': 9}", ["9 9 {'a': 9, 'b': 9}", "1 9 {'a': 1}", "1 None {'a': 1, 'b': 9}"],
      "setdefault only sets what is missing, and returns the value",
      """For an existing key it changes nothing and returns the stored 1. For a new key it stores 9 and
      returns it, so the dict gains `b`."""),

    q("get-default-evaluated", '''
        calls = []

        def fallback():
            calls.append(1)
            return 0

        {"a": 1}.get("a", fallback())
        print(len(calls))
    ''', "1", ["0", "2", "TypeError"],
      "The default argument is computed even when the key exists",
      """Arguments are evaluated before the call, so `fallback()` runs whether or not `get` ends up needing
      it. If the default is expensive, use `if key in d` or a defaultdict instead."""),

    q("dict-comprehension-collision", '''
        print({len(w): w for w in ["a", "bb", "c", "dd"]})
    ''', "{1: 'c', 2: 'dd'}", ["{1: 'a', 2: 'bb'}", "{1: ['a', 'c'], 2: ['bb', 'dd']}", "{'a': 1, 'bb': 2}"],
      "Later items overwrite earlier ones with the same key",
      """Two words share each length, so each key is set twice and the last word wins. Nothing groups them
      together; for that you need setdefault, a defaultdict or itertools."""),

    q("dict-merge-order", '''
        a = {"x": 1, "y": 2}
        b = {"y": 3, "z": 4}
        print({**a, **b}, {**b, **a})
    ''', "{'x': 1, 'y': 3, 'z': 4} {'y': 2, 'z': 4, 'x': 1}", ["{'x': 1, 'y': 2, 'z': 4} {'y': 3, 'z': 4, 'x': 1}",
      "{'x': 1, 'y': 3, 'z': 4} {'x': 1, 'y': 2, 'z': 4}", "{'x': 1, 'y': 3, 'z': 4} {'y': 3, 'z': 4, 'x': 1}"],
      "The later dict wins, and keys keep their first position",
      """In `{**a, **b}` the value from `b` replaces `y` but `y` stays where `a` put it. Swapping the order
      swaps both who wins and the order the keys appear in."""),

    q("in-dict-values", '''
        d = {"a": 1}
        print("a" in d, 1 in d, 1 in d.values())
    ''', "True False True", ["True True True", "False False True", "True True False"],
      "`in` on a dict checks the keys",
      """Membership on a dict means "is this a key?", so 1 is not found, though it is among the values. Ask
      `d.values()` when you mean the values."""),

    q("unpack-dict-keys", '''
        d = {"ab": 1, "cd": 2}
        print([(x, y) for x, y in d])
    ''', "[('a', 'b'), ('c', 'd')]", ["[('ab', 1), ('cd', 2)]", "ValueError", "[('a', 1), ('c', 2)]"],
      "Looping over a dict gives keys, and a two-letter key unpacks",
      """Each loop item is a key, here the string "ab", and `x, y = "ab"` quietly splits it into letters.
      You wanted `d.items()`, which gives the (key, value) pairs."""),

    q("set-difference-letters", '''
        print(sorted(set("banana") - set("an")), len(set("hello")))
    ''', "['b'] 4", ["['b', 'n'] 5", "['b', 'a'] 4", "[] 4"],
      "Sets of a string hold its distinct characters",
      """`set("banana")` is {b, a, n}; taking away {a, n} leaves b. "hello" has four different letters, since
      the repeated l counts once."""),

    q("set-int-order", '''
        print({10, 3, 8, 1})
    ''', "{8, 1, 10, 3}", ["{1, 3, 8, 10}", "{10, 3, 8, 1}", "{10, 8, 3, 1}"],
      "A set has no promised order, and it is not sorted",
      """Small ints land in a table slot given by their value modulo the table size, so 8 sits in slot 0,
      then 1, then 10 (slot 2) and 3. Never rely on this; call `sorted` if order matters."""),

    q("subset-strict", '''
        print({1, 2} < {1, 2}, {1, 2} <= {1, 2}, {1} < {1, 2})
    ''', "False True True", ["True True True", "False False True", "True False True"],
      "< is a strict subset, <= allows equal",
      """A set is not a strict subset of itself, so `<` is False for equal sets while `<=` is True. Both
      operators work as "is contained in" for sets rather than ordering them."""),

    q("range-equality", '''
        a, b = range(0, 6, 2), range(0, 5, 2)
        print(range(3) == range(3), range(0) == range(5, 5), a == b)
    ''', "True True True", ["True False False", "False False False", "True True False"],
      "Ranges are equal when they produce the same numbers",
      """Two ranges compare by the sequence they describe, not by their arguments. Both empty ranges are
      equal, and `range(0, 6, 2)` and `range(0, 5, 2)` both give 0, 2, 4."""),

    q("in-string-vs-list", '''
        print("ab" in "abc", "ab" in ["abc"], "ab" in ("ab",))
    ''', "True False True", ["True True True", "False False True", "True False False"],
      "in means substring for text and equality for lists",
      """On a string, `in` looks for a substring. On a list or tuple it asks whether any element equals the
      item, and "ab" does not equal "abc"."""),

    q("unhashable-tuple-key", '''
        d = {(1, [2]): 3}
        print(d)
    ''', "TypeError", ["{(1, [2]): 3}", "ValueError", "{(1, 2): 3}"],
      "A tuple is only hashable if everything inside is",
      """Tuples are immutable, but a key must be hashable all the way down, and a list inside is not. The
      error is raised the moment the dict is built.""", raises=True),

    q("sort-none-mixed", '''
        print(sorted([3, None, 1]))
    ''', "TypeError", ["[None, 1, 3]", "[1, 3, None]", "[3, None, 1]"],
      "Python 3 will not order None against numbers",
      """Python 2 sorted everything against everything. Python 3 raises TypeError when asked whether None is
      less than 3, so you must filter out or replace the None first.""", raises=True),

    q("join-ints", '''
        print(",".join([1, 2, 3]))
    ''', "TypeError", ["1,2,3", "123", "[1, 2, 3]"],
      "join only joins strings",
      """`str.join` does not convert anything for you, so a list of ints fails. Use
      `",".join(map(str, nums))`.""", raises=True),

    q("sum-of-strings", '''
        print(sum(["a", "b"]))
    ''', "TypeError", ["ab", "0ab", "ba"],
      "sum starts at the number 0",
      """`sum` begins with 0 and adds each item, so it tries `0 + "a"` and fails. Python even refuses
      `sum(words, "")` and tells you to use `"".join`.""", raises=True),

    # ── Functions, decorators, generators and scope ────────────────────────
    q("args-kwargs-split", '''
        def f(a, *args, b=0, **kw):
            return (a, args, b, kw)

        print(f(1, 2, 3, b=4, c=5))
    ''', "(1, (2, 3), 4, {'c': 5})", ["(1, (2, 3, 4), 0, {'c': 5})", "(1, [2, 3], 4, {'c': 5})",
                                       "(1, (2, 3), 0, {'b': 4, 'c': 5})"],
      "After *args, parameters are keyword-only",
      """The extra positional values 2 and 3 go into the tuple `args`. `b` comes after `*args`, so it can
      only be set by name, and `c` is left over for `**kw`."""),

    q("keyword-only", '''
        def f(a, *, b):
            return a + b

        print(f(1, 2))
    ''', "TypeError", ["3", "1", "2"],
      "A bare * makes everything after it keyword-only",
      """`b` must be passed as `b=2`. Giving it positionally leaves it missing and also supplies one
      argument too many, so Python raises TypeError.""", raises=True),

    q("default-names-earlier", '''
        def f(a, b=a):
            return b

        print(f(1))
    ''', "NameError", ["1", "None", "TypeError"],
      "A default cannot use another parameter",
      """Defaults are evaluated once, when `def` runs, in the surrounding scope where no `a` exists. The
      error appears at definition, before `f(1)` is ever called.""", raises=True),

    q("star-unpack-split", '''
        first, *rest = "hey"
        print(first, rest)
    ''', "h ['e', 'y']", ["h ey", "hey []", "h ('e', 'y')"],
      "A starred name collects the rest as a list",
      """The star target always becomes a list, whatever you unpacked, and here it takes the remaining
      letters one by one. It would be an empty list if only one item were left over."""),

    q("print-returns-none", '''
        x = print("a", end="")
        print(x)
    ''', "aNone", ["a", "a None", "None"],
      "print() returns None",
      """The first `print` writes "a" with no newline and hands back None, which is stored in `x`. The second
      print then writes "None" straight after it."""),

    q("missing-return", '''
        def sign(n):
            if n > 0:
                return "+"
            elif n < 0:
                return "-"

        print(sign(0), sign(0) is None)
    ''', "None True", ["0 False", "'' True", "None False"],
      "No return means None",
      """When the function runs off its end, it returns None. For 0 neither branch is taken, so you get None
      rather than an error or an empty string."""),

    q("shadow-builtin", '''
        list = [1, 2]
        print(list((3, 4)))
    ''', "TypeError", ["[3, 4]", "[1, 2]", "NameError"],
      "Assigning to a builtin's name hides it",
      """After `list = [1, 2]`, the name `list` is your list, not the builtin type, and a list cannot be
      called. Names like `list`, `sum`, `max` and `id` are easy to shadow by accident.""", raises=True),

    q("decorator-order", '''
        def a(f): return lambda: "A" + f()
        def b(f): return lambda: "B" + f()

        @a
        @b
        def hi():
            return "!"

        print(hi())
    ''', "AB!", ["BA!", "A!", "B!"],
      "Decorators apply from the bottom up",
      """`@b` wraps `hi` first, then `@a` wraps that. Calling it runs the outermost wrapper first, so A is
      added before B."""),

    q("wraps-name", '''
        import functools
        def deco(f):
            @functools.wraps(f)
            def inner(): return f()
            return inner

        def plain(f):
            def inner(): return f()
            return inner

        @deco
        def one(): pass
        @plain
        def two(): pass
        print(one.__name__, two.__name__)
    ''', "one inner", ["one two", "inner inner", "deco plain"],
      "Without functools.wraps a decorated function is called 'inner'",
      """A decorator replaces the function with its wrapper, so the wrapper's name is what you see unless
      `functools.wraps` copies the original's name and docstring over."""),

    q("generator-send", '''
        def g():
            got = yield 1
            yield got * 2

        it = g()
        print(next(it), it.send(5))
    ''', "1 10", ["1 2", "1 5", "1 None"],
      "send() becomes the value of the paused yield",
      """`next` runs to the first `yield` and gives 1. `send(5)` resumes there, making `got` equal 5, and the
      generator then yields `got * 2`, which is 10."""),

    q("yield-from-return", '''
        def inner():
            yield 1
            return "done"

        def outer():
            r = yield from inner()
            yield r

        print(list(outer()))
    ''', "[1, 'done']", ["[1]", "[1, None]", "['done']"],
      "yield from evaluates to the inner return value",
      """`yield from` passes along everything `inner` yields, and when it finishes, the expression's value is
      what `inner` returned. A `for` loop over `inner()` would never see that return value."""),

    q("next-default", '''
        g = (x for x in [1])
        next(g)
        print(next(g, "end"))
    ''', "end", ["StopIteration", "None", "1"],
      "next() with a default never raises StopIteration",
      """The generator has one item, which the first `next` already took. The second call would raise
      StopIteration, but the default is returned instead."""),

    q("groupby-unsorted", '''
        from itertools import groupby

        print([(k, len(list(g))) for k, g in groupby("aabaa")])
    ''', "[('a', 2), ('b', 1), ('a', 2)]", ["[('a', 4), ('b', 1)]", "[('a', 2), ('b', 1)]",
                                          "[('a', 4), ('b', 1), ('a', 4)]"],
      "groupby only groups neighbours",
      """It starts a new group every time the key changes, not when it has seen a key before. Sort first (by
      the same key) if you want one group per value."""),

    q("groupby-lazy-groups", '''
        from itertools import groupby

        groups = list(groupby("aab"))
        print([list(g) for _, g in groups])
    ''', "[[], []]", ["[['a', 'a'], ['b']]", "[['a', 'a']]", "[['a'], ['b']]"],
      "Each group is a live view that dies when groupby moves on",
      """The groups share the one underlying iterator. `list(groupby(...))` runs it to the end, so by the
      time you open a group there is nothing left in it. Use each group before asking for the next."""),

    q("global-vs-nonlocal", '''
        x = 0

        def outer():
            x = 1
            def inner():
                global x
                x = 2
            inner()
            return x

        print(outer(), x)
    ''', "1 2", ["2 2", "1 0", "2 0"],
      "global skips the enclosing function",
      """`global x` in `inner` binds to the module's `x`, not the `x = 1` in `outer`. So `outer` still
      returns its own 1 and the module-level `x` becomes 2. `nonlocal` is the one that targets `outer`."""),

    q("nonlocal-counter", '''
        def make():
            n = 0
            def tick():
                nonlocal n
                n += 1
                return n
            return tick

        a, b = make(), make()
        a(); a()
        print(a(), b())
    ''', "3 1", ["3 3", "1 1", "3 4"],
      "Each call to make() gets its own n",
      """`nonlocal n` lets `tick` change the `n` of the `make` call that created it. Two calls to `make` mean
      two separate counters, so `b` starts from zero."""),

    q("map-lambda-fresh", '''
        adders = list(map(lambda i: (lambda x: x + i), range(3)))
        print(adders[0](10), adders[2](10))
    ''', "10 12", ["12 12", "10 10", "12 10"],
      "A lambda made inside another function gets its own i",
      """Each call of the outer lambda has its own `i`, and the inner lambda captures that one. Unlike a lambda
      written straight in a loop, these do not all share the final value."""),

    q("any-short-circuit", '''
        seen = []

        def check(n):
            seen.append(n)
            return n > 1

        any(check(n) for n in [1, 2, 3, 4])
        print(seen)
    ''', "[1, 2]", ["[1, 2, 3, 4]", "[2]", "[1]"],
      "any() stops at the first true",
      """The generator is lazy and `any` quits as soon as it finds a true value, here at 2. With a list
      comprehension, `[check(n) for ...]` would have run for every item first."""),

    q("assert-tuple", '''
        assert (1 == 2, "never fails")
        print("passed")
    ''', "passed", ["AssertionError", "never fails", "1 == 2"],
      "A parenthesised assert is a non-empty tuple",
      """`assert (cond, msg)` asserts the tuple, and a non-empty tuple is always truthy. Python even warns
      about it. Write `assert cond, msg` with no brackets."""),

    q("name-is-main", '''
        print(__name__)
    ''', "__main__", ["main", "card", "None"],
      "A script's own __name__ is '__main__'",
      """Python names the file you run `__main__`, which is what `if __name__ == "__main__":` tests. When the
      same file is imported, `__name__` is the module's file name instead."""),

    q("type-hints-ignored", '''
        def double(n: int) -> int:
            return n * 2

        print(double("ab"))
    ''', "abab", ["TypeError", "ab", "ValueError"],
      "Type hints are not checked at run time",
      """The annotations are just notes for readers and tools like mypy. Python calls the function with a
      string, and `"ab" * 2` is a perfectly good expression."""),

    q("bytes-vs-str", '''
        print(b"abc" == "abc", b"abc"[0], b"abc"[:1])
    ''', "False 97 b'a'", ["True 97 b'a'", "False a b'a'", "False 97 97"],
      "Indexing bytes gives an int, slicing gives bytes",
      """Bytes and text are different types and are never equal. `b"abc"[0]` is the number 97, but a slice
      stays a bytes object."""),

    q("encode-length", '''
        s = "caf\\u00e9"
        print(len(s), len(s.encode()), len(s.encode("utf-16-le")))
    ''', "4 5 8", ["4 4 4", "5 5 8", "4 5 4"],
      "len counts characters; encoding counts bytes",
      """The text has four characters, but in UTF-8 the accented one takes two bytes, so five. In UTF-16 every
      character here takes two bytes, so eight."""),

    q("nan-comparisons", '''
        nan = float("nan")
        print(nan == nan, nan in [nan], [nan] == [nan])
    ''', "False True True", ["False False False", "True True True", "False False True"],
      "nan is not equal to itself, but containers check identity first",
      """`nan == nan` is False by the floating point rules. But `in` and list equality first ask whether it is
      the very same object, and only then compare with `==`, so the same nan is found."""),

    q("empty-list-vs-false", '''
        print([] == False, not [], bool([]) == False)
    ''', "False True True", ["True True True", "False False True", "True False False"],
      "An empty list is falsy, but it is not equal to False",
      """`not []` and `bool([])` use the list's truthiness, which is False. A direct `==` compares a list with a
      boolean, and those are never equal."""),

    # ── Errors, with-blocks and control flow ───────────────────────────────
    q("except-order", '''
        try:
            1 / 0
        except Exception:
            print("general")
        except ZeroDivisionError:
            print("specific")
    ''', "general", ["specific", "general specific", "ZeroDivisionError"],
      "The first matching except wins",
      """`ZeroDivisionError` is a kind of `Exception`, so the first clause already catches it, and the more
      specific one below can never run. Put narrow handlers before broad ones."""),

    q("finally-masks-error", '''
        def f():
            try:
                raise ValueError("a")
            finally:
                raise KeyError("b")

        try:
            f()
        except Exception as e:
            print(type(e).__name__, type(e.__context__).__name__)
    ''', "KeyError ValueError", ["ValueError KeyError", "KeyError NoneType", "ValueError NoneType"],
      "An error in finally replaces the first one",
      """The KeyError from the `finally` block is the one that escapes. The earlier ValueError is not lost
      entirely: Python keeps it as the new error's `__context__`."""),

    q("except-name-deleted", '''
        try:
            1 / 0
        except ZeroDivisionError as e:
            pass

        print(e)
    ''', "NameError", ["division by zero", "None", "ZeroDivisionError"],
      "The 'as e' name is deleted when the except block ends",
      """Python removes `e` at the end of the handler, to avoid keeping the traceback alive in a cycle. Using
      it afterwards gives NameError; copy it to another name inside the block if you need it.""",
      raises=True),

    q("suppress-skips-rest", '''
        from contextlib import suppress

        with suppress(KeyError):
            {}["a"]
            print("after")
        print("done")
    ''', "done", ["after done", "after", "KeyError"],
      "suppress ends the whole with-block, not just one line",
      """When the lookup raises KeyError, the `with` body stops right there and the error is swallowed. The
      `print("after")` line never runs; execution carries on after the block."""),

    q("with-enter-exit-order", '''
        out = []

        class C:
            def __init__(self, n): self.n = n
            def __enter__(self): out.append("in" + self.n); return self
            def __exit__(self, *a): out.append("out" + self.n)

        with C("1"), C("2"):
            out.append("body")
        print(*out)
    ''', "in1 in2 body out2 out1", ["in1 in2 body out1 out2", "in1 body out1 in2 out2",
                                    "in2 in1 body out1 out2"],
      "Context managers leave in reverse order",
      """Two managers in one `with` behave like nested blocks: the first one entered is the last one left.
      That is also why resources opened later are closed first."""),

    q("while-else", '''
        n = 0
        while n < 3:
            n += 1
            if n == 5:
                break
        else:
            print("else", n)
    ''', "else 3", ["3", "else 5", "nothing"],
      "while/else runs when the loop was not broken out of",
      """The `else` of a loop means "no break happened". The condition simply became false at 3, `break` was
      never reached, so the else block runs."""),

    q("match-capture-name", '''
        color = "red"

        match "blue":
            case color:
                print("captured", color)
            case "blue":
                print("blue")
    ''', "SyntaxError", ["captured blue", "blue", "captured red"],
      "In match, a bare name is a capture pattern, not a comparison",
      """`case color:` matches anything and binds it to `color`, so Python refuses the later case as
      unreachable. To compare with a variable you need a dotted name like `Color.RED`, or a guard.""",
      raises=True),

    q("mod-in-string-format", '''
        print("%s %s" % "ab")
    ''', "TypeError", ["a b", "ab ab", "ab"],
      "% formatting takes a tuple, and a string is not one",
      """`"%s %s" % "ab"` supplies one value for two slots, so it fails. A single string is one argument, not
      two letters. You need `("a", "b")`.""", raises=True),

    q("percent-single-tuple", '''
        t = (1, 2)
        print("%s" % (t,), "%d%%" % 50)
    ''', "(1, 2) 50%", ["1 50%", "TypeError", "(1, 2) 50"],
      "Wrap a tuple in a tuple to format it",
      """A bare tuple on the right of `%` is read as the list of values to fill in, so you have to wrap it in
      another tuple to print it as one thing. `%%` prints a literal percent sign."""),

    q("and-or-chain-values", '''
        print(repr(None or 0 or ""), 1 and 2 and 3, 1 and 0 and 3)
    ''', "'' 3 0", ["False 3 0", "None 3 0", "'' True False"],
      "and / or return one of their operands",
      """`or` returns the first truthy operand, or the last one if none is, so this chain ends on the empty
      string. `and` returns the first falsy operand, or the last one if all are truthy: 3, then 0."""),
)
