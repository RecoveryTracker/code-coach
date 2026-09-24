"""The code magnet puzzles in Dart.

The same puzzle as the JavaScript ones: the lines of a program that
works, jumbled, to be put back in an order that prints the right thing.
The shapes are the ones Flutter code is made of — a model class with a
named constructor, a cascade, a switch over an enum, a map of lists, an
error caught by its type, and a Future that is waited for.

Two things are different from the JavaScript puzzles, and both are
worth knowing before arranging anything.

Every program has a `main`. Dart does not run loose statements at the
top of a file, so the first and last magnets of most puzzles are
`void main() {` and its closing brace — and a statement that ends up
outside main is a compile error rather than a line that runs early.

Top-level declarations go in any order. A class, an enum, an extension
or a function can sit above main or below it and the program is the
same, because Dart reads every declaration in the file before it runs
anything. That is Dart's version of JavaScript's hoisting, and it is why
these puzzles have more than one right answer: marking runs what you
arranged, so an order that works is right.

Inside main it is the other way round. A local has to be declared above
the line that uses it, and statements run top to bottom.

The expected output beside each was typed out by a person and is held
to what `dart run` actually prints by tests/test_magnets_dart.py.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m


DART_MAGNETS: tuple[Magnet, ...] = (
    _m(
        id="magnet-dart-named-constructor",
        plan=(
            ("Declare the class and what it holds", 3),
            ("Two ways to make one", 2),
            ("What one can do, and the end of the class", 2),
            ("Make them and show them in order", 5),
        ),
        level=1,
        name="A class with a second constructor",
        family="Dart",
        language="dart",
        note=(
            "Every Flutter model and widget is a class shaped like this. "
            "The plain constructor takes both fields; the named one, "
            "`Todo.finished`, is a second way in. The part after its "
            "colon is an initializer list, and it is the last chance a "
            "`final` field has to be set before the constructor body "
            "runs. Inside main the order matters: `todo` has to be "
            "declared above the line that uses it, and the two prints "
            "come out in the order they are written. The class itself "
            "can go above or below main — Dart reads every top-level "
            "declaration before it runs anything."
        ),
        code=(
            "class Todo {\n"
            "  final String title;\n"
            "  final bool done;\n"
            "  Todo(this.title, this.done);\n"
            "  Todo.finished(this.title) : done = true;\n"
            "  String show() => done ? '[x] $title' : '[ ] $title';\n"
            "}\n"
            "void main() {\n"
            "  final todo = Todo.finished('Write tests');\n"
            "  print(Todo('Buy milk', false).show());\n"
            "  print(todo.show());\n"
            "}"
        ),
        expect="[ ] Buy milk\n[x] Write tests",
    ),
    _m(
        id="magnet-dart-cascade",
        plan=(
            ("Teach every list of strings a new method", 3),
            ("Build the list in one expression", 6),
            ("Show it using the new method", 2),
        ),
        level=2,
        name="A cascade, and a method of your own",
        family="Dart",
        language="dart",
        note=(
            "Two things Flutter code leans on. The `..` is a cascade: "
            "each `..add` calls a method on the same list and hands back "
            "the list rather than what `add` returned, so one expression "
            "can build it — the same shape as `Paint()..color = ...` in "
            "a painter. Only the last line of a cascade carries the "
            "semicolon, and the others run top to bottom: put the "
            "`addAll` first and the names come out in a different order. "
            "The extension gives every `List<String>` a `summary()` "
            "method; inside it, `length` and `join` are the list's own. "
            "Like a class, it can sit above main or below it."
        ),
        code=(
            "extension Summary on List<String> {\n"
            "  String summary() => '$length: ${join(', ')}';\n"
            "}\n"
            "void main() {\n"
            "  final names = <String>[]\n"
            "    ..add('Ada')\n"
            "    ..add('Grace')\n"
            "    ..addAll(['Linus', 'Guido'])\n"
            "    ..remove('Grace');\n"
            "  print(names.summary());\n"
            "}"
        ),
        expect="3: Ada, Linus, Guido",
    ),
    _m(
        id="magnet-dart-switch-enum",
        plan=(
            ("The values it can be", 1),
            ("Turn each value into advice", 5),
            ("Go through every value and print its advice", 5),
        ),
        level=2,
        name="Switching on an enum",
        family="Dart",
        language="dart",
        note=(
            "A switch expression turns a value into an answer — the shape "
            "of picking a widget for each state in a `build` method. The "
            "arms are tried top to bottom and the first match wins, so "
            "the catch-all `_` goes last: put it first and this still "
            "compiles (the analyzer only warns) and every day gets the "
            "same advice. Without the `_`, every value of the enum needs "
            "its own arm or the program does not compile at all. That is "
            "exhaustiveness, and it is why adding a value to an enum "
            "points at every switch that has not heard about it yet. "
            "`Weather.values` is in the order the enum declares them, "
            "which is why the output is too."
        ),
        code=(
            "enum Weather { sunny, rainy, snowy, windy }\n"
            "String advice(Weather w) => switch (w) {\n"
            "  Weather.rainy => 'take an umbrella',\n"
            "  Weather.snowy => 'wear boots',\n"
            "  _ => 'go as you are',\n"
            "};\n"
            "void main() {\n"
            "  for (final w in Weather.values) {\n"
            "    print('${w.name}: ${advice(w)}');\n"
            "  }\n"
            "}"
        ),
        expect=(
            "sunny: go as you are\n"
            "rainy: take an umbrella\n"
            "snowy: wear boots\n"
            "windy: go as you are"
        ),
    ),
    _m(
        id="magnet-dart-put-if-absent",
        plan=(
            ("Start with the words and an empty map", 3),
            ("File each word under its first letter", 3),
            ("Print each letter with its words", 4),
        ),
        level=3,
        name="Grouping into a map of lists",
        family="Dart",
        language="dart",
        note=(
            "`putIfAbsent` is the grouping idiom: it returns the list "
            "already filed under that letter, or makes an empty one, "
            "files it and returns that — so the `.add` always has "
            "somewhere to go. The map has to exist before the loop that "
            "fills it, and the printing loop has to come after the "
            "filling one; the other way round it prints an empty map, "
            "which is to say nothing at all. A Dart map literal keeps "
            "the order keys were added, which is why a comes out before "
            "b. Three closing braces at the end: each loop's, then "
            "main's."
        ),
        code=(
            "void main() {\n"
            "  final words = ['apple', 'bean', 'avocado', 'beet', 'cherry'];\n"
            "  final Map<String, List<String>> byLetter = {};\n"
            "  for (final word in words) {\n"
            "    byLetter.putIfAbsent(word[0], () => []).add(word);\n"
            "  }\n"
            "  for (final entry in byLetter.entries) {\n"
            "    print('${entry.key}: ${entry.value.join(', ')}');\n"
            "  }\n"
            "}"
        ),
        expect="a: apple, avocado\nb: bean, beet\nc: cherry",
    ),
    _m(
        id="magnet-dart-finally",
        plan=(
            ("Try to read the number", 3),
            ("A fallback for text that is not a number", 2),
            ("A line that runs either way", 4),
            ("Parse two and print the results", 3),
        ),
        level=4,
        name="Where finally goes",
        family="Dart",
        language="dart",
        note=(
            "`on FormatException` catches that one kind of error and "
            "lets anything else through, and `int.parse` throws exactly "
            "that on text that is not a number — the everyday case of "
            "reading a text field. The surprise is `finally`: the `try` "
            "returns before it gets anywhere near it, and it runs anyway, "
            "once per call, whichever block did the returning. The "
            "blocks go try, then on, then finally; Dart will not compile "
            "them in another order. Swap the two returns and it still "
            "compiles and runs, and every answer is -1."
        ),
        code=(
            "int parse(String text) {\n"
            "  try {\n"
            "    return int.parse(text);\n"
            "  } on FormatException {\n"
            "    return -1;\n"
            "  } finally {\n"
            "    print('checked $text');\n"
            "  }\n"
            "}\n"
            "void main() {\n"
            "  print([parse('42'), parse('forty')]);\n"
            "}"
        ),
        expect="checked 42\nchecked forty\n[42, -1]",
    ),
    _m(
        id="magnet-dart-await",
        plan=(
            ("The part of loading that runs straight away", 2),
            ("Wait, then finish loading", 4),
            ("Start loading without waiting for it", 3),
            ("Wait for the data and print it", 2),
        ),
        level=5,
        name="Carrying on while it loads",
        family="Dart",
        language="dart",
        note=(
            "An async function runs like any other until its first "
            "`await` — that is why `load starts` prints before `main "
            "carries on`. At the await it hands its caller a Future that "
            "is still pending, main carries on, and load picks up where "
            "it left off only once main stops to wait for it. That is a "
            "Flutter app starting a fetch and carrying on building: the "
            "screen is drawn while the data is on its way. Move a print "
            "across an await and it moves in the output. main awaits "
            "too, so it is `async` and returns `Future<void>`."
        ),
        code=(
            "Future<String> load() async {\n"
            "  print('load starts');\n"
            "  await Future.delayed(Duration.zero);\n"
            "  print('load resumes');\n"
            "  return 'data';\n"
            "}\n"
            "Future<void> main() async {\n"
            "  final future = load();\n"
            "  print('main carries on');\n"
            "  print(await future);\n"
            "}"
        ),
        expect="load starts\nmain carries on\nload resumes\ndata",
    ),
)
