"""Pages 350-359: Rust, starting with the type it is built around.

Sixteen hundred Rust answers in this workbook and not one of them contained
the word Option. None called .iter(). None mentioned Rc or RefCell, which
is the shape every tree problem in the Rust bank is written in, so the
pages could all be done and the first line of one still be unreadable.

Ten pages in dependency order. Option first, because nearly everything in
Rust that might not find something returns one. Then iterators, then the
entry idiom that replaces looking a key up before you change it, then the
Vec and VecDeque calls the solutions lean on, then ownership and what a
clone is actually for. Rc and RefCell after that, and then the tree, which
is those two ideas plus Option all at once and is why it comes last.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

RUST_ONLY = ("rust",)


def _page(page_id, number, name, teaches, example, shape, rows) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(
            Exercise(
                id=f"{page_id}-{i + 1:02d}",
                prompt=prompt,
                shape=shape,
                args=args,
            )
            for i, (prompt, args) in enumerate(rows)
        ),
        languages=RUST_ONLY,
        tier="advanced",
    )


def _seq(items) -> str:
    return ", ".join(str(n) for n in items)


def _wordlist(items) -> str:
    return ", ".join(f'"{w}"' for w in items)


# ── 350. Option ──────────────────────────────────────────────
#
# Both branches turn up on this page on purpose: some rows find nothing,
# so None is a thing you have watched happen rather than read about.

_MATCHES = (
    ((3, 9, 2), 5), ((1, 2, 3), 9), ((7, 4, 8), 6), ((2, 5, 1), 8),
    ((6, 3, 9), 4), ((1, 1, 2), 5), ((8, 2, 5), 7),
)

_UNWRAPS = (
    ((1, 2, 3), 9, 0), ((4, 8, 2), 5, -1), ((3, 1, 2), 7, 100),
    ((9, 5, 6), 8, 0), ((2, 2, 3), 6, 42), ((7, 1, 4), 3, 0),
    ((5, 5, 5), 9, 11),
)

_IF_LETS = (
    ((4, 8, 15), 8), ((3, 1, 4), 9), ((2, 7, 1), 1), ((6, 2, 9), 5),
    ((5, 3, 8), 8), ((1, 9, 4), 7),
)

OPTION_PAGE = _page(
    "rust-option", 350, "The type that might be nothing",
    "Rust has no null. A search returns Option, which is either Some with "
    "the value inside or None, and the compiler will not let you use the "
    "value without saying what happens when there is not one. match spells "
    "both out, unwrap_or supplies a default, if let handles the one case "
    "you care about.",
    "match found { Some(n) => println!(\"{}\", n), None => "
    "println!(\"none\") } — the None arm is not optional",
    "rust_option",
    tuple(
        (f"Find the first value in {{{_seq(v)}}} greater than {o}. match on "
         f"the Option and print the value, or the word none.",
         {"values": list(v), "want": "match", "over": o})
        for v, o in _MATCHES
    ) + tuple(
        (f"Find the first value in {{{_seq(v)}}} greater than {o}, and "
         f"print it or {f} if there is not one. Use unwrap_or.",
         {"values": list(v), "want": "unwrap_or", "over": o, "fallback": f})
        for v, o, f in _UNWRAPS
    ) + tuple(
        (f"Find the position of {t} in {{{_seq(v)}}} with position, then "
         f"use if let to print the index, or the word missing.",
         {"values": list(v), "want": "if_let", "target": t})
        for v, t in _IF_LETS
    ),
)


# ── 351. Iterators ───────────────────────────────────────────

_ITERS = (
    ((3, 1, 4, 1, 5), "sum", 0), ((2, 7, 1, 8), "sum", 0),
    ((9, 4, 6), "sum", 0), ((5, 5, 3, 1), "sum", 0),
    ((1, 2, 3, 4), "sum", 0),
    ((3, 9, 2, 8, 5), "count", 4), ((1, 7, 4, 6), "count", 3),
    ((5, 2, 9, 1), "count", 4), ((6, 3, 7, 2), "count", 4),
    ((2, 8, 1, 9), "count", 5),
    ((1, 9, 3), "max", 0), ((4, 2, 8), "max", 0), ((5, 1, 7), "max", 0),
    ((2, 6, 3), "max", 0), ((9, 1, 2), "max", 0),
    ((3, 1, 4, 1, 5), "doubled", 0), ((2, 7, 1), "doubled", 0),
    ((6, 2, 8), "doubled", 0), ((1, 5, 9), "doubled", 0),
    ((4, 3, 7), "doubled", 0),
)

_ITER_WORDS = {
    "sum": "add them up with sum",
    "count": "count how many are greater than {over} with filter and count",
    "max": "find the largest with max, falling back to 0",
    "doubled": "double each with map, collect them, and print them space "
               "separated",
}

ITER_PAGE = _page(
    "rust-iter", 351, "A chain of steps over a sequence",
    "iter borrows the sequence and hands you each item; map and filter "
    "describe what to do without doing it yet; sum, count and collect are "
    "what finally make it run. Nothing happens until one of those, which "
    "is why a chain with no ending does nothing at all.",
    "items.iter().filter(|&&n| n > 4).count() — two ampersands, because "
    "filter hands a reference to what iter already made a reference of",
    "rust_iter",
    tuple(
        (f"Take {{{_seq(v)}}} and "
         + (_ITER_WORDS[w].format(over=o) if w == "count" else _ITER_WORDS[w])
         + ". Print the answer.",
         {"values": list(v), "want": w, **({"over": o} if w == "count" else {})})
        for v, w, o in _ITERS
    ),
)


# ── 352. entry and or_insert ─────────────────────────────────

_TEXTS = (
    "banana", "mississippi", "letter", "success", "coffee", "balloon",
    "committee", "possess", "running", "little", "bookkeeper", "address",
    "tomorrow", "different", "necessary", "beginning", "parallel",
    "occurred", "access", "sheep",
)

ENTRY_PAGE = _page(
    "rust-entry", 352, "Counting without checking first",
    "entry hands you the slot for a key whether or not anything is there, "
    "and or_insert fills it in if it was empty. That is the whole counting "
    "idiom: no looking up to see whether the key exists, no second lookup "
    "to write it back. The star is because entry gives a reference and you "
    "want the number behind it.",
    "*counts.entry(ch).or_insert(0) += 1; — one lookup where "
    "contains_key then get then insert would be three",
    "rust_entry",
    tuple(
        (f"Count how often each character appears in {t!r}. Print them in "
         f"order of character as letter-then-count, space separated, using "
         f"entry and or_insert.", {"text": t})
        for t in _TEXTS
    ),
)


# ── 353. Vec calls ───────────────────────────────────────────

_POPS = (
    ((3, 1, 4, 1, 5), 2), ((2, 7, 1, 8), 1), ((9, 4, 6, 2), 3),
    ((5, 5, 3, 1), 2), ((1, 2, 3, 4, 5), 4), ((8, 3, 7), 1),
    ((6, 1, 9, 2), 2), ((4, 8, 2, 5), 3), ((7, 2, 6), 2),
    ((1, 5, 9, 3), 1),
)

_EMPTIES = (
    ((3, 1, 4), 7), ((2, 7), 5), ((9, 4, 6), 1), ((5, 3), 8),
    ((1, 2, 3), 4), ((8, 6), 2), ((7, 1, 5), 9), ((4, 9), 3),
    ((6, 2, 8), 6), ((5, 1), 7),
)

VEC_PAGE = _page(
    "rust-vec-ops", 353, "The calls a Vec answers to",
    "pop takes the last one and hands it back as an Option, because there "
    "might not be one. is_empty says what len == 0 says and says it better. "
    "clear keeps the memory and throws away the contents.",
    "items.pop() returns Option<i32>, not i32 — there might have been "
    "nothing to pop",
    "rust_vec_ops",
    tuple(
        (f"Start with {{{_seq(v)}}} and pop {t} time(s). Print what is left "
         f"space separated, then the length.",
         {"values": list(v), "want": "pop", "times": t})
        for v, t in _POPS
    ) + tuple(
        (f"Start with {{{_seq(v)}}}. Print whether it is empty, clear it, "
         f"print whether it is empty now, then push {p} and print the "
         f"length.", {"values": list(v), "want": "empty", "pushed": p})
        for v, p in _EMPTIES
    ),
)


# ── 354. VecDeque ────────────────────────────────────────────

_DEQUES = (
    ((3, 1, 4, 1, 5), 2), ((2, 7, 1, 8), 3), ((9, 4, 6), 1),
    ((5, 5, 3, 1), 2), ((1, 2, 3, 4, 5), 3), ((8, 3, 7, 2), 1),
    ((6, 1, 9), 2), ((4, 8, 2, 5), 3), ((7, 2, 6, 1), 2),
    ((1, 5, 9, 3), 1), ((2, 4, 6, 8), 3), ((5, 1, 7), 2),
    ((3, 9, 2, 6), 1), ((8, 2, 4), 2), ((6, 3, 1, 9), 3),
    ((4, 7, 5), 1), ((9, 6, 2, 8), 2), ((1, 3, 5, 7), 3),
    ((7, 4, 8), 2), ((2, 9, 1, 6), 1),
)

DEQUE_PAGE = _page(
    "rust-deque", 354, "A queue with two ends",
    "A Vec is fast at the back and slow at the front, so taking from the "
    "front of one is linear every time. VecDeque is the one to reach for "
    "when a breadth-first walk needs to push at one end and take from the "
    "other, and pop_front hands back an Option like every other pop here.",
    "queue.push_back(n) and queue.pop_front() — both constant, which is "
    "the whole reason it exists",
    "rust_deque",
    tuple(
        (f"Push {{{_seq(v)}}} onto the back of a VecDeque, then pop {t} "
         f"from the front. Print what came out space separated, then how "
         f"many are left.", {"values": list(v), "taken": t})
        for v, t in _DEQUES
    ),
)


# ── 355. Ownership and clone ─────────────────────────────────

_CLONES = (
    (3, 1, 4), (2, 7, 1, 8), (9, 4, 6), (5, 5, 3, 1), (1, 2, 3, 4),
    (8, 3, 7), (6, 1, 9, 2), (4, 8, 2), (7, 2, 6, 1), (1, 5, 9),
    (2, 4, 6, 8), (5, 1, 7), (3, 9, 2), (8, 2, 4, 6), (6, 3, 1),
    (4, 7, 5, 2), (9, 6, 2), (1, 3, 5, 7), (7, 4, 8), (2, 9, 1),
)

CLONE_PAGE = _page(
    "rust-clone", 355, "Who owns it, and what copying costs",
    "Passing a Vec by value moves it, and the name you passed is no longer "
    "usable. Passing a reference borrows it instead, which is what the "
    "ampersand is doing and why the function takes one. clone is the "
    "escape hatch and it is not free: it copies every element, which is "
    "why the solutions reach for a borrow first and a clone only when they "
    "must.",
    "fn total(items: &Vec<i32>) -> i32 borrows; total(items) without the "
    "ampersand would move it and there would be no second call",
    "rust_clone",
    tuple(
        (f"Make a Vec from {{{_seq(v)}}} and a clone of it. Print the total "
         f"of each through a function that borrows, then print whether "
         f"they are the same length.", {"values": list(v)})
        for v in _CLONES
    ),
)


# ── 356. Rc and RefCell ──────────────────────────────────────

_SHARED = (
    ((3, 1, 4), 9), ((2, 7, 1), 5), ((9, 4, 6), 2), ((5, 5, 3), 8),
    ((1, 2, 3), 7), ((8, 3, 7), 1), ((6, 1, 9), 4), ((4, 8, 2), 6),
    ((7, 2, 6), 3), ((1, 5, 9), 2), ((2, 4, 6), 8), ((5, 1, 7), 9),
    ((3, 9, 2), 5), ((8, 2, 4), 7), ((6, 3, 1), 4), ((4, 7, 5), 1),
    ((9, 6, 2), 3), ((1, 3, 5), 6), ((7, 4, 8), 2), ((2, 9, 1), 8),
)

RC_PAGE = _page(
    "rust-rc-refcell", 356, "Shared, and mutable anyway",
    "Rc lets two names own the same value by counting how many there are. "
    "That alone gives you sharing without mutation, because Rc hands out "
    "read-only access. RefCell is the other half: it moves the borrow "
    "check to run time, so you can change what is shared. Together they "
    "are how Rust writes a structure whose parts point at each other.",
    "let other = Rc::clone(&shared); other.borrow_mut().push(9); — and "
    "shared sees it, because there is only one value",
    "rust_rc_refcell",
    tuple(
        (f"Wrap {{{_seq(v)}}} in Rc and RefCell, make a second handle with "
         f"Rc::clone, push {p} through the second one, then print the "
         f"length, the total, and the strong count, from the first.",
         {"values": list(v), "pushed": p})
        for v, p in _SHARED
    ),
)


# ── 357. The tree Rust has to write ──────────────────────────

_TREES = (
    (3, 9, 20, 15, 7), (5, 3, 8, 1, 4, 7, 9), (1, 2, 3, 4),
    (10, 5, 15, 3, 7, 12, 18), (2, 1, 3, 6), (8, 4, 12, 2, 6),
    (6, 2, 9, 1, 4, 8), (7, 3, 11, 1, 5, 9, 13), (4, 2, 6, 1),
    (9, 5, 12, 3, 7, 11), (20, 10, 30, 5, 15), (1, 2, 3, 4, 5, 6, 7),
    (15, 9, 21, 4, 12), (3, 1, 5, 2, 4, 6), (11, 6, 16, 3, 8),
    (2, 7, 5, 1, 6, 9), (12, 7, 17, 4, 9, 14), (5, 2, 8, 1, 3),
    (30, 15, 45, 8, 20, 40), (1, 3, 2, 5, 4),
)

TREE_PAGE = _page(
    "rust-tree", 357, "A tree the way Rust has to write one",
    "Option<Rc<RefCell<TreeNode>>> is every one of the last three pages at "
    "once, and it is exactly what the tree problems in the bank hand you. "
    "Option because a child might not be there, Rc because a parent and a "
    "walk both need to reach the node, RefCell because you have to be able "
    "to attach children after making it. borrow to read, borrow_mut to "
    "change.",
    "type Tree = Option<Rc<RefCell<TreeNode>>>; and depth matches on it, "
    "None => 0",
    "rust_tree",
    tuple(
        (f"Build the complete tree {{{_seq(v)}}} as Option<Rc<RefCell<"
         f"TreeNode>>>, linking each position to the two below it. Print "
         f"the root value, the depth, and the total.",
         {"values": list(v)})
        for v in _TREES
    ),
)


# ── 358. Sorting ─────────────────────────────────────────────

_NUMBER_SORTS = (
    (5, 1, 4, 1, 2), (3, 9, 1, 3, 6), (8, 2, 7, 2), (6, 3, 9, 3, 5),
    (2, 8, 4, 8), (9, 1, 5, 1), (7, 4, 8, 4), (1, 6, 2, 6, 3),
    (4, 7, 1, 7), (5, 2, 9, 2, 6),
)

_WORD_SORTS = (
    ("pear", "fig", "banana", "kiwi"),
    ("cat", "elephant", "dog", "bee"),
    ("red", "yellow", "blue", "cyan"),
    ("one", "seven", "two", "eleven"),
    ("north", "up", "east", "down"),
    ("iron", "tin", "copper", "zinc"),
    ("oak", "willow", "elm", "cedar"),
    ("mars", "io", "venus", "titan"),
    ("salt", "pepper", "bay", "clove"),
    ("rook", "pawn", "bishop", "king"),
)

SORT_PAGE = _page(
    "rust-sort", 358, "Sorting, and sorting by something",
    "sort orders in place and dedup removes neighbouring repeats, which "
    "means dedup only removes all of them if you sorted first. sort_by "
    "takes a comparison returning Ordering, and then chains with it, "
    "which is how you say by length and alphabetically within that.",
    "items.sort(); items.dedup(); — the order matters, dedup only looks "
    "at neighbours",
    "rust_sort",
    tuple(
        (f"Sort {{{_seq(v)}}}, remove the repeats with dedup, and print "
         f"what is left space separated.",
         {"values": list(v), "want": "numbers"})
        for v in _NUMBER_SORTS
    ) + tuple(
        (f"Sort {{{_wordlist(w)}}} by length, and alphabetically where the "
         f"lengths tie, using sort_by and then. Print them space "
         f"separated.", {"words": list(w), "want": "words"})
        for w in _WORD_SORTS
    ),
)


# ── 359. String and str ──────────────────────────────────────

_BUILDS = (
    ("red", "green", "blue"), ("one", "two", "three"),
    ("north", "south"), ("cat", "dog", "bird"), ("iron", "tin"),
    ("oak", "elm", "ash"), ("salt", "pepper"), ("up", "down", "left"),
    ("mars", "venus"), ("rook", "pawn", "king"),
)

_UPPERS = (
    ("banana", "a"), ("mississippi", "s"), ("letter", "t"),
    ("success", "c"), ("coffee", "f"), ("balloon", "l"),
    ("running", "n"), ("little", "t"), ("address", "d"), ("sheep", "e"),
)

STRING_PAGE = _page(
    "rust-string", 359, "String and the str it borrows",
    "String owns its bytes and can grow; a str is a borrowed view of some "
    "and cannot. Literals are the second kind, which is why push_str takes "
    "one and why building up an answer means starting from String::new. "
    "chars is how you walk the characters, because indexing a string by "
    "byte would cut a character in half.",
    "let mut out = String::new(); out.push_str(word); — push_str takes "
    "the borrowed kind, and out owns the result",
    "rust_string",
    tuple(
        (f"Join {{{_wordlist(w)}}} with dashes by pushing onto a String, "
         f"trim the trailing dash, then print it and its length.",
         {"words": list(w), "want": "build"})
        for w in _BUILDS
    ) + tuple(
        (f"Upper-case {t!r} with chars and collect, print it, then print "
         f"how many {c!r} the original held.",
         {"text": t, "letter": c, "want": "upper"})
        for t, c in _UPPERS
    ),
)


RUST_PAGES: tuple[Page, ...] = (
    OPTION_PAGE,
    ITER_PAGE,
    ENTRY_PAGE,
    VEC_PAGE,
    DEQUE_PAGE,
    CLONE_PAGE,
    RC_PAGE,
    TREE_PAGE,
    SORT_PAGE,
    STRING_PAGE,
)
