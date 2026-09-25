"""Without Dart installed, nothing Dart is offered.

Every exercise here is checked by running it, and a Dart exercise on a
machine without Dart can only ever fail - which reads as the learner's
mistake. So each collection passes its Dart content through
engine.if_dart, and this pretends Dart is missing to prove every one of
them does.
"""

from __future__ import annotations

import unittest
from unittest import mock

import code_coach.engine as engine


def _offered() -> dict:
    from code_coach.bughunt import hunt_families
    from code_coach.errors import crash_families
    from code_coach.kata import languages
    from code_coach.kata.predict import predict_families
    from code_coach.magnets import magnet_families
    from code_coach.puzzles import supports
    from code_coach.regex import engine_for
    from code_coach.trace import trace_families

    return {
        "forms": "dart" in languages(),
        "bug hunt": "Dart" in hunt_families(),
        "errors": "Dart" in crash_families(),
        "magnets": "Dart" in magnet_families(),
        "trace": "Dart" in trace_families(),
        "predict": "Dart" in predict_families(),
        "puzzles": supports("dart"),
        "regex": engine_for("dart") == "dart",
    }


class DartHiddenTests(unittest.TestCase):

    def test_nothing_dart_is_offered_without_dart(self) -> None:
        with mock.patch.object(engine, "dart_path", return_value=None):
            offered = _offered()
        self.assertEqual([mode for mode, yes in offered.items() if yes], [])

    @unittest.skipUnless(engine.dart_available(), "needs dart (it comes with Flutter)")
    def test_everything_dart_is_offered_with_dart(self) -> None:
        offered = _offered()
        self.assertEqual([mode for mode, yes in offered.items() if not yes], [])

    def test_the_session_deals_no_dart_without_dart(self) -> None:
        from code_coach.progress.store import StudentProgress
        from code_coach.session import queue

        progress = StudentProgress()
        progress.language = "dart"
        with mock.patch.object(engine, "dart_path", return_value=None):
            dealt = queue(progress, 60)
        self.assertFalse([d for d in dealt if "dart" in d["id"]])


if __name__ == "__main__":
    unittest.main()
