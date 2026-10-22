"""Logic and flow pack, JavaScript side.

The hand models (truthiness tables, value trees, boolean trees, branch chains,
bit loops) are in `_logic_py.py`, shared by both languages; this file holds the
JavaScript templates - where the answers differ from Python's (`??`, `[]` is
truthy, `&` binds looser than `==`, 32-bit bit operations, `(1 < x) < 5`)
and where the idea is the same with a different spelling.
tests/test_brain_packs.py runs every template through the real node.
"""

from __future__ import annotations

import random

from ._logic_py import (BITS_SHARED, BRANCH_SHARED, CLASSIC_SHARED, NAN, RANGE_SHARED, SAME_SHARED, TABLE_SHARED,
                        TERNARY_SHARED, B_RAW, _edge_x, _lohi, b_op, binstr, bind, bit_not, chain_item, decls, divides,
                        hexstr, i32, js_shl, js_shr, js_ushr, popcount, value_template, yn_item)
from ._model import NULL, UNDEF, Maker, find, ints, ipow, js_show, lit
from .items import Item

# ── 1. Which Value ──────────────────────────────────────────────────────

JS_VALUES: dict[str, list] = {
    "T": [("1", 1), ("2", 2), ("5", 5), ("9", 9), ("-1", -1), ('"hi"', "hi"), ('"ab"', "ab"), ('"0"', "0"),
          ("[]", []), ("[0]", [0]), ("[1, 2]", [1, 2]), ("true", True)],
    "F": [("0", 0), ('""', ""), ("null", NULL), ("undefined", UNDEF), ("false", False), ("NaN", NAN)],
}
JS_VALUES["X"] = JS_VALUES["T"] + JS_VALUES["F"]
JS_VALUES["N"] = [("null", NULL), ("undefined", UNDEF)]
JS_VALUES["V"] = [p for p in JS_VALUES["X"] if p[1] is not NULL and p[1] is not UNDEF]

_JS_ONLY_SPECS: list[tuple[str, object]] = [
    ("nn_v_x", ("nn", "V", "X")), ("nn_n_t", ("nn", "N", "T")), ("nn_n_n", ("nn", "N", "N")),
    ("nn_n_f", ("nn", "N", "F")), ("nn3_nnv", ("nn", ("nn", "N", "N"), "V")),
    ("nn_or_p", ("or", ("p", ("nn", "N", "F")), "T")), ("nn_in_p", ("nn", ("p", ("or", "F", "N")), "X")),
    ("and_nn_p", ("and", ("p", ("nn", "N", "T")), "X")), ("nn_and_p", ("nn", ("p", ("and", "F", "X")), "T")),
    ("nn_f_v", ("nn", "F", "V")),
]


def j_guard(rng: random.Random) -> Item:
    xs = ints(rng, rng.randint(2, 3)) if rng.random() < 0.6 else []
    prompt = f"const items = {lit(xs)};\nitems.length && items[0]"
    got = xs[0] if xs else 0
    return Item(prompt, js_show(got),
                "A non-empty array has a truthy length, so && goes on to items[0]." if xs
                else "length is 0, which is falsy, so && stops there and gives that 0.")


def j_default_count(rng: random.Random) -> Item:
    n = rng.choice([0, 0, 3, 7, 12])
    if rng.random() < 0.5:
        got = n if n else 10
        return Item(f"const count = {n};\ncount || 10", str(got),
                    "|| keeps a truthy count; 0 is falsy, so the default 10 replaces it.")
    return Item(f"const count = {n};\ncount ?? 10", str(n),
                "?? only replaces null and undefined, so a real 0 is kept.")


def j_prop_default(rng: random.Random) -> Item:
    v = rng.choice([0, 0, 4, 9])
    if rng.random() < 0.5:
        got = v if v else 7
        return Item(f"const o = {{ n: {v} }};\no.n || 7", str(got),
                    "|| treats 0 as missing and uses 7." if not v else "n is truthy, so || keeps it.")
    return Item(f"const o = {{ n: {v} }};\no.n ?? 7", str(v), "n is there (not null or undefined), so ?? keeps it - even 0.")


def j_missing_prop(rng: random.Random) -> Item:
    k = rng.choice(["a", "b", "x"])
    if rng.random() < 0.5:
        return Item(f'const o = {{}};\no.{k} ?? "none"', "none", "A missing property is undefined, so ?? gives the default.")
    return Item(f'const o = {{}};\no.{k}?.length ?? "none"', "none",
                "?. stops at undefined and gives undefined, so ?? gives the default.")


def j_zero_div_or(rng: random.Random) -> Item:
    a = rng.randint(1, 9)
    return Item(f"{a} || 1 / 0", str(a), f"{a} is truthy, so || stops there and never looks at 1 / 0.")


def j_zero_div_inf(rng: random.Random) -> Item:
    if rng.random() < 0.5:
        return Item("0 || 1 / 0", "Infinity", "0 is falsy, so || goes on: 1 / 0 is Infinity in JavaScript - not an error.")
    return Item("0 && 1 / 0", "0", "0 is falsy, so && stops there and gives it.")


def j_array_truthy(rng: random.Random) -> Item:
    n = rng.randint(2, 9)
    if rng.random() < 0.5:
        return Item(f"[] || {n}", "[]", "An empty array is truthy in JavaScript, so || keeps it.")
    return Item(f"[] && {n}", str(n), "An empty array is truthy in JavaScript, so && goes on to the right side.")


def j_str_zero(rng: random.Random) -> Item:
    n = rng.randint(2, 9)
    return Item(f'"0" || {n}', "0", "The string \"0\" is not empty, so it is truthy and || keeps it.")


def j_nan(rng: random.Random) -> Item:
    n = rng.randint(2, 9)
    if rng.random() < 0.5:
        return Item(f"NaN || {n}", str(n), "NaN is falsy, so || goes on.")
    return Item(f"NaN ?? {n}", "NaN", "NaN is not null or undefined, so ?? keeps it.")


def j_cmp_and_str(rng: random.Random) -> Item:
    a, b = ints(rng, 2)
    got = "yes" if a > b else False
    return Item(f'{a} > {b} && "yes"', js_show(got),
                f"{a} > {b} is {js_show(a > b)}: " + ("&& goes on and gives \"yes\"." if a > b else "&& stops and gives that false."))


def j_str_len(rng: random.Random) -> Item:
    s = rng.choice(["", "hi", "code", ""])
    if not s:
        return Item('const s = "";\nJSON.stringify(s && s.length)', '""',
                    "The empty string is falsy, so && stops there and gives it. (Wrapped so that it shows.)")
    return Item(f'const s = "{s}";\ns && s.length', str(len(s)), "s is truthy, so && goes on to its length.")


def j_cmp_idiom(rng: random.Random) -> Item:
    a, b = ints(rng, 2)
    got = "big" if a > b else "small"
    return Item(f'{a} > {b} && "big" || "small"', got,
                "&& then || as a choice: " + ("true, so && gives \"big\" and || keeps it." if a > b
                                              else "false, so && gives false and || replaces it."))


def j_not_not(rng: random.Random) -> Item:
    src, v = rng.choice([("[]", True), ('""', False), ('"0"', True), ("0", False), ("null", False), ("[0]", True), ("NaN", False)])
    return Item(f"!!{src}", js_show(v), f"!! turns any value into true or false: {src} is {'truthy' if v else 'falsy'}.")


JS_VALUE_CUSTOM: list[Maker] = [j_guard, j_default_count, j_prop_default, j_missing_prop, j_zero_div_or, j_zero_div_inf,
                                j_array_truthy, j_str_zero, j_nan, j_cmp_and_str, j_cmp_idiom, j_not_not]

# The shared and/or shapes first (minus ones that need Python's own values), then ?? and the JavaScript traps.
from ._logic_py import PY_VALUE_SPECS  # noqa: E402

JS_VALUE = ([value_template(tag, spec, JS_VALUES, "js") for tag, spec in PY_VALUE_SPECS + _JS_ONLY_SPECS]
            + JS_VALUE_CUSTOM)

# ── 2. Which Branch ─────────────────────────────────────────────────────

def run_switch(value, cases: list[tuple], default: str | None, init: str) -> str:
    """cases are (value, label or None, breaks?); the default (if any) is last. Matching is ===."""
    start = None
    for i, (v, _lab, _brk) in enumerate(cases):
        if type(v) is type(value) and v == value:
            start = i
            break
    label = init
    if start is None:
        return default if default is not None else init
    for v, lab, brk in cases[start:]:
        if lab is not None:
            label = lab
        if brk:
            return label
    return default if default is not None else label


def switch_item(src: str, value, cases: list[tuple], default: str | None, init: str, why: str) -> Item:
    lines = [f"const n = {src};", f'let label = "{init}";', "switch (n) {"]
    for v, lab, brk in cases:
        shown = lit(v) if isinstance(v, str) else str(v)
        body = f' label = "{lab}";' if lab is not None else ""
        lines.append(f"  case {shown}:{body}{' break;' if brk else ''}")
    if default is not None:
        lines.append(f'  default: label = "{default}";')
    lines.append("}")
    prompt = "\n".join(lines)
    return Item(prompt, run_switch(value, cases, default, init), why, check=prompt + "\nlabel")


_NUMWORDS = ["one", "two", "three", "four"]


def j_switch_break(rng: random.Random) -> Item:
    n = rng.randint(0, 4)
    cases = [(i, _NUMWORDS[i - 1], True) for i in (1, 2, 3)]
    return switch_item(str(n), n, cases, "many", "none", "The matching case runs and break leaves the switch; no match runs the default.")


def j_switch_fall(rng: random.Random) -> Item:
    n = rng.randint(1, 4)
    cases = [(1, "one", True), (2, "two", False), (3, "three", True)]
    return switch_item(str(n), n, cases, "many", "none", "Without a break a case falls through into the next one, so its label is overwritten.")


def j_switch_group(rng: random.Random) -> Item:
    n = rng.randint(1, 5)
    cases = [(1, None, False), (2, "low", True), (3, None, False), (4, "high", True)]
    return switch_item(str(n), n, cases, "other", "none", "A case with nothing under it falls through to the next one: 1 and 2 share a body, 3 and 4 share another.")


def j_switch_str(rng: random.Random) -> Item:
    w = rng.choice(["red", "green", "blue", "pink"])
    cases = [("red", "stop", True), ("green", "go", True), ("blue", "calm", True)]
    return switch_item(lit(w), w, cases, "unknown", "none", "The string is compared to each case in order; no match runs the default.")


def j_switch_nodefault(rng: random.Random) -> Item:
    n = rng.randint(0, 5)
    cases = [(1, "one", True), (2, "two", True), (3, "three", True)]
    return switch_item(str(n), n, cases, None, "none", "With no default and no match, label keeps its start value.")


def j_switch_strict(rng: random.Random) -> Item:
    k = rng.randint(1, 3)
    cases = [(1, "one", True), (2, "two", True), (3, "three", True)]
    return switch_item(f'"{k}"', str(k), cases, "many", "none", "switch compares with ===, so the string \"" + str(k) + "\" never matches the number.")


def j_switch_fall_all(rng: random.Random) -> Item:
    n = rng.randint(1, 3)
    cases = [(1, "a", False), (2, "b", False), (3, "c", False)]
    return switch_item(str(n), n, cases, "d", "none", "No case has a break, so everything from the match to the end runs - the default included.")


def j_if_array(rng: random.Random) -> Item:
    xs = ints(rng, rng.randint(1, 2)) if rng.random() < 0.4 else []
    cond = B_RAW("", "items", lambda e: True, ("items",))
    return chain_item("js", {"items": xs}, [(cond, "yes")], "no",
                      why="Every array is truthy in JavaScript, even an empty one - test items.length instead.")


def j_eq_coerce(rng: random.Random) -> Item:
    k = rng.randint(2, 9)
    n = rng.choice([k, k, k + 1])
    if rng.random() < 0.5:
        cond = B_RAW("", f'n == "{k}"', lambda e: e["n"] == k, ("n",))
        why = "== converts the string to a number first, so 5 == \"5\" is true."
    else:
        cond = B_RAW("", f'n === "{k}"', lambda e: False, ("n",))
        why = "=== never mixes a number with a string, so it is false."
    return chain_item("js", {"n": n}, [(cond, "same")], "different", why=why)


JS_BRANCH = [bind(f, "js") for f in BRANCH_SHARED] + [j_switch_break, j_switch_fall, j_switch_group, j_switch_str,
                                                      j_switch_nodefault, j_switch_strict, j_switch_fall_all,
                                                      j_if_array, j_eq_coerce]

# ── 3. Same Logic and 4. Truth Table Row ────────────────────────────────
# The same trees, printed with ! && || and === (the answers are the same: it is the spelling that differs).

JS_SAME = [bind(f, "js") for f in SAME_SHARED]
JS_TABLE = [bind(f, "js") for f in TABLE_SHARED]

# ── 5. Ternary Pick ─────────────────────────────────────────────────────

def jt_typeof(rng: random.Random) -> Item:
    src, got = rng.choice([("5", "num"), ('"5"', "other"), ("true", "other"), ("0", "num"), ("2.5", "num")])
    return Item(f'const v = {src};\ntypeof v === "number" ? "num" : "other"', got,
                "typeof tells the kind of value: a string \"5\" is not a number.")


def jt_null_check(rng: random.Random) -> Item:
    src, got = rng.choice([("null", "-1"), ("0", "0"), ("4", "4"), ("null", "-1"), ("7", "7")])
    return Item(f"const x = {src};\nx !== null ? x : -1", got, "Only null is replaced: 0 is a real value.")


def jt_loose(rng: random.Random) -> Item:
    k = rng.randint(2, 9)
    n = rng.choice([k, k + 1])
    return Item(f'const n = {n};\nn == "{k}" ? "same" : "diff"', "same" if n == k else "diff",
                "== turns the string into a number before comparing.")


def jt_loose_strict(rng: random.Random) -> Item:
    k = rng.randint(2, 9)
    return Item(f'const n = {k};\nn === "{k}" ? "same" : "diff"', "diff", "=== never equates a number with a string.")


JS_TERNARY = [bind(f, "js") for f in TERNARY_SHARED] + [jt_typeof, jt_null_check, jt_loose, jt_loose_strict]

# ── 6. Bit Ops ──────────────────────────────────────────────────────────
# JavaScript's bit operators work on 32-bit signed integers (and >>> on unsigned ones): the models are in _logic_py.

def jb_shl_wrap(rng: random.Random) -> Item:
    k = rng.choice((30, 31, 32, 33, 34))
    return Item(f"1 << {k}", str(js_shl(1, k)), "Bits are 32 wide: 1 << 31 lands on the sign bit (negative), and the shift count wraps at 32.")


def jb_shift_count(rng: random.Random) -> Item:
    n = rng.randint(2, 9)
    k = rng.choice((32, 33, 34))
    if rng.random() < 0.5:
        return Item(f"{n} << {k}", str(js_shl(n, k)), f"The shift count is taken modulo 32, so << {k} is << {k % 32}.")
    return Item(f"{n * 8} >> {k}", str(js_shr(n * 8, k)), f"The shift count is taken modulo 32, so >> {k} is >> {k % 32}.")


def jb_ushr_neg(rng: random.Random) -> Item:
    a = rng.randint(1, 16)
    k = rng.choice((1, 4, 8, 24, 28, 30))
    return Item(f"-{a} >>> {k}", str(js_ushr(-a, k)), ">>> treats the 32 bits as unsigned and fills with 0s, so a negative number comes out big and positive.")


def jb_ushr_zero(rng: random.Random) -> Item:
    a = rng.randint(1, 5)
    return Item(f"-{a} >>> 0", str(js_ushr(-a, 0)), ">>> 0 reads the 32 bits as an unsigned number: 2 to the power 32 minus " + str(a) + ".")


def jb_ushr_pos(rng: random.Random) -> Item:
    n = rng.randint(8, 99)
    k = rng.randint(1, 3)
    return Item(f"{n} >>> {k}", str(js_ushr(n, k)), f"For a positive number >>> {k} is the same as >> {k}.")


def jb_trunc_or(rng: random.Random) -> Item:
    x = rng.randint(11, 99) / 10 * rng.choice((1, -1))
    return Item(f"{x} | 0", str(i32(x)), "Bit operators turn the number into an integer first: the fraction is cut off toward zero.")


def jb_trunc_tilde(rng: random.Random) -> Item:
    x = rng.randint(11, 99) / 10 * rng.choice((1, -1))
    return Item(f"~~{x}", str(bit_not(bit_not(i32(x), 32), 32)), "~~ flips twice: a trick to cut off the fraction (toward zero).")


def jb_trunc_shift(rng: random.Random) -> Item:
    x = rng.randint(11, 99) / 10
    return Item(f"{x} >> 0", str(js_shr(x, 0)), "Shifting by 0 still converts to a 32-bit integer, cutting the fraction.")


def jb_wrap(rng: random.Random) -> Item:
    kind = rng.randrange(4)
    if kind == 0:
        return Item("2 ** 32 | 0", str(i32(ipow(2, 32))), "2 ** 32 does not fit in 32 bits: only the low 32 bits are kept, and they are all 0.")
    if kind == 1:
        return Item("2 ** 31 | 0", str(i32(ipow(2, 31))), "2 ** 31 sets the sign bit, so it wraps to a negative number.")
    if kind == 2:
        k = rng.randint(1, 9)
        return Item(f"(2 ** 32 + {k}) | 0", str(i32(ipow(2, 32) + k)), f"Only the low 32 bits survive, so the 2 ** 32 vanishes and {k} is left.")
    return Item("2147483647 + 1 | 0", str(i32(2147483648)), "The largest 32-bit integer plus 1 wraps round to the smallest.")


def jb_string(rng: random.Random) -> Item:
    a, b = rng.randint(2, 15), rng.randint(2, 15)
    op = rng.choice("&|^")
    return Item(f'"{a}" {op} {b}', str(b_op("js", op, a, b)), "Bit operators convert a string to a number first, so this is the same as with the number.")


def jb_string_shift(rng: random.Random) -> Item:
    a, k = rng.randint(2, 9), rng.randint(1, 3)
    return Item(f'"{a}" << {k}', str(js_shl(a, k)), "The string becomes a number before the shift.")


def jb_bool(rng: random.Random) -> Item:
    a, b = rng.random() < 0.5, rng.random() < 0.5
    op = rng.choice("&|^")
    got = b_op("js", op, int(a), int(b))
    return Item(f"{js_show(a)} {op} {js_show(b)}", str(got), "true counts as 1 and false as 0, and the answer is a number, not a boolean.")


def jb_nonnum(rng: random.Random) -> Item:
    src, val = rng.choice([("null", 0), ("undefined", 0), ("NaN", 0), ("Infinity", 0)])
    k = rng.randint(2, 9)
    return Item(f"{src} | {k}", str(k), f"{src} turns into 0 for a bit operator, so this is 0 | {k}.")


def jb_prec_eq(rng: random.Random) -> Item:
    a = rng.randint(2, 15)
    b = rng.choice((1, 2, 3))
    c = rng.choice((b, b + 1))
    got = b_op("js", "&", a, 1 if b == c else 0)
    return Item(f"{a} & {b} == {c}", str(got),
                f"In JavaScript == binds tighter than &, so this is {a} & ({b} == {c}): {a} & {js_show(b == c)}.")


def jb_prec_eq_odd(rng: random.Random) -> Item:
    n = rng.randint(1, 30)
    return Item(f"{n} & 1 == 0", "0", f"== binds tighter than &, so this is {n} & (1 == 0), which is {n} & false: always 0.")


def jb_tostring2(rng: random.Random) -> Item:
    n = rng.randint(2, 40)
    return Item(f"({n}).toString(2)", binstr(n), "toString(2) writes the number in binary, as text.")


def jb_tostring2_pad(rng: random.Random) -> Item:
    n = rng.randint(1, 100)
    return Item(f'({n}).toString(2).padStart(8, "0")', binstr(n, 8), "padStart adds zeros on the left until there are 8 digits.")


def jb_tostring16(rng: random.Random) -> Item:
    n = rng.randint(10, 255)
    return Item(f"({n}).toString(16)", hexstr(n), "toString(16) writes the number in hexadecimal, as text.")


def jb_parse2(rng: random.Random) -> Item:
    n = rng.randint(2, 31)
    return Item(f'parseInt("{binstr(n)}", 2)', str(n), "parseInt(text, 2) reads the text as binary digits.")


def jb_parse16(rng: random.Random) -> Item:
    n = rng.randint(16, 255)
    return Item(f'parseInt("{hexstr(n)}", 16)', str(n), "parseInt(text, 16) reads the text as hexadecimal digits.")


def jb_length(rng: random.Random) -> Item:
    n = rng.randint(1, 255)
    return Item(f"({n}).toString(2).length", str(len(binstr(n))), f"{n} is {binstr(n)} in binary: that many digits.")


def jb_popcount(rng: random.Random) -> Item:
    n = rng.randint(1, 255)
    return Item(f'({n}).toString(2).split("1").length - 1', str(popcount(n)), f"{n} is {binstr(n)} in binary; splitting on 1 gives one piece more than there are 1s.")


JS_BITS_ONLY: list[Maker] = [jb_shl_wrap, jb_shift_count, jb_ushr_neg, jb_ushr_zero, jb_ushr_pos, jb_trunc_or,
                             jb_trunc_tilde, jb_trunc_shift, jb_wrap, jb_string, jb_string_shift, jb_bool, jb_nonnum,
                             jb_prec_eq, jb_prec_eq_odd, jb_tostring2, jb_tostring2_pad, jb_tostring16, jb_parse2,
                             jb_parse16, jb_length, jb_popcount]
JS_BITS = [bind(f, "js") for f in BITS_SHARED] + JS_BITS_ONLY

# ── 7. In Range ─────────────────────────────────────────────────────────

def _js_cmp(op: str, a: int, b: int) -> bool:
    return {"<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b}[op]


def jr_chain_trap(rng: random.Random) -> Item:
    lo, hi = rng.randint(1, 5), rng.randint(6, 9)
    x = rng.choice((0, lo - 1, lo, lo + 1, hi - 1, hi, hi + 3, 20))
    op1, op2 = rng.choice([("<", "<"), ("<=", "<="), ("<", "<=")])
    left = 1 if _js_cmp(op1, lo, x) else 0
    got = _js_cmp(op2, left, hi)
    return yn_item("js", decls("js", {"x": x}), f"{lo} {op1} x {op2} {hi}", got,
                   f"JavaScript has no chained comparison: ({lo} {op1} x) is {js_show(left == 1)}, which counts as {left}, "
                   f"and then {left} {op2} {hi} is {js_show(got)} - whatever x is.")


def jr_chain_trap_down(rng: random.Random) -> Item:
    lo, hi = rng.randint(1, 4), rng.randint(6, 9)
    x = rng.choice((lo, lo + 1, hi - 1, hi, lo - 1, 20))
    left = 1 if hi > x else 0
    got = left > lo
    return yn_item("js", decls("js", {"x": x}), f"{hi} > x > {lo}", got,
                   f"({hi} > x) is true or false, which counts as 1 or 0, and then that is compared with {lo}: {left} > {lo} is {js_show(got)}.")


def jr_chain_01(rng: random.Random) -> Item:
    x = rng.choice((-2, 0, 0, 1, 2, 5))
    left = 1 if 0 < x else 0
    got = left < 1
    return yn_item("js", decls("js", {"x": x}), "0 < x < 1", got,
                   f"(0 < x) counts as {left}, and {left} < 1 is {js_show(got)}: true only when x is not above 0.")


def jr_in_array(rng: random.Random) -> Item:
    xs = ints(rng, 3, 10, 40)
    i = rng.choice((0, 1, 2, 3, 5))
    return yn_item("js", [f"const xs = {lit(xs)};"], f"{i} in xs", 0 <= i < len(xs),
                   f"in looks at the positions, not the values: xs has positions 0 to {len(xs) - 1}.")


def jr_in_array_value(rng: random.Random) -> Item:
    xs = ints(rng, 3, 10, 40)
    v = rng.choice(xs)
    return yn_item("js", [f"const xs = {lit(xs)};"], f"{v} in xs", False, f"in asks whether xs has a position named {v}: it has only 0 to 2.")


def jr_length_in(rng: random.Random) -> Item:
    return yn_item("js", [], '"length" in []', True, "length is a property of every array, so in finds it.")


def jr_indexof_truthy(rng: random.Random) -> Item:
    xs = ints(rng, 3, 3, 9)
    v = rng.choice(xs + [1])
    pos = xs.index(v) if v in xs else -1
    return yn_item("js", [f"const xs = {lit(xs)};"], f"xs.indexOf({v})", pos != 0,
                   f"indexOf gives the position: {pos}. Position 0 is falsy, and -1 (not found) is truthy.")


def jr_clamp(rng: random.Random) -> Item:
    lo, hi = _lohi(rng)
    x = _edge_x(rng, lo, hi)
    return yn_item("js", decls("js", {"x": x}), f"x === Math.min(Math.max(x, {lo}), {hi})", lo <= x <= hi,
                   f"Clamping x into {lo} to {hi} changes nothing only if it was already inside.")


def jr_endpoints(rng: random.Random) -> Item:
    lo, hi = _lohi(rng)
    x = _edge_x(rng, lo, hi)
    return yn_item("js", decls("js", {"x": x}), f"[{lo}, {hi}].includes(x)", x in (lo, hi), f"Only the two end values {lo} and {hi} are in the list.")


def jr_nan(rng: random.Random) -> Item:
    if rng.random() < 0.5:
        return yn_item("js", [], "NaN < 5 || NaN >= 5", False, "Every comparison with NaN is false - even both of these.")
    return yn_item("js", [], "NaN === NaN", False, "NaN is not equal to anything, itself included.")


def jr_nan_includes(rng: random.Random) -> Item:
    if rng.random() < 0.5:
        return yn_item("js", [], "[NaN].includes(NaN)", True, "includes treats NaN as equal to NaN.")
    return yn_item("js", [], "[NaN].indexOf(NaN) !== -1", False, "indexOf uses ===, and NaN === NaN is false, so it never finds NaN.")


def jr_num_in_str(rng: random.Random) -> Item:
    n = rng.choice([2, 0, 4, 7])
    year = "2024"
    return yn_item("js", [], f'"{year}".includes({n})', find(year, str(n)) != -1, f"includes turns {n} into the text \"{n}\" first.")


def jr_set_type(rng: random.Random) -> Item:
    n = rng.randint(1, 5)
    if rng.random() < 0.5:
        return yn_item("js", [], f'new Set([{n}, {n + 1}]).has("{n}")', False, "A Set tells a number from a string: \"" + str(n) + "\" is not " + str(n) + ".")
    return yn_item("js", [], f"new Set([{n}, {n + 1}]).has({n})", True, f"{n} is in the set.")


#: (expression, true?, why): comparisons that convert their sides.
_LOOSE = [
    ("null >= 0", True, "null becomes 0 for >=, but == never converts null that way."),
    ("null > 0", False, "null becomes 0, and 0 > 0 is false."),
    ("null == 0", False, "== treats null as equal only to undefined (and itself), never to 0."),
    ("undefined == null", True, "== treats undefined and null as equal."),
    ("undefined === null", False, "=== compares types too: they are different."),
    ("undefined >= 0", False, "undefined becomes NaN, and NaN compares false with everything."),
    ('"10" < 9', False, "One side is a number, so the string becomes 10 and 10 < 9 is false."),
    ('"10" < "9"', True, "Both are strings: compared character by character, \"1\" comes before \"9\"."),
    ('"10" > 9', True, "The string becomes the number 10, and 10 > 9 is true."),
    ('"abc" < 5', False, '"abc" becomes NaN, which compares false with everything.'),
    ('"5" == 5', True, "== converts the string to a number first."),
    ('"5" === 5', False, "=== compares types too: a string is not a number."),
    ('"" == 0', True, "The empty string becomes 0."),
    ('"0" == false', True, "false becomes 0 and the string \"0\" becomes 0."),
    ("[] == false", True, "An empty array becomes the empty string, then 0, like false."),
    ('"b" > "a"', True, "Strings compare by their character codes: b comes after a."),
    ("true > false", True, "true counts as 1 and false as 0."),
    ("0 == false", True, "false becomes 0."),
    ("0 === false", False, "=== compares types too: a number is not a boolean."),
    ("[1] == 1", True, "[1] becomes the text \"1\", then the number 1."),
]


def jr_loose(rng: random.Random) -> Item:
    src, truth, why = rng.choice(_LOOSE)
    return yn_item("js", [], src, truth, why)


def jr_between_fixed(rng: random.Random) -> Item:
    lo, hi = _lohi(rng)
    x = _edge_x(rng, lo, hi)
    return yn_item("js", decls("js", {"x": x}), f"x >= {lo} && x < {hi}", lo <= x < hi, f"x is {x}: from {lo} up to, not including, {hi}.")


JS_RANGE_ONLY: list[Maker] = [jr_chain_trap, jr_chain_trap_down, jr_chain_01, jr_in_array, jr_in_array_value, jr_length_in,
                              jr_indexof_truthy, jr_clamp, jr_endpoints, jr_nan, jr_nan_includes, jr_num_in_str,
                              jr_set_type, jr_loose, jr_between_fixed]
JS_RANGE = [bind(f, "js") for f in RANGE_SHARED] + JS_RANGE_ONLY

# ── 8. Leap & Fizz ──────────────────────────────────────────────────────
# The same classics in JavaScript's spelling (loops and arrow functions where Python has comprehensions); the
# negative-number % (div_neg) has its own answer in each language.

def jc_even_odd_str(rng: random.Random) -> Item:
    n = rng.randint(1, 40)
    return Item(f'const n = {n};\nn % 2 === 0 ? "even" : "odd"', "even" if n % 2 == 0 else "odd",
                "A remainder of 0 after dividing by 2 means even.")


def jc_float_mod(rng: random.Random) -> Item:
    n = rng.randint(1, 9)
    return Item(f"{n}.5 % 1", "0.5", "% works on fractions too: what is left after taking out whole 1s.")


def jc_mod_zero_nan(rng: random.Random) -> Item:
    n = rng.randint(1, 9)
    return Item(f"{n} % 0", "NaN", "Dividing by 0 with % gives NaN in JavaScript (Python raises an error).")


def jc_leap_date(rng: random.Random) -> Item:
    y = rng.choice((1900, 2000, 2023, 2024, 2100, 1996, 2400, 2200))
    leap_ = divides(y, 4) and (not divides(y, 100) or divides(y, 400))
    return Item(f"new Date({y}, 1, 29).getDate()", "29" if leap_ else "1",
                "Day 29 of February only exists in a leap year; otherwise the date rolls over to March 1.")


JS_CLASSIC = [bind(f, "js") for f in CLASSIC_SHARED] + [jc_even_odd_str, jc_float_mod, jc_mod_zero_nan, jc_leap_date]

# --END--
