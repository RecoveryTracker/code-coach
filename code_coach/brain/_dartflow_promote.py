"""Dart flow pack, part 3: Promote Or Not - does it compile and run? (null-safety flow analysis)

A pick between "fine" and "error" (oracle `error`: the snippet as shown either runs quietly or does not compile or
throws). The rules the answers come from, all checked by the real compiler:

* a nullable LOCAL variable is *promoted* to its non-null type after a check the compiler can follow: `if (x != null)`,
  an early `return`/`throw` when it is null, `&&` / `||` / `?:`, `x!`, `x ??= v`, `x is int`, a pattern `case int y`;
* the *initialiser* promotes too: `int? x = 5;` is an `int` from there on (until it is assigned something nullable);
* assigning `null` (or any nullable value) takes the promotion away again;
* things that are not plain local variables do not promote: a map lookup, a list element, a public or non-final
  field, a top-level variable (a private FINAL field does promote since Dart 3.2);
* `!` on a null, a late variable that was never set, a missing key with `update`... fail when the line RUNS.
"""

from __future__ import annotations

from ._dartflow_model import F
from ._model import Maker

FIND = "int? find() => $a;\n"
NAME = "String? name() => '$w';\n"


def FE2(fmt: str, bad: bool, why: str) -> Maker:
    return F(fmt, lambda p: "error" if bad else "fine", why)


LOCAL_X = FIND + "int? x = find();\n"
STR_S = NAME + "String? s = name();\n"
NOPROMO = "find() might give null, so x is still int? and + is not allowed."

PROMOTE: list[Maker] = [
    # ── a nullable int local ──
    FE2("int? x = $a;\nprint(x + 1);", False, "The initial value is not null, so x is promoted to int right away."),
    FE2(LOCAL_X + "print(x + 1);", True, NOPROMO),
    FE2(LOCAL_X + "if (x != null) print(x + 1);", False, "Inside the if, x is known not to be null."),
    FE2(LOCAL_X + "if (x == null) return;\nprint(x + 1);", False, "After the early return, x cannot be null."),
    FE2(LOCAL_X + "if (x == null) print('$w');\nprint(x + 1);", True, "The if only prints; the code carries on, so x may still be null."),
    FE2(LOCAL_X + "if (x == null) throw '$w';\nprint(x + 1);", False, "A throw leaves the code, so after it x is not null."),
    FE2(LOCAL_X + "x!;\nprint(x + 1);", False, "x! passes only if x is not null, so after it x is promoted."),
    FE2("int? x;\nx ??= $a;\nprint(x + 1);", False, "After ??= with a non-null value, x is an int."),
    FE2(FIND + "int? x;\nx ??= find();\nprint(x + 1);", True, "find() may be null, so x may still be null after ??=."),
    FE2(LOCAL_X + "x = x ?? 0;\nprint(x + 1);", False, "x ?? 0 is never null, so x is an int after the assignment."),
    FE2(LOCAL_X + "if (x != null || x > $b) print('$w');", True, "|| tries the right side when the left is false, that is, when x IS null."),
    FE2(LOCAL_X + "if (x == null || x > $b) print('$w');", False, "The right side of || only runs when x is not null."),
    FE2(LOCAL_X + "if (x != null && x > $b) print('$w');", False, "The right side of && only runs when x is not null."),
    FE2(LOCAL_X + "if (x == null && x > $b) print('$w');", True, "The right side of && runs when x IS null."),
    FE2(LOCAL_X + "print(x != null ? x + 1 : 0);", False, "The ? branch is only reached when x is not null."),
    FE2(LOCAL_X + "print(x == null ? x + 1 : 0);", True, "The ? branch is the one where x is null."),
    FE2(LOCAL_X + "print(x == null ? 0 : x + 1);", False, "The : branch is only reached when x is not null."),
    FE2(LOCAL_X + "if (x != null) {\n  x = null;\n  print(x + 1);\n}", True, "Assigning null takes the promotion away."),
    FE2(LOCAL_X + "if (x != null) {\n  x = find();\n  print(x + 1);\n}", True, "An assignment of a nullable value takes the promotion away."),
    FE2(LOCAL_X + "x = null;\nprint(x + 1);", True, "x holds null now, and + on a nullable is not allowed."),
    FE2(LOCAL_X + "if (x != null) {\n  var f = () => x + 1;\n  print(f());\n}", False, "x is never assigned after the closure, so it stays promoted inside it."),
    FE2(LOCAL_X + "if (x != null) {\n  var f = () => x + 1;\n  x = null;\n  print(f());\n}", True, "x is assigned after the closure is made, so the closure cannot rely on it."),
    FE2(LOCAL_X + "if (x == $a) print(x + 1);", True, "Comparing with a number does not promote: x is still int?."),
    FE2(LOCAL_X + "if (x is int) print(x + 1);", False, "x is int means it is not null."),
    FE2(LOCAL_X + "if (x case int y) print(y + 1);", False, "The pattern case int y only matches a non-null int and names it y."),
    FE2(LOCAL_X + "var l = [if (x != null) x + 1];\nprint(l);", False, "The check promotes x inside the collection-if."),
    FE2(LOCAL_X + "var l = [x + 1];\nprint(l);", True, "Nothing promotes x here."),
    FE2(LOCAL_X + "while (x != null) {\n  print(x + 1);\n  break;\n}", False, "Inside the loop body, the condition has promoted x."),
    FE2(LOCAL_X + "for (var i = 0; i < 2; i++) {\n  print(x + 1);\n  x = find();\n}", True, "x is assigned inside the loop, so it is not promoted at the top of a turn."),
    FE2(FIND + "final int? y = find();\nif (y != null) print(y + 1);", False, "A final variable promotes like any other."),
    # ── a nullable String local ──
    FE2("String? s = '$w';\nprint(s.length);", False, "The initial value is not null, so s is promoted to String."),
    FE2(STR_S + "print(s.length);", True, "name() might give null, so s is still String? and .length is not allowed."),
    FE2(STR_S + "print(s!.length);", False, "s! says it is not null, and it is not."),
    FE2(STR_S + "print(s?.length);", False, "?. is allowed on a nullable and gives an int?."),
    FE2(STR_S + "int n = s?.length;", True, "s?.length can be null, and an int cannot hold null."),
    FE2(STR_S + "int n = s?.length ?? 0;\nprint(n);", False, "?? 0 removes the null, so n is an int."),
    FE2("String? s = null;\nprint(s.length);", True, "s holds null, so it is promoted to Null: there is no length."),
    FE2("String? s = '$w';\ns = null;\nprint(s.length);", True, "Assigning null takes the promotion away."),
    FE2(STR_S + "print(s?.toUpperCase().length);", False, "One ?. shortcuts the whole chain: if s is null, the rest is skipped."),
    FE2(STR_S + "print((s?.toUpperCase()).length);", True, "The brackets end the shortcut: the length is asked of a String? that may be null."),
    FE2("String s = '$w';\nprint(s?.length);", False, "?. on a value that cannot be null is allowed (the compiler only warns)."),
    FE2("String s = null;", True, "A String cannot hold null."),
    # ── Object and is ──
    FE2("Object o = $a;\nprint(o + 1);", True, "o is typed Object, and Object has no +."),
    FE2("Object o = $a;\nif (o is int) print(o + 1);", False, "is int promotes o to int inside the if."),
    FE2("Object o = $a;\no as int;\nprint(o + 1);", False, "After a successful cast, o is promoted to int."),
    FE2("Object o = $a;\nif (o is! int) return;\nprint(o + 1);", False, "After the early return, o must be an int."),
    FE2("Object o = $a;\nif (o is int || o is String) print(o.length);", True, "o could be the int, and an int has no length."),
    # ── maps and lists ──
    FE2("var m = {'$w': $a};\nint x = m['$w'];", True, "A map lookup gives int?, even for a key that is there."),
    FE2("var m = {'$w': $a};\nint x = m['$w']!;\nprint(x);", False, "The key is there, so the ! passes."),
    FE2("var m = {'$w': $a};\nint x = m['$v']!;\nprint(x);", True, "The key is missing: the lookup is null and ! throws."),
    FE2("var m = {'$w': $a};\nint x = m['$v'] ?? 0;\nprint(x);", False, "The missing key gives null and ?? supplies 0."),
    FE2("var m = {'$w': $a};\nif (m['$w'] != null) print(m['$w'] + 1);", True, "A map lookup is not a variable: asking twice is not promoted."),
    FE2("var m = {'$w': $a};\nvar v = m['$w'];\nif (v != null) print(v + 1);", False, "Copy the value into a local variable and the local promotes."),
    FE2("List<int>? xs;\nxs.add($a);", True, "xs may be null, so a method call needs ?. or a check."),
    FE2("List<int>? xs;\nxs?.add($a);\nprint(xs);", False, "?. skips the call when xs is null."),
    FE2("List<int>? xs;\nxs!.add($a);", True, "xs is null, so the ! throws."),
    FE2("List<int>? xs = [$a];\nxs.add($b);\nprint(xs);", False, "The initial list is not null, so xs is promoted to List<int>."),
    FE2("List<int?> xs = [$a, null];\nint s = xs[0] + 1;", True, "An element of a List<int?> is an int?."),
    FE2("List<int?> xs = [$a, null];\nint s = xs[0]! + 1;\nprint(s);", False, "The first element is there, so the ! passes."),
    FE2("List<int?> xs = [$a, null];\nint s = xs[1]! + 1;", True, "The second element is null, so the ! throws."),
    FE2("List<int?> xs = [$a, null];\nList<int> ys = xs;", True, "A List<int?> is not a List<int>."),
    FE2("List<int?> xs = [$a, null];\nvar ys = xs.whereType<int>().toList();\nprint(ys);", False, "whereType<int>() keeps only the ints and gives a List<int>."),
    FE2("List<String?> names = ['$w', null];\nfor (var n in names) {\n  print(n.length);\n}", True, "n is a String? in every turn."),
    FE2("List<String?> names = ['$w', null];\nfor (var n in names) {\n  if (n != null) print(n.length);\n}", False, "The check promotes the loop variable n."),
    FE2("List<int>? xs;\nprint([...xs]);", True, "A spread of a nullable list needs ...? instead of ..."),
    FE2("List<int>? xs;\nprint([...?xs]);", False, "...? spreads nothing when the list is null."),
    FE2("Map<String, int> m = {'$w': $a};\nm['$w'] += 1;", True, "m['$w'] is an int?, and += needs a number."),
    FE2("Map<String, int> m = {'$w': $a};\nm['$v'] = (m['$v'] ?? 0) + 1;\nprint(m);", False, "?? 0 gives a number to add to."),
    FE2("Map<String, int> m = {'$w': $a};\nm.update('$v', (v) => v + 1);", True, "update on a missing key without ifAbsent throws."),
    # ── definite assignment and late ──
    FE2("var a = $a;\nint x;\nif (a > $b) x = 1;\nprint(x);", True, "If the condition is false, x was never set."),
    FE2("var a = $a;\nint x;\nif (a > $b) x = 1; else x = 2;\nprint(x);", False, "Both branches set x."),
    FE2("int x;\nx = $a;\nprint(x);", False, "x is set before it is read."),
    FE2("int x;\nprint(x);", True, "A non-nullable variable must be set before it is read."),
    FE2("int? x;\nprint(x);", False, "A nullable variable starts as null."),
    FE2("late int x = $a;\nprint(x);", False, "A late variable with an initialiser is set the first time it is read."),
    FE2("late int x;\nvoid setIt() { x = $a; }\nsetIt();\nprint(x);", False, "The function sets x before it is read."),
    FE2("late int x;\nvoid setIt() { x = $a; }\nprint(x);", True, "setIt() is never called, so the late variable is read before it was set."),
    FE2("late final int x;\nx = $a;\nx = $b;", True, "A late final can be set only once."),
    # ── parameters ──
    FE2("void f(int n) => print(n);\nvoid main() {\n  f();\n}", True, "A required positional parameter must be given."),
    FE2("void f([int n]) => print(n);\nvoid main() {\n  f();\n}", True, "An optional parameter of a non-nullable type needs a default value."),
    FE2("void f([int n = $a]) => print(n);\nvoid main() {\n  f();\n}", False, "The default value fills in."),
    FE2("void f([int? n]) => print(n);\nvoid main() {\n  f();\n}", False, "An optional nullable parameter defaults to null."),
    FE2("void f({int n}) => print(n);\nvoid main() {\n  f();\n}", True, "A named parameter of a non-nullable type needs required or a default."),
    FE2("void f({required int n}) => print(n);\nvoid main() {\n  f();\n}", True, "required means the caller must give it."),
    FE2("void f({required int n}) => print(n);\nvoid main() {\n  f(n: $a);\n}", False, "The required named argument is given."),
    FE2("void f({int? n}) => print(n);\nvoid main() {\n  f();\n}", False, "A nullable named parameter may be left out."),
    FE2("void f(int n) => print(n);\nvoid main() {\n  f(null);\n}", True, "null does not fit an int parameter."),
    FE2("void f(int? n) {\n  print(n + 1);\n}\nvoid main() {\n  f($a);\n}", True, "n is an int? inside f, whatever was passed."),
    FE2("void f(int? n) {\n  if (n == null) return;\n  print(n + 1);\n}\nvoid main() {\n  f($a);\n}", False, "A parameter promotes like a local variable."),
    FE2("void f(int? n) {\n  n ??= 0;\n  print(n + 1);\n}\nvoid main() {\n  f(null);\n}", False, "n ??= 0 makes sure n is an int afterwards."),
    FE2("void f(int? n) {\n  bool b = n?.isEven;\n}\nvoid main() {\n  f($a);\n}", True, "n?.isEven is a bool?, which a bool cannot hold."),
    FE2("int f(int? n) {\n  if (n != null) return n;\n}\nvoid main() {\n  print(f($a));\n}", True, "If n is null the function ends without returning an int."),
    FE2("int f(int? n) {\n  if (n != null) return n;\n  return 0;\n}\nvoid main() {\n  print(f($a));\n}", False, "Every path returns an int."),
    # ── fields ──
    FE2("class ${W} {\n  int? n;\n  ${W}(this.n);\n}\nvoid main() {\n  var b = ${W}($a);\n  if (b.n != null) print(b.n + 1);\n}", True,
        "A public field can be changed by anyone, so it never promotes."),
    FE2("class ${W} {\n  final int? n;\n  ${W}(this.n);\n}\nvoid main() {\n  var b = ${W}($a);\n  if (b.n != null) print(b.n + 1);\n}", True,
        "A public final field still does not promote: a subclass could override it."),
    FE2("class ${W} {\n  final int? _n;\n  ${W}(this._n);\n  void show() {\n    if (_n != null) print(_n + 1);\n  }\n}\nvoid main() {\n  ${W}($a).show();\n}", False,
        "A private final field cannot be overridden or changed, so Dart 3.2 and later promote it."),
    FE2("class ${W} {\n  int? _n;\n  ${W}(this._n);\n  void show() {\n    if (_n != null) print(_n + 1);\n  }\n}\nvoid main() {\n  ${W}($a).show();\n}", True,
        "A private field that is not final can change between the check and the use."),
    FE2("class ${W} {\n  int? n;\n  ${W}(this.n);\n  void show() {\n    var m = n;\n    if (m != null) print(m + 1);\n  }\n}\nvoid main() {\n  ${W}($a).show();\n}", False,
        "Copy the field into a local variable and the local promotes."),
    FE2("class ${W} {\n  int? n;\n  ${W}(this.n);\n  void show() {\n    if (n != null) print(n! + 1);\n  }\n}\nvoid main() {\n  ${W}($a).show();\n}", False,
        "The ! does the check at run time, and n is not null."),
    FE2("class ${W} {\n  int n;\n}\nvoid main() {\n  print(${W}());\n}", True, "A non-nullable field must be set by the constructor."),
    FE2("class ${W} {\n  int? n;\n}\nvoid main() {\n  print(${W}().n);\n}", False, "A nullable field starts as null."),
    FE2("class ${W} {\n  late int n;\n}\nvoid main() {\n  print(${W}().n);\n}", True, "Nobody set the late field, so reading it throws."),
    FE2("class ${W} {\n  late int n;\n  ${W}() {\n    n = $a;\n  }\n}\nvoid main() {\n  print(${W}().n);\n}", False, "The constructor sets the late field before it is read."),
    FE2("class ${W} {\n  final int n;\n  ${W}();\n}\nvoid main() {\n  print(${W}().n);\n}", True, "A final field must be set by the constructor."),
    FE2("class ${W} {\n  final int n;\n  ${W}(int v) : n = v * 2;\n}\nvoid main() {\n  print(${W}($a).n);\n}", False, "The initialiser list sets the final field."),
    FE2("class ${W} {\n  late final int n;\n  void put() {\n    n = $a;\n  }\n}\nvoid main() {\n  var b = ${W}();\n  b.put();\n  b.put();\n}", True,
        "A late final field can be set only once; the second set throws."),
    FE2("int? g;\nvoid main() {\n  g = $a;\n  if (g != null) print(g + 1);\n}", True, "A top-level variable does not promote: other code could change it."),
    # ── Object? and dynamic ──
    FE2("Object? o;\nprint(o.toString());", False, "Every object, even null, has toString."),
    FE2("Object? o;\nprint(o.length);", True, "Object? has no length, and the compiler checks."),
    FE2("dynamic d = $a;\nprint(d.length);", True, "dynamic skips the compile check, but an int has no length at run time."),
    FE2("dynamic d = '$w';\nprint(d.length);", False, "dynamic skips the check, and a String has a length."),
]
