"""C++ code magnets.

Ten whole programs of at most twelve lines, in the shapes where C++ makes
the order matter: a declaration before its use, a class before main, an
`#include` before what it provides, a read after the update it should see,
and a destructor that runs by itself when a scope ends. Some lines are free
on purpose (two independent includes, map insertions that the map sorts
anyway) so the marker, which runs what you arranged, accepts every order
that works rather than the author's.

Everything is deterministic and portable: no `time`, no unordered
containers printed, no undefined behaviour, C++17 (g++, clang++ or MSVC).
The `expect` of each was worked out by hand and is held to what the real
compiler's build prints by tests/test_magnets_cpp.py.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m

FAMILY = "C++"


def _code(*lines: str) -> str:
    return "\n".join(lines)


CPP_MAGNETS: tuple[Magnet, ...] = (
    _m(
        id="magnet-cpp-vector-push",
        plan=(
            ("Bring in the library pieces", 2),
            ("Open main with an empty vector", 2),
            ("Add two numbers", 2),
            ("Print each one", 3),
            ("Close main", 1),
        ),
        level=1,
        name="A vector and a range-for",
        family=FAMILY,
        language="cpp",
        note=(
            "`std::vector` lives in `<vector>` and `std::cout` in "
            "`<iostream>`, so both are included before main uses them. The "
            "vector has to be declared before `push_back` is called on it, "
            "and the range-for has to come after the pushes or it walks an "
            "empty vector and prints nothing. The pushes keep the order "
            "they are written in, so 3 comes out before 5."
        ),
        code=_code(
            "#include <iostream>",
            "#include <vector>",
            "int main() {",
            "    std::vector<int> v;",
            "    v.push_back(3);",
            "    v.push_back(5);",
            "    for (int x : v) {",
            "        std::cout << x << \"\\n\";",
            "    }",
            "}",
        ),
        expect="3\n5",
    ),
    _m(
        id="magnet-cpp-string-concat",
        plan=(
            ("Bring in the library pieces", 2),
            ("Open main", 1),
            ("Two parts of a name", 2),
            ("Join them", 1),
            ("Show it and its length", 2),
            ("Close main", 1),
        ),
        level=1,
        name="Joining strings and asking size",
        family=FAMILY,
        language="cpp",
        note=(
            "`+` on a `std::string` builds a new string, but only from "
            "variables that already exist: `full` cannot be built above the "
            "lines that declare `first` and `last`. `size()` counts "
            "characters, here 3 + 1 + 8 = 12, and it is printed after the "
            "text because that is how the two lines were written."
        ),
        code=_code(
            "#include <iostream>",
            "#include <string>",
            "int main() {",
            "    std::string first = \"Ada\";",
            "    std::string last = \"Lovelace\";",
            "    std::string full = first + \" \" + last;",
            "    std::cout << full << \"\\n\";",
            "    std::cout << full.size() << \"\\n\";",
            "}",
        ),
        expect="Ada Lovelace\n12",
    ),
    _m(
        id="magnet-cpp-function-before-main",
        plan=(
            ("Bring in iostream", 1),
            ("A function that squares", 3),
            ("Open main", 1),
            ("Call it twice", 2),
            ("Close main", 1),
        ),
        level=2,
        name="A function declared before main",
        family=FAMILY,
        language="cpp",
        note=(
            "C++ reads top to bottom and a name must be known before it is "
            "used, so `square` has to be defined above `main`; put main "
            "first and the compiler says `square` was not declared. "
            "Inside the output line, `square(4)` is 16 and `square(2)` is "
            "4, added to give 20."
        ),
        code=_code(
            "#include <iostream>",
            "int square(int n) {",
            "    return n * n;",
            "}",
            "int main() {",
            "    int a = square(4);",
            "    std::cout << a + square(2) << \"\\n\";",
            "}",
        ),
        expect="20",
    ),
    _m(
        id="magnet-cpp-class-constructor",
        plan=(
            ("Bring in iostream", 1),
            ("Open the class with its fields", 3),
            ("A constructor and a read-only method", 2),
            ("Close the class", 1),
            ("Build one and ask its area", 4),
        ),
        level=2,
        name="A class with a constructor",
        family=FAMILY,
        language="cpp",
        note=(
            "A class must be complete before main builds one. Members are "
            "private until `public:`, so the constructor and `area` must "
            "come after it or main cannot call them. The `const` after "
            "`area()` promises it does not change the box, and the `;` "
            "after the closing brace is required. 3 * 4 is 12."
        ),
        code=_code(
            "#include <iostream>",
            "class Box {",
            "public:",
            "    int w, h;",
            "    Box(int a, int b) : w(a), h(b) {}",
            "    int area() const { return w * h; }",
            "};",
            "int main() {",
            "    Box b(3, 4);",
            "    std::cout << b.area() << \"\\n\";",
            "}",
        ),
        expect="12",
    ),
    _m(
        id="magnet-cpp-reference-param",
        plan=(
            ("Bring in iostream", 1),
            ("A function that changes its argument", 3),
            ("Open main with a number", 2),
            ("Bump it and show it", 2),
            ("Bump it again and show it", 2),
            ("Close main", 1),
        ),
        level=3,
        name="A reference changing the caller",
        family=FAMILY,
        language="cpp",
        note=(
            "`int& n` is another name for the caller's variable, so "
            "`n += 10` changes `x` itself, with no return value. A plain "
            "`int n` would change a copy. Each print shows what `x` holds "
            "at that moment, so a print only sees the bumps written above "
            "it: 5 becomes 15, then 25."
        ),
        code=_code(
            "#include <iostream>",
            "void bump(int& n) {",
            "    n += 10;",
            "}",
            "int main() {",
            "    int x = 5;",
            "    bump(x);",
            "    std::cout << x << \"\\n\";",
            "    bump(x);",
            "    std::cout << x << \"\\n\";",
            "}",
        ),
        expect="15\n25",
    ),
    _m(
        id="magnet-cpp-map-count",
        plan=(
            ("Bring in the library pieces", 3),
            ("Open main with an empty map", 2),
            ("Count three words", 3),
            ("Print in key order", 1),
            ("Close main", 1),
        ),
        level=3,
        name="A map counting words",
        family=FAMILY,
        language="cpp",
        note=(
            "`count[word]++` creates the entry at 0 if it is missing and "
            "then adds one, so \"pear\" ends at 2. A `std::map` keeps its "
            "keys sorted, so the loop prints apple before pear whatever "
            "order the words were counted in. The loop must come after all "
            "three counts, or it prints a map that is still short."
        ),
        code=_code(
            "#include <iostream>",
            "#include <map>",
            "#include <string>",
            "int main() {",
            "    std::map<std::string, int> count;",
            "    count[\"pear\"]++;",
            "    count[\"apple\"]++;",
            "    count[\"pear\"]++;",
            "    for (auto& p : count) std::cout << p.first << \" \" << p.second << \"\\n\";",
            "}",
        ),
        expect="apple 1\npear 2",
    ),
    _m(
        id="magnet-cpp-sort-lambda",
        plan=(
            ("Bring in the library pieces", 3),
            ("Open main with four numbers", 2),
            ("Sort biggest first", 1),
            ("Print each one", 3),
            ("Close main", 1),
        ),
        level=4,
        name="std::sort with a lambda",
        family=FAMILY,
        language="cpp",
        note=(
            "`std::sort` takes a range and, optionally, a comparison; the "
            "lambda `a > b` says a goes before b when a is bigger, so the "
            "result runs from large to small. It sorts the vector in place, "
            "so the print loop only shows the new order if it comes after "
            "the sort; above it, it prints 3 9 1 7 untouched. `<vector>` "
            "and `<algorithm>` must be included above what uses them."
        ),
        code=_code(
            "#include <algorithm>",
            "#include <iostream>",
            "#include <vector>",
            "int main() {",
            "    std::vector<int> v = {3, 9, 1, 7};",
            "    std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });",
            "    for (int x : v) {",
            "        std::cout << x << \"\\n\";",
            "    }",
            "}",
        ),
        expect="9\n7\n3\n1",
    ),
    _m(
        id="magnet-cpp-structured-bindings",
        plan=(
            ("Bring in the library pieces", 2),
            ("Open main with an empty map", 2),
            ("Add three grades", 3),
            ("Walk the map and unpack each pair", 3),
            ("Close main", 1),
        ),
        level=4,
        name="Auto and structured bindings",
        family=FAMILY,
        language="cpp",
        note=(
            "`const auto& [score, letter]` unpacks each key and value of "
            "the map into two names, and `auto` lets the compiler work out "
            "the pair type. A `std::map` walks its keys in ascending order, "
            "so the three grades come out 70, 80, 90 however they were "
            "added; the loop only has to come after all three. Structured "
            "bindings need C++17."
        ),
        code=_code(
            "#include <iostream>",
            "#include <map>",
            "int main() {",
            "    std::map<int, char> grade;",
            "    grade[90] = 'A';",
            "    grade[70] = 'C';",
            "    grade[80] = 'B';",
            "    for (const auto& [score, letter] : grade) {",
            "        std::cout << score << letter << \"\\n\";",
            "    }",
            "}",
        ),
        expect="70C\n80B\n90A",
    ),
    _m(
        id="magnet-cpp-unique-ptr",
        plan=(
            ("Bring in the library pieces", 2),
            ("A struct that announces itself", 4),
            ("Open main and own one", 2),
            ("Walk, then main ends", 2),
        ),
        level=5,
        name="A unique_ptr owning an object",
        family=FAMILY,
        language="cpp",
        note=(
            "`std::make_unique<Dog>()` builds the object, running the "
            "constructor, and the `unique_ptr` owns it. When `main` ends "
            "the pointer goes out of scope and the destructor runs by "
            "itself, with no delete written anywhere, so \"gone\" prints "
            "last. The struct must be defined above main, `<memory>` "
            "included above its use, and the creation line sits before the "
            "\"walk\" line to print born first."
        ),
        code=_code(
            "#include <iostream>",
            "#include <memory>",
            "struct Dog {",
            "    Dog() { std::cout << \"born\\n\"; }",
            "    ~Dog() { std::cout << \"gone\\n\"; }",
            "};",
            "int main() {",
            "    auto d = std::make_unique<Dog>();",
            "    std::cout << \"walk\\n\";",
            "}",
        ),
        expect="born\nwalk\ngone",
    ),
    _m(
        id="magnet-cpp-overload",
        plan=(
            ("Bring in the library pieces", 2),
            ("One name for an int", 1),
            ("One name for a string", 1),
            ("Open main", 1),
            ("Call with three different arguments", 3),
            ("Close main", 1),
        ),
        level=5,
        name="Overloads chosen by argument type",
        family=FAMILY,
        language="cpp",
        note=(
            "Two functions share the name `show`; the compiler picks one "
            "from the argument's type: `7` and `7 + 1` are int, the "
            "`std::string` is the other. Both overloads must be declared "
            "above main, because a call only sees the declarations before "
            "it. The calls run in the order written, so the output follows "
            "their order: int 7, then the string, then int 8."
        ),
        code=_code(
            "#include <iostream>",
            "#include <string>",
            "void show(int n) { std::cout << \"int \" << n << \"\\n\"; }",
            "void show(const std::string& s) { std::cout << \"string \" << s << \"\\n\"; }",
            "int main() {",
            "    show(7);",
            "    show(std::string(\"seven\"));",
            "    show(7 + 1);",
            "}",
        ),
        expect="int 7\nstring seven\nint 8",
    ),
)
