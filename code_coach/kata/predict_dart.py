"""Predict the output, in Dart.

Dart is the language Flutter is written in, and it looks enough like
JavaScript, Java and a little like Python that a reader from any of them
guesses with confidence — which is exactly when the guess is wrong. None
of these is exotic. Each is a line that turns up in ordinary Flutter
code and does something slightly different from what the same line does
in the language you came from.

Most of them are about types doing their job. `/` always hands back a
double. An int is 64 bits and wraps. A list compares by identity and a
record by value. A `const` list refuses changes at run time, not at
compile time. A `where` is not a list but a recipe for one, and runs
again every time it is read. Knowing these is the difference between a
build method that is cheap and one that quietly filters the same list
three times a frame.

Several answers here are for Dart on the VM, which is what `dart run`
uses and what a phone runs. Flutter on the web compiles to JavaScript,
where an int and a double are the same number: `6 / 2` prints `3`, an int
never wraps, and `2.0 is int` is true. The explanations say so where it
matters, because an app that behaves differently on the web is one of
the ways this bites.

Every expected output was typed out first and then checked against
Dart 3.7, and the suite keeps checking — same way round as the rest of
predict.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p


DART_PUZZLES: tuple[Puzzle, ...] = (
    _p(
        id="predict-dart-slash",
        level=1,
        language="dart",
        name="Dividing two whole numbers",
        family="Dart",
        code=(
            "void main() {\n"
            "  print(7 / 2);\n"
            "  print(6 / 2);\n"
            "  print(6 ~/ 2);\n"
            "}"
        ),
        expect="3.5\n3.0\n3",
        why=(
            "`/` always hands back a double, even when both sides are "
            "ints and it divides exactly, and a double always prints "
            "with its decimal point — so 6 / 2 is 3.0. `~/` is the "
            "operator for a whole-number answer. This is why "
            "`int half = total / 2;` will not compile in Flutter: the "
            "right-hand side is a double, whatever the numbers are."
        ),
    ),
    _p(
        id="predict-dart-interpolation",
        level=2,
        language="dart",
        name="A dollar sign and what follows it",
        family="Dart",
        code=(
            "void main() {\n"
            "  var a = 1, b = 2;\n"
            "  var name = 'Ada';\n"
            "  print('$a$b ${a + b}');\n"
            "  print('$name.length ${name.length}');\n"
            "  print('-' * 3 + name);\n"
            "}"
        ),
        expect="12 3\nAda.length 3\n---Ada",
        why=(
            "`$` takes a single name and stops at the first thing that "
            "is not part of one, so `$name.length` is the name followed "
            "by the text `.length`. Anything more than a bare name — a "
            "sum, a property, a call — needs the braces. And a string "
            "times a number repeats it, as in Python; JavaScript would "
            "give NaN. Only that way round, though: `3 * '-'` does not "
            "compile."
        ),
    ),
    _p(
        id="predict-dart-final-const",
        level=2,
        language="dart",
        name="final, and the list behind it",
        family="Dart",
        code=(
            "void main() {\n"
            "  final a = [1, 2];\n"
            "  a.add(3);\n"
            "  print(a);\n"
            "  const b = [1, 2];\n"
            "  try {\n"
            "    b.add(3);\n"
            "  } on UnsupportedError {\n"
            "    print('refused');\n"
            "  }\n"
            "  print(b);\n"
            "}"
        ),
        expect="[1, 2, 3]\nrefused\n[1, 2]",
        why=(
            "`final` fixes the name, not the thing it names: `a` can "
            "never point at another list, but the list itself changes "
            "freely. `const` goes all the way down and the list cannot "
            "change at all — and the refusal comes when the program "
            "runs, not when it compiles, because `add` exists on every "
            "list. A `final List` field in a Flutter widget is still a "
            "list anyone can add to."
        ),
    ),
    _p(
        id="predict-dart-null-aware",
        level=2,
        language="dart",
        name="A key that is not there",
        family="Dart",
        code=(
            "void main() {\n"
            "  var names = {'a': 'Ada'};\n"
            "  print(names['b'] ?? 'guest');\n"
            "  print(names['b']?.length);\n"
            "  names['a'] ??= 'Zed';\n"
            "  names['b'] ??= 'Bob';\n"
            "  print(names);\n"
            "}"
        ),
        expect="guest\nnull\n{a: Ada, b: Bob}",
        why=(
            "A missing key is null, not an error as in Python — which is "
            "why a map lookup has a nullable type. `??` supplies a "
            "fallback, `?.` gives up and hands back null instead of "
            "throwing, and `??=` assigns only when the thing is null, "
            "so Ada survives. A printed map shows no quotes round its "
            "strings, which makes `{a: 1}` and `{'a': 1}` look the same "
            "in a log."
        ),
    ),
    _p(
        id="predict-dart-list-filled",
        level=3,
        language="dart",
        name="One row, filled in three times",
        family="Dart",
        code=(
            "void main() {\n"
            "  var grid = List.filled(3, <int>[]);\n"
            "  grid[0].add(9);\n"
            "  print(grid);\n"
            "  var rows = List.generate(3, (_) => <int>[]);\n"
            "  rows[0].add(9);\n"
            "  print(rows);\n"
            "}"
        ),
        expect="[[9], [9], [9]]\n[[9], [], []]",
        why=(
            "`List.filled` evaluates its value once and puts that one "
            "object in every slot, so all three rows are the same list. "
            "`List.generate` calls its function once per slot and gets "
            "a new list each time. Filled is right for numbers and "
            "strings, which cannot be changed, and wrong for anything "
            "that can — a game board is the classic way to find out."
        ),
    ),
    _p(
        id="predict-dart-equality",
        level=3,
        language="dart",
        name="Two lists that look the same",
        family="Dart",
        code=(
            "void main() {\n"
            "  var a = [1, 2];\n"
            "  var b = [1, 2];\n"
            "  print(a == b);\n"
            "  print((1, 2) == (1, 2));\n"
            "  print(const [1, 2] == const [1, 2]);\n"
            "}"
        ),
        expect="false\ntrue\ntrue",
        why=(
            "A list's `==` asks whether it is the same object, not "
            "whether it holds the same things — Python would say True "
            "for the first. A record compares by its fields, so equal "
            "contents are equal. The last one is identity again, and "
            "true because two identical constants are made into one "
            "object. To compare list contents, use `listEquals` from "
            "Flutter's foundation library."
        ),
    ),
    _p(
        id="predict-dart-cascade",
        level=3,
        language="dart",
        name="What a cascade hands back",
        family="Dart",
        code=(
            "void main() {\n"
            "  var nums = [3, 1, 2]..sort()..add(0);\n"
            "  print(nums);\n"
            "  var loud = 'hi'..toUpperCase();\n"
            "  print(loud);\n"
            "}"
        ),
        expect="[1, 2, 3, 0]\nhi",
        why=(
            "`..` calls the method and then hands back the thing it was "
            "called on, throwing the method's own result away. That is "
            "what makes `[3, 1, 2]..sort()` useful, since sort returns "
            "nothing. It is also why the second line does nothing: "
            "toUpperCase built a new string, and the cascade dropped it "
            "and gave back the original."
        ),
    ),
    _p(
        id="predict-dart-negative-modulo",
        level=4,
        language="dart",
        name="Dividing a negative, the Dart way",
        family="Dart",
        code=(
            "void main() {\n"
            "  print(-7 ~/ 2);\n"
            "  print(-7 % 2);\n"
            "  print(7 % -2);\n"
            "  print((-7).remainder(2));\n"
            "}"
        ),
        expect="-3\n1\n1\n-1",
        why=(
            "`~/` rounds towards zero, like JavaScript and unlike "
            "Python's `//`, which would give -4. But `%` never comes "
            "back negative, whatever the signs — unlike JavaScript, "
            "where -7 % 2 is -1, and unlike Python, where 7 % -2 is -1. "
            "So the two do not pair up the way they do in Python; "
            "`remainder` is the one that goes with `~/`."
        ),
    ),
    _p(
        id="predict-dart-late",
        level=4,
        language="dart",
        name="late, and when it happens",
        family="Dart",
        code=(
            "int load(String name) {\n"
            "  print('loading $name');\n"
            "  return name.length;\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  late final a = load('first');\n"
            "  final b = load('second');\n"
            "  print('ready');\n"
            "  print(a + b);\n"
            "  print(a);\n"
            "}"
        ),
        expect="loading second\nready\nloading first\n11\n5",
        why=(
            "A `late` variable with an initialiser does not run it "
            "where it is written. It runs the first time the variable "
            "is read, and only that once — the second read uses the "
            "value it already has. So the lines print in the order the "
            "values are used, not the order they are declared. It is "
            "how Flutter state puts off expensive work until it is "
            "needed."
        ),
    ),
    _p(
        id="predict-dart-where-lazy",
        level=5,
        language="dart",
        name="A filter that runs every time you look",
        family="Dart",
        code=(
            "void main() {\n"
            "  var calls = 0;\n"
            "  var evens = [1, 2, 3, 4].where((n) {\n"
            "    calls++;\n"
            "    return n.isEven;\n"
            "  });\n"
            "  print(calls);\n"
            "  print(evens);\n"
            "  print(evens.length);\n"
            "  print(calls);\n"
            "}"
        ),
        expect="0\n(2, 4)\n2\n8",
        why=(
            "`where` does no work when it is called. It returns a lazy "
            "Iterable — printed with round brackets, not square ones — "
            "and the test runs each time something reads it. Printing "
            "read it once and asking its length read it all over again, "
            "so four items cost eight calls. Add `.toList()` to filter "
            "once and keep the answer, especially in a build method."
        ),
    ),
    _p(
        id="predict-dart-switch",
        level=5,
        language="dart",
        name="Which pattern catches it",
        family="Dart",
        code=(
            "String kind(Object v) => switch (v) {\n"
            "      int n when n < 0 => 'negative',\n"
            "      int() => 'int',\n"
            "      (_, _) => 'pair',\n"
            "      [_, ...] => 'list',\n"
            "      _ => 'other',\n"
            "    };\n"
            "void main() {\n"
            "  print(kind(-1));\n"
            "  print(kind(2.0));\n"
            "  print([kind((1, 2)), kind([])]);\n"
            "}"
        ),
        expect="negative\nother\n[pair, other]",
        why=(
            "A switch expression tries its arms in order and the first "
            "match wins. 2.0 is a double, not an int, so it falls to the "
            "end — though on Flutter web, where both are JavaScript "
            "numbers, it would say int. `[_, ...]` means a list with at "
            "least one element, so the empty list is not one. The guard "
            "after `when` is checked only once the type has matched."
        ),
    ),
    _p(
        id="predict-dart-int-wraps",
        level=5,
        language="dart",
        name="The biggest int, plus one",
        family="Dart",
        code=(
            "void main() {\n"
            "  var big = 9223372036854775807;\n"
            "  var next = big + 1;\n"
            "  print(next > big);\n"
            "  print(next.isNegative);\n"
            "  print(big * 2);\n"
            "}"
        ),
        expect="false\ntrue\n-2",
        why=(
            "An int on the VM, and on a phone, is 64 bits. Past the "
            "largest one it wraps round to the most negative, silently "
            "— no error, no bigger number as Python would give. Doubling "
            "the largest is two short of 2 to the 64, which wraps to -2. "
            "On Flutter web the same code loses precision instead of "
            "wrapping, so the two builds of one app can disagree."
        ),
    ),
)
