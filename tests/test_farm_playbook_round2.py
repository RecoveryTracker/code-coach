"""Farm playbook, the second round of tips: what they do on a real farm.

tests/test_farm_playbook.py already holds every entry (these ones included) to the
shape, the language gate and a clean run in every language. This file checks what
each group promises, and every expected answer is worked out from the rules of
the farm rather than read off the run: the tally from the tiles it was given, a
trial's seconds from a fresh simulated farm run on its own, a layout's lucky
plants from the wishes the farm drew, the bones from the tail the dinosaur
really dragged, the price of a maze from what the farm charges.

Original and Python run every case; JavaScript and Dart (when node and dart are
installed) run the cheap ones and one case of the dear ones, since each Dart
program, drone and simulation is a process of its own.
"""

from __future__ import annotations

import re
import unittest

# playbook first: it imports playbook_round2 at its end, and the two import each other.
from code_coach.farm import data, playbook, playbook_round2  # noqa: I001
from code_coach.farm.world import World
from tests.test_farm_playbook import (
    LANGUAGES,
    calling,
    explain,
    ripe,
    run,
    said,
    world_for,
)
from tests.test_farm_playbook_patterns import (
    count_calls,
    count_moves,
    floats,
    harvest_log,
    ints,
    lines_with,
    maze_world,
    run_files,
)

MINE = playbook_round2.ENTRIES
BY_ID = {e.id: e for e in MINE}

GROUPS = ("Dictionaries", "Utilities and Timing", "Costs", "Hats", "Imports and files",
          "Simulation", "Polyculture layouts", "Dinosaur: longer runs", "Maze: reuse and speed")

#: The two languages that are always there, and the others, when installed.
OLD = [language for language in LANGUAGES if language in ("original", "python")]
NEW = [language for language in LANGUAGES if language not in ("original", "python")]


# ── Helpers ─────────────────────────────────────────────────────────────


def ok(h, status: str) -> None:
    if status != "done":
        raise AssertionError(explain(h, status))


def line_about(h, word: str) -> str:
    """The one line of output that mentions `word`, however the language spells an item."""
    found = [line for line in said(h) if word in line.lower()]
    assert len(found) == 1, (word, said(h))
    return found[0]


def hats_worn(w) -> list[str]:
    """Every hat the program puts on, as the farm is told it ("Hats.Green_Hat")."""
    worn: list[str] = []
    real = w._do_change_hat

    def recording(args, language):
        worn.append(args[0])
        return real(args, language)

    w._do_change_hat = recording
    return worn


def trail(w) -> list[tuple[int, int, bool]]:
    """Where each move ends, and whether it happened (a blocked move stays put)."""
    seen: list[tuple[int, int, bool]] = []
    real = w._move

    def recording(direction):
        done = real(direction)
        seen.append((w.x, w.y, done))
        return done

    w._move = recording
    return seen


def tail_when_hat_comes_off(w) -> list[int]:
    """The tail's length at the moment the hat is taken off (the bones are its square)."""
    lengths: list[int] = []
    real = w._take_off_dinosaur

    def recording():
        lengths.append(len(w.tail))
        real()

    w._take_off_dinosaur = recording
    return lengths


def lucky_plants(w) -> tuple[int, int]:
    """(plants whose wished-for neighbour stands where it wished, plants), read off the field."""
    happy = total = 0
    for y in range(w.h):
        for x in range(w.w):
            tile = w.at(x, y)
            if tile.entity in ("Bush", "Tree"):
                total += 1
                kind, cx, cy = tile.companion
                happy += w.at(cx, cy).entity == kind
    return happy, total


def with_features(sim: World, *names: str) -> World:
    """A simulated farm may run code that uses these parts of the language (the game does
    not gate a simulation's own file, but this test starts it as a program of its own)."""
    for name in names:
        sim.unlocks[name] = max(2 if name == "Expand" else 1, sim.unlocks.get(name, 0))
    return sim


# ── The entries as a set ────────────────────────────────────────────────


class SetTests(unittest.TestCase):
    def test_the_nine_groups_come_in_order_and_hold_enough(self) -> None:
        groups = list(dict.fromkeys(e.group for e in MINE))
        self.assertEqual(groups, list(GROUPS))
        self.assertGreaterEqual(len(MINE), 20)
        for group in GROUPS:
            self.assertGreaterEqual(sum(e.group == group for e in MINE), 2, group)

    def test_they_are_part_of_the_playbook_after_the_other_tips(self) -> None:
        everyone = [e.id for e in playbook.ENTRIES]
        self.assertEqual(len(everyone), len(set(everyone)))
        self.assertTrue({e.id for e in MINE} <= set(everyone))
        self.assertEqual(playbook.ENTRIES[-len(MINE):], MINE)
        self.assertEqual(playbook.GROUPS[-len(GROUPS):], GROUPS)

    def test_the_file_snippets_ask_for_no_research_they_do_not_use(self) -> None:
        # The helper files import nothing themselves, so Import is not among their needs;
        # the tip says that main needs it.
        for entry_id in ("import-config", "import-names"):
            self.assertNotIn("Import", BY_ID[entry_id].needs)
            self.assertIn("Import", BY_ID[entry_id].tip)


# ── Dictionaries ────────────────────────────────────────────────────────


class DictionaryTests(unittest.TestCase):
    def run_tally(self, language: str, bushes: int, unripe: int = 0):
        e = BY_ID["dict-tally"]
        w = world_for(e, items={})
        for tile in w.tiles[:bushes]:
            ripe(tile, "Bush")
        for tile in w.tiles[bushes:bushes + unripe]:
            ripe(tile, "Bush", need=900.0, grown=0.0)
        h, status = run(w, language, e.snippets[language])
        ok(h, status)
        return w, h

    def test_the_tally_counts_each_harvested_kind_and_names_the_busiest(self) -> None:
        for language in LANGUAGES:
            with self.subTest(language=language, field="six bushes, three grass"):
                w, h = self.run_tally(language, 6)
                line = lines_with(h, "busiest").lower()
                self.assertIn("bush", line)
                self.assertEqual(ints(line), [6])
                self.assertEqual((w.items["Wood"], w.items["Hay"]), (6, 3))
            with self.subTest(language=language, field="two bushes and one unripe, six grass"):
                w, h = self.run_tally(language, 2, unripe=1)
                line = lines_with(h, "busiest").lower()
                self.assertIn("grass", line)
                self.assertEqual(ints(line), [6])
                # The unripe bush was not harvested, so it was not tallied.
                self.assertEqual(sum(t.entity == "Bush" for t in w.tiles), 1)
            with self.subTest(language=language, field="nothing ripe"):
                w, h = self.run_tally(language, 0, unripe=9)
                self.assertEqual(said(h), ["nothing was ripe"])

    def test_the_blueprint_plants_only_where_plan_and_field_disagree(self) -> None:
        e = BY_ID["dict-blueprint"]
        planned = {(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)}  # (x + y) even on a 3 by 3 field
        for language in LANGUAGES:
            with self.subTest(language=language, field="bare"):
                w = world_for(e, items={})
                calls = count_calls(w, "plant")
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                self.assertEqual({(x, y) for x in range(3) for y in range(3)
                                  if w.at(x, y).entity == "Bush"}, planned)
                self.assertEqual(calls[0], 5)
            with self.subTest(language=language, field="three right, one wrong, one missing"):
                w = world_for(e, items={})
                for spot in ((0, 0), (1, 1), (2, 2)):
                    ripe(w.at(*spot), "Bush")
                ripe(w.at(0, 2), "Carrot")   # something else stands on a planned square
                calls = count_calls(w, "plant")
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                bushes = {(x, y) for x in range(3) for y in range(3) if w.at(x, y).entity == "Bush"}
                self.assertEqual(bushes, {(0, 0), (1, 1), (2, 2), (2, 0)})
                self.assertEqual(w.at(0, 2).entity, "Carrot")  # planting over it is refused
                # Only the missing square and the carrot's were tried: the right ones cost a question.
                self.assertEqual(calls[0], 2)
                # Squares off the plan are left alone.
                self.assertTrue(all(w.at(x, y).entity == "Grass"
                                    for x in range(3) for y in range(3) if (x, y) not in planned))

    def test_two_snapshots_of_the_barn_give_what_the_pass_brought_in(self) -> None:
        e = BY_ID["dict-barn-diff"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={"Hay": 10, "Wood": 3})
                ripe(w.tiles[0], "Bush")
                ripe(w.tiles[4], "Bush")
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                self.assertEqual(ints(line_about(h, "hay")), [7])   # the seven grass squares
                self.assertEqual(ints(line_about(h, "wood")), [2])  # the two bushes
                self.assertEqual((w.items["Hay"], w.items["Wood"]), (17, 5))


# ── Utilities and Timing ────────────────────────────────────────────────


class UtilityTests(unittest.TestCase):
    PETALS = [9, 14, 7, 8, 12, 10, 11, 13, 9]

    def test_max_and_min_find_the_extremes_of_a_list_of_petals(self) -> None:
        e = BY_ID["util-extremes"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={})
                for tile, petals in zip(w.tiles, self.PETALS):
                    ripe(tile, "Sunflower", petals=petals)
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                self.assertEqual(ints(lines_with(h, "most")), [14, 7, 7])
            with self.subTest(language=language, field="no flowers"):
                h, status = run(world_for(e, items={}), language, e.snippets[language])
                ok(h, status)
                self.assertEqual(said(h), [])  # an empty list is not asked for its biggest

    def test_a_random_share_plants_none_all_or_some_and_the_same_some_in_every_language(self) -> None:
        e = BY_ID["util-random-share"]
        call = {"original": "plant_share(0.25)", "python": "plant_share(0.25)",
                "javascript": "plantShare(0.25);", "dart": "plantShare(0.25);"}
        counts = {}
        for language in LANGUAGES:
            share = call[language]
            for fraction, expect in ((0, 0), (2, 9)):
                with self.subTest(language=language, share=fraction):
                    w = world_for(e, items={})
                    h, status = run(w, language, calling(e.snippets[language], share,
                                                         share.replace("0.25", str(fraction))))
                    ok(h, status)
                    self.assertEqual(sum(t.entity == "Bush" for t in w.tiles), expect)
            with self.subTest(language=language, share=0.5):
                w = world_for(e, items={}, Expand=4, seed=1)  # 36 squares
                h, status = run(w, language, calling(e.snippets[language], share,
                                                     share.replace("0.25", "0.5")))
                ok(h, status)
                counts[language] = sum(t.entity == "Bush" for t in w.tiles)
                self.assertTrue(5 < counts[language] < 31, counts[language])
        # The drawing is the farm's own, so one seed gives one answer whoever asks.
        self.assertEqual(len(set(counts.values())), 1, counts)

    def test_the_clocks_agree_with_each_other_and_with_the_hay(self) -> None:
        e = BY_ID["timing-rate"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e)
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                gained, seconds, ticks = (float(v) for v in re.search(
                    r"(\d+) hay in ([\d.]+) seconds and (\d+) ticks", lines_with(h, "ticks")).groups())
                self.assertEqual(gained, 27)  # three laps of nine ripe squares
                # 3 laps of 12 moves (nine North, three East) and 9 harvests, 200 ticks each,
                # and a few one-tick questions.
                spent = (3 * 12 + 3 * 9) * data.ACTION_TICKS
                self.assertGreaterEqual(ticks, spent)
                self.assertLess(ticks, spent + (400 if language == "original" else 100))
                # One Speed level: a tick is a 1/600 of a second (and Original's own ticks count too).
                self.assertAlmostEqual(seconds, ticks / (data.BASE_TICKS_PER_SECOND * data.SPEED_STEP),
                                       delta=0.02 * seconds)
                self.assertAlmostEqual(floats(lines_with(h, "a second"))[0], gained / seconds, places=2)

    def test_the_loop_stops_within_a_move_of_the_deadline_and_counts_its_harvests(self) -> None:
        e = BY_ID["timing-deadline"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={})
                log = harvest_log(w)
                before = w.time
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                elapsed = w.time - before
                self.assertGreaterEqual(elapsed, 10)
                self.assertLess(elapsed, 11)
                self.assertEqual(ints(lines_with(h, "harvested"))[0], len(log))
                self.assertGreater(len(log), 5)


# ── Costs ───────────────────────────────────────────────────────────────


class CostTests(unittest.TestCase):
    def test_the_shortfall_names_what_is_missing_for_the_next_level(self) -> None:
        e = BY_ID["costs-shortfall"]
        for language in LANGUAGES:
            with self.subTest(language=language, barn="wood 5"):
                w = world_for(e, items={"Wood": 5})  # Speed 2 costs 20 wood
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                line = lines_with(h, "short")
                self.assertEqual(ints(line), [15])
                self.assertIn("wood", line.lower())
            with self.subTest(language=language, barn="enough"):
                w = world_for(e, items={"Wood": 500})
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(said(h), ["you can afford it"])
            with self.subTest(language=language, barn="speed 3 wants wood and carrots"):
                w = world_for(e, items={"Wood": 10}, Speed=2)  # costs 50 wood and 50 carrots
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                lines = sorted(said(h))
                self.assertEqual(len(lines), 2, lines)
                self.assertEqual(sorted(ints(" ".join(lines))), [40, 50])
            with self.subTest(language=language, barn="top level"):
                w = world_for(e, items={}, Speed=5)  # nothing left to buy: an empty cost
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(said(h), ["you can afford it"])

    def test_the_safe_buy_buys_every_level_it_can_pay_for_and_stops(self) -> None:
        e = BY_ID["costs-safe-buy"]
        later = data.UNLOCKS["Speed"].costs[1:]  # levels 2 to 5
        for language in LANGUAGES:
            with self.subTest(language=language, barn="rich"):
                w = world_for(e)
                before = dict(w.items)
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                self.assertEqual(ints(lines_with(h, "bought")), [4])
                self.assertEqual(w.level("Speed"), 5)
                for item in ("Wood", "Carrot"):
                    self.assertEqual(w.items[item], before[item] - sum(c.get(item, 0) for c in later))
            if language not in OLD:
                continue
            with self.subTest(language=language, barn="wood for one level"):
                w = world_for(e, items={"Wood": 30})
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                self.assertEqual(ints(lines_with(h, "bought")), [1])
                self.assertEqual((w.level("Speed"), w.items["Wood"]), (2, 10))
            with self.subTest(language=language, barn="top level"):
                w = world_for(e, Speed=5)
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                self.assertEqual(ints(lines_with(h, "bought")), [0])

    def test_how_many_is_the_least_the_barn_pays_for_at_todays_prices(self) -> None:
        e = BY_ID["costs-how-many"]
        #      barn                          Carrots level  carrots planted
        cases = [({"Hay": 5000, "Wood": 5000}, 1, 3),    # the limit of 3 stops it
                 ({"Hay": 2, "Wood": 100}, 1, 2),        # hay is short
                 ({"Hay": 50, "Wood": 1}, 1, 1),         # wood is short
                 ({"Hay": 5, "Wood": 100}, 2, 2),        # a carrot now costs 2 and 2
                 ({"Hay": 0, "Wood": 100}, 1, 0)]
        for language in LANGUAGES:
            for barn, level, expect in cases:
                with self.subTest(language=language, barn=barn, carrots=level):
                    w = world_for(e, items=barn, Carrots=level)
                    h, status = run(w, language, e.snippets[language])
                    ok(h, status)
                    self.assertEqual(ints(lines_with(h, "planted")), [expect])
                    self.assertEqual(sum(t.entity == "Carrot" for t in w.tiles), expect)
                    paid = 2 ** (level - 1) * expect
                    self.assertEqual((w.items["Hay"], w.items["Wood"]),
                                     (barn["Hay"] - paid, barn["Wood"] - paid))


# ── Hats ────────────────────────────────────────────────────────────────


class HatTests(unittest.TestCase):
    def test_every_costume_hat_costs_the_same_move_and_the_straw_hat_comes_back(self) -> None:
        e = BY_ID["hats-try-each"]
        costumes = [f"Hats.{h}" for h in data.HATS if h != "Dinosaur_Hat"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e)
                worn = hats_worn(w)
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                self.assertEqual(worn, costumes + ["Hats.Straw_Hat"])
                moves = [ints(line)[0] for line in said(h)]
                self.assertEqual(len(moves), len(costumes))
                # A move is 200 ticks in every hat (Original adds a few ticks of its own sums).
                if language != "original":
                    self.assertEqual(len(set(moves)), 1)
                for ticks in moves:
                    self.assertGreaterEqual(ticks, data.ACTION_TICKS)
                    self.assertLess(ticks, data.ACTION_TICKS + (60 if language == "original" else 1))
                self.assertEqual(w.hat, "Straw_Hat")
                self.assertEqual(w.y, len(costumes) % 3)  # seven steps North on a field of three

    def test_one_hat_change_a_lap_not_one_a_square(self) -> None:
        e = BY_ID["hats-job-colours"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={})
                worn = hats_worn(w)
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                self.assertEqual(worn, ["Hats.Green_Hat", "Hats.Purple_Hat", "Hats.Straw_Hat"])
                self.assertEqual([w.at(0, y).entity for y in range(3)], ["Bush"] * 3)
                self.assertEqual(w.items["Hay"], 3)  # the first lap cut the ripe grass
                self.assertEqual(w.hat, "Straw_Hat")


# ── Imports and files ───────────────────────────────────────────────────


class ImportTests(unittest.TestCase):
    def test_a_config_file_decides_for_main_and_one_edit_changes_it(self) -> None:
        e = BY_ID["import-config"]
        mains = {
            "original": "import config\nif config.rich_enough():\n    plant(config.CROP)\n",
            "python": "import config\nif config.rich_enough():\n    plant(config.CROP)\n",
            "javascript": 'import { CROP, richEnough } from "./config.js";\n'
                          "if (richEnough()) plant(CROP);\n",
            "dart": "import 'config.dart';\n\nvoid main() {\n  if (richEnough()) {\n"
                    "    plant(crop);\n  }\n}\n",
        }
        setting = {"original": "HAY_MIN = 50", "python": "HAY_MIN = 50", "javascript": "HAY_MIN = 50",
                   "dart": "hayMin = 50"}
        #      hay in the barn, the setting, planted?
        cases = [(100, 50, True), (10, 50, False), (10, 5, True)]
        for language in LANGUAGES:
            for hay, hay_min, planted in cases:
                with self.subTest(language=language, hay=hay, setting=hay_min):
                    w = world_for(e, items={"Hay": hay}, Import=1, Plant=1, Speed=1)
                    config = calling(e.snippets[language], setting[language],
                                     setting[language].replace("50", str(hay_min)))
                    h, status = run_files(w, language, {"main": mains[language], "config": config})
                    ok(h, status)
                    self.assertEqual(w.at(0, 0).entity == "Bush", planted)
            with self.subTest(language=language, run="the file alone"):
                w = world_for(e)
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                self.assertTrue(all(t.entity == "Grass" for t in w.tiles))

    def test_importing_by_name_leaves_main_free_to_have_a_cut_of_its_own(self) -> None:
        e = BY_ID["import-names"]
        mains = {
            "original": 'from farmlib import cut_all\n\ndef cut():\n    quick_print("my own cut")\n\ncut_all()\n',
            "python": 'from farmlib import cut_all\n\ndef cut():\n    quick_print("my own cut")\n\ncut_all()\n',
            "javascript": 'import { cutAll } from "./farmlib.js";\n\nfunction cut() {\n'
                          '  quickPrint("my own cut");\n}\n\ncutAll();\n',
            "dart": "import 'farmlib.dart' show cutAll;\n\nvoid cut() {\n  quickPrint('my own cut');\n}\n"
                    "\nvoid main() {\n  cutAll();\n}\n",
        }
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={}, Import=1, Debug=1)
                h, status = run_files(w, language, {"main": mains[language], "farmlib": e.snippets[language]})
                ok(h, status)
                self.assertEqual(said(h), [])           # farmlib's cut ran, never main's
                self.assertEqual(w.items["Hay"], 9)     # every square was cut once
            with self.subTest(language=language, run="the file alone"):
                w = world_for(e, items={})
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                self.assertEqual(w.items["Hay"], 0)


# ── Simulation ──────────────────────────────────────────────────────────


class SimulationTests(unittest.TestCase):
    @staticmethod
    def trial(language: str, code: str, research: dict, items: dict, tanks=None) -> float:
        """The game seconds a trial takes, worked out by running its file on a simulated
        farm of its own, the way simulate() builds one (a different path to the same time)."""
        setup = World.simulation_setup(
            ["main", research, items, {} if tanks is None else {"tanks": tanks}, 0, 0], language)
        sim = with_features(World.for_simulation(setup), "Loops", "Operators", "Variables",
                            "Functions", "Dictionaries", "Lists", "Debug", "Expand")
        if tanks is not None:
            code = {"original": f"tanks = {tanks}\n", "python": f"tanks = {tanks}\n",
                    "javascript": f"const tanks = {tanks};\n", "dart": ""}[language] + code
        h, status = run(sim, language, code)
        ok(h, status)
        return sim.time

    def test_the_next_speed_level_is_raced_against_this_one_and_the_real_farm_is_left_alone(self) -> None:
        e = BY_ID["sim-next-speed"]
        for language in LANGUAGES if NEW == [] else OLD + NEW[:1]:
            for level in (1, 2):
                with self.subTest(language=language, speed=level):
                    w = world_for(e, Speed=level)
                    items, tiles = dict(w.items), [(t.entity, t.ground) for t in w.tiles]
                    h, status = run(w, language, e.snippets[language])
                    ok(h, status)
                    found = re.search(r"Speed (\d+) : ([\d.]+) seconds\. Speed (\d+) : ([\d.]+) seconds",
                                      lines_with(h, "Speed"))
                    self.assertEqual((int(found.group(1)), int(found.group(3))), (level, level + 1))
                    now, later = float(found.group(2)), float(found.group(4))
                    for got, at in ((now, level), (later, level + 1)):
                        research = {"Unlocks.Expand": 3, "Unlocks.Senses": 1, "Unlocks.Speed": at}
                        self.assertAlmostEqual(
                            got, self.trial(language, e.snippets[language], research, {}), delta=0.001)
                    self.assertLess(later, now)
                    self.assertGreater(later / now, 0.5)   # a level is half as fast again, no more
                    self.assertEqual(w.items, items)
                    self.assertEqual([(t.entity, t.ground) for t in w.tiles], tiles)
                    self.assertEqual((w.x, w.y), (0, 0))

    def test_the_best_setting_wins_and_the_real_bush_is_grown_with_it(self) -> None:
        e = BY_ID["sim-best-tanks"]
        research = {"Unlocks.Plant": 1, "Unlocks.Speed": 1, "Unlocks.Watering": 1, "Unlocks.Senses": 1}
        grow = {"original": "grow_bush", "python": "grow_bush"}
        for language in OLD + NEW[:1]:
            with self.subTest(language=language):
                w = world_for(e, items={"Water": 50}, Plant=1)
                calls = count_calls(w, "use_item")
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                lines = [line for line in said(h) if "tanks:" in line]
                self.assertEqual([ints(line)[0] for line in lines], [0, 1, 2, 3, 4])
                seconds = [floats(line)[1] for line in lines]
                self.assertEqual(seconds, sorted(seconds, reverse=True))
                self.assertEqual(len(set(seconds)), 5)
                # Each is what a trial of that setting really takes on a fresh farm.
                if language in grow or language == "javascript":
                    for tanks, got in enumerate(seconds):
                        self.assertAlmostEqual(
                            got, self.trial(language, e.snippets[language], research,
                                            {"Items.Water": 4}, tanks), delta=0.001)
                # The real farm grew one bush with the winner (4 tanks) and harvested it.
                self.assertEqual(w.items["Water"], 46)
                self.assertEqual(w.items["Wood"], 1)
                self.assertEqual(w.here().entity, "Grass")
                self.assertEqual(calls[0], 1)  # the trials ran on farms of their own


# ── Polyculture layouts ─────────────────────────────────────────────────


class LayoutTests(unittest.TestCase):
    def test_bush_rows_are_planted_and_the_count_of_met_wishes_is_what_the_field_shows(self) -> None:
        e = BY_ID["poly-grass-rows"]
        seen_happy = 0
        for language in LANGUAGES:
            for seed in (1, 2, 3, 4) if language in OLD else (1,):
                with self.subTest(language=language, seed=seed):
                    w = world_for(e, seed=seed, Expand=4)  # 6 by 6
                    h, status = run(w, language, e.snippets[language])
                    ok(h, status)
                    for y in range(6):
                        want = "Bush" if y % 2 == 0 else "Grass"
                        self.assertEqual({w.at(x, y).entity for x in range(6)}, {want}, y)
                    happy, bushes = lucky_plants(w)
                    self.assertEqual(ints(lines_with(h, "wish")), [happy, bushes])
                    self.assertEqual(bushes, 18)
                    seen_happy += happy
                    # A happy bush really pays five times: its friend is grass, where it wished.
                    for y in (0, 2, 4):
                        for x in range(6):
                            tile = w.at(x, y)
                            kind, cx, cy = tile.companion
                            self.assertEqual(w._companion_bonus(tile) > 1, w.at(cx, cy).entity == kind)
        self.assertGreater(seen_happy, 0)  # the layout does meet some wishes

    def test_the_checkerboard_has_no_tree_beside_a_tree_and_counts_its_lucky_plants(self) -> None:
        e = BY_ID["poly-checkerboard"]
        seen_happy = 0
        for language in LANGUAGES:
            for seed in (1, 2, 3, 4) if language in OLD else (1,):
                with self.subTest(language=language, seed=seed):
                    w = world_for(e, seed=seed, Expand=4)
                    h, status = run(w, language, e.snippets[language])
                    ok(h, status)
                    for x in range(6):
                        for y in range(6):
                            self.assertEqual(w.at(x, y).entity, "Tree" if (x + y) % 2 == 0 else "Bush")
                    happy, plants = lucky_plants(w)
                    self.assertEqual(ints(lines_with(h, "wish")), [happy, 36])
                    self.assertEqual(plants, 36)
                    seen_happy += happy
        self.assertGreater(seen_happy, 0)


# ── Dinosaur: longer runs ───────────────────────────────────────────────


class DinosaurTests(unittest.TestCase):
    def dino_world(self, e, cactus: int = 100, seed: int = 1) -> World:
        return world_for(e, items={"Cactus": cactus}, Expand=3, seed=seed)  # 4 by 4

    def test_the_loop_visits_every_square_each_lap_and_the_tail_never_blocks_it(self) -> None:
        e = BY_ID["dino-cycle"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = self.dino_world(e)
                moves = trail(w)
                tails = tail_when_hat_comes_off(w)
                code = calling(e.snippets[language], "ride(2)", "ride(3)")
                h, status = run(w, language, code)
                ok(h, status)
                self.assertEqual(len(moves), 3 * 16)
                self.assertTrue(all(done for _x, _y, done in moves), "a move was blocked")
                for lap in range(3):
                    squares = [(x, y) for x, y, _ in moves[lap * 16:(lap + 1) * 16]]
                    self.assertEqual(len(set(squares)), 16, f"lap {lap}")
                steps = [(0, 0)] + [(x, y) for x, y, _ in moves]
                for (ax, ay), (bx, by) in zip(steps, steps[1:]):
                    self.assertEqual(abs(ax - bx) + abs(ay - by), 1)  # never wraps: the hat forbids it
                self.assertEqual(len(tails), 1)
                self.assertGreaterEqual(tails[0], 3)               # an apple or more a lap
                self.assertEqual(w.items["Bone"], tails[0] ** 2)  # the tail's length squared
                self.assertEqual(w.hat, "Straw_Hat")

    def test_riding_until_the_tail_is_long_enough_banks_its_square(self) -> None:
        e = BY_ID["dino-bank"]
        for language in LANGUAGES:
            for target in (4, 6) if language in OLD else (4,):
                with self.subTest(language=language, target=target):
                    w = self.dino_world(e)
                    tails = tail_when_hat_comes_off(w)
                    code = calling(e.snippets[language],
                                   "ride_until(4)" if language in OLD else "rideUntil(4)",
                                   ("ride_until(%d)" if language in OLD else "rideUntil(%d)") % target)
                    h, status = run(w, language, code)
                    ok(h, status)
                    self.assertEqual(ints(lines_with(h, "tail")), [target])
                    self.assertEqual(tails, [target])
                    self.assertEqual(w.items["Bone"], target * target)
                    self.assertEqual(w.hat, "Straw_Hat")

    def test_when_the_cactus_runs_out_the_step_budget_ends_the_ride_and_banks_what_there_is(self) -> None:
        e = BY_ID["dino-bank"]
        for language in OLD:
            with self.subTest(language=language):
                w = self.dino_world(e, cactus=4)  # two apples at 2 cactus each
                moves = trail(w)
                tails = tail_when_hat_comes_off(w)
                h, status = run(w, language, e.snippets[language])
                ok(h, status)
                self.assertEqual(ints(lines_with(h, "tail")), [2])
                self.assertEqual(tails, [2])
                self.assertEqual(w.items["Bone"], 4)
                self.assertEqual(w.items["Cactus"], 0)
                self.assertEqual(len(moves), 20 * 16)  # the budget: 20 laps, none blocked
                self.assertTrue(all(done for _x, _y, done in moves))


# ── Maze: reuse and speed ───────────────────────────────────────────────


class MazeTests(unittest.TestCase):
    def test_the_way_towards_the_treasure_first_beats_a_fixed_order_in_reused_mazes(self) -> None:
        e = BY_ID["maze-toward"]
        greedy_code = e.snippets["python"]
        # The same search with every direction counted as "towards": plain north-east-south-west.
        plain_code = calling(greedy_code, "toward = [ty > get_pos_y(), tx > get_pos_x(), "
                             "ty < get_pos_y(), tx < get_pos_x()]", "toward = [True, True, True, True]")
        totals = {"greedy": 0, "plain": 0}
        for seed in range(1, 9):
            for name, code in (("greedy", greedy_code), ("plain", plain_code)):
                w = maze_world(e, seed, loops=3, at=(3, 3), expand=4)  # 6 by 6, treasure moved 3 times
                moved = count_moves(w)
                h, status = run(w, "python", code)
                ok(h, status)
                self.assertEqual(w.items["Gold"], 36, f"{name} seed {seed}")  # it reached the treasure
                self.assertIsNone(w.maze)
                totals[name] += moved[0]
        self.assertLess(totals["greedy"], totals["plain"], totals)

    def test_it_reaches_the_treasure_in_every_language(self) -> None:
        e = BY_ID["maze-toward"]
        for language in LANGUAGES:
            for seed in (1, 2, 3) if language in OLD else (1,):
                with self.subTest(language=language, seed=seed):
                    w = maze_world(e, seed, loops=2)
                    h, status = run(w, language, e.snippets[language])
                    ok(h, status)
                    self.assertEqual(w.items["Gold"], 16)
                    self.assertIsNone(w.maze)

    def test_the_plan_is_what_the_barn_the_price_and_the_limit_allow(self) -> None:
        e = BY_ID["maze-hop-plan"]
        #      barn   Mazes level   hops   gold
        cases = [(500, 1, 165, 1494),    # 3 a time: 166 payments, the first grows the maze
                 (500, 2, 82, 1494),     # 6 a time, but twice the gold a treasure
                 (5000, 1, 300, 2709),   # the limit of 300 hops
                 (3, 1, 0, 9),           # one maze and no hops
                 (2, 1, None, None)]
        for language in LANGUAGES:
            for barn, level, hops, gold in cases:
                with self.subTest(language=language, barn=barn, mazes=level):
                    w = world_for(e, items={"Weird_Substance": barn}, Mazes=level)
                    h, status = run(w, language, e.snippets[language])
                    ok(h, status)
                    if hops is None:
                        self.assertEqual(said(h), ["not enough Weird Substance for a maze"])
                    else:
                        self.assertEqual(ints(lines_with(h, "hops")), [hops, gold])

    def test_the_farm_charges_and_pays_as_the_plan_says_and_stops_after_300_hops(self) -> None:
        e = BY_ID["maze-hop-plan"]

        def grown(barn: int) -> World:
            w = world_for(e, items={"Weird_Substance": barn}, Plant=1, Fertilizer=1)
            w.x = w.y = 1
            self.assertTrue(w.call("plant", ["Entities.Bush"])[0])
            self.assertTrue(w.call("use_item", ["Items.Weird_Substance", 3])[0])  # the first batch
            return w

        def hop(w: World) -> bool:
            w.x, w.y = w.maze.treasure
            return w.call("use_item", ["Items.Weird_Substance", 3])[0]

        # 13 Weird Substance is four batches of 3: the maze, then three hops.
        w = grown(13)
        hops = 0
        while hop(w):
            hops += 1
        self.assertEqual(hops, 3)
        self.assertEqual(w.items["Gold"], 3 * 9)
        w.x, w.y = w.maze.treasure
        w.call("harvest", [])
        self.assertEqual(w.items["Gold"], 4 * 9)  # (hops + 1) * size * cost: the plan's gold
        # With plenty in the barn the treasure still moves only 300 times.
        w = grown(5000)
        w.maze.moved = 298
        hops = 0
        while hop(w):
            hops += 1
        self.assertEqual(hops, 2)


if __name__ == "__main__":
    unittest.main()
