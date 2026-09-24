"""The Dart moments.

Same rule as the others: every expected value was read off the Dart
tracer (the VM-service runner behind /api/visualize) rather than
reasoned about, and tests/test_trace_dart.py keeps reading it.

These are aimed at someone arriving at Dart from JavaScript or Python
on the way to Flutter, so the wrong options are mostly what those two
languages would have done — `||` treating 0 as missing, `//` flooring,
`var` sharing one loop counter between every closure.

Two things about the Dart tracer shaped the programs:

- A breakpoint on a line that opens a closure lands inside the closure,
  not on the call that creates it. So no moment stops on such a line
  from the outside; the closure one stops inside the closure on purpose.
- Maps come back in the same notation as the JavaScript objects,
  `{ a: 2, b: 0 }` — close to what Dart's own print shows, `{a: 2, b: 0}`,
  but not identical. The map moment's choices are written that way so
  the right answer matches what the tracer reports.
"""

from __future__ import annotations

from code_coach.trace import Trace, _t


DART_TRACES: tuple[Trace, ...] = (
    _t(
        id="trace-dart-tilde-slash",
        level=1,
        name="Dividing into whole numbers",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final scores = [7, 8, 8];\n"
            "  final sum = scores.reduce((a, b) => a + b);\n"
            "  final avg = sum ~/ scores.length;\n"
            "  final exact = sum / scores.length;\n"
            "  print('$avg $exact');\n"
            "}"
        ),
        at_line=6,
        occurrence=1,
        variable="avg",
        expect="7",
        decoys=("8", "7.0", "7.666666666666667"),
        why=(
            "The sum is 23, and 23 / 3 is 7.67. `~/` is Dart's whole-number "
            "division and it throws the fraction away rather than rounding, "
            "so 7 and not 8. It hands back an int, too, so not 7.0. The "
            "plain `/` beside it always gives a double, even for 6 / 2, "
            "which is 3.0. That is why `~/` exists: it is the only way to "
            "divide two ints and get an int."
        ),
    ),
    _t(
        id="trace-dart-interpolation",
        level=2,
        name="A string built round a loop",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final names = ['Ada', 'Bo', 'Cy'];\n"
            "  var line = '';\n"
            "  for (final name in names) {\n"
            "    line += '$name.length ';\n"
            "  }\n"
            "  print(line);\n"
            "}"
        ),
        at_line=5,
        occurrence=3,
        variable="line",
        expect="'Ada.length Bo.length '",
        decoys=(
            "'3 2 '",
            "'3 2 2 '",
            "'Ada.length Bo.length Cy.length '",
        ),
        why=(
            "Two things to get right, and the four choices are every mix "
            "of them. First, `$name` takes only the name. `.length` is "
            "left behind as ordinary text, so you need `${name.length}` "
            "to get 3. Second, this is the third time the line is about "
            "to run, so only Ada and Bo have been added so far. Cy is "
            "next."
        ),
    ),
    _t(
        id="trace-dart-null-aware-zero",
        level=2,
        name="A default that only fills in null",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final saved = {'volume': 0};\n"
            "  int? volume = saved['volume'];\n"
            "  int? bass = saved['bass'];\n"
            "  volume ??= 50;\n"
            "  bass ??= 50;\n"
            "  print('$volume $bass');\n"
            "}"
        ),
        at_line=7,
        occurrence=1,
        variable="volume",
        expect="0",
        decoys=("50", "null"),
        why=(
            "`??=` assigns only when the variable is null, and 0 is not "
            "null. In JavaScript `volume = volume || 50` would have given "
            "50 here, because || treats 0 as missing, and Python's `or` "
            "does the same. That is how a saved setting of zero gets "
            "quietly reset. `bass` really was missing, so the map gave "
            "null and that one does become 50."
        ),
    ),
    _t(
        id="trace-dart-closure-in-loop",
        level=3,
        name="Callbacks made in a loop",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final calls = <void Function()>[];\n"
            "  for (var i = 1; i <= 3; i++) {\n"
            "    calls.add(() {\n"
            "      print(i);\n"
            "    });\n"
            "  }\n"
            "  for (final call in calls) call();\n"
            "}"
        ),
        at_line=5,
        occurrence=2,
        variable="i",
        expect="2",
        decoys=("4", "3", "1"),
        why=(
            "The loop has already finished and the second callback is "
            "running. Each time round, a Dart for loop makes a fresh `i`, "
            "and each closure keeps the one from its own pass, so the "
            "second one sees 2. JavaScript with `var` shares one i between "
            "all three, and they would all print 4, the value that ended "
            "the loop. In Flutter this is why a button made inside a loop "
            "remembers its own index."
        ),
    ),
    _t(
        id="trace-dart-update-if-absent",
        level=4,
        name="Counting with update",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final counts = <String, int>{};\n"
            "  for (final w in ['a', 'b', 'a', 'a']) {\n"
            "    counts.update(w, (n) => n + 1, ifAbsent: () => 0);\n"
            "  }\n"
            "  print(counts);\n"
            "}"
        ),
        at_line=6,
        occurrence=1,
        variable="counts",
        expect="{ a: 2, b: 0 }",
        decoys=("{ a: 3, b: 1 }", "{ a: 2, b: 1 }", "{ a: 3, b: 0 }"),
        why=(
            "`ifAbsent` supplies the value to store. It is not a starting "
            "value that the update function is then applied to. So the "
            "first 'a' is stored as 0 and never gets +1, and every count "
            "comes out one short: three a's give 2, one b gives 0. For "
            "counting it should be `ifAbsent: () => 1`, the value a key "
            "has after being seen once."
        ),
    ),
    _t(
        id="trace-dart-remove-in-loop",
        level=5,
        name="Removing while going round",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final nums = [1, 2, 2, 3];\n"
            "  for (var i = 0; i < nums.length; i++) {\n"
            "    if (nums[i] == 2) {\n"
            "      nums.removeAt(i);\n"
            "    }\n"
            "  }\n"
            "  print(nums);\n"
            "}"
        ),
        at_line=8,
        occurrence=1,
        variable="nums",
        expect="[1, 2, 3]",
        decoys=("[1, 3]", "[1, 2, 2, 3]", "[2, 2, 3]"),
        why=(
            "At i = 1 the first 2 is removed and everything after it moves "
            "left one place, so the second 2 is now at index 1, the one "
            "just checked. Then i++ moves on to index 2, which is the 3. "
            "The second 2 is never looked at. Go backwards, from the end "
            "to 0, or use `nums.removeWhere((n) => n == 2)`. (removeAt "
            "takes a position, not a value, which is why it isn't [2, 2, 3].)"
        ),
    ),
)
