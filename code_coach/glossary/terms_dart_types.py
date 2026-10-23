"""Dart words, part 2: classes and objects, generics, mixins and extensions, patterns and switch.

Examples with `main(` are whole programs; the others are the body of main (see terms_dart_core.py)."""

from __future__ import annotations

from .entry import Entry, dart

TERMS: list[Entry] = [
    # ── Classes and objects ─────────────────────────────────────────────
    *dart(
        "class",
        "Class",
        "A blueprint for objects: it lists the data each object holds (fields) and the actions it can do (methods).",
        see=("instance", "constructor", "method", "inheritance"),
        priority=50,
        aka=("classes", "oop", "class declaration", "field", "fields", "member"),
        detect=(r"^\s*(?:abstract\s+|sealed\s+|final\s+|base\s+|interface\s+|mixin\s+)*class\s+\w+",),
        rules=(
            "Make an object by calling the class like a function: Dog('Rex'). You do not need new.",
            "Members whose names start with _ are private to the file; all others are public.",
            "Everything in Dart is an object, even numbers and null.",
            "A class can extend one other class, implement many interfaces and use many mixins.",
        ),
        example="""
            class Dog {
              final String name;
              Dog(this.name);
              String bark() => '$name says woof';
            }
            void main() {
              print(Dog('Rex').bark());
            }
        """,
        out="Rex says woof",
    ),
    *dart(
        "instance",
        "Instance (object)",
        "One actual object made from a class. Each instance has its own copy of the fields.",
        see=("class", "constructor", "identity"),
        priority=35,
        aka=("instances", "object", "objects", "instantiate", "instance variable", "new"),
        rules=(
            "Dog('Rex') and Dog('Fido') are two instances with different name fields.",
            "Two instances are different objects even if their fields match, unless the class defines ==.",
            "obj.runtimeType names the class: Dog('Rex').runtimeType is Dog.",
        ),
        example="""
            class Counter {
              int n = 0;
            }
            void main() {
              var a = Counter();
              var b = Counter();
              a.n++;
              a.n++;
              print('${a.n} ${b.n}');
            }
        """,
        out="2 0",
    ),
    *dart(
        "method",
        "Method",
        "A function that belongs to a class. It runs on one object and can use that object's fields.",
        see=("function", "class", "static-method", "override"),
        priority=35,
        aka=("methods", "instance method", "member function"),
        rules=(
            "Call it with a dot: dog.bark().",
            "Inside a method the fields are used by name (name), or as this.name when a parameter has the same name.",
            "Getters and setters look like fields but are methods underneath.",
        ),
        example="""
            class Rect {
              final double w, h;
              Rect(this.w, this.h);
              double area() => w * h;
            }
            void main() {
              print(Rect(2, 3.5).area());
            }
        """,
        out="7.0",
    ),
    *dart(
        "static-method",
        "Static member (static)",
        "A field or method marked static belongs to the class itself, not to any one object. You use it through the class name.",
        see=("class", "method", "factory-constructor"),
        priority=60,
        aka=("static", "static field", "static variable", "class method", "class member", "static members"),
        detect=(r"\bstatic\b",),
        rules=(
            "Call it as ClassName.thing: Math.double(3), not on an instance.",
            "A static method has no this: it cannot see the object's fields.",
            "A static field is shared by every instance: one copy for the whole class.",
        ),
        example="""
            class Ids {
              static int next = 1;
              static int take() => next++;
            }
            void main() {
              print(Ids.take());
              print(Ids.take());
              print(Ids.next);
            }
        """,
        out="1\n2\n3",
    ),
    *dart(
        "this",
        "this",
        "Inside a class, the object the code is running on. Usually it can be left out; it is needed to tell a field from a parameter of the same name.",
        see=("class", "method", "initializing-formal"),
        priority=45,
        aka=("self", "this keyword", "receiver", "this."),
        detect=(r"\bthis\b",),
        rules=(
            "In Point(this.x, this.y) the this.x means 'store the argument straight into the field x'.",
            "In an extension method, this is the value the method was called on.",
            "A static method has no this.",
        ),
        example="""
            class Box {
              int size = 1;
              void grow(int size) {
                this.size += size;
              }
            }
            void main() {
              var b = Box();
              b.grow(4);
              print(b.size);
            }
        """,
        out="5",
    ),
    *dart(
        "constructor",
        "Constructor",
        "Special code in a class that builds a new object and sets up its fields. It has the same name as the class.",
        see=("initializing-formal", "named-constructor", "factory-constructor", "const-constructor"),
        priority=55,
        aka=("constructors", "ctor", "init", "__init__", "constructor body"),
        detect=(r"^\s*(?:const\s+|factory\s+)?[A-Z]\w*(?:\.\w+)?\s*\([^)\n]*\)\s*(?::[^{;\n]*)?[{;]",),
        rules=(
            "Dog(this.name); is the short form: the argument goes straight into the field.",
            "A class with no constructor written gets a no-argument one for free.",
            "A constructor cannot return a value; it always builds a new object (a factory constructor is the exception).",
        ),
        example="""
            class Dog {
              String name;
              int age;
              Dog(this.name, this.age);
            }
            void main() {
              var d = Dog('Rex', 3);
              print('${d.name} ${d.age}');
            }
        """,
        out="Rex 3",
    ),
    *dart(
        "initializing-formal",
        "Initializing formal (this.x)",
        "A constructor parameter written this.x. Dart copies the argument straight into the field x, with no extra code.",
        see=("constructor", "this", "named-parameter"),
        priority=70,
        aka=("this.x", "initializing formals", "initialising formal", "field parameter", "this parameter"),
        detect=(r"\(\s*(?:[^()\n]*,\s*)?(?:\{\s*)?(?:required\s+)?this\.\w+",),
        rules=(
            "Point(this.x, this.y); replaces Point(int x, int y) : x = x, y = y;",
            "It can be positional, named ({required this.x}) or have a default (this.x = 0).",
            "It also works with final fields, which can only be set this way or in the initializer list.",
        ),
        example="""
            class Point {
              final int x, y;
              Point(this.x, [this.y = 0]);
            }
            void main() {
              var p = Point(5);
              print('${p.x},${p.y}');
            }
        """,
        out="5,0",
    ),
    *dart(
        "named-constructor",
        "Named constructor",
        "An extra constructor with its own name, written ClassName.name(). It lets one class be built in different ways.",
        see=("constructor", "factory-constructor", "initializer-list"),
        priority=65,
        aka=("named constructors", "alternate constructor", "secondary constructor"),
        detect=(r"^\s*(?:const\s+|factory\s+)?[A-Z]\w*\.[a-z_]\w*\s*\([^)\n]*\)\s*(?:[:{;]|=>)",),
        rules=(
            "Point.origin() : x = 0, y = 0; is called as Point.origin().",
            "Constructors are not inherited: a subclass needs its own.",
            "Common names: fromJson, empty, withName.",
        ),
        example="""
            class Point {
              final int x, y;
              Point(this.x, this.y);
              Point.origin() : x = 0, y = 0;
            }
            void main() {
              var o = Point.origin();
              print('${o.x} ${o.y}');
            }
        """,
        out="0 0",
    ),
    *dart(
        "initializer-list",
        "Initializer list",
        "Code after a colon in a constructor header that sets fields (or checks something) before the constructor body runs.",
        see=("constructor", "initializing-formal", "named-constructor"),
        priority=60,
        aka=("initialiser list", "initializers", "constructor initializer", "assert in constructor"),
        detect=(r"\)\s*:\s*[A-Za-z_]\w*\s*=[^=]",),
        rules=(
            "Rect(double w, double h) : area = w * h; sets the field area from the arguments.",
            "Items are separated by commas and can include assert(...) and super(...).",
            "It runs before the body, so it cannot use this, but it can set final fields.",
        ),
        example="""
            class Rect {
              final double w, h, area;
              Rect(this.w, this.h) : area = w * h;
            }
            void main() {
              print(Rect(2, 4).area);
            }
        """,
        out="8.0",
    ),
    *dart(
        "factory-constructor",
        "Factory constructor",
        "A constructor marked factory. Unlike a normal one it may return an object that already exists, or one of a subtype, instead of always building a new one.",
        see=("constructor", "named-constructor", "static-method"),
        priority=75,
        aka=("factory", "factory constructors", "singleton", "cache"),
        detect=(r"\bfactory\b",),
        rules=(
            "A factory has no this and cannot use an initializer list: it just returns a value.",
            "Typical uses: return a cached instance (a singleton), pick a subclass, or build from JSON (factory Dog.fromJson(...)).",
            "It is called like any constructor: Logger('app').",
        ),
        example="""
            class Logger {
              static final Map<String, Logger> _cache = {};
              final String name;
              Logger._(this.name);
              factory Logger(String name) => _cache.putIfAbsent(name, () => Logger._(name));
            }
            void main() {
              print(identical(Logger('a'), Logger('a')));
              print(identical(Logger('a'), Logger('b')));
            }
        """,
        out="true\nfalse",
    ),
    *dart(
        "const-constructor",
        "Const constructor",
        "A constructor marked const, which lets you make constant objects. Every field must be final.",
        see=("const", "constructor", "final"),
        priority=70,
        aka=("const constructors", "const object", "constant constructor", "const keyword"),
        detect=(r"\bconst\s+[A-Z]\w*(?:\.\w+)?\s*\(",),
        rules=(
            "const Point(1, 2) is made once at compile time; every const Point(1, 2) is the same object.",
            "Without the word const at the call, new Point(1, 2) is an ordinary object, even if the constructor is const.",
            "In Flutter, const widgets are skipped when the screen is rebuilt, which saves work.",
        ),
        example="""
            class Point {
              final int x, y;
              const Point(this.x, this.y);
            }
            void main() {
              print(identical(const Point(1, 2), const Point(1, 2)));
              print(identical(Point(1, 2), Point(1, 2)));
            }
        """,
        out="true\nfalse",
    ),
    *dart(
        "getter-setter",
        "Getter and setter",
        "A method that looks like a field. A getter (get) is read like one; a setter (set) runs code when something is assigned to it.",
        see=("method", "class", "final"),
        priority=60,
        aka=("getter", "setter", "get", "set accessor", "property", "properties", "attribute", "computed property"),
        detect=(r"\b(?:get|set)\s+[a-z_]\w*\s*(?:=>|\{|\()",),
        rules=(
            "double get area => w * h; is used as shape.area, with no brackets.",
            "set side(double v) { ... } runs when you write shape.side = 5.",
            "A getter with no setter makes a read-only value.",
            "Every public field already has an invisible getter and setter.",
        ),
        example="""
            class Circle {
              double r;
              Circle(this.r);
              double get diameter => r * 2;
              set diameter(double d) => r = d / 2;
            }
            void main() {
              var c = Circle(3);
              print(c.diameter);
              c.diameter = 10;
              print(c.r);
            }
        """,
        out="6.0\n5.0",
    ),
    *dart(
        "inheritance",
        "Inheritance (extends)",
        "A class can extend another and get all of its fields and methods without rewriting them. class Dog extends Animal.",
        see=("subclass", "override", "super", "abstract-class"),
        priority=60,
        aka=("extends", "inherit", "inherits", "superclass", "parent class", "base class", "child class", "is-a"),
        detect=(r"\bextends\b",),
        rules=(
            "A class extends exactly one class (single inheritance); use mixins and interfaces for more.",
            "A subclass object is also an object of the parent type: Dog() is Animal is true.",
            "A subclass can replace an inherited method with @override.",
            "Constructors are not inherited; the subclass calls super(...) to set up the parent part.",
        ),
        example="""
            class Animal {
              String speak() => '...';
            }
            class Dog extends Animal {}
            void main() {
              var d = Dog();
              print(d.speak());
              print(d is Animal);
            }
        """,
        out="...\ntrue",
    ),
    *dart(
        "subclass",
        "Subclass",
        "A class that extends another. The one it extends is its superclass (parent).",
        see=("inheritance", "override", "super"),
        priority=35,
        aka=("subclasses", "child", "derived class", "subtype", "supertype"),
        rules=(
            "A subclass has everything its parent has, plus its own additions.",
            "Anywhere a parent type is expected, a subclass object is accepted.",
            "The parent knows nothing about its subclasses.",
        ),
        example="""
            class Shape {}
            class Circle extends Shape {}
            void main() {
              Shape s = Circle();
              print(s is Circle);
              print(s.runtimeType);
            }
        """,
        out="true\nCircle",
    ),
    *dart(
        "override",
        "Override",
        "Writing a method in a subclass with the same name as the parent's, so the subclass uses its own version. Mark it @override.",
        see=("inheritance", "super", "abstract-class"),
        priority=70,
        aka=("overriding", "overrides", "@override", "overridden", "polymorphism"),
        detect=(r"@override\b",),
        rules=(
            "The object's real class decides which version runs, even if the variable's type is the parent.",
            "@override makes the analyzer warn if no parent really has that member (a typo in the name).",
            "Call super.method() inside to run the parent's version too.",
        ),
        example="""
            class Animal {
              String speak() => '...';
            }
            class Dog extends Animal {
              @override
              String speak() => 'woof';
            }
            void main() {
              Animal a = Dog();
              print(a.speak());
            }
        """,
        out="woof",
    ),
    *dart(
        "super",
        "super",
        "Refers to the parent class: super.method() runs the parent's version, and super(...) in a constructor sets up the parent part.",
        see=("inheritance", "override", "constructor"),
        priority=65,
        aka=("super call", "super.", "super constructor", "super parameter", "super parameters", "super.x"),
        detect=(r"\bsuper\b",),
        rules=(
            "In a method: super.describe() calls the parent's describe.",
            "In a constructor header: Dog(String name) : super(name); passes it up.",
            "Dart 3 super parameters shorten this: Dog(super.name);",
        ),
        example="""
            class Animal {
              final String name;
              Animal(this.name);
              String describe() => 'animal $name';
            }
            class Dog extends Animal {
              Dog(super.name);
              @override
              String describe() => '${super.describe()}, a dog';
            }
            void main() {
              print(Dog('Rex').describe());
            }
        """,
        out="animal Rex, a dog",
    ),
    *dart(
        "abstract-class",
        "Abstract class",
        "A class marked abstract that cannot be built directly. It can list methods with no body that every subclass must supply.",
        see=("inheritance", "interface", "override"),
        priority=70,
        aka=("abstract", "abstract method", "abstract classes", "pure virtual"),
        detect=(r"\babstract\b",),
        rules=(
            "Shape() is an error when Shape is abstract; build a subclass instead.",
            "A method with no body (double area();) must be written in each concrete subclass.",
            "It can also hold ordinary methods and fields that subclasses inherit.",
        ),
        example="""
            abstract class Shape {
              double area();
              String show() => 'area ${area()}';
            }
            class Square extends Shape {
              final double s;
              Square(this.s);
              @override
              double area() => s * s;
            }
            void main() {
              print(Square(3).show());
            }
        """,
        out="area 9.0",
    ),
    *dart(
        "interface",
        "Interface (implements)",
        "Every Dart class doubles as an interface. A class that implements it promises to provide all its members, but inherits no code from it.",
        see=("abstract-class", "mixin", "inheritance"),
        priority=70,
        aka=("implements", "implement", "interface class", "contract", "protocol"),
        detect=(r"\bimplements\b",),
        rules=(
            "class Duck implements Walker, Swimmer lists several; a class can implement as many as it likes.",
            "Unlike extends, implements copies nothing: you must write every member yourself.",
            "interface class (Dart 3) is a class that can be implemented but not extended outside its library.",
        ),
        example="""
            abstract class Walker {
              String walk();
            }
            class Dog implements Walker {
              @override
              String walk() => 'trot';
            }
            void main() {
              Walker w = Dog();
              print(w.walk());
            }
        """,
        out="trot",
    ),
    *dart(
        "mixin",
        "Mixin (with)",
        "A bundle of methods and fields you can add to a class with the word with, without making it a parent.",
        see=("inheritance", "interface", "extension-method"),
        priority=75,
        aka=("mixins", "with", "mixin class", "trait", "on clause"),
        detect=(r"\bmixin\b", r"\bwith\s+[A-Z]\w*"),
        rules=(
            "class Dog extends Animal with Walker, Swimmer adds both sets of members.",
            "If two mixins define the same method, the one listed last wins.",
            "A mixin has no constructor. mixin Walker on Animal limits it to subclasses of Animal.",
        ),
        example="""
            mixin Walker {
              String move() => 'walk';
            }
            mixin Swimmer {
              String move() => 'swim';
            }
            class Duck with Walker, Swimmer {}
            void main() {
              print(Duck().move());
            }
        """,
        out="swim",
    ),
    *dart(
        "extension-method",
        "Extension method",
        "A way to add methods to a type you did not write, such as String or int, so you can call them with a dot.",
        see=("mixin", "this", "method"),
        priority=75,
        aka=("extension", "extensions", "extension type", "extension on", "extend a type"),
        detect=(r"^\s*extension\b",),
        rules=(
            "extension Shout on String { String shout() => toUpperCase() + '!'; } then 'hi'.shout() is 'HI!'.",
            "It adds no fields and changes nothing in the class: it is a different way to write a call.",
            "Inside, this is the value it was called on.",
            "It is chosen from the variable's declared type, so it does not work on a dynamic variable.",
        ),
        example="""
            extension Shout on String {
              String shout() => '${toUpperCase()}!';
            }
            extension on int {
              bool get isBig => this > 100;
            }
            void main() {
              print('hi'.shout());
              print(500.isBig);
            }
        """,
        out="HI!\ntrue",
    ),
    *dart(
        "generics",
        "Generics",
        "Types that take another type as a parameter, written in < >: List<int> is a list of ints, Map<String, int> maps text to ints. You can write your own: class Box<T>.",
        see=("type", "list", "dictionary"),
        priority=55,
        aka=("generic", "generic type", "type parameter", "type argument", "templates", "list<int>", "<t>", "t extends"),
        detect=(r"\b\w+<\s*[A-Z]\w*(?:\s+extends\s+\w+)?\s*>\s*[\w(]", r"<\s*(?:int|String|double|bool|num|dynamic|Object)\??\s*[,>]"),
        rules=(
            "Box<int>(3).value is an int; Box<String>('a').value is a String: the compiler tracks which.",
            "<T extends num> limits T to numbers.",
            "Dart keeps the type at run time: a List<int> is not a List<String>.",
            "Dart works out the type for you when it can: var xs = [1, 2]; is a List<int>.",
        ),
        example="""
            class Box<T> {
              final T value;
              Box(this.value);
            }
            T firstOf<T>(List<T> xs) => xs.first;
            void main() {
              print(Box<int>(3).value + 1);
              print(firstOf(['a', 'b']));
              print([1, 2] is List<String>);
            }
        """,
        out="4\na\nfalse",
    ),
    *dart(
        "string-representation",
        "toString (string representation)",
        "The text an object turns into when printed or placed in a string. Every class has toString(); the default says Instance of 'ClassName'.",
        see=("string-interpolation", "class", "override"),
        priority=55,
        aka=("tostring", "to string", "str", "repr", "__str__", "print an object", "string form", "describe"),
        detect=(r"\btoString\s*\(",),
        rules=(
            "print(obj) and '$obj' both call obj.toString().",
            "Override it to show something useful: @override String toString() => 'Dog($name)';",
            "Lists, maps and sets call toString on each item: print([dog]) shows [Dog(Rex)].",
            "Exceptions are shown the same way: print(e) uses the error's toString.",
        ),
        example="""
            class Dog {
              final String name;
              Dog(this.name);
              @override
              String toString() => 'Dog($name)';
            }
            class Cat {}
            void main() {
              var d = Dog('Rex');
              print(d);
              print('pet: $d');
              print([d]);
              print(Cat());
            }
        """,
        out="Dog(Rex)\npet: Dog(Rex)\n[Dog(Rex)]\nInstance of 'Cat'",
    ),
    *dart(
        "equality",
        "Equality (==)",
        "a == b asks whether two values count as equal. Numbers, strings and records compare by content; most objects only equal themselves unless the class defines ==.",
        see=("hash-code", "identity", "record"),
        priority=50,
        aka=("==", "!=", "equals", "equal", "loose-equality", "strict-equality", "===", "compare for equality", "value equality"),
        detect=(r"\boperator\s*==", r"[^=!<>]==[^=]"),
        rules=(
            "'a' == 'a' is true and 1 == 1.0 is true. [1] == [1] is false: lists are compared by identity, not by content.",
            "A class gets the default ==, which means 'the very same object'. Override == (and hashCode) to compare fields.",
            "Dart has one ==; there is no ===. For 'the very same object' use identical(a, b).",
            "Never compare computed doubles with == (see float-precision).",
        ),
        example="""
            print('a' == 'a');
            print(1 == 1.0);
            print([1] == [1]);
            print((1, 2) == (1, 2));
            print(const [1] == const [1]);
        """,
        out="true\ntrue\nfalse\ntrue\ntrue",
    ),
    *dart(
        "hash-code",
        "hashCode",
        "A whole number that stands for an object, used by Sets and Maps to find it quickly. Objects that are == must have the same hashCode.",
        see=("equality", "set", "dictionary"),
        priority=60,
        aka=("hashcode", "hash", "object.hash", "hashing", "hash code"),
        detect=(r"\bhashCode\b|\bObject\.hash(?:All)?\(",),
        rules=(
            "Override == and hashCode together, or a Set or Map can hold two 'equal' objects.",
            "Object.hash(x, y) combines fields into one hashCode.",
            "Strings, numbers and records already have correct ones.",
        ),
        example="""
            class P {
              final int x, y;
              P(this.x, this.y);
              @override
              bool operator ==(Object other) => other is P && other.x == x && other.y == y;
              @override
              int get hashCode => Object.hash(x, y);
            }
            void main() {
              print({P(1, 2), P(1, 2), P(3, 4)}.length);
            }
        """,
        out="2",
    ),
    *dart(
        "identity",
        "Identity (identical)",
        "Whether two names refer to the very same object in memory, not just equal ones. identical(a, b) asks that.",
        see=("equality", "const", "instance"),
        priority=50,
        aka=("identical", "same object", "reference equality", "reference", "copy", "alias", "aliasing", "shared reference"),
        detect=(r"\bidentical\s*\(",),
        rules=(
            "var b = a; makes b another name for the same list: changing b's items changes a's.",
            "A second list with the same items is a different object: identical is false, and so is ==.",
            "To copy a list: [...a] or List.of(a). The copy is shallow: the items inside are shared.",
        ),
        example="""
            var a = [1];
            var b = a;
            var c = [1];
            b.add(2);
            print(a);
            print(identical(a, b));
            print(identical(a, c));
            print(a == c);
            var d = [...a];
            d.add(9);
            print(a);
        """,
        out="[1, 2]\ntrue\nfalse\nfalse\n[1, 2]",
    ),
    *dart(
        "callable-class",
        "Callable class (call)",
        "A class with a method named call. You can then use its objects like functions: obj(3) means obj.call(3).",
        see=("method", "function", "higher-order-function"),
        priority=60,
        aka=("call method", "callable", "functor", "callable object"),
        detect=(r"^\s*\w[\w<>?, ]*\s+call\s*\(",),
        rules=(
            "An object with call() can be passed where a function is expected.",
            "The call method can take any parameters and return any type.",
        ),
        example="""
            class Adder {
              final int n;
              Adder(this.n);
              int call(int x) => x + n;
            }
            void main() {
              var add2 = Adder(2);
              print(add2(3));
              print([1, 2].map(add2).toList());
            }
        """,
        out="5\n[3, 4]",
    ),
    *dart(
        "private-member",
        "Private member (_name)",
        "A name that starts with an underscore is private. Dart's privacy is per file (library), not per class.",
        see=("class", "import", "getter-setter"),
        priority=50,
        aka=("private", "underscore", "public", "visibility", "access modifier", "encapsulation", "library private"),
        detect=(r"(?<![\w$.])_[a-z]\w*\s*(?:=|;|\(|=>)",),
        rules=(
            "There are no public or private keywords: just the leading _.",
            "Code in the same file can still see _name, even from another class.",
            "Code in other files cannot see it at all (it is a compile error).",
        ),
        example="""
            class A {
              int _secret = 42;
            }
            class B {
              int peek(A a) => a._secret;
            }
            void main() {
              print(B().peek(A()));
            }
        """,
        out="42",
    ),
    # ── Patterns and switch (Dart 3) ────────────────────────────────────
    *dart(
        "pattern",
        "Pattern",
        "A description of the shape of a value, which can both check it and pull parts out. New in Dart 3, used in switch, if-case and variable declarations.",
        see=("destructuring", "switch-expression", "if-case", "record"),
        priority=60,
        aka=("patterns", "pattern matching", "match", "list pattern", "object pattern", "record pattern", "map pattern", "wildcard", "rest", "rest pattern"),
        detect=(r"\bcase\s+(?:final\s+|var\s+)?[\[({A-Z]", r"\b(?:var|final)\s*[\[({]"),
        rules=(
            "Kinds: constants (1, 'a'), lists [a, b], records (x, y), maps {'k': v}, objects Point(x: var px), types (int n), comparisons (> 5), and _ for 'anything'.",
            "[first, ...rest] matches a list of one or more items; rest is the remaining items.",
            "p1 || p2 and p1 && p2 combine patterns; when adds an extra test.",
            "A refutable pattern may fail to match; then the next case (or the else) is tried.",
        ),
        example="""
            var (a, b) = (1, 2);
            var [x, ...rest] = [10, 20, 30];
            print(a + b);
            print(x);
            print(rest);
        """,
        out="3\n10\n[20, 30]",
    ),
    *dart(
        "destructuring",
        "Destructuring",
        "Taking a record, list or object apart in one step and giving names to its parts: var (a, b) = pair;",
        see=("pattern", "record", "spread"),
        priority=60,
        aka=("destructure", "unpacking", "unpack", "tuple unpacking", "array destructuring", "multiple assignment", "swap", "unpack a record"),
        detect=(r"\b(?:var|final)\s*\(\s*\w+\s*,", r"^\s*\(\s*\w+\s*,\s*\w+\s*\)\s*="),
        rules=(
            "var (name, age) = ('Ann', 30); declares both at once.",
            "Assign to existing variables with no var: (a, b) = (b, a); swaps them.",
            "var [first, ...rest] = list; takes the first item and the others. If the shapes do not match, it throws.",
            "Name only the fields you want: var (x: px, y: _) = point;",
        ),
        example="""
            var (a, b) = (1, 2);
            (a, b) = (b, a);
            print('$a $b');
            var [first, ...rest] = [1, 2, 3];
            print('$first $rest');
        """,
        out="2 1\n1 [2, 3]",
    ),
    *dart(
        "switch",
        "switch statement",
        "Picks which block of code to run by comparing a value to a list of cases. Dart cases do not fall through into the next one.",
        see=("switch-expression", "enum", "guard-clause"),
        priority=60,
        aka=("case", "switch case", "break in switch", "fall through", "fallthrough"),
        detect=(r"\bswitch\s*\([^)\n]*\)\s*\{(?![^}]*=>)",),
        rules=(
            "Each case ends by itself; you do not write break (though you can).",
            "Stacked empty cases share the next body: case 1: case 2: print('low');",
            "default (or _) catches everything else.",
            "A switch over an enum or a sealed class must cover every value or it does not compile.",
        ),
        example="""
            var n = 2;
            switch (n) {
              case 1:
              case 2:
                print('low');
              case 3:
                print('three');
              default:
                print('other');
            }
        """,
        out="low",
    ),
    *dart(
        "switch-expression",
        "switch expression",
        "A switch that works out to a value: switch (x) { pattern => result, ... }. The first arm that matches gives the answer.",
        see=("switch", "guard-clause", "sealed-class"),
        priority=70,
        aka=("switch expressions", "match expression", "pattern switch"),
        detect=(r"\bswitch\s*\([^)]*\)\s*\{[^}]*=>",),
        rules=(
            "Arms are separated by commas, not semicolons, and the last comma is optional.",
            "It must be exhaustive: end with _ => ... unless every value of an enum or sealed type is covered.",
            "a || b in one arm matches either; 1 || 2 => 'few'.",
            "It is an expression, so it can be returned or put in a variable.",
        ),
        example="""
            String name(int n) => switch (n) {
              1 => 'one',
              2 || 3 => 'few',
              _ => 'many',
            };
            print(name(1));
            print(name(3));
            print(name(9));
        """,
        out="one\nfew\nmany",
    ),
    *dart(
        "guard-clause",
        "when (guard clause)",
        "An extra condition after a pattern in a case: the case matches only if the pattern fits and the when test is true.",
        see=("switch-expression", "pattern", "if-case"),
        priority=70,
        aka=("when", "guard", "case guard", "when clause", "pattern guard"),
        detect=(r"\bwhen\s+[^\n=]+(?:=>|:)",),
        rules=(
            "int v when v > 100 => 'huge' matches only ints above 100.",
            "The pattern's variables (v) can be used in the when test and in the result.",
            "If the guard is false, matching moves on to the next case.",
        ),
        example="""
            String size(int n) => switch (n) {
              < 0 => 'negative',
              int v when v > 100 => 'huge',
              _ => 'normal',
            };
            print(size(-4));
            print(size(500));
            print(size(7));
        """,
        out="negative\nhuge\nnormal",
    ),
    *dart(
        "if-case",
        "if-case",
        "if (value case pattern) { ... } runs the block only when the value matches the pattern, and the pattern's variables are available inside.",
        see=("pattern", "guard-clause", "type-promotion"),
        priority=70,
        aka=("if case", "case in if", "if (x case"),
        detect=(r"\bif\s*\([^)\n]*\bcase\b",),
        rules=(
            "if (json case {'name': String n}) checks the shape and gives you n in one step.",
            "Add && or when for an extra test: if (v case int n when n > 3).",
            "A else branch handles the mismatch.",
        ),
        example="""
            Object? v = (1, 2);
            if (v case (int a, int b)) {
              print(a + b);
            }
            Object? w = 'text';
            if (w case int n) {
              print(n);
            } else {
              print('not an int');
            }
        """,
        out="3\nnot an int",
    ),
    *dart(
        "sealed-class",
        "Sealed class",
        "A class marked sealed whose direct subclasses are all in the same file. Because the compiler knows the full list, a switch over it must handle each one and needs no default.",
        see=("switch-expression", "abstract-class", "enum"),
        priority=75,
        aka=("sealed", "sealed classes", "exhaustive", "exhaustiveness", "exhaustive switch", "algebraic data type", "union type"),
        detect=(r"\bsealed\b",),
        rules=(
            "A sealed class cannot be built itself (it is abstract).",
            "Missing a subclass in the switch is a compile error, so a new subclass shows every place to update.",
            "Subclasses may be extended in the same library only.",
        ),
        example="""
            sealed class Shape {}
            class Circle extends Shape {
              final double r;
              Circle(this.r);
            }
            class Square extends Shape {
              final double s;
              Square(this.s);
            }
            double area(Shape sh) => switch (sh) {
              Circle(r: var r) => 3 * r * r,
              Square(s: var x) => x * x,
            };
            void main() {
              print(area(Circle(2)));
              print(area(Square(3)));
            }
        """,
        out="12.0\n9.0",
    ),
]
