"""Slides: the pure rules in web/src/lib/slides.ts (moving, autoplay timing, keys, saved speed).

The web project has no JavaScript test runner, so (like tests/test_brain_round.py) this bundles the
library with the esbuild already in web/node_modules and runs it in node. The expected values are
worked out here by hand, not read from the library.
"""

from __future__ import annotations

import functools
import json
import shutil
import subprocess
import tempfile
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

HARNESS = r"""
import * as S from "./slides.mjs";

const out = {};
const none = { tag: "BODY", editable: false, ctrl: false, alt: false, meta: false };
const k = (key, over = {}) => S.keyAction(key, { ...none, ...over });

out.move = {
  clampLow: S.clampIndex(-3, 5), clampHigh: S.clampIndex(99, 5), clampNaN: S.clampIndex(NaN, 5),
  clampEmpty: S.clampIndex(2, 0),
  next: S.nextIndex(1, 5), nextAtEnd: S.nextIndex(4, 5), prev: S.prevIndex(3, 5), prevAtStart: S.prevIndex(0, 5),
  last: [S.isLast(3, 5), S.isLast(4, 5)],
  autoMid: S.autoStep(1, 5), autoEnd: S.autoStep(4, 5), autoEmpty: S.autoStep(0, 0), autoSingle: S.autoStep(0, 1),
  label: S.progressLabel(2, 14), labelClamped: S.progressLabel(40, 14),
};

const plain = { text: "one two three", code: "", output: "", point: "" };
const dur = (s, speed = 1) => S.slideDurationMs(s, speed);
out.time = {
  words: S.countWords("  a b   c\nd "), noWords: S.countWords("   "),
  lines: [S.countLines(""), S.countLines("a"), S.countLines("a\nb\n"), S.countLines("a\nb\nc")],
  plain1: dur(plain),
  moreWords: dur({ ...plain, text: "one two three four five six" }),
  pointWords: dur({ ...plain, point: "and a point" }),
  oneLine: dur({ ...plain, code: "x = 1", output: "" }),
  threeLines: dur({ ...plain, code: "a\nb\nc", output: "" }),
  withOutput: dur({ ...plain, code: "x", output: "1" }),
  withoutOutput: dur({ ...plain, code: "x", output: "" }),
  speeds: [0.75, 1, 1.5, 2].map((s) => dur({ ...plain, code: "a\nb", output: "1" }, s)),
  oddSpeed: dur(plain, 7), delay: [0.75, 1, 1.5, 2].map(S.outputDelayMs),
};

out.speed = {
  parse: ["0.75", "1", "1.5", "2", "3", "", "abc", null, undefined].map((v) => S.parseSpeed(v)),
  labels: S.SPEEDS.map(S.speedLabel),
};

out.keys = {
  right: k("ArrowRight"), left: k("ArrowLeft"), space: k(" "), p: k("p"), other: k("a"), enter: k("Enter"),
  inInput: [k("ArrowRight", { tag: "INPUT" }), k(" ", { tag: "TEXTAREA" }), k("ArrowLeft", { tag: "SELECT" })],
  editable: k("ArrowRight", { editable: true }),
  ctrl: k("ArrowRight", { ctrl: true }), alt: k("ArrowLeft", { alt: true }), meta: k(" ", { meta: true }),
  onButton: [k(" ", { tag: "BUTTON" }), k("ArrowRight", { tag: "BUTTON" })],
};

console.log(JSON.stringify(out));
"""


@functools.cache
def results() -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="slides_ts_test_"))
    try:
        (tmp / "harness.mjs").write_text(HARNESS, encoding="utf-8")
        built = subprocess.run(
            [NODE, str(ESBUILD), str(LIB / "slides.ts"), "--bundle", "--format=esm", "--platform=node",
             f"--outfile={tmp / 'slides.mjs'}", "--log-level=error"],
            capture_output=True, text=True, timeout=120,
        )
        assert built.returncode == 0, built.stderr
        ran = subprocess.run([NODE, str(tmp / "harness.mjs")], capture_output=True, text=True, timeout=120, cwd=tmp)
        assert ran.returncode == 0, ran.stderr[-3000:]
        return json.loads(ran.stdout.strip().splitlines()[-1])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_moving_clamps_and_autoplay_stops_at_the_end():
    m = results()["move"]
    assert (m["clampLow"], m["clampHigh"], m["clampNaN"], m["clampEmpty"]) == (0, 4, 0, 0)
    assert (m["next"], m["nextAtEnd"], m["prev"], m["prevAtStart"]) == (2, 4, 2, 0)
    assert m["last"] == [False, True]
    assert (m["autoMid"], m["autoEnd"], m["autoEmpty"], m["autoSingle"]) == (2, None, None, None)
    assert m["label"] == "slide 3 of 14"
    assert m["labelClamped"] == "slide 14 of 14"


def test_counting_words_and_lines():
    t = results()["time"]
    assert t["words"] == 4 and t["noWords"] == 0
    assert t["lines"] == [0, 1, 2, 3]


def test_duration_grows_with_words_and_code_lines():
    t = results()["time"]
    assert t["moreWords"] > t["plain1"]
    assert t["pointWords"] > t["plain1"]
    assert t["oneLine"] > t["plain1"]
    assert t["threeLines"] > t["oneLine"]
    assert t["withOutput"] > t["withoutOutput"]
    # Per-unit steps are constant: three more words cost three times one word, two more lines twice one line.
    word = (t["moreWords"] - t["plain1"]) / 3
    assert word > 0 and (t["pointWords"] - t["plain1"]) == pytest.approx(3 * word, abs=1)
    line = t["oneLine"] - t["plain1"]
    assert (t["threeLines"] - t["oneLine"]) == pytest.approx(2 * line, abs=1)


def test_speed_scales_the_duration_and_the_output_delay():
    t = results()["time"]
    slow, normal, fast, fastest = t["speeds"]
    assert slow > normal > fast > fastest
    assert normal / fastest == pytest.approx(2, abs=0.01)
    assert normal / fast == pytest.approx(1.5, abs=0.01)
    assert slow / normal == pytest.approx(1 / 0.75, abs=0.01)
    assert t["oddSpeed"] == t["plain1"]  # an unknown speed counts as 1x
    assert t["delay"] == [1333, 1000, 667, 500]


def test_speed_reads_back_only_known_values():
    s = results()["speed"]
    assert s["parse"] == [0.75, 1, 1.5, 2, 1, 1, 1, 1, 1]
    assert s["labels"] == ["0.75x", "1x", "1.5x", "2x"]


def test_keys():
    k = results()["keys"]
    assert (k["right"], k["left"], k["space"], k["p"]) == ("next", "prev", "next", "toggle")
    assert k["other"] == "none" and k["enter"] == "none"


def test_keys_ignored_while_typing_or_with_modifiers():
    k = results()["keys"]
    assert k["inInput"] == ["none", "none", "none"]
    assert k["editable"] == "none"
    assert (k["ctrl"], k["alt"], k["meta"]) == ("none", "none", "none")
    # A focused button keeps its own Space; the arrows still move.
    assert k["onButton"] == ["none", "next"]
