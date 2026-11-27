"""A third set of Dart moments.

Same rule as the first two sets: every expected value was worked out by
hand first and tests/test_trace_dart3.py runs the real Dart tracer and
holds the set to it.

This set is plain control flow and data: loops that go round inside loops,
`continue` and `break`, recursion (a function's own variables, one set per
call), a list with two names, a map that remembers the order keys arrived
in, a string built up, `++` before and after, and a closure that changes
its caller's variable.

The tracer stops at a line BEFORE it runs, so a question about the third
time a line is reached sees what the first two times left behind.
"""

from __future__ import annotations

from code_coach.trace import Trace, _t


DART_TRACES_3: tuple[Trace, ...] = (
    _t(
        id="trace-dart3-while-continue",
        level=1,
        name="Skipping the even numbers",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  var n = 0;\n"
            "  var sum = 0;\n"
            "  while (n < 6) {\n"
            "    n++;\n"
            "    if (n % 2 == 0) continue;\n"
            "    sum += n;\n"
            "  }\n"
            "  print(sum);\n"
            "}"
        ),
        at_line=9,
        occurrence=1,
        variable="sum",
        expect="9",
        decoys=("6", "12", "21"),
        why=(
            "n goes 1, 2, 3, 4, 5, 6, and `continue` jumps back to the "
            "loop test the moment n is even, so `sum += n` only runs for "
            "1, 3 and 5. 1 + 3 + 5 is 9. Unlike `break`, continue does "
            "not leave the loop - it only abandons the rest of this "
            "round. 12 would be the evens, 21 every number."
        ),
    ),
    _t(
        id="trace-dart3-list-two-names",
        level=1,
        name="A list with two names, and a copy",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final a = [1, 2, 3];\n"
            "  final b = a;\n"
            "  b.add(4);\n"
            "  final c = [...a];\n"
            "  c.removeAt(0);\n"
            "  print(a);\n"
            "}"
        ),
        at_line=7,
        occurrence=1,
        variable="a",
        expect="[1, 2, 3, 4]",
        decoys=("[1, 2, 3]", "[1, 2, 4]", "[2, 3, 4]"),
        why=(
            "`final b = a` copies nothing: a and b are two names for "
            "one list, so `b.add(4)` is visible through a. `[...a]` on "
            "the other hand builds a brand-new list holding the same "
            "items, so `c.removeAt(0)` shortens only c, which ends up "
            "[2, 3, 4]. a was changed by the add and untouched by the "
            "remove."
        ),
    ),
    _t(
        id="trace-dart3-nested-count",
        level=2,
        name="Counting inside two loops",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  var steps = 0;\n"
            "  for (var i = 1; i <= 3; i++) {\n"
            "    for (var j = 0; j < i; j++) {\n"
            "      steps++;\n"
            "    }\n"
            "  }\n"
            "  print(steps);\n"
            "}"
        ),
        at_line=5,
        occurrence=4,
        variable="steps",
        expect="3",
        decoys=("4", "6", "1"),
        why=(
            "The inner loop runs i times for each i: once for i = 1, "
            "twice for i = 2, three times for i = 3 - six times in all, "
            "so line 5 is reached six times. We stop the fourth time, "
            "before that `steps++` runs, so only the first three have "
            "counted: 1 from i = 1, then 2 from i = 2. The finished "
            "total, 6, is what line 8 would show."
        ),
    ),
    _t(
        id="trace-dart3-string-prepend",
        level=2,
        name="Building a string backwards",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  var out = '';\n"
            "  for (var i = 1; i <= 4; i++) {\n"
            "    out = '$i$out';\n"
            "  }\n"
            "  print(out);\n"
            "}"
        ),
        at_line=4,
        occurrence=3,
        variable="out",
        expect="'21'",
        decoys=("'12'", "'123'", "'321'"),
        why=(
            "Each round puts the new number in FRONT of what is there: "
            "'$i$out' reads i first, then the old out. Round 1 makes '1', "
            "round 2 makes '21'. The question stops the third time the "
            "line is about to run, so out is still '21' - the 3 has not "
            "been added. Appending, `'$out$i'`, would have given '12'."
        ),
    ),
    _t(
        id="trace-dart3-post-increment",
        level=2,
        name="++ before and after",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  var i = 5;\n"
            "  final a = i++;\n"
            "  final b = ++i;\n"
            "  final c = i-- - 1;\n"
            "  print('$a $b $c $i');\n"
            "}"
        ),
        at_line=6,
        occurrence=1,
        variable="c",
        expect="6",
        decoys=("5", "7", "8"),
        why=(
            "`i++` hands over the old value and then adds: a is 5 and i "
            "becomes 6. `++i` adds first: i becomes 7 and b is 7. Then "
            "`i--` hands over the old value, 7, and i drops back to 6, "
            "so `i-- - 1` is 7 - 1 = 6. The variable i itself is also 6 "
            "at the end, which is a coincidence worth noticing: c and i "
            "agree here by accident."
        ),
    ),
    _t(
        id="trace-dart3-recursion-argument",
        level=3,
        name="The third call of a recursive function",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final r = fact(4);\n"
            "  print(r);\n"
            "}\n"
            "\n"
            "int fact(int n) {\n"
            "  if (n <= 1) return 1;\n"
            "  return n * fact(n - 1);\n"
            "}"
        ),
        at_line=7,
        occurrence=3,
        variable="n",
        expect="2",
        decoys=("1", "3", "4"),
        why=(
            "fact(4) calls fact(3), which calls fact(2), which calls "
            "fact(1). Line 7 is the first line of each call, so it is "
            "reached with n = 4, then 3, then 2, then 1. The third time "
            "is n = 2. Every call has its own n: the 4 is still waiting "
            "in the first call while the later ones run. Nothing is "
            "multiplied until the calls start coming back."
        ),
    ),
    _t(
        id="trace-dart3-map-order",
        level=3,
        name="Counting letters in a map",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final counts = <String, int>{};\n"
            "  for (final ch in 'banana'.split('')) {\n"
            "    counts[ch] = (counts[ch] ?? 0) + 1;\n"
            "  }\n"
            "  print(counts);\n"
            "}"
        ),
        at_line=6,
        occurrence=1,
        variable="counts",
        expect="{ b: 1, a: 3, n: 2 }",
        decoys=(
            "{ a: 3, b: 1, n: 2 }",
            "{ a: 1, b: 1, n: 1 }",
            "{ b: 1, a: 3, n: 2, a: 3 }",
        ),
        why=(
            "b, a, n, a, n, a go by. A key that is not in the map yet "
            "gives null, `?? 0` turns that into 0, and the +1 stores it: "
            "so b: 1, a: 1, n: 1, then a and n again, then a once more - "
            "a ends at 3, n at 2, b at 1. Dart's maps keep the order "
            "keys first arrived in (b, a, n), not alphabetical order and "
            "not by count."
        ),
    ),
    _t(
        id="trace-dart3-closure-counter",
        level=3,
        name="A function that changes its caller's variable",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  var count = 0;\n"
            "  void bump() {\n"
            "    count += 2;\n"
            "  }\n"
            "  bump();\n"
            "  bump();\n"
            "  print(count);\n"
            "}"
        ),
        at_line=4,
        occurrence=2,
        variable="count",
        expect="2",
        decoys=("0", "4", "1"),
        why=(
            "bump is defined inside main, so it sees main's count - the "
            "same variable, not a copy of it. The first call changes it "
            "from 0 to 2. We stop inside the second call, before its "
            "`count += 2` runs, so count is 2; when main prints, it is "
            "4. Remember that a function in Dart keeps hold of the "
            "variables around where it was written, which is what "
            "makes counters and callbacks work."
        ),
    ),
    _t(
        id="trace-dart3-recursion-list",
        level=4,
        name="A list that gets shorter with each call",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final t = total([3, 4, 5]);\n"
            "  print(t);\n"
            "}\n"
            "\n"
            "int total(List<int> xs) {\n"
            "  if (xs.isEmpty) return 0;\n"
            "  return xs.first + total(xs.sublist(1));\n"
            "}"
        ),
        at_line=8,
        occurrence=2,
        variable="xs",
        expect="[4, 5]",
        decoys=("[3, 4, 5]", "[5]", "[]"),
        why=(
            "Each call peels off the first number and hands everything "
            "after it to the next call: [3, 4, 5], then [4, 5], then "
            "[5], then []. Line 8 only runs when the list is not empty, "
            "so it is reached three times - the second is [4, 5]. The "
            "empty list is the call that stops the recursion at line 7 "
            "and never reaches line 8 at all."
        ),
    ),
    _t(
        id="trace-dart3-break-inner",
        level=4,
        name="A break that only leaves one loop",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  var found = '';\n"
            "  for (var r = 0; r < 3; r++) {\n"
            "    for (var c = 0; c < 3; c++) {\n"
            "      if (r * c == 2) { found = '$r$c'; break; }\n"
            "    }\n"
            "  }\n"
            "  print(found);\n"
            "}"
        ),
        at_line=8,
        occurrence=1,
        variable="found",
        expect="'21'",
        decoys=("'12'", "''", "'22'"),
        why=(
            "r * c is 2 first at r = 1, c = 2, which sets found to '12' "
            "and breaks. But `break` leaves only the inner loop: the "
            "outer one goes on to r = 2, where c = 1 gives 2 again and "
            "found is overwritten with '21'. Nothing stops the outer "
            "loop, so the last match wins. To stop everything, label "
            "the outer loop and write `break outer;`."
        ),
    ),
)
