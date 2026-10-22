"""Collections Pack, JavaScript side: arrays, objects, Maps and Sets.

The same eight activities as the Python side - List After, How Many, Dict
Lookup, Set Maths, Min Max Sum, Unpack It, Nested Reach, Sort Order - with
JavaScript's own rules (push/splice/shift, the default sort that compares as
TEXT, `undefined` instead of an error, `??` and `?.`, Object.keys' odd order for
number-like keys, destructuring with defaults). Every answer is modelled by hand
on the same list-and-pair-list models as the Python side (see
`_collections_py.py`); tests/test_brain_packs.py runs every template through the
real node.
"""

from __future__ import annotations

import random
from typing import Callable

from ._collections_py import (best, d_get, d_has, d_merge, d_set, diff, drop, dupes, has, inter, ins,
                              nums, pairs, pos, sort_by, sym, take, total, uniq, union, words)
from ._model import NULL, UNDEF, WORDS, Maker, decimal_div, fmod, ints, js_show, lit
from .items import Item


def jb(v: bool) -> str:
    return "true" if v else "false"


def olit(d: list) -> str:
    """An object literal for a pair list: `{ farm: 3, drone: 5 }` (word keys, int or word values)."""
    return "{ " + ", ".join(f"{k}: {lit(v)}" for k, v in d) + " }" if d else "{}"


def jobj(d: list) -> dict:
    return {k: v for k, v in d}


def err_js(code: str) -> str:
    """An oracle program that runs the whole snippet in a function and gives the last line's value, or the
    name of the error if anything threw. Its last line is `_go()`, a whole expression (Run it prints that line)."""
    head, _, last = code.rpartition("\n")
    body = "".join("    " + line + "\n" for line in head.split("\n")) if head else ""
    return ("const _go = () => {\n  try {\n" + body + f"    return ({last.rstrip(';')});\n  }} catch (e) {{\n    return e.name;\n  }}\n}};\n_go()")


def _v(rng: random.Random) -> int:
    return rng.randint(1, 9)


def is_index_key(k: str) -> bool:
    """A key JavaScript treats as an array index: digits, no leading zero."""
    return k != "" and all("0" <= c <= "9" for c in k) and (k == "0" or k[0] != "0")


def js_key_order(keys: list[str]) -> list[str]:
    """Object.keys order: whole-number keys ascending first, then the others as they were added."""
    nums_ = [k for k in keys if is_index_key(k)]
    nums_ = sort_by(nums_, key=lambda k: (len(k), k))
    return nums_ + [k for k in keys if not is_index_key(k)]


# ── 1. List After ───────────────────────────────────────────────────────

STEPS: dict[str, Callable] = {}
RULES: dict[str, str] = {}


def step(name: str, rule: str):
    def deco(fn):
        STEPS[name] = fn
        RULES[name] = rule
        return fn
    return deco


@step("push", "push adds an item at the end")
def _push(rng, xs):
    v = _v(rng)
    return f"xs.push({v});", xs + [v]


@step("push2", "push can add several items at once")
def _push2(rng, xs):
    a, b = _v(rng), _v(rng)
    return f"xs.push({a}, {b});", xs + [a, b]


@step("pop", "pop() removes the last item")
def _pop(rng, xs):
    return "xs.pop();", take(xs, 0, len(xs) - 1)


@step("shift", "shift() removes the first item")
def _shift(rng, xs):
    return "xs.shift();", drop(xs, 0)


@step("unshift", "unshift(v) adds v at the front")
def _unshift(rng, xs):
    v = _v(rng)
    return f"xs.unshift({v});", ins(xs, 0, v)


@step("splice_remove", "splice(i, 1) removes one item at position i")
def _splice_remove(rng, xs):
    i = rng.randrange(len(xs))
    return f"xs.splice({i}, 1);", drop(xs, i)


@step("splice_insert", "splice(i, 0, v) inserts v at position i and removes nothing")
def _splice_insert(rng, xs):
    i, v = rng.randint(1, len(xs) - 1), _v(rng)
    return f"xs.splice({i}, 0, {v});", ins(xs, i, v)


@step("splice_replace", "splice(i, 1, v) swaps the item at i for v")
def _splice_replace(rng, xs):
    i, v = rng.randrange(len(xs)), _v(rng)
    return f"xs.splice({i}, 1, {v});", take(xs, 0, i) + [v] + take(xs, i + 1, len(xs))


@step("splice_tail", "splice(i) with one argument removes everything from position i on")
def _splice_tail(rng, xs):
    i = rng.randint(1, len(xs) - 1)
    return f"xs.splice({i});", take(xs, 0, i)


@step("splice_neg", "splice(-2) removes the last two items")
def _splice_neg(rng, xs):
    return "xs.splice(-2);", take(xs, 0, len(xs) - 2)


@step("sort_num", "(a, b) => a - b makes sort compare numbers, smallest first")
def _sort_num(rng, xs):
    return "xs.sort((a, b) => a - b);", sort_by(xs)


@step("sort_num_desc", "(a, b) => b - a sorts numbers biggest first")
def _sort_num_desc(rng, xs):
    return "xs.sort((a, b) => b - a);", sort_by(xs, reverse=True)


@step("sort_default", "sort() with no function compares the items as TEXT, so 10 comes before 9")
def _sort_default(rng, xs):
    return "xs.sort();", sort_by(xs, key=lambda n: str(n))


@step("reverse", "reverse() flips the array in place")
def _reverse(rng, xs):
    return "xs.reverse();", [xs[len(xs) - 1 - i] for i in range(len(xs))]


@step("set_idx", "xs[i] = v replaces the item at position i")
def _set_idx(rng, xs):
    i, v = rng.randrange(len(xs)), _v(rng)
    return f"xs[{i}] = {v};", take(xs, 0, i) + [v] + take(xs, i + 1, len(xs))


@step("append_idx", "assigning at index xs.length adds an item at the end")
def _append_idx(rng, xs):
    v = _v(rng)
    return f"xs[xs.length] = {v};", xs + [v]


@step("set_len", "setting length shorter cuts the array off")
def _set_len(rng, xs):
    return "xs.length = 2;", take(xs, 0, 2)


@step("fill", "fill(0, 1) overwrites every item from position 1 on")
def _fill(rng, xs):
    return "xs.fill(0, 1);", take(xs, 0, 1) + [0 for _ in range(len(xs) - 1)]


@step("concat_assign", "concat builds a new array, and the assignment makes xs name it")
def _concat_assign(rng, xs):
    v = _v(rng)
    return f"xs = xs.concat([{v}]);", xs + [v]


@step("spread_back", "[...xs, v] copies xs and adds v at the end")
def _spread_back(rng, xs):
    v = _v(rng)
    return f"xs = [...xs, {v}];", xs + [v]


@step("spread_front", "[v, ...xs] copies xs after v")
def _spread_front(rng, xs):
    v = _v(rng)
    return f"xs = [{v}, ...xs];", ins(xs, 0, v)


@step("slice_front", "slice(1) is a new array without the first item")
def _slice_front(rng, xs):
    return "xs = xs.slice(1);", take(xs, 1, len(xs))


@step("filter", "filter keeps only the items the test accepts")
def _filter(rng, xs):
    k = rng.randint(2, 6)
    return f"xs = xs.filter(x => x > {k});", [x for x in xs if x > k]


@step("map", "map builds a new array from the old one")
def _map(rng, xs):
    return "xs = xs.map(x => x * 2);", [x * 2 for x in xs]


@step("noop_concat", "concat does not change xs: the new array is thrown away")
def _noop_concat(rng, xs):
    return f"xs.concat([{_v(rng)}]);", xs


@step("noop_map", "map returns a new array and leaves xs alone")
def _noop_map(rng, xs):
    return "xs.map(x => x * 2);", xs


@step("noop_slice", "slice returns a copy and leaves xs alone")
def _noop_slice(rng, xs):
    return "xs.slice(1);", xs


@step("noop_sorted", "toSorted returns a sorted copy and leaves xs alone")
def _noop_sorted(rng, xs):
    return "xs.toSorted((a, b) => a - b);", xs


@step("clear", "setting length to 0 empties the array")
def _clear(rng, xs):
    return "xs.length = 0;", []


_REBINDS = ("concat_assign", "spread_back", "spread_front", "slice_front", "filter", "map")


def _start(rng: random.Random, wide: bool, need_text_order: bool) -> list[int]:
    while True:
        if wide:
            xs = rng.sample(range(1, 10), 2) + rng.sample(range(10, 100), 2)
            rng.shuffle(xs)
        else:
            xs = ints(rng, rng.randint(3, 4), 1, 9)
        if not need_text_order or sort_by(xs, key=lambda n: str(n)) != sort_by(xs):
            return xs


def _recipe(steps: tuple[str, ...], final: str, wide: bool = False) -> Maker:
    def make(rng: random.Random) -> Item:
        cur = _start(rng, wide, "sort_default" in steps)
        rebinds = any(s in _REBINDS for s in steps)
        lines = [f"{'let' if rebinds else 'const'} xs = {lit(cur)};"]
        for name in steps:
            line, cur = STEPS[name](rng, cur)
            lines.append(line)
        if final == "xs":
            ans, last = js_show(cur), "xs"
        elif final == "first":
            ans, last = str(cur[0]), "xs[0]"
        else:
            ans, last = str(cur[len(cur) - 1]), "xs.at(-1)"
        seen: list[str] = []
        for s in steps:
            if RULES[s] not in seen:
                seen.append(RULES[s])
        why = "; ".join(seen[:2]) + "."
        return Item("\n".join(lines + [last]), ans, why)
    make.__name__ = "after_" + "_".join(steps) + "_" + final
    return make


_RECIPES: list[tuple[tuple[str, ...], str, bool]] = [
    (("push",), "xs", False), (("push2",), "xs", False), (("pop",), "xs", False), (("shift",), "xs", False),
    (("unshift",), "xs", False), (("splice_remove",), "xs", False), (("splice_insert",), "xs", False),
    (("splice_replace",), "xs", False), (("splice_tail",), "xs", False), (("splice_neg",), "xs", False),
    (("sort_num",), "xs", False), (("sort_num_desc",), "xs", False), (("sort_default",), "xs", True),
    (("sort_default",), "first", True), (("sort_default",), "last", True), (("reverse",), "xs", False),
    (("set_idx",), "xs", False), (("append_idx",), "xs", False), (("set_len",), "xs", False),
    (("fill",), "xs", False), (("concat_assign",), "xs", False), (("spread_back",), "xs", False),
    (("spread_front",), "xs", False), (("slice_front",), "xs", False), (("filter",), "xs", False),
    (("map",), "xs", False), (("noop_concat",), "xs", False), (("noop_map",), "xs", False),
    (("noop_slice",), "xs", False), (("noop_sorted",), "xs", False), (("clear", "push"), "xs", False),
    (("push", "sort_num"), "xs", False), (("push", "reverse"), "xs", False), (("pop", "push"), "xs", False),
    (("shift", "push"), "xs", False), (("unshift", "pop"), "xs", False), (("push", "shift"), "xs", False),
    (("reverse", "pop"), "xs", False), (("reverse", "push"), "xs", False), (("sort_num", "pop"), "xs", False),
    (("sort_num_desc", "shift"), "xs", False), (("splice_remove", "unshift"), "xs", False),
    (("splice_insert", "reverse"), "xs", False), (("push", "unshift", "pop"), "xs", False),
    (("push", "push", "shift"), "xs", False), (("reverse", "reverse"), "xs", False),
    (("sort_num", "reverse"), "xs", False), (("sort_default", "reverse"), "xs", True),
    (("sort_default", "pop"), "xs", True), (("push", "sort_default"), "xs", True),
    (("sort_num",), "first", False), (("sort_num_desc",), "first", False), (("pop",), "last", False),
    (("unshift", "sort_num"), "last", False), (("reverse",), "last", False),
]

AFTER: list[Maker] = [_recipe(s, f, w) for s, f, w in _RECIPES]


def _after(fn: Maker) -> Maker:
    AFTER.append(fn)
    return fn


@_after
def a_alias(rng):
    xs, v = nums(rng), _v(rng)
    return Item(f"const xs = {lit(xs)};\nconst ys = xs;\nys.push({v});\nxs", js_show(xs + [v]),
                "ys = xs does not copy: both names point at the same array, so the push shows in xs.")


@_after
def a_spread_copy(rng):
    xs, v = nums(rng), _v(rng)
    return Item(f"const xs = {lit(xs)};\nconst ys = [...xs];\nys.push({v});\nxs", js_show(xs),
                "[...xs] makes a separate array, so changing ys leaves xs alone.")


@_after
def a_slice_copy(rng):
    xs = nums(rng)
    return Item(f"const xs = {lit(xs)};\nconst ys = xs.slice();\nys.pop();\nxs", js_show(xs), "slice() with no arguments is a copy, so popping ys does not touch xs.")


@_after
def a_func(rng):
    xs, v = nums(rng), _v(rng)
    return Item(f"function add(items) {{\n  items.push({v});\n}}\nconst xs = {lit(xs)};\nadd(xs);\nxs", js_show(xs + [v]),
                "The function was handed the very same array, and push changes it in place.")


@_after
def a_func_rebind(rng):
    xs, v = nums(rng), _v(rng)
    return Item(f"function add(items) {{\n  items = [...items, {v}];\n}}\nconst xs = {lit(xs)};\nadd(xs);\nxs", js_show(xs),
                "[...items, v] builds a new array, and only the function's own name items points at it.")


@_after
def a_push_value(rng):
    xs, v = nums(rng), _v(rng)
    return Item(f"const xs = {lit(xs)};\nxs.push({v})", str(len(xs) + 1), "push gives back the NEW length, not the array.")


@_after
def a_unshift_value(rng):
    xs, v = nums(rng), _v(rng)
    return Item(f"const xs = {lit(xs)};\nxs.unshift({v})", str(len(xs) + 1), "unshift also gives back the new length.")


@_after
def a_pop_value(rng):
    xs = nums(rng)
    return Item(f"const xs = {lit(xs)};\nxs.pop()", str(xs[len(xs) - 1]), "pop() gives back the item it removed.")


@_after
def a_shift_value(rng):
    xs = nums(rng)
    return Item(f"const xs = {lit(xs)};\nxs.shift()", str(xs[0]), "shift() gives back the first item it removed.")


@_after
def a_splice_value(rng):
    xs = nums(rng, 4, 5)
    i = rng.randint(0, 1)
    return Item(f"const xs = {lit(xs)};\nxs.splice({i}, 2)", js_show(take(xs, i, i + 2)), "splice gives back an array of what it removed.")


@_after
def a_splice_left(rng):
    xs = nums(rng, 4, 5)
    i = rng.randint(0, 1)
    return Item(f"const xs = {lit(xs)};\nxs.splice({i}, 2);\nxs", js_show(take(xs, 0, i) + take(xs, i + 2, len(xs))), "splice(i, 2) takes two items out starting at position i.")


@_after
def a_sort_returns_same(rng):
    xs = nums(rng)
    return Item(f"const xs = {lit(xs)};\nxs.sort() === xs", "true", "sort() sorts in place and hands back the very same array.")


@_after
def a_reverse_value(rng):
    xs = nums(rng)
    return Item(f"const xs = {lit(xs)};\nxs.reverse()", js_show([xs[len(xs) - 1 - i] for i in range(len(xs))]), "reverse() flips in place and returns the array.")


@_after
def a_sort_default_trap(rng):
    xs = [rng.randint(1, 9), rng.randint(10, 20), rng.randint(21, 99)]
    xs = [xs[i] for i in rng.sample(range(3), 3)]
    return Item(f"const xs = {lit(xs)};\nxs.sort()", js_show(sort_by(xs, key=lambda n: str(n))), "The default sort compares text: '10' comes before '9'.")


@_after
def a_spread_sort(rng):
    xs = nums(rng)
    return Item(f"const xs = {lit(xs)};\n[...xs].sort((a, b) => a - b);\nxs[0]", str(xs[0]), "The sort ran on a copy, so xs keeps its order.")


@_after
def a_concat_flat(rng):
    a, b, c = ints(rng, 3, 1, 9)
    return Item(f"[{a}].concat([{b}, [{c}]])", js_show([a, b, [c]]), "concat spreads one level: [b, [c]] adds b and the inner array [c].")


@_after
def a_push_array(rng):
    xs, a, b = nums(rng, 2, 3), _v(rng), _v(rng)
    return Item(f"const xs = {lit(xs)};\nxs.push([{a}, {b}]);\nxs.length", str(len(xs) + 1), "push adds the whole array as ONE item.")


@_after
def a_push_spread(rng):
    xs, a, b = nums(rng, 2, 3), _v(rng), _v(rng)
    return Item(f"const xs = {lit(xs)};\nxs.push(...[{a}, {b}]);\nxs.length", str(len(xs) + 2), "The spread turns the array into separate items for push.")


@_after
def a_length_past(rng):
    xs, v = nums(rng, 3, 3), _v(rng)
    return Item(f"const xs = {lit(xs)};\nxs[{len(xs) + 2}] = {v};\nxs.length", str(len(xs) + 3), "Assigning past the end leaves a gap, and the length becomes index + 1.")


@_after
def a_while_shift(rng):
    xs = nums(rng, 4, 5)
    return Item(f"const xs = {lit(xs)};\nwhile (xs.length > 2) xs.shift();\nxs", js_show(take(xs, len(xs) - 2, len(xs))), "Each turn drops the first item until two are left.")


@_after
def a_for_push(rng):
    n = rng.randint(3, 5)
    return Item(f"const xs = [];\nfor (let i = 0; i < {n}; i++) xs.push(i * i);\nxs", js_show([i * i for i in range(n)]), "i runs 0, 1, 2 ... and each square is pushed in turn.")


@_after
def a_dup_splice(rng):
    xs = dupes(rng)
    xs = take(xs, 0, 5)
    v = xs[0]
    i = pos(xs, v)
    return Item(f"const xs = {lit(xs)};\nxs.splice(xs.indexOf({v}), 1);\nxs", js_show(drop(xs, i)), "indexOf finds the FIRST match, so only that one is spliced out.")


# ── 2. How Many ─────────────────────────────────────────────────────────

HOW: list[Maker] = []


def _how(fn: Maker) -> Maker:
    HOW.append(fn)
    return fn


def _n(code: str, n: int, why: str) -> Item:
    return Item(code, str(n), why)


@_how
def h_array(rng):
    xs = nums(rng, 3, 6)
    return _n(f"{lit(xs)}.length", len(xs), "length counts the items.")


@_how
def h_string(rng):
    w = rng.choice(WORDS)
    return _n(f'"{w}".length', len(w), "length of a string counts its characters.")


@_how
def h_empty(rng):
    code = rng.choice(["[].length", '"".length', "Object.keys({}).length", "new Set().size", "new Map().size"])
    return _n(code, 0, "Nothing inside means 0.")


@_how
def h_push(rng):
    xs, v = nums(rng), _v(rng)
    return _n(f"const xs = {lit(xs)};\nxs.push({v});\nxs.length", len(xs) + 1, "push adds one item.")


@_how
def h_push_many(rng):
    xs, a, b = nums(rng), _v(rng), _v(rng)
    return _n(f"const xs = {lit(xs)};\nxs.push({a}, {b});\nxs.length", len(xs) + 2, "push can add several items at once.")


@_how
def h_push_array(rng):
    xs, a, b = nums(rng, 2, 4), _v(rng), _v(rng)
    return _n(f"const xs = {lit(xs)};\nxs.push([{a}, {b}]);\nxs.length", len(xs) + 1, "push adds the whole array as a single item.")


@_how
def h_pop(rng):
    xs = nums(rng, 3, 6)
    return _n(f"const xs = {lit(xs)};\nxs.pop();\nxs.length", len(xs) - 1, "pop removes one item.")


@_how
def h_shift(rng):
    xs = nums(rng, 3, 6)
    return _n(f"const xs = {lit(xs)};\nxs.shift();\nxs.length", len(xs) - 1, "shift removes one item.")


@_how
def h_unshift(rng):
    xs, v = nums(rng), _v(rng)
    return _n(f"const xs = {lit(xs)};\nxs.unshift({v});\nxs.length", len(xs) + 1, "unshift adds one item.")


@_how
def h_push_returns(rng):
    xs, v = nums(rng), _v(rng)
    return _n(f"const xs = {lit(xs)};\nxs.push({v})", len(xs) + 1, "push returns the new length.")


@_how
def h_splice(rng):
    xs = nums(rng, 4, 6)
    k = rng.randint(1, 3)
    return _n(f"const xs = {lit(xs)};\nxs.splice(1, {k});\nxs.length", len(xs) - k, f"splice(1, {k}) removes {k} items.")


@_how
def h_splice_insert(rng):
    xs, v = nums(rng), _v(rng)
    return _n(f"const xs = {lit(xs)};\nxs.splice(1, 0, {v});\nxs.length", len(xs) + 1, "A delete count of 0 removes nothing, so it only adds.")


@_how
def h_splice_returned(rng):
    xs = nums(rng, 4, 6)
    k = rng.randint(1, 3)
    return _n(f"const xs = {lit(xs)};\nxs.splice(1, {k}).length", k, "splice gives back what it removed: that many items.")


@_how
def h_concat(rng):
    xs, ys = nums(rng, 2, 4), nums(rng, 2, 3)
    return _n(f"{lit(xs)}.concat({lit(ys)}).length", len(xs) + len(ys), "concat joins the two arrays.")


@_how
def h_spread(rng):
    xs, ys = nums(rng, 2, 3), nums(rng, 2, 3)
    return _n(f"[...{lit(xs)}, ...{lit(ys)}].length", len(xs) + len(ys), "Each spread adds all its items.")


@_how
def h_nested(rng):
    inner = [nums(rng, 1, 3) for _ in range(rng.randint(2, 3))] + [[]]
    return _n(f"{lit(inner)}.length", len(inner), "length counts the outer items only.")


@_how
def h_flat(rng):
    inner = [nums(rng, 1, 3) for _ in range(rng.randint(2, 3))]
    n = 0
    for part in inner:
        n += len(part)
    return _n(f"{lit(inner)}.flat().length", n, "flat() joins the inner arrays into one: count every item.")


@_how
def h_slice(rng):
    xs = nums(rng, 5, 6)
    a, b = rng.randint(0, 2), rng.randint(3, 5)
    return _n(f"{lit(xs)}.slice({a}, {b}).length", b - a, f"slice({a}, {b}) takes positions {a} up to, not including, {b}.")


@_how
def h_slice_neg(rng):
    xs, k = nums(rng, 4, 6), rng.randint(1, 3)
    return _n(f"{lit(xs)}.slice(-{k}).length", k, f"slice(-{k}) is the last {k}.")


@_how
def h_filter(rng):
    xs, k = nums(rng, 5, 6), rng.randint(3, 6)
    return _n(f"{lit(xs)}.filter(x => x > {k}).length", len([x for x in xs if x > k]), f"Only the items bigger than {k} are kept.")


@_how
def h_map(rng):
    xs = nums(rng, 3, 6)
    return _n(f"{lit(xs)}.map(x => x * 2).length", len(xs), "map makes one new item per old item.")


@_how
def h_array_fill(rng):
    n = rng.randint(3, 8)
    return _n(f"new Array({n}).fill(0).length", n, f"An array of {n} slots, every one filled.")


@_how
def h_array_from(rng):
    n = rng.randint(3, 8)
    return _n(f"Array.from({{ length: {n} }}).length", n, f"{{ length: {n} }} makes an array with {n} slots.")


@_how
def h_array_ctor(rng):
    n = rng.randint(3, 8)
    return _n(f"Array({n}).length", n, f"Array({n}) makes {n} empty slots, so the length is {n}.")


@_how
def h_trailing_comma(rng):
    a, b, c = ints(rng, 3, 1, 9)
    return _n(f"[{a}, {b}, {c},].length", 3, "A trailing comma is not an extra item.")


@_how
def h_hole(rng):
    a, b = ints(rng, 2, 1, 9)
    return _n(f"[{a}, , {b}].length", 3, "The gap between the commas still takes a slot.")


@_how
def h_past_end(rng):
    xs = nums(rng, 3, 3)
    k = rng.randint(5, 8)
    return _n(f"const xs = {lit(xs)};\nxs[{k}] = 1;\nxs.length", k + 1, "Assigning at index k makes the length k + 1.")


@_how
def h_set_length(rng):
    xs = nums(rng, 4, 6)
    k = rng.randint(1, 3)
    return _n(f"const xs = {lit(xs)};\nxs.length = {k};\nxs.length", k, "Setting length cuts the array down.")


@_how
def h_split(rng):
    ws = words(rng, rng.randint(2, 4))
    return _n(f'"{",".join(ws)}".split(",").length', len(ws), "One more piece than there are commas.")


@_how
def h_split_empty(rng):
    code, n, why = rng.choice([('"".split(",").length', 1, "Splitting an empty string at a comma gives one empty piece."),
                               ('"".split("").length', 0, "Splitting nothing into letters gives nothing."),
                               ('",".split(",").length', 2, "A lone comma has an empty piece on each side.")])
    return _n(code, n, why)


@_how
def h_spread_str(rng):
    w = rng.choice(WORDS)
    return _n(f'[..."{w}"].length', len(w), "Spreading a string makes one item per character.")


@_how
def h_set_dupes(rng):
    xs = dupes(rng)
    return _n(f"new Set({lit(xs)}).size", len(uniq(xs)), "A Set keeps each value once; size counts what is left.")


@_how
def h_set_str(rng):
    w = rng.choice(["hello", "little", "banana", "balloon", "carrot", "coffee", "pumpkin"])
    return _n(f'new Set("{w}").size', len(uniq(list(w))), "A Set of a string holds each different letter once.")


@_how
def h_set_types(rng):
    code, n, why = rng.choice([('new Set([1, "1"]).size', 2, "The number 1 and the text \"1\" are different values."),
                               ("new Set([NaN, NaN]).size", 1, "A Set treats NaN as equal to itself."),
                               ("new Set([[1], [1]]).size", 2, "Two separate arrays are two different objects."),
                               ("new Set([0, -0]).size", 1, "A Set treats 0 and -0 as the same value."),
                               ("new Set([{}, {}]).size", 2, "Two separate objects are never the same value.")])
    return _n(code, n, why)


@_how
def h_set_add(rng):
    a = nums(rng)
    k, new = rng.choice([(a[0], False), (a[0] + 9, True)])
    return _n(f"const s = new Set({lit(a)});\ns.add({k});\ns.size", len(a) + (1 if new else 0),
              "A new value makes the set bigger." if new else "The value was already there, so nothing changes.")


@_how
def h_set_delete(rng):
    a = nums(rng)
    k, absent = rng.choice([(a[0], False), (a[0] + 9, True)])
    return _n(f"const s = new Set({lit(a)});\ns.delete({k});\ns.size", len(a) - (0 if absent else 1),
              "delete does nothing for a missing value." if absent else "delete removes the value.")


@_how
def h_obj_keys(rng):
    d = pairs(rng, rng.randint(2, 4))
    return _n(f"Object.keys({olit(d)}).length", len(d), "keys gives one entry per property.")


@_how
def h_obj_values(rng):
    d = pairs(rng, rng.randint(2, 4))
    return _n(f"Object.values({olit(d)}).length", len(d), "values gives one entry per property.")


@_how
def h_obj_entries(rng):
    d = pairs(rng, rng.randint(2, 4))
    return _n(f"Object.entries({olit(d)}).length", len(d), "entries gives one [key, value] pair per property.")


@_how
def h_obj_add(rng):
    d, v = pairs(rng), _v(rng)
    return _n(f"const o = {olit(d)};\no.extra = {v};\nObject.keys(o).length", len(d) + 1, "A new property makes the object one bigger.")


@_how
def h_obj_replace(rng):
    d, v = pairs(rng), _v(rng)
    return _n(f"const o = {olit(d)};\no.{d[0][0]} = {v};\nObject.keys(o).length", len(d), "An existing property just gets a new value.")


@_how
def h_obj_delete(rng):
    d = pairs(rng, rng.randint(3, 4))
    return _n(f"const o = {olit(d)};\ndelete o.{d[0][0]};\nObject.keys(o).length", len(d) - 1, "delete removes the property.")


@_how
def h_obj_dup(rng):
    k, a, b = rng.choice(WORDS), _v(rng), _v(rng)
    return _n(f"Object.keys({{ {k}: {a}, {k}: {b} }}).length", 1, "A property name can only be there once: the later value replaces the earlier.")


@_how
def h_obj_numkeys(rng):
    return _n('Object.keys({ 1: "a", "1": "b" }).length', 1, 'Object keys are text, so 1 and "1" are the same key.')


@_how
def h_obj_spread(rng):
    d = pairs(rng, 3)
    e = [(d[0][0], 0), ("extra", 1)]
    return _n(f"Object.keys({{ ...{olit(d)}, ...{olit(e)} }}).length", len(d_merge(d, e)), "Spreading two objects keeps each name once: the shared one counts a single time.")


@_how
def h_obj_assign(rng):
    d = pairs(rng, 2)
    e = [(d[1][0], 0), ("extra", 1)]
    return _n(f"Object.keys(Object.assign({{}}, {olit(d)}, {olit(e)})).length", len(d_merge(d, e)), "assign copies properties in; a shared name is just overwritten.")


@_how
def h_map_size(rng):
    d = pairs(rng, rng.randint(2, 4))
    ent = "[" + ", ".join(f'["{k}", {v}]' for k, v in d) + "]"
    return _n(f"new Map({ent}).size", len(d), "A Map's size counts its entries.")


@_how
def h_map_dup(rng):
    k, a, b = rng.choice(WORDS), _v(rng), _v(rng)
    return _n(f'new Map([["{k}", {a}], ["{k}", {b}]]).size', 1, "The second entry replaces the first: same key.")


@_how
def h_map_set(rng):
    d = pairs(rng, 2)
    k, new = rng.choice([(d[0][0], False), ("extra", True)])
    return _n(f'const m = new Map([["{d[0][0]}", 1], ["{d[1][0]}", 2]]);\nm.set("{k}", 9);\nm.size', 2 + (1 if new else 0),
              "A new key adds an entry." if new else "An existing key just gets a new value.")


@_how
def h_map_delete(rng):
    d = pairs(rng, 3)
    return _n(f'const m = new Map([["{d[0][0]}", 1], ["{d[1][0]}", 2], ["{d[2][0]}", 3]]);\nm.delete("{d[1][0]}");\nm.size', 2, "delete removes the entry.")


@_how
def h_array_keys(rng):
    xs = nums(rng, 3, 5)
    return _n(f"Object.keys({lit(xs)}).length", len(xs), "An array's keys are its positions: one per item.")


@_how
def h_str_join(rng):
    ws = words(rng, rng.randint(2, 3))
    sep = rng.choice(["-", ", ", ""])
    n = 0
    for w in ws:
        n += len(w)
    n += len(sep) * (len(ws) - 1)
    return _n(f'{lit(ws)}.join("{sep}").length', n, "The letters of every word, plus the separator between each pair.")


@_how
def h_count_loop(rng):
    w = rng.choice(["hello", "little", "banana", "balloon", "coffee", "pumpkin"])
    d: list = []
    for ch in w:
        d = d_set(d, ch, d_get(d, ch, 0) + 1)
    return _n(f'const counts = {{}};\nfor (const c of "{w}") counts[c] = (counts[c] || 0) + 1;\nObject.keys(counts).length', len(d), "One key per different letter.")


# ── 3. Dict Lookup ──────────────────────────────────────────────────────

LOOKUP: list[Maker] = []


def _look(fn: Maker) -> Maker:
    LOOKUP.append(fn)
    return fn


def _L(code: str, ans, why: str, err: bool = False) -> Item:
    return Item(code, str(ans), why, check=err_js(code) if err else "")


def _decl(d: list) -> str:
    return f"const o = {olit(d)};"


def _missing(rng: random.Random, d: list) -> str:
    return rng.choice([w for w in WORDS if not d_has(d, w)])


@_look
def l_dot(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _L(f"{_decl(d)}\no.{k}", v, "o.name gives the value stored under that name.")


@_look
def l_bracket(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _L(f'{_decl(d)}\no["{k}"]', v, 'o["name"] works like o.name.')


@_look
def l_word_value(rng):
    d = pairs(rng, 3, strs=True)
    k, v = d[rng.randrange(3)]
    return _L(f"{_decl(d)}\no.{k}", v, "o.name gives the value stored under that name.")


@_look
def l_var_key(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _L(f'{_decl(d)}\nconst key = "{k}";\no[key]', v, "Square brackets use the VALUE of key, so it looks up the name it holds.")


@_look
def l_dot_var(rng):
    d = pairs(rng)
    while d_has(d, "key"):
        d = pairs(rng)
    k = d[rng.randrange(3)][0]
    return _L(f'{_decl(d)}\nconst key = "{k}";\no.key', "undefined", "o.key looks for a property literally named key, not for what the variable holds.")


@_look
def l_missing(rng):
    d = pairs(rng)
    return _L(f"{_decl(d)}\no.{_missing(rng, d)}", "undefined", "A missing property is undefined, not an error.")


@_look
def l_missing_bracket(rng):
    d = pairs(rng)
    return _L(f'{_decl(d)}\no["{_missing(rng, d)}"]', "undefined", "A missing key gives undefined.")


@_look
def l_nullish_missing(rng):
    d, n = pairs(rng), _v(rng)
    return _L(f"{_decl(d)}\no.{_missing(rng, d)} ?? {n}", n, "?? gives its right side when the left is undefined (or null).")


@_look
def l_nullish_present(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _L(f"{_decl(d)}\no.{k} ?? 0", v, "The property exists, so ?? keeps it.")


@_look
def l_or_zero(rng):
    k = rng.choice(WORDS)
    return _L(f"const o = {{ {k}: 0 }};\no.{k} || 5", 5, "0 is falsy, so || replaces it with 5.")


@_look
def l_nullish_zero(rng):
    k = rng.choice(WORDS)
    return _L(f"const o = {{ {k}: 0 }};\no.{k} ?? 5", 0, "?? only replaces undefined and null, so the 0 stays.")


@_look
def l_in(rng):
    d = pairs(rng)
    k, found = rng.choice([(d[rng.randrange(3)][0], True), (_missing(rng, d), False)])
    return _L(f'{_decl(d)}\n"{k}" in o', jb(found), "in asks whether the object has that property name.")


@_look
def l_in_value(rng):
    d = pairs(rng)
    return _L(f"{_decl(d)}\n{d[rng.randrange(3)][1]} in o", "false", "in looks at the property NAMES, and these names are words.")


@_look
def l_hasown(rng):
    d = pairs(rng)
    k, found = rng.choice([(d[rng.randrange(3)][0], True), (_missing(rng, d), False)])
    return _L(f'{_decl(d)}\nObject.hasOwn(o, "{k}")', jb(found), "hasOwn is true only for the object's own properties.")


@_look
def l_inherited(rng):
    d = pairs(rng)
    code, ans, why = rng.choice([(f'{_decl(d)}\n"toString" in o', "true", "in also finds inherited properties, and every object inherits toString."),
                                 (f'{_decl(d)}\nObject.hasOwn(o, "toString")', "false", "hasOwn ignores inherited properties.")])
    return _L(code, ans, why)


@_look
def l_set_get(rng):
    d, v = pairs(rng), _v(rng)
    return _L(f"{_decl(d)}\no.extra = {v};\no.extra", v, "Assigning to a new name adds the property.")


@_look
def l_overwrite(rng):
    d, v = pairs(rng), _v(rng)
    k = d[rng.randrange(3)][0]
    return _L(f"{_decl(d)}\no.{k} = {v};\no.{k}", v, "Assigning to an existing name replaces its value.")


@_look
def l_delete_then(rng):
    d = pairs(rng)
    k = d[rng.randrange(3)][0]
    return _L(f"{_decl(d)}\ndelete o.{k};\no.{k}", "undefined", "After delete the property is gone, so it reads as undefined.")


@_look
def l_delete_returns(rng):
    d = pairs(rng)
    return _L(f"{_decl(d)}\ndelete o.{d[rng.randrange(3)][0]}", "true", "delete gives true when it works (even for a name that was never there).")


@_look
def l_optional_missing(rng):
    k1, k2 = rng.sample(WORDS, 2)
    return _L(f"const o = {{ {k1}: {{ n: {_v(rng)} }} }};\no.{k2}?.n", "undefined", "?. stops and gives undefined when the part before it is undefined.")


@_look
def l_optional_present(rng):
    k = rng.choice(WORDS)
    v = _v(rng)
    return _L(f"const o = {{ {k}: {{ n: {v} }} }};\no.{k}?.n", v, "The object exists, so ?. goes on to read n.")


@_look
def l_chain_error(rng):
    k1, k2 = rng.sample(WORDS, 2)
    return _L(f"const o = {{ {k1}: {{ n: {_v(rng)} }} }};\no.{k2}.n", "TypeError", "o.name is undefined, and reading .n of undefined is a TypeError.", True)


@_look
def l_call_missing(rng):
    d = pairs(rng)
    return _L(f"{_decl(d)}\no.{_missing(rng, d)}()", "TypeError", "undefined is not a function, so calling it is a TypeError.", True)


@_look
def l_keys_i(rng):
    d = pairs(rng)
    i = rng.randrange(3)
    return _L(f"{_decl(d)}\nObject.keys(o)[{i}]", d[i][0], "keys come out in the order they were written (for word names).")


@_look
def l_values_i(rng):
    d = pairs(rng)
    i = rng.randrange(3)
    return _L(f"{_decl(d)}\nObject.values(o)[{i}]", d[i][1], "values follow the same order as the keys.")


@_look
def l_entries_i(rng):
    d = pairs(rng)
    i = rng.randrange(3)
    return _L(f"{_decl(d)}\nObject.entries(o)[{i}]", js_show([d[i][0], d[i][1]]), "entries gives [name, value] pairs.")


@_look
def l_keys_number_order(rng):
    names = rng.sample(WORDS, 2)
    nk = [str(n) for n in rng.sample(range(1, 10), 2)]
    order = [names[0], nk[0], names[1], nk[1]]
    body = ", ".join(f"{k}: 1" for k in order)
    return _L(f"Object.keys({{ {body} }})", js_show(js_key_order(order)), "Number-like keys jump to the front in ascending order; the other names keep the order they were written.")


@_look
def l_numkey(rng):
    n = rng.randint(1, 9)
    return _L(f'const o = {{ {n}: "a" }};\no["{n}"]', "a", "Object keys are text: the key 1 and the key \"1\" are the same.")


@_look
def l_spread_override(rng):
    k = rng.choice(WORDS)
    a, b = ints(rng, 2, 1, 9)
    return _L(f"const x = {{ {k}: {a} }};\nconst y = {{ {k}: {b} }};\n({{ ...x, ...y }}).{k}", b, "Spreading y after x lets y's value win for a shared name.")


@_look
def l_assign_override(rng):
    k = rng.choice(WORDS)
    a, b = ints(rng, 2, 1, 9)
    return _L(f"const x = {{ {k}: {a} }};\nconst y = {{ {k}: {b} }};\nObject.assign({{}}, x, y).{k}", b, "assign copies in order, so the later object wins.")


@_look
def l_dup_key(rng):
    k, a, b = rng.choice(WORDS), _v(rng), _v(rng)
    return _L(f"({{ {k}: {a}, {k}: {b} }}).{k}", b, "A repeated name keeps its last value.")


@_look
def l_obj_key(rng):
    return _L("const o = {};\no[{}] = 1;\nObject.keys(o)[0]", "[object Object]", "An object used as a key is turned into the text \"[object Object]\".")


def _map_decl(d: list) -> str:
    return "const m = new Map([" + ", ".join(f'["{k}", {v}]' for k, v in d) + "]);"


@_look
def l_map_get(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _L(f'{_map_decl(d)}\nm.get("{k}")', v, "A Map's get gives the value for that key.")


@_look
def l_map_missing(rng):
    d = pairs(rng)
    return _L(f'{_map_decl(d)}\nm.get("{_missing(rng, d)}")', "undefined", "get gives undefined for a missing key.")


@_look
def l_map_has(rng):
    d = pairs(rng)
    k, found = rng.choice([(d[rng.randrange(3)][0], True), (_missing(rng, d), False)])
    return _L(f'{_map_decl(d)}\nm.has("{k}")', jb(found), "has asks whether the Map holds that key.")


@_look
def l_map_set_chain(rng):
    d, v = pairs(rng), _v(rng)
    return _L(f'{_map_decl(d)}\nm.set("extra", {v}).get("extra")', v, "set returns the Map itself, so calls can be chained.")


@_look
def l_map_num_key(rng):
    n = rng.randint(1, 9)
    code, ans, why = rng.choice([(f'new Map([[{n}, "a"]]).get("{n}")', "undefined", "A Map keeps types apart: the number and the text are different keys."),
                                 (f'new Map([[{n}, "a"]]).get({n})', "a", "The same number finds it.")])
    return _L(code, ans, why)


@_look
def l_map_obj_key(rng):
    code, ans, why = rng.choice([("const k = {};\nconst m = new Map([[k, 1]]);\nm.get({})", "undefined", "A Map compares objects by identity: {} is a different object."),
                                 ("const k = {};\nconst m = new Map([[k, 1]]);\nm.get(k)", "1", "The same object finds the entry.")])
    return _L(code, ans, why)


@_look
def l_map_first_key(rng):
    d = pairs(rng)
    return _L(f"{_map_decl(d)}\n[...m.keys()][0]", d[0][0], "A Map keeps its entries in the order they were added.")


@_look
def l_in_map(rng):
    k = rng.choice(WORDS)
    return _L(f'const m = new Map([["{k}", 1]]);\n"{k}" in m', "false", "in looks at the Map object's own properties, not its entries - use m.has(key).")


@_look
def l_default_pattern(rng):
    d = pairs(rng)
    k = _missing(rng, d)
    n = _v(rng)
    return _L(f"{_decl(d)}\no.{k} === undefined ? {n} : o.{k}", n, "The check sees undefined, so the fallback is used.")


@_look
def l_destructure_default(rng):
    d = pairs(rng)
    k = _missing(rng, d)
    n = _v(rng)
    return _L(f"{_decl(d)}\nconst {{ {k} = {n} }} = o;\n{k}", n, "A default in destructuring is used when the property is undefined.")


@_look
def l_count_loop(rng):
    w = rng.choice(["hello", "little", "banana", "balloon", "coffee", "pumpkin"])
    ch = rng.choice(w)
    n = 0
    for c in w:
        if c == ch:
            n += 1
    return _L(f'const counts = {{}};\nfor (const c of "{w}") counts[c] = (counts[c] || 0) + 1;\ncounts["{ch}"]', n, f'It counts each letter; "{ch}" appears {n} time(s).')


@_look
def l_array_as_obj(rng):
    xs = nums(rng, 3, 4)
    i = rng.randrange(len(xs))
    return _L(f'const a = {lit(xs)};\na["{i}"]', xs[i], 'Array indexes are property names too, so "1" works like 1.')


@_look
def l_typeof(rng):
    d = pairs(rng)
    return _L(f"{_decl(d)}\ntypeof o.{_missing(rng, d)}", "undefined", "typeof gives the TEXT \"undefined\" for a missing property.")


@_look
def l_null_prop(rng):
    k = rng.choice(WORDS)
    code, ans, why = rng.choice([(f'const o = {{ {k}: null }};\no.{k} ?? "x"', "x", "null counts as nothing for ??."),
                                 (f'const o = {{ {k}: null }};\no.{k}?.n', "undefined", "?. stops at null too and gives undefined."),
                                 (f'const o = {{ {k}: undefined }};\n"{k}" in o', "true", "The property exists, even though its value is undefined.")])
    return _L(code, ans, why)


# ── 4. Set Maths ────────────────────────────────────────────────────────

SETS: list[Maker] = []


def _set(fn: Maker) -> Maker:
    SETS.append(fn)
    return fn


def _ab(rng: random.Random) -> tuple[list[int], list[int]]:
    while True:
        a, b = ints(rng, rng.randint(3, 4), 1, 8), ints(rng, 3, 1, 8)
        if inter(a, b) and diff(a, b) and diff(b, a):
            return a, b


def _decl_ab(a: list[int], b: list[int]) -> str:
    return f"const a = new Set({lit(a)});\nconst b = new Set({lit(b)});\n"


def _S(a, b, tail: str, ans, why: str) -> Item:
    return Item(_decl_ab(a, b) + tail, str(ans), why)


@_set
def s_union(rng):
    a, b = _ab(rng)
    return _S(a, b, "[...new Set([...a, ...b])]", js_show(union(a, b)), "Spreading both into a new Set drops the repeats; a Set keeps the order values were added.")


@_set
def s_union_sorted(rng):
    a, b = _ab(rng)
    return _S(a, b, "[...new Set([...a, ...b])].sort((x, y) => x - y)", js_show(sort_by(union(a, b))), "The union, then sorted as numbers.")


@_set
def s_inter(rng):
    a, b = _ab(rng)
    return _S(a, b, "[...a].filter(x => b.has(x))", js_show(inter(a, b)), "Keep the items of a that b also has.")


@_set
def s_diff(rng):
    a, b = _ab(rng)
    return _S(a, b, "[...a].filter(x => !b.has(x))", js_show(diff(a, b)), "Keep the items of a that b does not have.")


@_set
def s_diff_rev(rng):
    a, b = _ab(rng)
    return _S(a, b, "[...b].filter(x => !a.has(x))", js_show(diff(b, a)), "Now it keeps what b has and a lacks: the order matters.")


@_set
def s_sym(rng):
    a, b = _ab(rng)
    return Item(_decl_ab(a, b) + "const only = (p, q) => [...p].filter(x => !q.has(x));\n[...only(a, b), ...only(b, a)]",
                js_show(sym(a, b)), "What only a has, then what only b has.")


@_set
def s_union_size(rng):
    a, b = _ab(rng)
    return _S(a, b, "new Set([...a, ...b]).size", len(union(a, b)), "The union counts each value once.")


@_set
def s_inter_size(rng):
    a, b = _ab(rng)
    return _S(a, b, "[...a].filter(x => b.has(x)).length", len(inter(a, b)), "How many values the two sets share.")


@_set
def s_diff_size(rng):
    a, b = _ab(rng)
    return _S(a, b, "[...a].filter(x => !b.has(x)).length", len(diff(a, b)), "How many values are in a but not in b.")


@_set
def s_has(rng):
    a, b = _ab(rng)
    x = rng.randint(1, 8)
    return _S(a, b, f"a.has({x})", jb(has(a, x)), "has asks whether the set holds the value.")


@_set
def s_has_type(rng):
    n = rng.randint(1, 9)
    code, ans, why = rng.choice([(f'new Set([{n}]).has("{n}")', "false", "The number and the text are different values."),
                                 ("new Set([NaN]).has(NaN)", "true", "A Set treats NaN as equal to itself."),
                                 ("[NaN].includes(NaN)", "true", "includes treats NaN as equal to itself."),
                                 ("[NaN].indexOf(NaN)", "-1", "indexOf uses ===, and NaN === NaN is false, so it never matches.")])
    return Item(code, ans, why)


@_set
def s_size(rng):
    a, b = _ab(rng)
    return _S(a, b, "a.size", len(a), "size is the number of values in the set.")


@_set
def s_add_chain(rng):
    a, b = _ab(rng)
    k, new = rng.choice([(a[0], False), (9, True)])
    return _S(a, b, f"a.add({k}).size", len(a) + (1 if new else 0), "add returns the Set itself, so .size follows." + (" The new value counts." if new else " It was already there."))


@_set
def s_delete_returns(rng):
    a, b = _ab(rng)
    k, found = rng.choice([(a[0], True), (9, False)])
    return _S(a, b, f"a.delete({k})", jb(found), "delete says whether the value was there to remove.")


@_set
def s_delete_size(rng):
    a, b = _ab(rng)
    return _S(a, b, f"a.delete({a[0]});\na.size", len(a) - 1, "delete removes the value.")


@_set
def s_dedupe(rng):
    xs = dupes(rng)
    return Item(f"[...new Set({lit(xs)})]", js_show(uniq(xs)), "A Set drops the repeats and keeps first-seen order.")


@_set
def s_dedupe_len(rng):
    xs = dupes(rng)
    return Item(f"Array.from(new Set({lit(xs)})).length", str(len(uniq(xs))), "Array.from turns the Set back into an array of the different values.")


@_set
def s_letters(rng):
    w = rng.choice(["hello", "little", "banana", "balloon", "carrot", "coffee", "pumpkin"])
    return Item(f'[...new Set("{w}")].join("")', "".join(uniq(list(w))), "The different letters in first-seen order, glued together.")


@_set
def s_every(rng):
    b = ints(rng, 4, 1, 8)
    ok = rng.random() < 0.5
    a = take(b, 0, 2) if ok else take(b, 0, 2) + [9]
    return _S(a, b, "[...a].every(x => b.has(x))", jb(ok), "True only if every value of a is also in b: a subset test.")


@_set
def s_some(rng):
    a, b = _ab(rng)
    if rng.random() < 0.5:
        b = diff(b, a)
    return _S(a, b, "[...a].some(x => b.has(x))", jb(bool(inter(a, b))), "True if the sets share at least one value.")


@_set
def s_union_method(rng):
    a, b = _ab(rng)
    return _S(a, b, "a.union(b).size", len(union(a, b)), "Sets have a union method now; size counts the result.")


@_set
def s_inter_method(rng):
    a, b = _ab(rng)
    return _S(a, b, "a.intersection(b).size", len(inter(a, b)), "intersection gives the shared values.")


@_set
def s_diff_method(rng):
    a, b = _ab(rng)
    return _S(a, b, "a.difference(b).size", len(diff(a, b)), "difference gives what a has that b does not.")


@_set
def s_sym_method(rng):
    a, b = _ab(rng)
    return _S(a, b, "a.symmetricDifference(b).size", len(sym(a, b)), "symmetricDifference keeps values that are in only one of the sets.")


@_set
def s_subset_method(rng):
    b = ints(rng, 4, 1, 8)
    ok = rng.random() < 0.5
    a = take(b, 1, 3) if ok else take(b, 1, 3) + [9]
    return _S(a, b, "a.isSubsetOf(b)", jb(ok), "isSubsetOf is true when every value of a is in b.")


@_set
def s_disjoint_method(rng):
    a, b = _ab(rng)
    if rng.random() < 0.5:
        b = diff(b, a)
    return _S(a, b, "a.isDisjointFrom(b)", jb(not inter(a, b)), "isDisjointFrom is true when the sets share nothing.")


@_set
def s_not_equal(rng):
    a = ints(rng, 2, 1, 9)
    return Item(f"new Set({lit(a)}) === new Set({lit(a)})", "false", "=== compares objects by identity: two separate Sets are never ===.")


@_set
def s_same_size(rng):
    a, b = _ab(rng)
    return _S(a, b, "a.size === b.size", jb(len(a) == len(b)), "Only the counts are compared, not the members.")


@_set
def s_second(rng):
    a, b = _ab(rng)
    return _S(a, b, "[...a][1]", a[1], "Spreading a Set gives its values in insertion order.")


@_set
def s_first(rng):
    a, b = _ab(rng)
    return _S(a, b, "a.values().next().value", a[0], "The first value added comes out first.")


@_set
def s_max(rng):
    a, b = _ab(rng)
    return _S(a, b, "Math.max(...a)", best(a), "The spread feeds every value of the set to Math.max.")


@_set
def s_sum(rng):
    a, b = _ab(rng)
    return _S(a, b, "[...a].reduce((t, x) => t + x, 0)", total(a), "Adds up each value once.")


@_set
def s_same_object(rng):
    return Item("const o = {};\nnew Set([o, o]).size", "1", "It is the SAME object twice, so the set keeps one.")


@_set
def s_order(rng):
    a, b, c = ints(rng, 3, 1, 9)
    return Item(f"const s = new Set([{a}, {b}]);\ns.add({c});\ns.delete({a});\ns.add({a});\n[...s]", js_show([b, c, a]),
                "Deleting and re-adding a value puts it at the END of the order.")


@_set
def s_mod(rng):
    xs = nums(rng, 5, 6)
    return Item(f"[...new Set({lit(xs)}.map(x => x % 3))]", js_show(uniq([fmod(x, 3) for x in xs])), "x % 3 is 0, 1 or 2; the set keeps each result once, in first-seen order.")


@_set
def s_clear(rng):
    a, b = _ab(rng)
    return _S(a, b, "a.clear();\na.size", 0, "clear empties the set.")


# ── 5. Min Max Sum ──────────────────────────────────────────────────────

MINMAX: list[Maker] = []


def _mm(fn: Maker) -> Maker:
    MINMAX.append(fn)
    return fn


def _signed(rng: random.Random, lo: int = 4, hi: int = 6) -> list[int]:
    while True:
        xs = ints(rng, rng.randint(lo, hi), -9, 9)
        if any(x < 0 for x in xs) and any(x > 0 for x in xs):
            return xs


def _M(code: str, ans, why: str) -> Item:
    return Item(code, str(ans), why)


@_mm
def m_max(rng):
    xs = nums(rng, 4, 6)
    return _M(f"Math.max(...{lit(xs)})", best(xs), "The spread passes each item as a separate argument.")


@_mm
def m_min(rng):
    xs = nums(rng, 4, 6)
    return _M(f"Math.min(...{lit(xs)})", best(xs, want_max=False), "Math.min takes the smallest of its arguments.")


@_mm
def m_args(rng):
    xs = ints(rng, 3, -9, 9)
    return _M(f"Math.max({', '.join(map(str, xs))})", best(xs), "The biggest of the arguments.")


@_mm
def m_sum(rng):
    xs = nums(rng, 4, 6)
    return _M(f"{lit(xs)}.reduce((a, b) => a + b, 0)", total(xs), "reduce keeps a running total, starting from 0.")


@_mm
def m_max_neg(rng):
    xs = _signed(rng)
    return _M(f"Math.max(...{lit(xs)})", best(xs), "With negatives, the biggest is the one nearest the positive side.")


@_mm
def m_min_neg(rng):
    xs = _signed(rng)
    return _M(f"Math.min(...{lit(xs)})", best(xs, want_max=False), "The most negative number is the minimum.")


@_mm
def m_sum_neg(rng):
    xs = _signed(rng)
    return _M(f"{lit(xs)}.reduce((a, b) => a + b, 0)", total(xs), "Negative items subtract as they are added.")


@_mm
def m_empty(rng):
    code, ans, why = rng.choice([("Math.max()", "-Infinity", "With nothing to compare, max starts from -Infinity."),
                                 ("Math.min()", "Infinity", "With nothing to compare, min starts from Infinity."),
                                 ("Math.max(...[])", "-Infinity", "Spreading an empty array passes nothing, so -Infinity."),
                                 ("[].reduce((a, b) => a + b, 0)", "0", "With an initial value, an empty reduce gives that value.")])
    return _M(code, ans, why)


@_mm
def m_empty_reduce(rng):
    return Item("[].reduce((a, b) => a + b)", "TypeError", "reduce with no initial value on an empty array throws.", check=err_js("[].reduce((a, b) => a + b)"))


@_mm
def m_coerce(rng):
    n = rng.randint(1, 9)
    code, ans, why = rng.choice([
        (f'Math.max({n}, "{n + 3}")', n + 3, "Math.max turns the string into a number."),
        (f'Math.max({n}, "a")', "NaN", "\"a\" is not a number: the whole answer is NaN."),
        (f"Math.max({n}, undefined)", "NaN", "undefined becomes NaN, and NaN poisons the result."),
        (f"Math.max({n}, null)", n, "null counts as 0, which is less than " + str(n) + "."),
        (f"Math.min({n}, null)", 0, "null counts as 0, which is smaller."),
        (f"Math.max(-{n}, null)", 0, "null counts as 0, which beats a negative."),
        (f"Math.max([{n}])", n, "A one-item array turns into that number."),
        (f"Math.max([{n}, {n + 1}])", "NaN", "[a, b] turns into the text \"a,b\", which is not a number."),
    ])
    return _M(code, ans, why)


@_mm
def m_reduce_max(rng):
    xs = nums(rng, 4, 6)
    return _M(f"{lit(xs)}.reduce((a, b) => (a > b ? a : b))", best(xs), "It keeps the bigger of the running answer and the next item.")


@_mm
def m_reduce_text(rng):
    a, b, c = ints(rng, 3, 1, 9)
    code, ans, why = rng.choice([
        (f'["{a}", "{b}", "{c}"].reduce((x, y) => x + y)', f"{a}{b}{c}", "+ on strings joins them: it is text, not a sum."),
        (f'["{a}", "{b}", "{c}"].reduce((x, y) => x + Number(y), 0)', a + b + c, "Number() turns each string into a number before adding."),
        (f'[{a}, {b}, {c}].reduce((x, y) => x + y, "")', f"{a}{b}{c}", "Starting from an empty string, every + joins text."),
    ])
    return _M(code, ans, why)


@_mm
def m_avg(rng):
    xs = nums(rng, 4, 5)
    xs = take(xs, 0, rng.choice([2, 4, 5]) if len(xs) >= 5 else rng.choice([2, 4]))
    return _M(f"const xs = {lit(xs)};\nxs.reduce((a, b) => a + b, 0) / xs.length", decimal_div(total(xs), len(xs)), "The total divided by the count: a whole number prints without .0.")


@_mm
def m_avg_floor(rng):
    xs = nums(rng, 4, 5)
    n, t = len(xs), total(xs)
    q = 0
    while (q + 1) * n <= t:
        q += 1
    return _M(f"const xs = {lit(xs)};\nMath.floor(xs.reduce((a, b) => a + b, 0) / xs.length)", q, "Math.floor rounds the average down.")


@_mm
def m_sort_text_first(rng):
    xs = rng.choice([[10, 9, 2], [25, 3, 100], [8, 75, 100, 9], [30, 4, 12]])
    return _M(f"{lit(xs)}.sort()[0]", sort_by(xs, key=lambda n: str(n))[0], "sort() compares as text: the first character decides, so the smallest NUMBER is not always first.")


@_mm
def m_sort_text_last(rng):
    xs = rng.choice([[10, 9, 2], [25, 3, 100], [8, 75, 100, 9], [30, 4, 12]])
    return _M(f"{lit(xs)}.sort().at(-1)", sort_by(xs, key=lambda n: str(n))[len(xs) - 1], "Sorted as text, the last is the one with the biggest first digit - not the biggest number.")


@_mm
def m_sort_num_last(rng):
    xs = nums(rng, 4, 5)
    return _M(f"{lit(xs)}.sort((a, b) => a - b).at(-1)", best(xs), "Sorted as numbers, the last is the biggest.")


@_mm
def m_range(rng):
    xs = _signed(rng)
    return _M(f"const xs = {lit(xs)};\nMath.max(...xs) - Math.min(...xs)", best(xs) - best(xs, want_max=False), "Biggest minus smallest: the spread.")


@_mm
def m_word_len(rng):
    ws = words(rng, 4)
    return _M(f"Math.max(...{lit(ws)}.map(w => w.length))", best([len(w) for w in ws]), "map turns the words into lengths; max picks the biggest length.")


@_mm
def m_longest(rng):
    ws = words(rng, 4)
    return _M(f"{lit(ws)}.reduce((a, w) => (w.length > a.length ? w : a))", best(ws, key=len), "A word replaces the leader only if it is strictly longer, so the first of equals wins.")


@_mm
def m_filter_count(rng):
    xs, k = nums(rng, 5, 6), rng.randint(3, 6)
    return _M(f"{lit(xs)}.filter(x => x > {k}).length", len([x for x in xs if x > k]), f"How many items are bigger than {k}.")


@_mm
def m_min_positive(rng):
    xs = _signed(rng)
    return _M(f"Math.min(...{lit(xs)}.filter(x => x > 0))", best([x for x in xs if x > 0], want_max=False), "Drop the negatives and zeros first, then take the smallest.")


@_mm
def m_abs_max(rng):
    xs = _signed(rng)
    return _M(f"Math.max(...{lit(xs)}.map(Math.abs))", best([x if x >= 0 else -x for x in xs]), "map(Math.abs) drops the signs; max picks the biggest size.")


@_mm
def m_index_max(rng):
    xs = nums(rng, 4, 6)
    return _M(f"const xs = {lit(xs)};\nxs.indexOf(Math.max(...xs))", pos(xs, best(xs)), "max finds the biggest value; indexOf says where it sits.")


@_mm
def m_sum_slice(rng):
    xs = nums(rng, 5, 6)
    return _M(f"{lit(xs)}.slice(-2).reduce((a, b) => a + b, 0)", total(take(xs, len(xs) - 2, len(xs))), "The last two items, added.")


@_mm
def m_digits(rng):
    n = rng.randint(1000, 99999)
    return _M(f'[..."{n}"].reduce((t, d) => t + Number(d), 0)', total([int(c) for c in str(n)]), "Spread the number's text into digits, convert each, and add.")


@_mm
def m_obj_max(rng):
    d = pairs(rng)
    return _M(f"const o = {olit(d)};\nMath.max(...Object.values(o))", best([v for _, v in d]), "values() lists the numbers; max picks the biggest.")


@_mm
def m_obj_sum(rng):
    d = pairs(rng)
    return _M(f"const o = {olit(d)};\nObject.values(o).reduce((t, v) => t + v, 0)", total([v for _, v in d]), "Add up what the object stores.")


@_mm
def m_product(rng):
    xs = ints(rng, 3, 2, 6)
    return _M(f"{lit(xs)}.reduce((a, b) => a * b)", xs[0] * xs[1] * xs[2], "Each step multiplies the running answer by the next item.")


@_mm
def m_text_compare(rng):
    code, ans, why = rng.choice([('"9" > "10"', "true", "Two strings compare character by character: '9' beats '1'."),
                                 ('9 > "10"', "false", "A number and a string compare as numbers: 9 is not more than 10."),
                                 ('"apple" < "banana"', "true", "Strings compare like a dictionary."),
                                 ('"B" < "a"', "true", "Capital letters come before lower-case ones.")])
    return _M(code, ans, why)


@_mm
def m_text_sorted_ends(rng):
    xs = rng.choice([["10", "9", "100"], ["8", "75", "100", "9"], ["20", "3", "100"]])
    code, i = rng.choice([("[0]", 0), (".at(-1)", len(xs) - 1)])
    return _M(f"{lit(xs)}.sort(){code}", sort_by(xs)[i], "Strings sort character by character, not by size.")


@_mm
def m_max_numstrs(rng):
    a, b = rng.choice([("10", "9"), ("100", "25"), ("30", "4")])
    return _M(f'Math.max("{a}", "{b}")', best([int(a), int(b)]), "Math.max turns the strings into numbers, so it compares them as numbers.")


# ── 6. Unpack It ────────────────────────────────────────────────────────

UNPACK: list[Maker] = []


def _un(fn: Maker) -> Maker:
    UNPACK.append(fn)
    return fn


def _U(code: str, ans, why: str, err: bool = False) -> Item:
    return Item(code, str(ans), why, check=err_js(code) if err else "")


def _odecl(d: list) -> str:
    return f"const o = {olit(d)};"


@_un
def u_basic(rng):
    xs = nums(rng, 3, 3)
    return _U(f"const [a, b, c] = {lit(xs)};\nb", xs[1], "The names take the items in order.")


@_un
def u_skip(rng):
    xs = nums(rng, 3, 3)
    return _U(f"const [a, , c] = {lit(xs)};\nc", xs[2], "An empty slot between commas skips an item.")


@_un
def u_second(rng):
    xs = nums(rng, 3, 4)
    return _U(f"const [, second] = {lit(xs)};\nsecond", xs[1], "The leading comma skips the first item.")


@_un
def u_rest(rng):
    xs = nums(rng, 4, 5)
    return _U(f"const [first, ...rest] = {lit(xs)};\nrest", js_show(take(xs, 1, len(xs))), "...rest collects everything the other names did not take, as an array.")


@_un
def u_first(rng):
    xs = nums(rng, 4, 5)
    return _U(f"const [first, ...rest] = {lit(xs)};\nfirst", xs[0], "first takes just the first item.")


@_un
def u_swap(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"let a = {a}, b = {b};\n[a, b] = [b, a];\na", b, "The right side is built first, then both names are set: a takes b's old value.")


@_un
def u_swap_array(rng):
    xs = nums(rng, 4, 5)
    out = [xs[1], xs[0]] + take(xs, 2, len(xs))
    return _U(f"const xs = {lit(xs)};\n[xs[0], xs[1]] = [xs[1], xs[0]];\nxs", js_show(out), "The first two items trade places.")


@_un
def u_fib(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"let a = {a}, b = {b};\n[a, b] = [b, a + b];\nb", a + b, "The right side uses the OLD a and b, so the new b is old a + old b.")


@_un
def u_rotate(rng):
    a, b, c = ints(rng, 3, 1, 9)
    return _U(f"let a = {a}, b = {b}, c = {c};\n[a, b, c] = [b, c, a];\n[a, b, c]", js_show([b, c, a]), "Each name takes the next one's old value.")


@_un
def u_default_missing(rng):
    a, d1, d2 = ints(rng, 3, 1, 9)
    return _U(f"const [a = {d1}, b = {d2}] = [{a}];\nb", d2, "b has no item, so its default is used.")


@_un
def u_default_present(rng):
    a, d1, d2 = ints(rng, 3, 1, 9)
    return _U(f"const [a = {d1}, b = {d2}] = [{a}];\na", a, "a has an item, so the default is ignored.")


@_un
def u_default_null(rng):
    d = _v(rng)
    return _U(f"const [a = {d}] = [null];\na", "null", "A default only replaces undefined; null is a real value and stays.")


@_un
def u_default_undefined(rng):
    d = _v(rng)
    return _U(f"const [a = {d}] = [undefined];\na", d, "undefined triggers the default.")


@_un
def u_too_few(rng):
    xs = nums(rng, 2, 2)
    return _U(f"const [a, b, c] = {lit(xs)};\nc", "undefined", "There is no third item, and JavaScript gives undefined instead of an error.")


@_un
def u_default_other(rng):
    n = rng.randint(2, 6)
    return _U(f"const [x, y = x * 2] = [{n}];\ny", n * 2, "A default can use a name that came earlier in the pattern.")


@_un
def u_obj(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _U(f"{_odecl(d)}\nconst {{ {d[0][0]}, {d[1][0]}, {d[2][0]} }} = o;\n{k}", v, "Each name picks the property with the same name.")


@_un
def u_obj_rename(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _U(f"{_odecl(d)}\nconst {{ {k}: f }} = o;\nf", v, "{ name: f } reads the property name into a variable called f.")


@_un
def u_obj_default(rng):
    d = pairs(rng)
    k = rng.choice([w for w in WORDS if not d_has(d, w)])
    n = _v(rng)
    return _U(f"{_odecl(d)}\nconst {{ {k} = {n} }} = o;\n{k}", n, "The property is missing, so the default is used.")


@_un
def u_obj_missing(rng):
    k = rng.choice(WORDS)
    return _U(f"const {{ {k} }} = {{}};\n{k}", "undefined", "A missing property just gives undefined.")


@_un
def u_obj_rest(rng):
    d = pairs(rng)
    return _U(f"{_odecl(d)}\nconst {{ {d[0][0]}, ...others }} = o;\nothers", js_show({k: v for k, v in d[1:]}), "...others collects the properties that were not named.")


@_un
def u_obj_nested(rng):
    k1, k2 = rng.sample(WORDS, 2)
    v = _v(rng)
    return _U(f"const {{ {k1}: {{ {k2} }} }} = {{ {k1}: {{ {k2}: {v} }} }};\n{k2}", v, "The inner braces reach into the nested object.")


@_un
def u_arr_nested(rng):
    a, b, c = ints(rng, 3, 1, 9)
    return _U(f"const [a, [b, c]] = [{a}, [{b}, {c}]];\nc", c, "The inner brackets unpack the inner array.")


@_un
def u_string(rng):
    w = rng.choice([w for w in WORDS if len(w) == 3])
    return _U(f'const [a, b] = "{w}";\nb', w[1], "A string unpacks character by character.")


@_un
def u_string_rest(rng):
    w = rng.choice([w for w in WORDS if len(w) >= 4])
    return _U(f'const [h, ...t] = "{w}";\nt', js_show(list(w[1:])), "The rest is an array of one-character strings.")


@_un
def u_set(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"const [x, y] = new Set([{a}, {b}]);\ny", b, "Any iterable unpacks - a Set gives its values in insertion order.")


@_un
def u_length(rng):
    w = rng.choice(WORDS)
    return _U(f'const {{ length }} = "{w}";\nlength', len(w), "A string has a length property, so it can be destructured.")


@_un
def u_entries(rng):
    d = pairs(rng)
    return _U(f"{_odecl(d)}\nconst [k, v] = Object.entries(o)[0];\nv", d[0][1], "An entry is a [name, value] pair, which unpacks into k and v.")


@_un
def u_param_obj(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"function f({{ a, b = {b} }}) {{\n  return a + b;\n}}\nf({{ a: {a} }})", a + b, "The parameter is destructured, and b falls back to its default.")


@_un
def u_param_arr(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"const f = ([a, b]) => a - b;\nf([{a}, {b}])", a - b, "The array argument is unpacked right in the parameter list.")


@_un
def u_rest_param(rng):
    a, b, c = ints(rng, 3, 1, 9)
    return _U(f"function f(a, ...r) {{\n  return r;\n}}\nf({a}, {b}, {c})", js_show([b, c]), "...r collects the extra arguments into an array.")


@_un
def u_null_error(rng):
    code, why = rng.choice([("const { a } = null;\na", "null has no properties to read: TypeError."),
                            ("const { a } = undefined;\na", "undefined has no properties to read: TypeError."),
                            ("const [a] = null;\na", "null is not iterable: TypeError."),
                            ("const [a, b] = 5;\na", "A number is not iterable: TypeError.")])
    return _U(code, "TypeError", why, True)


@_un
def u_assign_expr(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"let a, b;\n({{ a, b }} = {{ a: {a}, b: {b} }});\nb", b, "Wrapping the assignment in brackets stops { from starting a block.")


@_un
def u_for_entries(rng):
    d = pairs(rng)
    return _U(f"{_odecl(d)}\nlet t = 0;\nfor (const [k, v] of Object.entries(o)) t += v;\nt", total([v for _, v in d]), "Each entry unpacks into k and v, and the values add up.")


@_un
def u_map_param(rng):
    a, b = ints(rng, 2, 1, 5)
    return _U(f"[{{ n: {a} }}, {{ n: {b} }}].map(({{ n }}) => n * 2)[1]", b * 2, "The parameter pulls n out of each object.")


@_un
def u_spread_call(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"const f = (a, b) => a - b;\nf(...[{a}, {b}])", a - b, "The spread turns the array into separate arguments.")


@_un
def u_default_twice(rng):
    return _U("const { a = 1, b = 2 } = { a: undefined, b: null };\n[a, b]", js_show([1, NULL]), "undefined takes the default (a = 1); null does not, so b stays null.")


@_un
def u_default_chain(rng):
    n = rng.randint(2, 6)
    return _U(f"const [a, b = a] = [{n}];\nb", n, "b has no item, so it copies a.")


# ── 7. Nested Reach ─────────────────────────────────────────────────────

NESTED: list[Maker] = []


def _ne(fn: Maker) -> Maker:
    NESTED.append(fn)
    return fn


def _N(code: str, ans, why: str, err: bool = False) -> Item:
    return Item(code, str(ans), why, check=err_js(code) if err else "")


def _grid(rng: random.Random, rows: int | None = None, cols: int | None = None) -> list[list[int]]:
    r, c = rows or rng.randint(2, 3), cols or rng.randint(3, 4)
    return [ints(rng, c, 1, 9) for _ in range(r)]


@_ne
def n_grid(rng):
    g = _grid(rng)
    r, c = rng.randrange(len(g)), rng.randrange(len(g[0]))
    return _N(f"const grid = {lit(g)};\ngrid[{r}][{c}]", g[r][c], "The first [] picks the row, the second the item in it.")


@_ne
def n_grid_at(rng):
    g = _grid(rng)
    return _N(f"const grid = {lit(g)};\ngrid.at(-1).at(-1)", g[len(g) - 1][len(g[0]) - 1], "at(-1) is the last row; its at(-1) the last item.")


@_ne
def n_grid_row(rng):
    g = _grid(rng)
    r = rng.randrange(len(g))
    return _N(f"const grid = {lit(g)};\ngrid[{r}]", js_show(g[r]), "One index gives a whole row.")


@_ne
def n_grid_col(rng):
    g = _grid(rng)
    c = rng.randrange(len(g[0]))
    return _N(f"const grid = {lit(g)};\ngrid.map(row => row[{c}])", js_show([row[c] for row in g]), "It takes the same position from every row: a column.")


@_ne
def n_grid_rows(rng):
    g = _grid(rng)
    return _N(f"const grid = {lit(g)};\ngrid.length", len(g), "length of the outer array counts the rows.")


@_ne
def n_grid_cols(rng):
    g = _grid(rng)
    return _N(f"const grid = {lit(g)};\ngrid[0].length", len(g[0]), "grid[0] is a row; its length counts the columns.")


@_ne
def n_grid_sum_row(rng):
    g = _grid(rng)
    r = rng.randrange(len(g))
    return _N(f"const grid = {lit(g)};\ngrid[{r}].reduce((a, b) => a + b, 0)", total(g[r]), "grid[r] is one row; reduce adds its items.")


@_ne
def n_grid_diag(rng):
    g = _grid(rng, 3, 3)
    return _N(f"const grid = {lit(g)};\ngrid.map((row, i) => row[i])", js_show([g[i][i] for i in range(3)]), "Row 0 column 0, row 1 column 1, row 2 column 2.")


@_ne
def n_grid_flat_len(rng):
    g = _grid(rng)
    return _N(f"const grid = {lit(g)};\ngrid.flat().length", len(g) * len(g[0]), "flat() joins the rows: rows times columns.")


@_ne
def n_grid_flat_i(rng):
    g = _grid(rng)
    flat = [x for row in g for x in row]
    k = rng.randrange(len(flat))
    return _N(f"const grid = {lit(g)};\ngrid.flat()[{k}]", flat[k], "The flat array reads row after row, left to right.")


@_ne
def n_grid_past_row(rng):
    g = _grid(rng)
    return _N(f"const grid = {lit(g)};\ngrid[{len(g)}][0]", "TypeError", "There is no such row, so grid[n] is undefined - and undefined[0] is a TypeError.", True)


@_ne
def n_grid_past_col(rng):
    g = _grid(rng)
    return _N(f"const grid = {lit(g)};\ngrid[0][{len(g[0])}]", "undefined", "Past the end of a row is just undefined.")


@_ne
def n_grid_optional(rng):
    g = _grid(rng)
    return _N(f"const grid = {lit(g)};\ngrid[{len(g)}]?.[0]", "undefined", "?. stops at undefined instead of throwing.")


@_ne
def n_alias_rows(rng):
    v = rng.randint(5, 9)
    return _N(f"const g = Array(2).fill([0, 0]);\ng[0][0] = {v};\ng", f"[ [ {v}, 0 ], [ {v}, 0 ] ]", "fill puts the SAME inner array in every slot, so a change shows in both.")


@_ne
def n_fresh_rows(rng):
    v = rng.randint(5, 9)
    return _N(f"const g = Array.from({{ length: 2 }}, () => [0, 0]);\ng[0][0] = {v};\ng", f"[ [ {v}, 0 ], [ 0, 0 ] ]", "The function builds a fresh row each time, so only one changes.")


@_ne
def n_shallow(rng):
    a, b = ints(rng, 2, 1, 9)
    return _N(f"const a = [[{a}], [{b}]];\nconst b = [...a];\nb[0].push(9);\na[0]", js_show([a, 9]), "The spread copy is shallow: the inner arrays are shared.")


@_ne
def n_deep(rng):
    a, b = ints(rng, 2, 1, 9)
    return _N(f"const a = [[{a}], [{b}]];\nconst b = JSON.parse(JSON.stringify(a));\nb[0].push(9);\na[0]", js_show([a]), "A JSON round trip copies every level, so a is untouched.")


@_ne
def n_obj2(rng):
    k1, k2 = rng.sample(WORDS, 2)
    v = _v(rng)
    return _N(f"const o = {{ {k1}: {{ {k2}: {v} }} }};\no.{k1}.{k2}", v, "Each dot goes one level deeper.")


@_ne
def n_obj3(rng):
    k1, k2, k3 = rng.sample(WORDS, 3)
    v = _v(rng)
    return _N(f"const o = {{ {k1}: {{ {k2}: {{ {k3}: {v} }} }} }};\no.{k1}.{k2}.{k3}", v, "One dot per level, outermost first.")


@_ne
def n_deep_mix(rng):
    v, w = ints(rng, 2, 1, 9)
    return _N(f"const data = {{ a: [{w}, {{ b: {v} }}] }};\ndata.a[1].b", v, "data.a is an array, [1] its second item (an object), .b looks inside it.")


@_ne
def n_deep_first(rng):
    v, w = ints(rng, 2, 1, 9)
    return _N(f"const data = {{ a: [{w}, {{ b: {v} }}] }};\ndata.a[0]", w, "data.a[0] is the first item of the array: the plain number.")


@_ne
def n_users(rng):
    ws = words(rng, 4)
    return _N(f'const data = {{ users: [{{ name: "{ws[0]}", tags: ["{ws[1]}", "{ws[2]}"] }}] }};\ndata.users[0].tags[1]', ws[2],
              "users is an array, [0] an object, .tags an array, [1] its second item.")


@_ne
def n_list_obj(rng):
    ws = words(rng, 2)
    vs = ints(rng, 2, 1, 9)
    i = rng.randrange(2)
    data = "[" + ", ".join(f'{{ name: "{w}", n: {v} }}' for w, v in zip(ws, vs)) + "]"
    return _N(f"const data = {data};\ndata[{i}].n", vs[i], "data[i] is an object; then read its property.")


@_ne
def n_list_obj_name(rng):
    ws = words(rng, 2)
    vs = ints(rng, 2, 1, 9)
    data = "[" + ", ".join(f'{{ name: "{w}", n: {v} }}' for w, v in zip(ws, vs)) + "]"
    return _N(f"const data = {data};\ndata.at(-1).name", ws[1], "at(-1) is the last object; read its name.")


@_ne
def n_optional_missing(rng):
    k1, k2 = rng.sample(WORDS, 2)
    return _N(f"const o = {{ {k1}: {{ n: {_v(rng)} }} }};\no.{k2}?.n", "undefined", "o.name is undefined, and ?. stops there.")


@_ne
def n_chain_error(rng):
    k1, k2 = rng.sample(WORDS, 2)
    return _N(f"const o = {{ {k1}: {{ n: {_v(rng)} }} }};\no.{k2}.n", "TypeError", "o.name is undefined, and reading .n of undefined throws a TypeError.", True)


@_ne
def n_optional_index(rng):
    k = rng.choice(WORDS)
    xs = nums(rng, 2, 3)
    return _N(f"const o = {{ {k}: {lit(xs)} }};\no.{k}?.[{len(xs)}]?.n", "undefined", "Index past the end gives undefined, and the second ?. stops there.")


@_ne
def n_push_inner(rng):
    k = rng.choice(WORDS)
    xs, v = nums(rng, 2, 3), _v(rng)
    return _N(f"const o = {{ {k}: {lit(xs)} }};\no.{k}.push({v});\no.{k}", js_show(xs + [v]), "o.name is the array itself, so push changes it in place.")


@_ne
def n_inc(rng):
    v = _v(rng)
    return _N(f"const data = {{ a: [0, {{ b: {v} }}] }};\ndata.a[1].b += 1;\ndata.a[1].b", v + 1, "+= reads the inner value, adds one and stores it back there.")


@_ne
def n_len_inner(rng):
    k = rng.choice(WORDS)
    xs = nums(rng, 3, 5)
    return _N(f"const o = {{ {k}: {lit(xs)} }};\no.{k}.length", len(xs), "o.name is the array; length counts its items.")


@_ne
def n_keys_inner(rng):
    k1, k2, k3 = rng.sample(WORDS, 3)
    return _N(f"const o = {{ {k1}: {{ {k2}: 1, {k3}: 2 }} }};\nObject.keys(o.{k1})[1]", k3, "keys of the inner object, in the order they were written.")


@_ne
def n_in_inner(rng):
    k1, k2 = rng.sample(WORDS, 2)
    code, ans, why = rng.choice([(f'const o = {{ {k1}: {{ {k2}: 1 }} }};\n"{k2}" in o.{k1}', "true", "o.name is the inner object, and the key is in it."),
                                 (f'const o = {{ {k1}: {{ {k2}: 1 }} }};\n"{k2}" in o', "false", "The outer object only has the key " + k1 + ".")])
    return _N(code, ans, why)


@_ne
def n_entries_nested(rng):
    k = rng.choice(WORDS)
    xs = nums(rng, 2, 3)
    return _N(f"const o = {{ {k}: {lit(xs)} }};\nObject.entries(o)[0][1]", js_show(xs), "entries()[0] is [key, value]; [1] is the value: the whole array.")


@_ne
def n_map_arrays(rng):
    k = rng.choice(WORDS)
    xs = nums(rng, 2, 3)
    return _N(f'const m = new Map([["{k}", {lit(xs)}]]);\nm.get("{k}")[1]', xs[1], "m.get gives the array; [1] picks its second item.")


@_ne
def n_str_in_array(rng):
    ws = words(rng, 3)
    i = rng.randrange(3)
    return _N(f"{lit(ws)}[{i}][0]", ws[i][0], "The array item is a word; [0] is its first letter.")


@_ne
def n_map_col(rng):
    g = _grid(rng, 2, 2)
    return _N(f"{lit(g)}.map(r => r[1])", js_show([g[0][1], g[1][1]]), "r[1] takes the second item of every row.")


@_ne
def n_flat_one(rng):
    a, b, c = ints(rng, 3, 1, 9)
    code, ans, why = rng.choice([(f"[[{a}, {b}], [{c}]].flat()", js_show([a, b, c]), "flat() joins the inner arrays into one."),
                                 (f"[[{a}, [{b}]], [{c}]].flat()", js_show([a, [b], c]), "flat() only goes one level deep: [b] stays an array."),
                                 (f"[[{a}, [{b}]], [{c}]].flat(2)", js_show([a, b, c]), "flat(2) goes two levels deep."),
                                 (f"[{a}, [{b}, [{c}, [{a}]]]].flat(Infinity).length", "4", "Infinity flattens every level: four numbers.")])
    return _N(code, ans, why)


@_ne
def n_identity(rng):
    a, b, c, d = ints(rng, 4, 1, 9)
    code, ans, why = rng.choice([(f"[[{a}, {b}], [{c}, {d}]].indexOf([{c}, {d}])", "-1", "indexOf compares objects by identity, and the new [c, d] is a different array."),
                                 (f"[[{a}, {b}], [{c}, {d}]].findIndex(r => r[0] === {c})", "1", "findIndex runs a test on each inner array."),
                                 (f"[[{a}]].includes([{a}])", "false", "includes compares arrays by identity too."),
                                 (f"[{a}, {b}] === [{a}, {b}]", "false", "Two separate arrays are never ===, even with the same items.")])
    return _N(code, ans, why)


@_ne
def n_typeof(rng):
    k = rng.choice(WORDS)
    code, ans, why = rng.choice([(f"const o = {{ {k}: [1] }};\nArray.isArray(o.{k})", "true", "isArray is the reliable way to tell an array from a plain object."),
                                 (f"const o = {{ {k}: [1] }};\ntypeof o.{k}", "object", "typeof says object for arrays too.")])
    return _N(code, ans, why)


# ── 8. Sort Order ───────────────────────────────────────────────────────

SORTS: list[Maker] = []


def _so(fn: Maker) -> Maker:
    SORTS.append(fn)
    return fn


def _S2(code: str, ans, why: str, err: bool = False) -> Item:
    return Item(code, str(ans), why, check=err_js(code) if err else "")


def _wide(rng: random.Random, n: int = 4) -> list[int]:
    """Numbers whose text order differs from their number order (a mix of 1 and 2 digit ones)."""
    while True:
        xs = rng.sample(range(1, 10), n // 2) + rng.sample(range(10, 100), n - n // 2)
        rng.shuffle(xs)
        if sort_by(xs, key=lambda v: str(v)) != sort_by(xs):
            return xs


def _txt(xs: list) -> list:
    return sort_by(xs, key=lambda v: str(v))


def _lower(w: str) -> str:
    return "".join(chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in w)


@_so
def so_default_first(rng):
    xs = _wide(rng)
    return _S2(f"{lit(xs)}.sort()[0]", _txt(xs)[0], "sort() with no function compares as text, so '10' comes before '9'.")


@_so
def so_default_last(rng):
    xs = _wide(rng)
    return _S2(f"{lit(xs)}.sort().at(-1)", _txt(xs)[len(xs) - 1], "Sorted as text, the last is the one with the biggest first digit - not the biggest number.")


@_so
def so_default_all(rng):
    xs = _wide(rng, 4)
    return _S2(f"{lit(xs)}.sort()", js_show(_txt(xs)), "Default sort is by text: the first character decides.")


@_so
def so_default_rev(rng):
    xs = _wide(rng)
    return _S2(f"{lit(xs)}.sort().reverse()[0]", _txt(xs)[len(xs) - 1], "Sort as text, then reverse: the text-biggest comes first.")


@_so
def so_num_first(rng):
    xs = _wide(rng)
    return _S2(f"{lit(xs)}.sort((a, b) => a - b)[0]", sort_by(xs)[0], "a - b compares as numbers: the smallest first.")


@_so
def so_num_desc(rng):
    xs = _wide(rng)
    return _S2(f"{lit(xs)}.sort((a, b) => b - a)[0]", sort_by(xs, reverse=True)[0], "b - a flips it: the biggest first.")


@_so
def so_num_last(rng):
    xs = nums(rng, 4, 6)
    return _S2(f"{lit(xs)}.sort((a, b) => a - b).at(-1)", sort_by(xs)[len(xs) - 1], "Sorted as numbers, the last is the biggest.")


@_so
def so_num_all(rng):
    xs = nums(rng, 4, 6)
    return _S2(f"{lit(xs)}.sort((a, b) => a - b)", js_show(sort_by(xs)), "The comparator makes it a numeric sort.")


@_so
def so_negatives(rng):
    xs = rng.choice([[-1, -2, 10], [-5, 3, -10, 20], [-3, 25, -30], [7, -7, 70, -70]])
    return _S2(f"{lit(xs)}.sort()", js_show(_txt(xs)), "As text, '-' sorts before digits and '-1' before '-2': the numbers come out in a surprising order.")


@_so
def so_undefined(rng):
    a, b = ints(rng, 2, 1, 9)
    return _S2(f"[{a}, undefined, {b}].sort()", js_show(sort_by([a, b]) + [UNDEF]), "undefined always sorts to the end.")


@_so
def so_undefined_cmp(rng):
    a, b = ints(rng, 2, 1, 9)
    return _S2(f"[{a}, undefined, {b}].sort((x, y) => x - y)", js_show(sort_by([a, b]) + [UNDEF]), "Even with a comparator, undefined goes last (it is never compared).")


@_so
def so_words_first(rng):
    ws = words(rng, 4)
    return _S2(f"{lit(ws)}.sort()[0]", sort_by(ws)[0], "Words sort like a dictionary: a before b.")


@_so
def so_words_last(rng):
    ws = words(rng, 4)
    return _S2(f"{lit(ws)}.sort().at(-1)", sort_by(ws)[3], "The last word alphabetically.")


@_so
def so_words_rev(rng):
    ws = words(rng, 4)
    return _S2(f"{lit(ws)}.sort().reverse()[0]", sort_by(ws)[3], "Sort, then reverse: the latest word first.")


@_so
def so_locale(rng):
    ws = words(rng, 4)
    return _S2(f"{lit(ws)}.sort((a, b) => a.localeCompare(b))[0]", sort_by(ws)[0], "localeCompare orders words alphabetically.")


@_so
def so_case(rng):
    a, b = rng.sample("abcdefg", 2)
    xs = [a, b.upper(), b]
    return _S2(f"{lit(xs)}.sort()", js_show(sort_by(xs)), "Capital letters sort before every lower-case one.")


@_so
def so_numstr(rng):
    xs = rng.choice([["10", "9", "100"], ["8", "75", "100", "9"], ["20", "3", "100"], ["15", "5", "150", "25"]])
    return _S2(f"{lit(xs)}.sort()", js_show(sort_by(xs)), "Strings sort character by character, so '10' comes before '9'.")


@_so
def so_numstr_cmp(rng):
    xs = rng.choice([["10", "9", "100"], ["8", "75", "100", "9"], ["20", "3", "100"]])
    return _S2(f"{lit(xs)}.sort((a, b) => a - b)[0]", sort_by(xs, key=int)[0], "a - b turns the strings into numbers to compare them, and the strings come back.")


@_so
def so_len(rng):
    ws = words(rng, 4)
    return _S2(f"{lit(ws)}.sort((a, b) => a.length - b.length)[0]", sort_by(ws, key=len)[0], "Sorted by length, shortest first; equal lengths keep their order (sort is stable).")


@_so
def so_len_desc(rng):
    ws = words(rng, 4)
    return _S2(f"{lit(ws)}.sort((a, b) => b.length - a.length)[0]", sort_by(ws, key=len, reverse=True)[0], "Longest first; equal lengths keep their original order.")


@_so
def so_len_all(rng):
    ws = words(rng, 3)
    return _S2(f"{lit(ws)}.sort((a, b) => a.length - b.length)", js_show(sort_by(ws, key=len)), "By length; a tie keeps the original order.")


@_so
def so_abs(rng):
    xs = rng.choice([[-5, 3, -1, 4], [2, -7, 6, -3], [-9, 8, -2, 5]])
    return _S2(f"{lit(xs)}.sort((a, b) => Math.abs(a) - Math.abs(b))[0]", sort_by(xs, key=lambda x: x if x >= 0 else -x)[0], "Sorted by size, ignoring the sign.")


@_so
def so_mutates(rng):
    xs = _wide(rng, 3)
    return _S2(f"const xs = {lit(xs)};\nxs.sort((a, b) => a - b);\nxs[0]", sort_by(xs)[0], "sort changes xs itself, so xs[0] is now the smallest.")


@_so
def so_copy_keeps(rng):
    xs = nums(rng, 4, 5)
    return _S2(f"const xs = {lit(xs)};\n[...xs].sort((a, b) => a - b);\nxs[0]", xs[0], "The sort ran on a copy, so xs keeps its order.")


@_so
def so_tosorted(rng):
    xs = nums(rng, 4, 5)
    return _S2(f"const xs = {lit(xs)};\nxs.toSorted((a, b) => a - b);\nxs[0]", xs[0], "toSorted returns a new sorted array and leaves xs alone.")


@_so
def so_tosorted_value(rng):
    xs = nums(rng, 4, 5)
    return _S2(f"{lit(xs)}.toSorted((a, b) => b - a)[0]", sort_by(xs, reverse=True)[0], "toSorted with b - a: biggest first.")


@_so
def so_same_array(rng):
    xs = nums(rng, 3, 4)
    return _S2(f"const xs = {lit(xs)};\nconst ys = xs.sort();\nys === xs", "true", "sort() returns the same array it sorted, not a copy.")


@_so
def so_entries(rng):
    d = pairs(rng, 3)
    return _S2(f"const o = {olit(d)};\nObject.entries(o).sort((a, b) => b[1] - a[1])[0][0]", sort_by(d, key=lambda p: p[1], reverse=True)[0][0], "Sort the [name, value] pairs by value, biggest first; the first pair's name.")


@_so
def so_keys(rng):
    d = pairs(rng, 4)
    return _S2(f"const o = {olit(d)};\nObject.keys(o).sort()[0]", sort_by([k for k, _ in d])[0], "The keys sorted alphabetically.")


@_so
def so_objs(rng):
    ws = words(rng, 3)
    vs = ints(rng, 3, 1, 9)
    data = "[" + ", ".join(f'{{ name: "{w}", n: {v} }}' for w, v in zip(ws, vs)) + "]"
    ps = list(zip(ws, vs))
    return _S2(f"const data = {data};\ndata.sort((a, b) => a.n - b.n)[0].name", sort_by(ps, key=lambda p: p[1])[0][0], "Sorted by n, smallest first; read the first one's name.")


@_so
def so_arrays_default(rng):
    xs = rng.choice([[[10, 1], [9, 1]], [[2, 1], [1, 5]], [[25, 0], [3, 0], [100, 0]]])
    return _S2(f"{lit(xs)}.sort()", js_show(sort_by(xs, key=lambda p: ",".join(str(x) for x in p))), "With no comparator each inner array is turned into text like '10,1' and compared as text.")


@_so
def so_bools(rng):
    return _S2("[true, false, true].sort()", js_show([False, True, True]), "As text 'false' comes before 'true'.")


@_so
def so_noop_cmp(rng):
    xs = nums(rng, 3, 4)
    return _S2(f"const xs = {lit(xs)};\nxs.sort(() => 0);\nxs[0]", xs[0], "A comparator that says 'equal' every time keeps the original order (sort is stable).")


@_so
def so_median(rng):
    xs = ints(rng, rng.choice([5, 7]), 1, 9)
    return _S2(f"const xs = {lit(xs)};\nxs.sort((a, b) => a - b)[Math.floor(xs.length / 2)]", sort_by(xs)[len(xs) // 2], "The middle of the sorted array.")


@_so
def so_stable_pairs(rng):
    ps = [[1, "b"], [0, "z"], [1, "a"]]
    ps = [ps[i] for i in rng.sample(range(3), 3)]
    return _S2(f"{lit(ps)}.sort((p, q) => p[0] - q[0])", js_show(sort_by(ps, key=lambda p: p[0])), "Only the number counts, so equal ones keep the order they came in.")


@_so
def so_alnum(rng):
    xs = rng.choice([["a1", "a10", "a2"], ["f9", "f10", "f1"], ["x20", "x3", "x100"]])
    return _S2(f"{lit(xs)}.sort()", js_show(sort_by(xs)), "Compared as text: '1' comes before '2', so 'a10' sits before 'a2'.")


@_so
def so_letters(rng):
    w = rng.choice(["hello", "little", "banana", "carrot", "coffee", "pumpkin"])
    return _S2(f'[..."{w}"].sort().join("")', "".join(sort_by(list(w))), "Spread into letters, sort, glue back together.")


@_so
def so_letters_rev(rng):
    w = rng.choice(WORDS)
    return _S2(f'"{w}".split("").sort().reverse().join("")', "".join(sort_by(list(w), reverse=True)), "Letters sorted, then reversed: the alphabet backwards.")


@_so
def so_top2(rng):
    xs = nums(rng, 4, 6)
    return _S2(f"{lit(xs)}.sort((a, b) => b - a).slice(0, 2)", js_show(take(sort_by(xs, reverse=True), 0, 2)), "Biggest first, and slice(0, 2) keeps the first two.")


@_so
def so_second_distinct(rng):
    xs = dupes(rng)
    u = sort_by(uniq(xs))
    return _S2(f"Array.from(new Set({lit(xs)})).sort((a, b) => a - b).at(-2)", u[len(u) - 2], "The Set drops repeats; sorted, the second from the end.")


@_so
def so_reverse_only(rng):
    xs = nums(rng, 3, 5)
    return _S2(f"{lit(xs)}.reverse()[0]", xs[len(xs) - 1], "reverse() only flips the order - it does not sort.")


@_so
def so_sort_map(rng):
    xs = nums(rng, 3, 4)
    return _S2(f"{lit(xs)}.sort().map(x => x * 2)", js_show([x * 2 for x in sort_by(xs)]), "Sort first (single digits sort fine as text), then double each.")
