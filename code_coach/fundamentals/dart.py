"""Dart fundamentals: the syntax the LeetCode patterns assume you already know.

Ordered so each snippet only uses ideas from the ones above it. Levels are the
chunk sizes: 1–2 single lines, 3 two-liners, 4 blocks, 5 whole functions.
"""

from __future__ import annotations

from code_coach.fundamentals.base import (
    FundamentalsBank,
    FundamentalsClass,
    Snippet,
    register,
)


def _s(code: str, tip: str, level: int = 1) -> Snippet:
    return Snippet(code=code, tip=tip, level=level)


_FOUNDATIONS = FundamentalsClass(
    id="foundations",
    name="Foundations",
    description="Values, names, printing, and your first functions.",
    snippets=(
        _s("print('Hello, world!');", "Every statement ends with a semicolon."),
        _s("var name = 'Alex';", "`var` lets Dart work out the type from the value."),
        _s("var age = 30;", "This one is an int, inferred the same way."),
        _s("String city = 'Denver';",
           "You can write the type instead — clearer in a signature."),
        _s("int count = 0;", "Dart's whole-number type."),
        _s("double price = 4.99;", "And its decimal type. `int` won't hold 4.99."),
        _s("bool isReady = true;", "Booleans are `true` / `false`, lowercase."),
        _s("final total = 42;",
           "`final` means assign once. Prefer it when nothing reassigns."),
        _s("const pi = 3.14;",
           "`const` is stronger: known at compile time, not just fixed."),
        _s("print(name);", "Print a variable by naming it, no quotes."),
        _s("print('Hi, \\$name!');",
           r"$name drops the value into the string — interpolation."),
        _s("print('Total: \\${count + 1}');",
           r"${...} interpolates a whole expression, not just a name."),
        _s("var nums = [1, 2, 3];", "A List — Dart's ordered collection.", 2),
        _s("var scores = <String, int>{};",
           "An empty Map needs its types spelled out.", 2),
        _s("var seen = <int>{};", "A Set: unordered, no duplicates.", 2),
        _s("nums.add(4);", "Append to a List.", 2),
        _s("print(nums.length);", "`length` is a property, not a method call.", 2),
        _s("print(nums[0]);", "Index from zero.", 2),
        _s("scores['alex'] = 10;", "Put a key/value into a Map.", 2),
        _s("print(scores['alex']);",
           "Reading a missing key gives null, not an error.", 2),
        _s(
            "var name = 'Alex';\nprint('Hello, \\$name!');",
            "Declare, then use — the two halves of almost every program.",
            3,
        ),
        _s(
            "var nums = [1, 2, 3];\nprint(nums.length);",
            "Build a collection, then ask it something.",
            3,
        ),
        _s(
            "int double(int n) {\n  return n * 2;\n}",
            "A function: return type, name, parameters, body.",
            4,
        ),
        _s(
            "int add(int a, int b) {\n  return a + b;\n}",
            "Two parameters, separated by a comma.",
            4,
        ),
        _s(
            "int triple(int n) => n * 3;",
            "`=>` is shorthand for a body that's a single expression.",
            4,
        ),
        _s(
            "void greet(String name) {\n  print('Hello, \\$name!');\n}",
            "`void` means it does something rather than hands something back.",
            4,
        ),
        _s(
            "int add(int a, int b) {\n  return a + b;\n}\n\nvoid main() {\n"
            "  print(add(7, 12));\n}",
            "`main` is where a Dart program starts.",
            5,
        ),
        _s(
            "String shout(String words) {\n  return words.toUpperCase();\n}\n\n"
            "void main() {\n  print(shout('hello'));\n}",
            "Define, then call from main — the shape of every exercise here.",
            5,
        ),
        _s(
            "void main() {\n  var nums = [3, 1, 2];\n  nums.sort();\n"
            "  print(nums);\n}",
            "`sort()` rearranges the list in place and returns nothing.",
            5,
        ),
        _s(
            "String greet(String name) {\n"
            "  return 'Hello, $name!';\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(greet('Alex'));\n"
            "}",
            "A $ inserts a variable straight into a string.",
            5,
        ),
        _s(
            "double average(List<int> nums) {\n"
            "  var total = 0;\n"
            "  for (final n in nums) {\n"
            "    total += n;\n"
            "  }\n"
            "  return total / nums.length;\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(average([2, 4, 6]));\n"
            "}",
            "/ always gives a double, even between two ints.",
            5,
        ),
        _s(
            "int area(int w, int h) => w * h;\n"
            "\n"
            "void main() {\n"
            "  print(area(3, 4));\n"
            "}",
            "=> is shorthand for a body that is one expression.",
            5,
        ),
        _s(
            "String describe({required String name, required int age}) {\n"
            "  return '$name is $age';\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(describe(name: 'Sam', age: 30));\n"
            "}",
            "Named parameters are ordinary in Dart, and required is a keyword.",
            5,
        ),
        _s(
            "class Point {\n"
            "  final int x;\n"
            "  final int y;\n"
            "  Point(this.x, this.y);\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  final p = Point(1, 2);\n"
            "  print(p.x);\n"
            "}",
            "this.x in the parameter list assigns the field for you.",
            5,
        ),
        _s(
            "T? firstOrNull<T>(List<T> items) {\n"
            "  return items.isEmpty ? null : items.first;\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(firstOrNull([10, 20]));\n"
            "}",
            "T? says the answer may be absent, and the compiler holds you to it.",
            5,
        ),
    ),
)


_DECISIONS = FundamentalsClass(
    id="decisions",
    name="Decisions",
    description="Comparing values and branching on the answer.",
    snippets=(
        _s("if (age > 18) {", "The condition goes in parentheses."),
        _s("if (count == 0) {", "`==` compares; `=` assigns."),
        _s("if (name != 'Alex') {", "`!=` is 'not equal to'."),
        _s("} else {", "The other branch."),
        _s("} else if (score > 50) {", "Chain another test on."),
        _s("if (isReady && count > 0) {", "`&&` needs both sides true.", 2),
        _s("if (isDone || isEmpty) {", "`||` needs only one.", 2),
        _s("if (!isReady) {", "`!` flips a boolean.", 2),
        _s("var label = age >= 18 ? 'adult' : 'minor';",
           "The ternary: condition ? this : that.", 2),
        _s("var shown = name ?? 'guest';",
           "`??` supplies a fallback when the left side is null.", 2),
        _s(
            "if (score > 50) {\n  print('pass');\n}",
            "Braces hold everything that runs when it's true.",
            3,
        ),
        _s(
            "if (score > 50) {\n  print('pass');\n} else {\n  print('fail');\n}",
            "One branch or the other, never both.",
            4,
        ),
        _s(
            "if (n > 0) {\n  print('positive');\n} else if (n < 0) {\n"
            "  print('negative');\n} else {\n  print('zero');\n}",
            "Tested in order; the first true one wins.",
            4,
        ),
        _s(
            "switch (day) {\n  case 'sat':\n  case 'sun':\n    print('weekend');\n"
            "    break;\n  default:\n    print('weekday');\n}",
            "`switch` compares one value against several cases.",
            4,
        ),
        _s(
            "String grade(int score) {\n  if (score >= 90) {\n    return 'A';\n"
            "  }\n  if (score >= 80) {\n    return 'B';\n  }\n  return 'C';\n}\n\n"
            "void main() {\n  print(grade(85));\n}",
            "An early return ends the function then and there.",
            5,
        ),
        _s(
            "bool isEven(int n) {\n  return n % 2 == 0;\n}\n\nvoid main() {\n"
            "  print(isEven(4));\n}",
            "`%` is the remainder — the usual way to test evenness.",
            5,
        ),
        _s(
            "int biggest(int a, int b) {\n  if (a > b) {\n    return a;\n  }\n"
            "  return b;\n}\n\nvoid main() {\n  print(biggest(3, 9));\n}",
            "No else needed: returning already left the function.",
            5,
        ),
        _s(
            "String grade(int score) {\n"
            "  if (score >= 90) return 'A';\n"
            "  if (score >= 80) return 'B';\n"
            "  return 'C';\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(grade(85));\n"
            "}",
            "Early returns keep the branches flat.",
            5,
        ),
        _s(
            "String sign(int n) {\n"
            "  if (n > 0) return 'positive';\n"
            "  if (n < 0) return 'negative';\n"
            "  return 'zero';\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(sign(-4));\n"
            "}",
            "Dart requires every path to return, and checks that it does.",
            5,
        ),
        _s(
            "bool canVote(int age, bool citizen) {\n"
            "  return age >= 18 && citizen;\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(canVote(20, true));\n"
            "}",
            "Conditions must be actual booleans; there is no truthiness.",
            5,
        ),
        _s(
            "String label(int n) => n.isEven ? 'even' : 'odd';\n"
            "\n"
            "void main() {\n"
            "  print(label(7));\n"
            "}",
            "isEven and isOdd are properties on int, not functions.",
            5,
        ),
        _s(
            "String greetOrDefault(String? name) {\n"
            "  final who = name ?? 'stranger';\n"
            "  return 'Hi, $who';\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(greetOrDefault(null));\n"
            "}",
            "?? supplies the fallback when the value is null.",
            5,
        ),
        _s(
            "String dayType(String day) {\n"
            "  switch (day) {\n"
            "    case 'Sat':\n"
            "    case 'Sun':\n"
            "      return 'weekend';\n"
            "    default:\n"
            "      return 'weekday';\n"
            "  }\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(dayType('Sun'));\n"
            "}",
            "Empty cases stack up; a case with a body must not fall through.",
            5,
        ),
    ),
)


_LOOPS = FundamentalsClass(
    id="loops",
    name="Loops",
    description="Repeating work, and stopping at the right moment.",
    snippets=(
        _s("for (var i = 0; i < 5; i++) {", "Start, keep-going test, step."),
        _s("for (final n in nums) {", "Walk the values directly."),
        _s("while (count > 0) {", "Repeat while the condition holds."),
        _s("count++;", "Add one. `count--` takes one away."),
        _s("total += n;", "Shorthand for total = total + n.", 2),
        _s("break;", "Leave the loop immediately.", 2),
        _s("continue;", "Skip to the next turn of the loop.", 2),
        _s("for (var i = nums.length - 1; i >= 0; i--) {",
           "Counting down: start at the end, step back.", 2),
        _s("nums.forEach(print);", "Every List can walk itself.", 2),
        _s(
            "for (final n in nums) {\n  print(n);\n}",
            "The most common loop you'll write in Dart.",
            3,
        ),
        _s(
            "var total = 0;\nfor (final n in nums) {\n  total += n;\n}",
            "An accumulator: start empty, add as you go.",
            4,
        ),
        _s(
            "var count = 3;\nwhile (count > 0) {\n  print(count);\n  count--;\n}",
            "Something inside must change, or it never ends.",
            4,
        ),
        _s(
            "for (var i = 0; i < nums.length; i++) {\n  print('\\$i: \\${nums[i]}');\n}",
            "Use the index form when you need the position too.",
            4,
        ),
        _s(
            "for (var r = 0; r < 3; r++) {\n  for (var c = 0; c < 3; c++) {\n"
            "    print('\\$r,\\$c');\n  }\n}",
            "A nested loop walks a grid — the inner one runs fully each time.",
            4,
        ),
        _s(
            "int sum(List<int> nums) {\n  var total = 0;\n  for (final n in nums) {\n"
            "    total += n;\n  }\n  return total;\n}\n\n"
            "void main() {\n  print(sum([1, 2, 3, 4]));\n}",
            "The accumulator pattern, wrapped up as a function.",
            5,
        ),
        _s(
            "int countdown(int n) {\n  while (n > 0) {\n    print(n);\n    n--;\n  }\n"
            "  return 0;\n}\n\nvoid main() {\n  countdown(3);\n}",
            "A while loop that changes its own condition.",
            5,
        ),
        _s(
            "int biggest(List<int> nums) {\n  var best = nums[0];\n"
            "  for (final n in nums) {\n    if (n > best) {\n      best = n;\n"
            "    }\n  }\n  return best;\n}\n\n"
            "void main() {\n  print(biggest([3, 9, 4]));\n}",
            "Loop plus decision — most algorithms are this shape.",
            5,
        ),
        _s(
            "int total(List<int> nums) {\n"
            "  var sum = 0;\n"
            "  for (final n in nums) {\n"
            "    sum += n;\n"
            "  }\n"
            "  return sum;\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(total([1, 2, 3, 4]));\n"
            "}",
            "final in a loop means each turn gets its own value.",
            5,
        ),
        _s(
            "List<int> countdown(int from) {\n"
            "  final out = <int>[];\n"
            "  for (var i = from; i > 0; i--) {\n"
            "    out.add(i);\n"
            "  }\n"
            "  return out;\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(countdown(3));\n"
            "}",
            "<int>[] is an empty list that knows what it holds.",
            5,
        ),
        _s(
            "int? firstNegative(List<int> nums) {\n"
            "  for (final n in nums) {\n"
            "    if (n < 0) return n;\n"
            "  }\n"
            "  return null;\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(firstNegative([3, 1, -2, 5]));\n"
            "}",
            "The ? is what lets the function return null at all.",
            5,
        ),
        _s(
            "List<int> doubled(List<int> nums) {\n"
            "  return nums.map((n) => n * 2).toList();\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(doubled([1, 2, 3]));\n"
            "}",
            "map is lazy in Dart, so toList is what actually runs it.",
            5,
        ),
        _s(
            "List<int> evens(List<int> nums) {\n"
            "  return nums.where((n) => n.isEven).toList();\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(evens([1, 2, 3, 4]));\n"
            "}",
            "Dart calls it where, not filter.",
            5,
        ),
        _s(
            "int tally(List<String> words) {\n"
            "  final counts = <String, int>{};\n"
            "  for (final word in words) {\n"
            "    counts[word] = (counts[word] ?? 0) + 1;\n"
            "  }\n"
            "  return counts['a'] ?? 0;\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(tally(['a', 'b', 'a']));\n"
            "}",
            "A missing key gives null, so ?? 0 starts the count.",
            5,
        ),
    ),
)


register(
    FundamentalsBank(
        language="dart",
        classes=(_FOUNDATIONS, _DECISIONS, _LOOPS),
    )
)
