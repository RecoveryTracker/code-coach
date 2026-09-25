"""More Dart moments.

The second set, same rule as `content_dart.py`: every expected value
was read off the Dart tracer rather than reasoned about, and
tests/test_trace_dart2.py keeps reading it.

The tracer quirks that shaped them:

- A breakpoint on a line that opens a closure lands inside the closure,
  so the fold moment stops on the closure's body on purpose, and the
  putIfAbsent moment asks about the map on the line after them all.
- Objects render as `?`, so the class moment copies the field into a
  local and asks about that.
"""

from __future__ import annotations

from code_coach.trace import Trace, _t


DART_TRACES_2: tuple[Trace, ...] = (
    _t(
        id="trace-dart-while-break",
        level=1,
        name="A counter after a break",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final rolls = [3, 5, 6, 2, 6];\n"
            "  var tries = 0;\n"
            "  while (tries < rolls.length) {\n"
            "    if (rolls[tries] == 6) break;\n"
            "    tries++;\n"
            "  }\n"
            "  print(tries);\n"
            "}"
        ),
        at_line=8,
        occurrence=1,
        variable="tries",
        expect="2",
        decoys=("3", "4", "5"),
        why=(
            "The first 6 is at index 2. When the loop reaches it, `break` "
            "leaves straight away, so the `tries++` under it never runs "
            "that time round: tries stays at 2, the index of the 6, not "
            "3, the count of rolls looked at. And break stops at the "
            "first match, so the second 6 at index 4 is never reached. "
            "5 would be the answer only if nothing had matched."
        ),
    ),
    _t(
        id="trace-dart-insert-front",
        level=2,
        name="Inserting at the front each time",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final recent = <int>[];\n"
            "  for (var page = 1; page <= 4; page++) {\n"
            "    recent.insert(0, page);\n"
            "  }\n"
            "  print(recent);\n"
            "}"
        ),
        at_line=4,
        occurrence=4,
        variable="recent",
        expect="[3, 2, 1]",
        decoys=("[1, 2, 3]", "[4, 3, 2, 1]", "[1, 2, 3, 4]"),
        why=(
            "Two things. `insert(0, x)` puts x in front of everything "
            "already there, so each new page pushes the older ones "
            "right and the list comes out newest first — the opposite "
            "of add. And the question stops the fourth time the line is "
            "about to run, before 4 has gone in, so only 1, 2 and 3 are "
            "there. A recent-history list in an app is built exactly "
            "like this."
        ),
    ),
    _t(
        id="trace-dart-fold-midway",
        level=3,
        name="Inside a fold, part way through",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final prices = [4, 10, 6];\n"
            "  final total = prices.fold<int>(0, (sum, p) {\n"
            "    return sum + p;\n"
            "  });\n"
            "  print(total);\n"
            "}"
        ),
        at_line=4,
        occurrence=2,
        variable="sum",
        expect="4",
        decoys=("0", "14", "20"),
        why=(
            "fold calls the function once per item, handing it the "
            "running total so far and the next item. The first call gets "
            "the starting 0 and 4 and returns 4. That 4 becomes `sum` "
            "for the second call, which is where this stops — before it "
            "adds the 10. So sum is 4, not 14 (that is what this call "
            "returns) and not 20 (the answer at the end). Unlike reduce, "
            "fold also works on an empty list: it just gives back the 0."
        ),
    ),
    _t(
        id="trace-dart-split-empty",
        level=3,
        name="Splitting where two commas meet",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final csv = 'ada,,bo';\n"
            "  final parts = csv.split(',');\n"
            "  final back = parts.join(' ');\n"
            "  print(back);\n"
            "}"
        ),
        at_line=4,
        occurrence=1,
        variable="parts",
        expect="['ada', '', 'bo']",
        decoys=("['ada', 'bo']", "['ada,,bo']", "['ada', ',', 'bo']"),
        why=(
            "split cuts at every comma and keeps whatever lies between, "
            "even when that is nothing. Between the two commas there is "
            "an empty string, so three parts, not two — and the commas "
            "themselves are thrown away. That empty part is still there "
            "on the next line: joining with a space gives 'ada  bo' with "
            "two spaces. To drop the blanks, "
            "`.where((s) => s.isNotEmpty)` after the split."
        ),
    ),
    _t(
        id="trace-dart-put-if-absent",
        level=4,
        name="putIfAbsent on a key that is already there",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final seats = <String, String>{};\n"
            "  seats.putIfAbsent('A1', () => 'Ada');\n"
            "  seats.putIfAbsent('A2', () => 'Bo');\n"
            "  seats.putIfAbsent('A1', () => 'Cy');\n"
            "  print(seats);\n"
            "}"
        ),
        at_line=6,
        occurrence=1,
        variable="seats",
        expect="{ A1: 'Ada', A2: 'Bo' }",
        decoys=(
            "{ A1: 'Cy', A2: 'Bo' }",
            "{ A2: 'Bo', A1: 'Cy' }",
            "{ A1: 'Ada', A2: 'Bo', A1: 'Cy' }",
        ),
        why=(
            "putIfAbsent only puts when the key is absent. A1 is already "
            "Ada's, so the third call does nothing at all — its function "
            "is not even called — and the map keeps Ada. `seats['A1'] = "
            "'Cy'` would have replaced her. A map cannot hold the same key "
            "twice, and Dart's maps keep the order keys were first added, "
            "so A1 stays in front. It is the first-come seat: whoever "
            "claimed it first keeps it."
        ),
    ),
    _t(
        id="trace-dart-shadowed-field",
        level=5,
        name="A parameter with the field's name",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final w = Wallet();\n"
            "  w.spend(5);\n"
            "  final left = w.balance;\n"
            "  print(left);\n"
            "}\n"
            "class Wallet {\n"
            "  int balance = 20;\n"
            "  void spend(int balance) => balance -= balance;\n"
            "}"
        ),
        at_line=5,
        occurrence=1,
        variable="left",
        expect="20",
        decoys=("15", "0", "5"),
        why=(
            "Inside spend, the name balance means the parameter, which "
            "hides the field with the same name. So `balance -= balance` "
            "is 5 minus 5, stored back into the parameter, and thrown "
            "away when spend returns. The field is never touched and "
            "stays 20. Dart lets you leave out `this.`, which is handy "
            "until a parameter shares a name. Write `this.balance -= "
            "amount` — or name the parameter amount — and it gives 15."
        ),
    ),
)
