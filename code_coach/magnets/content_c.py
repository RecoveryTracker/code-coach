"""The code magnet puzzles in C.

The same puzzle as the JavaScript and Dart ones: the lines of a program
that works, jumbled, to be put back in an order that prints the right
thing. The shapes are the first ones any C course reaches — a function
called from main, a loop over an array, a struct, a string walked to
its terminator, a swap through pointers, and a switch.

C is stricter about order than either of the others, and that is most
of what these puzzles teach.

C reads a file once, top to bottom. A function or a struct has to be
declared above the first line that uses it, because the compiler has
not looked any further down yet. Dart reads every declaration before it
runs anything and JavaScript hoists its functions; C does neither, so a
helper placed below main is a compile error rather than a different
right answer. (A prototype above main is the way round that, and is
left out here to keep each puzzle to twelve magnets.)

Every program starts with `#include <stdio.h>`, which is what makes
`printf` and `puts` known, and so has to come before anything that
prints. Every program has one `int main(void)`, and a statement outside
a function does not compile at all.

The expected output beside each was typed out by a person and is held
to what the compiler's program actually prints by tests/test_magnets_c.py.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m


C_MAGNETS: tuple[Magnet, ...] = (
    _m(
        id="magnet-c-function-before-main",
        plan=(
            ("Bring in the printing library", 1),
            ("A function that squares a number", 3),
            ("Start the program with a value", 2),
            ("Print two squares and finish", 4),
        ),
        level=1,
        name="A function above the main that calls it",
        family="C",
        language="c",
        note=(
            "C reads the file once, top to bottom, and a function has to "
            "be known before a line calls it. So `square` goes above "
            "main: move it below and the call inside main is to a "
            "function nobody has heard of, which modern C refuses to "
            "compile. The include comes first for the same reason — it is "
            "what tells the compiler `printf` exists. Inside main the "
            "usual rules hold: `side` is declared before it is used, the "
            "prints come out in the order they are written, and "
            "`return 0` tells whoever ran the program that it went well."
        ),
        code=(
            "#include <stdio.h>\n"
            "int square(int n) {\n"
            "    return n * n;\n"
            "}\n"
            "int main(void) {\n"
            "    int side = 7;\n"
            "    printf(\"%d\\n\", square(side));\n"
            "    printf(\"%d\\n\", square(side + 1));\n"
            "    return 0;\n"
            "}"
        ),
        expect="49\n64",
    ),
    _m(
        id="magnet-c-sum-array",
        plan=(
            ("Bring in the printing library", 1),
            ("Start the program and hold the scores", 3),
            ("Add each score to a running total", 4),
            ("Report and finish", 3),
        ),
        level=2,
        name="Summing an array with a for loop",
        family="C",
        language="c",
        note=(
            "A C array does not know its own length, so the program "
            "works it out: `sizeof scores` is the whole array in bytes, "
            "`sizeof scores[0]` is one element, and the one divided by "
            "the other is how many there are. That only works where the "
            "array was declared — pass it to a function and it arrives as "
            "a bare pointer. The total has to start at 0 above the loop "
            "(an uninitialised local holds whatever was there before), "
            "the `+=` goes inside the loop's braces, and the print goes "
            "after the closing one; inside, it prints a running total "
            "five times."
        ),
        code=(
            "#include <stdio.h>\n"
            "int main(void) {\n"
            "    int scores[] = {4, 8, 15, 16, 23};\n"
            "    int count = sizeof scores / sizeof scores[0];\n"
            "    int total = 0;\n"
            "    for (int i = 0; i < count; i++) {\n"
            "        total += scores[i];\n"
            "    }\n"
            "    printf(\"total %d of %d\\n\", total, count);\n"
            "    return 0;\n"
            "}"
        ),
        expect="total 66 of 5",
    ),
    _m(
        id="magnet-c-struct",
        plan=(
            ("Bring in the printing library", 1),
            ("Describe what a book holds", 4),
            ("Make one and fill in its length", 3),
            ("Print it and finish", 3),
        ),
        level=2,
        name="A struct, declared then filled",
        family="C",
        language="c",
        note=(
            "A struct is a type you describe before you use it, and in C "
            "it has to be described above the first line that makes one "
            "— below main, `struct Book book` is a variable of a type "
            "the compiler has not seen. Note the semicolon after the "
            "struct's closing brace: it ends a declaration, where a "
            "function's closing brace does not. The braces in `{\"Dune\", "
            "0}` fill the fields in the order they were declared. Then "
            "the order inside main shows: print before `book.pages` is "
            "set and the book has 0 pages."
        ),
        code=(
            "#include <stdio.h>\n"
            "struct Book {\n"
            "    const char *title;\n"
            "    int pages;\n"
            "};\n"
            "int main(void) {\n"
            "    struct Book book = {\"Dune\", 0};\n"
            "    book.pages = 412;\n"
            "    printf(\"%s has %d pages\\n\", book.title, book.pages);\n"
            "    return 0;\n"
            "}"
        ),
        expect="Dune has 412 pages",
    ),
    _m(
        id="magnet-c-walk-string",
        plan=(
            ("Start with a word and two counters", 4),
            ("Walk the word letter by letter, counting", 4),
            ("Report and finish", 3),
        ),
        level=3,
        name="Walking a string to its end",
        family="C",
        language="c",
        note=(
            "A C string is a row of characters with a zero byte, `'\\0'`, "
            "after the last one, and that byte is the only way to know "
            "where it ends — there is no length stored anywhere. So the "
            "loop walks until it finds it. The `i++` has to be inside the "
            "loop: outside, `i` never moves, the loop tests the same "
            "letter forever, and the program never finishes. That is the "
            "classic C hang. Put the print inside the loop and it reports "
            "a running count at every letter instead of the answer."
        ),
        code=(
            "#include <stdio.h>\n"
            "int main(void) {\n"
            "    const char *word = \"banana\";\n"
            "    int count = 0, i = 0;\n"
            "    while (word[i] != '\\0') {\n"
            "        if (word[i] == 'a') count++;\n"
            "        i++;\n"
            "    }\n"
            "    printf(\"%d a's in %s\\n\", count, word);\n"
            "    return 0;\n"
            "}"
        ),
        expect="3 a's in banana",
    ),
    _m(
        id="magnet-c-pointer-swap",
        plan=(
            ("Bring in the printing library", 1),
            ("A function that trades two values", 5),
            ("Two values to trade", 2),
            ("Trade them, show them, finish", 4),
        ),
        level=4,
        name="Swapping through pointers",
        family="C",
        language="c",
        note=(
            "C passes arguments by value, so a function handed `left` "
            "and `right` gets copies and cannot change the originals. "
            "Handing it their addresses, `&left` and `&right`, lets it "
            "reach back: `*a` is the int that `a` points at. The three "
            "lines inside are the whole trick and their order is the "
            "whole puzzle — `*a` has to be saved in `held` before it is "
            "overwritten. Assign `*a = *b` first and the old value is "
            "gone, so both come out as 2. The function goes above main, "
            "which calls it."
        ),
        code=(
            "#include <stdio.h>\n"
            "void swap(int *a, int *b) {\n"
            "    int held = *a;\n"
            "    *a = *b;\n"
            "    *b = held;\n"
            "}\n"
            "int main(void) {\n"
            "    int left = 1, right = 2;\n"
            "    swap(&left, &right);\n"
            "    printf(\"left %d, right %d\\n\", left, right);\n"
            "    return 0;\n"
            "}"
        ),
        expect="left 2, right 1",
    ),
    _m(
        id="magnet-c-switch-break",
        plan=(
            ("Bring in the printing library", 1),
            ("Start the program and count to three", 2),
            ("Choose by number, handling the first", 4),
            ("Every other number", 3),
            ("Close the loop and the program", 2),
        ),
        level=5,
        name="A switch, and where break goes",
        family="C",
        language="c",
        note=(
            "A `case` is only a label to jump to, not a block: once "
            "execution lands on one it runs straight down through every "
            "line below it, into the next case and the one after, until "
            "a `break` sends it out of the switch. So the `break` belongs "
            "under the first case's line. Move it below `default`'s and "
            "1 falls through, printing `one` and then `more` — the bug "
            "C programmers have been writing for fifty years. `puts` "
            "prints a line and adds the newline itself. And main has no "
            "`return 0` here: since C99, reaching main's closing brace "
            "returns 0 on its own."
        ),
        code=(
            "#include <stdio.h>\n"
            "int main(void) {\n"
            "    for (int n = 1; n <= 3; n++) {\n"
            "        switch (n) {\n"
            "        case 1:\n"
            "            puts(\"one\");\n"
            "            break;\n"
            "        default:\n"
            "            puts(\"more\");\n"
            "        }\n"
            "    }\n"
            "}"
        ),
        expect="one\nmore\nmore",
    ),
)
