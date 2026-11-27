"""The Rust glossary's rules, each held to the real rustc (run by tests/test_glossary_rust.py).

A check is ("<entry id>[, <entry id>]: the claim", program, expected). The program follows the Brain Drills item
convention: it is the BODY of `fn main()` unless it contains `fn main(` (then it is a complete program), and it prints
with println!. `expected` is the exact trimmed output, or "CE" (rustc refuses it: a type error, the borrow checker, a
deny-by-default lint) or "PANIC" (it compiles and panics when run). Every program is built debug AND -O and both must
agree, so no check depends on implicit integer overflow.

Every Rust word has a check here or is named in RUST_NOT_ORACLE_CHECKED (at most a tenth of them)."""

from __future__ import annotations

RUST_RULE_CHECKS: list[tuple[str, str, str]] = [
    # ── variables, mutability, constants, shadowing ─────────────────────
    ("variable: assigning twice to a plain let is a compile error", r"""let x = 1; x = 2; println!("{}", x);""", "CE"),
    ("variable: a variable must hold a value before it is read", r"""let x: i32; println!("{}", x);""", "CE"),
    ("variable: the type is worked out from how the variable is used later", r"""let x = 200; let y: u8 = x; println!("{}", y);""", "200"),
    ("variable: a plain whole number is an i32 (4 bytes)", r"""let x = 5; println!("{}", std::mem::size_of_val(&x));""", "4"),
    ("variable: a typed variable refuses a value of another type", r"""let x: u8 = 5.5; println!("{}", x);""", "CE"),
    ("mutability: let mut allows count += 1", r"""let mut count = 0; count += 1; count += 2; println!("{}", count);""", "3"),
    ("mutability: without mut the same line is an error", r"""let count = 0; count += 1; println!("{}", count);""", "CE"),
    ("mutability: moving a value into a plain let makes it fixed", r"""let mut a = vec![1]; let b = a; b.push(2); println!("{:?}", b);""", "CE"),
    ("mutability: a function taking &T cannot change what it is given", r"""
        fn add(v: &Vec<i32>) { v.push(1); }
        fn main() { let mut v = vec![]; add(&v); println!("{}", v.len()); }
    """, "CE"),
    ("mutability: a method taking &mut self needs a mut variable", r"""let v = vec![1]; v.push(2); println!("{:?}", v);""", "CE"),
    ("constant: a const can use arithmetic known at compile time", r"""const N: usize = 3 * 4; println!("{}", N);""", "12"),
    ("constant: a const can be an array length", r"""const N: usize = 3; let a = [0; N]; println!("{}", a.len());""", "3"),
    ("constant: a let variable cannot be an array length", r"""let n = 3; let a = [0; n]; println!("{}", a.len());""", "CE"),
    ("constant: const can never be mut", r"""const mut N: i32 = 1; println!("{}", N);""", "CE"),
    ("constant: the type is required", r"""const N = 5; println!("{}", N);""", "CE"),
    ("constant: static mut needs an unsafe block", r"""static mut C: i32 = 0; C += 1;""", "CE"),
    ("shadowing: a shadow inside a block ends at the brace", r"""let x = 1; { let x = 2; println!("{}", x); } println!("{}", x);""", "2\n1"),
    ("shadowing: let x = x * 2 makes a new x", r"""let x = 5; let x = x * 2; println!("{}", x);""", "10"),
    ("shadowing: a shadow may change the type", r"""let s = "42"; let s: i32 = s.parse().unwrap(); println!("{}", s + 1);""", "43"),
    ("shadowing: plain assignment cannot change the type", r"""let mut x = 1; x = "a"; println!("{}", x);""", "CE"),
    ("shadowing: a closure that captured the old variable keeps seeing it", r"""let x = 1; let f = || x; let x = 5; println!("{} {}", f(), x);""", "1 5"),
    ("shadowing: the old variable still exists, hidden", r"""let x = 1; let r = &x; let x = x + 1; println!("{} {}", r, x);""", "1 2"),
    # ── expressions, if, loops, functions, scope, closures ──────────────
    ("expression: a block's value is its last line without a semicolon", r"""let y = { let a = 3; a + 1 }; println!("{}", y);""", "4"),
    ("expression: a semicolon on the last line makes the block's value ()", r"""let y = { 1 + 2; }; println!("{:?}", y);""", "()"),
    ("expression: a function ending in a semicolon does not return its value", r"""
        fn f() -> i32 { 5; }
        fn main() { println!("{}", f()); }
    """, "CE"),
    ("expression: if branches must give the same type", r"""let x = if true { 1 } else { "a" }; println!("{}", x);""", "CE"),
    ("expression, match: match is an expression", r"""let s = match 3 { 3 => "three", _ => "other" }; println!("{}", s);""", "three"),
    ("if-expression: the condition must be a bool", r"""if 1 { println!("x"); }""", "CE"),
    ("if-expression: an if with no else has type ()", r"""let x = if true { 1 }; println!("{:?}", x);""", "CE"),
    ("if-expression: the braces are required", r"""if true println!("a");""", "CE"),
    ("if-expression: the first true condition wins", r"""let n = 5; if n > 3 { println!("a"); } else if n > 1 { println!("b"); } else { println!("c"); }""", "a"),
    ("if-expression: it can give a value", r"""let n = 7; let k = if n % 2 == 0 { "even" } else { "odd" }; println!("{}", k);""", "odd"),
    ("loop: a while body may run zero times", r"""let mut n = 0; while n > 5 { n += 1; } println!("{}", n);""", "0"),
    ("loop: break leaves the loop and continue skips a round", r"""
        let mut s = 0;
        for i in 1..=6 { if i % 2 == 0 { continue; } if i > 4 { break; } s += i; }
        println!("{}", s);
    """, "4"),
    ("loop: a for loop's value is ()", r"""let x = for _i in 0..3 {}; println!("{:?}", x);""", "()"),
    ("while-loop: the condition must be a bool", r"""while 1 { break; }""", "CE"),
    ("while-loop: break leaves the loop early", r"""let mut i = 0; while true { i += 1; if i == 3 { break; } } println!("{}", i);""", "3"),
    ("while-loop: the condition is checked before each round", r"""let mut n = 27; let mut steps = 0; while n != 1 { n = if n % 2 == 0 { n / 2 } else { 3 * n + 1 }; steps += 1; } println!("{}", steps);""", "111"),
    ("for-loop: for x in v moves the vector", r"""let v = vec![1, 2]; for x in v { println!("{}", x); } println!("{}", v.len());""", "CE"),
    ("for-loop: for x in &v only borrows it", r"""let v = vec![1, 2]; for x in &v { let _ = x; } println!("{}", v.len());""", "2"),
    ("for-loop, range: 0..3 leaves out the end and 0..=3 includes it", r"""let mut c = 0; for _ in 0..3 { c += 1; } for _ in 0..=3 { c += 10; } println!("{}", c);""", "43"),
    ("for-loop: the loop variable is fixed unless mut", r"""for i in 0..3 { i += 1; println!("{}", i); }""", "CE"),
    ("for-loop: enumerate gives the position and the item", r"""for (i, c) in "ab".chars().enumerate() { println!("{}{}", i, c); }""", "0a\n1b"),
    ("loop-keyword: break with a value gives the loop its value", r"""let mut n = 1; let r = loop { n *= 2; if n > 100 { break n; } }; println!("{}", r);""", "128"),
    ("loop-keyword: only loop can break with a value", r"""let x = while true { break 5; }; println!("{:?}", x);""", "CE"),
    ("loop-keyword, never-type: a loop with no break fits where a value is expected", r"""
        fn f() -> i32 { loop { return 3; } }
        fn main() { println!("{}", f()); }
    """, "3"),
    ("loop-keyword: continue jumps to the next round", r"""let mut n = 0; let r = loop { n += 1; if n < 3 { continue; } break n * 10; }; println!("{}", r);""", "30"),
    ("labeled-break: break 'outer leaves both loops", r"""
        let mut found = (0, 0);
        'outer: for a in 1..10 { for b in 1..10 { if a * b == 42 { found = (a, b); break 'outer; } } }
        println!("{:?}", found);
    """, "(6, 7)"),
    ("labeled-break: an unlabeled break leaves only the inner loop", r"""
        let mut count = 0;
        for _a in 0..3 { for b in 0..3 { if b == 1 { break; } count += 1; } }
        println!("{}", count);
    """, "3"),
    ("labeled-break: break 'outer stops everything", r"""
        let mut count = 0;
        'outer: for _a in 0..3 { for b in 0..3 { if b == 1 { break 'outer; } count += 1; } }
        println!("{}", count);
    """, "1"),
    ("labeled-break: continue 'outer skips the rest of the outer body", r"""
        let mut count = 0;
        'outer: for _a in 0..3 { for b in 0..3 { if b == 1 { continue 'outer; } count += 10; } count += 1; }
        println!("{}", count);
    """, "30"),
    ("function: the last expression is returned", r"""
        fn sq(x: i32) -> i32 { x * x }
        fn main() { println!("{}", sq(4)); }
    """, "16"),
    ("function: return leaves early", r"""
        fn f(x: i32) -> &'static str { if x < 0 { return "neg"; } "pos" }
        fn main() { println!("{} {}", f(-1), f(1)); }
    """, "neg pos"),
    ("function: every parameter needs a type", r"""
        fn f(x) -> i32 { 1 }
        fn main() { println!("{}", f(1)); }
    """, "CE"),
    ("function: without -> it returns ()", r"""
        fn hi() {}
        fn main() { println!("{:?}", hi()); }
    """, "()"),
    ("function: too many arguments is an error", r"""
        fn f(a: i32) -> i32 { a }
        fn main() { println!("{}", f(1, 2)); }
    """, "CE"),
    ("function: it may be written below its caller", r"""
        fn main() { println!("{}", later()); }
        fn later() -> i32 { 9 }
    """, "9"),
    ("scope: a name is unknown after the closing brace", r"""{ let a = 1; } println!("{}", a);""", "CE"),
    ("scope: a name is not visible above its let", r"""println!("{}", b); let b = 1;""", "CE"),
    ("scope: a function cannot see its caller's locals", r"""
        fn f() -> i32 { x }
        fn main() { let x = 1; println!("{}", f()); }
    """, "CE"),
    ("scope: inner blocks see the names around them", r"""let a = 1; { println!("{}", a + 1); }""", "2"),
    ("scope, drop: variables are dropped in reverse order at the end of the scope", r"""
        struct D(&'static str);
        impl Drop for D { fn drop(&mut self) { println!("drop {}", self.0); } }
        fn main() { let _a = D("a"); let _b = D("b"); println!("end"); }
    """, "end\ndrop b\ndrop a"),
    ("closure: it can use a variable from around it", r"""let offset = 10; let add = |x: i32| x + offset; println!("{} {}", add(1), add(2));""", "11 12"),
    ("closure: parameter types are usually worked out", r"""let f = |x| x + 1; println!("{}", f(2));""", "3"),
    ("closure: move takes ownership of what it uses", r"""let s = String::from("a"); let f = move || s.len(); println!("{} {}", f(), s);""", "CE"),
    ("closure: a closure that changes a capture must be mut", r"""let mut n = 0; let inc = || n += 1; inc(); println!("{}", n);""", "CE"),
    ("closure: declared mut it can change the capture", r"""let mut n = 0; let mut inc = || n += 1; inc(); inc(); println!("{}", n);""", "2"),
    ("closure: the first use fixes the parameter type", r"""let f = |x| x; f(1); f("a");""", "CE"),
    ("closure: two closures with the same code have different types", r"""let k = 1; let a = |x: i32| x + k; let b = |x: i32| x + k; let v = vec![a, b]; println!("{}", v.len());""", "CE"),
    # ── numbers ─────────────────────────────────────────────────────────
    ("integer: i8 and u8 hold -128..127 and 0..255", r"""println!("{} {} {} {}", i8::MIN, i8::MAX, u8::MIN, u8::MAX);""", "-128 127 0 255"),
    ("integer: an unsigned type cannot hold a negative number", r"""let x: u32 = -1; println!("{}", x);""", "CE"),
    ("integer: an i32 and an i64 cannot be added", r"""let a: i32 = 1; let b: i64 = 2; println!("{}", a + b);""", "CE"),
    ("integer: underscores and suffixes are allowed in literals", r"""println!("{} {}", 1_000 + 1, 5u8 + 250u8);""", "1001 255"),
    ("usize: an index must be a usize", r"""let v = vec![1]; let i: i32 = 0; println!("{}", v[i]);""", "CE"),
    ("usize: convert with as", r"""let n: i32 = 2; let v = vec![1, 2, 3]; println!("{}", v[n as usize]);""", "3"),
    ("usize: checked_sub catches going below zero", r"""let v: Vec<i32> = vec![]; println!("{:?}", v.len().checked_sub(1));""", "None"),
    ("usize: it is 8 bytes on a 64-bit machine", r"""println!("{}", std::mem::size_of::<usize>());""", "8"),
    ("usize, as-cast: a negative i32 becomes a huge usize", r"""println!("{}", -1i32 as usize);""", "18446744073709551615"),
    ("division: 7 / 2 is 3 and -7 / 2 is -3", r"""println!("{} {}", 7 / 2, -7 / 2);""", "3 -3"),
    ("division: the remainder has the sign of the left number", r"""println!("{} {} {}", 7 % 3, -7 % 3, (-7i32).rem_euclid(3));""", "1 -1 2"),
    ("division: an integer cannot be divided by a float", r"""println!("{}", 7 / 2.0);""", "CE"),
    ("division, panic: integer division by zero panics", r"""let v: Vec<i32> = Vec::new(); let z = v.len() as i32; println!("{}", 5 / z);""", "PANIC"),
    ("division: float division by zero is inf or NaN", r"""let z = 0.0_f64; println!("{} {}", 1.0 / z, (0.0 / z).is_nan());""", "inf true"),
    ("floating-point: an integer cannot fill an f64 variable", r"""let x: f64 = 3; println!("{}", x);""", "CE"),
    ("floating-point: 0.1 + 0.2 is not 0.3", r"""println!("{}", 0.1 + 0.2 == 0.3);""", "false"),
    ("floating-point: {} prints 1.0 as 1 and {:?} as 1.0", r"""println!("{} {:?}", 1.0, 1.0);""", "1 1.0"),
    ("floating-point: NaN is not equal to itself", r"""let n = f64::NAN; println!("{} {}", n == n, n.is_nan());""", "false true"),
    ("floating-point, sorting: a Vec<f64> cannot use sort()", r"""let mut v = vec![2.5, 1.5]; v.sort(); println!("{:?}", v);""", "CE"),
    ("floating-point: a decimal literal is an f64", r"""println!("{}", std::mem::size_of_val(&2.5));""", "8"),
    ("boolean: only a bool can be a condition", r"""let n = 1; if n { println!("yes"); }""", "CE"),
    ("boolean: && does not run the right side when the left is false", r"""
        fn noisy() -> bool { println!("called"); true }
        fn main() { let r = false && noisy(); println!("{}", r); }
    """, "false"),
    ("boolean: the single & runs both sides", r"""
        fn noisy() -> bool { println!("called"); true }
        fn main() { let r = false & noisy(); println!("{}", r); }
    """, "called\nfalse"),
    ("boolean: bools cast to integers and compare", r"""println!("{} {}", true as i32, false < true);""", "1 true"),
    ("boolean, as-cast: a number cannot be cast to bool", r"""let b = 1 as bool; println!("{}", b);""", "CE"),
    ("char: a string cannot fill a char", r"""let c: char = "a"; println!("{}", c);""", "CE"),
    ("char: a char is 4 bytes and a u8 is 1", r"""println!("{} {}", std::mem::size_of::<char>(), std::mem::size_of::<u8>());""", "4 1"),
    ("char, as-cast: 'a' as u32 is 97 and a u8 casts back", r"""println!("{} {}", 'a' as u32, 97u8 as char);""", "97 a"),
    ("char, as-cast: only a u8 can be cast to char", r"""let c = 97u32 as char; println!("{}", c);""", "CE"),
    ("char: to_digit gives an Option", r"""println!("{:?} {:?}", '7'.to_digit(10), 'x'.to_digit(10));""", "Some(7) None"),
    ("byte: b'a' is the u8 97", r"""let b = b'a'; println!("{}", b + 1);""", "98"),
    ("byte: len counts bytes", r"""println!("{}", "h\u{e9}llo".len());""", "6"),
    ("byte, string: a string cannot be indexed by position", r"""let s = "abc"; println!("{}", s[0]);""", "CE"),
    ("byte: as_bytes gives the bytes to index", r"""let s = "abc"; println!("{}", s.as_bytes()[0]);""", "97"),
    ("byte, as-cast: 300 as u8 keeps the low bits", r"""println!("{}", 300i32 as u8);""", "44"),
    ("tuple: parts are reached by position", r"""let t = (3, "three", 3.0); println!("{} {}", t.0, t.1);""", "3 three"),
    ("tuple: t[0] is an error", r"""let t = (1, 2); println!("{}", t[0]);""", "CE"),
    ("tuple: the type is the list of part types", r"""let t: (i32, i32) = (1, "a"); println!("{:?}", t);""", "CE"),
    ("tuple: tuples compare from the left", r"""println!("{}", (1, 2) < (1, 3));""", "true"),
    ("tuple: a one-part tuple needs a trailing comma", r"""let a = (5,); let b = (5); println!("{:?} {:?}", a, b);""", "(5,) 5"),
    ("array: the length is part of the type", r"""let a: [i32; 3] = [1, 2, 3, 4]; println!("{:?}", a);""", "CE"),
    ("array: a position past the end panics at run time", r"""let a = [1, 2, 3]; let i = a.iter().count(); println!("{}", a[i]);""", "PANIC"),
    ("array: a constant position past the end is refused when compiling", r"""let a = [1, 2, 3]; println!("{}", a[5]);""", "CE"),
    ("array: an array of Copy values is Copy", r"""let a = [1, 2]; let mut b = a; b[0] = 9; println!("{:?} {:?}", a, b);""", "[1, 2] [9, 2]"),
    ("array: [0; 4] makes four zeros", r"""let a = [0; 4]; println!("{:?} {}", a, a.len());""", "[0, 0, 0, 0] 4"),
    ("unit-type: a function with no -> returns ()", r"""
        fn nothing() {}
        fn main() { let u = nothing(); println!("{:?} {}", u, u == ()); }
    """, "() true"),
    ("unit-type: Ok(()) is a Result with nothing to report", r"""let r: Result<(), String> = Ok(()); println!("{:?}", r);""", "Ok(())"),
    ("unit-type: () takes zero bytes", r"""println!("{}", std::mem::size_of::<()>());""", "0"),
    ("unit-type: a block ending in a semicolon is ()", r"""let u = { 5; }; println!("{}", u == ());""", "true"),
    ("never-type: panic! fits in a branch of an i32", r"""let n: i32 = if true { 5 } else { panic!("x") }; println!("{}", n);""", "5"),
    ("never-type: continue in a match arm fits a number", r"""
        let mut sum = 0;
        for s in ["1", "x", "3"] { let n: i32 = match s.parse() { Ok(n) => n, Err(_) => continue }; sum += n; }
        println!("{}", sum);
    """, "4"),
    ("never-type: a function declared -> ! may not return", r"""
        fn f() -> ! { 1 }
        fn main() { f(); }
    """, "CE"),
    ("integer-overflow, lint: a constant that overflows is refused", r"""let x = i32::MAX + 1; println!("{}", x);""", "CE"),
    ("integer-overflow: the four ways to treat an overflow", r"""println!("{:?} {} {} {:?}", 250u8.checked_add(10), 250u8.wrapping_add(10), 250u8.saturating_add(10), 250u8.overflowing_add(10));""", "None 4 255 (4, true)"),
    ("integer-overflow: unsigned subtraction overflows below zero", r"""println!("{:?}", 5u32.checked_sub(6));""", "None"),
    ("integer-overflow: checked_mul catches a big product", r"""println!("{:?}", 100_000i32.checked_mul(100_000));""", "None"),
    ("wrapping-arithmetic: 250u8 + 10 wraps to 4 and 0u8 - 1 to 255", r"""println!("{} {}", 250u8.wrapping_add(10), 0u8.wrapping_sub(1));""", "4 255"),
    ("wrapping-arithmetic: a signed type wraps to the other end", r"""println!("{}", i8::MAX.wrapping_add(1));""", "-128"),
    ("wrapping-arithmetic: wrapping_mul loses the top bits", r"""println!("{}", 200u8.wrapping_mul(2));""", "144"),
    ("wrapping-arithmetic: the Wrapping type always wraps", r"""use std::num::Wrapping; let w = Wrapping(250u8) + Wrapping(10u8); println!("{}", w);""", "4"),
    ("checked-arithmetic: overflow gives None and no overflow gives Some", r"""println!("{:?} {:?}", i32::MAX.checked_add(1), 5i32.checked_add(1));""", "None Some(6)"),
    ("checked-arithmetic: checked_div(0) is None", r"""println!("{:?}", 10u32.checked_div(0));""", "None"),
    ("checked-arithmetic: checked_sub catches going below zero on unsigned", r"""println!("{:?}", 3u32.checked_sub(5));""", "None"),
    ("checked-arithmetic: unwrap_or(255) saturates by hand", r"""println!("{}", 250u8.checked_add(10).unwrap_or(255));""", "255"),
    ("checked-arithmetic: checked_pow(31) fits and checked_pow(32) does not", r"""println!("{:?} {:?}", 2u32.checked_pow(31), 2u32.checked_pow(32));""", "Some(2147483648) None"),
    ("saturating-arithmetic: 250u8 + 10 stops at 255", r"""println!("{}", 250u8.saturating_add(10));""", "255"),
    ("saturating-arithmetic: unsigned subtraction stops at 0", r"""println!("{}", 5u8.saturating_sub(10));""", "0"),
    ("saturating-arithmetic: signed types stop at their ends", r"""println!("{} {}", i8::MIN.saturating_sub(1), 100i8.saturating_mul(2));""", "-128 127"),
    ("as-cast: integers keep their low bits", r"""println!("{} {}", 300i32 as u8, -1i32 as u32);""", "44 4294967295"),
    ("as-cast: a float is cut toward zero and clamped", r"""println!("{} {} {} {} {}", 3.99_f64 as i32, -5.7_f64 as i32, 1e10_f64 as i32, f64::NAN as i32, -1.0_f64 as u8);""", "3 -5 2147483647 0 0"),
    ("as-cast: an integer to a float can lose precision", r"""println!("{}", 16777217i32 as f32);""", "16777216"),
    ("as-cast: a string cannot be cast to a number", r"""let n = "5" as i32; println!("{}", n);""", "CE"),
    ("type-conversion: i32 + i64 needs a conversion first", r"""let a = 1i32; let b = 2i64; println!("{}", i64::from(a) + b);""", "3"),
    ("type-conversion: From exists only for conversions that cannot fail", r"""let x = i32::from(5i64); println!("{}", x);""", "CE"),
    ("type-conversion: TryFrom gives a Result", r"""println!("{} {:?}", u8::try_from(300i32).is_err(), u8::try_from(200i32));""", "true Ok(200)"),
    ("type-conversion: parse gives a Result", r"""println!("{:?} {}", "12".parse::<i32>(), "x".parse::<i32>().is_err());""", "Ok(12) true"),
    ("type-conversion: parse rejects spaces", r"""println!("{}", " 5".parse::<i32>().is_err());""", "true"),
    ("hexadecimal: 0xFF, 0b101 and 0o17", r"""println!("{} {} {}", 0xFF, 0b101, 0o17);""", "255 5 15"),
    ("hexadecimal: {:#x} adds 0x and {:#010b} pads after the prefix", r"""println!("{:#x} {:#010b}", 255, 5);""", "0xff 0b00000101"),
    ("hexadecimal: lower and upper case", r"""println!("{:x} {:X}", 255, 255);""", "ff FF"),
    ("hexadecimal: a negative number prints its bits", r"""println!("{:x}", -1i8);""", "ff"),
    ("hexadecimal: from_str_radix does not accept a 0x prefix", r"""println!("{} {:?}", u8::from_str_radix("0xff", 16).is_err(), u8::from_str_radix("ff", 16));""", "true Ok(255)"),
    # ── printing, formatting, macros, panics, lints, attributes, modules ─
    ("formatting: the placeholders must match the arguments", r"""println!("{} {}", 1);""", "CE"),
    ("formatting: {{ and }} print braces", r"""println!("{{}} {}", 5);""", "{} 5"),
    ("formatting: format! returns a String", r"""let s = format!("{}-{}", 1, 2); println!("{}", s.len());""", "3"),
    ("formatting: {x} names a plain variable", r"""let x = 5; println!("{x} {x}");""", "5 5"),
    ("formatting: {x + 1} is an error", r"""let x = 5; println!("{x + 1}");""", "CE"),
    ("formatting: a Vec cannot use {}", r"""println!("{}", vec![1]);""", "CE"),
    ("println: print! adds no newline and println!() adds just one", r"""print!("a"); println!(); print!("b");""", "a\nb"),
    ("println: the template must be a literal", r"""let s = "hi"; println!(s);""", "CE"),
    ("println: eprintln! does not go to stdout", r"""eprintln!("err"); println!("out");""", "out"),
    ("println: arguments are only borrowed", r"""let s = String::from("a"); println!("{}", s); println!("{}", s);""", "a\na"),
    ("debug-format: a struct needs derive(Debug)", r"""
        struct P { x: i32 }
        fn main() { println!("{:?}", P { x: 1 }); }
    """, "CE"),
    ("debug-format: strings show quotes and escapes", r"""println!("{:?}", "a\nb");""", '"a\\nb"'),
    ("debug-format: {:#?} spreads over lines", r"""println!("{:#?}", (1, 2));""", "(\n    1,\n    2,\n)"),
    ("debug-format: dbg! gives the value back", r"""let x = dbg!(2 + 3); println!("{}", x);""", "5"),
    ("debug-format: Option and Vec print in debug form", r"""println!("{:?} {:?}", Some(3), vec!["a"]);""", 'Some(3) ["a"]'),
    ("display: a struct cannot use {} without Display", r"""
        struct P { x: i32 }
        fn main() { println!("{}", P { x: 1 }); }
    """, "CE"),
    ("display: implementing Display gives to_string", r"""
        use std::fmt;
        struct P(i32, i32);
        impl fmt::Display for P {
            fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result { write!(f, "({}, {})", self.0, self.1) }
        }
        fn main() { println!("{} {}", P(1, 2), P(3, 4).to_string()); }
    """, "(1, 2) (3, 4)"),
    ("display: Display cannot be derived", r"""
        #[derive(Display)]
        struct P;
        fn main() {}
    """, "CE"),
    ("display: Option has no Display", r"""println!("{}", Some(1));""", "CE"),
    ("padding: numbers right-align and text left-aligns", r"""println!("[{:5}] [{:5}]", 42, "ab");""", "[   42] [ab   ]"),
    ("padding: {:05} puts the zeros after the sign", r"""println!("{:05}", -42);""", "-0042"),
    ("padding: the width is a minimum", r"""println!("{:2}", 12345);""", "12345"),
    ("padding: precision cuts a string", r"""println!("{:.3}", "abcdef");""", "abc"),
    ("padding: the width may come from an argument", r"""println!("[{:>w$}]", 7, w = 4);""", "[   7]"),
    ("padding: ^ centres with the extra space on the right", r"""println!("[{:^5}] [{:*^7}]", 42, "ab");""", "[ 42  ] [**ab***]"),
    ("macro: a macro call needs the !", r"""println("x");""", "CE"),
    ("macro: vec! takes a list or a repeat", r"""println!("{:?} {:?}", vec![1, 2, 3], vec![0; 3]);""", "[1, 2, 3] [0, 0, 0]"),
    ("macro, panic: assert_eq! panics when the sides differ", r"""assert_eq!(1 + 1, 3);""", "PANIC"),
    ("macro: $x:expr keeps grouping, so square!(3 + 1) is 16", r"""
        macro_rules! square { ($x:expr) => { $x * $x }; }
        fn main() { println!("{}", square!(3 + 1)); }
    """, "16"),
    ("panic: an index past the end panics", r"""let v = vec![1, 2, 3]; let i = v.len() + 6; println!("{}", v[i]);""", "PANIC"),
    ("panic: get gives None instead of panicking", r"""let v = vec![1, 2, 3]; println!("{:?}", v.get(9));""", "None"),
    ("panic: a failed assert! panics", r"""let n = 3; assert!(n > 5);""", "PANIC"),
    ("panic: panic! takes a message like println!", r"""panic!("bad {}", 1);""", "PANIC"),
    ("panic: unwinding still runs drop", r"""
        struct D;
        impl Drop for D { fn drop(&mut self) { println!("cleanup"); } }
        fn main() {
            let r = std::panic::catch_unwind(|| { let _d = D; panic!("boom"); });
            println!("{}", r.is_err());
        }
    """, "cleanup\ntrue"),
    ("lint: a constant that overflows is refused", r"""let x: u8 = 255 + 1; println!("{}", x);""", "CE"),
    ("lint: an out-of-range literal is refused", r"""let x: u8 = 256; println!("{}", x);""", "CE"),
    ("lint: a constant division by zero is refused", r"""let x = 1 / 0; println!("{}", x);""", "CE"),
    ("lint: a warning does not stop the build", r"""let unused = 1; println!("ok");""", "ok"),
    ("lint: #[deny(unused_variables)] makes the warning an error", r"""
        #[deny(unused_variables)]
        fn main() { let x = 1; println!("ok"); }
    """, "CE"),
    ("lint: #[allow(unused_variables)] silences it", r"""
        #[allow(unused_variables)]
        fn main() { let x = 1; println!("ok"); }
    """, "ok"),
    ("attribute: derive applies to the next item only", r"""
        #[derive(Debug)]
        struct A;
        struct B;
        fn main() { println!("{:?} {:?}", A, B); }
    """, "CE"),
    ("attribute: #[cfg(test)] code is left out of an ordinary build", r"""
        #[cfg(test)]
        fn secret() -> i32 { 1 }
        fn main() { println!("{}", secret()); }
    """, "CE"),
    ("attribute: #[cfg(not(test))] code is kept", r"""
        #[cfg(not(test))]
        fn f() -> i32 { 7 }
        fn main() { println!("{}", f()); }
    """, "7"),
    ("attribute: #[allow(dead_code)] changes nothing at run time", r"""
        #[allow(dead_code)]
        fn unused() {}
        fn main() { println!("ok"); }
    """, "ok"),
    ("turbofish: parse needs to know the type", r"""let n = "5".parse().unwrap(); println!("{}", n);""", "CE"),
    ("turbofish: a type on the let works too", r"""let n: i32 = "5".parse().unwrap(); println!("{}", n + 1);""", "6"),
    ("turbofish: the :: is required", r"""let n = "5".parse<i32>().unwrap(); println!("{}", n);""", "CE"),
    ("turbofish: collect::<Vec<_>>() names the collection", r"""println!("{:?}", (1..4).map(|x| x * 2).collect::<Vec<_>>());""", "[2, 4, 6]"),
    ("module: a private function cannot be called from outside", r"""
        mod shapes { fn secret() -> u32 { 7 } pub fn reveal() -> u32 { secret() } }
        fn main() { println!("{} {}", shapes::reveal(), shapes::secret()); }
    """, "CE"),
    ("module: a pub function is reached by its path", r"""
        mod shapes { pub fn area(w: u32, h: u32) -> u32 { w * h } }
        fn main() { println!("{}", shapes::area(2, 3)); }
    """, "6"),
    ("module: a module's names are not in scope outside it", r"""
        mod m { pub fn f() {} }
        fn main() { f(); }
    """, "CE"),
    ("module: super:: reaches the parent", r"""
        fn base() -> i32 { 10 }
        mod inner { pub fn f() -> i32 { super::base() + 1 } }
        fn main() { println!("{}", inner::f()); }
    """, "11"),
    ("module: modules nest", r"""
        mod a { pub mod b { pub fn f() -> i32 { 4 } } }
        fn main() { println!("{}", a::b::f()); }
    """, "4"),
    ("use-statement: HashMap needs a use or the full path", r"""let m: HashMap<i32, i32> = HashMap::new(); println!("{}", m.len());""", "CE"),
    ("use-statement: the prelude needs no use", r"""let v: Vec<i32> = Vec::new(); let o: Option<i32> = Some(1); println!("{:?} {}", o, v.len());""", "Some(1) 0"),
    ("use-statement: use ... as renames", r"""use std::collections::HashMap as Map; let mut m = Map::new(); m.insert(1, 2); println!("{}", m.len());""", "1"),
    ("use-statement: the full path works without a use", r"""let mut m = std::collections::HashMap::new(); m.insert(1, 2); println!("{}", m.len());""", "1"),
    ("pub: a private field cannot be read outside its module", r"""
        mod bank { pub struct A { balance: i32 } impl A { pub fn new() -> A { A { balance: 1 } } } }
        fn main() { let a = bank::A::new(); println!("{}", a.balance); }
    """, "CE"),
    ("pub: a struct with a private field cannot be built by a literal outside", r"""
        mod bank { pub struct A { pub owner: i32, balance: i32 } }
        fn main() { let a = bank::A { owner: 1, balance: 2 }; println!("{}", a.owner); }
    """, "CE"),
    ("pub: a pub enum has public variants", r"""
        mod m { pub enum E { A, B } }
        fn main() { match m::E::A { m::E::A => println!("a"), m::E::B => println!("b") } }
    """, "a"),
    ("pub: a pub getter reads a private field", r"""
        mod bank { pub struct A { balance: i32 } impl A { pub fn new() -> A { A { balance: 100 } } pub fn balance(&self) -> i32 { self.balance } } }
        fn main() { println!("{}", bank::A::new().balance()); }
    """, "100"),
    # ── ownership ───────────────────────────────────────────────────────
    ("ownership: after a move the old owner cannot be read", r"""let a = String::from("x"); let b = a; println!("{} {}", a, b);""", "CE"),
    ("ownership: passing a String by value moves it", r"""
        fn eat(s: String) -> usize { s.len() }
        fn main() { let a = String::from("hi"); let n = eat(a); println!("{} {}", n, a); }
    """, "CE"),
    ("ownership: returning the value gives ownership back", r"""
        fn id(s: String) -> String { s }
        fn main() { let a = String::from("x"); let a = id(a); println!("{}", a); }
    """, "x"),
    ("ownership, move: a value is dropped once, by its last owner", r"""
        struct D;
        impl Drop for D { fn drop(&mut self) { println!("dropped"); } }
        fn main() { let a = D; let _b = a; println!("moved"); }
    """, "moved\ndropped"),
    ("ownership, copy: an integer is copied, not moved", r"""let a = 5; let b = a; println!("{} {}", a, b);""", "5 5"),
    ("move: reading a moved Vec is an error", r"""let a = vec![1]; let b = a; println!("{:?} {:?}", a, b);""", "CE"),
    ("move: a mut variable may be given a new value after a move", r"""let mut a = String::from("x"); let b = a; a = String::from("y"); println!("{} {}", a, b);""", "y x"),
    ("move: you cannot move a String out of a Vec by index", r"""let v = vec![String::from("a")]; let s = v[0]; println!("{}", s);""", "CE"),
    ("move: a move closure takes ownership", r"""let s = String::from("a"); let f = move || s.len(); println!("{} {}", f(), s.len());""", "CE"),
    ("copy: tuples of Copy values are Copy", r"""let a = (1, 2.5, 'c', true); let b = a; println!("{:?} {:?}", a, b);""", "(1, 2.5, 'c', true) (1, 2.5, 'c', true)"),
    ("copy: a struct is Copy only if you derive it", r"""
        #[derive(Clone, Copy, Debug)]
        struct P { x: i32 }
        fn main() { let a = P { x: 1 }; let b = a; println!("{:?} {:?}", a, b); }
    """, "P { x: 1 } P { x: 1 }"),
    ("copy: a struct with a Vec field cannot be Copy", r"""
        #[derive(Clone, Copy)]
        struct S { v: Vec<i32> }
        fn main() { let s = S { v: vec![] }; println!("{}", s.v.len()); }
    """, "CE"),
    ("copy: without Copy a struct moves", r"""
        struct P { x: i32 }
        fn main() { let a = P { x: 1 }; let b = a; println!("{} {}", a.x, b.x); }
    """, "CE"),
    ("copy, drop: a type with Drop cannot be Copy", r"""
        #[derive(Clone, Copy)]
        struct S;
        impl Drop for S { fn drop(&mut self) {} }
        fn main() { let _s = S; }
    """, "CE"),
    ("clone: both are usable and independent after a clone", r"""let a = vec![1, 2, 3]; let mut b = a.clone(); b.push(4); println!("{:?} {:?}", a, b);""", "[1, 2, 3] [1, 2, 3, 4]"),
    ("clone: your struct needs derive(Clone)", r"""
        struct P { x: i32 }
        fn main() { let a = P { x: 1 }; let b = a.clone(); println!("{}", b.x); }
    """, "CE"),
    ("clone: a Vec<String> clones every String", r"""let a = vec![String::from("x")]; let mut b = a.clone(); b[0].push('y'); println!("{:?} {:?}", a, b);""", r'["x"] ["xy"]'),
    ("clone, rc: Rc::clone copies only the pointer", r"""use std::rc::Rc; let a = Rc::new(5); let b = Rc::clone(&a); println!("{}", Rc::ptr_eq(&a, &b));""", "true"),
    ("borrowing: lending with & leaves the owner usable", r"""
        fn total(v: &Vec<i32>) -> i32 { v.iter().sum() }
        fn main() { let v = vec![1, 2, 3]; let t = total(&v); println!("{} {}", t, v.len()); }
    """, "6 3"),
    ("borrowing: many shared borrows may exist", r"""let s = String::from("a"); let r1 = &s; let r2 = &s; println!("{} {}", r1, r2);""", "a a"),
    ("borrowing: two &mut at once is an error", r"""let mut s = String::new(); let r1 = &mut s; let r2 = &mut s; r1.push('a'); r2.push('b');""", "CE"),
    ("borrowing: a & next to a &mut is an error", r"""let mut v = vec![1]; let first = &v[0]; v.push(2); println!("{}", first);""", "CE"),
    ("borrowing: the owner cannot move while a borrow is used later", r"""let s = String::from("a"); let r = &s; let t = s; println!("{} {}", r, t);""", "CE"),
    ("reference: it prints and compares like the value", r"""let x = 10; let r = &x; println!("{} {} {}", r, *r + 1, r == &10);""", "10 11 true"),
    ("reference: it cannot outlive its value", r"""let r; { let x = 5; r = &x; } println!("{}", r);""", "CE"),
    ("reference: there is no null, only Option<&T>", r"""let r: Option<&i32> = None; println!("{:?}", r);""", "None"),
    ("reference: &T is Copy", r"""let x = 1; let r = &x; let r2 = r; println!("{} {}", r, r2);""", "1 1"),
    ("reference: &mut T is not Copy", r"""let mut x = 1; let r = &mut x; let r2 = r; *r += 1; println!("{}", r2);""", "CE"),
    ("mutable-reference: &mut of a plain let variable is an error", r"""let x = 5; let r = &mut x; *r += 1; println!("{}", x);""", "CE"),
    ("mutable-reference: it changes the value through *", r"""
        fn bump(n: &mut i32) { *n += 1; }
        fn main() { let mut x = 5; bump(&mut x); bump(&mut x); println!("{}", x); }
    """, "7"),
    ("mutable-reference: n += 1 without a star is a type error", r"""
        fn bump(n: &mut i32) { n += 1; }
        fn main() { let mut x = 5; bump(&mut x); println!("{}", x); }
    """, "CE"),
    ("mutable-reference: reading the owner while the &mut is still used is an error", r"""let mut x = 1; let r = &mut x; println!("{}", x); *r += 1;""", "CE"),
    ("dereference: assigning to a &mut needs the star", r"""let mut x = 1; let r = &mut x; r = 9; println!("{}", x);""", "CE"),
    ("dereference: *r = 9 changes the owner", r"""let mut x = 1; let r = &mut x; *r = 9; println!("{}", x);""", "9"),
    ("dereference: method calls and println! look through references", r"""let x = -3i32; let r = &x; println!("{} {}", r.abs(), r);""", "3 -3"),
    ("dereference: a reference is not the value", r"""let x = 5; let r = &x; println!("{}", r == 5);""", "CE"),
    ("dereference: a Box is followed the same way", r"""println!("{}", *Box::new(7));""", "7"),
    ("borrow-checker: pushing while a reference into the Vec is used later is an error", r"""let mut v = vec![1]; let r = &v[0]; v.push(2); println!("{}", r);""", "CE"),
    ("borrow-checker: changing a Vec while looping over it is an error", r"""let mut v = vec![1, 2]; for x in &v { v.push(*x); }""", "CE"),
    ("borrow-checker: a conflict is refused even on a branch that never runs", r"""let mut v = vec![1]; let r = &v; if false { v.push(2); } println!("{}", r.len());""", "CE"),
    ("borrow-checker, lifetime: a function cannot return a reference to its local", r"""
        fn f() -> &'static i32 { let x = 1; &x }
        fn main() { println!("{}", f()); }
    """, "CE"),
    ("borrow-checker: copying a value out before the push is accepted", r"""let mut v = vec![1, 2, 3]; let first = v[0]; v.push(4); let last = &v[3]; println!("{} {}", first, last);""", "1 4"),
    ("lifetime: longest needs lifetime names", r"""
        fn longest(x: &str, y: &str) -> &str { if x.len() >= y.len() { x } else { y } }
        fn main() { println!("{}", longest("a", "bb")); }
    """, "CE"),
    ("lifetime: with names it works", r"""
        fn longest<'a>(x: &'a str, y: &'a str) -> &'a str { if x.len() >= y.len() { x } else { y } }
        fn main() { let a = String::from("apple"); let b = String::from("fig"); println!("{}", longest(&a, &b)); }
    """, "apple"),
    ("lifetime: the result lives only as long as the shorter-lived argument", r"""
        fn longest<'a>(x: &'a str, y: &'a str) -> &'a str { if x.len() > y.len() { x } else { y } }
        fn main() {
            let a = String::from("long string");
            let result;
            { let b = String::from("xyz"); result = longest(a.as_str(), b.as_str()); }
            println!("{}", result);
        }
    """, "CE"),
    ("lifetime: a string literal is a &'static str", r"""let s: &'static str = "hi"; println!("{}", s);""", "hi"),
    ("lifetime: one input reference needs no name", r"""
        fn first(s: &str) -> &str { &s[..1] }
        fn main() { println!("{}", first("hello")); }
    """, "h"),
    ("non-lexical-lifetimes: a borrow ends at its last use", r"""let mut v = vec![1, 2, 3]; let first = &v[0]; println!("{}", first); v.push(4); println!("{:?}", v);""", "1\n[1, 2, 3, 4]"),
    ("non-lexical-lifetimes: used after the push it is an error", r"""let mut v = vec![1, 2, 3]; let first = &v[0]; v.push(4); println!("{}", first);""", "CE"),
    ("non-lexical-lifetimes: a &mut borrow ends at its last use too", r"""let mut s = String::new(); let r = &mut s; r.push('a'); s.push('b'); println!("{}", s);""", "ab"),
    ("box: a recursive type needs a Box", r"""
        enum List { Cons(i32, List), Nil }
        fn main() { let _l = List::Nil; }
    """, "CE"),
    ("box: a Box has one owner", r"""let a = Box::new(1); let b = a; println!("{} {}", a, b);""", "CE"),
    ("box: a Box is one pointer in size", r"""println!("{}", std::mem::size_of::<Box<i32>>());""", "8"),
    ("box: * gives the value inside", r"""let b = Box::new(41); println!("{}", *b + 1);""", "42"),
    ("rc: strong_count counts the owners", r"""use std::rc::Rc; let a = Rc::new(5); let b = Rc::clone(&a); println!("{} {}", Rc::strong_count(&a), Rc::ptr_eq(&a, &b));""", "2 true"),
    ("rc: the contents are read-only", r"""use std::rc::Rc; let a = Rc::new(vec![1]); a.push(2);""", "CE"),
    ("rc: an Rc cannot be sent to a thread", r"""use std::rc::Rc; let a = Rc::new(1); let h = std::thread::spawn(move || println!("{}", a)); h.join().unwrap();""", "CE"),
    ("rc: an Arc can", r"""use std::sync::Arc; let a = Arc::new(5); let b = Arc::clone(&a); let h = std::thread::spawn(move || *b + 1); println!("{}", h.join().unwrap());""", "6"),
    ("rc: dropping one Rc lowers the count", r"""use std::rc::Rc; let a = Rc::new(1); let b = Rc::clone(&a); drop(b); println!("{}", Rc::strong_count(&a));""", "1"),
    ("refcell: two writers at once panic at run time", r"""use std::cell::RefCell; let c = RefCell::new(1); let a = c.borrow_mut(); let b = c.borrow_mut(); println!("{} {}", a, b);""", "PANIC"),
    ("refcell: it works without let mut", r"""use std::cell::RefCell; let c = RefCell::new(5); *c.borrow_mut() += 1; println!("{}", c.borrow());""", "6"),
    ("refcell: many readers are fine", r"""use std::cell::RefCell; let c = RefCell::new(1); let a = c.borrow(); let b = c.borrow(); println!("{}", *a + *b);""", "2"),
    ("refcell: Cell gets and sets Copy values", r"""use std::cell::Cell; let c = Cell::new(1); c.set(c.get() + 1); println!("{}", c.get());""", "2"),
    ("refcell: try_borrow_mut gives an Err while borrowed", r"""use std::cell::RefCell; let c = RefCell::new(1); let _r = c.borrow(); println!("{}", c.try_borrow_mut().is_err());""", "true"),
    ("drop: drops run in reverse order with drop(b) in the middle", r"""
        struct Noisy(&'static str);
        impl Drop for Noisy { fn drop(&mut self) { println!("drop {}", self.0); } }
        fn main() {
            let _a = Noisy("a");
            let b = Noisy("b");
            drop(b);
            let _c = Noisy("c");
            println!("end");
        }
    """, "drop b\nend\ndrop c\ndrop a"),
    ("drop: drop(x) moves x", r"""let s = String::from("a"); drop(s); println!("{}", s);""", "CE"),
    ("drop: a value moved into a function is dropped at its end", r"""
        struct Noisy(&'static str);
        impl Drop for Noisy { fn drop(&mut self) { println!("drop {}", self.0); } }
        fn take(n: Noisy) { println!("took {}", n.0); }
        fn main() { let a = Noisy("a"); take(a); println!("after"); }
    """, "took a\ndrop a\nafter"),
    ("drop: let _ = value drops at once", r"""
        struct Noisy(&'static str);
        impl Drop for Noisy { fn drop(&mut self) { println!("drop {}", self.0); } }
        fn main() { let _ = Noisy("a"); println!("after"); }
    """, "drop a\nafter"),
    ("drop: let _x = value keeps it to the end of the scope", r"""
        struct Noisy(&'static str);
        impl Drop for Noisy { fn drop(&mut self) { println!("drop {}", self.0); } }
        fn main() { let _x = Noisy("a"); println!("after"); }
    """, "after\ndrop a"),
    ("mem-swap: swap exchanges two variables", r"""let mut a = 1; let mut b = 2; std::mem::swap(&mut a, &mut b); println!("{} {}", a, b);""", "2 1"),
    ("mem-swap: take leaves the default behind", r"""let mut o = Some(3); let t = std::mem::take(&mut o); println!("{:?} {:?}", o, t);""", "None Some(3)"),
    ("mem-swap: you cannot move out of a &mut without them", r"""
        fn f(s: &mut String) -> String { *s }
        fn main() { let mut s = String::new(); println!("{}", f(&mut s)); }
    """, "CE"),
    ("mem-swap: v.swap(i, j) exchanges two positions", r"""let mut v = vec![1, 2, 3]; v.swap(0, 2); println!("{:?}", v);""", "[3, 2, 1]"),
    ("mem-swap: replace leaves the new value", r"""let mut s = String::from("a"); let old = std::mem::replace(&mut s, String::from("b")); println!("{} {}", old, s);""", "a b"),
    ("mem-swap: take on a String leaves it empty", r"""let mut s = String::from("a"); let t = std::mem::take(&mut s); println!("[{}] [{}]", s, t);""", "[] [a]"),
    ("unsafe: following a raw pointer needs unsafe", r"""let x = 5; let p = &x as *const i32; println!("{}", *p);""", "CE"),
    ("unsafe: inside unsafe the pointer can be followed", r"""let x = 5; let p = &x as *const i32; let y = unsafe { *p }; println!("{}", y);""", "5"),
    ("unsafe: a static mut needs unsafe", r"""static mut N: i32 = 1; println!("{}", N);""", "CE"),
    ("unsafe: use after move is still an error inside unsafe", r"""unsafe { let s = String::new(); let t = s; println!("{} {}", s, t); }""", "CE"),
    # ── types: structs, enums, impl, traits, generics, derive ───────────
    ("struct: every field must be given a value", r"""
        struct P { x: i32, y: i32 }
        fn main() { let p = P { x: 1 }; println!("{}", p.x); }
    """, "CE"),
    ("struct: changing a field needs let mut", r"""
        struct P { x: i32 }
        fn main() { let p = P { x: 1 }; p.x = 5; println!("{}", p.x); }
    """, "CE"),
    ("struct: a variable with the field's name can be used as shorthand", r"""
        struct P { x: i32, y: i32 }
        fn main() { let x = 3; let y = 4; let p = P { x, y }; println!("{} {}", p.x, p.y); }
    """, "3 4"),
    ("struct: it has no == until you derive it", r"""
        struct P { x: i32 }
        fn main() { let a = P { x: 1 }; let b = P { x: 1 }; println!("{}", a == b); }
    """, "CE"),
    ("struct: ..other fills the rest", r"""
        struct P { x: i32, y: i32 }
        fn main() { let p = P { x: 1, y: 2 }; let q = P { x: 10, ..p }; println!("{} {}", q.x, q.y); }
    """, "10 2"),
    ("enum: a match must cover every variant", r"""
        enum C { R, G, B }
        fn main() { let c = C::R; match c { C::R => println!("r"), C::G => println!("g") } }
    """, "CE"),
    ("enum: a variant with no data casts to its position", r"""
        enum C { R, G, B }
        fn main() { println!("{}", C::G as i32); }
    """, "1"),
    ("enum: variants carry different data", r"""
        enum Shape { Circle(f64), Rect { w: f64, h: f64 }, Empty }
        fn area(s: &Shape) -> f64 { match s { Shape::Circle(r) => 3.0 * r * r, Shape::Rect { w, h } => w * h, Shape::Empty => 0.0 } }
        fn main() { println!("{} {} {}", area(&Shape::Circle(2.0)), area(&Shape::Rect { w: 2.0, h: 3.5 }), area(&Shape::Empty)); }
    """, "12 7 0"),
    ("enum: it has no == until you derive it", r"""
        enum C { R, G }
        fn main() { println!("{}", C::R == C::G); }
    """, "CE"),
    ("enum, option: Option is an ordinary enum", r"""let o: Option<i32> = Some(1); match o { Some(x) => println!("{}", x), None => println!("none") }""", "1"),
    ("impl: a type may have several impl blocks", r"""
        struct C { n: u32 }
        impl C { fn new() -> C { C { n: 1 } } }
        impl C { fn get(&self) -> u32 { self.n + 2 } }
        fn main() { println!("{}", C::new().get()); }
    """, "3"),
    ("impl: a trait impl must supply every required method", r"""
        trait T { fn a(&self) -> i32; fn b(&self) -> i32; }
        struct S;
        impl T for S { fn a(&self) -> i32 { 1 } }
        fn main() { println!("{}", S.a()); }
    """, "CE"),
    ("impl: a foreign trait cannot be implemented for a foreign type", r"""
        use std::fmt;
        impl fmt::Display for Vec<i32> { fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result { write!(f, "v") } }
        fn main() {}
    """, "CE"),
    ("impl, associated-function: Self means the type", r"""
        struct P { x: i32 }
        impl P { fn new() -> Self { Self { x: 7 } } }
        fn main() { println!("{}", P::new().x); }
    """, "7"),
    ("method: r.area() is Rect::area(&r)", r"""
        struct Rect { w: u32, h: u32 }
        impl Rect { fn area(&self) -> u32 { self.w * self.h } }
        fn main() { let r = Rect { w: 2, h: 3 }; println!("{} {}", r.area(), Rect::area(&r)); }
    """, "6 6"),
    ("method: &mut self needs a mut variable", r"""
        struct R { w: u32 }
        impl R { fn double(&mut self) { self.w *= 2; } }
        fn main() { let r = R { w: 2 }; r.double(); println!("{}", r.w); }
    """, "CE"),
    ("method: a method taking self uses the value up", r"""
        struct R { w: u32 }
        impl R { fn consume(self) -> u32 { self.w } fn get(&self) -> u32 { self.w } }
        fn main() { let r = R { w: 2 }; println!("{}", r.consume()); println!("{}", r.get()); }
    """, "CE"),
    ("method: &mut self changes the fields", r"""
        struct R { w: u32, h: u32 }
        impl R { fn area(&self) -> u32 { self.w * self.h } fn double(&mut self) { self.w *= 2; self.h *= 2; } }
        fn main() { let mut r = R { w: 2, h: 3 }; r.double(); println!("{}", r.area()); }
    """, "24"),
    ("self-parameter: &self cannot change fields", r"""
        struct T { n: u32 }
        impl T { fn bump(&self) { self.n += 1; } }
        fn main() { let t = T { n: 1 }; t.bump(); println!("{}", t.n); }
    """, "CE"),
    ("self-parameter: self by value moves the value in", r"""
        struct T { l: u32 }
        impl T { fn empty(self) -> u32 { self.l } }
        fn main() { let t = T { l: 5 }; let a = t.empty(); println!("{} {}", a, t.l); }
    """, "CE"),
    ("self-parameter: &self, &mut self and Self together", r"""
        struct Tank { litres: u32 }
        impl Tank {
            fn level(&self) -> u32 { self.litres }
            fn fill(&mut self, n: u32) { self.litres += n; }
            fn empty(self) -> u32 { self.litres }
            fn full() -> Self { Self { litres: 100 } }
        }
        fn main() { let mut t = Tank::full(); t.fill(5); println!("{}", t.level()); println!("{}", t.empty()); }
    """, "105\n105"),
    ("associated-function: it is called with ::, not with a dot", r"""
        struct P { x: i32 }
        impl P { fn new(x: i32) -> P { P { x } } }
        fn main() { let p = P::new(1); let q = p.new(2); println!("{}", q.x); }
    """, "CE"),
    ("associated-function: any name works, not just new", r"""
        struct P { x: i32 }
        impl P { fn origin() -> P { P { x: 0 } } }
        fn main() { println!("{}", P::origin().x); }
    """, "0"),
    ("associated-function: String::from, Vec::new and Box::new are associated functions", r"""println!("{} {} {}", String::from("a"), Vec::<i32>::new().len(), Box::new(3));""", "a 0 3"),
    ("associated-function: an impl can hold a constant", r"""
        struct S;
        impl S { const N: i32 = 5; }
        fn main() { println!("{}", S::N); }
    """, "5"),
    ("trait: a trait impl must write every method without a default", r"""
        trait Speak { fn name(&self) -> String; fn speak(&self) -> String; }
        struct Dog;
        impl Speak for Dog { fn name(&self) -> String { "Dog".to_string() } }
        fn main() { println!("{}", Dog.name()); }
    """, "CE"),
    ("trait: a default method is used unless the impl overrides it", r"""
        trait Speak {
            fn name(&self) -> String;
            fn speak(&self) -> String { format!("{} makes a sound", self.name()) }
        }
        struct Dog;
        struct Cat;
        impl Speak for Dog { fn name(&self) -> String { "Dog".to_string() } }
        impl Speak for Cat { fn name(&self) -> String { "Cat".to_string() } fn speak(&self) -> String { "Cat purrs".to_string() } }
        fn main() { println!("{}", Dog.speak()); println!("{}", Cat.speak()); }
    """, "Dog makes a sound\nCat purrs"),
    ("trait: its methods need the trait in scope", r"""
        mod m { pub trait T { fn hi(&self) -> i32 { 1 } } impl T for i32 {} }
        fn main() { println!("{}", 5i32.hi()); }
    """, "CE"),
    ("trait: you can implement your own trait for a built-in type", r"""
        trait Double { fn double(&self) -> i32; }
        impl Double for i32 { fn double(&self) -> i32 { self * 2 } }
        fn main() { println!("{}", 4i32.double()); }
    """, "8"),
    ("trait-object: a Vec of one type cannot hold two", r"""
        trait Shape { fn area(&self) -> f64; }
        struct Sq(f64);
        struct Circle(f64);
        impl Shape for Sq { fn area(&self) -> f64 { self.0 } }
        impl Shape for Circle { fn area(&self) -> f64 { self.0 } }
        fn main() { let v = vec![Sq(1.0), Circle(1.0)]; println!("{}", v.len()); }
    """, "CE"),
    ("trait-object: Vec<Box<dyn Shape>> holds both", r"""
        trait Shape { fn area(&self) -> f64; }
        struct Sq(f64);
        struct Circle(f64);
        impl Shape for Sq { fn area(&self) -> f64 { self.0 * self.0 } }
        impl Shape for Circle { fn area(&self) -> f64 { 3.0 * self.0 * self.0 } }
        fn main() {
            let shapes: Vec<Box<dyn Shape>> = vec![Box::new(Sq(2.0)), Box::new(Circle(1.0))];
            let total: f64 = shapes.iter().map(|s| s.area()).sum();
            println!("{}", total);
        }
    """, "7"),
    ("trait-object: dyn needs a pointer", r"""
        trait Shape { fn area(&self) -> f64; }
        fn main() { let v: Vec<dyn Shape> = Vec::new(); println!("{}", v.len()); }
    """, "CE"),
    ("trait-object: a trait with a function returning Self cannot be dyn", r"""
        trait T { fn make() -> Self; }
        fn f(_: &dyn T) {}
        fn main() {}
    """, "CE"),
    ("generic: both fields of Pair<T> have the same T", r"""
        struct Pair<T> { a: T, b: T }
        fn main() { let p = Pair { a: 1, b: 2.5 }; println!("{}", p.a); }
    """, "CE"),
    ("generic: a > b on a bare T is an error", r"""
        fn big<T>(a: T, b: T) -> bool { a > b }
        fn main() { println!("{}", big(1, 2)); }
    """, "CE"),
    ("generic: an unused Vec::new() has no type", r"""let v = Vec::new(); println!("{}", 1);""", "CE"),
    ("generic: T is filled in per use", r"""
        struct Pair<T> { a: T, b: T }
        impl<T: PartialOrd + Copy> Pair<T> { fn larger(&self) -> T { if self.a > self.b { self.a } else { self.b } } }
        fn first<T>(items: &[T]) -> &T { &items[0] }
        fn main() {
            println!("{} {}", Pair { a: 3, b: 9 }.larger(), Pair { a: 2.5, b: 1.5 }.larger());
            println!("{}", first(&["x", "y"]));
        }
    """, "9 2.5\nx"),
    ("trait-bound: println! of a bare T needs T: Display", r"""
        fn show<T>(x: T) { println!("{}", x); }
        fn main() { show(1); }
    """, "CE"),
    ("trait-bound: a type without the trait is refused", r"""
        use std::fmt::Display;
        fn show_twice<T: Display>(x: T) -> String { format!("{x} {x}") }
        fn main() { println!("{}", show_twice(vec![1])); }
    """, "CE"),
    ("trait-bound: + combines bounds", r"""
        fn f<T: Clone + std::fmt::Debug>(x: T) -> String { format!("{:?}", x.clone()) }
        fn main() { println!("{}", f(vec![1])); }
    """, "[1]"),
    ("trait-bound: impl Display as a parameter type is shorthand", r"""
        fn f(x: impl std::fmt::Display) -> String { x.to_string() }
        fn main() { println!("{}", f(5)); }
    """, "5"),
    ("trait-bound: a where clause means the same", r"""
        fn f<T>(x: T) -> String where T: std::fmt::Display { x.to_string() }
        fn main() { println!("{}", f(2)); }
    """, "2"),
    ("derive: every field must have the derived trait", r"""
        struct NoClone;
        #[derive(Clone)]
        struct S { n: NoClone }
        fn main() { let _s = S { n: NoClone }; }
    """, "CE"),
    ("derive: a derived PartialOrd compares fields first to last", r"""
        #[derive(PartialEq, PartialOrd)]
        struct V(i32, i32);
        fn main() { println!("{}", V(1, 9) < V(2, 0)); }
    """, "true"),
    ("derive: Eq cannot be derived with an f64 field", r"""
        #[derive(PartialEq, Eq)]
        struct F(f64);
        fn main() { let _f = F(1.0); }
    """, "CE"),
    ("derive: Copy needs Clone", r"""
        #[derive(Copy)]
        struct S;
        fn main() { let _s = S; }
    """, "CE"),
    ("derive, default-trait: derive makes Clone, PartialEq and Default", r"""
        #[derive(Debug, Clone, PartialEq, Default)]
        struct Config { name: String, retries: u32 }
        fn main() {
            let a = Config { name: String::from("x"), retries: 3 };
            let b = a.clone();
            println!("{} {:?}", a == b, Config::default());
        }
    """, 'true Config { name: "", retries: 0 }'),
    ("partial-eq: == needs PartialEq", r"""
        struct P { x: i32 }
        fn main() { println!("{}", P { x: 1 } == P { x: 1 }); }
    """, "CE"),
    ("partial-eq: a derived == compares every field", r"""
        #[derive(PartialEq)]
        struct P { x: i32, y: i32 }
        fn main() { println!("{} {}", P { x: 1, y: 2 } == P { x: 1, y: 2 }, P { x: 1, y: 2 } == P { x: 1, y: 3 }); }
    """, "true false"),
    ("partial-eq: different types do not compare", r"""println!("{}", 1 == 1.0);""", "CE"),
    ("partial-eq: &a == &b compares the values", r"""let a = String::from("x"); let b = String::from("x"); println!("{}", &a == &b);""", "true"),
    ("partial-eq, hashset: an f64 cannot be a set member", r"""let mut s = std::collections::HashSet::new(); s.insert(1.5_f64);""", "CE"),
    ("partial-ord: an enum orders by variant position", r"""
        #[derive(PartialEq, PartialOrd)]
        enum Rank { Low, Mid, High }
        fn main() { println!("{} {}", Rank::Low < Rank::High, Rank::High < Rank::Mid); }
    """, "true false"),
    ("partial-ord: f64 partial_cmp is None with a NaN", r"""println!("{:?} {:?}", 2.5_f64.partial_cmp(&1.0), f64::NAN.partial_cmp(&1.0));""", "Some(Greater) None"),
    ("partial-ord, sorting: floats sort with sort_by and partial_cmp", r"""let mut v = vec![2.5, 1.5, 3.0]; v.sort_by(|a, b| a.partial_cmp(b).unwrap()); println!("{:?}", v);""", "[1.5, 2.5, 3.0]"),
    ("partial-ord: cmp gives an Ordering", r"""println!("{:?} {:?} {:?}", 3i32.cmp(&5), 5i32.cmp(&5), 7i32.cmp(&5));""", "Less Equal Greater"),
    ("default-trait: the standard defaults", r"""println!("{} {} {:?} {:?} {:?}", i32::default(), bool::default(), String::default(), Vec::<i32>::default(), Option::<i32>::default());""", '0 false "" [] None'),
    ("default-trait: derive(Default) needs every field to have a Default", r"""
        struct NoDefault;
        #[derive(Default)]
        struct S { n: NoDefault }
        fn main() { let _s = S::default(); }
    """, "CE"),
    ("default-trait: ..Default::default() fills the rest", r"""
        #[derive(Debug, Default)]
        struct Settings { volume: u8, name: String, muted: bool }
        fn main() { println!("{:?}", Settings { volume: 7, ..Default::default() }); }
    """, 'Settings { volume: 7, name: "", muted: false }'),
    ("default-trait, unwrap: unwrap_or_default gives the default for None", r"""let n: Option<i32> = None; println!("{}", n.unwrap_or_default());""", "0"),
    # ── Option, Result, ?, patterns ─────────────────────────────────────
    ("option: an Option<i32> is not an i32", r"""let a: Option<i32> = Some(1); let b = a + 1; println!("{:?}", b);""", "CE"),
    ("option: Some(1) does not fit an i32 variable", r"""let x: i32 = Some(1); println!("{}", x);""", "CE"),
    ("option: map changes what is inside", r"""println!("{:?} {:?}", Some(2).map(|x| x + 1), None::<i32>.map(|x| x + 1));""", "Some(3) None"),
    ("option, error-handling: ok_or turns None into Err", r"""println!("{:?}", None::<i32>.ok_or("missing"));""", 'Err("missing")'),
    ("option: get returns an Option", r"""let v = vec![1]; println!("{:?} {:?}", v.get(0), v.get(3));""", "Some(1) None"),
    ("result: ending with a bare value is an error", r"""
        fn f() -> Result<i32, String> { 5 }
        fn main() { println!("{:?}", f()); }
    """, "CE"),
    ("result: parse gives Ok or Err", r"""println!("{:?} {}", "7".parse::<i32>(), "x".parse::<i32>().is_err());""", "Ok(7) true"),
    ("result: ok() and map_err change the Result", r"""let r: Result<i32, String> = Err("bad".to_string()); println!("{:?} {:?}", r.clone().ok(), r.map_err(|e| e.len()));""", "None Err(3)"),
    ("result: Ok and Err may hold different types", r"""
        fn half(n: i32) -> Result<i32, String> { if n % 2 == 0 { Ok(n / 2) } else { Err(format!("{} is odd", n)) } }
        fn main() { println!("{:?} {:?}", half(8), half(7)); }
    """, 'Ok(4) Err("7 is odd")'),
    ("question-mark: ? in a function returning () is an error", r"""let n: i32 = "5".parse()?; println!("{}", n);""", "CE"),
    ("question-mark: ? on an Option returns None early", r"""
        fn first_even(v: &[i32]) -> Option<i32> { let f = v.first()?; if f % 2 == 0 { Some(*f) } else { None } }
        fn main() { println!("{:?} {:?}", first_even(&[]), first_even(&[4])); }
    """, "None Some(4)"),
    ("question-mark: the error is converted into Box<dyn Error>", r"""
        fn f() -> Result<i32, Box<dyn std::error::Error>> { let n: i32 = "x".parse()?; Ok(n) }
        fn main() { println!("{}", f().is_err()); }
    """, "true"),
    ("question-mark: Option and Result do not mix", r"""
        fn f() -> Result<i32, String> { let x = Some(1)?; Ok(x) }
        fn main() { println!("{:?}", f()); }
    """, "CE"),
    ("question-mark: it passes an Err up", r"""
        fn add_strs(a: &str, b: &str) -> Result<i32, std::num::ParseIntError> { let x: i32 = a.parse()?; let y: i32 = b.parse()?; Ok(x + y) }
        fn main() { println!("{:?} {}", add_strs("2", "3"), add_strs("2", "z").is_err()); }
    """, "Ok(5) true"),
    ("unwrap: None.unwrap() panics", r"""let n: Option<i32> = None; println!("{}", n.unwrap());""", "PANIC"),
    ("unwrap: expect on an Err panics", r"""let r: Result<i32, String> = Err("x".to_string()); println!("{}", r.expect("it failed"));""", "PANIC"),
    ("unwrap: unwrap_or evaluates its argument but unwrap_or_else does not", r"""
        fn costly() -> i32 { println!("called"); 1 }
        fn main() { let a = Some(5).unwrap_or(costly()); let b = Some(5).unwrap_or_else(costly); println!("{} {}", a, b); }
    """, "called\n5 5"),
    ("unwrap: unwrap_or and unwrap_or_else give a fallback", r"""let none: Option<i32> = None; println!("{} {}", none.unwrap_or(0), none.unwrap_or_else(|| 40 + 2));""", "0 42"),
    ("error-handling: a function returning Result<(), String> can use ? and ends with Ok(())", r"""
        fn run() -> Result<(), String> {
            let v: i32 = "5".parse().map_err(|_| "bad".to_string())?;
            println!("{}", v);
            Ok(())
        }
        fn main() { run().unwrap(); }
    """, "5"),
    ("error-handling: a custom error works as Box<dyn Error>", r"""
        use std::fmt;
        #[derive(Debug)]
        struct E;
        impl fmt::Display for E { fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result { write!(f, "bad") } }
        impl std::error::Error for E {}
        fn f() -> Result<(), Box<dyn std::error::Error>> { Err(Box::new(E)) }
        fn main() { println!("{}", f().unwrap_err()); }
    """, "bad"),
    ("error-handling: map_err converts the error type", r"""
        #[derive(Debug)]
        enum AgeError { NotANumber, TooBig(u32) }
        fn parse_age(s: &str) -> Result<u32, AgeError> {
            let n: u32 = s.parse().map_err(|_| AgeError::NotANumber)?;
            if n > 150 { Err(AgeError::TooBig(n)) } else { Ok(n) }
        }
        fn main() { for s in ["42", "abc", "200"] { println!("{:?}", parse_age(s)); } }
    """, "Ok(42)\nErr(NotANumber)\nErr(TooBig(200))"),
    ("error-handling: an Err that nobody looks at is not a crash", r"""let r: Result<i32, String> = Err("x".to_string()); let _ = r; println!("still running");""", "still running"),
    ("match: an integer match needs a catch-all", r"""let n = 3; match n { 0 => println!("a"), 1 => println!("b") }""", "CE"),
    ("match: the first arm that fits wins", r"""let r = match 3 { 1..=5 => "a", 3 => "b", _ => "c" }; println!("{}", r);""", "a"),
    ("match: the arms must give the same type", r"""let x = match 1 { 1 => "a", _ => 2 }; println!("{}", x);""", "CE"),
    ("match, pattern: name @ pattern binds the matched value", r"""let r = match 5 { n @ 1..=9 => n * 2, _ => 0 }; println!("{}", r);""", "10"),
    ("match: a String cannot be matched against literals", r"""let s = String::from("a"); let r = match s { "a" => 1, _ => 0 }; println!("{}", r);""", "CE"),
    ("match: as_str makes a String matchable", r"""let s = String::from("a"); let r = match s.as_str() { "a" => 1, _ => 0 }; println!("{}", r);""", "1"),
    ("match: ranges and | in one match", r"""let n = 7; let w = match n { 0 => "zero", 1..=5 => "small", 6 | 7 => "six or seven", _ => "big" }; println!("{}", w);""", "six or seven"),
    ("pattern: a refutable pattern in a plain let is an error", r"""let o = Some(1); let Some(x) = o; println!("{}", x);""", "CE"),
    ("pattern: tuples, structs and arrays are taken apart", r"""
        struct P { x: i32, y: i32 }
        fn main() {
            let (a, b) = (1, 2);
            let P { x, .. } = P { x: 10, y: 20 };
            let [first, .., last] = [1, 2, 3, 4];
            println!("{} {} {} {} {}", a, b, x, first, last);
        }
    """, "1 2 10 1 4"),
    ("pattern: a char range matches", r"""let r = match 'k' { 'a'..='m' => 1, _ => 2 }; println!("{}", r);""", "1"),
    ("pattern: patterns nest", r"""let o = Some((1, 2)); if let Some((a, b)) = o { println!("{}", a + b); }""", "3"),
    ("pattern: a | b matches either", r"""let r = match 2 { 1 | 2 => "low", _ => "high" }; println!("{}", r);""", "low"),
    ("match-guard: a false guard falls to the next arm", r"""
        for n in [Some(1), Some(8), None] {
            let text = match n { Some(x) if x > 5 => "big", Some(_) => "small", None => "none" };
            println!("{}", text);
        }
    """, "small\nbig\nnone"),
    ("match-guard: guarded arms still need a catch-all", r"""let n = 3; let r = match n { x if x > 0 => 1, x if x <= 0 => 2 }; println!("{}", r);""", "CE"),
    ("match-guard: the guard is tested for every alternative", r"""let n = 1; let r = match n { 1 | 2 if n > 1 => "a", _ => "b" }; println!("{}", r);""", "b"),
    ("if-let: values that do not fit are skipped", r"""if let Some(x) = None::<i32> { println!("{}", x); } println!("done");""", "done"),
    ("if-let: else runs when the pattern does not fit", r"""let r: Result<i32, String> = Err("no".to_string()); if let Ok(n) = r { println!("{}", n); } else { println!("failed"); }""", "failed"),
    ("if-let: the names exist only inside the block", r"""if let Some(x) = Some(1) { println!("{}", x); } println!("{}", x);""", "CE"),
    ("if-let: it moves a String out of the Option", r"""let o = Some(String::from("a")); if let Some(s) = o { println!("{}", s); } println!("{:?}", o);""", "CE"),
    ("if-let: matching &o keeps the Option usable", r"""let o = Some(String::from("a")); if let Some(s) = &o { println!("{}", s); } println!("{:?}", o);""", 'a\nSome("a")'),
    ("while-let: it pops last to first and leaves the Vec empty", r"""let mut stack = vec![1, 2, 3]; while let Some(top) = stack.pop() { println!("{}", top); } println!("{}", stack.len());""", "3\n2\n1\n0"),
    ("while-let: it drives an iterator by hand", r"""let v = vec![1, 2, 3]; let mut it = v.iter(); let mut s = 0; while let Some(x) = it.next() { s += x; } println!("{}", s);""", "6"),
    ("let-else: the else block must not fall through", r"""let Some(x) = Some(1) else { println!("no"); }; println!("{}", x);""", "CE"),
    ("let-else: the names are usable after the statement", r"""let Some(x) = Some(3) else { return; }; println!("{}", x);""", "3"),
    ("let-else: the else block runs when the pattern does not fit", r"""
        fn first_word_len(s: &str) -> usize {
            let Some(word) = s.split_whitespace().next() else { return 0; };
            word.len()
        }
        fn main() { println!("{} {}", first_word_len("hello world"), first_word_len("   ")); }
    """, "5 0"),
    # ── text and collections ────────────────────────────────────────────
    ("string: a literal is a &str, not a String", r"""let s: String = "hi"; println!("{}", s);""", "CE"),
    ("string: s1 + &s2 moves s1", r"""let a = String::from("x"); let b = String::from("y"); let c = a + &b; println!("{} {}", a, c);""", "CE"),
    ("string: a slice must fall on a character boundary", r"""let s = "\u{e9}a"; let t = &s[0..1]; println!("{}", t);""", "PANIC"),
    ("string: a function taking &str accepts &String", r"""
        fn len(s: &str) -> usize { s.len() }
        fn main() { println!("{}", len(&String::from("abc"))); }
    """, "3"),
    ("string: chars().rev().collect() reverses", r"""let r: String = "abc".chars().rev().collect(); println!("{}", r);""", "cba"),
    ("string: a string cannot be indexed by position", r"""let s = String::from("abc"); println!("{}", s[1]);""", "CE"),
    ("string: push_str and to_uppercase", r"""let mut s = String::from("hello"); s.push_str(", world"); s.push('!'); println!("{} {}", s, s.to_uppercase());""", "hello, world! HELLO, WORLD!"),
    ("string-from: all the ways give equal Strings", r"""let a = String::from("hi"); let b = "hi".to_string(); let c = "hi".to_owned(); let d: String = "hi".into(); println!("{}", a == b && b == c && c == d);""", "true"),
    ("string-from: String::new() is empty", r"""println!("{}", String::new().len());""", "0"),
    ("string-from: a String compares with a &str", r"""let s = String::from("a"); println!("{}", s == "a");""", "true"),
    ("string-from: to_string works on anything with Display", r"""println!("{}", 5.to_string() + "x");""", "5x"),
    ("string-from: a &str cannot grow", r"""let s = "hi"; s.push('!'); println!("{}", s);""", "CE"),
    ("vector: all items have the same type", r"""let v = vec![1, "a"]; println!("{}", v.len());""", "CE"),
    ("vector: get past the end is None", r"""let v = vec![1, 2, 3]; println!("{:?}", v.get(3));""", "None"),
    ("vector: indexing at len panics", r"""let v = vec![1, 2, 3]; let i = v.len(); println!("{}", v[i]);""", "PANIC"),
    ("vector: push needs let mut", r"""let v = vec![1]; v.push(2); println!("{:?}", v);""", "CE"),
    ("vector: a Vec moves like any owner", r"""let v = vec![1]; let w = v; println!("{} {}", v.len(), w.len());""", "CE"),
    ("vector: vec![0; 3] makes three zeros", r"""println!("{:?}", vec![0; 3]);""", "[0, 0, 0]"),
    ("vector: push and pop at the end", r"""let mut v = vec![10, 20, 30]; v.push(40); let last = v.pop(); println!("{:?} {:?} {} {}", v, last, v[1], v.len());""", "[10, 20, 30] Some(40) 20 3"),
    ("vec-methods: pop gives an Option", r"""let mut v = vec![1]; println!("{:?} {:?} {}", v.pop(), v.pop(), v.len());""", "Some(1) None 0"),
    ("vec-methods: remove past the end panics", r"""let mut v = vec![1, 2, 3]; let i = v.len() + 2; v.remove(i);""", "PANIC"),
    ("vec-methods: insert, remove, retain and extend together", r"""let mut v = vec![1, 2, 3, 4, 5, 6]; v.insert(0, 9); let removed = v.remove(1); v.retain(|x| x % 2 == 0); v.extend([7, 8]); println!("{:?} {} {}", v, removed, v.contains(&7));""", "[2, 4, 6, 7, 8] 1 true"),
    ("vec-methods: contains takes a reference", r"""let v = vec![7]; println!("{}", v.contains(7));""", "CE"),
    ("vec-methods: dedup removes only neighbouring duplicates", r"""let mut v = vec![1, 1, 2, 1]; v.dedup(); println!("{:?}", v);""", "[1, 2, 1]"),
    ("vec-methods: truncate keeps the first n", r"""let mut v = vec![1, 2, 3]; v.truncate(2); println!("{:?}", v);""", "[1, 2]"),
    ("hashmap: insert returns the old value", r"""use std::collections::HashMap; let mut m = HashMap::new(); m.insert(1, "a"); println!("{:?}", m.insert(1, "b"));""", 'Some("a")'),
    ("hashmap: m[&key] panics when the key is missing", r"""use std::collections::HashMap; let mut m: HashMap<i32, i32> = HashMap::new(); m.insert(1, 2); let k = 5; println!("{}", m[&k]);""", "PANIC"),
    ("hashmap: entry().or_insert() counts", r"""use std::collections::HashMap; let mut counts = HashMap::new(); for c in "abca".chars() { *counts.entry(c).or_insert(0) += 1; } println!("{} {}", counts[&'a'], counts[&'b']);""", "2 1"),
    ("hashmap: sort the keys for a fixed order", r"""use std::collections::HashMap; let mut m = HashMap::new(); m.insert(3, 'c'); m.insert(1, 'a'); m.insert(2, 'b'); let mut keys: Vec<_> = m.keys().collect(); keys.sort(); println!("{:?}", keys);""", "[1, 2, 3]"),
    ("hashmap: insert moves a String key", r"""use std::collections::HashMap; let k = String::from("a"); let mut m = HashMap::new(); m.insert(k, 1); println!("{} {}", k, m.len());""", "CE"),
    ("hashmap: get and len", r"""use std::collections::HashMap; let mut stock: HashMap<&str, i32> = HashMap::new(); stock.insert("apple", 3); stock.insert("apple", 5); *stock.entry("pear").or_insert(0) += 2; println!("{:?} {:?} {}", stock.get("apple"), stock.get("kiwi"), stock.len());""", "Some(5) None 2"),
    ("btreemap: it prints in key order", r"""use std::collections::BTreeMap; let mut m = BTreeMap::new(); m.insert(3, "c"); m.insert(1, "a"); m.insert(2, "b"); println!("{:?}", m);""", '{1: "a", 2: "b", 3: "c"}'),
    ("btreemap: keys need Ord, so an f64 is refused", r"""use std::collections::BTreeMap; let mut m = BTreeMap::new(); m.insert(1.5_f64, 1);""", "CE"),
    ("btreemap: first, last and range", r"""use std::collections::BTreeMap; let mut m = BTreeMap::new(); m.insert(3, "c"); m.insert(1, "a"); m.insert(2, "b"); println!("{:?} {:?} {}", m.first_key_value(), m.last_key_value(), m.range(2..).count());""", 'Some((1, "a")) Some((3, "c")) 2'),
    ("btreemap: entry counts as in a HashMap", r"""use std::collections::BTreeMap; let mut m = BTreeMap::new(); for c in "bab".chars() { *m.entry(c).or_insert(0) += 1; } println!("{:?}", m);""", "{'a': 1, 'b': 2}"),
    ("hashset: insert says whether the value was new", r"""use std::collections::HashSet; let mut s = HashSet::new(); println!("{} {}", s.insert(1), s.insert(1));""", "true false"),
    ("hashset: duplicates collapse", r"""use std::collections::HashSet; let s: HashSet<i32> = [3, 1, 3, 2, 1].into_iter().collect(); println!("{}", s.len());""", "3"),
    ("hashset: intersection and union", r"""use std::collections::HashSet; let a: HashSet<i32> = [1, 2, 3].into(); let b: HashSet<i32> = [2, 3, 4].into(); println!("{} {}", a.intersection(&b).count(), a.union(&b).count());""", "2 4"),
    ("hashset: sort before printing", r"""use std::collections::HashSet; let s: HashSet<i32> = [3, 1, 2].into(); let mut v: Vec<_> = s.into_iter().collect(); v.sort(); println!("{:?}", v);""", "[1, 2, 3]"),
    ("btreeset: sorted and unique", r"""use std::collections::BTreeSet; let s: BTreeSet<i32> = [5, 1, 3, 1].into_iter().collect(); println!("{:?}", s);""", "{1, 3, 5}"),
    ("btreeset: first, last and range", r"""use std::collections::BTreeSet; let s: BTreeSet<i32> = [5, 1, 3].into_iter().collect(); println!("{:?} {:?} {:?}", s.first(), s.last(), s.range(2..).collect::<Vec<_>>());""", "Some(1) Some(5) [3, 5]"),
    ("btreeset: an f64 is refused", r"""use std::collections::BTreeSet; let mut s = BTreeSet::new(); s.insert(1.5_f64);""", "CE"),
    ("deque: push_back then pop_front is first in, first out", r"""use std::collections::VecDeque; let mut q = VecDeque::new(); q.push_back(1); q.push_back(2); q.push_back(3); println!("{:?} {:?}", q.pop_front(), q.pop_front());""", "Some(1) Some(2)"),
    ("deque: it prints like a list and indexes by position", r"""use std::collections::VecDeque; let mut q = VecDeque::new(); q.push_back(1); q.push_front(0); println!("{:?} {}", q, q[1]);""", "[0, 1] 1"),
    ("deque: pop on an empty queue is None", r"""use std::collections::VecDeque; let mut q: VecDeque<i32> = VecDeque::new(); println!("{:?} {:?}", q.pop_front(), q.pop_back());""", "None None"),
    ("deque: it converts to and from a Vec", r"""use std::collections::VecDeque; let q = VecDeque::from(vec![1, 2]); let v = Vec::from(q); println!("{:?}", v);""", "[1, 2]"),
    ("slice: the range forms", r"""let v = vec![1, 2, 3, 4]; println!("{:?} {:?} {:?}", &v[1..3], &v[..2], &v[2..]);""", "[2, 3] [1, 2] [3, 4]"),
    ("slice: a range past the end panics", r"""let v = vec![1, 2, 3]; let n = v.len() + 2; let s = &v[1..n]; println!("{:?}", s);""", "PANIC"),
    ("slice: a slice borrows the Vec", r"""let mut v = vec![1, 2, 3]; let s = &v[..2]; v.push(4); println!("{:?}", s);""", "CE"),
    ("slice: &[i32] accepts a Vec and an array", r"""
        fn sum(xs: &[i32]) -> i32 { xs.iter().sum() }
        fn main() { println!("{}", sum(&vec![1, 2]) + sum(&[3, 4])); }
    """, "10"),
    ("slice: chunks splits into pieces", r"""println!("{:?}", [1, 2, 3, 4, 5].chunks(2).collect::<Vec<_>>());""", "[[1, 2], [3, 4], [5]]"),
    ("slice: a string slice", r"""let s = "hello world"; println!("{}", &s[6..]);""", "world"),
    ("range: 1..4 leaves out 4 and 1..=4 includes it", r"""let a: Vec<i32> = (1..4).collect(); let b: Vec<i32> = (1..=4).collect(); println!("{:?} {:?}", a, b);""", "[1, 2, 3] [1, 2, 3, 4]"),
    ("range: a backwards range is empty", r"""println!("{} {} {:?}", (1..1).count(), (5..1).count(), (1..5).rev().collect::<Vec<_>>());""", "0 0 [4, 3, 2, 1]"),
    ("range: characters work", r"""let s: String = ('a'..='e').collect(); println!("{}", s);""", "abcde"),
    ("range: step_by takes every nth", r"""let c: Vec<i32> = (0..10).step_by(5).collect(); println!("{:?}", c);""", "[0, 5]"),
    ("range: contains", r"""println!("{} {}", (1..4).contains(&4), (1..=4).contains(&4));""", "false true"),
    ("iterator: iter_mut lends the items for changing", r"""let mut v = vec![1, 2]; for x in v.iter_mut() { *x *= 10; } println!("{:?}", v);""", "[10, 20]"),
    ("iterator: into_iter on a Vec uses it up", r"""let v = vec![1]; let w: Vec<i32> = v.into_iter().collect(); println!("{} {}", w.len(), v.len());""", "CE"),
    ("iterator: next needs the iterator to be mut", r"""let it = vec![1].into_iter(); println!("{:?}", it.next());""", "CE"),
    ("iterator: a consuming call uses it up", r"""let it = vec![1, 2].into_iter(); let a = it.count(); let b = it.count(); println!("{} {}", a, b);""", "CE"),
    ("iterator: next gives Some then None", r"""let v = vec![10, 20]; let mut it = v.iter(); println!("{:?} {:?} {:?}", it.next(), it.next(), it.next());""", "Some(10) Some(20) None"),
    ("adaptor: filter and map", r"""let v = vec![1, 2, 3, 4, 5, 6]; let out: Vec<i32> = v.iter().filter(|x| *x % 2 == 0).map(|x| x * 10).collect(); println!("{:?}", out);""", "[20, 40, 60]"),
    ("adaptor: zip stops at the shorter side", r"""let a = [1, 2, 3]; let b = [10, 20]; println!("{}", a.iter().zip(b.iter()).count());""", "2"),
    ("adaptor: skip and take", r"""let v: Vec<i32> = (1..10).skip(2).take(3).collect(); println!("{:?}", v);""", "[3, 4, 5]"),
    ("adaptor: filter_map keeps the Some results", r"""let v: Vec<i32> = ["1", "x", "3"].iter().filter_map(|s| s.parse::<i32>().ok()).collect(); println!("{:?}", v);""", "[1, 3]"),
    ("adaptor: windows(2) gives the gaps", r"""let v: Vec<i32> = [1, 3, 6].windows(2).map(|w| w[1] - w[0]).collect(); println!("{:?}", v);""", "[2, 3]"),
    ("adaptor: enumerate counts from 0 and zip pairs", r"""let pairs: Vec<(usize, char)> = "abc".chars().enumerate().collect(); let sums: Vec<i32> = [1, 2, 3].iter().zip([10, 20, 30].iter()).map(|(a, b)| a + b).collect(); println!("{:?} {:?}", pairs, sums);""", "[(0, 'a'), (1, 'b'), (2, 'c')] [11, 22, 33]"),
    ("collect: it needs a type", r"""let v = (1..3).collect(); println!("{}", 1);""", "CE"),
    ("collect: a Result collection stops at the first Err", r"""let r: Result<Vec<i32>, _> = ["1", "x", "3"].iter().map(|s| s.parse::<i32>()).collect(); println!("{}", r.is_err());""", "true"),
    ("collect: an Option collection is None if any item is None", r"""let o: Option<Vec<i32>> = vec![Some(1), None].into_iter().collect(); println!("{:?}", o);""", "None"),
    ("collect: chars collect into a String", r"""let word: String = vec!['r', 'u', 's', 't'].into_iter().collect(); println!("{}", word);""", "rust"),
    ("collect: a HashSet drops duplicates", r"""use std::collections::HashSet; let s: HashSet<i32> = vec![1, 1, 2].into_iter().collect(); println!("{}", s.len());""", "2"),
    ("collect: pairs collect into a HashMap", r"""use std::collections::HashMap; let m: HashMap<_, _> = vec![("a", 1), ("b", 2)].into_iter().collect(); println!("{}", m["b"]);""", "2"),
    ("fold: sum needs the result type named", r"""let v = vec![1, 2]; let s = v.iter().sum(); println!("{}", s);""", "CE"),
    ("fold: the start value fixes the result type", r"""let t = [1.5, 2.5].iter().fold(0.0, |a, x| a + x); println!("{}", t);""", "4"),
    ("fold: an empty iterator sums to 0 and multiplies to 1", r"""let e: Vec<i32> = vec![]; println!("{} {}", e.iter().sum::<i32>(), e.iter().product::<i32>());""", "0 1"),
    ("fold: reduce gives an Option", r"""println!("{:?} {:?}", vec![1, 2, 3].into_iter().reduce(|a, b| a.max(b)), Vec::<i32>::new().into_iter().reduce(|a, b| a + b));""", "Some(3) None"),
    ("fold: fold, sum and product together", r"""let v = vec![1, 2, 3, 4]; let total = v.iter().fold(0, |acc, x| acc + x); let p: i32 = v.iter().product(); let text = v.iter().fold(String::new(), |acc, x| acc + &x.to_string()); println!("{} {} {}", total, p, text);""", "10 24 1234"),
    ("lazy-evaluation, adaptor: an unconsumed map runs nothing", r"""let v = vec![1, 2]; let _m = v.iter().map(|x| println!("{}", x)); println!("done");""", "done"),
    ("lazy-evaluation: find pulls only as many items as it needs", r"""let mut calls = 0; let first = (1..100).map(|x| { calls += 1; x * x }).find(|x| *x > 10); println!("{:?} {}", first, calls);""", "Some(16) 4"),
    ("lazy-evaluation: an endless range is fine", r"""let v: Vec<u32> = (1..).take(3).collect(); println!("{:?}", v);""", "[1, 2, 3]"),
    ("lazy-evaluation: a pipeline pulls item by item", r"""
        let v = vec![1, 2, 3, 4];
        let pipeline = v.iter().map(|x| { println!("map {}", x); x * 2 });
        println!("built");
        let first_big = pipeline.filter(|x| *x > 2).next();
        println!("{:?}", first_big);
    """, "built\nmap 1\nmap 2\nSome(4)"),
    ("sorting: sort returns ()", r"""let mut v = vec![2, 1]; let r = v.sort(); println!("{:?} {:?}", r, v);""", "() [1, 2]"),
    ("sorting: the Vec must be mut", r"""let v = vec![2, 1]; v.sort(); println!("{:?}", v);""", "CE"),
    ("sorting: the sort is stable", r"""let mut w = vec!["bb", "a", "cc", "d"]; w.sort_by_key(|s| s.len()); println!("{:?}", w);""", r'["a", "d", "bb", "cc"]'),
    ("sorting: descending with Reverse", r"""use std::cmp::Reverse; let mut v = vec![2, 3, 1]; v.sort_by_key(|x| Reverse(*x)); println!("{:?}", v);""", "[3, 2, 1]"),
    ("sorting: there is no sorted()", r"""let v = vec![2, 1]; let s = v.sorted(); println!("{:?}", s);""", "CE"),
    ("sorting: sort and sort_by", r"""let mut v = vec![3, 1, 2]; v.sort(); println!("{:?}", v); v.sort_by(|a, b| b.cmp(a)); println!("{:?}", v);""", "[1, 2, 3]\n[3, 2, 1]"),
    ("collection: every collection has len and is_empty", r"""let a = vec![1, 2]; let s = std::collections::HashSet::<i32>::new(); let q = std::collections::VecDeque::<i32>::new(); println!("{} {} {}", a.len(), s.is_empty(), q.len());""", "2 true 0"),
    ("collection: a Vec keeps duplicates and a set drops them", r"""let list = vec![3, 1, 3]; let set: std::collections::BTreeSet<i32> = list.iter().cloned().collect(); println!("{} {}", list.len(), set.len());""", "3 2"),
    ("collection: a collection owns what you put in", r"""let s = String::from("a"); let v = vec![s]; println!("{} {}", s, v.len());""", "CE"),
]

#: Words whose rules a program cannot show on its own. Nothing is listed: every Rust word has at least one check.
RUST_NOT_ORACLE_CHECKED: set[str] = set()
