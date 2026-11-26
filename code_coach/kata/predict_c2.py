"""More Predict puzzles in C, on ground the first twelve do not cover:
sizeof against strlen, an array that turns into a pointer when it is
passed, unsigned wrap-around in a small type, struct assignment copying,
partial initialisation, bit operators, a macro without brackets, enum
numbering, arrays of strings, function pointers and what printf returns.

The same rules as predict_c.py: every program is well-defined, compiles
with -std=c17 -Wall -Wextra -pedantic and not one warning, and where an
answer depends on the platform (the size of a pointer) it is the one for
64-bit Windows, Linux and macOS alike. tests/test_predict_c2.py checks
every answer against the compiler.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p

FAMILY = "C"


C_PUZZLES_2: tuple[Puzzle, ...] = (
    _p(
        id="predict-c2-sizeof-strlen",
        level=1,
        language="c",
        name="sizeof a string and its length",
        family=FAMILY,
        code=(
            "#include <stdio.h>\n"
            "#include <string.h>\n"
            "\n"
            "int main(void) {\n"
            "    char word[] = \"hi\";\n"
            "    char room[10] = \"hi\";\n"
            "    printf(\"%zu %zu\\n\", sizeof word, strlen(word));\n"
            "    printf(\"%zu %zu\\n\", sizeof room, strlen(room));\n"
            "    return 0;\n"
            "}"
        ),
        expect="3 2\n10 2",
        why=(
            "A string in C ends with an invisible '\\0', so \"hi\" needs 3 bytes "
            "and `sizeof` counts all of them. `strlen` counts the characters "
            "before the '\\0': 2. For `room`, sizeof is the whole array you "
            "asked for, 10, whatever is in it - strlen still says 2."
        ),
    ),
    _p(
        id="predict-c-int-into-double",
        level=1,
        language="c",
        name="Whole-number division stored in a double",
        family=FAMILY,
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    double half = 7 / 2;\n"
            "    double real = 7 / 2.0;\n"
            "    printf(\"%.1f %.1f\\n\", half, real);\n"
            "    return 0;\n"
            "}"
        ),
        expect="3.0 3.5",
        why=(
            "The right-hand side is worked out first, with no idea where it is "
            "going. 7 / 2 is two ints, so it is int division: 3. Only then is 3 "
            "stored in a double, as 3.0. Make one side a double - 2.0 - and the "
            "division itself is done in doubles: 3.5."
        ),
    ),
    _p(
        id="predict-c-enum-values",
        level=1,
        language="c",
        name="Numbering an enum",
        family=FAMILY,
        code=(
            "#include <stdio.h>\n"
            "\n"
            "enum level { LOW, MID = 5, HIGH, TOP = 10 };\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%d %d %d %d\\n\", LOW, MID, HIGH, TOP);\n"
            "    return 0;\n"
            "}"
        ),
        expect="0 5 6 10",
        why=(
            "An enum's names are just int constants. The first is 0 unless "
            "you say otherwise, and each one after is one more than the one "
            "before: MID is set to 5, so HIGH is 6. TOP is set outright."
        ),
    ),
    _p(
        id="predict-c-unsigned-char-wrap",
        level=2,
        language="c",
        name="255 plus one, twice",
        family=FAMILY,
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    unsigned char c = 255;\n"
            "    int sum = c + 1;\n"
            "    c = c + 1;\n"
            "    printf(\"%d %d\\n\", sum, c);\n"
            "    return 0;\n"
            "}"
        ),
        expect="256 0",
        why=(
            "In arithmetic, a small type like unsigned char is first turned "
            "into an int, so c + 1 is the int 256 - and an int can hold it. "
            "Storing that back in c cuts it to 8 bits: an unsigned char holds "
            "0 to 255 and wraps round, so 256 becomes 0. Wrapping is defined "
            "for unsigned types; for signed ones it is not."
        ),
    ),
    _p(
        id="predict-c2-struct-copy",
        level=2,
        language="c",
        name="Assigning one struct to another",
        family=FAMILY,
        code=(
            "#include <stdio.h>\n"
            "\n"
            "struct point { int x; int y; };\n"
            "\n"
            "int main(void) {\n"
            "    struct point a = { 1, 2 };\n"
            "    struct point b = a;\n"
            "    b.x = 9;\n"
            "    printf(\"%d %d\\n\", a.x, b.x);\n"
            "    return 0;\n"
            "}"
        ),
        expect="1 9",
        why=(
            "`b = a` copies every member of the struct into b. They are two "
            "separate structs from then on, so changing b.x leaves a.x at 1. "
            "Arrays cannot be assigned like this, but an array INSIDE a "
            "struct is copied along with the rest."
        ),
    ),
    _p(
        id="predict-c-partial-init",
        level=2,
        language="c",
        name="An array half filled in",
        family=FAMILY,
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    int a[5] = { 4, 5 };\n"
            "    int total = 0;\n"
            "    for (int i = 0; i < 5; i++) {\n"
            "        total += a[i];\n"
            "    }\n"
            "    printf(\"%d %d\\n\", a[4], total);\n"
            "    return 0;\n"
            "}"
        ),
        expect="0 9",
        why=(
            "Give an array SOME starting values and every one you left out is "
            "set to 0. So a is 4, 5, 0, 0, 0, and the total is 9. That is why "
            "`int counts[26] = { 0 };` is the usual way to start an array at "
            "all zeros. With no braces at all, a local array holds whatever "
            "was in that memory."
        ),
    ),
    _p(
        id="predict-c-bitwise",
        level=2,
        language="c",
        name="Bit by bit",
        family=FAMILY,
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    int a = 6;\n"
            "    int b = 3;\n"
            "    printf(\"%d %d %d\\n\", a & b, a | b, a ^ b);\n"
            "    printf(\"%d %d\\n\", 1 << 4, 40 >> 2);\n"
            "    return 0;\n"
            "}"
        ),
        expect="2 7 5\n16 10",
        why=(
            "6 is 110 in binary and 3 is 011. & keeps bits set in both: 010, "
            "2. | keeps bits set in either: 111, 7. ^ keeps bits set in "
            "exactly one: 101, 5. Shifting left by 4 multiplies by 2 four "
            "times, 16; shifting right by 2 halves twice, 10."
        ),
    ),
    _p(
        id="predict-c-strcmp",
        level=2,
        language="c",
        name="Comparing strings",
        family=FAMILY,
        code=(
            "#include <stdio.h>\n"
            "#include <string.h>\n"
            "\n"
            "int main(void) {\n"
            "    int a = strcmp(\"apple\", \"banana\") < 0;\n"
            "    int b = strcmp(\"Zoo\", \"apple\") < 0;\n"
            "    int c = strcmp(\"same\", \"same\") == 0;\n"
            "    printf(\"%d %d %d\\n\", a, b, c);\n"
            "    return 0;\n"
            "}"
        ),
        expect="1 1 1",
        why=(
            "strcmp gives a negative number when the first string sorts "
            "earlier, 0 when they match, positive when it sorts later. It "
            "compares character codes, and every capital letter has a smaller "
            "code than every small one - so \"Zoo\" comes before \"apple\". A "
            "comparison like `< 0` in C is an int: 1 for true."
        ),
    ),
    _p(
        id="predict-c-array-decays",
        level=3,
        language="c",
        name="An array passed to a function",
        family=FAMILY,
        code=(
            "#include <stdio.h>\n"
            "\n"
            "static void show(int *p) {\n"
            "    printf(\"in function: %zu\\n\", sizeof p);\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    int nums[5] = { 1, 2, 3, 4, 5 };\n"
            "    printf(\"in main: %zu\\n\", sizeof nums / sizeof nums[0]);\n"
            "    show(nums);\n"
            "    return 0;\n"
            "}"
        ),
        expect="in main: 5\nin function: 8",
        why=(
            "In main, nums is a real array, so sizeof gives all 20 bytes and "
            "dividing by one item's 4 bytes gives 5. Passed to a function, an "
            "array turns into a pointer to its first item, and sizeof a "
            "pointer is 8 on 64-bit machines - the length is gone. That is "
            "why C functions that take an array also take its length."
        ),
    ),
    _p(
        id="predict-c-macro-brackets",
        level=3,
        language="c",
        name="A macro without brackets",
        family=FAMILY,
        code=(
            "#include <stdio.h>\n"
            "\n"
            "#define SQUARE(x) x * x\n"
            "#define SAFE_SQUARE(x) ((x) * (x))\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%d %d\\n\", SQUARE(2 + 3), SAFE_SQUARE(2 + 3));\n"
            "    return 0;\n"
            "}"
        ),
        expect="11 25",
        why=(
            "A macro pastes text, it does not call anything. SQUARE(2 + 3) "
            "becomes 2 + 3 * 2 + 3, and * goes first: 2 + 6 + 3 = 11. Putting "
            "brackets round every use of x, and round the whole thing, makes "
            "it work out as intended: (2 + 3) * (2 + 3) = 25."
        ),
    ),
    _p(
        id="predict-c-string-array",
        level=3,
        language="c",
        name="An array of strings",
        family=FAMILY,
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    const char *words[] = { \"ant\", \"bee\", \"cat\" };\n"
            "    printf(\"%c\\n\", *words[1]);\n"
            "    printf(\"%s\\n\", words[2] + 1);\n"
            "    printf(\"%c\\n\", words[0][2]);\n"
            "    return 0;\n"
            "}"
        ),
        expect="b\nat\nt",
        why=(
            "words holds three pointers, each to the first letter of a word. "
            "`*words[1]` follows the second pointer to its first char, 'b'. "
            "`words[2] + 1` points one char further into \"cat\", so %s prints "
            "from there: \"at\". `words[0][2]` is the third char of \"ant\"."
        ),
    ),
    _p(
        id="predict-c-function-pointer",
        level=4,
        language="c",
        name="Choosing a function at runtime",
        family=FAMILY,
        code=(
            "#include <stdio.h>\n"
            "\n"
            "static int add(int a, int b) { return a + b; }\n"
            "static int mul(int a, int b) { return a * b; }\n"
            "\n"
            "int main(void) {\n"
            "    int (*ops[])(int, int) = { add, mul };\n"
            "    for (int i = 0; i < 2; i++) {\n"
            "        printf(\"%d\\n\", ops[i](3, 4));\n"
            "    }\n"
            "    return 0;\n"
            "}"
        ),
        expect="7\n12",
        why=(
            "A function's name, used without calling it, is its address, so "
            "ops is an array of two function pointers. `ops[i](3, 4)` calls "
            "whichever one is at i: add first, then mul. This is how C does "
            "what other languages do with first-class functions."
        ),
    ),
    _p(
        id="predict-c-printf-returns",
        level=4,
        language="c",
        name="What printf hands back",
        family=FAMILY,
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    int n = printf(\"hello\\n\");\n"
            "    int m = printf(\"%d\\n\", 1000);\n"
            "    printf(\"%d %d\\n\", n, m);\n"
            "    return 0;\n"
            "}"
        ),
        expect="hello\n1000\n6 5",
        why=(
            "printf returns how many characters it wrote, and the newline "
            "counts: \"hello\\n\" is 6, \"1000\\n\" is 5. Almost everyone ignores "
            "the result, but it is there - and a negative one means the "
            "output failed."
        ),
    ),
)
