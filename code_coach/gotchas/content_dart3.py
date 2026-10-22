"""Gotchas, Dart (third deck): run by the Dart VM (3.x on this machine); portability notes are in langs.py.

New angles on the first two decks: const canonicalisation, Iterable/List/Map/Set method corners, patterns and
switches, extensions and operators, exceptions, the async queues, and dart:convert and DateTime (always a fixed
UTC date, never now()). Every card prints one line.
"""

from __future__ import annotations

from .items import Item, make

q = make("dart")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking ──────────────────────────────────────────────────────
    q("const-instances-are-canonical", r'''
        class P {
          final int x;
          const P(this.x);
        }

        void main() {
          var a = const P(1);
          var b = const P(1);
          var c = P(1);
          print([identical(a, b), identical(a, c), a == b, a == c,
                 identical(const [1], const [1]), identical([1], [1])].join(' '));
        }
    ''', "true false true false true false", ["true true true true true false",
                                               "false false false false true false",
                                               "true false true false false false"],
      "Only a const expression is canonical; the same constructor without const makes a new object",
      """Two `const P(1)` expressions give the very same object, so they are identical and equal. `P(1)` without
      `const` builds a fresh instance, and since the class does not override `==`, equality is identity: false. The
      same split holds for list literals: `const [1]` twice is one object, `[1]` twice is two."""),

    q("switch-statement-has-no-fallthrough", r'''
        String s(int n) {
          var r = '';
          switch (n) {
            case 1: r += 'a';
            case 2: r += 'b';
            case 3:
            case 4: r += 'c';
            default: r += 'd';
          }
          return r;
        }
        void main() {
          print([for (var i = 1; i <= 5; i++) s(i)].join(' '));
        }
    ''', "a b c c d", ["abcd bcd cd cd d", "a b cd c d", "abcd b c c d"],
      "A case with a body ends there, with no break needed; only an empty case falls into the next",
      """Since Dart 3 a `switch` statement does not run on into the next case, and `break` is optional. Only a case
      with no statements, like `case 3:`, shares the body of the case after it, so 3 and 4 both give "c". This is
      unlike C, where 1 would print "abcd"."""),

    q("round-floor-ceil-negatives", r'''
        void main() {
          print([(-3.7).truncate(), (-3.7).floor(), (-3.7).ceil(), (-3.2).round(),
                 (-0.4).round(), 0.5.round(), (-0.5).round(), (-7 / 2).floor(),
                 -7 ~/ 2].join(' '));
        }
    ''', "-3 -4 -3 -3 0 1 -1 -4 -3", ["-3 -3 -4 -3 0 1 0 -3 -3", "-4 -4 -3 -3 0 1 -1 -4 -4",
                                      "-3 -4 -3 -3 -1 1 -1 -3 -4"],
      "truncate goes toward zero, floor down, ceil up, and round sends halves away from zero",
      """`-3.7.truncate()` drops the fraction: -3. `floor` goes down to -4 and `ceil` up to -3. `round` goes to the
      nearest integer, and exact halves move away from zero, so 0.5 becomes 1 and -0.5 becomes -1. `~/` truncates
      its quotient, so `-7 ~/ 2` is -3, whereas flooring -3.5 gives -4."""),

    q("int-helper-methods", r'''
        void main() {
          print([10.gcd(4), 10.sign, (-5).abs(), (-5).sign, 255.bitLength,
                 7.isOdd, 5.clamp(1, 3), (-5).remainder(3), -5 % 3,
                 (-5).abs().isEven].join(' '));
        }
    ''', "2 1 5 -1 8 true 3 -2 1 false", ["2 1 5 -1 8 true 3 -2 -2 false", "5 1 5 -1 8 true 3 -2 1 false",
                                         "2 1 -5 -1 8 true 3 2 1 false"],
      "remainder keeps the dividend's sign, % never goes negative, and clamp limits to a range",
      """`(-5).remainder(3)` is -2, like the C operator, while `-5 % 3` is 1 because Dart's `%` always returns a
      value from 0 up to the divisor. `255.bitLength` is the number of bits needed, 8. `5.clamp(1, 3)` gives the
      upper bound, and `(-5).abs()` is 5, an odd number."""),

    q("json-decode-number-types", r'''

        import 'dart:convert';

        void main() {
          var l = jsonDecode('[1, 1.0, 1e2, "1", 12345678901234567890]');
          print(l.map((x) => x.runtimeType).join(' '));
        }
    ''', "int double double String double", ["int int int String int", "int double int String double",
                                           "int double double int double"],
      "JSON numbers become int when they have no point or exponent, and a float when they do or are too big",
      """`jsonDecode` returns an int for `1` and a double for `1.0` and `1e2`, because the text has a point or an
      exponent. A digit string too large for 64 bits (20 digits here) cannot be an int on the VM, so it becomes a
      double and loses precision."""),

    q("call-method-makes-an-object-callable", r'''
        class Adder {
          final int n;
          Adder(this.n);
          int call(int x) => x + n;
        }

        void main() {
          var add = Adder(10);
          var f = add.call;
          print([add(1), [1, 2].map(add).toList(), f(5), add is Function,
                 (add as dynamic)(2)].join(' '));
        }
    ''', "11 [11, 12] 15 false 12", ["11 [11, 12] 15 true 12", "11 [1, 2] 15 false 12", "1 [11, 12] 5 false 12"],
      "A class with a call method can be used like a function, but it is not itself a Function",
      """The `call` method is what `add(1)` runs, and `map` accepts the object because it only needs something that
      can be called with one argument. The object is still an `Adder`, so `add is Function` is false; `add.call`
      is the tear-off that is a real function."""),

    # ── Medium ───────────────────────────────────────────────────────────
    q("iterable-chain-methods", r'''
        void main() {
          var a = [1, 2, 3, 4, 5];
          print([a.skip(1).take(3).toList(), a.takeWhile((x) => x < 3).toList(),
                 a.skipWhile((x) => x < 3).toList(),
                 a.expand((x) => [x, x * 10]).take(4).toList(),
                 a.fold<int>(0, (s, x) => s + x), [7].reduce((a, b) => a + b),
                 <int>[].fold(5, (s, x) => s + x)].join(' '));
        }
    ''', "[2, 3, 4] [1, 2] [3, 4, 5] [1, 10, 2, 20] 15 7 5",
      ["[2, 3, 4] [1, 2] [4, 5] [1, 10, 2, 20] 15 7 5", "[2, 3, 4] [1, 2] [3, 4, 5] [1, 10, 2, 20] 15 0 5",
       "[2, 3, 4] [1, 2, 4, 5] [3, 4, 5] [1, 2, 3, 4] 15 7 0"],
      "takeWhile stops at the first miss, expand flattens, and reduce of one element is that element",
      """`skip(1).take(3)` drops one and keeps the next three. `takeWhile` stops at the first failure (3), and
      `skipWhile` drops only the leading run. `expand` maps each element to a list and joins them. `reduce` on a
      single element returns it untouched, and `fold` on an empty list returns the initial value."""),

    q("list-range-methods", r'''
        void main() {
          var l = [1, 2, 3, 4, 5];
          l.removeRange(1, 3);
          l.insertAll(1, [8, 9]);
          l.replaceRange(0, 2, [0]);
          var s = l.sublist(1, 3);
          print('$l $s ${l.getRange(1, 3).toList()} ${l.indexWhere((x) => x > 4)} '
              '${l.lastIndexWhere((x) => x > 4)} ${l.asMap()}');
        }
    ''', "[0, 9, 4, 5] [9, 4] [9, 4] 1 3 {0: 0, 1: 9, 2: 4, 3: 5}",
      ["[0, 8, 9, 4, 5] [8, 9] [8, 9] 1 3 {0: 0, 1: 8, 2: 9, 3: 4, 4: 5}",
       "[0, 9, 4, 5] [9, 4, 5] [9, 4, 5] 1 3 {0: 0, 1: 9, 2: 4, 3: 5}",
       "[0, 9, 4, 5] [9, 4] [9, 4] 1 1 {0: 0, 1: 9, 2: 4, 3: 5}"],
      "Range arguments are (start, end) with the end excluded, and replaceRange swaps a whole slice",
      """`removeRange(1, 3)` removes indexes 1 and 2, leaving [1, 4, 5]. After `insertAll` the list is
      [1, 8, 9, 4, 5], and `replaceRange(0, 2, [0])` replaces the first two elements with one: [0, 9, 4, 5].
      `sublist(1, 3)` and `getRange(1, 3)` both stop before index 3. `asMap` pairs each element with its
      index."""),

    q("map-update-and-remove", r'''
        void main() {
          var m = {'a': 1, 'b': 2};
          var r1 = m.update('a', (v) => v * 10);
          var r2 = m.update('z', (v) => v, ifAbsent: () => 0);
          var r3 = m.remove('b');
          var r4 = m.remove('q');
          m.addAll({'a': 5, 'c': 3});
          m.updateAll((k, v) => v + 1);
          print('$r1 $r2 $r3 $r4 $m');
        }
    ''', "10 0 2 null {a: 6, z: 1, c: 4}", ["10 0 2 null {a: 6, c: 4}", "1 0 2 null {a: 6, z: 1, c: 4}",
                                           "10 0 2 0 {a: 15, z: 1, c: 4}"],
      "update returns the new value, remove returns the old one (or null), and addAll overwrites",
      """`update` gives back the value it stored: 10 for `'a'` and 0 from `ifAbsent` for `'z'`. `remove` returns what
      was there, and null for a missing key. `addAll` overwrites `'a'` with 5 and appends `'c'`, and `updateAll` then
      adds 1 to every value. Insertion order is kept, with `'b'` gone."""),

    q("set-operations-keep-insertion-order", r'''
        void main() {
          var a = {3, 1, 2};
          print([a.union({5, 1}).toList(), a.intersection({2, 3, 9}).toList(),
                 a.difference({1}).toList(), a.containsAll({1, 3}), a.add(1),
                 a.lookup(2), {1, 2}.toList().reversed.toList()].join(' '));
        }
    ''', "[3, 1, 2, 5] [3, 2] [3, 2] true false 2 [2, 1]",
      ["[1, 2, 3, 5] [2, 3] [2, 3] true false 2 [2, 1]", "[3, 1, 2, 5] [2, 3] [3, 2] true true 2 [2, 1]",
       "[3, 1, 2, 5, 1] [3, 2] [3, 2] true false 2 [2, 1]"],
      "Sets keep insertion order, set operations follow the receiver, and add reports if it changed",
      """A Dart set literal is a linked hash set: it iterates in insertion order, not sorted. `union` starts with
      the receiver's elements, and `intersection` and `difference` keep them in the receiver's order. `add(1)`
      returns false because 1 is already there, so nothing changes."""),

    q("replace-string-versus-regexp", r'''
        void main() {
          print(['a.b.c'.replaceAll('.', '-'),
                 'a.b.c'.replaceAll(RegExp('.'), '-'),
                 'a1b22'.replaceAllMapped(RegExp(r'\d+'),
                     (m) => '<${m[0]!.length}>'),
                 'hello'.replaceFirst('l', 'L'), 'abc'.replaceRange(1, 2, 'XY'),
                 'a b'.replaceAll(' ', r'$&'), 'ab'.replaceAll('', '-')].join(' '));
        }
    ''', "a-b-c ----- a<1>b<2> heLlo aXYc a$&b -a-b-",
      ["----- ----- a<1>b<2> heLlo aXYc a$&b -a-b-", "a-b-c a-b-c a<1>b<2> heLlo aXYc a$&b -a-b-",
       "a-b-c ----- a<1>b<2> heLlo aXYbc a b -a-b-"],
      "A String pattern is literal text, a RegExp is a pattern; an empty pattern matches between characters",
      """`replaceAll('.', '-')` looks for a literal dot, while `RegExp('.')` matches any character and replaces all
      five. `replaceAllMapped` calls a function for each match. `replaceRange(1, 2, 'XY')` swaps one character for
      two. In a plain-string replacement `$&` is just text, and an empty pattern matches between every character
      and at both ends."""),

    q("nan-ordering-and-comparisons", r'''
        void main() {
          var n = double.nan;
          print([n == n, n.compareTo(1), n.compareTo(n), [n].contains(n), n > 1,
                 n < 1, (0 / 0).isNaN, 1 / 0 > double.maxFinite, n.toString(),
                 [3.0, n, 1.0].map((x) => x.isNaN).toList()].join(' '));
        }
    ''', "false 1 0 false false false true true NaN [false, true, false]",
      ["true 1 0 true false false true true NaN [false, true, false]",
       "false -1 0 false false false true true NaN [false, true, false]",
       "false 1 1 false true false true true NaN [false, true, false]"],
      "NaN is not equal to anything, not even itself, but compareTo still sorts it above every number",
      """Every comparison with NaN is false, `==` included, so `contains` cannot find it. `compareTo` is different: it
      is a total order, where NaN is equal to itself and larger than every other number, giving 1 and 0. `0 / 0` is
      NaN, and infinity is still larger than the biggest finite double."""),

    q("null-shorting-skips-the-rest-of-the-chain", r'''
        void main() {
          String? s;
          List<int>? l;
          l?..add(1)..add(2);
          var m = [1]..add(2);
          print('${s?.trim().length} ${s?.trim().length ?? -1} $l '
              '${(s?.length ?? 0) + 1} ${l?.length} ${m?.length}');
        }
    ''', "null -1 null 1 null 2", ["null 0 [1, 2] 1 2 2", "Error null -1 null 1 null 2",
                                   "null -1 null 1 0 2"],
      "A ?. that meets null skips everything after it in the same chain, including plain . calls",
      """When `s` is null, `s?.trim().length` is null as a whole: the `.length` is not evaluated, so there is no
      error even though `trim()` returned nothing. `?..` does the same for a cascade: `l` stays null and nothing is
      added. A null-aware `?.` on a variable that is not nullable is only a warning, and it just works."""),

    q("record-fields-equality-and-order", r'''
        void main() {
          var a = (x: 1, y: 2);
          var b = (y: 2, x: 1);
          var (:x, :y) = a;
          var c = (1, 2, z: 3);
          print('${a == b} $x$y ${c.$2} $c ${(1, 2) == (1.0, 2)} '
              '${(1, 2) == (2, 1)}');
        }
    ''', "true 12 2 (1, 2, z: 3) true false",
      ["false 12 2 (1, 2, z: 3) false false", "true 12 1 (1, 2, z: 3) true false",
       "true 12 2 (z: 3, 1, 2) true false"],
      "Record equality compares fields by name or position and ignores the order names were written in",
      """`(x: 1, y: 2)` and `(y: 2, x: 1)` have the same named fields, so they are equal. Positional fields are
      numbered from `$1`, so `c.$2` is 2, and in the printed form the named ones come after the positional ones.
      Fields are compared with `==`, which makes `1` and `1.0` equal; the order of positional fields matters."""),

    q("list-pattern-with-rest", r'''
        String f(List<int> l) => switch (l) {
              [] => 'empty',
              [var a] => 'one $a',
              [var a, var b] => 'two $a$b',
              [var a, ..., var z] => 'ends $a$z',
            };

        void main() {
          var [h, ...t] = [1, 2, 3];
          print([f([]), f([1]), f([1, 2]), f([1, 2, 3, 4]), h, t].join(' '));
        }
    ''', "empty one 1 two 12 ends 14 1 [2, 3]",
      ["empty one 1 two 12 ends 14 1 2", "empty one 1 ends 12 ends 14 1 [2, 3]",
       "empty one 1 two 12 ends 13 1 [2, 3]"],
      "Cases are tried from the top, and ... in a list pattern matches any number of elements in the middle",
      """A list pattern matches only a list of the right length: `[var a, var b]` takes exactly two, so the two-element
      list never reaches the last case, while `[var a, ..., var z]` needs at least two and binds the first and last.
      In `var [h, ...t]` the rest pattern collects the remaining elements into a new list."""),

    q("if-case-map-pattern", r'''
        String f(Map<String, Object?> j) {
          if (j case {'name': String n, 'age': int a}) return '$n:$a';
          if (j case {'name': String n}) return '$n:?';
          return 'none';
        }

        void main() {
          print([f({'name': 'a', 'age': 3}), f({'name': 'b', 'age': '4'}),
                 f({'name': 'c', 'extra': 1}), f({'age': 5}), f({})].join(' '));
        }
    ''', "a:3 b:? c:? none none", ["a:3 b:4 c:? none none", "a:3 b:? c:? none:5 none",
                                   "a:3 b:? c:? none None"],
      "A map pattern needs every listed key present with the right type, and extra keys are ignored",
      """The first pattern wants `age` to be an int, so `'4'` (a string) fails it and falls to the second pattern,
      which only needs a name. Keys not mentioned in a map pattern are simply ignored. A map with no `name` matches
      neither, so the function returns "none"."""),

    q("relational-and-or-patterns", r'''
        String k(int n) => switch (n) {
              < 0 => 'neg',
              0 => 'zero',
              > 0 && < 10 => 'small',
              10 || 20 => 'round',
              _ => 'big',
            };

        void main() {
          print([-5, 0, 5, 10, 15, 20].map(k).join(' '));
        }
    ''', "neg zero small round big round", ["neg zero small small big big", "neg zero small round round round",
                                            "neg zero small round big big"],
      "Relational patterns can be combined with && and ||, and the first case that matches wins",
      """`> 0 && < 10` matches 1 to 9, so 5 is "small" but 10 is not. `10 || 20` matches either constant, which is why 20
      is "round" and not "big". Anything left over reaches `_`."""),

    q("extension-on-nullable-receiver", r'''
        extension Blank on String? {
          bool get blank => this == null || this!.trim().isEmpty;
        }

        extension Twice on int {
          int get twice => this * 2;
        }

        void main() {
          String? s;
          String? t = '  ';
          print([s.blank, t.blank, 'a'.blank, 5.twice, 5.twice.twice,
                 (null as String?).blank].join(' '));
        }
    ''', "true true false 10 20 true", ["Error true true false 10 20 true", "true false false 10 20 true",
                                        "true true false 10 10 true"],
      "An extension on a nullable type can be called on null, since it is not dispatched through the object",
      """Extensions are resolved from the static type, not through the object, so `s.blank` works even when `s` is
      null: inside, `this` is just null. That is why an extension on `String?` is safe where the regular method
      call `s.isEmpty` would not compile."""),

    q("compound-index-assignment-calls-both", r'''
        class Box {
          final log = <String>[];
          int _v = 1;
          int operator [](int i) { log.add('get$i'); return _v; }
          void operator []=(int i, int v) { log.add('set$i'); _v = v; }
        }
        void main() {
          var b = Box();
          var n = 0;
          int next() { n++; b.log.add('idx$n'); return n; }
          b[next()] += 5;
          b[next()]++;
          print('${b.log} ${b._v} $n');
        }
    ''', "[idx1, get1, set1, idx2, get2, set2] 7 2",
      ["[idx1, idx1, get1, set1, idx2, idx2, get2, set2] 7 4", "[get1, set1, get2, set2] 7 2",
       "[idx1, get1, set1, idx2, get2, set2] 6 2"],
      "b[i] += x calls [] and then []=, and works out the index expression only once",
      """A compound assignment on an index is a get followed by a set, here `get1` then `set1`, and the index
      expression is evaluated a single time, so `next()` runs once per statement and logs `idx1` and `idx2` once
      each. The box ends at 1 + 5 + 1 = 7."""),

    q("empty-iterable-errors", r'''
        String t(void Function() f) {
          try {
            f();
            return 'ok';
          } catch (e) {
            return e.runtimeType.toString();
          }
        }

        void main() {
          var e = <int>[];
          print([t(() => e.first), t(() => e.reduce((a, b) => a + b)),
                 t(() => [1, 2].single), t(() => [1][5]),
                 t(() => e.fold<int>(0, (a, b) => a + b)), e.firstOrNull,
                 e.every((x) => false), e.any((x) => true)].join(' '));
        }
    ''', "StateError StateError StateError RangeError ok null true false",
      ["RangeError StateError StateError RangeError ok null true false",
       "StateError StateError StateError IndexError ok null true false",
       "StateError ok StateError RangeError ok null true false"],
      "first, reduce and single throw StateError; fold, every and any are fine on an empty list",
      """`first` on an empty list, `reduce` without an initial value and `single` on a list of two all throw a
      StateError, since there is no element to return. A bad index is a RangeError. `fold` has an initial value
      so it works, and `every` is true and `any` is false when there is nothing to test."""),

    q("exception-versus-error-catch", r'''
        String t(Object o) {
          try {
            throw o;
          } on Exception { return 'exception';
          } on Error { return 'error';
          } catch (e) { return 'other'; }
        }

        void main() {
          print([t(FormatException('x')), t(StateError('x')), t('s'),
                 t(ArgumentError('x')), t(Exception('y')),
                 t(UnimplementedError()), t(42)].join(' '));
        }
    ''', "exception error other error exception error other",
      ["exception exception other exception exception exception other",
       "exception error error error exception error error", "exception error other exception exception error other"],
      "StateError, ArgumentError and RangeError are Errors, not Exceptions; anything can be thrown",
      """Dart separates `Exception` (things a program may expect and handle, like `FormatException`) from `Error`
      (programming mistakes such as `StateError`, `ArgumentError` and `UnimplementedError`). A clause is chosen by
      type, so errors skip `on Exception`. A string or a number can be thrown too, and only the bare `catch`
      gets those."""),

    q("finally-return-wins", r'''
        int f(List<String> log) {
          try {
            log.add('try');
            return 1;
          } finally {
            log.add('finally');
          }
        }
        int g() {
          try { return 1; } finally { return 2; }
        }
        void main() {
          var log = <String>[];
          var a = f(log);
          print('$a ${g()} $log');
        }
    ''', "1 2 [try, finally]", ["1 1 [try, finally]", "2 2 [finally]", "1 2 [finally, try]"],
      "finally runs after the return value is computed, and a return inside it replaces that value",
      """In `f` the value 1 is evaluated first, then the `finally` block runs and logs, and then the function returns
      the 1. In `g` the `finally` block has its own `return`, which replaces the pending one, so the result is
      2."""),

    q("future-wait-keeps-argument-order", r'''
        Future<void> main() async {
          var log = <String>[];
          var r = await Future.wait([
            Future.delayed(Duration(milliseconds: 30), () {
              log.add('slow');
              return 'S';
            }),
            Future.value('F').then((v) {
              log.add('fast');
              return v;
            }),
          ]);
          print('$r $log');
        }
    ''', "[S, F] [fast, slow]", ["[F, S] [fast, slow]", "[S, F] [slow, fast]", "[F, S] [slow, fast]"],
      "Future.wait lists results in the order of the futures given, not the order they finished in",
      """The slow future finishes last, but its result sits first in the list because `Future.wait` collects the
      results by position. The log, written as each one completes, shows the real order: the immediate future
      first."""),

    q("async-star-and-yield-star", r'''
        Stream<int> two() async* {
          yield 2;
          yield 3;
        }
        Stream<int> gen() async* {
          yield 1;
          yield* two();
          yield 4;
        }
        Future<void> main() async {
          var out = <int>[];
          await for (var v in gen()) { out.add(v); }
          print('$out ${await gen().length} ${await gen().last}');
        }
    ''', "[1, 2, 3, 4] 4 4", ["[1, 4] 2 4", "[1, 2, 3, 4] 4 1", "[1, [2, 3], 4] 3 4"],
      "yield* hands over every value of another stream, one by one, in place",
      """`yield* two()` yields each item of the inner stream before the outer function goes on to `yield 4`, so the
      values come out in order. Streams made by an `async*` function start fresh for each listener, which is why
      `gen()` can be consumed again for the length and the last element."""),

    q("microtask-and-event-queue-order", r'''
        import 'dart:async';

        Future<void> main() async {
          var log = <String>[];
          Future(() => log.add('e1'));
          Future.microtask(() => log.add('m1'));
          scheduleMicrotask(() => log.add('m2'));
          Future.value('v').then((_) => log.add('t1'));
          Future.delayed(Duration.zero, () => log.add('d1'));
          () async { log.add('a1'); await null; log.add('a2'); }();
          log.add('s');
          await Future.delayed(Duration(milliseconds: 20));
          print(log.join(' '));
        }
    ''', "a1 s m1 m2 t1 a2 e1 d1", ["a1 s m1 m2 a2 t1 e1 d1", "a1 s e1 m1 m2 t1 a2 d1",
                                    "s a1 m1 m2 t1 a2 e1 d1"],
      "Synchronous code first, then all microtasks in the order queued, then the event-queue items",
      """An `async` function runs synchronously until its first `await`, so `a1` comes before `s`. Everything
      queued as a microtask (`Future.microtask`, `scheduleMicrotask`, the `then` of an already-completed future
      and the continuation after `await null`) runs before any timer or `Future(...)` event, in the order it was
      queued. `e1` and `d1` are event-queue tasks and come last."""),

    q("inferred-element-types", r'''
        void main() {
          var a = [1, 2.5];
          var b = [1, 'x'];
          var c = [1, 2];
          var d = <num>[1, 2];
          print('${a.runtimeType} ${b.runtimeType} ${c.runtimeType} '
              '${d is List<int>} ${c is List<num>} ${[1, null].runtimeType}');
        }
    ''', "List<num> List<Object> List<int> false true List<int?>",
      ["List<double> List<Object> List<int> true true List<int>", "List<num> List<dynamic> List<int> false true List<int?>",
       "List<num> List<Object> List<int> true true List<int?>"],
      "The element type is inferred from all the elements, and it is a real runtime type",
      """`[1, 2.5]` mixes int and double, so Dart infers their common supertype `num`, and `[1, 'x']` gets
      `Object`. A `[1, null]` list holds nullable ints. Because generic types are kept at run time, the list
      created as `<num>[1, 2]` is not a `List<int>`, even though it only holds ints, while a `List<int>` is a
      `List<num>`."""),

    q("enum-lookup-helpers", r'''
        enum Color { red, green, blue }

        void main() {
          print([Color.values.byName('blue').index, Color.green,
                 Color.values.last.name, Color.red == Color.values.first,
                 Color.values.indexOf(Color.blue),
                 Enum.compareByIndex(Color.green, Color.red),
                 Color.values.map((c) => c.name).join('/')].join(' '));
        }
    ''', "2 Color.green blue true 2 1 red/green/blue", ["2 green blue true 2 1 red/green/blue",
                                                       "2 Color.green blue true 2 -1 red/green/blue",
                                                       "1 Color.green blue true 2 1 red/green/blue"],
      "An enum prints as Enum.name, name is the bare word, and index counts from zero",
      """`Color.green` interpolated into a string is "Color.green", while `.name` gives just "green". `byName` finds a
      case by that name, and `index` is its position, so blue is 2. `Enum.compareByIndex` compares positions, which
      makes green greater than red."""),

    q("static-and-top-level-initialisers-are-lazy", r'''
        var log = <String>[];
        int mark(String s, int v) { log.add(s); return v; }
        class A {
          static final x = mark('x', 1);
          static int y = mark('y', 2);
        }
        void main() {
          log.add('start');
          var t = A.y;
          log.add('mid');
          var s = A.x + A.y + t;
          log.add('$s');
          print(log);
        }
    ''', "[start, y, mid, x, 5]", ["[x, y, start, mid, 5]", "[start, mid, x, y, 5]", "[start, y, mid, x, y, 5]"],
      "Static fields and top-level variables are initialised on first use, and only once",
      """Nothing in `A` runs when the program starts. `A.y` runs its initialiser the first time it is read, which
      logs "y" after "start". `A.x` runs later, at the first use inside the sum. The second read of `A.y` reuses
      the stored 2, so "y" is not logged again."""),

    q("datetime-utc-rolls-over", r'''
        void main() {
          var a = DateTime.utc(2024, 2, 30);
          var b = DateTime.utc(2024, 1, 31).add(Duration(days: 30));
          print([a, a.weekday, DateTime.utc(2024, 13, 1).year, b.toIso8601String(),
                 b.difference(DateTime.utc(2024, 1, 1)).inDays,
                 DateTime.utc(2024, 3, 0).day].join(' | '));
        }
    ''', "2024-03-01 00:00:00.000Z | 5 | 2025 | 2024-03-01T00:00:00.000Z | 60 | 29",
      ["Error", "2024-02-30 00:00:00.000Z | 5 | 2024 | 2024-03-01T00:00:00.000Z | 60 | 29",
       "2024-03-01 00:00:00.000Z | 4 | 2025 | 2024-03-01T00:00:00.000Z | 59 | 29"],
      "DateTime does not reject a day or month that is too big; it rolls into the next period",
      """The 30th of February 2024 becomes the 1st of March (2024 has 29 days in February), and month 13 is January of
      the following year. Day 0 means the last day of the previous month, so `DateTime.utc(2024, 3, 0)` is
      29 February. Weekdays are numbered from Monday = 1, which makes 1 March 2024 a Friday: 5."""),

    q("take-stops-a-lazy-chain", r'''
        void main() {
          var log = <int>[];
          var r = [1, 2, 3, 4]
              .map((x) {
                log.add(x);
                return x * 2;
              })
              .where((x) => x > 2)
              .take(1)
              .toList();
          print('$r $log');
        }
    ''', "[4] [1, 2]", ["[4] [1, 2, 3, 4]", "[4] [2]", "[4, 6, 8] [1, 2, 3, 4]"],
      "A lazy chain stops pulling elements as soon as take has enough",
      """`map` and `where` are lazy, so each element goes through both steps one at a time. 1 becomes 2, which fails
      `> 2`; 2 becomes 4 and passes, and `take(1)` is satisfied, so 3 and 4 are never touched."""),

    q("tear-off-equality", r'''
        int one() => 1;

        void main() {
          var a = <int>[];
          var f = (int x) => x;
          print([a.add == a.add, <int>[].add == <int>[].add, identical(one, one),
                 f == f, (() => 1) == (() => 1), one == one].join(' '));
        }
    ''', "true false true true false true", ["false false true true false true", "true true true true true true",
                                              "true false false true false true"],
      "A method tear-off is equal when it has the same receiver; separate closure literals are never equal",
      """Tearing off `a.add` twice gives two objects that compare equal because they are bound to the same list.
      The same method on a different list is not equal. A top-level function is one object. Two separate function
      expressions are different closures, even when they look identical."""),

    q("bigint-avoids-wraparound", r'''
        void main() {
          var big = BigInt.one << 70;
          var m = 9223372036854775807;
          print([big, big.bitLength, big.isValidInt,
                 (big + BigInt.one) % BigInt.from(7), m + 1,
                 BigInt.from(m) + BigInt.one, BigInt.from(10).pow(20)]
              .join(' '));
        }
    ''', "1180591620717411303424 71 false 3 -9223372036854775808 9223372036854775808 100000000000000000000",
      ["1180591620717411303424 70 false 3 -9223372036854775808 9223372036854775808 100000000000000000000",
       "1180591620717411303424 71 true 3 9223372036854775808 9223372036854775808 100000000000000000000",
       "1180591620717411303424 71 false 3 -9223372036854775808 -9223372036854775808 100000000000000000000"],
      "A BigInt never overflows, while an ordinary int wraps around at 64 bits",
      """`BigInt.one << 70` is 2 to the power 70, which needs 71 bits, so it does not fit in an int. Plain
      `m + 1` on the largest int wraps to the smallest, but the same sum in BigInt is exact. The remainder
      check shows the arbitrary precision at work: 2^70 + 1 leaves 3 when divided by 7."""),
)
