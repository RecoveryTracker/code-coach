"""Predict the output: the snippets, and what they really print.

The load-bearing test is `test_python_agrees_with_every_written_answer`,
and it runs the opposite way round from the katas.

A kata's answer is computed by a reference and checked by a person,
because the reference could be wrong. Here the answer is whatever Python
does — there is nothing for it to be wrong about — so the risk moves: a
snippet that has been edited, or written from memory, can quietly stop
demonstrating what its explanation says it demonstrates. The hand-written
`expect` is what catches that, and running the snippet is what checks the
hand-written one.

It has already paid for itself. A puzzle about small-integer caching was
written as `a = 256; b = 256; c = 257; d = 257` printing `True False`.
Python prints `True True`, because two constants in one code object are
folded into a single value. The snippet demonstrated nothing except that
it had not been run, and it is not in the file.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code
from code_coach.kata.predict import PUZZLES, predict_families, puzzles


class PuzzleTests(unittest.TestCase):
    def test_the_language_agrees_with_every_written_answer(self) -> None:
        """Each snippet in its own language, which is now two of them."""
        from code_coach.engine import c_available, dart_available

        for p in PUZZLES:
            if p.language == "dart" and not dart_available():
                continue  # Dart comes with Flutter; skipped, not failed
            if p.language == "c" and not c_available():
                continue
            with self.subTest(puzzle=p.id, language=p.language):
                stdout, stderr, code = run_code(p.code, language=p.language)
                self.assertEqual(code, 0, (stderr or stdout)[:300])
                self.assertEqual(
                    stdout.rstrip("\n"), p.expect,
                    f"{p.id}: {p.language} prints {stdout.rstrip()!r} "
                    f"and the file says {p.expect!r}")

    def test_every_snippet_prints_something(self) -> None:
        """A puzzle whose answer is the empty string asks nothing."""
        for p in PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.expect.strip())

    def test_every_puzzle_explains_itself(self) -> None:
        for p in PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertTrue(p.name.strip())
                self.assertTrue(p.why.strip())
                self.assertIn(p.family, predict_families())
                self.assertIn(
                    {"python": "print", "javascript": "console.log",
                     "dart": "print(", "c": "printf("}[p.language],
                    p.code)

    def test_the_answer_is_not_sitting_in_the_snippet(self) -> None:
        """A snippet that contains its own answer as a literal is one you
        can read rather than work out.

        Not a general rule — plenty of correct snippets mention their
        values — so this only objects when the whole answer appears
        verbatim, which is the case that gives it away.
        """
        for p in PUZZLES:
            with self.subTest(puzzle=p.id):
                if len(p.expect) < 8:
                    continue
                self.assertNotIn(p.expect, p.code)

    def test_every_puzzle_is_named_once(self) -> None:
        ids = [p.id for p in PUZZLES]
        self.assertEqual(sorted(ids), sorted(set(ids)))

    def test_the_families_hold_every_puzzle_between_them(self) -> None:
        counted = sum(len(puzzles(f)) for f in predict_families())
        self.assertEqual(counted, len(PUZZLES))


class RouteTests(unittest.TestCase):
    def test_the_list_does_not_carry_the_answers(self) -> None:
        """The answer is the exercise. Shipping it with the list is
        shipping the thing being asked for."""
        from code_coach.api import server

        payload = server.predict_list()
        self.assertTrue(payload["families"])
        for family in payload["families"]:
            for entry in family["puzzles"]:
                with self.subTest(puzzle=entry["id"]):
                    self.assertNotIn("expect", entry)
                    self.assertNotIn("why", entry)
                    self.assertTrue(entry["code"])

    def test_a_right_guess_passes_and_a_wrong_one_does_not(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import PredictCheckRequest

        for p in PUZZLES:
            with self.subTest(puzzle=p.id):
                right = server.predict_check(
                    PredictCheckRequest(puzzle_id=p.id, guess=p.expect))
                self.assertTrue(right.passed)
                wrong = server.predict_check(
                    PredictCheckRequest(
                        puzzle_id=p.id, guess=p.expect + " and then some"))
                self.assertFalse(wrong.passed)

    def test_trailing_whitespace_is_forgiven(self) -> None:
        """Trailing spaces and a stray blank line are invisible, and
        failing someone for one teaches them to distrust the marker
        rather than to read the code."""
        from code_coach.api import server
        from code_coach.api.schemas import PredictCheckRequest

        p = PUZZLES[0]
        sloppy = "\n".join(f"{line}   " for line in p.expect.split("\n"))
        response = server.predict_check(
            PredictCheckRequest(puzzle_id=p.id, guess=sloppy + "\n\n"))
        self.assertTrue(response.passed)

    def test_leading_whitespace_is_not_forgiven(self) -> None:
        """Because it is not invisible.

        A space at the start of a line is part of what the program
        printed. Forgiving it would mark a different output correct, and
        on a screen about what code really does that is the wrong place
        to be generous. The first line is exempt only because stripping
        the whole answer is what removes a stray newline before it.
        """
        from code_coach.api import server
        from code_coach.api.schemas import PredictCheckRequest

        many = [p for p in PUZZLES if "\n" in p.expect]
        self.assertTrue(many, "no puzzle prints more than one line")
        p = many[0]
        first, rest = p.expect.split("\n", 1)
        response = server.predict_check(
            PredictCheckRequest(puzzle_id=p.id, guess=f"{first}\n  {rest}"))
        self.assertFalse(response.passed)

    def test_the_explanation_comes_back_either_way(self) -> None:
        """Being told only that you were wrong teaches you that you were
        wrong."""
        from code_coach.api import server
        from code_coach.api.schemas import PredictCheckRequest

        for guess in (PUZZLES[0].expect, "nonsense"):
            response = server.predict_check(
                PredictCheckRequest(puzzle_id=PUZZLES[0].id, guess=guess))
            self.assertTrue(response.why.strip())

    def test_an_unknown_puzzle_is_refused(self) -> None:
        from fastapi import HTTPException

        from code_coach.api import server
        from code_coach.api.schemas import PredictCheckRequest

        with self.assertRaises(HTTPException) as caught:
            server.predict_check(
                PredictCheckRequest(puzzle_id="nonsense", guess="x"))
        self.assertEqual(caught.exception.status_code, 404)


class LevelTests(unittest.TestCase):
    """The order a family of puzzles is read in.

    Same arrangement as the katas. There is no measure of surprise to
    compute, so what is checked is that the ranking was done: a family
    all on one level has a field saying nothing, and its order is then
    whichever order the puzzles were written in.
    """

    def test_every_level_is_in_range(self) -> None:
        for p in PUZZLES:
            with self.subTest(puzzle=p.id):
                self.assertIn(p.level, (1, 2, 3, 4, 5))

    def test_a_family_is_not_all_one_level(self) -> None:
        for family in predict_families():
            with self.subTest(family=family):
                levels = {p.level for p in puzzles(family)}
                self.assertGreater(
                    len(levels), 1,
                    f"{family} is all level {levels.pop()}, so nothing in "
                    f"it has been ranked against anything else")

    def test_each_family_reads_least_surprising_first(self) -> None:
        for family in predict_families():
            with self.subTest(family=family):
                levels = [p.level for p in puzzles(family)]
                self.assertEqual(levels, sorted(levels))

    def test_the_families_keep_their_own_order(self) -> None:
        """Sorting by level interleaves them, so the family list has to
        come from the file rather than from the sorted puzzles.

        This used to name the first and last families, which tested the
        content rather than the rule: adding a family to the end broke
        it while nothing about the ordering had changed. What it means
        to say is that the families come out in the order they are
        first written, and that is what it says now — which still fails
        if the list is ever built from the level-sorted puzzles, since
        those interleave.
        """
        in_file: list[str] = []
        for p in PUZZLES:
            if p.family not in in_file:
                in_file.append(p.family)
        self.assertEqual(list(predict_families()), in_file)
