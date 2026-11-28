"""Numbers in Depth: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 105

DECK = Deck(
    id="py-numbers",
    title="Numbers in Depth",
    language="python",
    blurb="Big ints, float precision, Decimal and Fraction, rounding, bits, math functions, inf, nan and complex numbers.",
    slides=(
        Slide(
            title="Ints never overflow",
            text="A Python int grows as large as memory allows. There is no 32-bit or 64-bit limit to wrap around, so big arithmetic is always exact.",
            code=r"""print(2 ** 100)
print(len(str(2 ** 100)))
print(10 ** 20 + 1)""",
            output="1267650600228229401496703205376\n31\n100000000000000000001",
            point="No overflow in Python ints; only memory is the limit.",
        ),
        Slide(
            title="Float precision: 0.1 + 0.2",
            text="A float stores a binary fraction, and 0.1 cannot be written exactly in binary. So tiny errors appear, and comparing floats with == is unreliable.",
            code=r"""print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
print(0.5 + 0.25 == 0.75)""",
            output="0.30000000000000004\nFalse\nTrue",
            point="Fractions like 0.5 and 0.25 are exact; 0.1 and 0.2 are not.",
        ),
        Slide(
            title="round(2.675, 2) is 2.67",
            text="Writing 2.675 really stores a value just under it, so rounding to two places goes down. Formatting agrees. Only an exact tie such as 0.125 goes to the even digit.",
            code=r"""print(round(2.675, 2))
print(f"{2.675:.2f}")
print(f"{0.125:.2f}")""",
            output="2.67\n2.67\n0.12",
            point="What you type is not always what the float holds.",
        ),
        Slide(
            title="math.isclose for floats",
            text="Instead of ==, ask whether two floats are close. isclose uses a relative tolerance by default; near zero, add abs_tol, because a relative gap to zero is always huge.",
            code=r"""import math
print(math.isclose(0.1 + 0.2, 0.3))
print(math.isclose(1.0, 1.1))
print(math.isclose(0, 1e-12))
print(math.isclose(0, 1e-12, abs_tol=1e-9))""",
            output="True\nFalse\nFalse\nTrue",
            point="Compare floats with isclose, and give abs_tol when a value may be 0.",
        ),
        Slide(
            title="Decimal for money",
            text="Decimal stores base-10 digits exactly. Build it from a string, never from a float, or the float's error comes along. quantize rounds to a set number of places.",
            code=r"""from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2"))
print(Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))
print(Decimal("1.10") * 3)
print(Decimal("2.675").quantize(Decimal("0.01")))""",
            output="0.3\nTrue\n3.30\n2.68",
            point="Money belongs in Decimal built from strings.",
        ),
        Slide(
            title="fractions.Fraction",
            text="Fraction keeps an exact numerator and denominator and always reduces them. It never loses precision, so 1/3 plus 1/6 is exactly one half.",
            code=r"""from fractions import Fraction
print(Fraction(1, 3) + Fraction(1, 6))
print(Fraction(3, 6))
print(Fraction("0.25"))
print(float(Fraction(1, 4)))""",
            output="1/2\n1/2\n1/4\n0.25",
            point="Fraction is exact rational arithmetic.",
        ),
        Slide(
            title="Floor division and modulo with negatives",
            text="// rounds down toward minus infinity, not toward zero, and % is defined so that a == (a // b) * b + a % b. The sign of a % b follows b. divmod gives both at once.",
            code=r"""print(divmod(17, 5))
print(-7 // 2, -7 % 2)
print(7 // -2, 7 % -2)
print(divmod(-7, 2))""",
            output="(3, 2)\n-4 1\n-4 -1\n(-4, 1)",
            point="// rounds down, so -7 // 2 is -4, and % keeps the pair consistent.",
        ),
        Slide(
            title="round: half goes to even",
            text="Python's round sends an exact tie to the nearest even number, which avoids always rounding up. A negative second argument rounds to tens, hundreds and so on.",
            code=r"""print(round(0.5), round(1.5))
print(round(2.5), round(3.5))
print(round(1234, -2))
print(round(1.26, 1))""",
            output="0 2\n2 4\n1200\n1.3",
            point="round(2.5) is 2 and round(3.5) is 4: ties go to even.",
        ),
        Slide(
            title="int(), float() and bases",
            text="int() on a float cuts off the decimals toward zero. int(text, base) reads digits in another base, such as 16 for hex and 2 for binary. float() reads decimal text.",
            code=r"""print(int("42"), int(3.99), int(-3.99))
print(float("2.5"))
print(int("ff", 16), int("101", 2))
print(int(" 7 "))""",
            output="42 3 -3\n2.5\n255 5\n7",
            point="int() truncates toward zero; int(s, base) parses other bases.",
        ),
        Slide(
            title="bin, oct, hex and format",
            text="bin, oct and hex give text with a 0b, 0o or 0x prefix. format with a code builds the same digits with padding and no prefix: b is binary, X is uppercase hex, and 08 pads with zeros to width 8.",
            code=r"""print(bin(10), oct(8), hex(255))
print(format(5, "08b"))
print(format(255, "X"))
print(f"{255:#x}")""",
            output="0b1010 0o10 0xff\n00000101\nFF\n0xff",
            point="Use format(n, '08b') for padded binary digits.",
        ),
        Slide(
            title="Bitwise operators",
            text="& keeps bits set in both numbers, | keeps bits set in either, and ^ keeps bits set in exactly one. ~ flips every bit, and << and >> slide the bits left and right.",
            code=r"""print(12 & 10)
print(12 | 10)
print(12 ^ 10)
print(~12)
print(1 << 4, 256 >> 2)""",
            output="8\n14\n6\n-13\n16 64",
            point="Shifting left by n multiplies by 2**n; ~x is -x - 1.",
        ),
        Slide(
            title="bit_count and bit tricks",
            text="int.bit_count() counts the 1 bits, and needs Python 3.10 or newer. n & (n - 1) switches off the lowest 1 bit, so it is zero exactly for powers of two.",
            code=r"""print((255).bit_count())
print((10).bit_count())
print(12 & 11)
print(16 & 15 == 0, 18 & 17 == 0)""",
            output="8\n2\n8\nTrue False",
            point="n & (n - 1) == 0 is the quick test for a power of two.",
        ),
        Slide(
            title="math: sqrt, floor, gcd, comb",
            text="sqrt always gives a float. floor rounds down and ceil rounds up to an int. gcd is the greatest common divisor, lcm the least common multiple (3.9+), comb counts choices, and perm counts ordered choices.",
            code=r"""import math
print(math.sqrt(16), math.floor(-2.5), math.ceil(2.1))
print(math.gcd(12, 18), math.lcm(4, 6))
print(math.comb(5, 2), math.perm(5, 2))""",
            output="4.0 -3 3\n6 12\n10 20",
            point="comb(5, 2) ignores order; perm(5, 2) counts it.",
        ),
        Slide(
            title="inf and nan",
            text="float('inf') is bigger than every number. nan means 'not a number', and it is not equal to anything, not even itself, so test it with math.isnan.",
            code=r"""import math
inf = float("inf")
nan = float("nan")
print(inf > 10 ** 100, -inf < 0)
print(nan == nan, nan != nan)
print(math.isnan(inf - inf), max(1, inf))""",
            output="True True\nFalse True\nTrue inf",
            point="Never test for nan with ==; use math.isnan().",
        ),
        Slide(
            title="Complex numbers",
            text="A complex number has a real and an imaginary part, written with a j. Python supports them directly: abs gives the length, conjugate flips the sign of the imaginary part, and 1j squared is minus one.",
            code=r"""z = 3 + 4j
print(abs(z), z.real, z.imag)
print(z * z)
print(z.conjugate())
print(1j ** 2)""",
            output="5.0 3.0 4.0\n(-7+24j)\n(3-4j)\n(-1+0j)",
            point="j is the imaginary unit in Python, not i.",
        ),
    ),
)
