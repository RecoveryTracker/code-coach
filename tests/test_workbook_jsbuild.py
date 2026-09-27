"""The "Building a game" JavaScript pages (198-207).

Written to pass both before and after the pages are registered: the
reference programs and expected outputs are taken from emit_jsbuild
directly, so nothing here depends on the dispatch in emit.py or the
workbook package. Once registered, the checks that go through
Exercise.expect and Exercise.answer switch on as well.
"""

from __future__ import annotations

import re
import unittest

from code_coach.engine import run_code
from code_coach.workbook import _value, matches, pages
from code_coach.workbook import emit_jsbuild
from code_coach.workbook.content_jsbuild import JSBUILD_PAGES

NEW = [(p, e) for p in JSBUILD_PAGES for e in p.exercises]
REGISTERED = any(p.id == JSBUILD_PAGES[0].id for p in pages())


def _expect(e) -> str:
    return emit_jsbuild.expected_output(e.shape, e.args, _value)


def _answer(e) -> str:
    code = emit_jsbuild.solution("javascript", e.shape, e.args)
    assert code is not None
    return code


def _others():
    """Every page that is not one of these, registered or not.

    The game-math pages (content_jsgame) are being written alongside these
    and may not be registered yet, so they are added by hand when the
    module exists and left out when it does not.
    """
    mine = {p.id for p in JSBUILD_PAGES}
    found = {p.id: p for p in pages() if p.id not in mine}
    try:
        from code_coach.workbook.content_jsgame import JSGAME_PAGES
    except ImportError:
        JSGAME_PAGES = ()
    for p in JSGAME_PAGES:
        found.setdefault(p.id, p)
    return list(found.values())


class ShapeTests(unittest.TestCase):
    def test_ten_pages_of_about_twenty(self) -> None:
        self.assertEqual(len(JSBUILD_PAGES), 10)
        for p in JSBUILD_PAGES:
            with self.subTest(page=p.id):
                self.assertTrue(p.id.startswith("js-build-"))
                self.assertGreaterEqual(len(p.exercises), 18)
                self.assertLessEqual(len(p.exercises), 22)
                self.assertEqual(len({e.shape for e in p.exercises}), 1)
                self.assertEqual(p.languages, ("javascript",))
                self.assertEqual(p.tier, "intermediate")
                self.assertGreater(len(p.teaches), 20)
                self.assertGreater(len(p.example), 60)

    def test_every_shape_has_a_page_and_a_note(self) -> None:
        used = {e.shape for _, e in NEW}
        self.assertEqual(used, set(emit_jsbuild.SHAPE_IDS))
        for shape in emit_jsbuild.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertTrue(shape.startswith("jsb_"))
                self.assertIsNotNone(emit_jsbuild.for_shape(shape))

    def test_shapes_are_new(self) -> None:
        from code_coach.workbook.emit import all_shape_ids

        mine = set(emit_jsbuild.SHAPE_IDS)
        self.assertEqual(len(mine), len(emit_jsbuild.SHAPE_IDS))
        others = {e.shape for p in _others() for e in p.exercises}
        others |= set(all_shape_ids()) - mine
        try:
            from code_coach.workbook.emit_jsgame import SHAPE_IDS as GAME
        except ImportError:
            GAME = ()
        self.assertFalse(mine & (others | set(GAME)))

    def test_ids_are_new(self) -> None:
        mine_pages = {p.id for p in JSBUILD_PAGES}
        mine_ex = [e.id for _, e in NEW]
        self.assertEqual(len(mine_ex), len(set(mine_ex)))
        self.assertEqual(len(mine_pages), len(JSBUILD_PAGES))
        others = _others()
        self.assertFalse(mine_pages & {p.id for p in others})
        self.assertFalse(
            set(mine_ex) & {e.id for p in others for e in p.exercises})

    def test_numbers_follow_the_rest_of_the_javascript_book(self) -> None:
        numbers = [p.number for p in JSBUILD_PAGES]
        self.assertEqual(numbers, list(range(198, 208)))
        mine = {p.id for p in JSBUILD_PAGES}
        # No other page uses these numbers; later pages may follow at 208.
        others = {p.number for p in pages("javascript") if p.id not in mine}
        self.assertFalse(others & set(numbers))
        # The game-math pages (content_jsgame) sit directly before these.
        try:
            from code_coach.workbook.content_jsgame import JSGAME_PAGES
        except ImportError:
            return
        self.assertEqual(numbers[0], max(p.number for p in JSGAME_PAGES) + 1)

    def test_prompts_are_sentences_without_syntax(self) -> None:
        for p, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertGreater(len(e.prompt), 20)
                self.assertTrue(e.prompt.strip().endswith("."))
                for giveaway in ("print(", "console.log", "println", "printf"):
                    self.assertNotIn(giveaway, e.prompt)

    def test_no_two_exercises_on_a_page_are_the_same(self) -> None:
        for p in JSBUILD_PAGES:
            with self.subTest(page=p.id):
                asked = [(e.prompt, _expect(e)) for e in p.exercises]
                self.assertEqual(len(asked), len(set(asked)))

    def test_every_exercise_prints_something(self) -> None:
        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertTrue(_expect(e).strip())

    def test_programs_are_short(self) -> None:
        """3-10 lines of logic, not counting a leading data literal.

        The state machine's transition table counts as data, like the
        arrays of entities and map rows, so a literal closed by }; ends
        the data just as ]; does.
        """
        for _, e in NEW:
            code = _answer(e)
            logic = re.split(r"^[\]}];$|\];", code, maxsplit=1, flags=re.M)[-1]
            logic = logic.strip().splitlines()
            with self.subTest(exercise=e.id):
                self.assertLessEqual(len(logic), 10)
                self.assertGreaterEqual(len(code.splitlines()), 3)

    def test_other_languages_get_no_answer(self) -> None:
        for _, e in NEW:
            for language in ("python", "typescript", "dart", "c"):
                with self.subTest(exercise=e.id, language=language):
                    self.assertIsNone(
                        emit_jsbuild.solution(language, e.shape, e.args))

    def test_the_pages_really_vary(self) -> None:
        """Where a page has two endings, both show up somewhere."""
        by_page = {p.id: [_expect(e) for e in p.exercises]
                   for p in JSBUILD_PAGES}
        ends = {out.split("\n")[1] for out in by_page["js-build-state"]}
        self.assertEqual(ends, {"still playing", "game over"})
        walkable = {out.split("\n")[2] for out in by_page["js-build-tiles"]}
        self.assertEqual(walkable, {"true", "false"})
        highs = [out.split(", high score ") for out in by_page["js-build-combo"]]
        self.assertTrue(any(s == "score " + h for s, h in highs))
        self.assertTrue(any(s != "score " + h for s, h in highs))
        loops = {e.args["want"] for p in JSBUILD_PAGES for e in p.exercises
                 if e.shape == "jsb_loop"}
        self.assertEqual(loops, {"move", "wrap"})

    def test_the_oracle_refuses_bad_data(self) -> None:
        with self.assertRaises(ValueError):
            emit_jsbuild.expected_output(
                "jsb_entities", {"var": "enemies", "damage": 9,
                                 "items": (("a", 1), ("b", 2))})
        with self.assertRaises(ValueError):
            emit_jsbuild.expected_output(
                "jsb_tiles", {"rows": ("#@#", "#@#"), "check": (0, 0)})
        with self.assertRaises(ValueError):
            emit_jsbuild.solution(
                "javascript", "jsb_state",
                {"player": "ana", "score": 1.5, "lives": 3, "gain": 1,
                 "lost": 1})

    @unittest.skipUnless(REGISTERED, "not registered in content.py yet")
    def test_registered_dispatch_agrees(self) -> None:
        from code_coach.workbook.complexity import for_shape

        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertEqual(e.expect, _expect(e))
                self.assertEqual(e.answer("javascript"), _answer(e))
                self.assertIsNone(e.answer("python"))
        for shape in emit_jsbuild.SHAPE_IDS:
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
