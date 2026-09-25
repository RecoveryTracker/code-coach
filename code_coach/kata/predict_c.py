"""Predict the output, in C.

C is the language the others are written in, and most of what surprises
people about it is C being honest about the machine: an int is a fixed
number of bits, a char is a small number, an array name is an address,
and a function gets a copy of whatever you pass it. The languages built
on top of it hide each of those, so a reader coming from Python or
JavaScript guesses the friendly answer and C prints the literal one.

Every program here is well-defined. That matters more in C than in any
other set: a snippet with undefined behaviour prints whatever the
compiler felt like that day, and a puzzle whose answer is "it depends"
teaches nothing. So nothing modifies a variable twice in one expression,
nothing relies on the order function arguments are evaluated in, and no
`printf` is handed a value that does not match its format. Where an
answer depends on the platform — the size of an int or a pointer — the
explanation says so, and the answer given is the one for 64-bit
Windows, Linux and macOS alike.

Every expected output was typed out first and then checked against
clang 21 at -std=c17, and the suite keeps checking — same way round as
the rest of predict.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p


C_PUZZLES: tuple[Puzzle, ...] = (
    _p(
        id="predict-c-int-division",
        level=1,
        language="c",
        name="Dividing whole numbers, both signs",
        family="C",
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%d %d\\n\", 7 / 2, -7 / 2);\n"
            "    printf(\"%d %d\\n\", 7 % 3, -7 % 3);\n"
            "    return 0;\n"
            "}"
        ),
        expect="3 -3\n1 -1",
        why=(
            "Two ints divide to an int, and C throws the fraction away "
            "towards zero — so -7 / 2 is -3, not the -4 Python's floor "
            "division gives. The remainder follows the division: it "
            "takes the sign of the left-hand side, so -7 % 3 is -1. "
            "Python says 2 for the same expression, which is why "
            "`n % 2 == 1` is not a test for odd numbers in C."
        ),
    ),
    _p(
        id="predict-c-char-arithmetic",
        level=1,
        language="c",
        name="A letter plus one",
        family="C",
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    char c = 'a' + 1;\n"
            "    printf(\"%c %d\\n\", c, c);\n"
            "    printf(\"%d\\n\", '7' - '0');\n"
            "    return 0;\n"
            "}"
        ),
        expect="b 98\n7",
        why=(
            "A char is a small integer, and 'a' is just a way of writing "
            "97. Adding one gives 98, which %c shows as a letter and %d "
            "as a number — same value, two formats. The digit trick is "
            "the one every C parser uses: the characters '0' to '9' are "
            "consecutive, so subtracting '0' turns a digit character into "
            "its value."
        ),
    ),
    _p(
        id="predict-c-float-format",
        level=2,
        language="c",
        name="Two decimal places",
        family="C",
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%.2f\\n\", 3.0 / 2);\n"
            "    printf(\"%.2f\\n\", (double)(3 / 2));\n"
            "    printf(\"%.2f\\n\", 2.675);\n"
            "    return 0;\n"
            "}"
        ),
        expect="1.50\n1.00\n2.67",
        why=(
            "One double in a division makes it a double division, so "
            "3.0 / 2 is 1.5. In the second line the cast comes too late: "
            "3 / 2 has already been done in ints and is 1, and turning "
            "1 into a double gives 1.00. The last one is not a rounding "
            "bug. 2.675 cannot be stored exactly — the nearest double is "
            "2.67499999… — and printf rounds the number it was given. "
            "(Passing 3.0 / 2 to %d instead would be undefined: the "
            "format has to match the type.)"
        ),
    ),
    _p(
        id="predict-c-increment",
        level=2,
        language="c",
        name="Before or after",
        family="C",
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    int i = 5;\n"
            "    int a = i++;\n"
            "    int b = ++i;\n"
            "    int c = 10 * i++;\n"
            "    printf(\"%d %d %d %d\\n\", a, b, c, i);\n"
            "    return 0;\n"
            "}"
        ),
        expect="5 7 70 8",
        why=(
            "`i++` hands back the old value and then adds one; `++i` adds "
            "one and hands back the new value. So a gets 5 (i becomes 6), "
            "b gets 7 (i is 7), and c is 10 times the old 7 before i "
            "moves on to 8. Each line changes i once, which is what keeps "
            "this well-defined — `i = i++` or `i++ + i++` would be "
            "undefined behaviour, not a harder puzzle."
        ),
    ),
    _p(
        id="predict-c-switch-fallthrough",
        level=2,
        language="c",
        name="A case with no break",
        family="C",
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    switch (2) {\n"
            "    case 1: printf(\"one \");\n"
            "    case 2: printf(\"two \");\n"
            "    case 3: printf(\"three \");\n"
            "    default: printf(\"many\");\n"
            "    }\n"
            "    printf(\"\\n\");\n"
            "    return 0;\n"
            "}"
        ),
        expect="two three many",
        why=(
            "A case label is only a place to jump to, not a block. The "
            "switch jumps to `case 2` and then carries on downwards "
            "through every statement after it, labels and all, until it "
            "meets a break or the closing brace. Forgetting a break is "
            "one of the oldest C bugs there is, which is why Go, Swift "
            "and C# all changed the rule."
        ),
    ),
    _p(
        id="predict-c-short-circuit",
        level=3,
        language="c",
        name="The increment that never ran",
        family="C",
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    int x = 0, n = 0;\n"
            "    if (x && ++n) printf(\"A\\n\");\n"
            "    if (x || ++n) printf(\"B\\n\");\n"
            "    if (!x || ++n) printf(\"C\\n\");\n"
            "    printf(\"%d\\n\", n);\n"
            "    return 0;\n"
            "}"
        ),
        expect="B\nC\n1",
        why=(
            "`&&` stops as soon as the left side is false, and `||` stops "
            "as soon as it is true — the right side is not evaluated at "
            "all, side effect included. In the first line x is 0, so ++n "
            "never runs. In the second, x is 0 so || has to look right: "
            "n becomes 1, which is true, and B prints. In the third, !x "
            "is already true, so n is left alone."
        ),
    ),
    _p(
        id="predict-c-static-local",
        level=3,
        language="c",
        name="A local that remembers",
        family="C",
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int tick(void) {\n"
            "    static int calls = 0;\n"
            "    int fresh = 0;\n"
            "    calls++;\n"
            "    fresh++;\n"
            "    return calls * 10 + fresh;\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    int a = tick();\n"
            "    int b = tick();\n"
            "    printf(\"%d %d %d\\n\", a, b, tick());\n"
            "    return 0;\n"
            "}"
        ),
        expect="11 21 31",
        why=(
            "`static` on a local changes how long it lives, not who can "
            "see it. It is set to 0 once, before the program starts, and "
            "keeps its value from call to call — so calls counts 1, 2, 3. "
            "`fresh` is an ordinary local, made again and set to 0 on "
            "every call, so it is always 1 by the time it is used. The "
            "first two calls are made on their own lines because C does "
            "not say which order a function's arguments are evaluated in."
        ),
    ),
    _p(
        id="predict-c-pointer-arithmetic",
        level=3,
        language="c",
        name="An array name is an address",
        family="C",
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    int a[] = {10, 20, 30, 40};\n"
            "    int *p = a + 1;\n"
            "    printf(\"%d %d\\n\", *p, *(p + 2));\n"
            "    printf(\"%d %d\\n\", p[1], 2[a]);\n"
            "    printf(\"%td\\n\", &a[3] - p);\n"
            "    return 0;\n"
            "}"
        ),
        expect="20 40\n30 30\n2",
        why=(
            "In an expression, `a` turns into a pointer to its first "
            "element, and adding to a pointer moves it by whole elements, "
            "not bytes — so a + 1 points at 20, and p + 2 at 40. `p[1]` "
            "is defined as *(p + 1), which is why the strange-looking "
            "2[a] is legal and means a[2]: addition does not care about "
            "order. Subtracting two pointers counts elements too, so the "
            "gap from 20 to 40 is 2."
        ),
    ),
    _p(
        id="predict-c-struct-copy",
        level=3,
        language="c",
        name="Moving a point",
        family="C",
        code=(
            "#include <stdio.h>\n"
            "\n"
            "struct point { int x, y; };\n"
            "\n"
            "void by_value(struct point p) { p.x += 10; }\n"
            "void by_pointer(struct point *p) { p->x += 10; }\n"
            "\n"
            "int main(void) {\n"
            "    struct point a = {1, 2};\n"
            "    struct point b = a;\n"
            "    b.y = 99;\n"
            "    by_value(a);\n"
            "    by_pointer(&b);\n"
            "    printf(\"%d %d %d %d\\n\", a.x, a.y, b.x, b.y);\n"
            "    return 0;\n"
            "}"
        ),
        expect="1 2 11 99",
        why=(
            "Assigning a struct copies every field, so b is a separate "
            "point and changing b.y leaves a alone. Passing a struct "
            "copies it too: by_value moves its own copy and the copy is "
            "thrown away when it returns. Only by_pointer, handed the "
            "address of b, changes something the caller can see. This is "
            "the opposite of Python, JavaScript and Dart, where an object "
            "is always shared."
        ),
    ),
    _p(
        id="predict-c-sizeof-strlen",
        level=4,
        language="c",
        name="How big is the word",
        family="C",
        code=(
            "#include <stdio.h>\n"
            "#include <string.h>\n"
            "\n"
            "void show(char *s) {\n"
            "    printf(\"%zu %zu\\n\", sizeof s, strlen(s));\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    char word[10] = \"hi\";\n"
            "    printf(\"%zu %zu\\n\", sizeof word, strlen(word));\n"
            "    show(word);\n"
            "    printf(\"%zu\\n\", sizeof \"hello\");\n"
            "    return 0;\n"
            "}"
        ),
        expect="10 2\n8 2\n6",
        why=(
            "`strlen` counts characters up to the terminating zero; "
            "`sizeof` asks the compiler how many bytes the thing takes. "
            "In main, word is an array of 10 bytes holding a 2-letter "
            "string. Passed to show, it arrives as a plain pointer — an "
            "array argument always does — so sizeof there is the size of "
            "a pointer, 8 on any 64-bit system. That is why C functions "
            "take a length alongside the array. A string literal is an "
            "array too, and it includes the zero: \"hello\" is 6 bytes."
        ),
    ),
    _p(
        id="predict-c-unsigned-wrap",
        level=4,
        language="c",
        name="Zero minus one",
        family="C",
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    unsigned int u = 0u - 1;\n"
            "    printf(\"%u\\n\", u);\n"
            "    printf(\"%s\\n\", -1 < 1u ? \"less\" : \"not less\");\n"
            "    return 0;\n"
            "}"
        ),
        expect="4294967295\nnot less",
        why=(
            "Unsigned arithmetic never goes negative — it wraps, and C "
            "guarantees exactly how: 0 - 1 is the largest value the type "
            "holds, 2^32 - 1 for a 32-bit unsigned int. The comparison is "
            "the dangerous version of the same thing. When a signed int "
            "meets an unsigned one, the signed one is converted, so -1 "
            "becomes 4294967295 and is not less than 1. A loop like "
            "`for (unsigned i = n - 1; i >= 0; i--)` never ends for this "
            "reason."
        ),
    ),
    _p(
        id="predict-c-char-promotion",
        level=5,
        language="c",
        name="Small numbers grow up",
        family="C",
        code=(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    unsigned char a = 200, b = 100;\n"
            "    unsigned char sum = a + b;\n"
            "    printf(\"%d %d\\n\", a + b, sum);\n"
            "    unsigned char mask = 0x0F;\n"
            "    printf(\"%s\\n\", ~mask == 0xF0 ? \"equal\" : \"different\");\n"
            "    return 0;\n"
            "}"
        ),
        expect="300 44\ndifferent",
        why=(
            "C never does arithmetic on anything smaller than an int. "
            "Both chars are promoted first, so a + b is the int 300 — no "
            "overflow. Only storing it back into an 8-bit unsigned char "
            "wraps it, to 300 - 256 = 44. The mask is the same rule "
            "biting harder: ~mask flips the bits of the promoted int, not "
            "of the byte, so the result is a negative int rather than "
            "0xF0, and the comparison fails. Cast back — "
            "`(unsigned char)~mask` — to get the byte you meant."
        ),
    ),
)
