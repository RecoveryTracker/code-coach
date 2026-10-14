"""The "Data" Python pages (362-371).

Written to pass both before and after the pages are registered: the
reference programs and expected outputs are taken from emit_pydata directly,
so nothing here depends on the dispatch in emit.py or the workbook package.
Once registered, the checks that go through Exercise.expect and
Exercise.answer switch on as well.

The expected outputs are worked out with small models in Python (a tally, a
stable grouper, exact decimals and fractions, a calendar from day numbers,
a JSON writer and reader, a csv writer and reader), never by running the
programs; the run test is what proves python prints the same characters.
"""

from __future__ import annotations

import ast
import importlib
import inspect
import pkgutil
import re
import unittest

import code_coach.workbook as workbook
from code_coach.engine import run_code
from code_coach.workbook import Page, _value, matches, pages
from code_coach.workbook import emit_pydata
from code_coach.workbook.content_pydata import PYDATA_PAGES

NEW = [(p, e) for p in PYDATA_PAGES for e in p.exercises]
REGISTERED = any(p.id == PYDATA_PAGES[0].id for p in pages())
BY_ID = {p.id: p for p in PYDATA_PAGES}


def _expect(e) -> str:
    return emit_pydata.expected_output(e.shape, e.args, _value)


def _answer(e) -> str:
    code = emit_pydata.solution("python", e.shape, e.args)
    assert code is not None
    return code


def _others() -> list[Page]:
    """Every page that is not one of these, registered or not.

    Not the review pages: they are built from the pages above and replay
    their exercises on purpose, so once these are registered a review page
    carries every one of these shapes.
    """
    mine = {id(p) for p in PYDATA_PAGES}
    found = {id(p): p for p in pages() if id(p) not in mine and not p.id.startswith("review-")}
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


def _data_loop_depth(node, d: int = 0) -> int:
    """How deeply the program loops over data (the rule in test_workbook)."""

    def fixed(it) -> bool:
        if isinstance(it, (ast.Tuple, ast.List)):
            return True
        return (isinstance(it, ast.Call) and isinstance(it.func, ast.Name)
                and it.func.id == "range"
                and all(isinstance(a, ast.Constant) for a in it.args))

    best = d
    for child in ast.iter_child_nodes(node):
        step = 0
        if isinstance(child, (ast.For, ast.AsyncFor)):
            step = 0 if fixed(child.iter) else 1
        elif isinstance(child, ast.While):
            step = 1
        elif isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp,
                                ast.GeneratorExp)):
            step = sum(0 if fixed(g.iter) else 1 for g in child.generators)
        best = max(best, _data_loop_depth(child, d + step))
    return best


class ShapeTests(unittest.TestCase):
    def test_ten_pages_of_about_twenty(self) -> None:
        self.assertEqual(len(PYDATA_PAGES), 10)
        for p in PYDATA_PAGES:
            with self.subTest(page=p.id):
                self.assertTrue(p.id.startswith("py-data-"))
                self.assertTrue(p.name.startswith("Data: "))
                self.assertGreaterEqual(len(p.exercises), 18)
                self.assertLessEqual(len(p.exercises), 22)
                self.assertEqual(len({e.shape for e in p.exercises}), 1)
                self.assertEqual(p.languages, ("python",))
                self.assertEqual(p.tier, "intermediate")
                self.assertGreater(len(p.teaches), 20)
                self.assertGreater(len(p.example), 60)

    def test_every_shape_has_a_page_and_a_note(self) -> None:
        used = [p.exercises[0].shape for p in PYDATA_PAGES]
        self.assertEqual(used, list(emit_pydata.SHAPE_IDS))
        for shape in emit_pydata.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertTrue(shape.startswith("py_data_"))
                self.assertTrue(emit_pydata.handles(shape))
                self.assertIsNotNone(emit_pydata.for_shape(shape))

    def test_shapes_are_new(self) -> None:
        from code_coach.workbook.emit import all_shape_ids

        mine = set(emit_pydata.SHAPE_IDS)
        self.assertEqual(len(mine), len(emit_pydata.SHAPE_IDS))
        others = {e.shape for p in _others() for e in p.exercises}
        others |= set(all_shape_ids()) - mine
        self.assertFalse(mine & others)

    def test_ids_are_new(self) -> None:
        mine_pages = {p.id for p in PYDATA_PAGES}
        mine_ex = [e.id for _, e in NEW]
        self.assertEqual(len(mine_ex), len(set(mine_ex)))
        self.assertEqual(len(mine_pages), len(PYDATA_PAGES))
        for p in PYDATA_PAGES:
            for i, e in enumerate(p.exercises):
                self.assertEqual(e.id, f"{p.id}-{i + 1:02d}")
        others = _others()
        self.assertFalse(mine_pages & {p.id for p in others})
        self.assertFalse(
            set(mine_ex) & {e.id for p in others for e in p.exercises})

    def test_numbers_are_consecutive_and_follow_the_scripting_pages(self) -> None:
        numbers = [p.number for p in PYDATA_PAGES]
        self.assertEqual(numbers, list(range(numbers[0], numbers[0] + 10)))
        self.assertGreater(numbers[0], 351)
        # No other Python page uses these numbers, registered or not. The
        # review pages are left out because they are numbered from whatever
        # the last page is, so they move up.
        mine = {p.id for p in PYDATA_PAGES}
        theirs = {p.number for p in pages("python")
                  if p.id not in mine and p.tier != "review"}
        theirs |= {p.number for p in _others()
                   if p.applies_to("python") and p.tier != "review"}
        self.assertFalse(theirs & set(numbers))

    def test_prompts_are_sentences_without_syntax(self) -> None:
        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertGreater(len(e.prompt), 20)
                self.assertTrue(e.prompt.strip().endswith("."))
                for giveaway in ("print(", "console.log", "println", "printf"):
                    self.assertNotIn(giveaway, e.prompt)

    def test_no_two_exercises_on_a_page_are_the_same(self) -> None:
        for p in PYDATA_PAGES:
            with self.subTest(page=p.id):
                asked = [(e.prompt, _expect(e)) for e in p.exercises]
                self.assertEqual(len(asked), len(set(asked)))
                self.assertEqual(
                    len({e.prompt for e in p.exercises}), len(p.exercises))
                self.assertEqual(
                    len({repr(sorted(e.args.items(), key=str)) for e in p.exercises}),
                    len(p.exercises))

    def test_every_exercise_prints_something(self) -> None:
        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertTrue(_expect(e).strip())

    def test_other_languages_get_no_answer(self) -> None:
        for _, e in NEW:
            for language in ("javascript", "typescript", "dart", "rust"):
                with self.subTest(exercise=e.id, language=language):
                    self.assertIsNone(
                        emit_pydata.solution(language, e.shape, e.args))
            self.assertIsNotNone(emit_pydata.solution("python", e.shape, e.args))

    def test_programs_are_short(self) -> None:
        """3-10 lines: a small program, not a project."""
        for _, e in NEW:
            lines = _answer(e).splitlines()
            with self.subTest(exercise=e.id):
                self.assertGreaterEqual(len(lines), 3)
                self.assertLessEqual(len(lines), emit_pydata.LIMIT)

    def test_the_pages_really_vary(self) -> None:
        """Each page mixes its variants, and the traps go both ways."""
        for p in PYDATA_PAGES:
            with self.subTest(page=p.id):
                wants = {e.args["want"] for e in p.exercises}
                self.assertGreaterEqual(len(wants), 3)

        def outs(page, **match):
            return [_expect(e) for e in BY_ID[page].exercises
                    if all(e.args.get(k) == v for k, v in match.items())]

        # Counter: a tie is listed in first-seen order; an anagram is and is
        # not; subtracting leaves a zero and a negative; a missing word is 0.
        self.assertIn("pen 2\nink 2", outs("py-data-counter", want="top"))
        self.assertEqual(set(outs("py-data-counter", want="anagram")), {"True", "False"})
        sub = outs("py-data-counter", want="subtract")
        self.assertTrue(all(", 0)" in s and "-1)" in s for s in sub))
        self.assertTrue(all(s.startswith("0\n") for s in outs("py-data-counter", want="missing")))
        # Grouping: without a sort a key comes back as a second group.
        for o in outs("py-data-grouping", want="unsorted"):
            keys = [line.split(" ")[0] for line in o.split("\n")]
            self.assertLess(len(set(keys)), len(keys))
        self.assertTrue(any("." in o for o in outs("py-data-grouping", want="averages")))
        # Records: ties on the first sort key, a stable second key.
        self.assertGreaterEqual(len(outs("py-data-records", want="sort2")), 3)
        # Statistics: a median of an even count lands between two values, a
        # multimode is a list, outliers can be none.
        self.assertIn("10.5", outs("py-data-stats", want="median"))
        self.assertTrue(all(o.startswith("[") for o in outs("py-data-stats", want="multimode")))
        self.assertEqual({o == "none" for o in outs("py-data-stats", want="outliers")},
                         {True, False})
        # csv: a string compare picks a smaller number than the numbers do.
        for e in BY_ID["py-data-csv"].exercises:
            if e.args["want"] == "string_max":
                with self.subTest(exercise=e.id):
                    i = e.args["rows"][0].index(e.args["col"])
                    values = [r[i] for r in e.args["rows"][1:]]
                    self.assertLess(int(_expect(e)), max(int(v) for v in values))
        self.assertTrue(any(o.startswith("2\n") for o in outs("py-data-csv", want="quoted")))
        # JSON: some text is bad and some is not; a round trip can and cannot
        # be equal.
        self.assertEqual({o == "bad" for o in outs("py-data-json", want="valid")},
                         {True, False})
        self.assertEqual({o.split("\n")[-1] for o in outs("py-data-json", want="round_trip")},
                         {"True", "False"})
        # Dates: more than one weekday, and a timedelta with and without days.
        self.assertGreaterEqual(len(set(outs("py-data-dates", want="weekday"))), 2)
        deltas = outs("py-data-dates", want="delta")
        self.assertTrue(any("day" in d for d in deltas) and any("day" not in d for d in deltas))
        self.assertIn("2024-02-29", outs("py-data-dates", want="month_end"))
        # Money: a tie rounds up and a share can leave a negative remainder.
        self.assertTrue(any(" -" in o for o in outs("py-data-money", want="split")))
        self.assertEqual({o.split("\n")[0] for o in outs("py-data-money", want="same_value")},
                         {"True", "False"})
        # Grid: the aliased rows are all the same, the built rows are not.
        for o in outs("py-data-grid", want="alias"):
            rows = o[2:-2].split("], [")
            self.assertEqual(len(set(rows)), 1)
        for o in outs("py-data-grid", want="set_cell"):
            rows = o[2:-2].split("], [")
            self.assertEqual(len(set(rows)), 2)
        # Text: a table can be aligned three ways.
        aligns = {e.args["align"][0] for e in BY_ID["py-data-text"].exercises
                  if e.args["want"] == "table"}
        self.assertEqual(aligns, {"<", "^"})

    def test_csv_programs_say_what_the_line_ends_with(self) -> None:
        """A csv writer's default is \\r\\n, which is not what the check sees."""
        for _, e in NEW:
            code = _answer(e)
            if "csv.writer(" in code or "csv.DictWriter(" in code:
                with self.subTest(exercise=e.id):
                    self.assertIn('lineterminator="\\n"', code)

    def test_dates_are_fixed_dates(self) -> None:
        for _, e in NEW:
            code = _answer(e)
            with self.subTest(exercise=e.id):
                for today in ("today(", "now(", "utcnow(", "time.time", "fromtimestamp"):
                    self.assertNotIn(today, code)

    def test_nothing_is_random_or_read_from_disk(self) -> None:
        for _, e in NEW:
            code = _answer(e)
            with self.subTest(exercise=e.id):
                for word in ("random", "open(", "read_text", "write_text", "input(",
                             "import os", "import sys", "tempfile"):
                    self.assertNotIn(word, code)

    def test_rounded_decimals_are_not_on_a_tie(self) -> None:
        """A fixed-decimals print is held away from ties, which binary
        floating point could round either way."""
        for _, e in NEW:
            code = _answer(e)
            if re.search(r":\.\d+f", code):
                with self.subTest(exercise=e.id):
                    self.assertTrue(_expect(e))  # the oracle refused every tie

    def test_the_oracle_is_a_model_not_the_library(self) -> None:
        """The module that works out the answers imports none of the
        libraries the answers use, so it cannot agree with them by being
        them."""
        modules = {name for name, value in vars(emit_pydata).items()
                   if inspect.ismodule(value)}
        self.assertEqual(modules, {"re"})
        source = inspect.getsource(emit_pydata)
        for library in ("json", "csv", "statistics", "collections", "itertools",
                        "datetime", "decimal", "fractions", "math", "calendar",
                        "io", "zip"):
            self.assertNotRegex(source, rf"(?m)^\s*(import|from)\s+{library}\b")

    def test_complexity_notes_do_not_contradict_the_code(self) -> None:
        """The rule in test_workbook, held to every program rather than the
        first of each shape: constant means no loop over data, linear means
        no loop inside a loop."""
        for _, e in NEW:
            note = emit_pydata.for_shape(e.shape)
            depth = _data_loop_depth(ast.parse(_answer(e)))
            with self.subTest(exercise=e.id, label=note.label):
                if note.label == "O(1)":
                    self.assertEqual(depth, 0)
                elif note.label == "O(n)":
                    self.assertLess(depth, 2)
                elif note.label.startswith("O(n²)"):
                    self.assertGreaterEqual(depth, 2)

    def test_the_oracle_refuses_bad_data(self) -> None:
        out = emit_pydata.expected_output

        def refuses(why: str, shape: str, **args) -> None:
            with self.subTest(why=why):
                with self.assertRaises(ValueError):
                    out(shape, args)

        refuses("a tie for the rarest word", "py_data_counter",
                want="least", words=["ant", "bee", "cow", "dog", "ant", "bee"])
        refuses("a word that is there", "py_data_counter",
                want="missing", words=["ant", "bee", "ant", "cow"], word="ant")
        refuses("capitals change nothing", "py_data_counter",
                want="normalised", text="the cat the dog the", word="the")
        refuses("no word repeats", "py_data_counter",
                want="best", words=["ant", "bee", "cow", "dog"])
        refuses("an anagram of itself", "py_data_counter",
                want="anagram", a="listen", b="listen")
        refuses("a sale that sells out nothing", "py_data_counter",
                want="subtract", words=["ant", "ant", "bee", "cow"], sold=["ant", "dog"])
        refuses("no key comes back", "py_data_group",
                want="unsorted", rows=[("a", 1), ("b", 2), ("c", 3), ("d", 4)])
        refuses("an average on a rounding tie", "py_data_group",
                want="averages", rows=[("x", 2), ("x", 2), ("x", 2), ("x", 3), ("y", 1)])
        refuses("a team that is there", "py_data_group",
                want="peek", team="red",
                pairs=[("ada", "red"), ("sam", "blue"), ("kim", "red")] * 2)
        refuses("a quote in a word", "py_data_counter",
                want="count", words=["it's", "a", "b", "a"], word="a")
        refuses("a tie in the sort key", "py_data_records", want="sort1",
                rows=[{"name": "Ada", "dept": "ops", "pay": 5},
                      {"name": "Sam", "dept": "ops", "pay": 5},
                      {"name": "Kim", "dept": "dev", "pay": 7},
                      {"name": "Lee", "dept": "dev", "pay": 9}],
                key="pay", reverse=False)
        refuses("a limit that keeps everything", "py_data_records", want="filter",
                rows=[{"name": "Ada", "dept": "ops", "pay": 5},
                      {"name": "Sam", "dept": "ops", "pay": 6},
                      {"name": "Kim", "dept": "dev", "pay": 7},
                      {"name": "Lee", "dept": "dev", "pay": 9}],
                key="pay", limit=1)
        refuses("a mean on a rounding tie", "py_data_stats",
                want="mean", data=[1, 1, 1, 1, 1, 1, 1, 2], digits=2)
        refuses("two modes", "py_data_stats", want="mode", data=[1, 1, 2, 2, 3])
        refuses("a value exactly on the line", "py_data_stats",
                want="above", data=[1, 2, 3])
        refuses("a median to two decimals", "py_data_stats",
                want="median", data=[1, 2, 3, 4], digits=2)
        refuses("a string max that is the number max", "py_data_csv",
                want="string_max", col="n",
                rows=[["id", "n"], ["a", "1"], ["b", "2"], ["c", "3"]])
        refuses("a field that is not plain", "py_data_csv", want="fieldnames",
                rows=[["a", "b"], ["1", "it's"], ["2", "x"], ["3", "y"]])
        refuses("a quoted row with nothing to quote", "py_data_csv", want="quoted",
                row=1, col=1, rows=[["a", "b"], ["1", "x"], ["2", "y"], ["3", "z"]])
        refuses("a float in the JSON", "py_data_json", want="valid", text="[1.5]")
        refuses("keys already sorted", "py_data_json",
                want="dumps_sorted", obj={"a": 1, "b": 2, "c": 3})
        refuses("a key that is not new", "py_data_json", want="update_dump",
                obj={"a": 1, "b": 2}, key="a", step=1, new="b", value=True)
        refuses("a move of no days", "py_data_dates",
                want="add", start=(2026, 1, 31), n=0)
        refuses("a date that is not there", "py_data_dates",
                want="diff", start=(2026, 2, 30), end=(2026, 4, 1))
        refuses("a birthday that has not happened", "py_data_dates",
                want="age", born=(2026, 3, 1), on=(2026, 2, 1))
        refuses("a format that is not read back", "py_data_dates", want="parse",
                fmt="%A", start=(2026, 3, 5), end=(2026, 4, 20))
        refuses("a tax that needs no rounding", "py_data_money", want="tax",
                prices=["1.00", "2.00", "3.00"], rate="0.5")
        refuses("a bill that splits evenly", "py_data_money",
                want="split", total="100.00", people=4)
        refuses("one way of writing it", "py_data_money",
                want="same_value", x="2.5", y="2.5")
        refuses("a fraction over zero", "py_data_money",
                want="fraction_ops", x="1/2", y="0", op="/")
        refuses("a square grid cannot show a turn", "py_data_grid",
                want="rotate", rows=[[1, 2], [3, 4]])
        refuses("a ragged grid", "py_data_grid",
                want="transpose", rows=[[1, 2, 3], [4, 5]])
        refuses("a tie for the biggest cell", "py_data_grid",
                want="biggest", rows=[[9, 2], [3, 9]])
        refuses("a name wider than its column", "py_data_text", want="table",
                lines=["ada,1", "kim,2", "sam,3"], widths=[3, 5], align=["<", ">"])
        refuses("a tie for the longest line", "py_data_text",
                want="longest", lines=["abc", "def", "g"])
        refuses("settings that are already tidy", "py_data_text", want="settings",
                lines=["a=1", "b=2", "c=3"])
        refuses("a level that is every line", "py_data_text", want="levels",
                lines=["2026-01-01 INFO a", "2026-01-01 INFO b", "2026-01-02 INFO c"],
                level="INFO")
        with self.assertRaises(KeyError):
            out("py_data_nothing", {})

    @unittest.skipUnless(REGISTERED, "not registered in content.py yet")
    def test_registered_dispatch_agrees(self) -> None:
        from code_coach.workbook.complexity import for_shape

        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertEqual(e.expect, _expect(e))
                self.assertEqual(e.answer("python"), _answer(e))
                self.assertIsNone(e.answer("javascript"))
        for shape in emit_pydata.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertIsNotNone(for_shape(shape))


class ReferenceRunTests(unittest.TestCase):
    TIMED_OUT = 124

    def test_every_reference_answer_prints_what_it_should(self) -> None:
        for _, e in NEW:
            code = _answer(e)
            with self.subTest(exercise=e.id):
                stdout, stderr, code_ = run_code(code, language="python")
                if code_ == self.TIMED_OUT:
                    stdout, stderr, code_ = run_code(code, language="python")
                self.assertEqual(code_, 0, (stderr or stdout)[:400])
                self.assertTrue(
                    matches(stdout, _expect(e)),
                    f"printed {stdout!r}, wanted {_expect(e)!r}\n{code}")


if __name__ == "__main__":
    unittest.main()
