"""Python moments: stop the program and say what a variable holds.

Same rules as the JavaScript and Dart sets: each question is "execution is
about to run line L (for the Nth time): what is x?", and every answer is
what Python's own tracer reports at that moment - tests/test_trace_python.py
runs each one. Answers are written the way Python's repr writes them:
'text' in quotes, True and None with capitals, (1, 2) for a tuple.

The decoys are the misreadings Python actually invites: an alias taken for
a copy, a string method taken for a change in place, `range` taken to
include its end, a default list taken to be fresh on every call, and the
loop variable a lambda closes over taken to be frozen when it was made.
"""

from __future__ import annotations

from code_coach.trace import Trace, _t

PYTHON = "Python"


PY_TRACES: tuple[Trace, ...] = (
    _t(
        id="trace-py-floor-division",
        level=1,
        name="Two kinds of division",
        family=PYTHON,
        language="python",
        code=(
            "scores = [7, 8, 8]\n"
            "total = sum(scores)\n"
            "avg = total // len(scores)\n"
            "exact = total / len(scores)\n"
            "print(avg, exact)"
        ),
        at_line=5,
        occurrence=1,
        variable="avg",
        expect="7",
        decoys=("8", "7.0", "7.666666666666667"),
        why=(
            "The total is 23, and 23 / 3 is 7.67. `//` is floor division: it "
            "rounds down, so 7 and not 8, and with two ints it gives an int, "
            "so not 7.0. The plain `/` beside it always gives a float, even "
            "for 6 / 2, which is 3.0."
        ),
    ),
    _t(
        id="trace-py-alias",
        level=1,
        name="Two names, one list",
        family=PYTHON,
        language="python",
        code=(
            "a = [1, 2]\n"
            "b = a\n"
            "b.append(3)\n"
            "print(a)"
        ),
        at_line=4,
        occurrence=1,
        variable="a",
        expect="[1, 2, 3]",
        decoys=("[1, 2]", "[3]", "[1, 2, [3]]"),
        why=(
            "`b = a` copies nothing: it puts a second name on the same list. "
            "So `b.append(3)` changes the one list both names point at, and "
            "a sees it. Watch it run shows one list with two arrows into it."
        ),
    ),
    _t(
        id="trace-py-running-total",
        level=1,
        name="A total part way round",
        family=PYTHON,
        language="python",
        code=(
            "total = 0\n"
            "for n in [3, 5, 7]:\n"
            "    total += n\n"
            "print(total)"
        ),
        at_line=3,
        occurrence=3,
        variable="total",
        expect="8",
        decoys=("15", "7", "10"),
        why=(
            "About to run line 3 for the third time means two additions have "
            "happened and the third has not: 0 + 3 + 5 = 8. 15 is the total "
            "after the loop, one step later. The moment is 'before the line "
            "runs', which is the question to ask of every loop."
        ),
    ),
    _t(
        id="trace-py-copy",
        level=2,
        name="A copy is a new list",
        family=PYTHON,
        language="python",
        code=(
            "a = [1, 2]\n"
            "b = a[:]\n"
            "b.append(3)\n"
            "print(a, b)"
        ),
        at_line=4,
        occurrence=1,
        variable="a",
        expect="[1, 2]",
        decoys=("[1, 2, 3]", "[]", "[3]"),
        why=(
            "`a[:]` is a slice of the whole list, and a slice is always a new "
            "list - so b is a copy this time, and appending to it leaves a "
            "alone. `list(a)` and `a.copy()` do the same. Compare with the "
            "alias one, where `b = a` made no copy at all."
        ),
    ),
    _t(
        id="trace-py-str-immutable",
        level=2,
        name="A string method changes nothing",
        family=PYTHON,
        language="python",
        code=(
            "word = \"hello\"\n"
            "word.upper()\n"
            "loud = word.upper()\n"
            "print(word, loud)"
        ),
        at_line=4,
        occurrence=1,
        variable="word",
        expect="'hello'",
        decoys=("'HELLO'", "None", "'Hello'"),
        why=(
            "Strings cannot be changed. `upper()` builds a new string and "
            "hands it back, so line 2 made 'HELLO' and threw it away, and "
            "word is untouched. Line 3 keeps the new one, in loud. To change "
            "word, assign it: word = word.upper()."
        ),
    ),
    _t(
        id="trace-py-range-end",
        level=2,
        name="Where range stops",
        family=PYTHON,
        language="python",
        code=(
            "last = None\n"
            "for i in range(1, 5):\n"
            "    last = i\n"
            "print(last)"
        ),
        at_line=4,
        occurrence=1,
        variable="last",
        expect="4",
        decoys=("5", "None", "3"),
        why=(
            "`range(1, 5)` is 1, 2, 3, 4: it starts at the first number and "
            "stops BEFORE the second. That is why range(len(xs)) gives every "
            "index of xs and never one past the end. The loop ran four times "
            "and the last value it handed out was 4."
        ),
    ),
    _t(
        id="trace-py-dict-order",
        level=2,
        name="Counting letters into a dict",
        family=PYTHON,
        language="python",
        code=(
            "counts = {}\n"
            "for ch in \"banana\":\n"
            "    counts[ch] = counts.get(ch, 0) + 1\n"
            "print(counts)"
        ),
        at_line=4,
        occurrence=1,
        variable="counts",
        expect="{'b': 1, 'a': 3, 'n': 2}",
        decoys=(
            "{'a': 3, 'b': 1, 'n': 2}",
            "{'b': 1, 'a': 1, 'n': 1}",
            "{'banana': 1}",
        ),
        why=(
            "A dict keeps its keys in the order they were first added, not "
            "sorted: b came first, then a, then n. `get(ch, 0)` gives 0 for a "
            "letter not seen yet, so each letter counts from there - three "
            "a's, two n's and one b."
        ),
    ),
    _t(
        id="trace-py-swap",
        level=3,
        name="Both sides before either changes",
        family=PYTHON,
        language="python",
        code=(
            "a = 1\n"
            "b = 2\n"
            "a, b = b, a + b\n"
            "print(a, b)"
        ),
        at_line=4,
        occurrence=1,
        variable="b",
        expect="3",
        decoys=("4", "2", "1"),
        why=(
            "The whole right-hand side is worked out first - (2, 1 + 2), so "
            "(2, 3) - and only then are a and b given their new values. 4 is "
            "the answer if a changed first and b used the new a, which is "
            "what two separate lines would do. This is the Fibonacci step."
        ),
    ),
    _t(
        id="trace-py-tuple-unpack",
        level=3,
        name="Unpacking pairs in a loop",
        family=PYTHON,
        language="python",
        code=(
            "pairs = [(\"a\", 1), (\"b\", 2)]\n"
            "keys = []\n"
            "for key, value in pairs:\n"
            "    keys.append(key * value)\n"
            "print(keys)"
        ),
        at_line=5,
        occurrence=1,
        variable="keys",
        expect="['a', 'bb']",
        decoys=("['a', 'b']", "['a1', 'b2']", "[('a', 1), ('b', 2)]"),
        why=(
            "`for key, value in pairs` takes each tuple apart as it goes: "
            "key is the letter, value the number. A string times a number "
            "repeats it, so 'a' * 1 is 'a' and 'b' * 2 is 'bb'. It is not "
            "joined to the number - that would need str(value)."
        ),
    ),
    _t(
        id="trace-py-collatz",
        level=3,
        name="A while loop's third time round",
        family=PYTHON,
        language="python",
        code=(
            "n = 10\n"
            "steps = 0\n"
            "while n != 1:\n"
            "    n = n // 2 if n % 2 == 0 else 3 * n + 1\n"
            "    steps += 1\n"
            "print(steps)"
        ),
        at_line=5,
        occurrence=3,
        variable="n",
        expect="8",
        decoys=("16", "4", "5"),
        why=(
            "Line 4 has run three times by the third arrival at line 5: 10 is "
            "even so 5, 5 is odd so 16, 16 is even so 8. The trap is counting "
            "line 5's arrivals as line 4's plus one, which gives 4, or "
            "stopping one short at 16."
        ),
    ),
    _t(
        id="trace-py-grid-times",
        level=4,
        name="A grid made with *",
        family=PYTHON,
        language="python",
        code=(
            "grid = [[0] * 2] * 2\n"
            "grid[0][0] = 5\n"
            "print(grid)"
        ),
        at_line=3,
        occurrence=1,
        variable="grid",
        expect="[[5, 0], [5, 0]]",
        decoys=("[[5, 0], [0, 0]]", "[[5, 5], [5, 5]]", "[[5, 0]]"),
        why=(
            "`[row] * 2` does not copy the row: it makes a list holding the "
            "same row twice. So both rows are one list, and setting grid[0][0] "
            "shows up in grid[1] too. Make each row new instead: "
            "grid = [[0] * 2 for _ in range(2)]. (`[0] * 2` is fine - ints "
            "cannot be changed, so sharing them does no harm.)"
        ),
    ),
    _t(
        id="trace-py-default-list",
        level=4,
        name="A default list is made once",
        family=PYTHON,
        language="python",
        code=(
            "def add(item, bag=[]):\n"
            "    bag.append(item)\n"
            "    return bag\n"
            "first = add(\"a\")\n"
            "second = add(\"b\")\n"
            "print(first)"
        ),
        at_line=6,
        occurrence=1,
        variable="first",
        expect="['a', 'b']",
        decoys=("['a']", "['b']", "None"),
        why=(
            "A default value is made once, when the def runs - not on every "
            "call. Both calls append to that one list and return it, so first "
            "and second are the same list, which now holds both. Use "
            "bag=None and `if bag is None: bag = []` inside to get a fresh "
            "one each time."
        ),
    ),
    _t(
        id="trace-py-late-binding",
        level=5,
        name="What a lambda remembers",
        family=PYTHON,
        language="python",
        code=(
            "funcs = []\n"
            "for i in range(3):\n"
            "    funcs.append(lambda: i)\n"
            "results = [f() for f in funcs]\n"
            "print(results)"
        ),
        at_line=5,
        occurrence=1,
        variable="results",
        expect="[2, 2, 2]",
        decoys=("[0, 1, 2]", "[3, 3, 3]", "[0, 0, 0]"),
        why=(
            "A lambda remembers the VARIABLE i, not the value i had when the "
            "lambda was made. All three are called after the loop, when i is "
            "2 (range(3) stops at 2, not 3), so all three answer 2. To freeze "
            "each value, make it a default: lambda i=i: i."
        ),
    ),
)
