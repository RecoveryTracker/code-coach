"""The concept bank: the half of an interview that is not a coding problem.

There is no compiler to check prose, so these check the properties that make
an answer worth reading — that it says a mechanism rather than a definition,
that it is long enough to have said something and short enough to say out
loud, and that nothing is duplicated across topics.
"""

from __future__ import annotations

import unittest

from code_coach.concepts import payload, question_count, topic, topics


class CoverageTests(unittest.TestCase):
    def test_there_is_a_substantial_bank(self) -> None:
        self.assertGreaterEqual(len(topics()), 9)
        self.assertGreaterEqual(question_count(), 100)

    def test_every_topic_is_a_full_set(self) -> None:
        """A topic with three questions in it reads as unfinished."""
        for t in topics():
            with self.subTest(topic=t.id):
                self.assertGreaterEqual(len(t.questions), 10)

    def test_the_topics_a_systems_interview_asks_about(self) -> None:
        """The areas a systems or quant round actually covers, so nothing
        whole is missing."""
        have = {t.id for t in topics()}
        for wanted in (
            "cpp-semantics",
            "os-internals",
            "cpu-memory",
            "concurrency",
            "networking",
            "floating-point",
            "build-linking",
            "probability",
            "microstructure",
        ):
            with self.subTest(topic=wanted):
                self.assertIn(wanted, have)

    def test_lookup_handles_nothing(self) -> None:
        self.assertIsNone(topic("nonsense"))
        self.assertIsNotNone(topic("concurrency"))


class ShapeTests(unittest.TestCase):
    def test_every_topic_says_what_it_is(self) -> None:
        for t in topics():
            with self.subTest(topic=t.id):
                self.assertTrue(t.name.strip())
                self.assertGreater(len(t.blurb), 20)
                self.assertGreater(t.order, 0)

    def test_the_order_is_a_real_order(self) -> None:
        orders = sorted(t.order for t in topics())
        self.assertEqual(len(orders), len(set(orders)))

    def test_every_question_asks_something(self) -> None:
        for t in topics():
            for q in t.questions:
                with self.subTest(ask=q.ask[:40]):
                    self.assertGreater(len(q.ask), 15)
                    self.assertTrue(q.ask.rstrip().endswith("?"))

    def test_an_answer_says_a_mechanism_not_a_definition(self) -> None:
        """Short enough to say out loud, long enough to have said something.

        The lower bound is the real one: an answer of a single clause is a
        definition, and a definition is what the question already contains.
        """
        for t in topics():
            for q in t.questions:
                with self.subTest(ask=q.ask[:40]):
                    self.assertGreater(len(q.answer), 120)
                    self.assertLess(len(q.answer), 700)
                    self.assertIn(q.answer.strip()[-1], ".?")

    def test_a_follow_up_is_a_question_when_there_is_one(self) -> None:
        for t in topics():
            for q in t.questions:
                if not q.follow_up:
                    continue
                with self.subTest(ask=q.ask[:40]):
                    self.assertTrue(q.follow_up.rstrip().endswith("?"))
                    self.assertGreater(len(q.follow_up), 15)

    def test_some_questions_carry_a_follow_up(self) -> None:
        """Not all of them — but a bank with none has lost the idea."""
        with_follow_up = sum(
            1 for t in topics() for q in t.questions if q.follow_up
        )
        self.assertGreaterEqual(with_follow_up, 5)

    def test_no_question_is_asked_twice(self) -> None:
        asked = [q.ask for t in topics() for q in t.questions]
        self.assertEqual(len(asked), len(set(asked)))

    def test_no_answer_is_reused(self) -> None:
        """Two questions with the same answer means one of them is padding."""
        answers = [q.answer for t in topics() for q in t.questions]
        self.assertEqual(len(answers), len(set(answers)))

    def test_answers_are_written_as_prose(self) -> None:
        """It is meant to be said, so no bullet lists and no code blocks."""
        for t in topics():
            for q in t.questions:
                with self.subTest(ask=q.ask[:40]):
                    self.assertNotIn("\n-", q.answer)
                    self.assertNotIn("```", q.answer)
                    self.assertNotIn("  ", q.answer)


class PayloadTests(unittest.TestCase):
    def test_it_serialises_whole(self) -> None:
        data = payload()
        self.assertEqual(len(data), len(topics()))
        for entry in data:
            with self.subTest(topic=entry["id"]):
                self.assertTrue(entry["name"])
                self.assertTrue(entry["blurb"])
                self.assertTrue(entry["questions"])
                for question in entry["questions"]:
                    self.assertIn("ask", question)
                    self.assertIn("answer", question)
                    self.assertIn("follow_up", question)

    def test_it_comes_out_in_order(self) -> None:
        orders = [entry["order"] for entry in payload()]
        self.assertEqual(orders, sorted(orders))

    def test_the_endpoint_returns_it(self) -> None:
        from code_coach.api import server

        served = server.concepts()
        self.assertEqual(len(served), len(topics()))
        self.assertEqual(
            sum(len(t["questions"]) for t in served), question_count()
        )

    def test_it_is_offered_regardless_of_language(self) -> None:
        """Only the C++ topic is language-specific, and the rest are not, so
        this is not gated the way the code banks are."""
        from code_coach.api import server

        first = server.concepts()
        progress = server._store.load()
        progress.language = "sql"
        server._store.save(progress)
        self.assertEqual(len(server.concepts()), len(first))


if __name__ == "__main__":
    unittest.main()
