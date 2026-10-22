"""Loops pack, Python side: eight activities about what a loop leaves behind.

Range Output, Running Total, Nested Count, Break & Continue, While Trace,
Comprehension Result, Enumerate Zip, Loop Variable After. Every answer is
modelled by hand - a `while` that walks a range, an accumulator updated in a
plain Python loop that stands for the loop shown, a list built by appending -
and tests/test_brain_packs.py then runs every template through the real
interpreter. In every item the LAST line is the expression being asked about.
"""

from __future__ import annotations

import random

from ._model import WORDS, Maker, fdiv, fmod, ints, lit, py_show
from .items import Item


def _wrap(fn) -> Maker:
    """A template function that returns (code, answer, why) as a Maker that returns an Item."""
    def make(rng: random.Random) -> Item:
        code, answer, why = fn(rng)
        return Item(code, py_show(answer), why)
    make.__name__ = fn.__name__
    return make


def _register(table: list[Maker]):
    """A decorator: the function returns (code, answer, why) and becomes a template in `table`."""
    def deco(fn):
        table.append(_wrap(fn))
        return fn
    return deco


def _prange(a: int, b: int, s: int = 1) -> list[int]:
    """What range(a, b, s) visits, walked by hand."""
    out: list[int] = []
    i = a
    if s > 0:
        while i < b:
            out.append(i)
            i += s
    else:
        while i > b:
            out.append(i)
            i += s
    return out


def _word(rng: random.Random, lo: int = 4, hi: int = 6) -> str:
    return rng.choice([w for w in WORDS if lo <= len(w) <= hi])


def _digits(rng: random.Random, n: int, lo: int = 1, hi: int = 9) -> list[int]:
    """n ints from lo..hi, repeats allowed."""
    return [rng.randint(lo, hi) for _ in range(n)]


# ═══ 1. Range Output ════════════════════════════════════════════════════

RANGE: list[Maker] = []
_r = _register(RANGE)


def _h_stop(rng):
    n = rng.randint(2, 6)
    return f"range({n})", _prange(0, n), f"range({n}) starts at 0 and stops before {n}."


def _h_start_stop(rng):
    a = rng.randint(1, 5)
    b = a + rng.randint(2, 5)
    return f"range({a}, {b})", _prange(a, b), f"From {a} up to, not including, {b}."


def _h_step(rng):
    a, s = rng.randint(0, 4), rng.randint(2, 4)
    b = a + rng.randint(2 * s, 4 * s)
    return f"range({a}, {b}, {s})", _prange(a, b, s), f"Start at {a}, add {s} each time, stop before {b}."


def _h_down(rng):
    a, s = rng.randint(0, 3), rng.randint(1, 3)
    b = a + rng.randint(2 * s + 1, 4 * s)
    return f"range({b}, {a}, -{s})", _prange(b, a, -s), f"Start at {b}, take {s} off each time, stop before {a}."


def _h_plus_one(rng):
    n = rng.randint(2, 6)
    return f"range(1, {n + 1})", _prange(1, n + 1), f"The stop is {n + 1}, so the last value is {n}."


_HEADERS = (_h_stop, _h_start_stop, _h_step, _h_down, _h_plus_one)

#: What each turn adds: (the line, the value added for i, a few words for the reason).
_BODIES = (
    ("out.append(i)", lambda i: i, "each i itself"),
    ("out.append(i * 2)", lambda i: i * 2, "double each i"),
    ("out.append(i * i)", lambda i: i * i, "the square of each i"),
    ("out.append(i + 10)", lambda i: i + 10, "each i plus 10"),
    ("out.append(10 - i)", lambda i: 10 - i, "10 minus each i"),
    ("out.append(i % 3)", lambda i: fmod(i, 3), "the remainder of each i divided by 3"),
    ("out.append(i // 2)", lambda i: fdiv(i, 2), "each i halved, rounded down"),
)


def _loop_template(header, body) -> Maker:
    line, fn, what = body

    def make(rng: random.Random):
        head, vals, why = header(rng)
        code = f"out = []\nfor i in {head}:\n    {line}\nout"
        return code, [fn(i) for i in vals], f"{why} The list collects {what}."
    make.__name__ = f"range_{header.__name__[3:]}_{line[11:-1].replace(' ', '')}"
    return _wrap(make)


for _h in _HEADERS:
    for _b in _BODIES:
        RANGE.append(_loop_template(_h, _b))


@_r
def range_bare(rng):
    h, vals, why = rng.choice(_HEADERS)(rng)
    return f"list({h})", vals, why + " list() lays the values out."


@_r
def range_bare_step(rng):
    a, s = rng.randint(0, 3), rng.randint(2, 5)
    b = a + rng.randint(3 * s, 5 * s)
    return f"list(range({a}, {b}, {s}))", _prange(a, b, s), f"Steps of {s} from {a}; {b} is never reached or passed."


@_r
def range_empty_forward(rng):
    a = rng.randint(3, 8)
    b = rng.randint(1, a)
    return f"list(range({a}, {b}))", [], f"{a} is already past {b}, and the step is +1: nothing to visit."


@_r
def range_empty_down(rng):
    a = rng.randint(1, 4)
    b = a + rng.randint(2, 5)
    return f"list(range({a}, {b}, -1))", [], f"Counting down from {a} can never reach {b}: an empty list."


@_r
def range_equal(rng):
    a = rng.randint(1, 9)
    return f"list(range({a}, {a}))", [], "The start equals the stop, so there is nothing in between."


@_r
def range_negative_down(rng):
    n = rng.randint(2, 5)
    return f"list(range(0, -{n}, -1))", _prange(0, -n, -1), f"0, -1, ... stopping before -{n}."


@_r
def range_through_zero(rng):
    n, s = rng.randint(2, 4), rng.randint(1, 2)
    return f"list(range(-{n}, {n}, {s}))", _prange(-n, n, s), f"From -{n} up in steps of {s}, stopping before {n}."


@_r
def range_var_n(rng):
    n = rng.randint(2, 6)
    return f"n = {n}\nlist(range(1, n + 1))", _prange(1, n + 1), f"n + 1 is {n + 1}: the values run 1 to {n}."


@_r
def range_var_n_minus(rng):
    n = rng.randint(4, 8)
    return f"n = {n}\nlist(range(n - 1))", _prange(0, n - 1), f"n - 1 is {n - 1}, so it stops at {n - 2}."


@_r
def range_len_xs(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"xs = {lit(xs)}\nlist(range(len(xs)))", _prange(0, len(xs)), f"The indexes of {len(xs)} items: 0 to {len(xs) - 1}."


@_r
def range_len_word(rng):
    w = _word(rng)
    return f'list(range(len("{w}")))', _prange(0, len(w)), f'"{w}" has {len(w)} characters.'


@_r
def range_last(rng):
    a, s = rng.randint(0, 4), rng.randint(2, 4)
    b = a + rng.randint(3 * s, 5 * s)
    return f"range({a}, {b}, {s})[-1]", _prange(a, b, s)[-1], f"The last value visited, which may fall short of {b - 1}."


@_r
def range_nth(rng):
    a, s = rng.randint(1, 5), rng.randint(2, 5)
    k = rng.randint(1, 4)
    return f"range({a}, {a + 10 * s}, {s})[{k}]", _prange(a, a + 10 * s, s)[k], f"Index {k} counts from 0: the value after {k} steps."


@_r
def range_len(rng):
    a, s = rng.randint(0, 5), rng.randint(2, 4)
    b = a + rng.randint(3 * s, 6 * s)
    return f"len(range({a}, {b}, {s}))", len(_prange(a, b, s)), f"The values are {a}, {a + s}, ... below {b}: count them."


@_r
def range_max(rng):
    a, s = rng.randint(0, 4), rng.randint(2, 4)
    b = a + rng.randint(3 * s, 5 * s)
    vals = _prange(a, b, s)
    hi = vals[0]
    for v in vals:
        if v > hi:
            hi = v
    return f"max(range({a}, {b}, {s}))", hi, "The biggest value the range visits."


@_r
def range_sum(rng):
    a = rng.randint(0, 3)
    b = a + rng.randint(3, 6)
    total = 0
    for v in _prange(a, b):
        total += v
    return f"sum(range({a}, {b}))", total, f"{a} up to {b - 1}, added together."


@_r
def range_in(rng):
    a, s = rng.randint(0, 4), rng.randint(2, 5)
    b = a + 6 * s
    vals = _prange(a, b, s)
    probe = rng.choice(vals) + rng.choice((0, 1))
    hit = probe in vals
    return (f"{probe} in range({a}, {b}, {s})", hit,
            f"The range visits {a}, {a + s}, {a + 2 * s} ... so {probe} is " + ("one of them." if hit else "not one of them."))


@_r
def range_reversed(rng):
    a = rng.randint(0, 4)
    b = a + rng.randint(3, 5)
    return f"list(reversed(range({a}, {b})))", _prange(b - 1, a - 1, -1), "reversed walks the same values from the end."


@_r
def range_slice_rev(rng):
    a, s = rng.randint(0, 3), rng.randint(2, 3)
    b = a + rng.randint(2 * s + 1, 4 * s)
    return f"list(range({a}, {b}, {s}))[::-1]", _prange(a, b, s)[::-1], "Build the list first, then flip it."


@_r
def range_join(rng):
    h, vals, why = rng.choice(_HEADERS)(rng)
    return f'" ".join(map(str, {h}))', " ".join(str(v) for v in vals), why + " Each number becomes text, joined by spaces."


@_r
def range_join_dash(rng):
    a, s = rng.randint(1, 4), rng.randint(1, 3)
    b = a + rng.randint(2 * s, 4 * s)
    return (f'"-".join(str(i) for i in range({a}, {b}, {s}))', "-".join(str(v) for v in _prange(a, b, s)),
            f"{a}, {a + s}, ... joined with dashes.")


@_r
def range_two_ranges(rng):
    a = rng.randint(1, 3)
    b = a + rng.randint(2, 3)
    c = b + rng.randint(2, 4)
    d = c + rng.randint(1, 2)
    return f"list(range({a}, {b})) + list(range({c}, {d}))", _prange(a, b) + _prange(c, d), "Two separate runs, joined end to end."


@_r
def range_while(rng):
    a, s = rng.randint(0, 3), rng.randint(2, 4)
    b = a + rng.randint(2 * s + 1, 4 * s)
    return (f"out = []\ni = {a}\nwhile i < {b}:\n    out.append(i)\n    i += {s}\nout", _prange(a, b, s),
            f"i starts at {a} and grows by {s} while it is below {b}.")


@_r
def range_while_down(rng):
    s = rng.randint(2, 3)
    a = rng.randint(0, 2)
    b = a + rng.randint(2 * s + 1, 4 * s)
    return (f"out = []\ni = {b}\nwhile i > {a}:\n    out.append(i)\n    i -= {s}\nout", _prange(b, a, -s),
            f"i starts at {b} and drops by {s} while it is above {a}.")


@_r
def range_word_pick(rng):
    w = _word(rng, 5, 6)
    picks = "".join(w[i] for i in _prange(0, len(w), 2))
    return f'out = ""\nfor i in range(0, len("{w}"), 2):\n    out += "{w}"[i]\nout', picks, "i takes every second index: 0, 2, 4 ..."


@_r
def range_index_pairs(rng):
    xs = _digits(rng, rng.randint(3, 5))
    out = []
    for i in range(len(xs)):
        out.append(i * xs[i])
    return (f"xs = {lit(xs)}\nout = []\nfor i in range(len(xs)):\n    out.append(i * xs[i])\nout", out,
            "Each turn multiplies the index by the item at that index.")


@_r
def range_reverse_index(rng):
    xs = _digits(rng, rng.randint(3, 5))
    out = []
    for i in range(len(xs)):
        out.append(xs[len(xs) - 1 - i])
    return (f"xs = {lit(xs)}\nout = []\nfor i in range(len(xs)):\n    out.append(xs[len(xs) - 1 - i])\nout", out,
            "The index counts from the far end, so the list comes out backwards.")


@_r
def range_map_lambda(rng):
    n, k = rng.randint(3, 6), rng.randint(2, 5)
    return f"list(map(lambda i: i * {k}, range({n})))", [i * k for i in _prange(0, n)], f"Each of 0 to {n - 1} times {k}."


@_r
def range_sorted_rev(rng):
    a = rng.randint(0, 3)
    b = a + rng.randint(3, 5)
    return f"sorted(range({a}, {b}), reverse=True)", _prange(b - 1, a - 1, -1), "sorted(..., reverse=True) puts the biggest first."


@_r
def range_doubled_list(rng):
    n = rng.randint(2, 4)
    return f"list(range({n})) * 2", _prange(0, n) + _prange(0, n), "Multiplying a list by 2 repeats the whole list."


@_r
def range_var_step(rng):
    step = rng.randint(2, 4)
    b = rng.randint(3 * step, 5 * step)
    return f"step = {step}\nlist(range(0, {b}, step))", _prange(0, b, step), f"Step is {step}: 0, {step}, {2 * step} ..."


@_r
def range_offset(rng):
    a = rng.randint(3, 6)
    n = rng.randint(2, 4)
    return f"list(range({a}, {a} + {n}))", _prange(a, a + n), f"{a} + {n} is {a + n}, so it stops before {a + n}."


@_r
def range_if_filter(rng):
    a = rng.randint(1, 3)
    b = a + rng.randint(5, 8)
    k = rng.choice((2, 3))
    out = [i for i in _prange(a, b) if fmod(i, k) == 0]
    return (f"out = []\nfor i in range({a}, {b}):\n    if i % {k} == 0:\n        out.append(i)\nout", out,
            f"Only the multiples of {k} in {a} to {b - 1} are kept.")


# ═══ 2. Running Total ═══════════════════════════════════════════════════

TOTAL: list[Maker] = []
_t = _register(TOTAL)

_VOWELS = "aeiou"


@_t
def total_sum_range(rng):
    a = rng.randint(1, 4)
    b = a + rng.randint(3, 6)
    t = 0
    for i in _prange(a, b):
        t += i
    return f"total = 0\nfor i in range({a}, {b}):\n    total += i\ntotal", t, f"Adds {a}, {a + 1} ... {b - 1}."


@_t
def total_sum_list(rng):
    xs = _digits(rng, rng.randint(3, 5))
    t = 0
    for x in xs:
        t += x
    return f"xs = {lit(xs)}\ntotal = 0\nfor x in xs:\n    total += x\ntotal", t, "total starts at 0 and takes each item in turn."


@_t
def total_product(rng):
    xs = _digits(rng, rng.randint(3, 4), 1, 5)
    t = 1
    for x in xs:
        t *= x
    return f"xs = {lit(xs)}\ntotal = 1\nfor x in xs:\n    total *= x\ntotal", t, "A product starts at 1, not 0."


@_t
def total_squares(rng):
    n = rng.randint(3, 6)
    t = 0
    for i in range(1, n + 1):
        t += i * i
    return f"total = 0\nfor i in range(1, {n + 1}):\n    total += i * i\ntotal", t, f"The squares of 1 to {n}, added up."


@_t
def total_evens(rng):
    xs = _digits(rng, 5)
    t = 0
    for x in xs:
        if fmod(x, 2) == 0:
            t += x
    return (f"xs = {lit(xs)}\ntotal = 0\nfor x in xs:\n    if x % 2 == 0:\n        total += x\ntotal", t,
            "Only the even items are added.")


@_t
def total_count_over(rng):
    xs = _digits(rng, rng.randint(5, 6))
    lim = rng.randint(3, 6)
    c = 0
    for x in xs:
        if x > lim:
            c += 1
    return (f"xs = {lit(xs)}\ncount = 0\nfor x in xs:\n    if x > {lim}:\n        count += 1\ncount", c,
            f"count goes up once for each item above {lim}.")


@_t
def total_count_equal(rng):
    xs = _digits(rng, 6, 1, 4)
    v = rng.randint(1, 4)
    c = 0
    for x in xs:
        if x == v:
            c += 1
    return f"xs = {lit(xs)}\ncount = 0\nfor x in xs:\n    if x == {v}:\n        count += 1\ncount", c, f"Counts the {v}s."


@_t
def total_max(rng):
    xs = _digits(rng, rng.randint(4, 6))
    best = xs[0]
    for x in xs:
        if x > best:
            best = x
    return f"xs = {lit(xs)}\nbest = xs[0]\nfor x in xs:\n    if x > best:\n        best = x\nbest", best, "best is replaced whenever a bigger item turns up."


@_t
def total_min(rng):
    xs = _digits(rng, rng.randint(4, 6))
    low = 99
    for x in xs:
        if x < low:
            low = x
    return f"xs = {lit(xs)}\nlow = 99\nfor x in xs:\n    if x < low:\n        low = x\nlow", low, "low is replaced whenever a smaller item turns up."


@_t
def total_reverse_text(rng):
    w = _word(rng)
    out = ""
    for ch in w:
        out = ch + out
    return f'out = ""\nfor ch in "{w}":\n    out = ch + out\nout', out, "Each new letter goes in front, so the word ends up backwards."


@_t
def total_double_letters(rng):
    w = _word(rng, 3, 4)
    out = ""
    for ch in w:
        out += ch * 2
    return f'out = ""\nfor ch in "{w}":\n    out += ch * 2\nout', out, "Every letter is added twice."


@_t
def total_vowels(rng):
    w = _word(rng, 4, 7)
    c = 0
    for ch in w:
        if ch in _VOWELS:
            c += 1
    return f'count = 0\nfor ch in "{w}":\n    if ch in "aeiou":\n        count += 1\ncount', c, "Counts the vowels in the word."


@_t
def total_countdown(rng):
    xs = _digits(rng, rng.randint(3, 4))
    start = rng.randint(20, 40)
    t = start
    for x in xs:
        t -= x
    return f"total = {start}\nfor x in {lit(xs)}:\n    total -= x\ntotal", t, f"{start} with each item taken off in turn."


@_t
def total_doubling(rng):
    a, n = rng.randint(1, 5), rng.randint(3, 5)
    t = a
    for _ in range(n):
        t *= 2
    return f"total = {a}\nfor _ in range({n}):\n    total *= 2\ntotal", t, f"{a} doubled {n} times."


@_t
def total_alternate(rng):
    xs = _digits(rng, rng.randint(4, 5))
    t, sign = 0, 1
    for x in xs:
        t += sign * x
        sign = -sign
    return (f"xs = {lit(xs)}\ntotal = 0\nsign = 1\nfor x in xs:\n    total += sign * x\n    sign = -sign\ntotal", t,
            "The sign flips every turn: add, subtract, add ...")


@_t
def total_number_build(rng):
    ds = _digits(rng, rng.randint(3, 4))
    n = 0
    for d in ds:
        n = n * 10 + d
    return f"n = 0\nfor d in {lit(ds)}:\n    n = n * 10 + d\nn", n, "Each turn shifts n one place left and adds the next digit."


@_t
def total_digit_text(rng):
    num = str(rng.randint(1000, 9999))
    t = 0
    for ch in num:
        t += int(ch)
    return f'total = 0\nfor ch in "{num}":\n    total += int(ch)\ntotal', t, "int(ch) turns each digit character into a number."


@_t
def total_partials(rng):
    xs = _digits(rng, rng.randint(3, 5))
    out, t = [], 0
    for x in xs:
        t += x
        out.append(t)
    return (f"xs = {lit(xs)}\nout = []\ntotal = 0\nfor x in xs:\n    total += x\n    out.append(total)\nout", out,
            "A running total: each entry is the sum so far.")


@_t
def total_running_max(rng):
    xs = _digits(rng, rng.randint(4, 6))
    out, best = [], 0
    for x in xs:
        if x > best:
            best = x
        out.append(best)
    return (f"xs = {lit(xs)}\nout = []\nbest = 0\nfor x in xs:\n    if x > best:\n        best = x\n    out.append(best)\nout", out,
            "Each entry is the biggest item seen so far.")


@_t
def total_weighted(rng):
    xs = _digits(rng, rng.randint(3, 4))
    t = 0
    for i in range(len(xs)):
        t += i * xs[i]
    return f"xs = {lit(xs)}\ntotal = 0\nfor i in range(len(xs)):\n    total += i * xs[i]\ntotal", t, "Each item is multiplied by its index first; the first counts for 0."


@_t
def total_dot(rng):
    n = rng.randint(2, 4)
    xs, ys = _digits(rng, n), _digits(rng, n)
    t = 0
    for i in range(n):
        t += xs[i] * ys[i]
    return (f"xs = {lit(xs)}\nys = {lit(ys)}\ntotal = 0\nfor i in range(len(xs)):\n    total += xs[i] * ys[i]\ntotal", t,
            "Multiply the items at the same position, then add the products.")


@_t
def total_str_numbers(rng):
    a = rng.randint(0, 3)
    b = a + rng.randint(3, 5)
    out = ""
    for i in _prange(a, b):
        out += str(i)
    return f'out = ""\nfor i in range({a}, {b}):\n    out += str(i)\nout', out, "str(i) is text, so += joins the digits instead of adding."


@_t
def total_str_commas(rng):
    a = rng.randint(1, 5)
    b = a + rng.randint(2, 4)
    out = ""
    for i in _prange(a, b):
        out += str(i) + ","
    return f'out = ""\nfor i in range({a}, {b}):\n    out += str(i) + ","\nout', out, "Every number is followed by a comma, including the last."


@_t
def total_dict_values(rng):
    ks = rng.sample(WORDS, 3)
    vs = _digits(rng, 3)
    d = ", ".join(f'"{k}": {v}' for k, v in zip(ks, vs))
    t = 0
    for v in vs:
        t += v
    return f"d = {{{d}}}\ntotal = 0\nfor k in d:\n    total += d[k]\ntotal", t, "Looping over a dict gives its keys; d[k] looks up each value."


@_t
def total_dict_vals_method(rng):
    ks = rng.sample(WORDS, 3)
    vs = _digits(rng, 3)
    d = ", ".join(f'"{k}": {v}' for k, v in zip(ks, vs))
    t = 1
    for v in vs:
        t *= v
    return f"d = {{{d}}}\ntotal = 1\nfor v in d.values():\n    total *= v\ntotal", t, ".values() gives the values themselves; they are multiplied together."


@_t
def total_factorial(rng):
    n = rng.randint(3, 6)
    t = 1
    for i in range(1, n + 1):
        t *= i
    return f"total = 1\nfor i in range(1, {n + 1}):\n    total *= i\ntotal", t, f"1 * 2 * ... * {n}."


@_t
def total_fib(rng):
    n = rng.randint(4, 9)
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return f"a, b = 0, 1\nfor _ in range({n}):\n    a, b = b, a + b\na", a, f"The pair steps along the Fibonacci numbers {n} times; a is the first of the pair."


@_t
def total_multiples(rng):
    n = rng.randint(8, 15)
    k = rng.choice((3, 4, 5))
    t = 0
    for i in range(1, n + 1):
        if fmod(i, k) == 0:
            t += i
    return f"total = 0\nfor i in range(1, {n + 1}):\n    if i % {k} == 0:\n        total += i\ntotal", t, f"Adds the multiples of {k} from 1 to {n}."


@_t
def total_balance(rng):
    start = rng.randint(10, 30)
    moves = [rng.choice((-1, 1)) * rng.randint(2, 12) for _ in range(rng.randint(3, 4))]
    t = start
    for m in moves:
        t += m
    return f"balance = {start}\nfor m in {lit(moves)}:\n    balance += m\nbalance", t, "Adding a negative number takes it away."


@_t
def total_word_lengths(rng):
    ws = rng.sample(WORDS, 3)
    t = 0
    for w in ws:
        t += len(w)
    return f"total = 0\nfor w in {lit(ws)}:\n    total += len(w)\ntotal", t, "len(w) is the number of letters in each word."


@_t
def total_first_letters(rng):
    ws = rng.sample(WORDS, rng.randint(3, 4))
    out = ""
    for w in ws:
        out += w[0]
    return f'out = ""\nfor w in {lit(ws)}:\n    out += w[0]\nout', out, "w[0] is the first letter of each word."


@_t
def total_longest(rng):
    ws = rng.sample(WORDS, 4)
    best = ""
    for w in ws:
        if len(w) > len(best):
            best = w
    return f'best = ""\nfor w in {lit(ws)}:\n    if len(w) > len(best):\n        best = w\nbest', best, "best changes only for a strictly longer word, so the first of a tie stays."


@_t
def total_net_sign(rng):
    xs = [rng.choice((-1, 1)) * rng.randint(1, 9) for _ in range(rng.randint(4, 6))]
    t = 0
    for x in xs:
        t += 1 if x > 0 else -1
    return f"total = 0\nfor x in {lit(xs)}:\n    total += 1 if x > 0 else -1\ntotal", t, "Each positive item adds 1, each other item takes 1 off."


@_t
def total_double_plus_one(rng):
    n = rng.randint(3, 6)
    t = 0
    for _ in range(n):
        t = t * 2 + 1
    return f"total = 0\nfor _ in range({n}):\n    total = total * 2 + 1\ntotal", t, "0, 1, 3, 7, 15 ...: each turn doubles and adds 1."


@_t
def total_average(rng):
    xs = _digits(rng, rng.choice((3, 4, 5)))
    t = 0
    for x in xs:
        t += x
    return f"xs = {lit(xs)}\ntotal = 0\nfor x in xs:\n    total += x\ntotal // len(xs)", fdiv(t, len(xs)), f"The sum is {t}; // len(xs) divides by {len(xs)} and rounds down."


@_t
def total_remainder(rng):
    xs = _digits(rng, rng.randint(4, 5))
    k = rng.randint(3, 7)
    t = 0
    for x in xs:
        t += x
    return f"xs = {lit(xs)}\ntotal = 0\nfor x in xs:\n    total += x\ntotal % {k}", fmod(t, k), f"The loop gives {t}; then % {k} is the remainder."


@_t
def total_abs(rng):
    xs = [rng.choice((-1, 1)) * rng.randint(1, 9) for _ in range(rng.randint(3, 5))]
    t = 0
    for x in xs:
        t += abs(x)
    return f"total = 0\nfor x in {lit(xs)}:\n    total += abs(x)\ntotal", t, "abs drops the minus sign, so every item adds."


@_t
def total_count_letter(rng):
    ws = rng.sample(WORDS, 5)
    c = 0
    for w in ws:
        if "r" in w:
            c += 1
    return f'count = 0\nfor w in {lit(ws)}:\n    if "r" in w:\n        count += 1\ncount', c, 'Counts the words that contain an "r".'


@_t
def total_grow_text(rng):
    n = rng.randint(2, 5)
    t = 1
    for _ in range(n):
        t += t
    return f'out = "a"\nfor _ in range({n}):\n    out = out + out\nlen(out)', t, f"The text doubles in length {n} times, starting from 1."


@_t
def total_binary(rng):
    bits = [rng.randint(0, 1) for _ in range(rng.randint(4, 5))]
    bits[0] = 1
    t = 0
    for b in bits:
        t = t * 2 + b
    return f"n = 0\nfor bit in {lit(bits)}:\n    n = n * 2 + bit\nn", t, "Reading binary: double what you have, then add the next bit."


@_t
def total_threshold(rng):
    xs = _digits(rng, rng.randint(5, 6))
    lim = rng.randint(3, 6)
    t = 0
    for x in xs:
        t += x if x > lim else 0
    return f"xs = {lit(xs)}\ntotal = 0\nfor x in xs:\n    total += x if x > {lim} else 0\ntotal", t, f"Only items above {lim} are added; the rest add 0."


@_t
def total_reverse_list(rng):
    xs = _digits(rng, rng.randint(3, 5))
    out: list[int] = []
    for x in xs:
        out = [x] + out
    return f"out = []\nfor x in {lit(xs)}:\n    out = [x] + out\nout", out, "Each item is put in front of the list so far: the order flips."


@_t
def total_step_range(rng):
    a, s = rng.randint(0, 3), rng.randint(2, 4)
    b = a + rng.randint(3 * s, 5 * s)
    t = 0
    for i in _prange(a, b, s):
        t += i
    return f"total = 0\nfor i in range({a}, {b}, {s}):\n    total += i\ntotal", t, f"Adds {a}, {a + s}, ... stopping before {b}."


@_t
def total_negative_count(rng):
    xs = [rng.choice((-1, 1)) * rng.randint(1, 9) for _ in range(rng.randint(5, 6))]
    c = 0
    for x in xs:
        if x < 0:
            c += 1
    return f"count = 0\nfor x in {lit(xs)}:\n    if x < 0:\n        count += 1\ncount", c, "Counts the items below zero."


@_t
def total_lengths_list(rng):
    ws = rng.sample(WORDS, 3)
    out = []
    for w in ws:
        out.append(len(w))
    return f"out = []\nfor w in {lit(ws)}:\n    out.append(len(w))\nout", out, "One length per word, in order."


# ═══ 3. Nested Count ════════════════════════════════════════════════════

NESTED: list[Maker] = []
_n = _register(NESTED)

@_n
def nest_product(rng):
    a, b = rng.randint(2, 5), rng.randint(2, 6)
    return (f"count = 0\nfor i in range({a}):\n    for j in range({b}):\n        count += 1\ncount", a * b,
            f"The inner loop runs {b} times for each of the {a} outer turns.")


@_n
def nest_ranges(rng):
    a = rng.randint(1, 3)
    b = a + rng.randint(2, 4)
    c = rng.randint(1, 3)
    d = c + rng.randint(2, 4)
    n = 0
    for _i in _prange(a, b):
        for _j in _prange(c, d):
            n += 1
    return (f"count = 0\nfor i in range({a}, {b}):\n    for j in range({c}, {d}):\n        count += 1\ncount", n,
            f"{b - a} outer values times {d - c} inner values.")


@_n
def nest_triangle(rng):
    a = rng.randint(3, 6)
    n = 0
    for i in range(a):
        for _j in range(i):
            n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range(i):\n        count += 1\ncount", n,
            f"The inner loop runs i times: 0 + 1 + ... + {a - 1}.")


@_n
def nest_triangle_plus(rng):
    a = rng.randint(3, 6)
    n = 0
    for i in range(a):
        for _j in range(i + 1):
            n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range(i + 1):\n        count += 1\ncount", n,
            f"The inner loop runs i + 1 times: 1 + 2 + ... + {a}.")


@_n
def nest_shrinking(rng):
    a = rng.randint(3, 6)
    n = 0
    for i in range(a):
        for _j in range(a - i):
            n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range({a} - i):\n        count += 1\ncount", n,
            f"The inner loop runs {a}, {a - 1}, ... 1 times.")


@_n
def nest_from_i(rng):
    a = rng.randint(3, 6)
    n = 0
    for i in range(a):
        for _j in range(i, a):
            n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range(i, {a}):\n        count += 1\ncount", n,
            f"j starts at i and stops before {a}: {a}, {a - 1}, ... 1 times.")


@_n
def nest_from_one(rng):
    a = rng.randint(3, 6)
    n = 0
    for i in range(1, a):
        for _j in range(i, a):
            n += 1
    return (f"count = 0\nfor i in range(1, {a}):\n    for j in range(i, {a}):\n        count += 1\ncount", n,
            f"i runs 1 to {a - 1}; each inner loop runs {a} - i times.")


@_n
def nest_i_less_j(rng):
    a = rng.randint(3, 6)
    n = 0
    for i in range(a):
        for j in range(a):
            if i < j:
                n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range({a}):\n        if i < j:\n            count += 1\ncount", n,
            "Counts the pairs where i is smaller than j: half the grid, without the diagonal.")


@_n
def nest_diagonal(rng):
    a, b = rng.randint(3, 6), rng.randint(3, 6)
    n = 0
    for i in range(a):
        for j in range(b):
            if i == j:
                n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range({b}):\n        if i == j:\n            count += 1\ncount", n,
            f"i equals j only on the diagonal: min({a}, {b}) times.")


@_n
def nest_off_diagonal(rng):
    a = rng.randint(2, 5)
    n = 0
    for i in range(a):
        for j in range(a):
            if i != j:
                n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range({a}):\n        if i != j:\n            count += 1\ncount", n,
            f"All {a * a} pairs except the {a} where i equals j.")


@_n
def nest_sum_target(rng):
    a, b, k = rng.randint(3, 5), rng.randint(3, 5), rng.randint(2, 5)
    n = 0
    for i in range(a):
        for j in range(b):
            if i + j == k:
                n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range({b}):\n        if i + j == {k}:\n            count += 1\ncount", n,
            f"Counts the pairs (i, j) that add up to {k}.")


@_n
def nest_even_sum(rng):
    a, b = rng.randint(2, 5), rng.randint(2, 5)
    n = 0
    for i in range(a):
        for j in range(b):
            if fmod(i + j, 2) == 0:
                n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range({b}):\n        if (i + j) % 2 == 0:\n            count += 1\ncount", n,
            "Counts the pairs whose sum is even.")


@_n
def nest_product_big(rng):
    a, b, t = rng.randint(3, 5), rng.randint(3, 5), rng.randint(2, 6)
    n = 0
    for i in range(a):
        for j in range(b):
            if i * j > t:
                n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range({b}):\n        if i * j > {t}:\n            count += 1\ncount", n,
            f"Counts the pairs whose product is above {t}.")


@_n
def nest_sum_products(rng):
    a, b = rng.randint(2, 4), rng.randint(2, 4)
    t = 0
    for i in range(a):
        for j in range(b):
            t += i * j
    return (f"total = 0\nfor i in range({a}):\n    for j in range({b}):\n        total += i * j\ntotal", t,
            "Every pair adds its product to total.")


@_n
def nest_sum_inner(rng):
    a, b = rng.randint(2, 4), rng.randint(3, 5)
    t = 0
    for _i in range(a):
        for j in range(b):
            t += j
    return (f"total = 0\nfor i in range({a}):\n    for j in range({b}):\n        total += j\ntotal", t,
            f"The inner loop adds 0 + 1 + ... + {b - 1}, once for each of the {a} outer turns.")


@_n
def nest_outer_counts_too(rng):
    a, b = rng.randint(2, 5), rng.randint(2, 4)
    n = 0
    for _i in range(a):
        n += 1
        for _j in range(b):
            n += 1
    return (f"count = 0\nfor i in range({a}):\n    count += 1\n    for j in range({b}):\n        count += 1\ncount", n,
            f"Each outer turn adds 1 itself, plus {b} from the inner loop.")


@_n
def nest_step_two(rng):
    a, b = rng.randint(4, 8), rng.randint(2, 4)
    n = 0
    for _i in range(0, a, 2):
        for _j in range(b):
            n += 1
    return (f"count = 0\nfor i in range(0, {a}, 2):\n    for j in range({b}):\n        count += 1\ncount", n,
            f"The outer loop visits {len(_prange(0, a, 2))} values.")


@_n
def nest_inner_step(rng):
    a, b = rng.randint(2, 4), rng.randint(5, 9)
    n = 0
    for _i in range(a):
        for _j in range(0, b, 3):
            n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range(0, {b}, 3):\n        count += 1\ncount", n,
            f"The inner loop visits {len(_prange(0, b, 3))} values: 0, 3, ...")


@_n
def nest_three(rng):
    a, b, c = rng.randint(2, 3), rng.randint(2, 3), rng.randint(2, 3)
    return (f"count = 0\nfor i in range({a}):\n    for j in range({b}):\n        for k in range({c}):\n            count += 1\ncount",
            a * b * c, f"{a} times {b} times {c}.")


@_n
def nest_three_triangle(rng):
    a = rng.randint(3, 4)
    n = 0
    for i in range(a):
        for j in range(i):
            for _k in range(j):
                n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range(i):\n        for k in range(j):\n            count += 1\ncount", n,
            "Each level is limited by the one outside it, so few passes reach the innermost body.")


@_n
def nest_while(rng):
    a, b = rng.randint(2, 4), rng.randint(2, 4)
    return (f"count = 0\ni = 0\nwhile i < {a}:\n    j = 0\n    while j < {b}:\n        count += 1\n        j += 1\n    i += 1\ncount",
            a * b, f"j restarts at 0 on each of the {a} outer turns.")


@_n
def nest_while_halving(rng):
    a = rng.randint(4, 8)
    n = 0
    for i in range(1, a):
        j = i
        while j > 0:
            n += 1
            j = fdiv(j, 2)
    return (f"count = 0\nfor i in range(1, {a}):\n    j = i\n    while j > 0:\n        count += 1\n        j //= 2\ncount", n,
            "The inner loop runs once per binary digit of i: 1 for 1, 2 for 2 and 3, 3 for 4 to 7.")


@_n
def nest_inner_break(rng):
    a, b, k = rng.randint(2, 5), rng.randint(4, 6), rng.randint(1, 3)
    n = 0
    for _i in range(a):
        for j in range(b):
            if j == k:
                break
            n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range({b}):\n        if j == {k}:\n            break\n        count += 1\ncount", n,
            f"break leaves only the inner loop: {k} passes for each of the {a} outer turns.")


@_n
def nest_inner_continue(rng):
    a, b, k = rng.randint(2, 4), rng.randint(3, 6), rng.randint(0, 2)
    n = 0
    for _i in range(a):
        for j in range(b):
            if j == k:
                continue
            n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range({b}):\n        if j == {k}:\n            continue\n        count += 1\ncount", n,
            f"One of the {b} inner turns is skipped each time.")


@_n
def nest_grid_cells(rng):
    grid = [_digits(rng, rng.randint(2, 4)) for _ in range(rng.randint(2, 3))]
    n = 0
    for row in grid:
        for _x in row:
            n += 1
    return f"grid = {lit(grid)}\ncount = 0\nfor row in grid:\n    for x in row:\n        count += 1\ncount", n, "Counts every cell in every row."


@_n
def nest_grid_sum(rng):
    grid = [_digits(rng, rng.randint(2, 3)) for _ in range(rng.randint(2, 3))]
    t = 0
    for row in grid:
        for x in row:
            t += x
    return f"grid = {lit(grid)}\ntotal = 0\nfor row in grid:\n    for x in row:\n        total += x\ntotal", t, "Adds every cell of every row."


@_n
def nest_grid_big(rng):
    grid = [_digits(rng, 3) for _ in range(rng.randint(2, 3))]
    lim = rng.randint(3, 6)
    n = 0
    for row in grid:
        for x in row:
            if x > lim:
                n += 1
    return (f"grid = {lit(grid)}\ncount = 0\nfor row in grid:\n    for x in row:\n        if x > {lim}:\n            count += 1\ncount", n,
            f"Counts the cells above {lim}.")


@_n
def nest_grid_flat(rng):
    grid = [_digits(rng, 2) for _ in range(rng.randint(2, 3))]
    out = []
    for row in grid:
        for x in row:
            out.append(x * 2)
    return f"grid = {lit(grid)}\nout = []\nfor row in grid:\n    for x in row:\n        out.append(x * 2)\nout", out, "The rows are flattened into one list, each cell doubled."


@_n
def nest_grid_column(rng):
    grid = [_digits(rng, 3) for _ in range(3)]
    c = rng.randint(0, 2)
    t = 0
    for row in grid:
        t += row[c]
    return f"grid = {lit(grid)}\ntotal = 0\nfor row in grid:\n    total += row[{c}]\ntotal", t, f"Adds item {c} of each row: a column."


@_n
def nest_words_letters(rng):
    ws = rng.sample(WORDS, 3)
    n = 0
    for w in ws:
        for _ch in w:
            n += 1
    return f'count = 0\nfor w in {lit(ws)}:\n    for ch in w:\n        count += 1\ncount', n, "One pass per letter of every word: the total of the lengths."


@_n
def nest_letter_hits(rng):
    ws = rng.sample(WORDS, 4)
    n = 0
    for w in ws:
        for ch in w:
            if ch == "e":
                n += 1
    return f'count = 0\nfor w in {lit(ws)}:\n    for ch in w:\n        if ch == "e":\n            count += 1\ncount', n, 'Counts every "e" in every word.'


@_n
def nest_stars(rng):
    a = rng.randint(2, 4)
    out = ""
    for i in range(a):
        for _j in range(i + 1):
            out += "*"
        out += "/"
    return f'out = ""\nfor i in range({a}):\n    for j in range(i + 1):\n        out += "*"\n    out += "/"\nout', out, "Row i has i + 1 stars; each row ends with a slash."


@_n
def nest_stars_len(rng):
    a = rng.randint(3, 5)
    n = 0
    for i in range(a):
        for _j in range(i + 1):
            n += 1
        n += 1
    return f'out = ""\nfor i in range({a}):\n    for j in range(i + 1):\n        out += "*"\n    out += "/"\nlen(out)', n, "The stars total 1 + 2 + ... plus one slash per row."


@_n
def nest_table(rng):
    a, b = rng.randint(2, 3), rng.randint(2, 4)
    out = []
    for i in range(1, a + 1):
        for j in range(1, b + 1):
            out.append(i * j)
    return f"out = []\nfor i in range(1, {a + 1}):\n    for j in range(1, {b + 1}):\n        out.append(i * j)\nout", out, "A multiplication table, read row by row."


@_n
def nest_pair_sums(rng):
    a = rng.randint(3, 4)
    out = []
    for i in range(a):
        for j in range(i):
            out.append(i + j)
    return f"out = []\nfor i in range({a}):\n    for j in range(i):\n        out.append(i + j)\nout", out, "j stays below i, so row 0 adds nothing."


@_n
def nest_index_pairs(rng):
    xs = _digits(rng, rng.randint(4, 5), 1, 6)
    t = rng.randint(5, 9)
    n = 0
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            if xs[i] + xs[j] == t:
                n += 1
    return (f"xs = {lit(xs)}\ncount = 0\nfor i in range(len(xs)):\n    for j in range(i + 1, len(xs)):\n        if xs[i] + xs[j] == {t}:\n            count += 1\ncount", n,
            f"Each pair of positions is tried once; counts those that add up to {t}.")


@_n
def nest_rising_pairs(rng):
    xs = _digits(rng, rng.randint(4, 5))
    n = 0
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            if xs[i] < xs[j]:
                n += 1
    return (f"xs = {lit(xs)}\ncount = 0\nfor i in range(len(xs)):\n    for j in range(i + 1, len(xs)):\n        if xs[i] < xs[j]:\n            count += 1\ncount", n,
            "Counts the pairs where the later item is bigger.")


@_n
def nest_all_pairs(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return (f"xs = {lit(xs)}\ncount = 0\nfor x in xs:\n    for y in xs:\n        count += 1\ncount", len(xs) * len(xs),
            f"{len(xs)} items against {len(xs)} items.")


@_n
def nest_edge(rng):
    a, b = rng.randint(3, 5), rng.randint(3, 5)
    n = 0
    for i in range(a):
        for j in range(b):
            if i == 0 or j == 0:
                n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range({b}):\n        if i == 0 or j == 0:\n            count += 1\ncount", n,
            "Counts the first row and the first column; the corner is counted once.")


@_n
def nest_i_greater(rng):
    a, b = rng.randint(3, 6), rng.randint(2, 5)
    n = 0
    for i in range(a):
        for j in range(b):
            if i > j:
                n += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range({b}):\n        if i > j:\n            count += 1\ncount", n,
            "Counts the pairs where i is the bigger one.")


@_n
def nest_divisors(rng):
    n = rng.randint(4, 8)
    c = 0
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if fmod(i, j) == 0:
                c += 1
    return (f"count = 0\nfor i in range(1, {n + 1}):\n    for j in range(1, {n + 1}):\n        if i % j == 0:\n            count += 1\ncount", c,
            "Counts the pairs where j divides i exactly.")


@_n
def nest_triangle_sums(rng):
    n = rng.randint(3, 5)
    t = 0
    for i in range(1, n + 1):
        for j in range(1, i + 1):
            t += j
    return f"total = 0\nfor i in range(1, {n + 1}):\n    for j in range(1, i + 1):\n        total += j\ntotal", t, "Row i adds 1 + 2 + ... + i; the rows are added together."


@_n
def nest_x_by_outer(rng):
    a, b = rng.randint(3, 5), rng.randint(2, 4)
    x = 0
    for i in range(a):
        for _j in range(b):
            x += i
    return f"x = 0\nfor i in range({a}):\n    for j in range({b}):\n        x += i\nx", x, f"Each i is added {b} times (once per inner pass)."


@_n
def nest_outer_only(rng):
    a, b = rng.randint(3, 5), rng.randint(2, 4)
    n = 0
    for _i in range(a):
        for _j in range(b):
            pass
        n += 1
    return f"count = 0\nfor i in range({a}):\n    for j in range({b}):\n        pass\n    count += 1\ncount", n, "count is bumped outside the inner loop: once per outer turn."


# ═══ 4. Break & Continue ════════════════════════════════════════════════

BREAK: list[Maker] = []
_b = _register(BREAK)

_STOP = "break leaves the loop at once; whatever came after it in that pass is skipped."
_SKIP = "continue skips the rest of this pass and goes straight to the next item."


@_b
def brk_sum_until_over(rng):
    xs = _digits(rng, rng.randint(5, 6))
    lim = rng.randint(8, 16)
    t = 0
    for x in xs:
        t += x
        if t > lim:
            break
    return (f"xs = {lit(xs)}\ntotal = 0\nfor x in xs:\n    total += x\n    if total > {lim}:\n        break\ntotal", t,
            f"The item that pushes total past {lim} is added first; then the loop stops.")


@_b
def brk_sum_before_over(rng):
    xs = _digits(rng, rng.randint(5, 6))
    lim = rng.randint(8, 16)
    t = 0
    for x in xs:
        if t + x > lim:
            break
        t += x
    return (f"xs = {lit(xs)}\ntotal = 0\nfor x in xs:\n    if total + x > {lim}:\n        break\n    total += x\ntotal", t,
            f"The check comes first, so the item that would pass {lim} is never added.")


@_b
def brk_count_before(rng):
    xs = _digits(rng, 6)
    t = xs[rng.randint(1, 5)]
    c = 0
    for x in xs:
        if x == t:
            break
        c += 1
    return (f"xs = {lit(xs)}\ncount = 0\nfor x in xs:\n    if x == {t}:\n        break\n    count += 1\ncount", c,
            f"Counts the items before the first {t}.")


@_b
def brk_count_missing(rng):
    xs = _digits(rng, rng.randint(4, 6), 1, 8)
    c = 0
    for x in xs:
        if x == 9:
            break
        c += 1
    return (f"xs = {lit(xs)}\ncount = 0\nfor x in xs:\n    if x == 9:\n        break\n    count += 1\ncount", c,
            "There is no 9, so the break never happens and every item is counted.")


@_b
def brk_skip_odd(rng):
    xs = _digits(rng, rng.randint(5, 6))
    t = 0
    for x in xs:
        if fmod(x, 2) == 1:
            continue
        t += x
    return (f"xs = {lit(xs)}\ntotal = 0\nfor x in xs:\n    if x % 2 == 1:\n        continue\n    total += x\ntotal", t,
            "Odd items are skipped, so only the even ones are added. " + _SKIP)


@_b
def brk_skip_value(rng):
    xs = _digits(rng, 6, 1, 4)
    v = rng.randint(1, 4)
    out = []
    for x in xs:
        if x == v:
            continue
        out.append(x)
    return (f"xs = {lit(xs)}\nout = []\nfor x in xs:\n    if x == {v}:\n        continue\n    out.append(x)\nout", out,
            f"Every {v} is skipped.")


@_b
def brk_skip_and_stop(rng):
    xs = [rng.choice((-1, 1)) * rng.randint(1, 9) for _ in range(6)]
    t = 0
    for x in xs:
        if x < 0:
            continue
        if x > 7:
            break
        t += x
    return (f"total = 0\nfor x in {lit(xs)}:\n    if x < 0:\n        continue\n    if x > 7:\n        break\n    total += x\ntotal", t,
            "Negatives are skipped; the first item over 7 ends the loop.")


@_b
def brk_else_big(rng):
    xs = _digits(rng, rng.randint(4, 5), 1, 9)
    lim = rng.randint(5, 9)
    res = "none"
    for x in xs:
        if x > lim:
            res = "big"
            break
    return (f'for x in {lit(xs)}:\n    if x > {lim}:\n        result = "big"\n        break\nelse:\n    result = "none"\nresult', res,
            "The else part runs only when the loop finishes without a break.")


@_b
def brk_else_prime(rng):
    n = rng.randint(2, 15)
    res = "prime"
    for d in range(2, n):
        if fmod(n, d) == 0:
            res = "composite"
            break
    return (f'n = {n}\nfor d in range(2, n):\n    if n % d == 0:\n        kind = "composite"\n        break\nelse:\n    kind = "prime"\nkind', res,
            "A divisor found means break (so no else); no divisor means the else runs.")


@_b
def brk_else_count(rng):
    xs = _digits(rng, rng.randint(3, 5))
    t = rng.randint(1, 9)
    n = -1
    for i in range(len(xs)):
        if xs[i] == t:
            n = i
            break
    return (f"xs = {lit(xs)}\nfor i in range(len(xs)):\n    if xs[i] == {t}:\n        n = i\n        break\nelse:\n    n = -1\nn", n,
            f"The position of the first {t}, or the else's -1 when there is none.")


@_b
def brk_while_true(rng):
    lim = rng.randint(20, 100)
    n = 1
    while True:
        n *= 2
        if n > lim:
            break
    return f"n = 1\nwhile True:\n    n *= 2\n    if n > {lim}:\n        break\nn", n, "Doubles until it is past the limit; the doubling that crosses it still counts."


@_b
def brk_while_true_count(rng):
    k = rng.randint(3, 7)
    lim = rng.randint(20, 40)
    t, c = 0, 0
    while True:
        t += k
        c += 1
        if t >= lim:
            break
    return f"total = 0\ncount = 0\nwhile True:\n    total += {k}\n    count += 1\n    if total >= {lim}:\n        break\ncount", c, f"How many {k}s it takes to reach {lim} or more."


@_b
def brk_while_continue(rng):
    n = rng.randint(5, 9)
    i, t = 0, 0
    while i < n:
        i += 1
        if fmod(i, 2) == 0:
            continue
        t += i
    return f"i = 0\ntotal = 0\nwhile i < {n}:\n    i += 1\n    if i % 2 == 0:\n        continue\n    total += i\ntotal", t, "i goes up before the check, so continue is safe; only odd i are added."


@_b
def brk_nested_inner(rng):
    a, b, k = rng.randint(2, 4), rng.randint(3, 5), rng.randint(1, 2)
    c = 0
    for _i in range(a):
        for j in range(b):
            if j >= k:
                break
            c += 1
    return (f"count = 0\nfor i in range({a}):\n    for j in range({b}):\n        if j >= {k}:\n            break\n        count += 1\ncount", c,
            f"break only ends the inner loop, so every outer turn still runs ({k} inner passes each).")


@_b
def brk_nested_flag(rng):
    n, t = rng.randint(3, 5), rng.randint(4, 8)
    pair = None
    done = False
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i * j >= t:
                pair = (i, j)
                done = True
                break
        if done:
            break
    return (f"pair = None\nfor i in range(1, {n + 1}):\n    for j in range(1, {n + 1}):\n        if i * j >= {t}:\n            pair = (i, j)\n            break\n    if pair:\n        break\npair", pair,
            f"The first pair, row by row, whose product reaches {t}. The second break stops the outer loop.")


@_b
def brk_words_until(rng):
    ws = rng.sample(WORDS, 4)
    cut = rng.randint(1, 3)
    ws[cut] = "stop"
    out = []
    for w in ws:
        if w == "stop":
            break
        out.append(w)
    return f'out = []\nfor w in {lit(ws)}:\n    if w == "stop":\n        break\n    out.append(w)\n"-".join(out)', "-".join(out), "Words are collected until the word stop appears."


@_b
def brk_words_skip(rng):
    ws = rng.sample(WORDS, 5)
    bad = rng.choice(ws)
    out = ""
    for w in ws:
        if w == bad:
            continue
        out += w[0]
    return f'out = ""\nfor w in {lit(ws)}:\n    if w == "{bad}":\n        continue\n    out += w[0]\nout', out, f'The word "{bad}" is skipped; the others give their first letter.'


@_b
def brk_sentinel(rng):
    xs = _digits(rng, 5)
    xs[rng.randint(1, 3)] = 0
    t = 0
    for x in xs:
        if x == 0:
            break
        t += x
    return f"total = 0\nfor x in {lit(xs)}:\n    if x == 0:\n        break\n    total += x\ntotal", t, "A 0 ends the loop: only what came before it is added."


@_b
def brk_skip_multiples(rng):
    n, k = rng.randint(7, 10), rng.randint(2, 3)
    out = []
    for i in range(1, n):
        if fmod(i, k) == 0:
            continue
        out.append(i)
    return f"out = []\nfor i in range(1, {n}):\n    if i % {k} == 0:\n        continue\n    out.append(i)\nout", out, f"Multiples of {k} are skipped."


@_b
def brk_range_stop(rng):
    n, k = rng.randint(8, 12), rng.randint(3, 6)
    out = []
    for i in range(n):
        if i == k:
            break
        out.append(i)
    return f"out = []\nfor i in range({n}):\n    if i == {k}:\n        break\n    out.append(i)\nout", out, f"The loop stops when i reaches {k}, before it is appended."


@_b
def brk_append_then_stop(rng):
    n, k = rng.randint(8, 12), rng.randint(3, 6)
    out = []
    for i in range(n):
        out.append(i)
        if i == k:
            break
    return f"out = []\nfor i in range({n}):\n    out.append(i)\n    if i == {k}:\n        break\nout", out, f"The append comes first, so {k} is in the list when the loop stops."


@_b
def brk_isqrt(rng):
    n = rng.randint(10, 80)
    r = 0
    for i in range(1, 20):
        if i * i > n:
            break
        r = i
    return f"r = 0\nfor i in range(1, 20):\n    if i * i > {n}:\n        break\n    r = i\nr", r, f"The biggest i whose square is at most {n}."


@_b
def brk_first_index(rng):
    xs = _digits(rng, rng.randint(5, 6), 1, 5)
    t = rng.randint(1, 6)
    idx = -1
    for i in range(len(xs)):
        if xs[i] == t:
            idx = i
            break
    return (f"xs = {lit(xs)}\nidx = -1\nfor i in range(len(xs)):\n    if xs[i] == {t}:\n        idx = i\n        break\nidx", idx,
            f"The first position holding {t}, or -1 if there is none.")


@_b
def brk_last_index(rng):
    xs = _digits(rng, rng.randint(5, 6), 1, 4)
    t = rng.randint(1, 5)
    idx = -1
    for i in range(len(xs)):
        if xs[i] == t:
            idx = i
    return (f"xs = {lit(xs)}\nidx = -1\nfor i in range(len(xs)):\n    if xs[i] == {t}:\n        idx = i\nidx", idx,
            f"No break, so idx keeps being replaced: the LAST position of {t}, or -1.")


@_b
def brk_max_skip_negative(rng):
    xs = [rng.choice((-1, 1)) * rng.randint(1, 9) for _ in range(6)]
    best = 0
    for x in xs:
        if x < 0:
            continue
        if x > best:
            best = x
    return f"best = 0\nfor x in {lit(xs)}:\n    if x < 0:\n        continue\n    if x > best:\n        best = x\nbest", best, "Negatives never get compared; best starts at 0."


@_b
def brk_count_even_continue(rng):
    xs = _digits(rng, 6)
    c = 0
    for x in xs:
        if fmod(x, 2) == 1:
            continue
        c += 1
    return f"count = 0\nfor x in {lit(xs)}:\n    if x % 2 == 1:\n        continue\n    count += 1\ncount", c, "Odd items skip the count: it counts the even ones."


@_b
def brk_leading_even(rng):
    xs = [2 * rng.randint(1, 4) for _ in range(rng.randint(2, 3))] + [rng.choice((1, 3, 5, 7))] + _digits(rng, 2)
    t = 0
    for x in xs:
        if fmod(x, 2) == 1:
            break
        t += x
    return f"total = 0\nfor x in {lit(xs)}:\n    if x % 2 == 1:\n        break\n    total += x\ntotal", t, "Adds items until the first odd one stops the loop."


@_b
def brk_ok_flag(rng):
    xs = _digits(rng, 5, 1, 9)
    if rng.random() < 0.5:
        xs[rng.randint(0, 4)] = -rng.randint(1, 5)
    ok = True
    for x in xs:
        if x < 0:
            ok = False
            break
    return f"ok = True\nfor x in {lit(xs)}:\n    if x < 0:\n        ok = False\n        break\nok", ok, "ok turns False the moment a negative item is met."


@_b
def brk_found_flag(rng):
    xs = _digits(rng, 5, 1, 9)
    lim = rng.randint(6, 10)
    found = False
    for x in xs:
        if x > lim:
            found = True
            break
    return f"found = False\nfor x in {lit(xs)}:\n    if x > {lim}:\n        found = True\n        break\nfound", found, f"Is any item above {lim}?"


@_b
def brk_nested_continue(rng):
    a = rng.randint(3, 5)
    c = 0
    for i in range(a):
        for j in range(a):
            if j == i:
                continue
            c += 1
    return f"count = 0\nfor i in range({a}):\n    for j in range({a}):\n        if j == i:\n            continue\n        count += 1\ncount", c, f"Each row skips its own diagonal cell: {a} rows of {a - 1}."


@_b
def brk_nested_triangle(rng):
    a = rng.randint(3, 5)
    c = 0
    for i in range(a):
        for j in range(a):
            if j > i:
                break
            c += 1
    return f"count = 0\nfor i in range({a}):\n    for j in range({a}):\n        if j > i:\n            break\n        count += 1\ncount", c, "Row i stops once j passes i, so it counts i + 1 cells."


@_b
def brk_outer_continue(rng):
    a, b = rng.randint(4, 7), rng.randint(2, 4)
    c = 0
    for i in range(a):
        if fmod(i, 2) == 0:
            continue
        for _j in range(b):
            c += 1
    return f"count = 0\nfor i in range({a}):\n    if i % 2 == 0:\n        continue\n    for j in range({b}):\n        count += 1\ncount", c, f"continue skips the whole inner loop for even i: {len([i for i in range(a) if i % 2])} rows run."


@_b
def brk_inner_sum_break(rng):
    a, b, k = rng.randint(2, 4), rng.randint(4, 6), rng.randint(2, 4)
    t = 0
    for _i in range(a):
        for j in range(b):
            t += j
            if j == k:
                break
    return (f"total = 0\nfor i in range({a}):\n    for j in range({b}):\n        total += j\n        if j == {k}:\n            break\ntotal", t,
            f"Each outer turn adds 0 + 1 + ... + {k} and then breaks.")


@_b
def brk_while_else(rng):
    start, step = rng.randint(15, 30), rng.randint(3, 5)
    target = rng.choice((start - step, start - 2 * step, start - 2 * step - 1))
    n = start
    msg = ""
    while n > 0:
        n -= step
        if n == target:
            msg = "hit"
            break
    else:
        msg = "missed"
    return (f'n = {start}\nwhile n > 0:\n    n -= {step}\n    if n == {target}:\n        msg = "hit"\n        break\nelse:\n    msg = "missed"\nmsg', msg,
            f"n steps down by {step}; the else part runs only if the loop ends without a break.")


@_b
def brk_leading_consonants(rng):
    w = rng.choice([x for x in WORDS if len(x) >= 4 and x[0] not in _VOWELS])
    out = ""
    for ch in w:
        if ch in _VOWELS:
            break
        out += ch
    return f'out = ""\nfor ch in "{w}":\n    if ch in "aeiou":\n        break\n    out += ch\nout', out, "Letters are collected up to the first vowel."


@_b
def brk_skip_letter(rng):
    w = _word(rng, 4, 7)
    ch0 = rng.choice(w)
    out = ""
    for ch in w:
        if ch == ch0:
            continue
        out += ch
    return f'out = ""\nfor ch in "{w}":\n    if ch == "{ch0}":\n        continue\n    out += ch\nout', out, f'Every "{ch0}" is left out.'


@_b
def brk_first_duplicate(rng):
    xs = rng.sample(range(1, 9), 4)
    xs.insert(rng.randint(2, 4), xs[rng.randint(0, 1)])
    seen = []
    for x in xs:
        if x in seen:
            break
        seen.append(x)
    return f"seen = []\nfor x in {lit(xs)}:\n    if x in seen:\n        break\n    seen.append(x)\nseen", seen, "Stops at the first item that has already been seen."


@_b
def brk_digits_until(rng):
    num = "".join(str(rng.randint(1, 7)) for _ in range(3)) + "8" + str(rng.randint(1, 7))
    t = 0
    for ch in num:
        if ch == "8":
            break
        t += int(ch)
    return f'total = 0\nfor ch in "{num}":\n    if ch == "8":\n        break\n    total += int(ch)\ntotal', t, "Digits are added up to the 8."


@_b
def brk_lcm(rng):
    a, b = rng.sample(range(2, 7), 2)
    n = 1
    while True:
        if fmod(n, a) == 0 and fmod(n, b) == 0:
            break
        n += 1
    return f"n = 1\nwhile True:\n    if n % {a} == 0 and n % {b} == 0:\n        break\n    n += 1\nn", n, f"The first number both {a} and {b} divide into."


@_b
def brk_product_over(rng):
    xs = _digits(rng, 6, 2, 4)
    lim = rng.randint(20, 60)
    p = 1
    for x in xs:
        p *= x
        if p > lim:
            break
    return f"xs = {lit(xs)}\np = 1\nfor x in xs:\n    p *= x\n    if p > {lim}:\n        break\np", p, f"Multiplies until the product is over {lim}."


@_b
def brk_skip_squares(rng):
    n = rng.randint(6, 9)
    out = []
    for i in range(n):
        if fmod(i, 2) == 1:
            continue
        out.append(i * i)
    return f"out = []\nfor i in range({n}):\n    if i % 2 == 1:\n        continue\n    out.append(i * i)\nout", out, "Only the even i are squared and kept."


# ═══ 5. While Trace ═════════════════════════════════════════════════════

WHILE: list[Maker] = []
_w = _register(WHILE)

_PALINDROMES = ("level", "noon", "radar", "civic", "kayak", "refer")
_NOT_PALINDROMES = ("farm", "drone", "carrot", "robot", "river", "maple", "stone", "grid")


@_w
def wh_halve_to(rng):
    k = rng.randint(2, 6)
    n0 = rng.randint(30, 120)
    n = n0
    while n > k:
        n = fdiv(n, 2)
    return f"n = {n0}\nwhile n > {k}:\n    n //= 2\nn", n, f"Halve (rounding down) until n is no more than {k}."


@_w
def wh_subtract_down(rng):
    s, m = rng.randint(3, 7), rng.randint(2, 6)
    n0 = rng.randint(20, 45)
    n = n0
    while n > m:
        n -= s
    return f"n = {n0}\nwhile n > {m}:\n    n -= {s}\nn", n, f"Takes {s} off until n is no more than {m}; the last step may overshoot below it."


@_w
def wh_triple(rng):
    lim = rng.randint(30, 200)
    x = 1
    while x < lim:
        x *= 3
    return f"x = 1\nwhile x < {lim}:\n    x *= 3\nx", x, f"1, 3, 9, 27 ... the first power of 3 that is {lim} or more."


@_w
def wh_double_plus(rng):
    a = rng.randint(1, 3)
    lim = rng.randint(20, 100)
    x = a
    while x < lim:
        x = x * 2 + 1
    return f"x = {a}\nwhile x < {lim}:\n    x = x * 2 + 1\nx", x, f"Each turn doubles and adds 1, until x reaches {lim} or more."


@_w
def wh_steps_down(rng):
    s = rng.randint(2, 6)
    n0 = rng.randint(15, 40)
    n, steps = n0, 0
    while n > 0:
        n -= s
        steps += 1
    return f"n = {n0}\nsteps = 0\nwhile n > 0:\n    n -= {s}\n    steps += 1\nsteps", steps, f"How many {s}s it takes to bring {n0} to zero or below."


@_w
def wh_digit_count(rng):
    n0 = rng.randint(10, 99999)
    n, c = n0, 0
    while n > 0:
        n = fdiv(n, 10)
        c += 1
    return f"n = {n0}\ncount = 0\nwhile n > 0:\n    n //= 10\n    count += 1\ncount", c, "Each // 10 drops the last digit; count counts the digits."


@_w
def wh_digit_sum(rng):
    n0 = rng.randint(100, 9999)
    n, t = n0, 0
    while n > 0:
        t += fmod(n, 10)
        n = fdiv(n, 10)
    return f"n = {n0}\ntotal = 0\nwhile n > 0:\n    total += n % 10\n    n //= 10\ntotal", t, "n % 10 is the last digit, n // 10 drops it: the digits are added."


@_w
def wh_digit_reverse(rng):
    n0 = rng.randint(100, 9999)
    n, r = n0, 0
    while n > 0:
        r = r * 10 + fmod(n, 10)
        n = fdiv(n, 10)
    return f"n = {n0}\nrev = 0\nwhile n > 0:\n    rev = rev * 10 + n % 10\n    n //= 10\nrev", r, "Digits come off the end of n and go onto the end of rev: reversed."


@_w
def wh_collatz(rng):
    n0 = rng.randint(3, 12)
    n, steps = n0, 0
    while n != 1:
        n = fdiv(n, 2) if fmod(n, 2) == 0 else 3 * n + 1
        steps += 1
    return (f"n = {n0}\nsteps = 0\nwhile n != 1:\n    n = n // 2 if n % 2 == 0 else 3 * n + 1\n    steps += 1\nsteps", steps,
            "Even: halve. Odd: triple and add 1. Count the turns until 1.")


@_w
def wh_gcd_mod(rng):
    a, b = rng.randint(6, 40), rng.randint(4, 30)
    a0, b0 = a, b
    while b:
        a, b = b, fmod(a, b)
    return f"a = {a0}\nb = {b0}\nwhile b:\n    a, b = b, a % b\na", a, "Euclid's way: replace (a, b) by (b, a % b) until b is 0; a is the common divisor."


@_w
def wh_gcd_sub(rng):
    a, b = rng.randint(4, 30), rng.randint(4, 30)
    a0, b0 = a, b
    while a != b:
        if a > b:
            a -= b
        else:
            b -= a
    return (f"a = {a0}\nb = {b0}\nwhile a != b:\n    if a > b:\n        a -= b\n    else:\n        b -= a\na", a,
            "The bigger one loses the smaller one each turn until they meet.")


@_w
def wh_next_multiple(rng):
    k = rng.randint(3, 9)
    n0 = rng.randint(10, 40)
    n = n0
    while fmod(n, k) != 0:
        n += 1
    return f"n = {n0}\nwhile n % {k} != 0:\n    n += 1\nn", n, f"The first number from {n0} up that {k} divides exactly."


@_w
def wh_meet_i(rng):
    hi0 = rng.randint(8, 16)
    i, j = 0, hi0
    while i < j:
        i += 2
        j -= 1
    return f"i = 0\nj = {hi0}\nwhile i < j:\n    i += 2\n    j -= 1\ni", i, "i climbs by 2 and j falls by 1 until they cross."


@_w
def wh_meet_j(rng):
    hi0 = rng.randint(8, 16)
    i, j = 1, hi0
    while i < j:
        i += 3
        j -= 1
    return f"i = 1\nj = {hi0}\nwhile i < j:\n    i += 3\n    j -= 1\nj", j, "i climbs by 3 and j falls by 1 until i is no longer below j."


@_w
def wh_pop_digits(rng):
    xs = _digits(rng, rng.randint(3, 4))
    out, ys = 0, list(xs)
    while ys:
        out = out * 10 + ys.pop()
    return f"xs = {lit(xs)}\nn = 0\nwhile xs:\n    n = n * 10 + xs.pop()\nn", out, "pop() takes from the END, so the digits are read backwards."


@_w
def wh_pop_front(rng):
    xs = _digits(rng, rng.randint(5, 6))
    keep = rng.randint(1, 3)
    ys = list(xs)
    while len(ys) > keep:
        ys.pop(0)
    return f"xs = {lit(xs)}\nwhile len(xs) > {keep}:\n    xs.pop(0)\nxs", ys, f"The first item is removed until only {keep} are left."


@_w
def wh_string_shrink(rng):
    w = _word(rng, 5, 7)
    s, c = w, 0
    while s:
        s = s[1:]
        c += 1
    return f's = "{w}"\ncount = 0\nwhile s:\n    s = s[1:]\n    count += 1\ncount', c, "An empty string is falsy, so the loop runs once per letter."


@_w
def wh_string_tail(rng):
    w = _word(rng, 5, 7)
    keep = rng.randint(2, 3)
    s = w
    while len(s) > keep:
        s = s[1:]
    return f'word = "{w}"\nwhile len(word) > {keep}:\n    word = word[1:]\nword', s, f"The front letter is dropped until {keep} are left."


@_w
def wh_popcount(rng):
    n0 = rng.randint(5, 60)
    n, bits = n0, 0
    while n > 0:
        bits += fmod(n, 2)
        n = fdiv(n, 2)
    return f"n = {n0}\nbits = 0\nwhile n > 0:\n    bits += n % 2\n    n //= 2\nbits", bits, "n % 2 is the lowest binary digit: bits counts the 1s."


@_w
def wh_binary_text(rng):
    n0 = rng.randint(2, 40)
    n, out = n0, ""
    while n > 0:
        out = str(fmod(n, 2)) + out
        n = fdiv(n, 2)
    return f'n = {n0}\nout = ""\nwhile n > 0:\n    out = str(n % 2) + out\n    n //= 2\nout', out, f"{n0} written in binary: each remainder goes in front."


@_w
def wh_fib_over(rng):
    lim = rng.randint(20, 120)
    a, b = 1, 1
    while b < lim:
        a, b = b, a + b
    return f"a, b = 1, 1\nwhile b < {lim}:\n    a, b = b, a + b\nb", b, f"The first Fibonacci number that is {lim} or more."


@_w
def wh_triangular(rng):
    lim = rng.randint(10, 40)
    t, i = 0, 0
    while t < lim:
        i += 1
        t += i
    return f"total = 0\ni = 0\nwhile total < {lim}:\n    i += 1\n    total += i\ni", i, f"How many of 1, 2, 3 ... it takes to add up to {lim} or more."


@_w
def wh_square_root(rng):
    n = rng.randint(5, 80)
    i = 0
    while i * i < n:
        i += 1
    return f"i = 0\nwhile i * i < {n}:\n    i += 1\ni", i, f"The first i whose square is {n} or more."


@_w
def wh_countdown_list(rng):
    s, n0 = rng.randint(2, 4), rng.randint(8, 16)
    out, n = [], n0
    while n > 0:
        out.append(n)
        n -= s
    return f"out = []\nn = {n0}\nwhile n > 0:\n    out.append(n)\n    n -= {s}\nout", out, f"Counts down from {n0} by {s} while n is above 0."


@_w
def wh_doubling_list(rng):
    lim = rng.randint(10, 70)
    a = rng.randint(1, 3)
    out, x = [], a
    while x < lim:
        out.append(x)
        x *= 2
    return f"out = []\nx = {a}\nwhile x < {lim}:\n    out.append(x)\n    x *= 2\nout", out, f"Doubles from {a} while below {lim}."


@_w
def wh_two_conditions(rng):
    a0, b0 = rng.randint(0, 3), rng.randint(2, 6)
    a, b = a0, b0
    while a < 10 and b > 0:
        a += 3
        b -= 1
    return f"a = {a0}\nb = {b0}\nwhile a < 10 and b > 0:\n    a += 3\n    b -= 1\na", a, "The loop ends as soon as either condition fails."


@_w
def wh_flag(rng):
    n0 = rng.randint(1, 20)
    n, done = n0, False
    while not done:
        n += 1
        if fmod(n, 7) == 0:
            done = True
    return f"n = {n0}\ndone = False\nwhile not done:\n    n += 1\n    if n % 7 == 0:\n        done = True\nn", n, f"Stops at the first multiple of 7 above {n0}."


@_w
def wh_else_runs(rng):
    n0, s = rng.randint(5, 12), rng.randint(2, 3)
    n = n0
    while n > 0:
        n -= s
    else:
        n = 100
    return f"n = {n0}\nwhile n > 0:\n    n -= {s}\nelse:\n    n = 100\nn", n, "No break happens, so the else part runs when the loop ends: n is 100."


@_w
def wh_else_skipped(rng):
    n0, s = rng.randint(10, 20), rng.randint(2, 4)
    stop = n0 - s * rng.randint(1, 3)
    n = n0
    while n > 0:
        n -= s
        if n == stop:
            break
    else:
        n = 100
    return (f"n = {n0}\nwhile n > 0:\n    n -= {s}\n    if n == {stop}:\n        break\nelse:\n    n = 100\nn", n,
            f"The break happens when n is {stop}, so the else part is skipped.")


@_w
def wh_count_multiples(rng):
    n, k = rng.randint(8, 20), rng.randint(2, 4)
    i, c = 0, 0
    while i < n:
        i += 1
        if fmod(i, k) == 0:
            c += 1
    return f"i = 0\ncount = 0\nwhile i < {n}:\n    i += 1\n    if i % {k} == 0:\n        count += 1\ncount", c, f"Counts the multiples of {k} from 1 to {n}."


@_w
def wh_growing_step(rng):
    lim = rng.randint(15, 50)
    pos, step = 0, 1
    while pos < lim:
        pos += step
        step += 1
    return f"pos = 0\nstep = 1\nwhile pos < {lim}:\n    pos += step\n    step += 1\npos", pos, "The step grows by 1 each turn: pos is 1, 3, 6, 10, ..."


@_w
def wh_growing_step_count(rng):
    lim = rng.randint(15, 50)
    pos, step = 0, 1
    while pos < lim:
        pos += step
        step += 1
    return f"pos = 0\nstep = 1\nwhile pos < {lim}:\n    pos += step\n    step += 1\nstep", step, "step ends one more than the number of turns."


@_w
def wh_growth(rng):
    m0 = rng.choice((50, 100, 200))
    lim = m0 + m0 // 2
    m, years = m0, 0
    while m < lim:
        m += fdiv(m, 10)
        years += 1
    return f"money = {m0}\nyears = 0\nwhile money < {lim}:\n    money += money // 10\n    years += 1\nyears", years, "Each year adds a tenth (rounded down) of what is there."


@_w
def wh_digital_root(rng):
    n0 = rng.randint(100, 9999)
    n = n0
    while n >= 10:
        s, m = 0, n
        while m:
            s += fmod(m, 10)
            m = fdiv(m, 10)
        n = s
    return (f"n = {n0}\nwhile n >= 10:\n    s = 0\n    while n:\n        s += n % 10\n        n //= 10\n    n = s\nn", n,
            "Add the digits again and again until one digit is left.")


@_w
def wh_both_shrink(rng):
    a0, b0 = rng.randint(8, 20), rng.randint(8, 20)
    a, b, c = a0, b0, 0
    while a > 0 and b > 0:
        a -= 2
        b -= 3
        c += 1
    return f"a = {a0}\nb = {b0}\ncount = 0\nwhile a > 0 and b > 0:\n    a -= 2\n    b -= 3\n    count += 1\ncount", c, "It stops when the first of a and b reaches 0 or below."


@_w
def wh_negative_end(rng):
    n0 = rng.randint(7, 30)
    n = n0
    while n > 0:
        n -= 3
    return f"x = {n0}\nwhile x > 0:\n    x -= 3\nx", n, "x ends at 0 or below, wherever the last step lands."


@_w
def wh_scan(rng):
    xs = sorted(rng.sample(range(1, 20), rng.randint(4, 6)))
    t = rng.randint(3, 18)
    i = 0
    while i < len(xs) and xs[i] < t:
        i += 1
    return f"xs = {lit(xs)}\ni = 0\nwhile i < len(xs) and xs[i] < {t}:\n    i += 1\ni", i, f"i stops at the first item that is {t} or more (or at the end)."


@_w
def wh_palindrome(rng):
    word = rng.choice(_PALINDROMES + _NOT_PALINDROMES)
    lo, hi = 0, len(word) - 1
    while lo < hi and word[lo] == word[hi]:
        lo += 1
        hi -= 1
    return (f'w = "{word}"\nlo, hi = 0, len(w) - 1\nwhile lo < hi and w[lo] == w[hi]:\n    lo += 1\n    hi -= 1\nlo >= hi', lo >= hi,
            "Two pointers walk inward while the letters match; they meet or cross only for a palindrome.")


@_w
def wh_step_to_tens(rng):
    n0 = rng.randint(11, 39)
    n = n0
    while fmod(n, 10) != 0:
        n += 3
    return f"n = {n0}\nwhile n % 10 != 0:\n    n += 3\nn", n, "Adds 3 until the last digit is 0."


@_w
def wh_odd_even_steps(rng):
    n0 = rng.randint(5, 30)
    n, steps = n0, 0
    while n > 1:
        n = n - 1 if fmod(n, 2) == 1 else fdiv(n, 2)
        steps += 1
    return f"n = {n0}\nsteps = 0\nwhile n > 1:\n    n = n - 1 if n % 2 else n // 2\n    steps += 1\nsteps", steps, "Odd: take 1 off. Even: halve. Count the turns until n reaches 1."


@_w
def wh_sum_powers(rng):
    lim = rng.randint(20, 150)
    n, t = 1, 0
    while n <= lim:
        t += n
        n *= 2
    return f"n = 1\ntotal = 0\nwhile n <= {lim}:\n    total += n\n    n *= 2\ntotal", t, f"Adds 1, 2, 4, 8 ... while n is {lim} or less."


@_w
def wh_div_quotient(rng):
    d, n0 = rng.randint(3, 7), rng.randint(20, 60)
    r, q = n0, 0
    while r >= d:
        r -= d
        q += 1
    return f"r = {n0}\nq = 0\nwhile r >= {d}:\n    r -= {d}\n    q += 1\nq", q, f"Division by repeated subtraction: how many {d}s fit in {n0}."


@_w
def wh_div_remainder(rng):
    d, n0 = rng.randint(3, 7), rng.randint(20, 60)
    r = n0
    while r >= d:
        r -= d
    return f"r = {n0}\nwhile r >= {d}:\n    r -= {d}\nr", r, f"What is left of {n0} when no more {d}s fit: the remainder."


@_w
def wh_odd_part(rng):
    n0 = rng.choice((12, 20, 24, 28, 36, 40, 44, 48, 56, 60, 72, 80))
    n = n0
    while fmod(n, 2) == 0:
        n = fdiv(n, 2)
    return f"n = {n0}\nwhile n % 2 == 0:\n    n //= 2\nn", n, "Keeps halving while n is even: what is left is odd."


@_w
def wh_string_digits(rng):
    n, i = rng.randint(6, 12), 0
    s = ""
    while i < n:
        s += str(i)
        i += 2
    return f's = ""\ni = 0\nwhile i < {n}:\n    s += str(i)\n    i += 2\ns', s, "The even numbers below n, written next to each other as text."


@_w
def wh_string_grow(rng):
    w = rng.choice(("ab", "xyz", "go", "abc", "hi"))
    s = w
    while len(s) < 10:
        s += w
    return f's = "{w}"\nwhile len(s) < 10:\n    s += "{w}"\nlen(s)', len(s), f'The text grows by {len(w)} until it has 10 or more characters.'


@_w
def wh_descending_sum(rng):
    n0 = rng.randint(6, 15)
    n, t = n0, 0
    while n > 0:
        t += n
        n -= 2
    return f"total = 0\nn = {n0}\nwhile n > 0:\n    total += n\n    n -= 2\ntotal", t, f"Adds {n0}, {n0 - 2}, ... while n is above 0."


# ═══ 6. Comprehension Result ════════════════════════════════════════════

COMP: list[Maker] = []
_c = _register(COMP)


def _short(rng: random.Random, n: int) -> list[str]:
    return rng.sample([w for w in WORDS if len(w) <= 5], n)


def _is_prime(n: int) -> bool:
    d = 2
    while d < n:
        if fmod(n, d) == 0:
            return False
        d += 1
    return n >= 2


@_c
def comp_times(rng):
    xs, k = _digits(rng, rng.randint(3, 5)), rng.randint(2, 5)
    return f"xs = {lit(xs)}\n[x * {k} for x in xs]", [x * k for x in xs], f"One result per item: each times {k}."


@_c
def comp_filter(rng):
    xs, t = _digits(rng, rng.randint(5, 6)), rng.randint(3, 6)
    return f"xs = {lit(xs)}\n[x for x in xs if x > {t}]", [x for x in xs if x > t], f"The if keeps only the items above {t}."


@_c
def comp_squares(rng):
    a = rng.randint(1, 3)
    b = a + rng.randint(3, 5)
    return f"[x * x for x in range({a}, {b})]", [x * x for x in _prange(a, b)], f"The squares of {a} to {b - 1}."


@_c
def comp_range_even(rng):
    a = rng.randint(0, 3)
    b = a + rng.randint(6, 10)
    return f"[x for x in range({a}, {b}) if x % 2 == 0]", [x for x in _prange(a, b) if fmod(x, 2) == 0], "The even numbers in the range."


@_c
def comp_range_double(rng):
    n = rng.randint(3, 6)
    return f"[i * 2 for i in range({n})]", [i * 2 for i in _prange(0, n)], f"0 to {n - 1}, doubled."


@_c
def comp_odd_plus(rng):
    xs = _digits(rng, rng.randint(5, 6))
    return f"xs = {lit(xs)}\n[x + 1 for x in xs if x % 2 == 1]", [x + 1 for x in xs if fmod(x, 2) == 1], "Only the odd items are kept, then each gets 1 added."


@_c
def comp_lengths(rng):
    ws = rng.sample(WORDS, rng.randint(3, 5))
    return f"[len(w) for w in {lit(ws)}]", [len(w) for w in ws], "The length of each word."


@_c
def comp_first_letters(rng):
    ws = _short(rng, rng.randint(3, 4))
    return f"[w[0] for w in {lit(ws)}]", [w[0] for w in ws], "The first letter of each word, as a list of one-letter strings."


@_c
def comp_join_first(rng):
    ws = rng.sample(WORDS, rng.randint(3, 5))
    return f'"".join(w[0] for w in {lit(ws)})', "".join(w[0] for w in ws), "A generator of first letters, joined into one string."


@_c
def comp_dict_squares(rng):
    n = rng.randint(3, 5)
    return f"{{x: x * x for x in range(1, {n + 1})}}", {x: x * x for x in _prange(1, n + 1)}, "A dict comprehension: each x is a key, its square the value."


@_c
def comp_dict_lengths(rng):
    ws = _short(rng, rng.randint(2, 3))
    return f"{{w: len(w) for w in {lit(ws)}}}", {w: len(w) for w in ws}, "Each word is a key and its length the value."


@_c
def comp_set_len(rng):
    xs = _digits(rng, rng.randint(5, 7), 1, 5)
    return f"xs = {lit(xs)}\nlen({{x for x in xs}})", len(set(xs)), "A set keeps each value once: len counts the different values."


@_c
def comp_sorted_set_mod(rng):
    xs, k = _digits(rng, rng.randint(5, 7)), rng.randint(3, 4)
    seen = sorted({fmod(x, k) for x in xs})
    return f"xs = {lit(xs)}\nsorted({{x % {k} for x in xs}})", seen, f"The different remainders after dividing by {k}, in order."


@_c
def comp_sum_squares(rng):
    xs = _digits(rng, rng.randint(3, 5))
    t = 0
    for x in xs:
        t += x * x
    return f"xs = {lit(xs)}\nsum(x * x for x in xs)", t, "sum adds up the squares the generator hands over."


@_c
def comp_sum_count(rng):
    xs, t = _digits(rng, rng.randint(5, 6)), rng.randint(3, 6)
    return f"xs = {lit(xs)}\nsum(1 for x in xs if x > {t})", len([x for x in xs if x > t]), f"A 1 for every item above {t}: a count."


@_c
def comp_max_mod(rng):
    xs, k = _digits(rng, rng.randint(4, 5)), rng.randint(3, 5)
    return f"xs = {lit(xs)}\nmax(x % {k} for x in xs)", max(fmod(x, k) for x in xs), f"The biggest remainder after dividing by {k}."


@_c
def comp_conditional(rng):
    xs, t = _digits(rng, rng.randint(4, 6)), rng.randint(3, 6)
    return f"xs = {lit(xs)}\n[x if x > {t} else 0 for x in xs]", [x if x > t else 0 for x in xs], "The condition before for picks each result: small items become 0."


@_c
def comp_even_odd_words(rng):
    xs = _digits(rng, rng.randint(3, 4))
    return (f'xs = {lit(xs)}\n["even" if x % 2 == 0 else "odd" for x in xs]', ["even" if fmod(x, 2) == 0 else "odd" for x in xs],
            "One word per item, chosen by the if/else.")


@_c
def comp_zip_mul(rng):
    n = rng.randint(3, 4)
    xs, ys = _digits(rng, n), _digits(rng, n)
    return f"xs = {lit(xs)}\nys = {lit(ys)}\n[a * b for a, b in zip(xs, ys)]", [xs[i] * ys[i] for i in range(n)], "zip pairs the items at the same position."


@_c
def comp_zip_diff(rng):
    n = rng.randint(3, 4)
    xs, ys = _digits(rng, n), _digits(rng, n)
    return f"xs = {lit(xs)}\nys = {lit(ys)}\n[a - b for a, b in zip(xs, ys)]", [xs[i] - ys[i] for i in range(n)], "Each pair is subtracted: the result may go negative."


@_c
def comp_two_for(rng):
    a, b = rng.randint(2, 3), rng.randint(2, 3)
    out = []
    for i in range(1, a + 1):
        for j in range(1, b + 1):
            out.append(i * j)
    return f"[i * j for i in range(1, {a + 1}) for j in range(1, {b + 1})]", out, "Two fors work like nested loops: the right one is the inner loop."


@_c
def comp_nested_lists(rng):
    n = rng.randint(3, 4)
    return f"[[j for j in range(i)] for i in range({n})]", [_prange(0, i) for i in range(n)], "An inner comprehension builds each row: row i is 0 to i - 1."


@_c
def comp_first_column(rng):
    grid = [_digits(rng, 3) for _ in range(rng.randint(2, 4))]
    return f"grid = {lit(grid)}\n[row[0] for row in grid]", [row[0] for row in grid], "The first item of every row."


@_c
def comp_flatten(rng):
    grid = [_digits(rng, 2) for _ in range(rng.randint(2, 3))]
    return f"grid = {lit(grid)}\n[x for row in grid for x in row]", [x for row in grid for x in row], "Rows first, then the items of each row: the grid flattened."


@_c
def comp_row_sums(rng):
    grid = [_digits(rng, 3) for _ in range(rng.randint(2, 3))]
    sums = []
    for row in grid:
        t = 0
        for x in row:
            t += x
        sums.append(t)
    return f"grid = {lit(grid)}\n[sum(row) for row in grid]", sums, "One sum per row."


@_c
def comp_dict_zip(rng):
    ks = _short(rng, 3)
    vs = _digits(rng, 3)
    return f"{{k: v for k, v in zip({lit(ks)}, {lit(vs)})}}", dict(zip(ks, vs)), "zip pairs each key with the value at its position."


@_c
def comp_dict_dupes(rng):
    xs = _digits(rng, rng.randint(4, 5), 1, 4)
    out = {}
    for x in xs:
        out[x] = fmod(x, 3)
    return f"{{x: x % 3 for x in {lit(xs)}}}", out, "A repeated key just overwrites the earlier one, so each key appears once."


@_c
def comp_dict_invert(rng):
    ks = _short(rng, 3)
    vs = ints(rng, 3)
    d = ", ".join(f'"{k}": {v}' for k, v in zip(ks, vs))
    return f"d = {{{d}}}\n{{v: k for k, v in d.items()}}", {v: k for k, v in zip(ks, vs)}, "Keys and values swap places."


@_c
def comp_dict_filter_keys(rng):
    ks = _short(rng, 4)
    vs = _digits(rng, 4)
    t = rng.randint(3, 6)
    d = ", ".join(f'"{k}": {v}' for k, v in zip(ks, vs))
    return f"d = {{{d}}}\n[k for k in d if d[k] > {t}]", [k for k, v in zip(ks, vs) if v > t], f"The keys whose value is above {t}."


@_c
def comp_count_equal(rng):
    xs, v = _digits(rng, 6, 1, 4), rng.randint(1, 4)
    return f"xs = {lit(xs)}\nlen([x for x in xs if x == {v}])", len([x for x in xs if x == v]), f"How many items equal {v}."


@_c
def comp_consonants(rng):
    w = _word(rng, 4, 7)
    return f'"".join([c for c in "{w}" if c not in "aeiou"])', "".join([c for c in w if c not in _VOWELS]), "The vowels are filtered out."


@_c
def comp_double_chars(rng):
    w = _word(rng, 3, 5)
    return f'"".join(c * 2 for c in "{w}")', "".join(c * 2 for c in w), "Each letter appears twice."


@_c
def comp_vowels_list(rng):
    w = rng.choice([x for x in WORDS if len(x) >= 5])
    return f'[c for c in "{w}" if c in "aeiou"]', [c for c in w if c in _VOWELS], "The vowels, in the order they appear."


@_c
def comp_mod_set(rng):
    n, k = rng.randint(6, 12), rng.randint(3, 5)
    return f"sorted({{x % {k} for x in range({n})}})", sorted({fmod(x, k) for x in _prange(0, n)}), f"Every remainder 0 to {k - 1} turns up, once."


@_c
def comp_fizz(rng):
    n = rng.randint(10, 16)
    return (f"[x for x in range({n}) if x % 3 == 0 or x % 5 == 0]", [x for x in _prange(0, n) if fmod(x, 3) == 0 or fmod(x, 5) == 0],
            "Multiples of 3 or of 5 (0 counts as both).")


@_c
def comp_double_filter(rng):
    xs, t = _digits(rng, rng.randint(5, 6)), rng.randint(3, 6)
    return f"xs = {lit(xs)}\n[x * 2 for x in xs if x > {t}]", [x * 2 for x in xs if x > t], "Filter first (the if), then double what is left."


@_c
def comp_primes(rng):
    lim = rng.randint(10, 22)
    return (f"[n for n in range(2, {lim}) if all(n % d for d in range(2, n))]", [n for n in _prange(2, lim) if _is_prime(n)],
            "all(...) is True when no d from 2 up divides n: the primes.")


@_c
def comp_any(rng):
    xs, t = _digits(rng, rng.randint(4, 5)), rng.randint(5, 9)
    return f"xs = {lit(xs)}\nany(x > {t} for x in xs)", any(x > t for x in xs), f"True if at least one item is above {t}."


@_c
def comp_all(rng):
    xs, t = _digits(rng, rng.randint(4, 5), 2, 9), rng.randint(2, 4)
    return f"xs = {lit(xs)}\nall(x > {t} for x in xs)", all(x > t for x in xs), f"True only if every item is above {t}."


@_c
def comp_indexes(rng):
    xs, t = _digits(rng, rng.randint(5, 6)), rng.randint(3, 6)
    return f"xs = {lit(xs)}\n[i for i, x in enumerate(xs) if x > {t}]", [i for i in range(len(xs)) if xs[i] > t], f"The positions (not the values) of items above {t}."


@_c
def comp_not_in(rng):
    xs, ys = _digits(rng, 6, 1, 6), _digits(rng, 3, 1, 6)
    return f"xs = {lit(xs)}\nys = {lit(ys)}\n[x for x in xs if x not in ys]", [x for x in xs if x not in ys], "Items of xs that ys does not contain."


@_c
def comp_in(rng):
    xs, ys = _digits(rng, 6, 1, 6), _digits(rng, 3, 1, 6)
    return f"xs = {lit(xs)}\nys = {lit(ys)}\n[x for x in xs if x in ys]", [x for x in xs if x in ys], "Items of xs that ys also contains; repeats stay."


@_c
def comp_dict_even_squares(rng):
    xs = rng.sample(range(1, 10), rng.randint(4, 5))
    return f"{{x: x * x for x in {lit(xs)} if x % 2 == 0}}", {x: x * x for x in xs if fmod(x, 2) == 0}, "Only even x make it into the dict."


@_c
def comp_pairs_times(rng):
    xs = _digits(rng, rng.randint(2, 3))
    out = []
    for x in xs:
        for y in (1, 10):
            out.append(x * y)
    return f"xs = {lit(xs)}\n[x * y for x in xs for y in (1, 10)]", out, "For each x, y takes 1 then 10."


@_c
def comp_nested_comp(rng):
    xs, t = _digits(rng, rng.randint(4, 5)), rng.randint(6, 12)
    return f"xs = {lit(xs)}\n[y for y in [x * 2 for x in xs] if y > {t}]", [y for y in [x * 2 for x in xs] if y > t], "Double first (the inner list), then keep what is over the limit."


@_c
def comp_first_letter_set(rng):
    ws = rng.sample(WORDS, 5)
    return f"len({{w[0] for w in {lit(ws)}}})", len({w[0] for w in ws}), "Different first letters: a set drops the repeats."


@_c
def comp_enumerate_dict(rng):
    ws = _short(rng, 3)
    return f"{{w: i for i, w in enumerate({lit(ws)})}}", {w: i for i, w in enumerate(ws)}, "enumerate numbers the words from 0."


@_c
def comp_above_first(rng):
    xs = _digits(rng, rng.randint(5, 6))
    return f"xs = {lit(xs)}\n[x for x in xs if x > xs[0]]", [x for x in xs if x > xs[0]], "Compared with the first item, which is not special inside the loop."


@_c
def comp_digits_list(rng):
    num = str(rng.randint(1000, 9999))
    return f'[int(c) for c in "{num}"]', [int(c) for c in num], "int(c) turns each digit character into a number."


@_c
def comp_digit_sum(rng):
    n = rng.randint(100, 99999)
    return f"sum(int(c) for c in str({n}))", sum(int(c) for c in str(n)), "str() gives the digits as characters; int() and sum add them."


@_c
def comp_str_range(rng):
    n = rng.randint(3, 5)
    return f"[str(i) for i in range({n})]", [str(i) for i in range(n)], "str(i) is text, so the list shows quotes."


@_c
def comp_floor_half(rng):
    xs = _digits(rng, rng.randint(4, 6))
    return f"xs = {lit(xs)}\n[x // 2 for x in xs]", [fdiv(x, 2) for x in xs], "Each item halved and rounded down."


@_c
def comp_mod_list(rng):
    xs, k = _digits(rng, rng.randint(4, 6)), rng.randint(3, 4)
    return f"xs = {lit(xs)}\n[x % {k} for x in xs]", [fmod(x, k) for x in xs], f"The remainder of each item divided by {k}."


@_c
def comp_sum_filtered_range(rng):
    n, k = rng.randint(8, 14), rng.randint(2, 4)
    t = 0
    for x in range(n):
        if fmod(x, k) == 0:
            t += x
    return f"sum([x for x in range({n}) if x % {k} == 0])", t, f"Adds the multiples of {k} below {n}."


# ═══ 7. Enumerate Zip ═══════════════════════════════════════════════════

ENUM: list[Maker] = []
_e = _register(ENUM)


def _sorted_by(items: list, key) -> list:
    """sorted(items, key=key): a stable insertion sort, by hand."""
    out: list = []
    for x in items:
        k = len(out)
        while k > 0 and key(out[k - 1]) > key(x):
            k -= 1
        out.insert(k, x)
    return out


@_e
def en_pairs(rng):
    xs = _digits(rng, rng.randint(3, 4))
    return f"xs = {lit(xs)}\nlist(enumerate(xs))", [(i, xs[i]) for i in range(len(xs))], "enumerate pairs each item with its position, from 0."


@_e
def en_start(rng):
    xs = _digits(rng, rng.randint(3, 4))
    s = rng.randint(1, 5)
    return f"xs = {lit(xs)}\nlist(enumerate(xs, {s}))", [(s + i, xs[i]) for i in range(len(xs))], f"The numbering starts at {s} instead of 0."


@_e
def en_weighted(rng):
    xs = _digits(rng, rng.randint(3, 4))
    t = 0
    for i in range(len(xs)):
        t += i * xs[i]
    return f"xs = {lit(xs)}\ntotal = 0\nfor i, x in enumerate(xs):\n    total += i * x\ntotal", t, "i is the position, x the item: each is weighted by its position."


@_e
def en_last_big(rng):
    xs, t = _digits(rng, rng.randint(5, 6)), rng.randint(3, 6)
    idx = -1
    for i in range(len(xs)):
        if xs[i] > t:
            idx = i
    return (f"xs = {lit(xs)}\nidx = -1\nfor i, x in enumerate(xs):\n    if x > {t}:\n        idx = i\nidx", idx,
            f"idx is replaced by every position holding an item above {t}, so the last one wins.")


@_e
def en_diagonal_letters(rng):
    ws = rng.sample([w for w in WORDS if len(w) >= 4], 3)
    out = ""
    for i in range(len(ws)):
        out += ws[i][i]
    return f'"".join(w[i] for i, w in enumerate({lit(ws)}))', out, "Letter 0 of the first word, letter 1 of the second, ..."


@_e
def en_zip_pairs(rng):
    xs, ys = _digits(rng, rng.randint(3, 4)), _digits(rng, rng.randint(3, 4))
    n = min(len(xs), len(ys))
    return f"list(zip({lit(xs)}, {lit(ys)}))", [(xs[i], ys[i]) for i in range(n)], "zip pairs by position and stops at the shorter list."


@_e
def en_zip_short(rng):
    xs, ys = _digits(rng, 4), _digits(rng, 2)
    return f"list(zip({lit(xs)}, {lit(ys)}))", [(xs[i], ys[i]) for i in range(2)], "The shorter list decides how many pairs there are."


@_e
def en_zip_dot(rng):
    n = rng.randint(2, 4)
    xs, ys = _digits(rng, n), _digits(rng, n)
    t = 0
    for i in range(n):
        t += xs[i] * ys[i]
    return f"xs = {lit(xs)}\nys = {lit(ys)}\ntotal = 0\nfor a, b in zip(xs, ys):\n    total += a * b\ntotal", t, "Multiply the pair, add it in."


@_e
def en_dict_zip(rng):
    ks, vs = _short(rng, 3), _digits(rng, 3)
    return f"dict(zip({lit(ks)}, {lit(vs)}))", dict(zip(ks, vs)), "Keys from the first list, values from the second."


@_e
def en_reversed_list(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"xs = {lit(xs)}\nlist(reversed(xs))", xs[::-1], "reversed walks from the last item to the first."


@_e
def en_reversed_loop(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"xs = {lit(xs)}\nout = []\nfor x in reversed(xs):\n    out.append(x * 2)\nout", [x * 2 for x in xs[::-1]], "Last item first, each doubled."


@_e
def en_sorted(rng):
    xs = _digits(rng, rng.randint(4, 6))
    return f"sorted({lit(xs)})", _sorted_by(xs, lambda x: x), "sorted gives a new list, smallest first."


@_e
def en_sorted_desc(rng):
    xs = _digits(rng, rng.randint(4, 6))
    return f"sorted({lit(xs)}, reverse=True)", _sorted_by(xs, lambda x: x)[::-1], "reverse=True puts the biggest first."


@_e
def en_sorted_words(rng):
    ws = rng.sample(WORDS, rng.randint(3, 4))
    return f"sorted({lit(ws)})", _sorted_by(ws, lambda w: w), "Words sort alphabetically."


@_e
def en_sorted_first_word(rng):
    ws = rng.sample(WORDS, 4)
    return f"sorted({lit(ws)})[0]", _sorted_by(ws, lambda w: w)[0], "The alphabetically first word."


@_e
def en_sorted_key_len(rng):
    ws = rng.sample(WORDS, 4)
    return f"sorted({lit(ws)}, key=len)", _sorted_by(ws, len), "Sorted by length; words of equal length keep their original order."


@_e
def en_longest(rng):
    ws = rng.sample(WORDS, 4)
    return f"sorted({lit(ws)}, key=len)[-1]", _sorted_by(ws, len)[-1], "The last after sorting by length: a longest word (the later one of a tie)."


@_e
def en_shortest(rng):
    ws = rng.sample(WORDS, 4)
    return f"sorted({lit(ws)}, key=len)[0]", _sorted_by(ws, len)[0], "The first after sorting by length: a shortest word (the earlier one of a tie)."


@_e
def en_key_last_letter(rng):
    ws = rng.sample(WORDS, 4)
    return f"sorted({lit(ws)}, key=lambda w: w[-1])", _sorted_by(ws, lambda w: w[-1]), "Sorted by each word's last letter; ties keep their order."


@_e
def en_diffs_index(rng):
    xs = _digits(rng, rng.randint(4, 5))
    return (f"xs = {lit(xs)}\nout = []\nfor i in range(len(xs) - 1):\n    out.append(xs[i + 1] - xs[i])\nout", [xs[i + 1] - xs[i] for i in range(len(xs) - 1)],
            "Each item minus the one before it: one fewer result than items.")


@_e
def en_diffs_zip(rng):
    xs = _digits(rng, rng.randint(4, 5))
    return f"xs = {lit(xs)}\n[b - a for a, b in zip(xs, xs[1:])]", [xs[i + 1] - xs[i] for i in range(len(xs) - 1)], "zip(xs, xs[1:]) pairs each item with the next one."


@_e
def en_vowel_positions(rng):
    w = rng.choice([x for x in WORDS if len(x) >= 5])
    out = []
    for i, c in enumerate(w):
        if c in _VOWELS:
            out.append(i)
    return f'out = []\nfor i, c in enumerate("{w}"):\n    if c in "aeiou":\n        out.append(i)\nout', out, "The positions of the vowels, counting from 0."


@_e
def en_even_positions(rng):
    xs = _digits(rng, rng.randint(4, 6))
    t = 0
    for i in range(len(xs)):
        if fmod(i, 2) == 0:
            t += xs[i]
    return f"xs = {lit(xs)}\ntotal = 0\nfor i, x in enumerate(xs):\n    if i % 2 == 0:\n        total += x\ntotal", t, "Adds the items at positions 0, 2, 4 ..."


@_e
def en_odd_positions(rng):
    xs = _digits(rng, rng.randint(4, 6))
    t = 0
    for i in range(len(xs)):
        if fmod(i, 2) == 1:
            t += xs[i]
    return f"xs = {lit(xs)}\nsum(x for i, x in enumerate(xs) if i % 2)", t, "i % 2 is 1 (true) at positions 1, 3, 5 ..."


@_e
def en_numbered(rng):
    ws = _short(rng, 3)
    out = ""
    for i in range(len(ws)):
        out += str(i + 1) + ws[i][0]
    return f'out = ""\nfor i, w in enumerate({lit(ws)}, 1):\n    out += f"{{i}}{{w[0]}}"\nout', out, "Numbering from 1: the number, then the first letter."


@_e
def en_argmax(rng):
    xs = ints(rng, rng.randint(4, 6))
    best = 0
    for i in range(len(xs)):
        if xs[i] > xs[best]:
            best = i
    return f"xs = {lit(xs)}\nmax(range(len(xs)), key=lambda i: xs[i])", best, "The index whose item is biggest."


@_e
def en_index_of_max(rng):
    xs = ints(rng, rng.randint(4, 6))
    best = 0
    for i in range(len(xs)):
        if xs[i] > xs[best]:
            best = i
    return f"xs = {lit(xs)}\nxs.index(max(xs))", best, "max finds the value, index finds where it sits."


@_e
def en_dict_keys_loop(rng):
    ks = _short(rng, 3)
    d = ", ".join(f'"{k}": {i}' for i, k in enumerate(ks))
    out = ""
    for k in ks:
        out += k[0]
    return f'd = {{{d}}}\nout = ""\nfor k in d:\n    out += k[0]\nout', out, "Looping over a dict gives its keys, in the order they were written."


@_e
def en_dict_items_sum(rng):
    ks, vs = _short(rng, 3), _digits(rng, 3)
    d = ", ".join(f'"{k}": {v}' for k, v in zip(ks, vs))
    t = 0
    for v in vs:
        t += v
    return f"d = {{{d}}}\ntotal = 0\nfor k, v in d.items():\n    total += v\ntotal", t, ".items() gives (key, value) pairs; only the values are added."


@_e
def en_dict_items_filter(rng):
    ks, vs = _short(rng, 4), _digits(rng, 4)
    t = rng.randint(3, 6)
    vs[rng.randrange(4)] = 9
    d = ", ".join(f'"{k}": {v}' for k, v in zip(ks, vs))
    out = ""
    for k, v in zip(ks, vs):
        if v > t:
            out += k[0]
    return (f'd = {{{d}}}\nout = ""\nfor k, v in d.items():\n    if v > {t}:\n        out += k[0]\nout', out,
            f"The first letters of the keys whose value is above {t}.")


@_e
def en_items_first(rng):
    ks, vs = _short(rng, 3), _digits(rng, 3)
    d = ", ".join(f'"{k}": {v}' for k, v in zip(ks, vs))
    return f"d = {{{d}}}\nlist(d.items())[0]", (ks[0], vs[0]), "The first (key, value) pair, as a tuple."


@_e
def en_zip_max(rng):
    n = rng.randint(3, 4)
    xs, ys = _digits(rng, n), _digits(rng, n)
    return f"xs = {lit(xs)}\nys = {lit(ys)}\n[max(a, b) for a, b in zip(xs, ys)]", [max(xs[i], ys[i]) for i in range(n)], "The bigger of each pair."


@_e
def en_interleave(rng):
    w1, w2 = rng.sample([w for w in WORDS if len(w) >= 3], 2)
    n = min(len(w1), len(w2))
    out = "".join(w1[i] + w2[i] for i in range(n))
    return f'"".join(a + b for a, b in zip("{w1}", "{w2}"))', out, "Letters are taken in pairs - one from each - until the shorter word ends."


@_e
def en_reversed_enumerate(rng):
    xs = _digits(rng, rng.randint(3, 4))
    t = 0
    for i, x in enumerate(xs[::-1]):
        t += i * x
    return f"xs = {lit(xs)}\ntotal = 0\nfor i, x in enumerate(reversed(xs)):\n    total += i * x\ntotal", t, "The position counts in the reversed order, so the last item has i = 0."


@_e
def en_char_pair(rng):
    w = _word(rng, 4, 6)
    k = rng.randint(0, len(w) - 1)
    return f'list(enumerate("{w}"))[{k}]', (k, w[k]), "enumerate over a string pairs positions with letters."


@_e
def en_first_big_index(rng):
    xs = _digits(rng, rng.randint(5, 6), 1, 6)
    xs[rng.randint(1, len(xs) - 1)] = rng.randint(8, 9)
    t = 7
    for i in range(len(xs)):
        if xs[i] > t:
            first = i
            break
    return f"xs = {lit(xs)}\nnext(i for i, x in enumerate(xs) if x > {t})", first, f"next takes the first position whose item is above {t}."


@_e
def en_zip_range(rng):
    ks = _short(rng, 2)
    return f"list(zip({lit(ks)}, range(10, 100, 10)))", [(ks[i], 10 * (i + 1)) for i in range(2)], "zip stops at the shorter one: the two words."


@_e
def en_count_bigger(rng):
    n = rng.randint(4, 5)
    xs, ys = _digits(rng, n), _digits(rng, n)
    c = 0
    for a, b in zip(xs, ys):
        if a > b:
            c += 1
    return f"xs = {lit(xs)}\nys = {lit(ys)}\ncount = 0\nfor a, b in zip(xs, ys):\n    if a > b:\n        count += 1\ncount", c, "Counts the positions where xs beats ys."


@_e
def en_median(rng):
    xs = _digits(rng, rng.choice((3, 5, 7)))
    s = _sorted_by(xs, lambda x: x)
    return f"xs = {lit(xs)}\nsorted(xs)[len(xs) // 2]", s[fdiv(len(xs), 2)], "Sort, then take the middle item."


@_e
def en_second_largest(rng):
    xs = _digits(rng, rng.randint(4, 6))
    return f"xs = {lit(xs)}\nsorted(xs)[-2]", _sorted_by(xs, lambda x: x)[-2], "Second from the end of the sorted list (a repeated biggest counts twice)."


@_e
def en_sorted_set(rng):
    xs = _digits(rng, rng.randint(5, 7), 1, 6)
    uniq: list[int] = []
    for x in xs:
        if x not in uniq:
            uniq.append(x)
    return f"xs = {lit(xs)}\nsorted(set(xs))", _sorted_by(uniq, lambda x: x), "set removes repeats; sorted puts the rest in order."


@_e
def en_range_len_reverse(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"xs = {lit(xs)}\nout = []\nfor i in reversed(range(len(xs))):\n    out.append(xs[i])\nout", xs[::-1], "i runs from the last index down to 0."


@_e
def en_join_reversed(rng):
    ws = rng.sample(WORDS, rng.randint(3, 4))
    return f'"-".join(reversed({lit(ws)}))', "-".join(ws[::-1]), "The words, last to first, joined with dashes."


@_e
def en_join_sorted(rng):
    ws = rng.sample(WORDS, rng.randint(3, 4))
    return f'" ".join(sorted({lit(ws)}))', " ".join(_sorted_by(ws, lambda w: w)), "Alphabetical order, joined with spaces."


@_e
def en_match_position(rng):
    n = rng.randint(4, 5)
    xs, ys = _digits(rng, n, 1, 4), _digits(rng, n, 1, 4)
    pos = -1
    for i in range(n):
        if xs[i] == ys[i]:
            pos = i
    return (f"xs = {lit(xs)}\nys = {lit(ys)}\npos = -1\nfor i, (a, b) in enumerate(zip(xs, ys)):\n    if a == b:\n        pos = i\npos", pos,
            "The last position where both lists hold the same value, or -1.")


@_e
def en_map_sum(rng):
    n = rng.randint(3, 4)
    xs, ys = _digits(rng, n), _digits(rng, n)
    return f"xs = {lit(xs)}\nys = {lit(ys)}\nlist(map(sum, zip(xs, ys)))", [xs[i] + ys[i] for i in range(n)], "Each pair from zip is summed."


@_e
def en_dict_enumerate(rng):
    ws = _short(rng, 3)
    return f"dict(enumerate({lit(ws)}))", {i: ws[i] for i in range(3)}, "enumerate gives (position, word) pairs, which dict turns into keys and values."


@_e
def en_zip_three(rng):
    n = rng.randint(2, 3)
    xs, ys, zs = _digits(rng, n), _digits(rng, n), _digits(rng, n)
    return f"list(zip({lit(xs)}, {lit(ys)}, {lit(zs)}))", [(xs[i], ys[i], zs[i]) for i in range(n)], "zip takes any number of lists: one triple per position."


@_e
def en_sorted_pairs(rng):
    n = rng.randint(3, 4)
    xs, ys = _digits(rng, n, 1, 4), _digits(rng, n)
    pairs = [(xs[i], ys[i]) for i in range(n)]
    return f"sorted(zip({lit(xs)}, {lit(ys)}))[0]", _sorted_by(pairs, lambda p: p)[0], "Pairs compare by the first value, then by the second if the first ties."


@_e
def en_sorted_abs(rng):
    xs = [rng.choice((-1, 1)) * rng.randint(1, 6) for _ in range(rng.randint(4, 5))]
    return f"sorted({lit(xs)}, key=abs)", _sorted_by(xs, abs), "Sorted by size without the sign; equal sizes keep their order."


# ═══ 8. Loop Variable After ═════════════════════════════════════════════

AFTER: list[Maker] = []
_a = _register(AFTER)


def _remove_first(xs: list, v) -> None:
    """xs.remove(v): delete the first item equal to v."""
    for k in range(len(xs)):
        if xs[k] == v:
            del xs[k:k + 1]
            return


@_a
def af_range_last(rng):
    n = rng.randint(2, 7)
    return f"for i in range({n}):\n    pass\ni", n - 1, f"range({n}) ends at {n - 1}, and i keeps that value after the loop."


@_a
def af_range_step_last(rng):
    a, s = rng.randint(0, 3), rng.randint(2, 4)
    b = a + rng.randint(3 * s, 5 * s)
    return f"for i in range({a}, {b}, {s}):\n    pass\ni", _prange(a, b, s)[-1], "i is the last value the range handed out."


@_a
def af_list_last(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"for x in {lit(xs)}:\n    pass\nx", xs[-1], "After the loop, x is still the last item."


@_a
def af_letter_last(rng):
    w = _word(rng)
    return f'for ch in "{w}":\n    pass\nch', w[-1], "The loop variable stays on the last letter."


@_a
def af_empty_keeps(rng):
    v = rng.randint(10, 99)
    return f"i = {v}\nfor i in range(0):\n    pass\ni", v, "The loop never runs, so i is never reassigned."


@_a
def af_empty_list_keeps(rng):
    v = rng.randint(10, 99)
    return f"x = {v}\nfor x in []:\n    pass\nx", v, "Nothing to loop over: x keeps its old value."


@_a
def af_overwrites(rng):
    xs = _digits(rng, rng.randint(3, 4))
    v = rng.randint(10, 99)
    return f"x = {v}\nfor x in {lit(xs)}:\n    pass\nx", xs[-1], "The loop assigns to x on every turn, wiping out the old value."


@_a
def af_break_var(rng):
    k, t = rng.randint(2, 5), rng.randint(8, 25)
    last = None
    for i in range(10):
        last = i
        if i * k > t:
            break
    return f"for i in range(10):\n    if i * {k} > {t}:\n        break\ni", last, f"The loop stops at the first i with i * {k} over {t}; i stays there."


@_a
def af_no_break_var(rng):
    k = rng.randint(2, 4)
    n = rng.randint(3, 6)
    last = None
    for i in range(n):
        last = i
        if i * k > 100:
            break
    return f"for i in range({n}):\n    if i * {k} > 100:\n        break\ni", last, "The condition is never true, so there is no break: i ends at the last value."


@_a
def af_var_and_total(rng):
    n = rng.randint(3, 6)
    t = 0
    for i in range(n):
        t += i
    return f"total = 0\nfor i in range({n}):\n    total += i\n[i, total]", [n - 1, t], "i ends at the last value; total is the sum of all the i."


@_a
def af_comp_no_leak(rng):
    v = rng.randint(10, 99)
    n = rng.randint(3, 5)
    return f"x = {v}\n[x for x in range({n})]\nx", v, "A comprehension has its own x: the outer x is not touched."


@_a
def af_comp_no_leak2(rng):
    v = rng.randint(10, 99)
    n = rng.randint(3, 5)
    return f"i = {v}\nsquares = [i * i for i in range({n})]\ni", v, "The i inside the comprehension does not leak out, unlike a for loop's."


@_a
def af_comp_result(rng):
    n = rng.randint(3, 5)
    return f"i = 0\nsquares = [i * i for i in range({n})]\nsquares[-1] + i", (n - 1) * (n - 1), "The comprehension's i is separate, so the outer i is still 0."


@_a
def af_double_in_place(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"xs = {lit(xs)}\nfor i in range(len(xs)):\n    xs[i] *= 2\nxs", [x * 2 for x in xs], "xs[i] assigns into the list, so the list itself changes."


@_a
def af_loop_var_copy(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"xs = {lit(xs)}\nfor x in xs:\n    x *= 2\nxs", xs, "x is a copy of each number: doubling it leaves the list alone."


@_a
def af_loop_var_plus(rng):
    xs = _digits(rng, rng.randint(3, 4))
    return f"xs = {lit(xs)}\nfor x in xs:\n    x = x + 100\nxs", xs, "Rebinding x never changes the list."


@_a
def af_inner_list_mutates(rng):
    grid = [_digits(rng, 2) for _ in range(rng.randint(2, 3))]
    return f"grid = {lit(grid)}\nfor row in grid:\n    row.append(0)\ngrid", [r + [0] for r in grid], "row IS the inner list, and append changes it in place."


@_a
def af_inner_list_rebind(rng):
    grid = [_digits(rng, 2) for _ in range(rng.randint(2, 3))]
    return f"grid = {lit(grid)}\nfor row in grid:\n    row = row + [0]\ngrid", grid, "row + [0] builds a new list; only the name row moves to it."


@_a
def af_reassign_var(rng):
    n = rng.randint(3, 5)
    m = rng.randint(2, 5)
    return f"for i in range({n}):\n    i = i * {m}\ni", (n - 1) * m, "The next turn replaces i anyway, but after the last turn i keeps what the body made."


@_a
def af_reassign_plus(rng):
    n = rng.randint(3, 5)
    return f"for i in range({n}):\n    i += 5\ni", n - 1 + 5, "Changing i inside does not change how many turns there are."


@_a
def af_range_once(rng):
    n = rng.randint(3, 5)
    return f"n = {n}\nfor i in range(n):\n    n += 1\nn", 2 * n, "range(n) was worked out once at the start: n turns, each adding 1."


@_a
def af_range_shadow(rng):
    n = rng.randint(4, 8)
    return f"n = {n}\nfor n in range(n):\n    pass\nn", n - 1, "range(n) is built first, then n is reused as the loop variable: it ends at n - 1."


@_a
def af_copy_remove_all(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"xs = {lit(xs)}\nfor x in list(xs):\n    xs.remove(x)\nxs", [], "The loop walks a copy, so removing from xs is safe: every item goes."


@_a
def af_remove_while_iter(rng):
    xs = rng.sample(range(1, 10), rng.randint(5, 6))
    ys = list(xs)
    i = 0
    while i < len(ys):
        x = ys[i]
        if fmod(x, 2) == 0:
            _remove_first(ys, x)
        i += 1
    return (f"xs = {lit(xs)}\nfor x in xs:\n    if x % 2 == 0:\n        xs.remove(x)\nxs", ys,
            "Removing shifts the next item into the spot just visited, so the loop skips it.")


@_a
def af_remove_big_while_iter(rng):
    xs = rng.sample(range(1, 10), rng.randint(5, 6))
    t = rng.randint(3, 6)
    ys = list(xs)
    i = 0
    while i < len(ys):
        x = ys[i]
        if x > t:
            _remove_first(ys, x)
        i += 1
    return (f"xs = {lit(xs)}\nfor x in xs:\n    if x > {t}:\n        xs.remove(x)\nxs", ys,
            "Each removal makes the loop jump over the item that slides into its place.")


@_a
def af_pop_while_iter(rng):
    xs = _digits(rng, rng.randint(4, 6))
    ys = list(xs)
    seen = []
    i = 0
    while i < len(ys):
        seen.append(ys[i])
        ys.pop()
        i += 1
    return f"xs = {lit(xs)}\nseen = []\nfor x in xs:\n    seen.append(x)\n    xs.pop()\nseen", seen, "The list shrinks from the end while the loop walks forward: they meet in the middle."


@_a
def af_pop_while_iter_left(rng):
    xs = _digits(rng, rng.randint(4, 6))
    ys = list(xs)
    i = 0
    while i < len(ys):
        ys.pop()
        i += 1
    return f"xs = {lit(xs)}\nfor x in xs:\n    xs.pop()\nxs", ys, "Each turn removes the last item, but the loop stops once its position passes the shrinking end."


@_a
def af_nested_vars(rng):
    a, b = rng.randint(2, 4), rng.randint(2, 4)
    return f"for i in range({a}):\n    for j in range({b}):\n        pass\n[i, j]", [a - 1, b - 1], "Each variable keeps the last value its own loop gave it."


@_a
def af_inner_empty_last(rng):
    n = rng.randint(3, 5)
    return (f"for i in range({n}):\n    for j in range({n} - 1 - i):\n        pass\nj", 0,
            "On the last turn the inner range is empty, so j still holds the value from the turn before: 0.")


@_a
def af_inner_triangle(rng):
    n = rng.randint(3, 6)
    return f"for i in range({n}):\n    for j in range(i):\n        pass\nj", n - 2, f"On the last turn i is {n - 1}, so j runs up to {n - 2}."


@_a
def af_dict_last_key(rng):
    ks = _short(rng, 3)
    d = ", ".join(f'"{k}": {i}' for i, k in enumerate(ks))
    return f"d = {{{d}}}\nfor k in d:\n    pass\nk", ks[-1], "A dict is looped in the order it was written; k ends on the last key."


@_a
def af_dict_last_value(rng):
    ks, vs = _short(rng, 3), _digits(rng, 3)
    d = ", ".join(f'"{k}": {v}' for k, v in zip(ks, vs))
    return f"d = {{{d}}}\nfor k, v in d.items():\n    pass\nv", vs[-1], "After the loop v is the last value."


@_a
def af_enumerate_end(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"xs = {lit(xs)}\nfor i, x in enumerate(xs):\n    pass\n[i, x]", [len(xs) - 1, xs[-1]], "Both variables stay at the last pair."


@_a
def af_zip_end(rng):
    xs, ys = _digits(rng, 4), _digits(rng, rng.randint(2, 3))
    n = len(ys)
    return f"xs = {lit(xs)}\nys = {lit(ys)}\nfor a, b in zip(xs, ys):\n    pass\n[a, b]", [xs[n - 1], ys[n - 1]], "zip stops with the shorter list, so the last pair is at its end."


@_a
def af_late_binding(rng):
    n = rng.randint(3, 4)
    return f"fns = []\nfor i in range({n}):\n    fns.append(lambda: i)\n[f() for f in fns]", [n - 1] * n, "Every lambda looks up i when it is called - after the loop, when i is the last value."


@_a
def af_default_binding(rng):
    n = rng.randint(3, 4)
    return f"fns = []\nfor i in range({n}):\n    fns.append(lambda i=i: i)\n[f() for f in fns]", list(range(n)), "A default argument is fixed when the lambda is made, so each keeps its own i."


@_a
def af_default_times(rng):
    n, k = rng.randint(3, 4), rng.randint(2, 5)
    return f"fns = []\nfor i in range({n}):\n    fns.append(lambda x=i: x * {k})\n[f() for f in fns]", [i * k for i in range(n)], "Each lambda captured its own i as x."


@_a
def af_late_comp(rng):
    n = rng.randint(3, 4)
    return f"[f() for f in [lambda: i for i in range({n})]]", [n - 1] * n, "The lambdas share one i, which is the last value by the time they run."


@_a
def af_two_loops(rng):
    a, b = rng.randint(2, 4), rng.randint(5, 8)
    return f"for i in range({a}):\n    pass\nfor i in range({b}, {b + 2}):\n    pass\ni", b + 1, "The second loop reuses i and leaves it at its own last value."


@_a
def af_iterate_original_str(rng):
    w = _word(rng, 3, 4)
    return f's = "{w}"\nfor ch in s:\n    s = s + "x"\ns', w + "x" * len(w), "The loop walks the original string; the new string does not change how many turns."


@_a
def af_iterate_original_list(rng):
    xs = _digits(rng, rng.randint(2, 3))
    return f"xs = {lit(xs)}\nfor x in xs:\n    xs = xs + [0]\nxs", xs + [0] * len(xs), "xs + [0] makes a new list each time; the loop keeps walking the first one."


@_a
def af_shared_row(rng):
    n = rng.randint(2, 3)
    full = _prange(0, n)
    return (f"grid = []\nrow = []\nfor i in range({n}):\n    row.append(i)\n    grid.append(row)\ngrid", [full for _ in range(n)],
            "grid holds the same list n times, so every row shows its final contents.")


@_a
def af_copied_row(rng):
    n = rng.randint(2, 3)
    return (f"grid = []\nrow = []\nfor i in range({n}):\n    row.append(i)\n    grid.append(list(row))\ngrid", [_prange(0, k + 1) for k in range(n)],
            "list(row) is a snapshot, so each row keeps what it had when it was added.")


@_a
def af_last_match(rng):
    xs, t = _digits(rng, rng.randint(4, 5)), rng.randint(5, 9)
    last = None
    for x in xs:
        if x > t:
            last = x
    return f"xs = {lit(xs)}\nlast = None\nfor x in xs:\n    if x > {t}:\n        last = x\nlast", last, f"last holds the final item above {t}, or None if there was none."


@_a
def af_add_index(rng):
    xs = _digits(rng, rng.randint(3, 4))
    return f"xs = {lit(xs)}\nfor i in range(len(xs)):\n    xs[i] = xs[i] + i\nxs", [xs[i] + i for i in range(len(xs))], "Each item gets its own position added, in place."


@_a
def af_swap_reverse(rng):
    xs = _digits(rng, rng.randint(4, 6))
    return (f"xs = {lit(xs)}\nfor i in range(len(xs) // 2):\n    xs[i], xs[-1 - i] = xs[-1 - i], xs[i]\nxs", xs[::-1],
            "Swapping the ends inward, half way, reverses the list in place.")


@_a
def af_first_letters_inplace(rng):
    ws = rng.sample(WORDS, 3)
    return f"ws = {lit(ws)}\nfor i in range(len(ws)):\n    ws[i] = ws[i][0]\nws", [w[0] for w in ws], "Each slot is replaced by its word's first letter."


@_a
def af_alias_grows(rng):
    xs = _digits(rng, 2)
    n = rng.randint(2, 3)
    return f"xs = {lit(xs)}\nys = xs\nfor i in range({n}):\n    xs.append(i)\nys", xs + _prange(0, n), "ys is the same list as xs, so it grows too."


@_a
def af_while_overshoot(rng):
    s, lim = rng.randint(3, 6), rng.randint(10, 20)
    i = 0
    while i < lim:
        i += s
    return f"i = 0\nwhile i < {lim}:\n    i += {s}\ni", i, f"i is not below {lim} when the loop ends: it overshoots in steps of {s}."


@_a
def af_name_in_range_loop(rng):
    n = rng.randint(3, 5)
    return f"for _ in range({n}):\n    pass\n_", n - 1, "_ is an ordinary variable name: it holds the last value too."


# ── END OF RANGE ──
