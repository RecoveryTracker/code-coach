"""C fundamentals — types you declare, memory you can see."""

from __future__ import annotations

from code_coach.fundamentals.base import (
    FundamentalsBank,
    FundamentalsClass,
    Snippet,
    register,
)


def _s(code: str, tip: str, level: int = 1) -> Snippet:
    return Snippet(code=code, tip=tip, level=level)


_FOUNDATIONS = FundamentalsClass(
    id="foundations",
    name="Foundations",
    description="Declaring types, printing, and your first functions.",
    snippets=(
        _s("#include <stdio.h>", "Brings in printf. Nothing works without it."),
        _s("int count = 0;", "Every variable states its type first."),
        _s("int age = 30;", "Whole numbers."),
        _s("double price = 4.99;", "Decimals. An int would drop the .99."),
        _s("char letter = 'A';", "A single character, in single quotes."),
        _s("char name[] = \"Alex\";", "A string is an array of characters."),
        _s('printf("Hello, world!\\n");', "`\\n` is the newline — printf won't add one."),
        _s('printf("%d\\n", count);', "%d is the placeholder for an int."),
        _s('printf("%s\\n", name);', "%s for a string."),
        _s('printf("%.2f\\n", price);', "%.2f prints two decimal places.", 2),
        _s("int nums[3] = {1, 2, 3};", "An array has a fixed size, decided now.", 2),
        _s("nums[0] = 5;", "Index from zero.", 2),
        _s("int n = sizeof(nums) / sizeof(nums[0]);",
           "C won't tell you a length — you work it out.", 2),
        _s("int *p = &nums[0];", "`&` takes an address; `*` says this holds one.", 2),
        _s("total = total + n;", "No shorthand needed, though += works.", 2),
        _s(
            "int count = 0;\nprintf(\"%d\\n\", count);",
            "Declare, then print.",
            3,
        ),
        _s(
            "int double_it(int n) {\n    return n * 2;\n}",
            "Return type, name, parameters, body.",
            4,
        ),
        _s(
            "int add(int a, int b) {\n    return a + b;\n}",
            "Each parameter needs its own type.",
            4,
        ),
        _s(
            "void greet(void) {\n    printf(\"Hello!\\n\");\n}",
            "`void` twice: returns nothing, takes nothing.",
            4,
        ),
        _s(
            "#include <stdio.h>\n\nint main(void) {\n    printf(\"Hello, world!\\n\");\n"
            "    return 0;\n}",
            "Every C program starts at main and returns 0 for success.",
            5,
        ),
        _s(
            "#include <stdio.h>\n\nint add(int a, int b) {\n    return a + b;\n}\n\n"
            "int main(void) {\n    printf(\"%d\\n\", add(7, 12));\n    return 0;\n}",
            "Define above main, or C won't know the function exists yet.",
            5,
        ),
    ),
)


_DECISIONS = FundamentalsClass(
    id="decisions",
    name="Decisions",
    description="Comparing values and branching on the answer.",
    snippets=(
        _s("if (age > 18) {", "The condition goes in parentheses."),
        _s("if (count == 0) {", "`==` compares; a single `=` assigns and compiles."),
        _s("if (n != 0) {", "`!=` is 'not equal to'."),
        _s("} else {", "The other branch."),
        _s("} else if (score > 50) {", "Chain another test on."),
        _s("if (a > 0 && b > 0) {", "`&&` needs both sides true.", 2),
        _s("if (a == 0 || b == 0) {", "`||` needs only one.", 2),
        _s("if (!found) {", "`!` flips it. Zero is false, anything else is true.", 2),
        _s("int max = a > b ? a : b;", "The ternary: condition ? this : that.", 2),
        _s(
            "if (score > 50) {\n    printf(\"pass\\n\");\n}",
            "Braces hold everything that runs when it's true.",
            3,
        ),
        _s(
            "if (score > 50) {\n    printf(\"pass\\n\");\n} else {\n"
            "    printf(\"fail\\n\");\n}",
            "One branch or the other.",
            4,
        ),
        _s(
            "switch (grade) {\n    case 'A':\n        printf(\"great\\n\");\n"
            "        break;\n    default:\n        printf(\"ok\\n\");\n}",
            "Without `break` it falls through to the next case.",
            4,
        ),
        _s(
            "#include <stdio.h>\n\nint is_even(int n) {\n    return n % 2 == 0;\n}\n\n"
            "int main(void) {\n    printf(\"%d\\n\", is_even(4));\n    return 0;\n}",
            "C has no bool by default — 1 and 0 do the job.",
            5,
        ),
        _s(
            "#include <stdio.h>\n\nint biggest(int a, int b) {\n    if (a > b) {\n"
            "        return a;\n    }\n    return b;\n}\n\nint main(void) {\n"
            "    printf(\"%d\\n\", biggest(3, 9));\n    return 0;\n}",
            "No else needed: returning already left the function.",
            5,
        ),
    ),
)


_LOOPS = FundamentalsClass(
    id="loops",
    name="Loops",
    description="Repeating work, and walking arrays by index.",
    snippets=(
        _s("for (int i = 0; i < 5; i++) {", "Start, keep-going test, step."),
        _s("while (count > 0) {", "Repeat while the condition holds."),
        _s("count++;", "Add one. `count--` takes one away."),
        _s("total += nums[i];", "Reach into the array by index.", 2),
        _s("break;", "Leave the loop immediately.", 2),
        _s("continue;", "Skip to the next turn.", 2),
        _s("for (int i = n - 1; i >= 0; i--) {", "Counting down.", 2),
        _s("do {", "A do-while runs its body before testing.", 2),
        _s(
            "for (int i = 0; i < 3; i++) {\n    printf(\"%d\\n\", i);\n}",
            "The loop you'll write most often in C.",
            3,
        ),
        _s(
            "int total = 0;\nfor (int i = 0; i < n; i++) {\n    total += nums[i];\n}",
            "An accumulator over an array.",
            4,
        ),
        _s(
            "for (int r = 0; r < 3; r++) {\n    for (int c = 0; c < 3; c++) {\n"
            "        printf(\"%d,%d\\n\", r, c);\n    }\n}",
            "Nested loops walk a grid.",
            4,
        ),
        _s(
            "#include <stdio.h>\n\nint sum(int nums[], int n) {\n    int total = 0;\n"
            "    for (int i = 0; i < n; i++) {\n        total += nums[i];\n    }\n"
            "    return total;\n}\n\nint main(void) {\n    int nums[3] = {1, 2, 3};\n"
            "    printf(\"%d\\n\", sum(nums, 3));\n    return 0;\n}",
            "An array parameter loses its length, so pass it alongside.",
            5,
        ),
        _s(
            "#include <stdio.h>\n\nint main(void) {\n    int count = 3;\n"
            "    while (count > 0) {\n        printf(\"%d\\n\", count);\n"
            "        count--;\n    }\n    return 0;\n}",
            "Something inside must change, or it never ends.",
            5,
        ),
    ),
)


register(
    FundamentalsBank(language="c", classes=(_FOUNDATIONS, _DECISIONS, _LOOPS))
)
