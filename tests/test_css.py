"""The CSS quizzes.

What this file can and cannot do is worth being blunt about. It cannot
check that an answer is right: there is no browser engine here, and the
partial ones get the cascade wrong often enough that agreeing with one
would be worse evidence than none. tools/verify_css.py does that job by
asking Chromium, and the answers in the content files were copied out of
its output.

So the load-bearing tests here are in VerifiedTests, which hold every
quiz to that browser run: the answer has to match what Chromium
returned, and the hash of the document Chromium measured has to match
the document in the content file now, so a quiz that has been edited
since fails until somebody opens a browser again.

Everything else is about the questions being answerable - a target that
matches one element, a set of choices that does not give the answer
away, an explanation long enough to explain something - and about the
payload not stating the answer it is asking for.
"""

from __future__ import annotations

import unittest

from code_coach.css import css_families, quiz, quizzes


class ShapeTests(unittest.TestCase):
    def test_there_are_some_in_every_family(self) -> None:
        self.assertGreaterEqual(len(quizzes()), 20)
        for family in css_families():
            with self.subTest(family=family):
                self.assertGreaterEqual(len(quizzes(family)), 4)

    def test_ids_are_unique(self) -> None:
        ids = [q.id for q in quizzes()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_quiz_is_findable_by_id(self) -> None:
        for q in quizzes():
            with self.subTest(quiz=q.id):
                self.assertIs(quiz(q.id), q)

    def test_the_target_matches_exactly_one_element(self) -> None:
        """Not a real selector match - there is nothing here to match
        with - but the whole convention is an id, and an id that is in
        the markup twice or not at all is the way this goes wrong.

        A quiz whose target matched two elements would have an answer
        that depends on which one the reader looked at, and the verifier
        refuses to measure it. This catches the same mistake earlier and
        without a browser.
        """
        for q in quizzes():
            with self.subTest(quiz=q.id):
                self.assertTrue(
                    q.target.startswith("#"),
                    f"{q.id} targets {q.target!r}, which is not an id")
                attribute = f'id="{q.target[1:]}"'
                self.assertEqual(
                    q.html.count(attribute), 1,
                    f"{q.id}: {attribute} appears "
                    f"{q.html.count(attribute)} times in the markup")

    def test_the_property_is_one_the_verifier_can_measure(self) -> None:
        """Three kinds, and the list is closed on purpose.

        A computed property; `rect.width`/`rect.height` for the space
        the element really takes, which is the question wherever the
        computed property reports the declaration and means nothing;
        and `dom.*` for what the parser built rather than how it was
        painted. Anything else reaches the verifier as "unknown
        measurement" and the quiz can never agree with a browser - a
        typo in a property name should fail here rather than there.
        """
        measurable = {
            "rect.width", "rect.height",
            "dom.parentTag", "dom.childCount", "dom.tag", "dom.text",
        }
        for q in quizzes():
            with self.subTest(quiz=q.id):
                if "." in q.prop:
                    self.assertIn(q.prop, measurable)
                else:
                    self.assertRegex(q.prop, r"^[a-z-]+$")


class ChoiceTests(unittest.TestCase):
    """The answer has to be hidden among the choices, not findable from
    their shape. A single distractor, a duplicate, or a right answer
    that is the only one of its kind all turn the question into a
    guess that works."""

    def test_there_is_something_to_choose_between(self) -> None:
        for q in quizzes():
            with self.subTest(quiz=q.id):
                self.assertGreaterEqual(len(q.choices), 2)

    def test_the_answer_is_among_the_choices(self) -> None:
        for q in quizzes():
            with self.subTest(quiz=q.id):
                self.assertIn(q.expect, q.choices)

    def test_the_distractors_are_not_the_answer(self) -> None:
        for q in quizzes():
            with self.subTest(quiz=q.id):
                self.assertNotIn(q.expect, q.distractors)
                self.assertEqual(
                    len(set(q.distractors)), len(q.distractors),
                    f"{q.id} lists the same wrong answer twice")

    def test_the_choices_are_the_same_kind_of_thing(self) -> None:
        """A colour question whose choices are three colours and a
        length is answerable without reading the CSS. The cheap version
        of that check: everything that looks like a length among the
        choices, or nothing does."""
        for q in quizzes():
            with self.subTest(quiz=q.id):
                colours = [c for c in q.choices if c.startswith("rgb")]
                self.assertIn(
                    len(colours), (0, len(q.choices)),
                    f"{q.id} mixes colours and non-colours in its "
                    f"choices, so the odd one out is visible")

    def test_the_order_gives_nothing_away(self) -> None:
        """Choices are sorted, so the answer's position is decided by
        the alphabet rather than by the author. Without this the right
        answer tends to be the first one written, and a reader picks up
        on that long before they notice they have."""
        for q in quizzes():
            with self.subTest(quiz=q.id):
                self.assertEqual(list(q.choices), sorted(q.choices))


class ExplanationTests(unittest.TestCase):
    def test_every_quiz_explains_itself(self) -> None:
        """A wrong guess with no explanation teaches only that you were
        wrong. The length floor is crude and it is the thing that
        actually stops a one-line why from being left in."""
        for q in quizzes():
            with self.subTest(quiz=q.id):
                self.assertGreater(
                    len(q.why), 150,
                    f"{q.id}'s explanation is too short to explain")
                self.assertTrue(q.name.strip())

    def test_the_ranking_was_done(self) -> None:
        """There is no measure of surprisingness to compute, so what is
        checked is that somebody sorted them rather than that the sort
        is right: a family whose quizzes all share one level has been
        left at the default."""
        for family in css_families():
            with self.subTest(family=family):
                levels = {q.level for q in quizzes(family)}
                self.assertGreater(len(levels), 1)
                for level in levels:
                    self.assertIn(level, range(1, 6))

    def test_families_come_back_easiest_first(self) -> None:
        for family in css_families():
            with self.subTest(family=family):
                levels = [q.level for q in quizzes(family)]
                self.assertEqual(levels, sorted(levels))


class PageTests(unittest.TestCase):
    def test_the_page_holds_the_markup_and_the_styles(self) -> None:
        for q in quizzes():
            with self.subTest(quiz=q.id):
                page = q.page()
                self.assertIn(q.html, page)
                if q.css:
                    self.assertIn(q.css, page)
                self.assertTrue(page.startswith("<!doctype html>"))


class VerifiedTests(unittest.TestCase):
    """The load-bearing one: every answer was seen in a browser, and
    the page the browser saw is the page that is here now.

    The first version of this test asked whether every quiz appeared in
    the page that tools/verify_css.py generates - and could never fail,
    because that page is generated by walking the same list the test
    walks. It proved the loop ran.

    What proves something is the record: verified.json holds what
    Chromium actually returned, keyed by a hash of the exact document
    it measured. So changing a quiz's markup, styles or property
    changes the hash, the record no longer describes the quiz in front
    of it, and the test fails until somebody opens a browser again.
    That is the same discipline as the katas - the expected answer has
    to come from somewhere other than the thing being checked - with a
    browser standing in for the person.
    """

    def setUp(self) -> None:
        import json
        import pathlib

        here = pathlib.Path(__file__).resolve().parents[1]
        data = json.loads(
            (here / "code_coach" / "css" / "verified.json").read_text(
                encoding="utf-8"))
        self.record = {r["id"]: r for r in data["record"]}

    def _sha(self, q) -> str:
        import hashlib

        return hashlib.sha256(q.page().encode("utf-8")).hexdigest()

    def test_every_quiz_was_measured(self) -> None:
        for q in quizzes():
            with self.subTest(quiz=q.id):
                self.assertIn(
                    q.id, self.record,
                    f"{q.id} has never been through a browser: run "
                    f"tools/verify_css.py and record what it says")

    def test_the_browser_agreed_with_the_recorded_answer(self) -> None:
        for q in quizzes():
            if q.id not in self.record:
                continue
            with self.subTest(quiz=q.id):
                self.assertEqual(
                    q.expect, self.record[q.id]["browser_value"],
                    f"{q.id} claims {q.expect!r} and the browser said "
                    f"{self.record[q.id]['browser_value']!r}")

    def test_the_measurement_is_of_this_version_of_the_quiz(self) -> None:
        """A stale record is worse than none - it reads as evidence for
        an answer nobody checked."""
        for q in quizzes():
            if q.id not in self.record:
                continue
            with self.subTest(quiz=q.id):
                self.assertEqual(
                    self._sha(q), self.record[q.id]["page_sha256"],
                    f"{q.id} has changed since it was measured: run "
                    f"tools/verify_css.py again")
                self.assertEqual(q.prop, self.record[q.id]["prop"])

    def test_the_record_has_nothing_stale_in_it(self) -> None:
        """A deleted quiz leaving its row behind is how a record starts
        being trusted for things it does not cover."""
        live = {q.id for q in quizzes()}
        self.assertEqual(set(self.record) - live, set())


class RouteTests(unittest.TestCase):
    """What the screen is actually served.

    The tests above check the quizzes. These check the payload, which
    is a different thing and has its own way of going wrong: the answer
    riding along in the list is the one that would quietly ruin the
    mode, and no test of the content files can see it.
    """

    def _list(self):
        from code_coach.api import server

        return server.css_list()

    def _check(self, quiz_id: str, choice: str):
        from code_coach.api import server
        from code_coach.api.schemas import CssCheckRequest

        return server.css_check(
            CssCheckRequest(quiz_id=quiz_id, choice=choice))

    def test_the_list_is_grouped_and_complete(self) -> None:
        served = self._list()
        names = [f["name"] for f in served["families"]]
        self.assertEqual(names, list(css_families()))
        count = sum(len(f["quizzes"]) for f in served["families"])
        self.assertEqual(count, len(quizzes()))

    def test_the_answer_does_not_ride_along_in_the_list(self) -> None:
        """The one that matters. Everything else about this mode works
        and means nothing if the payload states the answer: a person
        with the network tab open is no longer being asked a question.

        What is checked is that no field *says* the answer. The first
        version also asserted the answer's text appeared nowhere in the
        document, and that rule cannot be satisfied: `width: 200px` is
        in the stylesheet of the question whose answer is 200px, and a
        colour question's stylesheet says green. The document is the
        question - it is supposed to contain everything the answer is
        derived from. Deriving it is the exercise. An `expect` field
        would skip the derivation, and that is the difference this
        test is about.
        """
        served = self._list()
        for family in served["families"]:
            for row in family["quizzes"]:
                with self.subTest(quiz=row["id"]):
                    self.assertNotIn("expect", row)
                    self.assertNotIn("why", row)
                    self.assertNotIn("distractors", row)

    def test_the_choices_served_are_the_sorted_ones(self) -> None:
        """Sorted by the quiz, not by the route. If the payload ever
        built its own list the answer's position would go back to being
        decided by whoever wrote the question."""
        served = self._list()
        for family in served["families"]:
            for row in family["quizzes"]:
                with self.subTest(quiz=row["id"]):
                    self.assertEqual(
                        row["choices"], list(quiz(row["id"]).choices))

    def test_the_right_choice_passes_and_a_wrong_one_does_not(self) -> None:
        for q in quizzes():
            with self.subTest(quiz=q.id):
                self.assertTrue(self._check(q.id, q.expect).passed)
                for wrong in q.distractors:
                    self.assertFalse(self._check(q.id, wrong).passed)

    def test_the_explanation_comes_back_either_way(self) -> None:
        q = quizzes()[0]
        self.assertTrue(self._check(q.id, q.expect).why)
        self.assertTrue(self._check(q.id, q.distractors[0]).why)

    def test_an_unknown_quiz_is_a_404_rather_than_a_crash(self) -> None:
        from fastapi import HTTPException

        with self.assertRaises(HTTPException) as caught:
            self._check("no-such-quiz", "anything")
        self.assertEqual(caught.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
