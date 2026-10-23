"""Dart types pack, part 4: Generic Fit - generic functions and classes, bounds, inference, and `is` checks on types.

Three ideas: a type parameter (`T`) is filled in from the arguments or written out (`Box<num>`); a bound
(`T extends num`) limits what T may be; and Dart KEEPS the type arguments at run time, so `is List<int>` is a real
question whose answer depends on how the list was made. Only simple types are ever PRINTED (`int`, `double`, `String`,
`bool`, `Null`): the names of collection types are left out on purpose.
"""

from __future__ import annotations

from ._dart_model import D
from ._model import Maker

KEEP = "Dart keeps the type arguments at run time, so the list is a List of whatever it was made as."
VALUE = "runtimeType is the type of the value itself, not of the variable or the type parameter."


def _bigger(p: dict) -> object:
    return p["a"] if p["a"] > p["b"] + 0.5 else p["b"] + 0.5


GENERICS: list[Maker] = [
    D("T first<T>(List<T> xs) => xs[0];\nvoid main() => print(first([$a, $b]));", lambda p: p["a"], "T is inferred from the list, and first returns the first item."),
    D("T pick<T>(T a, T b) => b;\nvoid main() => print(pick('$w', '$v'));", lambda p: p["v"], "T is String, and pick returns its second argument."),
    D("List<T> twice<T>(T x) => [x, x];\nvoid main() => print(twice($a));", lambda p: [p["a"], p["a"]], "twice builds a list holding the value two times."),
    D("List<T> twice<T>(T x) => [x, x];\nvoid main() => print(twice('$w').join('-'));", lambda p: p["w"] + "-" + p["w"], "T is String, and join glues the two items with a dash."),
    D("T? firstOr<T>(List<T> xs) => xs.isEmpty ? null : xs.first;\nvoid main() => print(firstOr(<int>[]));", None, "An empty list gives null, and T? allows it."),
    D("T? firstOr<T>(List<T> xs) => xs.isEmpty ? null : xs.first;\nvoid main() => print(firstOr([$a, $b]));", lambda p: p["a"], "The list has items, so the first one comes back."),
    D("List<R> mapAll<T, R>(List<T> xs, R Function(T) f) => [for (var x in xs) f(x)];\nvoid main() => print(mapAll([$a, $b], (x) => x * 2));", lambda p: [2 * p["a"], 2 * p["b"]], "T is int, R is int, and f doubles each item."),
    D("List<R> mapAll<T, R>(List<T> xs, R Function(T) f) => [for (var x in xs) f(x)];\nvoid main() => print(mapAll([$a, $b], (x) => x > $c));", lambda p: [p["a"] > p["c"], p["b"] > p["c"]], "R is bool here: f answers true or false for each item."),
    D("T apply<T>(T Function() f) => f();\nvoid main() => print(apply(() => '$w'));", lambda p: p["w"], "T is String, the type f returns."),
    D("int go(int Function(int, int) f) => f($a, $b);\nvoid main() => print(go((x, y) => x * y));", lambda p: p["a"] * p["b"], "The parameter has a function type, and the lambda fits it."),
    D("Map<V, K> flip<K, V>(Map<K, V> m) => {for (var e in m.entries) e.value: e.key};\nvoid main() => print(flip({'$w': $a}));", lambda p: {p["a"]: p["w"]}, "Keys and values trade places."),
    # ── bounds ──
    D("T bigger<T extends num>(T a, T b) => a > b ? a : b;\nvoid main() => print(bigger($a, $b));", lambda p: max(p["a"], p["b"]), "T extends num lets the function compare with >."),
    D("T bigger<T extends num>(T a, T b) => a > b ? a : b;\nvoid main() => print(bigger($a, $b + 0.5));", _bigger, "T becomes num, so an int and a double can be mixed."),
    D("T bigger<T extends num>(T a, T b) => a > b ? a : b;\nvoid main() => print(bigger($a, $b + 0.5).runtimeType);", lambda p: "int" if p["a"] > p["b"] + 0.5 else "double", VALUE),
    D("num sum<T extends num>(List<T> xs) => xs.fold<num>(0, (a, b) => a + b);\nvoid main() => print(sum([$a, $b, $c]));", lambda p: p["a"] + p["b"] + p["c"], "The fold starts at 0 and adds the items."),
    D("num sum<T extends num>(List<T> xs) => xs.fold<num>(0, (a, b) => a + b);\nvoid main() => print(sum([$a, 0.5]));", lambda p: p["a"] + 0.5, "The list has a double, so the total is a double."),
    D("T maxOf<T extends Comparable<T>>(List<T> xs) => xs.reduce((a, b) => a.compareTo(b) >= 0 ? a : b);\nvoid main() => print(maxOf(['$w', '$v']));", lambda p: max(p["w"], p["v"]), "Strings are Comparable, and the later one in dictionary order wins."),
    D("class Sum<T extends num> {\n  T a, b;\n  Sum(this.a, this.b);\n  num get total => a + b;\n}\nvoid main() => print(Sum($a, $b).total);", lambda p: p["a"] + p["b"], "The bound num makes + legal on T."),
    # ── generic classes ──
    D("class Box<T> { T v; Box(this.v); }\nvoid main() => print(Box($a).v.runtimeType);", "int", VALUE),
    D("class Box<T> { T v; Box(this.v); }\nvoid main() => print(Box<num>($a).v.runtimeType);", "int", "The box is a Box<num>, but the value inside is still the int."),
    D("class Box<T> { T v; Box(this.v); }\nvoid main() => print(Box($a) is Box<int>);", True, "T was inferred as int from the argument."),
    D("class Box<T> { T v; Box(this.v); }\nvoid main() => print(Box($a) is Box<num>);", True, "A Box<int> is also a Box<num>."),
    D("class Box<T> { T v; Box(this.v); }\nvoid main() => print(Box<num>($a) is Box<int>);", False, "It was made as a Box<num>, whatever is inside."),
    D("class Box<T> { T v; Box(this.v); }\nvoid main() => print(Box<Object>('$w') is Box<String>);", False, "It was made as a Box<Object>."),
    D("class Box<T> { T v; Box(this.v); }\nvoid main() => print(Box<int>($a) is Box<String>);", False, "int and String have nothing in common."),
    D("class Pair<A, B> {\n  A a; B b;\n  Pair(this.a, this.b);\n  Pair<B, A> swap() => Pair(b, a);\n}\nvoid main() => print(Pair($a, '$w').swap().a);", lambda p: p["w"], "swap turns Pair<int, String> into Pair<String, int>, so a is the word."),
    D("class Pair<A, B> {\n  A a; B b;\n  Pair(this.a, this.b);\n  Pair<B, A> swap() => Pair(b, a);\n}\nvoid main() => print(Pair($a, '$w').swap().b.runtimeType);", "int", "After the swap, b holds the old a, an int."),
    D("class Stack<T> {\n  final _items = <T>[];\n  void push(T x) => _items.add(x);\n  T pop() => _items.removeLast();\n}\nvoid main() => print((Stack<int>()..push($a)..push($b)).pop());", lambda p: p["b"], "A stack gives back the last item pushed."),
    # ── is checks on collection types ──
    D("void main() => print([$a, $b] is List<int>);", True, "A list of ints is a List<int>."),
    D("void main() => print([$a, 2.5] is List<int>);", False, "Dart works out List<num>, because 2.5 is not an int."),
    D("void main() => print([$a, 2.5] is List<num>);", True, "The literal mixes an int and a double, so it is a List<num>."),
    D("void main() => print(<num>[$a, $b] is List<int>);", False, "It was made as a List<num>, though every item is an int."),
    D("void main() => print(<int>[$a] is List<num>);", True, "A List<int> counts as a List<num>."),
    D("void main() => print(<int>[$a] is List<String>);", False, "int is not String."),
    D("void main() => print(['$w', $a] is List<Object>);", True, "The mixed literal is List<Object>."),
    D("void main() => print(['$w', $a] is List<int>);", False, "One item is a string."),
    D("void main() {\n  var xs = [];\n  print(xs is List<int>);\n}", False, "An empty literal with no hint is a List<dynamic>."),
    D("void main() {\n  List<int> xs = [];\n  print(xs is List<int>);\n}", True, "The declared type makes the empty list a List<int>."),
    D("void main() => print({'$w': $a} is Map<String, int>);", True, "Keys are strings and values are ints."),
    D("void main() => print({'$w': $a} is Map<String, String>);", False, "The value is an int."),
    D("void main() => print(<String, int>{} is Map<String, num>);", True, "A Map<String, int> counts as a Map<String, num>."),
    D("void main() => print({'$w': $a, '$v': 'x'} is Map<String, Object>);", True, "Mixed values give Map<String, Object>."),
    D("void main() => print({$a, $b} is Set<int>);", True, "A set of ints is a Set<int>."),
    D("void main() {\n  List<int> xs = [$a];\n  List<Object> ys = xs;\n  print(ys is List<int>);\n}", True, "ys is the very same list, and it is still a List<int>."),
    D("void main() {\n  Iterable<int> xs = [$a, $b];\n  print(xs is List<int>);\n}", True, "The variable says Iterable, but the object is a list."),
    D("void main() {\n  Iterable<int> xs = {$a, $b};\n  print(xs is List<int>);\n}", False, "The object is a Set, not a List."),
    D("void main() {\n  Iterable<int> xs = [$a, $b].map((x) => x);\n  print(xs is List<int>);\n}", False, "map gives a lazy Iterable, not a List."),
    D("void main() {\n  List<Object> xs = <int>[$a];\n  try { xs.add('$w'); print('ok'); } on TypeError { print('type error'); }\n}", "type error", "The list is really a List<int>, so adding a string fails at run time."),
    D("void main() {\n  List<Object> xs = <int>[$a];\n  try { xs.add($b); print('ok'); } on TypeError { print('type error'); }\n}", "ok", "An int fits the List<int> that is really there."),
    D("void main() {\n  List<Object> xs = [$a];\n  try { xs.add('$w'); print('ok'); } on TypeError { print('type error'); }\n}", "ok", "The declared List<Object> makes the literal a List<Object>, so anything fits."),
    D("void main() {\n  List<dynamic> xs = [$a, '$w', $b + 0.5];\n  print(xs.whereType<int>().length);\n}", 1, "whereType<int> keeps only the items that are ints."),
    D("void main() {\n  List<dynamic> xs = [$a, '$w', $b + 0.5];\n  print(xs.whereType<num>().length);\n}", 2, "An int and a double are both nums."),
    D("void main() {\n  List<Object?> xs = [$a, null, '$w'];\n  print(xs.whereType<Object>().length);\n}", 2, "null is not an Object, so whereType<Object> skips it."),
    # ── type parameters at run time, and inference ──
    D("bool same<T>(Object o) => o is T;\nvoid main() => print(same<int>($a));", True, "T is int and the value is an int."),
    D("bool same<T>(Object o) => o is T;\nvoid main() => print(same<num>($a));", True, "An int is a num."),
    D("bool same<T>(Object o) => o is T;\nvoid main() => print(same<double>($a));", False, "$a is an int, not a double."),
    D("bool same<T>(Object o) => o is T;\nvoid main() => print(same<String>($a));", False, "$a is an int, not a String."),
    D("bool same<T>(Object? o) => o is T;\nvoid main() => print(same<int?>(null));", True, "int? allows null."),
    D("bool same<T>(Object? o) => o is T;\nvoid main() => print(same<int>(null));", False, "null is not an int."),
    D("String name<T>() => T.toString();\nvoid main() => print(name<int>());", "int", "T.toString() is the name of the type."),
    D("String name<T>() => T.toString();\nvoid main() => print(name<String>());", "String", "T.toString() is the name of the type."),
    D("String name<T>() => T.toString();\nvoid main() => print(name<double>());", "double", "T.toString() is the name of the type."),
    D("void main() {\n  var x = $a;\n  print(x.runtimeType);\n}", "int", "An int literal makes an int."),
    D("void main() {\n  var x = $a / $b;\n  print(x.runtimeType);\n}", "double", "/ always gives a double."),
    D("void main() {\n  var x = $a ~/ $b;\n  print(x.runtimeType);\n}", "int", "~/ divides and cuts to an int."),
    D("void main() {\n  var x = $a > $b;\n  print(x.runtimeType);\n}", "bool", "A comparison gives a bool."),
    D("void main() {\n  var x = $a + 0.5;\n  print(x.runtimeType);\n}", "double", "int + double is a double."),
    D("void main() {\n  var x = '$w';\n  print(x.runtimeType);\n}", "String", "A quoted literal is a String."),
    D("void main() {\n  var x = $a > $b ? 1 : 2.5;\n  print(x.runtimeType);\n}", lambda p: "int" if p["a"] > p["b"] else "double", "The chosen branch decides the type of the value."),
    D("void main() {\n  double d = $a;\n  print(d);\n}", lambda p: float(p["a"]), "An int literal where a double is expected becomes a double."),
    D("void main() {\n  num n = $a;\n  print(n.runtimeType);\n}", "int", "num is the declared type; the value is an int."),
    D("void main() {\n  num n = $a;\n  print(n is double);\n}", False, "The value is an int."),
    D("void main() {\n  num n = $a;\n  print((n / 2).runtimeType);\n}", "double", "/ gives a double even for an int."),
    D("void main() {\n  int? x;\n  print(x.runtimeType);\n}", "Null", "null has its own type, Null."),
    D("void main() {\n  Object? o;\n  print(o is Object);\n}", False, "null is not an Object."),
    D("void main() {\n  dynamic d = '$w';\n  print(d.length);\n}", lambda p: len(p["w"]), "dynamic skips the check; at run time d is a String with a length."),
]
