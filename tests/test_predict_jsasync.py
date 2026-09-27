"""Predict the output, for the JavaScript event loop.

The rules of tests/test_predict.py and tests/test_predict_jsgame.py,
applied to JS_ASYNC_PUZZLES on its own. It imports the set directly
rather than going through `predict.PUZZLES`, so these hold whether or
not it has been added to the Predict screen yet; the route checks
patch it in for their duration, so they mean the same thing before and
after it is registered.

The load-bearing test runs each snippet in Node and holds the typed-out
answer to what came back. Ordering puzzles have one extra way to be
wrong — a snippet that only prints its answer when the timers happen to
line up — so each is also run a second time, fresh, and must print the
same thing again.
"""

from __future__ import annotations

import contextlib
import functools
import unittest
from unittest import mock

import code_coach.kata.predict as predict_module
from code_coach.engine import run_code
from code_coach.kata.predict import PUZZLES, language_of
from code_coach.kata.predict_jsasync import JS_ASYNC_PUZZLES, LOOP

#: The shapes the set is meant to cover, by a word each must mention.
TOPICS = ("setTimeout", "setInterval", "clearInterval", "queueMicrotask",
          "new Promise", "async function", "await", ".then", ".catch",
          ".finally", "Promise.all", "Promise.race", "throw")

#: Every explanation names at least one of the places code waits.
PLACES = ("call stack", "microtask", "task", "queue")


@functools.lru_cache(maxsize=None)
def _run(code: str) -> tuple[str, str, int]:
    return run_code(code, language="javascript")


def _out(stdout: str) -> str:
    return stdout.replace("\r\n", "\n").rstrip("\n")


@contextlib.contextmanager
def _registered():
    """PUZZLES as it will be once the set is registered."""
    have = {p.id for p in PUZZLES}
    puzzles = (*PUZZLES, *(p for p in JS_ASYNC_PUZZLES if p.id not in have))
    with mock.patch.object(predict_module, "PUZZLES", puzzles):
        yield


class LoopPuzzleTests(unittest.TestCase):
    def test_node_agrees_with_every_written_answer(self) -> None:
        for p in JS_ASYNC_PUZZLES:
            with self.subTest(puzzle=p.id):
                stdout, stderr, code = _run(p.code)
                self.assertEqual(code, 0, (stderr or stdout)[:300])
                self.assertEqual(
                    _out(stdout), p.expect,
                    f"{p.id}: node prints {stdout.rstrip()!r} "
                    f"and the file says {p.expect!r}")

    def test_a_second_run_prints_the_same(self) -> None:
        """Not cached: a fresh Node, to catch an answer that depends on
        how quickly the machine happened to get round to a timer."""
        for p in JS_ASYNC_PUZZLES:
            with self.subTest(puzzle=p.id):
                stdout, _, code = run_code(p.code, language="javascript")
                self.assertEqual(code, 0)
                self.assertEqual(_out(stdout), p.expect)

    def test_nothing_is_said_on_stderr(self) -> None:
        for p in JS_ASYNC_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertEqual(_run(p.code)[1].strip(), "")

    def test_every_puzzle_explains_itself(self) -> None:
        for p in JS_ASYNC_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.expect.strip())
                self.assertTrue(p.name.strip())
                self.assertTrue(p.why.strip())
                self.assertEqual(p.family, LOOP)
                self.assertEqual(p.language, "javascript")
                self.assertIn("console.log", p.code)
                self.assertTrue(p.id.startswith("predict-jsa-"))

    def test_every_why_says_where_the_code_was_waiting(self) -> None:
        for p in JS_ASYNC_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertTrue(any(w in p.why for w in PLACES), p.why)

    def test_every_snippet_is_short(self) -> None:
        for p in JS_ASYNC_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertLessEqual(len(p.code.splitlines()), 12)

    def test_nothing_needs_a_browser(self) -> None:
        for p in JS_ASYNC_PUZZLES:
            with self.subTest(puzzle=p.id):
                for word in ("document", "window", "requestAnimationFrame",
                             "fetch("):
                    self.assertNotIn(word, p.code)

    def test_the_answer_is_not_sitting_in_the_snippet(self) -> None:
        for p in JS_ASYNC_PUZZLES:
            with self.subTest(puzzle=p.id):
                if len(p.expect) < 8:
                    continue
                self.assertNotIn(p.expect, p.code)

    def test_there_are_twelve_to_twenty(self) -> None:
        self.assertGreaterEqual(len(JS_ASYNC_PUZZLES), 12)
        self.assertLessEqual(len(JS_ASYNC_PUZZLES), 20)

    def test_the_event_loop_shapes_are_all_here(self) -> None:
        everything = "\n".join(p.code for p in JS_ASYNC_PUZZLES)
        for word in TOPICS:
            with self.subTest(topic=word):
                self.assertIn(word, everything)

    def test_every_puzzle_is_named_once_and_new(self) -> None:
        ids = [p.id for p in JS_ASYNC_PUZZLES]
        self.assertEqual(len(ids), len(set(ids)))
        others = {p.id for p in PUZZLES if p not in JS_ASYNC_PUZZLES}
        self.assertFalse(set(ids) & others)

    def test_the_family_is_new_or_already_javascript(self) -> None:
        """A family never mixes languages, so the name must not belong
        to another language's puzzles."""
        others = [p for p in PUZZLES
                  if p.family == LOOP and p not in JS_ASYNC_PUZZLES]
        for p in others:
            self.assertEqual(p.language, "javascript")

    def test_no_snippet_repeats_an_earlier_set(self) -> None:
        """The older "Async" family covers the first few of these ideas;
        none of its snippets may come back here word for word."""
        old = {p.code for p in PUZZLES if p not in JS_ASYNC_PUZZLES}
        for p in JS_ASYNC_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertNotIn(p.code, old)


class LoopLevelTests(unittest.TestCase):
    def test_the_file_is_written_least_surprising_first(self) -> None:
        levels = [p.level for p in JS_ASYNC_PUZZLES]
        self.assertEqual(levels, sorted(levels))
        self.assertEqual(set(levels), {1, 2, 3, 4})


class LoopRouteTests(unittest.TestCase):
    def test_registered_the_family_is_served_as_javascript(self) -> None:
        from code_coach.api import server

        with _registered():
            self.assertEqual(language_of(LOOP), "javascript")
            served = server.predict_list()
        family = next(f for f in served["families"] if f["name"] == LOOP)
        self.assertEqual(family["language"], "javascript")
        self.assertEqual(
            sorted(row["id"] for row in family["puzzles"]),
            sorted(p.id for p in JS_ASYNC_PUZZLES))
        for row in family["puzzles"]:
            self.assertNotIn("expect", row)
            self.assertNotIn("why", row)

    def test_registered_they_are_checked_by_the_route(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import PredictCheckRequest

        with _registered():
            levels = [p.level for p in predict_module.puzzles(LOOP)]
            self.assertEqual(levels, sorted(levels))
            for p in JS_ASYNC_PUZZLES:
                with self.subTest(puzzle=p.id):
                    right = server.predict_check(
                        PredictCheckRequest(puzzle_id=p.id, guess=p.expect))
                    self.assertTrue(right.passed)
                    self.assertTrue(right.why.strip())
                    wrong = server.predict_check(PredictCheckRequest(
                        puzzle_id=p.id, guess=p.expect + " and then some"))
                    self.assertFalse(wrong.passed)


if __name__ == "__main__":
    unittest.main()
