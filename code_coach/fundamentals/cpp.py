"""C++ fundamentals — C's types with the standard library on top."""

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
    description="Types, streams, and the containers you'll actually use.",
    snippets=(
        _s("#include <iostream>", "Brings in cout and cin."),
        _s("#include <vector>", "The growable array — your default container."),
        _s("#include <string>", "std::string, not C's char arrays."),
        _s("using namespace std;", "Saves typing std:: everywhere. Fine for practice."),
        _s("int count = 0;", "Types come first, as in C."),
        _s("double price = 4.99;", "Decimals."),
        _s("bool isReady = true;", "C++ has a real bool."),
        _s("string name = \"Alex\";", "Double quotes. It manages its own memory."),
        _s("auto total = 0;", "`auto` infers the type from the value."),
        _s("cout << \"Hello, world!\" << endl;", "`<<` chains; endl adds a newline."),
        _s("cout << count << endl;", "Streams print any type they know.", 2),
        _s("vector<int> nums = {1, 2, 3};", "A vector knows its own size.", 2),
        _s("nums.push_back(4);", "Append — it grows for you.", 2),
        _s("cout << nums.size() << endl;", "size() is a method, unlike C.", 2),
        _s("cout << nums[0] << endl;", "Index from zero.", 2),
        _s("map<string, int> counts;", "An ordered key/value container.", 2),
        _s("set<int> seen;", "No duplicates, kept sorted.", 2),
        _s(
            "vector<int> nums = {1, 2, 3};\ncout << nums.size() << endl;",
            "Build a container, then ask it something.",
            3,
        ),
        _s(
            "int doubleIt(int n) {\n    return n * 2;\n}",
            "Return type, name, parameters, body.",
            4,
        ),
        _s(
            "int add(int a, int b) {\n    return a + b;\n}",
            "Each parameter needs its own type.",
            4,
        ),
        _s(
            "void greet(const string& name) {\n"
            "    cout << \"Hello, \" << name << endl;\n}",
            "`const string&` avoids copying the string.",
            4,
        ),
        _s(
            "#include <iostream>\nusing namespace std;\n\nint main() {\n"
            "    cout << \"Hello, world!\" << endl;\n    return 0;\n}",
            "Every C++ program starts at main.",
            5,
        ),
        _s(
            "#include <iostream>\nusing namespace std;\n\nint add(int a, int b) {\n"
            "    return a + b;\n}\n\nint main() {\n    cout << add(7, 12) << endl;\n"
            "    return 0;\n}",
            "Define above main so the compiler has seen it.",
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
        _s("if (count == 0) {", "`==` compares; `=` assigns."),
        _s("if (name != \"Alex\") {", "std::string compares with == and != directly."),
        _s("} else {", "The other branch."),
        _s("} else if (score > 50) {", "Chain another test on."),
        _s("if (a > 0 && b > 0) {", "`&&` needs both sides true.", 2),
        _s("if (a == 0 || b == 0) {", "`||` needs only one.", 2),
        _s("if (!found) {", "`!` flips a bool.", 2),
        _s("int best = a > b ? a : b;", "The ternary.", 2),
        _s("if (counts.count(key) > 0) {", "`count` asks whether a key is present.", 2),
        _s(
            "if (score > 50) {\n    cout << \"pass\" << endl;\n}",
            "Braces hold what runs when it's true.",
            3,
        ),
        _s(
            "if (score > 50) {\n    cout << \"pass\" << endl;\n} else {\n"
            "    cout << \"fail\" << endl;\n}",
            "One branch or the other.",
            4,
        ),
        _s(
            "#include <iostream>\nusing namespace std;\n\nbool isEven(int n) {\n"
            "    return n % 2 == 0;\n}\n\nint main() {\n"
            "    cout << isEven(4) << endl;\n    return 0;\n}",
            "A bool prints as 1 or 0 unless you ask for boolalpha.",
            5,
        ),
        _s(
            "#include <iostream>\nusing namespace std;\n\nint biggest(int a, int b) {\n"
            "    if (a > b) {\n        return a;\n    }\n    return b;\n}\n\n"
            "int main() {\n    cout << biggest(3, 9) << endl;\n    return 0;\n}",
            "No else needed: returning already left the function.",
            5,
        ),
    ),
)


_LOOPS = FundamentalsClass(
    id="loops",
    name="Loops",
    description="Repeating work over vectors and ranges.",
    snippets=(
        _s("for (int i = 0; i < 5; i++) {", "Start, keep-going test, step."),
        _s("for (int n : nums) {", "The range-for walks values directly."),
        _s("while (count > 0) {", "Repeat while the condition holds."),
        _s("count++;", "Add one."),
        _s("total += n;", "Shorthand for total = total + n.", 2),
        _s("break;", "Leave the loop immediately.", 2),
        _s("continue;", "Skip to the next turn.", 2),
        _s("for (auto& pair : counts) {", "Walk a map; `&` avoids copying.", 2),
        _s("sort(nums.begin(), nums.end());", "Sorting takes a range, not a container.", 2),
        _s(
            "for (int n : nums) {\n    cout << n << endl;\n}",
            "The loop you'll reach for most.",
            3,
        ),
        _s(
            "int total = 0;\nfor (int n : nums) {\n    total += n;\n}",
            "An accumulator: start empty, add as you go.",
            4,
        ),
        _s(
            "for (int r = 0; r < 3; r++) {\n    for (int c = 0; c < 3; c++) {\n"
            "        cout << r << \",\" << c << endl;\n    }\n}",
            "Nested loops walk a grid.",
            4,
        ),
        _s(
            "#include <iostream>\n#include <vector>\nusing namespace std;\n\n"
            "int sum(vector<int>& nums) {\n    int total = 0;\n"
            "    for (int n : nums) {\n        total += n;\n    }\n    return total;\n}\n\n"
            "int main() {\n    vector<int> nums = {1, 2, 3};\n"
            "    cout << sum(nums) << endl;\n    return 0;\n}",
            "A vector carries its own length, unlike a C array.",
            5,
        ),
        _s(
            "#include <iostream>\nusing namespace std;\n\nint main() {\n"
            "    int count = 3;\n    while (count > 0) {\n"
            "        cout << count << endl;\n        count--;\n    }\n    return 0;\n}",
            "Something inside must change, or it never ends.",
            5,
        ),
    ),
)


register(
    FundamentalsBank(language="cpp", classes=(_FOUNDATIONS, _DECISIONS, _LOOPS))
)
