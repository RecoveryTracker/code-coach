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

    Three clauses, each of which had to be argued for.

    A container that is empty or holds one thing. This is the usual
    degenerate case and covers dicts and tuples as well as lists and
    strings — a kata taking a dict was the first to notice the predicate
    only knew about two of the four.

    A number that is zero, one, minus one, or negative. Zero is the
    obvious one and is not always a legal input: Collatz never
    terminates from zero, so its smallest legal input is one, and that
    is its base case rather than a middle.

    And a container holding a negative. Some functions cannot have a
    degenerate input at all — one that swaps a pair always gets exactly
    two things — so for those the awkward case is a sign rather than a
    size. Without this clause such a kata can have no awkward input at
    all and the rule becomes unsatisfiable rather than demanding.
    """
    if isinstance(arg, bool):
        return False
    if isinstance(arg, (str, list, dict, tuple)):
        if len(arg) <= 1:
            return True
        items = arg.values() if isinstance(arg, dict) else arg
        return any(
            isinstance(x, int) and not isinstance(x, bool) and x < 0
            for x in items
        )
    if isinstance(arg, int):
        return arg in (-1, 0, 1) or arg < 0
    return False


def _as_student(k) -> str:
    """Exactly what Show answer puts on screen.

    Not a re-derivation of it. The whole value of running this is that
    the string a student is shown is the string that was checked — a
    helper that rebuilt it here could pass while the screen showed
    something that does not work.
    """
    return k.reference()


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
                    got = k.answer(args)
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
                if k.edge_note:
                    continue
                on_edge = [
                    args for args, _ in k.checks
                    if any(_is_edge(a) for a in args)
                ]
                self.assertTrue(
                    on_edge,
                    f"{k.id}: every hand-written answer is for an ordinary "
                    f"input, so none of them pins a boundary")

    def test_every_reference_passes_its_own_cases(self) -> None:
        """Weaker than it looks, and it earns its keep anyway.

        It cannot catch a reference that is merely wrong, because the
        expectation comes from the reference — see the test above for
        that. What it does catch is a reference that will not run on its
        own: one that raises, hangs, returns something that cannot
        survive the trip through the driver, or leans on a name defined
        beside it rather than inside it.

        That last one is not hypothetical. `to_roman` kept its table of
        numerals at module level, which is the obvious place for it and
        means Show answer hands over a function referring to something
        that is not there. Every case came back as a NameError the first
        time this ran.
        """
        for k in katas():
            with self.subTest(kata=k.id):
                out, err, code = run_code(
                    harness(k, _as_student(k)), language=k.language)
                outcome = judge(k, out, err, code)
                self.assertEqual(outcome.broke, "")
                failed = [r for r in outcome.results if not r.passed]
                self.assertEqual(
                    failed, [],
                    f"{k.id}: {[(r.args, r.got, r.want) for r in failed][:3]}")

    def test_the_shown_answer_defines_the_function_that_was_asked_for(
        self,
    ) -> None:
        """Show answer has to be code you could paste in.

        The reference is written under a private name in the content
        file and renamed on the way out. A rename that stopped working
        would leave the screen offering `_count_vowels`, which runs and
        then fails every case for a reason that is nothing to do with
        the student.
        """
        for k in katas():
            with self.subTest(kata=k.id):
                shown = k.reference()
                opener = (
                    f"function {k.name}("
                    if k.language == "javascript"
                    else f"def {k.name}("
                )
                self.assertIn(opener, shown)
                self.assertNotIn(f"def {k.solve.__name__}(", shown)
                self.assertFalse(
                    shown.lstrip().startswith("def _"),
                    f"{k.id} shows a private name")

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
                if edges:
                    continue
                # No structural edge is possible for every shape — a
                # clock time is never the empty string. Such a kata has
                # to say so and say what stands in for one, which is a
                # stated exemption rather than a silent one.
                self.assertTrue(
                    k.edge_note.strip(),
                    f"{k.id} never tries an awkward input, and does not "
                    f"say why it cannot")
                self.assertGreater(
                    len(k.edge_note.split()), 6,
                    f"{k.id} waves the rule away rather than answering it")

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
                self.assertTrue(
                    entry["signature"].startswith(("def ", "function ")))
                self.assertGreater(entry["cases"], 0)

    def test_the_answer_is_served_for_one_kata_at_a_time(self) -> None:
        from code_coach.api import server

        payload = server.kata_answer(kata_id="digital-root")
        self.assertEqual(payload["id"], "digital-root")
        self.assertIn("def digital_root(", payload["answer"])

    def test_asking_for_an_unknown_answer_is_refused(self) -> None:
        from fastapi import HTTPException

        from code_coach.api import server

        with self.assertRaises(HTTPException) as caught:
            server.kata_answer(kata_id="nonsense")
        self.assertEqual(caught.exception.status_code, 404)

    def test_the_answer_is_not_in_the_list_payload(self) -> None:
        """Asking is the point. An answer already in the browser is one
        you did not decide to look at."""
        from code_coach.api import server

        payload = server.kata_list()
        for family in payload["families"]:
            for entry in family["katas"]:
                with self.subTest(kata=entry["id"]):
                    self.assertNotIn("answer", entry)

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


class BrokenExerciseTests(unittest.TestCase):
    """The ones that arrive already written and already wrong.

    Two things have to be true of each, and the second is the one that
    can rot silently.

    The correct version has to pass — same rule as any kata, and covered
    by the tests above, which walk every kata including these.

    And the broken version has to fail. A "fix the bug" exercise whose
    code already works is a page that wastes your time, reads as though
    the marker is broken, and nothing else in the suite would ever
    notice: every other check here is about correct answers passing.
    """

    def _run(self, k, code: str):
        out, err, exit_code = run_code(harness(k, code), language="python")
        return judge(k, out, err, exit_code)

    def test_the_broken_version_really_is_broken(self) -> None:
        for k in katas("Fix the bug"):
            with self.subTest(kata=k.id):
                outcome = self._run(k, k.start)
                if outcome.broke:
                    # Refusing to run at all counts as broken, and is how
                    # a couple of these fail — an IndexError on the empty
                    # string, say. What is not allowed is passing.
                    continue
                self.assertFalse(
                    outcome.passed,
                    f"{k.id} is meant to be broken and passes all "
                    f"{len(k.cases)} cases")

    def test_the_fixed_version_passes(self) -> None:
        """The other half. Both are run through the driver rather than
        compared as text, because what is being claimed is that one works
        and the other does not."""
        for k in katas("Fix the bug"):
            with self.subTest(kata=k.id):
                outcome = self._run(k, _as_student(k))
                self.assertEqual(outcome.broke, "")
                self.assertTrue(
                    outcome.passed,
                    f"{k.id}: the correct version fails "
                    f"{[r.args for r in outcome.results if not r.passed][:3]}")

    def test_each_broken_one_explains_itself(self) -> None:
        for k in katas("Fix the bug"):
            with self.subTest(kata=k.id):
                self.assertTrue(k.start.strip())
                self.assertTrue(k.bug.strip())
                self.assertIn(
                    f"def {k.name}", k.start,
                    f"{k.start!r} does not define {k.name}")

    def test_nothing_outside_those_families_is_pre_filled(self) -> None:
        """A kata with code already in the box is a different exercise.
        Filling one in by accident turns writing it yourself into reading
        someone else's, which is the one thing the mode is not for.

        Two families are allowed it and both say why in their name.
        "Fix the bug" hands you something wrong to repair, and "Finish
        the program" hands you the surroundings a function lives in so
        the exercise is writing against code you did not write. Every
        other family starts empty, and the exemption is a list here
        rather than a condition per kata so that adding a third one is
        a decision somebody makes on purpose.

        It was made once, on purpose, for "Change it": code that is
        right for yesterday's requirement, and a request to change it.
        That is the modify step of PRIMM, which this app had nothing
        for, and it cannot be done from an empty box - the code being
        changed is the exercise. test_modify.py holds those drills to
        the rules that make them changes rather than disguised bug
        fixes.
        """
        allowed = {
            "Fix the bug", "Finish the program",
            "Change it", "Change it: JavaScript",
        }
        for k in katas():
            if k.family in allowed:
                continue
            with self.subTest(kata=k.id):
                self.assertEqual(k.start, "")
                self.assertEqual(k.bug, "")

    def test_the_pre_filled_families_are_the_ones_named(self) -> None:
        """The other half of the rule above: a family that ships code in
        the box must be one of the two, so a new family cannot quietly
        acquire pre-filled starts by being written that way."""
        named = {
            "Fix the bug", "Finish the program",
            "Change it", "Change it: JavaScript",
        }
        for k in katas():
            if k.start.strip():
                with self.subTest(kata=k.id):
                    self.assertIn(k.family, named)

class ProgressTests(unittest.TestCase):
    """Counting the goes, which is what decides the next one.

    A tick would be the wrong shape. These are practised rather than
    completed — the premise of the whole app is a dozen goes at one
    thing — so what is kept is how many times each came out right, and
    the screen picks the one with the fewest.
    """

    def setUp(self) -> None:
        import tempfile
        from pathlib import Path as _Path

        from code_coach.api import server
        from code_coach.progress.store import ProgressStore

        self.folder = _Path(tempfile.mkdtemp())
        self.was = server._store
        server._store = ProgressStore(self.folder / "progress.json")
        self.server = server

    def tearDown(self) -> None:
        self.server._store = self.was

    def _check(self, kata_id: str, code: str):
        from code_coach.api.schemas import KataCheckRequest

        return self.server.kata_check(
            KataCheckRequest(kata_id=kata_id, code=code))

    def test_a_right_answer_counts_and_a_wrong_one_does_not(self) -> None:
        right = "def sum_digits(n):\n    return sum(int(d) for d in str(abs(n)))"
        self.assertEqual(self._check("sum-digits", right).done, 1)
        self.assertEqual(self._check("sum-digits", right).done, 2)
        # A wrong go leaves the count where it was rather than resetting
        # it — getting one wrong on the fifth attempt does not undo four.
        wrong = self._check("sum-digits", "def sum_digits(n):\n    return 0")
        self.assertFalse(wrong.passed)
        self.assertEqual(wrong.done, 0)
        self.assertEqual(self._check("sum-digits", right).done, 3)

    def test_the_count_is_on_the_list(self) -> None:
        right = "def sum_digits(n):\n    return sum(int(d) for d in str(abs(n)))"
        self._check("sum-digits", right)
        payload = self.server.kata_list()
        found = {
            k["id"]: k["done"]
            for f in payload["families"] for k in f["katas"]
        }
        self.assertEqual(found["sum-digits"], 1)
        # Everything else stays at nothing, so the screen can tell what
        # has been touched from what has not.
        self.assertEqual(found["count-vowels"], 0)

    def test_it_survives_being_written_and_read_back(self) -> None:
        """The number is the point, so losing it on a restart would be
        losing the feature."""
        from code_coach.progress.store import ProgressStore

        right = "def sum_digits(n):\n    return sum(int(d) for d in str(abs(n)))"
        self._check("sum-digits", right)
        self._check("sum-digits", right)
        fresh = ProgressStore(self.folder / "progress.json").load()
        self.assertEqual(fresh.kata_counts()["sum-digits"], 2)
        self.assertIsNotNone(fresh.kata_done["sum-digits"].last_at)

    def test_a_file_written_before_this_existed_still_loads(self) -> None:
        """Nothing done yet, rather than a crash."""
        from code_coach.progress.store import StudentProgress

        raw = StudentProgress().to_dict()
        del raw["kata_done"]
        del raw["predict_done"]
        loaded = StudentProgress.from_dict(raw)
        self.assertEqual(loaded.kata_counts(), {})
        self.assertEqual(loaded.predict_counts(), {})

    def test_predict_counts_the_same_way(self) -> None:
        from code_coach.api.schemas import PredictCheckRequest
        from code_coach.kata.predict import PUZZLES

        p = PUZZLES[0]
        first = self.server.predict_check(
            PredictCheckRequest(puzzle_id=p.id, guess=p.expect))
        self.assertEqual(first.done, 1)
        missed = self.server.predict_check(
            PredictCheckRequest(puzzle_id=p.id, guess="nonsense"))
        self.assertEqual(missed.done, 0)
        again = self.server.predict_check(
            PredictCheckRequest(puzzle_id=p.id, guess=p.expect))
        self.assertEqual(again.done, 2)

    def test_the_two_modes_count_separately(self) -> None:
        """A kata and a puzzle can share an id one day, and one being
        practised is not the other being practised."""
        from code_coach.api.schemas import PredictCheckRequest
        from code_coach.kata.predict import PUZZLES

        right = "def sum_digits(n):\n    return sum(int(d) for d in str(abs(n)))"
        self._check("sum-digits", right)
        self.server.predict_check(
            PredictCheckRequest(puzzle_id=PUZZLES[0].id, guess=PUZZLES[0].expect))
        saved = self.server._store.load()
        self.assertEqual(list(saved.kata_counts()), ["sum-digits"])
        self.assertEqual(list(saved.predict_counts()), [PUZZLES[0].id])


class LevelTests(unittest.TestCase):
    """The order a family is read in.

    Difficulty is a judgement and there is nothing to compute it from,
    so what can be checked is that the judgement was made rather than
    skipped. A family whose katas are all the same level has a field
    saying nothing, and its order is then whichever order they happened
    to be written in — which is the thing this exists to stop.
    """

    def test_every_level_is_in_range(self) -> None:
        for k in katas():
            with self.subTest(kata=k.id):
                self.assertIn(k.level, (1, 2, 3, 4, 5))

    def test_a_family_is_not_all_one_level(self) -> None:
        from code_coach.kata import families

        for family in families():
            with self.subTest(family=family):
                levels = {k.level for k in katas(family)}
                self.assertGreater(
                    len(levels), 1,
                    f"{family} is all level {levels.pop()}, so nothing in "
                    f"it has been ranked against anything else")

    def test_each_family_reads_easiest_first(self) -> None:
        from code_coach.kata import families

        for family in families():
            with self.subTest(family=family):
                levels = [k.level for k in katas(family)]
                self.assertEqual(
                    levels, sorted(levels),
                    f"{family} is out of order: {levels}")

    def test_the_order_inside_a_level_is_the_one_it_was_written_in(
        self,
    ) -> None:
        """Sorting has to be stable.

        Within a level the order is curated — a family opens on the one
        worth doing first — and a sort that reshuffled equals would
        throw that away silently.
        """
        from code_coach.kata import _in_file_order

        written = [k.id for k in _in_file_order()]
        for level in (1, 2, 3, 4, 5):
            at_level = [k.id for k in katas() if k.level == level]
            with self.subTest(level=level):
                self.assertEqual(
                    at_level,
                    [i for i in written if i in set(at_level)])

    def test_the_families_keep_their_own_order(self) -> None:
        """Sorting by level interleaves the families, so the list of
        families has to come from the files rather than from the sorted
        katas — otherwise it starts with whichever family happens to
        hold the easiest kata.

        Against the file order itself rather than against two names
        written down here. Naming the last family meant this failed the
        day a new one was added at the end, which says nothing about
        whether the rule still holds.
        """
        from code_coach.kata import _in_file_order, families

        written: list[str] = []
        for k in _in_file_order():
            if k.family not in written:
                written.append(k.family)
        self.assertEqual(list(families()), written)


class NextUpTests(unittest.TestCase):
    """What the screen offers next, and why recency is part of it.

    The count alone cannot separate two things you have done twice. One
    of them was last week and one was ten minutes ago, and only one of
    those is worth doing again now — so the list carries when each was
    last right, and the screen breaks the tie on it.
    """

    def setUp(self) -> None:
        import tempfile
        from pathlib import Path as _Path

        from code_coach.api import server
        from code_coach.progress.store import ProgressStore

        self.folder = _Path(tempfile.mkdtemp())
        self.was = server._store
        server._store = ProgressStore(self.folder / "progress.json")
        self.server = server

    def tearDown(self) -> None:
        self.server._store = self.was

    def test_the_list_says_when_each_was_last_right(self) -> None:
        from code_coach.api.schemas import KataCheckRequest

        right = "def sum_digits(n):\n    return sum(int(d) for d in str(abs(n)))"
        self.server.kata_check(
            KataCheckRequest(kata_id="sum-digits", code=right))
        served = {
            k["id"]: k
            for f in self.server.kata_list()["families"] for k in f["katas"]
        }
        self.assertTrue(served["sum-digits"]["last"])
        # Never done is an empty string rather than a missing key, so the
        # screen can compare it against a real date without a special
        # case — and empty sorts before every date, which is what puts
        # the untried ones first.
        self.assertEqual(served["count-vowels"]["last"], "")

    def test_a_later_pass_moves_the_date_on(self) -> None:
        from code_coach.api.schemas import KataCheckRequest

        right = "def sum_digits(n):\n    return sum(int(d) for d in str(abs(n)))"
        self.server.kata_check(
            KataCheckRequest(kata_id="sum-digits", code=right))
        first = self.server._store.load().kata_last()["sum-digits"]
        self.server.kata_check(
            KataCheckRequest(kata_id="sum-digits", code=right))
        second = self.server._store.load().kata_last()["sum-digits"]
        self.assertGreaterEqual(second, first)

    def test_predict_carries_the_same_two_fields(self) -> None:
        from code_coach.api.schemas import PredictCheckRequest
        from code_coach.kata.predict import PUZZLES

        self.server.predict_check(
            PredictCheckRequest(puzzle_id=PUZZLES[0].id, guess=PUZZLES[0].expect))
        served = {
            p["id"]: p
            for f in self.server.predict_list()["families"]
            for p in f["puzzles"]
        }
        self.assertEqual(served[PUZZLES[0].id]["done"], 1)
        self.assertTrue(served[PUZZLES[0].id]["last"])
        self.assertIn("level", served[PUZZLES[0].id])


class JavaScriptTests(unittest.TestCase):
    """The katas written in JavaScript, and the join between the two.

    A JavaScript kata keeps a Python `solve`, because that is the oracle
    rather than the answer — the expected values are numbers, strings,
    arrays and plain objects, which mean the same in both languages, so
    one implementation of the truth is guarded by the same hand-written
    checks as everything else.

    Which leaves one thing to prove that the Python katas do not need:
    that the JavaScript answer agrees with that oracle. Reading it
    cannot show that. Running it can, and it is the same driver a
    student's code goes through, so a reference that agreed with itself
    and not with the oracle fails here.
    """

    def _js(self) -> tuple:
        return tuple(k for k in katas() if k.language == "javascript")

    def test_there_are_some(self) -> None:
        self.assertTrue(self._js())

    def test_every_javascript_answer_passes_every_case(self) -> None:
        for k in self._js():
            with self.subTest(kata=k.id):
                out, err, code = run_code(
                    harness(k, k.reference()), language="javascript")
                outcome = judge(k, out, err, code)
                self.assertEqual(outcome.broke, "")
                failed = [
                    (r.args, r.got, r.want, r.changed, r.error)
                    for r in outcome.results if not r.passed
                ]
                self.assertEqual(failed, [], f"{k.id}: {failed[:2]}")

    def test_the_answer_shown_is_javascript(self) -> None:
        """Show answer on a JavaScript kata handing over Python would be
        worse than showing nothing."""
        for k in self._js():
            with self.subTest(kata=k.id):
                shown = k.reference()
                self.assertTrue(shown.strip())
                self.assertNotIn("def ", shown)
                self.assertIn(k.name, shown)

    def test_the_signature_is_in_the_right_language(self) -> None:
        """The box opens on this line, so a Python signature on a
        JavaScript kata is a line that has to be deleted before anything
        can be typed."""
        for k in katas():
            with self.subTest(kata=k.id):
                if k.language == "javascript":
                    self.assertTrue(k.signature.startswith("function "))
                    self.assertTrue(k.signature.endswith("{"))
                else:
                    self.assertTrue(k.signature.startswith("def "))

    def test_a_wrong_javascript_answer_fails_and_names_the_input(
        self,
    ) -> None:
        k = kata("js-unique-of")
        outcome = self._run(k, "function uniqueOf(items) { return items; }")
        self.assertFalse(outcome.passed)
        wrong = [r for r in outcome.results if not r.passed]
        self.assertTrue(wrong)

    def test_changing_the_array_fails_even_when_the_answer_is_right(
        self,
    ) -> None:
        """The rule that matters most in this language.

        sort, reverse and splice all change the array in place, and the
        array was the caller's. The value returned can be exactly right
        while the page behind it is wrong, and only comparing the
        arguments before and after the call can see it.
        """
        k = kata("js-sorted-desc")
        outcome = self._run(
            k, "function sortedDesc(numbers) {\n"
               "  return numbers.sort((a, b) => b - a);\n}")
        self.assertFalse(outcome.passed)
        spoiled = [r for r in outcome.results if r.changed]
        self.assertTrue(spoiled, "mutating sort was not noticed")

    def test_sorting_as_text_is_caught(self) -> None:
        """`[10, 9, 100].sort()` gives 10, 100, 9 — the default compares
        as strings, which is the trap this kata exists for."""
        k = kata("js-sorted-desc")
        outcome = self._run(
            k, "function sortedDesc(numbers) {\n"
               "  return [...numbers].sort().reverse();\n}")
        self.assertFalse(outcome.passed)

    def _run(self, k, code: str):
        out, err, exit_code = run_code(harness(k, code), language="javascript")
        return judge(k, out, err, exit_code)


class RouteLanguageTests(unittest.TestCase):
    """The route runs a kata in the kata's language.

    It ran everything as Python, which was right while Python was the
    only one and meant every JavaScript kata came back "this did not
    run" whatever was typed into it. The screen tests could not see it
    because they call the marker directly; only going through the route
    does.
    """

    def _check(self, kata_id: str, code: str):
        from code_coach.api import server
        from code_coach.api.schemas import KataCheckRequest

        return server.kata_check(
            KataCheckRequest(kata_id=kata_id, code=code))

    def test_a_javascript_kata_runs_as_javascript(self) -> None:
        response = self._check(
            "js-unique-of",
            "function uniqueOf(items) { return [...new Set(items)]; }")
        self.assertEqual(response.broke, "")
        self.assertTrue(response.passed)

    def test_a_wrong_javascript_answer_is_marked_wrong_not_broken(
        self,
    ) -> None:
        """The distinction the hard-coded language destroyed: code that
        runs and is wrong has to read differently from code that did not
        run at all."""
        response = self._check(
            "js-unique-of", "function uniqueOf(items) { return items; }")
        self.assertEqual(response.broke, "")
        self.assertFalse(response.passed)
        self.assertGreater(response.total, response.count)

    def test_every_language_has_a_route_that_runs_it(self) -> None:
        """One right answer per language, through the route.

        Derived rather than listing the two: a third language added
        without touching the route would otherwise fail silently in
        exactly the same way.
        """
        from code_coach.kata import languages

        for language in languages():
            with self.subTest(language=language):
                first = next(
                    k for k in katas() if k.language == language)
                response = self._check(first.id, first.reference())
                self.assertEqual(response.broke, "")
                self.assertTrue(
                    response.passed,
                    f"{first.id} does not pass through the route")


class StubTests(unittest.TestCase):
    """Finish the program: a stub with the rest of the code around it.

    Two things have to hold, and they are the mirror of the broken
    exercises' two.

    The stub as given must not pass. An unfinished function that
    already answers every case is not unfinished, and nothing else in
    the suite would notice — every other check here is about correct
    answers passing.

    And the surroundings have to be surroundings. A stub whose `start`
    is only the empty function is a kata with a comment in it: the
    whole point of the shape is that there is a helper or a constant
    already in scope, and the answer should use it.
    """

    def _stubs(self) -> tuple:
        return katas("Finish the program")

    def _run(self, k, code: str):
        out, err, exit_code = run_code(harness(k, code), language=k.language)
        return judge(k, out, err, exit_code)

    def test_there_are_some(self) -> None:
        self.assertTrue(self._stubs())

    def test_the_stub_as_given_does_not_pass(self) -> None:
        for k in self._stubs():
            with self.subTest(kata=k.id):
                outcome = self._run(k, k.start)
                if outcome.broke:
                    continue
                self.assertFalse(
                    outcome.passed,
                    f"{k.id} is meant to be unfinished and answers "
                    f"every case as it stands")

    def test_the_finished_version_passes(self) -> None:
        for k in self._stubs():
            with self.subTest(kata=k.id):
                outcome = self._run(k, k.reference())
                self.assertEqual(outcome.broke, "")
                failed = [
                    (r.args, r.got, r.want) for r in outcome.results
                    if not r.passed
                ]
                self.assertEqual(failed, [], f"{k.id}: {failed[:2]}")

    def test_there_is_a_program_around_the_stub(self) -> None:
        """More than the empty function, or it is not this shape.

        Measured as lines before the function being asked for: the
        constants, the helper, the comment saying how the page calls
        it. Three is a low bar and a stub that cannot clear it is a
        plain kata that has been filed in the wrong place.
        """
        for k in self._stubs():
            with self.subTest(kata=k.id):
                before = k.start.split(f"function {k.name}")[0]
                lines = [ln for ln in before.splitlines() if ln.strip()]
                self.assertGreaterEqual(
                    len(lines), 3,
                    f"{k.id} has {len(lines)} lines of program around it")

    def test_the_stub_defines_the_function_and_leaves_it_empty(
        self,
    ) -> None:
        for k in self._stubs():
            with self.subTest(kata=k.id):
                self.assertIn(f"function {k.name}(", k.start)
                self.assertIn("your code here", k.start)

    def test_each_one_says_what_to_take_away(self) -> None:
        for k in self._stubs():
            with self.subTest(kata=k.id):
                self.assertTrue(k.bug.strip())
