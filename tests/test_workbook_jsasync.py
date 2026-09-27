"""The "Async JavaScript" pages (208-217).

Written to pass both before and after the pages are registered: the
reference programs and expected outputs are taken from emit_jsasync
directly, so nothing here depends on the dispatch in emit.py or the
workbook package. Once registered, the checks that go through
Exercise.expect and Exercise.answer switch on as well.

The expected outputs are worked out in Python from the ordering rules
(synchronous lines, then promise callbacks, then timers soonest first);
the run test is what proves node agrees with that model.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code
from code_coach.workbook import _value, matches, pages
from code_coach.workbook import emit_jsasync
from code_coach.workbook.content_jsasync import JSASYNC_PAGES

NEW = [(p, e) for p in JSASYNC_PAGES for e in p.exercises]
REGISTERED = any(p.id == JSASYNC_PAGES[0].id for p in pages())


def _expect(e) -> str:
    return emit_jsasync.expected_output(e.shape, e.args, _value)


def _answer(e) -> str:
    code = emit_jsasync.solution("javascript", e.shape, e.args)
    assert code is not None
    return code


def _others():
    """Every page that is not one of these, registered or not."""
    mine = {p.id for p in JSASYNC_PAGES}
    found = {p.id: p for p in pages() if p.id not in mine}
    for module, name in (("content_jsgame", "JSGAME_PAGES"),
                         ("content_jsbuild", "JSBUILD_PAGES")):
        try:
            mod = __import__(f"code_coach.workbook.{module}", fromlist=[name])
        except ImportError:
            continue
        for p in getattr(mod, name):
            found.setdefault(p.id, p)
    return list(found.values())


class ShapeTests(unittest.TestCase):
    def test_ten_pages_of_about_twenty(self) -> None:
        self.assertEqual(len(JSASYNC_PAGES), 10)
        for p in JSASYNC_PAGES:
            with self.subTest(page=p.id):
                self.assertTrue(p.id.startswith("js-async-"))
                self.assertTrue(p.name.startswith("Async JavaScript: "))
                self.assertGreaterEqual(len(p.exercises), 18)
                self.assertLessEqual(len(p.exercises), 22)
                self.assertEqual(len({e.shape for e in p.exercises}), 1)
                self.assertEqual(p.languages, ("javascript",))
                self.assertEqual(p.tier, "intermediate")
                self.assertGreater(len(p.teaches), 20)
                self.assertGreater(len(p.example), 60)

    def test_every_shape_has_a_page_and_a_note(self) -> None:
        used = [p.exercises[0].shape for p in JSASYNC_PAGES]
        self.assertEqual(used, list(emit_jsasync.SHAPE_IDS))
        for shape in emit_jsasync.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertTrue(shape.startswith("jsa_"))
                self.assertIsNotNone(emit_jsasync.for_shape(shape))

    def test_shapes_are_new(self) -> None:
        from code_coach.workbook.emit import all_shape_ids

        mine = set(emit_jsasync.SHAPE_IDS)
        self.assertEqual(len(mine), len(emit_jsasync.SHAPE_IDS))
        others = {e.shape for p in _others() for e in p.exercises}
        others |= set(all_shape_ids()) - mine
        self.assertFalse(mine & others)

    def test_ids_are_new(self) -> None:
        mine_pages = {p.id for p in JSASYNC_PAGES}
        mine_ex = [e.id for _, e in NEW]
        self.assertEqual(len(mine_ex), len(set(mine_ex)))
        self.assertEqual(len(mine_pages), len(JSASYNC_PAGES))
        others = _others()
        self.assertFalse(mine_pages & {p.id for p in others})
        self.assertFalse(
            set(mine_ex) & {e.id for p in others for e in p.exercises})

    def test_numbers_follow_the_game_pages(self) -> None:
        numbers = [p.number for p in JSASYNC_PAGES]
        self.assertEqual(numbers, list(range(208, 218)))
        mine = {p.id for p in JSASYNC_PAGES}
        # No other page uses these numbers; later pages may follow at 218.
        others = {p.number for p in pages("javascript") if p.id not in mine}
        self.assertFalse(others & set(numbers))
        from code_coach.workbook.content_jsbuild import JSBUILD_PAGES

        self.assertEqual(numbers[0], max(p.number for p in JSBUILD_PAGES) + 1)

    def test_prompts_are_sentences_without_syntax(self) -> None:
        for p, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertGreater(len(e.prompt), 20)
                self.assertTrue(e.prompt.strip().endswith("."))
                for giveaway in ("print(", "console.log", "println", "printf"):
                    self.assertNotIn(giveaway, e.prompt)

    def test_no_two_exercises_on_a_page_are_the_same(self) -> None:
        for p in JSASYNC_PAGES:
            with self.subTest(page=p.id):
                asked = [(e.prompt, _expect(e)) for e in p.exercises]
                self.assertEqual(len(asked), len(set(asked)))

    def test_every_exercise_prints_something(self) -> None:
        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertTrue(_expect(e).strip())

    def test_programs_are_short(self) -> None:
        """About ten lines of logic, not counting data or the sleep helper.

        A leading `const name = [...]` literal is data, and the one-line
        sleep helper is the same on every page that uses it.
        """
        for _, e in NEW:
            code = _answer(e).splitlines()
            logic = [line for line in code if line != emit_jsasync.SLEEP]
            if logic[0].startswith("const ") and logic[0].endswith("];"):
                logic = logic[1:]
            with self.subTest(exercise=e.id):
                self.assertLessEqual(len(logic), 11)
                self.assertGreaterEqual(len(code), 2)

    def test_no_answer_reads_the_clock(self) -> None:
        for _, e in NEW:
            code = _answer(e)
            with self.subTest(exercise=e.id):
                for clock in ("Date", "performance", "hrtime", "console.time"):
                    self.assertNotIn(clock, code)

    def test_other_languages_get_no_answer(self) -> None:
        for _, e in NEW:
            for language in ("python", "typescript", "dart", "c"):
                with self.subTest(exercise=e.id, language=language):
                    self.assertIsNone(
                        emit_jsasync.solution(language, e.shape, e.args))

    def test_the_pages_really_vary(self) -> None:
        """Where a page has two versions, both show up somewhere."""
        def args(shape, key):
            return {bool(e.args.get(key)) if key != "want" and key != "rule"
                    else e.args[key]
                    for _, e in NEW if e.shape == shape}

        self.assertEqual(args("jsa_callback", "later"), {True, False})
        self.assertEqual(args("jsa_then", "forget"), {True, False})
        self.assertEqual(args("jsa_parallel", "want"), {"one", "all"})
        self.assertEqual(args("jsa_trycatch", "rule"), {"min", "even"})
        self.assertEqual({e.args["delay"] is None for _, e in NEW
                          if e.shape == "jsa_promise"}, {True, False})
        self.assertEqual({e.args["again"] is None for _, e in NEW
                          if e.shape == "jsa_promise"}, {True, False})
        # Timers that tie, fired in the order they were set.
        self.assertTrue(any(
            len([ms for _, ms in e.args["steps"] if ms is not None])
            != len({ms for _, ms in e.args["steps"] if ms is not None})
            for _, e in NEW if e.shape == "jsa_later"))
        # A callback called later prints after the line below the call.
        for _, e in NEW:
            if e.shape == "jsa_callback":
                first = _expect(e).split("\n")[0]
                self.assertEqual(first == e.args["word"], e.args["later"])

    def test_the_oracle_refuses_bad_data(self) -> None:
        with self.assertRaises(ValueError):  # delay 1 ties with 0 in node
            emit_jsasync.expected_output(
                "jsa_later", {"steps": (("a", 1), ("b", None))})
        with self.assertRaises(ValueError):  # nothing written after a timer
            emit_jsasync.expected_output(
                "jsa_later", {"steps": (("a", None), ("b", 10))})
        with self.assertRaises(ValueError):  # a tie makes the order a guess
            emit_jsasync.expected_output(
                "jsa_all", {"fn": "f", "give": "upper",
                            "jobs": (("a", 20), ("b", 10), ("c", 10))})
        with self.assertRaises(ValueError):
            emit_jsasync.solution(
                "javascript", "jsa_await",
                {"pre": (), "before": 'say "hi"', "value": 1, "after": "b",
                 "post": ("c",)})

    @unittest.skipUnless(REGISTERED, "not registered in content.py yet")
    def test_registered_dispatch_agrees(self) -> None:
        from code_coach.workbook.complexity import for_shape

        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertEqual(e.expect, _expect(e))
                self.assertEqual(e.answer("javascript"), _answer(e))
                self.assertIsNone(e.answer("python"))
        for shape in emit_jsasync.SHAPE_IDS:
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
