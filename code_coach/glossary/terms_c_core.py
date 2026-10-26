"""C words, part 1: numbers, types and operators - integer types, conversions, overflow, division and %, characters,
sizeof, undefined behaviour, the operators with their precedence and side effects, bits and number bases.

C is the fourth glossary language (added 2026-10-23). Every example is the BODY of `main` unless it mentions `main(`
(the Brain Drills convention: the four headers stdio.h stdint.h string.h stddef.h are always in front, an example
never writes them; a complete program may #include more). Examples are run for real by tests/test_glossary.py through
tests/c_oracle.py on every build it has; every rule that can run is a program in C_RULE_CHECKS there. C strings below
are raw (r"...") because C is full of backslashes."""

from __future__ import annotations

from .entry import Entry, c

TERMS: list[Entry] = [
    *c(
        "integer",
        "Integer",
        "A whole-number type: char, short, int, long, long long, each signed or unsigned. C only promises minimum sizes, so how many bytes each has depends on the machine.",
        see=("fixed-width-integer", "signed-integer", "unsigned", "division", "overflow"),
        priority=30,
        aka=("integers", "int", "long", "short", "whole number", "integer type"),
        detect=(r"\b(?:int|short|long)\s+\**[A-Za-z_]\w*\s*[=;,\[(]",),
        rules=(
            r"int is at least 16 bits and almost always 32; long is 32 or 64 bits depending on the machine; long long is at least 64.",
            r"A plain constant like 42 is an int; add L or LL (42L, 42LL) for bigger types and u for unsigned (42u).",
            r"Integer arithmetic never gives a fraction: 7 / 2 is 3 and the 0.5 is thrown away.",
            r"sizeof(char) is always 1, but plain char may be signed or unsigned depending on the compiler.",
        ),
        example=r"""
            int a = 7;
            long long big = 3000000000LL;
            printf("%d %lld %d\n", a / 2, big, a % 2);
        """,
        out=r"3 3000000000 1",
    ),
    *c(
        "fixed-width-integer",
        "Fixed-width integer",
        "An integer type with an exact size, from <stdint.h>: int8_t, uint8_t, int16_t, uint16_t, int32_t, uint32_t, int64_t, uint64_t. The u means unsigned.",
        see=("integer", "unsigned", "integer-promotion", "sizeof"),
        priority=70,
        aka=("fixed width integer", "stdint", "uint8_t", "uint16_t", "uint32_t", "uint64_t", "int8_t", "int16_t", "int32_t", "int64_t", "exact-width integer", "stdint.h"),
        detect=(r"\b(?:u?int(?:8|16|32|64)_t|u?intptr_t|u?intmax_t)\b|<stdint\.h>",),
        rules=(
            r"sizeof(uint8_t) is 1, sizeof(uint16_t) is 2, sizeof(uint32_t) is 4, sizeof(uint64_t) is 8 - on every machine that has them.",
            r"uint8_t holds 0 to 255; int8_t holds -128 to 127; going past the edge wraps for unsigned and is undefined for signed arithmetic.",
            r"Use them for bytes, bit patterns and file or network formats, where the exact size matters.",
            r'Arithmetic on the small ones happens in int (see integer promotion), and printf needs a cast or a matching macro: printf("%u", (unsigned)x).',
        ),
        example=r"""
            uint8_t small = 200;
            int32_t n = -5;
            printf("%d %d %d\n", (int)sizeof(small), (int)sizeof(n), (int)sizeof(uint64_t));
            printf("%u\n", (unsigned)(uint8_t)(small + 100));
        """,
        out=r"""1 4 8
44""",
    ),
    *c(
        "signed-integer",
        "Signed integer",
        "An integer type that can hold negative numbers as well as positive ones: int, long, signed char, int8_t. An ordinary int is signed.",
        see=("unsigned", "twos-complement", "overflow", "integer"),
        priority=50,
        aka=("signed", "signed int", "negative number", "negative integer"),
        detect=(r"\bsigned\b|\bINT(?:8|16|32|64)_(?:MIN|MAX)\b",),
        rules=(
            r"An n-bit signed type holds -2^(n-1) up to 2^(n-1)-1: for 8 bits that is -128 to 127.",
            r"Overflowing a signed type is undefined behaviour (the compiler may assume it never happens); unsigned types wrap instead.",
            r"Plain char may be signed or unsigned depending on the compiler: write signed char or unsigned char when it matters.",
            r"Mixing a signed and an unsigned number in one calculation turns the signed one into unsigned (-1 becomes huge).",
        ),
        example=r"""
            printf("%d %d\n", INT8_MIN, INT8_MAX);
            printf("%d\n", -5 * 2);
        """,
        out=r"""-128 127
-10""",
    ),
    *c(
        "unsigned",
        "Unsigned integer",
        "An integer type that cannot be negative: unsigned int, unsigned char, size_t, uint8_t. When a calculation leaves its range it wraps around, and C guarantees that.",
        see=("overflow", "signed-integer", "twos-complement", "size-t"),
        priority=60,
        aka=("unsigned int", "unsigned char", "unsigned long", "wraparound", "wrap around", "wrap-around", "unsigned integer"),
        detect=(r"\bunsigned\b|\b\d+[uU][lL]{0,2}\b",),
        rules=(
            r"An n-bit unsigned type holds 0 to 2^n - 1: uint8_t is 0 to 255.",
            r"Arithmetic wraps modulo 2^n: 0u - 1 is UINT_MAX, and (uint8_t)(255 + 1) is 0. This is well defined, unlike signed overflow.",
            r"Storing a negative number converts it: unsigned u = -1 makes u the largest value.",
            r"Trap: in -1 < 1u the -1 is converted to unsigned (a huge number), so the answer is 0 (false).",
            r"for (unsigned i = n; i >= 0; i--) never ends: an unsigned i is never below 0.",
        ),
        example=r"""
            unsigned int u = 0;
            u = u - 1;
            uint8_t b = 255;
            b = b + 1;
            printf("%u %u\n", u, (unsigned)b);
            printf("%d\n", -1 < 1u);
        """,
        out=r"""4294967295 0
0""",
    ),
    *c(
        "twos-complement",
        "Two's complement",
        "How computers store negative whole numbers: to negate, flip every bit and add 1. It is why -1 is all ones in binary.",
        see=("signed-integer", "unsigned", "bitwise-operator", "hexadecimal"),
        priority=40,
        aka=("twos complement", "two's complement", "negative binary", "sign bit", "ones complement"),
        detect=(r"\(\s*(?:unsigned|uint\d+_t)[^)\n]{0,12}\)\s*-\s*\d|~\s*\w+\s*\+\s*1\b",),
        rules=(
            r"-x equals ~x + 1: negate by flipping all the bits and adding 1.",
            r"In 8 bits, -1 is 0xFF (255 as unsigned) and -128 is 0x80; the top bit is the sign bit.",
            r"Converting a negative number to an unsigned type gives 2^n + x, so (uint8_t)-1 is 255.",
            r"Before C23 the standard did not insist on it, but every machine you will meet does it this way.",
        ),
        example=r"""
            int x = 5;
            printf("%d %d\n", ~x, -x == ~x + 1);
            printf("%u\n", (unsigned)(uint8_t)-1);
            printf("%02X\n", (unsigned)(uint8_t)-128);
        """,
        out=r"""-6 1
255
80""",
    ),
    *c(
        "integer-promotion",
        "Integer promotion",
        "Before arithmetic, any value smaller than int (char, short, uint8_t) is first widened to int. The calculation happens in int; only storing the result cuts it back down.",
        see=("usual-arithmetic-conversions", "fixed-width-integer", "overflow", "bitwise-operator"),
        priority=40,
        aka=("promotion", "integer promotions", "promoted to int", "integral promotion", "default promotion"),
        detect=(r"\b(?:uint8_t|int8_t|uint16_t|int16_t|short)\s+\w+\s*[=;,]",),
        rules=(
            r"With uint8_t a = 200, b = 100: a + b is 300 (an int), not 44. Only storing it back into a uint8_t gives 44.",
            r"sizeof(a + b) is sizeof(int) for two uint8_t values, never 1.",
            r"~ on a small unsigned value gives a negative int: ~(uint8_t)15 is -16. Cast the result back, (uint8_t)~x, to get 240.",
            r"This is why a char holding 'A' passes through printf's %d as the int 65.",
        ),
        example=r"""
            uint8_t a = 200, b = 100;
            int sum = a + b;
            uint8_t kept = a + b;
            printf("%d %d\n", sum, kept);
            printf("%d\n", sizeof(a + b) == sizeof(int));
        """,
        out=r"""300 44
1""",
    ),
    *c(
        "usual-arithmetic-conversions",
        "Usual arithmetic conversions",
        "The rules that make two different number types match before an operator works on them: both sides become the bigger type, double above float above long above int, and signed becomes unsigned at the same size.",
        see=("integer-promotion", "type-conversion", "cast", "division"),
        priority=40,
        aka=("arithmetic conversions", "mixed types", "mixed arithmetic", "implicit conversion rules", "type promotion"),
        detect=(r"-\s*1\s*[<>]=?\s*\w*[uU]\b|\b\d+[uU]\s*[<>]",),
        rules=(
            r"int + double becomes double: 1 + 0.5 is 1.5.",
            r"The conversion happens per operator and AFTER both sides are worked out: 5 / 2 is integer division (2) even if the result is stored in a double.",
            r"int mixed with unsigned int: the int becomes unsigned, so -1 < 1u is false.",
            r"A cast on one operand, (double)5 / 2, is the way to ask for the fractional answer.",
        ),
        example=r"""
            double d = 5 / 2;
            double e = 5 / 2.0;
            printf("%.1f %.1f %d\n", d, e, -1 < 1u);
        """,
        out=r"2.0 2.5 0",
    ),
    *c(
        "type-conversion",
        "Type conversion",
        "Changing a value from one type to another. C does it silently (implicit conversion) when you mix types in an assignment, call or calculation; a cast does it on purpose.",
        see=("cast", "usual-arithmetic-conversions", "integer-promotion", "floating-point"),
        priority=40,
        aka=("type conversion", "implicit conversion", "coercion", "type coercion", "type casting", "conversion", "implicit cast", "type-cast"),
        detect=(r"\b(?:int|char|short|long)\s+\w+\s*=\s*[-+]?\d+\.\d",),
        rules=(
            r"double to int drops the fraction toward zero: 3.9 becomes 3 and -3.9 becomes -3 (it does not round).",
            r"A value that is too big for a narrower UNSIGNED type wraps; for a narrower SIGNED type the result is implementation-defined.",
            r"int to double is exact for small numbers, and char widens to int without changing its value.",
            r"The compiler warns about some of these with -Wall -Wextra; it does not stop you.",
        ),
        example=r"""
            double x = 3.9;
            int a = x;
            int b = -x;
            char c = 65;
            double d = 7;
            printf("%d %d %c %.1f\n", a, b, c, d);
        """,
        out=r"3 -3 A 7.0",
    ),
    *c(
        "cast",
        "Cast",
        "Writing a type in brackets in front of a value to convert it on purpose: (double)total, (uint8_t)300, (int)3.9.",
        see=("type-conversion", "usual-arithmetic-conversions", "division", "void-pointer"),
        priority=45,
        aka=("casting", "type cast", "typecast", "explicit cast", "explicit conversion"),
        detect=(r"\([ \t]*(?:unsigned[ \t]+)?(?:u?int(?:8|16|32|64)?_t|char|short|int|long|float|double|size_t)[ \t]*\*?[ \t]*\)[ \t]*[\w(&*-]",),
        rules=(
            r"A cast applies to the value right after it, before other operators: (double)7 / 2 is 3.5, but (double)(7 / 2) is 3.0.",
            r"Casting to a narrower unsigned type keeps the low bits: (uint8_t)300 is 44; casting a double to int truncates toward zero.",
            r"A cast makes a new value; the variable itself is not changed.",
            r"Casting a pointer to another pointer type does not change the data, only how it is read.",
        ),
        example=r"""
            int a = 7, b = 2;
            int big = 300;
            printf("%d %.1f %.1f\n", a / b, (double)a / b, (double)(a / b));
            printf("%d\n", (uint8_t)big);
        """,
        out=r"""3 3.5 3.0
44""",
    ),
    *c(
        "overflow",
        "Overflow",
        "A result too big for its type. For unsigned types it wraps around (well defined); for signed types it is undefined behaviour.",
        see=("unsigned", "signed-integer", "undefined-behavior", "integer-limits"),
        priority=60,
        aka=("integer overflow", "signed overflow", "unsigned overflow", "wrap", "wraps", "wrapping", "arithmetic overflow", "underflow"),
        detect=(r"\b(?:INT_MAX|INT_MIN|UINT_MAX|LONG_MAX|SIZE_MAX|U?INT(?:8|16|32|64)_MAX)\b|\b255\s*\+\s*1\b|\b(?:uint8_t|unsigned char)\s+\w+\s*=\s*25[0-5]\b",),
        rules=(
            r"Unsigned wraps: UINT_MAX + 1u is 0, and storing 260 in a uint8_t gives 4 (the value modulo 256).",
            r"Signed overflow, such as INT_MAX + 1, is undefined behaviour: the program may print anything, and the optimiser may remove checks that rely on it.",
            r"Check BEFORE adding: a > INT_MAX - b means a + b would overflow.",
            r"Converting an out-of-range value into a signed type is a different thing (implementation-defined), not arithmetic overflow.",
        ),
        example=r"""
            uint8_t b = 250;
            b += 10;
            unsigned int u = 4294967295u;
            u += 2;
            printf("%u %u\n", (unsigned)b, u);
        """,
        out=r"4 1",
    ),
    *c(
        "division",
        "Division",
        "The / operator. With two integers it throws the remainder away and rounds toward zero (7 / 2 is 3, -7 / 2 is -3); with a floating-point number on either side it gives a fraction.",
        see=("modulo", "cast", "usual-arithmetic-conversions", "floating-point"),
        priority=35,
        aka=("integer division", "integer-division", "divide", "/", "divided by", "truncation", "truncate", "rounds toward zero"),
        detect=(r"[\w)\]][ \t]*/[ \t]*[\w(]",),
        rules=(
            r"Integer division rounds toward ZERO (not down): 7 / 2 is 3, -7 / 2 is -3, 7 / -2 is -3.",
            r"Dividing an integer by zero is undefined behaviour (usually a crash); so is INT_MIN / -1.",
            r"For a fraction make one side floating: 7 / 2.0 is 3.5 and (double)7 / 2 is 3.5, but (double)(7 / 2) is 3.0.",
            r"(a / b) * b + a % b always equals a.",
        ),
        example=r"""
            printf("%d %d %d\n", 7 / 2, -7 / 2, 7 / -2);
            printf("%.2f %.2f\n", 7 / 2.0, 1.0 / 3);
        """,
        out=r"""3 -3 -3
3.50 0.33""",
    ),
    *c(
        "modulo",
        "Modulo",
        "The % operator: the remainder left after integer division. In C its sign follows the left-hand number.",
        see=("division", "operator", "off-by-one"),
        priority=40,
        aka=("remainder", "mod", "%", "modulus", "modulo operator", "remainder operator"),
        detect=(r"[\w)\]][ \t]*%[ \t]*[\w(]",),
        rules=(
            r"7 % 3 is 1, -7 % 3 is -1 (the sign of the left side) and 7 % -3 is 1.",
            r"(a / b) * b + a % b is always a, which is why the sign follows the left side.",
            r"x % 2 == 1 is FALSE for negative odd numbers (-3 % 2 is -1): test x % 2 != 0.",
            r"% works on integers only (use fmod from <math.h> for doubles) and % 0 is undefined behaviour.",
        ),
        example=r"""
            printf("%d %d %d\n", 7 % 3, -7 % 3, 7 % -3);
            printf("%d %d\n", -3 % 2 == 1, -3 % 2 != 0);
        """,
        out=r"""1 -1 1
0 1""",
    ),
    *c(
        "floating-point",
        "Floating point",
        "The number types float and double, which store a fraction as an approximation in binary. Most decimals such as 0.1 cannot be stored exactly.",
        see=("division", "type-conversion", "format-specifier", "precision"),
        priority=35,
        aka=("float", "double", "floating point", "real number", "decimal", "floating-point number", "float precision", "float-precision", "long double"),
        detect=(r"\b(?:float|double)\b|\b\d+\.\d+[fF]?\b",),
        rules=(
            r"double is 64 bits (about 15 digits); float is 32 bits (about 7 digits). A literal 3.14 is a double, 3.14f a float.",
            r"0.1 + 0.2 is not exactly 0.3, so compare with a tolerance, fabs(a - b) < 1e-9, never with ==.",
            r"printf prints both with %f (a float is widened to double for the call); %.2f gives two decimals.",
            r"Dividing by zero gives inf or nan instead of a crash on common machines (not guaranteed by the standard).",
        ),
        example=r"""
            double x = 0.1 + 0.2;
            printf("%d %.17g\n", x == 0.3, x);
        """,
        out=r"0 0.30000000000000004",
    ),
    *c(
        "character",
        "Character",
        "The type char holds one character as a small integer code: 'A' is 65. A character literal uses single quotes; double quotes make a string.",
        see=("ascii", "string", "escape-sequence", "null-terminator"),
        priority=35,
        aka=("char", "chars", "char arithmetic", "char-arithmetic", "character arithmetic", "character literal", "character code", "single character"),
        detect=(r"'_'|\bchar\b",),
        rules=(
            r"In C a character constant has type int, so sizeof('A') is sizeof(int); a char variable holds one byte.",
            r"Characters are numbers: 'a' + 1 is 98, and printing 98 with %c shows b.",
            r"c - '0' turns the digit character '7' into the number 7 (the digits are in order).",
            r"Plain char may be signed or unsigned: keep values above 127 out of it, or use unsigned char.",
        ),
        example=r"""
            char c = 'A';
            printf("%c %d %c\n", c, c, c + 1);
            printf("%d\n", '7' - '0');
        """,
        out=r"""A 65 B
7""",
    ),
    *c(
        "ascii",
        "ASCII",
        "The standard table that gives each character a number: '0' is 48, 'A' is 65, 'a' is 97, space is 32. The digits, capitals and lower-case letters each sit in one unbroken row.",
        see=("character", "string", "character-functions", "bit-mask"),
        priority=45,
        aka=("ascii table", "ascii code", "character code", "char code", "unicode", "utf-8"),
        detect=(r"'_'[ \t]*[-+]|[-+][ \t]*'_'|\b(?:toupper|tolower)\b",),
        rules=(
            r"'0' to '9' are 48 to 57, 'A' to 'Z' are 65 to 90, 'a' to 'z' are 97 to 122.",
            r"A lower-case letter is 32 more than its capital: 'a' - 'A' is 32.",
            r"Characters outside ASCII (like é) take several bytes in UTF-8, so one char is not one letter.",
            r"Comparing letters with < and > compares codes: 'B' < 'a' is true.",
        ),
        example=r"""
            printf("%d %d %d %d\n", '0', 'A', 'a', ' ');
            printf("%c%c\n", 'a' - 32, 'Z' + 32);
        """,
        out=r"""48 65 97 32
Az""",
    ),
    *c(
        "sizeof",
        "sizeof",
        "An operator that gives the size of a type or a variable in bytes, as a size_t. The compiler works it out before the program runs.",
        see=("size-t", "array-decay", "string-length", "struct-padding"),
        priority=70,
        aka=("size of", "sizeof operator", "size in bytes", "byte size"),
        detect=(r"\bsizeof\b",),
        rules=(
            r"sizeof(char) is 1 by definition; sizeof(int) is usually 4 and sizeof(double) 8.",
            r"On an array it gives all the bytes, so the element count is sizeof a / sizeof a[0].",
            r"Inside a function an array parameter is a pointer, so sizeof gives the pointer's size, not the array's.",
            r'sizeof "abc" is 4 because of the terminator; sizeof does not evaluate its operand, so sizeof(i++) leaves i alone.',
        ),
        example=r"""
            int a[5];
            char s[] = "hi";
            printf("%d %d %d\n", (int)sizeof a, (int)(sizeof a / sizeof a[0]), (int)sizeof s);
            printf("%d %d\n", (int)sizeof(char), (int)sizeof(double));
        """,
        out=r"""20 5 3
1 8""",
    ),
    *c(
        "size-t",
        "size_t",
        "The unsigned integer type that sizeof and strlen produce, used for sizes and counts. Print it with %zu.",
        see=("sizeof", "unsigned", "string-length", "format-specifier"),
        priority=60,
        aka=("size_t", "size type", "%zu", "ssize_t", "ptrdiff_t"),
        detect=(r"\bsize_t\b|\bptrdiff_t\b", r"raw:%zu"),
        rules=(
            r"It is unsigned, so 0 - 1 wraps to a huge number: for (size_t i = n - 1; i >= 0; i--) never ends.",
            r"Comparing it with a negative int converts the int to unsigned: -1 becomes huge.",
            r"printf needs %zu for it; %d with a size_t is a format mismatch.",
            r"strlen, sizeof, malloc and memcpy all use it.",
        ),
        example=r"""
            size_t n = strlen("abc");
            size_t zero = 0;
            printf("%zu\n", n);
            printf("%d\n", zero - 1 > 100);
        """,
        out=r"""3
1""",
    ),
    *c(
        "integer-limits",
        "Integer limits",
        "Named constants for the biggest and smallest values of the integer types: INT_MAX, INT_MIN, UINT_MAX from <limits.h>, SIZE_MAX and UINT8_MAX from <stdint.h>, and CHAR_BIT, the bits in a byte.",
        see=("overflow", "signed-integer", "unsigned", "fixed-width-integer"),
        priority=65,
        aka=("limits.h", "int max", "int min", "int_max", "int_min", "uint_max", "char_bit", "limits", "maximum value", "minimum value"),
        detect=(r"\b(?:INT_MAX|INT_MIN|UINT_MAX|LONG_MAX|LONG_MIN|CHAR_BIT|SIZE_MAX|LLONG_MAX|SHRT_MAX|U?INT(?:8|16|32|64)_(?:MAX|MIN))\b|<limits\.h>",),
        rules=(
            r"With a 32-bit int, INT_MAX is 2147483647, INT_MIN is -2147483648 and UINT_MAX is 4294967295.",
            r"INT_MIN is one bigger in size than INT_MAX, so -INT_MIN and abs(INT_MIN) overflow.",
            r"INT_MAX + 1 is undefined behaviour; UINT_MAX + 1u is 0.",
            r"CHAR_BIT is 8 on every machine you will meet.",
        ),
        example=r"""
            #include <limits.h>
            int main(void) {
                printf("%d %d\n", INT_MIN, INT_MAX);
                printf("%u\n", UINT_MAX);
                printf("%d\n", CHAR_BIT);
                return 0;
            }
        """,
        out=r"""-2147483648 2147483647
4294967295
8""",
    ),
    *c(
        "undefined-behavior",
        "Undefined behaviour",
        "Code the C standard gives no meaning to, so the compiler may do anything: crash, print garbage, or seem to work. Signed overflow, reading outside an array and dereferencing NULL are examples.",
        see=("implementation-defined", "overflow", "null-pointer", "sequence-point", "buffer-overflow"),
        priority=55,
        aka=("undefined behavior", "ub", "undefined", "nasal demons", "unspecified behaviour", "unspecified behavior", "undefined behaviour", "runtime error"),
        detect=(r"\bINT_MAX[ \t]*\+|\b1[ \t]*<<[ \t]*(?:3[2-9]|[4-9]\d)\b|/[ \t]*0\b(?!\.)|\[[ \t]*-\d+[ \t]*\]",),
        rules=(
            r"It is not an error message: the program compiles, and may even work today and fail on another machine or with -O2.",
            r"Common causes: signed overflow, an index outside an array, using NULL or a freed pointer, dividing by zero, shifting by the type's width or more, reading an uninitialised variable, changing a variable twice in one expression.",
            r"The optimiser may assume it never happens and remove code that would catch it.",
            r"Find it with the sanitizers: -fsanitize=undefined,address.",
        ),
        example=r"""
            int a = 2147483647;
            if (a > 2147483647 - 1) printf("adding 1 would overflow\n");
            int arr[3] = {1, 2, 3};
            int i = 3;
            if (i < 3) printf("%d\n", arr[i]);
            else printf("index %d is out of range\n", i);
        """,
        out=r"""adding 1 would overflow
index 3 is out of range""",
    ),
    *c(
        "implementation-defined",
        "Implementation-defined",
        "Behaviour the standard leaves to each compiler, which must pick one answer and document it. Unlike undefined behaviour the program still means something, but it may differ between machines.",
        see=("undefined-behavior", "integer", "bit-shift", "signed-integer"),
        priority=30,
        aka=("implementation defined", "implementation-dependent", "platform dependent", "compiler dependent", "portable", "portability", "unspecified"),
        rules=(
            r"Examples: the size of int and long, whether plain char is signed, and what >> does to a negative number (usually it keeps the sign).",
            r"Not the same as undefined: the result is always one valid value, just not the same everywhere.",
            r"Write portable code with fixed-width types (uint32_t) and keep bit tricks on unsigned types.",
        ),
        example=r"""
            printf("%d\n", -8 >> 1);
        """,
        out=r"-4",
    ),
    *c(
        "boolean",
        "Boolean",
        "A yes-or-no value. Classic C has no boolean type: 0 means false and any other number means true, and comparisons give the int 1 or 0. <stdbool.h> adds bool, true and false.",
        see=("comparison", "condition", "short-circuit", "null-pointer"),
        priority=45,
        aka=("bool", "true", "false", "truthy", "falsy", "stdbool", "stdbool.h", "boolean value", "truth value", "true false", "logical value"),
        detect=(r"\b(?:true|false|bool)\b|<stdbool\.h>",),
        rules=(
            r"if (x) means if (x != 0): negative numbers, 0.1 and any non-NULL pointer are true; 0, 0.0, '\0' and NULL are false.",
            r"Comparison and logical operators give exactly 1 or 0, as an int: 5 > 3 is 1, !5 is 0, !!5 is 1.",
            r"bool, true and false need #include <stdbool.h> before C23; true is just 1 and false is 0.",
        ),
        example=r"""
            int a = 5;
            printf("%d %d %d %d\n", a > 3, a == 4, !a, !!a);
            if (-1) printf("negative is true\n");
            if (!0.0) printf("0.0 is false\n");
        """,
        out=r"""1 0 0 1
negative is true
0.0 is false""",
    ),
    *c(
        "comparison",
        "Comparison",
        "Operators that compare two values - == != < <= > >= - and give 1 for true or 0 for false, as an int.",
        see=("boolean", "assignment", "short-circuit", "strcmp"),
        priority=35,
        aka=("equality", "equal", "equals", "relational operator", "comparison operator", "==", "!=", "less than", "greater than", "compare"),
        detect=(r"[\w)\]][ \t]*(?:==|!=|<=|>=)[ \t]*[\w(\-'\"]",),
        rules=(
            r"= stores a value, == compares: if (x = 5) assigns 5 and is always true.",
            r"Chains do not work as in maths: 20 < x < 30 means (20 < x) < 30, a 0 or 1 compared with 30, which is always true. clang refuses to compile it; write x > 20 && x < 30.",
            r"Comparing two strings (char pointers) with == compares ADDRESSES, not text: use strcmp(a, b) == 0.",
            r"Comparing floating-point numbers with == is fragile; mixing signed and unsigned converts the signed one.",
        ),
        example=r"""
            int x = 10;
            int chained = (20 < x) < 30;
            printf("%d %d\n", chained, x == 10);
            if (x = 0) printf("never printed\n");
            printf("%d\n", x);
        """,
        out=r"""1 1
0""",
    ),
    *c(
        "assignment",
        "Assignment",
        "Storing a value in a variable with =. The right side is worked out first. In C an assignment is itself an expression with a value, so a = b = 0 works - and so does the mistake if (a = b).",
        see=("comparison", "increment", "expression", "variable"),
        priority=25,
        aka=("assign", "assigning", "assigned", "compound assignment", "+=", "-=", "*=", "reassign", "reassignment", "=", "assignment operator", "update"),
        detect=(r"\bif[ \t]*\([ \t]*\w+[ \t]*=[ \t]*[^=\s]", r"^\s*\w[\w.\[\]>-]*[ \t]*(?:[-+*/%&|^]|<<|>>)=[ \t]*[^=]"),
        rules=(
            r"x += 2 means x = x + 2; the same idea works for -= *= /= %= &= |= ^= <<= >>=.",
            r"a = b = 7 works right to left: b gets 7, and the value of that assignment (7) goes into a.",
            r"if (a = b) is legal: it assigns, then tests the value. Write if (a == b) - or, if you really mean it, if ((a = b)).",
            r"Arrays cannot be assigned (a = b is an error); copy with memcpy or a loop. Structs can.",
        ),
        example=r"""
            int a, b;
            a = b = 7;
            a += 3;
            int c = (b = 2) + 1;
            printf("%d %d %d\n", a, b, c);
        """,
        out=r"10 2 3",
    ),
    *c(
        "increment",
        "Increment and decrement",
        "++ adds 1 to a variable and -- subtracts 1. After the variable (i++) the expression has the OLD value; before it (++i) it has the NEW value.",
        see=("side-effect", "sequence-point", "assignment", "pointer-arithmetic"),
        priority=40,
        aka=("++", "--", "i++", "++i", "post-increment", "pre-increment", "postfix", "prefix", "decrement", "post increment", "pre increment"),
        detect=(r"\+\+|--",),
        rules=(
            r"int a = i++; stores the old i in a, then adds 1 to i. int b = ++i; adds 1 first and stores the new value.",
            r"As a statement on its own, i++; and ++i; do the same thing.",
            r"*p++ means *(p++): read what p points to, then move p to the next element.",
            r"Never change a variable twice in one expression: i = i++ + ++i is undefined behaviour.",
        ),
        example=r"""
            int i = 5;
            int a = i++;
            int b = ++i;
            printf("%d %d %d\n", a, b, i);
        """,
        out=r"5 7 7",
    ),
    *c(
        "operator",
        "Operator",
        "A symbol that does something to values: + - * / % arithmetic, == < > comparison, && || ! logic, & | ^ ~ << >> bits, = assignment, ? : choice, and & and * for addresses.",
        see=("precedence", "associativity", "expression", "bitwise-operator"),
        priority=20,
        aka=("operators", "operand", "operands", "arithmetic", "plus", "minus", "multiplication", "arithmetic operator", "unary", "binary operator", "unary operator", "addition", "subtraction"),
        detect=(r"[\w)\]][ \t]*[-+*/%][ \t]*[\w(]",),
        rules=(
            r"Arithmetic: + - * / %. Comparison: == != < > <= >=. Logic: && || !. Bits: & | ^ ~ << >>.",
            r"Unary operators take one operand: -x, !x, ~x, *p, &x, sizeof x, ++i. Binary ones take two. ?: takes three.",
            r"The same symbol can mean two things: & is bitwise AND between values and address-of before one; * is multiply or dereference.",
        ),
        example=r"""
            printf("%d %d %d\n", 7 + 3 * 2, 7 % 4, 7 > 3 && 2 > 1);
        """,
        out=r"13 3 1",
    ),
    *c(
        "expression",
        "Expression",
        "A piece of code that works out to a value: 2 + 3, a variable's name, a call f(x), a[i], x > 3 ? 1 : 2. Add a semicolon and it is a statement.",
        see=("operator", "side-effect", "precedence", "assignment"),
        priority=20,
        aka=("expressions", "expr", "evaluate", "evaluation", "value of an expression", "statement", "lvalue", "rvalue"),
        rules=(
            r"Every expression has a type and (usually) a value; an assignment is an expression too: its value is the stored value.",
            r"An expression followed by ; is a statement. x + 1; is legal but does nothing (the compiler warns).",
            r"In if and while, the expression is the condition: 0 is false and anything else is true.",
        ),
        example=r"""
            int x = 4;
            int y = (x = 9) * 2;
            printf("%d %d\n", x, y);
        """,
        out=r"9 18",
    ),
    *c(
        "precedence",
        "Operator precedence",
        "The order the operators in one expression are done in. Higher precedence goes first: that is why 2 + 3 * 4 is 14, and why a & 2 == 2 does not test a bit.",
        see=("associativity", "operator", "bitwise-operator", "short-circuit"),
        priority=65,
        aka=("order of operations", "operator precedence", "pemdas", "bodmas", "binding", "binds tighter", "parentheses", "brackets order"),
        detect=(
            r"[\w)\]][ \t]*[-+][ \t]*[\w.()\[\]]{1,20}[ \t]*[*/%][ \t]*[\w(]",
            r"[\w)\]][ \t]*[*/%][ \t]*[\w.()\[\]]{1,20}[ \t]*[-+][ \t]*[\w(]",
            r"&&[^\n;]{0,60}\|\||\|\|[^\n;]{0,60}&&",
            r"[\w)\]][ \t]*(?<![&])&(?![&=])[ \t]*[\w)\]]{1,20}[ \t]*(?:==|!=)",
            r"[\w)\]][ \t]*[-+][ \t]*\w{1,20}[ \t]*(?:<<|>>)",
        ),
        rules=(
            r"From first to last: x++ x-- () [] . -> | ! ~ ++x -x *p &x sizeof casts | * / % | + - | << >> | < <= > >= | == != | & | ^ | | | && | || | ?: | = += etc. | comma.",
            r"Trap: == binds tighter than & | ^, so a & 2 == 2 is a & (2 == 2). Write (a & 2) == 2.",
            r"Trap: + - bind tighter than << >>, so 1 + 2 << 3 is (1 + 2) << 3 = 24.",
            r"&& goes before ||. Unary operators bind tighter than binary ones: *p + 1 is (*p) + 1. When unsure, add brackets.",
        ),
        example=r"""
            int a = 6;
            printf("%d\n", a & 2 == 2);
            printf("%d\n", (a & 2) == 2);
            printf("%d %d\n", 2 + 3 * 4, 8 - 3 - 2);
            printf("%d\n", 1 + 2 << 3);
        """,
        out=r"""0
1
14 3
24""",
    ),
    *c(
        "associativity",
        "Associativity",
        "When two operators of the same precedence meet, associativity says which goes first. Most go left to right (8 - 3 - 2 is 3); assignment, ?: and the unary operators go right to left.",
        see=("precedence", "ternary", "assignment", "operator"),
        priority=45,
        aka=("left to right", "right to left", "left-associative", "right-associative", "grouping", "evaluation direction"),
        detect=(r"[\w)\]][ \t]*-[ \t]*\w{1,12}[ \t]*-[ \t]*\w|[\w)\]][ \t]*/[ \t]*\w{1,12}[ \t]*/[ \t]*\w|\w[ \t]*=[ \t]*\w{1,12}[ \t]*=[ \t]*[^=]",),
        rules=(
            r"Left to right: 8 - 3 - 2 is (8 - 3) - 2 = 3, and 100 / 10 / 5 is (100 / 10) / 5 = 2.",
            r"Right to left: a = b = c = 4 sets c first; and 0 ? 1 : 0 ? 2 : 3 is 0 ? 1 : (0 ? 2 : 3).",
            r"Associativity decides grouping, not the order operands are evaluated in (see evaluation order).",
        ),
        example=r"""
            int a, b, c;
            printf("%d %d\n", 8 - 3 - 2, 100 / 10 / 5);
            a = b = c = 4;
            printf("%d %d %d\n", a, b, c);
            printf("%d\n", 0 ? 1 : 0 ? 2 : 3);
        """,
        out=r"""3 2
4 4 4
3""",
    ),
    *c(
        "short-circuit",
        "Short-circuit evaluation",
        "&& and || stop as soon as the answer is known: a && b skips b when a is false, and a || b skips b when a is true. Anything b would have done does not happen.",
        see=("boolean", "side-effect", "ternary", "comparison"),
        priority=55,
        aka=("short circuit", "short-circuiting", "lazy evaluation", "logical and", "logical or", "&&", "||", "logical operator", "logical operators", "and or"),
        detect=(r"&&|\|\|",),
        rules=(
            r"The left side is always evaluated first, and && and || are sequence points, so the order is guaranteed.",
            r"p != NULL && *p > 0 is safe: the dereference only happens when p is not NULL.",
            r"The result is 1 or 0 (an int), not one of the operands.",
            r"& and | are the bit operators and do NOT short-circuit.",
        ),
        example=r"""
            int n = 0;
            int r = (1 > 2) && (++n > 0);
            int s = (2 > 1) || (++n > 0);
            printf("%d %d %d\n", r, s, n);
        """,
        out=r"0 1 0",
    ),
    *c(
        "ternary",
        "Conditional operator",
        "condition ? a : b - the one operator with three parts. It gives a if the condition is true and b otherwise, and only the chosen part is evaluated.",
        see=("short-circuit", "associativity", "condition", "expression"),
        priority=55,
        aka=("ternary operator", "ternary", "conditional expression", "?:", "question mark", "inline if", "conditional operator"),
        detect=(r"\?[^\n;:?]{0,60}:",),
        rules=(
            r"It is an expression, so it can sit inside printf or an initialiser: int m = n > 5 ? 1 : 0;",
            r"Nested choices group to the right: a ? b : c ? d : e is a ? b : (c ? d : e).",
            r"Its precedence is low, just above assignment: wrap it in brackets inside bigger expressions.",
            r"Both choices are converted to a common type (usual arithmetic conversions).",
        ),
        example=r"""
            int n = 7;
            printf("%s\n", n % 2 == 0 ? "even" : "odd");
            int m = n > 5 ? n > 9 ? 2 : 1 : 0;
            printf("%d\n", m);
        """,
        out=r"""odd
1""",
    ),
    *c(
        "comma-operator",
        "Comma operator",
        "a, b works out a, throws its value away, then works out b and gives b's value. It has the lowest precedence of all operators.",
        see=("sequence-point", "for-loop", "side-effect", "operator"),
        priority=55,
        aka=("comma", "comma operator", "comma expression", "sequence operator"),
        detect=(
            r"\bfor[ \t]*\([ \t]*[A-Za-z_]\w*[ \t]*=[^;,)\n]{1,30},[ \t]*[A-Za-z_]\w*[ \t]*=",
            r"=[ \t]*\([^()\n;]{1,30},[^()\n;]{1,30}\)[ \t]*;",
        ),
        rules=(
            r"int x = (1, 2, 3); makes x 3: only the last value is kept.",
            r"The commas that separate function arguments and declared variables are NOT the operator: f(a, b) passes two values.",
            r"Its everyday use is a for loop with two counters: for (i = 0, j = 5; i < j; i++, j--).",
            r"A comma is a sequence point: everything left of it is finished before the right side starts.",
        ),
        example=r"""
            int x = (1, 2, 3);
            int i, j;
            for (i = 0, j = 5; i < j; i++, j--) {}
            printf("%d %d %d\n", x, i, j);
        """,
        out=r"3 3 2",
    ),
    *c(
        "side-effect",
        "Side effect",
        "Anything an expression does besides producing a value: changing a variable (i++, x = 5), printing, or calling a function that changes something.",
        see=("sequence-point", "short-circuit", "increment", "evaluation-order"),
        priority=50,
        aka=("side effects", "side-effects", "has side effect", "mutation", "state change", "pure function"),
        detect=(r"(?:\+\+|--)[^;\n]{0,40}(?:\+\+|--)",),
        rules=(
            r"i++, assignment, compound assignment and function calls have side effects; a plain a + b has none.",
            r"&&, || and ?: may skip an operand entirely, so a side effect inside the skipped part never happens.",
            r"sizeof does not evaluate its operand: sizeof(i++) leaves i unchanged.",
            r"Changing a variable twice, or changing it and reading it, in one expression is undefined behaviour.",
        ),
        example=r"""
            int i = 1;
            int size = (int)sizeof(i++);
            int n = 0;
            if (0 && n++) {}
            printf("%d %d %d\n", i, n, size);
        """,
        out=r"1 0 4",
    ),
    *c(
        "sequence-point",
        "Sequence point",
        "A moment where every earlier side effect is finished before anything later starts: the end of a statement (;), and after &&, ||, ?: and the comma operator. Between two of them a variable may be changed only once.",
        see=("evaluation-order", "side-effect", "undefined-behavior", "increment"),
        priority=50,
        aka=("sequence points", "sequenced before", "unsequenced", "sequencing", "sequenced"),
        detect=(
            r"\b(\w+)[ \t]*=[ \t]*\1[ \t]*(?:\+\+|--)",
            r"\b(\w+)[ \t]*(?:\+\+|--)[^;\n)]{0,30}\b\1\b",
            r"\b(\w+)\b[^;\n)]{0,30}\b\1[ \t]*(?:\+\+|--)",
        ),
        rules=(
            r"i = i++ + 1 and a[i] = i++ change i twice (or read it while it changes) with no sequence point between: undefined behaviour.",
            r"Fix it by splitting into statements: the semicolon is a sequence point.",
            r"Guaranteed: the end of a full statement, the operators && || ?: and the comma, and just before a function is called.",
        ),
        example=r"""
            int i = 5;
            int x = i++;
            int y = i + 1;
            printf("%d %d %d\n", x, y, i);
        """,
        out=r"5 7 6",
    ),
    *c(
        "evaluation-order",
        "Evaluation order",
        "The order the parts of an expression are worked out. C mostly does not say: the operands of + and the arguments of a function call may be evaluated in any order. Only && || ?: and the comma are left to right.",
        see=("sequence-point", "side-effect", "short-circuit", "associativity"),
        priority=55,
        aka=("order of evaluation", "argument order", "unspecified order", "evaluated first", "left to right evaluation", "unspecified behavior"),
        detect=(
            r"\b\w+[ \t]*\([^;\n()]{0,60}(?:\w(?:\+\+|--)|(?:\+\+|--)\w)[^;\n()]{0,60},[^;\n()]{0,60}(?:\w(?:\+\+|--)|(?:\+\+|--)\w)",
            r"\b\w+[ \t]*\([^;\n()]{0,60}\b(\w+)\b[^;\n()]{0,40},[^;\n()]{0,40}\b\1(?:\+\+|--)",
        ),
        rules=(
            r'In f(a(), b()) either call may happen first; printf("%d %d", i++, i++) is not safe to rely on.',
            r"Do the dependent steps in separate statements; that fixes the order.",
            r"&&, || and ?: always evaluate the left operand first, and skip the right one when they can.",
        ),
        example=r"""
            int i = 0;
            int ok = (i++ == 0) && (i++ == 1);
            printf("%d %d\n", ok, i);
        """,
        out=r"1 2",
    ),
    *c(
        "bitwise-operator",
        "Bitwise operators",
        "& | ^ ~ work on every bit of a number separately: & keeps bits set in both, | keeps bits set in either, ^ keeps bits that differ, ~ flips every bit.",
        see=("bit-shift", "bit-mask", "precedence", "hexadecimal"),
        priority=60,
        aka=("bitwise", "bitwise and", "bitwise or", "xor", "bitwise xor", "bitwise not", "bit operation", "bit operations", "bitwise operators", "bit manipulation", "bit twiddling", "and or xor", "&", "|", "^", "~", "bit-wise"),
        detect=(r"[\w)\]][ \t]*(?:(?<!&)&(?![&=])|(?<!\|)\|(?![|=])|\^(?!=))[ \t]*[\w(~]|~[ \t]*[\w(]|[&|^]=",),
        rules=(
            r"12 & 10 is 8 (1100 & 1010 = 1000), 12 | 10 is 14, 12 ^ 10 is 6.",
            r"Not the same as && ||: 1 & 2 is 0 but 1 && 2 is 1.",
            r"^ is XOR, not a power: 2 ^ 3 is 1.",
            r"~x flips all the bits of the (promoted) int: ~0 is -1, and ~x equals -x - 1 for signed numbers.",
            r"They bind LOOSER than == and <: a & 1 == 0 means a & (1 == 0). Use brackets.",
        ),
        example=r"""
            unsigned a = 12, b = 10;
            printf("%u %u %u %u\n", a & b, a | b, a ^ b, ~a & 15u);
            printf("%d %d %d\n", 1 & 2, 1 && 2, 2 ^ 3);
        """,
        out=r"""8 14 6 3
0 1 1""",
    ),
    *c(
        "bit-shift",
        "Bit shift",
        "x << n slides the bits of x left by n places (like multiplying by 2^n); x >> n slides them right (like dividing by 2^n). Empty places fill with zeros.",
        see=("bitwise-operator", "bit-mask", "unsigned", "undefined-behavior"),
        priority=65,
        aka=("shift", "shifts", "shift left", "shift right", "left shift", "right shift", "<<", ">>", "bitshift", "shifting"),
        detect=(r"<<|>>",),
        rules=(
            r"5 << 1 is 10 and 5 << 3 is 40; 40 >> 2 is 10. Shifting right drops the bits that fall off.",
            r"Shifting by a negative amount, or by the width of the type or more (1 << 32 on a 32-bit int), is undefined behaviour.",
            r"Use unsigned for bit work: 1 << 31 on a signed int is undefined, 1u << 31 is 2147483648.",
            r"Right-shifting a negative signed number is implementation-defined (usually it keeps the sign bit).",
        ),
        example=r"""
            unsigned x = 5;
            printf("%u %u %u\n", x << 1, x << 3, 40u >> 2);
            printf("%u\n", 1u << 31);
        """,
        out=r"""10 40 10
2147483648""",
    ),
    *c(
        "bit-mask",
        "Bit mask",
        "A number used with & | ^ to pick out, set, clear or flip chosen bits of another number. 1u << n builds a mask with only bit n set.",
        see=("bitwise-operator", "bit-shift", "hexadecimal", "unsigned"),
        priority=60,
        aka=("mask", "masking", "bit flag", "bit flags", "flags", "set a bit", "clear a bit", "toggle a bit", "test a bit", "bitmask", "bit field"),
        detect=(r"&[ \t]*\(?[ \t]*(?:0[xX][0-9a-fA-F]+|\d+u?|~\w+|1u?[ \t]*<<)|\|=[ \t]*\(?[ \t]*1u?[ \t]*<<|&=[ \t]*~",),
        rules=(
            r"Test bit n: (x >> n) & 1, or x & (1u << n). Set it: x |= 1u << n. Clear it: x &= ~(1u << n). Flip it: x ^= 1u << n.",
            r"The lowest k bits as a mask: (1u << k) - 1; 0xFF keeps one byte.",
            r"Do bit work on unsigned types, so the sign bit does not get in the way.",
            r"Bracket the mask expression: x & mask == 0 means x & (mask == 0).",
        ),
        example=r"""
            unsigned flags = 0;
            flags |= 1u << 3;
            flags |= 1u << 0;
            flags &= ~(1u << 0);
            flags ^= 1u << 5;
            printf("%u %d %u\n", flags, (flags >> 3) & 1, (1u << 4) - 1);
        """,
        out=r"40 1 15",
    ),
    *c(
        "binary",
        "Binary",
        "Base 2, written with only the digits 0 and 1. Every bit is a power of two: 1010 is 8 + 2 = 10. Standard C has no binary literal (0b101 is an extension, standard from C23), so people write hex.",
        see=("hexadecimal", "bitwise-operator", "bit-shift", "twos-complement"),
        priority=35,
        aka=("base 2", "binary number", "binary digits", "bits", "bit", "bit pattern", "0b", "binary representation"),
        detect=(r"\b0[bB][01]+\b",),
        rules=(
            r"8 bits make one byte and hold 0 to 255; each hex digit is exactly 4 bits (0xF is 1111).",
            r"There is no %b in classic printf: print bits with a loop that tests (x >> i) & 1.",
            r"Reading 1010: 1*8 + 0*4 + 1*2 + 0*1 = 10.",
        ),
        example=r"""
            uint8_t x = 0xA5;
            for (int i = 7; i >= 0; i--) putchar(((x >> i) & 1) ? '1' : '0');
            putchar('\n');
        """,
        out=r"10100101",
    ),
    *c(
        "hexadecimal",
        "Hexadecimal",
        "Base 16, written with the digits 0-9 and a-f. In C a constant starts with 0x (0xFF is 255) and printf shows it with %x, %X or %02X.",
        see=("binary", "bit-mask", "format-specifier", "octal"),
        priority=45,
        aka=("hex", "base 16", "0x", "%x", "hexadecimal number", "hex digit", "hex digits", "%X"),
        detect=(r"\b0[xX][0-9a-fA-F]+\b", r"raw:%#?0?\d*l{0,2}[xX]"),
        rules=(
            r"0x10 is 16 and 0xFF is 255; each hex digit stands for 4 bits, so a byte is exactly two hex digits.",
            r"%x prints lower-case digits, %X upper-case, %#x adds the 0x, %04x pads with zeros to width 4.",
            r"%x expects an unsigned int: pass a negative int and you get its two's-complement bit pattern.",
        ),
        example=r"""
            int n = 255;
            printf("%x %X %#x %04x\n", n, n, n, n);
            printf("%d\n", 0x1F);
        """,
        out=r"""ff FF 0xff 00ff
31""",
    ),
    *c(
        "octal",
        "Octal",
        "Base 8. In C a number written with a leading 0 is octal: 010 is 8, not 10. Print one with %o.",
        see=("hexadecimal", "binary", "escape-sequence", "integer"),
        priority=50,
        aka=("base 8", "leading zero", "octal number", "%o", "octal literal"),
        detect=(r"(?<![\w.])0[0-7]+\b(?!\.)",),
        rules=(
            r"010 is 8, 017 is 15 and 0777 is 511: a leading zero changes the meaning of the number.",
            r"08 and 09 do not compile (8 and 9 are not octal digits).",
            r"Do not pad numbers with zeros in source code: write 7, not 007. Octal also appears in escapes: '\101' is 'A'.",
        ),
        example=r"""
            printf("%d %d %o\n", 010, 017, 8);
        """,
        out=r"8 15 10",
    ),
    *c(
        "variable",
        "Variable",
        "A named place in memory that holds a value of one type. int count = 3; creates a variable called count, ready to be used and changed.",
        see=("initialization", "assignment", "scope", "constant"),
        priority=30,
        aka=("variables", "name", "identifier", "declaration", "declare", "declaring", "naming", "var", "define a variable", "definition"),
        detect=(r"^[ \t]*(?:(?:const|static|unsigned|signed|long|short)[ \t]+)*(?:int|char|float|double|size_t|u?int\d+_t)[ \t]+\**[A-Za-z_]\w*[ \t]*[=;,\[]",),
        rules=(
            r"Declare every variable with its type before using it; the type never changes.",
            r"Names use letters, digits and _, cannot start with a digit, and are case-sensitive (total and Total differ); keywords cannot be names.",
            r"A local variable that is not initialised holds garbage: reading it is undefined behaviour.",
        ),
        example=r"""
            int count = 3;
            double ratio = 0.5;
            count = count + 1;
            printf("%d %.1f\n", count, ratio);
        """,
        out=r"4 0.5",
    ),
    *c(
        "initialization",
        "Initialization",
        "Giving a variable its first value as it is created. A local variable that is not initialised holds garbage; globals and static variables start at zero. A partly filled array is completed with zeros.",
        see=("variable", "array", "designated-initializer", "static-variable"),
        priority=45,
        aka=("initialize", "initialise", "initialisation", "initializer", "initialiser", "initialized", "uninitialized", "uninitialised", "array initialization", "initializing", "init", "= {0}", "zero initialize", "zero-initialization", "zero initialization", "zeroing"),
        detect=(
            r"\w[ \t]*\[[ \t]*\w*[ \t]*\][ \t]*=[ \t]*\{",
            r"=[ \t]*\{[ \t]*0[ \t]*\}",
            r"^[ \t]*(?:int|char|double|float|long)[ \t]+\w+[ \t]*;",
        ),
        rules=(
            r"int a[5] = {1, 2}; gives 1 2 0 0 0: the missing elements are zero.",
            r"int z[3] = {0}; sets every element to zero (so does = {0} on a struct).",
            r'int a[] = {1, 2, 3}; takes its size, 3, from the list; char name[8] = "Ann"; zero-fills the rest.',
            r"A local int x; has an indeterminate value; a global or static one is 0.",
        ),
        example=r"""
            int a[5] = {1, 2};
            int z[3] = {0};
            char name[8] = "Ann";
            printf("%d %d %d %d %d | %d | %d\n", a[0], a[1], a[2], a[3], a[4], z[2], name[5]);
        """,
        out=r"1 2 0 0 0 | 0 | 0",
    ),
    *c(
        "constant",
        "Constant (const)",
        "A value that must not change. const int limit = 3; makes the compiler refuse any assignment to limit; #define LIMIT 3 is the older text-substitution way.",
        see=("const-pointer", "macro", "variable", "volatile"),
        priority=50,
        aka=("const", "constants", "constant variable", "read-only", "readonly", "const qualifier", "magic number", "literal constant"),
        detect=(r"\bconst\b|^[ \t]*#[ \t]*define[ \t]+[A-Z_][A-Z0-9_]*[ \t]+[-\w(\"']",),
        rules=(
            r"Assigning to a const variable is a compile error; changing it through a cast pointer is undefined behaviour.",
            r"const char *p means the characters cannot be changed through p; char *const p means p itself cannot move (see const pointer).",
            r"A #define constant has no type and no memory: it is replaced by its text; a const variable is a real typed variable.",
            r"Parameters declared const (const char *s) promise the function will not modify the data.",
        ),
        example=r"""
            const int limit = 3;
            int total = 0;
            for (int i = 0; i < limit; i++) total += i;
            printf("%d\n", total);
        """,
        out=r"3",
    ),
    *c(
        "volatile",
        "volatile",
        "A promise-breaker for the optimiser: a volatile variable may change by something outside the program's own flow (hardware, a signal handler), so every read must really read memory.",
        see=("constant", "variable", "undefined-behavior"),
        priority=70,
        aka=("volatile qualifier", "volatile keyword", "memory-mapped", "hardware register"),
        detect=(r"\bvolatile\b",),
        rules=(
            r"Without volatile, the compiler may keep a value in a register and read it only once.",
            r"volatile does not make operations atomic and is not a thread tool; it matters for hardware registers and signal handlers.",
            r"It cannot be used to make a race condition safe.",
        ),
        example=r"""
            volatile int sensor = 7;
            int a = sensor;
            int b = sensor;
            printf("%d\n", a + b);
        """,
        out=r"14",
    ),
]
