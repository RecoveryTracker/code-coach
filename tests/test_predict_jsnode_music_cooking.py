"""Predict the output, for JavaScript about Node, music and cooking.

The rules of tests/test_predict_jsgame.py, applied to JS_NODE_PUZZLES,
JS_MUSIC_PUZZLES and JS_COOKING_PUZZLES on their own. The sets are imported directly
rather than through `predict.PUZZLES`, so these hold whether or not
they have been added to the Predict screen yet; the route checks patch
both in for their duration, so they mean the same thing before and
after they are registered.

The load-bearing test runs each snippet in Node and holds the typed-out
answer to what came back.
"""

from __future__ import annotations

import contextlib
import functools
import unittest
from unittest import mock

import code_coach.kata.predict as predict_module
from code_coach.engine import run_code
from code_coach.kata.predict import PUZZLES, language_of
from code_coach.kata.predict_jscooking import COOKING, JS_COOKING_PUZZLES
from code_coach.kata.predict_jsmusic import JS_MUSIC_PUZZLES, MUSIC
from code_coach.kata.predict_jsnode import JS_NODE_PUZZLES, NODE

_MINE = JS_NODE_PUZZLES + JS_MUSIC_PUZZLES + JS_COOKING_PUZZLES


@functools.lru_cache(maxsize=None)
def _run(code: str) -> tuple[str, str, int]:
    return run_code(code, language="javascript")


def _out(stdout: str) -> str:
    return stdout.replace("\r\n", "\n").rstrip("\n")


@contextlib.contextmanager
def _registered():
    """PUZZLES as it will be once both sets are registered."""
    have = {p.id for p in PUZZLES}
    puzzles = (*PUZZLES, *(p for p in _MINE if p.id not in have))
    with mock.patch.object(predict_module, "PUZZLES", puzzles):
        yield


class _SetRules:
    """What one themed set has to be."""

    SET: tuple = ()
    FAMILY = ""
    PREFIX = ""
    #: The shapes the set is meant to cover, by a word each must mention.
    TOPICS: tuple[str, ...] = ()

    def test_node_agrees_with_every_written_answer(self) -> None:
        for p in self.SET:
            with self.subTest(puzzle=p.id):
                stdout, stderr, code = _run(p.code)
                self.assertEqual(code, 0, (stderr or stdout)[:300])
                self.assertEqual(
                    _out(stdout), p.expect,
                    f"{p.id}: node prints {stdout.rstrip()!r} "
                    f"and the file says {p.expect!r}")

    def test_nothing_is_said_on_stderr(self) -> None:
        for p in self.SET:
            with self.subTest(puzzle=p.id):
                self.assertEqual(_run(p.code)[1].strip(), "")

    def test_every_puzzle_explains_itself(self) -> None:
        for p in self.SET:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.expect.strip())
                self.assertTrue(p.name.strip())
                self.assertTrue(p.why.strip())
                self.assertEqual(p.family, self.FAMILY)
                self.assertEqual(p.language, "javascript")
                self.assertIn("console.log", p.code)
                self.assertTrue(p.id.startswith(self.PREFIX))

    def test_every_snippet_is_short(self) -> None:
        for p in self.SET:
            with self.subTest(puzzle=p.id):
                self.assertLessEqual(len(p.code.splitlines()), 12)

    def test_nothing_needs_a_browser_or_the_network(self) -> None:
        """Plain Node: no page, no canvas, no animation frames, no fetch."""
        for p in self.SET:
            with self.subTest(puzzle=p.id):
                for word in ("document", "window", "requestAnimationFrame",
                             "canvas", "fetch("):
                    self.assertNotIn(word, p.code)

    def test_nothing_depends_on_the_clock_or_the_dice(self) -> None:
        """An answer typed out once has to be what every run prints."""
        for p in self.SET:
            with self.subTest(puzzle=p.id):
                for word in ("Math.random", "Date", "performance.now",
                             "setTimeout", "setInterval"):
                    self.assertNotIn(word, p.code)

    def test_the_answer_is_not_sitting_in_the_snippet(self) -> None:
        for p in self.SET:
            with self.subTest(puzzle=p.id):
                if len(p.expect) < 8:
                    continue
                self.assertNotIn(p.expect, p.code)

    def test_a_set_of_about_ten(self) -> None:
        self.assertGreaterEqual(len(self.SET), 8)
        self.assertLessEqual(len(self.SET), 20)

    def test_the_shapes_are_all_here(self) -> None:
        everything = "\n".join(p.code for p in self.SET)
        for word in self.TOPICS:
            with self.subTest(topic=word):
                self.assertIn(word, everything)

    def test_every_puzzle_is_named_once_and_new(self) -> None:
        ids = [p.id for p in self.SET]
        self.assertEqual(len(ids), len(set(ids)))
        others = {p.id for p in (*PUZZLES, *_MINE) if p not in self.SET}
        self.assertFalse(set(ids) & others)
        names = [p.name for p in self.SET]
        self.assertEqual(len(names), len(set(names)))

    def test_the_family_is_new_or_already_javascript(self) -> None:
        """A family never mixes languages, so the name must not belong
        to another language's puzzles."""
        others = [p for p in PUZZLES
                  if p.family == self.FAMILY and p not in self.SET]
        for p in others:
            self.assertEqual(p.language, "javascript")

    def test_no_snippet_repeats_an_earlier_set(self) -> None:
        old = {p.code for p in (*PUZZLES, *_MINE) if p not in self.SET}
        for p in self.SET:
            with self.subTest(puzzle=p.id):
                self.assertNotIn(p.code, old)

    def test_the_file_is_written_least_surprising_first(self) -> None:
        """Gentle sets: levels 1 to 3, all three used, in file order."""
        levels = [p.level for p in self.SET]
        self.assertEqual(levels, sorted(levels))
        self.assertEqual(set(levels), {1, 2, 3})


class NodePuzzleTests(_SetRules, unittest.TestCase):
    SET = JS_NODE_PUZZLES
    FAMILY = NODE
    PREFIX = "predict-jsnd-"
    TOPICS = ("process.argv", "JSON.parse", "path.join", "path.resolve",
              "readFileSync", "EventEmitter", "prependListener", "nextTick",
              "process.env", "JSON.stringify", "forEach", "exports")


class MusicPuzzleTests(_SetRules, unittest.TestCase):
    SET = JS_MUSIC_PUZZLES
    FAMILY = MUSIC
    PREFIX = "predict-jsms-"
    TOPICS = ("% 12", "0.1 + 0.2", "Math.round", "**", "sort()", "parseInt",
              "Math.log10", "fill(", "reduce", "toFixed")


class CookingPuzzleTests(_SetRules, unittest.TestCase):
    SET = JS_COOKING_PUZZLES
    FAMILY = COOKING
    PREFIX = "predict-jsck-"
    TOPICS = ("toFixed", "Math.round", "Math.ceil", "sort()", "reduce",
              "new Map", "padStart", "Intl.NumberFormat", "localeCompare",
              "structuredClone")


class RouteTests(unittest.TestCase):
    def test_registered_each_family_is_served_as_javascript(self) -> None:
        from code_coach.api import server

        with _registered():
            for family in (NODE, MUSIC, COOKING):
                self.assertEqual(language_of(family), "javascript")
            served = server.predict_list()
        for name, puzzle_set in ((NODE, JS_NODE_PUZZLES),
                                 (MUSIC, JS_MUSIC_PUZZLES),
                                 (COOKING, JS_COOKING_PUZZLES)):
            with self.subTest(family=name):
                family = next(f for f in served["families"] if f["name"] == name)
                self.assertEqual(family["language"], "javascript")
                self.assertEqual(
                    sorted(row["id"] for row in family["puzzles"]),
                    sorted(p.id for p in puzzle_set))
                for row in family["puzzles"]:
                    self.assertNotIn("expect", row)
                    self.assertNotIn("why", row)

    def test_registered_they_are_checked_by_the_route(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import PredictCheckRequest

        with _registered():
            for family in (NODE, MUSIC, COOKING):
                levels = [p.level for p in predict_module.puzzles(family)]
                self.assertEqual(levels, sorted(levels))
            for p in _MINE:
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
