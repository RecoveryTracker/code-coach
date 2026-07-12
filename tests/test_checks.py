"""
Tests for AST-based drill validation (code_coach/checks.py + the build drills).

The old substring checks let a student pass by putting keywords in a string or
comment. These tests lock in that (a) real solutions still complete every build
drill, and (b) keyword-in-string / keyword-in-comment / plausible-but-wrong code
does NOT complete.

Run: .venv/bin/python -m unittest discover -s tests
"""

from __future__ import annotations

import unittest

from code_coach import checks
from code_coach.practice.session import evaluate_drill
from code_coach.skills.drills import DRILLS, get_drill


def _is_build(d) -> bool:
    return "dictation" not in (d.tags or [])


class Predicates(unittest.TestCase):
    def test_syntax_error_returns_false_not_raises(self):
        broken = "def (:\n  print("
        self.assertFalse(checks.uses_for(broken))
        self.assertFalse(checks.defines_function(broken))
        self.assertFalse(checks.assigns_variable(broken, "x"))

    def test_keyword_in_string_is_ignored(self):
        self.assertFalse(checks.uses_if('print("if else")'))
        self.assertFalse(checks.uses_while('print("while true")'))
        self.assertFalse(checks.uses_for('x = "for each"'))

    def test_keyword_in_comment_is_ignored(self):
        self.assertFalse(checks.uses_while("# use a while loop\nprint(1)"))
        self.assertFalse(checks.defines_function("# def greet later\nx = 1"))

    def test_real_constructs_detected(self):
        self.assertTrue(checks.uses_if("if x > 0:\n    print(x)"))
        self.assertTrue(checks.uses_if_else("if x:\n    a()\nelse:\n    b()"))
        self.assertFalse(checks.uses_if_else("if x:\n    a()"))
        self.assertTrue(checks.uses_and("if a and b:\n    pass"))
        self.assertTrue(checks.uses_nested_for(
            "for i in range(2):\n    for j in range(2):\n        print(i, j)"
        ))
        self.assertFalse(checks.uses_nested_for(
            "for i in range(2):\n    print(i)"
        ))
        self.assertTrue(checks.returns_value("def f():\n    return 1"))
        self.assertFalse(checks.returns_value("def f():\n    return"))

    def test_assignment_and_literals(self):
        self.assertTrue(checks.assigns_variable("score = 10", "score"))
        self.assertTrue(checks.assigns_variable("score += 1", "score"))
        self.assertFalse(checks.assigns_variable("print(score)", "score"))
        self.assertTrue(checks.assigns_list("nums = [1, 2, 3]", "nums"))
        self.assertFalse(checks.assigns_list("nums = 5", "nums"))
        self.assertTrue(checks.assigns_dict("p = {'a': 1}", "p"))
        self.assertTrue(checks.subscripts_name('grades["score"]', "grades"))
        self.assertTrue(checks.calls_method("q.pop(0)", "pop", arg0=0))
        self.assertFalse(checks.calls_method("q.pop()", "pop", arg0=0))
        self.assertTrue(checks.has_constant("found = 7 in data", 7))
        self.assertFalse(checks.has_constant('x = "7"', 7))
        # 7 must not match True (type-strict)
        self.assertFalse(checks.has_constant("x = True", 7))

    def test_prints_name(self):
        self.assertTrue(checks.prints_name("print(total)", "total"))
        self.assertFalse(checks.prints_name('print("total")', "total"))


class BuildDrillsAcceptRealSolutions(unittest.TestCase):
    def test_every_build_drill_completes_on_its_example(self):
        failures = []
        for d in DRILLS:
            if not _is_build(d):
                continue
            solution = "\n".join(s.example for s in d.steps)
            res = evaluate_drill(d, solution, coach_level=2)
            if not res["complete"]:
                failures.append(d.id)
        self.assertEqual(failures, [], f"example solution stopped completing: {failures}")


class BuildDrillsRejectGaming(unittest.TestCase):
    CASES = [
        ("cond-if-1", 'print("if only")'),
        ("cond-else-2", 'print("if this else that")'),
        ("cond-and-3", "# age and ticket\nprint(1)"),
        ("loops-for-1", 'print("for real")'),
        ("loops-while-2", "# use while later\nprint(1)"),
        ("loops-nested-4", "for i in range(3):\n    print(i)"),
        ("func-def-2", 'print("def greet")'),
        ("func-return-3", "def double(n):\n    print(n * 2)"),
        ("dicts-create-2", "person = [1, 2]"),
        ("struct-queue-5", "queue.append(1)\nqueue.pop()"),
    ]

    def test_gaming_attempts_do_not_complete(self):
        still_passing = []
        for drill_id, code in self.CASES:
            d = get_drill(drill_id)
            res = evaluate_drill(d, code, coach_level=2)
            if res["complete"]:
                still_passing.append(drill_id)
        self.assertEqual(
            still_passing, [], f"gaming still completes: {still_passing}"
        )


if __name__ == "__main__":
    unittest.main()
