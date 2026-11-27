"""Dart for classes and types: the shapes object-oriented Dart is built from.

The same ground as the Python class set, written the way Dart writes it:
fields and initializing formals (`this.x`), named, const, factory and
redirecting constructors, initializer lists, getters and setters, `toString`,
`operator ==` with `Object.hash`, `extends` and `super`, abstract classes,
`implements`, mixins, extension methods, generics with bounds, enhanced
enums, sealed classes with exhaustive `switch` expressions, records and
patterns, `late`, `static`, private `_names`, `copyWith`, cascades and
`Comparable`.

The blocks are whole programs with a `main`, and the tests run every one
in Dart and hold what it prints to an answer worked out by hand.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

DARTCLASS_LINES: tuple[Passage, ...] = (
    # fields and constructors
    _s("class Account {", "a class: fields and methods in one place"),
    _s("double balance = 0;", "a field with a starting value"),
    _s("final String owner;", "set once, in the constructor"),
    _s("Account(this.owner, this.balance);", "initializing formals assign the fields directly"),
    _s("Account.empty(String owner) : this(owner, 0);", "a redirecting constructor"),
    _s("Account.named({required this.owner, this.balance = 0});", "required and optional named parameters"),
    _s("const Point(this.x, this.y);", "a const constructor: every field is final"),
    _s("const origin = Point(0, 0);", "a compile-time constant object"),
    _s("factory Cache.shared() => _instance;", "a factory may hand back an existing object"),
    _s("factory Shape.fromJson(Map<String, Object?> json) {", "a factory that can pick the subclass"),
    _s("Point.fromList(List<int> xs) : x = xs[0], y = xs[1];", "an initializer list sets finals before the body"),
    _s("Range(this.lo, this.hi) : assert(lo <= hi);", "an assert in the initializer list"),
    _s("Dog(super.name, {this.tricks = const []});", "a super parameter passes straight up"),
    _s("Dog(String name) : super(name);", "the older way to call the parent constructor"),
    # getters, setters, late, static, private
    _s("double get area => width * height;", "a getter, worked out each time it is read"),
    _s("set width(double w) => _width = w;", "a setter: assigning runs code"),
    _s("bool get isEmpty => _items.isEmpty;", "a getter reads like a field"),
    _s("set name(String value) {", "assigning to name runs this body"),
    _s("late final String label = _build();", "late: built on the first read, once"),
    _s("late int total;", "no value yet; reading it too early throws"),
    _s("static int count = 0;", "one copy shared by the whole class"),
    _s("static const maxSize = 100;", "a constant owned by the class"),
    _s("static Point zero() => const Point(0, 0);", "a static method needs no object"),
    _s("String _secret = 'hidden';", "the underscore makes it private to the file"),
    _s("void _log(String msg) => print(msg);", "a private method"),
    # the object protocol
    _s("@override", "marks a member that replaces an inherited one"),
    _s("String toString() => 'Point($x, $y)';", "what print and interpolation show"),
    _s("bool operator ==(Object other) =>", "what == means for this class"),
    _s("other is Point && x == other.x && y == other.y;", "same type, same fields"),
    _s("if (identical(this, other)) return true;", "the very same object is equal"),
    _s("int get hashCode => Object.hash(x, y);", "hash the same fields == compares"),
    _s("Point operator +(Point o) => Point(x + o.x, y + o.y);", "an operator is just a method"),
    _s("int compareTo(Point other) => x.compareTo(other.x);", "what sort() uses to order them"),
    _s("class Version implements Comparable<Version> {", "promise a compareTo"),
    _s("Point copyWith({int? x, int? y}) => Point(x ?? this.x, y ?? this.y);", "a copy with some fields changed"),
    _s("final moved = start.copyWith(y: 10);", "change one field, keep the rest"),
    # inheritance and interfaces
    _s("class Dog extends Animal {", "a Dog is an Animal, and more"),
    _s("return '${super.speak()} and woof';", "super runs the parent's version"),
    _s("abstract class Shape {", "cannot be built, only extended or implemented"),
    _s("double area();", "no body: subclasses must supply it"),
    _s("class Square implements Shape {", "implements: promise every member, inherit none"),
    _s("abstract interface class Repo {", "a pure interface, new in Dart 3"),
    _s("mixin Swimmer {", "behaviour to mix into other classes"),
    _s("class Duck extends Bird with Swimmer, Flyer {", "with adds the mixins' members"),
    _s("mixin Logs on Service {", "on: only for classes that extend Service"),
    _s("extension Shout on String {", "new members on a type you do not own"),
    _s("String get shout => '${toUpperCase()}!';", "an extension getter, using this implicitly"),
    _s("extension type Meters(double value) {}", "a zero-cost wrapper type"),
    # generics
    _s("class Box<T> {", "T is a type chosen when you make one"),
    _s("class Total<T extends num> {", "bounded: only int, double or num"),
    _s("T first<T>(List<T> xs) => xs.first;", "a generic function"),
    _s("T pick<T extends Comparable<T>>(T a, T b) => a.compareTo(b) >= 0 ? a : b;", "the larger of any two comparables"),
    _s("final Map<String, List<T>> _groups = {};", "generics nest like any other type"),
    _s("final box = Box<int>(42);", "the type argument written out"),
    # enums, sealed, records and patterns
    _s("enum Suit { hearts, spades }", "a fixed set of values"),
    _s("enum Planet { moon(1.6), mars(3.7); const Planet(this.g); final double g; }", "an enhanced enum: fields and a const constructor"),
    _s("final heavy = Planet.values.where((p) => p.g > 3);", "values lists every case"),
    _s("sealed class Result {}", "every subclass lives in this file"),
    _s("final class Ok extends Result { final int value; Ok(this.value); }", "one way a Result can be"),
    _s("final text = switch (result) { Ok() => 'fine', Err() => 'oops' };", "no default needed: sealed is exhaustive"),
    _s("Ok(:final value) => 'got $value',", "an object pattern pulls a field out"),
    _s("final (name, age) = ('Ana', 31);", "a record pattern unpacks two values"),
    _s("(int, String) pair() => (1, 'one');", "a function returning a record"),
    _s("final point = (x: 3, y: 4);", "a record with named fields"),
    _s("if (shape case Circle(:final r) when r > 0) print(r);", "if-case: match, bind and guard in one test"),
    _s("case Point(:final x, :final y) when x == y:", "a case with a guard"),
    # cascades and everyday use
    _s("final buf = StringBuffer()..write('a')..write('b');", "a cascade: several calls on one object"),
    _s("final car = Car()..speed = 10..color = 'red';", "a cascade can assign fields too"),
    _s("const User({required this.name, this.age = 18});", "required beside a default"),
    _s("final animals = <Animal>[Dog('Rex'), Cat('Tom')];", "one list, two subclasses"),
    _s("for (final a in animals) { print(a.speak()); }", "each class answers its own way"),
    _s("if (pet is Dog) pet.fetch();", "is promotes the type inside the if"),
    _s("final dog = pet as Dog;", "as: a cast that throws if wrong"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"Dart · {note}")


DARTCLASS_BLOCKS: tuple[Passage, ...] = (
    _b("""class Counter {
  int count = 0;
  final String label;

  Counter(this.label);

  void tick() => count++;
}

void main() {
  final c = Counter('hits')..tick()..tick();
  print('${c.label} ${c.count}');
}""",
       "a class with fields and cascades"),
    _b("""class Point {
  final int x, y;
  const Point(this.x, this.y);
  const Point.origin() : this(0, 0);
  Point.onX(int x) : x = x, y = 0;
}

void main() {
  final p = Point.onX(4);
  print('${p.x},${p.y} ${Point.origin().y}');
}""",
       "named and redirecting constructors"),
    _b("""class Temp {
  double _c = 0;
  double get fahrenheit => _c * 9 / 5 + 32;
  set fahrenheit(double f) => _c = (f - 32) * 5 / 9;
  double get celsius => _c;
}

void main() {
  final t = Temp()..fahrenheit = 212;
  print('${t.celsius} ${t.fahrenheit}');
}""",
       "a getter and a setter over a private field"),
    _b("""class Pair {
  final int a, b;
  const Pair(this.a, this.b);
  @override
  bool operator ==(Object other) => other is Pair && a == other.a && b == other.b;
  @override
  int get hashCode => Object.hash(a, b);
  @override
  String toString() => 'Pair($a, $b)';
}

void main() {
  final seen = {const Pair(1, 2), Pair(1, 2), Pair(2, 1)};
  print('${seen.length} $seen');
}""",
       "equality, hashCode and toString together"),
    _b("""class Animal {
  final String name;
  Animal(this.name);
  String speak() => '$name makes a sound';
}

class Dog extends Animal {
  Dog(super.name);
  @override
  String speak() => '${super.speak()}: woof';
}

void main() => print(Dog('Rex').speak());""",
       "a subclass calling super"),
    _b("""abstract class Shape {
  double area();
}

class Square implements Shape {
  Square(this.side);
  final double side;
  @override
  double area() => side * side;
}

void main() {
  final Shape s = Square(3);
  print('${s.area()} ${s is Square}');
}""",
       "an abstract class and implements"),
    _b("""mixin Walker {
  int steps = 0;
  void walk() => steps += 2;
}

class Robot with Walker {}

void main() {
  final r = Robot()..walk()..walk()..walk();
  print('${r.steps} ${r is Walker}');
}""",
       "a mixin added with with"),
    _b("""extension WordTools on String {
  String get shout => '${toUpperCase()}!';
  int get vowels => split('').where('aeiou'.contains).length;
}

void main() {
  print('hello'.shout);
  print('education'.vowels);
}""",
       "extension methods on String"),
    _b("""class Box<T extends num> {
  final List<T> items;
  Box(this.items);
  T get biggest => items.reduce((a, b) => a > b ? a : b);
  num get total => items.fold<num>(0, (s, x) => s + x);
}

void main() {
  final b = Box([3, 9, 4]);
  print('${b.biggest} ${b.total}');
}""",
       "a generic Box bounded to numbers"),
    _b("""enum Planet {
  moon(0.5), earth(1.0), jupiter(2.5);

  const Planet(this.gravity);
  final double gravity;

  double weigh(double kg) => kg * gravity;
}

void main() {
  print('${Planet.jupiter.name} ${Planet.jupiter.weigh(10)} ${Planet.values.length}');
}""",
       "an enhanced enum with a field and a method"),
    _b("""sealed class Shape {}

class Circle extends Shape {
  final double r;
  Circle(this.r);
}

class Rect extends Shape {
  final double w, h;
  Rect(this.w, this.h);
}

double area(Shape s) => switch (s) {
  Circle(:final r) => 3 * r * r,
  Rect(:final w, :final h) => w * h,
};

void main() => print('${area(Circle(2))} ${area(Rect(2, 3.5))}');""",
       "a sealed class and an exhaustive switch"),
    _b("""(int, int) minMax(List<int> xs) {
  final sorted = [...xs]..sort();
  return (sorted.first, sorted.last);
}

void main() {
  final (lo, hi) = minMax([5, 2, 9, 4]);
  final point = (x: 3, y: 4);
  print('$lo $hi ${point.x + point.y} $point');
}""",
       "records returned and unpacked"),
    _b("""class Config {
  static int created = 0;
  static const defaultName = 'app';
  late final String name = _load();
  Config() { created++; }
  String _load() => '$defaultName-$created';
}

void main() {
  final a = Config(), b = Config();
  print('${b.name} ${a.name} ${Config.created}');
}""",
       "static members and a late final field"),
    _b("""class Logger {
  static final Map<String, Logger> _cache = {};
  final String name;
  Logger._(this.name);

  factory Logger(String name) => _cache.putIfAbsent(name, () => Logger._(name));
}

void main() {
  print(identical(Logger('a'), Logger('a')));
  print(identical(Logger('a'), Logger('b')));
}""",
       "a factory constructor that caches"),
    _b("""class User {
  final String name;
  final int age;
  const User({required this.name, this.age = 18});

  User copyWith({String? name, int? age}) => User(name: name ?? this.name, age: age ?? this.age);

  @override
  String toString() => '$name/$age';
}

void main() {
  const u = User(name: 'Ana');
  print('$u ${u.copyWith(age: 30)} ${u.copyWith(name: 'Bo')}');
}""",
       "required named parameters and copyWith"),
    _b("""class Range {
  final int lo, hi;
  final int size;
  Range(this.lo, this.hi)
      : assert(lo <= hi),
        size = hi - lo + 1;
}

void main() {
  print(Range(3, 7).size);
  print(Range(5, 5).size);
}""",
       "an initializer list with an assert"),
    _b("""class Version implements Comparable<Version> {
  final int major, minor;
  const Version(this.major, this.minor);

  @override
  int compareTo(Version other) =>
      major != other.major ? major - other.major : minor - other.minor;

  @override
  String toString() => '$major.$minor';
}

void main() {
  final vs = [Version(1, 10), Version(1, 2), Version(0, 9)]..sort();
  print(vs);
}""",
       "Comparable and a natural sort"),
    _b("""class Point {
  final int x, y;
  const Point(this.x, this.y);
}

String describe(Object o) => switch (o) {
  Point(x: 0, y: 0) => 'origin',
  Point(:final x) when x < 0 => 'left $x',
  Point(:final x, :final y) => 'at $x,$y',
  _ => 'unknown',
};

void main() => print([Point(0, 0), Point(-2, 5), Point(1, 2), 7].map(describe).join('; '));""",
       "object patterns with a guard"),
)

#: What each block prints, by its note - worked out by hand before Dart was
#: asked, and held to the real run by tests/test_typing_dartclass.py.
DARTCLASS_PRINTS: dict[str, str] = {
    "a class with fields and cascades": "hits 2",
    "named and redirecting constructors": "4,0 0",
    "a getter and a setter over a private field": "100.0 212.0",
    "equality, hashCode and toString together": "2 {Pair(1, 2), Pair(2, 1)}",
    "a subclass calling super": "Rex makes a sound: woof",
    "an abstract class and implements": "9.0 true",
    "a mixin added with with": "6 true",
    "extension methods on String": "HELLO!\n5",
    "a generic Box bounded to numbers": "9 16",
    "an enhanced enum with a field and a method": "jupiter 25.0 3",
    "a sealed class and an exhaustive switch": "12.0 7.0",
    "records returned and unpacked": "2 9 7 (x: 3, y: 4)",
    "static members and a late final field": "app-2 app-2 2",
    "a factory constructor that caches": "true\nfalse",
    "required named parameters and copyWith": "Ana/18 Ana/30 Bo/18",
    "an initializer list with an assert": "5\n1",
    "Comparable and a natural sort": "[0.9, 1.2, 1.10]",
    "object patterns with a guard": "origin; left -2; at 1,2; unknown",
}
