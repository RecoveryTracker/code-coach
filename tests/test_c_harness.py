"""The C kata driver: every way a C answer can go, marked correctly.

C has no exceptions to catch and no JSON to read, so its driver is
generated per case and prints a line per case - see kata/c_harness.py.
These run real code through the real compiler, and skip on a machine
with no C compiler.
"""

from __future__ import annotations

import unittest

from code_coach.engine import c_available, run_code
from code_coach.kata import MARKER, Kata, judge
from code_coach.kata import c_harness as ch

NEEDS_C = "needs a C compiler (gcc, clang or MSVC)"

SUM = Kata(id="c-sum", name="sumOf", brief="", params=("nums",),
           cases=(([1, 2, 3],), ([],), ([-5],)), solve=sum,
           language="c", types=("int[]",), returns="int")
EVENS = Kata(id="c-evens", name="evensOf", brief="", params=("nums",),
             cases=(([1, 2, 3, 4],), ([],), ([7],)),
             solve=lambda nums: [n for n in nums if n % 2 == 0],
             language="c", types=("int[]",), returns="int[]")
SHOUT = Kata(id="c-shout", name="shout", brief="", params=("word",),
             cases=(("hi",), ("",), ('a"b',)), solve=lambda w: w.upper() + "!",
             language="c", types=("string",), returns="string")


def _run(kata: Kata, code: str):
    out, err, code_ = run_code(ch.harness(kata, code), language="c")
    if ch.missing(kata, out, err):
        return "missing"
    return judge(kata, ch.unpack(kata, out, err, code_, MARKER), err, code_)


class SignatureTests(unittest.TestCase):

    def test_an_array_is_a_pointer_and_a_length(self) -> None:
        self.assertEqual(ch.signature(SUM), "int sumOf(const int *nums, int nums_len) {")

    def test_a_list_result_is_written_into_out(self) -> None:
        self.assertEqual(ch.signature(EVENS),
                         "int evensOf(const int *nums, int nums_len, int *out) {")

    def test_a_string_is_a_const_char_pointer(self) -> None:
        self.assertEqual(ch.signature(SHOUT), "const char *shout(const char *word) {")


@unittest.skipUnless(c_available(), NEEDS_C)
class MarkingTests(unittest.TestCase):

    def test_a_right_answer_passes(self) -> None:
        code = ("int sumOf(const int *nums, int nums_len) {\n  int t = 0;\n"
                "  for (int i = 0; i < nums_len; i++) t += nums[i];\n  return t;\n}")
        self.assertTrue(_run(SUM, code).passed)

    def test_a_wrong_answer_names_the_inputs(self) -> None:
        outcome = _run(SUM, "int sumOf(const int *nums, int nums_len) {\n  return nums_len;\n}")
        self.assertEqual(outcome.broke, "")
        self.assertEqual([r.args for r in outcome.results if not r.passed],
                         [([1, 2, 3],), ([-5],)])

    def test_a_missing_function_is_named(self) -> None:
        self.assertEqual(_run(SUM, "int summ(const int *nums, int nums_len) { return 0; }"),
                         "missing")

    def test_a_compile_error_points_at_the_line_in_the_box(self) -> None:
        outcome = _run(SUM, "int sumOf(const int *nums, int nums_len) {\n  return nope;\n}")
        self.assertIn("Line 2:", outcome.broke)
        self.assertNotIn(".c:", outcome.broke)

    def test_a_crash_is_reported_against_the_input_that_caused_it(self) -> None:
        code = ("int sumOf(const int *nums, int nums_len) {\n"
                "  if (nums_len == 0) { int *p = 0; return *p; }\n  return nums[0];\n}")
        outcome = _run(SUM, code)
        self.assertEqual(outcome.broke, "")
        by_args = {tuple(map(tuple, r.args)): r for r in outcome.results}
        self.assertIn("crashed on this input", by_args[((),)].error)
        self.assertIn("not run", by_args[((-5,),)].error)

    def test_a_list_result_comes_back_as_a_list(self) -> None:
        code = ("int evensOf(const int *nums, int nums_len, int *out) {\n  int n = 0;\n"
                "  for (int i = 0; i < nums_len; i++) if (nums[i] % 2 == 0) out[n++] = nums[i];\n"
                "  return n;\n}")
        self.assertTrue(_run(EVENS, code).passed)

    def test_changing_the_array_it_was_given_fails(self) -> None:
        code = ("int evensOf(const int *nums, int nums_len, int *out) {\n"
                "  int *m = (int *)nums;\n  int n = 0;\n"
                "  for (int i = 0; i < nums_len; i++) { if (m[i] % 2 == 0) out[n++] = m[i]; m[i] = 0; }\n"
                "  return n;\n}")
        outcome = _run(EVENS, code)
        self.assertFalse(outcome.passed)
        self.assertTrue(any(r.changed for r in outcome.results))

    def test_strings_survive_the_trip_both_ways(self) -> None:
        code = ("#include <ctype.h>\nstatic char buf[64];\n"
                "const char *shout(const char *word) {\n  int i = 0;\n"
                "  for (; word[i]; i++) buf[i] = (char)toupper((unsigned char)word[i]);\n"
                "  buf[i] = '!'; buf[i + 1] = 0;\n  return buf;\n}")
        self.assertTrue(_run(SHOUT, code).passed)


if __name__ == "__main__":
    unittest.main()
