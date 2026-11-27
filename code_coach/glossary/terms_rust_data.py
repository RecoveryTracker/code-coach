"""Rust words, part 4: text and collections - String and &str, Vec and its methods, HashMap, BTreeMap, HashSet,
BTreeSet, VecDeque, slices, ranges, iterators and their adaptors, collect, fold and sum, lazy evaluation, sorting.

Examples are the BODY of `fn main()` unless they mention `fn main(` (a `use` line needs a complete program); each is
built by rustc debug and -O by tests/test_glossary.py. A hash map or set is never printed whole (its order is random):
the examples count, look up, or use the sorted BTree versions. Every rule that a program can show is a check in
tests/glossary_rust_checks.py."""

from __future__ import annotations

from .entry import Entry, rust

TERMS: list[Entry] = [
    *rust(
        "string",
        "String and &str",
        "Text. Rust has two main kinds: String, which owns its text and can grow, and &str (a string slice), a borrowed view of text such as the literal \"hi\". Both are UTF-8, so one character may take more than one byte.",
        see=("string-from", "slice", "char", "byte", "formatting"),
        priority=45,
        aka=("str", "&str", "text", "strings", "string slice", "string literal", "string type", "str type", "utf-8 string"),
        detect=(r"\bString\b|&\s*str\b|\bstr\b",),
        rules=(
            "A literal \"hi\" is a &str; let s: String = \"hi\"; is a type error. Make a String with String::from(\"hi\") or .to_string().",
            "s1 + &s2 moves s1 into the result, so s1 cannot be used afterwards.",
            "A slice must start and end on a character boundary: &s[0..1] of a two-byte character panics.",
            "A function taking &str also accepts &String, so prefer &str for parameters.",
            "chars().rev().collect::<String>() reverses a string; a string cannot be indexed by position (s[0] is an error).",
        ),
        example=r"""
            let mut s = String::from("hello");
            s.push_str(", world");
            s.push('!');
            let part: &str = &s[0..5];
            println!("{} {} {}", s, part, s.len());
            println!("{}", s.to_uppercase());
        """,
        out=r"""hello, world! hello 13
HELLO, WORLD!""",
    ),
    *rust(
        "string-from",
        "String::from, to_string, to_owned",
        "Three ways to turn a &str into an owned String: String::from(\"hi\"), \"hi\".to_string() and \"hi\".to_owned(), all with the same result. String::new() makes an empty one.",
        see=("string", "type-conversion", "display"),
        priority=55,
        aka=("string::from", "string::new", "to_owned", "owned string", "&str to string", "str to string", "into string"),
        detect=(r"\bString::(?:from|new)\b|\.to_string\(\)|\.to_owned\(\)",),
        rules=(
            "String::from(\"hi\"), \"hi\".to_string(), \"hi\".to_owned() and \"hi\".into() all give equal Strings.",
            "String::new() is empty, with len() 0.",
            "A String can be compared with a &str using ==: String::from(\"a\") == \"a\" is true.",
            "to_string() works on anything with Display: 5.to_string() is \"5\".",
            "A &str cannot grow: let s = \"hi\"; s.push('!'); is an error because only String has push.",
        ),
        example=r"""
            let a = String::from("hi");
            let b = "hi".to_string();
            let c = "hi".to_owned();
            let d: String = "hi".into();
            println!("{}", a == b && b == c && c == d);
            println!("{:?}", String::new());
        """,
        out=r"""true
""
""",
    ),
    *rust(
        "vector",
        "Vector (Vec)",
        "A growable list of items of one type, Vec<T>, stored on the heap. Make one with vec![1, 2, 3] or Vec::new(); items are reached by position starting at 0.",
        see=("vec-methods", "array", "slice", "iterator", "collection"),
        priority=55,
        aka=("vec", "list", "array list", "dynamic array", "vectors", "growable array", "arraylist", "vec<t>"),
        detect=(r"\bVec\b|\bvec!",),
        rules=(
            "All items have the same type: vec![1, \"a\"] is an error.",
            "Positions start at 0: v[len] panics, while v.get(len) gives None.",
            "push needs the Vec to be declared let mut.",
            "A Vec owns its items and moves like any owner: let w = v; leaves v unusable.",
            "vec![0; 3] makes three zeros.",
        ),
        example=r"""
            let mut v = vec![10, 20, 30];
            v.push(40);
            let last = v.pop();
            println!("{:?} {:?} {} {}", v, last, v[1], v.len());
        """,
        out=r"[10, 20, 30] Some(40) 20 3",
    ),
    *rust(
        "vec-methods",
        "Vec methods",
        "The everyday things a Vec can do: push and pop at the end, insert and remove at a position, len and is_empty, contains, retain to keep only some items, extend to add many, and truncate or clear to cut.",
        see=("vector", "slice", "sorting", "iterator"),
        priority=45,
        aka=("push", "pop", "insert", "remove", "len", "is_empty", "retain", "extend", "truncate", "drain", "contains", "dedup", "clear"),
        detect=(r"\.(?:push|pop|insert|remove|retain|extend|truncate|drain|dedup|contains|is_empty|clear|append|swap_remove)\(",),
        rules=(
            "push adds at the end; pop removes the last item and returns it as an Option (None when empty).",
            "insert(i, x) and remove(i) shift the later items, and an i past the end panics.",
            "retain(|x| keep) keeps the items for which the closure says true.",
            "contains takes a reference: v.contains(&7), not v.contains(7).",
            "dedup removes only neighbouring duplicates: [1, 1, 2, 1] becomes [1, 2, 1]. truncate(n) keeps the first n.",
        ),
        example=r"""
            let mut v = vec![1, 2, 3, 4, 5, 6];
            v.insert(0, 9);
            let removed = v.remove(1);
            v.retain(|x| x % 2 == 0);
            v.extend([7, 8]);
            println!("{:?} {} {}", v, removed, v.contains(&7));
        """,
        out=r"[2, 4, 6, 7, 8] 1 true",
    ),
    *rust(
        "hashmap",
        "HashMap",
        "A collection of key-value pairs with fast lookup by key: HashMap<K, V> from std::collections. Keys are unique. The order of iteration is not defined, so never rely on it.",
        see=("btreemap", "hashset", "option", "partial-eq"),
        priority=70,
        aka=("map", "dictionary", "dict", "hash map", "hash table", "hashmaps", "associative array", "lookup table"),
        detect=(r"\bHashMap\b",),
        rules=(
            "insert on an existing key replaces the value and returns the old one as Some(old).",
            "get(&key) returns an Option; m[&key] panics when the key is missing.",
            "*m.entry(k).or_insert(0) += 1; is the usual way to count: it adds the key with 0 only if it is absent.",
            "The iteration order is not defined: to print in a fixed order, collect the keys and sort them (or use a BTreeMap).",
            "insert moves a String key in: the original variable cannot be used afterwards.",
        ),
        example=r"""
            use std::collections::HashMap;
            fn main() {
                let mut stock: HashMap<&str, i32> = HashMap::new();
                stock.insert("apple", 3);
                stock.insert("apple", 5);
                *stock.entry("pear").or_insert(0) += 2;
                println!("{:?} {:?} {}", stock.get("apple"), stock.get("kiwi"), stock.len());
            }
        """,
        out=r"Some(5) None 2",
    ),
    *rust(
        "btreemap",
        "BTreeMap",
        "Like a HashMap but kept sorted by key, so iterating gives the keys in order every time and printing it is predictable. It can also give the first or last key and a range of keys.",
        see=("hashmap", "btreeset", "partial-ord"),
        priority=70,
        aka=("btree", "sorted map", "ordered map", "treemap", "tree map", "btree map"),
        detect=(r"\bBTreeMap\b",),
        rules=(
            "Iterating or printing goes in key order, whatever order you inserted in.",
            "Keys need Ord, so an f64 cannot be a key.",
            "range(2..) walks the keys from 2 upwards; first_key_value() and last_key_value() give the ends.",
            "It has the same insert, get, entry and remove as HashMap.",
        ),
        example=r"""
            use std::collections::BTreeMap;
            fn main() {
                let mut m = BTreeMap::new();
                m.insert(3, "c");
                m.insert(1, "a");
                m.insert(2, "b");
                println!("{:?}", m);
                println!("{:?} {:?}", m.first_key_value(), m.range(2..).count());
            }
        """,
        out=r"""{1: "a", 2: "b", 3: "c"}
Some((1, "a")) 2""",
    ),
    *rust(
        "hashset",
        "HashSet",
        "A collection of unique values with fast contains: HashSet<T>. Adding a value that is already there changes nothing. Its order is not defined, and it offers union, intersection and difference.",
        see=("btreeset", "hashmap", "collect", "partial-eq"),
        priority=70,
        aka=("set", "sets", "hash set", "unique", "distinct", "set operations", "intersection"),
        detect=(r"\bHashSet\b",),
        rules=(
            "insert returns true when the value was new and false when it was already there.",
            "Duplicates collapse: len() counts unique values only.",
            "a.intersection(&b) and a.union(&b) give the shared values and all values.",
            "The iteration order is not defined; sort before printing, or use a BTreeSet.",
        ),
        example=r"""
            use std::collections::HashSet;
            fn main() {
                let mut seen = HashSet::new();
                let added: Vec<bool> = [3, 1, 3, 2, 1].iter().map(|n| seen.insert(*n)).collect();
                println!("{:?} {}", added, seen.len());
                println!("{}", seen.contains(&2));
            }
        """,
        out=r"""[true, true, false, true, false] 3
true""",
    ),
    *rust(
        "btreeset",
        "BTreeSet",
        "Like a HashSet but sorted: iterating gives the values in order, and you can ask for the first, the last and a range.",
        see=("hashset", "btreemap", "partial-ord"),
        priority=70,
        aka=("sorted set", "ordered set", "treeset", "tree set", "btree set"),
        detect=(r"\bBTreeSet\b",),
        rules=(
            "Values are unique and always come out in sorted order, so printing a BTreeSet is stable.",
            "first() and last() give the smallest and largest as Options; range(2..) walks from 2 upwards.",
            "Values need Ord: a BTreeSet of f64 does not compile.",
        ),
        example=r"""
            use std::collections::BTreeSet;
            fn main() {
                let s: BTreeSet<i32> = [5, 1, 3, 1].into_iter().collect();
                println!("{:?} {:?} {:?}", s, s.first(), s.last());
                println!("{:?}", s.range(2..).collect::<Vec<_>>());
            }
        """,
        out=r"""{1, 3, 5} Some(1) Some(5)
[3, 5]""",
    ),
    *rust(
        "deque",
        "VecDeque",
        "A queue you can add to and take from at both ends quickly: push_back, push_front, pop_front, pop_back. A Vec is slow at the front; a VecDeque is the tool for first-in, first-out.",
        see=("vector", "collection", "while-let"),
        priority=70,
        aka=("vecdeque", "queue", "double-ended queue", "double ended queue", "ring buffer", "fifo", "stack and queue"),
        detect=(r"\bVecDeque\b",),
        rules=(
            "push_back then pop_front gives the items in the order they went in (first in, first out).",
            "It prints like a list, [1, 2], and q[i] reads by position.",
            "pop_front and pop_back return an Option, None when empty.",
            "VecDeque::from(vec![...]) and Vec::from(deque) convert both ways.",
        ),
        example=r"""
            use std::collections::VecDeque;
            fn main() {
                let mut q = VecDeque::new();
                q.push_back(1);
                q.push_back(2);
                q.push_front(0);
                println!("{:?} {:?} {:?}", q.pop_front(), q.pop_back(), q);
            }
        """,
        out=r"Some(0) Some(2) [1]",
    ),
    *rust(
        "slice",
        "Slice",
        "A view of part of an array, Vec or String: &v[1..3] or &s[..2]. A slice is borrowed (&[T] or &str), knows its length, owns nothing and cannot change the size of what it views.",
        see=("range", "array", "vector", "string"),
        priority=55,
        aka=("slices", "subarray", "substring", "sub-slice", "slicing", "view"),
        detect=(r"&\s*\w+\s*\[[^\]\n]{0,20}\.\.|&\s*(?:mut\s+)?\[[A-Za-z]",),
        rules=(
            "&v[a..b] leaves out b, &v[..b] starts at 0 and &v[a..] runs to the end.",
            "A range past the end panics: &v[1..n] with n bigger than v.len() is an index error.",
            "A slice borrows the owner: pushing to the Vec while the slice is still used later is a compile error.",
            "A parameter of type &[i32] accepts a &Vec<i32> and an &[i32; 3] alike.",
            "chunks(2) splits into pieces of two (the last may be shorter) and windows(2) slides over neighbours.",
        ),
        example=r"""
            let v = vec![10, 20, 30, 40, 50];
            let mid = &v[1..4];
            println!("{:?} {} {:?}", mid, mid.len(), &v[..2]);
            println!("{:?} {:?}", mid.first(), &v[3..]);
            let s = "hello world";
            println!("{}", &s[6..]);
        """,
        out=r"""[20, 30, 40] 3 [10, 20]
Some(20) [40, 50]
world""",
    ),
    *rust(
        "range",
        "Range",
        "A span of numbers written start..end (end left out) or start..=end (end included). Ranges drive for loops and slicing, and they are iterators: (1..4).sum() is 6, and (0..10).step_by(5) gives 0 and 5.",
        see=("for-loop", "slice", "iterator", "adaptor"),
        priority=50,
        aka=("ranges", "..", "..=", "range expression", "inclusive range", "step_by", "exclusive range"),
        detect=(r"\bin\s+[\w(]{1,20}\s*\.\.=?|\(\s*\w+\s*\.\.=?\s*\w|\b\d+\s*\.\.=?",),
        rules=(
            "start..end leaves out end and start..=end includes it: 1..4 is 1, 2, 3 and 1..=4 is 1, 2, 3, 4.",
            "1..1 is empty, and a backwards range such as 5..1 is empty too, not counting down; use (1..5).rev().",
            "Ranges of characters work: ('a'..='e').collect::<String>() is \"abcde\".",
            "step_by(n) takes every nth item: (0..10).step_by(5) gives 0 and 5.",
            "contains(&x) tests membership: (1..4).contains(&4) is false.",
        ),
        example=r"""
            let a: Vec<i32> = (1..4).collect();
            let b: Vec<i32> = (1..=4).collect();
            let c: Vec<i32> = (0..10).step_by(5).collect();
            println!("{:?} {:?} {:?}", a, b, c);
            println!("{} {}", (1..4).contains(&4), (1..=4).contains(&4));
        """,
        out=r"""[1, 2, 3] [1, 2, 3, 4] [0, 5]
false true""",
    ),
    *rust(
        "iterator",
        "Iterator",
        "Something that hands out items one at a time with .next(), which gives Some(item) and then None at the end. Vecs, ranges and strings can make one with .iter(), .into_iter() or .chars(). A for loop uses one.",
        see=("adaptor", "lazy-evaluation", "collect", "for-loop"),
        priority=55,
        aka=("iterators", "iter", "iter()", "into_iter", "iter_mut", "next", "iterable", "iterate", "stream"),
        detect=(r"\.(?:iter|into_iter|iter_mut)\(\)|\bIterator\b",),
        rules=(
            ".iter() borrows the items (&T), .iter_mut() lends them for changing (&mut T) and .into_iter() on a Vec moves them out, using the Vec up.",
            "Calling next() needs the iterator to be let mut.",
            "A for loop calls next() until it gives None; while let Some(x) = it.next() does the same by hand.",
            "Everything that consumes an iterator (sum, count, collect) takes it by value, so it can only be used once.",
        ),
        example=r"""
            let v = vec![10, 20];
            let mut it = v.iter();
            println!("{:?} {:?} {:?}", it.next(), it.next(), it.next());
            let total: i32 = v.iter().sum();
            println!("{}", total);
        """,
        out=r"""Some(10) Some(20) None
30""",
    ),
    *rust(
        "adaptor",
        "Iterator adaptors (map, filter, zip)",
        "Methods that turn one iterator into another: map changes each item, filter keeps some, zip pairs two iterators, enumerate adds positions, skip, take, rev and chain reshape. They do nothing until something consumes the result.",
        see=("iterator", "closure", "collect", "lazy-evaluation"),
        priority=60,
        aka=("map method", "filter", "zip", "enumerate", "iterator adapter", "adapter", "skip", "chain", "rev", "flat_map", "filter_map", "windows"),
        detect=(r"\.(?:map|filter|zip|enumerate|skip|take|chain|rev|flat_map|filter_map|take_while|skip_while|windows|chunks|peekable|cloned|copied)\(",),
        rules=(
            "filter(|x| test) keeps the items for which the closure says true; map(|x| ...) replaces each item with the closure's result.",
            "zip stops at the shorter side, enumerate counts from 0, and skip(2).take(3) of 1..10 gives 3, 4, 5.",
            "filter_map keeps only the Some results: parsing [\"1\", \"x\", \"3\"] gives [1, 3].",
            "windows(2) looks at each pair of neighbours: [1, 3, 6] gives the gaps [2, 3].",
            "Building a chain prints and computes nothing until a consumer such as collect runs it.",
        ),
        example=r"""
            let v = vec![1, 2, 3, 4, 5, 6];
            let out: Vec<i32> = v.iter().filter(|x| *x % 2 == 0).map(|x| x * 10).collect();
            println!("{:?}", out);
            let pairs: Vec<(usize, char)> = "abc".chars().enumerate().collect();
            println!("{:?}", pairs);
            let sums: Vec<i32> = [1, 2, 3].iter().zip([10, 20, 30].iter()).map(|(a, b)| a + b).collect();
            println!("{:?}", sums);
        """,
        out=r"""[20, 40, 60]
[(0, 'a'), (1, 'b'), (2, 'c')]
[11, 22, 33]""",
    ),
    *rust(
        "collect",
        "collect",
        "Eats an iterator and builds a collection from it: a Vec, a String, a HashMap, a HashSet, even a Result<Vec<_>, _>. What it builds is decided by the type you ask for, so you must name it with a let type or a turbofish.",
        see=("iterator", "turbofish", "vector", "result"),
        priority=65,
        aka=("collect()", "to_vec", "into collection", "build vec", "gather"),
        detect=(r"\.collect\b",),
        rules=(
            "collect() with no type named is an error: write let v: Vec<_> = ... or collect::<Vec<_>>().",
            "Collecting into Result<Vec<_>, _> stops at the first Err and gives it; into Option<Vec<_>> it gives None if any item is None.",
            "Collecting chars gives a String when the type is String.",
            "Collecting into a HashSet drops duplicates, and into a HashMap needs (key, value) pairs.",
        ),
        example=r"""
            let squares: Vec<u32> = (1..=4).map(|n| n * n).collect();
            let word: String = vec!['r', 'u', 's', 't'].into_iter().collect();
            let parsed: Result<Vec<i32>, _> = "1 2 3".split(' ').map(|s| s.parse::<i32>()).collect();
            println!("{:?} {} {:?}", squares, word, parsed);
        """,
        out=r"[1, 4, 9, 16] rust Ok([1, 2, 3])",
    ),
    *rust(
        "fold",
        "fold, sum and product",
        "fold(start, |acc, x| ...) walks the items, carrying a running value. sum() and product() are the common cases, and reduce is a fold that starts from the first item and gives an Option.",
        see=("iterator", "closure", "collect", "option"),
        priority=60,
        aka=("sum", "reduce", "product", "accumulate", "aggregate", "fold()", "running total", "inject"),
        detect=(r"\.(?:fold|sum|product|reduce)\b",),
        rules=(
            "sum() and product() need the result type: let s: i32 = v.iter().sum(); without a type is an error.",
            "fold's first argument is the starting value, and its type is the result's type: fold(0.0, ...) gives a float.",
            "An empty iterator sums to 0 and multiplies to 1.",
            "reduce gives None for an empty iterator and Some(result) otherwise.",
        ),
        example=r"""
            let v = vec![1, 2, 3, 4];
            let total = v.iter().fold(0, |acc, x| acc + x);
            let sum: i32 = v.iter().sum();
            let product: i32 = v.iter().product();
            let text = v.iter().fold(String::new(), |acc, x| acc + &x.to_string());
            println!("{} {} {} {}", total, sum, product, text);
        """,
        out=r"10 10 24 1234",
    ),
    *rust(
        "lazy-evaluation",
        "Lazy evaluation",
        "Iterator adaptors such as map and filter only describe work; nothing runs until a consumer like collect, sum, count or a for loop pulls the items through. Items are made one at a time, only as far as needed.",
        see=("iterator", "adaptor", "collect", "closure"),
        priority=40,
        aka=("lazy", "laziness", "lazy iterator", "deferred", "consumer", "consuming adaptor", "lazy evaluation"),
        rules=(
            "Building v.iter().map(|x| println!(\"{}\", x)) and never consuming it prints nothing.",
            "Consumers that can stop early (find, next, take) pull only as many items as they need.",
            "An endless range is fine because of laziness: (1..).take(3) gives 1, 2, 3.",
            "A consuming call takes the iterator by value, so a second use of it is a compile error.",
        ),
        example=r"""
            let v = vec![1, 2, 3, 4];
            let pipeline = v.iter().map(|x| {
                println!("map {}", x);
                x * 2
            });
            println!("built");
            let first_big = pipeline.filter(|x| *x > 2).next();
            println!("{:?}", first_big);
        """,
        out=r"""built
map 1
map 2
Some(4)""",
    ),
    *rust(
        "sorting",
        "Sorting",
        "v.sort() puts a Vec in order, in place. sort_by takes a comparison function, sort_by_key a key function, and reverse flips. They change the Vec itself and return nothing, and the items must be Ord (floats need sort_by with partial_cmp).",
        see=("partial-ord", "vector", "closure", "floating-point"),
        priority=60,
        aka=("sort", "sorted", "sort_by", "sort_by_key", "sort_unstable", "key function", "reverse sort", "ascending", "descending"),
        detect=(r"\.(?:sort|sort_by|sort_by_key|sort_unstable|sort_unstable_by|sort_unstable_by_key|reverse)\(",),
        rules=(
            "sort() works in place and returns (): let r = v.sort(); makes r the unit value, not a sorted copy. There is no sorted().",
            "The Vec must be mut: sort() on a plain let is an error.",
            "The sort is stable: items with equal keys keep their original order.",
            "A Vec<f64> cannot sort(): use v.sort_by(|a, b| a.partial_cmp(b).unwrap()).",
            "Descending order: sort_by(|a, b| b.cmp(a)) or sort_by_key(|x| Reverse(*x)).",
        ),
        example=r"""
            let mut v = vec![3, 1, 2];
            v.sort();
            println!("{:?}", v);
            v.sort_by(|a, b| b.cmp(a));
            println!("{:?}", v);
            let mut words = vec!["pear", "fig", "apple"];
            words.sort_by_key(|w| w.len());
            println!("{:?}", words);
        """,
        out=r"""[1, 2, 3]
[3, 2, 1]
["fig", "pear", "apple"]""",
    ),
    *rust(
        "collection",
        "Collection",
        "A value that holds many values. The standard ones are Vec (a list), VecDeque (a queue), HashMap and BTreeMap (key to value), HashSet and BTreeSet (unique values), plus arrays and slices. Pick one by how you will use it.",
        see=("vector", "hashmap", "hashset", "deque"),
        priority=35,
        aka=("collections", "container", "data structure", "std::collections", "containers"),
        rules=(
            "Every collection has len() and is_empty() and can be looped over with for.",
            "A Vec keeps duplicates and a set drops them: collecting [3, 1, 3] gives 3 items in a Vec and 2 in a set.",
            "Hash collections have no defined order; Vec, VecDeque and the BTree collections do.",
            "A collection owns what you put in: after vec![s], the String s has moved and cannot be used.",
        ),
        example=r"""
            use std::collections::{BTreeMap, BTreeSet, VecDeque};
            fn main() {
                let list = vec![3, 1, 3];
                let set: BTreeSet<i32> = list.iter().cloned().collect();
                let mut map = BTreeMap::new();
                for x in &list { *map.entry(*x).or_insert(0) += 1; }
                let queue: VecDeque<i32> = list.into_iter().collect();
                println!("{:?} {:?} {:?}", set, map, queue);
            }
        """,
        out=r"{1, 3} {1: 1, 3: 2} [3, 1, 3]",
    ),
]
