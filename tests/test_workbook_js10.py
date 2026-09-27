"""Pages 168-177: regex from zero, in JavaScript.

Checked straight from the new modules rather than through pages(), so the
suite holds before and after the pages are registered in content.py.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code
from code_coach.workbook import matches, pages
from code_coach.workbook import complexity_js10, emit_js10
from code_coach.workbook.content_js10 import JS10_PAGES


def _expect(e) -> str:
    return emit_js10.expected_output(e.shape, e.args, None)


class ShapeTests(unittest.TestCase):
    def test_ten_pages_numbered_after_the_javascript_book(self) -> None:
        self.assertEqual(len(JS10_PAGES), 10)
        numbers = [p.number for p in JS10_PAGES]
        self.assertEqual(numbers, list(range(168, 178)))
        # No other JavaScript page may use these numbers. Not "nothing comes
        # after them": the Working with data pages follow at 178.
        existing = {
            p.number for p in pages("javascript") if p not in JS10_PAGES
        }
        self.assertFalse(existing & set(numbers))

    def test_every_page_is_javascript_only_and_intermediate(self) -> None:
        for p in JS10_PAGES:
            with self.subTest(page=p.id):
                self.assertEqual(p.languages, ("javascript",))
                self.assertEqual(p.tier, "intermediate")
                self.assertGreater(len(p.teaches), 20)
                self.assertGreater(len(p.example), 60)

    def test_about_twenty_exercises_a_page_one_shape_each(self) -> None:
        for p in JS10_PAGES:
            with self.subTest(page=p.id):
                self.assertGreaterEqual(len(p.exercises), 18)
                self.assertLessEqual(len(p.exercises), 22)
                self.assertEqual(len({e.shape for e in p.exercises}), 1)

    def test_ids_are_unique_against_every_existing_page(self) -> None:
        mine_pages = {p.id for p in JS10_PAGES}
        mine_ex = [e.id for p in JS10_PAGES for e in p.exercises]
        self.assertEqual(len(mine_ex), len(set(mine_ex)))
        others = [p for p in pages() if p.id not in mine_pages]
        self.assertFalse(mine_pages & {p.id for p in others})
        self.assertFalse(
            set(mine_ex) & {e.id for p in others for e in p.exercises})

    def test_prompts_are_sentences_and_never_give_away_printing(self) -> None:
        for p in JS10_PAGES:
            asked = [(e.prompt, _expect(e)) for e in p.exercises]
            self.assertEqual(len(asked), len(set(asked)), p.id)
            for e in p.exercises:
                with self.subTest(exercise=e.id):
                    self.assertGreater(len(e.prompt), 20)
                    self.assertTrue(e.prompt.endswith("."))
                    for giveaway in ("print(", "console.log", "println"):
                        self.assertNotIn(giveaway, e.prompt)

    def test_every_shape_is_used_and_has_a_complexity_note(self) -> None:
        used = {e.shape for p in JS10_PAGES for e in p.exercises}
        self.assertEqual(used, set(emit_js10.SHAPE_IDS))
        for shape in emit_js10.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertIsNotNone(complexity_js10.for_shape(shape))

    def test_programs_are_short(self) -> None:
        for p in JS10_PAGES:
            for e in p.exercises:
                with self.subTest(exercise=e.id):
                    lines = emit_js10.solution("javascript", e.shape, e.args)
                    self.assertLessEqual(len(lines.splitlines()), 6)
                    self.assertGreaterEqual(len(lines.splitlines()), 3)

    def test_other_languages_get_no_answer(self) -> None:
        e = JS10_PAGES[0].exercises[0]
        self.assertIsNone(emit_js10.solution("python", e.shape, e.args))
        with self.assertRaises(KeyError):
            emit_js10.expected_output("nonsense", {}, None)


class ReferenceRunTests(unittest.TestCase):
    def _run(self, e) -> None:
        code = emit_js10.solution("javascript", e.shape, e.args)
        out, err, code_ = run_code(code, language="javascript")
        self.assertEqual(code_, 0, f"{e.id} failed:\n{code}\n{err}")
        self.assertTrue(
            matches(out, _expect(e)),
            f"{e.id} printed:\n{out}\nexpected:\n{_expect(e)}\n\n{code}",
        )


def _add(page) -> None:
    def test(self) -> None:
        for e in page.exercises:
            with self.subTest(exercise=e.id):
                self._run(e)

    name = "test_" + page.id.replace("-", "_") + "_answers_print_expect"
    test.__doc__ = f"Page {page.number}: every reference answer runs in node"
    setattr(ReferenceRunTests, name, test)


for _p in JS10_PAGES:
    _add(_p)


if __name__ == "__main__":
    unittest.main()
