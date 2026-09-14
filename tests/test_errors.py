"""Reading error messages.

The load-bearing test is `test_the_engine_says_exactly_this`. Both
halves of the answer — the message and the line it blames — are facts
the engine produces, so the suite runs every crash and holds the
recorded values to what actually came back. A crash that stops
crashing, or starts failing on a different line because a runtime
changed its wording, fails here rather than quietly marking people
wrong about something that is no longer true.

The plain-words reading is the part a person writes, and the tests
around it are about the question being answerable: a right answer that
is the only sensible-looking option is not a question.
"""

from __future__ import annotations

import unittest

from code_coach.errors import crash, crash_families, crashes, engine_report


class ShapeTests(unittest.TestCase):
    def test_there_are_some_in_every_family(self) -> None:
        self.assertGreaterEqual(len(crashes()), 9)
        for family in crash_families():
            with self.subTest(family=family):
                self.assertGreaterEqual(len(crashes(family)), 3)

    def test_ids_are_unique(self) -> None:
        ids = [c.id for c in crashes()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_crash_is_findable_by_id(self) -> None:
        for c in crashes():
            with self.subTest(crash=c.id):
                self.assertIs(crash(c.id), c)

    def test_they_are_short_enough_to_hold_in_your_head(self) -> None:
        """The line question is only fair if you can see every line at
        once. A thirty-line program turns 'which line' into scrolling."""
        for c in crashes():
            with self.subTest(crash=c.id):
                self.assertLessEqual(len(c.numbered), 10)
                self.assertGreaterEqual(len(c.numbered), 2)

    def test_the_ranking_was_done(self) -> None:
        for family in crash_families():
            with self.subTest(family=family):
                levels = [c.level for c in crashes(family)]
                self.assertEqual(levels, sorted(levels))
                self.assertGreater(len(set(levels)), 1)
                for level in levels:
                    self.assertIn(level, range(1, 6))


class EngineTests(unittest.TestCase):
    def test_the_engine_says_exactly_this(self) -> None:
        """The one everything else rests on.

        Both the message and the line are the engine's own report. If
        either drifts, every person answering this question is being
        marked against something that is not true any more.
        """
        for c in crashes():
            with self.subTest(crash=c.id):
                message, line = engine_report(c.code, c.language)
                self.assertEqual(
                    message, c.message,
                    f"{c.id}: the engine says {message!r}")
                self.assertEqual(
                    line, c.line,
                    f"{c.id}: the engine blames line {line}")

    def test_every_one_actually_crashes(self) -> None:
        """A program that runs fine has no error to read, and would be
        marked by comparing two blanks."""
        from code_coach.engine import run_code

        for c in crashes():
            with self.subTest(crash=c.id):
                _out, _err, exit_code = run_code(c.code, language=c.language)
                self.assertNotEqual(exit_code, 0, f"{c.id} does not crash")

    def test_the_blamed_line_is_a_real_line(self) -> None:
        for c in crashes():
            with self.subTest(crash=c.id):
                self.assertGreaterEqual(c.line, 1)
                self.assertLessEqual(c.line, len(c.numbered))

    def test_the_message_is_one_line(self) -> None:
        """The stack frames under it are about the runtime, not about
        you, and putting them on screen is what makes people stop
        reading the part that matters."""
        for c in crashes():
            with self.subTest(crash=c.id):
                self.assertNotIn("\n", c.message)
                self.assertNotIn("    at ", c.message)


class ChoiceTests(unittest.TestCase):
    def test_there_is_something_to_choose_between(self) -> None:
        for c in crashes():
            with self.subTest(crash=c.id):
                self.assertGreaterEqual(len(c.choices), 3)

    def test_the_answer_is_among_them(self) -> None:
        for c in crashes():
            with self.subTest(crash=c.id):
                self.assertIn(c.meaning, c.choices)

    def test_the_decoys_are_not_the_answer(self) -> None:
        for c in crashes():
            with self.subTest(crash=c.id):
                self.assertNotIn(c.meaning, c.decoys)
                self.assertEqual(len(set(c.decoys)), len(c.decoys))

    def test_the_order_gives_nothing_away(self) -> None:
        for c in crashes():
            with self.subTest(crash=c.id):
                self.assertEqual(list(c.choices), sorted(c.choices))

    def test_the_answer_is_not_the_longest_one(self) -> None:
        """Which is the oldest tell in multiple choice, and a reader
        picks up on it long before noticing they have."""
        longest = [c for c in crashes()
                   if len(c.meaning) > max(len(d) for d in c.decoys)]
        self.assertLessEqual(
            len(longest), len(crashes()) // 2,
            "the right reading is the longest option too often: "
            + ", ".join(c.id for c in longest))

    def test_every_one_says_what_to_do(self) -> None:
        for c in crashes():
            with self.subTest(crash=c.id):
                self.assertGreater(len(c.fix), 120)
                self.assertTrue(c.name.strip())


class RouteTests(unittest.TestCase):
    """What the screen is served, and what it is not."""

    def _list(self):
        from code_coach.api import server

        return server.error_list()

    def _check(self, crash_id: str, line: int, meaning: str):
        from code_coach.api import server
        from code_coach.api.schemas import ErrorCheckRequest

        return server.error_check(
            ErrorCheckRequest(crash_id=crash_id, line=line, meaning=meaning))

    def test_the_list_is_grouped_and_complete(self) -> None:
        served = self._list()
        names = [f["name"] for f in served["families"]]
        self.assertEqual(names, list(crash_families()))
        count = sum(len(f["crashes"]) for f in served["families"])
        self.assertEqual(count, len(crashes()))

    def test_the_answer_does_not_ride_along(self) -> None:
        """The message and the program have to be served — they are the
        question. The line it blames and the right reading must not be,
        and neither must the fix, which names the answer in prose."""
        served = self._list()
        for family in served["families"]:
            for row in family["crashes"]:
                with self.subTest(crash=row["id"]):
                    self.assertNotIn("line", row)
                    self.assertNotIn("meaning", row)
                    self.assertNotIn("fix", row)
                    self.assertIn("message", row)

    def test_the_right_answer_passes(self) -> None:
        for c in crashes():
            with self.subTest(crash=c.id):
                got = self._check(c.id, c.line, c.meaning)
                self.assertTrue(got.passed)
                self.assertTrue(got.fix)

    def test_the_wrong_line_does_not(self) -> None:
        for c in crashes():
            with self.subTest(crash=c.id):
                other = 1 if c.line != 1 else 2
                got = self._check(c.id, other, c.meaning)
                self.assertFalse(got.passed)
                self.assertFalse(got.line_right)
                self.assertTrue(got.meaning_right)

    def test_the_wrong_reading_does_not(self) -> None:
        for c in crashes():
            with self.subTest(crash=c.id):
                got = self._check(c.id, c.line, c.decoys[0])
                self.assertFalse(got.passed)
                self.assertTrue(got.line_right)
                self.assertFalse(got.meaning_right)

    def test_each_half_is_marked_separately(self) -> None:
        """Being told only 'wrong' when one of two answers was right
        teaches nothing about which half you cannot do yet."""
        c = crashes()[0]
        got = self._check(c.id, c.line + 1 if c.line < len(c.numbered) else 1,
                          c.decoys[0])
        self.assertFalse(got.line_right)
        self.assertFalse(got.meaning_right)

    def test_an_unknown_crash_is_a_404(self) -> None:
        from fastapi import HTTPException

        with self.assertRaises(HTTPException) as caught:
            self._check("no-such-crash", 1, "anything")
        self.assertEqual(caught.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
