"""Dart types pack, part 2: Extension Says - what do extension methods return, and which one is found?

Two ideas run through the templates. First, an extension adds a member to a type you do not own (`int`, `String`,
`List<int>`, your own class), and calling it looks like any other call. Second, extensions are chosen STATICALLY, by
the type the compiler sees: a member of the class always beats an extension member of the same name, and a variable
typed `Object` or `A` finds the extension for `Object` or `A` even when the object inside is a `String` or a `B`.
"""

from __future__ import annotations

from ._dart_model import D, capitalise, ddiv, dmod, replace_first, to_upper
from ._model import Maker

STATIC = "Extensions are picked by the variable's static type, not by the object inside it."
MEMBER = "A member of the class always wins over an extension method with the same name."

EXTENSIONS: list[Maker] = [
    D("extension on int { int twice() => this * 2; }\nvoid main() => print($a.twice());", lambda p: 2 * p["a"], "this is the int the method was called on."),
    D("extension on int { int get sq => this * this; }\nvoid main() => print($a.sq);", lambda p: p["a"] ** 2, "An extension can add a getter, read without parentheses."),
    D("extension on int { int twice() => this * 2; }\nvoid main() => print($a.twice().twice());", lambda p: 4 * p["a"], "The result is an int again, so the extension can be called on it."),
    D("extension on int { int get next => this + 1; }\nvoid main() => print($a.next.next);", lambda p: p["a"] + 2, "Each .next adds one to the result before it."),
    D("extension Twice on int { int twice() => this * 2; }\nvoid main() => print(Twice($a).twice());", lambda p: 2 * p["a"], "A named extension can be applied by hand: Twice(value)."),
    D("extension on int { int plus([int n = 1]) => this + n; }\nvoid main() => print($a.plus() + $b.plus($c));", lambda p: p["a"] + 1 + p["b"] + p["c"], "An extension method takes optional parameters like any method."),
    D("extension on int { bool by(int d) => this % d == 0; }\nvoid main() => print($n.by($a));", lambda p: dmod(p["n"], p["a"]) == 0, "by is true when the remainder of the division is 0."),
    D("extension on int { bool get big => this > 20; }\nvoid main() => print($n.big);", lambda p: p["n"] > 20, "The getter compares the int it is called on with 20."),
    D("extension on int { Duration get secs => Duration(seconds: this); }\nvoid main() => print($a.secs.inMilliseconds);", lambda p: 1000 * p["a"], "$a seconds is 1000 times as many milliseconds."),
    D("extension on bool { int get n => this ? 1 : 0; }\nvoid main() => print(($a > $b).n + ($c > $d).n);", lambda p: int(p["a"] > p["b"]) + int(p["c"] > p["d"]), "Each comparison is a bool, and n turns true into 1 and false into 0."),
    D("extension on num { double get half => this / 2; }\nvoid main() => print($a.half);", lambda p: ddiv(p["a"], 2), "/ always gives a double in Dart."),
    D("extension on int { int quad() => twice().twice(); int twice() => this * 2; }\nvoid main() => print($a.quad());", lambda p: 4 * p["a"], "One extension method can call another of the same extension."),
    D("extension on String { String shout() => toUpperCase() + '!'; }\nvoid main() => print('$w'.shout());", lambda p: to_upper(p["w"]) + "!", "Inside the extension, toUpperCase() is called on the string itself."),
    D("extension on String { String get first => this[0]; }\nvoid main() => print('$w'.first);", lambda p: p["f"], "this[0] is the first character of the string."),
    D("extension on String { String get rev => split('').reversed.join(); }\nvoid main() => print('$w'.rev);", lambda p: p["w"][::-1], "split into letters, reverse them, join them back."),
    D("extension on String { String boxed() => '[' + this + ']'; }\nvoid main() => print('$w'.boxed());", lambda p: "[" + p["w"] + "]", "this is the string, so the method wraps it in brackets."),
    D("extension on String { String get cap => this[0].toUpperCase() + substring(1); }\nvoid main() => print('$w'.cap);", lambda p: capitalise(p["w"]), "The first letter is upper-cased and the rest is kept."),
    D("extension on String { String times(int n) => this * n; }\nvoid main() => print('$f'.times($a));", lambda p: p["f"] * p["a"], "String * int repeats the string."),
    D("extension on String { String operator -(String o) => replaceFirst(o, ''); }\nvoid main() => print('$w' - '$y');", lambda p: replace_first(p["w"], p["y"], ""), "An extension can define an operator; here minus removes the first match."),
    D("extension on String { int get vowelCount => split('').where((c) => 'aeiou'.contains(c)).length; }\nvoid main() => print('$w'.vowelCount);", lambda p: sum(1 for c in p["w"] if c in "aeiou"), "It counts the letters that are in aeiou."),
    D("extension on String { bool get isPalin => this == split('').reversed.join(); }\nvoid main() => print('level'.isPalin);", True, "level reads the same backwards."),
    D("extension on String { bool get isPalin => this == split('').reversed.join(); }\nvoid main() => print('$w'.isPalin);", lambda p: p["w"] == p["w"][::-1], "A palindrome equals its own reverse."),
    D("extension on String? { String get safe => this ?? '-'; }\nvoid main() {\n  String? s;\n  print(s.safe);\n}", "-", "An extension on a nullable type can be called on null."),
    D("extension on String? { String get safe => this ?? '-'; }\nvoid main() {\n  String? s = '$w';\n  print(s.safe);\n}", lambda p: p["w"], "The string is not null, so it is returned as it is."),
    D("extension on List<int> { int get total => reduce((a, b) => a + b); }\nvoid main() => print([$a, $b, $c].total);", lambda p: p["a"] + p["b"] + p["c"], "reduce adds the items two at a time."),
    D("extension on List<int> { int get second => this[1]; }\nvoid main() => print([$a, $b, $c].second);", lambda p: p["b"], "this[1] is the second item."),
    D("extension E<T> on List<T> { T get second => this[1]; }\nvoid main() => print(['$w', '$v'].second);", lambda p: p["v"], "A generic extension works for a list of anything."),
    D("extension on List<String> { String get joined => join('-'); }\nvoid main() => print(['$w', '$v'].joined);", lambda p: p["w"] + "-" + p["v"], "join glues the strings with a dash between."),
    D("extension on List<int> { List<int> get evens => where((x) => x.isEven).toList(); }\nvoid main() => print([$a, $b, $c, $d].evens);", lambda p: [x for x in (p["a"], p["b"], p["c"], p["d"]) if x % 2 == 0], "where keeps the even items, toList makes a list again."),
    D("extension on List<int> { int get lastTwo => this[length - 1] + this[length - 2]; }\nvoid main() => print([$a, $b, $c].lastTwo);", lambda p: p["b"] + p["c"], "The last two items are b and c."),
    D("extension on Iterable<int> { int get total => reduce((a, b) => a + b); }\nvoid main() => print([$a, $b].map((x) => x * 2).total);", lambda p: 2 * (p["a"] + p["b"]), "map gives an Iterable<int>, and the extension works on any Iterable<int>."),
    D("extension on Iterable<String> { String get lens => map((s) => s.length).join(','); }\nvoid main() => print(['$w', '$v'].lens);", lambda p: f"{len(p['w'])},{len(p['v'])}", "Each string is turned into its length, then joined with commas."),
    D("extension on Map<String, int> { int get total => values.reduce((a, b) => a + b); }\nvoid main() => print({'x': $a, 'y': $b}.total);", lambda p: p["a"] + p["b"], "values are the numbers, and reduce adds them."),
    D("class P { int x; P(this.x); }\nextension on P { int get dbl => x * 2; }\nvoid main() => print(P($a).dbl);", lambda p: 2 * p["a"], "An extension can use the public members of the class it extends."),
    D("enum C { r, g }\nextension on C { String get up => name.toUpperCase(); }\nvoid main() => print(C.g.up);", "G", "An enum can get new members by an extension too."),
    D("extension X on int {\n  static int sq(int n) => n * n;\n}\nvoid main() => print(X.sq($a));", lambda p: p["a"] ** 2, "A static member of an extension is called on the extension's name."),
    D("extension on int { int call(int x) => this * x; }\nvoid main() {\n  int n = $a;\n  print(n($b));\n}", lambda p: p["a"] * p["b"], "An extension can give a type a call method, so the value can be called."),
    # ── which one is found: the traps ──
    D("class A { String f() => 'member'; }\nextension on A { String f() => 'ext'; }\nvoid main() => print(A().f());", "member", MEMBER),
    D("extension on int { int abs() => 0; }\nvoid main() => print((-$a).abs());", lambda p: p["a"], "int already has abs(), so the extension's abs is never reached."),
    D("extension on String { int get length => 99; }\nvoid main() => print('$w'.length);", lambda p: len(p["w"]), "String already has length, and the member wins."),
    D("class A {}\nclass B extends A {}\nextension on A { String who() => 'a'; }\nextension on B { String who() => 'b'; }\nvoid main() {\n  A x = B();\n  print(x.who());\n}", "a", STATIC),
    D("class A {}\nclass B extends A {}\nextension on A { String who() => 'a'; }\nextension on B { String who() => 'b'; }\nvoid main() {\n  var x = B();\n  print(x.who());\n}", "b", "The variable is a B, and the extension on B is more specific than the one on A."),
    D("extension on Object { String t() => 'obj'; }\nextension on String { String t() => 'str'; }\nvoid main() {\n  Object o = '$w';\n  print(o.t());\n}", "obj", STATIC),
    D("extension on Object { String t() => 'obj'; }\nextension on String { String t() => 'str'; }\nvoid main() {\n  var o = '$w';\n  print(o.t());\n}", "str", "var is inferred as String here, so the String extension is the more specific one."),
    D("extension on num { String get kind => 'num'; }\nextension on int { String get kind => 'int'; }\nvoid main() {\n  num n = $a;\n  print(n.kind);\n}", "num", STATIC),
    D("extension on num { String get kind => 'num'; }\nextension on int { String get kind => 'int'; }\nvoid main() {\n  int n = $a;\n  print(n.kind);\n}", "int", "The variable is an int, so the int extension is the closest fit."),
    D("extension on num { String get kind => 'num'; }\nextension on int { String get kind => 'int'; }\nvoid main() => print($a.5.kind);", "num", "A double is not an int, so only the num extension fits."),
]
