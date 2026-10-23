"""Dart data pack, part 3: Sort & Compare - `sort`, comparators, `compareTo` and what stays unsorted.

`xs.sort()` sorts IN PLACE and returns nothing (there is no `sorted`); strings compare by code unit, so every capital
letter sorts before every small one and "100" sorts before "9". Every random list has no ties (no two items compare
equal), so the order does not depend on whether the sort is stable.
"""

from __future__ import annotations

import random

from ._dartdata_model import R, distinct_length_words, ints, lit, sign, words
from ._model import Maker

INPLACE = "sort works in place: the list itself is reordered and nothing is returned."


def _caps(r: random.Random, ws: list[str]) -> list[str]:
    """Capitalise some of the words (and always at least one)."""
    out = [w.capitalize() if r.random() < 0.4 else w for w in ws]
    if all(w[0].islower() for w in out):
        i = r.randrange(len(out))
        out[i] = out[i].capitalize()
    return out


def o_sort_up(r):
    xs = ints(r, 5)
    return f"var xs = {lit(xs)};\nxs.sort();\nprint(xs);", sorted(xs), INPLACE


def o_sort_down(r):
    xs = ints(r, 5)
    return (f"var xs = {lit(xs)};\nxs.sort((a, b) => b.compareTo(a));\nprint(xs);", sorted(xs, reverse=True),
            "The comparator b.compareTo(a) is the normal order turned round: biggest first.")


def o_sort_minus(r):
    xs = ints(r, 5)
    return (f"var xs = {lit(xs)};\nxs.sort((a, b) => a - b);\nprint(xs);", sorted(xs),
            "a - b is negative when a belongs first: that is increasing order.")


def o_sort_minus_down(r):
    xs = ints(r, 5)
    return (f"var xs = {lit(xs)};\nxs.sort((a, b) => b - a);\nprint(xs);", sorted(xs, reverse=True),
            "b - a is negative when b is the smaller one, so the bigger a goes first.")


def o_first(r):
    xs = ints(r, 5)
    return f"var xs = {lit(xs)};\nxs.sort();\nprint(xs.first);", min(xs), "After sorting, first is the smallest."


def o_last(r):
    xs = ints(r, 5)
    return f"var xs = {lit(xs)};\nxs.sort();\nprint(xs.last);", max(xs), "After sorting, last is the biggest."


def o_second(r):
    xs = ints(r, 5)
    return f"var xs = {lit(xs)};\nxs.sort();\nprint(xs[1]);", sorted(xs)[1], "Position 1 is the second smallest."


def o_median(r):
    xs = ints(r, 5)
    return (f"var xs = {lit(xs)};\nxs.sort();\nprint(xs[xs.length ~/ 2]);", sorted(xs)[2],
            "Five items: 5 ~/ 2 is 2, the middle position of the sorted list.")


def o_range(r):
    xs = ints(r, 5)
    return f"var xs = {lit(xs)};\nxs.sort();\nprint(xs.last - xs.first);", max(xs) - min(xs), "Biggest minus smallest."


def o_two_smallest(r):
    xs = ints(r, 5)
    return f"var xs = {lit(xs)};\nxs.sort();\nprint(xs.take(2).toList());", sorted(xs)[:2], "After sorting, the first two are the smallest."


def o_two_biggest(r):
    xs = ints(r, 5)
    return (f"var xs = {lit(xs)};\nxs.sort((a, b) => b - a);\nprint(xs.take(2).toList());", sorted(xs, reverse=True)[:2],
            "Sorted biggest first, the first two are the biggest.")


def o_reversed_list(r):
    xs = ints(r, 4)
    return f"var xs = {lit(xs)};\nprint(xs.reversed.toList());", xs[::-1], "reversed turns the order round without sorting."


def o_sort_reversed(r):
    xs = ints(r, 4)
    return (f"var xs = {lit(xs)};\nxs.sort();\nprint(xs.reversed.toList());", sorted(xs, reverse=True),
            "Sort first, then read it backwards: biggest first.")


def o_sort_then_idx(r):
    xs = ints(r, 5)
    v = r.choice(xs)
    return (f"var xs = {lit(xs)};\nxs.sort();\nprint(xs.indexOf({v}));", sorted(xs).index(v),
            "indexOf finds the position in the SORTED list: how many items are smaller.")


def o_copy_sort(r):
    xs = ints(r, 4)
    return (f"var xs = {lit(xs)};\nvar ys = [...xs]..sort();\nprint(xs);", xs, "ys is a sorted copy; xs itself was never sorted.")


def o_alias_sort(r):
    xs = ints(r, 4)
    return (f"var xs = {lit(xs)};\nvar ys = xs..sort();\nprint(xs);", sorted(xs), "The cascade sorts xs itself and ys is just another name for it.")


def o_strings(r):
    ws = _caps(r, words(r, 4))
    return f"var ws = {lit(ws)};\nws.sort();\nprint(ws);", sorted(ws), "Strings compare by code unit: every capital letter sorts before every small one."


def o_strings_plain(r):
    ws = words(r, 4)
    return f"var ws = {lit(ws)};\nws.sort();\nprint(ws.first);", min(ws), "Alphabetical order: the first word is the one that comes first in a dictionary."


def o_strings_down(r):
    ws = words(r, 4)
    return (f"var ws = {lit(ws)};\nws.sort((a, b) => b.compareTo(a));\nprint(ws);", sorted(ws, reverse=True),
            "b.compareTo(a) reverses the alphabet.")


def o_by_length(r):
    ws = distinct_length_words(r, 4)
    return (f"var ws = {lit(ws)};\nws.sort((a, b) => a.length - b.length);\nprint(ws);", sorted(ws, key=len),
            "The comparator looks only at the lengths: shortest first.")


def o_by_length_desc(r):
    ws = distinct_length_words(r, 3)
    return (f"var ws = {lit(ws)};\nws.sort((a, b) => b.length.compareTo(a.length));\nprint(ws.first);", max(ws, key=len),
            "Longest first, so the first word is the longest.")


def o_numeric_strings(r):
    pool = r.sample(range(2, 10), 2) + r.sample(range(10, 30), 2) + r.sample(range(100, 150), 1)
    ss = [str(x) for x in pool]
    return (f"var xs = {lit(ss)};\nxs.sort();\nprint(xs);", sorted(ss),
            "Strings are compared character by character, not as numbers: '100' comes before '9'.")


def o_numeric_strings_first(r):
    pool = r.sample(range(2, 10), 2) + r.sample(range(10, 30), 2) + r.sample(range(100, 150), 1)
    ss = [str(x) for x in pool]
    return (f"var xs = {lit(ss)};\nxs.sort();\nprint(xs.last);", max(ss),
            "The last string in text order, which is not always the biggest number.")


def o_numeric_strings_as_int(r):
    pool = r.sample(range(2, 10), 2) + r.sample(range(10, 30), 2) + r.sample(range(100, 150), 1)
    ss = [str(x) for x in pool]
    return (f"var xs = {lit(ss)};\nxs.sort((a, b) => int.parse(a).compareTo(int.parse(b)));\nprint(xs);", sorted(ss, key=int),
            "Parsing inside the comparator sorts by number value.")


def o_length_then_alpha(r):
    ws = r.sample(["farm", "loop", "code", "grid", "tree", "seed", "corn", "barn", "lamp", "drone", "array", "wheat", "key", "carrot"], 5)
    return (f"var ws = {lit(ws)};\nws.sort((a, b) {{\n  var c = a.length.compareTo(b.length);\n  return c != 0 ? c : a.compareTo(b);\n}});\nprint(ws);",
            sorted(ws, key=lambda w: (len(w), w)), "Shorter words first; words of the same length fall back to alphabetical order.")


def o_cmp_ints(r):
    a, b = ints(r, 2, 1, 30)
    return f"print({a}.compareTo({b}));", sign(a - b), "compareTo gives -1 when the first is smaller, 1 when it is bigger and 0 when equal."


def o_cmp_equal(r):
    a = r.randint(1, 30)
    return f"print({a}.compareTo({a}));", 0, "Equal numbers compare as 0."


def o_comparable(r):
    a, b = ints(r, 2, 1, 30)
    return f"print(Comparable.compare({a}, {b}));", sign(a - b), "Comparable.compare(a, b) is the same as a.compareTo(b)."


def o_cmp_strings(r):
    w, v = words(r, 2)
    w2 = w.capitalize() if r.random() < 0.5 else w
    return (f"print('{w2}'.compareTo('{v}') < 0);", w2 < v, "Compare by code unit: a capital letter is smaller than any small letter.")


def o_cmp_prefix(r):
    return "print('app'.compareTo('apple') < 0);", True, "A shorter text that is a prefix of the other sorts first."


def o_cmp_case(r):
    w = words(r, 1)[0]
    return f"print('{w.capitalize()}'.compareTo('{w}') < 0);", True, "The capital letter has the smaller code unit, so it sorts first."


def o_abs(r):
    base = ints(r, 4, 1, 20)
    xs = [x if r.random() < 0.5 else -x for x in base]
    return (f"var xs = {lit(xs)};\nxs.sort((a, b) => a.abs().compareTo(b.abs()));\nprint(xs);", sorted(xs, key=abs),
            "Sorting by absolute value, the signs do not matter for the order.")


def o_last_digit(r):
    digits = r.sample(range(10), 4)
    xs = [d + 10 * r.randint(0, 9) for d in digits]
    return (f"var xs = {lit(xs)};\nxs.sort((a, b) => (a % 10).compareTo(b % 10));\nprint(xs);", sorted(xs, key=lambda x: x % 10),
            "The comparator looks only at the last digit.")


def o_even_first(r):
    xs = ints(r, 5, 1, 20)
    return (f"var xs = {lit(xs)};\nxs.sort((a, b) {{\n  if (a.isEven != b.isEven) return a.isEven ? -1 : 1;\n  return a - b;\n}});\nprint(xs);",
            sorted(xs, key=lambda x: (x % 2, x)), "Even numbers come first; inside each group the smaller number goes first.")


def o_doubles(r):
    xs = [k / 4 for k in r.sample(range(1, 40), 4)]
    return f"var xs = {lit(xs)};\nxs.sort();\nprint(xs);", sorted(xs), "Doubles sort by value; whole ones still print with .0."


def o_unique_sorted(r):
    xs = ints(r, 3, 1, 9)
    xs = xs + [xs[0], xs[1]]
    r.shuffle(xs)
    return (f"var xs = {lit(xs)};\nprint(xs.toSet().toList()..sort());", sorted(set(xs)),
            "toSet drops the repeats, toList makes a list again, and the cascade sorts it.")


def o_pairs(r):
    ws = words(r, 3)
    ns = ints(r, 3, 1, 9)
    pairs = list(zip(ws, ns))
    src = ", ".join(f"('{w}', {n})" for w, n in pairs)
    return (f"var ps = [{src}];\nps.sort((x, y) => x.$2.compareTo(y.$2));\nprint(ps.map((p) => p.$1).join(' '));",
            " ".join(w for w, n in sorted(pairs, key=lambda t: t[1])), "The records are sorted by their second field; then the names are read in that order.")


def o_entries_top(r):
    ws = words(r, 3)
    ns = ints(r, 3, 1, 30)
    src = ", ".join(f"'{w}': {n}" for w, n in zip(ws, ns))
    return (f"var m = {{{src}}};\nvar es = m.entries.toList()..sort((a, b) => b.value.compareTo(a.value));\nprint(es.first.key);",
            max(zip(ws, ns), key=lambda t: t[1])[0], "Entries sorted by value, biggest first: the first one holds the biggest value.")


def o_keys_sorted(r):
    ws = words(r, 3)
    src = ", ".join(f"'{w}': {i}" for i, w in enumerate(ws))
    return f"var m = {{{src}}};\nvar ks = m.keys.toList()..sort();\nprint(ks);", sorted(ws), "A map keeps insertion order, so sort the list of keys to get alphabetical order."


def o_letters(r):
    w = words(r, 1)[0]
    return f"print(('{w}'.split('')..sort()).join());", "".join(sorted(w)), "Sort the letters, then glue them back together."


def o_max_reduce(r):
    xs = ints(r, 4)
    return f"print({lit(xs)}.reduce((a, b) => a.compareTo(b) > 0 ? a : b));", max(xs), "Keeping the bigger of each pair leaves the biggest."


def o_list_of_sort(r):
    xs = ints(r, 4)
    return f"print(List.of({lit(xs)})..sort());", sorted(xs), "The cascade sorts the copy and the expression is that list."


def o_map_after_sort(r):
    xs = ints(r, 4, 1, 9)
    return (f"var xs = {lit(xs)};\nxs.sort();\nprint(xs.map((x) => x * 2).toList());", [2 * x for x in sorted(xs)],
            "Sort first, then double each item.")


def o_sort_desc_idx(r):
    xs = ints(r, 5)
    v = r.choice(xs)
    return (f"var xs = {lit(xs)};\nxs.sort((a, b) => b - a);\nprint(xs.indexOf({v}));", sorted(xs, reverse=True).index(v),
            "The position of the number in the list sorted biggest first: how many are bigger.")


def o_rank(r):
    xs = ints(r, 5)
    v = r.choice(xs)
    return (f"var xs = {lit(xs)};\nprint(xs.where((x) => x < {v}).length);", sorted(xs).index(v),
            "Counting the smaller items gives the same number as the position in the sorted list.")


SORTS: list[Maker] = [R(f) for f in (
    o_sort_up, o_sort_down, o_sort_minus, o_sort_minus_down, o_first, o_last, o_second, o_median, o_range,
    o_two_smallest, o_two_biggest, o_reversed_list, o_sort_reversed, o_sort_then_idx, o_copy_sort, o_alias_sort,
    o_strings, o_strings_plain, o_strings_down, o_by_length, o_by_length_desc, o_numeric_strings,
    o_numeric_strings_first, o_numeric_strings_as_int, o_length_then_alpha, o_cmp_ints, o_cmp_equal, o_comparable,
    o_cmp_strings, o_cmp_prefix, o_cmp_case, o_abs, o_last_digit, o_even_first, o_doubles, o_unique_sorted, o_pairs,
    o_entries_top, o_keys_sorted, o_letters, o_max_reduce, o_list_of_sort, o_map_after_sort, o_sort_desc_idx, o_rank)]
