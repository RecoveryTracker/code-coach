"""Dart data pack, part 2: Iterable Chains - where, map, take, skip, expand, whereType... and what they leave behind.

Most chains are LAZY: `xs.map(f)` does no work and prints in round brackets `(2, 4)` until `.toList()` (or `.length`,
`.first`, a loop...) asks for the items. Several templates count how often a function is called to show when the
work really happens. The random lists keep their numbers distinct and small, so every answer is one short line.
"""

from __future__ import annotations

import random

from ._dartdata_model import DIter, DSet, R, ints, lit, words
from ._model import Maker

LAZY = "map, where, take, skip and the like are lazy: print shows an Iterable in round brackets until toList() is called."


def _xs(r: random.Random, n: int = 5, lo: int = 1, hi: int = 30) -> list[int]:
    return ints(r, n, lo, hi)


def i_where_len(r):
    xs = _xs(r, 6)
    t = r.choice(xs)
    return (f"var xs = {lit(xs)};\nprint(xs.where((x) => x > {t}).length);", sum(1 for x in xs if x > t),
            "where keeps the items bigger than the limit; length counts them.")


def i_map_list(r):
    xs, k = _xs(r, 4, 1, 9), r.randint(2, 5)
    return (f"var xs = {lit(xs)};\nprint(xs.map((x) => x * {k}).toList());", [x * k for x in xs],
            "map turns every item into its multiple; toList() makes the real list.")


def i_map_lazy(r):
    xs, k = _xs(r, 3, 1, 9), r.randint(2, 9)
    return (f"var xs = {lit(xs)};\nprint(xs.map((x) => x + {k}));", DIter(x + k for x in xs), LAZY)


def i_where_lazy(r):
    xs = _xs(r, 5, 1, 20)
    return (f"var xs = {lit(xs)};\nprint(xs.where((x) => x.isEven));", DIter(x for x in xs if x % 2 == 0) if any(x % 2 == 0 for x in xs) else DIter(),
            LAZY)


def i_where_last(r):
    xs = _xs(r, 6)
    while not any(x % 2 for x in xs):
        xs = _xs(r, 6)
    return (f"var xs = {lit(xs)};\nprint(xs.where((x) => x.isOdd).last);", [x for x in xs if x % 2][-1],
            "where keeps the odd items in their order; last is the final one of those.")


def i_where_first(r):
    xs = _xs(r, 6)
    t = sorted(xs)[2]
    return (f"var xs = {lit(xs)};\nprint(xs.where((x) => x > {t}).first);", next(x for x in xs if x > t),
            "first is the first item in the LIST order that passes, not the smallest.")


def i_skip_take(r):
    xs = _xs(r, 6)
    s, t = r.randint(1, 3), r.randint(1, 3)
    return (f"var xs = {lit(xs)};\nprint(xs.skip({s}).take({t}).toList());", xs[s:][:t],
            "Skip the first items, then keep the next few.")


def i_take_skip(r):
    xs = _xs(r, 6)
    t, s = r.randint(3, 5), r.randint(1, 2)
    return (f"var xs = {lit(xs)};\nprint(xs.take({t}).skip({s}).toList());", xs[:t][s:],
            "take first cuts the list to its first items; skip then drops from those.")


def _takewhile(xs, f):
    out = []
    for x in xs:
        if not f(x):
            break
        out.append(x)
    return out


def _skipwhile(xs, f):
    i = 0
    while i < len(xs) and f(xs[i]):
        i += 1
    return xs[i:]


def i_takewhile(r):
    xs = _xs(r, 6)
    t = r.choice(xs)
    return (f"var xs = {lit(xs)};\nprint(xs.takeWhile((x) => x != {t}).toList());", _takewhile(xs, lambda x: x != t),
            "takeWhile stops at the first item that fails the test and ignores the rest.")


def i_takewhile_lt(r):
    xs = _xs(r, 6)
    t = r.randint(10, 20)
    return (f"var xs = {lit(xs)};\nprint(xs.takeWhile((x) => x < {t}).toList());", _takewhile(xs, lambda x: x < t),
            "takeWhile stops at the first item that is not below the limit, even if later ones are.")


def i_skipwhile(r):
    xs = _xs(r, 6)
    t = r.randint(10, 20)
    return (f"var xs = {lit(xs)};\nprint(xs.skipWhile((x) => x < {t}).toList());", _skipwhile(xs, lambda x: x < t),
            "skipWhile drops items while the test holds, then keeps everything that is left, passing or not.")


def i_takewhile_lazy(r):
    xs = _xs(r, 5)
    t = r.randint(10, 20)
    return (f"var xs = {lit(xs)};\nprint(xs.takeWhile((x) => x < {t}));", DIter(_takewhile(xs, lambda x: x < t)), LAZY)


def i_expand(r):
    a, b = ints(r, 2, 1, 9)
    return (f"print([{a}, {b}].expand((x) => [x, x * 10]).toList());", [a, a * 10, b, b * 10],
            "expand turns each item into a list of items and joins them all.")


def i_expand_take(r):
    a, b, c = ints(r, 3, 1, 9)
    return (f"print([{a}, {b}, {c}].expand((x) => [x, -x]).take(3).toList());", [a, -a, b],
            "expand gives a, -a, b, -b ...; take(3) keeps the first three.")


def i_expand_len(r):
    n = r.randint(3, 6)
    return (f"print(List.generate({n}, (i) => i).expand((i) => List.filled(i, i)).length);", sum(range(n)),
            "Item i becomes i copies of itself: 0 + 1 + 2 + ... altogether.")


def i_followed(r):
    xs, ys = _xs(r, 3, 1, 9), ints(r, 2, 10, 20)
    return (f"print({lit(xs)}.followedBy({lit(ys)}).toList());", xs + ys,
            "followedBy puts the second collection after the first.")


def i_followed_lazy(r):
    xs, ys = _xs(r, 2, 1, 9), ints(r, 2, 10, 20)
    return (f"print({lit(xs)}.followedBy({lit(ys)}));", DIter(xs + ys), LAZY)


def i_wheretype_ints(r):
    a, b = ints(r, 2, 1, 9)
    w, v = words(r, 2)
    return (f"var xs = <Object>[{a}, '{w}', {b}, '{v}'];\nprint(xs.whereType<int>().toList());", [a, b],
            "whereType<int>() keeps only the items that are ints.")


def i_wheretype_str(r):
    a, b = ints(r, 2, 1, 9)
    w, v = words(r, 2)
    items = [a, w, v, b]
    return (f"var xs = <Object>[{lit(items)[1:-1]}];\nprint(xs.whereType<String>().join('+'));", f"{w}+{v}",
            "whereType<String>() keeps the strings; join glues them with +.")


def i_wheretype_len(r):
    a, b, c = ints(r, 3, 1, 9)
    w = words(r, 1)[0]
    return (f"var xs = <Object>[{a}, '{w}', {b}, {c}];\nprint(xs.whereType<int>().length);", 3,
            "Three of the four items are ints.")


def i_single(r):
    xs = _xs(r, 5)
    t = sorted(xs)[-2]
    return (f"var xs = {lit(xs)};\nprint(xs.where((x) => x > {t}).single);", max(xs),
            "Only the biggest item is above the second biggest, so exactly one item is left: single is it.")


def i_elementat(r):
    xs = _xs(r, 5)
    i = r.randint(0, 4)
    return (f"var xs = {lit(xs)};\nprint(xs.elementAt({i}));", xs[i], "elementAt(i) counts from 0, like xs[i].")


def i_elementat_map(r):
    xs, i, k = _xs(r, 5, 1, 9), r.randint(0, 4), r.randint(2, 5)
    return (f"var xs = {lit(xs)};\nprint(xs.map((x) => x * {k}).elementAt({i}));", xs[i] * k,
            "elementAt walks the lazy map to position i and gives that item times the factor.")


def i_calls_twice(r):
    n = r.randint(2, 5)
    xs = _xs(r, n)
    return (f"var calls = 0;\nvar m = {lit(xs)}.map((x) {{\n  calls++;\n  return x;\n}});\nm.toList();\nm.toList();\nprint(calls);",
            2 * n, "Every toList() runs the function again for every item: lazy results are not remembered.")


def i_calls_none(r):
    n = r.randint(2, 5)
    xs = _xs(r, n)
    return (f"var calls = 0;\nvar m = {lit(xs)}.map((x) {{\n  calls++;\n  return x;\n}});\nprint(calls);", 0,
            "map does no work until somebody asks for the items.")


def i_calls_first(r):
    n = r.randint(3, 5)
    xs = _xs(r, n)
    return (f"var calls = 0;\nvar m = {lit(xs)}.map((x) {{\n  calls++;\n  return x;\n}});\nm.first;\nprint(calls);", 1,
            "first only needs one item, so the function runs once.")


def i_calls_take(r):
    k = r.randint(1, 3)
    xs = _xs(r, 5)
    return (f"var calls = 0;\nvar m = {lit(xs)}.map((x) {{\n  calls++;\n  return x;\n}});\nm.take({k}).toList();\nprint(calls);", k,
            "take stops asking after its items, so only that many calls happen.")


def i_calls_where_first(r):
    xs = _xs(r, 6)
    t = sorted(xs)[2]
    idx = next(i for i, x in enumerate(xs) if x > t)
    return (f"var calls = 0;\nvar ok = {lit(xs)}.where((x) {{\n  calls++;\n  return x > {t};\n}});\nok.first;\nprint(calls);",
            idx + 1, "The test runs on items one by one until the first that passes, and then stops.")


def i_calls_any(r):
    xs = _xs(r, 6)
    t = r.choice(xs)
    idx = xs.index(t)
    return (f"var calls = 0;\n{lit(xs)}.any((x) {{\n  calls++;\n  return x == {t};\n}});\nprint(calls);", idx + 1,
            "any stops at the first item that passes, so it counts the items up to and including it.")


def i_calls_every(r):
    xs = _xs(r, 6)
    t = r.choice(xs)
    idx = xs.index(t)
    return (f"var calls = 0;\n{lit(xs)}.every((x) {{\n  calls++;\n  return x != {t};\n}});\nprint(calls);", idx + 1,
            "every stops at the first item that fails.")


def i_view_later(r):
    xs = _xs(r, 2, 1, 9)
    c, k = r.randint(10, 20), r.randint(2, 4)
    return (f"var xs = {lit(xs)};\nvar m = xs.map((x) => x * {k});\nxs.add({c});\nprint(m.toList());", [x * k for x in xs + [c]],
            "m is lazy, so it sees the item added before toList() ran.")


def i_copy_later(r):
    xs = _xs(r, 2, 1, 9)
    c, k = r.randint(10, 20), r.randint(2, 4)
    return (f"var xs = {lit(xs)};\nvar l = xs.map((x) => x * {k}).toList();\nxs.add({c});\nprint(l);", [x * k for x in xs],
            "toList() made a real list at once, so the later add does not reach it.")


def i_reversed_view(r):
    xs = _xs(r, 3, 1, 9)
    c = r.randint(10, 20)
    return (f"var xs = {lit(xs)};\nvar rv = xs.reversed;\nxs.add({c});\nprint(rv.first);", c,
            "reversed is a view of xs, so it already includes the item added afterwards.")


def i_join(r):
    xs = _xs(r, 4, 1, 9)
    return (f"print({lit(xs)}.map((x) => x.toString()).join('+'));", "+".join(map(str, xs)), "Each number becomes text and join glues them with +.")


def i_digits(r):
    xs = ints(r, 3, 1, 9)
    return (f"print({lit(xs)}.fold<int>(0, (s, x) => s * 10 + x));", xs[0] * 100 + xs[1] * 10 + xs[2],
            "Each step shifts what is built one place left and adds the digit: 3 digits make one number.")


def i_product(r):
    xs = ints(r, 4, 1, 6)
    p = 1
    for x in xs:
        p *= x
    return (f"print({lit(xs)}.fold<int>(1, (p, x) => p * x));", p, "fold starts at 1 and multiplies by every item.")


def i_reduce_minus(r):
    xs = ints(r, 3, 1, 20)
    return (f"print({lit(xs)}.reduce((a, b) => a - b));", xs[0] - xs[1] - xs[2],
            "reduce goes left to right: first a - b, then that result minus the next item.")


def i_fold_max(r):
    xs = _xs(r, 5)
    return (f"print({lit(xs)}.fold<int>(0, (m, x) => x > m ? x : m));", max(xs), "fold keeps the biggest seen so far.")


def i_first_or_null(r):
    xs = _xs(r, 4)
    return (f"var xs = {lit(xs)};\nprint(xs.where((x) => x > 100).firstOrNull);", None,
            "Nothing passes the test, so firstOrNull gives null instead of failing.")


def i_first_or_default(r):
    xs = _xs(r, 4)
    t = max(xs) - 1
    return (f"var xs = {lit(xs)};\nprint(xs.where((x) => x > {t}).firstOrNull ?? -1);", max(xs),
            "Only the biggest passes; ?? would give -1 only if nothing did.")


def i_generate(r):
    n, k = r.randint(3, 5), r.randint(2, 4)
    return (f"print(Iterable.generate({n}, (i) => i * {k}).toList());", [i * k for i in range(n)],
            "generate calls the function for 0, 1, 2 ... and collects the results.")


def i_generate_state(r):
    return ("var i = 0;\nvar it = Iterable.generate(3, (_) => i++);\nit.toList();\nprint(it.toList());", [3, 4, 5],
            "The function runs again for each toList(): i is 0, 1, 2 the first time and 3, 4, 5 the second.")


def i_generate_count(r):
    return ("var i = 0;\nvar it = Iterable.generate(3, (_) => i++);\nit.toList();\nit.toList();\nprint(i);", 6,
            "Each toList() runs the function three times.")


def i_indexed(r):
    xs = ints(r, 3, 1, 9)
    return (f"print({lit(xs)}.indexed.map((e) => e.$1 * e.$2).toList());", [i * x for i, x in enumerate(xs)],
            "indexed pairs each item with its position: the first field of the pair is the position, the second the item.")


def i_toset_mod(r):
    xs = _xs(r, 6)
    k = r.randint(2, 4)
    return (f"print({lit(xs)}.map((x) => x % {k}).toSet().length);", len({x % k for x in xs}),
            "Count the different remainders; the set keeps each once.")


def i_chain_order(r):
    xs = _xs(r, 5)
    t = r.randint(8, 18)
    return (f"var xs = {lit(xs)};\nprint(xs.where((x) => x > {t}).map((x) => x - {t}).toList());", [x - t for x in xs if x > t],
            "Filter first, then subtract: the subtraction only sees the items that passed.")


def i_chain_order2(r):
    xs = _xs(r, 5)
    t = r.randint(8, 18)
    return (f"var xs = {lit(xs)};\nprint(xs.map((x) => x - {t}).where((x) => x > 0).toList());", [x - t for x in xs if x - t > 0],
            "Subtract first, then keep only the positive results.")


def i_skip_first(r):
    xs = _xs(r, 5)
    s = r.randint(1, 3)
    return (f"var xs = {lit(xs)};\nprint(xs.skip({s}).first);", xs[s], "skip(n).first is the item at position n.")


def i_take_last(r):
    xs = _xs(r, 5)
    t = r.randint(2, 4)
    return (f"var xs = {lit(xs)};\nprint(xs.take({t}).last);", xs[t - 1], "take(n) keeps n items; last is the nth.")


def i_take_over(r):
    xs = _xs(r, 4)
    return (f"print({lit(xs)}.take(100).length);", 4, "take(100) of a 4-item list just gives all four.")


def i_skip_over(r):
    xs = _xs(r, 4)
    return (f"print({lit(xs)}.skip(100).toList());", [], "Skipping more than there are leaves nothing.")


def i_even_sum(r):
    xs = _xs(r, 6)
    while not any(x % 2 == 0 for x in xs):
        xs = _xs(r, 6)
    return (f"print({lit(xs)}.where((x) => x.isEven).map((x) => x ~/ 2).reduce((a, b) => a + b));", sum(x // 2 for x in xs if x % 2 == 0),
            "Keep the even items, halve each, add them up.")


def i_every_empty(r):
    return ("print(<int>[].every((x) => x > 5));", True, "every is true for an empty list: no item fails.")


def i_any_empty(r):
    return ("print(<int>[].any((x) => x > 5));", False, "any is false for an empty list: no item passes.")


def i_letters(r):
    w = words(r, 1)[0]
    return (f"print('{w}'.split('').map((c) => c.toUpperCase()).take(3).join());", w[:3].upper(),
            "Upper-case every letter, keep the first three, glue them together.")


def i_iterator(r):
    xs = _xs(r, 4)
    return (f"var it = {lit(xs)}.iterator;\nit.moveNext();\nit.moveNext();\nprint(it.current);", xs[1],
            "Each moveNext() steps to the next item; after two steps current is the second.")


def i_iterator_count(r):
    xs = _xs(r, r.randint(3, 6))
    return (f"var it = {lit(xs)}.where((x) => x.isEven).iterator;\nvar c = 0;\nwhile (it.moveNext()) {{\n  c++;\n}}\nprint(c);",
            sum(1 for x in xs if x % 2 == 0), "The loop steps once for every even item.")


def i_bools(r):
    xs = _xs(r, 3)
    t = r.choice(xs)
    return (f"print({lit(xs)}.map((x) => x > {t}));", DIter(x > t for x in xs), LAZY)


def i_bools_list(r):
    xs = _xs(r, 3)
    t = r.choice(xs)
    return (f"print({lit(xs)}.map((x) => x > {t}).toList());", [x > t for x in xs], "A list of true and false answers, one per item.")


def i_list_from(r):
    xs = _xs(r, 5)
    t = r.randint(8, 18)
    return (f"print(List.from({lit(xs)}.where((x) => x > {t})));", [x for x in xs if x > t],
            "List.from makes a real list at once, so it prints in square brackets, not round ones.")


def i_set_from(r):
    xs = _xs(r, 4, 1, 9)
    return (f"print(Set.from({lit(xs)}.map((x) => x % 3)));", DSet(x % 3 for x in xs), "A set of the remainders, each once, in curly brackets.")


def i_cast(r):
    xs = ints(r, 3, 1, 9)
    return (f"print(<Object>{lit(xs)}.cast<int>().reduce((x, y) => x + y));", sum(xs),
            "The list holds ints only, so cast<int>() works and the items can be added.")


def i_sublist_take(r):
    xs = _xs(r, 6)
    return (f"print({lit(xs)}.sublist(2).take(2).toList());", xs[2:][:2], "sublist(2) drops two items, take(2) keeps the next two.")


def i_takewhile_idx(r):
    xs = _xs(r, 6)
    t = r.choice(xs)
    return (f"print({lit(xs)}.takeWhile((x) => x != {t}).length);", xs.index(t), "The items before t: its position, counting from 0.")


def i_where_isempty(r):
    xs = _xs(r, 4, 1, 9)
    return (f"print({lit(xs)}.where((x) => x > 9).isEmpty);", True, "No item is bigger than 9, so the filtered result is empty.")


def i_mapped_contains(r):
    xs = ints(r, 3, 1, 9)
    k = 2
    t = r.choice([x * k for x in xs] + [r.randint(10, 20)])
    return (f"print({lit(xs)}.map((x) => x * {k}).contains({t}));", t in [x * k for x in xs],
            "contains asks whether any of the doubled items equals the number.")


ITERS: list[Maker] = [R(f) for f in (
    i_where_len, i_map_list, i_map_lazy, i_where_lazy, i_where_last, i_where_first, i_skip_take, i_take_skip,
    i_takewhile, i_takewhile_lt, i_skipwhile, i_takewhile_lazy, i_expand, i_expand_take, i_expand_len, i_followed,
    i_followed_lazy, i_wheretype_ints, i_wheretype_str, i_wheretype_len, i_single, i_elementat, i_elementat_map,
    i_calls_twice, i_calls_none, i_calls_first, i_calls_take, i_calls_where_first, i_calls_any, i_calls_every,
    i_view_later, i_copy_later, i_reversed_view, i_join, i_digits, i_product, i_reduce_minus, i_fold_max,
    i_first_or_null, i_first_or_default, i_generate, i_generate_state, i_generate_count, i_indexed, i_toset_mod,
    i_chain_order, i_chain_order2, i_skip_first, i_take_last, i_take_over, i_skip_over, i_even_sum, i_every_empty,
    i_any_empty, i_letters, i_iterator, i_iterator_count, i_bools, i_bools_list, i_list_from, i_set_from, i_cast,
    i_sublist_take, i_takewhile_idx, i_where_isempty, i_mapped_contains)]
