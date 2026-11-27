"""Rust core pack, part 3: Match & Option, Iterator Chains and Vec & Maps.

Every answer is worked out by hand: a loop over a Python list stands in for the iterator, a dict sorted by key for a
BTreeMap, a lexicographic comparison for derived ordering. tests/rust_oracle.py builds every template with the real rustc
(debug and -O). Prompts are the BODY of `main` (they print their own answer) unless they define `fn main`.
"""

from __future__ import annotations

from ._model import Maker
from ._rs_model import RS, Retry, debug
from ._rustcore_basics import T, isqrt


def lst(xs) -> str:
    return "[" + ", ".join(str(x) for x in xs) + "]"


def some(x) -> str:
    return f"Some({x})"


# ── 1. Match & Option ───────────────────────────────────────────────────

def _grade(n: int) -> str:
    if n <= 59:
        return "D"
    if n <= 79:
        return "C"
    if n <= 89:
        return "B"
    return "A"


def _half(x: int):
    return x // 2 if x % 2 == 0 else None


def _opt(x) -> str:
    return "None" if x is None else f"Some({x})"


def _turns(n: int) -> str:
    return "NESW"[n % 4]


MATCH: list[Maker] = [
    RS(T(r'let n = $m;', r'let g = match n { 0..=59 => "D", 60..=79 => "C", 80..=89 => "B", _ => "A" };', r'println!("{}", g);'), lambda p: _grade(p["m"]), "The first range that contains the number decides."),
    RS(T(r'let n: i32 = $a - $b;', r'let s = match n { x if x < 0 => "neg", 0 => "zero", _ => "pos" };', r'println!("{}", s);'), lambda p: "neg" if p["a"] < p["b"] else "pos", "The guard x < 0 is checked first; a and b differ, so never zero."),
    RS(T(r'let x = $n;', r'let y = match x { v if v % 2 == 0 => v / 2, v => 3 * v + 1 };', r'println!("{}", y);'), lambda p: p["n"] // 2 if p["n"] % 2 == 0 else 3 * p["n"] + 1, "The guard picks halving for even numbers, the last arm handles the rest."),
    RS(T(r'let p = ($a % 2, $b % 2);', r'let s = match p { (0, 0) => "ee", (0, _) => "eo", (_, 0) => "oe", _ => "oo" };', r'println!("{}", s);'), lambda p: {(0, 0): "ee", (0, 1): "eo", (1, 0): "oe", (1, 1): "oo"}[(p["a"] % 2, p["b"] % 2)], "Each tuple pattern is tried in order; _ matches anything."),
    RS(T(r'#[derive(Debug)] enum D { N, E, S, W }', r'fn t(d: D) -> D { use D::*; match d { N => E, E => S, S => W, W => N } }', r'fn main() {', r'    let mut d = D::N;', r'    for _ in 0..$n { d = t(d); }', r'    println!("{:?}", d);', r'}'), lambda p: _turns(p["n"]), "Four turns bring the direction back, so only n % 4 matters."),
    RS(T(r'enum S { C(i32), R(i32, i32) }', r'fn main() {', r'    let v = vec![S::C($a), S::R($b, $c)];', r'    let t: i32 = v.iter().map(|s| match s { S::C(r) => 3 * r * r, S::R(w, h) => w * h }).sum();', r'    println!("{}", t);', r'}'), lambda p: 3 * p["a"] ** 2 + p["b"] * p["c"], "Each variant binds its data; the two areas are added."),
    RS(T(r'let o = Some($a);', r'if let Some(x) = o { println!("{}", x + $b); } else { println!("none"); }'), lambda p: p["a"] + p["b"], "The pattern matches Some and binds the number."),
    RS(T(r'let o: Option<i32> = None;', r'if let Some(x) = o { println!("{}", x + $b); } else { println!("none"); }'), "none", "None does not match Some(x), so the else branch runs."),
    RS(T(r'let o = if $a > $b { Some($a) } else { None };', r'let Some(x) = o else { println!("none"); return; };', r'println!("{}", x * 2);'), lambda p: p["a"] * 2 if p["a"] > p["b"] else "none", "let else binds on a match and runs the else block, which must leave, otherwise."),
    RS(r'println!("{:?}", Some($a).map(|x| x * $b));', lambda p: some(p["a"] * p["b"]), "map applies the closure inside the Some."),
    RS(r'println!("{:?}", None::<i32>.map(|x| x * $b));', "None", "map on None does nothing."),
    RS(r'println!("{}", None::<i32>.unwrap_or($a));', lambda p: p["a"], "unwrap_or supplies the fallback for None."),
    RS(r'println!("{}", Some($a).unwrap_or($b));', lambda p: p["a"], "A Some keeps its value; the fallback is ignored."),
    RS(T(r'fn half(x: i32) -> Option<i32> { if x % 2 == 0 { Some(x / 2) } else { None } }', r'fn main() { println!("{:?}", half($n).and_then(half)); }'), lambda p: _opt(_half(p["n"]) and _half(_half(p["n"]))) if _half(p["n"]) is not None else "None", "and_then runs half again only when the first call gave Some."),
    RS(r'println!("{:?}", Some($n).filter(|x| x % $a == 0));', lambda p: some(p["n"]) if p["n"] % p["a"] == 0 else "None", "filter keeps the value only if the test is true."),
    RS(r'println!("{:?}", Some($a).ok_or("none"));', lambda p: f"Ok({p['a']})", "ok_or turns Some(x) into Ok(x)."),
    RS(r'println!("{:?}", None::<i32>.ok_or("none"));', 'Err("none")', "ok_or turns None into the given Err."),
    RS(r'println!("{}", Some($a).is_some() && None::<i32>.is_none());', "true", "Some is_some, None is_none: both true."),
    RS(T(r'fn f(s: &str) -> Result<i32, std::num::ParseIntError> { let n = s.parse::<i32>()?; Ok(n * $a) }', r'fn main() { println!("{:?}", f("$n")); }'), lambda p: f"Ok({p['n'] * p['a']})", "? unwraps the parse and the function wraps the product in Ok."),
    RS(T(r'fn f(s: &str) -> Result<i32, std::num::ParseIntError> { let n = s.parse::<i32>()?; Ok(n * $a) }', r'fn main() { println!("{:?}", f("x$n").ok()); }'), "None", "? returned the parse error early; ok turns the Err into None."),
    RS(T(r'fn f(v: &[i32]) -> Option<i32> { let a = v.first()?; let b = v.get($k)?; Some(a + b) }', r'fn main() { println!("{:?}", f(&[$a, $b, $c])); }'), lambda p: some(p["a"] + [p["a"], p["b"], p["c"]][p["k"]]) if p["k"] < 3 else "None", "The ? returns None as soon as an index is missing."),
    RS(T(r'let v: Vec<i32> = Vec::new();', r'println!("{}", v.first().copied().unwrap_or_default());'), 0, "An empty vector has no first item, and the default of i32 is 0."),
    RS(r'println!("{}", None::<String>.unwrap_or_default().len());', 0, "The default String is empty."),
    RS(r'println!("{}", "$n".parse::<i32>().unwrap_or_default());', lambda p: p["n"], "The text is a number, so the default is not used."),
    RS(r'println!("{}", "x$n".parse::<i32>().unwrap_or_default());', 0, "The parse fails, so the default of i32 is used."),
    RS(T(r'let v = vec![$a, $b, $c];', r'let r = match v.as_slice() { [] => 0, [x] => *x, [x, .., y] => x + y };', r'println!("{}", r);'), lambda p: p["a"] + p["c"], "[x, .., y] matches the first and the last item."),
    RS(T(r'let v: Vec<i32> = vec![$a, $b, $c].into_iter().take($q).collect();', r'let r = match v.as_slice() { [] => 0, [x] => *x, [x, .., y] => x + y };', r'println!("{}", r);'), lambda p: [0, p["a"], p["a"] + p["b"]][p["q"]], "The slice has q items: none, one, or first plus last."),
    RS(T(r'let x = $a;', r'let r = match x { n @ 1..=5 => n * 10, n => n };', r'println!("{}", r);'), lambda p: p["a"] * 10 if p["a"] <= 5 else p["a"], "n @ binds the number that matched the range."),
    RS(T(r'let r: Result<i32, String> = if $a > $b { Ok($a) } else { Err(String::from("$w")) };', r'match r { Ok(v) => println!("{}", v), Err(e) => println!("{}", e) }'), lambda p: p["a"] if p["a"] > p["b"] else p["w"], "Ok prints the number, Err prints the message."),
    RS(T(r"let c = '$x';", r'''let k = match c { 'a' | 'e' | 'i' | 'o' | 'u' => "v", 'a'..='m' => "lo", _ => "hi" };''', r'println!("{}", k);'), lambda p: "v" if p["x"] in "aeiou" else "lo", "The vowel pattern comes first; letters a to h that are not vowels fall in a..=m."),
    RS(r'println!("{}", matches!($n, 10..=25));', lambda p: 10 <= p["n"] <= 25, "matches! is true when the value fits the pattern."),
    RS(r'println!("{}", matches!(Some($a), Some(x) if x > $b));', lambda p: p["a"] > p["b"], "The pattern matches and the guard compares a with b."),
    RS(r'println!("{}", Some($a) > None);', "true", "None is smaller than any Some."),
    RS(r'println!("{}", Some($a) < Some($b));', lambda p: p["a"] < p["b"], "Two Some values compare by their contents."),
    RS(r'println!("{:?}", ${a}i32.cmp(&$b));', lambda p: "Less" if p["a"] < p["b"] else "Greater", "cmp gives an Ordering."),
    RS(r'println!("{:?}", ${a}i32.partial_cmp(&$b));', lambda p: "Some(Less)" if p["a"] < p["b"] else "Some(Greater)", "partial_cmp wraps the Ordering in Some."),
    RS(r'println!("{:?}", [$a, $b, $c, $d].iter().find(|&&x| x > 6));', lambda p: next((some(x) for x in [p["a"], p["b"], p["c"], p["d"]] if x > 6), "None"), "find gives the first item above 6, or None."),
    RS(r'println!("{:?}", [$a, $b, $c].get($k));', lambda p: some([p["a"], p["b"], p["c"]][p["k"]]) if p["k"] < 3 else "None", "get is None when the index is past the end."),
    RS(r'println!("{:?}", "$u".parse::<i8>().unwrap_or(-1));', -1, "An i8 holds at most 127, so the parse fails and -1 is used."),
    RS(r'println!("{:?}", "$u".parse::<u8>().unwrap_or(0));', lambda p: p["u"], "A u8 holds up to 255, so the parse works."),
    RS(r'println!("{}", "-$a".parse::<u32>().unwrap_or(7));', 7, "A u32 cannot be negative, so the parse fails and 7 is used."),
    RS(T(r'let v = [Some($a), None, Some($b)];', r'let mut t = 0;', r'for o in v { if let Some(x) = o { t += x; } }', r'println!("{}", t);'), lambda p: p["a"] + p["b"], "The None is skipped by if let."),
    RS(T(r'let mut st = vec![$a, $b, $c];', r'let mut t = 0;', r'while let Some(x) = st.pop() { t = t * 10 + x; }', r'println!("{}", t);'), lambda p: p["c"] * 100 + p["b"] * 10 + p["a"], "pop takes items from the end, so the digits come out reversed."),
    RS(r'println!("{:?}", Some($a).or(Some($b)));', lambda p: some(p["a"]), "or keeps the first Some."),
    RS(r'println!("{:?}", None.or(Some($b)));', lambda p: some(p["b"]), "or falls back to the second option when the first is None."),
    RS(r'println!("{:?}", Some($a).xor(Some($b)));', "None", "xor needs exactly one Some."),
    RS(r'println!("{:?}", Some($a).zip(Some($b)));', lambda p: f"Some(({p['a']}, {p['b']}))", "zip pairs the two values inside Some."),
    RS(T(r'let mut o = Some($a);', r'let old = o.replace($b);', r'println!("{:?} {:?}", o, old);'), lambda p: f"Some({p['b']}) Some({p['a']})", "replace stores the new value and returns the old option."),
    RS(r'println!("{}", None::<i32>.unwrap_or_else(|| $a * $b));', lambda p: p["a"] * p["b"], "The closure runs only because the option is None."),
    RS(r'println!("{:?}", "$n".parse::<i32>().ok());', lambda p: some(p["n"]), "ok turns Ok(n) into Some(n)."),
    RS(r'println!("{}", "$w".parse::<i32>().is_ok());', "false", "A word is not a number."),
    RS(r'println!("{:?}", vec![$a, $b, $c].iter().max());', lambda p: some(max(p["a"], p["b"], p["c"])), "max gives an Option of the largest item."),
    RS(r'println!("{:?}", Vec::<i32>::new().iter().max());', "None", "An empty iterator has no maximum."),
]


# ── 2. Iterator Chains ──────────────────────────────────────────────────

def _chars_eq(a: str, b: str) -> int:
    return sum(1 for x, y in zip(a, b) if x == y)


ITER: list[Maker] = [
    RS(r'println!("{}", (1..=$n).sum::<i32>());', lambda p: sum(range(1, p["n"] + 1)), "The range is inclusive: 1 up to n are added."),
    RS(r'println!("{}", (1..$n).filter(|x| x % $a == 0).count());', lambda p: sum(1 for x in range(1, p["n"]) if x % p["a"] == 0), "1..n stops before n; the multiples of a are counted."),
    RS(r'println!("{}", (1..=$a).product::<i32>());', lambda p: __import__("math").prod(range(1, p["a"] + 1)), "product multiplies 1 * 2 * ... * a."),
    RS(r'println!("{}", (1..=$a).map(|x| x * x).sum::<i32>());', lambda p: sum(x * x for x in range(1, p["a"] + 1)), "The squares are added."),
    RS(r'println!("{}", (0..$n).step_by($a).count());', lambda p: len(range(0, p["n"], p["a"])), "step_by yields 0, a, 2a, ... below n."),
    RS(r'println!("{:?}", (1..=$n).rev().take($a).collect::<Vec<_>>());', lambda p: lst(list(range(p["n"], 0, -1))[:p["a"]]), "rev counts down from n; take keeps the first a items."),
    RS(r'println!("{}", (1..=$a).fold(0, |acc, x| acc * 10 + x));', lambda p: int("".join(str(i) for i in range(1, p["a"] + 1))), "fold builds the digits 1, 12, 123, ..."),
    RS(r'println!("{:?}", [$a, $b, $c, $d].iter().max());', lambda p: some(max(p["a"], p["b"], p["c"], p["d"])), "max returns Some of the largest."),
    RS(r'println!("{}", [$a, $b, $c, $d].iter().min().unwrap());', lambda p: min(p["a"], p["b"], p["c"], p["d"]), "min gives the smallest item."),
    RS(T(r'let v = [$a, $b, $c, $d];', r'println!("{}", v.iter().enumerate().filter(|(i, _)| i % 2 == 0).map(|(_, x)| x).sum::<i32>());'), lambda p: p["a"] + p["c"], "The items at positions 0 and 2 are added."),
    RS(T(r'let a = [$a, $b, $c];', r'let b = [$d, 1, 2];', r'println!("{}", a.iter().zip(b.iter()).map(|(x, y)| x * y).sum::<i32>());'), lambda p: p["a"] * p["d"] + p["b"] + 2 * p["c"], "zip pairs the items up and the products are added."),
    RS(r'println!("{:?}", [$a, $b, $c, $d].iter().position(|&x| x > 5));', lambda p: next((some(i) for i, x in enumerate([p["a"], p["b"], p["c"], p["d"]]) if x > 5), "None"), "position is the index of the first item above 5."),
    RS(r'println!("{} {}", [$a, $b, $c].iter().any(|&x| x > 5), [$a, $b, $c].iter().all(|&x| x > 2));', lambda p: f"{'true' if any(x > 5 for x in (p['a'], p['b'], p['c'])) else 'false'} {'true' if all(x > 2 for x in (p['a'], p['b'], p['c'])) else 'false'}", "any is true if one item passes; all needs every item to pass."),
    RS(r'println!("{:?}", (1..=$a).chain(20..22).collect::<Vec<_>>());', lambda p: lst(list(range(1, p["a"] + 1)) + [20, 21]), "chain walks the first range and then the second."),
    RS(r'println!("{:?}", [$a, $b, $c, $d].windows(2).map(|w| w[1] - w[0]).collect::<Vec<_>>());', lambda p: lst([y - x for x, y in zip([p["a"], p["b"], p["c"], p["d"]], [p["b"], p["c"], p["d"]])]), "Each window of two gives the difference of neighbours."),
    RS(r'println!("{}", (1..=$n).collect::<Vec<_>>().windows($a).count());', lambda p: p["n"] - p["a"] + 1, "A list of n items has n - a + 1 windows of size a."),
    RS(r'println!("{}", (1..=$n).collect::<Vec<_>>().chunks($a).count());', lambda p: -(-p["n"] // p["a"]), "The last chunk may be shorter, so the count rounds up."),
    RS(r'println!("{:?}", vec![$a, $b, $c, $d, 1].chunks(2).map(|c| c.iter().sum::<i32>()).collect::<Vec<_>>());', lambda p: lst([p["a"] + p["b"], p["c"] + p["d"], 1]), "The last chunk has one item."),
    RS(T(r'let mut c = 0;', r'let _it = (1..$n).map(|x| { c += 1; x * 2 });', r'println!("{}", c);'), 0, "Iterators are lazy: nothing consumed it, so the closure never ran."),
    RS(T(r'let mut c = 0;', r'let v: Vec<i32> = (1..$n).map(|x| { c += 1; x }).take($a).collect();', r'println!("{} {}", c, v.len());'), lambda p: f"{p['a']} {p['a']}", "take stops pulling after a items, so map ran a times."),
    RS(T(r'let mut c = 0;', r'let _ = (1..$n).find(|x| { c += 1; *x == $a });', r'println!("{}", c);'), lambda p: p["a"], "find stops at the first match, the a-th item."),
    RS(T(r'let mut c = 0;', r'let _ = (1..$n).any(|x| { c += 1; x > $a });', r'println!("{}", c);'), lambda p: p["a"] + 1, "any stops at the first item above a, the (a+1)-th."),
    RS(T(r'let mut c = 0;', r'let _ = (1..$n).all(|x| { c += 1; x < $a });', r'println!("{}", c);'), lambda p: p["a"], "all stops at the first failing item, which is a."),
    RS(T(r'let mut c = 0;', r'let v: Vec<i32> = (1..$n).filter(|x| { c += 1; x % 2 == 0 }).take($k).collect();', r'println!("{} {}", c, v.len());'), lambda p: f"{2 * p['k']} {p['k']}", "To find k even numbers the filter looks at 2k items."),
    RS(r'println!("{}", "$w".chars().rev().collect::<String>());', lambda p: p["w"][::-1], "rev reads the characters from the end."),
    RS(r'println!("{}", "$w".chars().filter(|c| "aeiou".contains(*c)).count());', lambda p: sum(1 for c in p["w"] if c in "aeiou"), "The vowels are counted."),
    RS(r'println!("{}", "$w".chars().map(|c| c.to_ascii_uppercase()).collect::<String>());', lambda p: p["w"].upper(), "Each char is capitalised and collected into a String."),
    RS(r'println!("{:?}", (1..=$n).filter(|x| x % 2 == 1).map(|x| x * x).take($a).last());', lambda p: some([x * x for x in range(1, p["n"] + 1) if x % 2 == 1][:p["a"]][-1]), "Odd squares, the first a of them, and the last of those."),
    RS(r'println!("{:?}", ["$w", "$z"].iter().max_by_key(|s| s.len()));', lambda p: 'Some("' + (p["z"] if len(p["z"]) >= len(p["w"]) else p["w"]) + '")', "max_by_key returns the last of equally long items."),
    RS(r'println!("{:?}", ["$w", "$z"].iter().min_by_key(|s| s.len()));', lambda p: 'Some("' + (p["w"] if len(p["w"]) <= len(p["z"]) else p["z"]) + '")', "min_by_key returns the first of equally short items."),
    RS(r'println!("{}", (1..=$n).take_while(|x| x * x < $m).count());', lambda p: len([x for x in range(1, p["n"] + 1) if x * x < p["m"]]), "take_while stops at the first square that is not below m."),
    RS(r'println!("{:?}", (1..=$n).skip_while(|&x| x < $a).take(2).collect::<Vec<_>>());', lambda p: lst([p["a"], p["a"] + 1]), "skip_while drops the items below a, take keeps two."),
    RS(r'println!("{}", (1..=$a).flat_map(|x| vec![x; x as usize]).count());', lambda p: p["a"] * (p["a"] + 1) // 2, "Each x is repeated x times: 1 + 2 + ... + a items."),
    RS(r'println!("{}", (1..=$a).flat_map(|x| 0..x).sum::<i32>());', lambda p: sum(sum(range(x)) for x in range(1, p["a"] + 1)), "For every x the numbers 0 to x - 1 are added."),
    RS(r'println!("{:?}", (1..=$n).filter(|x| x % $a == 0).last());', lambda p: some(p["n"] // p["a"] * p["a"]), "The last multiple of a that is not above n."),
    RS(T(r'let (e, o): (Vec<i32>, Vec<i32>) = (1..=$a).partition(|x| x % 2 == 0);', r'println!("{:?} {:?}", e, o);'), lambda p: lst([x for x in range(1, p["a"] + 1) if x % 2 == 0]) + " " + lst([x for x in range(1, p["a"] + 1) if x % 2]), "partition splits the items into those that pass and those that do not."),
    RS(r'println!("{}", [1, 2, 3].iter().cycle().take($n).sum::<i32>());', lambda p: sum([1, 2, 3][i % 3] for i in range(p["n"])), "cycle repeats 1, 2, 3 for n items."),
    RS(r'println!("{:?}", (0..$n).step_by($a).nth($b));', lambda p: some(p["a"] * p["b"]) if p["a"] * p["b"] < p["n"] else "None", "nth(b) of 0, a, 2a, ... is b times a, if it is below n."),
    RS(r'''println!("{}", "$w".chars().filter(|&c| c == '$f').count());''', lambda p: p["w"].count(p["f"]), "The matching letters are counted."),
    RS(r'println!("{:?}", [$a, $b, $c, $d].iter().rev().skip($k).next());', lambda p: some([p["d"], p["c"], p["b"], p["a"]][p["k"]]), "Reversed, skipping k items, the next one is d, c, b or a."),
    RS(r"""println!("{:?}", "$w $z".split(' ').map(|s| s.len()).collect::<Vec<_>>());""", lambda p: lst([len(p["w"]), len(p["z"])]), "Each word is turned into its length."),
    RS(r'println!("{:?}", (1..=$a).map(|x| x * x).rev().collect::<Vec<_>>());', lambda p: lst([x * x for x in range(p["a"], 0, -1)]), "The squares in reverse order."),
    RS(r'println!("{}", (1..=$a).fold(String::new(), |s, x| s + &x.to_string()));', lambda p: "".join(str(i) for i in range(1, p["a"] + 1)), "fold appends each number's text."),
    RS(r'println!("{:?}", [${a}i32, $b, $c].iter().min_by_key(|&&x| (x - 5).abs()));', lambda p: some(min([p["a"], p["b"], p["c"]], key=lambda x: abs(x - 5))), "The item closest to 5; the first one wins a tie."),
    RS(T(r'let v = [$a, $b, $c, $d];', r'println!("{}", v.iter().sum::<i32>() / v.len() as i32);'), lambda p: (p["a"] + p["b"] + p["c"] + p["d"]) // 4, "The integer mean cuts the fraction."),
    RS(r'println!("{}", (1..=$n).map(|x| x % $a).sum::<i32>());', lambda p: sum(x % p["a"] for x in range(1, p["n"] + 1)), "The remainders of 1..=n are added."),
    RS(r'println!("{}", (1..$n).zip("$w".chars()).count());', lambda p: p["L"], "zip stops at the shorter side, the word."),
    RS(r'println!("{}", "$w".chars().zip("$z".chars()).filter(|(a, b)| a == b).count());', lambda p: _chars_eq(p["w"], p["z"]), "Letters in the same position are compared."),
    RS(r'println!("{:?}", (1..=$a).map(|i| (1..=i).sum::<i32>()).collect::<Vec<_>>());', lambda p: lst([i * (i + 1) // 2 for i in range(1, p["a"] + 1)]), "Triangular numbers: the sum 1 to i for each i."),
    RS(r'''println!("{:?}", "$w".chars().last());''', lambda p: "Some('" + p["w"][-1] + "')", "last gives the final character in an Option."),
    RS(r'println!("{:?}", [$a, $b, $c, $d].iter().rev().position(|&x| x == $b));', "Some(2)", "From the back: d, c, b, so b is at position 2."),
    RS(r'println!("{}", (1..).take_while(|x| x * x < $m).count());', lambda p: isqrt(p["m"] - 1), "The count of x with x squared below m."),
    RS(r'println!("{:?}", (1..=$n).rev().step_by($a).nth(1));', lambda p: some(p["n"] - p["a"]), "n, then n - a: the second item."),
    RS(r'println!("{:?}", (1..=$n).skip($a).step_by(2).take(3).collect::<Vec<_>>());', lambda p: lst([p["a"] + 1, p["a"] + 3, p["a"] + 5]), "Skip a items, then every second one, three of them."),
]


# ── 3. Vec & Maps ───────────────────────────────────────────────────────

def _bsearch(v, x):
    lo, hi = 0, len(v)
    while lo < hi:
        mid = (lo + hi) // 2
        if v[mid] == x:
            return f"Ok({mid})"
        if v[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return f"Err({lo})"


def _dedup(v):
    out = []
    for x in v:
        if not out or out[-1] != x:
            out.append(x)
    return out


def _bmap(d: dict) -> str:
    return "{" + ", ".join(f"{k}: {v}" for k, v in sorted(d.items(), key=lambda kv: kv[0])) + "}"


def _bmap_s(d: dict) -> str:
    return "{" + ", ".join(f'"{k}": {v}' for k, v in sorted(d.items())) + "}"


COLLECT: list[Maker] = [
    RS(T(r'let mut v = vec![$a, $b, $c];', r'v.push($d);', r'println!("{:?}", v);'), lambda p: lst([p["a"], p["b"], p["c"], p["d"]]), "push appends at the end."),
    RS(T(r'let mut v = vec![$a, $b, $c];', r'let x = v.pop();', r'println!("{:?} {:?}", x, v);'), lambda p: f"Some({p['c']}) {lst([p['a'], p['b']])}", "pop returns the last item in an Option."),
    RS(T(r'let mut v = vec![$a, $b, $c];', r'v.insert(1, $d);', r'println!("{:?}", v);'), lambda p: lst([p["a"], p["d"], p["b"], p["c"]]), "insert shifts the later items right."),
    RS(T(r'let mut v = vec![$a, $b, $c];', r'let x = v.remove(1);', r'println!("{} {:?}", x, v);'), lambda p: f"{p['b']} {lst([p['a'], p['c']])}", "remove takes out the item at the index and shifts the rest left."),
    RS(T(r'let mut v = vec![$a, $b, $c];', r'v.swap(0, 2);', r'println!("{:?}", v);'), lambda p: lst([p["c"], p["b"], p["a"]]), "swap exchanges the first and the last."),
    RS(T(r'let mut v = vec![$a, $b, $c, $d];', r'v.retain(|&x| x % 2 == 0);', r'println!("{:?}", v);'), lambda p: lst([x for x in (p["a"], p["b"], p["c"], p["d"]) if x % 2 == 0]), "retain keeps only the items that pass the test."),
    RS(T(r'let mut v = vec![$a, $a, $b, $b, $a];', r'v.dedup();', r'println!("{:?}", v);'), lambda p: lst(_dedup([p["a"], p["a"], p["b"], p["b"], p["a"]])), "dedup removes only repeats that sit next to each other."),
    RS(T(r'let mut v = vec![$d, $b, $a, $c];', r'v.sort();', r'println!("{:?}", v);'), lambda p: lst(sorted([p["d"], p["b"], p["a"], p["c"]])), "sort puts the numbers in ascending order."),
    RS(T(r'let mut v = vec![$d, $b, $a, $c];', r'v.sort_by(|x, y| y.cmp(x));', r'println!("{:?}", v);'), lambda p: lst(sorted([p["d"], p["b"], p["a"], p["c"]], reverse=True)), "Comparing y with x reverses the order."),
    RS(T(r'let mut v = vec![$a, $b, $c];', r'v.reverse();', r'println!("{:?}", v);'), lambda p: lst([p["c"], p["b"], p["a"]]), "reverse flips the order in place."),
    RS(r'println!("{}", vec![$a, $b, $c].contains(&$b));', "true", "contains looks for the value."),
    RS(r'println!("{}", vec![$a, $b, $c].contains(&$n));', "false", "n is at least 10, and the items are single digits."),
    RS(r'println!("{:?}", [1, 3, 5, 7, 9, 11].binary_search(&$a));', lambda p: _bsearch([1, 3, 5, 7, 9, 11], p["a"]), "Ok gives the index when found, Err the place where it would go."),
    RS(T(r'let mut v = vec![$a];', r'v.extend([$c, $d]);', r'println!("{:?}", v);'), lambda p: lst([p["a"], p["c"], p["d"]]), "extend appends all the items."),
    RS(T(r'let mut v = vec![$a, $b, $c, $d];', r'v.truncate($k);', r'println!("{:?}", v);'), lambda p: lst([p["a"], p["b"], p["c"], p["d"]][:p["k"]]), "truncate keeps only the first k items."),
    RS(T(r'let mut v = vec![$a, $b, $c, $d, $n];', r'let d: Vec<i32> = v.drain(1..3).collect();', r'println!("{:?} {:?}", d, v);'), lambda p: f"{lst([p['b'], p['c']])} {lst([p['a'], p['d'], p['n']])}", "drain removes items 1 and 2 and hands them out."),
    RS(r'println!("{:?}", vec![$a; $k + 1]);', lambda p: lst([p["a"]] * (p["k"] + 1)), "vec![x; n] repeats x n times."),
    RS(T(r'let v = vec![$a, $b, $c, $d];', r'println!("{:?}", &v[1..3]);'), lambda p: lst([p["b"], p["c"]]), "A range 1..3 holds the items at 1 and 2."),
    RS(T(r'let v = vec![$a, $b, $c, $d];', r'println!("{:?} {:?}", &v[2..], &v[..=1]);'), lambda p: f"{lst([p['c'], p['d']])} {lst([p['a'], p['b']])}", "2.. runs to the end; ..=1 includes index 1."),
    RS(T(r'let mut v = vec![0; $a];', r'v.push(1);', r'v.pop();', r'v.pop();', r'println!("{}", v.len());'), lambda p: p["a"] - 1, "One push and two pops leave a - 1 items."),
    RS(T(r'let mut m = std::collections::BTreeMap::new();', r'for k in ["$w", "$z", "$w"] { *m.entry(k).or_insert(0) += 1; }', r'println!("{:?}", m);'), lambda p: _bmap_s({p["w"]: 2, p["z"]: 1}), "entry counts each key; a BTreeMap prints sorted by key."),
    RS(T(r'let mut m = std::collections::BTreeMap::new();', r'for x in [$a, $b, $a, $c, $a] { *m.entry(x).or_insert(0) += 1; }', r'println!("{:?}", m);'), lambda p: _bmap({p["a"]: 3, p["b"]: 1, p["c"]: 1}), "Keys print in ascending order with their counts."),
    RS(T(r'let mut m = std::collections::BTreeMap::new();', r'''for c in "$x$y$x".chars() { *m.entry(c).or_insert(0) += 1; }''', r'println!("{:?}", m);'), lambda p: "{" + ", ".join(f"'{k}': {v}" for k, v in sorted({p["x"]: 2, p["y"]: 1}.items())) + "}", "chars are counted and printed in single quotes, sorted."),
    RS(T(r'let mut m = std::collections::BTreeMap::new();', r'm.insert("$w", $a);', r'm.insert("$z", $b);', r'm.insert("$w", $c);', r'println!("{} {:?}", m.len(), m.get("$w"));'), lambda p: f"2 Some({p['c']})", "The second insert for the same key replaced the value."),
    RS(T(r'use std::collections::HashMap;', r'let mut m = HashMap::new();', r'm.insert("$w", $a);', r'm.insert("$z", $b);', r'm.insert("$w", $c);', r'println!("{} {:?}", m.len(), m.get("$w"));'), lambda p: f"2 Some({p['c']})", "Inserting an existing key replaces its value and keeps the length."),
    RS(T(r'use std::collections::HashMap;', r'let mut m = HashMap::new();', r'm.insert($a, "$w");', r'println!("{} {}", m.contains_key(&$a), m.contains_key(&$b));'), "true false", "contains_key tells whether the key was inserted."),
    RS(T(r'use std::collections::HashMap;', r'let mut m: HashMap<&str, i32> = HashMap::new();', r'm.insert("$w", $a);', r'println!("{:?} {:?}", m.get("$w"), m.get("$z"));'), lambda p: f"Some({p['a']}) None", "get gives Some for a stored key and None for a missing one."),
    RS(T(r'use std::collections::BTreeSet;', r'let s: BTreeSet<i32> = [$a, $b, $a, $c].into_iter().collect();', r'println!("{:?}", s);'), lambda p: "{" + ", ".join(str(x) for x in sorted({p["a"], p["b"], p["c"]})) + "}", "A set drops duplicates and a BTreeSet prints sorted."),
    RS(T(r'use std::collections::BTreeSet;', r'let s: BTreeSet<i32> = [$a, $b, $a, $c].into_iter().collect();', r'println!("{} {:?}", s.len(), s.first());'), lambda p: f"3 Some({min(p['a'], p['b'], p['c'])})", "Three different values; first is the smallest."),
    RS(T(r'use std::collections::VecDeque;', r'let mut d = VecDeque::new();', r'd.push_back($a);', r'd.push_front($b);', r'd.push_back($c);', r'let x = d.pop_back();', r'println!("{:?} {:?}", x, d);'), lambda p: f"Some({p['c']}) {lst([p['b'], p['a']])}", "push_front puts b before a; pop_back removes c."),
    RS(T(r'use std::collections::VecDeque;', r'let mut d: VecDeque<i32> = (1..=$a).collect();', r'd.rotate_left($k % $a);', r'println!("{:?}", d.front());'), lambda p: some(p["k"] % p["a"] + 1), "After rotating left by k, the item that was at index k is first."),
    RS(T(r'let mut g = vec![vec![0; 3]; 2];', r'g[1][2] = $a;', r'println!("{:?}", g);'), lambda p: f"[[0, 0, 0], [0, 0, {p['a']}]]", "g[1][2] is the last cell of the second row."),
    RS(T(r'let v = vec![$a, $b, $c, $d];', r'let (l, r) = v.split_at($k);', r'println!("{:?} {:?}", l, r);'), lambda p: f"{lst([p['a'], p['b'], p['c'], p['d']][:p['k']])} {lst([p['a'], p['b'], p['c'], p['d']][p['k']:])}", "split_at cuts before index k."),
    RS(T(r'let mut v = vec!["$w", "$z"];', r'v.sort();', r'println!("{:?}", v);'), lambda p: "[" + ", ".join('"' + x + '"' for x in sorted([p["w"], p["z"]])) + "]", "Strings sort alphabetically."),
    RS(r'println!("{}", vec!["$w", "$z"].join("-"));', lambda p: p["w"] + "-" + p["z"], "join puts the separator between the items."),
    RS(r'println!("{:?}", [[$a, $b], [$c, $d]].concat());', lambda p: lst([p["a"], p["b"], p["c"], p["d"]]), "concat joins the inner arrays into one vector."),
    RS(T(r'let mut v = vec![$a, $b, $c, $d];', r'v.rotate_left($k);', r'println!("{:?}", v);'), lambda p: lst(([p["a"], p["b"], p["c"], p["d"]] * 2)[p["k"]:p["k"] + 4]), "rotate_left moves the first k items to the back."),
    RS(T(r'let mut v = vec![$a, $b, $c];', r'*v.last_mut().unwrap() += $n;', r'println!("{:?}", v);'), lambda p: lst([p["a"], p["b"], p["c"] + p["n"]]), "last_mut gives a mutable reference to the final item."),
    RS(T(r'let mut v = vec![$a, $b, $c, $d];', r'let x = v.swap_remove(0);', r'println!("{} {:?}", x, v);'), lambda p: f"{p['a']} {lst([p['d'], p['b'], p['c']])}", "swap_remove puts the last item in the removed spot."),
    RS(T(r'let mut v = vec![$a];', r'v.resize($k + 2, $b);', r'println!("{:?}", v);'), lambda p: lst([p["a"]] + [p["b"]] * (p["k"] + 1)), "resize pads with copies of b up to the new length."),
    RS(T(r'let mut v = vec![$a, $b, $c, $d];', r'let t = v.split_off(2);', r'println!("{:?} {:?}", v, t);'), lambda p: f"{lst([p['a'], p['b']])} {lst([p['c'], p['d']])}", "split_off cuts the vector in two at index 2."),
    RS(T(r'use std::collections::BTreeMap;', r'let mut m = BTreeMap::new();', r'm.insert($a, 1);', r'm.insert($b, 2);', r'm.insert($c, 3);', r'println!("{}", m.iter().map(|(k, v)| k * v).sum::<i32>());'), lambda p: p["a"] + 2 * p["b"] + 3 * p["c"], "Each key is multiplied by its value and the products are added."),
    RS(T(r'use std::collections::BTreeMap;', r'let mut m = BTreeMap::new();', r"m.insert($a, 'x');", r"m.insert($b, 'y');", r'println!("{:?}", m.first_key_value());'), lambda p: f"Some(({min(p['a'], p['b'])}, '{'x' if p['a'] < p['b'] else 'y'}'))", "first_key_value gives the pair with the smallest key."),
    RS(T(r'use std::collections::BTreeMap;', r'let mut m = BTreeMap::new();', r'm.insert("$w", $a);', r'let old = m.insert("$w", $b);', r'println!("{:?} {}", old, m.len());'), lambda p: f"Some({p['a']}) 1", "insert returns the old value when the key already existed."),
    RS(T(r'use std::collections::BTreeMap;', r'let mut m = BTreeMap::new();', r'm.insert($a, "$w");', r'm.insert($b, "$z");', r'let x = m.remove(&$a);', r'println!("{:?} {}", x, m.len());'), lambda p: f'Some("{p["w"]}") 1', "remove returns the value that was stored and shrinks the map."),
    RS(T(r'use std::collections::BTreeMap;', r'let mut m: BTreeMap<&str, Vec<i32>> = BTreeMap::new();', r'm.entry("$w").or_default().push($a);', r'm.entry("$w").or_default().push($b);', r'println!("{:?}", m);'), lambda p: '{"' + p["w"] + '": ' + lst([p["a"], p["b"]]) + "}", "or_default creates the empty vector on the first use, then both pushes go in it."),
]
