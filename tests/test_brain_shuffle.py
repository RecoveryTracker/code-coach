"""Brain Drills Shuffle: one round of questions from many activities.

- The round (`brain.make_shuffle` / `GET /api/brain/shuffle`): 16 questions in every drill language, each naming the
  activity that made it, drawn only from the chosen home-screen headings (all of them when none or only unknown ones
  are given), never the same activity twice in a row, never a show-then-hide activity (Variable Recall), and every
  question exactly what its own activity would deal (a pick question's answer is one of ITS two choices).
- The result (`POST /api/brain/result` with activity "shuffle"): kept under "shuffle", counts for the day's stamp, has
  its own best on the home payload, is never part of a Code age check, and leaves every activity's best alone. Its age
  is the usual formula against the AVERAGE par and slow times of the activities its questions came from.
- A saved Shuffle round resumes only while every question's activity is still there and still fits
  (`staleReason` in web/src/lib/brainResume.ts, run in node).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import pytest

from code_coach import brain

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "web" / "src" / "lib"
ESBUILD = ROOT / "web" / "node_modules" / "esbuild" / "bin" / "esbuild"
NODE = shutil.which("node")


class Round(unittest.TestCase):
    def test_no_activity_is_called_shuffle(self):
        self.assertNotIn(brain.SHUFFLE_ID, brain.ACTIVITIES_BY_ID)

    def test_every_language_deals_a_full_mixed_round(self):
        for language in brain.LANGUAGES:
            for seed in range(25):
                with self.subTest(language=language, seed=seed):
                    got = brain.make_shuffle(language, (), seed)
                    self.assertEqual(len(got), brain.SHUFFLE_COUNT)
                    ids = [aid for aid, _ in got]
                    allowed = {a.id for a in brain.shuffle_activities(language)}
                    self.assertTrue(set(ids) <= allowed)
                    self.assertGreater(len(set(ids)), 3, "it really is a mix")
                    self.assertFalse(any(a == b for a, b in zip(ids, ids[1:])), "never one activity twice in a row")
                    keys = [aid + "|" + i.prompt + "|" + i.show for aid, i in got]
                    self.assertEqual(len(keys), len(set(keys)), "no question twice")

    def test_each_question_is_what_its_own_activity_deals(self):
        for language in brain.LANGUAGES:
            for seed in range(10):
                for aid, item in brain.make_shuffle(language, (), seed):
                    act = brain.activity_for(aid, language)
                    self.assertFalse(item.show, "a shuffle has no 'Remember these' phase")
                    self.assertEqual(act.show_seconds, 0)
                    if act.kind == "pick":
                        self.assertIn(item.answer, act.choices, (language, aid))
                    self.assertTrue(item.answer.strip(), (language, aid))

    def test_variable_recall_is_never_shuffled(self):
        for language in brain.LANGUAGES:
            ids = {a.id for a in brain.shuffle_activities(language)}
            shown = {a.id for a in brain.activities_in(language) if a.show_seconds > 0}
            self.assertFalse(ids & shown, language)
            self.assertTrue(ids, language)

    def test_groups_narrow_it_and_unknown_groups_mean_all(self):
        groups = brain.shuffle_groups("python")
        self.assertEqual(groups, [g for g in brain._groups("python") if g in groups], "home-screen order")
        one = groups[1]
        for seed in range(10):
            for aid, _ in brain.make_shuffle("python", [one], seed):
                self.assertEqual(brain.ACTIVITIES_BY_ID[aid].group, one)
        self.assertEqual(brain.shuffle_groups("python", ["No such heading"]), groups)
        self.assertEqual(brain.shuffle_groups("python", ["", one]), [one])

    def test_one_activity_alone_still_deals(self):
        # A heading with a single activity: it cannot avoid itself, and must not loop forever trying.
        python = brain.activities_in("python")
        lone = [g for g in brain.shuffle_groups("python")
                if sum(1 for a in python if a.group == g and a.show_seconds <= 0) == 1]
        if not lone:
            self.skipTest("no heading with a single activity today")
        got = brain.make_shuffle("python", [lone[0]], 3)
        self.assertEqual(len(got), brain.SHUFFLE_COUNT)

    def test_the_route(self):
        from code_coach.api import server

        got = server.brain_shuffle(language="c", groups="", seed=5)
        self.assertEqual(got["activity"], "shuffle")
        self.assertEqual(len(got["items"]), brain.SHUFFLE_COUNT)
        self.assertTrue(all(i["activity"] in brain.ACTIVITIES_BY_ID for i in got["items"]))
        self.assertEqual(got, server.brain_shuffle(language="c", groups="", seed=5), "the same seed, the same round")
        with self.assertRaises(Exception):
            server.brain_shuffle(language="cobol")


class Result(unittest.TestCase):
    def _post(self, **kw):
        from code_coach.api import server
        from code_coach.api.schemas import BrainResultRequest

        return server.brain_result(BrainResultRequest(**kw))

    def test_the_age_is_held_to_the_average_par(self):
        a, b = brain.activity_for("eval", "python"), brain.activity_for("truthy", "python")
        par, slow = (a.par + b.par) / 2, (a.slow + b.slow) / 2
        # Exactly at the average par, no mistakes: 20. Exactly at the average slow: 80. Halfway: 50.
        self.assertEqual(brain.shuffle_age(par * 4, 0, 4, ["eval", "truthy", "eval", "truthy"], "python"), 20)
        self.assertEqual(brain.shuffle_age(slow * 4, 0, 4, ["eval", "truthy", "eval", "truthy"], "python"), 80)
        self.assertEqual(brain.shuffle_age((par + slow) / 2 * 4, 0, 4, ["eval", "truthy", "eval", "truthy"], "python"),
                         50)
        # Five years a mistake; unknown ids ignored; nothing known left: by mistakes alone.
        self.assertEqual(brain.shuffle_age(par * 4, 2, 4, ["eval", "truthy", "nope", "truthy"], "python"),
                         brain.shuffle_age(par * 4, 0, 4, ["eval", "truthy", "truthy"], "python") + 10)
        self.assertEqual(brain.shuffle_age(999, 1, 4, ["nope"], "python"), 35)

    def test_a_shuffle_result_is_kept_and_counts_for_the_stamp(self):
        before = brain.summary(language="python")
        self.assertIsNone(before["shuffle"]["best"])
        ids = [aid for aid, _ in brain.make_shuffle("python", (), 1)]
        first = self._post(activity="shuffle", seconds=60, errors=2, total=16, language="python", activities=ids)
        self.assertTrue(first["best"])
        self.assertTrue(20 <= first["age"] <= 80)
        worse = self._post(activity="shuffle", seconds=200, errors=6, total=16, language="python", activities=ids)
        self.assertFalse(worse["best"])
        after = brain.summary(language="python")
        self.assertTrue(after["trainedToday"], "a shuffle round puts in the day's stamp")
        self.assertEqual(after["shuffle"]["best"]["age"], first["age"])
        self.assertEqual(after["shuffle"]["last"]["seconds"], 200)
        self.assertEqual([a["best"] for a in after["activities"]], [a["best"] for a in before["activities"]],
                         "no activity's best moves")
        self.assertEqual(after["checkAges"], before["checkAges"], "never part of a Code age check")
        self.assertIsNone(brain.summary(language="dart")["shuffle"]["best"], "kept per language")


@pytest.mark.skipif(NODE is None or not ESBUILD.exists(), reason="needs node and web/node_modules/esbuild")
class Resume(unittest.TestCase):
    HARNESS = r"""
import * as S from "./resume.mjs";
import * as R from "./round.mjs";
const T0 = 1_800_000_000_000;
const acts = [
  { id: "shuffle", title: "Shuffle", count: 16, kind: "type", choices: ["", ""] },
  { id: "eval", title: "Eval", count: 16, kind: "type", choices: ["", ""] },
  { id: "truthy", title: "Truthy", count: 16, kind: "pick", choices: ["truthy", "falsy"] },
];
const items = [
  { prompt: "1 + 1", answer: "2", explain: "", show: "", activity: "eval" },
  { prompt: "[]", answer: "truthy", explain: "", show: "", activity: "truthy" },
];
const snap = (its) => S.makeSnapshot({
  language: "python", activityId: "shuffle", checkId: "", checkLeft: [], checkAges: [], roundId: "r1",
  items: its, rs: R.newRound(its.length), typed: "", clock: null, showing: false, now: T0, perfNow: 0,
});
const ctx = (activities) => ({ language: "python", activities, now: T0 + 1000 });
const back = S.parseSnapshot(JSON.stringify(snap(items)));
console.log(JSON.stringify({
  fits: S.staleReason(snap(items), ctx(acts)),
  keepsActivity: back ? back.items.map((i) => i.activity) : null,
  gone: S.staleReason(snap(items), ctx(acts.filter((a) => a.id !== "truthy"))),
  changed: S.staleReason(snap(items), ctx(acts.map((a) => a.id === "truthy" ? { ...a, choices: ["yes", "no"] } : a))),
  noShuffle: S.staleReason(snap(items), ctx(acts.filter((a) => a.id !== "shuffle"))),
}));
"""

    def test_a_saved_shuffle_resumes_only_while_its_activities_fit(self):
        tmp = Path(tempfile.mkdtemp(prefix="brain_shuffle_test_"))
        try:
            (tmp / "harness.mjs").write_text(self.HARNESS, encoding="utf-8")
            for name, src in (("resume", "brainResume.ts"), ("round", "brainRound.ts")):
                built = subprocess.run(
                    [NODE, str(ESBUILD), str(LIB / src), "--bundle", "--format=esm", "--platform=node",
                     f"--outfile={tmp / (name + '.mjs')}", "--log-level=error"],
                    capture_output=True, text=True, timeout=120,
                )
                self.assertEqual(built.returncode, 0, built.stderr)
            ran = subprocess.run([NODE, str(tmp / "harness.mjs")], capture_output=True, text=True, encoding="utf-8",
                                 timeout=120, cwd=tmp)
            self.assertEqual(ran.returncode, 0, ran.stderr[-3000:])
            got = json.loads(ran.stdout.strip().splitlines()[-1])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(got["fits"], "")
        self.assertEqual(got["keepsActivity"], ["eval", "truthy"], "each question's activity survives a save")
        self.assertTrue(got["gone"])
        self.assertTrue(got["changed"])
        self.assertTrue(got["noShuffle"])
