"""Are the cheat sheets telling the truth?

test_reference.py checks that a sheet is dense, ordered, unrepetitive and
typeable. None of that can tell a real API from an invented one, and a
reference card is worse than no card when it is confidently wrong — the whole
point of it is that you copy the line without checking.

So the claims that could plausibly be made up get executed. Most entries are
fragments and cannot run alone, which is why this works two ways: every
complete SQL statement is run against the app's own database, and the C++
sheet's non-obvious claims are assembled into one program and compiled.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code
from code_coach.reference import sheet_for

STATEMENT_STARTS = ("SELECT", "WITH", "INSERT", "UPDATE", "DELETE", "CREATE")


def sql_statements() -> list[str]:
    out = []
    for section in sheet_for("sql").sections:
        for entry in section.entries:
            code = entry.code.strip()
            if code.endswith(";") and code.upper().startswith(STATEMENT_STARTS):
                out.append(code)
    return out


class SqlTests(unittest.TestCase):
    def test_every_whole_statement_parses(self) -> None:
        """A missing table or column is about the sample data, not about the
        SQL — the card teaches shapes, and not every shape fits the fixture.
        A syntax error is the thing being looked for, and it means the line
        would not run anywhere."""
        for statement in sql_statements():
            _, err, _ = run_code(statement, language="sql")
            with self.subTest(sql=statement.replace("\n", " ")[:50]):
                lowered = err.lower()
                self.assertNotIn("syntax error", lowered, err)
                self.assertNotIn("incomplete", lowered, err)

    def test_there_are_enough_of_them_to_be_worth_checking(self) -> None:
        """Guards against the extractor above quietly matching nothing."""
        self.assertGreaterEqual(len(sql_statements()), 15)


# Every non-obvious claim on the C++ sheet, in one program: the container and
# string methods, the algorithm names, the capture forms, the smart pointers,
# structured bindings, optional, the if-with-initialiser, and the stream
# manipulators. A wrong name fails to compile; a wrong behaviour returns a
# non-zero code naming the check that caught it.
CPP_PROGRAM = r"""
#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <map>
#include <unordered_map>
#include <set>
#include <memory>
#include <algorithm>
#include <numeric>
#include <optional>
#include <stdexcept>

struct Thing { int n = 1; int method() const { return n; } };
enum class Colour { Red, Green };
using Grid = std::vector<std::vector<int>>;

std::optional<int> find_one() { return 7; }

int main() {
    std::vector<int> nums(10, 0);
    std::vector<int> more = {1, 2, 3};
    more.push_back(4);
    more.pop_back();
    if (more.empty() || more.size() != 3) return 1;
    if (more.at(0) != more.front() || more.back() != 3) return 2;
    more.insert(more.begin(), 0);
    more.erase(more.begin() + 2);
    for (auto& x : more) x *= 2;
    Grid grid(3, std::vector<int>(4));
    if (grid[2][3] != 0 || nums.size() != 10) return 3;

    std::string s = "Ada";
    s += "more";
    if (s.substr(0, 3) != "Ada") return 4;
    if (s.find("zz") != std::string::npos) return 5;
    if (std::stoi("42") != 42 || std::to_string(7) != "7") return 6;
    std::reverse(s.begin(), s.end());
    if (s.c_str() == nullptr) return 7;

    std::map<std::string, int> counts;
    counts["a"]++;
    std::unordered_map<std::string, int> hashed;
    hashed["b"] = 1;
    if (counts.count("a") != 1) return 8;
    if (counts.find("a") == counts.end()) return 9;
    for (auto& [key, value] : counts) { (void)key; (void)value; }
    std::set<int> seen;
    if (!seen.insert(4).second) return 10;
    std::pair<int, int> p = {1, 2};
    if (p.first + p.second != 3) return 11;
    counts.erase("a");

    std::vector<int> v = {3, 1, 2};
    std::sort(v.begin(), v.end());
    std::sort(v.begin(), v.end(), std::greater<int>());
    std::reverse(v.begin(), v.end());
    if (*std::max_element(v.begin(), v.end()) != 3) return 12;
    if (std::find(v.begin(), v.end(), 5) != v.end()) return 13;
    if (std::count(v.begin(), v.end(), 2) != 1) return 14;
    if (std::accumulate(v.begin(), v.end(), 0) != 6) return 15;
    if (!std::binary_search(v.begin(), v.end(), 2)) return 16;
    int a = 1, b = 2;
    std::swap(a, b);
    if (std::min(a, b) != 1 || std::max(a, b) != 2) return 17;

    auto twice = [](int n) { return n * 2; };
    int offset = 5;
    auto byref = [&](int n) { return n + offset; };
    auto bycopy = [=](int n) { return n + offset; };
    auto named = [offset](int n) { return n + offset; };
    if (twice(2) != 4 || byref(1) != 6) return 18;
    if (bycopy(1) != 6 || named(1) != 6) return 19;

    auto up = std::make_unique<Thing>();
    auto sp = std::make_shared<Thing>();
    if (up->method() != 1 || sp->method() != 1) return 20;
    if (up.get() == nullptr) return 21;
    auto moved = std::move(up);
    if (up != nullptr) return 22;

    if (auto r = find_one(); r) { if (*r != 7) return 23; } else { return 24; }

    try { throw std::runtime_error("bad input"); }
    catch (const std::exception& e) {
        if (std::string(e.what()) != "bad input") return 25;
    }

    constexpr int MAX = 100;
    Colour c = Colour::Red;
    if (MAX != 100 || c != Colour::Red) return 26;

    std::cout << std::fixed << std::setprecision(2) << 1.5 << "\n";
    std::cout << std::setw(8) << "pad" << "\n";
    std::cout << std::boolalpha << true << "\n";
    return 0;
}
"""


class CppTests(unittest.TestCase):
    def test_the_sheets_claims_compile_and_hold(self) -> None:
        out, err, code = run_code(CPP_PROGRAM, language="cpp")
        if code != 0 and "isn't on your PATH" in err:
            self.skipTest("needs g++ or clang++ on PATH")
        self.assertEqual(code, 0, err or out)
        # The manipulators are on the card with specific claims about what
        # they do, so check the output rather than only the exit code.
        self.assertIn("1.50", out)
        self.assertIn("     pad", out)
        self.assertIn("true", out)


if __name__ == "__main__":
    unittest.main()
