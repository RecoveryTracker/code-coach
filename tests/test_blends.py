"""Several themes drawn as one pool.

The feature is small and the ways it can go quietly wrong are not, so
these are grouped by the failure they guard against rather than by the
function they call.

The one that matters most is the first: a single theme id has to behave
exactly as it did before blending existed. Every saved setting, every
link and every test written before this change depends on it, and a
regression there would look like "the app forgot my choice" rather than
like a bug in blending.
"""

from __future__ import annotations

import unittest

from code_coach.typing import blends
from code_coach.typing.drills import (
    THEMES_BY_ID,
    build_drill,
    resolve_theme,
    theme_name_for,
)


class SingleThemesAreUnchangedTests(unittest.TestCase):
    """The compatibility promise, checked against every theme there is."""

    def test_one_id_resolves_to_that_exact_theme(self) -> None:
        for theme_id, theme in THEMES_BY_ID.items():
            with self.subTest(theme=theme_id):
                self.assertIs(resolve_theme(theme_id), theme)

    def test_one_id_is_not_treated_as_a_blend(self) -> None:
        for theme_id in THEMES_BY_ID:
            with self.subTest(theme=theme_id):
                self.assertFalse(blends.is_blend(theme_id))

    def test_no_theme_id_contains_the_separator(self) -> None:
        """If one ever did, every blended id would be ambiguous and the
        split would silently produce themes nobody asked for."""
        for theme_id in THEMES_BY_ID:
            with self.subTest(theme=theme_id):
                self.assertNotIn(blends.SEPARATOR, theme_id)

    def test_an_unknown_id_still_falls_back(self) -> None:
        self.assertEqual(resolve_theme("not-a-theme").id, "mixed")
        self.assertEqual(resolve_theme("").id, "mixed")


class BlendContentTests(unittest.TestCase):

    def test_a_blend_holds_everything_from_both_parts(self) -> None:
        lore = THEMES_BY_ID["python"]
        code = THEMES_BY_ID["pycode"]
        mixed = resolve_theme("python,pycode")

        texts = {p.text for p in mixed.passages}
        for part in (lore, code):
            for passage in part.passages:
                with self.subTest(text=passage.text[:40]):
                    self.assertIn(passage.text, texts)

    def test_a_blend_adds_nothing_of_its_own(self) -> None:
        """The other half of the above: no line appears that did not
        come from one of the parts."""
        lore = THEMES_BY_ID["javascript"]
        code = THEMES_BY_ID["jscode"]
        allowed = {p.text for p in (*lore.passages, *code.passages)}
        for passage in resolve_theme("javascript,jscode").passages:
            with self.subTest(text=passage.text[:40]):
                self.assertIn(passage.text, allowed)

    def test_a_line_in_both_parts_appears_once(self) -> None:
        mixed = resolve_theme("pycode,jscode")
        texts = [p.text for p in mixed.passages]
        self.assertEqual(len(texts), len(set(texts)))

    def test_blocks_and_words_are_merged_too(self) -> None:
        """Not just passages. Whole-function mode reads blocks, and a
        blend that dropped them would fall back to Python without
        saying so."""
        mixed = resolve_theme("pycode,jscode")
        self.assertGreaterEqual(
            len(mixed.blocks),
            len(THEMES_BY_ID["pycode"].blocks),
        )
        worded = resolve_theme("vocab,common")
        self.assertGreaterEqual(
            len(worded.words), len(THEMES_BY_ID["vocab"].words)
        )

    def test_the_order_you_picked_is_the_order_you_get(self) -> None:
        first = resolve_theme("python,javascript").passages[0]
        self.assertIn(first.text, {p.text for p in THEMES_BY_ID["python"].passages})

    def test_a_blend_is_named_after_its_parts(self) -> None:
        name = theme_name_for("python,pycode")
        self.assertIn(THEMES_BY_ID["python"].name, name)
        self.assertIn(THEMES_BY_ID["pycode"].name, name)

    def test_too_many_parts_are_cut_rather_than_refused(self) -> None:
        ids = list(THEMES_BY_ID)[: blends.MAX_PARTS + 3]
        got = blends.split_id(resolve_theme(",".join(ids)).id)
        self.assertEqual(len(got), blends.MAX_PARTS)

    def test_an_unknown_part_is_dropped_not_fatal(self) -> None:
        """A renamed theme in a saved setting should cost that part,
        not the whole drill."""
        self.assertEqual(resolve_theme("python,gone").id, "python")


class BlendedDrillTests(unittest.TestCase):

    def test_a_blended_drill_draws_from_both(self) -> None:
        """The point of the whole feature. Checked over enough seeds
        that a draw which happens to favour one side cannot pass it."""
        lore = {p.text for p in THEMES_BY_ID["python"].passages}
        code = {p.text for p in THEMES_BY_ID["pycode"].passages}
        from_lore = from_code = 0
        for seed in range(25):
            drill = build_drill(
                "everything", "random",
                theme_id="python,pycode", seed=f"s{seed}", count=30,
            )
            for target in drill.targets:
                if target.text in lore:
                    from_lore += 1
                if target.text in code:
                    from_code += 1
        self.assertGreater(from_lore, 0, "no lore was ever drawn")
        self.assertGreater(from_code, 0, "no code was ever drawn")

    def test_a_blended_drill_is_the_same_shape_as_a_plain_one(self) -> None:
        plain = build_drill("everything", "random", theme_id="python", count=12)
        mixed = build_drill(
            "everything", "random", theme_id="python,pycode", count=12
        )
        self.assertEqual(len(plain.targets), len(mixed.targets))
        for target in mixed.targets:
            with self.subTest(text=target.text[:40]):
                self.assertTrue(target.text)
                self.assertTrue(target.note)

    def test_whole_function_mode_works_on_a_blend(self) -> None:
        drill = build_drill(
            "everything", "blocks", theme_id="pycode,jscode", count=6
        )
        self.assertTrue(drill.targets)
        self.assertTrue(any("\n" in t.text for t in drill.targets))

    def test_a_blend_with_no_blocks_still_falls_back(self) -> None:
        """Two prose themes cannot drive whole-function mode, and the
        fallback that already existed has to keep catching it rather
        than handing back an empty screen."""
        drill = build_drill(
            "everything", "blocks", theme_id="python,javascript", count=4
        )
        self.assertTrue(drill.targets)


class ApiTests(unittest.TestCase):

    def test_the_endpoint_accepts_a_blend(self) -> None:
        from code_coach.api.server import typing_drill

        got = typing_drill(
            section="everything", mode="random",
            theme="python,pycode", count=6,
        )
        self.assertEqual(got.theme, "python,pycode")
        self.assertIn("+", got.theme_name)
        self.assertTrue(got.targets)

    def test_an_unknown_part_is_a_404(self) -> None:
        """Dropped silently on the way in would mean asking for two
        themes and being given one without being told."""
        from fastapi import HTTPException

        from code_coach.api.server import typing_drill

        with self.assertRaises(HTTPException) as caught:
            typing_drill(
                section="everything", mode="random", theme="python,nope"
            )
        self.assertEqual(caught.exception.status_code, 404)
        self.assertIn("nope", str(caught.exception.detail))

    def test_a_plain_theme_still_answers_as_before(self) -> None:
        from code_coach.api.server import typing_drill

        got = typing_drill(
            section="everything", mode="random", theme="python", count=6
        )
        self.assertEqual(got.theme, "python")
        self.assertEqual(got.theme_name, THEMES_BY_ID["python"].name)


if __name__ == "__main__":
    unittest.main()
