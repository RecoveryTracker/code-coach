"""Rust words, part 1: the core - variables and mutability, shadowing, expressions, control flow, functions, closures,
numbers (integers, floats, overflow, casts, conversions, number bases), characters and bytes, tuples and arrays,
printing and formatting, macros, panics, lints, attributes, modules and visibility.

Rust is the sixth glossary language (added 2026-11-26). Every example is the BODY of `fn main()` unless it mentions
`fn main(` (the Brain Drills convention); it is built by rustc debug and -O by tests/test_glossary.py and must print
exactly `out`. Every rule that a program can show is a check in tests/glossary_rust_checks.py."""

from __future__ import annotations

from .entry import Entry, rust

TERMS: list[Entry] = [
    *rust(
        "variable",
        "Variable",
        "A name for a value, made with let. In Rust a variable cannot be assigned to again unless you wrote let mut.",
        see=("mutability", "shadowing", "scope", "constant"),
        priority=30,
        aka=("variables", "let", "binding", "let binding", "name"),
        rules=(
            "let x = 5; makes x. Rust works out the type from the value and from how x is used later (i32 for a plain whole number); write it with let x: u8 = 5; when you want another.",
            "Assigning to a plain let variable a second time is a compile error. Add mut to allow it.",
            "A variable must hold a value before it is read; reading one that might still be unset is a compile error.",
            "A variable lives until the end of its block; then its value is dropped.",
        ),
        example=r"""
            let width = 4;
            let height: u32 = 3;
            let area = width * height;
            println!("{}", area);
        """,
        out=r"12",
    ),
    *rust(
        "mutability",
        "Mutability (mut)",
        "Whether a variable may be changed. Variables are fixed by default; let mut makes one you can assign to, and &mut lets a function change something you lend it.",
        see=("variable", "mutable-reference", "shadowing", "borrow-checker"),
        priority=60,
        aka=("mut", "mutable", "immutable", "immutability", "const-ness"),
        detect=(r"\blet\s+mut\b",),
        rules=(
            "let mut count = 0; lets you write count += 1; without mut the same line is a compile error.",
            "mut belongs to the variable, not to the value: moving a value into a plain let makes it fixed again, so a pushed-to Vec must live in a let mut.",
            "A function can change what it is given only if it takes &mut T and the caller passes &mut value; with &T it cannot, whatever the caller's variable is.",
            "Calling a method that takes &mut self needs the variable to be mut: v.push(1) on a plain let v is an error.",
        ),
        example=r"""
            let mut count = 0;
            count += 1;
            count += 2;
            println!("{}", count);
        """,
        out=r"3",
    ),
    *rust(
        "constant",
        "Constant (const, static)",
        "A value fixed for the whole program: const NAME: Type = value; or static for one fixed place in memory. The type must always be written, and the value must be known when compiling.",
        see=("variable", "mutability", "array"),
        priority=60,
        aka=("const", "static", "constants", "global", "global variable"),
        detect=(r"\b(?:const|static)\s+(?:mut\s+)?[A-Z_][A-Z0-9_]*\s*:",),
        rules=(
            "const N: usize = 3 * 4; works because 3 * 4 is known at compile time; the type after the colon is required.",
            "A const can be an array length: [0; N]. A plain let variable cannot, even if it never changes.",
            "const can never be mut; static mut exists but every read or write of it needs an unsafe block.",
            "By convention the names are in CAPITALS_WITH_UNDERSCORES.",
        ),
        example=r"""
            const SECONDS_PER_DAY: u32 = 24 * 60 * 60;
            static GREETING: &str = "hi";
            println!("{} {}", SECONDS_PER_DAY, GREETING);
        """,
        out=r"86400 hi",
    ),
    *rust(
        "shadowing",
        "Shadowing",
        "Writing let again with the same name makes a NEW variable that hides the old one from then on. The new one may have a different type, and it needs no mut.",
        see=("variable", "scope", "mutability"),
        priority=55,
        aka=("shadow", "shadowed", "redeclare", "rebinding", "variable shadowing"),
        detect=(r"\blet\s+(?:mut\s+)?(\w+)\b[^;]{0,80};\s{0,40}let\s+(?:mut\s+)?\1\b",),
        rules=(
            "let x = x + 1; does not change the old x; it makes a new x, and the old one is hidden.",
            "Inside a block, a shadow lasts only to the closing brace; after it the outer name is visible again with its old value.",
            "A shadow may change the type: let s = \"42\"; let s: i32 = s.parse().unwrap(); is fine. Plain assignment s = ... cannot change the type.",
            "Something that already captured the old variable (a closure) keeps seeing the old value.",
        ),
        example=r"""
            let x = 5;
            let x = x * 2;
            {
                let x = "inner";
                println!("{}", x);
            }
            println!("{}", x);
        """,
        out=r"""inner
10""",
    ),
    *rust(
        "expression",
        "Expression",
        "A piece of code that produces a value: 3 + 4, a function call, an if, a match or a whole block. A line ending in a semicolon is a statement and produces nothing.",
        see=("if-expression", "unit-type", "scope", "match"),
        priority=30,
        aka=("expressions", "statement", "statements", "semicolon", "block value", "evaluate"),
        rules=(
            "A block { ... } is an expression: its value is its last line, when that line has no semicolon.",
            "Adding a semicolon to the last line makes the block's value () instead: let y = { 1 + 2; }; gives y the value ().",
            "A function whose last line ends in a semicolon returns () and does not compile if it promised another type.",
            "if and match are expressions, so every branch must give the same type.",
        ),
        example=r"""
            let y = {
                let a = 3;
                a + 1
            };
            let z = if y > 3 { "big" } else { "small" };
            println!("{} {}", y, z);
        """,
        out=r"4 big",
    ),
    *rust(
        "if-expression",
        "if / else",
        "if condition { a } else { b } is an expression: it gives a or b. The condition must be a real bool, and needs no parentheses.",
        see=("boolean", "expression", "match", "if-let"),
        priority=45,
        aka=("if", "else", "else if", "conditional", "ternary", "branch", "condition"),
        detect=(r"\blet\s+\w+[^=\n]{0,30}=\s*if\b",),
        rules=(
            "The condition must be exactly bool: if 1 { ... } and if some_string { ... } are errors, because Rust never treats 0 or empty as false.",
            "Both branches must give the same type, and an if with no else has type (), so let x = if c { 1 }; does not compile.",
            "The braces are required: if c println!(\"a\"); is a syntax error.",
            "else if chains are tried from the top; the first true condition wins and the rest are skipped.",
        ),
        example=r"""
            let n = 7;
            let kind = if n % 2 == 0 { "even" } else { "odd" };
            println!("{} is {}", n, kind);
        """,
        out=r"7 is odd",
    ),
    *rust(
        "loop",
        "Loop",
        "Code that repeats. Rust has three kinds: for (over a sequence), while (as long as a condition holds) and loop (until a break).",
        see=("for-loop", "while-loop", "loop-keyword", "labeled-break"),
        priority=30,
        aka=("loops", "iteration", "repeat", "repetition"),
        rules=(
            "while checks its condition before every round, so its body may run zero times.",
            "break leaves the nearest loop; continue skips to the next round of it.",
            "A for or while loop is an expression of type (): it produces no useful value.",
        ),
        example=r"""
            let mut total = 0;
            for i in 1..=4 {
                total += i;
            }
            println!("{}", total);
        """,
        out=r"10",
    ),
    *rust(
        "while-loop",
        "while",
        "while condition { ... } repeats its body as long as the condition, a bool, is true. The condition is checked before every round.",
        see=("loop", "while-let", "for-loop", "boolean"),
        priority=45,
        aka=("while loop", "while-loop"),
        detect=(r"\bwhile\b(?!\s+let\b)",),
        rules=(
            "The condition is checked first, so a condition that starts false means the body never runs.",
            "The condition must be a bool: while 1 { ... } is a compile error.",
            "break leaves the loop early, exactly as in for.",
            "To take items out of something until it is empty, while let is neater than while with an is_empty check.",
        ),
        example=r"""
            let mut n = 27;
            let mut steps = 0;
            while n != 1 {
                n = if n % 2 == 0 { n / 2 } else { 3 * n + 1 };
                steps += 1;
            }
            println!("{}", steps);
        """,
        out=r"111",
    ),
    *rust(
        "for-loop",
        "for",
        "for item in things { ... } runs the body once for each item that things produces. It works on anything iterable: a range, a Vec, a slice, a string's chars.",
        see=("loop", "range", "iterator", "adaptor"),
        priority=55,
        aka=("for loop", "for-in", "for each", "foreach", "for in"),
        detect=(r"\bfor\s+[A-Za-z_(][\w, ()&_]{0,30}\s+in\b",),
        rules=(
            "for x in v moves the vector v into the loop, so v cannot be used afterwards; for x in &v only borrows it.",
            "0..3 gives 0, 1, 2 and 0..=3 gives 0, 1, 2, 3: the end is left out unless you write ..=.",
            "The loop variable is a new, fixed variable each round: for i in 0..3 { i += 1; } is an error unless you write mut i.",
            "for (i, x) in v.iter().enumerate() gives the position and the item together.",
        ),
        example=r"""
            let names = ["Ann", "Bo"];
            for (i, name) in names.iter().enumerate() {
                println!("{}: {}", i, name);
            }
            for n in (1..4).rev() {
                println!("{}", n);
            }
        """,
        out=r"""0: Ann
1: Bo
3
2
1""",
    ),
    *rust(
        "loop-keyword",
        "loop (keyword)",
        "loop { ... } repeats until a break. Because the only way out is break, break can carry a value out and the whole loop becomes an expression.",
        see=("loop", "labeled-break", "never-type", "while-loop"),
        priority=65,
        aka=("infinite loop", "break with value", "break value", "loop break"),
        detect=(r"\bloop\s*\{",),
        rules=(
            "break n; ends the loop and makes n the value of the whole loop expression.",
            "Only loop can break with a value; in a while or a for, break 5; is a compile error.",
            "A loop with no break never ends, so its type is ! and it fits where any type is expected: fn f() -> i32 { loop { return 3; } } is fine.",
            "continue jumps to the start of the next round.",
        ),
        example=r"""
            let mut n = 1;
            let first_big = loop {
                n *= 2;
                if n > 100 {
                    break n;
                }
            };
            println!("{}", first_big);
        """,
        out=r"128",
    ),
    *rust(
        "labeled-break",
        "Labeled break",
        "A label like 'outer: names a loop, so break 'outer or continue 'outer can leave or restart that loop from inside an inner one. A plain break only leaves the innermost loop.",
        see=("loop", "loop-keyword", "for-loop"),
        priority=70,
        aka=("label", "loop label", "break label", "continue label"),
        detect=(r"'[a-z_]\w*\s*:\s*(?:loop|while|for)\b|\b(?:break|continue)\s+'[a-z_]\w*\b(?!')",),
        rules=(
            "The label starts with a single quote and ends with a colon, written just before the loop: 'outer: for ...",
            "break 'outer; leaves the outer loop and everything inside it.",
            "continue 'outer; abandons the rest of the inner loop and the rest of the outer body, and starts the outer loop's next round.",
            "Without a label, break and continue act on the innermost loop only.",
        ),
        example=r"""
            let mut found = (0, 0);
            'outer: for a in 1..10 {
                for b in 1..10 {
                    if a * b == 42 {
                        found = (a, b);
                        break 'outer;
                    }
                }
            }
            println!("{:?}", found);
        """,
        out=r"(6, 7)",
    ),
    *rust(
        "function",
        "Function",
        "A named, reusable block of code: fn name(param: Type) -> ReturnType { ... }. Parameter and return types are always written, and the last expression, with no semicolon, is the result.",
        see=("expression", "closure", "unit-type", "method"),
        priority=40,
        aka=("functions", "fn", "subroutine", "procedure", "return", "return value", "parameter", "argument"),
        detect=(r"\bfn\s+[a-z_]\w*",),
        rules=(
            "The last expression, without a semicolon, is returned; return x; leaves early from anywhere.",
            "Every parameter needs a type: fn f(x) is an error. The return type goes after ->, and without one the function returns ().",
            "The call must give exactly the parameters the function lists: too many or too few arguments is a compile error.",
            "A function may be written below the code that calls it.",
        ),
        example=r"""
            fn area(w: u32, h: u32) -> u32 {
                w * h
            }
            fn main() {
                println!("{}", area(3, 4));
            }
        """,
        out=r"12",
    ),
    *rust(
        "scope",
        "Scope",
        "The part of the program where a name can be used: from its let to the closing brace of its block. When the block ends, the variable's value is dropped.",
        see=("variable", "shadowing", "drop", "ownership"),
        priority=30,
        aka=("block", "local variable", "local", "lexical scope", "out of scope"),
        rules=(
            "A name made inside { ... } is unknown after the closing brace.",
            "A name is not visible above its let: using it before it is declared is an error.",
            "Inner blocks can use the names of the blocks around them, but a function cannot see its caller's local variables.",
            "At the end of a scope its variables are dropped in the reverse order they were made.",
        ),
        example=r"""
            let outer = 1;
            {
                let inner = 2;
                println!("{} {}", outer, inner);
            }
            println!("{}", outer);
        """,
        out=r"""1 2
1""",
    ),
    *rust(
        "closure",
        "Closure",
        "An anonymous function written |parameters| body that can use variables from the place where it was made. It is a value: store it in a variable or pass it to another function.",
        see=("function", "iterator", "move", "adaptor"),
        priority=70,
        aka=("closures", "lambda", "anonymous function", "arrow function", "callback", "fn trait", "fnmut"),
        detect=(r"[(,=]\s*(?:move\s+)?(?:\|[^|\n]{0,40}\||\|\|)",),
        rules=(
            "|x| x + 1 puts the parameters between bars; their types are usually worked out, and the first use fixes them.",
            "A closure borrows what it uses from around it; move || ... makes it take ownership instead, so the original variable is gone afterwards.",
            "A closure that changes a captured variable must itself be declared mut before it can be called.",
            "A closure has no name of its own; two closures with the same code are still different types.",
        ),
        example=r"""
            let offset = 10;
            let add = |x: i32| x + offset;
            println!("{} {}", add(1), add(2));
        """,
        out=r"11 12",
    ),
    *rust(
        "integer",
        "Integer",
        "A whole-number type. Rust has signed ones (i8, i16, i32, i64, i128, isize) and unsigned ones (u8, u16, u32, u64, u128, usize); the number is the count of bits. A plain whole number defaults to i32.",
        see=("usize", "integer-overflow", "division", "as-cast", "floating-point"),
        priority=30,
        aka=("integers", "int", "i32", "u32", "i64", "u64", "i8", "i16", "u16", "i128", "u128", "signed", "unsigned", "whole number", "integer type"),
        rules=(
            "i is signed and u is unsigned: i8 holds -128 to 127 and u8 holds 0 to 255. An unsigned type cannot hold a negative number.",
            "Whole-number types never mix: adding an i32 to an i64 is a compile error; convert one first.",
            "A plain literal such as 5 is an i32 unless the code forces another type; 5u8 or 5_u8 fixes it, and 1_000_000 may contain underscores.",
            "i32::MAX and u8::MIN and friends give the limits of a type.",
        ),
        example=r"""
            let a: i32 = -7;
            let b: u8 = 255;
            let c = 1_000_000;
            println!("{} {} {}", a.abs(), b, c);
            println!("{} {}", i8::MAX, u16::MAX);
        """,
        out=r"""7 255 1000000
127 65535""",
    ),
    *rust(
        "usize",
        "usize and isize",
        "usize is the unsigned integer sized for the machine (64 bits on a 64-bit computer); Rust uses it for lengths and positions. isize is its signed twin.",
        see=("integer", "vector", "as-cast", "checked-arithmetic"),
        priority=55,
        aka=("isize", "index type", "size type", "pointer-sized integer"),
        detect=(r"\b(?:usize|isize)\b",),
        rules=(
            "len() returns a usize, and an index must be a usize: v[i] with an i32 i is a compile error.",
            "Convert with as: v[n as usize]. A negative i32 turns into a huge usize.",
            "Being unsigned, a usize cannot go below zero: 0 - 1 panics in a debug build, so use checked_sub or saturating_sub when it might.",
            "Its size depends on the machine: 8 bytes on a 64-bit one.",
        ),
        example=r"""
            let v = vec![10, 20, 30];
            let i: usize = 2;
            println!("{} {}", v[i], v.len());
            println!("{}", std::mem::size_of::<usize>());
        """,
        out=r"""30 3
8""",
    ),
    *rust(
        "division",
        "Integer division and remainder",
        "On integers, / throws the fraction away (7 / 2 is 3, and -7 / 2 is -3) and % gives the remainder, which takes the sign of the left number. Integer division by zero panics.",
        see=("integer", "floating-point", "panic", "as-cast"),
        priority=40,
        aka=("divide", "modulo", "remainder", "integer division", "truncation", "rem_euclid", "%", "floor division"),
        rules=(
            "7 / 2 is 3: the result is cut toward zero, so -7 / 2 is -3, not -4.",
            "7 % 3 is 1 but -7 % 3 is -1: the remainder has the sign of the left number. (-7).rem_euclid(3) is 2, never negative.",
            "Both sides must have the same type: 7 / 2.0 is a compile error; write 7.0 / 2.0 for 3.5.",
            "An integer divided by zero panics at run time; a float divided by zero is inf (or NaN for 0.0 / 0.0).",
        ),
        example=r"""
            println!("{} {} {}", 7 / 2, -7 / 2, 7.0 / 2.0);
            println!("{} {}", 7 % 3, -7 % 3);
        """,
        out=r"""3 -3 3.5
1 -1""",
    ),
    *rust(
        "floating-point",
        "Floating-point (f64)",
        "A number with a fractional part: f64 (the default, 64 bits) or f32. They are approximate, so 0.1 + 0.2 is not exactly 0.3, and they can also be inf or NaN.",
        see=("integer", "division", "as-cast", "sorting"),
        priority=50,
        aka=("float", "f64", "f32", "double", "floating point", "decimal", "nan", "inf", "real number"),
        detect=(r"\bf(?:32|64)\b",),
        rules=(
            "A literal with a decimal point is an f64: 3.0 is a float but 3 is an integer, and let x: f64 = 3; is a compile error.",
            "0.1 + 0.2 == 0.3 is false: compare floats with a small tolerance, not with ==.",
            "{} prints 1.0 as 1 while {:?} prints it as 1.0.",
            "NaN is not equal to anything, itself included; ask x.is_nan(). Because of NaN, floats cannot use sort() or max(); use sort_by with partial_cmp.",
        ),
        example=r"""
            let x = 0.1 + 0.2;
            println!("{}", x);
            println!("{}", x == 0.3);
            println!("{:.2} {}", x, 2.0_f64.sqrt() > 1.41);
        """,
        out=r"""0.30000000000000004
false
0.30 true""",
    ),
    *rust(
        "boolean",
        "bool",
        "The type with two values, true and false. Conditions must be a real bool; Rust never treats 0, an empty string or None as false. && and || stop early, and ! flips.",
        see=("if-expression", "while-loop", "expression"),
        priority=30,
        aka=("bool", "booleans", "true", "false", "truthy", "falsy", "logical operator", "&&"),
        rules=(
            "Only a bool can be a condition: let n = 1; if n { ... } is a compile error.",
            "a && b does not run b when a is false, and a || b does not run b when a is true. The single & and | always run both sides.",
            "true as i32 is 1 and false as i32 is 0, but a number cannot be cast to bool: 1 as bool is an error.",
            "false < true: bools can be compared.",
        ),
        example=r"""
            let n = 15;
            let fizz = n % 3 == 0;
            let buzz = n % 5 == 0;
            println!("{} {} {}", fizz && buzz, fizz || false, !buzz);
        """,
        out=r"true true false",
    ),
    *rust(
        "char",
        "char",
        "A single Unicode character in single quotes: 'a', '7', '\\u{e9}'. A char is 4 bytes; it is not a u8 and not a one-letter string.",
        see=("byte", "string", "as-cast", "boolean"),
        priority=45,
        aka=("character", "characters", "chars", "unicode", "codepoint", "letter", "ascii"),
        detect=(r"\bchar\b|'_'",),
        rules=(
            "'a' with single quotes is a char; \"a\" with double quotes is a string, and let c: char = \"a\"; is an error.",
            "A char takes 4 bytes and a u8 takes 1: size_of::<char>() is 4.",
            "'a' as u32 is 97. Only a u8 can be cast back with as (97u8 as char); other integers need char::from_u32.",
            "c.to_digit(10) turns '7' into Some(7) and 'x' into None; c.is_alphabetic(), c.is_ascii_digit() and c.to_ascii_uppercase() test and convert.",
        ),
        example=r"""
            let c = 'a';
            println!("{} {}", c as u32, (c as u8 + 1) as char);
            println!("{} {}", '\u{e9}'.len_utf8(), c.is_alphabetic());
        """,
        out=r"""97 b
2 true""",
    ),
    *rust(
        "byte",
        "Byte (u8)",
        "One 8-bit value, type u8 (0 to 255). b'a' is the byte for a, and a string is stored as UTF-8 bytes, so len() counts bytes, not characters.",
        see=("char", "string", "integer", "as-cast"),
        priority=55,
        aka=("bytes", "u8", "as_bytes", "byte string", "utf-8", "utf8", "octet"),
        detect=(r"\bu8\b|\.(?:as_bytes|bytes)\(\)", r"raw:\bb'"),
        rules=(
            "b'a' is the u8 97, while 'a' is a char; b'a' + 1 is 98.",
            "s.len() is the number of bytes: a string with the character \\u{e9} counts it as 2, so \"h\\u{e9}llo\".len() is 6.",
            "A string cannot be indexed by position: s[0] is a compile error. Use s.as_bytes()[0] for a byte or s.chars().nth(0) for a character.",
            "300 as u8 does not fail; it keeps the low 8 bits and gives 44.",
        ),
        example=r"""
            let s = "hi!";
            let bytes = s.as_bytes();
            println!("{:?} {}", bytes, b'a');
            println!("{} {}", "\u{e9}".len(), "\u{e9}".chars().count());
        """,
        out=r"""[104, 105, 33] 97
2 1""",
    ),
    *rust(
        "tuple",
        "Tuple",
        "A fixed group of values that may have different types, written (1, \"a\", 2.5). Reach a part with .0, .1, or unpack it with let (x, y) = t;.",
        see=("array", "unit-type", "pattern", "struct"),
        priority=50,
        aka=("tuples", "pair", "triple", "destructuring tuple"),
        detect=(r"[A-Za-z_)\]]\.\d\b", r"\blet\s+\([^)\n]{0,40}\)\s*="),
        rules=(
            "A part is reached by position, t.0 and t.1; t[0] is an error.",
            "The type is the list of the part types: (i32, &str) is a different type from (i32, i32), and the size can never change.",
            "Tuples of the same type compare part by part from the left: (1, 2) < (1, 3) is true.",
            "A one-part tuple needs a trailing comma: (5,) is a tuple, (5) is just 5.",
        ),
        example=r"""
            let t = (3, "three", 3.0);
            let (n, name, _) = t;
            println!("{} {} {}", t.0, n, name);
        """,
        out=r"3 3 three",
    ),
    *rust(
        "array",
        "Array",
        "A fixed-length list of values of one type: [1, 2, 3], or [0; 5] for five zeros. The length is part of the type ([i32; 3]) and never changes; use a Vec when it must grow.",
        see=("vector", "slice", "tuple", "constant"),
        priority=55,
        aka=("arrays", "fixed array", "fixed-size array", "[t; n]", "array literal"),
        detect=(r"\[\s*[\w.\-]+\s*;\s*[\w]+\s*\]",),
        rules=(
            "[T; N] has its length in the type: [i32; 3] and [i32; 4] are different types, and [1, 2, 3, 4] does not fit [i32; 3].",
            "A position past the end panics at run time (a constant position past the end is refused when compiling).",
            "An array of Copy values is itself Copy: let b = a; copies it, and changing b leaves a alone.",
            "a.len(), a.iter() and slicing &a[1..] work as they do on a Vec.",
        ),
        example=r"""
            let a = [1, 2, 3];
            let zeros = [0; 4];
            println!("{} {:?} {}", a.len(), zeros, a[1]);
        """,
        out=r"3 [0, 0, 0, 0] 2",
    ),
    *rust(
        "unit-type",
        "Unit type ()",
        "The type with exactly one value, written (). It is what an expression with no result produces: a function without -> returns it, and so does a block that ends with a semicolon.",
        see=("expression", "function", "never-type", "result"),
        priority=50,
        aka=("unit", "()", "empty tuple", "void", "nothing"),
        detect=(r"\bOk\(\(\)\)|->\s*\(\s*\)|\bResult<\(\)",),
        rules=(
            "A function with no -> returns (): let u = nothing(); is allowed, and u == () is true.",
            "Ok(()) is a Result that succeeded with nothing to report; Result<(), E> is the type of such functions.",
            "() takes zero bytes of memory.",
            "A for loop, an assignment and a block ending in a semicolon all have the value ().",
        ),
        example=r"""
            fn nothing() {}
            fn main() {
                let u = nothing();
                println!("{:?} {}", u, u == ());
            }
        """,
        out=r"() true",
    ),
    *rust(
        "never-type",
        "Never type (!)",
        "The type of an expression that never finishes normally: panic!, return, break, continue and a function declared -> !. Having no value, it fits wherever any type is expected.",
        see=("panic", "loop-keyword", "match", "unit-type"),
        priority=60,
        aka=("never", "diverging", "diverging function", "!", "bottom type"),
        detect=(r"->\s*!(?!=)",),
        rules=(
            "panic! has type !, so it may sit in one branch of an if or match whose other branches give an i32.",
            "continue and break have type ! too, which is why Err(_) => continue is allowed in a match that gives a number.",
            "A function declared -> ! may not return: fn f() -> ! { 1 } is a compile error; it must panic, loop for ever or exit.",
            "The never type is why a loop with no break can stand where a value is expected.",
        ),
        example=r"""
            let n: i32 = if true { 5 } else { panic!("never reached") };
            let s: &str = match n { 5 => "five", _ => unreachable!() };
            println!("{} {}", n, s);
        """,
        out=r"5 five",
    ),
    *rust(
        "integer-overflow",
        "Integer overflow",
        "A result too big (or too small) for the integer's type. A debug build panics on it; a release build (-O) silently wraps around. So choose wrapping_, checked_ or saturating_ on purpose.",
        see=("wrapping-arithmetic", "checked-arithmetic", "saturating-arithmetic", "lint", "panic"),
        priority=60,
        aka=("overflow", "underflow", "wrap around", "wraparound", "overflowing", "overflowing_add"),
        detect=(r"\.overflowing_\w+\(",),
        rules=(
            "In a debug build 255u8 + 1 panics with 'attempt to add with overflow'; with -O it wraps to 0. The two builds disagree, so never depend on either.",
            "A constant that visibly overflows is refused when compiling: let x: u8 = 255 + 1; and let x: u8 = 256; are errors (deny lints).",
            "checked_add gives None on overflow, wrapping_add wraps, saturating_add stops at the limit and overflowing_add gives (wrapped, true).",
            "Unsigned subtraction overflows below zero: 5u32.checked_sub(6) is None.",
        ),
        example=r"""
            let big: u8 = 250;
            println!("{:?}", big.checked_add(10));
            println!("{}", big.wrapping_add(10));
            println!("{}", big.saturating_add(10));
            println!("{:?}", big.overflowing_add(10));
        """,
        out=r"""None
4
255
(4, true)""",
    ),
    *rust(
        "wrapping-arithmetic",
        "Wrapping arithmetic",
        "wrapping_add, wrapping_sub and wrapping_mul do the sum modulo the type's size: they go around from the top to the bottom and never panic, in debug and release alike.",
        see=("integer-overflow", "checked-arithmetic", "saturating-arithmetic"),
        priority=70,
        aka=("wrapping", "wrapping_add", "wrapping_sub", "wrapping_mul", "modular arithmetic", "std::num::wrapping"),
        detect=(r"\.wrapping_\w+\(|\bWrapping\b",),
        rules=(
            "250u8.wrapping_add(10) is 4, because 260 - 256 is 4; 0u8.wrapping_sub(1) is 255.",
            "A signed type wraps to the other end: i8::MAX.wrapping_add(1) is -128.",
            "200u8.wrapping_mul(2) is 144: the product 400 loses the top bits.",
            "std::num::Wrapping(x) is a number type whose + - * always wrap: Wrapping(250u8) + Wrapping(10u8) displays as 4.",
        ),
        example=r"""
            println!("{} {} {}", 250u8.wrapping_add(10), 0u8.wrapping_sub(1), i8::MAX.wrapping_add(1));
        """,
        out=r"4 255 -128",
    ),
    *rust(
        "checked-arithmetic",
        "Checked arithmetic",
        "checked_add, checked_sub, checked_mul and checked_div return an Option: Some(result), or None when the answer would overflow (or divide by zero). Nothing panics.",
        see=("integer-overflow", "option", "unwrap", "wrapping-arithmetic"),
        priority=70,
        aka=("checked", "checked_add", "checked_sub", "checked_mul", "checked_div", "checked_pow"),
        detect=(r"\.checked_\w+\(",),
        rules=(
            "i32::MAX.checked_add(1) is None and 5.checked_add(1) is Some(6); you must handle the Option before using the number.",
            "checked_div(0) is None instead of the panic that / 0 would give.",
            "On unsigned numbers checked_sub catches going below zero: 3u32.checked_sub(5) is None.",
            ".checked_add(10).unwrap_or(255) is a quick way to saturate; checked_pow(31) on 2u32 is Some(2147483648) but checked_pow(32) is None.",
        ),
        example=r"""
            let a: i32 = i32::MAX;
            println!("{:?} {:?}", a.checked_add(1), a.checked_sub(1));
            println!("{:?}", 10u32.checked_div(0));
        """,
        out=r"""None Some(2147483646)
None""",
    ),
    *rust(
        "saturating-arithmetic",
        "Saturating arithmetic",
        "saturating_add, saturating_sub and saturating_mul stop at the smallest or largest number of the type instead of wrapping or panicking.",
        see=("integer-overflow", "wrapping-arithmetic", "checked-arithmetic"),
        priority=70,
        aka=("saturating", "saturating_add", "saturating_sub", "saturating_mul", "clamp", "saturate"),
        detect=(r"\.saturating_\w+\(",),
        rules=(
            "250u8.saturating_add(10) is 255, the top of u8.",
            "5u8.saturating_sub(10) is 0: the safe way to subtract unsigned numbers without going below zero.",
            "i8::MIN.saturating_sub(1) stays -128, and 100i8.saturating_mul(2) is 127.",
            "Debug and release builds give the same answer.",
        ),
        example=r"""
            println!("{} {} {}", 250u8.saturating_add(10), 5u8.saturating_sub(10), i8::MIN.saturating_sub(1));
        """,
        out=r"255 0 -128",
    ),
    *rust(
        "as-cast",
        "as (cast)",
        "expr as Type converts a number to another type. A cast never fails or panics: a too-big integer keeps only its low bits, and a float is cut toward zero and clamped to the range.",
        see=("type-conversion", "integer", "floating-point", "char"),
        priority=65,
        aka=("cast", "casting", "casts", "as", "typecast", "type cast", "truncation cast"),
        detect=(r"\bas\s+(?:[iu](?:8|16|32|64|128|size)|f32|f64|char|bool)\b",),
        rules=(
            "Integers keep their low bits: 300i32 as u8 is 44, and -1i32 as u32 is 4294967295.",
            "A float becomes an integer by cutting toward zero and clamping: 3.99 as i32 is 3, -5.7 as i32 is -5, 1e10 as i32 is 2147483647 and NaN as i32 is 0.",
            "An integer to a float can lose precision: 16777217i32 as f32 prints 16777216.",
            "as works between numbers only: \"5\" as i32 is an error (use parse), and 1 as bool is an error. Only a u8 can be cast to char.",
        ),
        example=r"""
            println!("{} {} {}", 300i32 as u8, -1i32 as u32, 3.99_f64 as i32);
            println!("{} {}", -5.7_f64 as i32, 1e10_f64 as i32);
            println!("{}", 65u8 as char);
        """,
        out=r"""44 4294967295 3
-5 2147483647
A""",
    ),
    *rust(
        "type-conversion",
        "Type conversion (From, TryFrom, parse)",
        "Moving a value from one type to another on purpose. From and Into do safe conversions, TryFrom returns a Result when the value might not fit, and parse turns text into a number.",
        see=("as-cast", "result", "integer", "string-from"),
        priority=55,
        aka=("conversion", "convert", "from", "into", "tryfrom", "try_from", "parse", "from_str", "type coercion", "coercion"),
        detect=(r"\.parse\b|\.try_into\(|\b(?:TryFrom|From)\b|\b\w+::(?:try_)?from\(",),
        rules=(
            "Rust never converts between number types by itself: a 32-bit and a 64-bit number cannot be added until one is converted.",
            "i64::from(5i32) exists because it can never fail; i32::from(5i64) does not exist, because it could.",
            "u8::try_from(300i32) is Err and u8::try_from(200i32) is Ok(200).",
            "\"12\".parse::<i32>() is Ok(12) and \"x\".parse::<i32>() is an Err; it also rejects spaces, so \" 5\" fails.",
        ),
        example=r"""
            let a = i64::from(5i32);
            let b: Result<u8, _> = u8::try_from(300i32);
            let c: i32 = "42".parse().unwrap();
            println!("{} {} {}", a, b.is_err(), c + 1);
        """,
        out=r"5 true 43",
    ),
    *rust(
        "hexadecimal",
        "Hexadecimal and other bases",
        "Base 16, written with 0x (0xFF is 255); 0b is binary and 0o is octal. {:x}, {:X}, {:b} and {:o} print a number in those bases, and {:#x} adds the 0x.",
        see=("padding", "formatting", "integer", "byte"),
        priority=55,
        aka=("hex", "binary", "octal", "base 16", "radix", "0x", "from_str_radix", "{:x}", "{:b}", "base"),
        detect=(r"raw:\b0[xbo][0-9a-fA-F_]+\b", r"raw:\{[^{}\n]{0,12}:[^{}\n]{0,6}[xXbo]\}", r"\bfrom_str_radix\b"),
        rules=(
            "0xFF is 255, 0b101 is 5 and 0o17 is 15.",
            "{:x} prints lower-case hex, {:X} upper-case, {:#x} with the 0x in front, and {:#010b} pads with zeros after the 0b to a total width of 10.",
            "A negative number prints as its bits (two's complement): {:x} of -1i8 is ff.",
            "i64::from_str_radix(\"ff\", 16) reads text in a base; the text must not have a 0x prefix.",
        ),
        example=r"""
            let n = 255;
            println!("{:x} {:X} {:#x} {:b}", n, n, n, n);
            println!("{:08b} {:04x}", 5, 255);
            println!("{}", i64::from_str_radix("ff", 16).unwrap());
        """,
        out=r"""ff FF 0xff 11111111
00000101 00ff
255""",
    ),
    *rust(
        "formatting",
        "Formatting (format!)",
        "format!(...) builds a String from a template in which each {} is replaced by an argument; println! uses the same templates. {name} and {0} pick an argument by name or position, and {x} can name a variable directly.",
        see=("println", "display", "debug-format", "padding"),
        priority=60,
        aka=("format", "format!", "string formatting", "format string", "placeholder", "interpolation", "write!", "string interpolation"),
        detect=(r"\bformat!\s*\(|\bwrite!\s*\(|\bwriteln!\s*\(",),
        rules=(
            "The number of {} placeholders must equal the number of arguments, or it does not compile.",
            "{{ and }} print literal braces: println!(\"{{}} {}\", 5) prints {} 5.",
            "format! returns a String and prints nothing; println! prints and returns ().",
            "{x} works for a plain variable name only; {x + 1} is an error. Every argument must support the placeholder's trait: {} needs Display, so a Vec cannot use {}.",
        ),
        example=r"""
            let name = "Ana";
            let age = 30;
            let s = format!("{} is {}", name, age);
            println!("{s} / {0}-{0} / {a}", age, a = name);
        """,
        out=r"Ana is 30 / 30-30 / Ana",
    ),
    *rust(
        "println",
        "println! and print!",
        "println! writes its text and a newline to standard output; print! does the same with no newline. eprintln! writes to the error stream. The first argument must be a string literal.",
        see=("formatting", "macro", "debug-format", "display"),
        priority=45,
        aka=("print", "print!", "eprintln!", "eprintln", "output", "write to screen", "stdout", "console"),
        detect=(r"\b(?:println|print|eprintln|eprint)!",),
        rules=(
            "println!() with nothing inside prints just a newline.",
            "The template must be a literal: let s = \"hi\"; println!(s); is an error; write println!(\"{}\", s);.",
            "eprintln! goes to stderr, which is separate from stdout.",
            "Arguments are only borrowed, so a String can be printed twice.",
        ),
        example=r"""
            print!("a");
            print!("b");
            println!();
            println!("{}-{}", 1, 2);
        """,
        out=r"""ab
1-2""",
    ),
    *rust(
        "debug-format",
        "Debug ({:?})",
        "{:?} prints a value in developer form, such as Some(3), [1, 2] or \"text\" with its quotes. Most types have it once they #[derive(Debug)]; {:#?} spreads it over several lines.",
        see=("display", "derive", "formatting", "option"),
        priority=60,
        aka=("debug", "{:?}", "{:#?}", "dbg!", "dbg", "pretty print", "debug trait", "debug print"),
        detect=(r"raw:\{[^{}\n]{0,15}\?\}", r"\bdbg!\s*\("),
        rules=(
            "Your own struct needs #[derive(Debug)] before {:?} works; without it the program does not compile.",
            "Strings show their quotes and escapes: {:?} of \"a<newline>b\" prints \"a\\nb\" with the quotes.",
            "{:#?} (pretty debug) puts each part on its own line, indented.",
            "dbg!(expr) prints to stderr and gives the value back, so let x = dbg!(2 + 3); sets x to 5.",
        ),
        example=r"""
            #[derive(Debug)]
            struct P { x: i32, y: i32 }
            fn main() {
                let p = P { x: 1, y: -2 };
                println!("{:?} {:?}", p, Some("hi"));
                println!("{:?}", vec![(1, 'a')]);
            }
        """,
        out=r"""P { x: 1, y: -2 } Some("hi")
[(1, 'a')]""",
    ),
    *rust(
        "display",
        "Display ({})",
        "The trait behind {}: how a type looks to a person. Numbers and strings have it; your own type gets it only if you impl fmt::Display for it, which also gives you .to_string().",
        see=("debug-format", "trait", "impl", "formatting"),
        priority=65,
        aka=("{}", "to_string", "fmt", "impl display", "fmt::display", "tostring"),
        detect=(r"\bfmt::Display\b|\bimpl\b[^{\n]{0,40}\bDisplay\b|\.to_string\(\)",),
        rules=(
            "A struct cannot be printed with {} until it implements Display; the fmt function writes with write!(f, ...).",
            "Implementing Display gives .to_string() for free.",
            "Display cannot be derived: #[derive(Display)] does not exist.",
            "Vec and Option have no Display, only Debug: println!(\"{}\", Some(1)) is an error.",
        ),
        example=r"""
            use std::fmt;
            struct Point { x: i32, y: i32 }
            impl fmt::Display for Point {
                fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
                    write!(f, "({}, {})", self.x, self.y)
                }
            }
            fn main() {
                let p = Point { x: 1, y: 2 };
                println!("{} {}", p, p.to_string().len());
            }
        """,
        out=r"(1, 2) 6",
    ),
    *rust(
        "padding",
        "Padding, width and precision",
        "A number after the colon in {:5} is a minimum width; < left, > right and ^ centre it, and a fill character can come before: {:*^9}. {:.2} sets the decimals and {:05} pads with zeros.",
        see=("formatting", "hexadecimal", "floating-point", "string"),
        priority=55,
        aka=("width", "alignment", "pad", "precision", "zero pad", "left pad", "justify", "align", "fill", "decimal places"),
        detect=(r"raw:\{[^{}\n]{0,12}:[^{}\n]{0,3}[<>^0]?\d+[^{}\n]{0,8}\}", r"raw:\{[^{}\n]{0,12}:[^{}\n]{0,3}\.\d+\}"),
        rules=(
            "Numbers line up on the right by default and text on the left: {:5} of 42 is three spaces then 42, of \"ab\" is ab then three spaces.",
            "{:05} pads numbers with zeros after the sign: -42 becomes -0042.",
            "The width is a minimum; a longer value is never cut: {:2} of 12345 prints 12345.",
            "On a string, .3 means at most 3 characters: {:.3} of \"abcdef\" prints abc. The width may come from an argument: {:>w$} with w = 4.",
        ),
        example=r"""
            println!("[{:5}] [{:<5}] [{:>5}] [{:^5}]", 42, 42, 42, 42);
            println!("[{:5}] [{:*^7}] [{:05}]", "ab", "ab", 42);
            println!("{:.2} {:8.3}|{:+}", 3.14159, 2.5, 7);
        """,
        out=r"""[   42] [42   ] [   42] [ 42  ]
[ab   ] [**ab***] [00042]
3.14    2.500|+7""",
    ),
    *rust(
        "macro",
        "Macro (name!)",
        "Code that writes code. A name ending in ! (println!, vec!, format!, assert_eq!) is a macro call, expanded before the program is compiled; a macro can take arguments in ways a function cannot.",
        see=("println", "formatting", "attribute", "panic"),
        priority=40,
        aka=("macros", "macro_rules", "macro_rules!", "declarative macro", "assert_eq!", "assert!"),
        detect=(r"\b(?:vec|assert|assert_eq|assert_ne|matches|todo|unreachable|unimplemented)!|\bmacro_rules!",),
        rules=(
            "A macro call always has the !: println(\"x\") is an error because println is not a function.",
            "A macro accepts any number or shape of arguments: vec![1, 2, 3] and vec![0; 3] are both fine.",
            "assert_eq!(a, b) panics when a != b, and shows both values.",
            "macro_rules! square { ($x:expr) => { $x * $x }; } keeps what it is given as one expression, so square!(3 + 1) is 16, not 7.",
        ),
        example=r"""
            macro_rules! square {
                ($x:expr) => { $x * $x };
            }
            fn main() {
                println!("{} {:?}", square!(3 + 1), vec![1; 2]);
            }
        """,
        out=r"16 [1, 1]",
    ),
    *rust(
        "panic",
        "Panic",
        "Rust's stop-with-an-error. The program prints a message and unwinds, then stops that thread. panic! does it by hand; it also happens on a bad index, an integer divided by zero, unwrap on None and a failed assert.",
        see=("unwrap", "result", "integer-overflow", "error-handling"),
        priority=60,
        aka=("panics", "panic!", "crash", "abort", "unwind", "unwinding", "index out of bounds", "runtime error", "exception"),
        detect=(r"\bpanic!|\bassert(?:_eq|_ne)?!|\btodo!|\bunreachable!",),
        rules=(
            "v[9] on a three-item Vec panics with 'index out of bounds'; v.get(9) gives None instead and never panics.",
            "unwrap() on None or Err, an integer division by zero, and a failed assert! each panic.",
            "panic!(\"bad {}\", 1) takes a message like println!.",
            "Unwinding still runs the drop of every variable on the way out, so cleanup code runs; std::panic::catch_unwind can catch a panic.",
        ),
        example=r"""
            let v = vec![1, 2, 3];
            println!("{:?} {:?}", v.get(1), v.get(9));
            println!("{:?}", 5_i32.checked_div(0));
        """,
        out=r"""Some(2) None
None""",
    ),
    *rust(
        "lint",
        "Lint (deny, warn, allow)",
        "A rustc check on code that is legal but suspicious. Each lint is allow (silent), warn (a message) or deny (a compile error). arithmetic_overflow and overflowing_literals are deny: an overflow rustc can see will not compile.",
        see=("integer-overflow", "attribute", "panic"),
        priority=60,
        aka=("lints", "deny", "warn", "allow", "warning", "warnings", "arithmetic_overflow", "arithmetic overflow", "overflowing_literals", "clippy"),
        detect=(r"#!?\[(?:deny|forbid|warn|allow)\(",),
        rules=(
            "let x: u8 = 255 + 1; is refused when compiling (arithmetic_overflow), and so is let x: u8 = 256; (overflowing_literals).",
            "let x = 1 / 0; is refused too (unconditional_panic): a constant division by zero is an error, not a run-time panic.",
            "A warning, such as an unused variable, does not stop the build.",
            "#[deny(unused_variables)] on an item turns that warning into an error; #[allow(unused_variables)] silences it.",
        ),
        example=r"""
            #[allow(unused_variables)]
            let unused = 5;
            let big = 200u8;
            println!("{}", big.wrapping_add(100));
        """,
        out=r"44",
    ),
    *rust(
        "attribute",
        "Attribute (#[...])",
        "A note in #[...] before an item that changes how the compiler treats it: #[derive(Debug)], #[allow(unused)], #[test], #[cfg(...)]. Written #![...] with a bang it applies to the enclosing item or whole crate.",
        see=("derive", "lint", "macro", "struct"),
        priority=55,
        aka=("attributes", "#[test]", "cfg", "#[cfg]", "inline attribute", "inner attribute", "annotation", "decorator"),
        detect=(r"#!?\[\w+",),
        rules=(
            "An attribute applies to the next item only: #[derive(Debug)] struct A; struct B; gives A a Debug and B none.",
            "#[cfg(test)] code is left out of an ordinary build, so calling such a function from main does not compile.",
            "#[cfg(not(test))] code is kept in an ordinary build.",
            "#[allow(dead_code)] silences a warning; it does not change what the program does.",
        ),
        example=r"""
            #[derive(Debug, Clone)]
            struct Tag(u8);
            #[allow(dead_code)]
            fn unused() {}
            fn main() {
                let t = Tag(7);
                let u = t.clone();
                println!("{:?} {:?}", t, u);
            }
        """,
        out=r"Tag(7) Tag(7)",
    ),
    *rust(
        "turbofish",
        "Turbofish (::<>)",
        "Writing ::<Type> after a function or method name tells Rust which type to use when it cannot work it out: \"5\".parse::<i32>(), Vec::<u8>::new(), collect::<Vec<_>>().",
        see=("type-conversion", "collect", "generic", "vector"),
        priority=65,
        aka=("::<>", "::<", "explicit type", "type annotation", "type arguments"),
        detect=(r"::<",),
        rules=(
            "\"5\".parse().unwrap() alone does not compile: Rust cannot know which number type you want. Write parse::<i32>() or let n: i32 = ...",
            "The :: before the < is required in an expression: parse<i32>() is an error because it reads as a comparison.",
            "Either a type on the let or a turbofish gives the same answer.",
            "_ inside lets Rust fill in what it already knows: collect::<Vec<_>>().",
        ),
        example=r"""
            let n = "42".parse::<u8>().unwrap();
            let v = (1..4).map(|x| x * 2).collect::<Vec<_>>();
            let e = Vec::<i32>::new();
            println!("{} {:?} {}", n, v, e.len());
        """,
        out=r"42 [2, 4, 6] 0",
    ),
    *rust(
        "module",
        "Module (mod)",
        "A named container for code: mod name { ... } groups functions, structs and constants and gives them the path name::item. Everything inside is private until marked pub.",
        see=("pub", "use-statement", "function", "struct"),
        priority=60,
        aka=("mod", "modules", "namespace", "crate", "package", "path", "super"),
        detect=(r"\bmod\s+[a-z_]\w*\s*[{;]",),
        rules=(
            "A private function inside a module cannot be called from outside: shapes::secret() is an error unless secret is pub.",
            "A module's names are not in scope outside it: write the path (m::f()) or bring it in with use.",
            "super:: reaches the parent module, so an inner function can call one that is written outside the mod.",
            "A module may contain other modules, written a::b::item.",
        ),
        example=r"""
            mod shapes {
                pub fn area(w: u32, h: u32) -> u32 { w * h }
                fn secret() -> u32 { 7 }
                pub fn reveal() -> u32 { secret() }
            }
            fn main() {
                println!("{} {}", shapes::area(2, 3), shapes::reveal());
            }
        """,
        out=r"6 7",
    ),
    *rust(
        "use-statement",
        "use",
        "use brings a name from a module or the standard library into scope so you can write it without its full path: use std::collections::HashMap;. Several at once: use std::cmp::{max, min};.",
        see=("module", "pub", "hashmap"),
        priority=45,
        aka=("import", "imports", "use declaration", "include", "require", "using"),
        detect=(r"^\s*use\s+[A-Za-z_:{]",),
        rules=(
            "Without a use (or the full path), HashMap is unknown: let m: HashMap<i32, i32> = HashMap::new(); is an error.",
            "The prelude is already in scope everywhere: Vec, String, Option, Some, None, Result, Ok and Err need no use.",
            "use path as other renames the name.",
            "A use inside a function body lasts only for that block.",
        ),
        example=r"""
            use std::collections::HashMap;
            use std::cmp::{max, min};
            fn main() {
                let mut m = HashMap::new();
                m.insert("a", max(3, 9));
                println!("{:?} {}", m.get("a"), min(3, 9));
            }
        """,
        out=r"Some(9) 3",
    ),
    *rust(
        "pub",
        "pub (visibility)",
        "Marks an item or a struct field as usable outside its module. Everything is private by default: only the module it is written in, and the modules inside that, may use it.",
        see=("module", "struct", "use-statement"),
        priority=50,
        aka=("public", "private", "visibility", "pub(crate)", "encapsulation", "access modifier"),
        detect=(r"\bpub\b",),
        rules=(
            "A private field cannot be read outside its module: a.balance is an error if balance is not pub; a pub getter method is the usual way.",
            "A struct with a private field cannot be built with a struct literal outside its module; give it a pub fn new.",
            "pub on an enum makes all its variants public, unlike struct fields, which each need their own pub.",
        ),
        example=r"""
            mod bank {
                pub struct Account { pub owner: &'static str, balance: i32 }
                impl Account {
                    pub fn new(owner: &'static str) -> Account { Account { owner, balance: 100 } }
                    pub fn balance(&self) -> i32 { self.balance }
                }
            }
            fn main() {
                let a = bank::Account::new("Ana");
                println!("{} {}", a.owner, a.balance());
            }
        """,
        out=r"Ana 100",
    ),
]
