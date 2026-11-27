"""Rust words, part 3: types and control by shape - structs, enums, impl blocks, methods and self, associated
functions, traits (and trait objects), generics and bounds, derive and the standard traits (PartialEq, PartialOrd,
Default), Option and Result, the ? operator, unwrap, error handling, and match with its patterns, guards, if let,
while let and let else.

Examples are the BODY of `fn main()` unless they mention `fn main(`; each is built by rustc debug and -O by
tests/test_glossary.py. Each rule that a program can show is a check in tests/glossary_rust_checks.py."""

from __future__ import annotations

from .entry import Entry, rust

TERMS: list[Entry] = [
    *rust(
        "struct",
        "Struct",
        "A custom type that groups named fields: struct Point { x: i32, y: i32 }. Make one with Point { x: 1, y: 2 } and read a field with p.x. Tuple structs (struct Meters(f64);) have positions instead of names.",
        see=("impl", "enum", "derive", "pub"),
        priority=60,
        aka=("structs", "record", "object", "class", "tuple struct", "unit struct", "data type", "struct update"),
        detect=(r"\bstruct\s+[A-Z]\w*",),
        rules=(
            "Every field must be given a value: Point { x: 1 } with y missing is an error. ..other fills the rest from another value.",
            "Changing a field needs the variable to be let mut: p.x = 5; on a plain let p is an error.",
            "If a variable has the field's name you can write Point { x, y } instead of Point { x: x, y: y }.",
            "A struct has no == and no {:?} until you derive or implement them.",
        ),
        example=r"""
            struct Point { x: i32, y: i32 }
            struct Meters(f64);
            fn main() {
                let p = Point { x: 1, y: 2 };
                let q = Point { x: 10, ..p };
                let m = Meters(2.5);
                println!("{} {} {}", q.x, q.y, m.0);
            }
        """,
        out=r"10 2 2.5",
    ),
    *rust(
        "enum",
        "Enum",
        "A type that is exactly one of several variants, each of which may carry data: enum Shape { Circle(f64), Rect { w: f64, h: f64 }, Empty }. You take one apart with match.",
        see=("match", "option", "struct", "pattern"),
        priority=60,
        aka=("enums", "variant", "variants", "sum type", "tagged union", "union", "algebraic data type", "enumeration"),
        detect=(r"\benum\s+[A-Z]\w*",),
        rules=(
            "A value is exactly one variant at a time, written Enum::Variant.",
            "A match on an enum must cover every variant; leaving one out is a compile error.",
            "Variants can carry different data: Circle(f64) holds one number, Rect { w, h } holds two.",
            "A variant with no data can be cast to its position: Color::Green as i32 is 1 when Green is the second variant.",
            "Option and Result are ordinary enums from the standard library.",
        ),
        example=r"""
            enum Shape { Circle(f64), Rect { w: f64, h: f64 }, Empty }
            fn area(s: &Shape) -> f64 {
                match s {
                    Shape::Circle(r) => 3.0 * r * r,
                    Shape::Rect { w, h } => w * h,
                    Shape::Empty => 0.0,
                }
            }
            fn main() {
                println!("{} {} {}", area(&Shape::Circle(2.0)), area(&Shape::Rect { w: 2.0, h: 3.5 }), area(&Shape::Empty));
            }
        """,
        out=r"12 7 0",
    ),
    *rust(
        "impl",
        "impl block",
        "impl Type { ... } adds functions to a type: methods, which take self, and associated functions, which do not, such as new. impl Trait for Type { ... } makes the type keep a trait's promises.",
        see=("method", "associated-function", "trait", "struct"),
        priority=55,
        aka=("implementation", "impl", "implement", "implements", "implementing", "methods block"),
        detect=(r"\bimpl\b",),
        rules=(
            "A type may have several impl blocks; their functions all belong to it.",
            "impl Trait for Type must supply every method the trait has no default for, or it does not compile.",
            "You cannot implement a foreign trait for a foreign type (the orphan rule): impl fmt::Display for Vec<i32> is an error.",
            "Inside an impl, Self means the type being implemented.",
        ),
        example=r"""
            struct Counter { n: u32 }
            impl Counter {
                fn new() -> Counter { Counter { n: 0 } }
                fn bump(&mut self) { self.n += 1; }
                fn get(&self) -> u32 { self.n }
            }
            fn main() {
                let mut c = Counter::new();
                c.bump();
                c.bump();
                println!("{}", c.get());
            }
        """,
        out=r"2",
    ),
    *rust(
        "method",
        "Method",
        "A function inside an impl whose first parameter is self, &self or &mut self. You call it with a dot, counter.bump(), and the dot borrows or moves the receiver for you.",
        see=("self-parameter", "impl", "associated-function", "function"),
        priority=50,
        aka=("methods", "member function", "instance method", "method call", "dot call", "member"),
        detect=(r"\bfn\s+\w+\s*(?:<[^>\n]{0,30}>)?\(\s*&?(?:mut\s+)?self\b",),
        rules=(
            "r.area() is shorthand for Rect::area(&r); both give the same answer.",
            "A method that takes &mut self can only be called on a variable declared let mut.",
            "A method that takes self by value uses the value up: after r.consume(), r cannot be used.",
            "A function in an impl with no self is not a method: it is called as Type::name(), not with a dot.",
        ),
        example=r"""
            struct Rect { w: u32, h: u32 }
            impl Rect {
                fn area(&self) -> u32 { self.w * self.h }
                fn double(&mut self) { self.w *= 2; self.h *= 2; }
            }
            fn main() {
                let mut r = Rect { w: 2, h: 3 };
                r.double();
                println!("{}", r.area());
            }
        """,
        out=r"24",
    ),
    *rust(
        "self-parameter",
        "self, &self, &mut self",
        "The first parameter of a method: self takes the value (using it up), &self borrows it to read, &mut self borrows it to change. Inside the body it is the thing the method was called on; Self (capital) is the type itself.",
        see=("method", "impl", "borrowing", "mutable-reference"),
        priority=60,
        aka=("self", "&self", "&mut self", "this", "receiver", "self keyword", "self type"),
        detect=(r"&\s*mut\s+self\b|&\s*self\b|\(\s*self\b",),
        rules=(
            "&self may read fields but not change them: self.n += 1; inside a &self method is a compile error.",
            "self by value moves the value in: after t.empty() with fn empty(self), t is gone.",
            "&mut self allows self.n += 1; and needs the caller's variable to be mut.",
            "Self is the type name: Self { litres: 100 } builds one, and fn full() -> Self works inside the impl.",
        ),
        example=r"""
            struct Tank { litres: u32 }
            impl Tank {
                fn level(&self) -> u32 { self.litres }
                fn fill(&mut self, n: u32) { self.litres += n; }
                fn empty(self) -> u32 { self.litres }
                fn full() -> Self { Self { litres: 100 } }
            }
            fn main() {
                let mut t = Tank::full();
                t.fill(5);
                println!("{}", t.level());
                println!("{}", t.empty());
            }
        """,
        out=r"""105
105""",
    ),
    *rust(
        "associated-function",
        "Associated function (::new)",
        "A function in an impl block with no self parameter. You call it on the type with ::, as in Point::new(1, 2). Rust has no constructors; by convention a function named new builds a value.",
        see=("impl", "method", "struct", "default-trait"),
        priority=50,
        aka=("::new", "new", "constructor", "static method", "class method", "factory", "associated functions", "associated const"),
        detect=(r"\b[A-Z]\w*::[a-z_]\w*\s*\(",),
        rules=(
            "It is called with ::, not with a dot: p.new(1, 2) is an error.",
            "new is only a habit; any name works, such as Point::origin().",
            "String::from, Vec::new and Box::new are all associated functions.",
            "An impl can also hold associated constants, read as Type::NAME.",
        ),
        example=r"""
            struct Point { x: i32, y: i32 }
            impl Point {
                const ORIGIN: Point = Point { x: 0, y: 0 };
                fn new(x: i32, y: i32) -> Point { Point { x, y } }
            }
            fn main() {
                let p = Point::new(3, 4);
                println!("{} {} {}", p.x, p.y, Point::ORIGIN.x);
            }
        """,
        out=r"3 4 0",
    ),
    *rust(
        "trait",
        "Trait",
        "A set of method signatures a type promises to provide, like an interface: trait Speak { fn speak(&self) -> String; }. A type joins with impl Speak for Dog. A trait may also give default method bodies.",
        see=("impl", "trait-object", "trait-bound", "derive"),
        priority=65,
        aka=("interface", "traits", "protocol", "abstract class", "typeclass", "trait definition", "default method"),
        detect=(r"\btrait\s+[A-Z]\w*|\bimpl\b[^{\n]{0,80}\bfor\b",),
        rules=(
            "impl Trait for Type must write every method that has no default body; leaving one out is a compile error.",
            "A default method is used unless the impl writes its own, which overrides it.",
            "A trait's methods can be called only where the trait is in scope: a trait in another module needs a use.",
            "You can implement your own trait for built-in types: impl Double for i32 gives every i32 a double method.",
        ),
        example=r"""
            trait Speak {
                fn name(&self) -> String;
                fn speak(&self) -> String { format!("{} makes a sound", self.name()) }
            }
            struct Dog;
            struct Cat;
            impl Speak for Dog { fn name(&self) -> String { "Dog".to_string() } }
            impl Speak for Cat {
                fn name(&self) -> String { "Cat".to_string() }
                fn speak(&self) -> String { "Cat purrs".to_string() }
            }
            fn main() {
                println!("{}", Dog.speak());
                println!("{}", Cat.speak());
            }
        """,
        out=r"""Dog makes a sound
Cat purrs""",
    ),
    *rust(
        "trait-object",
        "Trait object (dyn)",
        "dyn Trait is a value whose exact type is known only at run time, used behind a pointer such as Box<dyn Trait> or &dyn Trait. It lets one Vec hold different types that share a trait; calls look the method up at run time.",
        see=("trait", "box", "generic", "trait-bound"),
        priority=75,
        aka=("dyn", "dyn trait", "dynamic dispatch", "box dyn", "polymorphism", "virtual function", "vtable", "dynamic polymorphism"),
        detect=(r"\bdyn\s+[A-Z]",),
        rules=(
            "A Vec<Sq> holds only Sq values; Vec<Box<dyn Shape>> can hold a Sq and a Circle together.",
            "dyn needs a pointer: Vec<dyn Shape> is an error, because the size of the items is not known.",
            "Only traits that can be called without knowing the type work as dyn: a trait with a function returning Self does not.",
            "A generic function (T: Shape) is settled at compile time; a dyn Shape call is settled at run time.",
        ),
        example=r"""
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
        """,
        out=r"7",
    ),
    *rust(
        "generic",
        "Generic",
        "Code written once for many types by using a type parameter: fn first<T>(items: &[T]) -> &T, struct Pair<T>, Vec<T>. The compiler makes a specialised copy for each type used, so it runs as fast as hand-written code.",
        see=("trait-bound", "turbofish", "trait", "struct"),
        priority=55,
        aka=("generics", "type parameter", "type variable", "template", "generic type", "generic function", "parametric polymorphism", "monomorphization"),
        detect=(r"\b(?:fn|struct|enum|trait)\s+\w+\s*<\s*[A-Z]|\bimpl\s*<\s*[A-Z]",),
        rules=(
            "T is a placeholder filled in for each use: Pair<i32> and Pair<f64> are different types.",
            "Both fields of Pair<T> have the same T: Pair { a: 1, b: 2.5 } is an error.",
            "Inside a generic function you can only do what the bounds allow: a > b on a bare T is an error until you write T: PartialOrd.",
            "If nothing fixes T, Rust asks for a type: let v = Vec::new(); that is never used is an error.",
        ),
        example=r"""
            struct Pair<T> { a: T, b: T }
            impl<T: PartialOrd + Copy> Pair<T> {
                fn larger(&self) -> T { if self.a > self.b { self.a } else { self.b } }
            }
            fn first<T>(items: &[T]) -> &T { &items[0] }
            fn main() {
                println!("{} {}", Pair { a: 3, b: 9 }.larger(), Pair { a: 2.5, b: 1.5 }.larger());
                println!("{}", first(&["x", "y"]));
            }
        """,
        out=r"""9 2.5
x""",
    ),
    *rust(
        "trait-bound",
        "Trait bound",
        "A requirement on a generic type: <T: Display + Clone> says T must implement both traits. It can also go in a where clause, or be written as impl Display for a parameter. Only what the bounds promise may be done with the value.",
        see=("generic", "trait", "display", "partial-ord"),
        priority=65,
        aka=("bound", "bounds", "where clause", "where", "impl trait", "constraint", "trait constraint", "t: display"),
        detect=(r"\bwhere\b|\b[A-Z]\s*:\s*[A-Z]\w*(?:\s*\+\s*[A-Z]\w*)*|:\s*impl\s+[A-Z]",),
        rules=(
            "Without a bound the operation is refused: println!(\"{}\", x) on a bare T is an error; T: Display fixes it.",
            "Calling with a type that lacks the trait is an error: show_twice(vec![1]) fails because Vec has no Display.",
            "+ combines bounds, and where T: A + B means the same as <T: A + B>.",
            "fn f(x: impl Display) is shorthand for a generic with that bound.",
        ),
        example=r"""
            use std::fmt::Display;
            fn show_twice<T: Display>(x: T) -> String { format!("{x} {x}") }
            fn biggest<T>(items: &[T]) -> &T where T: PartialOrd {
                let mut best = &items[0];
                for it in items { if it > best { best = it; } }
                best
            }
            fn main() {
                println!("{} {}", show_twice(7), biggest(&[3, 8, 5]));
            }
        """,
        out=r"7 7 8",
    ),
    *rust(
        "derive",
        "derive",
        "#[derive(...)] above a struct or enum asks the compiler to write the standard impl for you: Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash, Default. It works only if every field has that trait too.",
        see=("attribute", "partial-eq", "partial-ord", "default-trait", "debug-format"),
        priority=75,
        aka=("#[derive]", "derive macro", "derives", "derived", "auto implement", "derived trait", "derive attribute"),
        detect=(r"#\[derive\(",),
        rules=(
            "Every field must have the derived trait: derive(Clone) on a struct that holds a field type without Clone is an error.",
            "Derived PartialOrd compares fields from the first to the last: V(1, 9) < V(2, 0) is true.",
            "Eq and Ord cannot be derived when a field is an f64.",
            "Copy needs Clone as well: #[derive(Copy)] alone is an error.",
        ),
        example=r"""
            #[derive(Debug, Clone, PartialEq, Default)]
            struct Config { name: String, retries: u32 }
            fn main() {
                let a = Config { name: String::from("x"), retries: 3 };
                let b = a.clone();
                println!("{} {:?}", a == b, Config::default());
            }
        """,
        out=r"""true Config { name: "", retries: 0 }""",
    ),
    *rust(
        "partial-eq",
        "PartialEq and Eq",
        "The trait behind == and !=. Derive it to compare two values field by field. Floats are only PartialEq (NaN is not equal to itself); types where every value equals itself can also be Eq, which hash-map keys need.",
        see=("derive", "partial-ord", "hashmap", "floating-point"),
        priority=65,
        aka=("partialeq", "eq", "equality", "==", "!=", "equals", "eq trait", "equal"),
        detect=(r"\bPartialEq\b|\bEq\b",),
        rules=(
            "== on your own type does not compile until it has PartialEq.",
            "A derived == compares every field, and for an enum the variant and its data.",
            "Different types do not compare: 1 == 1.0 is an error.",
            "&a == &b compares the values the references point to, not the addresses.",
            "An f64 cannot be a HashSet or HashMap key, because f64 is not Eq.",
        ),
        example=r"""
            #[derive(PartialEq, Debug)]
            enum Light { Red, Green }
            #[derive(PartialEq)]
            struct P { x: i32, y: i32 }
            fn main() {
                println!("{} {}", Light::Red == Light::Green, P { x: 1, y: 2 } == P { x: 1, y: 2 });
                println!("{}", f64::NAN == f64::NAN);
            }
        """,
        out=r"""false true
false""",
    ),
    *rust(
        "partial-ord",
        "PartialOrd and Ord",
        "The traits behind < > <= >= and sorting. Ord gives a full order and .cmp() returning Less, Equal or Greater; PartialOrd is for types such as f64 where some values (NaN) cannot be compared. Derive them to compare fields in order.",
        see=("derive", "partial-eq", "sorting", "floating-point"),
        priority=65,
        aka=("partialord", "ord", "ordering", "comparison", "cmp", "partial_cmp", "<", "compare", "comparator", "order"),
        detect=(r"\bPartialOrd\b|\bOrd\b|\.cmp\(|\.partial_cmp\(|\bOrdering\b",),
        rules=(
            "A derived order for an enum follows the order the variants are written: Low < Mid < High.",
            "A derived order for a struct compares the fields from first to last.",
            "f64::partial_cmp returns an Option: Some(Greater) normally and None when a NaN is involved.",
            "sort() needs Ord, which floats lack; sort a Vec<f64> with sort_by(|a, b| a.partial_cmp(b).unwrap()).",
        ),
        example=r"""
            use std::cmp::Ordering;
            #[derive(PartialEq, Eq, PartialOrd, Ord, Debug)]
            enum Rank { Low, Mid, High }
            fn main() {
                println!("{} {:?}", Rank::Low < Rank::High, 3i32.cmp(&5));
                println!("{:?} {:?}", 2.5_f64.partial_cmp(&1.0), f64::NAN.partial_cmp(&1.0));
                println!("{}", Rank::Mid.cmp(&Rank::Mid) == Ordering::Equal);
            }
        """,
        out=r"""true Less
Some(Greater) None
true""",
    ),
    *rust(
        "default-trait",
        "Default",
        "The Default trait gives a type its empty value: 0 for numbers, false, an empty String or Vec, None. #[derive(Default)] builds it field by field, and ..Default::default() fills the fields you leave out.",
        see=("derive", "struct", "associated-function", "unwrap"),
        priority=65,
        aka=("default", "default()", "default value", "..default::default()", "zero value", "unwrap_or_default"),
        detect=(r"\bDefault\b|\bdefault\(\)",),
        rules=(
            "The defaults are 0, 0.0, false, '\\0', an empty String, an empty Vec and None.",
            "#[derive(Default)] needs every field to have a Default, or it is an error.",
            "Struct { volume: 7, ..Default::default() } sets volume and takes the rest from Default.",
            "opt.unwrap_or_default() gives the value inside, or the type's default when it is None.",
        ),
        example=r"""
            #[derive(Debug, Default)]
            struct Settings { volume: u8, name: String, muted: bool, tags: Vec<i32> }
            fn main() {
                let s = Settings { volume: 7, ..Default::default() };
                println!("{:?}", s);
                let n: i32 = Default::default();
                println!("{} {:?}", n, Option::<i32>::default());
            }
        """,
        out=r"""Settings { volume: 7, name: "", muted: false, tags: [] }
0 None""",
    ),
    *rust(
        "option",
        "Option",
        "A value that may be missing: Some(value) or None. It is an ordinary enum, so Rust has no null; the compiler makes you handle None before you can use what is inside.",
        see=("match", "if-let", "unwrap", "question-mark", "result"),
        priority=60,
        aka=("none", "some", "null", "maybe", "optional", "nullable", "nil", "option type", "option<t>"),
        detect=(r"\bOption\b|\bSome\(|\bNone\b",),
        rules=(
            "An Option<i32> is not an i32: Some(1) + 1 and let x: i32 = Some(1); are errors. Handle None first, with match, if let, unwrap_or or map.",
            "map changes what is inside: Some(2).map(|x| x + 1) is Some(3), and None stays None.",
            "ok_or(e) turns an Option into a Result: None becomes Err(e).",
            "Vec::get, str::find, iter().next() and HashMap::get all return an Option instead of panicking.",
        ),
        example=r"""
            let v = vec![10, 20];
            let a = v.get(1);
            let b = v.get(5);
            println!("{:?} {:?}", a, b);
            println!("{} {}", b.is_none(), b.copied().unwrap_or(0));
            println!("{:?}", a.map(|n| n * 2));
        """,
        out=r"""Some(20) None
true 0
Some(40)""",
    ),
    *rust(
        "result",
        "Result",
        "The outcome of something that can fail: Ok(value) when it worked, Err(error) when it did not. It is an ordinary enum; the compiler warns if you ignore one, and ? passes an Err up to the caller.",
        see=("question-mark", "unwrap", "error-handling", "option"),
        priority=60,
        aka=("ok", "err", "result<t, e>", "error type", "fallible", "success or failure", "result type"),
        detect=(r"\bResult\b|\bOk\(|\bErr\(",),
        rules=(
            "The two sides may have different types: Result<i32, String> holds an i32 on success and a String on failure.",
            "\"7\".parse::<i32>() is Ok(7) and \"x\".parse::<i32>() is an Err.",
            "map_err changes the error type and ok() turns the Result into an Option.",
            "A function declared to return Result must return Ok(...) or Err(...): ending with a bare 5 is an error.",
        ),
        example=r"""
            fn half(n: i32) -> Result<i32, String> {
                if n % 2 == 0 { Ok(n / 2) } else { Err(format!("{} is odd", n)) }
            }
            fn main() {
                println!("{:?} {:?}", half(8), half(7));
                println!("{}", half(7).unwrap_or(-1));
                match half(4) {
                    Ok(v) => println!("ok {}", v),
                    Err(e) => println!("err {}", e),
                }
            }
        """,
        out=r"""Ok(4) Err("7 is odd")
-1
ok 2""",
    ),
    *rust(
        "question-mark",
        "? operator",
        "Placed after a Result or Option, ? gives the value inside when it is Ok or Some, and otherwise returns the Err or None from the whole function at once. It only works in a function that returns a matching Result or Option.",
        see=("result", "option", "error-handling", "unwrap"),
        priority=70,
        aka=("?", "try operator", "propagate", "error propagation", "early return", "question mark", "try"),
        detect=(r"[\w)\]]\?\s*(?:;|\.|\)|$)",),
        rules=(
            "Using ? in a function that returns () (such as main) is a compile error.",
            "On an Option it needs a function returning Option: v.first()? returns None early when v is empty.",
            "The error is converted with From, so ? can turn many error types into Box<dyn Error>.",
            "Option and Result do not mix: ? on an Option inside a function returning Result is an error.",
        ),
        example=r"""
            fn add_strs(a: &str, b: &str) -> Result<i32, std::num::ParseIntError> {
                let x: i32 = a.parse()?;
                let y: i32 = b.parse()?;
                Ok(x + y)
            }
            fn main() {
                println!("{:?}", add_strs("2", "3"));
                println!("{}", add_strs("2", "z").is_err());
            }
        """,
        out=r"""Ok(5)
true""",
    ),
    *rust(
        "unwrap",
        "unwrap and expect",
        "unwrap() takes the value out of Some or Ok and panics on None or Err; expect(\"msg\") does the same with your message. unwrap_or(x) and unwrap_or_else(f) give a fallback instead of panicking.",
        see=("panic", "option", "result", "question-mark"),
        priority=70,
        aka=("expect", "unwrap_or", "unwrap_or_else", ".unwrap()", "force unwrap", "unwrap_err"),
        detect=(r"\.(?:unwrap|expect|unwrap_or|unwrap_or_else|unwrap_or_default)\(",),
        rules=(
            "None.unwrap() panics, and so does Err(e).unwrap().",
            "expect(\"msg\") panics too, with your message in the panic text.",
            "unwrap_or(costly()) always runs costly(); unwrap_or_else(costly) runs it only when the value is missing.",
            "unwrap_or_default() gives 0, an empty String and so on instead of panicking.",
        ),
        example=r"""
            let ok: Result<i32, String> = Ok(5);
            let none: Option<i32> = None;
            println!("{} {}", ok.clone().unwrap(), none.unwrap_or(0));
            println!("{}", none.unwrap_or_else(|| 40 + 2));
            println!("{}", "x".parse::<i32>().unwrap_or_default());
        """,
        out=r"""5 0
42
0""",
    ),
    *rust(
        "error-handling",
        "Error handling",
        "Rust has no exceptions. A function that can fail returns a Result; the caller matches on it, passes it up with ?, or falls back to a default. Panics are for bugs that should never happen, not for failures you expect.",
        see=("result", "question-mark", "panic", "option"),
        priority=50,
        aka=("errors", "error", "try catch", "exception handling", "map_err", "box dyn error", "std::error::error", "exceptions", "ok_or"),
        detect=(r"\bmap_err\b|\bBox<dyn\s+(?:std::)?error::Error|\bimpl\b[^{\n]{0,60}\bError\b|\.ok_or\w*\(",),
        rules=(
            "ok_or(e) turns None into Err(e); map_err(f) changes the error value of an Err.",
            "A function that returns Result<(), String> can use ? inside and ends with Ok(()) when nothing went wrong.",
            "A type that implements Display and Error can be returned as Box<dyn Error>.",
            "An Err that nobody looks at is not a crash; the program carries on.",
        ),
        example=r"""
            #[derive(Debug)]
            enum AgeError { NotANumber, TooBig(u32) }
            fn parse_age(s: &str) -> Result<u32, AgeError> {
                let n: u32 = s.parse().map_err(|_| AgeError::NotANumber)?;
                if n > 150 { Err(AgeError::TooBig(n)) } else { Ok(n) }
            }
            fn main() {
                for s in ["42", "abc", "200"] {
                    println!("{:?}", parse_age(s));
                }
            }
        """,
        out=r"""Ok(42)
Err(NotANumber)
Err(TooBig(200))""",
    ),
    *rust(
        "match",
        "match",
        "Compares a value against a list of patterns from the top and runs the first arm that fits. It is an expression, and it must be exhaustive: every possible value has to be covered, or the program does not compile.",
        see=("pattern", "match-guard", "enum", "if-let"),
        priority=60,
        aka=("switch", "case", "match expression", "match arm", "switch statement", "exhaustive", "exhaustiveness", "arm"),
        detect=(r"\bmatch\b",),
        rules=(
            "Every value must be covered: matching an integer with arms 0 and 1 only is an error; add _ => ... for the rest.",
            "The first arm that fits wins, and only that one runs; there is no fall-through.",
            "All arms must give the same type, because the match is an expression.",
            "name @ pattern gives a name to what matched: n @ 1..=9 => n * 2.",
            "A String cannot be matched against \"text\" literals; match s.as_str().",
        ),
        example=r"""
            let n = 7;
            let word = match n {
                0 => "zero",
                1..=5 => "small",
                6 | 7 => "six or seven",
                _ => "big",
            };
            println!("{}", word);
        """,
        out=r"six or seven",
    ),
    *rust(
        "pattern",
        "Pattern",
        "The shape on the left of a match arm, a let, an if let or a parameter. It checks a value's form and, in the same step, names its parts: (x, y), Some(n), Point { x, .. }, 1..=5, _.",
        see=("match", "if-let", "let-else", "tuple"),
        priority=55,
        aka=("pattern matching", "destructuring", "destructure", "wildcard", "underscore", "binding pattern", "irrefutable", "refutable"),
        detect=(r"\b_\s*=>|\blet\s+(?:\(|[A-Z]\w*\s*[({])|\.\.=\s*\w+\s*=>",),
        rules=(
            "let (a, b) = t; takes a tuple apart, and let P { x, .. } = p; takes one field out of a struct.",
            "_ ignores one part and .. ignores all the rest: let [first, .., last] = array;.",
            "a | b matches either, and ranges such as 'a'..='m' or 1..=5 match a span.",
            "A plain let needs a pattern that always fits: let Some(x) = opt; is an error; use if let or let else.",
            "Patterns nest: Some((a, b)) takes a pair out of an Option.",
        ),
        example=r"""
            struct P { x: i32, y: i32 }
            fn main() {
                let (a, b) = (1, 2);
                let P { x, .. } = P { x: 10, y: 20 };
                let [first, .., last] = [1, 2, 3, 4];
                println!("{} {} {} {} {}", a, b, x, first, last);
            }
        """,
        out=r"1 2 10 1 4",
    ),
    *rust(
        "match-guard",
        "Match guard (if)",
        "An extra if after a pattern in a match arm: Some(n) if n > 3 => .... The arm runs only when the pattern fits AND the guard is true; otherwise matching goes on with the next arm.",
        see=("match", "pattern", "if-expression"),
        priority=70,
        aka=("guard", "guard clause", "match if", "conditional pattern", "arm guard"),
        detect=(r"\bif\b[^\n{;]{0,60}=>",),
        rules=(
            "When the guard is false, the next arm is tried: Some(1) with the guard x > 5 falls to the Some(_) arm.",
            "The compiler does not use guards to prove exhaustiveness: arms x if x > 0 and x if x <= 0 still need a catch-all.",
            "With a | b if cond, the guard is tested for every alternative: 1 | 2 if n > 1 does not run for n = 1.",
        ),
        example=r"""
            for n in [Some(1), Some(8), None] {
                let text = match n {
                    Some(x) if x > 5 => "big",
                    Some(_) => "small",
                    None => "none",
                };
                println!("{}", text);
            }
        """,
        out=r"""small
big
none""",
    ),
    *rust(
        "if-let",
        "if let",
        "if let PATTERN = value { ... } runs the block only when the value fits the pattern, and names its parts inside. It is a short match for the one case you care about; add else for the rest.",
        see=("match", "option", "while-let", "let-else"),
        priority=65,
        aka=("if-let", "iflet", "conditional binding", "optional binding", "if let some"),
        detect=(r"\bif\s+let\b",),
        rules=(
            "It need not be exhaustive: values that do not fit are simply skipped.",
            "else runs when the pattern does not fit, and else if let chains several patterns.",
            "The names bound by the pattern exist only inside the block.",
            "if let Some(s) = o moves a String out of o; use if let Some(s) = &o to keep o usable afterwards.",
        ),
        example=r"""
            let v = vec![3, 9];
            if let Some(x) = v.first() {
                println!("first {}", x);
            }
            let r: Result<i32, String> = Err("no".to_string());
            if let Ok(n) = r { println!("{}", n); } else { println!("failed"); }
        """,
        out=r"""first 3
failed""",
    ),
    *rust(
        "while-let",
        "while let",
        "while let PATTERN = expr { ... } repeats as long as the value fits the pattern. The classic use is emptying a stack: while let Some(top) = stack.pop() { ... } stops by itself when pop gives None.",
        see=("if-let", "while-loop", "option", "vector"),
        priority=70,
        aka=("while-let", "whilelet", "pop loop"),
        detect=(r"\bwhile\s+let\b",),
        rules=(
            "The loop ends the first time the pattern does not fit.",
            "stack.pop() returns the last item, so a while let over pop visits the items last to first and leaves the Vec empty.",
            "It also drives an iterator by hand: while let Some(x) = it.next() { ... }.",
        ),
        example=r"""
            let mut stack = vec![1, 2, 3];
            while let Some(top) = stack.pop() {
                println!("{}", top);
            }
            println!("{}", stack.len());
        """,
        out=r"""3
2
1
0""",
    ),
    *rust(
        "let-else",
        "let else",
        "let PATTERN = value else { ... }; names the pattern's parts for the rest of the function when the value fits, and otherwise runs the else block, which must leave (return, break, continue or panic).",
        see=("if-let", "pattern", "option", "question-mark"),
        priority=75,
        aka=("let-else", "else return", "guard let", "early exit"),
        detect=(r"\blet\s+[^;=\n]{1,60}=[^;\n]{1,80}\belse\s*\{",),
        rules=(
            "The else block must not fall through: one that just prints and ends is a compile error.",
            "The names are usable after the statement, in the surrounding block, not only inside braces as with if let.",
            "It keeps the normal path flat: no nesting for the success case.",
        ),
        example=r"""
            fn first_word_len(s: &str) -> usize {
                let Some(word) = s.split_whitespace().next() else {
                    return 0;
                };
                word.len()
            }
            fn main() {
                println!("{} {}", first_word_len("hello world"), first_word_len("   "));
            }
        """,
        out=r"5 0",
    ),
]
