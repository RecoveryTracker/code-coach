"""Lessons: a problem taken from the question to a solution.

The rest of the study material says what a pattern is and hands over finished
code. A lesson is the part in between — the first thought anyone has, what it
costs, the observation that fixes it, and then the code assembled a stage at a
time. These check that it stays complete and stays honest.

Lessons are keyed by problem number. Every pattern has one it opens with (see
CANONICAL), and the rest of its problems fill in behind that.
"""

from __future__ import annotations

import unittest

from code_coach.leetcode.bank import lessons_catalogue, study_payload
from code_coach.leetcode.problems import PATTERNS, PATTERNS_BY_ID, all_problems
from code_coach.leetcode.worked import (
    CANONICAL,
    WORKED,
    worked_for,
    worked_for_problem,
)


def pattern_of(number: int) -> str:
    for pattern in PATTERNS:
        if any(p.number == number for p in pattern.problems):
            return pattern.id
    raise AssertionError(f"#{number} is in no pattern")


class CoverageTests(unittest.TestCase):
    def test_every_pattern_has_a_lesson_to_open_with(self) -> None:
        missing = [p.id for p in PATTERNS if p.id not in CANONICAL]
        self.assertEqual(missing, [])

    def test_the_opening_lesson_exists(self) -> None:
        for pattern_id, number in CANONICAL.items():
            with self.subTest(pattern=pattern_id):
                self.assertIn(number, WORKED)

    def test_the_opening_lesson_is_from_its_own_pattern(self) -> None:
        """Teaching hash maps by way of a tree problem would be a fine lesson
        and the wrong one to put here."""
        for pattern_id, number in CANONICAL.items():
            numbers = {p.number for p in PATTERNS_BY_ID[pattern_id].problems}
            with self.subTest(pattern=pattern_id):
                self.assertIn(number, numbers)

    def test_every_problem_has_its_own_lesson(self) -> None:
        """The fallback exists for a gap; there are no gaps left.

        A problem added without one still works — it borrows its pattern's —
        but it should be a decision rather than an oversight, so this says so.
        """
        missing = [p.number for p in all_problems() if p.number not in WORKED]
        self.assertEqual(missing, [])

    def test_every_lesson_belongs_to_a_real_problem(self) -> None:
        known = {p.number for p in all_problems()}
        self.assertEqual(sorted(n for n in WORKED if n not in known), [])

    def test_a_lesson_matches_the_problem_it_is_filed_under(self) -> None:
        for number, worked in WORKED.items():
            with self.subTest(problem=number):
                self.assertEqual(worked.problem, number)

    def test_the_problem_it_derives_has_a_brief(self) -> None:
        """The lesson assumes you have read the question."""
        from code_coach.leetcode.study import BRIEFS

        for number in WORKED:
            with self.subTest(problem=number):
                self.assertIn(number, BRIEFS)


class ShapeTests(unittest.TestCase):
    def test_a_lesson_has_all_of_its_parts(self) -> None:
        """Skip any one of them and it stops being a derivation: without the
        cost the naive version looks fine, and without the naive version the
        insight has nothing to be an insight about."""
        for number, worked in WORKED.items():
            with self.subTest(problem=number):
                # naive is often a single clause and finished: "Sort both
                # strings and compare them." The bar is against placeholders,
                # not against brevity. The other two carry the reasoning and
                # do need the room.
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
        """A lesson whose stages carry no code is prose, not a walkthrough."""
        for number, worked in WORKED.items():
            with self.subTest(problem=number):
                with_code = [s for s in worked.stages if s.code.strip()]
                self.assertGreaterEqual(len(with_code), 3)

    def test_stage_code_is_tidy(self) -> None:
        """It renders in a pre, so stray whitespace shows.

        A stage may open on an indented line when it continues a block from
        the stage before; what it must not carry is trailing whitespace or a
        tab.
        """
        for number, worked in WORKED.items():
            for i, stage in enumerate(worked.stages):
                if not stage.code:
                    continue
                with self.subTest(problem=number, stage=i):
                    self.assertEqual(stage.code, stage.code.rstrip())
                    self.assertNotIn("\t", stage.code)

    def test_a_lesson_is_readable_without_the_solution(self) -> None:
        for number, worked in WORKED.items():
            for i, stage in enumerate(worked.stages):
                with self.subTest(problem=number, stage=i):
                    self.assertNotIn("see above", stage.explain.lower())
                    self.assertNotIn("as shown", stage.explain.lower())


class PayloadTests(unittest.TestCase):
    def test_the_opening_lesson_reaches_the_client(self) -> None:
        for pattern in PATTERNS:
            number = CANONICAL[pattern.id]
            payload = study_payload(pattern.id, number, "python")
            with self.subTest(pattern=pattern.id):
                worked = payload["lesson"]["worked"]
                self.assertEqual(worked["problem"], number)
                self.assertTrue(worked["stages"])

    def test_a_problem_with_its_own_lesson_gets_that_one(self) -> None:
        """Not the pattern's opener — the one for the problem in hand."""
        for number in sorted(WORKED):
            payload = study_payload(pattern_of(number), number, "python")
            with self.subTest(problem=number):
                self.assertEqual(payload["lesson"]["worked"]["problem"], number)

    def test_a_problem_without_one_falls_back_to_the_pattern(self) -> None:
        """Better the pattern's lesson than a blank panel.

        Every problem in the bank now has its own lesson, so this can no
        longer be provoked with a real problem number — it used to loop over
        the unwritten ones and quietly did nothing once the last was written.
        A number that is deliberately not in the bank keeps the path covered
        for whenever a problem is added ahead of its lesson.
        """
        for pattern in PATTERNS:
            payload = study_payload(pattern.id, 999999, "python")
            with self.subTest(pattern=pattern.id):
                self.assertEqual(
                    payload["lesson"]["worked"]["problem"], CANONICAL[pattern.id]
                )

    def test_it_survives_the_api_schema(self) -> None:
        """StudyInfo is a pydantic model, so a field it does not declare is
        dropped silently on the way out."""
        from code_coach.api.schemas import StudyInfo

        raw = study_payload("lc-hashmap", 1, "python")
        shipped = StudyInfo(**raw).model_dump()
        self.assertIsNotNone(shipped["lesson"]["worked"])
        self.assertTrue(shipped["lesson"]["worked"]["stages"])

    def test_lookups_handle_nothing(self) -> None:
        self.assertIsNone(worked_for("lc-nonsense"))
        self.assertIsNone(worked_for(None))
        self.assertIsNone(worked_for_problem(None))
        self.assertIsNone(worked_for_problem(999999))


class CatalogueTests(unittest.TestCase):
    """The Lessons screen asks for the whole set, not the one you're on."""

    def test_it_serves_every_pattern_in_learning_order(self) -> None:
        entries = lessons_catalogue("python")
        self.assertEqual(len(entries), len(PATTERNS))
        orders = [e["order"] for e in entries]
        self.assertEqual(orders, sorted(orders))

    def test_each_entry_carries_its_lesson_and_its_problems(self) -> None:
        for entry in lessons_catalogue("python"):
            with self.subTest(pattern=entry["id"]):
                self.assertTrue(entry["summary"])
                self.assertTrue(entry["when"])
                self.assertTrue(entry["template"])
                self.assertIsNotNone(entry["worked"])
                self.assertEqual(len(entry["problems"]), 8)

    def test_each_problem_carries_its_own_lesson_where_there_is_one(self) -> None:
        for entry in lessons_catalogue("python"):
            for problem in entry["problems"]:
                with self.subTest(problem=problem["number"]):
                    if problem["number"] in WORKED:
                        self.assertIsNotNone(problem["worked"])
                        self.assertEqual(
                            problem["worked"]["problem"], problem["number"]
                        )
                    else:
                        self.assertIsNone(problem["worked"])

    def test_the_practice_list_links_to_the_real_questions(self) -> None:
        for entry in lessons_catalogue("python"):
            for problem in entry["problems"]:
                with self.subTest(problem=problem["number"]):
                    self.assertTrue(
                        problem["url"].startswith("https://leetcode.com/")
                    )
                    self.assertTrue(problem["statement"])

    def test_it_follows_the_language(self) -> None:
        for language in ("python", "javascript", "typescript", "dart"):
            with self.subTest(language=language):
                self.assertEqual(len(lessons_catalogue(language)), len(PATTERNS))

    def test_the_endpoint_returns_it(self) -> None:
        from code_coach.api import server

        entries = server.lessons("python")
        self.assertEqual(len(entries), len(PATTERNS))
        self.assertTrue(entries[0]["worked"]["stages"])

    def test_the_endpoint_takes_the_language_it_is_asked_for(self) -> None:
        """The Lessons screen has a picker on it now, so it names the language
        rather than waiting for the store to catch up with the switch that
        triggered the refetch."""
        from code_coach.api import server

        cpp = {e["id"] for e in server.lessons("cpp")}
        python = {e["id"] for e in server.lessons("python")}
        self.assertTrue(any(i.startswith("sys-") for i in cpp))
        self.assertFalse(any(i.startswith("sys-") for i in python))

    def test_an_unknown_language_falls_back_rather_than_failing(self) -> None:
        from code_coach.api import server

        self.assertEqual(
            len(server.lessons("klingon")), len(server.lessons(None))
        )


class GotoProblemTests(unittest.TestCase):
    """Clicking a problem in a lesson opens it in the editor.

    The window a problem lives in depends on the batch and the difficulty, so
    the jump has to work out which one holds it rather than assuming the
    first — otherwise the link lands you near the problem instead of on it.
    """

    def _server(self):
        import tempfile
        from pathlib import Path

        from code_coach.api import server
        from code_coach.progress.store import ProgressStore, active_store, use_store

        # use_store, not just server._store: the bank reads the
        # active store too, and if only one moves they answer
        # about different students.
        use_store(ProgressStore(Path(tempfile.mkdtemp()) / "p.json"))
        server._store = active_store()
        return server

    def test_it_lands_on_the_problem_asked_for(self) -> None:
        from code_coach.api import server as real_module
        from code_coach.api.schemas import GotoProblemRequest

        real = real_module._store
        try:
            server = self._server()
            for pattern in PATTERNS:
                for problem in pattern.problems[:3]:
                    session = server.practice_goto_problem(
                        GotoProblemRequest(
                            pattern_id=pattern.id, problem_number=problem.number
                        )
                    )
                    step = session.steps[session.jump_to_exercise]
                    with self.subTest(problem=problem.number):
                        self.assertEqual(session.class_id, pattern.id)
                        self.assertEqual(session.lesson_number, 1)
                        self.assertEqual(
                            step.study.problem.number, problem.number
                        )
        finally:
            real_module._store = real

    def test_it_works_at_every_difficulty(self) -> None:
        """The windows are cut differently at each chunk size."""
        from code_coach.api import server as real_module
        from code_coach.api.schemas import GotoProblemRequest

        real = real_module._store
        try:
            server = self._server()
            for level in (1, 3, 5):
                progress = server._store.load()
                progress.dictation_level = level
                server._store.save(progress)
                session = server.practice_goto_problem(
                    GotoProblemRequest(pattern_id="lc-dp", problem_number=152)
                )
                step = session.steps[session.jump_to_exercise]
                with self.subTest(level=level):
                    self.assertEqual(step.study.problem.number, 152)
        finally:
            real_module._store = real

    def test_a_language_without_solutions_says_so(self) -> None:
        """It used to answer with the fundamentals session instead.

        patterns_for_language falls back to Python's bank rather than
        failing, so the jump found a batch, saved the position, and then
        handed back a session with no problem in it at all. Clicking "Two
        Sum" in Rust landed you on println!("Hello, world!") with nothing
        said about why. Four of the eight languages did this.
        """
        from fastapi import HTTPException

        from code_coach.api import server as real_module
        from code_coach.api.schemas import GotoProblemRequest
        from code_coach.leetcode.bank import has_own_bank
        from code_coach.languages import LANGUAGES

        real = real_module._store
        try:
            server = self._server()
            for language in LANGUAGES:
                progress = server._store.load()
                progress.language = language.id
                server._store.save(progress)
                request = GotoProblemRequest(
                    pattern_id="lc-hashmap", problem_number=1
                )
                with self.subTest(language=language.id):
                    if has_own_bank(language.id):
                        session = server.practice_goto_problem(request)
                        step = session.steps[session.jump_to_exercise]
                        self.assertIsNotNone(step.study)
                        self.assertEqual(step.study.problem.number, 1)
                    else:
                        with self.assertRaises(HTTPException) as caught:
                            server.practice_goto_problem(request)
                        self.assertEqual(caught.exception.status_code, 409)
                        self.assertIn(
                            language.id, caught.exception.detail
                        )
        finally:
            real_module._store = real

    def test_the_screen_is_told_whether_the_link_will_work(self) -> None:
        """So it can show the title without pretending it is clickable."""
        from code_coach.leetcode.bank import has_own_bank, lessons_catalogue
        from code_coach.languages import LANGUAGES

        for language in LANGUAGES:
            entries = lessons_catalogue(language.id)
            with self.subTest(language=language.id):
                self.assertTrue(entries)
                for entry in entries:
                    self.assertEqual(
                        entry["can_open"], has_own_bank(language.id)
                    )
                    # The reading is worth showing either way.
                    self.assertEqual(len(entry["problems"]), 8)

    def test_a_problem_that_is_not_there_is_a_404(self) -> None:
        from fastapi import HTTPException

        from code_coach.api import server as real_module
        from code_coach.api.schemas import GotoProblemRequest

        real = real_module._store
        try:
            server = self._server()
            with self.assertRaises(HTTPException) as caught:
                server.practice_goto_problem(
                    GotoProblemRequest(pattern_id="lc-dp", problem_number=99999)
                )
            self.assertEqual(caught.exception.status_code, 404)
        finally:
            real_module._store = real

    def test_arriving_any_other_way_does_not_jump(self) -> None:
        """jump_to_exercise is the lesson link's business only; every other
        route wants wherever you left off."""
        from code_coach.api import server as real_module

        real = real_module._store
        try:
            server = self._server()
            self.assertIsNone(server.practice_current().jump_to_exercise)
        finally:
            real_module._store = real


if __name__ == "__main__":
    unittest.main()
