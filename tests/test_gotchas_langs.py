"""Gotchas, every language: the registry, the deck loader, the shape of every built-in card, and the oracle.

ONE parametrised file for all the languages in `code_coach/gotchas/langs.py`. Test ids carry the language, as
`<id>-deck`, so a content author runs just theirs:

    pytest tests/test_gotchas_langs.py -k rust-deck          (or: -k "oracle and rust-deck")

THE ORACLE RULE. The answer written in a `content_<id>*.py` file is never trusted. Every card is run for real
(`test_every_card_prints_the_marked_answer`) by the workbook's own runner, `engine.run_code` - a different code
path from the quiz's `runner.run_program` - and what it prints must be exactly the marked answer; then the quiz's
runner builds it once and runs it twice and has to agree. SQL is the exception: its oracle is plain `sqlite3`
in this file. A language whose toolchain is not installed is skipped with a stated reason, a language with no
cards yet is skipped with "no cards yet" (it is simply not offered). Python, JavaScript and C have their own,
much longer oracles (test_gotchas_content.py, test_gotchas_c.py), so here only a sample of their cards goes
through the generic path - enough to prove the machinery - not all 700.
"""

from __future__ import annotations

import functools
import re
import sqlite3
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi import HTTPException

from code_coach import engine, gotchas
from code_coach.api import server
from code_coach.api.schemas import (GotchaAnswerRequest, GotchaRunRequest, GotchaUserRequest,
                                    MomentumAwardRequest)
from code_coach.gotchas import DECKS, langs, runner, toolchains, user
from code_coach.gotchas.items import Item

LIMIT = 5.0
#: Tools that build and run in one command (Java, dotnet, dart, ABCL) include their start-up in the clock.
ONE_STEP_LIMIT = LIMIT + 4.0
#: These three have their own exhaustive oracles; the generic path only samples them.
LEGACY = {"python", "javascript", "c"}
ALL_IDS = list(langs.ORDER)
EXPECTED_ORDER = ["python", "javascript", "typescript", "c", "cpp", "java", "csharp", "go", "rust", "dart",
                  "kotlin", "swift", "ruby", "php", "lua", "zig", "odin", "lisp", "sql"]


def deck_ids(lang_id: str) -> str:
    return f"{lang_id}-deck"


by_lang = pytest.mark.parametrize("lang_id", ALL_IDS, ids=deck_ids)


def _norm(text: str) -> str:
    return " ".join(text.split())


def _deck(lang_id: str) -> tuple[Item, ...]:
    deck = DECKS.get(lang_id, ())
    if not deck:
        pytest.skip(f"no {langs.get(lang_id).name} cards yet (content_{langs.get(lang_id).content}.py): "
                    "an empty deck is simply not offered")
    return deck


def _installed(lang_id: str) -> None:
    if not toolchains.available(lang_id):
        name = langs.get(lang_id).name
        pytest.skip(f"no {name} toolchain is installed on this machine, so the {name} cards cannot be run here")


# ── The registry ────────────────────────────────────────────────────────


def test_languages_come_in_the_display_order():
    assert list(langs.ORDER) == EXPECTED_ORDER


@by_lang
def test_every_language_has_an_extension_title_probe_and_keywords(lang_id):
    lang = langs.get(lang_id)
    assert lang.name.strip() and lang.title == f"{lang.name} Quiz"
    assert re.fullmatch(r"[a-z0-9]{1,5}", lang.ext), lang.ext
    assert re.fullmatch(r"[a-z]{1,6}", lang.prefix), lang.prefix
    assert lang.syntax.keywords, "the colourer needs a keyword set"
    assert len(set(lang.syntax.keywords)) == len(lang.syntax.keywords), "a keyword listed twice"
    assert lang.syntax.line_comments or lang.syntax.block_comments, "no comment syntax"
    assert lang.syntax.quotes, "no string syntax"
    assert lang.notes.strip() and len(lang.notes) < 700, "one short paragraph of advice for card writers"
    assert lang.banned, "every language bans something (the clock, randomness, input...)"
    for pattern, why in lang.banned:
        re.compile(pattern)
        assert why.strip()
    assert isinstance(toolchains.available(lang_id), bool), "the availability probe answers yes or no"
    assert lang.problems("") == []
    # the extension agrees with the one the workbook's runner uses, where it has one
    if lang_id in engine._SUFFIXES:
        assert "." + lang.ext == engine._SUFFIXES[lang_id]


def test_prefixes_and_content_stems_are_unique():
    every = [langs.get(i) for i in ALL_IDS]
    assert len({lang.prefix for lang in every}) == len(every)
    assert len({lang.content for lang in every}) == len(every)
    assert len({lang.id for lang in every}) == len(every)
    assert langs.get("python").content == "py" and langs.get("javascript").content == "js"
    assert langs.get("c").content == "c" and langs.get("rust").content == "rust"


def test_the_syntax_the_browser_gets_covers_every_language_and_is_json():
    import json

    payload = langs.syntax_payload()
    assert list(payload) == EXPECTED_ORDER
    json.dumps(payload)
    for lang_id, syn in payload.items():
        assert set(syn) >= {"keywords", "types", "consts", "line", "block", "quotes", "triple", "prefixes",
                            "directives", "charLiterals", "ignoreCase", "lisp"}, lang_id
    # a few facts the colourer relies on
    assert payload["python"]["line"] == ["#"] and payload["python"]["triple"] is True
    assert payload["lisp"]["line"] == [";"] and payload["lisp"]["lisp"] is True
    assert payload["sql"]["line"] == ["--"] and payload["sql"]["ignoreCase"] is True
    assert payload["lua"]["line"] == ["--"] and ["--[[", "]]"] in payload["lua"]["block"]
    assert payload["rust"]["charLiterals"] is True and payload["go"]["quotes"] == "\"'`"
    assert payload["c"]["directives"] is True and payload["cpp"]["directives"] is True


@by_lang
def test_the_banned_patterns_catch_what_they_are_for(lang_id):
    probes = {
        "python": "import random\nprint(random.random())", "javascript": "console.log(Math.random())",
        "typescript": "console.log(Math.random())", "c": 'printf("%p", (void*)0);',
        "cpp": "std::unordered_map<int,int> m;", "java": "new HashMap<String, Integer>();",
        "csharp": "new HashSet<int>();", "go": "for k := range m {}\nvar m map[string]int",
        "rust": "use std::collections::HashMap;", "dart": "print(x.hashCode);",
        "kotlin": "hashMapOf(1 to 2)", "swift": 'let d = ["a": 1]', "ruby": "puts rand(5)",
        "php": "echo rand(1, 5);", "lua": "for k, v in pairs(t) do end",
        "zig": "std.time.timestamp()", "odin": 'import "core:time"', "lisp": "(random 5)",
        "sql": "SELECT random();",
    }
    assert langs.get(lang_id).problems(probes[lang_id]), f"{lang_id}: its own banned example slipped through"
    assert langs.get(lang_id).problems("") == []


def test_go_ranging_over_a_map_needs_a_sort():
    go = langs.get("go")
    unsafe = 'm := map[string]int{"a": 1}\nfor k := range m {\n}'
    assert go.problems(unsafe)
    assert not go.problems(unsafe + "\nsort.Strings(keys)")


# ── The loader ──────────────────────────────────────────────────────────


def test_every_content_module_imports_cleanly():
    assert gotchas.LOAD_ERRORS == {}, gotchas.LOAD_ERRORS


def test_the_existing_decks_keep_their_modules_and_order():
    assert gotchas.MODULES["python"][:3] == ("content_py", "content_py2", "content_py3")
    assert gotchas.MODULES["javascript"][:3] == ("content_js", "content_js2", "content_js3")
    assert gotchas.MODULES["c"][0] == "content_c"
    assert [it.id for it in DECKS["python"][:2]] == ["py-score-90", "py-loop-var-list"]
    assert [it.id for it in DECKS["c"][:2]] == ["c-int-division", "c-modulo-negative"]


def test_modules_are_found_by_name_and_sorted_by_their_number(monkeypatch):
    import pkgutil
    from types import SimpleNamespace

    names = ["content_py3", "content_py", "content_py10", "content_py2", "content_pyx", "content_pyramid",
             "content_c", "content_c2", "content_cpp", "content_cpp2", "content_rust", "content_rust2", "items"]
    monkeypatch.setattr(pkgutil, "iter_modules", lambda path: [SimpleNamespace(name=n) for n in names])
    assert gotchas._modules_for(langs.get("python")) == ["content_py", "content_py2", "content_py3",
                                                         "content_py10"]
    assert gotchas._modules_for(langs.get("c")) == ["content_c", "content_c2"], "content_cpp is not C's"
    assert gotchas._modules_for(langs.get("cpp")) == ["content_cpp", "content_cpp2"]
    assert gotchas._modules_for(langs.get("rust")) == ["content_rust", "content_rust2"]
    assert gotchas._modules_for(langs.get("go")) == []


def test_a_broken_content_module_is_skipped_and_reported_not_fatal(monkeypatch):
    import importlib
    import pkgutil
    from types import SimpleNamespace

    good = SimpleNamespace(ITEMS=(Item(id="lua-a", language="lua", code="print(1)", answer="1", wrong=("2", "3", "4"),
                                       trap="t", why="w"),))
    alien = SimpleNamespace(ITEMS=(Item(id="rb-a", language="ruby", code="puts 1", answer="1", wrong=("2", "3", "4"),
                                        trap="t", why="w"),))

    real_import = importlib.import_module

    def fake_import(name, package=None):
        if name.endswith("content_lua"):
            return good
        if name.endswith("content_lua2"):
            raise SyntaxError("oops, half written")
        if name.endswith("content_lua3"):
            return alien
        return real_import(name, package)

    monkeypatch.setattr(gotchas, "LOAD_ERRORS", {})
    monkeypatch.setattr(pkgutil, "iter_modules", lambda path: [SimpleNamespace(name=n) for n in
                                                               ("content_lua", "content_lua2", "content_lua3")])
    monkeypatch.setattr(importlib, "import_module", fake_import)
    deck = gotchas._load(langs.get("lua"))
    assert [it.id for it in deck] == ["lua-a"], "the good module still loads"
    assert set(gotchas.LOAD_ERRORS) == {"content_lua2", "content_lua3"}
    assert "SyntaxError" in gotchas.LOAD_ERRORS["content_lua2"]
    assert "not lua cards" in gotchas.LOAD_ERRORS["content_lua3"]


# ── The shape of every built-in card ────────────────────────────────────


@by_lang
def test_the_deck_is_well_formed(lang_id):
    deck = _deck(lang_id)
    lang = langs.get(lang_id)
    ids = [it.id for it in deck]
    assert len(ids) == len(set(ids)), "an id appears twice in this deck"
    everyone = [it.id for d in DECKS.values() for it in d]
    assert len(everyone) == len(set(everyone)), "an id is used by two decks"
    for it in deck:
        assert it.id.startswith(lang.prefix + "-") and it.language == lang_id, it.id
        assert re.fullmatch(r"[a-z0-9][a-z0-9-]*", it.id), f"{it.id}: lower-case letters, digits and hyphens"
        assert not it.mine and it.added == "", it.id
        assert it.code.strip() and it.trap.strip() and it.why.strip(), it.id
        assert len(it.trap) <= 100, f"{it.id}: the trap line is {len(it.trap)} characters"
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", it.why.strip()) if s]
        assert 1 <= len(sentences) <= 4, f"{it.id}: the explanation is {len(sentences)} sentences"
        if it.raises:
            assert lang.raises, f"{it.id}: {lang.name} cards cannot be 'raises' cards"


@by_lang
def test_every_card_has_four_distinct_options_one_line_each(lang_id):
    for it in _deck(lang_id):
        assert len(it.wrong) == 3, f"{it.id}: three wrong options"
        normalised = [_norm(o) for o in it.options]
        assert all(normalised), it.id
        assert len(set(normalised)) == 4, f"{it.id}: options collide after normalising whitespace: {it.options}"
        assert all("\n" not in o for o in it.options), f"{it.id}: an option runs over two lines"


@by_lang
def test_every_card_is_one_short_program(lang_id):
    for it in _deck(lang_id):
        lines = it.code.splitlines()
        assert len(lines) <= 16, f"{it.id} is {len(lines)} lines (the limit is 16)"
        assert max(len(line) for line in lines) <= 76, f"{it.id} has a line over 76 columns"
        assert "\t" not in it.code, f"{it.id}: tabs show differently on every screen"


@by_lang
def test_no_card_uses_anything_that_differs_between_machines_or_runs(lang_id):
    lang = langs.get(lang_id)
    for it in _deck(lang_id):
        found = lang.problems(it.code)
        assert not found, f"{it.id}: {'; '.join(found)}"
        assert not re.search(r"\b0x[0-9a-f]{8,}\b|@[0-9a-f]{6,}\b", it.answer, re.I), \
            f"{it.id}: the answer looks like a memory address or hash"


@by_lang
def test_the_first_two_served_cards_are_the_first_two_of_the_first_module(lang_id):
    deck = _deck(lang_id)
    first_module = gotchas.MODULES[lang_id][0]
    import importlib

    mod = importlib.import_module(f"code_coach.gotchas.{first_module}")
    assert tuple(deck[:2]) == tuple(mod.ITEMS[:2])
    assert [it.id for it in gotchas.STORE.builtin(lang_id)[:2]] == [it.id for it in deck[:2]]


# ── The oracle ──────────────────────────────────────────────────────────


def _sqlite_oracle(code: str) -> tuple[str, str, int]:
    """SQL's independent oracle: plain sqlite3 in this process, the last SELECT as `a|b; c|d`."""
    db = sqlite3.connect(":memory:")
    rows = None
    try:
        pending = ""
        for part in code.split(";"):
            pending += part + ";"
            if sqlite3.complete_statement(pending):
                cur = db.execute(pending)
                if cur.description is not None:
                    rows = cur.fetchall()
                pending = ""
    except sqlite3.Error as exc:
        return "", str(exc), 1
    if rows is None:
        return "", "", 0
    return "; ".join("|".join("NULL" if v is None else str(v) for v in row) for row in rows) + "\n", "", 0


def _oracle(lang_id: str, code: str) -> tuple[str, str, int]:
    """What the program prints according to the workbook's runner (never the quiz's own)."""
    if lang_id == "sql":
        return _sqlite_oracle(code)
    out, err, rc = engine.run_code(code, language=lang_id, timeout=120)
    if langs.get(lang_id).output_on_stderr and rc == 0:
        out, err = err, out
    return out, err, rc


def _sample(deck: tuple[Item, ...]) -> tuple[Item, ...]:
    """Everything, except for the three languages with their own exhaustive oracles: the first two and a spread."""
    if deck and deck[0].language not in LEGACY:
        return deck
    return (*deck[:2], *deck[2::max(1, len(deck) // 12)][:12])


@functools.cache
def observed(lang_id: str):
    """Per card: (workbook runner's result, the quiz runner's two results)."""
    deck = _sample(DECKS.get(lang_id, ()))

    def one(item: Item):
        oracle = _oracle(lang_id, item.code)
        first, second = runner.run_twice(lang_id, item.code)
        return item.id, (oracle, first, second)

    workers = 2 if lang_id in {"kotlin", "lisp", "csharp", "swift", "dart", "java", "cpp", "rust", "zig"} else 4
    with ThreadPoolExecutor(workers) as pool:
        return dict(pool.map(one, deck))


@by_lang
def test_every_card_prints_the_marked_answer(lang_id):
    _installed(lang_id)
    deck = _sample(_deck(lang_id))
    seen = observed(lang_id)
    wrong = []
    for it in deck:
        (out, err, rc), first, second = seen[it.id]
        if it.raises:
            ok = rc != 0 and not out.strip() and re.search(rf"^{re.escape(it.answer)}\b", err, re.M)
        else:
            ok = rc == 0 and out.strip() == it.answer
        if not ok:
            wrong.append((it.id, "marked", it.answer, "printed", out.strip(), err.strip()[-160:]))
        for label, result in (("run 1", first), ("run 2", second)):
            if it.raises:
                continue  # the quiz runner's raises handling is tested in test_gotchas_store.py
            if not (result.ok and result.stdout.strip() == it.answer):
                wrong.append((it.id, f"quiz runner {label}", it.answer, result.stdout.strip(),
                              result.stderr.strip()[-160:]))
    assert wrong == []


@by_lang
def test_no_wrong_option_is_what_the_program_really_prints(lang_id):
    _installed(lang_id)
    seen = observed(lang_id)
    for it in _sample(_deck(lang_id)):
        (out, _err, _rc), _first, _second = seen[it.id]
        real = _norm(it.answer) if it.raises else _norm(out)
        for wrong in it.wrong:
            assert _norm(wrong) != real, f"{it.id}: a 'wrong' option is the real output"


@by_lang
def test_every_card_prints_the_same_thing_every_run_and_is_quick(lang_id):
    _installed(lang_id)
    seen = observed(lang_id)
    limit = ONE_STEP_LIMIT if lang_id in {"java", "csharp", "dart", "lisp"} else LIMIT
    for it in _sample(_deck(lang_id)):
        _oracle_result, first, second = seen[it.id]
        assert (first.stdout, first.returncode) == (second.stdout, second.returncode), \
            f"{it.id} differs between two runs of one build: {first.stdout!r} / {second.stdout!r}"
        assert first.seconds < limit and second.seconds < limit, \
            f"{it.id} took {max(first.seconds, second.seconds):.1f}s (the limit is {limit:g}s)"


# ── The runner, language by language ────────────────────────────────────

#: An interpreted language, a compiled one and a one-step one - whichever are installed here.
RUN_CASES = {
    "lua": {"ok": "print(6 * 7)", "bad": "print(", "loop": "while true do end", "env": "print(os.getenv('GOTCHA_SECRET'))",
            "stdin": "print(io.read())", "expect": "42"},
    "go": {"ok": 'package main\nimport "fmt"\nfunc main() { fmt.Println(6 * 7) }',
           "bad": 'package main\nfunc main() { x := }', "loop": "package main\nfunc main() { for {} }",
           "env": 'package main\nimport ("fmt"; "os")\nfunc main() { fmt.Println(os.Getenv("GOTCHA_SECRET") == "") }',
           "stdin": 'package main\nimport ("fmt"; "os")\nfunc main() { b := make([]byte, 1)\n'
                    ' n, _ := os.Stdin.Read(b)\n fmt.Println(n) }',
           "expect": "42"},
    "rust": {"ok": 'fn main() { println!("{}", 6 * 7); }', "bad": "fn main() { let x = ; }",
             "loop": "fn main() { loop {} }",
             "env": 'fn main() { println!("{}", std::env::var("GOTCHA_SECRET").is_err()); }',
             "stdin": 'fn main() { let mut s = String::new(); let n = std::io::stdin().read_line(&mut s).unwrap();'
                      ' println!("{}", n); }',
             "expect": "42"},
    "java": {"ok": "public class Main { public static void main(String[] a) { System.out.println(6 * 7); } }",
             "bad": "public class Main { public static void main(String[] a) { int x = ; } }",
             "loop": "public class Main { public static void main(String[] a) { while (true) {} } }",
             "env": "public class Main { public static void main(String[] a) "
                    "{ System.out.println(System.getenv(\"GOTCHA_SECRET\") == null); } }",
             "stdin": "public class Main { public static void main(String[] a) throws Exception "
                      "{ System.out.println(System.in.read()); } }",
             "expect": "42"},
    "csharp": {"ok": "Console.WriteLine(6 * 7);", "bad": "int x = ;", "loop": "while (true) { }",
               "env": 'Console.WriteLine(Environment.GetEnvironmentVariable("GOTCHA_SECRET") == null);',
               "stdin": "Console.WriteLine(Console.In.Read());", "expect": "42"},
}
#: These compile inside the run command: the program's clock includes the tool's start-up (and the runner
#: still reports a failed build as a compile error, from what the tool said).
ONE_STEP = {"java", "csharp"}


def _case(lang_id: str, monkeypatch=None) -> dict:
    _installed(lang_id)
    return RUN_CASES[lang_id]


CASE_IDS = list(RUN_CASES)


@pytest.mark.parametrize("lang_id", CASE_IDS, ids=deck_ids)
def test_the_runner_runs_a_program_and_reports_its_output(lang_id):
    case = _case(lang_id)
    got = runner.run_program(lang_id, case["ok"])
    assert got.ok and got.stdout.strip() == case["expect"] and got.stderr == "", got
    assert runner.error_name(lang_id, got) == ""


@pytest.mark.parametrize("lang_id", [i for i in CASE_IDS if i != "lua"], ids=deck_ids)
def test_a_program_that_does_not_build_is_a_compile_error_with_a_tidy_first_line(lang_id):
    case = _case(lang_id)
    got = runner.run_program(lang_id, case["bad"])
    assert not got.ok and got.stdout == ""
    assert got.compile_error and runner.error_name(lang_id, got) == "CompileError"
    first = runner.last_error_line(got)
    assert first and "\n" not in first and "gotcha_run_" not in first and "error" in first.lower(), first
    assert "gotcha_run_" not in got.stderr


@pytest.mark.parametrize("lang_id", CASE_IDS, ids=deck_ids)
def test_a_program_that_never_ends_is_stopped(lang_id):
    case = _case(lang_id)
    started = time.monotonic()
    got = runner.run_program(lang_id, case["loop"], timeout=1.0)
    assert got.timed_out and not got.ok and runner.error_name(lang_id, got) == "timeout"
    assert time.monotonic() - started < 40
    if lang_id not in ONE_STEP:
        assert got.seconds < 4, "the program's own clock does not include a separate build"


@pytest.mark.parametrize("lang_id", CASE_IDS, ids=deck_ids)
def test_the_program_gets_a_bare_environment_and_no_input(lang_id, monkeypatch):
    case = _case(lang_id)
    monkeypatch.setenv("GOTCHA_SECRET", "hunter2")
    got = runner.run_program(lang_id, case["env"])
    assert got.stdout.strip().lower() in ("nil", "true") and "hunter2" not in got.stdout, got
    quiet = runner.run_program(lang_id, case["stdin"])
    assert quiet.stdout.strip() in ("nil", "0", "-1"), f"stdin is closed, so reading gets nothing: {quiet}"


@pytest.mark.parametrize("lang_id", CASE_IDS, ids=deck_ids)
def test_every_run_cleans_up_after_itself(lang_id):
    case = _case(lang_id)
    temp = Path(tempfile.gettempdir())
    before = {p.name for p in temp.glob("gotcha_run_*")}
    runner.run_program(lang_id, case["ok"])
    runner.run_program(lang_id, case["bad"])
    runner.run_program(lang_id, case["loop"], timeout=0.5)
    assert {p.name for p in temp.glob("gotcha_run_*")} == before


def test_a_one_step_tool_leaves_no_process_or_folder_behind():
    """`dotnet run` starts a compiler server that outlives the run and holds the throwaway folder open."""
    _installed("csharp")
    import subprocess

    def servers() -> set[str]:
        out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
        return {line for line in out.splitlines() if "VBCSCompiler" in line}

    temp = Path(tempfile.gettempdir())
    before_dirs, before_procs = {p.name for p in temp.glob("gotcha_run_*")}, servers()
    got = runner.run_program("csharp", RUN_CASES["csharp"]["ok"])
    assert got.ok and got.stdout.strip() == "42"
    assert {p.name for p in temp.glob("gotcha_run_*")} == before_dirs
    assert servers() <= before_procs, "a compiler server was left running"


def test_a_lisp_program_that_errors_is_a_failed_run_not_an_answer():
    """ABCL's --batch prints 'Error loading ...' and exits 0; the quiz must not take that for the output."""
    _installed("lisp")
    bad = runner.run_program("lisp", "(format t \"~a~%\" (car 5))")
    assert not bad.ok and bad.returncode == 1
    good = runner.run_program("lisp", "(format t \"~a~%\" (car (list 5)))")
    assert good.ok and good.stdout.strip() == "5"


def test_the_output_is_capped():
    _installed("lua")
    got = runner.run_program("lua", "for i = 1, 200000 do io.write('x') end")
    assert 0 < len(got.stdout) <= runner.MAX_OUTPUT


def test_a_pair_of_runs_builds_once(monkeypatch):
    _installed("go")
    from code_coach.gotchas import toolchains as tc

    calls = []
    real = tc._tool_build

    def counting(*args, **kwargs):
        build = real(*args, **kwargs)

        def wrapped(timeout):
            calls.append(1)
            return build(timeout)

        return wrapped

    monkeypatch.setattr(tc, "_tool_build", counting)
    first, second = runner.run_twice("go", RUN_CASES["go"]["ok"])
    assert first.stdout == second.stdout == "42\n" and len(calls) == 1


def test_zig_output_is_taken_from_stderr_on_a_clean_exit_only():
    _installed("zig")
    ok = runner.run_program("zig", 'const std = @import("std");\npub fn main() void {\n'
                                   '    std.debug.print("hi\\n", .{});\n}')
    assert ok.ok and ok.stdout.strip() == "hi" and ok.stderr == ""


# ── The routes, for languages that are not Python, JavaScript or C ───────

FAST = ("lua", "php", "ruby", "go", "rust", "java")


def _fast_language() -> str:
    for lang_id in FAST:
        if toolchains.available(lang_id) and DECKS.get(lang_id):
            return lang_id
    pytest.skip("none of lua, php, ruby, go, rust or java is installed here with cards, so no route can be tried")


def test_a_new_language_is_a_full_citizen_of_the_routes():
    lang_id = _fast_language()
    lang = langs.get(lang_id)
    deck = DECKS[lang_id]
    offered = server.gotchas_summary("python")["languages"]
    assert {"id": lang_id, "name": lang.name, "count": len(deck), "title": lang.title} in offered
    assert [d["id"] for d in offered] == [i for i in EXPECTED_ORDER if i in {d["id"] for d in offered}], \
        "display order"
    summary = server.gotchas_summary(lang_id)
    assert (summary["total"], summary["seen"], summary["title"]) == (len(deck), 0, lang.title)
    assert summary["syntax"][lang_id]["keywords"] == list(lang.syntax.keywords)
    first = server.gotchas_next(lang_id)
    assert first["id"] == deck[0].id, "the first card served is the first in the module"
    assert first["language"] == lang_id and len(first["options"]) == 4 and first["title"] == lang.title
    assert first["languages"] == offered
    for secret in ("answer", "answer_index", "trap", "why"):
        assert secret not in first
    card = deck[0]
    right = first["options"].index(card.answer)
    got = server.gotchas_answer(GotchaAnswerRequest(id=card.id, language=lang_id, chosen=right))
    assert got["correct"] and got["answer"] == card.answer and got["streak"] == 1
    assert server.gotchas_summary(lang_id)["seen"] == 1
    assert server.gotchas_summary("python")["seen"] == 0, "each language has its own counters"
    ran = server.gotchas_run(GotchaRunRequest(id=card.id, language=lang_id))
    assert ran["stdout"] == card.answer and ran["error"] == "" and ran["compile_error"] is False
    # Momentum keys work for any language id
    paid = server.momentum_award(MomentumAwardRequest(kind="gotcha", key=f"gotcha:{lang_id}:{card.id}"))
    assert paid["ok"] and paid["gained"] > 0
    again = server.momentum_award(MomentumAwardRequest(kind="gotcha", key=f"gotcha:{lang_id}:{card.id}"))
    assert again["gained"] == 0


def test_the_daily_5_for_a_new_language_is_its_own():
    lang_id = _fast_language()
    deck = DECKS[lang_id]
    summary = server.gotchas_summary(lang_id)
    assert summary["daily"]["total"] == min(5, len(deck))
    day = None
    ids = []
    for _ in range(summary["daily"]["total"]):
        card = server.gotchas_next(lang_id, daily=True)
        assert card["why_picked"] == "daily" and card["id"].startswith(langs.get(lang_id).prefix + "-")
        ids.append(card["id"])
        day = server.gotchas_answer(GotchaAnswerRequest(id=card["id"], language=lang_id, chosen=0))["daily"]
    assert len(set(ids)) == len(ids)
    assert day["complete"] and day["just_completed"]
    paid = server.momentum_award(MomentumAwardRequest(kind="gotcha_daily", key=f"daily:{lang_id}:{day['day']}"))
    assert paid["ok"] and paid["gained"] > 0
    assert server.gotchas_summary("python")["daily"]["complete"] is False


def test_your_own_card_in_a_new_language_takes_its_answer_from_a_real_run():
    lang_id = _fast_language()
    source = {"lua": "local t = {10, 20, 30}\nprint(#t + t[2])", "php": "<?php\necho 6 * 7, PHP_EOL;",
              "ruby": "puts [1, 2, 3].sum * 7", "go": 'package main\nimport "fmt"\nfunc main() { fmt.Println(6 * 7) }',
              "rust": 'fn main() { println!("{}", 6 * 7); }',
              "java": "public class Main { public static void main(String[] a) { System.out.println(6 * 7); } }"}
    code = source[lang_id]
    expected = {"lua": "23", "php": "42", "ruby": "42", "go": "42", "rust": "42", "java": "42"}[lang_id]
    added = server.gotchas_user_add(GotchaUserRequest(language=lang_id, code=code))
    assert added["saved"] and added["answer"] == expected and len(added["options"]) >= 3
    nxt = server.gotchas_next(lang_id)
    assert nxt["id"] == added["id"] and nxt["mine"] and nxt["why_picked"] == "yours"
    assert [c["id"] for c in server.gotchas_user_list(lang_id)["cards"]] == [added["id"]]
    assert server.gotchas_user_list("python")["cards"] == []
    assert server.gotchas_summary(lang_id)["mine"] == 1
    assert server.gotchas_user_delete(added["id"], lang_id)["deleted"] == added["id"]


def test_a_new_language_card_that_does_not_compile_is_refused_with_the_first_error():
    for lang_id in ("go", "rust"):
        if toolchains.available(lang_id) and DECKS.get(lang_id):
            break
    else:
        pytest.skip("neither go nor rust is installed here with cards")
    bad = GotchaUserRequest(language=lang_id, code=RUN_CASES[lang_id]["bad"])
    for call in (server.gotchas_user_preview, server.gotchas_user_add):
        with pytest.raises(HTTPException) as caught:
            call(bad)
        detail = str(caught.value.detail)
        assert caught.value.status_code == 400 and "does not compile" in detail and "error" in detail.lower()
        assert "gotcha_run_" not in detail and "\n" not in detail


def test_a_new_language_program_that_cannot_be_a_fair_question_is_refused():
    _installed("lua")
    if not DECKS.get("lua"):
        pytest.skip("no Lua cards yet")
    cases = {
        "printed nothing": "local x = 1",
        "waits for input": "print(io.read())",
        "different each time": "print(tostring({}))",
        "ended with exit code": "print('hi')\nos.exit(3)",
    }
    for expected, code in cases.items():
        with pytest.raises(user.CardRefused) as caught:
            user.build("lua", code)
        assert expected in str(caught.value), (expected, str(caught.value))


def test_a_language_without_a_toolchain_is_hidden_and_refused(monkeypatch):
    lang_id = _fast_language()
    name = langs.get(lang_id).name
    real = toolchains.available
    monkeypatch.setattr(toolchains, "available", lambda i: False if i == lang_id else real(i))
    assert lang_id not in gotchas.available_languages()
    assert lang_id not in [d["id"] for d in server.gotchas_summary("python")["languages"]]
    assert lang_id not in [d["id"] for d in server.gotchas_next("python")["languages"]]
    assert lang_id in DECKS, "the cards are still there, just not offered"
    refused = {
        "summary": (server.gotchas_summary, lang_id),
        "next": (server.gotchas_next, lang_id),
        "answer": (server.gotchas_answer, GotchaAnswerRequest(id=DECKS[lang_id][0].id, language=lang_id, chosen=0)),
        "run": (server.gotchas_run, GotchaRunRequest(id=DECKS[lang_id][0].id, language=lang_id)),
        "user list": (server.gotchas_user_list, lang_id),
        "user preview": (server.gotchas_user_preview, GotchaUserRequest(language=lang_id, code="x")),
        "user add": (server.gotchas_user_add, GotchaUserRequest(language=lang_id, code="x")),
        "user delete": (server.gotchas_user_delete, "mine-1", lang_id),
    }
    for label, (call, *args) in refused.items():
        with pytest.raises(HTTPException) as caught:
            call(*args)
        assert caught.value.status_code == 400, label
        assert f"No {name} toolchain" in str(caught.value.detail), (label, caught.value.detail)
    assert server.gotchas_next("python")["id"] == "py-score-90", "the others carry on"


def test_a_language_with_no_cards_yet_is_not_offered(monkeypatch):
    lang_id = _fast_language()
    monkeypatch.setattr(gotchas, "DECKS", {k: v for k, v in DECKS.items() if k != lang_id})
    assert lang_id not in gotchas.available_languages()
    with pytest.raises(HTTPException) as caught:
        server.gotchas_summary(lang_id)
    assert caught.value.status_code == 400 and "no cards yet" in str(caught.value.detail)
    assert gotchas.builtin_deck(lang_id) == ()


def test_unknown_languages_are_still_400():
    for call in (server.gotchas_summary, server.gotchas_next, server.gotchas_user_list):
        for bad in ("cobol", "C", "Rust", ""):
            if call is server.gotchas_user_list and bad == "":
                continue
            with pytest.raises(HTTPException) as caught:
                call(bad)
            assert caught.value.status_code == 400, (call.__name__, bad)


def test_an_old_progress_file_keeps_loading_and_new_languages_get_their_keys_lazily(tmp_path):
    import json

    lang_id = _fast_language()
    path = tmp_path / "gotchas.json"
    path.write_text(json.dumps({
        "version": 1,
        "stats": {"python:py-score-90": {"seen": 3, "right": 2, "last_day": "2026-10-01", "last_tick": 9, "due": None}},
        "ticks": {"python": 9}, "streak": {"python": {"now": 2, "best": 7}},
        "daily": {"python": {"day": "2026-10-01", "ids": ["py-score-90"], "results": {"py-score-90": True}}}}),
        encoding="utf-8")
    store = gotchas.GotchaStore(path, tmp_path / "gotchas_user.json")
    assert store.summary("python")["seen"] == 1 and store.summary("python")["streak_best"] == 7
    assert store.summary(lang_id)["seen"] == 0
    card = DECKS[lang_id][0]
    store.answer(lang_id, card.id, 0)
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["stats"]["python:py-score-90"]["seen"] == 3, "the old language is untouched"
    assert f"{lang_id}:{card.id}" in saved["stats"] and saved["ticks"][lang_id] == 1
    assert saved["streak"]["python"] == {"now": 2, "best": 7}
    assert lang_id in saved["streak"] and lang_id in saved["daily"]


def test_the_error_names_of_the_other_languages_are_exit_codes():
    from code_coach.gotchas.runner import RunResult

    crashed = RunResult("", "boom", 101, 0.1, False)
    assert runner.error_name("rust", crashed) == "exit code 101"
    assert runner.error_name("rust", RunResult("", "x", 1, 0.1, False, compile_error=True)) == "CompileError"
    assert runner.error_name("go", RunResult("", "", -9, 5.0, True)) == "timeout"
    assert runner.error_name("go", RunResult("42\n", "", 0, 0.1, False)) == ""
    assert runner.tidy_paths(r"C:\Users\x\AppData\Local\Temp\gotcha_run_ab12\snippet.rs:3:5: error") \
        == "snippet.rs:3:5: error"
    assert runner.tidy_paths("/tmp/gotcha_run_ab12/Main.kt:1:1: error: x") == "Main.kt:1:1: error: x"


def test_the_first_error_line_is_the_compilers_first_real_complaint():
    first = runner._first_error
    assert first("# command-line-arguments\nsnippet.go:6:2: undefined: x\nsnippet.go:7:1: more") \
        == "snippet.go:6:2: undefined: x", "Go says undefined, never 'error', under a # heading"
    assert first("snippet.c:2:5: warning: x\nsnippet.c:3:1: error: expected ';'") == "snippet.c:3:1: error: expected ';'"
    assert first("warning: unused\nerror[E0308]: mismatched types\n --> snippet.rs:2:5") \
        == "error[E0308]: mismatched types"
    assert first("") == "the compiler gave no reason"
    assert first("# only a heading") == "# only a heading"


def test_the_tools_that_start_other_tools_get_a_whitelisted_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-secret")
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_secret")
    env = toolchains._tool_env(tmp_path)
    assert "OPENAI_API_KEY" not in env and "GITHUB_TOKEN" not in env
    assert env["TEMP"] == str(tmp_path / "tmp"), "what a tool would leave in the temp folder stays in the throwaway one"
    assert toolchains._bare().keys() <= {"PYTHONIOENCODING", "SYSTEMROOT", "SystemRoot", "TEMP", "TMP"}
