"""Dart data pack, part 4: Number Parse - turning text into numbers and the arithmetic Dart does with them.

`int.parse`, `int.tryParse` (null when the text is not a number), radix, `double.parse`, `%` that is never negative,
`~/`, `remainder`, `clamp`, `round`/`floor`/`ceil`/`truncate` on negative numbers, 64-bit overflow, NaN and infinity,
`toStringAsFixed`/`Precision`/`Exponential`. Only values whose text is exact are used (halves, quarters, eighths and
digits far from a rounding tie), so every answer has exactly one right form.
"""

from __future__ import annotations

import math
import random

from ._dart_model import dceil, ddiv, dfloor, dmod, dround, dstr, fixed, tdiv_
from ._dartdata_model import INT_MAX, INT_MIN, R, dfmod, to_exponential, to_precision, to_radix, trunc, wrap64
from ._model import Maker, tmod

PARSE_NULL = "tryParse gives null for text that is not a whole number, instead of throwing like parse."
ROUND_AWAY = "round() sends a half away from zero: 2.5 becomes 3 and -2.5 becomes -3."


def _half(r: random.Random, neg: bool | None = None) -> float:
    """A float with a .25, .5 or .75 part: exactly representable."""
    x = r.randint(1, 9) + r.choice((0.25, 0.5, 0.5, 0.75))
    if neg is None:
        neg = r.random() < 0.5
    return -x if neg else x


def _neg(x: float) -> str:
    """Dart source for a possibly negative double used as a receiver: (-2.5)."""
    return f"({dstr(x)})" if x < 0 else dstr(x)


def n_round(r):
    x = _half(r)
    return f"print({_neg(x)}.round());", dround(x), ROUND_AWAY


def n_round_neg(r):
    x = _half(r, True)
    return f"print({_neg(x)}.round());", dround(x), ROUND_AWAY


def n_floor(r):
    x = _half(r)
    return f"print({_neg(x)}.floor());", dfloor(x), "floor goes toward minus infinity: -2.5 becomes -3."


def n_ceil(r):
    x = _half(r)
    return f"print({_neg(x)}.ceil());", dceil(x), "ceil goes toward plus infinity: -2.5 becomes -2."


def n_truncate(r):
    x = _half(r)
    return f"print({_neg(x)}.truncate());", trunc(x), "truncate throws the decimals away, which is toward zero."


def n_toint(r):
    x = _half(r)
    return f"print({_neg(x)}.toInt());", trunc(x), "toInt cuts toward zero, it does not round."


def n_prec_floor(r):
    x = _half(r, False)
    return f"print(-{dstr(x)}.floor());", -dfloor(x), "The minus applies AFTER the call: -(2.5.floor()) is -2, not the floor of -2.5."


def n_paren_floor(r):
    x = _half(r, False)
    return f"print((-{dstr(x)}).floor());", dfloor(-x), "With the brackets the number is negative first: the floor of -2.5 is -3."


def n_div_round(r):
    n, h = r.randint(10, 40), r.choice((2, 4, 5, 8))
    return f"print(({n} / {h}).round());", dround(n / h), "Divide first, then round the quotient (a half goes up)."


def n_div_floor(r):
    n, a = r.randint(10, 40), r.randint(2, 9)
    return f"print(({n} / {a}).floor());", n // a, "For positive numbers floor of / is the same as ~/."


def n_div_ceil(r):
    n, a = r.randint(10, 40), r.randint(2, 9)
    return f"print(({n} / {a}).ceil());", -(-n // a), "ceil rounds the quotient up to the next whole number."


def n_tdiv_neg(r):
    n, a = r.randint(10, 40), r.randint(2, 9)
    return f"print((-{n}) ~/ {a});", tdiv_(-n, a), "~/ cuts toward zero, so -7 ~/ 2 is -3, not -4."


def n_mod_neg(r):
    n, a = r.randint(10, 40), r.randint(2, 9)
    return f"print((-{n}) % {a});", dmod(-n, a), "Dart's % is never negative: -7 % 3 is 2."


def n_mod_negdiv(r):
    n, a = r.randint(10, 40), r.randint(2, 9)
    return f"print({n} % -{a});", dmod(n, -a), "The result of % is never negative, even when the divisor is."


def n_remainder(r):
    n, a = r.randint(10, 40), r.randint(2, 9)
    return f"print((-{n}).remainder({a}));", tmod(-n, a), "remainder keeps the sign of the dividend, unlike %: -7.remainder(3) is -1."


def n_mod_vs_rem(r):
    n, a = r.randint(10, 40), r.randint(2, 9)
    return (f"print((-{n}) % {a} == (-{n}).remainder({a}));", dmod(-n, a) == tmod(-n, a),
            "% and remainder differ for a negative dividend unless it divides exactly.")


def n_mod_double(r):
    x, a = _half(r, True), r.randint(2, 4)
    return f"print({_neg(x)} % {a});", dfmod(x, a), "A double % is never negative either."


def n_clamp(r):
    lo, hi = sorted(r.sample(range(1, 30), 2))
    x = r.randint(-5, 40)
    return f"print({x if x >= 0 else f'({x})'}.clamp({lo}, {hi}));", min(max(x, lo), hi), "clamp(lo, hi) squeezes the number into the range."


def n_clamp_neg(r):
    hi = r.randint(5, 20)
    return f"print((-{r.randint(1, 9)}).clamp(0, {hi}));", 0, "A number below the range is raised to the lower end."


def n_abs(r):
    a, n = r.randint(2, 9), r.randint(10, 40)
    return f"print(({a} - {n}).abs());", n - a, "The difference is negative; abs drops the sign."


def n_sign(r):
    a = r.randint(2, 9)
    return f"print((-{a}).sign);", -1, "sign is -1, 0 or 1."


def n_is_neg_zero(r):
    return "print((-0.0).isNegative);", True, "A double has a negative zero, and isNegative notices it."


def n_neg_zero(r):
    return "print(-0.0 == 0.0);", True, "Negative zero and zero compare equal."


def n_neg_zero_print(r):
    a = r.randint(2, 9)
    return f"print((-{a}) / double.infinity);", "-0.0", "A negative number over infinity is negative zero, which prints with its sign."


def n_inf(r):
    return "print(1 / 0);", "Infinity", "Dividing by zero with / gives infinity, not an error."


def n_neg_inf(r):
    a = r.randint(2, 9)
    return f"print(-{a} / 0);", "-Infinity", "A negative number over zero is minus infinity."


def n_nan(r):
    return "print(0 / 0);", "NaN", "Zero over zero is not a number."


def n_nan_isnan(r):
    return "print((0 / 0).isNaN);", True, "isNaN is the way to ask: NaN is not equal to anything."


def n_nan_eq(r):
    return "print(double.nan == double.nan);", False, "NaN is not even equal to itself."


def n_inf_minus(r):
    return "print(double.infinity - double.infinity);", "NaN", "Infinity minus infinity has no value."


def n_inf_plus(r):
    a = r.randint(2, 9)
    return f"print(double.infinity + {a});", "Infinity", "Adding a number to infinity changes nothing."


def n_inf_isinf(r):
    return "print((1 / 0).isInfinite);", True, "Dividing by zero gave infinity."


def n_inf_cmp(r):
    return "print(double.infinity > 1e300);", True, "Infinity is bigger than any finite number."


def n_max_finite(r):
    return "print(double.maxFinite * 2);", "Infinity", "Too big for a double: it overflows to infinity."


def n_mod_zero_double(r):
    a = r.randint(2, 9)
    return f"print({a}.0 % 0);", "NaN", "A double remainder with zero is NaN, while an int one would throw."


def n_third(r):
    return "print(1 / 3 * 3 == 1);", True, "1 / 3 is a rounded double, but multiplying it by 3 rounds back to exactly 1."


def n_overflow_up(r):
    k = r.randint(1, 3)
    return f"print(9223372036854775807 + {k});", wrap64(INT_MAX + k), "A Dart int has 64 bits: above the biggest value it wraps round to the smallest."


def n_overflow_down(r):
    return "print(-9223372036854775808 - 1);", wrap64(INT_MIN - 1), "Below the smallest int it wraps to the biggest."


def n_shift63(r):
    return "print(1 << 63);", wrap64(1 << 63), "The 64th bit is the sign bit, so this is the smallest int."


def n_shift62(r):
    return "print(1 << 62);", 1 << 62, "2 to the power 62 still fits."


def n_shift64(r):
    return "print(1 << 64);", 0, "The bit is shifted out of all 64 places: nothing is left."


def n_mul_wrap(r):
    k = r.randint(2, 4)
    return f"print((1 << 62) * {k});", wrap64((1 << 62) * k), "The product is too big for 64 bits and wraps."


def n_parse_big(r):
    return "print(int.tryParse('9223372036854775808'));", None, "One more than the biggest int does not fit, so tryParse gives null."


def n_runtime_div(r):
    a = r.randint(2, 9)
    return f"print(({a} / 1).runtimeType);", "double", "/ always makes a double, even for ints that divide exactly."


def n_runtime_tdiv(r):
    a = r.randint(2, 9)
    return f"print(({a} ~/ 1).runtimeType);", "int", "~/ always makes an int."


def n_runtime_mul(r):
    a = r.randint(2, 9)
    return f"print(({a} * 1.0).runtimeType);", "double", "An int times a double is a double."


def n_runtime_add(r):
    a, b = r.sample(range(2, 10), 2)
    return f"print(({a} + {b}).runtimeType);", "int", "Two ints add up to an int."


def n_runtime_parse(r):
    a = r.randint(2, 9)
    return f"print(num.parse('{a}').runtimeType);", "int", "num.parse gives an int when the text has no decimal point."


def n_runtime_parse2(r):
    a = r.randint(2, 9)
    return f"print(num.parse('{a}.0').runtimeType);", "double", "A decimal point makes it a double, even .0."


def n_num_parse(r):
    a = r.randint(2, 9)
    return f"print(num.parse('{a}.0'));", f"{a}.0", "The result is a double, which prints with .0."


def n_eq_int_double(r):
    a = r.randint(2, 9)
    return f"print({a}.0 == {a});", True, "== compares numbers by value, so 3.0 equals 3."


def n_eq_str(r):
    a = r.randint(2, 9)
    return f"print({a}.0.toString() == '{a}');", False, "3.0 prints as '3.0', not '3'."


def n_float_sum(r):
    return "print(0.1 + 0.2 == 0.3);", False, "Both 0.1 and 0.2 are slightly off in binary, and their sum is slightly more than 0.3."


def n_float_exact(r):
    return "print(0.5 + 0.25 == 0.75);", True, "Halves and quarters are exact in binary."


def n_float_mul(r):
    a = r.choice((3, 6, 7))
    return f"print({a} * 0.1);", a * 0.1, "0.1 is not exact in binary, so the product shows a long tail."


def n_float_fixed(r):
    return "print((0.1 + 0.2).toStringAsFixed(2));", "0.30", "toStringAsFixed(2) rounds to two decimals and always shows them."


def n_div_exact(r):
    n, h = r.randint(10, 40), r.choice((2, 4, 5, 8))
    return f"print({n} / {h});", ddiv(n, h), "/ always gives a double."


def n_div_times(r):
    n, h = r.randint(10, 40), r.choice((2, 4, 5, 8))
    return f"print({n} / {h} * {h});", f"{n}.0", "The quotient is exact here, so multiplying back gives the double n.0."


def n_mixed_add(r):
    a, n = r.randint(2, 9), r.randint(10, 40)
    return f"print({a} + {n} / 2);", a + n / 2, "/ happens before +; the quotient is a double, so the sum is too."


def n_tdiv_times(r):
    n, a = r.randint(10, 40), r.randint(2, 9)
    return f"print({n} ~/ {a} * {a});", (n // a) * a, "The multiple of a at or below n: ~/ and * go left to right."


def n_parse_add(r):
    a, b, c = r.sample(range(2, 10), 3)
    return f"print(int.parse('{a}{b}') + {c});", int(f"{a}{b}") + c, "The text '37' becomes the number 37 first, then c is added."


def n_str_concat(r):
    a, b = r.sample(range(2, 10), 2)
    return f"print('{a}' + '{b}');", f"{a}{b}", "+ on two strings joins them: the numbers are not added."


def n_parse_sum(r):
    a, b = r.sample(range(2, 10), 2)
    return f"print(int.parse('{a}') + int.parse('{b}'));", a + b, "Both strings become numbers, so + adds them."


def n_parse_lead(r):
    a = r.randint(2, 9)
    return f"print(int.parse('00{a}') + 1);", a + 1, "Leading zeros are fine: '007' is 7."


def n_parse_neg(r):
    a, b = r.sample(range(2, 10), 2)
    return f"print(int.parse('-{a}') + {b});", b - a, "A leading minus sign is part of the number."


def n_try_ok(r):
    a = r.randint(10, 40)
    return f"print(int.tryParse('{a}'));", a, "The text is a whole number, so tryParse gives it."


def n_try_word(r):
    w = r.choice(("farm", "drone", "carrot", "loop", "seed", "corn"))
    return f"print(int.tryParse('{w}'));", None, PARSE_NULL


def n_try_dec(r):
    a = r.randint(2, 9)
    return f"print(int.tryParse('{a}.5'));", None, "int.tryParse refuses a decimal point."


def n_try_junk(r):
    a = r.randint(10, 40)
    return f"print(int.tryParse('{a}px'));", None, "Extra characters make the whole text invalid."


def n_try_default(r):
    a = r.randint(10, 40)
    return f"print(int.tryParse('{a}x') ?? -1);", -1, "tryParse gave null, so ?? takes the fallback."


def n_try_default_ok(r):
    a = r.randint(10, 40)
    return f"print(int.tryParse('{a}') ?? -1);", a, "The text parses, so the fallback is not used."


def n_try_null_cmp(r):
    w = r.choice(("farm", "drone", "carrot", "loop"))
    return f"print(int.tryParse('{w}') == null);", True, "Not a number, so the result is null."


def n_try_plus(r):
    a = r.randint(2, 9)
    return f"print(int.tryParse('+{a}'));", a, "A leading + is allowed."


def n_try_double(r):
    w = r.choice(("farm", "drone", "carrot", "loop"))
    return f"print(double.tryParse('{w}'));", None, "double.tryParse also gives null for text that is not a number."


def n_hex_parse(r):
    n = r.randint(30, 255)
    return f"print(int.parse('{to_radix(n, 16)}', radix: 16));", n, "radix 16 reads the text as hexadecimal."


def n_bin_parse(r):
    n = r.randint(5, 31)
    return f"print(int.parse('{to_radix(n, 2)}', radix: 2));", n, "radix 2 reads the text as binary."


def n_oct_parse(r):
    digits = "".join(r.choice("1234567") for _ in range(r.randint(2, 3)))
    return f"print(int.parse('{digits}', radix: 8));", int(digits, 8), "radix 8 reads the text as octal."


def n_radix_bad(r):
    return "print(int.tryParse('12', radix: 2));", None, "2 is not a binary digit, so the text is invalid in radix 2."


def n_hex_prefix(r):
    n = r.randint(30, 255)
    return f"print(int.parse('0x{to_radix(n, 16)}'));", n, "The 0x prefix makes parse read hexadecimal even without a radix."


def n_to_radix2(r):
    n = r.randint(10, 40)
    return f"print({n}.toRadixString(2));", to_radix(n, 2), "toRadixString(2) writes the number in binary."


def n_to_radix16(r):
    n = r.randint(30, 255)
    return f"print({n}.toRadixString(16));", to_radix(n, 16), "Hexadecimal digits above 9 are lower-case letters."


def n_dbl_parse(r):
    a, b = r.sample(range(2, 10), 2)
    return f"print(double.parse('{a}.{b}'));", float(f"{a}.{b}"), "double.parse reads the decimals."


def n_dbl_parse_int(r):
    a = r.randint(2, 9)
    return f"print(double.parse('{a}') + 1);", a + 1.0, "A double even when the text has no decimal point."


def n_dbl_exp(r):
    k = r.randint(1, 3)
    return f"print(double.parse('1e{k}'));", float(10 ** k), "1e2 means 1 times 10 to the power 2."


def n_fixed_int(r):
    a = r.randint(2, 9)
    return f"print({a}.toStringAsFixed(2));", fixed(a, 2), "toStringAsFixed always shows that many decimals."


def n_fixed_div(r):
    n, h = r.randint(10, 40), r.choice((2, 4, 5, 8))
    return f"print(({n} / {h}).toStringAsFixed(1));", fixed(n / h, 1), "The quotient rounded to one decimal; an exact half rounds up."


def n_fixed_digits(r):
    a, b, c, d = r.randint(1, 9), r.randint(0, 9), r.choice((1, 2, 3, 4, 6, 7, 8, 9)), r.randint(0, 9)
    x = float(f"{a}.{b}{c}{d}")
    return f"print({dstr(x)}.toStringAsFixed(2));", fixed(x, 2), "Two decimals: the third decimal decides whether the second goes up."


def n_fixed_zero(r):
    n, h = r.randint(10, 40), r.choice((2, 4, 5, 8))
    return f"print(({n} / {h}).toStringAsFixed(0));", fixed(n / h, 0), "toStringAsFixed(0) rounds to a whole number and shows no point."


def n_precision(r):
    a, b, c, d = r.randint(1, 9), r.randint(0, 9), r.randint(0, 9), r.choice((1, 2, 3, 4, 6, 7, 8, 9))
    x = float(f"{a}.{b}{c}{d}")
    return f"print({dstr(x)}.toStringAsPrecision(3));", to_precision(x, 3), "Precision counts all the digits: three digits in total."


def n_exponential(r):
    d = [r.randint(1, 9)] + [r.randint(0, 9) for _ in range(2)] + [r.choice((1, 2, 3, 4, 6, 7, 8, 9))] + [r.randint(0, 9)]
    n = int("".join(map(str, d)))
    return f"print({n}.toStringAsExponential(2));", to_exponential(n, 2), "One digit, a point, two decimals, then e and the power of ten."


def n_exponential_small(r):
    a, b = r.randint(1, 9), r.choice((1, 2, 3, 4, 6, 7, 8, 9))
    x = float(f"0.00{a}{b}")
    return f"print({dstr(x)}.toStringAsExponential(1));", to_exponential(x, 1), "0.0012 is 1.2 times ten to the power minus 3."


def n_pow(r):
    a, b = r.randint(2, 6), r.randint(2, 6)
    return f"import 'dart:math';\nvoid main() => print(pow({a}, {b}));", a ** b, "pow of two ints with a positive power is an int."


def n_pow_neg(r):
    k = r.randint(1, 3)
    return f"import 'dart:math';\nvoid main() => print(pow(2, -{k}));", 1 / 2 ** k, "A negative power gives a double: 1 over the power."


def n_sqrt(r):
    a = r.randint(2, 12)
    return f"import 'dart:math';\nvoid main() => print(sqrt({a * a}));", float(a), "sqrt always gives a double: 7.0, not 7."


def n_min_max(r):
    a, b, c, d = r.sample(range(2, 10), 4)
    return f"import 'dart:math';\nvoid main() => print(min({a}, {b}) * max({c}, {d}));", min(a, b) * max(c, d), "The smaller of a and b times the bigger of c and d."


def n_and(r):
    a, b = r.randint(5, 30), r.randint(5, 30)
    return f"print({a} & {b});", a & b, "& keeps the bits that are set in both."


def n_or(r):
    a, b = r.randint(5, 30), r.randint(5, 30)
    return f"print({a} | {b});", a | b, "| keeps the bits that are set in either."


def n_xor(r):
    a, b = r.randint(5, 30), r.randint(5, 30)
    return f"print({a} ^ {b});", a ^ b, "^ keeps the bits that differ."


def n_shl(r):
    a, k = r.randint(2, 9), r.randint(1, 4)
    return f"print({a} << {k});", a << k, "Shifting left by k multiplies by 2 to the power k."


def n_shr(r):
    a, k = r.randint(20, 200), r.randint(1, 4)
    return f"print({a} >> {k});", a >> k, "Shifting right by k divides by 2 to the power k and drops the remainder."


def n_not(r):
    a = r.randint(2, 30)
    return f"print(~{a});", ~a, "~ flips every bit: ~n is always -n - 1."


def n_shr_neg(r):
    a = r.choice((7, 9, 11, 13, 15))
    return f"print((-{a}) >> 1);", (-a) >> 1, "Shifting right keeps the sign and rounds toward minus infinity: -7 >> 1 is -4."


def n_ushr(r):
    return "print(-1 >>> 60);", 15, "The triple shift fills with zeros, so only the top 4 of the 64 ones remain."


def n_bitlen(r):
    n = r.randint(20, 1000)
    return f"print({n}.bitLength);", n.bit_length(), "bitLength is how many binary digits the number needs."


def n_gcd(r):
    g, a, b = r.randint(2, 6), r.randint(2, 6), r.randint(2, 6)
    while math.gcd(a, b) != 1:
        a, b = r.randint(2, 6), r.randint(2, 6)
    return f"print({g * a}.gcd({g * b}));", g, "gcd is the greatest common divisor."


def n_even(r):
    n = r.randint(10, 40)
    return f"print({n}.isEven);", n % 2 == 0, "isEven is true when the number divides by 2."


def n_len_digits(r):
    n = r.randint(100, 99999)
    return f"print({n}.toString().length);", len(str(n)), "The number as text has one character per digit."


def n_pad(r):
    n = r.randint(2, 99)
    return f"print({n}.toString().padLeft(4, '0'));", str(n).rjust(4, "0"), "padLeft fills with zeros on the left up to 4 characters."


def n_digit_sum(r):
    n = r.randint(100, 999)
    return f"print({n}.toString().split('').map(int.parse).reduce((a, b) => a + b));", sum(map(int, str(n))), "Split into digit characters, turn each into a number, add them."


NUMS: list[Maker] = [R(f) for f in (
    n_round, n_round_neg, n_floor, n_ceil, n_truncate, n_toint, n_prec_floor, n_paren_floor,
    n_div_round, n_div_floor, n_div_ceil, n_tdiv_neg, n_mod_neg, n_mod_negdiv, n_remainder, n_mod_vs_rem,
    n_mod_double, n_clamp, n_clamp_neg, n_abs, n_sign, n_is_neg_zero, n_neg_zero, n_neg_zero_print, n_inf,
    n_neg_inf, n_nan, n_nan_isnan, n_nan_eq, n_inf_minus, n_inf_plus, n_inf_isinf, n_inf_cmp, n_max_finite,
    n_mod_zero_double, n_third, n_overflow_up, n_overflow_down, n_shift63, n_shift62, n_shift64, n_mul_wrap,
    n_parse_big, n_runtime_div, n_runtime_tdiv, n_runtime_mul, n_runtime_add, n_runtime_parse, n_runtime_parse2,
    n_num_parse, n_eq_int_double, n_eq_str, n_float_sum, n_float_exact, n_float_mul, n_float_fixed, n_div_exact,
    n_div_times, n_mixed_add, n_tdiv_times, n_parse_add, n_str_concat, n_parse_sum, n_parse_lead, n_parse_neg,
    n_try_ok, n_try_word, n_try_dec, n_try_junk, n_try_default, n_try_default_ok, n_try_null_cmp, n_try_plus,
    n_try_double, n_hex_parse, n_bin_parse, n_oct_parse, n_radix_bad, n_hex_prefix, n_to_radix2, n_to_radix16,
    n_dbl_parse, n_dbl_parse_int, n_dbl_exp, n_fixed_int, n_fixed_div, n_fixed_digits, n_fixed_zero, n_precision,
    n_exponential, n_exponential_small, n_pow, n_pow_neg, n_sqrt, n_min_max, n_and, n_or, n_xor, n_shl, n_shr,
    n_not, n_shr_neg, n_ushr, n_bitlen, n_gcd, n_even, n_len_digits, n_pad, n_digit_sum)]
