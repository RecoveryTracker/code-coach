"""Two-part puzzles: each part honest in both languages, and part two
really a new question.

The rule that is particular to this mode is the twist. Part one's answer,
with its function renamed to part two's, has to fail part two - checked
by running it. And "fail" has to mean the code ran and got answers
wrong, not that it never ran: while these were being written, a loaded
machine timed every Python run out, and a timeout also "does not pass".
So the twist test insists the run completed before it counts the fail.
"""

from __future__ import annotations

import unittest

from code_coach.puzzles import (
    NAMES,
    answer_for,
    function_name,
    puzzle,
    puzzles,
    run_part,
    supports,
)

LANGUAGES = ("python", "javascript")


class CollectionTests(unittest.TestCase):

    def test_ids_are_unique_and_findable(self) -> None:
        ids = [p.id for p in puzzles()]
        self.assertEqual(len(ids), len(set(ids)))
        for p in puzzles():
            self.assertIs(puzzle(p.id), p)

    def test_they_read_easiest_first(self) -> None:
        levels = [p.level for p in puzzles()]
        self.assertEqual(levels, sorted(levels))
        self.assertGreater(len(set(levels)), 1)

    def test_every_puzzle_says_what_it_needs_to(self) -> None:
        for p in puzzles():
            with self.subTest(puzzle=p.id):
                for text in (p.title, p.story, p.lesson):
                    self.assertTrue(text.strip())
                for n in (1, 2):
                    part = p.part(n)
                    self.assertTrue(part.brief.strip() and part.example.strip())

    def test_only_the_languages_with_answers_are_offered(self) -> None:
        self.assertEqual(set(NAMES), set(LANGUAGES))
        self.assertTrue(all(supports(lang) for lang in LANGUAGES))
        self.assertFalse(supports("rust"))


class OracleTests(unittest.TestCase):

    def test_the_oracle_agrees_with_answers_worked_out_by_hand(self) -> None:
        for p in puzzles():
            for n in (1, 2):
                part = p.part(n)
                with self.subTest(puzzle=p.id, part=n):
                    self.assertTrue(part.checks)
                    for args, want in part.checks:
                        got = part.solve(*args)
                        self.assertEqual(got, want, f"{p.id} part {n} {args}")
                        self.assertEqual(isinstance(got, bool), isinstance(want, bool))

    def test_a_hand_written_answer_is_about_a_real_case(self) -> None:
        for p in puzzles():
            for n in (1, 2):
                part = p.part(n)
                for args, _ in part.checks:
                    with self.subTest(puzzle=p.id, part=n, args=args):
                        self.assertIn(tuple(args), [tuple(c) for c in part.cases])

    def test_the_answers_are_not_all_the_same(self) -> None:
        for p in puzzles():
            for n in (1, 2):
                part = p.part(n)
                with self.subTest(puzzle=p.id, part=n):
                    answers = {repr(part.solve(*c)) for c in part.cases}
                    self.assertGreater(len(answers), 1)


class AnswerTests(unittest.TestCase):

    def test_each_answer_passes_its_part_in_both_languages(self) -> None:
        for p in puzzles():
            for n in (1, 2):
                for language in LANGUAGES:
                    with self.subTest(puzzle=p.id, part=n, language=language):
                        outcome = run_part(p, n, answer_for(p, n, language), language)
                        self.assertEqual(outcome.broke, "")
                        failed = [(r.args, r.got, r.want)
                                  for r in outcome.results if not r.passed]
                        self.assertEqual(failed, [])


class TheTwistTests(unittest.TestCase):

    def test_part_ones_answer_fails_part_two(self) -> None:
        for p in puzzles():
            for language in LANGUAGES:
                renamed = answer_for(p, 1, language).replace(
                    function_name(language, 1), function_name(language, 2))
                with self.subTest(puzzle=p.id, language=language):
                    outcome = run_part(p, 2, renamed, language)
                    # It ran - a timeout would also "not pass", and prove
                    # nothing about whether part two is a new question.
                    self.assertEqual(outcome.broke, "", outcome.broke)
                    self.assertFalse(
                        outcome.passed,
                        f"{p.id}: part one's answer already solves part two")


class RouteTests(unittest.TestCase):

    def test_the_list_carries_no_answers(self) -> None:
        from code_coach.api.server import puzzle_list

        listed = puzzle_list()
        self.assertEqual(listed["languages"], list(NAMES))
        text = repr(listed)
        for p in puzzles():
            for n in (1, 2):
                for language in LANGUAGES:
                    with self.subTest(puzzle=p.id, part=n, language=language):
                        self.assertNotIn(answer_for(p, n, language), text)

    def test_only_part_two_counts_the_puzzle(self) -> None:
        from code_coach.api.schemas import PuzzleCheckRequest
        from code_coach.api.server import _store, puzzle_check

        p = puzzles()[0]
        one = puzzle_check(PuzzleCheckRequest(
            puzzle_id=p.id, part=1, code=answer_for(p, 1, "python"), language="python"))
        self.assertTrue(one.passed, one.broke)
        self.assertEqual((one.done, one.lesson), (0, ""))
        self.assertEqual(_store.load().puzzle_counts().get(p.id, 0), 0)
        two = puzzle_check(PuzzleCheckRequest(
            puzzle_id=p.id, part=2, code=answer_for(p, 2, "python"), language="python"))
        self.assertTrue(two.passed, two.broke)
        self.assertEqual((two.done, two.lesson), (1, p.lesson))

    def test_an_unsupported_language_is_refused_not_swapped(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.schemas import PuzzleCheckRequest
        from code_coach.api.server import puzzle_check

        with self.assertRaises(HTTPException) as caught:
            puzzle_check(PuzzleCheckRequest(
                puzzle_id=puzzles()[0].id, part=1, code="", language="rust"))
        self.assertEqual(caught.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
