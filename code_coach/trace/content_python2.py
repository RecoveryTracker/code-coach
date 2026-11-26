"""More Python moments: the second set.

Same rules as content_python.py - each answer is what Python's tracer
reports at that exact moment, written the way repr writes it - on ground the
first thirteen do not cover: a nested loop part way through, a while loop's
counter, `+=` on a list versus `+`, a function's local shadowing a global,
string slicing, a set's size, sorted() versus .sort(), a dict updated in a
loop, integer division with a negative, and a recursion's depth.
"""

from __future__ import annotations

from code_coach.trace import Trace, _t

PYTHON = "Python"


PY_TRACES_2: tuple[Trace, ...] = (
    _t(
        id="trace-py-slice",
        level=1,
        name="Slicing a string",
        family=PYTHON,
        language="python",
        code=(
            "word = \"python\"\n"
            "start = word[:2]\n"
            "end = word[-2:]\n"
            "middle = word[2:4]\n"
            "print(start, middle, end)"
        ),
        at_line=5,
        occurrence=1,
        variable="middle",
        expect="'th'",
        decoys=("'yth'", "'tho'", "'ht'"),
        why=(
            "A slice [a:b] starts AT index a and stops BEFORE index b. 'python' "
            "is p0 y1 t2 h3 o4 n5, so [2:4] is indexes 2 and 3: 'th'. The same "
            "rule makes [:2] the first two letters and [-2:] the last two, and "
            "it is why b - a is always the length of the slice."
        ),
    ),
    _t(
        id="trace-py-set-size",
        level=1,
        name="A set keeps each thing once",
        family=PYTHON,
        language="python",
        code=(
            "seen = set()\n"
            "for ch in \"mississippi\":\n"
            "    seen.add(ch)\n"
            "size = len(seen)\n"
            "print(size)"
        ),
        at_line=5,
        occurrence=1,
        variable="size",
        expect="4",
        decoys=("11", "5", "3"),
        why=(
            "Adding something a set already holds does nothing, so eleven adds "
            "leave just the different letters: m, i, s and p. That makes "
            "len(set(text)) the quick way to count distinct items. A set has "
            "no order, which is why this asks for its size and not its "
            "contents."
        ),
    ),
    _t(
        id="trace-py-while-counter",
        level=2,
        name="A while loop's counter",
        family=PYTHON,
        language="python",
        code=(
            "balance = 100\n"
            "years = 0\n"
            "while balance < 150:\n"
            "    balance = balance * 1.2\n"
            "    years += 1\n"
            "print(years, round(balance))"
        ),
        at_line=6,
        occurrence=1,
        variable="years",
        expect="3",
        decoys=("2", "4", "50"),
        why=(
            "100 grows to 120 after one year, 144 after two - still under 150, "
            "so round again - and 172.8 after three, which ends the loop. The "
            "test is checked BEFORE each pass, so the loop stops as soon as the "
            "balance has passed 150, not one year early or late."
        ),
    ),
    _t(
        id="trace-py-sorted-vs-sort",
        level=2,
        name="sorted() and .sort()",
        family=PYTHON,
        language="python",
        code=(
            "scores = [3, 1, 2]\n"
            "ranked = sorted(scores)\n"
            "same = scores.sort()\n"
            "print(scores, ranked, same)"
        ),
        at_line=4,
        occurrence=1,
        variable="same",
        expect="None",
        decoys=("[1, 2, 3]", "[3, 1, 2]", "True"),
        why=(
            "`sorted(scores)` makes a NEW sorted list and hands it back. "
            "`scores.sort()` sorts scores itself, in place, and returns None on "
            "purpose, so nobody mistakes it for a copy. By line 4, scores is "
            "sorted too - but same is None."
        ),
    ),
    _t(
        id="trace-py-nested-loop",
        level=2,
        name="Inside a nested loop",
        family=PYTHON,
        language="python",
        code=(
            "pairs = []\n"
            "for a in range(2):\n"
            "    for b in range(3):\n"
            "        pairs.append((a, b))\n"
            "print(len(pairs))"
        ),
        at_line=4,
        occurrence=5,
        variable="b",
        expect="1",
        decoys=("4", "2", "0"),
        why=(
            "The inner loop runs all the way through for EACH turn of the "
            "outer one. The first three arrivals at line 4 are a = 0 with b = "
            "0, 1, 2; then a becomes 1 and b starts again from 0. So the fifth "
            "arrival is a = 1, b = 1."
        ),
    ),
    _t(
        id="trace-py-shadow-global",
        level=3,
        name="A local with a global's name",
        family=PYTHON,
        language="python",
        code=(
            "total = 10\n"
            "def add_tax(price):\n"
            "    total = price * 1.5\n"
            "    return total\n"
            "cost = add_tax(4)\n"
            "print(total, cost)"
        ),
        at_line=6,
        occurrence=1,
        variable="total",
        expect="10",
        decoys=("6.0", "15.0", "None"),
        why=(
            "Assigning to total inside the function makes a NEW local total that "
            "exists only while add_tax runs. The global total is untouched, so "
            "it is still 10 at line 6. The 6.0 went into cost. Changing the "
            "global would need `global total` - and usually a return is the "
            "better way."
        ),
    ),
    _t(
        id="trace-py-list-plus-equals",
        level=3,
        name="+= on a list, and +",
        family=PYTHON,
        language="python",
        code=(
            "a = [1]\n"
            "b = a\n"
            "a += [2]\n"
            "a = a + [3]\n"
            "print(a, b)"
        ),
        at_line=5,
        occurrence=1,
        variable="b",
        expect="[1, 2]",
        decoys=("[1]", "[1, 2, 3]", "[1, 3]"),
        why=(
            "`a += [2]` changes the list a points at, in place - and b points at "
            "the same list, so b sees the 2. `a = a + [3]` builds a NEW list and "
            "points a at it; b still points at the old one. So a is [1, 2, 3] "
            "but b stops at [1, 2]."
        ),
    ),
    _t(
        id="trace-py-negative-floor",
        level=3,
        name="Floor division below zero",
        family=PYTHON,
        language="python",
        code=(
            "temp = -7\n"
            "half = temp // 2\n"
            "rest = temp % 2\n"
            "print(half, rest)"
        ),
        at_line=4,
        occurrence=1,
        variable="half",
        expect="-4",
        decoys=("-3", "-3.5", "3"),
        why=(
            "`//` rounds DOWN, towards minus infinity, not towards zero: -3.5 "
            "goes down to -4. C, Java and JavaScript's Math.trunc would say -3. "
            "Python's % is built to match, so rest is 1 and half * 2 + rest is "
            "still -7."
        ),
    ),
    _t(
        id="trace-py-dict-running",
        level=4,
        name="A dict updated in a loop",
        family=PYTHON,
        language="python",
        code=(
            "sales = [(\"tea\", 2), (\"jam\", 5), (\"tea\", 3)]\n"
            "totals = {}\n"
            "for item, n in sales:\n"
            "    totals[item] = totals.get(item, 0) + n\n"
            "print(totals)"
        ),
        at_line=4,
        occurrence=3,
        variable="totals",
        expect="{'tea': 2, 'jam': 5}",
        decoys=("{'tea': 5, 'jam': 5}", "{'tea': 3, 'jam': 5}", "{'tea': 2, 'jam': 5, 'tea': 3}"),
        why=(
            "About to run line 4 for the third time means two sales are in and "
            "the third - tea 3 - is not yet. So tea is still 2. One line later "
            "it becomes 5. A dict never holds the same key twice: the last "
            "decoy is not something a dict can be."
        ),
    ),
    _t(
        id="trace-py-recursion-depth",
        level=5,
        name="How deep the recursion is",
        family=PYTHON,
        language="python",
        code=(
            "def depth(n):\n"
            "    if n <= 1:\n"
            "        return 0\n"
            "    return 1 + depth(n // 2)\n"
            "result = depth(20)\n"
            "print(result)"
        ),
        at_line=6,
        occurrence=1,
        variable="result",
        expect="4",
        decoys=("5", "10", "20"),
        why=(
            "Each call halves n: 20, 10, 5, 2, then 1 stops it. Four calls added "
            "1 each before the last one answered 0, so 4. That is how many "
            "times you can halve 20 before reaching 1 - roughly log2 of n - "
            "which is why halving algorithms like binary search are so fast."
        ),
    ),
)
