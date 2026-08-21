"""The course has to be a path someone can actually walk.

Every lesson must point at a section-and-mode the trainer really offers, the
order has to teach the keyboard the way it's taught, and progress has to come
from the records rather than being tracked separately — two sources of truth
about whether you finished lesson 3 is one too many.
"""

from __future__ import annotations

import unittest

from code_coach.typing.course import LESSONS, course_payload
from code_coach.typing.drills import THEMES_BY_ID, build_drill, catalog


def _offered() -> dict[str, set[str]]:
    return {e["id"]: {m["id"] for m in e["modes"]} for e in catalog()}


class CourseTests(unittest.TestCase):
    def test_every_lesson_points_at_a_real_drill(self) -> None:
        offered = _offered()
        for lesson in LESSONS:
            with self.subTest(lesson=lesson.number):
                self.assertIn(lesson.section, offered)
                self.assertIn(lesson.mode, offered[lesson.section])

    def test_lessons_are_numbered_without_gaps(self) -> None:
        numbers = [lesson.number for lesson in LESSONS]
        self.assertEqual(numbers, list(range(numbers[0], numbers[0] + len(LESSONS))))

    def test_it_opens_with_an_ordinary_mixed_run(self) -> None:
        """Lesson zero is a warm-up, not a test — somewhere to start typing
        before being told which row to care about."""
        self.assertEqual(LESSONS[0].section, "everything")
        self.assertEqual(LESSONS[0].mode, "random")

    def test_the_teaching_starts_on_the_home_row(self) -> None:
        """Fingers learn positions relative to where they rest, so everything
        else is taught as a reach out of home."""
        self.assertEqual(LESSONS[1].section, "home")

    def test_rows_are_taught_before_the_whole_alphabet(self) -> None:
        order = [lesson.section for lesson in LESSONS]
        self.assertLess(order.index("home"), order.index("top"))
        self.assertLess(order.index("top"), order.index("bottom"))
        self.assertLess(order.index("bottom"), order.index("letters"))
        self.assertLess(order.index("letters"), order.index("symbols"))

    def test_every_lesson_says_why_it_exists(self) -> None:
        for lesson in LESSONS:
            self.assertTrue(lesson.why.strip(), lesson.number)
            self.assertTrue(lesson.title.strip(), lesson.number)

    def test_accuracy_targets_are_plausible(self) -> None:
        for lesson in LESSONS:
            self.assertGreaterEqual(lesson.target_accuracy, 70, lesson.number)
            self.assertLessEqual(lesson.target_accuracy, 100, lesson.number)

    def test_reaction_lessons_are_not_judged_on_words_a_minute(self) -> None:
        """A wpm taken over single keypresses says more about how long the
        drill was than about the typist."""
        for lesson in LESSONS:
            if lesson.mode in ("whack", "recall", "sweep"):
                self.assertEqual(lesson.target_wpm, 0, lesson.number)

    def test_no_records_means_start_at_the_beginning(self) -> None:
        payload = course_payload({})
        self.assertEqual(payload["current"], LESSONS[0].number)
        self.assertEqual(payload["done"], 0)
        self.assertEqual(payload["total"], len(LESSONS))

    def test_lesson_zero_is_not_mistaken_for_no_lesson(self) -> None:
        """The warm-up is numbered zero, which is falsy — treating it as
        "nothing to do" sent everyone to the last lesson."""
        payload = course_payload({})
        self.assertEqual(payload["current"], 0)

    def test_a_passing_record_completes_its_lesson(self) -> None:
        first = LESSONS[0]
        payload = course_payload(
            {
                f"{first.section}:{first.mode}": {
                    "best_wpm": 40,
                    "best_accuracy": first.target_accuracy,
                    "runs": 1,
                }
            }
        )
        self.assertTrue(payload["lessons"][0]["done"])
        self.assertEqual(payload["current"], LESSONS[1].number)

    def test_missing_the_accuracy_target_does_not_complete_it(self) -> None:
        first = LESSONS[0]
        payload = course_payload(
            {
                f"{first.section}:{first.mode}": {
                    "best_wpm": 200,
                    "best_accuracy": first.target_accuracy - 1,
                    "runs": 9,
                }
            }
        )
        self.assertFalse(payload["lessons"][0]["done"])
        self.assertEqual(payload["current"], LESSONS[0].number)

    def test_missing_the_speed_target_does_not_complete_it(self) -> None:
        speed = next(lesson for lesson in LESSONS if lesson.target_wpm)
        payload = course_payload(
            {
                f"{speed.section}:{speed.mode}": {
                    "best_wpm": speed.target_wpm - 1,
                    "best_accuracy": 100,
                    "runs": 3,
                }
            }
        )
        entry = next(
            e for e in payload["lessons"] if e["number"] == speed.number
        )
        self.assertFalse(entry["done"])

    def test_current_is_the_first_gap_not_the_last_finished(self) -> None:
        """Skipping ahead shouldn't hide the lesson you actually skipped."""
        later = LESSONS[4]
        payload = course_payload(
            {
                f"{later.section}:{later.mode}": {
                    "best_wpm": 999,
                    "best_accuracy": 100,
                    "runs": 1,
                }
            }
        )
        self.assertEqual(payload["current"], LESSONS[0].number)
        self.assertEqual(payload["done"], 1)

    def test_lessons_carry_display_names(self) -> None:
        for entry in course_payload({})["lessons"]:
            self.assertTrue(entry["section_name"])
            self.assertTrue(entry["mode_name"])
            self.assertTrue(entry["theme_name"])
            self.assertNotEqual(entry["section_name"], entry["section"])

    def test_every_lesson_theme_exists(self) -> None:
        for lesson in LESSONS:
            self.assertIn(lesson.theme, THEMES_BY_ID, lesson.number)

    def test_lessons_build_a_real_drill_end_to_end(self) -> None:
        """The strongest check available: every lesson must actually run."""
        for lesson in LESSONS:
            drill = build_drill(
                lesson.section, lesson.mode, theme_id=lesson.theme, seed="course"
            )
            self.assertTrue(drill.targets, lesson.number)

    def test_the_course_covers_the_whole_keyboard(self) -> None:
        sections = {lesson.section for lesson in LESSONS}
        for needed in ("home", "top", "bottom", "numbers", "symbols", "coding"):
            self.assertIn(needed, sections)


if __name__ == "__main__":
    unittest.main()
