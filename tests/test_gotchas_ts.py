"""Gotchas' browser-side rules, run in node: web/src/lib/gotchas.ts and web/src/lib/codeColors.ts.

Like tests/test_brain_round.py, both files are pure TypeScript, so esbuild (already in web/node_modules) bundles
them and node runs a harness over them. The expected values are written here, worked out by hand or with Python:
a streak counted on paper, the key table, the deck line, and - for the colourer - the one invariant that
matters, that its runs join back into exactly the source, held against every built-in card's real code.
The stylesheet's colours are checked here too (WCAG contrast, reduced motion).
"""

from __future__ import annotations

import functools
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from code_coach.gotchas import DECKS, langs

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
LIB = WEB / "src" / "lib"
ESBUILD = WEB / "node_modules" / "esbuild" / "bin" / "esbuild"
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(
    NODE is None or not ESBUILD.exists(),
    reason="needs node and web/node_modules/esbuild (run npm install in web/)",
)

#: Every quote, comment opener and escape in one string, to be cut into runs by every language's colouring rules.
WEIRD = "é 😀 \x00 \\ ` \" ' (a) #| \\\n/* -- ; \"\"\" \'\'\' \n"

HARNESS = r"""
import * as G from "./gotchas.mjs";
import * as C from "./colors.mjs";
import { readFileSync } from "node:fs";

const input = JSON.parse(readFileSync(process.argv[2], "utf8"));
const out = {};

// The streak, counted by hand: right, right, wrong, right x3.
let s = 0;
out.streaks = [true, true, false, true, true, true].map((ok) => (s = G.nextStreak(s, ok)));
out.streakFromJunk = [G.nextStreak(-5, true), G.nextStreak(2.9, true), G.nextStreak(7, false)];
out.labels = [0, 1, 5, 12].map(G.streakLabel);
out.tiers = [0, 1, 4, 5, 7, 10, 15, 20, 30].map(G.streakTier);

out.keys = {
  four: ["1", "2", "3", "4", "5", "0"].map((k) => G.keyToIndex(k, 4)),
  letters: ["a", "b", "c", "d", "A", "D", "e", "E"].map((k) => G.keyToIndex(k, 4)),
  three: ["1", "3", "4", "c", "d"].map((k) => G.keyToIndex(k, 3)),
  two: ["a", "b", "c"].map((k) => G.keyToIndex(k, 2)),
  named: ["Enter", " ", "ArrowRight", "Shift", "", "ab", "12"].map((k) => G.keyToIndex(k, 4)),
  next: ["Enter", " ", "ArrowRight", "ArrowLeft", "n", "1"].map(G.isNextKey),
  letter: [0, 1, 2, 3].map(G.optionLetter),
};

out.optionStates = {
  before: [0, 1, 2, 3].map((i) => G.optionState(i, null, null)),
  pending: [0, 1, 2, 3].map((i) => G.optionState(i, 2, null)),
  right: [0, 1, 2, 3].map((i) => G.optionState(i, 1, 1)),
  wrong: [0, 1, 2, 3].map((i) => G.optionState(i, 0, 3)),
};

out.deck = [G.deckLine(34, 80), G.deckLine(0, 62), G.deckLine(3, 65, 3)];
let r = [];
for (const id of ["a", "b", "c", "a", "d", "e"]) r = G.recentIds(r, id, 3);
out.recent = { r, param: G.excludeParam(r), none: G.excludeParam([]), once: G.recentIds(["x"], "x", 3), min: G.recentIds(["x", "y"], "z", 0) };

out.daily = [
  G.dailyLine({ day: "d", total: 5, done: 2, complete: false, dots: [] }),
  G.dailyLine({ day: "d", total: 5, done: 5, complete: true, dots: [] }),
  G.dailyLine({ day: "d", total: 0, done: 0, complete: false, dots: [] }),
];
out.awardKeys = [G.cardAwardKey("python", "py-score-90"), G.cardAwardKey("javascript", "js-x"), G.dailyAwardKey("python", "2026-10-19"),
  G.cardAwardKey("c", "c-int-division"), G.dailyAwardKey("c", "2026-10-20"),
  G.cardAwardKey("rust", "rs-shadowing"), G.dailyAwardKey("csharp", "2026-10-21")];

const L = (id, name, count) => ({ id, name, count, title: name + " Quiz" });
const full = [L("python", "Python", 324), L("javascript", "JavaScript", 264), L("typescript", "TypeScript", 3), L("c", "C", 116),
  L("cpp", "C++", 3), L("go", "Go", 3), L("rust", "Rust", 3), L("csharp", "C#", 3), L("lisp", "Common Lisp", 3)];
const ids = (list) => list.map((l) => l.id);
out.languages = {
  keep: ids(G.offeredLanguages(full)),
  junk: G.offeredLanguages([L("python", "Python", 1), null, 5, {}, { id: "" }, L("python", "Python", 2), { id: "zig" }, "c"])
    .map((l) => [l.id, l.name, l.count, l.title]),
  older: [ids(G.offeredLanguages(undefined)), ids(G.offeredLanguages(null)), ids(G.offeredLanguages("python"))],
  nothing: ids(G.offeredLanguages([])),
  bareIds: ids(G.offeredLanguages(["python", "javascript", "c"])),
  pickSaved: [G.chooseLanguage("c", full), G.chooseLanguage("rust", full), G.chooseLanguage("lisp", full)],
  pickFallback: [G.chooseLanguage("zig", full), G.chooseLanguage(null, full), G.chooseLanguage(undefined, full),
    G.chooseLanguage("c", [L("javascript", "JavaScript", 1)]), G.chooseLanguage("c", [])],
  recent: [G.pushRecent([], "rust"), G.pushRecent(["rust", "go", "lua", "ruby"], "go"), G.pushRecent(["a", "b", "c", "d"], "e"),
    G.pushRecent(["a", "b"], "b", 1)],
  quick: {
    fresh: ids(G.quickLanguages(full, [], "python")),
    used: ids(G.quickLanguages(full, ["rust", "go"], "rust")),
    four: ids(G.quickLanguages(full, ["lisp", "csharp", "rust", "go"], "lisp")),
    currentAlwaysShown: ids(G.quickLanguages(full, [], "lisp")),
    few: ids(G.quickLanguages(full.slice(0, 2), [], "javascript")),
    unknownCurrent: ids(G.quickLanguages(full, ["zig"], "zig")),
    unavailableRecentIgnored: ids(G.quickLanguages(full.slice(0, 5), ["rust", "go"], "python")),
    max: ids(G.quickLanguages(full, [], "python", 2)),
  },
  filter: {
    empty: ids(G.filterLanguages(full, "")),
    c: ids(G.filterLanguages(full, "c")),
    upper: ids(G.filterLanguages(full, "RUST")),
    sharp: ids(G.filterLanguages(full, "c#")),
    plus: ids(G.filterLanguages(full, "c++")),
    none: ids(G.filterLanguages(full, "zz")),
    trimmed: ids(G.filterLanguages(full, "  go ")),
    inside: ids(G.filterLanguages(full, "script")),
    word: ids(G.filterLanguages(full, "common")),
    byId: ids(G.filterLanguages(full, "csh")),
  },
  move: {
    down: [G.moveActive(-1, "ArrowDown", 3), G.moveActive(0, "ArrowDown", 3), G.moveActive(2, "ArrowDown", 3)],
    up: [G.moveActive(-1, "ArrowUp", 3), G.moveActive(2, "ArrowUp", 3), G.moveActive(0, "ArrowUp", 3)],
    ends: [G.moveActive(1, "Home", 3), G.moveActive(1, "End", 3)],
    other: G.moveActive(1, "a", 3),
    empty: [G.moveActive(0, "ArrowDown", 0), G.moveActive(0, "End", 0)],
  },
};
out.accent = {
  hues: ["python", "rust", "go", "csharp", "rust"].map(G.hueOf),
  fixed: ["python", "javascript", "c"].map((id) => G.accentRgb(id)),
  derived: input.ids.map((id) => [id, G.hueOf(id), G.accentRgb(id)]),
  styleRust: G.accentStyle("rust"),
  hsl: [G.hslToRgb(0, 1, 0.5), G.hslToRgb(120, 1, 0.5), G.hslToRgb(240, 1, 0.5), G.hslToRgb(0, 0, 1)],
  sweep: Array.from({ length: 360 }, (_, h) => G.hslToRgb(h, G.ACCENT_S, G.ACCENT_L)),
  hints: [G.addHint("rust").includes("fn main"), G.addHint("python"), G.addHint("sql").includes("SELECT")],
};
out.labelsOfCode = [
  G.codeLabel("#include <stdio.h>\n\nint main(void) {\n    int i = 5;\n    printf(\"%d\", i);\n}"),
  G.codeLabel("arr = [1, 2, 3]\nprint(arr)"),
  G.codeLabel("#include <stdio.h>\n#include <string.h>\nint main(void)\n{"),
  G.codeLabel("   \n\nint main (void) {\n  x();"),
  G.codeLabel(""),
  G.codeLabel("a".repeat(100)).length,
];

out.errors = [
  G.errorText(new Error('{"detail":"It prints nothing."}')),
  G.errorText(new Error("plain text")),
  G.errorText(new Error('{"detail":[{"loc":["body"]}]}')),
  G.errorText("boom"),
  G.errorText(new Error("")),
];
out.lines = [G.lineCount(""), G.lineCount("a"), G.lineCount("a\n"), G.lineCount("a\nb\n\n"), G.lineCount("a\r\nb"), G.lineCount("\n\n")];

// The colourer: runs must join back into the source, for every card.
const S = input.syntax;
out.joined = input.cards.map((c) => {
  const runs = C.tokenize(c.code, S[c.language]);
  return { id: c.id, same: C.join(runs) === c.code, kinds: [...new Set(runs.map((x) => x.kind))].sort() };
});

const kinds = (code, language) => C.tokenize(code, S[language]).filter((x) => x.kind !== "space").map((x) => [x.text, x.kind]);
out.py = kinds('if score > 90:\n    print("A")  # note\nx = f"{a}" + None', "python");
out.js = kinds("const n = typeof null; // c\nconsole.log(`a${1}`, 1e-5, 0xff, NaN)", "javascript");
out.c = kinds('#include <stdio.h>\nint main(void) {\n    unsigned char c = 250; // wrap\n    return sizeof(c) + NULL; /* x */\n}', "c");
out.cMore = {
  define: kinds("#define SQUARE(x) x * x\nint y = SQUARE(2);", "c"),
  continued: kinds("#define A(x) \\\n  ((x) + 1)\nint z;", "c"),
  hashInside: kinds("  #  define N 5 // five\nint q = N;", "c"),
  midLineHash: kinds("int a = 1; # not at the start", "c"),
  strings: kinds("char s[] = \"a#b\"; char q = '\\n'; int n = 10u + 0xFFu + 3.5f;", "c"),
  notC: kinds("#include <x>", "python").slice(0, 2),
  pyHash: kinds("x = 1 # note", "python").slice(-1),
  jsNoTypes: kinds("int char", "javascript"),
  dotted: kinds("a.int", "c"),
  block: kinds("/* a\nb */ int", "c"),
};
out.odd = {
  unclosed: kinds('x = "abc\ny = 1', "python").slice(0, 4),
  triple: kinds("s = " + '"'.repeat(3) + "a\nb" + '"'.repeat(3) + "\nz", "python"),
  empty: C.tokenize("", S.python),
  dotted: kinds("a.if.b.None", "python"),
  jsBlock: kinds("/* x\ny */ 1", "javascript"),
  weird: Object.keys(S).filter((l) => C.join(C.tokenize(input.weird, S[l])) !== input.weird),
  noSyntax: C.join(C.tokenize("x = 'a' // b", undefined)) === "x = 'a' // b",
};
out.others = {
  lua: kinds("-- note\nlocal s = \"a\" --[[ block\nmore ]] print(s)", "lua"),
  lisp: kinds("(defun sq (x) ; square\n  (* x x) 1.5 :key 'sym t)", "lisp"),
  lispBlock: kinds("#| a\nb |# (format t \"~a~%\" nil)", "lisp"),
  rust: kinds("fn f<'a>(x: &'a str) -> char { 'x' }\nprintln!(\"{}\", x);", "rust"),
  sql: kinds("select name FROM t WHERE a = 'x' -- c", "sql"),
  goRaw: kinds("s := `a\nb` // c", "go"),
  php: kinds("$x = 1; # c\n// d", "php"),
  javaBlock: kinds("String t = " + '"'.repeat(3) + "\n  hi\n  " + '"'.repeat(3) + ";", "java"),
  zig: kinds("const c = 'a'; // x", "zig"),
  ruby: kinds("puts :a # c\nx.nil?", "ruby"),
  kotlin: kinds('val s = "a$b"; fun main() {}', "kotlin"),
  csharp: kinds("#region x\nvar n = 1; // c", "csharp"),
  dart: kinds("var s = " + "'".repeat(3) + "a\nb" + "'".repeat(3) + "; // c", "dart"),
  ts: kinds("const n: number = 1;", "typescript"),
  cpp: kinds("#include <vector>\nstd::vector<int> v;", "cpp"),
  swift: kinds("let x: Int? = nil", "swift"),
  odin: kinds("main :: proc() { x := 1 }", "odin"),
};

console.log(JSON.stringify(out));
"""


@functools.cache
def results() -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="gotchas_ts_"))
    try:
        (tmp / "harness.mjs").write_text(HARNESS, encoding="utf-8")
        cards = [{"id": it.id, "language": it.language, "code": it.code} for d in DECKS.values() for it in d]
        (tmp / "in.json").write_text(json.dumps({"cards": cards, "syntax": langs.syntax_payload(),
                                                 "ids": list(langs.ORDER), "weird": WEIRD}), encoding="utf-8")
        for name, out in (("gotchas", "gotchas.mjs"), ("codeColors", "colors.mjs")):
            built = subprocess.run(
                [NODE, str(ESBUILD), str(LIB / f"{name}.ts"), "--bundle", "--format=esm", "--platform=node",
                 f"--outfile={tmp / out}", "--log-level=error"],
                capture_output=True, text=True, timeout=120)
            assert built.returncode == 0, built.stderr
        ran = subprocess.run([NODE, str(tmp / "harness.mjs"), str(tmp / "in.json")], capture_output=True,
                             text=True, encoding="utf-8", timeout=120, cwd=tmp)
        assert ran.returncode == 0, ran.stderr[-3000:]
        return json.loads(ran.stdout.strip().splitlines()[-1])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_the_streak_counts_right_answers_in_a_row():
    r = results()
    assert r["streaks"] == [1, 2, 0, 1, 2, 3]
    assert r["streakFromJunk"] == [1, 3, 0]
    assert r["labels"] == ["", "1 in a row", "5 in a row", "12 in a row"]


def test_bigger_fuss_at_five_and_at_every_ten():
    assert results()["tiers"] == [0, 1, 1, 2, 1, 3, 2, 3, 3]


def test_keys_one_to_four_and_a_to_d_pick_options():
    k = results()["keys"]
    assert k["four"] == [0, 1, 2, 3, -1, -1]
    assert k["letters"] == [0, 1, 2, 3, 0, 3, -1, -1]
    assert k["three"] == [0, 2, -1, 2, -1], "a card with three options has no 4th or D"
    assert k["two"] == [0, 1, -1]
    assert k["named"] == [-1] * 7, "Enter, Space, arrows, multi-character keys pick nothing"
    assert k["next"] == [True, True, True, False, False, False]
    assert k["letter"] == ["A", "B", "C", "D"]


def test_option_states_before_and_after_an_answer():
    o = results()["optionStates"]
    assert o["before"] == ["idle"] * 4
    assert o["pending"] == ["idle", "idle", "picked", "idle"]
    assert o["right"] == ["dim", "right", "dim", "dim"]
    assert o["wrong"] == ["wrong", "dim", "dim", "reveal"]


def test_the_deck_line_and_what_was_just_seen():
    r = results()
    assert r["deck"] == ["Deck: 34/80 seen", "Deck: 0/62 seen", "Deck: 3/65 seen (3 yours)"]
    assert r["recent"]["r"] == ["a", "d", "e"], "a, b, c, a, d, e keeps the last three, each once"
    assert r["recent"]["param"] == "a,d,e"
    assert r["recent"]["none"] == ""
    assert r["recent"]["once"] == ["x"]
    assert r["recent"]["min"] == ["z"]


def test_daily_lines_and_award_keys_match_what_the_server_dedupes_on():
    r = results()
    assert r["daily"] == ["Daily 5 - 2 of 5", "Daily 5 - done today", "Daily 5"]
    assert r["awardKeys"] == ["gotcha:python:py-score-90", "gotcha:javascript:js-x", "daily:python:2026-10-19",
                              "gotcha:c:c-int-division", "daily:c:2026-10-20",
                              "gotcha:rust:rs-shadowing", "daily:csharp:2026-10-21"]


def test_the_language_switch_offers_what_the_server_says_in_its_order():
    r = results()["languages"]
    assert r["keep"] == ["python", "javascript", "typescript", "c", "cpp", "go", "rust", "csharp", "lisp"]
    assert r["junk"] == [["python", "Python", 1, "Python Quiz"], ["zig", "zig", 0, "zig Quiz"]], \
        "things that are not languages are skipped, a repeat counts once, a missing name falls back to the id"
    assert r["older"] == [["python", "javascript"]] * 3, "a server that does not say offers the two it always had"
    assert r["nothing"] == ["python"]
    assert r["bareIds"] == ["python"], "a list of bare ids is not what this server sends"


def test_a_remembered_language_that_cannot_be_used_falls_back_to_python():
    r = results()["languages"]
    assert r["pickSaved"] == ["c", "rust", "lisp"]
    assert r["pickFallback"] == ["python", "python", "python", "javascript", "python"], \
        "an unknown, missing or unavailable saved language falls back to Python (or the first on offer)"


def test_the_quick_buttons_are_the_last_used_languages_python_first_by_default():
    r = results()["languages"]
    assert r["recent"] == [["rust"], ["go", "rust", "lua", "ruby"], ["e", "a", "b", "c"], ["b"]]
    q = r["quick"]
    assert q["fresh"] == ["python", "javascript", "typescript", "c"]
    assert q["used"] == ["python", "javascript", "go", "rust"], "last used first, topped up from the front, shown in registry order"
    assert q["four"] == ["go", "rust", "csharp", "lisp"]
    assert q["currentAlwaysShown"] == ["python", "javascript", "typescript", "lisp"]
    assert q["few"] == ["python", "javascript"]
    assert q["unknownCurrent"] == ["python", "javascript", "typescript", "c"]
    assert q["unavailableRecentIgnored"] == ["python", "javascript", "typescript", "c"]
    assert q["max"] == ["python", "javascript"]


def test_the_more_menu_filters_as_you_type_and_the_arrows_wrap():
    f = results()["languages"]["filter"]
    assert f["empty"] == ["python", "javascript", "typescript", "c", "cpp", "go", "rust", "csharp", "lisp"]
    assert f["c"] == ["c", "cpp", "csharp", "lisp", "javascript", "typescript"], \
        "names and ids that start with it first, then ones that contain it, each in registry order"
    assert f["upper"] == ["rust"] and f["sharp"] == ["csharp"] and f["plus"] == ["cpp"]
    assert f["none"] == [] and f["trimmed"] == ["go"]
    assert f["inside"] == ["javascript", "typescript"] and f["word"] == ["lisp"] and f["byId"] == ["csharp"]
    m = results()["languages"]["move"]
    assert m["down"] == [0, 1, 0] and m["up"] == [2, 1, 2] and m["ends"] == [0, 2]
    assert m["other"] == 1, "any other key leaves the active row alone"
    assert m["empty"] == [-1, -1]


def _luminance_rgb(rgb) -> float:
    return _luminance("#" + "".join(f"{int(c):02x}" for c in rgb))


def test_every_language_gets_a_stable_accent_that_is_readable_on_the_dark_card():
    a = results()["accent"]
    assert a["hues"][1] == a["hues"][4] and all(0 <= h < 360 for h in a["hues"]), "the hue comes from the id alone"
    assert a["fixed"] == [[124, 196, 255], [255, 209, 102], [94, 234, 212]], "the first three keep their colours"
    t = _tokens()
    for lang_id, hue, rgb in a["derived"]:
        for surface in ("gq-bg", "gq-panel"):
            lum = _luminance_rgb(rgb)
            hi, lo = sorted((lum, _luminance(t[surface])), reverse=True)
            assert (hi + 0.05) / (lo + 0.05) >= 4.5, f"{lang_id}'s accent is {(hi + 0.05) / (lo + 0.05):.2f}:1 on {surface}"
    # and not just for the hues the registry happens to hit: every hue there is
    for h, rgb in enumerate(a["sweep"]):
        for surface in ("gq-bg", "gq-panel"):
            hi, lo = sorted((_luminance_rgb(rgb), _luminance(t[surface])), reverse=True)
            assert (hi + 0.05) / (lo + 0.05) >= 4.5, f"hue {h} is only {(hi + 0.05) / (lo + 0.05):.2f}:1 on {surface}"
    assert a["hsl"] == [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 255]]
    rust = next(rgb for lang_id, _h, rgb in a["derived"] if lang_id == "rust")
    assert a["styleRust"] == {"--gq-accent": "rgb({}, {}, {})".format(*rust), "--gq-accent-rgb": "{}, {}, {}".format(*rust)}
    assert a["hints"] == [True, "", True]


def test_no_two_languages_share_an_accent_hue_closely():
    hues = sorted((h, lang_id) for lang_id, h, _rgb in results()["accent"]["derived"]
                  if lang_id not in ("python", "javascript", "c"))
    for (h1, a), (h2, b) in zip(hues, hues[1:]):
        assert h2 - h1 >= 5, f"{a} and {b} have almost the same hue ({h1} and {h2})"


def test_your_own_cards_are_labelled_by_the_line_that_says_something():
    assert results()["labelsOfCode"] == [
        "int i = 5;", "arr = [1, 2, 3]", "{", "x();", "", 70]


def test_server_errors_read_plainly():
    r = results()
    assert r["errors"] == ["It prints nothing.", "plain text", "That did not look right; check the form and try again.",
                           "boom", "Something went wrong."]
    assert r["lines"] == [0, 1, 1, 2, 2, 0]


def test_the_colourer_gives_back_exactly_the_source_for_every_card():
    joined = results()["joined"]
    assert len(joined) == sum(len(d) for d in DECKS.values())
    assert [j["id"] for j in joined if not j["same"]] == []
    # And it is not a no-op: every card has something coloured.
    assert [j["id"] for j in joined if set(j["kinds"]) <= {"plain", "space", "punct"}] == []


def test_python_colours():
    assert results()["py"] == [
        ["if", "keyword"], ["score", "plain"], [">", "punct"], ["90", "number"], [":", "punct"],
        ["print", "fn"], ["(", "punct"], ['"A"', "string"], [")", "punct"], ["# note", "comment"],
        ["x", "plain"], ["=", "punct"], ['f"{a}"', "string"], ["+", "punct"], ["None", "const"],
    ]


def test_javascript_colours():
    assert results()["js"] == [
        ["const", "keyword"], ["n", "plain"], ["=", "punct"], ["typeof", "keyword"], ["null", "const"],
        [";", "punct"], ["// c", "comment"], ["console", "plain"], [".", "punct"], ["log", "fn"],
        ["(", "punct"], ["`a${1}`", "string"], [",", "punct"], ["1e-5", "number"], [",", "punct"],
        ["0xff", "number"], [",", "punct"], ["NaN", "const"], [")", "punct"],
    ]


def test_c_colours():
    assert results()["c"] == [
        ["#include <stdio.h>", "preproc"],
        ["int", "type"], ["main", "fn"], ["(", "punct"], ["void", "type"], [")", "punct"], ["{", "punct"],
        ["unsigned", "type"], ["char", "type"], ["c", "plain"], ["=", "punct"], ["250", "number"], [";", "punct"],
        ["// wrap", "comment"],
        ["return", "keyword"], ["sizeof", "keyword"], ["(", "punct"], ["c", "plain"], [")", "punct"],
        ["+", "punct"], ["NULL", "const"], [";", "punct"], ["/* x */", "comment"],
        ["}", "punct"],
    ]


def test_c_preprocessor_lines_strings_and_look_alikes():
    m = results()["cMore"]
    assert m["define"][:3] == [["#define SQUARE(x) x * x", "preproc"], ["int", "type"], ["y", "plain"]]
    assert m["define"][4:6] == [["SQUARE", "fn"], ["(", "punct"]], "a macro call outside its #define is a call"
    assert m["continued"][0] == ["#define A(x) \\\n  ((x) + 1)", "preproc"], "a trailing backslash continues the line"
    assert m["continued"][1:3] == [["int", "type"], ["z", "plain"]]
    assert m["hashInside"][:2] == [["#  define N 5 ", "preproc"], ["// five", "comment"]], \
        "indentation and spaces after the # are still a directive, and a comment ends it"
    assert ["#", "plain"] in m["midLineHash"], "a # that is not at the start of a line is not a directive"
    assert not any(k == "preproc" for _, k in m["midLineHash"])
    assert m["strings"][:6] == [["char", "type"], ["s", "plain"], ["[]", "punct"], ["=", "punct"],
                                ['"a#b"', "string"], [";", "punct"]], "a # inside a string is just text"
    assert ["'\\n'", "string"] in m["strings"], "a char literal is coloured like a string"
    assert [["10u", "number"], ["0xFFu", "number"], ["3.5f", "number"]] == [x for x in m["strings"] if x[1] == "number"]
    assert m["notC"][0][1] == "comment", "Python still reads # as a comment"
    assert m["pyHash"] == [["# note", "comment"]]
    assert m["jsNoTypes"] == [["int", "plain"], ["char", "plain"]], "type names are only coloured as C"
    assert m["dotted"] == [["a", "plain"], [".", "punct"], ["int", "plain"]]
    assert m["block"] == [["/* a\nb */", "comment"], ["int", "type"]]


def test_odd_input_does_not_break_the_colourer():
    o = results()["odd"]
    assert o["unclosed"][:2] == [["x", "plain"], ["=", "punct"]]
    assert o["unclosed"][2] == ['"abc', "string"], "an unclosed string ends at the line"
    assert o["unclosed"][3] == ["y", "plain"]
    assert o["triple"][:3] == [["s", "plain"], ["=", "punct"], ['"""a\nb"""', "string"]]
    assert o["empty"] == []
    assert o["dotted"] == [["a", "plain"], [".", "punct"], ["if", "plain"], [".", "punct"], ["b", "plain"],
                           [".", "punct"], ["None", "plain"]], "a name after a dot is never a keyword"
    assert o["jsBlock"] == [["/* x\ny */", "comment"], ["1", "number"]]
    assert o["weird"] == [], "every language's colourer gives back exactly the odd text it was handed"
    assert o["noSyntax"] is True, "a language with no rules still shows its text"


def test_every_language_has_its_own_comments_strings_and_names():
    o = results()["others"]
    assert o["lua"][0] == ["-- note", "comment"] and ["--[[ block\nmore ]]", "comment"] in o["lua"]
    assert ["local", "keyword"] in o["lua"] and ['"a"', "string"] in o["lua"] and ["print", "fn"] in o["lua"]
    lisp = o["lisp"]
    assert lisp[:3] == [["(", "punct"], ["defun", "keyword"], ["sq", "plain"]]
    assert ["; square", "comment"] in lisp and ["1.5", "number"] in lisp and [":key", "const"] in lisp
    assert ["x", "fn"] in lisp, "the name just after ( is a call"
    assert o["lispBlock"][0] == ["#| a\nb |#", "comment"] and ["format", "fn"] in o["lispBlock"]
    assert ['"~a~%"', "string"] in o["lispBlock"] and ["nil", "const"] in o["lispBlock"]
    rust = o["rust"]
    assert ["'a", "plain"] in rust and ["'x'", "string"] in rust, "a lifetime is not the start of a string"
    assert ["println", "fn"] in rust and ["str", "type"] in rust and rust[0] == ["fn", "keyword"]
    assert o["sql"][0] == ["select", "keyword"] and ["FROM", "keyword"] in o["sql"], "SQL keywords in any case"
    assert o["sql"][-1] == ["-- c", "comment"] and ["'x'", "string"] in o["sql"]
    assert ["`a\nb`", "string"] in o["goRaw"] and o["goRaw"][-1] == ["// c", "comment"]
    assert ["# c", "comment"] in o["php"] and ["// d", "comment"] in o["php"] and ["$x", "plain"] in o["php"]
    assert o["javaBlock"][3] == ['"""\n  hi\n  """', "string"]
    assert ["'a'", "string"] in o["zig"] and o["zig"][-1] == ["// x", "comment"]
    assert o["ruby"][3] == ["# c", "comment"]
    assert ["fun", "keyword"] in o["kotlin"] and ["main", "fn"] in o["kotlin"] and ['"a$b"', "string"] in o["kotlin"]
    assert o["csharp"][0] == ["#region x", "preproc"] and o["csharp"][-1] == ["// c", "comment"]
    assert ["'''a\nb'''", "string"] in o["dart"]
    assert ["number", "type"] in o["ts"] and ["const", "keyword"] in o["ts"]
    assert o["cpp"][0] == ["#include <vector>", "preproc"] and ["vector", "type"] in o["cpp"]
    assert ["int", "type"] in o["cpp"]
    assert ["Int", "type"] in o["swift"] and ["nil", "const"] in o["swift"]
    assert ["proc", "keyword"] in o["odin"] and ["1", "number"] in o["odin"]


# ── The stylesheet ──────────────────────────────────────────────────────


def _luminance(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    channels = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _contrast(a: str, b: str) -> float:
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _tokens() -> dict[str, str]:
    css = (WEB / "src" / "styles" / "gotchas.css").read_text(encoding="utf-8")
    block = css.split(".gq-wrap {", 1)[1].split("}", 1)[0]
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})\s*;", block))


def test_every_text_colour_on_the_card_is_at_least_aa():
    t = _tokens()
    for surface in ("gq-bg", "gq-panel"):
        for name in ("gq-text", "gq-dim", "gq-ok", "gq-bad", "gq-py", "gq-js", "gq-c", "tk-keyword", "tk-string",
                     "tk-number", "tk-comment", "tk-fn", "tk-const", "tk-punct", "tk-type", "tk-preproc"):
            ratio = _contrast(t[name], t[surface])
            assert ratio >= 4.5, f"{name} on {surface} is {ratio:.2f}:1"
    for name in ("gq-js",):
        assert _contrast(t["gq-bg"], t[name]) >= 4.5, "dark text on the yellow Trap / Yours badge"


def test_motion_stops_under_reduced_motion():
    css = (WEB / "src" / "styles" / "gotchas.css").read_text(encoding="utf-8")
    reduced = css.split("@media (prefers-reduced-motion: reduce)", 1)[1]
    for selector in (".gq-streak.tier3", ".gq-card.right", ".gq-card.wrong"):
        assert selector in reduced
    assert "animation: none" in reduced
    # Right and wrong never rely on colour alone: a mark and screen-reader text come with them.
    assert '"\\2713"' in css and '"\\2717"' in css


def test_the_card_never_scrolls_the_page_sideways():
    css = (WEB / "src" / "styles" / "gotchas.css").read_text(encoding="utf-8")
    code = css.split(".gq-code {", 1)[1].split("}", 1)[0]
    assert "overflow-x: auto" in code and "white-space: pre" in code and "max-width: 100%" in code
    assert "min-width: 0" in css.split(".gq-card {", 1)[1].split("}", 1)[0]
