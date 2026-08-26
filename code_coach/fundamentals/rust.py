"""Rust fundamentals — immutable by default, and the compiler means it."""

from __future__ import annotations

from code_coach.fundamentals.base import (
    FundamentalsBank,
    FundamentalsClass,
    Snippet,
    register,
)


def _s(code: str, tip: str, level: int = 1) -> Snippet:
    return Snippet(code=code, tip=tip, level=level)


_FOUNDATIONS = FundamentalsClass(
    id="foundations",
    name="Foundations",
    description="Bindings, ownership, and your first functions.",
    snippets=(
        _s('println!("Hello, world!");', "A macro, not a function — note the `!`."),
        _s("let name = \"Alex\";", "`let` binds. It can't be reassigned."),
        _s("let mut count = 0;", "`mut` is how you ask for a value that changes."),
        _s("let age: i32 = 30;", "The type goes after a colon, when you state it."),
        _s("let price: f64 = 4.99;", "f64 is the usual float."),
        _s("let is_ready = true;", "bool, inferred."),
        _s("let name = String::from(\"Alex\");", "An owned, growable string."),
        _s('println!("{}", count);', "`{}` is the placeholder."),
        _s('println!("Hi, {name}!");', "Newer Rust can name the variable inline."),
        _s("let nums = vec![1, 2, 3];", "`vec!` builds a growable Vec.", 2),
        _s("let mut nums: Vec<i32> = Vec::new();", "An empty Vec needs its type.", 2),
        _s("nums.push(4);", "Push needs the binding to be `mut`.", 2),
        _s('println!("{}", nums.len());', "`len()` is a method.", 2),
        _s("let first = nums[0];", "Index from zero. Out of range panics.", 2),
        _s("use std::collections::HashMap;", "Bring a collection into scope.", 2),
        _s("let mut counts = HashMap::new();", "Types get inferred from first use.", 2),
        _s(
            "let name = \"Alex\";\nprintln!(\"Hello, {name}!\");",
            "Bind, then use.",
            3,
        ),
        _s(
            "fn double(n: i32) -> i32 {\n    n * 2\n}",
            "`->` gives the return type. The last expression IS the return.",
            4,
        ),
        _s(
            "fn add(a: i32, b: i32) -> i32 {\n    a + b\n}",
            "No semicolon on the last line — that's what returns it.",
            4,
        ),
        _s(
            "fn greet(name: &str) {\n    println!(\"Hello, {name}!\");\n}",
            "`&str` borrows a string instead of taking ownership.",
            4,
        ),
        _s(
            "fn main() {\n    println!(\"Hello, world!\");\n}",
            "Every Rust program starts at main.",
            5,
        ),
        _s(
            "fn add(a: i32, b: i32) -> i32 {\n    a + b\n}\n\nfn main() {\n"
            "    println!(\"{}\", add(7, 12));\n}",
            "Order doesn't matter — Rust sees the whole file.",
            5,
        ),
        _s(
            "fn add(a: i32, b: i32) -> i32 {\n"
            "    a + b\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{}\", add(7, 12));\n"
            "}",
            "No semicolon on the last line: that is what makes it the return value.",
            5,
        ),
        _s(
            "fn greet(name: &str) -> String {\n"
            "    format!(\"Hello, {}!\", name)\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{}\", greet(\"Alex\"));\n"
            "}",
            "Take &str and return String: borrow the input, own the output.",
            5,
        ),
        _s(
            "fn average(nums: &[i32]) -> f64 {\n"
            "    let total: i32 = nums.iter().sum();\n"
            "    total as f64 / nums.len() as f64\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{}\", average(&[2, 4, 6]));\n"
            "}",
            "Rust never converts numbers for you; `as` is how you ask.",
            5,
        ),
        _s(
            "struct Point {\n"
            "    x: i32,\n"
            "    y: i32,\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    let p = Point { x: 1, y: 2 };\n"
            "    println!(\"{},{}\", p.x, p.y);\n"
            "}",
            "Struct fields are named at construction, so order does not matter.",
            5,
        ),
        _s(
            "fn first(items: &[i32]) -> Option<&i32> {\n"
            "    items.first()\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{:?}\", first(&[10, 20]));\n"
            "}",
            "Option is how Rust says the answer might not be there.",
            5,
        ),
        _s(
            "fn swap(pair: (i32, i32)) -> (i32, i32) {\n"
            "    let (a, b) = pair;\n"
            "    (b, a)\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{:?}\", swap((1, 2)));\n"
            "}",
            "A tuple returns several values without inventing a struct.",
            5,
        ),
    ),
)


_DECISIONS = FundamentalsClass(
    id="decisions",
    name="Decisions",
    description="Branching, and why `if` is an expression.",
    snippets=(
        _s("if age > 18 {", "No parentheses around the condition in Rust."),
        _s("if count == 0 {", "`==` compares."),
        _s("if name != \"Alex\" {", "`!=` is 'not equal to'."),
        _s("} else {", "The other branch."),
        _s("} else if score > 50 {", "Chain another test on."),
        _s("if a > 0 && b > 0 {", "`&&` needs both sides true.", 2),
        _s("if a == 0 || b == 0 {", "`||` needs only one.", 2),
        _s("if !found {", "`!` flips a bool.", 2),
        _s("let best = if a > b { a } else { b };",
           "`if` is an expression — it hands back a value.", 2),
        _s("match grade {", "`match` must cover every possibility.", 2),
        _s(
            "if score > 50 {\n    println!(\"pass\");\n}",
            "Braces hold what runs when it's true.",
            3,
        ),
        _s(
            "if score > 50 {\n    println!(\"pass\");\n} else {\n"
            "    println!(\"fail\");\n}",
            "One branch or the other.",
            4,
        ),
        _s(
            "match n {\n    0 => println!(\"zero\"),\n    1 => println!(\"one\"),\n"
            "    _ => println!(\"many\"),\n}",
            "`_` is the catch-all, and Rust insists you have one.",
            4,
        ),
        _s(
            "fn is_even(n: i32) -> bool {\n    n % 2 == 0\n}\n\nfn main() {\n"
            "    println!(\"{}\", is_even(4));\n}",
            "The comparison is the returned expression.",
            5,
        ),
        _s(
            "fn biggest(a: i32, b: i32) -> i32 {\n    if a > b {\n        a\n"
            "    } else {\n        b\n    }\n}\n\nfn main() {\n"
            "    println!(\"{}\", biggest(3, 9));\n}",
            "Each branch is an expression, so each one returns.",
            5,
        ),
        _s(
            "fn grade(score: i32) -> char {\n"
            "    if score >= 90 {\n"
            "        'A'\n"
            "    } else if score >= 80 {\n"
            "        'B'\n"
            "    } else {\n"
            "        'C'\n"
            "    }\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{}\", grade(85));\n"
            "}",
            "if is an expression, so every branch is a value of the same type.",
            5,
        ),
        _s(
            "fn sign(n: i32) -> &'static str {\n"
            "    match n {\n"
            "        n if n > 0 => \"positive\",\n"
            "        n if n < 0 => \"negative\",\n"
            "        _ => \"zero\",\n"
            "    }\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{}\", sign(-4));\n"
            "}",
            "A guard puts a condition on a match arm; _ catches the rest.",
            5,
        ),
        _s(
            "fn is_even(n: i32) -> bool {\n"
            "    n % 2 == 0\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{}\", is_even(7));\n"
            "}",
            "Return the comparison itself rather than true or false.",
            5,
        ),
        _s(
            "fn describe(value: Option<i32>) -> String {\n"
            "    match value {\n"
            "        Some(n) => format!(\"got {}\", n),\n"
            "        None => String::from(\"nothing\"),\n"
            "    }\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{}\", describe(None));\n"
            "}",
            "match on an Option must handle both arms, and the compiler checks.",
            5,
        ),
        _s(
            "fn or_default(name: Option<&str>) -> &str {\n"
            "    name.unwrap_or(\"stranger\")\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{}\", or_default(None));\n"
            "}",
            "unwrap_or supplies the fallback without a match block.",
            5,
        ),
        _s(
            "fn clamp_value(n: i32, low: i32, high: i32) -> i32 {\n"
            "    if n < low {\n"
            "        return low;\n"
            "    }\n"
            "    if n > high {\n"
            "        return high;\n"
            "    }\n"
            "    n\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{}\", clamp_value(15, 0, 10));\n"
            "}",
            "An early return needs the keyword; the final value does not.",
            5,
        ),
    ),
)


_LOOPS = FundamentalsClass(
    id="loops",
    name="Loops",
    description="Iterating, and borrowing while you do it.",
    snippets=(
        _s("for i in 0..5 {", "`0..5` is a range that stops before 5."),
        _s("for i in 0..=5 {", "`..=` includes the end."),
        _s("for n in &nums {", "`&` borrows, so the Vec survives the loop."),
        _s("while count > 0 {", "Repeat while the condition holds."),
        _s("count += 1;", "Rust has no `++`.", 2),
        _s("total += n;", "Shorthand for total = total + n.", 2),
        _s("break;", "Leave the loop immediately.", 2),
        _s("continue;", "Skip to the next turn.", 2),
        _s("loop {", "`loop` runs forever until you break.", 2),
        _s("for (i, n) in nums.iter().enumerate() {", "Index and value together.", 2),
        _s(
            "for n in &nums {\n    println!(\"{n}\");\n}",
            "The loop you'll write most often.",
            3,
        ),
        _s(
            "let mut total = 0;\nfor n in &nums {\n    total += n;\n}",
            "The accumulator must be `mut`.",
            4,
        ),
        _s(
            "let mut count = 3;\nwhile count > 0 {\n    println!(\"{count}\");\n"
            "    count -= 1;\n}",
            "Something inside must change, or it never ends.",
            4,
        ),
        _s(
            "fn sum(nums: &[i32]) -> i32 {\n    let mut total = 0;\n"
            "    for n in nums {\n        total += n;\n    }\n    total\n}\n\n"
            "fn main() {\n    let nums = vec![1, 2, 3];\n"
            "    println!(\"{}\", sum(&nums));\n}",
            "`&[i32]` is a slice — it borrows any list of numbers.",
            5,
        ),
        _s(
            "fn biggest(nums: &[i32]) -> i32 {\n    let mut best = nums[0];\n"
            "    for n in nums {\n        if *n > best {\n            best = *n;\n"
            "        }\n    }\n    best\n}\n\nfn main() {\n"
            "    println!(\"{}\", biggest(&[3, 9, 2]));\n}",
            "`*n` reads through the borrow to the number itself.",
            5,
        ),
        _s(
            "fn sum(nums: &[i32]) -> i32 {\n"
            "    let mut total = 0;\n"
            "    for n in nums {\n"
            "        total += n;\n"
            "    }\n"
            "    total\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{}\", sum(&[1, 2, 3, 4]));\n"
            "}",
            "mut is required to change a binding, even a running total.",
            5,
        ),
        _s(
            "fn biggest(nums: &[i32]) -> i32 {\n"
            "    let mut best = nums[0];\n"
            "    for &n in nums {\n"
            "        if n > best {\n"
            "            best = n;\n"
            "        }\n"
            "    }\n"
            "    best\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{}\", biggest(&[3, 9, 4]));\n"
            "}",
            "&n in the pattern copies the value out of the reference.",
            5,
        ),
        _s(
            "fn countdown(from: i32) -> Vec<i32> {\n"
            "    let mut out = Vec::new();\n"
            "    for i in (1..=from).rev() {\n"
            "        out.push(i);\n"
            "    }\n"
            "    out\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{:?}\", countdown(3));\n"
            "}",
            "..= includes the end; rev turns the range around.",
            5,
        ),
        _s(
            "fn doubled(nums: &[i32]) -> Vec<i32> {\n"
            "    nums.iter().map(|n| n * 2).collect()\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{:?}\", doubled(&[1, 2, 3]));\n"
            "}",
            "Iterators are lazy, so collect is what actually does the work.",
            5,
        ),
        _s(
            "fn evens(nums: &[i32]) -> Vec<i32> {\n"
            "    nums.iter().filter(|n| *n % 2 == 0).cloned().collect()\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{:?}\", evens(&[1, 2, 3, 4]));\n"
            "}",
            "filter hands the closure a reference, which is why it is dereferenced.",
            5,
        ),
        _s(
            "fn first_negative(nums: &[i32]) -> Option<i32> {\n"
            "    for &n in nums {\n"
            "        if n < 0 {\n"
            "            return Some(n);\n"
            "        }\n"
            "    }\n"
            "    None\n"
            "}\n"
            "\n"
            "fn main() {\n"
            "    println!(\"{:?}\", first_negative(&[3, 1, -2, 5]));\n"
            "}",
            "Option is the honest return type when there may be no answer.",
            5,
        ),
    ),
)


register(
    FundamentalsBank(language="rust", classes=(_FOUNDATIONS, _DECISIONS, _LOOPS))
)
