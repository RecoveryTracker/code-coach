"""The systems study material: briefs, pattern lessons and derivations.

The bank hands over a finished spinlock, which teaches what one looks like
and nothing about why it is shaped that way. These check that the reading
which fills that gap is actually there and actually complete — every problem
has a brief and a derivation, every derivation has all four of its parts, and
the study panel really serves them.

The bar is the LeetCode lessons' bar, because it is the same shape and the
same job.
"""

from __future__ import annotations

import unittest

from code_coach.systems import patterns_for_language
from code_coach.systems.study import BRIEFS, LESSONS, brief_for, lesson_for
from code_coach.systems.worked import CANONICAL, WORKED, worked_for, worked_for_problem

CPP = patterns_for_language("cpp")
ALL_PROBLEMS = [p for pattern in CPP for p in pattern.problems]


class CoverageTests(unittest.TestCase):
    def test_every_class_has_a_lesson(self) -> None:
        for pattern in CPP:
            with self.subTest(pattern=pattern.id):
                self.assertIn(pattern.id, LESSONS)

    def test_every_problem_has_a_brief(self) -> None:
        """Without one the study panel has nothing to say about the exercise
        you are actually typing."""
        missing = [p.number for p in ALL_PROBLEMS if p.number not in BRIEFS]
        self.assertEqual(missing, [])

    def test_every_problem_has_a_derivation(self) -> None:
        """This is the gap these exist to close: the finished primitive
        without the reasoning is the half that does not transfer."""
        missing = [p.number for p in ALL_PROBLEMS if p.number not in WORKED]
        self.assertEqual(missing, [])

    def test_nothing_is_written_for_a_problem_that_does_not_exist(self) -> None:
        known = {p.number for p in ALL_PROBLEMS}
        self.assertEqual(sorted(n for n in WORKED if n not in known), [])
        self.assertEqual(sorted(n for n in BRIEFS if n not in known), [])

    def test_every_class_opens_with_one_of_its_own(self) -> None:
        """Teaching the memory class with a market problem would be a fine
        lesson and the wrong one to put here."""
        for pattern in CPP:
            with self.subTest(pattern=pattern.id):
                self.assertIn(pattern.id, CANONICAL)
                numbers = {p.number for p in pattern.problems}
                self.assertIn(CANONICAL[pattern.id], numbers)

    def test_a_derivation_is_filed_under_its_own_problem(self) -> None:
        for number, worked in WORKED.items():
            with self.subTest(problem=number):
                self.assertEqual(worked.problem, number)


class ShapeTests(unittest.TestCase):
    def test_a_lesson_has_all_of_its_parts(self) -> None:
        for pattern_id, lesson in LESSONS.items():
            with self.subTest(pattern=pattern_id):
                self.assertGreater(len(lesson.summary), 80)
                self.assertGreater(len(lesson.when), 40)
                self.assertTrue(lesson.template.strip())
                self.assertGreaterEqual(len(lesson.steps), 3)
                self.assertGreaterEqual(len(lesson.pitfalls), 2)

    def test_a_brief_says_what_to_build(self) -> None:
        for number, brief in BRIEFS.items():
            with self.subTest(problem=number):
                self.assertGreater(len(brief.statement), 60)
                self.assertTrue(brief.statement.strip().endswith("."))

    def test_a_derivation_has_all_of_its_parts(self) -> None:
        """Skip any one and it stops being a derivation: without the cost the
        first attempt looks fine, and without the first attempt the insight
        has nothing to be an insight about."""
        for number, worked in WORKED.items():
            with self.subTest(problem=number):
                self.assertGreater(len(worked.naive), 20)
                for field in ("naive", "why_not", "insight"):
                    text = getattr(worked, field)
                    self.assertIn(text.strip()[-1], ".?")
                for field in ("why_not", "insight"):
                    self.assertGreater(len(getattr(worked, field)), 60, field)
                self.assertGreaterEqual(len(worked.stages), 3)

    def test_every_stage_explains_itself(self) -> None:
        for number, worked in WORKED.items():
            for i, stage in enumerate(worked.stages):
                with self.subTest(problem=number, stage=i):
                    self.assertGreater(len(stage.explain), 20)

    def test_the_stages_build_towards_something(self) -> None:
        """A derivation whose stages carry no code is prose, not a
        walkthrough. A closing stage may be commentary with none."""
        for number, worked in WORKED.items():
            with self.subTest(problem=number):
                with_code = [s for s in worked.stages if s.code.strip()]
                self.assertGreaterEqual(len(with_code), 3)

    def test_stage_code_is_tidy(self) -> None:
        for number, worked in WORKED.items():
            for i, stage in enumerate(worked.stages):
                if not stage.code:
                    continue
                with self.subTest(problem=number, stage=i):
                    self.assertEqual(stage.code, stage.code.rstrip())
                    self.assertNotIn("\t", stage.code)

    def test_no_two_problems_share_a_derivation(self) -> None:
        insights = [w.insight for w in WORKED.values()]
        self.assertEqual(len(insights), len(set(insights)))

    def test_no_two_problems_share_a_brief(self) -> None:
        statements = [b.statement for b in BRIEFS.values()]
        self.assertEqual(len(statements), len(set(statements)))

    def test_lookups_handle_nothing(self) -> None:
        self.assertIsNone(lesson_for(None))
        self.assertIsNone(lesson_for("sys-nonsense"))
        self.assertIsNone(brief_for(None))
        self.assertIsNone(brief_for(999999))
        self.assertIsNone(worked_for(None))
        self.assertIsNone(worked_for_problem(None))
        self.assertIsNone(worked_for_problem(999999))


class PayloadTests(unittest.TestCase):
    def test_the_study_panel_serves_a_systems_problem(self) -> None:
        from code_coach.leetcode.bank import study_payload

        for pattern in CPP:
            for problem in pattern.problems:
                payload = study_payload(pattern.id, problem.number, "cpp")
                with self.subTest(problem=problem.number):
                    self.assertIsNotNone(payload)
                    self.assertIsNotNone(payload["problem"])
                    self.assertIsNotNone(payload["lesson"])
                    self.assertEqual(
                        payload["problem"]["number"], problem.number
                    )
                    self.assertEqual(payload["problem"]["title"], problem.title)
                    self.assertEqual(
                        payload["lesson"]["worked"]["problem"], problem.number
                    )

    def test_it_carries_no_leetcode_url(self) -> None:
        """These are not LeetCode problems and there is nowhere to send you.
        An empty string rather than a link to something unrelated."""
        from code_coach.leetcode.bank import study_payload

        payload = study_payload("sys-memory", 9101, "cpp")
        self.assertEqual(payload["problem"]["url"], "")

    def test_it_follows_the_language(self) -> None:
        """The solution shown must be the one on screen, not C++'s."""
        from code_coach.leetcode.bank import study_payload

        for language in ("cpp", "rust", "c"):
            payload = study_payload("sys-lockfree", 9303, language)
            with self.subTest(language=language):
                self.assertIsNotNone(payload)
                solution = payload["problem"]["solution"]
                if language == "rust":
                    self.assertIn("pub fn", solution)
                elif language == "cpp":
                    self.assertIn("template", solution)
                else:
                    self.assertIn("static bool", solution)

    def test_the_leetcode_side_is_untouched(self) -> None:
        """The routing must not have broken the family it forked from."""
        from code_coach.leetcode.bank import study_payload

        payload = study_payload("lc-hashmap", 1, "python")
        self.assertIsNotNone(payload)
        self.assertEqual(payload["problem"]["title"], "Two Sum")
        self.assertTrue(payload["problem"]["url"].startswith("https://"))
        self.assertEqual(payload["lesson"]["worked"]["problem"], 1)

    def test_a_systems_problem_falls_back_to_its_class_lesson(self) -> None:
        """Every problem has its own today; this keeps the path honest for
        one added before its derivation is written."""
        from code_coach.leetcode.bank import study_payload

        payload = study_payload("sys-memory", 999999, "cpp")
        self.assertIsNotNone(payload)
        self.assertEqual(
            payload["lesson"]["worked"]["problem"], CANONICAL["sys-memory"]
        )


class CatalogueTests(unittest.TestCase):
    """The Lessons screen, not just the study panel.

    The derivations were reachable only while typing the exercise, which is
    backwards — the reading is what you want before you start.
    """

    def test_the_systems_classes_are_on_the_lessons_screen(self) -> None:
        from code_coach.leetcode.bank import lessons_catalogue

        listed = {
            e["id"]
            for e in lessons_catalogue("cpp")
            if e["id"].startswith("sys-")
        }
        self.assertEqual(listed, {p.id for p in CPP})

    def test_every_listed_problem_carries_its_derivation(self) -> None:
        from code_coach.leetcode.bank import lessons_catalogue

        for entry in lessons_catalogue("cpp"):
            if not entry["id"].startswith("sys-"):
                continue
            for problem in entry["problems"]:
                with self.subTest(problem=problem["number"]):
                    self.assertIsNotNone(problem["worked"])
                    self.assertEqual(
                        problem["worked"]["problem"], problem["number"]
                    )
                    self.assertTrue(problem["statement"])
                    self.assertEqual(problem["url"], "")

    def test_a_language_without_them_is_listed_none(self) -> None:
        from code_coach.leetcode.bank import lessons_catalogue
        from code_coach.languages import LANGUAGES
        from code_coach.systems import has_systems

        for language in LANGUAGES:
            listed = {
                e["id"]
                for e in lessons_catalogue(language.id)
                if e["id"].startswith("sys-")
            }
            with self.subTest(language=language.id):
                if has_systems(language.id):
                    self.assertTrue(listed)
                else:
                    self.assertEqual(listed, set())

    def test_the_leetcode_entries_survived_the_change(self) -> None:
        """The builder was made to serve two families; the first one has to
        come out exactly as it did."""
        from code_coach.leetcode.bank import lessons_catalogue
        from code_coach.leetcode.problems import PATTERNS

        entries = [
            e for e in lessons_catalogue("python") if not e["id"].startswith("sys-")
        ]
        self.assertEqual(len(entries), len(PATTERNS))
        for entry in entries:
            with self.subTest(pattern=entry["id"]):
                self.assertEqual(len(entry["problems"]), 8)
                self.assertTrue(
                    entry["problems"][0]["url"].startswith("https://")
                )

    def test_everything_is_in_learning_order(self) -> None:
        from code_coach.leetcode.bank import lessons_catalogue

        orders = [e["order"] for e in lessons_catalogue("cpp")]
        self.assertEqual(orders, sorted(orders))


if __name__ == "__main__":
    unittest.main()
