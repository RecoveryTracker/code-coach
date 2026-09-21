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
    shape_catalog,
)

#: The code themes that should be able to drive this mode.
DRILLABLE = ("pycode", "jscode", "assemblycode")


def _languages_of(theme_id: str) -> list[str]:
    """Every language the drill might read this theme in.

    A list, not one: a blend is several languages at once, and asking
    the resolver rather than the id matters because a theme that
    cannot drive the mode falls back to another one - the thing that
    went wrong here once already.
    """
    from code_coach.typing import blends
    from code_coach.typing.drills import MODES_BY_ID, theme_for

    resolved = theme_for(theme_id, MODES_BY_ID["reps"])
    langs = [
        THEMES_BY_ID[part].language
        for part in blends.split_id(resolved.id)
        if part in THEMES_BY_ID and THEMES_BY_ID[part].language
    ]
    return langs or ([resolved.language] if resolved.language else [])


def _served_shape(text: str, languages: list[str]) -> str | None:
    """The shape id of a drilled line, whichever language describes it."""
    for language in languages:
        key = shapes.shape_key(text, language)
        if key:
            return shapes.shape_id(key)
    return None


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




class ShapeIdTests(unittest.TestCase):
    """Ids the picker sends back, which have to survive a query string."""

    def test_ids_are_unique_within_a_theme(self) -> None:
        """Two shapes sharing an id would silently drill the wrong one,
        and slugging is lossy enough that this has to be checked rather
        than assumed."""
        for theme_id in DRILLABLE:
            ids = [s["id"] for s in shape_catalog(theme_id)]
            with self.subTest(theme=theme_id):
                self.assertEqual(len(ids), len(set(ids)), ids)

    def test_ids_are_url_safe(self) -> None:
        import re

        for theme_id in DRILLABLE:
            for entry in shape_catalog(theme_id):
                with self.subTest(id=entry["id"]):
                    self.assertRegex(entry["id"], r"^[a-z0-9-]+$")

    def test_ids_are_stable_across_calls(self) -> None:
        """A picker that sends back an id from a moment ago has to
        still match. Hashing on anything per-process would break this
        and only in production."""
        first = [s["id"] for s in shape_catalog("pycode")]
        second = [s["id"] for s in shape_catalog("pycode")]
        self.assertEqual(first, second)


class ShapeCatalogTests(unittest.TestCase):

    def test_the_catalogue_matches_what_can_be_drilled(self) -> None:
        for theme_id in DRILLABLE:
            listed = {s["id"] for s in shape_catalog(theme_id)}
            actual = {
                shapes.shape_id(key)
                for key, _l, _ls in _shape_sets(THEMES_BY_ID[theme_id])
            }
            with self.subTest(theme=theme_id):
                self.assertEqual(listed, actual)

    def test_the_count_is_the_real_number_of_lines(self) -> None:
        """Shown to help you choose, so it has to be true."""
        by_id = {
            shapes.shape_id(key): lines
            for key, _l, lines in _shape_sets(THEMES_BY_ID["jscode"])
        }
        for entry in shape_catalog("jscode"):
            with self.subTest(id=entry["id"]):
                self.assertEqual(entry["count"], len(by_id[entry["id"]]))

    def test_the_example_is_a_line_of_that_shape(self) -> None:
        for entry in shape_catalog("pycode"):
            with self.subTest(id=entry["id"]):
                self.assertEqual(
                    shapes.shape_id(shapes.shape_key(entry["example"], "python")),
                    entry["id"],
                )

    def test_commonest_first(self) -> None:
        for theme_id in DRILLABLE:
            counts = [s["count"] for s in shape_catalog(theme_id)]
            with self.subTest(theme=theme_id):
                self.assertEqual(counts, sorted(counts, reverse=True))

    def test_the_catalogue_always_matches_what_the_drill_serves(self) -> None:
        """The invariant this replaced a wrong test with.

        The first version asserted that a prose theme lists no shapes,
        which was true and was the bug: the drill fell back to Python
        and drilled Python shapes while the picker showed "No shapes",
        so the menu described a pool nothing was drawing from. What
        matters is not how many are listed, it is that the list is the
        one the drill will use.
        """
        for theme_id in (*DRILLABLE, "scripture", "mixed", "python",
                         "pycode,jscode"):
            listed = {s["id"] for s in shape_catalog(theme_id)}
            served = set()
            for seed in range(12):
                drill = build_drill(
                    "everything", "reps", theme_id=theme_id,
                    seed=f"c{seed}", count=4,
                )
                languages = _languages_of(theme_id)
                for target in drill.targets:
                    found = _served_shape(target.text, languages)
                    self.assertIsNotNone(found, target.text)
                    served.add(found)
            with self.subTest(theme=theme_id):
                self.assertTrue(listed)
                self.assertTrue(
                    served <= listed,
                    f"drilled shapes the picker never listed: {served - listed}",
                )


class ChosenShapeTests(unittest.TestCase):

    def test_asking_for_a_shape_gets_that_shape(self) -> None:
        """The whole point of the picker."""
        for theme_id, language in (("pycode", "python"),
                                   ("jscode", "javascript")):
            for entry in shape_catalog(theme_id):
                drill = build_drill(
                    "everything", "reps", theme_id=theme_id,
                    seed="fixed", count=8, shape_id=entry["id"],
                )
                keys = {
                    shapes.shape_id(shapes.shape_key(t.text, language))
                    for t in drill.targets
                }
                with self.subTest(theme=theme_id, shape=entry["id"]):
                    self.assertEqual(keys, {entry["id"]})

    def test_the_seed_no_longer_decides_which_shape(self) -> None:
        """Asked for by name, every seed has to give the same shape -
        otherwise the picker is a suggestion."""
        wanted = shape_catalog("jscode")[3]["id"]
        for seed in range(15):
            drill = build_drill(
                "everything", "reps", theme_id="jscode",
                seed=f"s{seed}", count=6, shape_id=wanted,
            )
            got = shapes.shape_id(
                shapes.shape_key(drill.targets[0].text, "javascript")
            )
            with self.subTest(seed=seed):
                self.assertEqual(got, wanted)

    def test_no_shape_asked_for_still_draws_one(self) -> None:
        """The old behaviour is the default and has to keep working."""
        drill = build_drill(
            "everything", "reps", theme_id="pycode", seed="d", count=6
        )
        self.assertTrue(drill.targets)

    def test_a_shape_the_theme_lacks_falls_back(self) -> None:
        """The picker can hold a stale id for a moment after the text
        changes. Losing the shape is the right cost; losing the drill
        is not."""
        drill = build_drill(
            "everything", "reps", theme_id="pycode",
            seed="x", count=6, shape_id="not-a-shape-at-all",
        )
        self.assertTrue(drill.targets)


class ShapeApiTests(unittest.TestCase):

    def test_the_endpoint_lists_a_themes_shapes(self) -> None:
        from code_coach.api.server import typing_shapes

        got = typing_shapes(theme="jscode")
        self.assertEqual(got.theme, "jscode")
        self.assertTrue(got.shapes)
        self.assertTrue(all(s.count >= shapes.MIN_LINES for s in got.shapes))

    def test_the_endpoint_rejects_an_unknown_theme(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.server import typing_shapes

        with self.assertRaises(HTTPException) as caught:
            typing_shapes(theme="nope")
        self.assertEqual(caught.exception.status_code, 404)

    def test_the_drill_endpoint_honours_a_shape(self) -> None:
        from code_coach.api.server import typing_drill, typing_shapes

        wanted = typing_shapes(theme="pycode").shapes[2]
        got = typing_drill(
            section="everything", mode="reps", theme="pycode",
            count=8, shape=wanted.id,
        )
        keys = {
            shapes.shape_id(shapes.shape_key(t.text, "python"))
            for t in got.targets
        }
        self.assertEqual(keys, {wanted.id})

    def test_a_blend_lists_shapes_from_both(self) -> None:
        from code_coach.api.server import typing_shapes

        got = typing_shapes(theme="pycode,jscode")
        only_py = {s.id for s in typing_shapes(theme="pycode").shapes}
        self.assertTrue({s.id for s in got.shapes} - only_py)


if __name__ == "__main__":
    unittest.main()
