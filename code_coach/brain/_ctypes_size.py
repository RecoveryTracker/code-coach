"""C types and preprocessor pack, part 2: Type Size (`ct_sizeof`) and Convert It (`ct_convert`).

Only sizes that are the same on every machine here are asked: the fixed-width types, `char`, `int`, `float`, `double`,
`long long`, arrays and strings of those, the type an expression gets after the integer promotions and the usual
arithmetic conversions, and structs whose padding every compiler here agrees on (members no wider than 4 bytes).
Never `sizeof(long)`, `sizeof(short)` or a pointer's size (the lint bans them as well).
"""

from __future__ import annotations

from ._c_model import SIZEOF, UINT, C, wrap
from ._ccore_numbers import T
from ._ccore_text import PF
from ._ctypes_model import f32, fixed_exact
from ._model import Maker, tdiv

SZ = SIZEOF


def S(expr: str) -> str:
    return PF("%zu", expr)


# ── 1. Type Size ────────────────────────────────────────────────────────

def _plain(t: str) -> Maker:
    return C(S(f"sizeof({t})"), SZ[t], f"{t} takes {SZ[t]} byte{'s' if SZ[t] != 1 else ''}.")


def _array_of(t: str) -> Maker:
    return C(T(f"{t} a[$n];", S("sizeof a")), lambda p: SZ[t] * p["n"], f"An array takes the size of one element times the length: {SZ[t]} * n.")


def _type_struct(members: str, size: int, why: str) -> Maker:
    return C(T(f"struct P {{ {members} }};", S("sizeof(struct P)")), size, why)


def _sum_vs_struct(members: str, parts: str, size: int, total: int) -> Maker:
    return C(T(f"struct P {{ {members} }};", PF("%zu %zu", f"sizeof(struct P), {parts}")), f"{size} {total}",
             "The compiler pads a struct so every member sits at a multiple of its own size: the struct is bigger than its members added up.")


def _row_count(t: str) -> Maker:
    return C(T(f"{t} m[$a][$n];", S("sizeof m / sizeof m[0]")), lambda p: p["a"], "One row is sizeof m[0]: the whole over one row is the number of rows.")


SIZES: list[Maker] = [
    _plain("char"), _plain("int8_t"), _plain("uint8_t"), _plain("int16_t"), _plain("uint16_t"), _plain("int32_t"),
    _plain("uint32_t"), _plain("int64_t"), _plain("uint64_t"), _plain("int"), _plain("float"), _plain("double"),
    C(S("sizeof(char)"), 1, "sizeof counts in chars, so a char is 1 by definition."),
    C(S("sizeof(uint16_t) * 8"), 16, "2 bytes of 8 bits each."),
    C(S("sizeof(uint32_t) * 8"), 32, "4 bytes of 8 bits each."),
    C(S("$n * sizeof(uint32_t)"), lambda p: p["n"] * 4, "n elements of 4 bytes each."),
    C(S("$n * sizeof(int16_t)"), lambda p: p["n"] * 2, "n elements of 2 bytes each."),
    C(PF("%d", "sizeof(int8_t) == sizeof(char)"), 1, "int8_t is the 8-bit signed type, the same size as char: 1."),
    _array_of("uint8_t"), _array_of("int16_t"), _array_of("int"), _array_of("double"), _array_of("uint64_t"),
    C(T("int16_t v[] = {$a, $b, $c};", S("sizeof v / sizeof v[0]")), 3, "The size of the whole array over the size of one element is the element count."),
    C(T("uint32_t v[] = {$a, $b, $c, $d, 1};", S("sizeof v")), 20, "Five elements of 4 bytes: the compiler counts the initializer."),
    C(T("double v[] = {$a, $b, $c, $d};", S("sizeof v / sizeof v[0]")), 4, "Whole array over one element: the number of elements."),
    C(T("uint8_t v[] = {$a, $b, $c};", PF("%zu %zu", "sizeof v, sizeof v[0]")), "3 1", "Three one-byte elements: the array is 3 bytes."),
    C(T("int a[$n];", S("sizeof a[0]")), 4, "sizeof a[0] is the size of one element: an int."),
    C(T('char s[] = "$w";', S("sizeof s")), lambda p: p["L"] + 1, "The array holds the letters and the final zero byte."),
    C(T('char s[] = "$w";', PF("%zu %zu", "sizeof s, strlen(s)")), lambda p: f"{p['L'] + 1} {p['L']}", "sizeof counts the zero byte, strlen does not."),
    C(S('sizeof("$w")'), lambda p: p["L"] + 1, "A string literal is an array of its letters plus the zero byte."),
    C(T('char s[] = "$w";', S("sizeof s - strlen(s)")), 1, "The only difference between the two is the terminating zero."),
    C(T('char s[$n] = "$w";', PF("%zu %zu", "sizeof s, strlen(s)")), lambda p: f"{p['n']} {p['L']}", "The array has the size written in the brackets; the word only fills its start."),
    C(T('char s[] = "$w$z";', S("sizeof s")), lambda p: len(p["w"]) + len(p["z"]) + 1, "Two literals side by side are one string, plus the zero byte."),
    C(T("char s[] = {'a', 'b', 'c'};", S("sizeof s")), 3, "With no string literal there is no terminating zero: just the three letters."),
    C(T('char s[$m] = "$w";', S("sizeof s")), lambda p: p["m"], "The size in the brackets, not the word, decides."),
    C(T('char s[] = "ab\\0cd";', PF("%zu %zu", "sizeof s, strlen(s)")), "6 2", "sizeof counts every byte, including the embedded zero and the final one; strlen stops at the first zero."),
    C(T("int m[$a][$b];", S("sizeof m")), lambda p: 4 * p["a"] * p["b"], "a rows of b ints, 4 bytes each."),
    C(T("int m[$a][$b];", S("sizeof m[0]")), lambda p: 4 * p["b"], "m[0] is one row: b ints."),
    C(T("uint8_t g[$a][$n];", S("sizeof g")), lambda p: p["a"] * p["n"], "a rows of n one-byte elements."),
    C(T("int16_t m[$a][$b];", S("sizeof m[0] / sizeof m[0][0]")), lambda p: p["b"], "One row over one element: the number of columns."),
    _row_count("int"), _row_count("uint8_t"),
    C(S("sizeof(uint8_t[$n])"), lambda p: p["n"], "sizeof can take an array type: n one-byte elements."),
    C(S("sizeof(int[$a][$b])"), lambda p: 4 * p["a"] * p["b"], "An array type of a rows of b ints."),
    C(S("sizeof(int16_t[$n]) / sizeof(int16_t)"), lambda p: p["n"], "The array type over its element type is the length."),
    # what an expression's type is
    C(T("uint8_t a = $a, b = $b;", S("sizeof(a)")), 1, "a is declared uint8_t: one byte."),
    C(T("uint8_t a = $a, b = $b;", S("sizeof(a + b)")), 4, "Adding promotes both to int first: the sum is an int, not a uint8_t."),
    C(T("uint8_t a = $a;", S("sizeof(-a)")), 4, "The unary minus promotes a to int first."),
    C(T("uint8_t a = $a;", S("sizeof(~a)")), 4, "The ~ promotes a to int first."),
    C(T("uint8_t a = $a, b = $b;", S("sizeof((uint8_t)(a + b))")), 1, "The cast squeezes the sum back into a uint8_t."),
    C(T("uint8_t a = $a;", S("sizeof(a * 1.0)")), 8, "A double is in the product, so it is a double."),
    C(T("uint8_t a = $a;", S("sizeof(a * 1.0f)")), 4, "The 1.0f is a float and nothing is wider: the product is a float."),
    C(T("uint8_t a = $a;", S("sizeof(a + 1LL)")), 8, "The long long operand wins: the sum is 8 bytes."),
    C(T("uint16_t a = $a;", S("sizeof(a + a)")), 4, "Promoted to int: an int sum."),
    C(T("int16_t x = $a;", PF("%zu %zu", "sizeof(x++), sizeof(x + 1)")), "2 4", "x++ has the type of x (2 bytes); x + 1 is promoted to int (4)."),
    C(T("int x = $a;", "size_t s = sizeof(x++);", PF("%zu %d", "s, x")), lambda p: f"4 {p['a']}", "sizeof does not run its operand, only looks at its type: x is unchanged."),
    C(T("uint8_t a = $a, b = $b;", PF("%zu", "sizeof(a < b)")), 4, "A comparison gives an int."),
    C(S("sizeof('x')"), 4, "In C a character constant is an int, not a char."),
    C(S("sizeof(1.5f)"), 4, "The f suffix makes it a float."),
    C(S("sizeof(1.5)"), 8, "A decimal constant with no suffix is a double."),
    C(S("sizeof(1LL)"), 8, "LL makes it a long long."),
    C(S("sizeof(1u)"), 4, "u makes it an unsigned int."),
    C(S("sizeof(1 + 2.0f)"), 4, "int and float meet: the float wins, 4 bytes."),
    C(S("sizeof(1 + 2.0)"), 8, "int and double meet: the double wins, 8 bytes."),
    C(PF("%d", "sizeof(int) > -1"), 0, "sizeof is unsigned, so -1 is turned into a huge unsigned number first: the comparison is false."),
    # structs (members no wider than 4 bytes: the same padding everywhere here)
    _type_struct("uint8_t a, b;", 2, "Two bytes, no gaps."),
    _type_struct("uint32_t a, b;", 8, "Two 4-byte members."),
    _type_struct("uint16_t a, b, c;", 6, "Three 2-byte members, no gaps."),
    _type_struct("uint8_t a[3];", 3, "An array of 3 bytes."),
    _sum_vs_struct("uint8_t a; uint32_t b;", "sizeof(uint8_t) + sizeof(uint32_t)", 8, 5),
    _sum_vs_struct("uint8_t a; uint16_t b;", "sizeof(uint8_t) + sizeof(uint16_t)", 4, 3),
    _sum_vs_struct("uint32_t a; uint8_t b;", "sizeof(uint32_t) + sizeof(uint8_t)", 8, 5),
    _sum_vs_struct("uint8_t a; uint16_t b; uint8_t c;", "sizeof(uint8_t) * 2 + sizeof(uint16_t)", 6, 4),
    _sum_vs_struct("uint8_t a; uint8_t b; uint16_t c;", "sizeof(uint8_t) * 2 + sizeof(uint16_t)", 4, 4),
]


# ── 2. Convert It ───────────────────────────────────────────────────────

def _f(x: float, d: int) -> str:
    return fixed_exact(x, d)


CONVERT: list[Maker] = [
    # integer / floating point
    C(T("double d = $n / $a;", PF("%.1f", "d")), lambda p: _f(float(tdiv(p["n"], p["a"])), 1), "n / a is an integer division and is only then stored in the double."),
    C(T("double d = $n / (double)$a;", PF("%.2f", "d")), lambda p: _f(p["n"] / p["a"], 2), "One operand is a double, so the other is converted and the division keeps its fraction."),
    C(T("double d = $n / $a.0;", PF("%.2f", "d")), lambda p: _f(p["n"] / p["a"], 2), "The constant $a.0 is a double, so the division is a real division."),
    C(T("int n = $n, k = $a;", "double d = (double)(n / k);", PF("%.1f", "d")), lambda p: _f(float(tdiv(p["n"], p["a"])), 1), "The cast comes too late: the integer division has already cut the fraction."),
    C(T("int n = $n, k = $a;", "double d = (double)n / k;", PF("%.2f", "d")), lambda p: _f(p["n"] / p["a"], 2), "The cast applies to n alone, so k is converted too and the division is real."),
    C(T("int a = $a, b = $b;", "double avg = (a + b) / 2;", PF("%.1f", "avg")), lambda p: _f(float(tdiv(p["a"] + p["b"], 2)), 1), "(a + b) / 2 is an int division: a .5 is lost before the double is made."),
    C(T("int a = $a, b = $b;", "double avg = (a + b) / 2.0;", PF("%.1f", "avg")), lambda p: _f((p["a"] + p["b"]) / 2, 1), "2.0 is a double, so the division keeps the .5."),
    C(T("float f = $n;", PF("%.1f", "f / 4")), lambda p: _f(p["n"] / 4, 1), "f is a float, so f / 4 is a float division; the float is promoted to double for printf."),
    C(T("double d = 7.9;", "int x = d;", PF("%d", "x")), 7, "Converting a double to int cuts the fraction off."),
    C(T("double d = -$a.9;", "int x = d;", PF("%d", "x")), lambda p: -p["a"], "The conversion cuts toward zero, not down: -$a.9 becomes -$a."),
    C(T("int x = $a * 2.5;", PF("%d", "x")), lambda p: int(p["a"] * 2.5), "a * 2.5 is a double; stored in an int it is cut."),
    C(T("int x = $a + 0.5;", PF("%d", "x")), lambda p: p["a"], "a + 0.5 is a double between a and a+1; the int keeps only a."),
    C(T("double d = 0.29;", "int cents = (int)(d * 100);", PF("%d", "cents")), 28, "0.29 is not exact in binary: d * 100 is 28.999..., and the cast cuts it to 28."),
    C(T("double d = 4.35;", "int cents = (int)(d * 100);", PF("%d", "cents")), 434, "4.35 is stored as 4.3499999...: times 100 is 434.99..., which the cast cuts to 434."),
    C(T("double d = 1.15;", "int cents = (int)(d * 100);", PF("%d", "cents")), 114, "1.15 is stored a little low: times 100 is 114.99..., which the cast cuts to 114."),
    C(T("double d = 0.5;", "int x = (int)(d * $a);", PF("%d", "x")), lambda p: int(0.5 * p["a"]), "0.5 times an int is exact, then cut toward zero."),
    C(T("float f = 0.1f;", PF("%.9f", "f")), lambda p: _f(f32(0.1), 9), "0.1f is the nearest float to 0.1; printing it with 9 decimals shows the difference."),
    C(T("double d = 0.1;", PF("%.17f", "d")), lambda p: _f(0.1, 17), "0.1 has no exact binary form: 17 decimals show what is really stored."),
    C(T("double x = $a / 4.0;", PF("%.2f", "x")), lambda p: _f(p["a"] / 4, 2), "a / 4.0 is exact in binary (a quarter), so it prints as it is."),
    C(T("long long p = (long long)$big * $big;", PF("%lld", "p")), lambda p: p["big"] * p["big"], "The cast makes the first operand 64 bits wide, so the product does not overflow."),
    C(T("long long p = $big;", "p *= $big;", PF("%lld", "p")), lambda p: p["big"] * p["big"], "p is a long long, so p *= n is worked out in 64 bits."),
    # signed / unsigned and promotion
    C(T("int8_t a = -1;", "uint8_t b = $a;", PF("%d", "a < b")), 1, "Both are promoted to int first, so it is -1 < a: true."),
    C(T("int16_t a = -$a;", "uint16_t b = $b;", PF("%d", "a < b")), 1, "Both are promoted to int, so the signs are kept: true."),
    C(T("int a = -$a;", "uint8_t b = $b;", PF("%d", "a < b")), 1, "b is promoted to int, not to unsigned: an ordinary comparison, true."),
    C(T("int8_t a = -1;", "uint32_t b = $a;", PF("%d", "a < b")), 0, "a is promoted to int and then converted to unsigned with b: -1 becomes a huge number."),
    C(T("int8_t a = -$a;", "uint8_t b = $b;", PF("%d", "a > b")), 0, "Both are promoted to int: -a > b is false."),
    C(T("uint8_t a = $u;", "int8_t b = -56;", PF("%d", "a == b")), 0, "b is promoted to -56, a to $u: they differ."),
    C(T("uint8_t a = 200;", "int8_t b = -56;", PF("%d", "a == (uint8_t)b")), 1, "(uint8_t)-56 is 200: the cast makes them equal."),
    C(PF("%d", "-1 < 0u"), 0, "-1 is converted to unsigned, a huge number, so it is not below 0."),
    C(PF("%d", "-$a < $b"), 1, "Both are plain ints: -a is below b."),
    C(T("unsigned u = $a;", PF("%u", "u - $n")), lambda p: wrap(p["a"] - p["n"], UINT), "unsigned arithmetic wraps around: a - n becomes 2 to the 32nd minus (n - a)."),
    C(T("int i = -$n;", "unsigned u = $a;", PF("%u", "i + u")), lambda p: wrap(-p["n"] + p["a"], UINT), "i is converted to unsigned, so the sum wraps instead of going negative."),
    C(PF("%u", "-7 / 2u"), (2**32 - 7) // 2, "-7 is converted to unsigned (4294967289) before the division."),
    C(T("int c = $r;", PF("%u", "c ? -1 : 1u")), lambda p: 4294967295 if p["r"] else 1, "The two branches meet in unsigned, so a true test gives -1 converted: 4294967295."),
    C(T("int c = $r;", PF("%.1f", "c ? 1 : 2.5")), lambda p: "1.0" if p["r"] else "2.5", "The two branches meet in double, so even the 1 comes out as 1.0."),
    # casts to fixed-width types
    C(PF("%d", "(uint8_t)-1"), 255, "Converting to unsigned wraps modulo 256: -1 is 255."),
    C(PF("%d", "(uint8_t)-$a"), lambda p: 256 - p["a"], "Converting to unsigned wraps modulo 256."),
    C(PF("%d", "(uint16_t)-1"), 65535, "Converting to unsigned wraps modulo 65536."),
    C(PF("%u", "(uint32_t)-$a"), lambda p: 2**32 - p["a"], "Converting to unsigned wraps modulo 2 to the 32nd."),
    C(T("int big = $big;", PF("%d", "(uint16_t)big")), lambda p: p["big"] % 65536, "The cast keeps the low 16 bits: the number modulo 65536."),
    C(T("unsigned u = $big;", PF("%d", "(uint8_t)u")), lambda p: p["big"] % 256, "The cast keeps the low 8 bits: the number modulo 256."),
    C(T("double d = $u.75;", PF("%d", "(uint8_t)d")), lambda p: p["u"], "A double that fits is cut toward zero, then stored."),
    C(T("uint8_t a = $u;", PF("%d", "(uint8_t)(a + $n)")), lambda p: (p["u"] + p["n"]) % 256, "The int sum is squeezed back into 8 bits: modulo 256."),
    C(T("uint8_t a = $a;", PF("%d", "(int)(a - $b)")), lambda p: p["a"] - p["b"], "a - b is worked out as int, so it just goes negative."),
    C(T("uint32_t a = $a;", PF("%u", "a - $b")), lambda p: wrap(p["a"] - p["b"], UINT), "uint32_t arithmetic is unsigned, so below 0 it wraps around."),
    # characters
    C(T("char c = 'a';", PF("%d", "c")), 97, "A char is a small number; printed with %d it shows its code."),
    C(T("char c = 'a';", PF("%d", "c + $a")), lambda p: 97 + p["a"], "c is promoted to int, so the sum is a number."),
    C(T("char c = 'a';", PF("%c", "c + $a")), lambda p: chr(97 + p["a"]), "The int sum is printed with %c as the character with that code."),
    C(T("char c = 'z';", PF("%c", "c - $a")), lambda p: chr(122 - p["a"]), "Going back a letters from z."),
    C(PF("%d", "'z' - 'a'"), 25, "Letters have consecutive codes: z is 25 after a."),
    C(PF("%d", "'$X' - 'A'"), lambda p: ord(p["X"]) - 65, "Capital letters have consecutive codes too: the position in the alphabet, from 0."),
    C(T("char d = '7';", PF("%d", "d - '0'")), 7, "Digit characters have consecutive codes, so subtracting '0' gives the number."),
    C(T("int n = $a;", PF("%c", "'0' + n")), lambda p: str(p["a"]), "'0' plus a number is the code of that digit character."),
    C(T("char c = '$x';", PF("%c", "c - 32")), lambda p: p["X"], "A lower-case letter is 32 above its capital."),
    C(T("char c = '$X';", PF("%c", "c + 32")), lambda p: p["x"], "A capital letter is 32 below its lower-case letter."),
    C(T("char c = 'A';", "c += $a;", PF("%c", "c")), lambda p: chr(65 + p["a"]), "Adding to a char moves along the alphabet."),
    # _Bool
    C(T("_Bool b = $n;", PF("%d", "b")), 1, "Converting to _Bool gives 1 for anything nonzero, not the value."),
    C(T("double d = 0.5;", "_Bool b = d;", PF("%d", "b")), 1, "0.5 is not zero, so it is true: _Bool does not cut the fraction first."),
    C(T("int n = 256 + $a;", "_Bool b = n;", "uint8_t u = n;", PF("%d %d", "b, u")), lambda p: f"1 {p['a']}", "_Bool keeps true/false only; uint8_t keeps the number modulo 256."),
]
