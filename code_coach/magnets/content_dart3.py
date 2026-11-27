"""More code magnet puzzles in Dart - the third set.

The first two sets cover a named constructor, a cascade, a switch over
an enum, putIfAbsent, finally, an unawaited Future, a getter and setter,
a generic class, a sealed class, a record, an override that calls super
and a lazy stream. These eight are more shapes Dart code is made of: a
mixin, an extension, a factory that hands out one shared object, an
async function awaited twice, a list built with where and a collection
for, try/on/catch around a throw, an endless sync* generator that is
only read as far as it is asked, and a sort by one key and then another.

The same rules hold. Top-level declarations go in any order; inside a
body, statements run top to bottom. Marking runs what was arranged, so
any order that prints the right thing is right. The expected output
beside each was worked out by hand first and is held to what `dart run`
prints by tests/test_magnets_dart3.py.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m


DART_MAGNETS_3: tuple[Magnet, ...] = (
    _m(
        id="magnet-dart3-mixin",
        plan=(
            ("A piece of behaviour to share", 3),
            ("A class that borrows it", 3),
            ("Make one and use it", 3),
        ),
        level=1,
        name="A mixin",
        family="Dart",
        language="dart",
        note=(
            "A mixin is behaviour with no family tree of its own: `class "
            "Dog with Loud` copies `shout` into Dog without Dog having to "
            "extend anything, so a class can take in several mixins. "
            "That is how Flutter hands out things like "
            "SingleTickerProviderStateMixin. `shout` is called from "
            "inside `bark` as if it were Dog's own method. The mixin and "
            "the class are top-level declarations, so they can sit above "
            "or below main in either order."
        ),
        code=(
            "mixin Loud {\n"
            "  String shout(String s) => s.toUpperCase();\n"
            "}\n"
            "class Dog with Loud {\n"
            "  String bark() => shout('woof');\n"
            "}\n"
            "void main() {\n"
            "  print(Dog().bark());\n"
            "}"
        ),
        expect="WOOF",
    ),
    _m(
        id="magnet-dart3-extension-int",
        plan=(
            ("Teach int two new tricks", 4),
            ("Try them on a number", 5),
        ),
        level=1,
        name="An extension on int",
        family="Dart",
        language="dart",
        note=(
            "An extension adds members to a type you did not write. "
            "Inside it, `this` is the int being asked, so `7.twice` is "
            "`7 * 2`. They are getters, so they are read without "
            "brackets, and they chain: `n.twice.isBig` asks the result "
            "of the first. The extension has to be declared before "
            "anything can use it only in the sense that the file has to "
            "contain it - top-level order does not matter - but inside "
            "main the prints come out in the order they are written, so "
            "swap them and the output swaps."
        ),
        code=(
            "extension IntX on int {\n"
            "  int get twice => this * 2;\n"
            "  bool get isBig => this > 10;\n"
            "}\n"
            "void main() {\n"
            "  var n = 7;\n"
            "  print(n.twice);\n"
            "  print(n.twice.isBig);\n"
            "}"
        ),
        expect="14\ntrue",
    ),
    _m(
        id="magnet-dart3-factory-shared",
        plan=(
            ("A class that hands out one shared object", 6),
            ("Bump the count from two places", 3),
            ("Show the count and the identity", 3),
        ),
        level=2,
        name="A factory that shares one object",
        family="Dart",
        language="dart",
        note=(
            "A normal constructor makes a new object every call. A "
            "`factory` constructor can return whatever it likes - here "
            "the same `_one` every time - so `Logger()` looks like "
            "construction but is really a lookup. The private "
            "constructor `Logger._()` is how the class makes its single "
            "instance and keeps everyone else from making more. That is "
            "why the two bumps land on one counter, and why `identical` "
            "is true. The prints have to come after the bumps or they "
            "would see 0."
        ),
        code=(
            "class Logger {\n"
            "  static final Logger _one = Logger._();\n"
            "  Logger._();\n"
            "  factory Logger() => _one;\n"
            "  int count = 0;\n"
            "}\n"
            "void main() {\n"
            "  Logger().count++;\n"
            "  Logger().count++;\n"
            "  print(Logger().count);\n"
            "  print(identical(Logger(), Logger()));\n"
            "}"
        ),
        expect="2\ntrue",
    ),
    _m(
        id="magnet-dart3-where-for",
        plan=(
            ("Start with some fruit", 2),
            ("Keep the short ones and put them in order", 3),
            ("Shout them", 3),
        ),
        level=2,
        name="Filter, sort, then a collection for",
        family="Dart",
        language="dart",
        note=(
            "`where` keeps the items that pass the test but gives back a "
            "lazy Iterable, so `toList()` is what makes a real list that "
            "can be sorted. `sort` changes the list in place and "
            "returns nothing, so it has to sit on its own line, before "
            "anything that wants the sorted order. The last step builds "
            "a new list with a `for` inside the brackets. Move `sort` "
            "below the first print and the first list comes out in the "
            "original order instead."
        ),
        code=(
            "void main() {\n"
            "  var words = ['pear', 'fig', 'apple', 'kiwi'];\n"
            "  var short = words.where((w) => w.length <= 4).toList();\n"
            "  short.sort();\n"
            "  print(short);\n"
            "  var caps = [for (var w in short) w.toUpperCase()];\n"
            "  print(caps);\n"
            "}"
        ),
        expect="[fig, kiwi, pear]\n[FIG, KIWI, PEAR]",
    ),
    _m(
        id="magnet-dart3-await-twice",
        plan=(
            ("A function that works asynchronously", 4),
            ("Wait for each answer in turn", 5),
        ),
        level=3,
        name="Awaiting one result after another",
        family="Dart",
        language="dart",
        note=(
            "An `async` function hands back a Future, and `await` waits "
            "for it without freezing everything else. The second call "
            "needs the first's answer, so the awaits have to be in that "
            "order: `a` is 2, then `b` is fetch(2), which is 4. "
            "The 'fetching' lines print as each call starts, so they "
            "come out in the order the calls are made. `main` is itself "
            "async here, which is what lets it use `await` at all."
        ),
        code=(
            "Future<int> fetch(int n) async {\n"
            "  print('fetching $n');\n"
            "  return n * 2;\n"
            "}\n"
            "Future<void> main() async {\n"
            "  var a = await fetch(1);\n"
            "  var b = await fetch(a);\n"
            "  print('total ${a + b}');\n"
            "}"
        ),
        expect="fetching 1\nfetching 2\ntotal 6",
    ),
    _m(
        id="magnet-dart3-try-on-string",
        plan=(
            ("A check that complains about small numbers", 4),
            ("Try two numbers", 4),
            ("Catch the complaint", 4),
        ),
        level=3,
        name="Throwing and catching a value",
        family="Dart",
        language="dart",
        note=(
            "Dart can throw any object, even a plain String. `on String "
            "catch (e)` catches only that type and names it `e`; "
            "anything else would sail past. The first check passes and "
            "prints, the second throws, and the rest of the `try` block "
            "is skipped on the spot - nothing after the throw runs, so a "
            "third check placed there would never be reached. Put the "
            "two checks the other way round and the 'ok' never prints."
        ),
        code=(
            "void check(int x) {\n"
            "  if (x < 3) throw 'low $x';\n"
            "  print('ok $x');\n"
            "}\n"
            "void main() {\n"
            "  try {\n"
            "    check(5);\n"
            "    check(1);\n"
            "  } on String catch (e) {\n"
            "    print('caught $e');\n"
            "  }\n"
            "}"
        ),
        expect="ok 5\ncaught low 1",
    ),
    _m(
        id="magnet-dart3-endless-generator",
        plan=(
            ("A sequence that never ends on its own", 7),
            ("Read only as much as is needed", 4),
        ),
        level=4,
        name="An endless generator, read a little",
        family="Dart",
        language="dart",
        note=(
            "A `sync*` function runs only as far as the reader asks. The "
            "`while (true)` never finishes, but `take(4)` stops asking "
            "after four items, so it is safe. Each call to `evens()` "
            "starts a fresh run from zero. `skip(2).first` asks for "
            "three items and keeps the third: 0 and 2 are skipped, so "
            "4. The order of `yield n` and `n += 2` is the whole "
            "puzzle: add before yielding and the sequence starts at 2."
        ),
        code=(
            "Iterable<int> evens() sync* {\n"
            "  var n = 0;\n"
            "  while (true) {\n"
            "    yield n;\n"
            "    n += 2;\n"
            "  }\n"
            "}\n"
            "void main() {\n"
            "  print(evens().take(4).toList());\n"
            "  print(evens().skip(2).first);\n"
            "}"
        ),
        expect="[0, 2, 4, 6]\n4",
    ),
    _m(
        id="magnet-dart3-sort-two-keys",
        plan=(
            ("Tally the votes", 3),
            ("Order by votes, then by name", 4),
            ("Show the order and the top count", 3),
        ),
        level=4,
        name="Sorting by one thing, then another",
        family="Dart",
        language="dart",
        note=(
            "A comparator returns negative, zero or positive. Comparing "
            "`votes[b]` with `votes[a]` puts the biggest count first; "
            "when two names tie on votes the comparison is 0, and only "
            "then does it fall back to the names, so bo comes before "
            "cy. The `!` after each lookup says the key is certainly "
            "there. `names.first` is then the winner, and the last "
            "print looks its count up. `sort` works in place, so it has "
            "to be above both prints."
        ),
        code=(
            "void main() {\n"
            "  var votes = {'ann': 3, 'bo': 5, 'cy': 5, 'di': 1};\n"
            "  var names = votes.keys.toList();\n"
            "  names.sort((a, b) {\n"
            "    var byVotes = votes[b]!.compareTo(votes[a]!);\n"
            "    return byVotes != 0 ? byVotes : a.compareTo(b);\n"
            "  });\n"
            "  print(names);\n"
            "  print(votes[names.first]);\n"
            "}"
        ),
        expect="[bo, cy, ann, di]\n5",
    ),
)
