"""Same Shape: one kind of line, many times, only the payload moving.

The property that makes this mode worth having is the one the tests
are about. If a "ten times in a row" drill quietly serves nine
different shapes, it looks fine on screen and trains nothing it
claims to - you would not notice, because every line is still real
code. So the first test is that a run is genuinely one shape, and the
rest guard the things that would let that be true while still being
useless: a run of the same line repeated, or a shape with so few
examples it cannot help repeating.
"""

from __future__ import annotations

import unittest

from code_coach.typing import shapes
from code_coach.typing.drills import (
    MODES_BY_ID,
    THEMES_BY_ID,
    _shape_sets,
    build_drill,
)

#: The code themes that should be able to drive this mode.
DRILLABLE = ("pycode", "jscode", "assemblycode")


class ShapeKeyTests(unittest.TestCase):

    def test_lines_of_one_shape_share_a_key(self) -> None:
        same = [
            "out.push(i);",
            "stack.push(ch);",
            "level.push(node.val);",
            "queue.push([r, c]);",
        ]
        keys = {shapes.shape_key(line, "javascript") for line in same}
        self.assertEqual(len(keys), 1, keys)

    def test_lines_of_different_shapes_do_not(self) -> None:
        keys = {
            shapes.shape_key("out.push(i);", "javascript"),
            shapes.shape_key("return best;", "javascript"),
            shapes.shape_key("const n = 0;", "javascript"),
            shapes.shape_key("for (const w of d) {", "javascript"),
        }
        self.assertEqual(len(keys), 4, keys)

    def test_the_payload_never_reaches_the_key(self) -> None:
        """Otherwise every line is its own shape and nothing groups."""
        a = shapes.shape_key("total = 0", "python")
        b = shapes.shape_key("answer = 999", "python")
        self.assertEqual(a, b)
        self.assertNotIn("total", a)
        self.assertNotIn("999", b)

    def test_an_undescribable_line_has_no_shape(self) -> None:
        self.assertIsNone(shapes.shape_key("}", "javascript"))
        self.assertIsNone(shapes.shape_key("x", "rust"))

    def test_a_shape_is_labelled_with_a_real_line_from_it(self) -> None:
        for theme_id in DRILLABLE:
            theme = THEMES_BY_ID[theme_id]
            texts = {p.text for p in theme.passages}
            for _key, label, _lines in _shape_sets(theme):
                with self.subTest(theme=theme_id, label=label):
                    self.assertIn(label, texts)


class DrillablePoolTests(unittest.TestCase):

    def test_every_offered_shape_has_enough_lines(self) -> None:
        """The floor exists so a sitting does not repeat itself."""
        for theme_id in DRILLABLE:
            for _key, label, lines in _shape_sets(THEMES_BY_ID[theme_id]):
                with self.subTest(theme=theme_id, label=label):
                    self.assertGreaterEqual(len(lines), shapes.MIN_LINES)

    def test_the_lines_in_a_shape_are_all_different(self) -> None:
        for theme_id in DRILLABLE:
            for _key, label, lines in _shape_sets(THEMES_BY_ID[theme_id]):
                texts = [p.text for p in lines]
                with self.subTest(theme=theme_id, label=label):
                    self.assertEqual(len(texts), len(set(texts)))

    def test_the_code_themes_offer_some_shapes(self) -> None:
        for theme_id in DRILLABLE:
            with self.subTest(theme=theme_id):
                self.assertTrue(_shape_sets(THEMES_BY_ID[theme_id]))

    def test_prose_themes_offer_none(self) -> None:
        """Lore is English. Grouping it by code shape would serve
        sentences under a mode that promises lines of code."""
        for theme_id in ("python", "javascript", "scripture", "mixed"):
            with self.subTest(theme=theme_id):
                self.assertFalse(_shape_sets(THEMES_BY_ID[theme_id]))

    def test_a_blend_groups_each_language_with_its_own_rules(self) -> None:
        """Python lines run through the JavaScript rules would land in
        shapes they do not have."""
        from code_coach.typing.drills import resolve_theme

        blended = _shape_sets(resolve_theme("pycode,jscode"))
        self.assertTrue(blended)
        py_lines = {p.text for p in THEMES_BY_ID["pycode"].passages}
        js_lines = {p.text for p in THEMES_BY_ID["jscode"].passages}
        for _key, _label, lines in blended:
            texts = {p.text for p in lines}
            with self.subTest(label=_label):
                # A shape's lines come from one language, not a mixture.
                self.assertTrue(texts <= py_lines or texts <= js_lines)


class SameShapeDrillTests(unittest.TestCase):

    def test_the_mode_exists_and_is_visible(self) -> None:
        self.assertIn("reps", MODES_BY_ID)
        self.assertFalse(MODES_BY_ID["reps"].hidden)

    def test_a_run_is_all_one_shape(self) -> None:
        """The whole promise of the mode, over enough seeds that a
        lucky draw cannot pass it."""
        for theme_id, language in (("pycode", "python"),
                                   ("jscode", "javascript")):
            for seed in range(20):
                drill = build_drill(
                    "everything", "reps",
                    theme_id=theme_id, seed=f"s{seed}", count=10,
                )
                keys = {
                    shapes.shape_key(t.text, language) for t in drill.targets
                }
                with self.subTest(theme=theme_id, seed=seed):
                    self.assertTrue(drill.targets)
                    self.assertEqual(len(keys), 1, keys)

    def test_a_run_does_not_repeat_a_line(self) -> None:
        """Ten of the same line is not ten reps of a shape, and it is
        the easiest way for this to look right and be wrong."""
        for seed in range(20):
            drill = build_drill(
                "everything", "reps", theme_id="jscode",
                seed=f"r{seed}", count=10,
            )
            texts = [t.text for t in drill.targets]
            with self.subTest(seed=seed):
                self.assertEqual(len(texts), len(set(texts)))

    def test_different_seeds_reach_different_shapes(self) -> None:
        """One shape per run, but not the same shape every run."""
        seen = set()
        for seed in range(30):
            drill = build_drill(
                "everything", "reps", theme_id="pycode",
                seed=f"v{seed}", count=6,
            )
            seen.add(shapes.shape_key(drill.targets[0].text, "python"))
        self.assertGreater(len(seen), 1, seen)

    def test_every_line_served_is_real_material(self) -> None:
        """Not generated. The variations have to come out of the bank,
        which is the thing that keeps them honest code."""
        pool = {p.text for p in THEMES_BY_ID["pycode"].passages}
        for seed in range(10):
            drill = build_drill(
                "everything", "reps", theme_id="pycode",
                seed=f"m{seed}", count=10,
            )
            for target in drill.targets:
                with self.subTest(text=target.text[:40]):
                    self.assertIn(target.text, pool)

    def test_every_target_carries_a_note(self) -> None:
        drill = build_drill(
            "everything", "reps", theme_id="jscode", seed="n", count=8
        )
        for target in drill.targets:
            with self.subTest(text=target.text[:40]):
                self.assertTrue(target.note.strip())

    def test_the_mode_is_not_offered_where_it_cannot_work(self) -> None:
        """A prose theme has no shapes, so asking for reps there must
        fall back rather than hand back an empty screen."""
        drill = build_drill(
            "everything", "reps", theme_id="scripture", seed="p", count=6
        )
        self.assertTrue(drill.targets)

    def test_assembly_can_drive_it_too(self) -> None:
        drill = build_drill(
            "everything", "reps", theme_id="assemblycode", seed="a", count=8
        )
        self.assertTrue(drill.targets)
        keys = {shapes.shape_key(t.text, "assembly") for t in drill.targets}
        self.assertEqual(len(keys), 1, keys)


class AssemblyMaterialTests(unittest.TestCase):
    """Assembly was added alongside the mode, to the same standard."""

    def test_the_lore_reaches_the_theme(self) -> None:
        from code_coach.typing import asmlore

        in_theme = {p.text for p in THEMES_BY_ID["assembly"].passages}
        for group in (asmlore.ASSEMBLY_STORY, asmlore.ASSEMBLY_IN_USE):
            self.assertTrue(group)
            for passage in group:
                with self.subTest(text=passage.text[:40]):
                    self.assertIn(passage.text, in_theme)

    def test_the_new_code_lines_reach_the_theme(self) -> None:
        from code_coach.typing import asmlore

        in_theme = {p.text for p in THEMES_BY_ID["assemblycode"].passages}
        for passage in asmlore.ASSEMBLY_CODE_MORE:
            with self.subTest(text=passage.text):
                self.assertIn(passage.text, in_theme)

    def test_the_dialect_is_consistent(self) -> None:
        """Intel syntax throughout. An AT&T line puts a % on its
        registers and a $ on its literals, and it would be described
        backwards by rules written for Intel order."""
        for passage in THEMES_BY_ID["assemblycode"].passages:
            with self.subTest(text=passage.text):
                self.assertNotIn("%rax", passage.text)
                self.assertNotIn("%eax", passage.text)

    def test_the_lore_states_rather_than_hedges(self) -> None:
        from code_coach.typing import asmlore

        for group in (asmlore.ASSEMBLY_STORY, asmlore.ASSEMBLY_IN_USE):
            for passage in group:
                lowered = passage.text.lower()
                for hedge in ("reportedly", "apparently", "supposedly",
                              "allegedly", "i think", "rumour"):
                    with self.subTest(hedge=hedge, text=passage.text[:40]):
                        self.assertNotIn(hedge, lowered)


if __name__ == "__main__":
    unittest.main()
