"""Brain Drills: the round's bookkeeping and the code each question can run.

web/src/lib/brainRound.ts is pure TypeScript - what you answered, where you
are, which question is next, what the clock counted, and the program behind
each question for "Run it". The web project has no JavaScript test runner,
so (like tests/test_farm_scene.py) this bundles it with the esbuild already
in web/node_modules and runs it in node.

Two kinds of test:

* The rules, as scenarios: reviewing adds no misses and no time, an answer
  counts once, jumping around still needs every question answered, the clock
  stops on an answered question and picks up where it stopped.
* The oracle for "Run it": for every question of every activity, in both
  languages, the program the module builds is run for real (node's vm, the
  Python interpreter) and what it prints must be the drill's answer - or, for
  Syntax Snap and Bracket Check, whether it parses must be the answer.
"""

from __future__ import annotations

import functools
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import pytest

from code_coach import brain

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
LIB = WEB / "src" / "lib"
ESBUILD = WEB / "node_modules" / "esbuild" / "bin" / "esbuild"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(
    NODE is None or not ESBUILD.exists(),
    reason="needs node and web/node_modules/esbuild (run npm install in web/)",
)

SEEDS = range(8)

HARNESS = r"""
import * as R from "./round.mjs";
import { readFileSync } from "node:fs";

const input = JSON.parse(readFileSync(process.argv[2], "utf8"));
const out = {};

// ── The rules ──────────────────────────────────────────────────────────
const labels = (s) => s.answers.map((_, i) => R.cellLabel(s, i));
const statuses = (s) => s.answers.map((_, i) => R.cellStatus(s, i));

{
  let s = R.newRound(5);
  out.fresh = {
    index: s.index, complete: R.isComplete(s), reviewing: R.isReviewing(s), answered: R.answeredCount(s),
    statuses: statuses(s), labels: labels(s), next: R.nextOpen(s, 0), back: R.backTarget(s),
    forward: R.forwardTarget(s), empty: R.isComplete(R.newRound(0)),
  };

  // Answer 0 right, 1 wrong, in order.
  s = R.recordAnswer(s, 0, "4", true);
  const afterFirst = { next: R.resumeTarget(s), statuses: statuses(s) };
  s = R.jumpTo(s, R.nextOpen(s, 0));
  s = R.recordAnswer(s, 1, "9", false);
  out.sequential = {
    afterFirst, index: s.index, reviewingMissed: R.isReviewing(s), statuses: statuses(s),
    labels: labels(s), answered: R.answeredCount(s), forward: R.forwardTarget(s), resume: R.resumeTarget(s),
  };

  // An answer counts once: a second one changes nothing, not even for a miss turned right.
  const again = R.recordAnswer(s, 1, "7", true);
  const again0 = R.recordAnswer(s, 0, "nope", false);
  out.once = {
    sameObject: again === s, given: again.answers[1], first: again0.answers[0],
    misses: R.missesOf(again, [1, 2, 3, 4, 5].map((n) => ({ prompt: "p" + n, answer: "a", explain: "", show: "" }))).length,
  };

  // Going back to look changes nothing about the score: same answers, same misses.
  const items = [0, 1, 2, 3, 4].map((n) => ({ prompt: "p" + n, answer: "a" + n, explain: "", show: "" }));
  const before = JSON.stringify(R.missesOf(s, items));
  let visited = R.jumpTo(s, 0);
  const wasReviewing = R.isReviewing(visited);
  visited = R.jumpTo(visited, 1);
  visited = R.jumpTo(visited, 0);
  out.review = {
    wasReviewing, answersUnchanged: JSON.stringify(visited.answers) === JSON.stringify(s.answers),
    missesUnchanged: JSON.stringify(R.missesOf(visited, items)) === before,
    answered: R.answeredCount(visited), backFromFirst: R.backTarget(visited), backFromSecond: R.backTarget(R.jumpTo(s, 1)),
  };

  // Out of order: answer 4 first, then 2 (a miss), then 0, 3, 1. Misses list in question order.
  let t = R.newRound(5);
  t = R.jumpTo(t, 4);
  t = R.recordAnswer(t, 4, "x4", true);
  const afterLast = { complete: R.isComplete(t), resume: R.resumeTarget(t) };
  t = R.jumpTo(t, 2);
  t = R.recordAnswer(t, 2, "wrong2", false);
  t = R.jumpTo(t, 0);
  t = R.recordAnswer(t, 0, "wrong0", false);
  const mid = { complete: R.isComplete(t), open: t.answers.map((a) => a === null) };
  t = R.recordAnswer(R.jumpTo(t, 3), 3, "x3", true);
  const oneLeft = { complete: R.isComplete(t), resume: R.nextOpen(t, 3) };
  t = R.recordAnswer(R.jumpTo(t, 1), 1, "x1", true);
  out.outOfOrder = {
    afterLast, mid, oneLeft, complete: R.isComplete(t), noneLeft: R.nextOpen(t, 1),
    misses: R.missesOf(t, items).map((m) => [m.item.prompt, m.given]),
  };

  // Navigation: wrap-around, clamping, the end of a finished round.
  let w = R.newRound(4);
  w = R.recordAnswer(R.recordAnswer(w, 0, "a", true), 3, "a", true);
  out.nav = {
    nextOpenFrom3: R.nextOpen(w, 3), nextOpenFrom1: R.nextOpen(w, 1),
    clampHigh: R.jumpTo(w, 99).index, clampLow: R.jumpTo(w, -4).index,
    forwardFromLast: R.forwardTarget(R.jumpTo(w, 3)), forwardMid: R.forwardTarget(R.jumpTo(w, 1)),
    sameIndex: R.jumpTo(w, 0) === w,
  };
  const done = R.recordAnswer(R.recordAnswer(w, 1, "a", false), 2, "a", true);
  out.nav.finishedForwardFromLast = R.forwardTarget(R.jumpTo(done, 3));
  out.nav.finishedComplete = R.isComplete(done);
}

// ── The clock ──────────────────────────────────────────────────────────
{
  const sec = (c, now) => R.clockElapsed(c, now);
  // Running 0-5s, reading a miss 5-15s (paused), running 15-18s.
  let s = R.newRound(4);
  let c = R.clockStart(0);
  s = R.recordAnswer(s, 0, "a", true);
  s = R.jumpTo(s, 1);
  c = R.clockFor(c, s, 2000);
  const running = sec(c, 3000);
  s = R.recordAnswer(s, 1, "bad", false);
  c = R.clockFor(c, s, 5000);
  const pausedAt5 = sec(c, 5000), pausedAt12 = sec(c, 12000);
  s = R.jumpTo(s, 2);
  c = R.clockFor(c, s, 15000);
  const resumed = sec(c, 18000);

  // Going Back to an answered question pauses; coming forward resumes; the stint counts for nothing.
  let c2 = R.clockStart(0);
  let s2 = R.recordAnswer(R.newRound(3), 0, "a", true);
  s2 = R.jumpTo(s2, 1);
  c2 = R.clockFor(c2, s2, 4000);          // running on q1
  s2 = R.jumpTo(s2, 0);
  c2 = R.clockFor(c2, s2, 6000);          // back to q0: paused at 6s
  const whileBack = sec(c2, 60000);
  s2 = R.jumpTo(s2, 1);
  c2 = R.clockFor(c2, s2, 66000);         // forward again after 60s
  const afterForward = sec(c2, 70000);

  // Pausing twice or resuming a running clock must not move it.
  let c3 = R.clockStart(1000);
  c3 = R.clockPause(c3, 3000);
  const c3b = R.clockPause(c3, 9000);
  const resumeRunning = R.clockResume(R.clockStart(0), 5000);
  // And looking at several answered questions in a row is still one pause.
  let c4 = R.clockStart(0);
  let s4 = R.recordAnswer(R.recordAnswer(R.newRound(4), 0, "a", true), 1, "a", true);
  s4 = R.jumpTo(s4, 0);
  c4 = R.clockFor(c4, s4, 2000);
  s4 = R.jumpTo(s4, 1);
  c4 = R.clockFor(c4, s4, 3000);
  s4 = R.jumpTo(s4, 2);
  c4 = R.clockFor(c4, s4, 10000);
  out.clock = {
    running, pausedAt5, pausedAt12, resumed, whileBack, afterForward,
    doublePause: sec(c3b, 20000), doublePauseSame: c3b === c3, resumeRunningSame: resumeRunning.lost,
    chain: sec(c4, 12000), neverNegative: R.clockElapsed(R.clockStart(5000), 1000),
  };
}

// ── The program behind a question ──────────────────────────────────────
out.runnables = input.items.map((it) => {
  const r = R.runnableFor(it.activity, it.item, it.language);
  return { ...it, runnable: r };
});

const fixed = (activity, item, language) => R.runnableFor(activity, item, language);
const item = (prompt, extra = {}) => ({ prompt, answer: "", explain: "", show: "", ...extra });
out.fixed = {
  jsBrackets: fixed("brackets", item("([)]"), "javascript"),
  pyBrackets: fixed("brackets", item("x = [1, 2"), "python"),
  jsSyntax: fixed("syntax", item("return 5;"), "javascript"),
  recallBad: fixed("recall", item("e?", {}), "python"),
  recall: fixed("recall", item("e?", { show: "e = 15" }), "python"),
  evalJs: fixed("eval", item("5 == \"5\""), "javascript"),
  evalPy: fixed("eval", item("len(\"tree\")"), "python"),
  cleaned: R.cleanError([
    "Traceback (most recent call last):",
    "  File \"C:\\\\x\\\\code_coach\\\\_trace_runner.py\", line 173, in main",
    "    exec(code_obj, globals_ns)",
    "    ~~~~^^^^^^^^^^^^^^^^^^^^^^",
    "  File \"C:\\\\Temp\\\\tmp5vdy15tw.py\", line 3, in <module>",
    "    x.foo",
    "AttributeError: 'int' object has no attribute 'foo'",
  ].join("\n")),
  syntaxA: R.isSyntaxError("SyntaxError: invalid syntax"),
  syntaxB: R.isSyntaxError("SyntaxError on line 2: Unexpected token ')'"),
  syntaxC: R.isSyntaxError("IndentationError: unexpected indent"),
  syntaxD: R.isSyntaxError("NameError: name 'x' is not defined"),
  syntaxE: R.isSyntaxError("Traceback (most recent call last):\n  File \"x\", line 1\nSyntaxError: bad"),
  syntaxF: R.isSyntaxError(null),
  syntaxG: R.isSyntaxError("TypeError: x is not a SyntaxError"),
};

console.log(JSON.stringify(out));
"""

# Runs each program for real, in one process per language, and reports what it
# printed (or the error's name) - the oracle for "Run it".
NODE_RUNNER = r"""
const vm = require("vm");
const util = require("util");
const progs = JSON.parse(require("fs").readFileSync(process.argv[2], "utf8"));
const show = (v) => (typeof v === "string" ? v : util.inspect(v, { depth: 3, breakLength: 100 }));
const result = progs.map((code) => {
  const lines = [];
  const ctx = vm.createContext({ console: { log: (...a) => lines.push(a.map(show).join(" ")) } });
  try {
    vm.runInContext(code, ctx, { timeout: 5000 });
    return { out: lines.join("\n"), error: "" };
  } catch (e) {
    return { out: lines.join("\n"), error: (e && e.name) || "Error" };
  }
});
process.stdout.write(JSON.stringify(result));
"""

PY_RUNNER = r"""
import contextlib, io, json, sys
progs = json.load(open(sys.argv[1], encoding="utf-8"))
result = []
for code in progs:
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "snippet", "exec"), {"__name__": "__main__"})
        result.append({"out": buf.getvalue(), "error": ""})
    except BaseException as e:
        result.append({"out": buf.getvalue(), "error": type(e).__name__})
sys.stdout.write(json.dumps(result))
"""


def _items() -> list[dict]:
    seen: dict[tuple, dict] = {}
    for language in ("javascript", "python", "dart"):
        for activity in brain.activities_in(language):
            for seed in SEEDS:
                for it in brain.make_round(activity.id, seed, language):
                    key = (language, activity.id, it.prompt, it.show)
                    seen.setdefault(key, {
                        "activity": activity.id,
                        "language": language,
                        "item": {"prompt": it.prompt, "answer": it.answer, "explain": it.explain,
                                 "show": it.show, "check": it.check},
                    })
    return list(seen.values())


@functools.cache
def results() -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="brain_round_test_"))
    try:
        (tmp / "harness.mjs").write_text(HARNESS, encoding="utf-8")
        (tmp / "items.json").write_text(json.dumps({"items": _items()}), encoding="utf-8")
        built = subprocess.run(
            [NODE, str(ESBUILD), str(LIB / "brainRound.ts"), "--bundle", "--format=esm", "--platform=node",
             f"--outfile={tmp / 'round.mjs'}", "--log-level=error"],
            capture_output=True, text=True, timeout=120,
        )
        assert built.returncode == 0, built.stderr
        ran = subprocess.run([NODE, str(tmp / "harness.mjs"), str(tmp / "items.json")],
                             capture_output=True, text=True, timeout=120, cwd=tmp)
        assert ran.returncode == 0, ran.stderr[-3000:]
        return json.loads(ran.stdout.strip().splitlines()[-1])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _execute(language: str, programs: list[str]) -> list[dict]:
    tmp = Path(tempfile.mkdtemp(prefix="brain_round_run_"))
    try:
        (tmp / "progs.json").write_text(json.dumps(programs), encoding="utf-8")
        if language == "javascript":
            (tmp / "run.js").write_text(NODE_RUNNER, encoding="utf-8")
            cmd = [NODE, str(tmp / "run.js"), str(tmp / "progs.json")]
        else:
            (tmp / "run.py").write_text(PY_RUNNER, encoding="utf-8")
            cmd = [sys.executable, "-I", str(tmp / "run.py"), str(tmp / "progs.json")]
        done = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=240, cwd=tmp)
        assert done.returncode == 0, done.stderr[-3000:]
        return json.loads(done.stdout)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _plain(text: str) -> str:
    """What the drill forgives when you type an answer: case, spacing in brackets, quotes."""
    t = text.strip()
    t = re.sub(r"^(['\"`])(.*)\1$", r"\2", t, flags=re.S).strip().lower()
    return re.sub(r"\s+", "", t) if t[:1] in "[({" else t


class RoundRules(unittest.TestCase):
    def test_a_fresh_round_is_all_open(self):
        r = results()["fresh"]
        self.assertEqual((r["index"], r["answered"], r["complete"], r["reviewing"]), (0, 0, False, False))
        self.assertEqual(r["statuses"], ["open"] * 5)
        self.assertEqual(r["labels"][0], "Question 1, not answered yet, current")
        self.assertEqual(r["labels"][4], "Question 5, not answered yet")
        self.assertEqual((r["next"], r["back"], r["forward"]), (1, -1, 1))
        self.assertFalse(r["empty"], "a round of no questions is not 'complete'")

    def test_answering_in_order_walks_forward_and_marks_cells(self):
        r = results()["sequential"]
        self.assertEqual(r["afterFirst"]["next"], 1)
        self.assertEqual(r["afterFirst"]["statuses"], ["right"] + ["open"] * 4)
        self.assertEqual(r["statuses"], ["right", "missed", "open", "open", "open"])
        self.assertEqual(r["labels"][1], "Question 2, missed, current")
        self.assertEqual(r["labels"][0], "Question 1, right")
        self.assertTrue(r["reviewingMissed"], "a missed question is shown for reading, not answering")
        self.assertEqual((r["answered"], r["forward"], r["resume"]), (2, 2, 2))

    def test_an_answer_counts_once(self):
        r = results()["once"]
        self.assertEqual(r["given"], {"given": "9", "right": False})
        self.assertEqual(r["first"], {"given": "4", "right": True})
        self.assertEqual(r["misses"], 1)

    def test_reviewing_changes_no_answer_and_no_miss(self):
        r = results()["review"]
        self.assertTrue(r["wasReviewing"])
        self.assertTrue(r["answersUnchanged"])
        self.assertTrue(r["missesUnchanged"])
        self.assertEqual((r["answered"], r["backFromFirst"], r["backFromSecond"]), (2, -1, 0))

    def test_jumping_around_still_needs_every_question(self):
        r = results()["outOfOrder"]
        self.assertFalse(r["afterLast"]["complete"], "answering the last one early is not finishing")
        self.assertEqual(r["afterLast"]["resume"], 0)
        self.assertFalse(r["mid"]["complete"])
        self.assertEqual(r["mid"]["open"], [False, True, False, True, False])
        self.assertFalse(r["oneLeft"]["complete"])
        self.assertEqual(r["oneLeft"]["resume"], 1)
        self.assertTrue(r["complete"])
        self.assertEqual(r["noneLeft"], -1)

    def test_misses_come_in_question_order_whatever_order_they_were_answered(self):
        self.assertEqual(results()["outOfOrder"]["misses"], [["p0", "wrong0"], ["p2", "wrong2"]])

    def test_navigation_edges(self):
        r = results()["nav"]
        self.assertEqual(r["nextOpenFrom3"], 1, "wraps round to the start")
        self.assertEqual(r["nextOpenFrom1"], 2)
        self.assertEqual((r["clampHigh"], r["clampLow"]), (3, 0))
        self.assertEqual(r["forwardFromLast"], 1, "from the last question, forward is the first one still open")
        self.assertEqual(r["forwardMid"], 2)
        self.assertTrue(r["sameIndex"])
        self.assertTrue(r["finishedComplete"])
        self.assertEqual(r["finishedForwardFromLast"], -1, "nothing open: the caller finishes the round")


class ClockRules(unittest.TestCase):
    def test_the_clock_stops_on_an_answered_question_and_resumes_on_an_open_one(self):
        c = results()["clock"]
        self.assertEqual(c["running"], 3.0)
        self.assertEqual(c["pausedAt5"], 5.0)
        self.assertEqual(c["pausedAt12"], 5.0, "reading a miss costs no time")
        self.assertEqual(c["resumed"], 8.0, "5 s running + 3 s after the pause; the 10 s between do not count")

    def test_going_back_and_forward_again_costs_nothing(self):
        c = results()["clock"]
        self.assertEqual(c["whileBack"], 6.0)
        self.assertEqual(c["afterForward"], 10.0, "6 s before going back + 4 s after coming forward")

    def test_pausing_twice_or_resuming_a_running_clock_changes_nothing(self):
        c = results()["clock"]
        self.assertEqual(c["doublePause"], 2.0)
        self.assertTrue(c["doublePauseSame"])
        self.assertEqual(c["resumeRunningSame"], 0)

    def test_a_run_of_reviews_is_one_pause(self):
        c = results()["clock"]
        self.assertEqual(c["chain"], 4.0, "2 s, then reviewing 2-10 s, then 2 s more")
        self.assertEqual(c["neverNegative"], 0)


class RunIt(unittest.TestCase):
    def test_fixed_cases(self):
        f = results()["fixed"]
        self.assertFalse(f["jsBrackets"]["ok"], "JavaScript brackets are not a program")
        self.assertIn("nothing to run", f["jsBrackets"]["reason"])
        self.assertEqual(f["pyBrackets"], {"ok": True, "code": "x = [1, 2", "run": "", "parseIsTheAnswer": True})
        self.assertEqual(f["jsSyntax"]["code"], "return 5;")
        self.assertEqual(f["jsSyntax"]["run"], '(0, eval)("return 5;");')
        self.assertFalse(f["recallBad"]["ok"])
        self.assertEqual(f["recall"]["code"], "e = 15\nprint(e)")
        self.assertEqual(f["evalJs"]["code"], 'console.log(5 == "5");')
        self.assertEqual(f["evalPy"]["code"], 'print(len("tree"))')

    def test_the_tracers_traceback_loses_the_tracer(self):
        cleaned = results()["fixed"]["cleaned"]
        self.assertNotIn("_trace_runner", cleaned)
        self.assertNotIn("exec(code_obj", cleaned)
        self.assertIn('File "snippet", line 3, in <module>', cleaned)
        self.assertIn("x.foo", cleaned)
        self.assertTrue(cleaned.endswith("AttributeError: 'int' object has no attribute 'foo'"))

    def test_what_counts_as_a_syntax_error(self):
        f = results()["fixed"]
        self.assertTrue(f["syntaxA"] and f["syntaxB"] and f["syntaxC"] and f["syntaxE"])
        self.assertFalse(f["syntaxD"] or f["syntaxF"] or f["syntaxG"])

    def _check(self, language: str) -> None:
        rows = [r for r in results()["runnables"] if r["language"] == language]
        runnable = [r for r in rows if r["runnable"]["ok"]]
        self.assertTrue(runnable)
        done = _execute(language, [r["runnable"]["run"] or r["runnable"]["code"] for r in runnable])
        wrong = []
        for r, got in zip(runnable, done):
            item = r["item"]
            if r["runnable"].get("raisesIsTheAnswer"):
                # Error or Fine: the snippet as shown either raises or it does not.
                if (got["error"] != "") != (item["answer"] == "error"):
                    wrong.append((r["activity"], item["prompt"], item["answer"], got))
            elif r["runnable"]["parseIsTheAnswer"]:
                parses = got["error"] != "SyntaxError" and not got["error"].endswith("IndentationError")
                if parses != (item["answer"] in ("valid", "yes")):
                    wrong.append((r["activity"], item["prompt"], item["answer"], got))
            elif got["error"] or _plain(got["out"]) != _plain(item["answer"]):
                wrong.append((r["activity"], item["prompt"], item["answer"], got))
        self.assertEqual(wrong[:5], [], f"{len(wrong)} of {len(runnable)} programs disagree with the drill")
        # Every activity (but JavaScript's bracket strings) is covered.
        covered = {r["activity"] for r in runnable}
        want = {a.id for a in brain.activities_in(language)} - ({"brackets"} if language == "javascript" else set())
        self.assertEqual(covered, want)

    def test_javascript_programs_print_the_drills_answers(self):
        self._check("javascript")

    def test_python_programs_print_the_drills_answers(self):
        self._check("python")

    def test_only_javascript_brackets_are_refused(self):
        refused = {(r["language"], r["activity"]) for r in results()["runnables"] if not r["runnable"]["ok"]
                   and brain.ACTIVITIES_BY_ID[r["activity"]].oracle != "flutter"}
        self.assertEqual(refused, {("javascript", "brackets")})


class RunItDart(unittest.TestCase):
    """Dart's "Run it": `dartProgram` in brainRound.ts is the same rule as `full_program` in tests/dart_oracle.py (the one
    the Dart oracle runs), and the programs it builds print each drill's answer under the real `dart`."""

    def _rows(self) -> list[dict]:
        # Flutter-widget activities have no "Run it" (RunItFlutter below), so they are not Dart programs here.
        return [r for r in results()["runnables"] if r["language"] == "dart"
                and brain.ACTIVITIES_BY_ID[r["activity"]].oracle != "flutter"]

    def test_the_browser_builds_the_program_the_oracle_runs(self):
        from tests import dart_oracle

        rows = self._rows()
        self.assertGreater(len(rows), 100)
        for r in rows:
            item = r["item"]
            self.assertTrue(r["runnable"]["ok"], item["prompt"])
            self.assertEqual(r["runnable"]["code"], dart_oracle.full_program(item["check"] or item["prompt"]), item["prompt"])
            self.assertEqual(r["runnable"]["run"], "")
            self.assertFalse(r["runnable"]["parseIsTheAnswer"])
        self.assertEqual({r["activity"] for r in rows},
                         {a.id for a in brain.activities_in("dart") if a.oracle != "flutter"})

    def test_dart_programs_print_the_drills_answers(self):
        from tests import dart_oracle

        if dart_oracle.DART is None:
            self.skipTest("needs dart")
        rows = self._rows()
        by_mode: dict[str, list[dict]] = {}
        for r in rows:
            by_mode.setdefault(brain.ACTIVITIES_BY_ID[r["activity"]].oracle, []).append(r)
        for mode, group in by_mode.items():
            got = dart_oracle.dart_values([r["runnable"]["code"] for r in group], mode)
            wrong = [(r["item"]["prompt"], r["item"]["answer"], g) for r, g in zip(group, got) if g != r["item"]["answer"]]
            self.assertEqual(wrong[:5], [], f"{len(wrong)} of {len(group)} Dart programs disagree with the drill ({mode})")

    def test_a_fine_or_error_item_is_judged_by_whether_it_throws(self):
        rows = [r for r in self._rows() if brain.ACTIVITIES_BY_ID[r["activity"]].oracle == "error"]
        self.assertTrue(rows)
        self.assertTrue(all(r["runnable"].get("raisesIsTheAnswer") for r in rows))
        others = [r for r in self._rows() if brain.ACTIVITIES_BY_ID[r["activity"]].oracle != "error"]
        self.assertFalse(any(r["runnable"].get("raisesIsTheAnswer") for r in others))


class RunItFlutter(unittest.TestCase):
    """A Flutter-widget question cannot be run in the browser: "Run it" says so instead of running anything."""

    def _rows(self) -> list[dict]:
        return [r for r in results()["runnables"] if r["language"] == "dart"
                and brain.ACTIVITIES_BY_ID[r["activity"]].oracle == "flutter"]

    def test_every_flutter_question_is_refused_with_the_reason(self):
        rows = self._rows()
        self.assertGreater(len(rows), 50)
        self.assertEqual({r["activity"] for r in rows}, {a.id for a in brain.activities_in("dart") if a.oracle == "flutter"})
        for r in rows:
            self.assertFalse(r["runnable"]["ok"], r["item"]["prompt"])
            self.assertIn("Flutter widgets cannot run here", r["runnable"]["reason"])
            self.assertIn("measured with Flutter itself", r["runnable"]["reason"])

    def test_the_rule_is_the_flutter_prefixes_and_only_for_dart(self):
        # The browser knows a Flutter activity by its id (tests/test_brain_packs.py holds id prefix == oracle).
        flutter_id = re.compile(r"f[lsw]_")
        self.assertTrue(all(flutter_id.match(a.id) for a in brain.activities_in("dart") if a.oracle == "flutter"))
        self.assertTrue(all(a.oracle == "flutter" for a in brain.ACTIVITIES if flutter_id.match(a.id)))


if __name__ == "__main__":
    unittest.main()
