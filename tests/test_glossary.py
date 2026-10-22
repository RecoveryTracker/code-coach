"""The glossary ("Words used" under Explain my code): code_coach/glossary and its screen.

Four kinds of test:

* Shape: every entry is well formed (ids, definitions, rules, links, a short definition).
* THE ORACLE: every entry's example is RUN for real (python, node) and must print exactly its
  `example_output`; every list of falsy and truthy values is run through bool() / Boolean(), and the
  prose rule that lists them is parsed and run too. The glossary must never teach something false.
  The expected values written in this file (the "claims") are worked out by hand, not read from
  the entries.
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

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
SRC = WEB / "src"
ESBUILD = WEB / "node_modules" / "esbuild" / "bin" / "esbuild"
NODE = shutil.which("node")

LANGS = glossary.LANGUAGES
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
    else:
        assert "print(" not in e.definition and "elif" not in e.definition


@pytest.mark.parametrize("lang", LANGS)
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
    for lang in LANGS:
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


@functools.cache
def example_results() -> dict[tuple[str, str], tuple[int, str, str]]:
    items = [e for lang in LANGS for e in glossary.all_entries(lang) if e.example and (lang == "python" or NODE)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        outs = list(pool.map(_run_example, items))
    return {(e.language, e.id): out for e, out in zip(items, outs)}


@pytest.mark.parametrize(("lang", "id_"), ENTRIES)
def test_example_prints_exactly_what_the_entry_says(lang, id_):
    e = entry(lang, id_)
    if not e.example:
        pytest.skip("no example")
    if lang == "javascript" and NODE is None:
        pytest.skip("needs node")
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


@pytest.mark.parametrize("lang", LANGS)
def test_the_hand_written_claims_hold_in_the_real_language(lang):
    """Guards the oracle itself: if this fails, the claims above are wrong, not the glossary."""
    falsy, truthy = CLAIMS[lang]
    assert truth_of(lang, list(falsy)) == [False] * len(falsy)
    assert truth_of(lang, list(truthy)) == [True] * len(truthy)


@pytest.mark.parametrize("lang", LANGS)
@pytest.mark.parametrize("word", ["truthy", "falsy"])
def test_the_false_and_true_lists_are_what_the_language_does(lang, word):
    e = entry(lang, word)
    assert e.counts_false and e.counts_true
    assert truth_of(lang, list(e.counts_false)) == [False] * len(e.counts_false), e.counts_false
    assert truth_of(lang, list(e.counts_true)) == [True] * len(e.counts_true), e.counts_true


@pytest.mark.parametrize("lang", LANGS)
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


@pytest.mark.parametrize("lang", LANGS)
def test_the_prose_rule_names_exactly_the_falsy_values(lang):
    """The first rule of Falsy is prose; its values are parsed out and run, and must match the list."""
    e = entry(lang, "falsy")
    named = _rule_values(e.rules[0])
    assert len(named) >= 8, named
    assert truth_of(lang, named) == [False] * len(named), named
    same = lambda items: sorted(i.replace('"', "'") for i in items)  # noqa: E731 - '' and "" are one value
    assert same(named) == same(e.counts_false), (named, e.counts_false)


@pytest.mark.parametrize("lang", LANGS)
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
    """A new pack is covered with ZERO glossary edits: its concepts become the context's words."""
    got = words_for_context(activity.id, lang)
    assert got, f"Brain Drills activity {activity.id!r} teaches no word at all in {lang}"
    if len(activity.concepts) >= 2:
        assert len(got) >= 2, (activity.id, lang, ids(got), activity.concepts)
    assert len(set(ids(got))) == len(got)


def test_concepts_that_resolve_in_neither_language_are_few_and_visible():
    """Lists, per activity, the concepts no glossary entry answers to, so a missing word is a failing line."""
    missing = {}
    for activity in ACTIVITIES:
        gone = [c for c in activity.concepts if all(glossary.resolve(lang, c) is None for lang in LANGS)]
        if gone:
            missing[activity.id] = gone
    too_many = {k: v for k, v in missing.items() if len(v) > MAX_UNRESOLVED_PER_ACTIVITY}
    assert not too_many, f"write entries (terms_brain_*.py) for: {too_many}"


def test_every_pack_concept_is_a_plain_word_and_most_resolve_in_both_languages():
    """Not a gate on single-language words (range, nonlocal...), but the tally is shown when it fails."""
    total = both = 0
    for activity in ACTIVITIES:
        for c in activity.concepts:
            assert c == c.strip().lower() and c, f"{activity.id}: concept {c!r} is not a plain lowercase word"
            total += 1
            both += all(glossary.resolve(lang, c) is not None for lang in LANGS)
    assert both >= 0.9 * total, f"only {both} of {total} concepts resolve in both languages"


def test_every_hand_written_context_term_exists_somewhere_and_enough_exist_everywhere():
    known = {e.id for lang in LANGS for e in glossary.all_entries(lang)}
    for cid, terms in CONTEXTS.items():
        assert not set(terms) - known, (cid, set(terms) - known)
        for lang in LANGS:
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
    for lang in LANGS:
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
    for lang in LANGS:
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


@pytest.mark.parametrize("lang", LANGS)
def test_plain_code_does_not_wake_the_brain_pack_vocabulary(lang):
    """Plain snippets show the everyday words; the specialised cards need their own tell-tale syntax."""
    new = _brain_ids()[lang]
    for snippet in QUIET[lang]:
        code = snippet
        noisy = [w for w in ids(find_words(code, lang, limit=80)) if w in new]
        assert not noisy, (code, noisy)


@pytest.mark.parametrize("lang", LANGS)
def test_generic_brain_words_are_never_loud(lang):
    """Words that are everywhere ('sum', 'state', 'counter', 'character'...) have no detection or a low priority."""
    loud = [e.id for e in glossary.all_entries(lang) if e.id in _brain_ids()[lang] and e.priority > 70]
    assert loud == [] or set(loud) <= {"mutable-default"}, loud
    for word in ("sum", "state", "counter", "flag", "character", "bug", "binary", "division", "whitespace", "default-value"):
        item = lookup(lang, word)
        assert item is not None and item.priority <= 50, (lang, word)


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
    assert time.perf_counter() - started < 3.0


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
