"""
Tests for curriculum navigation (code_coach/curriculum/runtime.py):
class/lesson bounds, boundary crossing, and review round-trips.

Run: .venv/bin/python -m unittest discover -s tests
"""

from __future__ import annotations

import unittest

from code_coach.curriculum.catalog import CLASSES, get_class
from code_coach.curriculum.runtime import (
    back_from_review,
    enter_review,
    goto_position,
    navigate_step,
)
from code_coach.progress.store import StudentProgress

FIRST_CLASS = CLASSES[0].id
SECOND_CLASS = CLASSES[1].id if len(CLASSES) > 1 else CLASSES[0].id


class GotoPosition(unittest.TestCase):
    def test_sets_class_and_lesson(self):
        p = StudentProgress()
        goto_position(p, class_id=SECOND_CLASS, lesson_number=1)
        self.assertEqual(p.curriculum_class, SECOND_CLASS)
        self.assertEqual(p.curriculum_lesson, 1)

    def test_lesson_clamped_to_valid_range(self):
        p = StudentProgress()
        goto_position(p, class_id=FIRST_CLASS, lesson_number=999)
        max_l = len(get_class(FIRST_CLASS).lessons)
        self.assertEqual(p.curriculum_lesson, max_l)
        goto_position(p, class_id=FIRST_CLASS, lesson_number=-5)
        self.assertEqual(p.curriculum_lesson, 1)


class NavigateStep(unittest.TestCase):
    def test_lesson_delta_moves_within_class(self):
        p = StudentProgress()
        goto_position(p, class_id=FIRST_CLASS, lesson_number=1)
        navigate_step(p, lesson_delta=1)
        self.assertEqual(p.curriculum_class, FIRST_CLASS)
        self.assertEqual(p.curriculum_lesson, 2)

    def test_class_delta_resets_lesson_to_one(self):
        p = StudentProgress()
        goto_position(p, class_id=FIRST_CLASS, lesson_number=2)
        navigate_step(p, class_delta=1)
        self.assertEqual(p.curriculum_class, SECOND_CLASS)
        self.assertEqual(p.curriculum_lesson, 1)

    def test_class_delta_clamps_at_first(self):
        p = StudentProgress()
        goto_position(p, class_id=FIRST_CLASS, lesson_number=1)
        navigate_step(p, class_delta=-1)
        self.assertEqual(p.curriculum_class, FIRST_CLASS)

    def test_lesson_delta_past_end_crosses_into_next_class(self):
        p = StudentProgress()
        last_lesson = len(get_class(FIRST_CLASS).lessons)
        goto_position(p, class_id=FIRST_CLASS, lesson_number=last_lesson)
        navigate_step(p, lesson_delta=1)
        # Either advanced into the next class at lesson 1, or (single-class
        # catalog) stayed put — never an invalid lesson.
        if SECOND_CLASS != FIRST_CLASS:
            self.assertEqual(p.curriculum_class, SECOND_CLASS)
            self.assertEqual(p.curriculum_lesson, 1)


class ReviewRoundTrip(unittest.TestCase):
    def test_enter_then_back_restores_position(self):
        p = StudentProgress()
        goto_position(p, class_id=FIRST_CLASS, lesson_number=2)
        enter_review(p, "lesson1")
        self.assertEqual(p.review_skill, "lesson1")
        back_from_review(p)
        self.assertIsNone(p.review_skill)
        self.assertEqual(p.curriculum_class, FIRST_CLASS)
        self.assertEqual(p.curriculum_lesson, 2)




class ReviewDue(unittest.TestCase):
    """Light spaced repetition: skills go 'due' after a few days idle."""

    def test_stale_skill_is_due_recent_is_not(self):
        from datetime import datetime, timedelta, timezone
        from code_coach.practice.session import progress_summary
        from code_coach.progress.store import DrillRecord

        p = StudentProgress()
        old = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        recent = datetime.now(timezone.utc).isoformat()
        # loops-for-1 (skill: loops) practiced 5 days ago -> due
        p.completed_drills["loops-for-1"] = DrillRecord(count=1, last_at=old)
        # cond-if-1 (skill: conditionals) practiced now -> not due
        p.completed_drills["cond-if-1"] = DrillRecord(count=1, last_at=recent)
        due = progress_summary(p)["review_due"]
        ids = [d["skill_id"] for d in due]
        self.assertIn("loops", ids)
        self.assertNotIn("conditionals", ids)
        self.assertGreaterEqual(due[0]["days"], 5)


if __name__ == "__main__":
    unittest.main()
