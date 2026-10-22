"""Loops pack, JavaScript side: the same eight activities with JavaScript's rules.

Every answer is modelled by hand (a `while` that walks the loop, an accumulator
updated in plain Python that stands for the JavaScript loop, `%` that keeps the
sign of the left side, the default sort that compares text) and
tests/test_brain_packs.py runs every template through the real node. The LAST
line of every item is the expression being asked about.
"""

from __future__ import annotations

import random

from ._loops_py import _digits, _prange, _word
from ._model import NULL, UNDEF, WORDS, Maker, fdiv, ints, js_show, tmod
from .items import Item


def _wrap(fn) -> Maker:
    """A template function that returns (code, answer, why) as a Maker that returns an Item."""
    def make(rng: random.Random) -> Item:
        code, answer, why = fn(rng)
        return Item(code, js_show(answer), why)
    make.__name__ = fn.__name__
    return make


def _register(table: list[Maker]):
    def deco(fn):
        table.append(_wrap(fn))
        return fn
    return deco


def _arr(v) -> str:
    """Source text for ints, strings and lists of them."""
    if isinstance(v, str):
        return '"' + v + '"'
    if isinstance(v, list):
        return "[" + ", ".join(_arr(x) for x in v) + "]"
    return str(v)


def _short(rng: random.Random, n: int) -> list[str]:
    return rng.sample([w for w in WORDS if len(w) <= 5], n)


def _fit(rng: random.Random, n: int) -> list[str]:
    """n different words whose array prints in at most 40 characters (the answer limit)."""
    while True:
        ws = rng.sample(WORDS, n)
        if sum(len(w) + 2 for w in ws) + 2 * (n - 1) + 4 <= 40:
            return ws


def _text_sorted(items: list) -> list:
    """The default .sort(): items compared as TEXT, by hand (an insertion sort on their text)."""
    out: list = []
    for x in items:
        k = len(out)
        while k > 0 and str(out[k - 1]) > str(x):
            k -= 1
        out.insert(k, x)
    return out


def _sorted_by(items: list, key) -> list:
    """A stable sort by key, by hand."""
    out: list = []
    for x in items:
        k = len(out)
        while k > 0 and key(out[k - 1]) > key(x):
            k -= 1
        out.insert(k, x)
    return out


_VOWELS = "aeiou"


# ═══ 1. Range Output ════════════════════════════════════════════════════

RANGE: list[Maker] = []
_r = _register(RANGE)


def _h_stop(rng):
    n = rng.randint(2, 6)
    return f"let i = 0; i < {n}; i++", _prange(0, n), f"i starts at 0 and stops before {n}."


def _h_start_stop(rng):
    a = rng.randint(1, 5)
    b = a + rng.randint(2, 5)
    return f"let i = {a}; i < {b}; i++", _prange(a, b), f"From {a} up to, not including, {b}."


def _h_step(rng):
    a, s = rng.randint(0, 4), rng.randint(2, 4)
    b = a + rng.randint(2 * s, 4 * s)
    return f"let i = {a}; i < {b}; i += {s}", _prange(a, b, s), f"Start at {a}, add {s} each time, stop before {b}."


def _h_down(rng):
    a, s = rng.randint(0, 3), rng.randint(1, 3)
    b = a + rng.randint(2 * s + 1, 4 * s)
    return f"let i = {b}; i > {a}; i -= {s}", _prange(b, a, -s), f"Start at {b}, take {s} off each time, stop before {a}."


def _h_inclusive(rng):
    n = rng.randint(2, 6)
    return f"let i = 1; i <= {n}; i++", _prange(1, n + 1), f"<= includes {n}, so the last value is {n}."


_HEADERS = (_h_stop, _h_start_stop, _h_step, _h_down, _h_inclusive)

_BODIES = (
    ("out.push(i)", lambda i: i, "each i itself"),
    ("out.push(i * 2)", lambda i: i * 2, "double each i"),
    ("out.push(i * i)", lambda i: i * i, "the square of each i"),
    ("out.push(i + 10)", lambda i: i + 10, "each i plus 10"),
    ("out.push(10 - i)", lambda i: 10 - i, "10 minus each i"),
    ("out.push(i % 3)", lambda i: tmod(i, 3), "the remainder of each i divided by 3"),
    ("out.push(Math.floor(i / 2))", lambda i: fdiv(i, 2), "each i halved, rounded down"),
)


def _loop_template(header, body) -> Maker:
    line, fn, what = body

    def make(rng: random.Random):
        head, vals, why = header(rng)
        code = f"const out = [];\nfor ({head}) {{\n  {line};\n}}\nout"
        return code, [fn(i) for i in vals], f"{why} The array collects {what}."
    make.__name__ = f"range_{header.__name__[3:]}_{line[9:-1].replace(' ', '')}"
    return _wrap(make)


for _h in _HEADERS:
    for _b in _BODIES:
        RANGE.append(_loop_template(_h, _b))


@_r
def range_keys(rng):
    n = rng.randint(2, 6)
    return f"[...Array({n}).keys()]", _prange(0, n), f"Array({n}).keys() are the positions 0 to {n - 1}."


@_r
def range_from_length(rng):
    n, k = rng.randint(3, 6), rng.randint(2, 5)
    return f"Array.from({{ length: {n} }}, (_, i) => i * {k})", [i * k for i in _prange(0, n)], f"{n} items, item i is i * {k}."


@_r
def range_from_offset(rng):
    a = rng.randint(1, 6)
    n = rng.randint(3, 5)
    return f"Array.from({{ length: {n} }}, (_, i) => {a} + i)", [a + i for i in _prange(0, n)], f"{n} items, counting up from {a}."


@_r
def range_from_step(rng):
    a, s, n = rng.randint(0, 4), rng.randint(2, 5), rng.randint(3, 5)
    return f"Array.from({{ length: {n} }}, (_, i) => {a} + i * {s})", [a + i * s for i in _prange(0, n)], f"{n} items starting at {a}, {s} apart."


@_r
def range_from_down(rng):
    n = rng.randint(3, 6)
    return f"Array.from({{ length: {n} }}, (_, i) => {n} - i)", [n - i for i in _prange(0, n)], f"{n} items counting down from {n}."


@_r
def range_keys_map(rng):
    n, k = rng.randint(3, 5), rng.randint(2, 4)
    return f"[...Array({n}).keys()].map(i => i + {k})", [i + k for i in _prange(0, n)], f"0 to {n - 1}, each plus {k}."


@_r
def range_keys_reverse(rng):
    n = rng.randint(3, 6)
    return f"[...Array({n}).keys()].reverse()", _prange(n - 1, -1, -1), "The positions, flipped."


@_r
def range_keys_filter(rng):
    n, k = rng.randint(6, 10), rng.choice((2, 3))
    return f"[...Array({n}).keys()].filter(i => i % {k} === 0)", [i for i in _prange(0, n) if tmod(i, k) == 0], f"Multiples of {k} below {n}."


@_r
def range_fill(rng):
    n, v = rng.randint(2, 5), rng.randint(1, 9)
    return f"Array({n}).fill({v})", [v] * n, f"{n} slots, every one set to {v}."


@_r
def range_from_text(rng):
    w = _word(rng, 3, 5)
    return f'Array.from("{w}")', list(w), "Array.from on a string gives one item per letter."


@_r
def range_split_chars(rng):
    w = _word(rng, 3, 5)
    return f'"{w}".split("")', list(w), 'split("") cuts between every character.'


@_r
def range_length(rng):
    n = rng.randint(3, 9)
    return f"Array.from({{ length: {n} }}).length", n, f"{n} slots (each undefined), so the length is {n}."


@_r
def range_from_undefined(rng):
    n = rng.randint(2, 3)
    return f"Array.from({{ length: {n} }})", "[ " + ", ".join(["undefined"] * n) + " ]", "The slots are filled with undefined."


@_r
def range_join(rng):
    h, vals, why = rng.choice(_HEADERS)(rng)
    return f'const out = [];\nfor ({h}) {{\n  out.push(i);\n}}\nout.join("-")', "-".join(str(v) for v in vals), why + " join glues the numbers with dashes."


@_r
def range_join_comma(rng):
    a = rng.randint(1, 4)
    b = a + rng.randint(3, 5)
    return f"Array.from({{ length: {b - a} }}, (_, i) => {a} + i).join(\"\")", "".join(str(i) for i in _prange(a, b)), "join with nothing between puts the digits side by side."


@_r
def range_to_string(rng):
    n = rng.randint(2, 6)
    return f"[...Array({n}).keys()].join(\" \")", " ".join(str(i) for i in _prange(0, n)), "The numbers joined with spaces."


@_r
def range_while(rng):
    a, s = rng.randint(0, 3), rng.randint(2, 4)
    b = a + rng.randint(2 * s + 1, 4 * s)
    return (f"const out = [];\nlet i = {a};\nwhile (i < {b}) {{\n  out.push(i);\n  i += {s};\n}}\nout", _prange(a, b, s),
            f"i starts at {a} and grows by {s} while it is below {b}.")


@_r
def range_while_down(rng):
    s = rng.randint(2, 3)
    a = rng.randint(0, 2)
    b = a + rng.randint(2 * s + 1, 4 * s)
    return (f"const out = [];\nlet i = {b};\nwhile (i > {a}) {{\n  out.push(i);\n  i -= {s};\n}}\nout", _prange(b, a, -s),
            f"i starts at {b} and drops by {s} while it is above {a}.")


@_r
def range_if_filter(rng):
    a = rng.randint(1, 3)
    b = a + rng.randint(5, 8)
    k = rng.choice((2, 3))
    out = [i for i in _prange(a, b) if tmod(i, k) == 0]
    return (f"const out = [];\nfor (let i = {a}; i < {b}; i++) {{\n  if (i % {k} === 0) out.push(i);\n}}\nout", out,
            f"Only the multiples of {k} in {a} to {b - 1} are kept.")


@_r
def range_word_pick(rng):
    w = _word(rng, 5, 6)
    picks = "".join(w[i] for i in _prange(0, len(w), 2))
    return f'let out = "";\nfor (let i = 0; i < "{w}".length; i += 2) {{\n  out += "{w}"[i];\n}}\nout', picks, "i takes every second index: 0, 2, 4 ..."


@_r
def range_index_loop(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return (f"const xs = {_arr(xs)};\nconst out = [];\nfor (let i = 0; i < xs.length; i++) {{\n  out.push(i * xs[i]);\n}}\nout",
            [i * xs[i] for i in range(len(xs))], "Each turn multiplies the index by the item at that index.")


@_r
def range_reverse_index(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return (f"const xs = {_arr(xs)};\nconst out = [];\nfor (let i = xs.length - 1; i >= 0; i--) {{\n  out.push(xs[i]);\n}}\nout", xs[::-1],
            "The index counts down from the last position: the array comes out backwards.")


@_r
def range_off_by_one(rng):
    n = rng.randint(2, 4)
    return (f"const out = [];\nfor (let i = 0; i <= {n}; i++) {{\n  out.push(i);\n}}\nout.length", n + 1, f"<= {n} includes both 0 and {n}: {n + 1} values.")


@_r
def range_reduce_sum(rng):
    n = rng.randint(3, 6)
    return f"[...Array({n}).keys()].reduce((a, b) => a + b, 0)", sum(_prange(0, n)), f"0 + 1 + ... + {n - 1}."


@_r
def range_from_sq(rng):
    n = rng.randint(3, 6)
    return f"Array.from({{ length: {n} }}, (_, i) => (i + 1) ** 2)", [(i + 1) ** 2 for i in _prange(0, n)], f"The squares of 1 to {n}."


@_r
def range_negative_count(rng):
    n = rng.randint(2, 5)
    return f"const out = [];\nfor (let i = 0; i > -{n}; i--) {{\n  out.push(i);\n}}\nout", _prange(0, -n, -1), f"0, -1, ... stopping before -{n}."


@_r
def range_through_zero(rng):
    n, s = rng.randint(2, 3), rng.randint(1, 2)
    return f"const out = [];\nfor (let i = -{n}; i < {n}; i += {s}) {{\n  out.push(i);\n}}\nout", _prange(-n, n, s), f"From -{n} up in steps of {s}, stopping before {n}."


@_r
def range_empty(rng):
    a = rng.randint(3, 8)
    b = rng.randint(1, a)
    return f"const out = [];\nfor (let i = {a}; i < {b}; i++) {{\n  out.push(i);\n}}\nout", [], f"{a} is already past {b}: the body never runs."


@_r
def range_two_arrays(rng):
    a = rng.randint(1, 3)
    b = a + rng.randint(2, 3)
    c = b + rng.randint(2, 4)
    return (f"[...Array.from({{ length: {b - a} }}, (_, i) => {a} + i), {c}, {c + 1}]", _prange(a, b) + [c, c + 1],
            "A spread copies the items of the first array, then the last two are added.")


@_r
def range_slice_keys(rng):
    n = rng.randint(6, 9)
    a = rng.randint(1, 2)
    b = rng.randint(4, 5)
    return f"[...Array({n}).keys()].slice({a}, {b})", _prange(a, b), f"The positions from {a} up to, not including, {b}."


# ═══ 2. Running Total ═══════════════════════════════════════════════════

TOTAL: list[Maker] = []
_t = _register(TOTAL)


@_t
def total_sum_range(rng):
    a = rng.randint(1, 4)
    b = a + rng.randint(3, 6)
    t = sum(_prange(a, b))
    return f"let total = 0;\nfor (let i = {a}; i < {b}; i++) {{\n  total += i;\n}}\ntotal", t, f"Adds {a}, {a + 1} ... {b - 1}."


@_t
def total_sum_of(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"const xs = {_arr(xs)};\nlet total = 0;\nfor (const x of xs) {{\n  total += x;\n}}\ntotal", sum(xs), "total starts at 0 and takes each item in turn."


@_t
def total_product(rng):
    xs = _digits(rng, rng.randint(3, 4), 1, 5)
    t = 1
    for x in xs:
        t *= x
    return f"const xs = {_arr(xs)};\nlet total = 1;\nfor (const x of xs) {{\n  total *= x;\n}}\ntotal", t, "A product starts at 1, not 0."


@_t
def total_squares(rng):
    n = rng.randint(3, 6)
    return f"let total = 0;\nfor (let i = 1; i <= {n}; i++) {{\n  total += i * i;\n}}\ntotal", sum(i * i for i in range(1, n + 1)), f"The squares of 1 to {n}, added up."


@_t
def total_evens(rng):
    xs = _digits(rng, 5)
    t = sum(x for x in xs if tmod(x, 2) == 0)
    return f"const xs = {_arr(xs)};\nlet total = 0;\nfor (const x of xs) {{\n  if (x % 2 === 0) total += x;\n}}\ntotal", t, "Only the even items are added."


@_t
def total_count_over(rng):
    xs = _digits(rng, rng.randint(5, 6))
    lim = rng.randint(3, 6)
    return (f"const xs = {_arr(xs)};\nlet count = 0;\nfor (const x of xs) {{\n  if (x > {lim}) count++;\n}}\ncount", len([x for x in xs if x > lim]),
            f"count goes up once for each item above {lim}.")


@_t
def total_max_loop(rng):
    xs = _digits(rng, rng.randint(4, 6))
    best = xs[0]
    for x in xs:
        if x > best:
            best = x
    return f"const xs = {_arr(xs)};\nlet best = xs[0];\nfor (const x of xs) {{\n  if (x > best) best = x;\n}}\nbest", best, "best is replaced whenever a bigger item turns up."


@_t
def total_min_loop(rng):
    xs = _digits(rng, rng.randint(4, 6))
    low = 99
    for x in xs:
        if x < low:
            low = x
    return f"const xs = {_arr(xs)};\nlet low = 99;\nfor (const x of xs) {{\n  if (x < low) low = x;\n}}\nlow", low, "low is replaced whenever a smaller item turns up."


@_t
def total_max_spread(rng):
    xs = _digits(rng, rng.randint(4, 6))
    return f"const xs = {_arr(xs)};\nMath.max(...xs) - Math.min(...xs)", max(xs) - min(xs), "The spread passes every item to Math.max and Math.min: biggest minus smallest."


@_t
def total_reverse_text(rng):
    w = _word(rng)
    return f'let out = "";\nfor (const ch of "{w}") {{\n  out = ch + out;\n}}\nout', w[::-1], "Each new letter goes in front, so the word ends up backwards."


@_t
def total_double_letters(rng):
    w = _word(rng, 3, 4)
    return f'let out = "";\nfor (const ch of "{w}") {{\n  out += ch + ch;\n}}\nout', "".join(c * 2 for c in w), "Every letter is added twice."


@_t
def total_vowels(rng):
    w = _word(rng, 4, 7)
    return f'let count = 0;\nfor (const ch of "{w}") {{\n  if ("aeiou".includes(ch)) count++;\n}}\ncount', len([c for c in w if c in _VOWELS]), "Counts the vowels in the word."


@_t
def total_countdown(rng):
    xs = _digits(rng, rng.randint(3, 4))
    start = rng.randint(20, 40)
    return f"let total = {start};\nfor (const x of {_arr(xs)}) {{\n  total -= x;\n}}\ntotal", start - sum(xs), f"{start} with each item taken off in turn."


@_t
def total_doubling(rng):
    a, n = rng.randint(1, 5), rng.randint(3, 5)
    return f"let total = {a};\nfor (let i = 0; i < {n}; i++) {{\n  total *= 2;\n}}\ntotal", a * 2 ** n, f"{a} doubled {n} times."


@_t
def total_alternate(rng):
    xs = _digits(rng, rng.randint(4, 5))
    t, sign = 0, 1
    for x in xs:
        t += sign * x
        sign = -sign
    return (f"const xs = {_arr(xs)};\nlet total = 0;\nlet sign = 1;\nfor (const x of xs) {{\n  total += sign * x;\n  sign = -sign;\n}}\ntotal", t,
            "The sign flips every turn: add, subtract, add ...")


@_t
def total_number_build(rng):
    ds = _digits(rng, rng.randint(3, 4))
    n = 0
    for d in ds:
        n = n * 10 + d
    return f"let n = 0;\nfor (const d of {_arr(ds)}) {{\n  n = n * 10 + d;\n}}\nn", n, "Each turn shifts n one place left and adds the next digit."


@_t
def total_digit_text(rng):
    num = str(rng.randint(1000, 9999))
    return f'let total = 0;\nfor (const ch of "{num}") {{\n  total += Number(ch);\n}}\ntotal', sum(int(c) for c in num), "Number(ch) turns each digit character into a number."


@_t
def total_digit_text_trap(rng):
    num = str(rng.randint(1000, 9999))
    return f'let total = 0;\nfor (const ch of "{num}") {{\n  total += ch;\n}}\ntotal', "0" + num, "+= with a string makes total a string from the first turn, so the digits are joined, not added."


@_t
def total_partials(rng):
    xs = _digits(rng, rng.randint(3, 5))
    out, t = [], 0
    for x in xs:
        t += x
        out.append(t)
    return (f"const xs = {_arr(xs)};\nconst out = [];\nlet total = 0;\nfor (const x of xs) {{\n  total += x;\n  out.push(total);\n}}\nout", out,
            "A running total: each entry is the sum so far.")


@_t
def total_weighted(rng):
    xs = _digits(rng, rng.randint(3, 4))
    return (f"const xs = {_arr(xs)};\nlet total = 0;\nfor (let i = 0; i < xs.length; i++) {{\n  total += i * xs[i];\n}}\ntotal", sum(i * xs[i] for i in range(len(xs))),
            "Each item is multiplied by its index first; the first counts for 0.")


@_t
def total_dot(rng):
    n = rng.randint(2, 4)
    xs, ys = _digits(rng, n), _digits(rng, n)
    return (f"const xs = {_arr(xs)};\nconst ys = {_arr(ys)};\nlet total = 0;\nfor (let i = 0; i < xs.length; i++) {{\n  total += xs[i] * ys[i];\n}}\ntotal",
            sum(xs[i] * ys[i] for i in range(n)), "Multiply the items at the same position, then add the products.")


@_t
def total_str_numbers(rng):
    a = rng.randint(0, 3)
    b = a + rng.randint(3, 5)
    return f'let out = "";\nfor (let i = {a}; i < {b}; i++) {{\n  out += i;\n}}\nout', "".join(str(i) for i in _prange(a, b)), "out is text, so += joins the digits instead of adding."


@_t
def total_str_start(rng):
    xs = _digits(rng, rng.randint(2, 3))
    return f'let total = "";\nfor (const x of {_arr(xs)}) {{\n  total += x;\n}}\ntotal', "".join(str(x) for x in xs), 'total starts as "", so it stays text and the numbers are glued together.'


@_t
def total_str_zero(rng):
    xs = _digits(rng, rng.randint(2, 3))
    return f'let total = 0;\nfor (const s of {_arr([str(x) for x in xs])}) {{\n  total += s;\n}}\ntotal', "0" + "".join(str(x) for x in xs), "0 + a string makes a string: \"0\", then each item is joined on."


@_t
def total_reduce(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"{_arr(xs)}.reduce((acc, x) => acc + x, 0)", sum(xs), "reduce carries an accumulator through the array."


@_t
def total_reduce_product(rng):
    xs = _digits(rng, rng.randint(3, 4), 1, 5)
    t = 1
    for x in xs:
        t *= x
    return f"{_arr(xs)}.reduce((acc, x) => acc * x, 1)", t, "The accumulator starts at 1 and is multiplied by each item."


@_t
def total_for_each(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"const xs = {_arr(xs)};\nlet total = 0;\nxs.forEach(x => {{\n  total += x * 2;\n}});\ntotal", sum(xs) * 2, "forEach runs the function once per item; each is doubled and added."


@_t
def total_object_values(rng):
    ks = rng.sample(WORDS, 3)
    vs = _digits(rng, 3)
    o = ", ".join(f"{k}: {v}" for k, v in zip(ks, vs))
    return f"const o = {{ {o} }};\nlet total = 0;\nfor (const k in o) {{\n  total += o[k];\n}}\ntotal", sum(vs), "for...in gives the keys; o[k] looks up each value."


@_t
def total_values_method(rng):
    ks = rng.sample(WORDS, 3)
    vs = _digits(rng, 3)
    o = ", ".join(f"{k}: {v}" for k, v in zip(ks, vs))
    t = 1
    for v in vs:
        t *= v
    return f"const o = {{ {o} }};\nlet total = 1;\nfor (const v of Object.values(o)) {{\n  total *= v;\n}}\ntotal", t, "Object.values gives the values themselves; they are multiplied together."


@_t
def total_factorial(rng):
    n = rng.randint(3, 6)
    t = 1
    for i in range(1, n + 1):
        t *= i
    return f"let total = 1;\nfor (let i = 1; i <= {n}; i++) {{\n  total *= i;\n}}\ntotal", t, f"1 * 2 * ... * {n}."


@_t
def total_fib(rng):
    n = rng.randint(4, 9)
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return f"let [a, b] = [0, 1];\nfor (let i = 0; i < {n}; i++) {{\n  [a, b] = [b, a + b];\n}}\na", a, f"The pair steps along the Fibonacci numbers {n} times; a is the first of the pair."


@_t
def total_balance(rng):
    start = rng.randint(10, 30)
    moves = [rng.choice((-1, 1)) * rng.randint(2, 12) for _ in range(rng.randint(3, 4))]
    return f"let balance = {start};\nfor (const m of {_arr(moves)}) {{\n  balance += m;\n}}\nbalance", start + sum(moves), "Adding a negative number takes it away."


@_t
def total_word_lengths(rng):
    ws = rng.sample(WORDS, 3)
    return f"let total = 0;\nfor (const w of {_arr(ws)}) {{\n  total += w.length;\n}}\ntotal", sum(len(w) for w in ws), "w.length is the number of letters in each word."


@_t
def total_first_letters(rng):
    ws = rng.sample(WORDS, rng.randint(3, 4))
    return f'let out = "";\nfor (const w of {_arr(ws)}) {{\n  out += w[0];\n}}\nout', "".join(w[0] for w in ws), "w[0] is the first letter of each word."


@_t
def total_longest(rng):
    ws = rng.sample(WORDS, 4)
    best = ""
    for w in ws:
        if len(w) > len(best):
            best = w
    return f'let best = "";\nfor (const w of {_arr(ws)}) {{\n  if (w.length > best.length) best = w;\n}}\nbest', best, "best changes only for a strictly longer word, so the first of a tie stays."


@_t
def total_average(rng):
    xs = _digits(rng, rng.choice((3, 4, 5)))
    return (f"const xs = {_arr(xs)};\nlet total = 0;\nfor (const x of xs) {{\n  total += x;\n}}\nMath.floor(total / xs.length)", fdiv(sum(xs), len(xs)),
            f"The sum is {sum(xs)}; dividing by {len(xs)} and rounding down.")


@_t
def total_remainder(rng):
    xs = _digits(rng, rng.randint(4, 5))
    k = rng.randint(3, 7)
    return f"const xs = {_arr(xs)};\nlet total = 0;\nfor (const x of xs) {{\n  total += x;\n}}\ntotal % {k}", tmod(sum(xs), k), f"The loop gives {sum(xs)}; then % {k} is the remainder."


@_t
def total_abs(rng):
    xs = [rng.choice((-1, 1)) * rng.randint(1, 9) for _ in range(rng.randint(3, 5))]
    return f"let total = 0;\nfor (const x of {_arr(xs)}) {{\n  total += Math.abs(x);\n}}\ntotal", sum(abs(x) for x in xs), "Math.abs drops the minus sign, so every item adds."


@_t
def total_binary(rng):
    bits = [rng.randint(0, 1) for _ in range(rng.randint(4, 5))]
    bits[0] = 1
    n = 0
    for b in bits:
        n = n * 2 + b
    return f"let n = 0;\nfor (const bit of {_arr(bits)}) {{\n  n = n * 2 + bit;\n}}\nn", n, "Reading binary: double what you have, then add the next bit."


@_t
def total_threshold(rng):
    xs = _digits(rng, rng.randint(5, 6))
    lim = rng.randint(3, 6)
    return (f"const xs = {_arr(xs)};\nlet total = 0;\nfor (const x of xs) {{\n  total += x > {lim} ? x : 0;\n}}\ntotal", sum(x for x in xs if x > lim),
            f"Only items above {lim} are added; the rest add 0.")


@_t
def total_double_plus_one(rng):
    n = rng.randint(3, 6)
    t = 0
    for _ in range(n):
        t = t * 2 + 1
    return f"let total = 0;\nfor (let i = 0; i < {n}; i++) {{\n  total = total * 2 + 1;\n}}\ntotal", t, "0, 1, 3, 7, 15 ...: each turn doubles and adds 1."


@_t
def total_lengths_list(rng):
    ws = rng.sample(WORDS, 3)
    return f"const out = [];\nfor (const w of {_arr(ws)}) {{\n  out.push(w.length);\n}}\nout", [len(w) for w in ws], "One length per word, in order."


@_t
def total_running_max(rng):
    xs = _digits(rng, rng.randint(4, 6))
    out, best = [], 0
    for x in xs:
        if x > best:
            best = x
        out.append(best)
    return (f"const xs = {_arr(xs)};\nconst out = [];\nlet best = 0;\nfor (const x of xs) {{\n  if (x > best) best = x;\n  out.push(best);\n}}\nout", out,
            "Each entry is the biggest item seen so far.")


# ═══ 3. Nested Count ════════════════════════════════════════════════════

NESTED: list[Maker] = []
_n = _register(NESTED)


def _two(outer: str, inner: str, body: str, init: str = "let count = 0;", last: str = "count") -> str:
    """Two nested for loops (headers given without `for (...)`), a one-line body, then the asked-about line."""
    return f"{init}\nfor ({outer}) {{\n  for ({inner}) {{\n    {body}\n  }}\n}}\n{last}"


def _f(v: str, a, b, step: str = "++", op: str = "<") -> str:
    return f"let {v} = {a}; {v} {op} {b}; {v}{step}"


@_n
def nest_product(rng):
    a, b = rng.randint(2, 5), rng.randint(2, 6)
    return _two(_f("i", 0, a), _f("j", 0, b), "count++;"), a * b, f"The inner loop runs {b} times for each of the {a} outer turns."


@_n
def nest_ranges(rng):
    a = rng.randint(1, 3)
    b = a + rng.randint(2, 4)
    c = rng.randint(1, 3)
    d = c + rng.randint(2, 4)
    return _two(_f("i", a, b), _f("j", c, d), "count++;"), (b - a) * (d - c), f"{b - a} outer values times {d - c} inner values."


@_n
def nest_triangle(rng):
    a = rng.randint(3, 6)
    return _two(_f("i", 0, a), _f("j", 0, "i"), "count++;"), sum(range(a)), f"The inner loop runs i times: 0 + 1 + ... + {a - 1}."


@_n
def nest_triangle_le(rng):
    a = rng.randint(3, 6)
    return _two(_f("i", 0, a), _f("j", 0, "i", op="<="), "count++;"), sum(i + 1 for i in range(a)), f"j <= i makes i + 1 passes: 1 + 2 + ... + {a}."


@_n
def nest_shrinking(rng):
    a = rng.randint(3, 6)
    return _two(_f("i", 0, a), _f("j", 0, f"{a} - i"), "count++;"), sum(a - i for i in range(a)), f"The inner loop runs {a}, {a - 1}, ... 1 times."


@_n
def nest_from_i(rng):
    a = rng.randint(3, 6)
    return _two(_f("i", 0, a), _f("j", "i", a), "count++;"), sum(a - i for i in range(a)), f"j starts at i and stops before {a}: {a}, {a - 1}, ... 1 times."


@_n
def nest_i_less_j(rng):
    a = rng.randint(3, 6)
    n = len([1 for i in range(a) for j in range(a) if i < j])
    return _two(_f("i", 0, a), _f("j", 0, a), "if (i < j) count++;"), n, "Counts the pairs where i is smaller than j: half the grid, without the diagonal."


@_n
def nest_diagonal(rng):
    a, b = rng.randint(3, 6), rng.randint(3, 6)
    return _two(_f("i", 0, a), _f("j", 0, b), "if (i === j) count++;"), min(a, b), f"i equals j only on the diagonal: min({a}, {b}) times."


@_n
def nest_off_diagonal(rng):
    a = rng.randint(2, 5)
    return _two(_f("i", 0, a), _f("j", 0, a), "if (i !== j) count++;"), a * a - a, f"All {a * a} pairs except the {a} where i equals j."


@_n
def nest_sum_target(rng):
    a, b, k = rng.randint(3, 5), rng.randint(3, 5), rng.randint(2, 5)
    n = len([1 for i in range(a) for j in range(b) if i + j == k])
    return _two(_f("i", 0, a), _f("j", 0, b), f"if (i + j === {k}) count++;"), n, f"Counts the pairs (i, j) that add up to {k}."


@_n
def nest_even_sum(rng):
    a, b = rng.randint(2, 5), rng.randint(2, 5)
    n = len([1 for i in range(a) for j in range(b) if tmod(i + j, 2) == 0])
    return _two(_f("i", 0, a), _f("j", 0, b), "if ((i + j) % 2 === 0) count++;"), n, "Counts the pairs whose sum is even."


@_n
def nest_product_big(rng):
    a, b, t = rng.randint(3, 5), rng.randint(3, 5), rng.randint(2, 6)
    n = len([1 for i in range(a) for j in range(b) if i * j > t])
    return _two(_f("i", 0, a), _f("j", 0, b), f"if (i * j > {t}) count++;"), n, f"Counts the pairs whose product is above {t}."


@_n
def nest_sum_products(rng):
    a, b = rng.randint(2, 4), rng.randint(2, 4)
    return _two(_f("i", 0, a), _f("j", 0, b), "total += i * j;", "let total = 0;", "total"), sum(i * j for i in range(a) for j in range(b)), "Every pair adds its product to total."


@_n
def nest_outer_counts_too(rng):
    a, b = rng.randint(2, 5), rng.randint(2, 4)
    return (f"let count = 0;\nfor (let i = 0; i < {a}; i++) {{\n  count++;\n  for (let j = 0; j < {b}; j++) {{\n    count++;\n  }}\n}}\ncount", a * (1 + b),
            f"Each outer turn adds 1 itself, plus {b} from the inner loop.")


@_n
def nest_step_two(rng):
    a, b = rng.randint(4, 8), rng.randint(2, 4)
    return _two(_f("i", 0, a, " += 2"), _f("j", 0, b), "count++;"), len(_prange(0, a, 2)) * b, f"The outer loop visits {len(_prange(0, a, 2))} values."


@_n
def nest_inner_step(rng):
    a, b = rng.randint(2, 4), rng.randint(5, 9)
    return _two(_f("i", 0, a), _f("j", 0, b, " += 3"), "count++;"), a * len(_prange(0, b, 3)), f"The inner loop visits {len(_prange(0, b, 3))} values: 0, 3, ..."


@_n
def nest_three(rng):
    a, b, c = rng.randint(2, 3), rng.randint(2, 3), rng.randint(2, 3)
    return (f"let count = 0;\nfor (let i = 0; i < {a}; i++) {{\n  for (let j = 0; j < {b}; j++) {{\n    for (let k = 0; k < {c}; k++) count++;\n  }}\n}}\ncount",
            a * b * c, f"{a} times {b} times {c}.")


@_n
def nest_three_triangle(rng):
    a = rng.randint(3, 4)
    n = len([1 for i in range(a) for j in range(i) for _k in range(j)])
    return (f"let count = 0;\nfor (let i = 0; i < {a}; i++) {{\n  for (let j = 0; j < i; j++) {{\n    for (let k = 0; k < j; k++) count++;\n  }}\n}}\ncount", n,
            "Each level is limited by the one outside it, so few passes reach the innermost body.")


@_n
def nest_while(rng):
    a, b = rng.randint(2, 4), rng.randint(2, 4)
    return (f"let count = 0, i = 0;\nwhile (i < {a}) {{\n  let j = 0;\n  while (j < {b}) {{ count++; j++; }}\n  i++;\n}}\ncount", a * b,
            f"j restarts at 0 on each of the {a} outer turns.")


@_n
def nest_inner_break(rng):
    a, b, k = rng.randint(2, 5), rng.randint(4, 6), rng.randint(1, 3)
    return (_two(_f("i", 0, a), _f("j", 0, b), f"if (j === {k}) break;\n    count++;"), a * k,
            f"break leaves only the inner loop: {k} passes for each of the {a} outer turns.")


@_n
def nest_inner_continue(rng):
    a, b, k = rng.randint(2, 4), rng.randint(3, 6), rng.randint(0, 2)
    return _two(_f("i", 0, a), _f("j", 0, b), f"if (j === {k}) continue;\n    count++;"), a * (b - 1), f"One of the {b} inner turns is skipped each time."


@_n
def nest_label_break(rng):
    a, b, k = rng.randint(2, 4), rng.randint(3, 5), rng.randint(1, 3)
    n = k if k < b else a * b
    return (f"let count = 0;\nouter: for (let i = 0; i < {a}; i++) {{\n  for (let j = 0; j < {b}; j++) {{\n    if (j === {k}) break outer;\n    count++;\n  }}\n}}\ncount", n,
            "break outer leaves BOTH loops, so after the first row's passes nothing more runs.")


@_n
def nest_label_continue(rng):
    a, b, k = rng.randint(2, 4), rng.randint(3, 5), rng.randint(1, 3)
    return (f"let count = 0;\nouter: for (let i = 0; i < {a}; i++) {{\n  for (let j = 0; j < {b}; j++) {{\n    if (j === {k}) continue outer;\n    count++;\n  }}\n}}\ncount",
            a * min(k, b), "continue outer skips to the next outer turn, abandoning the rest of the inner loop.")


@_n
def nest_grid_cells(rng):
    grid = [_digits(rng, rng.randint(2, 4)) for _ in range(rng.randint(2, 3))]
    return (f"const grid = {_arr(grid)};\nlet count = 0;\nfor (const row of grid) {{\n  for (const x of row) count++;\n}}\ncount", sum(len(r) for r in grid),
            "Counts every cell in every row.")


@_n
def nest_grid_sum(rng):
    grid = [_digits(rng, rng.randint(2, 3)) for _ in range(rng.randint(2, 3))]
    return (f"const grid = {_arr(grid)};\nlet total = 0;\nfor (const row of grid) {{\n  for (const x of row) total += x;\n}}\ntotal", sum(sum(r) for r in grid),
            "Adds every cell of every row.")


@_n
def nest_grid_flat(rng):
    grid = [_digits(rng, 2) for _ in range(rng.randint(2, 3))]
    return (f"const grid = {_arr(grid)};\nconst out = [];\nfor (const row of grid) {{\n  for (const x of row) out.push(x * 2);\n}}\nout", [x * 2 for r in grid for x in r],
            "The rows are flattened into one array, each cell doubled.")


@_n
def nest_grid_column(rng):
    grid = [_digits(rng, 3) for _ in range(3)]
    c = rng.randint(0, 2)
    return (f"const grid = {_arr(grid)};\nlet total = 0;\nfor (const row of grid) {{\n  total += row[{c}];\n}}\ntotal", sum(r[c] for r in grid),
            f"Adds item {c} of each row: a column.")


@_n
def nest_words_letters(rng):
    ws = rng.sample(WORDS, 3)
    return f"let count = 0;\nfor (const w of {_arr(ws)}) {{\n  for (const ch of w) count++;\n}}\ncount", sum(len(w) for w in ws), "One pass per letter of every word: the total of the lengths."


@_n
def nest_letter_hits(rng):
    ws = rng.sample(WORDS, 4)
    return (f'let count = 0;\nfor (const w of {_arr(ws)}) {{\n  for (const ch of w) {{\n    if (ch === "e") count++;\n  }}\n}}\ncount', sum(w.count("e") for w in ws),
            'Counts every "e" in every word.')


@_n
def nest_stars(rng):
    a = rng.randint(2, 4)
    return (f'let out = "";\nfor (let i = 0; i < {a}; i++) {{\n  for (let j = 0; j <= i; j++) out += "*";\n  out += "/";\n}}\nout',
            "".join("*" * (i + 1) + "/" for i in range(a)), "Row i has i + 1 stars; each row ends with a slash.")


@_n
def nest_table(rng):
    a = rng.randint(2, 3)
    b = rng.randint(2, 6 // a)
    return (_two(_f("i", 1, a, op="<="), _f("j", 1, b, op="<="), "out.push(i * j);", "const out = [];", "out"), [i * j for i in range(1, a + 1) for j in range(1, b + 1)],
            "A multiplication table, read row by row.")


@_n
def nest_pair_sums(rng):
    a = rng.randint(3, 4)
    return _two(_f("i", 0, a), _f("j", 0, "i"), "out.push(i + j);", "const out = [];", "out"), [i + j for i in range(a) for j in range(i)], "j stays below i, so row 0 adds nothing."


@_n
def nest_index_pairs(rng):
    xs = _digits(rng, rng.randint(4, 5), 1, 6)
    t = rng.randint(5, 9)
    n = len([1 for i in range(len(xs)) for j in range(i + 1, len(xs)) if xs[i] + xs[j] == t])
    return (f"const xs = {_arr(xs)};\nlet count = 0;\nfor (let i = 0; i < xs.length; i++) {{\n  for (let j = i + 1; j < xs.length; j++) {{\n    if (xs[i] + xs[j] === {t}) count++;\n  }}\n}}\ncount", n,
            f"Each pair of positions is tried once; counts those that add up to {t}.")


@_n
def nest_divisors(rng):
    n = rng.randint(4, 8)
    c = len([1 for i in range(1, n + 1) for j in range(1, n + 1) if tmod(i, j) == 0])
    return _two(_f("i", 1, n, op="<="), _f("j", 1, n, op="<="), "if (i % j === 0) count++;"), c, "Counts the pairs where j divides i exactly."


@_n
def nest_triangle_sums(rng):
    n = rng.randint(3, 5)
    return _two(_f("i", 1, n, op="<="), _f("j", 1, "i", op="<="), "total += j;", "let total = 0;", "total"), sum(j for i in range(1, n + 1) for j in range(1, i + 1)), "Row i adds 1 + 2 + ... + i; the rows are added together."


@_n
def nest_outer_only(rng):
    a, b = rng.randint(3, 5), rng.randint(2, 4)
    return (f"let count = 0;\nfor (let i = 0; i < {a}; i++) {{\n  for (let j = 0; j < {b}; j++) {{}}\n  count++;\n}}\ncount", a,
            "count is bumped outside the inner loop: once per outer turn.")


@_n
def nest_array_pairs(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"const xs = {_arr(xs)};\nlet count = 0;\nfor (const x of xs) {{\n  for (const y of xs) count++;\n}}\ncount", len(xs) ** 2, f"{len(xs)} items against {len(xs)} items."


# ═══ 4. Break & Continue ════════════════════════════════════════════════

BREAK: list[Maker] = []
_b = _register(BREAK)


def _of(xs, body: str, init: str = "", last: str = "") -> str:
    """A for...of loop over the array literal xs with a (possibly multi-line) body, then the asked-about line."""
    lines = body.split("\n")
    return f"{init}\nfor (const x of {_arr(xs)}) {{\n" + "\n".join("  " + ln for ln in lines) + f"\n}}\n{last}"


@_b
def brk_sum_until_over(rng):
    xs = _digits(rng, rng.randint(5, 6))
    lim = rng.randint(8, 16)
    t = 0
    for x in xs:
        t += x
        if t > lim:
            break
    return _of(xs, f"total += x;\nif (total > {lim}) break;", "let total = 0;", "total"), t, f"The item that pushes total past {lim} is added first; then the loop stops."


@_b
def brk_sum_before_over(rng):
    xs = _digits(rng, rng.randint(5, 6))
    lim = rng.randint(8, 16)
    t = 0
    for x in xs:
        if t + x > lim:
            break
        t += x
    return _of(xs, f"if (total + x > {lim}) break;\ntotal += x;", "let total = 0;", "total"), t, f"The check comes first, so the item that would pass {lim} is never added."


@_b
def brk_count_before(rng):
    xs = _digits(rng, 6)
    t = xs[rng.randint(1, 5)]
    c = 0
    for x in xs:
        if x == t:
            break
        c += 1
    return _of(xs, f"if (x === {t}) break;\ncount++;", "let count = 0;", "count"), c, f"Counts the items before the first {t}."


@_b
def brk_count_missing(rng):
    xs = _digits(rng, rng.randint(4, 6), 1, 8)
    return _of(xs, "if (x === 9) break;\ncount++;", "let count = 0;", "count"), len(xs), "There is no 9, so the break never happens and every item is counted."


@_b
def brk_skip_odd(rng):
    xs = _digits(rng, rng.randint(5, 6))
    t = sum(x for x in xs if tmod(x, 2) == 0)
    return _of(xs, "if (x % 2 === 1) continue;\ntotal += x;", "let total = 0;", "total"), t, "Odd items are skipped, so only the even ones are added. continue goes straight to the next item."


@_b
def brk_skip_value(rng):
    xs = _digits(rng, 6, 1, 4)
    v = rng.randint(1, 4)
    return _of(xs, f"if (x === {v}) continue;\nout.push(x);", "const out = [];", "out"), [x for x in xs if x != v], f"Every {v} is skipped."


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
    return _of(xs, "if (x < 0) continue;\nif (x > 7) break;\ntotal += x;", "let total = 0;", "total"), t, "Negatives are skipped; the first item over 7 ends the loop."


@_b
def brk_while_true(rng):
    lim = rng.randint(20, 100)
    n = 1
    while True:
        n *= 2
        if n > lim:
            break
    return f"let n = 1;\nwhile (true) {{\n  n *= 2;\n  if (n > {lim}) break;\n}}\nn", n, "Doubles until it is past the limit; the doubling that crosses it still counts."


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
    return f"let total = 0, count = 0;\nwhile (true) {{\n  total += {k};\n  count++;\n  if (total >= {lim}) break;\n}}\ncount", c, f"How many {k}s it takes to reach {lim} or more."


@_b
def brk_while_continue(rng):
    n = rng.randint(5, 9)
    t = sum(i for i in range(1, n + 1) if tmod(i, 2) == 1)
    return f"let i = 0, total = 0;\nwhile (i < {n}) {{\n  i++;\n  if (i % 2 === 0) continue;\n  total += i;\n}}\ntotal", t, "i goes up before the check, so continue is safe; only odd i are added."


@_b
def brk_do_while(rng):
    s, n0 = rng.randint(2, 5), rng.randint(1, 4)
    n = n0
    while True:
        n -= s
        if not n > 0:
            break
    return f"let n = {n0};\ndo {{\n  n -= {s};\n}} while (n > 0);\nn", n, "A do...while runs its body once before it ever checks the condition."


@_b
def brk_nested_inner(rng):
    a, b, k = rng.randint(2, 4), rng.randint(3, 5), rng.randint(1, 2)
    return (f"let count = 0;\nfor (let i = 0; i < {a}; i++) {{\n  for (let j = 0; j < {b}; j++) {{\n    if (j >= {k}) break;\n    count++;\n  }}\n}}\ncount", a * k,
            f"break only ends the inner loop, so every outer turn still runs ({k} inner passes each).")


@_b
def brk_label_break_pair(rng):
    n, t = rng.randint(3, 5), rng.randint(4, 8)
    pair = None
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            if i * j >= t:
                pair = [i, j]
                break
        if pair:
            break
    shown = js_show(pair) if pair else "null"
    return (f"let pair = null;\nouter: for (let i = 1; i <= {n}; i++) {{\n  for (let j = 1; j <= {n}; j++) {{\n    if (i * j >= {t}) {{\n      pair = [i, j];\n      break outer;\n    }}\n  }}\n}}\npair", shown,
            f"The first pair, row by row, whose product reaches {t}. break outer stops both loops.")


@_b
def brk_label_continue(rng):
    a, b = rng.randint(3, 5), rng.randint(3, 5)
    c = 0
    for i in range(a):
        for j in range(b):
            if j > i:
                break
            c += 1
    return (f"let count = 0;\nouter: for (let i = 0; i < {a}; i++) {{\n  for (let j = 0; j < {b}; j++) {{\n    if (j > i) continue outer;\n    count++;\n  }}\n}}\ncount", c,
            "continue outer ends the inner loop and moves to the next row: row i counts i + 1 cells (at most the row length).")


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
    return (f'const out = [];\nfor (const w of {_arr(ws)}) {{\n  if (w === "stop") break;\n  out.push(w);\n}}\nout.join("-")', "-".join(out), "Words are collected until the word stop appears.")


@_b
def brk_words_skip(rng):
    ws = rng.sample(WORDS, 5)
    bad = rng.choice(ws)
    out = "".join(w[0] for w in ws if w != bad)
    return f'let out = "";\nfor (const w of {_arr(ws)}) {{\n  if (w === "{bad}") continue;\n  out += w[0];\n}}\nout', out, f'The word "{bad}" is skipped; the others give their first letter.'


@_b
def brk_sentinel(rng):
    xs = _digits(rng, 5)
    xs[rng.randint(1, 3)] = 0
    t = 0
    for x in xs:
        if x == 0:
            break
        t += x
    return _of(xs, "if (x === 0) break;\ntotal += x;", "let total = 0;", "total"), t, "A 0 ends the loop: only what came before it is added."


@_b
def brk_skip_multiples(rng):
    n, k = rng.randint(7, 10), rng.randint(2, 3)
    return (f"const out = [];\nfor (let i = 1; i < {n}; i++) {{\n  if (i % {k} === 0) continue;\n  out.push(i);\n}}\nout", [i for i in range(1, n) if tmod(i, k) != 0],
            f"Multiples of {k} are skipped.")


@_b
def brk_range_stop(rng):
    n, k = rng.randint(8, 12), rng.randint(3, 5)
    return f"const out = [];\nfor (let i = 0; i < {n}; i++) {{\n  if (i === {k}) break;\n  out.push(i);\n}}\nout", _prange(0, k), f"The loop stops when i reaches {k}, before it is pushed."


@_b
def brk_push_then_stop(rng):
    n, k = rng.randint(8, 12), rng.randint(2, 4)
    return f"const out = [];\nfor (let i = 0; i < {n}; i++) {{\n  out.push(i);\n  if (i === {k}) break;\n}}\nout", _prange(0, k + 1), f"The push comes first, so {k} is in the array when the loop stops."


@_b
def brk_isqrt(rng):
    n = rng.randint(10, 80)
    r = 0
    for i in range(1, 20):
        if i * i > n:
            break
        r = i
    return f"let r = 0;\nfor (let i = 1; i < 20; i++) {{\n  if (i * i > {n}) break;\n  r = i;\n}}\nr", r, f"The biggest i whose square is at most {n}."


@_b
def brk_first_index(rng):
    xs = _digits(rng, rng.randint(5, 6), 1, 5)
    t = rng.randint(1, 6)
    idx = xs.index(t) if t in xs else -1
    return (f"const xs = {_arr(xs)};\nlet idx = -1;\nfor (let i = 0; i < xs.length; i++) {{\n  if (xs[i] === {t}) {{\n    idx = i;\n    break;\n  }}\n}}\nidx", idx,
            f"The first position holding {t}, or -1 if there is none.")


@_b
def brk_last_index(rng):
    xs = _digits(rng, rng.randint(5, 6), 1, 4)
    t = rng.randint(1, 5)
    idx = -1
    for i in range(len(xs)):
        if xs[i] == t:
            idx = i
    return (f"const xs = {_arr(xs)};\nlet idx = -1;\nfor (let i = 0; i < xs.length; i++) {{\n  if (xs[i] === {t}) idx = i;\n}}\nidx", idx,
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
    return _of(xs, "if (x < 0) continue;\nif (x > best) best = x;", "let best = 0;", "best"), best, "Negatives never get compared; best starts at 0."


@_b
def brk_count_even_continue(rng):
    xs = _digits(rng, 6)
    return _of(xs, "if (x % 2 === 1) continue;\ncount++;", "let count = 0;", "count"), len([x for x in xs if tmod(x, 2) == 0]), "Odd items skip the count: it counts the even ones."


@_b
def brk_leading_even(rng):
    xs = [2 * rng.randint(1, 4) for _ in range(rng.randint(2, 3))] + [rng.choice((1, 3, 5, 7))] + _digits(rng, 2)
    t = 0
    for x in xs:
        if tmod(x, 2) == 1:
            break
        t += x
    return _of(xs, "if (x % 2 === 1) break;\ntotal += x;", "let total = 0;", "total"), t, "Adds items until the first odd one stops the loop."


@_b
def brk_ok_flag(rng):
    xs = _digits(rng, 5, 1, 9)
    if rng.random() < 0.5:
        xs[rng.randint(0, 4)] = -rng.randint(1, 5)
    ok = all(x >= 0 for x in xs)
    return _of(xs, "if (x < 0) {\n  ok = false;\n  break;\n}", "let ok = true;", "ok"), ok, "ok turns false the moment a negative item is met."


@_b
def brk_foreach_return(rng):
    xs = _digits(rng, rng.randint(5, 6))
    lim = rng.randint(3, 6)
    t = sum(x for x in xs if x <= lim)
    return (f"const xs = {_arr(xs)};\nlet total = 0;\nxs.forEach(x => {{\n  if (x > {lim}) return;\n  total += x;\n}});\ntotal", t,
            f"return inside forEach only leaves that one call - it works like continue, it cannot stop the loop. Items above {lim} are skipped.")


@_b
def brk_nested_continue(rng):
    a = rng.randint(3, 5)
    return (f"let count = 0;\nfor (let i = 0; i < {a}; i++) {{\n  for (let j = 0; j < {a}; j++) {{\n    if (j === i) continue;\n    count++;\n  }}\n}}\ncount", a * (a - 1),
            f"Each row skips its own diagonal cell: {a} rows of {a - 1}.")


@_b
def brk_nested_triangle(rng):
    a = rng.randint(3, 5)
    c = sum(i + 1 for i in range(a))
    return (f"let count = 0;\nfor (let i = 0; i < {a}; i++) {{\n  for (let j = 0; j < {a}; j++) {{\n    if (j > i) break;\n    count++;\n  }}\n}}\ncount", c,
            "Row i stops once j passes i, so it counts i + 1 cells.")


@_b
def brk_outer_continue(rng):
    a, b = rng.randint(4, 7), rng.randint(2, 4)
    rows = len([i for i in range(a) if tmod(i, 2) == 1])
    return (f"let count = 0;\nfor (let i = 0; i < {a}; i++) {{\n  if (i % 2 === 0) continue;\n  for (let j = 0; j < {b}; j++) count++;\n}}\ncount", rows * b,
            f"continue skips the whole inner loop for even i: {rows} rows run.")


@_b
def brk_leading_consonants(rng):
    w = rng.choice([x for x in WORDS if len(x) >= 4 and x[0] not in _VOWELS])
    out = ""
    for ch in w:
        if ch in _VOWELS:
            break
        out += ch
    return f'let out = "";\nfor (const ch of "{w}") {{\n  if ("aeiou".includes(ch)) break;\n  out += ch;\n}}\nout', out, "Letters are collected up to the first vowel."


@_b
def brk_skip_letter(rng):
    w = _word(rng, 4, 7)
    ch0 = rng.choice(w)
    out = "".join(c for c in w if c != ch0)
    return f'let out = "";\nfor (const ch of "{w}") {{\n  if (ch === "{ch0}") continue;\n  out += ch;\n}}\nout', out, f'Every "{ch0}" is left out.'


@_b
def brk_first_duplicate(rng):
    xs = rng.sample(range(1, 9), 4)
    xs.insert(rng.randint(2, 4), xs[rng.randint(0, 1)])
    seen = []
    for x in xs:
        if x in seen:
            break
        seen.append(x)
    return _of(xs, "if (seen.includes(x)) break;\nseen.push(x);", "const seen = [];", "seen"), seen, "Stops at the first item that has already been seen."


@_b
def brk_digits_until(rng):
    num = "".join(str(rng.randint(1, 7)) for _ in range(3)) + "8" + str(rng.randint(1, 7))
    t = 0
    for ch in num:
        if ch == "8":
            break
        t += int(ch)
    return f'let total = 0;\nfor (const ch of "{num}") {{\n  if (ch === "8") break;\n  total += Number(ch);\n}}\ntotal', t, "Digits are added up to the 8."


@_b
def brk_lcm(rng):
    a, b = rng.sample(range(2, 7), 2)
    n = 1
    while not (tmod(n, a) == 0 and tmod(n, b) == 0):
        n += 1
    return f"let n = 1;\nwhile (true) {{\n  if (n % {a} === 0 && n % {b} === 0) break;\n  n++;\n}}\nn", n, f"The first number both {a} and {b} divide into."


@_b
def brk_product_over(rng):
    xs = _digits(rng, 6, 2, 4)
    lim = rng.randint(20, 60)
    p = 1
    for x in xs:
        p *= x
        if p > lim:
            break
    return _of(xs, f"p *= x;\nif (p > {lim}) break;", "let p = 1;", "p"), p, f"Multiplies until the product is over {lim}."


@_b
def brk_skip_squares(rng):
    n = rng.randint(6, 9)
    return (f"const out = [];\nfor (let i = 0; i < {n}; i++) {{\n  if (i % 2 === 1) continue;\n  out.push(i * i);\n}}\nout", [i * i for i in range(n) if tmod(i, 2) == 0],
            "Only the even i are squared and kept.")


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
    return f"let n = {n0};\nwhile (n > {k}) n = Math.floor(n / 2);\nn", n, f"Halve (rounding down) until n is no more than {k}."


@_w
def wh_subtract_down(rng):
    s, m = rng.randint(3, 7), rng.randint(2, 6)
    n0 = rng.randint(20, 45)
    n = n0
    while n > m:
        n -= s
    return f"let n = {n0};\nwhile (n > {m}) n -= {s};\nn", n, f"Takes {s} off until n is no more than {m}; the last step may overshoot below it."


@_w
def wh_triple(rng):
    lim = rng.randint(30, 200)
    x = 1
    while x < lim:
        x *= 3
    return f"let x = 1;\nwhile (x < {lim}) x *= 3;\nx", x, f"1, 3, 9, 27 ... the first power of 3 that is {lim} or more."


@_w
def wh_double_plus(rng):
    a = rng.randint(1, 3)
    lim = rng.randint(20, 100)
    x = a
    while x < lim:
        x = x * 2 + 1
    return f"let x = {a};\nwhile (x < {lim}) x = x * 2 + 1;\nx", x, f"Each turn doubles and adds 1, until x reaches {lim} or more."


@_w
def wh_steps_down(rng):
    s = rng.randint(2, 6)
    n0 = rng.randint(15, 40)
    n, steps = n0, 0
    while n > 0:
        n -= s
        steps += 1
    return f"let n = {n0}, steps = 0;\nwhile (n > 0) {{ n -= {s}; steps++; }}\nsteps", steps, f"How many {s}s it takes to bring {n0} to zero or below."


@_w
def wh_digit_count(rng):
    n0 = rng.randint(10, 99999)
    n, c = n0, 0
    while n > 0:
        n = fdiv(n, 10)
        c += 1
    return f"let n = {n0}, count = 0;\nwhile (n > 0) {{ n = Math.floor(n / 10); count++; }}\ncount", c, "Each division by 10 drops the last digit; count counts the digits."


@_w
def wh_digit_sum(rng):
    n0 = rng.randint(100, 9999)
    n, t = n0, 0
    while n > 0:
        t += tmod(n, 10)
        n = fdiv(n, 10)
    return f"let n = {n0}, total = 0;\nwhile (n > 0) {{ total += n % 10; n = Math.floor(n / 10); }}\ntotal", t, "n % 10 is the last digit, the division drops it: the digits are added."


@_w
def wh_digit_reverse(rng):
    n0 = rng.randint(100, 9999)
    n, r = n0, 0
    while n > 0:
        r = r * 10 + tmod(n, 10)
        n = fdiv(n, 10)
    return f"let n = {n0}, rev = 0;\nwhile (n > 0) {{ rev = rev * 10 + n % 10; n = Math.floor(n / 10); }}\nrev", r, "Digits come off the end of n and go onto the end of rev: reversed."


@_w
def wh_collatz(rng):
    n0 = rng.randint(3, 12)
    n, steps = n0, 0
    while n != 1:
        n = fdiv(n, 2) if tmod(n, 2) == 0 else 3 * n + 1
        steps += 1
    return (f"let n = {n0}, steps = 0;\nwhile (n !== 1) {{\n  n = n % 2 === 0 ? n / 2 : 3 * n + 1;\n  steps++;\n}}\nsteps", steps,
            "Even: halve. Odd: triple and add 1. Count the turns until 1.")


@_w
def wh_gcd_mod(rng):
    a, b = rng.randint(6, 40), rng.randint(4, 30)
    a0, b0 = a, b
    while b:
        a, b = b, tmod(a, b)
    return f"let a = {a0}, b = {b0};\nwhile (b) [a, b] = [b, a % b];\na", a, "Euclid's way: replace (a, b) by (b, a % b) until b is 0; a is the common divisor."


@_w
def wh_gcd_sub(rng):
    a, b = rng.randint(4, 30), rng.randint(4, 30)
    a0, b0 = a, b
    while a != b:
        if a > b:
            a -= b
        else:
            b -= a
    return f"let a = {a0}, b = {b0};\nwhile (a !== b) {{\n  if (a > b) a -= b;\n  else b -= a;\n}}\na", a, "The bigger one loses the smaller one each turn until they meet."


@_w
def wh_next_multiple(rng):
    k = rng.randint(3, 9)
    n0 = rng.randint(10, 40)
    n = n0
    while tmod(n, k) != 0:
        n += 1
    return f"let n = {n0};\nwhile (n % {k} !== 0) n++;\nn", n, f"The first number from {n0} up that {k} divides exactly."


@_w
def wh_meet_i(rng):
    hi0 = rng.randint(8, 16)
    i, j = 0, hi0
    while i < j:
        i += 2
        j -= 1
    return f"let i = 0, j = {hi0};\nwhile (i < j) {{ i += 2; j--; }}\ni", i, "i climbs by 2 and j falls by 1 until they cross."


@_w
def wh_meet_j(rng):
    hi0 = rng.randint(8, 16)
    i, j = 1, hi0
    while i < j:
        i += 3
        j -= 1
    return f"let i = 1, j = {hi0};\nwhile (i < j) {{ i += 3; j--; }}\nj", j, "i climbs by 3 and j falls by 1 until i is no longer below j."


@_w
def wh_pop_digits(rng):
    xs = _digits(rng, rng.randint(3, 4))
    out, ys = 0, list(xs)
    while ys:
        out = out * 10 + ys.pop()
    return f"const xs = {_arr(xs)};\nlet n = 0;\nwhile (xs.length) n = n * 10 + xs.pop();\nn", out, "pop() takes from the END, so the digits are read backwards."


@_w
def wh_shift_front(rng):
    xs = _digits(rng, rng.randint(5, 6))
    keep = rng.randint(1, 3)
    return f"const xs = {_arr(xs)};\nwhile (xs.length > {keep}) xs.shift();\nxs", xs[-keep:], f"shift() removes the first item, until only {keep} are left."


@_w
def wh_string_shrink(rng):
    w = _word(rng, 5, 7)
    return f'let s = "{w}", count = 0;\nwhile (s) {{ s = s.slice(1); count++; }}\ncount', len(w), "An empty string is falsy, so the loop runs once per letter."


@_w
def wh_string_tail(rng):
    w = _word(rng, 5, 7)
    keep = rng.randint(2, 3)
    return f'let word = "{w}";\nwhile (word.length > {keep}) word = word.slice(1);\nword', w[-keep:], f"The front letter is dropped until {keep} are left."


@_w
def wh_popcount(rng):
    n0 = rng.randint(5, 60)
    n, bits = n0, 0
    while n > 0:
        bits += tmod(n, 2)
        n = fdiv(n, 2)
    return f"let n = {n0}, bits = 0;\nwhile (n > 0) {{ bits += n % 2; n = Math.floor(n / 2); }}\nbits", bits, "n % 2 is the lowest binary digit: bits counts the 1s."


@_w
def wh_binary_text(rng):
    n0 = rng.randint(2, 40)
    n, out = n0, ""
    while n > 0:
        out = str(tmod(n, 2)) + out
        n = fdiv(n, 2)
    return f'let n = {n0}, out = "";\nwhile (n > 0) {{ out = (n % 2) + out; n = Math.floor(n / 2); }}\nout', out, f"{n0} written in binary: each remainder goes in front (number + string makes a string)."


@_w
def wh_fib_over(rng):
    lim = rng.randint(20, 120)
    a, b = 1, 1
    while b < lim:
        a, b = b, a + b
    return f"let [a, b] = [1, 1];\nwhile (b < {lim}) [a, b] = [b, a + b];\nb", b, f"The first Fibonacci number that is {lim} or more."


@_w
def wh_triangular(rng):
    lim = rng.randint(10, 40)
    t, i = 0, 0
    while t < lim:
        i += 1
        t += i
    return f"let total = 0, i = 0;\nwhile (total < {lim}) {{ i++; total += i; }}\ni", i, f"How many of 1, 2, 3 ... it takes to add up to {lim} or more."


@_w
def wh_square_root(rng):
    n = rng.randint(5, 80)
    i = 0
    while i * i < n:
        i += 1
    return f"let i = 0;\nwhile (i * i < {n}) i++;\ni", i, f"The first i whose square is {n} or more."


@_w
def wh_countdown_list(rng):
    s, n0 = rng.randint(3, 4), rng.randint(8, 16)
    out, n = [], n0
    while n > 0:
        out.append(n)
        n -= s
    return f"const out = [];\nlet n = {n0};\nwhile (n > 0) {{ out.push(n); n -= {s}; }}\nout", out, f"Counts down from {n0} by {s} while n is above 0."


@_w
def wh_doubling_list(rng):
    lim = rng.randint(10, 60)
    a = rng.randint(1, 3)
    out, x = [], a
    while x < lim:
        out.append(x)
        x *= 2
    return f"const out = [];\nlet x = {a};\nwhile (x < {lim}) {{ out.push(x); x *= 2; }}\nout", out, f"Doubles from {a} while below {lim}."


@_w
def wh_two_conditions(rng):
    a0, b0 = rng.randint(0, 3), rng.randint(2, 6)
    a, b = a0, b0
    while a < 10 and b > 0:
        a += 3
        b -= 1
    return f"let a = {a0}, b = {b0};\nwhile (a < 10 && b > 0) {{ a += 3; b--; }}\na", a, "The loop ends as soon as either condition fails."


@_w
def wh_flag(rng):
    n0 = rng.randint(1, 20)
    n = n0
    while True:
        n += 1
        if tmod(n, 7) == 0:
            break
    return f"let n = {n0}, done = false;\nwhile (!done) {{\n  n++;\n  if (n % 7 === 0) done = true;\n}}\nn", n, f"Stops at the first multiple of 7 above {n0}."


@_w
def wh_do_while(rng):
    s, n0 = rng.randint(2, 5), rng.randint(1, 4)
    n = n0
    while True:
        n -= s
        if not n > 0:
            break
    return f"let n = {n0};\ndo n -= {s};\nwhile (n > 0);\nn", n, "do...while runs the body first, then checks: even with n already small it subtracts once."


@_w
def wh_do_while_count(rng):
    lim = rng.randint(0, 2)
    c, n = 0, 100
    while True:
        c += 1
        if not (n < lim):
            break
    return f"let count = 0;\ndo count++;\nwhile (100 < {lim});\ncount", c, "The condition is false from the start, but a do...while still runs its body once."


@_w
def wh_count_multiples(rng):
    n, k = rng.randint(8, 20), rng.randint(2, 4)
    c = len([i for i in range(1, n + 1) if tmod(i, k) == 0])
    return f"let i = 0, count = 0;\nwhile (i < {n}) {{\n  i++;\n  if (i % {k} === 0) count++;\n}}\ncount", c, f"Counts the multiples of {k} from 1 to {n}."


@_w
def wh_growing_step(rng):
    lim = rng.randint(15, 50)
    pos, step = 0, 1
    while pos < lim:
        pos += step
        step += 1
    return f"let pos = 0, step = 1;\nwhile (pos < {lim}) {{ pos += step; step++; }}\npos", pos, "The step grows by 1 each turn: pos is 1, 3, 6, 10, ..."


@_w
def wh_growth(rng):
    m0 = rng.choice((50, 100, 200))
    lim = m0 + m0 // 2
    m, years = m0, 0
    while m < lim:
        m += fdiv(m, 10)
        years += 1
    return f"let money = {m0}, years = 0;\nwhile (money < {lim}) {{ money += Math.floor(money / 10); years++; }}\nyears", years, "Each year adds a tenth (rounded down) of what is there."


@_w
def wh_negative_end(rng):
    n0 = rng.randint(7, 30)
    n = n0
    while n > 0:
        n -= 3
    return f"let x = {n0};\nwhile (x > 0) x -= 3;\nx", n, "x ends at 0 or below, wherever the last step lands."


@_w
def wh_scan(rng):
    xs = sorted(rng.sample(range(1, 20), rng.randint(4, 6)))
    t = rng.randint(3, 18)
    i = 0
    while i < len(xs) and xs[i] < t:
        i += 1
    return f"const xs = {_arr(xs)};\nlet i = 0;\nwhile (i < xs.length && xs[i] < {t}) i++;\ni", i, f"i stops at the first item that is {t} or more (or at the end)."


@_w
def wh_palindrome(rng):
    word = rng.choice(_PALINDROMES + _NOT_PALINDROMES)
    lo, hi = 0, len(word) - 1
    while lo < hi and word[lo] == word[hi]:
        lo += 1
        hi -= 1
    return (f'const w = "{word}";\nlet lo = 0, hi = w.length - 1;\nwhile (lo < hi && w[lo] === w[hi]) {{ lo++; hi--; }}\nlo >= hi', lo >= hi,
            "Two pointers walk inward while the letters match; they meet or cross only for a palindrome.")


@_w
def wh_div_quotient(rng):
    d, n0 = rng.randint(3, 7), rng.randint(20, 60)
    r, q = n0, 0
    while r >= d:
        r -= d
        q += 1
    return f"let r = {n0}, q = 0;\nwhile (r >= {d}) {{ r -= {d}; q++; }}\nq", q, f"Division by repeated subtraction: how many {d}s fit in {n0}."


@_w
def wh_odd_part(rng):
    n0 = rng.choice((12, 20, 24, 28, 36, 40, 44, 48, 56, 60, 72, 80))
    n = n0
    while tmod(n, 2) == 0:
        n = fdiv(n, 2)
    return f"let n = {n0};\nwhile (n % 2 === 0) n /= 2;\nn", n, "Keeps halving while n is even: what is left is odd."


@_w
def wh_string_grow(rng):
    w = rng.choice(("ab", "xyz", "go", "abc", "hi"))
    s = w
    while len(s) < 10:
        s += w
    return f'let s = "{w}";\nwhile (s.length < 10) s += "{w}";\ns.length', len(s), f"The text grows by {len(w)} until it has 10 or more characters."


@_w
def wh_descending_sum(rng):
    n0 = rng.randint(6, 15)
    n, t = n0, 0
    while n > 0:
        t += n
        n -= 2
    return f"let total = 0, n = {n0};\nwhile (n > 0) {{ total += n; n -= 2; }}\ntotal", t, f"Adds {n0}, {n0 - 2}, ... while n is above 0."


@_w
def wh_sum_powers(rng):
    lim = rng.randint(20, 150)
    n, t = 1, 0
    while n <= lim:
        t += n
        n *= 2
    return f"let n = 1, total = 0;\nwhile (n <= {lim}) {{ total += n; n *= 2; }}\ntotal", t, f"Adds 1, 2, 4, 8 ... while n is {lim} or less."


# ═══ 6. Comprehension Result ════════════════════════════════════════════
# JavaScript has no comprehension syntax: the same job is map / filter / reduce / flatMap, Set and Object.fromEntries.

COMP: list[Maker] = []
_c = _register(COMP)


def _obj(ks, vs) -> str:
    return "{ " + ", ".join(f"{k}: {v}" for k, v in zip(ks, vs)) + " }"


@_c
def comp_times(rng):
    xs, k = _digits(rng, rng.randint(3, 5)), rng.randint(2, 5)
    return f"const xs = {_arr(xs)};\nxs.map(x => x * {k})", [x * k for x in xs], f"One result per item: each times {k}."


@_c
def comp_filter(rng):
    xs, t = _digits(rng, rng.randint(5, 6)), rng.randint(3, 6)
    return f"const xs = {_arr(xs)};\nxs.filter(x => x > {t})", [x for x in xs if x > t], f"filter keeps only the items above {t}."


@_c
def comp_squares(rng):
    a = rng.randint(1, 3)
    b = a + rng.randint(3, 4)
    return f"Array.from({{ length: {b - a} }}, (_, i) => ({a} + i) ** 2)", [(a + i) ** 2 for i in range(b - a)], f"The squares of {a} to {b - 1}."


@_c
def comp_range_even(rng):
    n = rng.randint(6, 11)
    return f"[...Array({n}).keys()].filter(i => i % 2 === 0)", [i for i in range(n) if tmod(i, 2) == 0], "The even numbers below n."


@_c
def comp_odd_plus(rng):
    xs = _digits(rng, rng.randint(5, 6))
    return f"const xs = {_arr(xs)};\nxs.filter(x => x % 2 === 1).map(x => x + 1)", [x + 1 for x in xs if tmod(x, 2) == 1], "Only the odd items are kept, then each gets 1 added."


@_c
def comp_lengths(rng):
    ws = rng.sample(WORDS, rng.randint(3, 5))
    return f"{_arr(ws)}.map(w => w.length)", [len(w) for w in ws], "The length of each word."


@_c
def comp_first_letters(rng):
    ws = _short(rng, rng.randint(3, 4))
    return f"{_arr(ws)}.map(w => w[0])", [w[0] for w in ws], "The first letter of each word, as an array of one-letter strings."


@_c
def comp_join_first(rng):
    ws = rng.sample(WORDS, rng.randint(3, 5))
    return f'{_arr(ws)}.map(w => w[0]).join("")', "".join(w[0] for w in ws), "map to first letters, then join into one string."


@_c
def comp_from_entries_lengths(rng):
    ws = _short(rng, rng.randint(2, 3))
    return f"Object.fromEntries({_arr(ws)}.map(w => [w, w.length]))", _obj(ws, [len(w) for w in ws]), "Each [key, value] pair becomes a property."


@_c
def comp_from_entries_zip(rng):
    ks, vs = _short(rng, 3), _digits(rng, 3)
    return f"Object.fromEntries({_arr(ks)}.map((k, i) => [k, {_arr(vs)}[i]]))", _obj(ks, vs), "map gives the index too: it picks the value at the same position."


@_c
def comp_set_size(rng):
    xs = _digits(rng, rng.randint(5, 7), 1, 5)
    return f"new Set({_arr(xs)}).size", len(set(xs)), "A Set keeps each value once: size counts the different values."


@_c
def comp_unique(rng):
    xs = _digits(rng, rng.randint(5, 7), 1, 4)
    uniq = []
    for x in xs:
        if x not in uniq:
            uniq.append(x)
    return f"[...new Set({_arr(xs)})]", uniq, "A Set drops repeats but keeps the order of first appearance."


@_c
def comp_unique_sorted(rng):
    xs = _digits(rng, rng.randint(5, 7), 1, 5)
    uniq = []
    for x in xs:
        if x not in uniq:
            uniq.append(x)
    return f"[...new Set({_arr(xs)})].sort((a, b) => a - b)", _sorted_by(uniq, lambda v: v), "Repeats removed, then sorted by number."


@_c
def comp_sum_squares(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"{_arr(xs)}.reduce((acc, x) => acc + x * x, 0)", sum(x * x for x in xs), "reduce adds up the squares."


@_c
def comp_count_over(rng):
    xs, t = _digits(rng, rng.randint(5, 6)), rng.randint(3, 6)
    return f"const xs = {_arr(xs)};\nxs.filter(x => x > {t}).length", len([x for x in xs if x > t]), f"How many items are above {t}."


@_c
def comp_max_mod(rng):
    xs, k = _digits(rng, rng.randint(4, 5)), rng.randint(3, 5)
    return f"const xs = {_arr(xs)};\nMath.max(...xs.map(x => x % {k}))", max(tmod(x, k) for x in xs), f"The biggest remainder after dividing by {k}."


@_c
def comp_conditional(rng):
    xs, t = _digits(rng, rng.randint(4, 6)), rng.randint(3, 6)
    return f"const xs = {_arr(xs)};\nxs.map(x => (x > {t} ? x : 0))", [x if x > t else 0 for x in xs], "The ternary picks each result: small items become 0."


@_c
def comp_even_odd_words(rng):
    xs = _digits(rng, rng.randint(3, 4))
    return f'const xs = {_arr(xs)};\nxs.map(x => (x % 2 === 0 ? "even" : "odd"))', ["even" if tmod(x, 2) == 0 else "odd" for x in xs], "One word per item, chosen by the ternary."


@_c
def comp_booleans(rng):
    xs, t = _digits(rng, rng.randint(4, 5)), rng.randint(3, 6)
    return f"const xs = {_arr(xs)};\nxs.map(x => x > {t})", [x > t for x in xs], f"One true or false per item: is it above {t}?"


@_c
def comp_zip_mul(rng):
    n = rng.randint(3, 4)
    xs, ys = _digits(rng, n), _digits(rng, n)
    return f"const xs = {_arr(xs)};\nconst ys = {_arr(ys)};\nxs.map((x, i) => x * ys[i])", [xs[i] * ys[i] for i in range(n)], "map's second argument is the position, so ys[i] is the partner."


@_c
def comp_flat_map(rng):
    xs = _digits(rng, rng.randint(2, 3))
    out = []
    for x in xs:
        out += [x, x * 10]
    return f"const xs = {_arr(xs)};\nxs.flatMap(x => [x, x * 10])", out, "flatMap maps each item to an array and joins them into one flat array."


@_c
def comp_nested_lists(rng):
    n = rng.randint(3, 4)
    return f"Array.from({{ length: {n} }}, (_, i) => Array.from({{ length: i }}, (_, j) => j))", [list(range(i)) for i in range(n)], "An inner Array.from builds each row: row i is 0 to i - 1."


@_c
def comp_first_column(rng):
    grid = [_digits(rng, 3) for _ in range(rng.randint(2, 4))]
    return f"const grid = {_arr(grid)};\ngrid.map(row => row[0])", [row[0] for row in grid], "The first item of every row."


@_c
def comp_flatten(rng):
    grid = [_digits(rng, 2) for _ in range(rng.randint(2, 3))]
    return f"const grid = {_arr(grid)};\ngrid.flat()", [x for row in grid for x in row], "flat() joins the rows into one array."


@_c
def comp_row_sums(rng):
    grid = [_digits(rng, 3) for _ in range(rng.randint(2, 3))]
    return f"const grid = {_arr(grid)};\ngrid.map(row => row.reduce((a, b) => a + b, 0))", [sum(row) for row in grid], "One sum per row."


@_c
def comp_filter_keys(rng):
    ks, vs = _short(rng, 4), _digits(rng, 4)
    t = rng.randint(3, 6)
    return f"const o = {_obj(ks, vs)};\nObject.keys(o).filter(k => o[k] > {t})", [k for k, v in zip(ks, vs) if v > t], f"The keys whose value is above {t}."


@_c
def comp_entries_join(rng):
    ks, vs = _short(rng, 2), _digits(rng, 2)
    return f"const o = {_obj(ks, vs)};\nObject.entries(o).map(([k, v]) => k + v).join(\"-\")", "-".join(f"{k}{v}" for k, v in zip(ks, vs)), "Each [key, value] pair becomes key + value text."


@_c
def comp_count_equal(rng):
    xs, v = _digits(rng, 6, 1, 4), rng.randint(1, 4)
    return f"const xs = {_arr(xs)};\nxs.filter(x => x === {v}).length", len([x for x in xs if x == v]), f"How many items equal {v}."


@_c
def comp_consonants(rng):
    w = _word(rng, 4, 7)
    return f'[..."{w}"].filter(c => !"aeiou".includes(c)).join("")', "".join(c for c in w if c not in _VOWELS), "The vowels are filtered out."


@_c
def comp_double_chars(rng):
    w = _word(rng, 3, 5)
    return f'[..."{w}"].map(c => c + c).join("")', "".join(c * 2 for c in w), "Each letter appears twice."


@_c
def comp_vowels_list(rng):
    w = rng.choice([x for x in WORDS if len(x) >= 5])
    return f'[..."{w}"].filter(c => "aeiou".includes(c))', [c for c in w if c in _VOWELS], "The vowels, in the order they appear."


@_c
def comp_fizz(rng):
    n = rng.randint(7, 11)
    return (f"[...Array({n}).keys()].filter(x => x % 3 === 0 || x % 5 === 0)", [x for x in range(n) if tmod(x, 3) == 0 or tmod(x, 5) == 0],
            "Multiples of 3 or of 5 (0 counts as both).")


@_c
def comp_map_filter(rng):
    xs, t = _digits(rng, rng.randint(4, 5)), rng.randint(6, 12)
    return f"const xs = {_arr(xs)};\nxs.map(x => x * 2).filter(y => y > {t})", [y for y in [x * 2 for x in xs] if y > t], "Double first, then keep what is over the limit."


@_c
def comp_some(rng):
    xs, t = _digits(rng, rng.randint(4, 5)), rng.randint(5, 9)
    return f"const xs = {_arr(xs)};\nxs.some(x => x > {t})", any(x > t for x in xs), f"true if at least one item is above {t}."


@_c
def comp_every(rng):
    xs, t = _digits(rng, rng.randint(4, 5), 2, 9), rng.randint(2, 4)
    return f"const xs = {_arr(xs)};\nxs.every(x => x > {t})", all(x > t for x in xs), f"true only if every item is above {t}."


@_c
def comp_indexes(rng):
    xs, t = _digits(rng, rng.randint(5, 6)), rng.randint(3, 6)
    return f"const xs = {_arr(xs)};\nxs.flatMap((x, i) => (x > {t} ? [i] : []))", [i for i in range(len(xs)) if xs[i] > t], f"The positions (not the values) of items above {t}."


@_c
def comp_not_in(rng):
    xs, ys = _digits(rng, 6, 1, 6), _digits(rng, 3, 1, 6)
    return f"const xs = {_arr(xs)};\nconst ys = {_arr(ys)};\nxs.filter(x => !ys.includes(x))", [x for x in xs if x not in ys], "Items of xs that ys does not contain."


@_c
def comp_digits_list(rng):
    num = str(rng.randint(1000, 9999))
    return f'[..."{num}"].map(Number)', [int(c) for c in num], "Number turns each digit character into a number."


@_c
def comp_digit_sum(rng):
    n = rng.randint(100, 99999)
    return f'[..."{n}"].reduce((a, c) => a + Number(c), 0)', sum(int(c) for c in str(n)), "Spread the digits of the text, then add them as numbers."


@_c
def comp_to_strings(rng):
    xs = _digits(rng, rng.randint(3, 4))
    return f"{_arr(xs)}.map(String)", [str(x) for x in xs], "String(x) is text, so the array shows quotes."


@_c
def comp_floor_half(rng):
    xs = _digits(rng, rng.randint(4, 6))
    return f"const xs = {_arr(xs)};\nxs.map(x => Math.floor(x / 2))", [fdiv(x, 2) for x in xs], "Each item halved and rounded down."


@_c
def comp_parseint_trap(rng):
    d = rng.choice(("1", "2", "3"))
    # map passes (item, index, array); parseInt reads the index as the radix: radix 0 means 10, radix 1 is invalid,
    # and in radix 2 only the digits 0 and 1 are read.
    xs = [d, d, d]
    out = [int(d), "NaN", int(d) if int(d) < 2 else "NaN"]
    shown = "[ " + ", ".join(str(v) for v in out) + " ]"
    return f"{_arr(xs)}.map(parseInt)", shown, "map hands parseInt the index as a second argument, the radix: 0 means 10, 1 is invalid, 2 reads only 0s and 1s."


@_c
def comp_filter_boolean(rng):
    xs = [rng.choice((0, 0, 1, 2, 3, 4, 5)) for _ in range(rng.randint(5, 6))]
    return f"{_arr(xs)}.filter(Boolean)", [x for x in xs if x], "filter(Boolean) keeps the truthy items: 0 is dropped."


# ═══ 7. Enumerate Zip ═══════════════════════════════════════════════════
# JavaScript spells these entries(), forEach((x, i) => ...), map((x, i) => ...), reverse(), sort() and for...in.

ENUM: list[Maker] = []
_e = _register(ENUM)


@_e
def en_pairs(rng):
    xs = _digits(rng, rng.randint(2, 3))
    return f"const xs = {_arr(xs)};\n[...xs.entries()]", [[i, xs[i]] for i in range(len(xs))], "entries() pairs each item with its position, from 0."


@_e
def en_next_value(rng):
    xs = _digits(rng, 3)
    return f"const xs = {_arr(xs)};\nxs.entries().next().value", [0, xs[0]], "next() gives the first step of the iterator; its value is the [position, item] pair."


@_e
def en_start_offset(rng):
    xs = _digits(rng, rng.randint(2, 3))
    s = rng.randint(1, 5)
    return f"const xs = {_arr(xs)};\nxs.map((x, i) => [i + {s}, x])", [[s + i, xs[i]] for i in range(len(xs))], f"The numbering starts at {s}: i + {s}."


@_e
def en_weighted(rng):
    xs = _digits(rng, rng.randint(3, 4))
    return (f"const xs = {_arr(xs)};\nlet total = 0;\nfor (const [i, x] of xs.entries()) {{\n  total += i * x;\n}}\ntotal", sum(i * xs[i] for i in range(len(xs))),
            "i is the position, x the item: each is weighted by its position.")


@_e
def en_for_each_index(rng):
    xs, t = _digits(rng, rng.randint(5, 6)), rng.randint(3, 6)
    idx = -1
    for i in range(len(xs)):
        if xs[i] > t:
            idx = i
    return (f"const xs = {_arr(xs)};\nlet idx = -1;\nxs.forEach((x, i) => {{\n  if (x > {t}) idx = i;\n}});\nidx", idx,
            f"idx is replaced by every position holding an item above {t}, so the last one wins.")


@_e
def en_diagonal_letters(rng):
    ws = rng.sample([w for w in WORDS if len(w) >= 4], 3)
    return f'{_arr(ws)}.map((w, i) => w[i]).join("")', "".join(ws[i][i] for i in range(3)), "Letter 0 of the first word, letter 1 of the second, ..."


@_e
def en_zip_map(rng):
    n = rng.randint(2, 3)
    xs, ys = _digits(rng, n), _digits(rng, n)
    return f"const xs = {_arr(xs)};\nconst ys = {_arr(ys)};\nxs.map((x, i) => [x, ys[i]])", [[xs[i], ys[i]] for i in range(n)], "map's second argument is the position: it pairs each x with the y at the same place."


@_e
def en_zip_missing(rng):
    xs, ys = _digits(rng, 3), _digits(rng, 2)
    return (f"const xs = {_arr(xs)};\nconst ys = {_arr(ys)};\nxs.map((x, i) => [x, ys[i]])", [[xs[0], ys[0]], [xs[1], ys[1]], [xs[2], UNDEF]],
            "map follows the first array; a missing partner is undefined (Python's zip would stop short instead).")


@_e
def en_zip_dot(rng):
    n = rng.randint(2, 4)
    xs, ys = _digits(rng, n), _digits(rng, n)
    return (f"const xs = {_arr(xs)};\nconst ys = {_arr(ys)};\nlet total = 0;\nxs.forEach((x, i) => {{\n  total += x * ys[i];\n}});\ntotal", sum(xs[i] * ys[i] for i in range(n)),
            "Multiply the pair, add it in.")


@_e
def en_zip_sum(rng):
    n = rng.randint(3, 4)
    xs, ys = _digits(rng, n), _digits(rng, n)
    return f"const xs = {_arr(xs)};\nconst ys = {_arr(ys)};\nxs.map((x, i) => x + ys[i])", [xs[i] + ys[i] for i in range(n)], "Each item plus its partner."


@_e
def en_from_entries_zip(rng):
    ks, vs = _short(rng, 3), _digits(rng, 3)
    return f"Object.fromEntries({_arr(ks)}.map((k, i) => [k, {_arr(vs)}[i]]))", _obj(ks, vs), "Keys from the first array, values from the second."


@_e
def en_reverse_copy(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"const xs = {_arr(xs)};\n[...xs].reverse()", xs[::-1], "The spread makes a copy, so reverse() flips the copy."


@_e
def en_reverse_mutates(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"const xs = {_arr(xs)};\nxs.reverse();\nxs", xs[::-1], "reverse() changes the array itself, in place."


@_e
def en_reverse_alias(rng):
    xs = _digits(rng, rng.randint(3, 4))
    return f"const xs = {_arr(xs)};\nconst ys = xs.reverse();\nxs[0] === ys[0]", True, "reverse() returns the SAME array, so xs and ys are one array."


@_e
def en_reverse_loop(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"const xs = {_arr(xs)};\nconst out = [];\nfor (let i = xs.length - 1; i >= 0; i--) {{\n  out.push(xs[i] * 2);\n}}\nout", [x * 2 for x in xs[::-1]], "Last item first, each doubled."


@_e
def en_default_sort(rng):
    xs = rng.sample(range(1, 31), rng.randint(4, 5))
    return f"const xs = {_arr(xs)};\n[...xs].sort()", _text_sorted(xs), "sort() with no function compares the items as TEXT: \"10\" comes before \"9\"."


@_e
def en_default_sort_trap(rng):
    xs = [rng.choice((1, 2, 3, 9)), rng.randint(10, 19), rng.randint(20, 29), rng.randint(4, 9)]
    return f"const xs = {_arr(xs)};\n[...xs].sort()", _text_sorted(xs), "Text order: compare the first character, then the next - not the size of the number."


@_e
def en_numeric_sort(rng):
    xs = rng.sample(range(1, 31), rng.randint(4, 5))
    return f"const xs = {_arr(xs)};\n[...xs].sort((a, b) => a - b)", _sorted_by(xs, lambda v: v), "The compare function makes it a numeric sort, smallest first."


@_e
def en_numeric_sort_desc(rng):
    xs = rng.sample(range(1, 31), rng.randint(4, 5))
    return f"const xs = {_arr(xs)};\n[...xs].sort((a, b) => b - a)", _sorted_by(xs, lambda v: v)[::-1], "b - a flips the order: biggest first."


@_e
def en_sort_mutates(rng):
    xs = _digits(rng, rng.randint(4, 5), 1, 9)
    return f"const xs = {_arr(xs)};\nxs.sort((a, b) => a - b);\nxs", _sorted_by(xs, lambda v: v), "sort() works in place: xs itself is now in order."


@_e
def en_sort_copy_original(rng):
    xs = _digits(rng, rng.randint(4, 5))
    return f"const xs = {_arr(xs)};\nconst ys = [...xs].sort((a, b) => a - b);\nxs", xs, "The sort was done on a copy, so xs is unchanged."


@_e
def en_sorted_words(rng):
    ws = _fit(rng, rng.randint(3, 4))
    return f"{_arr(ws)}.sort()", _sorted_by(ws, lambda w: w), "Words sort alphabetically."


@_e
def en_sort_by_length(rng):
    ws = _fit(rng, 4)
    return f"{_arr(ws)}.sort((a, b) => a.length - b.length)", _sorted_by(ws, len), "Sorted by length; words of equal length keep their original order."


@_e
def en_longest(rng):
    ws = rng.sample(WORDS, 4)
    return f"{_arr(ws)}.sort((a, b) => a.length - b.length).at(-1)", _sorted_by(ws, len)[-1], "The last after sorting by length: a longest word (the later one of a tie)."


@_e
def en_diffs_slice(rng):
    xs = _digits(rng, rng.randint(4, 5))
    return f"const xs = {_arr(xs)};\nxs.slice(1).map((x, i) => x - xs[i])", [xs[i + 1] - xs[i] for i in range(len(xs) - 1)], "Each item minus the one before it: one fewer result than items."


@_e
def en_vowel_positions(rng):
    w = rng.choice([x for x in WORDS if len(x) >= 5])
    return (f'const out = [];\nfor (const [i, c] of [..."{w}"].entries()) {{\n  if ("aeiou".includes(c)) out.push(i);\n}}\nout', [i for i, c in enumerate(w) if c in _VOWELS],
            "The positions of the vowels, counting from 0.")


@_e
def en_even_positions(rng):
    xs = _digits(rng, rng.randint(4, 6))
    return (f"const xs = {_arr(xs)};\nlet total = 0;\nxs.forEach((x, i) => {{\n  if (i % 2 === 0) total += x;\n}});\ntotal", sum(xs[i] for i in range(0, len(xs), 2)),
            "Adds the items at positions 0, 2, 4 ...")


@_e
def en_odd_positions(rng):
    xs = _digits(rng, rng.randint(4, 6))
    return f"const xs = {_arr(xs)};\nxs.filter((x, i) => i % 2 === 1)", [xs[i] for i in range(1, len(xs), 2)], "filter also passes the position: keeps positions 1, 3, 5 ..."


@_e
def en_numbered(rng):
    ws = _short(rng, 3)
    return f"{_arr(ws)}.map((w, i) => (i + 1) + w[0]).join(\"\")", "".join(f"{i + 1}{ws[i][0]}" for i in range(3)), "Numbering from 1: the number, then the first letter."


@_e
def en_argmax(rng):
    xs = ints(rng, rng.randint(4, 6))
    return f"const xs = {_arr(xs)};\nxs.indexOf(Math.max(...xs))", xs.index(max(xs)), "Math.max finds the value, indexOf finds where it sits."


@_e
def en_for_in_indexes(rng):
    xs = _digits(rng, rng.randint(3, 4))
    return f'const xs = {_arr(xs)};\nlet out = "";\nfor (const i in xs) {{\n  out += i;\n}}\nout', "".join(str(i) for i in range(len(xs))), "for...in gives the keys, which are the positions as TEXT; += joins them."


@_e
def en_for_in_plus(rng):
    xs = _digits(rng, rng.randint(3, 4))
    return f"const xs = {_arr(xs)};\nlet total = 0;\nfor (const i in xs) {{\n  total += i;\n}}\ntotal", "0" + "".join(str(i) for i in range(len(xs))), "i is text (\"0\", \"1\", ...), so total becomes text: 0 + \"0\" is \"00\", and so on."


@_e
def en_for_in_type(rng):
    xs = _digits(rng, rng.randint(2, 4))
    return f"const xs = {_arr(xs)};\nlet kind = \"\";\nfor (const i in xs) kind = typeof i;\nkind", "string", "The keys given by for...in are always strings."


@_e
def en_for_of_vs_in(rng):
    xs = _digits(rng, rng.randint(3, 4))
    return f"const xs = {_arr(xs)};\nlet total = 0;\nfor (const x of xs) {{\n  total += x;\n}}\ntotal", sum(xs), "for...of gives the items themselves, so they add as numbers."


@_e
def en_object_keys_loop(rng):
    ks = _short(rng, 3)
    return f'const o = {_obj(ks, [1, 2, 3])};\nlet out = "";\nfor (const k in o) {{\n  out += k[0];\n}}\nout', "".join(k[0] for k in ks), "for...in over an object gives its keys, in the order they were written."


@_e
def en_entries_sum(rng):
    ks, vs = _short(rng, 3), _digits(rng, 3)
    return f"const o = {_obj(ks, vs)};\nlet total = 0;\nfor (const [k, v] of Object.entries(o)) {{\n  total += v;\n}}\ntotal", sum(vs), "Object.entries gives [key, value] pairs; only the values are added."


@_e
def en_entries_first(rng):
    ks, vs = _short(rng, 3), _digits(rng, 3)
    return f"const o = {_obj(ks, vs)};\nObject.entries(o)[0]", [ks[0], vs[0]], "The first [key, value] pair, as an array."


@_e
def en_interleave(rng):
    w1, w2 = rng.sample([w for w in WORDS if len(w) >= 3], 2)
    n = min(len(w1), len(w2))
    return (f'const a = "{w1}", b = "{w2}";\nArray.from({{ length: Math.min(a.length, b.length) }}, (_, i) => a[i] + b[i]).join("")', "".join(w1[i] + w2[i] for i in range(n)),
            "Letters are taken in pairs - one from each - until the shorter word ends.")


@_e
def en_char_pair(rng):
    w = _word(rng, 4, 6)
    k = rng.randint(0, len(w) - 1)
    return f'[...[..."{w}"].entries()][{k}]', [k, w[k]], "entries() over the letters pairs positions with letters."


@_e
def en_find_index(rng):
    xs = _digits(rng, rng.randint(5, 6), 1, 6)
    xs[rng.randint(1, len(xs) - 1)] = rng.randint(8, 9)
    first = [i for i in range(len(xs)) if xs[i] > 7][0]
    return f"const xs = {_arr(xs)};\nxs.findIndex(x => x > 7)", first, "findIndex gives the position of the first item above 7."


@_e
def en_median(rng):
    xs = _digits(rng, rng.choice((3, 5, 7)))
    s = _sorted_by(xs, lambda v: v)
    return f"const xs = {_arr(xs)};\n[...xs].sort((a, b) => a - b)[Math.floor(xs.length / 2)]", s[len(xs) // 2], "Sort, then take the middle item."


@_e
def en_second_largest(rng):
    xs = _digits(rng, rng.randint(4, 6))
    return f"const xs = {_arr(xs)};\n[...xs].sort((a, b) => a - b).at(-2)", _sorted_by(xs, lambda v: v)[-2], "Second from the end of the sorted array (a repeated biggest counts twice)."


@_e
def en_join_reversed(rng):
    ws = rng.sample(WORDS, rng.randint(3, 4))
    return f'{_arr(ws)}.reverse().join("-")', "-".join(ws[::-1]), "The words, last to first, joined with dashes."


@_e
def en_join_sorted(rng):
    ws = rng.sample(WORDS, rng.randint(3, 4))
    return f'{_arr(ws)}.sort().join(" ")', " ".join(_sorted_by(ws, lambda w: w)), "Alphabetical order, joined with spaces."


@_e
def en_match_position(rng):
    n = rng.randint(4, 5)
    xs, ys = _digits(rng, n, 1, 4), _digits(rng, n, 1, 4)
    pos = -1
    for i in range(n):
        if xs[i] == ys[i]:
            pos = i
    return (f"const xs = {_arr(xs)};\nconst ys = {_arr(ys)};\nlet pos = -1;\nxs.forEach((x, i) => {{\n  if (x === ys[i]) pos = i;\n}});\npos", pos,
            "The last position where both arrays hold the same value, or -1.")


@_e
def en_count_bigger(rng):
    n = rng.randint(4, 5)
    xs, ys = _digits(rng, n), _digits(rng, n)
    return (f"const xs = {_arr(xs)};\nconst ys = {_arr(ys)};\nlet count = 0;\nfor (let i = 0; i < xs.length; i++) {{\n  if (xs[i] > ys[i]) count++;\n}}\ncount", len([1 for i in range(n) if xs[i] > ys[i]]),
            "Counts the positions where xs beats ys.")


@_e
def en_pair_destructure(rng):
    pairs = [_digits(rng, 2) for _ in range(rng.randint(2, 3))]
    return f"let total = 0;\nfor (const [a, b] of {_arr(pairs)}) {{\n  total += a * b;\n}}\ntotal", sum(a * b for a, b in pairs), "Each inner array is unpacked into a and b."


@_e
def en_sorted_unique(rng):
    xs = _digits(rng, rng.randint(5, 7), 1, 6)
    uniq = []
    for x in xs:
        if x not in uniq:
            uniq.append(x)
    return f"const xs = {_arr(xs)};\n[...new Set(xs)].sort((a, b) => a - b)", _sorted_by(uniq, lambda v: v), "Set removes repeats; the compare function sorts the rest by number."


# ═══ 8. Loop Variable After ═════════════════════════════════════════════
# JavaScript: var leaks out of the loop (and out of a block), let and const do not; a for loop's i ends one step PAST
# the last value, because the failing test is what ends it.

AFTER: list[Maker] = []
_a = _register(AFTER)


def _overshoot(a: int, b: int, s: int) -> int:
    """What i is after `for (var i = a; i < b; i += s) {}`: the first value that fails the test."""
    i = a
    while i < b:
        i += s
    return i


def _splice_out(xs: list, i: int) -> None:
    del xs[i:i + 1]


@_a
def af_var_after(rng):
    n = rng.randint(2, 7)
    return f"for (var i = 0; i < {n}; i++) {{}}\ni", n, f"var leaks out of the loop, and i ends at {n}: the first value that fails i < {n}."


@_a
def af_var_after_step(rng):
    a, s = rng.randint(0, 3), rng.randint(2, 4)
    b = a + rng.randint(3 * s, 5 * s)
    return f"for (var i = {a}; i < {b}; i += {s}) {{}}\ni", _overshoot(a, b, s), "The loop ends when the test fails, so i holds the first value that is not below the limit."


@_a
def af_var_down(rng):
    n = rng.randint(2, 6)
    return f"for (var i = {n}; i > 0; i--) {{}}\ni", 0, "Counting down ends on the value that fails i > 0: 0."


@_a
def af_let_gone(rng):
    n = rng.randint(2, 7)
    return f"for (let i = 0; i < {n}; i++) {{}}\ntypeof i", "undefined", "let is scoped to the loop, so out here there is no i (typeof says undefined, it does not throw)."


@_a
def af_let_shadow(rng):
    v, n = rng.randint(10, 99), rng.randint(2, 5)
    return f"let i = {v};\nfor (let i = 0; i < {n}; i++) {{}}\ni", v, "The loop's let i is a new variable that hides the outer one only inside the loop."


@_a
def af_var_overwrite(rng):
    v, n = rng.randint(10, 99), rng.randint(2, 5)
    return f"var i = {v};\nfor (var i = 0; i < {n}; i++) {{}}\ni", n, "var does not make a new variable: it is the same i, so the loop overwrites it."


@_a
def af_of_var(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"const xs = {_arr(xs)};\nfor (var x of xs) {{}}\nx", xs[-1], "A var loop variable stays on the last item."


@_a
def af_of_const(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"const xs = {_arr(xs)};\nfor (const x of xs) {{}}\ntypeof x", "undefined", "const is scoped to the loop: after it, x does not exist."


@_a
def af_letter_var(rng):
    w = _word(rng)
    return f'for (var ch of "{w}") {{}}\nch', w[-1], "A var loop variable stays on the last letter."


@_a
def af_empty_init(rng):
    v = rng.randint(10, 99)
    return f"var i = {v};\nfor (i = 0; i < 0; i++) {{}}\ni", 0, "The first part of the for runs once even though the body never does: i is set to 0 (Python would keep the old value)."


@_a
def af_empty_of_keeps(rng):
    v = rng.randint(10, 99)
    return f"var x = {v};\nfor (x of []) {{}}\nx", v, "A for...of over nothing never assigns x, so it keeps its value."


@_a
def af_break_var(rng):
    k, t = rng.randint(2, 5), rng.randint(8, 25)
    last = 0
    while last < 10:
        if last * k > t:
            break
        last += 1
    return f"for (var i = 0; i < 10; i++) {{\n  if (i * {k} > {t}) break;\n}}\ni", last, f"The loop stops at the first i with i * {k} over {t}; i stays there."


@_a
def af_no_break_var(rng):
    k, n = rng.randint(2, 4), rng.randint(3, 6)
    return f"for (var i = 0; i < {n}; i++) {{\n  if (i * {k} > 100) break;\n}}\ni", n, "The condition is never true, so there is no break: the loop runs to the end and i is the failing value."


@_a
def af_var_block(rng):
    v = rng.randint(2, 9)
    return f"{{\n  var v = {v};\n}}\nv", v, "var ignores blocks: it belongs to the whole function (or script)."


@_a
def af_let_block(rng):
    v = rng.randint(2, 9)
    return f"{{\n  let v = {v};\n}}\ntypeof v", "undefined", "let belongs to its block, so v is gone after the closing brace."


@_a
def af_block_shadow(rng):
    a, b = rng.sample(range(1, 10), 2)
    return f"let x = {a};\n{{\n  let x = {b};\n}}\nx", a, "The inner let x is a different variable that only exists inside the braces."


@_a
def af_block_var_overwrite(rng):
    a, b = rng.sample(range(1, 10), 2)
    return f"var x = {a};\n{{\n  var x = {b};\n}}\nx", b, "Both var x are the same variable, so the block's assignment sticks."


@_a
def af_closure_var(rng):
    n = rng.randint(3, 4)
    return f"const fns = [];\nfor (var i = 0; i < {n}; i++) {{\n  fns.push(() => i);\n}}\nfns.map(f => f())", [n] * n, f"All the arrows share ONE i, which is {n} by the time they run."


@_a
def af_closure_let(rng):
    n = rng.randint(3, 4)
    return f"const fns = [];\nfor (let i = 0; i < {n}; i++) {{\n  fns.push(() => i);\n}}\nfns.map(f => f())", list(range(n)), "let gives every turn its own i, so each arrow keeps its own value."


@_a
def af_closure_let_times(rng):
    n, k = rng.randint(3, 4), rng.randint(2, 5)
    return f"const fns = [];\nfor (let i = 0; i < {n}; i++) {{\n  fns.push(() => i * {k});\n}}\nfns.map(f => f())", [i * k for i in range(n)], "Each turn has its own i, remembered by that turn's arrow."


@_a
def af_closure_var_iife(rng):
    n = rng.randint(3, 4)
    return (f"const fns = [];\nfor (var i = 0; i < {n}; i++) {{\n  ((j) => fns.push(() => j))(i);\n}}\nfns.map(f => f())", list(range(n)),
            "The immediately-called function copies i into its own j each turn, which is what let does for you.")


@_a
def af_foreach_last(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"const xs = {_arr(xs)};\nlet last;\nxs.forEach(x => {{\n  last = x;\n}});\nlast", xs[-1], "The callback assigns the outer last on every call."


@_a
def af_foreach_var_local(rng):
    xs = _digits(rng, rng.randint(3, 4))
    return f"const xs = {_arr(xs)};\nxs.forEach(x => {{\n  var seen = x;\n}});\ntypeof seen", "undefined", "A var inside a function belongs to that function, not to the code around it."


@_a
def af_map_unchanged(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"const xs = {_arr(xs)};\nxs.map(x => x * 2);\nxs", xs, "map returns a new array; the result was thrown away and xs is untouched."


@_a
def af_foreach_inplace(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"const xs = {_arr(xs)};\nxs.forEach((x, i) => {{\n  xs[i] = x * 2;\n}});\nxs", [x * 2 for x in xs], "xs[i] = ... assigns into the array itself."


@_a
def af_of_copy(rng):
    xs = _digits(rng, rng.randint(3, 5))
    return f"const xs = {_arr(xs)};\nfor (let x of xs) {{\n  x *= 2;\n}}\nxs", xs, "x is a copy of each number: doubling it leaves the array alone."


@_a
def af_of_rows_mutate(rng):
    grid = [_digits(rng, rng.randint(2, 3)) for _ in range(2)]
    return f"const grid = {_arr(grid)};\nfor (const row of grid) {{\n  row.push(0);\n}}\ngrid", [r + [0] for r in grid], "row IS the inner array, and push changes it in place."


@_a
def af_of_rows_rebind(rng):
    grid = [_digits(rng, 2) for _ in range(rng.randint(2, 3))]
    return f"const grid = {_arr(grid)};\nfor (let row of grid) {{\n  row = row.concat(0);\n}}\ngrid", grid, "concat builds a new array; only the name row moves to it."


@_a
def af_reassign_skips(rng):
    n = rng.randint(4, 9)
    c = 0
    i = 0
    while i < n:
        i += 1
        c += 1
        i += 1
    return f"let count = 0;\nfor (let i = 0; i < {n}; i++) {{\n  i++;\n  count++;\n}}\ncount", c, "Changing i inside the body DOES change the loop in JavaScript: each pass skips one."


@_a
def af_condition_recheck(rng):
    n0, cap = rng.randint(2, 4), rng.randint(4, 7)
    n, count, i = n0, 0, 0
    while i < n and count < cap:
        n += 1
        count += 1
        i += 1
    return (f"let n = {n0}, count = 0;\nfor (let i = 0; i < n && count < {cap}; i++) {{\n  n++;\n  count++;\n}}\nn", n,
            "The test i < n is checked fresh every turn, so growing n keeps the loop going until the other test stops it.")


@_a
def af_splice_forward(rng):
    xs = rng.sample(range(1, 10), rng.randint(5, 6))
    ys = list(xs)
    i = 0
    while i < len(ys):
        if tmod(ys[i], 2) == 0:
            _splice_out(ys, i)
        i += 1
    return (f"const xs = {_arr(xs)};\nfor (let i = 0; i < xs.length; i++) {{\n  if (xs[i] % 2 === 0) xs.splice(i, 1);\n}}\nxs", ys,
            "Removing shifts the next item into the spot just visited, so the loop skips it.")


@_a
def af_splice_backward(rng):
    xs = rng.sample(range(1, 10), rng.randint(5, 6))
    return (f"const xs = {_arr(xs)};\nfor (let i = xs.length - 1; i >= 0; i--) {{\n  if (xs[i] % 2 === 0) xs.splice(i, 1);\n}}\nxs", [x for x in xs if tmod(x, 2) == 1],
            "Going backwards, a removal only shifts items already visited: nothing is skipped.")


@_a
def af_of_remove(rng):
    xs = rng.sample(range(1, 10), rng.randint(5, 6))
    t = rng.randint(3, 6)
    ys = list(xs)
    i = 0
    while i < len(ys):
        if ys[i] > t:
            _splice_out(ys, i)
        i += 1
    return (f"const xs = {_arr(xs)};\nfor (const x of xs) {{\n  if (x > {t}) xs.splice(xs.indexOf(x), 1);\n}}\nxs", ys,
            "The loop walks by position: each removal makes it jump over the item that slides into its place.")


@_a
def af_of_pop(rng):
    xs = _digits(rng, rng.randint(4, 6))
    ys = list(xs)
    seen = []
    i = 0
    while i < len(ys):
        seen.append(ys[i])
        ys.pop()
        i += 1
    return (f"const xs = {_arr(xs)};\nconst seen = [];\nfor (const x of xs) {{\n  seen.push(x);\n  xs.pop();\n}}\nseen", seen,
            "The array shrinks from the end while the loop walks forward: they meet in the middle.")


@_a
def af_nested_var(rng):
    a, b = rng.randint(2, 4), rng.randint(2, 4)
    return f"for (var i = 0; i < {a}; i++) {{\n  for (var j = 0; j < {b}; j++) {{}}\n}}\n[i, j]", [a, b], "Each var ends on the value that failed its own test."


@_a
def af_nested_let(rng):
    a, b = rng.randint(2, 4), rng.randint(2, 4)
    return f"for (let i = 0; i < {a}; i++) {{\n  for (let j = 0; j < {b}; j++) {{}}\n}}\ntypeof i + typeof j", "undefinedundefined", "Neither let variable exists after its loop, so both typeofs say undefined."


@_a
def af_for_in_var(rng):
    ks = _short(rng, 3)
    return f"const o = {_obj(ks, [1, 2, 3])};\nfor (var k in o) {{}}\nk", ks[-1], "A var loop variable stays on the last key."


@_a
def af_for_in_const(rng):
    ks = _short(rng, 3)
    return f"const o = {_obj(ks, [1, 2, 3])};\nfor (const k in o) {{}}\ntypeof k", "undefined", "const is scoped to the loop, so k is gone afterwards."


@_a
def af_last_match(rng):
    xs, t = _digits(rng, rng.randint(4, 5)), rng.randint(5, 9)
    last = None
    for x in xs:
        if x > t:
            last = x
    return (f"const xs = {_arr(xs)};\nlet last = null;\nfor (const x of xs) {{\n  if (x > {t}) last = x;\n}}\nlast", last if last is not None else NULL,
            f"last holds the final item above {t}, or null if there was none.")


@_a
def af_add_index(rng):
    xs = _digits(rng, rng.randint(3, 4))
    return f"const xs = {_arr(xs)};\nfor (let i = 0; i < xs.length; i++) {{\n  xs[i] = xs[i] + i;\n}}\nxs", [xs[i] + i for i in range(len(xs))], "Each item gets its own position added, in place."


@_a
def af_swap_reverse(rng):
    xs = _digits(rng, rng.randint(4, 6))
    return (f"const xs = {_arr(xs)};\nfor (let i = 0; i < Math.floor(xs.length / 2); i++) {{\n  [xs[i], xs[xs.length - 1 - i]] = [xs[xs.length - 1 - i], xs[i]];\n}}\nxs", xs[::-1],
            "Swapping the ends inward, half way, reverses the array in place.")


@_a
def af_alias_grows(rng):
    xs = _digits(rng, 2)
    n = rng.randint(2, 3)
    return f"const xs = {_arr(xs)};\nconst ys = xs;\nfor (let i = 0; i < {n}; i++) {{\n  xs.push(i);\n}}\nys", xs + list(range(n)), "ys is the same array as xs, so it grows too."


@_a
def af_while_overshoot(rng):
    s, lim = rng.randint(3, 6), rng.randint(10, 20)
    return f"let i = 0;\nwhile (i < {lim}) i += {s};\ni", _overshoot(0, lim, s), f"i is not below {lim} when the loop ends: it overshoots in steps of {s}."


@_a
def af_string_original(rng):
    w = _word(rng, 3, 4)
    return f'let s = "{w}";\nfor (const ch of s) {{\n  s += "x";\n}}\ns', w + "x" * len(w), "The loop walks the original string; the new string does not change how many turns there are."


@_a
def af_array_original(rng):
    xs = _digits(rng, rng.randint(2, 3))
    return f"let xs = {_arr(xs)};\nfor (const x of xs) {{\n  xs = xs.concat(0);\n}}\nxs", xs + [0] * len(xs), "concat makes a new array each time; the loop keeps walking the first one."


@_a
def af_shared_row(rng):
    n, k = 2, rng.randint(1, 5)
    return (f"const grid = [], row = [];\nfor (let i = 0; i < {n}; i++) {{\n  row.push(i * {k});\n  grid.push(row);\n}}\ngrid", [[i * k for i in range(n)] for _ in range(n)],
            "grid holds the same array n times, so every row shows its final contents.")


@_a
def af_copied_row(rng):
    n = rng.randint(2, 3)
    return (f"const grid = [], row = [];\nfor (let i = 0; i < {n}; i++) {{\n  row.push(i);\n  grid.push([...row]);\n}}\ngrid", [list(range(k + 1)) for k in range(n)],
            "[...row] is a snapshot, so each row keeps what it had when it was added.")


@_a
def af_hoisting(rng):
    v = rng.randint(2, 9)
    return f"const before = typeof v;\nvar v = {v};\n[before, typeof v]", ["undefined", "number"], "A var is created (as undefined) before any code runs, so typeof v works early."


# ── END OF RANGE ──
