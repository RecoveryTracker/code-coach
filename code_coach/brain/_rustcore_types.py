"""Rust core pack, part 4: Structs, Enums & Traits (complete programs with `fn main`).

Every answer is worked out by hand in Python; tests/rust_oracle.py builds every template with the real rustc (debug and
-O). The programs are kept compact (one-line functions) so that they fit the 220-character, 10-line limit.
"""

from __future__ import annotations

import random

from ._model import Maker
from ._rs_model import RS
from ._rustcore_basics import T
from .items import Item


def lst(xs) -> str:
    return "[" + ", ".join(str(x) for x in xs) + "]"


def Var(build) -> Maker:
    """A template whose text depends on a random choice: `build(rng)` returns (fmt, answer, why) for RS."""
    def make(rng: random.Random) -> Item:
        fmt, ans, why = build(rng)
        return RS(fmt, ans, why)(rng)
    make.__name__ = "var_" + getattr(build, "__name__", "t")
    return make


def _tuple_lt(a, b):
    return a < b


def _lex_cmp(rng: random.Random):
    ops = [("<", lambda x, y: x < y), (">", lambda x, y: x > y), ("<=", lambda x, y: x <= y), (">=", lambda x, y: x >= y)]
    return rng.choice(ops)


def _cmp_struct(rng):
    a, b, c, d = rng.sample(range(1, 10), 4)
    if rng.random() < 0.5:
        c = a
    op, f = _lex_cmp(rng)
    return (T("#[derive(PartialEq, PartialOrd)] struct V(i32, i32);", "fn main() { println!(\"{}\", V(%d, %d) %s V(%d, %d)); }" % (a, b, op, c, d)),
            "true" if f((a, b), (c, d)) else "false",
            "Derived ordering compares the first field, then the second only when the first is equal.")


def _cmp_named(rng):
    a, b, c, d = rng.sample(range(1, 10), 4)
    if rng.random() < 0.5:
        c = a
    return (T("#[derive(PartialEq, PartialOrd)] struct P { age: i32, id: i32 }",
              "fn main() { println!(\"{}\", P { id: %d, age: %d } < P { id: %d, age: %d }); }" % (a, b, c, d)),
            "true" if (b, a) < (d, c) else "false",
            "Fields compare in declaration order (age first), not the order they are written in the literal.")


def _enum_order(rng):
    names = ["Low", "Mid", "High"]
    i, j = rng.sample(range(3), 2)
    op, f = _lex_cmp(rng)
    return (T("#[derive(PartialEq, PartialOrd)] enum L { Low, Mid, High }",
              "fn main() { println!(\"{}\", L::%s %s L::%s); }" % (names[i], op, names[j])),
            "true" if f(i, j) else "false",
            "Enum variants compare in the order they are declared.")


def _enum_data_order(rng):
    a, b = rng.sample(range(1, 10), 2)
    if rng.random() < 0.5:
        return (T("#[derive(PartialEq, PartialOrd)] enum E { A(i32), B(i32) }", "fn main() { println!(\"{}\", E::A(%d) < E::B(%d)); }" % (a, b)),
                "true", "A is declared before B, so any A is smaller than any B.")
    return (T("#[derive(PartialEq, PartialOrd)] enum E { A(i32), B(i32) }", "fn main() { println!(\"{}\", E::A(%d) < E::A(%d)); }" % (a, b)),
            "true" if a < b else "false", "The same variant compares by its data.")


def _flips(rng):
    k = rng.randint(1, 5)
    chain = "D::N" + ".f()" * k
    return (T("enum D { N, S }", "impl D { fn f(&self) -> D { match self { D::N => D::S, D::S => D::N } } }",
              "fn main() { println!(\"{}\", matches!(%s, D::S)); }" % chain),
            "true" if k % 2 else "false", "Every flip swaps the direction, so the end is S when k is odd.")


def _debug_variants(rng):
    a, b = rng.sample(range(1, 10), 2)
    c = rng.choice(["Red", "Green", "Blue"])
    kinds = [
        (T("#[derive(Debug)] struct P { x: i32, y: i32 }", "fn main() { println!(\"{:?}\", P { x: %d, y: %d }); }" % (a, b)), f"P {{ x: {a}, y: {b} }}", "Debug of a struct names its fields."),
        (T("#[derive(Debug)] struct P(i32, i32);", "fn main() { println!(\"{:?}\", P(%d, %d)); }" % (a, b)), f"P({a}, {b})", "Debug of a tuple struct shows it like a call."),
        (T("#[derive(Debug)] enum C { Red, Green, Blue }", "fn main() { println!(\"{:?}\", C::%s); }" % c), c, "Debug of a unit variant is its name."),
        (T("#[derive(Debug)] enum S { Circle(i32), Rect(i32, i32) }", "fn main() { println!(\"{:?}\", S::Rect(%d, %d)); }" % (a, b)), f"Rect({a}, {b})", "Debug of a variant with data shows the name and the data."),
        (T("#[derive(Debug)] struct W { v: Option<i32> }", "fn main() { println!(\"{:?}\", W { v: Some(%d) }); }" % a), f"W {{ v: Some({a}) }}", "The field is itself printed with its Debug."),
        (T("#[derive(Debug)] struct S { v: Vec<i32>, ok: bool }", "fn main() { println!(\"{:?}\", S { v: vec![%d, %d], ok: true }); }" % (a, b)), f"S {{ v: [{a}, {b}], ok: true }}", "Vectors and bools print the way they do alone."),
        (T("#[derive(Debug)] struct U;", "fn main() { println!(\"{:?} {:?}\", U, Some(%d)); }" % a), f"U Some({a})", "A unit struct prints just its name."),
        (T("#[derive(Debug)] struct P { name: String }", "fn main() { println!(\"{:?}\", P { name: String::from(\"%s\") }); }" % rng.choice(["farm", "drone", "lamp"])), None, "Strings inside Debug are quoted."),
    ]
    fmt, ans, why = rng.choice(kinds[:7])
    return fmt, ans, why


def _debug_name(rng):
    w = rng.choice(["farm", "drone", "lamp", "seed", "barn", "robot"])
    return (T("#[derive(Debug)] struct P { name: String }", "fn main() { println!(\"{:?}\", P { name: String::from(\"%s\") }); }" % w),
            'P { name: "%s" }' % w, "The String field is printed in quotes.")


STRUCT: list[Maker] = [
    RS(T(r'struct P { x: i32, y: i32 }', r'impl P { fn new(x: i32, y: i32) -> P { P { x, y } } fn sum(&self) -> i32 { self.x + self.y } }', r'fn main() { println!("{}", P::new($a, $b).sum()); }'), lambda p: p["a"] + p["b"], "new builds the struct and sum adds the two fields."),
    RS(T(r'struct C { n: i32 }', r'impl C { fn inc(&mut self) { self.n += $a; } }', r'fn main() { let mut c = C { n: $b }; c.inc(); c.inc(); println!("{}", c.n); }'), lambda p: p["b"] + 2 * p["a"], "Each call to inc changes the field through &mut self."),
    RS(T(r'trait A { fn name(&self) -> String; fn hi(&self) -> String { format!("hi {}", self.name()) } }', r'struct D;', r'impl A for D { fn name(&self) -> String { "$w".to_string() } }', r'fn main() { println!("{}", D.hi()); }'), lambda p: "hi " + p["w"], "hi is the default method; it calls the name the struct provides."),
    RS(T(r'trait S { fn v(&self) -> i32 { $a } }', r'struct X; struct Y;', r'impl S for X {}', r'impl S for Y { fn v(&self) -> i32 { $b } }', r'fn main() { println!("{}", X.v() + Y.v()); }'), lambda p: p["a"] + p["b"], "X uses the default, Y overrides it."),
    RS(T(r'use std::fmt;', r'struct P(i32, i32);', r'impl fmt::Display for P {', r'    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result { write!(f, "<{}|{}>", self.0, self.1) }', r'}', r'fn main() { println!("{}", P($a, $b)); }'), lambda p: f"<{p['a']}|{p['b']}>", "{} calls the Display implementation."),
    RS(T(r'use std::fmt;', r'struct P(i32, i32);', r'impl fmt::Display for P {', r'    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result { write!(f, "<{}|{}>", self.0, self.1) }', r'}', r'fn main() { println!("{}", P($n, $m).to_string().len()); }'), 7, "to_string uses Display: two two-digit numbers plus three marks make 7."),
    Var(_debug_variants),
    Var(_debug_name),
    Var(_cmp_struct),
    Var(_cmp_named),
    Var(_enum_order),
    Var(_enum_data_order),
    Var(_flips),
    RS(T(r'#[derive(Default, Debug)] struct C { n: i32, s: String, b: bool }', r'fn main() { println!("{:?}", C::default()); }'), 'C { n: 0, s: "", b: false }', "Default gives 0, an empty String and false."),
    RS(T(r'#[derive(Default, Debug)] struct C { n: i32, v: Vec<i32> }', r'fn main() { println!("{:?}", C { n: $a, ..Default::default() }); }'), lambda p: f"C {{ n: {p['a']}, v: [] }}", "The remaining field comes from Default."),
    RS(T(r'enum S { C(i32), R(i32, i32) }', r'impl S { fn area(&self) -> i32 { match self { S::C(r) => 3 * r * r, S::R(w, h) => w * h } } }', r'fn main() { println!("{}", S::R($a, $b).area() + S::C($c).area()); }'), lambda p: p["a"] * p["b"] + 3 * p["c"] ** 2, "The match picks the formula for each variant."),
    RS(T(r'fn big<T: PartialOrd>(a: T, b: T) -> T { if a > b { a } else { b } }', r'fn main() { println!("{} {}", big($a, $b), big("$w", "$z")); }'), lambda p: f"{max(p['a'], p['b'])} {max(p['w'], p['z'])}", "The generic function works for numbers and for strings."),
    RS(T(r'fn total(it: impl Iterator<Item = i32>) -> i32 { it.sum() }', r'fn main() { println!("{}", total((1..=$a).map(|x| x * 2))); }'), lambda p: p["a"] * (p["a"] + 1), "The doubled numbers 2, 4, ... are added."),
    RS(T(r'trait A { fn s(&self) -> i32; }', r'struct X;', r'impl A for X { fn s(&self) -> i32 { $a } }', r'impl A for i32 { fn s(&self) -> i32 { *self } }', r'fn main() { let v: [&dyn A; 2] = [&X, &$b]; println!("{}", v[0].s() + v[1].s()); }'), lambda p: p["a"] + p["b"], "Each trait object answers through its own implementation."),
    RS(T(r'struct C;', r'impl C { const K: i32 = $a; fn dbl() -> i32 { Self::K * 2 } }', r'fn main() { println!("{}", C::dbl() + C::K); }'), lambda p: 3 * p["a"], "An associated constant is shared by all methods."),
    RS(T(r'use std::ops::Add;', r'#[derive(Debug)] struct V(i32, i32);', r'impl Add for V { type Output = V; fn add(self, o: V) -> V { V(self.0 + o.0, self.1 + o.1) } }', r'fn main() { println!("{:?}", V($a, $b) + V($c, $d)); }'), lambda p: f"V({p['a'] + p['c']}, {p['b'] + p['d']})", "The + operator calls the add method."),
    RS(T(r'struct C(i32);', r'impl C { fn add(mut self, n: i32) -> C { self.0 += n; self } }', r'fn main() { println!("{}", C($a).add($b).add($c).0); }'), lambda p: p["a"] + p["b"] + p["c"], "Each add takes the value and returns the changed one."),
    RS(T(r'#[derive(Debug)] struct P { x: i32, y: i32 }', r'fn main() {', r'    let a = P { x: $a, y: $b };', r'    let b = P { x: $c, ..a };', r'    println!("{:?}", b);', r'}'), lambda p: f"P {{ x: {p['c']}, y: {p['b']} }}", "..a fills the remaining field from a."),
    RS(T(r'struct C(u32);', r'impl Iterator for C { type Item = u32; fn next(&mut self) -> Option<u32> { if self.0 < $a { self.0 += 1; Some(self.0) } else { None } } }', r'fn main() { println!("{}", C(0).sum::<u32>()); }'), lambda p: p["a"] * (p["a"] + 1) // 2, "The iterator yields 1 up to a and sum adds them."),
    RS(T(r'struct W(i32);', r'impl From<i32> for W { fn from(n: i32) -> W { W(n * $a) } }', r'fn main() { let w: W = $b.into(); println!("{}", w.0); }'), lambda p: p["a"] * p["b"], "into calls the From implementation."),
    RS(T(r'enum L { N, C(i32, Box<L>) }', r'fn sum(l: &L) -> i32 { match l { L::N => 0, L::C(v, t) => v + sum(t) } }', r'fn main() {', r'    let l = L::C($a, Box::new(L::C($b, Box::new(L::N))));', r'    println!("{}", sum(&l));', r'}'), lambda p: p["a"] + p["b"], "The recursive match adds each node and stops at N."),
    RS(T(r'struct C { n: i32 }', r'impl Default for C { fn default() -> C { C { n: $a } } }', r'fn main() { println!("{}", C::default().n + 1); }'), lambda p: p["a"] + 1, "default is the function written in the impl."),
    RS(T(r'#[derive(PartialEq)] struct P { x: i32, y: i32 }', r'fn main() { println!("{}", P { x: $a, y: $b } == P { x: $a, y: $b }); }'), "true", "Derived equality compares every field."),
    RS(T(r'#[derive(PartialEq)] struct P { x: i32, y: i32 }', r'fn main() { println!("{}", P { x: $a, y: $b } == P { x: $a, y: $c }); }'), "false", "One field differs, so the structs differ."),
    RS(T(r'#[derive(PartialEq, Eq, PartialOrd, Ord, Debug)] struct V(i32, i32);', r'fn main() {', r'    let mut v = vec![V($a, $b), V($a, $c), V($c, $a)];', r'    v.sort();', r'    println!("{:?}", v);', r'}'), lambda p: "[" + ", ".join(f"V({x}, {y})" for x, y in sorted([(p["a"], p["b"]), (p["a"], p["c"]), (p["c"], p["a"])])) + "]", "Derived Ord sorts by the first field, then the second."),
    RS(T(r'struct W<T>(T);', r'impl<T: std::fmt::Display> W<T> { fn show(&self) -> String { format!("[{}]", self.0) } }', r'fn main() { println!("{}{}", W($a).show(), W("$w").show()); }'), lambda p: f"[{p['a']}][{p['w']}]", "The same generic method works for any Display type."),
    RS(T(r'struct Acc { total: i32 }', r'impl Acc { fn add(&mut self, n: i32) -> &mut Acc { self.total += n; self } }', r'fn main() {', r'    let mut a = Acc { total: 0 };', r'    a.add($a).add($b).add($c);', r'    println!("{}", a.total);', r'}'), lambda p: p["a"] + p["b"] + p["c"], "Returning &mut Self lets the calls chain."),
    RS(T(r'const K: i32 = $a;', r'static S: &str = "$w";', r'fn main() { println!("{}{}", K * 2, S); }'), lambda p: f"{p['a'] * 2}{p['w']}", "The constant is doubled, then the static text follows."),
    RS(T(r'fn mk(n: i32) -> impl Fn(i32) -> i32 { move |x| x + n }', r'fn main() { println!("{}", mk($a)($b)); }'), lambda p: p["a"] + p["b"], "mk returns a closure that remembers a."),
    RS(T(r'trait A { fn v(&self) -> i32; }', r'impl A for i32 { fn v(&self) -> i32 { *self * 2 } }', r'fn main() { println!("{}", ${a}i32.v() + ${b}i32.v()); }'), lambda p: 2 * (p["a"] + p["b"]), "The trait is implemented for i32, doubling each value."),
    RS(T(r'fn sum<T: Copy + std::ops::Add<Output = T>>(a: T, b: T) -> T { a + b }', r'fn main() { println!("{} {}", sum($a, $b), sum($a.5, $b.5)); }'), lambda p: f"{p['a'] + p['b']} {p['a'] + p['b'] + 1}", "The float sum is a whole number, which Display prints without .0."),
    RS(T(r'struct R { w: i32, h: i32 }', r'impl R { fn area(&self) -> i32 { self.w * self.h } fn grow(&mut self) { self.w += 1; self.h += 1; } }', r'fn main() { let mut r = R { w: $a, h: $b }; r.grow(); println!("{}", r.area()); }'), lambda p: (p["a"] + 1) * (p["b"] + 1), "grow adds one to both sides before area multiplies them."),
    RS(T(r'#[derive(Clone, Copy, Debug)] struct P { x: i32 }', r'fn main() {', r'    let a = P { x: $a };', r'    let mut b = a;', r'    b.x += $b;', r'    println!("{:?} {:?}", a, b);', r'}'), lambda p: f"P {{ x: {p['a']} }} P {{ x: {p['a'] + p['b']} }}", "P is Copy, so b is a separate copy of a."),
    RS(T(r'enum Op { Add(i32), Mul(i32) }', r'fn run(x: i32, ops: &[Op]) -> i32 { ops.iter().fold(x, |a, o| match o { Op::Add(n) => a + n, Op::Mul(n) => a * n }) }', r'fn main() { println!("{}", run($a, &[Op::Add($b), Op::Mul($c)])); }'), lambda p: (p["a"] + p["b"]) * p["c"], "The operations are applied in order: add first, then multiply."),
    RS(T(r'struct S { n: i32 }', r'impl S { fn double(self) -> S { S { n: self.n * 2 } } }', r'fn main() { let s = S { n: $a }; let t = s.double().double(); println!("{}", t.n); }'), lambda p: p["a"] * 4, "Each double consumes the value and returns a new one."),
    RS(T(r'trait A { fn l(&self) -> u32; fn n(&self) -> String { format!("{} legs", self.l()) } }', r'struct B;', r'impl A for B { fn l(&self) -> u32 { $a } }', r'fn main() { println!("{}", B.n()); }'), lambda p: f"{p['a']} legs", "The default method n calls the l that B provides."),
]
