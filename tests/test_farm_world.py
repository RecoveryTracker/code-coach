"""Farm: the rules of the field, held to the game's numbers.

Each test sets up just enough of a World - research bought, items in hand,
a few squares planted - and checks one rule as the game states it: a
harvest takes half a second at the start; trees crowd each other; a 2x2
giant pumpkin gives 8, not 4; a sorted 3x3 of cacti gives 81; a maze can
always be walked to its treasure.
"""

from __future__ import annotations

import unittest

from code_coach.farm import data
from code_coach.farm.world import Refusal, World


def farm(size: int = 3, seed: int = 7, **levels: int) -> World:
    """A world with research bought and the field at a given size."""
    w = World(seed=seed)
    for name in data.UNLOCKS:
        w.unlocks[name] = max(w.unlocks[name], levels.get(name, 0))
    w.width = w.height = size
    w._fill()
    return w


def everything(size: int = 6, seed: int = 7) -> World:
    w = farm(size, seed, **{name: 1 for name in data.UNLOCKS})
    w.unlocks["Grass"] = 1
    for item in data.ITEMS:
        w.items[item] = 10 ** 6
    w.items["Power"] = 0
    return w


def call(w: World, name: str, *args):
    result, _seconds = w.call(name, list(args))
    return result


def grow(w: World, seconds: float = 30.0) -> None:
    w.advance(seconds)


class StartTests(unittest.TestCase):
    def test_a_new_farm_is_one_square_of_grass(self) -> None:
        w = World(seed=1)
        self.assertEqual((w.w, w.h), (1, 1))
        self.assertEqual(w.here().entity, "Grass")
        self.assertTrue(w.has_function("harvest"))
        self.assertTrue(w.has_function("do_a_flip"))
        self.assertFalse(w.has_function("move"))

    def test_a_harvest_takes_half_a_second_and_grass_gives_hay(self) -> None:
        w = World(seed=1)
        grow(w, 1)
        ok, seconds = w.call("harvest", [])
        self.assertTrue(ok)
        self.assertAlmostEqual(seconds, 0.5)
        self.assertEqual(w.items["Hay"], 1)

    def test_harvesting_too_early_destroys_and_gives_nothing(self) -> None:
        w = World(seed=1)
        self.assertTrue(call(w, "harvest"))  # the grass has not grown yet
        self.assertEqual(w.items["Hay"], 0)
        # The harvest's own half second is growing time: the grass that came
        # back is ripe by the time the drone can act again.
        self.assertTrue(call(w, "harvest"))
        self.assertEqual(w.items["Hay"], 1)

    def test_harvesting_nothing_costs_one_tick(self) -> None:
        w = farm(3, Carrots=1, Plant=1, Expand=2)
        call(w, "till")  # soil: no grass grows
        ok, seconds = w.call("harvest", [])
        self.assertFalse(ok)
        self.assertAlmostEqual(seconds, 1 / data.BASE_TICKS_PER_SECOND)

    def test_locked_commands_are_refused_with_the_unlock_named(self) -> None:
        w = World(seed=1)
        with self.assertRaises(Refusal) as caught:
            w.call("move", ["North"])
        self.assertIn("Expand", str(caught.exception))
        with self.assertRaises(Refusal) as caught:
            w.call("can_harvest", [], "javascript")
        self.assertIn("canHarvest()", str(caught.exception))

    def test_flips_take_a_second_whatever_the_speed(self) -> None:
        w = farm(3, Speed=5)
        _, seconds = w.call("do_a_flip", [])
        self.assertEqual(seconds, 1.0)


class ResearchTests(unittest.TestCase):
    def test_loops_cost_five_hay(self) -> None:
        w = World(seed=1)
        self.assertEqual(w.next_cost("Loops"), {"Hay": 5})
        self.assertFalse(w.buy("Loops"))
        w.items["Hay"] = 5
        self.assertTrue(w.buy("Loops"))
        self.assertEqual(w.items["Hay"], 0)
        self.assertIn("while", w.unlocked_features())

    def test_unlocks_wait_for_what_they_need(self) -> None:
        w = World(seed=1)
        w.items["Hay"] = 1000
        self.assertFalse(w.available("Plant"))
        self.assertTrue(w.buy("Loops"))
        self.assertTrue(w.buy("Expand"))
        self.assertTrue(w.available("Plant"))

    def test_expand_grows_the_farm_and_brings_move_then_for(self) -> None:
        w = World(seed=1)
        w.unlocks["Loops"] = 1
        w.items.update(Hay=100, Wood=100)
        w.buy("Expand")
        self.assertEqual((w.w, w.h), (1, 3))
        self.assertTrue(w.has_function("move"))
        self.assertNotIn("for", w.unlocked_features())
        w.buy("Expand")
        self.assertEqual((w.w, w.h), (3, 3))
        self.assertIn("for", w.unlocked_features())
        self.assertTrue(w.has_function("get_world_size"))

    def test_speed_makes_actions_quicker_by_half_again(self) -> None:
        w = farm(3, Speed=2)
        _, seconds = w.call("harvest", [])
        self.assertAlmostEqual(seconds, 0.5 / 2.25)

    def test_grass_starts_at_level_one_and_upgrades_double_hay(self) -> None:
        w = World(seed=1)
        self.assertEqual(w.level("Grass"), 1)
        self.assertEqual(w.next_cost("Grass"), {"Hay": 100})
        w.unlocks["Grass"] = 3
        grow(w, 1)
        call(w, "harvest")
        self.assertEqual(w.items["Hay"], 4)

    def test_a_maxed_unlock_has_no_cost(self) -> None:
        w = World(seed=1)
        w.unlocks["Loops"] = 1
        self.assertIsNone(w.next_cost("Loops"))
        self.assertFalse(w.available("Loops"))


class MovingTests(unittest.TestCase):
    def test_north_is_up_and_the_edges_wrap(self) -> None:
        w = farm(3, Expand=2)
        call(w, "move", "North")
        self.assertEqual((w.x, w.y), (0, 1))
        call(w, "move", "West")
        self.assertEqual((w.x, w.y), (2, 1))
        call(w, "move", "South")
        call(w, "move", "South")
        self.assertEqual((w.x, w.y), (2, 2))

    def test_a_wrong_direction_is_named_in_the_players_language(self) -> None:
        w = farm(3, Expand=2)
        with self.assertRaises(Refusal) as caught:
            w.call("move", ["Up"], "dart")
        self.assertIn("north, east, south, west", str(caught.exception))


class PlantTests(unittest.TestCase):
    def test_bushes_grow_wood(self) -> None:
        w = farm(3, Plant=1, Expand=2, Senses=1)
        self.assertTrue(call(w, "plant", "Entities.Bush"))
        self.assertEqual(call(w, "get_entity_type"), "Entities.Bush")
        grow(w, 10)
        call(w, "harvest")
        self.assertGreaterEqual(w.items["Wood"], 1)

    def test_carrots_need_soil_and_cost_hay_and_wood(self) -> None:
        w = farm(3, Plant=1, Carrots=1, Expand=2)
        w.items.update(Hay=5, Wood=5)
        self.assertFalse(call(w, "plant", "Entities.Carrot"))  # grassland
        call(w, "till")
        self.assertTrue(call(w, "plant", "Entities.Carrot"))
        self.assertEqual((w.items["Hay"], w.items["Wood"]), (4, 4))
        grow(w, 10)
        call(w, "harvest")
        self.assertEqual(w.items["Carrot"], 1)

    def test_carrots_cost_double_per_upgrade(self) -> None:
        w = farm(3, Plant=1, Carrots=4)
        self.assertEqual(w.plant_cost("Carrot"), {"Hay": 8, "Wood": 8})

    def test_planting_a_locked_plant_is_refused(self) -> None:
        w = farm(3, Plant=1)
        with self.assertRaises(Refusal):
            w.call("plant", ["Entities.Pumpkin"])

    def test_cannot_plant_on_a_growing_plant(self) -> None:
        w = farm(3, Plant=1, Trees=1)
        self.assertTrue(call(w, "plant", "Entities.Bush"))
        self.assertFalse(call(w, "plant", "Entities.Tree"))

    def test_trees_give_five_and_grow_slower_when_crowded(self) -> None:
        w = farm(3, Plant=1, Trees=1, Expand=2)
        call(w, "plant", "Entities.Tree")
        lonely = w.here()
        call(w, "move", "East")
        call(w, "move", "East")  # (2, 0): no tree beside it... but (0,0) wraps? neighbours don't wrap
        call(w, "plant", "Entities.Tree")
        call(w, "move", "North")
        call(w, "plant", "Entities.Tree")  # (2, 1) next to (2, 0)
        crowded = w.at(2, 0)
        lonely.need = crowded.need = 6.0
        lonely.grown = crowded.grown = 0.0
        grow(w, 3)
        self.assertAlmostEqual(lonely.grown, 3.0)
        self.assertAlmostEqual(crowded.grown, 1.5)
        lonely.grown = lonely.need
        w.x, w.y = 0, 0
        call(w, "harvest")
        self.assertEqual(w.items["Wood"], 5)


class WaterAndFertilizerTests(unittest.TestCase):
    def test_water_arrives_every_ten_seconds_and_doubles_per_upgrade(self) -> None:
        w = farm(3, Watering=1)
        grow(w, 25)
        self.assertEqual(w.items["Water"], 2)
        w.unlocks["Watering"] = 3
        grow(w, 10)
        self.assertEqual(w.items["Water"], 6)

    def test_a_tank_adds_a_quarter_and_wet_ground_grows_faster(self) -> None:
        w = farm(3, Plant=1, Watering=1)
        w.items["Water"] = 4
        call(w, "plant", "Entities.Bush")
        t = w.here()
        call(w, "use_item", "Items.Water", 4)
        self.assertAlmostEqual(call(w, "get_water"), 1.0, places=2)
        t.need, t.grown = 100.0, 0.0
        grow(w, 1)
        self.assertGreater(t.grown, 4.9)

    def test_ground_dries_by_about_one_percent_a_second(self) -> None:
        w = farm(3, Watering=1)
        w.items["Water"] = 1
        call(w, "use_item", "Items.Water")
        before = w.here().water
        grow(w, 10)
        self.assertAlmostEqual(w.here().water / before, 0.99 ** 10, places=2)

    def test_fertilizer_takes_two_seconds_off_and_infects(self) -> None:
        w = farm(3, Plant=1, Fertilizer=1)
        w.items["Fertilizer"] = 1
        call(w, "plant", "Entities.Bush")
        t = w.here()
        t.need, t.grown = 10.0, 0.0
        self.assertTrue(call(w, "use_item", "Items.Fertilizer"))
        self.assertGreaterEqual(t.grown, 2.0)
        self.assertTrue(t.infected)

    def test_an_infected_harvest_turns_half_into_weird_substance(self) -> None:
        w = farm(3, Plant=1, Trees=1)
        call(w, "plant", "Entities.Tree")
        t = w.here()
        t.grown = t.need
        t.infected = True
        call(w, "harvest")
        self.assertEqual(w.items["Weird_Substance"], 2)
        self.assertEqual(w.items["Wood"], 3)


class PumpkinTests(unittest.TestCase):
    def _field(self, n: int) -> World:
        w = everything(6)
        for x in range(n):
            for y in range(n):
                t = w.at(x, y)
                t.ground, t.entity, t.need, t.grown = "Soil", "Pumpkin", 1.0, 1.0
        w._changed()
        return w

    def test_a_two_by_two_giant_gives_eight(self) -> None:
        w = self._field(2)
        self.assertEqual(w.pumpkin_groups()[(1, 1)], (0, 0, 2))
        call(w, "harvest")
        self.assertEqual(w.items["Pumpkin"] - 10 ** 6, 8)
        self.assertIsNone(w.at(1, 1).entity)

    def test_six_and_up_give_n_squared_times_six(self) -> None:
        w = self._field(6)
        call(w, "harvest")
        self.assertEqual(w.items["Pumpkin"] - 10 ** 6, 6 * 6 * 6)

    def test_a_dead_pumpkin_breaks_the_square_and_cannot_be_harvested(self) -> None:
        w = self._field(2)
        w.at(1, 1).entity = "Dead_Pumpkin"
        w._changed()
        self.assertNotIn((1, 1), w.pumpkin_groups())
        w.x = w.y = 1
        self.assertFalse(call(w, "can_harvest"))

    def test_about_one_in_five_dies_as_it_ripens(self) -> None:
        w = everything(10, seed=3)
        for t in w.tiles:
            t.ground, t.entity, t.need, t.grown = "Soil", "Pumpkin", 1.0, 0.0
        grow(w, 5)
        dead = sum(1 for t in w.tiles if t.entity == "Dead_Pumpkin")
        self.assertTrue(8 <= dead <= 35, dead)

    def test_measure_gives_one_id_per_giant(self) -> None:
        w = self._field(2)
        ids = set()
        for x, y in ((0, 0), (1, 0), (0, 1), (1, 1)):
            w.x, w.y = x, y
            ids.add(call(w, "measure"))
        self.assertEqual(len(ids), 1)


class CactusTests(unittest.TestCase):
    def _field(self, sizes: list[list[int]]) -> World:
        """sizes[row] from the South row up."""
        w = everything(6)
        for y, row in enumerate(sizes):
            for x, s in enumerate(row):
                t = w.at(x, y)
                t.ground, t.entity, t.need, t.grown, t.size = "Soil", "Cactus", 1.0, 1.0, s
        return w

    def test_a_sorted_square_is_harvested_whole_for_n_squared(self) -> None:
        w = self._field([[1, 2, 3], [2, 3, 4], [3, 4, 5]])
        call(w, "harvest")
        self.assertEqual(w.items["Cactus"] - 10 ** 6, 81)

    def test_an_unsorted_cactus_comes_alone(self) -> None:
        # The game's own example (top row first): 1 5 3 / 4 9 7 / 3 3 2.
        w = self._field([[3, 3, 2], [4, 9, 7], [1, 5, 3]])
        call(w, "harvest")
        self.assertEqual(w.items["Cactus"] - 10 ** 6, 1)

    def test_swap_moves_a_cactus(self) -> None:
        w = self._field([[5, 1]])
        call(w, "swap", "East")
        self.assertEqual((w.at(0, 0).size, w.at(1, 0).size), (1, 5))
        self.assertEqual(call(w, "measure", "East"), 5)


class SunflowerTests(unittest.TestCase):
    def test_the_biggest_of_ten_gives_eight_times_the_power(self) -> None:
        w = everything(6)
        for i in range(10):
            t = w.tiles[i]
            t.ground, t.entity, t.need, t.grown, t.petals = "Soil", "Sunflower", 1.0, 1.0, 7
        w.tiles[0].petals = 15
        call(w, "harvest")
        # The harvest's own 200 ticks already run on the new power.
        self.assertEqual(round(w.items["Power"]), 8)

    def test_harvesting_a_smaller_one_spoils_the_next_bonus(self) -> None:
        w = everything(6)
        for i in range(12):
            t = w.tiles[i]
            t.ground, t.entity, t.need, t.grown, t.petals = "Soil", "Sunflower", 1.0, 1.0, 7
        w.tiles[5].petals = 15
        w.x, w.y = 0, 0
        call(w, "harvest")  # a 7 while a 15 stands
        w.x, w.y = 5, 0
        call(w, "harvest")  # the 15: no bonus this time
        self.assertEqual(round(w.items["Power"]), 2)

    def test_power_doubles_speed_and_runs_down(self) -> None:
        w = farm(3, Plant=1)
        w.items["Power"] = 1
        _, seconds = w.call("harvest", [])
        self.assertAlmostEqual(seconds, 0.25)
        self.assertAlmostEqual(w.items["Power"], 1 - 200 / 6000)


class MazeTests(unittest.TestCase):
    def _maze(self, size: int = 6, seed: int = 11) -> World:
        w = everything(size, seed)
        call(w, "plant", "Entities.Bush")
        self.assertTrue(call(w, "use_item", "Items.Weird_Substance", size))
        return w

    def test_a_full_field_maze_always_reaches_its_treasure(self) -> None:
        for seed in range(5):
            w = self._maze(6, seed)
            target = w.maze.treasure
            seen = {(w.x, w.y)}
            frontier = [(w.x, w.y)]
            while frontier:
                cx, cy = frontier.pop()
                for nx, ny in w.neighbours(cx, cy).values():
                    if (nx, ny) not in seen and w.maze.passable((cx, cy), (nx, ny)):
                        seen.add((nx, ny))
                        frontier.append((nx, ny))
            self.assertIn(target, seen)
            self.assertEqual(len(seen), 36)  # every cell, and no loops: 35 passages
            self.assertEqual(len(w.maze.open), 35)

    def test_walls_stop_the_drone_and_can_move_sees_them(self) -> None:
        w = self._maze()
        for d in data.DIRECTIONS:
            self.assertEqual(call(w, "can_move", d), w._target(d) is not None)
        blocked = [d for d in data.DIRECTIONS if not call(w, "can_move", d)]
        self.assertTrue(blocked)
        ok, seconds = w.call("move", [blocked[0]])
        self.assertFalse(ok)
        self.assertAlmostEqual(seconds, 1 / (data.BASE_TICKS_PER_SECOND * w.speed_factor()))

    def test_measure_points_at_the_treasure_and_it_pays_the_area(self) -> None:
        w = self._maze()
        tx, ty = call(w, "measure")
        self.assertEqual((tx, ty), w.maze.treasure)
        w.x, w.y = tx, ty
        self.assertTrue(call(w, "can_harvest"))
        gold = w.items["Gold"]
        call(w, "harvest")
        self.assertEqual(w.items["Gold"] - gold, 36)
        self.assertIsNone(w.maze)

    def test_harvesting_anywhere_else_loses_the_maze(self) -> None:
        w = self._maze()
        tx, ty = w.maze.treasure
        w.x, w.y = (tx + 1) % 6, ty
        gold = w.items["Gold"]
        call(w, "harvest")
        self.assertIsNone(w.maze)
        self.assertEqual(w.items["Gold"], gold)

    def test_reusing_the_maze_moves_the_treasure(self) -> None:
        w = self._maze()
        w.x, w.y = w.maze.treasure
        gold = w.items["Gold"]
        self.assertTrue(call(w, "use_item", "Items.Weird_Substance", 6))
        self.assertIsNotNone(w.maze)
        self.assertEqual(w.items["Gold"] - gold, 36)
        self.assertEqual(w.maze.moved, 1)


class DinosaurTests(unittest.TestCase):
    def test_the_tail_follows_apples_grow_it_and_bones_are_its_length_squared(self) -> None:
        w = everything(6, seed=5)
        call(w, "change_hat", "Hats.Dinosaur_Hat")
        self.assertEqual(w.here().entity, "Apple")
        cost = w._apple_cost()["Cactus"]
        cactus = w.items["Cactus"]
        ok, seconds = w.call("move", ["East"])  # eats the apple it was over
        self.assertTrue(ok)
        self.assertAlmostEqual(seconds, 400 / (data.BASE_TICKS_PER_SECOND * w.speed_factor()))
        self.assertEqual(len(w.tail), 1)
        self.assertEqual(w.items["Cactus"], cactus - cost)  # the next apple bought
        self.assertEqual(w.dino_move, 388)
        call(w, "move", "East")
        self.assertEqual(len(w.tail), 1)  # no apple: the tail follows
        bones = w.items["Bone"]
        call(w, "change_hat", "Hats.Straw_Hat")
        self.assertEqual(w.items["Bone"] - bones, 1)
        self.assertEqual(w.tail, [])

    def test_the_tail_blocks_and_the_border_does_not_wrap(self) -> None:
        w = everything(3, seed=5)
        call(w, "change_hat", "Hats.Dinosaur_Hat")
        self.assertFalse(call(w, "move", "West"))  # border: no wrapping with the hat on
        call(w, "move", "East")
        self.assertEqual(len(w.tail), 1)
        # A tail of one is only its last segment, which moves out of the way.
        self.assertTrue(call(w, "can_move", "West"))
        w.tail = [(0, 0), (0, 1)]
        self.assertFalse(call(w, "can_move", "West"))


class CompanionTests(unittest.TestCase):
    def test_a_plant_with_its_companion_in_place_yields_five_times(self) -> None:
        w = everything(6)
        call(w, "plant", "Entities.Bush")
        kind, (cx, cy) = call(w, "get_companion")
        self.assertNotEqual(kind, "Entities.Bush")
        self.assertLessEqual(abs(cx) + abs(cy), 6)
        other = w.at(cx, cy)
        other.entity, other.ground = kind.split(".")[1], "Soil"
        w.here().grown = w.here().need
        wood = w.items["Wood"]
        call(w, "harvest")
        self.assertEqual(w.items["Wood"] - wood, 5)


class SaveTests(unittest.TestCase):
    def test_a_world_survives_saving(self) -> None:
        w = everything(6, seed=9)
        call(w, "plant", "Entities.Bush")
        call(w, "use_item", "Items.Weird_Substance", 6)
        call(w, "move", "North") if w._target("North") else None
        copy = World.from_json(w.to_json())
        self.assertEqual(copy.to_json(), w.to_json())
        self.assertEqual(copy.rng.random(), w.rng.random())

    def test_snapshot_draws_every_square(self) -> None:
        w = everything(6)
        snap = w.snapshot()
        self.assertEqual(len(snap["tiles"]), 36)
        self.assertEqual(snap["drone"], {"x": 0, "y": 0, "hat": "Straw_Hat"})


if __name__ == "__main__":
    unittest.main()
