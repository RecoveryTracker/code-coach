"""Forms in Rust: small functions, written the Rust way.

The same exercise as every other language's forms - write the function, and
it is called with inputs you have not seen - through kata/rust_harness.py,
which writes each case into the program as Rust literals and catches a
panic per case. The signature is given in full, because the types are half
of a Rust function: a borrowed `&[i32]` or `&str` in, an owned `Vec` or
`String` out, an `Option` when there might be no answer.

The oracle is Python, as for every kata; the worked answer is checked by
running it through the Rust driver against it.
"""

from __future__ import annotations

from code_coach.kata import Kata

FAMILY = "Rust"


def _sum_positive(nums):
    return sum(n for n in nums if n > 0)


def _count_vowels(text):
    return sum(1 for ch in text.lower() if ch in "aeiou")


def _largest(nums):
    return max(nums) if nums else None


def _reversed_words(text):
    return " ".join(reversed(text.split()))


def _doubled(nums):
    return [n * 2 for n in nums]


def _is_palindrome(text):
    cleaned = [ch.lower() for ch in text if ch.isalnum()]
    return cleaned == cleaned[::-1]


def _first_repeat(nums):
    seen = set()
    for n in nums:
        if n in seen:
            return n
        seen.add(n)
    return None


def _fizz(n):
    out = []
    for i in range(1, n + 1):
        out.append("FizzBuzz" if i % 15 == 0 else "Fizz" if i % 3 == 0 else "Buzz" if i % 5 == 0 else str(i))
    return out


def _running_total(nums):
    out, total = [], 0
    for n in nums:
        total += n
        out.append(total)
    return out


def _mean(nums):
    return sum(nums) / len(nums) if nums else None


def _caesar(text, shift):
    out = []
    for ch in text:
        if "a" <= ch <= "z":
            out.append(chr((ord(ch) - 97 + shift) % 26 + 97))
        else:
            out.append(ch)
    return "".join(out)


def _min_max(nums):
    return [min(nums), max(nums)] if nums else None


RUST_KATAS: tuple[Kata, ...] = (
    Kata(
        id="rust-sum-positive", level=1, language="rust", family=FAMILY, name="sum_positive",
        brief="Add up only the numbers above zero. An empty slice totals 0.",
        params=("nums",), types=("&[i32]",), returns="i32",
        example="sum_positive(&[3, -1, 4]) is 7",
        hint="nums.iter().filter(|&&n| n > 0).sum() - or a for loop over nums with a running total.",
        cases=(([3, -1, 4],), ([],), ([-5, -2],), ([0, 1],), ([10, 20, -30],)),
        solve=_sum_positive,
        checks=((([3, -1, 4],), 7), (([],), 0), (([-5, -2],), 0)),
        rust_answer=(
            "fn sum_positive(nums: &[i32]) -> i32 {\n"
            "    nums.iter().filter(|&&n| n > 0).sum()\n"
            "}\n"
        ),
    ),
    Kata(
        id="rust-count-vowels", level=1, language="rust", family=FAMILY, name="vowel_count",
        brief="How many vowels (a, e, i, o, u, either case) are in the text?",
        params=("text",), types=("&str",), returns="usize",
        example='vowel_count("Rust Lang") is 2',
        hint="text.chars() walks the characters; to_ascii_lowercase() and a match on 'a' | 'e' | ... decide each.",
        cases=(("Rust Lang",), ("",), ("AEIOU",), ("rhythm",), ("Hello, World!",)),
        solve=_count_vowels,
        checks=((("Rust Lang",), 2), (("rhythm",), 0), (("AEIOU",), 5), (("",), 0)),
        rust_answer=(
            "fn vowel_count(text: &str) -> usize {\n"
            "    text.chars()\n"
            "        .filter(|c| matches!(c.to_ascii_lowercase(), 'a' | 'e' | 'i' | 'o' | 'u'))\n"
            "        .count()\n"
            "}\n"
        ),
    ),
    Kata(
        id="rust-doubled", level=1, language="rust", family=FAMILY, name="doubled_all",
        brief="A new Vec with every number doubled. The slice you are given is borrowed: leave it alone.",
        params=("nums",), types=("&[i32]",), returns="Vec<i32>",
        example="doubled_all(&[1, 2, 3]) is vec![2, 4, 6]",
        hint="nums.iter().map(|n| n * 2).collect() builds the new Vec in one go.",
        cases=(([1, 2, 3],), ([],), ([-4],), ([0, 5, 10],)),
        solve=_doubled,
        checks=((([1, 2, 3],), [2, 4, 6]), (([],), [])),
        rust_answer=(
            "fn doubled_all(nums: &[i32]) -> Vec<i32> {\n"
            "    nums.iter().map(|n| n * 2).collect()\n"
            "}\n"
        ),
    ),
    Kata(
        id="rust-largest", level=2, language="rust", family=FAMILY, name="largest",
        brief="The largest number, or None when the slice is empty.",
        params=("nums",), types=("&[i32]",), returns="Option<i32>",
        example="largest(&[3, 9, 2]) is Some(9); largest(&[]) is None",
        hint="nums.iter().max() already returns an Option, of a reference: .copied() turns it into Option<i32>.",
        cases=(([3, 9, 2],), ([],), ([-7],), ([-3, -1, -2],), ([5, 5],)),
        solve=_largest,
        checks=((([3, 9, 2],), 9), (([],), None), (([-3, -1, -2],), -1)),
        rust_answer=(
            "fn largest(nums: &[i32]) -> Option<i32> {\n"
            "    nums.iter().max().copied()\n"
            "}\n"
        ),
    ),
    Kata(
        id="rust-reversed-words", level=2, language="rust", family=FAMILY, name="reversed_words",
        brief="The words of the text in reverse order, joined by single spaces.",
        params=("text",), types=("&str",), returns="String",
        example='reversed_words("one two three") is "three two one"',
        hint="split_whitespace() ignores extra spaces; .rev() turns it round; collect into a Vec<&str> and join(\" \").",
        cases=(("one two three",), ("",), ("single",), ("  lots   of space ",)),
        solve=_reversed_words,
        checks=((("one two three",), "three two one"), (("",), ""), (("  lots   of space ",), "space of lots")),
        rust_answer=(
            "fn reversed_words(text: &str) -> String {\n"
            "    text.split_whitespace().rev().collect::<Vec<&str>>().join(\" \")\n"
            "}\n"
        ),
    ),
    Kata(
        id="rust-running-total", level=2, language="rust", family=FAMILY, name="running_total",
        brief="Each position holds the total of every number up to and including it.",
        params=("nums",), types=("&[i32]",), returns="Vec<i32>",
        example="running_total(&[1, 2, 3]) is vec![1, 3, 6]",
        hint="Keep a `let mut total = 0;` and push total after adding each number.",
        cases=(([1, 2, 3],), ([],), ([5],), ([2, -2, 2],)),
        solve=_running_total,
        checks=((([1, 2, 3],), [1, 3, 6]), (([2, -2, 2],), [2, 0, 2])),
        rust_answer=(
            "fn running_total(nums: &[i32]) -> Vec<i32> {\n"
            "    let mut total = 0;\n"
            "    let mut out = Vec::new();\n"
            "    for n in nums {\n"
            "        total += n;\n"
            "        out.push(total);\n"
            "    }\n"
            "    out\n"
            "}\n"
        ),
    ),
    Kata(
        id="rust-fizz-buzz", level=2, language="rust", family=FAMILY, name="fizz_buzz",
        brief="From 1 to n: \"Fizz\" for multiples of 3, \"Buzz\" for 5, \"FizzBuzz\" for both, otherwise the number.",
        params=("n",), types=("u32",), returns="Vec<String>",
        example='fizz_buzz(5) is ["1", "2", "Fizz", "4", "Buzz"]',
        hint="Test 15 first. i.to_string() makes the number into a String; \"Fizz\".to_string() makes the words one.",
        cases=((5,), (0,), (15,), (3,)),
        solve=_fizz,
        checks=(((5,), ["1", "2", "Fizz", "4", "Buzz"]), ((0,), [])),
        rust_answer=(
            "fn fizz_buzz(n: u32) -> Vec<String> {\n"
            "    (1..=n)\n"
            "        .map(|i| match (i % 3, i % 5) {\n"
            "            (0, 0) => \"FizzBuzz\".to_string(),\n"
            "            (0, _) => \"Fizz\".to_string(),\n"
            "            (_, 0) => \"Buzz\".to_string(),\n"
            "            _ => i.to_string(),\n"
            "        })\n"
            "        .collect()\n"
            "}\n"
        ),
    ),
    Kata(
        id="rust-is-palindrome", level=3, language="rust", family=FAMILY, name="is_palindrome",
        brief="Does it read the same both ways, ignoring case and anything that is not a letter or digit?",
        params=("text",), types=("&str",), returns="bool",
        example='is_palindrome("A man, a plan, a canal: Panama") is true',
        hint="Collect the alphanumeric chars, lower-cased, into a Vec<char>; then compare it with its own reverse.",
        cases=(("A man, a plan, a canal: Panama",), ("",), ("rust",), ("No lemon, no melon",), ("ab",)),
        solve=_is_palindrome,
        checks=((("A man, a plan, a canal: Panama",), True), (("rust",), False), (("",), True)),
        rust_answer=(
            "fn is_palindrome(text: &str) -> bool {\n"
            "    let cleaned: Vec<char> = text\n"
            "        .chars()\n"
            "        .filter(|c| c.is_alphanumeric())\n"
            "        .map(|c| c.to_ascii_lowercase())\n"
            "        .collect();\n"
            "    cleaned.iter().eq(cleaned.iter().rev())\n"
            "}\n"
        ),
    ),
    Kata(
        id="rust-first-repeat", level=3, language="rust", family=FAMILY, name="first_repeat",
        brief="The first number that has already appeared earlier, or None if none repeats.",
        params=("nums",), types=("&[i32]",), returns="Option<i32>",
        example="first_repeat(&[3, 1, 4, 1, 3]) is Some(1)",
        hint="A HashSet remembers what you have seen: insert returns false when the value was already there.",
        cases=(([3, 1, 4, 1, 3],), ([],), ([1, 2, 3],), ([7, 7],), ([5, 6, 6, 5],)),
        solve=_first_repeat,
        checks=((([3, 1, 4, 1, 3],), 1), (([1, 2, 3],), None), (([5, 6, 6, 5],), 6), (([],), None)),
        rust_answer=(
            "fn first_repeat(nums: &[i32]) -> Option<i32> {\n"
            "    let mut seen = std::collections::HashSet::new();\n"
            "    for &n in nums {\n"
            "        if !seen.insert(n) {\n"
            "            return Some(n);\n"
            "        }\n"
            "    }\n"
            "    None\n"
            "}\n"
        ),
    ),
    Kata(
        id="rust-mean", level=3, language="rust", family=FAMILY, name="average_of",
        brief="The average as an f64, or None for an empty slice.",
        params=("nums",), types=("&[i32]",), returns="Option<f64>",
        example="average_of(&[1, 2]) is Some(1.5)",
        hint="Check is_empty() first. Turn the sum and the length into f64 with `as f64` BEFORE dividing.",
        cases=(([1, 2],), ([],), ([4, 4, 4],), ([-3, 3],), ([1, 2, 2],)),
        solve=_mean,
        checks=((([1, 2],), 1.5), (([],), None), (([-3, 3],), 0.0)),
        rust_answer=(
            "fn average_of(nums: &[i32]) -> Option<f64> {\n"
            "    if nums.is_empty() {\n"
            "        return None;\n"
            "    }\n"
            "    let total: i32 = nums.iter().sum();\n"
            "    Some(total as f64 / nums.len() as f64)\n"
            "}\n"
        ),
    ),
    Kata(
        id="rust-caesar", level=4, language="rust", family=FAMILY, name="rotate_letters",
        brief="Shift every small letter a-z forward by shift places, wrapping z round to a. Anything else stays.",
        params=("text", "shift"), types=("&str", "u8"), returns="String",
        example='rotate_letters("abc xyz", 2) is "cde zab"',
        hint="For a small letter: ((c as u8 - b'a' + shift) % 26 + b'a') as char. Map every char, collect into a String.",
        cases=(("abc xyz", 2), ("", 5), ("hello, world!", 13), ("zzz", 1), ("Abc", 1)),
        solve=_caesar,
        checks=((("abc xyz", 2), "cde zab"), (("zzz", 1), "aaa"), (("Abc", 1), "Acd")),
        rust_answer=(
            "fn rotate_letters(text: &str, shift: u8) -> String {\n"
            "    text.chars()\n"
            "        .map(|c| {\n"
            "            if c.is_ascii_lowercase() {\n"
            "                ((c as u8 - b'a' + shift) % 26 + b'a') as char\n"
            "            } else {\n"
            "                c\n"
            "            }\n"
            "        })\n"
            "        .collect()\n"
            "}\n"
        ),
    ),
    Kata(
        id="rust-min-max", level=4, language="rust", family=FAMILY, name="min_max",
        brief="The smallest and largest numbers as a pair, or None when the slice is empty.",
        params=("nums",), types=("&[i32]",), returns="Option<(i32, i32)>",
        example="min_max(&[3, 9, 2]) is Some((2, 9))",
        hint="One pass: start both at the first number, then widen them. Or use iter().min() and max() with `?`.",
        cases=(([3, 9, 2],), ([],), ([4],), ([-1, -5, 0],)),
        solve=_min_max,
        checks=((([3, 9, 2],), [2, 9]), (([],), None), (([4],), [4, 4])),
        rust_answer=(
            "fn min_max(nums: &[i32]) -> Option<(i32, i32)> {\n"
            "    let lo = *nums.iter().min()?;\n"
            "    let hi = *nums.iter().max()?;\n"
            "    Some((lo, hi))\n"
            "}\n"
        ),
    ),
)
