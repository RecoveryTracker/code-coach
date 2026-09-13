"""
Tests for the v2 → v3 StudentProgress migration (Phase 5):
  - old `class1_batch` / `class1_lines_done` move into the per-class dicts
  - old `difficulty` alias is accepted on read, not written back
  - round-trip is stable and the saved file is clean v3

Run: .venv/bin/python -m unittest discover -s tests
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from code_coach.progress.store import ProgressStore, StudentProgress

V2_FILE = {
    "version": 2,
    "mode": "progressive",
    "coach_level": 1,
    "difficulty": 1,
    "selected_skills": [],
    "completed_drills": {"class-1-dictation": {"count": 3, "last_at": None}},
    "completed_waypoints": {},
    "current_drill_id": "class-1-dictation",
    "total_completes": 3,
    "skill_xp": {"basics": 3},
    "class1_batch": 31,
    "class1_lines_done": 16,
    "dictation_level": 3,
    "curriculum_class": "foundations",
    "curriculum_lesson": 1,
    "review_skill": None,
    "exercise_index": 0,
    "updated_at": "2026-07-11T00:00:00+00:00",
}


class MigrationV2ToV3(unittest.TestCase):
    def setUp(self):
        self.path = Path(tempfile.mkdtemp()) / "progress.json"
        self.path.write_text(json.dumps(V2_FILE), encoding="utf-8")
        self.store = ProgressStore(self.path)

    def test_counters_migrate_into_per_class_dicts(self):
        p = self.store.load()
        self.assertEqual(p.version, 3)
        self.assertEqual(p.batch_for("foundations"), 31)
        self.assertEqual(p.lines_for("foundations"), 16)
        self.assertEqual(p.batch_for("decisions"), 0)

    def test_everything_else_survives(self):
        p = self.store.load()
        self.assertEqual(p.coach_level, 1)
        self.assertEqual(p.dictation_level, 3)
        self.assertEqual(p.total_completes, 3)
        self.assertEqual(p.completed_drills["class-1-dictation"].count, 3)

    def test_saved_file_is_clean_v3(self):
        self.store.save(self.store.load())
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(raw["version"], 3)
        self.assertNotIn("difficulty", raw)
        self.assertNotIn("class1_batch", raw)
        self.assertNotIn("class1_lines_done", raw)
        self.assertEqual(raw["dictation_batches"], {"foundations": 31})

    def test_round_trip_stable(self):
        p1 = self.store.save(self.store.load())
        p2 = self.store.load()
        self.assertEqual(p1.dictation_batches, p2.dictation_batches)
        self.assertEqual(p1.dictation_lines, p2.dictation_lines)

    def test_v3_file_loads_directly(self):
        p = StudentProgress()
        p.bump_batch("loops")
        p.add_lines("loops", 8)
        self.store.save(p)
        p2 = self.store.load()
        self.assertEqual(p2.batch_for("loops"), 1)
        self.assertEqual(p2.lines_for("loops"), 8)

    def test_old_difficulty_only_file_maps_to_coach_level(self):
        raw = dict(V2_FILE)
        del raw["coach_level"]
        raw["difficulty"] = 2
        self.path.write_text(json.dumps(raw), encoding="utf-8")
        p = self.store.load()
        self.assertEqual(p.coach_level, 2)


if __name__ == "__main__":
    unittest.main()


class CounterRoundTripTests(unittest.TestCase):
    """Every practice counter has to survive being saved and read back.

    This is here because three of them did not. A counter is declared on
    StudentProgress and must also be named in the loader, and the three
    that were missing from the loader failed in the quietest way
    available: the field existed, writing to it worked, saving wrote it
    to the file — and the next read dropped it. So a count went up,
    persisted, and came back as one every single time.

    It surfaced as a magnet puzzle solved twice that still said "done
    1x". The CSS quizzes and the typing drills had been doing it since
    the day they shipped and nobody had looked.

    So this walks the counters rather than listing them. A test that
    named them would have to be remembered too, which is the thing that
    already failed.
    """

    def _counters(self) -> list[str]:
        from dataclasses import fields

        from code_coach.progress.store import StudentProgress

        return [
            f.name for f in fields(StudentProgress)
            if f.name.endswith("_done") and f.name != "workbook_done"
        ]

    def test_there_are_some_to_check(self) -> None:
        self.assertGreaterEqual(len(self._counters()), 5)

    def test_every_counter_survives_a_save_and_load(self) -> None:
        import tempfile
        from pathlib import Path

        from code_coach.progress.store import ProgressStore, StudentProgress

        for name in self._counters():
            with self.subTest(counter=name):
                folder = tempfile.mkdtemp(prefix="counter-test-")
                store = ProgressStore(Path(folder) / "progress.json")
                progress = StudentProgress()
                bumped = getattr(progress, name)
                from code_coach.progress.store import _bump

                _bump(bumped, "thing-one")
                _bump(bumped, "thing-one")
                _bump(bumped, "thing-two")
                store.save(progress)

                back = store.load()
                counts = {k: v.count for k, v in getattr(back, name).items()}
                self.assertEqual(
                    counts, {"thing-one": 2, "thing-two": 1},
                    f"{name} did not come back from the file — it is "
                    f"probably missing from the loader")

    def test_every_counter_has_a_last_at_that_survives(self) -> None:
        """The dates decide what is offered next. A counter that keeps
        its count and loses its dates makes the picker offer things in
        the order they were first tried, for ever."""
        import tempfile
        from pathlib import Path

        from code_coach.progress.store import (
            ProgressStore,
            StudentProgress,
            _bump,
        )

        for name in self._counters():
            with self.subTest(counter=name):
                folder = tempfile.mkdtemp(prefix="counter-date-")
                store = ProgressStore(Path(folder) / "progress.json")
                progress = StudentProgress()
                _bump(getattr(progress, name), "thing")
                store.save(progress)

                back = getattr(store.load(), name)
                self.assertTrue(back["thing"].last_at)
