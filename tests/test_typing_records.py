"""Records must only move when a run actually beat something.

A personal best that creeps upward on its own is worse than no record at all,
so the interesting cases here are the ones where a number should *not* change.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from code_coach.typing.guide import guide_payload
from code_coach.typing.keys import ALL_KEYS, FINGER_NAMES
from code_coach.typing.records import MIN_KEYSTROKES, RecordStore


def _store() -> RecordStore:
    return RecordStore(Path(tempfile.mkdtemp()) / "records.json")


class RecordTests(unittest.TestCase):
    def test_first_run_sets_every_best(self) -> None:
        record, improvement = _store().submit(
            section="home", mode="whack", wpm=40, accuracy=95,
            reaction_ms=300, streak=12, keystrokes=30,
        )
        self.assertEqual(record.best_wpm, 40)
        self.assertEqual(record.best_reaction_ms, 300)
        self.assertTrue(improvement.any)

    def test_a_worse_run_leaves_the_bests_alone(self) -> None:
        store = _store()
        store.submit(
            section="home", mode="whack", wpm=40, accuracy=95,
            reaction_ms=300, streak=12, keystrokes=30,
        )
        record, improvement = store.submit(
            section="home", mode="whack", wpm=20, accuracy=80,
            reaction_ms=500, streak=3, keystrokes=30,
        )
        self.assertEqual(record.best_wpm, 40)
        self.assertEqual(record.best_accuracy, 95)
        self.assertEqual(record.best_reaction_ms, 300)
        self.assertFalse(improvement.any)
        self.assertEqual(record.runs, 2)

    def test_reaction_improves_by_getting_smaller(self) -> None:
        """Lower is better, which is the one that's easy to get backwards."""
        store = _store()
        store.submit(
            section="home", mode="whack", wpm=40, accuracy=95,
            reaction_ms=300, streak=12, keystrokes=30,
        )
        record, improvement = store.submit(
            section="home", mode="whack", wpm=10, accuracy=50,
            reaction_ms=200, streak=1, keystrokes=30,
        )
        self.assertEqual(record.best_reaction_ms, 200)
        self.assertTrue(improvement.reaction)
        self.assertFalse(improvement.wpm)

    def test_a_short_but_complete_drill_can_still_set_a_record(self) -> None:
        """A Bottom Row sweep is seven keys; it must not be locked out."""
        record, improvement = _store().submit(
            section="bottom", mode="sweep", wpm=30, accuracy=100,
            reaction_ms=280, streak=7, keystrokes=7,
        )
        self.assertEqual(record.best_wpm, 30)
        self.assertTrue(improvement.any)

    def test_a_two_key_run_cannot_set_a_record(self) -> None:
        record, improvement = _store().submit(
            section="home", mode="whack", wpm=900, accuracy=100,
            reaction_ms=5, streak=2, keystrokes=MIN_KEYSTROKES - 1,
        )
        self.assertEqual(record.best_wpm, 0)
        self.assertFalse(improvement.any)
        self.assertEqual(record.runs, 1)  # it still counts as a run

    def test_sections_and_modes_keep_separate_records(self) -> None:
        store = _store()
        store.submit(
            section="home", mode="whack", wpm=40, accuracy=95,
            reaction_ms=300, streak=9, keystrokes=30,
        )
        store.submit(
            section="home", mode="words", wpm=55, accuracy=99,
            reaction_ms=180, streak=40, keystrokes=60,
        )
        board = store.all_records()
        self.assertEqual(len(board), 2)
        self.assertEqual(board[0].mode, "words")  # sorted best first

    def test_records_survive_a_reload(self) -> None:
        store = _store()
        store.submit(
            section="symbols", mode="pairs", wpm=33, accuracy=91,
            reaction_ms=250, streak=8, keystrokes=40,
        )
        reloaded = RecordStore(store.path).load()
        self.assertEqual(reloaded.entries["symbols:pairs"].best_wpm, 33)

    def test_a_corrupt_file_does_not_stop_you_typing(self) -> None:
        store = _store()
        store.path.parent.mkdir(parents=True, exist_ok=True)
        store.path.write_text("{not json", encoding="utf-8")
        self.assertEqual(store.load().entries, {})

    def test_unknown_fields_in_the_file_are_ignored(self) -> None:
        """An older app reading a newer file shouldn't crash."""
        store = _store()
        store.path.parent.mkdir(parents=True, exist_ok=True)
        store.path.write_text(
            '{"entries": {"home:whack": {"section": "home", "mode": "whack",'
            ' "best_wpm": 12, "invented_later": 5}}}',
            encoding="utf-8",
        )
        self.assertEqual(store.load().entries["home:whack"].best_wpm, 12)


class GuideTests(unittest.TestCase):
    def test_every_finger_is_described(self) -> None:
        fingers = guide_payload()["fingers"]
        self.assertEqual(len(fingers), len(FINGER_NAMES))
        for finger in fingers:
            self.assertTrue(finger["note"].strip(), finger["finger"])
            self.assertTrue(finger["home"])

    def test_finger_key_lists_match_the_keyboard(self) -> None:
        """The guide is generated from the layout, so it can't drift from it."""
        listed = {
            key
            for finger in guide_payload()["fingers"]
            for key in finger["keys"]
            if key != " "
        }
        self.assertEqual(listed, {k.char for k in ALL_KEYS})

    def test_home_row_marks_the_two_bumped_keys(self) -> None:
        anchors = [k["char"] for k in guide_payload()["home_row"] if k["anchor"]]
        self.assertEqual(sorted(anchors), ["f", "j"])

    def test_tips_and_faq_are_populated(self) -> None:
        payload = guide_payload()
        self.assertGreaterEqual(len(payload["tips"]), 6)
        self.assertGreaterEqual(len(payload["faq"]), 6)
        for item in payload["faq"]:
            self.assertTrue(item["question"].endswith("?"), item["question"])
            self.assertTrue(item["answer"].strip())


if __name__ == "__main__":
    unittest.main()
