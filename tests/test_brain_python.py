"""Brain Drills in Python: every answer held to the real interpreter.

The Python templates work out their answers by modelling Python by hand
(see code_coach/brain/pythonic.py); here the real interpreter is the
oracle. Every template, over forty seeds, is run - Quick Eval through
print(), Truthy or Falsy through bool(), loop counts and final values by
running the code, Bracket Check and Syntax Snap through compile() - and
must agree with the model. Code age is kept per language, so the history
tests check that Python rounds and JavaScript rounds don't mix.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from datetime import date

from code_coach import brain
from code_coach.brain import ACTIVITIES, ACTIVITIES_BY_ID, CHECK, make_round, pythonic

SEEDS = range(40)

#: Runs every (how, code) case in a fresh namespace of the real interpreter.
DRIVER = r'''
import ast, contextlib, io, json, sys

def run(how, code):
    try:
        if how == "print":
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                exec("print(" + code + ")", {})
            return buf.getvalue().rstrip("\n")
        if how == "bool":
            return "truthy" if eval(code, {}) else "falsy"
        if how == "run":
            body = ast.parse(code).body
            ns = {}
            exec(compile(ast.Module(body[:-1], []), "<s>", "exec"), ns)
            return str(eval(compile(ast.Expression(body[-1].value), "<s>", "eval"), ns))
        if how == "syntax":
            compile(code, "<s>", "exec")
            return "valid"
    except SyntaxError as e:
        if how == "syntax":
            return "invalid"
        return "ERROR " + repr(e)
    except Exception as e:
        return "ERROR " + repr(e)

cases = json.loads(sys.stdin.read())
sys.stdout.write(json.dumps([run(h, c) for h, c in cases]))
'''


def py_values(cases: list[tuple[str, str]]) -> list[str]:
    """Run each (how, code) in the real Python; how is print, bool, run or syntax."""
    done = subprocess.run([sys.executable, "-W", "ignore", "-c", DRIVER], input=json.dumps(cases),
                          capture_output=True, text=True, encoding="utf-8", timeout=180)
    if done.returncode != 0:
        raise AssertionError(done.stderr)
    return json.loads(done.stdout)


def _rounds(activity_id: str):
    for seed in SEEDS:
        yield from make_round(activity_id, seed, "python")


class OracleTests(unittest.TestCase):
    def check(self, activity_id: str, how: str, code_of) -> None:
        items = list({i.prompt + i.check: i for i in _rounds(activity_id)}.values())
        self.assertGreater(len(items), 10)
        got = py_values([(how, code_of(i)) for i in items])
        for item, value in zip(items, got):
            with self.subTest(prompt=item.prompt):
                self.assertEqual(value, item.answer)

    def test_quick_eval_prints_what_python_prints(self) -> None:
        self.check("eval", "print", lambda i: i.prompt)

    def test_truthy_or_falsy_is_what_bool_says(self) -> None:
        self.check("truthy", "bool", lambda i: i.check)

    def test_loop_counts_are_what_the_loops_do(self) -> None:
        self.check("loops", "run", lambda i: i.check)

    def test_final_values_are_what_the_code_leaves(self) -> None:
        self.check("trace", "run", lambda i: i.check)

    def test_variable_recall_matches_what_the_lines_assign(self) -> None:
        items = list({i.prompt + i.show: i for i in _rounds("recall")}.values())
        got = py_values([("run", i.show + "\n" + i.prompt.rstrip("?")) for i in items])
        for item, value in zip(items, got):
            with self.subTest(prompt=item.prompt, show=item.show):
                self.assertEqual(value, item.answer)

    def test_bracket_check_agrees_with_the_compiler(self) -> None:
        items = list({i.prompt: i for i in _rounds("brackets")}.values())
        got = py_values([("syntax", i.prompt) for i in items])
        for item, value in zip(items, got):
            with self.subTest(text=item.prompt):
                self.assertEqual(value == "valid", item.answer == "yes")

    def test_syntax_snap_agrees_with_the_compiler(self) -> None:
        lines = [(line, "valid" if ok else "invalid") for line, ok, _why in pythonic.SYNTAX]
        got = py_values([("syntax", line) for line, _ in lines])
        for (line, want), value in zip(lines, got):
            with self.subTest(line=line):
                self.assertEqual(value, want)

    def test_truthy_table_agrees_with_bool(self) -> None:
        got = py_values([("bool", value) for value, _ok, _why in pythonic.TRUTHY])
        for (value, ok, _why), said in zip(pythonic.TRUTHY, got):
            with self.subTest(value=value):
                self.assertEqual(said, "truthy" if ok else "falsy")

    def test_the_engine_runs_a_round_the_same_way(self) -> None:
        # The app's own runner (code_coach.engine.run_code, language python)
        # agrees on a handful of Quick Eval items, printed one per line.
        from code_coach.engine import run_code

        items = [i for i in list(_rounds("eval"))[:12] if "\n" not in i.answer]
        code = "\n".join(f"print({i.prompt})" for i in items)
        out, _err, status = run_code(code, language="python")
        self.assertEqual(status, 0)
        self.assertEqual(out.strip().splitlines(), [i.answer for i in items])


class ActivityTests(unittest.TestCase):
    def test_every_activity_makes_a_full_round_of_its_kind(self) -> None:
        for activity in ACTIVITIES:
            with self.subTest(activity=activity.id):
                items = make_round(activity.id, 1, "python")
                self.assertEqual(len(items), activity.count)
                if activity.kind == "pick":
                    self.assertTrue(all(i.answer in activity.choices for i in items))
                    answers = {i.answer for s in range(10) for i in make_round(activity.id, s, "python")}
                    self.assertEqual(answers, set(activity.choices))

    def test_a_seed_gives_the_same_round(self) -> None:
        for activity in ACTIVITIES:
            self.assertEqual(make_round(activity.id, 9, "python"), make_round(activity.id, 9, "python"))

    def test_python_semantics_differ_where_the_languages_differ(self) -> None:
        # The same expression, answered by each language's own rules: "/"
        # gives 8 in JavaScript and 8.0 in Python.
        js = {i.prompt: i.answer for s in SEEDS for i in make_round("eval", s)}
        py = {i.prompt: i.answer for s in SEEDS for i in make_round("eval", s, "python")}
        self.assertTrue(any(p in js and js[p] != a for p, a in py.items()))

    def test_nothing_in_a_python_round_is_javascript(self) -> None:
        banned = ("console.log", "let ", "const ", "===", "typeof", "Math.", "=>", "undefined", "null", ";")
        for activity in ACTIVITIES:
            if activity.id == "syntax":  # its invalid lines are deliberately other languages
                continue
            for item in _rounds(activity.id):
                with self.subTest(prompt=item.prompt):
                    self.assertFalse(any(b in item.prompt + item.show for b in banned))

    def test_every_quick_eval_template_turns_up(self) -> None:
        # The python templates are a long if-chain; make sure none is unreachable.
        prompts = [i.prompt for i in _rounds("eval")]
        for marker in ("**", "//", "-", "% ", "/ 2", " / ", "[::-1]", "__name__", "bool(", "round(", " in ",
                       ".upper()", "True +", " < ", "str(", "len("):
            self.assertTrue(any(marker in p for p in prompts), marker)

    def test_bracket_answers_agree_with_another_way_of_checking(self) -> None:
        def by_removal(text: str) -> bool:
            text = "".join(ch for ch in text if ch in "()[]{}")
            while any(p in text for p in ("()", "[]", "{}")):
                for p in ("()", "[]", "{}"):
                    text = text.replace(p, "")
            return text == ""

        seen = set()
        for item in _rounds("brackets"):
            seen.add(item.answer)
            with self.subTest(text=item.prompt):
                self.assertEqual(item.answer == "yes", by_removal(item.prompt))
        self.assertEqual(seen, {"yes", "no"})


class LanguageHistoryTests(unittest.TestCase):
    def test_old_history_without_a_language_counts_as_javascript(self) -> None:
        path = brain.save_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        old = {"day": "2026-10-01", "activity": "eval", "seconds": 50.0, "errors": 1, "total": 20, "age": 40,
               "check_id": ""}
        path.write_text(json.dumps({"results": [old]}), encoding="utf-8")
        js = brain.summary(today=date(2026, 10, 1))
        py = brain.summary(today=date(2026, 10, 1), language="python")
        self.assertEqual(next(a for a in js["activities"] if a["id"] == "eval")["best"]["age"], 40)
        self.assertIsNone(next(a for a in py["activities"] if a["id"] == "eval")["best"])
        # ...but the day still counts toward the stamps in both.
        self.assertEqual(js["streak"], 1)
        self.assertEqual(py["streak"], 1)

    def test_code_age_is_kept_per_language(self) -> None:
        day = date(2026, 10, 3)
        brain.record("eval", 100, 2, 20, today=day)
        brain.record("eval", 40, 0, 20, today=day, language="python")
        js = next(a for a in brain.summary(today=day)["activities"] if a["id"] == "eval")
        py = next(a for a in brain.summary(today=day, language="python")["activities"] if a["id"] == "eval")
        self.assertEqual(js["best"]["seconds"], 100)
        self.assertEqual(py["best"]["seconds"], 40)
        self.assertEqual(py["best"]["language"], "python")
        self.assertLess(py["best"]["age"], js["best"]["age"])

    def test_a_python_round_stamps_the_day_and_a_python_check_has_its_own_age(self) -> None:
        day = date(2026, 10, 3)
        for activity_id in CHECK:
            brain.record(activity_id, 30, 1, ACTIVITIES_BY_ID[activity_id].count,
                         check_id="2026-10-03/py", today=day, language="python")
        py = brain.summary(today=day, language="python")
        js = brain.summary(today=day)
        self.assertEqual([c["day"] for c in py["checkAges"]], ["2026-10-03"])
        self.assertEqual(js["checkAges"], [])
        self.assertTrue(js["trainedToday"])
        self.assertEqual(py["language"], "python")
        self.assertEqual(py["languages"], ["javascript", "python"])

    def test_python_activities_are_worded_for_python(self) -> None:
        py = {a["id"]: a for a in brain.summary(language="python")["activities"]}
        self.assertEqual(py["syntax"]["question"], "Valid Python?")
        self.assertIn("print", py["eval"]["question"])
        self.assertEqual([a for a in py], [a.id for a in ACTIVITIES])

    def test_both_languages_score_alike(self) -> None:
        for a in ACTIVITIES:
            self.assertEqual(brain.code_age(a.id, 70, 1, a.count), brain.code_age(a.id, 70, 1, a.count, "python"))

    def test_an_unknown_language_is_refused(self) -> None:
        with self.assertRaises(KeyError):
            brain.record("eval", 10, 0, 20, language="cobol")
        with self.assertRaises(KeyError):
            make_round("eval", 1, "cobol")


class RouteTests(unittest.TestCase):
    def test_a_python_round_comes_over_the_route(self) -> None:
        from code_coach.api.server import brain_round

        r = brain_round("trace", 3, "python")
        self.assertEqual(r["language"], "python")
        self.assertEqual(len(r["items"]), ACTIVITIES_BY_ID["trace"].count)
        self.assertEqual(r["items"][0]["prompt"], make_round("trace", 3, "python")[0].prompt)

    def test_a_python_result_is_kept_under_python(self) -> None:
        from code_coach.api.schemas import BrainResultRequest
        from code_coach.api.server import brain_result, brain_summary

        self.assertTrue(brain_result(BrainResultRequest(activity="eval", seconds=90, errors=1, total=20,
                                                        language="python"))["best"])
        py = next(a for a in brain_summary("python")["activities"] if a["id"] == "eval")
        js = next(a for a in brain_summary()["activities"] if a["id"] == "eval")
        self.assertIsNotNone(py["best"])
        self.assertIsNone(js["best"])
        # A result with no language is still JavaScript.
        self.assertTrue(brain_result(BrainResultRequest(activity="eval", seconds=90, errors=1, total=20))["best"])

    def test_an_unknown_language_is_a_404(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.schemas import BrainResultRequest
        from code_coach.api.server import brain_result, brain_round, brain_summary

        with self.assertRaises(HTTPException):
            brain_round("eval", 1, "cobol")
        with self.assertRaises(HTTPException):
            brain_summary("cobol")
        with self.assertRaises(HTTPException):
            brain_result(BrainResultRequest(activity="eval", language="cobol"))


if __name__ == "__main__":
    unittest.main()
