"""Dart types pack, part 3: Abstract and Implements - abstract classes, `implements` versus `extends`, and what a call reaches.

The rules the templates drill: an abstract class can hold real code that calls its own abstract methods (the template
method pattern); `extends` INHERITS the bodies of the parent, while `implements` only promises the parent's shape, so
every member must be written again and the parent's bodies and constructors are never used; a call goes to the object's
real class, whatever the variable's type says. Also the object protocol: `toString`, `==` with `hashCode`, `compareTo`
with `sort`, operators, and `call`.
"""

from __future__ import annotations

from ._dart_model import D
from ._model import Maker

DISPATCH = "The call goes to the real class of the object, whatever type the variable has."
IMPL = "implements takes the shape of the other class but none of its code, so B has to write its own."

ABSTRACTS: list[Maker] = [
    D("abstract class S { int area(); }\nclass Sq extends S { int s; Sq(this.s); int area() => s * s; }\nvoid main() => print(Sq($a).area());", lambda p: p["a"] ** 2, "Sq fills in the abstract method."),
    D("abstract class A { String name(); String hi() => 'hi ' + name(); }\nclass B extends A { String name() => '$w'; }\nvoid main() => print(B().hi());", lambda p: "hi " + p["w"], "hi is real code in A, and it calls the name that B supplies."),
    D("abstract class A { int get n; String show() => 'n=' + n.toString(); }\nclass B extends A { int get n => $a; }\nvoid main() => print(B().show());", lambda p: f"n={p['a']}", "An abstract getter is filled in by the subclass, and show uses it."),
    D("abstract class A { int x; A(this.x); }\nclass B extends A { B() : super($a); }\nvoid main() => print(B().x);", lambda p: p["a"], "An abstract class can have a constructor, and the subclass calls it with super."),
    D("abstract class A { String hi() => '$s1'; }\nclass B extends A { String hi() => super.hi() + '$s2'; }\nvoid main() => print(B().hi());", lambda p: p["s1"] + p["s2"], "An abstract class can have real methods, and super reaches them."),
    D("abstract class A { String a(); String b(); }\nabstract class B extends A { String a() => '$s1'; }\nclass C extends B { String b() => '$s2'; }\nvoid main() => print(C().a() + C().b());", lambda p: p["s1"] + p["s2"], "The abstract methods are filled in one by one down the chain."),
    D("abstract class U { static int twice(int x) => x * 2; }\nvoid main() => print(U.twice($a));", lambda p: 2 * p["a"], "A static method is called on the class itself, so the class needs no object."),
    D("abstract class S { int area(); }\nclass Sq extends S { int s; Sq(this.s); int area() => s * s; }\nclass Tw extends S { int s; Tw(this.s); int area() => s * 2; }\nvoid main() => print(Sq($a).area() + Tw($b).area());", lambda p: p["a"] ** 2 + 2 * p["b"], "Each class uses its own area."),
    # ── extends versus implements ──
    D("class A { String hi() => '$s1'; }\nclass B extends A {}\nvoid main() => print(B().hi());", lambda p: p["s1"], "extends inherits the body of hi."),
    D("class A { String hi() => '$s1'; }\nclass B implements A { String hi() => '$s2'; }\nvoid main() => print(B().hi());", lambda p: p["s2"], IMPL),
    D("class A { String a() => 'A'; String both() => a() + a(); }\nclass B extends A { String a() => '$s1'; }\nvoid main() => print(B().both());", lambda p: p["s1"] + p["s1"], "both is inherited and calls a, which B has replaced."),
    D("class A { String a() => 'A'; String both() => a() + a(); }\nclass B implements A {\n  String a() => '$s1';\n  String both() => '$s2';\n}\nvoid main() => print(B().both());", lambda p: p["s2"], IMPL),
    D("var s = '';\nclass A { A() { s += 'A'; } }\nclass B extends A { B() { s += 'B'; } }\nvoid main() { B(); print(s); }", "AB", "extends runs the parent's constructor first."),
    D("var s = '';\nclass A { A() { s += 'A'; } }\nclass B implements A { B() { s += 'B'; } }\nvoid main() { B(); print(s); }", "B", "implements takes no code from A, not even its constructor."),
    D("class A { final int x; A(this.x); }\nclass B implements A { int get x => $a; }\nvoid main() => print(B().x);", lambda p: p["a"], "A field of the interface is implemented by a getter."),
    D("abstract class A { int get n; set n(int v); }\nclass B implements A { int n = 0; }\nvoid main() => print((B()..n = $a).n);", lambda p: p["a"], "One plain field supplies both the getter and the setter."),
    D("class A {}\nclass B implements A {}\nvoid main() => print(B() is A);", True, "implements makes B a subtype of A."),
    D("class A {}\nclass B implements A {}\nvoid main() => print(A() is B);", False, "A plain A is not a B."),
    D("abstract class A { String a(); }\nabstract class B { String b(); }\nclass C implements A, B {\n  String a() => '$s1';\n  String b() => '$s2';\n}\nvoid main() => print(C().a() + C().b());", lambda p: p["s1"] + p["s2"], "A class can implement several interfaces, and must write them all."),
    D("abstract class A { String a(); }\nabstract class B { String b(); }\nclass C implements A, B {\n  String a() => 'x';\n  String b() => 'y';\n}\nvoid main() => print(C() is A && C() is B);", True, "C is a subtype of both interfaces."),
    D("abstract interface class Shape { int area(); }\nclass Sq implements Shape { int s; Sq(this.s); int area() => s * s; }\nvoid main() => print(Sq($a).area());", lambda p: p["a"] ** 2, "An abstract interface class is only a promise; Sq writes the code."),
    D("abstract class N { String n(); }\nenum E implements N { a, b; String n() => name + '!'; }\nvoid main() => print(E.b.n());", "b!", "An enum can implement an interface and write its method."),
    D("abstract class Box<T> { T get v; }\nclass IntBox implements Box<int> { int get v => $a; }\nvoid main() => print(IntBox().v + 1);", lambda p: p["a"] + 1, "Box<int> fixes T to int, so v is an int."),
    # ── calling through the interface type ──
    D("abstract class Pet { String say(); }\nclass Dog implements Pet { String say() => '$w'; }\nclass Cat implements Pet { String say() => '$v'; }\nvoid main() => print(<Pet>[Dog(), Cat()].map((p) => p.say()).join(' '));", lambda p: p["w"] + " " + p["v"], DISPATCH),
    D("abstract class Pet { String say(); }\nclass Dog implements Pet { String say() => '$w'; }\nvoid main() {\n  Pet p = Dog();\n  print(p.say());\n}", lambda p: p["w"], DISPATCH),
    D("abstract class Pet { String say(); }\nclass Dog implements Pet { String say() => '$w'; }\nvoid main() {\n  Object o = Dog();\n  print(o is Pet ? (o as Pet).say() : 'no');\n}", lambda p: p["w"], "The object is a Dog, so it is a Pet, and as Pet lets us call say."),
    D("abstract class Pet { String say(); }\nclass Dog implements Pet { String say() => 'woof'; }\nvoid main() {\n  Object o = 'hello';\n  print(o is Pet ? 'pet' : 'no');\n}", "no", "A string is not a Pet."),
    D("abstract class A { int f([int x = 1]); }\nclass B implements A { int f([int x = $a]) => x * 2; }\nvoid main() {\n  A a = B();\n  print(a.f());\n}", lambda p: 2 * p["a"], "The default value comes from the method that runs, which is B's."),
    D("abstract class A { String hi() => 'A'; }\nclass B extends A { String hi() => 'B'; }\nclass C extends B {}\nvoid main() {\n  A a = C();\n  print(a.hi());\n}", "B", "C inherits B's hi, which replaced A's."),
    # ── the object protocol ──
    D("class Adder { int n; Adder(this.n); int call(int x) => x + n; }\nvoid main() => print(Adder($a)($b));", lambda p: p["a"] + p["b"], "An object with a call method is called like a function."),
    D("class Adder { int n; Adder(this.n); int call(int x) => x + n; }\nvoid main() => print([$b, $c].map(Adder($a)).toList());", lambda p: [p["b"] + p["a"], p["c"] + p["a"]], "An object with call can be passed where a function is wanted."),
    D("class V implements Comparable<V> {\n  int n; V(this.n);\n  int compareTo(V o) => n - o.n;\n}\nvoid main() => print(([V($a), V($b), V($c)]..sort()).first.n);", lambda p: min(p["a"], p["b"], p["c"]), "sort uses compareTo, so the smallest n comes first."),
    D("class V implements Comparable<V> {\n  int n; V(this.n);\n  int compareTo(V o) => o.n - n;\n}\nvoid main() => print(([V($a), V($b), V($c)]..sort()).first.n);", lambda p: max(p["a"], p["b"], p["c"]), "compareTo is reversed, so the biggest n comes first."),
    D("class P {\n  int x; P(this.x);\n  bool operator ==(Object o) => o is P && o.x == x;\n  int get hashCode => x;\n}\nvoid main() => print({P($a), P($a), P($b)}.length);", 2, "A set drops items that are == with the same hashCode."),
    D("class P {\n  int x; P(this.x);\n  bool operator ==(Object o) => o is P && o.x == x;\n  int get hashCode => x;\n}\nvoid main() => print({P($a): 'hit'}[P($a)]);", "hit", "The key P(a) is found because == and hashCode agree."),
    D("class P {\n  int x; P(this.x);\n}\nvoid main() => print({P($a): 'hit'}[P($a)]);", None, "Without == and hashCode, two P objects are different keys."),
    D("class P {\n  int x; P(this.x);\n  bool operator ==(Object o) => o is P && o.x == x;\n  int get hashCode => x;\n}\nvoid main() => print([P($a), P($b)].contains(P($b)));", True, "contains uses ==, which compares x."),
    D("class P {\n  int x; P(this.x);\n}\nvoid main() {\n  var p = P($a);\n  print(p == p);\n}", True, "An object is always == itself."),
    D("class P {\n  int x; P(this.x);\n  String toString() => 'P($$x)';\n}\nvoid main() => print('got $${P($a)}');", lambda p: f"got P({p['a']})", "Interpolation calls toString."),
    D("class P {\n  int x; P(this.x);\n  String toString() => 'P$$x';\n}\nvoid main() => print([P($a), P($b)]);", lambda p: f"[P{p['a']}, P{p['b']}]", "A list prints its items with toString."),
    D("abstract class A { String toString() => '$s1'; }\nclass B extends A {}\nvoid main() => print(B());", lambda p: p["s1"], "B inherits the toString of A."),
    D("class V {\n  int x; V(this.x);\n  V operator *(int k) => V(x * k);\n}\nvoid main() => print((V($a) * $b).x);", lambda p: p["a"] * p["b"], "operator * defines what V * int means."),
    D("class V {\n  int x; V(this.x);\n  V operator -() => V(-x);\n}\nvoid main() => print((-V($a)).x);", lambda p: -p["a"], "The unary minus operator is written operator -()."),
    D("class Row {\n  List<int> xs; Row(this.xs);\n  int operator [](int i) => xs[i] * 2;\n}\nvoid main() => print(Row([$a, $b, $c])[1]);", lambda p: 2 * p["b"], "[] on a Row runs operator [], which doubles the item."),
    D("class Row {\n  List<int> xs; Row(this.xs);\n  int get length => xs.length;\n  int operator [](int i) => xs[i];\n}\nvoid main() => print(Row([$a, $b, $c])[Row([$a, $b]).length]);", lambda p: p["c"], "The inner Row has 2 items, so the outer index is 2."),
]
