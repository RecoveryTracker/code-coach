"""The Dart bank, and the text-based checks that stand in for an AST."""

import unittest

from code_coach import dart_checks as chk
from code_coach.engine import dart_available, run_code
from code_coach.leetcode.problems import PATTERNS as PY_PATTERNS
from code_coach.leetcode.problems_dart import PATTERNS as DART_PATTERNS


class ParityTests(unittest.TestCase):
    """Switching language must keep your place, so both banks line up."""

    def test_same_patterns_in_the_same_order(self):
        self.assertEqual(
            [p.id for p in DART_PATTERNS], [p.id for p in PY_PATTERNS]
        )

    def test_same_problems_in_the_same_order(self):
        for dart, py in zip(DART_PATTERNS, PY_PATTERNS):
            with self.subTest(pattern=py.id):
                self.assertEqual(
                    [p.number for p in dart.problems],
                    [p.number for p in py.problems],
                )

    def test_solutions_are_actually_dart(self):
        for pattern in DART_PATTERNS:
            for problem in pattern.problems:
                with self.subTest(problem=problem.number):
                    self.assertNotIn("def ", problem.code)
                    self.assertIn("{", problem.code)

    def test_imports_come_before_declarations_in_preambles(self):
        # Dart rejects a directive that follows a declaration, and these
        # blocks are typed in order as the pattern's first exercises.
        for pattern in DART_PATTERNS:
            blocks = list(pattern.preamble)
            seen_declaration = False
            for block in blocks:
                if block.startswith("import "):
                    with self.subTest(pattern=pattern.id):
                        self.assertFalse(
                            seen_declaration,
                            f"{pattern.id}: import must precede declarations",
                        )
                else:
                    seen_declaration = True


class DartCheckTests(unittest.TestCase):
    def test_keyword_in_a_comment_does_not_count(self):
        self.assertFalse(chk.uses_while("// while (x) {}\nint f() => 1;"))
        self.assertFalse(chk.uses_for("/* for (;;) {} */ int f() => 1;"))

    def test_keyword_in_a_string_does_not_count(self):
        self.assertFalse(chk.uses_if("void f() { print('if (a) then'); }"))

    def test_real_control_flow_counts(self):
        self.assertTrue(chk.uses_while("void f() { while (x) { y(); } }"))
        self.assertTrue(chk.uses_for("void f() { for (var i = 0; i < 3; i++) {} }"))
        self.assertTrue(chk.uses_if("void f() { if (a) { b(); } }"))

    def test_bare_return_is_not_a_returned_value(self):
        self.assertFalse(chk.returns_value("void f() { return; }"))
        self.assertTrue(chk.returns_value("int f() { return 1; }"))

    def test_calling_a_function_is_not_defining_it(self):
        self.assertFalse(chk.defines_function("void main() { twoSum(a, b); }", "twoSum"))

    def test_definition_is_recognised(self):
        code = "List<int> twoSum(List<int> nums, int target) {\n  return [];\n}"
        self.assertTrue(chk.defines_function(code, "twoSum"))

    def test_arrow_definition_is_recognised(self):
        self.assertTrue(chk.defines_function("int f(int a) => a * 2;", "f"))

    def test_class_detection(self):
        self.assertTrue(chk.defines_class("class MinStack {}", "MinStack"))
        self.assertFalse(chk.defines_class("// class MinStack {}", "MinStack"))

    def test_top_level_names_finds_the_solution_function(self):
        code = (
            "List<int> twoSum(List<int> nums, int target) {\n"
            "  final seen = <int, int>{};\n"
            "  return [];\n"
            "}"
        )
        funcs, classes = chk.top_level_names(code)
        self.assertIn("twoSum", funcs)
        self.assertEqual(classes, [])


@unittest.skipUnless(dart_available(), "Dart SDK not on PATH")
class DartRunsTests(unittest.TestCase):
    """A slice of the bank actually compiled and executed. The full sweep of
    all 52 lives in scripts rather than here — each `dart run` costs seconds."""

    def test_hash_map_solutions_compile_and_answer_correctly(self):
        pattern = next(p for p in DART_PATTERNS if p.id == "lc-hashmap")
        src = "\n\n".join(
            list(pattern.preamble) + [p.code for p in pattern.problems]
        )
        src += (
            "\n\nvoid main() {\n"
            "  print(twoSum([2, 7, 11, 15], 9));\n"
            "  print(containsDuplicate([1, 2, 3, 1]));\n"
            "  print(isAnagram('anagram', 'nagaram'));\n"
            "  print(groupAnagrams(['eat', 'tea', 'tan']).length);\n"
            "}\n"
        )
        out, err, code = run_code(src, language="dart")
        self.assertEqual(code, 0, err[:400])
        self.assertEqual(out.split(), ["[0,", "1]", "true", "true", "2"])

    def test_a_dart_syntax_error_is_reported_not_raised(self):
        out, err, code = run_code("void main() { int x = ; }", language="dart")
        self.assertNotEqual(code, 0)
        self.assertIn("Error", err)


if __name__ == "__main__":
    unittest.main()
