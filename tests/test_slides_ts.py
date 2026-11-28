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
  half: dur(plain, 0.5), one: dur(plain, 1),
  oddSpeed: dur(plain, 7), delay: [0.5, 0.75, 1, 1.5, 2].map(S.outputDelayMs),
};

out.speed = {
  parse: ["0.5", "0.75", "1", "1.5", "2", "3", "", "abc", null, undefined].map((v) => S.parseSpeed(v)),
  labels: S.SPEEDS.map(S.speedLabel),
};

out.keys = {
  right: k("ArrowRight"), left: k("ArrowLeft"), space: k(" "), p: k("p"), other: k("a"), enter: k("Enter"),
  explain: [k("e"), k("E"), k("e", { tag: "INPUT" }), k("e", { ctrl: true })],
  inInput: [k("ArrowRight", { tag: "INPUT" }), k(" ", { tag: "TEXTAREA" }), k("ArrowLeft", { tag: "SELECT" })],
  editable: k("ArrowRight", { editable: true }),
  ctrl: k("ArrowRight", { ctrl: true }), alt: k("ArrowLeft", { alt: true }), meta: k(" ", { meta: true }),
  onButton: [k(" ", { tag: "BUTTON" }), k("ArrowRight", { tag: "BUTTON" })],
};

const order = ["a", "b", "c", "d"];
const rng = (v) => () => v;
const o = (over = {}) => ({ loop: false, shuffle: false, seen: [], rng: rng(0), ...over });
out.deck = {
  inOrder: [S.nextDeckId(order, "a", o()), S.nextDeckId(order, "c", o())],
  endNoLoop: S.nextDeckId(order, "d", o()),
  endLoop: S.nextDeckId(order, "d", o({ loop: true })),
  unknownCurrent: [S.nextDeckId(order, "zzz", o()), S.nextDeckId(order, "zzz", o({ loop: true }))],
  empty: S.nextDeckId([], "a", o({ loop: true })),
  singleLoop: S.nextDeckId(["a"], "a", o({ loop: true })),
  // shuffle: unseen decks only (the current one counts as seen); rng picks within the pool in order
  shuffleFirst: S.nextDeckId(order, "a", o({ shuffle: true, rng: rng(0) })),
  shuffleLast: S.nextDeckId(order, "a", o({ shuffle: true, rng: rng(0.999) })),
  shuffleSkipsSeen: S.nextDeckId(order, "a", o({ shuffle: true, seen: ["b", "c"], rng: rng(0.5) })),
  shuffleDone: S.nextDeckId(order, "a", o({ shuffle: true, seen: ["a", "b", "c", "d"] })),
  shuffleLoop: S.nextDeckId(order, "a", o({ shuffle: true, loop: true, seen: ["a", "b", "c", "d"], rng: rng(0) })),
  shuffleBadRng: S.nextDeckId(order, "a", o({ shuffle: true, rng: rng(NaN) })),
  shuffleSeq: (() => {  // a whole shuffled session with a seeded generator never repeats before the end
    let x = 12345; const r = () => { x = (x * 1103515245 + 12345) % 2147483648; return x / 2147483648; };
    const seen = []; let cur = "a"; seen.push(cur);
    for (let g = 0; g < 10; g++) { const n = S.nextDeckId(order, cur, o({ shuffle: true, seen, rng: r })); if (n === null) break; seen.push(n); cur = n; }
    return seen;
  })(),
  label: [S.deckPositionLabel(order, "d"), S.deckPositionLabel(order, "zzz")],
  up: [S.upNextLabel(true, true, "Types"), S.upNextLabel(false, true, "Types"), S.upNextLabel(true, false, "Types"), S.upNextLabel(true, true, null)],
};

out.resume = {
  good: S.parseResume(S.serializeResume({ deckId: "b", index: 4 }), order),
  missing: [S.parseResume(null, order), S.parseResume(undefined, order), S.parseResume("", order)],
  junk: ["not json", "[]", "null", "42", '{"deckId":5}', '{"index":2}'].map((v) => S.parseResume(v, order)),
  goneDeck: S.parseResume('{"deckId":"old","index":2}', order),
  badIndex: ["-3", '"x"', "null", "2.9"].map((v) => S.parseResume(`{"deckId":"c","index":${v}}`, order)),
  label: S.resumeLabel("Types", 4),
  flags: [S.parseFlag("1", false), S.parseFlag("0", true), S.parseFlag(null, true), S.parseFlag("yes", false), S.parseFlag("", true)],
};

// Several presses in the same tick: each one is applied to the latest index, like a functional state update.
out.presses = (() => {
  let i = 0; const log = [];
  for (const a of ["next", "next", "next", "prev", "next"]) { i = S.pressTarget(a, i, 5); log.push(i); }
  let j = 3; for (let n = 0; n < 6; n++) j = S.pressTarget("next", j, 5);
  return { log, clamped: j };
})();

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
    assert t["delay"] == [2000, 1333, 1000, 667, 500]
    assert t["half"] == 2 * t["one"]  # 0.5x is twice as slow as 1x


def test_speed_reads_back_only_known_values():
    s = results()["speed"]
    assert s["parse"] == [0.5, 0.75, 1, 1.5, 2, 1, 1, 1, 1, 1]
    assert s["labels"] == ["0.5x", "0.75x", "1x", "1.5x", "2x"]


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


def test_next_deck_in_order_loop_and_stop():
    d = results()["deck"]
    assert d["inOrder"] == ["b", "d"]
    assert d["endNoLoop"] is None  # the last deck without Loop ends the run
    assert d["endLoop"] == "a"  # Loop goes round to the first
    assert d["unknownCurrent"] == [None, "a"]
    assert d["empty"] is None and d["singleLoop"] is None


def test_next_deck_shuffle_picks_unseen_with_the_given_rng():
    d = results()["deck"]
    assert d["shuffleFirst"] == "b" and d["shuffleLast"] == "d"
    assert d["shuffleSkipsSeen"] == "d"  # only "d" is unseen
    assert d["shuffleDone"] is None  # everything seen, no Loop
    assert d["shuffleLoop"] == "b"  # Loop starts a new round, never straight back to the same deck
    assert d["shuffleBadRng"] == "b"
    seq = d["shuffleSeq"]
    assert sorted(seq) == ["a", "b", "c", "d"] and seq[0] == "a"  # every deck exactly once


def test_deck_labels():
    d = results()["deck"]
    assert d["label"] == ["deck 4 of 4", None]
    assert d["up"] == ["Next deck: Types", None, None, None]


def test_resume_parsing():
    r = results()["resume"]
    assert r["good"] == {"deckId": "b", "index": 4}
    assert r["missing"] == [None, None, None]
    assert r["junk"] == [None] * 6
    assert r["goneDeck"] is None  # a deck that no longer exists falls back to the picker
    assert r["badIndex"] == [{"deckId": "c", "index": 0}, {"deckId": "c", "index": 0},
                             {"deckId": "c", "index": 0}, {"deckId": "c", "index": 2}]
    assert r["label"] == "Picked up at Types, slide 5"
    assert r["flags"] == [True, False, True, False, True]


def test_several_presses_each_move_one_slide():
    p = results()["presses"]
    assert p["log"] == [1, 2, 3, 2, 3]
    assert p["clamped"] == 4


def test_e_opens_explain_this_code_but_not_while_typing_or_with_a_modifier():
    assert results()["keys"]["explain"] == ["explain", "explain", "none", "none"]


def test_the_python_reader_explains_slide_examples():
    """"Explain this code" sends a slide's example to /api/explain: the Python reader must read every one without an
    error and give each a row (a sample of every deck: its first and last slide with code)."""
    from code_coach.api import server
    from code_coach.api.schemas import ExplainRequest
    from code_coach import slides

    checked = 0
    for d in slides.decks_for("python"):
        with_code = [s for s in d.slides if s.code]
        for s in (with_code[:1] + with_code[-1:]):
            r = server.explain(ExplainRequest(code=s.code, language="python"))
            assert r.ok, (d.id, s.title, r.summary)
            assert r.lines, (d.id, s.title)
            checked += 1
    assert checked >= 40
