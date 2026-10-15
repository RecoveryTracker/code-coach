"""Farm: the event stream - what the drones just did, for the screen to animate.

Every action that changes a square (harvest, plant, till, water, fertilize, swap,
change_hat, unlock) writes one event on the World; the snapshot carries the latest
60, oldest first, each with an `n` that only ever rises. Moves are not events.
These tests hold the stream to the inventory (what a harvest says it paid is what
the barn actually gained), to the program (which tile, which drone) and to the wire
(the field reaches the browser).
"""

from __future__ import annotations

import json
import shutil
import time
import unittest

from fastapi.encoders import jsonable_encoder

from code_coach.api.server import farm_state
from code_coach.farm import data, scratch
from code_coach.farm.runner import HOST, LANGUAGES, FarmHost
from code_coach.farm.world import World
from tests.test_farm_world import call, everything, farm, grow

HAS_NODE = shutil.which("node") is not None


def gained(before: dict, after: dict) -> dict:
    """Items that went up between two looks at the barn."""
    out = {}
    for item, amount in after.items():
        if amount > before.get(item, 0):
            gain = amount - before.get(item, 0)
            out[item] = int(gain) if float(gain).is_integer() else gain
    return out


class HarvestEventTests(unittest.TestCase):
    def test_a_ripe_harvest_reports_exactly_what_the_barn_gained(self) -> None:
        w = World(seed=1)
        grow(w, 5)
        before = dict(w.items)
        call(w, "harvest")
        event = w.events[-1]
        self.assertEqual(event["k"], "harvest")
        self.assertTrue(event["ok"])
        self.assertEqual((event["x"], event["y"], event["d"]), (0, 0, 0))
        self.assertEqual(event["e"], "Grass")
        self.assertEqual(event["items"], gained(before, w.items))
        self.assertEqual(event["items"], {"Hay": 1})

    def test_an_unripe_harvest_is_not_ok_and_pays_nothing(self) -> None:
        w = World(seed=1)
        before = dict(w.items)
        call(w, "harvest")  # the grass has not grown yet
        event = w.events[-1]
        self.assertEqual(event["k"], "harvest")
        self.assertFalse(event["ok"])
        self.assertNotIn("items", event)
        self.assertEqual(gained(before, w.items), {})

    def test_harvesting_bare_soil_is_not_ok(self) -> None:
        w = farm(3, Carrots=1, Plant=1, Expand=2)
        call(w, "till")
        call(w, "harvest")
        event = w.events[-1]
        self.assertEqual(event["k"], "harvest")
        self.assertFalse(event["ok"])
        self.assertNotIn("e", event)
        self.assertNotIn("items", event)

    def test_a_giant_pumpkin_reports_its_whole_payout(self) -> None:
        w = everything(6)
        for x in range(2):
            for y in range(2):
                t = w.at(x, y)
                t.ground, t.entity, t.need, t.grown = "Soil", "Pumpkin", 1.0, 1.0
        w._changed()
        before = dict(w.items)
        call(w, "harvest")
        event = w.events[-1]
        self.assertTrue(event["ok"])
        self.assertEqual(event["e"], "Pumpkin")
        self.assertEqual(event["items"], gained(before, w.items))
        self.assertEqual(event["items"], {"Pumpkin": 8})  # a 2x2 giant, as the game states it

    def test_an_infected_harvest_reports_the_weird_substance_too(self) -> None:
        w = everything(3)
        w.at(0, 0).infected = True
        grow(w, 5)
        before = dict(w.items)
        call(w, "harvest")
        event = w.events[-1]
        self.assertEqual(event["items"], gained(before, w.items))
        self.assertIn("Weird_Substance", event["items"])

    def test_a_maze_treasure_reports_the_gold(self) -> None:
        w = everything(6, 11)
        call(w, "plant", "Entities.Bush")
        self.assertTrue(call(w, "use_item", "Items.Weird_Substance", 6))
        w.x, w.y = w.maze.treasure
        before = dict(w.items)
        call(w, "harvest")
        event = w.events[-1]
        self.assertEqual((event["x"], event["y"]), (w.x, w.y))
        self.assertEqual(event["items"], gained(before, w.items))
        self.assertEqual(event["items"], {"Gold": 36})


class OtherActionEventTests(unittest.TestCase):
    def test_plant_till_and_water_carry_their_tile_and_plant(self) -> None:
        w = everything(4)
        w.x, w.y = 2, 1
        call(w, "till")
        self.assertEqual(w.events[-1]["k"], "till")
        self.assertTrue(w.events[-1]["ok"])
        self.assertEqual((w.events[-1]["x"], w.events[-1]["y"]), (2, 1))
        call(w, "plant", "Entities.Carrot")
        plant = w.events[-1]
        self.assertEqual((plant["k"], plant["e"], plant["ok"]), ("plant", "Carrot", True))
        self.assertEqual((plant["x"], plant["y"]), (2, 1))
        self.assertEqual(w.at(2, 1).entity, "Carrot")
        call(w, "use_item", "Items.Water")
        water = w.events[-1]
        self.assertEqual((water["k"], water["ok"], water["e"]), ("water", True, "Carrot"))
        self.assertEqual((water["x"], water["y"]), (2, 1))
        self.assertGreater(w.at(2, 1).water, 0)

    def test_fertilize_swap_hat_and_unlock_are_events_too(self) -> None:
        w = everything(4)
        call(w, "plant", "Entities.Bush")
        call(w, "use_item", "Items.Fertilizer")
        self.assertEqual((w.events[-1]["k"], w.events[-1]["ok"]), ("fertilize", True))
        call(w, "swap", "East")
        self.assertEqual((w.events[-1]["k"], w.events[-1]["ok"]), ("swap", True))
        call(w, "change_hat", "Hats.Wizard_Hat")
        hat = w.events[-1]
        self.assertEqual((hat["k"], hat["e"], hat["ok"]), ("hat", "Wizard_Hat", True))
        call(w, "unlock", "Unlocks.Speed")
        unlock = w.events[-1]
        self.assertEqual((unlock["k"], unlock["e"], unlock["ok"]), ("unlock", "Speed", True))

    def test_failed_attempts_are_ok_false(self) -> None:
        w = World(seed=1)
        w.unlocks["Auto_Unlock"] = 1
        call(w, "unlock", "Unlocks.Loops")  # no hay to pay for it
        self.assertEqual((w.events[-1]["k"], w.events[-1]["ok"]), ("unlock", False))
        w = everything(3)
        w.items["Carrot"] = 0
        w.items["Hay"] = w.items["Wood"] = 0
        call(w, "plant", "Entities.Carrot")  # grass, not soil, and nothing to pay with
        event = w.events[-1]
        self.assertEqual((event["k"], event["e"], event["ok"]), ("plant", "Carrot", False))
        self.assertEqual(w.at(0, 0).entity, "Grass")
        w.items["Water"] = 0
        call(w, "use_item", "Items.Water")
        self.assertEqual((w.events[-1]["k"], w.events[-1]["ok"]), ("water", False))

    def test_moves_and_questions_are_not_events(self) -> None:
        w = everything(4)
        for command, args in (("move", ["East"]), ("move", ["North"]), ("get_pos_x", []),
                              ("can_harvest", []), ("measure", []), ("num_items", ["Items.Hay"])):
            w.call(command, args)
        self.assertEqual(len(w.events), 0)
        self.assertEqual(w.snapshot()["events"], [])


class StreamTests(unittest.TestCase):
    def test_n_rises_and_is_unique_and_snapshots_do_not_reset_it(self) -> None:
        w = everything(3)
        seen = []
        for _ in range(4):
            call(w, "till")
            w.snapshot()
            seen += [e["n"] for e in w.snapshot()["events"]]
            call(w, "harvest")
        numbers = [e["n"] for e in w.snapshot()["events"]]
        self.assertEqual(len(numbers), 8)
        self.assertEqual(numbers, sorted(set(numbers)))
        self.assertTrue(all(b > a for a, b in zip(numbers, numbers[1:])))
        self.assertTrue(set(seen) <= set(numbers))
        # The farm starts over (a reset is a new World): numbers still never go back.
        fresh = everything(3)
        call(fresh, "till")
        self.assertGreater(fresh.events[0]["n"], max(numbers))

    def test_the_buffer_is_capped_and_keeps_the_newest_oldest_first(self) -> None:
        w = everything(3)
        made = []
        for _ in range(125):
            call(w, "till")
            made.append(w.events[-1]["n"])
        events = w.snapshot()["events"]
        self.assertEqual(len(events), 60)  # the contract with the screen: about 60
        self.assertEqual([e["n"] for e in events], made[-60:])

    def test_event_times_are_farm_time(self) -> None:
        w = everything(3)
        call(w, "till")
        first = w.events[-1]["t"]
        call(w, "till")
        second = w.events[-1]["t"]
        self.assertGreater(first, 0)
        self.assertGreater(second, first)
        self.assertAlmostEqual(second, round(w.time, 3))


class WireTests(unittest.TestCase):
    def test_the_events_reach_the_browser(self) -> None:
        HOST._load()
        world = HOST._world_for(HOST.language)
        grow(world, 5)
        before = dict(world.items)
        call(world, "harvest")
        got = farm_state()
        wire = json.loads(json.dumps(jsonable_encoder(got)))
        events = wire["farm"]["events"]
        self.assertTrue(events)
        last = events[-1]
        self.assertEqual(
            sorted(last), sorted(["n", "t", "k", "x", "y", "d", "e", "items", "ok"]))
        self.assertEqual(last["k"], "harvest")
        self.assertEqual(last["items"], gained(before, world.items))
        # A second look at the state shows the same events, not fewer.
        again = farm_state()["farm"]["events"]
        self.assertEqual([e["n"] for e in again], [e["n"] for e in events])


def finish(h: FarmHost, timeout: float = 90.0) -> str:
    deadline = time.monotonic() + timeout
    while h.run and h.run.status in ("starting", "running"):
        if time.monotonic() > deadline:
            h.stop_run(wait=True)
            raise AssertionError("the program did not finish")
        time.sleep(0.02)
    return h.run.status


def host(**levels: int) -> FarmHost:
    h = FarmHost()
    h._load()
    for lang in LANGUAGES:
        h.warps[lang] = 0
        world = h._world_for(lang)
        for name, level in levels.items():
            world.unlocks[name] = level
        if levels.get("Expand"):
            world.width, world.height = data.FARM_SIZES[levels["Expand"]]
            world._fill()
        world.advance(5)  # every square's grass ripe
    return h


MEGA = dict(Loops=1, Speed=1, Expand=2, Plant=1, Senses=1, Operators=1, Variables=1,
            Functions=1, Lists=1, Debug=1, Timing=1, Megafarm=1)

PY_COLUMNS = """\
def column():
    for i in range(get_world_size()):
        harvest()
        move(North)

other = spawn_drone(column)
move(East)
column()
wait_for(other)
"""


class ProgramRunTests(unittest.TestCase):
    def test_a_python_run_emits_a_harvest_event(self) -> None:
        h = host()
        before = dict(h._load().items)
        self.assertTrue(h.start("python", "harvest()\n")["ok"])
        self.assertEqual(finish(h), "done")
        world = h._load()
        harvests = [e for e in world.events if e["k"] == "harvest"]
        self.assertEqual(len(harvests), 1)
        self.assertTrue(harvests[0]["ok"])
        self.assertEqual(harvests[0]["d"], 0)
        self.assertEqual(harvests[0]["items"], {"Hay": 1})
        self.assertEqual(gained(before, world.items), {"Hay": 1})

    @unittest.skipUnless(HAS_NODE, "needs node")
    def test_a_javascript_run_emits_a_harvest_event(self) -> None:
        h = host()
        before = dict(h._load().items)
        self.assertTrue(h.start("javascript", "harvest();\n")["ok"])
        self.assertEqual(finish(h), "done")
        world = h._load()
        harvests = [e for e in world.events if e["k"] == "harvest"]
        self.assertEqual(len(harvests), 1)
        self.assertEqual(harvests[0]["items"], gained(before, world.items))

    def test_the_games_own_language_on_the_scratch_farm_emits_events(self) -> None:
        world = scratch.make_world()
        world.advance(5)
        before = dict(world.items)
        sh = scratch._ScratchHost(world)
        self.assertTrue(sh.start("original", "harvest()\ntill()\n", "main")["ok"])
        self.assertEqual(finish(sh), "done")
        kinds = [e["k"] for e in world.events]
        self.assertEqual(kinds, ["harvest", "till"])
        self.assertEqual(world.events[0]["items"], gained(before, world.items))

    def test_a_spawned_drone_s_actions_carry_its_own_index(self) -> None:
        h = host(**MEGA)
        self.assertTrue(h.start("python", PY_COLUMNS)["ok"])
        self.assertEqual(finish(h), "done", h.run.error)
        world = h._load()
        harvests = [e for e in world.events if e["k"] == "harvest"]
        self.assertEqual(len(harvests), 6)  # two columns of the 3x3 field
        mine = [e for e in harvests if e["d"] == 0]
        spawned = [e for e in harvests if e["d"] == 1]
        self.assertEqual(len(mine), 3)
        self.assertEqual(len(spawned), 3)
        # The program sends the spawned drone down the column it stands in (x 0) and its
        # own drone down the next (x 1): the tiles say which drone made which event.
        self.assertEqual({e["x"] for e in spawned}, {0})
        self.assertEqual({e["x"] for e in mine}, {1})
        self.assertEqual(sorted(e["y"] for e in spawned), [0, 1, 2])
        self.assertTrue(all(e["ok"] and e["items"] == {"Hay": 1} for e in harvests))
        self.assertEqual(len({e["n"] for e in harvests}), 6)
        self.assertEqual(h._world_for("python").drone_id, 0)


if __name__ == "__main__":
    unittest.main()
