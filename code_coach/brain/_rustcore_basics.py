"""Rust core pack, part 1: Rust Eval and Strings & Formatting.

Every answer is worked out by hand in Python (truncating division by counting, wrapping by modular arithmetic, padding by
building the string); tests/rust_oracle.py then builds every template with the real rustc, debug and -O. Prompts are the
BODY of `main` (they print their own answer with println!) unless they define `fn main`.
"""

from __future__ import annotations

from ._c_model import fixed
from ._model import Maker, tdiv, tmod
from ._rs_model import RS, Retry, debug, fmt_float, fmt_float_debug, show


def T(*lines: str) -> str:
    return "\n".join(lines)


def wrap32(v: int) -> int:
    return (v + 2 ** 31) % 2 ** 32 - 2 ** 31


def isqrt(n: int) -> int:
    r = 0
    while (r + 1) * (r + 1) <= n:
        r += 1
    return r


def _is_neg(sign: str) -> bool:
    return sign == "-"


# ── 1. Rust Eval ────────────────────────────────────────────────────────

EVAL: list[Maker] = [
    RS(r'println!("{}", -$m / $a);', lambda p: tdiv(-p["m"], p["a"]), "Integer division cuts toward zero, so the negative quotient is rounded up."),
    RS(r'println!("{}", -$m % $a);', lambda p: tmod(-p["m"], p["a"]), "The remainder takes the sign of the left operand."),
    RS(r'println!("{}", $m % -$a);', lambda p: tmod(p["m"], -p["a"]), "The remainder takes the sign of the left operand, whatever the right one is."),
    RS(r'let x: i32 = -$m;' + "\n" + r'println!("{}", x / $a * $a + x % $a);', lambda p: -p["m"], "Quotient times divisor plus remainder always rebuilds the original number."),
    RS(r'println!("{}", (-${m}i32).rem_euclid($a));', lambda p: (-p["m"]) % p["a"], "rem_euclid never gives a negative result, unlike the % operator."),
    RS(r'println!("{}", (-${m}i32).div_euclid($a));', lambda p: (-p["m"]) // p["a"], "div_euclid rounds down so that rem_euclid stays non-negative."),
    RS(T(r'let f = -$a.${b}5;', r'println!("{}", f as i32);'), lambda p: -p["a"], "Casting a float to an integer truncates toward zero."),
    RS(T(r'let f = $a.${b}5_f64;', r'println!("{}", (f * 10.0) as i32);'), lambda p: p["a"] * 10 + p["b"], "Multiplying by ten and truncating keeps the first decimal digit."),
    RS(T(r'let x: i32 = $big;', r'println!("{}", x as u8);'), lambda p: p["big"] % 256, "Casting to u8 keeps only the low eight bits."),
    RS(T(r'let x: i32 = -$a;', r'println!("{}", x as u8);'), lambda p: 256 - p["a"], "A negative i32 cast to u8 wraps around from 256."),
    RS(T(r'let x: u8 = $u;', r'println!("{}", x as i8);'), lambda p: p["u"] - 256, "A u8 above 127 wraps to a negative i8."),
    RS(T(r'let x = $m as f64 / $h.0;', r'println!("{}", x);'), lambda p: fmt_float(p["m"] / p["h"]), "Display prints a whole-number float without the .0."),
    RS(r'println!("{:?}", $a as f64 * 2.0);', lambda p: fmt_float_debug(p["a"] * 2.0), "Debug keeps the .0 of a whole-number float."),
    RS(r'println!("{}", $a.0 * $b.0);', lambda p: fmt_float(p["a"] * p["b"] * 1.0), "Display prints the product as a plain whole number."),
    RS(r'println!("{:?}", $a.0 + $b.5);', lambda p: fmt_float_debug(p["a"] + p["b"] + 0.5), "Debug prints the decimal part of the float sum."),
    RS(r'''println!("{}", (b'$x' + $a) as char);''', lambda p: chr(ord(p["x"]) + p["a"]), "Adding to the byte value moves along the alphabet."),
    RS(r'''println!("{}", ('$x' as u8 - b'a') as i32);''', lambda p: ord(p["x"]) - 97, "The letter's position in the alphabet, counting from 0."),
    RS(r'''println!("{}", '$x' as u32);''', lambda p: ord(p["x"]), "A char casts to its Unicode code point."),
    RS(r'''println!("{}", (b'0' + $a) as char);''', lambda p: str(p["a"]), "Adding a digit to the byte of '0' gives that digit's character."),
    RS(r'println!("{}", ${m}u8.wrapping_add($u));', lambda p: (p["m"] + p["u"]) % 256, "wrapping_add wraps around past 255."),
    RS(r'println!("{:?}", ${u}u8.checked_add($m));', lambda p: debug(("Some", p["u"] + p["m"])) if p["u"] + p["m"] <= 255 else "None", "checked_add gives None when the sum does not fit in a u8."),
    RS(r'println!("{}", ${a}u8.saturating_sub($b));', lambda p: max(0, p["a"] - p["b"]), "saturating_sub stops at zero instead of going negative."),
    RS(r'println!("{:?}", ${u}u8.overflowing_mul($a));', lambda p: f"({p['u'] * p['a'] % 256}, {'true' if p['u'] * p['a'] > 255 else 'false'})", "overflowing_mul returns the wrapped value and whether it wrapped."),
    RS(r'println!("{}", ${a}i64.pow($b));', lambda p: p["a"] ** p["b"], "pow multiplies the base by itself the given number of times."),
    RS(r'println!("{}", (-${a}i32).abs() + (${b}i32 - $c).abs());', lambda p: p["a"] + abs(p["b"] - p["c"]), "abs drops the sign of each part before they are added."),
    RS(r'println!("{}", ${a}i32.min($b).max($c));', lambda p: max(min(p["a"], p["b"]), p["c"]), "min is applied first, then max on its result."),
    RS(T(r'let x = $a;', r'let x = x * $b;', r'{ let x = x + $c; }', r'println!("{}", x);'), lambda p: p["a"] * p["b"], "The inner x shadows only inside its block; outside the second x is used."),
    RS(T(r'let x = "$n";', r'let x = x.len();', r'println!("{}", x * $a);'), lambda p: 2 * p["a"], "Shadowing can change the type: x is now the length of the text, 2."),
    RS(T(r'let x = { let y = $a; y * y + $b };', r'println!("{}", x);'), lambda p: p["a"] ** 2 + p["b"], "A block's last expression, without a semicolon, is its value."),
    RS(T(r'let x = { $a + $b; };', r'println!("{:?}", x);'), "()", "A semicolon turns the last line into a statement, so the block is the unit value."),
    RS(T(r'let n = $n;', r'let s = if n % 2 == 0 { n / 2 } else { 3 * n + 1 };', r'println!("{}", s);'), lambda p: p["n"] // 2 if p["n"] % 2 == 0 else 3 * p["n"] + 1, "if is an expression: the matching branch's value is stored."),
    RS(T(r'let r = if $a > $b { "big" } else { "small" };', r'println!("{}", r);'), lambda p: "big" if p["a"] > p["b"] else "small", "The condition picks which branch's value r gets."),
    RS(r'println!("{}", ($m as f64).sqrt() as i32);', lambda p: isqrt(p["m"]), "sqrt gives a float; the cast truncates it."),
    RS(r'println!("{}", $n / $a * $a);', lambda p: p["n"] // p["a"] * p["a"], "Integer division drops the remainder before the multiplication."),
    RS(r'println!("{}", $a + $b * $c - $d / 2);', lambda p: p["a"] + p["b"] * p["c"] - p["d"] // 2, "Multiplication and division bind tighter; d / 2 is integer division."),
    RS(r'println!("{}", ${n}u32 >> $k);', lambda p: p["n"] >> p["k"], "Shifting right by k divides by 2 to the k, dropping the rest."),
    RS(r'println!("{}", ${a}u32 << $b);', lambda p: p["a"] << p["b"], "Shifting left by b multiplies by 2 to the b."),
    RS(r'println!("{}", -${a}i32.abs());', lambda p: -p["a"], "The method call binds tighter than the minus sign, so abs runs first."),
    RS(r'println!("{}", i32::MAX.wrapping_add($k));', lambda p: wrap32(2 ** 31 - 1 + p["k"]), "Adding past i32::MAX wraps around to the most negative values."),
    RS(r'println!("{}", u8::MAX as u32 + $a);', lambda p: 255 + p["a"], "The cast happens first, so the sum is done in u32 without overflow."),
    RS(r'println!("{}", (${a}i64 - $m) / $b);', lambda p: tdiv(p["a"] - p["m"], p["b"]), "A negative quotient is cut toward zero."),
    RS(r'println!("{}", (${a}i32 - $m).rem_euclid($b));', lambda p: (p["a"] - p["m"]) % p["b"], "rem_euclid is a remainder that is never negative."),
    RS(r'println!("{}", $n % $a == 0 && $n > $m);', lambda p: p["n"] % p["a"] == 0 and p["n"] > p["m"], "Both sides of && must be true; n is below 50."),
    RS(r'println!("{}", ${n}i32 as f32 / 4.0);', lambda p: fmt_float(p["n"] / 4), "A quarter of n, printed without .0 when it is whole."),
    RS(T(r'let x = -$a.5_f64;', r'println!("{}", x.round());'), lambda p: -(p["a"] + 1), "round goes away from zero on a half."),
    RS(T(r'let x = $a.5_f64;', r'println!("{}", x.round());'), lambda p: p["a"] + 1, "round goes up (away from zero) on a half."),
    RS(T(r'let x = -$a.5_f64;', r'println!("{}", x.floor());'), lambda p: -(p["a"] + 1), "floor goes toward minus infinity, so a negative half goes down."),
    RS(T(r'let x = -$a.5_f64;', r'println!("{}", x.ceil());'), lambda p: -p["a"], "ceil goes toward plus infinity, so a negative half goes up."),
    RS(r'''println!("{}", $m as u8 as char);''', lambda p: chr(p["m"]), "A number cast to u8 and then char is that ASCII character."),
]


# ── 2. Strings & Formatting ─────────────────────────────────────────────

def pad(s: str, width: int, align: str = "<", fill: str = " ") -> str:
    n = width - len(s)
    if n <= 0:
        return s
    if align == "<":
        return s + fill * n
    if align == ">":
        return fill * n + s
    left = n // 2
    return fill * left + s + fill * (n - left)


def _debug_str(s: str) -> str:
    return '"' + s + '"'


STRINGS: list[Maker] = [
    RS(r'println!("{}", "$w".len());', lambda p: p["L"], "len counts bytes, and each ASCII letter is one byte."),
    RS(r'let s = "$w\u{e9}";' + "\n" + r'println!("{} {}", s.len(), s.chars().count());', lambda p: f"{p['L'] + 2} {p['L'] + 1}", "The accented letter is two bytes but one char."),
    RS(r'println!("{}", "$w".to_uppercase());', lambda p: p["w"].upper(), "to_uppercase makes a new string with every letter capitalised."),
    RS(r'println!("{}", "  $w  ".trim().len());', lambda p: p["L"], "trim removes the spaces at both ends, leaving only the word."),
    RS(r'println!("|{}|", "  $w  ".trim_start());', lambda p: "|" + p["w"] + "  |", "trim_start removes only the leading spaces."),
    RS(r'println!("|{}|", "  $w  ".trim_end());', lambda p: "|  " + p["w"] + "|", "trim_end removes only the trailing spaces."),
    RS(r'println!("{}", "$w  $z   $w".split_whitespace().count());', 3, "split_whitespace skips runs of blanks, so there are three words."),
    RS(r'''println!("{}", "$x  $y".split(' ').count());''', 3, "split(' ') keeps the empty piece between two spaces."),
    RS(r'println!("{}", "$w".replace("$f", "$X"));', lambda p: p["w"].replace(p["f"], p["X"]), "replace changes every match, not just the first."),
    RS(r'''println!("{}", "$w".contains('$x'));''', lambda p: p["x"] in p["w"], "contains tells whether the letter appears anywhere."),
    RS(r'''println!("{}", "$w".starts_with('$x'));''', lambda p: p["w"].startswith(p["x"]), "starts_with looks only at the first character."),
    RS(r'''println!("{}", "$w".ends_with('$x'));''', lambda p: p["w"].endswith(p["x"]), "ends_with looks only at the last character."),
    RS(r'println!("{}", &"$w"[$i..]);', lambda p: p["w"][p["i"]:], "A slice from byte i to the end."),
    RS(r'println!("{}", &"$w"[..$i]);', lambda p: p["w"][:p["i"]], "A slice stops before byte i."),
    RS(r'println!("{}", &"$w"[$j..=$j]);', lambda p: p["w"][p["j"]], "An inclusive range of one byte is a single letter."),
    RS(r'println!("|{:>$a}|", "$w");', lambda p: "|" + pad(p["w"], p["a"], ">") + "|", "{:>N} right-aligns in N columns; a longer text is not cut."),
    RS(r'println!("|{:<$a}|", "$w");', lambda p: "|" + pad(p["w"], p["a"], "<") + "|", "{:<N} pads on the right."),
    RS(r'println!("|{:^$a}|", "$x");', lambda p: "|" + pad(p["x"], p["a"], "^") + "|", "{:^N} centres; the extra space goes on the right."),
    RS(r'println!("|{:*^$n}|", "$w");', lambda p: "|" + pad(p["w"], p["n"], "^", "*") + "|", "The character before the alignment is the fill."),
    RS(r'println!("|{:->$a}|", $n);', lambda p: "|" + pad(str(p["n"]), p["a"], ">", "-") + "|", "The fill is a dash, right-aligned."),
    RS(r'println!("{:05}", $n);', lambda p: f"{p['n']:05d}", "{:05} pads a number with zeros to 5 digits."),
    RS(r'println!("{:05}", -$a);', lambda p: "-" + f"{p['a']:04d}", "The width counts the minus sign, so there are four digits."),
    RS(r'println!("{:.2}", $m as f64 / 3.0);', lambda p: fixed(p["m"] / 3.0, 2), "{:.2} rounds to two decimals."),
    RS(r'println!("{:.1}", $m as f64 / 7.0);', lambda p: fixed(p["m"] / 7.0, 1), "{:.1} rounds to one decimal."),
    RS(r'println!("{:.0}", $m as f64 / 7.0);', lambda p: fixed(p["m"] / 7.0, 0), "{:.0} rounds to a whole number and prints no point."),
    RS(r'println!("{:.2}", $a);'.replace("$a", "$a.0"), lambda p: f"{p['a']}.00", "Precision pads with zeros: 2 decimals even for a whole float."),
    RS(r'println!("|{:7.2}|", $m as f64 / 3.0);', lambda p: "|" + pad(fixed(p["m"] / 3.0, 2), 7, ">") + "|", "Width 7 includes the decimals and the point; numbers go right."),
    RS(r'println!("{:+}", $a - $b);', lambda p: f"{p['a'] - p['b']:+d}", "{:+} always shows the sign."),
    RS(r'println!("{:x}", $m);', lambda p: format(p["m"], "x"), "{:x} is lowercase hexadecimal."),
    RS(r'println!("{:X}", $u);', lambda p: format(p["u"], "X"), "{:X} is uppercase hexadecimal."),
    RS(r'println!("{:#x}", $u);', lambda p: "0x" + format(p["u"], "x"), "{:#x} adds the 0x prefix."),
    RS(r'println!("{:#06x}", $u);', lambda p: "0x" + format(p["u"], "04x"), "The width counts the 0x, so four digits follow it."),
    RS(r'println!("{:b}", $n);', lambda p: format(p["n"], "b"), "{:b} is binary without padding."),
    RS(r'println!("{:08b}", $m);', lambda p: format(p["m"], "08b"), "{:08b} pads the binary to 8 digits with zeros."),
    RS(r'println!("{:#b}", $a);', lambda p: "0b" + format(p["a"], "b"), "{:#b} adds the 0b prefix."),
    RS(r'println!("{:o}", $m);', lambda p: format(p["m"], "o"), "{:o} is octal."),
    RS(r'println!("{:?}", "$w");', lambda p: _debug_str(p["w"]), "Debug of a string includes the quotes."),
    RS(r'''println!("{:?}", '$x');''', lambda p: "'" + p["x"] + "'", "Debug of a char is in single quotes."),
    RS(r'println!("{:?}", "$w\t$z");', lambda p: '"' + p["w"] + "\\t" + p["z"] + '"', "Debug shows the tab as an escape, \\t, between quotes."),
    RS(r'println!("{:?}", vec!["$w", "$z"]);', lambda p: "[" + _debug_str(p["w"]) + ", " + _debug_str(p["z"]) + "]", "A vector of strs prints its items quoted."),
    RS(r'println!("{1}{0}{1}", "$w", "$x");', lambda p: p["x"] + p["w"] + p["x"], "Numbered placeholders pick arguments by position."),
    RS(T(r'let n = $a;', r'println!("{n}{n}-{}", n + 1);'), lambda p: f"{p['a']}{p['a']}-{p['a'] + 1}", "{n} reads the variable named n; the bare {} takes the argument."),
    RS(r'println!("|{:.3}|", "$w");', lambda p: "|" + p["w"][:3] + "|", "Precision on a string cuts it to that many characters."),
    RS(r'println!("|{:5}|{:5}|", $a, "$x");', lambda p: "|" + pad(str(p["a"]), 5, ">") + "|" + pad(p["x"], 5, "<") + "|", "Numbers are right-aligned by default, text left-aligned."),
    RS(r'println!("{{{}}}", $a);', lambda p: "{" + str(p["a"]) + "}", "Doubled braces print a literal brace."),
    RS(r'println!("{:?} {}", $a as f64, $a as f64);', lambda p: f"{p['a']}.0 {p['a']}", "Debug keeps .0 on a whole float; Display drops it."),
    RS(r'''println!("{:?}", "$w".chars().nth($j));''', lambda p: "Some('" + p["w"][p["j"]] + "')", "nth gives an Option of a char, shown in single quotes."),
    RS(r'println!("{}", "$w".chars().nth($j).unwrap());', lambda p: p["w"][p["j"]], "chars().nth(j) is the j-th character, counting from 0."),
    RS(r'println!("{}", "$x".repeat($a));', lambda p: p["x"] * p["a"], "repeat copies the text a number of times."),
    RS(r"""println!("{}", "$a,$b,$c".split(',').map(|s| s.parse::<i32>().unwrap()).sum::<i32>());""", lambda p: p["a"] + p["b"] + p["c"], "Each piece is parsed to a number and the numbers are added."),
    RS(r"""println!("{:?}", "$w=$z".split_once('='));""", lambda p: 'Some(("' + p["w"] + '", "' + p["z"] + '"))', "split_once gives an Option of a pair of strs."),
    RS(r'''println!("{:?}", "$w".find('$f'));''', lambda p: debug(("Some", p["w"].index(p["f"]))), "find gives the byte position of the first match."),
    RS(r'println!("{:?}", "$w".find("zz"));', "None", "No match means None."),
    RS(r'println!("{}", "$w".bytes().map(|b| b as u32).sum::<u32>());', lambda p: sum(ord(c) for c in p["w"]), "Each letter is its ASCII number and the numbers are added."),
    RS(r'println!("{}", "$w".as_bytes()[$j]);', lambda p: ord(p["w"][p["j"]]), "Indexing the bytes gives the number, not the letter."),
    RS(T(r'let mut s = String::from("$w");', r's.push_str("$z");', r"s.push('$x');", r'println!("{} {}", s, s.len());'), lambda p: f"{p['w']}{p['z']}{p['x']} {p['L'] + len(p['z']) + 1}", "push_str and push append; len counts all the bytes."),
    RS(T(r'let mut s = String::from("$w");', r'let c = s.pop();', r'println!("{:?} {}", c, s);'), lambda p: "Some('" + p["w"][-1] + "') " + p["w"][:-1], "pop removes the last char and returns it in an Option."),
    RS(T(r'let mut s = String::from("$w");', r"s.insert(0, '$x');", r'println!("{}", s);'), lambda p: p["x"] + p["w"], "insert puts the char at that byte position."),
    RS(T(r'let mut s = String::from("$w");', r's.truncate($i);', r'println!("{}", s);'), lambda p: p["w"][:p["i"]], "truncate keeps the first i bytes."),
    RS(T(r'let mut s = String::from("$w");', r'let c = s.remove(0);', r'println!("{} {}", c, s);'), lambda p: p["w"][0] + " " + p["w"][1:], "remove takes out the char at that position and returns it."),
    RS(r'println!("{:?}", "$w$z".strip_prefix("$w"));', lambda p: 'Some("' + p["z"] + '")', "strip_prefix returns the rest wrapped in Some when the prefix matches."),
    RS(r'println!("{}", "$w\n$z\n".lines().count());', 2, "lines does not count the empty piece after a final newline."),
    RS(r'println!("{}", "$w\n\n$z".lines().count());', 3, "A blank line in the middle is still a line."),
    RS(r"""println!("{}", "$w\n$z\n".split('\n').count());""", 3, "split on the newline does keep the empty piece at the end."),
    RS(r'println!("{}", "$w" < "$z");', lambda p: p["w"] < p["z"], "Strings compare alphabetically, byte by byte."),
    RS(r'println!("{}", "$w$a$b".chars().filter(|c| c.is_ascii_digit()).count());', 2, "Only the two digits are counted."),
    RS(r'''println!("{}", '$x'.to_ascii_uppercase());''', lambda p: p["X"], "to_ascii_uppercase gives the capital letter."),
    RS(r"""println!("{:?}", '$a'.to_digit(10));""", lambda p: debug(("Some", p["a"])), "to_digit gives an Option of the digit's value."),
    RS(r'println!("{}", "$X$w".to_lowercase());', lambda p: p["x"] + p["w"], "to_lowercase lowers the capital too."),
    RS(r'println!("{}", $big.to_string().len());', 5, "The number written as text has five digits."),
    RS(r'println!("{}", (-$n).to_string());', lambda p: "-" + str(p["n"]), "to_string of a negative number keeps its sign."),
    RS(r'println!("{}", "$w".chars().rev().collect::<String>());', lambda p: p["w"][::-1], "rev walks the chars backwards and collect builds a new String."),
    RS(r'println!("{}", "$w".chars().filter(|&c| "aeiou".contains(c)).count());', lambda p: sum(1 for c in p["w"] if c in "aeiou"), "Each vowel is counted."),
]
