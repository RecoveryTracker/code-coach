"""Farm playbook: every tip's snippet, in all four languages, held to the farm.

A snippet is only worth pasting if it works, so each one is held to three
things. The shape: ids are unique, every language has code, and `needs`
names real research. The gate: with exactly the research a snippet lists
(and no more) the language gate lets it through, and with a part of the
language missing it does not. And the farm: each snippet is started for
real, in every language that is installed, on a farm with exactly that
research, and the ones with something to prove - the pumpkin check, go_to,
the sweep, the maze solvers, the cactus sort - are run on a farm arranged
to prove it.
"""

from __future__ import annotations

import json
import random
import re
import shutil
import time
import unittest
from pathlib import Path

from code_coach.engine import dart_path
from code_coach.farm import data, gate, playbook, protocol
from code_coach.farm.data import UNLOCKS
from code_coach.farm.playbook import ENTRIES, Entry
from code_coach.farm.runner import FarmHost
from code_coach.farm.world import World

HAS_NODE = shutil.which("node") is not None
HAS_DART = dart_path() is not None
#: The JavaScript gate reads code with TypeScript; without it, it lets everything through.
HAS_JS_GATE = HAS_NODE and gate.TYPESCRIPT.is_dir()

LANGUAGES = ["original", "python"] + (["javascript"] if HAS_NODE else []) + (["dart"] if HAS_DART else [])

BY_ID = {entry.id: entry for entry in ENTRIES}

#: stubs/farm_api.dart declares `bool swap(...)` and casts the farm's answer to bool,
#: but the farm answers a swap with null - so in Dart every swap() throws. The cactus
#: snippet is right; its Dart run waits for that to be fixed (and starts running by itself).
DART_SWAP_BROKEN = "bool swap(" in (
    Path(gate.__file__).parent / "stubs" / "farm_api.dart").read_text(encoding="utf-8")


def skip_if_swap_is_broken(entry_id: str, language: str) -> None:
    if entry_id == "cactus-sort" and language == "dart" and DART_SWAP_BROKEN:
        raise unittest.SkipTest("farm_api.dart's swap() casts the farm's null answer to bool")

#: What a farm has in the barn for these tests: plenty of everything a snippet might spend.
RICH = {"Hay": 5000, "Wood": 5000, "Carrot": 5000, "Pumpkin": 5000, "Water": 50,
        "Weird_Substance": 500}


# ── Helpers ─────────────────────────────────────────────────────────────


def gate_language(language: str) -> str:
    """The game's own language is Python's syntax, and is gated as Python."""
    return "python" if language == "original" else language


def features_of(needs, levels: dict[str, int]) -> set[str]:
    """The parts of the language that research brings, at the levels given."""
    found: set[str] = set()
    for name in needs:
        for level, features in UNLOCKS[name].features.items():
            if level <= levels.get(name, 1):
                found.update(features)
    return found


def world_for(entry: Entry, items: dict | None = None, seed: int = 1, **levels: int) -> World:
    """A farm with exactly the research the entry lists (at its levels), a barn well
    stocked, and every square's grass ripe."""
    w = World(seed=seed)
    wanted = {name: 1 for name in entry.needs}
    wanted.update(entry.levels)
    wanted.update(levels)
    for name, level in wanted.items():
        w.unlocks[name] = level
    w.width, w.height = data.FARM_SIZES[w.level("Expand")]
    w._fill()
    for item, amount in (RICH if items is None else items).items():
        w.items[item] = amount
    w.advance(5)
    return w


def finish(h: FarmHost, timeout: float = 90.0) -> str:
    deadline = time.monotonic() + timeout
    while h.run and h.run.status in ("starting", "running"):
        if time.monotonic() > deadline:
            h.stop_run(wait=True)
            raise AssertionError("the program did not finish")
        time.sleep(0.02)
    return h.run.status if h.run else "none"


def run(world: World, language: str, code: str) -> tuple[FarmHost, str]:
    """Run a program on a farm the way the Run button does, at full warp."""
    h = FarmHost()
    h.warp = 0
    h._load()
    h.world = world
    h.save = lambda: None  # the farm under test is the one handed in, not a file on disk
    started = h.start(language, code)
    if not started["ok"]:
        return h, f"refused: {started}"
    return h, finish(h)


def said(h: FarmHost) -> list[str]:
    return [line["text"] for line in h.output if line["kind"] in ("print", "out")]


def explain(h: FarmHost, status: str) -> str:
    return f"{status}: {h.run.error!r} (line {h.run.error_line})" if h.run else status


def calling(code: str, old: str, new: str) -> str:
    """The snippet with its example call changed - the call must be there to change."""
    assert code.count(old) == 1, f"{old!r} should appear once in\n{code}"
    return code.replace(old, new)


def ripe(tile, entity: str, **fields) -> None:
    tile.ground = "Soil"
    tile.entity = entity
    tile.need = tile.grown = 1.0
    tile.companion = None
    for name, value in fields.items():
        setattr(tile, name, value)


def pumpkin_field(w: World) -> None:
    for tile in w.tiles:
        ripe(tile, "Pumpkin")
    w._changed()


def strip(code: str) -> str:
    """Code without strings and comments, to read the names in it."""
    code = re.sub(r"'(?:\\.|[^'\\\n])*'|\"(?:\\.|[^\"\\\n])*\"", '""', code)
    return re.sub(r"(//|#).*", "", code)


# What the code calls, by the game's own (Python) names.

_SPELLINGS = {
    language: {getattr(f, attr): f.py for f in protocol.FUNCTIONS}
    for language, attr in (("python", "py"), ("javascript", "js"), ("dart", "dart"))
}
_SPELLINGS["original"] = _SPELLINGS["python"]

PROVIDERS: dict[str, list[tuple[str, int]]] = {}
for _u in UNLOCKS.values():
    for _level, _names in _u.functions.items():
        for _name in _names:
            PROVIDERS.setdefault(_name, []).append((_u.name, _level))


def api_calls(code: str, language: str) -> set[str]:
    """The farm's functions the snippet calls (by Python name), not counting its own."""
    code = strip(code) + " " + " ".join(re.findall(r"\$\{([^}]*)\}", code))  # Dart's ${...} is code
    names = {m.group(1) for m in re.finditer(r"\b([A-Za-z_]\w*)\s*\(", code)}
    own = {m.group(1) for m in re.finditer(r"\b(?:def|function)\s+(\w+)", code)}
    own |= {m.group(1) for m in re.finditer(r"\b(?:void|bool|int|double)\s+(\w+)\s*\(", code)}
    return {_SPELLINGS[language][n] for n in names - own if n in _SPELLINGS[language]}


def named_values(code: str) -> set[tuple[str, str]]:
    """Entities.Bush / Entities.bush: the same value, however the language spells it."""
    found = {(g, m.lower().replace("_", "")) for g, m in re.findall(
        r"\b(Entities|Items|Grounds|Unlocks|Hats)\.(\w+)", strip(code))}
    found |= {("Direction", d.lower()) for d in re.findall(
        r"\b(North|East|South|West|north|east|south|west)\b", strip(code))}
    return found


# ── The shape ───────────────────────────────────────────────────────────


class ShapeTests(unittest.TestCase):
    def test_there_are_enough_entries_in_groups_in_order(self) -> None:
        self.assertGreaterEqual(len(ENTRIES), 16)
        self.assertLessEqual(len(ENTRIES), 24)
        self.assertEqual(
            playbook.GROUPS,
            ("Moving", "Planting", "Pumpkins", "Sunflowers", "Cactus", "Maze", "Speed", "Tips"),
        )
        seen = [e.group for e in ENTRIES]
        self.assertEqual(seen, sorted(seen, key=playbook.GROUPS.index), "entries run group by group")

    def test_ids_are_unique(self) -> None:
        ids = [e.id for e in ENTRIES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(re.fullmatch(r"[a-z]+(-[a-z]+)*", i) for i in ids), ids)

    def test_every_entry_has_a_title_a_tip_and_all_four_languages(self) -> None:
        for e in ENTRIES:
            with self.subTest(entry=e.id):
                self.assertTrue(e.title.strip())
                self.assertTrue(e.tip.strip())
                self.assertLessEqual(e.tip.count(". ") + 1, 7, "a tip is a few plain sentences")
                self.assertEqual(set(e.snippets), set(playbook.LANGUAGES))
                for language, code in e.snippets.items():
                    self.assertTrue(code.strip(), language)
                    self.assertNotIn("\r", code)
                    self.assertTrue(code.endswith("\n") and not code.endswith("\n\n"), language)
                    self.assertLessEqual(len(code.splitlines()), 40, f"{e.id} in {language}")

    def test_needs_are_real_unlocks_at_real_levels(self) -> None:
        for e in ENTRIES:
            with self.subTest(entry=e.id):
                self.assertEqual(len(e.needs), len(set(e.needs)))
                for name in e.needs:
                    self.assertIn(name, UNLOCKS)
                    self.assertFalse(UNLOCKS[name].missing, name)
                for name, level in e.levels.items():
                    self.assertIn(name, e.needs)
                    self.assertLessEqual(level, UNLOCKS[name].starts_at + len(UNLOCKS[name].costs))

    def test_the_screen_gets_plain_data(self) -> None:
        sent = playbook.entries()
        self.assertEqual(len(sent), len(ENTRIES))
        json.dumps(sent)
        for row, e in zip(sent, ENTRIES):
            self.assertEqual(set(row), {"id", "group", "title", "tip", "needs", "levels", "snippets"})
            self.assertEqual(row["id"], e.id)
            self.assertEqual(row["needs"], list(e.needs))
            self.assertEqual(set(row["snippets"]), {"original", "python", "javascript", "dart"})

    def test_the_four_languages_say_the_same_thing(self) -> None:
        # Same farm functions, same named values (Entities.Bush = Entities.bush = ...).
        for e in ENTRIES:
            with self.subTest(entry=e.id):
                base_calls = api_calls(e.snippets["python"], "python")
                base_values = named_values(e.snippets["python"])
                for language in ("original", "javascript", "dart"):
                    code = e.snippets[language]
                    self.assertEqual(api_calls(code, language), base_calls, language)
                    self.assertEqual(named_values(code), base_values, language)

    def test_the_pumpkin_check_and_helper_are_in_the_snippet_a_player_reads(self) -> None:
        merged = BY_ID["pumpkin-merged"].snippets
        self.assertIn("fully_merged", merged["python"])
        self.assertIn("fullyMerged", merged["javascript"])
        self.assertIn("get_pos_x() > 0", merged["python"])
        self.assertEqual(merged["python"].count("measure()"), 2)  # the two corners


# ── The gate ────────────────────────────────────────────────────────────


class GateTests(unittest.TestCase):
    def check(self, e: Entry, language: str, unlocked: set[str]):
        return gate.check(e.snippets[language], gate_language(language), unlocked)

    def test_each_snippet_passes_with_exactly_its_needs(self) -> None:
        for e in ENTRIES:
            unlocked = features_of(e.needs, e.levels)
            for language in playbook.LANGUAGES:
                with self.subTest(entry=e.id, language=language):
                    if language == "javascript" and not HAS_JS_GATE:
                        self.skipTest("the JavaScript gate needs node and TypeScript")
                    self.assertEqual(self.check(e, language, unlocked), [])

    def test_no_snippet_needs_a_part_of_the_language_it_does_not_use(self) -> None:
        # Take each need that is language, away: something must be refused.
        for e in ENTRIES:
            for name in e.needs:
                brings = features_of([name], e.levels)
                if not brings:
                    continue
                rest = features_of([n for n in e.needs if n != name], e.levels)
                lost = brings - rest
                if not lost:
                    continue
                for language in ("python", "dart") + (("javascript",) if HAS_JS_GATE else ()):
                    with self.subTest(entry=e.id, take_away=name, language=language):
                        refused = {v.feature for v in self.check(e, language, rest)}
                        if refused & lost:
                            continue
                        # Then the need must be here for something else: a function it brings.
                        calls = api_calls(e.snippets[language], language)
                        owns = any({p for p, _ in PROVIDERS.get(c, [])} & {name} for c in calls)
                        self.assertTrue(owns, f"{name} is neither used as language nor for a function")

    def test_every_need_is_used_by_something(self) -> None:
        entity_unlock = {"Bush": "Plant", "Tree": "Trees", "Carrot": "Carrots",
                         "Pumpkin": "Pumpkins", "Sunflower": "Sunflowers", "Cactus": "Cactus"}
        for e in ENTRIES:
            code = e.snippets["python"]
            calls = api_calls(code, "python")
            used = {name for c in calls for name, _ in PROVIDERS.get(c, [])}
            used |= {entity_unlock[m] for m in re.findall(r"Entities\.(\w+)", code) if m in entity_unlock}
            used |= set(re.findall(r"Unlocks\.(\w+)", code))
            used |= {n for n in e.needs if features_of([n], e.levels)}  # language: tested above
            for name in e.needs:
                with self.subTest(entry=e.id, need=name):
                    self.assertIn(name, used)

    def test_every_function_it_calls_is_researched_by_its_needs(self) -> None:
        for e in ENTRIES:
            for language in playbook.LANGUAGES:
                with self.subTest(entry=e.id, language=language):
                    for call in api_calls(e.snippets[language], language):
                        if call in data.STARTING_FUNCTIONS:
                            continue
                        ok = any(name in e.needs and level <= e.levels.get(name, 1)
                                 for name, level in PROVIDERS[call])
                        self.assertTrue(ok, f"{call}() needs one of {PROVIDERS[call]}")

    def test_with_less_language_the_gate_stops_real_examples(self) -> None:
        # (entry, the part of the language to take away, what the gate must name)
        cases = [
            ("move-go-to", "functions", "functions"),
            ("move-go-to", "for", "for"),
            ("move-go-to", "operators", "operators"),
            ("move-sweep", "variables", "variables"),
            ("move-wrap", "while", "while"),
            ("plant-harvest-replant", "if", "if"),
            ("pumpkin-merged", "operators", "operators"),
            ("pumpkin-loop", "while", "while"),
            ("maze-right-hand", "lists", "lists"),
            ("maze-reuse", "lists", "lists"),
            ("cactus-sort", "if", "if"),
        ]
        for entry_id, away, named in cases:
            e = BY_ID[entry_id]
            full = features_of(e.needs, e.levels)
            self.assertIn(away, full, f"{entry_id} should be using {away}")
            for language in playbook.LANGUAGES:
                if language == "javascript" and not HAS_JS_GATE:
                    continue
                with self.subTest(entry=entry_id, away=away, language=language):
                    refused = {v.feature for v in self.check(e, language, full - {away})}
                    self.assertIn(named, refused)

    def test_below_the_square_farm_the_loops_are_refused(self) -> None:
        # Expand level 1 is a column of three: no `for`, and no get_world_size().
        e = BY_ID["move-sweep"]
        one = features_of(e.needs, {"Expand": 1})
        self.assertNotIn("for", one)
        self.assertTrue({v.feature for v in self.check(e, "python", one)} >= {"for"})
        self.assertEqual(e.levels, {"Expand": 2})


# ── The farm ────────────────────────────────────────────────────────────


def arrange(entry_id: str, w: World) -> None:
    """Set the farm up as the snippet's tip says to start: cacti on every tile, a maze to solve."""
    if entry_id == "cactus-sort":
        rng = random.Random(3)
        for tile in w.tiles:
            ripe(tile, "Cactus", size=rng.randrange(10))
    elif entry_id in ("maze-right-hand", "maze-reuse"):
        w._grow_maze(w.w, w.w)


class EverySnippetRunsTests(unittest.TestCase):
    """Each snippet started for real, on a farm with exactly the research it lists."""

    def test_every_snippet_runs_to_the_end(self) -> None:
        for e in ENTRIES:
            for language in LANGUAGES:
                with self.subTest(entry=e.id, language=language):
                    skip_if_swap_is_broken(e.id, language)
                    w = world_for(e)
                    arrange(e.id, w)
                    h, status = run(w, language, e.snippets[language])
                    self.assertEqual(status, "done", explain(h, status))


class MovingTests(unittest.TestCase):
    def test_go_to_ends_on_the_target_by_the_short_way(self) -> None:
        e = BY_ID["move-go-to"]
        n = 6
        #           start   target
        cases = [((0, 0), (5, 5)), ((1, 1), (4, 4)), ((5, 0), (0, 5)), ((2, 3), (2, 3)),
                 ((0, 0), (3, 2)), ((4, 1), (1, 4)), ((3, 3), (0, 0))]
        for language in LANGUAGES:
            call = {"original": "go_to(2, 1)", "python": "go_to(2, 1)"}.get(language, "goTo(2, 1)")
            for start, target in cases:
                with self.subTest(language=language, start=start, target=target):
                    w = world_for(e, Expand=4)
                    self.assertEqual((w.w, w.h), (n, n))
                    w.x, w.y = start
                    code = calling(e.snippets[language], call,
                                   call.replace("2, 1", f"{target[0]}, {target[1]}"))
                    h, status = run(w, language, code)
                    self.assertEqual(status, "done", explain(h, status))
                    self.assertEqual((w.x, w.y), target)
                    short = sum(min(d, n - d) for d in (
                        (target[0] - start[0]) % n, (target[1] - start[1]) % n))
                    # A move is 200 ticks and everything else a few: the moves are counted exactly.
                    self.assertEqual(w.run_ticks // 200, short, f"ticks {w.run_ticks}")

    def test_the_sweep_visits_every_tile_once_with_no_wasted_move(self) -> None:
        e = BY_ID["move-sweep"]
        n = 4
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, Expand=3)
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                visited = [tuple(int(v) for v in re.findall(r"\d+", line)) for line in said(h)]
                self.assertEqual(len(visited), n * n)
                self.assertEqual(set(visited), {(x, y) for x in range(n) for y in range(n)})
                for (ax, ay), (bx, by) in zip(visited, visited[1:]):
                    steps = min((bx - ax) % n, (ax - bx) % n) + min((by - ay) % n, (ay - by) % n)
                    self.assertEqual(steps, 1, f"{(ax, ay)} -> {(bx, by)}")

    def test_one_step_West_and_South_from_the_origin_is_the_far_corner(self) -> None:
        e = BY_ID["move-wrap"]
        for language in LANGUAGES:
            for start in ((0, 0), (2, 1), (3, 3), (0, 3)):
                with self.subTest(language=language, start=start):
                    w = world_for(e, Expand=3)
                    w.x, w.y = start
                    h, status = run(w, language, e.snippets[language])
                    self.assertEqual(status, "done", explain(h, status))
                    self.assertEqual((w.x, w.y), (3, 3))
                    if start == (0, 0):
                        self.assertEqual(w.run_ticks // 200, 2)  # not 6


class PlantingTests(unittest.TestCase):
    def test_harvest_and_replant_turns_a_column_of_grass_into_bushes(self) -> None:
        e = BY_ID["plant-harvest-replant"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={})
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertEqual([w.at(0, y).entity for y in range(3)], ["Bush"] * 3)
                self.assertEqual(w.items["Hay"], 3)
                self.assertEqual(w.at(1, 0).entity, "Grass")

    def test_an_unripe_plant_is_left_alone(self) -> None:
        e = BY_ID["plant-harvest-replant"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={})
                w.at(0, 1).need, w.at(0, 1).grown = 900.0, 0.0
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertEqual([w.at(0, y).entity for y in range(3)], ["Bush", "Grass", "Bush"])

    def test_till_then_plant_makes_soil_once(self) -> None:
        e = BY_ID["plant-till"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e)
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertEqual((w.here().ground, w.here().entity), ("Soil", "Carrot"))
                # Already soil: it must not be tilled back to grass.
                again = world_for(e)
                again.here().ground = "Soil"
                again.here().entity = None
                h, status = run(again, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertEqual((again.here().ground, again.here().entity), ("Soil", "Carrot"))

    def test_water_tops_up_to_the_level(self) -> None:
        e = BY_ID["plant-water"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e)
                w.here().water = 0.0
                tanks = w.items["Water"]
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertGreaterEqual(w.here().water, 0.74)
                self.assertLess(w.here().water, 1.0)
                self.assertIn(tanks - w.items["Water"], (3, 4))
        # And with no water in the barn it stops rather than spinning.
        dry = world_for(e, items={"Water": 0})
        h, status = run(dry, "python", e.snippets["python"])
        self.assertEqual(status, "done", explain(h, status))

    def test_companion_says_what_is_wanted_and_where(self) -> None:
        e = BY_ID["plant-companion"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e)
                w.here().companion = ("Carrot", 2, 1)
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                text = " ".join(said(h)).lower()
                self.assertIn("carrot", text)
                self.assertRegex(text, r"2\D+1")
                none = world_for(e)
                none.here().companion = None
                h, status = run(none, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertIn("nothing wanted", " ".join(said(h)))


class PumpkinTests(unittest.TestCase):
    def merged_run(self, language: str, arrange_field, start=(0, 0)):
        e = BY_ID["pumpkin-merged"]
        w = world_for(e)  # 3 by 3
        pumpkin_field(w)
        arrange_field(w)
        w._changed()
        w.x, w.y = start
        h, status = run(w, language, e.snippets[language])
        self.assertEqual(status, "done", explain(h, status))
        return w

    def test_a_field_of_ripe_pumpkins_is_one_giant_and_is_harvested(self) -> None:
        for language in LANGUAGES:
            for start in ((0, 0), (1, 2), (2, 2), (2, 0)):
                with self.subTest(language=language, start=start):
                    w = self.merged_run(language, lambda w: None, start)
                    self.assertEqual(w.items["Pumpkin"], 5000 + 27)  # a 3 by 3 giant: 3 cubed
                    self.assertTrue(all(t.entity != "Pumpkin" for t in w.tiles))

    def test_the_helper_says_yes_only_for_a_giant(self) -> None:
        e = BY_ID["pumpkin-merged"]
        # Each language's example call, and what to say instead: print the helper's answer.
        ending = {
            "original": ("if fully_merged():", "quick_print(fully_merged())\n"),
            "python": ("if fully_merged():", "quick_print(fully_merged())\n"),
            "javascript": ("if (fullyMerged())", "quickPrint(String(fullyMerged()));\n"),
            "dart": ("void main() {", "void main() {\n  quickPrint('${fullyMerged()}');\n}\n"),
        }

        def unripe(x: int, y: int):
            return lambda w: (setattr(w.at(x, y), "need", 900.0), setattr(w.at(x, y), "grown", 0.0))

        def entity(x: int, y: int, what):
            return lambda w: setattr(w.at(x, y), "entity", what)

        cases = {
            "the whole field": (lambda w: None, "true"),
            "one tile unripe": (unripe(1, 1), "false"),
            "the far corner unripe": (unripe(2, 2), "false"),
            "the origin unripe": (unripe(0, 0), "false"),
            "a tile dead": (entity(1, 0, "Dead_Pumpkin"), "false"),
            "both corners dead": (lambda w: (entity(0, 0, "Dead_Pumpkin")(w),
                                             entity(2, 2, "Dead_Pumpkin")(w)), "false"),
            "a tile missing": (entity(2, 1, None), "false"),
        }
        for language in LANGUAGES:
            code = e.snippets[language]
            marker, replacement = ending[language]
            probe = code[: code.index(marker)] + replacement
            for name, (change, expect) in cases.items():
                with self.subTest(language=language, field=name):
                    w = world_for(e, Debug=1)
                    pumpkin_field(w)
                    change(w)
                    w._changed()
                    h, status = run(w, language, probe)
                    self.assertEqual(status, "done", explain(h, status))
                    self.assertEqual(said(h)[-1].strip().lower(), expect)

    def test_it_does_not_harvest_a_field_that_is_not_done(self) -> None:
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = self.merged_run(language, lambda w: setattr(w.at(1, 1), "grown", 0.0) or
                                    setattr(w.at(1, 1), "need", 900.0))
                self.assertEqual(w.items["Pumpkin"], 5000)
                self.assertEqual(sum(t.entity == "Pumpkin" for t in w.tiles), 9)

    def test_the_whole_loop_grows_one_giant_from_bare_grass(self) -> None:
        e = BY_ID["pumpkin-loop"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, seed=4)
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertEqual(w.items["Pumpkin"] - 5000, 27)
                self.assertLessEqual(w.items["Carrot"], 5000 - 9)  # the planting cost carrots

    def test_planting_the_square_fills_every_tile_with_a_pumpkin_on_soil(self) -> None:
        e = BY_ID["pumpkin-square"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e)
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                # (One in five dies as it ripens, which is why the loop replaces the dead.)
                self.assertTrue(all(t.entity in ("Pumpkin", "Dead_Pumpkin") and t.ground == "Soil"
                                    for t in w.tiles))
                self.assertEqual((w.x, w.y), (0, 0))


class SunflowerCactusTests(unittest.TestCase):
    PETALS = [15, 15, 14, 13, 12, 12, 11, 10, 10, 9, 9, 8, 8, 7, 7, 7]

    def test_the_biggest_flowers_go_first_and_earn_the_bonus(self) -> None:
        e = BY_ID["sunflower-biggest-first"]
        # Sixteen flowers, so ten or more stand until the seventh harvest: seven bonuses.
        bonus_ceiling = 7 * data.SUNFLOWER_BONUS + 9
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, Expand=3, items={})
                order = list(self.PETALS)
                random.Random(5).shuffle(order)
                for tile, petals in zip(w.tiles, order):
                    ripe(tile, "Sunflower", petals=petals)
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertFalse(any(t.entity == "Sunflower" for t in w.tiles))
                # Running burns a little of the power (one per 6000 ticks): the bonus is mostly intact.
                self.assertGreater(w.items["Power"], bonus_ceiling - 12)
                self.assertFalse(w.sunflower_spoiled)

    def test_the_sort_leaves_the_field_sorted_and_the_harvest_takes_all_of_it(self) -> None:
        e = BY_ID["cactus-sort"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                skip_if_swap_is_broken(e.id, language)
                w = world_for(e, Expand=3, items={})
                arrange("cactus-sort", w)
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertEqual(w.items["Cactus"], 16 * 16)  # one patch of 16: 16 squared
                self.assertFalse(any(t.entity == "Cactus" for t in w.tiles))


class MazeTests(unittest.TestCase):
    def maze_world(self, e: Entry, seed: int, size: int = 4, at=(1, 2)) -> World:
        w = world_for(e, seed=seed, items={"Weird_Substance": 500}, Expand=3 if size == 4 else 7)
        w.x, w.y = at
        w._grow_maze(w.w, w.w)
        return w

    def test_the_right_hand_rule_walks_a_new_maze_to_the_treasure(self) -> None:
        e = BY_ID["maze-right-hand"]
        for language in LANGUAGES:
            seeds = range(1, 7) if language in ("original", "python") else (1, 2)
            for seed in seeds:
                with self.subTest(language=language, seed=seed):
                    w = self.maze_world(e, seed)
                    treasure = w.maze.treasure
                    h, status = run(w, language, e.snippets[language])
                    self.assertEqual(status, "done", explain(h, status))
                    self.assertEqual(w.items["Gold"], 16)  # 4 by 4: the area
                    self.assertEqual((w.x, w.y), treasure)
                    self.assertIsNone(w.maze)

    def test_a_bigger_maze_too(self) -> None:
        e = BY_ID["maze-right-hand"]
        for language in ("python",) + (("dart",) if HAS_DART else ()):
            with self.subTest(language=language):
                w = self.maze_world(e, 3, size=12, at=(5, 5))
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertEqual(w.items["Gold"], 144)

    def test_reusing_the_maze_pays_every_time_even_when_it_has_loops(self) -> None:
        e = BY_ID["maze-reuse"]
        for language in LANGUAGES:
            seeds = range(1, 6) if language in ("original", "python") else (1, 2)
            for seed in seeds:
                with self.subTest(language=language, seed=seed):
                    w = self.maze_world(e, seed)
                    code = calling(e.snippets[language],
                                   "mine_gold(3, get_world_size())" if language in ("original", "python")
                                   else "mineGold(3, getWorldSize())",
                                   "mine_gold(5, 4)" if language in ("original", "python")
                                   else "mineGold(5, 4)")
                    h, status = run(w, language, code)
                    self.assertEqual(status, "done", explain(h, status))
                    self.assertEqual(w.items["Gold"], 5 * 16)  # four relocations and the last harvest
                    self.assertEqual(w.items["Weird_Substance"], 500 - 4 * 4)
                    self.assertIsNone(w.maze)

    def test_the_original_language_copes_with_a_deep_search(self) -> None:
        e = BY_ID["maze-reuse"]
        w = self.maze_world(e, 2, size=12, at=(5, 5))
        code = calling(e.snippets["original"], "mine_gold(3, get_world_size())", "mine_gold(2, 12)")
        h, status = run(w, "original", code)
        self.assertEqual(status, "done", explain(h, status))
        self.assertEqual(w.items["Gold"], 2 * 144)

    def test_growing_a_maze_from_a_bush_fills_the_field(self) -> None:
        e = BY_ID["maze-grow"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e)
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertIsNotNone(w.maze)
                self.assertEqual(w.maze.m, 3)
                self.assertEqual(w.items["Weird_Substance"], 500 - 3)
        # At Mazes level 2 each square costs two.
        w = world_for(e, Mazes=2, Expand=3)
        h, status = run(w, "python", e.snippets["python"])
        self.assertEqual(status, "done", explain(h, status))
        self.assertEqual(w.maze.m, 4)
        self.assertEqual(w.items["Weird_Substance"], 500 - 8)


class SpeedTests(unittest.TestCase):
    def test_ticks_counts_the_moves(self) -> None:
        e = BY_ID["speed-ticks"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e)
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                ticks = int(re.search(r"ticks: (\d+)", said(h)[-1]).group(1))
                self.assertGreaterEqual(ticks, 3 * data.ACTION_TICKS)
                self.assertLess(ticks, 4 * data.ACTION_TICKS)

    def test_a_drone_per_column_harvests_every_column(self) -> None:
        e = BY_ID["speed-drones"]
        for language in LANGUAGES:
            for level in (1, 2):
                with self.subTest(language=language, megafarm=level):
                    w = world_for(e, items={}, Megafarm=level)
                    h, status = run(w, language, e.snippets[language])
                    self.assertEqual(status, "done", explain(h, status))
                    self.assertEqual(w.items["Hay"], 9)  # all three columns, helped or alone

    def test_working_beside_a_helper_harvests_two_columns(self) -> None:
        e = BY_ID["speed-wait"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={})
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertEqual(w.items["Hay"], 6)


class TipTests(unittest.TestCase):
    def test_quick_print_is_instant_and_print_takes_a_second(self) -> None:
        e = BY_ID["tip-quick-print"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e)
                before = w.time
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertAlmostEqual(w.time - before, data.FIXED_SECONDS, places=3)
                self.assertEqual(len(said(h)), 2)

    def test_the_unlock_check_reads_the_level(self) -> None:
        e = BY_ID["tip-unlocks"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e)
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertEqual(said(h), ["research Pumpkins first"])
                w = world_for(e, Pumpkins=1)
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(said(h), ["pumpkins are ready"])

    def test_a_flip_takes_one_second_with_no_research_at_all(self) -> None:
        e = BY_ID["tip-flip"]
        for language in LANGUAGES:
            with self.subTest(language=language):
                w = world_for(e, items={})
                before = w.time
                h, status = run(w, language, e.snippets[language])
                self.assertEqual(status, "done", explain(h, status))
                self.assertAlmostEqual(w.time - before, data.FIXED_SECONDS, places=3)


if __name__ == "__main__":
    unittest.main()
