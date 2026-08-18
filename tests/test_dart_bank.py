"""The Dart and JavaScript banks, and the checks that stand in for an AST."""

import unittest

from code_coach import brace_checks as chk
from code_coach.engine import dart_available, run_code, typescript_available
from code_coach.leetcode.problems import PATTERNS as PY_PATTERNS
from code_coach.leetcode.problems_dart import PATTERNS as DART_PATTERNS
from code_coach.leetcode.problems_js import PATTERNS as JS_PATTERNS
from code_coach.leetcode.problems_ts import PATTERNS as TS_PATTERNS

TRANSLATED = {
    "dart": DART_PATTERNS,
    "javascript": JS_PATTERNS,
    "typescript": TS_PATTERNS,
}


class ParityTests(unittest.TestCase):
    """Switching language must keep your place, so every bank lines up."""

    def test_same_patterns_in_the_same_order(self):
        for language, patterns in TRANSLATED.items():
            with self.subTest(language=language):
                self.assertEqual(
                    [p.id for p in patterns], [p.id for p in PY_PATTERNS]
                )

    def test_same_problems_in_the_same_order(self):
        for language, patterns in TRANSLATED.items():
            for translated, py in zip(patterns, PY_PATTERNS):
                with self.subTest(language=language, pattern=py.id):
                    self.assertEqual(
                        [p.number for p in translated.problems],
                        [p.number for p in py.problems],
                    )

    def test_solutions_are_not_python(self):
        for language, patterns in TRANSLATED.items():
            for pattern in patterns:
                for problem in pattern.problems:
                    with self.subTest(language=language, problem=problem.number):
                        self.assertNotIn("def ", problem.code)
                        self.assertIn("{", problem.code)

    def test_the_bank_is_selected_by_language(self):
        from code_coach.leetcode.bank import patterns_for_language

        self.assertIs(patterns_for_language("dart"), DART_PATTERNS)
        self.assertIs(patterns_for_language("javascript"), JS_PATTERNS)
        self.assertIs(patterns_for_language("typescript"), TS_PATTERNS)
        self.assertIs(patterns_for_language("python"), PY_PATTERNS)
        # An unknown language falls back rather than failing.
        self.assertIs(patterns_for_language("cobol"), PY_PATTERNS)

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

    def test_javascript_function_keyword(self):
        code = "function twoSum(nums, target) {\n  return [];\n}"
        self.assertTrue(chk.defines_function(code, "twoSum"))
        funcs, _ = chk.top_level_names(code)
        self.assertIn("twoSum", funcs)

    def test_javascript_arrow_binding(self):
        # `const f = (n) => n * 2` declares by binding, not by keyword.
        self.assertTrue(chk.defines_function("const f = (n) => n * 2;", "f"))
        funcs, _ = chk.top_level_names("const f = (n) => n * 2;")
        self.assertIn("f", funcs)

    def test_template_literal_contents_are_ignored(self):
        self.assertFalse(chk.uses_while("const s = `while (x) {}`;"))

    def test_typescript_return_annotation_still_reads_as_a_definition(self):
        # `function f(...): number[] {` — the annotation sits between the
        # parameter list and the brace, and used to hide the definition.
        code = "function twoSum(nums: number[], target: number): number[] {\n  return [];\n}"
        self.assertTrue(chk.defines_function(code, "twoSum"))
        funcs, _ = chk.top_level_names(code)
        self.assertIn("twoSum", funcs)

    def test_typescript_annotated_arrow_is_a_definition(self):
        code = "const ok = (c: string): boolean => c.length > 0;"
        self.assertTrue(chk.defines_function(code, "ok"))

    def test_every_translated_bank_yields_a_function_requirement(self):
        # A build lesson with no "write this function" line would let an empty
        # answer look half-right.
        from code_coach.leetcode.bank import _requirements_for

        for language, patterns in TRANSLATED.items():
            problem = patterns[0].problems[0]
            labels = [
                label for label, _ in _requirements_for(problem, language)
            ]
            with self.subTest(language=language):
                self.assertTrue(
                    any("twoSum" in label for label in labels),
                    f"{language}: {labels}",
                )

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


class JavaScriptRunsTests(unittest.TestCase):
    """Node ships with the project's own toolchain, so these always run."""

    def test_hash_map_solutions_run_and_answer_correctly(self):
        pattern = next(p for p in JS_PATTERNS if p.id == "lc-hashmap")
        src = "\n\n".join(
            list(pattern.preamble) + [p.code for p in pattern.problems]
        )
        src += (
            "\n\nconsole.log(JSON.stringify(twoSum([2, 7, 11, 15], 9)));\n"
            "console.log(containsDuplicate([1, 2, 3, 1]));\n"
            "console.log(isAnagram('anagram', 'nagaram'));\n"
            "console.log(groupAnagrams(['eat', 'tea', 'tan']).length);\n"
        )
        out, err, code = run_code(src, language="javascript")
        self.assertEqual(code, 0, err[:400])
        self.assertEqual(out.split(), ["[0,1]", "true", "true", "2"])

    def test_linked_list_solutions_run(self):
        pattern = next(p for p in JS_PATTERNS if p.id == "lc-linked-list")
        src = "\n\n".join(
            list(pattern.preamble) + [p.code for p in pattern.problems]
        )
        src += (
            "\n\nlet head = null;\n"
            "for (const v of [3, 2, 1]) head = new ListNode(v, head);\n"
            "let n = reverseList(head);\nconst out = [];\n"
            "while (n) { out.push(n.val); n = n.next; }\n"
            "console.log(JSON.stringify(out));\n"
        )
        out, err, code = run_code(src, language="javascript")
        self.assertEqual(code, 0, err[:400])
        self.assertEqual(out.strip(), "[3,2,1]")

    def test_a_syntax_error_is_reported_not_raised(self):
        out, err, code = run_code("const x = ;", language="javascript")
        self.assertNotEqual(code, 0)
        self.assertTrue(err.strip())


@unittest.skipUnless(typescript_available(), "tsc not available")
class TypeScriptRunsTests(unittest.TestCase):
    def test_hash_map_solutions_type_check_and_run(self):
        pattern = next(p for p in TS_PATTERNS if p.id == "lc-hashmap")
        src = "\n\n".join(
            list(pattern.preamble) + [p.code for p in pattern.problems]
        )
        src += (
            "\n\nconsole.log(JSON.stringify(twoSum([2, 7, 11, 15], 9)));\n"
            "console.log(containsDuplicate([1, 2, 3, 1]));\n"
        )
        out, err, code = run_code(src, language="typescript")
        self.assertEqual(code, 0, err[:500])
        self.assertEqual(out.split(), ["[0,1]", "true"])

    def test_a_type_error_stops_the_run(self):
        # The whole point of TypeScript — running past a type error would
        # teach exactly the wrong lesson.
        out, err, code = run_code(
            'const x: number = "nope";\nconsole.log(x);', language="typescript"
        )
        self.assertNotEqual(code, 0)
        self.assertIn("TS2322", err)
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
