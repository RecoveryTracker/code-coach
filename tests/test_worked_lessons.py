"""Lessons: one problem per pattern, taken from the question to a solution.

The rest of the study material says what a pattern is and hands over finished
code. A lesson is the part in between — the first thought anyone has, what it
costs, the observation that fixes it, and then the code assembled a stage at a
time. These check that it stays complete and stays honest.
"""

from __future__ import annotations

import unittest

from code_coach.leetcode.bank import study_payload
from code_coach.leetcode.problems import PATTERNS, PATTERNS_BY_ID, all_problems
from code_coach.leetcode.worked import WORKED, worked_for


class CoverageTests(unittest.TestCase):
    def test_every_pattern_has_a_lesson(self) -> None:
        missing = [p.id for p in PATTERNS if p.id not in WORKED]
        self.assertEqual(missing, [], "write a Worked entry for these")

    def test_every_lesson_belongs_to_a_pattern(self) -> None:
        known = {p.id for p in PATTERNS}
        self.assertEqual(sorted(k for k in WORKED if k not in known), [])

    def test_a_lesson_derives_a_problem_from_its_own_pattern(self) -> None:
        """Teaching hash maps by way of a tree problem would be a fine lesson
        and the wrong one to put here."""
        for pattern_id, worked in WORKED.items():
            numbers = {p.number for p in PATTERNS_BY_ID[pattern_id].problems}
            with self.subTest(pattern=pattern_id):
                self.assertIn(worked.problem, numbers)

    def test_the_problem_it_derives_has_a_brief(self) -> None:
        """The lesson assumes you have read the question."""
        from code_coach.leetcode.study import BRIEFS

        for pattern_id, worked in WORKED.items():
            with self.subTest(pattern=pattern_id):
                self.assertIn(worked.problem, BRIEFS)


class ShapeTests(unittest.TestCase):
    def test_a_lesson_has_all_four_parts(self) -> None:
        """Skip any one of them and it stops being a derivation: without the
        cost the naive version looks fine, and without the naive version the
        insight has nothing to be an insight about."""
        for pattern_id, worked in WORKED.items():
            with self.subTest(pattern=pattern_id):
                for field in ("naive", "why_not", "insight"):
                    text = getattr(worked, field)
                    self.assertGreater(len(text), 40, field)
                    self.assertIn(text.strip()[-1], ".?")
                self.assertGreaterEqual(len(worked.stages), 3)

    def test_every_stage_explains_itself(self) -> None:
        for pattern_id, worked in WORKED.items():
            for i, stage in enumerate(worked.stages):
                with self.subTest(pattern=pattern_id, stage=i):
                    self.assertGreater(len(stage.explain), 20)

    def test_the_stages_build_towards_something(self) -> None:
        """A lesson whose stages carry no code is prose, not a walkthrough."""
        for pattern_id, worked in WORKED.items():
            with self.subTest(pattern=pattern_id):
                with_code = [s for s in worked.stages if s.code.strip()]
                self.assertGreaterEqual(len(with_code), 3)

    def test_stage_code_is_not_indented_by_accident(self) -> None:
        """It renders in a pre, so a stray leading space is visible."""
        for pattern_id, worked in WORKED.items():
            for i, stage in enumerate(worked.stages):
                if not stage.code:
                    continue
                with self.subTest(pattern=pattern_id, stage=i):
                    first = stage.code.splitlines()[0]
                    self.assertEqual(first, first.lstrip())
                    self.assertEqual(stage.code, stage.code.rstrip())

    def test_a_lesson_is_readable_without_the_solution(self) -> None:
        """No stage should point at something only the finished code shows."""
        for pattern_id, worked in WORKED.items():
            for i, stage in enumerate(worked.stages):
                with self.subTest(pattern=pattern_id, stage=i):
                    self.assertNotIn("see above", stage.explain.lower())
                    self.assertNotIn("as shown", stage.explain.lower())


class PayloadTests(unittest.TestCase):
    def test_the_lesson_reaches_the_client(self) -> None:
        for pattern in PATTERNS:
            first = pattern.problems[0].number
            payload = study_payload(pattern.id, first, "python")
            with self.subTest(pattern=pattern.id):
                self.assertIsNotNone(payload)
                worked = payload["lesson"]["worked"]
                self.assertEqual(worked["problem"], WORKED[pattern.id].problem)
                self.assertTrue(worked["stages"])
                self.assertIn("explain", worked["stages"][0])

    def test_it_is_the_same_lesson_in_every_language(self) -> None:
        """The reasoning does not change with the syntax, and the stages are
        written in the neutral style the templates already use."""
        for language in ("python", "javascript", "typescript", "dart"):
            payload = study_payload("lc-dp", 70, language)
            with self.subTest(language=language):
                self.assertEqual(
                    payload["lesson"]["worked"]["problem"],
                    WORKED["lc-dp"].problem,
                )

    def test_it_survives_the_api_schema(self) -> None:
        """StudyInfo is a pydantic model, so a field it does not declare is
        dropped silently on the way out. The lesson reached study_payload and
        vanished before the client, and nothing failed — this is the test that
        would have caught it."""
        from code_coach.api.schemas import StudyInfo

        raw = study_payload("lc-hashmap", 1, "python")
        shipped = StudyInfo(**raw).model_dump()
        self.assertIsNotNone(
            shipped["lesson"]["worked"],
            "declare the field in schemas.py or pydantic drops it",
        )
        self.assertTrue(shipped["lesson"]["worked"]["stages"])

    def test_a_pattern_with_no_lesson_returns_none(self) -> None:
        self.assertIsNone(worked_for("lc-nonsense"))
        self.assertIsNone(worked_for(None))


class ContentTests(unittest.TestCase):
    def test_the_derived_problems_are_spread_across_the_bank(self) -> None:
        """Thirteen lessons all deriving the same problem would technically
        pass everything above."""
        derived = {w.problem for w in WORKED.values()}
        self.assertEqual(len(derived), len(WORKED))

    def test_each_derived_problem_exists(self) -> None:
        numbers = {p.number for p in all_problems()}
        for pattern_id, worked in WORKED.items():
            with self.subTest(pattern=pattern_id):
                self.assertIn(worked.problem, numbers)


class CatalogueTests(unittest.TestCase):
    """The Lessons screen asks for the whole set, not the one you're on."""

    def test_it_serves_every_pattern_in_learning_order(self) -> None:
        from code_coach.leetcode.bank import lessons_catalogue

        entries = lessons_catalogue("python")
        self.assertEqual(len(entries), len(PATTERNS))
        orders = [e["order"] for e in entries]
        self.assertEqual(orders, sorted(orders))

    def test_each_entry_carries_its_lesson_and_its_problems(self) -> None:
        from code_coach.leetcode.bank import lessons_catalogue

        for entry in lessons_catalogue("python"):
            with self.subTest(pattern=entry["id"]):
                self.assertTrue(entry["summary"])
                self.assertTrue(entry["when"])
                self.assertTrue(entry["template"])
                self.assertIsNotNone(entry["worked"])
                self.assertTrue(entry["worked"]["title"])
                self.assertTrue(entry["worked"]["statement"])
                self.assertEqual(len(entry["problems"]), 8)

    def test_the_practice_list_links_to_the_real_questions(self) -> None:
        from code_coach.leetcode.bank import lessons_catalogue

        for entry in lessons_catalogue("python"):
            for problem in entry["problems"]:
                with self.subTest(problem=problem["number"]):
                    self.assertTrue(
                        problem["url"].startswith("https://leetcode.com/")
                    )

    def test_it_follows_the_language(self) -> None:
        """The problems listed should be the ones that language can serve."""
        from code_coach.leetcode.bank import lessons_catalogue

        for language in ("python", "javascript", "typescript", "dart"):
            with self.subTest(language=language):
                self.assertEqual(len(lessons_catalogue(language)), len(PATTERNS))

    def test_the_endpoint_returns_it(self) -> None:
        from code_coach.api import server

        entries = server.lessons()
        self.assertEqual(len(entries), len(PATTERNS))
        self.assertTrue(entries[0]["worked"]["stages"])


if __name__ == "__main__":
    unittest.main()
