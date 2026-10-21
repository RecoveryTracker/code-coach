"""Gotchas, Rust: rustc -O, edition 2021; portability notes are in langs.py (the `rust` entry)."""

from __future__ import annotations

from .items import Item, make

q = make("rust")

ITEMS: tuple[Item, ...] = (
    q("shadowing", r'''
        fn main() {
            let x = 5;
            let x = x * 2;
            {
                let x = x + 1;
                let _ = x;
            }
            println!("{}", x);
        }
    ''', "10", ["11", "5", "Error"],
      "let x again makes a new variable; an inner block's x vanishes at its brace",
      """`let x = x * 2` shadows the first x with a new one holding 10, so no mutation (and no `mut`) is needed.
      The x inside the braces is a third variable that only lives until the closing brace, so the outer x is
      still 10."""),

    q("as-truncates", r'''
        fn main() {
            let a = 300i32 as u8;
            let b = -1i8 as u8;
            println!("{} {}", a, b);
        }
    ''', "44 255", ["300 255", "44 -1", "255 255"],
      "`as` between integer sizes keeps the low bits and never complains",
      """300 is 0x12C and a u8 keeps only the low byte, 0x2C, which is 44. -1 as an i8 is all ones, and read as an
      unsigned byte that is 255. `as` never panics or saturates for integers; use `try_from` when you need to
      know it did not fit."""),

    q("len-is-bytes", r'''
        fn main() {
            let s = "h\u{e9}llo";
            println!("{} {}", s.len(), s.chars().count());
        }
    ''', "6 5", ["5 5", "6 6", "5 6"],
      "A string's len() counts UTF-8 bytes, not characters",
      """The letter e-acute is one character but takes two bytes in UTF-8, so the string is 6 bytes long and
      `chars().count()` finds 5 characters. Indexing and slicing a `str` use byte positions for the same
      reason."""),
)
