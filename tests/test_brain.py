"""Brain Drills: every answer held to real JavaScript, and the code age.

The drills' answers are worked out in Python by modelling JavaScript; here
node is the oracle. Every template, over many seeds, is run in node -
Quick Eval as console.log would print it, Truthy or Falsy through
Boolean(), loop counts and final values by running the code, Syntax Snap
by compiling the line as a script - and must agree with the model.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import unittest
from datetime import date

from code_coach import brain
from code_coach.brain import ACTIVITIES, ACTIVITIES_BY_ID, CHECK, balanced, code_age, make_round

HAS_NODE = shutil.which("node") is not None
SEEDS = range(40)


def node_values(snippets: list[tuple[str, str]]) -> list[str]:
    """Run each (how, code) in node; how is "print", "bool", "run" or "syntax"."""
    script = """
const util = require("util");
const vm = require("vm");
const cases = JSON.parse(require("fs").readFileSync(0, "utf8"));
const show = (v) => (typeof v === "string" ? v : util.inspect(v));
const out = cases.map(([how, code]) => {
  try {
    if (how === "print") return show((0, eval)("(" + code + ")"));
    if (how === "bool") return Boolean((0, eval)("(" + code + ")")) ? "truthy" : "falsy";
    if (how === "run") return show((0, eval)(code));
    if (how === "syntax") { new vm.Script(code); return "valid"; }
  } catch (e) {
    if (how === "syntax" && e instanceof SyntaxError) return "invalid";
    return "ERROR " + e.message;
  }
});
process.stdout.write(JSON.stringify(out));
"""
    done = subprocess.run([shutil.which("node"), "-e", script], input=json.dumps(snippets),
                          capture_output=True, text=True, encoding="utf-8", timeout=120)
    if done.returncode != 0:
        raise AssertionError(done.stderr)
    return json.loads(done.stdout)


def _rounds(activity_id: str):
    for seed in SEEDS:
        yield from make_round(activity_id, seed)


@unittest.skipUnless(HAS_NODE, "needs node")
class OracleTests(unittest.TestCase):
    def check(self, activity_id: str, how: str, code_of) -> None:
        items = list({i.prompt + i.check: i for i in _rounds(activity_id)}.values())
        got = node_values([(how, code_of(i)) for i in items])
        for item, value in zip(items, got):
            with self.subTest(prompt=item.prompt):
                self.assertEqual(value, item.answer)

    def test_quick_eval_prints_what_node_prints(self) -> None:
        self.check("eval", "print", lambda i: i.prompt)

    def test_truthy_or_falsy_is_what_boolean_says(self) -> None:
        self.check("truthy", "bool", lambda i: i.prompt)

    def test_loop_counts_are_what_the_loops_do(self) -> None:
        self.check("loops", "run", lambda i: i.check)

    def test_final_values_are_what_the_code_leaves(self) -> None:
        self.check("trace", "run", lambda i: i.check)

    def test_syntax_snap_agrees_with_the_parser(self) -> None:
        lines = [(line, "valid" if ok else "invalid") for line, ok, _why in brain._SYNTAX]
        got = node_values([("syntax", line) for line, _ in lines])
        for (line, want), value in zip(lines, got):
            with self.subTest(line=line):
                self.assertEqual(value, want)


class ActivityTests(unittest.TestCase):
    def test_every_activity_makes_a_full_round_of_its_kind(self) -> None:
        for activity in ACTIVITIES:
            with self.subTest(activity=activity.id):
                items = make_round(activity.id, 1)
                self.assertEqual(len(items), activity.count)
                if activity.kind == "pick":
                    self.assertTrue(all(i.answer in activity.choices for i in items))
                    # Both answers turn up, so guessing one side all round fails.
                    answers = {i.answer for s in range(10) for i in make_round(activity.id, s)}
                    self.assertEqual(answers, set(activity.choices))

    def test_a_seed_gives_the_same_round(self) -> None:
        for activity in ACTIVITIES:
            self.assertEqual(make_round(activity.id, 9), make_round(activity.id, 9))

    def test_bracket_answers_agree_with_another_way_of_checking(self) -> None:
        def by_removal(text: str) -> bool:
            while any(p in text for p in ("()", "[]", "{}")):
                for p in ("()", "[]", "{}"):
                    text = text.replace(p, "")
            return text == ""

        for item in _rounds("brackets"):
            with self.subTest(text=item.prompt):
                self.assertEqual(item.answer == "yes", by_removal(item.prompt))
                self.assertEqual(balanced(item.prompt), by_removal(item.prompt))

    def test_recall_asks_for_a_value_it_showed(self) -> None:
        for item in _rounds("recall"):
            name = item.prompt.rstrip("?")
            self.assertIn(f"let {name} = {item.answer};", item.show)


class CodeAgeTests(unittest.TestCase):
    def test_sharp_is_twenty_and_slow_is_eighty(self) -> None:
        a = ACTIVITIES_BY_ID["eval"]
        self.assertEqual(code_age("eval", a.par * a.count * 0.5, 0, a.count), 20)
        self.assertEqual(code_age("eval", a.slow * a.count * 2, 0, a.count), 80)

    def test_faster_is_younger_and_mistakes_add_years(self) -> None:
        a = ACTIVITIES_BY_ID["truthy"]
        mid = (a.par + a.slow) / 2 * a.count
        self.assertLess(code_age("truthy", mid * 0.8, 0, a.count), code_age("truthy", mid, 0, a.count))
        self.assertEqual(code_age("truthy", mid, 2, a.count), code_age("truthy", mid, 0, a.count) + 10)

    def test_recall_is_scored_on_memory_not_speed(self) -> None:
        self.assertEqual(code_age("recall", 999, 0, 6), 20)
        self.assertEqual(code_age("recall", 1, 3, 6), 50)


class RecordTests(unittest.TestCase):
    def test_stamps_streak_and_check_ages(self) -> None:
        days = [date(2026, 10, d) for d in (1, 2, 3)]
        for day in days:
            brain.record("eval", 60, 0, 20, today=day)
        for activity_id in CHECK:
            brain.record(activity_id, 30, 1, ACTIVITIES_BY_ID[activity_id].count,
                         check_id="2026-10-03/1", today=days[-1])
        s = brain.summary(today=days[-1])
        self.assertEqual(s["streak"], 3)
        self.assertTrue(s["trainedToday"])
        self.assertEqual(len(s["stamps"]), 28)
        self.assertTrue(s["stamps"][-1]["trained"])
        self.assertEqual([c["day"] for c in s["checkAges"]], ["2026-10-03"])
        eval_entry = next(a for a in s["activities"] if a["id"] == "eval")
        self.assertIsNotNone(eval_entry["best"])

    def test_a_missed_day_breaks_the_streak(self) -> None:
        brain.record("eval", 60, 0, 20, today=date(2026, 10, 1))
        brain.record("eval", 60, 0, 20, today=date(2026, 10, 3))
        self.assertEqual(brain.summary(today=date(2026, 10, 3))["streak"], 1)

    def test_an_unfinished_check_has_no_age(self) -> None:
        brain.record("eval", 60, 0, 20, check_id="2026-10-03/9", today=date(2026, 10, 3))
        self.assertEqual(brain.summary(today=date(2026, 10, 3))["checkAges"], [])


class RouteTests(unittest.TestCase):
    def test_the_home_screen_has_every_activity_and_four_weeks_of_stamps(self) -> None:
        from code_coach.api.server import brain_summary

        s = brain_summary()
        self.assertEqual([a["id"] for a in s["activities"]], [a.id for a in ACTIVITIES])
        self.assertEqual(len(s["stamps"]), 28)
        self.assertEqual(s["check"], list(CHECK))

    def test_a_round_carries_its_answers(self) -> None:
        from code_coach.api.server import brain_round

        r = brain_round("loops", 3)
        self.assertEqual(len(r["items"]), ACTIVITIES_BY_ID["loops"].count)
        self.assertTrue(all(i["answer"] for i in r["items"]))

    def test_a_result_reports_its_age_and_a_new_best(self) -> None:
        from code_coach.api.schemas import BrainResultRequest
        from code_coach.api.server import brain_result

        first = brain_result(BrainResultRequest(activity="eval", seconds=100, errors=2, total=20))
        self.assertTrue(first["best"])
        slower = brain_result(BrainResultRequest(activity="eval", seconds=150, errors=3, total=20))
        self.assertFalse(slower["best"])
        faster = brain_result(BrainResultRequest(activity="eval", seconds=40, errors=0, total=20))
        self.assertTrue(faster["best"])
        self.assertLess(faster["age"], first["age"])

    def test_an_unknown_activity_is_a_404(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.server import brain_round

        with self.assertRaises(HTTPException):
            brain_round("chess")


if __name__ == "__main__":
    unittest.main()
