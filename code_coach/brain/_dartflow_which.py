"""Dart flow pack, part 2: Which Exception - what does `e.runtimeType` (or `e is ...`) show for the failing line?

Each template is the BODY of main: a `try { <failing code>; } catch (e) { print(e.runtimeType); }` (one line), and the
answer is the class name of what Dart throws. The classes: FormatException (a parse that fails), RangeError (an index
or a range that is outside), StateError (`first`/`last`/`single` on the wrong number of items, `firstWhere` with no
match), UnsupportedError (changing what cannot change), ConcurrentModificationError (changing a collection while
looping over it), NoSuchMethodError (a method on a `dynamic` that does not have it), ArgumentError (a bad argument),
IntegerDivisionByZeroException (`~/` and `%` by zero on ints). The `e is X` templates ask for the family tree of
`_dartflow_model.IS_A` instead. A `TypeError` has the private runtime type `_TypeError`, so it is only asked with `is`.
"""

from __future__ import annotations

from string import Template

from ._dartflow_model import F, catches
from ._model import Maker

WRAP = "try { %s } catch (e) { print(e.runtimeType); }"
WHY = {
    "FormatException": "The text cannot be read as that kind of value, so parsing throws a FormatException.",
    "RangeError": "The index or range is outside what the list or string holds: a RangeError.",
    "StateError": "The collection has the wrong number of items for this: a StateError (Bad state).",
    "UnsupportedError": "That change is not allowed on this object: an UnsupportedError.",
    "ConcurrentModificationError": "Changing a collection while a loop walks over it throws a ConcurrentModificationError.",
    "NoSuchMethodError": "A dynamic value is checked only when the call runs, and this one has no such member: NoSuchMethodError.",
    "ArgumentError": "The argument is not acceptable to the function: an ArgumentError.",
    "IntegerDivisionByZeroException": "Dividing an int by zero with ~/ or % throws an IntegerDivisionByZeroException.",
}


def W(op: str, answer: str, why: str | None = None) -> Maker:
    """A one-line try/catch around `op` (a Dart statement or statements ending in ;), answer: the exception class."""
    return F(WRAP % op, lambda p: answer, why or WHY[answer])


#: (statement, class) pairs also used by the `is` templates; the same holes as the P() of _dart_model.
OPS: list[tuple[str, str]] = [
    ("int.parse('$w');", "FormatException"),
    ("double.parse('$w');", "FormatException"),
    ("int.parse('$a.$b');", "FormatException"),
    ("[$a, $b, $c][$n];", "RangeError"),
    ("'$w'.substring($n);", "RangeError"),
    ("<int>[].first;", "StateError"),
    ("[$a, $b].single;", "StateError"),
    ("[$a, $b, $c].firstWhere((x) => x > 100);", "StateError"),
    ("List.unmodifiable([$a, $b]).add($c);", "UnsupportedError"),
    ("var xs = [$a, $b, $c]; for (var x in xs) { xs.add(x); }", "ConcurrentModificationError"),
    ("dynamic d = $a; d.length;", "NoSuchMethodError"),
    ("$a ~/ 0;", "IntegerDivisionByZeroException"),
    ("RegExp('(');", "FormatException"),
    ("$a.clamp($b + 10, $b);", "ArgumentError"),
]


def _op(code: str, cls: str) -> Maker:
    return F(WRAP % code, lambda p: cls, WHY[cls])


def _is_family(test: str) -> Maker:
    """`print(e is <test>)` for a random operation: true when the thrown class is a <test>."""
    def pre(p, rng):
        code, cls = rng.choice([o for o in OPS if o[1] != "IntegerDivisionByZeroException"])  # it is both kinds
        p["op"], p["cls"] = Template(code).safe_substitute(p), cls

    def why(p):
        yes = catches(p["cls"], test)
        return (f"A {p['cls']} is {'a' if yes else 'not a'} {test}: " + (
            "FormatException and IntegerDivisionByZeroException are Exceptions; the others are Errors."
            if test == "Exception" else
            "Error is the family of mistakes in the program (StateError, RangeError, ...); FormatException is not one."
            if test == "Error" else "RangeError is a kind of ArgumentError; the rest are not."))

    return F("try { ${op} } catch (e) { print(e is %s); }" % test, lambda p: catches(p["cls"], test), why, pre)


def _throw_value(code: str, name: str) -> Maker:
    return F(WRAP % ("throw " + code + ";"), lambda p: name,
             "You can throw any value; the runtimeType is the type of whatever was thrown.")


WHICH: list[Maker] = [
    # one idea each: the line and the class it throws
    *[_op(code, cls) for code, cls in OPS],
    W("[$a, $b, $c][-$k];", "RangeError", "A negative index is outside the list: a RangeError."),
    W("'$w'[$n];", "RangeError", "A string index past its last character is a RangeError."),
    W("'$w'.codeUnitAt($n);", "RangeError"),
    W("[$a, $b].sublist($n);", "RangeError", "sublist starting past the end is a RangeError."),
    W("var xs = [$a, $b]; xs.removeAt($n);", "RangeError", "removeAt with an index that is not there is a RangeError."),
    W("var xs = [$a, $b]; xs[$n] = $c;", "RangeError", "Assigning to an index past the end does not grow the list: a RangeError."),
    W("var xs = [$a, $b]; xs.insert($n, $c);", "RangeError", "insert allows 0 up to the length; beyond that is a RangeError."),
    W("List.generate(-$k, (i) => i);", "RangeError", "A negative length is a RangeError."),
    W("<int>[].last;", "StateError", "last on an empty list is a StateError."),
    W("<int>{}.first;", "StateError", "first on an empty set is a StateError."),
    W("<int>[].reduce((a, b) => a + b);", "StateError", "reduce has nothing to start from on an empty list: a StateError."),
    W("[$a, $b, $c].singleWhere((x) => x > 0);", "StateError", "singleWhere wants exactly one match; three is too many: a StateError."),
    W("const [$a, $b].add($c);", "UnsupportedError", "A const list can never change: an UnsupportedError."),
    W("List<int>.filled($a, 0, growable: false).add($b);", "UnsupportedError", "A fixed-length list cannot grow: an UnsupportedError."),
    W("Map.unmodifiable({'$w': $a})['$v'] = $b;", "UnsupportedError", "An unmodifiable map refuses changes: an UnsupportedError."),
    W("var m = {'$w': $a, '$v': $b}; for (var k in m.keys) { m.remove(k); }", "ConcurrentModificationError",
      "Removing a key while looping over the keys is a ConcurrentModificationError."),
    W("var xs = [$a, $b, $c]; xs.forEach((x) { xs.remove(x); });", "ConcurrentModificationError",
      "forEach is a loop too: removing from the list while it runs throws."),
    W("dynamic d; d.length;", "NoSuchMethodError", "d is null, and null has no length: NoSuchMethodError."),
    W("dynamic d = '$w'; d.foo();", "NoSuchMethodError", "A String has no foo method: NoSuchMethodError."),
    W("$n % 0;", "IntegerDivisionByZeroException", "% by an int zero throws the same way ~/ does."),
    W("DateTime.parse('$w');", "FormatException", "DateTime.parse wants a date text: a FormatException."),
    W("throw ArgumentError('$w');", "ArgumentError", "You can throw the classes yourself; this one is an ArgumentError."),
    W("throw StateError('$w');", "StateError", "throw StateError(...) throws a StateError."),
    W("throw FormatException('$w');", "FormatException", "throw FormatException(...) throws a FormatException."),
    W("throw UnsupportedError('$w');", "UnsupportedError", "throw UnsupportedError(...) throws an UnsupportedError."),
    W("throw UnimplementedError();", "UnimplementedError", "UnimplementedError marks code that is not written yet."),
    W("throw RangeError('$w');", "RangeError", "throw RangeError(...) throws a RangeError."),
    # thrown values that are not exceptions at all
    _throw_value("$a", "int"),
    _throw_value("'$w'", "String"),
    _throw_value("$a.5", "double"),
    _throw_value("true", "bool"),
    _throw_value("[$a, $b]", "List<int>"),
    # your own classes
    F("class ${W}Error implements Exception {}\nvoid main() {\n  try {\n    throw ${W}Error();\n  } catch (e) {\n    print(e.runtimeType);\n  }\n}",
      lambda p: p["W"] + "Error", "runtimeType is the class of the thrown object, here your own class."),
    F("class ${W}Error extends Error {}\nvoid main() {\n  try {\n    throw ${W}Error();\n  } catch (e) {\n    print(e.runtimeType);\n  }\n}",
      lambda p: p["W"] + "Error", "A class can extend Error too; the runtimeType is still the class that was thrown."),
    F("class Base implements Exception {}\nclass ${W}Error extends Base {}\nvoid main() {\n  try {\n    throw ${W}Error();\n  } on Base catch (e) {\n    print(e.runtimeType);\n  }\n}",
      lambda p: p["W"] + "Error", "on Base catches it, but runtimeType shows what was really thrown: the child class."),
    F("void check(int age) {\n  if (age < 0) throw ArgumentError.value(age);\n  if (age > 150) throw RangeError.value(age);\n}\nvoid main() {\n  try { check(-$a); } catch (e) { print(e.runtimeType); }\n}",
      lambda p: "ArgumentError", "The first check fires: ArgumentError.value throws an ArgumentError."),
    F("void check(int age) {\n  if (age < 0) throw ArgumentError.value(age);\n  if (age > 150) throw RangeError.value(age);\n}\nvoid main() {\n  try { check(${n}00); } catch (e) { print(e.runtimeType); }\n}",
      lambda p: "RangeError", "A number above 150 passes the first check and fails the second."),
    # the family tree
    *[_is_family(t) for t in ("Exception", "Error", "Error", "ArgumentError", "Exception", "Error")],
    F("try { Object o = '$w'; o as int; } catch (e) { print(e is TypeError); }", lambda p: True,
      "A bad cast throws a TypeError (its real class name is private, but `is TypeError` works)."),
    F("try { Object o = $a; o as String; } catch (e) { print(e is Exception); }", lambda p: False,
      "A TypeError is an Error, not an Exception."),
    F("try { int.parse('$w'); } catch (e) { print(e is Error); }", lambda p: False,
      "A FormatException is an Exception: the family of things that can fail on input, not a mistake in the program."),
]
