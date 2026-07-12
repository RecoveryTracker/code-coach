"""
Tests for the endless type-along generators (code_coach/dictation/bank.py).
These are where subtle content bugs hide: duplicate lines in a window, or lines
that don't parse.

Run: .venv/bin/python -m unittest discover -s tests
"""

from __future__ import annotations

import ast
import unittest

from code_coach.dictation.bank import (
    DICTATION_LEVEL_MAX,
    DICTATION_LEVEL_MIN,
    WINDOW_SIZE,
    build_class_dictation_steps,
    build_dictation_steps,
)
from code_coach.dictation.session import make_class_dictation_batch


def _parses(example: str) -> bool:
    try:
        ast.parse(example)
        return True
    except SyntaxError:
        return False


class WindowInvariants(unittest.TestCase):
    def test_no_duplicate_examples_in_a_window(self):
        for level in range(DICTATION_LEVEL_MIN, DICTATION_LEVEL_MAX + 1):
            steps = build_dictation_steps(
                seed=f"seed-{level}", count=WINDOW_SIZE, level=level
            )
            examples = [s.example for s in steps]
            self.assertEqual(
                len(examples), len(set(examples)),
                f"duplicate example at level {level}",
            )

    def test_window_size_honored(self):
        steps = build_dictation_steps(seed="s", count=WINDOW_SIZE, level=1)
        self.assertLessEqual(len(steps), WINDOW_SIZE)
        self.assertGreater(len(steps), 0)

    def test_every_example_parses_at_every_level(self):
        for level in range(DICTATION_LEVEL_MIN, DICTATION_LEVEL_MAX + 1):
            steps = build_dictation_steps(
                seed=f"lvl-{level}", count=WINDOW_SIZE, level=level
            )
            for s in steps:
                self.assertTrue(
                    _parses(s.example),
                    f"level {level} produced unparseable line: {s.example!r}",
                )

    def test_spine_only_on_first_batch_easy_levels(self):
        first = build_dictation_steps(
            seed="student:batch:0", count=WINDOW_SIZE, include_spine=True, level=1
        )
        self.assertTrue(any(s.id.startswith("spine-") for s in first))
        # A later batch (include_spine False) should have no spine lines.
        later = build_dictation_steps(
            seed="student:batch:3", count=WINDOW_SIZE, include_spine=False, level=1
        )
        self.assertFalse(any(s.id.startswith("spine-") for s in later))

    def test_each_step_check_accepts_its_own_example(self):
        steps = build_dictation_steps(seed="chk", count=WINDOW_SIZE, level=3)
        for s in steps:
            self.assertTrue(
                s.check(s.example),
                f"step {s.id} rejects its own example: {s.example!r}",
            )


class PerClassWindows(unittest.TestCase):
    """Every class's Lesson 1 is an endless type-along drilling that class's
    own syntax (decisions: if/else/comparisons; loops: for/while/range)."""

    def test_all_levels_parse_and_dedupe(self):
        for class_id in ("decisions", "loops"):
            for level in range(DICTATION_LEVEL_MIN, DICTATION_LEVEL_MAX + 1):
                steps = build_class_dictation_steps(
                    class_id,
                    seed=f"t:{level}",
                    count=WINDOW_SIZE,
                    level=level,
                    include_spine=(level <= 2),
                )
                exs = [s.example for s in steps]
                self.assertEqual(len(exs), len(set(exs)), f"{class_id} L{level}")
                for s in steps:
                    ast.parse(s.example)
                    self.assertTrue(s.check(s.example), s.example)

    def test_content_is_class_specific(self):
        dec = " ".join(
            s.example
            for s in build_class_dictation_steps(
                "decisions", seed="x", count=WINDOW_SIZE, level=3,
                include_spine=False,
            )
        )
        self.assertIn("if ", dec)
        lp = " ".join(
            s.example
            for s in build_class_dictation_steps(
                "loops", seed="x", count=WINDOW_SIZE, level=3,
                include_spine=False,
            )
        )
        self.assertIn("for ", lp)

    def test_batches_differ(self):
        a = [s.example for s in build_class_dictation_steps(
            "loops", seed="s:batch:1", count=WINDOW_SIZE, level=2,
            include_spine=False)]
        b = [s.example for s in build_class_dictation_steps(
            "loops", seed="s:batch:2", count=WINDOW_SIZE, level=2,
            include_spine=False)]
        self.assertNotEqual(a, b)

    def test_drill_wrapper_metadata(self):
        d = make_class_dictation_batch(
            "decisions", class_number=2, class_name="Decisions",
            seed="t", batch=0, level=1,
        )
        self.assertEqual(d.id, "decisions-l1")
        self.assertIn("dictation", d.tags)
        self.assertIn("endless", d.tags)
        self.assertEqual(d.skill, "conditionals")
        self.assertIn("Class 2", d.title)

    def test_foundations_falls_through_to_original(self):
        d = make_class_dictation_batch(
            "foundations", class_number=1, class_name="Foundations",
            seed="local-student", batch=0, level=1,
        )
        self.assertEqual(d.id, "class-1-dictation")


if __name__ == "__main__":
    unittest.main()
