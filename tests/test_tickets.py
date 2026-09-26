"""Tickets: a continuous story, and checks that bite both ways.

A ticket is only a lesson in keeping old behaviour if the old behaviour
is really being checked, so every rule here is checked by running code
through the real drivers rather than by reading it:

  continuity    ticket k starts where ticket k-1 finished
  the answer    every ticket's model `after` passes all its checks
  there is      every ticket's `start` fails at least one of the checks
  work to do    the ticket names as new
  the rest is   and passes every check it does not - so the regression
  real          half is behaviour the start already had
  small         the answer is an edit, not a rewrite
  the oracles   agree with answers written out by hand, and never
                change what they were handed
"""

from __future__ import annotations

import copy
import difflib
import json
import os
import unittest

os.environ.setdefault("CODE_COACH_RUN_TIMEOUT", "30")

from code_coach.tickets import KINDS, Check, projects, project, run_ticket, ticket  # noqa: E402

#: How many lines the model answer may change, counted as the larger of
#: lines added and lines removed.
MAX_CHANGED_LINES = 12


def _all():
    return [(p, t) for p in projects() for t in p.tickets]


def _changed(start: str, after: str) -> int:
    diff = [
        line for line in difflib.unified_diff(
            start.strip().splitlines(), after.strip().splitlines(),
            lineterm="", n=0)
        if line[:1] in "+-" and not line.startswith(("+++", "---"))
    ]
    added = sum(1 for line in diff if line.startswith("+"))
    removed = sum(1 for line in diff if line.startswith("-"))
    return max(added, removed)


class ShapeTests(unittest.TestCase):

    def test_two_projects_in_two_languages(self) -> None:
        self.assertEqual({p.language for p in projects()},
                         {"python", "javascript"})

    def test_ids_are_unique(self) -> None:
        pids = [p.id for p in projects()]
        self.assertEqual(len(pids), len(set(pids)))
        tids = [t.id for _, t in _all()]
        # Unique across projects too: progress is keyed by ticket id.
        self.assertEqual(len(tids), len(set(tids)))

    def test_five_or_six_tickets_each_of_known_kinds(self) -> None:
        for p in projects():
            with self.subTest(project=p.id):
                self.assertIn(len(p.tickets), (5, 6))
                self.assertEqual({t.kind for t in p.tickets}, set(KINDS))
                for t in p.tickets:
                    self.assertIn(t.kind, KINDS)
                    self.assertTrue(t.report and t.hint and t.lesson, t.id)

    def test_new_names_are_checked_names(self) -> None:
        for _, t in _all():
            with self.subTest(ticket=t.id):
                names = [c.name for c in t.checks]
                self.assertEqual(len(names), len(set(names)))
                self.assertTrue(t.new)
                for name in t.new:
                    self.assertIn(name, names)
                self.assertLess(len(t.new), len(names),
                                "no regression checks at all")

    def test_projects_are_a_realistic_size(self) -> None:
        for p in projects():
            for t in p.tickets:
                with self.subTest(ticket=t.id):
                    lines = len(t.after.strip().splitlines())
                    self.assertGreaterEqual(lines, 25)
                    self.assertLessEqual(lines, 90)

    def test_lookup(self) -> None:
        p = projects()[0]
        self.assertIs(project(p.id), p)
        self.assertIs(ticket(p.id, p.tickets[1].id), p.tickets[1])
        self.assertIsNone(ticket(p.id, "nope"))
        self.assertIsNone(project("nope"))


class ContinuityTests(unittest.TestCase):

    def test_each_ticket_starts_where_the_last_finished(self) -> None:
        for p in projects():
            for before, after in zip(p.tickets, p.tickets[1:]):
                with self.subTest(ticket=after.id):
                    self.assertEqual(after.start, before.after)

    def test_checks_carry_forward(self) -> None:
        """A function checked once stays checked: a later ticket cannot
        quietly stop caring whether it still works."""
        for p in projects():
            for before, after in zip(p.tickets, p.tickets[1:]):
                with self.subTest(ticket=after.id):
                    self.assertLessEqual(
                        {c.name for c in before.checks},
                        {c.name for c in after.checks})

    def test_the_answer_is_an_edit(self) -> None:
        for _, t in _all():
            with self.subTest(ticket=t.id):
                n = _changed(t.start, t.after)
                self.assertGreaterEqual(n, 1)
                self.assertLessEqual(n, MAX_CHANGED_LINES)


class RunTests(unittest.TestCase):
    """Through the real drivers, once per ticket for start and after."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.after = {t.id: run_ticket(p, t, t.after) for p, t in _all()}
        cls.start = {t.id: run_ticket(p, t, t.start) for p, t in _all()}

    def test_every_answer_passes_every_check(self) -> None:
        for _, t in _all():
            with self.subTest(ticket=t.id):
                got = self.after[t.id]
                self.assertEqual(got["broke"], "")
                failing = [(f["name"], f["broke"],
                            [r for r in f["results"] if not r["passed"]])
                           for f in got["functions"] if not f["passed"]]
                self.assertTrue(got["passed"], failing)

    def test_every_start_fails_something_new(self) -> None:
        for _, t in _all():
            with self.subTest(ticket=t.id):
                got = self.start[t.id]
                self.assertFalse(got["passed"])
                self.assertFalse(got["new_passed"])
                self.assertTrue(any(not f["passed"] for f in got["functions"]
                                    if f["new"]))

    def test_every_start_passes_every_regression_check(self) -> None:
        for _, t in _all():
            with self.subTest(ticket=t.id):
                got = self.start[t.id]
                self.assertEqual(got["broke"], "")
                for f in got["functions"]:
                    if not f["new"]:
                        self.assertTrue(f["passed"], (f["name"], f["broke"]))
                self.assertTrue(got["kept_passed"])

    def test_new_flags_match_the_ticket(self) -> None:
        for _, t in _all():
            with self.subTest(ticket=t.id):
                flagged = {f["name"] for f in self.after[t.id]["functions"]
                           if f["new"]}
                self.assertEqual(flagged, set(t.new))


class BreakingSomethingOldTests(unittest.TestCase):
    """The point of the mode: a fix that breaks old behaviour fails."""

    def test_python_regression_is_reported_as_regression(self) -> None:
        p = project("corner-shop")
        t = ticket("corner-shop", "shop-3")
        # Does the new rule, and breaks pounds on the way.
        code = t.after.replace(
            'return f"£{pence // 100}.{pence % 100:02d}"',
            'return f"£{pence / 100}"')
        self.assertNotEqual(code, t.after)
        got = run_ticket(p, t, code)
        self.assertFalse(got["passed"])
        self.assertTrue(got["new_passed"])
        self.assertFalse(got["kept_passed"])
        broken = {f["name"] for f in got["functions"] if not f["passed"]}
        self.assertIn("pounds", broken)
        self.assertNotIn("discounted_total", broken)

    def test_javascript_regression_is_reported_as_regression(self) -> None:
        p = project("task-board")
        t = ticket("task-board", "board-5")
        # Leaves done tasks out of the workload by deleting them from the
        # board's own array: the counts are right, and the board has lost
        # its done column for every caller after this one.
        code = t.after.replace(
            "function assigneeCounts(tasks) {\n",
            "function assigneeCounts(tasks) {\n"
            "  for (let i = tasks.length - 1; i >= 0; i--) "
            "if (tasks[i].status === \"done\") tasks.splice(i, 1);\n")
        self.assertNotEqual(code, t.after)
        got = run_ticket(p, t, code)
        self.assertFalse(got["passed"])
        counts = next(f for f in got["functions"]
                      if f["name"] == "assigneeCounts")
        # Right answers, but it changed what it was handed.
        self.assertTrue(any(r["changed"] for r in counts["results"]))

    def test_sort_in_place_is_caught(self) -> None:
        p = project("task-board")
        t = ticket("task-board", "board-4")
        code = t.after.replace("return [...tasks]\n", "return tasks\n")
        self.assertNotEqual(code, t.after)
        got = run_ticket(p, t, code)
        sort = next(f for f in got["functions"] if f["name"] == "sortedByDue")
        self.assertFalse(sort["passed"])
        self.assertTrue(any(r["changed"] for r in sort["results"]))

    def test_a_file_that_does_not_run_is_one_message(self) -> None:
        for p in projects():
            t = p.tickets[0]
            with self.subTest(project=p.id):
                got = run_ticket(p, t, t.start + "\n)(\n")
                self.assertFalse(got["passed"])
                self.assertTrue(got["broke"])
                self.assertTrue(all(f["broke"] == "" for f in got["functions"]))

    def test_learner_prints_are_kept_apart(self) -> None:
        p = project("corner-shop")
        t = p.tickets[0]
        got = run_ticket(p, t, t.after + '\nprint("hello there")\n')
        self.assertTrue(got["passed"])
        self.assertIn("hello there", got["stdout"])
        self.assertNotIn("<<<KATA", got["stdout"])


def _checks() -> list[tuple[str, Check]]:
    seen: dict[int, tuple[str, Check]] = {}
    for _, t in _all():
        for c in t.checks:
            seen.setdefault(id(c), (t.id, c))
    return list(seen.values())


class OracleTests(unittest.TestCase):

    def test_every_check_has_hand_written_answers(self) -> None:
        for where, c in _checks():
            with self.subTest(ticket=where, check=c.name):
                self.assertTrue(c.checks)

    def test_hand_written_answers_agree_with_the_oracle(self) -> None:
        for where, c in _checks():
            for args, want in c.checks:
                with self.subTest(ticket=where, check=c.name, args=args):
                    self.assertEqual(c.solve(*copy.deepcopy(args)), want)

    def test_oracles_never_mutate(self) -> None:
        for where, c in _checks():
            for args in c.cases:
                with self.subTest(ticket=where, check=c.name):
                    before = json.dumps(args, sort_keys=True)
                    c.solve(*args)
                    self.assertEqual(json.dumps(args, sort_keys=True), before)

    def test_cases_are_json(self) -> None:
        for where, c in _checks():
            with self.subTest(ticket=where, check=c.name):
                for args in c.cases:
                    self.assertEqual(len(args), len(c.params))
                    self.assertEqual(json.loads(json.dumps(list(args))),
                                     list(args))

    def test_new_checks_differ_from_the_last_ticket(self) -> None:
        """A check named as new must actually be new or changed: either
        the function was not checked before, or its oracle now gives a
        different answer somewhere."""
        for p in projects():
            for before, after in zip(p.tickets, p.tickets[1:]):
                old = {c.name: c for c in before.checks}
                for c in after.checks:
                    with self.subTest(ticket=after.id, check=c.name):
                        if c.name not in old:
                            self.assertIn(c.name, after.new)
                            continue
                        was = old[c.name]
                        differs = c.cases != was.cases and any(
                            c.solve(*copy.deepcopy(a))
                            != was.solve(*copy.deepcopy(a))
                            for a in c.cases)
                        if c.name in after.new:
                            self.assertTrue(differs)
                        else:
                            # Unchanged: same truth on the same inputs.
                            self.assertEqual(
                                [c.solve(*copy.deepcopy(a)) for a in c.cases],
                                [was.solve(*copy.deepcopy(a)) for a in c.cases])


if __name__ == "__main__":
    unittest.main()
