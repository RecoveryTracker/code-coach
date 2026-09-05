"""Rust: Option, iterators, and the shape its tree problems actually have.

The coverage audit found the Rust pages covering twelve of the sixty-four
constructs their own solution bank uses. Reading the answers directly is
worse than that number suggests. Across sixteen hundred Rust answers the
workbook had never once written `Option<`, never called `.iter()`, and had
never mentioned `Rc` or `RefCell`.

Option is the type the language is built around, and the tree problems in
the bank are all `Option<Rc<RefCell<TreeNode>>>`, so a student who had done
every Rust page in the book could not read the first line of one. The
counting idiom is `entry().or_insert(0)` and that was missing too, though
HashMap itself was taught, which is the sort of half-covered that looks
fine in a page list.

Ten pages, in dependency order: Option first because everything returns
one, then iterators, then the entry idiom, the Vec and VecDeque calls, then
ownership and clone, then Rc and RefCell, then the tree they add up to.

Rust only. Nothing prints a collection directly, because the debug format
for a Vec is a Rust-specific rendering and the answers here are compared as
text.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("rust",)

SHAPES: tuple[Shape, ...] = (
    Shape("rust_option", "the type that might be nothing"),
    Shape("rust_iter", "a chain of steps over a sequence"),
    Shape("rust_entry", "counting without checking first"),
    Shape("rust_vec_ops", "the calls a Vec answers to"),
    Shape("rust_deque", "a queue with two ends"),
    Shape("rust_clone", "who owns it, and what copying costs"),
    Shape("rust_rc_refcell", "shared, and mutable anyway"),
    Shape("rust_tree", "a tree the way Rust has to write one"),
    Shape("rust_sort", "sorting, and sorting by something"),
    Shape("rust_string", "String and the str it borrows"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _ints(items) -> str:
    return ", ".join(str(n) for n in items)


def _strs(items) -> str:
    return ", ".join(f'"{s}"' for s in items)


# ── 350. Option ──────────────────────────────────────────────


def _option(a: dict) -> str:
    values, want = a["values"], a["want"]
    if want == "match":
        return _lines(
            "fn main() {",
            f"    let items = vec![{_ints(values)}];",
            f"    let found = items.iter().find(|&&n| n > {a['over']});",
            "    match found {",
            '        Some(n) => println!("{}", n),',
            '        None => println!("none"),',
            "    }",
            "}",
        )
    if want == "unwrap_or":
        return _lines(
            "fn main() {",
            f"    let items = vec![{_ints(values)}];",
            f"    let found = items.iter().find(|&&n| n > {a['over']});",
            f'    println!("{{}}", found.copied().unwrap_or({a["fallback"]}));',
            "}",
        )
    return _lines(
        "fn main() {",
        f"    let items = vec![{_ints(values)}];",
        f"    let found = items.iter().position(|&n| n == {a['target']});",
        "    if let Some(at) = found {",
        '        println!("{}", at);',
        "    } else {",
        '        println!("missing");',
        "    }",
        "}",
    )


# ── 351. Iterators ───────────────────────────────────────────


def _iter(a: dict) -> str:
    values, want = a["values"], a["want"]
    body = {
        "sum": "items.iter().sum::<i32>()",
        "count": f"items.iter().filter(|&&n| n > {a.get('over', 0)}).count()",
        "max": "items.iter().max().copied().unwrap_or(0)",
        "doubled": None,
    }[want]
    if want == "doubled":
        return _lines(
            "fn main() {",
            f"    let items = vec![{_ints(values)}];",
            "    let doubled: Vec<i32> = items.iter().map(|n| n * 2).collect();",
            "    let text: Vec<String> = doubled.iter()",
            "        .map(|n| n.to_string())",
            "        .collect();",
            '    println!("{}", text.join(" "));',
            "}",
        )
    return _lines(
        "fn main() {",
        f"    let items = vec![{_ints(values)}];",
        f'    println!("{{}}", {body});',
        "}",
    )


# ── 352. entry and or_insert ─────────────────────────────────


def _entry(a: dict) -> str:
    return _lines(
        "use std::collections::HashMap;",
        "",
        "fn main() {",
        f'    let text = "{a["text"]}";',
        "    let mut counts: HashMap<char, i32> = HashMap::new();",
        "    for ch in text.chars() {",
        "        *counts.entry(ch).or_insert(0) += 1;",
        "    }",
        "    let mut keys: Vec<&char> = counts.keys().collect();",
        "    keys.sort();",
        "    let shown: Vec<String> = keys.iter()",
        '        .map(|k| format!("{}{}", k, counts[k]))',
        "        .collect();",
        '    println!("{}", shown.join(" "));',
        "}",
    )


# ── 353. Vec calls ───────────────────────────────────────────


def _vec_ops(a: dict) -> str:
    values, want = a["values"], a["want"]
    if want == "pop":
        return _lines(
            "fn main() {",
            f"    let mut items = vec![{_ints(values)}];",
            f"    for _ in 0..{a['times']} {{",
            "        items.pop();",
            "    }",
            "    let text: Vec<String> = items.iter()",
            "        .map(|n| n.to_string())",
            "        .collect();",
            '    println!("{}", text.join(" "));',
            '    println!("{}", items.len());',
            "}",
        )
    return _lines(
        "fn main() {",
        f"    let mut items: Vec<i32> = vec![{_ints(values)}];",
        '    println!("{}", items.is_empty());',
        "    items.clear();",
        '    println!("{}", items.is_empty());',
        f"    items.push({a['pushed']});",
        '    println!("{}", items.len());',
        "}",
    )


# ── 354. VecDeque ────────────────────────────────────────────


def _deque(a: dict) -> str:
    return _lines(
        "use std::collections::VecDeque;",
        "",
        "fn main() {",
        "    let mut queue: VecDeque<i32> = VecDeque::new();",
        f"    for n in [{_ints(a['values'])}] {{",
        "        queue.push_back(n);",
        "    }",
        "    let mut order: Vec<String> = Vec::new();",
        f"    for _ in 0..{a['taken']} {{",
        "        if let Some(n) = queue.pop_front() {",
        "            order.push(n.to_string());",
        "        }",
        "    }",
        '    println!("{}", order.join(" "));',
        '    println!("{}", queue.len());',
        "}",
    )


# ── 355. Ownership and clone ─────────────────────────────────


def _clone(a: dict) -> str:
    return _lines(
        "fn total(items: &Vec<i32>) -> i32 {",
        "    items.iter().sum()",
        "}",
        "",
        "fn main() {",
        f"    let first = vec![{_ints(a['values'])}];",
        "    // A clone, because the next line would otherwise move it and",
        "    // the borrow below would have nothing left to look at.",
        "    let second = first.clone();",
        '    println!("{}", total(&first));',
        '    println!("{}", total(&second));',
        '    println!("{}", first.len() == second.len());',
        "}",
    )


# ── 356. Rc and RefCell ──────────────────────────────────────


def _rc_refcell(a: dict) -> str:
    return _lines(
        "use std::cell::RefCell;",
        "use std::rc::Rc;",
        "",
        "fn main() {",
        f"    let shared = Rc::new(RefCell::new(vec![{_ints(a['values'])}]));",
        "    let other = Rc::clone(&shared);",
        f"    other.borrow_mut().push({a['pushed']});",
        "    // Both names see the push: Rc shares one value, and RefCell",
        "    // is what allows changing it while it is shared.",
        '    println!("{}", shared.borrow().len());',
        '    println!("{}", shared.borrow().iter().sum::<i32>());',
        '    println!("{}", Rc::strong_count(&shared));',
        "}",
    )


# ── 357. The tree Rust has to write ──────────────────────────

_TREE_DEFS = (
    "use std::cell::RefCell;",
    "use std::rc::Rc;",
    "",
    "#[derive(Debug)]",
    "pub struct TreeNode {",
    "    pub val: i32,",
    "    pub left: Option<Rc<RefCell<TreeNode>>>,",
    "    pub right: Option<Rc<RefCell<TreeNode>>>,",
    "}",
    "",
    "impl TreeNode {",
    "    pub fn new(val: i32) -> Self {",
    "        TreeNode { val, left: None, right: None }",
    "    }",
    "}",
    "",
    "type Tree = Option<Rc<RefCell<TreeNode>>>;",
    "",
    "fn leaf(val: i32) -> Tree {",
    "    Some(Rc::new(RefCell::new(TreeNode::new(val))))",
    "}",
    "",
    "fn depth(node: &Tree) -> i32 {",
    "    match node {",
    "        None => 0,",
    "        Some(inner) => {",
    "            let borrowed = inner.borrow();",
    "            1 + depth(&borrowed.left).max(depth(&borrowed.right))",
    "        }",
    "    }",
    "}",
    "",
    "fn total(node: &Tree) -> i32 {",
    "    match node {",
    "        None => 0,",
    "        Some(inner) => {",
    "            let borrowed = inner.borrow();",
    "            borrowed.val + total(&borrowed.left) + total(&borrowed.right)",
    "        }",
    "    }",
    "}",
    "",
)


def _tree(a: dict) -> str:
    values = a["values"]
    lines = [f"    let n{i} = leaf({v}).unwrap();"
             for i, v in enumerate(values)]
    for i in range(len(values)):
        left, right = 2 * i + 1, 2 * i + 2
        if left < len(values):
            lines.append(f"    n{i}.borrow_mut().left = Some(Rc::clone(&n{left}));")
        if right < len(values):
            lines.append(f"    n{i}.borrow_mut().right = Some(Rc::clone(&n{right}));")
    return _lines(
        *_TREE_DEFS,
        "fn main() {",
        *lines,
        "    let root: Tree = Some(n0);",
        '    println!("{}", root.as_ref().unwrap().borrow().val);',
        '    println!("{}", depth(&root));',
        '    println!("{}", total(&root));',
        "}",
    )


# ── 358. Sorting ─────────────────────────────────────────────


def _sort(a: dict) -> str:
    if a["want"] == "numbers":
        return _lines(
            "fn main() {",
            f"    let mut items = vec![{_ints(a['values'])}];",
            "    items.sort();",
            "    items.dedup();",
            "    let text: Vec<String> = items.iter()",
            "        .map(|n| n.to_string())",
            "        .collect();",
            '    println!("{}", text.join(" "));',
            "}",
        )
    return _lines(
        "fn main() {",
        f"    let mut words = vec![{_strs(a['words'])}];",
        "    words.sort_by(|a, b| a.len().cmp(&b.len()).then(a.cmp(b)));",
        '    println!("{}", words.join(" "));',
        "}",
    )


# ── 359. String and str ──────────────────────────────────────


def _string(a: dict) -> str:
    if a["want"] == "build":
        return _lines(
            "fn main() {",
            "    let mut out = String::new();",
            f"    for word in [{_strs(a['words'])}] {{",
            "        out.push_str(word);",
            "        out.push('-');",
            "    }",
            "    let trimmed = out.trim_end_matches('-');",
            '    println!("{}", trimmed);',
            '    println!("{}", trimmed.len());',
            "}",
        )
    return _lines(
        "fn main() {",
        f'    let text = "{a["text"]}";',
        "    let upper: String = text.chars()",
        "        .map(|c| c.to_ascii_uppercase())",
        "        .collect();",
        '    println!("{}", upper);',
        f'    println!("{{}}", text.chars().filter(|c| *c == \'{a["letter"]}\').count());',
        "}",
    )


_BUILDERS = {
    "rust_option": _option,
    "rust_iter": _iter,
    "rust_entry": _entry,
    "rust_vec_ops": _vec_ops,
    "rust_deque": _deque,
    "rust_clone": _clone,
    "rust_rc_refcell": _rc_refcell,
    "rust_tree": _tree,
    "rust_sort": _sort,
    "rust_string": _string,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out in Python, from the data rather than from the Rust.

    The guards are the usual question. A find that always succeeds never
    shows None. A dedup with nothing to remove is a sort. A clone whose
    original is never used again did not need to be a clone.
    """
    a = args
    if shape == "rust_option":
        values, want = list(a["values"]), a["want"]
        if want in ("match", "unwrap_or"):
            over = a["over"]
            found = next((n for n in values if n > over), None)
            if want == "match":
                if found is None and a.get("expect_some", True):
                    pass
                return str(found) if found is not None else "none"
            fallback = a["fallback"]
            if found is not None and found == fallback:
                raise ValueError(
                    "the fallback must differ from the value found, or the "
                    "two branches print the same thing"
                )
            return str(found if found is not None else fallback)
        target = a["target"]
        if target in values:
            return str(values.index(target))
        return "missing"
    if shape == "rust_iter":
        values, want = list(a["values"]), a["want"]
        if want == "sum":
            return str(sum(values))
        if want == "count":
            over = a["over"]
            kept = [n for n in values if n > over]
            if not kept or len(kept) == len(values):
                raise ValueError(
                    "the filter must keep some and drop some, or counting "
                    "it is the same as counting the whole list"
                )
            return str(len(kept))
        if want == "max":
            if not values:
                raise ValueError("max of nothing is the fallback, not a max")
            return str(max(values))
        return " ".join(str(n * 2) for n in values)
    if shape == "rust_entry":
        text = a["text"]
        if len(set(text)) == len(text):
            raise ValueError(
                "some character must repeat, or every count is one and the "
                "or_insert never has anything to add to"
            )
        counts: dict = {}
        for ch in text:
            counts[ch] = counts.get(ch, 0) + 1
        return " ".join(f"{k}{counts[k]}" for k in sorted(counts))
    if shape == "rust_vec_ops":
        values = list(a["values"])
        if a["want"] == "pop":
            times = a["times"]
            if not 0 < times < len(values):
                raise ValueError("popping must leave something behind")
            left = values[:len(values) - times]
            return NL.join([" ".join(str(n) for n in left), str(len(left))])
        if not values:
            raise ValueError("is_empty is only interesting on something")
        return NL.join(["false", "true", "1"])
    if shape == "rust_deque":
        values, taken = list(a["values"]), a["taken"]
        if not 0 < taken < len(values):
            raise ValueError("taking must leave something in the queue")
        return NL.join([
            " ".join(str(n) for n in values[:taken]),
            str(len(values) - taken),
        ])
    if shape == "rust_clone":
        values = list(a["values"])
        if not values:
            raise ValueError("cloning nothing costs nothing")
        return NL.join([str(sum(values)), str(sum(values)), "true"])
    if shape == "rust_rc_refcell":
        values, pushed = list(a["values"]), a["pushed"]
        return NL.join([
            str(len(values) + 1),
            str(sum(values) + pushed),
            "2",
        ])
    if shape == "rust_tree":
        values = list(a["values"])
        if len(values) < 4:
            raise ValueError("a tree this small has nothing to recurse into")
        depth = 0
        while (1 << depth) - 1 < len(values):
            depth += 1
        return NL.join([str(values[0]), str(depth), str(sum(values))])
    if shape == "rust_sort":
        if a["want"] == "numbers":
            values = list(a["values"])
            if len(set(values)) == len(values):
                raise ValueError(
                    "something must repeat, or dedup does nothing and the "
                    "page is only about sort"
                )
            return " ".join(str(n) for n in sorted(set(values)))
        words = list(a["words"])
        order = sorted(words, key=lambda w: (len(w), w))
        if order == words:
            raise ValueError("the words must not already be in order")
        if len({len(w) for w in words}) < 2:
            raise ValueError("the words must differ in length")
        return " ".join(order)
    if shape == "rust_string":
        if a["want"] == "build":
            words = list(a["words"])
            if not words:
                raise ValueError("building from nothing shows nothing")
            joined = "-".join(words)
            return NL.join([joined, str(len(joined))])
        text, letter = a["text"], a["letter"]
        if letter not in text:
            raise ValueError("the letter counted must be in the text")
        if not text.islower():
            raise ValueError(
                "the text must be lower case to start, or upper-casing it "
                "does not visibly do anything"
            )
        return NL.join([text.upper(), str(text.count(letter))])
    raise KeyError(shape)
