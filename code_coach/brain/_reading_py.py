"""Reading Pack, Python side, part 1: Index It, Slice It, What Type, Equal or Not.

Every answer is modelled by hand (index arithmetic, slice positions, a type
table, comparison rules) and tests/test_brain_packs.py runs every template
through the real interpreter.
"""

from __future__ import annotations

import random

from ._model import (WORDS, Maker, fdiv, fmod, find, ints, isort, lit, py_show, py_slice, reverse, row,
                     upper, yes_no_py)
from .items import Item


def _pos(n: int, i: int) -> int:
    """Where index i lands in a sequence of length n (negatives count from the end)."""
    return i if i >= 0 else n + i


def _at(seq, i: int):
    return seq[_pos(len(seq), i)]


def _word(rng: random.Random, lo: int = 4) -> str:
    return rng.choice([w for w in WORDS if len(w) >= lo])


def _nums(rng: random.Random, lo: int = 4, hi: int = 6) -> list[int]:
    return ints(rng, rng.randint(lo, hi))


# ── 1. Index It ─────────────────────────────────────────────────────────

ZERO = "Counting starts at 0, so [0] is the first item."
NEG = "A negative index counts from the end: -1 is the last."


def i_list(rng):
    xs = _nums(rng)
    i = rng.randrange(len(xs))
    return Item(f"{lit(xs)}[{i}]", str(xs[i]), ZERO)


def i_str(rng):
    w = _word(rng)
    i = rng.randrange(len(w))
    return Item(f'"{w}"[{i}]', w[i], "A string counts its characters from 0 too.")


def i_last(rng):
    xs = _nums(rng)
    return Item(f"{lit(xs)}[-1]", str(xs[-1]), NEG)


def i_neg(rng):
    xs = _nums(rng)
    k = rng.randint(2, len(xs))
    return Item(f"{lit(xs)}[-{k}]", str(_at(xs, -k)), f"-{k} is {k} from the end: the same as index {len(xs) - k}.")


def i_str_last(rng):
    w = _word(rng)
    return Item(f'"{w}"[-1]', w[-1], NEG)


def i_str_neg(rng):
    w = _word(rng)
    k = rng.randint(2, 4)
    return Item(f'"{w}"[-{k}]', _at(w, -k), f"-{k} counts {k} back from the end.")


def i_var(rng):
    xs = _nums(rng)
    i = rng.randrange(len(xs))
    return Item(f"nums = {lit(xs)}\nnums[{i}]", str(xs[i]), ZERO)


def i_len_minus(rng):
    xs = _nums(rng)
    k = rng.randint(1, 3)
    return Item(f"nums = {lit(xs)}\nnums[len(nums) - {k}]", str(xs[len(xs) - k]),
                f"len is {len(xs)}, so the index is {len(xs) - k}.")


def i_mid(rng):
    xs = ints(rng, rng.choice((5, 7, 9)))
    h = fdiv(len(xs), 2)
    return Item(f"nums = {lit(xs)}\nnums[len(nums) // 2]", str(xs[h]), f"{len(xs)} // 2 is {h}: the middle item.")


def i_ends(rng):
    xs = _nums(rng)
    return Item(f"nums = {lit(xs)}\nnums[0] + nums[-1]", str(xs[0] + xs[-1]), "The first plus the last.")


def i_prod(rng):
    xs = _nums(rng)
    i, j = rng.sample(range(len(xs)), 2)
    return Item(f"nums = {lit(xs)}\nnums[{i}] * nums[{j}]", str(xs[i] * xs[j]), "Look each one up, then multiply.")


def i_by_value(rng):
    n = rng.randint(4, 6)
    xs = rng.sample(range(n), n)
    return Item(f"xs = {lit(xs)}\nxs[xs[0]]", str(xs[xs[0]]), f"xs[0] is {xs[0]}, so it is xs[{xs[0]}].")


def i_grid(rng):
    grid = [ints(rng, 3) for _ in range(rng.randint(2, 3))]
    r, c = rng.randrange(len(grid)), rng.randrange(3)
    return Item(f"grid = {lit(grid)}\ngrid[{r}][{c}]", str(grid[r][c]), "The first [] picks the row, the second the item.")


def i_grid_neg(rng):
    grid = [ints(rng, 3) for _ in range(rng.randint(2, 3))]
    c = rng.choice((0, -1))
    return Item(f"grid = {lit(grid)}\ngrid[-1][{c}]", str(_at(grid[-1], c)), "grid[-1] is the last row.")


def i_grid_row(rng):
    grid = [ints(rng, 3) for _ in range(3)]
    r = rng.randrange(3)
    return Item(f"grid = {lit(grid)}\ngrid[{r}]", py_show(grid[r]), "One index gives a whole row.")


def i_tuple(rng):
    t = ints(rng, 3)
    i = rng.choice((0, 1, 2, -1, -2))
    return Item(f"t = ({', '.join(map(str, t))})\nt[{i}]", str(_at(t, i)), "Tuples index like lists.")


def i_split(rng):
    ws = rng.sample(WORDS, 3)
    i = rng.randrange(3)
    return Item(f'"{",".join(ws)}".split(",")[{i}]', ws[i], "split gives a list of the pieces; then index it.")


def i_split_ws(rng):
    ws = rng.sample(WORDS, 3)
    i = rng.choice((0, 1, 2, -1))
    return Item(f'"{" ".join(ws)}".split()[{i}]', _at(ws, i), "split() with nothing cuts at the spaces.")


def i_dict(rng):
    ks = rng.sample(WORDS, 3)
    vs = ints(rng, 3)
    k = rng.randrange(3)
    d = ", ".join(f'"{a}": {b}' for a, b in zip(ks, vs))
    return Item(f'd = {{{d}}}\nd["{ks[k]}"]', str(vs[k]), "A dict is looked up by key, not by position.")


def i_dict_list(rng):
    xs = _nums(rng, 3, 5)
    i = rng.choice((0, -1, 1))
    return Item(f'd = {{"xs": {lit(xs)}}}\nd["xs"][{i}]', str(_at(xs, i)), "d[\"xs\"] is the list; then index it.")


def i_range_list(rng):
    s = rng.randint(1, 5)
    e = s + rng.randint(4, 8)
    i = rng.randrange(e - s)
    return Item(f"list(range({s}, {e}))[{i}]", str(s + i), f"The list starts at {s} and counts up.")


def i_range(rng):
    st = rng.randint(2, 5)
    s = rng.randint(0, 5)
    i = rng.randint(1, 4)
    return Item(f"range({s}, {s + 40}, {st})[{i}]", str(s + i * st), f"Items go {s}, {s + st}, {s + 2 * st} ...")


def i_range_neg(rng):
    n = rng.randint(5, 12)
    return Item(f"range({n})[-1]", str(n - 1), "range(n) stops before n, so its last is n - 1.")


def i_list_index(rng):
    xs = _nums(rng, 5, 6)
    v = rng.choice(xs)
    return Item(f"{lit(xs)}.index({v})", str(find(xs, v)), ".index gives the position of the first match.")


def i_str_index(rng):
    w = _word(rng)
    ch = rng.choice(w)
    return Item(f'"{w}".index("{ch}")', str(find(w, ch)), "The position of the first match, from 0.")


def i_find_missing(rng):
    w = _word(rng)
    return Item(f'"{w}".find("z")', "-1", "find gives -1 when there is no match (index would raise).")


def i_after(rng):
    xs = _nums(rng, 5, 6)
    k = rng.randrange(len(xs) - 1)
    return Item(f"nums = {lit(xs)}\nnums[nums.index({xs[k]}) + 1]", str(xs[k + 1]), "The item just after that value.")


def i_sorted(rng):
    xs = _nums(rng, 4, 6)
    i = rng.choice((0, 1, -1, -2))
    return Item(f"sorted({lit(xs)})[{i}]", str(_at(isort(xs), i)), "sorted makes a new list in order; then index it.")


def i_upper(rng):
    w = _word(rng)
    i = rng.randrange(len(w))
    return Item(f'"{w}".upper()[{i}]', upper(w)[i], "upper() first, then the index.")


def i_rev(rng):
    xs = _nums(rng)
    i = rng.randrange(len(xs))
    return Item(f"{lit(xs)}[::-1][{i}]", str(reverse(xs)[i]), "[::-1] reverses; then index the reversed list.")


def i_str_rev(rng):
    w = _word(rng)
    i = rng.randrange(len(w))
    return Item(f'"{w}"[::-1][{i}]', reverse(w)[i], "Reverse the word, then index it.")


def i_slice_then(rng):
    xs = _nums(rng, 5, 6)
    s = rng.randint(1, 2)
    j = rng.randrange(len(xs) - s)
    return Item(f"{lit(xs)}[{s}:][{j}]", str(xs[s + j]), f"[{s}:] drops the first {s}; then index what is left.")


def i_str_slice(rng):
    w = _word(rng, 5)
    return Item(f'"{w}"[1:4][-1]', w[3], "[1:4] is the 2nd to 4th letters; its last is the 4th.")


def i_concat(rng):
    xs, ys = _nums(rng, 3, 3), _nums(rng, 3, 3)
    i = rng.randrange(6)
    return Item(f"({lit(xs)} + {lit(ys)})[{i}]", str((xs + ys)[i]), "+ joins the lists first; then index.")


def i_repeat(rng):
    xs = ints(rng, 3)
    i = rng.choice((0, 1, 2, 3, 4, 5, -1, -2, -4))
    return Item(f"({lit(xs)} * 2)[{i}]", str(xs[fmod(_pos(6, i), 3)]), "* 2 repeats the list: six items, then index.")


def i_expr(rng):
    xs = _nums(rng)
    k = rng.randint(2, len(xs))
    return Item(f"nums = {lit(xs)}\ni = {k}\nnums[i - 1]", str(xs[k - 1]), f"i - 1 is {k - 1}.")


def i_negvar(rng):
    xs = _nums(rng)
    k = rng.randint(1, len(xs))
    return Item(f"nums = {lit(xs)}\ni = {k}\nnums[-i]", str(_at(xs, -k)), f"-i is -{k}: {k} from the end.")


def i_wrap(rng):
    xs = _nums(rng, 4, 5)
    i = rng.randint(len(xs) + 1, len(xs) + 7)
    return Item(f"nums = {lit(xs)}\nnums[{i} % len(nums)]", str(xs[fmod(i, len(xs))]),
                f"{i} % {len(xs)} is {fmod(i, len(xs))}: the index wraps round.")


def i_digit(rng):
    num = rng.randint(1000, 9999)
    i = rng.randrange(4)
    return Item(f"str({num})[{i}]", str(num)[i], "str() makes it text, so each digit is a character.")


def i_lastdigit(rng):
    num = rng.randint(100, 9999)
    return Item(f"str({num})[-1]", str(num)[-1], "The last character of the text is the last digit.")


def i_listword(rng):
    w = _word(rng)
    i = rng.randrange(len(w))
    return Item(f'list("{w}")[{i}]', w[i], "list() on a string gives one item per letter.")


def i_split_last(rng):
    ws = rng.sample(WORDS, 3)
    return Item(f'"{"-".join(ws)}".split("-")[-1]', ws[-1], "The last piece after splitting.")


def i_maxpos(rng):
    xs = _nums(rng, 5, 6)
    best = xs[0]
    for x in xs:
        if x > best:
            best = x
    return Item(f"nums = {lit(xs)}\nnums.index(max(nums))", str(find(xs, best)), "Where the biggest one sits.")


def i_tuple_neg(rng):
    t = ints(rng, 3)
    return Item(f"({', '.join(map(str, t))})[-2]", str(t[1]), "-2 is the second from the end.")


def i_enum(rng):
    w = rng.sample("abcdefg", 3)
    i = rng.randrange(3)
    return Item(f'list(enumerate("{"".join(w)}"))[{i}]', py_show((i, w[i])), "enumerate pairs each letter with its position.")


def i_zip(rng):
    xs = ints(rng, 3)
    w = rng.sample("abcdefg", 3)
    i = rng.randrange(3)
    return Item(f'list(zip({lit(xs)}, "{"".join(w)}"))[{i}]', py_show((xs[i], w[i])), "zip pairs the items up by position.")


def i_dict_first(rng):
    ks = rng.sample(WORDS, 3)
    vs = ints(rng, 3)
    i = rng.choice((0, 1, -1))
    d = ", ".join(f'"{a}": {b}' for a, b in zip(ks, vs))
    return Item(f"d = {{{d}}}\nlist(d)[{i}]", _at(ks, i), "list(d) is the keys, in the order they were added.")


def i_dict_values(rng):
    ks = rng.sample(WORDS, 3)
    vs = ints(rng, 3)
    d = ", ".join(f'"{a}": {b}' for a, b in zip(ks, vs))
    return Item(f"d = {{{d}}}\nlist(d.values())[-1]", str(vs[-1]), "The values come out in insertion order.")


def i_nested_str(rng):
    ws = rng.sample(WORDS, 2)
    r, c = rng.randrange(2), rng.choice((0, -1))
    return Item(f'{lit(ws)}[{r}][{c}]', _at(ws[r], c), "The first index picks the word, the second its letter.")


def i_two_neg(rng):
    xs = _nums(rng, 4, 6)
    return Item(f"nums = {lit(xs)}\nnums[-1] - nums[-2]", str(xs[-1] - xs[-2]), "The last two, from the end.")


INDEX = [i_list, i_str, i_last, i_neg, i_str_last, i_str_neg, i_var, i_len_minus, i_mid, i_ends, i_prod, i_by_value,
         i_grid, i_grid_neg, i_grid_row, i_tuple, i_split, i_split_ws, i_dict, i_dict_list, i_range_list, i_range,
         i_range_neg, i_list_index, i_str_index, i_find_missing, i_after, i_sorted, i_upper, i_rev, i_str_rev,
         i_slice_then, i_str_slice, i_concat, i_repeat, i_expr, i_negvar, i_wrap, i_digit, i_lastdigit, i_listword,
         i_split_last, i_maxpos, i_tuple_neg, i_enum, i_zip, i_dict_first, i_dict_values, i_nested_str, i_two_neg]


# ── 2. Slice It ─────────────────────────────────────────────────────────

CUT = "seq[a:b] takes from a up to, not including, b."


def _xs(rng, lo=6, hi=8):
    return ints(rng, rng.randint(lo, hi))


def s_ab(rng):
    xs = _xs(rng)
    a = rng.randint(0, 2)
    b = rng.randint(a + 2, len(xs) - 1)
    return Item(f"{lit(xs)}[{a}:{b}]", py_show(py_slice(xs, a, b)), CUT)


def s_first(rng):
    xs = _xs(rng)
    k = rng.randint(2, 4)
    return Item(f"{lit(xs)}[:{k}]", py_show(py_slice(xs, None, k)), f"[:{k}] is the first {k}.")


def s_from(rng):
    xs = _xs(rng)
    k = rng.randint(2, 4)
    return Item(f"{lit(xs)}[{k}:]", py_show(py_slice(xs, k)), f"[{k}:] is everything from index {k} on.")


def s_lastk(rng):
    xs = _xs(rng)
    k = rng.randint(2, 4)
    return Item(f"{lit(xs)}[-{k}:]", py_show(py_slice(xs, -k)), f"[-{k}:] is the last {k}.")


def s_dropk(rng):
    xs = _xs(rng)
    k = rng.randint(1, 3)
    return Item(f"{lit(xs)}[:-{k}]", py_show(py_slice(xs, None, -k)), f"[:-{k}] drops the last {k}.")


def s_step2(rng):
    xs = _xs(rng)
    return Item(f"{lit(xs)}[::2]", py_show(py_slice(xs, None, None, 2)), "A step of 2 takes every second item.")


def s_step_from1(rng):
    xs = _xs(rng)
    return Item(f"{lit(xs)}[1::2]", py_show(py_slice(xs, 1, None, 2)), "Start at index 1, then every second.")


def s_reverse(rng):
    xs = _xs(rng, 4, 6)
    return Item(f"{lit(xs)}[::-1]", py_show(py_slice(xs, None, None, -1)), "A step of -1 walks backwards.")


def s_rev2(rng):
    xs = _xs(rng)
    return Item(f"{lit(xs)}[::-2]", py_show(py_slice(xs, None, None, -2)), "Backwards, every second item, from the end.")


def s_ab_step(rng):
    xs = _xs(rng, 8, 9)
    a = rng.randint(0, 2)
    b = rng.randint(6, 8)
    return Item(f"{lit(xs)}[{a}:{b}:2]", py_show(py_slice(xs, a, b, 2)), "From a to b, taking every second.")


def s_down(rng):
    xs = _xs(rng, 7, 8)
    a = rng.randint(5, 6)
    b = rng.randint(0, 2)
    return Item(f"{lit(xs)}[{a}:{b}:-1]", py_show(py_slice(xs, a, b, -1)), "Going backwards: from a down to, not including, b.")


def s_negneg(rng):
    xs = _xs(rng)
    k = rng.randint(2, 3)
    return Item(f"{lit(xs)}[-1:-{k + 1}:-1]", py_show(py_slice(xs, -1, -(k + 1), -1)), f"The last {k}, in reverse.")


def s_beyond(rng):
    xs = _xs(rng, 4, 6)
    return Item(f"{lit(xs)}[{len(xs) + 3}:]", "[]", "Slicing past the end is not an error: it is just empty.")


def s_empty_equal(rng):
    xs = _xs(rng, 4, 6)
    k = rng.randint(1, 3)
    return Item(f"{lit(xs)}[{k}:{k}]", "[]", "Start and stop are the same, so nothing is taken.")


def s_empty_backwards(rng):
    xs = _xs(rng, 5, 6)
    a = rng.randint(3, 4)
    b = rng.randint(1, 2)
    return Item(f"{lit(xs)}[{a}:{b}]", "[]", "Going forward from a bigger index to a smaller one gives nothing.")


def s_clamp_low(rng):
    xs = _xs(rng, 5, 6)
    b = rng.randint(2, 3)
    return Item(f"{lit(xs)}[-100:{b}]", py_show(py_slice(xs, -100, b)), "A start past the beginning is clamped to 0.")


def s_clamp_high(rng):
    xs = _xs(rng, 4, 6)
    return Item(f"{lit(xs)}[:100]", py_show(xs), "A stop past the end is clamped: you get everything.")


def s_copy(rng):
    xs = _xs(rng, 3, 5)
    return Item(f"{lit(xs)}[:]", py_show(xs), "[:] is the whole list, as a copy.")


def s_str(rng):
    w = _word(rng, 5)
    a = rng.randint(0, 1)
    b = rng.randint(3, 4)
    return Item(f'"{w}"[{a}:{b}]', py_slice(w, a, b), CUT)


def s_str_first(rng):
    w = _word(rng, 5)
    k = rng.randint(2, 3)
    return Item(f'"{w}"[:{k}]', py_slice(w, None, k), f"The first {k} letters.")


def s_str_last(rng):
    w = _word(rng, 5)
    k = rng.randint(2, 3)
    return Item(f'"{w}"[-{k}:]', py_slice(w, -k), f"The last {k} letters.")


def s_str_rev(rng):
    w = _word(rng)
    return Item(f'"{w}"[::-1]', reverse(w), "A string reversed by a step of -1.")


def s_str_step(rng):
    w = _word(rng, 5)
    return Item(f'"{w}"[::2]', py_slice(w, None, None, 2), "Every second letter, from the first.")


def s_str_trim(rng):
    w = _word(rng, 5)
    return Item(f'"{w}"[1:-1]', py_slice(w, 1, -1), "Drops the first and the last letter.")


def s_str_ab_step(rng):
    w = _word(rng, 6)
    return Item(f'"{w}"[0:{len(w)}:2]', py_slice(w, 0, len(w), 2), "Every second letter of the whole word.")


def s_str_empty(rng):
    w = _word(rng)
    return Item(f'repr("{w}"[{len(w) + 2}:])', "''", "An empty slice is an empty string; repr shows its quotes.")


def s_len(rng):
    xs = _xs(rng, 7, 9)
    a = rng.randint(0, 2)
    b = rng.randint(5, 7)
    return Item(f"len({lit(xs)}[{a}:{b}])", str(b - a), f"{b} - {a} items.")


def s_len_step(rng):
    xs = _xs(rng, 6, 9)
    return Item(f"len({lit(xs)}[::2])", str(fdiv(len(xs) + 1, 2)), f"Every second of {len(xs)} items: round up.")


def s_then_index(rng):
    xs = _xs(rng)
    a = rng.randint(1, 3)
    j = rng.randint(0, 2)
    return Item(f"{lit(xs)}[{a}:][{j}]", str(py_slice(xs, a)[j]), f"[{a}:] first, then item {j} of that.")


def s_slice_slice(rng):
    xs = _xs(rng, 7, 9)
    return Item(f"{lit(xs)}[1:][::2]", py_show(py_slice(py_slice(xs, 1), None, None, 2)), "Drop the first, then take every second.")


def s_tuple(rng):
    t = ints(rng, 5)
    a = rng.randint(0, 1)
    b = rng.randint(3, 4)
    return Item(f"({', '.join(map(str, t))})[{a}:{b}]", py_show(py_slice(tuple(t), a, b)), "A tuple slice is a tuple.")


def s_tuple_rev(rng):
    t = ints(rng, 4)
    return Item(f"({', '.join(map(str, t))})[::-1]", py_show(py_slice(tuple(t), None, None, -1)), "Reversed, still a tuple.")


def s_whole(rng):
    xs = _xs(rng, 4, 6)
    k = rng.randint(1, 3)
    return Item(f"{lit(xs)}[:{k}] + {lit(xs)}[{k}:]", py_show(xs), "The two halves join back into the whole list.")


def s_rotate(rng):
    xs = _xs(rng, 5, 6)
    k = rng.randint(1, 3)
    return Item(f"nums = {lit(xs)}\nnums[{k}:] + nums[:{k}]", py_show(py_slice(xs, k) + py_slice(xs, None, k)),
                "The front moves to the back: a rotation.")


def s_str_ends(rng):
    w = _word(rng, 5)
    k = rng.randint(1, 2)
    return Item(f'"{w}"[:{k}] + "{w}"[-{k}:]', py_slice(w, None, k) + py_slice(w, -k), "The first letters and the last letters joined.")


def s_neg_pair(rng):
    xs = _xs(rng, 6, 8)
    return Item(f"{lit(xs)}[-3:-1]", py_show(py_slice(xs, -3, -1)), "From 3rd-last up to, not including, the last.")


def s_half_hi(rng):
    xs = ints(rng, rng.choice((6, 7, 8)))
    h = fdiv(len(xs), 2)
    return Item(f"nums = {lit(xs)}\nnums[len(nums) // 2:]", py_show(py_slice(xs, h)), f"{len(xs)} // 2 is {h}: from there on.")


def s_half_lo(rng):
    xs = ints(rng, rng.choice((6, 7, 8)))
    h = fdiv(len(xs), 2)
    return Item(f"nums = {lit(xs)}\nnums[:len(nums) // 2]", py_show(py_slice(xs, None, h)), f"The first {h}.")


def s_range(rng):
    n = rng.randint(9, 12)
    a, b = rng.randint(0, 3), rng.randint(7, 9)
    return Item(f"list(range({n}))[{a}:{b}:3]", py_show(py_slice(list(range(n)), a, b, 3)), "Every third number from a up to b.")


def s_split(rng):
    ws = rng.sample(WORDS, 3)
    return Item(f'"{",".join(ws)}".split(",")[1:]', py_show(ws[1:]), "Slicing the pieces drops the first.")


def s_rev_first(rng):
    xs = _xs(rng, 6, 8)
    k = rng.randint(2, 3)
    return Item(f"{lit(xs)}[::-1][:{k}]", py_show(py_slice(py_slice(xs, None, None, -1), None, k)), f"Reverse it, then the first {k}: the last {k}, backwards.")


def s_sorted_top(rng):
    xs = _xs(rng, 5, 7)
    k = rng.randint(2, 3)
    return Item(f"sorted({lit(xs)})[-{k}:]", py_show(py_slice(isort(xs), -k)), f"The {k} biggest, in order.")


def s_word_second(rng):
    ws = rng.sample(WORDS, 2)
    return Item(f'"{ws[0]} {ws[1]}".split()[1][:2]', ws[1][:2], "The second word, then its first two letters.")


def s_trim_list(rng):
    xs = _xs(rng, 5, 7)
    return Item(f"{lit(xs)}[1:-1]", py_show(py_slice(xs, 1, -1)), "Drops the first and the last.")


def s_join2(rng):
    xs = _xs(rng, 6, 7)
    return Item(f"nums = {lit(xs)}\nnums[::2] + nums[1::2]", py_show(py_slice(xs, None, None, 2) + py_slice(xs, 1, None, 2)),
                "The even places first, then the odd places.")


def s_str_neg_pair(rng):
    w = _word(rng, 6)
    return Item(f'"{w}"[-3:-1]', py_slice(w, -3, -1), "Two letters, ending just before the last.")


def s_var_str(rng):
    w = _word(rng, 5)
    return Item(f's = "{w}"\ns[1:3] + s[-1]', py_slice(w, 1, 3) + w[-1], "Two letters from the middle, then the last letter.")


SLICE = [s_ab, s_first, s_from, s_lastk, s_dropk, s_step2, s_step_from1, s_reverse, s_rev2, s_ab_step, s_down, s_negneg,
         s_beyond, s_empty_equal, s_empty_backwards, s_clamp_low, s_clamp_high, s_copy, s_str, s_str_first, s_str_last,
         s_str_rev, s_str_step, s_str_trim, s_str_ab_step, s_str_empty, s_len, s_len_step, s_then_index, s_slice_slice,
         s_tuple, s_tuple_rev, s_whole, s_rotate, s_str_ends, s_neg_pair, s_half_hi, s_half_lo, s_range, s_split,
         s_rev_first, s_sorted_top, s_word_second, s_trim_list, s_join2, s_str_neg_pair, s_var_str]


# ── 3. What Type ────────────────────────────────────────────────────────

def _t(expr: str, answer: str | object, why: str = "") -> Maker:
    return row(f"type({expr}).__name__", answer, why)  # type: ignore[arg-type]


TYPE = [
    _t("$a", "int", "A whole number is an int."),
    _t("-$a", "int", "A negative whole number is still an int."),
    _t("$a.5", "float", "A number with a decimal point is a float."),
    _t("$a / $b", "float", "/ always gives a float, even when it divides exactly."),
    _t("$a // $b", "int", "// divides and rounds down to an int."),
    _t("$a // $b.0", "float", "A float anywhere makes the answer a float."),
    _t("$a * 1.0", "float", "Times a float: a float."),
    _t("$a ** 2", "int", "An int to a positive int power stays an int."),
    _t("2 ** -$k", "float", "A negative power gives a fraction: a float."),
    _t('"$w"', "str", "Text in quotes is a str."),
    _t("str($a)", "str", "str() makes text."),
    _t('"$w"[0]', "str", "One letter is still a str: Python has no char type."),
    _t('"$w" * $k', "str", "A string repeated is a string."),
    _t('len("$w")', "int", "len gives a whole number."),
    _t("True", "bool", "True is a bool."),
    _t("$a > $b", "bool", "A comparison gives a bool."),
    _t('"$x" in "$w"', "bool", "in gives a bool."),
    _t("not $a", "bool", "not always gives a bool."),
    _t("True + $a", "int", "Adding makes the bool a number: an int."),
    _t("[$a, $b]", "list", "Square brackets make a list."),
    _t('[$a, "$w"][1]', "str", "Look at the item you pick, not the list."),
    _t("[$a, $b][0]", "int", "The item is an int."),
    _t("[[$a]][0]", "list", "The item is itself a list."),
    _t("($a, $b)", "tuple", "Round brackets with a comma make a tuple."),
    _t("($a)", "int", "Without a comma, round brackets are just grouping."),
    _t("($a,)", "tuple", "The comma is what makes a tuple."),
    _t("{}", "dict", "Empty braces are a dict, not a set."),
    _t("{$a}", "set", "Braces with items and no colons are a set."),
    _t("{$a: $b}", "dict", "Braces with key: value pairs are a dict."),
    _t("set()", "set", "set() is the empty set."),
    _t("None", "NoneType", "None has its own type, NoneType."),
    _t('{"k": $a}.get("z")', "NoneType", "get gives None for a missing key."),
    _t("[].append($a)", "NoneType", "append changes the list and returns None."),
    _t("[$b, $a].sort()", "NoneType", "sort changes the list in place and returns None."),
    _t("sorted([$b, $a])", "list", "sorted gives a new list."),
    _t('"$w".split()', "list", "split gives a list of pieces."),
    _t('"$w".upper()', "str", "A string method that makes text gives a str."),
    _t('"$w".find("$x")', "int", "find gives a position (or -1): an int."),
    _t("range($a)", "range", "range is its own type; it is not a list."),
    _t("list(range($a))", "list", "list() turns it into a real list."),
    _t("divmod($a, $b)", "tuple", "divmod gives a pair: a tuple."),
    _t("round($a / $b)", "int", "round with one argument gives an int."),
    _t("round($a / $b, 1)", "float", "round with digits gives a float."),
    _t("max($a, $b)", "int", "max gives back one of the ints."),
    _t("max($a, $b / 2)", lambda p: "int" if 2 * p["a"] >= p["b"] else "float", "max gives back the winning object, so its type is the winner's."),
    _t("abs(-$a)", "int", "abs keeps the type."),
    _t('int("$a")', "int", "int() makes an int."),
    _t("float($a)", "float", "float() makes a float."),
    _t("bool($a)", "bool", "bool() makes a bool."),
    _t("0 or None", "NoneType", "or gives the last value when the first is falsy."),
    _t('[] or "$w"', "str", "or gives the first truthy value: the string."),
    _t('"$w" and $a', "int", "and gives the second value when the first is truthy."),
    _t('$a if $a > $b else "$w"', lambda p: "int" if p["a"] > p["b"] else "str", "Look at which side the condition picks."),
    _t("(lambda: $a)", "function", "A lambda is a function."),
    _t("{$a: 1}.keys()", "dict_keys", "keys() is a view, not a list."),
    _t("{$a: 1}.items()", "dict_items", "items() is a view of pairs."),
    _t("zip([$a], [$b])", "zip", "zip is a lazy object."),
    _t('enumerate("$w")', "enumerate", "enumerate is a lazy object."),
    _t("map(str, [$a])", "map", "map is lazy: it gives a map object."),
    _t('[x for x in "$w"]', "list", "A list comprehension makes a list."),
    _t('(x for x in "$w")', "generator", "Round brackets make a generator, not a tuple."),
    _t('{x for x in "$w"}', "set", "Braces with no colon: a set comprehension."),
    _t('{x: 1 for x in "$w"}', "dict", "Braces with key: value: a dict comprehension."),
    _t('"$w".encode()', "bytes", "encode gives bytes."),
    _t("$a + $b * 1j", "complex", "j makes a complex number."),
    _t("$a < $b < 10", "bool", "A chain of comparisons is still a bool."),
    _t("[$a] * $k", "list", "A list repeated is a list."),
    _t("($a, $b) * $k", "tuple", "A tuple repeated is a tuple."),
    _t('"$w"[:2]', "str", "A slice of a string is a string."),
    _t("[$a, $b, $c][:2]", "list", "A slice of a list is a list."),
    _t("($a, $b, $c)[:2]", "tuple", "A slice of a tuple is a tuple."),
    _t("($a, $b, $c)[0]", "int", "The item is an int."),
    _t('"%d" % $a', "str", "% formatting makes text."),
    _t('f"{$a}"', "str", "An f-string is a str."),
    _t("dict(a=$a)", "dict", "dict() makes a dict."),
    _t('list("$w")', "list", "list() on a string is a list of letters."),
    _t("tuple([$a])", "tuple", "tuple() makes a tuple."),
    _t("frozenset([$a])", "frozenset", "A frozenset is a set that cannot change."),
    _t("$a == $b", "bool", "== gives a bool."),
    _t("1e3", "float", "e notation is always a float."),
    _t("10 ** 2", "int", "An int power is an int."),
    _t("10 / 2", "float", "True division: a float."),
]


# ── 4. Equal or Not ─────────────────────────────────────────────────────

def _lexless(a: str, b: str) -> bool:
    for x, y in zip(a, b):
        if x != y:
            return x < y
    return len(a) < len(b)


def _q(fmt: str, truth, why: str = "") -> Maker:
    """An Equal or Not row: `truth` is a bool or a function of the parameters."""
    return row(fmt, lambda p: "yes" if (truth(p) if callable(truth) else truth) else "no", why, check=yes_no_py)


EQUAL = [
    _q("$a == $a.0", True, "An int and a float compare by value."),
    _q('"$a" == $a', False, "Python never converts: a string is not a number."),
    _q("$a + $b == $b + $a", True, "Adding in either order gives the same."),
    _q("[$a, $b] == [$b, $a]", False, "Lists are equal only in the same order."),
    _q("[$a, $b] == [$a, $b]", True, "Same items, same order."),
    _q("[] == []", True, "Two empty lists are equal (but not the same list)."),
    _q("[$a] == ($a,)", False, "A list is never equal to a tuple."),
    _q("($a, $b) == ($a, $b)", True, "Same items, same order."),
    _q("{$a, $b} == {$b, $a}", True, "Sets have no order."),
    _q('{"a": $a, "b": $b} == {"b": $b, "a": $a}', True, "Dicts compare by content, not order."),
    _q('"$w" == "$w".upper()', False, "Capitals are different characters."),
    _q('"$w" == "$w"[::-1]', lambda p: p["w"] == "".join(p["w"][len(p["w"]) - 1 - i] for i in range(len(p["w"]))),
       "Equal only if the word reads the same backwards."),
    _q('"$w" < "$v"', lambda p: _lexless(p["w"], p["v"]), "Strings compare letter by letter, alphabetically."),
    _q('"10" < "9"', True, "As strings, '1' comes before '9'."),
    _q("10 < 9", False, "As numbers, ten is bigger."),
    _q('"B" < "a"', True, "Capitals sort before lower case."),
    _q('"a" < "B"', False, "Lower case sorts after capitals."),
    _q("[$a, $b] < [$a, $c]", lambda p: p["b"] < p["c"], "Lists compare item by item: the first difference decides."),
    _q("($a, $b) < ($a + 1,)", True, "The first items differ: a < a + 1 decides."),
    _q("0.1 + 0.2 == 0.3", False, "Floats are binary: the sum is 0.30000000000000004."),
    _q("0.5 + 0.25 == 0.75", True, "These are exact in binary, so it is exact."),
    _q("0.1 * 3 == 0.3", False, "0.1 * 3 is 0.30000000000000004."),
    _q("abs(0.1 + 0.2 - 0.3) < 1e-9", True, "The usual way to compare floats: close enough."),
    _q("None == False", False, "None is not False."),
    _q("None == 0", False, "None equals nothing but None."),
    _q("True == 1", True, "True is 1 as far as == goes."),
    _q("False == 0", True, "False is 0 as far as == goes."),
    _q('True == "True"', False, "A bool is not a string."),
    _q("[] == False", False, "An empty list is falsy but not equal to False."),
    _q("bool([]) == False", True, "bool() makes the falsiness explicit."),
    _q('"" == None', False, "An empty string is not None."),
    _q('float("nan") == float("nan")', False, "nan is not equal to anything, itself included."),
    _q('float("inf") == float("inf")', True, "Infinity equals infinity."),
    _q("x = None\nx is None", True, "is None is the right way to ask."),
    _q("x = None\nx is not None", False, "x is None, so 'is not None' is false."),
    _q("x = [$a]\ny = [$a]\nx is y", False, "Two separate lists: equal, but not the same object."),
    _q("x = [$a]\ny = x\nx is y", True, "y is another name for the same list."),
    _q("x = [$a]\ny = [$a]\nx == y", True, "== compares the contents."),
    _q("x = [$a]\ny = x.copy()\nx is y", False, "copy makes a new list."),
    _q("x = [$a]\ny = x.copy()\nx == y", True, "The copy has the same contents."),
    _q("x = [$a, $b]\ny = x[:]\nx is y", False, "A full slice is a new list."),
    _q("[] is []", False, "Each [] makes a new list."),
    _q("True is True", True, "There is only one True."),
    _q("None is None", True, "There is only one None."),
    _q("type($a) is int", True, "The type of a whole number is int."),
    _q("type(True) == int", False, "The type of True is bool (although bool is a kind of int)."),
    _q("isinstance(True, int)", True, "bool is a subclass of int."),
    _q("type($a.5) == float", True, "A decimal literal is a float."),
    _q("$a < $b < $c", lambda p: p["a"] < p["b"] < p["c"], "A chain means a < b and b < c."),
    _q("$a > $b > $c", lambda p: p["a"] > p["b"] > p["c"], "A chain means a > b and b > c."),
    _q('"$x" in "$w"', lambda p: find(p["w"], p["x"]) >= 0, "in looks for that run of letters."),
    _q("$a in [$a, $b]", True, "It is in the list."),
    _q('"$a" in [$a, $b]', False, "The string '$a' is not the number."),
    _q("$a in ($b, $c)", False, "The number is not one of them."),
    _q('"k" in {"k": $a}', True, "in on a dict looks at the keys."),
    _q('$a in {"k": $a}', False, "in on a dict looks at the keys, not the values."),
    _q("$a != $a.0", False, "3 and 3.0 are equal, so != is false."),
    _q("not ($a == $b)", True, "a and b are different, so == is false and not flips it."),
    _q("$a == $a and $b == $c", False, "and needs both."),
    _q("$a == $a or $b == $c", True, "or needs one."),
    _q("[1, [$a]] == [1, [$a]]", True, "Nested lists compare deeply."),
    _q("{} == set()", False, "A dict is never equal to a set."),
    _q("($a) == ($a,)", False, "($a) is just the number; ($a,) is a tuple."),
    _q('"$a" == str($a)', True, "str() makes the same text."),
    _q('int("$a") == "$a"', False, "A number is not a string."),
    _q("$a // $b == $a / $b", lambda p: fmod(p["a"], p["b"]) == 0, "Equal only when b divides a exactly."),
    _q("7 / 2 == 3.5", True, "True division keeps the fraction."),
    _q("7 // 2 == 3.5", False, "// rounds down to 3."),
    _q("round(2.5) == 3", False, "round(2.5) is 2: halves go to the even number."),
    _q("round(3.5) == 4", True, "3.5 rounds to the even neighbour, 4."),
    _q("[3, 1, 2].sort() == [1, 2, 3]", False, "sort returns None."),
    _q("sorted([3, 1, 2]) == [1, 2, 3]", True, "sorted returns the new list."),
    _q("[1, 2, 3].reverse() == [3, 2, 1]", False, "reverse returns None."),
    _q('len("$w") == len("$w"[::-1])', True, "Reversing keeps the length."),
    _q('"abc"[0] == "abc"[0:1]', True, "One letter either way."),
    _q("1e3 == 1000", True, "A float and an int compare by value."),
    _q("0.0 == -0.0", True, "Negative zero equals zero."),
    _q("(1, 2) < (1, 2, 0)", True, "A shorter tuple that matches so far is smaller."),
    _q('"ab" * 2 == "abab"', True, "Repeating joins copies."),
    _q("[0] * 3 == [0, 0, 0]", True, "Repeating a list copies the items."),
    _q('str($a) == $a', False, "'$a' and the number are different types."),
]
