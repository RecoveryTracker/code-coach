"""Predict the output, in C++.

C++ keeps C's honesty about the machine and adds its own surprises: a map's
square brackets INSERT a key that was not there, a range-for copies unless
you ask for a reference, a char added to a number is a number, objects are
destroyed in the reverse order they were made, and `auto` can deduce a
different type than the one you pictured. Every program here is well-defined
and compiles cleanly; tests/test_predict_more.py checks every answer against
the compiler.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p

FAMILY = "C++"


CPP_PUZZLES: tuple[Puzzle, ...] = (
    _p(
        id="predict-cpp-int-division",
        level=1,
        language="cpp",
        name="Dividing whole numbers",
        family=FAMILY,
        code=(
            "#include <iostream>\n"
            "\n"
            "int main() {\n"
            "    std::cout << 7 / 2 << \" \" << 7 % 2 << \" \" << 7 / 2.0 << \"\\n\";\n"
            "    return 0;\n"
            "}"
        ),
        expect="3 1 3.5",
        why=(
            "Two ints divide to an int and the fraction is dropped, so 7 / 2 is 3, "
            "and 7 % 2 is the 1 left over. Make either side a double - 2.0 - and "
            "the division is done in doubles: 3.5. std::cout prints a double "
            "without trailing zeros, so 3.5 rather than 3.500000."
        ),
    ),
    _p(
        id="predict-cpp-char-plus-int",
        level=1,
        language="cpp",
        name="A letter plus one",
        family=FAMILY,
        code=(
            "#include <iostream>\n"
            "\n"
            "int main() {\n"
            "    char c = 'A';\n"
            "    std::cout << c << \" \" << c + 1 << \" \" << char(c + 1) << \"\\n\";\n"
            "    return 0;\n"
            "}"
        ),
        expect="A 66 B",
        why=(
            "A char prints as a letter. But c + 1 is arithmetic, and arithmetic on "
            "a char happens in int, so the result is the int 66 - the code for B - "
            "and an int prints as a number. Casting back with char(...) makes it a "
            "letter again."
        ),
    ),
    _p(
        id="predict-cpp-reference",
        level=1,
        language="cpp",
        name="A reference is another name",
        family=FAMILY,
        code=(
            "#include <iostream>\n"
            "\n"
            "int main() {\n"
            "    int a = 1;\n"
            "    int copy = a;\n"
            "    int& alias = a;\n"
            "    copy = 5;\n"
            "    alias = 9;\n"
            "    std::cout << a << \" \" << copy << \"\\n\";\n"
            "    return 0;\n"
            "}"
        ),
        expect="9 5",
        why=(
            "`int copy = a` makes a new int with a's value; changing it leaves a "
            "alone. `int& alias = a` makes no new int at all - alias IS a, under "
            "another name - so assigning 9 to alias changes a."
        ),
    ),
    _p(
        id="predict-cpp-pass-by-value",
        level=2,
        language="cpp",
        name="A function gets a copy",
        family=FAMILY,
        code=(
            "#include <iostream>\n"
            "#include <vector>\n"
            "\n"
            "void addByValue(std::vector<int> v) { v.push_back(1); }\n"
            "void addByRef(std::vector<int>& v) { v.push_back(2); }\n"
            "\n"
            "int main() {\n"
            "    std::vector<int> nums;\n"
            "    addByValue(nums);\n"
            "    addByRef(nums);\n"
            "    std::cout << nums.size() << \" \" << nums[0] << \"\\n\";\n"
            "    return 0;\n"
            "}"
        ),
        expect="1 2",
        why=(
            "Passed by value, the function gets its own copy of the whole vector, "
            "pushes onto that, and the copy is thrown away when it returns. Passed "
            "by reference (&), it pushes onto main's vector. So only the 2 arrives."
        ),
    ),
    _p(
        id="predict-cpp-map-brackets",
        level=2,
        language="cpp",
        name="Looking a key up with []",
        family=FAMILY,
        code=(
            "#include <iostream>\n"
            "#include <map>\n"
            "#include <string>\n"
            "\n"
            "int main() {\n"
            "    std::map<std::string, int> ages;\n"
            "    ages[\"ada\"] = 36;\n"
            "    int bo = ages[\"bo\"];\n"
            "    std::cout << bo << \" \" << ages.size() << \" \" << ages.count(\"cy\") << \"\\n\";\n"
            "    return 0;\n"
            "}"
        ),
        expect="0 2 0",
        why=(
            "Reading ages[\"bo\"] does not just fail when bo is missing: [] INSERTS "
            "the key with a default value, 0 for an int, and gives you that. So the "
            "map now has two keys. count() only asks, and changes nothing, which is "
            "why cy is still 0 and not added."
        ),
    ),
    _p(
        id="predict-cpp-range-for-copy",
        level=2,
        language="cpp",
        name="A range-for that changes nothing",
        family=FAMILY,
        code=(
            "#include <iostream>\n"
            "#include <vector>\n"
            "\n"
            "int main() {\n"
            "    std::vector<int> v = {1, 2, 3};\n"
            "    for (int x : v) x *= 10;\n"
            "    for (int& x : v) x += 1;\n"
            "    std::cout << v[0] << \" \" << v[1] << \" \" << v[2] << \"\\n\";\n"
            "    return 0;\n"
            "}"
        ),
        expect="2 3 4",
        why=(
            "`for (int x : v)` hands the loop a copy of each item, so multiplying x "
            "multiplies the copy. `for (int& x : v)` hands it a reference to the "
            "real item, so adding 1 sticks. The first loop did nothing at all."
        ),
    ),
    _p(
        id="predict-cpp-string-size",
        level=2,
        language="cpp",
        name="Building a std::string",
        family=FAMILY,
        code=(
            "#include <iostream>\n"
            "#include <string>\n"
            "\n"
            "int main() {\n"
            "    std::string s = \"ab\";\n"
            "    s += 'c';\n"
            "    s = s + s;\n"
            "    std::cout << s << \" \" << s.size() << \" \" << s.find('c') << \"\\n\";\n"
            "    return 0;\n"
            "}"
        ),
        expect="abcabc 6 2",
        why=(
            "+= with a char appends it, and s + s joins two strings. find returns "
            "the position of the FIRST match, counting from 0, so the c at index 2, "
            "not the one at 5."
        ),
    ),
    _p(
        id="predict-cpp-sort-vector",
        level=3,
        language="cpp",
        name="Sorting with a comparator",
        family=FAMILY,
        code=(
            "#include <algorithm>\n"
            "#include <iostream>\n"
            "#include <vector>\n"
            "\n"
            "int main() {\n"
            "    std::vector<int> v = {10, 9, 100, 1};\n"
            "    std::sort(v.begin(), v.end());\n"
            "    std::cout << v.front() << \" \" << v.back() << \" \";\n"
            "    std::sort(v.begin(), v.end(), [](int a, int b) { return a > b; });\n"
            "    std::cout << v.front() << \"\\n\";\n"
            "    return 0;\n"
            "}"
        ),
        expect="1 100 100",
        why=(
            "std::sort compares ints as numbers - not as text, which is the "
            "JavaScript trap - so smallest first: 1 ... 100. The lambda says 'a "
            "comes first when it is bigger', which turns the order round, so the "
            "front is then 100."
        ),
    ),
    _p(
        id="predict-cpp-pre-post-increment",
        level=3,
        language="cpp",
        name="i++ and ++i",
        family=FAMILY,
        code=(
            "#include <iostream>\n"
            "\n"
            "int main() {\n"
            "    int i = 5;\n"
            "    int a = i++;\n"
            "    int b = ++i;\n"
            "    std::cout << a << \" \" << b << \" \" << i << \"\\n\";\n"
            "    return 0;\n"
            "}"
        ),
        expect="5 7 7",
        why=(
            "i++ hands back the OLD value and then adds one: a gets 5, i becomes 6. "
            "++i adds one first and hands back the NEW value: i becomes 7 and so "
            "does b. Each is its own statement, so there is no doubt about order."
        ),
    ),
    _p(
        id="predict-cpp-auto-deduction",
        level=3,
        language="cpp",
        name="What auto deduces",
        family=FAMILY,
        code=(
            "#include <iostream>\n"
            "#include <vector>\n"
            "\n"
            "int main() {\n"
            "    std::vector<int> v = {1, 2, 3};\n"
            "    auto first = v[0];\n"
            "    auto& last = v[2];\n"
            "    first = 100;\n"
            "    last = 300;\n"
            "    std::cout << v[0] << \" \" << v[2] << \"\\n\";\n"
            "    return 0;\n"
            "}"
        ),
        expect="1 300",
        why=(
            "`auto` on its own deduces a plain int - a copy - even though v[0] is a "
            "reference into the vector. You have to ask for a reference with "
            "`auto&`, which is what last is, so only the change through last "
            "reaches the vector."
        ),
    ),
    _p(
        id="predict-cpp-destructor-order",
        level=4,
        language="cpp",
        name="Who is destroyed first",
        family=FAMILY,
        code=(
            "#include <iostream>\n"
            "\n"
            "struct Noisy {\n"
            "    char name;\n"
            "    ~Noisy() { std::cout << \"bye \" << name << \"\\n\"; }\n"
            "};\n"
            "\n"
            "int main() {\n"
            "    Noisy a{'a'};\n"
            "    { Noisy b{'b'}; }\n"
            "    Noisy c{'c'};\n"
            "    std::cout << \"end\\n\";\n"
            "    return 0;\n"
            "}"
        ),
        expect="bye b\nend\nbye c\nbye a",
        why=(
            "An object is destroyed when its scope ends. b's scope is the inner "
            "braces, so it goes first, before end is printed. a and c live until "
            "main's closing brace and go in REVERSE order of creation - c, then a. "
            "This is RAII: cleanup tied to scope, in a predictable order."
        ),
    ),
    _p(
        id="predict-cpp-static-counter",
        level=4,
        language="cpp",
        name="A static member counts every object",
        family=FAMILY,
        code=(
            "#include <iostream>\n"
            "\n"
            "struct Ticket {\n"
            "    static int made;\n"
            "    int number;\n"
            "    Ticket() : number(++made) {}\n"
            "};\n"
            "int Ticket::made = 0;\n"
            "\n"
            "int main() {\n"
            "    Ticket a, b, c;\n"
            "    std::cout << a.number << b.number << c.number << \" \" << Ticket::made << \"\\n\";\n"
            "    return 0;\n"
            "}"
        ),
        expect="123 3",
        why=(
            "A static member belongs to the class, not to each object: there is one "
            "`made` shared by every Ticket. Each constructor bumps it and keeps the "
            "new value as its own number, so the three tickets are 1, 2 and 3, and "
            "made ends at 3."
        ),
    ),
    _p(
        id="predict-cpp-overload",
        level=5,
        language="cpp",
        name="Which overload is called",
        family=FAMILY,
        code=(
            "#include <iostream>\n"
            "#include <string>\n"
            "\n"
            "void show(int) { std::cout << \"int \"; }\n"
            "void show(double) { std::cout << \"double \"; }\n"
            "void show(const std::string&) { std::cout << \"string \"; }\n"
            "\n"
            "int main() {\n"
            "    show(3);\n"
            "    show(3.0);\n"
            "    show('x');\n"
            "    show(std::string(\"hi\"));\n"
            "    std::cout << \"end\\n\";\n"
            "    return 0;\n"
            "}"
        ),
        expect="int double int string end",
        why=(
            "The compiler picks the closest match at compile time. 3 is an int and "
            "3.0 a double. A char is not a string - it is a small integer - and "
            "promoting char to int beats converting it to double, so 'x' calls the "
            "int version."
        ),
    ),
)
