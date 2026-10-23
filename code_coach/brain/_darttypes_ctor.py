"""Dart types pack, part 8: Ctor Order - what runs first when an object is made?

The order, for `B extends A`: (1) B's field initialisers (`int y = f();`), in the order written; (2) B's initializer
list (`B() : x = ...`), left to right; (3) A's constructor - its field initialisers, its initializer list, and its body;
(4) B's own constructor body. So a subclass's field initialisers run BEFORE the parent's constructor body. A redirecting
constructor (`: this(...)`) runs the target first and then its own body. `late` fields and `static` fields are lazy:
their initialisers run on first use. A `factory` can return an old object; `const` objects with equal arguments are one
object. The log templates share a global string `s` and a helper `f(x)` that appends to it and returns 0.
"""

from __future__ import annotations

from ._dart_model import D
from ._model import Maker

LOG = "var s = '';\nint f(String x) { s += x; return 0; }\n"
FIELDS = "Field initialisers run first, then the initializer list, then the constructor body."
LAZY = "A late field with an initializer, like a static field, runs it only on first use."

CTORS: list[Maker] = [
    # ── the order of things ──
    D(LOG + "class A {\n  int a = f('$s1');\n  int b;\n  A() : b = f('$s2') { s += '$s3'; }\n}\nvoid main() { A(); print(s); }", lambda p: p["s1"] + p["s2"] + p["s3"], FIELDS),
    D(LOG + "class A {\n  int a = f('$s1');\n  int b = f('$s2');\n  A() { s += '$s3'; }\n}\nvoid main() { A(); print(s); }", lambda p: p["s1"] + p["s2"] + p["s3"], "Fields are initialised in the order written, before the body."),
    D("var s = '';\nclass A { A() { s += '$s1'; } }\nclass B extends A { B() { s += '$s2'; } }\nvoid main() { B(); print(s); }", lambda p: p["s1"] + p["s2"], "The parent's constructor body finishes before the child's starts."),
    D("var s = '';\nclass A { A() { s += '$s1'; } }\nclass B extends A { B() { s += '$s2'; } }\nclass C extends B { C() { s += '$s3'; } }\nvoid main() { C(); print(s); }", lambda p: p["s1"] + p["s2"] + p["s3"], "Constructor bodies run from the top of the family down."),
    D(LOG + "class A { A() { s += '$s1'; } }\nclass B extends A {\n  int y = f('$s2');\n  B() { s += '$s3'; }\n}\nvoid main() { B(); print(s); }", lambda p: p["s2"] + p["s1"] + p["s3"], "The child's field initialisers run even before the parent's constructor."),
    D(LOG + "class A { A() { s += '$s1'; } }\nclass B extends A {\n  int y;\n  B() : y = f('$s2'), super() { s += '$s3'; }\n}\nvoid main() { B(); print(s); }", lambda p: p["s2"] + p["s1"] + p["s3"], "The child's initializer list runs, then super(), then the child's body."),
    D("var s = '';\nclass A {\n  A() { s += '$s1'; }\n  A.n() : this();\n}\nvoid main() { A.n(); print(s); }", lambda p: p["s1"], "A redirecting constructor has no body of its own: the target's body is all that runs."),
    D("var s = '';\nclass A {\n  A() { s += '$s1'; }\n  A.n() { s += '$s2'; }\n}\nclass B extends A { B() : super.n(); }\nvoid main() { B(); print(s); }", lambda p: p["s2"], "super.n() picks the named constructor, so A's plain one never runs."),
    D("var s = '';\nclass A { A() { s += '$s1'; } }\nclass B extends A {}\nvoid main() { B(); print(s); }", lambda p: p["s1"], "With no constructor of its own, B calls super() by itself."),
    D("var s = '';\nclass A {\n  A() { s += '$s1'; }\n  A.n() { s += '$s2'; }\n}\nclass B extends A {}\nvoid main() { B(); print(s); }", lambda p: p["s1"], "The implicit constructor calls the unnamed super constructor."),
    D("var s = '';\nint g(String x) { s += x; return 1; }\nclass A { A(int a, int b); }\nvoid main() { A(g('$s1'), g('$s2')); print(s); }", lambda p: p["s1"] + p["s2"], "Arguments are worked out left to right."),
    D("class A {\n  static int c = 0;\n  final int id;\n  A() : id = ++c;\n}\nvoid main() => print('$${A().id}$${A().id}');", "12", "The static counter is shared, and each new object takes the next number."),
    D("class A {\n  static int c = 0;\n  final int id;\n  A() : id = ++c;\n}\nvoid main() {\n  var x = A(), y = A();\n  print(x.id + y.id * 10 + A.c * 100);\n}", 221, "ids are 1 and 2, and the counter ends at 2."),
    # ── lazy things ──
    D(LOG + "class A { static final x = f('$s1'); }\nvoid main() {\n  s += '$s2';\n  A.x;\n  s += '$s3';\n  print(s);\n}", lambda p: p["s2"] + p["s1"] + p["s3"], "A static final field is initialised when it is first used."),
    D(LOG + "class A { static final x = f('$s1'); }\nvoid main() {\n  A.x; A.x; A.x;\n  print(s);\n}", lambda p: p["s1"], "The initialiser runs only once."),
    D(LOG + "class A {\n  static final x = f('$s1');\n  static final y = f('$s2');\n}\nvoid main() {\n  A.y; A.x;\n  print(s);\n}", lambda p: p["s2"] + p["s1"], "Each static is set up when first touched, not in the order written."),
    D(LOG + "final top = f('$s1');\nvoid main() {\n  s += '$s2';\n  top;\n  print(s);\n}", lambda p: p["s2"] + p["s1"], "A top-level final variable is lazy too."),
    D(LOG + "class A {\n  late final int x = f('$s1');\n  A() { s += '$s2'; }\n}\nvoid main() { var a = A(); s += '$s3'; a.x; print(s); }", lambda p: p["s2"] + p["s3"] + p["s1"], LAZY),
    D(LOG + "class A {\n  late final int x = f('$s1');\n  A() { s += '$s2'; }\n}\nvoid main() {\n  A();\n  print(s);\n}", lambda p: p["s2"], "Nobody reads x, so its initialiser never runs."),
    D(LOG + "class A { late final int x = f('$s1'); }\nvoid main() {\n  var a = A();\n  a.x; a.x;\n  print(s);\n}", lambda p: p["s1"], "A late final field is worked out once."),
    D("class A {\n  int a = $a;\n  late int b = a + 1;\n}\nvoid main() => print(A().b);", lambda p: p["a"] + 1, "A late initialiser can read this, which an ordinary one cannot."),
    D("class A {\n  late final int x;\n  A(int v) { x = v * 2; }\n}\nvoid main() => print(A($a).x);", lambda p: 2 * p["a"], "A late final field can be set once, from the constructor body."),
    # ── the forms of a constructor ──
    D("class A {\n  int x, y;\n  A(this.x, [this.y = $b]);\n}\nvoid main() => print(A($a).y);", lambda p: p["b"], "An optional parameter keeps its default."),
    D("class A {\n  int x, y;\n  A(this.x, [this.y = $b]);\n}\nvoid main() => print(A($a, $c).y);", lambda p: p["c"], "The argument replaces the default."),
    D("class A {\n  int x, y;\n  A({this.x = $a, required this.y});\n}\nvoid main() => print(A(y: $b).x + A(y: $b).y);", lambda p: p["a"] + p["b"], "x keeps its default; y was given."),
    D("class A { int x; A(this.x); }\nclass B extends A { B(super.x); }\nvoid main() => print(B($a).x);", lambda p: p["a"], "super.x passes the argument straight to A."),
    D("class A { int x; A(this.x); }\nclass B extends A { B(int v) : super(v + $b); }\nvoid main() => print(B($a).x);", lambda p: p["a"] + p["b"], "The initializer list calls super with the changed value."),
    D("class A {\n  int area; String label;\n  A(int w, int h) : area = w * h, label = 'r$$w';\n}\nvoid main() {\n  var r = A($a, $b);\n  print(r.label + ' ' + r.area.toString());\n}", lambda p: f"r{p['a']} {p['a'] * p['b']}", "The initializer list sets both fields from the parameters."),
    D("class A {\n  int x;\n  A(this.x) { x += $b; }\n}\nvoid main() => print(A($a).x);", lambda p: p["a"] + p["b"], "this.x stores the argument, then the body adds to it."),
    D("class A {\n  int x;\n  A.a() : this.b($a);\n  A.b(int v) : x = v * 2;\n}\nvoid main() => print(A.a().x);", lambda p: 2 * p["a"], "A.a hands over to A.b, which doubles the value."),
    D("class A {\n  int x;\n  A(this.x);\n  A.from(List<int> xs) : x = xs.length;\n}\nvoid main() => print(A.from([$a, $b, $c]).x);", 3, "The named constructor takes the length of the list."),
    D("class A { int x; A(this.x); }\nvoid main() => print([$a, $b].map(A.new).map((o) => o.x).toList());", lambda p: [p["a"], p["b"]], "A.new is the constructor as a function, so map builds one A per number."),
    D("class A {\n  int x;\n  A._(this.x);\n  factory A(int v) => A._(v * $b);\n}\nvoid main() => print(A($a).x);", lambda p: p["a"] * p["b"], "The factory builds the object through the private constructor."),
    # ── factory and cache ──
    D("class A {\n  static final _c = <String, A>{};\n  final String k;\n  A._(this.k);\n  factory A(String k) => _c.putIfAbsent(k, () => A._(k));\n}\nvoid main() => print(identical(A('$w'), A('$w')));", True, "The cache hands back the object it made the first time."),
    D("class A {\n  static final _c = <String, A>{};\n  final String k;\n  A._(this.k);\n  factory A(String k) => _c.putIfAbsent(k, () => A._(k));\n}\nvoid main() => print(identical(A('$w'), A('$v')));", False, "Different keys make different objects."),
    D("class A {\n  static final _c = <String, A>{};\n  static int made = 0;\n  A._() { made++; }\n  factory A(String k) => _c.putIfAbsent(k, A._);\n}\nvoid main() {\n  A('$w'); A('$w'); A('$v');\n  print(A.made);\n}", 2, "Only two different keys, so only two objects are made."),
    D("class A {\n  A() { print('x'); }\n}\nclass B implements A {\n  B();\n}\nvoid main() => print(B() is A);", True, "B implements A, so it is an A, and A's constructor is never called.".replace("x", "x")),
    D("abstract class Sh {\n  factory Sh(int n) => n > $c ? Big() : Small();\n}\nclass Big implements Sh {}\nclass Small implements Sh {}\nvoid main() => print(Sh($a) is Big);", lambda p: p["a"] > p["c"], "A factory can return any subtype of its class."),
    D("var s = '';\nclass S {\n  static final S _i = S._();\n  S._() { s += '$s1'; }\n  factory S() => _i;\n}\nvoid main() { S(); S(); S(); print(s); }", lambda p: p["s1"], "The one instance is made once, the first time it is needed."),
    # ── const ──
    D("class P { final int x; const P(this.x); }\nvoid main() => print(identical(const P($a), const P($a)));", True, "const objects with equal arguments are one object."),
    D("class P { final int x; const P(this.x); }\nvoid main() => print(identical(const P($a), const P($b)));", False, "Different arguments make different constants."),
    D("class P { final int x; const P(this.x); }\nvoid main() => print(identical(P($a), P($a)));", False, "Without const, each call makes a new object."),
    D("class P { final int x; const P(this.x); }\nvoid main() => print(identical(const P($a), P($a)));", False, "One is a shared constant and the other a fresh object."),
    D("class P { final int x; const P(this.x); }\nvoid main() => print(const P($a) == P($a));", False, "== is identity unless the class overrides it."),
    D("class P { final int x; const P(this.x); }\nvoid main() {\n  const a = P($a);\n  const b = P($a);\n  print(identical(a, b));\n}", True, "In a const declaration, P(...) is a constant."),
    D("class P { final int x; const P(this.x); }\nvoid main() {\n  final a = P($a);\n  final b = P($a);\n  print(identical(a, b));\n}", False, "final does not make the call const, so there are two objects."),
    D("class P { final int x; const P(this.x); }\nvoid main() {\n  var c = const [P($a), P($a)];\n  print(identical(c[0], c[1]));\n}", True, "Inside a const list, the items are constants."),
    D("void main() => print(identical(const [$a], const [$a]));", True, "Equal const lists are one list."),
    D("void main() => print(identical([$a], [$a]));", False, "Two list literals are two lists."),
    D("class P {\n  final int x;\n  const P(int a) : x = a * $b;\n}\nvoid main() => print(const P($a).x);", lambda p: p["a"] * p["b"], "A const constructor can still compute with its initializer list."),
    D("class P {\n  final int x, y;\n  P(this.x, this.y);\n  bool operator ==(Object o) => o is P && o.x == x && o.y == y;\n  int get hashCode => Object.hash(x, y);\n}\nvoid main() => print({P($a, $b), P($a, $b), P($b, $a)}.length);", 2, "The first two are equal; the swapped one is not."),
]
