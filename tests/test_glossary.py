"""The glossary ("Words used" under Explain my code): code_coach/glossary and its screen.

Four kinds of test:

* Shape: every entry is well formed (ids, definitions, rules, links, a short definition).
* THE ORACLE: every entry's example is RUN for real (python, node, and dart for the Dart/Flutter words, all of
  them in ONE `dart run` through tests/dart_oracle.py) and must print exactly its `example_output`; every list
  of falsy and truthy values is run through bool() / Boolean(), and the prose rule that lists them is parsed and
  run too. The glossary must never teach something false. The expected values written in this file (the
  "claims") are worked out by hand, not read from the entries. Dart rules are backed by DART_RULE_CHECKS (real
  dart) and the layout/state rules of the Flutter words by FLUTTER_CHECKS (real Flutter, tests/flutter_oracle.py);
  the Flutter rules no test can measure are named in NOT_ORACLE_CHECKED.
* Matching: `find_words` (context words first, detection by code, limit, dedupe, no crash), and
  every Brain Drills activity has its words.
* The wiring: /api/explain gets `words` in one place and old fields are unchanged, /api/glossary,
  the pure front-end rules (web/src/lib/words.ts, bundled with esbuild and run in node) and the
  components that must show the section.
"""

from __future__ import annotations

import functools
import json
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from code_coach import glossary
from code_coach.api import server
from code_coach.api.schemas import ExplainRequest, ExplainResponse
from code_coach.brain import ACTIVITIES
from code_coach.explain import explain_code
from code_coach.glossary import CONTEXTS, find_words, lookup, words_for_context
from tests import dart_oracle, flutter_oracle

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
SRC = WEB / "src"
ESBUILD = WEB / "node_modules" / "esbuild" / "bin" / "esbuild"
NODE = shutil.which("node")

LANGS = glossary.LANGUAGES
#: The two languages the old tests were written for. Truthy/falsy lists, the original seven activities and the
#: terms_brain_* vocabulary exist only there; Dart (and Flutter, which is Dart) has its own tests further down.
CLASSIC = ("python", "javascript")
ENTRIES = [(e.language, e.id) for lang in LANGS for e in glossary.all_entries(lang)]

needs_node = pytest.mark.skipif(NODE is None, reason="needs node")


def entry(language: str, id_: str):
    found = glossary.lookup(language, id_)
    assert found is not None and found.id == id_, (language, id_)
    return found


# ── Shape ───────────────────────────────────────────────────────────────

def test_every_terms_module_imports_cleanly():
    assert glossary.LOAD_ERRORS == {}


@pytest.mark.parametrize("lang", LANGS)
def test_a_language_has_a_real_glossary(lang):
    assert len(glossary.all_entries(lang)) >= 70, "the brief: at least ~70 terms per language"


@pytest.mark.parametrize("lang", LANGS)
def test_ids_are_unique_and_kebab_case(lang):
    ids = [e.id for e in glossary.all_entries(lang)]
    assert len(ids) == len(set(ids))
    for i in ids:
        assert re.fullmatch(r"[a-z]+(?:-[a-z]+)*", i), i


@pytest.mark.parametrize("lang", LANGS)
def test_no_two_words_answer_to_the_same_spelling_unless_they_are_the_same_word(lang):
    """lookup() must be unambiguous for every id and display term (aka spellings may overlap)."""
    for e in glossary.all_entries(lang):
        assert lookup(lang, e.id) is e
        assert lookup(lang, e.term) is e or lookup(lang, e.term).term.lower() == e.term.lower()


@pytest.mark.parametrize(("lang", "id_"), ENTRIES)
def test_entry_is_well_formed(lang, id_):
    e = entry(lang, id_)
    assert e.language == lang
    assert e.term.strip() and e.definition.strip()
    assert len(e.definition) <= 300, f"{id_}: definition is {len(e.definition)} characters"
    assert isinstance(e.rules, tuple) and all(isinstance(r, str) and r.strip() for r in e.rules)
    assert all(len(r) <= 330 for r in e.rules), f"{id_}: a rule is too long to skim"
    assert len(e.rules) <= 6
    assert not e.example_output or e.example, f"{id_}: an output without an example"
    assert not e.example or e.example_output, f"{id_}: an example with no verified output"
    assert e.example_output == e.example_output.strip("\n")
    ids = {x.id for x in glossary.all_entries(lang)}
    for s in e.see_also:
        assert s in ids, f"{lang}:{id_} sees also {s!r}, which does not exist"
        assert s != id_
    for pattern in e.detect:
        re.compile(pattern[4:] if pattern.startswith("raw:") else pattern, re.M)
    assert not e.example.endswith("\n")
    # Words a learner never sees defined must not hide in a definition: no jargon from the other language.
    if lang == "python":
        assert "console.log" not in e.definition and "undefined" not in e.definition
    elif lang == "javascript":
        assert "print(" not in e.definition and "elif" not in e.definition
    else:
        assert "console.log" not in e.definition and "elif" not in e.definition and "print(" not in e.definition


@pytest.mark.parametrize("lang", CLASSIC)
def test_most_entries_have_an_example_and_rules(lang):
    entries = glossary.all_entries(lang)
    assert sum(1 for e in entries if e.example) >= 0.95 * len(entries)
    assert sum(1 for e in entries if e.rules) >= 0.95 * len(entries)


def test_the_brief_s_words_are_all_there():
    wanted = (
        "truthy falsy boolean expression statement operator operand precedence evaluate variable assignment "
        "reassign mutable immutable scope local global function parameter argument return call loop iteration "
        "iterable index slice off-by-one string key value type type-conversion comparison short-circuit ternary "
        "condition branch nesting bracket balanced syntax syntax-error token keyword comment indentation "
        "floor-division modulo exponent integer float rounding float-precision concatenation closure recursion "
        "exception finally import class method unpacking generator callback async-await"
    ).split()
    for lang in CLASSIC:
        have = {e.id for e in glossary.all_entries(lang)}
        assert not set(wanted) - have, (lang, sorted(set(wanted) - have))
    assert {"none", "list", "tuple", "dict", "set", "range", "equality", "identity", "f-string", "lambda",
            "comprehension", "self"} <= {e.id for e in glossary.all_entries("python")}
    assert {"null", "undefined", "nan", "array", "object", "loose-equality", "strict-equality",
            "template-literal", "arrow-function", "this", "spread-rest", "promise", "event-loop"} <= {
        e.id for e in glossary.all_entries("javascript")}


# ── The oracle: run every example ───────────────────────────────────────

def _run_example(item) -> tuple[int, str, str]:
    tmp = Path(tempfile.mkdtemp(prefix="glossary_example_"))
    try:
        if item.language == "python":
            path = tmp / "example.py"
            cmd = [sys.executable, "-I", "-X", "utf8", str(path)]
        else:
            path = tmp / "example.js"
            cmd = [NODE, str(path)]
        path.write_text(item.example + "\n", encoding="utf-8")
        done = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=30, cwd=tmp,
                              stdin=subprocess.DEVNULL)
        return done.returncode, done.stdout.replace("\r\n", "\n"), done.stderr
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _dart_result(run) -> tuple[int, str, str]:
    """A DartRun as the (exit code, stdout, stderr) the other languages' runners give."""
    problem = run.compile_error or run.error
    return (1 if problem else 0), "\n".join(run.lines) + "\n", problem


@functools.cache
def example_results() -> dict[tuple[str, str], tuple[int, str, str]]:
    items = [e for lang in CLASSIC for e in glossary.all_entries(lang) if e.example and (lang == "python" or NODE)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        outs = list(pool.map(_run_example, items))
    found = {(e.language, e.id): out for e, out in zip(items, outs)}
    if dart_oracle.DART:  # every Dart/Flutter example, in ONE dart run
        dart_items = [e for e in glossary.all_entries("dart") if e.example]
        runs = dart_oracle.run_batch([e.example for e in dart_items])
        found.update({(e.language, e.id): _dart_result(run) for e, run in zip(dart_items, runs)})
    return found


@pytest.mark.parametrize(("lang", "id_"), ENTRIES)
def test_example_prints_exactly_what_the_entry_says(lang, id_):
    e = entry(lang, id_)
    if not e.example:
        pytest.skip("no example")
    if lang == "javascript" and NODE is None:
        pytest.skip("needs node")
    if lang == "dart" and not dart_oracle.DART:
        pytest.skip("needs dart")
    code, out, err = example_results()[(lang, id_)]
    assert code == 0, f"{lang}:{id_} crashed:\n{err[-600:]}"
    assert out.rstrip("\n") == e.example_output, f"{lang}:{id_} printed\n{out!r}\nnot\n{e.example_output!r}"
    assert not err.strip(), f"{lang}:{id_} wrote to stderr: {err[-300:]}"


# The claims below are written by hand from the language specs, NOT read from the entries.
PY_FALSY_CLAIMS = ("False", "None", "0", "0.0", "0j", '""', "''", "[]", "()", "{}", "set()", "range(0)", "b''",
                   "bytearray()", "frozenset()")
PY_TRUTHY_CLAIMS = ('"0"', '"False"', '"None"', '" "', "[0]", "[[]]", "[None]", "-1", "0.1", "1j", "(0,)",
                    "{0}", '{"a": 0}', "float('nan')", "float('inf')", "object()", "lambda: 0", "True")
JS_FALSY_CLAIMS = ("false", "0", "-0", "0n", '""', "''", "``", "null", "undefined", "NaN")
JS_TRUTHY_CLAIMS = ('"0"', '"false"', '"null"', '"undefined"', '" "', "[]", "[0]", "{}", "-1", "Infinity",
                    "1n", "Symbol()", "function () {}", "() => {}", "new Boolean(false)", "new Number(0)",
                    "true")

PY_BOOL = r"""
import json, sys
out = []
for expr in json.loads(sys.stdin.read()):
    out.append(bool(eval(expr, {"__builtins__": __builtins__})))
print(json.dumps(out))
"""
JS_BOOL = r"""
const exprs = JSON.parse(require("fs").readFileSync(0, "utf8"));
console.log(JSON.stringify(exprs.map((e) => Boolean(eval("(" + e + ")")))));
"""


def truth_of(language: str, exprs: list[str]) -> list[bool]:
    """Run bool() / Boolean() over source expressions in the real language."""
    if language == "python":
        cmd = [sys.executable, "-I", "-X", "utf8", "-c", PY_BOOL]
    else:
        if NODE is None:
            pytest.skip("needs node")
        cmd = [NODE, "-e", JS_BOOL]
    done = subprocess.run(cmd, input=json.dumps(exprs), capture_output=True, text=True, encoding="utf-8",
                          timeout=60)
    assert done.returncode == 0, done.stderr[-800:]
    return json.loads(done.stdout.strip().splitlines()[-1])


CLAIMS = {
    "python": (PY_FALSY_CLAIMS, PY_TRUTHY_CLAIMS),
    "javascript": (JS_FALSY_CLAIMS, JS_TRUTHY_CLAIMS),
}


@pytest.mark.parametrize("lang", CLASSIC)
def test_the_hand_written_claims_hold_in_the_real_language(lang):
    """Guards the oracle itself: if this fails, the claims above are wrong, not the glossary."""
    falsy, truthy = CLAIMS[lang]
    assert truth_of(lang, list(falsy)) == [False] * len(falsy)
    assert truth_of(lang, list(truthy)) == [True] * len(truthy)


@pytest.mark.parametrize("lang", CLASSIC)
@pytest.mark.parametrize("word", ["truthy", "falsy"])
def test_the_false_and_true_lists_are_what_the_language_does(lang, word):
    e = entry(lang, word)
    assert e.counts_false and e.counts_true
    assert truth_of(lang, list(e.counts_false)) == [False] * len(e.counts_false), e.counts_false
    assert truth_of(lang, list(e.counts_true)) == [True] * len(e.counts_true), e.counts_true


@pytest.mark.parametrize("lang", CLASSIC)
def test_the_lists_cover_every_value_the_language_calls_false(lang):
    """Not just 'what is listed is right' but 'nothing falsy is missing' from the lists' core."""
    falsy_core = {"python": {"False", "None", "0", "0.0", "0j", '""', "[]", "()", "{}", "set()", "range(0)"},
                  "javascript": {"false", "0", "-0", "0n", '""', "null", "undefined", "NaN"}}[lang]
    assert set(entry(lang, "falsy").counts_false) >= falsy_core
    if lang == "javascript":
        assert set(entry(lang, "falsy").counts_false) == falsy_core, "JavaScript has exactly eight"
    # the trap values each language is famous for sit on the truthy side
    traps = {"python": {'"0"', '"False"', "[0]"}, "javascript": {'"0"', '"false"', "[]", "{}"}}[lang]
    assert set(entry(lang, "truthy").counts_true) >= traps


def _rule_values(rule: str) -> list[str]:
    """The values a 'These are falsy: a, b (note), c and d.' sentence names."""
    body = rule.split(":", 1)[1].rstrip(".")
    body = re.sub(r"\s\([a-z][^()]*\)", "", body)
    return [t.strip() for t in re.split(r",\s*|\s+and\s+", body) if t.strip()]


@pytest.mark.parametrize("lang", CLASSIC)
def test_the_prose_rule_names_exactly_the_falsy_values(lang):
    """The first rule of Falsy is prose; its values are parsed out and run, and must match the list."""
    e = entry(lang, "falsy")
    named = _rule_values(e.rules[0])
    assert len(named) >= 8, named
    assert truth_of(lang, named) == [False] * len(named), named
    same = lambda items: sorted(i.replace('"', "'") for i in items)  # noqa: E731 - '' and "" are one value
    assert same(named) == same(e.counts_false), (named, e.counts_false)


@pytest.mark.parametrize("lang", CLASSIC)
def test_the_prose_about_the_traps_is_true(lang):
    """Rules that name a surprising value are checked by running that value."""
    e = entry(lang, "truthy")
    text = " ".join(e.rules)
    quoted = {"python": ['"0"', '"False"', "[0]", "float('nan')"],
              "javascript": ['"0"', '"false"', "[]", "{}", "-1", "Infinity"]}[lang]
    mentioned = [q for q in quoted if q.replace('"', "'") in text or q in text]
    assert len(mentioned) >= 3, text
    assert truth_of(lang, mentioned) == [True] * len(mentioned)


# ── Matching ────────────────────────────────────────────────────────────

def ids(words) -> list[str]:
    return [w.id for w in words]


#: The activities whose words are written by hand in contexts.CONTEXTS; every other one is derived from
#: its `Activity.concepts` (see "Derived contexts" below).
ORIGINAL_SEVEN = {"eval", "truthy", "loops", "trace", "brackets", "recall", "syntax"}

#: A pack author's `concepts` that resolve in NEITHER language are invisible gaps in "Words used". After the
#: terms_brain_* files none are missing; this many per activity is the headroom for a new pack's odd word
#: before someone writes the entry. A word that exists in only one language is fine (range is Python's).
MAX_UNRESOLVED_PER_ACTIVITY = 2


def test_the_original_seven_keep_their_hand_written_contexts():
    assert set(CONTEXTS) == ORIGINAL_SEVEN
    assert {a.id for a in ACTIVITIES} >= ORIGINAL_SEVEN
    assert ids(words_for_context("loops", "python")) == ["loop", "iteration", "off-by-one", "range"]
    assert ids(words_for_context("loops", "javascript")) == ["loop", "iteration", "off-by-one"], "range is Python's"
    assert ids(words_for_context("eval", "python")) == ["expression", "evaluate", "operator", "precedence"]
    assert ids(words_for_context("syntax", "javascript")) == ["syntax", "syntax-error", "token", "keyword"]


@pytest.mark.parametrize("lang", LANGS)
@pytest.mark.parametrize("activity", ACTIVITIES, ids=lambda a: a.id)
def test_every_brain_activity_has_a_context(activity, lang):
    """A new pack is covered with ZERO glossary edits: its concepts become the context's words. (For each
    language the activity can be played in: a Dart-only activity has no Python or JavaScript words to show.)"""
    if lang not in activity.languages:
        pytest.skip(f"{activity.id} is not played in {lang}")
    got = words_for_context(activity.id, lang)
    assert got, f"Brain Drills activity {activity.id!r} teaches no word at all in {lang}"
    if len(activity.concepts) >= 2:
        assert len(got) >= 2, (activity.id, lang, ids(got), activity.concepts)
    assert len(set(ids(got))) == len(got)


def test_concepts_that_resolve_in_no_language_the_activity_is_played_in_are_few_and_visible():
    """Lists, per activity, the concepts no glossary entry answers to IN A LANGUAGE THE ACTIVITY IS PLAYED IN (a
    Dart-only activity is judged by the Dart glossary alone), so a missing word is a failing line."""
    missing = {}
    for activity in ACTIVITIES:
        gone = [c for c in activity.concepts if all(glossary.resolve(lang, c) is None for lang in activity.languages)]
        if gone:
            missing[activity.id] = gone
    too_many = {k: v for k, v in missing.items() if len(v) > MAX_UNRESOLVED_PER_ACTIVITY}
    assert not too_many, f"write entries (terms_brain_*.py / terms_dart_*.py) for: {too_many}"


def test_every_pack_concept_is_a_plain_word_and_most_resolve_in_every_language_played():
    """Not a gate on single-language words (range, nonlocal...), but the tally is shown when it fails. A concept
    counts as resolved when EVERY language its activity is played in has a word for it."""
    total = resolved = 0
    for activity in ACTIVITIES:
        for c in activity.concepts:
            assert c == c.strip().lower() and c, f"{activity.id}: concept {c!r} is not a plain lowercase word"
            total += 1
            resolved += all(glossary.resolve(lang, c) is not None for lang in activity.languages)
    assert resolved >= 0.9 * total, f"only {resolved} of {total} concepts resolve in every language played"


def test_the_dart_activities_resolve_nearly_every_concept_in_dart():
    """The Dart packs' words are not skipped: each Dart activity has at most one concept the Dart glossary lacks,
    and the tally over all of them is complete (Dart is a full glossary language, not an afterthought)."""
    dart_acts = [a for a in ACTIVITIES if "dart" in a.languages]
    assert len(dart_acts) >= 30, "the Dart and Flutter packs are discovered"
    lacking = {}
    for a in dart_acts:
        gone = [c for c in a.concepts if glossary.resolve("dart", c) is None]
        if gone:
            lacking[a.id] = gone
    assert all(len(v) <= 1 for v in lacking.values()), lacking
    assert len(lacking) <= max(2, len(dart_acts) // 10), lacking


def test_every_hand_written_context_term_exists_somewhere_and_enough_exist_everywhere():
    known = {e.id for lang in LANGS for e in glossary.all_entries(lang)}
    for cid, terms in CONTEXTS.items():
        assert not set(terms) - known, (cid, set(terms) - known)
        for lang in CLASSIC:  # the original seven are not played in Dart
            assert len(words_for_context(cid, lang)) >= 2, (cid, lang)


@pytest.mark.parametrize(
    ("lang", "spoken", "wanted"),
    [
        ("javascript", "type coercion", "type-conversion"),
        ("javascript", "Type-Coercion", "type-conversion"),
        ("python", "type coercion", "type-conversion"),
        ("javascript", "tostring", "string-representation"),
        ("javascript", "toString", "string-representation"),
        ("python", "closures", "closure"),
        ("python", "Short Circuit", "short-circuit"),
        ("python", "f string", "f-string"),
        ("python", "list comprehensions", "comprehension"),
        ("python", "off by one", "off-by-one"),
        ("javascript", "classes", "class"),
        ("python", "keyword arguments", "keyword-argument"),
        ("javascript", "keyword argument", "options-object"),
        ("python", "isinstance", "isinstance"),
        ("javascript", "isinstance", "instanceof"),
        ("javascript", "method resolution order", "prototype-chain"),
        ("javascript", "self", "this"),
        ("javascript", "===", "strict-equality"),
    ],
)
def test_resolve_ignores_case_hyphens_spaces_and_plurals(lang, spoken, wanted):
    found = glossary.resolve(lang, spoken)
    assert found is not None and found.id == wanted, (lang, spoken, found and found.id)


def test_resolve_says_none_for_a_word_a_language_does_not_have():
    assert glossary.resolve("javascript", "range") is None
    assert glossary.resolve("javascript", "nonlocal").id == "closure", "the counterpart, not nothing"
    assert glossary.resolve("python", "for else").id == "for-else"
    assert glossary.resolve("javascript", "for else") is None
    for junk in ("", "   ", None, 12, "\x00", "-" * 50):
        assert glossary.resolve("python", junk) is None  # type: ignore[arg-type]
    assert glossary.resolve("cobol", "closure") is None


def test_a_concept_list_becomes_the_context_in_order_skipping_what_a_language_lacks():
    """The derivation, on a made-up activity: no glossary edit is needed for a pack that does not exist yet."""
    from dataclasses import replace

    from code_coach import brain

    fake = replace(
        next(a for a in ACTIVITIES if a.id not in ORIGINAL_SEVEN),
        id="zz_fake_pack",
        concepts=("palindrome", "range", "no such word at all", "Closure", "closures", "type coercion"),
    )
    brain.ACTIVITIES_BY_ID["zz_fake_pack"] = fake
    try:
        assert ids(words_for_context("zz_fake_pack", "python")) == ["palindrome", "range", "closure", "type-conversion"]
        assert ids(words_for_context("zz_fake_pack", "javascript")) == ["palindrome", "closure", "type-conversion"]
        assert ids(find_words("x = 1", "python", context="zz_fake_pack"))[:4] == [
            "palindrome", "range", "closure", "type-conversion"]
    finally:
        brain.ACTIVITIES_BY_ID.pop("zz_fake_pack", None)
    assert words_for_context("zz_fake_pack", "python") == []


def test_the_glossary_never_needs_the_brain_package_to_import():
    """Contexts are derived lazily: importing the glossary must not import brain (no import cycle)."""
    done = subprocess.run(
        [sys.executable, "-c",
         "import sys, code_coach.glossary as g; g.all_entries('python'); "
         "print('code_coach.brain' in sys.modules); g.words_for_context('fn_scope', 'python'); "
         "print('code_coach.brain' in sys.modules)"],
        capture_output=True, text=True, timeout=60, cwd=ROOT)
    assert done.returncode == 0, done.stderr[-800:]
    assert done.stdout.split() == ["False", "True"]


@pytest.mark.parametrize("lang", LANGS)
@pytest.mark.parametrize("activity", [a.id for a in ACTIVITIES])
def test_context_words_are_always_present_and_first(lang, activity):
    for code in ("", "x", "print(1)", "if x:\n    pass", "\x00\x01 garbage ((("):
        got = find_words(code, lang, context=activity)
        want = ids(words_for_context(activity, lang))
        assert ids(got)[: len(want)] == want
        assert len(set(ids(got))) == len(got)


def test_the_truthy_drill_always_lists_truthy_and_falsy_with_their_full_rules():
    for lang in CLASSIC:
        got = find_words("print('truthy' if (0) else 'falsy')", lang, context="truthy")
        assert ids(got)[:2] == ["truthy", "falsy"]
        falsy = got[1]
        assert falsy.counts_false and falsy.rules and falsy.example


def test_the_brain_drills_mapping_is_what_the_brief_asks_for():
    want = {
        "eval": {"expression", "evaluate", "precedence"},
        "truthy": {"truthy", "falsy"},
        "loops": {"loop", "iteration", "off-by-one"},
        "trace": {"variable", "assignment", "reassign"},
        "brackets": {"bracket", "balanced", "nesting"},
        "recall": {"variable", "value", "assignment"},
        "syntax": {"syntax", "syntax-error", "token", "keyword"},
    }
    for cid, terms in want.items():
        assert terms <= set(CONTEXTS[cid]), cid


def test_python_if_x_shows_truthy():
    got = ids(find_words("x = []\nif x:\n    print('has items')\n", "python"))
    assert "truthy" in got and "falsy" in got and "branch" in got


def test_python_not_items_shows_truthy_and_falsy():
    got = ids(find_words("if not items:\n    return\n", "python"))
    assert got[:2] in (["falsy", "truthy"], ["truthy", "falsy"])


def test_javascript_if_x_strict_equals_null_shows_equality_and_null():
    got = ids(find_words("if (x === null) { go(); }", "javascript"))
    assert "strict-equality" in got and "null" in got
    assert "loose-equality" not in got


def test_javascript_double_equals_is_loose_not_strict():
    got = ids(find_words("if (a == b) {}", "javascript"))
    assert "loose-equality" in got and "strict-equality" not in got


@pytest.mark.parametrize(
    ("lang", "code", "expect"),
    [
        ("python", "for i in range(3):\n    print(i)", {"loop", "range", "indentation"}),
        ("python", "x = 7 // 2 + 7 % 2", {"floor-division", "modulo"}),
        ("python", "name = f'{a} items'", {"f-string"}),
        ("python", "squares = [n * n for n in nums]", {"comprehension"}),
        ("python", "def f(x):\n    return x\n", {"function", "return"}),
        ("python", "a is None", {"identity", "none"}),
        ("python", "try:\n    pass\nexcept ValueError:\n    pass", {"try-except", "exception"}),
        ("python", "while n > 1:\n    n //= 2", {"while-loop", "floor-division"}),
        ("python", "x = 0.1 + 0.2", {"float-precision"}),
        ("javascript", "for (let i = 0; i < 3; i++) {}", {"loop", "increment"}),
        ("javascript", "const f = (a) => a * 2;", {"arrow-function", "let-const-var"}),
        ("javascript", "const s = `hi ${name}`;", {"template-literal"}),
        ("javascript", "x ?? y", {"nullish"}),
        ("javascript", "a?.b", {"optional-chaining"}),
        ("javascript", "items.map(f).filter(g)", {"map", "filter"}),
        ("javascript", "const [a, b] = pair;", {"unpacking"}),
        ("javascript", "console.log(typeof x)", {"type", "console-log"}),
        ("javascript", "x == NaN", {"nan", "loose-equality"}),
        ("dart", "var n = name ?? 'guest';", {"null-coalescing"}),
        ("dart", "name ??= 'x';", {"null-aware-assignment"}),
        ("dart", "final len = s?.length;", {"null-aware-access", "final"}),
        ("dart", "int? age;\nlate String label;", {"nullable-type", "late"}),
        ("dart", "print(n ~/ 2);", {"truncating-division"}),
        ("dart", "var l = [1, ...more, ...?maybe];", {"spread"}),
        ("dart", "var sb = StringBuffer()..write('a')..write('b');", {"cascade", "string-buffer"}),
        ("dart", "var p = const Point(1, 2);", {"const", "const-constructor"}),
        ("dart", "Future<int> f() async { return await g(); }", {"future", "async-await"}),
        ("dart", "Stream<int> count() async* { yield 1; }", {"stream", "async-generator"}),
        ("dart", "class Dog extends Animal with Walker implements Pet {}", {"class", "inheritance", "mixin", "interface"}),
        ("dart", "sealed class Shape {}\nenum Color { red }", {"sealed-class", "enum"}),
        ("dart", "var s = switch (n) { 1 => 'a', _ => 'b' };", {"switch-expression", "arrow-function"}),
        ("dart", "switch (n) {\n  case 1:\n    print(1);\n}", {"switch"}),
        ("dart", "try { f(); } on FormatException catch (e) { rethrow; } finally { done(); }",
         {"try-catch", "rethrow", "finally"}),
        ("dart", "String greet({required String name, int age = 0}) => name;", {"named-parameter", "required"}),
        ("dart", "void main() { print('hi'); }", {"main-function"}),
        ("dart", "xs.where((n) => n.isEven).map((n) => n * 2).toList();", {"filter", "map", "to-list"}),
        ("dart", "final (a, b) = pair;", {"destructuring"}),
        ("dart", "factory Logger(String n) => _cache[n]!;", {"factory-constructor", "null-assertion"}),
        ("dart", "class S extends State<W> { void initState() { super.initState(); } }", {"init-state", "super"}),
        ("dart", "setState(() { count++; });", {"set-state"}),
        ("dart", "Row(children: [Expanded(child: Text('a')), Spacer(), Column()])",
         {"row", "expanded", "spacer", "column", "text-widget"}),
        ("dart", "Stack(children: [Positioned(left: 1, child: x)])", {"stack-widget", "positioned"}),
        ("dart", "ListView.builder(itemCount: 3, itemBuilder: (c, i) => x)", {"list-view-builder", "list-view"}),
        ("dart", "MaterialApp(home: Scaffold(body: Center(child: Text('x'))))",
         {"material-app", "scaffold", "center"}),
        ("dart", "final c = TextEditingController();", {"text-editing-controller"}),
        ("dart", "Navigator.push(context, MaterialPageRoute(builder: (_) => P()));", {"navigator", "route"}),
    ],
)
def test_detection_on_sample_snippets(lang, code, expect):
    got = set(ids(find_words(code, lang, limit=30)))
    assert expect <= got, (expect - got, sorted(got))


def test_a_word_inside_a_string_or_comment_is_not_code():
    assert "loop" not in ids(find_words("print('for each while')", "python", limit=30))
    assert "loop" not in ids(find_words("# for the while\nx = 1", "python", limit=30))
    assert "loop" not in ids(find_words("console.log('for while'); // for", "javascript", limit=30))
    assert "null" not in ids(find_words("const s = 'null';", "javascript", limit=30))
    # Dart: strings, raw strings, triple-quoted strings and both kinds of comment
    assert "null" not in ids(find_words("var s = 'null';", "dart", limit=60))
    assert "null-coalescing" not in ids(find_words("var s = '$a ?? b'; // c ?? d", "dart", limit=60))
    assert "null-coalescing" not in ids(find_words("var s = r'a ?? b';", "dart", limit=60))
    assert "null-coalescing" not in ids(find_words("var s = \"\"\"a\n?? b\n\"\"\";", "dart", limit=60))
    assert "null-coalescing" not in ids(find_words("/* x ?? y\n */ var a = 1;", "dart", limit=60))
    assert "null-coalescing" in ids(find_words("var a = b ?? 'it\\'s';", "dart", limit=60))


def test_limit_dedupe_and_order():
    code = "for i in range(10):\n    if not x and y or z:\n        print([a for a in b if a is None])\n"
    for limit in (0, 1, 2, 3, 5, 8, 40):
        got = find_words(code, "python", limit=limit)
        assert len(got) <= limit
        assert len(set(ids(got))) == len(got)
    assert find_words(code, "python", limit=0) == []
    wide = find_words(code, "python", limit=40)
    assert len(wide) > 8
    assert ids(find_words(code, "python")) == ids(wide)[:8], "the default limit is 8 and a prefix of the full order"
    # context first, even with a small limit; the rest follow by priority
    ctx = find_words(code, "python", context="loops", limit=3)
    assert ids(ctx) == ids(words_for_context("loops", "python"))[:3]
    # by priority, then first appearance
    priorities = [w.priority for w in wide]
    assert priorities == sorted(priorities, reverse=True)


def test_unknown_language_and_junk_input_never_raise():
    assert find_words("if x: pass", "cobol") == []
    assert find_words("if x: pass", "") == []
    assert find_words("if x: pass", None) == []  # type: ignore[arg-type]
    assert find_words("x", "python", context="no-such-activity") == find_words("x", "python")
    for junk in ("", "   \n", None, 12, "\x00" * 50, "'" * 500, "((((" * 400, "/*" * 300, '"""' * 99, "`" * 301,
                 "é😀" * 400, "if " * 5000, "a" * 100_000):
        for lang in LANGS:
            assert isinstance(find_words(junk, lang), list)  # type: ignore[arg-type]
            assert isinstance(find_words(junk, lang, context="syntax"), list)  # type: ignore[arg-type]


def test_aliases_borrow_a_glossary():
    assert glossary.language_for("tfwr") == "python"
    assert glossary.language_for("TypeScript") == "javascript"
    assert glossary.language_for("dart") == "dart" and glossary.language_for(" Dart ") == "dart"
    assert glossary.LANGUAGES == ("python", "javascript", "dart")
    assert glossary.language_for("sql") == ""
    assert glossary.language_for(None) == ""


def test_lookup_by_id_term_or_other_spelling():
    assert lookup("python", "falsy").id == "falsy"
    assert lookup("python", "Falsy").id == "falsy"
    assert lookup("python", "falsey").id == "falsy"
    assert lookup("javascript", "===").id == "strict-equality"
    assert lookup("python", "is").id == "identity"
    assert lookup("python", "nope-not-a-word") is None
    assert lookup("cobol", "falsy") is None


# ── The brain-pack vocabulary: rules held to the real languages, detection and noise ──

#: Every claim below is written by hand (NOT read from the entries) and RUN in the real language; the
#: rules of terms_brain_*.py that can be run are backed by one of these. (name, language, program, stdout).
RULE_CHECKS: list[tuple[str, str, str, str]] = [
    # strings
    ("py-case-matters", "python", """print('a' == 'A', "level" == "level"[::-1], "Level" == "Level"[::-1])""",
     "False True False"),
    ("py-strip-ends-only", "python", """print("xxhixx".strip("x"), repr("  a b ".lstrip()), repr(" a ".rstrip()))""",
     "hi 'a b ' ' a'"),
    ("py-replace-count", "python", """print("aaa".replace("a", "b", 2), "abc".replace("z", "y"))""", "bba abc"),
    ("py-split-rules", "python", """print("a,b,c".split(",", 1), "a  b".split(), " a ".split())""",
     "['a', 'b,c'] ['a', 'b'] ['a']"),
    ("py-join-needs-strings", "python", """
        try:
            ",".join([1, 2])
        except TypeError:
            print("TypeError")
        print(",".join("a,b,c".split(",")))
     """, "TypeError\na,b,c"),
    ("py-index-raises-find-does-not", "python", """
        try:
            "abc".index("z")
        except ValueError:
            print("ValueError", "abc".find("z"))
     """, "ValueError -1"),
    ("py-padding-never-cuts", "python", """print("abcdef".rjust(3), "7".zfill(3), "abcdef".ljust(3))""",
     "abcdef 007 abcdef"),
    ("py-character-codes", "python",
     """print(ord("b") - ord("a"), chr((ord("x") - ord("a") + 3) % 26 + ord("a")), ord("a") - ord("A"), ord("0"))""",
     "1 a 32 48"),
    ("py-format-spec", "python",
     """print(f"{0.256:.1%}", f"{5:05d}", "{:.2f}".format(3.14159), f"{'ab':>5}|{'ab':<5}|")""",
     "25.6% 00005 3.14    ab|ab   |"),
    # collections
    ("py-set-operations", "python", """
        a = {1, 2, 3}
        print(sorted(a ^ {2, 3, 4}), {1, 2, 3} - {2} == {1, 3}, {2} - {1, 2, 3}, sorted(a.union({9})),
              sorted(a.intersection({1, 9})), sorted(a.difference({1})))
     """, "[1, 4] True set() [1, 2, 3, 9] [1] [2, 3]"),
    ("py-default-value", "python", """
        d = {"a": None}
        print(d.get("a", 0), 0 or 5, d.setdefault("b", []), d)
     """, "None 5 [] {'a': None, 'b': []}"),
    ("py-min-max", "python", """
        words = ["ab", "cd", "e"]
        print(max(words, key=len), min(3, 1, 2), max([], default=0))
        try:
            max([])
        except ValueError:
            print("ValueError")
     """, "ab 1 0\nValueError"),
    ("py-sum", "python", """
        print(sum([1, 2, 3], 10), sum([]))
        try:
            sum(["a", "b"])
        except TypeError:
            print("TypeError")
     """, "16 0\nTypeError"),
    ("py-sorting", "python", """
        a = [3, 1, 2]
        print(sorted(["b", "A", "a"]), a.sort(), a.reverse(), a)
        try:
            sorted([1, "a"])
        except TypeError:
            print("TypeError")
     """, "['A', 'a', 'b'] None None [3, 2, 1]\nTypeError"),
    ("py-sorted-is-a-copy", "python", """
        a = [3, 1, 2]
        b = sorted(a)
        c = a[::-1]
        print(a, b, c)
     """, "[3, 1, 2] [1, 2, 3] [2, 1, 3]"),
    ("py-stable-also-with-reverse", "python",
     """print(sorted(["bb", "aa", "c"], key=len, reverse=True), sorted(["b", "a", "c"], key=lambda s: 0))""",
     "['bb', 'aa', 'c'] ['b', 'a', 'c']"),
    ("py-key-is-not-called", "python", """
        try:
            sorted(["a"], key=len())
        except TypeError:
            print("TypeError")
     """, "TypeError"),
    ("py-swap", "python", """
        a, b = 1, 2
        a = b
        b = a
        print(a, b)
        nums = [1, 2]
        nums[0], nums[1] = nums[1], nums[0]
        print(nums)
     """, "2 2\n[2, 1]"),
    ("py-accumulator-reset", "python", """
        for n in [1, 2, 3]:
            total = 0
            total += n
        print(total)
     """, "3"),
    ("py-negative-index", "python", """
        a = [1, 2, 3]
        print(a[-1] == a[len(a) - 1], a[-3], "hello"[-1])
        try:
            a[-4]
        except IndexError:
            print("IndexError")
        print(a[-4:])
     """, "True 1 o\nIndexError\n[1, 2, 3]"),
    ("py-step", "python", """
        print(list(range(5, 0, -2)), list(range(0, 10, 3)))
        try:
            range(0, 5, 0)
        except ValueError:
            print("ValueError")
     """, "[5, 3, 1] [0, 3, 6, 9]\nValueError"),
    ("py-map-filter-reduce", "python", """
        from functools import reduce
        print(type(map(str, [1])).__name__, type(filter(None, [1])).__name__)
        try:
            reduce(lambda a, b: a + b, [])
        except TypeError:
            print("TypeError")
        print(reduce(lambda a, b: a + b, [], 7))
     """, "map filter\nTypeError\n7"),
    # functions and loops
    ("py-default-after-non-default", "python", """
        try:
            compile("def f(a=1, b): pass", "x", "exec")
        except SyntaxError:
            print("SyntaxError")
     """, "SyntaxError"),
    ("py-keyword-arguments", "python", """
        def area(w, h):
            return w * h
        try:
            compile("area(w=3, 4)", "x", "eval")
        except SyntaxError:
            print("SyntaxError")
        for call in ("area(3, x=4)", "area(3, w=4)"):
            try:
                eval(call)
            except TypeError:
                print("TypeError")
     """, "SyntaxError\nTypeError\nTypeError"),
    ("py-short-circuit-skips-side-effects", "python", """
        calls = []
        def f():
            calls.append(1)
            return True
        False and f()
        True or f()
        print(calls)
     """, "[]"),
    ("py-recursion-limit", "python", "import sys\nprint(sys.getrecursionlimit())", "1000"),
    ("py-no-block-scope", "python", """
        print([j for j in range(2)])
        try:
            print(j)
        except NameError:
            print("NameError")
        for i in range(2):
            inner = i
        print(inner)
     """, "[0, 1]\nNameError\n1"),
    ("py-class-attribute-shadowed", "python", """
        class A:
            n = 1
        a = A()
        b = A()
        a.n = 5
        print(A.n, a.n, b.n)
        A.n = 7
        print(a.n, b.n)
     """, "1 5 1\n5 7"),
    ("py-loop-variable-reset-each-pass", "python", """
        seen = []
        for i in range(3):
            i += 10
            seen.append(i)
        print(seen)
     """, "[10, 11, 12]"),
    ("py-break-leaves-inner-only", "python", """
        c = 0
        for i in range(3):
            for j in range(3):
                if j == 1:
                    break
                c += 1
        print(c)
     """, "3"),
    ("py-for-else-empty-loop", "python", """
        for x in []:
            pass
        else:
            print("else")
     """, "else"),
    ("py-counter-library", "python",
     """from collections import Counter\nprint(Counter("banana")["a"], Counter("banana").most_common(1))""",
     "3 [('a', 3)]"),
    # classes
    ("py-attributes", "python", """
        class P:
            def __init__(self):
                self.n = 1
            @property
            def double(self):
                return self.n * 2
        p = P()
        p.k = 3
        print(p.double, p.k)
        try:
            p.zzz
        except AttributeError:
            print("AttributeError")
     """, "2 3\nAttributeError"),
    ("py-classmethod-gets-the-class", "python", """
        class A:
            @classmethod
            def who(cls):
                return cls.__name__
        class B(A):
            pass
        print(A.who(), B.who(), B().who())
     """, "A B B"),
    ("py-issubclass", "python", """
        class A: pass
        class B(A): pass
        print(issubclass(A, A), issubclass(B, A), isinstance(B(), A), type(B()) is A)
     """, "True True True False"),
    ("py-override-by-name-only", "python", """
        class A:
            def f(self, x):
                return x
        class B(A):
            def f(self):
                return "B"
        print(B().f(), A().f(1))
     """, "B 1"),
    ("py-super-init", "python", """
        class A:
            def __init__(self, n):
                self.n = n
        class B(A):
            def __init__(self, n):
                super().__init__(n)
                self.m = n + 1
        b = B(1)
        print(b.n, b.m)
     """, "1 2"),
    ("py-mro-several-parents", "python", """
        class A: pass
        class B: pass
        class C(A, B): pass
        print([c.__name__ for c in C.__mro__])
     """, "['C', 'A', 'B', 'object']"),
    ("py-repr-only-is-used-by-print", "python", """
        class P:
            def __repr__(self):
                return "P!"
        print(P(), [P()])
        class Q: pass
        print(str(Q()).startswith("<"))
     """, "P! [P!]\nTrue"),
    # logic
    ("py-logic", "python",
     """print(True or False and False, not 0, 1 and 2, 1 & 2, ~6 == -6 - 1, ~5 == -5 - 1, 0 % 5, -3 % 2 == 1)""",
     "True True 2 0 True True 0 True"),
    ("py-de-morgan-holds", "python", """
        print(all(((not (a and b)) == ((not a) or (not b))) and ((not (a or b)) == ((not a) and (not b)))
                  for a in (True, False) for b in (True, False)))
     """, "True"),
    ("py-leap-year-rule-vs-the-calendar", "python", """
        import calendar
        def leap(y):
            return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
        print(all(leap(y) == calendar.isleap(y) for y in range(1, 3001)))
     """, "True"),
    ("py-chained-comparison", "python", """
        calls = []
        def f():
            calls.append(1)
            return 3
        print(all((1 < x < 5) == (1 < x and x < 5) for x in range(-3, 10)), (1 < f() < 5, len(calls)))
     """, "True (True, 1)"),
    ("py-division-by-zero", "python", """
        for expr in ("1 / 0", "1 // 0", "1 % 0", "1.0 / 0"):
            try:
                eval(expr)
            except ZeroDivisionError as e:
                print(type(e).__name__)
        print(divmod(7, 2), 6 / 3)
     """, "ZeroDivisionError\nZeroDivisionError\nZeroDivisionError\nZeroDivisionError\n(3, 1) 2.0"),
    ("py-bit-rules", "python", """
        print(1 << 3 == 1 * 2 ** 3, 20 >> 2 == 20 // 2 ** 2, -8 >> 1 == -8 // 2, 1 << 100 == 2 ** 100,
              bin(5), int("101", 2), 0b1010, f"{10:08b}", (0b101101 & (1 << 2)) != 0)
     """, "True True True True 0b101 5 10 00001010 True"),
    ("py-primes-vs-a-sieve", "python", """
        def prime(n):
            return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))
        sieve = [True] * 201
        sieve[0] = sieve[1] = False
        for i in range(2, 201):
            if sieve[i]:
                for j in range(i * i, 201, i):
                    sieve[j] = False
        print(all(prime(n) == sieve[n] for n in range(201)), [n for n in range(30) if prime(n) and n % 2 == 0])
     """, "True [2]"),
    ("py-fizzbuzz-order", "python", """
        def bad(n):
            return "Fizz" if n % 3 == 0 else "Buzz" if n % 5 == 0 else "FizzBuzz" if n % 15 == 0 else n
        print(bad(15))
     """, "Fizz"),
    # errors
    ("py-error-types", "python", """
        for f in (lambda: "1" + 1, lambda: len(5), lambda: int("abc"), lambda: [].remove(1), lambda: int(None)):
            try:
                f()
            except Exception as e:
                print(type(e).__name__)
        try:
            x, y = [1, 2, 3]
        except ValueError as e:
            print(type(e).__name__)
        print(hasattr("abc", "push"), float("nan") != float("nan"))
        d = {"a": 1}
        try:
            d["b"]
        except KeyError as e:
            print(e.args[0], str(e))
        print(d.get("b"), "b" in d)
     """, "TypeError\nTypeError\nValueError\nValueError\nTypeError\nValueError\nFalse True\nb 'b'\nNone False"),
    ("py-syntax-error-runs-nothing-runtime-error-runs-the-start", "python", """
        try:
            compile("print('x')\\nprint(", "s", "exec")
        except SyntaxError:
            print("SyntaxError")
        try:
            exec("print('before')\\n1/0\\nprint('after')")
        except ZeroDivisionError:
            print("stopped")
     """, "SyntaxError\nbefore\nstopped"),
    ("py-traceback-order", "python", """
        import sys, traceback
        def inner(): 1 / 0
        def outer(): inner()
        try:
            outer()
        except ZeroDivisionError:
            print([f.name for f in traceback.extract_tb(sys.exc_info()[2])])
     """, "['<module>', 'outer', 'inner']"),
    # ── JavaScript ──
    ("js-case-matters", "javascript",
     """console.log("a" === "A", "level" === [..."level"].reverse().join(""), "Level" === [..."Level"].reverse().join(""));""",
     "false true false"),
    ("js-trim-takes-no-argument", "javascript",
     """console.log("xxhixx".trim("x"), JSON.stringify("  a b ".trimStart()), JSON.stringify(" a ".trimEnd()));""",
     'xxhixx "a b " " a"'),
    ("js-split-limit-keeps-pieces", "javascript",
     """console.log("a,b,c".split(",", 2), "".split(","), "abc".split(""));""", "[ 'a', 'b' ] [ '' ] [ 'a', 'b', 'c' ]"),
    ("js-join", "javascript",
     """console.log([1, 2, 3].join(""), [null, undefined, 1].join("-"), "a,b,c".split(",").join(","));""",
     "123 --1 a,b,c"),
    ("js-indexof-zero-is-falsy", "javascript",
     """console.log("abc".indexOf("a"), Boolean("abc".indexOf("a")), "abc".indexOf("a") !== -1);""", "0 false true"),
    ("js-replace-first-only", "javascript", """console.log("a-b-c".replace(/-/g, "+"), "aaa".replace("a", "b"));""",
     "a+b+c baa"),
    ("js-tofixed-and-padding", "javascript",
     """console.log((1.005).toFixed(2), typeof (3.14159).toFixed(2), "abcdef".padStart(3), "7".padStart(3, "0"));""",
     "1.00 string abcdef 007"),
    ("js-characters", "javascript", """console.log([..."😀"].length, "😀".length, "é".length);""", "1 2 1"),
    ("js-character-codes", "javascript",
     """console.log("b".charCodeAt(0) - "a".charCodeAt(0), String.fromCharCode((("x".charCodeAt(0) - 97 + 3) % 26) + 97), "a".charCodeAt(0) - "A".charCodeAt(0), "0".charCodeAt(0));""",
     "1 a 32 48"),
    ("js-localecompare", "javascript", """console.log("a".localeCompare("B"), "Z" < "a", "10" < "9");""", "-1 true true"),
    ("js-membership", "javascript",
     """console.log(1 in [5, 6], 6 in [5, 6], "a" in { a: 1 }, 1 in { a: 1 }, [1, 2].includes(2));""",
     "true false true false true"),
    ("js-defaults", "javascript", """
        const { x = 9 } = { x: null };
        const { y = 9 } = {};
        console.log(x, y, 0 ?? 5, 0 || 5);
     """, "null 9 0 5"),
    ("js-math-max-min", "javascript", """console.log(Math.max([1, 2]), Math.max(), Math.min(), Math.max(...[3, 7]));""",
     "NaN -Infinity Infinity 7"),
    ("js-reduce-needs-a-start", "javascript", """
        try { [].reduce((a, b) => a + b); } catch (e) { console.log(e.name); }
        console.log(["1", "2"].reduce((t, x) => t + x, 0));
     """, "TypeError\n012"),
    ("js-sort-and-reverse-return-the-same-array", "javascript", """
        const a = [3, 1, 2];
        console.log(a.sort() === a, a.reverse() === a, ["b", "A", "a"].sort(), [10, 9, 1].sort());
     """, "true true [ 'A', 'a', 'b' ] [ 1, 10, 9 ]"),
    ("js-comparators", "javascript",
     """console.log(["pear", "fig"].sort((a, b) => a.length - b.length), [3, 1, 2].sort((a, b) => b - a));""",
     "[ 'fig', 'pear' ] [ 3, 2, 1 ]"),
    ("js-swap-needs-the-semicolon", "javascript", """
        let r;
        try { r = new Function("let a = 1, b = 2\\n[a, b] = [b, a]\\nreturn [a, b].join()")(); } catch (e) { r = e.name; }
        console.log(r === "2,1", new Function("let a = 1, b = 2;\\n[a, b] = [b, a]\\nreturn [a, b].join()")());
     """, "false 2,1"),
    ("js-negative-index-and-slice-step", "javascript", """
        const a = [1, 2, 3];
        console.log(a[-1], a.at(-4), a.at(-1), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].slice(0, 10, 3).length);
     """, "undefined undefined 3 10"),
    ("js-default-parameters", "javascript", """
        function f(a = []) { a.push(1); return a.length; }
        console.log(f(), f(), (({ w, h }) => h)({ w: 1 }));
     """, "1 1 undefined"),
    ("js-short-circuit-skips-side-effects", "javascript", """
        const calls = [];
        const f = () => { calls.push(1); return true; };
        false && f();
        true || f();
        console.log(calls.length);
     """, "0"),
    ("js-var-ignores-blocks", "javascript", """
        { var v = 1; let w = 2; }
        console.log(v, typeof w);
        for (var k = 0; k < 3; k++) {}
        console.log(k);
     """, "1 undefined\n3"),
    ("js-body-changes-the-loop", "javascript", """
        const seen = [];
        for (let i = 0; i < 3; i++) { seen.push(i); i++; }
        console.log(seen.join());
     """, "0,2"),
    ("js-break-leaves-inner-only", "javascript", """
        let c = 0;
        for (let i = 0; i < 3; i++) {
          for (let j = 0; j < 3; j++) {
            if (j === 1) break;
            c++;
          }
        }
        console.log(c);
     """, "3"),
    ("js-statics-fields-prototype", "javascript", """
        class A { static count = 0; items = []; static who() { return this === A; } }
        const a = new A(), b = new A();
        a.items.push(1);
        console.log(a.count, A.count, b.items.length, A.who(), new A() === new A(), typeof new A().who);
        class H {}
        H.prototype.items = [];
        const x = new H(), y = new H();
        x.items.push(1);
        console.log(y.items.length);
     """, "undefined 0 0 true false undefined\n1"),
    ("js-super-before-this", "javascript", """
        class A {}
        class B extends A { constructor() { this.x = 1; super(); } }
        try { new B(); } catch (e) { console.log(e.name); }
        class D { constructor(n) { this.n = n; } }
        class E extends D {}
        console.log(new E(4).n);
     """, "ReferenceError\n4"),
    ("js-prototype-chain-and-instanceof", "javascript", """
        class A { hi() { return "A"; } }
        class B extends A {}
        console.log(Object.getPrototypeOf(B.prototype) === A.prototype, B.prototype.hasOwnProperty("hi"),
          "hi" in B.prototype, "a" instanceof String, new String("a") instanceof String, [] instanceof Object);
     """, "true false true false true true"),
    ("js-tostring", "javascript", """
        class P { constructor(n) { this.n = n; } toString() { return "P" + this.n; } }
        console.log(new P(1));
        console.log(String({}), `${new P(2)}`, "" + new P(3));
     """, "P { n: 1 }\n[object Object] P2 P3"),
    ("js-getter", "javascript", """class A { get area() { return 2; } }\nconsole.log(new A().area);""", "2"),
    ("js-logic", "javascript",
     """console.log(true || false && false, !![], 1 && 2, 1 & 2, ~6, 2 ** 32 | 0, 1 << 31, 0b1010, -3 % 2, -3 % 2 !== 0);""",
     "true true 2 0 -7 0 -2147483648 10 -1 true"),
    ("js-de-morgan-holds", "javascript", """
        let ok = true;
        for (const a of [true, false]) for (const b of [true, false]) {
          if (!(a && b) !== (!a || !b) || !(a || b) !== (!a && !b)) ok = false;
        }
        console.log(ok);
     """, "true"),
    ("js-leap-year-rule-vs-the-date-object", "javascript", """
        const leap = (y) => y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0);
        let bad = 0;
        for (let y = 100; y < 3000; y++) {
          const d = new Date(Date.UTC(2000, 1, 1));
          d.setUTCFullYear(y, 1, 29);
          if ((d.getUTCMonth() === 1) !== leap(y)) bad++;
        }
        console.log(bad);
     """, "0"),
    ("js-division", "javascript",
     """console.log(1 / 0, 0 / 0, -1 / 0, 7 / 2, Math.floor(-7 / 2), Math.trunc(-3.9), -7 % 2);""",
     "Infinity NaN -Infinity 3.5 -4 -3 -1"),
    ("js-comparisons-do-not-chain", "javascript", """console.log(10 < 3 < 5, 1 < 5 < 3, (10 < 3) < 5);""", "true true true"),
    ("js-bit-rules", "javascript", """
        console.log(1 << 3 === 1 * 2 ** 3, 20 >> 2 === Math.floor(20 / 4), -8 >> 1 === Math.floor(-8 / 2),
          (5).toString(2), parseInt("101", 2), (10).toString(2).padStart(8, "0"), (0b101101 & (1 << 2)) !== 0, -1 >>> 28);
     """, "true true true 101 5 00001010 true 15"),
    ("js-primes-vs-a-sieve", "javascript", """
        const prime = (n) => { if (n < 2) return false; for (let d = 2; d * d <= n; d++) if (n % d === 0) return false; return true; };
        const sieve = Array(201).fill(true);
        sieve[0] = sieve[1] = false;
        for (let i = 2; i <= 200; i++) if (sieve[i]) for (let j = i * i; j <= 200; j += i) sieve[j] = false;
        let ok = true;
        for (let n = 0; n <= 200; n++) if (prime(n) !== sieve[n]) ok = false;
        console.log(ok, [...Array(30).keys()].filter((n) => prime(n) && n % 2 === 0));
     """, "true [ 2 ]"),
    ("js-fizzbuzz-order", "javascript", """
        const bad = (n) => n % 3 === 0 ? "Fizz" : n % 5 === 0 ? "Buzz" : n % 15 === 0 ? "FizzBuzz" : n;
        console.log(bad(15));
     """, "Fizz"),
    ("js-error-types", "javascript", """
        const tries = [() => null.x, () => undefined.y, () => (5)(), () => undefinedName, () => new Array(-1),
          () => (1).toFixed(101), () => "a".repeat(-1)];
        for (const f of tries) { try { f(); } catch (e) { console.log(e.name); } }
        console.log("1" + 1, [1, 2, 3][5], "abc"[9]);
     """, "TypeError\nTypeError\nTypeError\nReferenceError\nRangeError\nRangeError\nRangeError\n11 undefined undefined"),
    ("js-syntax-error-runs-nothing-runtime-error-runs-the-start", "javascript", """
        try { new Function("console.log(1);\\nconsole.log("); } catch (e) { console.log(e.name); }
        try { new Function("console.log('before'); null.x; console.log('after')")(); } catch (e) { console.log("stopped"); }
     """, "SyntaxError\nbefore\nstopped"),
    ("js-stack-newest-call-first", "javascript", """
        function inner() { null.x; }
        function outer() { inner(); }
        try { outer(); } catch (e) {
          const names = e.stack.split("\\n").slice(1).map((l) => l.trim().split(" ")[1]);
          console.log(names.slice(0, 2));
        }
     """, "[ 'inner', 'outer' ]"),
]


def _run_rule_check(job: tuple[str, str, str, str]) -> tuple[int, str, str]:
    name, language, program, _expected = job
    tmp = Path(tempfile.mkdtemp(prefix="glossary_rule_"))
    try:
        body = "\n".join(line for line in program.strip("\n").splitlines())
        import textwrap

        body = textwrap.dedent(body)
        path = tmp / ("rule.py" if language == "python" else "rule.js")
        path.write_text(body + "\n", encoding="utf-8")
        cmd = ([sys.executable, "-I", "-X", "utf8", str(path)] if language == "python" else [NODE, str(path)])
        done = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=30, cwd=tmp,
                              stdin=subprocess.DEVNULL)
        return done.returncode, done.stdout.replace("\r\n", "\n"), done.stderr
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@functools.cache
def rule_results() -> dict[str, tuple[int, str, str]]:
    jobs = [c for c in RULE_CHECKS if c[1] == "python" or NODE]
    with ThreadPoolExecutor(max_workers=4) as pool:
        outs = list(pool.map(_run_rule_check, jobs))
    return {job[0]: out for job, out in zip(jobs, outs)}


def test_rule_check_names_are_unique():
    names = [c[0] for c in RULE_CHECKS]
    assert len(names) == len(set(names))
    assert sum(c[1] == "python" for c in RULE_CHECKS) >= 40 and sum(c[1] == "javascript" for c in RULE_CHECKS) >= 35


@pytest.mark.parametrize(("name", "language", "program", "expected"), RULE_CHECKS, ids=[c[0] for c in RULE_CHECKS])
def test_the_brain_pack_rules_hold_in_the_real_language(name, language, program, expected):
    """The claims behind the rules of terms_brain_*.py: hand-written here, run for real."""
    if language == "javascript" and NODE is None:
        pytest.skip("needs node")
    code, out, err = rule_results()[name]
    assert code == 0, f"{name} crashed:\n{err[-600:]}"
    assert out.rstrip("\n") == expected, f"{name} printed\n{out!r}\nnot\n{expected!r}"


def _brain_ids() -> dict[str, set[str]]:
    """The ids written in the terms_brain_* files, per language."""
    import importlib
    import pkgutil

    found: dict[str, set[str]] = {lang: set() for lang in LANGS}
    for info in pkgutil.iter_modules(glossary.__path__):
        if info.name.startswith("terms_brain_"):
            module = importlib.import_module(f"code_coach.glossary.{info.name}")
            for item in module.TERMS:
                found[item.language].add(item.id)
    return found


def test_the_brain_pack_files_added_a_lot_of_words_to_both_languages():
    new = _brain_ids()
    for lang in CLASSIC:
        assert len(new[lang]) >= 80, (lang, len(new[lang]))
        assert len(glossary.all_entries(lang)) >= 170


@pytest.mark.parametrize(
    ("lang", "code", "expect"),
    [
        # a slice
        ("python", "s = text[::2]\nlast = items[-1]\nhead = items[:3]", {"slice", "step", "negative-index"}),
        ("javascript", "const head = items.slice(0, 3);\nconst last = items.at(-1);", {"slice", "negative-index"}),
        # an f-string / template literal
        ("python", 'print(f"{price:.2f} for {n} items")', {"f-string", "format"}),
        ("javascript", "const label = price.toFixed(2).padStart(8);", {"format", "padding"}),
        # a class with inheritance
        ("python", "class Dog(Animal):\n    def __init__(self, name):\n        super().__init__()\n        self.name = name\n",
         {"class", "inheritance", "super", "attribute"}),
        ("javascript", "class Dog extends Animal {\n  constructor(name) {\n    super();\n    this.name = name;\n  }\n}",
         {"class", "inheritance", "super", "property"}),
        # a try/except
        ("python", 'try:\n    value = data["b"]\nexcept KeyError as e:\n    print(e)', {"try-except", "key-error", "exception"}),
        ("javascript", "try {\n  JSON.parse(text);\n} catch (e) {\n  console.log(e.message);\n}", {"try-catch", "exception"}),
        ("javascript", "try { null.x; } catch (e) { if (e instanceof TypeError) {} }", {"type-error", "instanceof"}),
        # a comprehension / its counterpart
        ("python", "squares = [n * n for n in nums if n % 2 == 0]", {"comprehension", "modulo"}),
        ("javascript", "const out = nums.filter((n) => n % 2 === 0).map((n) => n * n);", {"filter", "map", "arrow-function"}),
        # a lambda / arrow function used as a sort key or comparator
        ("python", "ordered = sorted(words, key=lambda w: len(w))", {"lambda", "sorting", "key-function"}),
        ("javascript", "words.sort((a, b) => a.length - b.length);", {"arrow-function", "sorting", "comparator"}),
        # strings
        ("python", 'parts = line.strip().split(",")\nname = ",".join(parts).upper()',
         {"strip", "split", "join", "letter-case"}),
        ("javascript", 'const parts = line.trim().split(",");\nconst name = parts.join(",").toUpperCase();',
         {"strip", "split", "join", "letter-case"}),
        # defaults and scopes
        ("python", "def add(x, items=[]):\n    items.append(x)\n    return items", {"mutable-default", "default-parameter"}),
        ("javascript", "const fns = [];\nfor (var i = 0; i < 3; i++) {\n  fns.push(() => i);\n}", {"late-binding", "arrow-function"}),
        # logic
        ("python", "flags = (mask & 0b1111) | (1 << 3)", {"bitwise", "bit-shift"}),
        ("javascript", "const flags = (mask & 0b1111) | (1 << 3);", {"bitwise", "bit-shift"}),
        ("python", "for item in items:\n    pass\nelse:\n    print('none')", {"for-else"}),
        ("python", "ok = 1 < x < 5", {"chained-comparison"}),
    ],
)
def test_the_brain_pack_words_are_found_in_representative_snippets(lang, code, expect):
    got = set(ids(find_words(code, lang, limit=60)))
    assert expect <= got, (expect - got, sorted(got))


QUIET = {
    "python": [
        "x = 5\nprint(x)", "name = input()\nprint('hi', name)", "if x > 3:\n    print('big')",
        "total = 0\nfor n in nums:\n    total += n\nprint(total)", "def add(a, b):\n    return a + b\nprint(add(1, 2))",
        "words = ['a', 'b']\nprint(len(words))", "for i in range(3):\n    print(i)", "d = {'a': 1}\nprint(d['a'])",
        "while n > 1:\n    n //= 2", "a = [3, 1, 2]\na.append(4)\nprint(a[0])",
        "class Dog:\n    def __init__(self, name):\n        pass", "x = 0.1 + 0.2\nprint(x == 0.3)",
    ],
    "javascript": [
        "const x = 5;\nconsole.log(x);", "if (x > 3) { console.log('big'); }",
        "let total = 0;\nfor (const n of nums) { total += n; }\nconsole.log(total);",
        "function add(a, b) { return a + b; }\nconsole.log(add(1, 2));", "const words = ['a', 'b'];\nconsole.log(words.length);",
        "for (let i = 0; i < 3; i++) { console.log(i); }", "const o = { a: 1 };\nconsole.log(o.a);",
        "const f = (a, b) => a + b;", "if (x = 3) { go(); }", "arr.push(4);\nconsole.log(arr[0]);",
        "class Dog {\n  bark() { return 'woof'; }\n}",
    ],
}


@pytest.mark.parametrize("lang", CLASSIC)
def test_plain_code_does_not_wake_the_brain_pack_vocabulary(lang):
    """Plain snippets show the everyday words; the specialised cards need their own tell-tale syntax."""
    new = _brain_ids()[lang]
    for snippet in QUIET[lang]:
        code = snippet
        noisy = [w for w in ids(find_words(code, lang, limit=80)) if w in new]
        assert not noisy, (code, noisy)


@pytest.mark.parametrize("lang", CLASSIC)
def test_generic_brain_words_are_never_loud(lang):
    """Words that are everywhere ('sum', 'state', 'counter', 'character'...) have no detection or a low priority."""
    loud = [e.id for e in glossary.all_entries(lang) if e.id in _brain_ids()[lang] and e.priority > 70]
    assert loud == [] or set(loud) <= {"mutable-default"}, loud
    for word in ("sum", "state", "counter", "flag", "character", "bug", "binary", "division", "whitespace", "default-value"):
        item = lookup(lang, word)
        assert item is not None and item.priority <= 50, (lang, word)


DART_SINK = (
    "import 'dart:math' as math;\n"
    "sealed class Shape { const Shape(); }\n"
    "class Dog extends Animal with Walker implements Pet {\n  static int count = 0;\n  late final String name;\n"
    "  Dog._(this.name);\n  factory Dog(String n) => Dog._(n);\n  @override\n"
    "  String toString() => 'Dog($name)';\n  String? get nick => name?.substring(0, 1) ?? 'x';\n}\n"
    "extension on String { bool get big => length > 3; }\n"
    "Future<void> main() async {\n  try {\n    final xs = [for (var i = 0; i < 9; i++) if (i.isOdd) i, ...?more];\n"
    "    var t = xs.map((n) => n * 2).where((n) => n % 3 ~/ 1 > 0).fold<int>(0, (a, b) => a + b);\n"
    "    var (a, b) = (1, 2);\n    var s = switch (a) { 1 when b > 1 => 'x', _ => 'y' };\n"
    "    await for (final v in Stream.fromIterable(xs)) { print(v!); }\n"
    "  } on FormatException catch (e, st) {\n    rethrow;\n  } finally {\n    cascade()..a()..b();\n  }\n}\n"
    "class W extends State<X> {\n  @override\n  void initState() { super.initState(); }\n"
    "  @override\n  Widget build(BuildContext context) => Scaffold(body: Center(child: Column(children: [\n"
    "    Expanded(child: ListView.builder(itemBuilder: (c, i) => Text('$i'))), Stack(children: [Positioned(left: 1, child: Spacer())]),\n"
    "    TextField(controller: TextEditingController()), Padding(padding: EdgeInsets.all(8)),\n"
    "  ])));\n}\n"
)


def test_find_words_never_exceeds_the_limit_with_the_whole_vocabulary_in_play():
    sink = {
        "python": (
            "class Dog(Animal):\n    count = 0\n    def __init__(self, name, tags=[]):\n        super().__init__()\n"
            "        self.name = name\n    def __str__(self):\n        return f'{self.name:>8}'\n"
            "try:\n    x = [n * n for n in sorted(nums, key=lambda v: -v) if n & 1]\n    y = 1 << 3 | 0b101\n"
            "except (KeyError, ValueError, ZeroDivisionError) as e:\n    print(e)\n"
            "for a in range(0, 10, 2):\n    for b in a[::-1]:\n        break\n    else:\n        print(isinstance(a, int))\n"
            "total = sum(map(int, '1 2'.split())) + max(nums, key=len)\n"
        ),
        "javascript": (
            "class Dog extends Animal {\n  static count = 0;\n  constructor(name, tags = []) {\n    super();\n"
            "    this.name = name;\n  }\n  toString() { return `${this.name}`; }\n}\n"
            "try {\n  const x = nums.filter((n) => n & 1).map((n) => n * n).sort((a, b) => a - b);\n  const y = 1 << 3 | 0b101;\n"
            "} catch (e) {\n  if (e instanceof TypeError || e instanceof RangeError) console.log(e.stack);\n}\n"
            "for (let a = 0; a < 10; a += 2) {\n  for (const [i, b] of items.entries()) {\n    break;\n  }\n}\n"
            "const total = nums.reduce((t, n) => t + n, 0) + Math.max(...nums) + items.at(-1);\n"
        ),
        "dart": DART_SINK,
    }
    for lang in LANGS:
        for limit in (1, 2, 3, 5, 8, 13, 40):
            got = find_words(sink[lang], lang, limit=limit)
            assert len(got) <= limit and len(set(ids(got))) == len(got), (lang, limit)
        # a context's words still come first, whatever else matches
        for activity in (a for a in ACTIVITIES if a.id not in ORIGINAL_SEVEN):
            want = ids(words_for_context(activity.id, lang))
            got = ids(find_words(sink[lang], lang, context=activity.id, limit=40))
            assert got[: len(want)] == want, (lang, activity.id)
            assert len(got) <= 40


def test_a_derived_context_reaches_the_route_and_explain():
    got = server.glossary_words(language="python", context="str_check").words
    assert [w.id for w in got][:3] == ["string", "comparison", "palindrome"]
    assert "range" not in [w.id for w in server.glossary_words(language="javascript", context="loop_range").words]
    r = explain("print(1)", "python", context="cls_inherit")
    assert [w.id for w in r.words][:5] == ["inheritance", "override", "subclass", "super", "method-resolution-order"]
    assert all(w.language == "python" for w in r.words)


def test_a_class_with_several_methods_is_read_quickly():
    """A detection regex once backtracked without end on a class with a few one-line methods."""
    import time

    methods = "".join(f"    def m{i}(self, x):\n        return x + {i}\n" for i in range(40))
    code = "class Big:\n" + methods + "def f(n):\n    if n:\n        return f(n - 1)\n"
    started = time.perf_counter()
    got = ids(find_words(code, "python", limit=60))
    assert time.perf_counter() - started < 2.0
    assert "recursion" in got
    js = "class Big {\n" + "".join(f"  m{i}(x) {{ return x + {i}; }}\n" for i in range(40)) + "}\n"
    started = time.perf_counter()
    find_words(js, "javascript", limit=60)
    assert time.perf_counter() - started < 2.0
    started = time.perf_counter()
    find_words("for a in b:\n" + "    x = 1\n" * 300, "python", limit=60)
    find_words("for (const a of b) {\n" + "  x = 1;\n" * 300 + "}", "javascript", limit=60)
    find_words("for (var a in b) {\n" + "  x = 1;\n" * 300 + "}", "dart", limit=60)
    assert time.perf_counter() - started < 3.0
    # Dart: a class of 40 one-line methods, a long list literal, deeply nested widgets and a long chain
    started = time.perf_counter()
    dart_class = "class Big {\n" + "".join(f"  int m{i}(int x) => x + {i};\n" for i in range(40)) + "}\n"
    got = ids(find_words(dart_class, "dart", limit=60))
    assert "class" in got and "arrow-function" in got
    find_words("var xs = [" + ", ".join(str(i) for i in range(3000)) + "];", "dart", limit=60)
    find_words("Widget w = " + "Padding(child: " * 150 + "Text('x')" + ")" * 150 + ";", "dart", limit=60)
    find_words("var r = xs" + ".map((n) => n + 1)" * 300 + ";", "dart", limit=60)
    find_words("x" + "?" * 400 + "." * 400 + "!" * 400 + "<" * 400 + "," * 400, "dart", limit=60)
    assert time.perf_counter() - started < 4.0


# ── The API ─────────────────────────────────────────────────────────────

def explain(code: str, language: str = "", context: str = "") -> ExplainResponse:
    return server.explain(ExplainRequest(code=code, language=language, context=context))


def test_explain_returns_words_for_python():
    r = explain("items = []\nif not items:\n    print('empty')\n", "python")
    assert r.ok and r.words
    got = [w.id for w in r.words]
    assert "falsy" in got and "truthy" in got
    falsy = next(w for w in r.words if w.id == "falsy")
    assert falsy.language == "python" and falsy.counts_false and falsy.example and falsy.example_output
    assert all(ref.term for w in r.words for ref in w.see_also)


@needs_node
def test_explain_returns_words_for_javascript_and_context_comes_first():
    r = explain('console.log((0) ? "truthy" : "falsy");', "javascript", context="truthy")
    assert [w.id for w in r.words][:2] == ["truthy", "falsy"]
    assert all(w.language == "javascript" for w in r.words)
    assert next(w for w in r.words if w.id == "falsy").counts_false[-1] == "NaN"


def test_explain_with_no_context_still_works_and_old_fields_are_unchanged():
    code = "total = 0\nfor n in [1, 2, 3]:\n    total += n\nprint(total)\n"
    with_words = explain(code, "python")
    plain = ExplainResponse(**explain_code(code))
    assert with_words.words
    assert with_words.model_dump(exclude={"words"}) == plain.model_dump(exclude={"words"})
    assert ExplainRequest(code="x").context == ""


def test_explain_for_a_language_without_a_reader_has_no_words():
    r = explain("SELECT 1;", "sql")
    assert r.ok is False and r.words == []


def test_explain_for_dart_has_no_reader_but_still_gets_its_dart_words():
    """Dart has a glossary but no explainer: the answer is still the honest 'no reader yet', and the words (which
    are about the code, not about the missing walkthrough) ride along, from the one place in the handler."""
    r = explain("String? name;\nprint(name ?? 'guest');\n", "dart")
    assert r.ok is False and "no reader" in r.summary
    got = [w.id for w in r.words]
    assert "null-coalescing" in got and "nullable-type" in got, got
    assert r.words and all(w.language == "dart" for w in r.words)
    assert [w.id for w in explain("x", "dart", context="dart_null").words][:3] == [
        "short-circuit", "default-value", "null-aware-access"]


def test_words_are_added_in_the_handler_only():
    src = Path(server.__file__).read_text(encoding="utf-8")
    assert src.count("glossary.find_words(") == 1
    for reader in ("code_coach/explain.py", "code_coach/explain_js.py", "code_coach/farm/explain_farm.py"):
        assert "glossary" not in (ROOT / reader).read_text(encoding="utf-8"), reader


def test_the_farm_language_is_given_python_words():
    r = explain("if not can_harvest():\n    pass\n", "tfwr")
    if r.ok:  # the farm reader may be missing on a machine; when it answers, words ride along
        assert any(w.id in ("truthy", "falsy") for w in r.words)
        assert all(w.language == "python" for w in r.words)


def test_glossary_route_one_word_a_context_or_a_whole_language():
    one = server.glossary_words(language="python", term="falsy").words
    assert [w.id for w in one] == ["falsy"] and one[0].counts_false
    assert [w.id for w in server.glossary_words(language="javascript", term="===").words] == ["strict-equality"]
    ctx = server.glossary_words(language="python", context="loops").words
    assert [w.id for w in ctx][:3] == ["loop", "iteration", "off-by-one"]
    assert len(server.glossary_words(language="python").words) == len(glossary.all_entries("python"))
    # never an error
    assert server.glossary_words(language="cobol", term="falsy").words == []
    assert server.glossary_words(language="python", term="nonsense").words == []
    assert server.glossary_words().words == []
    # Dart is a third glossary language
    assert [w.id for w in server.glossary_words(language="dart", term="??").words] == ["null-coalescing"]
    assert [w.id for w in server.glossary_words(language="dart", term="~/").words] == ["truncating-division"]
    assert [w.id for w in server.glossary_words(language="dart", context="dart_null").words][:3] == [
        "short-circuit", "default-value", "null-aware-access"]
    assert len(server.glossary_words(language="dart").words) == len(glossary.all_entries("dart")) >= 200
    assert all(w.language == "dart" for w in server.glossary_words(language="dart", context="fl_flex").words)


# ── The front end ───────────────────────────────────────────────────────

HARNESS = r"""
import * as W from "./words.mjs";
import { readFileSync } from "node:fs";

const input = JSON.parse(readFileSync(process.argv[2], "utf8"));
const w = (id, extra = {}) => ({
  id, term: id, language: "python", definition: "d", rules: [], example: "", example_output: "",
  see_also: [], counts_false: [], counts_true: [], ...extra,
});
const a = w("a"), b = w("b"), c = w("c");
const out = {};

out.initial = [W.initialOpen([]), W.initialOpen([a]), W.initialOpen([a, b, c])];
out.toggle = [W.toggleOpen([], "a"), W.toggleOpen(["a"], "a"), W.toggleOpen(["a", "b"], "a"), W.toggleOpen(["a"], "b")];
out.reveal = [W.revealOpen([], "a"), W.revealOpen(["a"], "a"), W.revealOpen(["a"], "b")];
out.extras = [
  W.withExtras([a, b], []).map((x) => x.id),
  W.withExtras([a, b], [c]).map((x) => x.id),
  W.withExtras([a, b], [b, c, c]).map((x) => x.id),
  W.withExtras([], [c, a]).map((x) => x.id),
];
out.action = [W.seeAlsoAction([a, b], "a"), W.seeAlsoAction([a, b], "z"), W.seeAlsoAction([], "a")];
out.dom = [W.cardDomId("brain", "off-by-one"), W.cardDomId("a b", "x.y"), W.cardDomId("s", "a") === W.cardDomId("t", "a")];
const truthy = w("truthy", { counts_false: ["0", "[]"], counts_true: ['"0"'] });
out.columns = [W.columnsOf(a), W.columnsOf(truthy)];
out.question = [
  W.showsQuestionWords(true, [a]), W.showsQuestionWords(false, [a]), W.showsQuestionWords(true, []),
  W.showsQuestionWords(true, null),
];
console.log(JSON.stringify(out));
"""


@functools.cache
def web_results() -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="glossary_web_"))
    try:
        (tmp / "harness.mjs").write_text(HARNESS, encoding="utf-8")
        (tmp / "in.json").write_text("{}", encoding="utf-8")
        built = subprocess.run(
            [NODE, str(ESBUILD), str(SRC / "lib" / "words.ts"), "--bundle", "--format=esm", "--platform=node",
             f"--outfile={tmp / 'words.mjs'}", "--log-level=error"],
            capture_output=True, text=True, timeout=120,
        )
        assert built.returncode == 0, built.stderr
        ran = subprocess.run([NODE, str(tmp / "harness.mjs"), str(tmp / "in.json")], capture_output=True,
                             text=True, timeout=120, cwd=tmp)
        assert ran.returncode == 0, ran.stderr[-3000:]
        return json.loads(ran.stdout.strip().splitlines()[-1])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


web = pytest.mark.skipif(NODE is None or not ESBUILD.exists(), reason="needs node and web/node_modules/esbuild")


@web
def test_the_first_word_is_open_and_the_rest_are_shut():
    assert web_results()["initial"] == [[], ["a"], ["a"]]


@web
def test_toggling_and_revealing_cards():
    r = web_results()
    assert r["toggle"] == [["a"], [], ["b"], ["a", "b"]]
    assert r["reveal"] == [["a"], ["a"], ["a", "b"]]


@web
def test_fetched_words_join_the_list_once_and_after_it():
    r = web_results()
    assert r["extras"] == [["a", "b"], ["a", "b", "c"], ["a", "b", "c"], ["c", "a"]]
    assert r["action"] == ["show", "fetch", "fetch"]


@web
def test_card_ids_are_clean_and_unique_per_list():
    r = web_results()["dom"]
    assert r[0] == "word-brain-off-by-one"
    assert re.fullmatch(r"[A-Za-z0-9_-]+", r[1])
    assert r[2] is False


@web
def test_truthy_and_falsy_get_two_columns_and_other_words_none():
    cols = web_results()["columns"]
    assert cols[0] == []
    assert [c["title"] for c in cols[1]] == ["Counts as false", "Counts as true"]
    assert cols[1][0]["items"] == ["0", "[]"] and cols[1][1]["items"] == ['"0"']


@web
def test_the_question_line_shows_only_on_a_miss_with_words():
    assert web_results()["question"] == [True, False, False, False]


# ── Static checks: the section is rendered everywhere an explanation is ──

def read(rel: str) -> str:
    return (SRC / rel).read_text(encoding="utf-8")


@pytest.mark.parametrize("rel", ["components/ExplainPanel.tsx", "components/BrainTools.tsx",
                                 "components/Workbook.tsx", "components/Katas.tsx"])
def test_every_explanation_view_renders_the_words(rel):
    text = read(rel)
    assert "WordsUsed" in text and "<WordsUsed" in text, rel


def test_brain_drills_passes_the_activity_as_context_and_shows_chips_on_a_miss():
    tools = read("components/BrainTools.tsx")
    assert re.search(r"explainCode\(what\.code, language, activityId\)", tools)
    assert "ws-btn on" in tools and "Hide explain" in tools, "the Explain button is still a toggle"
    drills = read("components/BrainDrills.tsx")
    assert re.search(r"record\.right \? null : \(\s*<QuestionWords", drills)


def test_the_words_stylesheet_never_lets_the_page_scroll_sideways():
    css = read("styles/words.css")
    assert "overflow-x: auto" in css, "code scrolls inside its own card"
    assert "min-width: 0" in css and "overflow-wrap: anywhere" in css
    assert not re.search(r"(?<![-\w])(?:min-)?width:\s*\d{3,}px", css), "no fixed wide widths"


# ── Dart (and Flutter): the third glossary language ─────────────────────
# Dart words live in terms_dart_*.py (the language) and terms_flutter.py (Flutter, which is Dart). Every EXAMPLE is
# run by test_example_prints_exactly_what_the_entry_says (one dart run). Every runnable RULE is backed by a program
# below, run for real in ONE more dart run; the Flutter layout/state rules by programs run in ONE flutter test. The
# expected output is written here by hand, never read from the entries.

CE = "COMPILE ERROR"

#: (name = "<entry id>[+<entry id>]: the claim", program, expected). A program without `main(` is the body of main
#: (the Brain Drills convention); CE means "does not compile" (the message is not compared).
DART_RULE_CHECKS: list[tuple[str, str, str]] = [
    # ── null safety ──
    ("null-safety: a plain int cannot be null", r"""
        int x = null;
        print(x);
    """, CE),
    ("null-safety: using a nullable as if it had a value does not compile", r"""
        bool f(int? n) => n.isEven;
        print(f(2));
    """, CE),
    ("null: print(null) shows null", r"""
        print(null);
    """, "null"),
    ("null: if (null) does not compile, there is no falsy", r"""
        if (null) {
          print('x');
        }
    """, CE),
    ("nullable-type: List<int?> versus List<int>?", r"""
        List<int?> a = [1, null];
        List<int>? b;
        print(a);
        print(b);
    """, "[1, null]\nnull"),
    ("nullable-type: n + 1 does not compile when n is int?", r"""
        int f(int? n) => n + 1;
        print(f(1));
    """, CE),
    ("null-assertion: the failing ! is a TypeError", r"""
        String? t = [null][0];
        try {
          t!;
        } on TypeError {
          print('TypeError');
        }
    """, "TypeError"),
    ("null-coalescing: the right side is worked out only when needed", r"""
        int calls = 0;
        int f() {
          calls++;
          return 1;
        }
        int? a = 5;
        print(a ?? f());
        print(calls);
    """, "5\n0"),
    ("null-coalescing: it chains", r"""
        int? a;
        int? b;
        print(a ?? b ?? 3);
    """, "3"),
    ("null-coalescing: only null triggers it", r"""
        String? e = '';
        bool? f = false;
        print('[${e ?? 'x'}] ${f ?? true}');
    """, "[] false"),
    ("null-aware-access: the rest of the chain is skipped", r"""
        String? s;
        print(s?.toUpperCase().length);
    """, "null"),
    ("null-aware-access: the result is nullable", r"""
        String? s;
        int n = s?.length;
        print(n);
    """, CE),
    ("null-aware-access: ?[ ] indexing", r"""
        List<int>? xs;
        print(xs?[0]);
    """, "null"),
    ("null-aware-assignment: the right side is skipped when a has a value", r"""
        int? a = 1;
        int calls = 0;
        int f() {
          calls++;
          return 9;
        }
        a ??= f();
        print('$a $calls');
    """, "1 0"),
    ("late: reading before assignment throws a LateError", r"""
        class A {
          late int x;
        }
        void main() {
          try {
            print(A().x);
          } catch (e) {
            print(e.runtimeType);
          }
        }
    """, "LateError"),
    ("late: a late final can be set once", r"""
        class A {
          late final int x;
        }
        void main() {
          var a = A();
          a.x = 1;
          try {
            a.x = 2;
          } catch (e) {
            print(e.runtimeType);
          }
          print(a.x);
        }
    """, "LateError\n1"),
    ("final: assigning twice does not compile", r"""
        final x = 1;
        x = 2;
        print(x);
    """, CE),
    ("final: the value can be worked out at run time", r"""
        final now = DateTime.now();
        print(now is DateTime);
    """, "true"),
    ("const: needs a compile-time value", r"""
        const t = DateTime.now();
        print(t);
    """, CE),
    ("const: changing a const list throws UnsupportedError", r"""
        const xs = [1, 2];
        try {
          xs.add(3);
        } catch (e) {
          print(e.runtimeType);
        }
    """, "UnsupportedError"),
    ("var: the type is fixed by the first value", r"""
        var n = 3;
        n = 'three';
        print(n);
    """, CE),
    ("var: var x with no value is dynamic", r"""
        var x;
        x = 1;
        x = 'a';
        print(x);
    """, "a"),
    ("type-promotion: a field is not promoted", r"""
        class A {
          int? n;
          void f() {
            if (n != null) print(n + 1);
          }
        }
        void main() {
          A().f();
        }
    """, CE),
    ("type-promotion: an early exit promotes the rest", r"""
        int f(String? s) {
          if (s == null) return 0;
          return s.length;
        }
        print(f(null));
        print(f('ab'));
    """, "0\n2"),
    ("dynamic: Object? lets you use only what every object has", r"""
        Object? o = 'hi';
        print(o.length);
    """, CE),
    ("dynamic: a missing member on dynamic fails when it runs", r"""
        dynamic d = 5;
        try {
          d.nope();
        } on NoSuchMethodError {
          print('nsm');
        }
    """, "nsm"),
    # ── types ──
    ("integer: an int wraps around at 64 bits", r"""
        int big = 9223372036854775807;
        print(big + 1);
    """, "-9223372036854775808"),
    ("integer: a double never fits an int variable", r"""
        int x = 2.5;
        print(x);
    """, CE),
    ("float: 0 / 0 is NaN", r"""
        print(0 / 0);
    """, "NaN"),
    ("num: the shared num methods", r"""
        num a = -3;
        print(a.abs());
        print(a.compareTo(2) < 0);
        print(a.toDouble());
    """, "3\ntrue\n-3.0"),
    ("boolean: if (1) does not compile", r"""
        if (1) {
          print('x');
        }
    """, CE),
    ("boolean: if of a string does not compile", r"""
        if ('') {
          print('x');
        }
    """, CE),
    ("string: a string cannot be assigned into", r"""
        var s = 'abc';
        s[0] = 'x';
        print(s);
    """, CE),
    ("string: single and double quotes are the same", r"""
        print('a' == "a");
        print('it\'s');
        print("it's");
    """, "true\nit's\nit's"),
    ("character: a character is a String of length 1", r"""
        print('abc'[1].runtimeType);
    """, "String"),
    ("list: a fixed-length list cannot grow", r"""
        var xs = List.filled(3, 0);
        xs[0] = 5;
        try {
          xs.add(1);
        } catch (e) {
          print(e.runtimeType);
        }
        print(xs);
    """, "UnsupportedError\n[5, 0, 0]"),
    ("set: union and difference", r"""
        print({1, 2}.union({2, 3}));
        print({1, 2, 3}.difference({2}));
    """, "{1, 2, 3}\n{1, 3}"),
    ("dictionary: assigning to an existing key replaces its value", r"""
        var m = {'a': 1};
        m['a'] = 2;
        m['a'] = 3;
        print(m);
        print(m.length);
    """, "{a: 3}\n1"),
    ("dictionary: a missing key makes the result nullable", r"""
        var m = {'a': 1};
        int v = m['a'];
        print(v);
    """, CE),
    ("dictionary: entries, keys and values", r"""
        var m = {'a': 1, 'b': 2};
        for (final e in m.entries) {
          print('${e.key}=${e.value}');
        }
    """, "a=1\nb=2"),
    ("record: a record cannot be changed", r"""
        var p = (1, 2);
        p.$1 = 5;
        print(p);
    """, CE),
    ("record: named fields are equal by value", r"""
        print((x: 1, y: 2) == (x: 1, y: 2));
        (int, String) f() => (1, 'a');
        var (n, s) = f();
        print('$n$s');
    """, "true\n1a"),
    ("enum: a switch statement over an enum must cover every value", r"""
        enum C { a, b }
        void main() {
          var c = C.a;
          switch (c) {
            case C.a:
              print('a');
          }
        }
    """, CE),
    ("enum: enums can have fields and constructors", r"""
        enum P {
          small(1),
          big(10);
          final int n;
          const P(this.n);
        }
        void main() {
          print(P.big.n + P.small.n);
        }
    """, "11"),
    ("typedef: it is another name for the same type", r"""
        typedef IntList = List<int>;
        void main() {
          IntList a = [1];
          List<int> b = a;
          print(b);
        }
    """, "[1]"),
    ("type-conversion: toInt cuts the decimals, '5' + 1 does not compile", r"""
        print(3.7.toInt());
    """, "3"),
    ("type-conversion: a string plus an int does not compile", r"""
        print('5' + 1);
    """, CE),
    ("rounding: roundToDouble gives a double", r"""
        print(2.5.roundToDouble());
    """, "3.0"),
    ("division: a double divided by zero is Infinity", r"""
        print(1.0 / 0.0);
        print(-1 / 0);
    """, "Infinity\n-Infinity"),
    ("division: whole-number division by zero throws", r"""
        try {
          print(1 ~/ 0);
        } catch (e) {
          print(e is Error || e is Exception);
        }
    """, "true"),
    ("truncating-division: the quotient and remainder add back up", r"""
        print((17 ~/ 5) * 5 + 17 % 5);
        print(-7 ~/ 2 == (-7 / 2).truncate());
    """, "17\ntrue"),
    ("modulo: an even test", r"""
        print(6 % 2 == 0 && 6.isEven);
    """, "true"),
    ("bitwise: & and | on bools do not skip the right side", r"""
        bool f() {
          print('f ran');
          return true;
        }
        print(false & f());
        print(true || f());
    """, "f ran\nfalse\ntrue"),
    ("cascade: ?.. does nothing for null", r"""
        StringBuffer? sb;
        sb?..write('a');
        print(sb);
    """, "null"),
    ("cascade: the value of a cascade is the object", r"""
        var xs = [3, 1]..sort();
        print(xs);
    """, "[1, 3]"),
    ("spread: a shallow copy shares the inner items", r"""
        var a = [[1]];
        var b = [...a];
        b[0].add(2);
        print(a);
    """, "[[1, 2]]"),
    ("spread: ...? with null gives nothing", r"""
        List<int>? m;
        print([...?m]);
    """, "[]"),
    ("collection-if-for: sets and maps too", r"""
        print({1, if (true) 2, if (false) 3});
        print({for (var i = 0; i < 2; i++) i: i * i});
    """, "{1, 2}\n{0: 0, 1: 1}"),
    ("ternary: the condition must be a bool", r"""
        print(1 ? 'a' : 'b');
    """, CE),
    ("type-check: only null is not an Object", r"""
        Object? o = null;
        print(o is Object);
        print(3 is Object);
        print(null is Object?);
    """, "false\ntrue\ntrue"),
    # ── functions ──
    ("function: a function is a value", r"""
        int twice(int n) => n * 2;
        var f = twice;
        print(f(3));
    """, "6"),
    ("parameter: too few positional arguments does not compile", r"""
        int add(int a, int b) => a + b;
        print(add(1));
    """, CE),
    ("named-parameter: a non-required named parameter needs a default or nullable type", r"""
        void f({int n}) {}
        f();
    """, CE),
    ("required: leaving a required parameter out does not compile", r"""
        String f({required String a}) => a;
        print(f());
    """, CE),
    ("optional-positional-parameter: [ ] and { } cannot be mixed", r"""
        void f([int a = 1], {int b = 2}) {}
        f();
    """, CE),
    ("default-parameter: a non-constant default does not compile", r"""
        int f([List<int> a = []]) => a.length;
        print(f());
    """, CE),
    ("default-parameter: a const default is the same constant every call", r"""
        List<int> f([List<int> a = const []]) => a;
        var d = f();
        try {
          d.add(1);
        } catch (e) {
          print('const list');
        }
        print(identical(f(), f()));
    """, "const list\ntrue"),
    ("default-value: putIfAbsent stores and returns", r"""
        var m = <String, int>{};
        print(m.putIfAbsent('a', () => 5));
        print(m);
    """, "5\n{a: 5}"),
    ("arrow-function: only one expression fits", r"""
        int f(int n) => if (n > 0) 1;
        print(f(1));
    """, CE),
    ("callback: a callback given to something asynchronous runs later", r"""
        Future(() => print('callback'));
        print('after');
    """, "after\ncallback"),
    ("return: a non-void function must return on every path", r"""
        int f(int n) {
          if (n > 0) return 1;
        }
        print(f(1));
    """, CE),
    ("return: several values through a record", r"""
        (int, String) f() => (1, 'a');
        var (n, s) = f();
        print('$n$s');
    """, "1a"),
    ("main-function: Future<void> main() async", r"""
        Future<void> main() async {
          await Future<void>.value();
          print('ran');
        }
    """, "ran"),
    # ── classes ──
    ("instance: two instances with equal fields are different objects", r"""
        class P {
          final int x;
          P(this.x);
        }
        void main() {
          print(P(1) == P(1));
          print(P(1).runtimeType);
        }
    """, "false\nP"),
    ("static-method: a static method cannot see the fields", r"""
        class A {
          int n = 1;
          static int f() => n;
        }
        void main() {
          print(A.f());
        }
    """, CE),
    ("this: a static method has no this", r"""
        class A {
          static int f() => this.hashCode;
        }
        void main() {
          print(A.f());
        }
    """, CE),
    ("constructor: a class without a constructor gets a free one", r"""
        class A {
          int x = 1;
        }
        void main() {
          print(A().x);
        }
    """, "1"),
    ("initializing-formal: named with a default", r"""
        class P {
          final int x;
          P({this.x = 4});
        }
        void main() {
          print(P().x);
          print(P(x: 9).x);
        }
    """, "4\n9"),
    ("initializing-formal: a final field must be set", r"""
        class P {
          final int x;
          P();
        }
        void main() {
          print(P().x);
        }
    """, CE),
    ("named-constructor: constructors are not inherited", r"""
        class A {
          A.named();
        }
        class B extends A {}
        void main() {
          B.named();
        }
    """, CE),
    ("initializer-list: runs before the body", r"""
        class R {
          final int a, b;
          R(int x) : a = x, b = x * 2 {
            print('body');
          }
        }
        void main() {
          var r = R(3);
          print('${r.a} ${r.b}');
        }
    """, "body\n3 6"),
    ("initializer-list: it cannot use this", r"""
        class R {
          int a, b;
          R() : a = 1, b = this.a;
        }
        void main() {
          R();
        }
    """, CE),
    ("factory-constructor: a factory has no this", r"""
        class A {
          int x = 1;
          factory A() => this;
        }
        void main() {
          A();
        }
    """, CE),
    ("factory-constructor: it can pick a subclass", r"""
        abstract class S {
          factory S(bool b) => b ? C1() : C2();
        }
        class C1 implements S {}
        class C2 implements S {}
        void main() {
          print(S(true).runtimeType);
          print(S(false).runtimeType);
        }
    """, "C1\nC2"),
    ("const-constructor: every field must be final", r"""
        class P {
          int x;
          const P(this.x);
        }
        void main() {
          print(const P(1).x);
        }
    """, CE),
    ("getter-setter: a getter with no setter is read-only", r"""
        class A {
          int get x => 1;
        }
        void main() {
          A().x = 2;
        }
    """, CE),
    ("inheritance: a class extends only one class", r"""
        class A {}
        class B {}
        class C extends A, B {}
        void main() {}
    """, CE),
    ("abstract-class: it cannot be built", r"""
        abstract class S {}
        void main() {
          S();
        }
    """, CE),
    ("abstract-class: a concrete subclass must supply the bodiless method", r"""
        abstract class S {
          double area();
        }
        class T extends S {}
        void main() {
          T();
        }
    """, CE),
    ("interface: implements copies no code", r"""
        class A {
          void f() {}
        }
        class B implements A {}
        void main() {
          B();
        }
    """, CE),
    ("mixin: a mixin has no constructor", r"""
        mixin M {
          M();
        }
        void main() {}
    """, CE),
    ("mixin: on limits who can use it", r"""
        class A {}
        mixin M on A {}
        class B with M {}
        void main() {
          B();
        }
    """, CE),
    ("extension-method: not on a dynamic variable", r"""
        extension on String {
          int get two => 2;
        }
        void main() {
          String s = 'a';
          print(s.two);
          dynamic d = 'a';
          try {
            print(d.two);
          } on NoSuchMethodError {
            print('not on dynamic');
          }
        }
    """, "2\nnot on dynamic"),
    ("generics: a bound limits the type", r"""
        T big<T extends num>(T a, T b) => a > b ? a : b;
        print(big('a', 'b'));
    """, CE),
    ("equality: there is no ===", r"""
        print(1 === 1);
    """, CE),
    ("equality: lists compare by identity, const lists are one object", r"""
        print([1] == [1]);
        print(const [1] == const [1]);
    """, "false\ntrue"),
    ("hash-code: strings, numbers and records have correct ones", r"""
        print('a'.hashCode == 'a'.hashCode && (1, 2).hashCode == (1, 2).hashCode && 1.hashCode == 1.hashCode);
    """, "true"),
    ("identity: List.of copies", r"""
        var a = [1];
        var b = List.of(a);
        b.add(2);
        print(a);
        print(b);
    """, "[1]\n[1, 2]"),
    # ── patterns ──
    ("pattern: a list pattern of the wrong length throws", r"""
        try {
          var [a, b] = [1, 2, 3];
          print(a + b);
        } catch (e) {
          print('no match');
        }
    """, "no match"),
    ("pattern: named record fields can be picked", r"""
        var (x: px, y: _) = (x: 1, y: 2);
        print(px);
    """, "1"),
    ("pattern: relational and logical patterns", r"""
        String f(int n) => switch (n) {
          < 0 => 'neg',
          0 || 1 => 'tiny',
          > 100 && < 200 => 'hundreds',
          _ => 'other',
        };
        print(f(-5));
        print(f(1));
        print(f(150));
        print(f(500));
    """, "neg\ntiny\nhundreds\nother"),
    ("switch: break is optional", r"""
        switch (1) {
          case 1:
            print('a');
            break;
          case 2:
            print('b');
        }
    """, "a"),
    ("switch-expression: it must be exhaustive", r"""
        var s = switch (3) { 1 => 'a' };
        print(s);
    """, CE),
    ("if-case: with a when test", r"""
        Object v = 5;
        if (v case int n when n > 3) {
          print('big $n');
        }
    """, "big 5"),
    ("sealed-class: it cannot be built", r"""
        sealed class S {}
        void main() {
          S();
        }
    """, CE),
    ("sealed-class: missing a subclass in the switch does not compile", r"""
        sealed class S {}
        class A extends S {}
        class B extends S {}
        int f(S s) => switch (s) {
          A() => 1,
        };
        void main() {
          print(f(A()));
        }
    """, CE),
    # ── async ──
    ("future: an async function must return a Future", r"""
        int f() async => 1;
        void main() {
          print(f());
        }
    """, CE),
    ("async-await: await only works inside an async function", r"""
        void f() {
          await Future.value(1);
        }
        void main() {
          f();
        }
    """, CE),
    ("async-await: an awaited error is thrown at the await", r"""
        Future<void> main() async {
          try {
            await Future.error('x');
          } catch (e) {
            print('caught $e');
          }
        }
    """, "caught x"),
    ("then: the callback runs after the code that follows", r"""
        Future.value(1).then((_) => print('then'));
        print('sync');
    """, "sync\nthen"),
    ("catch-error: an unhandled Future error is reported as uncaught", r"""
        Future.error('x');
    """, "ERROR String"),
    ("stream: a plain stream can be listened to only once", r"""
        import 'dart:async';
        void main() {
          var c = StreamController<int>();
          c.stream.listen((_) {});
          try {
            c.stream.listen((_) {});
          } on StateError {
            print('once');
          }
          var b = StreamController<int>.broadcast();
          b.stream.listen((_) {});
          b.stream.listen((_) {});
          print('many');
        }
    """, "once\nmany"),
    ("async-generator: the body runs only while someone listens", r"""
        Stream<int> f() async* {
          print('run');
          yield 1;
        }
        void main() {
          var s = f();
          print('made');
        }
    """, "made"),
    ("generator: yield* produces every value of another iterable", r"""
        Iterable<int> f() sync* {
          yield* [1, 2];
          yield 3;
        }
        print(f().toList());
    """, "[1, 2, 3]"),
    # ── errors ──
    ("try-catch: an unmatched error goes up to the caller", r"""
        try {
          try {
            int.parse('x');
          } on RangeError {
            print('inner');
          }
        } on FormatException {
          print('outer');
        }
    """, "outer"),
    ("finally: it runs while an uncaught error travels up", r"""
        try {
          try {
            throw 1;
          } finally {
            print('f');
          }
        } catch (e) {
          print('c $e');
        }
    """, "f\nc 1"),
    ("throw: any object can be thrown", r"""
        try {
          throw 'text';
        } catch (e) {
          print(e);
        }
    """, "text"),
    ("rethrow: only inside a catch", r"""
        void f() {
          rethrow;
        }
        void main() {
          f();
        }
    """, CE),
    ("rethrow: it keeps the original stack trace, throw e does not", r"""
        void origin() {
          throw StateError('x');
        }
        void viaRethrow() {
          try {
            origin();
          } catch (e) {
            rethrow;
          }
        }
        void viaThrow() {
          try {
            origin();
          } catch (e) {
            throw e;
          }
        }
        void main() {
          try {
            viaRethrow();
          } catch (e, st) {
            print(st.toString().contains('origin'));
          }
          try {
            viaThrow();
          } catch (e, st) {
            print(st.toString().contains('origin'));
          }
        }
    """, "true\nfalse"),
    ("exception: on Exception catches only Exceptions", r"""
        try {
          [1][5];
        } on Exception {
          print('exc');
        } catch (e) {
          print('other');
        }
    """, "other"),
    ("exception: a class can implement Exception", r"""
        class MyErr implements Exception {
          final String m;
          MyErr(this.m);
        }
        void main() {
          try {
            throw MyErr('a');
          } on Exception catch (e) {
            print(e is MyErr);
          }
        }
    """, "true"),
    ("index-error: negative positions throw too", r"""
        try {
          [1][-1];
        } on RangeError {
          print('neg');
        }
    """, "neg"),
    ("state-error: reduce on an empty list", r"""
        try {
          <int>[].reduce((a, b) => a + b);
        } on StateError {
          print('empty');
        }
        try {
          <int>[].last;
        } on StateError {
          print('no last');
        }
    """, "empty\nno last"),
    ("type-error: the compiler rejects int x = 'a'", r"""
        int x = 'a';
        print(x);
    """, CE),
    ("stack-trace: StackTrace.current", r"""
        print(StackTrace.current.toString().isNotEmpty);
    """, "true"),
    ("syntax-error: a calling a method that does not exist does not compile", r"""
        var s = 'a';
        s.nope();
    """, CE),
    ("syntax-error: nothing prints if one line does not compile", r"""
        print('hello');
        int x = 'a';
    """, CE),
    # ── strings ──
    ("raw-string: a triple-quoted string spans lines", r"""
        var s = '''one
        two''';
        print(s.split('\n').length);
    """, "2"),
    ("string-buffer: writeln and writeAll", r"""
        var sb = StringBuffer();
        sb.writeln('a');
        print(sb.length);
        print((StringBuffer()..writeAll([1, 2, 3], ', ')).toString());
    """, "2\n1, 2, 3"),
    ("regexp: the first group", r"""
        print(RegExp(r'(\d+)-(\d+)').firstMatch('10-20')!.group(2));
    """, "20"),
    ("padding: the default filler is a space", r"""
        print('a'.padLeft(3) + '|');
    """, "  a|"),
    ("replace: a RegExp as the target", r"""
        print('a1b2'.replaceAll(RegExp(r'\d'), '#'));
    """, "a#b#"),
    ("format: a whole number with one decimal", r"""
        print(5.toStringAsFixed(1));
    """, "5.0"),
    ("string-comparison: < does not work on strings", r"""
        print('apple' < 'banana');
    """, CE),
    ("iterable: any and every", r"""
        print([1, 2].any((x) => x > 1) && [1, 2].every((x) => x > 0));
    """, "true"),
    ("lazy: every read runs the callback again", r"""
        var c = 0;
        var m = [1, 2].map((x) {
          c++;
          return x;
        });
        m.toList();
        m.toList();
        print(c);
    """, "4"),
    ("filter: removeWhere changes the list in place", r"""
        var xs = [1, 2, 3];
        xs.removeWhere((n) => n.isEven);
        print(xs);
    """, "[1, 3]"),
    ("reduce: reduce on an empty list throws, fold does not", r"""
        try {
          <int>[].reduce((a, b) => a + b);
        } on StateError {
          print('empty');
        }
        print(<int>[].fold<int>(7, (a, b) => a + b));
    """, "empty\n7"),
    ("sum: a sum of doubles starts from 0.0", r"""
        print([1.5, 2.5].fold<double>(0.0, (a, b) => a + b));
    """, "4.0"),
    ("sorting: sort returns nothing", r"""
        var xs = [2, 1];
        print(xs.sort());
    """, CE),
    ("to-list: growable false", r"""
        var f = [1].toList(growable: false);
        try {
          f.add(2);
        } catch (e) {
          print('fixed');
        }
    """, "fixed"),
    ("import: an import after other code does not compile", r"""
        void main() {}
        import 'dart:math';
    """, CE),
    # ── the everyday words ──
    ("statement: an if is not an expression", r"""
        var x = true;
        var y = (if (x) 1);
        print(y);
    """, CE),
    ("variable: an undeclared name does not compile", r"""
        print(zzz);
    """, CE),
    ("variable: a non-nullable local must be given a value before it is read", r"""
        int x;
        print(x);
    """, CE),
    ("variable: names are case-sensitive", r"""
        var total = 1;
        var Total = 2;
        print(total + Total);
    """, "3"),
    ("scope: a local name used before its declaration does not compile", r"""
        void main() {
          print(x);
          var x = 1;
        }
    """, CE),
    ("scope: a top-level variable is visible in the whole file", r"""
        int g = 5;
        void main() {
          print(g);
        }
    """, "5"),
    ("recursion: no base case ends in StackOverflowError", r"""
        int f(int n) => f(n + 1) + 1;
        try {
          f(0);
        } catch (e) {
          print(e.runtimeType);
          print(e is Error);
        }
    """, "StackOverflowError\ntrue"),
    ("short-circuit: a null guard", r"""
        int? x;
        print(x != null && x.isEven);
    """, "false"),
    ("comparison: chained comparisons do not compile", r"""
        print(1 < 2 < 3);
    """, CE),
    ("loop: break does not work inside forEach", r"""
        [1].forEach((x) {
          break;
        });
    """, CE),
    ("for-loop: changing a list while looping over it throws", r"""
        var xs = [1, 2, 3];
        try {
          for (final x in xs) {
            xs.add(x);
          }
        } catch (e) {
          print(e.runtimeType);
        }
    """, "ConcurrentModificationError"),
    ("while-loop: do-while runs at least once", r"""
        var n = 0;
        do {
          n++;
        } while (false);
        print(n);
    """, "1"),
    ("slice: ends past the length throw, take and skip are forgiving", r"""
        try {
          [1, 2].sublist(0, 5);
        } on RangeError {
          print('range');
        }
        print([1, 2].take(5).toList());
        print([1, 2].skip(5).toList());
    """, "range\n[1, 2]\n[]"),
    # ── more claims, one program each ──
    ("accumulator: the start value is the answer for an empty input", r"""
        var t = 0;
        for (final n in <int>[]) {
          t += n;
        }
        print(t);
    """, "0"),
    ("argument+evaluate: arguments are worked out before the function runs", r"""
        int f(int a) {
          print('f');
          return a;
        }
        int g(int x) {
          print('g');
          return x;
        }
        print(g(f(1)));
    """, "f\ng\n1"),
    ("assignment: an assignment is an expression whose value is the stored value", r"""
        var x = 1;
        print(x = 5);
        print(x += 2);
    """, "5\n7"),
    ("break-continue: they only affect the innermost loop", r"""
        var c = 0;
        for (var i = 0; i < 3; i++) {
          for (var j = 0; j < 3; j++) {
            if (j == 1) break;
            c++;
          }
        }
        print(c);
    """, "3"),
    ("call-stack: a StackOverflowError is not an Exception", r"""
        int f(int n) => f(n + 1) + 1;
        try {
          f(0);
        } catch (e) {
          print(e is Exception);
        }
    """, "false"),
    ("callable-class: an object with call can be used as a function", r"""
        class A {
          int call(int x) => x + 1;
        }
        void main() {
          Function f = A();
          print(f(3));
        }
    """, "4"),
    ("class: everything is an object, even numbers and null", r"""
        print(3.runtimeType);
        print(null.runtimeType);
    """, "int\nNull"),
    ("closure: it captures the variable, not a copy", r"""
        var n = 1;
        var f = () => n;
        n = 2;
        print(f());
    """, "2"),
    ("comparator: a flipped compareTo sorts downward", r"""
        print([1, 3, 2]..sort((a, b) => b.compareTo(a)));
    """, "[3, 2, 1]"),
    ("condition: only the first true branch of an else-if chain runs", r"""
        var n = 15;
        if (n % 3 == 0) {
          print('a');
        } else if (n % 5 == 0) {
          print('b');
        }
    """, "a"),
    ("control-flow: return leaves the function from inside a loop", r"""
        int f() {
          for (var i = 0; i < 5; i++) {
            if (i == 2) return i;
          }
          return -1;
        }
        print(f());
    """, "2"),
    ("counter: where(test).length counts the matches", r"""
        print([1, 2, 3, 4].where((n) => n.isEven).length);
    """, "2"),
    ("destructuring: a declaration names both parts at once", r"""
        var (name, age) = ('Ann', 30);
        print('$name $age');
    """, "Ann 30"),
    ("error-message: a FormatException has a message", r"""
        try {
          int.parse('q');
        } on FormatException catch (e) {
          print(e.message.isNotEmpty);
        }
    """, "true"),
    ("expression: a switch expression is an expression", r"""
        var v = switch (2) { 2 => 'two', _ => 'x' };
        print(v);
    """, "two"),
    ("float-precision: toStringAsFixed rounds to the decimals asked", r"""
        print(3.14159.toStringAsFixed(2));
        print(0.1 + 0.2 == 0.3);
    """, "3.14\nfalse"),
    ("format-exception: double.parse throws it too", r"""
        try {
          double.parse('x');
        } on FormatException {
          print('fe');
        }
    """, "fe"),
    ("guard-clause: a false guard moves on to the next case", r"""
        String f(int n) => switch (n) {
          int v when v > 5 => 'big',
          int v => 'small',
        };
        print(f(3));
        print(f(9));
    """, "small\nbig"),
    ("higher-order-function: a function can return a function", r"""
        Function adder(int n) => (int x) => x + n;
        print(adder(2)(3));
    """, "5"),
    ("immutable: a final field cannot be reassigned", r"""
        class P {
          final int x;
          P(this.x);
        }
        void main() {
          P(1).x = 2;
        }
    """, CE),
    ("index: strings are indexed too", r"""
        print('abc'[1]);
    """, "b"),
    ("isolate: isolates share no memory", r"""
        import 'dart:isolate';
        int counter = 0;
        Future<void> main() async {
          await Isolate.run(() {
            counter = 5;
            return 0;
          });
          print(counter);
        }
    """, "0"),
    ("iteration: a three-pass loop has i = 0, 1, 2", r"""
        var seen = <int>[];
        for (var i = 0; i < 3; i++) {
          seen.add(i);
        }
        print(seen);
    """, "[0, 1, 2]"),
    ("join: items that are not strings are turned into text", r"""
        print([1, 2].join('+'));
    """, "1+2"),
    ("key: remove deletes the key and its value", r"""
        var m = {'a': 1};
        m.remove('a');
        print(m.containsKey('a'));
    """, "false"),
    ("letter-case: toUpperCase leaves the original alone", r"""
        var s = 'a';
        s.toUpperCase();
        print(s);
    """, "a"),
    ("map: the result has the transformed items", r"""
        print(['ann', 'bo'].map((s) => s.length).toList());
    """, "[3, 2]"),
    ("method: a method uses the object's fields", r"""
        class C {
          int n = 2;
          int twice() => n * 2;
        }
        void main() {
          print(C().twice());
        }
    """, "4"),
    ("microtask: microtasks added by microtasks still run before the next event", r"""
        import 'dart:async';
        void main() {
          Future(() => print('event'));
          scheduleMicrotask(() {
            print('m1');
            scheduleMicrotask(() => print('m2'));
          });
        }
    """, "m1\nm2\nevent"),
    ("mutable: a map is changed in place", r"""
        var m = {'a': 1};
        m['b'] = 2;
        print(m);
    """, "{a: 1, b: 2}"),
    ("off-by-one: the end of a sublist is left out", r"""
        print([10, 20, 30].sublist(0, 2));
    """, "[10, 20]"),
    ("length: the last position is length - 1, and isEmpty reads better", r"""
        var xs = [4, 5, 6];
        print(xs[xs.length - 1]);
        print(xs.isEmpty || xs.isNotEmpty);
        print({'a': 1, 'b': 2}.length);
    """, "6\ntrue\n2"),
    ("string-interpolation: braces take an expression, $name only the name", r"""
        var a = 1, b = 2;
        print('${a + b}');
        print('$a+$b');
    """, "3\n1+2"),
]

FLUTTER_CHECKS: list[tuple[str, str, str, str]] = [
    # (name = "<entry id>: the claim", widget prompt as the Brain Drills oracle takes it, measurement, expected)
    ("flex: two flex children share 400 as 1:3", "Row(children: [Expanded(flex: 1, child: Box('a')), Expanded(flex: 3, child: Box('b'))])",
     "'${w('a')} ${w('b')}'", "100.0 300.0"),
    ("expanded: the default flex is 1", "Row(children: [Expanded(child: Box('a')), Expanded(child: Box('b'))])",
     "'${w('a')} ${w('b')}'", "200.0 200.0"),
    ("expanded: it fills what is left", "Row(children: [Box('a', w: 100), Expanded(child: Box('b'))])", "w('b')", "300"),
    ("expanded: only valid inside a Row, Column or Flex", "Center(child: Expanded(child: Box('a')))", "w('a')",
     "ERROR: Incorrect use of ParentDataWidget."),
    ("expanded: a long child that is expanded no longer overflows", "Row(children: [Expanded(child: Box('a', w: 300)), Box('b', w: 300)])",
     "overflowed", "false"),
    ("flexible: loose, the child keeps its size", "Row(children: [Flexible(child: Box('a'))])", "w('a')", "50"),
    ("spacer: pushes the neighbours apart", "Row(children: [Box('a'), Spacer(), Box('b')])", "x('b')", "350"),
    ("main-axis: spaceBetween puts the last child at the end", "Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Box('a'), Box('b')])",
     "x('b')", "350"),
    ("main-axis: spaceEvenly makes equal gaps", "Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [Box('a'), Box('b')])",
     "'${x('a')} ${x('b')}'", "100.0 250.0"),
    ("main-axis: with no spare room there is nothing to align", "Row(mainAxisAlignment: MainAxisAlignment.center, children: [Box('a', w: 400)])",
     "x('a')", "0"),
    ("main-axis: crossAxisAlignment stretch", "Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [Box('a', w: 50)])",
     "w('a')", "400"),
    ("column: the cross axis is centered by default", "Column(children: [Box('a', w: 100)])", "x('a')", "150"),
    ("column: too much height overflows", "Column(children: [Box('a', h: 200), Box('b', h: 200)])", "overflowed", "true"),
    ("column: a ListView directly inside has no height limit", "Column(children: [ListView()])", "1",
     "ERROR: Vertical viewport was given unbounded height."),
    ("column: Expanded gives the ListView a height", "Column(children: [Expanded(child: ListView(children: [Box('a')]))])", "w('a')", "400"),
    ("row: too much width overflows", "Row(children: [Box('a', w: 300), Box('b', w: 300)])", "overflowed", "true"),
    ("row: it takes all the width unless mainAxisSize min", "Center(child: Row(key: Key('r'), children: [Box('a')]))", "w('r')", "400"),
    ("row: mainAxisSize min", "Center(child: Row(key: Key('r'), mainAxisSize: MainAxisSize.min, children: [Box('a')]))", "w('r')", "50"),
    ("overflow: a long Text in a Row overflows", "Row(children: [Text('long ' * 40)])", "overflowed", "true"),
    ("overflow: Expanded lets the Text wrap", "Row(children: [Expanded(child: Text('long ' * 40))])", "overflowed", "false"),
    ("center: it loosens the constraints", "Center(child: Box('a', w: 100, h: 40))", "'${x('a')} ${y('a')}'", "150.0 130.0"),
    ("center: it takes all the space it is given", "Center(key: Key('c'), child: Box('a'))", "'${w('c')} ${h('c')}'", "400.0 300.0"),
    ("align+alignment: a corner", "Align(alignment: Alignment.bottomRight, child: Box('a'))", "'${x('a')} ${y('a')}'", "350.0 250.0"),
    ("align: it expands to fill the space", "Center(child: Align(key: Key('al'), alignment: Alignment.topLeft, child: Box('a')))",
     "'${w('al')} ${h('al')}'", "400.0 300.0"),
    ("padding: 8 on every side adds 16", "Center(child: Padding(key: Key('p'), padding: EdgeInsets.all(8), child: Box('a', w: 100, h: 40)))",
     "'${w('p')} ${h('p')}'", "116.0 56.0"),
    ("container: with a child it is as big as the child", "Center(child: Container(key: Key('c'), child: Box('a')))", "'${w('c')} ${h('c')}'", "50.0 50.0"),
    ("container: with no child it fills the space", "Center(child: Container(key: Key('c')))", "'${w('c')} ${h('c')}'", "400.0 300.0"),
    ("container: in a Row its width is 0", "Row(children: [Container(key: Key('c'))])", "'${w('c')} ${h('c')}'", "0.0 300.0"),
    ("sized-box: a parent that forces a size wins", "SizedBox(key: Key('s'), width: 200, child: Box('a'))", "'${w('s')} ${w('a')}'", "400.0 400.0"),
    ("sized-box: inside a Center it is obeyed", "Center(child: SizedBox(key: Key('s'), width: 200, height: 100))", "'${w('s')} ${h('s')}'", "200.0 100.0"),
    ("sized-box: expand and shrink", "Center(child: SizedBox.shrink(key: Key('s')))", "'${w('s')} ${h('s')}'", "0.0 0.0"),
    ("tight-loose: the root gets tight constraints", "Container(key: Key('c'))", "'${w('c')} ${h('c')}'", "400.0 300.0"),
    ("constrained-box+constraints: a minimum beats the child's size", "Center(child: ConstrainedBox(constraints: BoxConstraints(minWidth: 200), child: Box('a')))",
     "w('a')", "200"),
    ("constrained-box+constraints: a maximum stops growth", "Center(child: ConstrainedBox(constraints: BoxConstraints(maxWidth: 30), child: Box('a')))",
     "w('a')", "30"),
    ("aspect-ratio: the biggest width, then the height from the ratio", "Center(child: AspectRatio(aspectRatio: 2, child: Box('a')))",
     "'${w('a')} ${h('a')}'", "400.0 200.0"),
    ("aspect-ratio: under tight constraints it can do nothing", "AspectRatio(aspectRatio: 2, child: Box('a'))",
     "'${w('a')} ${h('a')}'", "400.0 300.0"),
    ("stack-widget: Positioned children do not count towards the size",
     "Center(child: Stack(key: Key('s'), children: [Box('a', w: 100, h: 50), Positioned(left: 300, top: 300, child: Box('b'))]))",
     "'${w('s')} ${h('s')}'", "100.0 50.0"),
    ("positioned: measured from the Stack's top-left", "Stack(children: [Positioned(left: 10, top: 20, child: Box('a'))])",
     "'${x('a')} ${y('a')}'", "10.0 20.0"),
    ("positioned: two opposite sides stretch the child",
     "Stack(children: [Positioned(left: 10, right: 10, top: 0, child: Container(key: Key('c'), height: 20))])", "w('c')", "380"),
    ("wrap-widget: a new line when the children no longer fit", "Wrap(children: [Box('a', w: 150), Box('b', w: 150), Box('c', w: 150)])",
     "'${y('a')} ${y('b')} ${y('c')}'", "0.0 0.0 50.0"),
    ("wrap-widget: in a Row a Wrap never wraps",
     "Row(children: [Wrap(children: [Box('a', w: 150), Box('b', w: 150), Box('c', w: 150)])])",
     "'${{y('a'), y('b'), y('c')}.length} $overflowed'", "1 true"),
    ("list-view-builder: only the items near the screen are built",
     "ListView.builder(itemCount: 100, itemBuilder: (c, i) => SizedBox(height: 50, child: Text('item $i')))",
     "count(find.byType(Text)) < 20 && count(find.byType(Text)) > 3", "true"),
    ("media-query: the size of the app window", "MaterialApp(home: Builder(builder: (c) => Text('${MediaQuery.of(c).size.width}')))",
     "count(find.text('400.0'))", "1"),
    ("text-field: it needs a Material ancestor", "TextField()", "1", "ERROR: No Material widget found."),
    ("scaffold: the body gets the space below the app bar",
     "MaterialApp(home: Scaffold(appBar: AppBar(title: Text('t')), body: Container(key: Key('b'))))", "h('b')", "244"),
    ("material-app: it creates the Navigator, so none exists above it", "Builder(builder: (c) { Navigator.of(c); return SizedBox(); })", "1",
     "ERROR: Navigator operation requested with a context that does not include a Navigator."),
    ("value-notifier: it notifies only on a real change; a ChangeNotifier on every call", "Box('a')", r"""final n = ValueNotifier<int>(0);
var c = 0;
n.addListener(() => c++);
n.value = 1;
n.value = 1;
n.value = 2;
final m = ChangeNotifier();
var d = 0;
m.addListener(() => d++);
// ignore: invalid_use_of_protected_member
m.notifyListeners();
// ignore: invalid_use_of_protected_member
m.notifyListeners();
return '$c $d';""", "2 2"),
    ("set-state: without it the screen keeps the old value", r"""class Counter extends StatefulWidget {
  const Counter({super.key});
  @override
  State<Counter> createState() => _CounterState();
}
class _CounterState extends State<Counter> {
  int plain = 0;
  int shown = 0;
  @override
  Widget build(BuildContext context) => Column(children: [
        Text('plain $plain'),
        Text('shown $shown'),
        GestureDetector(onTap: () { plain++; }, child: Container(key: Key('p'), width: 50, height: 20, color: Colors.red)),
        GestureDetector(onTap: () { setState(() { shown++; }); }, child: Container(key: Key('s'), width: 50, height: 20, color: Colors.blue)),
      ]);
}
Counter()""", r"""await tester.tap(find.byKey(Key('p')));
await tester.pump();
final afterPlain = '${count(find.text('plain 1'))} ${count(find.text('plain 0'))}';
await tester.tap(find.byKey(Key('s')));
await tester.pump();
return '$afterPlain | ${count(find.text('shown 1'))} ${count(find.text('plain 1'))}';""", "0 1 | 1 1"),
    ("widget-lifecycle+init-state+dispose: initState, didChangeDependencies, build, didUpdateWidget, build, dispose", r"""class H {
  static final log = <String>[];
}
class P extends StatefulWidget {
  final int v;
  const P(this.v, {super.key});
  @override
  State<P> createState() => _P();
}
class _P extends State<P> {
  @override
  void initState() {
    super.initState();
    H.log.add('init');
  }
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    H.log.add('deps');
  }
  @override
  void didUpdateWidget(P old) {
    super.didUpdateWidget(old);
    H.log.add('update');
  }
  @override
  void dispose() {
    H.log.add('dispose');
    super.dispose();
  }
  @override
  Widget build(BuildContext c) {
    H.log.add('build');
    return const SizedBox();
  }
}
P(1)""", r"""await tester.pumpWidget(Directionality(textDirection: TextDirection.ltr, child: P(2)));
await tester.pumpWidget(const SizedBox());
return H.log.join(',');""", "init,deps,build,update,build,dispose"),
    ("const-widget: a const child is not rebuilt, a fresh one is", r"""class H {
  static int constBuilds = 0;
  static int plainBuilds = 0;
}
class Leaf extends StatelessWidget {
  final bool isConst;
  const Leaf(this.isConst, {super.key});
  @override
  Widget build(BuildContext c) {
    if (isConst) {
      H.constBuilds++;
    } else {
      H.plainBuilds++;
    }
    return const SizedBox();
  }
}
class Parent extends StatefulWidget {
  const Parent({super.key});
  @override
  State<Parent> createState() => _PS();
}
class _PS extends State<Parent> {
  @override
  Widget build(BuildContext c) => Column(children: [
        const Leaf(true),
        Leaf(false),
        GestureDetector(onTap: () => setState(() {}), child: Container(key: Key('go'), width: 50, height: 20, color: Colors.red)),
      ]);
}
Parent()""", r"""await tester.tap(find.byKey(Key('go')));
await tester.pump();
return '${H.constBuilds} ${H.plainBuilds}';""", "1 2"),
    ("widget-key: without keys the State stays with the position, with keys with the widget", r"""class H {
  static int next = 0;
}
class Tile extends StatefulWidget {
  final String label;
  const Tile(this.label, {super.key});
  @override
  State<Tile> createState() => _Tile();
}
class _Tile extends State<Tile> {
  final int id = H.next++;
  @override
  Widget build(BuildContext c) => Text('${widget.label}${id}');
}
class Parent extends StatefulWidget {
  final bool keys;
  const Parent(this.keys, {super.key});
  @override
  State<Parent> createState() => _Parent();
}
class _Parent extends State<Parent> {
  bool swapped = false;
  @override
  Widget build(BuildContext c) {
    final a = widget.keys ? Tile('A', key: ValueKey('A')) : Tile('A');
    final b = widget.keys ? Tile('B', key: ValueKey('B')) : Tile('B');
    return Column(children: [
      ...(swapped ? [b, a] : [a, b]),
      GestureDetector(onTap: () => setState(() => swapped = true), child: Container(key: Key('go'), width: 50, height: 20, color: Colors.red)),
    ]);
  }
}
Parent(false)""", r"""await tester.tap(find.byKey(Key('go')));
await tester.pump();
final plain = find.byType(Text).evaluate().map((e) => (e.widget as Text).data).join(',');
await tester.pumpWidget(const SizedBox());
H.next = 0;
await tester.pumpWidget(Directionality(textDirection: TextDirection.ltr, child: Parent(true)));
await tester.tap(find.byKey(Key('go')));
await tester.pump();
final keyed = find.byType(Text).evaluate().map((e) => (e.widget as Text).data).join(',');
return '$plain | $keyed';""", "B0,A1 | B1,A0"),
    ("text-editing-controller: the controller holds the text", r"""class H {
  static final c = TextEditingController();
}
MaterialApp(home: Scaffold(body: TextField(controller: H.c)))""", r"""await tester.enterText(find.byType(TextField), 'hi');
final typed = H.c.text;
H.c.clear();
return '$typed|${H.c.text}';""", "hi|"),
    ("form-validator: validate returns true only when every validator gave null", r"""class H {
  static final k = GlobalKey<FormState>();
}
MaterialApp(home: Scaffold(body: Form(key: H.k, child: TextFormField(validator: (v) => (v == null || v.isEmpty) ? 'required' : null))))""", r"""final a = H.k.currentState!.validate();
await tester.pump();
final shown = find.text('required').evaluate().length;
await tester.enterText(find.byType(TextFormField), 'x');
final b = H.k.currentState!.validate();
return '$a $shown $b';""", "false 1 true"),
    ("navigator: push opens a screen, pop returns", r"""MaterialApp(home: Builder(builder: (c) => GestureDetector(onTap: () => Navigator.push(c, MaterialPageRoute(builder: (_) => Scaffold(body: GestureDetector(onTap: () => Navigator.pop(c), child: Text('second'))))), child: Container(key: Key('go'), width: 50, height: 50, color: Colors.red, child: Text('first')))))""", r"""await tester.tap(find.byKey(Key('go')));
await tester.pumpAndSettle();
final onSecond = '${count(find.text('second'))}';
await tester.tap(find.text('second'));
await tester.pumpAndSettle();
return '$onSecond ${count(find.text('second'))} ${count(find.text('first'))}';""", "1 0 1"),
    ("gesture-detector: by default a child with nothing painted is not hit; opaque is", r"""class H {
  static int n = 0;
}
Center(child: Column(children: [
  GestureDetector(onTap: () => H.n += 1, child: SizedBox(key: Key('empty'), width: 100, height: 40)),
  GestureDetector(behavior: HitTestBehavior.opaque, onTap: () => H.n += 10, child: SizedBox(key: Key('opaque'), width: 100, height: 40)),
]))""", r"""await tester.tap(find.byKey(Key('empty')), warnIfMissed: false);
final first = H.n;
await tester.tap(find.byKey(Key('opaque')), warnIfMissed: false);
return '$first ${H.n}';""", "0 10"),
]

#: Flutter entries whose rules are NOT backed by any measurement above or in pure Dart: they are well-known documented
#: Flutter behaviour (and the checks above cover the neighbouring layout/state rules). The test keeps this list honest:
#: an entry is either here or has at least one check named after it, never both.
NOT_ORACLE_CHECKED = {
    "widget", "stateless-widget", "stateful-widget", "state", "build-method", "build-context",
    "widget-tree", "inherited-widget", "theme", "change-notifier", "listenable-builder", "future-builder", "run-app",
    "hot-reload", "layout", "route", "ink-well", "text-widget", "list-view",
}


def _dart_module_ids() -> dict[str, set[str]]:
    import importlib
    import pkgutil

    found: dict[str, set[str]] = {}
    for info in pkgutil.iter_modules(glossary.__path__):
        if info.name.startswith(("terms_dart_", "terms_flutter")):
            module = importlib.import_module(f"code_coach.glossary.{info.name}")
            found[info.name] = {item.id for item in module.TERMS if item.language == "dart"}
    return found


def _check_ids(name: str) -> list[str]:
    return name.split(":", 1)[0].split("+")


def test_dart_is_a_full_glossary_language():
    modules = _dart_module_ids()
    assert {"terms_dart_core", "terms_dart_types", "terms_dart_async", "terms_dart_basics", "terms_flutter"} <= set(modules)
    flutter = modules["terms_flutter"]
    language = set().union(*(v for k, v in modules.items() if k != "terms_flutter"))
    assert len(flutter) >= 50 and len(language) >= 140, (len(flutter), len(language))
    assert not flutter & language, "a word is in one file only"
    assert len(glossary.all_entries("dart")) == len(flutter) + len(language) >= 200
    assert not glossary.LOAD_ERRORS


def test_only_flutter_words_and_the_compile_error_card_go_without_an_example():
    flutter = _dart_module_ids()["terms_flutter"]
    bare = {e.id for e in glossary.all_entries("dart") if not e.example}
    assert bare <= flutter | {"syntax-error"}, sorted(bare - flutter)
    language = [e for e in glossary.all_entries("dart") if e.id not in flutter]
    assert sum(1 for e in language if e.example) >= 0.97 * len(language)
    assert all(e.rules for e in glossary.all_entries("dart")), "every Dart card has its rules"
    assert all(e.see_also for e in glossary.all_entries("dart")), "every Dart card links onward"


def test_every_rule_check_is_named_after_a_real_dart_word():
    ids_ = {e.id for e in glossary.all_entries("dart")}
    flutter = _dart_module_ids()["terms_flutter"]
    for name, _program, _expected in DART_RULE_CHECKS:
        assert set(_check_ids(name)) <= ids_ - flutter, name
    for name, _prompt, _check, _expected in FLUTTER_CHECKS:
        assert set(_check_ids(name)) <= ids_, name  # a Flutter check may back a plain word (padding)
    names = [c[0] for c in DART_RULE_CHECKS] + [c[0] for c in FLUTTER_CHECKS]
    assert len(names) == len(set(names))


def test_most_dart_words_have_a_rule_checked_by_real_dart():
    """The oracle rule for rules: each word with something runnable to say has a program behind it."""
    flutter = _dart_module_ids()["terms_flutter"]
    checked = {i for c in DART_RULE_CHECKS for i in _check_ids(c[0])}
    language = [e for e in glossary.all_entries("dart") if e.id not in flutter]
    unchecked = sorted(e.id for e in language if e.id not in checked)
    assert len(checked) >= 0.8 * len(language), f"{len(checked)} of {len(language)} words; no check: {unchecked}"


@functools.cache
def dart_rule_results() -> list[str]:
    import textwrap

    return dart_oracle.dart_values([textwrap.dedent(p).strip("\n") for _n, p, _e in DART_RULE_CHECKS])


@pytest.mark.skipif(not dart_oracle.DART, reason="needs dart")
@pytest.mark.parametrize("index", range(len(DART_RULE_CHECKS)), ids=[c[0] for c in DART_RULE_CHECKS])
def test_the_dart_rules_hold_in_real_dart(index):
    name, _program, expected = DART_RULE_CHECKS[index]
    got = dart_rule_results()[index]
    if expected == CE:
        assert got.startswith(CE), f"{name}: should not compile, but printed {got!r}"
    else:
        assert got == expected, f"{name}: printed {got!r}, not {expected!r}"


def test_not_oracle_checked_flutter_words_are_listed_honestly():
    flutter = _dart_module_ids()["terms_flutter"]
    checked = {i for c in FLUTTER_CHECKS for i in _check_ids(c[0])} & flutter
    assert not NOT_ORACLE_CHECKED & checked, "listed as unchecked but has a check"
    assert flutter == checked | NOT_ORACLE_CHECKED, sorted(flutter ^ (checked | NOT_ORACLE_CHECKED))


@functools.cache
def flutter_results() -> list[str]:
    return flutter_oracle.flutter_values([(p, c) for _n, p, c, _e in FLUTTER_CHECKS])


@pytest.mark.skipif(flutter_oracle._flutter() is None, reason="needs flutter")
@pytest.mark.parametrize("index", range(len(FLUTTER_CHECKS)), ids=[c[0] for c in FLUTTER_CHECKS])
def test_the_flutter_rules_hold_in_real_flutter(index):
    name, _prompt, _check, expected = FLUTTER_CHECKS[index]
    got = flutter_results()[index]
    assert got == expected, f"{name}: Flutter measured {got!r}, not {expected!r}"


#: Words that plain Dart may legitimately wake: the everyday ones, with low priority.
EVERYDAY_DART = {
    "variable", "main-function", "function", "integer", "float", "string", "list", "boolean", "condition", "loop",
    "for-loop", "while-loop", "expression", "operator", "argument", "parameter", "return", "class", "constructor", "var",
    "final", "division", "comparison", "modulo", "instance", "method", "precedence", "num", "type", "null", "set",
    "dictionary", "arrow-function", "initializing-formal", "this", "const", "truncating-division", "length",
}
QUIET_DART = [
    "int x = 5;\nprint(x);", "void main() {\n  print('hi');\n}", "var total = 0;\nfor (final n in nums) {\n  total += n;\n}",
    "if (x > 3) {\n  print('big');\n}", "int add(int a, int b) {\n  return a + b;\n}\nvoid main() {\n  print(add(1, 2));\n}",
    "var xs = [3, 1, 2];\nprint(xs.length);", "class Dog {\n  final String name;\n  Dog(this.name);\n}",
    "String s = 'hello';\nprint(s.length);", "while (n > 1) {\n  n = n ~/ 2;\n}",
]


@pytest.mark.parametrize("code", QUIET_DART)
def test_plain_dart_does_not_wake_the_specialised_cards(code):
    woken = ids(find_words(code, "dart", limit=80))
    assert set(woken) <= EVERYDAY_DART, (code, sorted(set(woken) - EVERYDAY_DART))
    assert len(woken) <= 8


def test_generic_dart_words_are_never_loud():
    for word in ("sum", "state", "counter", "character", "division", "default-value", "value", "key", "index", "variable",
                 "expression", "statement", "side-effect", "accumulator"):
        item = lookup("dart", word)
        assert item is not None and item.priority <= 50, word


@pytest.mark.parametrize(
    ("spoken", "wanted"),
    [
        ("switch", "switch"), ("tuple", "record"), ("string-representation", "string-representation"),
        ("tostring", "string-representation"), ("default-value", "default-value"), ("short-circuit", "short-circuit"),
        ("optional-chaining", "null-aware-access"), ("destructuring", "destructuring"), ("unpacking", "destructuring"),
        ("generator", "generator"), ("yield", "async-generator"), ("async-await", "async-await"), ("await", "async-await"),
        ("keyword argument", "named-parameter"), ("isinstance", "type-check"), ("instanceof", "type-check"),
        ("lambda", "anonymous-function"), ("f-string", "string-interpolation"), ("template literal", "string-interpolation"),
        ("floor division", "truncating-division"), ("null", "null"), ("none", "null"), ("dict", "dictionary"),
        ("array", "list"), ("try", "try-catch"), ("catch", "try-catch"), ("raise", "throw"), ("range error", "index-error"),
        ("index error", "index-error"), ("type error", "type-error"), ("remainder", "modulo"), ("filter", "filter"),
        ("where", "filter"), ("fold", "reduce"), ("copy", "identity"), ("mixin", "mixin"), ("stack", "stack-widget"),
        ("position", "positioned"), ("padding", "padding"), ("truthy", "boolean"), ("this", "this"), ("self", "this"),
        ("optional parameter", "optional-positional-parameter"), ("operator ==", "operator"),
        ("inherited", "inherited-widget"), ("order", "control-flow"), ("listener", "change-notifier"),
        ("text", "text-widget"), ("length", "length"), ("setstate", "set-state"), ("lifecycle", "widget-lifecycle"),
        ("element", "widget-tree"), ("context", "build-context"), ("notifier", "value-notifier"),
    ],
)
def test_a_python_or_javascript_word_leads_to_the_dart_card(spoken, wanted):
    found = glossary.resolve("dart", spoken)
    assert found is not None and found.id == wanted, (spoken, found and found.id)


def test_the_dart_cards_say_dart_s_own_rules():
    """The same word, a different rule: the Dart card must not teach the Python or JavaScript one."""
    modulo = " ".join(entry("dart", "modulo").rules)
    assert "-7 % 3 is 2" in modulo and "never negative" in entry("dart", "modulo").definition
    assert "not compile" in " ".join(entry("dart", "boolean").rules), "no truthy and falsy in Dart"
    assert "no 'shared mutable default' trap" in " ".join(entry("dart", "default-parameter").rules)
    assert "break" in " ".join(entry("dart", "switch").rules) and "fall" in entry("dart", "switch").definition
    assert "1 == 1.0 is true" in " ".join(entry("dart", "comparison").rules)
    assert "[1] == [1] is false" in " ".join(entry("dart", "equality").rules)
    assert "4.0" in " ".join(entry("dart", "division").rules)
    assert "fresh" in " ".join(entry("dart", "closure").rules) or "its own" in " ".join(entry("dart", "closure").rules)


@pytest.mark.parametrize("word", [e.id for e in glossary.all_entries("dart")])
def test_a_dart_card_does_not_teach_python_or_javascript_syntax(word):
    e = entry("dart", word)
    text = " ".join([e.definition, *e.rules, e.example])
    for bad in (r"\bNone\b", r"\bundefined\b", r"console\.log", r"\belif\b", r"\bdef \w+\(", r"===", r"\bself\.", r"\bnull_ok\b"):
        if word == "equality" and bad == r"===":
            continue  # the card says Dart has no ===
        assert not re.search(bad, text), (word, bad)


def test_every_dart_activity_gets_dart_words_derived_from_its_concepts():
    played = [a for a in ACTIVITIES if "dart" in a.languages]
    assert len(played) >= 40
    for a in played:
        got = words_for_context(a.id, "dart")
        assert got and all(w.language == "dart" for w in got), a.id
        resolved = [glossary.resolve("dart", c) for c in a.concepts]
        assert ids(got) == list(dict.fromkeys(r.id for r in resolved if r)), a.id
    assert ids(words_for_context("dd_num", "dart"))[:4] == ["type-conversion", "integer", "float", "modulo"]
    assert ids(words_for_context("fl_flex", "dart"))[:3] == ["layout", "flex", "division"]
    assert "stack-widget" in ids(words_for_context("fl_stack", "dart"))
    assert ids(words_for_context("dd_pattern", "dart"))[:3] == ["destructuring", "pattern", "condition"]


def test_chips_and_find_words_for_a_dart_drill_come_from_the_dart_glossary():
    got = find_words("String? s;\nprint(s?.length ?? 0);", "dart", context="dart_null")
    assert ids(got)[:5] == ["short-circuit", "default-value", "null-aware-access", "ternary", "string"]
    assert "null-coalescing" in ids(got) or len(got) == 8
    assert all(w.language == "dart" for w in got)
