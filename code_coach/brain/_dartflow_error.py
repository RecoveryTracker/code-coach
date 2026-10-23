"""Dart flow pack, part 8: Error Message - read what Dart says when it fails.

Each template catches an error and prints it (`print(e)`, `e.message`, `e.invalidValue`...); the answer is the text
or number that comes out (oracle `value`, one line of at most 40 characters). Only the STABLE parts of Dart's
messages are used - the ones written by the exception classes themselves:

    StateError('x')            Bad state: x             Exception('x')         Exception: x
    ArgumentError('x')         Invalid argument(s): x   FormatException('x')   FormatException: x
    UnsupportedError('x')      Unsupported operation: x RangeError('x')        RangeError: x
    UnimplementedError('x')    UnimplementedError: x    AssertionError('x')    Assertion failed: "x"
    ArgumentError.value(5, 'age')   Invalid argument (age): 5
    first/last/single/reduce on nothing   Bad state: No element     single with 2 or more   Bad state: Too many elements

a thrown String or number prints as itself, an object of your own class prints `Instance of 'Name'` unless its class
overrides `toString`. The RangeError text itself ("(index)" or "(length)") changed between versions, so a RangeError
is only asked through its parts: `invalidValue` (the bad number), `start` and `end` of `RangeError.range`.
"""

from __future__ import annotations

from ._dartflow_model import F
from ._model import Maker

ONE = "try { %s; } catch (e) { print(e); }"
MSG = "try { %s; } on %s catch (e) { print(e.%s); }"
EXC_WHY = "print(e) shows the exception's toString: the class's own wording followed by the message you gave."


def E(throws: str, answer, why: str = EXC_WHY) -> Maker:
    """`try { <throws>; } catch (e) { print(e); }` - answer is a string or a function of the holes."""
    return F(ONE % throws, answer if callable(answer) else (lambda p: answer), why)


def M(code: str, cls: str, member: str, answer, why: str, decls: str = "", pre=None) -> Maker:
    """`try { <code>; } on <cls> catch (e) { print(e.<member>); }`."""
    src = MSG % (code, cls, member)
    if decls:
        src = decls + "void main() {" + chr(10) + "  " + src + chr(10) + "}"
    return F(src, answer if callable(answer) else (lambda p: answer), why, pre)


def pre_ab(p, rng):
    p["a"], p["b"] = rng.sample(range(2, 9), 2)


def pre_idx(p, rng):
    p["a"], p["b"], p["c"] = rng.sample(range(1, 9), 3)
    p["n"] = rng.randint(10, 40)


def pre_range(p, rng):
    p["lo"] = rng.randint(0, 3)
    p["hi"] = p["lo"] + rng.randint(3, 9)
    p["v"] = p["hi"] + rng.randint(1, 9)


def pre_neg(p, rng):
    p["m"] = rng.randint(1, 9)


def pre_cls(p, rng):
    p["cls"] = rng.choice(["Farm", "Barn", "Corn", "Seed", "Lamp", "Tree", "Wheat"]) + "Error"
    p["W"] = p["cls"]


APP = ("class AppError implements Exception {\n  final String msg;\n  AppError(this.msg);\n"
       "  @override\n  String toString() => 'AppError: $$msg';\n}\n")
CUSTOM_HEAD = "class ${cls} implements Exception {\n  final String msg;\n  ${cls}(this.msg);\n"

ERROR: list[Maker] = [
    # ── the wording of each exception class ──
    E("throw StateError('$w')", lambda p: "Bad state: " + p["w"], "StateError's text starts with Bad state: and then your message."),
    E("throw ArgumentError('$w')", lambda p: "Invalid argument(s): " + p["w"], "ArgumentError's text starts with Invalid argument(s): ."),
    E("throw UnsupportedError('$w')", lambda p: "Unsupported operation: " + p["w"], "UnsupportedError's text starts with Unsupported operation: ."),
    E("throw UnimplementedError('$w')", lambda p: "UnimplementedError: " + p["w"], "UnimplementedError names itself, then the message."),
    E("throw Exception('$w')", lambda p: "Exception: " + p["w"], "A plain Exception prints Exception: and the message."),
    E("throw FormatException('$w')", lambda p: "FormatException: " + p["w"], "FormatException names itself, then the message."),
    E("throw RangeError('$w')", lambda p: "RangeError: " + p["w"], "RangeError names itself, then the message."),
    E("throw AssertionError('$w')", lambda p: 'Assertion failed: "' + p["w"] + '"', "AssertionError prints Assertion failed: with the message in double quotes."),
    E("throw ArgumentError.value($a, '$w')", lambda p: f"Invalid argument ({p['w']}): {p['a']}", "ArgumentError.value(value, name) prints the name in brackets, then the bad value."),
    E("throw ArgumentError('$w', '$v')", lambda p: f"Invalid argument(s) ({p['v']}): {p['w']}", "The second argument is the name of the parameter: it goes in brackets before the message."),
    E("throw ArgumentError()", "Invalid argument(s)", "With no message, only the class's wording is left."),
    E("throw Exception()", "Exception", "With no message, only the word Exception."),
    E("throw FormatException()", "FormatException", "With no message, only the class name."),
    E("throw UnimplementedError()", "UnimplementedError", "With no message, only the class name."),
    # ── things thrown that are not exceptions at all ──
    E("throw '$w'", lambda p: p["w"], "A thrown String prints as itself."),
    E("throw $n", lambda p: p["n"], "A thrown number prints as itself."),
    E("throw [$a, $b]", lambda p: [p["a"], p["b"]], "A thrown list prints as a list."),
    E("throw {'$w': $a}", lambda p: {p["w"]: p["a"]}, "A thrown map prints like any map: no quotes."),
    E("throw $a.5", lambda p: f"{p['a']}.5", "A thrown double prints with its decimal point."),
    # ── the messages Dart's own code writes ──
    E("<int>[].first", "Bad state: No element", "first on an empty list: Bad state: No element."),
    E("<int>[].last", "Bad state: No element", "last on an empty list is the same error."),
    E("<int>{}.first", "Bad state: No element", "An empty set is empty too."),
    E("<int>[].single", "Bad state: No element", "single wants exactly one item; none is 'No element'."),
    E("[$a, $b].single", "Bad state: Too many elements", "single wants exactly one item; two or more is 'Too many elements'."),
    E("[$a, $b, $c].firstWhere((x) => x > 99)", "Bad state: No element", "firstWhere with no match and no orElse: No element."),
    E("[$a, $b, $c].singleWhere((x) => x > 0)", "Bad state: Too many elements", "singleWhere finds three matches: Too many elements."),
    E("[$a, $b, $c].singleWhere((x) => x > 99)", "Bad state: No element", "singleWhere finds none: No element."),
    E("<int>[].reduce((a, b) => a + b)", "Bad state: No element", "reduce has no first item to start from."),
    F("import 'dart:async';\nvoid main() {\n  try {\n    Completer<int>()..complete($a)..complete($b);\n  } catch (e) {\n    print(e);\n  }\n}", lambda p: "Bad state: Future already completed",
      "A Completer finishes only once; the second complete throws a StateError."),
    M("<int>[].first", "StateError", "message", "No element", "message is the text without the class's wording."),
    M("[$a, $b].single", "StateError", "message", "Too many elements", "message is the text without the class's wording."),
    M("List.unmodifiable([$a]).add($b)", "UnsupportedError", "message", "Cannot add to an unmodifiable list", "message is the text without Unsupported operation: ."),
    M("const [$a, $b].add($c)", "UnsupportedError", "message", "Cannot add to an unmodifiable list", "A const list is unmodifiable too."),
    M("List<int>.filled($a, 0, growable: false).add($b)", "UnsupportedError", "message", "Cannot add to a fixed-length list", "A fixed-length list cannot grow."),
    M("var c = StreamController<int>(); c.close(); c.add($a)", "StateError", "message", "Cannot add event after closing", "A closed controller takes no more events.",
      decls="import 'dart:async';\n"),
    M("var c = StreamController<int>(); c.stream.listen(null); c.stream.listen(null)", "StateError", "message", "Stream has already been listened to.",
      "A single-subscription stream has one listener only.", decls="import 'dart:async';\n"),
    # ── FormatException: message, source, offset ──
    M("int.parse('$w')", "FormatException", "message", "Invalid radix-10 number", "radix-10 is the everyday base 10: the text is not a whole number."),
    M("double.parse('$w')", "FormatException", "message", "Invalid double", "double.parse's own wording."),
    M("DateTime.parse('$w')", "FormatException", "message", "Invalid date format", "DateTime.parse's own wording."),
    M("BigInt.parse('$w')", "FormatException", "message", "Could not parse BigInt", "BigInt.parse's own wording."),
    M("int.parse('$w')", "FormatException", "source", lambda p: p["w"], "source is the text that could not be parsed."),
    M("int.parse('$a$w')", "FormatException", "source", lambda p: str(p["a"]) + p["w"], "source is the whole text, not just the bad part."),
    M("throw FormatException('$w', '$v', $a)", "FormatException", "offset", lambda p: p["a"], "FormatException(message, source, offset): offset is the third argument."),
    M("throw FormatException('$w', '$v', $a)", "FormatException", "source", lambda p: p["v"], "FormatException(message, source, offset): source is the second argument."),
    M("throw FormatException('$w', '$v', $a)", "FormatException", "message", lambda p: p["w"], "FormatException(message, source, offset): message is the first argument."),
    # ── RangeError and ArgumentError parts ──
    M("[$a, $b, $c][$n]", "RangeError", "invalidValue", lambda p: p["n"], "invalidValue is the index that was asked for."),
    M("[$a, $b, $c][-$m]", "RangeError", "invalidValue", lambda p: -p["m"], "invalidValue is the (negative) index that was asked for.", pre=pre_neg),
    M("'$w'.substring($n)", "RangeError", "invalidValue", lambda p: p["n"], "invalidValue is the start that was asked for."),
    M("[$a, $b].removeAt($n)", "RangeError", "invalidValue", lambda p: p["n"], "invalidValue is the index that was asked for."),
    M("throw RangeError.range($v, $lo, $hi)", "RangeError", "invalidValue", lambda p: p["v"], "RangeError.range(value, min, max): invalidValue is the first argument.", pre=pre_range),
    M("throw RangeError.range($v, $lo, $hi)", "RangeError", "start", lambda p: p["lo"], "RangeError.range(value, min, max): start is the allowed minimum.", pre=pre_range),
    M("throw RangeError.range($v, $lo, $hi)", "RangeError", "end", lambda p: p["hi"], "RangeError.range(value, min, max): end is the allowed maximum.", pre=pre_range),
    M("throw ArgumentError.value($a, '$w', '$v')", "ArgumentError", "invalidValue", lambda p: p["a"], "ArgumentError.value(value, name, message): invalidValue is the first argument."),
    M("throw ArgumentError.value($a, '$w', '$v')", "ArgumentError", "name", lambda p: p["w"], "ArgumentError.value(value, name, message): name is the second argument."),
    M("throw ArgumentError.value($a, '$w', '$v')", "ArgumentError", "message", lambda p: p["v"], "ArgumentError.value(value, name, message): message is the third argument."),
    M("throw StateError('$w')", "StateError", "message", lambda p: p["w"], "message is just the text you gave, without Bad state: ."),
    M("throw AssertionError('$w')", "AssertionError", "message", lambda p: p["w"], "message is just the text you gave, without the wording."),
    # ── a little context around the message ──
    F("try {\n  throw StateError('$w');\n} catch (e) {\n  print('Error: $$e');\n}", lambda p: "Error: Bad state: " + p["w"], "Inside a string, the dollar sign puts in e's toString."),
    F("try {\n  throw Exception('$w');\n} catch (e) {\n  print('caught $$e');\n}", lambda p: "caught Exception: " + p["w"], "Inside a string, the dollar sign puts in e's toString."),
    F("try {\n  try {\n    throw StateError('$w');\n  } catch (e) {\n    throw Exception('lost $$e');\n  }\n} catch (e) {\n  print(e);\n}", lambda p: "Exception: lost Bad state: " + p["w"],
      "The inner text becomes part of the new message."),
    F("try {\n  throw '$w';\n} catch (e) {\n  print(e.toString().length);\n}", lambda p: p["L"], "A thrown String's toString is the String: its length."),
    # ── your own classes ──
    F(APP + "void main() {\n  try { throw AppError('$w'); } catch (e) { print(e); }\n}", lambda p: "AppError: " + p["w"], "The class overrides toString, and print(e) uses it."),
    F(CUSTOM_HEAD + "}\nvoid main() {\n  try { throw ${cls}('$w'); } catch (e) { print(e); }\n}", lambda p: f"Instance of '{p['cls']}'",
      "Without a toString of its own, print shows Instance of and the class name.", pre_cls),
    F(CUSTOM_HEAD + "}\nvoid main() {\n  try { throw ${cls}('$w'); } on ${cls} catch (e) { print(e.msg); }\n}", lambda p: p["w"],
      "e.msg reads the field, which does not need a toString.", pre_cls),
    F(CUSTOM_HEAD + "  @override\n  String toString() => msg;\n}\nvoid main() {\n  try { throw ${cls}('$w'); } catch (e) { print(e); }\n}", lambda p: p["w"],
      "toString returns only the message, so that is all print shows.", pre_cls),
    F(CUSTOM_HEAD + "  @override\n  String toString() => '${cls}($$msg)';\n}\nvoid main() {\n  try { throw ${cls}('$w'); } catch (e) { print(e); }\n}",
      lambda p: f"{p['cls']}({p['w']})", "The toString writes the class name, then the message in brackets.", pre_cls),
    F("class Boom extends Error {\n  @override\n  String toString() => 'Boom!';\n}\nvoid main() {\n  try { throw Boom(); } catch (e) { print(e); }\n}", lambda p: "Boom!",
      "An Error subclass can override toString just the same."),
    F("class Boom extends Error {}\nvoid main() {\n  try { throw Boom(); } catch (e) { print(e); }\n}", lambda p: "Instance of 'Boom'",
      "Error's own toString is the plain Instance of ... wording."),
    F("class Code implements Exception {\n  final int n;\n  Code(this.n);\n  @override\n  String toString() => 'E$$n';\n}\nvoid main() {\n  try { throw Code($a); } catch (e) { print(e); }\n}",
      lambda p: f"E{p['a']}", "toString puts the number after an E."),
]
