"""The workbook: pages of exercises you solve by typing.

The claim this file has to hold up is narrow and load-bearing: every exercise
is solvable, and the output it demands is the output a correct program
actually produces. That cannot be asserted by reading the data — the expected
output is worked out in Python and the student's answer is run by a compiler,
so the only honest check is to run the reference program and compare.

The compiled languages are checked one exercise per shape rather than all 108,
because within a shape only the numbers differ and each extra one is another
compile. The shape is what could be wrong; the numbers are checked in full by
the languages that run in milliseconds.
"""

from __future__ import annotations

import unittest

from code_coach.engine import run_code
from code_coach.workbook import (
    exercise_count,
    expected_output,
    has_workbook,
    matches,
    normalise,
    page,
    pages,
)
from code_coach.workbook.emit import LANGUAGES, all_shape_ids

ALL = [(p, e) for p in pages() for e in p.exercises]

# Fast enough to run every exercise: no compiler in the loop.
INTERPRETED = ("python", "javascript")
# Everything else gets one exercise per shape it actually has.
OTHERS = tuple(lang for lang in LANGUAGES if lang not in INTERPRETED)


def _one_per_shape(language: str | None = None):
    """One exercise for each shape, out of the pages this language has.

    Pages 12 onwards exist in three languages only, so asking C for one of
    those would be asking for a reference that was never meant to exist.
    """
    seen: dict[str, tuple] = {}
    for p in pages(language):
        for e in p.exercises:
            seen.setdefault(e.shape, (p, e))
    return list(seen.values())


class ShapeTests(unittest.TestCase):
    def test_there_is_a_workbook_worth_working_through(self) -> None:
        self.assertGreaterEqual(len(pages()), 9)
        self.assertGreaterEqual(exercise_count(), 100)

    def test_a_page_is_a_dozen_goes_at_one_thing(self) -> None:
        """Three exercises is a demonstration. The repetition is the method."""
        for p in pages():
            with self.subTest(page=p.id):
                self.assertGreaterEqual(len(p.exercises), 10)
                shapes = {e.shape for e in p.exercises}
                self.assertEqual(len(shapes), 1, f"{p.id} mixes {shapes}")

    def test_the_pages_are_in_order_and_numbered_once_each(self) -> None:
        numbers = [p.number for p in pages()]
        self.assertEqual(numbers, sorted(numbers))
        self.assertEqual(len(numbers), len(set(numbers)))

    def test_every_page_says_what_it_adds(self) -> None:
        for p in pages():
            with self.subTest(page=p.id):
                self.assertGreater(len(p.teaches), 20)
                self.assertGreater(len(p.example), 60)

    def test_every_exercise_asks_for_something_specific(self) -> None:
        for p, e in ALL:
            with self.subTest(exercise=e.id):
                self.assertGreater(len(e.prompt), 20)
                self.assertTrue(e.prompt.strip().endswith("."))

    def test_an_exercise_prints_something_unless_that_is_the_point(self) -> None:
        """Printing nothing is a real answer on the conditional pages — the
        condition does not hold, so the body never runs. Anywhere else an
        empty expectation is a mistake in the data."""
        allowed = {"only-when", "list-filter"}
        for p, e in ALL:
            if p.id in allowed:
                continue
            with self.subTest(exercise=e.id):
                self.assertTrue(e.expect.strip(), "prints nothing")

    def test_the_pages_that_allow_it_really_use_it(self) -> None:
        """If none of them printed nothing, the exemption above would be
        quietly covering a page that no longer needs it."""
        from code_coach.workbook import page as find_page

        for page_id in ("only-when", "list-filter"):
            with self.subTest(page=page_id):
                found = find_page(page_id)
                self.assertTrue(
                    any(e.expect == "" for e in found.exercises),
                    "no exercise here prints nothing any more",
                )

    def test_no_exercise_id_is_used_twice(self) -> None:
        ids = [e.id for _, e in ALL]
        self.assertEqual(len(ids), len(set(ids)))

    def test_no_two_exercises_on_a_page_are_the_same(self) -> None:
        """Repetition means the same shape, not the same numbers — twelve
        copies of one sum is not practice."""
        for p in pages():
            with self.subTest(page=p.id):
                asked = [(e.prompt, e.expect) for e in p.exercises]
                self.assertEqual(len(asked), len(set(asked)))

    def test_every_shape_is_used(self) -> None:
        """A shape with no page behind it is code nobody runs."""
        used = {e.shape for _, e in ALL}
        self.assertEqual(used, set(all_shape_ids()))

    def test_a_prompt_never_gives_away_the_syntax(self) -> None:
        """The prompt is the same sentence in every language, so anything that
        only makes sense in one of them is a bug in the prompt."""
        for _, e in ALL:
            with self.subTest(exercise=e.id):
                for giveaway in ("print(", "console.log", "println", "printf"):
                    self.assertNotIn(giveaway, e.prompt)


class OutputTests(unittest.TestCase):
    def test_output_is_worked_out_not_guessed(self) -> None:
        self.assertEqual(expected_output("print_expr", {"expr": "3 + 4"}), "7")
        self.assertEqual(
            expected_output("for_range_print", {"lo": 1, "hi": 3, "expr": "i"}),
            "1\n2\n3",
        )
        self.assertEqual(
            expected_output("for_sum", {"lo": 1, "hi": 10, "expr": "i"}), "55"
        )

    def test_a_loop_that_stops_before_its_limit_is_not_the_same(self) -> None:
        """Page 6's whole point. If these two ever compared equal the page
        would be teaching nothing."""
        before = expected_output("for_print", {"count": 5, "expr": "i"})
        inclusive = expected_output(
            "for_range_print", {"lo": 1, "hi": 5, "expr": "i"}
        )
        self.assertNotEqual(before, inclusive)

    def test_trailing_whitespace_is_not_the_exercise(self) -> None:
        self.assertTrue(matches("7\n", "7"))
        self.assertTrue(matches("7", "7\n\n"))
        self.assertTrue(matches("1 \n2\n", "1\n2"))
        self.assertEqual(normalise("a\r\nb\r\n"), "a\nb")

    def test_the_wrong_answer_is_still_wrong(self) -> None:
        """The normalising must forgive whitespace and nothing else."""
        self.assertFalse(matches("8", "7"))
        self.assertFalse(matches("1\n2", "1\n2\n3"))
        self.assertFalse(matches("", "7"))

    def test_an_unknown_shape_is_an_error_not_an_empty_page(self) -> None:
        with self.assertRaises(KeyError):
            expected_output("nonsense", {})


class ReferenceRunTests(unittest.TestCase):
    """The check that matters: run the answer and see what it prints.

    Everything else in this file reads data. This executes it.
    """

    def _run(self, language: str, exercise) -> None:
        code = exercise.answer(language)
        self.assertIsNotNone(code, f"no reference for {language}")
        stdout, stderr, exit_code = run_code(code, language=language)
        self.assertEqual(exit_code, 0, (stderr or stdout)[:400])
        self.assertTrue(
            matches(stdout, exercise.expect),
            f"printed {stdout!r}, wanted {exercise.expect!r}",
        )

    def test_every_exercise_solves_in_python(self) -> None:
        for p, e in ALL:
            with self.subTest(exercise=e.id):
                self._run("python", e)

    def test_every_exercise_solves_in_javascript(self) -> None:
        for p, e in ALL:
            with self.subTest(exercise=e.id):
                self._run("javascript", e)

    def test_every_shape_compiles_and_runs_in_every_language(self) -> None:
        """One per shape rather than all of them: within a shape only the
        numbers change, and each of these is another compile."""
        for language in OTHERS:
            for p, e in _one_per_shape(language):
                with self.subTest(language=language, shape=e.shape):
                    self._run(language, e)

    def test_dart_runs_one_of_everything_it_has(self) -> None:
        """Dart is one of the three the long ramp is written for, so its
        coverage is every shape rather than only the shared ones."""
        shapes = {e.shape for _, e in _one_per_shape("dart")}
        self.assertEqual(shapes, set(all_shape_ids()))


class EndpointTests(unittest.TestCase):
    def _request(self, **kwargs):
        from code_coach.api.schemas import WorkbookCheckRequest

        return WorkbookCheckRequest(**kwargs)

    def test_it_serves_the_pages_for_a_language(self) -> None:
        from code_coach.api import server

        served = server.workbook("python")
        self.assertTrue(served["has_workbook"])
        self.assertEqual(len(served["pages"]), len(pages("python")))
        first = served["pages"][0]["exercises"][0]
        self.assertTrue(first["prompt"])
        self.assertTrue(first["answer"])

    def test_it_says_so_for_a_language_it_cannot_serve(self) -> None:
        """SQL has no print statement and no loop. An empty page with a reason
        beats a page of exercises that cannot be written."""
        from code_coach.api import server

        served = server.workbook("sql")
        self.assertFalse(served["has_workbook"])
        self.assertEqual(served["pages"], [])
        self.assertFalse(has_workbook("sql"))

    def test_a_right_answer_passes_and_is_remembered(self) -> None:
        import tempfile
        from pathlib import Path

        from code_coach.api import server
        from code_coach.progress.store import ProgressStore, active_store, use_store

        real = server._store
        try:
            use_store(ProgressStore(Path(tempfile.mkdtemp()) / "p.json"))
            server._store = active_store()
            got = server.workbook_check(
                self._request(
                    page_id="arithmetic",
                    exercise_id="arithmetic-01",
                    code="print(3 + 4)",
                    language="python",
                )
            )
            self.assertTrue(got.passed)
            self.assertEqual(got.done_on_page, 1)
            self.assertEqual(got.page_total, 12)
            # And it survives a reload — the store's from_dict is an explicit
            # allow-list, so a new field it does not name is silently dropped.
            stored = server._store.load()
            self.assertIn("arithmetic-01", stored.workbook_for("python"))
        finally:
            server._store = real

    def test_a_different_language_is_counted_separately(self) -> None:
        """Solving it in Python does not mean you can write it in Rust."""
        import tempfile
        from pathlib import Path

        from code_coach.api import server
        from code_coach.progress.store import ProgressStore, active_store, use_store

        real = server._store
        try:
            use_store(ProgressStore(Path(tempfile.mkdtemp()) / "p.json"))
            server._store = active_store()
            server.workbook_check(
                self._request(
                    page_id="arithmetic",
                    exercise_id="arithmetic-01",
                    code="print(3 + 4)",
                    language="python",
                )
            )
            stored = server._store.load()
            self.assertEqual(stored.workbook_for("javascript"), [])
        finally:
            server._store = real

    def test_the_right_answer_written_a_different_way_also_passes(self) -> None:
        """It checks what the program printed, not how it was written."""
        from code_coach.api import server

        for code in ("print(7)", "print(3 + 4)", "x = 3\ny = 4\nprint(x + y)"):
            with self.subTest(code=code):
                got = server.workbook_check(
                    self._request(
                        page_id="arithmetic",
                        exercise_id="arithmetic-01",
                        code=code,
                        language="python",
                    )
                )
                self.assertTrue(got.passed)

    def test_a_wrong_answer_says_what_it_printed(self) -> None:
        from code_coach.api import server

        got = server.workbook_check(
            self._request(
                page_id="arithmetic",
                exercise_id="arithmetic-01",
                code="print(8)",
                language="python",
            )
        )
        self.assertFalse(got.passed)
        self.assertFalse(got.failed_to_run)
        self.assertEqual(got.stdout.strip(), "8")
        self.assertEqual(got.expect, "7")

    def test_code_that_does_not_run_is_a_different_answer(self) -> None:
        """A syntax error and a wrong number are different problems, and
        reading "wrong" for a program that never started is misleading."""
        from code_coach.api import server

        got = server.workbook_check(
            self._request(
                page_id="arithmetic",
                exercise_id="arithmetic-01",
                code="print(3 + ",
                language="python",
            )
        )
        self.assertFalse(got.passed)
        self.assertTrue(got.failed_to_run)
        self.assertTrue(got.stderr.strip())

    def test_an_exercise_that_does_not_exist_is_a_404(self) -> None:
        from fastapi import HTTPException

        from code_coach.api import server

        with self.assertRaises(HTTPException) as caught:
            server.workbook_check(
                self._request(
                    page_id="arithmetic",
                    exercise_id="arithmetic-99",
                    code="print(7)",
                    language="python",
                )
            )
        self.assertEqual(caught.exception.status_code, 404)

    def test_a_language_without_a_workbook_is_refused(self) -> None:
        from fastapi import HTTPException

        from code_coach.api import server

        with self.assertRaises(HTTPException) as caught:
            server.workbook_check(
                self._request(
                    page_id="arithmetic",
                    exercise_id="arithmetic-01",
                    code="SELECT 7;",
                    language="sql",
                )
            )
        self.assertEqual(caught.exception.status_code, 409)

    def test_lookups_handle_nothing(self) -> None:
        from code_coach.workbook import exercise as find

        self.assertIsNone(page("nonsense"))
        self.assertIsNone(find("nonsense", "x"))
        self.assertIsNone(find("arithmetic", "nope"))


class LanguageReachTests(unittest.TestCase):
    """How far the ramp goes in each language.

    All of it, in every language the workbook runs in. The later pages —
    lists, strings, functions — were three languages deep for a while, on the
    assumption that C would need the exercise faked to take part. It did not.
    SQL is still out, and for a real reason: no statement that prints a line
    and no loop.
    """

    DEEP = (
        "python",
        "javascript",
        "typescript",
        "dart",
        "c",
        "cpp",
        "rust",
    )

    # Where each language's ramp ends, and why. C stops at 48 because
    # splitting text and looking things up by key need types it has not got —
    # and the honest C answer to either is a week of memory management rather
    # than one exercise.
    EVERY_PAGE = (
        "python",
        "javascript",
        "typescript",
        "dart",
        "cpp",
        "rust",
    )

    def test_most_languages_get_the_whole_ramp(self) -> None:
        for language in self.EVERY_PAGE:
            with self.subTest(language=language):
                self.assertEqual(len(pages(language)), len(pages()))
                self.assertGreaterEqual(exercise_count(language), 600)

    def test_c_stops_where_its_types_do(self) -> None:
        """Deliberate, not an accident — so a later page cannot quietly drop
        C without someone deciding to."""
        numbers = [p.number for p in pages("c")]
        self.assertEqual(max(numbers), 48)
        self.assertEqual(len(numbers), 48)
        dropped = {p.id for p in pages() if not p.applies_to("c")}
        self.assertEqual(
            dropped,
            {
                "split-words",
                "count-words",
                "join-list",
                "map-lookup",
                "map-build",
                "str-contains",
                "str-slice",
                "str-find",
            },
        )

    def test_the_languages_that_get_it_are_the_ones_that_can_run_it(self) -> None:
        """The list on the pages and the list of runners have to be the same
        list, or a page is offered to somebody who cannot answer it."""
        self.assertEqual(set(self.DEEP), set(LANGUAGES))

    def test_sql_is_left_out_and_says_so(self) -> None:
        self.assertFalse(has_workbook("sql"))
        self.assertNotIn("sql", self.DEEP)

    def test_a_language_is_never_offered_a_page_it_cannot_answer(self) -> None:
        """The real check: every page a language is shown must have a
        reference program in it, or the exercise cannot be marked right."""
        for language in LANGUAGES:
            for p in pages(language):
                for e in p.exercises:
                    with self.subTest(language=language, exercise=e.id):
                        self.assertIsNotNone(e.answer(language))

    def test_the_early_pages_are_open_to_everyone(self) -> None:
        for p in pages():
            if p.number > 11:
                continue
            with self.subTest(page=p.id):
                self.assertEqual(p.languages, ())

    def test_the_later_pages_name_who_they_are_for(self) -> None:
        """Past page 11 a page always says which languages it is for, and the
        set is always one the app actually runs."""
        for p in pages():
            if p.number <= 11:
                continue
            with self.subTest(page=p.id):
                self.assertTrue(p.languages)
                self.assertTrue(set(p.languages) <= set(self.DEEP))

    def test_no_two_languages_are_told_to_print_different_things(self) -> None:
        """The rule the whole design rests on. An exercise has one expected
        output, so if two languages would print different characters for it
        the exercise is unanswerable in one of them — and it fails quietly,
        for that language only."""
        for p in pages():
            for e in p.exercises:
                with self.subTest(exercise=e.id):
                    self.assertIsInstance(e.expect, str)
                    # Nothing may print a Python container or a Python bool:
                    # those are the two that render differently elsewhere.
                    self.assertNotIn("[", e.expect)
                    self.assertNotIn("True", e.expect)
                    self.assertNotIn("False", e.expect)

    def test_the_payload_only_carries_pages_you_can_do(self) -> None:
        from code_coach.api import server

        for language in ("python", "c", "sql"):
            with self.subTest(language=language):
                served = server.workbook(language)
                self.assertEqual(len(served["pages"]), len(pages(language)))
                for entry in served["pages"]:
                    for item in entry["exercises"]:
                        self.assertTrue(item["answer"])


class MemoryTests(unittest.TestCase):
    """Where you were, and what you wrote.

    The workbook used to open at page one however far in you were, and threw
    away every answer the moment you moved on. Both are stored in the progress
    file, whose loader is an explicit allow-list — a field it does not name is
    silently dropped on the next read, which has already happened once here.
    So every one of these checks the value comes back after a reload rather
    than only that it was set.
    """

    def _fresh(self):
        import tempfile
        from pathlib import Path

        from code_coach.api import server
        from code_coach.progress.store import ProgressStore, active_store, use_store

        use_store(ProgressStore(Path(tempfile.mkdtemp()) / "p.json"))
        server._store = active_store()
        return server

    def _check(self, server, page_id, exercise_id, code, language="python"):
        from code_coach.api.schemas import WorkbookCheckRequest

        return server.workbook_check(
            WorkbookCheckRequest(
                page_id=page_id,
                exercise_id=exercise_id,
                code=code,
                language=language,
            )
        )

    def setUp(self) -> None:
        from code_coach.api import server

        self._real = server._store
        self.server = self._fresh()

    def tearDown(self) -> None:
        from code_coach.api import server

        server._store = self._real

    def test_it_opens_where_you_were(self) -> None:
        self._check(
            self.server, "first-loop", "first-loop-01", "for i in range(5):\n    print(i)"
        )
        self.assertEqual(self.server.workbook("python")["at"], "first-loop")

    def test_a_wrong_answer_still_keeps_your_place(self) -> None:
        """Coming back to the page you were stuck on is the point."""
        got = self._check(self.server, "ranges", "ranges-01", "print(0)")
        self.assertFalse(got.passed)
        self.assertEqual(self.server.workbook("python")["at"], "ranges")

    def test_a_new_student_has_no_place_to_return_to(self) -> None:
        """Empty rather than a guess, so the screen can fall back to page one
        itself instead of being sent somewhere arbitrary."""
        self.assertEqual(self.server.workbook("python")["at"], "")

    def test_your_answer_is_kept(self) -> None:
        code = "for i in range(5):\n    print(i)"
        self._check(self.server, "first-loop", "first-loop-01", code)
        answers = self.server.workbook("python")["answers"]
        self.assertEqual(answers["first-loop-01"], code)

    def test_only_answers_that_worked_are_kept(self) -> None:
        """A record of your work, not of your typos."""
        self._check(self.server, "arithmetic", "arithmetic-01", "print(8)")
        self.assertEqual(self.server.workbook("python")["answers"], {})

    def test_a_later_answer_replaces_an_earlier_one(self) -> None:
        self._check(self.server, "arithmetic", "arithmetic-01", "print(7)")
        self._check(self.server, "arithmetic", "arithmetic-01", "print(3 + 4)")
        answers = self.server.workbook("python")["answers"]
        self.assertEqual(answers["arithmetic-01"], "print(3 + 4)")

    def test_it_survives_a_reload(self) -> None:
        """The bit that the allow-list loader breaks if it is forgotten."""
        from code_coach.api import server

        code = "print(3 + 4)"
        self._check(self.server, "arithmetic", "arithmetic-01", code)
        reloaded = server._store.load()
        self.assertEqual(reloaded.workbook_page_for("python"), "arithmetic")
        self.assertEqual(
            reloaded.workbook_answers_for("python")["arithmetic-01"], code
        )

    def test_each_language_is_remembered_separately(self) -> None:
        self._check(self.server, "arithmetic", "arithmetic-01", "print(7)")
        self._check(
            self.server,
            "first-loop",
            "first-loop-01",
            "for (let i = 0; i < 5; i++) { console.log(i); }",
            language="javascript",
        )
        python = self.server.workbook("python")
        javascript = self.server.workbook("javascript")
        self.assertEqual(python["at"], "arithmetic")
        self.assertEqual(javascript["at"], "first-loop")
        self.assertNotIn("first-loop-01", python["answers"])
        self.assertNotIn("arithmetic-01", javascript["answers"])

    def test_an_enormous_answer_cannot_bloat_the_file(self) -> None:
        from code_coach.progress.store import MAX_ANSWER_CHARS

        progress = self.server._store.load()
        progress.remember_workbook_answer("python", "x-01", "a" * 99999)
        self.assertEqual(
            len(progress.workbook_answers_for("python")["x-01"]),
            MAX_ANSWER_CHARS,
        )


if __name__ == "__main__":
    unittest.main()
