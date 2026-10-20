"""Gotchas, C: the "what will it print?" traps, compiled and run for real.

Same rules as the other content modules, plus the ones C needs. The oracle (tests/test_gotchas_c.py) compiles every
card and holds the marked answer to what it printed, then does it again on every compiler installed (clang, gcc,
Visual Studio) and at -O0 and -O2 and with char forced signed and unsigned, and the output must be the same
everywhere: a card whose answer depends on the machine does not belong here.

So every card is portable C and well defined: no signed overflow, no out-of-bounds or uninitialised reads, no
variable modified twice without a sequence point, no `sizeof(long)`, no padding sizes, no plain `char` signedness,
no right shift of a negative, nothing about the order function arguments are evaluated in, no `%p`. Fixed-width
`<stdint.h>` types are welcome, the printf of an `unsigned long` is cast, and the answer is always one line.
About a third are easy-looking on purpose, and the rest are medium and hard.
"""

from __future__ import annotations

from .items import Item, make

q = make("c")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: basics a beginner can get, with a real trap ──────────
    q("int-division", r'''
        #include <stdio.h>

        int main(void) {
            printf("%d %d %d\n", 7 / 2, -7 / 2, 7 / -2);
        }
    ''', "3 -3 -3", ["3 -4 -4", "4 -4 -4", "3.5 -3.5 -3.5"],
      "Integer division throws the fraction away, toward zero",
      """Both operands are ints, so the result is an int. Since C99 the quotient is cut toward zero, which
      makes -7 / 2 equal -3, not -4."""),

    q("modulo-negative", r'''
        #include <stdio.h>

        int main(void) {
            printf("%d %d %d\n", 7 % 3, -7 % 3, 7 % -3);
        }
    ''', "1 -1 1", ["1 2 -2", "1 -1 -1", "1 2 1"],
      "The sign of % follows the left operand",
      """Since C99, a / b is cut toward zero and a % b is whatever makes (a / b) * b + a % b equal a. So
      -7 % 3 is -1 and 7 % -3 is 1; unlike Python, it is never "wrapped" to be positive."""),

    q("float-vs-int-division", r'''
        #include <stdio.h>

        int main(void) {
            double d = 5 / 2;
            printf("%.1f %.1f %.1f\n", d, 5 / 2.0, (double)(5 / 2));
        }
    ''', "2.0 2.5 2.0", ["2.5 2.5 2.5", "2.0 2.5 2.5", "2.5 2.5 2.0"],
      "The division happens before the conversion to double",
      """`5 / 2` is two ints, so it is 2 before it ever reaches the double. Only `5 / 2.0` has a double
      operand, and a cast placed around the whole division is too late."""),

    q("char-arithmetic", r'''
        #include <stdio.h>

        int main(void) {
            char c = 'a' + 1;
            printf("%c %d %c\n", c, c, 'A' + 2);
        }
    ''', "b 98 C", ["b 97 C", "b 98 67", "98 b C"],
      "A char is a small integer, and %c or %d decide how it is shown",
      """`'a' + 1` is the number 98, which as a char is 'b'. The same number printed with %d is 98, and
      `'A' + 2` is 67, which %c shows as 'C'."""),

    q("printf-flags", r'''
        #include <stdio.h>

        int main(void) {
            printf("%d%%|%c|%.2s|%03d|%+.1f|%#x\n", 50, 65, "abcdef", 7, 2.0, 255);
        }
    ''', "50%|A|ab|007|+2.0|0xff",
      ["50%|65|ab|007|+2.0|0xff", "50%|A|abcdef|7|2.0|ff", "50|A|ab|007|+2.0|0xff"],
      "Each printf conversion has its own meaning: %% is a percent sign, %c a character code",
      """`%%` prints one percent sign, `%c` turns 65 into 'A', and `%.2s` stops after two characters. `%03d`
      pads with zeros, `%+.1f` always shows the sign, and `%#x` adds the 0x prefix."""),

    q("strlen-vs-sizeof", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char s[] = "hello";
            printf("%zu %zu\n", strlen(s), sizeof(s));
        }
    ''', "5 6", ["5 5", "6 6", "6 5"],
      "sizeof counts the hidden terminating zero; strlen does not",
      """The array holds 'h', 'e', 'l', 'l', 'o' and a final '\\0', so it is 6 bytes. `strlen` walks
      the text and stops at the zero without counting it."""),

    q("partial-array-init", r'''
        #include <stdio.h>

        int main(void) {
            int a[5] = {1, 2};
            printf("%zu %d %d\n", sizeof a / sizeof a[0], a[1], a[4]);
        }
    ''', "5 2 0", ["2 2 0", "5 2 garbage", "5 0 0"],
      "An array with fewer initialisers keeps its size and zero-fills the rest",
      """The size comes from the declaration, 5, not from how many values you wrote. Every element without
      an initialiser is set to zero, so `a[4]` is 0, not leftover memory."""),

    q("post-pre-increment", r'''
        #include <stdio.h>

        int main(void) {
            int i = 5;
            int a = i++;
            int b = ++i;
            printf("%d %d %d\n", a, b, i);
        }
    ''', "5 7 7", ["6 7 7", "5 6 7", "5 7 6"],
      "i++ gives the old value, ++i gives the new one",
      """`i++` hands over 5 and then raises i to 6. `++i` raises i to 7 first and hands over 7, so
      a is 5, b is 7 and i ends at 7."""),

    q("dangling-else", r'''
        #include <stdio.h>

        int main(void) {
            int x = 1, y = 0;
            if (x)
                if (y) printf("A");
            else printf("B");
            printf("\n");
        }
    ''', "B", ["nothing", "A", "AB"],
      "An else belongs to the nearest if, whatever the indentation says",
      """The else pairs with `if (y)`, not with `if (x)`. Since x is true and y is false, the inner
      else runs and prints B. The indentation is only decoration."""),

    q("switch-fallthrough", r'''
        #include <stdio.h>

        int main(void) {
            int n = 2;
            switch (n) {
            case 1: printf("a");
            case 2: printf("b");
            case 3: printf("c"); break;
            default: printf("d");
            }
            printf("\n");
        }
    ''', "bc", ["b", "bcd", "abc"],
      "Without break, a switch keeps running into the next case",
      """It jumps to `case 2`, prints b, and with no break carries on into `case 3` to print c, where the
      break finally stops it. It never reaches `default`."""),

    q("for-loop-exit-value", r'''
        #include <stdio.h>

        int main(void) {
            int i, n = 0;
            for (i = 0; i < 10; i += 3) n++;
            printf("%d %d\n", i, n);
        }
    ''', "12 4", ["9 4", "12 3", "9 3"],
      "After a for loop, the variable holds the first value that failed the test",
      """The body runs for i = 0, 3, 6 and 9, which is 4 times. Then i becomes 12, the test fails, and
      the loop ends with i left at 12."""),

    q("post-increment-in-condition", r'''
        #include <stdio.h>

        int main(void) {
            int i = 0;
            while (1) {
                if (i++ >= 3) break;
            }
            printf("%d\n", i);
        }
    ''', "4", ["3", "5", "2"],
      "The increment in i++ still happens on the pass that breaks",
      """On the pass where i is 3 the test `3 >= 3` is true, but i++ has already raised i to 4. The break
      then leaves the loop with i at 4."""),

    q("ternary-nesting", r'''
        #include <stdio.h>

        int main(void) {
            int a = 3, b = 7;
            printf("%d %d\n", a > b ? a : b, a < b ? a > 1 ? 10 : 20 : 30);
        }
    ''', "7 10", ["3 10", "7 20", "7 30"],
      "Read a nested ?: from the left: the middle part is its own whole ?:",
      """The first one picks the larger of 3 and 7, which is 7. In the second, `a < b` is true, so the
      value is the inner `a > 1 ? 10 : 20`, which is 10."""),

    q("short-circuit", r'''
        #include <stdio.h>

        int main(void) {
            int x = 0, y = 0;
            int r = (x != 0 && 10 / x > 1);
            int s = (1 || ++y);
            printf("%d %d %d\n", r, s, y);
        }
    ''', "0 1 0", ["0 1 1", "1 1 0", "0 0 0"],
      "&& and || stop as soon as the answer is known, skipping the rest",
      """`x != 0` is false, so the division by zero on its right never runs. `1 || ++y` is already true,
      so `++y` is skipped too and y stays 0."""),

    q("assign-in-condition", r'''
        #include <stdio.h>

        int main(void) {
            int x = 5;
            if (x = 0) printf("zero");
            else printf("nonzero");
            printf(" %d\n", x);
        }
    ''', "nonzero 0", ["zero 0", "nonzero 5", "zero 5"],
      "A single = in an if is an assignment, and its value is the condition",
      """`x = 0` stores 0 in x, and the value of the whole expression is that 0, which counts as false.
      So the else branch runs, and x is now 0."""),

    q("semicolon-after-for", r'''
        #include <stdio.h>

        int main(void) {
            int n = 0;
            for (int i = 0; i < 4; i++);
                n++;
            printf("%d\n", n);
        }
    ''', "1", ["4", "3", "0"],
      "A stray ; after a for makes the loop body empty",
      """The semicolon is the whole loop body, so the loop just counts i up to 4 and does nothing. The
      `n++` on the next line is an ordinary statement that runs once."""),

    q("semicolon-after-if", r'''
        #include <stdio.h>

        int main(void) {
            int x = 3;
            if (x > 5);
            printf("big");
            printf(" done\n");
        }
    ''', "big done", ["done", "big", "bigdone"],
      "if (cond); runs an empty statement; the next line always runs",
      """The `;` right after the condition is the whole body of the if. The two printf calls are separate
      statements after it, so both of them run no matter what x is."""),

    q("macro-square", r'''
        #include <stdio.h>
        #define SQUARE(x) x * x

        int main(void) {
            printf("%d\n", SQUARE(1 + 2));
        }
    ''', "5", ["9", "7", "3"],
      "A macro pastes text; it does not add brackets for you",
      """`SQUARE(1 + 2)` becomes `1 + 2 * 1 + 2`, and the multiplication goes first: 1 + 2 + 2 is 5. Writing
      `((x) * (x))` in the macro fixes it."""),

    q("sizeof-char-literal", r'''
        #include <stdio.h>

        int main(void) {
            char c = 'x';
            printf("%zu %zu %d\n", sizeof(char), sizeof c,
                   sizeof('x') == sizeof(int));
        }
    ''', "1 1 1", ["1 1 0", "1 4 1", "4 4 1"],
      "In C a character literal like 'x' has type int, not char",
      """`sizeof(char)` is always 1, and so is the size of the variable c. But the literal `'x'` is an
      int in C, so its size equals `sizeof(int)`. (In C++ it would be a char, and this would print 1 1 0.)"""),

    q("uint8-wraps", r'''
        #include <stdio.h>
        #include <stdint.h>

        int main(void) {
            uint8_t a = 200, b = 100;
            uint8_t c = a + b;
            int d = a + b;
            printf("%d %d\n", c, d);
        }
    ''', "44 300", ["300 300", "44 44", "255 300"],
      "Small types are promoted to int for the sum; only storing it back wraps",
      """`a + b` is computed as an int, 300. Storing that in a `uint8_t` keeps only the low 8 bits, 300
      minus 256 = 44, while the int d holds the full 300."""),

    q("signed-unsigned-compare", r'''
        #include <stdio.h>

        int main(void) {
            unsigned u = 3;
            int i = -1;
            printf("%d %d\n", i < u, i < 0);
        }
    ''', "0 1", ["1 1", "0 0", "1 0"],
      "Comparing a signed int with an unsigned converts the int to unsigned",
      """In `i < u`, the -1 is converted to the largest unsigned value, which is bigger than 3, so the
      test is false. `i < 0` compares two ints and is true."""),

    q("float-division-printing", r'''
        #include <stdio.h>

        int main(void) {
            int a = 7, b = 2;
            float f = a / b;
            double g = (double)a / b;
            printf("%.2f %.2f %.2f\n", f, g, a / (double)b * 2);
        }
    ''', "3.00 3.50 7.00", ["3.50 3.50 7.00", "3.00 3.00 6.00", "3.50 3.50 3.50"],
      "A float variable does not rescue an integer division",
      """`a / b` is an int division, 3, and only then stored as 3.00. Casting one operand to double first
      gives 3.5, and `7 / 2.0 * 2` is 7.0."""),

    q("float-equality", r'''
        #include <stdio.h>

        int main(void) {
            double a = 0.1 + 0.2;
            printf("%d %d %.1f %.17g\n", a == 0.3, a > 0.3, a, a);
        }
    ''', "0 1 0.3 0.30000000000000004",
      ["1 0 0.3 0.3", "0 0 0.3 0.30000000000000004", "0 1 0.3 0.3"],
      "0.1 and 0.2 are not stored exactly, so the sum is not exactly 0.3",
      """Binary floating point cannot hold 0.1 or 0.2 exactly, so the sum lands a hair above 0.3. That is
      why == fails, and why `%.1f` still rounds it to 0.3 on screen."""),

    q("const-pointers", r'''
        #include <stdio.h>

        int main(void) {
            int a = 1, b = 2;
            int *const p = &a;
            const int *q = &a;
            q = &b;
            *p = 9;
            printf("%d %d %d\n", a, *q, b);
        }
    ''', "9 2 2", ["1 2 2", "9 1 2", "9 9 2"],
      "const on the left guards the value; const after the * guards the pointer",
      """`int *const p` is a fixed pointer to a changeable int, so `*p = 9` sets a. `const int *q` is a
      changeable pointer to a read-only int, so moving q to b is fine."""),

    q("static-local", r'''
        #include <stdio.h>

        int counted(void) { static int n = 0; n++; return n; }
        int fresh(void) { int n = 0; n++; return n; }

        int main(void) {
            int x = counted(), y = counted();
            int p = fresh(), q = fresh();
            printf("%d %d %d %d\n", x, y, p, q);
        }
    ''', "1 2 1 1", ["1 1 1 1", "1 2 1 2", "2 3 1 1"],
      "A static local keeps its value between calls; an ordinary local starts over",
      """The `static int n = 0` is set up once and survives, so it counts 1 then 2. The ordinary local is
      a new 0 on every call, so `fresh()` always returns 1."""),

    q("array-name-compare", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char a[] = "cat", b[] = "cat";
            printf("%d %d\n", a == b, strcmp(a, b) == 0);
        }
    ''', "0 1", ["1 1", "0 0", "1 0"],
      "== on two arrays compares their addresses, not their contents",
      """Each array is its own object at its own address, so `a == b` is false. `strcmp` compares the
      characters and returns 0 for equal text, which is what makes the second test true."""),

    q("array-dimensions", r'''
        #include <stdio.h>

        int main(void) {
            int g[2][3] = {{1, 2, 3}, {4, 5, 6}};
            printf("%zu %zu %zu\n", sizeof g / sizeof g[0],
                   sizeof g[0] / sizeof g[0][0], sizeof g / sizeof g[0][0]);
        }
    ''', "2 3 6", ["3 2 6", "2 3 3", "6 3 2"],
      "g[0] is a whole row; dividing sizes gives rows, columns and total",
      """`sizeof g` is the whole table, `sizeof g[0]` is one row of 3 ints, and `sizeof g[0][0]` is one
      int. So there are 2 rows, 3 columns and 6 ints in all."""),

    q("pointer-arithmetic", r'''
        #include <stdio.h>

        int main(void) {
            int a[] = {10, 20, 30, 40};
            int *p = a + 1;
            printf("%d %d %d %td\n", *p, *(p + 2), p[-1], (a + 3) - p);
        }
    ''', "20 40 10 2", ["10 30 20 2", "20 30 10 3", "20 40 20 2"],
      "Pointer arithmetic counts elements, not bytes, and indexing can go backwards",
      """`p` points at a[1], which is 20. `p + 2` is a[3] = 40, `p[-1]` is a[0] = 10, and the distance from
      p to `a + 3` is 2 elements."""),

    q("comma-operator", r'''
        #include <stdio.h>

        int main(void) {
            int i = 0, j;
            j = (i += 2, i * 10);
            printf("%d %d\n", i, j);
        }
    ''', "2 20", ["0 20", "2 10", "2 0"],
      "The comma operator runs the left part, then gives the value of the right part",
      """`i += 2` runs first and makes i 2. The whole bracket then has the value of `i * 10`, which is
      20, and that is what j receives."""),

    q("bitand-precedence", r'''
        #include <stdio.h>

        int main(void) {
            int f = 6;
            if (f & 2 == 2) puts("yes");
            else puts("no");
        }
    ''', "no", ["yes", "6", "2"],
      "== binds tighter than &, so the mask is applied to the wrong thing",
      """`f & 2 == 2` is `f & (2 == 2)`, which is `6 & 1` and that is 0. Write `(f & 2) == 2` to test the
      bit as intended."""),

    q("unsigned-bit-ops", r'''
        #include <stdio.h>

        int main(void) {
            unsigned a = 12, b = 10;
            printf("%u %u %u %u %u\n", a & b, a | b, a ^ b, a << 2, a >> 2);
        }
    ''', "8 14 6 48 3", ["8 14 6 24 6", "8 14 2 48 3", "12 14 6 48 3"],
      "Shifts multiply and divide by powers of two; & | ^ work on each bit",
      """12 is 1100 and 10 is 1010. AND gives 1000 (8), OR gives 1110 (14), XOR gives 0110 (6). Shifting
      left by 2 multiplies by 4 (48) and shifting right by 2 divides by 4 (3)."""),

    q("not-on-small-type", r'''
        #include <stdio.h>
        #include <stdint.h>

        int main(void) {
            uint8_t x = 0x0F;
            printf("%d %d\n", ~x, (uint8_t)~x);
        }
    ''', "-16 240", ["240 240", "-16 -16", "-15 240"],
      "~ works on the promoted int, so the result is negative until you cast it back",
      """x is promoted to an int 15 first, and flipping every bit of an int gives -16. Converting that back
      to `uint8_t` keeps the low 8 bits, 0xF0, which is 240."""),

    q("unsigned-char-loop", r'''
        #include <stdio.h>

        int main(void) {
            unsigned char c = 250;
            for (int i = 0; i < 10; i++) c++;
            printf("%d\n", c);
        }
    ''', "4", ["260", "0", "255"],
      "An unsigned char wraps around at 256",
      """250 plus 10 is 260, but the variable only holds 0 to 255, so it wraps to 260 minus 256 = 4."""),

    q("digit-char-math", r'''
        #include <stdio.h>

        int main(void) {
            char c = '7';
            int n = c - '0';
            printf("%d %d %c\n", n, c, n + '0');
        }
    ''', "7 55 7", ["55 7 7", "7 7 55", "7 55 55"],
      "A digit character is a code, not the number it shows",
      """`'7'` is the character code 55. Subtracting `'0'` (48) gives the number 7, and adding `'0'` back
      turns 7 into the character '7' for %c."""),

    q("string-pointer-offsets", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            const char *s = "hello";
            printf("%c %s %zu\n", s[1], s + 3, strlen(s + 1));
        }
    ''', "e lo 4", ["h hello 5", "e llo 4", "e lo 5"],
      "s + n is the same text starting n characters later",
      """`s[1]` is 'e'. `s + 3` is a string that starts at the second 'l', so it reads "lo". `s + 1` is
      "ello", which has 4 characters."""),

    q("printf-return-value", r'''
        #include <stdio.h>

        int main(void) {
            int n = printf("hey");
            printf(" %d\n", n);
        }
    ''', "hey 3", ["hey 0", "hey 4", "hey"],
      "printf returns how many characters it printed",
      """The first call prints "hey" and returns 3, which is stored in n. The second call then prints a
      space and that 3."""),

    q("array-decay-in-call", r'''
        #include <stdio.h>

        void change(int a[], int n) { a[0] = 99; n = 0; }

        int main(void) {
            int x[3] = {1, 2, 3};
            int n = 3;
            change(x, n);
            printf("%d %d\n", x[0], n);
        }
    ''', "99 3", ["1 3", "99 0", "1 0"],
      "An array is passed as a pointer; a plain int is passed as a copy",
      """The function receives the address of `x`, so `a[0] = 99` changes the real array. `n` arrives as a
      copy, so setting it to 0 inside has no effect on the caller's n."""),

    q("struct-copy-pointer", r'''
        #include <stdio.h>

        struct P { int x; };

        int main(void) {
            struct P a = {1};
            struct P b = a;
            struct P *c = &a;
            b.x = 2;
            c->x = 3;
            printf("%d %d %d\n", a.x, b.x, c->x);
        }
    ''', "3 2 3", ["1 2 3", "3 3 3", "1 2 1"],
      "Assigning a struct copies it; a pointer to it still sees the original",
      """`b = a` makes an independent copy, so changing b.x leaves a alone. `c` points at `a` itself, so
      `c->x = 3` changes a.x."""),

    q("enum-values", r'''
        #include <stdio.h>

        enum C { RED, GREEN = 5, BLUE, PINK = 2, WHITE };

        int main(void) {
            printf("%d %d %d %d\n", RED, GREEN, BLUE, WHITE);
        }
    ''', "0 5 6 3", ["0 5 5 3", "0 1 2 3", "0 5 6 6"],
      "An enum constant without a value is one more than the one before it",
      """RED starts at 0. GREEN is set to 5, so BLUE is 6. PINK resets the count to 2, so WHITE is 3, even
      though 3 is lower than BLUE."""),

    q("shadowed-variable", r'''
        #include <stdio.h>

        int main(void) {
            int x = 1;
            { int x = 2; x += 10; }
            for (int x = 5; x < 7; x++);
            printf("%d\n", x);
        }
    ''', "1", ["12", "7", "2"],
      "A variable declared in an inner block hides the outer one only inside it",
      """The block's `x` and the loop's `x` are new variables that disappear at the closing brace. The
      outer `x` was never touched, so it is still 1."""),

    q("recursion-call-count", r'''
        #include <stdio.h>

        static int calls;

        int fib(int n) {
            calls++;
            return n < 2 ? n : fib(n - 1) + fib(n - 2);
        }

        int main(void) {
            int v = fib(5);
            printf("%d %d\n", v, calls);
        }
    ''', "5 15", ["5 5", "5 9", "5 10"],
      "Naive recursion calls itself far more times than the answer suggests",
      """fib(5) is 5, but it gets there by calling fib 15 times: each call makes two more, so the count
      grows like the Fibonacci numbers themselves."""),

    q("char-sum-promotion", r'''
        #include <stdio.h>

        int main(void) {
            char a = 'a', b = 'b';
            printf("%d %c\n", a + b, a + 1);
        }
    ''', "195 b", ["195 c", "ab b", "98 b"],
      "Adding chars gives an int, not a joined string",
      """'a' is 97 and 'b' is 98, so the sum is the number 195. `a + 1` is 98, which %c prints as 'b'."""),

    q("globals-start-at-zero", r'''
        #include <stdio.h>

        int g;
        static double d;
        char *p;

        int main(void) {
            printf("%d %.1f %d\n", g, d, p == NULL);
        }
    ''', "0 0.0 1", ["0 0.0 0", "1 1.0 1", "0 0.0 garbage"],
      "Globals and statics are zeroed for you; local variables are not",
      """Everything with static storage starts as all-zero bits: 0 for ints, 0.0 for doubles and a null
      pointer. Only local variables are left with whatever was in memory."""),

    q("sizeof-not-evaluated", r'''
        #include <stdio.h>

        int main(void) {
            int i = 5;
            size_t n = sizeof(i++);
            printf("%d %d\n", i, n == sizeof(int));
        }
    ''', "5 1", ["6 1", "5 0", "6 0"],
      "sizeof looks at the type only; its operand is never run",
      """The compiler works out the size from the type of `i++`, which is int, and never executes the
      expression. So i is still 5."""),

    q("sizeof-array-vs-pointer", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char a[100] = "hi";
            char *p = a;
            printf("%zu %d %zu\n", sizeof a, sizeof p == sizeof a, strlen(a));
        }
    ''', "100 0 2", ["100 1 2", "2 1 2", "100 0 100"],
      "sizeof on an array is the whole array; on a pointer it is just the pointer",
      """`sizeof a` is all 100 bytes, while `sizeof p` is only the size of an address, far smaller, so
      they are not equal. `strlen` stops at the first zero, after "hi"."""),

    q("unsigned-wraparound", r'''
        #include <stdio.h>
        #include <limits.h>

        int main(void) {
            unsigned int x = UINT_MAX;
            x += 2;
            printf("%u\n", x);
        }
    ''', "1", ["0", "2", "4294967297"],
      "Unsigned arithmetic wraps around instead of overflowing",
      """Unsigned values are reduced modulo one more than the maximum. The maximum plus 1 is 0, and plus 2
      is 1, so there is no error and no big number."""),

    q("char-array-modify", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char s[] = "hello";
            s[0] = 'J';
            s[4] = '\0';
            printf("%s %zu\n", s, strlen(s));
        }
    ''', "Jell 4", ["Jello 5", "hell 4", "Jell 5"],
      "A string ends at the first zero byte, wherever you put it",
      """The array is a private, writable copy, so the first letter becomes 'J'. Putting a zero at
      index 4 cuts the string to "Jell", so `strlen` is 4."""),

    q("string-embedded-nul", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char s[] = "ab\0cd";
            printf("%zu %zu %s\n", strlen(s), sizeof s, s + 3);
        }
    ''', "2 6 cd", ["5 6 cd", "2 5 cd", "2 6 d"],
      "strlen stops at the first zero byte, but the array still holds everything",
      """The `\\0` in the middle ends the string for `strlen`, giving 2. The array itself holds a, b, a
      zero, c, d and the final zero, which is 6 bytes. `s + 3` starts at 'c'."""),

    q("octal-literal", r'''
        #include <stdio.h>

        int main(void) {
            printf("%d %d\n", 010 + 1, 0x10 + 1);
        }
    ''', "9 17", ["11 17", "11 11", "9 11"],
      "A leading 0 on a number makes it octal",
      """`010` is written in base 8, so it is 8, and 8 + 1 is 9. `0x10` is hexadecimal, 16, and
      16 + 1 is 17."""),

    q("mixed-int-float", r'''
        #include <stdio.h>

        int main(void) {
            printf("%d %.2f\n", 10 / 4 * 4, 10 / 4.0 * 4);
        }
    ''', "8 10.00", ["10 10.00", "8 8.00", "10 8.00"],
      "Integer division loses the fraction before the multiplication sees it",
      """`10 / 4 * 4` goes left to right: 10 / 4 is 2 as ints, and 2 * 4 is 8. With `4.0` the division is
      done in doubles, 2.5, and 2.5 * 4 is 10.00."""),

    q("bool-conversion", r'''
        #include <stdio.h>
        #include <stdbool.h>

        int main(void) {
            bool b = 5;
            int n = 3;
            printf("%d %d %d\n", b, (bool)0.5, !!n);
        }
    ''', "1 1 1", ["5 0 1", "5 1 3", "1 0 1"],
      "Anything nonzero becomes exactly 1 when stored in a bool",
      """Converting to `bool` is a test for zero, not a truncation: 5 becomes 1 and so does 0.5.
      `!!n` is the same trick done by hand, turning 3 into 1."""),

    q("comparison-is-one", r'''
        #include <stdio.h>

        int main(void) {
            int a = 3;
            printf("%d %d %d\n", a > 1, (a > 1) == 1, (a > 1) == a);
        }
    ''', "1 1 0", ["1 1 1", "3 1 0", "1 0 0"],
      "A comparison gives exactly 1 or 0, not the value that made it true",
      """`a > 1` is true, and true is the number 1, not 3. So it equals 1, but it does not equal a, even
      though both are "true" in an if."""),

    q("float-vs-double-literal", r'''
        #include <stdio.h>

        int main(void) {
            float f = 0.1f;
            printf("%d %d\n", f == 0.1, f == 0.1f);
        }
    ''', "0 1", ["1 1", "0 0", "1 0"],
      "0.1 is a double; 0.1f is a float; they are different numbers",
      """The float holds 0.1 rounded to about 7 digits, and the double 0.1 is rounded to about 16. When
      they meet, the float is widened but is still the coarser number, so they differ."""),

    q("logical-and-bitwise-not", r'''
        #include <stdio.h>

        int main(void) {
            printf("%d %d %d\n", !5, ~5, !!5);
        }
    ''', "0 -6 1", ["0 -5 1", "0 -6 5", "-6 0 1"],
      "! flips true and false; ~ flips every bit",
      """`!5` is 0 because 5 counts as true. `~5` flips all the bits of 5, and for an int that is -6
      (the same as -5 - 1). `!!5` is back to 1."""),

    q("string-array-sizes", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char a[] = "abc";
            char b[10] = "abc";
            printf("%zu %zu %zu %zu\n", sizeof a, sizeof b, strlen(a), strlen(b));
        }
    ''', "4 10 3 3", ["3 10 3 3", "4 4 3 3", "4 10 4 10"],
      "The array size is its declared length; the string length is where the zero is",
      """With no size given, `a` gets exactly enough room for "abc" and its zero: 4. `b` was declared with
      10, and the rest is filled with zeros. Both strings are 3 characters long."""),

    q("compound-assign-precedence", r'''
        #include <stdio.h>

        int main(void) {
            int x = 10;
            x *= 2 + 3;
            printf("%d\n", x);
        }
    ''', "50", ["23", "25", "30"],
      "x *= 2 + 3 multiplies by the whole right-hand side",
      """The right side is worked out first: 2 + 3 is 5. Then x is multiplied by that 5, which gives 50,
      not 10 * 2 + 3."""),

    q("while-decrement-count", r'''
        #include <stdio.h>

        int main(void) {
            int n = 3;
            while (n--) printf("%d", n);
            printf("\n");
        }
    ''', "210", ["321", "3210", "10"],
      "n-- tests the old value but the body already sees the new one",
      """The test sees 3, 2, 1 and then 0 and stops. But n has been lowered before the body runs, so it
      prints 2, 1 and 0."""),

    q("break-inner-loop", r'''
        #include <stdio.h>

        int main(void) {
            int c = 0;
            for (int i = 0; i < 3; i++)
                for (int j = 0; j < 3; j++) {
                    if (j == 1) break;
                    c++;
                }
            printf("%d\n", c);
        }
    ''', "3", ["1", "6", "9"],
      "break leaves only the innermost loop",
      """For each of the 3 values of i, the inner loop counts once at j = 0 and breaks at j = 1. The outer
      loop carries on regardless, so c is 3."""),

    q("static-in-loop", r'''
        #include <stdio.h>

        int main(void) {
            int r1 = 0, r2 = 0;
            for (int i = 0; i < 3; i++) {
                static int s = 0;
                int a = 0;
                s++;
                a++;
                r1 = s;
                r2 = a;
            }
            printf("%d %d\n", r1, r2);
        }
    ''', "3 1", ["3 3", "1 1", "1 3"],
      "static is set up once; an ordinary local is rebuilt on every pass",
      """`static int s = 0` happens only once and keeps counting across the three passes, ending at 3.
      The ordinary `a` is a fresh 0 each pass, so it is only ever 1."""),

    q("switch-default-middle", r'''
        #include <stdio.h>

        int main(void) {
            switch (3) {
            default: printf("d");
            case 1: printf("1"); break;
            case 2: printf("2");
            }
            printf("\n");
        }
    ''', "d1", ["d", "d12", "1"],
      "default can sit anywhere, and it falls through like any other case",
      """3 matches no case, so control jumps to `default`. It prints d and, with no break, falls into
      `case 1`, which prints 1 and breaks."""),

    q("array-index-forms", r'''
        #include <stdio.h>

        int main(void) {
            int a[] = {5, 6, 7};
            printf("%d %d %d\n", a[1], 1[a], *(a + 2));
        }
    ''', "6 6 7", ["6 5 7", "5 6 7", "6 6 6"],
      "a[i] is *(a + i), and addition commutes, so i[a] works too",
      """The index form is just shorthand for `*(a + i)`. Since `a + 1` and `1 + a` are the same address,
      `1[a]` is the same element as `a[1]`."""),

    q("array-index-increments", r'''
        #include <stdio.h>

        int main(void) {
            int i = 0;
            int a[3] = {10, 20, 30};
            int x = a[i++];
            int y = a[++i];
            printf("%d %d %d\n", x, y, i);
        }
    ''', "10 30 2", ["10 20 2", "20 30 2", "10 30 1"],
      "i++ inside [ ] uses the old index; ++i uses the new one",
      """`a[i++]` reads a[0], which is 10, and then i becomes 1. `a[++i]` raises i to 2 first and reads
      a[2], which is 30."""),

    # ── Medium: a real misreading, but a careful reader gets there ──────────
    q("macro-double-eval", r'''
        #include <stdio.h>
        #define MAX(a, b) ((a) > (b) ? (a) : (b))

        int main(void) {
            int i = 3, j = 5;
            int m = MAX(i++, j++);
            printf("%d %d %d\n", m, i, j);
        }
    ''', "6 4 7", ["5 4 6", "5 4 7", "6 4 6"],
      "A macro argument is pasted in everywhere it appears, so its side effect can run twice",
      """The macro becomes `((i++) > (j++) ? (i++) : (j++))`. The test uses up one i++ and one j++, and
      since 3 is not greater than 5 the else part runs j++ again: m is 6, i is 4 and j is 7."""),

    q("swap-by-value", r'''
        #include <stdio.h>

        void swap_copy(int a, int b) { int t = a; a = b; b = t; }
        void swap_ptr(int *a, int *b) { int t = *a; *a = *b; *b = t; }

        int main(void) {
            int x = 1, y = 2;
            swap_copy(x, y);
            printf("%d %d ", x, y);
            swap_ptr(&x, &y);
            printf("%d %d\n", x, y);
        }
    ''', "1 2 2 1", ["2 1 1 2", "1 2 1 2", "2 1 2 1"],
      "C passes arguments by value: the function swaps its own copies",
      """`swap_copy` receives copies of x and y and swaps those, so the caller sees no change. `swap_ptr`
      is given the addresses and writes through them, so it really swaps."""),

    q("struct-array-field-copy", r'''
        #include <stdio.h>

        struct B { int v[3]; };

        int main(void) {
            struct B a = {{1, 2, 3}};
            struct B b = a;
            b.v[0] = 9;
            printf("%d %d\n", a.v[0], b.v[0]);
        }
    ''', "1 9", ["9 9", "1 1", "9 1"],
      "An array inside a struct is copied along with the struct",
      """A bare array cannot be assigned, but an array that is a member of a struct is part of the
      struct's value. So `b = a` copies all three ints, and changing b leaves a alone."""),

    q("memset-ints", r'''
        #include <stdio.h>
        #include <stdint.h>
        #include <string.h>

        int main(void) {
            int32_t a[2];
            memset(a, 1, sizeof a);
            printf("%d\n", (int)a[0]);
        }
    ''', "16843009", ["1", "257", "65793"],
      "memset fills bytes, not whole ints",
      """Every byte becomes 0x01, so a 4-byte int is 0x01010101, which is 16843009 in decimal. Only 0
      (or -1) gives the number you might expect from `memset`."""),

    q("strcat-strcpy-offset", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char buf[16] = "ab";
            strcat(buf, "cd");
            strcpy(buf + 1, "XYZ");
            printf("%s %zu\n", buf, strlen(buf));
        }
    ''', "aXYZ 4", ["abXYZ 5", "aXYZd 5", "aXYZ 3"],
      "strcpy writes its terminating zero too, cutting off whatever came after",
      """`strcat` makes it "abcd". Copying "XYZ" over it from index 1 also writes a zero byte after the
      Z, so the string becomes "aXYZ" and the old "d" is cut off."""),

    q("strchr-strstr", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            const char *s = "hello world";
            printf("%s|%td|%d\n", strchr(s, 'o'), strstr(s, "wor") - s,
                   strchr(s, 'z') == NULL);
        }
    ''', "o world|6|1", ["o|4|1", "world|6|1", "o world|7|1"],
      "strchr returns the rest of the string from the first match, not just the character",
      """`strchr` points at the first 'o' (index 4), so printing it shows "o world". `strstr` finds "wor" at
      index 6, and a letter that is not there gives NULL."""),

    q("atoi-partial", r'''
        #include <stdio.h>
        #include <stdlib.h>

        int main(void) {
            printf("%d %d %d\n", atoi("42abc"), atoi("abc"), atoi("  7"));
        }
    ''', "42 0 7", ["0 0 7", "42 0 0", "42 -1 7"],
      "atoi reads what it can and silently gives 0 when there is nothing",
      """It skips leading spaces, reads digits, and stops at the first non-digit, so "42abc" is 42 and
      "  7" is 7. With no digits at all it just returns 0, with no way to tell it failed."""),

    q("snprintf-truncation", r'''
        #include <stdio.h>

        int main(void) {
            char b[8];
            int n = snprintf(b, sizeof b, "%d-%d", 123, 456789);
            printf("%s %d\n", b, n);
        }
    ''', "123-456 10", ["123-456 7", "123-4567 10", "123-456789 10"],
      "snprintf cuts the text to fit but returns the length it wanted",
      """Room for 8 bytes means 7 characters and the zero, so the text is cut to "123-456". The return value
      is the length the full text would have had, 10, which is how you notice the cut."""),

    q("constant-folding-types", r'''
        #include <stdio.h>

        int main(void) {
            printf("%.1f %d\n", 1 ? 2 : 3.5,
                   sizeof(1 ? 'a' : 1.0) == sizeof(double));
        }
    ''', "2.0 1", ["2 1", "2 0", "2.0 0"],
      "Both branches of ?: are converted to one common type",
      """With a double in one branch, the 2 is converted to a double as well, even though the 3.5 is never
      chosen. So the result is 2.0, and the whole expression has the size of a double."""),

    q("assignment-chain", r'''
        #include <stdio.h>

        int main(void) {
            int a, b, c;
            a = b = c = 5;
            a += b -= c *= 2;
            printf("%d %d %d\n", a, b, c);
        }
    ''', "0 -5 10", ["10 -5 10", "0 5 10", "10 0 10"],
      "Assignment operators group from the right, so the innermost runs first",
      """`c *= 2` makes c 10. Then `b -= 10` makes b -5. Finally `a += -5` makes a 0."""),

    q("designated-initializers", r'''
        #include <stdio.h>

        int main(void) {
            int a[6] = {[1] = 5, [4] = 7, 8};
            printf("%d %d %d %d\n", a[0], a[1], a[4], a[5]);
        }
    ''', "0 5 7 8", ["5 7 8 0", "0 5 7 0", "0 5 8 0"],
      "An initialiser after a designator continues from the next position",
      """`[1] = 5` and `[4] = 7` set those slots. The plain `8` has no designator, so it goes into the
      slot right after the last one used, a[5]. Everything else is 0."""),

    q("struct-designated-continue", r'''
        #include <stdio.h>

        struct P { int x, y, z; };

        int main(void) {
            struct P p = {.y = 5, 7};
            printf("%d %d %d\n", p.x, p.y, p.z);
        }
    ''', "0 5 7", ["5 7 0", "7 5 0", "0 5 0"],
      "After .y, the next plain value goes to the member that follows y",
      """The `.y = 5` names y. The 7 has no name, so it fills the next member in declaration order, which
      is z. Members never mentioned, like x, are zero."""),

    q("struct-partial-init", r'''
        #include <stdio.h>

        struct Q { int a; int b; int c[2]; };

        int main(void) {
            struct Q q = {1};
            printf("%d %d %d %d\n", q.a, q.b, q.c[0], q.c[1]);
        }
    ''', "1 0 0 0", ["1 1 1 1", "1 0 0 1", "1 2 3 4"],
      "Members without an initialiser are zeroed, nested arrays included",
      """Only the first member is given a value. Every other member, including both elements of the nested
      array, is initialised to 0."""),

    q("string-literal-concat", r'''
        #include <stdio.h>

        int main(void) {
            const char *w[] = {"red" "green", "blue"};
            printf("%zu %s\n", sizeof w / sizeof w[0], w[0]);
        }
    ''', "2 redgreen", ["3 red", "2 red", "3 redgreen"],
      "Two string literals side by side are joined into one",
      """The missing comma does not cause an error: adjacent literals are glued together at compile time.
      So the array holds only 2 strings, "redgreen" and "blue"."""),

    q("unsigned-size-minus", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            int diff = (int)strlen("ab") - 5;
            printf("%d %d\n", diff, strlen("ab") - 5 > 0);
        }
    ''', "-3 1", ["-3 0", "3 1", "-3 -1"],
      "strlen returns an unsigned size_t, so subtracting below zero wraps to a huge number",
      """The cast makes the first subtraction a plain int: -3. Without it, 2 - 5 is done in `size_t` and
      wraps to an enormous positive value, so `> 0` is true."""),

    q("unsigned-countdown", r'''
        #include <stdio.h>

        int main(void) {
            unsigned i = 3;
            int n = 0;
            while (i-- > 0) n++;
            printf("%d %d\n", n, i == (unsigned)-1);
        }
    ''', "3 1", ["3 0", "4 1", "3 3"],
      "The i-- in the test still runs on the check that ends the loop",
      """The body runs 3 times. On the last check i is 0, the test fails, but the decrement still happens
      and an unsigned 0 minus 1 wraps around to the largest value, which is `(unsigned)-1`."""),

    q("unsigned-conversions", r'''
        #include <stdio.h>
        #include <stdint.h>
        #include <limits.h>

        int main(void) {
            int m = -1;
            unsigned char c = m;
            uint16_t s = m;
            unsigned u = m;
            printf("%d %d %d\n", c, s, u == UINT_MAX);
        }
    ''', "255 65535 1", ["-1 -1 0", "255 255 1", "255 65535 0"],
      "Converting -1 to an unsigned type gives that type's largest value",
      """Conversion to an unsigned type is defined as wrapping modulo its size. So -1 becomes 255 for a
      byte, 65535 for 16 bits, and the maximum for an `unsigned`."""),

    q("bitmask-update", r'''
        #include <stdio.h>
        #include <stdint.h>

        int main(void) {
            uint8_t flags = 0;
            flags |= 1 << 2;
            flags |= 1 << 0;
            flags &= ~(1 << 2);
            flags ^= 0xF0;
            printf("%d\n", flags);
        }
    ''', "241", ["245", "240", "1"],
      "Set a bit with |=, clear it with &= ~, flip with ^=",
      """After the first two lines flags is 5 (binary 101). Clearing bit 2 leaves 1. Flipping the top four
      bits with 0xF0 gives 241."""),

    q("hex-parts", r'''
        #include <stdio.h>
        #include <stdint.h>

        int main(void) {
            uint32_t x = 0xDEADBEEF;
            unsigned long hi = x >> 16, lo = x & 0xFFFF;
            unsigned long top = (uint32_t)(x << 8) >> 24;
            printf("%lX %lX %lu\n", hi, lo, top);
        }
    ''', "DEAD BEEF 173", ["BEEF DEAD 173", "DEAD BEEF 237", "DEADBEEF 0 173"],
      "Shifting right keeps the top half; masking with 0xFFFF keeps the bottom half",
      """`x >> 16` leaves the high half, 0xDEAD, and `x & 0xFFFF` the low half, 0xBEEF. Shifting left by 8
      drops the top byte, giving 0xADBEEF00, and shifting that right by 24 leaves 0xAD, which is 173."""),

    q("pointer-increment-deref", r'''
        #include <stdio.h>

        int main(void) {
            int a[] = {1, 2, 3};
            int *p = a;
            int x = *p++;
            int y = *p;
            int z = (*p)++;
            printf("%d %d %d %d\n", x, y, z, a[1]);
        }
    ''', "1 2 2 3", ["2 2 2 3", "1 2 3 3", "1 2 2 2"],
      "*p++ moves the pointer; (*p)++ changes the value it points at",
      """`*p++` reads a[0] and then moves p along to a[1]. `*p` reads that 2. `(*p)++` returns the old 2 and
      raises a[1] to 3."""),

    q("pointer-to-pointer", r'''
        #include <stdio.h>

        int main(void) {
            int x = 1, y = 2;
            int *p = &x;
            int **pp = &p;
            **pp = 10;
            *pp = &y;
            **pp += 5;
            printf("%d %d %d\n", x, y, *p);
        }
    ''', "10 7 7", ["10 2 7", "15 2 7", "10 7 10"],
      "Writing through **pp changes a value; writing to *pp changes where p points",
      """`**pp = 10` sets x. `*pp = &y` makes p point at y. After that, `**pp += 5` adds 5 to y, and
      `*p` sees the same y."""),

    q("pointer-minus-neg-index", r'''
        #include <stdio.h>

        int main(void) {
            int a[] = {1, 2, 3, 4, 5};
            int *p = &a[3];
            printf("%d %d\n", p[-1], -1[p]);
        }
    ''', "3 -5", ["3 5", "3 3", "4 -5"],
      "-1[p] is -(1[p]), not p[-1]",
      """`p[-1]` steps back one element to a[2], which is 3. In `-1[p]`, the subscript binds tighter than
      the minus, so it is the negative of `p[1]`, which is a[4] = 5."""),

    q("typedef-vs-define-pointer", r'''
        #include <stdio.h>
        #define IP int *
        typedef int *TP;

        int main(void) {
            int x = 3;
            IP a, b;
            TP c, d;
            a = &x; b = 4; c = &x; d = &x;
            printf("%d %d %d\n", *a, b, *c + *d);
        }
    ''', "3 4 6", ["3 3 6", "3 4 3", "3 4 7"],
      "#define pastes text, so the * sticks to the first name only; typedef makes a real type",
      """`IP a, b;` becomes `int *a, b;`, so only a is a pointer and b is a plain int. With the typedef,
      both c and d are pointers to int, and each reads the 3."""),

    q("strtok-mutates", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char s[] = "a,b,,c";
            int n = 0;
            for (char *t = strtok(s, ","); t; t = strtok(NULL, ",")) n++;
            printf("%d %zu\n", n, strlen(s));
        }
    ''', "3 1", ["4 6", "3 6", "4 1"],
      "strtok skips empty tokens and writes zero bytes into your string",
      """The double comma is treated as one separator, so there are 3 tokens, not 4. Each delimiter it
      finds is overwritten with a zero, so the original string now ends after the first "a"."""),

    q("long-long-literals", r'''
        #include <stdio.h>

        int main(void) {
            long long a = 1LL << 40;
            long long b = 1000000LL * 1000000;
            printf("%lld %lld\n", a, b);
        }
    ''', "1099511627776 1000000000000", ["1099511627776 -727379968", "0 1000000000000", "1099511627776 0"],
      "The LL suffix makes the arithmetic 64-bit; without it, an int would overflow",
      """`1LL << 40` and `1000000LL * 1000000` are done in `long long`, so neither overflows. The same
      sums with plain ints would be undefined behaviour."""),

    q("comparison-and-or-precedence", r'''
        #include <stdio.h>

        int main(void) {
            int a = 5, b = 3;
            printf("%d %d %d\n", a / b * b + a % b, a & b | a ^ b, a && b || !a);
        }
    ''', "5 7 1", ["5 6 1", "1 7 1", "5 7 0"],
      "Among the bit operators, & binds tighter than ^, which binds tighter than |",
      """`a / b * b + a % b` always gives back a: 5. The second is `(a & b) | (a ^ b)`, which is
      `1 | 6`, or 7. The last is true because `a && b` is already true."""),

    q("macro-stringify", r'''
        #include <stdio.h>
        #define STR(x) #x
        #define XSTR(x) STR(x)
        #define N 5

        int main(void) {
            printf("%s %s\n", STR(N), XSTR(N));
        }
    ''', "N 5", ["5 5", "N N", "5 N"],
      "# turns the argument into text before it is expanded",
      """`STR(N)` stringifies the name N itself, so it gives "N". `XSTR(N)` first lets N expand to 5 as
      its own argument, then passes that to STR, which gives "5"."""),

    q("macro-paste", r'''
        #include <stdio.h>
        #define CAT(a, b) a##b

        int main(void) {
            int xy = 7, x = 1, y = 2;
            printf("%d %d\n", CAT(x, y), x + y);
        }
    ''', "7 3", ["12 3", "3 3", "7 12"],
      "## glues two tokens into one name before the compiler reads it",
      """`CAT(x, y)` becomes the single name `xy`, which is the variable holding 7. `x + y` is an ordinary
      sum, 3."""),

    q("macro-two-statements", r'''
        #include <stdio.h>
        #define BUMP(v) v++; v++

        int main(void) {
            int n = 0;
            if (0) BUMP(n);
            printf("%d\n", n);
        }
    ''', "1", ["0", "2", "3"],
      "A macro of two statements only puts the first one under the if",
      """The text becomes `if (0) n++; n++;`. The if guards only the first `n++`, which is skipped, and
      the second `n++` always runs, so n is 1."""),

    q("shift-and-plus", r'''
        #include <stdio.h>

        int main(void) {
            printf("%d %d\n", 1 << 2 + 1, (1 << 2) + 1);
        }
    ''', "8 5", ["5 5", "8 8", "5 8"],
      "+ binds tighter than <<",
      """`1 << 2 + 1` is `1 << 3`, which is 8. Only the bracketed version shifts first: 4 + 1 is 5."""),

    q("two-d-pointer-walk", r'''
        #include <stdio.h>

        int main(void) {
            int g[2][3] = {{1, 2, 3}, {4, 5, 6}};
            int (*p)[3] = g + 1;
            printf("%d %d %d\n", g[1][0], p[0][2], (*(g + 1))[1]);
        }
    ''', "4 6 5", ["2 6 5", "4 3 2", "4 6 6"],
      "g + 1 skips a whole row, not one int",
      """`g` decays to a pointer to a row of 3 ints, so adding 1 moves down a full row to {4, 5, 6}. From
      there `[0][2]` is 6, and `(*(g + 1))[1]` is 5."""),

    q("char-2d-strings", r'''
        #include <stdio.h>

        int main(void) {
            char names[3][6] = {"ann", "bob", "cy"};
            printf("%s %c %zu\n", names[1], names[2][1], sizeof names[0]);
        }
    ''', "bob y 6", ["bob y 3", "ann c 6", "bob b 18"],
      "Every row of a 2-D char array has the same fixed width",
      """Each row is 6 chars no matter how short its string is, so `sizeof names[0]` is 6. `names[2]` is "cy",
      whose second letter is 'y'."""),

    q("struct-return-by-value", r'''
        #include <stdio.h>

        struct P { int x, y; };

        struct P make(int x) { struct P p = {x, x * 2}; return p; }

        int main(void) {
            struct P a = make(2), b = make(5);
            a.x += b.y;
            printf("%d %d %d\n", a.x, a.y, b.x);
        }
    ''', "12 4 5", ["7 4 5", "12 10 5", "12 4 10"],
      "A struct is returned by value: each call gives a separate copy",
      """`make(2)` is (2, 4) and `make(5)` is (5, 10). Adding b.y = 10 to a.x gives 12, and nothing else
      changes."""),

    q("linked-list-walk", r'''
        #include <stdio.h>

        struct N { int v; struct N *next; };

        int main(void) {
            struct N c = {3, NULL}, b = {2, &c}, a = {1, &b};
            int s = 0;
            for (struct N *p = &a; p; p = p->next) s = s * 10 + p->v;
            printf("%d\n", s);
        }
    ''', "123", ["321", "6", "3"],
      "The loop follows the next pointers from the head, one node at a time",
      """It visits a, then b, then c, and each step shifts the total one decimal place and adds the
      node's value: 1, 12, 123. It stops when `next` is NULL."""),

    q("function-pointer-table", r'''
        #include <stdio.h>

        int add(int a, int b) { return a + b; }
        int mul(int a, int b) { return a * b; }

        int main(void) {
            int (*ops[2])(int, int) = {add, mul};
            ops[1] = add;
            int r = ops[0](3, 4);
            int s = ops[1](3, 4);
            printf("%d %d\n", r, s);
        }
    ''', "7 7", ["7 12", "12 7", "12 12"],
      "Assigning a function name to the array slot replaces what that slot calls",
      """The table starts as {add, mul}, but `ops[1] = add` overwrites the second slot. Both calls now
      go to `add`, so both give 7."""),

    q("eval-order-and", r'''
        #include <stdio.h>

        int main(void) {
            int i = 0;
            int r = (i++ == 0) && (i++ == 1) && (i++ == 5);
            printf("%d %d\n", r, i);
        }
    ''', "0 3", ["1 3", "0 1", "0 2"],
      "&& is a sequence point: each side finishes before the next starts, left to right",
      """The first two tests see i as 0 and then 1, so both are true. The third sees 2, and 2 is not 5, so
      the result is 0. All three increments ran, so i is 3."""),

    # ── Hard, but legal and the same on every compiler ─────────────────────
    q("address-of-array", r'''
        #include <stdio.h>

        int main(void) {
            int a[3] = {1, 2, 3};
            printf("%td %td\n", (int *)(&a + 1) - a, (a + 1) - a);
        }
    ''', "3 1", ["1 1", "3 3", "12 1"],
      "&a + 1 steps over the whole array; a + 1 steps over one element",
      """`&a` has the type "pointer to an array of 3 ints", so adding 1 moves past all three. Viewed as an
      int pointer, that spot is 3 elements after the start. `a + 1` is just one element along."""),

    q("array-param-sizeof", r'''
        #include <stdio.h>

        void f(int a[10]) {
            printf("%d %d\n", sizeof a == sizeof(int *),
                   sizeof a == 10 * sizeof(int));
        }

        int main(void) {
            int x[10] = {0};
            f(x);
        }
    ''', "1 0", ["0 1", "1 1", "0 0"],
      "An array parameter is really a pointer, whatever size you write in the brackets",
      """The `[10]` in the parameter list is ignored: `a` is an `int *`. So `sizeof a` is the size of a
      pointer, not the size of 10 ints."""),

    q("double-accumulation", r'''
        #include <stdio.h>

        int main(void) {
            double d = 0;
            for (int i = 0; i < 10; i++) d += 0.1;
            printf("%d %.16f\n", d == 1.0, d);
        }
    ''', "0 0.9999999999999999",
      ["1 1.0000000000000000", "0 1.0000000000000000", "1 0.9999999999999999"],
      "Ten additions of 0.1 do not make exactly 1.0",
      """Each 0.1 carries a tiny rounding error, and they add up to a number just under 1. It prints as
      1.0 with few digits, but `== 1.0` is false."""),

    q("float-runs-out-of-digits", r'''
        #include <stdio.h>

        int main(void) {
            float f = 16777216.0f;
            f += 1;
            printf("%.1f\n", f);
        }
    ''', "16777216.0", ["16777217.0", "16777218.0", "16777216.5"],
      "A float has 24 bits of precision, so above 16777216 it skips whole numbers",
      """Past 2 to the power 24, a float cannot tell n from n + 1. The exact answer 16777217 sits halfway
      between two floats and rounds back to the even one, 16777216, so adding 1 does nothing."""),

    q("count-set-bits", r'''
        #include <stdio.h>

        int main(void) {
            unsigned x = 0xF0F0;
            int c = 0;
            while (x) {
                x &= x - 1;
                c++;
            }
            printf("%d\n", c);
        }
    ''', "8", ["16", "4", "12"],
      "x &= x - 1 clears the lowest set bit each time round",
      """0xF0F0 has eight bits set (four in each of two groups). Each pass of the loop removes exactly one
      of them, so it runs 8 times."""),

    q("promotion-then-shift", r'''
        #include <stdio.h>
        #include <stdint.h>

        int main(void) {
            uint8_t x = 0x80;
            printf("%d %d\n", x << 1, (uint8_t)(x << 1));
        }
    ''', "256 0", ["0 0", "256 256", "128 0"],
      "A byte is promoted to int before shifting, so the bit is not lost until you cast back",
      """`x << 1` happens in int arithmetic, so the set bit moves into position 8 and gives 256. Casting
      that to `uint8_t` keeps only the low 8 bits, which are all zero."""),

    q("unsigned-char-vs-minus-one", r'''
        #include <stdio.h>

        int main(void) {
            unsigned char c = 255;
            printf("%d %d\n", c == 255, c == -1);
        }
    ''', "1 0", ["1 1", "0 1", "0 0"],
      "Both sides become int first, and 255 is not -1",
      """The unsigned char is promoted to the int 255, which is compared with the int -1. Since the type
      is unsigned, the comparison can never be true, even if the bits look alike."""),

    q("pointer-after-loop", r'''
        #include <stdio.h>

        int main(void) {
            const char *start = "abc", *s = start;
            int n = 0;
            while (*s++) n++;
            printf("%d %td\n", n, s - start);
        }
    ''', "3 4", ["3 3", "4 4", "4 3"],
      "The ++ runs even on the test that ends the loop, so s goes one past the zero",
      """The loop counts 3 letters. On the fourth test `*s` is the zero, the loop ends, but `s++` has
      already moved s on, so it ends 4 characters from the start."""),

    q("strcmp-by-code", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            printf("%d %d\n", strcmp("Zebra", "apple") < 0, strcmp("10", "9") < 0);
        }
    ''', "1 1", ["0 0", "0 1", "1 0"],
      "strcmp compares character codes one by one, not alphabet order or numbers",
      """Capital letters have smaller codes than lowercase ones, so "Zebra" sorts before "apple". And
      '1' is smaller than '9', so "10" sorts before "9"."""),

    q("xor-swap-alias", r'''
        #include <stdio.h>

        int main(void) {
            int a = 5;
            int *p = &a, *q = &a;
            *p ^= *q;
            *q ^= *p;
            *p ^= *q;
            printf("%d\n", a);
        }
    ''', "0", ["5", "10", "1"],
      "The XOR swap zeroes a value that is swapped with itself",
      """When both pointers point at the same int, the first step is `a ^= a`, which is 0, and everything
      after that is 0 ^ 0. The trick only works with two different variables."""),

    q("char-array-partial", r'''
        #include <stdio.h>
        #include <string.h>

        int main(void) {
            char a[5] = {'a', 'b'};
            printf("%zu %d\n", strlen(a), a[4]);
        }
    ''', "2 0", ["5 0", "2 98", "2 garbage"],
      "The unlisted elements of a partly initialised array are zero, which ends the string",
      """Only a[0] and a[1] are given letters. The other three are set to 0, so the array is a proper
      string of length 2, and a[4] is 0."""),

    q("double-to-int-truncates", r'''
        #include <stdio.h>

        int main(void) {
            double x = 3.99, y = -3.99;
            int a = x, b = y;
            printf("%d %d %d\n", a, b, (int)(2.5 + 0.5));
        }
    ''', "3 -3 3", ["4 -4 3", "3 -4 3", "4 -3 2"],
      "Converting a double to an int drops the fraction toward zero; it never rounds",
      """3.99 loses its .99 and becomes 3, and -3.99 loses its fraction and becomes -3 (not -4). The sum
      2.5 + 0.5 is exactly 3.0 before the cast."""),

    q("short-circuit-trace", r'''
        #include <stdio.h>

        int f(int x) { printf("%d", x); return x; }

        int main(void) {
            if (f(0) && f(1)) {}
            if (f(2) || f(3)) {}
            if (f(4) && f(5)) {}
            printf("\n");
        }
    ''', "0245", ["012345", "0235", "01"],
      "&& and || skip their right side when the left side has already decided",
      """`f(0)` is false, so `f(1)` is never called. `f(2)` is true, so `f(3)` is skipped. `f(4)` is true,
      so `&&` must also call `f(5)`. That prints 0, 2, 4 and 5."""),

    q("unsigned-overflow-check", r'''
        #include <stdio.h>
        #include <stdint.h>

        int main(void) {
            uint32_t a = 4000000000u, b = 500000000u;
            uint32_t s = a + b;
            printf("%lu %d\n", (unsigned long)s, s < a);
        }
    ''', "205032704 1", ["4500000000 0", "205032704 0", "0 1"],
      "An unsigned sum that wraps ends up smaller than one of its parts",
      """The true sum 4,500,000,000 does not fit in 32 bits, so it wraps to that minus 4,294,967,296, or
      205,032,704. Seeing `s < a` is the standard way to notice the wrap."""),

    q("strcpy-idiom", r'''
        #include <stdio.h>

        int main(void) {
            char dst[8];
            const char *src = "hey";
            char *d = dst;
            while ((*d++ = *src++));
            printf("%s %td\n", dst, d - dst);
        }
    ''', "hey 4", ["hey 3", "he 3", "hey 5"],
      "The loop copies the zero byte too, and d is moved past it",
      """The assignment `*d++ = *src++` is also the loop test, so it stops after copying the terminating
      zero. That makes four bytes written and d four places from the start."""),

    q("negate-unsigned", r'''
        #include <stdio.h>

        int main(void) {
            unsigned u = 1;
            printf("%d %d\n", -u > 0, -(int)u > 0);
        }
    ''', "1 0", ["0 0", "1 1", "0 1"],
      "Negating an unsigned number wraps instead of going below zero",
      """`-u` stays unsigned, so -1 wraps to the largest value, which is greater than 0. After the cast
      to int, `-(int)u` is a real -1, which is not."""),

    q("shift-out-bits", r'''
        #include <stdio.h>
        #include <stdint.h>

        int main(void) {
            uint32_t x = 3;
            x <<= 31;
            printf("%lu\n", (unsigned long)x);
        }
    ''', "2147483648", ["6442450944", "3", "0"],
      "Bits shifted past the top of an unsigned type are simply lost",
      """3 is binary 11. Shifting it left by 31 puts the lowest bit in position 31 and pushes the other one
      off the end, leaving only bit 31, which is 2147483648."""),

    q("do-while-continue", r'''
        #include <stdio.h>

        int main(void) {
            int i = 0, n = 0;
            do {
                i++;
                if (i < 3) continue;
                n++;
            } while (i < 5);
            printf("%d %d\n", i, n);
        }
    ''', "5 3", ["5 5", "5 2", "3 1"],
      "continue in a do-while jumps to the test at the bottom, not the top",
      """For i = 1 and 2, `continue` skips `n++` but still goes on to the `while` test. For i = 3, 4 and 5
      `n++` runs, so n is 3, and the loop ends when i reaches 5."""),
)
