"""Farm: the floating-window layout (web/src/components/FarmMode.tsx and farm/).

The web project has no JS test runner, so this checks what Python can see: the
invariants the layout relies on, read from the source text, and the event helpers
(`farm/farmEvents.ts`), which are pure, bundled with the esbuild that ships with
Vite and run in node (skipped when either is missing). Expected values are worked
out by hand from the rules in the file, never taken from its output.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "web"
SRC = WEB / "src"
FARM = SRC / "components" / "farm"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def window_ids() -> list[str]:
    source = text(FARM / "useFarmWindows.ts")
    body = re.search(r"WINDOW_IDS\s*=\s*\[(.*?)\]\s*as const", source, re.S)
    assert body, "WINDOW_IDS not found"
    return re.findall(r'"(\w+)"', body.group(1))


class TestWindows(unittest.TestCase):
    def test_every_menu_window_has_a_definition_and_content(self):
        ids = window_ids()
        self.assertGreaterEqual(len(ids), 5)
        defs = text(FARM / "windowDefs.tsx")
        mode = text(SRC / "components" / "FarmMode.tsx")
        for wid in ids:
            self.assertRegex(defs, rf"\b{wid}:\s*\{{\s*title:", f"{wid} has no definition")
            self.assertIn(f'case "{wid}":', mode, f"{wid} has no content")
        # ...and the menu is built from the same list, so it cannot name a window that is not there.
        menu = text(FARM / "FarmMenu.tsx")
        self.assertIn("WINDOW_IDS.map", menu)
        self.assertIn("WINDOW_DEFS[id]", menu)

    def test_storage_key_is_unique_and_namespaced(self):
        key = re.search(r'LAYOUT_KEY\s*=\s*"([^"]+)"', text(FARM / "useFarmWindows.ts"))
        assert key
        self.assertTrue(key.group(1).startswith("code-coach:farm-"))
        for path in SRC.rglob("*"):
            if path.suffix in (".ts", ".tsx") and path.name != "useFarmWindows.ts":
                self.assertNotIn(key.group(1), text(path), f"{path.name} reuses the key")

    def test_storage_is_always_guarded(self):
        for path in FARM.glob("*.ts*"):
            source = text(path)
            if "localStorage" in source:
                self.assertIn("try {", source, path.name)
                self.assertIn("catch", source, path.name)

    def test_windows_are_buttons_with_labels(self):
        win = text(FARM / "FarmWindow.tsx")
        self.assertIn("aria-label={`${minimised ? \"Restore\" : \"Minimise\"} ${title}`}", win)
        self.assertIn("aria-label={`Close ${title}`}", win)
        self.assertIn('e.key !== "Escape"', win)
        menu = text(FARM / "FarmMenu.tsx")
        self.assertIn("aria-pressed", menu)
        self.assertIn("aria-label", menu)


class TestScene(unittest.TestCase):
    def test_scene_uses_the_contract_and_cleans_up(self):
        scene = text(FARM / "FarmScene.tsx")
        self.assertIn('import { drawScene } from "../../lib/farmScene"', scene)
        self.assertIn("requestAnimationFrame", scene)
        self.assertIn("cancelAnimationFrame", scene)
        self.assertIn("document.hidden", scene)
        self.assertIn("devicePixelRatio", scene)
        self.assertIn("setTransform(dpr", scene)
        self.assertIn("ResizeObserver", scene)
        self.assertIn("watcher.disconnect()", scene)
        # The loop draws from refs: it must not be able to re-render the screen.
        self.assertNotIn("useState", scene)

    def test_farm_mode_no_longer_draws_the_flat_farm(self):
        mode = text(SRC / "components" / "FarmMode.tsx")
        self.assertNotIn("drawFarm", mode)
        self.assertIn("<FarmScene", mode)


class TestStyles(unittest.TestCase):
    def test_every_rule_is_scoped_to_the_farm(self):
        css = re.sub(r"/\*.*?\*/", "", text(SRC / "styles" / "farm.css"), flags=re.S)
        bad = []
        for prelude in re.findall(r"([^{}]+)\{", css):
            prelude = prelude.strip()
            if prelude.startswith("@") or re.fullmatch(r"[\d.%,\s]+|from|to", prelude):
                continue  # @media / @keyframes and their steps
            for selector in prelude.split(","):
                if not re.search(r"\.(fm|farm)-", selector):
                    bad.append(selector.strip())
        self.assertEqual(bad, [], "rules that could leak into other screens")

    def test_no_class_the_css_defines_outside_its_prefix(self):
        css = re.sub(r"/\*.*?\*/", "", text(SRC / "styles" / "farm.css"), flags=re.S)
        defined = set(re.findall(r"\.([A-Za-z_][\w-]*)", css))
        # .iae-pane is the editor's own class, styled only as a child of .fm-editor.
        stray = {c for c in defined if not c.startswith(("fm-", "farm-"))}
        self.assertEqual(stray - {"iae-pane", "panning", "on", "ok", "lit", "short", "failed",
                                  "primary", "stop", "danger", "tab", "bump", "sim", "min",
                                  "focused", "dragging", "narrow", "locked", "missing", "ready",
                                  "done", "open", "close", "running", "error", "info", "print"},
                         set())


def bundle(entry: Path, out: Path) -> bool:
    node = shutil.which("node")
    esbuild = WEB / "node_modules" / "esbuild" / "lib" / "main.js"
    if not node or not esbuild.exists():
        return False
    script = (
        "const e=require(process.argv[1]);"
        "e.buildSync({entryPoints:[process.argv[2]],bundle:true,platform:'node',"
        "format:'cjs',outfile:process.argv[3],logLevel:'error'});"
    )
    got = subprocess.run(
        [node, "-e", script, str(esbuild), str(entry), str(out)],
        capture_output=True, text=True, timeout=60,
    )
    return got.returncode == 0 and out.exists()


DRIVER = r"""
const m = require(process.argv[2]);
const ev = (n, k, o = {}) => ({ n, t: 10, k, x: 0, y: 0, d: 0, ok: true, ...o });
const out = {};
out.first = m.diffEvents([ev(5, "plant"), ev(6, "harvest")], null);
out.again = m.diffEvents([ev(5, "plant"), ev(6, "harvest"), ev(7, "till")], 6);
out.restart = m.diffEvents([ev(2, "plant")], 40);
out.empty = m.diffEvents([], null);
out.lines = [
  m.eventLine(ev(1, "harvest", { x: 3, y: 2, items: { Hay: 4 } })),
  m.eventLine(ev(2, "harvest", { x: 1, y: 1, ok: false })),
  m.eventLine(ev(3, "plant", { x: 1, y: 1, e: "Carrot" })),
  m.eventLine(ev(4, "plant", { x: 0, y: 0, e: "Bush", ok: false })),
  m.eventLine(ev(5, "harvest", { x: 0, y: 0, items: { Weird_Substance: 1500, Hay: 0 } })),
];
out.bumps = m.bumpsFor([
  ev(1, "harvest", { items: { Hay: 4, Wood: 2 } }),
  ev(2, "harvest", { items: { Hay: 1 } }),
  ev(3, "harvest", { ok: false, items: { Hay: 99 } }),
  ev(4, "plant", { items: { Hay: 50 } }),
]);
const snap = (time, events) => ({ time, events });
out.doing = [
  m.droneDoing(snap(10.5, [ev(1, "harvest", { e: "Hay" })]), true),
  m.droneDoing(snap(10.5, [ev(1, "harvest", { ok: false })]), true),
  m.droneDoing(snap(12, [ev(1, "plant", { e: "Carrot" })]), true),
  m.droneDoing(snap(12, [ev(1, "plant", { e: "Carrot" })]), false),
  m.droneDoing(snap(10.5, [ev(1, "water", { d: 1 })]), false),
  m.droneDoing(snap(10.5, [ev(1, "till"), ev(2, "water")]), true),
  m.droneDoing(undefined, false),
];
console.log(JSON.stringify(out));
"""


class TestEventHelpers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="farm_layout_"))
        cls.ok = bundle(FARM / "farmEvents.ts", cls.tmp / "events.cjs")
        cls.result = None
        if cls.ok:
            (cls.tmp / "driver.cjs").write_text(DRIVER, encoding="utf-8")
            got = subprocess.run(
                [shutil.which("node"), str(cls.tmp / "driver.cjs"),
                 str(cls.tmp / "events.cjs")],
                capture_output=True, text=True, timeout=60,
            )
            assert got.returncode == 0, got.stderr
            cls.result = json.loads(got.stdout)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        if not self.ok:
            self.skipTest("node or esbuild is not available")

    def test_first_load_replays_nothing_and_later_events_play_once(self):
        r = self.result
        self.assertEqual(r["first"], {"fresh": [], "seen": 6})
        self.assertEqual([e["n"] for e in r["again"]["fresh"]], [7])
        self.assertEqual(r["again"]["seen"], 7)
        self.assertEqual(r["empty"], {"fresh": [], "seen": 0})

    def test_a_farm_that_started_over_is_not_waited_on(self):
        self.assertEqual(self.result["restart"], {"fresh": [], "seen": 2})

    def test_log_lines(self):
        self.assertEqual(
            self.result["lines"],
            [
                "Harvested Hay +4 at (3,2)",
                "Nothing ripe at (1,1)",
                "Planted Carrot (1,1)",
                "Could not plant Bush (0,0)",
                "Harvested Weird Substance +1,500 at (0,0)",
            ],
        )

    def test_only_ok_harvests_bump_counters(self):
        self.assertEqual(self.result["bumps"], {"Hay": 5, "Wood": 2})

    def test_what_the_drone_is_doing(self):
        self.assertEqual(
            self.result["doing"],
            [
                "Harvesting Hay",
                "Harvest: nothing ripe",
                "Moving",  # the plant is two seconds old: only "running" is left
                "",  # ...and the program is not running
                "",  # a water by drone 1 is not drone 0's
                "Watering",  # the latest event (highest n) wins
                "",
            ],
        )


if __name__ == "__main__":
    unittest.main()
