"""A print of a name defined nowhere fails, even when the output is right.

Found in use: on page 15 ("Only when"), `console.log(big)` without
quotes failed the exercises where the condition held and passed their
twins where it did not - the line never ran, so the missing quotes were
never discovered. The output was right; the program was not.
"""

from __future__ import annotations

import unittest

from code_coach.workbook import pages, undefined_print


class DetectorTests(unittest.TestCase):

    def test_it_never_flags_a_reference_answer(self) -> None:
        """Every correct answer in the workbook, in every language it
        checks. A false alarm here would fail someone's right answer."""
        for language in ("javascript", "typescript", "python", "dart"):
            for p in pages(language):
                for e in p.exercises:
                    code = e.answer(language)
                    if code:
                        with self.subTest(language=language, exercise=e.id):
                            self.assertEqual(undefined_print(code, language), "")

    def test_it_finds_the_missing_quotes(self) -> None:
        cases = {
            "javascript": "const n = 3;\nif (n > 5) {\n  console.log(big);\n}",
            "python": "n = 3\nif n > 5:\n    print(big)",
            "dart": "void main() {\n  var n = 3;\n  if (n > 5) print(big);\n}",
        }
        for language, code in cases.items():
            with self.subTest(language=language):
                self.assertEqual(undefined_print(code, language), "big")

    def test_a_defined_name_or_a_constant_is_fine(self) -> None:
        self.assertEqual(undefined_print("const big = 1;\nconsole.log(big);", "javascript"), "")
        self.assertEqual(undefined_print("console.log(undefined);", "javascript"), "")
        self.assertEqual(undefined_print("print(None)", "python"), "")
        self.assertEqual(undefined_print('console.log("big");', "javascript"), "")


class RouteTests(unittest.TestCase):
    """Through the real check, on the page it was found on."""

    def _check(self, code: str):
        from code_coach.api.schemas import WorkbookCheckRequest
        from code_coach.api.server import workbook_check

        return workbook_check(WorkbookCheckRequest(
            page_id="only-when", exercise_id="only-when-02",
            code=code, language="javascript"))

    def test_missing_quotes_on_a_branch_that_does_not_run_fail(self) -> None:
        got = self._check("const n = 3;\nif (n > 5) {\n  console.log(big);\n}")
        self.assertFalse(got.passed)
        self.assertIn("big", got.problem)
        self.assertIn('"big"', got.problem)

    def test_with_quotes_it_passes(self) -> None:
        got = self._check('const n = 3;\nif (n > 5) {\n  console.log("big");\n}')
        self.assertTrue(got.passed)
        self.assertEqual(got.problem, "")


if __name__ == "__main__":
    unittest.main()
