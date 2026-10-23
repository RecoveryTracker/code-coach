"""Dart data pack, part 6: Map Moves - putIfAbsent, update, updateAll, remove, entries, fold, sorting by key or value.

A Dart map made with `{...}` keeps the order its keys were first added (a LinkedHashMap), so printing it, listing its
keys and walking its entries are all predictable. A key that is overwritten keeps its place; a key that is removed
and added again goes to the end. Python's dict has the same rules, which is how the answers are modelled.
"""

from __future__ import annotations

import random

from ._dartdata_model import DIter, R, ints, words
from ._model import Maker


def _src(m: dict) -> str:
    """A map literal in Dart: {'farm': 3, 'key': 5}."""
    return "{" + ", ".join(f"'{k}': {v}" for k, v in m.items()) + "}"


def _mk(r: random.Random, n: int = 3, lo: int = 1, hi: int = 9, distinct: bool = True) -> dict:
    ks = words(r, n)
    vs = ints(r, n, lo, hi) if distinct else [r.randint(lo, hi) for _ in range(n)]
    return dict(zip(ks, vs))


def _other(r: random.Random, m: dict) -> str:
    return r.choice([w for w in ("lamp", "robot", "stone", "river", "cloud", "brick", "maple", "wheat") if w not in m])


def m_pia_value_new(r):
    m = _mk(r)
    k = _other(r, m)
    v = r.randint(10, 40)
    return f"var m = {_src(m)};\nprint(m.putIfAbsent('{k}', () => {v}));", v, "A missing key is added, and putIfAbsent returns the new value."


def m_pia_value_old(r):
    m = _mk(r)
    k = r.choice(list(m))
    return f"var m = {_src(m)};\nprint(m.putIfAbsent('{k}', () => 99));", m[k], "The key is already there: nothing changes and the OLD value is returned."


def m_pia_map(r):
    m = _mk(r, 2)
    k = _other(r, m)
    v = r.randint(10, 40)
    out = {**m, k: v}
    return f"var m = {_src(m)};\nm.putIfAbsent('{k}', () => {v});\nprint(m);", out, "The new key goes at the end of the map."


def m_pia_keep(r):
    m = _mk(r, 2)
    k = r.choice(list(m))
    return f"var m = {_src(m)};\nm.putIfAbsent('{k}', () => 99);\nprint(m['{k}']);", m[k], "putIfAbsent never overwrites an existing key."


def m_assign_keep(r):
    m = _mk(r, 3)
    k = list(m)[0]
    v = r.randint(10, 40)
    m2 = dict(m)
    m2[k] = v
    return f"var m = {_src(m)};\nm['{k}'] = {v};\nprint(m.keys.toList());", list(m2), "Overwriting a value keeps the key where it was."


def m_remove_readd(r):
    m = _mk(r, 3)
    k = list(m)[0]
    m2 = dict(m)
    del m2[k]
    m2[k] = 1
    return f"var m = {_src(m)};\nm.remove('{k}');\nm['{k}'] = 1;\nprint(m.keys.toList());", list(m2), "A removed key that is added again is a new entry, so it goes last."


def m_update(r):
    m = _mk(r, 3)
    k = r.choice(list(m))
    n = r.randint(2, 4)
    m2 = dict(m)
    m2[k] = m[k] * n
    return f"var m = {_src(m)};\nm.update('{k}', (v) => v * {n});\nprint(m);", m2, "update replaces the value with the function's result, using the old value."


def m_update_absent(r):
    m = _mk(r, 2)
    k = _other(r, m)
    v = r.randint(10, 40)
    return (f"var m = {_src(m)};\nm.update('{k}', (v) => v + 1, ifAbsent: () => {v});\nprint(m['{k}']);", v,
            "The key is missing, so ifAbsent supplies the value and the update function is not used.")


def m_update_present(r):
    m = _mk(r, 2)
    k = r.choice(list(m))
    v = r.randint(10, 40)
    return (f"var m = {_src(m)};\nm.update('{k}', (v) => v + 1, ifAbsent: () => {v});\nprint(m['{k}']);", m[k] + 1,
            "The key exists, so the update function runs and ifAbsent is ignored.")


def m_updateall(r):
    m = _mk(r, 3)
    n = r.randint(10, 20)
    return (f"var m = {_src(m)};\nm.updateAll((k, v) => v + {n});\nprint(m);", {k: v + n for k, v in m.items()}, "updateAll changes every value.")


def m_updateall_key(r):
    m = _mk(r, 3)
    return (f"var m = {_src(m)};\nm.updateAll((k, v) => k.length * v);\nprint(m.values.toList());", [len(k) * v for k, v in m.items()],
            "The function sees each key and value; here the key's length times the value.")


def m_remove_value(r):
    m = _mk(r, 3)
    k = r.choice(list(m))
    return f"var m = {_src(m)};\nprint(m.remove('{k}'));", m[k], "remove returns the value it took out."


def m_remove_absent(r):
    m = _mk(r, 3)
    k = _other(r, m)
    return f"var m = {_src(m)};\nprint(m.remove('{k}'));", None, "A missing key: remove returns null."


def m_remove_len(r):
    m = _mk(r, 3)
    k, j = r.sample(list(m), 2)
    return f"var m = {_src(m)};\nm.remove('{k}');\nm.remove('{j}');\nprint(m.length);", 1, "Two of the three pairs are gone."


def m_removewhere(r):
    m = _mk(r, 4)
    return (f"var m = {_src(m)};\nm.removeWhere((k, v) => v.isOdd);\nprint(m.keys.toList());", [k for k, v in m.items() if v % 2 == 0],
            "removeWhere deletes every pair whose test is true.")


def m_contains_key(r):
    m = _mk(r, 3)
    k = r.choice(list(m) + [_other(r, m)])
    return f"var m = {_src(m)};\nprint(m.containsKey('{k}'));", k in m, "containsKey looks at the keys only."


def m_contains_value(r):
    m = _mk(r, 3)
    v = r.choice(list(m.values()) + [r.randint(10, 40)])
    return f"var m = {_src(m)};\nprint(m.containsValue({v}));", v in m.values(), "containsValue looks at the values only."


def m_contains_swap(r):
    m = _mk(r, 3)
    k = r.choice(list(m))
    return f"var m = {_src(m)};\nprint(m.containsKey({m[k]}));", False, "The number is a value, not a key, and the keys are strings."


def m_missing(r):
    m = _mk(r, 3)
    k = _other(r, m)
    return f"var m = {_src(m)};\nprint(m['{k}']);", None, "A missing key gives null."


def m_missing_default(r):
    m = _mk(r, 3)
    k = _other(r, m)
    d = r.randint(10, 40)
    return f"var m = {_src(m)};\nprint(m['{k}'] ?? {d});", d, "?? takes the right side when the lookup is null."


def m_missing_plus(r):
    m = _mk(r, 3)
    k = _other(r, m)
    n = r.randint(2, 9)
    return f"var m = {_src(m)};\nm['{k}'] = (m['{k}'] ?? 0) + {n};\nprint(m['{k}']);", n, "A new key starts from 0, then n is added."


def m_nullassign(r):
    m = _mk(r, 2)
    k = _other(r, m)
    v = r.randint(10, 40)
    return f"var m = {_src(m)};\nm['{k}'] ??= {v};\nprint(m);", {**m, k: v}, "??= stores the value only when the entry is null (here it is missing)."


def m_nullassign_keep(r):
    m = _mk(r, 2)
    k = r.choice(list(m))
    return f"var m = {_src(m)};\nm['{k}'] ??= 99;\nprint(m['{k}']);", m[k], "The entry already has a value, so ??= does nothing."


def m_entries_join(r):
    m = _mk(r, 3)
    return (f"var m = {_src(m)};\nprint(m.entries.map((e) => '${{e.key}}:${{e.value}}').join(' '));", " ".join(f"{k}:{v}" for k, v in m.items()),
            "Each entry has a key and a value; join glues the texts.")


def m_fold(r):
    m = _mk(r, 3)
    return f"var m = {_src(m)};\nprint(m.values.fold<int>(0, (s, v) => s + v));", sum(m.values()), "fold adds up all the values."


def m_fold_keys(r):
    m = _mk(r, 3)
    return f"var m = {_src(m)};\nprint(m.keys.fold<int>(0, (s, k) => s + k.length));", sum(len(k) for k in m), "Add up the lengths of the keys."


def m_keys_lazy(r):
    m = _mk(r, 3)
    return f"var m = {_src(m)};\nprint(m.keys);", DIter(m), "keys is an Iterable, so print shows round brackets."


def m_values_list(r):
    m = _mk(r, 3)
    return f"var m = {_src(m)};\nprint(m.values.toList());", list(m.values()), "The values, in the order the keys were added."


def m_first_key(r):
    m = _mk(r, 3)
    return f"var m = {_src(m)};\nprint(m.keys.first);", next(iter(m)), "A map remembers the order its keys were added."


def m_last_value(r):
    m = _mk(r, 3)
    return f"var m = {_src(m)};\nprint(m.values.last);", list(m.values())[-1], "The last key added holds the last value."


def m_key_index(r):
    m = _mk(r, 3)
    k = r.choice(list(m))
    return f"var m = {_src(m)};\nprint(m.keys.toList().indexOf('{k}'));", list(m).index(k), "The position of the key in insertion order."


def m_entry_at(r):
    m = _mk(r, 3)
    i = r.randint(0, 2)
    k = list(m)[i]
    return f"var m = {_src(m)};\nprint(m.entries.toList()[{i}].value);", m[k], "entries in insertion order; the entry at that position has its own value."


def m_from_copy(r):
    m = _mk(r, 2)
    k = _other(r, m)
    return f"var m = {_src(m)};\nvar c = Map.from(m);\nc['{k}'] = 1;\nprint(m.length);", 2, "Map.from makes a copy: adding to c does not touch m."


def m_alias(r):
    m = _mk(r, 2)
    k = _other(r, m)
    return f"var m = {_src(m)};\nvar c = m;\nc['{k}'] = 1;\nprint(m.length);", 3, "c is the same map as m, so the added key shows in both."


def m_spread_copy(r):
    m = _mk(r, 3)
    k = list(m)[0]
    return f"var m = {_src(m)};\nvar c = {{...m}};\nc.remove('{k}');\nprint(m.length);", 3, "The spread made a separate copy; removing from c leaves m alone."


def m_sort_by_key(r):
    m = _mk(r, 3)
    return (f"var m = {_src(m)};\nvar s = Map.fromEntries(m.entries.toList()..sort((a, b) => a.key.compareTo(b.key)));\nprint(s);",
            dict(sorted(m.items())), "Sort the entries by key, then build a new map from them: it keeps that order.")


def m_sort_by_value(r):
    m = _mk(r, 3)
    return (f"var m = {_src(m)};\nvar s = Map.fromEntries(m.entries.toList()..sort((a, b) => a.value.compareTo(b.value)));\nprint(s.keys.toList());",
            [k for k, v in sorted(m.items(), key=lambda t: t[1])], "The keys in order of their values, smallest first.")


def m_invert(r):
    m = _mk(r, 3)
    return f"var m = {_src(m)};\nprint(m.map((k, v) => MapEntry(v, k)));", {v: k for k, v in m.items()}, "map builds a new map; here every key and value swap places."


def m_map_double(r):
    m = _mk(r, 3)
    n = r.randint(2, 5)
    return f"var m = {_src(m)};\nprint(m.map((k, v) => MapEntry(k, v * {n})));", {k: v * n for k, v in m.items()}, "A new map with every value multiplied."


def m_where_keys(r):
    m = _mk(r, 4)
    t = sorted(m.values())[1]
    return (f"var m = {_src(m)};\nprint(m.entries.where((e) => e.value > {t}).map((e) => e.key).toList());", [k for k, v in m.items() if v > t],
            "Keep the entries whose value is above the limit, then take their keys.")


def m_reverse_lookup(r):
    m = _mk(r, 3)
    k = r.choice(list(m))
    return f"var m = {_src(m)};\nprint(m.entries.firstWhere((e) => e.value == {m[k]}).key);", k, "Search the entries for the value and give the key it belongs to."


def m_max_value(r):
    m = _mk(r, 4)
    return f"var m = {_src(m)};\nprint(m.values.reduce((a, b) => a > b ? a : b));", max(m.values()), "Keep the bigger value at each step."


def m_foreach(r):
    m = _mk(r, 3)
    return f"var m = {_src(m)};\nvar t = 0;\nm.forEach((k, v) {{\n  t += v;\n}});\nprint(t);", sum(m.values()), "forEach visits every pair; t adds up the values."


def m_foreach_len(r):
    m = _mk(r, 3)
    return f"var m = {_src(m)};\nvar t = '';\nm.forEach((k, v) {{\n  t += k[0];\n}});\nprint(t);", "".join(k[0] for k in m), "The first letters of the keys, in insertion order."


def m_addall(r):
    m = _mk(r, 2)
    k = list(m)[0]
    n = _other(r, m)
    v = r.randint(10, 40)
    out = dict(m)
    out[k] = 0
    out[n] = v
    return f"var m = {_src(m)};\nm.addAll({{'{k}': 0, '{n}': {v}}});\nprint(m);", out, "addAll overwrites the keys it shares and appends the new ones."


def m_addentries(r):
    m = _mk(r, 2)
    n = _other(r, m)
    v = r.randint(10, 40)
    return f"var m = {_src(m)};\nm.addEntries([MapEntry('{n}', {v})]);\nprint(m.length);", 3, "addEntries adds the entry as a new pair."


def m_clear(r):
    m = _mk(r, 3)
    return f"var m = {_src(m)};\nm.clear();\nprint(m.isEmpty);", True, "clear removes every pair."


def m_count_letters(r):
    w = r.choice(["carrot", "robot", "array", "loop", "seed", "tree", "pumpkin", "corn", "barn", "maple", "wheat"])
    out: dict = {}
    for ch in w:
        out[ch] = out.get(ch, 0) + 1
    return (f"var m = <String, int>{{}};\nfor (var ch in '{w}'.split('')) {{\n  m[ch] = (m[ch] ?? 0) + 1;\n}}\nprint(m);", out,
            "A tally: each letter's count goes up by one, and the keys keep their first-seen order.")


def m_count_letter_max(r):
    w = r.choice(["carrot", "robot", "array", "loop", "seed", "tree", "pumpkin"])
    out: dict = {}
    for ch in w:
        out[ch] = out.get(ch, 0) + 1
    return (f"var m = <String, int>{{}};\nfor (var ch in '{w}'.split('')) {{\n  m.update(ch, (v) => v + 1, ifAbsent: () => 1);\n}}\nprint(m.values.reduce((a, b) => a > b ? a : b));", max(out.values()),
            "update with ifAbsent counts the letters; the biggest count is the answer.")


def m_group(r):
    ws = r.sample(["farm", "loop", "code", "drone", "array", "wheat", "key", "carrot", "seed"], 4)
    g: dict = {}
    for w in ws:
        g.setdefault(len(w), []).append(w)
    return (f"var g = <int, List<String>>{{}};\nfor (var w in {_lit_list(ws)}) {{\n  g.putIfAbsent(w.length, () => []).add(w);\n}}\nprint(g.values.toList());", list(g.values()),
            "Words are grouped by length: putIfAbsent makes the group's list the first time and add fills it.")


def _lit_list(ws: list[str]) -> str:
    return "[" + ", ".join(f"'{w}'" for w in ws) + "]"


def m_nested_set(r):
    k, a, b = r.choice(["farm", "loop", "code"]), r.randint(1, 9), r.randint(10, 40)
    return f"var m = {{'{k}': {{'x': {a}}}}};\nm['{k}']!['x'] = {b};\nprint(m);", {k: {"x": b}}, "m[key]! is the inner map itself, so the change shows inside m."


def m_nested_missing(r):
    k = r.choice(["farm", "loop", "code"])
    return f"var m = {{'{k}': {{'x': 1}}}};\nprint(m['{k}']?['y']);", None, "The inner map has no y, so the lookup gives null."


def m_nested_null(r):
    k, j = r.sample(["farm", "loop", "code", "seed"], 2)
    return f"var m = {{'{k}': {{'x': 1}}}};\nprint(m['{j}']?['x']);", None, "m has no such key, so ?[ stops and the whole thing is null instead of failing."


def m_list_value(r):
    k = r.choice(["farm", "loop", "code"])
    a, b = r.sample(range(2, 10), 2)
    return f"var m = {{'{k}': [{a}]}};\nm['{k}']!.add({b});\nprint(m);", {k: [a, b]}, "The value is a list, and add changes that very list."


def m_from_iterable(r):
    xs = ints(r, 3, 1, 9)
    return f"print(Map.fromIterable({_ilist(xs)}, key: (x) => x, value: (x) => x * x));", {x: x * x for x in xs}, "Each item becomes a key, and the function gives its value."


def _ilist(xs: list[int]) -> str:
    return "[" + ", ".join(map(str, xs)) + "]"


def m_length_after(r):
    m = _mk(r, 3)
    k = _other(r, m)
    return f"var m = {_src(m)};\nm['{k}'] = 1;\nm['{k}'] = 2;\nprint(m.length);", 4, "The same key twice is one pair: 3 + 1."


def m_isnotempty(r):
    m = _mk(r, 2)
    k, j = list(m)
    return f"var m = {_src(m)};\nm.remove('{k}');\nprint(m.isNotEmpty);", True, "One pair is still left."


MAPS: list[Maker] = [R(f) for f in (
    m_pia_value_new, m_pia_value_old, m_pia_map, m_pia_keep, m_assign_keep, m_remove_readd, m_update,
    m_update_absent, m_update_present, m_updateall, m_updateall_key, m_remove_value, m_remove_absent, m_remove_len,
    m_removewhere, m_contains_key, m_contains_value, m_contains_swap, m_missing, m_missing_default, m_missing_plus,
    m_nullassign, m_nullassign_keep, m_entries_join, m_fold, m_fold_keys, m_keys_lazy, m_values_list, m_first_key,
    m_last_value, m_key_index, m_entry_at, m_from_copy, m_alias, m_spread_copy, m_sort_by_key, m_sort_by_value,
    m_invert, m_map_double, m_where_keys, m_reverse_lookup, m_max_value, m_foreach, m_foreach_len, m_addall,
    m_addentries, m_clear, m_count_letters, m_count_letter_max, m_group, m_nested_set, m_nested_missing,
    m_nested_null, m_list_value, m_from_iterable, m_length_after, m_isnotempty)]
