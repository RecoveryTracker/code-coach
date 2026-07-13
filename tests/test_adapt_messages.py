"""
Coach feedback quality (adapt.py): the message must diagnose the real
mistake, and build lessons must never say "type this line" or leak the
solution outside the Hint ladder.

Run: .venv/bin/python -m unittest discover -s tests
"""

from __future__ import annotations

import unittest

from code_coach.practice.session import evaluate_drill
from code_coach.skills.drills import get_drill


# Build lessons score sequentially, so a realistic buffer has the earlier
# steps done (this mirrors the real student situation that hit this bug).
PREFIX = (
    'print("hello")\n'
    'name = "Ada"\n'
    "print(name)\n"
    'city = "Wenatchee"\n'
    "print(city)\n"
)


class QuotedNumberDiagnosis(unittest.TestCase):
    """var = "5" where a whole number is expected — the classic slip."""

    def setUp(self):
        self.drill = get_drill("foundations-l2")

    def test_quoted_number_gets_targeted_message(self):
        code = PREFIX + 'favorite_number = "5"\nprint(favorite_number)'
        r = evaluate_drill(self.drill, code, coach_level=1, exercise_index=3)
        self.assertFalse(r["checks"][3]["passed"])
        self.assertIn("quotes", r["observation"].lower())
        self.assertIn("favorite_number = 7", r["observation"])

    def test_unquoted_number_passes(self):
        code = PREFIX + "favorite_number = 5\nprint(favorite_number)"
        r = evaluate_drill(self.drill, code, coach_level=1, exercise_index=3)
        self.assertTrue(r["checks"][3]["passed"])


class BuildFallbackTone(unittest.TestCase):
    def test_build_fallback_never_says_type_this_line(self):
        drill = get_drill("foundations-l2")
        r = evaluate_drill(
            drill, "favorite_number == 5", coach_level=1, exercise_index=3
        )
        obs = r["observation"] or ""
        self.assertNotIn("type this line", obs.lower())
        # And it must not leak the solution lines
        self.assertNotIn("favorite_number = 7", obs)


if __name__ == "__main__":
    unittest.main()
