"""Predict the output, in Python, for the behaviours interviews circle back to.

The first Python set (predict.py) covers the famous five: the shared
default list, the aliased row, the late-binding lambda, the tuple that
fails and works, the finally that wins. This one is everything an
interviewer reaches for next, grouped by what is being tested:

* Generators - nothing runs until the first next(), the return value hides
  inside StopIteration, send() resumes with a value, and a generator
  expression reads its first iterable now and the rest later.
* Iteration - zip stops at the shortest, a sort is stable even reversed,
  changing a dict's size mid-loop is refused, and a for loop's else runs
  when nothing broke out.
* Scope and closures - a name assigned anywhere in a function is local
  everywhere in it, a default is read at definition, a class body is not
  an enclosing scope, and an except variable is deleted afterwards.
* Data model - __eq__ without __hash__, properties, __slots__, class
  attributes behind instance names, super() in a diamond, and iteration
  falling back to __getitem__.
* Typing and dataclasses - hints are not checked, a mutable default is
  refused, frozen is not a hash, and eq=True without frozen makes a
  dataclass unhashable.
* Numbers and formatting - Decimal strings, the half that is not a half,
  the precedence of unary minus, format specs, and 1 == 1.0 as a key.
* Strings - split with and without an argument, negative-step slices,
  strip taking a set of characters, and interning.
* Standard library - lru_cache hit counts, Counter ties, defaultdict
  creating a key on a read, bisect on duplicates, contextlib ordering and
  the exit code a raised exception skips.
* Asyncio - a coroutine is not running until something drives it, gather
  keeps argument order, a task starts at the next await, and a TaskGroup
  raises an ExceptionGroup.
* Syntax and flow - the walrus, structural matching, a capture pattern
  that looks like a constant, try/else/finally order, the value a
  return has already computed, and exception context.

Every expected output was worked out by hand first and then checked
against the interpreter, and tests/test_predict_pyextra.py keeps
checking. Nothing depends on the clock, the dice, the hash seed of a
string, or the order a set of strings iterates in. The two CPython
details (small-integer caching, interning) are marked as such in their
explanations, since no other implementation promises them.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p

GENERATORS = "Generators"
ITERATION = "Iteration"
SCOPE = "Scope and closures"
DATA_MODEL = "Data model"
TYPING = "Typing and dataclasses"
NUMBERS = "Numbers and formatting"
STRINGS = "Strings"
STDLIB = "Standard library"
ASYNCIO = "Asyncio"
SYNTAX = "Syntax and flow"

PREFIX = "predict-pyx-"


PY_EXTRA_PUZZLES: tuple[Puzzle, ...] = (
    # ── Generators ───────────────────────────────────────────
    _p(
        id="predict-pyx-gen-lazy-start",
        level=2,
        name="Calling a generator function",
        family=GENERATORS,
        code=(
            "def gen():\n"
            '    print("start")\n'
            "    yield 1\n"
            '    print("end")\n'
            "\n"
            "g = gen()\n"
            'print("made")\n'
            "print(next(g))"
        ),
        expect="made\nstart\n1",
        why=(
            "Calling a function that contains `yield` runs none of its "
            "body. It hands back a generator object and stops there, so "
            "`made` prints before `start`. The first next() runs the body "
            "up to the first yield, which is where `start` appears and "
            "where the value 1 comes out. `end` would only print on a "
            "second next()."
        ),
    ),
    _p(
        id="predict-pyx-gen-any-stops",
        level=3,
        name="How much of a generator any() reads",
        family=GENERATORS,
        code=(
            "def noisy():\n"
            "    for i in range(5):\n"
            '        print("tick", i)\n'
            "        yield i\n"
            "\n"
            "print(any(n == 1 for n in noisy()))"
        ),
        expect="tick 0\ntick 1\nTrue",
        why=(
            "any() stops at the first true item and a generator only "
            "does work when asked for the next value, so the producer "
            "is never asked for 2, 3 or 4. The ticks for those never "
            "happen. Replace the generator expression with a list "
            "comprehension and all five ticks print first, because the "
            "whole list is built before any() sees it."
        ),
    ),
    _p(
        id="predict-pyx-gen-return-value",
        level=3,
        name="Where a generator's return goes",
        family=GENERATORS,
        code=(
            "def count():\n"
            "    yield 1\n"
            '    return "done"\n'
            "\n"
            "g = count()\n"
            "print(next(g))\n"
            "try:\n"
            "    next(g)\n"
            "except StopIteration as e:\n"
            "    print(e.value)"
        ),
        expect="1\ndone",
        why=(
            "A return inside a generator ends it, and the returned "
            "value is carried on the StopIteration that the second "
            "next() raises, in its `value` attribute. A for loop catches "
            "that exception and throws the value away, which is why you "
            "never see it there. `yield from` is the thing that "
            "collects it, handing it back as the result of the "
            "expression."
        ),
    ),
    _p(
        id="predict-pyx-gen-send",
        level=4,
        name="Sending a value into a generator",
        family=GENERATORS,
        code=(
            "def acc():\n"
            "    total = 0\n"
            "    while True:\n"
            "        x = yield total\n"
            "        total += x\n"
            "\n"
            "g = acc()\n"
            "print(next(g), g.send(5), g.send(10))"
        ),
        expect="0 5 15",
        why=(
            "A yield is an expression: the generator pauses on it, and "
            "send(v) resumes it with v as the expression's value. The "
            "first next() has to come first to run the generator up to "
            "its first yield, which produces 0. send(5) makes `x` 5, "
            "adds it, loops and yields the new total 5. send(10) does "
            "the same and gives 15. Starting with send(5) instead is a "
            "TypeError, since there is no yield waiting for it yet."
        ),
    ),
    _p(
        id="predict-pyx-gen-expression-late",
        level=4,
        name="What a generator expression reads when",
        family=GENERATORS,
        code=(
            "xs = [1, 2, 3]\n"
            "g = (x * 10 for x in xs)\n"
            "xs = [7, 8, 9]\n"
            "print(list(g))\n"
            "n = 1\n"
            "h = (x for x in range(5) if x > n)\n"
            "n = 3\n"
            "print(list(h))"
        ),
        expect="[10, 20, 30]\n[4]",
        why=(
            "The outermost iterable of a generator expression is "
            "evaluated straight away, when the expression is created: "
            "it grabbed the first list, so rebinding `xs` later changes "
            "nothing. Everything else inside is evaluated lazily, on "
            "each step. The `n` in the condition is looked up as the "
            "values are produced, by which time it is 3, so only 4 "
            "gets through."
        ),
    ),
    # ── Iteration ────────────────────────────────────────────
    _p(
        id="predict-pyx-iter-zip-enumerate",
        level=1,
        name="Zip and enumerate",
        family=ITERATION,
        code=(
            'print(list(zip("abc", [1, 2])))\n'
            'print(list(enumerate("ab", 1)))'
        ),
        expect="[('a', 1), ('b', 2)]\n[(1, 'a'), (2, 'b')]",
        why=(
            "zip stops when its shortest input runs out, so the c "
            "quietly disappears with no error (itertools.zip_longest "
            "pads instead, and zip(strict=True) raises). enumerate puts "
            "the counter first, and its second argument is where the "
            "counting starts, which is how you get 1-based numbering "
            "without adding one yourself."
        ),
    ),
    _p(
        id="predict-pyx-iter-sort-stable",
        level=3,
        name="Equal keys, sorted and reversed",
        family=ITERATION,
        code=(
            'words = ["bb", "a", "cc", "d"]\n'
            "print(sorted(words, key=len))\n"
            "print(sorted(words, key=len, reverse=True))"
        ),
        expect="['a', 'd', 'bb', 'cc']\n['bb', 'cc', 'a', 'd']",
        why=(
            "Sorting is stable: items whose keys are equal stay in the "
            "order they started in. reverse=True keeps that promise too "
            "- it does not simply flip the result, so bb still comes "
            "before cc and a before d. That is what makes sorting by "
            "one key and then by another work, as a way of building a "
            "multi-key sort."
        ),
    ),
    _p(
        id="predict-pyx-iter-dict-resize",
        level=3,
        name="Adding keys while looping over a dict",
        family=ITERATION,
        code=(
            'd = {"a": 1, "b": 2}\n'
            "try:\n"
            "    for k in d:\n"
            '        d[k + "x"] = 0\n'
            "except RuntimeError as e:\n"
            "    print(e)\n"
            "print(len(d))"
        ),
        expect="dictionary changed size during iteration\n3",
        why=(
            "A dict notices when its size changes under a running "
            "loop and raises on the next step, rather than guessing "
            "what you wanted. The first pass added `ax`, so the "
            "dict had grown to 3 by the time the error came. "
            "Overwriting existing keys is fine, because the size does "
            "not change; to add or delete while looping, loop over "
            "`list(d)` instead."
        ),
    ),
    _p(
        id="predict-pyx-iter-for-else",
        level=4,
        name="The else on a loop",
        family=ITERATION,
        code=(
            "for n in range(2, 6):\n"
            "    if n % 7 == 0:\n"
            "        break\n"
            "else:\n"
            '    print("no break")\n'
            "print(n)"
        ),
        expect="no break\n5",
        why=(
            "A loop's else runs when the loop finished without hitting "
            "a break, which is the opposite of what the word suggests "
            "to most people. Nothing in 2 to 5 divides by 7, so it "
            "fell through to the else. The loop variable also outlives "
            "the loop, still holding the last value, 5. Read it as "
            "`nobreak`."
        ),
    ),
    # ── Scope and closures ───────────────────────────────────
    _p(
        id="predict-pyx-scope-default-early",
        level=2,
        name="When a default is read",
        family=SCOPE,
        code=(
            'x = "early"\n'
            "def show(v=x):\n"
            "    return v\n"
            "\n"
            'x = "late"\n'
            "print(show())"
        ),
        expect="early",
        why=(
            "A default value is evaluated once, when the def statement "
            "runs, and stored on the function. Rebinding `x` afterwards "
            "does not reach it. This is the same rule that makes a "
            "list default shared between calls, shown with a harmless "
            "string instead."
        ),
    ),
    _p(
        id="predict-pyx-scope-nonlocal",
        level=2,
        name="Two nonlocal counters",
        family=SCOPE,
        code=(
            "def counter():\n"
            "    n = 0\n"
            "    def bump():\n"
            "        nonlocal n\n"
            "        n += 1\n"
            "        return n\n"
            "    return bump\n"
            "\n"
            "a, b = counter(), counter()\n"
            "print(a(), a(), b())"
        ),
        expect="1 2 1",
        why=(
            "Each call to counter() creates a fresh `n` and a fresh "
            "bump closing over it, so the two counters never share "
            "state. Without the `nonlocal` line, `n += 1` would try to "
            "assign to a new local and fail, because assignment makes a "
            "name local unless it is declared otherwise."
        ),
    ),
    _p(
        id="predict-pyx-scope-unbound",
        level=3,
        name="Reading a name you assign later",
        family=SCOPE,
        code=(
            "x = 1\n"
            "def f():\n"
            "    print(x)\n"
            "    x = 2\n"
            "\n"
            "try:\n"
            "    f()\n"
            "except UnboundLocalError:\n"
            '    print("unbound")'
        ),
        expect="unbound",
        why=(
            "Python decides whether a name is local by looking at the "
            "whole function body before running it. `x = 2` further "
            "down makes `x` local for the entire function, including "
            "the earlier print, so the global is never consulted and "
            "the local has no value yet. Delete the assignment and it "
            "prints the global 1."
        ),
    ),
    _p(
        id="predict-pyx-scope-class-body",
        level=4,
        name="A comprehension inside a class body",
        family=SCOPE,
        code=(
            "class K:\n"
            "    n = 5\n"
            "    try:\n"
            "        a = [n for _ in range(2)]\n"
            "    except NameError as e:\n"
            "        a = str(e)\n"
            "\n"
            "print(K.a)"
        ),
        expect="name 'n' is not defined",
        why=(
            "A class body is not an enclosing scope for functions "
            "or comprehensions written inside it. Only the outermost "
            "iterable is evaluated in the class body; the rest, "
            "including `n`, is looked up from inside the "
            "comprehension, which cannot see the class's names. "
            "Putting the value at module level, or passing it in "
            "through the outermost iterable, avoids it."
        ),
    ),
    _p(
        id="predict-pyx-scope-except-name",
        level=4,
        name="The name an except clause takes",
        family=SCOPE,
        code=(
            'e = "outer"\n'
            "try:\n"
            "    1 / 0\n"
            "except ZeroDivisionError as e:\n"
            "    pass\n"
            "try:\n"
            "    print(e)\n"
            "except NameError:\n"
            '    print("gone")'
        ),
        expect="gone",
        why=(
            "`except ... as e` deletes `e` when the clause ends, to "
            "break the reference cycle between the exception, its "
            "traceback and the frame that holds the name. It deletes "
            "it, rather than restoring the old value, so the earlier "
            "`e` is gone too and the lookup fails. Copy it to another "
            "name inside the clause if you need it afterwards."
        ),
    ),
    # ── Data model ───────────────────────────────────────────
    _p(
        id="predict-pyx-dm-property-setter",
        level=2,
        name="A property with a setter",
        family=DATA_MODEL,
        code=(
            "class Temp:\n"
            "    def __init__(self):\n"
            "        self._c = 0\n"
            "    @property\n"
            "    def c(self):\n"
            "        return self._c\n"
            "    @c.setter\n"
            "    def c(self, v):\n"
            "        self._c = max(v, -273)\n"
            "\n"
            "t = Temp()\n"
            "t.c = -500\n"
            "print(t.c)"
        ),
        expect="-273",
        why=(
            "The assignment `t.c = -500` looks like setting an "
            "attribute and runs the setter function instead, which "
            "clamps the value before storing it in `_c`. Reading "
            "`t.c` runs the getter. Callers see a plain attribute, "
            "which is why a property lets you add validation later "
            "without changing the interface."
        ),
    ),
    _p(
        id="predict-pyx-dm-int-is",
        level=3,
        name="Same number, same object?",
        family=DATA_MODEL,
        code=(
            'a = int("256")\n'
            'b = int("256")\n'
            'c = int("257")\n'
            'd = int("257")\n'
            "print(a is b, c is d, c == d)"
        ),
        expect="True False True",
        why=(
            "CPython keeps one shared object for each integer from -5 "
            "to 256, so two separate ways of arriving at 256 give "
            "the very same object. 257 is built fresh each time. "
            "(The values come from int() on purpose: two literals in "
            "the same piece of code are merged by the compiler.) "
            "It is an implementation detail, not a language rule, "
            "which is exactly why `==` is the right comparison for "
            "numbers."
        ),
    ),
    _p(
        id="predict-pyx-dm-eq-no-hash",
        level=3,
        name="An __eq__ and no __hash__",
        family=DATA_MODEL,
        code=(
            "class P:\n"
            "    def __init__(self, x):\n"
            "        self.x = x\n"
            "    def __eq__(self, other):\n"
            "        return self.x == other.x\n"
            "\n"
            "try:\n"
            "    {P(1)}\n"
            "except TypeError as e:\n"
            "    print(e)"
        ),
        expect="unhashable type: 'P'",
        why=(
            "Defining __eq__ in a class quietly sets its __hash__ to "
            "None. Python does that because equal objects must have "
            "equal hashes, and it cannot know how you want the two "
            "to line up, so it refuses to let the instances be set "
            "members or dict keys until you write a __hash__ that "
            "agrees with your __eq__."
        ),
    ),
    _p(
        id="predict-pyx-dm-slots",
        level=3,
        name="A class with __slots__",
        family=DATA_MODEL,
        code=(
            "class P:\n"
            '    __slots__ = ("x",)\n'
            "\n"
            "p = P()\n"
            "p.x = 1\n"
            "try:\n"
            "    p.y = 2\n"
            "except AttributeError:\n"
            '    print("no y")\n'
            'print(hasattr(p, "__dict__"))'
        ),
        expect="no y\nFalse",
        why=(
            "__slots__ gives instances a fixed set of attribute "
            "slots in place of the per-instance dictionary. That is "
            "where the memory saving comes from, and it is also why "
            "an undeclared name like `y` has nowhere to go and "
            "raises AttributeError. With no __dict__ on the "
            "instance, hasattr says False."
        ),
    ),
    _p(
        id="predict-pyx-dm-class-attr",
        level=3,
        name="Class attributes behind instance names",
        family=DATA_MODEL,
        code=(
            "class C:\n"
            "    items = []\n"
            "    n = 0\n"
            "\n"
            "a, b = C(), C()\n"
            "a.items.append(1)\n"
            "a.n += 1\n"
            "print(b.items, b.n, a.n)"
        ),
        expect="[1] 0 1",
        why=(
            "`a.items.append(1)` finds `items` on the class and "
            "mutates that one shared list, so `b` sees it. `a.n += 1` "
            "reads the class's 0, adds one, and assigns the result "
            "to the instance, creating `a.n` and leaving `C.n` and "
            "`b.n` alone. Mutating a shared object and rebinding a "
            "name are different operations even when they look "
            "alike."
        ),
    ),
    _p(
        id="predict-pyx-dm-getitem-iter",
        level=4,
        name="Iterating something with only __getitem__",
        family=DATA_MODEL,
        code=(
            "class Seq:\n"
            "    def __getitem__(self, i):\n"
            "        if i > 2:\n"
            "            raise IndexError\n"
            "        return i * i\n"
            "\n"
            "print(list(Seq()), 4 in Seq())"
        ),
        expect="[0, 1, 4] True",
        why=(
            "With no __iter__, Python falls back to the old sequence "
            "protocol: it calls __getitem__ with 0, 1, 2 and so on "
            "until an IndexError says stop. list() and the `in` "
            "operator both iterate that way, so 4 is found as the "
            "third item. Nothing here is a list, and nothing needed "
            "to be."
        ),
    ),
    _p(
        id="predict-pyx-dm-super-diamond",
        level=4,
        name="super() in a diamond",
        family=DATA_MODEL,
        code=(
            "class A:\n"
            '    def hi(self): return ["A"]\n'
            "class B(A):\n"
            '    def hi(self): return ["B"] + super().hi()\n'
            "class C(A):\n"
            '    def hi(self): return ["C"] + super().hi()\n'
            "class D(B, C):\n"
            '    def hi(self): return ["D"] + super().hi()\n'
            "\n"
            "print(D().hi())"
        ),
        expect="['D', 'B', 'C', 'A']",
        why=(
            "super() does not mean \"my parent\". It means \"the next "
            "class after this one in the instance's method resolution "
            "order\", and for a D that order is D, B, C, A. So B's "
            "super() call lands on C, not A, and A is reached once, at "
            "the end. This is what makes cooperative inheritance "
            "work, and it is why every class in the chain has to "
            "call super()."
        ),
    ),
    # ── Typing and dataclasses ───────────────────────────────
    _p(
        id="predict-pyx-typing-not-enforced",
        level=1,
        name="A hint that nobody checks",
        family=TYPING,
        code=(
            "def add(a: int, b: int) -> int:\n"
            "    return a + b\n"
            "\n"
            'print(add("x", "y"))'
        ),
        expect="xy",
        why=(
            "Annotations are information for tools and readers. "
            "The interpreter stores them and never checks them, so "
            "passing strings to an int-annotated function simply "
            "runs, and + on two strings joins them. A type checker "
            "such as mypy or pyright would have complained before "
            "the program ever ran."
        ),
    ),
    _p(
        id="predict-pyx-typing-default-factory",
        level=2,
        name="Two carts from one dataclass",
        family=TYPING,
        code=(
            "from dataclasses import dataclass, field\n"
            "\n"
            "@dataclass\n"
            "class Cart:\n"
            "    items: list = field(default_factory=list)\n"
            "\n"
            "a, b = Cart(), Cart()\n"
            'a.items.append("x")\n'
            "print(a, b)"
        ),
        expect="Cart(items=['x']) Cart(items=[])",
        why=(
            "`default_factory=list` is a function that dataclass "
            "calls for every new instance, so each cart gets its own "
            "list. A plain `= []` would have shared one list across "
            "all of them, which is why dataclass refuses that "
            "outright instead of letting it through. The printed "
            "form is the generated __repr__."
        ),
    ),
    _p(
        id="predict-pyx-typing-mutable-default",
        level=3,
        name="The default a dataclass refuses",
        family=TYPING,
        code=(
            "from dataclasses import dataclass\n"
            "\n"
            "try:\n"
            "    @dataclass\n"
            "    class Bad:\n"
            "        items: list = []\n"
            "except ValueError as e:\n"
            "    print(e)"
        ),
        expect=(
            "mutable default <class 'list'> for field items is not "
            "allowed: use default_factory"
        ),
        why=(
            "The same trap as a mutable default argument, caught at "
            "class creation instead of being left to bite later. The "
            "message even names the cure. A default that is "
            "unhashable counts as mutable for this check, which is "
            "why a list, a dict or a set is refused and an int or a "
            "tuple is not."
        ),
    ),
    _p(
        id="predict-pyx-typing-frozen",
        level=3,
        name="A frozen dataclass",
        family=TYPING,
        code=(
            "from dataclasses import dataclass\n"
            "\n"
            "@dataclass(frozen=True)\n"
            "class P:\n"
            "    x: int\n"
            "\n"
            "p = P(1)\n"
            "try:\n"
            "    p.x = 2\n"
            "except AttributeError as e:\n"
            "    print(type(e).__name__)\n"
            'print({p: "ok"}[P(1)])'
        ),
        expect="FrozenInstanceError\nok",
        why=(
            "frozen=True makes assignment raise FrozenInstanceError, "
            "which is a kind of AttributeError, so the except clause "
            "catches it. Together with the default eq=True it also "
            "generates a __hash__ built from the fields, so a "
            "different P(1) finds the entry made with the first: "
            "equal fields, equal hash, equal object."
        ),
    ),
    _p(
        id="predict-pyx-typing-eq-unhashable",
        level=4,
        name="A dataclass that is equal but unhashable",
        family=TYPING,
        code=(
            "from dataclasses import dataclass\n"
            "\n"
            "@dataclass\n"
            "class P:\n"
            "    x: int\n"
            "\n"
            "print(P(1) == P(1), P(1) is P(1), P.__hash__)"
        ),
        expect="True False None",
        why=(
            "dataclass writes an __eq__ that compares field by field, "
            "so two P(1) are equal though they are two objects. And "
            "because the class is equal-comparable and mutable, the "
            "decorator sets __hash__ to None: a hash that changes "
            "when the object does would break sets and dicts. "
            "Adding frozen=True gets the hash back."
        ),
    ),
    # ── Numbers and formatting ───────────────────────────────
    _p(
        id="predict-pyx-num-format-specs",
        level=2,
        name="Format specs, read left to right",
        family=NUMBERS,
        code=(
            "x = 1234.5678\n"
            'print(f"{x:,.2f}|{x:10.1f}|{x:<10.0f}|")\n'
            'print(f"{255:#x} {255:08b} {0.256:.1%} {42:+d}")'
        ),
        expect=(
            "1,234.57|    1234.6|1235      |\n"
            "0xff 11111111 25.6% +42"
        ),
        why=(
            "After the colon comes fill and alignment, then a width, "
            "then a precision after the dot, then the type. A comma "
            "adds thousands separators, and numbers align right by "
            "default, so `10.1f` pads on the left while `<10.0f` pads "
            "on the right. `#x` is hex with its 0x prefix, `08b` is "
            "binary zero-padded to 8, `.1%` multiplies by 100 and "
            "adds the sign, and `+d` shows the plus."
        ),
    ),
    _p(
        id="predict-pyx-num-decimal",
        level=3,
        name="Decimal from a string and from a float",
        family=NUMBERS,
        code=(
            "from decimal import Decimal\n"
            "\n"
            'print(Decimal("0.1") + Decimal("0.2"))\n'
            'print(Decimal(0.1) == Decimal("0.1"))'
        ),
        expect="0.3\nFalse",
        why=(
            "Decimal works in base ten, so 0.1 and 0.2 are exact and "
            "add to exactly 0.3. The trap is building one from a "
            "float: Decimal(0.1) captures the float's binary "
            "approximation exactly, digit for digit, which is not the "
            "same number as the string \"0.1\". Always construct "
            "Decimals from strings (or integers) when the point is "
            "exactness."
        ),
    ),
    _p(
        id="predict-pyx-num-round-digits",
        level=3,
        name="Rounding to two places",
        family=NUMBERS,
        code="print(round(2.675, 2), round(1234, -2), round(-2.5))",
        expect="2.67 1200 -2",
        why=(
            "2.675 is stored as a float slightly below 2.675, so "
            "rounding to two places correctly gives 2.67, not the "
            "2.68 the decimal text suggests. A negative number of "
            "digits rounds to the left of the point, so 1234 becomes "
            "1200. And the half-to-even rule rounds -2.5 to -2, "
            "since 2 is the even neighbour."
        ),
    ),
    _p(
        id="predict-pyx-num-unary-minus",
        level=3,
        name="Minus and the power operator",
        family=NUMBERS,
        code="print(-3 ** 2, (-3) ** 2, 2 ** 3 ** 2, 7 % -3)",
        expect="-9 9 512 -2",
        why=(
            "`**` binds tighter than a unary minus, so `-3 ** 2` is "
            "-(3 ** 2) = -9. It also groups from the right, so "
            "`2 ** 3 ** 2` is 2 ** 9 = 512, not 8 ** 2. And `%` "
            "takes its sign from the right-hand number, so 7 % -3 "
            "is -2, which keeps (7 // -3) * -3 + (7 % -3) equal "
            "to 7."
        ),
    ),
    _p(
        id="predict-pyx-num-one-is-one-point-zero",
        level=4,
        name="1, 1.0 and True as keys",
        family=NUMBERS,
        code=(
            "print(1 == 1.0, hash(1) == hash(1.0))\n"
            'print({1: "a", 1.0: "b", True: "c"})'
        ),
        expect="True True\n{1: 'c'}",
        why=(
            "1, 1.0 and True are equal and hash alike, so to a dict "
            "they are the same key. The first one in keeps its place "
            "and its spelling (the key stays 1), and every later "
            "assignment replaces only the value, which ends as "
            "'c'. That is the rule that equal objects must have equal "
            "hashes, seen from the outside."
        ),
    ),
    # ── Strings ──────────────────────────────────────────────
    _p(
        id="predict-pyx-str-slicing-negative",
        level=2,
        name="Slices that walk backwards",
        family=STRINGS,
        code=(
            's = "abcdef"\n'
            "print(s[::-1], s[4:1:-1], s[-2:], s[::2])"
        ),
        expect="fedcba edc ef ace",
        why=(
            "With a negative step the slice walks right to left, and "
            "start and stop swap roles: `s[4:1:-1]` starts at index "
            "4 and goes down to, but not including, index 1, giving "
            "e, d, c. `[-2:]` counts from the end, and `[::2]` takes "
            "every second character."
        ),
    ),
    _p(
        id="predict-pyx-str-count-replace",
        level=2,
        name="Counting and replacing",
        family=STRINGS,
        code=(
            's = "banana"\n'
            'print(s.count("ana"), s.replace("an", "AN", 1),'
            ' s.find("x"), s.index("n"))'
        ),
        expect="1 bANana -1 2",
        why=(
            "count() does not count overlapping matches: the \"ana\" "
            "at position 1 uses up the letters the one at position 3 "
            "would need, so the answer is 1. The third argument to "
            "replace limits how many are replaced, here just the "
            "first. find() returns -1 for a miss while index() "
            "raises ValueError for the same miss."
        ),
    ),
    _p(
        id="predict-pyx-str-split",
        level=3,
        name="Split with and without an argument",
        family=STRINGS,
        code=(
            'print("a  b c".split())\n'
            'print("a  b c".split(" "))\n'
            'print("a,b,,c".split(","))'
        ),
        expect=(
            "['a', 'b', 'c']\n"
            "['a', '', 'b', 'c']\n"
            "['a', 'b', '', 'c']"
        ),
        why=(
            "With no argument, split treats any run of whitespace as "
            "a single separator and drops empty pieces. With an "
            "explicit separator, every occurrence counts, so two "
            "adjacent separators produce an empty string between "
            "them. That is the difference to remember when parsing "
            "anything delimited, like CSV-ish text."
        ),
    ),
    _p(
        id="predict-pyx-str-strip-chars",
        level=3,
        name="Strip takes characters, not a prefix",
        family=STRINGS,
        code=(
            'print("xxhixx".strip("x"))\n'
            'print("abcba".lstrip("ab"))\n'
            'print("hello.py".removesuffix(".py"))'
        ),
        expect="hi\ncba\nhello",
        why=(
            "The argument to strip, lstrip and rstrip is a set of "
            "characters, not a string to remove: lstrip(\"ab\") eats "
            "any a or b from the left until it hits something else, "
            "so \"abcba\" becomes \"cba\". If you mean an exact "
            "prefix or suffix, removeprefix and removesuffix (3.9+) "
            "are the tools."
        ),
    ),
    _p(
        id="predict-pyx-str-intern",
        level=4,
        name="Equal strings, same string?",
        family=STRINGS,
        code=(
            "import sys\n"
            "\n"
            'a = "py"\n'
            'b = "".join(["p", "y"])\n'
            "print(a == b, a is b, a is sys.intern(b))"
        ),
        expect="True False True",
        why=(
            "The compiler interns short, identifier-like string "
            "literals, so `a` is a shared object. join builds a "
            "brand-new string at run time, equal to it but not the "
            "same object. sys.intern looks the text up in the table "
            "of interned strings and hands back the shared one. This "
            "is CPython behaviour; the lesson is again that `is` is "
            "for identity, not for text."
        ),
    ),
    # ── Standard library ─────────────────────────────────────
    _p(
        id="predict-pyx-lib-contextmanager-order",
        level=2,
        name="Two context managers in one with",
        family=STDLIB,
        code=(
            "from contextlib import contextmanager\n"
            "\n"
            "@contextmanager\n"
            "def tag(name):\n"
            '    print("enter", name)\n'
            "    yield\n"
            '    print("exit", name)\n'
            "\n"
            'with tag("a"), tag("b"):\n'
            '    print("body")'
        ),
        expect="enter a\nenter b\nbody\nexit b\nexit a",
        why=(
            "`with a, b:` is the same as nesting b inside a, so they "
            "are entered left to right and left in the opposite "
            "order, like a stack. The code before the yield is the "
            "__enter__ half and the code after it is the __exit__ "
            "half, which is the whole trick behind "
            "@contextmanager."
        ),
    ),
    _p(
        id="predict-pyx-lib-copy-deepcopy",
        level=2,
        name="Shallow and deep copies",
        family=STDLIB,
        code=(
            "import copy\n"
            "\n"
            "a = [[1], [2]]\n"
            "b = copy.copy(a)\n"
            "c = copy.deepcopy(a)\n"
            "a[0].append(9)\n"
            "print(b[0], c[0])"
        ),
        expect="[1, 9] [1]",
        why=(
            "A shallow copy makes a new outer list but reuses the "
            "inner lists, so `b[0]` is still the very list that "
            "`a[0]` is, and the append shows through. deepcopy "
            "copies the inner lists as well, so `c` is untouched. "
            "`list(a)` and `a[:]` are shallow in the same way."
        ),
    ),
    _p(
        id="predict-pyx-lib-lru-cache",
        level=3,
        name="What the cache remembers",
        family=STDLIB,
        code=(
            "from functools import lru_cache\n"
            "\n"
            "@lru_cache(maxsize=None)\n"
            "def sq(n):\n"
            "    return n * n\n"
            "\n"
            "sq(2); sq(2); sq(3)\n"
            "print(sq.cache_info())"
        ),
        expect="CacheInfo(hits=1, misses=2, maxsize=None, currsize=2)",
        why=(
            "The first sq(2) is a miss and computes the answer. The "
            "second is a hit, served from the cache without running "
            "the function. sq(3) is a new argument, so a second "
            "miss. Two distinct results are held. Remember that the "
            "arguments become dictionary keys, so they have to be "
            "hashable."
        ),
    ),
    _p(
        id="predict-pyx-lib-counter-ties",
        level=3,
        name="Counter.most_common with a tie",
        family=STDLIB,
        code=(
            "from collections import Counter\n"
            "\n"
            'c = Counter("abracadabra")\n'
            'print(c.most_common(2), c["z"])'
        ),
        expect="[('a', 5), ('b', 2)] 0",
        why=(
            "a appears 5 times; b and r tie at 2. most_common sorts "
            "by count and keeps equal counts in the order they were "
            "first seen, so b, which appeared before r, takes the "
            "second slot. And a missing key in a Counter reads as 0 "
            "instead of raising KeyError, without adding the key."
        ),
    ),
    _p(
        id="predict-pyx-lib-defaultdict-read",
        level=3,
        name="Reading from a defaultdict",
        family=STDLIB,
        code=(
            "from collections import defaultdict\n"
            "\n"
            "d = defaultdict(list)\n"
            'd["a"]\n'
            'print(len(d), "b" in d, d.get("b"), len(d))'
        ),
        expect="1 False None 1",
        why=(
            "Indexing a defaultdict with a missing key calls the "
            "factory and stores the result, so a plain read of "
            "d[\"a\"] grew the dict to one entry. `in` and `.get()` "
            "do not go through that path, so they neither create "
            "`b` nor report a default. The side effect of a read "
            "is exactly why it is easy to fill one by accident."
        ),
    ),
    _p(
        id="predict-pyx-lib-bisect",
        level=3,
        name="Binary search with duplicates",
        family=STDLIB,
        code=(
            "from bisect import bisect_left, bisect_right\n"
            "\n"
            "a = [1, 2, 2, 3]\n"
            "print(bisect_left(a, 2), bisect_right(a, 2), bisect_left(a, 5))"
        ),
        expect="1 3 4",
        why=(
            "Both functions return an insertion point in a sorted "
            "list. bisect_left gives the position before any equal "
            "items, 1, and bisect_right the position after them, 3, "
            "so their difference is the number of copies. A value "
            "bigger than everything goes at the end, which is the "
            "length, 4."
        ),
    ),
    _p(
        id="predict-pyx-lib-contextmanager-raise",
        level=4,
        name="The cleanup an exception skips",
        family=STDLIB,
        code=(
            "from contextlib import contextmanager\n"
            "\n"
            "@contextmanager\n"
            "def tag():\n"
            '    print("enter")\n'
            "    yield\n"
            '    print("exit")\n'
            "\n"
            "try:\n"
            "    with tag():\n"
            "        raise ValueError\n"
            "except ValueError:\n"
            '    print("caught")'
        ),
        expect="enter\ncaught",
        why=(
            "When the body raises, the exception is thrown into the "
            "generator at the yield. Nothing there catches it, so "
            "the lines after the yield never run and `exit` is "
            "never printed. Cleanup in a generator-based context "
            "manager has to be in a try/finally around the yield; "
            "it does not run by itself the way a class's __exit__ "
            "does."
        ),
    ),
    # ── Asyncio ──────────────────────────────────────────────
    _p(
        id="predict-pyx-async-not-running",
        level=2,
        name="Calling a coroutine function",
        family=ASYNCIO,
        code=(
            "import asyncio\n"
            "\n"
            "async def hello():\n"
            '    print("hello")\n'
            "\n"
            "c = hello()\n"
            'print("created")\n'
            "asyncio.run(c)"
        ),
        expect="created\nhello",
        why=(
            "Calling an async function runs none of it: it returns a "
            "coroutine object, the way a generator function returns "
            "a generator. The body starts only when something drives "
            "it, here asyncio.run. A coroutine that is never awaited "
            "does nothing at all, apart from a warning."
        ),
    ),
    _p(
        id="predict-pyx-async-gather-order",
        level=3,
        name="Finishing order and result order",
        family=ASYNCIO,
        code=(
            "import asyncio\n"
            "\n"
            "async def job(name, delay):\n"
            "    await asyncio.sleep(delay)\n"
            '    print("done", name)\n'
            "    return name\n"
            "\n"
            "async def main():\n"
            '    print(await asyncio.gather(job("slow", 0.05), job("fast", 0.01)))\n'
            "\n"
            "asyncio.run(main())"
        ),
        expect="done fast\ndone slow\n['slow', 'fast']",
        why=(
            "The two jobs run at the same time, so the quick one "
            "finishes and prints first. gather still returns "
            "results in the order the awaitables were passed in, "
            "not the order they finished, so the list reads slow "
            "then fast. The total time is that of the slowest job, "
            "not the sum."
        ),
    ),
    _p(
        id="predict-pyx-async-task-starts-late",
        level=3,
        name="When a created task actually runs",
        family=ASYNCIO,
        code=(
            "import asyncio\n"
            "\n"
            "async def worker():\n"
            '    print("worker")\n'
            "\n"
            "async def main():\n"
            "    t = asyncio.create_task(worker())\n"
            '    print("before")\n'
            "    await asyncio.sleep(0)\n"
            '    print("after")\n'
            "    await t\n"
            "\n"
            "asyncio.run(main())"
        ),
        expect="before\nworker\nafter",
        why=(
            "create_task schedules the coroutine but does not run it: "
            "there is one thread, and it is busy with main until main "
            "hits an await. `sleep(0)` is the smallest possible "
            "await, a pure yield to the event loop, and that is "
            "where the worker gets its turn. Switches happen only "
            "at awaits, which is why the order is so predictable."
        ),
    ),
    _p(
        id="predict-pyx-async-return-exceptions",
        level=3,
        name="One task fails in a gather",
        family=ASYNCIO,
        code=(
            "import asyncio\n"
            "\n"
            "async def ok():\n"
            "    await asyncio.sleep(0.01)\n"
            "    return 1\n"
            "\n"
            "async def bad():\n"
            '    raise ValueError("boom")\n'
            "\n"
            "async def main():\n"
            "    r = await asyncio.gather(ok(), bad(), return_exceptions=True)\n"
            "    print(r)\n"
            "\n"
            "asyncio.run(main())"
        ),
        expect="[1, ValueError('boom')]",
        why=(
            "With return_exceptions=True, gather puts the exception "
            "in the results list instead of raising it, and waits "
            "for everything else, so ok() still finishes and "
            "returns 1. Without it, the first exception goes to the "
            "caller straight away while the other tasks carry on "
            "running in the background, which surprises people."
        ),
    ),
    _p(
        id="predict-pyx-async-taskgroup",
        level=4,
        name="A failure in a TaskGroup",
        family=ASYNCIO,
        code=(
            "import asyncio\n"
            "\n"
            "async def boom():\n"
            '    raise ValueError("x")\n'
            "\n"
            "async def main():\n"
            "    try:\n"
            "        async with asyncio.TaskGroup() as tg:\n"
            "            tg.create_task(boom())\n"
            "    except* ValueError as eg:\n"
            "        print(type(eg).__name__, len(eg.exceptions))\n"
            "\n"
            "asyncio.run(main())"
        ),
        expect="ExceptionGroup 1",
        why=(
            "A TaskGroup (3.11+) cancels the other tasks when one "
            "fails and then raises everything that went wrong "
            "together, wrapped in an ExceptionGroup, even when "
            "there was only one error. `except*` is the matching "
            "syntax: it picks out the ValueErrors from inside the "
            "group, and `eg` is a group again, not a bare "
            "ValueError."
        ),
    ),
    # ── Syntax and flow ──────────────────────────────────────
    _p(
        id="predict-pyx-flow-walrus",
        level=2,
        name="The walrus in a condition",
        family=SYNTAX,
        code=(
            "data = [1, 5, 8]\n"
            "if (n := len(data)) > 2:\n"
            "    print(n, n * 2)\n"
            "print([y for x in data if (y := x * 2) > 5])"
        ),
        expect="3 6\n[10, 16]",
        why=(
            "`:=` assigns and gives back the value in one expression, "
            "so `n` is both tested and kept for the body. In the "
            "comprehension it computes x * 2 once and uses the result "
            "twice, in the filter and as the output: 2 is dropped, "
            "5 and 8 give 10 and 16."
        ),
    ),
    _p(
        id="predict-pyx-flow-try-else-finally",
        level=2,
        name="Else and finally together",
        family=SYNTAX,
        code=(
            "def f(n):\n"
            "    try:\n"
            "        v = 10 // n\n"
            "    except ZeroDivisionError:\n"
            '        print("zero")\n'
            "    else:\n"
            '        print("else", v)\n'
            "    finally:\n"
            '        print("finally")\n'
            "\n"
            "f(5)\n"
            "f(0)"
        ),
        expect="else 2\nfinally\nzero\nfinally",
        why=(
            "The else block runs only when the try finished without "
            "raising, which keeps code that should not be "
            "protected by the except out of the try. The finally "
            "runs in both cases, and always last. For 5 that is "
            "else then finally; for 0 the except handles it and "
            "finally follows."
        ),
    ),
    _p(
        id="predict-pyx-flow-match-shapes",
        level=3,
        name="Matching by shape",
        family=SYNTAX,
        code=(
            "def f(x):\n"
            "    match x:\n"
            "        case [a, b]:\n"
            '            return f"pair {a} {b}"\n'
            '        case {"k": v}:\n'
            '            return f"key {v}"\n'
            "        case str():\n"
            '            return "text"\n'
            "        case _:\n"
            '            return "other"\n'
            "\n"
            'print(f((1, 2)), f({"k": 3, "z": 0}), f("hi"), f([1, 2, 3]))'
        ),
        expect="pair 1 2 key 3 text other",
        why=(
            "A sequence pattern matches any sequence of that length, "
            "tuple or list, but never a string. A mapping pattern "
            "matches a dict that has at least those keys, so the "
            "extra `z` does not matter. `str()` is a class pattern, "
            "an isinstance check. Three items fit no earlier case, "
            "so the wildcard gets it."
        ),
    ),
    _p(
        id="predict-pyx-flow-return-evaluated",
        level=4,
        name="The value a return has already computed",
        family=SYNTAX,
        code=(
            "def f():\n"
            "    x = [1]\n"
            "    n = 1\n"
            "    try:\n"
            "        return n, x\n"
            "    finally:\n"
            "        n = 2\n"
            "        x.append(2)\n"
            "\n"
            "print(f())"
        ),
        expect="(1, [1, 2])",
        why=(
            "The return expression is evaluated first, producing a "
            "tuple holding the number 1 and a reference to the "
            "list, and only then does the finally run. Rebinding "
            "`n` afterwards changes nothing about the tuple that "
            "is already built. The list, though, is the same object, "
            "so the append made in the finally shows up in the "
            "result."
        ),
    ),
    _p(
        id="predict-pyx-flow-match-capture",
        level=4,
        name="A name in a case that looks like a constant",
        family=SYNTAX,
        code=(
            "RED = 1\n"
            "def f(x):\n"
            "    match x:\n"
            "        case RED:\n"
            '            return "matched"\n'
            "\n"
            "print(f(2), RED)"
        ),
        expect="matched 1",
        why=(
            "A bare name in a case is a capture pattern: it matches "
            "anything and binds the name, it does not compare "
            "against the existing RED. So f(2) \"matches\", with a "
            "local RED set to 2, and the global stays 1. To compare "
            "against a constant, use a dotted name such as Color.RED "
            "or a literal."
        ),
    ),
    _p(
        id="predict-pyx-flow-exception-context",
        level=4,
        name="An exception raised while handling one",
        family=SYNTAX,
        code=(
            "try:\n"
            "    try:\n"
            "        1 / 0\n"
            "    except ZeroDivisionError:\n"
            '        raise ValueError("bad")\n'
            "except ValueError as e:\n"
            "    print(type(e.__context__).__name__, e.__cause__)"
        ),
        expect="ZeroDivisionError None",
        why=(
            "An exception raised inside an except block remembers the "
            "one being handled, in __context__, and the traceback "
            "shows both (\"during handling of the above exception\"). "
            "__cause__ is something else: it is set only by an "
            "explicit `raise ... from ...`, and is None here. "
            "`from None` suppresses the context display."
        ),
    ),
)
