"""Running out of a pattern class moves on to the next one.

A pattern class holds a fixed set of answers. Looping back to its first
exercise once you've been through them is busywork, and worse, it looks like
the app is stuck — the next pattern is the point of finishing this one.

Foundations is the exception: its lines are generated rather than drawn from a
bank, so there is no end to run out of.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from code_coach.api import server
from code_coach.api.schemas import GotoLessonRequest
from code_coach.leetcode.bank import unit_count
from code_coach.progress.store import ProgressStore


class GraduationTests(unittest.TestCase):
    def setUp(self) -> None:
        # A throwaway progress file, so tests can't disturb real progress or
        # each other.
        self._real_store = server._store
        server._store = ProgressStore(Path(tempfile.mkdtemp()) / "progress.json")
        progress = server._store.load()
        progress.language = "python"
        # Whole functions: one unit per problem, so a class ends quickly.
        progress.dictation_level = 5
        server._store.save(progress)

    def tearDown(self) -> None:
        server._store = self._real_store

    def _goto(self, class_id: str) -> None:
        server.practice_goto_lesson(
            GotoLessonRequest(class_id=class_id, lesson_number=1)
        )

    def test_finishing_hash_maps_lands_on_two_pointers(self) -> None:
        self._goto("lc-hashmap")
        session = server.practice_more_lines()
        self.assertEqual(session.class_id, "lc-two-pointers")

    def test_it_lands_at_the_start_of_the_next_class(self) -> None:
        self._goto("lc-hashmap")
        session = server.practice_more_lines()
        self.assertEqual(session.lesson_number, 1)
        self.assertEqual(session.class_position, 0)

    def test_it_keeps_going_rather_than_stopping_at_the_second(self) -> None:
        self._goto("lc-hashmap")
        reached = []
        for _ in range(4):
            reached.append(server.practice_more_lines().class_id)
        self.assertEqual(
            reached[:3], ["lc-two-pointers", "lc-sliding-window", "lc-stack"]
        )

    def test_a_class_with_material_left_does_not_graduate(self) -> None:
        """At single-line level there are dozens of units, so one window in
        you're still in the same class."""
        progress = server._store.load()
        progress.dictation_level = 1
        server._store.save(progress)
        self._goto("lc-hashmap")
        self.assertGreater(unit_count("lc-hashmap", 1), 8)
        self.assertEqual(server.practice_more_lines().class_id, "lc-hashmap")

    def test_foundations_never_graduates(self) -> None:
        self._goto("foundations")
        for _ in range(6):
            self.assertEqual(server.practice_more_lines().class_id, "foundations")

    def test_the_last_class_wraps_rather_than_falling_off_the_end(self) -> None:
        self._goto("lc-dp")
        session = server.practice_more_lines()
        self.assertEqual(session.class_id, "lc-dp")

    def test_position_and_total_describe_the_whole_class(self) -> None:
        progress = server._store.load()
        progress.dictation_level = 1
        server._store.save(progress)
        self._goto("lc-hashmap")
        first = server.practice_more_lines()
        second = server.practice_more_lines()
        self.assertEqual(first.class_total, unit_count("lc-hashmap", 1))
        self.assertLess(first.class_position, second.class_position)


if __name__ == "__main__":
    unittest.main()
