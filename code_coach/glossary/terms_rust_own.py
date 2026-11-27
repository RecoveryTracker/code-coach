"""Rust words, part 2: ownership - owners, moves, Copy and Clone, borrowing and references (&, &mut, *), the borrow
checker and lifetimes, smart pointers (Box, Rc, RefCell), Drop, mem::swap, and unsafe.

Every example is the BODY of `fn main()` unless it mentions `fn main(`; each is built by rustc debug and -O by
tests/test_glossary.py. Each rule that a program can show is a check in tests/glossary_rust_checks.py (a borrow-checker
rule is a check whose expected value is "CE": rustc refuses it)."""

from __future__ import annotations

from .entry import Entry, rust

TERMS: list[Entry] = [
    *rust(
        "ownership",
        "Ownership",
        "Rust's rule for memory: every value has exactly one owner, a variable. When the owner goes out of scope the value is dropped (freed). Ownership can be handed over (a move) or lent out (a borrow).",
        see=("move", "borrowing", "drop", "copy", "borrow-checker"),
        priority=40,
        aka=("owner", "owners", "owned", "owning", "memory safety", "garbage collection"),
        rules=(
            "A value has one owner at a time: after let b = a; with a String, a no longer owns it and reading a is a compile error.",
            "Passing a String to a function by value moves it in: the caller cannot use it afterwards, unless the function returns it.",
            "When the owner goes out of scope the value is dropped exactly once, with no garbage collector.",
            "Copy types such as i32 are duplicated instead of moved, so their old name stays usable.",
        ),
        example=r"""
            fn consume(s: String) -> usize {
                s.len()
            }
            fn main() {
                let a = String::from("hello");
                let n = consume(a);
                println!("{}", n);
            }
        """,
        out=r"5",
    ),
    *rust(
        "move",
        "Move",
        "Giving a value to a new owner: let b = a;, passing it to a function, or a move closure. Afterwards the old name cannot be used. A move copies no heap data; only the owner changes.",
        see=("ownership", "copy", "clone", "closure"),
        priority=60,
        aka=("move semantics", "moved value", "moved", "moves", "use after move", "transfer ownership", "borrow of moved value"),
        detect=(r"\bmove\s*\|",),
        rules=(
            "let b = a; moves a when its type is not Copy (String, Vec, Box...): reading a afterwards is the error 'borrow of moved value'.",
            "A moved-from variable declared mut may be given a new value, and is usable again.",
            "You cannot move out of a Vec by index: let s = v[0]; with Strings is an error; use &v[0], v[0].clone() or v.remove(0).",
            "A move closure takes ownership of what it uses.",
        ),
        example=r"""
            let a = vec![1, 2, 3];
            let b = a;
            println!("{:?}", b);
            let f = move || b.len();
            println!("{}", f());
        """,
        out=r"""[1, 2, 3]
3""",
    ),
    *rust(
        "copy",
        "Copy",
        "A type is Copy when assigning or passing it makes an exact duplicate and the original stays usable. Integers, floats, bool, char, &T and tuples or arrays of Copy things are Copy; String and Vec are not.",
        see=("move", "clone", "ownership", "derive"),
        priority=65,
        aka=("copy trait", "copy types", "bitwise copy", "pass by value", "copied"),
        detect=(r"\bCopy\b",),
        rules=(
            "After let b = a; with a Copy type, a is still usable: let a = (1, 2.5, 'c', true); let b = a; works.",
            "A struct is Copy only if you ask: #[derive(Clone, Copy)], and every field must be Copy too. A struct holding a Vec cannot be Copy.",
            "Without Copy a struct is moved: let b = a; then a.x is an error.",
            "A type with a Drop impl cannot be Copy.",
        ),
        example=r"""
            #[derive(Clone, Copy, Debug)]
            struct P { x: i32 }
            fn main() {
                let a = P { x: 1 };
                let b = a;
                let n = 5;
                let m = n;
                println!("{:?} {:?} {} {}", a, b, n, m);
            }
        """,
        out=r"P { x: 1 } P { x: 1 } 5 5",
    ),
    *rust(
        "clone",
        "Clone",
        "A full, independent copy made on request with .clone(): a new value with its own owner. It can cost time and memory, so Rust makes you ask for it.",
        see=("copy", "move", "rc", "derive"),
        priority=70,
        aka=("clone()", "deep copy", "duplicate", "clone trait", "shallow copy", "cloning"),
        detect=(r"\.clone\(\)|\bClone\b",),
        rules=(
            "After let b = a.clone(); both a and b are usable, and changing one leaves the other alone.",
            "Your own struct needs #[derive(Clone)] before .clone() works.",
            "Cloning a Vec<String> clones every String too, so the copies are fully independent.",
            "Rc::clone(&a) is different: it copies only the pointer and adds an owner of the same data.",
        ),
        example=r"""
            let a = vec![1, 2, 3];
            let mut b = a.clone();
            b.push(4);
            println!("{:?} {:?}", a, b);
        """,
        out=r"[1, 2, 3] [1, 2, 3, 4]",
    ),
    *rust(
        "borrowing",
        "Borrowing",
        "Using a value through a reference instead of taking it: &x lends it read-only, &mut x lends it for changing. The owner keeps ownership and gets full use of the value back when the loan ends.",
        see=("reference", "mutable-reference", "borrow-checker", "ownership"),
        priority=50,
        aka=("borrow", "borrowed", "borrows", "lend", "loan", "borrowed value"),
        detect=(r"(?:[(,=]|\bin|\breturn)\s*&\s*(?:mut\s+)?[a-z_]\w*",),
        rules=(
            "Lending with & leaves the owner usable afterwards: total(&v) and then v.len() is fine.",
            "Any number of shared & borrows may exist at once.",
            "A &mut borrow must be the only one: two &mut of the same value at the same time is a compile error, and so is a & alongside a &mut.",
            "While a borrow is still going to be used, the owner cannot be moved or changed: let r = &s; let t = s; println!(\"{}\", r); is an error.",
        ),
        example=r"""
            fn total(v: &Vec<i32>) -> i32 {
                v.iter().sum()
            }
            fn main() {
                let v = vec![1, 2, 3];
                let t = total(&v);
                println!("{} {}", t, v.len());
            }
        """,
        out=r"6 3",
    ),
    *rust(
        "reference",
        "Reference (&)",
        "A pointer to a value you do not own: &T (read-only) or &mut T (read and write). It always points at a live value, is never null, and cannot outlive what it points to.",
        see=("borrowing", "mutable-reference", "dereference", "lifetime"),
        priority=45,
        aka=("references", "ref", "&", "pointer", "pointers", "address", "borrowed pointer", "null pointer"),
        detect=(r":\s*&\s*(?:'\w+\s+)?(?:mut\s+)?[A-Za-z\[]",),
        rules=(
            "A reference prints and compares like the value it points to: println!(\"{}\", r) shows the number, and r == &10 is true.",
            "A reference cannot outlive its value: storing &x in a variable that lives longer than x is a compile error.",
            "There is no null reference; use Option<&T> where there might be none.",
            "&T is Copy (copying a reference is cheap and fine); &mut T is not.",
        ),
        example=r"""
            let x = 10;
            let r = &x;
            println!("{} {} {}", r, *r + 1, r == &10);
        """,
        out=r"10 11 true",
    ),
    *rust(
        "mutable-reference",
        "&mut (mutable reference)",
        "A reference that lets you change the value it points to. While it is in use it is the ONLY way to reach that value: no other reference, shared or mutable, may be used at the same time.",
        see=("borrowing", "dereference", "mutability", "borrow-checker"),
        priority=70,
        aka=("mutable borrow", "exclusive reference", "mutable borrowing", "mut reference", "mutable reference"),
        detect=(r"&\s*mut\b",),
        rules=(
            "&mut x needs x to be declared let mut: taking &mut of a plain let variable is an error.",
            "Only one &mut at a time: let r1 = &mut s; let r2 = &mut s; with both used is an error.",
            "Assigning through it needs a star: *n += 1; writing n += 1; on a &mut i32 is a type error.",
            "While a &mut is still going to be used, even reading the owner is an error.",
        ),
        example=r"""
            fn bump(n: &mut i32) {
                *n += 1;
            }
            fn main() {
                let mut x = 5;
                bump(&mut x);
                bump(&mut x);
                println!("{}", x);
            }
        """,
        out=r"7",
    ),
    *rust(
        "dereference",
        "Dereference (*)",
        "The * operator follows a reference (or a Box) to the value behind it: if r is a &i32 then *r is the i32. Method calls and printing do it for you; assigning through a &mut needs it written.",
        see=("reference", "mutable-reference", "box"),
        priority=60,
        aka=("deref", "*", "dereferencing", "deref coercion", "star operator", "auto-deref"),
        detect=(r"(?:^|[;{(,]|\s)\*\s*\(?[a-z_]\w*\)?\s*(?:[-+*/%]=|=(?!=))",),
        rules=(
            "To change a value through a &mut you write *r = 9; plain r = 9; is a type error.",
            "Method calls and println! look through references by themselves: r.abs() and println!(\"{}\", r) need no star.",
            "A reference is not the value: r == 5 with r a &i32 is an error; write *r == 5.",
            "A Box is followed the same way: *Box::new(7) is 7.",
        ),
        example=r"""
            let mut x = 5;
            let r = &mut x;
            *r += 10;
            let b = Box::new(7);
            println!("{} {}", x, *b + 1);
        """,
        out=r"15 8",
    ),
    *rust(
        "borrow-checker",
        "Borrow checker",
        "The part of the compiler that checks every reference: none may outlive its value, and a value has either any number of & references or exactly one &mut at a time. It works at compile time and costs nothing when the program runs.",
        see=("borrowing", "lifetime", "non-lexical-lifetimes", "ownership"),
        priority=40,
        aka=("borrow check", "borrowck", "aliasing xor mutability", "borrow checking"),
        rules=(
            "Pushing to a Vec while a reference into it is still going to be used is an error: the push may move the data.",
            "Changing a Vec while looping over it with for x in &v is an error for the same reason.",
            "The check is static: a borrow conflict is refused even on a branch that never runs, such as if false { v.push(2); }.",
            "A function cannot return a reference to one of its own local variables: the local is gone when the function ends.",
        ),
        example=r"""
            let mut v = vec![1, 2, 3];
            let first = v[0];
            v.push(4);
            let last = &v[3];
            println!("{} {}", first, last);
        """,
        out=r"1 4",
    ),
    *rust(
        "lifetime",
        "Lifetime",
        "How long a reference stays valid. A name like 'a in fn longest<'a>(x: &'a str, y: &'a str) -> &'a str ties the result's life to its inputs, so the compiler can prove the result never outlives what it points to.",
        see=("reference", "borrow-checker", "non-lexical-lifetimes", "generic"),
        priority=75,
        aka=("lifetimes", "'a", "dangling reference", "dangling", "lifetime annotation", "lifetime elision", "static lifetime", "outlives"),
        detect=(r"<\s*'[a-z_]\w*\b(?!')|&\s*'[a-z_]\w*\b(?!')|:\s*'static\b",),
        rules=(
            "A function that returns a reference taken from two reference parameters needs lifetime names: fn longest(x: &str, y: &str) -> &str is an error.",
            "A reference may not outlive its owner: using r after the block that owned x ended is an error (a dangling reference).",
            "'static means 'for the whole program'; every string literal is a &'static str.",
            "With one reference parameter the output is tied to it automatically (fn first(s: &str) -> &str needs no 'a).",
            "The result of longest lives only as long as the shorter-lived argument: using it after the shorter one is dropped is an error.",
        ),
        example=r"""
            fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
                if x.len() >= y.len() { x } else { y }
            }
            fn main() {
                let a = String::from("apple");
                let b = String::from("fig");
                println!("{}", longest(&a, &b));
            }
        """,
        out=r"apple",
    ),
    *rust(
        "non-lexical-lifetimes",
        "Non-lexical lifetimes",
        "A borrow ends at its last use, not at the closing brace of its block. So you may borrow, use the reference for the last time, and then change the original in the same block.",
        see=("borrow-checker", "borrowing", "lifetime", "scope"),
        priority=40,
        aka=("nll", "borrow ends at last use", "last use", "lexical lifetime"),
        rules=(
            "let first = &v[0]; println!(\"{}\", first); v.push(4); is accepted: first is not used after the push.",
            "The same code is an error if first is read after the push, because the borrow is then still alive.",
            "A &mut borrow also ends at its last use: after r.push('a'), the owner s can be used again.",
        ),
        example=r"""
            let mut v = vec![1, 2, 3];
            let first = &v[0];
            println!("{}", first);
            v.push(4);
            println!("{:?}", v);
        """,
        out=r"""1
[1, 2, 3, 4]""",
    ),
    *rust(
        "box",
        "Box",
        "A smart pointer that puts a value on the heap and owns it. A Box<T> is the size of one pointer, which lets you store a value of unknown size, such as a recursive type or a trait object. The heap memory is freed when the Box is dropped.",
        see=("ownership", "trait-object", "dereference", "rc"),
        priority=70,
        aka=("box::new", "heap", "heap allocation", "smart pointer", "boxed", "boxing", "boxes"),
        detect=(r"\bBox::new\b|\bBox<",),
        rules=(
            "A type that contains itself needs a Box: enum List { Cons(i32, List), Nil } is an error ('infinite size'); Cons(i32, Box<List>) is fine.",
            "A Box has exactly one owner: let b = a; moves it, and a cannot be used afterwards.",
            "size_of::<Box<i32>>() is the size of a pointer (8 bytes on a 64-bit machine), whatever is inside.",
            "*b gives the value inside, and method calls look through the Box by themselves.",
        ),
        example=r"""
            enum List { Cons(i32, Box<List>), Nil }
            fn sum(l: &List) -> i32 {
                match l {
                    List::Cons(n, rest) => n + sum(rest),
                    List::Nil => 0,
                }
            }
            fn main() {
                let l = List::Cons(1, Box::new(List::Cons(2, Box::new(List::Nil))));
                println!("{} {}", sum(&l), *Box::new(5) + 1);
            }
        """,
        out=r"3 6",
    ),
    *rust(
        "rc",
        "Rc (reference counting)",
        "Rc<T> lets several owners share one value. Rc::clone adds an owner by bumping a counter, without copying the data; the value is freed when the last Rc is dropped. Arc is the thread-safe version.",
        see=("clone", "refcell", "ownership", "drop"),
        priority=75,
        aka=("rc", "reference counting", "shared ownership", "arc", "refcount", "reference count", "reference counted", "shared pointer"),
        detect=(r"\b(?:Rc|Arc)::|\b(?:Rc|Arc)<",),
        rules=(
            "Rc::clone(&a) copies only the pointer and adds one to the count; Rc::strong_count(&a) tells how many owners there are.",
            "What is inside an Rc is read-only: a.push(2) on an Rc<Vec<i32>> is an error. Put a RefCell inside to change it.",
            "Rc cannot be sent to another thread (a compile error); Arc can.",
            "Dropping one Rc lowers the count; the data is freed when it reaches zero.",
        ),
        example=r"""
            use std::rc::Rc;
            fn main() {
                let a = Rc::new(String::from("shared"));
                let b = Rc::clone(&a);
                println!("{} {}", Rc::strong_count(&a), b);
                drop(b);
                println!("{}", Rc::strong_count(&a));
            }
        """,
        out=r"""2 shared
1""",
    ),
    *rust(
        "refcell",
        "RefCell (interior mutability)",
        "RefCell<T> lets you change a value through a shared reference: the borrow rules are checked while the program runs instead of when compiling, and breaking them panics. Rc<RefCell<T>> is the usual way to share a changeable value.",
        see=("rc", "borrow-checker", "mutable-reference", "panic"),
        priority=75,
        aka=("interior mutability", "cell", "refcell", "borrow_mut", "runtime borrow checking", "mutex"),
        detect=(r"\bRefCell\b|\bCell\b|\.borrow_mut\(\)",),
        rules=(
            "borrow() gives a read guard and borrow_mut() a write guard; at any moment there may be many readers or one writer.",
            "Breaking that rule, such as two borrow_mut() guards alive at once, panics at run time; with & and &mut it would not compile.",
            "A RefCell works without let mut: let c = RefCell::new(5); *c.borrow_mut() += 1; changes it.",
            "Cell<T> is the simpler version for small Copy values, with get and set and no guards.",
            "try_borrow_mut() returns an Err instead of panicking when the cell is already borrowed.",
        ),
        example=r"""
            use std::cell::RefCell;
            use std::rc::Rc;
            fn main() {
                let shared = Rc::new(RefCell::new(vec![1]));
                let other = Rc::clone(&shared);
                other.borrow_mut().push(2);
                shared.borrow_mut().push(3);
                println!("{:?} {}", shared.borrow(), shared.borrow().len());
            }
        """,
        out=r"[1, 2, 3] 3",
    ),
    *rust(
        "drop",
        "Drop",
        "What happens when a value's owner goes out of scope: the value is freed, and if its type implements Drop, its drop method runs first. drop(x) ends a value's life early. Locals are dropped in the reverse order they were made.",
        see=("ownership", "scope", "rc", "panic"),
        priority=65,
        aka=("drop trait", "destructor", "free", "deallocate", "cleanup", "finalizer", "dropped"),
        detect=(r"\bdrop\s*\(|\bimpl\b[^{\n]{0,40}\bDrop\b",),
        rules=(
            "At the end of a scope the variables are dropped in reverse order: last made, first dropped.",
            "drop(x) moves x into the function, so x cannot be used afterwards.",
            "A value moved into a function is dropped at the end of that function, not by the caller; nothing is dropped twice.",
            "let _ = value; drops it at once, but let _x = value; keeps it until the end of the scope.",
            "A type that implements Drop cannot also be Copy.",
        ),
        example=r"""
            struct Noisy(&'static str);
            impl Drop for Noisy {
                fn drop(&mut self) {
                    println!("drop {}", self.0);
                }
            }
            fn main() {
                let _a = Noisy("a");
                let b = Noisy("b");
                drop(b);
                let _c = Noisy("c");
                println!("end");
            }
        """,
        out=r"""drop b
end
drop c
drop a""",
    ),
    *rust(
        "mem-swap",
        "mem::swap, take and replace",
        "std::mem::swap(&mut a, &mut b) exchanges two values. take(&mut x) gives you the old value and leaves the default behind; replace(&mut x, new) leaves new behind. They let you move a value out from behind a &mut.",
        see=("mutable-reference", "move", "option"),
        priority=70,
        aka=("swap", "mem::swap", "mem::take", "mem::replace", "take", "replace", "std::mem", "exchange"),
        detect=(r"\bmem::(?:swap|take|replace)\b",),
        rules=(
            "mem::swap(&mut a, &mut b) exchanges the two variables without cloning anything.",
            "mem::take leaves the type's default: an empty String or Vec, 0 for a number, None for an Option.",
            "Without them you cannot move out of a &mut: fn f(s: &mut String) -> String { *s } is an error.",
            "v.swap(i, j) exchanges two positions of a Vec or slice.",
        ),
        example=r"""
            use std::mem;
            fn main() {
                let mut a = String::from("one");
                let mut b = String::from("two");
                mem::swap(&mut a, &mut b);
                let old = mem::take(&mut a);
                let prev = mem::replace(&mut b, String::from("new"));
                println!("[{}] [{}] [{}] [{}]", a, b, old, prev);
            }
        """,
        out=r"[] [new] [two] [one]",
    ),
    *rust(
        "unsafe",
        "unsafe",
        "A block or function marked unsafe may do a few things the compiler cannot check, such as following a raw pointer or touching a static mut. It means 'I promise this is safe'; it does not turn the borrow checker off.",
        see=("reference", "borrow-checker", "constant"),
        priority=70,
        aka=("unsafe block", "raw pointer", "unsafe fn", "ffi", "unsafe rust"),
        detect=(r"\bunsafe\b",),
        rules=(
            "Following a raw pointer (*p where p is *const i32) is only allowed inside unsafe.",
            "Reading or writing a static mut is only allowed inside unsafe.",
            "Inside an unsafe block the usual rules still apply: use after move is still an error.",
        ),
        example=r"""
            let x = 5;
            let p = &x as *const i32;
            let y = unsafe { *p };
            println!("{}", y);
        """,
        out=r"5",
    ),
]
