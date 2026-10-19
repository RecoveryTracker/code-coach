"""Gotchas, Python: short programs where the obvious reading is a trap.

Every answer here is written by hand and then *run* by tests/test_gotchas_content.py in the
real interpreter (three different PYTHONHASHSEED values); the test fails if what the program
prints is not the marked answer. The three wrong options are the real misreads, never filler.
Nothing may depend on randomness, the clock, `id()` or hash order, and each program prints
exactly one line (or, with raises=True, dies with the named error having printed nothing).
"""

from __future__ import annotations

from .items import Item, make

q = make("python")

ITEMS: tuple[Item, ...] = (
    # ── The two the whole mode started from ────────────────────────────────
    q("score-90", '''
        score = 90
        if score > 90:
            print("A")
        elif score >= 90 and score < 90:
            print("B")
        elif score == 100:
            print("C")
        else:
            print("D")
    ''', "D", ["A", "B", "C"],
      "A condition that can never be true",
      """90 is not greater than 90, so the first branch is out. `score >= 90 and score < 90` asks for a
      number that is both at least 90 and below 90, which nothing is, and score is not 100, so only
      the else runs. Nothing here ever gives 90 an 'A'."""),

    q("loop-var-list", '''
        arr = [1, 2, 3]
        for i in arr:
            i = i * 2
        print(arr)
    ''', "[1, 2, 3]", ["[2, 4, 6]", "[1, 4, 9]", "Error"],
      "Rebinding the loop variable does not change the list",
      """`i` is only a name that points at each element in turn. `i = i * 2` points the name at a new
      number and leaves the list alone, because ints cannot be changed in place."""),

    # ── Rebinding vs mutating ───────────────────────────────────────────────
    q("loop-append-inner", '''
        lst = [[1], [2]]
        for x in lst:
            x.append(0)
        print(lst)
    ''', "[[1, 0], [2, 0]]", ["[[1], [2]]", "[[1, 0], [2]]", "[1, 0, 2, 0]"],
      "Mutating through the loop variable does change the list",
      """Each `x` is the very same inner list that sits in `lst`, not a copy. `x.append(0)` changes that
      list in place, so the change shows up in `lst`. Compare with `x = x * 2`, which would not."""),

    q("loop-index-assign", '''
        nums = [1, 2, 3]
        for n in nums:
            n += 10
        for i in range(len(nums)):
            nums[i] += 1
        print(nums)
    ''', "[2, 3, 4]", ["[11, 12, 13]", "[12, 13, 14]", "[1, 2, 3]"],
      "Only item assignment writes back into the list",
      """`n += 10` rebinds the loop variable and the list never hears about it. `nums[i] += 1` assigns
      into the list itself, so only the second loop changes anything: each item goes up by one."""),

    q("loop-var-after", '''
        for i in range(3):
            i += 10
        print(i)
    ''', "12", ["2", "3", "13"],
      "The loop variable outlives the loop, and so does your last change to it",
      """After the loop, `i` is still the name from the last pass: 2 from range, plus 10 from the
      body, so 12. A for loop does not clean its variable up, and it never ends on 3."""),

    q("loop-var-reset", '''
        seen = []
        for i in range(3):
            seen.append(i)
            i = 5
        print(seen)
    ''', "[0, 1, 2]", ["[0, 5, 5]", "[5, 5, 5]", "[0]"],
      "Rebinding the loop variable does not affect the next pass",
      """Every pass starts by assigning the next number from range to `i`, whatever the body did to it
      last time. Setting `i = 5` at the bottom only lasts until the loop picks the next value."""),

    q("string-immutable", '''
        s = "abc"
        s.upper()
        print(s)
    ''', "abc", ["ABC", "Error", "None"],
      "Strings never change; their methods return new ones",
      """`s.upper()` builds a new string and hands it back, and here the result is thrown away. `s` still
      points at the original, because strings cannot be changed in place."""),

    q("tuple-holds-list", '''
        t = ([1], 2)
        t[0].append(9)
        print(t)
    ''', "([1, 9], 2)", ["([1], 2)", "TypeError", "([1, 9], 2, 9)"],
      "An immutable tuple can hold a mutable list",
      """A tuple fixes which objects it holds, not what those objects contain. The list inside is still
      a normal list, so appending to it is fine; only `t[0] = ...` would raise TypeError."""),

    q("comprehension-scope", '''
        x = 10
        squares = [x * x for x in range(3)]
        print(x)
    ''', "10", ["2", "0", "[0, 1, 4]"],
      "A comprehension has its own scope in Python 3",
      """The `x` inside the comprehension is a separate variable that disappears when it finishes, so
      the outer `x` is untouched. (Python 2 used to leak it, which is where the idea comes from.)"""),

    q("param-rebind", '''
        def f(lst):
            lst = lst + [4]

        a = [1, 2, 3]
        f(a)
        print(a)
    ''', "[1, 2, 3]", ["[1, 2, 3, 4]", "None", "[4]"],
      "Reassigning a parameter vs mutating it",
      """`lst + [4]` makes a new list and `lst =` points the local name at it. The caller's list was never
      touched. Mutating it with `lst.append(4)` would have changed `a`."""),

    q("param-augmented", '''
        def f(lst):
            lst += [4]

        a = [1, 2, 3]
        f(a)
        print(a)
    ''', "[1, 2, 3, 4]", ["[1, 2, 3]", "[4]", "None"],
      "+= on a list changes it in place",
      """For lists, `+=` calls `extend` on the same object instead of making a new one. So unlike
      `lst = lst + [4]`, it does reach the caller's list."""),

    q("param-int", '''
        def bump(n):
            n += 1

        x = 5
        bump(x)
        print(x)
    ''', "5", ["6", "None", "Error"],
      "Ints are immutable, so a function cannot change the caller's",
      """`n += 1` builds a new int and rebinds the local name `n`. The caller's `x` still points at 5."""),

    q("remove-while-iterating", '''
        nums = [1, 2, 3, 4]
        for n in nums:
            nums.remove(n)
        print(nums)
    ''', "[2, 4]", ["[]", "[1, 2, 3, 4]", "[4]"],
      "Changing a list while looping over it",
      """The loop walks by position. After 1 is removed, 2 slides into index 0, and the loop moves on to
      index 1, which is now 3. So 2 and 4 are skipped and survive."""),

    q("dict-change-iterating", '''
        d = {"a": 1}
        for k in d:
            d[k + "x"] = 2
        print(d)
    ''', "RuntimeError", ["{'a': 1, 'ax': 2}", "{'a': 1}", "{'a': 1, 'ax': 2, 'axx': 2}"],
      "Adding keys while looping over a dict",
      """A dict refuses to change size while it is being iterated: the next step of the loop raises
      RuntimeError ('dictionary changed size during iteration'). Loop over `list(d)` to change it safely.""",
      raises=True),

    # ── Mutable defaults and when they are evaluated ───────────────────────
    q("mutable-default", '''
        def add(item, bag=[]):
            bag.append(item)
            return bag

        add(1)
        print(add(2))
    ''', "[1, 2]", ["[2]", "[1]", "[2, 2]"],
      "A mutable default argument is shared between calls",
      """The default list is created once, when `def` runs, not on each call. Both calls append to that
      same list, so the second call sees the 1 from the first."""),

    q("default-eval-time", '''
        x = 1

        def show(v=x):
            return v

        x = 2
        print(show())
    ''', "1", ["2", "None", "NameError"],
      "Defaults are evaluated when the function is defined",
      """`v=x` captured the value of `x` at the moment of `def`, which was 1. Changing `x` afterwards
      does not change the default."""),

    q("default-set", '''
        def f(n, seen=set()):
            seen.add(n)
            return len(seen)

        f(1)
        f(2)
        print(f(1))
    ''', "2", ["1", "3", "0"],
      "A shared default set remembers earlier calls",
      """The same set is reused every time, so it holds {1, 2} by the third call. Adding 1 again changes
      nothing, and the length is 2, not 1."""),

    q("default-none-idiom", '''
        def add(item, bag=None):
            if bag is None:
                bag = []
            bag.append(item)
            return bag

        add(1)
        print(add(2))
    ''', "[2]", ["[1, 2]", "[1]", "None"],
      "The fix for the shared default: a fresh list per call",
      """Using None as the default and building the list inside means every call gets its own list. The
      second call knows nothing about the first, so it returns just [2]."""),

    # ── Closures, scope and shadowing ──────────────────────────────────────
    q("late-binding", '''
        funcs = [lambda: i for i in range(3)]
        print([f() for f in funcs])
    ''', "[2, 2, 2]", ["[0, 1, 2]", "[3, 3, 3]", "[0, 0, 0]"],
      "Closures look the variable up late, not when they are made",
      """All three lambdas share the one `i` of the comprehension. By the time they are called the loop
      has finished and `i` is 2, so each returns 2."""),

    q("late-binding-fix", '''
        funcs = [lambda i=i: i for i in range(3)]
        print([f() for f in funcs])
    ''', "[0, 1, 2]", ["[2, 2, 2]", "[1, 2, 3]", "[0, 0, 0]"],
      "A default argument freezes the value at definition",
      """`i=i` copies the current value into a default when each lambda is created, and defaults are
      fixed at that moment. Each lambda keeps its own 0, 1 or 2."""),

    q("unbound-local", '''
        def counter():
            n = 0

            def inc():
                n += 1
                return n

            return inc

        c = counter()
        print(c())
    ''', "UnboundLocalError", ["1", "0", "None"],
      "Assigning to a name makes it local for the whole function",
      """`n += 1` assigns to `n`, so Python treats `n` as a local of `inc`, and reading it before it has
      a value fails. Declaring `nonlocal n` first is what makes it update the outer one.""",
      raises=True),

    q("shadow-global", '''
        x = 5

        def f():
            x = 10

        f()
        print(x)
    ''', "5", ["10", "None", "NameError"],
      "Assigning inside a function creates a local",
      """Without a `global x` line, `x = 10` makes a new local variable. The module-level `x` is
      never touched."""),

    q("global-late-lookup", '''
        x = 3

        def f():
            return x

        x = 4
        print(f())
    ''', "4", ["3", "None", "NameError"],
      "A global is looked up when the function runs",
      """The function does not remember `x` from when it was defined (that is only true of default
      arguments). It reads the global at call time, by which point it is 4."""),

    q("class-attr-shadow", '''
        class A:
            x = 1

        a = A()
        b = A()
        a.x += 1
        print(A.x, b.x)
    ''', "1 1", ["2 2", "2 1", "1 2"],
      "An instance attribute shadows the class attribute",
      """`a.x += 1` reads the class value 1, adds one, and stores 2 as a new attribute on the instance
      `a` alone. The class and the other instance still say 1."""),

    q("class-list-shared", '''
        class Bag:
            items = []

        a = Bag()
        b = Bag()
        a.items.append(1)
        print(len(b.items))
    ''', "1", ["0", "2", "None"],
      "A list on the class is shared by every instance",
      """`items = []` runs once, in the class body. Every instance sees that one list, so appending
      through `a` also shows up in `b`. Create it in `__init__` for a list per instance."""),

    # ── Aliasing and copying ───────────────────────────────────────────────
    q("alias-list", '''
        a = [1, 2, 3]
        b = a
        b.append(4)
        print(a)
    ''', "[1, 2, 3, 4]", ["[1, 2, 3]", "[4]", "[1, 2, 3, 4, 4]"],
      "Assignment never copies",
      """`b = a` makes a second name for the same list. Changing it through either name changes the
      one list."""),

    q("multiply-nested", '''
        a = [[0] * 2] * 2
        a[0][0] = 1
        print(a)
    ''', "[[1, 0], [1, 0]]", ["[[1, 0], [0, 0]]", "[[1, 1], [1, 1]]", "[[0, 0], [0, 0]]"],
      "Multiplying a list repeats the same inner list",
      """`[row] * 2` does not copy the row, it puts the same row in twice. Changing the first row
      changes the second, because they are one list. Use a comprehension for independent rows."""),

    q("shallow-copy", '''
        a = [[1], [2]]
        b = a.copy()
        b[0].append(9)
        print(a)
    ''', "[[1, 9], [2]]", ["[[1], [2]]", "[[1, 9], [2, 9]]", "[[1], [2], [9]]"],
      "A shallow copy still shares what is inside",
      """`copy()` makes a new outer list, but the inner lists are the same objects in both. Appending to
      an inner list shows through `a`. `copy.deepcopy` copies the inside too."""),

    q("chained-assign-list", '''
        x = y = []
        x += [1]
        print(y)
    ''', "[1]", ["[]", "[1, 1]", "None"],
      "+= on a list mutates, so every alias sees it",
      """`x = y = []` gives both names one list. `x += [1]` extends that list in place, so `y`
      sees the 1 as well."""),

    q("chained-assign-tuple", '''
        x = y = ()
        x += (1,)
        print(y)
    ''', "()", ["(1,)", "[1]", "None"],
      "+= on a tuple makes a new tuple",
      """Tuples cannot be changed, so `x += (1,)` builds a new tuple and rebinds `x`. `y` still points at
      the old empty one. Same `+=` as with lists, a different result."""),

    q("plus-vs-plus-equals", '''
        a = [1, 2]
        b = a
        a = a + [3]
        print(b)
    ''', "[1, 2]", ["[1, 2, 3]", "[3]", "[1, 2, 3, 3]"],
      "a + [x] builds a new list; += would not",
      """`a + [3]` creates a new list and `a` is rebound to it, while `b` keeps the old one. If you had
      written `a += [3]` the old list itself would have grown and `b` would show it."""),

    # ── == vs is, small ints, strings ──────────────────────────────────────
    q("is-vs-eq-ints", '''
        a = int("257")
        b = int("257")
        print(a is b, a == b)
    ''', "False True", ["True True", "False False", "True False"],
      "== compares values, `is` compares identity",
      """Two separately made 257s are equal but are two different objects. Only the small ints from -5 to
      256 are shared by CPython, which is why `is` on numbers seems to work until it does not."""),

    q("small-int-cache", '''
        a = int("100")
        b = int("100")
        c = int("1000")
        d = int("1000")
        print(a is b, c is d)
    ''', "True False", ["True True", "False False", "False True"],
      "Small integers are cached (CPython), bigger ones are not",
      """CPython keeps one object for every int from -5 to 256, so the two 100s are the same object.
      The two 1000s were made separately and are not. Never use `is` to compare numbers."""),

    q("string-is", '''
        s = "hello"
        t = "".join(["hel", "lo"])
        print(s == t, s is t)
    ''', "True False", ["True True", "False False", "False True"],
      "Equal strings are not always the same object",
      """`join` builds a brand new string that happens to have the same characters. It is equal to `s`
      but is not the same object. Use `==` for text."""),

    q("none-vs-false", '''
        print(0 == False, "" == False, None == False)
    ''', "True False False", ["True True False", "True True True", "False False False"],
      "Falsy is not the same as equal to False",
      """`0 == False` is true because False is the number 0 underneath. An empty string and None are
      falsy, but neither is equal to False. Use `not x` for truthiness, not `x == False`."""),

    q("bool-is-int", '''
        print(isinstance(True, int), type(True) == int)
    ''', "True False", ["True True", "False False", "False True"],
      "bool is a subclass of int",
      """True is an int for `isinstance`, because bool inherits from it. But its exact type is bool, so
      `type(True) == int` is false."""),

    q("list-eq-tuple", '''
        print([1, 2, 3] == [1, 2, 3.0], (1, 2) == [1, 2])
    ''', "True False", ["True True", "False False", "False True"],
      "Equal numbers match; a tuple never equals a list",
      """3 == 3.0, so the lists match item by item. A tuple and a list are different types and never
      compare equal, even with the same contents."""),

    # ── Floats and numbers ─────────────────────────────────────────────────
    q("float-equality", '''
        print(0.1 + 0.2 == 0.3)
    ''', "False", ["True", "0.3", "0.30000000000000004"],
      "Floats are binary approximations",
      """0.1 and 0.2 cannot be stored exactly, and their sum is 0.30000000000000004, not 0.3, so the
      comparison is false. Compare floats with `math.isclose`."""),

    q("float-sum-repr", '''
        print(0.1 + 0.2)
    ''', "0.30000000000000004", ["0.3", "0.30000000000000001", "0.3000000000000001"],
      "Floats show their true shortest representation",
      """Python prints the shortest text that reads back as exactly the same float. The sum of 0.1 and
      0.2 is a slightly different float from 0.3, and its shortest form is 0.30000000000000004."""),

    q("float-times-three", '''
        print(0.1 * 3 == 0.3, abs(0.1 * 3 - 0.3) < 1e-9)
    ''', "False True", ["True True", "False False", "True False"],
      "Compare floats with a tolerance",
      """0.1 * 3 is 0.30000000000000004, so exact equality fails. The tolerance check is true because the
      difference is about 5e-17, far below 1e-9."""),

    q("float-truncate", '''
        print(int(0.29 * 100))
    ''', "28", ["29", "30", "28.99"],
      "int() truncates, and the float was a hair below 29",
      """0.29 * 100 is 28.999999999999996 in floating point, and int() cuts off the decimals instead of
      rounding, giving 28. Use round() when you want the nearest whole number."""),

    q("float-big-plus-one", '''
        print(1e16 + 1)
    ''', "1e+16", ["10000000000000001.0", "1.0000000000000001e+16", "10000000000000001"],
      "Large floats cannot hold small additions",
      """Floats have about 16 significant digits. At 1e16 the gap between neighbouring floats is 2, so
      adding 1 rounds straight back to 1e16, and Python prints it as 1e+16."""),

    q("round-bankers", '''
        print(round(2.5), round(3.5), round(0.5))
    ''', "2 4 0", ["3 4 1", "3 4 0", "2 4 1"],
      "round() rounds halves to the nearest even number",
      """Python 3 uses banker's rounding: exact halves go to the even neighbour, so 2.5 becomes 2,
      3.5 becomes 4 and 0.5 becomes 0. It is not the 'round half up' from school."""),

    q("floor-division", '''
        print(int(-3.7), -7 // 2, -7 % 3)
    ''', "-3 -4 2", ["-3 -3 -1", "-4 -3 -1", "-3 -4 -1"],
      "// floors toward minus infinity, and % follows it",
      """int() chops toward zero (-3), but `//` floors, so -7 // 2 is -4. The remainder of `%` takes the
      sign of the divisor, so -7 % 3 is 2, because -3 * 3 + 2 = -7."""),

    q("true-division", '''
        print(6 / 3, 2 ** 2, 2 ** -1)
    ''', "2.0 4 0.5", ["2 4 0", "2.0 4.0 0.5", "2 4 0.5"],
      "/ always gives a float; ** with ints gives an int",
      """In Python 3, `/` is true division and returns a float even when the result is whole: 2.0. `2 ** 2`
      stays an int, and only a negative exponent turns it into a float, 0.5."""),

    q("int-vs-true-div", '''
        print(7 / 2, 7 // 2)
    ''', "3.5 3", ["3 3", "3.5 3.5", "3 3.5"],
      "/ and // are different operators",
      """`/` is true division, giving 3.5. `//` is floor division, giving 3. Python 2 used `/` for both,
      which is where the old expectation comes from."""),

    q("max-strings", '''
        print(max("9", "10"), max(9, 10))
    ''', "9 10", ["10 10", "9 9", "10 9"],
      "Strings compare character by character",
      """As text, "9" is bigger than "10" because '9' comes after '1'. Compare as numbers and 10 wins.
      This is why you convert input() with int() before comparing."""),

    q("no-plus-plus", '''
        x = 5
        print(++x, --x)
    ''', "5 5", ["6 4", "6 5", "5 4"],
      "Python has no ++ or --",
      """`++x` is just a plus sign applied twice, `+(+x)`, and `--x` is a minus applied twice, so
      both give 5 and x never changes. Use `x += 1`."""),

    # ── Chained comparisons, truthiness, precedence ────────────────────────
    q("chained-compare", '''
        print(1 < 2 < 3, 3 > 2 > 2, 1 == 1.0 == True)
    ''', "True False True", ["True True True", "True False False", "False False True"],
      "a < b < c means a < b and b < c",
      """Comparisons chain. `3 > 2 > 2` is `3 > 2 and 2 > 2`, which fails on the second half. And
      `1 == 1.0 == True` is true because each neighbouring pair is equal."""),

    q("in-chain", '''
        print("x" in "xyz" == True)
    ''', "False", ["True", "None", "TypeError"],
      "`in` and `==` chain like any comparison",
      """This is `("x" in "xyz") and ("xyz" == True)`. The first half is true, but the string "xyz" is
      never equal to True, so the answer is False."""),

    q("tuple-string-compare", '''
        print((1, 2) < (1, 3), "apple" < "Banana", [1, 2] < [1, 2, 0])
    ''', "True False True", ["True True True", "False False True", "True False False"],
      "Sequences compare item by item, text by character code",
      """Tuples and lists compare left to right, and a shorter prefix is smaller. Text compares by
      character code, where every capital letter comes before every lowercase one, so "apple" > "Banana"."""),

    q("truthiness-table", '''
        print(bool([]), bool([[]]), bool("0"), bool(0.0))
    ''', "False True True False", ["False False True False", "False True False False",
                                    "False False False False"],
      "Empty containers are falsy; non-empty ones are truthy whatever they hold",
      """`[[]]` has one item (an empty list), so it is truthy. `"0"` is a non-empty string, so it is
      truthy as well, unlike the number 0 or 0.0."""),

    q("or-and-values", '''
        print(0 or "x", 0 and "x", [] or None, 1 and 2)
    ''', "x 0 None 2", ["x x None 2", "True 0 None True", "x 0 [] 2"],
      "and / or return one of their operands, not True or False",
      """`or` returns the first truthy operand (or the last one), `and` returns the first falsy operand
      (or the last one). So `0 or "x"` is "x", `0 and "x"` is 0, and `1 and 2` is 2."""),

    q("not-precedence", '''
        print(not 1 == 2, not True and False, True or False and False)
    ''', "True False True", ["False False True", "True True True", "True False False"],
      "not binds looser than ==, but tighter than and / or",
      """`not 1 == 2` is `not (1 == 2)`, so True. `not True and False` is `(not True) and False`, which
      is False. And `and` binds tighter than `or`, so the last one is True or (False and False)."""),

    q("power-precedence", '''
        print(-2 ** 2, (-2) ** 2, 2 ** 3 ** 2)
    ''', "-4 4 512", ["4 4 64", "-4 4 64", "4 4 512"],
      "** binds tighter than unary minus, and goes right to left",
      """`-2 ** 2` is `-(2 ** 2)`, so -4. `2 ** 3 ** 2` is `2 ** (3 ** 2)` = 2 ** 9 = 512, not
      (2 ** 3) ** 2."""),

    q("or-two", '''
        x = 5
        print(x == 1 or 2, x == 5 or 2)
    ''', "2 True", ["False True", "True True", "2 5"],
      "`x == 1 or 2` is not 'x is 1 or 2'",
      """It parses as `(x == 1) or 2`. With x = 5 the left side is False, so `or` hands back the 2,
      which is truthy, so `if x == 1 or 2:` is always true."""),

    q("ternary-precedence", '''
        print("a" if 0 else "b" + "c")
    ''', "bc", ["b", "a", "abc"],
      "The else branch of a conditional expression runs to the end",
      """The condition 0 is falsy, so the else part is used, and that part is everything after
      `else`: `"b" + "c"`. The result is "bc"."""),

    # ── Control flow ───────────────────────────────────────────────────────
    q("fizzbuzz-order", '''
        n = 15
        if n % 3 == 0:
            print("Fizz")
        elif n % 5 == 0:
            print("Buzz")
        elif n % 15 == 0:
            print("FizzBuzz")
        else:
            print(n)
    ''', "Fizz", ["FizzBuzz", "Buzz", "15"],
      "An unreachable branch: the order of the elifs matters",
      """15 is divisible by 3, so the first test already matches and the rest are skipped. The
      FizzBuzz test must come first, or it can never run."""),

    q("if-vs-elif", '''
        x = 7
        if x > 5:
            print("big", end=" ")
        if x > 3:
            print("medium", end=" ")
        else:
            print("small", end=" ")
    ''', "big medium", ["big", "medium", "big small"],
      "Separate ifs all run; an elif chain stops at the first match",
      """These are two independent `if` statements, not one chain. Both tests are true for 7, so both
      messages print, and the else belongs only to the second `if`."""),

    q("for-else", '''
        for n in range(2, 6):
            if n == 7:
                break
        else:
            n = -1
        print(n)
    ''', "-1", ["5", "6", "2"],
      "A loop's else runs when the loop did NOT break",
      """No number in 2..5 equals 7, so the loop never hits `break`, and then the `else` block runs.
      It sets n to -1."""),

    q("try-else-finally", '''
        try:
            print("a", end="")
            raise ValueError
        except ValueError:
            print("b", end="")
        else:
            print("c", end="")
        finally:
            print("d", end="")
    ''', "abd", ["abcd", "ad", "abc"],
      "try/else only runs when nothing was raised",
      """The error is caught, so `except` runs and `else` is skipped. `finally` always runs last. That
      gives a, b, d."""),

    q("return-finally", '''
        def f():
            try:
                return "try"
            finally:
                return "finally"

        print(f())
    ''', "finally", ["try", "None", "tryfinally"],
      "A return in finally overrides the return in try",
      """`finally` always runs before the function really returns, and its own `return` replaces the
      pending one. The "try" value is thrown away."""),

    q("finally-after-return", '''
        def f():
            x = 1
            try:
                return x
            finally:
                x = 2

        print(f())
    ''', "1", ["2", "None", "3"],
      "The return value is fixed before finally runs",
      """`return x` evaluates `x` (1) first, then `finally` runs and rebinds the local `x`, but the
      value being returned is already decided."""),

    q("walrus-leak", '''
        nums = [n for x in range(3) if (n := x * 2) > 0]
        print(nums, n)
    ''', "[2, 4] 4", ["[2, 4] 2", "[0, 2, 4] 4", "[2, 4] 0"],
      "A walrus inside a comprehension binds in the enclosing scope",
      """Unlike the loop variable `x`, the name set by `:=` is not hidden inside the comprehension. It
      ends up as a normal variable of the surrounding code, holding the last value it was given: 4."""),

    q("tuple-swap", '''
        a, b = 3, 4
        a, b = b, a + b
        print(a, b)
    ''', "4 7", ["4 8", "7 4", "3 7"],
      "The whole right side is evaluated before any assignment",
      """`b, a + b` is worked out first as (4, 7) using the old values, and only then assigned. Doing it
      one at a time would give 4 8."""),

    q("assign-order", '''
        x = [1, 2, 3]
        i = 0
        i, x[i] = 1, 9
        print(x)
    ''', "[1, 9, 3]", ["[9, 2, 3]", "[1, 2, 9]", "[1, 2, 3]"],
      "Targets are assigned left to right",
      """`i` is assigned 1 first, and only then is `x[i]` worked out, using the new i. So the 9 goes to
      index 1, not index 0."""),

    # ── Generators and laziness ────────────────────────────────────────────
    q("generator-exhausted", '''
        gen = (x * 2 for x in range(3))
        print(list(gen), list(gen))
    ''', "[0, 2, 4] []", ["[0, 2, 4] [0, 2, 4]", "[] []", "[0, 2, 4] [0, 2]"],
      "A generator can only be used once",
      """The first `list(gen)` uses it all up. The second finds nothing left and gives an empty list.
      Make a list first if you need to loop twice."""),

    q("generator-late-name", '''
        n = 2
        gen = (i * n for i in range(3))
        n = 10
        print(list(gen))
    ''', "[0, 10, 20]", ["[0, 2, 4]", "[0, 20, 40]", "[10, 20, 30]"],
      "A generator expression reads its free variables late",
      """Only the outermost `range(3)` is evaluated straight away. The `n` in `i * n` is looked up when
      each value is produced, by which time n is 10."""),

    q("map-lazy", '''
        nums = [1, 2, 3]
        squares = map(lambda n: n * n, nums)
        nums.append(4)
        print(list(squares))
    ''', "[1, 4, 9, 16]", ["[1, 4, 9]", "[1, 2, 3, 4]", "[1, 4, 9, 4]"],
      "map is lazy and sees later changes to its input",
      """`map` does no work until you consume it, and it walks the original list, which by then has a
      fourth item. So 4 is squared as well."""),

    q("any-all-empty", '''
        print(any([]), all([]))
    ''', "False True", ["False False", "True True", "True False"],
      "all() of nothing is True",
      """`any` asks 'is there at least one true item?', which is false for an empty list. `all` asks
      'is there no false item?', which is vacuously true."""),

    q("zip-shortest", '''
        print(list(zip("abc", [1, 2])))
    ''', "[('a', 1), ('b', 2)]", ["[('a', 1), ('b', 2), ('c', None)]", "[('a', 1), ('b', 2), 'c']",
                                  "IndexError"],
      "zip stops at the shortest input",
      """`zip` quietly drops the leftover items instead of padding or failing. Use
      `itertools.zip_longest` if you want the padding."""),

    # ── Sorting, ordering, containers ──────────────────────────────────────
    q("sort-returns-none", '''
        nums = [3, 1, 2]
        print(nums.sort())
    ''', "None", ["[1, 2, 3]", "[3, 1, 2]", "0"],
      "list.sort() sorts in place and returns None",
      """`sort` changes the list itself and returns None as a signal that it did. Use `sorted(nums)` if
      you want a new sorted list back."""),

    q("reverse-order-of-eval", '''
        words = ["b", "a"]
        print(words.reverse(), words)
    ''', "None ['a', 'b']", ["['a', 'b'] ['b', 'a']", "None ['b', 'a']", "['a', 'b'] ['a', 'b']"],
      "reverse() changes the list and returns None; arguments run left to right",
      """`words.reverse()` runs first, reversing the list in place and returning None. Then `words` is
      read, already reversed. So you get None and ['a', 'b']."""),

    q("sort-key-str", '''
        print(sorted([10, 9, 100], key=str))
    ''', "[10, 100, 9]", ["[9, 10, 100]", "[100, 10, 9]", "[10, 9, 100]"],
      "Sorting numbers as text puts '10' before '9'",
      """With `key=str` the numbers are compared as strings: "10" < "100" < "9", because comparison goes
      character by character and '1' comes before '9'."""),

    q("dict-order", '''
        d = {}
        d["c"] = 1
        d["a"] = 2
        d["b"] = 3
        print(list(d))
    ''', "['c', 'a', 'b']", ["['a', 'b', 'c']", "['b', 'a', 'c']", "['c', 'b', 'a']"],
      "Dicts keep insertion order",
      """Since Python 3.7 a dict remembers the order its keys were first added. It is not sorted and it
      does not depend on the keys' hashes."""),

    q("dict-duplicate-keys", '''
        d = {"a": 1, "b": 2, "a": 3}
        print(d)
    ''', "{'a': 3, 'b': 2}", ["{'a': 1, 'b': 2}", "{'b': 2, 'a': 3}", "{'a': 1, 'a': 3, 'b': 2}"],
      "The last value wins, but the key keeps its first position",
      """A dict cannot hold the same key twice. The later value 3 replaces the 1, and the key stays where
      it first appeared, so 'a' is still first."""),

    q("dict-true-one", '''
        print({1: "a", True: "b", 1.0: "c"})
    ''', "{1: 'c'}", ["{1: 'a', True: 'b', 1.0: 'c'}", "{1: 'a'}", "{1: 'b'}"],
      "1, 1.0 and True are the same dict key",
      """They are equal and have the same hash, so they count as one key. The key stays as the first
      one written, 1, and the value is the last one assigned."""),

    q("empty-braces", '''
        print(type({}).__name__, type({1}).__name__)
    ''', "dict set", ["set set", "dict dict", "set dict"],
      "{} is an empty dict, not an empty set",
      """Curly braces with nothing in them make a dict. To get an empty set you have to write `set()`."""),

    q("one-tuple", '''
        print(type((1)).__name__, type((1,)).__name__)
    ''', "int tuple", ["tuple tuple", "int int", "tuple int"],
      "A tuple is made by the comma, not the brackets",
      """`(1)` is just 1 in brackets, an int. The trailing comma in `(1,)` is what makes a one-item
      tuple."""),

    q("missing-comma", '''
        x = ["a", "b" "c"]
        print(len(x))
    ''', "2", ["3", "1", "Error"],
      "Neighbouring string literals join into one",
      """Without the comma, `"b" "c"` is read as the single string "bc". The list has two items: "a"
      and "bc". A classic bug in long lists of strings."""),

    # ── Slices, ranges, indexes ────────────────────────────────────────────
    q("slice-bounds", '''
        s = [0, 1, 2, 3, 4]
        print(s[1:100], s[100:])
    ''', "[1, 2, 3, 4] []", ["IndexError", "[1, 2, 3, 4] [4]", "[0, 1, 2, 3, 4] []"],
      "Slices never raise for out-of-range bounds",
      """A slice quietly clips its bounds to the list. `s[1:100]` stops at the end and `s[100:]` is
      empty. Only a single index such as `s[100]` raises IndexError."""),

    q("slice-text", '''
        print("python"[1:4], "python"[-3:], "python"[::-2])
    ''', "yth hon nhy", ["pyt tho nyh", "yth hon yp", "yt ho nh"],
      "Slice ends are exclusive; a negative step walks backwards",
      """`[1:4]` takes indexes 1, 2, 3 and stops before 4. `[-3:]` is the last three letters. `[::-2]`
      starts at the end and takes every second letter backwards: n, h, y."""),

    q("range-direction", '''
        print(list(range(5, 0)), list(range(5, 0, -1)))
    ''', "[] [5, 4, 3, 2, 1]", ["[5, 4, 3, 2, 1] [5, 4, 3, 2, 1]", "[] [5, 4, 3, 2, 1, 0]",
                                "[5, 4, 3, 2, 1] []"],
      "range counts up unless you give a negative step, and excludes the stop",
      """`range(5, 0)` has step +1, so it is already past the stop and gives nothing. With step -1 it
      counts down 5 to 1: the stop value 0 is never included."""),

    q("range-len", '''
        print(len(range(1, 10, 3)), list(range(1, 10, 3))[-1])
    ''', "3 7", ["3 10", "4 10", "4 7"],
      "The stop of a range is never reached",
      """The values are 1, 4, 7. The next would be 10, which is not below 10, so there are three
      values and the last is 7."""),

    q("slice-assign", '''
        x = [1, 2, 3, 4, 5]
        x[1:3] = [9]
        print(x)
    ''', "[1, 9, 4, 5]", ["[1, 9, 9, 4, 5]", "[1, 9, 3, 4, 5]", "[9, 3, 4, 5]"],
      "Assigning to a slice replaces it, whatever its length",
      """`x[1:3]` is the two items 2 and 3. Assigning a one-item list replaces both with that one item,
      so the list gets shorter."""),

    q("negative-zero-index", '''
        a = [1, 2, 3]
        print(a[-0], a[-1], a[len(a) - 3])
    ''', "1 3 1", ["3 3 1", "1 3 3", "1 1 1"],
      "-0 is just 0",
      """Negative indexes count from the end starting at -1, because -0 is the same number as 0. So
      `a[-0]` is the first item, not the last."""),

    q("find-zero", '''
        print("found" if "abc".find("a") else "missing")
    ''', "missing", ["found", "True", "None"],
      "find() returns an index, and index 0 is falsy",
      """"a" is at position 0, and 0 is falsy, so the condition fails and "missing" is printed. Test
      `!= -1` or use `in`."""),

    q("rstrip-set", '''
        print("happy.py".rstrip(".py"))
    ''', "ha", ["happy", "happ", "hap"],
      "strip() takes a set of characters, not a suffix",
      """`rstrip(".py")` removes any run of the characters '.', 'p' and 'y' from the end. It eats the
      '.py', then the 'y' and both 'p's, and stops at 'a'. Use `removesuffix` for a real suffix."""),

    q("split-space", '''
        print("a  b".split(" "), "a  b".split())
    ''', "['a', '', 'b'] ['a', 'b']", ["['a', 'b'] ['a', 'b']", "['a', '', 'b'] ['a', '', 'b']",
                                      "['a', 'b'] ['a', '', 'b']"],
      "split(' ') and split() are different",
      """Splitting on one explicit space leaves an empty string where two spaces met. With no argument,
      split treats any run of whitespace as one separator."""),

    q("string-times", '''
        print("5" + "5", "5" * 3)
    ''', "55 555", ["10 15", "10 555", "55 15"],
      "+ and * on strings join and repeat",
      """With strings, `+` joins and `*` repeats. Nothing is converted to numbers, so you get "55" and
      "555"."""),
)
