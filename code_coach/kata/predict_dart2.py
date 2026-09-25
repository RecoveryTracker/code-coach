"""Predict the output, in Dart: a second set.

The first set (predict_dart.py) is about values: division, equality,
null, laziness. This one is about the parts of Dart a Flutter app leans
on as soon as it has more than one screen — classes, collections built
with `...` and `if`, and above all the order that asynchronous code
runs in. `setState` after an `await`, a `FutureBuilder`, a stream that
fires "later" — every one of them depends on knowing which line prints
first, and the answer is rarely the order the lines are written in.

As before, the answers are for Dart on the VM (`dart run`, and a phone).
Every expected output was typed out first and then checked by running
it, and the suite keeps checking.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p


DART_PUZZLES_2: tuple[Puzzle, ...] = (
    _p(
        id="predict-dart-parse",
        level=1,
        language="dart",
        name="Reading a number out of a string",
        family="Dart",
        code=(
            "void main() {\n"
            "  print(int.parse('42') + 1);\n"
            "  print(double.parse('42'));\n"
            "  print(num.parse('42'));\n"
            "  print(int.tryParse('4.2'));\n"
            "}"
        ),
        expect="43\n42.0\n42\nnull",
        why=(
            "`double.parse` makes a double even from a whole number, and "
            "a double always prints its decimal point. `num.parse` picks "
            "for you: an int if the text looks like one. `int.parse` is "
            "strict — '4.2' is not an int, and rather than rounding it "
            "throws a FormatException. `tryParse` hands back null "
            "instead, which is the one to use on a TextField."
        ),
    ),
    _p(
        id="predict-dart-named-params",
        level=2,
        language="dart",
        name="Named parameters and their defaults",
        family="Dart",
        code=(
            "String greet(String name, {String greeting = 'Hi', int times = 1}) =>\n"
            "    '$greeting $name' * times;\n"
            "\n"
            "void main() {\n"
            "  print(greet('Ada'));\n"
            "  print(greet('Bo', times: 2));\n"
            "  print(greet(greeting: 'Yo', 'Cy'));\n"
            "}"
        ),
        expect="Hi Ada\nHi BoHi Bo\nYo Cy",
        why=(
            "Parameters inside braces are named: leave one out and its "
            "default is used, give it and the name says which. Named "
            "arguments can go anywhere in the call, even before the "
            "positional one, which is how Flutter can put `child:` last. "
            "And `*` repeats the string with nothing in between, so the "
            "two greetings run together."
        ),
    ),
    _p(
        id="predict-dart-list-alias",
        level=2,
        language="dart",
        name="A copy, and something that is not one",
        family="Dart",
        code=(
            "void main() {\n"
            "  var a = [1, 2];\n"
            "  var b = a;\n"
            "  var c = List.from(a);\n"
            "  var d = [...a];\n"
            "  a.add(3);\n"
            "  print('$b $c $d');\n"
            "}"
        ),
        expect="[1, 2, 3] [1, 2] [1, 2]",
        why=(
            "`=` never copies a list — `b` is a second name for the same "
            "one, so it sees the new 3. `List.from` and a spread each "
            "build a new list with the same items. This is why Flutter "
            "state code writes `items = [...items, x]` rather than "
            "`items.add(x)`: a widget that compares the old list with "
            "the new one sees no change if they are the same list."
        ),
    ),
    _p(
        id="predict-dart-getter",
        level=3,
        language="dart",
        name="A getter, and a field that looks the same",
        family="Dart",
        code=(
            "var n = 0;\n"
            "\n"
            "class Clock {\n"
            "  int get tick => ++n;\n"
            "  final start = ++n;\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  var c = Clock();\n"
            "  print([c.tick, c.tick, c.start, c.start]);\n"
            "}"
        ),
        expect="[2, 3, 1, 1]",
        why=(
            "From outside, `c.tick` and `c.start` look alike, but a "
            "getter is a method without brackets: it runs again every "
            "time it is read. The field's initialiser ran once, when the "
            "Clock was made, before either tick. A getter in a widget "
            "that filters or sorts does that work on every read, every "
            "build."
        ),
    ),
    _p(
        id="predict-dart-collection-if",
        level=3,
        language="dart",
        name="A list built with if and for",
        family="Dart",
        code=(
            "void main() {\n"
            "  var extra = <int>[];\n"
            "  List<int>? none;\n"
            "  var loggedIn = false;\n"
            "  var xs = [0, ...extra, ...?none, if (loggedIn) 1 else 2,\n"
            "    for (var i in [3, 4]) i * 10];\n"
            "  print(xs);\n"
            "  print({...{'a': 1, 'b': 1}, 'a': 2});\n"
            "}"
        ),
        expect="[0, 2, 30, 40]\n{a: 2, b: 1}",
        why=(
            "Spreading an empty list adds nothing, `...?` spreads a list "
            "that may be null, and `if` and `for` inside the brackets "
            "add elements rather than being statements. It is how a "
            "Flutter `children:` list shows a widget only sometimes. In "
            "a map, a later key replaces the earlier value but keeps its "
            "place in the order."
        ),
    ),
    _p(
        id="predict-dart-hashcode",
        level=3,
        language="dart",
        name="Equal, and still in the set twice",
        family="Dart",
        code=(
            "class P {\n"
            "  final int x;\n"
            "  P(this.x);\n"
            "  @override\n"
            "  bool operator ==(Object o) => o is P && o.x == x;\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print(P(1) == P(1));\n"
            "  print({P(1), P(1)}.length);\n"
            "  print([P(1)].contains(P(1)));\n"
            "}"
        ),
        expect="true\n2\ntrue",
        why=(
            "A Set and a Map look at `hashCode` first and only ask `==` "
            "when two hashes match. This class changed `==` but kept the "
            "hashCode every object gets, which differs for each one, so "
            "the set never compares them. A List's `contains` just walks "
            "and asks `==`, so it agrees. Override the two together — or "
            "use a record, which does both."
        ),
    ),
    _p(
        id="predict-dart-await-order",
        level=4,
        language="dart",
        name="Where an async function stops",
        family="Dart",
        code=(
            "Future<void> work(String n) async {\n"
            "  print('start $n');\n"
            "  await null;\n"
            "  print('end $n');\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  work('a');\n"
            "  work('b');\n"
            "  print('main');\n"
            "}"
        ),
        expect="start a\nstart b\nmain\nend a\nend b",
        why=(
            "Calling an async function runs it straight away, line by "
            "line, until its first `await` — only then does it hand back "
            "a Future and let the caller carry on. Everything after the "
            "await waits until the code that is running now has "
            "finished, even when what it awaits is already there. That "
            "is why a widget can be gone by the time the line after an "
            "await runs, and why Flutter asks you to check `mounted`."
        ),
    ),
    _p(
        id="predict-dart-microtask",
        level=4,
        language="dart",
        name="Now, soon, and later",
        family="Dart",
        code=(
            "import 'dart:async';\n"
            "\n"
            "void main() {\n"
            "  print(1);\n"
            "  Future(() => print(2));\n"
            "  scheduleMicrotask(() => print(3));\n"
            "  Future.value(4).then(print);\n"
            "  print(5);\n"
            "}"
        ),
        expect="1\n5\n3\n4\n2",
        why=(
            "Dart has two queues. The ordinary code runs first, all of "
            "it. Then every microtask, in the order they were queued — "
            "`then` on a future that already has its value is one. Only "
            "then the event queue, where `Future(...)` puts its work, "
            "alongside timers, taps and frames. So a plain Future is the "
            "last thing to happen, not the next."
        ),
    ),
    _p(
        id="predict-dart-future-wait",
        level=4,
        language="dart",
        name="Three futures, finishing out of order",
        family="Dart",
        code=(
            "Future<int> after(int ms) =>\n"
            "    Future.delayed(Duration(milliseconds: ms), () {\n"
            "      print('done $ms');\n"
            "      return ms;\n"
            "    });\n"
            "\n"
            "void main() {\n"
            "  Future.wait([after(30), after(10), after(20)]).then(print);\n"
            "}"
        ),
        expect="done 10\ndone 20\ndone 30\n[30, 10, 20]",
        why=(
            "All three start at once, so they finish in order of how "
            "long they take. But `Future.wait` gives back the results in "
            "the order the futures were listed, not the order they "
            "finished — so the answer can be read by position, which is "
            "what makes it safe to load a profile and its settings side "
            "by side."
        ),
    ),
    _p(
        id="predict-dart-mixin-order",
        level=5,
        language="dart",
        name="Two mixins, one method",
        family="Dart",
        code=(
            "class Base { String hi() => 'Base'; }\n"
            "mixin A on Base { String hi() => 'A>' + super.hi(); }\n"
            "mixin B on Base { String hi() => 'B>' + super.hi(); }\n"
            "class C extends Base with A, B {}\n"
            "class D extends Base with B, A {}\n"
            "\n"
            "void main() {\n"
            "  print(C().hi());\n"
            "  print(D().hi());\n"
            "}"
        ),
        expect="B>A>Base\nA>B>Base",
        why=(
            "Each mixin is stacked on top of what came before it, so the "
            "last one in the `with` list is the outermost and its method "
            "runs first. Its `super` is the mixin before it, not Base. "
            "Swapping the order swaps the answer. A Flutter State with "
            "`TickerProviderStateMixin` and others is layered the same "
            "way."
        ),
    ),
    _p(
        id="predict-dart-extension",
        level=5,
        language="dart",
        name="An extension that tries to replace a method",
        family="Dart",
        code=(
            "extension Loud on String {\n"
            "  String toUpperCase() => 'LOUD';\n"
            "  String shout() => '${toUpperCase()}!';\n"
            "}\n"
            "\n"
            "void main() {\n"
            "  print('hi'.toUpperCase());\n"
            "  print('hi'.shout());\n"
            "  print(Loud('hi').toUpperCase());\n"
            "}"
        ),
        expect="HI\nLOUD!\nLOUD",
        why=(
            "An extension can add methods but never replace one: String "
            "already has toUpperCase, so `'hi'.toUpperCase()` ignores the "
            "extension. Inside the extension, though, a bare name is "
            "looked up there first, so `shout` calls its own. Naming the "
            "extension, as in `Loud('hi')`, is the way to ask for it "
            "from outside."
        ),
    ),
    _p(
        id="predict-dart-record-named",
        level=5,
        language="dart",
        name="A record with a name in it",
        family="Dart",
        code=(
            "(int, {String name}) pick() => (7, name: 'Ada');\n"
            "\n"
            "void main() {\n"
            "  var r = pick();\n"
            "  print(r);\n"
            "  print(r.$1 + r.name.length);\n"
            "  var (n, name: who) = r;\n"
            "  print('$who$n');\n"
            "  print((1, name: 'x') == (name: 'x', 1));\n"
            "}"
        ),
        expect="(7, name: Ada)\n10\nAda7\ntrue",
        why=(
            "Positional fields are read as `$1`, `$2` — counting from "
            "one, not zero — and named ones by their name. Destructuring "
            "can give a named field a new local name with `name: who`. "
            "Named fields have no order, so where one is written makes "
            "no difference to equality. It is the tidy way to return two "
            "things from a function."
        ),
    ),
)
