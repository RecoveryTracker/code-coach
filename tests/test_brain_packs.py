"""Brain Drills' packs: every activity the package discovered, in both languages.

These tests are parametrised over `brain.ACTIVITIES`, so a new pack
(`code_coach/brain/pack_<name>.py`) is covered the moment it exists - nothing
here names a pack's activities. They check

* discovery: packs are found by name, the originals come first with their ids
  in order, a pack that fails to import is recorded in `LOAD_ERRORS` (and fails
  `test_every_pack_imports_cleanly`), ids are unique;
* shape: a round has `count` items, no repeats, short prompts, non-empty
  answers, pick answers among the two choices, typed answers with no stray
  spaces, each language in its own spelling (True/None vs true/null), a
  sentence of 'explain', a deterministic round per seed, `concepts` as plain
  lowercase words, par < slow;
* the oracle: every answer of every activity with `oracle="value"` held to the
  real node (JavaScript) or the real interpreter (Python) over many seeds and
  over every template of every Pool. The answers are modelled by hand in the
  packs; here the runtime is the judge (the oracle rule).

The original seven keep their own oracles in test_brain.py and
test_brain_python.py (`oracle=""`); only they may skip the generic one.
"""

from __future__ import annotations

import json
import random
import re
import shutil
import subprocess
import sys
import unittest

from code_coach import brain
from code_coach.brain import ACTIVITIES, ACTIVITIES_BY_ID, CHECK, activity_for, make_round

NODE = shutil.which("node")
ORIGINAL_IDS = ("eval", "truthy", "loops", "trace", "brackets", "recall", "syntax")
LANGS = ("python", "javascript")
SEEDS = range(40)
TEMPLATE_SEEDS = range(8)
CONCEPT = re.compile(r"^[a-z]+([ -][a-z]+)*$")


def _pack_activities():
    return [a for a in ACTIVITIES if a.id not in ORIGINAL_IDS]


# ── The real runtimes ───────────────────────────────────────────────────

PY_DRIVER = r'''
import ast, contextlib, io, json, sys

def run(code):
    sink = io.StringIO()
    try:
        with contextlib.redirect_stdout(sink):
            body = ast.parse(code).body
            ns = {}
            exec(compile(ast.Module(body[:-1], []), "<s>", "exec"), ns)
            last = body[-1]
            if not isinstance(last, ast.Expr):
                return "ERROR the last line is not an expression"
            return str(eval(compile(ast.Expression(last.value), "<s>", "eval"), ns))
    except BaseException as e:
        return "ERROR " + repr(e)

cases = json.loads(sys.stdin.read())
sys.stdout.write(json.dumps([run(c) for c in cases]))
'''

NODE_DRIVER = r'''
const vm = require("vm");
const util = require("util");
const cases = JSON.parse(require("fs").readFileSync(0, "utf8"));
const show = (v) => (typeof v === "string" ? v : util.inspect(v, { depth: 3, breakLength: 100 }));
const out = cases.map((code) => {
  const ctx = vm.createContext({ console: { log() {} } });
  try {
    return show(vm.runInContext(code, ctx, { timeout: 3000 }));
  } catch (e) {
    return "ERROR " + ((e && e.name) || "Error") + ": " + ((e && e.message) || "");
  }
});
process.stdout.write(JSON.stringify(out));
'''


def run_programs(language: str, programs: list[str]) -> list[str]:
    """The printed value of each program's last line, from the real runtime."""
    if language == "python":
        cmd = [sys.executable, "-I", "-W", "ignore", "-c", PY_DRIVER]
    else:
        cmd = [NODE, "-e", NODE_DRIVER]
    done = subprocess.run(cmd, input=json.dumps(programs), capture_output=True, text=True, encoding="utf-8",
                          timeout=300)
    if done.returncode != 0:
        raise AssertionError(done.stderr[-3000:])
    return json.loads(done.stdout)


def _samples(activity, language: str):
    """Items over many seeds, plus every template of the activity's pool on several seeds."""
    seen: dict[str, object] = {}
    for seed in SEEDS:
        for item in make_round(activity.id, seed, language):
            seen.setdefault(item.prompt + "\x00" + item.check, item)
    pool = activity_for(activity.id, language).make
    for template in getattr(pool, "templates", ()):
        for seed in TEMPLATE_SEEDS:
            item = template(random.Random(seed))
            seen.setdefault(item.prompt + "\x00" + item.check, item)
    return list(seen.values())


# ── Discovery ───────────────────────────────────────────────────────────

class DiscoveryTests(unittest.TestCase):
    def test_every_pack_imports_cleanly(self) -> None:
        self.assertEqual(brain.LOAD_ERRORS, {}, "a pack failed to import or is malformed")

    def test_the_originals_come_first_in_their_own_order(self) -> None:
        self.assertEqual([a.id for a in ACTIVITIES][:len(ORIGINAL_IDS)], list(ORIGINAL_IDS))

    def test_ids_are_unique_and_looked_up_by_id(self) -> None:
        ids = [a.id for a in ACTIVITIES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ACTIVITIES_BY_ID), set(ids))
        self.assertTrue(set(CHECK) <= set(ids))

    def test_packs_load_in_sorted_name_order(self) -> None:
        self.assertEqual(brain.PACKS, sorted(brain.PACKS))
        self.assertEqual([a.id for a in ACTIVITIES][len(ORIGINAL_IDS):],
                         [a.id for name in brain.PACKS
                          for a in __import__(f"code_coach.brain.{name}", fromlist=["ACTIVITIES"]).ACTIVITIES])

    def test_only_the_originals_may_skip_the_generic_oracle(self) -> None:
        for a in ACTIVITIES:
            if a.id not in ORIGINAL_IDS:
                self.assertEqual(a.oracle, "value", f"{a.id} needs oracle='value'")

    def test_the_home_screen_payload_knows_groups_and_concepts(self) -> None:
        for language in LANGS:
            s = brain.summary(language=language)
            self.assertEqual([a["id"] for a in s["activities"]], [a.id for a in ACTIVITIES])
            for a in s["activities"]:
                self.assertTrue(a["group"], a["id"])
                self.assertTrue(a["concepts"], a["id"])
            self.assertEqual(s["languages"][0], "python", "Python is listed first")
            self.assertTrue({a["group"] for a in s["activities"]} <= set(s["groups"]))


# ── Shape ───────────────────────────────────────────────────────────────

class ShapeTests(unittest.TestCase):
    def test_every_activity_is_well_formed(self) -> None:
        for a in ACTIVITIES:
            with self.subTest(activity=a.id):
                self.assertTrue(a.title and a.blurb and a.question)
                self.assertGreater(a.count, 0)
                self.assertIn(a.kind, ("type", "pick"))
                self.assertGreater(a.par, 0)
                self.assertLess(a.par, a.slow)
                self.assertTrue(a.group.strip(), "needs a group")
                self.assertTrue(a.concepts, "needs concepts")
                self.assertIsInstance(a.concepts, tuple)
                for c in a.concepts:
                    self.assertRegex(c, CONCEPT)
                self.assertIsNotNone(a.make_py, "needs a Python generator")
                if a.kind == "pick":
                    self.assertEqual(len(set(a.choices)), 2)
                    self.assertTrue(all(a.choices))

    def test_a_round_has_count_items_without_repeats_and_short_prompts(self) -> None:
        for a in ACTIVITIES:
            for language in LANGS:
                for seed in range(5):
                    with self.subTest(activity=a.id, language=language, seed=seed):
                        items = make_round(a.id, seed, language)
                        self.assertEqual(len(items), a.count)
                        self.assertEqual(len({i.prompt + "|" + i.show for i in items}), len(items), "repeat in a round")
                        for i in items:
                            self.assertLessEqual(len(i.prompt), 220)
                            self.assertLessEqual(i.prompt.count("\n"), 9)

    def test_answers_are_typeable_and_pick_answers_are_a_choice(self) -> None:
        for a in ACTIVITIES:
            for language in LANGS:
                for seed in range(10):
                    for i in make_round(a.id, seed, language):
                        with self.subTest(activity=a.id, language=language, prompt=i.prompt):
                            self.assertTrue(i.answer)
                            self.assertEqual(i.answer, i.answer.strip(), "leading/trailing spaces")
                            self.assertNotIn("\n", i.answer)
                            self.assertLessEqual(len(i.answer), 40)
                            if a.kind == "pick":
                                self.assertIn(i.answer, a.choices)

    def test_a_pick_round_uses_both_choices(self) -> None:
        for a in ACTIVITIES:
            if a.kind != "pick":
                continue
            for language in LANGS:
                answers = {i.answer for s in range(10) for i in make_round(a.id, s, language)}
                self.assertEqual(answers, set(a.choices), f"{a.id} {language}")

    def test_each_language_is_spelled_its_own_way(self) -> None:
        # Python says True/False/None; JavaScript says true/false/null/undefined. (Answers only: a Python
        # string answer is text, so it is checked as a whole word.)
        py_banned = re.compile(r"\b(true|false|null|undefined)\b")
        js_banned = re.compile(r"\b(True|False|None)\b")
        for a in ACTIVITIES:
            for seed in range(10):
                for i in make_round(a.id, seed, "python"):
                    with self.subTest(activity=a.id, language="python", prompt=i.prompt):
                        self.assertIsNone(py_banned.search(i.answer), i.answer)
                for i in make_round(a.id, seed, "javascript"):
                    with self.subTest(activity=a.id, language="javascript", prompt=i.prompt):
                        self.assertIsNone(js_banned.search(i.answer), i.answer)

    def test_pack_items_explain_themselves_in_a_sentence(self) -> None:
        for a in _pack_activities():
            for language in LANGS:
                for i in _samples(a, language):
                    with self.subTest(activity=a.id, language=language, prompt=i.prompt):
                        self.assertGreaterEqual(len(i.explain.strip()), 8)
                        self.assertNotIn("$", i.explain, "an unfilled hole")
                        self.assertNotIn("$", i.prompt, "an unfilled hole")

    def test_a_seed_gives_the_same_round(self) -> None:
        for a in ACTIVITIES:
            for language in LANGS:
                self.assertEqual(make_round(a.id, 7, language), make_round(a.id, 7, language), f"{a.id} {language}")

    def test_pack_pools_have_many_templates_and_every_one_makes_an_item(self) -> None:
        for a in _pack_activities():
            for language in LANGS:
                pool = activity_for(a.id, language).make
                templates = getattr(pool, "templates", None)
                self.assertIsNotNone(templates, f"{a.id}: build the generator with _model.Pool")
                self.assertGreaterEqual(len(templates), 10, f"{a.id} {language}")
                for t in templates:
                    for seed in range(3):
                        item = t(random.Random(seed))
                        self.assertTrue(item.prompt and item.answer, f"{a.id} {language} {t.__name__}")

    def test_the_reading_pack_is_deep_in_python_and_wide_in_javascript(self) -> None:
        # The brief for pack_reading: Python is the priority, so its pool is the bigger one.
        if "pack_reading" not in brain.PACKS:
            self.skipTest("no reading pack")
        from code_coach.brain import pack_reading

        self.assertEqual(len(pack_reading.ACTIVITIES), 8)
        for a in pack_reading.ACTIVITIES:
            self.assertGreaterEqual(len(activity_for(a.id, "python").make.templates), 40, a.id)
            self.assertGreaterEqual(len(activity_for(a.id, "javascript").make.templates), 25, a.id)

    def test_the_two_languages_have_their_own_wording_where_given(self) -> None:
        for a in ACTIVITIES:
            js, py = activity_for(a.id, "javascript"), activity_for(a.id, "python")
            self.assertEqual(js.title, py.title)
            self.assertTrue(py.question and py.blurb)

    def test_everything_that_takes_an_activity_id_takes_a_pack_activity(self) -> None:
        for a in _pack_activities():
            for language in LANGS:
                payload = brain.round_payload(a.id, 3, language)
                self.assertEqual(len(payload["items"]), a.count)
                self.assertEqual(brain.code_age(a.id, a.par * a.count, 0, a.count, language), 20)
                self.assertEqual(brain.code_age(a.id, a.slow * a.count, 0, a.count, language), 80)
            brain.record(a.id, 30, 1, a.count, language="python")
            entry = next(x for x in brain.summary(language="python")["activities"] if x["id"] == a.id)
            self.assertIsNotNone(entry["best"])


# ── The routes ──────────────────────────────────────────────────────────

class RouteTests(unittest.TestCase):
    def test_python_is_the_default_language_and_javascript_still_works(self) -> None:
        from code_coach.api.server import brain_round, brain_summary

        self.assertEqual(brain_summary()["language"], "python")
        self.assertEqual(brain_round("loops", 1)["language"], "python")
        self.assertEqual(brain_summary("javascript")["language"], "javascript")
        self.assertEqual(brain_round("loops", 1, "javascript")["language"], "javascript")

    def test_a_pack_round_comes_over_the_routes_in_both_languages(self) -> None:
        from code_coach.api.server import brain_round, brain_summary

        for a in _pack_activities():
            for language in LANGS:
                r = brain_round(a.id, 4, language)
                self.assertEqual(len(r["items"]), a.count)
                self.assertTrue(all(i["answer"] for i in r["items"]))
                self.assertTrue(all(i["check"] or i["prompt"] for i in r["items"]))
        ids = [x["id"] for x in brain_summary()["activities"]]
        self.assertTrue({a.id for a in _pack_activities()} <= set(ids))


# ── The oracle ──────────────────────────────────────────────────────────

class OracleTests(unittest.TestCase):
    def _check(self, language: str) -> None:
        for a in ACTIVITIES:
            if a.oracle != "value":
                continue
            items = _samples(a, language)
            self.assertGreater(len(items), 20, a.id)
            got = run_programs(language, [i.check or i.prompt for i in items])
            wrong = [(i.prompt, i.answer, g) for i, g in zip(items, got) if g != i.answer]
            self.assertEqual(wrong[:5], [], f"{a.id} ({language}): {len(wrong)} of {len(items)} disagree with the runtime")

    def test_python_answers_are_what_python_prints(self) -> None:
        self._check("python")

    @unittest.skipUnless(NODE, "needs node")
    def test_javascript_answers_are_what_node_prints(self) -> None:
        self._check("javascript")


if __name__ == "__main__":
    unittest.main()
