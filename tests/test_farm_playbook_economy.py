"""Playbook economy tips: what the snippets actually do on a real farm.

tests/test_farm_playbook.py already gates every entry (these ones included)
and starts it on a bare farm in every language. These tests hold the economy
tips to their word: each group has a farm arranged so that the snippet's
claim shows - the checkerboard has no two trees side by side, the mowing
pays hay as the Grass upgrade says, fertilized plants grow faster and pay
Weird Substance, the sunflower scan earns the bonus in fewer ticks than the
nine passes, the sorted cacti pay their square, the dinosaur eats a dozen
apples, and the barn guards keep their reserve.
"""

from __future__ import annotations

import random
import re
import unittest

from code_coach.farm import data
from code_coach.farm.playbook import ENTRIES
from tests.test_farm_playbook import (
    LANGUAGES,
    calling,
    explain,
    ripe,
    run,
    said,
    world_for,
)

BY_ID = {entry.id: entry for entry in ENTRIES}


def ok(case: unittest.TestCase, h, status: str) -> None:
    case.assertEqual(status, "done", explain(h, status))


def bare(tile, ground: str = "Soil") -> None:
    """An empty tile of the given ground."""
    tile.ground = ground
    tile.entity = None
    tile.need = tile.grown = 0.0
    tile.companion = None


def growing(tile, entity: str, need: float = 900.0, **fields) -> None:
    """A plant in soil that is nowhere near ripe."""
    ripe(tile, entity, need=need, grown=0.0, **fields)


def without(code: str, old: str) -> str:
    """The snippet with its closing call taken out - the call must be there once."""
    return calling(code, old, "")


# ── Grass and hay ───────────────────────────────────────────────────────


class GrassTests(unittest.TestCase):
    def test_mowing_cuts_every_ripe_tile_and_each_grass_upgrade_doubles_a_cut(self) -> None:
        e = BY_ID["grass-mow"]
        for language in LANGUAGES:
            for level in (1, 3):
                with self.subTest(language=language, grass=level):
                    w = world_for(e, items={}, Grass=level)
                    h, status = run(w, language, e.snippets[language])
                    ok(self, h, status)
                    self.assertEqual(w.items["Hay"], 9 * 2 ** (level - 1))
            with self.subTest(language=language, case="one tile not ripe"):
                w = world_for(e, items={})
                w.at(1, 1).need, w.at(1, 1).grown = 900.0, 0.0
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(w.items["Hay"], 8)  # the unripe one was left standing
                self.assertEqual(w.at(1, 1).need, 900.0)

    def test_the_cut_is_counted_from_the_barn_and_waits_for_ripe_grass(self) -> None:
        e = BY_ID["grass-hay-per-cut"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={}, Grass=3)
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(said(h), ["hay per cut: 4"])
                # Grass that is not ripe: it flips (a second) until it is, and throws nothing away.
                young = world_for(e, items={})
                young.here().need, young.here().grown = 2.5, 0.0
                before = young.time
                h, status = run(young, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(said(h), ["hay per cut: 1"])
                self.assertGreaterEqual(young.time - before, 2.0)


# ── Trees and bushes ────────────────────────────────────────────────────


class TreeTests(unittest.TestCase):
    def test_the_checkerboard_never_puts_two_trees_side_by_side(self) -> None:
        e = BY_ID["trees-checkerboard"]
        n = 4
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, Expand=3)
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                for x in range(n):
                    for y in range(n):
                        want = "Tree" if (x + y) % 2 == 0 else "Bush"
                        self.assertEqual(w.at(x, y).entity, want, (x, y))
                trees = {(x, y) for x in range(n) for y in range(n) if w.at(x, y).entity == "Tree"}
                for x, y in trees:
                    self.assertFalse({(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)} & trees)
                # Nothing slows them: every tree is ripe by the slowest growing time.
                w.advance(data.PLANTS["Tree"].grow[1] + 0.1)
                self.assertTrue(all(t.ripe for t in w.tiles))

    def test_a_solid_field_of_trees_is_the_slow_one(self) -> None:
        e = BY_ID["trees-checkerboard"]
        w = world_for(e, Expand=3)
        for t in w.tiles:
            ripe(t, "Tree", need=data.PLANTS["Tree"].grow[1], grown=0.0)
        w.advance(data.PLANTS["Tree"].grow[1] + 0.1)
        self.assertFalse(all(t.ripe for t in w.tiles))  # crowded trees take twice, four times as long

    def test_the_wood_loop_sets_up_from_grass_then_takes_the_wood(self) -> None:
        e = BY_ID["trees-wood-loop"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                hay = w.items["Hay"]
                self.assertGreaterEqual(hay, 9)  # the grass it cut on the way (a companion pays more)
                self.assertEqual(w.items["Wood"], 0)
                w.advance(data.PLANTS["Tree"].grow[1] + 0.6)
                for t in w.tiles:
                    t.companion = None  # a lucky neighbour would pay five times; count the plain yield
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(w.items["Wood"], 5 * 5 + 4 * 1)  # five trees, four bushes
                self.assertEqual(w.items["Hay"], hay)  # no grass left to cut
                kinds = [[w.at(x, y).entity for x in range(3)] for y in range(3)]
                self.assertEqual(kinds, [["Tree", "Bush", "Tree"], ["Bush", "Tree", "Bush"],
                                         ["Tree", "Bush", "Tree"]])


# ── Carrots ─────────────────────────────────────────────────────────────

#: Where each language's snippet turns into "farm for a goal", and what to put there instead:
#: just one pass over the field.
ONE_PASS = {
    "original": ("goal = ", "tend_field()\n"),
    "python": ("goal = ", "tend_field()\n"),
    "javascript": ("const goal", "tendField();\n"),
    "dart": ("void main() {", "void main() {\n  tendField();\n}\n"),
}


class CarrotTests(unittest.TestCase):
    def test_the_first_plot_tills_plants_and_counts_what_went_in(self) -> None:
        e = BY_ID["carrots-first-plot"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={"Hay": 100, "Wood": 100})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(said(h), ["planted 9"])
                self.assertTrue(all((t.ground, t.entity) == ("Soil", "Carrot") for t in w.tiles))
                self.assertEqual((w.items["Hay"], w.items["Wood"]), (91, 91))  # 1 and 1 each
            with self.subTest(language=language, case="short of hay"):
                w = world_for(e, items={"Hay": 4, "Wood": 100})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(said(h), ["planted 4"])
                self.assertEqual(w.items["Hay"], 0)
                self.assertEqual(sum(t.entity == "Carrot" for t in w.tiles), 4)

    def test_a_pass_handles_every_kind_of_tile_and_never_tills_soil_back(self) -> None:
        e = BY_ID["carrots-tend-loop"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                marker, one_pass = ONE_PASS[language]
                code = e.snippets[language]
                code = code[: code.index(marker)] + one_pass
                w = world_for(e, items={"Hay": 100, "Wood": 100})
                h, status = run(w, language, code)  # bare grass: till and plant
                ok(self, h, status)
                self.assertTrue(all((t.ground, t.entity) == ("Soil", "Carrot") for t in w.tiles))
                w.advance(data.PLANTS["Carrot"].grow[1] + 0.1)
                h, status = run(w, language, code)  # ripe: harvest and plant again, no till
                ok(self, h, status)
                self.assertEqual(w.items["Carrot"], 9)
                self.assertTrue(all((t.ground, t.entity) == ("Soil", "Carrot") for t in w.tiles))
                self.assertEqual((w.items["Hay"], w.items["Wood"]), (82, 82))

    def test_the_goal_loop_stops_once_there_are_enough_carrots(self) -> None:
        e = BY_ID["carrots-tend-loop"]
        for language in ("original", "python"):
            with self.subTest(language=language):
                w = world_for(e, items={"Hay": 500, "Wood": 500, "Carrot": 0})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertGreaterEqual(w.items["Carrot"], 20)
                self.assertLess(w.items["Carrot"], 20 + 9)  # one pass over the goal at most


# ── Water and fertilizer ────────────────────────────────────────────────


class WaterTests(unittest.TestCase):
    def test_every_tile_is_topped_up_while_the_barn_has_water(self) -> None:
        e = BY_ID["water-field"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={"Water": 100})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertTrue(all(t.water >= 0.4 for t in w.tiles), [t.water for t in w.tiles])
                self.assertTrue(18 <= 100 - w.items["Water"] <= 36)  # 2 to 4 tanks a tile
            with self.subTest(language=language, case="a short barn"):
                w = world_for(e, items={"Water": 5})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)  # stops by itself, with every tank spent
                self.assertEqual(w.items["Water"], 0)

    def test_only_growing_plants_get_a_tank(self) -> None:
        e = BY_ID["water-only-growing"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={"Water": 100})
                bare(w.at(0, 0))                     # empty soil
                # (0, 1) stays ripe grass
                ripe(w.at(0, 2), "Carrot")           # ripe carrot
                still_growing = [(1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
                for x, y in still_growing:
                    growing(w.at(x, y), "Carrot")
                w._changed()
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                for x in range(3):
                    for y in range(3):
                        if (x, y) in still_growing:
                            self.assertGreaterEqual(w.at(x, y).water, 0.5, (x, y))
                        else:
                            self.assertEqual(w.at(x, y).water, 0.0, (x, y))


class FertilizerTests(unittest.TestCase):
    def test_fertilized_grass_pays_weird_substance_and_no_hay(self) -> None:
        e = BY_ID["fertilizer-weird"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={"Fertilizer": 6})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(w.items["Weird_Substance"], 5)
                self.assertEqual(w.items["Fertilizer"], 1)
            with self.subTest(language=language, case="no fertilizer"):
                w = world_for(e, items={})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)  # it gives up at once, no endless loop
                self.assertEqual(w.items["Weird_Substance"], 0)

    def test_the_pass_takes_two_seconds_off_and_infects_then_harvests_half_as_weird(self) -> None:
        e = BY_ID["fertilizer-pass"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                def field(fertilizer: int):
                    w = world_for(e, items={"Fertilizer": fertilizer})
                    for t in w.tiles:
                        growing(t, "Tree", need=20.0)
                    return w

                fed, control = field(20), field(0)
                for w in (fed, control):
                    h, status = run(w, language, e.snippets[language])
                    ok(self, h, status)
                # One dose a tile (and the barn's own delivery every ten seconds).
                self.assertIn(fed.items["Fertilizer"], (11, 12))
                for a, b in zip(fed.tiles, control.tiles):
                    self.assertTrue(a.infected and not b.infected)
                    self.assertGreaterEqual(a.grown - b.grown, data.FERTILIZER_SECONDS - 1e-6)
                # Ripe and infected: half the tree's 5 wood (rounded down) is Weird Substance.
                for t in fed.tiles:
                    t.grown = t.need
                fed.items["Wood"] = fed.items["Weird_Substance"] = 0
                h, status = run(fed, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual((fed.items["Wood"], fed.items["Weird_Substance"]), (27, 18))
                self.assertFalse(any(t.entity == "Tree" for t in fed.tiles))


# ── Companions ──────────────────────────────────────────────────────────


class CompanionTests(unittest.TestCase):
    def test_the_wished_for_bush_or_tree_is_planted_there_and_the_drone_comes_back(self) -> None:
        e = BY_ID["companion-plant-wish"]
        cases = [
            (("Bush", 2, 1), "Bush"),
            (("Tree", 1, 2), "Tree"),
            (("Carrot", 2, 2), "Grass"),   # a carrot would need till() first: left alone
            (("Grass", 1, 1), "Grass"),    # the grass is already there
            (None, "Grass"),
        ]
        for language in LANGUAGES:
            for wish, planted in cases:
                with self.subTest(language=language, wish=wish):
                    w = world_for(e)
                    w.here().companion = wish
                    h, status = run(w, language, e.snippets[language])
                    ok(self, h, status)
                    self.assertEqual((w.x, w.y), (0, 0))
                    if wish:
                        self.assertEqual(w.at(wish[1], wish[2]).entity, planted)
                    others = [t.entity for t in w.tiles if t.entity != "Grass"]
                    self.assertEqual(others, [] if planted == "Grass" else [planted])

    def test_planting_the_wish_multiplies_the_harvest_by_five(self) -> None:
        e = BY_ID["companion-plant-wish"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={})
                w.here().companion = ("Bush", 2, 1)
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                w.call("harvest", [])
                self.assertEqual(w.items["Hay"], data.COMPANION_MULTIPLIER)

    def test_it_harvests_only_when_the_friend_is_there(self) -> None:
        e = BY_ID["companion-check-friend"]
        for language in LANGUAGES:
            with self.subTest(language=language, friend="standing"):
                w = world_for(e, items={})
                w.here().companion = ("Bush", 1, 0)
                growing(w.at(1, 0), "Bush", need=900.0)
                w._changed()
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(w.items["Hay"], data.COMPANION_MULTIPLIER)
                self.assertEqual((w.x, w.y), (0, 0))
            with self.subTest(language=language, friend="missing"):
                w = world_for(e, items={})
                w.here().companion = ("Bush", 1, 0)  # (1, 0) is only grass
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(w.items["Hay"], 0)
                self.assertEqual(w.here().entity, "Grass")
                self.assertEqual((w.x, w.y), (0, 0))
            with self.subTest(language=language, friend="none wanted"):
                w = world_for(e, items={})
                w.here().companion = None
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(w.items["Hay"], 1)


# ── Sunflower power ─────────────────────────────────────────────────────

PETALS = [15, 15, 14, 13, 12, 12, 11, 10, 10, 9, 9, 8, 8, 7, 7, 7]


def sunflower_field(e, seed: int = 5):
    w = world_for(e, Expand=3, items={})
    order = list(PETALS)
    random.Random(seed).shuffle(order)
    for tile, petals in zip(w.tiles, order):
        ripe(tile, "Sunflower", petals=petals)
    w._changed()
    return w


class SunflowerTests(unittest.TestCase):
    def test_the_field_says_whether_the_bonus_is_possible(self) -> None:
        e = BY_ID["sunflower-field"]
        for language in LANGUAGES:
            with self.subTest(language=language, farm="4 by 4"):
                w = world_for(e, Expand=3)
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(said(h), ["16 sunflowers: the bonus is possible"])
                self.assertTrue(all((t.ground, t.entity) == ("Soil", "Sunflower") for t in w.tiles))
                self.assertTrue(all(7 <= t.petals <= 15 for t in w.tiles))
            with self.subTest(language=language, farm="3 by 3"):
                w = world_for(e)
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(said(h), ["9 sunflowers: too few for the bonus"])
            with self.subTest(language=language, farm="a short barn"):
                w = world_for(e, Expand=3, items={"Carrot": 5})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(said(h), ["5 sunflowers: too few for the bonus"])

    def test_the_scan_earns_the_bonus_in_fewer_ticks_than_the_passes(self) -> None:
        e = BY_ID["sunflower-scan-harvest"]
        bonus_ceiling = 7 * data.SUNFLOWER_BONUS + 9  # sixteen flowers: seven bonuses
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = sunflower_field(e)
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertFalse(any(t.entity == "Sunflower" for t in w.tiles))
                self.assertGreater(w.items["Power"], bonus_ceiling - 12)
                self.assertFalse(w.sunflower_spoiled)
        old = BY_ID["sunflower-biggest-first"]
        scan, passes = sunflower_field(e), sunflower_field(old)
        for w, entry in ((scan, e), (passes, old)):
            h, status = run(w, "python", entry.snippets["python"])
            ok(self, h, status)
        self.assertLess(scan.run_ticks, passes.run_ticks)
        self.assertGreaterEqual(scan.items["Power"], passes.items["Power"] - 1)

    def test_a_field_without_sunflowers_is_scanned_and_left_alone(self) -> None:
        e = BY_ID["sunflower-scan-harvest"]
        w = world_for(e, items={})
        h, status = run(w, "python", e.snippets["python"])
        ok(self, h, status)
        self.assertEqual(w.items["Power"], 0)


# ── Cactus: faster sorting ──────────────────────────────────────────────


def cactus_field(w, seed: int) -> None:
    rng = random.Random(seed)
    for tile in w.tiles:
        ripe(tile, "Cactus", size=rng.randrange(data.CACTUS_SIZES))
    w._changed()


class CactusTests(unittest.TestCase):
    def test_the_field_is_planted_in_soil_and_ripe_when_the_snippet_ends(self) -> None:
        e = BY_ID["cactus-plant-field"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={"Pumpkin": 100})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertTrue(all((t.ground, t.entity) == ("Soil", "Cactus") for t in w.tiles))
                self.assertTrue(all(t.ripe for t in w.tiles))  # the flip waited the second
                self.assertTrue(all(0 <= t.size < data.CACTUS_SIZES for t in w.tiles))
                self.assertEqual(w.items["Pumpkin"], 100 - 9 * 2)

    def test_a_sorted_row_is_a_patch_of_its_own_and_pays_its_length_squared(self) -> None:
        e = BY_ID["cactus-row-sort"]
        for language in LANGUAGES:
            for seed in (1, 2) if language in ("original", "python") else (1,):
                with self.subTest(language=language, seed=seed):
                    w = world_for(e, Expand=3, items={"Pumpkin": 100}, seed=seed)
                    h, status = run(w, language, without(e.snippets[language], "harvest()"
                                                         if language in ("original", "python")
                                                         else "harvest();"))
                    ok(self, h, status)
                    sizes = [w.at(x, 0).size for x in range(4)]
                    self.assertEqual(sizes, sorted(sizes))
                    self.assertTrue(all(w.at(x, 0).ripe for x in range(4)))
                    self.assertEqual(sum(t.entity == "Cactus" for t in w.tiles), 4)  # one row
                    w.call("harvest", [])
                    self.assertEqual(w.items["Cactus"], 4 * 4)
                    self.assertEqual(w.items["Pumpkin"], 100 - 4 * 2)

    def test_columns_then_rows_leave_the_whole_field_sorted_and_pay_the_square(self) -> None:
        e = BY_ID["cactus-rows-then-columns"]
        for language in LANGUAGES:
            for seed in (1, 2, 3) if language in ("original", "python") else (1,):
                with self.subTest(language=language, seed=seed):
                    w = world_for(e, Expand=3, items={}, seed=seed)
                    cactus_field(w, seed)
                    h, status = run(w, language, e.snippets[language])
                    ok(self, h, status)
                    self.assertEqual(w.items["Cactus"], (4 * 4) ** 2)
                    self.assertFalse(any(t.entity == "Cactus" for t in w.tiles))
        # The order matters: after the sort every row and every column climbs.
        w = world_for(e, Expand=4, items={}, seed=7)
        cactus_field(w, 7)
        code = without(e.snippets["python"], "harvest()")
        h, status = run(w, "python", code)
        ok(self, h, status)
        grid = [[w.at(x, y).size for x in range(6)] for y in range(6)]
        for row in grid:
            self.assertEqual(row, sorted(row))
        for x in range(6):
            column = [grid[y][x] for y in range(6)]
            self.assertEqual(column, sorted(column))

    def test_the_whole_field_is_the_better_deal_per_tick_than_one_row(self) -> None:
        row, field = BY_ID["cactus-row-sort"], BY_ID["cactus-rows-then-columns"]
        plant = BY_ID["cactus-plant-field"].snippets["python"]
        sort = field.snippets["python"]
        whole = (plant.rsplit("plant_cacti()", 1)[0] + sort.rsplit("sort_field()", 1)[0]
                 + "plant_cacti()\nsort_field()\nharvest()\n")
        one = world_for(row, Expand=3, items={"Pumpkin": 100}, seed=1)
        h, status = run(one, "python", row.snippets["python"])
        ok(self, h, status)
        many = world_for(field, Expand=3, items={"Pumpkin": 100}, seed=1, Plant=1, Carrots=1)
        h, status = run(many, "python", whole)
        ok(self, h, status)
        self.assertEqual((one.items["Cactus"], many.items["Cactus"]), (16, 256))
        # 16 times as much cactus for well under 16 times the ticks.
        self.assertLess(many.run_ticks / one.run_ticks, 16)


# ── Dinosaur and apples ─────────────────────────────────────────────────


class DinosaurTests(unittest.TestCase):
    def test_one_apple_is_eaten_and_the_hat_comes_off_for_a_bone(self) -> None:
        e = BY_ID["dino-first-apple"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={"Cactus": 4})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(w.items["Bone"], 1)       # a tail of one, squared
                self.assertEqual(w.items["Cactus"], 0)     # two apples at 2 cactus
                self.assertEqual(w.hat, "Straw_Hat")
                self.assertNotEqual((w.x, w.y), (0, 0))    # it walked to the second apple
                self.assertFalse(any(t.entity in ("Apple", "Dinosaur") for t in w.tiles))
            with self.subTest(language=language, case="no cactus"):
                w = world_for(e, items={})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual((w.items["Bone"], w.x, w.y), (0, 0, 0))

    def test_the_chaser_eats_a_dozen_apples_and_banks_the_bones(self) -> None:
        e = BY_ID["dino-chaser"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, Expand=5, items={"Cactus": 100}, seed=1)  # an 8 by 8 farm
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                tail = round(w.items["Bone"] ** 0.5)
                self.assertGreaterEqual(tail, 12)
                self.assertEqual(w.items["Bone"], tail * tail)
                self.assertLessEqual(w.items["Cactus"], 100 - 2 * tail)  # 2 cactus an apple
                self.assertEqual(w.hat, "Straw_Hat")
                self.assertFalse(any(t.entity in ("Apple", "Dinosaur") for t in w.tiles))

    def test_it_stops_by_itself_when_the_cactus_runs_out(self) -> None:
        e = BY_ID["dino-chaser"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, Expand=5, items={"Cactus": 6}, seed=1)  # three apples' worth
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(w.items["Bone"], 3 * 3)
                self.assertEqual(w.items["Cactus"], 0)


# ── Gold and the treasure ───────────────────────────────────────────────


class GoldTests(unittest.TestCase):
    def maze_world(self, e, seed: int) -> "object":
        w = world_for(e, seed=seed, Expand=3)
        w.x, w.y = 1, 2
        w._grow_maze(w.w, w.w)
        return w

    def test_the_price_and_the_pay_follow_the_mazes_level(self) -> None:
        e = BY_ID["gold-maze-cost"]
        for language in LANGUAGES:
            for level, cost, gold in ((1, 3, 9), (2, 6, 18)):
                with self.subTest(language=language, mazes=level):
                    w = world_for(e, Mazes=level)
                    h, status = run(w, language, e.snippets[language])
                    ok(self, h, status)
                    self.assertEqual(
                        said(h), [f"a 3 by 3 maze costs {cost} and pays {gold} gold"])
                    self.assertEqual(w.maze.m, 3)
                    self.assertEqual(w.items["Weird_Substance"], 500 - cost)
                    w.x, w.y = w.maze.treasure
                    w.call("harvest", [])
                    self.assertEqual(w.items["Gold"], gold)  # exactly what it said it would pay
            with self.subTest(language=language, case="too little Weird Substance"):
                w = world_for(e, items={"Weird_Substance": 2})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertIsNone(w.maze)
                self.assertEqual((w.items["Weird_Substance"], w.here().entity), (2, "Grass"))

    def test_the_wall_follower_cashes_in_only_on_the_treasure(self) -> None:
        e = BY_ID["gold-cash-in"]
        for language in LANGUAGES:
            for seed in range(1, 5) if language in ("original", "python") else (1, 2):
                with self.subTest(language=language, seed=seed):
                    w = self.maze_world(e, seed)
                    treasure = w.maze.treasure
                    h, status = run(w, language, e.snippets[language])
                    ok(self, h, status)
                    self.assertEqual((w.x, w.y), treasure)
                    self.assertEqual(w.items["Gold"], 16)
                    self.assertIsNone(w.maze)

    def test_can_harvest_is_the_treasure_test_and_a_wrong_harvest_pays_nothing(self) -> None:
        e = BY_ID["gold-cash-in"]
        w = self.maze_world(e, 1)
        cells = [(x, y) for x in range(4) for y in range(4)]
        for x, y in cells:
            w.x, w.y = x, y
            self.assertEqual(w.call("can_harvest", [])[0], (x, y) == w.maze.treasure)
        w.x, w.y = next(c for c in cells if c != w.maze.treasure)
        w.call("harvest", [])
        self.assertEqual(w.items["Gold"], 0)
        self.assertIsNone(w.maze)


# ── Items ───────────────────────────────────────────────────────────────


class ItemTests(unittest.TestCase):
    def test_the_reserve_stays_in_the_barn(self) -> None:
        e = BY_ID["items-reserve"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={"Hay": 52, "Wood": 100})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(sum(t.entity == "Carrot" for t in w.tiles), 2)
                self.assertEqual((w.items["Hay"], w.items["Wood"]), (50, 98))
            with self.subTest(language=language, case="already at the reserve"):
                w = world_for(e, items={"Hay": 50, "Wood": 100})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(sum(t.entity == "Carrot" for t in w.tiles), 0)
                self.assertEqual(w.items["Hay"], 50)

    def test_several_tanks_go_in_as_one_action_and_never_overflow(self) -> None:
        e = BY_ID["items-use-count"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={"Water": 10})
                w.here().water = 0.3
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(w.items["Water"], 8)      # (1 - 0.3) // 0.25 = 2 fit
                self.assertAlmostEqual(w.here().water, 0.8, delta=0.01)
                if language != "original":                 # its own arithmetic costs ticks too
                    self.assertEqual(w.run_ticks // data.ACTION_TICKS, 1)
            with self.subTest(language=language, case="empty ground and a small barn"):
                w = world_for(e, items={"Water": 3})
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(w.items["Water"], 0)      # four fit, the barn had three
                self.assertAlmostEqual(w.here().water, 0.75, delta=0.01)
            with self.subTest(language=language, case="already full"):
                w = world_for(e, items={"Water": 5})
                w.here().water = 1.0
                h, status = run(w, language, e.snippets[language])
                ok(self, h, status)
                self.assertEqual(w.items["Water"], 5)

    def test_it_plants_only_what_the_barn_can_pay_for_at_todays_prices(self) -> None:
        e = BY_ID["items-get-cost"]
        for language in LANGUAGES:
            for carrots, items, planted in (
                (1, {"Hay": 1, "Wood": 1}, 1),
                (1, {"Hay": 0, "Wood": 5}, 0),
                (1, {"Hay": 5, "Wood": 0}, 0),
                (2, {"Hay": 1, "Wood": 1}, 0),   # an upgrade doubles the price...
                (2, {"Hay": 2, "Wood": 2}, 1),   # ...and the check follows it
            ):
                with self.subTest(language=language, carrots=carrots, barn=items):
                    w = world_for(e, items=items, Carrots=carrots)
                    h, status = run(w, language, e.snippets[language])
                    ok(self, h, status)
                    self.assertEqual(w.here().entity == "Carrot", bool(planted))
                    if planted:
                        self.assertEqual((w.items["Hay"], w.items["Wood"]), (0, 0))


class ShapeOfThisGroupTests(unittest.TestCase):
    def test_the_economy_groups_come_in_the_order_asked_for(self) -> None:
        from code_coach.farm import playbook_economy

        groups = list(dict.fromkeys(e.group for e in playbook_economy.ENTRIES))
        self.assertEqual(groups, [
            "Grass and hay", "Trees and bushes", "Carrots", "Water and fertilizer",
            "Companions", "Sunflower power", "Cactus: faster sorting", "Dinosaur and apples",
            "Gold and the treasure", "Items",
        ])
        self.assertGreaterEqual(len(playbook_economy.ENTRIES), 22)
        for entry in playbook_economy.ENTRIES:
            self.assertIn(entry, ENTRIES)
            self.assertTrue(re.fullmatch(r"[a-z]+(-[a-z]+)+", entry.id), entry.id)


if __name__ == "__main__":
    unittest.main()
