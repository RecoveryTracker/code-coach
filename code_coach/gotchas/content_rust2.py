"""Gotchas, Rust, the second helping: casts, iterators, formatting and the order things are dropped.

Same rules as content_rust.py: edition 2021, rustc -O, one println! line, no HashMap/HashSet, no raw pointers or
layout, no threads, no clock. Overflow is spelled out with wrapping_/checked_/saturating_ so the answer does not
depend on the build mode, and anything that would panic is avoided (a card prints, it does not crash).
"""

from __future__ import annotations

from .items import Item, make

q = make("rust")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking: basics with a real trap ──────────────────────────────
    q("division-and-euclid", r'''
        fn main() {
            let a = -7i32;
            println!("{} {} {} {}", a / 2, a % 3, a.rem_euclid(3), a.div_euclid(2));
        }
    ''', "-3 -1 2 -4", ["-4 2 2 -4", "-3 2 2 -3", "-4 -1 -1 -3"],
      "/ and % truncate toward zero; rem_euclid and div_euclid round down",
      """Integer division cuts toward zero, so -7 / 2 is -3 and -7 % 3 keeps the sign of the dividend: -1. The
      Euclidean versions keep the remainder non-negative, which pairs it with a quotient of -4 and a remainder
      of 2."""),

    q("as-saturates-floats", r'''
        fn main() {
            let big = 300.7f64;
            let neg = -5.0f64;
            let nan = f64::NAN;
            println!("{} {} {} {} {}", big as u8, neg as u8, nan as i32,
                -1i32 as u32, 3.99f64 as i32);
        }
    ''', "255 0 0 4294967295 3", ["44 251 0 4294967295 4", "255 0 0 -1 3", "255 0 NaN 4294967295 4"],
      "Float-to-int casts saturate (NaN gives 0); int-to-int casts wrap",
      """Casting a float clamps it to the target's range, turns NaN into 0 and drops the fraction. Integer casts
      instead keep the low bits, so -1 as a u32 is all ones: 4294967295."""),

    q("wrapping-checked-saturating", r'''
        fn main() {
            let x = 250u8;
            println!("{} {:?} {} {:?}", x.wrapping_add(10), x.checked_add(10),
                x.saturating_add(10), x.overflowing_add(10));
        }
    ''', "4 None 255 (4, true)", ["260 None 255 (4, true)", "4 Some(4) 255 (4, false)", "4 None 4 (255, true)"],
      "Four ways to overflow: wrap, report None, clamp, or return the flag too",
      """`wrapping_add` keeps the low 8 bits (260 - 256 = 4), `checked_add` returns None, `saturating_add` stops at
      the maximum 255, and `overflowing_add` gives the wrapped result together with a flag that it overflowed."""),

    q("wrapping-abs-of-min", r'''
        fn main() {
            println!("{} {:?} {}", i8::MIN.wrapping_abs(), i8::MIN.checked_abs(),
                i8::MIN.unsigned_abs());
        }
    ''', "-128 None 128", ["128 None 128", "-128 Some(-128) 128", "-128 None -128"],
      "The smallest signed number has no positive twin; unsigned_abs is the safe way out",
      """+128 does not fit in an i8, so `wrapping_abs` returns -128 again and `checked_abs` reports None. The
      result type of `unsigned_abs` is u8, where 128 fits."""),

    q("char-widths", r'''
        fn main() {
            let e = "\u{e9}";
            let combined = "e\u{301}";
            println!("{} {} {} {}", e.len(), '\u{1F600}'.len_utf8(),
                e.chars().count(), combined.chars().count());
        }
    ''', "2 4 1 2", ["1 1 1 1", "2 4 1 1", "2 2 2 2"],
      "A char is a code point; what looks like one letter may be several chars",
      """The precomposed e-acute is one char taking 2 bytes. An emoji is one char taking 4 bytes. The same
      letter written as `e` plus a combining accent is two chars, even though it displays as one."""),

    q("parse-forms", r'''
        fn main() {
            println!("{:?} {} {} {:?}", "+7".parse::<i32>(),
                " 7".parse::<i32>().is_err(), "3.0".parse::<i32>().is_err(),
                "3".parse::<f64>());
        }
    ''', "Ok(7) true true Ok(3.0)", ["Ok(7) false true Ok(3)", "Ok(7) true false Ok(3.0)", "Err(7) true true Ok(3)"],
      "parse accepts a leading + but no spaces, and an integer parse rejects a decimal point",
      """A sign is allowed, whitespace is not, so " 7" is an error. "3.0" is not a valid i32 text. Parsing "3" as
      an f64 works, and the `{:?}` output of the float shows the .0."""),

    q("float-display-versus-debug", r'''
        fn main() {
            println!("{} {:?} {} {:?}", 1.0, 1.0, 1e21, 1e21);
        }
    ''', "1 1.0 1000000000000000000000 1e21",
      ["1.0 1.0 1e21 1e21", "1 1 1e21 1e21", "1 1.0 1e21 1000000000000000000000"],
      "Display prints 1.0 as 1 and never uses an exponent; Debug keeps .0 and may use one",
      """Display writes the shortest digits that identify the float and omits a zero fraction, expanding even huge
      values in full. Debug prints a float so that it still looks like a float: 1.0, and 1e21 in exponent form."""),

    q("float-format-ties", r'''
        fn main() {
            println!("{:.0} {:.0} {:.0} {} {:.1}", 0.5, 1.5, 2.5,
                2.5f64.round(), 0.25);
        }
    ''', "0 2 2 3 0.2", ["1 2 3 3 0.3", "0 2 2 2 0.2", "1 2 2 3 0.3"],
      "Formatting rounds exact ties to even, while f64::round rounds them away from zero",
      """The exact values 0.5, 1.5, 2.5 and 0.25 are ties, and `{:.N}` breaks ties toward the even digit, giving
      0, 2, 2 and 0.2. The `round` method always sends halves away from zero, so 2.5 becomes 3."""),

    q("vec-of-vec-is-independent", r'''
        fn main() {
            let mut g = vec![vec![0; 2]; 2];
            g[0][0] = 1;
            let mut a = [1, 2, 3];
            let b = a;
            a[0] = 9;
            println!("{:?} {:?} {:?}", g, a, b);
        }
    ''', "[[1, 0], [0, 0]] [9, 2, 3] [1, 2, 3]",
      ["[[1, 0], [1, 0]] [9, 2, 3] [1, 2, 3]", "[[1, 0], [0, 0]] [9, 2, 3] [9, 2, 3]",
       "[[1, 0], [0, 0]] [1, 2, 3] [1, 2, 3]"],
      "vec![x; n] clones x for each row, and arrays of Copy values are copied on assignment",
      """Unlike a Python list multiplication, `vec![vec![0; 2]; 2]` clones the inner vec, so the rows are
      separate. An array of integers is `Copy`, so `let b = a` duplicates it and later writes do not show in
      `b`."""),

    q("iter-mut-versus-copy", r'''
        fn main() {
            let mut v = vec![1, 2, 3];
            for x in v.iter_mut() {
                *x *= 2;
            }
            let mut w = vec![1, 2, 3];
            for mut x in w.clone() {
                x *= 2;
            }
            w.push(0);
            println!("{:?} {:?}", v, w);
        }
    ''', "[2, 4, 6] [1, 2, 3, 0]", ["[1, 2, 3] [1, 2, 3, 0]", "[2, 4, 6] [2, 4, 6, 0]", "[2, 4, 6] [1, 2, 3]"],
      "iter_mut hands out references into the vector; a by-value loop works on copies",
      """Writing through `*x` changes the elements of `v`. The second loop iterates over a clone and its `x` is a
      private integer, so `w` is unchanged apart from the later `push`."""),

    q("loop-labels", r'''
        fn main() {
            let mut n = 0;
            'outer: for i in 0..3 {
                for j in 0..3 {
                    if j == 2 { continue 'outer; }
                    n += 1 + i;
                }
            }
            let mut i = 0;
            let v = loop { i += 1; if i == 3 { break i * 2; } };
            println!("{} {}", n, v);
        }
    ''', "12 6", ["9 6", "6 6", "18 6"],
      "continue 'outer skips the rest of the inner loop, and loop can return a value with break",
      """For each i only j = 0 and 1 add 1 + i before `continue 'outer` skips j = 2, so n is 2 + 4 + 6 = 12. The
      `loop` expression evaluates to the value given to `break`, here 3 * 2."""),

    q("enum-discriminants", r'''
        enum E { A = 1, B, C = 10, D }

        fn main() {
            println!("{} {} {}", E::A as i32, E::B as i32, E::D as i32);
        }
    ''', "1 2 11", ["0 1 11", "1 2 10", "1 1 10"],
      "An enum member without a value is the previous one plus one",
      """Explicit discriminants set the number, and each following member without one continues from the one
      before: B is 2 and D is 11."""),

    q("shift-and-sign", r'''
        fn main() {
            let a = -1i32 >> 1;
            let b = (-1i32 as u32) >> 1;
            println!("{} {} {}", a, b, 1u8 << 7);
        }
    ''', "-1 2147483647 128", ["2147483647 2147483647 128", "-1 -1 128", "-1 2147483647 0"],
      "Right shift is arithmetic for signed types and logical for unsigned ones",
      """On an i32 the sign bit is copied in, so -1 stays -1. Reinterpreted as a u32 (all ones), a right shift
      brings in a zero and gives 2147483647. A u8 holds 128 fine."""),

    q("usize-subtraction", r'''
        fn main() {
            let a: usize = 2;
            let b: usize = 3;
            println!("{} {:?} {}", a.saturating_sub(b), a.checked_sub(b),
                a as i64 - b as i64);
        }
    ''', "0 None -1", ["-1 None -1", "0 Some(0) -1", "0 None 1"],
      "Unsigned subtraction cannot go below zero, so pick how to handle it",
      """`2usize - 3` would panic in a debug build or wrap to a huge number in a release build. The explicit forms
      clamp to 0, return None, or convert to a signed type first."""),

    q("option-take-and-replace", r'''
        fn main() {
            let mut o = Some(3);
            let a = o.take();
            let b = o.replace(9);
            let mut s = String::from("hi");
            let t = std::mem::take(&mut s);
            println!("{:?} {:?} {:?} {:?} {:?}", a, b, o, s, t);
        }
    ''', 'Some(3) None Some(9) "" "hi"', ['None None Some(9) "hi" ""', 'Some(3) Some(3) Some(9) "" "hi"', 'Some(3) None Some(3) "hi" ""'],
      "take and replace swap a value out and give back the old one",
      """`take` moves the value out and leaves None behind. `replace` stores a new value and returns the old,
      which is None at that moment. `mem::take` does the same for any type with a default, leaving "" in the
      string."""),

    q("question-mark-parse", r'''
        use std::num::ParseIntError;

        fn double(s: &str) -> Result<i32, ParseIntError> {
            let n: i32 = s.parse()?;
            Ok(n * 2)
        }

        fn main() {
            println!("{:?} {:?}", double("21"), double("x"));
        }
    ''', "Ok(42) Err(ParseIntError { kind: InvalidDigit })",
      ["Ok(42) Err(\"x\")", "42 Err(InvalidDigit)", "Ok(42) Ok(0)"],
      "? returns the error early from the whole function",
      """When `parse` fails, `?` returns that `Err` from `double` immediately instead of continuing to the
      multiplication. The error value is a `ParseIntError` whose kind says why."""),

    q("binary-search-result", r'''
        fn main() {
            let v = [1, 3, 5, 7];
            println!("{:?} {:?} {:?}", v.binary_search(&3),
                v.binary_search(&4), v.binary_search(&9));
        }
    ''', "Ok(1) Err(2) Err(4)", ["Ok(1) None None", "Ok(1) Err(1) Err(3)", "Some(1) Err(2) Err(4)"],
      "A failed binary_search returns where the value would be inserted",
      """`Ok(i)` gives the index of a match; `Err(i)` gives the position that keeps the slice sorted. 4 would go at
      index 2 and 9 at the end, index 4."""),

    q("chunks-and-windows", r'''
        fn main() {
            let v = [1, 2, 3, 4, 5];
            let c: Vec<_> = v.chunks(2).collect();
            println!("{:?} {} {:?}", c, v.windows(2).count(), v.windows(2).last());
        }
    ''', "[[1, 2], [3, 4], [5]] 4 Some([4, 5])",
      ["[[1, 2], [3, 4]] 4 Some([4, 5])", "[[1, 2], [3, 4], [5]] 5 Some([5])", "[[1, 2], [3, 4], [5]] 4 Some([5])"],
      "chunks do not overlap and the last may be short; windows overlap",
      """`chunks(2)` splits into pairs plus a leftover single element. `windows(2)` slides one step at a time, so
      five elements make four windows, the last being [4, 5]."""),

    q("split-variants", r'''
        fn main() {
            println!("{} {} {}", "a,b,,".split(',').count(),
                "  a b ".split(' ').count(),
                "  a b ".split_whitespace().count());
        }
    ''', "4 5 2", ["2 3 2", "4 5 5", "4 2 2"],
      "split keeps empty pieces; split_whitespace skips them",
      """Splitting on a single separator keeps the empty strings between and after separators: "a,b,," has four
      pieces and "  a b " has five. `split_whitespace` treats a run of whitespace as one gap and ignores the
      ends."""),

    q("char-as-u8-truncates", r'''
        fn main() {
            let euro = '\u{20ac}';
            println!("{} {} {}", euro as u8, euro as u32, (b'a' + 1) as char);
        }
    ''', "172 8364 b", ["8364 8364 b", "172 172 98", "255 8364 98"],
      "char as u8 keeps only the low byte of the code point",
      """The euro sign is U+20AC = 8364; truncated to its low 8 bits that is 0xAC = 172. The cast to u32 is
      lossless, and adding to a byte literal and casting back with `as char` gives a letter."""),

    q("pow-and-roots", r'''
        fn main() {
            println!("{} {} {:?} {}", 2i32.pow(10), 2f64.powi(-1),
                2u64.checked_pow(64), (-8f64).cbrt());
        }
    ''', "1024 0.5 None -2", ["1024 0.5 Some(0) NaN", "1024 -1 None -2", "1024 0.5 None NaN"],
      "Negative exponents need floats, a power can overflow, and a cube root works on negatives",
      """`powi` takes an integer exponent for floats, so 2 to the -1 is 0.5. 2 to the 64th does not fit in a u64,
      which `checked_pow` reports as None. `cbrt` is defined for negative numbers, unlike `sqrt`."""),

    q("string-get-char-boundary", r'''
        fn main() {
            let s = "h\u{e9}llo";
            println!("{:?} {:?} {}", s.get(0..2).map(|t| t.len()),
                s.get(0..3).map(|t| t.len()), s.is_char_boundary(2));
        }
    ''', "None Some(3) false", ["Some(2) Some(3) true", "None None false", "Some(2) Some(2) false"],
      "Slicing a str happens at byte positions and must land between characters",
      """The accented e occupies bytes 1 and 2, so index 2 is inside it. `get` returns None for such a range,
      where `&s[0..2]` would panic. Byte 3 is a boundary and gives 3 bytes."""),

    q("debug-escapes", r'''
        fn main() {
            println!("{:?} {:?} {:?}", "a\"b", '\'', "tab\there");
        }
    ''', r'''"a\"b" '\'' "tab\there"''', ['a"b \' tab\there', '"a"b" \'\'\' "tab\there"', '"a\\"b" \'\\\'\' "tab here"'],
      "Debug formatting quotes the value and escapes what needs it",
      """`{:?}` shows a value the way you would write it in source code, so a string gets quotes and its inner
      quote and tab are escaped. A char gets single quotes and an escaped apostrophe."""),

    q("format-width-and-flags", r'''
        fn main() {
            println!("|{:>5}|{:<5}|{:^5}|{:05}|{:+}|{:#x}|{:#b}|{:8.3}|",
                "ab", "ab", "ab", 42, 7, 255, 5, 3.14159);
        }
    ''', "|   ab|ab   | ab  |00042|+7|0xff|0b101|   3.142|",
      ["|ab   |   ab| ab  |42000|7|ff|101|3.14159|", "|   ab|ab   | ab  |00042|+7|0xff|0b101|3.14|",
       "|   ab|ab   | ab  |00042|7|0xff|0b101|   3.142|"],
      "Fill, alignment, sign, # and precision are each separate flags",
      """Strings default to left alignment and numbers to right, but `>`, `<` and `^` choose. Centring puts the
      extra space on the right, `0` pads with zeros, `+` forces a sign, `#` adds the 0x and 0b prefixes, and
      `.3` fixes three decimals."""),

    q("format-star-precision", r'''
        fn main() {
            let w = 4;
            let x = "a";
            println!("{:.*} {:>w$}|{x:?}", 1, 2.55, 7);
        }
    ''', '2.5    7|"a"', ['2.6    7|"a"', '2.55    7|a', '2.5 7 |"a"'],
      "{:.*} takes its precision from the arguments; w$ and {x} read variables by name",
      """`.*` consumes two arguments: first the precision 1, then the value 2.55, which prints as 2.5 because the
      double is just below 2.55. `{:>w$}` right-aligns the next argument in `w` columns, and `{x:?}` captures
      the variable directly."""),

    q("display-ignores-width", r'''
        use std::fmt;

        struct P(i32);

        impl fmt::Display for P {
            fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
                write!(f, "P{}", self.0)
            }
        }

        fn main() {
            println!("|{:>6}|{:>6}|{:>6}|", P(1), "ab", P(2).to_string());
        }
    ''', "|P1|    ab|    P2|", ["|    P1|    ab|    P2|", "|P1|ab|P2|", "|    P1|    ab|P2|"],
      "A custom Display ignores width unless it uses f.pad",
      """The width flag is passed to your `fmt` as part of the Formatter, and `write!` simply ignores it. Strings
      pad themselves, so converting with `to_string()` first gives a String that does honour the width."""),

    # ── Ownership, drops and smart pointers ────────────────────────────────
    q("drop-order-locals", r'''
        use std::cell::RefCell;
        struct D<'a>(&'a str, &'a RefCell<String>);
        impl Drop for D<'_> {
            fn drop(&mut self) { self.1.borrow_mut().push_str(self.0); }
        }

        fn main() {
            let log = RefCell::new(String::new());
            {
                let _a = D("a", &log);
                let _b = D("b", &log);
                let _ = D("c", &log);
            }
            println!("{}", log.borrow());
        }
    ''', "cba", ["abc", "cab", "bac"],
      "Locals drop in reverse order, but `let _ =` drops the value immediately",
      """The pattern `_` does not bind anything, so the temporary is dropped at the end of its own statement and
      "c" is logged first. `_a` and `_b` live to the end of the block and drop in reverse order of creation."""),

    q("drop-order-fields", r'''
        use std::cell::RefCell;
        struct D<'a>(&'a str, &'a RefCell<String>);
        impl Drop for D<'_> {
            fn drop(&mut self) { self.1.borrow_mut().push_str(self.0); }
        }
        struct P<'a> { x: D<'a>, y: D<'a> }
        fn main() {
            let log = RefCell::new(String::new());
            {
                let p = P { x: D("x", &log), y: D("y", &log) };
                let _q = D("q", &log);
                drop(p);
                log.borrow_mut().push('|');
            }
            println!("{}", log.borrow());
        }
    ''', "xy|q", ["yx|q", "q|xy", "xyq|"],
      "A struct drops its fields in declaration order; drop(p) runs right away",
      """`drop(p)` moves the struct into a function that ends immediately, dropping field `x` then field `y`. The
      bar is logged after that, and `_q` is dropped at the closing brace."""),

    q("rc-strong-count", r'''
        use std::rc::Rc;

        fn main() {
            let a = Rc::new(5);
            let inside = {
                let _b = Rc::clone(&a);
                Rc::strong_count(&a)
            };
            println!("{} {}", inside, Rc::strong_count(&a));
        }
    ''', "2 1", ["1 1", "2 2", "1 2"],
      "Cloning an Rc adds an owner; leaving the scope removes it",
      """Inside the block there are two owners of the 5. When `_b` goes out of scope at the closing brace, the
      count drops back to one."""),

    q("refcell-runtime-borrow", r'''
        use std::cell::RefCell;

        fn main() {
            let c = RefCell::new(1);
            let r = c.borrow();
            println!("{} {} {}", c.try_borrow_mut().is_err(),
                c.try_borrow().is_ok(), *r);
        }
    ''', "true true 1", ["false true 1", "true false 1", "false false 1"],
      "RefCell checks borrow rules when the program runs, not when it compiles",
      """While a shared borrow `r` is alive, a second shared borrow is fine but a mutable one is refused. With
      `try_borrow_mut` you get an `Err`; `borrow_mut` would panic instead."""),

    q("move-closure-copies", r'''
        fn main() {
            let mut c = 0;
            let mut inc = move || { c += 1; c };
            inc();
            inc();
            println!("{} {}", c, inc());
        }
    ''', "0 3", ["2 3", "3 3", "0 1"],
      "A move closure over a Copy value gets its own copy",
      """`c` is an integer, so `move` copies it into the closure. The closure's private counter is bumped by each
      call, while the outer `c` stays 0 forever."""),

    q("closure-borrows-mutably", r'''
        fn main() {
            let mut c = 0;
            let mut inc = || c += 1;
            inc();
            inc();
            println!("{}", c);
        }
    ''', "2", ["0", "1", "Error"],
      "Without move, a closure borrows the variable and changes the real one",
      """The closure holds a mutable borrow of `c`, so its two calls add to the original. The borrow ends after
      the last use of `inc`, which is why `c` can be printed."""),

    q("struct-update-syntax", r'''
        #[derive(Debug)]
        struct Cfg { a: i32, b: i32, c: bool }

        fn main() {
            let base = Cfg { a: 1, b: 2, c: true };
            let n = Cfg { a: 9, ..base };
            println!("{:?}", n);
        }
    ''', "Cfg { a: 9, b: 2, c: true }", ["Cfg { a: 9, b: 0, c: false }", "Cfg { a: 1, b: 2, c: true }", "Cfg { a: 9 }"],
      "..base fills in every field you did not list",
      """The listed field gets the new value and the remaining fields are taken from `base`. These fields are
      Copy, so `base` stays usable; a String field would have been moved out."""),

    q("derive-partial-ord", r'''
        #[derive(PartialEq, PartialOrd)]
        struct V(i32, i32);

        #[derive(PartialEq, PartialOrd)]
        enum E { B, A }

        fn main() {
            println!("{} {} {}", V(1, 9) < V(2, 0), E::B < E::A, V(1, 2) < V(1, 2));
        }
    ''', "true true false", ["false true false", "true false false", "true true true"],
      "Derived ordering is lexicographic by field, and by variant position for enums",
      """Tuples and structs compare their first field, then the next on a tie. Enum variants are ordered by where
      they are declared, not by name, so `B` is less than `A`. Equal values are not less than each other."""),

    q("inherent-beats-trait", r'''
        trait T { fn f(&self) -> &str; }

        struct S;

        impl S { fn f(&self) -> &str { "inherent" } }
        impl T for S { fn f(&self) -> &str { "trait" } }

        fn main() {
            println!("{} {}", S.f(), T::f(&S));
        }
    ''', "inherent trait", ["trait trait", "inherent inherent", "trait inherent"],
      "When both exist, the inherent method wins unless you name the trait",
      """Method lookup tries methods defined directly on the type before trait methods of the same name. Calling
      `T::f(&S)` spells out which one is meant."""),

    # ── Iterators and collections ──────────────────────────────────────────
    q("iterator-is-lazy", r'''
        use std::cell::Cell;

        fn main() {
            let c = Cell::new(0);
            let it = (1..=5).map(|x| { c.set(c.get() + 1); x });
            let before = c.get();
            let s: i32 = it.take(2).sum();
            println!("{} {} {}", before, c.get(), s);
        }
    ''', "0 2 3", ["5 5 3", "0 5 3", "5 2 3"],
      "map does nothing until something pulls items out of the iterator",
      """Creating the adaptor runs no closure, so the count is 0. `take(2).sum()` pulls just two items through
      `map`, which runs twice, and the sum is 1 + 2."""),

    q("take-while-eats-one", r'''
        fn main() {
            let mut it = [1, 2, 3, 4].iter();
            let a: Vec<_> = it.by_ref().take_while(|&&x| x < 3).collect();
            println!("{:?} {:?}", a, it.next());
        }
    ''', "[1, 2] Some(4)", ["[1, 2] Some(3)", "[1, 2, 3] Some(4)", "[1, 2] None"],
      "take_while must read the first failing item to know it fails, and that item is gone",
      """The 3 is pulled from the iterator, tested, and rejected, but it cannot be put back. So the next item
      the original iterator yields is 4."""),

    q("rev-enumerate-order", r'''
        fn main() {
            let v = ["a", "b", "c"];
            let x = v.iter().rev().enumerate().next();
            let y = v.iter().enumerate().rev().next();
            println!("{:?} {:?}", x, y);
        }
    ''', 'Some((0, "c")) Some((2, "c"))', ['Some((2, "c")) Some((0, "c"))', 'Some((0, "a")) Some((2, "c"))', 'Some((0, "c")) Some((0, "c"))'],
      "The order of rev and enumerate decides whether the index counts the original positions",
      """`rev().enumerate()` numbers items in the order they are produced, so "c" is first with index 0.
      `enumerate().rev()` attaches indexes first and then reverses, so "c" keeps index 2."""),

    q("max-by-key-ties", r'''
        fn main() {
            let w = ["bb", "aa", "c", "d"];
            let hi = w.iter().max_by_key(|s| s.len()).unwrap();
            let lo = w.iter().min_by_key(|s| s.len()).unwrap();
            println!("{} {}", hi, lo);
        }
    ''', "aa c", ["bb d", "bb c", "aa d"],
      "On ties, max_by_key returns the last item and min_by_key the first",
      """Both "bb" and "aa" have length 2; `max_by_key` keeps the later one. Both "c" and "d" have length 1;
      `min_by_key` keeps the earlier."""),

    q("sort-stability-with-reverse", r'''
        use std::cmp::Reverse;

        fn main() {
            let mut v = vec![(1, 'b'), (2, 'a'), (3, 'b'), (4, 'a')];
            v.sort_by_key(|p| Reverse(p.1));
            println!("{:?}", v);
        }
    ''', "[(1, 'b'), (3, 'b'), (2, 'a'), (4, 'a')]",
      ["[(3, 'b'), (1, 'b'), (4, 'a'), (2, 'a')]", "[(2, 'a'), (4, 'a'), (1, 'b'), (3, 'b')]",
       "[(4, 'a'), (2, 'a'), (3, 'b'), (1, 'b')]"],
      "A stable sort keeps equal items in their original order, even in descending order",
      """`Reverse` flips the comparison of the keys, but items with equal keys are still not reordered. So the two
      'b' entries stay as 1 then 3, ahead of the two 'a' entries."""),

    q("dedup-adjacent", r'''
        fn main() {
            let mut v = vec![1, 1, 2, 1, 3, 3];
            v.dedup();
            let mut w = vec![1, 2, 3, 4, 5];
            let x = w.swap_remove(0);
            println!("{:?} {:?} {}", v, w, x);
        }
    ''', "[1, 2, 1, 3] [5, 2, 3, 4] 1", ["[1, 2, 3] [2, 3, 4, 5] 1", "[1, 2, 1, 3] [2, 3, 4, 5] 1", "[1, 2, 3] [5, 2, 3, 4] 1"],
      "dedup removes only neighbours; swap_remove fills the gap with the last element",
      """`dedup` looks at consecutive duplicates only, so the separated 1 survives. `swap_remove(0)` is O(1)
      because it moves the final element, 5, into the hole instead of shifting everything down."""),

    q("trim-matches-patterns", r'''
        fn main() {
            let s = "abba-x";
            println!("{} {}", s.trim_start_matches("ab"),
                s.trim_start_matches(|c| c == 'a' || c == 'b'));
        }
    ''', "ba-x -x", ["-x -x", "ba-x ba-x", "-x ba-x"],
      "A &str pattern removes the whole string repeatedly; a char test removes any matching char",
      """The pattern "ab" is a two-character prefix: it matches once at the start and then "ba-x" does not begin
      with it. The closure matches single characters, so it keeps stripping through "abba"."""),

    q("btreemap-entry-counts", r'''
        use std::collections::BTreeMap;

        fn main() {
            let mut m = BTreeMap::new();
            for w in "9 10 9".split(' ') {
                *m.entry(w).or_insert(0) += 1;
            }
            println!("{:?}", m);
        }
    ''', '{"10": 1, "9": 2}', ['{"9": 2, "10": 1}', '{"9": 1, "10": 1}', '{"10": 1, "9": 1}'],
      "String keys in a BTreeMap sort as text, so \"10\" comes before \"9\"",
      """`entry(w).or_insert(0)` gives a mutable reference to the count, creating it at 0 the first time. The
      map iterates in key order, and for strings that is character by character, not numeric."""),

    q("eager-versus-lazy-default", r'''
        use std::cell::Cell;

        fn main() {
            let c = Cell::new(0);
            let f = || { c.set(c.get() + 1); 0 };
            let a = Some(1).unwrap_or(f());
            let b = Some(1).unwrap_or_else(f);
            println!("{} {} {}", a, b, c.get());
        }
    ''', "1 1 1", ["1 1 0", "1 1 2", "0 0 1"],
      "unwrap_or evaluates its argument even when it is not needed; unwrap_or_else does not",
      """The argument `f()` is computed before `unwrap_or` is even called, so the counter goes up once although
      the Some(1) makes the default irrelevant. The `_else` form only calls the closure for None."""),

    q("option-combinators", r'''
        fn main() {
            let a = Some(0).filter(|x| *x > 0).unwrap_or(5);
            let b = None::<i32>.or(Some(1));
            let c = Some(3).map_or(0, |x| x * 2);
            let d = Some(2).and_then(|x| if x > 5 { Some(x) } else { None });
            println!("{} {:?} {} {:?}", a, b, c, d);
        }
    ''', "5 Some(1) 6 None", ["0 Some(1) 6 None", "5 None 6 Some(2)", "5 Some(1) 3 Some(2)"],
      "filter turns a Some into None when the test fails",
      """`Some(0)` fails the test `x > 0`, so `filter` produces None and `unwrap_or` supplies 5. `or` fills in a
      missing value, `map_or` transforms a present one, and `and_then` can turn a Some into None."""),

    q("match-guards-in-order", r'''
        fn kind(x: i32) -> &'static str {
            match x {
                n if n % 2 == 0 => "even",
                1..=5 => "small",
                _ => "big",
            }
        }

        fn main() {
            println!("{} {} {} {}", kind(2), kind(3), kind(7), kind(-4));
        }
    ''', "even small big even", ["small small big even", "even small big big", "even even big even"],
      "Match arms are tried top to bottom, and a guard decides whether the arm applies",
      """2 and -4 satisfy the first guard, so they never reach the range arm, even though 2 is also in 1..=5.
      3 is odd and in range, 7 is odd and out of range."""),

    q("matches-and-binding", r'''
        fn main() {
            let v = Some(7);
            let a = matches!(v, Some(n) if n > 5);
            let b = match v { Some(n @ 1..=5) => n, Some(n) => -n, None => 0 };
            println!("{} {}", a, b);
        }
    ''', "true -7", ["false -7", "true 7", "true 0"],
      "n @ pattern binds the value while testing it against a range",
      """7 passes the guard in `matches!`, so that is true. In the `match`, `Some(n @ 1..=5)` does not accept 7,
      so the next arm is taken and negates it."""),

    q("tuple-vec-debug", r'''
        fn main() {
            let t = (1, "a", 2.0, 'c', [1u8, 2], ());
            println!("{:?}", t);
        }
    ''', "(1, \"a\", 2.0, 'c', [1, 2], ())", ["(1, a, 2, c, [1, 2], ())", "(1, \"a\", 2, 'c', [1, 2], ())", "[1, \"a\", 2.0, 'c', [1, 2], ()]"],
      "Debug shows each part the way it would be written: quotes on text, a point on floats",
      """Strings get double quotes, chars single quotes, floats keep their .0, and the unit value prints as an
      empty pair of parentheses."""),
    q("default-method-dispatch", r'''
        trait A {
            fn n(&self) -> String { "A".to_string() }
            fn hi(&self) -> String { format!("hi {}", self.n()) }
        }

        struct S;

        impl A for S {
            fn n(&self) -> String { "S".to_string() }
        }

        fn main() {
            println!("{}", S.hi());
        }
    ''', "hi S", ["hi A", "A", "S"],
      "A default method calls the implementor's override, not the default",
      """`hi` is written once in the trait, but `self.n()` is resolved for the concrete type, `S`, which supplies
      its own `n`. Only types that do not override `n` would get "A"."""),

    q("with-capacity-is-not-length", r'''
        fn main() {
            let mut v: Vec<i32> = Vec::with_capacity(10);
            let z = vec![0; 10];
            v.push(1);
            println!("{} {} {}", v.len(), z.len(), v.capacity() >= 10);
        }
    ''', "1 10 true", ["10 10 true", "1 10 false", "11 10 true"],
      "with_capacity reserves room but the vector is still empty",
      """Capacity is memory set aside, length is how many elements exist. `vec![0; 10]` creates ten elements,
      `with_capacity(10)` creates none and the push makes one."""),

    q("char-indices-bytes", r'''
        fn main() {
            let s = "h\u{e9}llo";
            let idx: Vec<usize> = s.char_indices().map(|(i, _)| i).collect();
            println!("{:?} {}", idx, s.bytes().len());
        }
    ''', "[0, 1, 3, 4, 5] 6", ["[0, 1, 2, 3, 4] 6", "[0, 1, 3, 4, 5] 5", "[0, 1, 2, 3, 4] 5"],
      "char_indices reports the byte offset of each char",
      """The accented e is two bytes, so every char after it starts one byte further along than its char count
      would suggest. The offsets skip 2 and the total is 6 bytes."""),

    q("float-addition-not-associative", r'''
        fn main() {
            let (a, b, c) = (0.1, 0.2, 0.3);
            println!("{} {}", (a + b) + c, a + (b + c));
        }
    ''', "0.6000000000000001 0.6",
      ["0.6 0.6", "0.6 0.6000000000000001", "0.6000000000000001 0.6000000000000001"],
      "Floating-point addition depends on grouping",
      """Each addition rounds its result. Adding 0.1 and 0.2 first gives a slightly high 0.30000000000000004,
      which carries into the next sum, while 0.2 + 0.3 happens to be exactly the double nearest 0.5."""),

    q("nan-and-inf-formatting", r'''
        fn main() {
            let z = 0.0f64;
            println!("{} {} {} {} {:?}", f64::NAN == f64::NAN, 0.0 == -z,
                1.0 / z, -1.0 / z, z.total_cmp(&-z));
        }
    ''', "false true inf -inf Greater",
      ["true true Infinity -Infinity Equal", "false true inf -inf Equal", "false false +inf -inf Greater"],
      "NaN is not equal to itself, -0.0 equals 0.0, and Rust prints infinities as inf",
      """`==` follows IEEE rules, so NaN differs from NaN and the two zeros are equal. `total_cmp` is a total order
      that does separate them: positive zero is greater than negative zero. Display spells infinity `inf`."""),

    q("str-ordering", r'''
        fn main() {
            println!("{} {} {} {}", "a" < "B", "10" < "9", "abc" < "abd",
                "ab" < "abc");
        }
    ''', "false true true true", ["true false true true", "false false true true", "false true true false"],
      "Strings compare byte by byte; a prefix is smaller than the longer string",
      """The capital B (66) is below the lower-case a (97). "10" is below "9" because '1' is below '9'. A string
      that is a prefix of another comes first."""),

    q("slice-patterns", r'''
        fn main() {
            let v = [1, 2, 3, 4];
            let s = match &v[..] {
                [a, rest @ ..] => format!("{} {:?}", a, rest),
                [] => String::new(),
            };
            let t = if let [first, .., last] = v { first + last } else { 0 };
            println!("{} {}", s, t);
        }
    ''', "1 [2, 3, 4] 5", ["1 [2, 3] 5", "1 [2, 3, 4] 4", "[1] [2, 3, 4] 5"],
      "Slice patterns can bind the first element, the last, and the rest",
      """`[a, rest @ ..]` binds the head and gives the tail as a slice, so `rest` is [2, 3, 4]. `[first, .., last]`
      ignores the middle and picks both ends: 1 + 4 = 5."""),

    q("vec-append-empties-source", r'''
        fn main() {
            let mut a = vec![1];
            let mut b = vec![2, 3];
            a.append(&mut b);
            let c = [4, 5];
            a.extend(c.iter());
            println!("{:?} {}", a, b.len());
        }
    ''', "[1, 2, 3, 4, 5] 0", ["[1, 2, 3, 4, 5] 2", "[1, 4, 5] 2", "[1, 2, 3] 0"],
      "append moves everything out of the other vector, leaving it empty",
      """`append(&mut b)` takes the elements of `b` rather than copying them, so `b.len()` is 0 afterwards.
      `extend` with an iterator of references copies the integers in."""),

    q("rc-refcell-versus-vec-clone", r'''
        use std::cell::RefCell;
        use std::rc::Rc;

        fn main() {
            let a = Rc::new(RefCell::new(vec![1]));
            let b = Rc::clone(&a);
            b.borrow_mut().push(2);
            let mut c = a.borrow().clone();
            c.push(3);
            println!("{} {}", a.borrow().len(), c.len());
        }
    ''', "2 3", ["3 3", "1 3", "2 2"],
      "Cloning an Rc shares the data; cloning the Vec inside copies it",
      """`b` is a second handle to the same vector, so its push is visible through `a` (length 2). `c` is an
      independent copy of that vector, so the push to it is not."""),

    q("empty-iterator-folds", r'''
        fn main() {
            let e: Vec<i32> = Vec::new();
            println!("{} {:?} {} {}", e.iter().sum::<i32>(), e.iter().max(),
                e.iter().product::<i32>(), "x".parse::<i32>().unwrap_or_default());
        }
    ''', "0 None 1 0", ["0 None 0 0", "0 Some(0) 1 0", "1 None 1 -1"],
      "An empty sum is 0 and an empty product is 1; max of nothing is None",
      """Each fold starts from its identity element: 0 for addition and 1 for multiplication. `max` has no
      identity value, so it returns an Option. `unwrap_or_default` turns a failed parse into 0."""),

    q("rotate-and-split-at", r'''
        fn main() {
            let mut v = [1, 2, 3, 4, 5];
            v.rotate_left(2);
            let (a, b) = v.split_at(2);
            println!("{:?} {:?}", a, b);
        }
    ''', "[3, 4] [5, 1, 2]", ["[1, 2] [3, 4, 5]", "[4, 5] [1, 2, 3]", "[3, 4, 5] [1, 2]"],
      "rotate_left moves the first elements to the back, in place",
      """After rotating by 2 the array is [3, 4, 5, 1, 2]. `split_at(2)` then gives the first two elements and
      the rest, without copying."""),

    q("uppercase-sharp-s", r'''
        fn main() {
            let s = "stra\u{df}e";
            println!("{} {} {}", s.to_uppercase(), '\u{df}'.to_uppercase().count(),
                s.len());
        }
    ''', "STRASSE 2 7", ["STRAßE 1 6", "STRASSE 1 7", "STRASSE 2 6"],
      "Upper-casing can change the length: one sharp s becomes two letters",
      """German sharp s has no single upper-case letter, so `to_uppercase` produces "SS". That is why `char`'s
      version returns an iterator rather than a single char. The original is 7 bytes because the sharp s takes
      two."""),

    q("float-sort-total-cmp", r'''
        fn main() {
            let mut f = vec![2.5, -1.0, f64::NAN, 0.0];
            f.sort_by(|a, b| a.total_cmp(b));
            println!("{:?}", f);
        }
    ''', "[-1.0, 0.0, 2.5, NaN]", ["[NaN, -1.0, 0.0, 2.5]", "[-1.0, 0.0, NaN, 2.5]", "[-1.0, 0.0, 2.5]"],
      "f64 has no Ord, so sort needs total_cmp, which puts NaN after everything",
      """Plain `sort()` does not compile for floats because NaN breaks ordering. `total_cmp` defines a complete
      order, with positive NaN larger than every number."""),

    q("cast-sign-extension", r'''
        fn main() {
            let b = -1i8;
            println!("{} {} {}", b as u32, b as u8 as u32, (200u8 as i8) as i32);
        }
    ''', "4294967295 255 -56", ["255 255 200", "4294967295 4294967295 -56", "255 4294967295 -56"],
      "Widening a signed value copies the sign bit; go through u8 first to avoid it",
      """-1i8 as u32 sign-extends: all 32 bits are ones. Casting to u8 first gives 255, and zero-extending that
      keeps 255. 200 as an i8 reinterprets the bits as -56, which stays -56 when widened."""),

    q("slice-get-ranges", r'''
        fn main() {
            let v = [1, 2, 3];
            println!("{:?} {:?} {:?} {:?}", v.get(3..), v.get(4..), v.first(),
                v.get(..0));
        }
    ''', "Some([]) None Some(1) Some([])",
      ["None None Some(1) None", "Some([]) Some([]) Some(1) Some([])", "Some([]) None 1 Some([])"],
      "get(n..) with n equal to the length is an empty slice; past the end is None",
      """A range may start exactly at the end and gives an empty slice, but one past that is out of range.
      `first` returns an Option of the element, shown here with `{:?}` as `Some(1)`."""),
)
