"""The Rust cheat sheet.

Rust's difficulty is concentrated in a few places, and they are not the
syntax. Ownership, borrowing, and the fact that Option and Result are ordinary
enums you have to open rather than exceptions that happen to you — those are
where the time goes, so those get sections of their own rather than a line
each.

The rest is arranged the way the other sheets are: what you write in the first
minute, then outward.
"""

from __future__ import annotations

from code_coach.reference import Entry, Section, Sheet, register


def _e(code: str, note: str = "") -> Entry:
    return Entry(code=code, note=note)


SHEET = Sheet(
    language="rust",
    sections=(
        Section(
            "The first minute",
            "What you write before you have written anything.",
            (
                _e("fn main() {\n}", "no semicolon after a block"),
                _e('println!("hi");', "a macro; the ! is not decoration"),
                _e('println!("{}", n);', "{} takes the next argument"),
                _e("let count = 0;", "immutable by default"),
                _e("let mut count = 0;", "mut is how you get a variable"),
                _e("let n: i32 = 0;", "type after the name, when it needs saying"),
                _e("fn add(a: i32, b: i32) -> i32 {\n    a + b\n}", "last expression returns, no semicolon"),
                _e("if a == b {", "no brackets round the condition"),
                _e("for x in &items {", "& borrows, so items survives the loop"),
                _e("// a note to your later self", "and /// for documentation"),
            ),
        ),
        Section(
            "Printing",
            "It is all macros, and the format string is checked at compile time.",
            (
                _e('println!("{name} is {age}");', "names captured straight from scope"),
                _e('println!("{}, {}", a, b);', "positional, in order"),
                _e('println!("{0} {1} {0}", a, b);', "by index, to repeat one"),
                _e('println!("{:?}", items);', "debug: for anything derive(Debug)"),
                _e('println!("{:#?}", items);', "pretty debug, one field per line"),
                _e('println!("{:.2}", value);', "two decimal places"),
                _e('println!("{:>8}", name);', "right-align in eight; < and ^ too"),
                _e('print!("no newline");', "println! adds one, print! does not"),
                _e('eprintln!("oops");', "errors go to stderr"),
                _e('let s = format!("{}-{}", a, b);', "same syntax, returns a String"),
            ),
        ),
        Section(
            "Ownership",
            "One owner at a time. This is the part that is genuinely new.",
            (
                _e("let a = String::from(\"x\");\nlet b = a;", "a is moved; using a now is an error"),
                _e("let b = a.clone();", "an explicit copy, when you want one"),
                _e("let n = 5;\nlet m = n;", "numbers are Copy, so n is still usable"),
                _e("fn takes(s: String)", "takes ownership; the caller loses it"),
                _e("fn borrows(s: &String)", "borrows; the caller keeps it"),
                _e("fn borrows_mut(s: &mut String)", "borrows and may modify"),
                _e("fn takes_str(s: &str)", "prefer &str for a parameter over &String"),
                _e("&value", "make a reference"),
                _e("*reference", "read through one; usually automatic"),
                _e("value.to_string()", "&str to String; String::from does the same"),
            ),
        ),
        Section(
            "Borrowing rules",
            "Any number of readers, or one writer. Never both.",
            (
                _e("let a = &v;\nlet b = &v;", "two shared borrows: fine"),
                _e("let a = &mut v;\nlet b = &mut v;", "two mutable borrows: rejected"),
                _e("let a = &v;\nlet b = &mut v;", "shared and mutable at once: rejected"),
                _e("for x in &v {", "read the items"),
                _e("for x in &mut v {", "modify them; x is a &mut"),
                _e("for x in v {", "consumes v; you cannot use it afterwards"),
                _e("v.push(1);", "needs v to be mut, and no live borrows"),
                _e("let len = v.len();", "the borrow ends here, not at the brace"),
            ),
        ),
        Section(
            "Option",
            "Maybe a value. Not null, and the compiler makes you open it.",
            (
                _e("Option<i32>", "either Some(i32) or None"),
                _e("Some(5)\nNone", "the two cases"),
                _e("match maybe {\n    Some(n) => n,\n    None => 0,\n}", "handle both; the compiler checks you did"),
                _e("if let Some(n) = maybe {", "when only one case matters"),
                _e("maybe.unwrap_or(0)", "the value, or a default"),
                _e("maybe.unwrap_or_else(|| expensive())", "when the default costs something"),
                _e("maybe.unwrap()", "panics on None; fine in a test, rarely elsewhere"),
                _e("maybe.expect(\"should exist\")", "unwrap with a message worth reading"),
                _e("maybe.is_some()\nmaybe.is_none()", "just asking"),
                _e("maybe.map(|n| n * 2)", "act on the value if there is one"),
                _e("let n = maybe?;", "None returns early from an Option function"),
            ),
        ),
        Section(
            "Result and errors",
            "Success or failure as a value. Rust has no exceptions.",
            (
                _e("Result<i32, String>", "either Ok(i32) or Err(String)"),
                _e("Ok(5)\nErr(\"bad\".to_string())", "the two cases"),
                _e("match result {\n    Ok(n) => n,\n    Err(e) => return Err(e),\n}", "the long way"),
                _e("let n = result?;", "the short way: unwraps, or returns the error"),
                _e("fn run() -> Result<(), String> {", "? needs the function to return Result"),
                _e("result.unwrap_or(0)", "a default instead of an error"),
                _e("result.is_ok()\nresult.is_err()", "just asking"),
                _e('"42".parse::<i32>()', "returns a Result, not a number"),
                _e('let n: i32 = \"42\".parse().unwrap();', "the turbofish is unnecessary when the type is known"),
                _e("panic!(\"unrecoverable\");", "for bugs, not for expected failure"),
            ),
        ),
        Section(
            "Vec and slices",
            "The growable list, and the borrowed view of one.",
            (
                _e("let mut v: Vec<i32> = Vec::new();", "empty; the type cannot be inferred yet"),
                _e("let v = vec![1, 2, 3];", "the macro, when you have the values"),
                _e("let v = vec![0; 10];", "ten zeros"),
                _e("v.push(4);", "needs mut"),
                _e("v.pop()", "returns Option, because it may be empty"),
                _e("v.len()\nv.is_empty()", "how many, and whether any"),
                _e("v[0]", "panics if out of range"),
                _e("v.get(0)", "returns Option instead of panicking"),
                _e("&v[1..3]", "a slice: items 1 and 2"),
                _e("v.iter().sum::<i32>()", "the type is needed; sum cannot guess"),
                _e("v.contains(&3)", "note the &"),
                _e("v.sort();", "in place; sort_by for a comparator"),
            ),
        ),
        Section(
            "Iterators",
            "Lazy until something consumes them. Usually clearer than a loop.",
            (
                _e("v.iter()", "borrows each item as &T"),
                _e("v.into_iter()", "consumes v, yields each T"),
                _e("v.iter_mut()", "borrows each item mutably"),
                _e("v.iter().map(|n| n * 2)", "lazy: nothing has happened yet"),
                _e("v.iter().filter(|n| **n > 2)", "the closure gets a reference to a reference"),
                _e(".collect::<Vec<_>>()", "runs it; the _ is inferred"),
                _e("let out: Vec<i32> = v.iter().map(|n| n * 2).collect();", "or annotate the binding instead"),
                _e("v.iter().enumerate()", "yields (index, item)"),
                _e("v.iter().max()\nv.iter().min()", "return Option"),
                _e("v.iter().any(|n| *n > 2)", "and .all for every one"),
                _e("v.iter().find(|n| **n > 2)", "the first match, as an Option"),
                _e("v.iter().rev()", "backwards"),
                _e("v.iter().fold(0, |acc, n| acc + n)", "sum with a starting value"),
            ),
        ),
        Section(
            "Strings",
            "Two types, and the reason people trip over them.",
            (
                _e("&str", "a borrowed view; what a literal is"),
                _e("String", "owned and growable"),
                _e('let s = "hi";', "a &str, baked into the binary"),
                _e('let s = String::from("hi");', "owned, on the heap"),
                _e("s.len()", "BYTES, not characters"),
                _e("s.chars().count()", "characters, and it walks the string"),
                _e("s.push_str(\" more\");", "append to a String; needs mut"),
                _e("s.contains(\"hi\")", "substring test"),
                _e("s.split(',')", "an iterator, not a Vec"),
                _e("s.trim()", "returns a &str; does not modify"),
                _e("s.to_uppercase()", "returns a new String"),
                _e("s.replace(\"a\", \"b\")", "also a new String"),
                _e("&s[0..2]", "by BYTE index; panics mid-character"),
            ),
        ),
        Section(
            "Structs and enums",
            "Your own types, and the match that goes with them.",
            (
                _e("struct Point {\n    x: i32,\n    y: i32,\n}", "no semicolon after a braced struct"),
                _e("let p = Point { x: 1, y: 2 };", "every field, by name"),
                _e("#[derive(Debug, Clone, PartialEq)]", "the three you want almost always"),
                _e("impl Point {\n    fn new(x: i32) -> Self {\n        Self { x, y: 0 }\n    }\n}", "Self is the type; x means x: x"),
                _e("fn dist(&self) -> f64 {", "&self borrows; self consumes"),
                _e("enum Shape {\n    Circle(f64),\n    Rect(f64, f64),\n}", "variants can carry data"),
                _e("match shape {\n    Shape::Circle(r) => r,\n    Shape::Rect(w, h) => w * h,\n}", "every variant, or the compiler complains"),
                _e("_ => 0,", "the catch-all arm"),
                _e("struct Wrapper(i32);", "a tuple struct; field is .0"),
            ),
        ),
        Section(
            "Maps and sets",
            "In the standard library, but not in scope by default.",
            (
                _e("use std::collections::HashMap;", "the line everyone forgets"),
                _e("let mut m: HashMap<String, i32> = HashMap::new();", "annotate, or insert first"),
                _e('m.insert("a".to_string(), 1);', "returns the old value as an Option"),
                _e('m.get("a")', "an Option<&i32>, not an i32"),
                _e('m["a"]', "panics if missing; get is usually better"),
                _e('*m.entry("a".to_string()).or_insert(0) += 1;', "the counting idiom"),
                _e('m.contains_key("a")', "just asking"),
                _e("for (k, v) in &m {", "order is not stable; BTreeMap if you need it"),
                _e("use std::collections::HashSet;", "and HashSet::new()"),
                _e("set.insert(3);", "returns true if it was new"),
            ),
        ),
        Section(
            "Cargo and the rest",
            "The commands, and a few things you meet early.",
            (
                _e("cargo new name", "makes the folder and the manifest"),
                _e("cargo run", "builds and runs; --release to optimise"),
                _e("cargo test", "runs #[test] functions"),
                _e("cargo check", "type-checks without building: much faster"),
                _e("cargo clippy", "lints that teach you the idioms"),
                _e("cargo fmt", "formats; there is one style and no argument"),
                _e("const MAX: i32 = 100;", "SCREAMING_CASE, type required"),
                _e("let closure = |n: i32| n * 2;", "pipes, not brackets"),
                _e("as i32", "an explicit numeric cast, and it can truncate"),
                _e("#[test]\nfn it_works() {\n    assert_eq!(2 + 2, 4);\n}", "tests live beside the code"),
            ),
        ),
    ),
)

register(SHEET)
