"""Rust errors: most of them from the compiler, a few from a panic.

Rust stops most mistakes before the program runs, and its messages are the
best of any language here once you can read them. The first line is the
whole sentence - `error[E0382]: borrow of moved value: `s`` - and the arrow
under it, ` --> file.rs:4:23`, is the line. The drawing below that labels
each line involved (where the value was moved, where it was used), which is
usually the explanation, and `rustc --explain E0382` prints a page about it.

A panic is the other kind: the program compiled and then hit something it
refuses to carry on past, an index out of range or an unwrap of None. Its
message is the line after `panicked at file.rs:L:C:`.

Every message and line was copied from what rustc printed, and
tests/test_errors_rust.py holds them to a real build.
"""

from __future__ import annotations

from code_coach.errors import Crash, _c

RUST = "Rust"


RUST_CRASHES: tuple[Crash, ...] = (
    _c(
        id="err-rs-typo",
        level=1,
        name="A name the compiler has never seen",
        family=RUST,
        language="rust",
        code=(
            "fn main() {\n"
            "    let total = 40 + 2;\n"
            "    println!(\"{}\", totl);\n"
            "}"
        ),
        message="error[E0425]: cannot find value `totl` in this scope",
        line=3,
        meaning="No variable called totl exists; the one made on line 2 is called total",
        decoys=(
            "println! cannot print a plain number with {} and needs a debug format like {:?} for it",
            "total goes out of scope at the end of line 2",
            "40 + 2 has to be written inside brackets to be stored",
        ),
        fix=(
            "'cannot find value ... in this scope' is Rust's NameError: it "
            "looked the name up and found nothing. Under the message the "
            "compiler usually adds 'help: a local variable with a similar "
            "name exists: total' - read the help lines, they are often the "
            "fix itself. Spell it as it was declared: totl becomes total."
        ),
    ),
    _c(
        id="err-rs-assign-twice",
        level=1,
        name="Changing a variable that is not mut",
        family=RUST,
        language="rust",
        code=(
            "fn main() {\n"
            "    let count = 0;\n"
            "    for _ in 0..3 {\n"
            "        count += 1;\n"
            "    }\n"
            "    println!(\"{}\", count);\n"
            "}"
        ),
        message="error[E0384]: cannot assign twice to immutable variable `count`",
        line=4,
        meaning="count was declared without mut, so Rust will not let it change",
        decoys=(
            "A for loop cannot change a variable made outside the loop",
            "count += 1 is not allowed in Rust; it has to be count = count + 1, which is the same thing written out in full",
            "The loop variable _ cannot be ignored like that",
        ),
        fix=(
            "Every variable in Rust is fixed unless you say otherwise, so a "
            "value cannot change behind your back. 'immutable variable' is "
            "the clue: declare it as `let mut count = 0;` and the += is "
            "fine. The compiler's help line suggests exactly that."
        ),
    ),
    _c(
        id="err-rs-mismatched",
        level=1,
        name="Text where a number goes",
        family=RUST,
        language="rust",
        code=(
            "fn main() {\n"
            "    let age: u32 = \"36\";\n"
            "    println!(\"{}\", age + 1);\n"
            "}"
        ),
        message="error[E0308]: mismatched types",
        line=2,
        meaning="age is declared as a number, u32, but \"36\" is text, a &str",
        decoys=(
            "u32 cannot hold a number as large as 36",
            "age + 1 cannot be printed with {}",
            "Variables with a type cannot be given a value on the same line",
        ),
        fix=(
            "'mismatched types' always comes with 'expected X, found Y' in "
            "the drawing underneath - here expected u32, found &str. Rust "
            "never turns text into a number for you. Write the number "
            "itself, `let age: u32 = 36;`, or parse the text: "
            "`\"36\".parse::<u32>().unwrap()`."
        ),
    ),
    _c(
        id="err-rs-moved",
        level=2,
        name="Using a value after it moved",
        family=RUST,
        language="rust",
        code=(
            "fn main() {\n"
            "    let s = String::from(\"hi\");\n"
            "    let t = s;\n"
            "    println!(\"{} {}\", s, t);\n"
            "}"
        ),
        message="error[E0382]: borrow of moved value: `s`",
        line=4,
        meaning="let t = s moved the String into t, so s no longer holds anything to print",
        decoys=(
            "A String cannot be printed together with another String in one println!, only one at a time",
            "s is out of scope because it was made on line 2",
            "t and s are two names for the same String, which Rust forbids",
        ),
        fix=(
            "A String owns its text, and `let t = s` hands ownership to t: "
            "there is still only one String, and s gives it up. Using s "
            "afterwards is the error, and the drawing marks both lines - "
            "'value moved here' and 'value borrowed here after move'. Copy "
            "it with `let t = s.clone();`, or borrow it with `let t = &s;`."
        ),
    ),
    _c(
        id="err-rs-not-mut-borrow",
        level=2,
        name="Pushing to a vector that is not mut",
        family=RUST,
        language="rust",
        code=(
            "fn main() {\n"
            "    let names = vec![\"ann\"];\n"
            "    names.push(\"bo\");\n"
            "    println!(\"{:?}\", names);\n"
            "}"
        ),
        message="error[E0596]: cannot borrow `names` as mutable, as it is not declared as mutable",
        line=3,
        meaning="push changes the vector, and names was not declared mut",
        decoys=(
            "A vector made with vec! has a fixed size and can never grow, so push does not exist for it",
            "push needs a String, not a &str",
            "names cannot be printed with {:?}",
        ),
        fix=(
            "push needs to change the vector, so it borrows it mutably - and "
            "you can only do that to a variable declared mut. Same rule as "
            "the assign-twice one, met through a method. `let mut names = "
            "vec![\"ann\"];` fixes it."
        ),
    ),
    _c(
        id="err-rs-index-panic",
        level=2,
        name="An index past the end",
        family=RUST,
        language="rust",
        code=(
            "fn main() {\n"
            "    let v = vec![10, 20, 30];\n"
            "    let i = v.len() + 2;\n"
            "    println!(\"{}\", v[i]);\n"
            "}"
        ),
        message="index out of bounds: the len is 3 but the index is 5",
        line=4,
        meaning="v has 3 items, so its indexes are 0 to 2, and 5 is past the end",
        decoys=(
            "v.len() is 2 because it counts from 0",
            "println! cannot print one item of a vector",
            "i has to be declared mut before it can be used as an index",
        ),
        fix=(
            "This one compiled - the compiler cannot know i's value - and "
            "then panicked when it ran. Rust checks every index and stops "
            "rather than read memory that is not the vector's. The message "
            "gives the length and the index, which is usually enough. Use "
            "`v.get(i)` when an index might be out of range: it returns None "
            "instead of panicking."
        ),
    ),
    _c(
        id="err-rs-unwrap-none",
        level=2,
        name="Unwrapping nothing",
        family=RUST,
        language="rust",
        code=(
            "fn main() {\n"
            "    let scores: Vec<u32> = Vec::new();\n"
            "    let best = scores.iter().max().unwrap();\n"
            "    println!(\"{}\", best);\n"
            "}"
        ),
        message="called `Option::unwrap()` on a `None` value",
        line=3,
        meaning="The vector was empty, so max() had nothing to return and gave None",
        decoys=(
            "max() only works on vectors of floats, and these scores are whole numbers, so it returns None",
            "scores has to be declared mut to be searched",
            "println! cannot print a u32 that came out of an iterator",
        ),
        fix=(
            "max() returns an Option because an empty list has no maximum. "
            "`unwrap()` means 'I am sure there is a value - panic if not', "
            "and here there was not. Say what to do instead: "
            "`.max().unwrap_or(&0)`, or `if let Some(best) = ...`."
        ),
    ),
    _c(
        id="err-rs-parse-unwrap",
        level=2,
        name="Unwrapping a failed parse",
        family=RUST,
        language="rust",
        code=(
            "fn main() {\n"
            "    let text = \"12a\";\n"
            "    let n: i32 = text.parse().unwrap();\n"
            "    println!(\"{}\", n * 2);\n"
            "}"
        ),
        message="called `Result::unwrap()` on an `Err` value: ParseIntError { kind: InvalidDigit }",
        line=3,
        meaning="\"12a\" is not a whole number, so parse gave an Err and unwrap panicked on it",
        decoys=(
            "i32 is too small to hold 12",
            "n * 2 overflowed the i32",
            "parse can only read text that is a single character long",
        ),
        fix=(
            "parse returns a Result, and the panic message prints the Err it "
            "found: InvalidDigit, the 'a'. unwrap on a Result is the same "
            "promise as on an Option, and broken the same way. Handle it: "
            "`match text.parse::<i32>() { Ok(n) => ..., Err(e) => ... }`, or "
            "return it to the caller with `?`."
        ),
    ),
    _c(
        id="err-rs-borrow-then-push",
        level=3,
        name="Holding a reference while the vector changes",
        family=RUST,
        language="rust",
        code=(
            "fn main() {\n"
            "    let mut v = vec![1, 2, 3];\n"
            "    let first = &v[0];\n"
            "    v.push(4);\n"
            "    println!(\"{}\", first);\n"
            "}"
        ),
        message="error[E0502]: cannot borrow `v` as mutable because it is also borrowed as immutable",
        line=4,
        meaning="first still points into v when push wants to change it, which could move v's items",
        decoys=(
            "v is not declared mut, so nothing can be pushed",
            "first is a copy of v[0], so after the push it would be out of date, and Rust refuses stale copies",
            "push cannot add a number that is larger than the others",
        ),
        fix=(
            "push may need more room and move every item somewhere new, "
            "which would leave first pointing at freed memory - the bug C "
            "lets you write. So while a shared borrow (first) is alive, no "
            "mutable borrow is allowed. Use first before the push, or copy "
            "the value out: `let first = v[0];`."
        ),
    ),
    _c(
        id="err-rs-non-exhaustive",
        level=3,
        name="A match that misses a case",
        family=RUST,
        language="rust",
        code=(
            "enum Dir { North, South, East, West }\n"
            "\n"
            "fn label(d: Dir) -> &'static str {\n"
            "    match d {\n"
            "        Dir::North => \"up\",\n"
            "        Dir::South => \"down\",\n"
            "        Dir::East => \"right\",\n"
            "    }\n"
            "}\n"
            "fn main() { println!(\"{}\", label(Dir::North)); }"
        ),
        message="error[E0004]: non-exhaustive patterns: `Dir::West` not covered",
        line=4,
        meaning="The match has no arm for West, and every possible Dir must be handled",
        decoys=(
            "A match can only have three arms",
            "label is only ever called with North, which is covered, so the missing West arm should not matter",
            "Enum values have to be written without the Dir:: in front",
        ),
        fix=(
            "A match must cover every value its input could have, so adding "
            "a variant to an enum makes the compiler point at every match "
            "that forgot it. It even names the missing one. Add "
            "`Dir::West => \"left\",` - or `_ => ...` for 'everything else', "
            "though that gives up the warning next time."
        ),
    ),
    _c(
        id="err-rs-divide-by-zero",
        level=3,
        name="An average of nothing",
        family=RUST,
        language="rust",
        code=(
            "fn average(nums: &[i32]) -> i32 {\n"
            "    let total: i32 = nums.iter().sum();\n"
            "    total / nums.len() as i32\n"
            "}\n"
            "fn main() {\n"
            "    println!(\"{}\", average(&[4, 6]));\n"
            "    println!(\"{}\", average(&[]));\n"
            "}"
        ),
        message="attempt to divide by zero",
        line=3,
        meaning="The second call's slice was empty, so len was 0 and the division was by 0",
        decoys=(
            "sum() cannot add up an empty slice",
            "as i32 turned the length into a negative number",
            "average can only be called once in a program",
        ),
        fix=(
            "Integer division by zero has no answer, so Rust panics rather "
            "than invent one, in debug and release builds alike. The line is "
            "inside average; the first call worked, so the formula is fine "
            "and the empty input is the problem. Decide what an empty "
            "average is: `if nums.is_empty() { return 0; }`."
        ),
    ),
    _c(
        id="err-rs-two-mut-borrows",
        level=4,
        name="Two mutable borrows at once",
        family=RUST,
        language="rust",
        code=(
            "fn main() {\n"
            "    let mut score = 10;\n"
            "    let a = &mut score;\n"
            "    let b = &mut score;\n"
            "    *a += 1;\n"
            "    *b += 1;\n"
            "    println!(\"{}\", score);\n"
            "}"
        ),
        message="error[E0499]: cannot borrow `score` as mutable more than once at a time",
        line=4,
        meaning="a is still a live mutable borrow of score when b tries to take another",
        decoys=(
            "score is not mut, so it cannot be borrowed with &mut",
            "*a += 1 is not how a value behind a reference is changed",
            "Two references cannot point at an i32",
        ),
        fix=(
            "Rust allows many readers or one writer, never two writers: with "
            "two &mut to one value, each could change it under the other. "
            "The borrow a lasts until its last use on line 5, so b on line 4 "
            "overlaps it. Finish with one before taking the next - move "
            "`*a += 1;` above the line that makes b."
        ),
    ),
    _c(
        id="err-rs-lifetime",
        level=5,
        name="Returning a reference from two",
        family=RUST,
        language="rust",
        code=(
            "fn longer(a: &str, b: &str) -> &str {\n"
            "    if a.len() >= b.len() { a } else { b }\n"
            "}\n"
            "fn main() {\n"
            "    println!(\"{}\", longer(\"apple\", \"fig\"));\n"
            "}"
        ),
        message="error[E0106]: missing lifetime specifier",
        line=1,
        meaning="The returned &str could come from a or from b, and Rust cannot tell how long it lives",
        decoys=(
            "Two &str parameters cannot be compared by length",
            "An if cannot be used as the last expression of a function",
            "The function has to return a String, never a &str",
        ),
        fix=(
            "A returned reference must not outlive what it points into, so "
            "Rust needs to know which input it came from. With one input it "
            "works that out; with two it asks. `fn longer<'a>(a: &'a str, "
            "b: &'a str) -> &'a str` says the result lives as long as both "
            "inputs do. The help line under the message writes this for you."
        ),
    ),
)
