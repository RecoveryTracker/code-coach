"""Regex: every task honest in both engines, and the runner safe.

The load-bearing tests are the first two. Each task's answer has to
pass in Python's re and JavaScript's RegExp, run as real processes -
so a task is about regular expressions, not about one engine. And each
task's pitfalls have to fail in both: a pitfall is the classic wrong
answer for the idea the task is named after, and if it passes, the task
does not test that idea. One was caught this way while writing them -
"p[aiu]n" was listed as a pitfall and is a perfectly good answer.
"""

from __future__ import annotations

import unittest

from code_coach.regex import (
    MAX_PATTERN,
    check,
    engine_for,
    families,
    run_pattern,
    task,
    tasks,
)

ENGINES = ("python", "javascript")


class EveryTaskIsHonestTests(unittest.TestCase):

    def test_the_answer_passes_in_both_engines(self) -> None:
        for t in tasks():
            for engine in ENGINES:
                with self.subTest(task=t.id, engine=engine):
                    verdict = check(t, t.answer, engine)
                    self.assertEqual(verdict.broke, "", t.id)
                    wrong = [r[0] for r in verdict.rows if not r[5]]
                    self.assertTrue(verdict.passed, f"{t.id} misses {wrong}")

    def test_every_pitfall_fails_in_both_engines(self) -> None:
        for t in tasks():
            self.assertTrue(t.pitfalls, f"{t.id} has no pitfall")
            for pitfall in t.pitfalls:
                for engine in ENGINES:
                    with self.subTest(task=t.id, pitfall=pitfall, engine=engine):
                        self.assertFalse(
                            check(t, pitfall, engine).passed,
                            f"{t.id}: the pitfall {pitfall!r} passes, so the "
                            f"task does not test what it is named after")

    def test_there_is_something_to_match_and_something_to_skip(self) -> None:
        """With nothing to skip, .* passes; with nothing to match, a
        pattern that finds nothing does."""
        for t in tasks():
            with self.subTest(task=t.id):
                self.assertTrue(t.match)
                self.assertTrue(t.skip)
                self.assertFalse(set(t.match) & set(t.skip))
                for engine in ENGINES:
                    self.assertFalse(check(t, ".*", engine).passed)

    def test_captures_are_about_strings_that_must_match(self) -> None:
        for t in tasks():
            for text, _ in t.capture:
                with self.subTest(task=t.id, text=text):
                    self.assertIn(text, t.match)

    def test_every_task_says_what_it_needs_to(self) -> None:
        for t in tasks():
            with self.subTest(task=t.id):
                for text in (t.title, t.brief, t.hint, t.lesson, t.answer):
                    self.assertTrue(text.strip())
                self.assertLessEqual(len(t.answer), MAX_PATTERN)


class CollectionTests(unittest.TestCase):

    def test_ids_are_unique_and_findable(self) -> None:
        ids = [t.id for t in tasks()]
        self.assertEqual(len(ids), len(set(ids)))
        for t in tasks():
            self.assertIs(task(t.id), t)

    def test_it_reads_easiest_first(self) -> None:
        levels = [t.level for t in tasks()]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(families()), 2)


class CheckingTests(unittest.TestCase):

    def test_a_capture_task_answered_without_a_group_says_so(self) -> None:
        t = task("rx-capture-year")
        verdict = check(t, r"\d{4}-\d\d-\d\d", "python")
        self.assertFalse(verdict.passed)
        self.assertIn("parentheses", verdict.broke)

    def test_a_wrong_capture_is_marked_wrong(self) -> None:
        """Right strings found, wrong piece captured - still wrong."""
        t = task("rx-capture-year")
        verdict = check(t, r"\d{4}-(\d\d)-\d\d", "python")
        self.assertEqual(verdict.broke, "")
        self.assertFalse(verdict.passed)

    def test_a_pattern_that_does_not_compile_says_so(self) -> None:
        for engine in ENGINES:
            with self.subTest(engine=engine):
                verdict = check(task("rx-literal"), "(unclosed", engine)
                self.assertFalse(verdict.passed)
                self.assertTrue(verdict.broke)

    def test_an_empty_or_huge_pattern_is_refused_without_running(self) -> None:
        self.assertTrue(check(task("rx-literal"), "", "python").broke)
        self.assertTrue(check(task("rx-literal"), "a" * (MAX_PATTERN + 1), "python").broke)

    def test_each_language_gets_the_right_engine(self) -> None:
        self.assertEqual(engine_for("javascript"), "javascript")
        self.assertEqual(engine_for("typescript"), "javascript")
        self.assertEqual(engine_for("python"), "python")
        self.assertEqual(engine_for("rust"), "python")


class SafetyTests(unittest.TestCase):

    def test_a_runaway_pattern_ends_in_a_message_not_a_hang(self) -> None:
        """(a+)+$ against a's ending in b takes exponential time in a
        backtracking engine. In the server it would freeze the app; in a
        child process it has to come back as a message."""
        got = run_pattern(r"(a+)+$", ["a" * 34 + "b"], "python")
        self.assertIn("error", got)
        self.assertIn("too long", got["error"])

    def test_the_pattern_is_data_not_code(self) -> None:
        """A pattern is handed to the engine as a string, never pasted
        into the program - so quotes and braces in it cannot break out."""
        for engine in ENGINES:
            with self.subTest(engine=engine):
                got = run_pattern("\"');}{print(1)//", ["x"], engine)
                self.assertTrue("results" in got or "error" in got)
                if "results" in got:
                    self.assertFalse(got["results"][0]["found"])


class RouteTests(unittest.TestCase):
    """The screen's view: no answers in the list, counted only on a pass."""

    def test_the_list_carries_no_answers(self) -> None:
        from code_coach.api.server import regex_list

        for family in regex_list()["families"]:
            for entry in family["tasks"]:
                found = task(entry["id"])
                with self.subTest(task=found.id):
                    self.assertNotIn("answer", entry)
                    self.assertNotIn(found.answer, [str(v) for v in entry.values()])

    def test_a_pass_is_counted_and_a_miss_is_not(self) -> None:
        from code_coach.api.schemas import RegexCheckRequest
        from code_coach.api.server import _store, regex_check

        found = tasks()[0]
        miss = regex_check(RegexCheckRequest(
            task_id=found.id, pattern=found.pitfalls[0], language="python"))
        self.assertFalse(miss.passed)
        self.assertEqual(miss.lesson, "")
        self.assertEqual(_store.load().regex_counts().get(found.id, 0), 0)
        hit = regex_check(RegexCheckRequest(
            task_id=found.id, pattern=found.answer, language="javascript"))
        self.assertTrue(hit.passed, hit.broke)
        self.assertEqual(hit.engine, "javascript")
        self.assertEqual(hit.lesson, found.lesson)
        self.assertEqual(_store.load().regex_counts()[found.id], 1)


if __name__ == "__main__":
    unittest.main()
