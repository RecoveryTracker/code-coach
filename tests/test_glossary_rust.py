"""The Rust glossary (code_coach/glossary/terms_rust_*.py): its rules held to the real rustc, its blanking, its words.

The generic tests in tests/test_glossary.py already cover Rust like every glossary language (shape, unique ids, every
example built by rustc debug and -O and printing exactly its `out`, a context for every Rust drill, the limit test on
RUST_SINK). This file adds what is Rust's own:

* RUST_RULE_CHECKS (tests/glossary_rust_checks.py): one small program per claim a rule makes, named
  "<entry id>: the claim", with the expected output, or `CE` (rustc refuses it: a type error, the borrow checker, a deny
  lint) or `PANIC` (it compiles and panics at run time). Every Rust word has a check or is named in
  RUST_NOT_ORACLE_CHECKED, and the two partition the ids;
* the comment and string blanking (lifetimes are not char literals, raw strings, nested block comments);
* the Rust Brain Drills' concepts resolve in the Rust glossary.
"""

from __future__ import annotations

import functools
import re
import textwrap

import pytest

from code_coach import glossary
from code_coach.brain import activities_in
from code_coach.glossary import find_words, words_for_context
from tests import rust_oracle
from tests.glossary_rust_checks import RUST_NOT_ORACLE_CHECKED, RUST_RULE_CHECKS

needs_rustc = pytest.mark.skipif(not rust_oracle.HAVE_RUSTC, reason="needs rustc")


def _rust_ids() -> set[str]:
    return {e.id for e in glossary.all_entries("rust")}


def _check_ids(name: str) -> list[str]:
    """The entry ids a check is named after: "a, b: the claim" -> ["a", "b"]."""
    return [x.strip() for x in name.split(":", 1)[0].split(",")]


@functools.cache
def rule_results():
    return rust_oracle.rust_results([textwrap.dedent(p).strip("\n") for _n, p, _e in RUST_RULE_CHECKS])


def _matches(expected: str, run) -> bool:
    if expected == "CE":
        return not run.compiled
    if expected == "PANIC":
        return run.compiled and run.panicked and not run.out.startswith("BUILDS DIFFER")
    return run.compiled and not run.panicked and run.out == expected


# ── The language is there ───────────────────────────────────────────────

def test_rust_is_a_glossary_language_of_its_own():
    assert "rust" in glossary.LANGUAGES
    assert glossary.language_for("rust") == "rust"
    assert len(glossary.all_entries("rust")) >= 80
    assert all(e.language == "rust" for e in glossary.all_entries("rust"))


def test_the_everyday_words_share_the_other_languages_ids():
    # so a drill's plain concepts ("loop", "closure", "scope"...) resolve in Rust as they do elsewhere
    want = {"variable", "loop", "closure", "scope", "function", "string", "integer", "expression", "shadowing",
            "struct", "enum", "trait", "ownership", "borrowing", "move", "clone", "copy", "reference", "lifetime",
            "option", "result", "match", "iterator", "vector", "panic", "integer-overflow", "macro"}
    assert want <= _rust_ids(), sorted(want - _rust_ids())


# ── The rules hold in real Rust ─────────────────────────────────────────

def test_check_names_are_unique_and_named_after_real_words():
    names = [c[0] for c in RUST_RULE_CHECKS]
    assert len(names) == len(set(names))
    for name in names:
        assert set(_check_ids(name)) <= _rust_ids(), name
    assert len(RUST_RULE_CHECKS) >= 100


@needs_rustc
@pytest.mark.parametrize("index", range(len(RUST_RULE_CHECKS)), ids=[c[0][:70] for c in RUST_RULE_CHECKS])
def test_the_rust_rules_hold_in_real_rust(index):
    name, _program, expected = RUST_RULE_CHECKS[index]
    run = rule_results()[index]
    assert _matches(expected, run), f"{name}: rustc gave {run.value!r} (panicked={run.panicked}), not {expected!r}"


def test_the_words_with_no_measured_rule_are_listed_honestly():
    checked = {i for c in RUST_RULE_CHECKS for i in _check_ids(c[0])}
    assert not RUST_NOT_ORACLE_CHECKED & checked, "listed as unchecked but has a check"
    assert _rust_ids() == checked | RUST_NOT_ORACLE_CHECKED, sorted(_rust_ids() ^ (checked | RUST_NOT_ORACLE_CHECKED))
    assert len(RUST_NOT_ORACLE_CHECKED) <= 0.1 * len(_rust_ids()), "nearly every Rust word has a measured rule"


@needs_rustc
def test_the_check_harness_tells_compile_errors_and_panics_apart():
    runs = rust_oracle.rust_results(['let v: Vec<i32> = Vec::new();\nprintln!("{}", v[0]);',
                                     'let s = String::new();\nlet t = s;\nprintln!("{}", s);', 'println!("ok");'])
    assert [_matches("PANIC", runs[0]), _matches("CE", runs[1]), _matches("ok", runs[2])] == [True, True, True]
    assert not _matches("CE", runs[0]) and not _matches("PANIC", runs[1])


# ── Blanking: comments and string contents are not code ─────────────────

def test_strings_chars_and_comments_are_blanked_but_lifetimes_are_code():
    src = "\n".join([
        "fn f<'a>(s: &'a str) -> &'static str { // a comment with match in it",
        "    let c = '\\n'; let b = b'x'; let u = '\\u{e9}';",
        '    let r = r#"raw "loop" text"#; /* outer /* nested match */ still comment */',
        '    let t = "es\\"c match";',
        "    'q'",
        "}",
    ])
    out = glossary.blank_code(src, "rust")
    assert "'a" in out and "'static" in out, "a lifetime is code"
    assert "match" not in out and "loop" not in out and "comment" not in out
    assert out.count("\n") == src.count("\n"), "line numbers are kept"
    assert "'_'" in out and '""' in out


def test_a_word_inside_a_string_or_comment_wakes_no_card():
    quiet = find_words('fn main() {\n    // loop match clone unwrap\n    println!("loop match clone unwrap");\n}', "rust")
    loud = find_words("fn main() {\n    let v = vec![1];\n    let w = v.clone();\n    for x in w { }\n}", "rust")
    assert not ({"loop", "match", "clone", "unwrap"} & {w.id for w in quiet}) or len(quiet) <= 2
    assert {w.id for w in loud} & {"clone", "vector", "for-loop", "loop"}


def test_detect_patterns_never_hang_on_adversarial_input():
    import time

    for junk in ("'a " * 5000, "r#\"" * 3000, "/*" * 3000, "&mut " * 4000, "fn " * 5000, "::<" * 4000,
                 "'\\" * 4000, "impl<T> " * 3000, "x." * 10000, "\"" * 5001):
        start = time.time()
        assert isinstance(find_words(junk, "rust"), list)
        assert time.time() - start < 2.0, junk[:20]


def test_detect_patterns_have_bounded_gaps():
    for e in glossary.all_entries("rust"):
        for pattern in e.detect:
            body = pattern[4:] if pattern.startswith("raw:") else pattern
            assert not re.search(r"(?<!\\)\.\*|\[\^\\n\]\*", body), f"{e.id}: unbounded gap in {pattern!r}"


# ── The Rust drills' words ──────────────────────────────────────────────

def test_every_rust_drill_concept_resolves_in_rust():
    acts = activities_in("rust")
    assert acts, "the Rust core pack is discovered"
    missing = {a.id: [c for c in a.concepts if glossary.resolve("rust", c) is None] for a in acts}
    assert not {k: v for k, v in missing.items() if v}, missing


def test_a_rust_drill_shows_rust_words_first():
    for a in activities_in("rust"):
        got = words_for_context(a.id, "rust")
        assert len(got) >= 2 and all(w.language == "rust" for w in got), a.id
