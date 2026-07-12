"""
Regression tests for the type-along advance behavior.

Run: .venv/bin/python -m unittest discover -s tests
(No pytest dependency — pure stdlib unittest.)

Covers the two bugs reported 2026-07-11:
  1. A line "completed" before the last brace/quote was typed
     (root cause was Monaco auto-closing; a frontend option, tested by the
     `check_block` artifact case here — a stray closing char must NOT match).
  2. A correctly typed line did not advance
     (root cause: sequential blocking on the endless type-along; an earlier
     line's artifact force-failed every later line).
"""

from __future__ import annotations

import unittest

from code_coach.dictation.bank import check_block
from code_coach.dictation.session import make_class1_batch
from code_coach.practice.session import evaluate_drill
from code_coach.skills.drills import get_drill


class CheckBlockArtifacts(unittest.TestCase):
    def test_exact_line_matches(self):
        self.assertTrue(check_block('print("hi")', 'print("hi")'))

    def test_stray_closing_brace_does_not_match(self):
        # Auto-close used to leave this; it must read as "not done yet".
        self.assertFalse(check_block('print("hi"))', 'print("hi")'))

    def test_doubled_quote_does_not_match(self):
        self.assertFalse(check_block('print("hi"")', 'print("hi")'))

    def test_partial_line_does_not_match(self):
        self.assertFalse(check_block('print("hi"', 'print("hi")'))


class DictationScoresIndependently(unittest.TestCase):
    def setUp(self):
        self.drill = make_class1_batch(seed="local-student", batch=0, level=1)

    def test_is_dictation(self):
        self.assertIn("dictation", self.drill.tags)

    def test_window_has_no_duplicate_examples(self):
        labels = [s.label for s in self.drill.steps]
        self.assertEqual(len(labels), len(set(labels)))

    def test_earlier_artifact_does_not_block_later_lines(self):
        s = self.drill.steps
        buggy_first = s[0].label.rstrip() + ")"  # stray brace on line 0
        buf = "\n".join([buggy_first, s[1].label, s[2].label])
        res = evaluate_drill(self.drill, buf, coach_level=1)
        checks = res["checks"]
        self.assertFalse(checks[0]["passed"])  # artifact line fails
        self.assertTrue(checks[1]["passed"])   # later lines score on their own
        self.assertTrue(checks[2]["passed"])

    def test_current_line_advances_when_typed(self):
        s = self.drill.steps
        # Student is on exercise 0; types exactly it.
        res = evaluate_drill(self.drill, s[0].label, coach_level=1)
        self.assertTrue(res["checks"][0]["passed"])

    def test_untyped_line_does_not_falsely_pass(self):
        s = self.drill.steps
        res = evaluate_drill(self.drill, s[0].label, coach_level=1)
        # A different, not-yet-typed line must remain unpassed.
        self.assertFalse(res["checks"][1]["passed"])


class CoachMessageFollowsCurrentExercise(unittest.TestCase):
    """The 'type this line' banner must describe the exercise the student is
    on, not the first-unpassed line (they can differ once scoring is
    independent and the buffer is out of forward order)."""

    def setUp(self):
        self.drill = make_class1_batch(seed="local-student", batch=0, level=1)

    def test_observation_targets_given_exercise_index(self):
        s = self.drill.steps
        # Buffer that matches no line; student says they are on exercise 2.
        res = evaluate_drill(self.drill, "x", coach_level=1, exercise_index=2)
        self.assertEqual(res["adapt_example"], s[2].label)
        self.assertIn(s[2].label, res["observation"])

    def test_without_index_falls_back_to_first_unpassed(self):
        s = self.drill.steps
        res = evaluate_drill(self.drill, "x", coach_level=1)
        self.assertEqual(res["adapt_example"], s[0].label)

    def test_out_of_range_index_is_clamped(self):
        s = self.drill.steps
        res = evaluate_drill(
            self.drill, "x", coach_level=1, exercise_index=999
        )
        self.assertEqual(res["adapt_example"], s[-1].label)


class BuildLessonsStaySequential(unittest.TestCase):
    def test_later_step_blocked_until_earlier_done(self):
        d = get_drill("basics-var-1")
        self.assertNotIn("dictation", d.tags or [])
        # print(score) alone satisfies step[1]'s pattern in isolation …
        self.assertTrue(d.steps[1].check("print(score)"))
        # … but sequential blocking must keep it False (assign not done).
        res = evaluate_drill(d, "print(score)", coach_level=2)
        self.assertFalse(res["checks"][0]["passed"])
        self.assertFalse(res["checks"][1]["passed"])


if __name__ == "__main__":
    unittest.main()
