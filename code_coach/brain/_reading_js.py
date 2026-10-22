"""Reading Pack, JavaScript side: the same eight activities with JavaScript's rules.

Every answer is modelled by hand (index arithmetic, slice positions, the
truncating %, the rounding rules, a typeof table) and tests/test_brain_packs.py
runs every template through the real node.
"""

from __future__ import annotations

import random
from string import Template
from typing import Callable

from ._model import (WORDS, Maker, decimal_div, fdiv, ints, ipow, isort, js_show, js_slice, js_substring,
                     lit, params, raises_js, reverse, row, tdiv, tmod, upper, yes_no_js)
from .items import Item


def _word(rng: random.Random, lo: int = 4) -> str:
    return rng.choice([w for w in WORDS if len(w) >= lo])


def _nums(rng: random.Random, lo: int = 4, hi: int = 6) -> list[int]:
    return ints(rng, rng.randint(lo, hi))


def _at(seq, i: int):
    return seq[i if i >= 0 else len(seq) + i]


def _find(seq, v) -> int:
    for i in range(len(seq)):
        if seq[i] == v:
            return i
    return -1


# ── 1. Index It ─────────────────────────────────────────────────────────

ZERO = "Counting starts at 0, so [0] is the first item."
OFF = "Out of range is not an error in JavaScript: you just get undefined."


def i_list(rng):
    xs = _nums(rng)
    i = rng.randrange(len(xs))
    return Item(f"{lit(xs)}[{i}]", str(xs[i]), ZERO)


def i_str(rng):
    w = _word(rng)
    i = rng.randrange(len(w))
    return Item(f'"{w}"[{i}]', w[i], "A string counts its characters from 0 too.")


def i_at_last(rng):
    xs = _nums(rng)
    return Item(f"{lit(xs)}.at(-1)", str(xs[-1]), ".at(-1) is the last item.")


def i_at_neg(rng):
    xs = _nums(rng)
    k = rng.randint(2, len(xs))
    return Item(f"{lit(xs)}.at(-{k})", str(_at(xs, -k)), f".at(-{k}) counts {k} from the end.")


def i_str_at(rng):
    w = _word(rng)
    k = rng.randint(1, 3)
    return Item(f'"{w}".at(-{k})', _at(w, -k), "Strings have .at() too: negatives count from the end.")


def i_len_minus(rng):
    xs = _nums(rng)
    k = rng.randint(1, 3)
    return Item(f"const nums = {lit(xs)};\nnums[nums.length - {k}]", str(xs[len(xs) - k]),
                f"length is {len(xs)}, so the index is {len(xs) - k}.")


def i_past(rng):
    xs = _nums(rng, 3, 4)
    return Item(f"{lit(xs)}[{len(xs) + rng.randint(0, 3)}]", "undefined", OFF)


def i_str_past(rng):
    w = _word(rng)
    return Item(f'"{w}"[{len(w) + rng.randint(0, 3)}]', "undefined", OFF)


def i_negidx(rng):
    xs = _nums(rng)
    return Item(f"{lit(xs)}[-1]", "undefined", "[-1] is not the last item in JavaScript: there is no such index. Use .at(-1).")


def i_str_negidx(rng):
    w = _word(rng)
    return Item(f'"{w}"[-1]', "undefined", "No negative indexes with [] - use .at(-1).")


def i_ends(rng):
    xs = _nums(rng)
    return Item(f"const nums = {lit(xs)};\nnums[0] + nums[nums.length - 1]", str(xs[0] + xs[-1]), "The first plus the last.")


def i_grid(rng):
    grid = [ints(rng, 3) for _ in range(rng.randint(2, 3))]
    r, c = rng.randrange(len(grid)), rng.randrange(3)
    return Item(f"const grid = {lit(grid)};\ngrid[{r}][{c}]", str(grid[r][c]), "The first [] picks the row, the second the item.")


def i_grid_at(rng):
    grid = [ints(rng, 3) for _ in range(rng.randint(2, 3))]
    return Item(f"const grid = {lit(grid)};\ngrid.at(-1)[0]", str(grid[-1][0]), "grid.at(-1) is the last row.")


def i_split(rng):
    ws = rng.sample(WORDS, 3)
    i = rng.randrange(3)
    return Item(f'"{",".join(ws)}".split(",")[{i}]', ws[i], "split gives an array of the pieces; then index it.")


def _obj(rng):
    ks = rng.sample(WORDS, 3)
    vs = ints(rng, 3)
    return ks, vs, "const o = { " + ", ".join(f"{k}: {v}" for k, v in zip(ks, vs)) + " };"


def i_prop(rng):
    ks, vs, decl = _obj(rng)
    k = rng.randrange(3)
    return Item(f"{decl}\no.{ks[k]}", str(vs[k]), "An object is looked up by name, not by position.")


def i_prop_str(rng):
    ks, vs, decl = _obj(rng)
    k = rng.randrange(3)
    return Item(f'{decl}\no["{ks[k]}"]', str(vs[k]), "Square brackets with a string work like a dot.")


def i_prop_missing(rng):
    ks, vs, decl = _obj(rng)
    return Item(f"{decl}\no.missing", "undefined", "A property that is not there is undefined, not an error.")


def i_indexof(rng):
    xs = _nums(rng, 5, 6)
    v = rng.choice(xs)
    return Item(f"{lit(xs)}.indexOf({v})", str(_find(xs, v)), ".indexOf gives the position of the first match.")


def i_indexof_missing(rng):
    xs = _nums(rng, 4, 6)
    return Item(f"{lit(xs)}.indexOf(0)", "-1", ".indexOf gives -1 when nothing matches.")


def i_str_indexof(rng):
    w = _word(rng)
    ch = rng.choice(w)
    return Item(f'"{w}".indexOf("{ch}")', str(_find(w, ch)), "The position of the first match, from 0.")


def i_after(rng):
    xs = _nums(rng, 5, 6)
    k = rng.randrange(len(xs) - 1)
    return Item(f"const nums = {lit(xs)};\nnums[nums.indexOf({xs[k]}) + 1]", str(xs[k + 1]), "The item just after that value.")


def i_rev(rng):
    xs = _nums(rng)
    i = rng.randrange(len(xs))
    return Item(f"[...{lit(xs)}].reverse()[{i}]", str(reverse(xs)[i]), "Reverse a copy, then index it.")


def i_ends_at(rng):
    xs = _nums(rng)
    return Item(f"const nums = {lit(xs)};\nnums.at(-1) - nums.at(0)", str(xs[-1] - xs[0]), "The last minus the first.")


def i_digit(rng):
    num = rng.randint(1000, 9999)
    i = rng.randrange(4)
    return Item(f"String({num})[{i}]", str(num)[i], "String() makes it text, so each digit is a character.")


def i_keys(rng):
    ks, vs, decl = _obj(rng)
    i = rng.randrange(3)
    return Item(f"{decl}\nObject.keys(o)[{i}]", ks[i], "The keys come out in the order they were written.")


def i_values_at(rng):
    ks, vs, decl = _obj(rng)
    return Item(f"{decl}\nObject.values(o).at(-1)", str(vs[-1]), "The last value.")


def i_concat(rng):
    xs, ys = _nums(rng, 3, 3), _nums(rng, 3, 3)
    i = rng.randrange(6)
    return Item(f"{lit(xs)}.concat({lit(ys)})[{i}]", str((xs + ys)[i]), "concat joins the arrays first; then index.")


def i_expr(rng):
    xs = _nums(rng)
    k = rng.randint(2, len(xs))
    return Item(f"const nums = {lit(xs)};\nconst i = {k};\nnums[i - 1]", str(xs[k - 1]), f"i - 1 is {k - 1}.")


def i_charat(rng):
    w = _word(rng)
    i = rng.randrange(len(w))
    return Item(f'"{w}".charAt({i})', w[i], "charAt gives the character at that position.")


def i_by_value(rng):
    n = rng.randint(4, 6)
    xs = rng.sample(range(n), n)
    return Item(f"const xs = {lit(xs)};\nxs[xs[0]]", str(xs[xs[0]]), f"xs[0] is {xs[0]}, so it is xs[{xs[0]}].")


def i_from(rng):
    j = rng.randint(1, 4)
    m = rng.randint(2, 4)
    return Item(f"Array.from({{ length: 6 }}, (_, i) => i * {m})[{j}]", str(j * m), f"Item i is i * {m}.")


def i_findindex(rng):
    xs = _nums(rng, 5, 6)
    t = rng.randint(3, 6)
    hit = -1
    for i in range(len(xs)):
        if xs[i] > t:
            hit = i
            break
    return Item(f"{lit(xs)}.findIndex(x => x > {t})", str(hit), f"The position of the first item over {t}, or -1.")


def i_split_chars(rng):
    w = _word(rng)
    i = rng.randrange(len(w))
    return Item(f'"{w}".split("")[{i}]', w[i], 'split("") gives one item per letter.')


def i_spread(rng):
    xs = _nums(rng, 3, 4)
    v = rng.randint(1, 9)
    i = rng.randrange(len(xs) + 1)
    return Item(f"[...{lit(xs)}, {v}][{i}]", str((xs + [v])[i]), "The spread copies the items, then the last is added.")


def i_maxpos(rng):
    xs = _nums(rng, 5, 6)
    best = xs[0]
    for x in xs:
        if x > best:
            best = x
    return Item(f"const nums = {lit(xs)};\nnums.indexOf(Math.max(...nums))", str(_find(xs, best)), "Where the biggest one sits.")


def i_upper(rng):
    w = _word(rng)
    i = rng.randrange(len(w))
    return Item(f'"{w}".toUpperCase()[{i}]', upper(w)[i], "toUpperCase() first, then the index.")


INDEX = [i_list, i_str, i_at_last, i_at_neg, i_str_at, i_len_minus, i_past, i_str_past, i_negidx, i_str_negidx, i_ends,
         i_grid, i_grid_at, i_split, i_prop, i_prop_str, i_prop_missing, i_indexof, i_indexof_missing, i_str_indexof,
         i_after, i_rev, i_ends_at, i_digit, i_keys, i_values_at, i_concat, i_expr, i_charat, i_by_value, i_from,
         i_findindex, i_split_chars, i_spread, i_maxpos, i_upper]


# ── 2. Slice It ─────────────────────────────────────────────────────────

def _xs(rng, lo=6, hi=7):
    """A source list. Node prints an array of more than 6 items in grouped columns, so answers that are
    arrays must stay at 6 items or fewer: 7 source items at most (and every answer drops at least one)."""
    return ints(rng, rng.randint(lo, min(hi, 7)))


def s_ab(rng):
    xs = _xs(rng)
    a = rng.randint(0, 2)
    b = rng.randint(a + 2, len(xs) - 1)
    return Item(f"{lit(xs)}.slice({a}, {b})", js_show(js_slice(xs, a, b)), "slice(a, b) takes from a up to, not including, b.")


def s_from(rng):
    xs = _xs(rng)
    k = rng.randint(2, 4)
    return Item(f"{lit(xs)}.slice({k})", js_show(js_slice(xs, k)), f"slice({k}) is everything from index {k} on.")


def s_lastk(rng):
    xs = _xs(rng)
    k = rng.randint(2, 4)
    return Item(f"{lit(xs)}.slice(-{k})", js_show(js_slice(xs, -k)), f"slice(-{k}) is the last {k}.")


def s_dropk(rng):
    xs = _xs(rng)
    k = rng.randint(1, 3)
    return Item(f"{lit(xs)}.slice(0, -{k})", js_show(js_slice(xs, 0, -k)), f"A negative end drops the last {k}.")


def s_beyond(rng):
    xs = _xs(rng, 4, 6)
    return Item(f"{lit(xs)}.slice({len(xs) + 2})", "[]", "Slicing past the end is not an error: it is just empty.")


def s_same(rng):
    xs = _xs(rng, 4, 6)
    k = rng.randint(1, 3)
    return Item(f"{lit(xs)}.slice({k}, {k})", "[]", "Start and end are the same, so nothing is taken.")


def s_backwards(rng):
    xs = _xs(rng, 5, 6)
    a, b = rng.randint(3, 4), rng.randint(1, 2)
    return Item(f"{lit(xs)}.slice({a}, {b})", "[]", "slice never goes backwards: a start after the end gives nothing.")


def s_copy(rng):
    xs = _xs(rng, 3, 5)
    return Item(f"{lit(xs)}.slice()", js_show(xs), "slice() with nothing is a copy of the whole array.")


def s_clamp(rng):
    xs = _xs(rng, 5, 6)
    b = rng.randint(2, 3)
    return Item(f"{lit(xs)}.slice(-100, {b})", js_show(js_slice(xs, -100, b)), "A start before the beginning is clamped to 0.")


def s_clamp_hi(rng):
    xs = _xs(rng, 4, 6)
    return Item(f"{lit(xs)}.slice(0, 100)", js_show(xs), "An end past the length is clamped: you get everything.")


def s_pair(rng):
    xs = _xs(rng, 6, 8)
    return Item(f"{lit(xs)}.slice(-3, -1)", js_show(js_slice(xs, -3, -1)), "From 3rd-last up to, not including, the last.")


def s_trim(rng):
    xs = _xs(rng, 5, 7)
    return Item(f"{lit(xs)}.slice(1, -1)", js_show(js_slice(xs, 1, -1)), "Drops the first and the last.")


def s_str(rng):
    w = _word(rng, 5)
    a, b = rng.randint(0, 1), rng.randint(3, 4)
    return Item(f'"{w}".slice({a}, {b})', js_slice(w, a, b), "slice(a, b): from a up to, not including, b.")


def s_str_last(rng):
    w = _word(rng, 5)
    k = rng.randint(2, 3)
    return Item(f'"{w}".slice(-{k})', js_slice(w, -k), f"The last {k} letters.")


def s_str_trim(rng):
    w = _word(rng, 5)
    return Item(f'"{w}".slice(1, -1)', js_slice(w, 1, -1), "Drops the first and the last letter.")


def s_substring(rng):
    w = _word(rng, 5)
    a, b = rng.randint(0, 1), rng.randint(3, 4)
    return Item(f'"{w}".substring({a}, {b})', js_substring(w, a, b), "substring(a, b): from a up to, not including, b.")


def s_substring_swap(rng):
    w = _word(rng, 5)
    a, b = rng.randint(3, 4), rng.randint(0, 1)
    return Item(f'"{w}".substring({a}, {b})', js_substring(w, a, b), "substring swaps its arguments when the first is bigger.")


def s_substring_neg(rng):
    w = _word(rng, 5)
    b = rng.randint(2, 3)
    return Item(f'"{w}".substring(-2, {b})', js_substring(w, -2, b), "substring treats a negative as 0 (slice would count from the end).")


def s_slice_neg_pair(rng):
    w = _word(rng, 6)
    return Item(f'"{w}".slice(-3, -1)', js_slice(w, -3, -1), "Two letters, ending just before the last.")


def s_str_empty(rng):
    w = _word(rng, 5)
    return Item(f'JSON.stringify("{w}".slice(4, 2))', '""', "An empty slice is an empty string; JSON.stringify shows its quotes.")


def s_len(rng):
    xs = _xs(rng, 7, 9)
    a, b = rng.randint(0, 2), rng.randint(5, 7)
    return Item(f"{lit(xs)}.slice({a}, {b}).length", str(b - a), f"{b} - {a} items.")


def s_then_index(rng):
    xs = _xs(rng)
    a = rng.randint(1, 3)
    return Item(f"{lit(xs)}.slice({a})[0]", str(xs[a]), f"slice({a}) drops the first {a}; its first item is xs[{a}].")


def s_last_of(rng):
    xs = _xs(rng)
    k = rng.randint(2, 3)
    return Item(f"{lit(xs)}.slice(-{k})[0]", str(_at(xs, -k)), f"The last {k}, and the first of those.")


def s_rev_first(rng):
    xs = _xs(rng, 6, 8)
    k = rng.randint(2, 3)
    return Item(f"[...{lit(xs)}].reverse().slice(0, {k})", js_show(js_slice(reverse(xs), 0, k)),
                f"Reverse a copy, then the first {k}: the last {k}, backwards.")


def s_whole(rng):
    xs = _xs(rng, 4, 6)
    k = rng.randint(1, 3)
    return Item(f"{lit(xs)}.slice(0, {k}).concat({lit(xs)}.slice({k}))", js_show(xs), "The two halves join back into the whole.")


def s_rotate(rng):
    xs = _xs(rng, 5, 6)
    k = rng.randint(1, 3)
    return Item(f"const nums = {lit(xs)};\nnums.slice({k}).concat(nums.slice(0, {k}))",
                js_show(js_slice(xs, k) + js_slice(xs, 0, k)), "The front moves to the back: a rotation.")


def s_split(rng):
    ws = rng.sample(WORDS, 3)
    return Item(f'"{",".join(ws)}".split(",").slice(1)', js_show(ws[1:]), "Slicing the pieces drops the first.")


def s_half(rng):
    xs = ints(rng, rng.choice((6, 7, 8)))
    h = fdiv(len(xs), 2)
    return Item(f"const nums = {lit(xs)};\nnums.slice(0, Math.floor(nums.length / 2))", js_show(js_slice(xs, 0, h)), f"The first {h}.")


def s_half_hi(rng):
    xs = ints(rng, rng.choice((6, 7, 8)))
    h = fdiv(len(xs), 2)
    return Item(f"const nums = {lit(xs)};\nnums.slice(Math.floor(nums.length / 2))", js_show(js_slice(xs, h)), f"{len(xs)} / 2 rounded down is {h}: from there on.")


def s_letters(rng):
    w = _word(rng, 5)
    return Item(f'[..."{w}"].slice(1, 3)', js_show(list(js_slice(w, 1, 3))), "The spread makes an array of letters; slice takes two.")


def s_rev_word(rng):
    w = _word(rng)
    return Item(f'"{w}".split("").reverse().join("")', reverse(w), "Split into letters, reverse, join back.")


def s_every2(rng):
    xs = _xs(rng, 6, 8)
    return Item(f"{lit(xs)}.filter((_, i) => i % 2 === 0)", js_show([xs[i] for i in range(0, len(xs), 2)]), "Keeps the items at even positions: 0, 2, 4...")


def s_ends(rng):
    w = _word(rng, 5)
    return Item(f'"{w}".slice(0, 1) + "{w}".slice(-1)', w[0] + w[-1], "The first letter and the last.")


def s_sorted_low(rng):
    xs = _xs(rng, 5, 7)
    k = rng.randint(2, 3)
    return Item(f"[...{lit(xs)}].sort().slice(0, {k})", js_show(isort(xs)[:k]), f"Sort a copy, then the {k} smallest.")


def s_slice_slice(rng):
    xs = _xs(rng, 6, 8)
    return Item(f"{lit(xs)}.slice(1).slice(-2)", js_show(js_slice(js_slice(xs, 1), -2)), "Drop the first, then take the last two.")


SLICE = [s_ab, s_from, s_lastk, s_dropk, s_beyond, s_same, s_backwards, s_copy, s_clamp, s_clamp_hi, s_pair, s_trim,
         s_str, s_str_last, s_str_trim, s_substring, s_substring_swap, s_substring_neg, s_slice_neg_pair, s_str_empty,
         s_len, s_then_index, s_last_of, s_rev_first, s_whole, s_rotate, s_split, s_half, s_half_hi, s_letters,
         s_rev_word, s_every2, s_ends, s_sorted_low, s_slice_slice]


# ── 3. What Type ────────────────────────────────────────────────────────

def _t(expr: str, answer, why: str = "") -> Maker:
    return row(f"typeof {expr}", answer, why)


TYPE = [
    _t("$a", "number", "Every number, whole or not, is a number."),
    _t('"$w"', "string", "Text in quotes is a string."),
    _t("true", "boolean", "true is a boolean."),
    _t("undefined", "undefined", "undefined is its own type."),
    _t("null", "object", "typeof null is \"object\": a famous old mistake in JavaScript itself."),
    _t("[$a]", "object", "Arrays are objects to typeof."),
    _t("{}", "object", "A plain object."),
    _t("(() => $a)", "function", "A function."),
    _t("Math.max", "function", "A method is a function."),
    _t("Math", "object", "Math is an object that holds functions."),
    _t("NaN", "number", "NaN means \"not a number\", but its type is number."),
    _t("Infinity", "number", "Infinity is a number."),
    _t('($a + "$w")', "string", "A string on either side of + makes a string."),
    _t("($a + $b)", "number", "Two numbers add: a number."),
    _t('("$a" * 2)', "number", "* only multiplies, so the string became a number."),
    _t('("$a" + 1)', "string", "+ with a string joins: a string."),
    _t("($a < $b)", "boolean", "A comparison gives a boolean."),
    _t("nothingHere", "undefined", "typeof on a name that does not exist is \"undefined\", not an error."),
    _t("typeof $a", "string", "typeof always gives a string - even for itself."),
    _t('Symbol("$w")', "symbol", "Symbols are their own type."),
    _t("${a}n", "bigint", "A number with n on the end is a BigInt."),
    _t("new Date()", "object", "A date is an object."),
    _t("/ab/", "object", "A regular expression is an object."),
    _t("[].length", "number", "length is a number."),
    _t('"$w".length', "number", "length is a number."),
    _t('"$w"[0]', "string", "One character is still a string."),
    _t('[$a, "$w"][1]', "string", "Look at the item you pick, not the array."),
    _t('Number("$a")', "number", "Number() gives a number."),
    _t("String($a)", "string", "String() gives text."),
    _t("Boolean($a)", "boolean", "Boolean() gives true or false."),
    _t('parseInt("$a")', "number", "parseInt gives a number."),
    _t("JSON.stringify({})", "string", "stringify gives text."),
    _t('JSON.parse("[1]")', "object", "parse gave back an array: an object."),
    _t("[].push", "function", "push is a function."),
    _t('!!"x"', "boolean", "! always gives a boolean."),
    _t("void 0", "undefined", "void gives undefined."),
    _t("new Number($a)", "object", "new Number makes an object, not a primitive number."),
    _t("class {}", "function", "A class is a function underneath."),
    _t("Array.isArray([])", "boolean", "isArray gives true or false."),
    _t("[$a, $b].map(x => x)", "object", "map gives a new array: an object."),
    _t('"$w".split("")', "object", "split gives an array."),
    _t("({}).toString()", "string", "toString gives text."),
    _t("Object.keys({})", "object", "keys gives an array."),
    _t("new Map()", "object", "A Map is an object."),
    _t("($a).toString()", "string", "toString gives text."),
    _t("($a).toFixed(1)", "string", "toFixed gives text, not a number."),
    _t("Math.round($a / 2)", "number", "round gives a number."),
    _t("[$b, $a].sort", "function", "sort is a function."),
    _t("(1 / 0)", "number", "Infinity is a number."),
    _t("(0 / 0)", "number", "NaN is a number."),
    _t("(null ?? $a)", "number", "?? skips null and gives the right side."),
    _t('(0 || "$w")', "string", "|| gives the first truthy value: the string."),
]


# ── 4. Equal or Not ─────────────────────────────────────────────────────

def _lexless(a: str, b: str) -> bool:
    for x, y in zip(a, b):
        if x != y:
            return x < y
    return len(a) < len(b)


def _q(fmt: str, truth, why: str = "") -> Maker:
    return row(fmt, lambda p: "yes" if (truth(p) if callable(truth) else truth) else "no", why, check=yes_no_js)


EQUAL = [
    _q('$a == "$a"', True, "== converts first, so the string becomes a number."),
    _q('$a === "$a"', False, "=== also compares types: a number is never a string."),
    _q('0 == ""', True, "Both become 0."),
    _q('0 == "0"', True, "The string becomes 0."),
    _q('"" == "0"', False, "Two strings: compared as text, and they differ."),
    _q("null == undefined", True, "== treats the two nothings as equal."),
    _q("null === undefined", False, "=== also compares types."),
    _q("null == 0", False, "null only equals undefined (and itself) with ==."),
    _q("undefined == 0", False, "undefined only equals null (and itself) with ==."),
    _q("NaN == NaN", False, "NaN is not equal to anything, itself included."),
    _q("Number.isNaN(NaN)", True, "isNaN is how you ask."),
    _q("[] == []", False, "Two separate arrays are never ==."),
    _q('[] == ""', True, "The empty array becomes the empty string."),
    _q("[] == false", True, "Both become 0."),
    _q("[$a] == $a", True, "[3] becomes the text '3', then the number 3."),
    _q('[$a, $b] == "$a,$b"', True, "The array becomes the text '3,5'."),
    _q('({}) == "[object Object]"', True, "An object becomes the text '[object Object]'."),
    _q('"b" > "a"', True, "Strings compare alphabetically."),
    _q('"10" < "9"', True, "As strings, '1' comes before '9'."),
    _q('10 < "9"', False, "With a number, the string becomes a number: 10 < 9."),
    _q("null >= 0", True, "null becomes 0 for >=, though null == 0 is false."),
    _q("null > 0", False, "null becomes 0 for >, and 0 > 0 is false."),
    _q("0.1 + 0.2 === 0.3", False, "Floats are binary: the sum is 0.30000000000000004."),
    _q("0.5 + 0.25 === 0.75", True, "These are exact in binary."),
    _q("true == 1", True, "true becomes 1."),
    _q('true == "1"', True, "Both become 1."),
    _q("true === 1", False, "=== also compares types."),
    _q('"true" == true', False, "true becomes 1, and the text 'true' becomes NaN."),
    _q('typeof null === "object"', True, "A famous quirk."),
    _q('typeof [] === "array"', False, "typeof says \"object\" for arrays."),
    _q("Array.isArray([])", True, "The right way to ask."),
    _q("[$a, $b].includes($a)", True, "includes looks for the value."),
    _q('[$a, $b].includes("$a")', False, "includes compares with ===: the string is not the number."),
    _q("const a = [$a];\nconst b = a;\na === b", True, "b is the same array as a."),
    _q("const a = [$a];\nconst b = [$a];\na === b", False, "Two separate arrays, equal contents or not."),
    _q("const a = [$a];\nconst b = [$a];\nJSON.stringify(a) === JSON.stringify(b)", True, "Compared as text, the contents match."),
    _q('"$a" - 2 === $a - 2', True, "- turns the string into a number."),
    _q('"$a" + 2 === $a + 2', False, "+ joins the string: '32' is not 5."),
    _q('+"$a" === $a', True, "The unary + makes a number."),
    _q('!!"0"', True, "A non-empty string is truthy."),
    _q("-0 === 0", True, "=== says negative zero is zero."),
    _q("Object.is(-0, 0)", False, "Object.is tells them apart."),
    _q("Object.is(NaN, NaN)", True, "Object.is says NaN is NaN."),
    _q("3 > 2 > 1", False, "(3 > 2) is true, then true > 1 is 1 > 1: false."),
    _q("1 < 2 < 3", True, "(1 < 2) is true, then true < 3 is 1 < 3."),
    _q("$a < $b < $c", True, "Not a chain: (a < b) is true or false (1 or 0), and either is smaller than c."),
    _q("[$b] > $a", lambda p: p["b"] > p["a"], "[b] becomes the number b."),
    _q('"abc".length === 3', True, "Three letters."),
    _q('"$w" < "$v"', lambda p: _lexless(p["w"], p["v"]), "Strings compare letter by letter."),
    _q("undefined === void 0", True, "void 0 is undefined."),
    _q('"5" == 5.0', True, "The string becomes 5."),
    _q("[1, 2, 3] + '' === '1,2,3'", True, "An array plus text becomes its items joined by commas."),
    _q("NaN !== NaN", True, "NaN is the one value not equal to itself."),
]


# ── 5. Mutate or Copy ───────────────────────────────────────────────────

def _m(setup: str, body: str, changed, why: str = "") -> Maker:
    """The oracle program snapshots `a` with JSON.stringify after the setup and compares after the body."""
    def make(rng: random.Random) -> Item:
        p = params(rng)
        s, b = Template(setup).substitute(p), Template(body).substitute(p)
        yes = changed(p) if callable(changed) else changed
        check = s + "\nconst _before = JSON.stringify(a);\n" + b + '\nJSON.stringify(a) === _before ? "no" : "yes"'
        return Item(s + "\n" + b, "yes" if yes else "no", Template(why).safe_substitute(p), check=check)
    make.__name__ = "mut_" + body[:20]
    return make


L2 = "let a = [$a, $b];"
L3 = "let a = [$a, $b, $c];"
O1 = "let a = { x: $a };"

MUTATE = [
    _m(L2, "const b = a;\nb.push($c);", True, "b is the same array as a, so the push shows in both."),
    _m(L2, "const b = [...a];\nb.push($c);", False, "The spread made a separate array."),
    _m(L2, "const b = a.slice();\nb.push($c);", False, "slice() with no arguments is a copy."),
    _m(L2, "const b = Array.from(a);\nb.push($c);", False, "Array.from builds a new array."),
    _m(L2, "const b = a.concat([$c]);", False, "concat builds a new array and leaves a alone."),
    _m(L2, "a.concat([$c]);", False, "The new array is thrown away, and a never changes."),
    _m(L2, "a = a.concat([$c]);", True, "a now names the longer array."),
    _m(L2, "a.push($c);", True, "push changes the array in place."),
    _m(L2, "a.pop();", True, "pop removes the last item."),
    _m(L2, "a.shift();", True, "shift removes the first item."),
    _m(L2, "a.unshift($c);", True, "unshift adds at the front."),
    _m(L3, "a.sort();", lambda p: isort([p["a"], p["b"], p["c"]]) != [p["a"], p["b"], p["c"]],
       "sort() works in place: it changes a unless it was already in order."),
    _m(L3, "a.reverse();", True, "reverse() works in place."),
    _m(L3, "[...a].reverse();", False, "It reverses a copy."),
    _m(L3, "a.map(x => x * 2);", False, "map returns a new array and does not touch a."),
    _m(L3, "a.forEach(x => { x *= 2; });", False, "x is a copy of each number."),
    _m(L3, "a.forEach((x, i) => { a[i] = x * 2; });", True, "a[i] assigns into the array."),
    _m(L2, "function add(xs) { xs.push($c); }\nadd(a);", True, "The function got the same array, not a copy."),
    _m(L2, "function add(xs) { xs = [...xs, $c]; }\nadd(a);", False, "The function made a new array; only its own xs changed."),
    _m(L2, "function add(xs) { xs = xs.concat($c); }\nadd(a);", False, "concat builds a new array."),
    _m(O1, "const b = a;\nb.y = $b;", True, "b is the same object as a."),
    _m(O1, "const b = { ...a };\nb.y = $b;", False, "The spread made a separate object."),
    _m(O1, "Object.assign({}, a, { y: $b });", False, "assign into a new empty object leaves a alone."),
    _m(O1, "Object.assign(a, { y: $b });", True, "assign copies into its first argument: a."),
    _m(O1, "delete a.x;", True, "delete removes the property."),
    _m("let a = [[$a], [$b]];", "const b = JSON.parse(JSON.stringify(a));\nb[0].push($c);", False, "A deep copy: the inner arrays are new too."),
    _m("let a = [[$a], [$b]];", "const b = [...a];\nb[0].push($c);", True, "The spread is shallow: the inner arrays are shared."),
    _m("const a = [$a, $b];", "a.push($c);", True, "const stops the name being reassigned, not the array changing."),
    _m(L2, "let b = a;\nb = [$c];", False, "b now names a different array; a is untouched."),
    _m(L2, "a.length = 0;", True, "Setting length to 0 empties the array."),
    _m(L3, "a.splice(1, 1);", True, "splice removes items in place."),
    _m(L3, "a.slice(1, 2);", False, "slice only copies."),
    _m(L3, "a.fill(0);", True, "fill overwrites every item."),
    _m('let a = "$w";', "a.toUpperCase();", False, "Strings cannot change; the new string is thrown away."),
    _m('let a = "$w";', 'let b = a;\nb += "!";', False, "Strings cannot change: b is a new string."),
    _m('let a = "$w";', "a = a.toUpperCase();", True, "a now names the upper-case string."),
    _m(L2, "a.indexOf($a);", False, "indexOf only looks."),
    _m(L2, "a.includes($a);", False, "includes only looks."),
    _m(L2, "a.push(...[$c, $d]);", True, "The spread feeds push two items."),
    _m(L2, "const b = a;\nb.length = 0;", True, "b is a: emptying it empties both."),
    _m(L2, "const b = a.map(x => x);\nb.push($c);", False, "map returns a new array."),
    _m(L2, "const [first] = a;", False, "Destructuring only reads."),
]


# ── 6. Error or Fine ────────────────────────────────────────────────────

def _e(code: str, why: str) -> Maker:
    return row(code, "error", why, check=raises_js)


def _f(code: str, why: str) -> Maker:
    return row(code, "fine", why, check=raises_js)


ERROR = [
    _e("const a = null;\na.length;", "TypeError: null has no properties."),
    _e("let a;\na.length;", "TypeError: undefined has no properties."),
    _e("const x = $a;\nx = $b;", "TypeError: a const cannot be assigned again."),
    _e("foo();", "ReferenceError: foo is not defined."),
    _e("let x = $a;\nx();", "TypeError: x is not a function."),
    _e("[].foo();", "TypeError: arrays have no foo method."),
    _e("({}).foo();", "TypeError: foo is not a function."),
    _e('JSON.parse("{bad");', "SyntaxError: that is not JSON."),
    _e('JSON.parse("");', "SyntaxError: empty text is not JSON."),
    _e("new Array(-1);", "RangeError: an array cannot have a negative length."),
    _e('"$w".repeat(-1);', "RangeError: repeat count must not be negative."),
    _e("(1).toFixed(101);", "RangeError: toFixed takes 0 to 100 digits."),
    _e("BigInt(1.5);", "RangeError: a fraction is not a BigInt."),
    _e("1n + 1;", "TypeError: BigInt and number do not mix."),
    _e("const o = {};\no.a.b;", "TypeError: o.a is undefined, so it has no b."),
    _e("const o = {};\no.a.b = $a;", "TypeError: o.a is undefined, so you cannot set its b."),
    _e("console.log(y);\nlet y = $a;", "ReferenceError: y is used before its let line runs."),
    _e("class A {}\nA();", "TypeError: a class needs new."),
    _e("[...$a];", "TypeError: a number is not iterable."),
    _e("const [a] = null;", "TypeError: null cannot be destructured."),
    _e("const { a } = undefined;", "TypeError: undefined cannot be destructured."),
    _e("for (const x of $a) {}", "TypeError: a number is not iterable."),
    _e("total = total + $a;", "ReferenceError: total was never declared."),
    _e("Object.keys(null);", "TypeError: null cannot be turned into an object."),
    _e("new Set($a);", "TypeError: a number is not iterable."),
    _e('new Date("x").toISOString();', "RangeError: an invalid date has no ISO string."),
    _e("[].reduce((s, x) => s + x);", "TypeError: reduce of nothing needs a starting value."),
    _e('decodeURIComponent("%");', "URIError: that is not valid encoding."),
    _e("($a).toUpperCase();", "TypeError: numbers have no toUpperCase."),
    _e('"$w".foo();', "TypeError: strings have no foo method."),
    _e("const o = {};\no.self = o;\nJSON.stringify(o);", "TypeError: a circular structure cannot be turned into JSON."),
    _e("JSON.stringify(1n);", "TypeError: a BigInt cannot be turned into JSON."),
    _e("null.toString();", "TypeError: null has no methods."),
    _e('Symbol() + "";', "TypeError: a symbol cannot become text this way."),
    _e("undefined.x;", "TypeError: undefined has no properties."),
    _e("const f = {};\nf.run();", "TypeError: f.run is not a function."),
    _e("x.y = $a;", "ReferenceError: x is not defined."),
    _f("1 / 0;", "JavaScript gives Infinity instead of an error."),
    _f("0 / 0;", "NaN, not an error."),
    _f("[$a, $b][5];", "Out of range gives undefined."),
    _f('"$w"[9];', "Out of range gives undefined."),
    _f("({}).missing;", "A missing property is undefined."),
    _f("const o = {};\no.a?.b;", "?. stops at undefined instead of failing."),
    _f("null?.x;", "?. stops at null."),
    _f("undefined ?? $a;", "?? gives the right side."),
    _f('parseInt("$w");', "parseInt gives NaN for text that is not a number."),
    _f('Number("$w");', "Number gives NaN."),
    _f("[].pop();", "pop on an empty array gives undefined."),
    _f("[].shift();", "shift on an empty array gives undefined."),
    _f('"$w" + $a;', "+ joins them."),
    _f('$a + "$w";', "+ joins them."),
    _f("null + $a;", "null counts as 0."),
    _f("undefined + $a;", "NaN, not an error."),
    _f("[] + {};", "Both become text and join."),
    _f("typeof nope;", "typeof is the one safe way to ask about a name that may not exist."),
    _f('"$w".slice(9);', "Past the end: an empty string."),
    _f("[$a].concat($b);", "concat adds the item."),
    _f('JSON.parse("[$a]");', "That is valid JSON."),
    _f("const x = $a;\nx.foo;", "A number has no foo, which is just undefined."),
    _f("let x;\nx;", "x is undefined: fine."),
    _f("const a = [];\na.push($a);", "const stops reassigning, not changing the array."),
    _f("Math.sqrt(-$a);", "NaN, not an error."),
    _f('"$a" * "$b";', "Both become numbers."),
    _f("new Array(3);", "Three empty slots."),
    _f("[...[$a, $b]];", "Spreading an array is fine."),
    _f("Object.keys({});", "An empty array."),
    _f('isNaN("$w");', "true, not an error."),
    _f('"$w".repeat(0);', "An empty string."),
    _f("($a).toFixed(2);", "Text with two decimals."),
    _f("JSON.stringify({});", 'The text "{}".'),
    _f("const a = null;\na?.[0];", "?. stops at null."),
    _f("[$a, $b, $c].at(-1);", ".at(-1) is the last."),
    _f('"$w".at(-1);', ".at(-1) is the last letter."),
    _f("[].reduce((s, x) => s + x, 0);", "With a starting value, nothing to add gives 0."),
    _f("Math.max();", "-Infinity, not an error."),
    _f("let a = [$a];\na.length = 0;", "Setting length is allowed."),
    _f("undefined === null;", "A comparison never throws."),
]


# ── 7. Return Value ─────────────────────────────────────────────────────

def _r(fmt: str, answer, why: str = "") -> Maker:
    return row(fmt, answer, why)


def _fact(n: int) -> int:
    out = 1
    for k in range(2, n + 1):
        out *= k
    return out


F2 = "function f(a, b) {\n  return [a + b, a * b];\n}\n"

RETURN = [
    _r("function f(x) {\n  return x * 2;\n}\nf($a)", lambda p: str(p["a"] * 2), "The call gives back x * 2."),
    _r("function f(x) {\n  x * 2;\n}\nf($a)", "undefined", "There is no return, so the call gives undefined."),
    _r("const f = x => x * 2;\nf($a)", lambda p: str(p["a"] * 2), "An arrow with no braces returns its expression."),
    _r("const f = x => { x * 2 };\nf($a)", "undefined", "With braces an arrow needs return."),
    _r("const f = x => ({ v: x });\nf($a)", lambda p: js_show({"v": p["a"]}), "Round brackets make the braces an object, not a body."),
    _r("const f = x => { v: x };\nf($a)", "undefined", "The braces are a body, and v: is just a label - nothing is returned."),
    _r("function f(a, b = 10) {\n  return a + b;\n}\nf($a)", lambda p: str(p["a"] + 10), "b falls back to its default, 10."),
    _r("function f(a, b = 10) {\n  return a + b;\n}\nf($a, $b)", lambda p: str(p["a"] + p["b"]), "A value passed in replaces the default."),
    _r("function f(a, b = 10) {\n  return a + b;\n}\nf($a, undefined)", lambda p: str(p["a"] + 10), "Passing undefined still uses the default."),
    _r("function f(a, b = 10) {\n  return a + b;\n}\nf($a, null)", lambda p: str(p["a"]), "null is a value, so there is no default: a + null is a + 0."),
    _r(F2 + "f($a, $b)", lambda p: js_show([p["a"] + p["b"], p["a"] * p["b"]]), "An array is how a function gives back two values."),
    _r(F2 + "const [s, p] = f($a, $b);\np", lambda p: str(p["a"] * p["b"]), "The array unpacks into s and p."),
    _r("function f(a, b) {\n  return a, b;\n}\nf($a, $b)", lambda p: str(p["b"]), "The comma operator gives the last value."),
    _r("function f(x) {\n  return\n    x * 2;\n}\nf($a)", "undefined", "A line break after return ends the statement: it returns nothing."),
    _r("function f() {\n  return arguments.length;\n}\nf($a, $b, $c)", "3", "arguments holds everything passed."),
    _r("const f = (...xs) => xs.length;\nf($a, $b)", "2", "...xs collects the arguments into an array."),
    _r("function make(n) {\n  return x => x + n;\n}\nmake($a)($b)", lambda p: str(p["a"] + p["b"]), "The inner function remembers n."),
    _r("function f(n) {\n  return n <= 1 ? 1 : n * f(n - 1);\n}\nf($a)", lambda p: str(_fact(p["a"])), "n * (n-1) * ... * 1."),
    _r("function f(xs) {\n  for (const x of xs) {\n    return x;\n  }\n}\nf([$a, $b])", lambda p: str(p["a"]),
       "The return runs on the first turn, so only the first item is seen."),
    _r("function f(xs) {\n  xs.forEach(x => {\n    if (x > 0) return x;\n  });\n}\nf([$a, $b])", "undefined",
       "That return leaves the callback, not f, so f returns nothing."),
    _r("function f(xs) {\n  return xs.map(x => x * 2);\n}\nf([$a, $b])", lambda p: js_show([p["a"] * 2, p["b"] * 2]), "A new array of doubles."),
    _r("function f(xs) {\n  return xs.filter(x => x > $c);\n}\nf([$a, $b, $d])",
       lambda p: js_show([x for x in (p["a"], p["b"], p["d"]) if x > p["c"]]), "Keeps the items over the limit."),
    _r("function f(xs) {\n  return xs.find(x => x > 20);\n}\nf([$a, $b])", "undefined", "find gives undefined when nothing matches."),
    _r("function f(xs) {\n  return xs.reduce((s, x) => s + x, 0);\n}\nf([$a, $b, $c])", lambda p: str(p["a"] + p["b"] + p["c"]), "reduce adds them up."),
    _r("function f(a, b) {\n  return b;\n}\nf($a)", "undefined", "No second argument was passed, so b is undefined."),
    _r("function f(a) {\n  a = a + 1;\n  return a;\n}\nlet n = $a;\nf(n);\nn", lambda p: str(p["a"]), "The function changed its own copy of the number."),
    _r("function f(a) {\n  a.push(1);\n  return a.length;\n}\nconst nums = [$a];\nf(nums);\nnums", lambda p: js_show([p["a"], 1]),
       "The function changed the very array it was given."),
    _r('function f(x) {\n  if (x) {\n    return "yes";\n  }\n}\nf(0)', "undefined", "0 is falsy, so the return is skipped."),
    _r('function f(x) {\n  if (x) {\n    return "yes";\n  }\n}\nf($a)', "yes", "$a is truthy, so it returns."),
    _r("const f = (a, b) => a > b ? a : b;\nf($a, $b)", lambda p: str(max(p["a"], p["b"])), "It gives back the bigger one."),
    _r("(() => $a * 2)()", lambda p: str(p["a"] * 2), "An arrow called straight away."),
    _r("function f(n = $a) {\n  return n * 2;\n}\nf()", lambda p: str(p["a"] * 2), "No argument: the default is used."),
    _r("function f(x) {\n  return typeof x;\n}\nf($a)", "number", "It returns the type name."),
    _r("function f() {\n  return;\n}\nf()", "undefined", "A bare return gives undefined."),
    _r('function f(xs) {\n  return xs.length > 0 ? xs[0] : "none";\n}\nf([])', "none", "The array is empty, so the second choice."),
    _r("function f(n) {\n  let t = 0;\n  for (let i = 0; i < n; i++) {\n    t += i;\n    return t;\n  }\n}\nf($a)", "0",
       "The return is inside the loop, so it stops after the first turn: t is 0."),
    _r("function f(a, b) {\n  return a ?? b;\n}\nf(null, $b)", lambda p: str(p["b"]), "?? takes the right side for null or undefined."),
    _r("function f(a, b) {\n  return a ?? b;\n}\nf(0, $b)", "0", "?? only skips null and undefined: 0 stays."),
    _r("function f(a, b) {\n  return a || b;\n}\nf(0, $b)", lambda p: str(p["b"]), "|| skips any falsy value, 0 included."),
    _r('function f(s) {\n  return s.length;\n}\nf("$w")', lambda p: str(len(p["w"])), "The number of letters."),
]


# ── 8. Number Crunch ────────────────────────────────────────────────────

def _n(fmt: str, answer: Callable[[dict], object], why: str = "") -> Maker:
    return row(fmt, lambda p: str(answer(p)), why)


def _n_div(rng: random.Random) -> Item:
    d = rng.choice((2, 4, 5, 8))
    n = rng.randint(10, 40)
    return Item(f"{n} / {d}", decimal_div(n, d), "/ is true division: the fraction is kept.")


def _bits(a: int, b: int, how: str) -> int:
    out, bit = 0, 1
    while a or b:
        x, y = a - 2 * fdiv(a, 2), b - 2 * fdiv(b, 2)
        if (how == "and" and x and y) or (how == "or" and (x or y)) or (how == "xor" and x != y):
            out += bit
        a, b, bit = fdiv(a, 2), fdiv(b, 2), bit * 2
    return out


def _base(n: int, base: int) -> str:
    digits = "0123456789abcdef"
    out = ""
    while n:
        out = digits[n - base * fdiv(n, base)] + out
        n = fdiv(n, base)
    return out


NUMBER = [
    _n_div,
    _n("$a * $b / $b", lambda p: p["a"], "It divides exactly; there is no separate whole-number type."),
    _n("$n % $a", lambda p: tmod(p["n"], p["a"]), "% is the remainder."),
    _n("-$n % $a", lambda p: "-0" if tmod(-p["n"], p["a"]) == 0 else tmod(-p["n"], p["a"]),
       "% takes the sign of the left side: the result is 0 or below (and -0 shows as -0)."),
    _n("$n % -$a", lambda p: tmod(p["n"], -p["a"]), "% takes the sign of the left side, so this one is not negative."),
    _n("Math.floor(-$n / $a)", lambda p: fdiv(-p["n"], p["a"]), "floor rounds toward minus infinity."),
    _n("Math.trunc(-$n / $a)", lambda p: tdiv(-p["n"], p["a"]), "trunc cuts the fraction off, toward zero."),
    _n("Math.floor($n / $a)", lambda p: fdiv(p["n"], p["a"]), "Divide, then round down."),
    _n("Math.ceil($n / $a)", lambda p: -fdiv(-p["n"], p["a"]), "ceil rounds up."),
    _n("Math.round($a.5)", lambda p: p["a"] + 1, "round sends an exact half up."),
    _n("Math.round(-$a.5)", lambda p: -p["a"], "Halves go up, toward plus infinity: -2.5 becomes -2."),
    _n("Math.round(-0.5)", lambda p: "-0", "The rounded half is minus zero, which prints as -0."),
    _n("Math.round($a / 2)", lambda p: fdiv(p["a"] + 1, 2), "An odd number over 2 is an exact half, and halves go up."),
    _n("2 ** $a", lambda p: ipow(2, p["a"]), "2 multiplied by itself $a times."),
    _n("2 ** -$k", lambda p: decimal_div(1, ipow(2, p["k"])), "A negative power is a fraction."),
    _n("(-$a) ** 3", lambda p: -ipow(p["a"], 3), "A negative number cubed stays negative."),
    _n("2 ** 3 ** 2", lambda p: 512, "** goes right to left: 2 ** 9."),
    _n("Math.pow($a, 2)", lambda p: p["a"] * p["a"], "a squared."),
    _n("Math.sqrt($a * $a)", lambda p: p["a"], "The square root of a square."),
    _n("Math.abs(-$a)", lambda p: p["a"], "abs drops the sign."),
    _n("Math.max($a, $b, $c)", lambda p: max(p["a"], p["b"], p["c"]), "The biggest."),
    _n("Math.min($a, $b, $c)", lambda p: min(p["a"], p["b"], p["c"]), "The smallest."),
    _n("Math.max()", lambda p: "-Infinity", "With nothing to compare, max is -Infinity."),
    _n("Math.min()", lambda p: "Infinity", "With nothing to compare, min is Infinity."),
    _n('parseInt("${n}px")', lambda p: p["n"], "parseInt reads the digits and stops at the first other character."),
    _n('parseInt("px$n")', lambda p: "NaN", "It starts with a letter, so there is no number."),
    _n('parseInt("$a.9")', lambda p: p["a"], "parseInt stops at the point: whole numbers only."),
    _n('parseFloat("$a.5abc")', lambda p: f"{p['a']}.5", "parseFloat reads the decimal, then stops at the letters."),
    _n('Number("$n")', lambda p: p["n"], "Number reads the whole text as a number."),
    _n('Number("")', lambda p: 0, "Empty text counts as 0."),
    _n('Number("${n}px")', lambda p: "NaN", "Number needs the whole text to be a number."),
    _n("Number(true)", lambda p: 1, "true is 1."),
    _n("Number(null)", lambda p: 0, "null is 0."),
    _n("Number(undefined)", lambda p: "NaN", "undefined is not a number."),
    _n('+"$a" + $b', lambda p: p["a"] + p["b"], "The unary + makes the string a number, so it adds."),
    _n('"$a" - $b', lambda p: p["a"] - p["b"], "- only subtracts: the string becomes a number."),
    _n('"$a" + $b', lambda p: f"{p['a']}{p['b']}", "+ with a string joins: the answer is text."),
    _n('"$a" * "$b"', lambda p: p["a"] * p["b"], "* only multiplies."),
    _n("0.1 + 0.2", lambda p: "0.30000000000000004", "Floats are binary: 0.1 + 0.2 is a hair over 0.3."),
    _n("0.1 * 3", lambda p: "0.30000000000000004", "The same famous float error."),
    _n("$a / 0", lambda p: "Infinity", "Dividing by zero gives Infinity."),
    _n("-$a / 0", lambda p: "-Infinity", "Dividing a negative by zero gives -Infinity."),
    _n("0 / 0", lambda p: "NaN", "Not a number."),
    _n("$a % 0", lambda p: "NaN", "A remainder by zero is NaN."),
    _n("$n / $a | 0", lambda p: tdiv(p["n"], p["a"]), "| 0 chops the fraction off."),
    _n("-$n / $a | 0", lambda p: tdiv(-p["n"], p["a"]), "| 0 truncates toward zero, so a negative goes up."),
    _n("~~$a.7", lambda p: p["a"], "~~ is a short way to truncate."),
    _n("$a & $b", lambda p: _bits(p["a"], p["b"], "and"), "A 1 only where both have a 1."),
    _n("$a | $b", lambda p: _bits(p["a"], p["b"], "or"), "A 1 where either has a 1."),
    _n("$a ^ $b", lambda p: _bits(p["a"], p["b"], "xor"), "A 1 where exactly one has a 1."),
    _n("1 << $a", lambda p: ipow(2, p["a"]), "Shifting left doubles each place."),
    _n("$n >> 1", lambda p: fdiv(p["n"], 2), "Shifting right halves, rounding down."),
    _n("(255).toString(16)", lambda p: "ff", "255 in base 16."),
    _n("($n).toString(2)", lambda p: _base(p["n"], 2), "The base 2 digits."),
    _n("(3.14159).toFixed(2)", lambda p: "3.14", "Two decimals, as text."),
    _n("(1234.5678).toFixed(1)", lambda p: "1234.6", "One decimal, rounded."),
    _n("($a).toFixed(2)", lambda p: f"{p['a']}.00", "toFixed pads with zeros."),
    _n("0xff", lambda p: 255, "0x starts a hexadecimal number."),
    _n("0b101", lambda p: 5, "0b starts a binary number."),
    _n('parseInt("ff", 16)', lambda p: 255, "Read as base 16."),
    _n('parseInt("101", 2)', lambda p: 5, "Read as base 2."),
    _n("[$a, $b, $c].reduce((s, x) => s + x)", lambda p: p["a"] + p["b"] + p["c"], "Adds them all."),
    _n('"abc".length + $a', lambda p: 3 + p["a"], "length is 3."),
    _n("$a - $b - $c", lambda p: p["a"] - p["b"] - p["c"], "Left to right."),
    _n("1 + $a * $b ** 2", lambda p: 1 + p["a"] * p["b"] ** 2, "** first, then *, then +."),
    _n("$n % $a * $b", lambda p: tmod(p["n"], p["a"]) * p["b"], "% and * share a level: left to right."),
]
