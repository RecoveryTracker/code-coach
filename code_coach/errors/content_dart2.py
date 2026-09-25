"""More Dart crashes.

The second set, same rules as `content_dart.py`: each one compiles,
then dies while running (exit 255, "Unhandled exception:"), and every
message and line was copied from what `dart run` printed and is held to
it by tests/test_errors_dart2.py through `engine_report`.

These lean toward what a Flutter app meets once it talks to the
outside world — an empty response, a missing JSON key, a const list
someone tried to grow, a `dynamic` that turned out to be something else.
"""

from __future__ import annotations

from code_coach.errors import Crash, _c


DART_CRASHES_2: tuple[Crash, ...] = (
    _c(
        id="err-dart-range-empty",
        level=1,
        name="Asking an empty list for its first item",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final results = <String>[];\n"
            "  final best = results[0];\n"
            "  print('Best: $best');\n"
            "}"
        ),
        message="RangeError (length): Invalid value: Valid value range is empty: 0",
        line=3,
        meaning="The list was empty, so there is no index 0 to read",
        decoys=(
            "The list had a length, but it was set to zero by mistake",
            "Indexes in Dart start at 1, so 0 is not allowed",
            "results was null when the square brackets were used",
        ),
        fix=(
            "Read it back to front: the value you asked for was 0, and "
            "the range of valid indexes is empty — because the list has "
            "nothing in it. '(length)' names what the range was checked "
            "against. Dart does not hand back null for a missing index "
            "the way a Map does for a missing key, and it does not give "
            "undefined like JavaScript: it throws. Check first — "
            "`results.isEmpty ? null : results[0]`, or `results.firstOrNull` "
            "from package:collection. In Flutter this is the ListView "
            "that builds item 0 before the data has loaded."
        ),
    ),
    _c(
        id="err-dart-null-json",
        level=2,
        name="A JSON key that was not there",
        family="Dart",
        language="dart",
        code=(
            "import 'dart:convert';\n"
            "\n"
            "void main() {\n"
            "  const body = '{\"id\": 7, \"title\": \"Hello\"}';\n"
            "  final post = jsonDecode(body) as Map<String, dynamic>;\n"
            "  final author = post['author'] as String;\n"
            "  print('By $author');\n"
            "}"
        ),
        message="type 'Null' is not a subtype of type 'String' in type cast",
        line=6,
        meaning="There is no author key, so the lookup gave null",
        decoys=(
            "The author's name was a number, not text",
            "The JSON text was malformed and could not be decoded",
            "Null is a kind of String, but the cast forgot that",
        ),
        fix=(
            "'Null' with a capital N is the type of null, so the message "
            "says: the value was null, and you said String. The body "
            "has id and title and nothing called author, and a Map "
            "answers a missing key with null rather than an error — the "
            "`as String` is what turned that null into a crash. It is "
            "the twin of the int-for-String cast: same words, different "
            "first type. In a fromJson, write `post['author'] as String?` "
            "and decide what a missing one means, or check the spelling "
            "against the real response — a typo'd key reads exactly like this."
        ),
    ),
    _c(
        id="err-dart-unmodifiable",
        level=2,
        name="Adding to a const list",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  const defaults = ['dark', 'large'];\n"
            "  final settings = defaults;\n"
            "  settings.add('sound');\n"
            "  print(settings);\n"
            "}"
        ),
        message="Unsupported operation: Cannot add to an unmodifiable list",
        line=4,
        meaning="settings is the same const list, which can never change",
        decoys=(
            "final on settings means nothing can ever be added to it later",
            "Lists in Dart have a fixed size once they are made",
            "add only works on a list that is declared with var",
        ),
        fix=(
            "`const` makes the list itself frozen, not just the name. "
            "`final settings = defaults` does not copy anything: both "
            "names point at the same frozen list, so the add fails even "
            "though settings was never declared const. (And `final` is "
            "innocent — it only stops the name being pointed elsewhere.) "
            "The analyzer cannot always see this coming, which is why it "
            "compiles. Make a copy you own: `final settings = [...defaults];` "
            "or `List.of(defaults)`. List.unmodifiable and a Flutter "
            "widget's const lists fail the same way."
        ),
    ),
    _c(
        id="err-dart-int-div-zero",
        level=3,
        name="Whole-number division by zero",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final slices = 8;\n"
            "  final people = <String>[];\n"
            "  final each = slices ~/ people.length;\n"
            "  print('$each each');\n"
            "}"
        ),
        message="IntegerDivisionByZeroException",
        line=4,
        meaning="people was empty, so ~/ was asked to divide by 0",
        decoys=(
            "slices was too large a number to divide",
            "Dart cannot divide by zero at all, with any operator",
            "~/ only works on doubles, and these are ints",
        ),
        fix=(
            "The message is only the exception's name, with no value and "
            "no variable: something was divided by zero with `~/`. The "
            "line has one `~/`, and the thing on its right is "
            "people.length — an empty list. Plain `/` would not have "
            "thrown: 8 / 0 is the double Infinity, which is its own "
            "trouble later. Guard the case where there is nobody to "
            "share with — `people.isEmpty ? 0 : slices ~/ people.length` "
            "— because a count of zero is a real state, not a bug."
        ),
    ),
    _c(
        id="err-dart-no-such-method",
        level=4,
        name="A dynamic value that was not what you thought",
        family="Dart",
        language="dart",
        code=(
            "import 'dart:convert';\n"
            "\n"
            "void main() {\n"
            "  final dynamic user = jsonDecode('{\"name\": \"Ada\", \"age\": 36}');\n"
            "  final shout = user['age'].toUpperCase();\n"
            "  print(shout);\n"
            "}"
        ),
        message="NoSuchMethodError: Class 'int' has no instance method 'toUpperCase'.",
        line=5,
        meaning="user['age'] is an int, and ints have no toUpperCase",
        decoys=(
            "toUpperCase is not a method that Dart has on anything at all",
            "The user map has no key called age",
            "jsonDecode gave back a String, not a Map",
        ),
        fix=(
            "`dynamic` switches the compiler's checking off, so a call "
            "that could never work still compiles and fails only when it "
            "runs — which is the point of this one. Read the message as "
            "three facts: the value was of class int, you called "
            "toUpperCase on it, and int has no such thing. It names the "
            "method, so find it on the line and look at what is in front "
            "of it. Give JSON a type as early as you can — `as "
            "Map<String, dynamic>`, then `as int` or `as String` per "
            "field — and the analyzer would have caught this before it ran."
        ),
    ),
    _c(
        id="err-dart-stack-overflow",
        level=5,
        name="A function that never stops calling itself",
        family="Dart",
        language="dart",
        code=(
            "int countDown(int n) {\n"
            "  return countDown(n - 1);\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(countDown(3));\n"
            "}"
        ),
        message="Stack Overflow",
        line=1,
        meaning="countDown has no case where it stops, so the calls never end",
        decoys=(
            "n went below zero, and an int in Dart is not allowed to be negative",
            "3 is too large a number to count down from",
            "print was given too much text to show at once",
        ),
        fix=(
            "Every call waits for the one it made, and each waiting call "
            "takes a little memory — the stack. Nothing here ever returns, "
            "so it fills. The first frame points at line 1, where "
            "countDown is entered, because that is where the check runs "
            "out of room; the frames under it are hundreds of copies of "
            "line 2, and a trace that repeats the same line over and over "
            "is the tell. The number never matters: 3 or 3 million, it "
            "fails the same. Give it a base case first — "
            "`if (n == 0) return 0;` — so there is a way out."
        ),
    ),
)
