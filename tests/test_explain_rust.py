"""Explain my code for Rust (code_coach/explain_rust.py): coverage over the app's own Rust, alignment, the rules it states
held to the real rustc, the exact words of the important rows, and what it says the program printed.

The oracle rule: no expected value here comes from the reader. Every claim written into a rule sentence as
`EXPR` gives `VALUE` is put in `println!("{}", EXPR)` and run by rustc (tests/rust_oracle.py: debug and -O must agree); the
facts that are not one expression (a move, a borrow, shadowing, `?`, an overflow panic) are complete programs with the exact
outcome rustc gives."""

from __future__ import annotations

import time
from collections import Counter
from pathlib import Path

import pytest

from code_coach import explain_rust as K
from code_coach.explain_programs import wrap
from tests import explain_corpus as E
from tests.rust_oracle import HAVE_RUSTC, full_program, rust_values

needs_rustc = pytest.mark.skipif(not HAVE_RUSTC, reason="needs rustc")


def explain(code: str, run: bool = False, context: str = ""):
    return K.explain_rust(code, run=run, context=context)


def texts(code: str) -> dict[int, str]:
    return {r["line"]: r["text"] for r in explain(code)["lines"]}


# ── the corpus: every bit of Rust the app itself shows ─────────

def _glossary() -> tuple[tuple[str, str], ...]:
    from code_coach import glossary

    return tuple((e.id, e.example) for e in glossary.all_entries("rust") if e.example)


def corpora() -> dict[str, tuple[tuple[str, str], ...]]:
    return {"brain": E.brain("rust"), "glossary": _glossary(), "gotchas": E.gotchas("rust")}


def _coverage() -> dict[str, tuple[int, int, Counter]]:
    out = {}
    for name, items in corpora().items():
        total = bad = 0
        shapes: Counter = Counter()
        for _label, code in items:
            _rows, n, badlines = K._read_rows(code)
            total += n
            bad += len(badlines)
            raw = code.split("\n")
            for b in badlines:
                shapes[E.shape(raw[int(b) - 1])] += 1
        out[name] = (total, bad, shapes)
    return out


# (a) coverage

def test_at_least_90_percent_of_the_apps_own_rust_lines_get_a_specific_row():
    got = _coverage()
    assert set(got) == {"brain", "glossary", "gotchas"}
    problems = []
    for name, (total, bad, shapes) in got.items():
        assert total > 300, (name, total)
        ratio = (total - bad) / total
        if ratio < 0.90:
            top = "\n".join(f"  {n:4d}  {s}" for s, n in shapes.most_common(15))
            problems.append(f"rust {name}: {ratio:.1%} specific ({bad} of {total} lines fell back); the commonest:\n{top}")
    assert not problems, "\n".join(problems)


def test_an_unrecognised_line_gets_the_honest_generic_row_and_is_counted():
    rows, n, bad = K._read_rows("@ ~ ^ `\nlet x = 1;")
    assert any(r["text"].endswith("does not break down yet.") for r in rows)
    assert bad == ["1"] and n == 2


# (b) alignment

def test_rows_match_the_input_line_by_line():
    for name, items in corpora().items():
        for label, code in items[:400]:
            r = explain(code)
            raw = code.split("\n")
            last = 0
            for row in r["lines"]:
                assert 1 <= row["line"] <= len(raw), (name, label, row)
                assert row["source"] == raw[row["line"] - 1].strip(), (name, label, row)
                assert row["depth"] >= 0 and isinstance(row["text"], str) and row["text"].strip(), (name, label, row)
                assert row["line"] >= last, (name, label, "rows out of line order")
                last = row["line"]


def test_closing_braces_and_comment_only_lines_are_not_rows():
    r = explain("// a note\nfn main() {\n    /* a\n    note */\n    let x = 1;\n}\n")
    assert [row["line"] for row in r["lines"]] == [2, 5]


# (c) never raises

ADVERSARIAL = [
    "&mut " * 4000, "(" * 3000, "[" * 3000 + "]" * 10, "{ " * 3000, "} " * 3000, "a." * 5000, "a.b()" * 2000, "|x| " * 2000, "if " * 3000, "let " * 3000,
    '"' * 5001, "'" * 3000, "'a " * 3000, "/*" * 3000, 'r#"' * 2000, "<" * 3000, "x::" * 3000, "match x { " * 500, "fn f(" * 1000, "#[" * 2000,
    "1.." * 3000, "-> " * 3000, "=> " * 3000, "let x = " + "vec![ " * 500, "x = " + "(a + " * 800 + ")" * 800, "fn f(){\n" * 400, "struct A {\n" * 500,
]
RUSTY = [
    'let s = r#"a "quoted" {} word"#;', 'let b = br"raw bytes";', "fn f<'a>(x: &'a str) -> &'a str { x }", "let c = 'a';\nlet d: &'static str = \"x\";",
    "/* outer /* nested */ still a comment */\nlet x = 1;", "let t = '\\'';\nlet u = '\\u{1F600}';", "'outer: loop { break 'outer; }", "let r = 1..=5;\nlet q = ..3;\nlet w = 2..;",
    "match x {", "if let Some(x) = ", "fn f(", "let v = vec![", "struct P {", "impl", "let x: Vec<Vec<i32>> = Vec::new();", "x.0.1.2", "1.max(2)", "let (a, b", "|x| x +", "a ? ? ?", "println!(", 'println!("{', "#[derive(",
]


def test_junk_empty_and_half_typed_input_never_raises_and_stays_fast():
    E.check_never_raises(explain, extra=RUSTY)
    for code in ADVERSARIAL:
        t = time.time()
        r = explain(code)
        assert isinstance(r, dict) and isinstance(r["lines"], list), repr(code[:30])
        assert time.time() - t < 2.0, repr(code[:30])
    assert explain("")["ok"] is False


def test_the_huge_file_is_still_quick():
    t = time.time()
    explain("let x = 1;\n" * 5000)
    assert time.time() - t < 2.0


# (d) the rules it states are true

#: Facts that are not one expression: (a complete program or the body of main, what rustc gives).
#: "X*" means the outcome starts with X; "~X" means it contains X.
EXTRA: dict[str, list[tuple[str, str]]] = {
    "debugvec": [('let v = vec![1, 2];\nprintln!("{}", v);', "COMPILE ERROR: error[E0277]*")],
    "shadow": [('let x = 5;\nlet x = x * 2;\n{\n    let x = x + 1;\n    println!("{}", x);\n}\nprintln!("{}", x);', "11\n10"),
               ('let x = "five";\nlet x = x.len();\nprintln!("{}", x);', "4")],
    "immut": [('let x = 5;\nx = 6;\nprintln!("{}", x);', "COMPILE ERROR: error[E0384]*")],
    "move": [('let s = String::from("a");\nlet t = s;\nprintln!("{} {}", s, t);', "COMPILE ERROR: error[E0382]*"),
             ('let a = 5;\nlet b = a;\nprintln!("{} {}", a, b);', "5 5")],
    "clonefact": [('let s = String::from("a");\nlet t = s.clone();\nprintln!("{} {}", s, t);', "a a")],
    "borrow": [('fn len_of(s: &String) -> usize { s.len() }\nfn main() {\n    let s = String::from("ab");\n    let n = len_of(&s);\n    println!("{} {}", s, n);\n}', "ab 2")],
    "mutborrow": [('let mut v = vec![1];\nlet a = &mut v;\nlet b = &mut v;\na.push(2);\nb.push(3);', "COMPILE ERROR: error[E0499]*")],
    "deref": [('let mut x = 5;\nlet r = &mut x;\n*r += 1;\nprintln!("{}", x);', "6")],
    "exhaustive": [('let n = 3;\nmatch n {\n    1 => println!("one"),\n    2 => println!("two"),\n}', "COMPILE ERROR: error[E0004]*"),
                   ('let n = 3;\nmatch n {\n    1 => println!("one"),\n    _ => println!("other"),\n}', "other")],
    "qmark": [('fn f(s: &str) -> Result<i32, String> {\n    let n: i32 = s.parse().map_err(|_| "bad".to_string())?;\n    Ok(n + 1)\n}\nfn main() {\n    println!("{:?} {:?}", f("1"), f("x"));\n}', 'Ok(2) Err("bad")')],
    "overflow": [('let a: u8 = std::hint::black_box(255);\nlet b = a + 1;\nprintln!("{}", b);', "~attempt to add with overflow")],
    "tail": [("fn f() -> i32 { 3 }\nfn main() { println!(\"{}\", f()); }", "3"),
             ("fn g() -> i32 { 3; }\nfn main() { println!(\"{}\", g()); }", "COMPILE ERROR: error[E0308]*")],
    "unwrapnone": [('let n: Option<i32> = None;\nprintln!("{}", n.unwrap());', "PANIC: called `Option::unwrap()` on a `None` value")],
    "indexpanic": [('let v = vec![1, 2, 3];\nlet i = std::hint::black_box(7);\nprintln!("{}", v[i]);', "PANIC: index out of bounds*")],
    "movecl": [('let s = String::from("a");\nlet f = move || s.len();\nprintln!("{} {}", f(), s);', "COMPILE ERROR: error[E0382]*")],
    "rc": [('use std::rc::Rc;\nfn main() {\n    let a = Rc::new(5);\n    let b = Rc::clone(&a);\n    println!("{} {}", Rc::strong_count(&a), b);\n}', "2 5")],
    "refcell": [('use std::cell::RefCell;\nlet c = RefCell::new(1);\nlet a = c.borrow_mut();\nlet b = c.borrow_mut();\nprintln!("{} {}", a, b);', "PANIC:*")],
    "labeled": [("let mut n = 0;\n'outer: for i in 0..3 {\n    for j in 0..3 {\n        if j == 1 { continue 'outer; }\n        if i == 2 { break 'outer; }\n        n += 1;\n    }\n}\nprintln!(\"{}\", n);", "2")],
    "loopvalue": [('let mut i = 0;\nlet v = loop {\n    i += 1;\n    if i == 3 { break i * 10; }\n};\nprintln!("{}", v);', "30")],
    "lazy": [('let v = vec![1, 2];\nlet _it = v.iter().map(|x| {\n    println!("saw {}", x);\n    x * 2\n});\nprintln!("done");', "done"),
             ('let v = vec![1, 2];\nlet total: i32 = v.iter().map(|x| {\n    println!("saw {}", x);\n    x * 2\n}).sum();\nprintln!("{}", total);', "saw 1\nsaw 2\n6")],
    "needsmut": [('let v = Vec::new();\nv.push(1);\nprintln!("{:?}", v);', "COMPILE ERROR: error[E0596]*")],
    "formove": [('let v = vec![1, 2];\nfor x in v {\n    println!("{}", x);\n}\nprintln!("{}", v.len());', "COMPILE ERROR: error[E0382]*"),
                ('let v = vec![1, 2];\nfor x in &v {\n    println!("{}", x);\n}\nprintln!("{}", v.len());', "1\n2\n2")],
    "ifexpr": [('let x = if 3 > 2 { 1 } else { 2 };\nprintln!("{}", x);', "1"), ('let x = if true { 1 } else { "a" };', "COMPILE ERROR: error[E0308]*")],
    "unsafe": [('let x = 5;\nlet p = &x as *const i32;\nlet y = unsafe { *p };\nprintln!("{}", y);', "5"),
               ('let x = 5;\nlet p = &x as *const i32;\nprintln!("{}", *p);', "COMPILE ERROR: error[E0133]*")],
}


def _matches(got: str, want: str) -> bool:
    if want.startswith("~"):
        return want[1:] in got
    if want.endswith("*"):
        return got.startswith(want[:-1])
    return got == want


@needs_rustc
def test_every_rule_sentence_that_states_a_checkable_fact_is_held_to_the_real_rustc():
    claims = E.claims(K.FACTS)
    assert len(claims) >= 40
    got = rust_values([f'println!("{{}}", {expr});' for _f, expr, _v in claims])
    for (fid, expr, want), have in zip(claims, got):
        assert have == want, f"{fid}: `{expr}` -> rustc printed {have!r}, the rule sentence says {want!r}"
    covered = {f for f, _e, _v in claims} | set(EXTRA)
    assert set(K.FACTS) <= covered, f"rules with no check: {sorted(set(K.FACTS) - covered)}"
    assert set(EXTRA) <= set(K.FACTS), f"checks for no rule: {sorted(set(EXTRA) - set(K.FACTS))}"


@needs_rustc
def test_the_facts_that_are_whole_programs_are_run_for_real():
    cases = [(fid, p, w) for fid, cs in EXTRA.items() for p, w in cs]
    got = rust_values([p for _f, p, _w in cases])
    for (fid, p, want), have in zip(cases, got):
        assert _matches(have, want), f"{fid}: {p!r}: rustc gave {have!r}, expected {want!r}"


def test_a_rule_sentence_is_shown_once_per_explanation():
    r = explain('println!("{}", 7 / 2);\nprintln!("{}", 9 / 2);\nprintln!("{}", 1 / 3);')
    assert sum(row["text"].count(K.FACTS["div"]) for row in r["lines"]) == 1
    r2 = explain('let x = 5;\nlet x = x + 1;\nlet x = x + 2;')
    assert sum(row["text"].count(K.FACTS["shadow"]) for row in r2["lines"]) == 1


def test_float_division_does_not_claim_the_fraction_is_lost():
    assert K.FACTS["div"] not in " ".join(texts('println!("{}", 7.0 / 2.0);').values())


def test_the_reader_never_mentions_the_glossary():
    assert "glossary" not in Path(K.__file__).read_text(encoding="utf-8").lower()


# (e) exact sentences for the important rows

def test_a_move_is_named_a_move():
    t = texts('let s = String::from("a");\nlet t = s;')
    assert t[1] == 'Creates s (fixed: no `mut`), set to a String made from the text "a".'
    assert t[2] == "Creates t (fixed: no `mut`), set to s (this MOVES s into t: s cannot be used again afterwards). " + K.FACTS["move"]


def test_a_number_is_not_said_to_move():
    t = texts("let a = 5;\nlet b = a;")
    assert "MOVES" not in t[2] and t[2] == "Creates b (fixed: no `mut`), set to a."


def test_passing_an_owned_value_to_a_function_is_a_move_and_a_reference_is_a_borrow():
    t = texts('let s = String::from("a");\nlet n = eat(s);\nlet m = look(&s);')
    assert "(this moves s in: it cannot be used again afterwards)" in t[2]
    assert t[3] == "Creates m (fixed: no `mut`), set to the result of calling look with a reference to s. " + K.FACTS["borrow"]


def test_shadowing_is_called_shadowing():
    t = texts("let x = 5;\nlet x = x * 2;")
    assert t[1] == "Creates x (fixed: no `mut`), set to 5."
    assert t[2] == "Creates a new x that shadows the earlier x (fixed: no `mut`), set to x times 2. " + K.FACTS["shadow"]


def test_a_let_in_an_inner_block_that_reuses_a_name_shadows_the_outer_one():
    t = texts("let x = 1;\n{\n    let x = 2;\n}\nlet y = 3;")
    assert t[3].startswith("Creates a new x that shadows the earlier x")
    assert t[5] == "Creates y (fixed: no `mut`), set to 3."


def test_the_question_mark_says_it_returns_early():
    t = texts('fn f(s: &str) -> Result<i32, String> {\n    let n = s.parse::<i32>().map_err(|_| "bad".to_string())?;\n    Ok(n)\n}')
    assert "if that is an Err (or None) this function stops here and returns it (`?`)" in t[2]
    assert K.FACTS["qmark"] in t[2]
    assert t[3].startswith("Gives an Ok holding n as the value of this block")


def test_a_match_arm_with_a_guard_says_the_guard():
    t = texts('match n {\n    x if x > 5 => "big",\n    0 => "zero",\n    1..=5 => "small",\n    Some(y) => y,\n    _ => "other",\n}')
    assert t[2] == 'For any value, calling it x, but only if x is greater than 5: gives the text "big".'
    assert t[3] == 'When it is 0: gives the text "zero".'
    assert t[4] == 'When it is a value from 1 to 5 (both included): gives the text "small".'
    assert t[5] == "When it is a Some holding y: gives y."
    assert t[6] == 'In every other case (`_` matches anything that is left): gives the text "other".'


def test_a_format_width_is_read_one_placeholder_at_a_time():
    r = explain('println!("[{:>5}] [{:<4}] [{:^6}] [{:05}] {:.2} {:x} {:#b} {name}", a, b, c, d, e, f, g);')
    text = r["lines"][0]["text"]
    for part in ("`{:>5}` shows a, padded to at least 5 wide, right-aligned (padding on the left)", "`{:<4}` shows b, padded to at least 4 wide, left-aligned (padding on the right)", "`{:^6}` shows c, padded to at least 6 wide, centred",
                 "`{:05}` shows d, padded with zeros to at least 5 wide", "`{:.2}` shows e, with 2 digits after the point", "`{:x}` shows f in hexadecimal", "`{:#b}` shows g in binary", "`{name}` shows the variable name", "then ends the line"):
        assert part in text, part
    assert K.FACTS["width"] in text


def test_debug_display_and_positional_placeholders():
    t = texts('println!("{} {:?} {1} {0}", a, b);')[1]
    assert "`{}` shows a" in t and "`{:?}` shows b in Debug form" in t and "`{1}` shows b" in t and "`{0}` shows a" in t


def test_print_without_a_newline_and_to_the_error_output():
    assert "without ending the line" in texts('print!("a");')[1]
    assert "error output" in texts('eprintln!("a");')[1]


def test_a_function_header_reads_parameters_return_type_self_generics_and_lifetimes():
    t = texts("fn add(a: i32, b: i32) -> i32 {\n    a + b\n}")
    assert t[1] == "Defines the function add, taking a (an i32), b (an i32), giving back an i32 (a 32-bit whole number, can be negative)."
    assert t[2] == "Gives a plus b as the value of this block (the last expression, with no `;`). " + K.FACTS["tail"]
    m = texts("impl P {\n    fn a(&self) -> i32 { 1 }\n    fn b(&mut self) { }\n    fn c(self) { }\n    fn d() { }\n}")
    assert "It borrows the value it is called on (`&self`)" in m[2]
    assert "so it can change it (`&mut self`)" in m[3]
    assert "takes ownership of the value it is called on (`self`)" in m[4]
    assert m[5].startswith("Defines the associated function d (called as Type::d, with no `self`)")
    g = texts("fn show<T: Display>(x: T) {\n}\nfn pick<'a>(x: &'a str) -> &'a str {\n    x\n}")
    assert "T stands for any type that can be shown with `{}`" in g[1]
    assert "`'a` is a lifetime name" in g[3]


def test_let_forms_typed_mut_destructuring_and_let_else():
    t = texts("let mut n: u8 = 7;\nlet (a, b) = (1, 2);\nlet P { x, y } = p;\nlet _ = f();\nlet Some(v) = o else {\n    return;\n};")
    assert t[1] == "Creates n (changeable: it has `mut`), a u8 (a whole number from 0 to 255), set to 7."
    assert t[2].startswith("Unpacks a tuple of 1, 2 into a, b: the first name gets the first part")
    assert t[3].startswith("Unpacks p into x, y: each name gets the field of the same name")
    assert t[4] == "Works out the result of calling f and throws the result away."
    assert t[5].startswith("Tries to unpack o as a Some holding v: if it fits")


def test_assignment_and_compound_assignment_and_deref():
    t = texts("let mut n = 0;\nn = 5;\nn += 2;\n*r += 1;\nv[0] = 9;")
    assert t[2].startswith("Sets n to 5 (replacing what it held; n must have been made with `mut`).")
    assert t[3] == "Adds 2 to n."
    assert t[4].startswith("Adds 1 to what r points to.")
    assert t[5].startswith("Stores 9 at position 0 of v.")


def test_loops_if_and_labels_are_read():
    t = texts("for i in 0..3 {\n}\nfor i in 0..=3 {\n}\nfor x in &v {\n}\nfor (i, x) in v.iter().enumerate() {\n}\nwhile n > 0 {\n}\nloop {\n}\n'outer: for a in b {\n    break 'outer;\n}")
    assert t[1].startswith("Repeats once for each number from 0 up to but not including 3, calling the current one i.")
    assert t[3].startswith("Repeats once for each number from 0 up to and including 3")
    assert t[5].startswith("Repeats once for each item of v, borrowing them")
    assert t[7].startswith("Repeats once for each item of v, with its position: i is the position (counting from 0) and x is the item.")
    assert t[9] == "Keeps repeating while n is greater than 0."
    assert t[11].startswith("Repeats forever, until something inside leaves with `break`")
    assert "It is labeled 'outer" in t[13]
    assert t[14].startswith("Leaves the loop labeled 'outer right here.")


def test_if_else_if_let_while_let_and_if_as_an_expression():
    t = texts("if a > 1 {\n} else if b {\n} else {\n}\nif let Some(x) = o {\n}\nwhile let Some(y) = it.next() {\n}\nlet z = if c { 1 } else { 2 };")
    assert t[1] == "If a is greater than 1, does what follows."
    assert t[2] == "Otherwise, if b, does what follows."
    assert t[3] == "Otherwise, does what follows."
    assert t[5].startswith("If o fits the pattern a Some holding x, does what follows. The name x can be used inside.")
    assert t[7].startswith("Keeps repeating as long as the next item of it")
    assert t[9].startswith("Creates z (fixed: no `mut`), set to whichever of two values the `if` picks (the first when c).")


def test_types_traits_impls_derive_use_const_and_static():
    t = texts("#[derive(Debug, Clone)]\nstruct P {\n    x: i32,\n    pub name: String,\n}\nenum E {\n    A,\n    B(i32),\n    C { w: f64 },\n}\ntrait T {\n    fn f(&self) -> i32;\n}\nimpl T for P {\n}\nuse std::collections::HashMap;\nconst MAX: u32 = 10;\nstatic NAME: &str = \"x\";")
    assert t[1].startswith("Asks the compiler to write the standard code for Debug (so `{:?}` can show it), Clone (so `.clone()` works) on the type below.")
    assert t[2] == "Defines the struct P: a bundle of named fields, listed below."
    assert t[3] == "Has a field x: an i32 (a 32-bit whole number, can be negative)."
    assert t[4].startswith("Has a field name: a String (text it owns and can grow). It is `pub`")
    assert t[7] == "Is the variant A, which carries no data."
    assert t[8] == "Is the variant B, which carries an i32 (a 32-bit whole number, can be negative)."
    assert t[9].startswith("Is the variant C, which carries the named fields w (an f64")
    assert t[12].startswith("Declares the method f with no body")
    assert t[14] == "Says that P implements the trait T: the functions inside are the ones the trait asks for."
    assert t[16] == "Brings HashMap (from std::collections) into scope, so it can be written without the full path."
    assert t[17].startswith("Defines the constant MAX, a u32 (a whole number from 0 to 4294967295), set to 10. A constant can never change")
    assert t[18].startswith("Defines the static variable NAME, a &str (borrowed text)")


def test_method_chains_closures_casts_and_boxes():
    t = texts("let s: i32 = v.iter().map(|x| x * 2).filter(|x| *x > 3).sum::<i32>();\nlet f = move |a| a + 1;\nlet n = 300i32 as u8;\nlet b = Box::new(5);\nlet r = Rc::new(1);\nlet c = Rc::clone(&r);\nlet z = cell.borrow_mut();\nlet u = unsafe { *p };")
    assert "then going through its items one at a time (borrowed), then changing each item x into x times 2, then keeping only the items x for which what x points to is greater than 3, then adding them all up" in t[1]
    assert "a `move` closure (it takes ownership of the variables it uses) taking a that gives a plus 1" in t[2]
    assert "300i32 converted to a u8 (a whole number from 0 to 255) with `as`" in t[3] and K.FACTS["astrunc"] in t[3]
    assert "5 put in a Box (kept on the heap)" in t[4]
    assert "1 wrapped in an Rc (a value with several owners)" in t[5]
    assert "another owner of a reference to r (it shares the value, it does not copy it)" in t[6]
    assert "a changeable borrow of what is inside cell, checked while the program runs" in t[7]
    assert "the value of the unsafe block below" not in t[8]


def test_references_are_read_as_borrows():
    t = texts("let a = &x;\nlet b = &mut y;\nlet c = *a;")
    assert t[1] == "Creates a (fixed: no `mut`), set to a reference to x. " + K.FACTS["borrow"]
    assert t[2] == "Creates b (fixed: no `mut`), set to a mutable reference to y. " + K.FACTS["mutborrow"]
    assert t[3].startswith("Creates c (fixed: no `mut`), set to what a points to.")


def test_a_multi_line_chain_and_struct_literal_and_vec_are_read_line_by_line():
    t = texts("let s: u32 = items.iter()\n    .map(|x| x + 1)\n    .sum();\nlet p = Point {\n    x: 1,\n    y: 2,\n};\nlet v = vec![\n    1,\n    2,\n];")
    assert t[2].startswith("Carries on the chain above: changing each item x into x plus 1")
    assert t[3] == "Carries on the chain above: adding them all up."
    assert t[4] == "Creates p (fixed: no `mut`), set to a Point (the rest of it is on the next lines)."
    assert t[5] == "Sets the field x to 1." and t[6] == "Sets the field y to 2."
    assert t[8] == "Creates v (fixed: no `mut`), set to a Vec (a growable list) whose items are on the next lines."
    assert t[9] == "Is one of the items or arguments: 1."


def test_a_bare_tail_expression_is_the_blocks_value_and_a_semicolon_line_is_not():
    t = texts("fn f() -> i32 {\n    let a = 1;\n    a + 1\n}\nfn g() {\n    foo();\n}")
    assert t[3].startswith("Gives a plus 1 as the value of this block")
    assert t[6] == "Calls foo."


def test_return_break_continue_and_the_loop_value():
    t = texts("return 5;\nreturn;\nlet v = loop {\n    break 7;\n};\nfor i in a {\n    continue;\n}")
    assert t[1] == "Leaves this function now, giving back 5."
    assert t[2] == "Leaves this function now, giving back nothing."
    assert t[4].startswith("Leaves the loop, and the loop's value is 7 right here.")
    assert t[7] == "Skips the rest of this round of the loop and starts the next."


# every construct the brief names is read on its own, with no fallback row
CONSTRUCTS = [
    "fn f(a: i32, b: &str) -> bool {\n    true\n}", "fn g<T: Display>(x: T) {\n}", "fn h<'a>(x: &'a str) -> &'a str {\n    x\n}", "impl P {\n    fn a(&self) -> i32 {\n        1\n    }\n    fn b(&mut self) {\n    }\n    fn c(self) {\n    }\n}",
    "let x = 5;", "let mut y = 6;", "let z: f64 = 1.5;", "let (a, b) = (1, 2);", "let P { x, y } = p;", "let x = 5;\nlet x = x + 1;", "y = 7;", "y += 1;", "println!(\"{} {:?} {:>5} {:<5} {:^5} {:05} {:.2} {:x} {:#x} {:b} {name}\", a, b, c, d, e, f, g, h, i, j);",
    "print!(\"a\");", "eprintln!(\"a\");", "let s = format!(\"{}-{}\", a, b);", "let v = vec![1, 2, 3];", "let w = vec![0; 5];", "let t = v.iter().map(|x| x * 2).filter(|x| *x > 2).sum::<i32>();", "let u = v.clone();", "let n = x.to_string();",
    "let m = v.len();", "v.push(4);", "let a = o.unwrap();", "let b = o.unwrap_or(0);", "let c: Vec<_> = v.iter().collect::<Vec<_>>();", "let f = |x| x + 1;", "let g = move || 1;", "let r = &x;", "let q = &mut x;", "*q += 1;", "let d = *r;",
    "if a {\n} else if b {\n} else {\n}", "let z = if a { 1 } else { 2 };", "match n {\n    Some(x) => x,\n    None => 0,\n    1..=5 => 1,\n    k if k > 5 => 2,\n    _ => 3,\n}", "if let Some(x) = o {\n}", "while let Some(x) = it.next() {\n}",
    "let Some(x) = o else {\n    return;\n};", "loop {\n    break;\n}", "while a < 3 {\n    a += 1;\n}", "for x in 0..n {\n}", "for x in 0..=n {\n}", "for x in &v {\n}", "for (i, x) in v.iter().enumerate() {\n}", "'outer: for i in 0..3 {\n    for j in 0..3 {\n        break 'outer;\n    }\n}",
    "let v = loop {\n    break 3;\n};", "fn f() -> i32 {\n    return 1;\n}", "fn f() -> Result<i32, String> {\n    let n = g()?;\n    Ok(n)\n}", "struct P {\n    x: i32,\n}", "enum E {\n    A,\n    B(i32),\n}", "impl T for P {\n}", "trait T {\n    fn f(&self);\n}",
    "#[derive(Debug, Clone)]\nstruct P;", "use std::collections::HashMap;", "const N: usize = 3;", "static S: &str = \"s\";", "let c = n as u8;", "let b = Box::new(1);", "let r = Rc::new(1);", "let r2 = Rc::clone(&r);", "let c = cell.borrow_mut();", "let u = unsafe { *p };", "unsafe {\n    f();\n}",
    "fn f() -> i32 {\n    1\n}", "type T = u32;", "mod m {\n    pub fn f() {\n    }\n}", "let a = [1, 2, 3];", "let t = (1, \"a\");", "let o: Option<i32> = None;", "let r: Result<i32, String> = Ok(1);", "let s = &v[1..3];", "let l = 'a';", "let x = 1_000u32;",
    "let h = std::mem::swap(&mut a, &mut b);", "assert_eq!(a, b);", "panic!(\"no\");", "let p = Point { x: 1, y: 2 };",
]


def test_every_construct_the_brief_names_is_read_with_no_fallback_row():
    missed = []
    for code in CONSTRUCTS:
        rows, n, bad = K._read_rows(code)
        if bad or not rows:
            missed.append(code.split("\n")[0])
    assert not missed, missed


# (f) output notes

@needs_rustc
def test_the_output_note_is_what_the_real_program_printed():
    for code in ('println!("{}", 7 / 2);', 'let a = [3, 1, 2];\nprintln!("{} {}", a[0], a[2]);', 'fn main() {\n    println!("hi");\n}'):
        want = rust_values([code])[0]
        notes = explain(code, run=True)["output_notes"]
        printed = [n[len("It printed: "):] for n in notes if n.startswith("It printed: ")]
        assert "\n".join(printed).strip() == want, (code, notes, want)


@needs_rustc
def test_a_compile_error_is_an_error_note_with_the_snippets_own_line_and_no_temp_path():
    r = explain('let s = String::from("a");\nlet t = s;\nprintln!("{}", s);', run=True)
    assert r["error_note"] == "It does not compile: line 3: error[E0382]: borrow of moved value: `s`"
    assert "snippet" not in r["error_note"] and "\\" not in r["error_note"]
    assert len(r["lines"]) == 3
    r2 = explain("fn main() {\n    let x: i32 = \"a\";\n}", run=True)
    assert r2["error_note"].startswith("It does not compile: line 2: error[E0308]")


@needs_rustc
def test_a_panic_is_it_stopped_with_an_error_and_the_line():
    r = explain("let v: Vec<i32> = Vec::new();\nprintln!(\"{}\", v[3]);", run=True)
    assert r["error_note"] == "It stopped with an error: index out of bounds: the len is 0 but the index is 3 (line 2). A panic stops the program at once."
    r2 = explain('println!("before");\nlet n: Option<i32> = None;\nn.unwrap();', run=True)
    assert "It printed: before" in r2["output_notes"]
    assert r2["error_note"].startswith("It stopped with an error: called `Option::unwrap()` on a `None` value (line 3)")


@needs_rustc
def test_a_program_that_prints_nothing_gets_no_made_up_output_note():
    r = explain("let a = 5;", run=True)
    assert r["output_notes"] == [] and r["error_note"] is None


def test_a_missing_toolchain_or_a_timeout_is_a_note_and_never_an_exception(monkeypatch):
    from code_coach.gotchas import runner

    def boom(*a, **k):
        raise RuntimeError("rustc is not installed, so Rust cannot be run here.")

    monkeypatch.setattr(runner, "run_program", boom)
    r = explain("let a = 5;", run=True)
    assert r["ok"] and r["error_note"] is None and "was not run here" in r["output_notes"][0] and "rustc is not installed" in r["output_notes"][0]

    class Res:
        stdout = "1\n"
        stderr = ""
        returncode = -1
        timed_out = True
        compile_error = False
        ok = False

    monkeypatch.setattr(runner, "run_program", lambda *a, **k: Res())
    r2 = explain("loop {}", run=True)
    assert r2["output_notes"][0] == "It printed: 1" and "still running after 3 seconds" in r2["output_notes"][-1] and r2["error_note"] is None


def test_the_run_is_off_when_asked_not_to_run():
    r = explain('println!("a");', run=False)
    assert r["output_notes"] == [] and r["error_note"] is None


def test_the_summary_names_the_functions_defined():
    r = explain("fn double(x: i32) -> i32 { x * 2 }\nfn main() { println!(\"{}\", double(2)); }")
    assert r["summary"] == "This defines double. Here's what each line does:"
    assert explain("let x = 1;")["summary"] == "Here's what each line does:"


# (g) the one place a fragment becomes a program

PROGRAMS = ['let x = 1;\n\nprintln!("{}", x);\n', "fn main() {\n    println!(\"a\");\n}\n", "", "   \n", "let a = 1;  \n\n\n", "fn f() -> i32 { 3 }\nfn main(){ println!(\"{}\", f()); }", "struct P;\nimpl P {}\nprintln!(\"x\");", "fn  main (\n) {}\n"]


def test_wrap_rust_is_exactly_the_oracles_full_program():
    for code in PROGRAMS:
        p = wrap("rust", code)
        assert p.text == full_program(code), repr(code)
        assert p.runnable and not p.why_not
    assert wrap("rust", "let x = 1;").offset == 1
    assert wrap("rust", "fn main() {}").offset == 0


def test_wrap_leaves_the_other_languages_alone():
    assert wrap("c", "return 0;").text.startswith("#include <stdio.h>")
    assert wrap("sql", "SELECT 1;\n").text == "SELECT 1;"
    assert wrap("dart", "print(1);").text.startswith("void main()")
    with pytest.raises(ValueError):
        wrap("cobol", "x")
