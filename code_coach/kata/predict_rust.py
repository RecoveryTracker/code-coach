"""Predict the output, in Rust.

Rust's surprises are mostly Rust being exact where other languages are
friendly: a String's len is bytes, not letters; `as` between integer types
cuts bits off rather than complaining; an iterator does nothing until
something asks it for values; and values are dropped in a set order you can
watch. Programs that would not compile are not puzzles here - the borrow
checker's refusals belong to the Errors mode - so every one of these
compiles cleanly and runs.

Every expected output was typed out first and then checked against rustc
(edition 2021) by tests/test_predict_rust.py, which also holds every program
to compiling without a single warning.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p

FAMILY = "Rust"


RUST_PUZZLES: tuple[Puzzle, ...] = (
    _p(
        id="predict-rust-int-division",
        level=1,
        language="rust",
        name="Dividing whole numbers, both signs",
        family=FAMILY,
        code=(
            "fn main() {\n"
            "    println!(\"{} {}\", 7 / 2, -7 / 2);\n"
            "    println!(\"{} {}\", -7 % 3, (-7_i32).rem_euclid(3));\n"
            "}"
        ),
        expect="3 -3\n-1 2",
        why=(
            "Integer division drops the fraction towards zero, so -7 / 2 is "
            "-3 (Python's // would say -4). `%` keeps the sign of the left "
            "side, so -7 % 3 is -1. When you want a remainder that is never "
            "negative - for wrapping round a list, say - `rem_euclid` gives "
            "it."
        ),
    ),
    _p(
        id="predict-rust-shadowing",
        level=1,
        language="rust",
        name="Shadowing a name",
        family=FAMILY,
        code=(
            "fn main() {\n"
            "    let x = 5;\n"
            "    let x = x * 2;\n"
            "    {\n"
            "        let x = 0;\n"
            "        println!(\"inner {}\", x);\n"
            "    }\n"
            "    println!(\"outer {}\", x);\n"
            "}"
        ),
        expect="inner 0\nouter 10",
        why=(
            "`let x` again makes a NEW variable that hides the old one - it is "
            "not changing x, which is why x needs no `mut`. The second let "
            "reads the old x to make the new one, 10. The x inside the braces "
            "hides it only until the closing brace; after that the 10 is back."
        ),
    ),
    _p(
        id="predict-rust-ranges",
        level=1,
        language="rust",
        name="Two kinds of range",
        family=FAMILY,
        code=(
            "fn main() {\n"
            "    let open: i32 = (1..5).sum();\n"
            "    let closed: i32 = (1..=5).sum();\n"
            "    println!(\"{} {}\", open, closed);\n"
            "    println!(\"{}\", (0..10).step_by(3).count());\n"
            "}"
        ),
        expect="10 15\n4",
        why=(
            "`1..5` stops BEFORE 5: 1 + 2 + 3 + 4 = 10. `1..=5` includes it: "
            "15. `step_by(3)` takes 0, 3, 6 and 9 - four numbers - and stops "
            "because 12 is past the end."
        ),
    ),
    _p(
        id="predict-rust-clone",
        level=1,
        language="rust",
        name="A clone is a separate vector",
        family=FAMILY,
        code=(
            "fn main() {\n"
            "    let a = vec![1, 2];\n"
            "    let mut b = a.clone();\n"
            "    b.push(3);\n"
            "    println!(\"{:?} {:?}\", a, b);\n"
            "}"
        ),
        expect="[1, 2] [1, 2, 3]",
        why=(
            "`clone` makes a whole new vector with its own copy of the items, "
            "so pushing to b leaves a alone. Without the clone, `let b = a` "
            "would MOVE the vector into b, and printing a afterwards would "
            "not compile at all - Rust never quietly gives you two names for "
            "one changeable vector."
        ),
    ),
    _p(
        id="predict-rust-string-len",
        level=2,
        language="rust",
        name="How long is a String",
        family=FAMILY,
        code=(
            "fn main() {\n"
            "    let word = String::from(\"café\");\n"
            "    println!(\"{} {}\", word.len(), word.chars().count());\n"
            "    println!(\"{}\", word.to_uppercase());\n"
            "}"
        ),
        expect="5 4\nCAFÉ",
        why=(
            "A String is UTF-8 bytes, and `len` counts bytes. 'c', 'a' and 'f' "
            "are one byte each, but 'é' takes two, so 5. `chars().count()` "
            "counts characters: 4. This is also why you cannot index a String "
            "with word[3] - a byte position might land in the middle of a "
            "letter."
        ),
    ),
    _p(
        id="predict-rust-float",
        level=2,
        language="rust",
        name="A tenth plus two tenths",
        family=FAMILY,
        code=(
            "fn main() {\n"
            "    let sum = 0.1 + 0.2;\n"
            "    println!(\"{}\", sum);\n"
            "    println!(\"{}\", sum == 0.3);\n"
            "    println!(\"{:.2}\", sum);\n"
            "}"
        ),
        expect="0.30000000000000004\nfalse\n0.30",
        why=(
            "0.1 and 0.2 have no exact binary form, so their sum is a hair "
            "over 0.3, and Rust prints the f64 exactly as it is. That makes "
            "`== 0.3` false. `{:.2}` rounds for display only - two places - "
            "without changing the value. Compare floats with a tolerance, not "
            "==."
        ),
    ),
    _p(
        id="predict-rust-option",
        level=2,
        language="rust",
        name="The first of nothing",
        family=FAMILY,
        code=(
            "fn main() {\n"
            "    let empty: Vec<i32> = Vec::new();\n"
            "    let full = vec![7, 8];\n"
            "    println!(\"{:?} {:?}\", empty.first(), full.first());\n"
            "    println!(\"{}\", empty.first().copied().unwrap_or(0));\n"
            "}"
        ),
        expect="None Some(7)\n0",
        why=(
            "`first` cannot promise there is a first item, so it returns an "
            "Option: None for an empty vector, Some(...) wrapping the item "
            "otherwise. There is no null to forget to check. `unwrap_or(0)` "
            "takes the value out, or 0 when there is none."
        ),
    ),
    _p(
        id="predict-rust-parse",
        level=2,
        language="rust",
        name="Parsing text that is not a number",
        family=FAMILY,
        code=(
            "fn main() {\n"
            "    let good: Result<i32, _> = \"42\".parse();\n"
            "    let bad: Result<i32, _> = \"4x2\".parse();\n"
            "    println!(\"{:?} {}\", good, bad.is_err());\n"
            "    println!(\"{}\", bad.unwrap_or(-1));\n"
            "}"
        ),
        expect="Ok(42) true\n-1",
        why=(
            "`parse` returns a Result: Ok with the number, or Err saying why "
            "it failed. \"4x2\" is not a whole number, so Err. Nothing "
            "crashes until you ask for the value carelessly; `unwrap_or` "
            "supplies -1 for the failure instead."
        ),
    ),
    _p(
        id="predict-rust-while-let",
        level=2,
        language="rust",
        name="Popping a stack until it is empty",
        family=FAMILY,
        code=(
            "fn main() {\n"
            "    let mut stack = vec![\"a\", \"b\", \"c\"];\n"
            "    while let Some(top) = stack.pop() {\n"
            "        print!(\"{} \", top);\n"
            "    }\n"
            "    println!(\"| left {}\", stack.len());\n"
            "}"
        ),
        expect="c b a | left 0",
        why=(
            "`pop` takes from the END, so the last one pushed comes out "
            "first. It returns Some(item) while there is one and None when "
            "the vector is empty, and `while let` keeps looping exactly as "
            "long as the pattern Some(top) matches."
        ),
    ),
    _p(
        id="predict-rust-lazy-iterator",
        level=3,
        language="rust",
        name="An iterator that has not started",
        family=FAMILY,
        code=(
            "fn main() {\n"
            "    let nums = vec![1, 2];\n"
            "    let doubled = nums.iter().map(|n| {\n"
            "        println!(\"doubling {}\", n);\n"
            "        n * 2\n"
            "    });\n"
            "    println!(\"made it\");\n"
            "    let out: Vec<i32> = doubled.collect();\n"
            "    println!(\"{:?}\", out);\n"
            "}"
        ),
        expect="made it\ndoubling 1\ndoubling 2\n[2, 4]",
        why=(
            "`map` does not run the closure; it builds an iterator that WILL "
            "run it when asked for values. Nothing asks until `collect`, so "
            "\"made it\" prints first. That laziness is what lets a chain of "
            "map and filter run in a single pass with no lists in between."
        ),
    ),
    _p(
        id="predict-rust-as-cast",
        level=3,
        language="rust",
        name="as between integer sizes",
        family=FAMILY,
        code=(
            "fn main() {\n"
            "    let big: i32 = 300;\n"
            "    let small = big as u8;\n"
            "    let neg = -1_i32 as u8;\n"
            "    println!(\"{} {}\", small, neg);\n"
            "    println!(\"{:?}\", u8::try_from(big).is_err());\n"
            "}"
        ),
        expect="44 255\ntrue",
        why=(
            "A u8 holds 0 to 255, and `as` does not check: it keeps the low 8 "
            "bits and drops the rest. 300 is 256 + 44, so 44. -1 is all ones "
            "in binary, which as 8 bits is 255. `u8::try_from` is the careful "
            "version: it returns an Err when the number does not fit."
        ),
    ),
    _p(
        id="predict-rust-dedup",
        level=3,
        language="rust",
        name="dedup removes neighbours only",
        family=FAMILY,
        code=(
            "fn main() {\n"
            "    let mut v = vec![1, 1, 2, 1, 3, 3];\n"
            "    v.dedup();\n"
            "    println!(\"{:?}\", v);\n"
            "    v.sort();\n"
            "    v.dedup();\n"
            "    println!(\"{:?}\", v);\n"
            "}"
        ),
        expect="[1, 2, 1, 3]\n[1, 2, 3]",
        why=(
            "`dedup` only removes a value when it repeats the one right "
            "before it, so the lone 1 after the 2 survives. Sort first and "
            "every duplicate ends up next to its twin, and then dedup really "
            "does leave one of each."
        ),
    ),
    _p(
        id="predict-rust-btreemap",
        level=3,
        language="rust",
        name="Counting into a BTreeMap",
        family=FAMILY,
        code=(
            "use std::collections::BTreeMap;\n"
            "\n"
            "fn main() {\n"
            "    let mut counts = BTreeMap::new();\n"
            "    for ch in \"banana\".chars() {\n"
            "        *counts.entry(ch).or_insert(0) += 1;\n"
            "    }\n"
            "    println!(\"{:?}\", counts);\n"
            "}"
        ),
        expect="{'a': 3, 'b': 1, 'n': 2}",
        why=(
            "`entry(ch).or_insert(0)` finds the count for a letter, putting 0 "
            "there first if it is new, and `*... += 1` adds to it in place. A "
            "BTreeMap keeps its keys sorted, so the letters print in order "
            "whatever order they were seen in. A HashMap would print them in "
            "an order that can change from run to run."
        ),
    ),
    _p(
        id="predict-rust-checked",
        level=4,
        language="rust",
        name="Three ways to go past 255",
        family=FAMILY,
        code=(
            "fn main() {\n"
            "    let x: u8 = 250;\n"
            "    println!(\"{:?}\", x.checked_add(10));\n"
            "    println!(\"{}\", x.saturating_add(10));\n"
            "    println!(\"{}\", x.wrapping_add(10));\n"
            "}"
        ),
        expect="None\n255\n4",
        why=(
            "250 + 10 does not fit in a u8, and Rust makes you say what you "
            "want. `checked_add` refuses: None. `saturating_add` stops at the "
            "top: 255. `wrapping_add` goes round like a clock: 260 - 256 = 4. "
            "A plain + would panic in a debug build, so the choice is never "
            "left to chance."
        ),
    ),
    _p(
        id="predict-rust-fnmut",
        level=4,
        language="rust",
        name="A closure that keeps count",
        family=FAMILY,
        code=(
            "fn main() {\n"
            "    let mut calls = 0;\n"
            "    let mut bump = || {\n"
            "        calls += 1;\n"
            "        calls * 10\n"
            "    };\n"
            "    let first = bump();\n"
            "    let second = bump();\n"
            "    println!(\"{} {} {}\", first, second, calls);\n"
            "}"
        ),
        expect="10 20 2",
        why=(
            "The closure borrows `calls` mutably and changes the real "
            "variable, so each call sees the last one's change - which is "
            "why `bump` itself has to be `mut`. Once bump is no longer used, "
            "the borrow ends and calls can be read again: 2."
        ),
    ),
    _p(
        id="predict-rust-drop-order",
        level=5,
        language="rust",
        name="Who is dropped first",
        family=FAMILY,
        code=(
            "struct Noisy(&'static str);\n"
            "\n"
            "impl Drop for Noisy {\n"
            "    fn drop(&mut self) {\n"
            "        println!(\"drop {}\", self.0);\n"
            "    }\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    let _a = Noisy(\"a\");\n"
            "    let _b = Noisy(\"b\");\n"
            "    drop(Noisy(\"c\"));\n"
            "    println!(\"end of main\");\n"
            "}"
        ),
        expect="drop c\nend of main\ndrop b\ndrop a",
        why=(
            "`drop(...)` drops a value right there, so c goes first. The rest "
            "live until the end of main and are then dropped in REVERSE order "
            "of creation - b before a - so anything made later, which might "
            "depend on the earlier ones, is cleaned up first."
        ),
    ),
)
