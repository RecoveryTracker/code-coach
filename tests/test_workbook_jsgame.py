"""The "Game math" JavaScript pages (188-197).

Written to pass both before and after the pages are registered: the
reference programs and expected outputs are taken from emit_jsgame directly,
so nothing here depends on the dispatch in emit.py or the workbook package.
Once registered, the checks that go through Exercise.expect and
Exercise.answer switch on as well.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code
from code_coach.workbook import _value, matches, pages
from code_coach.workbook import emit_jsgame
from code_coach.workbook.content_jsgame import JSGAME_PAGES

NEW = [(p, e) for p in JSGAME_PAGES for e in p.exercises]
REGISTERED = any(p.id == JSGAME_PAGES[0].id for p in pages())


def _expect(e) -> str:
    return emit_jsgame.expected_output(e.shape, e.args, _value)


def _answer(e) -> str:
    code = emit_jsgame.solution("javascript", e.shape, e.args)
    assert code is not None
    return code


class ShapeTests(unittest.TestCase):
    def test_ten_pages_of_about_twenty(self) -> None:
        self.assertEqual(len(JSGAME_PAGES), 10)
        for p in JSGAME_PAGES:
            with self.subTest(page=p.id):
                self.assertGreaterEqual(len(p.exercises), 18)
                self.assertLessEqual(len(p.exercises), 22)
                self.assertEqual(len({e.shape for e in p.exercises}), 1)
                self.assertEqual(p.languages, ("javascript",))
                self.assertEqual(p.tier, "intermediate")
                self.assertGreater(len(p.teaches), 20)
                self.assertGreater(len(p.example), 60)

    def test_every_shape_has_a_page_and_a_note(self) -> None:
        used = {e.shape for _, e in NEW}
        self.assertEqual(used, set(emit_jsgame.SHAPE_IDS))
        for shape in emit_jsgame.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertIsNotNone(emit_jsgame.for_shape(shape))

    def test_ids_are_new(self) -> None:
        mine_pages = {p.id for p in JSGAME_PAGES}
        mine_ex = [e.id for _, e in NEW]
        self.assertEqual(len(mine_ex), len(set(mine_ex)))
        self.assertEqual(len(mine_pages), len(JSGAME_PAGES))
        others = [p for p in pages() if p.id not in mine_pages]
        self.assertFalse(mine_pages & {p.id for p in others})
        self.assertFalse(
            set(mine_ex) & {e.id for p in others for e in p.exercises})

    def test_shape_ids_are_new(self) -> None:
        from code_coach.workbook.emit_js11 import SHAPE_IDS as JS11_SHAPES

        self.assertFalse(set(emit_jsgame.SHAPE_IDS) & set(JS11_SHAPES))
        mine = {p.id for p in JSGAME_PAGES}
        other_shapes = {e.shape for p in pages() if p.id not in mine
                        for e in p.exercises}
        self.assertFalse(set(emit_jsgame.SHAPE_IDS) & other_shapes)

    def test_numbers_follow_the_rest_of_the_javascript_book(self) -> None:
        numbers = [p.number for p in JSGAME_PAGES]
        self.assertEqual(numbers, list(range(188, 198)))
        mine = {p.id for p in JSGAME_PAGES}
        before = [p.number for p in pages("javascript")
                  if p.id not in mine and p.number < numbers[0]]
        self.assertEqual(max(before), numbers[0] - 1)
        # The data pages (content_js11) sit directly before these.
        from code_coach.workbook.content_js11 import JS11_PAGES

        self.assertEqual(numbers[0], max(p.number for p in JS11_PAGES) + 1)
        self.assertFalse(
            set(numbers) & {p.number for p in pages("javascript")
                            if p.id not in mine})

    def test_prompts_are_sentences_without_syntax(self) -> None:
        for p, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertGreater(len(e.prompt), 20)
                self.assertTrue(e.prompt.strip().endswith("."))
                for giveaway in ("print(", "console.log", "println", "printf"):
                    self.assertNotIn(giveaway, e.prompt)

    def test_no_two_exercises_on_a_page_are_the_same(self) -> None:
        for p in JSGAME_PAGES:
            with self.subTest(page=p.id):
                asked = [(e.prompt, _expect(e)) for e in p.exercises]
                self.assertEqual(len(asked), len(set(asked)))

    def test_every_exercise_prints_something(self) -> None:
        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertTrue(_expect(e).strip())

    def test_other_languages_get_no_answer(self) -> None:
        for _, e in NEW:
            for language in ("python", "typescript", "dart", "rust"):
                with self.subTest(exercise=e.id, language=language):
                    self.assertIsNone(
                        emit_jsgame.solution(language, e.shape, e.args))

    def test_programs_are_short(self) -> None:
        """3-10 lines: a formula, not a project."""
        for _, e in NEW:
            lines = _answer(e).splitlines()
            with self.subTest(exercise=e.id):
                self.assertGreaterEqual(len(lines), 3)
                self.assertLessEqual(len(lines), 10)

    def test_the_pages_really_vary(self) -> None:
        """Every yes-no page says yes somewhere and no somewhere."""
        by_page = {p.id: [_expect(e) for e in p.exercises]
                   for p in JSGAME_PAGES}
        for page in ("js-game-distance", "js-game-aabb", "js-game-circles"):
            said = {line for out in by_page[page] for line in out.split("\n")
                    if line in ("true", "false")}
            with self.subTest(page=page):
                self.assertEqual(said, {"true", "false"})
        # Clamping has to leave some values alone and change others.
        clamp = JSGAME_PAGES[0].exercises
        changed = [_expect(e) != str(e.args["value"]) for e in clamp
                   if e.args["want"] == "clamp"]
        self.assertIn(True, changed)
        self.assertIn(False, changed)

    @unittest.skipUnless(REGISTERED, "not registered in content.py yet")
    def test_registered_dispatch_agrees(self) -> None:
        from code_coach.workbook.complexity import for_shape

        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertEqual(e.expect, _expect(e))
                self.assertEqual(e.answer("javascript"), _answer(e))
                self.assertIsNone(e.answer("python"))
        for shape in emit_jsgame.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertIsNotNone(for_shape(shape))


class ReferenceRunTests(unittest.TestCase):
    TIMED_OUT = 124

    def test_every_reference_answer_prints_what_it_should(self) -> None:
        for _, e in NEW:
            code = _answer(e)
            with self.subTest(exercise=e.id):
                stdout, stderr, code_ = run_code(code, language="javascript")
                if code_ == self.TIMED_OUT:
                    stdout, stderr, code_ = run_code(code, language="javascript")
                self.assertEqual(code_, 0, (stderr or stdout)[:400])
                self.assertTrue(
                    matches(stdout, _expect(e)),
                    f"printed {stdout!r}, wanted {_expect(e)!r}\n{code}")


if __name__ == "__main__":
    unittest.main()
