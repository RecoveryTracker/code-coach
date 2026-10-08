"""The "Bodybuilding" JavaScript pages (228-237).

Written to pass both before and after the pages are registered: the
reference programs and expected outputs are taken from emit_jslifting
directly, so nothing here depends on the dispatch in emit.py or the
workbook package. Once registered, the checks that go through
Exercise.expect and Exercise.answer switch on as well.

The expected outputs are worked out in Python, with toFixed and Math.round
modelled on the exact value of the double; the run test is what proves node
prints the same. The planets pages (218-227) are being written alongside
these, so they are checked against when they exist and skipped when not.
"""

from __future__ import annotations

import importlib
import unittest

from code_coach.engine import run_code
from code_coach.workbook import Page, _value, matches, pages
from code_coach.workbook import emit_jslifting
from code_coach.workbook.content_jslifting import JSLIFTING_PAGES

NEW = [(p, e) for p in JSLIFTING_PAGES for e in p.exercises]
REGISTERED = any(p.id == JSLIFTING_PAGES[0].id for p in pages())


def _expect(e) -> str:
    return emit_jslifting.expected_output(e.shape, e.args, _value)


def _answer(e) -> str:
    code = emit_jslifting.solution("javascript", e.shape, e.args)
    assert code is not None
    return code


def _module(name: str):
    """A workbook module that may not have been written yet, or None."""
    try:
        return importlib.import_module(f"code_coach.workbook.{name}")
    except ImportError:
        return None


def _planet_pages() -> list[Page]:
    """The planets pages, registered or not; empty until the module exists.

    Found by type rather than by name, so this does not have to guess what
    that set calls its tuple of pages.
    """
    mod = _module("content_jsplanets")
    if mod is None:
        return []
    found: dict[str, Page] = {}
    for value in vars(mod).values():
        if isinstance(value, tuple) and value and all(
                isinstance(p, Page) for p in value):
            for p in value:
                found.setdefault(p.id, p)
    return list(found.values())


def _others() -> list[Page]:
    """Every page that is not one of these, registered or not."""
    mine = {p.id for p in JSLIFTING_PAGES}
    found = {p.id: p for p in pages() if p.id not in mine}
    for p in _planet_pages():
        found.setdefault(p.id, p)
    return list(found.values())


def _outputs(page_id: str) -> list[str]:
    page = next(p for p in JSLIFTING_PAGES if p.id == page_id)
    return [_expect(e) for e in page.exercises]


def _lines(page_id: str) -> set[str]:
    return {line for out in _outputs(page_id) for line in out.split("\n")}


class ShapeTests(unittest.TestCase):
    def test_ten_pages_of_about_twenty(self) -> None:
        self.assertEqual(len(JSLIFTING_PAGES), 10)
        for p in JSLIFTING_PAGES:
            with self.subTest(page=p.id):
                self.assertTrue(p.id.startswith("js-lift-"))
                self.assertTrue(p.name.startswith("Bodybuilding: "))
                self.assertGreaterEqual(len(p.exercises), 18)
                self.assertLessEqual(len(p.exercises), 22)
                self.assertEqual(len({e.shape for e in p.exercises}), 1)
                self.assertEqual(p.languages, ("javascript",))
                self.assertEqual(p.tier, "intermediate")
                self.assertGreater(len(p.teaches), 20)
                self.assertGreater(len(p.example), 60)

    def test_every_shape_has_a_page_and_a_note(self) -> None:
        used = [p.exercises[0].shape for p in JSLIFTING_PAGES]
        self.assertEqual(used, list(emit_jslifting.SHAPE_IDS))
        for shape in emit_jslifting.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertTrue(shape.startswith("js_lift_"))
                self.assertTrue(emit_jslifting.handles(shape))
                self.assertIsNotNone(emit_jslifting.for_shape(shape))

    def test_ids_are_new(self) -> None:
        mine_pages = {p.id for p in JSLIFTING_PAGES}
        mine_ex = [e.id for _, e in NEW]
        self.assertEqual(len(mine_ex), len(set(mine_ex)))
        self.assertEqual(len(mine_pages), len(JSLIFTING_PAGES))
        for p in JSLIFTING_PAGES:
            for i, e in enumerate(p.exercises):
                self.assertEqual(e.id, f"{p.id}-{i + 1:02d}")
        others = _others()
        self.assertFalse(mine_pages & {p.id for p in others})
        self.assertFalse(
            set(mine_ex) & {e.id for p in others for e in p.exercises})

    def test_shape_ids_are_new(self) -> None:
        from code_coach.workbook.emit import all_shape_ids

        mine = set(emit_jslifting.SHAPE_IDS)
        self.assertEqual(len(mine), len(emit_jslifting.SHAPE_IDS))
        others = {e.shape for p in _others() for e in p.exercises}
        others |= set(all_shape_ids()) - mine
        planets = _module("emit_jsplanets")
        if planets is not None:
            others |= set(getattr(planets, "SHAPE_IDS", ()))
        self.assertFalse(mine & others)

    def test_numbers_follow_the_planets_pages(self) -> None:
        numbers = [p.number for p in JSLIFTING_PAGES]
        self.assertEqual(numbers, list(range(228, 238)))
        mine = {p.id for p in JSLIFTING_PAGES}
        # No other JavaScript page uses these numbers; later pages may
        # follow at 238.
        others = {p.number for p in pages("javascript") if p.id not in mine}
        others |= {p.number for p in _planet_pages()}
        self.assertFalse(others & set(numbers))
        # The planets pages sit directly before these, once they exist.
        planets = _planet_pages()
        if planets:
            self.assertEqual(numbers[0], max(p.number for p in planets) + 1)

    def test_prompts_are_sentences_without_syntax(self) -> None:
        for p, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertGreater(len(e.prompt), 20)
                self.assertTrue(e.prompt.strip().endswith("."))
                for giveaway in ("print(", "console.log", "println", "printf"):
                    self.assertNotIn(giveaway, e.prompt)

    def test_no_two_exercises_on_a_page_are_the_same(self) -> None:
        for p in JSLIFTING_PAGES:
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
                        emit_jslifting.solution(language, e.shape, e.args))

    def test_programs_are_short(self) -> None:
        """3-10 lines: a formula, not a project."""
        for _, e in NEW:
            lines = _answer(e).splitlines()
            with self.subTest(exercise=e.id):
                self.assertGreaterEqual(len(lines), 3)
                self.assertLessEqual(len(lines), 10)

    def test_the_pages_really_vary(self) -> None:
        """Every yes-no page says yes and no; every two-way page shows both."""
        for page in ("js-lift-volume", "js-lift-split"):
            with self.subTest(page=page):
                self.assertEqual(_lines(page) & {"true", "false"},
                                 {"true", "false"})
        # Some sets are estimated, some turned away by a guard clause.
        onerm = _lines("js-lift-onerm")
        self.assertIn("too many reps", onerm)
        self.assertTrue(any(line[:1].isdigit() for line in onerm))
        # Rounding to 2.5 kg moves some weights and leaves others alone.
        moved = [float(_expect(e)) != e.args["max"] * e.args["percent"] / 100
                 for p, e in NEW if p.id == "js-lift-percent"
                 and e.args["want"] == "one"]
        self.assertIn(True, moved)
        self.assertIn(False, moved)
        # Some plans end on a deload week and some do not, and some reach
        # their goal a week late because the plan got there on a deload.
        finals = {e.args["weeks"] % e.args["every"] == 0 for _, e in NEW
                  if e.shape == "js_lift_overload" and e.args["want"] == "final"}
        self.assertEqual(finals, {True, False})
        late = []
        for _, e in NEW:
            if e.shape == "js_lift_overload" and e.args["want"] == "goal":
                a, week = e.args, int(_expect(e))
                plan_before = a["start"] + (week - 2) * a["step"]
                late.append(week > 1 and (week - 1) % a["every"] == 0
                            and plan_before >= a["goal"])
        self.assertIn(True, late)
        self.assertIn(False, late)
        # Some sessions break records and some break none, and a lift that
        # is not in the log prints none.
        records = _lines("js-lift-records")
        self.assertIn("records broken: 0", records)
        self.assertTrue(any(line.startswith("records broken: ")
                            and line != "records broken: 0" for line in records))
        self.assertTrue(any(line.endswith(" none") for line in records))
        # Some loads come out exactly and some leave something over.
        plates = _lines("js-lift-plates")
        self.assertIn("exact", plates)
        self.assertTrue(any(line.endswith(" left over") for line in plates))
        # One split is two days running only because Sunday runs into Monday.
        wraps = []
        for _, e in NEW:
            if e.shape == "js_lift_split" and e.args["want"] == "row":
                days = e.args["days"]
                inside = any(set(days[i][1]) & set(days[i + 1][1])
                             for i in range(len(days) - 1))
                wraps.append(_expect(e) == "true" and not inside)
        self.assertIn(True, wraps)

    def test_the_oracle_refuses_bad_data(self) -> None:
        bad = (
            # 75% of 145 kg is 108.75, 43.5 steps of 2.5: a halfway case.
            ("js_lift_percent", {"want": "one", "max": 145, "percent": 75}),
            # 15% of 85 kg is 12.75: on the edge at one decimal place.
            ("js_lift_bodycomp", {"want": "lean", "weight": 85, "fat": 15}),
            # The formulas are only for 2 to 10 reps.
            ("js_lift_onerm", {"want": "epley", "kg": 100, "reps": 12}),
            # 101 kg leaves 0.5 over, so it is not a plain loading row.
            ("js_lift_plates", {"want": "kg", "target": 101}),
            # 100 down by 30 never shows 0.
            ("js_lift_timer", {"want": "countdown", "rest": 100, "step": 30}),
            # Today's bench has no record to beat.
            ("js_lift_records", {"want": "new", "records": (("squat", 100),),
                                 "today": (("bench", 80),)}),
            # A day missing from the week.
            ("js_lift_split", {"want": "rest",
                               "days": (("Mon", ("legs",)), ("Tue", ()))}),
        )
        for shape, args in bad:
            with self.subTest(shape=shape, args=args):
                with self.assertRaises(ValueError):
                    emit_jslifting.expected_output(shape, args)
        with self.assertRaises(ValueError):  # a quote inside a name
            emit_jslifting.solution(
                "javascript", "js_lift_records",
                {"want": "best", "log": (('say "hi"', 100), ("squat", 90))})

    @unittest.skipUnless(REGISTERED, "not registered in content.py yet")
    def test_registered_dispatch_agrees(self) -> None:
        from code_coach.workbook.complexity import for_shape

        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertEqual(e.expect, _expect(e))
                self.assertEqual(e.answer("javascript"), _answer(e))
                self.assertIsNone(e.answer("python"))
        for shape in emit_jslifting.SHAPE_IDS:
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
