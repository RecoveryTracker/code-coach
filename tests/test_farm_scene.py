"""The Farm's picture: web/src/lib/farmScene.ts (and its farmScene* helpers).

The web project has no JavaScript test runner, so these tests bundle the
TypeScript with the esbuild already in web/node_modules and run it in node
against a stand-in 2D context: a Proxy that writes down every call. They check
what must hold whatever the picture looks like - it never throws, saves and
restores balance, the whole canvas is painted, no NaN reaches a drawing call,
the same input draws the same calls, time animates the drone, growth changes
a plant's size, nothing strays off the canvas, it is fast enough for 22x22 -
and the action animations: each event plays once, replays are refused, the
number playing at once is bounded, and a missing `events` is fine.

(What it LOOKS like is checked by eye; see the notes at the top of
farmScene.ts for the axes and sizes.)
"""

from __future__ import annotations

import functools
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
LIB = WEB / "src" / "lib"
ESBUILD = WEB / "node_modules" / "esbuild" / "bin" / "esbuild"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(
    NODE is None or not ESBUILD.exists(),
    reason="needs node and web/node_modules/esbuild (run npm install in web/)",
)

ENTRY = """\
export { drawScene, resetSceneState } from "%s/farmScene";
export { fxCount, MAX_ANIMS } from "%s/farmSceneFx";
""" % (LIB.as_posix(), LIB.as_posix())

HARNESS = r"""
import { drawScene, resetSceneState, fxCount, MAX_ANIMS } from "./scene.mjs";

const allLogs = [];
let surfaces = 0;

function makeCtx(log, canvas, scale) {
  const props = { canvas };
  return new Proxy({}, {
    get(_, name) {
      if (typeof name === "symbol" || name === "toJSON") return undefined;
      if (name in props) return props[name];
      if (name === "measureText") return (t) => { log.push([name, [t]]); return { width: String(t).length * 7 }; };
      if (name === "getTransform") return () => ({ a: scale, b: 0, c: 0, d: scale });
      if (name === "createLinearGradient" || name === "createRadialGradient") {
        return (...a) => { log.push([name, a]); return { addColorStop: (o, c) => log.push(["addColorStop", [o, c]]) }; };
      }
      if (name === "drawImage") return (img, ...a) => { log.push([name, ["<surface>", ...a]]); };
      return (...a) => { log.push([name, a]); };
    },
    set(_, name, v) { props[name] = v; log.push(["=" + name, [v]]); return true; },
  });
}

globalThis.OffscreenCanvas = class {
  constructor(w, h) {
    this.width = w; this.height = h; this.log = []; surfaces++;
    allLogs.push(this.log);
    this.ctx = makeCtx(this.log, this, 1);
  }
  getContext() { return this.ctx; }
};

let canvas = {};
function freshCanvas() { canvas = {}; }

/** Draw one frame; returns the main context's calls and the calls of any cache surface built meanwhile. */
function run(snap, W, H, time, scale = 1) {
  const before = allLogs.length;
  const log = [];
  const ctx = makeCtx(log, canvas, scale);
  drawScene(ctx, snap, { width: W, height: H, time });
  return { main: log, built: allLogs.slice(before) };
}

function walk(log, f) { for (const [name, args] of log) f(name, args); }

function nanIn(log) {
  let bad = 0;
  walk(log, (name, args) => {
    for (const a of args) {
      if (typeof a === "number" && !Number.isFinite(a)) bad++;
      else if (typeof a === "string" && /NaN|undefined|Infinity/.test(a)) bad++;
    }
  });
  return bad;
}

function balance(log) {
  let depth = 0, ok = true;
  walk(log, (name) => {
    if (name === "save") depth++;
    else if (name === "restore") { depth--; if (depth < 0) ok = false; }
  });
  return ok && depth === 0;
}

function overshoot(log, W, H) {
  let over = 0;
  const chk = (x, y) => { over = Math.max(over, -x, x - W, -y, y - H); };
  walk(log, (name, a) => {
    switch (name) {
      case "moveTo": case "lineTo": chk(a[0], a[1]); break;
      case "quadraticCurveTo": chk(a[0], a[1]); chk(a[2], a[3]); break;
      case "arc": chk(a[0] - a[2], a[1] - a[2]); chk(a[0] + a[2], a[1] + a[2]); break;
      case "ellipse": {
        // a turned ellipse is bounded by a circle of its longer radius
        const rx = a[4] === 0 ? a[2] : Math.max(a[2], a[3]), ry = a[4] === 0 ? a[3] : rx;
        chk(a[0] - rx, a[1] - ry); chk(a[0] + rx, a[1] + ry); break;
      }
      case "rect": case "fillRect": chk(a[0], a[1]); chk(a[0] + a[2], a[1] + a[3]); break;
      case "fillText": case "strokeText": chk(a[1], a[2]); break;
      default: break;
    }
  });
  return over;
}

function covers(log, W, H) {
  let yes = false;
  walk(log, (name, a) => { if (name === "fillRect" && a[0] <= 0 && a[1] <= 0 && a[2] >= W && a[3] >= H) yes = true; });
  return yes;
}

// ---- snapshots ---------------------------------------------------------------------------

const ENTS = ["Grass", "Bush", "Tree", "Carrot", "Pumpkin", "Dead_Pumpkin", "Sunflower", "Cactus", "Apple"];
const HATS = ["Straw_Hat", "Brown_Hat", "Gray_Hat", "Green_Hat", "Purple_Hat", "Traffic_Cone", "Wizard_Hat", "Dinosaur_Hat", "Mystery_Hat"];

function blank(w, h) {
  const tiles = [];
  for (let i = 0; i < w * h; i++) tiles.push({ g: "G" });
  return { w, h, time: 0, drone: { x: 0, y: 0, hat: "Straw_Hat" }, tiles, maze: null, tail: [], smoke: [], speed: 1 };
}

function bigFarm(shift = 0) {
  const w = 22, h = 22, s = blank(w, h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = y * w + x, t = s.tiles[i];
    t.g = (x * 7 + y * 3) % 4 === 0 ? "S" : "G";
    if ((x + y) % 5 !== 0) {
      const e = ENTS[(x + 2 * y) % ENTS.length];
      t.e = e;
      if (e !== "Dead_Pumpkin") t.p = ((i * 13) % 100) / 100;
      if (i % 6 === 0) t.p = 1;
      if (e === "Sunflower") t.n = 3 + (i % 12);
      if (e === "Cactus") { t.n = i % 11; if (t.p === 1) t.s = i % 2; }
    }
    if (i % 4 === 0) t.w = 0.3 + (i % 3) * 0.3;
    if (i % 9 === 0) t.i = 1;
  }
  for (const [x, y] of [[18, 2], [19, 2], [18, 3], [19, 3]]) s.tiles[y * w + x] = { g: "G", e: "Pumpkin", p: 1, giant: [18, 2, 2] };
  const m = 8, sides = [];
  for (let k = 0; k < m * m; k++) sides.push((k * 37 + 11) % 16);
  s.maze = { x0: 2, y0: 2, m, sides, treasure: [5, 5] };
  for (let dy = 0; dy < m; dy++) for (let dx = 0; dx < m; dx++) s.tiles[(2 + dy) * w + 2 + dx] = { g: "G", e: "Hedge" };
  s.tiles[5 * w + 5] = { g: "G", e: "Treasure" };
  s.tail = [[15, 15], [15, 16], [16, 16], [17, 16], [17, 17]];
  for (const [x, y] of s.tail) s.tiles[y * w + x] = { g: "G", e: "Dinosaur" };
  s.drones = HATS.map((hat, k) => ({ x: (14 + k + shift) % 22, y: (14 + 2 * k) % 22, hat }));
  s.drone = { x: 15, y: 14, hat: "Dinosaur_Hat" };
  s.drones[0] = s.drone;
  s.smoke = ["hello", "a very long message that should be cut short, truly, it is long", "Hay: 12"];
  return s;
}

function droneOnly(w = 3, h = 3, x = 1, y = 1) {
  const s = blank(w, h);
  s.drone = { x, y, hat: "Wizard_Hat" };
  return s;
}

function smallFarm(events) {
  const s = blank(4, 4);
  s.tiles[1 * 4 + 1] = { g: "S", e: "Carrot", p: 1 };
  s.drone = { x: 3, y: 3, hat: "Straw_Hat" };
  if (events !== undefined) s.events = events;
  return s;
}

const ev = (n, k, x, y, o = {}) => ({ n, t: 1, k, x, y, d: 0, ok: true, ...o });

// ---- the checks ----------------------------------------------------------------------------

const out = {};
const SIZES = { small: [100, 60], wide: [1600, 400], tall: [400, 1600], normal: [800, 600], big: [1280, 900] };
const scenarios = {
  one: () => { const s = blank(1, 1); s.tiles[0] = { g: "S", e: "Pumpkin", p: 0.7 }; return s; },
  three: () => { const s = blank(3, 3); s.tiles[4] = { g: "G", e: "Tree", p: 1 }; s.smoke = ["hi"]; return s; },
  big: () => bigFarm(),
};

out.errors = {}; out.balanced = {}; out.nan = {}; out.covers = {}; out.over = {};
for (const sc of Object.keys(scenarios)) {
  for (const sz of Object.keys(SIZES)) {
    const key = sc + "@" + sz, [W, H] = SIZES[sz];
    try {
      resetSceneState(); freshCanvas();
      const a = run(scenarios[sc](), W, H, 1.0);
      const moved = scenarios[sc]();
      moved.drone = { x: moved.drone.x + (moved.w > 1 ? 1 : 0), y: moved.drone.y, hat: "Wizard_Hat" };
      if (moved.drones) moved.drones = moved.drones.map((d) => ({ ...d, x: (d.x + 1) % moved.w }));
      const b = run(moved, W, H, 1.05, 2);
      const logs = [a.main, b.main, ...a.built, ...b.built];
      out.errors[key] = null;
      out.balanced[key] = logs.every(balance);
      out.nan[key] = logs.reduce((n, l) => n + nanIn(l), 0);
      out.covers[key] = covers(a.main, W, H) && covers(b.main, W, H);
      out.over[key] = Math.max(...logs.map((l) => overshoot(l, W, H)));
    } catch (e) {
      out.errors[key] = String(e && e.stack || e);
    }
  }
}

// determinism and animation
{
  resetSceneState(); freshCanvas();
  const [W, H] = SIZES.normal;
  run(bigFarm(), W, H, 3.0);
  const a = run(bigFarm(), W, H, 3.0), b = run(bigFarm(), W, H, 3.0);
  out.deterministic = JSON.stringify(a.main) === JSON.stringify(b.main);
  out.cacheBuilt = surfaces;
  out.usedCache = a.main.some(([n]) => n === "drawImage");
  resetSceneState(); freshCanvas();
  run(droneOnly(), W, H, 3.0);
  const d0 = run(droneOnly(), W, H, 3.0), d1 = run(droneOnly(), W, H, 3.0), d2 = run(droneOnly(), W, H, 3.4);
  out.droneDeterministic = JSON.stringify(d0.main) === JSON.stringify(d1.main);
  out.droneAnimates = JSON.stringify(d0.main) !== JSON.stringify(d2.main);
  // a different ground layout rebuilds the cached ground; the same one does not
  const before = surfaces;
  run(droneOnly(), W, H, 3.5);
  const same = surfaces === before;
  const g = droneOnly(); g.tiles[0] = { g: "S" };
  run(g, W, H, 3.5);
  out.cacheKeyed = same && surfaces === before + 1;
}

// growth changes a plant's size
function plantBox(kind, p) {
  resetSceneState(); freshCanvas();
  const s = blank(1, 1);
  s.tiles[0] = { g: "G", e: kind, p, n: 8 };
  s.drone = { x: 6, y: 6, hat: "Straw_Hat" };
  const [W, H] = [600, 500];
  const r = run(s, W, H, 1.0);
  let lo = Infinity, hi = -Infinity, left = Infinity, right = -Infinity;
  const take = (x, y) => {
    if (Math.abs(x - W / 2) > 150) return;
    lo = Math.min(lo, y); hi = Math.max(hi, y); left = Math.min(left, x); right = Math.max(right, x);
  };
  walk(r.main, (name, a) => {
    if (name === "moveTo" || name === "lineTo") take(a[0], a[1]);
    else if (name === "arc") { take(a[0] - a[2], a[1] - a[2]); take(a[0] + a[2], a[1] + a[2]); }
    else if (name === "ellipse") { const q = Math.max(a[2], a[3]); take(a[0] - q, a[1] - q); take(a[0] + q, a[1] + q); }
    else if (name === "rect" || name === "fillRect") { take(a[0], a[1]); take(a[0] + a[2], a[1] + a[3]); }
  });
  return { h: hi - lo, w: right - left };
}
out.growth = {};
for (const kind of ["Grass", "Bush", "Tree", "Carrot", "Pumpkin", "Sunflower", "Cactus"]) {
  out.growth[kind] = [plantBox(kind, 0.3), plantBox(kind, 1.0)];
}

// events
function fresh() { resetSceneState(); freshCanvas(); }
const [EW, EH] = [800, 600];
out.events = {};
{
  fresh();
  run(smallFarm([]), EW, EH, 1.0);
  const harvest = [ev(1, "harvest", 1, 1, { e: "Grass", items: { Hay: 4 } })];
  const first = run(smallFarm(harvest), EW, EH, 2.0).main;
  const countDuring = fxCount();
  const again = run(smallFarm(harvest), EW, EH, 2.0).main;
  const countAgain = fxCount();
  const later = run(smallFarm(harvest), EW, EH, 2.1).main;
  const after = run(smallFarm(harvest), EW, EH, 3.5).main;
  fresh();
  run(smallFarm([]), EW, EH, 1.0);
  const none = run(smallFarm([]), EW, EH, 2.0).main;
  const noneLater = run(smallFarm([]), EW, EH, 3.5).main;
  out.events.during = first.length;
  out.events.without = none.length;
  out.events.again = again.length;
  out.events.laterLen = later.length;
  out.events.countDuring = countDuring;
  out.events.countAgain = countAgain;
  out.events.afterSame = JSON.stringify(after) === JSON.stringify(noneLater);
  out.events.afterLen = after.length;
  out.events.afterNoneLen = noneLater.length;
}
{
  // the drone does a quick action pose for the drone that acted, and only for ~0.25 s
  fresh();
  const base = droneOnly(); base.events = [];
  run(base, EW, EH, 1.0);
  const e1 = [ev(1, "water", 0, 0)];
  const s1 = droneOnly(); s1.events = e1;
  const dip = run(s1, EW, EH, 2.0).main;
  const dip2 = run(s1, EW, EH, 2.1).main;
  fresh();
  const s0 = droneOnly(); s0.events = [];
  run(s0, EW, EH, 1.0);
  const plain = run(s0, EW, EH, 2.0).main;
  const plain2 = run(s0, EW, EH, 2.1).main;
  // compare only the drone's own calls: the ones that do not belong to an effect are the same count
  out.events.dipDiffers = JSON.stringify(dip) !== JSON.stringify(plain) && JSON.stringify(dip2) !== JSON.stringify(plain2);
}
{
  // replay protection
  fresh();
  run(smallFarm([ev(1, "till", 0, 0), ev(2, "till", 0, 1), ev(3, "till", 0, 2)]), EW, EH, 1.0);
  out.events.firstSightNoReplay = fxCount();
  run(smallFarm([ev(10, "till", 0, 0)]), EW, EH, 2.0);
  out.events.newOne = fxCount();
  run(smallFarm([ev(1, "till", 0, 0), ev(2, "till", 1, 0)]), EW, EH, 2.1);
  out.events.afterReset = fxCount();
  run(smallFarm([ev(1, "till", 0, 0), ev(2, "till", 1, 0), ev(3, "till", 2, 0)]), EW, EH, 2.2);
  out.events.afterResetNew = fxCount();
  // a farm of another size is a new stream too
  const big = blank(5, 5); big.events = [ev(50, "till", 0, 0)];
  run(big, EW, EH, 2.3);
  out.events.otherFarm = fxCount();
  // the clock running backwards drops what was playing
  fresh();
  run(smallFarm([]), EW, EH, 5.0);
  run(smallFarm([ev(1, "plant", 1, 1, { e: "Bush" })]), EW, EH, 6.0);
  out.events.beforeBackwards = fxCount();
  run(smallFarm([ev(1, "plant", 1, 1, { e: "Bush" })]), EW, EH, 0.5);
  out.events.afterBackwards = fxCount();
}
{
  // sixty at once
  fresh();
  run(smallFarm([]), EW, EH, 1.0);
  const evs = [];
  for (let k = 1; k <= 60; k++) evs.push(ev(k, "harvest", k % 4, (k >> 2) % 4, { e: "Grass", items: { Hay: 1 } }));
  const r = run(smallFarm(evs), EW, EH, 2.0);
  out.events.sixtyCount = fxCount();
  out.events.maxAnims = MAX_ANIMS;
  const labels = r.main.filter(([n, a]) => n === "fillText" && String(a[0]).startsWith("+")).map(([, a]) => a[0]);
  out.events.sixtyLabels = labels;
  out.events.sixtyNan = nanIn(r.main);
  // ...and a steady stream of them across many snapshots stays bounded too
  fresh();
  run(smallFarm([]), EW, EH, 1.0);
  let seq = 0, peak = 0;
  for (let k = 0; k < 10; k++) {
    const batch = [];
    for (let j = 0; j < 5; j++) { seq++; batch.push(ev(seq, "water", seq % 4, 0)); }
    run(smallFarm(batch), EW, EH, 2.0 + k * 0.02);
    peak = Math.max(peak, fxCount());
  }
  out.events.streamPeak = peak;
  // every kind, odd positions, odd drone indexes and odd items: no NaN, no throw
  fresh();
  run(smallFarm([]), EW, EH, 1.0);
  const kinds = ["harvest", "plant", "till", "water", "fertilize", "swap", "hat", "unlock"];
  const wild = [];
  let n = 0;
  for (const k of kinds) for (const ok of [true, false]) {
    wild.push(ev(++n, k, 1, 1, { ok, e: "Pumpkin", items: { Hay: 3, Wood: 0, Carrot: -2, Weird_Substance: 7 } }));
    wild.push(ev(++n, k, 99, -5, { ok, d: 77 }));
    wild.push(ev(++n, k, 2, 2, { ok, e: "Nonsense", d: -3 }));
  }
  let bad = 0, thrown = null, balancedAll = true;
  try {
    for (const t of [2.0, 2.05, 2.2, 2.6, 3.1, 4.0]) {
      const r2 = run(smallFarm(t === 2.0 ? wild : wild), EW, EH, t);
      bad += nanIn(r2.main);
      balancedAll = balancedAll && balance(r2.main);
    }
  } catch (e) { thrown = String(e && e.stack || e); }
  out.events.wildNan = bad;
  out.events.wildThrown = thrown;
  out.events.wildBalanced = balancedAll;
  out.events.wildBounded = fxCount();
  // events missing altogether
  fresh();
  let missing = null;
  try { run(smallFarm(undefined), EW, EH, 1.0); run(smallFarm(undefined), EW, EH, 1.1); } catch (e) { missing = String(e); }
  out.events.missingThrown = missing;
  out.events.missingCount = fxCount();
}

// speed: 22x22, 30 frames, against a context that remembers nothing
{
  freshCanvas();
  resetSceneState();
  const noop = () => {};
  const mk = () => new Proxy({}, {
    get(_, name) {
      if (name === "measureText") return () => ({ width: 40 });
      if (name === "getTransform") return () => ({ a: 1, b: 0, c: 0, d: 1 });
      if (name === "canvas") return canvas;
      if (name === "createLinearGradient" || name === "createRadialGradient") return () => ({ addColorStop: noop });
      return noop;
    },
    set() { return true; },
  });
  const fast = class { constructor() { this.ctx = mk(); } getContext() { return this.ctx; } };
  globalThis.OffscreenCanvas = fast;
  const ctx = mk();
  const s = bigFarm();
  drawScene(ctx, s, { width: 1100, height: 700, time: 0 });
  const t0 = performance.now();
  for (let k = 0; k < 30; k++) drawScene(ctx, s, { width: 1100, height: 700, time: k / 30 });
  out.perfMs = performance.now() - t0;
}

console.log(JSON.stringify(out));
"""


@functools.cache
def results() -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="farm_scene_test_"))
    try:
        (tmp / "entry.ts").write_text(ENTRY, encoding="utf-8")
        (tmp / "harness.mjs").write_text(HARNESS, encoding="utf-8")
        built = subprocess.run(
            [NODE, str(ESBUILD), str(tmp / "entry.ts"), "--bundle", "--format=esm", "--platform=node",
             f"--outfile={tmp / 'scene.mjs'}", "--log-level=error"],
            capture_output=True, text=True, timeout=120,
        )
        assert built.returncode == 0, built.stderr
        ran = subprocess.run([NODE, str(tmp / "harness.mjs")], capture_output=True, text=True, timeout=300, cwd=tmp)
        assert ran.returncode == 0, ran.stderr[-3000:]
        return json.loads(ran.stdout.strip().splitlines()[-1])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class TestSceneBasics(unittest.TestCase):
    def test_draws_every_farm_and_canvas_without_throwing(self):
        errs = {k: v for k, v in results()["errors"].items() if v}
        assert not errs, errs
        # 3 farms (1x1, 3x3, 22x22 with everything) x 5 canvas shapes
        assert len(results()["errors"]) == 15

    def test_save_and_restore_balance(self):
        bad = [k for k, ok in results()["balanced"].items() if not ok]
        assert not bad, bad

    def test_paints_the_whole_canvas(self):
        bad = [k for k, ok in results()["covers"].items() if not ok]
        assert not bad, bad

    def test_no_nan_or_infinity_reaches_a_drawing_call(self):
        bad = {k: v for k, v in results()["nan"].items() if v}
        assert not bad, bad

    def test_stays_on_the_canvas(self):
        # Slab, plants, drones, hats and puffs are fitted inside the canvas; 4 px of slack for
        # strokes. (A 100x60 canvas is too small for a 22x22 farm or a speech bubble to fit: only
        # "does not throw" is asked of it.)
        bad = {k: v for k, v in results()["over"].items() if v > 4 and not k.endswith("@small")}
        assert not bad, bad

    def test_same_input_draws_the_same_calls(self):
        r = results()
        assert r["deterministic"], "two draws of one snapshot at one time differ"
        assert r["droneDeterministic"]

    def test_time_animates_the_drone(self):
        assert results()["droneAnimates"]

    def test_ground_is_cached_and_keyed_by_the_ground_layout(self):
        r = results()
        assert r["usedCache"], "the ground is drawn from an offscreen canvas"
        assert r["cacheKeyed"], "same ground: no rebuild; a changed tile: exactly one rebuild"

    def test_growth_changes_every_plants_size(self):
        for kind, (young, ripe) in results()["growth"].items():
            assert ripe["h"] > young["h"] * 1.1, (kind, young, ripe)
            assert ripe["w"] > young["w"], (kind, young, ripe)

    def test_fast_enough_for_22x22(self):
        # 30 frames of 484 tiles, with a stand-in that does nothing: far under a second normally.
        assert results()["perfMs"] < 8000, results()["perfMs"]


class TestActionAnimations(unittest.TestCase):
    def test_an_event_adds_drawing_while_it_plays_and_nothing_after(self):
        e = results()["events"]
        assert e["during"] > e["without"], e
        assert e["afterSame"], (e["afterLen"], e["afterNoneLen"])

    def test_each_event_plays_once(self):
        e = results()["events"]
        assert e["countDuring"] == 1
        assert e["countAgain"] == 1, "the same snapshot drawn again must not start it again"
        assert e["again"] == e["during"]

    def test_the_drone_that_acted_does_a_quick_action_pose(self):
        assert results()["events"]["dipDiffers"]

    def test_old_events_and_other_streams_are_not_replayed(self):
        e = results()["events"]
        assert e["firstSightNoReplay"] == 0, "the first snapshot with events is only a baseline"
        assert e["newOne"] == 1
        assert e["afterReset"] == 0, "n going down drops everything and replays nothing"
        assert e["afterResetNew"] == 1, "only the event newer than the new stream's baseline plays"
        assert e["otherFarm"] == 0, "a farm of another size starts a new stream"
        assert e["beforeBackwards"] == 1
        assert e["afterBackwards"] == 0, "a clock that runs backwards drops what was playing"

    def test_sixty_events_at_once_play_a_bounded_number_and_merge_labels(self):
        e = results()["events"]
        assert e["sixtyCount"] == e["maxAnims"] == 12
        assert e["sixtyLabels"] == ["+60 Hay"], e["sixtyLabels"]
        assert e["sixtyNan"] == 0
        assert e["streamPeak"] == 12, "newer animations replace the oldest when 12 are playing"

    def test_every_kind_with_odd_inputs_never_breaks(self):
        e = results()["events"]
        assert e["wildThrown"] is None, e["wildThrown"]
        assert e["wildNan"] == 0
        assert e["wildBalanced"]
        assert e["wildBounded"] <= e["maxAnims"]

    def test_missing_events_are_fine(self):
        e = results()["events"]
        assert e["missingThrown"] is None
        assert e["missingCount"] == 0
