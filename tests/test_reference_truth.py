"""Are the cheat sheets telling the truth?

test_reference.py checks that a sheet is dense, ordered, unrepetitive and
typeable. None of that can tell a real API from an invented one, and a
reference card is worse than no card when it is confidently wrong — the whole
point of it is that you copy the line without checking.

So the claims that could plausibly be made up get executed. Most entries are
fragments and cannot run alone, which is why this works two ways: every
complete SQL statement is run against the app's own database, and the C++
sheet's non-obvious claims are assembled into one program and compiled.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.engine import run_code
from code_coach.reference import sheet_for

STATEMENT_STARTS = ("SELECT", "WITH", "INSERT", "UPDATE", "DELETE", "CREATE")


def sql_statements() -> list[str]:
    out = []
    for section in sheet_for("sql").sections:
        for entry in section.entries:
            code = entry.code.strip()
            if code.endswith(";") and code.upper().startswith(STATEMENT_STARTS):
                out.append(code)
    return out


class SqlTests(unittest.TestCase):
    def test_every_whole_statement_parses(self) -> None:
        """A missing table or column is about the sample data, not about the
        SQL — the card teaches shapes, and not every shape fits the fixture.
        A syntax error is the thing being looked for, and it means the line
        would not run anywhere."""
        for statement in sql_statements():
            _, err, _ = run_code(statement, language="sql")
            with self.subTest(sql=statement.replace("\n", " ")[:50]):
                lowered = err.lower()
                self.assertNotIn("syntax error", lowered, err)
                self.assertNotIn("incomplete", lowered, err)

    def test_there_are_enough_of_them_to_be_worth_checking(self) -> None:
        """Guards against the extractor above quietly matching nothing."""
        self.assertGreaterEqual(len(sql_statements()), 15)


# Every non-obvious claim on the C++ sheet, in one program: the container and
# string methods, the algorithm names, the capture forms, the smart pointers,
# structured bindings, optional, the if-with-initialiser, and the stream
# manipulators. A wrong name fails to compile; a wrong behaviour returns a
# non-zero code naming the check that caught it.
CPP_PROGRAM = r"""
#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <map>
#include <unordered_map>
#include <set>
#include <memory>
#include <algorithm>
#include <numeric>
#include <optional>
#include <stdexcept>

struct Thing { int n = 1; int method() const { return n; } };
enum class Colour { Red, Green };
using Grid = std::vector<std::vector<int>>;

std::optional<int> find_one() { return 7; }

int main() {
    std::vector<int> nums(10, 0);
    std::vector<int> more = {1, 2, 3};
    more.push_back(4);
    more.pop_back();
    if (more.empty() || more.size() != 3) return 1;
    if (more.at(0) != more.front() || more.back() != 3) return 2;
    more.insert(more.begin(), 0);
    more.erase(more.begin() + 2);
    for (auto& x : more) x *= 2;
    Grid grid(3, std::vector<int>(4));
    if (grid[2][3] != 0 || nums.size() != 10) return 3;

    std::string s = "Ada";
    s += "more";
    if (s.substr(0, 3) != "Ada") return 4;
    if (s.find("zz") != std::string::npos) return 5;
    if (std::stoi("42") != 42 || std::to_string(7) != "7") return 6;
    std::reverse(s.begin(), s.end());
    if (s.c_str() == nullptr) return 7;

    std::map<std::string, int> counts;
    counts["a"]++;
    std::unordered_map<std::string, int> hashed;
    hashed["b"] = 1;
    if (counts.count("a") != 1) return 8;
    if (counts.find("a") == counts.end()) return 9;
    for (auto& [key, value] : counts) { (void)key; (void)value; }
    std::set<int> seen;
    if (!seen.insert(4).second) return 10;
    std::pair<int, int> p = {1, 2};
    if (p.first + p.second != 3) return 11;
    counts.erase("a");

    std::vector<int> v = {3, 1, 2};
    std::sort(v.begin(), v.end());
    std::sort(v.begin(), v.end(), std::greater<int>());
    std::reverse(v.begin(), v.end());
    if (*std::max_element(v.begin(), v.end()) != 3) return 12;
    if (std::find(v.begin(), v.end(), 5) != v.end()) return 13;
    if (std::count(v.begin(), v.end(), 2) != 1) return 14;
    if (std::accumulate(v.begin(), v.end(), 0) != 6) return 15;
    if (!std::binary_search(v.begin(), v.end(), 2)) return 16;
    int a = 1, b = 2;
    std::swap(a, b);
    if (std::min(a, b) != 1 || std::max(a, b) != 2) return 17;

    auto twice = [](int n) { return n * 2; };
    int offset = 5;
    auto byref = [&](int n) { return n + offset; };
    auto bycopy = [=](int n) { return n + offset; };
    auto named = [offset](int n) { return n + offset; };
    if (twice(2) != 4 || byref(1) != 6) return 18;
    if (bycopy(1) != 6 || named(1) != 6) return 19;

    auto up = std::make_unique<Thing>();
    auto sp = std::make_shared<Thing>();
    if (up->method() != 1 || sp->method() != 1) return 20;
    if (up.get() == nullptr) return 21;
    auto moved = std::move(up);
    if (up != nullptr) return 22;

    if (auto r = find_one(); r) { if (*r != 7) return 23; } else { return 24; }

    try { throw std::runtime_error("bad input"); }
    catch (const std::exception& e) {
        if (std::string(e.what()) != "bad input") return 25;
    }

    constexpr int MAX = 100;
    Colour c = Colour::Red;
    if (MAX != 100 || c != Colour::Red) return 26;

    std::cout << std::fixed << std::setprecision(2) << 1.5 << "\n";
    std::cout << std::setw(8) << "pad" << "\n";
    std::cout << std::boolalpha << true << "\n";
    return 0;
}
"""


class CppTests(unittest.TestCase):
    def test_the_sheets_claims_compile_and_hold(self) -> None:
        out, err, code = run_code(CPP_PROGRAM, language="cpp")
        if code != 0 and "isn't on your PATH" in err:
            self.skipTest("needs g++, clang++, or an MSVC install")
        self.assertEqual(code, 0, err or out)
        # The manipulators are on the card with specific claims about what
        # they do, so check the output rather than only the exit code.
        self.assertIn("1.50", out)
        self.assertIn("     pad", out)
        self.assertIn("true", out)


# The same idea for Rust: every claim on the sheet that could plausibly be a
# misremembered method name, in one program. A wrong name will not compile,
# and a wrong behaviour trips an assert naming itself.
RUST_PROGRAM = r"""
use std::collections::HashMap;
use std::collections::HashSet;

#[derive(Debug, Clone, PartialEq)]
struct Point {
    x: i32,
    y: i32,
}

impl Point {
    fn new(x: i32) -> Self {
        Self { x, y: 0 }
    }
    fn total(&self) -> i32 {
        self.x + self.y
    }
}

#[derive(Debug)]
enum Shape {
    Circle(f64),
    Rect(f64, f64),
}

struct Wrapper(i32);

fn area(shape: &Shape) -> f64 {
    match shape {
        Shape::Circle(r) => *r,
        Shape::Rect(w, h) => w * h,
    }
}

fn borrows(s: &String) -> usize {
    s.len()
}

fn takes_str(s: &str) -> usize {
    s.len()
}

fn maybe_double(maybe: Option<i32>) -> Option<i32> {
    let n = maybe?;
    Some(n * 2)
}

fn run() -> Result<i32, String> {
    let n: i32 = "42".parse().map_err(|_| "bad".to_string())?;
    Ok(n)
}

fn main() {
    // ownership
    let a = String::from("x");
    let b = a.clone();
    let c = a;
    assert_eq!(b, c);
    let n = 5;
    let m = n;
    assert_eq!(n, m);
    assert_eq!(borrows(&b), 1);
    assert_eq!(takes_str("hi"), 2);
    assert_eq!(5.to_string(), "5");

    // Option
    let maybe: Option<i32> = Some(5);
    let nothing: Option<i32> = None;
    assert_eq!(match maybe { Some(v) => v, None => 0 }, 5);
    if let Some(v) = maybe { assert_eq!(v, 5); }
    assert_eq!(nothing.unwrap_or(0), 0);
    assert_eq!(nothing.unwrap_or_else(|| 1), 1);
    assert_eq!(maybe.unwrap(), 5);
    assert_eq!(maybe.expect("should exist"), 5);
    assert!(maybe.is_some() && nothing.is_none());
    assert_eq!(maybe.map(|v| v * 2), Some(10));
    assert_eq!(maybe_double(maybe), Some(10));
    assert_eq!(maybe_double(nothing), None);

    // Result
    let ok: Result<i32, String> = Ok(5);
    let bad: Result<i32, String> = Err("bad".to_string());
    assert!(ok.is_ok() && bad.is_err());
    assert_eq!(bad.unwrap_or(0), 0);
    assert!("42".parse::<i32>().is_ok());
    let parsed: i32 = "42".parse().unwrap();
    assert_eq!(parsed, 42);
    assert_eq!(run(), Ok(42));

    // Vec and slices
    let mut v: Vec<i32> = Vec::new();
    v.push(4);
    assert_eq!(v.pop(), Some(4));
    let zeros = vec![0; 10];
    assert_eq!(zeros.len(), 10);
    let mut v = vec![1, 2, 3];
    assert!(!v.is_empty());
    assert_eq!(v[0], 1);
    assert_eq!(v.get(0), Some(&1));
    assert_eq!(&v[1..3], &[2, 3]);
    assert_eq!(v.iter().sum::<i32>(), 6);
    assert!(v.contains(&3));
    v.sort();

    // iterators
    assert_eq!(v.iter().map(|n| n * 2).collect::<Vec<_>>(), vec![2, 4, 6]);
    assert_eq!(v.iter().filter(|n| **n > 2).count(), 1);
    let out: Vec<i32> = v.iter().map(|n| n * 2).collect();
    assert_eq!(out, vec![2, 4, 6]);
    assert_eq!(v.iter().enumerate().next(), Some((0, &1)));
    assert_eq!(v.iter().max(), Some(&3));
    assert_eq!(v.iter().min(), Some(&1));
    assert!(v.iter().any(|n| *n > 2));
    assert!(v.iter().all(|n| *n > 0));
    assert_eq!(v.iter().find(|n| **n > 2), Some(&3));
    assert_eq!(v.iter().rev().next(), Some(&3));
    assert_eq!(v.iter().fold(0, |acc, n| acc + n), 6);
    for x in &mut v { *x += 0; }
    for x in &v { assert!(*x > 0); }

    // strings
    let mut s = String::from("hi");
    assert_eq!(s.len(), 2);
    assert_eq!(s.chars().count(), 2);
    s.push_str(" more");
    assert!(s.contains("hi"));
    assert_eq!(s.split(',').count(), 1);
    assert_eq!("  x  ".trim(), "x");
    assert_eq!("a".to_uppercase(), "A");
    assert_eq!("aa".replace("a", "b"), "bb");
    assert_eq!(&s[0..2], "hi");
    assert_eq!(format!("{}-{}", 1, 2), "1-2");

    // structs and enums
    let p = Point { x: 1, y: 2 };
    let q = Point::new(1);
    assert_eq!(p.total(), 3);
    assert_eq!(q.y, 0);
    assert_eq!(p.clone(), p);
    assert_eq!(area(&Shape::Circle(2.0)), 2.0);
    assert_eq!(area(&Shape::Rect(2.0, 3.0)), 6.0);
    let w = Wrapper(7);
    assert_eq!(w.0, 7);

    // maps and sets
    let mut counts: HashMap<String, i32> = HashMap::new();
    counts.insert("a".to_string(), 1);
    assert_eq!(counts.get("a"), Some(&1));
    assert_eq!(counts["a"], 1);
    *counts.entry("a".to_string()).or_insert(0) += 1;
    assert_eq!(counts["a"], 2);
    assert!(counts.contains_key("a"));
    for (k, v) in &counts { assert!(!k.is_empty() && *v > 0); }
    let mut set: HashSet<i32> = HashSet::new();
    assert!(set.insert(3));

    // odds and ends
    const MAX: i32 = 100;
    let closure = |n: i32| n * 2;
    assert_eq!(closure(2), 4);
    assert_eq!(3.9_f64 as i32, 3);
    assert_eq!(MAX, 100);

    println!("{MAX}");
    println!("{}, {}", 1, 2);
    println!("{0} {1} {0}", 1, 2);
    println!("{:?}", v);
    println!("{:.2}", 1.5);
    println!("{:>8}", "pad");
    print!("no newline");
    println!();
    eprintln!("oops");
    println!("all good");
}
"""


class RustTests(unittest.TestCase):
    def test_the_sheets_claims_compile_and_hold(self) -> None:
        if shutil.which("rustc") is None:
            self.skipTest("needs rustc on PATH")
        out, err, code = run_code(RUST_PROGRAM, language="rust")
        self.assertEqual(code, 0, err or out)
        self.assertIn("all good", out)
        self.assertIn("1.50", out)
        self.assertIn("     pad", out)
        # A snippet someone copies should not teach them to ignore warnings.
        self.assertNotIn("warning:", err, err)


if __name__ == "__main__":
    unittest.main()
