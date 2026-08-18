"""Per-language fundamentals banks."""

import unittest

from code_coach.engine import dart_available, run_code
from code_coach.fundamentals.base import (
    CLASS_IDS,
    bank_for,
    classes_with_material,
    has_fundamentals,
    material_count,
    snippets_for,
    specs_for,
)

DECLARED = ("dart", "javascript")


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

    def test_ids_are_stable_across_calls(self):
        first = [s.id for s in specs_for("dart", "decisions", batch=1, count=5, level=2)]
        again = [s.id for s in specs_for("dart", "decisions", batch=1, count=5, level=2)]
        self.assertEqual(first, again)

    def test_a_snippet_checks_against_itself(self):
        for spec in specs_for("javascript", "loops", batch=0, count=6, level=4):
            with self.subTest(code=spec.example[:30]):
                self.assertTrue(spec.check(spec.example))


@unittest.skipUnless(dart_available(), "Dart SDK not on PATH")
class DartSnippetsCompileTests(unittest.TestCase):
    """Whole-program snippets must actually run — a typo in one would ask the
    student to type something that can't work."""

    def test_level_five_snippets_run(self):
        for class_id in CLASS_IDS:
            for snippet in snippets_for("dart", class_id, 5):
                src = snippet.code
                if "void main(" not in src:
                    src += "\n\nvoid main() {}\n"
                out, err, code = run_code(src, language="dart")
                with self.subTest(class_id=class_id, code=snippet.code[:40]):
                    self.assertEqual(code, 0, err[:300])


if __name__ == "__main__":
    unittest.main()
