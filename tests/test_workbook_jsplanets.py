"""The "Planets" JavaScript pages (218-227).

Written to pass both before and after the pages are registered: the
reference programs and expected outputs are taken from emit_jsplanets
directly, so nothing here depends on the dispatch in emit.py or the
workbook package. Once registered, the checks that go through
Exercise.expect and Exercise.answer switch on as well.

The expected outputs are worked out in Python from the formulas, never by
running the JavaScript; the run test is what proves node prints the same
characters.
"""

from __future__ import annotations

import importlib
import pkgutil
import unittest

import code_coach.workbook as workbook
from code_coach.engine import run_code
from code_coach.workbook import Page, _value, matches, pages
from code_coach.workbook import content_jsplanets, emit_jsplanets
from code_coach.workbook.content_jsplanets import JSPLANETS_PAGES

NEW = [(p, e) for p in JSPLANETS_PAGES for e in p.exercises]
REGISTERED = any(p.id == JSPLANETS_PAGES[0].id for p in pages())
BY_ID = {p.id: p for p in JSPLANETS_PAGES}


def _expect(e) -> str:
    return emit_jsplanets.expected_output(e.shape, e.args, _value)


def _answer(e) -> str:
    code = emit_jsplanets.solution("javascript", e.shape, e.args)
    assert code is not None
    return code


def _others() -> list[Page]:
    """Every page that is not one of these, registered or not.

    A set written alongside this one may not be registered yet, so every
    content module's *_PAGES tuple is read as well as pages(). A module
    that will not import is skipped: it is that set's own test's business.
    """
    mine = {id(p) for p in JSPLANETS_PAGES}
    found = {id(p): p for p in pages() if id(p) not in mine}
    for info in pkgutil.iter_modules(workbook.__path__):
        if not info.name.startswith("content_"):
            continue
        try:
            module = importlib.import_module(f"code_coach.workbook.{info.name}")
        except Exception:  # noqa: BLE001 - a set still being written
            continue
        for name, value in vars(module).items():
            if name.endswith("_PAGES") and isinstance(value, tuple):
                for p in value:
                    if isinstance(p, Page) and id(p) not in mine:
                        found.setdefault(id(p), p)
    return list(found.values())


class ShapeTests(unittest.TestCase):
    def test_ten_pages_of_about_twenty(self) -> None:
        self.assertEqual(len(JSPLANETS_PAGES), 10)
        for p in JSPLANETS_PAGES:
            with self.subTest(page=p.id):
                self.assertTrue(p.id.startswith("js-planets-"))
                self.assertTrue(p.name.startswith("Planets: "))
                self.assertGreaterEqual(len(p.exercises), 18)
                self.assertLessEqual(len(p.exercises), 22)
                self.assertEqual(len({e.shape for e in p.exercises}), 1)
                self.assertEqual(p.languages, ("javascript",))
                self.assertEqual(p.tier, "intermediate")
                self.assertGreater(len(p.teaches), 20)
                self.assertGreater(len(p.example), 60)

    def test_every_shape_has_a_page_and_a_note(self) -> None:
        used = [p.exercises[0].shape for p in JSPLANETS_PAGES]
        self.assertEqual(used, list(emit_jsplanets.SHAPE_IDS))
        for shape in emit_jsplanets.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertTrue(shape.startswith("js_planets_"))
                self.assertTrue(emit_jsplanets.handles(shape))
                self.assertIsNotNone(emit_jsplanets.for_shape(shape))

    def test_shapes_are_new(self) -> None:
        from code_coach.workbook.emit import all_shape_ids

        mine = set(emit_jsplanets.SHAPE_IDS)
        self.assertEqual(len(mine), len(emit_jsplanets.SHAPE_IDS))
        others = {e.shape for p in _others() for e in p.exercises}
        others |= set(all_shape_ids()) - mine
        self.assertFalse(mine & others)

    def test_ids_are_new(self) -> None:
        mine_pages = {p.id for p in JSPLANETS_PAGES}
        mine_ex = [e.id for _, e in NEW]
        self.assertEqual(len(mine_ex), len(set(mine_ex)))
        self.assertEqual(len(mine_pages), len(JSPLANETS_PAGES))
        others = _others()
        self.assertFalse(mine_pages & {p.id for p in others})
        self.assertFalse(
            set(mine_ex) & {e.id for p in others for e in p.exercises})

    def test_numbers_follow_the_async_pages(self) -> None:
        numbers = [p.number for p in JSPLANETS_PAGES]
        self.assertEqual(numbers, list(range(218, 228)))
        mine = {p.id for p in JSPLANETS_PAGES}
        # No other JavaScript page uses these numbers, registered or not;
        # later pages may follow at 228.
        theirs = {p.number for p in pages("javascript") if p.id not in mine}
        theirs |= {p.number for p in _others() if "javascript" in p.languages}
        self.assertFalse(theirs & set(numbers))
        from code_coach.workbook.content_jsasync import JSASYNC_PAGES

        self.assertEqual(numbers[0], max(p.number for p in JSASYNC_PAGES) + 1)

    def test_prompts_are_sentences_without_syntax(self) -> None:
        for p, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertGreater(len(e.prompt), 20)
                self.assertTrue(e.prompt.strip().endswith("."))
                for giveaway in ("print(", "console.log", "println", "printf"):
                    self.assertNotIn(giveaway, e.prompt)

    def test_no_two_exercises_on_a_page_are_the_same(self) -> None:
        for p in JSPLANETS_PAGES:
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
                        emit_jsplanets.solution(language, e.shape, e.args))

    def test_programs_are_short(self) -> None:
        """3-10 lines: a formula or a small array, not a project."""
        for _, e in NEW:
            lines = _answer(e).splitlines()
            with self.subTest(exercise=e.id):
                self.assertGreaterEqual(len(lines), 3)
                self.assertLessEqual(len(lines), 10)

    def test_the_pages_really_vary(self) -> None:
        """Each page mixes its variants, and yes-no answers go both ways."""
        for p in JSPLANETS_PAGES:
            with self.subTest(page=p.id):
                wants = {e.args["want"] for e in p.exercises}
                self.assertGreaterEqual(len(wants), 3)
        for page in ("js-planets-weight", "js-planets-filter"):
            said = {line for e in BY_ID[page].exercises
                    for line in _expect(e).split("\n")
                    if line in ("true", "false")}
            with self.subTest(page=page):
                self.assertEqual(said, {"true", "false"})
        # Sorting goes both ways, and reduce finds both ends.
        sort = {e.args["want"] for e in BY_ID["js-planets-sort"].exercises}
        self.assertLessEqual({"up", "down", "max", "min"}, sort)
        # Temperatures below zero keep their minus sign through toFixed.
        temps = {_expect(e)[0] == "-" for e in BY_ID["js-planets-units"].exercises
                 if e.args["want"] == "temp"}
        self.assertEqual(temps, {True, False})
        # Some synodic rows name the slower planet first, so Math.abs matters.
        firsts = {e.args["one"][1] < e.args["two"][1]
                  for e in BY_ID["js-planets-orbit"].exercises
                  if e.args["want"] == "synodic"}
        self.assertEqual(firsts, {True, False})
        # A remainder of zero seconds still prints, as 0 s.
        light = [_expect(e) for e in BY_ID["js-planets-light"].exercises]
        self.assertTrue(any(out.endswith(" 0 s") for out in light))

    def test_the_facts_agree_across_pages(self) -> None:
        c = content_jsplanets
        self.assertEqual(float(emit_jsplanets.EARTH_G), c.GRAVITY["Earth"])
        self.assertEqual(float(emit_jsplanets.EARTH_YEAR), c.YEAR["Earth"])
        self.assertEqual(float(emit_jsplanets.AU_MILLION_KM), c.DISTANCE["Earth"])
        # The AU table is the fact sheet's distance over 149.6, to 3 places.
        for body, d in c.DISTANCE.items():
            with self.subTest(body=body):
                self.assertEqual(c.AU[body], round(d / 149.6, 3))
        # The escape page writes the sheet's masses in e-notation: 6.42e23
        # is the same number as the sheet's 0.642 x 10^24.
        for _, e in NEW:
            if e.shape == "js_planets_escape" and "mass" in e.args:
                digits, power = e.args["mass"]
                with self.subTest(exercise=e.id):
                    self.assertAlmostEqual(
                        digits * 10 ** (power - 24) / c.MASS[e.args["body"]], 1)

    def test_the_oracle_refuses_bad_data(self) -> None:
        out = emit_jsplanets.expected_output
        with self.assertRaises(ValueError):  # 1.5 * 3.7 is 5.55, on an edge
            out("js_planets_weight",
                {"want": "newtons", "mass": 1.5, "body": "Mars", "g": 3.7})
        with self.assertRaises(ValueError):  # a tie: either could come first
            out("js_planets_sort",
                {"want": "up", "field": "gravity",
                 "items": (("Mercury", 3.7), ("Mars", 3.7), ("Earth", 9.8))})
        with self.assertRaises(ValueError):  # Earth's 24 hours is the limit
            out("js_planets_filter",
                {"want": "names", "field": "day", "op": ">", "limit": 24,
                 "items": (("Earth", 24), ("Mars", 24.7), ("Venus", 2802))})
        with self.assertRaises(ValueError):  # keeps them all: filter does nothing
            out("js_planets_filter",
                {"want": "count", "field": "au", "op": ">", "limit": 0.1,
                 "items": (("Mercury", 0.387), ("Venus", 0.723), ("Earth", 1))})
        with self.assertRaises(ValueError):  # day 8662 is a Jupiter birthday
            out("js_planets_age",
                {"want": "next", "days": 8662, "body": "Jupiter", "year": 4331})
        with self.assertRaises(ValueError):  # 1374 days is exactly two orbits
            out("js_planets_orbit",
                {"want": "angle", "body": "Mars", "year": 687, "days": 1374})
        with self.assertRaises(ValueError):  # over an hour: not min and s
            out("js_planets_light", {"want": "minsec", "km": 1432000000})
        with self.assertRaises(ValueError):  # Mercury overflows its column
            out("js_planets_table",
                {"want": "two", "field": "au", "digits": 2, "name_width": 6,
                 "width": 6, "items": (("Mercury", 0.387), ("Venus", 0.723),
                                       ("Earth", 1))})
        with self.assertRaises(ValueError):  # earthGravity would clash
            emit_jsplanets.solution(
                "javascript", "js_planets_weight",
                {"want": "scale", "reading": 60, "body": "Earth", "g": 9.8})

    @unittest.skipUnless(REGISTERED, "not registered in content.py yet")
    def test_registered_dispatch_agrees(self) -> None:
        from code_coach.workbook.complexity import for_shape

        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertEqual(e.expect, _expect(e))
                self.assertEqual(e.answer("javascript"), _answer(e))
                self.assertIsNone(e.answer("python"))
        for shape in emit_jsplanets.SHAPE_IDS:
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
