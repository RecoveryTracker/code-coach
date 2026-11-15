"""Explain my code for Dart (code_coach/explain_dart.py): coverage over the app's own code, alignment, the rules it states
held to the real `dart`, and what it says the program printed.

The oracle rule: no expected value here comes from the reader. Every ``EXPR` gives `VALUE`` claim written into a rule
sentence is run in the real dart and compared; the facts about errors are programs with an expected outcome."""

from __future__ import annotations

import pytest

from code_coach import explain_dart as D
from code_coach.api import server
from code_coach.api.schemas import ExplainRequest
from tests import explain_corpus as E
from tests.dart_oracle import DART, dart_values

needs_dart = pytest.mark.skipif(not DART, reason="needs dart")


def explain(code: str, run: bool = False, context: str = ""):
    return D.explain_dart(code, run=run, context=context)


# (a) coverage and never raising

def test_at_least_90_percent_of_the_apps_own_dart_lines_get_a_specific_row():
    numbers = E.assert_coverage(D._read_rows, "dart", 0.90)
    assert set(numbers) >= {"brain", "gotchas", "workbook"}, numbers


def test_junk_empty_and_half_typed_input_never_raises():
    E.check_never_raises(explain, extra=["class A {", "void main() {\n  var x = [1,\n", "Row(children: [", "if (a) {\n} else", "switch (x) {\n  1 =>", "x ??=", "print('${"])
    assert explain("")["ok"] is False and explain("")["lines"] == []


def test_an_unrecognised_line_gets_the_honest_generic_row_and_is_counted():
    rows, n, bad = D._read_rows("# ~ ^\nvar x = 1;")
    assert any(r["text"].endswith("does not break down yet.") for r in rows)
    assert bad == ["1"] and n == 2


# (b) alignment

def test_rows_match_the_input_line_by_line():
    E.check_alignment(explain, "dart")


# (c) truth

#: Facts that are not an expression's value: program -> expected outcome ("error" starts the output with ERROR).
EXTRA = {
    "bang": [("String? s; print(s!);", "ERROR")],
    "nullassign": [("int? a; a ??= 5; int? b = 1; b ??= 9; print('$a $b');", "5 1")],
    "final": [("void main() { final x = 1; x = 2; }", "COMPILE ERROR")],
    "const": [("void main() { const xs = [1]; xs.add(2); }", "ERROR")],
    "late": [("late int x; print(x);", "ERROR")],
    "nofall": [("switch (1) { case 1: print('a'); case 2: print('b'); }", "a")],
    "rethrow": [("try { try { throw 'x'; } catch (e) { rethrow; } } catch (e) { print(e); }", "x")],
}


@needs_dart
def test_every_rule_sentence_that_states_a_checkable_fact_is_held_to_the_real_dart():
    claims = E.claims(D.FACTS)
    assert claims, "the facts carry claims"
    got = dart_values([f"print({expr});" for _f, expr, _v in claims])
    for (fid, expr, want), have in zip(claims, got):
        assert have == want, f"{fid}: `{expr}` -> real dart printed {have!r}, the rule sentence says {want!r}"
    covered = {f for f, _e, _v in claims} | set(EXTRA)
    assert set(D.FACTS) <= covered, f"rules with no check: {sorted(set(D.FACTS) - covered)}"


@needs_dart
def test_the_facts_about_errors_and_assignment_are_programs_run_for_real():
    programs = [p for cases in EXTRA.values() for p, _w in cases]
    got = dart_values(programs)
    for (p, want), have in zip([c for cases in EXTRA.values() for c in cases], got):
        assert (want in have if want.isupper() else have == want), f"{p!r}: real dart gave {have!r}, expected {want!r}"


def test_a_row_that_states_a_rule_uses_the_checked_sentence():
    r = explain("print(-7 % 3);\nvar q = 7 ~/ 2;\nvar d = 7 / 2;")
    text = " ".join(row["text"] for row in r["lines"])
    for fid in ("mod", "tdiv", "div"):
        assert D.FACTS[fid] in text, fid


# (d) output notes

@needs_dart
def test_the_output_note_is_what_the_real_program_printed():
    for code in ("print(2 + 3);", "var xs = [3, 1, 2];\nxs.sort();\nprint(xs);\nprint(xs.length);", "7 ~/ 2"):
        want = dart_values([code])[0].split("\n")
        notes = explain(code, run=True)["output_notes"]
        printed = [n[len("It printed: "):] for n in notes if n.startswith("It printed: ")]
        assert printed == want, (code, notes, want)


@needs_dart
def test_a_bare_last_line_is_said_to_be_printed_for_you_and_a_silent_program_has_no_made_up_note():
    notes = explain("7 ~/ 2", run=True)["output_notes"]
    assert any("bare value" in n for n in notes)
    assert explain("var x = 1;", run=True)["output_notes"] == []


@needs_dart
def test_a_compile_error_is_an_error_note_with_no_temp_path_and_the_rows_still_come_back():
    r = explain("var x = ;\nprint(x);", run=True)
    assert r["error_note"] and r["error_note"].startswith("It does not compile")
    assert "gotcha_run_" not in r["error_note"] and "snippet.dart" not in r["error_note"] and "\\" not in r["error_note"]
    assert "line 1" in r["error_note"], r["error_note"]
    assert len(r["lines"]) == 2


@needs_dart
def test_a_runtime_error_is_an_error_note():
    r = explain("var xs = [1];\nprint(xs[3]);", run=True)
    assert "RangeError" in (r["error_note"] or ""), r


def test_flutter_widgets_are_read_but_never_run():
    code = "Row(children: [Text('a'), Icon(Icons.add)])"
    r = explain(code, run=True)
    assert r["error_note"] is None
    assert any("Flutter widgets cannot run here" in n for n in r["output_notes"])
    assert any("Row" in row["text"] and "children" in row["text"] for row in r["lines"]), r["lines"]
    by_id = explain("Placeholder()", run=True, context="fl_flex")
    assert any("Flutter widgets cannot run here" in n for n in by_id["output_notes"])
    r2 = explain("class K extends StatefulWidget {\n  createState() => S();\n}\nclass S extends State<K> {\n  int n = 0;\n  void initState() {}\n  Widget build(c) => Text('$n');\n}", run=False)
    joined = " ".join(row["text"] for row in r2["lines"])
    assert "State object" in joined and "initState" in joined and "build" in joined


def test_widget_and_dart_constructs_are_named_in_plain_words():
    r = explain("class Dog extends Animal with Walks {\n  final String name;\n  Dog(this.name);\n  Dog.puppy() : name = 'p';\n  String get shout => name.toUpperCase();\n}\nenum Mode { a, b }\n"
                "var s = switch (x) {\n  1 => 'one',\n  _ => 'many',\n};\nfor (var i = 0; i < 3; i++) {}\nvoid f() async {\n  await g();\n}")
    joined = " ".join(row["text"] for row in r["lines"]).lower()
    for word in ("extends animal", "mixing in walks", "constructor of dog", "named constructor", "getter shout", "enum", "matches 1", "counts with i", "async", "waits for"):
        assert word in joined, word


# (e) API

def test_the_api_reads_dart_and_puts_the_drills_dart_words_first():
    r = server.explain(ExplainRequest(code="var s = 'a';\nprint(s ?? 'b');", language="dart", context="dart_eval"))
    assert r.ok and r.lines and r.error_note is None
    assert "Creates the variable s" in r.lines[0].text, "read by the Dart reader, not by Python's"
    assert r.words and r.words[0].language == "dart" and r.words[0].id == "expression"
    assert all(w.language == "dart" for w in r.words)
    assert any("It printed: a" in n for n in r.output_notes) or not DART


def test_a_flutter_drill_item_explains_and_says_widgets_cannot_run():
    r = server.explain(ExplainRequest(code="Row(children: [Text('a')])", language="dart", context="fl_flex"))
    assert r.ok and r.lines and any("cannot run" in n for n in r.output_notes)


def test_a_program_that_never_ends_is_skipped_with_a_note_not_an_exception():
    r = explain("while (true) {}", run=True)
    assert any("stopped" in n for n in r["output_notes"]) or r["error_note"], r


# (a2) every construct the brief names is read specifically on its own, so dropping one rule fails here even when the
# corpus-wide percentage would hide it

CONSTRUCTS = [
    "var x = 1;", "final y = 'a';", "const z = [1, 2];", "late int n;", "int? m;", "String s = 'a' + 'b';", "x += 2;", "x ??= 5;", "var a = b ?? 3;", "var c = d?.length;",
    "var e = f!;", "var q = 7 ~/ 2;", "var r = -7 % 3;", "print('${x + 1} items');", "var l = [1, ...a, if (x > 1) 2, for (var i in a) i];", "var sb = StringBuffer()..write('x');",
    "if (x > 1) {\n  print(1);\n} else if (x < 0) {\n  print(2);\n} else {\n  print(3);\n}", "for (var i = 0; i < 3; i++) {\n  print(i);\n}", "for (var v in [1, 2]) {\n  print(v);\n}",
    "while (x < 3) {\n  x++;\n}", "do {\n  x++;\n} while (x < 3);", "switch (x) {\n  case 1:\n    print(1);\n    break;\n  default:\n    print(0);\n}", "var t = switch (x) {\n  1 => 'a',\n  int n when n > 3 => 'b',\n  _ => 'c',\n};",
    "int add(int a, int b) => a + b;", "void f({required int a, int b = 1}) {\n  print(a);\n}", "var g = (int a) => a * 2;", "class A extends B with C implements D {\n  final int x;\n  A(this.x);\n  A.named() : x = 1;\n  factory A.f() => A(1);\n  const A.c(this.x);\n  int get v => x;\n  set v(int n) {}\n  static int s = 1;\n}",
    "mixin M {\n  void m() {}\n}", "extension E on int {\n  int get d => this * 2;\n}", "enum Color { red, green }", "sealed class S {}", "var (a, b) = (1, 2);", "var rec = (1, name: 'x');", "try {\n  f();\n} on FormatException catch (e) {\n  print(e);\n} catch (e, st) {\n  rethrow;\n} finally {\n  print(1);\n}",
    "throw StateError('x');", "Future<void> f() async {\n  await g();\n}", "Future.delayed(Duration.zero).then((_) => print(1));", "Stream<int> s() async* {\n  yield 1;\n}", "import 'dart:math';", "Row(children: [Text('a'), Icon(Icons.add)]);",
    "class W extends StatefulWidget {\n  createState() => S();\n}", "class S extends State<W> {\n  void initState() {\n    super.initState();\n  }\n  Widget build(BuildContext c) {\n    return Text('a');\n  }\n}", "setState(() {\n  n++;\n});", "xs.map((x) => x * 2).toList();",
]


def test_every_construct_the_brief_names_is_read_with_no_fallback_row():
    missed = []
    for code in CONSTRUCTS:
        rows, n, bad = D._read_rows(code)
        if bad or not rows:
            missed.append(code.split("\n")[0])
    assert not missed, missed
