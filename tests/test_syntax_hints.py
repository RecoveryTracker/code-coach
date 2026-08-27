"""Reminders about code that will not run.

The bar for these is high in one specific direction: a hint that fires on
working code is worse than no hint at all, because free mode exists to be left
alone in. So most of these check silence.
"""

from __future__ import annotations

import unittest

from code_coach.syntax_hints import hints_for

WORKING = {
    "python": "def add(a, b):\n    return a + b\n\nprint(add(1, 2))\n",
    "javascript": "function add(a, b) {\n  return a + b;\n}\n\nconsole.log(add(1, 2));\n",
    "typescript": "function add(a: number, b: number): number {\n  return a + b;\n}\n",
    "dart": "int add(int a, int b) => a + b;\n\nvoid main() {\n  print(add(1, 2));\n}\n",
    "c": '#include <stdio.h>\n\nint main(void) {\n    printf("hi\\n");\n    return 0;\n}\n',
    "rust": 'fn main() {\n    println!("{}", 1 + 2);\n}\n',
    "sql": "SELECT name\nFROM users\nWHERE id = 1;\n",
}


class SilenceTests(unittest.TestCase):
    def test_nothing_to_say_about_working_code(self) -> None:
        for language, code in WORKING.items():
            with self.subTest(language=language):
                self.assertEqual(hints_for(code, language), [])

    def test_nothing_to_say_about_an_empty_editor(self) -> None:
        for language in WORKING:
            with self.subTest(language=language):
                self.assertEqual(hints_for("", language), [])
                self.assertEqual(hints_for("   \n\n", language), [])

    def test_a_bracket_inside_a_string_is_not_structure(self) -> None:
        """The commonest way a checker like this embarrasses itself."""
        self.assertEqual(hints_for('const s = "a ( b";\n', "javascript"), [])
        self.assertEqual(hints_for("s = 'a ( b'\n", "python"), [])

    def test_a_bracket_inside_a_comment_is_not_structure(self) -> None:
        self.assertEqual(hints_for("// an unmatched ( here\n", "javascript"), [])
        self.assertEqual(hints_for("# an unmatched ( here\n", "python"), [])
        self.assertEqual(hints_for("-- an unmatched ( here\n", "sql"), [])

    def test_an_apostrophe_in_a_comment_is_not_a_quote(self) -> None:
        self.assertEqual(hints_for("// don't worry\n", "javascript"), [])

    def test_an_escaped_quote_does_not_open_a_string(self) -> None:
        self.assertEqual(hints_for('const s = "a \\" b";\n', "javascript"), [])


class CatchTests(unittest.TestCase):
    def test_an_unclosed_quote(self) -> None:
        for language, code in (
            ("python", "name = 'Alex\n"),
            ("javascript", "const a = 'hi;\n"),
            ("dart", "final a = 'hi;\n"),
        ):
            found = hints_for(code, language)
            with self.subTest(language=language):
                self.assertTrue(found)
                self.assertIn("clos", found[0].message.lower())

    def test_an_unclosed_bracket(self) -> None:
        for language, code in (
            ("python", "x = (1 + 2\n"),
            ("javascript", "function f() {\n  return 1;\n"),
            ("c", "int main(void) {\n    return 0;\n"),
        ):
            found = hints_for(code, language)
            with self.subTest(language=language):
                self.assertTrue(found)

    def test_the_wrong_closing_bracket(self) -> None:
        found = hints_for("const a = [1, 2);\n", "javascript")
        self.assertTrue(found)
        self.assertIn("match", found[0].message.lower())

    def test_a_python_block_with_no_colon(self) -> None:
        found = hints_for("if x > 1\n    print(1)\n", "python")
        self.assertTrue(found)
        self.assertIn("colon", found[0].message.lower())

    def test_a_python_block_with_no_body(self) -> None:
        found = hints_for("def f():\nreturn 1\n", "python")
        self.assertTrue(found)
        self.assertIn("indent", found[0].message.lower())

    def test_tabs_and_spaces_in_one_indent(self) -> None:
        found = hints_for("def f():\n \tpass\n", "python")
        self.assertTrue(any("tabs and spaces" in h.message for h in found))


class ShapeTests(unittest.TestCase):
    def test_a_hint_names_a_line_and_says_something(self) -> None:
        for language, code in (
            ("python", "x = (1 + 2\n"),
            ("javascript", "const a = [1, 2);\n"),
        ):
            for hint in hints_for(code, language):
                with self.subTest(language=language):
                    self.assertGreaterEqual(hint.line, 1)
                    self.assertGreater(len(hint.message), 15)
                    # Not necessarily a capital: "'(' was never closed."
                    # opens on the bracket it is talking about. The rule is
                    # that it never opens on a lowercase word.
                    self.assertFalse(hint.message[0].islower())
                    self.assertTrue(hint.message.rstrip().endswith("."))

    def test_one_missing_bracket_does_not_start_an_avalanche(self) -> None:
        """A cascade from a single mistake is noise; the first one is the one
        to fix."""
        code = "function f() {\n  if (a) {\n    while (b) {\n      go();\n"
        self.assertLessEqual(len(hints_for(code, "javascript")), 3)

    def test_at_most_one_hint_per_line(self) -> None:
        code = "const a = ['x;\n"
        lines = [h.line for h in hints_for(code, "javascript")]
        self.assertEqual(len(lines), len(set(lines)))

    def test_hints_come_in_line_order(self) -> None:
        code = "function f() {\n  const a = [1;\n"
        lines = [h.line for h in hints_for(code, "javascript")]
        self.assertEqual(lines, sorted(lines))


class EndpointTests(unittest.TestCase):
    def test_it_answers(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import HintsRequest

        got = server.hints(HintsRequest(code="name = 'Alex", language="python"))
        self.assertTrue(got.hints)
        self.assertEqual(got.hints[0].line, 1)

    def test_it_stays_quiet_on_working_code(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import HintsRequest

        for language, code in WORKING.items():
            with self.subTest(language=language):
                got = server.hints(HintsRequest(code=code, language=language))
                self.assertEqual(got.hints, [])


if __name__ == "__main__":
    unittest.main()
