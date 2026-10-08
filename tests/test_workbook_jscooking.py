"""The "Cooking" JavaScript pages (258-267).

Written to pass both before and after the pages are registered: the
reference programs and expected outputs are taken from emit_jscooking
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
from code_coach.workbook import content_jscooking, emit_jscooking
from code_coach.workbook.content_jscooking import JSCOOKING_PAGES

NEW = [(p, e) for p in JSCOOKING_PAGES for e in p.exercises]
REGISTERED = any(p.id == JSCOOKING_PAGES[0].id for p in pages())
BY_ID = {p.id: p for p in JSCOOKING_PAGES}


def _expect(e) -> str:
    return emit_jscooking.expected_output(e.shape, e.args, _value)


def _answer(e) -> str:
    code = emit_jscooking.solution("javascript", e.shape, e.args)
    assert code is not None
    return code


def _others() -> list[Page]:
    """Every page that is not one of these, registered or not.

    A set written alongside this one may not be registered yet, so every
    content module's *_PAGES tuple is read as well as pages(). A module
    that will not import is skipped: it is that set's own test's business.
    """
    mine = {id(p) for p in JSCOOKING_PAGES}
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
        self.assertEqual(len(JSCOOKING_PAGES), 10)
        for p in JSCOOKING_PAGES:
            with self.subTest(page=p.id):
                self.assertTrue(p.id.startswith("js-cook-"))
                self.assertTrue(p.name.startswith("Cooking: "))
                self.assertGreaterEqual(len(p.exercises), 18)
                self.assertLessEqual(len(p.exercises), 22)
                self.assertEqual(len({e.shape for e in p.exercises}), 1)
                self.assertEqual(p.languages, ("javascript",))
                self.assertEqual(p.tier, "intermediate")
                self.assertGreater(len(p.teaches), 20)
                self.assertGreater(len(p.example), 60)

    def test_every_shape_has_a_page_and_a_note(self) -> None:
        used = [p.exercises[0].shape for p in JSCOOKING_PAGES]
        self.assertEqual(used, list(emit_jscooking.SHAPE_IDS))
        for shape in emit_jscooking.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertTrue(shape.startswith("js_cook_"))
                self.assertTrue(emit_jscooking.handles(shape))
                self.assertIsNotNone(emit_jscooking.for_shape(shape))

    def test_shapes_are_new(self) -> None:
        from code_coach.workbook.emit import all_shape_ids

        mine = set(emit_jscooking.SHAPE_IDS)
        self.assertEqual(len(mine), len(emit_jscooking.SHAPE_IDS))
        others = {e.shape for p in _others() for e in p.exercises}
        others |= set(all_shape_ids()) - mine
        self.assertFalse(mine & others)

    def test_ids_are_new(self) -> None:
        mine_pages = {p.id for p in JSCOOKING_PAGES}
        mine_ex = [e.id for _, e in NEW]
        self.assertEqual(len(mine_ex), len(set(mine_ex)))
        self.assertEqual(len(mine_pages), len(JSCOOKING_PAGES))
        others = _others()
        self.assertFalse(mine_pages & {p.id for p in others})
        self.assertFalse(
            set(mine_ex) & {e.id for p in others for e in p.exercises})

    def test_numbers_are_consecutive_and_unused(self) -> None:
        numbers = [p.number for p in JSCOOKING_PAGES]
        self.assertEqual(numbers, list(range(258, 268)))
        mine = {p.id for p in JSCOOKING_PAGES}
        # No other JavaScript page uses these numbers, registered or not;
        # sets on either side may exist or not.
        theirs = {p.number for p in pages("javascript") if p.id not in mine}
        theirs |= {p.number for p in _others() if "javascript" in p.languages}
        self.assertFalse(theirs & set(numbers))

    def test_prompts_are_sentences_without_syntax(self) -> None:
        for p, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertGreater(len(e.prompt), 20)
                self.assertTrue(e.prompt.strip().endswith("."))
                for giveaway in ("print(", "console.log", "println", "printf"):
                    self.assertNotIn(giveaway, e.prompt)

    def test_no_two_exercises_on_a_page_are_the_same(self) -> None:
        for p in JSCOOKING_PAGES:
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
                        emit_jscooking.solution(language, e.shape, e.args))

    def test_programs_are_short(self) -> None:
        """3-10 lines: a formula or a small array, not a project."""
        for _, e in NEW:
            lines = _answer(e).splitlines()
            with self.subTest(exercise=e.id):
                self.assertGreaterEqual(len(lines), 3)
                self.assertLessEqual(len(lines), 10)

    def test_the_pages_really_vary(self) -> None:
        """Each page mixes its variants, and yes-no answers go both ways."""
        for p in JSCOOKING_PAGES:
            with self.subTest(page=p.id):
                wants = {e.args["want"] for e in p.exercises}
                self.assertGreaterEqual(len(wants), 3)
        for page in ("js-cook-time", "js-cook-filter", "js-cook-cost"):
            said = {line for e in BY_ID[page].exercises
                    for line in _expect(e).split("\n")
                    if line in ("true", "false")}
            with self.subTest(page=page):
                self.assertEqual(said, {"true", "false"})
        # Temperatures below zero keep their minus sign through toFixed.
        temps = {_expect(e)[0] == "-" for e in BY_ID["js-cook-temp"].exercises
                 if e.args["want"] in ("c2f", "f2c")}
        self.assertEqual(temps, {True, False})
        # A remainder of zero minutes still prints, as 0 min.
        times = [_expect(e) for e in BY_ID["js-cook-time"].exercises]
        self.assertTrue(any(out.endswith(" 0 min") for out in times))
        # Both rounding ways show up: a scaled amount that is whole and one
        # that is not, and eggs rounded up always go up.
        scale = BY_ID["js-cook-scale"].exercises
        for e in scale:
            if e.args["want"] == "whole":
                exact = e.args["qty"] * e.args["wanted"] / e.args["orig"]
                self.assertGreater(int(_expect(e)), exact, e.id)
        # Recipes sometimes keep one of the vegetarian lists and some drop it.
        veg = {e.args["op"] for e in BY_ID["js-cook-filter"].exercises
               if e.args["field"] == "veg"}
        self.assertEqual(veg, {"is", "not"})

    def test_the_timeline_wraps_past_midnight(self) -> None:
        wraps = {"start": 0, "steps": 0, "ready": 0}
        stays = {"start": 0, "steps": 0, "ready": 0}
        for e in BY_ID["js-cook-timeline"].exercises:
            a = e.args
            if a["want"] == "ready":
                end = a["begin"][0] * 60 + a["begin"][1] + a["hours"] * 60 + a["mins"]
                key = "ready"
                over = end >= 1440
            else:
                begin = (a["serve"][0] * 60 + a["serve"][1]
                         - a["prep"] - a["cook"])
                key = a["want"]
                over = begin < 0
            (wraps if over else stays)[key] += 1
        for key in wraps:
            with self.subTest(want=key):
                self.assertGreaterEqual(wraps[key], 1)
                self.assertGreaterEqual(stays[key], 1)
        # A single-digit hour or minute is padded: 07:05 and 00:10 appear.
        said = {line for e in BY_ID["js-cook-timeline"].exercises
                for line in _expect(e).split("\n")}
        self.assertTrue(any(s.startswith("0") for s in said))
        self.assertTrue(any(s[3] == "0" for s in said))

    def test_the_facts_agree_across_pages(self) -> None:
        c, m = content_jscooking, emit_jscooking
        # The gas table is stated in every prompt that needs it, in order.
        for e in BY_ID["js-cook-temp"].exercises:
            if e.args["want"] in ("gas2c", "gas2f", "c2gas"):
                with self.subTest(exercise=e.id):
                    self.assertIn(c._GAS_TEXT, e.prompt)
        self.assertEqual(sorted(m.GAS), list(range(1, 10)))
        self.assertEqual(list(m.GAS.values()), sorted(m.GAS.values()))
        # Every unit factor is stated in the prompts that use it.
        for e in BY_ID["js-cook-units"].exercises:
            with self.subTest(exercise=e.id):
                if e.args["want"] in ("oz_g", "g_oz"):
                    self.assertIn(f"1 oz is {m.OZ_G} g", e.prompt)
                if e.args["want"] in ("to_ml", "from_ml", "cup_tbsp"):
                    unit = e.args.get("unit", "cup")
                    ml = {"cup": m.CUP_ML, "tbsp": m.TBSP_ML, "tsp": m.TSP_ML}
                    self.assertIn(f"is {ml[unit]} ml", e.prompt)
        # The nutrition prompts say the numbers the program uses.
        for e in BY_ID["js-cook-nutrition"].exercises:
            with self.subTest(exercise=e.id):
                if e.args["want"] == "dv":
                    self.assertIn(f"{m.DAILY_KCAL} kcal", e.prompt)
                if e.args["want"] == "dvof":
                    self.assertIn(f"{e.args['dv']} ", e.prompt)
        # A recipe table and the arrays in the prompts agree.
        for e in BY_ID["js-cook-filter"].exercises:
            slot = c.RECIPE_FIELDS[e.args["field"]][0]
            for name, value in e.args["items"]:
                with self.subTest(exercise=e.id, name=name):
                    self.assertEqual(c.RECIPES[name][slot], value)
        for e in BY_ID["js-cook-card"].exercises:
            if e.args["want"] == "three":
                continue
            slot = c.CARD_FIELDS[e.args["field"]][0]
            for name, value in e.args["items"]:
                with self.subTest(exercise=e.id, name=name):
                    self.assertEqual(c.INGREDIENTS[name][slot], value)
        # Prices in the cost prompts are the prices the program multiplies.
        for e in BY_ID["js-cook-cost"].exercises:
            for item in e.args.get("items", ()):
                with self.subTest(exercise=e.id, item=item[0]):
                    self.assertIn(f"${item[2]:.2f}", e.prompt)

    def test_the_oracle_refuses_bad_data(self) -> None:
        out = emit_jscooking.expected_output
        with self.assertRaises(ValueError):  # 45 * 3 / 4 is 33.75, on an edge
            out("js_cook_scale",
                {"want": "amount", "thing": "honey", "qty": 45, "orig": 4,
                 "wanted": 3})
        with self.assertRaises(ValueError):  # 2 * 6 / 4 is 3: nothing to round up
            out("js_cook_scale",
                {"want": "whole", "thing": "eggs", "qty": 2, "orig": 4,
                 "wanted": 6})
        with self.assertRaises(ValueError):  # a third of a cup is not exact
            out("js_cook_units", {"want": "to_ml", "unit": "cup", "qty": 0.3})
        with self.assertRaises(ValueError):  # 210 °C is not a gas mark
            out("js_cook_temp", {"want": "c2gas", "c": 210})
        with self.assertRaises(ValueError):  # 45 * 1.8 + 20 is 101, on a whole
            out("js_cook_time",
                {"want": "min", "base": 20, "per": 45, "kg": 1.8})
        with self.assertRaises(ValueError):  # under an hour: not H h M min
            out("js_cook_time", {"want": "hm", "base": 10, "per": 21, "kg": 1.5})
        with self.assertRaises(ValueError):  # a tie: either could come first
            out("js_cook_time",
                {"want": "longer", "one": ("ham", 40, 32, 3.7),
                 "two": ("pig", 40, 32, 3.7)})
        with self.assertRaises(ValueError):  # Pancakes serves exactly 4
            out("js_cook_filter",
                {"want": "names", "field": "serves", "op": ">", "limit": 4,
                 "items": (("Pancakes", 4), ("Lasagne", 8), ("Salad", 2))})
        with self.assertRaises(ValueError):  # keeps them all: filter does nothing
            out("js_cook_filter",
                {"want": "count", "field": "minutes", "op": ">", "limit": 5,
                 "items": (("Pancakes", 20), ("Lasagne", 90), ("Salad", 15))})
        with self.assertRaises(ValueError):  # nothing repeated: nothing to merge
            out("js_cook_shop",
                {"want": "sorted",
                 "lines": (("eggs", 1), ("milk", 1), ("flour", 1))})
        with self.assertRaises(ValueError):  # a tie for the most packs
            out("js_cook_shop",
                {"want": "most",
                 "lines": (("eggs", 2), ("milk", 2), ("eggs", 1), ("milk", 1),
                           ("flour", 1))})
        with self.assertRaises(ValueError):  # 0.765 is exactly halfway
            out("js_cook_cost",
                {"want": "serving", "servings": 4,
                 "items": (("rice", 0.3, 2.2), ("onions", 2, 0.4),
                           ("tomatoes", 0.5, 3.2))})
        with self.assertRaises(ValueError):  # 423.75 is exactly halfway
            out("js_cook_nutrition",
                {"want": "per", "protein": 90, "carbs": 210, "fat": 55,
                 "servings": 4})
        with self.assertRaises(ValueError):  # 250 / 2000 * 100 is 12.5
            out("js_cook_nutrition",
                {"want": "dvof", "nutrient": "sodium", "amount": 250, "dv": 2000})
        with self.assertRaises(ValueError):  # 25:00 is not a time of day
            out("js_cook_timeline",
                {"want": "ready", "begin": (25, 0), "hours": 1, "mins": 0})
        with self.assertRaises(ValueError):  # Cheese overflows its column
            out("js_cook_card",
                {"want": "two", "field": "price", "digits": 2, "name_width": 6,
                 "width": 6, "items": (("Cheese", 3.25), ("Flour", 0.4),
                                       ("Sugar", 0.55))})
        with self.assertRaises(ValueError):  # the two names would clash
            emit_jscooking.solution(
                "javascript", "js_cook_scale",
                {"want": "amount", "thing": "wanted", "qty": 100, "orig": 4,
                 "wanted": 6})

    @unittest.skipUnless(REGISTERED, "not registered in content.py yet")
    def test_registered_dispatch_agrees(self) -> None:
        from code_coach.workbook.complexity import for_shape

        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertEqual(e.expect, _expect(e))
                self.assertEqual(e.answer("javascript"), _answer(e))
                self.assertIsNone(e.answer("python"))
        for shape in emit_jscooking.SHAPE_IDS:
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
