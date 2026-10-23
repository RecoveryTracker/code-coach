"""Dart data pack, part 1: Spread and Collection If - what `[...a, if (c) x, for (...) y]` builds.

Lists, maps and sets written with the spread (`...`, and the null-aware `...?`), `if` and `for` inside the brackets.
Every prompt prints its last line; answers are worked out by hand (a list, a map or a set as Dart prints it).
"""

from __future__ import annotations

from ._dart_model import D, dmod
from ._dartdata_model import DSet, V
from ._model import Maker

SPREAD = "The spread ... pours the items of a collection into the new one, in order."
IFS = "An if inside a collection literal adds its item only when the test is true."
COPY = "A spread makes a NEW collection: later changes to the old one do not reach it."

LISTS: list[Maker] = [
    D("var xs = [$a, $b];\nprint([...xs, $c]);", V("a", "b", "c"), SPREAD),
    D("var xs = [$a, $b];\nprint([$c, ...xs, ...xs]);", V("c", "a", "b", "a", "b"), "Each spread pours the items in again, one after the other."),
    D("var xs = [$a, $b, $c];\nprint([...xs.reversed, $d]);", V("c", "b", "a", "d"), "xs.reversed is spread backwards, then the last item follows."),
    D("List<int>? xs;\nprint([$a, ...?xs, $b]);", V("a", "b"), "...? spreads nothing when the list is null, instead of failing."),
    D("List<int>? xs = [$c];\nprint([$a, ...?xs, $b]);", V("a", "c", "b"), "xs is not null, so ...? spreads it like an ordinary ..."),
    D("List<int>? xs;\nprint([...?xs, $a].length);", 1, "The null list adds nothing: only the one item is left."),
    D("List<int>? xs;\nprint([...?xs].isEmpty);", True, "Spreading a null list with ...? gives an empty list."),
    D("var xs = [$a, $b];\nvar ys = [...xs];\nys.add($c);\nprint('$${xs.length} $${ys.length}');", lambda p: "2 3", "ys is a copy: adding to it leaves xs with its two items."),
    D("var xs = [$a];\nvar ys = xs;\nvar zs = [...xs];\nxs.add($b);\nprint('$${ys.length} $${zs.length}');", "2 1", "ys is the same list as xs, zs is a copy made before the add."),
    D("var xs = [$a, $b];\nvar ys = [...xs, 99];\nxs.add($c);\nprint(ys);", lambda p: [p["a"], p["b"], 99], COPY),
    D("print([$a, if ($a > $b) $c]);", lambda p: [p["a"], p["c"]] if p["a"] > p["b"] else [p["a"]], IFS),
    D("print([$a, if ($a < $b) $c else $d]);", lambda p: [p["a"], p["c"] if p["a"] < p["b"] else p["d"]], "if ... else inside a list always adds exactly one of the two items."),
    D("var big = $a > 5;\nprint([if (big) 'big' else 'small']);", lambda p: ["big" if p["a"] > 5 else "small"], "The test picks which of the two strings goes into the list."),
    D("var on = $a.isEven;\nprint(['x', if (on) 'y', 'z']);", lambda p: ["x", "y", "z"] if p["a"] % 2 == 0 else ["x", "z"], IFS),
    D("print([$a, if ($b > $c) $d, $n].length);", lambda p: 3 if p["b"] > p["c"] else 2, "The middle item only counts when its test is true."),
    D("var xs = [$a, $b, $c];\nprint([for (var x in xs) x * 2]);", lambda p: [2 * p[k] for k in "abc"], "A for inside the brackets adds one item per turn of the loop."),
    D("print([for (var i = 1; i <= $k + 1; i++) i * $a]);", lambda p: [i * p["a"] for i in range(1, p["k"] + 2)], "i counts from 1 up to k + 1 and each turn adds i * a."),
    D("print([for (var i = $a; i > $a - 3; i--) i]);", lambda p: [p["a"], p["a"] - 1, p["a"] - 2], "The loop counts down three times."),
    D("print([for (var i = 0; i < 3; i++) if (i != $k - 1) i]);", lambda p: [i for i in range(3) if i != p["k"] - 1], "The if skips the turn whose i equals k - 1."),
    D("print([for (var x in [$a, $b, $c, $d]) if (x > 5) x * 10]);", lambda p: [10 * p[k] for k in "abcd" if p[k] > 5], "Only the items bigger than 5 are added, each times ten."),
    D("print([for (var x in [$a, $b, $c]) if (x > 5) 'big' else 'small']);", lambda p: ["big" if p[k] > 5 else "small" for k in "abc"], "Every turn adds exactly one word, big or small."),
    D("print([for (var i = 1; i <= 2; i++) for (var j = 1; j <= $k + 1; j++) i * 10 + j]);", lambda p: [i * 10 + j for i in (1, 2) for j in range(1, p["k"] + 2)], "Two fors: for each i, j runs through all its values."),
    D("var rows = [[$a, $b], [$c]];\nprint([for (var r in rows) ...r]);", V("a", "b", "c"), "for plus ... flattens a list of lists."),
    D("var rows = [[$a, $b], [$c, $d]];\nprint([for (var r in rows) ...r.reversed]);", V("b", "a", "d", "c"), "Each row is spread backwards."),
    D("print([...[$a, $b].map((x) => x + 1), $c]);", lambda p: [p["a"] + 1, p["b"] + 1, p["c"]], "A lazy map can be spread too: its items are added one by one."),
    D("print([...{$a, $b}, $c]);", V("a", "b", "c"), "A set can be spread into a list: its items come in order."),
    D("var m = {'x': $a, 'y': $b};\nprint([...m.keys, ...m.values]);", lambda p: ["x", "y", p["a"], p["b"]], "Spread the keys, then the values; strings print bare."),
    D("print([...[$a, $b], ...[$c], ...[]].length);", 3, "An empty list adds nothing."),
    D("var xs = [$a, $b, $c, $d];\nprint([...xs.take(1), ...xs.skip(3)]);", V("a", "d"), "take(1) is the first item, skip(3) leaves the last one."),
    D("print([if ($a > 5) ...[$b, $c] else ...[$d]]);", lambda p: [p["b"], p["c"]] if p["a"] > 5 else [p["d"]], "if and ... together: the chosen branch is spread."),
    D("var xs = [$a, $b];\nprint([...xs, ...xs.map((x) => x * x)]);", lambda p: [p["a"], p["b"], p["a"] ** 2, p["b"] ** 2], "The items, then their squares."),
    D("print([for (var s in ['$w', '$v']) '$$s!']);", lambda p: [p["w"] + "!", p["v"] + "!"], "Each turn adds the word with an exclamation mark."),
    D("print(<int>[...[$a], ...[$b]].last);", lambda p: p["b"], "The last item poured in is b."),
    D("print([...(true ? [$a, $b] : [$c])]);", V("a", "b"), "The conditional gives the first list, and the spread pours it."),
    D("print([for (var i = 0; i < $a; i++) if (i % 3 == 0) i]);", lambda p: [i for i in range(p["a"]) if i % 3 == 0], "Only the multiples of 3 below a are kept."),
]

MAPS: list[Maker] = [
    D("print({'a': $a, ...{'b': $b}});", lambda p: {"a": p["a"], "b": p["b"]}, "The spread adds the pairs of the other map."),
    D("print({'a': $a, 'b': $b, ...{'a': $c}});", lambda p: {"a": p["c"], "b": p["b"]}, "The later a wins, but the key keeps its first place."),
    D("print({...{'a': $a}, 'a': $b});", lambda p: {"a": p["b"]}, "A key written later overwrites the spread one."),
    D("print({for (var i in [$a, $b]) i: i * i});", lambda p: {p["a"]: p["a"] ** 2, p["b"]: p["b"] ** 2}, "A for in a map literal adds one key: value pair per turn."),
    D("var on = $a > $b;\nprint({'k': 1, if (on) 'm': 2});", lambda p: {"k": 1, "m": 2} if p["a"] > p["b"] else {"k": 1}, "The pair after if is added only when the test is true."),
    D("print({for (var w in ['$w', '$v']) w: w.length});", lambda p: {p["w"]: len(p["w"]), p["v"]: len(p["v"])}, "Each word becomes a key with its length."),
    D("var m = {'x': $a};\nvar n = {...m, 'y': $b};\nm['x'] = $c;\nprint(n);", lambda p: {"x": p["a"], "y": p["b"]}, COPY),
    D("var m = {'x': $a, 'y': $b};\nprint({for (var e in m.entries) e.key: e.value + 1});", lambda p: {"x": p["a"] + 1, "y": p["b"] + 1}, "Same keys, each value one bigger."),
    D("var m = {'x': $a, 'y': $b};\nprint({for (var e in m.entries) e.value: e.key});", lambda p: {p["a"]: "x", p["b"]: "y"}, "Key and value swap places: the map is inverted."),
    D("Map<String, int>? m;\nprint({'a': $a, ...?m});", lambda p: {"a": p["a"]}, "...? skips a map that is null."),
    D("print({...{'a': 1, 'b': 2}, ...{'b': $a, 'c': $b}});", lambda p: {"a": 1, "b": p["a"], "c": p["b"]}, "b is overwritten by the later map; c is new and goes last."),
    D("print({'a': [$a, ...[$b]]});", lambda p: {"a": [p["a"], p["b"]]}, "The spread works inside the list that is the value."),
    D("print({for (var i = 1; i <= 3; i++) 'k$$i': i * $a});", lambda p: {f"k{i}": i * p["a"] for i in (1, 2, 3)}, "The key is built from i with interpolation."),
]

SETS: list[Maker] = [
    D("print({...[$a, $b, $a, $c]});", lambda p: DSet([p["a"], p["b"], p["a"], p["c"]]), "A set keeps each value once, so the repeat of a disappears."),
    D("print({$a, ...[$b, $a], $c});", lambda p: DSet([p["a"], p["b"], p["a"], p["c"]]), "The second a is already in the set and is dropped."),
    D("print({for (var x in [$a, $b, $c]) x % 3});", lambda p: DSet([dmod(p[k], 3) for k in "abc"]), "Remainders after dividing by 3; equal ones are kept once."),
    D("print({for (var x in [$a, $b, $c, $d]) x.isEven}.length);", lambda p: len({p[k] % 2 == 0 for k in "abcd"}), "The set holds true, false or both: its size is how many different answers."),
    D("var s = <int>{...[$a, $b]};\ns.addAll([$b, $c]);\nprint(s);", lambda p: DSet([p["a"], p["b"], p["b"], p["c"]]), "addAll skips what is already there."),
    D("print(<int>{...[$a, $a, $b]}.length);", 2, "Two different values."),
    D("print({$a, if ($a > $b) $b});", lambda p: DSet([p["a"], p["b"]]) if p["a"] > p["b"] else DSet([p["a"]]), IFS),
    D("print([...{$a, $b, $a}].length);", 2, "The set drops the repeat before the list is built."),
]

SPREADS: list[Maker] = LISTS + MAPS + SETS
