"""More code magnet puzzles in Dart - the second set.

The first set (content_dart) covers a named constructor, a cascade and
an extension, a switch over an enum, putIfAbsent into a map of lists,
try/on/finally, and an unawaited Future. These are six more shapes that
Flutter code is made of: a getter and setter pair, a generic class, a
sealed class switched over by subtype, a record returned and
destructured, an override that calls super (the shape of initState),
and a lazy async* stream read with await for.

The same rules hold. Top-level declarations go in any order; inside a
body, statements run top to bottom. Marking runs what was arranged, so
any order that prints the right thing is right. The expected output
beside each was typed out by a person and is held to what `dart run`
prints by tests/test_magnets_dart2.py.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m


DART_MAGNETS_2: tuple[Magnet, ...] = (
    _m(
        id="magnet-dart-getter-setter",
        plan=(
            ("A class that guards its value", 5),
            ("Make one", 2),
            ("Set it twice, reading it back each time", 5),
        ),
        level=1,
        name="A getter and a setter",
        family="Dart",
        language="dart",
        note=(
            "From outside, `v.level = 42` looks like setting a field, but "
            "it calls the setter, which caps the value at 10 before storing "
            "it in the private `_level`. Reading `v.level` calls the getter. "
            "That is why Dart classes start with plain public fields: you "
            "can swap one for a getter and setter later without changing a "
            "single caller. The underscore makes `_level` private to the "
            "file. Inside main the order matters - each print shows the "
            "value set just above it, so swap the two assignments and the "
            "output swaps too."
        ),
        code=(
            "class Volume {\n"
            "  int _level = 5;\n"
            "  int get level => _level;\n"
            "  set level(int value) => _level = value > 10 ? 10 : value;\n"
            "}\n"
            "void main() {\n"
            "  final v = Volume();\n"
            "  v.level = 7;\n"
            "  print('level ${v.level}');\n"
            "  v.level = 42;\n"
            "  print('level ${v.level}');\n"
            "}"
        ),
        expect="level 7\nlevel 10",
    ),
    _m(
        id="magnet-dart-generic-box",
        plan=(
            ("A box that holds one value of any type", 6),
            ("Box a word, then turn it into a number", 3),
            ("Show both boxes", 3),
        ),
        level=2,
        name="A generic class",
        family="Dart",
        language="dart",
        note=(
            "`Box<T>` holds one value of whatever type it is made with, "
            "and Dart works T out from the constructor call: `Box('flutter')` "
            "is a `Box<String>`. `map` has a type parameter of its own, R, "
            "so the function it is given decides what the new box holds - "
            "here a String goes in and an int comes out. That is the shape "
            "of `Future<T>.then`, `List<T>.map` and Flutter's `State<T>`. "
            "`size` is made from `word`, so it has to come after it, and "
            "the prints come out in the order they are written."
        ),
        code=(
            "class Box<T> {\n"
            "  final T value;\n"
            "  Box(this.value);\n"
            "  Box<R> map<R>(R Function(T) f) => Box(f(value));\n"
            "  @override String toString() => 'Box($value)';\n"
            "}\n"
            "void main() {\n"
            "  final word = Box('flutter');\n"
            "  final size = word.map((s) => s.length);\n"
            "  print(word);\n"
            "  print(size);\n"
            "}"
        ),
        expect="Box(flutter)\nBox(7)",
    ),
    _m(
        id="magnet-dart-sealed-switch",
        plan=(
            ("The only kinds of shape there are", 6),
            ("Describe each kind", 4),
            ("Describe a square and a dot", 1),
        ),
        level=2,
        name="A sealed class and a switch",
        family="Dart",
        language="dart",
        note=(
            "`sealed` means every subtype of Shape is declared in this file, "
            "so the compiler knows the full list - and a switch over a Shape "
            "with an arm for each one needs no `_` catch-all. Add a third "
            "shape and every switch that has not heard of it stops "
            "compiling. `Square(side: final n)` is an object pattern: it "
            "checks the type and pulls the field out in one go. This is how "
            "Flutter code models states like loading, loaded and failed. "
            "The classes and the function can sit in any order around "
            "main, because they are all top-level declarations."
        ),
        code=(
            "sealed class Shape {}\n"
            "class Dot extends Shape {}\n"
            "class Square extends Shape {\n"
            "  Square(this.side);\n"
            "  final int side;\n"
            "}\n"
            "String describe(Shape s) => switch (s) {\n"
            "  Dot() => 'a dot',\n"
            "  Square(side: final n) => 'a square of area ${n * n}',\n"
            "};\n"
            "void main() => [Square(3), Dot()].map(describe).forEach(print);"
        ),
        expect="a square of area 9\na dot",
    ),
    _m(
        id="magnet-dart-record",
        plan=(
            ("Start both ends at the first number", 2),
            ("Stretch them to fit every number", 4),
            ("Hand back both at once", 2),
            ("Unpack the pair and print it", 4),
        ),
        level=3,
        name="Returning two values in a record",
        family="Dart",
        language="dart",
        note=(
            "`(int, int)` is a record type: two values handed back together "
            "without a class to hold them. `return (lo, hi);` builds one, "
            "and `final (low, high) = ...` takes it apart again into two "
            "locals - a destructuring pattern. Both ends have to start at a "
            "real number before the loop can stretch them, and the return "
            "has to come after the loop, or it hands back the first number "
            "twice. Records arrived in Dart 3 and are the tidy answer to "
            "'I need to return two things'."
        ),
        code=(
            "(int, int) minMax(List<int> xs) {\n"
            "  var lo = xs.first, hi = xs.first;\n"
            "  for (final x in xs) {\n"
            "    if (x < lo) lo = x;\n"
            "    if (x > hi) hi = x;\n"
            "  }\n"
            "  return (lo, hi);\n"
            "}\n"
            "void main() {\n"
            "  final (low, high) = minMax([4, 9, 1, 7]);\n"
            "  print('from $low to $high, a spread of ${high - low}');\n"
            "}"
        ),
        expect="from 1 to 9, a spread of 8",
    ),
    _m(
        id="magnet-dart-super-call",
        plan=(
            ("A base class that sets up any screen", 4),
            ("A home screen with its own title", 2),
            ("Opening it: the shared part, then its own", 5),
            ("Open the home screen", 1),
        ),
        level=3,
        name="An override that calls super",
        family="Dart",
        language="dart",
        note=(
            "Screen is abstract: it leaves `title` for each subclass to "
            "fill in, and cannot be made on its own. Home overrides `open`, "
            "and `super.open()` runs the base class's version first - which "
            "itself reads the title Home supplied. This is exactly the "
            "shape of `initState` in a Flutter State: call "
            "`super.initState()` first, then your own set-up (and in "
            "`dispose`, your own clean-up first, then super). Move the "
            "super call below the print and the lines come out the other "
            "way round."
        ),
        code=(
            "abstract class Screen {\n"
            "  String get title;\n"
            "  void open() => print('set up $title');\n"
            "}\n"
            "class Home extends Screen {\n"
            "  @override String get title => 'Home';\n"
            "  @override void open() {\n"
            "    super.open();\n"
            "    print('load $title data');\n"
            "  }\n"
            "}\n"
            "void main() => Home().open();"
        ),
        expect="set up Home\nload Home data",
    ),
    _m(
        id="magnet-dart-await-for",
        plan=(
            ("A stream that counts down", 6),
            ("Make the stream without listening yet", 3),
            ("Listen to every tick, then finish", 3),
        ),
        level=4,
        name="A lazy stream and await for",
        family="Dart",
        language="dart",
        note=(
            "`async*` makes a function that returns a Stream, and each "
            "`yield` sends one value down it. The surprise is when the body "
            "runs: not when `countdown(3)` is called, but when something "
            "starts listening - so 'stream made' prints before 'counting "
            "from 3'. `await for` listens, runs its body once per value, "
            "and only moves on when the stream is done, so 'liftoff' comes "
            "last. Flutter's StreamBuilder is the widget version of this "
            "loop. main awaits, so it is `async` and returns "
            "`Future<void>`."
        ),
        code=(
            "Stream<int> countdown(int from) async* {\n"
            "  print('counting from $from');\n"
            "  for (var i = from; i > 0; i--) {\n"
            "    yield i;\n"
            "  }\n"
            "}\n"
            "Future<void> main() async {\n"
            "  final ticks = countdown(3);\n"
            "  print('stream made');\n"
            "  await for (final n in ticks) print('tick $n');\n"
            "  print('liftoff');\n"
            "}"
        ),
        expect=(
            "stream made\ncounting from 3\ntick 3\ntick 2\ntick 1\nliftoff"
        ),
    ),
)
