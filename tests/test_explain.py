"""
Tests for the code explainer (code_coach/explain.py). Assert structure and key
attributions, not exact prose (wording may evolve).

Run: .venv/bin/python -m unittest discover -s tests
"""

from __future__ import annotations

import unittest

from code_coach.explain import explain_code


class ExplainStructure(unittest.TestCase):
    def test_loop_walkthrough_and_output(self):
        r = explain_code("for i in range(3):\n    print(i)\n")
        self.assertTrue(r["ok"])
        self.assertTrue(any("loop" in L["text"].lower() for L in r["lines"]))
        joined = " ".join(r["output_notes"])
        self.assertIn("0", joined)
        self.assertIn("2", joined)

    def test_variable_and_fstring(self):
        r = explain_code('name = "Ada"\nprint(f"hi {name}")\n')
        self.assertTrue(r["ok"])
        self.assertTrue(any("variable" in L["text"].lower() for L in r["lines"]))

    def test_nameerror_reported(self):
        r = explain_code("print(greeting)\n")
        self.assertIsNotNone(r["error_note"])
        self.assertIn("NameError", r["error_note"])

    def test_no_print_is_explained(self):
        r = explain_code("x = 5\ny = x * 2\n")
        joined = " ".join(r["output_notes"]).lower()
        self.assertIn("print", joined)

    def test_syntax_error_gives_error_note_not_crash(self):
        r = explain_code("def (:\n")
        self.assertTrue(r["ok"])
        self.assertIsNotNone(r["error_note"])

    def test_empty_code(self):
        r = explain_code("   \n  \n")
        self.assertTrue(r["ok"])
        self.assertEqual(r["lines"], [])

    def test_infinite_loop_notes_timeout(self):
        # Runs with a ~3s trace timeout; asserts it reports non-completion.
        r = explain_code("while True:\n    pass\n")
        joined = " ".join(r["output_notes"]).lower()
        self.assertTrue("never finished" in joined or "stopped" in joined)


if __name__ == "__main__":
    unittest.main()
