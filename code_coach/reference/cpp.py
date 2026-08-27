"""The C++ cheat sheet.

Deliberately modern where it matters. Someone learning C++ today should reach
for vector before new[], for string before char*, and for a range-for before
an index loop — so those are what the card puts in front of them. The older
forms appear where you still have to read them, not as the recommendation.
"""

from __future__ import annotations

from code_coach.reference import Entry, Section, Sheet, register


def _e(code: str, note: str = "") -> Entry:
    return Entry(code=code, note=note)


SHEET = Sheet(
    language="cpp",
    sections=(
        Section(
            "The first minute",
            "What you write before you have written anything.",
            (
                _e("#include <iostream>", "cout and cin live here"),
                _e("int main() {\n    return 0;\n}", "0 means success"),
                _e('std::cout << "hi\\n";', "<< chains; \\n beats std::endl"),
                _e("int count = 0;", "type first, always"),
                _e("auto total = 0;", "auto takes the type from the value"),
                _e("std::vector<int> nums;", "the default container"),
                _e("std::string name = \"Ada\";", "not char*, not char[]"),
                _e("if (a == b) {", "one = assigns, and compiles"),
                _e("for (int x : nums) {", "range-for; add & to avoid a copy"),
                _e("// a note to your later self", "and /* ... */ for a block"),
            ),
        ),
        Section(
            "Printing and reading",
            "Streams, and the two or three things that surprise people.",
            (
                _e("std::cout << x << \" \" << y << \"\\n\";", "chain as many as you like"),
                _e("std::cerr << \"oops\\n\";", "errors do not belong on stdout"),
                _e("std::cin >> n;", "stops at whitespace"),
                _e("std::getline(std::cin, line);", "a whole line, spaces included"),
                _e("std::cin >> n;\nstd::cin.ignore();", "ignore eats the newline >> left"),
                _e("while (std::cin >> n) {", "loops until the read fails"),
                _e("#include <iomanip>", "for the formatting below"),
                _e("std::cout << std::fixed << std::setprecision(2);", "sticky: applies to all later output"),
                _e("std::cout << std::setw(8) << name;", "pad to eight columns"),
                _e("std::cout << std::boolalpha << ready;", "true instead of 1"),
                _e("using std::cout;", "better than using namespace std;"),
            ),
        ),
        Section(
            "vector",
            "The container to reach for unless you know why not.",
            (
                _e("#include <vector>", "the include everyone forgets"),
                _e("std::vector<int> nums(10, 0);", "ten zeros; not ten capacity"),
                _e("std::vector<int> nums = {1, 2, 3};", "braces initialise"),
                _e("nums.push_back(4);", "grows as needed"),
                _e("nums.pop_back();", "removes the last; returns nothing"),
                _e("nums.size()", "unsigned, so mind the comparisons"),
                _e("nums.empty()", "clearer than size() == 0"),
                _e("nums[i]", "no bounds check; .at(i) throws instead"),
                _e("nums.front()\nnums.back()", "first and last; undefined if empty"),
                _e("nums.clear();", "size to zero, capacity kept"),
                _e("nums.insert(nums.begin(), 0);", "at the front; shifts everything"),
                _e("nums.erase(nums.begin() + 2);", "removes the third"),
                _e("for (auto& x : nums) x *= 2;", "the & is what makes it edit"),
                _e("std::vector<std::vector<int>> grid(3, std::vector<int>(4));", "3 by 4, all zero"),
            ),
        ),
        Section(
            "string",
            "It is a real type, with real methods.",
            (
                _e("#include <string>", "often pulled in already; do not rely on it"),
                _e("s.size()", "same as .length(); both are there"),
                _e("s + t", "concatenation, unlike C"),
                _e("s += \"more\";", "appends in place"),
                _e("s.substr(2, 3)", "from index 2, three characters"),
                _e("s.find(\"ab\")", "index, or std::string::npos"),
                _e("if (s.find(t) != std::string::npos) {", "the idiom for contains"),
                _e("std::stoi(s)", "text to int; stod for double"),
                _e("std::to_string(n)", "number to text"),
                _e("s[0]", "a char, not a one-character string"),
                _e("std::reverse(s.begin(), s.end());", "needs <algorithm>"),
                _e("s.c_str()", "for C functions that want char*"),
            ),
        ),
        Section(
            "References, pointers and copies",
            "The part that is genuinely different from other languages.",
            (
                _e("void f(std::vector<int> v)", "copies the whole vector"),
                _e("void f(const std::vector<int>& v)", "no copy, cannot modify: the default"),
                _e("void f(std::vector<int>& v)", "no copy, can modify"),
                _e("int& r = n;", "another name for n; cannot be reseated"),
                _e("int* p = &n;", "a pointer; *p reads through it"),
                _e("nullptr", "not NULL, and not 0"),
                _e("if (p) {", "a pointer is truthy when non-null"),
                _e("auto x = nums;", "auto copies; auto& does not"),
                _e("const auto& x = nums;", "read-only, no copy"),
                _e("obj.field\nptr->field", "dot for objects, arrow through a pointer"),
            ),
        ),
        Section(
            "Ownership and memory",
            "You almost never write new. When you do, write it once.",
            (
                _e("#include <memory>", "for the pointers below"),
                _e("auto p = std::make_unique<Thing>();", "one owner; freed automatically"),
                _e("auto p = std::make_shared<Thing>();", "counted; freed when the last one goes"),
                _e("std::unique_ptr<Thing> p;", "the type, if you must name it"),
                _e("p->method();", "smart pointers use arrow like raw ones"),
                _e("std::move(p)", "hands ownership on; p is empty after"),
                _e("Thing* raw = p.get();", "borrow without owning; do not delete it"),
                _e("delete ptr;", "only for a raw new, and prefer neither"),
                _e("~Thing();", "the destructor: cleanup happens here"),
            ),
        ),
        Section(
            "Maps, sets and pairs",
            "Ordered by default; the unordered ones are the hash tables.",
            (
                _e("#include <map>\n#include <unordered_map>", "ordered and hashed"),
                _e("std::map<std::string, int> counts;", "sorted by key, log n"),
                _e("std::unordered_map<std::string, int> counts;", "hashed, average constant"),
                _e("counts[\"a\"]++;", "inserts a zero first if missing"),
                _e("counts.count(\"a\")", "0 or 1; .contains(\"a\") in C++20"),
                _e("counts.find(k) != counts.end()", "the pre-C++20 contains"),
                _e("for (auto& [key, value] : counts) {", "structured binding, C++17"),
                _e("std::set<int> seen;", "sorted, no duplicates"),
                _e("seen.insert(4);", "returns a pair; .second says if it was new"),
                _e("std::pair<int, int> p = {1, 2};", "p.first and p.second"),
                _e("counts.erase(k);", "by key, for maps and sets"),
            ),
        ),
        Section(
            "algorithm",
            "Written once, in the standard library, faster than your loop.",
            (
                _e("#include <algorithm>", "everything below needs it"),
                _e("std::sort(nums.begin(), nums.end());", "ascending by default"),
                _e("std::sort(nums.begin(), nums.end(), std::greater<int>());", "descending"),
                _e("std::reverse(nums.begin(), nums.end());", "in place"),
                _e("std::max_element(nums.begin(), nums.end())", "an iterator; * to read it"),
                _e("*std::max_element(nums.begin(), nums.end())", "the value itself"),
                _e("std::find(nums.begin(), nums.end(), 5)", "== .end() means not found"),
                _e("std::count(nums.begin(), nums.end(), 5)", "how many equal 5"),
                _e("std::accumulate(nums.begin(), nums.end(), 0)", "sums; needs <numeric>"),
                _e("std::binary_search(nums.begin(), nums.end(), 5)", "sorted input only"),
                _e("std::min(a, b)\nstd::max(a, b)", "two values, not a range"),
                _e("std::swap(a, b);", "works on anything movable"),
            ),
        ),
        Section(
            "Lambdas",
            "A function written where it is used.",
            (
                _e("[](int a, int b) { return a < b; }", "the comparator shape"),
                _e("auto twice = [](int n) { return n * 2; };", "store it in an auto"),
                _e("[&](int n) { return n + offset; }", "& captures surroundings by reference"),
                _e("[=](int n) { return n + offset; }", "= captures them by copy"),
                _e("[offset](int n) { return n + offset; }", "name exactly what you need"),
                _e("std::sort(v.begin(), v.end(), [](auto& a, auto& b) {\n    return a.score > b.score;\n});", "sort by a field"),
            ),
        ),
        Section(
            "Classes",
            "Just enough to read one and write a small one.",
            (
                _e("class Point {\npublic:\n    int x = 0;\n};", "class members are private by default"),
                _e("struct Point {\n    int x = 0;\n};", "struct members are public by default"),
                _e("Point(int x) : x(x) {}", "the initialiser list, not assignment"),
                _e("int get() const { return x; }", "const means it does not modify"),
                _e("static int count;", "one per class, not per object"),
                _e("virtual void draw();", "without virtual, overriding does not dispatch"),
                _e("void draw() override;", "override makes the compiler check you"),
                _e("class Circle : public Shape {", "public inheritance"),
            ),
        ),
        Section(
            "Errors and the rest",
            "The bits you meet soon after the basics.",
            (
                _e("#include <stdexcept>", "the standard exception types"),
                _e("throw std::runtime_error(\"bad input\");", "throws by value"),
                _e("try {\n} catch (const std::exception& e) {\n    std::cerr << e.what();\n}", "catch by const reference"),
                _e("std::optional<int> find();", "maybe a value; needs <optional>, C++17"),
                _e("if (auto r = find(); r) {", "the if-with-initialiser, C++17"),
                _e("constexpr int MAX = 100;", "computed at compile time"),
                _e("enum class Colour { Red, Green };", "scoped: Colour::Red, no implicit int"),
                _e("using Grid = std::vector<std::vector<int>>;", "a type alias; clearer than typedef"),
                _e("g++ -std=c++17 -Wall -Wextra main.cpp", "warnings on, always"),
            ),
        ),
    ),
)

register(SHEET)
