"""More C code magnets, on shapes the first six do not cover: a while loop
reading digits off a number, a function that fills an array through a
pointer, a 2D array walked by two loops, a string built with a char
buffer, a linked list of two nodes, malloc and free, a recursive function,
and a struct passed by pointer.

C is the strictest about order of all the languages here: a function must
be declared before the line that calls it, a variable before its first use,
and every `{` closed by the right `}`. The expected output beside each was
typed by a person and is held to what the compiler's build prints by
tests/test_magnets_more.py.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m

FAMILY = "C"

C_MAGNETS_2: tuple[Magnet, ...] = (
    _m(
        id="magnet-c-digits",
        plan=(
            ("Bring in printf and open main", 2),
            ("Start with a number and a sum", 2),
            ("Take the digits off one at a time", 4),
            ("Report and finish", 3),
        ),
        level=1,
        name="Adding up the digits of a number",
        family=FAMILY,
        language="c",
        note=(
            "`n % 10` is the last digit and `n / 10` drops it, so the loop "
            "eats the number from the right until nothing is left. The sum "
            "must start at 0 before the loop, and the line that shortens n "
            "has to come AFTER the line that uses its last digit, or the "
            "first digit read is the second one."
        ),
        code=(
            "#include <stdio.h>\n"
            "int main(void) {\n"
            "    int n = 4096;\n"
            "    int sum = 0;\n"
            "    while (n > 0) {\n"
            "        sum += n % 10;\n"
            "        n /= 10;\n"
            "    }\n"
            "    printf(\"%d\\n\", sum);\n"
            "    return 0;\n"
            "}"
        ),
        expect="19",
    ),
    _m(
        id="magnet-c-recursion",
        plan=(
            ("Bring in printf", 1),
            ("A function that counts down by calling itself", 7),
            ("Start it from main", 4),
        ),
        level=2,
        name="A recursive countdown",
        family=FAMILY,
        language="c",
        note=(
            "Each call prints its number and then calls itself with one "
            "less, until it reaches 0 and simply returns. The stop test has "
            "to come first in the function. In C the function must also be "
            "defined (or declared) above main, because main's call is "
            "checked against it when main is compiled."
        ),
        code=(
            "#include <stdio.h>\n"
            "static void countdown(int n) {\n"
            "    if (n == 0) {\n"
            "        return;\n"
            "    }\n"
            "    printf(\"%d \", n);\n"
            "    countdown(n - 1);\n"
            "}\n"
            "int main(void) {\n"
            "    countdown(3);\n"
            "    return 0;\n"
            "}"
        ),
        expect="3 2 1",
    ),
    _m(
        id="magnet-c-fill-array",
        plan=(
            ("Bring in printf", 1),
            ("A function that fills an array it is given", 5),
            ("Make the array, fill it, show the last", 6),
        ),
        level=2,
        name="A function that fills an array",
        family=FAMILY,
        language="c",
        note=(
            "An array passed to a function arrives as a pointer to its first "
            "item, so the function writes straight into main's array - and "
            "it needs the length passed separately, because the pointer does "
            "not know it. The array must exist before it is filled, and be "
            "filled before it is read."
        ),
        code=(
            "#include <stdio.h>\n"
            "static void squares(int *out, int count) {\n"
            "    for (int i = 0; i < count; i++) {\n"
            "        out[i] = i * i;\n"
            "    }\n"
            "}\n"
            "int main(void) {\n"
            "    int nums[5];\n"
            "    squares(nums, 5);\n"
            "    printf(\"%d %d\\n\", nums[2], nums[4]);\n"
            "    return 0;\n"
            "}"
        ),
        expect="4 16",
    ),
    _m(
        id="magnet-c-grid",
        plan=(
            ("Bring in printf and open main", 2),
            ("A small grid of numbers", 1),
            ("Walk every row and every column", 6),
            ("Finish", 2),
        ),
        level=3,
        name="Two loops over a 2D array",
        family=FAMILY,
        language="c",
        note=(
            "`grid[r][c]` is row r, column c. The inner loop runs all the "
            "way through for EACH turn of the outer one, so a row is printed "
            "and then the newline ends it - which means the newline belongs "
            "after the inner loop's closing brace but inside the outer one."
        ),
        code=(
            "#include <stdio.h>\n"
            "int main(void) {\n"
            "    int grid[2][3] = { { 1, 2, 3 }, { 4, 5, 6 } };\n"
            "    for (int r = 0; r < 2; r++) {\n"
            "        for (int c = 0; c < 3; c++) {\n"
            "            printf(\"%d\", grid[r][c] * 10);\n"
            "        }\n"
            "        printf(\"\\n\");\n"
            "    }\n"
            "    return 0;\n"
            "}"
        ),
        expect="102030\n405060",
    ),
    _m(
        id="magnet-c-struct-pointer",
        plan=(
            ("Bring in printf and describe a player", 2),
            ("A function that changes the player it points to", 3),
            ("Make one, change it, show it", 6),
        ),
        level=3,
        name="Changing a struct through a pointer",
        family=FAMILY,
        language="c",
        note=(
            "C passes everything by value, so a function given a struct gets "
            "a copy. Handing it `&hero` - the address - lets it change the "
            "real one, and `p->score` reaches the field through the pointer. "
            "The struct type has to be declared above anything that names it."
        ),
        code=(
            "#include <stdio.h>\n"
            "struct player { const char *name; int score; };\n"
            "static void bonus(struct player *p) {\n"
            "    p->score += 50;\n"
            "}\n"
            "int main(void) {\n"
            "    struct player hero = { \"Ada\", 100 };\n"
            "    bonus(&hero);\n"
            "    printf(\"%s %d\\n\", hero.name, hero.score);\n"
            "    return 0;\n"
            "}"
        ),
        expect="Ada 150",
    ),
    _m(
        id="magnet-c-malloc",
        plan=(
            ("Bring in printf and malloc", 2),
            ("Ask for room for some numbers", 4),
            ("Fill and add them", 3),
            ("Hand the memory back and finish", 3),
        ),
        level=4,
        name="malloc, use, free",
        family=FAMILY,
        language="c",
        note=(
            "malloc asks for memory at runtime and can fail, so its result is "
            "checked before use. The memory is yours until you `free` it - "
            "and free has to come after the last use, never before: reading "
            "freed memory is one of the classic C bugs. Every malloc wants "
            "exactly one free."
        ),
        code=(
            "#include <stdio.h>\n"
            "#include <stdlib.h>\n"
            "int main(void) {\n"
            "    int count = 4;\n"
            "    int *nums = malloc(count * sizeof *nums);\n"
            "    if (nums == NULL) return 1;\n"
            "    int total = 0;\n"
            "    for (int i = 0; i < count; i++) { nums[i] = i + 1; total += nums[i]; }\n"
            "    printf(\"%d\\n\", total);\n"
            "    free(nums);\n"
            "    return 0;\n"
            "}"
        ),
        expect="10",
    ),
    _m(
        id="magnet-c-linked-list",
        plan=(
            ("Bring in printf and describe a node", 2),
            ("Open main with two linked nodes", 3),
            ("Follow the links to the end", 3),
            ("Finish", 3),
        ),
        level=4,
        name="Walking a linked list",
        family=FAMILY,
        language="c",
        note=(
            "Each node holds a value and a pointer to the next node; the last "
            "one's next is NULL. The second node must be made before the "
            "first, because the first points at it. The walk follows `next` "
            "until it hits NULL, and the line that moves along goes after the "
            "line that prints, or the first value is skipped."
        ),
        code=(
            "#include <stdio.h>\n"
            "struct node { int value; struct node *next; };\n"
            "int main(void) {\n"
            "    struct node b = { 20, NULL };\n"
            "    struct node a = { 10, &b };\n"
            "    for (struct node *at = &a; at != NULL; at = at->next) {\n"
            "        printf(\"%d \", at->value);\n"
            "    }\n"
            "    printf(\"end\\n\");\n"
            "    return 0;\n"
            "}"
        ),
        expect="10 20 end",
    ),
    _m(
        id="magnet-c-build-string",
        plan=(
            ("Bring in printf and open main", 2),
            ("A buffer and the word to flip", 2),
            ("Copy it in backwards", 4),
            ("Show it and finish", 3),
        ),
        level=5,
        name="Building a string in a buffer",
        family=FAMILY,
        language="c",
        note=(
            "A C string is chars ending in '\\0', and nothing adds that end "
            "for you when you fill a buffer by hand: forget the line that "
            "writes it and printf runs on past the letters. The loop copies "
            "from the far end of the word to the near end of the buffer, so "
            "it needs the length first."
        ),
        code=(
            "#include <stdio.h>\n"
            "int main(void) {\n"
            "    const char *word = \"stressed\";\n"
            "    char out[16];\n"
            "    int len = 0;\n"
            "    while (word[len] != '\\0') len++;\n"
            "    for (int i = 0; i < len; i++) out[i] = word[len - 1 - i];\n"
            "    out[len] = '\\0';\n"
            "    printf(\"%s\\n\", out);\n"
            "    return 0;\n"
            "}"
        ),
        expect="desserts",
    ),
)
