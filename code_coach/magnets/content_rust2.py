"""A second set of Rust code magnets.

The first set (content_rust.py) covers a function, a mutable loop, a struct
with a method, borrowing, an enum match, Option, Result with `?`, an
iterator chain and a trait. These are ten other shapes: a function that
takes `&mut Vec`, a closure capturing a value, a struct with `new`, a
`while let` over a stack, an enum carrying data, an Option from `position`,
a trait default method, a Result function, a BTreeMap tally, and a closure
that changes what it captured.

Everything is deterministic and identical in a debug and an optimised build:
no arithmetic can overflow, and no HashMap is ever iterated or printed (a
BTreeMap keeps its keys sorted). The expected output beside each was worked
out by hand and is held to what rustc's build prints by
tests/test_magnets_rust2.py.
"""

from __future__ import annotations

from code_coach.magnets import Magnet, _m

FAMILY = "Rust"

RUST_MAGNETS_2: tuple[Magnet, ...] = (
    _m(
        id="magnet-rust2-mut-vec",
        plan=(
            ("A function that adds to a list", 4),
            ("Open main with a list", 2),
            ("Add, then show", 2),
            ("Close main", 1),
        ),
        level=1,
        name="A function taking &mut Vec",
        family=FAMILY,
        language="rust",
        note=(
            "`&mut Vec<i32>` lends the list out so the function may change "
            "it, and the caller says so with `&mut list`, which needs the "
            "list declared `mut`. The pushes happen in the order written, so "
            "2 lands before 4, and the print has to come after the call that "
            "adds, or it shows the list as it was."
        ),
        code=(
            "fn add_two(v: &mut Vec<i32>) {\n"
            "    v.push(2);\n"
            "    v.push(4);\n"
            "}\n"
            "fn main() {\n"
            "    let mut list = vec![1];\n"
            "    add_two(&mut list);\n"
            "    println!(\"{:?}\", list);\n"
            "}"
        ),
        expect="[1, 2, 4]",
    ),
    _m(
        id="magnet-rust2-closure-capture",
        plan=(
            ("Open main and pick a base", 2),
            ("A closure that uses it", 1),
            ("Call it twice", 2),
            ("Show and close", 2),
        ),
        level=1,
        name="A closure that captures a variable",
        family=FAMILY,
        language="rust",
        note=(
            "A closure can use variables from around it: `add` reads `base` "
            "without it being passed in. So `base` has to be declared above "
            "the closure that mentions it, and the closure above the calls "
            "to it. Calling it twice with different inputs gives 11 and 15 "
            "from the same code."
        ),
        code=(
            "fn main() {\n"
            "    let base = 10;\n"
            "    let add = |x: i32| x + base;\n"
            "    let a = add(1);\n"
            "    let b = add(5);\n"
            "    println!(\"{} {}\", a, b);\n"
            "}"
        ),
        expect="11 15",
    ),
    _m(
        id="magnet-rust2-struct-new",
        plan=(
            ("A struct holding a count", 1),
            ("Its impl, starting with new", 2),
            ("A method that bumps and returns", 4),
            ("Close the impl", 1),
            ("Open main and make one", 2),
            ("Bump twice and show", 1),
            ("Close main", 1),
        ),
        level=2,
        name="A struct with new and a method",
        family=FAMILY,
        language="rust",
        note=(
            "Items such as the struct and its impl can sit in any order at "
            "the top level; the order that matters is inside the bodies. In "
            "`bump` the `+= 1` statement has to come first and the bare "
            "`self.count` last, because the last expression with no "
            "semicolon is what the method returns. In main the counter must "
            "be made before it is bumped, and `c` is `mut` because `bump` "
            "changes it."
        ),
        code=(
            "struct Counter { count: u32 }\n"
            "impl Counter {\n"
            "    fn new() -> Counter { Counter { count: 0 } }\n"
            "    fn bump(&mut self) -> u32 {\n"
            "        self.count += 1;\n"
            "        self.count\n"
            "    }\n"
            "}\n"
            "fn main() {\n"
            "    let mut c = Counter::new();\n"
            "    println!(\"{} {}\", c.bump(), c.bump());\n"
            "}"
        ),
        expect="1 2",
    ),
    _m(
        id="magnet-rust2-while-let-pop",
        plan=(
            ("Open main with a stack and an empty list", 3),
            ("Pop until it is empty", 3),
            ("Show and close", 2),
        ),
        level=2,
        name="while let with pop",
        family=FAMILY,
        language="rust",
        note=(
            "`stack.pop()` takes the last item and gives Some(item), or None "
            "once the stack is empty, which is what ends `while let`. So the "
            "items come off 3, 2, 1: last in, first out, and the results "
            "land in `out` in that order. Print before the loop and the "
            "program still compiles but shows the list while it is empty."
        ),
        code=(
            "fn main() {\n"
            "    let mut stack = vec![1, 2, 3];\n"
            "    let mut out = Vec::new();\n"
            "    while let Some(top) = stack.pop() {\n"
            "        out.push(top * 10);\n"
            "    }\n"
            "    println!(\"{:?}\", out);\n"
            "}"
        ),
        expect="[30, 20, 10]",
    ),
    _m(
        id="magnet-rust2-enum-data",
        plan=(
            ("An enum with data", 1),
            ("Match on it to get an area", 6),
            ("Open main and make two shapes", 3),
            ("Show both and close", 2),
        ),
        level=3,
        name="An enum that carries data",
        family=FAMILY,
        language="rust",
        note=(
            "Each variant holds its own data, and `match` has an arm for "
            "each: a Circle(2) takes the first arm and gives 3 * 2 * 2 = 12, "
            "a Rect(3, 5) takes the second and gives 15. The match has to "
            "cover every variant or it does not compile. In main both "
            "shapes must be made before the line that prints them."
        ),
        code=(
            "enum Shape { Circle(u32), Rect(u32, u32) }\n"
            "fn area(s: &Shape) -> u32 {\n"
            "    match s {\n"
            "        Shape::Circle(r) => 3 * r * r,\n"
            "        Shape::Rect(w, h) => w * h,\n"
            "    }\n"
            "}\n"
            "fn main() {\n"
            "    let a = Shape::Circle(2);\n"
            "    let b = Shape::Rect(3, 5);\n"
            "    println!(\"{} {}\", area(&a), area(&b));\n"
            "}"
        ),
        expect="12 15",
    ),
    _m(
        id="magnet-rust2-option-if-let",
        plan=(
            ("A function that finds the first long word", 3),
            ("Open main with some words", 2),
            ("Use the answer if there is one", 3),
            ("Show the plain Option and close", 2),
        ),
        level=3,
        name="Option with if let",
        family=FAMILY,
        language="rust",
        note=(
            "`position` answers with an Option: Some(index) of the first "
            "match, or None. `if let Some(i) = ...` runs its block only "
            "when there is an answer, so the block can use `i` safely. "
            "\"bear\" is at index 2. The first two words are both short, so "
            "the second call gives None. The `if let` block prints before "
            "the plain `{:?}` print, and `words` is declared before both."
        ),
        code=(
            "fn first_long(words: &[&str]) -> Option<usize> {\n"
            "    words.iter().position(|w| w.len() > 3)\n"
            "}\n"
            "fn main() {\n"
            "    let words = [\"an\", \"ox\", \"bear\", \"wolf\"];\n"
            "    if let Some(i) = first_long(&words) {\n"
            "        println!(\"long word {} at {}\", words[i], i);\n"
            "    }\n"
            "    println!(\"{:?}\", first_long(&words[..2]));\n"
            "}"
        ),
        expect="long word bear at 2\nNone",
    ),
    _m(
        id="magnet-rust2-trait-default",
        plan=(
            ("A trait with a default method", 4),
            ("A type that has the trait", 1),
            ("Give it a name", 3),
            ("Open main and make one", 2),
            ("Say hello and close", 2),
        ),
        level=4,
        name="A trait default method and an impl",
        family=FAMILY,
        language="rust",
        note=(
            "The trait asks for `name` and supplies `hello` for free, built "
            "on `name`. `impl Speak for Dog` only has to write `name`; "
            "`hello` comes along. The trait, the struct and the impl are "
            "items, so they can sit in any order, but inside main the "
            "`let d` has to come before the line that calls `d.hello()`."
        ),
        code=(
            "trait Speak {\n"
            "    fn name(&self) -> String;\n"
            "    fn hello(&self) -> String { format!(\"hi, I am {}\", self.name()) }\n"
            "}\n"
            "struct Dog;\n"
            "impl Speak for Dog {\n"
            "    fn name(&self) -> String { String::from(\"Rex\") }\n"
            "}\n"
            "fn main() {\n"
            "    let d = Dog;\n"
            "    println!(\"{}\", d.hello());\n"
            "}"
        ),
        expect="hi, I am Rex",
    ),
    _m(
        id="magnet-rust2-result-question",
        plan=(
            ("A function that can fail", 5),
            ("Open main and show a good sum", 2),
            ("Match on a bad one", 4),
            ("Close main", 1),
        ),
        level=4,
        name="A Result function using ?",
        family=FAMILY,
        language="rust",
        note=(
            "Each `?` hands back the error right away if the parse failed, "
            "and otherwise unwraps the number, so `Ok(x + y)` at the end can "
            "only run when both worked, and it has to be the last line of "
            "the function, after `x` and `y` exist. \"4\" and \"5\" give "
            "Ok(9). \"z\" is not a digit, so `?` returns the error before "
            "any sum is made, and the match prints the error's message."
        ),
        code=(
            "fn parse_sum(a: &str, b: &str) -> Result<i32, std::num::ParseIntError> {\n"
            "    let x: i32 = a.parse()?;\n"
            "    let y: i32 = b.parse()?;\n"
            "    Ok(x + y)\n"
            "}\n"
            "fn main() {\n"
            "    println!(\"{:?}\", parse_sum(\"4\", \"5\"));\n"
            "    match parse_sum(\"4\", \"z\") {\n"
            "        Ok(n) => println!(\"sum {}\", n),\n"
            "        Err(e) => println!(\"error: {}\", e),\n"
            "    }\n"
            "}"
        ),
        expect="Ok(9)\nerror: invalid digit found in string",
    ),
    _m(
        id="magnet-rust2-btreemap-count",
        plan=(
            ("Bring in the sorted map", 1),
            ("Open main with the text and an empty map", 3),
            ("Count each word", 3),
            ("Print in sorted order and close", 4),
        ),
        level=5,
        name="Counting words in a BTreeMap",
        family=FAMILY,
        language="rust",
        note=(
            "A BTreeMap keeps its keys sorted, so the print is alphabetical "
            "whatever order the words arrived in: be, not, or, to. (A "
            "HashMap would print in an order that changes from run to run, "
            "which is why it is never printed here.) `entry(w).or_insert(0)` "
            "gives a place to add one. The count loop has to run before the "
            "print loop, or the map is empty when it is read."
        ),
        code=(
            "use std::collections::BTreeMap;\n"
            "fn main() {\n"
            "    let text = \"to be or not to be\";\n"
            "    let mut counts: BTreeMap<&str, u32> = BTreeMap::new();\n"
            "    for w in text.split(' ') {\n"
            "        *counts.entry(w).or_insert(0) += 1;\n"
            "    }\n"
            "    for (w, n) in &counts {\n"
            "        println!(\"{} {}\", w, n);\n"
            "    }\n"
            "}"
        ),
        expect="be 2\nnot 1\nor 1\nto 2",
    ),
    _m(
        id="magnet-rust2-closure-counter",
        plan=(
            ("Open main with a count", 2),
            ("A closure that bumps it", 4),
            ("Call it twice", 2),
            ("Show and close", 2),
        ),
        level=5,
        name="A closure that changes what it captured",
        family=FAMILY,
        language="rust",
        note=(
            "`bump` borrows `count` mutably, so the closure itself is "
            "declared `let mut`. Each call adds one and returns the new "
            "count, so the first call gives 1 and the second 2: the values "
            "go to `first` and `second` in the order the calls are written. "
            "The calls must come after the closure is made, and the print "
            "after both names exist."
        ),
        code=(
            "fn main() {\n"
            "    let mut count = 0;\n"
            "    let mut bump = || {\n"
            "        count += 1;\n"
            "        count\n"
            "    };\n"
            "    let first = bump();\n"
            "    let second = bump();\n"
            "    println!(\"{} {}\", first, second);\n"
            "}"
        ),
        expect="1 2",
    ),
)
