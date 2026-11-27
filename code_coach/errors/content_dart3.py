"""A third set of Dart crashes.

Same rules as `content_dart.py` and `content_dart2.py`: each one compiles,
then dies while running (exit 255, "Unhandled exception:"), and every
message and line was copied from what `dart run` printed and is held to
it by tests/test_errors_dart3.py through `engine_report`.

This set is the everyday throws: an index past the end, a string cut too
far, a `single` that found two, a value that was a double and not an int,
a `late final` set twice, an exception somebody threw on purpose.
"""

from __future__ import annotations

from code_coach.errors import Crash, _c


DART_CRASHES_3: tuple[Crash, ...] = (
    _c(
        id="err-dart-index-past-end",
        level=1,
        name="An index one past the end",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final seats = ['A', 'B', 'C'];\n"
            "  final pick = 5;\n"
            "  print(seats[pick]);\n"
            "}"
        ),
        message="RangeError (length): Invalid value: Not in inclusive range 0..2: 5",
        line=4,
        meaning="The list has three items, so 5 is past its last index of 2",
        decoys=(
            "Lists in Dart only accept indexes up to 2, whatever their length",
            "pick should have been a String, not an int",
            "The list is empty, so there is nothing at any index",
        ),
        fix=(
            "Read it as: the allowed range is 0..2, and the value you gave "
            "was 5. Three items means indexes 0, 1 and 2 - the last index is "
            "always length minus one. Dart does not hand back null for a "
            "missing index, as a Map does for a missing key, and it does not "
            "give undefined as JavaScript does: it throws. Check before "
            "you read - `if (pick < seats.length) ...` - or work out where "
            "the 5 came from, since it is usually a count that is off by one "
            "or a list that is shorter than you thought."
        ),
    ),
    _c(
        id="err-dart-thrown-exception",
        level=1,
        name="An exception somebody threw on purpose",
        family="Dart",
        language="dart",
        code=(
            "void sell(int stock) {\n"
            "  if (stock == 0) throw Exception('Out of stock');\n"
            "  print('Sold');\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  sell(0);\n"
            "}"
        ),
        message="Exception: Out of stock",
        line=2,
        meaning="The code itself threw it, and nothing caught it",
        decoys=(
            "Dart ran out of memory while selling the item",
            "sell was called with the wrong kind of argument",
            "The word Exception is a name Dart reserves for a crash in the SDK",
        ),
        fix=(
            "This crash is not Dart noticing a mistake - it is your own "
            "`throw`. The text in the message is the text in the quotes, and "
            "the line is the line with `throw` on it, not line 7 where sell "
            "was called. It is uncaught because no `try` and `catch` stands "
            "between the throw and the top. Either the call site handles it - "
            "`try { sell(0); } on Exception catch (e) { ... }` - or the "
            "function checks and returns a result instead of throwing."
        ),
    ),
    _c(
        id="err-dart-argument-error",
        level=2,
        name="A function that refused its argument",
        family="Dart",
        language="dart",
        code=(
            "int setAge(int age) {\n"
            "  if (age < 0) {\n"
            "    throw ArgumentError('age must not be negative');\n"
            "  }\n"
            "  return age;\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(setAge(-3));\n"
            "}"
        ),
        message="Invalid argument(s): age must not be negative",
        line=3,
        meaning="A check inside setAge threw it on purpose for a bad value",
        decoys=(
            "setAge was called without the one argument it declares as required",
            "-3 is not a valid int literal in Dart",
            "print was handed a value of a type that it is unable to display",
        ),
        fix=(
            "'Invalid argument(s):' is how an ArgumentError introduces "
            "itself, and what follows is whatever words the author chose. "
            "Here the author is you: line 3 throws it when age is below "
            "zero, and main passed -3. The fault is in the caller's value, "
            "and the crash points at the function that noticed it. Fix the "
            "value, or have the caller check first - and when you write "
            "such a guard, put the reason in the message, as this one does."
        ),
    ),
    _c(
        id="err-dart-substring-range",
        level=2,
        name="Cutting a string past its end",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final code = 'AB';\n"
            "  final tail = code.substring(3);\n"
            "  print(tail);\n"
            "}"
        ),
        message="RangeError (start): Invalid value: Not in inclusive range 0..2: 3",
        line=3,
        meaning="The string has two letters, so a start of 3 is past its end",
        decoys=(
            "substring is only allowed on a string that has three or more letters in it",
            "substring counts from the end, and 3 is too far back",
            "code was declared final, and a final string can never be cut into pieces",
        ),
        fix=(
            "The word in brackets - start - names which argument was out "
            "of range, and 0..2 is what it could have been: for a string "
            "of 2 letters, a cut may start at 0, 1 or 2 (2 gives an empty "
            "string). You asked for 3. Python and JavaScript quietly give "
            "an empty string for a slice past the end; Dart's substring "
            "does not. Compare with `code.length` first, or use "
            "`code.length > 3 ? code.substring(3) : ''`."
        ),
    ),
    _c(
        id="err-dart-single-many",
        level=3,
        name="single when there are two",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  final admins = ['ann', 'raj'];\n"
            "  final boss = admins.single;\n"
            "  print(boss);\n"
            "}"
        ),
        message="Bad state: Too many elements",
        line=3,
        meaning="single wants exactly one item and the list has two",
        decoys=(
            "The list has more elements than Dart allows in one variable",
            "single can only be used on a list of numbers",
            "boss is final, so it cannot be given a list element",
        ),
        fix=(
            "`single` is a promise: this collection holds exactly one "
            "thing, and here is that thing. Two or more breaks the promise "
            "('Too many elements'); none breaks it the other way ('No "
            "element'). 'Bad state' is the family StateError belongs to - "
            "the call was fine, the collection was not what the call "
            "needed. If you want the first, say `.first`; if there might be "
            "none, `.firstOrNull` or check `isNotEmpty` first."
        ),
    ),
    _c(
        id="err-dart-double-as-int",
        level=3,
        name="A price that was not a whole number",
        family="Dart",
        language="dart",
        code=(
            "import 'dart:convert';\n"
            "\n"
            "void main() {\n"
            "  final item = jsonDecode('{\"price\": 9.5}') as Map<String, dynamic>;\n"
            "  final price = item['price'] as int;\n"
            "  print(price);\n"
            "}"
        ),
        message="type 'double' is not a subtype of type 'int' in type cast",
        line=5,
        meaning="The price is 9.5, which is a double, and the cast said int",
        decoys=(
            "9.5 is a String in JSON, so the cast to int failed",
            "A double always rounds to an int when it is cast",
            "The key price is missing, so the value was null",
        ),
        fix=(
            "The first type in the message is what the value really is, "
            "the second is what you promised: a double, and you said int. "
            "A cast with `as` never converts - it only checks - so "
            "9.5 is not squeezed into 9. If prices may have cents, ask "
            "for what is there: `as double`, or `as num` to accept both "
            "and then `.toDouble()` or `.round()` on purpose. 'double' "
            "is the clue that the JSON had a decimal point."
        ),
    ),
    _c(
        id="err-dart-enum-byname",
        level=3,
        name="An enum name that does not exist",
        family="Dart",
        language="dart",
        code=(
            "enum Color { red, green }\n"
            "\n"
            "void main() {\n"
            "  final c = Color.values.byName('purple');\n"
            "  print(c);\n"
            "}"
        ),
        message='Invalid argument (name): No enum value with that name: "purple"',
        line=4,
        meaning="Color has no value called purple, only red and green",
        decoys=(
            "byName expects the enum's index number as its argument, not a name",
            "Enum value names have to be written in capital letters to be found",
            "purple is a reserved word in Dart",
        ),
        fix=(
            "The brackets say which argument was wrong - name - and the "
            "quotes show the exact text that was tried, which is how you "
            "spot a typo or a wrong-case 'Red'. byName is strict and "
            "throws on a miss, which is good: a bad colour from a file or a "
            "server should not silently become something else. For input "
            "you do not trust, use "
            "`Color.values.asNameMap()['purple']`, which gives null."
        ),
    ),
    _c(
        id="err-dart-late-twice",
        level=4,
        name="A late final set a second time",
        family="Dart",
        language="dart",
        code=(
            "class Order {\n"
            "  late final int id;\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  final o = Order();\n"
            "  o.id = 1;\n"
            "  o.id = 2;\n"
            "  print(o.id);\n"
            "}"
        ),
        message="LateInitializationError: Field 'id' has already been initialized.",
        line=8,
        meaning="A late final can be given a value only once, and id had one",
        decoys=(
            "id was read before it was ever given a value",
            "late fields can only be set inside the class that declares them",
            "Order needed a constructor to set id the first time",
        ),
        fix=(
            "The earlier late crash said 'has not been initialized' - read "
            "before set. This is the mirror image: 'already been "
            "initialized' - set after it was set. `late final` means 'I "
            "will give this a value later, but only once', and line 7 "
            "used up that one chance, so line 8 is the one that fails. "
            "Plain `late` (no final) can be set again. If the value truly "
            "never changes, set it in one place only."
        ),
    ),
    _c(
        id="err-dart-list-cast",
        level=4,
        name="A list that was too general to cast",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  List<Object> items = [1, 2, 3];\n"
            "  final nums = items as List<int>;\n"
            "  print(nums.length);\n"
            "}"
        ),
        message="type 'List<Object>' is not a subtype of type 'List<int>' in type cast",
        line=3,
        meaning="The list was made as List<Object>, so it is not a List<int>",
        decoys=(
            "The three items are not integers, so the cast failed",
            "A List cannot be cast to a more specific List in Dart",
            "nums is final, so it cannot hold a cast result",
        ),
        fix=(
            "The cast looks at the list's own type, not at what is in it: "
            "this list was created as List<Object>, so it does not count "
            "as a List<int>, even though every item happens to be an int. "
            "The fix is to build a new list rather than relabel the old "
            "one: `items.cast<int>().toList()`, or "
            "`List<int>.from(items)`, or create it as List<int> in the "
            "first place."
        ),
    ),
    _c(
        id="err-dart-null-getter",
        level=4,
        name="Asking a null for its length",
        family="Dart",
        language="dart",
        code=(
            "void main() {\n"
            "  dynamic profile;\n"
            "  print(profile.length);\n"
            "}"
        ),
        message="NoSuchMethodError: The getter 'length' was called on null.",
        line=3,
        meaning="profile never got a value, so it is null and has no length",
        decoys=(
            "length is a method in Dart, so it must have brackets written after its name",
            "a variable declared dynamic is not allowed to be printed with print",
            "profile is an empty string, which has no length",
        ),
        fix=(
            "A `dynamic` variable that is never set starts as null, and "
            "null has no members at all, so asking it for `length` is "
            "'a getter called on null'. 'Getter' means you read a "
            "property without brackets; a call with brackets would say "
            "'method'. With a real type - `String? profile` - the "
            "analyzer would not let this compile until you handled null: "
            "`profile?.length`, or `profile ?? ''`. dynamic is what "
            "switches that help off."
        ),
    ),
)
