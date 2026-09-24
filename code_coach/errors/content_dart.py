"""The Dart crashes.

The ones a Flutter app actually dies of. Every one compiles cleanly —
the analyzer is happy, the build succeeds — and then fails while it
runs, which is the whole difficulty: the tooling that caught everything
else said nothing about these.

Every message and line number here was copied out of what `dart run`
actually printed, and the suite runs each program and holds it to that.

How Dart reports a crash
------------------------
Not the way Node or Python do, and it is worth knowing the shape:

    Unhandled exception:
    Bad state: No element
    #0      ListBase.firstWhere (dart:collection/list.dart:132:5)
    #1      main (file:///C:/.../program.dart:6:20)

The message is the line after "Unhandled exception:", and it often does
not contain the word Error at all. The frames under it are numbered,
and the first one is frequently inside the SDK — `dart:collection`,
`dart:core-patch` — because the SDK is what noticed the problem. The
line that is yours is the first frame that names your own file, and
the number after `.dart:` is the line.

The plain-words readings are written by hand, and so are the wrong
options — each is a misreading people really make, usually by taking a
word in the message at face value ("concurrent", "bad state") or by
blaming the thing the message never mentions.
"""

from __future__ import annotations

from code_coach.errors import Crash, _c


# -- Dart -----------------------------------------------------

DART_CRASHES: tuple[Crash, ...] = (
    _c(
        id="err-dart-null-check",
        level=1,
        name="A ! on something that was null",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final ages = <String, int>{'ada': 36, 'alan': 41};\n"
            "  final name = 'grace';\n"
            "  final age = ages[name]!;\n"
            "  print('$name is $age');\n"
            "}"
        ),
        message="Null check operator used on a null value",
        line=4,
        meaning="ages[name] was null, and the ! insists it is not",
        decoys=(
            "The map ages was itself null when it was read",
            "name was declared but never given a value",
            "print cannot put an int inside a string using $ like that",
        ),
        fix=(
            "`!` is a promise to the compiler: this is not null, trust "
            "me. Looking up a key that is not in a Map does not throw in "
            "Dart — it hands back null, and the `!` turns that null into "
            "this crash. The message names only the operator, never the "
            "map or the key, so find the `!` on the line and ask what was "
            "in front of it. `ages[name] ?? 0` gives a default instead. "
            "In Flutter this is the one you meet from `snapshot.data!` "
            "before the data has arrived."
        ),
    ),
    _c(
        id="err-dart-format",
        level=2,
        name="Text that is not a whole number",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final typed = ['3', '12', '4.5'];\n"
            "  var total = 0;\n"
            "  for (final text in typed) {\n"
            "    total += int.parse(text);\n"
            "  }\n"
            "  print(total);\n"
            "}"
        ),
        message="FormatException: Invalid radix-10 number (at character 1)",
        line=5,
        meaning="int.parse was given text that is not a whole number",
        decoys=(
            "int.parse needs a radix argument, and none was given",
            "The first character of every string is not allowed",
            "The total grew too big for an int to hold",
        ),
        fix=(
            "Radix-10 just means base ten — ordinary digits — and "
            "FormatException means the text was not the shape asked "
            "for. It is not about the loop or the list: one string, "
            "'4.5', has a decimal point, and int.parse takes whole "
            "numbers only. In a terminal the two lines under the message "
            "echo the text that failed, which is the quickest part to "
            "read. Anything a person typed deserves `int.tryParse(text)`, "
            "which gives null instead of crashing; for decimals, "
            "double.parse."
        ),
    ),
    _c(
        id="err-dart-late",
        level=2,
        name="A late field read before anything set it",
        family="Dart",
        language="dart",
        code=(
            "class Profile {\n"
            "  late String name;\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  final profile = Profile();\n"
            "  print(profile.name.length);\n"
            "}"
        ),
        message="LateInitializationError: Field 'name' has not been initialized.",
        line=7,
        meaning="name was read before any line gave it a value",
        decoys=(
            "name was set to null, which a String cannot hold",
            "Profile() cannot be built because it has no constructor",
            "There is no field called name on Profile",
        ),
        fix=(
            "`late` tells the compiler: this will be set before anyone "
            "reads it, so stop checking. Nothing checks, until the read "
            "happens and it was never set. 'Field' means a member of a "
            "class; a late local variable says 'Local' instead. Set it "
            "before the first read — in the constructor, or in a Flutter "
            "State, in initState rather than in build or a callback. If "
            "it genuinely might not be there yet, make it `String?` "
            "instead of late, so the compiler makes you check."
        ),
    ),
    _c(
        id="err-dart-cast",
        level=3,
        name="A cast the value does not fit",
        family="Dart",
        language="dart",
        code=(
            "import 'dart:convert';\n"
            "\n"
            "void main() {\n"
            "  const body = '{\"name\": \"Ada\", \"age\": 36}';\n"
            "  final user = jsonDecode(body) as Map<String, dynamic>;\n"
            "  final age = user['age'] as String;\n"
            "  print('Age: $age');\n"
            "}"
        ),
        message="type 'int' is not a subtype of type 'String' in type cast",
        line=6,
        meaning="user['age'] held an int, and an int is not a String",
        decoys=(
            "The JSON text was malformed and jsonDecode rejected it",
            "There is no key called age, so the lookup gave nothing",
            "The decoded JSON could not be treated as a Map at all",
        ),
        fix=(
            "Read it as: the value was an int; you said String. `as` "
            "never converts anything — it checks, and throws if the "
            "check fails. JSON numbers decode to int or double, so this "
            "wants `user['age'] as int`, or `.toString()` if text is "
            "really what you need. The message names the two types and "
            "never the key, so look for the `as String` on the line. Its "
            "twin, type 'Null' is not a subtype of type 'String', is the "
            "same line with a key that was missing or misspelled — every "
            "Flutter fromJson meets both."
        ),
    ),
    _c(
        id="err-dart-no-element",
        level=4,
        name="Asking for the one that matches when none does",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final users = [\n"
            "    {'id': 1, 'name': 'Ada'},\n"
            "    {'id': 2, 'name': 'Alan'},\n"
            "  ];\n"
            "  final me = users.firstWhere((u) => u['id'] == 3);\n"
            "  print(me['name']);\n"
            "}"
        ),
        message="Bad state: No element",
        line=6,
        meaning="No user matched, so firstWhere had nothing to return",
        decoys=(
            "The users list was empty when firstWhere ran",
            "Something on an earlier line left the whole program broken",
            "The user that was found has no name to print",
        ),
        fix=(
            "'Bad state' is how Dart prints a StateError: you asked for "
            "something that makes no sense right now, and 'No element' "
            "says what was missing. first, last, single and firstWhere "
            "all throw it when there is nothing to give — and here the "
            "list is not empty, nothing in it matched. The message never "
            "mentions the list, the search or the id, which is why it is "
            "so hard to read the first time. Use "
            "`users.where((u) => u['id'] == 3).firstOrNull` and handle "
            "null: in a lookup by id, 'not found' is a normal answer, not "
            "a crash."
        ),
    ),
    _c(
        id="err-dart-concurrent",
        level=5,
        name="Removing from a list while walking it",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final cart = ['apple', 'bread', 'milk'];\n"
            "  for (final item in cart) {\n"
            "    if (item == 'bread') {\n"
            "      cart.remove(item);\n"
            "    }\n"
            "  }\n"
            "  print(cart);\n"
            "}"
        ),
        message=(
            "Concurrent modification during iteration: "
            "Instance(length:2) of '_GrowableList'."
        ),
        line=3,
        meaning="The list changed while the for loop was still walking it",
        decoys=(
            "Two parts of the program ran at once and both used the list",
            "A list declared final cannot have items removed from it",
            "remove was given an item that is not in the cart",
        ),
        fix=(
            "'Concurrent' sounds like threads, but nothing ran at the "
            "same time — the loop and the remove take turns. The loop "
            "keeps its place by position; the remove shifted everything "
            "under it; on its next step the loop sees the length changed "
            "and stops rather than silently skip an item. That is why it "
            "blames the `for` line, not the remove, and why the message "
            "describes the list by its new length. Use "
            "`cart.removeWhere((item) => item == 'bread')`, or loop over "
            "a copy: `for (final item in [...cart])`. (And `final` is "
            "not the problem — it fixes the name, not the list's contents.)"
        ),
    ),
)
