"""The C++ kata driver: every way a C++ answer can go, marked correctly.

Generated per case like the C driver (kata/cpp_harness.py), with
exceptions caught per case. These run real code through the real compiler
and skip on a machine with no C++ compiler.
"""

from __future__ import annotations

import unittest

from code_coach.engine import cpp_available, run_code
from code_coach.kata import Kata, harness, judge
from code_coach.kata import cpp_harness as ch

NEEDS = "needs a C++ compiler (g++, clang++ or MSVC)"

SUM = Kata(id="cpp-sum", name="sumOf", brief="", params=("nums",),
           cases=(([1, 2, 3],), ([],), ([-5],)), solve=sum,
           language="cpp", types=("vector<int>",), returns="int")
EVENS = Kata(id="cpp-evens", name="evensOf", brief="", params=("nums",),
             cases=(([1, 2, 3, 4],), ([],), ([7],)),
             solve=lambda nums: [n for n in nums if n % 2 == 0],
             language="cpp", types=("vector<int>",), returns="vector<int>")
SHOUT = Kata(id="cpp-shout", name="shout", brief="", params=("word",),
             cases=(("hi",), ("",), ('a"b\\c',), ("café?",)),
             solve=lambda w: w.upper() + "!",
             language="cpp", types=("string",), returns="string")
SPLIT = Kata(id="cpp-words", name="words", brief="", params=("text",),
             cases=(("a b",), ("",)), solve=lambda t: t.split(),
             language="cpp", types=("string",), returns="vector<string>")
MIX = Kata(id="cpp-mix", name="mix", brief="", params=("n", "big", "x", "flag"),
           cases=((3, 5000000000, 1.5, True), (-2, -1, 0.1, False)),
           solve=lambda n, big, x, flag: (n + big) * x if flag else float(n),
           language="cpp", types=("int", "long long", "double", "bool"),
           returns="double")
IS_EVEN = Kata(id="cpp-even", name="isEven", brief="", params=("n",),
               cases=((4,), (7,), (0,)), solve=lambda n: n % 2 == 0,
               language="cpp", types=("int",), returns="bool")


def _run(kata: Kata, code: str):
    out, err, status = run_code(harness(kata, code), language="cpp")
    return judge(kata, out, err, status)


class SignatureTests(unittest.TestCase):

    def test_a_vector_is_taken_by_const_reference(self) -> None:
        self.assertEqual(ch.signature(SUM), "int sumOf(const std::vector<int> &nums) {")
        self.assertEqual(SUM.signature, ch.signature(SUM))

    def test_a_list_result_is_a_vector(self) -> None:
        self.assertEqual(ch.signature(EVENS),
                         "std::vector<int> evensOf(const std::vector<int> &nums) {")

    def test_strings_and_scalars(self) -> None:
        self.assertEqual(ch.signature(SHOUT), "std::string shout(const std::string &word) {")
        self.assertEqual(ch.signature(MIX),
                         "double mix(int n, long long big, double x, bool flag) {")

    def test_std_prefixes_and_aliases_mean_the_same_type(self) -> None:
        self.assertEqual(ch.norm("std::vector< int >"), "vector<int>")
        self.assertEqual(ch.norm("int[]"), "vector<int>")
        self.assertEqual(ch.norm("string[]"), "vector<string>")


class WritingValuesTests(unittest.TestCase):
    """No compiler needed: how a value is spelled in the program."""

    def test_non_ascii_and_question_marks_are_escaped(self) -> None:
        self.assertEqual(ch._cpp_string("a?"), '"a\\?"')
        self.assertEqual(ch._cpp_string("é"), '"\\303\\251"')
        self.assertEqual(ch._cpp_string('q"\\'), '"q\\"\\\\"')

    def test_a_vector_literal(self) -> None:
        self.assertEqual(ch._value("vector<int>", [1, -2]), "std::vector<int>{1, -2}")
        self.assertEqual(ch._value("long long", 7), "7LL")


@unittest.skipUnless(cpp_available(), NEEDS)
class MarkingTests(unittest.TestCase):

    def test_a_right_answer_passes(self) -> None:
        code = ("int sumOf(const std::vector<int> &nums) {\n  int t = 0;\n"
                "  for (int n : nums) t += n;\n  return t;\n}")
        self.assertTrue(_run(SUM, code).passed)

    def test_a_wrong_answer_names_the_inputs(self) -> None:
        outcome = _run(SUM, "int sumOf(const std::vector<int> &nums) {\n"
                            "  return (int)nums.size();\n}")
        self.assertEqual(outcome.broke, "")
        # sizes 3, 0, 1 against sums 6, 0, -5
        self.assertEqual([r.args for r in outcome.results if not r.passed],
                         [([1, 2, 3],), ([-5],)])
        self.assertEqual([r.got for r in outcome.results], [3, 0, 1])

    def test_a_missing_function_is_named(self) -> None:
        outcome = _run(SUM, "int summ(const std::vector<int> &nums) { return 0; }")
        self.assertIn("there is no function called sumOf", outcome.broke)

    def test_a_compile_error_points_at_the_line_in_the_box(self) -> None:
        outcome = _run(SUM, "int sumOf(const std::vector<int> &nums) {\n  return nope;\n}")
        self.assertIn("Line 2:", outcome.broke)
        self.assertNotIn(".cpp", outcome.broke)

    def test_a_crash_is_reported_against_the_input_that_caused_it(self) -> None:
        code = ("int sumOf(const std::vector<int> &nums) {\n"
                "  if (nums.empty()) { int *p = nullptr; return *p; }\n  return nums[0];\n}")
        outcome = _run(SUM, code)
        self.assertEqual(outcome.broke, "")
        by_args = {tuple(r.args[0]): r for r in outcome.results}
        # nums[0] is 1 where the sum is 6: wrong, but it ran
        self.assertFalse(by_args[(1, 2, 3)].passed)
        self.assertEqual(by_args[(1, 2, 3)].got, 1)
        self.assertIn("crashed on this input", by_args[()].error)
        self.assertIn("not run", by_args[(-5,)].error)

    def test_an_exception_is_reported_against_its_case_only(self) -> None:
        code = ("int sumOf(const std::vector<int> &nums) {\n"
                "  return nums.at(0);\n}")
        outcome = _run(SUM, code)
        self.assertEqual(outcome.broke, "")
        by_args = {tuple(r.args[0]): r for r in outcome.results}
        self.assertIn("threw an exception", by_args[()].error)
        self.assertEqual(by_args[(-5,)].got, -5)
        self.assertTrue(by_args[(-5,)].passed)

    def test_a_vector_result_comes_back_as_a_list(self) -> None:
        code = ("std::vector<int> evensOf(const std::vector<int> &nums) {\n"
                "  std::vector<int> r;\n"
                "  for (int n : nums) if (n % 2 == 0) r.push_back(n);\n  return r;\n}")
        self.assertTrue(_run(EVENS, code).passed)

    def test_changing_the_vector_it_was_given_fails(self) -> None:
        code = ("std::vector<int> evensOf(std::vector<int> &nums) {\n"
                "  std::vector<int> r;\n"
                "  for (int &n : nums) { if (n % 2 == 0) r.push_back(n); n = 0; }\n"
                "  return r;\n}")
        outcome = _run(EVENS, code)
        self.assertFalse(outcome.passed)
        self.assertTrue(any(r.changed for r in outcome.results))

    def test_taking_the_vector_by_value_is_fine(self) -> None:
        code = ("std::vector<int> evensOf(std::vector<int> nums) {\n"
                "  nums.erase(std::remove_if(nums.begin(), nums.end(),\n"
                "             [](int n) { return n % 2 != 0; }), nums.end());\n"
                "  return nums;\n}")
        self.assertTrue(_run(EVENS, code).passed)

    def test_strings_survive_the_trip_both_ways(self) -> None:
        # the é case is two UTF-8 bytes, which toupper-by-ASCII leaves alone
        code = ("std::string shout(const std::string &word) {\n"
                "  std::string r = word;\n"
                "  for (char &c : r) if (c >= 'a' && c <= 'z') c = (char)(c - 32);\n"
                "  return r + \"!\";\n}")
        outcome = _run(SHOUT, code)
        self.assertEqual(outcome.broke, "")
        got = [r.got for r in outcome.results]
        self.assertEqual(got, ["HI!", "!", 'A"B\\C!', "CAFé?!"])

    def test_a_vector_of_strings_comes_back(self) -> None:
        code = ("std::vector<std::string> words(const std::string &text) {\n"
                "  std::vector<std::string> r; std::string cur;\n"
                "  for (char c : text) {\n"
                "    if (c == ' ') { if (!cur.empty()) r.push_back(cur); cur.clear(); }\n"
                "    else cur += c;\n  }\n"
                "  if (!cur.empty()) r.push_back(cur);\n  return r;\n}")
        outcome = _run(SPLIT, code)
        self.assertEqual([r.got for r in outcome.results], [["a", "b"], []])
        self.assertTrue(outcome.passed)

    def test_ints_long_long_doubles_and_bools_round_trip(self) -> None:
        # (3 + 5e9) * 1.5 = 7500000004.5 ; the unflagged case is just n = -2
        code = ("double mix(int n, long long big, double x, bool flag) {\n"
                "  if (flag) return (double)(n + big) * x;\n"
                "  return (double)n;\n}")
        outcome = _run(MIX, code)
        self.assertEqual(outcome.broke, "")
        self.assertEqual([r.got for r in outcome.results], [7500000004.5, -2])
        self.assertTrue(outcome.passed)

    def test_a_bool_result_is_a_real_bool(self) -> None:
        self.assertTrue(_run(IS_EVEN, "bool isEven(int n) { return n % 2 == 0; }").passed)
        outcome = _run(IS_EVEN, "bool isEven(int n) { return n % 2 != 0; }")
        self.assertEqual([r.got for r in outcome.results], [False, True, False])

    def test_the_students_own_printing_does_not_break_the_marker(self) -> None:
        code = ("int sumOf(const std::vector<int> &nums) {\n"
                "  std::cout << \"debug\";\n  int t = 0;\n"
                "  for (int n : nums) t += n;\n  return t;\n}")
        self.assertTrue(_run(SUM, code).passed)


if __name__ == "__main__":
    unittest.main()
