"""The code magnet puzzles in Rust.

The same puzzle as the other languages. Rust adds its own reasons a line
cannot go just anywhere: a value moved into a function cannot be used after
the move, a `let` has to come before the first use, a `mut` borrow has to
end before the value is read again, and every `{` has its own `}`. Items -
functions, structs, impls - may sit in any order at the top level, so
those are free; the lines inside `main` are not.

The expected output beside each was typed by a person and is held to what
rustc's build prints by tests/test_magnets_rust.py.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m

FAMILY = "Rust"

RUST_MAGNETS: tuple[Magnet, ...] = (
    _m(
        id="magnet-rust-function",
        plan=(
            ("A function that squares a number", 3),
            ("Open main and use it", 3),
            ("Close main", 1),
        ),
        level=1,
        name="A function and main",
        family=FAMILY,
        language="rust",
        note=(
            "In Rust the last expression of a function, with no semicolon, is "
            "what it returns - `n * n` here. Functions can be declared in any "
            "order, so `square` could sit below main; what matters is that "
            "main's own lines run top to bottom, and that each `}` closes the "
            "right `{`."
        ),
        code=(
            "fn square(n: i32) -> i32 {\n"
            "    n * n\n"
            "}\n"
            "fn main() {\n"
            "    let side = 7;\n"
            "    println!(\"{}\", square(side));\n"
            "}"
        ),
        expect="49",
    ),
    _m(
        id="magnet-rust-mut-loop",
        plan=(
            ("Open main with a running total", 2),
            ("Add up the odd numbers to ten", 6),
            ("Report and close", 2),
        ),
        level=1,
        name="A mutable total in a loop",
        family=FAMILY,
        language="rust",
        note=(
            "Variables cannot change unless declared `mut`, so the total is "
            "`let mut total = 0`. `1..=10` includes 10. The `continue` skips "
            "the rest of the loop body for even numbers, so it has to come "
            "BEFORE the line that adds; after it, it would skip nothing."
        ),
        code=(
            "fn main() {\n"
            "    let mut total = 0;\n"
            "    for n in 1..=10 {\n"
            "        if n % 2 == 0 {\n"
            "            continue;\n"
            "        }\n"
            "        total += n;\n"
            "    }\n"
            "    println!(\"{}\", total);\n"
            "}"
        ),
        expect="25",
    ),
    _m(
        id="magnet-rust-struct-impl",
        plan=(
            ("A rectangle with two sides", 4),
            ("A method that measures it", 3),
            ("Make one and measure it", 4),
        ),
        level=2,
        name="A struct with a method",
        family=FAMILY,
        language="rust",
        note=(
            "Data goes in the `struct`, behaviour in an `impl` block for it. "
            "`&self` borrows the rectangle to read it without taking it. The "
            "struct and impl are items and can go in either order, but each "
            "needs its own closing brace, and main can only call `area` on a "
            "rect that has been made."
        ),
        code=(
            "struct Rect {\n"
            "    w: u32,\n"
            "    h: u32,\n"
            "}\n"
            "impl Rect {\n"
            "    fn area(&self) -> u32 { self.w * self.h }\n"
            "}\n"
            "fn main() {\n"
            "    let r = Rect { w: 3, h: 4 };\n"
            "    println!(\"{}x{} = {}\", r.w, r.h, r.area());\n"
            "}"
        ),
        expect="3x4 = 12",
    ),
    _m(
        id="magnet-rust-borrow",
        plan=(
            ("A function that reads a list without taking it", 3),
            ("Make a list, lend it, then keep using it", 6),
        ),
        level=2,
        name="Lending a value with &",
        family=FAMILY,
        language="rust",
        note=(
            "`total(&nums)` lends the vector: the function gets a reference "
            "and gives it back when it returns, so main can push to nums "
            "afterwards. Had it been `total(nums)`, the vector would have "
            "MOVED into the function and the push below would not compile. "
            "The push needs `mut` on nums, and it has to come after the "
            "first total to give 6 and then 10."
        ),
        code=(
            "fn total(list: &[i32]) -> i32 {\n"
            "    list.iter().sum()\n"
            "}\n"
            "fn main() {\n"
            "    let mut nums = vec![1, 2, 3];\n"
            "    println!(\"{}\", total(&nums));\n"
            "    nums.push(4);\n"
            "    println!(\"{}\", total(&nums));\n"
            "}"
        ),
        expect="6\n10",
    ),
    _m(
        id="magnet-rust-match-enum",
        plan=(
            ("Three kinds of coin", 1),
            ("What each one is worth", 7),
            ("Add up a handful", 4),
        ),
        level=3,
        name="An enum and a match",
        family=FAMILY,
        language="rust",
        note=(
            "`match` must cover every variant of the enum, or it does not "
            "compile - leave out a coin and Rust names the one you forgot. "
            "Each arm is `pattern => value`, and the whole match is the "
            "function's return value because it is the last expression with "
            "no semicolon."
        ),
        code=(
            "enum Coin { Penny, Nickel, Dime }\n"
            "fn cents(c: &Coin) -> u32 {\n"
            "    match c {\n"
            "        Coin::Penny => 1,\n"
            "        Coin::Nickel => 5,\n"
            "        Coin::Dime => 10,\n"
            "    }\n"
            "}\n"
            "fn main() {\n"
            "    let hand = [Coin::Dime, Coin::Penny, Coin::Dime];\n"
            "    println!(\"{}\", hand.iter().map(cents).sum::<u32>());\n"
            "}"
        ),
        expect="21",
    ),
    _m(
        id="magnet-rust-option",
        plan=(
            ("Find where a name is, if it is there", 3),
            ("Open main with a team", 2),
            ("Say what was found", 5),
        ),
        level=3,
        name="Option and if let",
        family=FAMILY,
        language="rust",
        note=(
            "`position` cannot promise a match, so it returns Option<usize>: "
            "Some(index) or None. `if let Some(i) = ...` runs its block only "
            "when there is a value, and names it i. The `else` belongs to the "
            "if let, so it has to follow that block's closing brace."
        ),
        code=(
            "fn find(names: &[&str], who: &str) -> Option<usize> {\n"
            "    names.iter().position(|n| *n == who)\n"
            "}\n"
            "fn main() {\n"
            "    let team = [\"ann\", \"bo\", \"cy\"];\n"
            "    if let Some(i) = find(&team, \"cy\") {\n"
            "        println!(\"cy is at {}\", i);\n"
            "    }\n"
            "    println!(\"{:?}\", find(&team, \"zed\"));\n"
            "}"
        ),
        expect="cy is at 2\nNone",
    ),
    _m(
        id="magnet-rust-result",
        plan=(
            ("A function that can fail", 4),
            ("Open main and try it twice", 2),
            ("Handle each outcome", 4),
            ("Close the loop and main", 2),
        ),
        level=4,
        name="Result and the ? operator",
        family=FAMILY,
        language="rust",
        note=(
            "`?` after the parse means: if this is an Err, return it from the "
            "function right now; if it is Ok, take the value out. So the "
            "doubling line only runs for good input. main matches on the "
            "Result to handle both cases - nothing is ignored by accident."
        ),
        code=(
            "fn double(text: &str) -> Result<i32, std::num::ParseIntError> {\n"
            "    let n: i32 = text.trim().parse()?;\n"
            "    Ok(n * 2)\n"
            "}\n"
            "fn main() {\n"
            "    for t in [\" 21 \", \"two\"] {\n"
            "        match double(t) {\n"
            "            Ok(v) => println!(\"ok {}\", v),\n"
            "            Err(e) => println!(\"error: {}\", e),\n"
            "        }\n"
            "    }\n"
            "}"
        ),
        expect="ok 42\nerror: invalid digit found in string",
    ),
    _m(
        id="magnet-rust-iterator-chain",
        plan=(
            ("Open main with some words", 2),
            ("Keep the long ones, made loud", 5),
            ("Show them and close", 2),
        ),
        level=4,
        name="An iterator chain",
        family=FAMILY,
        language="rust",
        note=(
            "`filter` and `map` only describe the work; `collect` runs it, "
            "in one pass, and the type on `loud` says what to collect into. "
            "The chain has to be in order - filter on length first, then "
            "upper-case - and the semicolon goes at the very end of the "
            "chain, after collect."
        ),
        code=(
            "fn main() {\n"
            "    let words = vec![\"sun\", \"moon\", \"stars\", \"sky\"];\n"
            "    let loud: Vec<String> = words\n"
            "        .iter()\n"
            "        .filter(|w| w.len() > 3)\n"
            "        .map(|w| w.to_uppercase())\n"
            "        .collect();\n"
            "    println!(\"{:?}\", loud);\n"
            "}"
        ),
        expect='["MOON", "STARS"]',
    ),
    _m(
        id="magnet-rust-trait",
        plan=(
            ("A behaviour any type can have", 1),
            ("Two types that have it", 8),
            ("Ask each one", 3),
        ),
        level=5,
        name="A trait with two implementations",
        family=FAMILY,
        language="rust",
        note=(
            "A trait names a behaviour; each `impl Speak for X` gives X its "
            "own version. `&dyn Speak` is a reference to anything that can "
            "speak, so the array can hold a Dog and a Cat side by side. All "
            "of these are items and could go in any order - the work is in "
            "matching each `}` to the `{` it closes."
        ),
        code=(
            "trait Speak { fn speak(&self) -> String; }\n"
            "struct Dog;\n"
            "struct Cat;\n"
            "impl Speak for Dog {\n"
            "    fn speak(&self) -> String { \"woof\".to_string() }\n"
            "}\n"
            "impl Speak for Cat {\n"
            "    fn speak(&self) -> String { \"meow\".to_string() }\n"
            "}\n"
            "fn main() {\n"
            "    for p in [&Dog as &dyn Speak, &Cat] { println!(\"{}\", p.speak()); }\n"
            "}"
        ),
        expect="woof\nmeow",
    ),
)
