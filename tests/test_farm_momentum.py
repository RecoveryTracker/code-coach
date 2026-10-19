"""Farm -> Momentum: milestones paid by the server, the farm quest's items, the welcome-back.

The farm's world is authoritative (programs run far faster than the screen polls, and the
browser is not trusted with "I harvested a pumpkin"), so the host watches the World and pays
through the engine in process. These tests drive real farms: programs in the game's own
language, Python and JavaScript on a FarmHost, and direct actions on its worlds, holding
what is paid to the rules in code_coach/farm/milestones.py's docstring - a first pays once
ever, per language, never when the action failed, never so as to break the farm.

Expected numbers are worked out here: the base prices come from the table's stated XP with
luck switched off, a combo of one pays the base, ripe counts are read off the snapshot's own
cells, welcome pay is 15 + 1 per ten ripe (max 10).
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.encoders import jsonable_encoder

from code_coach import momentum
from code_coach.api import server
from code_coach.farm import data, milestones, scratch
from code_coach.farm.runner import LANGUAGES, FarmHost
from code_coach.farm.world import World
from code_coach.momentum import Momentum, rules
from tests.test_farm_events import MEGA, finish, host
from tests.test_farm_world import call
from tests.test_momentum import D0, Clock, Stub, day, stamp

HAS_NODE = shutil.which("node") is not None
MILESTONE = "farm_milestone"


class Rig:
    """A host whose rewards talk to a throwaway Momentum (luck off, a clock in hand)."""

    def __init__(self, test: unittest.TestCase, when=D0, **levels: int) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="farm-momentum-")
        test.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "momentum.json"
        self.clock = Clock(stamp(when))
        self.engine = Momentum(self.path, clock=self.clock, rng=Stub())
        self.host = host(**levels)
        self.host.language = "python"  # the farm on screen: where `buy` and `welcome` look
        self.host.rewards.engine = self.engine

    def saved(self) -> dict:
        return json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}

    def paid(self) -> list[str]:
        """The milestone ids paid so far, as `<language>:<id>`, in the order paid."""
        return [k.split(":", 1)[1] for k in self.saved().get("once", [])]

    def world(self, language: str = "python") -> World:
        return self.host._world_for(language)

    def xp(self) -> int:
        return self.saved().get("xp", 0)


def stock(w: World, size: int = 6, level: int = 1, **levels: int) -> World:
    """Every unlock researched, a field of `size`, a million of everything: a farm to set up squares on."""
    for name in data.UNLOCKS:
        w.unlocks[name] = max(w.unlocks[name], levels.get(name, level))
    w.width = w.height = size
    w._fill()
    for item in data.ITEMS:
        w.items[item] = 10 ** 6
    w.items["Power"] = 0
    return w


def put(w: World, x: int, y: int, entity: str, ripe: bool = True, size: int = 0) -> None:
    t = w.at(x, y)
    t.ground = "Soil" if data.PLANTS[entity].needs_soil else "Grassland"
    t.entity, t.need, t.grown = entity, 1.0, 1.0 if ripe else 0.0
    t.petals, t.size = (9 if entity == "Sunflower" else 0), size
    w._changed()


class TableIsConsistent(unittest.TestCase):
    def test_ids_are_unique_and_keys_are_unique_per_language(self) -> None:
        ids = [m.id for m in milestones.MILESTONES]
        self.assertEqual(len(ids), len(set(ids)))
        keys = {milestones.key_for(lang, m) for lang in LANGUAGES for m in milestones.MILESTONES}
        self.assertEqual(len(keys), len(LANGUAGES) * len(ids))

    def test_every_row_has_a_price_a_label_and_a_known_trigger(self) -> None:
        triggers = {"harvest", "giant", "patch", "treasure", "drone", "grow", "total"}
        for m in milestones.MILESTONES:
            self.assertIsInstance(m.xp, int, m.id)
            self.assertGreater(m.xp, 0, m.id)
            self.assertTrue(m.label.strip(), m.id)
            self.assertIn(m.trigger, triggers, m.id)

    def test_every_crop_it_names_exists_in_the_world(self) -> None:
        named = [str(m.arg) for m in milestones.MILESTONES if m.trigger == "harvest"]
        self.assertTrue(named)
        for crop in named:
            self.assertIn(crop, data.PLANTS)
        self.assertTrue(set(milestones.MAIN_ITEMS) <= set(data.ITEMS))
        for m in milestones.MILESTONES:
            if m.trigger == "grow":
                self.assertTrue(1 <= int(m.arg) < len(data.FARM_SIZES), m.id)
            if m.trigger == "harvest":
                self.assertEqual(m.id, f"harvest_{str(m.arg).lower()}")

    def test_every_expand_size_has_a_step_and_totals_climb(self) -> None:
        sizes = {f"grow_{w}x{h}" for w, h in data.FARM_SIZES[1:]}
        self.assertTrue(sizes <= {m.id for m in milestones.MILESTONES})
        steps = [int(m.arg) for m in milestones.TOTALS]
        self.assertEqual(steps, sorted(set(steps)))
        self.assertTrue(steps and steps[0] >= 1)

    def test_the_price_list_grows_with_the_size_step(self) -> None:
        prices = [m.xp for m in sorted((m for m in milestones.MILESTONES if m.trigger == "grow"),
                                        key=lambda m: int(m.arg))]
        self.assertEqual(prices, sorted(prices))

    def test_labels_read_after_farm_and_name_the_language(self) -> None:
        m = milestones.BY_ID["harvest_pumpkin"]
        self.assertEqual(milestones.label_for("python", m), "Farm: first pumpkin! (Python)")
        self.assertEqual(milestones.label_for("original", m), "Farm: first pumpkin! (Original)")


class FirstHarvests(unittest.TestCase):
    def test_each_crop_pays_its_first_once_and_a_single_one_is_not_a_giant_or_a_patch(self) -> None:
        rig = Rig(self)
        w = stock(rig.world())
        crops = [m for m in milestones.MILESTONES if m.trigger == "harvest"]
        for n, m in enumerate(crops):
            put(w, n % 6, n // 6, str(m.arg))
            w.x, w.y = n % 6, n // 6
            call(w, "harvest")
            self.assertIn(f"python:{m.id}", rig.paid(), m.id)
        paid = rig.paid()
        for m in crops:
            self.assertEqual(paid.count(f"python:{m.id}"), 1, m.id)
        self.assertNotIn("python:giant_pumpkin", paid)
        self.assertNotIn("python:sorted_cactus", paid)
        base = sum(m.xp for m in crops)
        # Every award an instant after the last: the combo climbs a tenth each.
        self.assertGreaterEqual(rig.xp(), base)
        # And a second harvest of each pays nothing more.
        before = (rig.xp(), list(paid))
        for n, m in enumerate(crops):
            put(w, n % 6, n // 6, str(m.arg))
            w.x, w.y = n % 6, n // 6
            call(w, "harvest")
        self.assertEqual((rig.xp(), rig.paid()), before)

    def test_the_first_pays_its_table_price_with_a_combo_of_one(self) -> None:
        rig = Rig(self)
        w = stock(rig.world())
        put(w, 0, 0, "Pumpkin")
        call(w, "harvest")
        got = rig.host.state()["momentum"]
        self.assertEqual(len(got), 1)
        self.assertEqual((got[0]["base"], got[0]["gained"]), (20, 20))  # the wiki-style price in the table
        self.assertEqual(got[0]["label"], "Farm: first pumpkin! (Python)")
        self.assertEqual(rig.xp(), 20)

    def test_a_giant_pumpkin_pays_its_own_first_and_the_pumpkin_one(self) -> None:
        rig = Rig(self)
        w = stock(rig.world())
        for x in range(2):
            for y in range(2):
                put(w, x, y, "Pumpkin")
        w.x = w.y = 0
        call(w, "harvest")
        self.assertEqual(sorted(rig.paid()), ["python:giant_pumpkin", "python:harvest_pumpkin"])
        # A second giant pays nothing; neither does the pumpkin it is.
        xp = rig.xp()
        for x in range(2):
            for y in range(2):
                put(w, x, y, "Pumpkin")
        call(w, "harvest")
        self.assertEqual(rig.xp(), xp)

    def test_a_sorted_cactus_patch_pays_but_a_lone_cactus_does_not(self) -> None:
        rig = Rig(self)
        w = stock(rig.world())
        put(w, 0, 0, "Cactus", size=3)
        w.x = w.y = 0
        call(w, "harvest")
        self.assertEqual(rig.paid(), ["python:harvest_cactus"])
        # Two cacti side by side, the bigger one to the East: sorted, so one harvest takes both.
        put(w, 0, 0, "Cactus", size=2)
        put(w, 1, 0, "Cactus", size=5)
        w.x = w.y = 0
        before = dict(w.items)
        call(w, "harvest")
        self.assertEqual(w.items["Cactus"] - before["Cactus"], 2 ** 2)  # n cacti give n squared
        self.assertEqual(rig.paid(), ["python:harvest_cactus", "python:sorted_cactus"])

    def test_an_unsorted_pair_is_not_a_patch(self) -> None:
        rig = Rig(self)
        w = stock(rig.world())
        put(w, 0, 0, "Cactus", size=7)
        put(w, 1, 0, "Cactus", size=1)  # the smaller one is to the East: not sorted
        w.x = w.y = 0
        call(w, "harvest")
        self.assertEqual(rig.paid(), ["python:harvest_cactus"])

    def test_a_maze_treasure_pays(self) -> None:
        rig = Rig(self)
        w = stock(rig.world(), 6)
        call(w, "plant", "Entities.Bush")
        self.assertTrue(call(w, "use_item", "Items.Weird_Substance", 6))
        self.assertEqual(rig.paid(), [], "growing the maze is not finding the treasure")
        w.x, w.y = w.maze.treasure
        call(w, "harvest")
        self.assertEqual(rig.paid(), ["python:maze_treasure"])

    def test_gold_and_weird_substance_are_not_main_items_for_the_total(self) -> None:
        rig = Rig(self)
        w = stock(rig.world(), 6)
        call(w, "plant", "Entities.Bush")
        call(w, "use_item", "Items.Weird_Substance", 6)
        w.x, w.y = w.maze.treasure
        call(w, "harvest")
        rig.host.rewards.flush()
        # 36 gold came in; the main items' lifetime total did not move.
        self.assertEqual(rig.saved()["farm"]["totals"].get("python", 0), 0)
        self.assertEqual(rig.saved()["days"][D0.isoformat()]["counters"]["farm_items"], 36)


class NeverOnFailure(unittest.TestCase):
    def test_an_unripe_harvest_pays_nothing_and_writes_nothing(self) -> None:
        h = FarmHost()
        h._load()
        tmp = tempfile.TemporaryDirectory(prefix="farm-momentum-")
        self.addCleanup(tmp.cleanup)
        engine = Momentum(Path(tmp.name) / "momentum.json", clock=Clock(stamp(D0)), rng=Stub())
        h.rewards.engine = engine
        w = h._world_for("python")
        self.assertFalse(w.here().ripe)
        call(w, "harvest")
        self.assertFalse(w.events[-1]["ok"])
        h.rewards.flush()
        self.assertFalse(engine.path.exists())

    def test_harvesting_bare_soil_a_dead_pumpkin_and_a_failed_plant_pay_nothing(self) -> None:
        rig = Rig(self)
        w = stock(rig.world())
        w.at(0, 0).ground, w.at(0, 0).entity = "Soil", None
        call(w, "harvest")
        put(w, 1, 0, "Pumpkin")
        w.at(1, 0).entity = "Dead_Pumpkin"
        w.x = 1
        call(w, "harvest")
        w.items["Carrot"] = 0
        w.x = w.y = 3
        call(w, "plant", "Entities.Pumpkin")  # grass, not soil, and no carrots to pay with
        self.assertEqual([e["ok"] for e in w.events], [False, False, False])
        rig.host.rewards.flush()
        self.assertEqual(rig.paid(), [])
        self.assertEqual(rig.xp(), 0)

    def test_a_failed_purchase_does_not_pay_a_size_step(self) -> None:
        rig = Rig(self)
        w = rig.world()
        w.unlocks["Loops"] = 1
        self.assertFalse(rig.host.buy("Expand"))  # no hay to pay with
        self.assertEqual(rig.paid(), [])
        self.assertFalse(rig.path.exists())

    def test_a_refused_spawn_pays_no_drone(self) -> None:
        rig = Rig(self, Functions=1)  # no Megafarm: spawn_drone is refused and the program stops with an error
        code = "def f():\n    harvest()\n\nspawn_drone(f)\n"
        self.assertTrue(rig.host.start("python", code)["ok"])
        self.assertEqual(finish(rig.host), "error")
        self.assertNotIn("python:first_drone", rig.paid())


class GrowthSteps(unittest.TestCase):
    def test_buying_expand_pays_the_size_it_reaches_once(self) -> None:
        rig = Rig(self)
        w = rig.world()
        w.unlocks["Loops"] = 1
        w.items["Hay"], w.items["Wood"] = 100, 100
        self.assertTrue(rig.host.buy("Expand"))
        self.assertEqual(rig.paid(), ["python:grow_1x3"])  # the first Expand makes a column of three
        self.assertTrue(rig.host.buy("Expand"))
        self.assertEqual(rig.paid(), ["python:grow_1x3", "python:grow_3x3"])  # the second, a square
        got = rig.host.state()["momentum"]
        self.assertEqual([g["label"] for g in got],
                         ["Farm: expanded to 1x3! (Python)", "Farm: expanded to 3x3! (Python)"])
        # Start the farm over and grow it again: the steps are firsts, not repeats.
        rig.host.reset()
        w = rig.world()
        w.unlocks["Loops"] = 1
        w.items["Hay"], w.items["Wood"] = 100, 100
        xp = rig.xp()
        self.assertTrue(rig.host.buy("Expand"))
        self.assertEqual(rig.xp(), xp)
        self.assertNotIn("momentum", rig.host.state())

    def test_a_program_that_unlocks_expand_pays_it_too(self) -> None:
        rig = Rig(self, Loops=1, Auto_Unlock=1, Costs=1)
        w = rig.world()
        w.items["Hay"] = 50
        self.assertTrue(rig.host.start("python", "unlock(Unlocks.Expand)\n")["ok"])
        self.assertEqual(finish(rig.host), "done", rig.host.run.error)
        self.assertEqual(rig.paid(), ["python:grow_1x3"])

    def test_each_languages_farm_grows_on_its_own(self) -> None:
        rig = Rig(self)
        for lang in ("python", "original"):
            w = rig.world(lang)
            w.unlocks["Loops"] = 1
            w.items["Hay"] = 40
        rig.host.language = "python"
        self.assertTrue(rig.host.buy("Expand"))
        rig.host.language = "original"
        self.assertTrue(rig.host.buy("Expand"))
        self.assertEqual(sorted(rig.paid()), ["original:grow_1x3", "python:grow_1x3"])


class Totals(unittest.TestCase):
    def harvest_hay(self, rig: Rig, language: str, times: int, grass_level: int) -> int:
        w = rig.world(language)
        w.unlocks["Grass"] = grass_level
        got = 0
        for _ in range(times):
            w.advance(1)
            before = w.items["Hay"]
            call(w, "harvest")
            got += int(w.items["Hay"] - before)
        return got

    def test_crossing_100_1000_and_10000_pays_each_once_even_when_one_flush_jumps_two(self) -> None:
        rig = Rig(self)
        got = self.harvest_hay(rig, "python", 3, 10)  # 3 x 512 hay
        self.assertEqual(got, 3 * 512)
        rig.host.rewards.flush()
        self.assertEqual(sorted(p for p in rig.paid() if "total" in p), ["python:total_100", "python:total_1000"])
        got = self.harvest_hay(rig, "python", 18, 10)
        rig.host.rewards.flush()
        self.assertEqual(sorted(p for p in rig.paid() if "total" in p),
                         ["python:total_100", "python:total_1000", "python:total_10000"])
        xp = rig.xp()
        self.harvest_hay(rig, "python", 5, 10)
        rig.host.rewards.flush()
        self.assertEqual(rig.xp(), xp)
        self.assertEqual(rig.saved()["farm"]["totals"]["python"], (3 + 18 + 5) * 512)

    def test_below_the_step_pays_nothing(self) -> None:
        rig = Rig(self)
        self.assertEqual(self.harvest_hay(rig, "python", 6, 4), 6 * 8)  # 48 hay
        rig.host.rewards.flush()
        self.assertEqual([p for p in rig.paid() if "total" in p], [])

    def test_each_language_counts_its_own_harvest(self) -> None:
        rig = Rig(self)
        self.harvest_hay(rig, "python", 4, 5)  # 4 x 16 = 64
        self.harvest_hay(rig, "original", 4, 5)
        rig.host.rewards.flush()
        self.assertEqual([p for p in rig.paid() if "total" in p], [], "64 and 64 are not 128 of one farm")
        self.harvest_hay(rig, "python", 3, 5)  # python is at 112
        rig.host.rewards.flush()
        self.assertEqual([p for p in rig.paid() if "total" in p], ["python:total_100"])
        self.assertEqual(rig.saved()["farm"]["totals"], {"python": 112, "original": 64})

    def test_the_flush_is_rate_limited_and_a_run_ending_flushes(self) -> None:
        rig = Rig(self)
        rig.host.rewards.FLUSH_SECONDS = 10_000.0
        self.assertTrue(rig.host.start("python", "harvest()\nharvest()\nharvest()\n")["ok"])
        self.assertEqual(finish(rig.host), "done")
        # three hay harvested, handed to the engine at the end of the run, not before
        self.assertEqual(rig.saved()["days"][D0.isoformat()]["counters"]["farm_items"], 3)


class ProgramsInEveryLanguage(unittest.TestCase):
    def run_once(self, rig: Rig, language: str, code: str) -> None:
        self.assertTrue(rig.host.start(language, code)["ok"])
        self.assertEqual(finish(rig.host), "done", rig.host.run.error)

    def test_python_pays_the_first_hay_once_across_repeated_runs(self) -> None:
        rig = Rig(self)
        self.run_once(rig, "python", "harvest()\n")
        self.assertEqual(rig.paid(), ["python:harvest_grass"])
        self.assertEqual(rig.xp(), 10)
        first = rig.host.state()["momentum"]
        self.assertEqual([g["label"] for g in first], ["Farm: first hay! (Python)"])
        self.assertNotIn("momentum", rig.host.state(), "drained on read")
        for _ in range(2):
            self.run_once(rig, "python", "harvest()\nharvest()\n")
        self.assertEqual(rig.paid(), ["python:harvest_grass"])
        self.assertEqual(rig.xp(), 10)
        self.assertNotIn("momentum", rig.host.state())

    @unittest.skipUnless(HAS_NODE, "needs node")
    def test_javascript_pays_once_across_repeated_runs(self) -> None:
        rig = Rig(self)
        self.run_once(rig, "javascript", "harvest();\n")
        self.assertEqual(rig.paid(), ["javascript:harvest_grass"])
        self.run_once(rig, "javascript", "harvest();\nharvest();\n")
        self.assertEqual(rig.paid(), ["javascript:harvest_grass"])
        self.assertEqual(rig.xp(), 10)

    def test_the_games_own_language_pays_once_across_repeated_runs(self) -> None:
        rig = Rig(self)
        self.run_once(rig, "original", "harvest()\n")
        self.assertEqual(rig.paid(), ["original:harvest_grass"])
        self.run_once(rig, "original", "harvest()\nharvest()\n")
        self.assertEqual(rig.paid(), ["original:harvest_grass"])
        self.assertEqual(rig.xp(), 10)

    @unittest.skipUnless(HAS_NODE, "needs node")
    def test_every_language_pays_its_own_first_and_not_another_languages(self) -> None:
        rig = Rig(self)
        self.run_once(rig, "python", "harvest()\n")
        self.assertEqual(rig.paid(), ["python:harvest_grass"])
        self.run_once(rig, "javascript", "harvest();\n")
        self.run_once(rig, "original", "harvest()\n")
        self.assertEqual(sorted(rig.paid()),
                         ["javascript:harvest_grass", "original:harvest_grass", "python:harvest_grass"])
        labels = [g["label"] for g in rig.host.state()["momentum"]]
        self.assertEqual(sorted(labels), sorted(f"Farm: first hay! ({n})"
                                                for n in ("Python", "JavaScript", "Original")))
        for lang, code in (("python", "harvest()\n"), ("javascript", "harvest();\n"),
                           ("original", "harvest()\n")):
            self.run_once(rig, lang, code)
        self.assertEqual(len(rig.paid()), 3)

    def test_a_spawned_drone_pays_the_first_drone_once(self) -> None:
        rig = Rig(self, **MEGA)
        code = ("def column():\n    harvest()\n\nother = spawn_drone(column)\nwait_for(other)\n")
        self.run_once(rig, "python", code)
        self.assertEqual(sorted(rig.paid()), ["python:first_drone", "python:harvest_grass"])
        self.run_once(rig, "python", code)
        self.assertEqual(len(rig.paid()), 2)

    def test_a_spawn_that_fails_for_want_of_a_free_drone_pays_no_drone(self) -> None:
        rig = Rig(self, **MEGA)  # Megafarm 1 allows two drones: the third spawn fails (returns None)
        code = ("def f():\n    harvest()\n\na = spawn_drone(f)\nb = spawn_drone(f)\nwait_for(a)\n")
        self.run_once(rig, "python", code)
        self.assertEqual(rig.paid().count("python:first_drone"), 1)

    def test_a_simulation_s_farm_is_not_the_players(self) -> None:
        rig = Rig(self, Loops=1, Speed=1, Expand=2, Plant=1, Senses=1, Operators=1, Variables=1,
                  Functions=1, Lists=1, Dictionaries=1, Megafarm=1, Simulation=1)
        h = rig.host
        # The trial file harvests twice on the simulated farm (the second is ripe: a real harvest).
        h.files["python"]["trial"] = "harvest()\nharvest()\n"
        self.assertTrue(h.start("python", "simulate('trial', [], {}, {}, 1, 0)\n", "main")["ok"])
        self.assertEqual(finish(h), "done", h.run.error)
        self.assertTrue(any("took" in line["text"] for line in h.output), h.output)
        # None of it was the player's farm: no first hay, nothing counted, nothing written.
        self.assertEqual(rig.paid(), [])
        self.assertFalse(rig.path.exists())
        sim = World.for_simulation({"unlocks": {}, "items": {}, "globals": {}, "seed": 1, "file": "x",
                                    "speedup": 0.0})
        self.assertIsNone(sim.listener)

    def test_the_throwaway_scratch_farm_pays_nothing(self) -> None:
        world = scratch.make_world()
        world.advance(5)
        sh = scratch._ScratchHost(world)
        self.assertIsNone(sh.rewards)
        self.assertTrue(sh.start("original", "harvest()\ntill()\n", "main")["ok"])
        finish(sh)
        self.assertNotIn("momentum", sh.state())
        self.assertFalse(momentum.MOMENTUM.path.exists(), "the app's own momentum file was never touched")


class TheFarmSurvivesAMomentumThatFails(unittest.TestCase):
    class Broken(Momentum):
        def award_server(self, *a, **k):
            raise RuntimeError("momentum is down")

        def record_farm_items(self, *a, **k):
            raise RuntimeError("momentum is down")

        def farm_touch(self, *a, **k):
            raise RuntimeError("momentum is down")

        def farm_visit(self, *a, **k):
            raise RuntimeError("momentum is down")

        def claim_welcome(self, *a, **k):
            raise RuntimeError("momentum is down")

    def test_a_run_finishes_and_harvests_normally_when_every_engine_call_raises(self) -> None:
        h = host()
        h.rewards.engine = self.Broken(Path(tempfile.gettempdir()) / "never-written.json")
        before = dict(h._load().items)
        self.assertTrue(h.start("python", "harvest()\nharvest()\n")["ok"])
        self.assertEqual(finish(h), "done", h.run.error)
        self.assertEqual(h._load().items["Hay"] - before["Hay"], 2)
        state = h.state()
        self.assertNotIn("momentum", state)
        self.assertEqual(state["items"]["Hay"], before["Hay"] + 2)
        self.assertIsNone(h.welcome())
        self.assertFalse(h.claim_welcome()["ok"])

    def test_a_purchase_and_a_world_action_survive_it_too(self) -> None:
        h = host()
        h.rewards.engine = self.Broken(Path(tempfile.gettempdir()) / "never-written.json")
        h.language = "python"
        w = h._world_for("python")
        w.unlocks["Loops"] = 1
        w.items["Hay"] = 100
        self.assertTrue(h.buy("Expand"))
        self.assertEqual((w.w, w.h), (1, 3))
        w.advance(5)  # the new field's grass ripens
        call(w, "harvest")
        self.assertTrue(w.events[-1]["ok"])

    def test_a_listener_that_raises_cannot_break_the_world(self) -> None:
        w = World(seed=1)
        w.advance(5)

        def boom(*a):
            raise RuntimeError("watcher")

        w.listener = boom
        self.assertTrue(call(w, "harvest"))
        self.assertEqual(w.items["Hay"], 1)
        self.assertEqual(len(w.events), 1)

    def test_a_milestone_the_engine_could_not_keep_is_tried_again(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="farm-momentum-")
        self.addCleanup(tmp.cleanup)
        blocker = Path(tmp.name) / "a-file"
        blocker.write_text("x", encoding="utf-8")
        clock = Clock(stamp(D0))
        h = host()
        h.rewards.engine = Momentum(blocker / "momentum.json", clock=clock, rng=Stub())
        w = h._world_for("python")
        call(w, "harvest")
        self.assertNotIn("momentum", h.state())
        good = Momentum(Path(tmp.name) / "momentum.json", clock=clock, rng=Stub())
        h.rewards.engine = good
        w.advance(1)
        call(w, "harvest")
        self.assertIn("momentum", h.state())
        self.assertEqual(good.summary()["xp_total"], 10)


class FarmItemsAndQuest(unittest.TestCase):
    def test_a_run_adds_exactly_what_it_harvested_to_the_days_counter(self) -> None:
        rig = Rig(self)
        before = dict(rig.world().items)
        self.assertTrue(rig.host.start("python", "harvest()\nharvest()\nharvest()\n")["ok"])
        self.assertEqual(finish(rig.host), "done")
        gained = rig.world().items["Hay"] - before["Hay"]
        self.assertEqual(gained, 3)
        self.assertEqual(rig.saved()["days"][D0.isoformat()]["counters"], {"farm_items": gained})

    def test_the_quest_completes_from_recorded_items_and_the_screen_hears_of_it(self) -> None:
        d = next(n for n in range(4000) if "farm_items" in rules.pick_quests(day(n)))
        rig = Rig(self, when=day(d))
        w = stock(rig.world(), 3, level=1)
        w.unlocks["Grass"] = 7  # 2**6 = 64 hay a harvest
        w.advance(2)
        call(w, "harvest")
        rig.host.rewards.flush()
        got = rig.host.state()["momentum"]
        quest_answers = [g for g in got if any(q["just_done"] and q["id"] == "farm_items" for q in g["quests"])]
        self.assertEqual(len(quest_answers), 1)
        self.assertEqual(quest_answers[0]["gained"], 0)
        have = next(q for q in rig.engine.summary()["quests"] if q["id"] == "farm_items")
        self.assertEqual((have["have"], have["done"]), (50, True))

    def test_the_quests_stay_fixed_once_the_day_started_by_a_harvest(self) -> None:
        rig = Rig(self)
        w = rig.world()
        w.advance(2)
        call(w, "harvest")
        rig.host.rewards.flush()
        self.assertEqual(rig.saved()["days"][D0.isoformat()]["quests"], rules.pick_quests(D0))


def ripe_from_snapshot(snap: dict) -> int:
    """Ripe tiles by the snapshot's own cells: a plant (not plain grass) fully grown."""
    return sum(1 for c in snap["tiles"] if c.get("e") in data.PLANTS and c["e"] != "Grass" and c.get("p") == 1)


class WelcomeBackOnTheFarm(unittest.TestCase):
    def set_last_seen(self, rig: Rig, seconds_ago: float) -> None:
        state = rig.saved()
        state["farm"]["last_seen"] = rig.clock.t - seconds_ago
        rig.path.write_text(json.dumps(state), encoding="utf-8")

    def setup_field(self, rig: Rig, ripe_carrots: int) -> World:
        w = stock(rig.world(), 6)
        for i in range(ripe_carrots):
            put(w, i % 6, i // 6, "Carrot")
        put(w, 5, 5, "Carrot", ripe=False)
        put(w, 4, 5, "Pumpkin")
        w.at(4, 5).entity = "Dead_Pumpkin"
        put(w, 3, 5, "Cactus")
        return w

    def test_no_card_on_the_first_visit_ever(self) -> None:
        rig = Rig(self)
        self.assertIsNone(rig.host.welcome())
        self.assertIsNone(rig.host.welcome(), "and none on the second look either")

    def test_a_card_after_thirty_minutes_counts_the_ripe_tiles_the_snapshot_shows(self) -> None:
        rig = Rig(self)
        w = self.setup_field(rig, 25)
        rig.host.welcome()
        oracle = ripe_from_snapshot(w.snapshot())
        self.assertEqual(oracle, 25 + 1)  # the carrots and the cactus; not the grass, the dead pumpkin or the unripe carrot
        self.set_last_seen(rig, 31 * 60)
        card = rig.host.welcome()
        self.assertEqual(card["ripe"], oracle)
        self.assertEqual(card["xp"], 15 + min(10, oracle // 10))
        self.assertEqual((card["minutes"], card["language"]), (31, rig.host.language))

    def test_just_under_thirty_minutes_is_no_card(self) -> None:
        rig = Rig(self)
        rig.host.welcome()
        self.set_last_seen(rig, 29 * 60)
        self.assertIsNone(rig.host.welcome())

    def test_claiming_pays_once_a_day_and_never_without_an_absence(self) -> None:
        rig = Rig(self)
        self.setup_field(rig, 12)
        self.assertFalse(rig.host.claim_welcome()["ok"], "nothing was offered yet")
        rig.host.welcome()
        self.assertEqual(rig.host.claim_welcome()["reason"], "no_absence")
        self.assertEqual(rig.xp(), 0)
        self.set_last_seen(rig, 2 * 3600)
        card = rig.host.welcome()
        got = rig.host.claim_welcome()
        self.assertTrue(got["ok"])
        self.assertEqual(got["gained"], card["xp"])
        self.assertEqual(rig.xp(), card["xp"])
        self.assertEqual(rig.host.claim_welcome()["reason"], "already_claimed")
        self.assertEqual(rig.xp(), card["xp"])
        self.set_last_seen(rig, 2 * 3600)
        self.assertIsNone(rig.host.welcome(), "claimed today: no second card")

    def test_a_quiet_farm_says_zero_and_still_pays_the_base(self) -> None:
        rig = Rig(self)
        rig.host.welcome()
        self.set_last_seen(rig, 3 * 3600)
        card = rig.host.welcome()
        self.assertEqual((card["ripe"], card["xp"]), (0, 15))
        self.assertEqual(rig.host.claim_welcome()["gained"], 15)

    def test_a_farm_that_was_polled_all_along_is_not_away(self) -> None:
        rig = Rig(self)
        rig.host.welcome()
        self.set_last_seen(rig, 5 * 3600)
        rig.host.rewards._touched = 0.0  # the polling's heartbeat is due
        rig.host.state()
        self.assertIsNone(rig.host.welcome())

    def test_an_idle_farm_does_not_grow_while_away(self) -> None:
        # What the card says is honest: nothing ripens in the app's absence. A farm with
        # nothing running moves on only while it is looked at, by a couple of seconds a look.
        h = FarmHost()
        h._load()
        w = h._world_for("python")
        put(w, 0, 0, "Carrot", ripe=False)
        w.at(0, 0).need = 600.0
        h._last_look -= 3 * 3600  # three hours since anyone looked
        before = w.time
        h.state()
        self.assertLessEqual(w.time - before, 2.0 + 1e-6)
        self.assertEqual(w.ripe_tiles(), 0)

    def test_the_routes_carry_the_card_and_take_the_claim(self) -> None:
        rig = Rig(self)
        from code_coach.farm.runner import HOST

        saved = HOST.rewards.engine
        HOST.rewards.engine = rig.engine
        self.addCleanup(lambda: setattr(HOST.rewards, "engine", saved))
        first = server.farm_overview()
        self.assertIn("welcome_back", first)
        self.assertIsNone(first["welcome_back"])
        state = rig.saved()
        state["farm"]["last_seen"] = rig.clock.t - 3 * 3600
        rig.path.write_text(json.dumps(state), encoding="utf-8")
        card = server.farm_overview()["welcome_back"]
        self.assertIsNotNone(card)
        self.assertEqual(set(card), {"minutes", "ripe", "xp", "language"})
        got = server.farm_welcome_claim()
        self.assertTrue(got["ok"])
        self.assertEqual(got["gained"], card["xp"])
        self.assertEqual(got["label"], "Welcome back")
        self.assertFalse(server.farm_welcome_claim()["ok"])
        self.assertIn(("/api/farm/welcome/claim", ("POST",)),
                      {(r.path, tuple(sorted(r.methods))) for r in server.app.routes if hasattr(r, "methods")})


class QueueBehaviour(unittest.TestCase):
    def test_the_queue_keeps_the_newest_and_drains_oldest_first(self) -> None:
        r = milestones.FarmRewards(engine=object())
        for n in range(r.QUEUE_CAP + 15):
            r._enqueue({"n": n})
        got = r.drain()
        self.assertEqual(len(got), r.QUEUE_CAP)
        self.assertEqual([g["n"] for g in got], list(range(15, r.QUEUE_CAP + 15)))
        self.assertEqual(r.drain(), [])

    def test_the_wire_form_is_a_list_oldest_first_under_momentum(self) -> None:
        rig = Rig(self)
        w = stock(rig.world(), 6)
        for n, entity in enumerate(("Carrot", "Pumpkin")):
            put(w, n, 0, entity)
            w.x = n
            call(w, "harvest")
        wire = json.loads(json.dumps(jsonable_encoder(rig.host.state())))
        self.assertEqual([g["label"] for g in wire["momentum"]],
                         ["Farm: first carrot! (Python)", "Farm: first pumpkin! (Python)"])
        self.assertTrue(all(g["ok"] and not g["repeat"] for g in wire["momentum"]))


if __name__ == "__main__":
    unittest.main()
