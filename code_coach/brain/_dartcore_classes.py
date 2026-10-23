"""Dart core pack, part 4: Class Check - what do small Dart classes print?

Every prompt is a COMPLETE program ending in `void main() => print(...)` (or a short `main` body), so it is a real
Dart file the learner could save and run. Dart's `$name` interpolation is written `$$name` in these templates (the
`$` of a string.Template hole is doubled to get a literal one).
"""

from __future__ import annotations

from ._dart_model import D
from ._model import Maker

NEW = "A new object is made by calling the class like a function."
OVER = "The subclass's own version replaces the inherited one, even when the variable's type is the parent."

CLASSES: list[Maker] = [
    D("class Box {\n  int w;\n  Box(this.w);\n}\nvoid main() => print(Box($a).w);", lambda p: p["a"], "Box(this.w) stores the argument straight into the field w."),
    D("class Dog {\n  String name;\n  Dog(this.name);\n  String toString() => 'Dog($$name)';\n}\nvoid main() => print(Dog('$w'));", lambda p: f"Dog({p['w']})", "print uses toString(), so the override decides what shows."),
    D("class Dog {\n  String name;\n  Dog(this.name);\n  String toString() => 'Dog($$name)';\n}\nvoid main() => print([Dog('$w')]);", lambda p: f"[Dog({p['w']})]", "A list prints each item with its toString()."),
    D("class Counter {\n  int n;\n  Counter([this.n = $a]);\n}\nvoid main() => print(Counter().n);", lambda p: p["a"], "No argument, so the optional parameter keeps its default."),
    D("class Counter {\n  int n;\n  Counter([this.n = $a]);\n}\nvoid main() => print(Counter($b).n);", lambda p: p["b"], "The argument replaces the default."),
    D("class Pt {\n  int x, y;\n  Pt(this.x, this.y);\n  Pt.origin() : x = 0, y = 0;\n}\nvoid main() => print(Pt.origin().x + Pt($a, $b).y);", lambda p: p["b"], "Pt.origin() is a named constructor that sets both to 0."),
    D("class User {\n  String name;\n  int age;\n  User({required this.name, this.age = $a});\n}\nvoid main() => print(User(name: '$w').age);", lambda p: p["a"], "age was not given, so it keeps its default."),
    D("class Rect {\n  int w, h;\n  Rect(this.w, this.h);\n  int get area => w * h;\n}\nvoid main() => print(Rect($a, $b).area);", lambda p: p["a"] * p["b"], "A getter is read like a field but calculated when asked."),
    D("class Box {\n  int _v = 0;\n  int get v => _v;\n  set v(int x) => _v = x * 2;\n}\nvoid main() {\n  var b = Box()..v = $a;\n  print(b.v);\n}", lambda p: 2 * p["a"], "Assigning to v runs the setter, which doubles it."),
    D("class Foo {\n  static int count = 0;\n  Foo() {\n    count++;\n  }\n}\nvoid main() {\n  for (var i = 0; i < $k + 1; i++) Foo();\n  print(Foo.count);\n}", lambda p: p["k"] + 1, "A static field belongs to the class, so every Foo adds to the same count."),
    D("class M {\n  static int dbl(int x) => x * 2;\n}\nvoid main() => print(M.dbl($a));", lambda p: 2 * p["a"], "A static method is called on the class itself, with no object."),
    D("class C {\n  static const base = $a;\n}\nvoid main() => print(C.base + $b);", lambda p: p["a"] + p["b"], "A static const is a constant that belongs to the class."),
    D("class Pt {\n  final int x;\n  const Pt(this.x);\n}\nvoid main() => print(identical(const Pt($a), const Pt($a)));", True, "Two const objects with the same values are one and the same object."),
    D("class Pt {\n  final int x;\n  Pt(this.x);\n}\nvoid main() => print(Pt($a) == Pt($a));", False, "Without an == override, two separate objects are never equal."),
    D("class Pt {\n  final int x;\n  const Pt(this.x);\n}\nvoid main() => print(const Pt($a) == const Pt($a));", True, "const objects with the same values are the same object, so they are equal."),
    D("class Pt {\n  final int x;\n  Pt(this.x);\n  bool operator ==(Object o) => o is Pt && o.x == x;\n  int get hashCode => x;\n}\nvoid main() => print(Pt($a) == Pt($a));", True, "The == override compares the fields, so equal values are equal."),
    D("class Pt {\n  final int x;\n  Pt(this.x);\n  bool operator ==(Object o) => o is Pt && o.x == x;\n  int get hashCode => x;\n}\nvoid main() => print(Pt($a) == Pt($b));", False, "The x values differ."),
    D("class A {\n  String hi() => 'A';\n}\nclass B extends A {}\nvoid main() => print(B().hi());", "A", "B inherits hi() from A."),
    D("class A {\n  String hi() => 'A';\n}\nclass B extends A {\n  String hi() => 'B';\n}\nvoid main() => print(B().hi());", "B", OVER),
    D("class A {\n  String hi() => 'A';\n}\nclass B extends A {\n  String hi() => 'B';\n}\nvoid main() {\n  A a = B();\n  print(a.hi());\n}", "B", OVER),
    D("class A {\n  String hi() => '$s1';\n}\nclass B extends A {\n  String hi() => super.hi() + '$s2';\n}\nvoid main() => print(B().hi());", lambda p: p["s1"] + p["s2"], "super.hi() runs the parent's version first."),
    D("class A {\n  int x;\n  A(this.x);\n}\nclass B extends A {\n  B(int v) : super(v * 2);\n}\nvoid main() => print(B($a).x);", lambda p: 2 * p["a"], ": super(...) passes the doubled value to the parent's constructor."),
    D("class A {}\nclass B extends A {}\nvoid main() => print(B() is A);", True, "A B is an A, because it extends A."),
    D("class A {}\nclass B extends A {}\nvoid main() => print(A() is B);", False, "A plain A is not a B."),
    D("class A {}\nclass B extends A {}\nvoid main() {\n  A a = B();\n  print(a is B);\n}", True, "The object is really a B, whatever the variable's type says."),
    D("class A {}\nclass B extends A {}\nvoid main() {\n  A a = A();\n  print(a is! B);\n}", True, "is! is true when the object is not that type."),
    D("class A {}\nclass B extends A {\n  int extra = $a;\n}\nvoid main() {\n  A a = B();\n  print((a as B).extra);\n}", lambda p: p["a"], "as B treats the object as a B, which it is, so extra is available."),
    D("abstract class Shape {\n  int area();\n}\nclass Sq extends Shape {\n  int s;\n  Sq(this.s);\n  int area() => s * s;\n}\nvoid main() => print(Sq($a).area());", lambda p: p["a"] ** 2, "Sq fills in the abstract method."),
    D("mixin Walk {\n  String go() => 'walk';\n}\nclass Duck with Walk {}\nvoid main() => print(Duck().go());", "walk", "A mixin adds its methods to the class that uses it."),
    D("class A {\n  final int x;\n  A(this.x);\n  factory A.twice(int n) => A(n * 2);\n}\nvoid main() => print(A.twice($a).x);", lambda p: 2 * p["a"], "A factory constructor can build the object any way it likes."),
    D("class A {\n  int? x;\n}\nvoid main() => print(A().x);", None, "A nullable field with no value starts as null."),
    D("class Rect {\n  int area;\n  Rect(int w, int h) : area = w * h;\n}\nvoid main() => print(Rect($a, $b).area);", lambda p: p["a"] * p["b"], "The initializer list sets the field before the constructor body."),
    D("class Dog {}\nvoid main() => print(Dog().runtimeType);", "Dog", "runtimeType is the class the object was made from."),
    D("class Animal {}\nclass Dog extends Animal {}\nvoid main() {\n  Animal a = Dog();\n  print(a.runtimeType);\n}", "Dog", "runtimeType is the real class, not the variable's type."),
    D("abstract class Speaker {\n  String say();\n}\nclass Bot implements Speaker {\n  String say() => '$w';\n}\nvoid main() => print(Bot().say());", lambda p: p["w"], "Bot promises Speaker's methods and supplies its own say()."),
    D("extension Twice on int {\n  int twice() => this * 2;\n}\nvoid main() => print($a.twice());", lambda p: 2 * p["a"], "An extension adds a method to an existing type."),
    D("enum Color { red, green, blue }\nvoid main() => print(Color.values[$k - 1].name);", lambda p: ["red", "green", "blue"][p["k"] - 1], "values lists the constants in order, and name is the constant's name."),
    D("enum Color { red, green, blue }\nvoid main() => print(Color.green.index);", 1, "index counts from 0: red 0, green 1, blue 2."),
    D("enum Color { red, green, blue }\nvoid main() => print(Color.values.length);", 3, "Three constants."),
    D("enum Color { red, green, blue }\nvoid main() => print(Color.blue);", "Color.blue", "An enum constant prints as EnumName.constant."),
    D("enum Size {\n  small(1), big(2);\n  final int v;\n  const Size(this.v);\n}\nvoid main() => print(Size.big.v + $a);", lambda p: 2 + p["a"], "Each constant carries its own value."),
    D("class Person {\n  int age;\n  Person(this.age);\n  bool get isAdult => age >= 18;\n}\nvoid main() => print(Person($n).isAdult);", lambda p: p["n"] >= 18, "isAdult is calculated from age each time."),
    D("class V {\n  int x;\n  V(this.x);\n  V operator +(V o) => V(x + o.x);\n}\nvoid main() => print((V($a) + V($b)).x);", lambda p: p["a"] + p["b"], "operator + lets two V objects be added."),
    D("class Adder {\n  int call(int x) => x + $a;\n}\nvoid main() => print(Adder()($b));", lambda p: p["a"] + p["b"], "An object with a call method can be called like a function."),
    D("class C {\n  static int s = 0;\n  int i = 0;\n  void bump() { s++; i++; }\n}\nvoid main() {\n  var a = C(), b = C();\n  a.bump(); b.bump();\n  print('$${C.s} $${a.i}');\n}", "2 1", "s is shared by the class, i belongs to each object."),
    D("class A {\n  String hi() => 'A';\n}\nclass B extends A {\n  String hi() => 'B';\n}\nvoid main() => print([A(), B(), A()].map((x) => x.hi()).join());", "ABA", "Each object answers with its own class's hi()."),
    D("class Box<T> {\n  T v;\n  Box(this.v);\n}\nvoid main() => print(Box<int>($a).v);", lambda p: p["a"], "Box<int> is a Box that holds an int."),
    D("class Box<T> {\n  T v;\n  Box(this.v);\n}\nvoid main() => print(Box('$w').v);", lambda p: p["w"], "T is a String here."),
    D("class Box<T> {\n  T v;\n  Box(this.v);\n}\nvoid main() => print(Box($a).v is int);", True, "Dart worked out T is int from the argument."),
    D("class Box<T> {\n  T v;\n  Box(this.v);\n}\nvoid main() => print(Box('$w').v is int);", False, "The value is a String."),
    D("class P {\n  int x;\n  P(int x) : x = x + 1;\n}\nvoid main() => print(P($a).x);", lambda p: p["a"] + 1, "The field x gets the parameter plus one."),
    D("class A {\n  int x;\n  A(this.x);\n  A.zero() : this($a);\n}\nvoid main() => print(A.zero().x);", lambda p: p["a"], "this(...) hands the work to the main constructor."),
    D("class P {\n  int x = 0, y = 0;\n}\nvoid main() {\n  var p = P()..x = $a..y = $b;\n  print(p.x + p.y);\n}", lambda p: p["a"] + p["b"], "A cascade sets several fields on the same object."),
    D("class A {\n  int x = $a;\n  int y = 0;\n  A() {\n    y = x + 1;\n  }\n}\nvoid main() => print(A().y);", lambda p: p["a"] + 1, "The field initializer runs before the constructor body."),
    D("class A {\n  int _x = $a;\n  int get x => _x;\n}\nvoid main() => print(A().x);", lambda p: p["a"], "The getter hands out the private field."),
    D("class A {\n  int f(int n) => n + 1;\n}\nclass B extends A {\n  int f(int n) => super.f(n) * 2;\n}\nvoid main() => print(B().f($a));", lambda p: (p["a"] + 1) * 2, "super.f(n) runs first, then the result is doubled."),
    D("class Pt {\n  int x, y;\n  Pt(this.x, this.y);\n  String toString() => '($$x, $$y)';\n}\nvoid main() => print(Pt($a, $b));", lambda p: f"({p['a']}, {p['b']})", "toString builds the text print shows."),
    D("class A {\n  int get v => $a;\n}\nclass B extends A {\n  int get v => super.v + 1;\n}\nvoid main() => print(B().v);", lambda p: p["a"] + 1, "A getter can be overridden too."),
    D("class S {\n  static final S _i = S._();\n  S._();\n  factory S() => _i;\n}\nvoid main() => print(identical(S(), S()));", True, "The factory always hands out the same stored object."),
    D("class P {\n  String n;\n  P(this.n);\n  P.guest() : n = 'guest';\n}\nvoid main() => print(P.guest().n);", "guest", "The named constructor sets the name to guest."),
]
