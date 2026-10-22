"""Collections Pack, Python side: lists, dicts, sets and tuples.

Eight activities - List After, How Many, Dict Lookup, Set Maths, Min Max Sum,
Unpack It, Nested Reach, Sort Order - each a list of templates (`AFTER`, `HOW`,
`LOOKUP`, `SETS`, `MINMAX`, `UNPACK`, `NESTED`, `SORTS`).

Every answer is modelled by hand: a list is a plain list that only ever gets
cut and joined by index arithmetic (`take`, `ins`, `drop`), a dict is a list of
(key, value) pairs in insertion order, a set is a list with the repeats left
out, a sort is a stable insertion sort that compares strings character by
character. Nothing here asks Python what the answer is; tests/test_brain_packs.py
runs every template through the real interpreter.
"""

from __future__ import annotations

import random
from typing import Callable

from ._model import WORDS, Maker, decimal_div, fmod, ints, lit, py_div, py_show, py_slice_positions
from .items import Item

# ── Hand models: the list, the pair-list dict, the set ──────────────────


def take(xs: list, a: int, b: int) -> list:
    """xs[a:b] for 0 <= a, b <= len(xs)."""
    return [xs[i] for i in range(a, b)]


def ins(xs: list, i: int, v) -> list:
    """list.insert for a position already clamped into 0..len."""
    return take(xs, 0, i) + [v] + take(xs, i, len(xs))


def drop(xs: list, i: int) -> list:
    """xs without the item at position i."""
    return take(xs, 0, i) + take(xs, i + 1, len(xs))


def pos(xs: list, v) -> int:
    for i in range(len(xs)):
        if xs[i] == v:
            return i
    return -1


def has(xs: list, v) -> bool:
    return pos(xs, v) >= 0


def rm_first(xs: list, v) -> list:
    """list.remove: the first item equal to v goes, any others stay."""
    return drop(xs, pos(xs, v))


def uniq(xs: list) -> list:
    """The members of a set built from xs, in first-seen order (the order a set may not promise)."""
    out: list = []
    for x in xs:
        if not has(out, x):
            out.append(x)
    return out


def total(xs: list) -> int:
    t = 0
    for x in xs:
        t += x
    return t


def lt(a, b) -> bool:
    """Python's a < b for ints, strings (character codes), and lists/tuples of those (item by item)."""
    if isinstance(a, str) and isinstance(b, str):
        for i in range(min(len(a), len(b))):
            if ord(a[i]) != ord(b[i]):
                return ord(a[i]) < ord(b[i])
        return len(a) < len(b)
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        for i in range(min(len(a), len(b))):
            if lt(a[i], b[i]):
                return True
            if lt(b[i], a[i]):
                return False
        return len(a) < len(b)
    return a < b


def sort_by(xs: list, key: Callable = lambda x: x, reverse: bool = False) -> list:
    """sorted(xs, key=key, reverse=reverse): a stable insertion sort (equal keys keep their original order,
    even with reverse=True)."""
    out: list = []
    for x in xs:
        k = len(out)
        while k > 0 and (lt(key(x), key(out[k - 1])) if not reverse else lt(key(out[k - 1]), key(x))):
            k -= 1
        out.insert(k, x)
    return out


def best(xs: list, key: Callable = lambda x: x, want_max: bool = True):
    """max/min: the first item to hold the record wins a tie."""
    top = xs[0]
    for x in xs:
        if (lt(key(top), key(x)) if want_max else lt(key(x), key(top))):
            top = x
    return top


def d_get(d: list, k, default=None):
    for a, b in d:
        if a == k:
            return b
    return default


def d_has(d: list, k) -> bool:
    for a, _ in d:
        if a == k:
            return True
    return False


def d_set(d: list, k, v) -> list:
    """d[k] = v: an old key keeps its place, a new key goes last."""
    if d_has(d, k):
        return [(a, v if a == k else b) for a, b in d]
    return d + [(k, v)]


def d_del(d: list, k) -> list:
    return [(a, b) for a, b in d if a != k]


def d_merge(d: list, e: list) -> list:
    out = d
    for k, v in e:
        out = d_set(out, k, v)
    return out


def dlit(d: list) -> str:
    """A dict literal for a pair list (keys and values are ints or strings)."""
    return "{" + ", ".join(lit(k) + ": " + lit(v) for k, v in d) + "}"


def slit(xs: list) -> str:
    """A set literal."""
    return "{" + ", ".join(lit(x) for x in xs) + "}"


def union(a: list, b: list) -> list:
    return uniq(a + b)


def inter(a: list, b: list) -> list:
    return [x for x in uniq(a) if has(b, x)]


def diff(a: list, b: list) -> list:
    return [x for x in uniq(a) if not has(b, x)]


def sym(a: list, b: list) -> list:
    return diff(a, b) + diff(b, a)


def pyb(v: bool) -> str:
    return "True" if v else "False"


# ── Random parameters ───────────────────────────────────────────────────

def nums(rng: random.Random, lo: int = 3, hi: int = 5) -> list[int]:
    return ints(rng, rng.randint(lo, hi), 1, 9)


def dupes(rng: random.Random) -> list[int]:
    """A list with repeated values (3-4 different ones, then 2-3 repeats, shuffled)."""
    base = ints(rng, rng.randint(3, 4), 1, 9)
    xs = base + [rng.choice(base) for _ in range(rng.randint(2, 3))]
    rng.shuffle(xs)
    return xs


def words(rng: random.Random, n: int, lo: int = 3) -> list[str]:
    return rng.sample([w for w in WORDS if len(w) >= lo], n)


def pairs(rng: random.Random, n: int = 3, strs: bool = False) -> list:
    """A pair list: word keys, int (or word) values."""
    ks = words(rng, n)
    vs = rng.sample([w for w in WORDS if w not in ks], n) if strs else ints(rng, n, 1, 9)
    return list(zip(ks, vs))


def err_py(code: str) -> str:
    """An oracle program that runs the whole snippet inside a function and gives the last line's value, or the
    name of the exception if anything raised."""
    head, _, last = code.rpartition("\n")
    body = "".join("        " + line + "\n" for line in head.split("\n")) if head else ""
    return "def _go():\n    try:\n" + body + f"        return ({last})\n    except Exception as e:\n        return type(e).__name__\n_go()"



# ── 1. List After ───────────────────────────────────────────────────────
# A recipe is a few steps, each a line of code and what it does to the list, then a last line.

STEPS: dict[str, Callable] = {}
RULES: dict[str, str] = {}


def step(name: str, rule: str):
    def deco(fn):
        STEPS[name] = fn
        RULES[name] = rule
        return fn
    return deco


def _v(rng: random.Random) -> int:
    return rng.randint(1, 9)


@step("append", "append adds one item at the end")
def _s_append(rng, xs):
    v = _v(rng)
    return f"xs.append({v})", xs + [v]


@step("extend", "extend adds each item of the other list at the end")
def _s_extend(rng, xs):
    a, b = _v(rng), _v(rng)
    return f"xs.extend([{a}, {b}])", xs + [a, b]


@step("insert_front", "insert(0, v) puts v at the front")
def _s_insert_front(rng, xs):
    v = _v(rng)
    return f"xs.insert(0, {v})", ins(xs, 0, v)


@step("insert_mid", "insert(i, v) puts v at position i and moves the rest along")
def _s_insert_mid(rng, xs):
    v, i = _v(rng), rng.randint(1, len(xs) - 1)
    return f"xs.insert({i}, {v})", ins(xs, i, v)


@step("insert_neg", "insert(-1, v) goes in before the last item, not after it")
def _s_insert_neg(rng, xs):
    v = _v(rng)
    return f"xs.insert(-1, {v})", ins(xs, len(xs) - 1, v)


@step("insert_far", "insert past the end just appends")
def _s_insert_far(rng, xs):
    v = _v(rng)
    return f"xs.insert(99, {v})", xs + [v]


@step("pop_last", "pop() removes the last item")
def _s_pop_last(rng, xs):
    return "xs.pop()", take(xs, 0, len(xs) - 1)


@step("pop_first", "pop(0) removes the first item")
def _s_pop_first(rng, xs):
    return "xs.pop(0)", drop(xs, 0)


@step("pop_mid", "pop(i) removes the item at position i")
def _s_pop_mid(rng, xs):
    i = rng.randint(1, len(xs) - 2)
    return f"xs.pop({i})", drop(xs, i)


@step("remove", "remove(v) deletes the first item equal to v")
def _s_remove(rng, xs):
    v = rng.choice(xs)
    return f"xs.remove({v})", rm_first(xs, v)


@step("sort_asc", "sort() puts the list in order, smallest first")
def _s_sort_asc(rng, xs):
    return "xs.sort()", sort_by(xs)


@step("sort_desc", "sort(reverse=True) puts the biggest first")
def _s_sort_desc(rng, xs):
    return "xs.sort(reverse=True)", sort_by(xs, reverse=True)


@step("reverse", "reverse() flips the order in place")
def _s_reverse(rng, xs):
    return "xs.reverse()", [xs[len(xs) - 1 - i] for i in range(len(xs))]


@step("del_idx", "del xs[i] removes the item at position i")
def _s_del_idx(rng, xs):
    i = rng.randrange(len(xs))
    return f"del xs[{i}]", drop(xs, i)


@step("del_neg", "del xs[-2] removes the second from the end")
def _s_del_neg(rng, xs):
    return "del xs[-2]", drop(xs, len(xs) - 2)


@step("set_idx", "xs[i] = v replaces the item at position i")
def _s_set_idx(rng, xs):
    i, v = rng.randrange(len(xs)), _v(rng)
    return f"xs[{i}] = {v}", take(xs, 0, i) + [v] + take(xs, i + 1, len(xs))


@step("set_neg", "xs[-1] = v replaces the last item")
def _s_set_neg(rng, xs):
    v = _v(rng)
    return f"xs[-1] = {v}", take(xs, 0, len(xs) - 1) + [v]


@step("iadd", "+= on a list adds the items to the same list")
def _s_iadd(rng, xs):
    a, b = _v(rng), _v(rng)
    return f"xs += [{a}, {b}]", xs + [a, b]


@step("plus_new", "xs + [v] builds a new list, and the assignment makes xs name it")
def _s_plus_new(rng, xs):
    v = _v(rng)
    return f"xs = xs + [{v}]", xs + [v]


@step("slice_assign", "assigning to a slice swaps those items for the new ones")
def _s_slice_assign(rng, xs):
    v = _v(rng)
    return f"xs[0:2] = [{v}]", [v] + take(xs, 2, len(xs))


@step("slice_del", "del xs[:2] removes the first two")
def _s_slice_del(rng, xs):
    return "del xs[:2]", take(xs, 2, len(xs))


@step("slice_insert", "assigning to an empty slice inserts there")
def _s_slice_insert(rng, xs):
    a, b = _v(rng), _v(rng)
    return f"xs[1:1] = [{a}, {b}]", take(xs, 0, 1) + [a, b] + take(xs, 1, len(xs))


@step("slice_front", "xs[1:] is a new list without the first item")
def _s_slice_front(rng, xs):
    return "xs = xs[1:]", take(xs, 1, len(xs))


@step("slice_back", "xs[:-1] is a new list without the last item")
def _s_slice_back(rng, xs):
    return "xs = xs[:-1]", take(xs, 0, len(xs) - 1)


@step("clear", "clear() empties the list")
def _s_clear(rng, xs):
    return "xs.clear()", []


@step("double", "a comprehension builds a new list from the old one")
def _s_double(rng, xs):
    return "xs = [x * 2 for x in xs]", [x * 2 for x in xs]


@step("keep_big", "the if in a comprehension keeps only the matching items")
def _s_keep_big(rng, xs):
    k = rng.randint(2, 6)
    return f"xs = [x for x in xs if x > {k}]", [x for x in xs if x > k]


def _recipe(steps: tuple[str, ...], final: str) -> Maker:
    def make(rng: random.Random) -> Item:
        cur = nums(rng, 3, 5)
        lines = [f"xs = {lit(cur)}"]
        for name in steps:
            line, cur = STEPS[name](rng, cur)
            lines.append(line)
        if final == "xs":
            ans, last = py_show(cur), "xs"
        elif final == "first":
            ans, last = str(cur[0]), "xs[0]"
        else:
            ans, last = str(cur[len(cur) - 1]), "xs[-1]"
        seen: list[str] = []
        for s in steps:
            if RULES[s] not in seen:
                seen.append(RULES[s])
        why = "; ".join(seen[:2]) + "."
        return Item("\n".join(lines + [last]), ans, why)
    make.__name__ = "after_" + "_".join(steps) + "_" + final
    return make


_RECIPES: list[tuple[tuple[str, ...], str]] = [
    (("append",), "xs"), (("append", "append"), "xs"), (("extend",), "xs"), (("insert_front",), "xs"),
    (("insert_mid",), "xs"), (("insert_neg",), "xs"), (("insert_far",), "xs"), (("pop_last",), "xs"),
    (("pop_first",), "xs"), (("pop_mid",), "xs"), (("remove",), "xs"), (("sort_asc",), "xs"),
    (("sort_desc",), "xs"), (("reverse",), "xs"), (("del_idx",), "xs"), (("del_neg",), "xs"),
    (("set_idx",), "xs"), (("set_neg",), "xs"), (("iadd",), "xs"), (("plus_new",), "xs"),
    (("slice_assign",), "xs"), (("slice_del",), "xs"), (("slice_insert",), "xs"), (("slice_front",), "xs"),
    (("slice_back",), "xs"), (("double",), "xs"), (("keep_big",), "xs"),
    (("append", "sort_asc"), "xs"), (("append", "reverse"), "xs"), (("pop_last", "append"), "xs"),
    (("pop_first", "append"), "xs"), (("insert_front", "pop_last"), "xs"), (("remove", "append"), "xs"),
    (("extend", "sort_desc"), "xs"), (("sort_asc", "pop_last"), "xs"), (("sort_desc", "pop_first"), "xs"),
    (("reverse", "pop_last"), "xs"), (("reverse", "append"), "xs"), (("append", "pop_first"), "xs"),
    (("insert_mid", "remove"), "xs"), (("del_idx", "insert_front"), "xs"), (("set_idx", "sort_asc"), "xs"),
    (("append", "append", "pop_last"), "xs"), (("pop_last", "pop_last", "append"), "xs"),
    (("reverse", "reverse"), "xs"), (("sort_asc", "reverse"), "xs"), (("extend", "reverse"), "xs"),
    (("append", "insert_front", "remove"), "xs"), (("clear", "append"), "xs"),
    (("sort_asc",), "first"), (("sort_desc",), "first"), (("append", "reverse"), "first"),
    (("pop_last",), "last"), (("insert_front", "sort_asc"), "last"), (("reverse",), "last"),
]

AFTER: list[Maker] = [_recipe(s, f) for s, f in _RECIPES]


def _after(fn: Maker) -> Maker:
    AFTER.append(fn)
    return fn


@_after
def a_alias(rng):
    xs, v = nums(rng), _v(rng)
    return Item(f"xs = {lit(xs)}\nys = xs\nys.append({v})\nxs", py_show(xs + [v]),
                "ys = xs does not copy: both names are the same list, so the append shows in xs.")


@_after
def a_copy(rng):
    xs, v = nums(rng), _v(rng)
    return Item(f"xs = {lit(xs)}\nys = xs.copy()\nys.append({v})\nxs", py_show(xs),
                "copy() makes a separate list, so changing ys leaves xs alone.")


@_after
def a_slice_copy(rng):
    xs = nums(rng)
    return Item(f"xs = {lit(xs)}\nys = xs[:]\nys.pop()\nxs", py_show(xs), "xs[:] is a copy, so popping ys does not touch xs.")


@_after
def a_func(rng):
    xs, v = nums(rng), _v(rng)
    return Item(f"def add(items):\n    items.append({v})\nxs = {lit(xs)}\nadd(xs)\nxs", py_show(xs + [v]),
                "The function was handed the very same list, and append changes it in place.")


@_after
def a_func_rebind(rng):
    xs, v = nums(rng), _v(rng)
    return Item(f"def add(items):\n    items = items + [{v}]\nxs = {lit(xs)}\nadd(xs)\nxs", py_show(xs),
                "items + [...] builds a new list, and only the function's own name items points at it.")


@_after
def a_sort_none(rng):
    xs = nums(rng)
    return Item(f"xs = {lit(xs)}\nys = xs.sort()\nys", "None", "sort() changes the list in place and gives back None.")


@_after
def a_append_none(rng):
    xs, v = nums(rng), _v(rng)
    return Item(f"xs = {lit(xs)}\nxs = xs.append({v})\nxs", "None",
                "append returns None, so the assignment replaces the list with None.")


@_after
def a_reverse_none(rng):
    xs = nums(rng)
    return Item(f"xs = {lit(xs)}\nxs = xs.reverse()\nxs", "None", "reverse() works in place and returns None.")


@_after
def a_sorted_keeps(rng):
    xs = nums(rng)
    return Item(f"xs = {lit(xs)}\nsorted(xs)\nxs", py_show(xs), "sorted() builds a new list and throws it away here; xs is untouched.")


@_after
def a_sorted_assign(rng):
    xs = nums(rng)
    return Item(f"xs = {lit(xs)}\nxs = sorted(xs)\nxs", py_show(sort_by(xs)), "sorted() gives a new list, and xs now names it.")


@_after
def a_dup_remove(rng):
    xs = dupes(rng)
    v = xs[0]
    return Item(f"xs = {lit(xs)}\nxs.remove({v})\nxs", py_show(rm_first(xs, v)), "remove takes out only the first match; later copies stay.")


@_after
def a_pop_value(rng):
    xs = nums(rng)
    return Item(f"xs = {lit(xs)}\nxs.pop()", str(xs[len(xs) - 1]), "pop() hands back the item it removes.")


@_after
def a_pop0_value(rng):
    xs = nums(rng)
    return Item(f"xs = {lit(xs)}\nxs.pop(0)", str(xs[0]), "pop(0) hands back the first item.")


@_after
def a_append_value(rng):
    xs, v = nums(rng), _v(rng)
    return Item(f"xs = {lit(xs)}\nxs.append({v})", "None", "append changes the list and returns None.")


@_after
def a_sorted_last(rng):
    xs = nums(rng)
    return Item(f"xs = {lit(xs)}\nxs.sort()\nxs.pop()", str(sort_by(xs)[len(xs) - 1]), "Sorted smallest first, so pop() takes the biggest.")


@_after
def a_two_names(rng):
    xs, v = nums(rng), _v(rng)
    return Item(f"a = {lit(xs)}\nb = a\nb = b + [{v}]\na", py_show(xs), "b + [...] makes a new list, so b leaves a behind.")


@_after
def a_two_names_iadd(rng):
    xs, v = nums(rng), _v(rng)
    return Item(f"a = {lit(xs)}\nb = a\nb += [{v}]\na", py_show(xs + [v]), "+= changes the list in place, and a is that list.")


@_after
def a_times(rng):
    xs = ints(rng, 2, 1, 9)
    return Item(f"xs = {lit(xs)}\nxs *= 2\nxs", py_show(xs + xs), "*= 2 repeats the list: the items again, in the same order.")


@_after
def a_unique_sorted(rng):
    xs = dupes(rng)
    return Item(f"xs = {lit(xs)}\nsorted(set(xs))", py_show(sort_by(uniq(xs))), "set drops the repeats; sorted puts what is left in order.")


@_after
def a_extend_append(rng):
    xs, a, b = nums(rng, 2, 3), _v(rng), _v(rng)
    return Item(f"xs = {lit(xs)}\nxs.append([{a}, {b}])\nlen(xs)", str(len(xs) + 1),
                "append adds the whole list as ONE item (extend would add two).")


@_after
def a_list_from_str(rng):
    w = rng.choice([w for w in WORDS if len(w) == 4])
    return Item(f'xs = list("{w}")\nxs.reverse()\nxs[0]', w[3], "list() splits the word into letters; reversed, the last letter is first.")


@_after
def a_pop_in_loop(rng):
    xs = nums(rng, 4, 5)
    return Item(f"xs = {lit(xs)}\nwhile len(xs) > 2:\n    xs.pop(0)\nxs", py_show(take(xs, len(xs) - 2, len(xs))),
                "Each turn drops the first item until two are left: the last two stay.")


@_after
def a_for_append(rng):
    n = rng.randint(3, 5)
    return Item(f"xs = []\nfor i in range({n}):\n    xs.append(i * i)\nxs", py_show([i * i for i in range(n)]),
                "i runs 0, 1, 2 ... and each square is appended in turn.")


# ── 2. How Many ─────────────────────────────────────────────────────────

HOW: list[Maker] = []


def _how(fn: Maker) -> Maker:
    HOW.append(fn)
    return fn


def _n(code: str, n: int, why: str) -> Item:
    return Item(code, str(n), why)


@_how
def h_list(rng):
    xs = nums(rng, 3, 6)
    return _n(f"len({lit(xs)})", len(xs), "len counts the items.")


@_how
def h_str(rng):
    w = rng.choice(WORDS)
    return _n(f'len("{w}")', len(w), "len of a string counts its characters.")


@_how
def h_tuple(rng):
    xs = nums(rng, 2, 5)
    return _n(f"len(({', '.join(map(str, xs))},))" if len(xs) == 1 else f"len(({', '.join(map(str, xs))}))", len(xs),
              "A tuple's length is how many items it holds.")


@_how
def h_dict(rng):
    d = pairs(rng, rng.randint(2, 4))
    return _n(f"len({dlit(d)})", len(d), "len of a dict counts its keys.")


@_how
def h_set_literal(rng):
    xs = dupes(rng)
    return _n(f"len({slit(xs)})", len(uniq(xs)), "A set keeps each value once, so repeats do not count.")


@_how
def h_set_of_list(rng):
    xs = dupes(rng)
    return _n(f"len(set({lit(xs)}))", len(uniq(xs)), "set() drops the repeats: count the different values.")


@_how
def h_empty(rng):
    code = rng.choice(["[]", '""', "{}", "()", "set()", "dict()", "list()"])
    return _n(f"len({code})", 0, "An empty collection has length 0.")


@_how
def h_nested(rng):
    inner = [nums(rng, 1, 3) for _ in range(rng.randint(2, 3))] + [[]]
    return _n(f"len({lit(inner)})", len(inner), "len counts the outer items only, whatever each one holds.")


@_how
def h_append(rng):
    xs, v = nums(rng), _v(rng)
    return _n(f"xs = {lit(xs)}\nxs.append({v})\nlen(xs)", len(xs) + 1, "append adds one item.")


@_how
def h_extend(rng):
    xs, ys = nums(rng, 2, 4), nums(rng, 2, 3)
    return _n(f"xs = {lit(xs)}\nxs.extend({lit(ys)})\nlen(xs)", len(xs) + len(ys), "extend adds every item of the other list.")


@_how
def h_append_list(rng):
    xs, ys = nums(rng, 2, 4), nums(rng, 2, 3)
    return _n(f"xs = {lit(xs)}\nxs.append({lit(ys)})\nlen(xs)", len(xs) + 1, "append adds the whole list as a single item.")


@_how
def h_pop(rng):
    xs = nums(rng, 3, 6)
    return _n(f"xs = {lit(xs)}\nxs.pop()\nlen(xs)", len(xs) - 1, "pop removes one item.")


@_how
def h_remove(rng):
    xs = dupes(rng)
    return _n(f"xs = {lit(xs)}\nxs.remove({xs[0]})\nlen(xs)", len(xs) - 1, "remove deletes one match only, even when there are more.")


@_how
def h_insert(rng):
    xs, v = nums(rng), _v(rng)
    return _n(f"xs = {lit(xs)}\nxs.insert(1, {v})\nlen(xs)", len(xs) + 1, "insert adds one item.")


@_how
def h_del(rng):
    xs = nums(rng, 3, 6)
    return _n(f"xs = {lit(xs)}\ndel xs[0]\nlen(xs)", len(xs) - 1, "del removes one item.")


@_how
def h_clear(rng):
    xs = nums(rng)
    return _n(f"xs = {lit(xs)}\nxs.clear()\nlen(xs)", 0, "clear empties the list.")


@_how
def h_plus(rng):
    xs, ys = nums(rng, 2, 4), nums(rng, 2, 4)
    return _n(f"len({lit(xs)} + {lit(ys)})", len(xs) + len(ys), "+ joins two lists: the lengths add up.")


@_how
def h_times(rng):
    xs, k = nums(rng, 2, 3), rng.randint(2, 4)
    return _n(f"len({lit(xs)} * {k})", len(xs) * k, f"* {k} repeats the list {k} times.")


@_how
def h_slice(rng):
    xs = nums(rng, 5, 7)
    a, b = rng.randint(0, 2), rng.randint(3, 6)
    return _n(f"len({lit(xs)}[{a}:{b}])", len(py_slice_positions(len(xs), a, b, None)), f"[{a}:{b}] stops at {b} (or the end) and starts at {a}.")


@_how
def h_slice_neg(rng):
    xs, k = nums(rng, 4, 6), rng.randint(1, 3)
    return _n(f"len({lit(xs)}[-{k}:])", len(py_slice_positions(len(xs), -k, None, None)), f"[-{k}:] is the last {k}.")


@_how
def h_slice_drop(rng):
    xs, k = nums(rng, 4, 6), rng.randint(1, 3)
    return _n(f"len({lit(xs)}[:-{k}])", len(py_slice_positions(len(xs), None, -k, None)), f"[:-{k}] drops the last {k}.")


@_how
def h_slice_step(rng):
    xs = nums(rng, 5, 7)
    return _n(f"len({lit(xs)}[::2])", len(py_slice_positions(len(xs), None, None, 2)), "[::2] takes every second item, starting with the first.")


@_how
def h_range(rng):
    a = rng.randint(0, 5)
    b = a + rng.randint(3, 9)
    return _n(f"len(range({a}, {b}))", b - a, "range stops before the end value: b - a items.")


@_how
def h_range_step(rng):
    a, s = rng.randint(0, 4), rng.randint(2, 4)
    b = a + rng.randint(8, 16)
    count, i = 0, a
    while i < b:
        count += 1
        i += s
    return _n(f"len(range({a}, {b}, {s}))", count, f"It counts {a}, {a + s}, {a + 2 * s} ... while below {b}.")


@_how
def h_range_one(rng):
    n = rng.randint(4, 12)
    return _n(f"len(range({n}))", n, f"range({n}) is 0 up to {n - 1}: {n} numbers.")


@_how
def h_split(rng):
    ws = words(rng, rng.randint(2, 4))
    return _n(f'len("{" ".join(ws)}".split())', len(ws), "split() cuts at the spaces: one piece per word.")


@_how
def h_split_comma(rng):
    ws = words(rng, rng.randint(2, 4))
    return _n(f'len("{",".join(ws)}".split(","))', len(ws), "One more piece than there are commas.")


@_how
def h_split_empty(rng):
    code, n, why = rng.choice([('len("".split(","))', 1, 'Splitting an empty string at a comma still gives one (empty) piece.'),
                               ('len("".split())', 0, "split() with no argument gives nothing for an empty string."),
                               ('len(",".split(","))', 2, "A lone comma has an empty piece on each side.")])
    return _n(code, n, why)


@_how
def h_list_str(rng):
    w = rng.choice(WORDS)
    return _n(f'len(list("{w}"))', len(w), "list() of a string is one item per letter.")


@_how
def h_dict_add(rng):
    d, v = pairs(rng), _v(rng)
    return _n(f'd = {dlit(d)}\nd["new"] = {v}\nlen(d)', len(d_set(d, "new", v)), "A new key makes a new entry.")


@_how
def h_dict_replace(rng):
    d, v = pairs(rng), _v(rng)
    return _n(f'd = {dlit(d)}\nd["{d[0][0]}"] = {v}\nlen(d)', len(d_set(d, d[0][0], v)), "An existing key just gets a new value: the size stays.")


@_how
def h_dict_pop(rng):
    d = pairs(rng, rng.randint(3, 4))
    return _n(f'd = {dlit(d)}\nd.pop("{d[1][0]}")\nlen(d)', len(d_del(d, d[1][0])), "pop removes the key.")


@_how
def h_dict_update(rng):
    d = pairs(rng, 3)
    e = [(d[0][0], 0), ("new", 1)]
    return _n(f"d = {dlit(d)}\nd.update({dlit(e)})\nlen(d)", len(d_merge(d, e)), "update replaces the old key and adds the new one.")


@_how
def h_dict_del(rng):
    d = pairs(rng, rng.randint(3, 4))
    return _n(f'd = {dlit(d)}\ndel d["{d[0][0]}"]\nlen(d)', len(d_del(d, d[0][0])), "del removes the key.")


@_how
def h_setdefault(rng):
    d, v = pairs(rng), _v(rng)
    k, new = rng.choice([(d[0][0], False), ("zzz", True)])
    return _n(f'd = {dlit(d)}\nd.setdefault("{k}", {v})\nlen(d)', len(d) + (1 if new else 0),
              "setdefault adds the key only when it is missing." if new else "The key was already there, so nothing is added.")


@_how
def h_dict_dupkey(rng):
    k, a, b = rng.choice(WORDS), _v(rng), _v(rng)
    return _n(f'len({{"{k}": {a}, "{k}": {b}}})', 1, "A key can only be there once: the second value replaces the first.")


@_how
def h_dict_one_one(rng):
    return _n('len({1: "a", 1.0: "b"})', 1, "1 and 1.0 are equal, so they are the same key.")


@_how
def h_dict_views(rng):
    d = pairs(rng, rng.randint(2, 4))
    code = rng.choice(["d.keys()", "d.values()", "d.items()", "list(d)"])
    return _n(f"d = {dlit(d)}\nlen({code})", len(d), "keys, values and items each have one entry per key.")


@_how
def h_merge(rng):
    d = pairs(rng, 3)
    e = [(d[0][0], 0), ("new", 1)]
    return _n(f"len({{**{dlit(d)}, **{dlit(e)}}})", len(d_merge(d, e)), "Merging keeps each key once: the shared key counts a single time.")


@_how
def h_set_union(rng):
    a, b = nums(rng, 3, 4), nums(rng, 3, 4)
    return _n(f"a = {slit(a)}\nb = {slit(b)}\nlen(a | b)", len(union(a, b)), "| is the union: every value in either, each counted once.")


@_how
def h_set_inter(rng):
    a, b = nums(rng, 3, 5), nums(rng, 3, 5)
    return _n(f"a = {slit(a)}\nb = {slit(b)}\nlen(a & b)", len(inter(a, b)), "& keeps the values that are in both.")


@_how
def h_set_diff(rng):
    a, b = nums(rng, 3, 5), nums(rng, 3, 5)
    return _n(f"a = {slit(a)}\nb = {slit(b)}\nlen(a - b)", len(diff(a, b)), "a - b keeps what is in a and not in b.")


@_how
def h_set_sym(rng):
    a, b = nums(rng, 3, 5), nums(rng, 3, 5)
    return _n(f"a = {slit(a)}\nb = {slit(b)}\nlen(a ^ b)", len(sym(a, b)), "^ keeps the values that are in exactly one of the two.")


@_how
def h_set_add_dup(rng):
    a = nums(rng)
    return _n(f"s = {slit(a)}\ns.add({a[0]})\nlen(s)", len(a), "The value was already in the set, so adding it changes nothing.")


@_how
def h_set_add_new(rng):
    a = ints(rng, 3, 1, 5)
    return _n(f"s = {slit(a)}\ns.add({a[0] + 5})\nlen(s)", len(a) + 1, "A new value makes the set one bigger.")


@_how
def h_set_discard(rng):
    a = nums(rng)
    k, absent = rng.choice([(a[0], False), (10, True)])
    return _n(f"s = {slit(a)}\ns.discard({k})\nlen(s)", len(a) - (0 if absent else 1),
              "discard does nothing when the value is not there." if absent else "discard removes the value.")


@_how
def h_zip(rng):
    xs, ys = nums(rng, 3, 5), nums(rng, 2, 4)
    return _n(f"len(list(zip({lit(xs)}, {lit(ys)})))", min(len(xs), len(ys)), "zip stops when the shorter list runs out.")


@_how
def h_enumerate(rng):
    xs = nums(rng, 3, 5)
    return _n(f"len(list(enumerate({lit(xs)})))", len(xs), "enumerate gives one pair per item.")


@_how
def h_filter(rng):
    xs, k = nums(rng, 5, 7), rng.randint(3, 6)
    return _n(f"xs = {lit(xs)}\nlen([x for x in xs if x > {k}])", len([x for x in xs if x > k]), f"Only the items bigger than {k} are kept.")


@_how
def h_comp(rng):
    xs = nums(rng, 3, 6)
    return _n(f"xs = {lit(xs)}\nlen([x * 2 for x in xs])", len(xs), "A comprehension without an if makes one new item per old item.")


@_how
def h_digits(rng):
    n = rng.randint(100, 99999)
    return _n(f"len(str({n}))", len(str(n)), "str() writes the number out; len counts the digits.")


@_how
def h_fromkeys(rng):
    xs = dupes(rng)
    return _n(f"len(dict.fromkeys({lit(xs)}))", len(uniq(xs)), "fromkeys makes one key per different value.")


@_how
def h_zero_list(rng):
    n = rng.randint(3, 9)
    return _n(f"len([0] * {n})", n, f"[0] * {n} is {n} zeros.")


@_how
def h_grid_rows(rng):
    a, b = rng.randint(2, 4), rng.randint(2, 4)
    return _n(f"grid = [[0] * {a}] * {b}\nlen(grid)", b, "The outer list has one entry per row.")


@_how
def h_grid_cols(rng):
    a, b = rng.randint(2, 5), rng.randint(2, 4)
    return _n(f"grid = [[0] * {a}] * {b}\nlen(grid[0])", a, "grid[0] is one row: its length is the number of columns.")


@_how
def h_tuple_one(rng):
    a = _v(rng)
    code, n, why = rng.choice([(f"len(({a},))", 1, "The trailing comma makes a one-item tuple."),
                               (f"len(({a}, {a}))", 2, "Two items, repeats and all."),
                               (f"len((({a}, {a}),))", 1, "A tuple holding one pair has length 1.")])
    return _n(code, n, why)


@_how
def h_sorted(rng):
    xs = nums(rng, 3, 6)
    return _n(f"len(sorted({lit(xs)}))", len(xs), "sorted keeps every item; only the order changes.")


@_how
def h_join(rng):
    ws = words(rng, rng.randint(2, 3))
    sep = rng.choice(["-", ", ", ""])
    n = 0
    for w in ws:
        n += len(w)
    n += len(sep) * (len(ws) - 1)
    return _n(f'len("{sep}".join({lit(ws)}))', n, "The letters of every word, plus the separator between each pair.")


@_how
def h_set_str(rng):
    w = rng.choice(["hello", "little", "pumpkin", "banana", "balloon", "carrot", "coffee"])
    return _n(f'len(set("{w}"))', len(uniq(list(w))), "A set of a string holds each different letter once.")


@_how
def h_str_times(rng):
    w, k = rng.choice(WORDS), rng.randint(2, 4)
    return _n(f'len("{w}" * {k})', len(w) * k, f"The word {k} times over.")


@_how
def h_set_comp(rng):
    xs = nums(rng, 5, 6)
    return _n(f"len({{x % 3 for x in {lit(xs)}}})", len(uniq([fmod(x, 3) for x in xs])), "x % 3 can only be 0, 1 or 2, and a set keeps each once.")


@_how
def h_count_dict(rng):
    w = rng.choice(["hello", "little", "banana", "balloon", "coffee", "pumpkin"])
    d: list = []
    for ch in w:
        d = d_set(d, ch, d_get(d, ch, 0) + 1)
    return _n(f'counts = {{}}\nfor ch in "{w}":\n    counts[ch] = counts.get(ch, 0) + 1\nlen(counts)', len(d),
              "One key per different letter.")


# ── 3. Dict Lookup ──────────────────────────────────────────────────────
# An answer is the value, or the name of the exception (KeyError, TypeError...) when the line raises.

LOOKUP: list[Maker] = []


def _look(fn: Maker) -> Maker:
    LOOKUP.append(fn)
    return fn


def _L(code: str, ans: str, why: str, err: bool = False) -> Item:
    return Item(code, ans, why, check=err_py(code) if err else "")


def _decl(d: list) -> str:
    return f"d = {dlit(d)}"


def _missing(rng: random.Random, d: list) -> str:
    return rng.choice([w for w in WORDS if not d_has(d, w)])


@_look
def l_get(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _L(f'{_decl(d)}\nd["{k}"]', str(v), "d[key] gives the value stored under that key.")


@_look
def l_get_word(rng):
    d = pairs(rng, 3, strs=True)
    k, v = d[rng.randrange(3)]
    return _L(f'{_decl(d)}\nd["{k}"]', v, "d[key] gives the value stored under that key.")


@_look
def l_get_dflt_present(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _L(f'{_decl(d)}\nd.get("{k}", 0)', str(v), "get gives the stored value when the key exists; the default is only for a missing key.")


@_look
def l_get_dflt_missing(rng):
    d = pairs(rng)
    n = _v(rng)
    return _L(f'{_decl(d)}\nd.get("{_missing(rng, d)}", {n})', str(n), "get gives its second argument when the key is missing.")


@_look
def l_get_none(rng):
    d = pairs(rng)
    return _L(f'{_decl(d)}\nd.get("{_missing(rng, d)}")', "None", "get with no default gives None for a missing key.")


@_look
def l_keyerror(rng):
    d = pairs(rng)
    return _L(f'{_decl(d)}\nd["{_missing(rng, d)}"]', "KeyError", "d[key] raises KeyError when the key is not there (get would not).", True)


@_look
def l_keyerror_int(rng):
    d = pairs(rng)
    return _L(f"{_decl(d)}\nd[{rng.randint(0, 2)}]", "KeyError", "A dict is looked up by key, not position: there is no key 0, 1 or 2 here.", True)


@_look
def l_in_key(rng):
    d = pairs(rng)
    k, found = rng.choice([(d[rng.randrange(3)][0], True), (_missing(rng, d), False)])
    return _L(f'{_decl(d)}\n"{k}" in d', pyb(found), "in on a dict asks about the keys.")


@_look
def l_not_in(rng):
    d = pairs(rng)
    k, found = rng.choice([(d[rng.randrange(3)][0], True), (_missing(rng, d), False)])
    return _L(f'{_decl(d)}\n"{k}" not in d', pyb(not found), "not in is True when the key is missing.")


@_look
def l_in_value(rng):
    d = pairs(rng)
    return _L(f"{_decl(d)}\n{d[rng.randrange(3)][1]} in d", "False", "in looks at the keys, and these keys are words: a value is never found there.")


@_look
def l_in_values(rng):
    d = pairs(rng)
    v, found = rng.choice([(d[rng.randrange(3)][1], True), (10, False)])
    return _L(f"{_decl(d)}\n{v} in d.values()", pyb(found), "d.values() holds the values, so in checks those.")


@_look
def l_set_then_get(rng):
    d, v = pairs(rng), _v(rng)
    k = _missing(rng, d)
    return _L(f'{_decl(d)}\nd["{k}"] = {v}\nd["{k}"]', str(v), "Assigning to a new key adds it.")


@_look
def l_overwrite(rng):
    d, v = pairs(rng), _v(rng)
    k = d[rng.randrange(3)][0]
    return _L(f'{_decl(d)}\nd["{k}"] = {v}\nd["{k}"]', str(v), "Assigning to an existing key replaces its value.")


@_look
def l_update(rng):
    d, v = pairs(rng), _v(rng)
    k = d[rng.randrange(3)][0]
    return _L(f'{_decl(d)}\nd.update({{"{k}": {v}}})\nd["{k}"]', str(v), "update copies the new pairs in, replacing old values.")


@_look
def l_update_kw(rng):
    d, v = pairs(rng), _v(rng)
    k = d[rng.randrange(3)][0]
    return _L(f"{_decl(d)}\nd.update({k}={v})\nd[\"{k}\"]", str(v), "update(name=value) sets that key too.")


@_look
def l_pop(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _L(f'{_decl(d)}\nd.pop("{k}")', str(v), "pop removes the key and hands back its value.")


@_look
def l_pop_default(rng):
    d, n = pairs(rng), _v(rng)
    return _L(f'{_decl(d)}\nd.pop("{_missing(rng, d)}", {n})', str(n), "pop with a default gives that default instead of raising.")


@_look
def l_pop_missing(rng):
    d = pairs(rng)
    return _L(f'{_decl(d)}\nd.pop("{_missing(rng, d)}")', "KeyError", "pop with no default raises KeyError for a missing key.", True)


@_look
def l_pop_then_in(rng):
    d = pairs(rng)
    k = d[rng.randrange(3)][0]
    return _L(f'{_decl(d)}\nd.pop("{k}")\n"{k}" in d', "False", "pop removed the key.")


@_look
def l_del_then_get(rng):
    d = pairs(rng)
    k = d[rng.randrange(3)][0]
    return _L(f'{_decl(d)}\ndel d["{k}"]\nd.get("{k}")', "None", "After del the key is gone, so get gives None.")


@_look
def l_del_then_index(rng):
    d = pairs(rng)
    k = d[rng.randrange(3)][0]
    return _L(f'{_decl(d)}\ndel d["{k}"]\nd["{k}"]', "KeyError", "The key was deleted, so looking it up raises KeyError.", True)


@_look
def l_setdefault_present(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _L(f'{_decl(d)}\nd.setdefault("{k}", 99)', str(v), "setdefault gives the existing value and leaves it alone.")


@_look
def l_setdefault_new(rng):
    d, n = pairs(rng), _v(rng)
    return _L(f'{_decl(d)}\nd.setdefault("{_missing(rng, d)}", {n})', str(n), "setdefault adds the key with the default and gives that default back.")


@_look
def l_setdefault_kept(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _L(f'{_decl(d)}\nd.setdefault("{k}", 99)\nd["{k}"]', str(v), "The key existed, so setdefault did not change it.")


@_look
def l_aug(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _L(f'{_decl(d)}\nd["{k}"] += 1\nd["{k}"]', str(v + 1), "d[k] += 1 reads the value, adds one, and stores it back.")


@_look
def l_aug_missing(rng):
    d = pairs(rng)
    return _L(f'{_decl(d)}\nd["{_missing(rng, d)}"] += 1\nd', "KeyError", "+= has to read the key first, and a missing key raises KeyError.", True)


@_look
def l_count_get(rng):
    d = pairs(rng)
    k = _missing(rng, d)
    return _L(f'{_decl(d)}\nd["{k}"] = d.get("{k}", 0) + 1\nd["{k}"]', "1", "get gives 0 for the new key, so the count starts at 0 + 1.")


@_look
def l_dup_key(rng):
    k, a, b = rng.choice(WORDS), _v(rng), _v(rng)
    return _L(f'd = {{"{k}": {a}, "{k}": {b}}}\nd["{k}"]', str(b), "A repeated key keeps its last value.")


@_look
def l_float_key(rng):
    d = [(1, "one"), (2, "two")]
    k = rng.choice([1, 2])
    return _L(f'd = {{1: "one", 2: "two"}}\nd[{k}.0]', d_get(d, k), f"{k}.0 equals {k}, so it finds the same key.")


@_look
def l_str_int_key(rng):
    return _L('d = {1: "a", 2: "b"}\nd["1"]', "KeyError", 'The key is the number 1, and the text "1" is a different key.', True)


@_look
def l_int_str_key(rng):
    return _L('d = {"1": "a", "2": "b"}\nd[1]', "KeyError", 'The keys are text, and the number 1 is a different key from "1".', True)


@_look
def l_both_keys(rng):
    return _L('d = {1: "num", "1": "text"}\nd["1"]', "text", 'The number 1 and the text "1" are two separate keys.')


@_look
def l_bool_key(rng):
    return _L('d = {1: "a", True: "b"}\nd[1]', "b", "True equals 1, so they are one key and the later value wins.")


@_look
def l_tuple_key(rng):
    a, b = rng.sample(range(1, 9), 2)
    ok = rng.random() < 0.5
    return _L(f'd = {{({a}, {b}): "here"}}\nd[({a}, {b})]' if ok else f'd = {{({a}, {b}): "here"}}\nd[({b}, {a})]',
              "here" if ok else "KeyError", "A tuple works as a key, and its order matters." if ok else "(a, b) and (b, a) are different keys.", not ok)


@_look
def l_list_key(rng):
    a = _v(rng)
    return _L(f'{{[{a}]: "x"}}', "TypeError", "A list can change, so it cannot be a dict key (unhashable).", True)


@_look
def l_keys_first(rng):
    d = pairs(rng)
    return _L(f"{_decl(d)}\nlist(d)[0]", d[0][0], "A dict keeps keys in the order they were added.")


@_look
def l_keys_last(rng):
    d = pairs(rng)
    return _L(f"{_decl(d)}\nlist(d)[-1]", d[2][0], "The keys come out in insertion order: the last one added is last.")


@_look
def l_new_key_last(rng):
    d, v = pairs(rng), _v(rng)
    k = _missing(rng, d)
    return _L(f'{_decl(d)}\nd["{k}"] = {v}\nlist(d)[-1]', k, "A new key goes at the end.")


@_look
def l_replace_keeps_place(rng):
    d, v = pairs(rng), _v(rng)
    return _L(f'{_decl(d)}\nd["{d[0][0]}"] = {v}\nlist(d)[0]', d[0][0], "Replacing a value does not move its key.")


@_look
def l_values_i(rng):
    d = pairs(rng)
    i = rng.randrange(3)
    return _L(f"{_decl(d)}\nlist(d.values())[{i}]", str(d[i][1]), "values() follows the same insertion order as the keys.")


@_look
def l_items_i(rng):
    d = pairs(rng)
    i = rng.randrange(3)
    return _L(f"{_decl(d)}\nlist(d.items())[{i}]", py_show((d[i][0], d[i][1])), "items() gives (key, value) pairs.")


@_look
def l_popitem(rng):
    d = pairs(rng)
    return _L(f"{_decl(d)}\nd.popitem()", py_show((d[2][0], d[2][1])), "popitem removes and returns the most recently added pair.")


@_look
def l_get_chain(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _L(f'{_decl(d)}\nd.get("{_missing(rng, d)}", d["{k}"])', str(v), "The default here is itself a lookup, used because the first key is missing.")


@_look
def l_merge_star(rng):
    a, b = _v(rng), _v(rng)
    k = rng.choice(WORDS)
    return _L(f'x = {{"{k}": {a}}}\ny = {{"{k}": {b}}}\n{{**x, **y}}["{k}"]', str(b), "In a merge, the later dict wins for a shared key.")


@_look
def l_merge_bar(rng):
    a, b = _v(rng), _v(rng)
    k = rng.choice(WORDS)
    return _L(f'x = {{"{k}": {a}}}\ny = {{"{k}": {b}}}\n(x | y)["{k}"]', str(b), "x | y merges, and the right side wins for a shared key.")


@_look
def l_fromkeys(rng):
    ks = words(rng, 3)
    return _L(f"dict.fromkeys({lit(ks)}, 0)[\"{ks[1]}\"]", "0", "fromkeys gives every key the same starting value.")


@_look
def l_zip(rng):
    ks, vs = words(rng, 3), ints(rng, 3, 1, 9)
    i = rng.randrange(3)
    return _L(f'dict(zip({lit(ks)}, {lit(vs)}))["{ks[i]}"]', str(vs[i]), "zip pairs the keys with the values, in order.")


@_look
def l_comp(rng):
    n = rng.randint(4, 7)
    k = rng.randint(1, n)
    return _L(f"{{x: x * x for x in range(1, {n + 1})}}[{k}]", str(k * k), f"The key {k} maps to {k} * {k}.")


@_look
def l_comp_len(rng):
    ws = words(rng, 3)
    i = rng.randrange(3)
    return _L(f'{{w: len(w) for w in {lit(ws)}}}["{ws[i]}"]', str(len(ws[i])), "Each word maps to its own length.")


@_look
def l_invert(rng):
    d = pairs(rng)
    k, v = d[rng.randrange(3)]
    return _L(f"{_decl(d)}\n{{v: k for k, v in d.items()}}[{v}]", k, "Swapping keys and values: the value becomes the way in.")


@_look
def l_sum_values(rng):
    d = pairs(rng)
    return _L(f"{_decl(d)}\nsum(d.values())", str(total([v for _, v in d])), "values() lists the values; sum adds them.")


@_look
def l_max_key(rng):
    d = pairs(rng)
    return _L(f"{_decl(d)}\nmax(d, key=d.get)", best(d, key=lambda p: p[1])[0], "max with key=d.get picks the key whose value is biggest.")


@_look
def l_get_or(rng):
    d = pairs(rng)
    return _L(f'{_decl(d)}\nd.get("{_missing(rng, d)}") or "none"', "none", "get gives None, which is falsy, so or falls through to the right side.")


@_look
def l_zero_or(rng):
    k = rng.choice(WORDS)
    return _L(f'd = {{"{k}": 0}}\nd.get("{k}") or 5', "5", "The stored 0 is falsy, so or replaces it - get(key, 5) would have kept the 0.")


@_look
def l_zero_default(rng):
    k = rng.choice(WORDS)
    return _L(f'd = {{"{k}": 0}}\nd.get("{k}", 5)', "0", "The key exists, so get gives its 0, not the default.")


@_look
def l_is_none(rng):
    d = pairs(rng)
    k, found = rng.choice([(d[rng.randrange(3)][0], True), (_missing(rng, d), False)])
    return _L(f'{_decl(d)}\nd.get("{k}") is None', pyb(not found), "get gives None only when the key is missing.")


@_look
def l_bool(rng):
    code, ans, why = rng.choice([("bool({})", "False", "An empty dict is falsy."),
                                 ('bool({"a": 0})', "True", "A dict with any key is truthy, whatever the value."),
                                 ("not {}", "True", "An empty dict is falsy, so not gives True.")])
    return _L(code, ans, why)


@_look
def l_count_loop(rng):
    w = rng.choice(["hello", "little", "banana", "balloon", "coffee", "pumpkin"])
    ch = rng.choice(w)
    n = 0
    for c in w:
        if c == ch:
            n += 1
    return _L(f'counts = {{}}\nfor c in "{w}":\n    counts[c] = counts.get(c, 0) + 1\ncounts["{ch}"]', str(n), f"It counts each letter; \"{ch}\" appears {n} time(s).")


@_look
def l_last_key_loop(rng):
    d = pairs(rng)
    return _L(f'{_decl(d)}\nfor k in d:\n    last = k\nlast', d[2][0], "Looping over a dict visits the keys in order; last keeps the final one.")


@_look
def l_alias(rng):
    d = pairs(rng)
    return _L(f'{_decl(d)}\ne = d\ne["new"] = 1\n"new" in d', "True", "e = d is the same dict under a second name.")


@_look
def l_copy(rng):
    d = pairs(rng)
    return _L(f'{_decl(d)}\ne = d.copy()\ne["new"] = 1\n"new" in d', "False", "copy() made a separate dict.")


@_look
def l_clear(rng):
    d, n = pairs(rng), _v(rng)
    return _L(f'{_decl(d)}\nd.clear()\nd.get("{d[0][0]}", {n})', str(n), "clear empties the dict, so the key is missing and get gives the default.")


# ── 4. Set Maths ────────────────────────────────────────────────────────

SETS: list[Maker] = []


def _set(fn: Maker) -> Maker:
    SETS.append(fn)
    return fn


def _ab(rng: random.Random) -> tuple[list[int], list[int]]:
    """Two small sets that overlap and each have something of their own."""
    while True:
        a, b = ints(rng, rng.randint(3, 5), 1, 8), ints(rng, rng.randint(3, 5), 1, 8)
        if inter(a, b) and diff(a, b) and diff(b, a):
            return a, b


def _ab_decl(a: list[int], b: list[int]) -> str:
    return f"a = {slit(a)}\nb = {slit(b)}\n"


def _S(a, b, tail: str, ans: str, why: str, err: bool = False) -> Item:
    code = _ab_decl(a, b) + tail
    return Item(code, ans, why, check=err_py(code) if err else "")


@_set
def s_union(rng):
    a, b = _ab(rng)
    return _S(a, b, "sorted(a | b)", py_show(sort_by(union(a, b))), "| is the union: everything in either set, once.")


@_set
def s_inter(rng):
    a, b = _ab(rng)
    return _S(a, b, "sorted(a & b)", py_show(sort_by(inter(a, b))), "& is the intersection: only what is in both.")


@_set
def s_diff(rng):
    a, b = _ab(rng)
    return _S(a, b, "sorted(a - b)", py_show(sort_by(diff(a, b))), "a - b is what a has that b does not.")


@_set
def s_diff_rev(rng):
    a, b = _ab(rng)
    return _S(a, b, "sorted(b - a)", py_show(sort_by(diff(b, a))), "b - a is what b has that a does not: the order matters.")


@_set
def s_sym(rng):
    a, b = _ab(rng)
    return _S(a, b, "sorted(a ^ b)", py_show(sort_by(sym(a, b))), "^ keeps what is in exactly one of the two sets.")


@_set
def s_union_len(rng):
    a, b = _ab(rng)
    return _S(a, b, "len(a | b)", str(len(union(a, b))), "The union counts each value once, however many sets hold it.")


@_set
def s_inter_len(rng):
    a, b = _ab(rng)
    return _S(a, b, "len(a & b)", str(len(inter(a, b))), "How many values the two sets share.")


@_set
def s_diff_len(rng):
    a, b = _ab(rng)
    return _S(a, b, "len(a - b)", str(len(diff(a, b))), "How many values are in a but not in b.")


@_set
def s_sym_len(rng):
    a, b = _ab(rng)
    return _S(a, b, "len(a ^ b)", str(len(sym(a, b))), "How many values belong to only one of the sets.")


@_set
def s_method_union(rng):
    a, b = _ab(rng)
    return _S(a, b, "sorted(a.union(b))", py_show(sort_by(union(a, b))), "union() is the method form of |.")


@_set
def s_method_inter(rng):
    a, b = _ab(rng)
    return _S(a, b, "sorted(a.intersection(b))", py_show(sort_by(inter(a, b))), "intersection() is the method form of &.")


@_set
def s_method_diff(rng):
    a, b = _ab(rng)
    return _S(a, b, "sorted(a.difference(b))", py_show(sort_by(diff(a, b))), "difference() is the method form of -.")


@_set
def s_method_sym(rng):
    a, b = _ab(rng)
    return _S(a, b, "sorted(a.symmetric_difference(b))", py_show(sort_by(sym(a, b))), "symmetric_difference() is the method form of ^.")


@_set
def s_in(rng):
    a, b = _ab(rng)
    x = rng.randint(1, 8)
    return _S(a, b, f"{x} in a", pyb(has(a, x)), "in asks whether the set holds that value.")


@_set
def s_in_both(rng):
    a, b = _ab(rng)
    x = rng.randint(1, 8)
    return _S(a, b, f"{x} in a & b", pyb(has(a, x) and has(b, x)), "a & b is built first; then in asks about it.")


@_set
def s_in_union(rng):
    a, b = _ab(rng)
    x = rng.randint(1, 8)
    return _S(a, b, f"{x} in a | b", pyb(has(a, x) or has(b, x)), "a | b is built first; then in asks about it.")


@_set
def s_subset(rng):
    b = ints(rng, rng.randint(4, 5), 1, 8)
    ok = rng.random() < 0.5
    a = take(b, 0, 2) if ok else take(b, 0, 2) + [rng.choice([x for x in range(1, 10) if not has(b, x)])]
    return Item(_ab_decl(a, b) + "a <= b", pyb(ok), "<= asks whether every value of a is also in b." if ok else "a has a value b lacks, so it is not a subset.")


@_set
def s_issubset(rng):
    b = ints(rng, rng.randint(4, 5), 1, 8)
    ok = rng.random() < 0.5
    a = take(b, 1, 3) if ok else take(b, 1, 3) + [rng.choice([x for x in range(1, 10) if not has(b, x)])]
    return Item(_ab_decl(a, b) + "a.issubset(b)", pyb(ok), "issubset is True when every value of a is in b.")


@_set
def s_superset(rng):
    a = ints(rng, rng.randint(4, 5), 1, 8)
    ok = rng.random() < 0.5
    b = take(a, 0, 2) if ok else take(a, 0, 2) + [rng.choice([x for x in range(1, 10) if not has(a, x)])]
    return Item(_ab_decl(a, b) + "a >= b", pyb(ok), ">= asks whether a holds every value of b.")


@_set
def s_disjoint(rng):
    a, b = _ab(rng)
    if rng.random() < 0.5:
        b = diff(b, a)
    return Item(_ab_decl(a, b) + "a.isdisjoint(b)", pyb(not inter(a, b)), "isdisjoint is True when the sets share nothing.")


@_set
def s_eq_order(rng):
    a = ints(rng, 4, 1, 9)
    b = sort_by(a, reverse=True)
    return Item(f"{slit(a)} == {slit(b)}", "True", "Sets have no order, so the same members are equal.")


@_set
def s_eq_list_order(rng):
    a = ints(rng, 3, 1, 9)
    b = sort_by(a, reverse=True)
    return Item(f"{lit(a)} == {lit(b)}", pyb(a == b), "Lists care about order: the same items in a different order are not equal.")


@_set
def s_dedupe(rng):
    xs = dupes(rng)
    return Item(f"sorted(set({lit(xs)}))", py_show(sort_by(uniq(xs))), "set() keeps each value once; sorted puts them in order.")


@_set
def s_all_different(rng):
    xs = dupes(rng) if rng.random() < 0.5 else nums(rng)
    return Item(f"xs = {lit(xs)}\nlen(set(xs)) == len(xs)", pyb(len(uniq(xs)) == len(xs)), "If dropping repeats shortens it, there were repeats.")


@_set
def s_add(rng):
    a = ints(rng, 3, 1, 5)
    v = rng.randint(6, 9)
    return Item(f"s = {slit(a)}\ns.add({v})\nsorted(s)", py_show(sort_by(a + [v])), "add puts the value in.")


@_set
def s_add_dup(rng):
    a = nums(rng)
    return Item(f"s = {slit(a)}\ns.add({a[0]})\nsorted(s)", py_show(sort_by(a)), "The value was already there: a set holds it once.")


@_set
def s_discard(rng):
    a = nums(rng)
    return Item(f"s = {slit(a)}\ns.discard({a[1]})\nsorted(s)", py_show(sort_by(rm_first(a, a[1]))), "discard removes the value.")


@_set
def s_discard_missing(rng):
    a = ints(rng, 3, 1, 5)
    return Item(f"s = {slit(a)}\ns.discard(9)\nsorted(s)", py_show(sort_by(a)), "discard of a missing value does nothing and raises nothing.")


@_set
def s_remove_missing(rng):
    a = ints(rng, 3, 1, 5)
    code = f"s = {slit(a)}\ns.remove(9)\nsorted(s)"
    return Item(code, "KeyError", "remove raises KeyError for a missing value (discard would not).", check=err_py(code))


@_set
def s_update(rng):
    a, b = _ab(rng)
    return _S(a, b, "a.update(b)\nsorted(a)", py_show(sort_by(union(a, b))), "update adds every value of b to a.")


@_set
def s_ior(rng):
    a, b = _ab(rng)
    return _S(a, b, "a |= b\nsorted(a)", py_show(sort_by(union(a, b))), "|= is a union that changes a in place.")


@_set
def s_iand(rng):
    a, b = _ab(rng)
    return _S(a, b, "a &= b\nsorted(a)", py_show(sort_by(inter(a, b))), "&= keeps only the shared values, in place.")


@_set
def s_isub(rng):
    a, b = _ab(rng)
    return _S(a, b, "a -= b\nsorted(a)", py_show(sort_by(diff(a, b))), "-= takes b's values out of a, in place.")


@_set
def s_ixor(rng):
    a, b = _ab(rng)
    return _S(a, b, "a ^= b\nsorted(a)", py_show(sort_by(sym(a, b))), "^= keeps what only one side had, in place.")


@_set
def s_pop_one(rng):
    v = _v(rng)
    return Item(f"{{{v}}}.pop()", str(v), "pop takes an item out of the set; with one member there is no choice.")


@_set
def s_empty_type(rng):
    code, ans, why = rng.choice([("type({}).__name__", "dict", "{} is an empty dict, not an empty set."),
                                 ("type(set()).__name__", "set", "set() is how you write an empty set."),
                                 (f"type({{{_v(rng)}}}).__name__", "set", "Braces with a value inside make a set."),
                                 (f'type({{"a": {_v(rng)}}}).__name__', "dict", "Braces with key: value make a dict.")])
    return Item(code, ans, why)


@_set
def s_letters(rng):
    w = rng.choice(["hello", "little", "banana", "balloon", "carrot", "coffee", "pumpkin"])
    return Item(f'sorted(set("{w}"))', py_show(sort_by(uniq(list(w)))), "set splits the word into its different letters; sorted puts them in order.")


@_set
def s_letters_join(rng):
    w = rng.choice(["hello", "little", "banana", "balloon", "carrot", "coffee", "pumpkin"])
    return Item(f'"".join(sorted(set("{w}")))', "".join(sort_by(uniq(list(w)))), "The different letters, in alphabet order, glued back together.")


@_set
def s_comp(rng):
    xs = nums(rng, 5, 6)
    return Item(f"sorted({{x % 3 for x in {lit(xs)}}})", py_show(sort_by(uniq([fmod(x, 3) for x in xs]))), "x % 3 is 0, 1 or 2, and the set keeps each result once.")


@_set
def s_comp_if(rng):
    xs, k = nums(rng, 5, 6), rng.randint(3, 6)
    return Item(f"sorted({{x for x in {lit(xs)} if x > {k}}})", py_show(sort_by([x for x in xs if x > k])), f"Only the values over {k} go in the set.")


@_set
def s_max_inter(rng):
    a, b = _ab(rng)
    return _S(a, b, "max(a & b)", str(best(inter(a, b))), "The biggest value the two sets share.")


@_set
def s_sum_union(rng):
    a, b = _ab(rng)
    return _S(a, b, "sum(a | b)", str(total(union(a, b))), "Each shared value is added once, because the union holds it once.")


@_set
def s_three(rng):
    a, b = _ab(rng)
    c = ints(rng, 3, 1, 8)
    code = _ab_decl(a, b) + f"c = {slit(c)}\nsorted(a | b | c)"
    return Item(code, py_show(sort_by(union(union(a, b), c))), "Chained | joins all three.")


@_set
def s_three_inter(rng):
    a = ints(rng, 5, 1, 8)
    b, c = ints(rng, 5, 1, 8), ints(rng, 5, 1, 8)
    code = f"a = {slit(a)}\nb = {slit(b)}\nc = {slit(c)}\nsorted(a & b & c)"
    return Item(code, py_show(sort_by(inter(inter(a, b), c))), "Only what all three sets hold survives the chained &.")


@_set
def s_chain(rng):
    a, b = _ab(rng)
    c = ints(rng, 3, 1, 8)
    code = _ab_decl(a, b) + f"c = {slit(c)}\nsorted((a | b) - c)"
    return Item(code, py_show(sort_by(diff(union(a, b), c))), "The brackets go first: the union, then take c's values away.")


@_set
def s_lists_equal_sets(rng):
    xs = dupes(rng)
    ys = sort_by(xs)
    return Item(f"set({lit(xs)}) == set({lit(ys)})", "True", "Same values, so the same set - order and repeats do not matter.")


@_set
def s_range(rng):
    a, b = rng.randint(3, 8), rng.randint(3, 8)
    return Item(f"sorted(set(range({a})) & set(range({b})))", py_show(list(range(min(a, b)))), "Both ranges start at 0, so the shared part is the shorter range.")


@_set
def s_unhashable(rng):
    code = f"{{[{_v(rng)}, {_v(rng)}]}}"
    return Item(code, "TypeError", "A list cannot go in a set because it can change (it is unhashable).", check=err_py(code))


@_set
def s_tuples(rng):
    a, b = rng.sample(range(1, 9), 2)
    return Item(f"len({{({a}, {b}), ({b}, {a}), ({a}, {b})}})", "2", "A tuple can go in a set; (a, b) and (b, a) are different, and the repeat counts once.")


@_set
def s_diff_self(rng):
    a = nums(rng)
    return Item(f"a = {slit(a)}\nsorted(a - a)", "[]", "Taking a set's own values away leaves nothing.")


@_set
def s_empty_subset(rng):
    a = nums(rng)
    code, ans, why = rng.choice([(f"set() <= {slit(a)}", "True", "The empty set is a subset of every set."),
                                 (f"{slit(a)} < {slit(a)}", "False", "< means a proper subset: a set is not a proper subset of itself."),
                                 (f"{slit(a)} <= {slit(a)}", "True", "<= allows equality: a set is a subset of itself.")])
    return Item(code, ans, why)


@_set
def s_one_one(rng):
    return Item("len({1, 1.0, True})", "1", "1, 1.0 and True are all equal, so the set keeps just one.")


# ── 5. Min Max Sum ──────────────────────────────────────────────────────

MINMAX: list[Maker] = []


def _mm(fn: Maker) -> Maker:
    MINMAX.append(fn)
    return fn


def _signed(rng: random.Random, lo: int = 4, hi: int = 6) -> list[int]:
    """Different ints from -9..9 with at least one negative."""
    while True:
        xs = ints(rng, rng.randint(lo, hi), -9, 9)
        if any(x < 0 for x in xs):
            return xs


def _M(code: str, ans, why: str, err: bool = False) -> Item:
    return Item(code, str(ans), why, check=err_py(code) if err else "")


@_mm
def m_max(rng):
    xs = nums(rng, 4, 6)
    return _M(f"max({lit(xs)})", best(xs), "max is the biggest item.")


@_mm
def m_min(rng):
    xs = nums(rng, 4, 6)
    return _M(f"min({lit(xs)})", best(xs, want_max=False), "min is the smallest item.")


@_mm
def m_sum(rng):
    xs = nums(rng, 4, 6)
    return _M(f"sum({lit(xs)})", total(xs), "sum adds every item.")


@_mm
def m_max_neg(rng):
    xs = _signed(rng)
    return _M(f"max({lit(xs)})", best(xs), "With negatives, the biggest is the one closest to the positive side.")


@_mm
def m_min_neg(rng):
    xs = _signed(rng)
    return _M(f"min({lit(xs)})", best(xs, want_max=False), "-9 is smaller than -1: the most negative number is the minimum.")


@_mm
def m_sum_neg(rng):
    xs = _signed(rng)
    return _M(f"sum({lit(xs)})", total(xs), "Negative items subtract as they are added.")


@_mm
def m_all_neg(rng):
    xs = ints(rng, 4, -9, -1)
    return _M(f"max({lit(xs)})", best(xs), "Among negatives the biggest is the one nearest zero.")


@_mm
def m_range(rng):
    xs = _signed(rng)
    return _M(f"xs = {lit(xs)}\nmax(xs) - min(xs)", best(xs) - best(xs, want_max=False), "Biggest minus smallest: the spread.")


@_mm
def m_args(rng):
    xs = ints(rng, 3, -9, 9)
    return _M(f"max({', '.join(map(str, xs))})", best(xs), "max can take its items as separate arguments.")


@_mm
def m_min_args(rng):
    xs = ints(rng, 3, -9, 9)
    return _M(f"min({', '.join(map(str, xs))})", best(xs, want_max=False), "min can take its items as separate arguments.")


@_mm
def m_str_max(rng):
    ws = words(rng, 3)
    return _M(f"max({lit(ws)})", best(ws), "Strings compare letter by letter, like a dictionary: the later word is bigger.")


@_mm
def m_str_min(rng):
    ws = words(rng, 3)
    return _M(f"min({lit(ws)})", best(ws, want_max=False), "The word that comes first in the dictionary is the minimum.")


@_mm
def m_chars_max(rng):
    w = rng.choice(WORDS)
    return _M(f'max("{w}")', best(list(w)), "A string is a row of letters: max is the one latest in the alphabet.")


@_mm
def m_chars_min(rng):
    w = rng.choice(WORDS)
    return _M(f'min("{w}")', best(list(w), want_max=False), "min of a string is its earliest letter in the alphabet.")


@_mm
def m_key_len(rng):
    ws = words(rng, 4)
    return _M(f"max({lit(ws)}, key=len)", best(ws, key=len), "key=len compares the words by length; max gives the word, and the first one wins a tie.")


@_mm
def m_key_len_min(rng):
    ws = words(rng, 4)
    return _M(f"min({lit(ws)}, key=len)", best(ws, key=len, want_max=False), "key=len compares by length; min gives the shortest word (the first on a tie).")


@_mm
def m_key_neg(rng):
    xs = nums(rng, 4, 5)
    return _M(f"max({lit(xs)}, key=lambda x: -x)", best(xs, key=lambda x: -x), "Ranking by -x flips the order, so max finds the smallest.")


@_mm
def m_key_abs(rng):
    xs = _signed(rng)
    return _M(f"min({lit(xs)}, key=abs)", best(xs, key=lambda x: x if x >= 0 else -x, want_max=False), "key=abs ranks by distance from zero, and the item itself comes back.")


@_mm
def m_key_abs_max(rng):
    xs = _signed(rng)
    return _M(f"max({lit(xs)}, key=abs)", best(xs, key=lambda x: x if x >= 0 else -x), "The item furthest from zero, sign and all.")


@_mm
def m_key_mod(rng):
    xs = nums(rng, 4, 5)
    return _M(f"max({lit(xs)}, key=lambda x: x % 3)", best(xs, key=lambda x: fmod(x, 3)), "It ranks by x % 3; on a tie the first one wins.")


@_mm
def m_sorted_idx(rng):
    xs = nums(rng, 4, 6)
    return _M(f"sorted({lit(xs)})[1]", sort_by(xs)[1], "sorted puts them in order; index 1 is the second smallest.")


@_mm
def m_sorted_neg(rng):
    xs = nums(rng, 4, 6)
    return _M(f"sorted({lit(xs)})[-2]", sort_by(xs)[len(xs) - 2], "Index -2 of the sorted list is the second biggest.")


@_mm
def m_sorted_rev(rng):
    xs = nums(rng, 4, 6)
    return _M(f"sorted({lit(xs)}, reverse=True)[1]", sort_by(xs, reverse=True)[1], "Biggest first, so index 1 is the second biggest.")


@_mm
def m_mean(rng):
    xs = nums(rng, 4, 5)
    xs = take(xs, 0, rng.choice([2, 4, 5]) if len(xs) >= 5 else rng.choice([2, 4]))
    return _M(f"xs = {lit(xs)}\nsum(xs) / len(xs)", py_div(total(xs), len(xs)), "Dividing with / always gives a float, even when it comes out whole.")


@_mm
def m_mean_floor(rng):
    xs = nums(rng, 4, 5)
    n = len(xs)
    q = 0
    while (q + 1) * n <= total(xs):
        q += 1
    return _M(f"xs = {lit(xs)}\nsum(xs) // len(xs)", q, "// divides and rounds down to a whole number.")


@_mm
def m_sum_start(rng):
    xs, s = nums(rng, 3, 4), rng.randint(10, 50)
    return _M(f"sum({lit(xs)}, {s})", total(xs) + s, "The second argument is where the adding starts.")


@_mm
def m_sum_bool(rng):
    xs, k = nums(rng, 5, 6), rng.randint(3, 6)
    return _M(f"sum(x > {k} for x in {lit(xs)})", len([x for x in xs if x > k]), "Each True counts as 1, so the sum counts the items bigger than " + str(k) + ".")


@_mm
def m_sum_sq(rng):
    xs = nums(rng, 3, 4)
    return _M(f"sum(x * x for x in {lit(xs)})", total([x * x for x in xs]), "Square each item, then add.")


@_mm
def m_sum_even(rng):
    xs = nums(rng, 5, 6)
    return _M(f"sum(x for x in {lit(xs)} if x % 2 == 0)", total([x for x in xs if fmod(x, 2) == 0]), "Only the even items are added.")


@_mm
def m_sum_len(rng):
    ws = words(rng, 3)
    return _M(f"sum(len(w) for w in {lit(ws)})", total([len(w) for w in ws]), "The letters of all the words together.")


@_mm
def m_max_len(rng):
    ws = words(rng, 4)
    return _M(f"max(len(w) for w in {lit(ws)})", best([len(w) for w in ws]), "max of the lengths: a number, not the word.")


@_mm
def m_min_default(rng):
    code, ans, why = rng.choice([("min([], default=0)", "0", "default is what min gives for an empty list."),
                                 ("max([], default=-1)", "-1", "default is what max gives for an empty list."),
                                 ("sum([])", "0", "The sum of nothing is 0.")])
    return _M(code, ans, why)


@_mm
def m_empty_error(rng):
    code = rng.choice(["max([])", "min([])", "max(())"])
    return _M(code, "ValueError", "max and min of nothing raise ValueError (unless you give default=).", True)


@_mm
def m_mixed_error(rng):
    return _M(f'max([{_v(rng)}, "{rng.choice(WORDS)}"])', "TypeError", "A number and a string cannot be compared.", True)


@_mm
def m_numstr_max(rng):
    xs = ["10", "9", "100"] if rng.random() < 0.5 else ["8", "75", "100", "9"]
    return _M(f"max({lit(xs)})", best(xs), "Strings compare character by character, so '9' beats '100'.")


@_mm
def m_numstr_min(rng):
    xs = ["10", "9", "100"] if rng.random() < 0.5 else ["8", "75", "100", "9"]
    return _M(f"min({lit(xs)})", best(xs, want_max=False), "As text, '100' comes before '75' and '8' - the first character decides.")


@_mm
def m_numstr_key(rng):
    xs = ["10", "9", "100"] if rng.random() < 0.5 else ["8", "75", "100", "9"]
    return _M(f"max({lit(xs)}, key=int)", best(xs, key=int), "key=int compares them as numbers, and the original string comes back.")


@_mm
def m_dict_max(rng):
    d = pairs(rng)
    return _M(f"d = {dlit(d)}\nmax(d.values())", best([v for _, v in d]), "values() are the numbers; max picks the biggest.")


@_mm
def m_dict_min_key(rng):
    d = pairs(rng)
    return _M(f"d = {dlit(d)}\nmin(d, key=d.get)", best(d, key=lambda p: p[1], want_max=False)[0], "min with key=d.get gives the key with the smallest value.")


@_mm
def m_dict_max_key(rng):
    d = pairs(rng)
    return _M(f"d = {dlit(d)}\nmax(d)", best([k for k, _ in d]), "max of a dict looks at its keys: the latest word alphabetically.")


@_mm
def m_dict_sum(rng):
    d = pairs(rng)
    return _M(f"d = {dlit(d)}\nsum(d.values())", total([v for _, v in d]), "Add up what the dict stores.")


@_mm
def m_range_sum(rng):
    a = rng.randint(1, 4)
    b = a + rng.randint(3, 6)
    return _M(f"sum(range({a}, {b}))", total(list(range(a, b))), f"{a} up to {b - 1}, added together (the end is left out).")


@_mm
def m_slice(rng):
    xs = nums(rng, 5, 6)
    return _M(f"max({lit(xs)}[:3])", best(take(xs, 0, 3)), "The slice keeps the first three; max looks only at those.")


@_mm
def m_slice_sum(rng):
    xs = nums(rng, 5, 6)
    return _M(f"sum({lit(xs)}[-2:])", total(take(xs, len(xs) - 2, len(xs))), "The last two items, added.")


@_mm
def m_tuple_max(rng):
    ps = []
    while len(ps) < 3:
        p = (rng.randint(1, 3), rng.randint(1, 9))
        if not has(ps, p):
            ps.append(p)
    shown = "[" + ", ".join(f"({a}, {b})" for a, b in ps) + "]"
    return _M(f"max({shown})", py_show(best(ps)), "Tuples compare item by item: the first numbers first, the second only on a tie.")


@_mm
def m_sum_nested(rng):
    a, b, c = _v(rng), _v(rng), _v(rng)
    return _M(f"sum([[{a}, {b}], [{c}]], [])", py_show([a, b, c]), "Starting from [], + joins the lists one after another.")


@_mm
def m_sum_floats(rng):
    qs = [rng.randint(1, 7) for _ in range(rng.randint(3, 4))]
    shown = "[" + ", ".join(decimal_div(q, 4) for q in qs) + "]"
    return _M(f"sum({shown})", py_div(total(qs), 4), "These are quarters, which floats store exactly, so the sum is exact.")


@_mm
def m_index_max(rng):
    xs = nums(rng, 4, 6)
    return _M(f"xs = {lit(xs)}\nxs.index(max(xs))", pos(xs, best(xs)), "max finds the biggest value; index says where it sits.")


@_mm
def m_index_min(rng):
    xs = nums(rng, 4, 6)
    return _M(f"xs = {lit(xs)}\nxs.index(min(xs))", pos(xs, best(xs, want_max=False)), "min finds the smallest value; index says where it sits.")


@_mm
def m_count_max(rng):
    xs = dupes(rng)
    top = best(xs)
    n = 0
    for x in xs:
        if x == top:
            n += 1
    return _M(f"xs = {lit(xs)}\nxs.count(max(xs))", n, "How many times the biggest value appears.")


@_mm
def m_second_distinct(rng):
    xs = dupes(rng)
    return _M(f"sorted(set({lit(xs)}))[-2]", sort_by(uniq(xs))[len(uniq(xs)) - 2], "set drops repeats, so the second from the end is the second biggest distinct value.")


@_mm
def m_digits(rng):
    n = rng.randint(1000, 99999)
    return _M(f"sum(int(c) for c in str({n}))", total([int(c) for c in str(n)]), "str() splits the number into digits; int turns each back; sum adds.")


@_mm
def m_len_times(rng):
    xs = nums(rng, 3, 5)
    return _M(f"xs = {lit(xs)}\nlen(xs) * min(xs)", len(xs) * best(xs, want_max=False), "Two separate answers multiplied: the count, then the smallest.")


@_mm
def m_max_of_two(rng):
    a, b = nums(rng, 2, 3), nums(rng, 2, 3)
    return _M(f"max(max({lit(a)}), max({lit(b)}))", max(best(a), best(b)), "Each max finds one list's biggest; the outer max picks between them.")


@_mm
def m_sorted_equal(rng):
    xs = nums(rng, 3, 5)
    return _M(f"xs = {lit(xs)}\nsorted(xs)[-1] == max(xs)", "True", "The last of a sorted list is always the biggest.")


# ── 6. Unpack It ────────────────────────────────────────────────────────

UNPACK: list[Maker] = []


def _un(fn: Maker) -> Maker:
    UNPACK.append(fn)
    return fn


def _U(code: str, ans, why: str, err: bool = False) -> Item:
    return Item(code, str(ans), why, check=err_py(code) if err else "")


@_un
def u_basic(rng):
    xs = nums(rng, 3, 3)
    return _U(f"a, b, c = {lit(xs)}\nb", xs[1], "The names take the items in order: a the first, b the second, c the third.")


@_un
def u_basic_c(rng):
    xs = nums(rng, 3, 3)
    return _U(f"a, b, c = {', '.join(map(str, xs))}\nc", xs[2], "A bare comma list is a tuple, and it unpacks the same way.")


@_un
def u_swap(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"a, b = {a}, {b}\na, b = b, a\na", b, "The right side is worked out first, then both names are set: a takes b's old value.")


@_un
def u_swap_tuple(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"a, b = {a}, {b}\na, b = b, a\n(a, b)", py_show((b, a)), "After the swap a holds the old b and b the old a.")


@_un
def u_swap_list(rng):
    xs = nums(rng, 4, 5)
    out = [xs[len(xs) - 1]] + take(xs, 1, len(xs) - 1) + [xs[0]]
    return _U(f"xs = {lit(xs)}\nxs[0], xs[-1] = xs[-1], xs[0]\nxs", py_show(out), "The first and last items trade places.")


@_un
def u_first_rest(rng):
    xs = nums(rng, 4, 5)
    return _U(f"first, *rest = {lit(xs)}\nrest", py_show(take(xs, 1, len(xs))), "*rest collects everything the other names did not take, as a list.")


@_un
def u_first(rng):
    xs = nums(rng, 4, 5)
    return _U(f"first, *rest = {lit(xs)}\nfirst", xs[0], "first takes just the first item.")


@_un
def u_init_last(rng):
    xs = nums(rng, 4, 5)
    return _U(f"*init, last = {lit(xs)}\ninit", py_show(take(xs, 0, len(xs) - 1)), "*init collects everything but the last item.")


@_un
def u_last(rng):
    xs = nums(rng, 4, 5)
    return _U(f"*init, last = {lit(xs)}\nlast", xs[len(xs) - 1], "last takes the final item.")


@_un
def u_mid(rng):
    xs = nums(rng, 4, 6)
    return _U(f"first, *mid, last = {lit(xs)}\nmid", py_show(take(xs, 1, len(xs) - 1)), "mid gets what is between the first and the last.")


@_un
def u_star_empty(rng):
    xs = nums(rng, 2, 2)
    return _U(f"a, b, *c = {lit(xs)}\nc", "[]", "The star gets whatever is left - here, nothing: an empty list.")


@_un
def u_nested(rng):
    a, b, c = ints(rng, 3, 1, 9)
    return _U(f"a, (b, c) = {a}, ({b}, {c})\nc", c, "The brackets unpack the inner pair into b and c.")


@_un
def u_str(rng):
    w = rng.choice([w for w in WORDS if len(w) == 3])
    return _U(f'a, b, c = "{w}"\nb', w[1], "A string unpacks letter by letter.")


@_un
def u_str_star(rng):
    w = rng.choice([w for w in WORDS if len(w) >= 4])
    return _U(f'a, *b = "{w}"\nb', py_show(list(w[1:])), "The star gets the rest of the letters, as a list of one-letter strings.")


@_un
def u_too_many(rng):
    xs = nums(rng, 3, 3)
    return _U(f"a, b = {lit(xs)}\na", "ValueError", "Three items cannot fit two names: ValueError (too many values to unpack).", True)


@_un
def u_too_few(rng):
    xs = nums(rng, 2, 2)
    return _U(f"a, b, c = {lit(xs)}\na", "ValueError", "Two items cannot fill three names: ValueError (not enough values).", True)


@_un
def u_one_name(rng):
    v = _v(rng)
    return _U(f"a, = [{v}]\na", v, "The trailing comma makes it an unpacking of a one-item list.")


@_un
def u_underscore(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"_, y = ({a}, {b})\ny", b, "_ is just a name people use for a value they do not need.")


@_un
def u_fib(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"a, b = {a}, {b}\na, b = b, a + b\nb", a + b, "The right side uses the OLD a and b, so the new b is old a + old b.")


@_un
def u_fib_a(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"a, b = {a}, {b}\na, b = b, a + b\na", b, "The new a is the old b.")


@_un
def u_chain_num(rng):
    v = _v(rng)
    return _U(f"a = b = {v}\nb += 1\na", v, "Numbers cannot change: b += 1 makes b name a new number, and a keeps the old one.")


@_un
def u_chain_list(rng):
    v, w = ints(rng, 2, 1, 9)
    return _U(f"a = b = [{v}]\nb.append({w})\na", py_show([v, w]), "a = b = [...] gives both names the same list, so the append shows in a.")


@_un
def u_rotate(rng):
    a, b, c = ints(rng, 3, 1, 9)
    return _U(f"a, b, c = {a}, {b}, {c}\na, b, c = b, c, a\n(a, b, c)", py_show((b, c, a)), "Each name takes the next one's old value; a takes the old c's turn at the end.")


@_un
def u_divmod(rng):
    n, m = rng.randint(10, 40), rng.randint(3, 9)
    return _U(f"q, r = divmod({n}, {m})\nr", fmod(n, m), "divmod gives the quotient and the remainder as a pair.")


@_un
def u_divmod_q(rng):
    n, m = rng.randint(10, 40), rng.randint(3, 9)
    q = 0
    while (q + 1) * m <= n:
        q += 1
    return _U(f"q, r = divmod({n}, {m})\nq", q, "The first of the pair is how many times it fits.")


@_un
def u_func_two(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"def f():\n    return {a}, {b}\np, q = f()\nq", b, "Returning two values returns one tuple, and the caller unpacks it.")


@_un
def u_func_tuple(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"def f():\n    return {a}, {b}\nf()", py_show((a, b)), "return a, b gives back a tuple.")


@_un
def u_for_pairs(rng):
    ps = [tuple(ints(rng, 2, 1, 5)) for _ in range(2)]
    t = 0
    for a, b in ps:
        t += a * b
    shown = "[" + ", ".join(f"({a}, {b})" for a, b in ps) + "]"
    return _U(f"total = 0\nfor a, b in {shown}:\n    total += a * b\ntotal", t, "Each pair unpacks into a and b, and their product is added.")


@_un
def u_items_loop(rng):
    d = pairs(rng)
    return _U(f"d = {dlit(d)}\nfor k, v in d.items():\n    last = v\nlast", d[2][1], "items() gives (key, value) pairs; the loop leaves the last value in last.")


@_un
def u_enumerate_i(rng):
    ws = words(rng, rng.randint(3, 4))
    return _U(f"for i, w in enumerate({lit(ws)}):\n    pass\ni", len(ws) - 1, "enumerate counts from 0, and i keeps its last value after the loop.")


@_un
def u_enumerate_start(rng):
    ws = words(rng, 3)
    s = rng.randint(1, 5)
    return _U(f"list(enumerate({lit(ws)}, {s}))[1]", py_show((s + 1, ws[1])), f"start={s} sets the first count, so the second item is numbered {s + 1}.")


@_un
def u_zip_pairs(rng):
    ws, ns = words(rng, 3), ints(rng, 3, 1, 9)
    return _U(f"list(zip({lit(ws)}, {lit(ns)}))[1]", py_show((ws[1], ns[1])), "zip makes a tuple from each position of the two lists.")


@_un
def u_zip_star(rng):
    a, b, c, d = ints(rng, 4, 1, 9)
    return _U(f"x, y = zip(*[({a}, {b}), ({c}, {d})])\ny", py_show((b, d)), "zip(*pairs) turns the pairs sideways: all the firsts, then all the seconds.")


@_un
def u_dict_first(rng):
    d = pairs(rng)
    return _U(f"d = {dlit(d)}\nk, v = list(d.items())[0]\nv", d[0][1], "The first pair unpacks into key and value.")


@_un
def u_tuple_index(rng):
    xs = nums(rng, 3, 4)
    i = rng.randrange(len(xs))
    return _U(f"t = ({', '.join(map(str, xs))})\nt[{i}]", xs[i], "A tuple is indexed like a list.")


@_un
def u_tuple_slice(rng):
    xs = nums(rng, 4, 5)
    return _U(f"t = ({', '.join(map(str, xs))})\nt[1:]", py_show(tuple(take(xs, 1, len(xs)))), "Slicing a tuple gives a tuple.")


@_un
def u_tuple_type(rng):
    v = _v(rng)
    code, ans, why = rng.choice([(f"type(({v})).__name__", "int", "Brackets alone are just grouping: (5) is the number 5."),
                                 (f"type(({v},)).__name__", "tuple", "The comma is what makes a tuple."),
                                 (f"type(({v}, {v})).__name__", "tuple", "Two items with a comma: a tuple.")])
    return _U(code, ans, why)


@_un
def u_tuple_comma(rng):
    v = _v(rng)
    return _U(f"t = {v},\nt", py_show((v,)), "A trailing comma makes a one-item tuple, printed with its comma.")


@_un
def u_tuple_add(rng):
    a, b, c = ints(rng, 3, 1, 9)
    return _U(f"({a}, {b}) + ({c},)", py_show((a, b, c)), "+ joins tuples into a new tuple.")


@_un
def u_tuple_mul(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"({a}, {b}) * 2", py_show((a, b, a, b)), "* 2 repeats the tuple.")


@_un
def u_tuple_cmp(rng):
    a, b = rng.randint(1, 3), rng.randint(1, 3)
    c, d = rng.randint(1, 3), rng.randint(1, 3)
    return _U(f"({a}, {b}) < ({c}, {d})", pyb(lt((a, b), (c, d))), "Tuples compare item by item; the second item only matters when the first are equal.")


@_un
def u_tuple_methods(rng):
    xs = dupes(rng)
    v = xs[0]
    n = 0
    for x in xs:
        if x == v:
            n += 1
    return _U(f"t = ({', '.join(map(str, xs))})\nt.count({v})", n, "count says how many items equal the value.")


@_un
def u_tuple_index_m(rng):
    xs = nums(rng, 4, 5)
    v = rng.choice(xs)
    return _U(f"t = ({', '.join(map(str, xs))})\nt.index({v})", pos(xs, v), "index gives the position of the first match.")


@_un
def u_tuple_assign(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"t = ({a}, {b})\nt[0] = {_v(rng)}\nt", "TypeError", "A tuple cannot be changed after it is made.", True)


@_un
def u_tuple_inner(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"t = ([{a}], {b})\nt[0].append(9)\nt", py_show(([a, 9], b)), "The tuple holds the same list, and the list itself can still change.")


@_un
def u_tuple_list(rng):
    xs = nums(rng, 3, 3)
    return _U(f"tuple({lit(xs)})", py_show(tuple(xs)), "tuple() turns a list into a tuple.")


@_un
def u_list_tuple(rng):
    xs = nums(rng, 3, 3)
    return _U(f"list(({', '.join(map(str, xs))}))", py_show(xs), "list() turns a tuple into a list.")


@_un
def u_sorted_pair(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"lo, hi = sorted(({a}, {b}))\nlo", min(a, b), "sorted gives a list in order, and the two names unpack it: lo is the smaller.")


@_un
def u_star_call(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"def f(a, b):\n    return a - b\nf(*[{a}, {b}])", a - b, "* spreads the list into separate arguments.")


@_un
def u_star_call_dict(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f'def f(a, b):\n    return a - b\nf(**{{"b": {a}, "a": {b}}})', b - a, "** spreads a dict into keyword arguments, matched by name.")


@_un
def u_args(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f"def f(*args):\n    return args\nf({a}, {b})", py_show((a, b)), "*args collects the extra arguments into a tuple.")


@_un
def u_minmax(rng):
    xs = nums(rng, 4, 5)
    return _U(f"lo, hi = min({lit(xs)}), max({lit(xs)})\nhi - lo", best(xs) - best(xs, want_max=False), "Two values on one line, then their difference.")


@_un
def u_split_unpack(rng):
    a, b = rng.sample(WORDS, 2)
    return _U(f'first, second = "{a} {b}".split()\nsecond', b, "split() gives a two-item list, which unpacks.")


@_un
def u_split_too_many(rng):
    a, b, c = rng.sample(WORDS, 3)
    return _U(f'first, second = "{a} {b} {c}".split()\nfirst', "ValueError", "Three words do not fit two names.", True)


@_un
def u_nested_for(rng):
    a, b, c = ints(rng, 3, 1, 9)
    return _U(f"for (a, b), c in [(({a}, {b}), {c})]:\n    r = a + b + c\nr", a + b + c, "The inner pair unpacks too, inside the loop header.")


@_un
def u_dict_unpack(rng):
    d = pairs(rng, 2)
    return _U(f"a, b = {dlit(d)}\nb", d[1][0], "Unpacking a dict gives its keys, in insertion order.")


@_un
def u_map_int(rng):
    a, b = ints(rng, 2, 1, 9)
    return _U(f'a, b = map(int, "{a} {b}".split())\na + b', a + b, "map(int, ...) turns each piece into a number before they unpack.")


# ── 7. Nested Reach ─────────────────────────────────────────────────────

NESTED: list[Maker] = []


def _ne(fn: Maker) -> Maker:
    NESTED.append(fn)
    return fn


def _N(code: str, ans, why: str, err: bool = False) -> Item:
    return Item(code, str(ans), why, check=err_py(code) if err else "")


def _grid(rng: random.Random, rows: int | None = None, cols: int | None = None) -> list[list[int]]:
    r, c = rows or rng.randint(2, 3), cols or rng.randint(3, 4)
    return [ints(rng, c, 1, 9) for _ in range(r)]


@_ne
def n_grid(rng):
    g = _grid(rng)
    r, c = rng.randrange(len(g)), rng.randrange(len(g[0]))
    return _N(f"grid = {lit(g)}\ngrid[{r}][{c}]", g[r][c], "The first [] picks the row, the second the item in it.")


@_ne
def n_grid_neg(rng):
    g = _grid(rng)
    return _N(f"grid = {lit(g)}\ngrid[-1][-1]", g[len(g) - 1][len(g[0]) - 1], "grid[-1] is the last row; its [-1] is the last item.")


@_ne
def n_grid_row(rng):
    g = _grid(rng)
    r = rng.randrange(len(g))
    return _N(f"grid = {lit(g)}\ngrid[{r}]", py_show(g[r]), "One index gives a whole row.")


@_ne
def n_grid_col(rng):
    g = _grid(rng)
    c = rng.randrange(len(g[0]))
    return _N(f"grid = {lit(g)}\n[row[{c}] for row in grid]", py_show([row[c] for row in g]), "It takes the same position from every row: a column.")


@_ne
def n_grid_rows(rng):
    g = _grid(rng)
    return _N(f"grid = {lit(g)}\nlen(grid)", len(g), "len of the outer list counts the rows.")


@_ne
def n_grid_cols(rng):
    g = _grid(rng)
    return _N(f"grid = {lit(g)}\nlen(grid[0])", len(g[0]), "grid[0] is a row; its length counts the columns.")


@_ne
def n_grid_sum_row(rng):
    g = _grid(rng)
    r = rng.randrange(len(g))
    return _N(f"grid = {lit(g)}\nsum(grid[{r}])", total(g[r]), "grid[r] is one row, and sum adds its items.")


@_ne
def n_grid_diag(rng):
    g = _grid(rng, 3, 3)
    return _N(f"grid = {lit(g)}\n[grid[i][i] for i in range(3)]", py_show([g[i][i] for i in range(3)]), "Row 0 column 0, row 1 column 1, row 2 column 2.")


@_ne
def n_grid_flat(rng):
    g = _grid(rng)
    flat = [x for row in g for x in row]
    k = rng.randrange(len(flat))
    return _N(f"grid = {lit(g)}\n[x for row in grid for x in row][{k}]", flat[k], "The flat list reads row after row, left to right.")


@_ne
def n_grid_flat_len(rng):
    g = _grid(rng)
    return _N(f"grid = {lit(g)}\nlen([x for row in grid for x in row])", len(g) * len(g[0]), "Every item of every row: rows times columns.")


@_ne
def n_grid_transpose(rng):
    g = _grid(rng)
    c = rng.randrange(len(g[0]))
    return _N(f"grid = {lit(g)}\nlist(zip(*grid))[{c}]", py_show(tuple(row[c] for row in g)), "zip(*grid) turns rows into columns, as tuples.")


@_ne
def n_grid_max(rng):
    g = _grid(rng)
    return _N(f"grid = {lit(g)}\nmax(max(row) for row in grid)", best([best(row) for row in g]), "The biggest of each row's biggest.")


@_ne
def n_grid_set(rng):
    g, v = _grid(rng), _v(rng)
    r, c = rng.randrange(len(g)), rng.randrange(len(g[0]))
    row = take(g[r], 0, c) + [v] + take(g[r], c + 1, len(g[r]))
    return _N(f"grid = {lit(g)}\ngrid[{r}][{c}] = {v}\ngrid[{r}]", py_show(row), "The assignment changes one item inside that row.")


@_ne
def n_grid_loop(rng):
    g = _grid(rng)
    return _N(f"grid = {lit(g)}\ntotal = 0\nfor row in grid:\n    total += row[0]\ntotal", total([row[0] for row in g]), "It adds the first item of each row.")


@_ne
def n_grid_str(rng):
    ws = words(rng, 2, 4)
    i, j = rng.randrange(2), rng.randrange(4)
    return _N(f"grid = {lit(ws)}\ngrid[{i}][{j}]", ws[i][j], "A list of strings: the first index picks the word, the second the letter.")


@_ne
def n_alias_rows(rng):
    v = rng.randint(5, 9)
    return _N(f"grid = [[0] * 2] * 2\ngrid[0][0] = {v}\ngrid", f"[[{v}, 0], [{v}, 0]]",
              "[row] * 2 repeats the SAME row twice, so a change shows in both.")


@_ne
def n_comp_rows(rng):
    v = rng.randint(5, 9)
    return _N(f"grid = [[0] * 2 for _ in range(2)]\ngrid[0][0] = {v}\ngrid", f"[[{v}, 0], [0, 0]]",
              "The comprehension builds a fresh row each time, so only one changes.")


@_ne
def n_shallow(rng):
    a, b = ints(rng, 2, 1, 9)
    return _N(f"a = [[{a}], [{b}]]\nb = a.copy()\nb[0].append(9)\na[0]", py_show([a, 9]), "copy() is shallow: the inner lists are shared.")


@_ne
def n_shallow_outer(rng):
    a, b = ints(rng, 2, 1, 9)
    return _N(f"a = [[{a}], [{b}]]\nb = a.copy()\nb.append([9])\nlen(a)", 2, "Adding to the outer list of the copy leaves a alone.")


@_ne
def n_deep(rng):
    a, b = ints(rng, 2, 1, 9)
    return _N(f"a = [[{a}], [{b}]]\nb = [row[:] for row in a]\nb[0].append(9)\na[0]", py_show([a]), "Each row was copied too, so a's rows are untouched.")


@_ne
def n_dict2(rng):
    k1, k2 = rng.sample(WORDS, 2)
    v = _v(rng)
    return _N(f'd = {{"{k1}": {{"{k2}": {v}}}}}\nd["{k1}"]["{k2}"]', v, "The first [] gives the inner dict; the second looks in it.")


@_ne
def n_dict3(rng):
    k1, k2, k3 = rng.sample(WORDS, 3)
    v = _v(rng)
    return _N(f'd = {{"{k1}": {{"{k2}": {{"{k3}": {v}}}}}}}\nd["{k1}"]["{k2}"]["{k3}"]', v, "One [] per level, outermost first.")


@_ne
def n_dict_list(rng):
    k = rng.choice(WORDS)
    xs = nums(rng, 3, 4)
    i = rng.randrange(len(xs))
    return _N(f'd = {{"{k}": {lit(xs)}}}\nd["{k}"][{i}]', xs[i], "d[key] is the list; then index it.")


@_ne
def n_dict_list_neg(rng):
    k = rng.choice(WORDS)
    xs = nums(rng, 3, 4)
    return _N(f'd = {{"{k}": {lit(xs)}}}\nd["{k}"][-1]', xs[len(xs) - 1], "d[key] is the list; [-1] is its last item.")


@_ne
def n_list_dict(rng):
    ws = words(rng, 2)
    vs = ints(rng, 2, 1, 9)
    i = rng.randrange(2)
    data = "[" + ", ".join(f'{{"name": "{w}", "n": {v}}}' for w, v in zip(ws, vs)) + "]"
    return _N(f'data = {data}\ndata[{i}]["n"]', vs[i], "data[i] is a dict; then look up its key.")


@_ne
def n_list_dict_name(rng):
    ws = words(rng, 2)
    vs = ints(rng, 2, 1, 9)
    data = "[" + ", ".join(f'{{"name": "{w}", "n": {v}}}' for w, v in zip(ws, vs)) + "]"
    return _N(f'data = {data}\ndata[-1]["name"]', ws[1], "data[-1] is the last dict; look up its name.")


@_ne
def n_deep_mix(rng):
    v, w = ints(rng, 2, 1, 9)
    return _N(f'data = {{"a": [{w}, {{"b": {v}}}]}}\ndata["a"][1]["b"]', v, 'data["a"] is a list, [1] its second item (a dict), ["b"] looks inside it.')


@_ne
def n_deep_first(rng):
    v, w = ints(rng, 2, 1, 9)
    return _N(f'data = {{"a": [{w}, {{"b": {v}}}]}}\ndata["a"][0]', w, 'data["a"][0] is the first item of the list: the plain number.')


@_ne
def n_users(rng):
    ws = words(rng, 4)
    code = f'data = {{"users": [{{"name": "{ws[0]}", "tags": ["{ws[1]}", "{ws[2]}"]}}]}}\ndata["users"][0]["tags"][1]'
    return _N(code, ws[2], 'users is a list, [0] a dict, ["tags"] a list, [1] its second item.')


@_ne
def n_get_chain_missing(rng):
    k = rng.choice(WORDS)
    return _N(f'd = {{"{k}": {{"y": 1}}}}\nd.get("zzz", {{}}).get("y", 0)', 0, "The first get gives {} for the missing key; the second then gives its default.")


@_ne
def n_get_chain_present(rng):
    k = rng.choice(WORDS)
    v = _v(rng)
    return _N(f'd = {{"{k}": {{"y": {v}}}}}\nd.get("{k}", {{}}).get("y", 0)', v, "Both gets find their key, so the defaults are never used.")


@_ne
def n_keyerror_inner(rng):
    k1, k2, k3 = rng.sample(WORDS, 3)
    return _N(f'd = {{"{k1}": {{"{k2}": {_v(rng)}}}}}\nd["{k1}"]["{k3}"]', "KeyError", "The inner dict has no such key.", True)


@_ne
def n_keyerror_outer(rng):
    k1, k2, k3 = rng.sample(WORDS, 3)
    return _N(f'd = {{"{k1}": {{"{k2}": {_v(rng)}}}}}\nd["{k3}"]["{k2}"]', "KeyError", "The outer lookup fails first.", True)


@_ne
def n_indexerror_outer(rng):
    g = _grid(rng)
    return _N(f"grid = {lit(g)}\ngrid[{len(g) + 1}][0]", "IndexError", "There is no row that far down.", True)


@_ne
def n_indexerror_inner(rng):
    g = _grid(rng)
    return _N(f"grid = {lit(g)}\ngrid[0][{len(g[0])}]", "IndexError", "The row has no item at that position (indexes stop at length - 1).", True)


@_ne
def n_typeerror_int(rng):
    k = rng.choice(WORDS)
    return _N(f'd = {{"{k}": {_v(rng)}}}\nd["{k}"][0]', "TypeError", "d[key] is a number, and a number cannot be indexed.", True)


@_ne
def n_typeerror_list_key(rng):
    k = rng.choice(WORDS)
    return _N(f'd = {{"{k}": {lit(nums(rng, 2, 3))}}}\nd["{k}"]["x"]', "TypeError", "A list is indexed by whole numbers, not text.", True)


@_ne
def n_keyerror_list_as_dict(rng):
    k = rng.choice(WORDS)
    return _N(f'd = {{"{k}": {{"x": 1}}}}\nd["{k}"][0]', "KeyError", "It is a dict, so 0 is looked up as a key - and there is no key 0.", True)


@_ne
def n_append_inner(rng):
    k = rng.choice(WORDS)
    xs, v = nums(rng, 2, 3), _v(rng)
    return _N(f'd = {{"{k}": {lit(xs)}}}\nd["{k}"].append({v})\nd["{k}"]', py_show(xs + [v]), "d[key] is the list itself, so append changes it in place.")


@_ne
def n_inc(rng):
    v = _v(rng)
    return _N(f'data = {{"a": [0, {{"b": {v}}}]}}\ndata["a"][1]["b"] += 1\ndata["a"][1]["b"]', v + 1, "+= reads the inner value, adds one and stores it back there.")


@_ne
def n_tuple_in_dict(rng):
    k = rng.choice(WORDS)
    a, b = ints(rng, 2, 1, 9)
    return _N(f'd = {{"{k}": ({a}, {b})}}\nd["{k}"][1]', b, "d[key] is a tuple; [1] is its second item.")


@_ne
def n_tuple_list(rng):
    a, b = ints(rng, 2, 1, 9)
    return _N(f"t = ({a}, [{b}, {a}])\nt[1][0]", b, "t[1] is the list; [0] is its first item.")


@_ne
def n_tuple_append(rng):
    a, b = ints(rng, 2, 1, 9)
    return _N(f"t = ({a}, [{b}])\nt[1].append(9)\nt", py_show((a, [b, 9])), "The tuple cannot change, but the list inside it can.")


@_ne
def n_len_inner(rng):
    k = rng.choice(WORDS)
    xs = nums(rng, 3, 5)
    return _N(f'd = {{"{k}": {lit(xs)}}}\nlen(d["{k}"])', len(xs), "d[key] is the list; len counts its items.")


@_ne
def n_str_in_list(rng):
    ws = words(rng, 3)
    i = rng.randrange(3)
    return _N(f"{lit(ws)}[{i}][0]", ws[i][0], "The list item is a word; [0] is its first letter.")


@_ne
def n_str_in_list_last(rng):
    ws = words(rng, 3)
    return _N(f"{lit(ws)}[-1][-1]", ws[2][len(ws[2]) - 1], "The last word, then its last letter.")


@_ne
def n_split_split(rng):
    ws = words(rng, 4)
    return _N(f'"{ws[0]} {ws[1]},{ws[2]} {ws[3]}".split(",")[1].split()[0]', ws[2], "Split at the comma, take the second piece, split that at the space, take the first.")


@_ne
def n_sum_inner(rng):
    k = rng.choice(WORDS)
    xs = nums(rng, 3, 4)
    return _N(f'd = {{"{k}": {lit(xs)}}}\nsum(d["{k}"])', total(xs), "d[key] is the list, and sum adds it.")


@_ne
def n_keys_inner(rng):
    k1, k2, k3 = rng.sample(WORDS, 3)
    return _N(f'd = {{"{k1}": {{"{k2}": 1, "{k3}": 2}}}}\nlist(d["{k1}"])[1]', k3, "list() of the inner dict gives its keys, in insertion order.")


@_ne
def n_in_inner(rng):
    k1, k2 = rng.sample(WORDS, 2)
    code, ans, why = rng.choice([(f'd = {{"{k1}": {{"{k2}": 1}}}}\n"{k2}" in d["{k1}"]', "True", "d[key] is the inner dict, and the key is in it."),
                                 (f'd = {{"{k1}": {{"{k2}": 1}}}}\n"{k2}" in d', "False", "The outer dict only has the key " + k1 + ".")])
    return _N(code, ans, why)


@_ne
def n_update_inner(rng):
    k1, k2, k3 = rng.sample(WORDS, 3)
    return _N(f'd = {{"{k1}": {{"{k2}": 1}}}}\nd["{k1}"]["{k3}"] = 2\nlen(d["{k1}"])', 2, "Assigning a new key into the inner dict makes it one bigger.")


@_ne
def n_pairs_index(rng):
    ws, vs = words(rng, 2), ints(rng, 2, 1, 9)
    return _N(f'pairs = [("{ws[0]}", {vs[0]}), ("{ws[1]}", {vs[1]})]\npairs[1][0]', ws[1], "pairs[1] is a tuple; [0] is its first part.")


@_ne
def n_dict_from_pairs(rng):
    ws, vs = words(rng, 2), ints(rng, 2, 1, 9)
    return _N(f'pairs = [("{ws[0]}", {vs[0]}), ("{ws[1]}", {vs[1]})]\ndict(pairs)["{ws[1]}"]', vs[1], "dict() turns each pair into a key and a value.")


@_ne
def n_pop_inner(rng):
    k = rng.choice(WORDS)
    xs = nums(rng, 3, 4)
    return _N(f'd = {{"{k}": {lit(xs)}}}\nd["{k}"].pop()\nd["{k}"]', py_show(take(xs, 0, len(xs) - 1)), "pop removes the last item from the list inside.")


@_ne
def n_in_nested_list(rng):
    a, b, c = ints(rng, 3, 1, 9)
    code, ans, why = rng.choice([(f"[{a}, {b}] in [[{c}], [{a}, {b}]]", "True", "in compares whole items: [a, b] is one of the inner lists."),
                                 (f"{a} in [[{c}], [{a}, {b}]]", "False", "The items are lists, and a bare number is not one of them.")])
    return _N(code, ans, why)


@_ne
def n_index_inner(rng):
    a, b, c, d = ints(rng, 4, 1, 9)
    return _N(f"[[{a}, {b}], [{c}, {d}]].index([{c}, {d}])", 1, "index finds the position of the equal inner list.")


# ── 8. Sort Order ───────────────────────────────────────────────────────

SORTS: list[Maker] = []


def _so(fn: Maker) -> Maker:
    SORTS.append(fn)
    return fn


def _S2(code: str, ans, why: str, err: bool = False) -> Item:
    return Item(code, str(ans), why, check=err_py(code) if err else "")


def _lower(w: str) -> str:
    return "".join(chr(ord(c) + 32) if "A" <= c <= "Z" else c for c in w)


def _cap(w: str) -> str:
    return (chr(ord(w[0]) - 32) if "a" <= w[0] <= "z" else w[0]) + w[1:]


def _numstrs(rng: random.Random) -> list[str]:
    return rng.choice([["10", "9", "100"], ["8", "75", "100", "9"], ["20", "3", "100"], ["15", "5", "150", "25"], ["7", "70", "17"]])


@_so
def so_first(rng):
    xs = nums(rng, 4, 6)
    return _S2(f"sorted({lit(xs)})[0]", sort_by(xs)[0], "sorted puts the smallest first.")


@_so
def so_desc_first(rng):
    xs = nums(rng, 4, 6)
    return _S2(f"sorted({lit(xs)}, reverse=True)[0]", sort_by(xs, reverse=True)[0], "reverse=True puts the biggest first.")


@_so
def so_last(rng):
    xs = nums(rng, 4, 6)
    return _S2(f"sorted({lit(xs)})[-1]", sort_by(xs)[len(xs) - 1], "The last of an ascending list is the biggest.")


@_so
def so_second(rng):
    xs = nums(rng, 4, 6)
    return _S2(f"sorted({lit(xs)})[1]", sort_by(xs)[1], "Index 1 is the second smallest.")


@_so
def so_inplace_first(rng):
    xs = nums(rng, 4, 6)
    return _S2(f"xs = {lit(xs)}\nxs.sort()\nxs[0]", sort_by(xs)[0], "sort() reorders xs itself, smallest first.")


@_so
def so_inplace_last(rng):
    xs = nums(rng, 4, 6)
    return _S2(f"xs = {lit(xs)}\nxs.sort()\nxs[-1]", sort_by(xs)[len(xs) - 1], "After sort() the biggest is last.")


@_so
def so_inplace_desc(rng):
    xs = nums(rng, 4, 6)
    return _S2(f"xs = {lit(xs)}\nxs.sort(reverse=True)\nxs", py_show(sort_by(xs, reverse=True)), "reverse=True sorts biggest first.")


@_so
def so_sorted_keeps(rng):
    xs = nums(rng, 4, 6)
    return _S2(f"xs = {lit(xs)}\nsorted(xs)\nxs[0]", xs[0], "sorted() made a new list and dropped it; xs is still in its old order.")


@_so
def so_sort_none(rng):
    xs = nums(rng, 3, 4)
    code, ans, why = rng.choice([(f"{lit(xs)}.sort()", "None", "sort() works in place and returns None."),
                                 (f"xs = {lit(xs)}\nxs = xs.sort()\nxs", "None", "xs.sort() gives None, and the assignment stores that None.")])
    return _S2(code, ans, why)


@_so
def so_words_first(rng):
    ws = words(rng, 4)
    return _S2(f"sorted({lit(ws)})[0]", sort_by(ws)[0], "Words sort like a dictionary: a before b.")


@_so
def so_words_last(rng):
    ws = words(rng, 4)
    return _S2(f"sorted({lit(ws)})[-1]", sort_by(ws)[3], "The last word alphabetically.")


@_so
def so_words_rev(rng):
    ws = words(rng, 4)
    return _S2(f"sorted({lit(ws)}, reverse=True)[0]", sort_by(ws, reverse=True)[0], "Backwards alphabet: the latest word first.")


@_so
def so_len_first(rng):
    ws = words(rng, 4)
    return _S2(f"sorted({lit(ws)}, key=len)[0]", sort_by(ws, key=len)[0], "key=len sorts by length; equal lengths keep their original order.")


@_so
def so_len_last(rng):
    ws = words(rng, 4)
    return _S2(f"sorted({lit(ws)}, key=len)[-1]", sort_by(ws, key=len)[3], "The longest comes last, and ties stay in the order they came.")


@_so
def so_len_rev(rng):
    ws = words(rng, 4)
    return _S2(f"sorted({lit(ws)}, key=len, reverse=True)[0]", sort_by(ws, key=len, reverse=True)[0],
               "Longest first; among equal lengths reverse=True still keeps the original order.")


@_so
def so_len_all(rng):
    ws = words(rng, 3)
    return _S2(f"sorted({lit(ws)}, key=len)", py_show(sort_by(ws, key=len)), "By length, shortest first; a tie keeps the original order.")


@_so
def so_numstr(rng):
    xs = _numstrs(rng)
    return _S2(f"sorted({lit(xs)})", py_show(sort_by(xs)), "Strings sort character by character, so '10' comes before '9'.")


@_so
def so_numstr_first(rng):
    xs = _numstrs(rng)
    return _S2(f"sorted({lit(xs)})[0]", sort_by(xs)[0], "As text, the first character decides: '1...' comes first.")


@_so
def so_numstr_last(rng):
    xs = _numstrs(rng)
    return _S2(f"sorted({lit(xs)})[-1]", sort_by(xs)[len(xs) - 1], "As text, '9' is bigger than '100'.")


@_so
def so_numstr_int(rng):
    xs = _numstrs(rng)
    return _S2(f"sorted({lit(xs)}, key=int)[0]", sort_by(xs, key=int)[0], "key=int sorts by the number each string holds; the string itself comes back.")


@_so
def so_num_key_str(rng):
    xs = rng.choice([[10, 9, 100], [8, 75, 100, 9], [20, 3, 100]])
    return _S2(f"sorted({lit(xs)}, key=str)", py_show(sort_by(xs, key=lambda n: str(n))), "key=str compares the numbers as text, so 100 comes before 9.")


@_so
def so_case(rng):
    a, b = rng.sample("abcdefg", 2)
    xs = [a, b.upper(), b]
    return _S2(f"sorted({lit(xs)})", py_show(sort_by(xs)), "Capital letters sort before every lower-case one.")


@_so
def so_case_words(rng):
    ws = words(rng, 3)
    i = rng.randrange(3)
    xs = [_cap(w) if k == i else w for k, w in enumerate(ws)]
    return _S2(f"sorted({lit(xs)})[0]", sort_by(xs)[0], "A word starting with a capital sorts before all the lower-case ones.")


@_so
def so_case_key(rng):
    a, b = rng.sample("abcdefg", 2)
    xs = [b, b.upper(), a]
    return _S2(f"sorted({lit(xs)}, key=str.lower)", py_show(sort_by(xs, key=_lower)), "key=str.lower ignores case; the equal pair keeps its original order.")


@_so
def so_chars(rng):
    w = rng.choice(["hello", "little", "banana", "carrot", "coffee", "pumpkin"])
    return _S2(f'sorted("{w}")', py_show(sort_by(list(w))), "A string sorts as its letters; repeats stay.")


@_so
def so_chars_join(rng):
    w = rng.choice(WORDS)
    return _S2(f'"".join(sorted("{w}"))', "".join(sort_by(list(w))), "Sort the letters, then glue them back into one string.")


@_so
def so_abs(rng):
    xs = _signed(rng, 4, 5)
    return _S2(f"sorted({lit(xs)}, key=abs)[0]", sort_by(xs, key=lambda x: x if x >= 0 else -x)[0], "key=abs sorts by distance from zero.")


@_so
def so_abs_last(rng):
    xs = _signed(rng, 4, 5)
    return _S2(f"sorted({lit(xs)}, key=abs)[-1]", sort_by(xs, key=lambda x: x if x >= 0 else -x)[len(xs) - 1], "The item furthest from zero comes last.")


@_so
def so_neg_key(rng):
    xs = nums(rng, 4, 5)
    return _S2(f"sorted({lit(xs)}, key=lambda x: -x)[0]", sort_by(xs, key=lambda x: -x)[0], "Ranking by -x flips the order: the biggest first.")


@_so
def so_signed(rng):
    xs = _signed(rng, 4, 5)
    return _S2(f"sorted({lit(xs)})[0]", sort_by(xs)[0], "The most negative number is the smallest.")


@_so
def so_mod(rng):
    xs = nums(rng, 4, 5)
    return _S2(f"sorted({lit(xs)}, key=lambda x: x % 3)", py_show(sort_by(xs, key=lambda x: fmod(x, 3))), "Sorted by remainder; items with the same remainder keep their original order.")


@_so
def so_dict_keys(rng):
    d = pairs(rng, 4)
    return _S2(f"d = {dlit(d)}\nsorted(d)[0]", sort_by([k for k, _ in d])[0], "sorted of a dict sorts its keys.")


@_so
def so_dict_value(rng):
    d = pairs(rng, 4)
    return _S2(f"d = {dlit(d)}\nsorted(d, key=d.get)[0]", sort_by(d, key=lambda p: p[1])[0][0], "key=d.get sorts the keys by their values: smallest value first.")


@_so
def so_dict_value_rev(rng):
    d = pairs(rng, 4)
    return _S2(f"d = {dlit(d)}\nsorted(d, key=d.get, reverse=True)[0]", sort_by(d, key=lambda p: p[1], reverse=True)[0][0], "Biggest value first.")


@_so
def so_items(rng):
    d = pairs(rng, 3)
    return _S2(f"d = {dlit(d)}\nsorted(d.items())[0]", py_show(sort_by(d)[0]), "Pairs sort by key first, then by value on a tie.")


@_so
def so_items_key(rng):
    d = pairs(rng, 3)
    return _S2(f"d = {dlit(d)}\nsorted(d.items(), key=lambda p: p[1])[-1]", py_show(sort_by(d, key=lambda p: p[1])[2]), "Sorted by value: the last pair has the biggest value.")


@_so
def so_tuples(rng):
    ps = []
    while len(ps) < 3:
        p = (rng.randint(1, 3), rng.choice("abxyz"))
        if not has(ps, p):
            ps.append(p)
    shown = "[" + ", ".join(f'({a}, "{b}")' for a, b in ps) + "]"
    return _S2(f"sorted({shown})", py_show(sort_by(ps)), "Tuples sort by the first item, then the second to break a tie.")


@_so
def so_tuples_key(rng):
    ps = [(rng.randint(1, 3), rng.choice("abxyz")) for _ in range(3)]
    shown = "[" + ", ".join(f'({a}, "{b}")' for a, b in ps) + "]"
    return _S2(f"sorted({shown}, key=lambda p: p[1])[0]", py_show(sort_by(ps, key=lambda p: p[1])[0]), "Sorted by the letter only; equal letters keep their order.")


@_so
def so_stable_pairs(rng):
    ps = [(1, "b"), (0, "z"), (1, "a")]
    ps = [ps[i] for i in rng.sample(range(3), 3)]
    shown = "[" + ", ".join(f'({a}, "{b}")' for a, b in ps) + "]"
    return _S2(f"sorted({shown}, key=lambda p: p[0])", py_show(sort_by(ps, key=lambda p: p[0])), "Only the first item counts, so equal ones stay in the order they came.")


@_so
def so_lists_lex(rng):
    xs = [[2, 1], [1, 5], [1, 2]]
    xs = [xs[i] for i in rng.sample(range(3), 3)]
    return _S2(f"sorted({lit(xs)})", py_show(sort_by(xs)), "Lists compare item by item, like tuples.")


@_so
def so_is_sorted(rng):
    xs = nums(rng, 3, 5)
    if rng.random() < 0.5:
        xs = sort_by(xs)
    return _S2(f"xs = {lit(xs)}\nsorted(xs) == xs", pyb(sort_by(xs) == xs), "True only if the list was already in order.")


@_so
def so_median(rng):
    xs = ints(rng, rng.choice([5, 7]), 1, 9)
    return _S2(f"sorted({lit(xs)})[len({lit(xs)}) // 2]", sort_by(xs)[len(xs) // 2], "The middle of the sorted list.")


@_so
def so_distinct_second(rng):
    xs = dupes(rng)
    u = sort_by(uniq(xs))
    return _S2(f"sorted(set({lit(xs)}))[-2]", u[len(u) - 2], "set drops the repeats first; then the second from the end.")


@_so
def so_top2(rng):
    xs = nums(rng, 4, 6)
    return _S2(f"sorted({lit(xs)}, reverse=True)[:2]", py_show(take(sort_by(xs, reverse=True), 0, 2)), "Biggest first, and [:2] keeps the first two.")


@_so
def so_bottom3(rng):
    xs = nums(rng, 4, 6)
    return _S2(f"sorted({lit(xs)})[:3]", py_show(take(sort_by(xs), 0, 3)), "The three smallest, in order.")


@_so
def so_alnum(rng):
    xs = rng.choice([["a1", "a10", "a2"], ["f9", "f10", "f1"], ["x20", "x3", "x100"]])
    return _S2(f"sorted({lit(xs)})", py_show(sort_by(xs)), "Compared as text: '1' comes before '2', so 'a10' sits before 'a2'.")


@_so
def so_bools(rng):
    return _S2("sorted([True, False, True])", py_show([False, True, True]), "False counts as 0 and True as 1.")


@_so
def so_last_letter(rng):
    ws = words(rng, 4)
    return _S2(f"sorted({lit(ws)}, key=lambda s: s[-1])[0]", sort_by(ws, key=lambda s: s[len(s) - 1])[0], "Sorted by each word's last letter.")


@_so
def so_len_then_alpha(rng):
    ws = words(rng, 4)
    return _S2(f"sorted({lit(ws)}, key=lambda w: (len(w), w))[0]", sort_by(ws, key=lambda w: (len(w), w))[0], "A tuple key sorts by length first, then alphabetically to break ties.")


@_so
def so_reversed(rng):
    xs = nums(rng, 4, 5)
    return _S2(f"list(reversed(sorted({lit(xs)})))[0]", sort_by(xs)[len(xs) - 1], "Sort ascending, then reverse: the biggest is first.")


@_so
def so_mixed_error(rng):
    return _S2(f'sorted([{_v(rng)}, "{rng.choice(WORDS)}", {_v(rng)}])', "TypeError", "Numbers and strings cannot be compared, so sorted fails.", True)


@_so
def so_none_error(rng):
    return _S2(f"sorted([{_v(rng)}, None, {_v(rng)}])", "TypeError", "None cannot be compared with a number.", True)


@_so
def so_min_vs(rng):
    xs = nums(rng, 4, 5)
    return _S2(f"xs = {lit(xs)}\nmin(xs) == sorted(xs)[0]", "True", "The smallest item is always the first of the sorted list.")
