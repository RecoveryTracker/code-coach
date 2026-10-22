"""Gotchas, Python, the fourth helping: dunder methods, the standard-library corners, protocols and more.

Same rules as content_py.py: every answer is held to a real run by tests/test_gotchas_content.py, the
wrong options are real misreads, nothing depends on randomness, the clock or identity, and each program
prints one line (or, with raises=True, dies with the named error having printed nothing). About a third
look easy on purpose, the rest are middle and hard traps. They come after the earlier modules in the deck.
"""

from __future__ import annotations

from .items import Item, make

q = make("python")

ITEMS: tuple[Item, ...] = (
    # ── Dunder methods: printing, truth, comparing, arithmetic ─────────────
    # E
    q("repr-only-fallback", '''
        class Pt:
            def __repr__(self):
                return "Pt(1)"
        p = Pt()
        print(p, f"{p}", "%s" % p, [p])
    ''', "Pt(1) Pt(1) Pt(1) [Pt(1)]",
      ["<Pt object> <Pt object> <Pt object> [Pt(1)]", "Pt(1) Pt(1) Pt(1) [<Pt object>]",
       "Pt(1) <Pt object> Pt(1) [Pt(1)]"],
      "With only __repr__ defined, str() falls back to it",
      """`object.__str__` calls `__repr__`, so print, an f-string and `%s` all show the repr text. The
      fallback only goes one way: a class with just `__str__` still gets the ugly default repr."""),

    # M
    q("str-only-in-list", '''
        class P:
            def __str__(self):
                return "hi"
        p = P()
        print(p, str([p]).count("hi"))
    ''', "hi 0", ["hi 1", "hi 2", "[hi] 0"],
      "A list shows its items with repr, and __str__ does not feed repr",
      """`print(p)` uses `__str__`, so it says `hi`. Inside a list, items are shown with `repr()`, and a class
      that only defines `__str__` has the default repr `<__main__.P object at ...>`, with no `hi` in it."""),

    # E
    q("bool-beats-len", '''
        class Box:
            def __len__(self):
                return 0
            def __bool__(self):
                return True
        print(bool(Box()), len(Box()), "yes" if Box() else "no")
    ''', "True 0 yes", ["False 0 no", "True 0 no", "True 1 yes"],
      "__bool__ is asked first; __len__ is only the fallback",
      """Truth testing calls `__bool__` when it exists and only falls back to `__len__` when it does not. Here
      the object is truthy even though its length is 0, and `len()` still reports 0."""),

    # M
    q("bool-must-return-bool", '''
        class Flag:
            def __bool__(self):
                return 1
        print(bool(Flag()))
    ''', "TypeError", ["True", "1", "ValueError"],
      "__bool__ must return a real bool, not just a truthy value",
      """Python checks the return type of `__bool__` and refuses anything but `True` or `False`, even
      the int 1. The error says `__bool__ should return bool, returned int`.""",
      raises=True),

    # M
    q("sort-needs-only-lt", '''
        class V:
            def __init__(self, n):
                self.n = n
            def __lt__(self, other):
                return self.n < other.n
            def __repr__(self):
                return f"V{self.n}"
        print(sorted([V(3), V(1), V(2)]), max(V(3), V(1)))
    ''', "[V1, V2, V3] V3",
      ["TypeError", "[V3, V1, V2] V3", "[V1, V2, V3] V1"],
      "sorted() and max() only ever use <, so __lt__ is enough",
      """Sorting compares with `<`, and `max` uses `>`, which Python gets by flipping the operands and calling
      the other side's `__lt__`. No `__gt__`, `__eq__` or `functools.total_ordering` is needed for this."""),

    # H
    q("le-not-from-lt", '''
        class V:
            def __init__(self, n):
                self.n = n
            def __lt__(self, other):
                return self.n < other.n
        print(V(1) <= V(2))
    ''', "TypeError", ["True", "False", "AttributeError"],
      "<= is not built from < and ==",
      """Python never derives one comparison from another. `V(1) <= V(2)` looks for `__le__`, then tries the
      reflected `__ge__` on the other object, finds neither and raises TypeError. `functools.total_ordering`
      is the tool that fills the gaps in.""",
      raises=True),

    # M
    q("eq-always-true", '''
        class A:
            def __eq__(self, other):
                return True
        print(A() == 1, 1 == A(), A() != 1, [A()] == [5])
    ''', "True True False True",
      ["True True True True", "True False False False", "True False True True"],
      "!= is the inverse of __eq__, and 1 == A() asks A when int says no",
      """`1 == A()` makes int answer `NotImplemented`, so Python tries the reflected `A.__eq__` and gets True.
      `!=` defaults to the inverse of `__eq__`, and lists compare their items with `==`, so `[A()] == [5]` is
      True as well."""),

    # M
    q("sum-needs-radd", '''
        class M:
            def __init__(self, v):
                self.v = v
            def __add__(self, other):
                return M(self.v + other.v)
        print(sum([M(1), M(2)]).v)
    ''', "TypeError", ["3", "1", "AttributeError"],
      "sum() starts from the int 0, so the first step is 0 + M(1)",
      """`sum` begins with the start value 0 and computes `0 + M(1)`. `int.__add__` gives up and Python then
      needs `M.__radd__`, which this class does not have, so the very first addition is a TypeError.""",
      raises=True),

    # H
    q("reflected-subclass-first", '''
        class A:
            def __add__(self, other):
                return "A.add"
            def __radd__(self, other):
                return "A.radd"
        class B(A):
            def __radd__(self, other):
                return "B.radd"
        print(A() + B(), B() + A(), A() + A())
    ''', "B.radd A.add A.add",
      ["A.add A.add A.add", "B.radd B.radd A.add", "A.radd A.add A.add"],
      "A subclass that overrides the reflected method goes first",
      """If the right operand is a subclass of the left one's type and overrides `__radd__`, Python tries
      that method before the left side's `__add__`. `B() + A()` has the subclass on the left, so the normal
      order applies and the inherited `__add__` answers."""),

    # M
    q("getitem-slice-object", '''
        class S:
            def __getitem__(self, key):
                return key
        s = S()
        print(s[1], s[1:3], s[::2], s[1, 2])
    ''', "1 slice(1, 3, None) slice(None, None, 2) (1, 2)",
      ["1 [1, 2] [0, 2] (1, 2)", "1 slice(1, 3) slice(None, 2) (1, 2)", "1 (1, 3) (None, 2) [1, 2]"],
      "A slice reaches __getitem__ as one slice object; a comma makes a tuple",
      """`s[1:3]` passes `slice(1, 3, None)` and `s[::2]` passes `slice(None, None, 2)`: the missing parts stay
      `None` and it is up to the class to interpret them. `s[1, 2]` is not a slice at all, just the tuple
      `(1, 2)`."""),

    # M
    q("contains-beats-iter", '''
        class C:
            def __iter__(self):
                return iter([1, 2, 3])
            def __contains__(self, x):
                return x == 99
        print(2 in C(), 99 in C(), list(C()))
    ''', "False True [1, 2, 3]",
      ["True False [1, 2, 3]", "True True [1, 2, 3]", "False False [1, 2, 3]"],
      "in asks __contains__ first and only iterates when there is none",
      """The `in` operator calls `__contains__` when the class has it, whatever the iterator would produce. Only
      without `__contains__` does Python fall back to looping over `__iter__` (and then to `__getitem__`)."""),

    # M
    q("self-iterator-exhausts", '''
        class Count:
            def __init__(self):
                self.i = 0
            def __iter__(self):
                return self
            def __next__(self):
                self.i += 1
                if self.i > 3:
                    raise StopIteration
                return self.i
        c = Count()
        print(list(c), list(c))
    ''', "[1, 2, 3] []",
      ["[1, 2, 3] [1, 2, 3]", "[1, 2, 3, 4] []", "[1, 2, 3] [4, 5]"],
      "An object that returns itself from __iter__ can only be walked once",
      """`__iter__` returns the very same object, so its counter is shared by both loops. The second
      `list(c)` finds the iterator already past the end and gets nothing. A container should return a fresh
      iterator from `__iter__` each time."""),

    # E
    q("call-dunder", '''
        class Adder:
            def __init__(self, n):
                self.n = n
            def __call__(self, x):
                return x + self.n
        add5 = Adder(5)
        print(add5(1), callable(add5), callable(Adder), callable(add5.n))
    ''', "6 True True False",
      ["6 True False False", "6 False True False", "6 True True True"],
      "An instance with __call__ is callable; the class always is",
      """Defining `__call__` makes instances callable like functions, so `add5(1)` is 6. Classes are callable
      too, since calling one builds an instance, but the plain int `5` stored in `add5.n` is not."""),

    # H
    q("call-on-instance-not-used", '''
        class A:
            pass
        a = A()
        a.__call__ = lambda: "hi"
        print(hasattr(a, "__call__"), callable(a))
    ''', "True False", ["True True", "False False", "False True"],
      "Special methods are looked up on the class, not on the instance",
      """The attribute exists on the instance, so `hasattr` says True. But `callable` and the `()` syntax look
      for `__call__` on the type, and `A` has none, so `a()` would be a TypeError."""),

    # M
    q("iadd-forgets-return", '''
        class Acc:
            def __init__(self):
                self.t = 0
            def __iadd__(self, n):
                self.t += n
        x = Acc()
        x += 5
        print(x)
    ''', "None", ["5", "0", "TypeError"],
      "x += n rebinds x to whatever __iadd__ returns",
      """The augmented assignment is `x = x.__iadd__(5)`. The method updated `t` but returned nothing, so `x`
      is now `None`. An in-place method must end with `return self`."""),

    # E
    q("getattr-only-when-missing", '''
        class G:
            x = 1
            def __getattr__(self, name):
                return f"missing {name}"
        g = G()
        g.y = 2
        print(g.x, g.y, g.z)
    ''', "1 2 missing z",
      ["missing x 2 missing z", "1 missing y missing z", "1 2 None"],
      "__getattr__ only runs after the normal lookup fails",
      """Attributes found on the instance or the class never reach `__getattr__`. It is the last resort, used
      only for `g.z`, which is not found anywhere. `__getattribute__` is the one that sees every access."""),

    # H
    q("non-data-descriptor-shadowed", '''
        class Get:
            def __get__(self, obj, owner):
                return "get"
        class GetSet(Get):
            def __set__(self, obj, value):
                pass
        class A:
            a = Get()
            b = GetSet()
        o = A()
        o.a = o.b = "set"
        print(o.a, o.b, o.__dict__)
    ''', "set get {'a': 'set'}",
      ["get get {}", "set set {'a': 'set', 'b': 'set'}", "get set {'b': 'set'}"],
      "Only a descriptor with __set__ beats the instance's own dictionary",
      """A data descriptor (it has `__set__`) intercepts both reading and writing, so `b` stays "get" and
      nothing lands in the instance dict. A descriptor with just `__get__` loses: the assignment stores `a`
      in the instance, and that value now wins."""),

    # M
    q("slots-no-dict", '''
        class P:
            __slots__ = ("x",)
        p = P()
        p.x = 1
        try:
            p.y = 2
        except AttributeError:
            print("no y", hasattr(p, "__dict__"))
    ''', "no y False", ["no y True", "2", "no x False"],
      "__slots__ removes the per-instance __dict__, so new names are refused",
      """With `__slots__` the instance has room only for the listed names and no `__dict__`. Setting `y`
      raises AttributeError, and the instance really has no dict to look at."""),

    # ── functools, collections, itertools, bisect, heapq ───────────────────
    # E
    q("reduce-empty-no-start", '''
        from functools import reduce
        print(reduce(lambda a, b: a + b, []))
    ''', "TypeError", ["0", "None", "[]"],
      "reduce() of nothing, with no start value, has no answer to give",
      """With an empty list and no initial value there is not even a first item to start from, so `reduce`
      raises TypeError. `sum` quietly returns 0 because it has a built-in start value; give `reduce` a third
      argument to get the same safety.""",
      raises=True),

    # M
    q("counter-ties-first-seen", '''
        from collections import Counter
        c = Counter("abcab")
        print(c.most_common(2), Counter("xyzzy").most_common(1))
    ''', "[('a', 2), ('b', 2)] [('y', 2)]",
      ["[('a', 2), ('b', 2)] [('z', 2)]", "[('a', 2), ('c', 1)] [('y', 2)]",
       "[('b', 2), ('a', 2)] [('y', 2)]"],
      "Counter ties keep the order the keys were first seen",
      """`most_common` sorts by count and the sort is stable, so keys with equal counts stay in the order
      they were first inserted. `a` came before `b`, and `y` before `z`."""),

    # M
    q("deque-rotate-direction", '''
        from collections import deque
        d = deque([1, 2, 3, 4, 5])
        d.rotate(2)
        first = list(d)
        d.rotate(-3)
        print(first, list(d))
    ''', "[4, 5, 1, 2, 3] [2, 3, 4, 5, 1]",
      ["[3, 4, 5, 1, 2] [5, 1, 2, 3, 4]", "[4, 5, 1, 2, 3] [5, 1, 2, 3, 4]",
       "[4, 5, 1, 2, 3] [1, 2, 3, 4, 5]"],
      "A positive rotate moves items to the right, a negative one to the left",
      """`rotate(2)` takes the last two items and puts them in front. `rotate(-3)` then moves three items from
      the front to the back, and the in-place method returns None, which is why the lists are saved first."""),

    # E
    q("extendleft-reverses", '''
        from collections import deque
        d = deque([1])
        d.extendleft([2, 3])
        print(list(d))
    ''', "[3, 2, 1]", ["[2, 3, 1]", "[1, 2, 3]", "[1, 3, 2]"],
      "extendleft adds the items one by one at the front, so they end up reversed",
      """Each item is pushed onto the left end in turn: 2 goes in front of 1, then 3 goes in front of 2. The
      result is the reverse of the iterable you passed."""),

    # M
    q("chainmap-writes-first", '''
        from collections import ChainMap
        a, b = {"x": 1}, {"x": 2, "y": 3}
        c = ChainMap(a, b)
        c["y"] = 9
        c["z"] = 0
        print(c["x"], c["y"], b["y"], a, len(c))
    ''', "1 9 3 {'x': 1, 'y': 9, 'z': 0} 3",
      ["1 9 9 {'x': 1, 'z': 0} 3", "2 9 3 {'x': 1, 'y': 9, 'z': 0} 3",
       "1 9 3 {'x': 1, 'y': 9, 'z': 0} 4"],
      "Reads search every map; writes always go into the first one",
      """A ChainMap looks a key up in each map in order but only ever changes the first. Setting `y` adds a
      new `y` to `a` and shadows the one in `b` rather than updating it. The length counts distinct keys: x, y, z."""),

    # M
    q("ordereddict-equality-order", '''
        from collections import OrderedDict
        a = OrderedDict(x=1, y=2)
        b = OrderedDict(y=2, x=1)
        before = a == b
        a.move_to_end("x")
        print(before, a == b, a == dict(b), list(a))
    ''', "False True True ['y', 'x']",
      ["True True True ['y', 'x']", "False False True ['x', 'y']", "False True False ['y', 'x']"],
      "Two OrderedDicts compare equal only with the same order; against a dict, order is ignored",
      """OrderedDict to OrderedDict equality checks the order of the keys too, so `before` is False. After
      `move_to_end("x")` both are y, x and they match. Compared with a plain dict the order never matters."""),

    # M
    q("namedtuple-replace", '''
        from collections import namedtuple
        P = namedtuple("P", "x y")
        p = P(1, 2)
        moved = p._replace(x=5)
        print(p, moved, p == (1, 2), p._asdict())
    ''', "P(x=1, y=2) P(x=5, y=2) True {'x': 1, 'y': 2}",
      ["P(x=5, y=2) P(x=5, y=2) True {'x': 1, 'y': 2}",
       "P(x=1, y=2) P(x=5, y=2) False {'x': 1, 'y': 2}",
       "P(x=1, y=2) P(x=5, y=2) True OrderedDict([('x', 1), ('y', 2)])"],
      "_replace returns a new tuple, and a namedtuple still equals the plain tuple",
      """Tuples are immutable, so `_replace` builds a copy and leaves `p` alone. Equality is inherited from
      tuple, so `p == (1, 2)` is True, and `_asdict()` gives a plain dict in current Python."""),

    # E
    q("partial-positional-first", '''
        from functools import partial
        print(partial(pow, 2)(5), partial(pow, exp=2)(5))
    ''', "32 25", ["25 32", "10 10", "32 32"],
      "partial's positional arguments go first; keyword ones fill a named slot",
      """`partial(pow, 2)(5)` is `pow(2, 5)`, which is 32. With `exp=2` the 2 is bound by name, so the later 5
      lands in the first free slot, the base, giving `pow(5, exp=2)`, or 25."""),

    # H
    q("lru-cache-shared-result", '''
        from functools import lru_cache
        @lru_cache(maxsize=None)
        def make(n):
            return [n]
        a = make(1)
        a.append(2)
        print(make(1), make(1) is a)
    ''', "[1, 2] True", ["[1] False", "[1] True", "[1, 2] False"],
      "The cache hands back the same object every time, not a copy",
      """`lru_cache` stores the returned list itself. Mutating it changes what every later call returns,
      because the second `make(1)` is a cache hit that returns that same, now longer, list."""),

    # M
    q("lru-cache-unhashable", '''
        from functools import lru_cache
        @lru_cache(maxsize=None)
        def total(xs):
            return sum(xs)
        print(total([1, 2]))
    ''', "TypeError", ["3", "None", "ValueError"],
      "Cached arguments become a dict key, so they must be hashable",
      """`lru_cache` builds a key from the arguments, and a list cannot be hashed, so the call fails with
      `unhashable type: 'list'` before the function body ever runs. Pass a tuple instead.""",
      raises=True),

    # H
    q("cache-key-spelling", '''
        from functools import lru_cache
        @lru_cache(maxsize=None)
        def f(x, y=0):
            return x + y
        f(1); f(1, 0); f(x=1); f(1, y=0)
        print(f.cache_info().misses, f.cache_info().hits)
    ''', "4 0", ["1 3", "2 2", "3 1"],
      "The same call spelled differently is a different cache key",
      """The cache key is built from the arguments as written: `f(1)`, `f(1, 0)`, `f(x=1)` and `f(1, y=0)` look
      different, so each one is a miss even though they all compute the same value."""),

    # M
    q("accumulate-forms", '''
        from itertools import accumulate
        print(list(accumulate([1, 2, 3, 4])),
              list(accumulate([1, 2, 3], initial=10)), list(accumulate("abc")))
    ''', "[1, 3, 6, 10] [10, 11, 13, 16] ['a', 'ab', 'abc']",
      ["[1, 3, 6, 10] [11, 13, 16] ['a', 'ab', 'abc']", "[1, 2, 6, 24] [10, 11, 13, 16] ['a', 'ab', 'abc']",
       "[1, 3, 6, 10] [10, 11, 13, 16] ['a', 'b', 'c']"],
      "accumulate is a running total; initial= adds a leading item, and strings concatenate",
      """The default operation is `+`, giving running totals. With `initial=10` the 10 is emitted first, then
      the totals continue from it. Adding strings joins them, so `"abc"` builds up `a`, `ab`, `abc`."""),

    # M
    q("permutations-duplicates", '''
        from itertools import permutations
        print(len(list(permutations("aab"))), len(set(permutations("aab"))))
    ''', "6 3", ["3 3", "6 6", "3 6"],
      "permutations works on positions, not on distinct values",
      """The two `a` letters are different positions, so 3! = 6 arrangements are produced, and some of them
      print identically. Putting them in a set shows only 3 different ones."""),

    # E
    q("chain-string-pieces", '''
        from itertools import chain
        words = ["ab", "cd"]
        print(list(chain("ab", "cd")), list(chain.from_iterable(words)),
              list(chain(words)))
    ''', "['a', 'b', 'c', 'd'] ['a', 'b', 'c', 'd'] ['ab', 'cd']",
      ["['ab', 'cd'] ['a', 'b', 'c', 'd'] ['ab', 'cd']", "['a', 'b', 'c', 'd'] ['ab', 'cd'] ['ab', 'cd']",
       "['a', 'b', 'c', 'd'] ['a', 'b', 'c', 'd'] ['a', 'b', 'c', 'd']"],
      "chain walks each argument; from_iterable walks each item of one argument",
      """`chain("ab", "cd")` has two arguments, each a string that is walked letter by letter. `from_iterable`
      takes one iterable and walks its items, which gives the same letters. `chain(["ab", "cd"])` has a single
      argument, so it just walks that list and gives its two strings."""),

    # H
    q("takewhile-eats-one", '''
        from itertools import takewhile
        it = iter([1, 2, 5, 3, 1])
        print(list(takewhile(lambda x: x < 4, it)), list(it))
    ''', "[1, 2] [3, 1]", ["[1, 2] [5, 3, 1]", "[1, 2, 3, 1] []", "[1, 2] []"],
      "takewhile has to read the first failing item to know it failed, and drops it",
      """To decide to stop, `takewhile` pulls 5 from the iterator and tests it. That item is thrown away, so
      the iterator continues from 3."""),

    # E
    q("zip-longest-fill", '''
        from itertools import zip_longest
        print(list(zip_longest("ab", [1, 2, 3], fillvalue="-")))
    ''', "[('a', 1), ('b', 2), ('-', 3)]",
      ["[('a', 1), ('b', 2)]", "[('a', 1), ('b', 2), (None, 3)]", "[('a', 1), ('b', 2), ('-', '-')]"],
      "zip_longest runs to the longest input and pads only the shorter ones",
      """Plain `zip` would stop after two pairs. `zip_longest` keeps going to the end of the longest input and
      fills the missing slots with `fillvalue`, here the short string's third slot."""),

    # M
    q("islice-relative-to-iterator", '''
        from itertools import islice
        it = iter(range(10))
        a = list(islice(it, 3))
        b = list(islice(it, 2, 4))
        print(a, b, next(it))
    ''', "[0, 1, 2] [5, 6] 7",
      ["[0, 1, 2] [2, 3] 4", "[0, 1, 2] [5, 6] 8", "[0, 1, 2] [3, 4] 5"],
      "islice counts from wherever the iterator currently is, and consumes what it skips",
      """After the first slice the iterator sits at 3. The second `islice(it, 2, 4)` skips 3 and 4 (consuming
      them), yields 5 and 6, then stops, leaving 7 as the next item."""),

    # H
    q("tee-then-original", '''
        from itertools import tee
        it = iter([1, 2, 3])
        a, b = tee(it)
        print(next(a), next(a), next(b), list(it))
    ''', "1 2 1 [3]", ["1 2 1 [1, 2, 3]", "1 2 1 []", "1 2 3 [3]"],
      "tee pulls from the original iterator, so using the original afterwards skips ahead",
      """`tee` shares one source: `next(a)` twice took 1 and 2 out of `it` (and saved them for `b`). `b` gets
      the saved 1, but the original `it` is now past those items and only has 3 left."""),

    # E
    q("bisect-left-right", '''
        from bisect import bisect_left, bisect_right
        a = [1, 2, 2, 3]
        print(bisect_left(a, 2), bisect_right(a, 2), bisect_left(a, 5))
    ''', "1 3 4", ["2 3 4", "1 2 4", "1 3 3"],
      "bisect_left goes before equal items, bisect_right after them",
      """These return insertion points in the sorted list. For the value 2 that is index 1 before both
      equal items, or index 3 after them. A value bigger than everything goes at the very end, index 4."""),

    # E
    q("heap-smallest-first", '''
        import heapq
        h = [5, 1, 4, 2, 3]
        heapq.heapify(h)
        print(h[0], heapq.nlargest(2, h), [heapq.heappop(h) for _ in range(3)])
    ''', "1 [5, 4] [1, 2, 3]",
      ["5 [5, 4] [5, 4, 3]", "1 [4, 5] [1, 2, 3]", "1 [5, 4] [5, 4, 3]"],
      "heapq is a min-heap: the front and the pops are the smallest",
      """`h[0]` is the smallest item, 1, and `heappop` hands items out smallest first. `nlargest` is a separate
      helper that lists the biggest ones, biggest first, without disturbing the heap."""),

    # M
    q("heap-tuple-tie", '''
        import heapq
        h = []
        heapq.heappush(h, (1, {"a": 1}))
        heapq.heappush(h, (1, {"b": 2}))
        print(h[0])
    ''', "TypeError", ["(1, {'a': 1})", "(1, {'b': 2})", "KeyError"],
      "Equal priorities make tuple comparison move on to the next item",
      """Tuples compare element by element. The two priorities tie at 1, so Python tries to compare the dicts,
      which have no ordering, and the second push raises TypeError. A tie-breaking counter before the payload
      fixes it.""",
      raises=True),

    # ── Strings, formatting, unpacking, comprehensions ─────────────────────
    # M
    q("partition-missing-sep", '''
        print("a=b=c".rpartition("="), "abc".partition("="), "abc".rpartition("="))
    ''', "('a=b', '=', 'c') ('abc', '', '') ('', '', 'abc')",
      ["('a', '=', 'b=c') ('abc', '', '') ('', '', 'abc')",
       "('a=b', '=', 'c') ('abc', '', '') ('abc', '', '')",
       "('a=b', '=', 'c') ('', '', 'abc') ('abc', '', '')"],
      "partition and rpartition always return three parts, and the empties land on opposite sides",
      """`rpartition` splits at the last separator. When the separator is missing, `partition` gives
      `(text, '', '')` but `rpartition` gives `('', '', text)`: the whole string goes to the side the search
      started from, which is the front for one and the back for the other."""),

    # M
    q("splitlines-keepends", r'''
        print("a\nb\r\n\nc\n".splitlines(), "a\nb".splitlines(True))
    ''', r"['a', 'b', '', 'c'] ['a\n', 'b']",
      [r"['a', 'b', '', 'c', ''] ['a\n', 'b']", r"['a', 'b', 'c'] ['a', 'b']",
       r"['a', 'b', '', 'c'] ['a', '\n', 'b']"],
      "splitlines drops a final newline, keeps blank lines, and keepends=True keeps the breaks",
      """A trailing newline does not create an empty last line (unlike `split("\\n")`), but a blank line in the
      middle is an empty string. `\\r\\n` counts as one break, and `keepends=True` leaves each break on its line."""),

    # H
    q("center-odd-padding", '''
        parts = ["ab".center(5, "."), "abc".center(6, "*")]
        parts += ["ab".center(4, "-"), "ab".center(1, "!")]
        print(*parts)
    ''', "..ab. *abc** -ab- ab",
      [".ab.. *abc** -ab- ab", "..ab. **abc* -ab- ab", "..ab. *abc** -ab- a"],
      "center puts the odd spare character on the left or right depending on the sizes",
      """With an odd amount of padding, `str.center` is not consistent: 3 spare characters in a width of 5 put
      the extra one on the left, while 3 in a width of 6 put it on the right. A width smaller than the text
      changes nothing, and it never truncates."""),

    # M
    q("casefold-eszett", '''
        s = "ß"
        print(len(s.upper()), s.casefold(), s.lower() == "ss", s.casefold() == "ss")
    ''', "2 ss False True", ["1 ss False True", "2 ss True True", "2 ß False False"],
      "upper and casefold of the German ß are two letters long",
      """`"ß".upper()` is `"SS"`, so the length changes. `casefold()` is the aggressive lowercasing meant for
      comparing text and gives `"ss"`, whereas `lower()` leaves the ß alone."""),

    # M
    q("translate-table", '''
        table = str.maketrans("abc", "xyz", "d")
        drop = {ord("l"): None, ord("h"): "J"}
        print("aabbccdd".translate(table), "hello".translate(drop))
    ''', "xxyyzz Jeo", ["xxyyzzdd Jeo", "xxyyzz Jello", "aabbccdd Jeo"],
      "translate maps by code point, and a third maketrans argument deletes characters",
      """`maketrans("abc", "xyz", "d")` replaces a, b, c by x, y, z and removes every d. A dict table maps
      numbers to a replacement, and the value `None` deletes that character."""),

    # H
    q("fstring-sign-and-pad", '''
        n = -42
        print(f"[{n:=6}] [{n:+}] [{255:#x}] [{'a'!r:>5}] [{n:06}]")
    ''', "[-   42] [-42] [0xff] [  'a'] [-00042]",
      ["[   -42] [-42] [0xff] [  'a'] [-00042]", "[-   42] [-42] [ff] [  'a'] [-00042]",
       "[-   42] [-42] [0xff] [a    ] [-00042]"],
      "'=' pads between the sign and the digits, and !r runs before the width",
      """`=` is sign-aware padding: the minus sign stays at the left edge and the spaces go after it. `#x`
      adds the `0x` prefix, `!r` turns `a` into `'a'` first (three characters) and then the width
      pads it to five."""),

    # E
    q("star-unpack-forms", '''
        a, *b, c = [1, 2, 3, 4]
        x, *y = "hi"
        *p, z = (7,)
        print(a, b, c, x, y, p, z)
    ''', "1 [2, 3] 4 h ['i'] [] 7",
      ["1 (2, 3) 4 h ['i'] () 7", "1 [2, 3] 4 hi [] [] 7", "1 [2, 3] 4 h i None 7"],
      "A starred name always collects a list, and may collect nothing",
      """The starred target takes whatever is left over and is always a list, even when unpacking a tuple
      or a string. If nothing is left it is an empty list, not `None`."""),

    # M
    q("walrus-in-tuple", '''
        a = (b := 1, 2)
        c = (d := 3) * 2
        print(a, b, c, d)
    ''', "(1, 2) 1 6 3", ["1 1 6 3", "(1, 2) (1, 2) 6 3", "(1, 2) 1 3 3"],
      "Inside a tuple, := only binds the item next to it",
      """`(b := 1, 2)` is a tuple of two items, the first of which assigns `b`. The walrus does not swallow the
      comma, so `a` is `(1, 2)` and `b` is just 1."""),

    # M
    q("any-list-vs-generator", '''
        seen = []
        def hit(x):
            seen.append(x)
            return x == 1
        any([hit(x) for x in (1, 2, 3)])
        first = len(seen)
        any(hit(x) for x in (1, 2, 3))
        print(first, len(seen) - first)
    ''', "3 1", ["1 1", "3 3", "1 3"],
      "A list comprehension runs completely before any() sees it; a generator stops early",
      """The square brackets build the whole list first, so all three calls happen. With a generator `any`
      asks for one item at a time and stops at the first true one, so only one call happens."""),

    # M
    q("deepcopy-keeps-aliasing", '''
        import copy
        a = [1]
        b = [a, a]
        c = copy.deepcopy(b)
        print(c[0] is c[1], c[0] is a, c == b)
    ''', "True False True", ["False False True", "True True True", "False True True"],
      "deepcopy copies a shared object once and keeps the sharing",
      """`deepcopy` remembers what it has already copied. Both slots of `c` hold the same new list, which is
      not `a`, and the new structure still compares equal to the old one."""),

    # M
    q("slice-assign-iterable", '''
        a = [1, 2, 3]
        a[1:2] = "xy"
        a[:0] = [0]
        a[10:] = [9]
        print(a)
    ''', "[0, 1, 'x', 'y', 3, 9]", ["[0, 1, 'xy', 3, 9]", "[0, 1, 'x', 3, 9]", "IndexError"],
      "Slice assignment takes any iterable and clamps out-of-range ends",
      """The right side is iterated, so a string is spread into its letters. `a[:0] = [0]` inserts at the
      front, and a slice starting past the end just appends, with no IndexError."""),

    # M
    q("dataclass-order", '''
        from dataclasses import dataclass
        @dataclass(order=True)
        class V:
            a: int
            b: int = 0
        x = V(1, 5)
        print(x < V(2, 0), x < V(1, 6), V(1) == V(1, 0), max(x, V(0, 9)))
    ''', "True True True V(a=1, b=5)",
      ["False True True V(a=1, b=5)", "True True False V(a=1, b=5)", "True True True V(a=0, b=9)"],
      "order=True compares the fields as tuples, in the order they are declared",
      """The generated comparisons behave like comparing `(a, b)` tuples, so the first field decides and the
      second only breaks ties. `V(1)` fills in the default `b=0`, so it equals `V(1, 0)`."""),

    # H
    q("cached-property-assign", '''
        from functools import cached_property
        class A:
            calls = 0
            @cached_property
            def v(self):
                A.calls += 1
                return 42
        a = A()
        a.v, a.v
        a.v = 7
        print(a.v, A.calls, "v" in a.__dict__)
    ''', "7 1 True", ["42 1 True", "7 2 True", "7 1 False"],
      "cached_property stores its result in the instance dict, where it can be overwritten",
      """The first access runs the function once and saves the value in `a.__dict__`, so later reads never
      reach the method. It is a descriptor without `__set__`, so plain assignment simply replaces the saved
      value, and 7 wins."""),

    # H
    q("exit-return-truthy", '''
        class Cm:
            def __init__(self, ret):
                self.ret = ret
            def __enter__(self):
                pass
            def __exit__(self, *exc):
                return self.ret
        def run(r):
            try:
                with Cm(r):
                    raise KeyError
            except KeyError:
                return "raised"
            return "quiet"
        print([run(r) for r in (0, "no", None)])
    ''', "['raised', 'quiet', 'raised']",
      ["['raised', 'raised', 'raised']", "['quiet', 'quiet', 'quiet']", "['raised', 'quiet', 'quiet']"],
      "Any truthy value returned from __exit__ swallows the exception",
      """Python only tests the truth of what `__exit__` returns. 0 and `None` let the error continue, but the
      string "no" is truthy, so it suppresses the exception just as `True` would."""),

    # M
    q("send-before-start", '''
        def g():
            x = yield 1
            print(x)
        it = g()
        it.send("hi")
    ''', "TypeError", ["hi", "StopIteration", "None"],
      "A generator that has not started can only be sent None",
      """The first `send` must deliver `None`, because there is no `yield` waiting yet to receive a value.
      Use `next(it)` to run up to the first `yield`, and send after that.""",
      raises=True),

    # H
    q("genexp-first-iterable-eager", '''
        xs = [1, 2]
        g = (x * 10 for x in xs)
        xs.append(3)
        xs = [7]
        print(list(g))
    ''', "[10, 20, 30]", ["[70]", "[10, 20]", "[10, 20, 30, 70]"],
      "A generator expression grabs its outermost iterable right away, but not what the list holds later",
      """The first `for` iterable is evaluated when the generator is created, so `g` is tied to that list
      object. Appending to it is seen later, while rebinding `xs` to a new list is not."""),

    # M
    q("decorator-without-parens", '''
        def tag(t):
            def deco(f):
                return lambda: f"<{t}>{f()}</{t}>"
            return deco
        @tag
        def hi():
            return "hi"
        print(hi())
    ''', "TypeError", ["<hi>hi</hi>", "hi", "NameError"],
      "A decorator factory used without () hands the function to the wrong layer",
      """`@tag` calls `tag(hi)`, so `t` becomes the function and the result is the inner `deco`. Calling
      `hi()` is then calling `deco()` without its `f` argument, which is a TypeError.""",
      raises=True),

    # E
    q("closures-share-one-cell", '''
        def make():
            n = 0
            def inc():
                nonlocal n
                n += 1
                return n
            def get():
                return n
            return inc, get
        inc, get = make()
        inc(); inc()
        inc2, get2 = make()
        inc2()
        print(get(), get2())
    ''', "2 1", ["2 2", "0 1", "3 1"],
      "Closures made by one call share a variable; a second call makes a fresh one",
      """`inc` and `get` from the same `make()` call look at the same `n`, so `get()` sees the two increments.
      The second call to `make` creates a brand-new `n`, so `get2()` sees only its own one increment."""),

    # M
    q("int-underscores-and-bases", '''
        print(int("1_000"), int("0b11", 0), int("0x1f", 16), float("1_0.5e1"))
    ''', "1000 3 31 105.0", ["ValueError", "1000 3 0 105.0", "1000 3 31 10.5"],
      "int() and float() accept underscores, and a prefix is valid when it matches the base",
      """Underscores between digits are allowed in the text just as in source code. Base 0 reads the prefix
      to decide the base, and `0x` is also accepted when the base is 16. `1_0.5e1` is 10.5 times 10."""),

    # E
    q("type-names-list", '''
        things = (1, 1.0, {}, {1}, (), (1), None, ..., len, type)
        print([type(t).__name__ for t in things])
    ''', "['int', 'float', 'dict', 'set', 'tuple', 'int', 'NoneType', 'ellipsis', "
         "'builtin_function_or_method', 'type']",
      ["['int', 'float', 'set', 'set', 'tuple', 'tuple', 'NoneType', 'ellipsis', "
       "'builtin_function_or_method', 'type']",
       "['int', 'float', 'dict', 'set', 'tuple', 'int', 'None', 'Ellipsis', 'function', 'type']",
       "['int', 'float', 'dict', 'set', 'list', 'int', 'NoneType', 'ellipsis', "
       "'builtin_function_or_method', 'type']"],
      "{} is a dict, (1) is just an int, and None has a class called NoneType",
      """Empty braces make a dict, a set needs at least one item. Parentheses alone do not make a tuple (the
      comma does), and built-in functions like `len` have the type `builtin_function_or_method`."""),

    # H
    q("raise-from-none-context", '''
        try:
            try:
                1 / 0
            except ZeroDivisionError:
                raise ValueError("bad") from None
        except ValueError as v:
            print(v.__cause__, type(v.__context__).__name__, v.__suppress_context__)
    ''', "None ZeroDivisionError True",
      ["None None False", "ZeroDivisionError ZeroDivisionError True", "None ZeroDivisionError False"],
      "from None clears __cause__ but the original is still kept as __context__",
      """`raise ... from None` sets `__suppress_context__` so a traceback does not show the earlier error, but
      `__context__` still records it. `__cause__` is what `from x` sets, and here it is `None`."""),

    # E
    q("else-block-not-covered", '''
        try:
            try:
                pass
            except ValueError:
                print("inner")
            else:
                raise ValueError
        except ValueError:
            print("outer")
    ''', "outer", ["inner", "inner outer", "ValueError"],
      "An error raised in the else block is not caught by the same try's except clauses",
      """The `except` clauses only guard the `try` body. Errors from `else` (and `finally`) are not caught by
      them, so this one flies on to the outer handler."""),

    # H
    q("match-guards-and-classes", '''
        def f(v):
            match v:
                case {"k": 1, **rest}: return f"map {rest}"
                case [x, y] if x == y: return "pair-eq"
                case [_, _]: return "pair"
                case int() | float() as n if n > 0: return "pos"
                case _: return "other"
        print(f({"k": 1, "z": 2}), f([1, 1]), f((1, 2)), f(True), f(-1))
    ''', "map {'z': 2} pair-eq pair pos other",
      ["map {'k': 1, 'z': 2} pair-eq pair pos other", "map {'z': 2} pair-eq pair other other",
       "map {'z': 2} pair pair pos other"],
      "Mapping patterns match extra keys, a tuple fits a sequence pattern, and True is an int",
      """`**rest` collects the keys the pattern did not name. A tuple matches `[x, y]` like a list does, the
      guard picks between the two pair cases, and `int()` accepts `True` because bool is a subclass of int."""),

    # M
    q("flag-auto-values", '''
        from enum import Flag, auto
        class P(Flag):
            R = auto()
            W = auto()
            X = auto()
        rw = P.R | P.W
        print(rw.value, P.W in rw, P.X in rw, (P.R | P.X).value)
    ''', "3 True False 5", ["3 True False 4", "3 False False 5", "3 True True 5"],
      "auto() in a Flag hands out powers of two, so members combine without overlapping",
      """`R`, `W`, `X` are 1, 2 and 4, which are separate bits. `R | W` is 3, `in` tests that a bit is set,
      and `R | X` is 5. In a plain Enum `auto()` would count 1, 2, 3 instead."""),

    # M
    q("capwords-vs-title", '''
        import string
        s = "big-world wide"
        print(string.capwords(s), "|", s.title(), "|", s.capitalize())
    ''', "Big-world Wide | Big-World Wide | Big-world wide",
      ["Big-World Wide | Big-World Wide | Big-World Wide", "Big-world Wide | Big-world Wide | Big-world wide",
       "Big-world wide | Big-World Wide | Big-world wide"],
      "capwords splits on whitespace only; title() starts a new word after any non-letter",
      """`capwords` treats only whitespace as a word break, so the hyphenated word is capitalized once.
      `str.title()` starts a new word after every non-letter, so the `W` after the hyphen is capital too,
      and `capitalize()` touches only the very first letter."""),

    # H
    q("popitem-after-argument-eval", '''
        d = {"a": 1, "b": 2, "c": 3}
        d["a"] = 9
        d.popitem()
        del d["b"]
        d["b"] = 0
        print(d, list(d.items())[-1], d.popitem())
    ''', "{'a': 9} ('b', 0) ('b', 0)",
      ["{'a': 9, 'b': 0} ('b', 0) ('b', 0)", "{'a': 9, 'b': 0} ('b', 0) ('a', 9)",
       "{'a': 9} ('b', 0) ('a', 9)"],
      "print receives the same dict object, so it shows the dict after popitem ran",
      """All the arguments are evaluated before printing starts. `popitem()` removes the newest item, `b`,
      while the dict is still waiting to be printed, so it shows as `{'a': 9}`. Re-assigning `a` kept its
      original position, and `b` came back last."""),

    # M
    q("chained-compare-custom", '''
        log = []
        class V:
            def __init__(self, n):
                self.n = n
            def __lt__(self, other):
                log.append(f"{self.n}<{other.n}")
                return self.n < other.n
        a, b, c = V(3), V(2), V(1)
        print(a < b < c, log)
    ''', "False ['3<2']", ["False ['3<2', '2<1']", "True ['3<2']", "False []"],
      "A chain stops at the first False link",
      """`a < b < c` means `a < b and b < c` with `b` evaluated only once. The first comparison is already
      False, so the second `__lt__` is never called."""),

    # M
    q("dict-missing-hook", '''
        class D(dict):
            def __missing__(self, key):
                return key * 2
        d = D(a=1)
        print(d["a"], d["zz"], d.get("zz"), "zz" in d, len(d))
    ''', "1 zzzz None False 1",
      ["1 zzzz zzzz False 1", "1 zzzz None True 2", "1 zzzz None False 2"],
      "__missing__ is only used by [], not by get() or in, and it does not store anything",
      """Indexing a missing key calls `__missing__`, which here just computes a value. `get` and `in` bypass
      the hook, and nothing is inserted, so the dict still has one item (unlike a `defaultdict`)."""),

    # M
    q("new-runs-init-again", '''
        class S:
            inst = None
            def __new__(cls):
                if cls.inst is None:
                    cls.inst = super().__new__(cls)
                return cls.inst
            def __init__(self):
                self.count = getattr(self, "count", 0) + 1
        a, b = S(), S()
        print(a is b, a.count)
    ''', "True 2", ["True 1", "False 1", "False 2"],
      "__init__ runs on every S(), even when __new__ returns the old instance",
      """After `__new__` returns an instance of the class, Python calls `__init__` on it, every time. The
      singleton is reused but re-initialized, so the counter goes to 2."""),

    # M
    q("round-ndigits-type", '''
        print(round(2.5), round(2.5, 0), round(3.5, 0), round(1234, -2))
    ''', "2 2.0 4.0 1200", ["3 3.0 4.0 1200", "2 2 4 1200", "2 2.0 4.0 1234"],
      "round(x) gives an int, round(x, 0) keeps the float, and both round half to even",
      """With no second argument `round` returns an int; with any `ndigits`, even 0, it returns the same type
      it was given. Halves go to the nearest even number, so 2.5 becomes 2 and 3.5 becomes 4."""),

    # E
    q("power-negative-exponent", '''
        print(2 ** -1, type(2 ** 2).__name__, type(2 ** -2).__name__, 0 ** 0)
    ''', "0.5 int float 1", ["0 int int 1", "0.5 float float 1", "0.5 int float 0"],
      "A negative exponent makes a float, and 0 ** 0 is 1",
      """Integer powers stay ints only when the exponent is not negative. `2 ** -1` is the float 0.5, not
      integer division. Python defines `0 ** 0` as 1."""),

    # E
    q("implicit-concat-binds-first", '''
        print("a" "b" * 2, "a" + "b" * 2)
    ''', "abab abb", ["abb abb", "abab abab", "abb abab"],
      "Neighbouring string literals are joined before any operator runs",
      """`"a" "b"` is a single literal `"ab"` made while the code is compiled, so `* 2` repeats all of it.
      With an explicit `+`, the multiplication binds tighter and only `"b"` is repeated."""),

    # E
    q("filter-none-truthiness", '''
        print(list(filter(None, [0, 1, "", "0", [], [0], None])))
    ''', "[1, '0', [0]]", ["[1]", "[1, [0]]", "[1, '0']"],
      "filter(None, ...) keeps what is truthy, and '0' or [0] are not empty",
      """Passing `None` as the function keeps every item that is truthy. The string `"0"` and the list `[0]`
      are non-empty, so they stay. Only 0, `""`, `[]` and `None` are dropped."""),

    # M
    q("isnumeric-family", '''
        a, b = "²", "½"
        print(a.isdecimal(), a.isdigit(), a.isnumeric(), b.isnumeric(), b.isdigit())
    ''', "False True True True False",
      ["True True True True True", "False False True True False", "False True True False False"],
      "isdecimal is strictest, isdigit adds superscripts, isnumeric adds fractions",
      """A superscript two is a digit but not a decimal digit, so `int("²")` would fail. A vulgar fraction like
      one half is numeric, but not a digit. The three tests are nested: decimal, then digit, then numeric."""),

    # ── Plain-looking traps: numbers, text, containers, standard library ───
    # E
    q("number-literal-forms", '''
        print(1_000 + 1, 0o10, 0b11, 0xff, 1e3)
    ''', "1001 8 3 255 1000.0",
      ["1001 10 11 ff 1000", "1001 10 11 255 1000.0", "2 8 3 255 1000"],
      "Prefixed literals are numbers, and 1e3 is a float",
      """`0o10` is octal for 8, `0b11` is binary for 3 and `0xff` is hexadecimal for 255, and all of them print
      as ordinary decimal ints. Underscores are ignored, and the exponent form `1e3` always makes a float."""),

    # E
    q("join-over-string", '''
        print("-".join("abc"), "-".join(["abc"]), "-".join(["a", "b"]))
    ''', "a-b-c abc a-b", ["abc abc a-b", "a-b-c a-b-c a-b", "a-b-c abc a-b-"],
      "join walks whatever it is given, and a string is a sequence of letters",
      """`join` puts the separator between the items. A string's items are its letters, so `"abc"` gives
      `a-b-c`. A one-item list has nothing to put a separator next to."""),

    # E
    q("abs-of-complex", '''
        print(abs(-3), abs(-3.5), abs(-0.0), abs(3 + 4j))
    ''', "3 3.5 0.0 5.0", ["3 3.5 -0.0 7", "3 3.5 0.0 7.0", "3 3.5 -0.0 5.0"],
      "abs of a complex number is its length, a float",
      """For `3 + 4j` the result is the distance from the origin, `sqrt(3**2 + 4**2)`, which is 5.0. And
      `abs(-0.0)` gives positive `0.0`."""),

    # E
    q("sqrt-float-vs-isqrt", '''
        import math
        print(math.sqrt(16), 16 ** 0.5, math.isqrt(17), 16 ** (1 / 2))
    ''', "4.0 4.0 4 4.0", ["4 4 4 4", "4.0 4.0 4.0 4.0", "4 4.0 4 4"],
      "sqrt and fractional powers are floats; isqrt is the integer square root",
      """Even for a perfect square `math.sqrt` returns a float, and so does `**` with a fractional exponent.
      `math.isqrt` works on ints, rounds down and returns an int, so `isqrt(17)` is 4."""),

    # E
    q("len-of-bytes", '''
        print(len("héllo"), len("héllo".encode()), len("日本"), len("日本".encode()))
    ''', "5 6 2 6", ["6 5 2 6", "5 5 2 2", "5 6 6 6"],
      "len of a string counts characters; len of its UTF-8 bytes counts bytes",
      """A string has 5 characters in `héllo`, but the `é` takes two bytes in UTF-8, so the encoded version
      has 6. Each of the two Japanese characters takes three bytes."""),

    # E
    q("list-plus-tuple", '''
        print([1, 2] + (3,))
    ''', "TypeError", ["[1, 2, 3]", "(1, 2, 3)", "[1, 2, (3,)]"],
      "+ does not mix lists and tuples",
      """Both sides of `+` must be the same sequence type. Python refuses to guess which type the result
      should have: `[1, 2] + list((3,))` or `[1, 2] += (3,)` work, but this one is an error.""",
      raises=True),

    # E
    q("split-empty-separator", '''
        print("abc".split(""))
    ''', "ValueError", ["['a', 'b', 'c']", "['abc']", "['', 'a', 'b', 'c', '']"],
      "Python refuses an empty separator; use list(text) for the letters",
      """Splitting on nothing is ill-defined, so `str.split("")` raises `ValueError: empty separator`.
      `list("abc")` is the way to get the letters (JavaScript's `split("")` would work, Python's does not).""",
      raises=True),

    # E
    q("pop-forms", '''
        x = [1, 2, 3, 4]
        print(x.pop(), x.pop(0), x.pop(-1), x)
    ''', "4 1 3 [2]", ["1 2 3 [4]", "4 1 2 [3]", "4 1 3 [2, 3]"],
      "pop() takes the last item, pop(i) takes index i, and each call changes the list",
      """The first call removes and returns the last item, 4. `pop(0)` then removes the first, 1, and `pop(-1)`
      the last of what remains, 3. Only 2 is left."""),

    # E
    q("map-int-over-string", '''
        n = "123"
        print(list(map(int, n)), sum(map(int, n)), list(map(str.upper, "ab")))
    ''', "[1, 2, 3] 6 ['A', 'B']", ["[123] 123 ['AB']", "[1, 2, 3] 6 ['AB']", "[1, 2, 3] 123 ['A', 'B']"],
      "map over a string works one character at a time",
      """A string is iterated letter by letter, so `map(int, "123")` converts three one-digit strings. The sum
      is 1 + 2 + 3, and `str.upper` is applied to each letter separately."""),

    # E
    q("isclose-zero", '''
        import math
        s = 0.1 + 0.2
        print(math.isclose(s, 0.3), s == 0.3, math.isclose(1e-10, 0))
    ''', "True False False", ["True False True", "False False False", "True True False"],
      "isclose is relative by default, so nothing is close to 0 without abs_tol",
      """`0.1 + 0.2` is a hair off 0.3, but `isclose` allows a relative error of 1e-9, so it says True. The
      relative error against 0 is infinite, so `isclose(1e-10, 0)` is False unless you pass `abs_tol`."""),

    # E
    q("math-helpers-empty", '''
        import math
        a = math.gcd(12, 18), math.lcm(4, 6), math.factorial(5)
        print(*a, math.comb(5, 2), math.prod([]))
    ''', "6 12 120 10 1", ["6 24 120 10 1", "6 12 120 20 1", "6 12 120 10 0"],
      "comb counts choices without order, lcm is not the product, and the empty product is 1",
      """`lcm(4, 6)` is 12, not 24. `comb(5, 2)` is 5 * 4 / 2 = 10, while 20 would count order. An empty product
      is 1 (the multiplicative start value), unlike an empty sum, which is 0."""),

    # E
    q("startswith-tuple-empty", '''
        t = "abc"
        a = t.startswith(("x", "a")), t.startswith("abcd")
        print(*a, "".startswith(""), t.endswith(""))
    ''', "True False True True", ["True False False True", "False False True True", "True False True False"],
      "startswith accepts a tuple of options, and the empty prefix always matches",
      """A tuple means "any of these", so one match is enough. The empty string is a prefix and a suffix of
      every string, even of itself. A prefix longer than the text cannot match."""),

    # E
    q("empty-string-predicates", '''
        print("".isalpha(), "".isalnum(), all(""), "".isspace(), "".isupper())
    ''', "False False True False False",
      ["True True True True True", "False False False False False", "True True True False False"],
      "The str.is... tests need at least one character, but all() of nothing is True",
      """`isalpha`, `isalnum`, `isspace` and the other string tests return False for an empty string because
      they require at least one character. `all("")` has no character failing, so it is vacuously True."""),

    # E
    q("pairwise-and-starmap", '''
        from itertools import pairwise, starmap
        a = list(pairwise([1, 2, 3])), list(pairwise([1]))
        print(*a, list(starmap(pow, [(2, 3), (3, 2)])))
    ''', "[(1, 2), (2, 3)] [] [8, 9]", ["[(1, 2), (3, 1)] [] [8, 9]", "[(1, 2), (2, 3)] [(1,)] [8, 9]",
       "[(1, 2), (2, 3)] [] [6, 6]"],
      "pairwise gives overlapping neighbours, and one item has no neighbour",
      """`pairwise` slides a window of two over the input, so n items make n-1 pairs and a single item makes
      none. `starmap` unpacks each tuple into arguments, so the results are `pow(2, 3)` and `pow(3, 2)`."""),

    # E
    q("percent-format-dict", '''
        d = {"a": "x", "b": 2.9}
        print("%(a)s-%(b)d" % d, "%d%%" % 7.99, "%s" % None, "%r" % "a")
    ''', "x-2 7% None 'a'", ["x-3 8% None a", "x-2.9 7.99% None 'a'", "x-2 7% 'None' 'a'"],
      "%d truncates a float, %% prints a percent sign, %r shows the repr",
      """`%d` converts to an int by truncating, so 2.9 becomes 2 and 7.99 becomes 7, with no rounding. `%%`
      is a literal percent sign, `%s` of `None` is the text `None`, and `%r` keeps the quotes."""),

    # E
    q("bytes-basics", r'''
        print(str(b"hi"), b"hi".decode(), bytes(3), bytes([65, 66]), b"ab"[0])
    ''', r"b'hi' hi b'\x00\x00\x00' b'AB' 97",
      [r"hi hi b'\x00\x00\x00' b'AB' 97", r"b'hi' hi b'3' b'AB' 97", r"b'hi' hi b'\x00\x00\x00' b'AB' b'a'"],
      "bytes(3) is three zero bytes, and indexing bytes gives an int",
      """`str()` of a bytes object shows its `b'...'` repr rather than decoding it. `bytes(3)` makes 3 zero
      bytes, not the text "3", and `b"ab"[0]` is the number 97, not a one-byte object."""),

    # E
    q("dataclass-default-factory", '''
        from dataclasses import dataclass, field
        @dataclass
        class C:
            xs: list = field(default_factory=list)
            n: int = 0
        a, b = C(), C()
        a.xs.append(1)
        print(b.xs, a == b, C([1]) == a)
    ''', "[] False True", ["[1] False True", "[] True True", "[] False False"],
      "default_factory builds a new list per instance, and equality compares fields",
      """Each `C()` calls `list()` again, so `b` is not affected by `a`'s change. Instances are equal when
      their fields are equal, so `a` equals `C([1])` but not `b`."""),

    # H
    q("max-ties-first", '''
        print(max(1, 2.0), max(2, 2.0), max(2.0, 2), min(True, 1))
    ''', "2.0 2 2.0 True", ["2.0 2.0 2 1", "2.0 2.0 2.0 True", "2.0 2 2 1"],
      "When values tie, max and min return the first one they met",
      """`max` only replaces its current best when the next value is strictly bigger. For equal values the
      earlier argument wins, so the int `2` or the float `2.0` comes out depending on position, and
      `min(True, 1)` returns `True`."""),

    # M
    q("eq-notimplemented", '''
        class A:
            def __eq__(self, other):
                return NotImplemented
        a = A()
        print(a == A(), a == a, a != A(), a == 1)
    ''', "False True True False", ["False True False False", "True True False False", "False False True False"],
      "If both sides answer NotImplemented, == falls back to identity",
      """When neither operand knows how to compare, `==` ends up comparing identities, so an object equals
      only itself. `!=` is the inverse, so a different instance is unequal."""),

    # H
    q("custom-hash-eq-dict", '''
        class K:
            def __init__(self, v):
                self.v = v
            def __hash__(self):
                return 1
            def __eq__(self, other):
                return self.v == other.v
        d = {K(1): "a", K(2): "b"}
        d[K(1)] = "c"
        print(len(d), d[K(1)], K(1) in {K(1)}, K(3) in d)
    ''', "2 c True False", ["3 a True False", "2 a True False", "2 c True True"],
      "A dict needs equal hashes to find a key, then == to confirm it",
      """Every key has hash 1, so they all land in the same place and `__eq__` decides. `K(1)` equals the
      existing key, so the assignment replaces `"a"` with `"c"` instead of adding a third entry. `K(3)`
      is equal to none of them."""),

    # H
    q("property-override-loses-setter", '''
        class A:
            @property
            def x(self):
                return 1
            @x.setter
            def x(self, v):
                pass
        class B(A):
            @property
            def x(self):
                return 2
        b = B()
        try:
            b.x = 5
        except AttributeError:
            print("read-only", b.x)
    ''', "read-only 2", ["2", "read-only 1", "TypeError"],
      "Redefining a property in a subclass replaces the whole thing, setter included",
      """`B.x` is a brand-new property with only a getter. It does not inherit the setter of `A.x`, so the
      assignment raises AttributeError. A subclass has to attach its own `.setter`."""),

    # H
    q("bound-method-identity", '''
        class A:
            def f(self):
                pass
        a = A()
        print(a.f == a.f, a.f is a.f, A.f is A.f)
    ''', "True False True", ["True True True", "False False True", "True False False"],
      "Each a.f makes a new bound method object, which still compares equal",
      """Functions are descriptors: reading `a.f` builds a fresh bound-method wrapper every time. Two
      wrappers around the same function and instance are equal but not the same object, while `A.f` is
      the plain function itself."""),

    # H
    q("dict-ior-iterable", '''
        a = {"x": 1}
        a |= [("y", 2)]
        print(a, a | {"x": 0})
    ''', "{'x': 1, 'y': 2} {'x': 0, 'y': 2}",
      ["{'x': 1} {'x': 0, 'y': 2}", "TypeError", "{'x': 1, 'y': 2} {'x': 1, 'y': 2}"],
      "|= works like update() and takes pairs, | needs two dicts, and the right side wins",
      """`a |= other` is `a.update(other)`, so a list of pairs is fine. A plain `a | b` builds a new dict and
      in a clash the right-hand value wins, so `x` becomes 0 in the copy while `a` itself is unchanged."""),

    # H
    q("zip-eats-one-extra", '''
        a = iter([1, 2, 3])
        b = iter([10, 20])
        pairs = list(zip(a, b))
        c = iter([1, 2, 3])
        d = iter([10, 20])
        list(zip(d, c))
        print(pairs, next(a, "done"), next(c, "done"))
    ''', "[(1, 10), (2, 20)] done 3", ["[(1, 10), (2, 20)] 3 3", "[(1, 10), (2, 20)] done done",
       "[(1, 10), (2, 20)] 3 done"],
      "zip pulls from its inputs in order, so the first one loses an item at the end",
      """On the third round `zip(a, b)` takes 3 from `a` first and only then finds `b` empty, so that 3 is
      lost and `a` is exhausted. With the short iterator first, `zip(d, c)` stops before touching `c`, and
      the 3 is still there."""),

    # H
    q("except-star-split", '''
        try:
            raise ExceptionGroup("g", [ValueError(1), TypeError(2)])
        except* ValueError as eg:
            print(len(eg.exceptions), type(eg).__name__)
        except* TypeError:
            pass
    ''', "1 ExceptionGroup", ["2 ValueError", "1 ValueError", "2 ExceptionGroup"],
      "except* picks matching errors out of a group; the handler gets a smaller group",
      """Each `except*` clause receives a new ExceptionGroup holding only the errors it matches, so the
      ValueError handler sees a group of one. Every clause can run for the same raise, unlike a normal
      `except`, which stops at the first match."""),

    # M
    q("name-mangling", '''
        class A:
            def __init__(self):
                self.__x = 1
        a = A()
        print(hasattr(a, "__x"), hasattr(a, "_A__x"), sorted(vars(a)))
    ''', "False True ['_A__x']", ["True False ['__x']", "True True ['__x']", "False True ['__x']"],
      "A double-underscore name inside a class is renamed to _ClassName__name",
      """Python rewrites `self.__x` to `self._A__x` when compiling the class body, so the plain name does not
      exist on the instance. It is a way to avoid clashes with subclasses, not real privacy."""),

    # H
    q("posixpath-join-reset", '''
        import posixpath
        print(posixpath.join("a", "/b", "c"), posixpath.splitext("a.tar.gz"),
              repr(posixpath.basename("a/b/")))
    ''', "/b/c ('a.tar', '.gz') ''", ["a/b/c ('a.tar', '.gz') ''", "/b/c ('a', '.tar.gz') ''",
       "/b/c ('a.tar', '.gz') 'b'"],
      "An absolute part restarts the join, and a trailing slash leaves an empty basename",
      """`join` restarts from the last absolute component, so `a` is thrown away. `splitext` only splits at the
      last dot. `basename("a/b/")` is what follows the final slash, which is nothing."""),
)
