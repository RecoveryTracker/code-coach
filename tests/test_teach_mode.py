"""Learn and Type: read it by typing it, then type what it describes.

The value of the mode is entirely in the pairing — the sentence and the code
it is about, adjacent and in that order. Split them up, shuffle them apart, or
let the prose be a two-word label, and there is nothing left worth doing.
"""

from __future__ import annotations

import unittest

from code_coach.typing.drills import build_drill, catalog, reset_deals
from code_coach.typing.teach import (
    MIN_PROSE,
    has_own_solutions,
    teaching_pairs,
)


class PairTests(unittest.TestCase):
    def test_every_language_has_something_to_teach(self) -> None:
        for language in ("python", "javascript", "typescript", "dart", "c"):
            with self.subTest(language=language):
                self.assertGreaterEqual(len(teaching_pairs(language)), 40)

    def test_a_pair_is_prose_and_code(self) -> None:
        for language in ("python", "javascript", "dart"):
            for pair in teaching_pairs(language):
                with self.subTest(language=language, source=pair.source):
                    self.assertGreaterEqual(len(pair.prose), MIN_PROSE)
                    self.assertTrue(pair.code.strip())
                    self.assertTrue(pair.source.strip())

    def test_the_prose_is_one_line(self) -> None:
        """It is being typed, so a wrapped paragraph would be a wall."""
        for language in ("python", "javascript", "dart"):
            for pair in teaching_pairs(language):
                with self.subTest(language=language, source=pair.source):
                    self.assertNotIn("\n", pair.prose)
                    self.assertNotIn("  ", pair.prose)

    def test_no_code_is_taught_twice(self) -> None:
        for language in ("python", "javascript", "dart"):
            codes = [p.code for p in teaching_pairs(language)]
            with self.subTest(language=language):
                self.assertEqual(len(codes), len(set(codes)))

    def test_a_language_is_never_taught_another_language(self) -> None:
        """patterns_for_language falls back to Python's bank, so without a
        guard a C learner would be typing Python solutions."""
        for language in ("c", "cpp", "rust", "sql"):
            with self.subTest(language=language):
                self.assertFalse(has_own_solutions(language))
                for pair in teaching_pairs(language):
                    self.assertFalse(
                        pair.source.startswith("lesson #"),
                        f"{language} was offered a pseudocode lesson stage",
                    )
                    self.assertFalse(
                        pair.source.startswith("#"),
                        f"{language} was offered a solution it does not have",
                    )


class DrillTests(unittest.TestCase):
    def test_the_mode_is_offered_where_it_can_be_typed(self) -> None:
        for entry in catalog():
            offers = "teach" in {m["id"] for m in entry["modes"]}
            with self.subTest(section=entry["id"]):
                self.assertEqual(offers, entry["id"] in ("everything", "code"))

    def test_targets_come_in_pairs(self) -> None:
        reset_deals()
        targets = build_drill("everything", "teach", seed="t").targets
        self.assertTrue(targets)
        self.assertEqual(len(targets) % 2, 0)

    def test_the_idea_always_comes_before_its_code(self) -> None:
        """Adjacent and in order. This is the whole mode."""
        reset_deals()
        targets = build_drill("everything", "teach", seed="t").targets
        for i, target in enumerate(targets):
            with self.subTest(i=i):
                if i % 2 == 0:
                    self.assertTrue(target.note.startswith("the idea"))
                else:
                    self.assertEqual(target.note, "now the code it describes")

    def test_a_run_is_worth_sitting_down_for(self) -> None:
        reset_deals()
        targets = build_drill("everything", "teach", seed="t").targets
        self.assertGreaterEqual(len(targets), 8)

    def test_consecutive_runs_work_through_the_material(self) -> None:
        """Same dealing rule as the passages: nothing repeats until the pool
        has been worked through."""
        reset_deals()
        seen: list[str] = []
        for i in range(6):
            for target in build_drill("everything", "teach", seed=str(i)).targets:
                seen.append(target.text)
        self.assertEqual(len(seen), len(set(seen)))

    def test_the_prose_can_be_typed(self) -> None:
        """It goes through `typeable`, so a curly quote in a tip becomes one
        the keyboard has."""
        from code_coach.typing.drills import UNTYPEABLE

        reset_deals()
        for i in range(4):
            for target in build_drill("everything", "teach", seed=str(i)).targets:
                for wrong in UNTYPEABLE:
                    with self.subTest(char=wrong):
                        self.assertNotIn(wrong, target.text)


if __name__ == "__main__":
    unittest.main()
