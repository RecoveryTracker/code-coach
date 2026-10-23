"""Dart core pack, part 2: Final or Const (does it compile and run?) and List Map Set (what do the collections print?).

Final or Const is a pick between "fine" and "error"; the oracle (`oracle="error"`) runs each snippet as shown and
calls it an error when it does not compile or throws. List Map Set is typed, and its answers are printed the way
Dart prints them: `[1, 2]`, `{a: 1}`, `{1, 2}`, and a lazy Iterable (map, where, take...) in ROUND brackets.
"""

from __future__ import annotations

from ._dart_model import D, DIter, DSet, FE
from ._model import Maker

# ── 3. Final or Const ───────────────────────────────────────────────────

ONCE = "A final variable can be given a value only once."
NOT_LIST = "final or const on the variable does not stop the list from changing - unless the list itself is const."
CONST_LIST = "A const list can never change: add, remove and assignment throw."

FINALS: list[Maker] = [
    FE("final x = $a;\nx = $b;", True, ONCE),
    FE("const x = $a;\nx = $b;", True, "A const variable can never be given a new value."),
    FE("var x = $a;\nx = $b;", False, "var can be reassigned as often as you like."),
    FE("final xs = [$a, $b];\nxs.add($c);", False, "final fixes the variable, not the list: the list can still grow."),
    FE("final xs = [$a, $b];\nxs = [$c];", True, "final means xs cannot point at a new list."),
    FE("const xs = [$a, $b];\nxs.add($c);", True, CONST_LIST),
    FE("const xs = [$a, $b];\nvar ys = [...xs, $c];\nys.add($d);", False, "ys is a new, ordinary list made from the const one."),
    FE("var xs = const [$a, $b];\nxs.add($c);", True, "The list is const even though the variable is var."),
    FE("var xs = const [$a, $b];\nxs = [$c];", False, "The var may point at a new list; only the const list is frozen."),
    FE("final m = {'a': $a};\nm['b'] = $b;", False, "final fixes the variable, not the map."),
    FE("const m = {'a': $a};\nm['b'] = $b;", True, "A const map can never change."),
    FE("final s = '$w';\ns = '$v';", True, ONCE),
    FE("late final int x;\nx = $a;\nx = $b;", True, "late final may be set later, but only once."),
    FE("late final int x;\nx = $a;", False, "The first assignment of a late final is allowed."),
    FE("late int x;\nprint(x);", True, "Reading a late variable before it is set throws."),
    FE("late int x;\nx = $a;\nprint(x);", False, "It is set before it is read."),
    FE("int x;\nprint(x);", True, "A non-nullable variable must have a value before it is read."),
    FE("int? x;\nprint(x);", False, "A nullable variable starts as null, so reading it is fine."),
    FE("int x;\nx = $a;\nprint(x);", False, "It gets its value before it is read."),
    FE("final int x;\nx = $a;\nprint(x);", False, "A final may be left empty and set once afterwards."),
    FE("final int x;\nx = $a;\nx = $b;", True, ONCE),
    FE("const n = $a;\nconst m = n * $b;", False, "A const can be built from another const."),
    FE("var n = $a;\nconst m = n * $b;", True, "A const needs a value known when the program is compiled; var is not."),
    FE("final n = $a;\nconst m = n * 2;", True, "A final is only known when the program runs, so it cannot feed a const."),
    FE("const w = '$w';\nconst l = w.length;", False, "The length of a const string is itself a compile-time constant."),
    FE("var list = [$a, $b];\nconst c = list;", True, "A const must be built from constants, and a var is not one."),
    FE("const xs = [$a, $b];\nprint(xs[0]);", False, "Reading from a const list is fine."),
    FE("const xs = [$a, $b];\nxs[0] = $c;", True, CONST_LIST),
    FE("final xs = List.unmodifiable([$a, $b]);\nxs.add($c);", True, "An unmodifiable list throws when you try to change it."),
    FE("final xs = List.filled(2, $a);\nxs.add($b);", True, "List.filled makes a fixed-length list: it cannot grow."),
    FE("final xs = List.filled(2, $a);\nxs[0] = $b;", False, "A fixed-length list can still have its items replaced."),
    FE("final xs = <int>[];\nxs.add($a);", False, NOT_LIST),
    FE("final xs = [$a, $b];\nxs.clear();", False, NOT_LIST),
    FE("final xs = [$a, $b];\nxs[5] = $c;", True, "Index 5 is past the end of a two-item list: a RangeError."),
    FE("final xs = [$a, $b];\nprint(xs[2]);", True, "A two-item list has indexes 0 and 1 only: a RangeError."),
    FE("var xs = <int>[];\nprint(xs.first);", True, "An empty list has no first item: a StateError."),
    FE("final s = {$a, $b};\ns.add($c);", False, NOT_LIST),
    FE("const s = {$a, $b};\ns.add($c);", True, "A const set can never change."),
    FE("final a = $a;\nfinal b = a + $b;", False, "A final may be worked out from another variable."),
    FE("var x = $a;\nx = '$w';", True, "var took the type int from the first value, so a String does not fit."),
    FE("dynamic x = $a;\nx = '$w';", False, "dynamic accepts any type."),
    FE("int x = $a;\nx = 1.5;", True, "An int variable cannot hold a double."),
    FE("num x = $a;\nx = 1.5;", False, "num holds both ints and doubles."),
    FE("var x = null;\nx = $a;", False, "var with null is dynamic, so anything fits."),
    FE("String s = null;", True, "A non-nullable String cannot be null."),
    FE("String? s = null;", False, "The ? makes null allowed."),
    FE("int x = '$a';", True, "A String is not an int."),
    FE("final x = $a;\nx++;", True, "x++ gives x a new value, which a final cannot take."),
    FE("var x = $a;\nx++;", False, "x++ adds one to a var."),
    FE("final xs = [$a, $b];\nxs.removeLast();", False, NOT_LIST),
    FE("const xs = [$a, $b];\nxs.clear();", True, CONST_LIST),
    FE("const xs = [$a, $b, $c];\nxs.sort();", True, "sort changes the list in place, which a const list cannot do."),
    FE("final xs = [$a, $b];\nxs.add('$w');", True, "xs is a List<int>, so a String does not fit."),
    FE("var xs = [$a, '$w'];\nxs.add(true);", False, "A list holding an int and a String is a List<Object>: anything fits."),
    FE("late String s;\nprint(s.length);", True, "s was never set, so reading it throws."),
    FE("late final int x = $a;\nprint(x);", False, "A late variable with a value is set the first time it is read."),
]

# ── 4. List Map Set ─────────────────────────────────────────────────────


def _l(p: dict, *keys: str) -> list:
    return [p[k] for k in keys]


LISTS: list[Maker] = [
    D("print([$a, $b, $c].map((x) => x * 2).toList());", lambda p: [2 * x for x in _l(p, "a", "b", "c")], "map applies the function to every item; toList() makes a list of the results."),
    D("print([$a, $b, $c].map((x) => x * 2));", lambda p: DIter(2 * x for x in _l(p, "a", "b", "c")), "map is lazy: without toList() print shows an Iterable, in round brackets."),
    D("print([$a, $b, $c, $d].where((x) => x.isEven).toList());", lambda p: [x for x in _l(p, "a", "b", "c", "d") if x % 2 == 0], "where keeps the items the test accepts."),
    D("print([$a, $b, $c, $d].where((x) => x > 5).toList());", lambda p: [x for x in _l(p, "a", "b", "c", "d") if x > 5], "Only the items bigger than 5 stay; maybe none."),
    D("print([$a, $b, $c].reduce((x, y) => x + y));", lambda p: p["a"] + p["b"] + p["c"], "reduce folds the list into one value, starting from the first item."),
    D("var t = [$a, $b, $c].fold(10, (s, x) => s + x);\nprint(t);", lambda p: 10 + p["a"] + p["b"] + p["c"], "fold starts from the first argument, here 10, and adds each item."),
    D("print([$a, $b, $c, $d].reduce((x, y) => x > y ? x : y));", lambda p: max(_l(p, "a", "b", "c", "d")), "Keeping the bigger of each pair leaves the biggest."),
    D("print([$a, $b, $c].take(2).toList());", lambda p: [p["a"], p["b"]], "take(2) keeps the first two items."),
    D("print([$a, $b, $c, $d].skip(2).toList());", lambda p: [p["c"], p["d"]], "skip(2) drops the first two items."),
    D("print([$a, $b, $c].take(2));", lambda p: DIter([p["a"], p["b"]]), "take gives a lazy Iterable, which print shows in round brackets."),
    D("print([$a, $b, $c].any((x) => x > $d));", lambda p: any(x > p["d"] for x in _l(p, "a", "b", "c")), "any is true when at least one item passes."),
    D("print([$a, $b, $c].every((x) => x > $d));", lambda p: all(x > p["d"] for x in _l(p, "a", "b", "c")), "every is true only when all items pass."),
    D("print([$a, $b, $c].contains($b));", True, "b is one of the items."),
    D("print([$a, $b, $c].contains($d));", False, "d is not in the list."),
    D("print([$a, $b, $c].indexOf($c));", 2, "indexOf gives the position, counting from 0."),
    D("print([$a, $b, $c].indexOf($d));", -1, "indexOf gives -1 when the item is missing."),
    D("print([$a, $b, $c, $d].sublist(1, 3));", lambda p: [p["b"], p["c"]], "sublist(1, 3) takes positions 1 and 2: the end is left out."),
    D("print([$a, $b, $c, $d].sublist(2));", lambda p: [p["c"], p["d"]], "sublist(2) takes everything from position 2."),
    D("var xs = [$a, $b, $c];\nxs.insert(1, $d);\nprint(xs);", lambda p: [p["a"], p["d"], p["b"], p["c"]], "insert(1, v) puts v at position 1 and pushes the rest along."),
    D("var xs = [$a, $b, $c];\nxs.removeAt(0);\nprint(xs);", lambda p: [p["b"], p["c"]], "removeAt(0) takes out the first item."),
    D("var xs = [$a, $b, $c];\nprint(xs.removeAt(1));", lambda p: p["b"], "removeAt gives back the item it removed."),
    D("var xs = [$a, $b, $c];\nxs.remove($b);\nprint(xs);", lambda p: [p["a"], p["c"]], "remove(v) takes out the first item equal to v."),
    D("var xs = [$a, $b];\nxs.add($c);\nxs.addAll([$d, $n]);\nprint(xs);", lambda p: _l(p, "a", "b", "c", "d", "n"), "add puts one item at the end; addAll puts several."),
    D("var xs = [$a, $b, $c];\nprint(xs.removeLast());", lambda p: p["c"], "removeLast takes out and returns the last item."),
    D("var xs = [$a, $b, $c];\nxs.removeLast();\nprint(xs.length);", 2, "One item is gone, so two are left."),
    D("print([$a, $b].expand((x) => [x, x]).toList());", lambda p: [p["a"], p["a"], p["b"], p["b"]], "expand turns each item into several and joins them all."),
    D("var xs = [$a, $b, $c];\nprint(xs.first + xs.last);", lambda p: p["a"] + p["c"], "first is the first item, last the last one."),
    D("print(<int>[].isEmpty);", True, "A list with no items is empty."),
    D("print([$a, $b, $c].reversed.toList());", lambda p: [p["c"], p["b"], p["a"]], "reversed walks the list backwards."),
    D("print([$a, $b, $c].reversed);", lambda p: DIter([p["c"], p["b"], p["a"]]), "reversed is a lazy Iterable, so print shows round brackets."),
    D("var xs = [$a, $b, $c, $d];\nxs.sort();\nprint(xs);", lambda p: sorted(_l(p, "a", "b", "c", "d")), "sort puts the numbers in increasing order, in place."),
    D("var xs = [$a, $b, $c, $d];\nxs.sort((x, y) => y - x);\nprint(xs);", lambda p: sorted(_l(p, "a", "b", "c", "d"), reverse=True), "Comparing y - x puts the bigger numbers first."),
    D("print([$a, $a, $b, $b, $c].toSet().length);", 3, "A set keeps each value once: three different numbers."),
    D("print([$a, $a, $b].toSet());", lambda p: DSet([p["a"], p["b"]]), "toSet drops the repeat; sets print in curly brackets."),
    D("print([$a, $b] + [$c]);", lambda p: _l(p, "a", "b", "c"), "+ joins two lists into a new one."),
    D("print([...[$a, $b], $c]);", lambda p: _l(p, "a", "b", "c"), "The spread ... pours a list's items into the new list."),
    D("print([for (var i = 0; i < $k + 2; i++) i * $a]);", lambda p: [i * p["a"] for i in range(p["k"] + 2)], "A for inside a list builds one item per turn."),
    D("print([for (var x in [$a, $b, $c]) if (x.isOdd) x]);", lambda p: [x for x in _l(p, "a", "b", "c") if x % 2], "The if inside keeps only the odd ones."),
    D("print([$a, if ($a > $b) $b, $c]);", lambda p: [p["a"], p["b"], p["c"]] if p["a"] > p["b"] else [p["a"], p["c"]], "An if inside a list adds its item only when the test is true."),
    D("print(List.generate($k + 2, (i) => i * i));", lambda p: [i * i for i in range(p["k"] + 2)], "generate calls the function for 0, 1, 2 ..."),
    D("print(List.filled($k + 1, $a));", lambda p: [p["a"]] * (p["k"] + 1), "filled repeats the value."),
    D("print(List.filled(3, 'x'));", ["x", "x", "x"], "Strings print without quotes, even inside a list."),
    D("print([$a, $b, $c].join('-'));", lambda p: f"{p['a']}-{p['b']}-{p['c']}", "join glues the items together with the separator."),
    D("print(['$w', '$v'].join());", lambda p: p["w"] + p["v"], "join with no argument uses no separator."),
    D("print(['$w', '$v'].join(', '));", lambda p: f"{p['w']}, {p['v']}", "join puts the separator between the items."),
    D("print([$a, $b, $c].map((x) => x.toString()).join());", lambda p: f"{p['a']}{p['b']}{p['c']}", "Each number becomes text, then join glues them."),
    D("var xs = ['$w', '$v'];\nxs.sort();\nprint(xs);", lambda p: sorted([p["w"], p["v"]]), "Strings sort alphabetically."),
    D("print([$a, $b, $c, $d].firstWhere((x) => x > 5, orElse: () => -1));", lambda p: next((x for x in _l(p, "a", "b", "c", "d") if x > 5), -1), "firstWhere gives the first item that passes, or the orElse value."),
    D("print([$a, $b, $c, $d].indexWhere((x) => x.isEven));", lambda p: next((i for i, x in enumerate(_l(p, "a", "b", "c", "d")) if x % 2 == 0), -1), "indexWhere gives the position of the first match, or -1."),
    D("print([$a, $b, $c, $d].lastWhere((x) => x.isOdd, orElse: () => 0));", lambda p: next((x for x in reversed(_l(p, "a", "b", "c", "d")) if x % 2), 0), "lastWhere looks from the end for the first match."),
    D("var xs = [$a, $b, $c, $d];\nxs.removeWhere((x) => x.isEven);\nprint(xs);", lambda p: [x for x in _l(p, "a", "b", "c", "d") if x % 2], "removeWhere deletes every item that passes the test."),
    D("print([$a, $b, $c, $d].skip(1).take(2).toList());", lambda p: [p["b"], p["c"]], "Skip one, then take two."),
    D("print([$a, $b, $c].map((x) => x % 2 == 0 ? 'e' : 'o').join());", lambda p: "".join("e" if x % 2 == 0 else "o" for x in _l(p, "a", "b", "c")), "Each number becomes e or o, and join glues them."),
    D("var xs = [$a, $b];\nvar ys = xs;\nys.add($c);\nprint(xs);", lambda p: _l(p, "a", "b", "c"), "ys is the same list as xs, not a copy."),
    D("var xs = [$a, $b];\nvar ys = [...xs];\nys.add($c);\nprint(xs);", lambda p: _l(p, "a", "b"), "[...xs] makes a copy, so xs is untouched."),
    D("var xs = [$a, $b, $c];\nxs[1] = $d;\nprint(xs);", lambda p: [p["a"], p["d"], p["c"]], "xs[1] = v replaces the item at position 1."),
    D("var xs = [$a, $b, $c];\nxs.clear();\nprint(xs);", [], "clear removes every item."),
    D("print([$a, $b, $c].map((x) => x * x).reduce((x, y) => x + y));", lambda p: sum(x * x for x in _l(p, "a", "b", "c")), "Square each, then add them up."),
    D("print([[$a, $b], [$c, $d]].expand((x) => x).toList());", lambda p: _l(p, "a", "b", "c", "d"), "expand with the list itself flattens a list of lists."),
    D("print([$a]..add($b)..add($c));", lambda p: _l(p, "a", "b", "c"), ".. calls the method and keeps the list, so the cascade gives the list."),
    D("var xs = [$a, $b, $c]..sort((x, y) => y - x);\nprint(xs);", lambda p: sorted(_l(p, "a", "b", "c"), reverse=True), "The cascade sorts the list and xs is that list."),
]


def _m(p: dict) -> dict:
    return {"a": p["a"], "b": p["b"]}


M2 = "var m = {'a': $a, 'b': $b};\n"

MAPS: list[Maker] = [
    D(M2 + "print(m['b']);", lambda p: p["b"], "m[key] gives the value stored under the key."),
    D(M2 + "print(m);", lambda p: _m(p), "A map prints as {key: value, ...} with strings bare."),
    D(M2 + "print(m.keys);", lambda p: DIter(["a", "b"]), "keys is an Iterable, so print shows round brackets."),
    D(M2 + "print(m.keys.toList());", ["a", "b"], "toList makes a real list of the keys."),
    D(M2 + "print(m.values.toList());", lambda p: [p["a"], p["b"]], "values are the stored values, in the order the keys were added."),
    D(M2 + "print(m.length);", 2, "The number of key-value pairs."),
    D(M2 + "m['c'] = $c;\nprint(m);", lambda p: {**_m(p), "c": p["c"]}, "A new key is added at the end."),
    D(M2 + "m['a'] = $c;\nprint(m);", lambda p: {"a": p["c"], "b": p["b"]}, "An existing key keeps its place and gets the new value."),
    D(M2 + "print(m.containsKey('c'));", False, "There is no key c."),
    D(M2 + "print(m.containsValue($b));", True, "b is one of the values."),
    D(M2 + "print(m.remove('a'));", lambda p: p["a"], "remove gives back the value it removed."),
    D(M2 + "m.remove('a');\nprint(m);", lambda p: {"b": p["b"]}, "The key a is gone."),
    D(M2 + "print(m.putIfAbsent('c', () => $c));", lambda p: p["c"], "c is missing, so it is added and its value is returned."),
    D(M2 + "m.putIfAbsent('a', () => $c);\nprint(m);", lambda p: _m(p), "a is already there, so nothing changes."),
    D(M2 + "print(m.map((k, v) => MapEntry(k, v * 2)));", lambda p: {"a": 2 * p["a"], "b": 2 * p["b"]}, "map on a map builds a new map from each pair."),
    D("print({for (var k in ['x', 'yy']) k: k.length});", {"x": 1, "yy": 2}, "A for inside a map literal builds one pair per turn."),
    D(M2 + "m.update('a', (v) => v + 1);\nprint(m['a']);", lambda p: p["a"] + 1, "update changes one value using the old one."),
    D("var m = <String, int>{};\nm['k'] = $a;\nm['k'] = m['k']! + 1;\nprint(m);", lambda p: {"k": p["a"] + 1}, "The same key is overwritten, not added twice."),
    D("var m = <String, int>{};\nfor (var c in '$w'.split('')) {\n  m[c] = (m[c] ?? 0) + 1;\n}\nprint(m);", lambda p: _count(p["w"]), "Counting letters: each new letter starts at 0, then adds one."),
    D(M2 + "print(m.entries.map((e) => '$${e.key}$${e.value}').join(','));", lambda p: f"a{p['a']},b{p['b']}", "Each entry has a key and a value."),
    D("var m = {1: 'x', 2: 'y'};\nprint(m[2]);", "y", "Keys do not have to be strings."),
    D("print({$a: 'x'}[$b]);", None, "The key is missing, so the lookup gives null."),
    D("print(<String, int>{}.isEmpty);", True, "A map with no pairs is empty."),
    D("print(Map.fromIterables(['a', 'b'], [$a, $b]));", lambda p: _m(p), "fromIterables pairs the keys with the values."),
    D("print({...{'a': $a}, ...{'a': $b}});", lambda p: {"a": p["b"]}, "The later spread overwrites the earlier key."),
    D(M2 + "print(m.keys.map((k) => k.toUpperCase()).toList());", ["A", "B"], "Each key is upper-cased."),
    D(M2 + "print(m.values.reduce((x, y) => x + y));", lambda p: p["a"] + p["b"], "Add the two values."),
]


def _count(word: str) -> dict:
    out: dict = {}
    for ch in word:
        out[ch] = out.get(ch, 0) + 1
    return out


SETS: list[Maker] = [
    D("print({$a, $b, $a});", lambda p: DSet([p["a"], p["b"]]), "A set keeps each value once, in the order it first appeared."),
    D("var s = {$a, $b};\ns.add($c);\nprint(s);", lambda p: DSet(_l(p, "a", "b", "c")), "add puts a new value at the end."),
    D("var s = {$a, $b};\nprint(s.add($a));", False, "add gives false when the value was already there."),
    D("var s = {$a, $b};\nprint(s.add($c));", True, "add gives true when the value was new."),
    D("print({$a, $b}.union({$b, $c}));", lambda p: DSet(_l(p, "a", "b", "c")), "union holds everything that is in either set."),
    D("print({$a, $b, $c}.intersection({$b, $c, $d}));", lambda p: DSet([p["b"], p["c"]]), "intersection holds only what is in both."),
    D("print({$a, $b, $c}.difference({$b}));", lambda p: DSet([p["a"], p["c"]]), "difference holds what is in the first set but not the second."),
    D("print({$a, $b}.contains($a));", True, "a is in the set."),
    D("print({$a, $b}.length);", 2, "Two different values."),
    D("print([$a, $b, $a, $c, $b].toSet().toList());", lambda p: _l(p, "a", "b", "c"), "toSet removes the repeats, toList turns it back."),
    D("var s = <int>{};\ns.add($a);\ns.add($a);\nprint(s.length);", 1, "The second add finds the value already there."),
    D("print({'$w', '$v'}.length);", 2, "Two different words."),
    D("print({$a, $b} == {$b, $a});", False, "== on two sets asks whether they are the same object, not whether they hold the same values."),
    D("print([$a] == [$a]);", False, "== on two lists asks whether they are the same object, not whether they hold the same values."),
]

COLLECTIONS: list[Maker] = LISTS + MAPS + SETS
