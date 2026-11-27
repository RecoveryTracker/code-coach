"""Brain Drills' packs: every activity the package discovered, in every language it is played in.

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
  packs; here the runtime is the judge (the oracle rule). Dart is held to the
  real `dart` in BATCHES (tests/dart_oracle.py: one program, one compile, one
  run per activity); a Dart activity's `oracle` says how its printed lines
  become the value - "value", "lines" (glued together) or "error" (does it
  compile and run quietly: "fine" or "error").

An activity is played in a language exactly when it has that language's
generator (`Activity.languages`), so every loop below goes over
`brain.activities_in(language)`: a Dart-only pack is never asked for Python.

C is held to the real compilers in ONE batch for all the C activities (tests/c_oracle.py: clang -O0 and
-O2 with signed and unsigned `char`, MSVC /Od where installed, all printing the same thing, plus the undefined-behaviour
sanitizer); SQL to the real SQLite, a fresh in-memory database per item (tests/sql_oracle.py).

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
from pathlib import Path

from code_coach import brain
from code_coach.brain import ACTIVITIES, ACTIVITIES_BY_ID, CHECK, activities_in, activity_for, make_round
from code_coach.brain.items import Activity
from tests import c_oracle, dart_oracle, flutter_oracle, rust_oracle, sql_oracle, ts_oracle

NODE = shutil.which("node")
ORIGINAL_IDS = ("eval", "truthy", "loops", "trace", "brackets", "recall", "syntax")
LANGS = ("python", "javascript", "dart", "c", "sql", "typescript", "rust")
#: How a Dart activity's printed lines become its value (Activity.oracle); python and javascript only have "value".
DART_MODES = ("value", "lines", "error")
#: How a TypeScript or Rust activity's run becomes its value: "value" (what it printed) or "error" (a fine/error pick:
#: it does not compile, or it throws / panics).
TYPED_MODES = ("value", "error")
#: A Dart-language activity about Flutter WIDGETS: held to a real `flutter test` (tests/flutter_oracle.py), not to `dart`.
FLUTTER_MODE = "flutter"
SEEDS = range(40)
WEB = Path(__file__).resolve().parent.parent / "web"
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
                if a.languages == ("dart",):
                    self.assertIn(a.oracle, DART_MODES + (FLUTTER_MODE,), f"{a.id} needs oracle in {DART_MODES + (FLUTTER_MODE,)}")
                elif a.languages in (("typescript",), ("rust",)):
                    self.assertIn(a.oracle, TYPED_MODES, f"{a.id} needs oracle in {TYPED_MODES}")
                else:
                    self.assertEqual(a.oracle, "value", f"{a.id} needs oracle='value'")

    def test_an_activity_is_played_in_exactly_the_languages_it_has_a_generator_for(self) -> None:
        for a in ACTIVITIES:
            self.assertEqual(a.languages, tuple(
                lang for lang, make in (("python", a.make_py), ("javascript", a.make), ("dart", a.make_dart),
                                        ("c", a.make_c), ("sql", a.make_sql), ("typescript", a.make_ts),
                                        ("rust", a.make_rs)) if make))
            for language in LANGS:
                if language in a.languages:
                    self.assertEqual(activity_for(a.id, language).id, a.id)
                else:
                    with self.assertRaises(KeyError):
                        activity_for(a.id, language)
                    with self.assertRaises(KeyError):
                        make_round(a.id, 1, language)

    def test_a_pack_activity_may_be_dart_only_but_needs_at_least_one_generator(self) -> None:
        from code_coach.brain import _check_pack
        from code_coach.brain.items import Item

        def make(rng):
            return Item("1", "1", "one")

        dart_only = Activity("zz_dart_only", "Z", "z", "q", 3, "type", 1.0, 2.0, make_dart=make, group="Z",
                             concepts=("string",))
        none_at_all = Activity("zz_none", "Z", "z", "q", 3, "type", 1.0, 2.0, group="Z", concepts=("string",))
        self.assertEqual(dart_only.languages, ("dart",))
        self.assertEqual(none_at_all.languages, ())
        self.assertEqual(_check_pack("pack_zz", (dart_only,), set()), (dart_only,))
        with self.assertRaisesRegex(ValueError, "at least one generator"):
            _check_pack("pack_zz", (none_at_all,), set())
        with self.assertRaisesRegex(ValueError, "duplicate"):
            _check_pack("pack_zz", (dart_only,), {"zz_dart_only"})

    def test_a_dart_only_activity_is_never_listed_under_python_or_javascript(self) -> None:
        dart_only = [a.id for a in ACTIVITIES if a.languages == ("dart",)]
        self.assertTrue(dart_only, "the Dart Core Pack is Dart-only")
        for language in ("python", "javascript"):
            listed = {x["id"] for x in brain.summary(language=language)["activities"]}
            self.assertFalse(listed & set(dart_only), language)
            self.assertTrue(set(brain.check_for(language)) <= listed)
        in_dart = {x["id"] for x in brain.summary(language="dart")["activities"]}
        self.assertEqual(in_dart, {a.id for a in activities_in("dart")})
        self.assertTrue(set(dart_only) <= in_dart)
        self.assertTrue(set(brain.check_for("dart")) <= in_dart)

    def test_the_home_screen_payload_knows_groups_and_concepts(self) -> None:
        for language in LANGS:
            s = brain.summary(language=language)
            self.assertEqual([a["id"] for a in s["activities"]], [a.id for a in activities_in(language)])
            for a in s["activities"]:
                self.assertTrue(a["group"], a["id"])
                self.assertTrue(a["concepts"], a["id"])
            self.assertEqual(s["languages"], ["python", "javascript", "dart", "c", "sql", "typescript", "rust"],
                             "Python first, then JavaScript, Dart, C, SQL, TypeScript and Rust")
            self.assertEqual(set(s["groups"]), {a["group"] for a in s["activities"]}, "no empty heading")
            self.assertEqual(s["check"], list(brain.check_for(language)))


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
                self.assertTrue(a.languages, "needs at least one generator")
                if a.kind == "pick":
                    self.assertEqual(len(set(a.choices)), 2)
                    self.assertTrue(all(a.choices))

    def test_a_round_has_count_items_without_repeats_and_short_prompts(self) -> None:
        for language in LANGS:
            for a in activities_in(language):
                for seed in range(5):
                    with self.subTest(activity=a.id, language=language, seed=seed):
                        items = make_round(a.id, seed, language)
                        self.assertEqual(len(items), a.count)
                        self.assertEqual(len({i.prompt + "|" + i.show for i in items}), len(items), "repeat in a round")
                        for i in items:
                            self.assertLessEqual(len(i.prompt), 220)
                            self.assertLessEqual(i.prompt.count("\n"), 9)

    def test_answers_are_typeable_and_pick_answers_are_a_choice(self) -> None:
        for language in LANGS:
            for a in activities_in(language):
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
        for language in LANGS:
            for a in activities_in(language):
                if a.kind != "pick":
                    continue
                answers = {i.answer for s in range(10) for i in make_round(a.id, s, language)}
                self.assertEqual(answers, set(a.choices), f"{a.id} {language}")

    def test_each_language_is_spelled_its_own_way(self) -> None:
        # Python says True/False/None; JavaScript says true/false/null/undefined. (Answers only: a Python
        # string answer is text, so it is checked as a whole word.)
        # Dart prints like JavaScript here (true/false/null) - but has no `undefined`.
        py_banned = re.compile(r"\b(true|false|null|undefined)\b")
        js_banned = re.compile(r"\b(True|False|None)\b")
        dart_banned = re.compile(r"\b(True|False|None|undefined)\b")
        # C prints numbers and text (1 and 0 for a truth value); SQL prints 1/0 and NULL (typeof() says the word null).
        c_banned = re.compile(r"\b(True|False|None|undefined|null)\b")
        sql_banned = re.compile(r"\b(True|False|None|undefined)\b")
        # TypeScript prints like JavaScript; Rust says true/false and None/Some(..), never null or undefined.
        ts_banned = js_banned
        rust_banned = re.compile(r"\b(True|False|null|undefined)\b")
        banned = {"python": py_banned, "javascript": js_banned, "dart": dart_banned, "c": c_banned, "sql": sql_banned,
                  "typescript": ts_banned, "rust": rust_banned}
        for language, pattern in banned.items():
            for a in activities_in(language):
                for seed in range(10):
                    for i in make_round(a.id, seed, language):
                        with self.subTest(activity=a.id, language=language, prompt=i.prompt):
                            self.assertIsNone(pattern.search(i.answer), i.answer)

    def test_pack_items_explain_themselves_in_a_sentence(self) -> None:
        for language in LANGS:
            for a in activities_in(language):
                if a.id in ORIGINAL_IDS:
                    continue
                for i in _samples(a, language):
                    with self.subTest(activity=a.id, language=language, prompt=i.prompt):
                        self.assertGreaterEqual(len(i.explain.strip()), 8)
                        self.assertNotIn("$", i.explain, "an unfilled hole")
                        if language != "dart":  # Dart's own string interpolation is written with a $
                            self.assertNotIn("$", i.prompt, "an unfilled hole")

    def test_a_seed_gives_the_same_round(self) -> None:
        for language in LANGS:
            for a in activities_in(language):
                self.assertEqual(make_round(a.id, 7, language), make_round(a.id, 7, language), f"{a.id} {language}")

    def test_pack_pools_have_many_templates_and_every_one_makes_an_item(self) -> None:
        for language in LANGS:
            for a in activities_in(language):
                if a.id in ORIGINAL_IDS:
                    continue
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

    def test_the_languages_have_their_own_wording_where_given(self) -> None:
        for a in ACTIVITIES:
            played = [activity_for(a.id, language) for language in a.languages]
            self.assertEqual(len({x.title for x in played}), 1)
            for x in played:
                self.assertTrue(x.question and x.blurb)

    def test_the_dart_core_pack_is_eight_dart_only_activities_with_many_templates(self) -> None:
        if "pack_dartcore" not in brain.PACKS:
            self.skipTest("no dart core pack")
        from code_coach.brain import pack_dartcore

        self.assertEqual([a.id for a in pack_dartcore.ACTIVITIES], [
            "dart_eval", "dart_null", "dart_final", "dart_lms", "dart_str", "dart_func", "dart_class", "dart_async"])
        for a in pack_dartcore.ACTIVITIES:
            self.assertEqual(a.languages, ("dart",), a.id)
            self.assertEqual(a.group, "Dart core")
            self.assertGreaterEqual(len(a.make_dart.templates), 40, a.id)
            self.assertIn(a.kind, ("type", "pick"))
        self.assertEqual({a.oracle for a in pack_dartcore.ACTIVITIES}, {"value", "lines", "error"})

    def test_everything_that_takes_an_activity_id_takes_a_pack_activity(self) -> None:
        for a in _pack_activities():
            for language in a.languages:
                payload = brain.round_payload(a.id, 3, language)
                self.assertEqual(len(payload["items"]), a.count)
                self.assertEqual(brain.code_age(a.id, a.par * a.count, 0, a.count, language), 20)
                self.assertEqual(brain.code_age(a.id, a.slow * a.count, 0, a.count, language), 80)
            language = a.languages[0]
            brain.record(a.id, 30, 1, a.count, language=language)
            entry = next(x for x in brain.summary(language=language)["activities"] if x["id"] == a.id)
            self.assertIsNotNone(entry["best"])
            for other in set(LANGS) - set(a.languages):
                with self.assertRaises(KeyError):
                    brain.record(a.id, 30, 1, a.count, language=other)


# ── The routes ──────────────────────────────────────────────────────────

class RouteTests(unittest.TestCase):
    def test_python_is_the_default_language_and_javascript_still_works(self) -> None:
        from code_coach.api.server import brain_round, brain_summary

        self.assertEqual(brain_summary()["language"], "python")
        self.assertEqual(brain_round("loops", 1)["language"], "python")
        self.assertEqual(brain_summary("javascript")["language"], "javascript")
        self.assertEqual(brain_round("loops", 1, "javascript")["language"], "javascript")

    def test_a_pack_round_comes_over_the_routes_in_every_language_it_is_played_in(self) -> None:
        from code_coach.api.server import brain_round, brain_summary

        for a in _pack_activities():
            for language in a.languages:
                r = brain_round(a.id, 4, language)
                self.assertEqual(len(r["items"]), a.count)
                self.assertTrue(all(i["answer"] for i in r["items"]))
                self.assertTrue(all(i["check"] or i["prompt"] for i in r["items"]))
        ids = [x["id"] for x in brain_summary()["activities"]]
        self.assertTrue({a.id for a in _pack_activities() if "python" in a.languages} <= set(ids))


# ── The oracle ──────────────────────────────────────────────────────────

class OracleTests(unittest.TestCase):
    def _check(self, language: str) -> None:
        for a in activities_in(language):
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


# ── Dart: held to the real `dart`, in batches ───────────────────────────

def dart_wrong(activity, items) -> list[tuple[str, str, str]]:
    """The items whose answer is not what the real dart gives (one batched run for the whole list)."""
    got = dart_oracle.dart_values([i.check or i.prompt for i in items], activity.oracle)
    return [(i.prompt, i.answer, g) for i, g in zip(items, got) if g != i.answer]


@unittest.skipUnless(dart_oracle.DART, "needs dart")
class DartOracleTests(unittest.TestCase):
    """THE ORACLE for every Dart activity: each template on several seeds plus 40 whole rounds, per activity ONE dart
    program (see tests/dart_oracle.py), so a new pack costs seconds, not a `dart run` per item. A new pack is
    picked up here with no edit: this goes over `activities_in("dart")`, by the activity's own `oracle` mode."""

    def test_dart_answers_are_what_dart_prints(self) -> None:
        for a in activities_in("dart"):
            if a.oracle == FLUTTER_MODE:  # widgets: FlutterOracleTests below
                continue
            self.assertIn(a.oracle, DART_MODES, a.id)
            items = _samples(a, "dart")
            self.assertGreater(len(items), 20, a.id)
            wrong = dart_wrong(a, items)
            self.assertEqual(wrong[:5], [], f"{a.id} (dart): {len(wrong)} of {len(items)} disagree with the runtime")

    def test_every_dart_prompt_follows_the_item_convention(self) -> None:
        # What the oracle and "Run it" run: a complete program (it has main), or the body of main, which is never empty.
        for a in activities_in("dart"):
            if a.oracle == FLUTTER_MODE:
                continue
            for i in _samples(a, "dart"):
                with self.subTest(activity=a.id, prompt=i.prompt):
                    program = i.check or i.prompt
                    self.assertTrue(program.strip())
                    full = dart_oracle.full_program(program)
                    self.assertRegex(full, r"\bmain\s*\(")
                    for banned in ("console.log", "def ", "elif ", " := ", "println("):
                        self.assertNotIn(banned, i.prompt)

    def test_dart_prints_true_false_null_lists_and_maps_the_way_the_models_say(self) -> None:
        # A direct check of the printing rules the models rely on (so a Dart upgrade that changes them is noticed).
        from code_coach.brain._dart_model import DIter, DSet, show

        programs = [
            "print(true);\nprint(null);\nprint(2 / 1);\nprint('a');",
            "print([1, 'a', null, 2.0]);",
            "print({'a': 1, 'b': [2]});",
            "print({1, 2, 2});",
            "print([1, 2].map((x) => x));",
            "print([1, 2].toSet());",
        ]
        got = [r.lines for r in dart_oracle.run_batch(programs)]
        self.assertEqual(got[0], ("true", "null", "2.0", "a"))
        self.assertEqual(got[1], (show([1, "a", None, 2.0]),))
        self.assertEqual(got[2], (show({"a": 1, "b": [2]}),))
        self.assertEqual(got[3], (show(DSet([1, 2])),))
        self.assertEqual(got[4], (show(DIter([1, 2])),))
        self.assertEqual(got[5], (show(DSet([1, 2])),))


@unittest.skipUnless(dart_oracle.DART, "needs dart")
class DartOracleSelfTests(unittest.TestCase):
    """The oracle itself is held to account: a wrong model fails it, a broken template is named, batches do not bleed."""

    def test_a_wrong_model_fails_the_oracle(self) -> None:
        from dataclasses import replace

        a = ACTIVITIES_BY_ID["dart_eval"]
        items = _samples(a, "dart")[:30]
        self.assertEqual(dart_wrong(a, items), [])
        # sabotage: the model says / is integer division, and that 1 + 1 is 3
        sabotaged = [replace(i, answer=str(int(float(i.answer)) // 1 + 1)) if i.answer.lstrip("-").replace(".", "").isdigit() else i
                     for i in items]
        self.assertGreater(len(dart_wrong(a, sabotaged)), 5, "the oracle must notice wrong answers")
        for activity_id in ("dart_final", "dart_async"):
            b = ACTIVITIES_BY_ID[activity_id]
            its = _samples(b, "dart")[:30]
            flipped = [replace(i, answer={"fine": "error", "error": "fine"}.get(i.answer, i.answer[::-1] + "Q")) for i in its]
            self.assertGreater(len(dart_wrong(b, flipped)), 10, activity_id)

    def test_a_template_that_does_not_compile_is_named_and_hides_nothing(self) -> None:
        programs = ["print(1 + 1);", "var x = ;\nprint(x);", "print('fine');",
                    "class A {}\nvoid main() => print(A().nope);", "print(7 ~/ 2);"]
        got = dart_oracle.run_batch(programs)
        self.assertEqual([r.lines for r in got], [("2",), (), ("fine",), (), ("3",)])
        self.assertIn("Expected an identifier", got[1].compile_error)
        self.assertIn("line 1 of the snippet", got[1].compile_error, "the message names the line inside the snippet")
        self.assertIn("nope", got[3].compile_error)
        self.assertEqual(got[0].compile_error + got[2].compile_error + got[4].compile_error, "")
        values = dart_oracle.dart_values(programs)
        self.assertTrue(values[1].startswith("COMPILE ERROR"), values[1])

    def test_items_are_isolated_from_each_other(self) -> None:
        # Two programs declaring the same class, a throwing one, and a late async print: nothing leaks between them.
        programs = [
            "class Dog {\n  String toString() => 'one';\n}\nvoid main() => print(Dog());",
            "class Dog {\n  String toString() => 'two';\n}\nvoid main() => print(Dog());",
            "var xs = [1];\nprint(xs[5]);",
            "print('after');",
            "void main() {\n  Future.delayed(Duration.zero, () => print('late'));\n  print('first');\n}",
            "print('last');",
        ]
        got = dart_oracle.run_batch(programs)
        self.assertEqual([r.lines for r in got], [("one",), ("two",), (), ("after",), ("first", "late"), ("last",)])
        self.assertEqual(got[2].error, "RangeError")
        self.assertEqual([dart_oracle.dart_values([p], "error")[0] for p in programs[:3]], ["fine", "fine", "error"])

    def test_the_modes_turn_lines_into_values(self) -> None:
        run = dart_oracle.run_batch(["print('a');\nprint('b');", "final x = 1;\nx = 2;", "print('a');\nthrow 'boom';"])
        self.assertEqual([r.value("value") for r in run][0], "a\nb")
        self.assertEqual(run[0].value("lines"), "ab")
        self.assertEqual([r.value("error") for r in run], ["fine", "error", "error"])
        self.assertTrue(run[2].value("value").startswith("ERROR "))

    def test_the_program_a_snippet_becomes_is_the_one_rule(self) -> None:
        f = dart_oracle.full_program
        self.assertEqual(f("7 ~/ 2"), "void main() {\n  print(7 ~/ 2);\n}")
        self.assertEqual(f("var a = 1;\nprint(a);"), "void main() {\n  var a = 1;\n  print(a);\n}")
        self.assertEqual(f("final x = 1;\nx = 2;"), "void main() {\n  final x = 1;\n  x = 2;\n}")
        whole = "class A {}\nvoid main() => print(A());"
        self.assertEqual(f(whole), whole)


# ── Flutter widgets: held to a real `flutter test`, in ONE batch ────────

FLUTTER_TEMPLATE_SEEDS = range(4)
FLUTTER_ROUND_SEEDS = range(8)


def _flutter_activities():
    return [a for a in activities_in("dart") if a.oracle == FLUTTER_MODE]


def _flutter_samples(activity) -> list:
    """Items over a few rounds plus every template of the pool on a few seeds (a flutter run costs ~10 ms an item)."""
    seen: dict[str, object] = {}
    for seed in FLUTTER_ROUND_SEEDS:
        for item in make_round(activity.id, seed, "dart"):
            seen.setdefault(item.prompt + "\x00" + item.check, item)
    for template in getattr(activity_for(activity.id, "dart").make, "templates", ()):
        for seed in FLUTTER_TEMPLATE_SEEDS:
            item = template(random.Random(seed))
            seen.setdefault(item.prompt + "\x00" + item.check, item)
    return list(seen.values())


_FLUTTER_RESULTS: dict | None = None


def flutter_results() -> dict:
    """{activity id: [(item, what real Flutter measured)]} for EVERY Flutter activity: one `flutter test` run for all of
    them together, made once per test process and shared by the tests below."""
    global _FLUTTER_RESULTS
    if _FLUTTER_RESULTS is None:
        samples = {a.id: _flutter_samples(a) for a in _flutter_activities()}
        flat = [(a_id, i) for a_id, items in samples.items() for i in items]
        got = flutter_oracle.flutter_values([(i.prompt, i.check) for _, i in flat])
        out: dict[str, list] = {a_id: [] for a_id in samples}
        for (a_id, i), g in zip(flat, got):
            out[a_id].append((i, g))
        _FLUTTER_RESULTS = out
    return _FLUTTER_RESULTS


def flutter_wrong(pairs) -> list[tuple[str, str, str]]:
    """The (prompt, answer, what Flutter measured) of every item whose answer is not what Flutter measured."""
    return [(i.prompt, i.answer, g) for i, g in pairs if g != i.answer]


class FlutterShapeTests(unittest.TestCase):
    """What needs no Flutter: the convention of a Flutter item and how the pack is wired."""

    def test_a_flutter_activity_is_dart_only_and_its_id_says_so(self) -> None:
        # the browser's "Run it" cannot run widgets and knows an activity by its id (runnableFor in brainRound.ts)
        acts = _flutter_activities()
        self.assertTrue(acts, "the Flutter layout pack is Flutter-oracle")
        for a in acts:
            self.assertEqual(a.languages, ("dart",), a.id)
            self.assertTrue(re.match(r"f[lsw]_", a.id), f"{a.id}: a Flutter-oracle activity's id starts with fl_, fs_ or fw_")
        for a in ACTIVITIES:
            if re.match(r"f[lsw]_", a.id):
                self.assertEqual(a.oracle, FLUTTER_MODE, f"{a.id}: an fl_/fs_/fw_ activity is a Flutter-oracle activity")

    def test_every_flutter_item_follows_the_convention(self) -> None:
        for a in _flutter_activities():
            for i in _flutter_samples(a):
                with self.subTest(activity=a.id, prompt=i.prompt):
                    first, _, code = i.prompt.partition("\n")
                    self.assertTrue(first.startswith("// "), "the comment says what to measure")
                    self.assertTrue(code.strip(), "then the widget expression")
                    self.assertFalse(code.rstrip().endswith(";"), "an expression, not a statement")
                    self.assertTrue(i.check.strip(), "the measurement the oracle evaluates")
                    self.assertNotIn("$", i.explain)

    def test_the_flutter_layout_pack_is_eight_dart_only_activities(self) -> None:
        if "pack_flutterlayout" not in brain.PACKS:
            self.skipTest("no flutter layout pack")
        from code_coach.brain import pack_flutterlayout

        self.assertEqual([a.id for a in pack_flutterlayout.ACTIVITIES], [
            "fl_flex", "fl_padding", "fl_main", "fl_cross", "fl_tight", "fl_stack", "fl_wrap", "fl_overflow"])
        for a in pack_flutterlayout.ACTIVITIES:
            self.assertEqual(a.languages, ("dart",), a.id)
            self.assertEqual(a.group, "Flutter layout")
            self.assertEqual(a.oracle, FLUTTER_MODE)
            self.assertGreaterEqual(len(a.make_dart.templates), 30, a.id)
        for language in ("python", "javascript"):
            listed = {x["id"] for x in brain.summary(language=language)["activities"]}
            self.assertFalse(listed & {a.id for a in pack_flutterlayout.ACTIVITIES}, language)
        dart = brain.summary(language="dart")
        self.assertIn("Flutter layout", dart["groups"])
        self.assertTrue({a.id for a in pack_flutterlayout.ACTIVITIES} <= {x["id"] for x in dart["activities"]})

    def test_a_round_asks_for_whole_numbers_or_fine_and_overflow(self) -> None:
        for a in _flutter_activities():
            for seed in range(6):
                for i in make_round(a.id, seed, "dart"):
                    with self.subTest(activity=a.id, prompt=i.prompt):
                        if a.kind == "pick":
                            self.assertIn(i.answer, a.choices)
                        else:
                            self.assertRegex(i.answer, r"^-?\d+(\.\d+)?$")

    def test_the_host_and_the_helpers_are_explained_in_the_blurb(self) -> None:
        for a in _flutter_activities():
            self.assertIn("400 x 300", a.blurb, a.id)
            self.assertIn("Box(", a.blurb, a.id)


@unittest.skipUnless(flutter_oracle.FLUTTER, "needs flutter")
class FlutterOracleTests(unittest.TestCase):
    """THE ORACLE for every Flutter-widget activity: each template on several seeds plus whole rounds, ALL activities in
    one `flutter test` run (tests/flutter_oracle.py: about 7 s to compile plus ~10 ms an item). A new Flutter pack is
    picked up here with no edit: this goes over the Dart activities whose `oracle` is "flutter"."""

    def test_flutter_answers_are_what_flutter_measures(self) -> None:
        for a_id, pairs in flutter_results().items():
            self.assertGreater(len(pairs), 20, a_id)
            wrong = flutter_wrong(pairs)
            self.assertEqual(wrong[:5], [], f"{a_id} (flutter): {len(wrong)} of {len(pairs)} disagree with Flutter")

    def test_a_wrong_layout_model_fails_the_oracle(self) -> None:
        from dataclasses import replace

        for a_id, pairs in flutter_results().items():
            self.assertEqual(flutter_wrong(pairs), [])
            sabotaged = []
            for i, g in pairs:
                if ACTIVITIES_BY_ID[a_id].kind == "pick":
                    wrong = "overflow" if i.answer == "fine" else "fine"
                else:  # the model "forgets" one pixel of padding, or one flex part
                    wrong = str(int(float(i.answer)) + 1)
                sabotaged.append((replace(i, answer=wrong), g))
            self.assertEqual(len(flutter_wrong(sabotaged)), len(pairs), a_id)

    def test_no_item_hit_a_compile_error_or_a_flutter_error(self) -> None:
        for a_id, pairs in flutter_results().items():
            broken = [(i.prompt, g) for i, g in pairs if g.startswith(("COMPILE ERROR", "ERROR"))]
            self.assertEqual(broken[:3], [], f"{a_id}: {len(broken)} items did not build or measure")

    def test_the_harness_names_what_does_not_compile_and_hides_nothing(self) -> None:
        cases = [
            ("Row(children: [Expanded(flex: 2, child: Box('a')), Expanded(child: Box('b'))])", "w('a')"),
            ("Rwo(children: [Box('a')])", "w('a')"),
            ("Row(children: [Box('a', w: 300), Box('b', w: 300)])", "overflowed"),
            ("Row(children: [Box('a', w: 300), Box('b', w: 300)])", "w('a')"),
            ("Row(children: [Box('a')])", "w('nope')"),
            ("// width of a\nCenter(child: Box('a', w: 100))", "w('a') / 8"),
            ("class Counter extends StatefulWidget {\n  const Counter({super.key});\n  @override\n"
             "  State<Counter> createState() => _S();\n}\nclass _S extends State<Counter> {\n  int n = 0;\n  @override\n"
             "  Widget build(BuildContext c) => GestureDetector(onTap: () => setState(() => n++), child: Text('n$n'));\n}\n"
             "Counter()", "await tester.tap(find.byType(Counter));\nawait tester.pump();\nreturn count(find.text('n1'));"),
            ("class Counter extends StatefulWidget {\n  const Counter({super.key});\n  @override\n"
             "  State<Counter> createState() => _S();\n}\nclass _S extends State<Counter> {\n  @override\n"
             "  Widget build(BuildContext c) => Nope();\n}\nCounter()", "1"),
            ("Box('a')", "w('a')"),
        ]
        got = [r.result() for r in flutter_oracle.run_batch(cases)]
        self.assertEqual(got[0], "266.6666666666667")
        self.assertTrue(got[1].startswith("COMPILE ERROR"), got[1])
        self.assertIn("Rwo", got[1])
        self.assertIn("line 2 of the snippet", got[1], "the message names the line inside the snippet")
        self.assertEqual(got[2], "true", "overflowed is how a check asks about the RenderFlex complaint")
        self.assertTrue(got[3].startswith("ERROR: A RenderFlex overflowed"), got[3])
        self.assertTrue(got[4].startswith("ERROR: Bad state"), got[4])
        self.assertEqual(got[5], "12.5", "a fraction prints the Dart way; a whole number prints as an integer")
        self.assertEqual(got[6], "1", "a prompt with classes is its own library, and a check may tap and pump")
        self.assertTrue(got[7].startswith("COMPILE ERROR"), got[7])
        self.assertIn("Nope", got[7])
        self.assertEqual(got[8], "400", "the root widget gets TIGHT 400 x 300 constraints")
        self.assertEqual(len([g for g in got if g.startswith("COMPILE ERROR")]), 2, "only the two broken items fail")


# ── C: held to the real compilers, in ONE batch for every C activity ────

#: C compiles are the dear ones (a complete program is its own translation unit), so fewer samples than the others:
#: every template on 6 seeds plus 12 whole rounds, ALL C activities together in one batch (tests/c_oracle.py).
C_TEMPLATE_SEEDS = range(6)
C_ROUND_SEEDS = range(12)


def _c_samples(activity) -> list:
    seen: dict[str, object] = {}
    for seed in C_ROUND_SEEDS:
        for item in make_round(activity.id, seed, "c"):
            seen.setdefault(item.prompt + "\x00" + item.check, item)
    for template in getattr(activity_for(activity.id, "c").make, "templates", ()):
        for seed in C_TEMPLATE_SEEDS:
            item = template(random.Random(seed))
            seen.setdefault(item.prompt + "\x00" + item.check, item)
    return list(seen.values())


_C_RESULTS: dict | None = None


def c_results() -> dict:
    """{activity id: [(item, Checked)]} for EVERY C activity: one batch through every build (value and warnings), made once
    per test process and shared by the tests below."""
    global _C_RESULTS
    if _C_RESULTS is None:
        samples = {a.id: _c_samples(a) for a in activities_in("c")}
        flat = [(a_id, i) for a_id, items in samples.items() for i in items]
        got = c_oracle.check_items([i.check or i.prompt for _, i in flat])
        out: dict[str, list] = {a_id: [] for a_id in samples}
        for (a_id, i), g in zip(flat, got):
            out[a_id].append((i, g))
        _C_RESULTS = out
    return _C_RESULTS


_C_UB: dict | None = None


def c_undefined() -> dict:
    """{(activity id, prompt): the undefined behaviour the sanitizer found} - one sanitized batch, made once."""
    global _C_UB
    if _C_UB is None:
        flat = [(a_id, i) for a_id, pairs in c_results().items() for i, _ in pairs]
        found = c_oracle.ub_findings([i.check or i.prompt for _, i in flat])
        _C_UB = {(flat[k][0], flat[k][1].prompt): why for k, why in found.items()}
    return _C_UB


class CShapeTests(unittest.TestCase):
    """What needs no compiler: how the C Core Pack is wired and what its items look like."""

    def test_the_c_core_pack_is_eight_c_only_activities_with_many_templates(self) -> None:
        if "pack_ccore" not in brain.PACKS:
            self.skipTest("no C core pack")
        from code_coach.brain import pack_ccore

        self.assertEqual([a.id for a in pack_ccore.ACTIVITIES], [
            "c_int", "c_printf", "c_string", "c_bits", "c_loop", "c_array", "c_order", "c_scope"])
        for a in pack_ccore.ACTIVITIES:
            self.assertEqual(a.languages, ("c",), a.id)
            self.assertEqual(a.group, "C core")
            self.assertEqual(a.oracle, "value")
            self.assertGreaterEqual(len(a.make_c.templates), 40, a.id)
        self.assertEqual(brain.check_for("c"), ("c_int", "c_printf", "c_loop"))

    def test_a_c_activity_is_listed_under_c_alone(self) -> None:
        c_only = [a.id for a in ACTIVITIES if a.languages == ("c",)]
        self.assertTrue(c_only)
        for language in ("python", "javascript", "dart", "sql"):
            listed = {x["id"] for x in brain.summary(language=language)["activities"]}
            self.assertFalse(listed & set(c_only), language)
        in_c = brain.summary(language="c")
        self.assertEqual({x["id"] for x in in_c["activities"]}, {a.id for a in activities_in("c")})
        self.assertTrue(set(brain.check_for("c")) <= {x["id"] for x in in_c["activities"]})

    def test_a_c_item_follows_the_item_convention(self) -> None:
        # headers are never the item's own; the program prints its answer; the answer starts and ends with something visible
        for a in activities_in("c"):
            for i in _c_samples(a):
                with self.subTest(activity=a.id, prompt=i.prompt):
                    program = i.check or i.prompt
                    self.assertIn("printf", program, "a C item prints its own answer")
                    self.assertEqual(c_oracle.lint(program), "", "something that can differ between machines")
                    full = c_oracle.full_program(program)
                    self.assertTrue(full.startswith(c_oracle.HEADERS))
                    self.assertRegex(full, r"\bmain\s*\(")
                    self.assertEqual(i.answer, i.answer.strip())

    def test_the_four_headers_are_the_ones_run_it_adds(self) -> None:
        ts = (WEB / "src" / "lib" / "brainRound.ts").read_text(encoding="utf-8")
        shown = re.search(r'C_HEADERS = "(.*?)";', ts).group(1)
        self.assertEqual(shown.encode().decode("unicode_escape"), c_oracle.HEADERS)

    def test_isolate_makes_file_level_names_static_so_two_programs_can_share_them(self) -> None:
        code = "int total = 0;\nconst int k[2] = {1, 2};\nint next(void) {\n    static int n;\n    return ++n;\n}\nint main(void) {\n    return 0;\n}"
        out = c_oracle.isolate(code)
        self.assertIn("static int total = 0;", out)
        self.assertIn("static const int k[2]", out)
        self.assertIn("static int next(void) {", out)
        self.assertIn("    static int n;", out, "a local is untouched")
        self.assertIn("int main(void) {\n    return 0;\n}", out)
        self.assertNotIn("static int main", out)
        self.assertEqual(c_oracle.isolate("struct P {\n    int x;\n};\nint main(void) {\n    struct P p = {1};\n    return p.x;\n}").count("static"), 0)
        # main gets the `return 0;` that its renamed twin needs
        self.assertIn("return 0;", c_oracle.isolate("int main(void) {\n    puts(\"x\");\n}"))


@unittest.skipUnless(c_oracle.HAVE_COMPILER, "needs a C compiler (clang, gcc or Visual Studio)")
class COracleTests(unittest.TestCase):
    """THE ORACLE for every C activity: each template on several seeds plus whole rounds, ALL C activities in one batch
    through every build (tests/c_oracle.py). A new C pack is picked up here with no edit: this goes over
    `activities_in("c")`."""

    def test_c_answers_are_what_the_real_compilers_print_on_every_build(self) -> None:
        for a_id, pairs in c_results().items():
            self.assertGreater(len(pairs), 20, a_id)
            wrong = [(i.prompt, i.answer, g.value) for i, g in pairs if g.value != i.answer]
            self.assertEqual(wrong[:5], [], f"{a_id} (c): {len(wrong)} of {len(pairs)} disagree with the compilers")

    def test_every_c_build_really_took_part(self) -> None:
        names = {b.name for b in c_oracle.DEFAULT_BUILDS}
        self.assertGreaterEqual(len(names), 2, "at least -O0 and -O2/unsigned char")
        if c_oracle.VCVARS:
            self.assertIn("msvc /Od", names)
        any_pair = next(iter(c_results().values()))[0][1]
        self.assertEqual(set(any_pair.builds), names)

    def test_c_items_trigger_only_harmless_warnings(self) -> None:
        for a_id, pairs in c_results().items():
            bad = [(i.prompt, c_oracle.bad_warnings(g.warnings)) for i, g in pairs if c_oracle.bad_warnings(g.warnings)]
            self.assertEqual(bad[:5], [], f"{a_id}: {len(bad)} items trigger a warning that smells of undefined behaviour")

    @unittest.skipUnless(c_oracle.sanitizer_available(), "needs clang for the sanitizer")
    def test_the_undefined_behaviour_sanitizer_finds_nothing(self) -> None:
        self.assertEqual(sorted(c_undefined().items())[:5], [])


@unittest.skipUnless(c_oracle.HAVE_COMPILER, "needs a C compiler (clang, gcc or Visual Studio)")
class COracleSelfTests(unittest.TestCase):
    """The C oracle is held to account: a wrong model fails it, a broken item is named, one item cannot hide the rest."""

    def test_a_wrong_c_model_fails_the_oracle(self) -> None:
        from dataclasses import replace

        pairs = c_results()["c_int"][:30] + c_results()["c_printf"][:30]
        self.assertEqual([i.prompt for i, g in pairs if g.value != i.answer], [])
        # sabotage: the model says / rounds down for negatives, that a uint8_t does not wrap, ... (every answer one off)
        sabotaged = [replace(i, answer=str(int(i.answer) + 1) if i.answer.lstrip("-").isdigit() else i.answer + "?") for i, _ in pairs]
        wrong = [i for i, (_, g) in zip(sabotaged, pairs) if g.value != i.answer]
        self.assertGreater(len(wrong), 40, "the oracle must notice wrong answers")

    def test_an_item_that_does_not_compile_is_named_by_file_and_line_and_hides_nothing(self) -> None:
        programs = ['printf("%d\\n", 1 + 1);', 'int x = ;\nprintf("%d\\n", x);', 'printf("fine\\n");',
                    'int a = 3;\nprintf("%d\\n", a +* 2);', 'printf("%d\\n", 7 / 2);']
        got = c_oracle.run_batch(programs)
        self.assertEqual([r.value() for r in got][::2], ["2", "fine", "3"])
        self.assertIn("line 1 of the item", got[1].compile_error, "the message names the line inside the item")
        self.assertIn("line 2 of the item", got[3].compile_error)
        self.assertTrue(got[1].value().startswith("COMPILE ERROR"))
        checked = c_oracle.check_items(programs)
        self.assertTrue(checked[1].value.startswith("COMPILE ERROR") or checked[1].value.startswith("BUILDS DIFFER"))

    def test_a_crash_or_a_hang_names_the_item_and_the_rest_still_run(self) -> None:
        programs = ['printf("a\\n");', 'int *p = NULL;\nprintf("%d\\n", *p);', 'printf("b\\n");', 'for (;;) {\n}', 'printf("c\\n");']
        old = c_oracle.RUN_SECONDS
        c_oracle.RUN_SECONDS = 3.0
        try:
            got = c_oracle.run_batch(programs, c_oracle.DEFAULT_BUILDS[0])
        finally:
            c_oracle.RUN_SECONDS = old
        self.assertEqual([r.output.strip() if r.output is not None else None for r in got], ["a", None, "b", None, "c"])
        self.assertIn("crashed", got[1].stopped)
        self.assertIn("ran for too long", got[3].stopped)

    def test_builds_that_disagree_are_reported_by_name(self) -> None:
        # plain char holding 200 is -56 on one build and 200 on the other: not portable, so not an answer
        got = c_oracle.check_items(['char c = 200;\nprintf("%d\\n", c);'])
        self.assertTrue(got[0].value.startswith("BUILDS DIFFER"), got[0].value)
        self.assertIn("-56", got[0].value)

    def test_two_complete_programs_may_declare_the_same_names(self) -> None:
        programs = ['int counter(void) {\n    static int n = 0;\n    return ++n;\n}\nint main(void) {\n    counter();\n    printf("%d\\n", counter());\n}',
                    'int counter(void) {\n    static int n = 10;\n    return ++n;\n}\nint main(void) {\n    printf("%d\\n", counter());\n}',
                    'int total = 5;\nint main(void) {\n    printf("%d\\n", total);\n}',
                    'int total = 7;\nint main(void) {\n    printf("%d\\n", total);\n}',
                    'printf("body\\n");']
        self.assertEqual(c_oracle.c_values(programs), ["2", "11", "5", "7", "body"])

    @unittest.skipUnless(c_oracle.sanitizer_available(), "needs clang for the sanitizer")
    def test_the_sanitizer_names_the_item_that_does_something_undefined(self) -> None:
        programs = ['printf("%d\\n", 1);', 'int a = 2147483647;\nprintf("%d\\n", a + 1);', 'int x = 3;\nprintf("%d\\n", x << 40);']
        found = c_oracle.ub_findings(programs)
        self.assertEqual(sorted(found), [1, 2])
        self.assertIn("signed integer overflow", found[1])
        self.assertIn("line 2 of the item", found[1])

    def test_the_lint_refuses_what_differs_between_machines(self) -> None:
        for bad in ('printf("%p\\n", (void *)0);', "int r = rand();", "char c = 200;", '#include <stdlib.h>\nint x = 1;'):
            self.assertTrue(c_oracle.lint(bad), bad)
        self.assertEqual(c_oracle.lint('printf("%d\\n", 1);'), "")


# ── SQL: held to the real SQLite, one fresh in-memory database per item ─

class SqlShapeTests(unittest.TestCase):
    def test_the_sql_core_pack_is_eight_sql_only_activities_with_many_templates(self) -> None:
        if "pack_sqlcore" not in brain.PACKS:
            self.skipTest("no SQL core pack")
        from code_coach.brain import pack_sqlcore

        self.assertEqual([a.id for a in pack_sqlcore.ACTIVITIES], [
            "sql_count", "sql_null", "sql_group", "sql_join", "sql_order", "sql_scalar", "sql_case", "sql_window"])
        for a in pack_sqlcore.ACTIVITIES:
            self.assertEqual(a.languages, ("sql",), a.id)
            self.assertEqual(a.group, "SQL core")
            self.assertEqual(a.oracle, "value")
            self.assertGreaterEqual(len(a.make_sql.templates), 40, a.id)
        self.assertEqual(brain.check_for("sql"), ("sql_count", "sql_null", "sql_scalar"))

    def test_a_sql_activity_is_listed_under_sql_alone(self) -> None:
        sql_only = [a.id for a in ACTIVITIES if a.languages == ("sql",)]
        self.assertTrue(sql_only)
        for language in ("python", "javascript", "dart", "c"):
            listed = {x["id"] for x in brain.summary(language=language)["activities"]}
            self.assertFalse(listed & set(sql_only), language)
        in_sql = brain.summary(language="sql")
        self.assertEqual({x["id"] for x in in_sql["activities"]}, {a.id for a in activities_in("sql")})
        self.assertTrue(set(brain.check_for("sql")) <= {x["id"] for x in in_sql["activities"]})

    def test_a_sql_item_is_a_whole_script_that_ends_in_a_query(self) -> None:
        for a in activities_in("sql"):
            for i in _samples(a, "sql"):
                with self.subTest(activity=a.id, prompt=i.prompt):
                    program = i.check or i.prompt
                    last = program.rstrip().split("\n")[-1]
                    self.assertTrue(last.startswith("SELECT"), "the last line is the query")
                    self.assertTrue(program.rstrip().endswith(";"))
                    self.assertFalse(i.answer.startswith(("ERROR", "COMPILE")))


class SqlOracleTests(unittest.TestCase):
    """THE ORACLE for every SQL activity: each template on several seeds plus 40 whole rounds, every script in a fresh
    in-memory SQLite (tests/sql_oracle.py). A new SQL pack is picked up here with no edit: this goes over
    `activities_in("sql")`."""

    def test_sql_answers_are_what_sqlite_returns(self) -> None:
        for a in activities_in("sql"):
            items = _samples(a, "sql")
            self.assertGreater(len(items), 20, a.id)
            got = sql_oracle.sql_values([i.check or i.prompt for i in items])
            wrong = [(i.prompt, i.answer, g) for i, g in zip(items, got) if g != i.answer]
            self.assertEqual(wrong[:5], [], f"{a.id} (sql): {len(wrong)} of {len(items)} disagree with SQLite")

    def test_the_in_process_oracle_prints_what_the_real_driver_prints(self) -> None:
        # the driver is what "Run it" uses: a handful of items from every activity through it, one process each
        picks = []
        for a in activities_in("sql"):
            picks.extend(_samples(a, "sql")[:3])
        self.assertGreater(len(picks), 20)
        for i in picks:
            program = i.check or i.prompt
            self.assertEqual(sql_oracle.driver_value(program), sql_oracle.run_sql(program), program)
            self.assertEqual(sql_oracle.driver_value(program), i.answer, program)

    def test_the_answer_format_is_the_drivers(self) -> None:
        run = sql_oracle.run_sql
        self.assertEqual(run("SELECT 7 / 2, 7 / 2.0, NULL, 'x';"), "3|3.5|NULL|x")
        self.assertEqual(run("SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT NULL;"), "1; 2; NULL")
        self.assertEqual(run("SELECT 0.1 + 0.2;"), "0.30000000000000004")
        self.assertEqual(run("CREATE TABLE t(a); SELECT a FROM t;"), "", "no rows prints nothing")
        self.assertEqual(run("CREATE TABLE t(a); INSERT INTO t VALUES (1); SELECT a FROM t; SELECT 5;"), "5", "the LAST SELECT")
        self.assertTrue(run("SELECT nope FROM nowhere;").startswith("ERROR: "))


class SqlOracleSelfTests(unittest.TestCase):
    def test_a_wrong_sql_model_fails_the_oracle(self) -> None:
        from dataclasses import replace

        a = ACTIVITIES_BY_ID["sql_scalar"]
        items = _samples(a, "sql")[:60]
        self.assertEqual([i.prompt for i, g in zip(items, sql_oracle.sql_values([i.prompt for i in items])) if g != i.answer], [])
        # sabotage: the model says SQL divides integers like Python's / (a real), and that NULL sorts last
        sabotaged = [replace(i, answer=str(float(i.answer)) if i.answer.lstrip("-").isdigit() else i.answer + "!") for i in items]
        wrong = [1 for i, g in zip(sabotaged, sql_oracle.sql_values([i.prompt for i in sabotaged])) if g != i.answer]
        self.assertGreater(len(wrong), 30, "the oracle must notice wrong answers")

    def test_every_item_runs_in_its_own_database(self) -> None:
        got = sql_oracle.sql_values(["CREATE TABLE t(a); INSERT INTO t VALUES (1); SELECT COUNT(*) FROM t;",
                                     "CREATE TABLE t(a); SELECT COUNT(*) FROM t;"])
        self.assertEqual(got, ["1", "0"], "the second script sees an empty t: nothing leaks from the first")


# ── Per-language code age, history and the routes ───────────────────────

class DartHistoryTests(unittest.TestCase):
    def test_an_old_history_file_without_a_dart_key_still_loads(self) -> None:
        import json as _json
        from datetime import date

        path = brain.save_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        old = [{"day": "2026-10-01", "activity": "eval", "seconds": 50.0, "errors": 1, "total": 20, "age": 40, "check_id": ""},
               {"day": "2026-10-02", "activity": "eval", "seconds": 40.0, "errors": 0, "total": 20, "age": 30, "check_id": "",
                "language": "python"}]
        path.write_text(_json.dumps({"results": old}), encoding="utf-8")
        d = brain.summary(today=date(2026, 10, 2), language="dart")
        self.assertTrue(all(a["best"] is None and a["last"] is None for a in d["activities"]))
        self.assertEqual(d["streak"], 2, "training in any language counts toward the streak")
        self.assertEqual(d["checkAges"], [])
        self.assertEqual(brain.summary(today=date(2026, 10, 2))["activities"][0]["best"]["age"], 40)
        # the first Dart round puts "dart" into the file, and nothing else moves
        brain.record("dart_eval", 40, 0, 20, today=date(2026, 10, 3), language="dart")
        stored = _json.loads(path.read_text(encoding="utf-8"))["results"]
        self.assertEqual([r.get("language", "javascript") for r in stored], ["javascript", "python", "dart"])
        self.assertEqual(brain.summary(today=date(2026, 10, 3), language="python")["activities"][0]["best"]["age"], 30)

    def test_dart_results_are_kept_per_language_like_the_others(self) -> None:
        from datetime import date

        day = date(2026, 10, 5)
        brain.record("dart_eval", 100, 2, 20, today=day, language="dart")
        brain.record("dart_eval", 40, 0, 20, today=day, language="dart")
        entry = next(a for a in brain.summary(today=day, language="dart")["activities"] if a["id"] == "dart_eval")
        self.assertEqual(entry["best"]["seconds"], 40)
        self.assertEqual(entry["last"]["seconds"], 40)
        self.assertEqual(entry["best"]["language"], "dart")
        for other in ("python", "javascript"):
            self.assertNotIn("dart_eval", {a["id"] for a in brain.summary(today=day, language=other)["activities"]})
        self.assertLess(brain.code_age("dart_eval", 40, 0, 20, "dart"), brain.code_age("dart_eval", 100, 2, 20, "dart"))

    def test_each_language_has_its_own_check_trio_and_its_own_check_ages(self) -> None:
        from datetime import date

        self.assertEqual(brain.check_for("python"), CHECK)
        self.assertEqual(brain.check_for("javascript"), CHECK)
        dart_check = brain.check_for("dart")
        self.assertEqual(len(dart_check), 3)
        self.assertNotEqual(dart_check, CHECK)
        self.assertTrue(all(ACTIVITIES_BY_ID[x].languages == ("dart",) for x in dart_check))
        self.assertEqual(brain.CHECK, ("eval", "truthy", "brackets"), "Python's and JavaScript's check is unchanged")
        with self.assertRaises(KeyError):
            brain.check_for("cobol")
        day = date(2026, 10, 6)
        for activity_id in dart_check[:2]:  # an unfinished Dart check has no age
            brain.record(activity_id, 30, 1, ACTIVITIES_BY_ID[activity_id].count, check_id="2026-10-06/d", today=day,
                         language="dart")
        self.assertEqual(brain.summary(today=day, language="dart")["checkAges"], [])
        brain.record(dart_check[2], 30, 1, ACTIVITIES_BY_ID[dart_check[2]].count, check_id="2026-10-06/d", today=day,
                     language="dart")
        self.assertEqual([c["day"] for c in brain.summary(today=day, language="dart")["checkAges"]], ["2026-10-06"])
        self.assertEqual(brain.summary(today=day, language="python")["checkAges"], [], "a Dart check is not a Python one")
        self.assertEqual(brain.summary(today=day, language="dart")["check"], list(dart_check))
        self.assertEqual(brain.summary(today=day, language="python")["check"], list(CHECK))
        # a Python trio recorded under the same check id does not complete a Dart check, and vice versa
        for activity_id in CHECK:
            brain.record(activity_id, 30, 1, ACTIVITIES_BY_ID[activity_id].count, check_id="2026-10-06/p", today=day,
                         language="python")
        self.assertEqual([c["day"] for c in brain.summary(today=day, language="python")["checkAges"]], ["2026-10-06"])

    def test_the_routes_know_dart(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.schemas import BrainResultRequest
        from code_coach.api.server import brain_result, brain_round, brain_summary

        s = brain_summary("dart")
        self.assertEqual(s["language"], "dart")
        self.assertEqual({a["id"] for a in s["activities"]}, {a.id for a in activities_in("dart")})
        self.assertIn("Dart core", s["groups"])
        self.assertEqual(set(s["groups"]), {a.group for a in activities_in("dart")}, "exactly the groups of the Dart activities")
        self.assertEqual(len(s["groups"]), len(set(s["groups"])))
        self.assertEqual(s["check"], list(brain.check_for("dart")))
        r = brain_round("dart_eval", 3, "dart")
        self.assertEqual((r["language"], len(r["items"])), ("dart", ACTIVITIES_BY_ID["dart_eval"].count))
        for bad_language in ("python", "javascript"):
            with self.assertRaises(HTTPException) as caught:
                brain_round("dart_eval", 3, bad_language)
            self.assertEqual(caught.exception.status_code, 404)
        with self.assertRaises(HTTPException):
            brain_round("eval", 3, "dart")  # a Python/JavaScript activity with no Dart version
        got = brain_result(BrainResultRequest(activity="dart_null", seconds=40, errors=0, total=16, language="dart"))
        self.assertTrue(got["best"])
        with self.assertRaises(HTTPException):
            brain_result(BrainResultRequest(activity="dart_null", seconds=40, errors=0, total=16, language="python"))
        with self.assertRaises(HTTPException):
            brain_result(BrainResultRequest(activity="eval", seconds=40, errors=0, total=20, language="dart"))

    def test_explain_reads_dart_and_the_dart_words_come_first(self) -> None:
        # Dart has a reader (code_coach/explain_dart.py) and is a glossary language: the words of the activity come back first.
        from code_coach.api import server
        from code_coach.api.schemas import ExplainRequest

        reply = server.explain(ExplainRequest(code="print(1 + 1);", language="dart", context="dart_eval"))
        self.assertTrue(reply.ok)
        self.assertTrue(reply.lines, "the code is read line by line")
        self.assertTrue(reply.words, "Dart is a glossary language: the context's words come back")
        self.assertEqual(reply.words[0].language, "dart")
        self.assertEqual(reply.words[0].id, "expression")
        ctx = server.glossary_words(language="dart", context="dart_eval").words
        self.assertTrue(ctx and ctx[0].id == "expression")

    @unittest.skipUnless(dart_oracle.DART, "needs dart")
    def test_run_it_runs_a_dart_snippet_for_real(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.schemas import BrainRunRequest
        from code_coach.api.server import brain_run

        ok = brain_run(BrainRunRequest(code=dart_oracle.full_program("7 ~/ 2")))
        self.assertTrue(ok["ok"])
        self.assertEqual(ok["stdout"], "3")
        self.assertIsNone(ok["error"])
        boom = brain_run(BrainRunRequest(code="void main() {\n  var xs = [1];\n  print(xs[3]);\n}"))
        self.assertFalse(boom["ok"])
        self.assertIn("RangeError", boom["error"])
        bad = brain_run(BrainRunRequest(code="void main() {\n  final x = 1;\n  x = 2;\n}"))
        self.assertTrue(bad["compile_error"])
        self.assertIn("final", bad["error"])
        self.assertNotIn("gotcha_run_", bad["error"], "no throwaway folder in the message")
        for code in ("", "x" * 5000):
            with self.assertRaises(HTTPException) as caught:
                brain_run(BrainRunRequest(code=code))
            self.assertEqual(caught.exception.status_code, 400)
        with self.assertRaises(HTTPException):
            brain_run(BrainRunRequest(code="print(1)", language="python"))


class CAndSqlHistoryTests(unittest.TestCase):
    """C and SQL are languages like the others: their rounds are kept per language, lazily, and an old history file loads."""

    def test_an_old_history_file_without_c_or_sql_keys_still_loads_and_the_first_round_adds_the_key(self) -> None:
        import json as _json
        from datetime import date

        path = brain.save_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        old = [{"day": "2026-10-01", "activity": "eval", "seconds": 50.0, "errors": 1, "total": 20, "age": 40, "check_id": ""},
               {"day": "2026-10-02", "activity": "dart_eval", "seconds": 40.0, "errors": 0, "total": 20, "age": 30, "check_id": "",
                "language": "dart"}]
        path.write_text(_json.dumps({"results": old}), encoding="utf-8")
        for language in ("c", "sql"):
            s = brain.summary(today=date(2026, 10, 2), language=language)
            self.assertTrue(all(a["best"] is None and a["last"] is None for a in s["activities"]), language)
            self.assertEqual(s["streak"], 2, "training in any language counts toward the streak")
            self.assertEqual(s["checkAges"], [])
        brain.record("c_int", 40, 0, 16, today=date(2026, 10, 3), language="c")
        brain.record("sql_count", 40, 0, 10, today=date(2026, 10, 3), language="sql")
        stored = _json.loads(path.read_text(encoding="utf-8"))["results"]
        self.assertEqual([r.get("language", "javascript") for r in stored], ["javascript", "dart", "c", "sql"])
        self.assertEqual(brain.summary(today=date(2026, 10, 3), language="dart")["activities"][0]["best"]["age"], 30)

    def test_c_and_sql_results_are_kept_per_language_like_the_others(self) -> None:
        from datetime import date

        day = date(2026, 10, 5)
        for language, activity, count in (("c", "c_int", 16), ("sql", "sql_count", 10)):
            brain.record(activity, 100, 2, count, today=day, language=language)
            brain.record(activity, 40, 0, count, today=day, language=language)
            entry = next(a for a in brain.summary(today=day, language=language)["activities"] if a["id"] == activity)
            self.assertEqual(entry["best"]["seconds"], 40)
            self.assertEqual(entry["last"]["seconds"], 40)
            self.assertEqual(entry["best"]["language"], language)
            for other in set(LANGS) - {language}:
                self.assertNotIn(activity, {a["id"] for a in brain.summary(today=day, language=other)["activities"]})
            self.assertLess(brain.code_age(activity, 40, 0, count, language), brain.code_age(activity, 100, 2, count, language))
            with self.assertRaises(KeyError):
                brain.code_age(activity, 40, 0, count, "python")

    def test_each_language_has_its_own_check_trio(self) -> None:
        from datetime import date

        day = date(2026, 10, 6)
        for language in ("c", "sql"):
            trio = brain.check_for(language)
            self.assertEqual(len(trio), 3)
            self.assertTrue(all(ACTIVITIES_BY_ID[x].languages == (language,) for x in trio))
            for activity_id in trio[:2]:  # an unfinished check has no age
                brain.record(activity_id, 30, 1, ACTIVITIES_BY_ID[activity_id].count, check_id=f"2026-10-06/{language}",
                             today=day, language=language)
            self.assertEqual(brain.summary(today=day, language=language)["checkAges"], [])
            brain.record(trio[2], 30, 1, ACTIVITIES_BY_ID[trio[2]].count, check_id=f"2026-10-06/{language}", today=day, language=language)
            self.assertEqual([c["day"] for c in brain.summary(today=day, language=language)["checkAges"]], ["2026-10-06"])
            self.assertEqual(brain.summary(today=day, language=language)["check"], list(trio))
        self.assertEqual(brain.summary(today=day, language="dart")["checkAges"], [], "a C or SQL check is not a Dart one")
        self.assertEqual(brain.summary(today=day, language="python")["checkAges"], [])
        self.assertEqual(len({brain.check_for(x) for x in LANGS}), len(LANGS) - 1, "Python and JavaScript share one trio, the rest have their own")

    def test_the_routes_know_c_and_sql(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.schemas import BrainResultRequest
        from code_coach.api.server import brain_result, brain_round, brain_summary

        for language, activity, group in (("c", "c_int", "C core"), ("sql", "sql_count", "SQL core")):
            s = brain_summary(language)
            self.assertEqual(s["language"], language)
            self.assertEqual({a["id"] for a in s["activities"]}, {a.id for a in activities_in(language)})
            self.assertIn(group, s["groups"])
            self.assertEqual(set(s["groups"]), {a.group for a in activities_in(language)})
            self.assertEqual(s["check"], list(brain.check_for(language)))
            r = brain_round(activity, 3, language)
            self.assertEqual((r["language"], len(r["items"])), (language, ACTIVITIES_BY_ID[activity].count))
            for bad_language in set(LANGS) - {language}:
                with self.assertRaises(HTTPException) as caught:
                    brain_round(activity, 3, bad_language)
                self.assertEqual(caught.exception.status_code, 404)
            with self.assertRaises(HTTPException):
                brain_round("eval", 3, language)  # a Python/JavaScript activity with no version in this language
            got = brain_result(BrainResultRequest(activity=activity, seconds=40, errors=0, total=10, language=language))
            self.assertTrue(got["best"])
            with self.assertRaises(HTTPException):
                brain_result(BrainResultRequest(activity=activity, seconds=40, errors=0, total=10, language="python"))
            with self.assertRaises(HTTPException):
                brain_result(BrainResultRequest(activity="eval", seconds=40, errors=0, total=20, language=language))
        with self.assertRaises(HTTPException):
            brain_summary("cobol")

    def test_run_it_runs_a_sql_script_for_real(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.schemas import BrainRunRequest
        from code_coach.api.server import brain_run

        ok = brain_run(BrainRunRequest(code="CREATE TABLE t(a INT);\nINSERT INTO t VALUES (1),(NULL),(3);\nSELECT COUNT(a), AVG(a) FROM t;",
                                       language="sql"))
        self.assertTrue(ok["ok"])
        self.assertEqual(ok["stdout"], "2|2.0")
        self.assertIsNone(ok["error"])
        bad = brain_run(BrainRunRequest(code="SELECT nope FROM nowhere;", language="sql"))
        self.assertFalse(bad["ok"])
        self.assertIn("no such table", bad["error"])
        for code in ("", "x" * 5000):
            with self.assertRaises(HTTPException) as caught:
                brain_run(BrainRunRequest(code=code, language="sql"))
            self.assertEqual(caught.exception.status_code, 400)

    @unittest.skipUnless(c_oracle.HAVE_COMPILER, "needs a C compiler")
    def test_run_it_runs_a_c_program_for_real(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.schemas import BrainRunRequest
        from code_coach.api.server import brain_run

        ok = brain_run(BrainRunRequest(code=c_oracle.full_program('printf("%d\\n", -7 / 2);'), language="c"))
        self.assertTrue(ok["ok"], ok)
        self.assertEqual(ok["stdout"], "-3")
        self.assertIsNone(ok["error"])
        broken = brain_run(BrainRunRequest(code=c_oracle.full_program('int x = ;\nprintf("%d\\n", x);'), language="c"))
        self.assertFalse(broken["ok"])
        self.assertTrue(broken["compile_error"])
        self.assertIn("error", broken["error"])
        self.assertNotIn("gotcha_run_", broken["error"], "no throwaway folder in the message")
        self.assertIn("snippet.c", broken["error"])
        crash = brain_run(BrainRunRequest(code=c_oracle.full_program("int *p = NULL;\nprintf(\"%d\\n\", *p);"), language="c"))
        self.assertFalse(crash["ok"])
        for code in ("", "x" * 5000):
            with self.assertRaises(HTTPException) as caught:
                brain_run(BrainRunRequest(code=code, language="c"))
            self.assertEqual(caught.exception.status_code, 400)

    def test_run_it_refuses_the_languages_that_have_the_tracer(self) -> None:
        from fastapi import HTTPException

        from code_coach.api.schemas import BrainRunRequest
        from code_coach.api.server import brain_run

        for language in ("python", "javascript", "go", ""):
            with self.assertRaises(HTTPException) as caught:
                brain_run(BrainRunRequest(code="print(1)", language=language))
            self.assertEqual(caught.exception.status_code, 400, language)

    def test_the_explain_words_of_a_c_or_sql_drill_are_its_glossary_words_and_nothing_breaks(self) -> None:
        # C and SQL have glossaries (code_coach/glossary/terms_c_*.py, terms_sql_*.py): the chips show the activity's words
        from code_coach.api import server

        for language, context, first in (("c", "c_int", "integer"), ("sql", "sql_count", "where-clause")):
            words = server.glossary_words(language=language, context=context).words
            self.assertTrue(words, (language, context))
            self.assertEqual(words[0].id, first)
            self.assertTrue(all(w.language == language for w in words))
        self.assertEqual(server.glossary_words(language="postgresql", context="sql_count").words, [])


if __name__ == "__main__":
    unittest.main()


# ── TypeScript and Rust: held to `tsc --strict` + node and to rustc (debug and -O), in batches ───────

TYPED_TEMPLATE_SEEDS = range(5)
TYPED_ROUND_SEEDS = range(10)


def _typed_samples(activity, language: str) -> list:
    seen: dict[str, object] = {}
    for seed in TYPED_ROUND_SEEDS:
        for item in make_round(activity.id, seed, language):
            seen.setdefault(item.prompt + "\x00" + item.check, item)
    for template in getattr(activity_for(activity.id, language).make, "templates", ()):
        for seed in TYPED_TEMPLATE_SEEDS:
            item = template(random.Random(seed))
            seen.setdefault(item.prompt + "\x00" + item.check, item)
    return list(seen.values())


_TYPED: dict[str, dict] = {}


def typed_results(language: str) -> dict:
    """{activity id: [(item, run)]} for EVERY activity of TypeScript or Rust, in one batch per language, made once per
    test process."""
    if language not in _TYPED:
        samples = {a.id: _typed_samples(a, language) for a in activities_in(language)}
        flat = [(a_id, i) for a_id, items in samples.items() for i in items]
        run = ts_oracle.ts_results if language == "typescript" else rust_oracle.rust_results
        got = run([i.check or i.prompt for _, i in flat])
        out: dict[str, list] = {a_id: [] for a_id in samples}
        for (a_id, i), g in zip(flat, got):
            out[a_id].append((i, g))
        _TYPED[language] = out
    return _TYPED[language]


def _typed_wrong(language: str) -> dict[str, list]:
    wrong = {}
    for a_id, pairs in typed_results(language).items():
        mode = ACTIVITIES_BY_ID[a_id].oracle
        bad = [(i.prompt, i.answer, g.verdict if mode == "error" else g.value) for i, g in pairs
               if (g.verdict if mode == "error" else g.value) != i.answer]
        if bad:
            wrong[a_id] = (len(bad), len(pairs), bad[:3])
    return wrong


class TypedShapeTests(unittest.TestCase):
    """What needs no compiler: how the TypeScript and Rust core packs are wired and what their items look like."""

    PACKS = (("pack_tscore", "typescript", "TypeScript core", "ts_",
              ["ts_eval", "ts_narrow", "ts_compile", "ts_generics", "ts_classes", "ts_arrays", "ts_enum", "ts_null"]),
             ("pack_rustcore", "rust", "Rust core", "rs_",
              ["rs_eval", "rs_own", "rs_borrow", "rs_match", "rs_iter", "rs_string", "rs_struct", "rs_collect"]))

    def test_each_core_pack_is_eight_single_language_activities_with_many_templates(self) -> None:
        import importlib

        for pack, language, group, prefix, ids in self.PACKS:
            with self.subTest(pack=pack):
                if pack not in brain.PACKS:
                    self.skipTest(f"no {pack}")
                acts = importlib.import_module(f"code_coach.brain.{pack}").ACTIVITIES
                self.assertEqual([a.id for a in acts], ids)
                for a in acts:
                    self.assertEqual(a.languages, (language,), a.id)
                    self.assertEqual(a.group, group)
                    self.assertTrue(a.id.startswith(prefix))
                    self.assertIn(a.oracle, TYPED_MODES)
                    if a.oracle == "error":
                        self.assertEqual((a.kind, a.choices), ("pick", ("fine", "error")), a.id)
                    self.assertGreaterEqual(len(a.generator(language).templates), 25, a.id)
                self.assertTrue(set(brain.check_for(language)) <= set(ids))

    def test_a_typescript_or_rust_activity_is_listed_under_its_language_alone(self) -> None:
        for language in ("typescript", "rust"):
            only = [a.id for a in ACTIVITIES if a.languages == (language,)]
            if not only:
                continue
            for other in LANGS:
                if other == language:
                    continue
                listed = {x["id"] for x in brain.summary(language=other)["activities"]}
                self.assertFalse(listed & set(only), (language, other))
            mine = {x["id"] for x in brain.summary(language=language)["activities"]}
            self.assertEqual(mine, {a.id for a in activities_in(language)})
            self.assertTrue(set(brain.check_for(language)) <= mine)

    def test_an_item_prints_its_own_answer(self) -> None:
        for language, printer in (("typescript", "console.log"), ("rust", "println!")):
            for a in activities_in(language):
                for i in _typed_samples(a, language):
                    with self.subTest(activity=a.id, prompt=i.prompt):
                        program = i.check or i.prompt
                        if a.oracle == "value":
                            self.assertIn(printer, program, "an item prints its own answer")
                        self.assertNotIn("$", i.explain)
                        self.assertTrue(i.explain.strip())


@unittest.skipUnless(ts_oracle.HAVE_TSC, "needs node and web/node_modules/typescript")
class TypeScriptOracleTests(unittest.TestCase):
    """THE ORACLE for every TypeScript activity: every template on several seeds plus whole rounds, in ONE `tsc --strict`
    program and one node run (tests/ts_oracle.py). A new TypeScript pack is picked up with no edit."""

    def test_typescript_answers_are_what_tsc_and_node_print(self) -> None:
        if not activities_in("typescript"):
            self.skipTest("no TypeScript activities")
        for a_id, pairs in typed_results("typescript").items():
            self.assertGreater(len(pairs), 20, a_id)
        self.assertEqual(_typed_wrong("typescript"), {})

    def test_a_fine_or_error_round_holds_both_answers_for_real(self) -> None:
        for a_id, pairs in typed_results("typescript").items():
            if ACTIVITIES_BY_ID[a_id].oracle == "error":
                self.assertEqual({g.verdict for _, g in pairs}, {"fine", "error"}, a_id)


@unittest.skipUnless(ts_oracle.HAVE_TSC, "needs node and web/node_modules/typescript")
class TypeScriptOracleSelfTests(unittest.TestCase):
    def test_the_harness_tells_values_compile_errors_throws_and_hangs_apart(self) -> None:
        got = ts_oracle.ts_results([
            "console.log(7 / 2);",
            'const n: number = "a";\nconsole.log(n);',
            'throw new RangeError("nope");',
            "while (true) {}",
            "const xs = [1, 2];\nconsole.log(xs, { a: 'x' });",
            'const name = "a";\nconsole.log(name);',
            "console.log('after');",
        ])
        self.assertEqual(got[0].value, "3.5")
        self.assertFalse(got[1].compiled)
        self.assertIn("TS2322", got[1].value)
        self.assertIn("item1.ts(1,7)", got[1].value, "named by the item's own file and line")
        self.assertEqual((got[2].verdict, got[2].threw), ("error", True))
        self.assertIn("RangeError: nope", got[2].value)
        self.assertEqual(got[3].verdict, "error")
        self.assertIn("HANG", got[3].value)
        self.assertEqual(got[4].value, "[ 1, 2 ] { a: 'x' }", "printed as console.log prints")
        self.assertEqual(got[5].value, "a", "a module: a top-level name never clashes with the DOM library")
        self.assertEqual((got[6].value, got[6].verdict), ("after", "fine"), "the rest still run")

    def test_a_syntax_error_in_one_item_never_hides_a_type_error_in_another(self) -> None:
        # tsc skips every semantic check while any file has a syntax error: the oracle takes those files out first
        got = ts_oracle.ts_results(["console.log(5.toString());", 'const n: number = "a";\nconsole.log(n);',
                                    "console.log(1);"])
        self.assertEqual([g.verdict for g in got], ["error", "error", "fine"])
        self.assertIn("TS2322", got[1].value)

    def test_a_batch_of_thousands_of_files_fits_the_command_line(self) -> None:
        got = ts_oracle.ts_values([f"console.log({k});" for k in range(2500)])
        self.assertEqual(got[2499], "2499")

    def test_two_items_may_declare_the_same_names(self) -> None:
        got = ts_oracle.ts_values(["interface P { x: number }\nconst p: P = { x: 1 };\nconsole.log(p.x);",
                                   "interface P { x: string }\nconst p: P = { x: 'q' };\nconsole.log(p.x);"])
        self.assertEqual(got, ["1", "q"])

    def test_a_wrong_model_fails_the_oracle(self) -> None:
        self.assertNotEqual(ts_oracle.ts_values(["console.log([10, 9, 1].sort());"])[0], "[ 1, 9, 10 ]",
                            "the default sort compares strings")


@unittest.skipUnless(rust_oracle.HAVE_RUSTC, "needs rustc")
class RustOracleTests(unittest.TestCase):
    """THE ORACLE for every Rust activity: every template on several seeds plus whole rounds, in crates built debug AND -O
    (tests/rust_oracle.py), which must agree. A new Rust pack is picked up with no edit."""

    def test_rust_answers_are_what_rustc_builds_print(self) -> None:
        if not activities_in("rust"):
            self.skipTest("no Rust activities")
        for a_id, pairs in typed_results("rust").items():
            self.assertGreater(len(pairs), 20, a_id)
        self.assertEqual(_typed_wrong("rust"), {})

    def test_a_fine_or_error_round_holds_both_answers_for_real(self) -> None:
        for a_id, pairs in typed_results("rust").items():
            if ACTIVITIES_BY_ID[a_id].oracle == "error":
                self.assertEqual({g.verdict for _, g in pairs}, {"fine", "error"}, a_id)

    def test_no_value_item_differs_between_debug_and_release(self) -> None:
        differ = [(a_id, i.prompt) for a_id, pairs in typed_results("rust").items() for i, g in pairs
                  if g.value.startswith("BUILDS DIFFER")]
        self.assertEqual(differ[:5], [])


@unittest.skipUnless(rust_oracle.HAVE_RUSTC, "needs rustc")
class RustOracleSelfTests(unittest.TestCase):
    def test_the_harness_tells_values_borrow_errors_panics_overflow_and_hangs_apart(self) -> None:
        got = rust_oracle.rust_results([
            'println!("{}", -7 / 2);',
            'let s = String::from("a");\nlet t = s;\nprintln!("{}", s);',
            'let v: Vec<i32> = Vec::new();\nprintln!("{}", v[3]);',
            'let mut x: u8 = 250;\nx += std::hint::black_box(10u8);\nprintln!("{}", x);',
            "loop {}",
            'struct P { x: i32 }\nfn main() {\n    println!("{}", P { x: 4 }.x);\n}',
            'struct P { x: f64 }\nfn main() {\n    println!("{:?}", P { x: 2.0 }.x);\n}',
            'println!("after");',
        ])
        self.assertEqual(got[0].value, "-3")
        self.assertFalse(got[1].compiled)
        self.assertIn("E0382", got[1].value, "the borrow checker ran")
        self.assertTrue(got[2].panicked)
        self.assertIn("index out of bounds", got[2].value)
        self.assertTrue(got[3].value.startswith("BUILDS DIFFER"), "debug panics on overflow, -O wraps")
        self.assertEqual(got[4].value, "HANG")
        self.assertEqual(got[5].value, "4")
        self.assertEqual(got[6].value, "2.0", "two programs may both declare struct P")
        self.assertEqual((got[7].value, got[7].verdict), ("after", "fine"), "the rest still run")

    def test_an_error_only_the_real_build_finds_is_a_compile_error_not_a_crash(self) -> None:
        # unconditional_panic is a deny lint raised in code generation, after `--emit=metadata` said yes
        got = rust_oracle.rust_results(["let a = [1, 2, 3];\nprintln!(\"{}\", a[5]);", 'println!("{}", 3);'])
        self.assertFalse(got[0].compiled)
        self.assertEqual((got[0].verdict, got[1].value), ("error", "3"))

    def test_an_item_the_batch_refuses_is_judged_on_its_own(self) -> None:
        # a type error in one item never makes its neighbour fail
        got = rust_oracle.rust_results(['let x: i32 = "a";\nprintln!("{}", x);', 'println!("{}", 1 + 1);'])
        self.assertEqual((got[0].verdict, got[1].value), ("error", "2"))

    def test_a_wrong_model_fails_the_oracle(self) -> None:
        self.assertNotEqual(rust_oracle.rust_values(['println!("{}", "h\\u{e9}".len());'])[0], "2", "len() counts bytes")


class TypedRunItTests(unittest.TestCase):
    @unittest.skipUnless(ts_oracle.HAVE_TSC, "needs tsc")
    def test_run_it_runs_a_typescript_program_for_real(self) -> None:
        from code_coach.api.schemas import BrainRunRequest
        from code_coach.api.server import brain_run

        ok = brain_run(BrainRunRequest(code=ts_oracle.full_program("const n: number = 7;\nconsole.log(n / 2);"),
                                       language="typescript"))
        self.assertTrue(ok["ok"], ok)
        self.assertEqual(ok["stdout"].strip(), "3.5")
        broken = brain_run(BrainRunRequest(code=ts_oracle.full_program('const n: number = "a";'), language="typescript"))
        self.assertFalse(broken["ok"])
        self.assertTrue(broken["compile_error"])

    @unittest.skipUnless(rust_oracle.HAVE_RUSTC, "needs rustc")
    def test_run_it_runs_a_rust_program_for_real(self) -> None:
        from code_coach.api.schemas import BrainRunRequest
        from code_coach.api.server import brain_run

        ok = brain_run(BrainRunRequest(code=rust_oracle.full_program('let v = vec![1, 2];\nprintln!("{:?}", v);'),
                                       language="rust"))
        self.assertTrue(ok["ok"], ok)
        self.assertEqual(ok["stdout"].strip(), "[1, 2]")
        broken = brain_run(BrainRunRequest(code=rust_oracle.full_program('let s = String::new();\nlet t = s;\nprintln!("{}", s);'),
                                           language="rust"))
        self.assertFalse(broken["ok"])
        self.assertTrue(broken["compile_error"])
