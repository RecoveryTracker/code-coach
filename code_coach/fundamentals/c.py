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
        _s(
            "#include <stdio.h>\n"
            "\n"
            "int add(int a, int b) {\n"
            "    return a + b;\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%d\\n\", add(7, 12));\n"
            "    return 0;\n"
            "}",
            "Declare the return type first, then the name, then the parameters.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "\n"
            "double average(int a, int b) {\n"
            "    return (a + b) / 2.0;\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%.1f\\n\", average(3, 4));\n"
            "    return 0;\n"
            "}",
            "2.0 rather than 2, or integer division truncates the answer.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "\n"
            "void greet(const char *name) {\n"
            "    printf(\"Hello, %s!\\n\", name);\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    greet(\"Alex\");\n"
            "    return 0;\n"
            "}",
            "const char * is a string you promise not to write through.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "#include <string.h>\n"
            "\n"
            "int length(const char *text) {\n"
            "    return (int)strlen(text);\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%d\\n\", length(\"hello\"));\n"
            "    return 0;\n"
            "}",
            "strlen counts up to the zero byte, so it walks the whole string.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "\n"
            "void swap(int *a, int *b) {\n"
            "    int temp = *a;\n"
            "    *a = *b;\n"
            "    *b = temp;\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    int x = 1, y = 2;\n"
            "    swap(&x, &y);\n"
            "    printf(\"%d %d\\n\", x, y);\n"
            "    return 0;\n"
            "}",
            "Passing the address is the only way to change a caller's variable.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "\n"
            "struct Point {\n"
            "    int x;\n"
            "    int y;\n"
            "};\n"
            "\n"
            "int main(void) {\n"
            "    struct Point p = {1, 2};\n"
            "    printf(\"%d,%d\\n\", p.x, p.y);\n"
            "    return 0;\n"
            "}",
            "A struct groups values; the fields are laid out in order.",
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
        _s(
            "#include <stdio.h>\n"
            "\n"
            "char grade(int score) {\n"
            "    if (score >= 90) return 'A';\n"
            "    if (score >= 80) return 'B';\n"
            "    return 'C';\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%c\\n\", grade(85));\n"
            "    return 0;\n"
            "}",
            "A char is a single quote; a string is a double quote.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "\n"
            "int is_even(int n) {\n"
            "    return n % 2 == 0;\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%d\\n\", is_even(7));\n"
            "    return 0;\n"
            "}",
            "C has no bool by default: 0 is false, anything else is true.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "\n"
            "int larger(int a, int b) {\n"
            "    return a > b ? a : b;\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%d\\n\", larger(3, 9));\n"
            "    return 0;\n"
            "}",
            "The ternary is an expression, so it can be returned directly.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "\n"
            "int can_vote(int age, int citizen) {\n"
            "    return age >= 18 && citizen;\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%d\\n\", can_vote(20, 1));\n"
            "    return 0;\n"
            "}",
            "&& stops as soon as the answer is known.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "\n"
            "const char *day_type(int day) {\n"
            "    switch (day) {\n"
            "        case 6:\n"
            "        case 7:\n"
            "            return \"weekend\";\n"
            "        default:\n"
            "            return \"weekday\";\n"
            "    }\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%s\\n\", day_type(7));\n"
            "    return 0;\n"
            "}",
            "Empty cases fall through to the next one on purpose.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "\n"
            "int clamp(int n, int low, int high) {\n"
            "    if (n < low) return low;\n"
            "    if (n > high) return high;\n"
            "    return n;\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%d\\n\", clamp(15, 0, 10));\n"
            "    return 0;\n"
            "}",
            "Three cases, three returns, and no nesting.",
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
        _s(
            "#include <stdio.h>\n"
            "\n"
            "int sum(const int *nums, int count) {\n"
            "    int total = 0;\n"
            "    for (int i = 0; i < count; i++) {\n"
            "        total += nums[i];\n"
            "    }\n"
            "    return total;\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    int nums[4] = {1, 2, 3, 4};\n"
            "    printf(\"%d\\n\", sum(nums, 4));\n"
            "    return 0;\n"
            "}",
            "An array loses its length when passed, so the count comes too.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "\n"
            "int biggest(const int *nums, int count) {\n"
            "    int best = nums[0];\n"
            "    for (int i = 1; i < count; i++) {\n"
            "        if (nums[i] > best) best = nums[i];\n"
            "    }\n"
            "    return best;\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    int nums[3] = {3, 9, 4};\n"
            "    printf(\"%d\\n\", biggest(nums, 3));\n"
            "    return 0;\n"
            "}",
            "Start from the first element, not from zero, or negatives break it.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "\n"
            "int factorial(int n) {\n"
            "    int result = 1;\n"
            "    while (n > 1) {\n"
            "        result *= n;\n"
            "        n--;\n"
            "    }\n"
            "    return result;\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%d\\n\", factorial(5));\n"
            "    return 0;\n"
            "}",
            "A while loop when the count is not a simple range.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "\n"
            "int count_vowels(const char *text) {\n"
            "    int found = 0;\n"
            "    for (int i = 0; text[i] != '\\0'; i++) {\n"
            "        if (text[i] == 'a' || text[i] == 'e') found++;\n"
            "    }\n"
            "    return found;\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    printf(\"%d\\n\", count_vowels(\"beach\"));\n"
            "    return 0;\n"
            "}",
            "Walking to the zero byte is how you loop over a C string.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "\n"
            "int first_negative(const int *nums, int count) {\n"
            "    for (int i = 0; i < count; i++) {\n"
            "        if (nums[i] < 0) return nums[i];\n"
            "    }\n"
            "    return 0;\n"
            "}\n"
            "\n"
            "int main(void) {\n"
            "    int nums[4] = {3, 1, -2, 5};\n"
            "    printf(\"%d\\n\", first_negative(nums, 4));\n"
            "    return 0;\n"
            "}",
            "Returning from inside the loop is the cleanest early exit.",
            5,
        ),
        _s(
            "#include <stdio.h>\n"
            "\n"
            "int main(void) {\n"
            "    for (int i = 1; i <= 3; i++) {\n"
            "        for (int j = 1; j <= 3; j++) {\n"
            "            printf(\"%d\", i * j);\n"
            "        }\n"
            "    }\n"
            "    printf(\"\\n\");\n"
            "    return 0;\n"
            "}",
            "Nested loops: the inner one runs fully for every outer turn.",
            5,
        ),
    ),
)


register(
    FundamentalsBank(language="c", classes=(_FOUNDATIONS, _DECISIONS, _LOOPS))
)
