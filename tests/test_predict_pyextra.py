"""Predict the output, for the Python behaviours interviews circle back to.

The rules of tests/test_predict_jsnode_music_cooking.py, applied to
PY_EXTRA_PUZZLES on its own. The set is imported directly rather than
through `predict.PUZZLES`, so these hold whether or not it has been added
to the Predict screen yet; the route checks patch it in for their
duration, so they mean the same thing before and after it is registered.

The load-bearing test runs each snippet in the real Python interpreter and
holds the typed-out answer to what came back. Besides that, the set must
not repeat an idea the first Python set (predict.py) already has: same id,
same name, same code, or the same shape under another spelling.
"""

from __future__ import annotations

import contextlib
import functools
import re
import unittest
from unittest import mock

import code_coach.kata.predict as predict_module
from code_coach.engine import run_code
from code_coach.kata.predict import PUZZLES, language_of
from code_coach.kata.predict_pyextra import (
    ASYNCIO,
    DATA_MODEL,
    GENERATORS,
    ITERATION,
    NUMBERS,
    PREFIX,
    PY_EXTRA_PUZZLES,
    SCOPE,
    STDLIB,
    STRINGS,
    SYNTAX,
    TYPING,
)

FAMILIES = (GENERATORS, ITERATION, SCOPE, DATA_MODEL, TYPING, NUMBERS,
            STRINGS, STDLIB, ASYNCIO, SYNTAX)

#: The shapes the set is meant to cover, by a word each must mention.
TOPICS = (
    "yield", "send(", "nonlocal", "__slots__", "@property", ".setter",
    "default_factory", "frozen=True", "Decimal", "round(", ".split(",
    "lru_cache", "gather", "create_task", "TaskGroup", ":=", "match ",
    "finally", "__eq__", "copy.deepcopy", "sys.intern", "contextmanager",
    "bisect", "Counter", "defaultdict", "super()", "__getitem__", "enumerate",
    "sorted(", "for n in range", "except*", "-3 ** 2", "{x:,.2f}",
    "removesuffix", "[::-1]", "__context__",
)

#: What the first Python set (predict.py) already teaches, by its ids.
#: Not a copy of the list - the test below takes the live ids - but the
#: ideas this set deliberately steps around, so a reader of the file knows.
AVOIDED_IDEAS = (
    "predict-default-list", "predict-repeated-row", "predict-alias",
    "predict-late-binding", "predict-generator-once", "predict-dict-order",
    "predict-negative-division", "predict-rounding", "predict-finally-return",
    "predict-tuple-of-list", "predict-chained",
)


@functools.lru_cache(maxsize=None)
def _run(code: str) -> tuple[str, str, int]:
    return run_code(code, language="python", timeout=60)


def _out(stdout: str) -> str:
    return stdout.replace("\r\n", "\n").rstrip("\n")


def _squash(code: str) -> str:
    """A snippet with its names and numbers blurred, to catch the same
    idea under a different spelling."""
    code = re.sub(r"\b[A-Za-z_]\w*\b", "N", code)
    code = re.sub(r"\d+(\.\d+)?", "0", code)
    return re.sub(r"\s+", "", code)


def _earlier() -> tuple:
    """Every puzzle that is not one of ours, whether or not ours are
    registered yet."""
    return tuple(p for p in PUZZLES if p not in PY_EXTRA_PUZZLES)


@contextlib.contextmanager
def _registered():
    """PUZZLES as it will be once the set is registered."""
    have = {p.id for p in PUZZLES}
    puzzles = (*PUZZLES, *(p for p in PY_EXTRA_PUZZLES if p.id not in have))
    with mock.patch.object(predict_module, "PUZZLES", puzzles):
        yield


class PyExtraPuzzleTests(unittest.TestCase):
    def test_python_agrees_with_every_written_answer(self) -> None:
        for p in PY_EXTRA_PUZZLES:
            with self.subTest(puzzle=p.id):
                stdout, stderr, code = _run(p.code)
                self.assertEqual(code, 0, (stderr or stdout)[:300])
                self.assertEqual(
                    _out(stdout), p.expect,
                    f"{p.id}: python prints {stdout.rstrip()!r} "
                    f"and the file says {p.expect!r}")

    def test_nothing_is_said_on_stderr(self) -> None:
        """No warning is hiding in a snippet: an un-awaited coroutine, a
        deprecation, a leaked task."""
        for p in PY_EXTRA_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertEqual(_run(p.code)[1].strip(), "")

    def test_every_puzzle_explains_itself(self) -> None:
        for p in PY_EXTRA_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.expect.strip())
                self.assertTrue(p.name.strip())
                self.assertGreater(len(p.why), 80)
                self.assertIn(p.family, FAMILIES)
                self.assertEqual(p.language, "python")
                self.assertIn("print(", p.code)
                self.assertTrue(p.id.startswith(PREFIX))

    def test_every_snippet_is_short(self) -> None:
        for p in PY_EXTRA_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertLessEqual(len(p.code.splitlines()), 15)

    def test_nothing_depends_on_the_clock_the_dice_or_the_hash_seed(self) -> None:
        """An answer typed out once has to be what every run prints.

        Asyncio snippets use sleep to order tasks, and the order comes from
        the deadlines, so it holds however slow the machine; real time is
        never read.
        """
        for p in PY_EXTRA_PUZZLES:
            with self.subTest(puzzle=p.id):
                for word in ("import random", "import time", "datetime",
                             "perf_counter", "uuid", "os.urandom",
                             "PYTHONHASHSEED"):
                    self.assertNotIn(word, p.code)

    def test_no_snippet_iterates_a_set_of_strings(self) -> None:
        """Strings hash differently in every run, so the order a set of
        them comes out in is not an answer."""
        for p in PY_EXTRA_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertNotRegex(p.code, r"""set\(\s*["']""")
                self.assertNotRegex(p.code, r"""\{\s*["'][^:}]*["']\s*[,}]""")

    def test_nothing_needs_the_network_or_the_disk(self) -> None:
        for p in PY_EXTRA_PUZZLES:
            with self.subTest(puzzle=p.id):
                for word in ("open(", "socket", "urllib", "requests",
                             "subprocess", "os.system", "input("):
                    self.assertNotIn(word, p.code)

    def test_the_answer_is_not_sitting_in_the_snippet(self) -> None:
        for p in PY_EXTRA_PUZZLES:
            with self.subTest(puzzle=p.id):
                if len(p.expect) < 8:
                    continue
                self.assertNotIn(p.expect, p.code)

    def test_a_set_of_about_fifty(self) -> None:
        self.assertGreaterEqual(len(PY_EXTRA_PUZZLES), 40)
        self.assertLessEqual(len(PY_EXTRA_PUZZLES), 60)

    def test_every_family_is_a_real_set(self) -> None:
        for family in FAMILIES:
            with self.subTest(family=family):
                mine = [p for p in PY_EXTRA_PUZZLES if p.family == family]
                self.assertGreaterEqual(len(mine), 4)

    def test_the_shapes_are_all_here(self) -> None:
        everything = "\n".join(p.code for p in PY_EXTRA_PUZZLES)
        for word in TOPICS:
            with self.subTest(topic=word):
                self.assertIn(word, everything)


class PyExtraNovelty(unittest.TestCase):
    def test_every_puzzle_is_named_once_and_new(self) -> None:
        ids = [p.id for p in PY_EXTRA_PUZZLES]
        self.assertEqual(len(ids), len(set(ids)))
        names = [p.name for p in PY_EXTRA_PUZZLES]
        self.assertEqual(len(names), len(set(names)))
        old = _earlier()
        self.assertFalse(set(ids) & {p.id for p in old})
        self.assertFalse(set(names) & {p.name for p in old})

    def test_the_family_is_new_or_already_python(self) -> None:
        """A family never mixes languages, so a name another language's
        puzzles already use cannot be ours."""
        for p in _earlier():
            if p.family in FAMILIES:
                with self.subTest(puzzle=p.id):
                    self.assertEqual(p.language, "python")

    def test_no_snippet_repeats_an_earlier_one(self) -> None:
        old = {p.code for p in _earlier()}
        for p in PY_EXTRA_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertNotIn(p.code, old)

    def test_no_snippet_is_an_earlier_python_one_renamed(self) -> None:
        """The same shape with other names and numbers is the same idea."""
        old = {_squash(p.code): p.id
               for p in _earlier() if p.language == "python"}
        for p in PY_EXTRA_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertNotIn(_squash(p.code), old,
                                 f"{p.id} is {old.get(_squash(p.code))} "
                                 f"with other names")

    def test_the_ideas_the_first_set_has_are_still_there_to_avoid(self) -> None:
        """If one of the ideas named above is renamed or removed from
        predict.py, this set's promise to step around it needs a look."""
        ids = {p.id for p in _earlier()}
        for wanted in AVOIDED_IDEAS:
            with self.subTest(idea=wanted):
                self.assertIn(wanted, ids)

    def test_no_snippet_repeats_another_in_this_set(self) -> None:
        shapes = [_squash(p.code) for p in PY_EXTRA_PUZZLES]
        self.assertEqual(len(shapes), len(set(shapes)))

    def test_no_snippet_is_one_of_the_javascript_ideas_translated(self) -> None:
        """Python only: nothing here mentions a JavaScript runtime."""
        for p in PY_EXTRA_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertNotIn("console.log", p.code)


class PyExtraLevels(unittest.TestCase):
    def test_every_level_is_in_range(self) -> None:
        for p in PY_EXTRA_PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertIn(p.level, (1, 2, 3, 4))

    def test_all_four_levels_are_used(self) -> None:
        self.assertEqual({p.level for p in PY_EXTRA_PUZZLES}, {1, 2, 3, 4})

    def test_a_family_is_not_all_one_level(self) -> None:
        for family in FAMILIES:
            with self.subTest(family=family):
                levels = {p.level for p in PY_EXTRA_PUZZLES
                          if p.family == family}
                self.assertGreater(len(levels), 1)

    def test_each_family_is_written_least_surprising_first(self) -> None:
        for family in FAMILIES:
            with self.subTest(family=family):
                levels = [p.level for p in PY_EXTRA_PUZZLES
                          if p.family == family]
                self.assertEqual(levels, sorted(levels))

    def test_the_families_are_written_together(self) -> None:
        """A family's puzzles sit next to each other in the file, so the
        order the families come out in is the order they were written."""
        seen: list[str] = []
        for p in PY_EXTRA_PUZZLES:
            if not seen or seen[-1] != p.family:
                seen.append(p.family)
        self.assertEqual(len(seen), len(set(seen)))
        self.assertEqual(tuple(seen), FAMILIES)


class PyExtraRouteTests(unittest.TestCase):
    def test_registered_each_family_is_served_as_python(self) -> None:
        from code_coach.api import server

        with _registered():
            for family in FAMILIES:
                self.assertEqual(language_of(family), "python")
            served = server.predict_list()
        for family_name in FAMILIES:
            with self.subTest(family=family_name):
                family = next(
                    f for f in served["families"] if f["name"] == family_name)
                self.assertEqual(family["language"], "python")
                self.assertEqual(
                    sorted(row["id"] for row in family["puzzles"]),
                    sorted(p.id for p in PY_EXTRA_PUZZLES
                           if p.family == family_name))
                for row in family["puzzles"]:
                    self.assertNotIn("expect", row)
                    self.assertNotIn("why", row)

    def test_registered_they_are_checked_by_the_route(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import PredictCheckRequest

        with _registered():
            for family in FAMILIES:
                levels = [p.level for p in predict_module.puzzles(family)]
                self.assertEqual(levels, sorted(levels))
            for p in PY_EXTRA_PUZZLES:
                with self.subTest(puzzle=p.id):
                    right = server.predict_check(
                        PredictCheckRequest(puzzle_id=p.id, guess=p.expect))
                    self.assertTrue(right.passed)
                    self.assertTrue(right.why.strip())
                    wrong = server.predict_check(PredictCheckRequest(
                        puzzle_id=p.id, guess=p.expect + " and then some"))
                    self.assertFalse(wrong.passed)

    def test_registered_the_families_keep_to_the_rules_of_the_page(self) -> None:
        """What tests/test_predict.py asks of every family, asked of ours
        with the set registered."""
        with _registered():
            for family in FAMILIES:
                with self.subTest(family=family):
                    self.assertIn(family, predict_module.predict_families())
                    levels = {p.level for p in predict_module.puzzles(family)}
                    self.assertGreater(len(levels), 1)


if __name__ == "__main__":
    unittest.main()
