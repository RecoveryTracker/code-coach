"""Farm: one save per language.

Original, Python, JavaScript and Dart each have their own farm - field,
items, research, clock - their own code files and open tab, and their own time
warp. Progress in one never touches another; switching language switches save.
A save from before this (one farm_save.json with everything in it) is split up
on first load, and what it held is kept.
"""

from __future__ import annotations

import json
import shutil
import time
import unittest
from pathlib import Path

from code_coach.api.schemas import FarmCodeRequest, FarmFileRequest, FarmUnlockRequest, FarmWarpRequest
from code_coach.api.server import (
    farm_code,
    farm_file,
    farm_overview,
    farm_reset,
    farm_state,
    farm_unlock,
    farm_warp,
)
from code_coach.engine import dart_path
from code_coach.farm import data
from code_coach.farm.runner import (
    BACKUP_SUFFIX,
    HOST,
    LANGUAGES,
    STARTER_CODE,
    FarmHost,
    Run,
    language_save_path,
    save_path,
)
from code_coach.farm.world import World

HAS_NODE = shutil.which("node") is not None
HAS_DART = dart_path() is not None

RIPE = dict(Loops=1, Speed=1, Expand=2, Plant=1, Senses=1, Operators=1, Variables=1, Functions=1)


def host() -> FarmHost:
    """A fresh host on the test's own store, unpaced."""
    h = FarmHost()
    h._load()
    for lang in LANGUAGES:
        h.warps[lang] = 0
    return h


def ripe(h: FarmHost, language: str, **levels: int) -> World:
    """Give one language's farm research and a field whose grass is ready - and only that one."""
    world = h._world_for(language)
    for name, level in levels.items():
        world.unlocks[name] = level
    world.width, world.height = data.FARM_SIZES[world.level("Expand")]
    world._fill()
    world.advance(5)
    return world


def finish(h: FarmHost, timeout: float = 60.0) -> str:
    deadline = time.monotonic() + timeout
    while h.run and h.run.status in ("starting", "running"):
        if time.monotonic() > deadline:
            h.stop_run(wait=True)
            raise AssertionError("the program did not finish")
        time.sleep(0.02)
    assert h.run is not None
    return h.run.status


def go(h: FarmHost, language: str) -> None:
    assert h.file_op(language, "select", h.entry[language])["ok"]


class SeparateFarmsTests(unittest.TestCase):
    def test_research_bought_in_one_language_is_not_in_another(self) -> None:
        h = host()
        go(h, "python")
        h._load().items["Hay"] = 5
        self.assertTrue(h.buy("Loops"))
        self.assertEqual(h._load().level("Loops"), 1)
        go(h, "javascript")
        self.assertEqual(h._load().level("Loops"), 0)
        self.assertEqual(h._load().items["Hay"], 0)
        self.assertNotIn("while", h._load().unlocked_features())
        go(h, "python")
        self.assertEqual(h._load().level("Loops"), 1)
        self.assertEqual(h._load().items["Hay"], 0)  # the five hay were spent
        # And the Original farm never had it either.
        self.assertEqual(h._world_for("original").level("Loops"), 0)

    def test_every_language_has_a_world_of_its_own(self) -> None:
        h = host()
        worlds = {lang: h._world_for(lang) for lang in LANGUAGES}
        self.assertEqual(len({id(w) for w in worlds.values()}), len(LANGUAGES))
        for lang in LANGUAGES:
            go(h, lang)
            self.assertIs(h._load(), worlds[lang])

    def test_a_bigger_field_is_that_languages_only(self) -> None:
        h = host()
        ripe(h, "python", Expand=2)
        self.assertGreater(h._world_for("python").w, 1)
        for lang in ("original", "javascript", "dart"):
            self.assertEqual((h._world_for(lang).w, h._world_for(lang).h), data.FARM_SIZES[0])

    def test_harvest_in_python_leaves_original_alone(self) -> None:
        h = host()
        ripe(h, "python", Loops=1)
        ripe(h, "original", Loops=1)
        before = json.dumps(h._world_for("original").to_json())
        started = h.start("python", "harvest()\n")
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h), "done")
        self.assertEqual(h.language, "python")
        self.assertEqual(h._load().items["Hay"], 1)
        self.assertEqual(json.dumps(h._world_for("original").to_json()), before)

    @unittest.skipUnless(HAS_DART, "needs dart")
    def test_items_harvested_in_dart_do_not_change_original(self) -> None:
        h = host()
        ripe(h, "dart")
        before = json.dumps(h._world_for("original").to_json())
        started = h.start("dart", "void main() {\n  harvest();\n}\n")
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h), "done", h.run.error)
        self.assertEqual(h._load().items["Hay"], 1)
        go(h, "original")
        self.assertEqual(h._load().items["Hay"], 0)
        self.assertEqual(json.dumps(h._world_for("original").to_json()), before)

    @unittest.skipUnless(HAS_NODE, "needs node")
    def test_a_run_in_one_language_never_touches_another_languages_world(self) -> None:
        h = host()
        ripe(h, "python")
        ripe(h, "javascript")
        python_before = json.dumps(h._world_for("python").to_json())
        self.assertTrue(h.start("javascript", "harvest();\nharvest();\n")["ok"])
        self.assertEqual(finish(h), "done")
        self.assertEqual(h._world_for("javascript").items["Hay"], 2)
        self.assertEqual(json.dumps(h._world_for("python").to_json()), python_before)
        js_after = json.dumps(h._world_for("javascript").to_json())
        self.assertTrue(h.start("python", "harvest()\n")["ok"])
        self.assertEqual(finish(h), "done")
        self.assertEqual(h._world_for("python").items["Hay"], 1)
        self.assertEqual(json.dumps(h._world_for("javascript").to_json()), js_after)

    def test_starting_a_program_goes_to_its_languages_farm(self) -> None:
        h = host()
        ripe(h, "python")
        self.assertEqual(h.language, "original")
        self.assertTrue(h.start("python", "harvest()\n")["ok"])
        self.assertEqual(h.language, "python")
        finish(h)
        self.assertEqual(h.run.language, "python")
        self.assertEqual(h._world_for("original").items["Hay"], 0)

    def test_code_entry_and_warp_are_each_languages_own(self) -> None:
        h = host()
        h.file_op("python", "add", "rows")
        h.keep_code("python", "harvest()\n# python\n", "rows")
        h.file_op("python", "select", "rows")
        h.set_warp(8)
        h.keep_code("javascript", "harvest(); // js\n")
        h.set_warp(4)
        self.assertEqual(h.language, "javascript")
        self.assertEqual(h.warps["javascript"], 4)
        self.assertEqual(h.warps["python"], 8)
        self.assertEqual(h.warps["original"], 0)  # host() ran Original unpaced
        self.assertEqual(h.entry["python"], "rows")
        self.assertEqual(h.entry["javascript"], "main")
        self.assertEqual(list(h.files["python"]), ["main", "rows"])
        self.assertEqual(list(h.files["javascript"]), ["main"])
        self.assertEqual(h.files["original"], {"main": STARTER_CODE["original"]})
        go(h, "python")
        self.assertEqual(h.warp, 8)
        go(h, "javascript")
        self.assertEqual(h.warp, 4)
        self.assertEqual(h.state()["warp"], 4)

    def test_set_warp_changes_only_the_current_language(self) -> None:
        h = host()
        go(h, "dart")
        h.set_warp(16)
        self.assertEqual({lang: h.warps[lang] for lang in LANGUAGES},
                         {"original": 0, "python": 0, "javascript": 0, "dart": 16})

    def test_a_run_takes_its_languages_warp(self) -> None:
        h = host()
        ripe(h, "python")
        h.warps["python"] = 64
        h.warps["original"] = 0
        self.assertTrue(h.start("python", "harvest()\n")["ok"])
        self.assertEqual(h.run.warp, 64)
        finish(h)

    def test_reset_clears_only_the_current_languages_farm(self) -> None:
        h = host()
        h._world_for("python").items["Hay"] = 20
        h._world_for("javascript").items["Hay"] = 30
        h._world_for("javascript").unlocks["Loops"] = 1
        go(h, "python")
        h.keep_code("python", "harvest()\n# mine\n")
        h.reset()
        self.assertEqual(h._load().items["Hay"], 0)
        self.assertEqual(h.language, "python")
        self.assertEqual(h.files["python"]["main"], "harvest()\n# mine\n")  # the code stays
        go(h, "javascript")
        self.assertEqual(h._load().items["Hay"], 30)
        self.assertEqual(h._load().level("Loops"), 1)
        # And it is the saved farms that say so, not just this host.
        again = FarmHost()
        again._load()
        self.assertEqual(again._world_for("python").items["Hay"], 0)
        self.assertEqual(again._world_for("javascript").items["Hay"], 30)

    def test_the_overview_and_state_describe_the_current_languages_farm(self) -> None:
        h = host()
        ripe(h, "python", **RIPE)
        h._world_for("python").items["Hay"] = 7
        h._world_for("dart").items["Hay"] = 3
        go(h, "python")
        o = h.overview()
        self.assertEqual(o["language"], "python")
        self.assertEqual(o["items"]["Hay"], 7)
        self.assertGreater(o["farm"]["w"], 1)
        self.assertIn("while", o["features"])
        self.assertEqual(next(u for u in o["unlocks"] if u["name"] == "Loops")["level"], 1)
        go(h, "dart")
        o = h.overview()
        self.assertEqual(o["language"], "dart")
        self.assertEqual(o["items"]["Hay"], 3)
        self.assertEqual(o["farm"]["w"], 1)
        self.assertNotIn("while", o["features"])
        self.assertEqual(next(u for u in o["unlocks"] if u["name"] == "Loops")["level"], 0)
        # Every language's code comes along either way: the screen shows the tabs of them all.
        self.assertEqual(set(o["files"]), set(LANGUAGES))

    def test_levels_are_every_languages_research(self) -> None:
        h = host()
        ripe(h, "python", Loops=1, Plant=1)
        ripe(h, "javascript", Loops=2)
        go(h, "original")
        levels = h.overview()["levels"]
        self.assertEqual(set(levels), set(LANGUAGES))
        self.assertEqual((levels["python"]["Loops"], levels["python"]["Plant"]), (1, 1))
        self.assertEqual((levels["javascript"]["Loops"], levels["javascript"]["Plant"]), (2, 0))
        self.assertEqual(levels["original"]["Loops"], 0)
        self.assertEqual(levels["dart"]["Loops"], 0)
        names = {u["name"] for u in h.overview()["unlocks"]}
        for lang in LANGUAGES:
            self.assertEqual(set(levels[lang]), names)
        # The current language's own list agrees with its entry.
        mine = {u["name"]: u["level"] for u in h.overview()["unlocks"]}
        self.assertEqual(mine, levels["original"])

    def test_the_saves_summary_has_a_line_per_language(self) -> None:
        h = host()
        ripe(h, "python", Expand=2)
        h._world_for("python").items["Hay"] = 12
        saves = h.overview()["saves"]
        self.assertEqual(set(saves), set(LANGUAGES))
        self.assertEqual(saves["python"]["items"]["Hay"], 12)
        self.assertEqual(saves["python"]["w"], h._world_for("python").w)
        self.assertEqual(saves["dart"]["w"], 1)

    def test_a_program_running_on_one_farm_keeps_you_there(self) -> None:
        h = host()
        h.run = Run(id=1, language="python", warp=0, status="running")
        h.language = "python"
        refused = h.file_op("javascript", "select", "main")
        self.assertFalse(refused["ok"])
        self.assertIn("Stop", refused["error"])
        self.assertFalse(h.keep_code("javascript", "harvest();\n"))
        self.assertEqual(h.language, "python")
        self.assertEqual(h.files["javascript"]["main"], STARTER_CODE["javascript"])
        # The same language's files are fine to touch, as before.
        self.assertTrue(h.file_op("python", "add", "more")["ok"])
        self.assertTrue(h.keep_code("python", "harvest()\n"))
        h.run.status = "done"
        self.assertTrue(h.file_op("javascript", "select", "main")["ok"])
        self.assertEqual(h.language, "javascript")

    def test_state_shows_a_run_only_on_the_farm_it_ran_on(self) -> None:
        h = host()
        go(h, "python")
        h.run = Run(id=3, language="python", warp=0, status="done")
        self.assertEqual(h.state()["run"]["id"], 3)
        go(h, "javascript")
        self.assertIsNone(h.state()["run"])
        go(h, "python")
        self.assertEqual(h.state()["run"]["id"], 3)

    def test_switching_starts_the_output_afresh(self) -> None:
        h = host()
        go(h, "python")
        h._say("info", "hello")
        self.assertEqual(h.state()["outputEnd"], 1)
        go(h, "dart")
        self.assertEqual(h.state()["outputEnd"], 0)
        self.assertEqual(h.overview()["outputEnd"], 0)


class SavedFarmsTests(unittest.TestCase):
    def test_each_language_gets_its_own_save_file_and_none_is_left_half_written(self) -> None:
        h = host()
        for lang in LANGUAGES:
            go(h, lang)
        folder = save_path().parent
        for lang in LANGUAGES:
            path = language_save_path(lang)
            self.assertEqual(path.name, f"farm_save_{lang}.json")
            self.assertEqual(path.parent, folder)
            raw = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(set(raw), {"world", "files", "entry", "warp"})
            self.assertEqual(set(raw["files"]), {"main"})  # only this language's files
            self.assertEqual(raw["files"]["main"], STARTER_CODE[lang])
            self.assertEqual(raw["entry"], "main")
        self.assertEqual(list(folder.glob("farm_save*.tmp")), [])
        pointer = json.loads(save_path().read_text(encoding="utf-8"))
        self.assertEqual(pointer["language"], "dart")
        self.assertNotIn("world", pointer)

    def test_a_save_holds_only_its_own_language(self) -> None:
        h = host()
        h.keep_code("python", "harvest()\n# python only\n")
        h.keep_code("dart", "// dart only\nvoid main() {}\n")
        python = json.loads(language_save_path("python").read_text(encoding="utf-8"))
        self.assertEqual(python["files"], {"main": "harvest()\n# python only\n"})
        dart = json.loads(language_save_path("dart").read_text(encoding="utf-8"))
        self.assertEqual(dart["files"], {"main": "// dart only\nvoid main() {}\n"})

    def test_switching_language_and_restarting_restores_each_save(self) -> None:
        h = host()
        ripe(h, "python", Loops=1, Expand=2)
        h._world_for("python").items["Hay"] = 11
        h._world_for("javascript").items["Hay"] = 22
        h._world_for("original").items["Hay"] = 33
        h.file_op("python", "add", "rows")
        h.keep_code("python", "harvest()\n# rows\n", "rows")
        h.file_op("python", "select", "rows")
        h.set_warp(8)
        go(h, "javascript")
        h.keep_code("javascript", "harvest(); // js\n")
        h.set_warp(2)
        go(h, "original")
        go(h, "javascript")  # the language you leave on is the one you come back to
        for lang in ("python", "javascript", "original"):
            h.save(lang)

        again = FarmHost()
        self.assertEqual(again._load().items["Hay"], 22)
        self.assertEqual(again.language, "javascript")
        self.assertEqual(again.warp, 2)
        self.assertEqual(again.code["javascript"], "harvest(); // js\n")
        self.assertEqual(again._world_for("python").items["Hay"], 11)
        self.assertEqual(again._world_for("python").level("Loops"), 1)
        self.assertGreater(again._world_for("python").w, 1)
        self.assertEqual(again._world_for("original").items["Hay"], 33)
        self.assertEqual(again.warps["python"], 8)
        self.assertEqual(again.entry["python"], "rows")
        self.assertEqual(again.files["python"]["rows"], "harvest()\n# rows\n")
        self.assertEqual(again._world_for("dart").items["Hay"], 0)
        self.assertEqual(again._world_for("javascript").level("Loops"), 0)

    def test_the_current_language_survives_a_restart_for_each_language(self) -> None:
        for lang in LANGUAGES:
            with self.subTest(language=lang):
                h = host()
                go(h, lang)
                self.assertEqual(FarmHost().overview()["language"], lang)

    def test_worlds_are_built_when_first_looked_at(self) -> None:
        h = host()
        ripe(h, "dart")
        go(h, "dart")
        again = FarmHost()
        again._load()
        self.assertEqual(set(again.worlds), {"dart"})
        again.overview()  # the Playbook's levels look at every language
        self.assertEqual(set(again.worlds), set(LANGUAGES))

    def test_leaving_a_farm_keeps_where_it_got_to(self) -> None:
        h = host()
        go(h, "python")
        h._load().items["Hay"] = 4  # not saved by anything but leaving
        go(h, "javascript")
        again = FarmHost()
        again._load()
        self.assertEqual(again._world_for("python").items["Hay"], 4)

    def test_a_damaged_language_save_is_only_that_farm_starting_over(self) -> None:
        h = host()
        h._world_for("javascript").items["Hay"] = 9
        h._world_for("dart").items["Hay"] = 8
        go(h, "javascript")
        go(h, "dart")
        language_save_path("javascript").write_text("{not json", encoding="utf-8")
        again = FarmHost()
        again._load()
        self.assertEqual(again.language, "dart")
        self.assertEqual(again._world_for("dart").items["Hay"], 8)
        self.assertEqual(again._world_for("javascript").items["Hay"], 0)
        self.assertEqual(again.files["javascript"], {"main": STARTER_CODE["javascript"]})


def write_old_save(language: str | None = "python", warp: float = 4, hay: int = 7) -> tuple[Path, dict]:
    """A save the way the app wrote it before separate farms: one file, everything in it."""
    world = World()
    world.items["Hay"] = hay
    world.time = 12.5
    old = {
        "world": world.to_json(),
        "files": {
            "original": {"main": "harvest()\n# original\n"},
            "python": {"main": "harvest()\n# python main\n", "rows": "def f():\n    harvest()\n"},
            "javascript": {"main": "harvest(); // javascript\n"},
            "dart": {"main": "// dart\nvoid main() {}\n"},
        },
        "entry": {"original": "main", "python": "rows", "javascript": "main", "dart": "main"},
        "warp": warp,
    }
    if language is not None:
        old["language"] = language
    path = save_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(old), encoding="utf-8")
    return path, old


class MigrationTests(unittest.TestCase):
    def test_the_test_store_is_not_the_real_one(self) -> None:
        self.assertNotEqual(save_path().parent, Path.home() / ".code_coach")

    def test_the_old_farm_becomes_the_save_of_the_language_it_says(self) -> None:
        path, old = write_old_save("python")
        h = FarmHost()
        world = h._load()
        self.assertEqual(h.language, "python")
        self.assertEqual(world.items["Hay"], 7)
        self.assertEqual(world.time, 12.5)
        self.assertEqual(h.warp, 4)
        for lang in ("original", "javascript", "dart"):
            self.assertEqual(h._world_for(lang).items["Hay"], 0, lang)
            self.assertEqual(h._world_for(lang).time, 0, lang)
            self.assertEqual(h.warps[lang], 1, lang)
        # Everyone's code is kept, and so is everyone's open tab.
        self.assertEqual(h.files, old["files"])
        self.assertEqual(h.entry, old["entry"])
        self.assertEqual(h.code["python"], "def f():\n    harvest()\n")

    def test_the_old_file_is_kept_as_a_backup_and_the_new_layout_is_used(self) -> None:
        path, _old = write_old_save("python")
        original_bytes = path.read_bytes()
        FarmHost()._load()
        backup = path.with_name("farm_save.json" + BACKUP_SUFFIX)
        self.assertEqual(backup.name, "farm_save.json.before-per-language")
        self.assertEqual(backup.read_bytes(), original_bytes)
        pointer = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(pointer["language"], "python")
        self.assertNotIn("world", pointer)
        for lang in LANGUAGES:
            self.assertTrue(language_save_path(lang).exists(), lang)
        python = json.loads(language_save_path("python").read_text(encoding="utf-8"))
        self.assertEqual(python["world"]["items"]["Hay"], 7)
        self.assertEqual(python["warp"], 4)
        self.assertEqual(set(python["files"]), {"main", "rows"})
        javascript = json.loads(language_save_path("javascript").read_text(encoding="utf-8"))
        self.assertNotIn("world", javascript)
        self.assertEqual(javascript["files"], {"main": "harvest(); // javascript\n"})

    def test_migrating_twice_changes_nothing(self) -> None:
        path, _old = write_old_save("python")
        original_bytes = path.read_bytes()
        first = FarmHost()
        first._load()
        first.overview()
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        snapshot = {p.name: p.read_bytes() for p in path.parent.glob("farm_save*") if p.suffix != ".tmp"}
        second = FarmHost()
        self.assertEqual(second._load().items["Hay"], 7)
        self.assertEqual(second.language, "python")
        self.assertEqual({p.name: p.read_bytes() for p in path.parent.glob("farm_save*")}, snapshot)
        self.assertEqual(backup.read_bytes(), original_bytes)
        self.assertEqual(list(path.parent.glob("*.before-per-language*")), [backup])

    def test_playing_after_the_migration_keeps_going_in_the_new_layout(self) -> None:
        path, _old = write_old_save("python")
        original_bytes = path.read_bytes()
        h = FarmHost()
        h._load().items["Hay"] = 99
        go(h, "javascript")
        h._load().items["Hay"] = 5
        h.save()
        again = FarmHost()
        self.assertEqual(again._load().items["Hay"], 5)
        self.assertEqual(again.language, "javascript")
        self.assertEqual(again._world_for("python").items["Hay"], 99)
        self.assertEqual(path.with_name(path.name + BACKUP_SUFFIX).read_bytes(), original_bytes)

    def test_the_language_can_be_any_of_the_four(self) -> None:
        for lang in LANGUAGES:
            with self.subTest(language=lang):
                folder = save_path().parent
                for stale in folder.glob("farm_save*"):
                    stale.unlink()
                write_old_save(lang, warp=2, hay=3)
                h = FarmHost()
                self.assertEqual(h._load().items["Hay"], 3)
                self.assertEqual(h.language, lang)
                self.assertEqual(h.warp, 2)
                for other in LANGUAGES:
                    if other != lang:
                        self.assertEqual(h._world_for(other).items["Hay"], 0)

    def test_an_old_save_without_a_language_is_originals(self) -> None:
        write_old_save(None)
        h = FarmHost()
        self.assertEqual(h._load().items["Hay"], 7)
        self.assertEqual(h.language, "original")

    def test_the_users_shape_of_save_only_grass_and_one_square(self) -> None:
        # The farm of someone who has done nothing but harvest grass on the first square.
        path, old = write_old_save("python", warp=1, hay=2)
        world = World().to_json()
        world["items"]["Hay"] = 2
        old["world"] = world
        path.write_text(json.dumps(old), encoding="utf-8")
        h = FarmHost()
        got = h._load()
        self.assertEqual((got.w, got.h), (1, 1))
        self.assertEqual(got.items["Hay"], 2)
        self.assertEqual(got.level("Loops"), 0)
        self.assertEqual(h.overview()["levels"]["python"]["Loops"], 0)

    def test_a_save_from_before_files_is_split_too(self) -> None:
        path = save_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"world": {}, "language": "javascript",
                                    "code": {"javascript": "harvest();\nharvest();\n"}}), encoding="utf-8")
        h = FarmHost()
        h._load()
        self.assertEqual(h.language, "javascript")
        self.assertEqual(h.files["javascript"], {"main": "harvest();\nharvest();\n"})
        self.assertEqual(h.files["python"], {"main": STARTER_CODE["python"]})

    def test_a_backup_already_there_is_never_overwritten(self) -> None:
        path, _old = write_old_save("python")
        backup = path.with_name(path.name + BACKUP_SUFFIX)
        backup.write_text("an earlier backup", encoding="utf-8")
        FarmHost()._load()
        self.assertEqual(backup.read_text(encoding="utf-8"), "an earlier backup")
        extra = path.with_name(path.name + BACKUP_SUFFIX + ".2")
        self.assertTrue(extra.exists())
        self.assertIn('"python"', extra.read_text(encoding="utf-8"))

    def test_a_fresh_store_is_not_a_migration(self) -> None:
        h = FarmHost()
        h._load()
        self.assertEqual(h.language, "original")
        self.assertEqual(list(save_path().parent.glob("farm_save*")), [])


class RouteTests(unittest.TestCase):
    """The routes the screen calls: choosing a file in a language takes you to its farm."""

    def setUp(self) -> None:
        saved = dict(HOST.warps)
        self.addCleanup(lambda: HOST.warps.update(saved))
        HOST._load()  # this test's own store: loading it starts the farms afresh

    def test_selecting_a_file_in_another_language_switches_the_farm(self) -> None:
        HOST._load().items["Hay"] = 9
        o = farm_file(FarmFileRequest(language="python", action="select", name="main"))
        self.assertTrue(o["ok"])
        self.assertEqual(o["language"], "python")
        self.assertEqual(o["items"]["Hay"], 0)
        self.assertEqual(farm_state()["items"]["Hay"], 0)
        back = farm_file(FarmFileRequest(language="original", action="select", name="main"))
        self.assertEqual(back["language"], "original")
        self.assertEqual(back["items"]["Hay"], 9)
        self.assertEqual(farm_state()["items"]["Hay"], 9)

    def test_research_bought_through_the_routes_stays_in_its_language(self) -> None:
        farm_file(FarmFileRequest(language="python", action="select", name="main"))
        HOST._load().items["Hay"] = 5
        bought = farm_unlock(FarmUnlockRequest(name="Loops"))
        self.assertTrue(bought["ok"])
        self.assertIn("while", bought["features"])
        self.assertEqual(bought["levels"]["python"]["Loops"], 1)
        self.assertEqual(bought["levels"]["original"]["Loops"], 0)
        other = farm_file(FarmFileRequest(language="javascript", action="select", name="main"))
        self.assertNotIn("while", other["features"])
        self.assertEqual(next(u for u in other["unlocks"] if u["name"] == "Loops")["level"], 0)
        # ...but the overview still knows python's level, for the Playbook.
        self.assertEqual(other["levels"]["python"]["Loops"], 1)
        self.assertEqual(farm_overview()["levels"]["javascript"]["Loops"], 0)

    def test_keeping_code_in_a_language_takes_you_to_its_farm(self) -> None:
        HOST._world_for("dart").items["Hay"] = 6
        got = farm_code(FarmCodeRequest(language="dart", code="// mine\nvoid main() {}\n"))
        self.assertTrue(got["ok"])
        o = farm_overview()
        self.assertEqual(o["language"], "dart")
        self.assertEqual(o["items"]["Hay"], 6)
        self.assertEqual(o["code"]["dart"], "// mine\nvoid main() {}\n")
        self.assertFalse(farm_code(FarmCodeRequest(language="dart", code="x", file="nope"))["ok"])

    def test_the_warp_is_the_current_languages(self) -> None:
        farm_file(FarmFileRequest(language="python", action="select", name="main"))
        farm_warp(FarmWarpRequest(warp=8))
        self.assertEqual(farm_state()["warp"], 8)
        o = farm_file(FarmFileRequest(language="javascript", action="select", name="main"))
        self.assertEqual(o["warp"], 1)
        farm_warp(FarmWarpRequest(warp=64))
        o = farm_file(FarmFileRequest(language="python", action="select", name="main"))
        self.assertEqual(o["warp"], 8)

    def test_reset_through_the_route_starts_over_only_the_current_farm(self) -> None:
        HOST._world_for("original").items["Hay"] = 4
        HOST._world_for("python").items["Hay"] = 5
        farm_file(FarmFileRequest(language="python", action="select", name="main"))
        o = farm_reset()
        self.assertEqual(o["language"], "python")
        self.assertEqual(o["items"]["Hay"], 0)
        self.assertEqual(o["saves"]["original"]["items"]["Hay"], 4)
        back = farm_file(FarmFileRequest(language="original", action="select", name="main"))
        self.assertEqual(back["items"]["Hay"], 4)

    def test_the_file_answer_for_a_missing_file_does_not_switch(self) -> None:
        got = farm_file(FarmFileRequest(language="python", action="select", name="nope"))
        self.assertFalse(got["ok"])
        self.assertEqual(got["language"], "original")


if __name__ == "__main__":
    unittest.main()
