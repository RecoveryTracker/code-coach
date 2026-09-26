"""Session history: what has been done, what has not, and what is due.

Every expectation here is worked out by hand from a progress record with
known dates and a fixed "now" - not read back from the function.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from code_coach.progress.store import DrillRecord, StudentProgress
from code_coach.session import REFRESH_CHOICES, history

NOW = datetime(2026, 9, 26, 12, 0, tzinfo=timezone.utc)


def _stamp(days_ago: float) -> str:
    return (NOW - timedelta(days=days_ago)).isoformat()


def _progress() -> StudentProgress:
    from code_coach.kata import katas

    first, second, third = [k.id for k in katas()[:3]]
    progress = StudentProgress()
    progress.language = "python"
    progress.kata_done = {
        first: DrillRecord(count=3, last_at=_stamp(10)),   # due at a 7-day gap
        second: DrillRecord(count=1, last_at=_stamp(2)),   # fresh
        third: DrillRecord(count=2, last_at=_stamp(30)),   # due, and oldest
    }
    return progress


class HistoryTests(unittest.TestCase):

    def setUp(self) -> None:
        self.progress = _progress()
        self.forms = lambda h: next(p for p in h["practices"] if p["key"] == "forms")

    def test_tried_counts_what_has_been_done_at_least_once(self) -> None:
        self.assertEqual(self.forms(history(self.progress, 7, NOW))["tried"], 3)

    def test_due_is_done_before_and_older_than_the_gap_oldest_first(self) -> None:
        from code_coach.kata import katas

        first, _, third = [k.id for k in katas()[:3]]
        due = self.forms(history(self.progress, 7, NOW))["due"]
        self.assertEqual([d["id"] for d in due], [third, first])
        self.assertEqual([d["days_ago"] for d in due], [30.0, 10.0])

    def test_a_longer_gap_leaves_less_due(self) -> None:
        from code_coach.kata import katas

        third = katas()[2].id
        self.assertEqual([d["id"] for d in self.forms(history(self.progress, 14, NOW))["due"]],
                         [third])
        self.assertEqual(self.forms(history(self.progress, 30, NOW))["due"], [])

    def test_never_done_is_never_due(self) -> None:
        empty = StudentProgress()
        h = history(empty, 3, NOW)
        self.assertTrue(all(p["tried"] == 0 and p["due"] == [] for p in h["practices"]))
        self.assertEqual(h["recent"], [])

    def test_recent_is_newest_first(self) -> None:
        recent = history(self.progress, 7, NOW)["recent"]
        self.assertEqual([r["days_ago"] for r in recent], [2.0, 10.0, 30.0])

    def test_totals_match_what_the_queue_could_deal(self) -> None:
        from code_coach.session import SOURCES, dealable

        h = history(self.progress, 7, NOW)
        for source, row in zip(SOURCES, h["practices"]):
            with self.subTest(practice=source.key):
                self.assertEqual(row["total"], len(dealable(source, self.progress)))


class RouteTests(unittest.TestCase):

    def test_the_gap_is_one_of_the_choices(self) -> None:
        from code_coach.api.server import session_history

        self.assertEqual(session_history(14)["refresh_days"], 14)
        # Anything else falls back to a week rather than meaning nonsense.
        self.assertEqual(session_history(-5)["refresh_days"], 7)
        self.assertEqual(session_history(14)["choices"], list(REFRESH_CHOICES))


if __name__ == "__main__":
    unittest.main()
