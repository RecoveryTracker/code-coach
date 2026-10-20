"""Gotchas, Python, the third helping: a wider mix, with a lot of easy-looking cards.

Same rules as content_py.py: every answer is held to a real run by tests/test_gotchas_content.py, the
wrong options are real misreads, nothing depends on randomness, the clock or identity, and each program
prints one line (or, with raises=True, dies with the named error having printed nothing). Roughly a third
of these look easy on purpose (a beginner can get them right, but there is a real tempting wrong answer),
the rest are the usual middle and hard traps. They come after the earlier modules in the deck.
"""

from __future__ import annotations

from .items import Item, make

q = make("python")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: types, lengths, indexes, slices ──────────────────────
    q("type-of-arithmetic", '''
        print(type(3 / 1), type(3 // 1), type(3 * 1.0))
    ''', "<class 'float'> <class 'int'> <class 'float'>",
      ["<class 'int'> <class 'int'> <class 'int'>", "<class 'float'> <class 'float'> <class 'float'>",
       "<class 'int'> <class 'int'> <class 'float'>"],
      "/ always gives a float, // keeps ints as ints",
      """Division with `/` returns a float even when it divides evenly, so `3 / 1` is `3.0`. Floor division
      `//` of two ints stays an int, and multiplying by a float gives a float."""),

    q("index-len-past-end", '''
        word = "hello"
        print(word[len(word)])
    ''', "IndexError", ["o", "h", "None"],
      "len() is one past the last index",
      """`hello` has 5 letters, so the valid indexes are 0 to 4. `word[5]` is off the end and raises
      IndexError instead of giving the last letter. The last letter is `word[len(word) - 1]` or `word[-1]`.""",
      raises=True),

    q("negative-index-string", '''
        s = "python"
        print(s[-1], s[-6], s[-len(s)])
    ''', "n p p", ["n y p", "n p y", "p n n"],
      "Negative indexes count from the end, and -len is the first item",
      """`s[-1]` is the last letter, `n`. `s[-6]` is six from the end, which is the very first letter, `p`,
      and `-len(s)` is the same spot. Negative indexes start at -1, not -0."""),

    q("list-times-precedence", '''
        print([1, 2] + [3] * 2)
    ''', "[1, 2, 3, 3]", ["[1, 2, 3, 1, 2, 3]", "[4, 5]", "[1, 2, 6]"],
      "* binds tighter than + even for lists",
      """The multiplication happens first: `[3] * 2` is `[3, 3]`. Then `+` glues the lists together to
      give `[1, 2, 3, 3]`. Nothing is added item by item, and the parentheses you imagined are not there."""),

    q("range-end-sum", '''
        total = 0
        for i in range(1, 5):
            total += i
        print(total)
    ''', "10", ["15", "6", "5"],
      "range stops before its end value",
      """`range(1, 5)` gives 1, 2, 3, 4 and never reaches 5. The sum is 10. To include 5 you would write
      `range(1, 6)`."""),

    q("for-else-reset", '''
        result = "none"
        for n in [2, 4, 5, 6]:
            if n % 2:
                result = "odd found"
                break
        else:
            result = "all even"
        print(result)
    ''', "odd found", ["all even", "none", "odd found all even"],
      "A loop's else only runs when there was no break",
      """The loop meets 5, which is odd, so it sets `result` and breaks. A `break` skips the `else`
      block completely, so "all even" is never assigned."""),

    q("len-of-things", '''
        print(len("a b"), len([[1, 2], [3]]), len({1, 1, 2}), len(str(100)))
    ''', "3 2 2 3", ["2 2 2 3", "3 3 3 3", "3 2 3 1"],
      "len counts items, spaces count, and nested lists count once",
      """The space is a character, so `"a b"` has 3. The outer list holds two lists, so its length is 2,
      not 3. A set drops the repeated 1, leaving 2 items, and `str(100)` is the three characters "100"."""),

    q("str-plus-int", '''
        print("Age: " + 30)
    ''', "TypeError", ["Age: 30", "Age:30", "None"],
      "Python will not join a string and an int with +",
      """Unlike some languages, Python does not turn the number into text for you, so `+` between a
      str and an int raises TypeError. Use `str(30)` or an f-string such as `f"Age: {30}"`.""",
      raises=True),

    q("slice-inclusive-end", '''
        nums = [10, 20, 30, 40, 50]
        print(nums[1:3], nums[:2], nums[-2:])
    ''', "[20, 30] [10, 20] [40, 50]",
      ["[20, 30, 40] [10, 20, 30] [40, 50]", "[20, 30] [10, 20] [30, 40]", "[20, 30] [10] [40, 50]"],
      "A slice includes its start and excludes its end",
      """`nums[1:3]` takes indexes 1 and 2, not 3. `nums[:2]` takes the first two items, and `nums[-2:]`
      takes the last two. The end index is always left out."""),

    q("method-chain", '''
        s = "  Hello World  "
        print(s.strip().lower().replace("o", "0"))
    ''', "hell0 w0rld", ["hello world", "Hell0 W0rld", "hell0 world"],
      "Each string method returns a new string, and they chain left to right",
      """`strip()` removes the outer spaces, `lower()` makes everything lowercase, and only then does
      `replace` turn every `o` into a zero. The capital `H` and `W` are already lowercase by that point."""),

    q("split-index-string", '''
        print("2024-01-15".split("-")[1])
    ''', "01", ["1", "2024", "01-15"],
      "split gives strings, so the leading zero stays",
      """`split("-")` gives `["2024", "01", "15"]`, all strings. Item 1 is the text `01`, and print shows it
      with its zero because it was never turned into a number."""),

    q("bool-string-false", '''
        print(bool("False"), bool(""), bool(" "))
    ''', "True False True", ["False False True", "True False False", "False False False"],
      "Any non-empty string is true, whatever it says",
      """Truthiness depends on being empty, not on the meaning of the text. `"False"` is a string with
      letters in it, and even a single space is non-empty, so both are true. Only `""` is false."""),

    q("dict-get-missing", '''
        d = {"a": 1}
        print(d.get("b"), d.get("b", 0), d.get("a", 0))
    ''', "None 0 1", ["0 0 1", "None 0 0", "None None 1"],
      "get returns None when no default is given, and ignores the default when the key exists",
      """`d.get("b")` finds nothing and gives `None`. With a second argument it gives that instead. For
      the key that exists, the real value `1` wins and the default is never used."""),

    q("dict-key-error", '''
        d = {"a": 1}
        print(d["b"])
    ''', "KeyError", ["None", "0", "b"],
      "Square brackets on a missing key raise, they do not return None",
      """`d["b"]` has no fallback, so a missing key raises KeyError. Only `.get()` quietly returns
      `None`.""",
      raises=True),

    q("set-case-sensitive", '''
        names = ["bob", "Bob", "bob"]
        print(len(set(names)))
    ''', "2", ["1", "3", "0"],
      "A set removes exact duplicates only",
      """`"bob"` and `"Bob"` are different strings, so both stay. Only the second plain `"bob"` is a
      repeat, which leaves 2 items."""),

    q("fstring-expressions", '''
        print(f"{'a' * 3} {2 * 3} {'2' * 3}")
    ''', "aaa 6 222", ["aaa 6 6", "a3 6 222", "aaa 23 222"],
      "An f-string braces hold real expressions",
      """Each pair of braces is evaluated like normal code. `'a' * 3` repeats the text, `2 * 3` is
      arithmetic, and `'2' * 3` repeats the text `2` three times to give `222`."""),

    q("modulo-small-left", '''
        print(10 % 3, 10 % 5, 3 % 10)
    ''', "1 0 3", ["3 2 0", "1 0 0", "1 2 3"],
      "A smaller number modulo a bigger one is itself",
      """`10 % 3` leaves 1, and `10 % 5` divides exactly so it leaves 0. For `3 % 10`, 10 goes into 3
      zero times, so the whole 3 is left over."""),

    q("string-compare-length", '''
        print("a" < "ab", "abc" < "abd", "b" < "ab")
    ''', "True True False", ["False True True", "True False False", "True True True"],
      "Strings compare letter by letter, and a prefix comes first",
      """`"a"` is a prefix of `"ab"`, so it sorts earlier. `"abc"` and `"abd"` first differ at `c` against
      `d`. In `"b" < "ab"` the first letters already decide it, and `b` comes after `a`."""),

    q("return-ends-function", '''
        def double(x):
            return x * 2
            print("done")

        print(double("ab"))
    ''', "abab", ["done", "ab2", "None"],
      "Code after return never runs",
      """`return` leaves the function immediately, so the `print("done")` line is dead code. Multiplying
      a string by 2 repeats it, giving `abab`."""),

    q("default-arg-keyword", '''
        def greet(name="friend", punct="!"):
            return "Hi " + name + punct

        print(greet("Sam"), greet(punct="?"))
    ''', "Hi Sam! Hi friend?", ["Hi Sam! Hi friend!", "Hi Sam? Hi friend?", "Hi Sam! Hi ?"],
      "Defaults fill in only what you did not pass",
      """The first call passes `name` by position and leaves `punct` at its `!`. The second call passes
      only `punct` by keyword, so `name` keeps its default of `friend`."""),

    q("factorial-base", '''
        def f(n):
            return 1 if n <= 1 else n * f(n - 1)

        print(f(5), f(0))
    ''', "120 1", ["120 0", "24 1", "720 1"],
      "The base case returns 1, so zero factorial is 1",
      """`f(5)` is 5 * 4 * 3 * 2 * 1 = 120. `f(0)` hits the `n <= 1` case straight away and returns 1,
      which is also the mathematically correct 0!."""),

    q("fib-call-count", '''
        calls = 0

        def fib(n):
            global calls
            calls += 1
            if n < 2:
                return n
            return fib(n - 1) + fib(n - 2)

        print(fib(4), calls)
    ''', "3 9", ["3 4", "3 5", "4 9"],
      "Naive recursion calls itself far more often than n",
      """`fib(4)` is 3, but it takes 9 calls: fib(4) calls fib(3) and fib(2), and those keep branching
      until fib(1) and fib(0). The count grows roughly like the Fibonacci numbers themselves."""),

    q("enumerate-index-first", '''
        names = ["a", "b"]
        print([f"{i}{n}" for i, n in enumerate(names, 1)])
    ''', "['1a', '2b']", ["['0a', '1b']", "['a1', 'b2']", "['1', '2']"],
      "enumerate gives (index, item), and the second argument sets where it starts",
      """`enumerate(names, 1)` numbers from 1, and each pair is the index first, then the item. So the
      strings are `1a` and `2b`, not `a1`."""),

    q("sorted-vs-reversed", '''
        nums = [3, 1, 2]
        print(sorted(nums), nums, list(reversed(nums)))
    ''', "[1, 2, 3] [3, 1, 2] [2, 1, 3]",
      ["[1, 2, 3] [1, 2, 3] [3, 2, 1]", "[1, 2, 3] [3, 1, 2] [3, 2, 1]", "[1, 2, 3] [1, 2, 3] [2, 1, 3]"],
      "sorted returns a new list, and reversed flips the original order",
      """`sorted(nums)` leaves `nums` as it was. `reversed(nums)` walks the original list backwards, which
      gives `[2, 1, 3]`, not the sorted list backwards."""),

    q("min-max-sum-start", '''
        print(min("b", "a", "C"), max([3, 10, 2]), sum([1, 2, 3], 10))
    ''', "C 10 16", ["a 10 6", "a 10 16", "C 10 6"],
      "Capitals sort before lowercase, and sum can start from a number",
      """In character codes `C` (67) is lower than `a` (97), so `min` picks `C`. `sum` with a second
      argument starts its total there: 10 + 1 + 2 + 3 is 16."""),

    q("round-abs-pow", '''
        print(round(2.567, 1), abs(-2.5), pow(2, 3), 2 ** -1)
    ''', "2.6 2.5 8 0.5", ["2.5 2.5 8 0.5", "2.6 2.5 6 0.5", "2.6 2.5 8 -2"],
      "round rounds, it does not cut; a negative power is a fraction",
      """`round(2.567, 1)` rounds to 2.6 rather than chopping to 2.5. `pow(2, 3)` is 2 cubed, 8, and
      `2 ** -1` is one over 2, so 0.5."""),

    q("count-replace-index", '''
        w = "Mississippi"
        print(w.count("ss"), w.replace("ss", "").upper(), w.index("i"))
    ''', "2 MIIIPPI 1", ["4 MIIIPPI 1", "2 MIIIPPI 0", "2 MIISSPPI 1"],
      "count counts separate pieces; index starts at 0 and finds the first one",
      """The text `ss` appears twice. Removing both gives `Miiippi`, which upper-cases to `MIIIPPI`.
      The first `i` sits at index 1, right after the `M`."""),

    q("in-operator-basic", '''
        print(2 in [1, 2, 3], "2" in [1, 2, 3], 2 in {2: "x"}, "x" in {2: "x"})
    ''', "True False True False",
      ["True False True True", "True True True False", "True False False False"],
      "in checks the items of a list but the keys of a dict",
      """`"2"` is a string and the list holds ints, so it is not found. For a dict `in` looks at the keys
      only: 2 is a key, `"x"` is a value."""),

    q("tuple-item-assign", '''
        t = (1, 2, 3)
        t[0] = 9
        print(t)
    ''', "TypeError", ["(9, 2, 3)", "(1, 2, 3)", "9"],
      "Tuples cannot be changed in place",
      """A tuple is immutable, so item assignment fails with TypeError before print is reached. A list
      with the same items would have accepted it.""",
      raises=True),

    q("while-halving", '''
        n = 10
        steps = 0
        while n > 1:
            n //= 2
            steps += 1
        print(steps, n)
    ''', "3 1", ["4 0", "3 0", "4 1"],
      "Floor division by two stops at 1, not 0",
      """n goes 10, 5, 2, 1, and the loop stops because 1 is not greater than 1. That took 3 passes,
      and `n` ends at 1."""),

    q("continue-then-break", '''
        out = []
        for i in range(6):
            if i % 2 == 0:
                continue
            if i == 5:
                break
            out.append(i)
        print(out)
    ''', "[1, 3]", ["[1, 3, 5]", "[0, 2, 4]", "[1]"],
      "continue skips the rest of one pass; break ends the loop",
      """The even numbers are skipped by `continue`. 1 and 3 are appended, and when `i` is 5 the loop
      breaks before it can append, so 5 never makes it in."""),

    q("bool-expression-mix", '''
        x = 5
        print(x > 3 and x < 10, x > 3 and x > 10 or x == 5, not x > 3)
    ''', "True True False", ["True False False", "True True True", "False True False"],
      "and binds tighter than or, and not applies after the comparison",
      """The second test is `(x > 3 and x > 10) or (x == 5)`: the first part is false but the second part
      is true. `not x > 3` is `not (x > 3)`, which is false."""),

    # ── Lists, dicts and sets: the middle of the road ─────────────────────
    q("sort-copy-alias", '''
        a = [3, 1, 2]
        b = sorted(a)
        c = a
        c.sort()
        print(a, b is a, c is a)
    ''', "[1, 2, 3] False True",
      ["[3, 1, 2] False True", "[1, 2, 3] True True", "[1, 2, 3] False False"],
      "sorted makes a new list; .sort() on an alias changes the original",
      """`sorted(a)` builds a separate list, so `b is a` is False. But `c = a` only adds a second name for
      the same list, and `c.sort()` sorts that one list in place, so `a` is sorted too."""),

    q("dict-pop-default", '''
        d = {"a": 1, "b": 2}
        print(d.pop("a"), d.pop("z", "none"), d)
    ''', "1 none {'b': 2}",
      ["1 none {'a': 1, 'b': 2}", "a none {'b': 2}", "1 z {'b': 2}"],
      "pop returns the value and removes the key",
      """`d.pop("a")` hands back the value 1 and deletes the key, so `d` really shrinks. A key that is
      missing returns the default you gave instead of raising KeyError."""),

    q("comprehension-if-else", '''
        print([x if x % 2 else 0 for x in range(5)], [x for x in range(5) if x % 2])
    ''', "[0, 1, 0, 3, 0] [1, 3]",
      ["[1, 3] [1, 3]", "[0, 1, 0, 3, 0] [0, 1, 0, 3, 0]", "[0, 1, 2, 3, 4] [1, 3]"],
      "if-else before the for keeps every item; a trailing if filters",
      """With `x if cond else 0` in front, every item produces something, so the list has 5 entries. An
      `if` at the end drops the items that fail, leaving only 1 and 3."""),

    q("find-minus-one", '''
        s = "hello"
        print(s.find("z"), s[s.find("z")], s.find("l"), s.rfind("l"))
    ''', "-1 o 2 3", ["-1 None 2 3", "-1 h 2 3", "-1 o 2 2"],
      "find returns -1, and -1 is a valid index",
      """A missing substring gives -1 rather than an error, and `s[-1]` is the last letter, `o`. `find`
      returns the first match (2), `rfind` the last (3)."""),

    q("nested-comprehension-order", '''
        print([(i, j) for i in range(2) for j in range(i + 1)])
    ''', "[(0, 0), (1, 0), (1, 1)]",
      ["[(0, 0), (0, 1), (1, 0), (1, 1)]", "[(0, 0), (0, 1), (1, 1)]", "[(0, 0), (1, 1)]"],
      "Comprehension loops nest in the order you read them",
      """The first `for` is the outer loop. When `i` is 0, `range(1)` gives just 0, and when `i` is 1,
      `range(2)` gives 0 and 1. That makes three pairs, not four."""),

    q("sort-key-tuple", '''
        words = ["bb", "a", "ccc", "dd"]
        print(sorted(words, key=lambda w: (-len(w), w)))
    ''', "['ccc', 'bb', 'dd', 'a']",
      ["['a', 'bb', 'dd', 'ccc']", "['ccc', 'dd', 'bb', 'a']", "['bb', 'dd', 'ccc', 'a']"],
      "A tuple key sorts by the first part, then breaks ties with the next",
      """The key puts the longest words first through the negative length, then orders ties
      alphabetically. So `ccc` leads, then `bb` before `dd`, and the one-letter `a` is last."""),

    q("format-fill-align", '''
        print(f"{'ab':*>5} {'ab':*<5} {'ab':*^5} {7:0>3}")
    ''', "***ab ab*** *ab** 007",
      ["ab*** ***ab *ab** 007", "***ab ab*** **ab* 007", "***ab ab*** *ab** 700"],
      "> pads on the left, < on the right, ^ centres with the extra on the right",
      """The arrow points where the text goes: `>` pushes it right so the stars come first, `<` the
      opposite. `^` centres it, and when the padding is odd Python puts the extra star on the right."""),

    q("dict-update-position", '''
        d = {"b": 1, "a": 2}
        d.update(a=9, c=3)
        print(d)
    ''', "{'b': 1, 'a': 9, 'c': 3}",
      ["{'a': 9, 'b': 1, 'c': 3}", "{'b': 1, 'a': 2, 'c': 3}", "{'b': 1, 'a': 9}"],
      "Updating an existing key keeps its place; new keys go on the end",
      """A dict remembers the order keys were first added. `a` already exists, so its value is replaced
      where it stands, and the new key `c` goes last. Nothing gets sorted."""),

    q("digits-sum-text", '''
        print(sum(int(c) for c in str(2 ** 10)), sum(map(int, "123")), str(12) * 2)
    ''', "7 6 1212", ["1024 6 1212", "7 6 24", "7 123 1212"],
      "Digits of a number are characters until you convert them",
      """`2 ** 10` is 1024, whose digits add up to 7. `map(int, "123")` turns each character into a
      number before summing, giving 6. Multiplying a string repeats it: `"12" * 2` is `1212`."""),

    q("copy-by-slice", '''
        a = [1, 2, 3]
        b = a[:]
        b[0] = 9
        c = a
        c[1] = 8
        print(a, b)
    ''', "[1, 8, 3] [9, 2, 3]",
      ["[9, 8, 3] [9, 2, 3]", "[1, 2, 3] [9, 2, 3]", "[1, 8, 3] [9, 8, 3]"],
      "[:] makes a copy; plain = makes a second name",
      """`a[:]` is a new list, so changing `b` leaves `a` alone. `c = a` is the same list under another
      name, so `c[1] = 8` shows up in `a`. And `b` was copied before that, so it never sees the 8."""),

    q("escape-lengths", '''
        print(len("a\\nb"), len(r"a\\nb"), len("a\\\\b"))
    ''', "3 4 3", ["4 4 4", "3 3 3", "4 4 3"],
      "A backslash escape is one character; a raw string keeps both",
      """In `"a\\nb"` the `\\n` is a single newline, so the length is 3. The raw string `r"a\\nb"` keeps
      the backslash and the n as two characters, so it is 4. `"a\\\\b"` is an escaped backslash: 3."""),

    q("set-operators", '''
        a = {1, 2, 3}
        b = {2, 3, 4}
        print(sorted(a & b), sorted(a | b), sorted(a - b), sorted(a ^ b))
    ''', "[2, 3] [1, 2, 3, 4] [1] [1, 4]",
      ["[2, 3] [1, 2, 3, 4] [1, 4] [1]", "[1, 4] [1, 2, 3, 4] [1] [2, 3]", "[2, 3] [1, 4] [1] [1, 2, 3, 4]"],
      "& is both, | is either, - is only the left, ^ is exactly one",
      """`&` keeps what both sets have, `|` everything. `a - b` is what only `a` has, just 1, while `^`
      is the symmetric difference: items in exactly one set, 1 and 4."""),

    q("fromkeys-shared", '''
        d = dict.fromkeys(["a", "b"], [])
        d["a"].append(1)
        print(d)
    ''', "{'a': [1], 'b': [1]}",
      ["{'a': [1], 'b': []}", "{'a': [], 'b': [1]}", "{'a': [1]}"],
      "fromkeys gives every key the same value object",
      """The `[]` is created once and every key points at that one list. Appending through `d["a"]`
      changes the list that `d["b"]` also holds. A dict comprehension builds a fresh list per key."""),

    q("param-mutate-then-rebind", '''
        def f(lst):
            lst.append(1)
            lst = [9]
            lst.append(2)
            return lst

        a = []
        print(f(a), a)
    ''', "[9, 2] [1]", ["[1, 2] [1, 2]", "[9, 2] []", "[9, 2] [1, 2]"],
      "append changes the caller's list; = cuts the name loose from it",
      """The first `append` changes the list that was passed in, so `a` becomes `[1]`. Then `lst = [9]`
      points the local name at a brand new list, and the second `append` goes into that one instead."""),

    q("dict-values-while-looping", '''
        d = {"a": 1, "b": 2}
        for k, v in d.items():
            v *= 10
            d[k] = v + 1
        print(d)
    ''', "{'a': 11, 'b': 21}",
      ["RuntimeError", "{'a': 10, 'b': 20}", "{'a': 1, 'b': 2}"],
      "Changing values while looping is fine; changing the size is not",
      """Assigning to a key that already exists does not change the dict's size, so the loop is allowed
      to continue. `v` is a copy of the number, and the assignment back stores `v + 1`."""),

    q("try-int-parse", '''
        def parse(s):
            try:
                return int(s)
            except ValueError:
                return -1

        print(parse("12"), parse("1.5"), parse(" 7 "), parse(""))
    ''', "12 -1 7 -1", ["12 1 7 -1", "12 -1 -1 -1", "12 -1 7 0"],
      "int() allows surrounding spaces but not a decimal point",
      """`int("1.5")` is a ValueError, and so is the empty string. Spaces around the digits are
      fine, so `" 7 "` parses to 7."""),

    q("sorted-text-numbers", '''
        words = "10 9 2".split()
        print(sorted(words), sorted([10, 9, 2]), sorted(words, key=int))
    ''', "['10', '2', '9'] [2, 9, 10] ['2', '9', '10']",
      ["['2', '9', '10'] [2, 9, 10] ['2', '9', '10']",
       "['10', '2', '9'] [10, 9, 2] ['10', '2', '9']",
       "['2', '9', '10'] [2, 9, 10] ['10', '2', '9']"],
      "Strings sort letter by letter, not by value",
      """Text is compared character by character, and `"1"` comes before `"2"`, so `"10"` sorts first.
      With `key=int` the comparison is by number, but the items stay strings."""),

    q("or-default-zero", '''
        def area(w, h=None):
            h = h or w
            return w * h

        print(area(3), area(3, 0), area(3, 2))
    ''', "9 9 6", ["9 0 6", "9 9 9", "6 0 6"],
      "`or` treats a real 0 as missing",
      """`h or w` falls back to `w` whenever `h` is falsy, and 0 is falsy. So `area(3, 0)` quietly
      becomes 3 * 3. The safe check is `if h is None`."""),

    q("chain-short-circuit-calls", '''
        calls = []

        def f(x):
            calls.append(x)
            return x

        print(f(3) < f(2) < f(9), calls)
    ''', "False [3, 2]", ["False [3, 2, 9]", "False [2, 3]", "True [3, 2, 9]"],
      "A chained comparison stops at the first false link",
      """`3 < 2` is already False, so Python never evaluates `f(9)`. The calls happen left to right, in
      the order 3 then 2."""),

    q("finally-in-loop-continue", '''
        out = []
        for i in range(3):
            try:
                if i == 1:
                    continue
                out.append(i)
            finally:
                out.append("f")
        print(out)
    ''', "[0, 'f', 'f', 2, 'f']",
      ["[0, 'f', 2, 'f']", "[0, 'f', 'f', 2]", "[0, 2, 'f', 'f', 'f']"],
      "finally runs even when continue jumps out of the try",
      """On `i == 1` the `continue` skips the append, but `finally` still runs on the way out, so an `f`
      is added anyway. Each of the three passes ends with one `f`."""),

    q("zip-same-iterator", '''
        it = iter([1, 2, 3])
        print(list(zip(it, it)))
    ''', "[(1, 2)]",
      ["[(1, 1), (2, 2), (3, 3)]", "[(1, 2), (3, 3)]", "[(1, 2), (3, None)]"],
      "Both zip arguments pull from the same iterator",
      """The first item comes from `it` as 1 and the second from `it` as 2, forming `(1, 2)`. Then zip takes 3
      from the first side, finds the second side empty and stops, so 3 is thrown away."""),

    q("isinstance-bool", '''
        print(isinstance(True, int), type(True) == int,
              isinstance(1, bool), issubclass(bool, int))
    ''', "True False False True",
      ["True True False True", "False False False True", "True False True True"],
      "bool is a subclass of int, but an int is not a bool",
      """`True` is an instance of `int` because `bool` inherits from it. `type(True)` is exactly `bool`,
      not `int`, and plain 1 is not a `bool`."""),

    q("heap-not-sorted", '''
        import heapq
        h = [5, 1, 4]
        heapq.heapify(h)
        print(h[0], h)
    ''', "1 [1, 5, 4]", ["1 [1, 4, 5]", "5 [5, 1, 4]", "1 [5, 1, 4]"],
      "A heap keeps the smallest first, not the whole list sorted",
      """`heapify` rearranges the list in place so the smallest item is at index 0, which is all a heap
      promises. The rest is only partly ordered: `[1, 5, 4]` is a valid heap and not sorted."""),

    q("counter-missing", '''
        from collections import Counter
        c = Counter("hello")
        print(c.most_common(1), c["z"], len(c))
    ''', "[('l', 2)] 0 4", ["[('l', 2)] 0 5", "[('h', 1)] 0 4", "[('l', 2)] None 4"],
      "Counter returns 0 for a missing item, and counts distinct keys",
      """`hello` has the four distinct letters h, e, l, o, with `l` twice. A Counter answers 0 for a
      letter it has never seen (and does not store it)."""),

    q("deque-maxlen", '''
        from collections import deque
        d = deque([1, 2, 3], maxlen=3)
        d.append(4)
        d.appendleft(0)
        print(list(d))
    ''', "[0, 2, 3]", ["[0, 2, 3, 4]", "[2, 3, 4]", "[0, 1, 2, 3]"],
      "A full deque drops from the opposite end",
      """Appending 4 pushes out the 1 on the left, giving `[2, 3, 4]`. Then adding 0 on the left pushes
      out the 4 on the right, leaving `[0, 2, 3]`. It never grows past three."""),

    q("reduce-left-fold", '''
        from functools import reduce
        print(reduce(lambda a, b: a - b, [10, 2, 3]))
    ''', "5", ["11", "-5", "15"],
      "reduce folds from the left: (10 - 2) - 3",
      """The first step is 10 - 2 = 8, and then 8 - 3 = 5. Folding from the right would give
      10 - (2 - 3) = 11, which is not what `reduce` does."""),

    q("ord-chr-shift", '''
        print(ord("a"), chr(ord("a") + 1), ord("A") - ord("a"), chr(65) + chr(66))
    ''', "97 b -32 AB", ["97 b 32 AB", "1 b -32 AB", "97 98 -32 AB"],
      "ord gives a number, chr gives a letter, and capitals are smaller",
      """`ord("a")` is 97, and adding 1 then converting back gives `b`. Capital `A` is 65, which is 32
      below the lowercase `a`, so the difference is negative."""),

    q("len-makes-falsy", '''
        class Box:
            def __len__(self):
                return 0

        print(bool(Box()), "yes" if Box() else "no")
    ''', "False no", ["True yes", "True no", "False yes"],
      "An object with __len__ of 0 is falsy",
      """When a class has no `__bool__`, Python falls back to `__len__`, and a length of 0 means false.
      So an empty-looking object takes the `no` branch."""),

    q("override-through-self", '''
        class A:
            def hi(self):
                return self.name()

            def name(self):
                return "A"

        class B(A):
            def name(self):
                return "B"

        print(A().hi(), B().hi())
    ''', "A B", ["A A", "B B", "B A"],
      "self.name() looks up the method on the real object's class",
      """`hi` is defined in `A`, but `self` is a `B` in the second call, so `self.name()` finds B's
      version first. The method you start in does not decide which override runs."""),

    # ── Strings, numbers and printing ──────────────────────────────────────
    q("format-indexes", '''
        print("{1}-{0}-{1}".format("x", "y"), "{}{}".format(1, 2),
              "{0}".format(1, 2))
    ''', "y-x-y 12 1", ["x-y-x 12 1", "y-x-y 3 1", "y-x-y 12 12"],
      "Numbers in braces pick an argument, and extra arguments are ignored",
      """`{1}` is the second argument and `{0}` the first, and an index can be used more than once.
      Plain `{}` takes the arguments in order, and an unused extra argument is silently dropped."""),

    q("title-vs-capitalize", '''
        print("hello world".title(), "hello world".capitalize(),
              "HELLO".capitalize(), "Hello".swapcase())
    ''', "Hello World Hello world Hello hELLO",
      ["Hello World Hello World Hello hELLO", "Hello World Hello world HELLO hELLO",
       "Hello World Hello world Hello HELLO"],
      "capitalize only touches the first letter and lowers the rest",
      """`title()` capitalises every word, but `capitalize()` raises only the very first letter and
      lowers everything else, so `HELLO` becomes `Hello`. `swapcase()` flips every letter."""),

    q("divmod-clock", '''
        h, m = divmod(125, 60)
        print(f"{h}:{m:02d}", f"{h}:{m}")
    ''', "2:05 2:5", ["2:05 2:05", "2:65 2:65", "5:02 5:2"],
      "A bare number drops its leading zero; :02d pads it",
      """`divmod(125, 60)` gives 2 hours and 5 minutes. Without a format spec the 5 prints as a plain
      `5`, and `:02d` pads it to two digits."""),

    q("no-int-overflow", '''
        print(2 ** 63 + 1)
    ''', "9223372036854775809", ["-9223372036854775807", "9223372036854775808", "OverflowError"],
      "Python ints never overflow",
      """Python integers grow as large as memory allows, so going past 2 to the 63rd just produces a
      bigger number. 2 ** 63 is 9223372036854775808, and adding 1 gives ...809."""),

    q("print-sep-end", '''
        print("a", "b", sep="-", end="!")
    ''', "a-b!", ["a b!", "a-b", "a-b-!"],
      "sep goes between the items and end goes after the last one",
      """`sep` is placed only between items, so there is no dash before the exclamation mark. `end`
      replaces the usual newline, so the `!` finishes the output."""),

    q("pass-is-not-continue", '''
        n = 0
        for i in range(5):
            if i == 2:
                pass
            n += i
        print(n)
    ''', "10", ["8", "6", "15"],
      "pass does nothing, so the loop body carries on",
      """`pass` is only a placeholder for an empty block. The next line still runs for `i == 2`, so
      everything from 0 to 4 is added: 10. A `continue` would have skipped 2 and given 8."""),

    q("range-contains", '''
        a, b = range(1, 5), range(0, 10, 2)
        print(5 in a, 4 in a, 0 in b, 3 in b)
    ''', "False True True False",
      ["True True True True", "True True True False", "False True True True"],
      "A range respects its end and its step when you test membership",
      """`range(1, 5)` stops at 4, so 5 is out. `range(0, 10, 2)` holds only the even numbers, so 0 is in
      and 3 is not."""),

    q("method-chaining", '''
        class Cart:
            def __init__(self):
                self.items = []

            def add(self, x):
                self.items.append(x)
                return self

        print(Cart().add(1).add(2).items)
    ''', "[1, 2]", ["[1]", "[2]", "None"],
      "Returning self lets calls chain on the same object",
      """`add` hands back the same cart, so `.add(2)` runs on it too. Both items end up in the one
      list. Without `return self` the second call would fail on `None`."""),

    q("reverse-words-vs-chars", '''
        print(" ".join("one two".split()[::-1]), "one two"[::-1])
    ''', "two one owt eno", ["owt eno owt eno", "two one one two", "eno owt owt eno"],
      "Reversing the word list is not reversing the text",
      """`split()` makes a list of words, and reversing that list swaps the words but leaves each one
      alone. Reversing the string itself flips every character."""),

    q("unpack-count", '''
        a, b = [1, 2, 3]
        print(a, b)
    ''', "ValueError", ["1 2", "1 [2, 3]", "None None"],
      "Unpacking needs exactly as many names as items",
      """Three items cannot go into two names, so Python raises ValueError ('too many values to
      unpack'). Writing `a, *b = ...` is how you say 'and the rest'.""",
      raises=True),

    q("max-empty", '''
        print(max([]))
    ''', "ValueError", ["None", "0", "[]"],
      "max of nothing is an error, not None",
      """There is no largest item in an empty list, so `max` raises ValueError. If an empty list is
      possible, pass `default=` to say what to return.""",
      raises=True),

    q("float-div-zero", '''
        print(1 / 0.0)
    ''', "ZeroDivisionError", ["inf", "nan", "0.0"],
      "Python raises on float division by zero too",
      """Some languages give `Infinity` for `1 / 0.0`. Python refuses and raises ZeroDivisionError, for
      floats just as for ints. You get `inf` only by writing `float('inf')`.""",
      raises=True),

    q("append-while-iterating", '''
        a = [1, 2, 3]
        for i, x in enumerate(a):
            if x == 1:
                a.append(4)
        print(i, a)
    ''', "3 [1, 2, 3, 4]", ["2 [1, 2, 3, 4]", "2 [1, 2, 3]", "3 [1, 2, 3]"],
      "A list grown during a loop gets visited to the new end",
      """The loop walks by position, and the list is now four long, so it visits the new 4 as well.
      The last `i` is 3. This is also why growing a list while looping can run forever."""),

    q("sci-literal-float", '''
        print(1e3, 1_000, 10 ** 3, 1e3 == 1000, type(1e3).__name__)
    ''', "1000.0 1000 1000 True float",
      ["1000 1000 1000 True int", "1e3 1000 1000 True float", "1000.0 1000 1000 False float"],
      "Scientific notation always makes a float",
      """Any literal with an `e` is a float, so `1e3` prints as `1000.0`. It still compares equal to the
      int 1000. The underscore in `1_000` is only a readability aid."""),

    q("float-repr-threshold", '''
        print(1e16, 1e15, 0.0001, 0.00001)
    ''', "1e+16 1000000000000000.0 0.0001 1e-05",
      ["10000000000000000.0 1000000000000000.0 0.0001 0.00001",
       "1e+16 1e+15 0.0001 1e-05", "1e+16 1000000000000000.0 0.0001 0.00001"],
      "Floats switch to scientific notation at 1e16 and below 1e-4",
      """Python prints a float in plain form while it stays within about 16 digits, then switches to
      exponent form. `1e15` is still plain, but `1e16` is not, and `0.00001` is shown as `1e-05`."""),

    q("removeprefix-vs-lstrip", '''
        print("aabc".lstrip("a"), "aabc".removeprefix("a"), "abc".strip("ac"))
    ''', "bc abc b", ["bc bc b", "abc abc b", "bc abc abc"],
      "strip methods take a set of characters; removeprefix takes one exact string",
      """`lstrip("a")` removes every leading `a`, while `removeprefix("a")` removes the text once. And
      `strip("ac")` strips any mix of `a` and `c` from both ends, leaving just the `b`."""),

    q("key-abs", '''
        nums = [-3, 1, -2]
        print(min(nums, key=abs), max(nums, key=abs), sorted(nums, key=abs))
    ''', "1 -3 [1, -2, -3]", ["-3 1 [-3, -2, 1]", "1 3 [1, 2, 3]", "1 -3 [-3, -2, 1]"],
      "key decides the order, but the original items come back",
      """The items are compared by their absolute value, yet what is returned is the original item,
      sign included. So the max by size is `-3`, and the sorted list keeps its minus signs."""),

    q("count-nonoverlapping", '''
        print("aaaa".count("aa"), "aaaa".replace("aa", "b"), "banana".find("ana"),
              "banana".rfind("ana"))
    ''', "2 bb 1 3", ["3 bb 1 3", "2 baa 1 3", "2 bb 1 1"],
      "count and replace never reuse letters that were already matched",
      """In `aaaa` the matches are positions 0-1 and 2-3, so there are 2, not 3 overlapping ones. In
      `banana` the overlapping `ana` begins at 1 and again at 3, which `find` and `rfind` report."""),

    q("sum-start-list", '''
        print(sum([[1, 2], [3]], []))
    ''', "[1, 2, 3]", ["[6]", "[[1, 2], [3]]", "TypeError"],
      "sum can add lists if you give it a list to start from",
      """The default start value is the number 0, and 0 + a list is an error. With `[]` as the start,
      `sum` computes `[] + [1, 2] + [3]`, which glues the lists together."""),

    q("sort-dict-by-value", '''
        d = {"a": 3, "b": 1, "c": 2}
        by_value = sorted(d.items(), key=lambda kv: kv[1])
        print(sorted(d), sorted(d, key=d.get), by_value[0])
    ''', "['a', 'b', 'c'] ['b', 'c', 'a'] ('b', 1)",
      ["['b', 'c', 'a'] ['b', 'c', 'a'] ('b', 1)", "['a', 'b', 'c'] [1, 2, 3] ('b', 1)",
       "['a', 'b', 'c'] ['b', 'c', 'a'] ('a', 3)"],
      "sorted(d) sorts the keys; a key function sorts them by value",
      """Looping over a dict gives its keys, so plain `sorted(d)` is alphabetical. `key=d.get` orders
      the keys by their values instead, but it still returns keys, not values."""),

    q("bitwise-basics", '''
        print(5 & 3, 5 | 3, 5 ^ 3, 1 << 4, 16 >> 2)
    ''', "1 7 6 16 4", ["1 7 125 16 4", "15 8 6 16 4", "1 7 6 16 8"],
      "^ is XOR, not a power",
      """`5` is 101 and `3` is 011 in binary. AND gives 001 (1), OR gives 111 (7), and XOR gives 110 (6).
      `1 << 4` is 16 and `16 >> 2` is 4."""),

    q("zfill-rjust", '''
        print("7".zfill(3), "-7".zfill(4), "abc".zfill(2), str(7).rjust(3, "0"))
    ''', "007 -007 abc 007", ["007 00-7 abc 007", "007 -007 ab 007", "007 -007 0abc 007"],
      "zfill keeps a sign in front and never shortens",
      """`zfill` pads with zeros after any leading minus sign, so `-7` becomes `-007`. A string already
      longer than the width is returned unchanged."""),

    q("split-empty-pieces", '''
        print("a,b,".split(","), len("".split(",")), len("".split()))
    ''', "['a', 'b', ''] 1 0", ["['a', 'b'] 1 0", "['a', 'b', ''] 0 0", "['a', 'b', ''] 1 1"],
      "split with a separator keeps empty pieces; split() with none does not",
      """A trailing comma leaves an empty piece after it. Splitting the empty string on a comma gives
      one empty piece, but `split()` with no argument splits on runs of whitespace and finds none."""),

    q("property-recomputes", '''
        class Circle:
            def __init__(self, r):
                self.r = r

            @property
            def d(self):
                return self.r * 2

        c = Circle(2)
        c.r = 5
        print(c.d)
    ''', "10", ["4", "5", "AttributeError"],
      "A property is computed each time it is read",
      """`d` is not stored anywhere. Every `c.d` runs the method again with the current `r`, so after
      `c.r = 5` it reports 10."""),

    q("star-star-unpack", '''
        def f(a, b):
            return a - b

        print(f(*[5, 2]), f(**{"b": 5, "a": 2}))
    ''', "3 -3", ["3 3", "-3 -3", "-3 3"],
      "* spreads a list by position; ** spreads a dict by name",
      """`*[5, 2]` becomes `f(5, 2)`, which is 3. `**{"b": 5, "a": 2}` becomes `f(b=5, a=2)`, so the order
      in the dict does not matter: it is `2 - 5`."""),

    q("map-two-iterables", '''
        print(list(map(lambda a, b: a * b, [1, 2, 3], [4, 5])))
    ''', "[4, 10]", ["[4, 10, 0]", "[4, 10, 3]", "[4, 10, 15]"],
      "map stops at the shortest input",
      """With two lists, `map` hands the function one item from each and quits when the shorter one
      runs out. The unmatched 3 is never used."""),

    q("splitlines-vs-split", '''
        print("a\\nb\\n".splitlines(), "a\\nb\\n".split("\\n"))
    ''', "['a', 'b'] ['a', 'b', '']",
      ["['a', 'b'] ['a', 'b']", "['a', 'b', ''] ['a', 'b', '']", "['a', 'b', ''] ['a', 'b']"],
      "A trailing newline leaves an empty piece for split, not for splitlines",
      """`splitlines` understands that a final newline ends the last line, so there is no extra empty
      entry. `split("\\n")` just cuts at every newline, leaving an empty string after the last one."""),

    q("lru-cache-calls", '''
        from functools import lru_cache

        calls = []

        @lru_cache(maxsize=None)
        def f(x):
            calls.append(x)
            return x * 2

        f(1); f(1); f(2); f(1)
        print(len(calls))
    ''', "2", ["4", "3", "1"],
      "A cached function only runs for arguments it has not seen",
      """The first `f(1)` and `f(2)` do the real work. Every repeat of an argument that was seen comes
      straight from the cache, without running the body again, so only two calls are recorded."""),

    q("join-dict-keys", '''
        d = {"b": 1, "a": 2}
        print(",".join(d), ",".join(map(str, d.values())))
    ''', "b,a 1,2", ["1,2 1,2", "a,b 2,1", "b,a 2,1"],
      "Joining a dict joins its keys, in insertion order",
      """Iterating a dict gives its keys, so the first join is `b,a`, in the order they were added,
      not sorted. Joining numbers needs them turned into strings first, which `map(str, ...)` does."""),

    q("chain-target-order", '''
        i = 0
        a = [0, 0]
        a[i] = i = 1
        print(a, i)
    ''', "[1, 0] 1", ["[0, 1] 1", "[1, 0] 0", "[1, 1] 1"],
      "Chained targets are assigned left to right",
      """The value 1 is stored into `a[i]` first, while `i` is still 0, so `a[0]` becomes 1. Only then is
      `i` set to 1. The index in `a[i]` was already used by then."""),

    # ── Harder: protocols, the standard library, odd corners ───────────────
    q("float-literal-rounds", '''
        print(2.9999999999999999 == 3, int(2.9999999999999999),
              int(2.999999999999999))
    ''', "True 3 2", ["False 2 2", "True 2 2", "True 3 3"],
      "A float literal is rounded to the nearest double before you ever see it",
      """Sixteen 9s is closer to 3.0 than to any other double, so the literal is exactly 3.0 and `int`
      gives 3. With only fifteen 9s there is a double just below 3, which `int` truncates to 2."""),

    q("keyerror-str-quotes", '''
        try:
            {"a": 1}["k"]
        except KeyError as e:
            print(e, e.args)
    ''', "'k' ('k',)", ["k ('k',)", "'k' 'k'", "k k"],
      "A KeyError prints its key with quotes, because it shows the repr",
      """`str()` of a KeyError is the repr of the missing key, so a string key keeps its quotes. The
      `args` tuple holds the key itself, which is why it shows as `('k',)`."""),

    q("asyncio-gather-interleave", '''
        import asyncio

        out = []

        async def w(n):
            out.append(f"s{n}")
            await asyncio.sleep(0)
            out.append(f"e{n}")

        async def main():
            await asyncio.gather(w(1), w(2))

        asyncio.run(main())
        print(out)
    ''', "['s1', 's2', 'e1', 'e2']",
      ["['s1', 'e1', 's2', 'e2']", "['s2', 's1', 'e2', 'e1']", "['s1', 's2', 'e2', 'e1']"],
      "Tasks take turns only at an await",
      """Each task runs until its first `await`, which hands control to the other. Both start before either
      finishes, and then they resume in the order they paused, so the ends come out 1 then 2."""),

    q("dict-view-live", '''
        d = {"a": 1}
        keys = d.keys()
        d["b"] = 2
        print(list(keys), len(keys))
    ''', "['a', 'b'] 2", ["['a'] 1", "['a', 'b'] 1", "['a'] 2"],
      "dict.keys() is a live view, not a snapshot",
      """The view reads the dict each time you use it, so it sees the key added after it was created.
      Use `list(d.keys())` straight away if you want a frozen copy."""),

    q("generator-pipeline-order", '''
        log = []

        def src():
            for i in range(3):
                log.append(f"p{i}")
                yield i

        def dbl(it):
            for x in it:
                log.append(f"d{x}")
                yield x * 2

        list(dbl(src()))
        print(" ".join(log))
    ''', "p0 d0 p1 d1 p2 d2",
      ["p0 p1 p2 d0 d1 d2", "d0 p0 d1 p1 d2 p2", "p0 d0 p1 d1 p2"],
      "Chained generators pass one item at a time through every stage",
      """Nothing runs until `list` asks for an item. Then each item travels the whole pipeline before the
      next is produced, so the steps alternate instead of one stage finishing first."""),

    q("getitem-iteration", '''
        class Seq:
            def __getitem__(self, i):
                if i > 2:
                    raise IndexError
                return i * i

        print(list(Seq()), 4 in Seq(), sum(Seq()))
    ''', "[0, 1, 4] True 5", ["[0, 1, 4] False 5", "[0, 1, 4, 9] True 14", "[0, 1, 4] True 3"],
      "__getitem__ alone makes an object iterable",
      """Without `__iter__`, Python tries `obj[0]`, `obj[1]`, and so on until an IndexError. So `list`,
      `in` and `sum` all work. `4 in Seq()` checks the values (0, 1, 4), not the indexes."""),

    q("insert-negative-index", '''
        a = [1, 2]
        a.insert(10, 3)
        a.insert(-1, 4)
        print(a)
    ''', "[1, 2, 4, 3]", ["[1, 2, 3, 4]", "[1, 4, 2, 3]", "[4, 1, 2, 3]"],
      "insert puts the item before the given index, and clamps a big one",
      """An index past the end just appends, giving `[1, 2, 3]`. Then `insert(-1, 4)` goes before the
      last item, not after it, so the 4 lands between 2 and 3."""),

    q("enum-basics", '''
        from enum import Enum

        class C(Enum):
            R = 1
            G = 2

        print(C.R.name, C(2), C.R == 1, len(C))
    ''', "R C.G False 2", ["R G False 2", "R C.G True 2", "1 C.G False 2"],
      "An Enum member is not its value",
      """`C.R.name` is the text `R`, and `C(2)` looks a member up by value, printing as `C.G`. A plain
      Enum member does not equal the number 1; you would need `IntEnum` for that."""),

    q("namedtuple-tuple", '''
        from collections import namedtuple

        P = namedtuple("P", "x y")
        p = P(1, 2)
        print(p, p[0] + p.y, p == (1, 2))
    ''', "P(x=1, y=2) 3 True", ["(1, 2) 3 True", "P(x=1, y=2) 3 False", "P(1, 2) 3 True"],
      "A namedtuple is still a tuple underneath",
      """It prints with its field names, can be read by index or by name, and compares equal to a plain
      tuple holding the same values."""),

    q("itertools-islice", '''
        from itertools import chain, count, cycle, islice

        print(list(islice(count(5), 3)), list(chain("ab", [1])),
              list(islice(cycle("ab"), 5)))
    ''', "[5, 6, 7] ['a', 'b', 1] ['a', 'b', 'a', 'b', 'a']",
      ["[5, 6, 7] [['a', 'b'], 1] ['a', 'b', 'a', 'b', 'a']",
       "[5, 6, 7] ['a', 'b', 1] ['a', 'b', 'a', 'b']",
       "[5, 6, 7, 8] ['a', 'b', 1] ['a', 'b', 'a', 'b', 'a']"],
      "islice cuts an endless iterator; chain flattens one level",
      """`count` and `cycle` never end, so `islice` takes only the first 3 or 5 items. `chain("ab", [1])`
      walks the string's letters and then the list, with no nesting."""),

    q("itertools-counts", '''
        from itertools import combinations, permutations, product

        print(len(list(permutations("abc", 2))), len(list(combinations("abc", 2))),
              len(list(product("ab", repeat=3))))
    ''', "6 3 8", ["3 3 6", "6 6 8", "6 3 6"],
      "Order matters for permutations but not for combinations",
      """Ordered pairs from three letters: 3 * 2 = 6. Unordered pairs: just 3, since `ab` and `ba` count once.
      `product` with `repeat=3` is every three-letter string over two letters: 2 ** 3 = 8."""),

    q("reversed-enumerate", '''
        a = list(enumerate(reversed("ab")))
        b = list(reversed(list(enumerate("ab"))))
        print(a, b)
    ''', "[(0, 'b'), (1, 'a')] [(1, 'b'), (0, 'a')]",
      ["[(1, 'b'), (0, 'a')] [(0, 'b'), (1, 'a')]",
       "[(0, 'b'), (1, 'a')] [(0, 'b'), (1, 'a')]",
       "[(1, 'b'), (0, 'a')] [(1, 'b'), (0, 'a')]"],
      "Reverse before numbering and the numbers restart; reverse after and they stay with the item",
      """In the first, the letters are flipped and then counted from 0, so `b` is 0. In the second, the
      numbers are attached first, `(0, 'a'), (1, 'b')`, and flipping the pairs keeps each number with its letter."""),

    q("format-nested-width", '''
        w, p = 8, 3
        print(f"{3.14159:*>{w}.{p}f}|{'x':-^{w}}")
    ''', "***3.142|---x----",
      ["3.142***|---x----", "***3.14|---x----", "***3.142|----x---"],
      "Braces inside a format spec fill in width and precision",
      """The inner `{w}` and `{p}` become 8 and 3, so the number is rounded to `3.142` and padded to
      8 characters with stars on the left. `x` is centred in 8 with the extra dash on the right."""),

    q("match-string-not-sequence", '''
        def kind(x):
            match x:
                case [a, b]:
                    return "pair"
                case {"k": v}:
                    return "dict"
                case str():
                    return "text"
                case _:
                    return "other"

        print(kind([1, 2]), kind("ab"), kind({"k": 1}), kind(b"ab"))
    ''', "pair text dict other",
      ["pair pair dict pair", "pair pair dict other", "pair text dict pair"],
      "A sequence pattern never matches str or bytes",
      """Match treats strings and bytes as single values, not as sequences of characters, even though
      `"ab"` has two items. So `"ab"` falls through to the `str()` case and `b"ab"` reaches the default."""),

    q("positional-only", '''
        def f(a, /, b):
            return a + b

        print(f(a=1, b=2))
    ''', "TypeError", ["3", "None", "1"],
      "Parameters before / cannot be passed by name",
      """The slash marks `a` as positional-only, so `f(a=1, ...)` is refused with TypeError. Calling
      `f(1, b=2)` would have worked and returned 3.""",
      raises=True),

    q("copy-instance-shallow", '''
        import copy

        class A:
            def __init__(self):
                self.l = [1]

        a = A()
        b = copy.copy(a)
        b.l.append(2)
        c = copy.deepcopy(a)
        c.l.append(3)
        print(a.l, b.l, c.l)
    ''', "[1, 2] [1, 2] [1, 2, 3]",
      ["[1, 2] [1, 2] [1, 3]", "[1] [1, 2] [1, 2, 3]", "[1, 2] [1, 2] [1, 2]"],
      "copy.copy shares the inner list; deepcopy takes it as it is at that moment",
      """`copy.copy` makes a new `A` whose `l` is the same list, so appending through `b` changes `a`. The
      deep copy comes later, so it starts from `[1, 2]` and its own append gives `[1, 2, 3]`."""),

    q("decimal-float-ctor", '''
        from decimal import Decimal

        a = Decimal("0.1") + Decimal("0.2")
        b = Decimal(0.1) == Decimal("0.1")
        print(a == Decimal("0.3"), b, Decimal("1.10") + Decimal("2.20"))
    ''', "True False 3.30", ["False False 3.3", "True True 3.30", "True False 3.3"],
      "Build Decimals from strings, not floats",
      """Strings keep the exact decimal digits, so 0.1 + 0.2 equals 0.3. `Decimal(0.1)` captures the float's
      binary error, so it is not equal to `Decimal("0.1")`. Trailing zeros are kept: `3.30`."""),

    q("fraction-reduce", '''
        from fractions import Fraction

        print(Fraction(1, 3) + Fraction(1, 6), Fraction("0.5") == 0.5,
              Fraction(2, 4))
    ''', "1/2 True 1/2", ["2/9 True 1/2", "1/2 False 2/4", "0.5 True 1/2"],
      "Fractions stay exact and are always reduced",
      """1/3 + 1/6 is 2/6 + 1/6 = 3/6, reduced to 1/2. `Fraction(2, 4)` is reduced on creation, and 0.5 is
      exactly representable, so the comparison with the float is true."""),

    q("dict-reinsert-order", '''
        d = {"a": 1, "b": 2}
        del d["a"]
        d["a"] = 3
        print(list(d))
    ''', "['b', 'a']", ["['a', 'b']", "['b']", "['a', 'b', 'a']"],
      "A deleted and re-added key goes to the end",
      """Deleting `a` removes its place in the order, and adding it back puts it after `b`. Only
      updating a key that is still there leaves its position alone."""),

    q("counter-subtract-drops", '''
        from collections import Counter

        print(Counter("aab") - Counter("ab"), Counter("ab") - Counter("aab"))
    ''', "Counter({'a': 1}) Counter()",
      ["Counter({'a': 1}) Counter({'a': -1})", "Counter({'a': 1, 'b': 0}) Counter()", "{'a': 1} {}"],
      "Counter subtraction keeps only positive counts",
      """The - operator throws away anything at zero or below, so no negative counts appear. Only
      `.subtract()` would keep them."""),

    q("empty-in", '''
        print("" in "abc", "" in ["abc"], [] in [[]], () in [[]])
    ''', "True False True False", ["False False True False", "True True True False", "True False True True"],
      "The empty string is inside every string, but a list needs a real match",
      """Every string contains the empty string. A list is checked item by item with `==`: `[]` equals
      the `[]` inside, but `()` is a tuple and never equals a list."""),

    q("class-attr-inherit-live", '''
        class A:
            x = 1

        class B(A):
            pass

        class C(A):
            pass

        B.x = 2
        A.x = 5
        print(A.x, B.x, C.x)
    ''', "5 2 5", ["2 2 2", "1 2 1", "5 5 5"],
      "A subclass sees the parent's attribute until it sets its own",
      """`B.x = 2` gives B its own `x`, hiding the parent's. `C` never set one, so it looks up to `A` each
      time and sees the later change to 5."""),

    q("generator-close-finally", '''
        log = []

        def g():
            try:
                yield 1
                yield 2
            finally:
                log.append("closed")

        it = g()
        next(it)
        it.close()
        print(log, list(it))
    ''', "['closed'] []", ["[] [2]", "['closed'] [2]", "[] []"],
      "close() stops a generator on the spot, and runs its finally block",
      """`close()` raises an exit signal inside the paused generator at its `yield`, so the `finally` runs and
      the generator is finished. Asking it for more items afterwards gives nothing."""),

    q("late-binding-genexp", '''
        gens = [(i for _ in range(1)) for i in range(3)]
        print([next(g) for g in gens])
    ''', "[2, 2, 2]", ["[0, 1, 2]", "[0, 0, 0]", "[3, 3, 3]"],
      "A generator expression looks up an outer name when it runs, not when it is made",
      """Each inner generator refers to the variable `i` of the surrounding comprehension, and it only reads
      it when `next` is called, by which time the outer loop has finished with `i` at 2."""),

    q("format-field-access", '''
        print("{0[1]} {1.real} {name!r}".format([5, 6], 3, name="x"))
    ''', "6 3 'x'", ["5 3 'x'", "6 3 x", "[5, 6] 3 'x'"],
      "A format field can index, read an attribute, and apply !r",
      """`{0[1]}` takes the first argument and indexes it, giving 6. `{1.real}` reads an attribute of the
      second argument, and `!r` shows the repr of the keyword argument, so the quotes appear."""),

    q("dict-equality-order", '''
        from collections import OrderedDict

        a = {"a": 1, "b": 2}
        b = {"b": 2, "a": 1}
        oa, ob = OrderedDict(a), OrderedDict(b)
        print(a == b, oa == ob, oa == b, list(a) == list(b))
    ''', "True False True False",
      ["False False True False", "True True True False", "True False False False"],
      "Plain dicts ignore order when compared; two OrderedDicts do not",
      """A normal dict equals another with the same pairs in any order. Two OrderedDicts also compare their
      order, so they differ here, but an OrderedDict against a plain dict ignores it."""),

    q("partial-override", '''
        from functools import partial

        p = partial(int, base=2)
        print(p("101"), p("101", base=10), partial(pow, 2)(5))
    ''', "5 101 32", ["5 5 32", "101 101 32", "5 101 25"],
      "partial fixes arguments, but a keyword given at call time wins",
      """`p("101")` uses the fixed `base=2` and gives 5. Passing `base=10` at call time replaces it, so
      it reads 101. `partial(pow, 2)(5)` is `pow(2, 5)`, with the 2 fixed first."""),

    # ── END ──
)
