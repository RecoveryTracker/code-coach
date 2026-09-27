"""The "Working with data" JavaScript pages (178-187).

Written to pass both before and after the pages are registered: the
reference programs and expected outputs are taken from emit_js11 directly,
so nothing here depends on the dispatch in emit.py or the workbook package.
Once registered, the checks that go through Exercise.expect and
Exercise.answer switch on as well.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code
from code_coach.workbook import _value, matches, pages
from code_coach.workbook import emit_js11
from code_coach.workbook.content_js11 import JS11_PAGES

NEW = [(p, e) for p in JS11_PAGES for e in p.exercises]
REGISTERED = any(p.id == JS11_PAGES[0].id for p in pages())


def _expect(e) -> str:
    return emit_js11.expected_output(e.shape, e.args, _value)


def _answer(e) -> str:
    code = emit_js11.solution("javascript", e.shape, e.args)
    assert code is not None
    return code


class ShapeTests(unittest.TestCase):
    def test_ten_pages_of_about_twenty(self) -> None:
        self.assertEqual(len(JS11_PAGES), 10)
        for p in JS11_PAGES:
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
        self.assertEqual(used, set(emit_js11.SHAPE_IDS))
        for shape in emit_js11.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertIsNotNone(emit_js11.for_shape(shape))

    def test_ids_are_new(self) -> None:
        mine_pages = {p.id for p in JS11_PAGES}
        mine_ex = [e.id for _, e in NEW]
        self.assertEqual(len(mine_ex), len(set(mine_ex)))
        self.assertEqual(len(mine_pages), len(JS11_PAGES))
        others = [p for p in pages() if p.id not in mine_pages]
        self.assertFalse(mine_pages & {p.id for p in others})
        self.assertFalse(
            set(mine_ex) & {e.id for p in others for e in p.exercises})

    def test_numbers_follow_the_rest_of_the_javascript_book(self) -> None:
        numbers = [p.number for p in JS11_PAGES]
        self.assertEqual(numbers, list(range(numbers[0], numbers[0] + 10)))
        mine = {p.id for p in JS11_PAGES}
        before = [p.number for p in pages("javascript") if p.id not in mine]
        self.assertGreater(numbers[0], max(before))
        # The regex pages (content_js10) sit directly before these.
        try:
            from code_coach.workbook.content_js10 import JS10_PAGES
        except ImportError:
            return
        self.assertEqual(numbers[0], max(p.number for p in JS10_PAGES) + 1)

    def test_prompts_are_sentences_without_syntax(self) -> None:
        for p, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertGreater(len(e.prompt), 20)
                self.assertTrue(e.prompt.strip().endswith("."))
                for giveaway in ("print(", "console.log", "println", "printf"):
                    self.assertNotIn(giveaway, e.prompt)

    def test_no_two_exercises_on_a_page_are_the_same(self) -> None:
        for p in JS11_PAGES:
            with self.subTest(page=p.id):
                asked = [(e.prompt, _expect(e)) for e in p.exercises]
                self.assertEqual(len(asked), len(set(asked)))

    def test_every_exercise_prints_something(self) -> None:
        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertTrue(_expect(e).strip())

    def test_programs_are_short(self) -> None:
        """3-10 lines of logic, not counting the data literal."""
        for _, e in NEW:
            code = _answer(e)
            logic = code.split("];", 1)[1].strip().splitlines()
            with self.subTest(exercise=e.id):
                self.assertLessEqual(len(logic), 10)
                self.assertGreaterEqual(len(code.splitlines()), 3)

    def test_the_pages_really_vary(self) -> None:
        """Where a page has variants, both answers show up somewhere."""
        by_page = {p.id: [_expect(e) for e in p.exercises] for p in JS11_PAGES}
        some = [out.split("\n") for out in by_page["js-data-some-every"]]
        for line in range(3):
            with self.subTest(line=line):
                self.assertEqual({s[line] for s in some}, {"true", "false"})

    @unittest.skipUnless(REGISTERED, "not registered in content.py yet")
    def test_registered_dispatch_agrees(self) -> None:
        from code_coach.workbook.complexity import for_shape

        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertEqual(e.expect, _expect(e))
                self.assertEqual(e.answer("javascript"), _answer(e))
                self.assertIsNone(e.answer("python"))
        for shape in emit_js11.SHAPE_IDS:
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
