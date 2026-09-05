"""Pages 81-90: Dart, starting with null safety.

Sixteen hundred Dart answers and the workbook had never written `Map<` or
`Set<`, never called `.sort`, `.map` or `.where`, and never once used `??`,
`?.` or `late`.

The null-safety gap is the one that matters. Dart is null-safe by default,
so `int` and `int?` are genuinely different types and the compiler enforces
it, the same way Rust enforces Option. The Dart solutions rely on that
throughout: `Node?` for a child that might not exist, `??=` for a parameter
that arrived null, `!` to promise something the compiler cannot see. None
of it had ever appeared in a Dart page.

Ten pages. Null safety first because it is the type system rather than a
convenience, then the collections, then the node classes where the two meet
and a chain walk has to prove non-null before it can follow a link.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

DART_ONLY = ("dart",)


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
        languages=DART_ONLY,
        tier="advanced",
    )


def _seq(items) -> str:
    return ", ".join(str(n) for n in items)


def _wordlist(items) -> str:
    return ", ".join(f"'{w}'" for w in items)


def _pairs_text(pairs) -> str:
    return ", ".join(f"{k}={v}" for k, v in pairs)


# ── 81. Null safety ──────────────────────────────────────────
#
# Half the rows find nothing, so null is something you have watched turn
# up rather than been told about.

_NULLS = (
    ((3, 9, 2), 5, 0), ((1, 2, 3), 9, 7), ((7, 4, 8), 6, 0),
    ((2, 5, 1), 8, 4), ((6, 3, 9), 4, 0), ((1, 1, 2), 5, 8),
    ((8, 2, 5), 7, 0), ((3, 3, 1), 6, 5), ((9, 1, 4), 5, 0),
    ((2, 2, 2), 4, 6), ((5, 7, 3), 6, 0), ((1, 4, 2), 8, 9),
    ((6, 8, 1), 7, 0), ((3, 2, 5), 9, 1), ((4, 9, 2), 6, 0),
    ((1, 3, 3), 7, 2), ((7, 5, 9), 8, 0), ((2, 4, 1), 6, 3),
    ((8, 6, 3), 7, 0), ((1, 2, 4), 9, 5),
)

NULL_PAGE = _page(
    "dart-null", 81, "The question mark that changes the type",
    "int and int? are different types here, and the compiler enforces it. "
    "?? supplies a value when the left side is null, ??= assigns only when "
    "it was null, and neither fires on zero or an empty string the way a "
    "falsy check would. This is Dart's version of the thing Rust calls "
    "Option, and the solutions lean on it constantly.",
    "int? found = at == -1 ? null : items[at]; then found ?? 0 — and ??= "
    "assigns only if it was still null",
    "dart_null",
    tuple(
        (f"Look in {{{_seq(v)}}} for the first value above {o}, keeping the "
         f"result as int?. Print it or {f} with ??, then whether it was "
         f"null, then assign {f} with ??= and print it again.",
         {"values": list(v), "over": o, "fallback": f})
        for v, o, f in _NULLS
    ),
)


# ── 82. Map ──────────────────────────────────────────────────

_MAPS = (
    ((("ann", 30), ("bob", 25)), "ann"),
    ((("ann", 30), ("bob", 25)), "cy"),
    ((("red", 4), ("blue", 7), ("green", 2)), "blue"),
    ((("red", 4), ("blue", 7)), "pink"),
    ((("one", 1), ("two", 2), ("three", 3)), "three"),
    ((("one", 1), ("two", 2)), "four"),
    ((("cat", 9), ("dog", 5)), "cat"),
    ((("cat", 9), ("dog", 5)), "bird"),
    ((("north", 1), ("south", 2), ("east", 3)), "east"),
    ((("north", 1), ("south", 2)), "west"),
    ((("iron", 26), ("tin", 50)), "tin"),
    ((("iron", 26), ("tin", 50)), "zinc"),
    ((("oak", 3), ("elm", 6), ("ash", 9)), "elm"),
    ((("oak", 3), ("elm", 6)), "yew"),
    ((("salt", 2), ("pepper", 8)), "salt"),
    ((("salt", 2), ("pepper", 8)), "bay"),
    ((("rook", 5), ("pawn", 1), ("king", 7)), "pawn"),
    ((("rook", 5), ("pawn", 1)), "queen"),
    ((("mars", 4), ("venus", 2)), "venus"),
    ((("mars", 4), ("venus", 2)), "pluto"),
)

MAP_PAGE = _page(
    "dart-map", 82, "A keyed store, and the key that is not there",
    "Looking a key up in a Dart Map gives you V? rather than V, because it "
    "might not be there — the same rule as everywhere else in the language, "
    "applied to a lookup. containsKey answers the question directly, and "
    "keys comes back as an iterable you turn into a list before sorting.",
    "final found = ages['cy']; is int?, so it needs ?? before it can be "
    "printed as a number",
    "dart_map",
    tuple(
        (f"Build a Map<String, int> holding {_pairs_text(ps)}. Look up "
         f"'{look}' and print the value or the word missing, then whether "
         f"the key is there, then the length, then the keys sorted.",
         {"pairs": [list(p) for p in ps], "look": look})
        for ps, look in _MAPS
    ),
)


# ── 83. Set ──────────────────────────────────────────────────

_SETS = (
    ((3, 1, 4, 1, 5), 4, 3), ((2, 7, 2, 8), 8, 7), ((9, 4, 9, 6), 6, 4),
    ((5, 5, 3, 1), 3, 5), ((1, 2, 2, 3), 2, 3), ((8, 3, 8, 7), 7, 3),
    ((6, 1, 6, 9), 9, 1), ((4, 8, 4, 2), 2, 8), ((7, 2, 7, 6), 6, 2),
    ((1, 5, 1, 9), 9, 5), ((2, 4, 4, 8), 8, 2), ((5, 1, 5, 7), 7, 1),
    ((3, 9, 3, 2), 2, 9), ((8, 2, 8, 4), 4, 2), ((6, 3, 6, 1), 1, 3),
    ((4, 7, 4, 5), 5, 7), ((9, 6, 9, 2), 2, 6), ((1, 3, 1, 5), 5, 3),
    ((7, 4, 7, 8), 8, 4), ((2, 9, 2, 1), 1, 9),
)

SET_PAGE = _page(
    "dart-set", 83, "Membership without repeats",
    "toSet drops the duplicates, and contains is constant where a list scan "
    "is not. A Set has no order, so anything you print from one has to be "
    "sorted first or the answer is not repeatable — which is a rule worth "
    "learning once rather than debugging later.",
    "final seen = items.toSet(); then seen.toList()..sort() — the cascade "
    "sorts and hands the list back",
    "dart_set",
    tuple(
        (f"Turn {{{_seq(v)}}} into a Set, remove {d}, then print what is "
         f"left in ascending order, the length, and whether {p} is still "
         f"there.", {"values": list(v), "dropped": d, "probe": p})
        for v, d, p in _SETS
    ),
)


# ── 84. Building a list ──────────────────────────────────────

_FILLS = ((4, 3), (5, 0), (3, 7), (6, 1), (4, 9), (7, 2), (3, 5),
          (5, 4), (6, 8), (4, 6))
_GENS = ((5, 2), (4, 3), (6, 1), (3, 5), (7, 2), (5, 4), (4, 7),
         (6, 3), (3, 9), (5, 6))

MAKE_PAGE = _page(
    "dart-list-make", 84, "Building a list of a known length",
    "List.filled makes n copies of one value and is fixed length unless you "
    "ask otherwise. List.generate takes the index and builds each element "
    "from it, which is the one that turns a pattern into a list in a single "
    "step and the one the solutions reach for.",
    "List<int>.generate(5, (i) => i * 2) gives 0 2 4 6 8 — the function "
    "receives the position",
    "dart_list_make",
    tuple(
        (f"Make a list of {n} copies of {s} with List.filled. Print it "
         f"space separated, then its length.",
         {"n": n, "step": s, "want": "filled"})
        for n, s in _FILLS
    ) + tuple(
        (f"Use List.generate to build {n} values where position i holds "
         f"i * {s}. Print it space separated, then its length.",
         {"n": n, "step": s, "want": "generate"})
        for n, s in _GENS
    ),
)


# ── 85. Adding and taking away ───────────────────────────────

_OPS = (
    ((3, 1, 4), 9, 1, 7), ((2, 7, 1), 5, 0, 8), ((9, 4, 6), 2, 2, 3),
    ((5, 5, 3), 8, 1, 1), ((1, 2, 3), 4, 0, 6), ((8, 3, 7), 1, 2, 9),
    ((6, 1, 9), 4, 1, 2), ((4, 8, 2), 6, 0, 5), ((7, 2, 6), 3, 2, 4),
    ((1, 5, 9), 2, 1, 7), ((2, 4, 6), 8, 0, 3), ((5, 1, 7), 9, 2, 6),
    ((3, 9, 2), 5, 1, 8), ((8, 2, 4), 7, 0, 1), ((6, 3, 1), 4, 2, 9),
    ((4, 7, 5), 1, 1, 2), ((9, 6, 2), 3, 0, 5), ((1, 3, 5), 6, 2, 4),
    ((7, 4, 8), 2, 1, 6), ((2, 9, 1), 8, 0, 3),
)

OPS_PAGE = _page(
    "dart-list-ops", 85, "Adding and taking away",
    "removeLast hands back what it removed and costs nothing; removeAt "
    "hands back what it removed and has to shift everything after it along. "
    "insert at the front is the same cost for the same reason. A list "
    "literal is fixed length, so these start with toList to get a growable "
    "one.",
    "final gone = items.removeAt(1); — it returns the element, not the "
    "list, which is easy to forget",
    "dart_list_ops",
    tuple(
        (f"Start with {{{_seq(v)}}}. add {added}, removeLast and print what "
         f"came back, removeAt({at}) and print that, then insert {f} at the "
         f"front and print the list space separated.",
         {"values": list(v), "added": added, "at": at, "front": f})
        for v, added, at, f in _OPS
    ),
)


# ── 86. map and where ────────────────────────────────────────

_ITERS = (
    ((3, 1, 4), "doubled", 0), ((2, 7, 1), "doubled", 0),
    ((6, 2, 8), "doubled", 0), ((1, 5, 9), "doubled", 0),
    ((4, 3, 7), "doubled", 0), ((5, 2, 6), "doubled", 0),
    ((3, 9, 2, 8), "kept", 4), ((1, 7, 4, 6), "kept", 3),
    ((5, 2, 9, 1), "kept", 4), ((6, 3, 7, 2), "kept", 4),
    ((2, 8, 1, 9), "kept", 5), ((7, 1, 5, 3), "kept", 4),
    ((9, 2, 6, 4), "kept", 5),
    ((3, 1, 4), "reduce", 0), ((2, 7, 1), "reduce", 0),
    ((9, 4, 6), "reduce", 0), ((5, 5, 3), "reduce", 0),
    ((1, 2, 3), "reduce", 0), ((8, 3, 7), "reduce", 0),
    ((6, 1, 9), "reduce", 0),
)

_ITER_WORDS = {
    "doubled": "double each with map and print them space separated",
    "kept": "keep the ones above {over} with where, print them space "
            "separated, then how many",
    "reduce": "add them all with reduce and print it, then find the largest "
              "with reduce and print that",
}

ITER_PAGE = _page(
    "dart-iter", 86, "map, where, and what makes them run",
    "map and where return lazy iterables rather than lists, so nothing "
    "happens until something asks — toList, or a for loop, or a reduce. "
    "That is why the calls end in toList here, and why forgetting it gives "
    "you an object that looks wrong when printed.",
    "items.where((n) => n > 4).toList() — without the toList it is an "
    "Iterable that has not run yet",
    "dart_iter",
    tuple(
        (f"Take {{{_seq(v)}}} and "
         + (_ITER_WORDS[w].format(over=o) if w == "kept" else _ITER_WORDS[w])
         + ".",
         {"values": list(v), "want": w, **({"over": o} if w == "kept" else {})})
        for v, w, o in _ITERS
    ),
)


# ── 87. Sorting ──────────────────────────────────────────────

_NUMBER_SORTS = (
    (5, 1, 4, 2), (3, 9, 1, 6), (8, 2, 7, 4), (6, 3, 9, 1),
    (2, 8, 4, 6), (9, 1, 5, 3), (7, 4, 8, 2), (1, 6, 2, 9),
    (4, 7, 1, 8), (5, 2, 9, 6),
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
    "dart-sort", 87, "Sorting in place, with a comparison",
    "sort returns nothing. It reorders the list you gave it and hands back "
    "void, which is why assigning its result gives you null and why the "
    "cascade operator exists. The comparison returns a negative number, "
    "zero or a positive one, and compareTo is how you get one out of two "
    "strings.",
    "final down = items.toList()..sort((x, y) => y - x); — the cascade "
    "keeps the list, because sort itself returns nothing",
    "dart_sort",
    tuple(
        (f"Sort {{{_seq(v)}}} ascending and print it, then sort a copy "
         f"descending and print that, both space separated.",
         {"values": list(v), "want": "numbers"})
        for v in _NUMBER_SORTS
    ) + tuple(
        (f"Sort {{{_wordlist(w)}}} by length, alphabetically where lengths "
         f"tie, and print it space separated.",
         {"words": list(w), "want": "words"})
        for w in _WORD_SORTS
    ),
)


# ── 88. Strings ──────────────────────────────────────────────

_REPEATS = (
    ("ab", 3, "hi", 5), ("xy", 4, "go", 6), ("-", 5, "up", 4),
    ("ab", 2, "cat", 6), ("=", 6, "dog", 7), ("no", 3, "yes", 5),
    ("z", 7, "end", 6), ("qp", 2, "on", 5), ("*", 4, "run", 7),
    ("mn", 3, "it", 4),
)

_SPLITS = (
    ("a,b,c", ",", 3), ("one two three", " ", 3), ("x-y-z", "-", 3),
    ("red,blue", ",", 3), ("up down", " ", 2), ("1:2:3", ":", 3),
    ("cat,dog,emu", ",", 4), ("north south", " ", 5), ("p|q|r", "|", 3),
    ("salt,bay", ",", 4),
)

STRING_PAGE = _page(
    "dart-string", 88, "Splitting, joining, padding",
    "A string times a number repeats it, which no other language here "
    "spells that way. padLeft takes the total width rather than the padding "
    "to add. substring takes a start and an end, not a length, and split "
    "and join are the pair that turns text into a list and back.",
    "'ab' * 3 gives 'ababab', and 'hi'.padLeft(5, '.') gives '...hi'",
    "dart_string",
    tuple(
        (f"Print {u!r} repeated {t} times using the multiply operator, then "
         f"{w!r} padded on the left with dots to width {n}.",
         {"unit": u, "times": t, "word": w, "width": n, "want": "repeat"})
        for u, t, w, n in _REPEATS
    ) + tuple(
        (f"Split {txt!r} on {sep!r}, print the parts joined with dashes, "
         f"then how many parts, then the first {c} characters of the "
         f"original.",
         {"text": txt, "sep": sep, "cut": c, "want": "split"})
        for txt, sep, c in _SPLITS
    ),
)


# ── 89. A class that points at itself ────────────────────────

_CHAINS = (
    (3, 1, 4), (2, 7, 1, 8), (9, 4, 6), (5, 5, 3, 1), (1, 2, 3, 4),
    (8, 3, 7), (6, 1, 9, 2), (4, 8, 2), (7, 2, 6, 1), (1, 5, 9),
    (2, 4, 6, 8), (5, 1, 7), (3, 9, 2), (8, 2, 4, 6), (6, 3, 1),
    (4, 7, 5, 2), (9, 6, 2), (1, 3, 5, 7), (7, 4, 8), (2, 9, 1),
)

NODE_PAGE = _page(
    "dart-node", 89, "A class that points at itself",
    "ListNode? next is the whole idea: the last node has nothing after it, "
    "and the type says so. The walk cannot reach through node.next until it "
    "has proved node is not null, and the compiler tracks that proof — "
    "which is why the loop variable is var rather than final and why the "
    "null check is the loop condition.",
    "class ListNode { int val; ListNode? next; ListNode(this.val, "
    "[this.next]); } — the optional positional parameter builds it in one "
    "line",
    "dart_node",
    tuple(
        (f"Build a chain of ListNode from {{{_seq(v)}}}, walking backwards "
         f"so each node points at the one after it. Print it with arrows, "
         f"then how many nodes there were.", {"values": list(v)})
        for v in _CHAINS
    ),
)


# ── 90. Two children ─────────────────────────────────────────

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
    "dart-tree", 90, "Two children, either of which might be missing",
    "The same class with one more nullable field, and recursion that "
    "returns zero at null rather than checking before it descends. That is "
    "the shape every tree solution in the bank uses, and it works precisely "
    "because TreeNode? is a type the function can accept.",
    "int depth(TreeNode? node) { if (node == null) return 0; ... } — the "
    "parameter is nullable so the recursion needs no guard at the call",
    "dart_tree",
    tuple(
        (f"Build the complete tree {{{_seq(v)}}} node by node, linking each "
         f"position to the two below it. Print the root value, the depth, "
         f"and the total.", {"values": list(v)})
        for v in _TREES
    ),
)


DART2_PAGES: tuple[Page, ...] = (
    NULL_PAGE, MAP_PAGE, SET_PAGE, MAKE_PAGE, OPS_PAGE,
    ITER_PAGE, SORT_PAGE, STRING_PAGE, NODE_PAGE, TREE_PAGE,
)
