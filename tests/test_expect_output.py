"""
Output-pinned build goals (DrillStep.expect_output): structure alone isn't
enough — a Run whose stdout matches is required, and wrong output is called
out even when the code's structure looks right.

Run: .venv/bin/python -m unittest discover -s tests
"""

from __future__ import annotations

import unittest

from code_coach.curriculum.catalog import resolve_drill
from code_coach.practice.session import evaluate_drill

CODE = "for i in range(3):\n    print(i)"


class OutputPinnedGoals(unittest.TestCase):
    def setUp(self):
        _, self.drill = resolve_drill("loops", 2)

    def test_structure_alone_does_not_complete(self):
        r = evaluate_drill(self.drill, CODE, coach_level=1, exercise_index=0)
        self.assertFalse(r["checks"][0]["passed"])
        # The checklist shows the output row with a Run prompt
        labels = [q["label"] for q in r["requirements"]]
        self.assertTrue(any("prints exactly" in L for L in labels))
        self.assertIn("Run", r["observation"])

    def test_matching_run_completes(self):
        r = evaluate_drill(
            self.drill, CODE, coach_level=1, exercise_index=0,
            ran=True, stdout="0\n1\n2\n", exit_code=0,
        )
        self.assertTrue(r["checks"][0]["passed"])

    def test_wrong_output_fails_even_with_right_structure(self):
        r = evaluate_drill(
            self.drill,
            "for i in range(4):\n    print(i)",
            coach_level=1, exercise_index=0,
            ran=True, stdout="0\n1\n2\n3\n", exit_code=0,
        )
        self.assertFalse(r["checks"][0]["passed"])
        self.assertIn("prints exactly", r["observation"])

    def test_trailing_whitespace_normalized(self):
        r = evaluate_drill(
            self.drill, CODE, coach_level=1, exercise_index=0,
            ran=True, stdout="0 \n1\n2\n\n", exit_code=0,
        )
        self.assertTrue(r["checks"][0]["passed"])

    def test_crash_does_not_pass(self):
        r = evaluate_drill(
            self.drill, CODE, coach_level=1, exercise_index=0,
            ran=True, stdout="0\n1\n2\n", exit_code=1,
        )
        self.assertFalse(r["checks"][0]["passed"])


class StructureOnlyGoalsUnaffected(unittest.TestCase):
    def test_foundations_build_completes_without_run(self):
        _, drill = resolve_drill("foundations", 2)
        code = 'print("hi")'
        r = evaluate_drill(drill, code, coach_level=1, exercise_index=0)
        self.assertTrue(r["checks"][0]["passed"])


if __name__ == "__main__":
    unittest.main()
