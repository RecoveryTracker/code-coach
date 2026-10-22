"""Words the Brain Drills logic pack teaches: logical operators, negation, De Morgan, equivalence, truth tables,
bitwise operators, shifts, binary, masks, chained comparisons, boundaries, divisibility, leap years, FizzBuzz, primes
and division."""

from __future__ import annotations

from .entry import Entry, both

TERMS: list[Entry] = [
    *both(
        "logical-operator",
        "Logical operator",
        "A word or symbol that combines true-or-false values: and, or, not (in JavaScript &&, || and !).",
        see=("boolean", "short-circuit", "precedence", "truth-table"),
        priority=50,
        aka=("logical operators", "boolean operator", "boolean operators", "logic operator", "logical and", "logical or"),
        python=dict(
            rules=(
                "a and b needs both; a or b needs at least one; not a flips it.",
                "Order of work: not first, then and, then or. So True or False and False is True (the and goes first).",
                "and / or hand back one of the actual values, not always True or False (see short-circuit).",
            ),
            example="""
                print(True and False, True or False, not True, not False or True, True or False and False)
            """,
            out="False True False True True",
        ),
        javascript=dict(
            rules=(
                "a && b needs both; a || b needs at least one; !a flips it.",
                "Order of work: ! first, then &&, then ||. So true || false && false is true (the && goes first).",
                "&& and || hand back one of the actual values, not always true or false (see short-circuit).",
            ),
            example="""
                console.log(true && false, true || false, !true, !false || true, true || false && false);
            """,
            out="false true false true true",
        ),
    ),
    *both(
        "negation",
        "Negation (not)",
        "Flipping a true-or-false value: not true is false and not false is true.",
        see=("logical-operator", "boolean", "de-morgan"),
        priority=45,
        aka=("not", "negate", "negated", "negating", "invert", "!"),
        python=dict(
            rules=(
                "not always gives True or False, whatever it is given: not 0 is True and not 'hi' is False.",
                "not not x turns any value into a plain True or False.",
                "Negating a comparison turns it around: not (a < b) means a >= b, for numbers.",
            ),
            detect=(r"\bnot\b",),
            example="""
                print(not 0, not "hi", not [], not not "a")
            """,
            out="True False True True",
        ),
        javascript=dict(
            rules=(
                "! always gives true or false, whatever it is given: !0 is true and !'hi' is false.",
                "!!x turns any value into a plain true or false.",
                "Negating a comparison turns it around: !(a < b) means a >= b, for numbers.",
            ),
            detect=(r"(?<![!=<>])!(?!=)",),
            example="""
                console.log(!0, !"hi", ![], !![]);
            """,
            out="true false false true",
        ),
    ),
    *both(
        "de-morgan",
        "De Morgan's laws",
        "Two rules for turning a not around an and/or: not (A and B) is (not A) or (not B), and not (A or B) is (not A) and (not B).",
        see=("negation", "logical-operator", "equivalence"),
        priority=60,
        aka=("de morgan", "demorgan", "de morgan's law", "de morgan's laws", "de morgans laws"),
        python=dict(
            rules=(
                "Flip the and to or (or the or to and) and negate each part.",
                "Use it to simplify: not (x > 3 and x < 9) is x <= 3 or x >= 9.",
                "Both laws hold for every combination of True and False; the example checks all four.",
            ),
            detect=(r"\bnot\s*\([^)\n]*\b(?:and|or)\b",),
            example="""
                for a in (True, False):
                    for b in (True, False):
                        print(a, b, (not (a and b)) == ((not a) or (not b)), (not (a or b)) == ((not a) and (not b)))
            """,
            out="True True True True\nTrue False True True\nFalse True True True\nFalse False True True",
        ),
        javascript=dict(
            rules=(
                "Flip the && to || (or the || to &&) and negate each part.",
                "Use it to simplify: !(x > 3 && x < 9) is x <= 3 || x >= 9.",
                "Both laws hold for every combination of true and false; the example checks all four.",
            ),
            detect=(r"!\s*\([^)\n]*(?:&&|\|\|)",),
            example="""
                for (const a of [true, false]) {
                  for (const b of [true, false]) {
                    console.log(a, b, !(a && b) === (!a || !b), !(a || b) === (!a && !b));
                  }
                }
            """,
            out="true true true true\ntrue false true true\nfalse true true true\nfalse false true true",
        ),
    ),
    *both(
        "equivalence",
        "Equivalence",
        "Two conditions are equivalent when they give the same answer for every possible input, even though they look different.",
        see=("de-morgan", "truth-table", "condition"),
        priority=50,
        aka=("equivalent", "logically equivalent", "same condition", "same result", "rewrite a condition"),
        python=dict(
            rules=(
                "To prove two conditions equivalent you must check all inputs (a truth table does); to disprove, one input that differs is enough.",
                "not (x > 3) is equivalent to x <= 3 for numbers.",
                "A or B and C is NOT equivalent to (A or B) and C: and binds tighter than or.",
            ),
            example="""
                print(all((not (x > 3)) == (x <= 3) for x in range(-5, 10)))
                print(all((a or b and c) == ((a or b) and c) for a in (0, 1) for b in (0, 1) for c in (0, 1)))
            """,
            out="True\nFalse",
        ),
        javascript=dict(
            rules=(
                "To prove two conditions equivalent you must check all inputs (a truth table does); to disprove, one input that differs is enough.",
                "!(x > 3) is equivalent to x <= 3 for numbers.",
                "A || B && C is NOT equivalent to (A || B) && C: && binds tighter than ||.",
            ),
            example="""
                let same = true;
                for (let x = -5; x < 10; x++) {
                  if (!(x > 3) !== (x <= 3)) same = false;
                }
                let same2 = true;
                for (const a of [0, 1]) for (const b of [0, 1]) for (const c of [0, 1]) {
                  if ((a || (b && c)) !== ((a || b) && c)) same2 = false;
                }
                console.log(same, same2);
            """,
            out="true false",
        ),
    ),
    *both(
        "truth-table",
        "Truth table",
        "A table that lists every possible combination of true and false inputs and the result for each.",
        see=("logical-operator", "equivalence", "boolean"),
        priority=50,
        aka=("truth tables", "all combinations", "table of values"),
        python=dict(
            rules=(
                "With n inputs there are 2**n rows: two inputs give 4 rows, three give 8.",
                "Reading it: and is true only in the row where both inputs are true; or is false only where both are false.",
                "Two conditions are equivalent exactly when their columns are identical.",
            ),
            example="""
                print("a b and or")
                for a in (False, True):
                    for b in (False, True):
                        print(int(a), int(b), int(a and b), int(a or b))
            """,
            out="a b and or\n0 0 0 0\n0 1 0 1\n1 0 0 1\n1 1 1 1",
        ),
        javascript=dict(
            rules=(
                "With n inputs there are 2**n rows: two inputs give 4 rows, three give 8.",
                "Reading it: && is true only in the row where both inputs are true; || is false only where both are false.",
                "Two conditions are equivalent exactly when their columns are identical.",
            ),
            example="""
                console.log("a b and or");
                for (const a of [false, true]) {
                  for (const b of [false, true]) {
                    console.log(+a, +b, +(a && b), +(a || b));
                  }
                }
            """,
            out="a b and or\n0 0 0 0\n0 1 0 1\n1 0 0 1\n1 1 1 1",
        ),
    ),
    *both(
        "bitwise",
        "Bitwise operators",
        "Operators that work on the individual binary digits (bits) of whole numbers: & (and), | (or), ^ (exclusive or) and ~ (not).",
        see=("binary", "bit-shift", "mask"),
        priority=50,
        aka=("bitwise operator", "bitwise operators", "bitwise and", "bitwise or", "xor", "bit operations", "bit operation", "&", "^", "~"),
        python=dict(
            rules=(
                "6 is 110 in binary and 3 is 011: 6 & 3 keeps the bits set in both (010 = 2), 6 | 3 keeps bits set in either (111 = 7), 6 ^ 3 keeps bits set in exactly one (101 = 5).",
                "~x flips every bit and is always -x - 1, so ~6 is -7.",
                "& | ^ work on bits; and / or work on true-or-false. 1 and 2 is 2, but 1 & 2 is 0.",
            ),
            detect=(r"[\w)]\s*(?:&|\^)\s*[\w(~]|(?<![\w)\s])\s*~\w|[\w)]\s+\|\s+[\w(]",),
            example="""
                print(6 & 3, 6 | 3, 6 ^ 3, ~6, 1 and 2, 1 & 2)
            """,
            out="2 7 5 -7 2 0",
        ),
        javascript=dict(
            rules=(
                "6 is 110 in binary and 3 is 011: 6 & 3 keeps the bits set in both (010 = 2), 6 | 3 keeps bits set in either (111 = 7), 6 ^ 3 keeps bits set in exactly one (101 = 5).",
                "~x flips every bit and is always -x - 1, so ~6 is -7.",
                "JavaScript does these on 32-bit signed integers, so 2**32 | 0 is 0 and 1 << 31 is negative.",
                "& | ^ work on bits; && and || work on true-or-false. 1 && 2 is 2, but 1 & 2 is 0.",
            ),
            detect=(r"[\w)]\s*(?:&(?!&)|\^)\s*[\w(~]|~\w|[\w)]\s+\|(?!\|)\s+[\w(]",),
            example="""
                console.log(6 & 3, 6 | 3, 6 ^ 3, ~6, 1 && 2, 1 & 2);
            """,
            out="2 7 5 -7 2 0",
        ),
    ),
    *both(
        "bit-shift",
        "Bit shift",
        "Sliding all the bits of a number left or right. Each step left doubles the number; each step right halves it, rounding down.",
        see=("bitwise", "binary", "mask"),
        priority=50,
        aka=("shift", "shifts", "left shift", "right shift", "<<", ">>", ">>>", "bit shifting", "shifting"),
        python=dict(
            rules=(
                "x << n is x * 2**n, so 1 << 3 is 8.",
                "x >> n is x // 2**n (rounding down), so 20 >> 2 is 5 and -8 >> 1 is -4.",
                "Python integers have no size limit, so a left shift never overflows.",
            ),
            detect=(r"<<|>>",),
            example="""
                print(1 << 3, 20 >> 2, -8 >> 1, 5 << 0)
            """,
            out="8 5 -4 5",
        ),
        javascript=dict(
            rules=(
                "x << n is x * 2**n, so 1 << 3 is 8.",
                "x >> n halves n times, rounding down and keeping the sign: 20 >> 2 is 5 and -8 >> 1 is -4.",
                "x >>> n treats x as an unsigned 32-bit number and fills with zeros: -1 >>> 28 is 15.",
            ),
            detect=(r"<<|>>",),
            example="""
                console.log(1 << 3, 20 >> 2, -8 >> 1, -1 >>> 28);
            """,
            out="8 5 -4 15",
        ),
    ),
    *both(
        "binary",
        "Binary",
        "Writing numbers with only the digits 0 and 1. Each place is worth double the one to its right: 1, 2, 4, 8, 16...",
        see=("bitwise", "bit-shift", "integer"),
        priority=40,
        aka=("base 2", "bits", "bit", "binary number", "binary numbers", "base two", "0b"),
        python=dict(
            rules=(
                "101 in binary is 4 + 0 + 1 = 5.",
                "bin(5) is '0b101'; int('101', 2) reads binary text back; 0b1010 is the number 10 written in binary.",
                "f'{10:08b}' writes 10 in binary padded to 8 digits.",
            ),
            detect=(r"\bbin\(|\b0b[01]+|:0?\d*b\}",),
            example="""
                print(bin(5), int("101", 2), 0b1010, f"{10:08b}")
            """,
            out="0b101 5 10 00001010",
        ),
        javascript=dict(
            rules=(
                "101 in binary is 4 + 0 + 1 = 5.",
                "(5).toString(2) is '101'; parseInt('101', 2) reads binary text back; 0b1010 is the number 10 written in binary.",
                "(10).toString(2).padStart(8, '0') writes 10 in binary padded to 8 digits.",
            ),
            detect=(r"\btoString\(\s*2\s*\)|\b0b[01]+|parseInt\([^)]*,\s*2\s*\)",),
            example="""
                console.log((5).toString(2), parseInt("101", 2), 0b1010, (10).toString(2).padStart(8, "0"));
            """,
            out="101 5 10 00001010",
        ),
    ),
    *both(
        "mask",
        "Bit mask",
        "A number whose binary digits pick out certain bits of another number. AND keeps the picked bits, OR sets them, XOR flips them.",
        see=("bitwise", "binary", "bit-shift"),
        priority=50,
        aka=("bitmask", "bit mask", "masking", "flags", "bit flag", "bit flags"),
        python=dict(
            rules=(
                "x & 0b1111 keeps only the lowest four bits; x | 0b10 turns bit 1 on; x ^ 1 flips bit 0.",
                "To test one bit: x & (1 << k) is non-zero when bit k is set.",
                "Use 0b... or 0x... to write the mask so the bits are visible.",
            ),
            example="""
                x = 0b101101
                print(x & 0b1111, x | 0b10, x ^ 1, bool(x & 0b100))
            """,
            out="13 47 44 True",
        ),
        javascript=dict(
            rules=(
                "x & 0b1111 keeps only the lowest four bits; x | 0b10 turns bit 1 on; x ^ 1 flips bit 0.",
                "To test one bit: x & (1 << k) is non-zero when bit k is set.",
                "Use 0b... or 0x... to write the mask so the bits are visible.",
            ),
            example="""
                const x = 0b101101;
                console.log(x & 0b1111, x | 0b10, x ^ 1, (x & 0b100) !== 0);
            """,
            out="13 47 44 true",
        ),
    ),
    *both(
        "chained-comparison",
        "Chained comparison",
        "Writing two comparisons in a row, like 1 < x < 5, to mean that x is between the two numbers.",
        see=("comparison", "short-circuit", "boundary"),
        priority=55,
        aka=("chained comparisons", "chain comparisons", "between", "range check", "in range"),
        python=dict(
            rules=(
                "Python reads 1 < x < 5 as 1 < x and x < 5, with x worked out only once.",
                "It can chain any comparisons: 1 < 2 < 3 < 4 is True, and 5 > x > 1 is the same test written backwards.",
                "The two ends are included only with <= : 1 <= x <= 5.",
            ),
            detect=(r"[\w)\]]\s*(?:<|<=|>|>=)\s*[\w(\[-]+\s*(?:<|<=|>|>=)\s*[\w(\[-]",),
            example="""
                x = 3
                print(1 < x < 5, 1 < x < 3, 5 > x > 1, 1 < 2 < 3 < 4)
            """,
            out="True False True True",
        ),
        javascript=dict(
            rules=(
                "JavaScript does NOT chain: 1 < x < 5 is (1 < x) < 5, and a true or false is compared with 5 as 1 or 0.",
                "So 10 < x < 5 is true for x = 3: 10 < 3 is false, false counts as 0, and 0 < 5 is true.",
                "Write both tests with &&: 1 < x && x < 5.",
            ),
            detect=(r"[\w)\]]\s*(?:<|<=|>|>=)\s*[\w(\[-]+\s*(?:<|<=|>|>=)\s*[\w(\[-]",),
            example="""
                const x = 3;
                console.log(1 < x && x < 5, 10 < x < 5);
            """,
            out="true true",
        ),
    ),
    *both(
        "boundary",
        "Boundary",
        "The edge of a range: the first or last value that still counts. Many bugs happen exactly on the boundary.",
        see=("off-by-one", "comparison", "chained-comparison"),
        priority=50,
        aka=("boundaries", "bounds", "edge", "edges", "edge case", "edge cases", "inclusive", "exclusive", "limit", "limits", "upper bound", "lower bound"),
        python=dict(
            see=("off-by-one", "comparison", "chained-comparison", "range"),
            rules=(
                "A boundary is inclusive if the edge value counts and exclusive if it does not.",
                "< and > exclude the edge; <= and >= include it: 5 < 5 is False but 5 <= 5 is True.",
                "range(1, 5) includes its start and excludes its stop, so it holds 1, 2, 3, 4.",
            ),
            example="""
                print(list(range(1, 5)), 5 in range(1, 5), 5 < 5, 5 <= 5)
            """,
            out="[1, 2, 3, 4] False False True",
        ),
        javascript=dict(
            rules=(
                "A boundary is inclusive if the edge value counts and exclusive if it does not.",
                "< and > exclude the edge; <= and >= include it: 5 < 5 is false but 5 <= 5 is true.",
                "for (let i = 1; i < 5; i++) runs 4 times; changing < to <= makes it run 5.",
            ),
            example="""
                let n = 0, m = 0;
                for (let i = 1; i < 5; i++) n++;
                for (let i = 1; i <= 5; i++) m++;
                console.log(n, m);
            """,
            out="4 5",
        ),
    ),
    *both(
        "divisibility",
        "Divisibility",
        "A number is divisible by another when it divides with nothing left over: the remainder is 0.",
        see=("modulo", "floor-division", "negative-number"),
        priority=45,
        aka=("divisible", "multiple", "multiples", "factor", "factors", "even", "odd", "even or odd", "evenness"),
        python=dict(
            rules=(
                "n % d == 0 means n is divisible by d. An even number has n % 2 == 0; an odd one has n % 2 == 1.",
                "0 is divisible by everything: 0 % 5 is 0.",
                "Python's % is never negative for a positive d, so n % 2 == 1 is a safe odd test even for -3.",
            ),
            example="""
                print(12 % 4 == 0, 12 % 5 == 0, 7 % 2 == 1, 0 % 5, -3 % 2 == 1)
            """,
            out="True False True 0 True",
        ),
        javascript=dict(
            rules=(
                "n % d === 0 means n is divisible by d. An even number has n % 2 === 0.",
                "0 is divisible by everything: 0 % 5 is 0.",
                "-3 % 2 is -1 in JavaScript, so test odd with n % 2 !== 0, not n % 2 === 1.",
            ),
            example="""
                console.log(12 % 4 === 0, 12 % 5 === 0, 7 % 2 === 1, 0 % 5, -3 % 2 === 1, -3 % 2 !== 0);
            """,
            out="true false true 0 false true",
        ),
    ),
    *both(
        "leap-year",
        "Leap year",
        "A year with an extra day (29 February). The rule: divisible by 4, except century years, which must also be divisible by 400.",
        see=("divisibility", "logical-operator", "modulo"),
        priority=40,
        aka=("leap years", "leap", "is leap"),
        python=dict(
            rules=(
                "Every year divisible by 4 is a leap year, except those divisible by 100, unless they are also divisible by 400.",
                "So 2024 and 2000 are leap years, but 1900 and 2023 are not.",
                "As one test: year % 4 == 0 and (year % 100 != 0 or year % 400 == 0).",
            ),
            example="""
                def leap(y):
                    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
                print([leap(y) for y in (1900, 2000, 2023, 2024)])
            """,
            out="[False, True, False, True]",
        ),
        javascript=dict(
            rules=(
                "Every year divisible by 4 is a leap year, except those divisible by 100, unless they are also divisible by 400.",
                "So 2024 and 2000 are leap years, but 1900 and 2023 are not.",
                "As one test: year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0).",
            ),
            example="""
                const leap = (y) => y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0);
                console.log([1900, 2000, 2023, 2024].map(leap));
            """,
            out="[ false, true, false, true ]",
        ),
    ),
    *both(
        "fizzbuzz",
        "FizzBuzz",
        "A classic exercise: for each number say Fizz if it divides by 3, Buzz if it divides by 5, and FizzBuzz if it divides by both.",
        see=("divisibility", "modulo", "branch"),
        priority=40,
        aka=("fizz buzz", "fizz-buzz"),
        python=dict(
            rules=(
                "Test the both-case (divisible by 15) FIRST. If Fizz is tested first, 15 prints Fizz and never reaches FizzBuzz.",
                "n % 3 == 0 tests divisibility by 3.",
                "A number divisible by neither prints as itself.",
            ),
            example="""
                def fb(n):
                    if n % 15 == 0:
                        return "FizzBuzz"
                    if n % 3 == 0:
                        return "Fizz"
                    if n % 5 == 0:
                        return "Buzz"
                    return str(n)
                print(" ".join(fb(n) for n in range(9, 16)))
            """,
            out="Fizz Buzz 11 Fizz 13 14 FizzBuzz",
        ),
        javascript=dict(
            rules=(
                "Test the both-case (divisible by 15) FIRST. If Fizz is tested first, 15 prints Fizz and never reaches FizzBuzz.",
                "n % 3 === 0 tests divisibility by 3.",
                "A number divisible by neither prints as itself.",
            ),
            example="""
                function fb(n) {
                  if (n % 15 === 0) return "FizzBuzz";
                  if (n % 3 === 0) return "Fizz";
                  if (n % 5 === 0) return "Buzz";
                  return String(n);
                }
                console.log([9, 10, 11, 12, 13, 14, 15].map(fb).join(" "));
            """,
            out="Fizz Buzz 11 Fizz 13 14 FizzBuzz",
        ),
    ),
    *both(
        "prime",
        "Prime number",
        "A whole number above 1 whose only divisors are 1 and itself: 2, 3, 5, 7, 11...",
        see=("divisibility", "modulo", "loop"),
        priority=40,
        aka=("prime numbers", "primes", "is prime", "primality"),
        python=dict(
            rules=(
                "1 is not prime, and 2 is the only even prime.",
                "To test n, try dividing by 2, 3, ... up to the square root of n; if none divides, it is prime.",
                "A number that is not prime is called composite: 9 = 3 x 3.",
            ),
            example="""
                def prime(n):
                    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))
                print(*[n for n in range(1, 20) if prime(n)])
            """,
            out="2 3 5 7 11 13 17 19",
        ),
        javascript=dict(
            rules=(
                "1 is not prime, and 2 is the only even prime.",
                "To test n, try dividing by 2, 3, ... up to the square root of n; if none divides, it is prime.",
                "A number that is not prime is called composite: 9 = 3 x 3.",
            ),
            example="""
                function prime(n) {
                  if (n < 2) return false;
                  for (let d = 2; d * d <= n; d++) {
                    if (n % d === 0) return false;
                  }
                  return true;
                }
                const found = [];
                for (let n = 1; n < 20; n++) if (prime(n)) found.push(n);
                console.log(found.join(" "));
            """,
            out="2 3 5 7 11 13 17 19",
        ),
    ),
    *both(
        "division",
        "Division",
        "Splitting one number by another. Languages differ in whether the answer keeps its fraction and what happens when you divide by zero.",
        see=("floor-division", "modulo", "float"),
        priority=45,
        aka=("divide", "divides", "true division", "/", "divide by zero", "division by zero"),
        python=dict(
            rules=(
                "/ always gives a float: 6 / 3 is 2.0. // rounds down to a whole number, and % is the remainder.",
                "divmod(7, 2) gives both at once: (3, 1).",
                "Dividing by zero raises a ZeroDivisionError, for / and // and % alike.",
            ),
            example="""
                print(7 / 2, 6 / 3, 7 // 2, 7 % 2, divmod(7, 2))
            """,
            out="3.5 2.0 3 1 (3, 1)",
        ),
        javascript=dict(
            rules=(
                "/ always keeps the fraction: 7 / 2 is 3.5. There is no // : use Math.floor(7 / 2) (or Math.trunc) for a whole number.",
                "6 / 3 is just 2: JavaScript has one number type, so there is no 2.0.",
                "Dividing by zero does not raise an error: 1 / 0 is Infinity and 0 / 0 is NaN.",
            ),
            example="""
                console.log(7 / 2, 6 / 3, Math.floor(7 / 2), 7 % 2, 1 / 0, 0 / 0);
            """,
            out="3.5 2 3 1 Infinity NaN",
        ),
    ),
]
