"""Predict the output, in Dart: a third set.

The first two sets cover values (division, equality, null, laziness) and
the order asynchronous code runs in. This one is the everyday toolkit a
Dart file reaches for once it is more than a demo: formatting numbers and
strings, cascades, spreads, records and patterns, sealed classes, a
generator, lazy iterables, `fold` and `whereType`, null-aware chains, `const`
identity, and a stream's order against an `await`. No timers: where the
order of asynchronous work matters it is microtasks and zero-length event
turns only, so nothing here depends on a clock.

As before, the answers are for Dart on the VM. Every expected output was
worked out by hand first and then checked by running it, and the suite
keeps checking.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p


DART_PUZZLES_3: tuple[Puzzle, ...] = (
    _p(
        id="predict-dart3-fixed",
        level=1,
        language="dart",
        name="Rounding to places",
        family="Dart",
        code=(
            "void main() {\n"
            "  print(3.14159.toStringAsFixed(2));\n"
            "  print(2.5.round());\n"
            "  print((-2.5).round());\n"
            "  print(7.toStringAsFixed(1));\n"
            "}"
        ),
        expect="3.14\n3\n-3\n7.0",
        why=(
            "`toStringAsFixed` gives back a String with exactly that many "
            "places, which is what a price label wants. `round` sends a "
            "half away from zero, so 2.5 goes up to 3 and -2.5 goes down "
            "to -3 — not the banker's rounding Python does, where "
            "round(2.5) is 2. And it works on an int too: padding 7 out "
            "to '7.0' is the usual way to show a whole price with its "
            "decimal."
        ),
    ),
    _p(
        id="predict-dart3-buffer",
        level=1,
        language="dart",
        name="Building a string in a buffer",
        family="Dart",
        code=(
            "void main() {\n"
            "  var sb = StringBuffer('a');\n"
            "  sb.write('b');\n"
            "  sb.writeAll(['c', 'd'], '-');\n"
            "  sb.write('e');\n"
            "  print(sb.length);\n"
            "  print(sb);\n"
            "}"
        ),
        expect="6\nabc-de",
        why=(
            "A StringBuffer collects pieces without making a new String "
            "for every `+`, which matters in a loop. `writeAll` puts its "
            "separator between the items, not after the last one, so "
            "'c' and 'd' land as `c-d`. The length counts everything "
            "written so far: abc-de is six characters. `print` calls "
            "toString on it, which is when the pieces are joined."
        ),
    ),
    _p(
        id="predict-dart3-split-trim",
        level=1,
        language="dart",
        name="Cutting up a string",
        family="Dart",
        code=(
            "void main() {\n"
            "  print('a,b,,c'.split(',').length);\n"
            "  print('  hi '.trim().length);\n"
            "  print('abc'.substring(1));\n"
            "  print('abc'[1] + 'abc'.codeUnitAt(0).toString());\n"
            "}"
        ),
        expect="4\n2\nbc\nb97",
        why=(
            "`split` keeps the empty piece between two commas, so "
            "'a,b,,c' is four pieces, not three. `trim` takes the spaces "
            "off both ends and leaves 'hi'. `substring(1)` runs from "
            "index 1 to the end. Indexing a string gives a one-character "
            "String, not a number, and `codeUnitAt` is the way to get "
            "the number — 97 for 'a' — so the last line joins the text "
            "'b' to the text '97'."
        ),
    ),
    _p(
        id="predict-dart3-chain-cascade",
        level=2,
        language="dart",
        name="A cascade against a chain",
        family="Dart",
        code=(
            "class Counter {\n"
            "  int n = 0;\n"
            "  Counter inc() { n++; return this; }\n"
            "}\n"
            "void main() {\n"
            "  var c = Counter()..inc()..inc();\n"
            "  var d = Counter().inc().inc().inc();\n"
            "  print('${c.n} ${d.n}');\n"
            "  print((c..n = 10).n);\n"
            "}"
        ),
        expect="2 3\n10",
        why=(
            "Both styles end up counting, but they hand back different "
            "things. A chain (`.inc().inc()`) passes along whatever each "
            "call returns, which only works because inc returns `this`. "
            "A cascade (`..inc()..inc()`) ignores what the calls return "
            "and keeps the original object, so it works on methods that "
            "return nothing. The last line uses it on a setter: `..n = "
            "10` assigns, and the whole expression is `c`, so `.n` "
            "reads back the 10."
        ),
    ),
    _p(
        id="predict-dart3-spread-for",
        level=2,
        language="dart",
        name="Spread, null-spread and a for inside a list",
        family="Dart",
        code=(
            "void main() {\n"
            "  List<int>? extra;\n"
            "  var a = [1, 2];\n"
            "  var b = [...a, ...?extra, for (var i in a) i * 10];\n"
            "  print(b);\n"
            "  print([for (var i = 0; i < 3; i++) if (i != 1) i]);\n"
            "}"
        ),
        expect="[1, 2, 10, 20]\n[0, 2]",
        why=(
            "`...a` pours a list's items into the new one. `...?extra` "
            "does the same only if the list is not null, and here it is "
            "null, so it adds nothing instead of crashing. A `for` "
            "inside the brackets runs its body once per item and adds "
            "what it produces, and an `if` in there adds nothing when "
            "it is false — so index 1 is skipped. It is how a Flutter "
            "`children:` list is built."
        ),
    ),
    _p(
        id="predict-dart3-int-div-order",
        level=2,
        language="dart",
        name="Integer division in a longer sum",
        family="Dart",
        code=(
            "void main() {\n"
            "  print(7 ~/ 2 * 2);\n"
            "  print(7 / 2 * 2);\n"
            "  print(10 ~/ 3 + 10 % 3);\n"
            "  print((7.5 ~/ 2).runtimeType);\n"
            "}"
        ),
        expect="6\n7.0\n4\nint",
        why=(
            "`~/`, `*` and `%` all sit at the same level and run left "
            "to right. So `7 ~/ 2 * 2` is 3 * 2, which is 6 — the "
            "remainder is lost, unlike `7 / 2 * 2`, which is 3.5 * 2 and "
            "prints as the double 7.0. The third is 3 + 1. And `~/` "
            "always gives back an int, even from a double: 7.5 ~/ 2 "
            "is the whole number 3."
        ),
    ),
    _p(
        id="predict-dart3-record-swap",
        level=3,
        language="dart",
        name="Destructuring in place",
        family="Dart",
        code=(
            "void main() {\n"
            "  var (a, b) = (1, 2);\n"
            "  (a, b) = (b, a + b);\n"
            "  (a, b) = (b, a + b);\n"
            "  print('$a $b');\n"
            "  var (x, [y, ...rest]) = (0, [5, 6, 7]);\n"
            "  print('$x $y $rest');\n"
            "}"
        ),
        expect="3 5\n0 5 [6, 7]",
        why=(
            "The right-hand side of a pattern assignment is built "
            "completely before anything is assigned, so `(a, b) = "
            "(b, a + b)` swaps without a temporary: it uses the old a "
            "and b both times. Two steps take (1, 2) to (2, 3) and then "
            "(3, 5) — Fibonacci. The second declaration nests a list "
            "pattern inside a record pattern: `y` takes the first item "
            "and `...rest` takes everything after it."
        ),
    ),
    _p(
        id="predict-dart3-switch-patterns",
        level=3,
        language="dart",
        name="A switch expression that checks types",
        family="Dart",
        code=(
            "String sort(Object o) => switch (o) {\n"
            "  int n when n < 0 => 'neg',\n"
            "  int() => 'int',\n"
            "  String s when s.isEmpty => 'blank',\n"
            "  String() => 'text',\n"
            "  [var first, ...] => 'list:$first',\n"
            "  _ => 'other',\n"
            "};\n"
            "void main() {\n"
            "  for (var v in [-3, 8, '', 'hi', [9, 1], 2.5]) print(sort(v));\n"
            "}"
        ),
        expect="neg\nint\nblank\ntext\nlist:9\nother",
        why=(
            "The arms are tried top to bottom and the first match "
            "wins. `int n when n < 0` only matches a negative int, so "
            "8 falls through to the plain `int()` arm below it — swap "
            "those two and every int would be 'int'. A String is "
            "checked the same way, blank first. `[var first, ...]` "
            "matches any list with at least one item and names the first. "
            "2.5 matches nothing but the `_` at the end."
        ),
    ),
    _p(
        id="predict-dart3-sealed",
        level=3,
        language="dart",
        name="Taking a sealed class apart",
        family="Dart",
        code=(
            "sealed class Result {}\n"
            "class Ok extends Result { final int v; Ok(this.v); }\n"
            "class Err extends Result { final String m; Err(this.m); }\n"
            "String show(Result r) => switch (r) {\n"
            "  Ok(:var v) => 'ok $v',\n"
            "  Err(:var m) => 'err $m',\n"
            "};\n"
            "void main() {\n"
            "  for (var r in [Ok(1), Err('x'), Ok(30)]) print(show(r));\n"
            "}"
        ),
        expect="ok 1\nerr x\nok 30",
        why=(
            "`sealed` tells the compiler Ok and Err are the only kinds "
            "of Result, so the switch needs no `_` arm and would not "
            "compile if one kind were missing. `Ok(:var v)` is an object "
            "pattern: it checks the type and pulls the field `v` into a "
            "variable of the same name. The list `[Ok(1), Err('x'), "
            "Ok(30)]` is a list of Result, and each item is taken "
            "apart by whichever arm fits."
        ),
    ),
    _p(
        id="predict-dart3-sync-star",
        level=3,
        language="dart",
        name="A generator that runs a bit at a time",
        family="Dart",
        code=(
            "Iterable<int> count(int n) sync* {\n"
            "  print('start');\n"
            "  for (var i = 1; i <= n; i++) {\n"
            "    yield i;\n"
            "    print('after $i');\n"
            "  }\n"
            "}\n"
            "void main() {\n"
            "  var it = count(2);\n"
            "  print('made');\n"
            "  for (var x in it) print('got $x');\n"
            "}"
        ),
        expect="made\nstart\ngot 1\nafter 1\ngot 2\nafter 2",
        why=(
            "Calling a `sync*` function runs none of its body — it hands "
            "back an Iterable and waits. 'made' prints first. The body "
            "starts when the `for` asks for the first item, runs to the "
            "first `yield`, and stops there while the loop body gets its "
            "turn. Asking for the next item resumes it on the line after "
            "the `yield`, which is why 'after 1' comes after 'got 1', "
            "not before."
        ),
    ),
    _p(
        id="predict-dart3-lazy-map",
        level=4,
        language="dart",
        name="When a map actually runs",
        family="Dart",
        code=(
            "void main() {\n"
            "  var n = 0;\n"
            "  var doubled = [1, 2, 3].map((x) { n++; return x * 2; });\n"
            "  print(n);\n"
            "  print(doubled.first);\n"
            "  print(n);\n"
            "  print(doubled.toList());\n"
            "  print(n);\n"
            "}"
        ),
        expect="0\n2\n1\n[2, 4, 6]\n4",
        why=(
            "`map` on an Iterable does nothing yet — it builds a recipe, "
            "so n is still 0. `first` only needs one item, so the "
            "function runs once (n is 1) and the other two are never "
            "touched. `toList()` needs everything and runs the function "
            "for all three items, again from the start, which takes n to "
            "4: the first item was computed twice. Anything with side "
            "effects inside a `map` runs whenever the result is read, "
            "not when it is written."
        ),
    ),
    _p(
        id="predict-dart3-wheretype-fold",
        level=4,
        language="dart",
        name="Filtering by type, then folding",
        family="Dart",
        code=(
            "void main() {\n"
            "  var mix = [1, 'a', 2.5, 3, null, 'b'];\n"
            "  print(mix.whereType<int>().toList());\n"
            "  print(mix.whereType<num>().length);\n"
            "  print(mix.whereType<String>().fold<String>('', (acc, s) => s + acc));\n"
            "  print(mix.whereType<int>().fold<int>(10, (a, b) => a - b));\n"
            "}"
        ),
        expect="[1, 3]\n3\nba\n6",
        why=(
            "`whereType<T>()` keeps the items that are a T, and the "
            "result is typed as T as well — null matches nothing. "
            "`num` takes in both the ints and the double, so three. "
            "`fold` starts from a seed and combines one item at a time: "
            "with `s + acc` each string goes in front of what was "
            "built, so 'a' then 'b' makes 'ba', backwards. The last "
            "starts at 10 and takes away 1, then 3."
        ),
    ),
    _p(
        id="predict-dart3-null-chain",
        level=4,
        language="dart",
        name="A chain that stops at the first null",
        family="Dart",
        code=(
            "class User {\n"
            "  String? name;\n"
            "  User(this.name);\n"
            "}\n"
            "void main() {\n"
            "  User? u;\n"
            "  print(u?.name?.length);\n"
            "  u = User(null);\n"
            "  print(u.name?.length ?? -1);\n"
            "  u.name ??= 'anon';\n"
            "  print(u.name!.toUpperCase());\n"
            "}"
        ),
        expect="null\n-1\nANON",
        why=(
            "`?.` stops the whole chain when it meets null and the "
            "answer is null — `.length` is never asked for, so there is "
            "no crash. `?? -1` gives that null a stand-in. `??=` "
            "assigns only if the thing is null now, so the name becomes "
            "'anon'; had it been set already it would be left alone. "
            "The `!` then promises Dart it is not null, which is true "
            "by that line, and `toUpperCase` runs."
        ),
    ),
    _p(
        id="predict-dart3-const-identity",
        level=5,
        language="dart",
        name="One constant, or a new one each time",
        family="Dart",
        code=(
            "class P {\n"
            "  final int x;\n"
            "  const P(this.x);\n"
            "}\n"
            "void main() {\n"
            "  print(identical(const P(1), const P(1)));\n"
            "  print(identical(const P(1), const P(2)));\n"
            "  print(identical(P(1), P(1)));\n"
            "  var a = P(1);\n"
            "  print(identical(a, const P(1)));\n"
            "}"
        ),
        expect="true\nfalse\nfalse\nfalse",
        why=(
            "Two `const` objects with the same values are one object in "
            "memory: Dart makes each combination once and reuses it, so "
            "`identical` says true. A different value is a different "
            "constant. But a const constructor is only const when "
            "called with `const` (or inside a const context); plain "
            "`P(1)` builds a fresh object every time, so two of them "
            "are not identical, and neither is one of them against the "
            "canonical `const P(1)`. This is why Flutter wants `const` "
            "on widgets: it lets a rebuild reuse the very same object."
        ),
    ),
    _p(
        id="predict-dart3-stream-order",
        level=5,
        language="dart",
        name="When a stream's items arrive",
        family="Dart",
        code=(
            "void main() {\n"
            "  var s = Stream.fromIterable([1, 2]);\n"
            "  s.listen((x) => print('got $x'));\n"
            "  print('listening');\n"
            "  Future(() {}).then((_) => print('done'));\n"
            "}"
        ),
        expect="listening\ngot 1\ngot 2\ndone",
        why=(
            "`listen` does not deliver anything straight away, even "
            "though the data is already sitting in a list: events go "
            "out from a microtask, so 'listening' prints first. The "
            "`Future(() {})` finishes on a later turn of the event loop, "
            "and all pending microtasks run before the event loop takes "
            "its next turn — so both items are delivered before 'done'. "
            "The order is fixed by the loop's rules, not by how long "
            "anything takes."
        ),
    ),
)
