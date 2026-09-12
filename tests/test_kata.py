"""The katas, and the marker that judges them.

The load-bearing test is `test_every_reference_passes_its_own_cases`. A
kata marks a student against what its reference produces, so a reference
that is wrong does not fail loudly — it marks correct answers wrong, and
the student has no way to tell which of the two of you is at fault. So
every reference goes through the same driver a student's code goes
through, and has to pass every case.

The rest is about the marker being hard to fool in both directions: it
must not pass something wrong, and it must not fail something right.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code
from code_coach.kata import families, harness, judge, kata, katas


def _is_edge(arg) -> bool:
    """Whether one argument is an awkward input rather than a middle.

    Zero is the obvious degenerate number and is not always legal —
    Collatz never terminates from zero, so its smallest legal input is
    one. Counting one is the difference between describing the rule and
    describing the data that happened to exist when this was written.
    """
    if isinstance(arg, bool):
        return False
    if isinstance(arg, (str, list)):
        return len(arg) <= 1
    if isinstance(arg, int):
        return arg in (-1, 0, 1) or arg < 0
    return False


def _as_student(k) -> str:
    """The reference, renamed to what the kata asks for."""
    return k.reference().replace(
        f"def {k.solve.__name__}", f"def {k.name}", 1)


class ReferenceTests(unittest.TestCase):
    def test_every_reference_agrees_with_an_answer_typed_by_a_person(
        self,
    ) -> None:
        """The one that can actually catch a wrong reference.

        The test below this one — running the reference against what the
        reference says — is worth having and does not do this job: it
        compares the reference with itself and passes however wrong it
        is. That was found by breaking `digital_root` so it stopped at
        ten instead of nine and watching the suite stay green.

        These answers were worked out by hand and typed in. They are the
        only values in the kata files that did not come out of the code
        being checked, which is what makes disagreeing with them mean
        something.
        """
        for k in katas():
            with self.subTest(kata=k.id):
                self.assertTrue(
                    k.checks, f"{k.id} has no hand-written answer")
                for args, want in k.checks:
                    got = k.solve(*args)
                    self.assertEqual(
                        got, want,
                        f"{k.id}{args}: the reference says {got!r} and a "
                        f"person wrote {want!r}")
                    self.assertEqual(
                        isinstance(got, bool), isinstance(want, bool),
                        f"{k.id}{args}: {got!r} and {want!r} are not the "
                        f"same kind of thing")

    def test_the_hand_written_answers_are_about_real_cases(self) -> None:
        """A hand-written answer for an input the kata never uses proves
        nothing about the kata."""
        for k in katas():
            with self.subTest(kata=k.id):
                for args, _ in k.checks:
                    self.assertIn(
                        tuple(args), k.cases,
                        f"{k.id} checks {args}, which is not one of its cases")

    def test_a_hand_written_answer_lands_on_an_awkward_input(self) -> None:
        """Where the hand-written answers have to be, not just that there
        are some.

        Three answers for large ordinary numbers catch almost nothing. A
        reference for digital root was broken so that it stopped at ten
        rather than nine — a difference visible in exactly one input —
        and the hand-written answers for 999999999, 12345 and 100 all
        still agreed with it. The boundary is where a reference goes
        wrong, so the boundary is where a person has to have written
        something down.
        """
        for k in katas():
            with self.subTest(kata=k.id):
                on_edge = [
                    args for args, _ in k.checks
                    if any(_is_edge(a) for a in args)
                ]
                self.assertTrue(
                    on_edge,
                    f"{k.id}: every hand-written answer is for an ordinary "
                    f"input, so none of them pins a boundary")

    def test_every_reference_passes_its_own_cases(self) -> None:
        """Weaker than it looks, and kept for what it does catch: a
        reference that raises, hangs, or returns something that cannot
        survive the trip through the driver. It cannot catch one that is
        merely wrong — see the test above."""
        for k in katas():
            with self.subTest(kata=k.id):
                out, err, code = run_code(
                    harness(k, _as_student(k)), language="python")
                outcome = judge(k, out, err, code)
                self.assertEqual(outcome.broke, "")
                failed = [r for r in outcome.results if not r.passed]
                self.assertEqual(
                    failed, [],
                    f"{k.id}: {[(r.args, r.got, r.want) for r in failed][:3]}")

    def test_every_kata_is_named_once(self) -> None:
        ids = [k.id for k in katas()]
        self.assertEqual(sorted(ids), sorted(set(ids)))
        names = [k.name for k in katas()]
        self.assertEqual(sorted(names), sorted(set(names)))

    def test_the_signature_matches_the_reference(self) -> None:
        """The screen shows a signature and the marker calls that name with
        that many arguments. If they disagree, every case errors and the
        student is told their logic is wrong."""
        import inspect

        for k in katas():
            with self.subTest(kata=k.id):
                taken = list(inspect.signature(k.solve).parameters)
                self.assertEqual(
                    len(taken), len(k.params),
                    f"{k.id} shows {k.params} and calls {taken}")
                for case in k.cases:
                    self.assertEqual(
                        len(case), len(k.params),
                        f"{k.id} has a case with {len(case)} arguments")

    def test_the_cases_reach_an_edge(self) -> None:
        """The whole reason this mode exists.

        A kata whose ten cases are ten ordinary middles teaches nothing a
        printed exercise did not. Each one has to contain something
        awkward: an empty input, a single element, a negative, or the
        smallest number the problem allows.

        That last clause is the one worth spelling out. Zero is the
        obvious degenerate number and is not always a legal input —
        Collatz never terminates from zero, so its smallest legal input
        is one, and that is its base case rather than a middle. Counting
        one as an edge is the difference between this test describing the
        rule and describing the data that happened to exist when it was
        written.
        """
        for k in katas():
            with self.subTest(kata=k.id):
                edges = sum(
                    1 for case in k.cases for arg in case if _is_edge(arg))
                self.assertGreater(
                    edges, 0, f"{k.id} never tries an awkward input")

    def test_the_answers_are_not_all_the_same(self) -> None:
        """A case set whose every answer is False passes for a function
        that returns False and ignores its argument."""
        for k in katas():
            with self.subTest(kata=k.id):
                answers = [repr(a) for a in k.expected()]
                self.assertGreater(
                    len(set(answers)), 1,
                    f"{k.id} has one answer for every input")

    def test_every_kata_belongs_to_a_family(self) -> None:
        for k in katas():
            with self.subTest(kata=k.id):
                self.assertIn(k.family, families())
                self.assertTrue(k.brief and k.example and k.hint)


class MarkerTests(unittest.TestCase):
    """The judge, from both sides."""

    def _check(self, kata_id: str, code: str):
        k = kata(kata_id)
        out, err, exit_code = run_code(harness(k, code), language="python")
        return judge(k, out, err, exit_code)

    def test_a_wrong_answer_fails_and_says_which_input(self) -> None:
        outcome = self._check(
            "count-vowels",
            "def count_vowels(word):\n"
            "    return sum(1 for c in word if c in 'aeiou')")
        self.assertFalse(outcome.passed)
        wrong = [r for r in outcome.results if not r.passed]
        self.assertTrue(wrong)
        self.assertIn("Apple", [r.args[0] for r in wrong])

    def test_a_missing_function_is_not_reported_as_ten_wrong_answers(
        self,
    ) -> None:
        outcome = self._check("count-vowels", "def vowels(word):\n    return 0")
        self.assertIn("no function called count_vowels", outcome.broke)
        self.assertEqual(outcome.results, ())

    def test_code_that_does_not_parse_says_so(self) -> None:
        outcome = self._check("count-vowels", "def count_vowels(word)\n    x")
        self.assertIn("SyntaxError", outcome.broke)
        # And not the scratch file it happened to be written to.
        self.assertNotIn("Temp", outcome.broke)
        self.assertNotIn(".py", outcome.broke)

    def test_a_raised_error_is_reported_against_its_own_case(self) -> None:
        outcome = self._check(
            "count-vowels",
            "def count_vowels(word):\n"
            "    if word == '':\n"
            "        raise ValueError('no')\n"
            "    return sum(1 for c in word.lower() if c in 'aeiou')")
        broken = [r for r in outcome.results if r.error]
        self.assertEqual(len(broken), 1)
        self.assertEqual(broken[0].args, ("",))
        self.assertIn("ValueError", broken[0].error)

    def test_the_students_own_printing_does_not_confuse_the_marker(
        self,
    ) -> None:
        """Printing while you work something out is normal, and it lands on
        stdout in front of the marker's line."""
        outcome = self._check(
            "count-vowels",
            "def count_vowels(word):\n"
            "    print('checking', word)\n"
            "    return sum(1 for c in word.lower() if c in 'aeiou')")
        self.assertTrue(outcome.passed)

    def test_a_number_is_not_accepted_where_the_answer_is_a_boolean(
        self,
    ) -> None:
        """True == 1 in Python, and a function returning 1 is not right.
        This exact confusion produced thirteen false matches in a Lisp
        harness in this repo once already."""
        outcome = self._check(
            "is-prime",
            "def is_prime(n):\n"
            "    if n < 2:\n"
            "        return 0\n"
            "    f = 2\n"
            "    while f * f <= n:\n"
            "        if n % f == 0:\n"
            "            return 0\n"
            "        f += 1\n"
            "    return 1")
        self.assertFalse(outcome.passed)

    def test_a_tuple_is_accepted_where_a_list_was_expected(self) -> None:
        """JSON has one sequence type and Python has two. A correct answer
        that happens to be a tuple must not fail for that alone."""
        outcome = self._check(
            "sort-odds",
            "def sort_odds(numbers):\n"
            "    odds = sorted(n for n in numbers if n % 2 != 0)\n"
            "    out = list(numbers)\n"
            "    spare = iter(odds)\n"
            "    for i, n in enumerate(out):\n"
            "        if n % 2 != 0:\n"
            "            out[i] = next(spare)\n"
            "    return tuple(out)")
        self.assertTrue(outcome.passed)


class RouteTests(unittest.TestCase):
    def test_the_list_is_served_grouped(self) -> None:
        from code_coach.api import server

        payload = server.kata_list()
        self.assertTrue(payload["families"])
        served = sum(len(f["katas"]) for f in payload["families"])
        self.assertEqual(served, len(katas()))
        for family in payload["families"]:
            for entry in family["katas"]:
                self.assertTrue(entry["signature"].startswith("def "))
                self.assertGreater(entry["cases"], 0)

    def test_checking_an_unknown_kata_is_refused(self) -> None:
        from fastapi import HTTPException

        from code_coach.api import server
        from code_coach.api.schemas import KataCheckRequest

        with self.assertRaises(HTTPException) as caught:
            server.kata_check(KataCheckRequest(kata_id="nonsense", code="x"))
        self.assertEqual(caught.exception.status_code, 404)

    def test_a_right_answer_comes_back_as_passed(self) -> None:
        from code_coach.api import server
        from code_coach.api.schemas import KataCheckRequest

        response = server.kata_check(
            KataCheckRequest(
                kata_id="sum-digits",
                code="def sum_digits(n):\n"
                     "    return sum(int(d) for d in str(abs(n)))"))
        self.assertTrue(response.passed)
        self.assertEqual(response.count, response.total)
