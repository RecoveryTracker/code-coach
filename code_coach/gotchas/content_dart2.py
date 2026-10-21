"""Gotchas, Dart (second deck): run by `dart run` on the VM (3.7 here); portability notes are in langs.py.

VM semantics: `int` is 64-bit and wraps. Nothing prints a hash code, a runtime type that is a private
implementation class (`_Map<dynamic, dynamic>`), or the order of anything that is not insertion-ordered, and
no `sort` is given elements that compare equal (Dart's sort is not stable). Async cards only use orderings
that the language guarantees (synchronous code, then microtasks, then the event queue).
"""

from __future__ import annotations

from .items import Item, make

q = make("dart")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: basics a beginner can get, with a real trap ──────────
    q("modulo-remainder-rounding", r'''
        void main() {
          print([4 / 2, -7 % 3, 7 % -3, (-7).remainder(3), 1e3, 3.0.toInt(),
                 2.5.round(), (-2.5).round(), 3.5.round()]);
        }
    ''', "[2.0, 2, 1, -1, 1000.0, 3, 3, -3, 4]", ["[2, -1, 1, -1, 1000, 3, 2, -2, 4]",
                                                  "[2.0, 2, -2, -1, 1000.0, 3, 2, -3, 4]",
                                                  "[2.0, -1, 1, 2, 1000.0, 3, 3, -3, 4]"],
      "% is never negative in Dart, remainder() keeps the dividend's sign, round() goes away from zero",
      """Dart's `%` always gives a result between 0 and the absolute value of the divisor, so -7 % 3 is 2 and
      7 % -3 is 1. `remainder` truncates like C and gives -1. `/` returns a double even for whole results, and
      `round` rounds halves away from zero."""),

    q("interpolation-forms", r'''
        void main() {
          var x = 'ab';
          print('$x.length ${x.length} \$x ${x * 2} ${1 + 2} ${x == 'ab'}');
        }
    ''', "ab.length 2 $x abab 3 true", ["2 2 ab abab 3 true", "ab.length 2 ab abab 3 true", "ab.length 2 $x ab2 3 true"],
      "$name takes only the identifier; use ${...} for member access or expressions",
      """In `'$x.length'` the interpolation ends at the name `x`, so the text `.length` is printed literally.
      Braces make it an expression. A backslash before the dollar sign prints the dollar sign itself."""),

    q("null-aware-operators", r'''
        void main() {
          String? s;
          int? n;
          n ??= 5;
          n ??= 9;
          print('${s?.length} ${s?.length ?? -1} $n ${s ?? "d"} '
              '${(s ?? "xy").length}');
        }
    ''', "null -1 5 d 2", ["0 -1 9 d 2", "null null 5 d 2", "null -1 9 null 0"],
      "?. gives null for a null receiver, ?? supplies a default, and ??= assigns only when null",
      """`s?.length` is null when `s` is null, and interpolating null prints the word null. `??` replaces the
      null with the right side. `n ??= 9` does nothing because `n` already holds 5."""),

    q("copies-and-lazy-views", r'''
        void main() {
          var a = [1, 2, 3];
          var b = [...a];
          var c = a.sublist(0, 2);
          var lazy = a.where((x) => x > 1);
          a.add(4);
          print('${b.length} ${c.length} ${lazy.length} ${a.take(2).toList()}');
        }
    ''', "3 2 3 [1, 2]", ["4 3 3 [1, 2]", "3 2 2 [1, 2]", "3 2 4 [1, 2]"],
      "Spread and sublist copy; where and map are lazy and see later changes",
      """`[...a]` and `sublist` build new lists, so adding 4 to `a` does not affect them. `where` returns a lazy
      view over `a` that is evaluated when it is used, after the add, so it finds 2, 3 and 4."""),

    q("final-const-lists", r'''
        void main() {
          final a = [1];
          a.add(2);
          const b = [1, 2];
          var c = [...b];
          c.add(3);
          String r;
          try { b.add(3); r = 'ok'; } catch (e) { r = e.runtimeType.toString(); }
          print('${a.length} ${c.length} $r');
        }
    ''', "2 3 UnsupportedError", ["1 3 ok", "2 3 ok", "2 2 UnsupportedError"],
      "final stops reassignment only; a const list cannot be changed at all",
      """The list in a `final` variable can still be modified, only the variable is fixed. A `const` list is
      immutable, so `add` throws an UnsupportedError. Spreading it into a new literal gives an ordinary,
      growable copy."""),

    q("cascade-returns-receiver", r'''
        void main() {
          var a = [3, 1, 2]..sort();
          var b = (StringBuffer()..write('x')..write(1)).toString();
          var c = [1]..add(2)..add(3);
          print('$a $b ${c.length} ${(<int>[]..add(5)).first}');
        }
    ''', "[1, 2, 3] x1 3 5", ["null x1 3 5", "[1, 2, 3] x1 1 5", "[3, 1, 2] x1 3 5"],
      "A cascade evaluates to the object it started with, whatever the methods return",
      """`sort()` returns nothing, but `[3, 1, 2]..sort()` is the list itself, now sorted. Each `..` call is made
      on the same receiver and its result discarded. Parentheses are needed to call a method on the cascaded
      expression as a whole."""),

    q("loop-closure-capture", r'''
        void main() {
          var fs = <int Function()>[];
          for (var i = 0; i < 3; i++) { fs.add(() => i); }
          var gs = <int Function()>[];
          var j = 0;
          while (j < 3) { gs.add(() => j); j++; }
          print('${fs.map((f) => f()).toList()} ${gs.map((f) => f()).toList()}');
        }
    ''', "[0, 1, 2] [3, 3, 3]", ["[3, 3, 3] [3, 3, 3]", "[0, 1, 2] [0, 1, 2]", "[1, 2, 3] [3, 3, 3]"],
      "A for loop gives each iteration its own variable; a variable declared outside is shared",
      """The loop variable of a `for` statement is copied for every iteration, so the closures remember 0, 1
      and 2. The `while` loop uses one `j` declared outside, and all three closures read it after it has
      reached 3."""),

    q("string-length-code-units", r'''
        void main() {
          var s = 'a\u{1F600}b';
          print('${s.length} ${s.runes.length} ${s.codeUnitAt(1)} '
              '${s.runes.elementAt(1)} ${s.substring(1, 3).length}');
        }
    ''', "4 3 55357 128512 2", ["3 3 128512 128512 1", "4 4 55357 55357 2", "4 3 128512 128512 1"],
      "length counts UTF-16 code units, so a character outside the basic plane counts as 2",
      """Dart strings are sequences of UTF-16 code units. The emoji is stored as the surrogate pair 55357 and
      56832, so `length` is 4, while `runes` yields code points and counts 3. Slicing between the two halves
      of a pair would produce an invalid string."""),

    q("optional-and-named-parameters", r'''
        String f(int a, [int b = 2, int? c]) => '$a $b $c';
        String g(int a, {int b = 2, required int c}) => '$a $b $c';
        void main() {
          print('${f(1)}|${f(1, 5, 6)}|${g(1, c: 3)}|${g(c: 4, b: 9, 1)}');
        }
    ''', "1 2 null|1 5 6|1 2 3|1 9 4", ["1 2 0|1 5 6|1 2 3|1 9 4", "1 2 null|1 5 6|1 3 2|1 9 4",
                                        "1 2 null|1 5 6|1 2 3|9 4 1"],
      "Optional positionals fill in order, named ones go by name and can appear anywhere in the call",
      """The unspecified optional `c` has no default, so it is null. Named arguments are matched by their
      names and may be written before the positional ones. Only a `required` named parameter must be given."""),

    q("collection-if-for-spread", r'''
        void main() {
          var a = [1, 2];
          List<int>? n;
          var b = [0, ...a, if (a.length > 1) 9, for (var x in a) x * 10];
          var c = [...?n, 7];
          print('$b $c');
        }
    ''', "[0, 1, 2, 9, 10, 20] [7]", ["[0, [1, 2], 9, 10, 20] [7]", "[0, 1, 2, 9, 1, 2] [null, 7]",
                                      "[0, 1, 2, 9, 10, 20] [7, null]"],
      "Collection literals can hold spreads, if and for; ...? skips a null collection",
      """The `...` spread inserts the elements of a list rather than the list itself, `if` adds an element only
      when the condition holds, and `for` generates one element per iteration. `...?` spreads nothing when the
      value is null instead of failing."""),

    q("integer-wraps-at-64-bits", r'''
        void main() {
          var m = 9223372036854775807;
          print('${m + 1} ${1 << 63} ${1 << 64} ${-1 >>> 1} ${m * 2} ${-8 >> 1}');
        }
    ''', "-9223372036854775808 -9223372036854775808 0 9223372036854775807 -2 -4",
      ["9223372036854775808 9223372036854775808 0 9223372036854775807 -2 -4",
       "-9223372036854775808 -9223372036854775808 1 -1 -2 -4",
       "-9223372036854775808 -9223372036854775808 0 9223372036854775807 -2 4"],
      "On the VM int is a 64-bit two's complement number that wraps around silently",
      """Adding 1 to the largest 64-bit value wraps to the smallest, and doubling it gives -2. Shifting by 64
      or more gives 0. `>>` keeps the sign bit, but `>>>` shifts in zeros, so -1 >>> 1 is the largest int."""),

    q("double-to-string", r'''
        void main() {
          print([0.1 + 0.2, 1e21, 1e-7, 100.0, 1 / 3, 2.50, 1e20, 1234567890.0 * 10]
              .join(' '));
        }
    ''', "0.30000000000000004 1e+21 1e-7 100.0 0.3333333333333333 2.5 100000000000000000000.0 12345678900.0",
      ["0.3 1e21 1e-7 100 0.3333333333333333 2.5 1e20 12345678900", "0.30000000000000004 1e21 1e-7 100.0 0.33333333 2.5 1e+20 12345678900.0",
       "0.30000000000000004 1e+21 0.0000001 100.0 0.3333333333333333 2.50 100000000000000000000.0 12345678900.0"],
      "Doubles print with the shortest round-trip digits, keep a .0, and switch to exponents at 1e21",
      """`toString` gives the shortest digit string that reads back as the same double, so the famous sum shows
      all its digits. A whole double keeps its `.0`. Exponent notation starts at 1e21 for large values and below
      about 1e-6 for small ones."""),

    q("fixed-and-precision-formats", r'''
        void main() {
          print([2.5.toStringAsFixed(0), 3.5.toStringAsFixed(0),
                 0.125.toStringAsFixed(2), 1.005.toStringAsFixed(2),
                 1234.5678.toStringAsFixed(1),
                 12345.6789.toStringAsPrecision(3), 255.toRadixString(2),
                 (-5).toRadixString(2), 5.toString().padLeft(3, '0')].join(' '));
        }
    ''', "3 4 0.13 1.00 1234.6 1.23e+4 11111111 -101 005",
      ["2 4 0.12 1.01 1234.6 12300 11111111 -101 005", "3 4 0.13 1.01 1234.6 1.23e+4 11111111 -101 005",
       "3 4 0.13 1.00 1234.6 12300.0 11111111 11111011 005"],
      "toStringAsFixed rounds half up on the exact binary value, so 1.005 gives 1.00",
      """Halves round away from zero when the binary value is exactly a half (2.5, 3.5, 0.125). But 1.005 is
      stored slightly below 1.005, so it rounds down to 1.00. `toStringAsPrecision` switches to exponent form
      when the digits do not fit, and `toRadixString` puts the sign in front of the digits."""),

    q("operator-equality-types", r'''
        void main() {
          print([1 == 1.0, identical(1, 1.0), 0.0 == -0.0, double.nan == double.nan,
                 'a' == 'a', {1, 2} == {1, 2}, (1, 2) == (1, 2)].join(' '));
        }
    ''', "true false true false true false true", ["true true true false true true true", "false false true false true false true",
                                                   "true false false true true false true"],
      "== on numbers compares values, identical() distinguishes int from double; Sets have no ==",
      """`1 == 1.0` is true because `==` compares numerically, but on the VM the two are different objects, so
      `identical` is false. NaN is not equal to itself. Records compare by their fields, while two sets with
      the same elements are only equal if they are the same object."""),

    q("records-and-destructuring", r'''
        void main() {
          var p = (1, 'a', x: 2.0);
          var (a, b) = (1, 2);
          (a, b) = (b, a);
          print('${p.$1} ${p.x} $p $a$b');
        }
    ''', "1 2.0 (1, a, x: 2.0) 21", ["a 2.0 (1, a, x: 2.0) 12", "1 2.0 (1, 'a', x: 2.0) 21", "1 2 (1, a, x: 2.0) 21"],
      "Record fields are $1, $2... by position and names for named ones; a pattern assignment swaps",
      """Positional fields of a record are reached as `$1`, `$2` and so on, and named fields by their name. The
      right side of `(a, b) = (b, a)` is built completely before the assignment, so the values swap
      without a temporary."""),

    # ── Medium: classes, patterns, lazy evaluation, async ordering ─────────
    q("iterable-printing-forms", r'''
        void main() {
          var l = [1, 2];
          print('${l.map((x) => x + 1)} ${l.where((x) => x > 5)} ${l.toList()} '
              '${l.reversed} ${['a']} ${{'k': 'v'}} ${<String>{'x'}}');
        }
    ''', "(2, 3) () [1, 2] (2, 1) [a] {k: v} {x}", ["[2, 3] [] [1, 2] [2, 1] [a] {k: v} {x}",
                                                   "(2, 3) () [1, 2] (2, 1) [\"a\"] {\"k\": \"v\"} {\"x\"}",
                                                   "[2, 3] () [1, 2] (2, 1) [a] {k: v} [x]"],
      "A lazy Iterable prints with parentheses, a List with brackets, and strings print without quotes",
      """`map`, `where` and `reversed` return lazy iterables, whose `toString` uses parentheses; only a real
      List (or `toList()`) prints with square brackets, and a Set or Map with braces. Collections show their
      string elements without quotes, unlike JSON."""),

    q("switch-expression-patterns", r'''
        String f(Object o) => switch (o) {
              int n when n > 5 => 'big',
              int() => 'int',
              String s => 's$s',
              [1, ...] => 'list1',
              _ => 'other',
            };
        void main() {
          print([f(7), f(3), f('x'), f([1, 2]), f(2.0), f([2])].join(' '));
        }
    ''', "big int sx list1 other other", ["big int sx other other other", "int int sx list1 other other",
                                          "big int x list1 other other"],
      "Cases are tried in order, `when` adds a condition, and a list pattern matches the head",
      """Dart 3 `switch` expressions use patterns: `int n when n > 5` only matches big integers, so 3 falls to
      the plain `int()` case. `[1, ...]` matches any list whose first element is 1. Doubles and lists that
      start with something else reach the wildcard."""),

    q("late-initialiser-runs-on-use", r'''
        void main() {
          var log = <String>[];
          late int a = (() { log.add('init'); return 5; })();
          log.add('before');
          var s = a + a;
          log.add('sum $s');
          print(log);
        }
    ''', "[before, init, sum 10]", ["[init, before, sum 10]", "[before, init, init, sum 10]", "[init, before, init, sum 10]"],
      "A late variable's initialiser runs on the first read, once",
      """Unlike an ordinary local, a `late` variable with an initialiser is lazy: nothing happens at the
      declaration. The first read of `a` runs the initialiser, so `init` is logged after `before`, and the
      value is then cached for the second read."""),

    q("setter-through-compound-assignment", r'''
        class Box {
          int _v = 0;
          int get v => _v;
          set v(int x) => _v = x.clamp(0, 10);
        }
        void main() {
          var b = Box();
          b.v = 50;
          b.v += 3;
          print('${b.v} ${b._v}');
        }
    ''', "10 10", ["53 53", "10 13", "13 10"],
      "b.v += 3 reads through the getter, adds, and writes through the setter",
      """The first assignment stores `50.clamp(0, 10)`, which is 10. The compound assignment `b.v += 3` reads
      10, adds 3 and passes 13 to the setter, which clamps it to 10 again."""),

    q("constructor-and-initialiser-order", r'''
        var log = <String>[];
        class A {
          A() { log.add('A'); }
        }
        class B extends A {
          final int x = (() { log.add('field'); return 1; })();
          B() : super() { log.add('B'); }
        }
        void main() {
          B();
          print(log);
        }
    ''', "[field, A, B]", ["[A, field, B]", "[A, B, field]", "[B, A, field]"],
      "Field initialisers run first, then the superclass constructor, then the constructor body",
      """In Dart the instance fields with initialisers are set before the super constructor is called, unlike
      Java. The order is: fields of this class, then `A()`, then the body of `B()`. A subclass's body always
      runs last."""),

    q("factory-returns-cached-object", r'''
        class Tag {
          static final _cache = <String, Tag>{};
          final String name;
          Tag._(this.name);
          factory Tag(String name) => _cache.putIfAbsent(name, () => Tag._(name));
        }
        void main() {
          print('${identical(Tag('a'), Tag('a'))} ${identical(Tag('a'), Tag('b'))} '
              '${Tag._cache.length}');
        }
    ''', "true false 2", ["false false 2", "true false 3", "true true 1"],
      "A factory constructor may return an existing instance instead of making a new one",
      """Unlike a normal constructor, a `factory` runs ordinary code and can return a cached object. The two
      calls with the name "a" return the same instance. The cache ends up with two entries."""),

    q("async-ordering-sync-micro-event", r'''
        import 'dart:async';
        Future<void> main() async {
          var log = <String>[];
          Future(() => log.add('event'));
          scheduleMicrotask(() => log.add('micro'));
          Future.value(1).then((_) => log.add('then'));
          log.add('sync');
          await Future(() {});
          print(log);
        }
    ''', "[sync, micro, then, event]", ["[sync, event, micro, then]", "[event, sync, micro, then]", "[sync, then, micro, event]"],
      "Synchronous code first, then microtasks in order, then the event queue",
      """Everything the program runs immediately goes first: only `sync` is logged. Then the microtask queue is
      emptied in the order things were scheduled, so `micro` and `then` run before any timer-style event.
      `Future(() => ...)` goes on the event queue and runs after both."""),

    q("async-function-runs-until-await", r'''
        var log = <String>[];
        Future<void> a() async {
          log.add('a1');
          await null;
          log.add('a2');
        }
        Future<void> main() async {
          a();
          log.add('main');
          await Future.delayed(Duration.zero);
          print(log);
        }
    ''', "[a1, main, a2]", ["[main, a1, a2]", "[a1, a2, main]", "[main, a2, a1]"],
      "An async function runs synchronously until its first await, then yields to the caller",
      """Calling `a()` executes its body immediately up to the `await`, so `a1` is logged before `main`
      continues. Even `await null` gives up control, and the rest of the function is resumed as a microtask,
      after the caller has logged `main`."""),

    q("future-chain-recovery", r'''
        Future<void> main() async {
          var log = <String>[];
          var r = await Future.value(1)
              .then((v) => v + 1)
              .then<int>((v) => throw 'boom')
              .catchError((e) => -1)
              .whenComplete(() => log.add('done'));
          print('$r $log');
        }
    ''', "-1 [done]", ["boom [done]", "-1 []", "2 [done]"],
      "catchError turns an error into a value, and whenComplete passes the value along",
      """The second `then` throws, so the error skips ahead to `catchError`, whose return value -1 becomes the
      chain's result. `whenComplete` runs its callback either way and does not change the value."""),

    q("stream-await-for", r'''
        Future<void> main() async {
          var l = await Stream.fromIterable([1, 2, 3])
              .map((x) => x * 2)
              .where((x) => x > 2)
              .toList();
          var sum = 0;
          await for (var v in Stream.fromIterable([1, 2, 3])) { sum += v; }
          print('$l $sum ${await Stream.fromIterable([5, 6]).first}');
        }
    ''', "[4, 6] 6 5", ["[2, 4, 6] 6 5", "[4, 6] 6 11", "[4, 6] 3 5"],
      "Stream operators like map and where are lazy until a terminal operation such as toList",
      """Nothing flows until the stream is listened to. `toList` collects the doubled values that pass the test,
      4 and 6. `await for` consumes one stream sequentially, adding 1, 2 and 3, and `first` takes only the first
      element."""),

    q("sync-star-restarts", r'''
        void main() {
          var log = <String>[];
          Iterable<int> g() sync* {
            log.add('s');
            yield 1;
            log.add('m');
            yield 2;
            log.add('e');
          }
          var it = g();
          log.add('made');
          var f = it.first;
          var l = it.toList();
          print('$log $f $l');
        }
    ''', "[made, s, s, m, e] 1 [1, 2]", ["[s, made, s, m, e] 1 [1, 2]", "[made, s, m, e] 1 [1, 2]", "[made, s, m, e, s] 1 [1, 2]"],
      "A sync* generator is lazy and starts over for every iteration",
      """Calling `g()` runs none of its body. `first` starts an iteration, which stops at the first `yield`
      after logging `s`. `toList` iterates the iterable again from the beginning, so `s` is logged a second time
      before `m` and `e`."""),

    q("map-operations", r'''
        void main() {
          var m = {'a': 1};
          m['b'] ??= 2;
          m.putIfAbsent('a', () => 9);
          var v = m['z'];
          print('${m.length} $v ${m.containsKey('z')} ${m['a']! + 1} '
              '${m.entries.map((e) => '${e.key}${e.value}').join()}');
        }
    ''', "2 null false 2 a1b2", ["2 0 false 2 a1b2", "3 null true 2 a1b2", "2 null false 10 a9b2"],
      "Reading a missing key gives null without adding it; putIfAbsent keeps existing values",
      """`m['b'] ??= 2` stores 2 because the key is absent, and `putIfAbsent` leaves the existing `a` alone.
      Reading `m['z']` returns null and does not create the key. Iteration follows insertion order."""),

    q("concurrent-modification", r'''
        void main() {
          var l = [1, 2, 3];
          String r;
          try {
            for (var x in l) { if (x == 1) l.add(9); }
            r = 'ok';
          } catch (e) {
            r = e.runtimeType.toString();
          }
          print('$r ${l.length}');
        }
    ''', "ConcurrentModificationError 4", ["ok 4", "ConcurrentModificationError 3", "RangeError 4"],
      "Adding to a list while a for-in loop is walking it throws",
      """The list notices that it changed after the iterator was created and throws a
      ConcurrentModificationError on the next step. The element was already added by then, so the length
      is 4."""),

    q("list-method-results-and-views", r'''
        void main() {
          var l = [3, 1, 2, 1];
          var a = l.remove(1);
          var b = l.remove(9);
          var c = l.removeAt(0);
          var d = l.indexOf(9);
          var r = l.reversed;
          l.add(7);
          var e = l.firstWhere((x) => x > 8, orElse: () => -1);
          print('$a $b $c $d ${r.toList()} $l $e');
        }
    ''', "true false 3 -1 [7, 1, 2] [2, 1, 7] -1", ["true false 3 -1 [1, 2] [2, 1, 7] -1",
                                                   "1 null 3 -1 [7, 1, 2] [2, 1, 7] -1",
                                                   "true false 3 -1 [7, 1, 2] [2, 1, 7] null"],
      "remove returns a bool and removes only the first match; reversed is a view of the live list",
      """`remove(1)` deletes the first 1 only and returns true; `remove(9)` returns false. `removeAt` returns the
      removed element. `reversed` is not a copy, so converting it after `add(7)` includes the new element."""),

    q("split-edge-cases", r'''
        void main() {
          print(['a,b,,c,'.split(',').length, ''.split(',').length,
                 'abc'.split('').length, ' a  b '.split(' ').length, 'ab' * 3,
                 'abc'.padLeft(5, '*'), 'abc'.compareTo('abd'),
                 'Hello'.replaceFirst('l', 'L')].join(' '));
        }
    ''', "5 1 3 5 ababab **abc -1 HeLlo", ["4 0 3 2 ababab **abc -1 HeLlo", "5 1 3 2 ababab **abc 1 HeLlo", "4 1 3 5 ababab abc** -1 HeLLo"],
      "split keeps empty pieces, including a trailing one, and splitting \"\" gives one empty string",
      """Dart's `split` never drops empty strings: a trailing separator leaves an empty last piece, and
      consecutive separators leave empty pieces in between. Splitting an empty string yields a list with a single
      empty string, and splitting on the empty pattern gives each character."""),

    q("number-parsing-forms", r'''
        void main() {
          print([int.parse(' 12 '), int.tryParse('12.5'), int.tryParse('0x1F'),
                 int.parse('ff', radix: 16), double.parse('1e3'), num.parse('3'),
                 num.parse('3.0'), int.tryParse('1_000'),
                 double.tryParse('.5')].join(' '));
        }
    ''', "12 null 31 255 1000.0 3 3.0 null 0.5", ["12 12 31 255 1000.0 3 3.0 1000 0.5", "12 null 0 255 1000 3 3 null 0.5",
                                                 "12 null 31 255 1000.0 3 3 null null"],
      "tryParse returns null on bad input; int.parse accepts hex with 0x and trims whitespace",
      """`int.tryParse('12.5')` fails because a decimal point is not allowed in an int, so it is null. Hex needs
      the `0x` prefix when no radix is given. `num.parse` returns an int or a double depending on the text, so
      '3.0' stays a double."""),

    q("runtime-types-of-numbers", r'''
        void main() {
          num n = 5;
          print([n is int, 5.0 is int, (7 / 7).runtimeType,
                 7.0.toInt().runtimeType, (n + 0.5).runtimeType, n.runtimeType,
                 (n ~/ 2).runtimeType].join(' '));
        }
    ''', "true false double int double int int", ["true true double int double int int", "true false int int double int int",
                                                   "false false double int double num int"],
      "On the VM an int and a double are different types; `/` always yields a double",
      """`5.0 is int` is false on the VM (in JavaScript it would be true), and dividing two ints with `/` gives a
      double. Adding an int and a double gives a double, `toInt` and `~/` give ints, and a `num` variable
      reports the type of the actual value."""),

    q("lazy-map-reruns-callback", r'''
        void main() {
          var calls = 0;
          var it = [1, 2, 3].map((x) { calls++; return x * 2; });
          var a = calls;
          it.toList();
          it.toList();
          print('$a $calls ${it.first}');
        }
    ''', "0 6 2", ["3 3 2", "0 3 2", "0 6 6"],
      "map returns a lazy iterable that calls the function again on every pass",
      """Creating the mapped iterable runs nothing, so `calls` is still 0. Each `toList` re-runs the function for
      all three elements, which makes 6. The final `first` only needs one element, so its call is made after the
      count was read."""),

    q("sort-orders", r'''
        void main() {
          var w = ['pear', 'Fig', 'apple', 'Banana'];
          var a = [...w]..sort();
          var b = [...w]
            ..sort((x, y) => x.toLowerCase().compareTo(y.toLowerCase()));
          var c = [...w]..sort((x, y) => x.length.compareTo(y.length));
          print('$a $b $c');
        }
    ''', "[Banana, Fig, apple, pear] [apple, Banana, Fig, pear] [Fig, pear, apple, Banana]",
      ["[apple, Banana, Fig, pear] [apple, Banana, Fig, pear] [Fig, pear, apple, Banana]",
       "[Banana, Fig, apple, pear] [apple, Banana, Fig, pear] [Banana, apple, pear, Fig]",
       "[Banana, Fig, apple, pear] [Banana, Fig, apple, pear] [Fig, pear, apple, Banana]"],
      "Strings sort by code unit, so every capital letter comes before every lowercase one",
      """The default order compares UTF-16 code units, which puts "Banana" and "Fig" ahead of "apple". A custom
      comparator can fold the case first or sort by length instead. Dart's `sort` is not guaranteed to be stable,
      so these examples avoid ties."""),

    # ── Hard but legal: precedence, mixins, generics, tear-offs ────────────
    q("operator-precedence", r'''
        void main() {
          print([2 + 3 * 4 ~/ 5 % 3, -2 * -3 - 1, 7 ~/ 2 * 2, 1 << 2 + 1,
                 6 & 3 == 2, 5 > 3 == true, true || false && false,
                 null ?? 1 + 1].join(' '));
        }
    ''', "4 5 6 8 true true true 2", ["4 5 6 8 false true true 2", "1 5 7 8 true true true 2", "4 5 6 5 true true true 2"],
      "In Dart & binds tighter than ==, shifts are below +, and * ~/ % share one level",
      """Unlike C, bitwise AND has a higher precedence than equality, so `6 & 3 == 2` is `(6 & 3) == 2`, true.
      Multiplication, `~/` and `%` are on the same level and group left to right: 3 * 4 ~/ 5 % 3 is 2. Addition
      binds tighter than a shift, so `1 << 2 + 1` is `1 << 3`."""),

    q("string-escapes-and-raw", r'''
        void main() {
          print([r'a\nb'.length, 'a\nb'.length, '\$x'.length, 'it\'s'.length,
                 "it's".length, '\x41', '\t'.length].join(' '));
        }
    ''', "4 3 2 4 4 A 1", ["3 3 2 4 4 A 1", "4 3 2 5 4 A 1", "4 3 3 4 4 x41 1"],
      "A raw string keeps the backslash as a character; \\$ prints a dollar sign",
      r"""In an `r'...'` string no escapes are processed, so `\n` is two characters. A normal string turns `\n`
      into one newline character and `\$` into a single dollar sign. Either quote style can hold the other
      quote without an escape."""),

    q("enhanced-enum", r'''
        enum Level {
          low(1), mid(5), high(9);
          final int w;
          const Level(this.w);
          Level get next => values[(index + 1) % values.length];
        }
        void main() {
          print('${Level.high.next.name} ${Level.low.index} '
              '${Level.values.where((l) => l.w > 2).length} ${Level.mid}');
        }
    ''', "low 0 2 Level.mid", ["low 1 2 mid", "low 0 2 mid", "low 0 3 Level.mid"],
      "An enum value prints as Enum.name; .name gives just the name and .index the position",
      """Enums can have fields, constructors and methods. `values` lists the cases in order, so after `high`
      comes `low` again with index 0. Interpolating the enum value itself gives `Level.mid`, with the type
      name in front."""),

    q("class-method-beats-extension", r'''
        class A {
          String hi() => 'class';
        }
        extension E on A {
          String hi() => 'ext';
          String bye() => 'ext-bye';
        }
        void main() {
          print('${A().hi()} ${A().bye()}');
        }
    ''', "class ext-bye", ["ext ext-bye", "class class", "ext class"],
      "An extension method never overrides a method the class already has",
      """Member lookup finds the instance method first, so `A().hi()` calls the class's own version and the
      extension's `hi` is unreachable that way. A name the class does not have, like `bye`, is resolved to the
      extension."""),

    q("mixin-application-order", r'''
        class A { String m() => 'A'; }
        mixin M on A { String m() => 'M${super.m()}'; }
        mixin N on A { String m() => 'N${super.m()}'; }
        class B extends A with M, N {}
        class C extends A with N, M {}
        void main() {
          print('${B().m()} ${C().m()}');
        }
    ''', "NMA MNA", ["MNA NMA", "NMA NMA", "MA NA"],
      "The last mixin listed is applied last, so it is called first and its super reaches the one before",
      """`with M, N` builds the chain A, then M on top of it, then N on top of that. A call starts at the top
      (N), whose `super.m()` goes to M, and then to A: NMA. Swapping the order in `C` swaps the result."""),

    q("tear-off-versus-closure", r'''
        void main() {
          var s = 'x';
          var f = s.toUpperCase;
          s = 'y';
          var g = () => s.toUpperCase();
          s = 'z';
          print('${f()} ${g()}');
        }
    ''', "X Z", ["Y Z", "X X", "Y Y"],
      "A tear-off binds the object at that moment; a closure reads the variable when it is called",
      """`s.toUpperCase` without parentheses takes the current string object, "x", together with the method, so
      later reassigning `s` does not affect it. The closure instead refers to the variable `s`, and sees "z"
      when it runs."""),

    q("math-library-types", r'''
        import 'dart:math';
        void main() {
          print([pow(2, 10), pow(2, -1), pow(2.0, 3), sqrt(16), max(1, 2.5),
                 min(1, 2.5), pow(10, 2).runtimeType].join(' '));
        }
    ''', "1024 0.5 8.0 4.0 2.5 1 int", ["1024.0 0.5 8 4 2.5 1 double", "1024 0.5 8.0 4.0 2.5 1.0 int", "1024 0 8.0 4.0 2.5 1 int"],
      "pow keeps ints for non-negative int exponents; sqrt is always a double; min keeps the winner's type",
      """`pow(2, 10)` is the integer 1024 because both arguments are integers and the exponent is not negative,
      but `pow(2, -1)` has to be 0.5. `sqrt(16)` is the double 4.0. `min(1, 2.5)` returns the int 1 itself,
      not a converted double."""),

    q("list-filled-shares-elements", r'''
        void main() {
          var a = List.filled(2, <int>[]);
          a[0].add(1);
          var b = List.generate(2, (_) => <int>[]);
          b[0].add(1);
          print('$a $b');
        }
    ''', "[[1], [1]] [[1], []]", ["[[1], []] [[1], []]", "[[1], [1]] [[1], [1]]", "[[1], []] [[1], [1]]"],
      "List.filled repeats one object; List.generate calls the function for every element",
      """The value passed to `List.filled` is evaluated once, so both slots hold the same inner list and a push
      shows up twice. `List.generate` runs its callback per index and creates separate lists."""),

    q("empty-braces-are-a-map", r'''
        void main() {
          var e = {};
          var s = <int>{};
          var t = {1, 2};
          print('${e is Map} ${s is Set} ${t.add(2)} ${t.add(3)} ${t.length} '
              '${{1, 2, 3}.difference({2}).toList()} ${[1, 1, 2].toSet().length}');
        }
    ''', "true true false true 3 [1, 3] 2", ["false true false true 3 [1, 3] 2", "true true true true 4 [1, 3] 2",
                                             "true true false true 3 [1, 3] 3"],
      "{} alone is an empty Map; a Set needs a type argument or at least one element",
      """Without a type argument or elements, the empty braces are read as a Map literal. `Set.add` returns false
      when the element was already there, which is why the second `add(2)` reports false and the length is
      3 after adding 3."""),

    q("division-by-zero-forms", r'''
        void main() {
          var z = 0;
          String r;
          try { r = '${1 ~/ z}'; } catch (e) { r = 'err'; }
          print('${1 / 0} ${-1 / 0} ${0 / 0} ${(1 / 0).isInfinite} '
              '${1.5 ~/ 0.5} $r');
        }
    ''', "Infinity -Infinity NaN true 3 err", ["err err err true 3 err", "Infinity -Infinity 0 true 3 err",
                                              "Infinity -Infinity NaN true 3 Infinity"],
      "/ follows floating-point rules and gives Infinity or NaN, but integer ~/ by zero throws",
      """The `/` operator always works on doubles, so dividing by zero gives Infinity, -Infinity or NaN and
      never throws. The truncating division `~/` of integers has no such value and throws instead. A double
      operand like `1.5 ~/ 0.5` is fine and returns the int 3."""),

    q("default-object-to-string", r'''
        class P {}
        class Q {
          @override
          String toString() => 'Q!';
        }
        void main() {
          print('${P()} ${[Q(), Q()]} ${Q()} ${P().runtimeType}');
        }
    ''', "Instance of 'P' [Q!, Q!] Q! P", ["P [Q!, Q!] Q! P", "Instance of 'P' [Q, Q] Q! P", "Instance of 'P' [Q!, Q!] Instance of 'Q' P"],
      "The default toString is \"Instance of 'ClassName'\"; collections use each element's toString",
      """Without an override, an object prints as `Instance of 'P'`. A list calls `toString` on each of its
      elements, so the overridden version shows up inside the brackets. `runtimeType` prints the class
      name."""),

    q("labeled-continue-and-break", r'''
        void main() {
          var out = <String>[];
          outer:
          for (var i = 0; i < 3; i++) {
            for (var j = 0; j < 3; j++) {
              if (j == 2) continue outer;
              if (i == 2) break outer;
              out.add('$i$j');
            }
          }
          print(out.join(','));
        }
    ''', "00,01,10,11", ["00,01,10,11,20,21", "00,01,02,10,11,12", "00,10"],
      "continue outer skips to the next iteration of the labelled loop, break outer ends it",
      """For i = 0 and i = 1 the inner loop adds two pairs and then `continue outer` moves to the next i at j =
      2. When i is 2, the first inner iteration reaches `break outer` before adding anything, which ends both
      loops."""),

    q("covariant-list-write-fails", r'''
        void main() {
          List<int> ints = [1];
          List<Object> objs = ints;
          String r;
          try {
            objs.add('s');
            r = 'ok';
          } catch (e) {
            r = e is TypeError ? 'TypeError' : 'other';
          }
          print('$r ${ints.length}');
        }
    ''', "TypeError 1", ["ok 2", "ok 1", "TypeError 2"],
      "A List<int> can be used as List<Object>, but adding a non-int is checked at run time",
      """Dart generics are covariant, so the assignment compiles. The list itself is still a `List<int>`, and
      `add('s')` fails the run-time type check with a TypeError before changing anything, leaving the length
      at 1."""),

    q("reified-generic-types", r'''
        void main() {
          var x = <int>[1];
          var d = <dynamic>[1];
          print([x is List<int>, x is List<num>, x is List<String>, d is List<int>,
                 List<int>.from(d) is List<int>].join(' '));
        }
    ''', "true true false false true", ["true true true false true", "true false false true true", "true true false true true"],
      "Generic type arguments exist at run time, so a List<dynamic> is not a List<int>",
      """Dart keeps the type arguments of an object, so `is` can tell `List<int>` from `List<String>`. A list
      created as `<dynamic>[1]` is a `List<dynamic>` whatever it holds. `List.from` builds a new list with the
      requested element type."""),

    q("duration-parts", r'''
        void main() {
          var d = Duration(minutes: 90);
          print('${d.inHours} ${d.inMinutes % 60} $d ${d.inSeconds / 60} '
              '${d + Duration(seconds: 30)}');
        }
    ''', "1 30 1:30:00.000000 90.0 1:30:30.000000", ["1 90 1:30:00 90.0 1:30:30", "2 30 1:30:00.000000 90 1:30:30.000000",
                                                    "1 30 01:30:00 90.0 01:30:30"],
      "inHours and inMinutes truncate and are totals, not remainders",
      """`inHours` is the whole number of hours, 1, while `inMinutes` is the total of 90, which is why the
      remainder is taken. A Duration prints as hours:minutes:seconds.microseconds with a fixed six-digit
      fraction. `/` on the integer seconds gives a double."""),

    q("regexp-groups", r'''
        void main() {
          var m = RegExp(r'(\d)(\d)?').firstMatch('1')!;
          var n = RegExp(r'\d+').allMatches('a1b22c333').length;
          var s = 'a1b22'.replaceAll(RegExp(r'\d'), '#');
          print('${m.group(0)} ${m.group(1)} ${m.group(2)} ${m.groupCount} '
              '$n $s ${RegExp('a.c').hasMatch('abc')}');
        }
    ''', "1 1 null 2 3 a#b## true", ["1 1  2 3 a#b## true", "1 1 null 2 3 a#b# true", "1 1 null 1 3 a#b## true"],
      "An optional group that did not take part gives null, but groupCount still counts it",
      """The pattern has two groups, so `groupCount` is 2, but the second one matched nothing in the text "1" and
      returns null. `allMatches` finds the three runs of digits, and `replaceAll` replaces every single digit."""),
)
