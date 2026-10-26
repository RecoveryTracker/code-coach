"""Brain Drills: a round in progress survives leaving the tab.

web/src/lib/brainResume.ts is pure TypeScript (a snapshot of the round, its clock, the rules for when it is too old or
no longer fits the activity, and a little storage with a module-level copy plus sessionStorage). Like
tests/test_brain_round.py this bundles it with the esbuild already in web/node_modules and runs it in node, handing it
a fake Storage (and ones that throw) in place of the browser's.

The rules under test: a snapshot round-trips exactly (the SAME questions, every answer and mark, the typed text, the
Code age check chain, the round id Momentum's keys are built from); the clock reads what it read when you left and
runs on from there, however long you were away; one language's round is not another's; a snapshot older than 12 hours,
for an activity that is gone / not played in that language / no longer shaped like the saved questions, or corrupt,
is dropped; unavailable storage never throws.
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

HARNESS = r"""
import * as S from "./resume.mjs";
import * as R from "./round.mjs";

const out = {};
const HOUR = 3600 * 1000;
const T0 = 1_800_000_000_000;

const items = [0, 1, 2, 3].map((n) => ({
  prompt: "p" + n, answer: "a" + n, explain: "why" + n, show: n === 2 ? "x = 1" : "", check: n === 1 ? "print(1)" : undefined,
}));
const noUndefined = (o) => JSON.parse(JSON.stringify(o));

// A round: q0 right, q1 missed ("nope"), q2 open and being looked at, "ab" half typed. Clock: 0-5 s running, so 5 s.
let rs = R.newRound(4);
rs = R.recordAnswer(rs, 0, "a0", true);
rs = R.jumpTo(rs, 1);
rs = R.recordAnswer(rs, 1, "nope", false);
rs = R.jumpTo(rs, 2);
const clock = { t0: 1000, pausedAt: null, lost: 0 };
const make = (extra = {}) => S.makeSnapshot({
  language: "python", activityId: "eval", checkId: "2026-10-26/99", checkLeft: ["truthy", "brackets"], checkAges: [31],
  roundId: "kq1", items, rs, typed: "ab", clock, showing: false, now: T0, perfNow: 6000, ...extra,
});
const snap = make();

const wire = S.serialize(snap);
const back = S.parseSnapshot(wire);
out.roundTrip = {
  equal: JSON.stringify(back) === JSON.stringify(snap),
  items: back && JSON.stringify(back.items) === JSON.stringify(noUndefined(items)),
  answers: back && back.rs.answers, index: back && back.rs.index, typed: back && back.typed,
  check: back && [back.checkId, back.checkLeft, back.checkAges], roundId: back && back.roundId, elapsed: back && back.elapsed,
  statuses: back && back.rs.answers.map((_, i) => R.cellStatus(back.rs, i)),
  // The snapshot is a copy: changing the round afterwards does not change it.
  isolated: (() => { const s2 = make(); rs.answers[3] = { given: "z", right: true }; const kept = s2.rs.answers[3] === null; rs.answers[3] = null; return kept; })(),
};

// ── The clock ──
{
  // Left at perf 6000 with the clock at 5 s: restored a "day later" (perf is a different number) it still reads 5 s.
  const open = R.newRound(3);
  const c = S.clockFromElapsed(5, 900000, open);              // an open question: running from 5 s
  const reviewing = R.recordAnswer(open, 0, "a", true);
  const cp = S.clockFromElapsed(5, 900000, reviewing);         // looking at an answered one: paused at 5 s
  // Round trip with a clock that lost time paused: t0 0, 10 s lost, read at 25 s = 15 s.
  const lossy = S.makeSnapshot({ ...{
    language: "python", activityId: "eval", checkId: "", checkLeft: [], checkAges: [], roundId: "r", items, rs: R.newRound(4),
    typed: "", showing: false, now: T0 }, clock: { t0: 0, pausedAt: null, lost: 10000 }, perfNow: 25000 });
  const paused = S.makeSnapshot({ ...{
    language: "python", activityId: "eval", checkId: "", checkLeft: [], checkAges: [], roundId: "r", items, rs: R.newRound(4),
    typed: "", showing: false, now: T0 }, clock: { t0: 0, pausedAt: 7000, lost: 1000 }, perfNow: 90000 });
  out.clock = {
    snapElapsed: snap.elapsed,
    atRestore: R.clockElapsed(c, 900000), threeLater: R.clockElapsed(c, 903000),
    pausedAtRestore: R.clockElapsed(cp, 900000), pausedLater: R.clockElapsed(cp, 990000), pausedFlag: cp.pausedAt !== null,
    runningFlag: c.pausedAt === null,
    lossy: lossy.elapsed, pausedSnap: paused.elapsed,
    noClock: S.makeSnapshot({ ...{
      language: "python", activityId: "eval", checkId: "", checkLeft: [], checkAges: [], roundId: "r", items, rs: R.newRound(4),
      typed: "", showing: false, now: T0 }, clock: null, perfNow: 1 }).elapsed,
    negativeSeconds: R.clockElapsed(S.clockFromElapsed(-4, 1000, open), 1000),
  };
}

// ── What it is held to ──
const acts = [
  { id: "eval", title: "Quick Eval", count: 16, kind: "type", choices: [] },
  { id: "truthy", title: "Truthy", count: 16, kind: "pick", choices: ["a0", "a1", "a2", "a3"] },
  { id: "brackets", title: "Brackets", count: 16, kind: "pick", choices: ["a0", "a1", "a2", "a3"] },
];
const ctx = (extra = {}) => ({ language: "python", activities: acts, now: T0 + 1000, ...extra });
const reason = (s, c) => S.staleReason(s, c);
const chk = (activities) => reason(make(), ctx({ activities }));
out.stale = {
  fine: reason(snap, ctx()),
  justUnder12h: reason(snap, ctx({ now: T0 + 12 * HOUR })),
  over12h: reason(snap, ctx({ now: T0 + 12 * HOUR + 1 })),
  future: reason(snap, ctx({ now: T0 - 5 * 60 * 1000 })),
  otherLanguage: reason(snap, ctx({ language: "dart" })),
  gone: chk(acts.filter((a) => a.id !== "eval")),
  fewerQuestions: chk(acts.map((a) => (a.id === "eval" ? { ...a, count: 3 } : a))),
  moreQuestionsFine: chk(acts.map((a) => (a.id === "eval" ? { ...a, count: 30 } : a))),
  shorterRoundFine: chk(acts.map((a) => (a.id === "eval" ? { ...a, count: 4 } : a))),
  checkMemberGone: chk(acts.filter((a) => a.id !== "brackets")),
  pickChoicesChanged: reason(make({ activityId: "truthy", checkLeft: [], checkId: "" }),
    ctx({ activities: acts.map((a) => (a.id === "truthy" ? { ...a, choices: ["yes", "no"] } : a)) })),
  pickChoicesSame: reason(make({ activityId: "truthy", checkLeft: [], checkId: "" }), ctx()),
};

// ── Corrupt ones ──
const bad = (mutate) => { const o = JSON.parse(S.serialize(snap)); mutate(o); return S.parseSnapshot(JSON.stringify(o)); };
out.corrupt = {
  empty: S.parseSnapshot(""), nullIn: S.parseSnapshot(null), undef: S.parseSnapshot(undefined),
  notJson: S.parseSnapshot("{not json"), array: S.parseSnapshot("[1,2]"), number: S.parseSnapshot("5"), nullJson: S.parseSnapshot("null"),
  otherVersion: bad((o) => { o.v = 0; }),
  futureVersion: bad((o) => { o.v = 2; }),
  noItems: bad((o) => { o.items = []; }),
  answersLength: bad((o) => { o.rs.answers.pop(); }),
  indexHigh: bad((o) => { o.rs.index = 4; }),
  indexNeg: bad((o) => { o.rs.index = -1; }),
  indexFraction: bad((o) => { o.rs.index = 1.5; }),
  badAnswer: bad((o) => { o.rs.answers[0] = { given: 5, right: true }; }),
  badItem: bad((o) => { o.items[0].prompt = 7; }),
  elapsedNaN: bad((o) => { o.elapsed = "5"; }),
  elapsedNegative: bad((o) => { o.elapsed = -1; }),
  checkAgesText: bad((o) => { o.checkAges = ["31"]; }),
  noTyped: bad((o) => { delete o.typed; }),
  noRoundId: bad((o) => { delete o.roundId; }),
  stillFine: bad(() => {}) !== null,
};

// ── Storage ──
const fake = () => {
  const m = new Map();
  return { getItem: (k) => (m.has(k) ? m.get(k) : null), setItem: (k, v) => { m.set(k, String(v)); }, removeItem: (k) => { m.delete(k); }, _m: m };
};
const boom = { getItem() { throw new Error("blocked"); }, setItem() { throw new Error("full"); }, removeItem() { throw new Error("blocked"); } };
const dartAct = [{ id: "dart_eval", title: "Dart Eval", count: 16, kind: "type", choices: [] }];
const pySnap = make();
const dartSnap = make({ language: "dart", activityId: "dart_eval", checkId: "", checkLeft: [], checkAges: [], roundId: "kd9" });
{
  S.forgetMemory();
  const st = fake();
  S.saveSnapshot(pySnap, st);
  S.saveSnapshot(dartSnap, st);
  const keys = [...st._m.keys()].sort();
  const py = S.loadResumable(ctx(), st);
  const dt = S.loadResumable({ language: "dart", activities: dartAct, now: T0 + 1000 }, st);
  // Each language's own copy, independently.
  S.clearSnapshot("python", st);
  const pyAfterClear = S.loadResumable(ctx(), st);
  const dtAfterClear = S.loadResumable({ language: "dart", activities: dartAct, now: T0 + 1000 }, st);
  const keysAfter = [...st._m.keys()];
  out.storage = {
    keys, key: S.resumeKey("sql"),
    py: py && [py.language, py.roundId], dart: dt && [dt.language, dt.roundId],
    pyAfterClear, dtAfterClear: dtAfterClear && dtAfterClear.roundId, keysAfter,
  };
}
{
  // A page reload forgets the module copy; sessionStorage still has it.
  S.forgetMemory();
  const st = fake();
  S.saveSnapshot(pySnap, st);
  S.forgetMemory();
  const reloaded = S.loadResumable(ctx(), st);
  out.reload = {
    same: reloaded && JSON.stringify(reloaded) === JSON.stringify(pySnap),
    // and the module copy serves a tab switch even when storage is gone
    memoryOnly: (() => { S.forgetMemory(); const s2 = fake(); S.saveSnapshot(pySnap, s2); s2._m.clear(); const r = S.loadResumable(ctx(), s2); return !!r && r.roundId === "kq1"; })(),
  };
}
{
  // Expiry and stale activities clear BOTH copies.
  S.forgetMemory();
  const st = fake();
  S.saveSnapshot(pySnap, st);
  const expired = S.loadResumable(ctx({ now: T0 + 13 * HOUR }), st);
  out.expiry = { expired, storageEmpty: st._m.size === 0, againNull: S.loadResumable(ctx(), st) };
  S.saveSnapshot(pySnap, st);
  const gone = S.loadResumable(ctx({ activities: [acts[1], acts[2]] }), st);
  out.expiry.goneNull = gone; out.expiry.goneStorageEmpty = st._m.size === 0;
  // Corrupt text in storage is removed, not used.
  S.forgetMemory();
  const st2 = fake();
  st2.setItem(S.resumeKey("python"), "{oops");
  out.expiry.corruptNull = S.loadResumable(ctx(), st2);
  out.expiry.corruptRemoved = st2._m.size === 0;
  // A snapshot stored under the wrong language's key is not used for that language.
  S.forgetMemory();
  const st3 = fake();
  st3.setItem(S.resumeKey("dart"), S.serialize(pySnap));
  out.expiry.wrongKey = S.loadResumable({ language: "dart", activities: dartAct, now: T0 + 1000 }, st3);
}
{
  S.forgetMemory();
  let threw = "";
  try {
    S.saveSnapshot(pySnap, boom);
    const r = S.loadResumable(ctx(), boom);
    out.blocked = { servedFromMemory: !!r && r.roundId === "kq1" };
    S.clearSnapshot("python", boom);
    out.blocked.cleared = S.loadResumable(ctx(), boom);
    S.forgetMemory();
    out.blocked.nothing = S.loadResumable(ctx(), boom);
    out.blocked.noStore = S.loadResumable(ctx(), null);
    S.saveSnapshot(pySnap, null);
    out.blocked.noStoreSave = !!S.loadResumable(ctx(), null);
  } catch (e) { threw = String(e); }
  out.blocked = { ...out.blocked, threw };
}

// ── The button ──
out.label = {
  mid: S.resumeLabel(snap, "Quick Eval"),
  first: S.resumeLabel({ items, rs: R.newRound(4) }, "Truthy"),
  last: S.resumeLabel({ items, rs: R.jumpTo(R.newRound(4), 3) }, "Truthy"),
};

console.log(JSON.stringify(out));
"""


@functools.cache
def results() -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="brain_resume_test_"))
    try:
        (tmp / "harness.mjs").write_text(HARNESS, encoding="utf-8")
        for name, src in (("resume", "brainResume.ts"), ("round", "brainRound.ts")):
            built = subprocess.run(
                [NODE, str(ESBUILD), str(LIB / src), "--bundle", "--format=esm", "--platform=node",
                 f"--outfile={tmp / (name + '.mjs')}", "--log-level=error"],
                capture_output=True, text=True, timeout=120,
            )
            assert built.returncode == 0, built.stderr
        ran = subprocess.run([NODE, str(tmp / "harness.mjs")], capture_output=True, text=True, timeout=120, cwd=tmp)
        assert ran.returncode == 0, ran.stderr[-3000:]
        return json.loads(ran.stdout.strip().splitlines()[-1])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class Snapshot(unittest.TestCase):
    def test_a_round_trips_exactly(self):
        r = results()["roundTrip"]
        self.assertTrue(r["equal"], "serialize then parse gives back the same snapshot")
        self.assertTrue(r["items"], "the SAME questions, never regenerated")
        self.assertEqual(r["answers"], [{"given": "a0", "right": True}, {"given": "nope", "right": False}, None, None])
        self.assertEqual((r["index"], r["typed"]), (2, "ab"))
        self.assertEqual(r["statuses"], ["right", "missed", "open", "open"], "the Questions grid is derived from it")
        self.assertEqual(r["check"], ["2026-10-26/99", ["truthy", "brackets"], [31]], "a Code age check chain rides along")
        self.assertEqual(r["roundId"], "kq1", "Momentum's per-answer keys are built from the round id: it must not change")

    def test_the_snapshot_is_a_copy(self):
        self.assertTrue(results()["roundTrip"]["isolated"])


class ClockFreeze(unittest.TestCase):
    def test_the_elapsed_value_is_taken_when_saved(self):
        c = results()["clock"]
        self.assertEqual(c["snapElapsed"], 5.0, "clock started at 1 s, read at 6 s")
        self.assertEqual(c["lossy"], 15.0, "paused time already taken off stays off")
        self.assertEqual(c["pausedSnap"], 6.0, "a paused clock reads where it stopped, however late it was saved")
        self.assertEqual(c["noClock"], 0)

    def test_time_away_is_not_counted(self):
        c = results()["clock"]
        self.assertAlmostEqual(c["atRestore"], 5.0, places=6, msg="reads what it read when you left")
        self.assertAlmostEqual(c["threeLater"], 8.0, places=6, msg="then runs on from there")
        self.assertTrue(c["runningFlag"])

    def test_an_answered_question_comes_back_paused(self):
        c = results()["clock"]
        self.assertTrue(c["pausedFlag"])
        self.assertAlmostEqual(c["pausedAtRestore"], 5.0, places=6)
        self.assertAlmostEqual(c["pausedLater"], 5.0, places=6, msg="reading a miss costs no time, away or not")

    def test_a_negative_value_never_runs_backwards(self):
        self.assertEqual(results()["clock"]["negativeSeconds"], 0)


class WhenItIsDropped(unittest.TestCase):
    def test_twelve_hours(self):
        s = results()["stale"]
        self.assertEqual(s["fine"], "")
        self.assertEqual(s["justUnder12h"], "", "exactly 12 hours is still fine")
        self.assertEqual(s["over12h"], "expired")
        self.assertTrue(s["future"], "a clock set back does not keep a snapshot forever")

    def test_another_language_is_not_this_ones_round(self):
        self.assertEqual(results()["stale"]["otherLanguage"], "another language")

    def test_an_activity_that_is_gone_or_not_played_here(self):
        s = results()["stale"]
        self.assertTrue(s["gone"])
        self.assertTrue(s["checkMemberGone"], "a check whose later activity is gone cannot go on")

    def test_questions_that_no_longer_match(self):
        s = results()["stale"]
        self.assertTrue(s["fewerQuestions"], "more saved questions than the activity now asks")
        self.assertEqual(s["moreQuestionsFine"], "")
        self.assertEqual(s["shorterRoundFine"], "", "a round can be shorter than the count (a small pool)")
        self.assertTrue(s["pickChoicesChanged"], "a pick answer that is no longer one of its two choices")
        self.assertEqual(s["pickChoicesSame"], "")

    def test_corrupt_snapshots_are_rejected(self):
        c = results()["corrupt"]
        self.assertTrue(c.pop("stillFine"), "the mutator itself keeps a good snapshot good")
        self.assertEqual({k: v for k, v in c.items() if v is not None}, {}, "every corrupt shape parses to null")


class Storage(unittest.TestCase):
    def test_one_key_per_language(self):
        s = results()["storage"]
        self.assertEqual(s["key"], "code-coach:brain-round:sql")
        self.assertEqual(s["keys"], ["code-coach:brain-round:dart", "code-coach:brain-round:python"])

    def test_two_languages_resume_independently(self):
        s = results()["storage"]
        self.assertEqual(s["py"], ["python", "kq1"])
        self.assertEqual(s["dart"], ["dart", "kd9"])
        self.assertIsNone(s["pyAfterClear"], "clearing Python's round")
        self.assertEqual(s["dtAfterClear"], "kd9", "leaves Dart's alone")
        self.assertEqual(s["keysAfter"], ["code-coach:brain-round:dart"])

    def test_a_reload_loses_the_module_copy_but_not_the_round(self):
        r = results()["reload"]
        self.assertTrue(r["same"])
        self.assertTrue(r["memoryOnly"], "and with sessionStorage gone the module copy still serves a tab switch")

    def test_stale_and_corrupt_copies_are_removed_from_both_places(self):
        e = results()["expiry"]
        self.assertIsNone(e["expired"])
        self.assertTrue(e["storageEmpty"])
        self.assertIsNone(e["againNull"])
        self.assertIsNone(e["goneNull"])
        self.assertTrue(e["goneStorageEmpty"])
        self.assertIsNone(e["corruptNull"])
        self.assertTrue(e["corruptRemoved"])
        self.assertIsNone(e["wrongKey"])

    def test_unavailable_storage_never_throws(self):
        b = results()["blocked"]
        self.assertEqual(b["threw"], "")
        self.assertTrue(b["servedFromMemory"])
        self.assertIsNone(b["cleared"])
        self.assertIsNone(b["nothing"])
        self.assertIsNone(b["noStore"])
        self.assertTrue(b["noStoreSave"])


class Button(unittest.TestCase):
    def test_the_resume_button_text(self):
        label = results()["label"]
        self.assertEqual(label["mid"], "Resume Quick Eval - question 3 of 4")
        self.assertEqual(label["first"], "Resume Truthy - question 1 of 4")
        self.assertEqual(label["last"], "Resume Truthy - question 4 of 4")
