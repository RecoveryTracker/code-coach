"""Farm: a program in several files (Import), end to end.

The game lets a program span several code windows that import each other;
here each language keeps a set of named files, Run runs the open one, and
the others are imported with the language's own syntax. These tests hold
the files to that: what may be called what, an old single-file save
carried over, the gate checking every file and naming it, and real runs
in all three languages where the entry imports a helper and an error in
the helper is reported with the helper's name and line.
"""

from __future__ import annotations

import json
import shutil
import time
import unittest

from code_coach.engine import dart_path
from code_coach.farm import data
from code_coach.farm.runner import STARTER_CODE, FarmHost, save_path

HAS_NODE = shutil.which("node") is not None
HAS_DART = dart_path() is not None

LEVELS = dict(Loops=1, Speed=1, Expand=2, Plant=1, Senses=1, Operators=1, Variables=1,
              Functions=1, Import=1, Debug=1)


def host(**levels: int) -> FarmHost:
    h = FarmHost()
    h.warp = 0
    world = h._load()
    for name, level in (levels or LEVELS).items():
        world.unlocks[name] = level
    world.width, world.height = data.FARM_SIZES[2]
    world._fill()
    world.advance(5)
    return h


def finish(h: FarmHost, timeout: float = 90.0) -> str:
    deadline = time.monotonic() + timeout
    while h.run and h.run.status in ("starting", "running"):
        if time.monotonic() > deadline:
            h.stop_run(wait=True)
            raise AssertionError("the program did not finish")
        time.sleep(0.02)
    return h.run.status


class FileTests(unittest.TestCase):
    def test_a_new_farm_has_one_main_file_per_language(self) -> None:
        h = FarmHost()
        h._load()
        for lang in ("python", "javascript", "dart"):
            self.assertEqual(h.files[lang], {"main": STARTER_CODE[lang]})
            self.assertEqual(h.entry[lang], "main")

    def test_files_can_be_added_renamed_selected_and_deleted(self) -> None:
        h = FarmHost()
        h._load()
        self.assertTrue(h.file_op("python", "add", "utils")["ok"])
        self.assertIn("import utils", h.files["python"]["utils"])
        self.assertTrue(h.file_op("python", "select", "utils")["ok"])
        self.assertEqual(h.entry["python"], "utils")
        self.assertTrue(h.file_op("python", "rename", "utils", "helpers")["ok"])
        self.assertEqual(h.entry["python"], "helpers")
        self.assertEqual(list(h.files["python"]), ["main", "helpers"])
        self.assertTrue(h.file_op("python", "delete", "helpers")["ok"])
        self.assertEqual(h.entry["python"], "main")

    def test_names_must_be_module_names_and_not_the_farms_own(self) -> None:
        h = FarmHost()
        h._load()
        for bad in ("Utils", "2fast", "my-file", "farm_api", "runner", "package", "", "x" * 30):
            with self.subTest(name=bad):
                got = h.file_op("python", "add", bad)
                self.assertFalse(got["ok"])
                self.assertTrue(got["error"])
        self.assertFalse(h.file_op("python", "add", "main")["ok"])  # already there

    def test_the_last_file_cannot_go(self) -> None:
        h = FarmHost()
        h._load()
        self.assertFalse(h.file_op("dart", "delete", "main")["ok"])

    def test_an_old_single_file_save_becomes_main(self) -> None:
        path = save_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"world": {}, "code": {"python": "harvest()\nharvest()\n"}}),
                        encoding="utf-8")
        h = FarmHost()
        h._load()
        self.assertEqual(h.files["python"], {"main": "harvest()\nharvest()\n"})
        self.assertEqual(h.code["python"], "harvest()\nharvest()\n")

    def test_files_survive_saving(self) -> None:
        h = FarmHost()
        h._load()
        h.file_op("javascript", "add", "utils")
        h.keep_code("javascript", "export const N = 3;\n", "utils")
        again = FarmHost()
        again._load()
        self.assertEqual(again.files["javascript"]["utils"], "export const N = 3;\n")

    def test_every_file_is_checked_and_the_problem_file_named(self) -> None:
        h = host(Loops=1)
        h.file_op("python", "add", "helper")
        h.keep_code("python", "def f():\n    harvest()\n", "helper")
        got = h.start("python", "harvest()\n", "main")
        self.assertFalse(got["ok"])
        files = {v["file"] for v in got["violations"]}
        self.assertEqual(files, {"helper"})
        self.assertIn("functions", {v["feature"] for v in got["violations"]})

    def test_import_needs_its_unlock(self) -> None:
        levels = dict(LEVELS)
        levels["Import"] = 0
        h = host(**levels)
        h.file_op("python", "add", "helper")
        got = h.start("python", "import helper\n", "main")
        self.assertFalse(got["ok"])
        self.assertEqual(got["violations"][0]["feature"], "import")


class PythonImportRunTests(unittest.TestCase):
    def test_the_entry_imports_a_helper_that_drives_the_drone(self) -> None:
        h = host()
        h.file_op("python", "add", "rows")
        h.keep_code("python", (
            "def column():\n"
            "    for i in range(get_world_size()):\n"
            "        harvest()\n"
            "        move(North)\n"
        ), "rows")
        started = h.start("python", "from rows import column\nimport rows\ncolumn()\nmove(East)\nrows.column()\n", "main")
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h), "done", h.run.error)
        self.assertEqual(h._load().items["Hay"], 6)

    def test_an_error_in_a_helper_names_the_helper_and_its_line(self) -> None:
        h = host()
        h.file_op("python", "add", "rows")
        h.keep_code("python", "def broken():\n    harvest()\n    till()\n", "rows")
        h.start("python", "import rows\nrows.broken()\n", "main")
        self.assertEqual(finish(h), "error")
        self.assertEqual((h.run.error_file, h.run.error_line), ("rows", 3))
        self.assertIn("Carrots", h.run.error)
        self.assertTrue(any("rows, line 3" in line["text"] for line in h.output))

    def test_run_runs_the_open_file(self) -> None:
        h = host()
        h.file_op("python", "add", "other")
        h.start("python", "quick_print('main ran')\n", "main")
        finish(h)
        h.start("python", "quick_print('other ran')\n", "other")
        finish(h)
        self.assertEqual(h.entry["python"], "other")
        texts = [line["text"] for line in h.output if line["kind"] == "out"]
        self.assertEqual(texts, ["main ran", "other ran"])


@unittest.skipUnless(HAS_NODE, "needs node")
class JavaScriptImportRunTests(unittest.TestCase):
    def test_es_modules_import_each_other(self) -> None:
        h = host()
        h.file_op("javascript", "add", "rows")
        h.keep_code("javascript", (
            "export function column() {\n"
            "  for (const i of range(getWorldSize())) {\n"
            "    harvest();\n"
            "    move(North);\n"
            "  }\n"
            "}\n"
        ), "rows")
        started = h.start("javascript", (
            'import { column } from "./rows.js";\n'
            'import * as rows from "./rows.js";\n'
            "column();\n"
            "move(East);\n"
            "rows.column();\n"
        ), "main")
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h), "done", h.run.error)
        self.assertEqual(h._load().items["Hay"], 6)

    def test_an_error_in_a_module_names_it(self) -> None:
        h = host()
        h.file_op("javascript", "add", "rows")
        h.keep_code("javascript", "export function broken() {\n  harvest();\n  till();\n}\n", "rows")
        h.start("javascript", 'import { broken } from "./rows.js";\nbroken();\n', "main")
        self.assertEqual(finish(h), "error")
        self.assertEqual((h.run.error_file, h.run.error_line), ("rows", 3))


@unittest.skipUnless(HAS_DART, "needs dart")
class DartImportRunTests(unittest.TestCase):
    def test_dart_files_import_each_other(self) -> None:
        h = host()
        h.file_op("dart", "add", "rows")
        h.keep_code("dart", (
            "void column() {\n"
            "  for (final i in range(getWorldSize())) {\n"
            "    harvest();\n"
            "    move(north);\n"
            "  }\n"
            "}\n"
        ), "rows")
        started = h.start("dart", (
            "import 'rows.dart';\n"
            "\n"
            "void main() {\n"
            "  column();\n"
            "  move(east);\n"
            "  column();\n"
            "}\n"
        ), "main")
        self.assertTrue(started["ok"], started)
        self.assertEqual(finish(h, 180), "done", h.run.error)
        self.assertEqual(h._load().items["Hay"], 6)

    def test_a_compile_error_in_a_dart_helper_names_it(self) -> None:
        h = host()
        h.file_op("dart", "add", "rows")
        h.keep_code("dart", "void column() {\n  harvest()\n}\n", "rows")
        h.start("dart", "import 'rows.dart';\n\nvoid main() {\n  column();\n}\n", "main")
        self.assertEqual(finish(h, 180), "error")
        self.assertEqual((h.run.error_file, h.run.error_line), ("rows", 2))


if __name__ == "__main__":
    unittest.main()
