"""code_coach/explain_programs.py: the one Python place that turns a Brain Drills fragment into a program.

It must agree with the rules the browser's "Run it" uses (web/src/lib/brainRound.ts) and with the oracles the packs are
held to (tests/dart_oracle.full_program, tests/c_oracle.full_program), so an explanation runs the same program Run it does."""

from __future__ import annotations

from code_coach import brain
from code_coach.explain_programs import C_HEADERS, dart_program, is_flutter, sql_program, wrap
from tests import c_oracle, dart_oracle
from tests.test_brain_round import results


def test_dart_programs_are_the_dart_oracles_programs():
    for code in ("7 ~/ 2", "var xs = [1, 2];\nxs.add(3);\nxs", "print(1);", "void main() {\n  print(2);\n}", "int f() => 3;\nf()"):
        p = dart_program(code)
        assert p.runnable and p.text == dart_oracle.full_program(code), code
    assert dart_program("7 ~/ 2").printed_last and dart_program("7 ~/ 2").offset == 1
    assert not dart_program("print(1);").printed_last


def test_c_programs_are_the_c_oracles_programs_and_the_headers_are_the_browsers():
    assert C_HEADERS == c_oracle.HEADERS == results()["cHeaders"]
    for code in ('printf("%d\\n", 7);', 'int x = 1;\n\nprintf("%d\\n", x);', 'int main(void) {\n    puts("x");\n}\n'):
        assert wrap("c", code).text == c_oracle.full_program(code), code
    browser = results()["cPrograms"]
    assert wrap("c", 'printf("%d\\n", 7);').text == browser["body"]
    assert wrap("c", 'int main(void) {\n    puts("x");\n}\n\n').text == browser["whole"]
    assert wrap("c", "int x = 1;\n\nprintf(\"%d\\n\", x);").text == browser["indent"]
    assert wrap("c", 'printf("a");').offset == C_HEADERS.count("\n") + 1


def test_every_brain_dart_prompt_wraps_to_the_oracle_program_unless_it_is_flutter():
    for act in brain.activities_in("dart"):
        for item in brain.make_round(act.id, 1, "dart")[:4]:
            code = item.prompt
            if act.id[:3] in ("fl_", "fs_", "fw_"):
                assert not dart_program(code, act.id).runnable
            elif is_flutter(code):
                continue
            else:
                p = dart_program(code, act.id)
                assert p.text == dart_oracle.full_program(code) or not p.runnable, (act.id, code)


def test_flutter_and_a_library_with_no_main_are_not_run():
    assert not dart_program("Row(children: [Text('a')])").runnable
    assert "Flutter widgets cannot run here" in dart_program("MaterialApp(home: Text('a'))").why_not
    assert not dart_program("class A {}\nvoid f() {}").runnable
    assert dart_program("var x = 1;\nprint(x);").runnable


def test_sql_is_the_script_as_it_is_and_other_languages_are_refused():
    assert sql_program("SELECT 1;\n").text == "SELECT 1;"
    try:
        wrap("python", "x")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("no convention for python")
