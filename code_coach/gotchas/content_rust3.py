"""Gotchas, Rust, the third helping: blocks as values, integer helpers, iterator adaptors and smart pointers.

Same rules as content_rust.py: edition 2021, rustc -O, one println! line, no HashMap/HashSet, no raw pointers or
layout, no threads, no clock; overflow is avoided or spelled out with wrapping_/checked_. Fresh ground compared with
the second deck: what a block evaluates to, the small integer and char helper methods, the less common iterator
adaptors (scan, successors, step_by, peekable, nth), Option/Result combinators, Rc::make_mut and Weak, blanket
impls and associated consts, and closures that capture only the fields they use.
"""

from __future__ import annotations

from .items import Item, make

q = make("rust")

ITEMS: tuple[Item, ...] = (
    # ── Easy-looking ───────────────────────────────────────────────────────
    q("block-trailing-semicolon", r'''
        fn main() {
            let a = { let x = 3; x + 1 };
            let b = { let x = 3; x + 1; };
            println!("{} {:?}", a, b);
        }
    ''', "4 ()", ["4 4", "4 0", "4 None"],
      "A block is worth its last expression; a semicolon after it makes the block worth ()",
      """Without a trailing semicolon `x + 1` is the value of the block, so `a` is 4. With the semicolon it is just a
      statement, the block ends with nothing, and its value is the unit type, which prints as `()`."""),

    q("array-argument-is-copied", r'''
        fn bump(mut a: [i32; 3]) -> i32 { a[0] += 10; a[0] }
        fn bump_ref(a: &mut [i32]) { a[0] += 10; }

        fn main() {
            let mut a = [1, 2, 3];
            let r = bump(a);
            let before = a[0];
            bump_ref(&mut a);
            println!("{} {} {}", r, before, a[0]);
        }
    ''', "11 1 11", ["11 11 21", "1 1 11", "11 11 11"],
      "A fixed-size array of Copy values is copied into a function; a &mut borrow shares it",
      """`bump(a)` receives its own copy of the three integers, so the original is still 1 afterwards. Passing
      `&mut a` hands over a borrow, and that call really does add 10 to the caller's array."""),

    q("loop-break-value-and-labelled-block", r'''
        fn main() {
            let mut i = 0;
            let r = loop {
                i += 3;
                if i > 10 { break i * 2; }
            };
            let s = 'blk: {
                if r > 20 { break 'blk "big"; }
                "small"
            };
            println!("{} {}", r, s);
        }
    ''', "24 big", ["12 big", "24 small", "11 small"],
      "break can carry a value out of a loop, and a labelled block can be left early the same way",
      """`i` goes 3, 6, 9, 12, and the `break i * 2` hands back 24 as the value of the loop. A labelled block works
      like an early return from the block: 24 is above 20, so `break 'blk "big"` picks the first value."""),

    q("cell-through-shared-references", r'''
        use std::cell::Cell;

        fn main() {
            let c = Cell::new(1);
            let (r1, r2) = (&c, &c);
            r1.set(r1.get() + 10);
            r2.set(r2.get() * 2);
            let old = c.replace(0);
            println!("{} {}", old, c.get());
        }
    ''', "22 0", ["11 0", "22 22", "12 0"],
      "Cell lets several shared references change the same value",
      """Both `r1` and `r2` are plain `&Cell` borrows, which the compiler allows because a Cell never hands out a
      reference to what is inside. 1 + 10 is 11, doubled is 22, and `replace` returns that old value."""),

    q("abs-diff-does-not-overflow", r'''
        fn main() {
            let a = 10u8.abs_diff(250);
            let b = i32::MIN.abs_diff(i32::MAX);
            let c = (-128i8).unsigned_abs();
            println!("{} {} {}", a, b, c);
        }
    ''', "240 4294967295 128", ["240 -1 128", "-240 4294967295 128", "240 4294967295 0"],
      "abs_diff and unsigned_abs return the unsigned type, so they can hold what a signed one cannot",
      """The distance between i32::MIN and i32::MAX needs 32 bits, which fits in a u32 but not in an i32. In the
      same way the absolute value of -128 is 128 as a u8, even though +128 does not fit in an i8."""),

    q("bit-counting-methods", r'''
        fn main() {
            let a = 1u32.leading_zeros();
            let b = 0b1011u8.count_ones();
            let c = 0x12u8.rotate_left(4);
            let d = (-1i8).count_ones();
            println!("{} {} {} {}", a, b, c, d);
        }
    ''', "31 3 33 8", ["32 3 18 8", "31 3 33 1", "31 4 33 8"],
      "The bit methods work on the whole fixed width of the type",
      """A u32 holding 1 has 31 zeros in front of the single bit. Rotating 0x12 by 4 within 8 bits swaps its two
      nibbles into 0x21, which is 33. The i8 value -1 is eight 1-bits."""),

    q("digit-conversions", r'''
        fn main() {
            println!("{:?} {:?} {:?} {:?}", char::from_digit(11, 16),
                'z'.to_digit(36), 'z'.to_digit(10), char::from_digit(10, 10));
        }
    ''', "Some('b') Some(35) None None", ["Some('B') Some(35) None None",
                                         "Some('b') Some(25) None None", "Some('b') Some(35) Some(0) None"],
      "to_digit and from_digit work in any radix up to 36, and return None when the digit does not fit",
      """In base 16, digit 11 is the lower-case letter b. In base 36, `z` is worth 35, but in base 10 it is not a
      digit at all. And 10 is not a base-10 digit, so `from_digit` gives None."""),

    q("lines-and-trailing-newlines", r'''
        fn main() {
            let a = "a\nb\n".lines().count();
            let b = "a\n\nb".lines().count();
            let c = "".lines().count();
            let d = "\n".lines().count();
            println!("{} {} {} {}", a, b, c, d);
        }
    ''', "2 3 0 1", ["3 3 0 1", "2 2 0 1", "3 3 1 2"],
      "lines() ignores one final newline, but keeps empty lines in the middle",
      """A trailing newline ends the last line instead of starting a new empty one, so "a\\nb\\n" has two lines. An
      empty line between two newlines is a real, empty line. The empty string has none, and "\\n" is one empty
      line."""),

    q("split-once-forms", r'''
        fn main() {
            let s = "k=v=w";
            let a = s.split_once('=');
            let b = s.rsplit_once('=');
            println!("{:?} {:?} {:?}", a, b, "kvw".split_once('='));
        }
    ''', 'Some(("k", "v=w")) Some(("k=v", "w")) None',
      ['Some(("k", "v")) Some(("v", "w")) None', 'Some(("k", "v=w")) Some(("k=v", "w")) Some(("kvw", ""))',
       'Some(("k", "v=w")) Some(("v=w", "k")) None'],
      "split_once cuts at the first separator and rsplit_once at the last; a miss is None",
      """Each returns a pair of slices of the original text, with the separator itself dropped. When the separator
      is missing there is nothing to split, so the answer is None rather than the whole string."""),

    q("partition-and-unzip", r'''
        fn main() {
            let (ev, od): (Vec<i32>, Vec<i32>) = (1..=6).partition(|x| x % 2 == 0);
            let pairs = vec![(1, 'a'), (2, 'b')];
            let (xs, ys): (Vec<i32>, Vec<char>) = pairs.into_iter().unzip();
            println!("{:?} {:?} {:?} {:?}", ev, od, xs, ys);
        }
    ''', "[2, 4, 6] [1, 3, 5] [1, 2] ['a', 'b']",
      ["[1, 3, 5] [2, 4, 6] [1, 2] ['a', 'b']", "[2, 4, 6] [1, 3, 5] [1, 'a'] [2, 'b']",
       "[1, 3, 5] [2, 4, 6] ['a', 'b'] [1, 2]"],
      "partition puts the items where the predicate is true first; unzip splits pairs into two collections",
      """The first collection gets the items for which the closure returns true, the evens, and the second gets
      the rest. `unzip` turns a sequence of pairs into a collection of firsts and a collection of seconds."""),

    q("try-from-versus-as", r'''
        fn main() {
            let a = 300i32 as u8;
            let b = u8::try_from(300i32).is_err();
            let c = u8::try_from(255i32);
            println!("{} {} {:?}", a, b, c);
        }
    ''', "44 true Ok(255)", ["300 true Ok(255)", "44 false Ok(255)", "44 true Err(255)"],
      "as silently truncates; try_from tells you when the value does not fit",
      """`300 as u8` keeps the low 8 bits, 300 - 256 = 44, with no warning. `u8::try_from` returns an `Err` for
      300 and `Ok(255)` for a value that fits."""),

    q("closures-keep-their-own-state", r'''
        fn make() -> impl FnMut() -> u32 {
            let mut c = 0;
            move || { c += 1; c }
        }

        fn main() {
            let mut a = make();
            let mut b = make();
            a();
            a();
            println!("{} {}", a(), b());
        }
    ''', "3 1", ["3 3", "1 1", "3 4"],
      "Each call to make() builds a new closure with its own copy of the captured variable",
      """`move` copies `c` into the closure, so every closure returned by `make` owns a separate counter. `a` is
      called three times and counts to 3, while `b` is called once."""),

    q("boxed-closures-in-a-vec", r'''
        fn main() {
            let fs: Vec<Box<dyn Fn(i32) -> i32>> =
                vec![Box::new(|x| x + 1), Box::new(|x| x * 2)];
            let a = fs.iter().fold(3, |acc, f| f(acc));
            let b = fs.iter().rev().fold(3, |acc, f| f(acc));
            println!("{} {}", a, b);
        }
    ''', "8 7", ["7 8", "8 8", "7 7"],
      "The order closures are applied in changes the result when they do not commute",
      """Forwards, 3 + 1 = 4 and then 4 * 2 = 8. In reverse order the doubling comes first, giving 6, and then
      adding 1 gives 7. `Box<dyn Fn>` lets closures of different types sit in one Vec."""),

    q("integer-helper-methods", r'''
        fn main() {
            let a = 99u32.isqrt();
            let b = 1000u32.ilog10();
            let c = 17u32.next_power_of_two();
            let d = 255u8.ilog2();
            println!("{} {} {} {}", a, b, c, d);
        }
    ''', "9 3 32 7", ["10 3 32 7", "9 4 32 7", "9 3 17 8"],
      "isqrt and ilog round down; next_power_of_two rounds up",
      """The integer square root of 99 is 9, because 10 * 10 is already 100. `ilog10(1000)` is exactly 3, and
      `ilog2(255)` is 7 since 2^8 = 256 is too big. 17 rounds up to the next power of two, 32."""),

    q("skip-while-skips-a-prefix", r'''
        fn main() {
            let v = [1, 2, 5, 1, 2];
            let a: Vec<_> = v.iter().skip_while(|&&x| x < 3).collect();
            let b: Vec<_> = v.iter().filter(|&&x| x >= 3).collect();
            println!("{:?} {:?}", a, b);
        }
    ''', "[5, 1, 2] [5]", ["[5] [5]", "[5, 1, 2] [5, 1, 2]", "[1, 2, 5] [5]"],
      "skip_while only drops the leading items; once the test fails it lets everything through",
      """The first item that is not below 3 is the 5, and from there on `skip_while` stops testing, so the later
      1 and 2 are kept. `filter` tests every item, so it keeps only the 5."""),

    # ── Medium and hard ────────────────────────────────────────────────────
    q("f32-sum-hides-the-error", r'''
        fn main() {
            let a = 0.1 + 0.2 == 0.3;
            let b = 0.1f32 + 0.2f32 == 0.3f32;
            println!("{} {}", a, b);
        }
    ''', "false true", ["true true", "false false", "true false"],
      "With less precision the rounding error can vanish, so float equality results change with the type",
      """As f64, 0.1 + 0.2 lands just above 0.3. In f32 there are far fewer digits, and the rounded sum happens to
      be exactly the f32 closest to 0.3. Neither result makes `==` a good way to compare floats."""),

    q("nan-is-ignored-by-max", r'''
        fn main() {
            let a = f64::NAN.max(1.0);
            let b = 2.0f64.min(f64::NAN);
            let c = [1.0, f64::NAN, 3.0].iter().cloned().fold(0.0, f64::max);
            println!("{} {} {}", a, b, c);
        }
    ''', "1 2 3", ["NaN NaN NaN", "1 NaN 3", "1 2 NaN"],
      "f64::max and min return the other value when one side is NaN",
      """Unlike `>` and `<`, the `max` and `min` methods treat NaN as missing data and return the number. That
      is why folding with `f64::max` skips the NaN in the middle and finishes with 3."""),

    q("nth-consumes-what-it-skips", r'''
        fn main() {
            let mut it = 1..10;
            let a = it.nth(2);
            let b = it.next();
            let c = it.nth(0);
            println!("{:?} {:?} {:?}", a, b, c);
        }
    ''', "Some(3) Some(4) Some(5)", ["Some(3) Some(3) Some(4)", "Some(2) Some(3) Some(4)",
                                    "Some(3) Some(4) Some(4)"],
      "nth(n) throws away n items and then returns the next one, and the iterator stays advanced",
      """`nth(2)` skips 1 and 2 and returns 3, so the following `next` gives 4. `nth(0)` is the same as `next`, so
      it returns 5."""),

    q("successors-includes-the-failing-value", r'''
        use std::iter::successors;

        fn main() {
            let step = |&x: &u32| if x < 50 { Some(x * 3) } else { None };
            let v: Vec<u32> = successors(Some(1), step).collect();
            println!("{:?}", v);
        }
    ''', "[1, 3, 9, 27, 81]", ["[1, 3, 9, 27]", "[1, 3, 9, 27, 81, 243]", "[3, 9, 27, 81]"],
      "The closure sees the previous item and decides whether there is a next one",
      """From 27 the closure still says Some(81), because it only checks the value it was given. When it receives
      81 it returns None. So the first value that is 50 or more is included, and the sequence stops right after
      it."""),

    q("step-by-and-rev-order", r'''
        fn main() {
            let a: Vec<_> = (1..11).rev().step_by(4).collect();
            let b: Vec<_> = (1..11).step_by(4).rev().collect();
            println!("{:?} {:?}", a, b);
        }
    ''', "[10, 6, 2] [9, 5, 1]", ["[10, 6, 2] [10, 6, 2]", "[1, 5, 9] [9, 5, 1]",
                                 "[10, 7, 4, 1] [9, 5, 1]"],
      "step_by counts from the front of whatever it is given, so the adaptor order matters",
      """Reversing first makes the stepping start at 10: 10, 6, 2. Stepping first picks 1, 5, 9 from the front,
      and reversing that sequence gives 9, 5, 1."""),

    q("scan-stops-on-none", r'''
        fn main() {
            let v: Vec<i32> = (1..10)
                .scan(0, |acc, x| {
                    *acc += x;
                    if *acc > 10 { None } else { Some(*acc) }
                })
                .collect();
            println!("{:?}", v);
        }
    ''', "[1, 3, 6, 10]", ["[1, 3, 6, 10, 15, 21, 28, 36, 45]", "[1, 3, 6, 10, 15]", "[1, 3, 6]"],
      "scan carries state between items, and returning None ends the whole iteration",
      """The running totals are 1, 3, 6, 10 and then 15. At 15 the closure returns None, and `scan` stops there
      instead of skipping that item. The remaining numbers are never looked at."""),

    q("collect-into-result-stops-early", r'''
        use std::cell::Cell;

        fn main() {
            let n = Cell::new(0);
            let r: Result<Vec<i32>, _> = ["1", "x", "3", "y"].iter()
                .map(|s| { n.set(n.get() + 1); s.parse::<i32>() })
                .collect();
            println!("{} {}", r.is_err(), n.get());
        }
    ''', "true 2", ["true 4", "false 2", "true 1"],
      "Collecting into Result stops at the first Err and never looks at the rest",
      """The iterator is pulled lazily. After "1" parses and "x" fails, `collect` has its answer, an `Err`, so the
      closure runs only twice. Collecting into `Option<Vec<_>>` stops at the first None in the same way."""),

    q("option-zip-xor-filter", r'''
        fn main() {
            let a = Some(1).zip(Some('a'));
            let b = Some(1).xor(Some(2));
            let c = Some(4).filter(|x| x % 2 == 1);
            let d = Some(Some(3)).flatten().or(Some(0));
            println!("{:?} {:?} {:?} {:?}", a, b, c, d);
        }
    ''', "Some((1, 'a')) None None Some(3)",
      ["Some((1, 'a')) Some(1) None Some(3)", "Some(1) None None Some(3)",
       "Some((1, 'a')) None Some(4) Some(3)"],
      "xor wants exactly one Some; filter turns a failing Some into None; or only fills a None",
      """`zip` pairs two Somes. With two Somes, `xor` gives None because both are present. `filter` drops the 4
      since it is not odd, and `or(Some(0))` does nothing when the value is already Some(3)."""),

    q("parse-error-messages", r'''
        fn main() {
            let a = "".parse::<i32>().unwrap_err();
            let b = "99999999999".parse::<i32>().unwrap_err();
            let c = "-1".parse::<u8>().unwrap_err();
            println!("{} | {} | {}", a, b, c);
        }
    ''', "cannot parse integer from empty string | number too large to fit in target type"
         " | invalid digit found in string",
      ["invalid digit found in string | number too large to fit in target type"
       " | number too small to fit in target type",
       "cannot parse integer from empty string | number too large to fit in target type"
       " | number too small to fit in target type",
       "cannot parse integer from empty string | invalid digit found in string"
       " | invalid digit found in string"],
      "Each failed parse has its own message; for an unsigned type a minus sign is an invalid digit",
      """An empty string, an overflow and a stray character are three different error kinds. For an unsigned type
      the `-` is not accepted at all, so "-1" is an invalid digit rather than too small."""),

    q("rc-make-mut-clones-when-shared", r'''
        use std::rc::Rc;

        fn main() {
            let mut a = Rc::new(5);
            let b = Rc::clone(&a);
            *Rc::make_mut(&mut a) += 1;
            println!("{} {} {}", a, b, Rc::strong_count(&b));
        }
    ''', "6 5 1", ["6 6 2", "6 5 2", "5 5 2"],
      "Rc::make_mut copies the value first if anyone else shares it (clone on write)",
      """Because `b` also points at the 5, `make_mut` cannot change it in place. It clones the value into a new
      allocation for `a`, which becomes 6, and `b` keeps the old one, now with a strong count of 1."""),

    q("rc-weak-upgrade", r'''
        use std::rc::Rc;

        fn main() {
            let a = Rc::new(5);
            let w = Rc::downgrade(&a);
            let before = w.upgrade().is_some();
            let (s, k) = (Rc::strong_count(&a), Rc::weak_count(&a));
            drop(a);
            println!("{} {} {} {}", before, s, k, w.upgrade().is_none());
        }
    ''', "true 1 1 true", ["true 2 1 true", "true 1 0 true", "true 1 1 false"],
      "A Weak does not keep the value alive, and upgrade() returns None once the last Rc is gone",
      """Creating the Weak raises only the weak count, so the strong count stays at 1. The temporary Rc from the
      first `upgrade` has already been dropped. After `drop(a)` nothing owns the 5, so `upgrade` gives None."""),

    q("counter-iterator-pipeline", r'''
        struct Counter(u32);

        impl Iterator for Counter {
            type Item = u32;
            fn next(&mut self) -> Option<u32> {
                if self.0 < 5 { self.0 += 1; Some(self.0) } else { None }
            }
        }

        fn main() {
            let s: u32 = Counter(0).zip(Counter(0).skip(1)).map(|(a, b)| a * b)
                .filter(|x| x % 3 == 0).sum();
            println!("{}", s);
        }
    ''', "18", ["40", "6", "12"],
      "A custom Iterator gets every adaptor for free; zip pairs 1..5 with 2..5 and stops at the shorter",
      """The pairs are (1,2), (2,3), (3,4), (4,5), with products 2, 6, 12 and 20. Only 6 and 12 are multiples of 3,
      and they add up to 18."""),

    q("blanket-impl-for-display", r'''
        use std::fmt::Display;

        trait Twice { fn twice(&self) -> String; }

        impl<T: Display> Twice for T {
            fn twice(&self) -> String { format!("{}{}", self, self) }
        }

        fn main() {
            println!("{} {} {}", 5.twice(), "ab".twice(), 1.5.twice());
        }
    ''', "55 abab 1.51.5", ["10 abab 3", "55 abab 3", "55 ab 1.5"],
      "A blanket impl gives the method to every type that meets the bound, literals included",
      """`impl<T: Display> Twice for T` covers integers, strings and floats alike. The method builds a string by
      printing the value twice, so 5 becomes "55" (text, not 10)."""),

    q("associated-const-through-generics", r'''
        trait Shape { const SIDES: u32; fn sides(&self) -> u32 { Self::SIDES } }
        struct Tri;
        struct Sq;
        impl Shape for Tri { const SIDES: u32 = 3; }
        impl Shape for Sq {
            const SIDES: u32 = 4;
            fn sides(&self) -> u32 { Self::SIDES * 10 }
        }

        fn total<A: Shape, B: Shape>() -> u32 { A::SIDES + B::SIDES }

        fn main() {
            println!("{} {} {}", Tri.sides(), Sq.sides(), total::<Tri, Sq>());
        }
    ''', "3 40 7", ["3 4 7", "3 40 70", "4 40 7"],
      "A default method sees each type's own constant; a type can override the method itself",
      """`Tri` uses the default `sides`, which reads its own SIDES, 3. `Sq` overrides the method to multiply by
      10. `total::<Tri, Sq>()` needs no value at all, because the constants belong to the types."""),

    q("sort-by-two-keys", r'''
        fn main() {
            let mut v = vec![(1, 'b'), (2, 'a'), (3, 'b'), (4, 'a')];
            v.sort_by(|x, y| x.1.cmp(&y.1).then_with(|| y.0.cmp(&x.0)));
            println!("{:?}", v);
        }
    ''', "[(4, 'a'), (2, 'a'), (3, 'b'), (1, 'b')]",
      ["[(2, 'a'), (4, 'a'), (1, 'b'), (3, 'b')]", "[(2, 'a'), (4, 'a'), (3, 'b'), (1, 'b')]",
       "[(4, 'a'), (2, 'a'), (1, 'b'), (3, 'b')]"],
      "then_with breaks ties in the first key; swapping the operands reverses that key",
      """The letters decide first, a before b. Inside each letter the second comparison is written `y.0.cmp(&x.0)`
      with the operands flipped, so the numbers come out largest first."""),

    q("hex-format-of-negatives", r'''
        fn main() {
            println!("{:x} {:#b} {:#06x} {:o}", -1i8, 5u8, 255, 64);
        }
    ''', "ff 0b101 0x00ff 100", ["-1 0b101 0x00ff 100", "ff 101 0xff 100", "ff 0b101 0x00ff 64"],
      "{:x} shows the two's-complement bits of a negative number; # adds the prefix, and 0 pads after it",
      """An i8 of -1 is all ones, which is `ff` in hex. `#` adds `0b` or `0x`, and in `{:#06x}` the width 6 counts
      the prefix, so 255 becomes 0x00ff. `{:o}` of 64 is 100 in octal."""),

    q("peekable-run-lengths", r'''
        fn main() {
            let mut it = "aaabcc".chars().peekable();
            let mut out = String::new();
            while let Some(c) = it.next() {
                let mut n = 1;
                while it.peek() == Some(&c) {
                    it.next();
                    n += 1;
                }
                out.push_str(&format!("{}{}", c, n));
            }
            println!("{}", out);
        }
    ''', "a3b1c2", ["a3bc2", "a2b0c1", "a1b1c1"],
      "peek looks at the next item without consuming it, which is what makes run counting easy",
      """The outer `next` takes the first `a`, then `peek` shows further a's without using them up, and `next`
      inside the loop eats them one by one. Each letter gets its count, including 1 for the single b."""),

    q("retain-closure-keeps-state", r'''
        fn main() {
            let mut v = vec![3, 1, 3, 2, 1];
            let mut seen = Vec::new();
            v.retain(|x| {
                if seen.contains(x) { false } else { seen.push(*x); true }
            });
            println!("{:?} {:?}", v, seen);
        }
    ''', "[3, 1, 2] [3, 1, 2]", ["[1, 2] [3, 1, 2]", "[3, 1, 3, 2, 1] [3, 1, 2]",
                                "[3, 1, 2] [3, 1, 2, 3, 1]"],
      "retain visits the items once, in order, with a closure that may keep its own state",
      """The closure is `FnMut`, so it can remember what it has seen. It keeps the first 3, 1 and 2 and rejects
      the later repeats. That is a de-duplication that, unlike `dedup`, also removes non-adjacent copies."""),

    q("let-else-diverges", r'''
        fn pick(s: &str) -> i32 {
            let Some(first) = s.split(',').next().filter(|t| !t.is_empty()) else {
                return -1;
            };
            let Ok(n) = first.parse::<i32>() else { return -2; };
            n
        }

        fn main() {
            println!("{} {} {}", pick("7,8"), pick(",1"), pick("x"));
        }
    ''', "7 -1 -2", ["7 1 -2", "7 -1 x", "7 -2 -2"],
      "let ... else binds on success and must leave the function (or loop) on failure",
      """For "7,8" both patterns match and the value 7 flows on. For ",1" the first piece is empty, `filter` turns
      it into None and the first `else` returns -1. For "x" the first piece exists but does not parse."""),

    q("drain-removes-even-if-unused", r'''
        fn main() {
            let mut v = vec![1, 2, 3, 4, 5];
            v.drain(..2);
            let d: Vec<_> = v.drain(1..).take(1).collect();
            println!("{:?} {:?}", v, d);
        }
    ''', "[3] [4]", ["[3, 5] [4]", "[3, 4, 5] [4]", "[1, 2, 3] [4]"],
      "Dropping a Drain removes the whole range, whether or not you read the items",
      """`v.drain(..2)` is never iterated, but dropping it at the end of the statement still deletes 1 and 2. The
      second drain removes 4 and 5, and although `take(1)` only reads the 4, the 5 goes too when the iterator is
      dropped."""),

    q("closure-captures-only-its-fields", r'''
        struct S { a: String, b: String }

        fn main() {
            let mut s = S { a: "a".into(), b: "b".into() };
            let mut c = || s.a.push('x');
            s.b.push('y');
            c();
            println!("{} {}", s.a, s.b);
        }
    ''', "ax by", ["ax b", "a by", "ax bx"],
      "In edition 2021 a closure captures the individual field it uses, not the whole struct",
      """The closure only touches `s.a`, so only that field is borrowed mutably, and the main body can still change
      `s.b` meanwhile. Before edition 2021 the closure borrowed all of `s` and this would not compile."""),

    q("numeric-is-not-a-digit", r'''
        fn main() {
            let c = '\u{663}';
            let (n, d, a) = (c.is_numeric(), c.to_digit(10), c.is_ascii_digit());
            println!("{} {:?} {}", n, d, a);
        }
    ''', "true None false", ["true Some(3) true", "false None false", "true Some(3) false"],
      "is_numeric accepts digits of every script; to_digit and is_ascii_digit only accept ASCII ones",
      """U+0663 is an Arabic-Indic three. Unicode classes it as a number, so `is_numeric` is true, but `to_digit`
      and `is_ascii_digit` only know 0 to 9, so they say no."""),

    q("checked-division-cases", r'''
        fn main() {
            let a = 10i32.checked_div(0);
            let b = i32::MIN.checked_div(-1);
            let c = 7i32.checked_rem(-1);
            let d = (-7i32).checked_rem_euclid(3);
            println!("{:?} {:?} {:?} {:?}", a, b, c, d);
        }
    ''', "None None Some(0) Some(2)",
      ["None Some(-2147483648) Some(0) Some(2)", "None None Some(0) Some(-1)", "None None None Some(2)"],
      "Division can fail in two ways: dividing by zero, and MIN / -1, which does not fit",
      """The true quotient of i32::MIN and -1 is 2147483648, one more than i32::MAX, so `checked_div` returns None.
      Dividing 7 by -1 has remainder 0, and the Euclidean remainder of -7 modulo 3 is 2."""),

    q("char-arithmetic-and-ranges", r'''
        fn main() {
            let a = (b'a' + 3) as char;
            let b = char::from(b'a' + 3);
            let c: String = ('a'..='e').rev().collect();
            let d: String = ('a'..='e').step_by(2).collect();
            println!("{} {} {} {}", a, b, c, d);
        }
    ''', "d d edcba ace", ["d 100 edcba ace", "d d abcde ace", "d d edcba abcde"],
      "chars are not numbers, but you can add to the byte and convert back, or iterate a char range",
      """Arithmetic is done on the u8 value of the letter, 97 + 3 = 100, and `as char` or `char::from` turns that
      back into d. Inclusive char ranges are iterators too, so `rev` and `step_by` work on them."""),

    q("swap-and-replace", r'''
        use std::mem;

        fn main() {
            let mut a = vec![1];
            let mut b = vec![2, 3];
            mem::swap(&mut a, &mut b);
            let old = mem::replace(&mut a, vec![9]);
            println!("{:?} {:?} {:?}", a, b, old);
        }
    ''', "[9] [1] [2, 3]", ["[9] [1] [1]", "[2, 3] [1] [9]", "[9] [2, 3] [1]"],
      "swap exchanges two places; replace stores a new value and hands back the old one",
      """After the swap, `a` is [2, 3] and `b` is [1]. `replace` stores [9] in `a` and returns what was there, which
      is [2, 3]. No value is cloned or dropped in the process."""),
)
