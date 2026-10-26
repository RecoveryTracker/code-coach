"""SQL core pack, part 3: Scalar Math, Case & Subquery and Window Row.

Every answer is worked out by hand with `_sql_model.py` (integer division that cuts, ROUND away from zero, 1-based
SUBSTR, CASE taking the first WHEN that is true, a subquery as a loop over rows, a window as a sort and a walk with the
default frame that includes a row's peers), and tests/test_brain_packs.py runs every script in a fresh in-memory SQLite
(tests/sql_oracle.py). Most scalar questions have no table at all: the prompt is one `SELECT`.
"""

from __future__ import annotations

import random
from typing import Callable

from ._model import Maker, tdiv, tmod
from ._sql_model import (NULL, Retry, Tbl, avg_, fit, instr,
                         ints, lt, max_, rank_dense, row_number, running_sum, sql_item, sql_mod, sql_round, substr, with_nulls, words)


def _scalar(build: Callable[[random.Random], tuple[str, object, str]]) -> Maker:
    def make(rng: random.Random):
        query, answer, why = build(rng)
        return sql_item([], query, answer, why)
    make.__name__ = build.__name__
    return fit(make)


def _w(rng, n=1):
    ws = words(rng, n)
    return ws[0] if n == 1 else ws


# ── 1. Scalar Math ──────────────────────────────────────────────────────

def s_div(rng):
    a, b = rng.randint(5, 30), rng.randint(2, 7)
    return f"SELECT {a} / {b};", tdiv(a, b), "Two integers divide as integers: the fraction is thrown away."


def s_div_real(rng):
    a, b = rng.randint(5, 30), rng.randint(2, 7)
    return f"SELECT {a} / {b}.0;", a / b, "One side is a real, so the division keeps its fraction (and the answer has a decimal point)."


def s_div_neg(rng):
    a, b = rng.randint(5, 30), rng.randint(2, 7)
    return f"SELECT -{a} / {b};", tdiv(-a, b), "Integer division cuts toward zero, not down."


def s_mod(rng):
    a, b = rng.randint(5, 30), rng.randint(2, 7)
    return f"SELECT {a} % {b};", sql_mod(a, b), "% is the remainder after the division."


def s_mod_neg(rng):
    a, b = rng.randint(5, 30), rng.randint(2, 7)
    return f"SELECT -{a} % {b};", sql_mod(-a, b), "The remainder takes the sign of the left number."


def s_div_mul(rng):
    a, b = rng.randint(5, 30), rng.randint(2, 7)
    return f"SELECT {a} / {b} * {b};", tdiv(a, b) * b, "Left to right: the division cuts first, then it is multiplied back."


def s_mul_div(rng):
    a, b, c = rng.randint(3, 9), rng.randint(3, 9), rng.randint(2, 7)
    return f"SELECT {a} * {b} / {c};", tdiv(a * b, c), "Multiply first, then divide as integers."


def s_div_zero(rng):
    a = rng.randint(2, 30)
    return f"SELECT {a} / 0;", NULL, "SQLite does not raise an error for a zero divisor: it gives NULL."


def s_mod_zero(rng):
    a = rng.randint(2, 30)
    return f"SELECT {a} % 0;", NULL, "A zero divisor gives NULL for % too."


def s_div_plus(rng):
    a, b, c = rng.randint(5, 30), rng.randint(2, 7), rng.randint(2, 9)
    return f"SELECT {a} / {b} + {c};", tdiv(a, b) + c, "The division comes first and cuts; then c is added."


def s_real_mul(rng):
    a, b = rng.randint(5, 30), rng.randint(2, 7)
    return f"SELECT 1.0 * {a} / {b};", 1.0 * a / b, "1.0 * a is a real, so the division keeps the fraction."


def s_times_one(rng):
    a = rng.randint(2, 30)
    return f"SELECT {a} * 1.0;", a * 1.0, "A real in the product makes the answer a real: it prints with .0."


def s_float_sum(rng):
    return "SELECT 0.1 + 0.2;", 0.1 + 0.2, "Reals are binary fractions: 0.1 + 0.2 is not exactly 0.3."


def s_float_eq(rng):
    return "SELECT 0.1 + 0.2 = 0.3;", 0, "Because of that, the comparison is false (0)."


def s_round_one(rng):
    a = rng.randint(1, 9)
    d1, d2, d3 = rng.randint(0, 9), rng.choice((1, 2, 3, 6, 7, 8)), rng.randint(1, 9)
    x = float(f"{a}.{d1}{d2}{d3}")
    return f"SELECT ROUND({x}, 1);", sql_round(x, 1), "ROUND rounds to the digits asked and always returns a real."


def s_round_half(rng):
    a = rng.randint(1, 9)
    return f"SELECT ROUND({a}.5);", sql_round(a + 0.5), "A half rounds away from zero; ROUND gives a real."


def s_round_neg_half(rng):
    a = rng.randint(1, 9)
    return f"SELECT ROUND(-{a}.5);", sql_round(-(a + 0.5)), "A half rounds away from zero, which is down for a negative."


def s_round_third(rng):
    a = rng.choice([v for v in range(2, 20) if v % 3])
    return f"SELECT ROUND({a} / 3.0, 2);", sql_round(a / 3.0, 2), "The real quotient rounded to two decimals."


def s_abs(rng):
    a = rng.randint(2, 30)
    return f"SELECT ABS(-{a});", a, "ABS drops the sign."


def s_abs_diff(rng):
    a, b = ints(rng, 2, 2, 30)
    return f"SELECT ABS({a} - {b});", abs(a - b), "The distance between the two numbers."


def s_length(rng):
    w = _w(rng)
    return f"SELECT LENGTH('{w}');", len(w), "LENGTH counts characters."


def s_length_concat(rng):
    w, z = _w(rng, 2)
    return f"SELECT LENGTH('{w}' || '{z}');", len(w) + len(z), "The two words are joined first, then counted."


def s_length_number(rng):
    n = rng.randint(100, 99999)
    return f"SELECT LENGTH({n});", len(str(n)), "A number is counted as the text of its digits."


def s_substr_from(rng):
    w = _w(rng)
    i = rng.randint(2, len(w))
    return f"SELECT SUBSTR('{w}', {i});", substr(w, i), "SUBSTR counts from 1, not 0: from position i to the end."


def s_substr_len(rng):
    w = _w(rng)
    i = rng.randint(1, len(w) - 1)
    n = rng.randint(1, 3)
    return f"SELECT SUBSTR('{w}', {i}, {n});", substr(w, i, n), "SUBSTR(text, start, length): the start is 1-based."


def s_substr_neg(rng):
    w = _w(rng)
    k = rng.randint(1, 3)
    return f"SELECT SUBSTR('{w}', -{k});", substr(w, -k), "A negative start counts from the end of the text."


def s_substr_first(rng):
    w = _w(rng)
    return f"SELECT SUBSTR('{w}', 1, 1);", w[0], "Position 1 is the first letter."


def s_instr(rng):
    w = _w(rng)
    f = rng.choice(w)
    return f"SELECT INSTR('{w}', '{f}');", instr(w, f), "INSTR gives the 1-based position of the first match."


def s_instr_none(rng):
    w = _w(rng)
    return f"SELECT INSTR('{w}', 'zz');", 0, "INSTR gives 0 when the text is not found."


def s_replace(rng):
    w = _w(rng)
    f = rng.choice(w)
    return f"SELECT REPLACE('{w}', '{f}', '*');", w.replace(f, "*"), "REPLACE swaps every occurrence."


def s_upper(rng):
    w = _w(rng)
    return f"SELECT UPPER('{w}');", w.upper(), "UPPER makes the letters capitals."


def s_capitalise(rng):
    w = _w(rng)
    return f"SELECT UPPER(SUBSTR('{w}', 1, 1)) || SUBSTR('{w}', 2);", w[0].upper() + w[1:], "The first letter in capitals, then the rest as it was."


def s_concat(rng):
    w, z = _w(rng, 2)
    return f"SELECT '{w}' || '{z}';", w + z, "|| joins text."


def s_concat_null(rng):
    w = _w(rng)
    return f"SELECT '{w}' || NULL;", NULL, "Joining with NULL gives NULL."


def s_concat_int(rng):
    w, a = _w(rng), rng.randint(2, 9)
    return f"SELECT '{w}' || {a};", w + str(a), "A number is turned into text when it is joined."


def s_concat_nums(rng):
    a, b = ints(rng, 2, 2, 9)
    return f"SELECT {a} || {b};", f"{a}{b}", "|| makes the text of the two digits side by side."


def s_concat_plus(rng):
    a, b = ints(rng, 2, 2, 9)
    return f"SELECT {a} || {b} + 1;", int(f"{a}{b}") + 1, "|| ranks above +: the text is joined first, then it is read as a number."


def s_typeof(expr: str, kind: str, why: str):
    def build(rng):
        return f"SELECT typeof({expr});", kind, why
    build.__name__ = "typeof_" + kind
    return build


def s_text_plus(rng):
    a, b = ints(rng, 2, 2, 9)
    return f"SELECT '{a}' + {b};", a + b, "Text that looks like a number is read as one for +."


def s_word_plus(rng):
    w, a = _w(rng), rng.randint(2, 9)
    return f"SELECT '{w}' + {a};", a, "Text that is not a number counts as 0."


def s_text_eq(rng):
    a = rng.randint(2, 9)
    return f"SELECT '{a}' = {a};", 0, "A text and a number are never equal when they are plain values."


def s_real_eq(rng):
    a = rng.randint(2, 9)
    return f"SELECT {a} = {a}.0;", 1, "An integer and a real with the same value are equal."


def s_max_args(rng):
    a, b, c = ints(rng, 3, 2, 30)
    return f"SELECT MAX({a}, {b}, {c});", max(a, b, c), "With several arguments MAX is a plain function: the biggest."


def s_min_args(rng):
    a, b, c = ints(rng, 3, 2, 30)
    return f"SELECT MIN({a}, {b}, {c});", min(a, b, c), "With several arguments MIN gives the smallest."


def s_cast_real(rng):
    a = rng.randint(2, 9)
    return f"SELECT CAST({a}.9 AS INTEGER);", a, "CAST to INTEGER cuts the fraction off."


def s_cast_text(rng):
    a = rng.randint(2, 99)
    return f"SELECT CAST('{a}x' AS INTEGER);", a, "CAST reads the digits at the start and stops at the first other character."


def s_cast_junk(rng):
    w = _w(rng)
    return f"SELECT CAST('{w}' AS INTEGER);", 0, "Text with no leading digits casts to 0."


def s_cast_as_real(rng):
    a = rng.randint(2, 30)
    return f"SELECT CAST({a} AS REAL);", float(a), "A real prints with a decimal point."


def s_precedence(rng):
    a, b, c = rng.randint(2, 9), rng.randint(2, 9), rng.randint(2, 9)
    return f"SELECT {a} + {b} * {c};", a + b * c, "* before +."


def s_brackets(rng):
    a, b, c = rng.randint(2, 9), rng.randint(2, 9), rng.randint(2, 9)
    return f"SELECT ({a} + {b}) * {c};", (a + b) * c, "Brackets first."


def s_mixed(rng):
    a, b = rng.randint(5, 30), rng.randint(2, 7)
    return f"SELECT {a} / {b} + {a} % {b};", tdiv(a, b) + tmod(a, b), "Quotient plus remainder."


def s_multiple_check(rng):
    n = rng.randint(5, 30)
    return f"SELECT {n} / 4 * 4 = {n};", 1 if tdiv(n, 4) * 4 == n else 0, "True (1) only when the integer division lost nothing: a multiple of 4."


def s_int_vs_real_eq(rng):
    return "SELECT 7 / 2 = 3.5;", 0, "7 / 2 is the integer 3."


def s_trim(rng):
    w = _w(rng)
    return f"SELECT TRIM('  {w}  ') || '!';", w + "!", "TRIM removes the spaces at both ends."


def s_between(rng):
    n, a, b = rng.randint(1, 20), *sorted(ints(rng, 2, 3, 15))
    return f"SELECT {n} BETWEEN {a} AND {b};", 1 if a <= n <= b else 0, "BETWEEN includes both ends: 1 for true, 0 for false."


def s_in(rng):
    a, b, c, d = ints(rng, 4, 2, 9)
    return f"SELECT {a} IN ({b}, {c}, {d});", 0, "None of them equals a: 0."


def s_iif(rng):
    a, b = ints(rng, 2, 2, 9)
    w, z = _w(rng, 2)
    return f"SELECT IIF({a} > {b}, '{w}', '{z}');", w if a > b else z, "IIF(test, yes, no)."


def s_shift(rng):
    a, k = rng.randint(2, 9), rng.randint(1, 3)
    return f"SELECT {a} << {k};", a << k, "<< shifts the bits left: a times 2 to the k."


def s_bitand(rng):
    a = rng.randint(5, 30)
    return f"SELECT {a} & 1;", a & 1, "& 1 is 1 for an odd number."


def s_cmp_text(rng):
    return "SELECT 'B' < 'a';", 1, "Capital letters sort before lower-case ones."


def s_like_case(rng):
    return "SELECT 'apple' LIKE 'APPLE';", 1, "LIKE ignores case for ASCII letters."


def s_eq_case(rng):
    return "SELECT 'apple' = 'APPLE';", 0, "= is case-sensitive."


def s_int_then_real(rng):
    return "SELECT 5 / 2 * 2.0;", 4.0, "5 / 2 is the integer 2, then times 2.0 is the real 4.0."


def s_real_then_int(rng):
    return "SELECT 5 * 2.0 / 2;", 5.0, "5 * 2.0 is 10.0, and 10.0 / 2 is the real 5.0."


def s_upper_eq(rng):
    w = _w(rng)
    return f"SELECT UPPER('{w}') = '{w}';", 0, "The capitals differ from the original lower-case word."


def s_lower(rng):
    w = _w(rng).upper()
    return f"SELECT LOWER('{w}');", w.lower(), "LOWER makes the letters lower case."


def s_coalesce_num(rng):
    a = rng.randint(2, 9)
    return f"SELECT COALESCE(NULL, {a}, 0) + 1;", a + 1, "COALESCE gives a; then 1 is added."


def s_length_trim(rng):
    w = _w(rng)
    return f"SELECT LENGTH(TRIM('  {w}  '));", len(w), "The spaces are cut off before counting."


TYPEOFS = [
    ("1", "integer", "A whole number literal is an integer."),
    ("1.0", "real", "A number with a decimal point is a real."),
    ("'1'", "text", "Quotes make text, whatever is inside."),
    ("1 / 2", "integer", "Integer divided by integer is an integer."),
    ("1 / 2.0", "real", "A real in the division makes a real."),
    ("2 * 3", "integer", "Integer times integer."),
    ("1 || 2", "text", "|| always makes text."),
    ("'3' + 1", "integer", "The text is read as a number, and the sum of two integers is an integer."),
    ("3 + 0.0", "real", "Adding a real gives a real."),
    ("ROUND(2.5)", "real", "ROUND always returns a real."),
    ("LENGTH('ab')", "integer", "LENGTH is a whole number."),
    ("CAST(2.9 AS INTEGER)", "integer", "CAST made it an integer."),
]

SCALAR_BUILDS = [s_div, s_div_real, s_div_neg, s_mod, s_mod_neg, s_div_mul, s_mul_div, s_div_zero, s_mod_zero, s_div_plus,
                 s_real_mul, s_times_one, s_float_sum, s_float_eq, s_round_one, s_round_half, s_round_neg_half, s_round_third,
                 s_abs, s_abs_diff, s_length, s_length_concat, s_length_number, s_substr_from, s_substr_len, s_substr_neg,
                 s_substr_first, s_instr, s_instr_none, s_replace, s_upper, s_capitalise, s_concat, s_concat_null, s_concat_int,
                 s_concat_nums, s_concat_plus, s_text_plus, s_word_plus, s_text_eq, s_real_eq, s_max_args, s_min_args,
                 s_cast_real, s_cast_text, s_cast_junk, s_cast_as_real, s_precedence, s_brackets, s_mixed, s_multiple_check,
                 s_int_vs_real_eq, s_trim, s_between, s_in, s_iif, s_shift, s_bitand, s_cmp_text, s_like_case, s_eq_case,
                 s_int_then_real, s_real_then_int, s_upper_eq, s_lower, s_coalesce_num, s_length_trim]

SCALAR: list[Maker] = ([_scalar(b) for b in SCALAR_BUILDS] + [_scalar(s_typeof(e, k, why)) for e, k, why in TYPEOFS])


# ── 2. Case & Subquery ──────────────────────────────────────────────────

def _vals(rng: random.Random, n: int = 5, nulls: int = 0) -> Tbl:
    v = ints(rng, n, 1, 20)
    if nulls:
        v = with_nulls(rng, v, nulls)
    return Tbl("t", [("a", "INT")], [(x,) for x in v])


def _emp(rng: random.Random, n: int = 4) -> Tbl:
    ws = words(rng, n)
    sal = ints(rng, n, 1, 9)
    return Tbl("e", [("name", "TEXT"), ("sal", "INT")], list(zip(ws, sal)))


def k_case_two(rng):
    a, b = ints(rng, 2, 2, 9)
    w, z = _w(rng, 2)
    return sql_item([], f"SELECT CASE WHEN {a} > {b} THEN '{w}' ELSE '{z}' END;", w if a > b else z, "The first branch when the test is true, else the ELSE.")


def k_case_ranges(rng):
    x = rng.randint(1, 14)
    got = "low" if x < 5 else ("mid" if x < 10 else "high")
    return sql_item([], f"SELECT CASE WHEN {x} < 5 THEN 'low' WHEN {x} < 10 THEN 'mid' ELSE 'high' END;", got, "The WHENs are tried in order and the first true one wins.")


def k_case_order(rng):
    x = rng.randint(7, 12)
    return sql_item([], f"SELECT CASE WHEN {x} > 3 THEN 'a' WHEN {x} > 6 THEN 'b' ELSE 'c' END;", "a", "Both tests are true, but the first true WHEN wins: the second is never reached.")


def k_case_no_else(rng):
    a = rng.randint(2, 9)
    return sql_item([], f"SELECT CASE WHEN {a} > {a + 5} THEN 1 END;", NULL, "With no ELSE and no true WHEN the CASE gives NULL.")


def k_case_simple(rng):
    k = rng.randint(1, 4)
    got = {1: "one", 2: "two"}.get(k, "many")
    return sql_item([], f"SELECT CASE {k} WHEN 1 THEN 'one' WHEN 2 THEN 'two' ELSE 'many' END;", got, "CASE value WHEN x compares the value with each x in turn.")


def k_case_null(rng):
    return sql_item([], "SELECT CASE WHEN NULL = NULL THEN 'same' ELSE 'diff' END;", "diff", "NULL = NULL is unknown, not true: the ELSE runs.")


def k_case_null_simple(rng):
    return sql_item([], "SELECT CASE NULL WHEN NULL THEN 'same' ELSE 'diff' END;", "diff", "The simple CASE uses =, and NULL = NULL is not true.")


def k_sum_case(rng):
    t, k = _vals(rng), rng.randint(5, 14)
    n = sum(1 for (a,) in t.rows if a > k)
    return sql_item([t], f"SELECT SUM(CASE WHEN a > {k} THEN 1 ELSE 0 END) FROM t;", n, "1 for each row above k, 0 for the others: the sum is the count.")


def k_count_case(rng):
    t, k = _vals(rng), rng.randint(5, 14)
    n = sum(1 for (a,) in t.rows if a > k)
    return sql_item([t], f"SELECT COUNT(CASE WHEN a > {k} THEN 1 END) FROM t;", n, "The CASE gives NULL when it does not match, and COUNT skips NULLs.")


def k_count_case_else(rng):
    t, k = _vals(rng), rng.randint(5, 14)
    return sql_item([t], f"SELECT COUNT(CASE WHEN a > {k} THEN 1 ELSE 0 END) FROM t;", len(t.rows), "0 is not NULL, so COUNT counts every row.")


def k_sum_even(rng):
    t = _vals(rng)
    s = sum(a for (a,) in t.rows if a % 2 == 0)
    return sql_item([t], "SELECT SUM(CASE WHEN a % 2 = 0 THEN a ELSE 0 END) FROM t;", s, "Only the even numbers are added.")


def k_max_case(rng):
    n = 5
    a = ints(rng, n, 1, 20)
    b = [rng.choice("xy") for _ in range(n)]
    t = Tbl("t", [("a", "INT"), ("b", "TEXT")], list(zip(a, b)))
    xs = [v for v, c in zip(a, b) if c == "x"]
    return sql_item([t], "SELECT MAX(CASE WHEN b = 'x' THEN a END) FROM t;", max(xs) if xs else NULL, "Only the rows with b = x give a number; the others give NULL, which MAX skips.")


def k_range(rng):
    t = _vals(rng)
    v = [a for (a,) in t.rows]
    return sql_item([t], "SELECT (SELECT MAX(a) FROM t) - (SELECT MIN(a) FROM t);", max(v) - min(v), "Two scalar subqueries, each one value.")


def k_top(rng):
    t = _vals(rng)
    return sql_item([t], "SELECT a FROM t WHERE a = (SELECT MAX(a) FROM t);", max(a for (a,) in t.rows), "The subquery gives the biggest a; the outer query finds that row.")


def k_above_avg(rng):
    t = _vals(rng)
    avg = avg_([a for (a,) in t.rows])
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE a > (SELECT AVG(a) FROM t);", sum(1 for (a,) in t.rows if a > avg), "The subquery is the average: the rows above it are counted.")


def k_below_max(rng):
    t = _vals(rng, nulls=1)
    m = max_([a for (a,) in t.rows])
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE a < (SELECT MAX(a) FROM t);", sum(1 for (a,) in t.rows if lt(a, m) is True), "Every row below the maximum; the NULL row is unknown, so it is left out.")


def _two(rng: random.Random):
    t = _vals(rng, 5)
    u = Tbl("u", [("x", "INT")], [(x,) for x in rng.sample([a for (a,) in t.rows], 2) + [rng.randint(21, 25)]])
    return t, u


def k_in_sub(rng):
    t, u = _two(rng)
    xs = [x for (x,) in u.rows]
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE a IN (SELECT x FROM u);", sum(1 for (a,) in t.rows if a in xs), "The rows of t whose a is one of u's values.")


def k_not_in_sub(rng):
    t, u = _two(rng)
    xs = [x for (x,) in u.rows]
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE a NOT IN (SELECT x FROM u);", sum(1 for (a,) in t.rows if a not in xs), "The rows whose a is not among u's values.")


def k_exists(rng):
    t, u = _two(rng)
    xs = [x for (x,) in u.rows]
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE EXISTS (SELECT 1 FROM u WHERE u.x = t.a);", sum(1 for (a,) in t.rows if a in xs), "For each t row the subquery looks for a matching u row.")


def k_not_in_null(rng):
    t, u = _two(rng)
    u = Tbl("u", u.cols, u.rows[:2] + [(None,)])
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE a NOT IN (SELECT x FROM u);", 0, "u contains a NULL, so NOT IN is never true.")


def k_not_exists_null(rng):
    t, u = _two(rng)
    u = Tbl("u", u.cols, u.rows[:2] + [(None,)])
    xs = [x for (x,) in u.rows if x is not None]
    return sql_item([t, u], "SELECT COUNT(*) FROM t WHERE NOT EXISTS (SELECT 1 FROM u WHERE u.x = t.a);", sum(1 for (a,) in t.rows if a not in xs), "NOT EXISTS is not fooled by the NULL: it counts the rows with no equal x.")


def _parents(rng: random.Random):
    ids = ints(rng, 3, 1, 5)
    a = Tbl("a", [("id", "INT")], [(i,) for i in ids])
    keys = [rng.choice(ids) for _ in range(4)]
    keys[1] = keys[0]
    b = Tbl("b", [("aid", "INT")], [(k,) for k in keys])
    return a, b


def k_correlated(rng):
    a, b = _parents(rng)
    n = sum(1 for (i,) in a.rows if sum(1 for (k,) in b.rows if k == i) > 1)
    return sql_item([a, b], "SELECT COUNT(*) FROM a WHERE (SELECT COUNT(*) FROM b WHERE b.aid = a.id) > 1;", n, "For each a the subquery counts its b rows; the ids with more than one are counted.")


def k_correlated_zero(rng):
    a, b = _parents(rng)
    n = sum(1 for (i,) in a.rows if sum(1 for (k,) in b.rows if k == i) == 0)
    return sql_item([a, b], "SELECT COUNT(*) FROM a WHERE (SELECT COUNT(*) FROM b WHERE b.aid = a.id) = 0;", n, "The a rows that have no b row.")


def k_top_name(rng):
    e = _emp(rng)
    top = max(e.rows, key=lambda r: r[1])
    return sql_item([e], "SELECT name FROM e WHERE sal = (SELECT MAX(sal) FROM e);", top[0], "The subquery gives the biggest salary; the outer query names its owner.")


def k_low_name(rng):
    e = _emp(rng)
    low = min(e.rows, key=lambda r: r[1])
    return sql_item([e], "SELECT name FROM e WHERE sal = (SELECT MIN(sal) FROM e);", low[0], "The smallest salary's owner.")


def k_second(rng):
    e = _emp(rng)
    ordered = sorted(e.rows, key=lambda r: -r[1])
    return sql_item([e], "SELECT name FROM e e1 WHERE (SELECT COUNT(*) FROM e e2 WHERE e2.sal > e1.sal) = 1;", ordered[1][0], "Exactly one person earns more: the second highest.")


def k_second_lowest(rng):
    e = _emp(rng)
    ordered = sorted(e.rows, key=lambda r: r[1])
    return sql_item([e], "SELECT name FROM e WHERE sal = (SELECT MIN(sal) FROM e WHERE sal > (SELECT MIN(sal) FROM e));", ordered[1][0], "The inner subquery is the lowest salary; the next one gives the second lowest.")


def k_null_count(rng):
    t = _vals(rng, nulls=1)
    return sql_item([t], "SELECT (SELECT COUNT(*) FROM t) - (SELECT COUNT(a) FROM t);", 1, "All the rows minus the rows with a number: the NULLs.")


def k_derived(rng):
    t, k = _vals(rng), rng.randint(5, 14)
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT a FROM t WHERE a > {k});", sum(1 for (a,) in t.rows if a > k), "The inner query is a small table of the rows above k; the outer counts them.")


def k_exists_case(rng):
    t, k = _vals(rng), rng.randint(5, 18)
    got = "yes" if any(a > k for (a,) in t.rows) else "no"
    return sql_item([t], f"SELECT CASE WHEN EXISTS (SELECT 1 FROM t WHERE a > {k}) THEN 'yes' ELSE 'no' END;", got, "EXISTS is true when the subquery finds any row.")


def k_count_case_sub(rng):
    t, k = _vals(rng), rng.randint(3, 6)
    got = "big" if len(t.rows) > k else "small"
    return sql_item([t], f"SELECT CASE WHEN (SELECT COUNT(*) FROM t) > {k} THEN 'big' ELSE 'small' END;", got, "The subquery counts the rows; the CASE compares that with k.")


def k_empty_sub(rng):
    t = _vals(rng)
    return sql_item([t], "SELECT IFNULL((SELECT a FROM t WHERE a > 99), -1);", -1, "A scalar subquery that finds no row gives NULL, and IFNULL replaces it.")


def k_sum_above_avg(rng):
    t = _vals(rng)
    avg = avg_([a for (a,) in t.rows])
    return sql_item([t], "SELECT SUM(a) FROM t WHERE a > (SELECT AVG(a) FROM t);", sum(a for (a,) in t.rows if a > avg), "The rows above the average are added.")


def k_missing_row(rng):
    t = _vals(rng)
    return sql_item([t], "SELECT COUNT(*) FROM t WHERE a > (SELECT a FROM t WHERE a = 99);", 0, "The subquery finds nothing and gives NULL: a > NULL is never true.")


def k_in_filtered(rng):
    t = _vals(rng)
    k, m = rng.randint(4, 8), rng.randint(10, 18)
    n = sum(1 for (a,) in t.rows if a > k and a < m)
    return sql_item([t], f"SELECT COUNT(*) FROM t WHERE a IN (SELECT a FROM t WHERE a > {k}) AND a < {m};", n, "In the subquery's rows (a > k) and also below m.")


def k_case_sum_two(rng):
    t = _vals(rng)
    k = rng.randint(6, 14)
    s = sum(a if a > k else -a for (a,) in t.rows)
    return sql_item([t], f"SELECT SUM(CASE WHEN a > {k} THEN a ELSE -a END) FROM t;", s, "The big ones count plus, the others minus.")


def k_case_label_count(rng):
    t = _vals(rng)
    k = rng.randint(6, 14)
    labels = ["big" if a > k else "small" for (a,) in t.rows]
    return sql_item([t], f"SELECT COUNT(*) FROM (SELECT CASE WHEN a > {k} THEN 'big' ELSE 'small' END AS s FROM t) WHERE s = 'big';", labels.count("big"), "Each row is labelled, then the 'big' labels are counted.")


def k_case_null_branch(rng):
    t = _vals(rng, nulls=1)
    k = rng.randint(6, 14)
    n = sum(1 for (a,) in t.rows if a is None or a <= k)
    return sql_item([t], f"SELECT SUM(CASE WHEN a > {k} THEN 0 ELSE 1 END) FROM t;", n, "For the NULL row the test is unknown, so the ELSE runs: it counts as 1.")


def k_nested_case(rng):
    a, b = ints(rng, 2, 1, 9)
    inner = "p" if a > 5 else "q"
    got = inner if b > 5 else "r"
    return sql_item([], f"SELECT CASE WHEN {b} > 5 THEN CASE WHEN {a} > 5 THEN 'p' ELSE 'q' END ELSE 'r' END;", got, "The outer CASE chooses first; the inner one only runs for its branch.")


def k_max_sub_min(rng):
    e = _emp(rng)
    s = sorted(r[1] for r in e.rows)
    return sql_item([e], "SELECT MAX(sal) - MIN(sal) FROM e;", s[-1] - s[0], "The spread of the salaries.")


def k_name_above_avg_count(rng):
    e = _emp(rng)
    avg = avg_([r[1] for r in e.rows])
    return sql_item([e], "SELECT COUNT(*) FROM e WHERE sal > (SELECT AVG(sal) FROM e);", sum(1 for r in e.rows if r[1] > avg), "The salaries above the average salary.")


CASES: list[Maker] = [fit(f) for f in (
    k_case_two, k_case_ranges, k_case_order, k_case_no_else, k_case_simple, k_case_null, k_case_null_simple, k_sum_case,
    k_count_case, k_count_case_else, k_sum_even, k_max_case, k_range, k_top, k_above_avg, k_below_max, k_in_sub, k_not_in_sub,
    k_exists, k_not_in_null, k_not_exists_null, k_correlated, k_correlated_zero, k_top_name, k_low_name, k_second,
    k_second_lowest, k_null_count, k_derived, k_exists_case, k_count_case_sub, k_empty_sub, k_sum_above_avg, k_missing_row,
    k_in_filtered, k_case_sum_two, k_case_label_count, k_case_null_branch, k_nested_case, k_max_sub_min, k_name_above_avg_count)]


# ── 3. Window Row ───────────────────────────────────────────────────────

def _scores(rng: random.Random, ties: str = "none", letters: bool = False, n: int = 5) -> Tbl:
    """t(n TEXT, s INT): five names; `ties` is none, 'mid' (two rows tie, not at the top) or 'top' (two tie for first)."""
    ns = list("abcde")[:n] if letters else words(rng, n)
    vals = ints(rng, n, 1, 9)
    if ties == "mid":
        vals = sorted(vals)
        vals[1] = vals[2]
        rng.shuffle(vals)
    elif ties == "top":
        vals = sorted(vals)
        vals[-2] = vals[-1]
        rng.shuffle(vals)
    return Tbl("t", [("n", "TEXT"), ("s", "INT")], list(zip(ns, vals)))


def _pick(rng: random.Random, t: Tbl):
    return rng.choice(t.rows)


def w_row_number(rng):
    t = _scores(rng)
    name = _pick(rng, t)[0]
    rn = {x[0]: i for x, i in row_number(t.rows, lambda x: x[1])}[name]
    return sql_item([t], f"SELECT rn FROM (SELECT n, ROW_NUMBER() OVER (ORDER BY s) AS rn FROM t) WHERE n = '{name}';", rn, "ROW_NUMBER numbers the rows 1, 2, 3 ... in the order of s.")


def w_row_number_desc(rng):
    t = _scores(rng)
    name = _pick(rng, t)[0]
    rn = {x[0]: i for x, i in row_number(t.rows, lambda x: x[1], True)}[name]
    return sql_item([t], f"SELECT rn FROM (SELECT n, ROW_NUMBER() OVER (ORDER BY s DESC) AS rn FROM t) WHERE n = '{name}';", rn, "Sorted from the biggest s: the biggest is row 1.")


def w_nth_name(rng):
    t = _scores(rng)
    k = rng.randint(1, 5)
    name = [x for x, i in row_number(t.rows, lambda x: x[1], True) if i == k][0][0]
    return sql_item([t], f"SELECT n FROM (SELECT n, ROW_NUMBER() OVER (ORDER BY s DESC) AS rn FROM t) WHERE rn = {k};", name, "The name at row number k when sorted from the biggest s.")


def w_rank_tie(rng):
    t = _scores(rng, "mid")
    name = _pick(rng, t)[0]
    r = {x[0]: rk for x, rk, d in rank_dense(t.rows, lambda x: x[1])}[name]
    return sql_item([t], f"SELECT r FROM (SELECT n, RANK() OVER (ORDER BY s) AS r FROM t) WHERE n = '{name}';", r, "Rows with the same s share a rank, and the next rank skips the places the tie used.")


def w_dense_tie(rng):
    t = _scores(rng, "mid")
    name = _pick(rng, t)[0]
    r = {x[0]: d for x, rk, d in rank_dense(t.rows, lambda x: x[1])}[name]
    return sql_item([t], f"SELECT r FROM (SELECT n, DENSE_RANK() OVER (ORDER BY s) AS r FROM t) WHERE n = '{name}';", r, "DENSE_RANK shares the rank for a tie and does not skip any after it.")


def w_rank_desc_tie(rng):
    t = _scores(rng, "top")
    name = _pick(rng, t)[0]
    r = {x[0]: rk for x, rk, d in rank_dense(t.rows, lambda x: x[1], True)}[name]
    return sql_item([t], f"SELECT r FROM (SELECT n, RANK() OVER (ORDER BY s DESC) AS r FROM t) WHERE n = '{name}';", r, "Two rows tie for 1; the next one is rank 3.")


def w_dense_desc_tie(rng):
    t = _scores(rng, "top")
    name = _pick(rng, t)[0]
    r = {x[0]: d for x, rk, d in rank_dense(t.rows, lambda x: x[1], True)}[name]
    return sql_item([t], f"SELECT r FROM (SELECT n, DENSE_RANK() OVER (ORDER BY s DESC) AS r FROM t) WHERE n = '{name}';", r, "Two rows tie for 1; DENSE_RANK goes on with 2 right after.")


def w_count_first(rng):
    t = _scores(rng, "top")
    n = sum(1 for x, rk, d in rank_dense(t.rows, lambda x: x[1], True) if rk == 1)
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT RANK() OVER (ORDER BY s DESC) AS r FROM t) WHERE r = 1;", n, "A tie for first puts both rows at rank 1.")


def w_max_dense(rng):
    t = _scores(rng, "mid")
    return sql_item([t], "SELECT MAX(r) FROM (SELECT DENSE_RANK() OVER (ORDER BY s) AS r FROM t);", len({x[1] for x in t.rows}), "DENSE_RANK counts the different values.")


def w_max_rank(rng):
    t = _scores(rng, "mid")
    top = max(rk for x, rk, d in rank_dense(t.rows, lambda x: x[1]))
    return sql_item([t], "SELECT MAX(r) FROM (SELECT RANK() OVER (ORDER BY s) AS r FROM t);", top, "RANK skips after the tie, so its biggest value is the row count when the tie is not last.")


def _series(rng: random.Random, n: int = 5, ties: bool = False) -> Tbl:
    """t(id INT, s INT): ids 1..n in order, small s (with ties for the peers questions)."""
    vals = [rng.randint(1, 9) for _ in range(n)]
    if ties:
        vals = rng.sample(range(1, 10), n - 1)
        vals.insert(rng.randint(1, n - 2), vals[rng.randrange(n - 1)])
    return Tbl("t", [("id", "INT"), ("s", "INT")], [(i + 1, v) for i, v in enumerate(vals)])


def w_running(rng):
    t = _series(rng)
    k = rng.randint(2, 5)
    s = sum(r[1] for r in t.rows if r[0] <= k)
    return sql_item([t], f"SELECT v FROM (SELECT id, SUM(s) OVER (ORDER BY id) AS v FROM t) WHERE id = {k};", s, "A running total: the sum of s from the first row up to this one.")


def w_running_peers(rng):
    t = _series(rng, ties=True)
    k = rng.randint(1, 5)
    row = t.rows[k - 1]
    got = [v for r, v in running_sum(t.rows, lambda r: r[1], lambda r: r[1]) if r == row][0]
    return sql_item([t], f"SELECT v FROM (SELECT id, SUM(s) OVER (ORDER BY s) AS v FROM t) WHERE id = {k};", got, "The default frame includes every row with the same s as this one, so tied rows get the same total.")


def w_running_count(rng):
    t = _series(rng, ties=True)
    k = rng.randint(1, 5)
    row = t.rows[k - 1]
    got = [v for r, v in running_sum(t.rows, lambda r: r[1], lambda r: 1) if r == row][0]
    return sql_item([t], f"SELECT v FROM (SELECT id, COUNT(*) OVER (ORDER BY s) AS v FROM t) WHERE id = {k};", got, "The running count also includes the rows tied with this one.")


def w_total(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    return sql_item([t], f"SELECT v FROM (SELECT id, SUM(s) OVER () AS v FROM t) WHERE id = {k};", sum(r[1] for r in t.rows), "With an empty OVER () every row sees the whole table: the same total on each row.")


def w_count_over(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    return sql_item([t], f"SELECT v FROM (SELECT id, COUNT(*) OVER () AS v FROM t) WHERE id = {k};", len(t.rows), "Every row sees all the rows.")


def w_max_over(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    return sql_item([t], f"SELECT v FROM (SELECT id, MAX(s) OVER () AS v FROM t) WHERE id = {k};", max(r[1] for r in t.rows), "The biggest s, shown on every row.")


def w_share(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    tot = sum(r[1] for r in t.rows)
    return sql_item([t], f"SELECT v FROM (SELECT id, s * 100 / SUM(s) OVER () AS v FROM t) WHERE id = {k};", tdiv(t.rows[k - 1][1] * 100, tot), "The row's s times 100 over the total, as an integer division.")


def w_lag(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    got = t.rows[k - 2][1] if k > 1 else NULL
    return sql_item([t], f"SELECT v FROM (SELECT id, LAG(s) OVER (ORDER BY id) AS v FROM t) WHERE id = {k};", got, "LAG looks at the row before: the first row has none, so NULL.")


def w_lag_default(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    d = rng.randint(0, 3)
    got = t.rows[k - 2][1] if k > 1 else d
    return sql_item([t], f"SELECT v FROM (SELECT id, LAG(s, 1, {d}) OVER (ORDER BY id) AS v FROM t) WHERE id = {k};", got, "LAG(s, 1, d) gives d where there is no row before.")


def w_lag2(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    got = t.rows[k - 3][1] if k > 2 else NULL
    return sql_item([t], f"SELECT v FROM (SELECT id, LAG(s, 2) OVER (ORDER BY id) AS v FROM t) WHERE id = {k};", got, "LAG(s, 2) looks two rows back; the first two rows have nothing there.")


def w_lead(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    got = t.rows[k][1] if k < 5 else NULL
    return sql_item([t], f"SELECT v FROM (SELECT id, LEAD(s) OVER (ORDER BY id) AS v FROM t) WHERE id = {k};", got, "LEAD looks at the next row: the last row has none, so NULL.")


def w_lead_default(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    d = rng.randint(0, 3)
    got = t.rows[k][1] if k < 5 else d
    return sql_item([t], f"SELECT v FROM (SELECT id, LEAD(s, 1, {d}) OVER (ORDER BY id) AS v FROM t) WHERE id = {k};", got, "LEAD(s, 1, d) gives d on the last row.")


def w_lead2(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    got = t.rows[k + 1][1] if k < 4 else NULL
    return sql_item([t], f"SELECT v FROM (SELECT id, LEAD(s, 2) OVER (ORDER BY id) AS v FROM t) WHERE id = {k};", got, "LEAD(s, 2) looks two rows ahead.")


def w_diff(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    got = t.rows[k - 1][1] - t.rows[k - 2][1] if k > 1 else NULL
    return sql_item([t], f"SELECT v FROM (SELECT id, s - LAG(s) OVER (ORDER BY id) AS v FROM t) WHERE id = {k};", got, "The change since the previous row; the first row has no previous one, so NULL.")


def w_first_value(rng):
    t = _scores(rng)
    name = _pick(rng, t)[0]
    top = max(t.rows, key=lambda r: r[1])[0]
    return sql_item([t], f"SELECT v FROM (SELECT n, FIRST_VALUE(n) OVER (ORDER BY s DESC) AS v FROM t) WHERE n = '{name}';", top, "FIRST_VALUE is the name at the top of the window: the same on every row.")


def w_last_value(rng):
    t = _scores(rng)
    name = _pick(rng, t)[0]
    return sql_item([t], f"SELECT v FROM (SELECT n, LAST_VALUE(n) OVER (ORDER BY s) AS v FROM t) WHERE n = '{name}';", name, "The default frame stops at the current row, so LAST_VALUE is the row's own name.")


def _grouped(rng: random.Random) -> Tbl:
    ns = list("abcd")
    vals = ints(rng, 4, 1, 9)
    gs = ["x", "x", "y", "y"]
    rng.shuffle(gs)
    return Tbl("t", [("n", "TEXT"), ("g", "TEXT"), ("s", "INT")], list(zip(ns, gs, vals)))


def w_part_rn(rng):
    t = _grouped(rng)
    name, g, s = rng.choice(t.rows)
    same = sorted((r for r in t.rows if r[1] == g), key=lambda r: -r[2])
    rn = [i + 1 for i, r in enumerate(same) if r[0] == name][0]
    return sql_item([t], f"SELECT v FROM (SELECT n, ROW_NUMBER() OVER (PARTITION BY g ORDER BY s DESC) v FROM t) WHERE n = '{name}';", rn, "The numbering starts again in each group.")


def w_part_sum(rng):
    t = _grouped(rng)
    name, g, s = rng.choice(t.rows)
    return sql_item([t], f"SELECT v FROM (SELECT n, SUM(s) OVER (PARTITION BY g) AS v FROM t) WHERE n = '{name}';", sum(r[2] for r in t.rows if r[1] == g), "Each row shows the total of its own group.")


def w_part_max(rng):
    t = _grouped(rng)
    name, g, s = rng.choice(t.rows)
    return sql_item([t], f"SELECT v FROM (SELECT n, MAX(s) OVER (PARTITION BY g) AS v FROM t) WHERE n = '{name}';", max(r[2] for r in t.rows if r[1] == g), "The biggest s in the row's own group.")


def w_part_count(rng):
    t = _grouped(rng)
    name, g, s = rng.choice(t.rows)
    return sql_item([t], f"SELECT v FROM (SELECT n, COUNT(*) OVER (PARTITION BY g) v FROM t) WHERE n = '{name}';", sum(1 for r in t.rows if r[1] == g), "How many rows share the row's group.")


def w_part_rank(rng):
    t = _grouped(rng)
    name, g, s = rng.choice(t.rows)
    same = sorted(r[2] for r in t.rows if r[1] == g)
    rank = 1 + sum(1 for v in same if v > s)
    return sql_item([t], f"SELECT v FROM (SELECT n, RANK() OVER (PARTITION BY g ORDER BY s DESC) v FROM t) WHERE n = '{name}';", rank, "The rank counts only the rows of the same group.")


def w_part_running(rng):
    t = _grouped(rng)
    name, g, s = rng.choice(t.rows)
    same = sorted((r for r in t.rows if r[1] == g), key=lambda r: r[2])
    total = 0
    for r in same:
        total += r[2]
        if r[0] == name:
            break
    return sql_item([t], f"SELECT v FROM (SELECT n, SUM(s) OVER (PARTITION BY g ORDER BY s) v FROM t) WHERE n = '{name}';", total, "A running total that restarts for each group.")


def w_avg_over(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    return sql_item([t], f"SELECT v FROM (SELECT id, AVG(s) OVER () AS v FROM t) WHERE id = {k};", avg_([r[1] for r in t.rows]), "The average of all rows, a real number, on every row.")


def w_above_avg_rows(rng):
    t = _series(rng)
    avg = avg_([r[1] for r in t.rows])
    return sql_item([t], "SELECT COUNT(*) FROM (SELECT s, AVG(s) OVER () AS a FROM t) WHERE s > a;", sum(1 for r in t.rows if r[1] > avg), "Each row carries the overall average; the rows above it are counted.")


def w_min_over(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    return sql_item([t], f"SELECT v FROM (SELECT id, s - MIN(s) OVER () AS v FROM t) WHERE id = {k};", t.rows[k - 1][1] - min(r[1] for r in t.rows), "How far this row's s is above the smallest.")


def w_row_in_part_top(rng):
    t = _grouped(rng)
    g = rng.choice("xy")
    rows = [r for r in t.rows if r[1] == g]
    if not rows:
        raise Retry
    top = max(rows, key=lambda r: r[2])[0]
    return sql_item([t], f"SELECT n FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY g ORDER BY s DESC) r FROM t) WHERE g = '{g}' AND r = 1;", top, "The first row of each group when sorted from the biggest s: the group's top name.")


def w_lag_diff_sum(rng):
    t = _series(rng)
    s = sum(t.rows[i][1] - t.rows[i - 1][1] for i in range(1, 5))
    return sql_item([t], "SELECT SUM(d) FROM (SELECT s - LAG(s) OVER (ORDER BY id) AS d FROM t);", s, "The first row's difference is NULL and SUM skips it; the others add up to last minus first.")


def w_running_last(rng):
    t = _series(rng)
    return sql_item([t], "SELECT MAX(v) FROM (SELECT SUM(s) OVER (ORDER BY id) AS v FROM t);", sum(r[1] for r in t.rows), "A running total ends at the grand total.")


def w_rank_three(rng):
    t = _scores(rng, "top")
    name = [x for x, rk, d in rank_dense(t.rows, lambda x: x[1], True) if rk == 3][0][0]
    return sql_item([t], "SELECT n FROM (SELECT n, RANK() OVER (ORDER BY s DESC) AS r FROM t) WHERE r = 3;", name, "Ranks 1, 1, 3: after the tie for first, the next row is rank 3.")


def w_dense_two(rng):
    t = _scores(rng, "top")
    name = [x for x, rk, d in rank_dense(t.rows, lambda x: x[1], True) if d == 2][0][0]
    return sql_item([t], "SELECT n FROM (SELECT n, DENSE_RANK() OVER (ORDER BY s DESC) AS r FROM t) WHERE r = 2;", name, "DENSE_RANK gives 1, 1, 2, 3, 4: only one row has rank 2.")


def w_rows_two(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    s = sum(r[1] for r in t.rows[max(0, k - 2):k])
    return sql_item([t], f"SELECT v FROM (SELECT id, SUM(s) OVER (ORDER BY id ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS v FROM t) WHERE id = {k};", s, "The frame is this row and the one before it: the first row has only itself.")


def w_rows_three(rng):
    t = _series(rng)
    k = rng.randint(1, 5)
    s = sum(r[1] for r in t.rows[max(0, k - 3):k])
    return sql_item([t], f"SELECT v FROM (SELECT id, SUM(s) OVER (ORDER BY id ROWS 2 PRECEDING) AS v FROM t) WHERE id = {k};", s, "ROWS 2 PRECEDING is this row and the two before it (fewer at the start).")


def w_last_full(rng):
    t = _scores(rng, letters=True, n=4)
    top = max(t.rows, key=lambda r: r[1])[0]
    return sql_item([t], "SELECT LAST_VALUE(n) OVER (ORDER BY s ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) FROM t LIMIT 1;", top, "With the frame stretched over all rows, LAST_VALUE is the name with the biggest s, on every row.")


WINDOWS: list[Maker] = [fit(f) for f in (w_rank_three, w_dense_two, w_rows_two, w_rows_three, w_last_full,
    w_row_number, w_row_number_desc, w_nth_name, w_rank_tie, w_dense_tie, w_rank_desc_tie, w_dense_desc_tie, w_count_first,
    w_max_dense, w_max_rank, w_running, w_running_peers, w_running_count, w_total, w_count_over, w_max_over, w_share, w_lag,
    w_lag_default, w_lag2, w_lead, w_lead_default, w_lead2, w_diff, w_first_value, w_last_value, w_part_rn, w_part_sum,
    w_part_max, w_part_count, w_part_rank, w_part_running, w_avg_over, w_above_avg_rows, w_min_over, w_row_in_part_top,
    w_lag_diff_sum, w_running_last)]
