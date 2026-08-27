"""Per-language fundamentals banks."""

import unittest

import shutil

from code_coach.engine import (
    dart_available,
    run_code,
    typescript_available,
)
from code_coach.fundamentals.base import (
    CLASS_IDS,
    bank_for,
    classes_with_material,
    has_fundamentals,
    material_count,
    snippets_for,
    specs_for,
)

DECLARED = ("dart", "javascript", "typescript", "c", "cpp", "rust", "sql")


class BankShapeTests(unittest.TestCase):
    def test_declared_languages_are_registered(self):
        for language in DECLARED:
            with self.subTest(language=language):
                self.assertIsNotNone(bank_for(language))

    def test_every_class_has_material(self):
        for language in DECLARED:
            for class_id in CLASS_IDS:
                with self.subTest(language=language, class_id=class_id):
                    self.assertTrue(has_fundamentals(language, class_id))
                    self.assertGreater(material_count(language, class_id, 5), 0)

    def test_python_reports_material_without_a_bank(self):
        # Python's fundamentals are generated, not declared.
        self.assertIsNone(bank_for("python"))
        for class_id in CLASS_IDS:
            self.assertTrue(has_fundamentals("python", class_id))

    def test_unknown_language_has_nothing(self):
        self.assertEqual(classes_with_material("cobol"), ())
        self.assertEqual(snippets_for("cobol", "foundations", 1), [])


class LevelTests(unittest.TestCase):
    def test_levels_are_cumulative_below_five(self):
        one = material_count("dart", "foundations", 1)
        four = material_count("dart", "foundations", 4)
        self.assertGreater(four, one)

    def test_level_five_is_whole_programs_only(self):
        five = snippets_for("dart", "foundations", 5)
        self.assertTrue(five)
        for snippet in five:
            with self.subTest(code=snippet.code[:30]):
                self.assertEqual(snippet.level, 5)

    def test_level_one_snippets_are_single_lines(self):
        for language in DECLARED:
            for snippet in snippets_for(language, "foundations", 1):
                with self.subTest(language=language, code=snippet.code[:30]):
                    self.assertNotIn("\n", snippet.code)

    def test_every_snippet_carries_a_tip(self):
        for language in DECLARED:
            for class_id in CLASS_IDS:
                for snippet in snippets_for(language, class_id, 5):
                    with self.subTest(language=language, code=snippet.code[:30]):
                        self.assertTrue(snippet.tip.strip())


class WindowTests(unittest.TestCase):
    def test_a_window_is_the_size_asked_for(self):
        specs = specs_for("dart", "foundations", batch=0, count=8, level=2)
        self.assertEqual(len(specs), 8)

    def test_windows_wrap_rather_than_running_out(self):
        # Far past the end of the material — endless mode depends on this.
        specs = specs_for("dart", "loops", batch=99, count=8, level=3)
        self.assertEqual(len(specs), 8)

    def test_a_window_stops_at_the_end_of_the_material(self):
        # Padding the last window back out to eight refills it with snippets
        # you have just typed, which reads as being sent back to the start.
        total = material_count("javascript", "foundations", 1)
        seen = 0
        batch = 0
        while seen < total:
            specs = specs_for(
                "javascript", "foundations", batch=batch, count=8, level=1
            )
            self.assertEqual(specs[0].id.split("-")[2], str(seen))
            seen += len(specs)
            batch += 1
        self.assertEqual(seen, total)

    def test_ids_are_stable_across_calls(self):
        first = [s.id for s in specs_for("dart", "decisions", batch=1, count=5, level=2)]
        again = [s.id for s in specs_for("dart", "decisions", batch=1, count=5, level=2)]
        self.assertEqual(first, again)

    def test_a_snippet_checks_against_itself(self):
        for spec in specs_for("javascript", "loops", batch=0, count=6, level=4):
            with self.subTest(code=spec.example[:30]):
                self.assertTrue(spec.check(spec.example))


class LanguageRegistryTests(unittest.TestCase):
    def test_every_available_language_has_material(self):
        from code_coach.languages import LANGUAGES

        for lang in LANGUAGES:
            if not lang.available:
                continue
            with self.subTest(language=lang.id):
                self.assertTrue(
                    classes_with_material(lang.id),
                    f"{lang.id} is offered but has no classes",
                )

    def test_a_language_can_rename_its_classes(self):
        # SQL doesn't loop, so its third class is Grouping & Joins.
        bank = bank_for("sql")
        self.assertIsNotNone(bank)
        self.assertEqual(bank.get("loops").name, "Grouping & Joins")
        self.assertEqual(bank.get("foundations").name, "Queries")


class SqlRunnerTests(unittest.TestCase):
    """SQL runs in-process on sqlite3, so this needs nothing installed."""

    def test_a_select_returns_a_table(self):
        from code_coach.sql_runner import run_sql

        out, err, code = run_sql("SELECT name FROM users ORDER BY name LIMIT 2;")
        self.assertEqual(code, 0, err)
        self.assertIn("Alex", out)
        self.assertIn("name", out)

    def test_an_aggregate_works(self):
        from code_coach.sql_runner import run_sql

        out, err, code = run_sql("SELECT COUNT(*) AS n FROM users;")
        self.assertEqual(code, 0, err)
        self.assertIn("5", out)

    def test_a_join_works(self):
        from code_coach.sql_runner import run_sql

        out, _, code = run_sql(
            "SELECT u.name, SUM(o.price) AS total FROM users u "
            "JOIN orders o ON o.user_id = u.id GROUP BY u.name;"
        )
        self.assertEqual(code, 0)
        self.assertIn("Alex", out)

    def test_a_broken_query_reports_rather_than_raises(self):
        from code_coach.sql_runner import run_sql

        out, err, code = run_sql("SELECT * FROM nope;")
        self.assertEqual(code, 1)
        self.assertIn("SQL error", err)

    def test_nulls_are_shown_not_blank(self):
        from code_coach.sql_runner import run_sql

        out, _, _ = run_sql("SELECT email FROM users WHERE email IS NULL;")
        self.assertIn("NULL", out)

    def test_the_database_is_rebuilt_each_run(self):
        from code_coach.sql_runner import run_sql

        run_sql("DELETE FROM users;")
        out, _, _ = run_sql("SELECT COUNT(*) AS n FROM users;")
        self.assertIn("5", out)


# Which languages can be executed here, and what each needs to be present.
# A language is skipped rather than assumed: a snippet nobody can run is a
# snippet nobody has checked, and saying so is better than pretending.
#
# Rust sat outside this for as long as there was no rustc on the machine, and
# the snippets went unexecuted the whole time — they were reviewed, which is
# not the same thing. With a toolchain present they are checked like the rest.
RUNNABLE = {
    "javascript": lambda: shutil.which("node") is not None,
    "typescript": typescript_available,
    "dart": dart_available,
    "rust": lambda: shutil.which("rustc") is not None,
    "sql": lambda: True,  # sqlite3 ships with Python
}


class LevelFiveSnippetsRunTests(unittest.TestCase):
    """A level-5 snippet is a whole program, so it has to be one.

    These are typed verbatim and then Run, so a typo would be drilled in
    rather than caught. Exit code alone is not enough: a JavaScript file that
    only defines a function exits 0 and prints nothing, and a Dart string with
    an escaped dollar runs perfectly while printing the variable's name
    instead of its value. Both of those were real, and both are checked here.
    """

    def _check(self, language: str) -> None:
        for class_id in CLASS_IDS:
            for snippet in snippets_for(language, class_id, 5):
                with self.subTest(class_id=class_id, code=snippet.code[:40]):
                    out, err, code = run_code(snippet.code, language=language)
                    self.assertEqual(code, 0, (err or out)[:300])
                    self.assertTrue(
                        out.strip(),
                        "printed nothing, so Run does nothing visible",
                    )

    def test_a_level_five_snippet_is_a_whole_function(self):
        """Two lines is a level-4 block; level 5 is the function itself.

        Except in SQL, which has no functions to write. There a complete
        statement is the whole unit, and SELECT name / FROM users is two
        lines and finished.
        """
        for language in RUNNABLE:
            if language == "sql":
                continue
            for class_id in CLASS_IDS:
                for snippet in snippets_for(language, class_id, 5):
                    with self.subTest(language=language, code=snippet.code[:30]):
                        self.assertGreaterEqual(
                            len(snippet.code.splitlines()), 3
                        )

    def test_every_class_has_enough_whole_functions(self):
        """Fewer than this and the class is over in one short window."""
        for language in DECLARED:
            for class_id in CLASS_IDS:
                with self.subTest(language=language, class_id=class_id):
                    self.assertGreaterEqual(
                        material_count(language, class_id, 5),
                        4,
                        "add level-5 snippets for this class",
                    )


def _runner(language: str):
    def test(self):
        if not RUNNABLE[language]():
            self.skipTest(f"no toolchain for {language}")
        self._check(language)

    test.__doc__ = f"Every level-5 {language} snippet runs and prints."
    return test


for _lang in RUNNABLE:
    setattr(LevelFiveSnippetsRunTests, f"test_{_lang}_snippets_run", _runner(_lang))


if __name__ == "__main__":
    unittest.main()
