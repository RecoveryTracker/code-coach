"""Gotchas, C, second deck: the standard library, the preprocessor and the conversions that bite.

Same rules as content_c.py, and the same oracle (tests/test_gotchas_c.py builds every card with clang, gcc and Visual
Studio, at -O0/-O2, with char forced signed and unsigned, and under the sanitizers): portable and well defined, one
printed line, fixed-width types where the width matters, and nothing the language leaves to the implementation.
This file is the library and preprocessor side: printf's width and precision, strtol, qsort and bsearch, memmove,
strncpy, #if, macro expansion, compound literals, and the promotions and conversions around them.
"""

from __future__ import annotations

from .items import Item, make

q = make("c")

ITEMS: tuple[Item, ...] = (
    # ── Batch 1: the library and the preprocessor ──────────────────────────
    q("putchar-returns-the-char", r'''
        #include <stdio.h>

        int main(void) {
            printf(" %d\n", putchar('A'));
        }
    ''', "A 65", ["65 A", "A 1", "A A"],
      "putchar returns the character it wrote, and it runs before printf does",
      """The argument `putchar('A')` is evaluated first: it prints `A` and returns 65 (the character as an
      int). Only then does printf print its space and that 65."""),

    q("strncmp-counts-characters", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            const char *a = "apple pie";
            printf("%d %d %d\n", strncmp(a, "apple", 5) == 0,
                   strncmp(a, "apple", 6) > 0, strcmp(a, "apple") < 0);
        }
    ''', "1 1 0", ["1 0 0", "1 1 1", "0 1 0"],
      "strncmp looks at n characters at most, and the terminator counts as one",
      """The first five characters match. At position 5 the string has a space and "apple" has its
      terminator (0), so the space is the bigger one: `> 0` is true, and `strcmp(...) < 0` is false."""),

    q("memcmp-does-not-stop-at-nul", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            const char *a = "ab\0x";
            const char *b = "ab\0y";
            printf("%d %d\n", strcmp(a, b) == 0, memcmp(a, b, 4) < 0);
        }
    ''', "1 1", ["1 0", "0 1", "0 0"],
      "strcmp stops at the first 0 byte; memcmp compares exactly n bytes",
      """To strcmp both strings are just "ab", so they are equal. memcmp is given 4 bytes and walks
      straight past the 0 to the `x` and `y`, which differ, so it reports a negative number."""),

    q("bsearch-gives-a-pointer", r'''
        #include <stdio.h>
        #include <stdlib.h>

        static int cmp(const void *a, const void *b) {
            return *(const int *)a - *(const int *)b;
        }

        int main(void) {
            int v[] = {2, 4, 6, 8, 10};
            int hit = 8, miss = 5;
            int *p = bsearch(&hit, v, 5, sizeof v[0], cmp);
            int *q = bsearch(&miss, v, 5, sizeof v[0], cmp);
            printf("%d %d\n", (int)(p - v), q == NULL);
        }
    ''', "3 1", ["8 1", "3 0", "4 1"],
      "bsearch returns a pointer to the element, or NULL, never an index",
      """A hit points at v[3], so subtracting the array start gives index 3 (not the value 8, and not
      a 1-based position). A miss gives a null pointer, which is why `q == NULL` is 1."""),

    q("compound-literal-sizeof-and-lifetime", r'''
        #include <stdio.h>

        struct P { int x, y; };

        static int sum(const struct P *p) { return p->x + p->y; }

        int main(void) {
            int total = 0;
            for (int i = 0; i < 3; i++)
                total += sum(&(struct P){i, i * 10});
            printf("%d %d\n", total, (int)sizeof((int[]){1, 2, 3}));
        }
    ''', "33 12", ["33 3", "33 8", "0 12"],
      "A compound literal is a real, addressable object, and sizeof sees the whole array",
      """`(struct P){i, i * 10}` makes a fresh unnamed object on each pass, so 0 + 11 + 22 adds up to
      33. `(int[]){1, 2, 3}` is an array of three ints, so sizeof gives 12, not a pointer size."""),

    q("printf-star-width", r'''
        #include <stdio.h>

        int main(void) {
            printf("[%*d] [%-*d] [%.*s]\n", 5, 42, 4, 7, 3, "abcdef");
        }
    ''', "[   42] [7   ] [abc]", ["[42 ] [ 7] [abc]", "[42] [7] [abcdef]", "[ 42] [7 ] [def]"],
      "A * in a format takes its number from the arguments, just before the value",
      """`%*d` reads the width 5 and then the value 42, giving `   42`. A `-` flag left-aligns, so
      `%-*d` pads 7 on the right to 4 wide. `%.*s` takes the precision 3, so only `abc` is printed."""),

    q("printf-integer-precision", r'''
        #include <stdio.h>

        int main(void) {
            printf("[%.3d] [%5.3d] [%.0d] [%.3s]\n", 7, 7, 0, "abcdef");
        }
    ''', "[007] [  007] [] [abc]", ["[7] [    7] [0] [abc]", "[007] [00007] [0] [abc]",
                                   "[007] [  007] [0] [abcdef]"],
      "For an integer, the precision is the minimum number of digits, and 0 with .0 is nothing",
      """`%.3d` pads with zeros to three digits; the width 5 then pads that with spaces. A precision of
      0 printing the value 0 produces no characters at all. Only for `%s` does it mean a cut-off."""),

    q("strtol-stops-where", r'''
        #include <stdio.h>
        #include <stdlib.h>

        int main(void) {
            char s[] = "0x1Fzz";
            char *end;
            long a = strtol(s, &end, 16);
            int ea = (int)(end - s);
            long b = strtol(s, &end, 10);
            printf("%ld@%d %ld@%d\n", a, ea, b, (int)(end - s));
        }
    ''', "31@4 0@1", ["31@6 0@1", "31@4 0@0", "31@2 0@1"],
      "strtol uses as much of the text as the base allows and leaves the pointer after it",
      """In base 16 an optional `0x` is accepted and `1F` is 31, ending at index 4 (the first `z`). In
      base 10, `0` is a number and the `x` is not a digit, so it stops at index 1 with the value 0."""),

    q("if-treats-an-unknown-name-as-zero", r'''
        #include <stdio.h>

        #define LEVEL 2

        int main(void) {
        #if LEVEL > 1 && DEBUG
            puts("verbose");
        #elif LEVEL > 1 && !DEBUG
            puts("quiet");
        #else
            puts("off");
        #endif
        }
    ''', "quiet", ["verbose", "off", "(nothing)"],
      "In #if, a name that is not a macro is quietly replaced by 0",
      """`DEBUG` was never defined, so the preprocessor reads it as 0 and the first test is false. The
      `#elif` then sees `2 > 1 && !0`, which is true, so the second `puts` is the one that is kept."""),

    q("object-macro-without-parentheses", r'''
        #include <stdio.h>

        #define WIDTH 3 + 4

        int main(void) {
            printf("%d %d\n", WIDTH * 2, 28 / WIDTH);
        }
    ''', "11 13", ["14 4", "14 13", "11 4"],
      "A macro is pasted in as text, so an unbracketed sum does not stay a unit",
      """`WIDTH * 2` becomes `3 + 4 * 2`, which is 11, and `28 / WIDTH` becomes `28 / 3 + 4`, which
      is 9 + 4 = 13. Write `#define WIDTH (3 + 4)` to get 14 and 4."""),

    # ── Batch 2 ────────────────────────────────────────────────────────────
    q("memmove-overlap", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char s[] = "abcdef";
            memmove(s + 2, s, 4);
            printf("%s\n", s);
        }
    ''', "ababcd", ["ababab", "abcdef", "cdefef"],
      "memmove copies as if through a temporary, so overlapping ranges are safe",
      """The four bytes `abcd` are copied to start at index 2, giving `ab` + `abcd`. A byte-by-byte
      forward copy would have smeared `ab` over itself (`ababab`); memcpy is not allowed to overlap."""),

    q("strncpy-pads-or-truncates", r'''
        #include <stdio.h>
        #include <string.h>

        static void put(char *to, const char *from, size_t n) {
            strncpy(to, from, n);
        }

        int main(void) {
            char a[8] = "XXXXXXX";
            char b[8] = "XXXXXXX";
            put(a, "abcdef", 3);
            put(b, "hi", 5);
            printf("%s %s %d %c\n", a, b, b[4], b[5]);
        }
    ''', "abcXXXX hi 0 X", ["abc hi 0 X", "abcXXXX hiXXX 0 X", "abcXXXX hi X X"],
      "strncpy cuts without a terminator, and pads a short source with zeros up to n",
      """Copying 3 of 6 characters writes `abc` and no 0, so the old X's behind it are still part of
      the string. Copying "hi" with n = 5 writes `h`, `i` and three 0 bytes, so b[4] is 0 and b[5] is
      untouched."""),

    q("flexible-array-member-sizeof", r'''
        #include <stdio.h>

        struct Buf {
            int n;
            int data[];
        };

        int main(void) {
            int need = (int)sizeof(struct Buf) + 3 * (int)sizeof(int);
            printf("%d %d\n", (int)sizeof(struct Buf), need);
        }
    ''', "4 16", ["8 20", "4 4", "16 16"],
      "A flexible array member adds nothing to sizeof; you add its room yourself",
      """`int data[]` has no size, so the struct is just the `int n`: 4 bytes. The usual idiom is
      `sizeof(struct Buf) + count * sizeof(int)` for the allocation: 4 + 12 = 16."""),

    q("promotion-hides-the-wrap", r'''
        #include <stdio.h>
        #include <stdint.h>

        int main(void) {
            uint16_t a = 50000, b = 20000;
            printf("%d %d\n", a + b > 65535, (uint16_t)(a + b) > 65535);
        }
    ''', "1 0", ["0 0", "1 1", "0 1"],
      "Small types are promoted to int before the sum, so only the cast wraps it",
      """`a + b` is computed as an int, 70000, and that is above 65535. Casting the sum back to
      uint16_t wraps it to 4464, which can never be above 65535, so the second test is always 0."""),

    q("wider-signed-type-wins", r'''
        #include <stdio.h>
        #include <stdint.h>

        int main(void) {
            int64_t s = -1;
            int32_t t = -1;
            printf("%d %d\n", s < (uint32_t)1, t < (uint64_t)1);
        }
    ''', "1 0", ["0 0", "1 1", "0 1"],
      "A signed value is converted to the unsigned type only when that type is not narrower",
      """A 64-bit signed type can hold every uint32_t, so `-1 < 1` is evaluated as signed: true. A
      32-bit int against a uint64_t is turned into a uint64_t, so -1 becomes a huge number: false."""),

    q("ternary-picks-one-common-type", r'''
        #include <stdio.h>

        int main(void) {
            printf("%d %d\n", (1 ? -1 : 0u) > 0, (int)sizeof(1 ? 1 : 2.0));
        }
    ''', "1 8", ["0 4", "0 8", "1 4"],
      "Both branches of ?: are converted to one type, whichever branch is taken",
      """Mixing int and unsigned makes the whole conditional unsigned, so the taken `-1` becomes a huge
      number and is greater than 0. Mixing int and double makes it a double, 8 bytes, even for `1`."""),

    q("continue-inside-a-switch", r'''
        #include <stdio.h>

        int main(void) {
            int n = 0;
            for (int i = 0; i < 5; i++) {
                switch (i % 3) {
                case 0: continue;
                case 1: n += 10; break;
                default: n += 1;
                }
                n += 100;
            }
            printf("%d\n", n);
        }
    ''', "321", ["331", "230", "421"],
      "break leaves only the switch, but continue goes on to the next loop iteration",
      """i = 0 and 3 hit `continue` and skip the `+= 100`. i = 1 and 4 add 10 then `break` out of the
      switch and add 100 (110 each). i = 2 adds 1 then 100. Total 1 x 101 + 2 x 110 = 321."""),

    q("work-after-the-recursive-call", r'''
        #include <stdio.h>

        static void walk(int n) {
            if (n == 0) return;
            printf("%d", n);
            walk(n - 1);
            printf("%d", n);
        }

        int main(void) {
            walk(3);
            printf("\n");
        }
    ''', "321123", ["321", "123321", "123"],
      "Code after the recursive call runs on the way back out, in reverse order",
      """Going in, 3, 2 and 1 are printed. At n = 0 the calls start returning, and each frame
      then prints its own n again: 1, 2, 3."""),

    q("enum-takes-any-int", r'''
        #include <stdio.h>

        enum Dir { N, E, S, W };

        int main(void) {
            enum Dir d = W;
            d = (enum Dir)(d + 1);
            printf("%d %d %d\n", d, d == N, d > W);
        }
    ''', "4 0 1", ["0 1 0", "4 0 0", "3 0 0"],
      "An enum variable is just an integer: it does not wrap or complain at the end of the list",
      """`W + 1` is 4, which is not one of the named values, and C stores it as it is. It does not wrap
      round to N, so `d == N` is 0 and `d > W` is 1."""),

    q("macro-body-expands-at-the-use", r'''
        #include <stdio.h>

        #define X 1
        #define Y (X + X)
        #undef X
        #define X 10

        int main(void) {
            printf("%d\n", Y);
        }
    ''', "20", ["2", "11", "10"],
      "A macro's replacement text is expanded where it is used, not where it was defined",
      """`Y` only stores the tokens `(X + X)`. When `Y` is used in main, X has meanwhile been redefined
      as 10, so the text becomes `(10 + 10)`."""),

    # ── Batch 3 ────────────────────────────────────────────────────────────
    q("negative-converts-before-dividing", r'''
        #include <stdio.h>
        #include <stdint.h>

        int main(void) {
            int32_t n = -7;
            printf("%lu %d\n", (unsigned long)(n / 2u), n / 2);
        }
    ''', "2147483644 -3", ["-3 -3", "2147483644 -4", "3 -3"],
      "With an unsigned operand the negative is converted first, and only then divided",
      """In `n / 2u` the int -7 becomes the unsigned number 4294967289, and half of that is
      2147483644. The plain `n / 2` stays signed and is cut toward zero, giving -3."""),

    q("percent-g-trims", r'''
        #include <stdio.h>

        int main(void) {
            printf("%g %g %g %g\n", 2.50, 100.0, 3.14159265, 0.1 + 0.2);
        }
    ''', "2.5 100 3.14159 0.3",
    ["2.5 100 3.14159265 0.3", "2.500000 100.000000 3.141593 0.300000", "2.5 100 3.14159 0.30000000000000004"],
      "%g keeps six significant digits and drops trailing zeros",
      """Unlike `%f`, `%g` does not print a fixed number of decimals: it rounds to 6 significant
      digits and removes the zeros at the end. That is also why 0.1 + 0.2 shows up as a tidy 0.3."""),

    q("static-buffer-is-shared", r'''
        #include <stdio.h>

        static char *tag(int n) {
            static char buf[16];
            sprintf(buf, "<%d>", n);
            return buf;
        }

        int main(void) {
            char *a = tag(1);
            char *b = tag(2);
            printf("%s %s\n", a, b);
        }
    ''', "<2> <2>", ["<1> <2>", "<1> <1>", "<2> <1>"],
      "A function that returns its static buffer hands everyone the same buffer",
      """Both calls return the address of the same `buf`. The second call overwrote what the first
      wrote, so `a` and `b` point at the same text, `<2>`."""),

    q("lowest-set-bit", r'''
        #include <stdio.h>

        int main(void) {
            unsigned x = 12;
            printf("%u %u %u\n", x & -x, x & (x - 1), x & ~(x - 1));
        }
    ''', "4 8 4", ["12 8 4", "8 4 8", "4 4 4"],
      "x & -x isolates the lowest set bit; x & (x - 1) clears it",
      """12 is binary 1100. `-x` on an unsigned wraps around, so `x & -x` leaves just the lowest 1 bit:
      4. `x & (x - 1)` removes that bit and leaves 8, and `x & ~(x - 1)` is the lowest bit again."""),

    q("rotate-left-by-shifts", r'''
        #include <stdio.h>
        #include <stdint.h>

        int main(void) {
            uint32_t x = 0x12345678u;
            uint32_t r = (x << 8) | (x >> 24);
            printf("%08lX\n", (unsigned long)r);
        }
    ''', "34567812", ["78123456", "78563412", "56781234"],
      "A left rotate is a left shift ORed with the bits that fell off, shifted the other way",
      """`x << 8` drops the top byte 12 and puts zeros at the bottom: 34567800. `x >> 24` leaves just
      that top byte, 00000012, and ORing the two puts it back at the bottom: 34567812."""),

    q("for-with-two-counters", r'''
        #include <stdio.h>

        int main(void) {
            int i, j;
            for (i = 0, j = 10; i < j; i += 3, j -= 3) {
            }
            printf("%d %d\n", i, j);
        }
    ''', "6 4", ["3 7", "9 1", "6 7"],
      "Both counters step together, and the loop ends after the step that crosses",
      """The pairs are (0, 10), (3, 7), (6, 4). At (6, 4) the test `i < j` fails, but both variables
      have already been stepped, so that is what is printed."""),

    q("strspn-counts-a-prefix", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            const char *s = "abcab,de";
            printf("%d %d %d\n", (int)strspn(s, "ab"), (int)strcspn(s, ","),
                   (int)strspn(s, "xyz"));
        }
    ''', "2 5 0", ["4 5 0", "2 6 0", "2 3 0"],
      "strspn measures the opening run of allowed characters, not every allowed character",
      """`strspn(s, "ab")` stops at the `c`, so it is 2 even though more a's and b's follow.
      `strcspn(s, ",")` is the index of the first comma, 5, and the first letter is not in "xyz", so 0."""),

    q("strchr-finds-the-terminator", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            const char *s = "a/b/c.txt";
            printf("%s %s %d\n", strrchr(s, '/') + 1, strchr(s, '/') + 1,
                   (int)(strchr(s, '\0') - s));
        }
    ''', "c.txt b/c.txt 9", ["b/c.txt c.txt 9", "c.txt b/c.txt 8", "c.txt c.txt 9"],
      "strrchr finds the last match, strchr the first, and searching for 0 finds the end",
      """`strrchr` looks from the right, so it finds the last slash and `+ 1` is `c.txt`. `strchr`
      finds the first slash. Searching for '\\0' finds the terminator, 9 bytes in, which is the length."""),

    q("sscanf-counts-conversions", r'''
        #include <stdio.h>

        int main(void) {
            int a = -1, b = -1;
            int n = sscanf("12 abc", "%d %d", &a, &b);
            printf("%d %d %d\n", n, a, b);
        }
    ''', "1 12 -1", ["2 12 0", "1 12 0", "0 -1 -1"],
      "sscanf returns how many values it stored, and stops at the first mismatch",
      """`%d` reads 12 into a. For the second `%d` the text is `abc`, which is not a number, so scanning
      stops, b is left alone at -1, and the return value is 1."""),

    q("array-size-from-the-initialiser", r'''
        #include <stdio.h>

        struct P { int x, y; };

        int main(void) {
            struct P pts[] = {{1, 2}, {3, 4}, {5}};
            int n = (int)(sizeof pts / sizeof pts[0]);
            printf("%d %d %d\n", n, pts[2].x, pts[2].y);
        }
    ''', "3 5 0", ["2 5 0", "3 5 5", "3 0 5"],
      "The array gets one element per initialiser, and missing members are zero",
      """Three brace groups give three elements, so sizeof divides to 3. The last group `{5}` sets only
      `x`; the members it does not mention are set to 0."""),

    # ── Batch 4 ────────────────────────────────────────────────────────────
    q("same-precedence-runs-left-to-right", r'''
        #include <stdio.h>

        int main(void) {
            printf("%d %d %d\n", 10 - 4 - 3, 100 / 10 / 5, 2 * 3 % 4);
        }
    ''', "3 2 2", ["9 50 6", "3 2 6", "3 50 2"],
      "Operators of equal rank group from the left: (10 - 4) - 3",
      """`-`, `/`, `*` and `%` all associate left to right, so these are `(10 - 4) - 3`, `(100 / 10) / 5`
      and `(2 * 3) % 4`: 3, 2 and 2. Only assignment and the conditional group from the right."""),

    q("sizeof-is-unsigned", r'''
        #include <stdio.h>

        int main(void) {
            int n = -1;
            printf("%d %d\n", sizeof(int) > n, (long long)sizeof(int) > n);
        }
    ''', "0 1", ["1 1", "0 0", "1 0"],
      "sizeof is an unsigned number, so comparing it with a negative int goes wrong",
      """`sizeof(int) > n` turns n into a size_t, so -1 becomes the largest possible value and 4 is not
      greater. Casting the sizeof to a signed type first keeps the comparison honest."""),

    q("floor-ceil-round-trunc", r'''
        #include <stdio.h>
        #include <math.h>

        int main(void) {
            printf("%.0f %.0f %.0f %.0f\n", floor(-2.5), ceil(-2.5), round(-2.5),
                   trunc(-2.5));
        }
    ''', "-3 -2 -3 -2", ["-3 -2 -2 -2", "-2 -3 -3 -2", "-3 -2 -3 -3"],
      "On negatives, floor goes down, trunc goes toward zero and round goes away from zero",
      """floor(-2.5) is -3 and ceil(-2.5) is -2. trunc just drops the fraction (-2). round sends halves
      away from zero, so -2.5 becomes -3, not -2."""),

    q("qsort-only-sorts-its-range", r'''
        #include <stdio.h>
        #include <stdlib.h>

        static int up(const void *a, const void *b) {
            int x = *(const int *)a, y = *(const int *)b;
            return (x > y) - (x < y);
        }

        int main(void) {
            int v[] = {9, 5, 3, 7, 1};
            qsort(v + 1, 3, sizeof v[0], up);
            for (int i = 0; i < 5; i++) printf("%d ", v[i]);
            printf("\n");
        }
    ''', "9 3 5 7 1", ["1 3 5 7 9", "9 7 5 3 1", "9 5 3 7 1"],
      "qsort sorts exactly the count of elements you give it, from the pointer you give it",
      """`v + 1` with a count of 3 covers {5, 3, 7} only. That slice becomes {3, 5, 7}, and the 9 in
      front and the 1 at the end are never touched."""),

    q("unary-minus-promotes-first", r'''
        #include <stdio.h>
        #include <stdint.h>

        int main(void) {
            uint8_t u = 5;
            printf("%d %d %d\n", -u, (uint8_t)-u, -u < 0);
        }
    ''', "-5 251 1", ["251 251 0", "-5 5 1", "-5 251 0"],
      "A small unsigned type is promoted to int before the minus, so it really goes negative",
      """`u` becomes an int, so `-u` is -5 and `-u < 0` is true. Only the cast back to uint8_t wraps
      it, to 256 - 5 = 251."""),

    q("octal-escapes-take-three-digits", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            printf("%s %d %d\n", "\1012", (int)strlen("ab\0007"),
                   (int)sizeof "ab\0007");
        }
    ''', "A2 2 5", ["A2 2 4", "A2 4 5", "A2 5 5"],
      "An octal escape reads up to three digits, so the next digit is an ordinary character",
      """`\\101` is 'A' (65), and the `2` after it is just a 2. In "ab\\0007" the escape is `\\000`, a
      zero byte, followed by a `7`: strlen stops at the zero (2), but the array holds a, b, 0, 7 and
      the final 0, so sizeof is 5."""),

    q("compound-assignment-converts-back", r'''
        #include <stdio.h>

        int main(void) {
            int x = 10;
            x += 0.9;
            int a = x;
            x *= 1.5;
            int b = x;
            x -= 0.5;
            printf("%d %d %d\n", a, b, x);
        }
    ''', "10 15 14", ["11 16 16", "10 15 15", "10.9 16.35 15.85"],
      "x op= y computes in double, then truncates the result back into the int",
      """`x += 0.9` is 10.9, which is stored as 10. Then 10 * 1.5 is 15, and finally 15 - 0.5 is 14.5,
      which is cut to 14. The variable stays an int, and each step truncates toward zero."""),

    q("multiply-then-widen", r'''
        #include <stdio.h>
        #include <stdint.h>

        int main(void) {
            uint32_t a = 100000, b = 100000;
            uint64_t early = a * b;
            uint64_t late = (uint64_t)a * b;
            printf("%llu %llu\n", (unsigned long long)early,
                   (unsigned long long)late);
        }
    ''', "1410065408 10000000000",
    ["10000000000 10000000000", "1410065408 1410065408", "10000000000 1410065408"],
      "The product is computed in the operands' own type; storing it in a wider one is too late",
      """`a * b` is a 32-bit multiplication, and 10 billion wraps modulo 2^32 to 1410065408 before it
      is stored. Casting one operand to uint64_t first makes the whole multiplication 64-bit."""),

    q("divide-then-multiply", r'''
        #include <stdio.h>

        int main(void) {
            printf("%d %d\n", 3 / 4 * 100, 3 * 100 / 4);
        }
    ''', "0 75", ["75 75", "0 0", "75 0"],
      "Integer division loses the remainder at once, so the order of * and / matters",
      """`3 / 4 * 100` is `(3 / 4) * 100`, and 3 / 4 is already 0. Multiplying first, `(3 * 100) / 4`,
      divides 300 by 4 and gives 75."""),

    q("reverse-loop-with-unsigned", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            const char *s = "abc";
            for (size_t i = strlen(s); i-- > 0;)
                putchar(s[i]);
            putchar('\n');
        }
    ''', "cba", ["cb", "abc", "(loops forever)"],
      "`i-- > 0` tests the old value and then decrements, so unsigned never goes below 0",
      """The test sees i = 3, 2, 1, 0 and the body runs with the decremented values 2, 1, 0. When the
      test sees 0 it fails, though i then wraps to a huge value, which nothing uses any more."""),
)
