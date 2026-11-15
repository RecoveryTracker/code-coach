"""Explain my code for C (code_coach/explain_c.py): coverage over the app's own code, alignment, the rules it states
held to the real compilers, and what it says the program printed.

The oracle rule: no expected value here comes from the reader. Every claim written into a rule sentence as
a printf call and what it prints is compiled and run (tests/c_oracle.py: clang -O0, clang -O2 and MSVC when present,
which must agree); the facts that are not one expression are complete programs with an exact expected output."""

from __future__ import annotations

import pytest

from code_coach import explain_c as K
from code_coach.api import server
from code_coach.api.schemas import ExplainRequest
from tests import explain_corpus as E
from tests.c_oracle import HAVE_COMPILER, c_values

needs_cc = pytest.mark.skipif(not HAVE_COMPILER, reason="needs a C compiler")


def explain(code: str, run: bool = False, context: str = ""):
    return K.explain_c(code, run=run, context=context)


# (a) coverage and never raising

def test_at_least_90_percent_of_the_apps_own_c_lines_get_a_specific_row():
    numbers = E.assert_coverage(K._read_rows, "c", 0.90)
    assert set(numbers) >= {"brain", "gotchas", "workbook"}, numbers


def test_junk_empty_and_half_typed_input_never_raises():
    E.check_never_raises(explain, extra=['printf("%d %s\\n", x);', "int main(void) {", "for (int i = 0;", "struct P {", "#define SQ(x", "x = (int", "a[", "case 1:"])
    assert explain("")["ok"] is False


def test_an_unrecognised_line_gets_the_honest_generic_row_and_is_counted():
    rows, n, bad = K._read_rows("@ ~ ^ `\nint x = 1;")
    assert any(r["text"].endswith("does not break down yet.") for r in rows)
    assert bad == ["1"] and n == 2


# (b) alignment

def test_rows_match_the_input_line_by_line():
    E.check_alignment(explain, "c")


# (c) truth

#: Facts that are not one printf call: (complete program or body of main, exact output).
EXTRA = {
    "macro": [("#define SQ(x) x * x\nint main(void) { printf(\"%d\", SQ(1 + 2)); return 0; }", "5")],
    "fallthrough": [("int main(void) { switch (1) { case 1: printf(\"a\"); case 2: printf(\"b\"); } return 0; }", "ab")],
    "ptrarith": [("int a[2] = {0, 0};\nprintf(\"%d\", (int)((char *)(a + 1) - (char *)a));", "4")],
    "postinc": [("int a[] = {7, 8};\nint *p = a;\nint v = *p++;\nprintf(\"%d %d\", v, *p);", "7 8")],
    "assignif": [("int x = 0;\nif (x = 5) printf(\"yes\");", "yes")],
}


@needs_cc
def test_every_rule_sentence_that_states_a_checkable_fact_is_held_to_the_real_compilers():
    claims = E.claims(K.FACTS)
    assert claims
    got = c_values([f"{expr};" for _f, expr, _v in claims])
    for (fid, expr, want), have in zip(claims, got):
        assert have == want, f"{fid}: `{expr}` -> the compilers printed {have!r}, the rule sentence says {want!r}"
    covered = {f for f, _e, _v in claims} | set(EXTRA)
    assert set(K.FACTS) <= covered, f"rules with no check: {sorted(set(K.FACTS) - covered)}"


@needs_cc
def test_the_facts_that_are_whole_programs_are_run_for_real():
    cases = [(p, w) for cs in EXTRA.values() for p, w in cs]
    got = c_values([p for p, _w in cases])
    for (p, want), have in zip(cases, got):
        assert have == want, f"{p!r}: the compilers gave {have!r}, expected {want!r}"


def test_the_macro_trap_is_named_only_when_the_body_is_unprotected():
    risky = " ".join(r["text"] for r in explain("#define SQ(x) x * x")["lines"])
    safe = " ".join(r["text"] for r in explain("#define SQ(x) ((x) * (x))")["lines"])
    assert K.FACTS["macro"] in risky
    assert K.FACTS["macro"] not in safe


def test_printf_specifiers_are_explained_one_by_one():
    r = explain('printf("[%5d] [%-4d] [%05.1f] %x %c %s %zu%%\\n", 1, 2, 3.0, 255, 65, "s", sizeof(int));')
    text = r["lines"][0]["text"]
    for part in ("`%5d`", "`%-4d`", "`%05.1f`", "`%x`", "`%c`", "`%s`", "`%zu`", "literal `%`", "then ends the line", "on the right"):
        assert part in text, part


def test_a_case_without_a_break_is_said_to_fall_through_and_an_empty_one_to_share():
    r = explain("switch (n) {\n  case 1:\n  case 2:\n    puts(\"a\");\n  case 3:\n    puts(\"b\");\n    break;\n}")
    texts = {row["line"]: row["text"] for row in r["lines"]}
    assert "shares" in texts[2]
    assert "no `break`" in texts[4] or "no `break`" in texts[5] or K.FACTS["fallthrough"] in " ".join(texts.values())


# (d) output notes

@needs_cc
def test_the_output_note_is_what_the_real_program_printed():
    for code in ('printf("%d\\n", 7 / 2);', 'int a[] = {3, 1, 2};\nprintf("%d %d\\n", a[0], a[2]);', '#include <stdio.h>\nint main(void) {\n    puts("hi");\n    return 0;\n}'):
        want = c_values([code])[0]
        notes = explain(code, run=True)["output_notes"]
        printed = [n[len("It printed: "):] for n in notes if n.startswith("It printed: ")]
        assert "\n".join(printed).strip() == want, (code, notes, want)


@needs_cc
def test_a_compile_error_is_an_error_note_with_no_temp_path_and_the_rows_still_come_back():
    r = explain("int x = ;\nprintf(\"%d\\n\", x);", run=True)
    assert r["error_note"] and r["error_note"].startswith("It does not compile")
    assert "gotcha_run_" not in r["error_note"] and "snippet.c" not in r["error_note"] and "\\" not in r["error_note"]
    assert "line 1" in r["error_note"], r["error_note"]
    assert len(r["lines"]) == 2


@needs_cc
def test_a_program_that_prints_nothing_gets_no_made_up_output_note():
    assert explain("int a = 5;", run=True)["output_notes"] == []


def test_a_file_of_functions_with_no_main_says_so_instead_of_running():
    r = explain("int sq(int x) {\n    return x * x;\n}", run=True)
    assert any("no main()" in n for n in r["output_notes"]), r


# (e) API

def test_the_api_reads_c_and_puts_the_drills_c_words_first():
    r = server.explain(ExplainRequest(code='printf("%x\\n", 255 & 15);', language="c", context="c_bits"))
    assert r.ok and r.lines
    assert [w.id for w in r.words][:3] == ["bitwise-operator", "bit-shift", "bit-mask"]
    assert all(w.language == "c" for w in r.words)


# (a2) every construct the brief names is read specifically on its own (see tests/test_explain_dart.py)

CONSTRUCTS = [
    "#include <stdio.h>", "#define N 10", "#define SQ(x) x * x", "#if defined(X)\n#endif", "int x = 5;", "uint8_t u = 200;", "int a[5] = {1, 2, 3};", "char s[8] = \"stone\";", "int *p = &x;", "const char *w = \"hi\";", "static int c;", "x += 2;", "x++;", "--x;",
    "int d = 7 / 2;", "int m = -7 % 3;", "u = u + 100;", "*p = 3;", "a[2] = 1;", "p = p + 1;", "int v = *p++;", "q->x = 1;", "struct P { int x, y; };", "enum { A, B = 5, C };", "typedef struct { int x; } T;", "typedef int (*Op)(int, int);", "struct P pt = {1, 2};",
    "if (x > 1) {\n    x = 0;\n} else if (x < 0) {\n    x = 1;\n} else {\n    x = 2;\n}", "for (int i = 0; i < 3; i++) {\n    x += i;\n}", "while (*p) {\n    p++;\n}", "do {\n    x--;\n} while (x > 0);", "switch (x) {\n    case 1:\n        puts(\"a\");\n        break;\n    case 2:\n    default:\n        puts(\"b\");\n}",
    "int sq(int n) {\n    return n * n;\n}", "int sq(int n);", "int main(void) {\n    return 0;\n}", "int (*f)(int) = NULL;", "r = f(3);", "printf(\"%d %5.2f %c %s %x %zu\\n\", 1, 2.0, 'a', \"s\", 255, sizeof(int));", "strlen(s);", "strcpy(b, \"a\");", "strcmp(a, b);", "memcpy(b, a, 4);", "size_t n = sizeof(a) / sizeof(a[0]);",
    "break;", "continue;", "goto end;",
]


def test_every_construct_the_brief_names_is_read_with_no_fallback_row():
    missed = []
    for code in CONSTRUCTS:
        rows, n, bad = K._read_rows(code)
        if bad or not rows:
            missed.append(code.split("\n")[0])
    assert not missed, missed
