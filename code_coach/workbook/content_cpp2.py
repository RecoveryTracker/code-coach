"""Pages 81-90: C++, past the point the pages stopped.

The C++ pages taught vector, push_back and size, and then stopped. Across
sixteen hundred answers the workbook had never written unordered_map, never
called std::sort, never used begin or end, never touched stack or queue,
and never called empty, which the solutions use thirty-five times.

It is a particular kind of half-covered. The container was taught and the
library that makes containers worth having was not, so every C++ solution
in the bank is assembled out of the parts that were missing.

Ten pages: the vector calls in full, the two hash containers, sort with a
lambda, iterators, the adapters, the algorithms header, strings, and the
node structs, which here carry the same new-and-delete duty they had in C.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

CPP_ONLY = ("cpp",)


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
        languages=CPP_ONLY,
        tier="advanced",
    )


def _seq(items) -> str:
    return ", ".join(str(n) for n in items)


def _wordlist(items) -> str:
    return ", ".join(f'"{w}"' for w in items)


def _pairs_text(pairs) -> str:
    return ", ".join(f"{k}={v}" for k, v in pairs)


# ── 81. vector ───────────────────────────────────────────────

_VECTORS = (
    ((3, 1, 4), 9), ((2, 7, 1), 5), ((9, 4, 6), 2), ((5, 5, 3), 8),
    ((1, 2, 3), 4), ((8, 3, 7), 1), ((6, 1, 9), 4), ((4, 8, 2), 6),
    ((7, 2, 6), 3), ((1, 5, 9), 2), ((2, 4, 6), 8), ((5, 1, 7), 9),
    ((3, 9, 2), 5), ((8, 2, 4), 7), ((6, 3, 1), 4), ((4, 7, 5), 1),
    ((9, 6, 2), 3), ((1, 3, 5), 6), ((7, 4, 8), 2), ((2, 9, 1), 8),
)

VECTOR_PAGE = _page(
    "cpp-vector", 81, "The calls a vector answers to",
    "empty says what size() == 0 says and says it in constant time on every "
    "container, including the ones where size is not. front and back hand "
    "back references, so they can be assigned through, and neither checks "
    "that there is anything there — on an empty vector both are undefined "
    "behaviour rather than an error.",
    "items.empty() before items.front(), always — front on an empty vector "
    "is undefined, not a crash you can rely on",
    "cpp_vector",
    tuple(
        (f"Start with a vector holding {{{_seq(v)}}}. Print whether it is "
         f"empty as yes or no, push_back {p}, print front, print back, "
         f"pop_back, then print what is left space separated and the size.",
         {"values": list(v), "pushed": p})
        for v, p in _VECTORS
    ),
)


# ── 82. unordered_map ────────────────────────────────────────

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
    "cpp-map", 82, "An unordered map, and the key that is not there",
    "count is how you ask without changing anything. Square brackets on a "
    "missing key do not fail and do not return nothing: they insert a "
    "default-constructed value and hand it back, so a lookup written that "
    "way quietly grows the map. That is the trap, and count before "
    "brackets is the habit that avoids it.",
    "if (seen.count(k)) cout << seen[k]; — brackets alone would insert a "
    "zero for a key that was never there",
    "cpp_map",
    tuple(
        (f"Build an unordered_map<string, int> holding {_pairs_text(ps)}. "
         f'Use count to look up "{look}" and print the value or the word '
         f"missing, then the count itself, then the size, then the keys "
         f"sorted.", {"pairs": [list(p) for p in ps], "look": look})
        for ps, look in _MAPS
    ),
)


# ── 83. unordered_set ────────────────────────────────────────

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
    "cpp-set", 83, "Membership without repeats",
    "Built from a pair of iterators, which is how most containers accept "
    "another container. count is constant where a scan of a vector is "
    "linear, and that is the whole reason the solutions build one. An "
    "unordered_set has no order, so anything printed from it is sorted "
    "first or the output is not repeatable.",
    "unordered_set<int> seen(items.begin(), items.end()); — the two "
    "iterators are the range, and this is the usual way to convert",
    "cpp_set",
    tuple(
        (f"Build an unordered_set from {{{_seq(v)}}}, erase {d}, then print "
         f"what is left in ascending order, the size, and the count of {p}.",
         {"values": list(v), "dropped": d, "probe": p})
        for v, d, p in _SETS
    ),
)


# ── 84. sort ─────────────────────────────────────────────────

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
    "cpp-sort", 84, "Sorting a range with a lambda",
    "sort takes two iterators rather than a container, which is what lets "
    "it sort part of one. The comparator answers does x come strictly "
    "before y, and it must be a strict weak ordering: return true for equal "
    "elements and the sort is entitled to run off the end of the array. "
    "Because a lambda is its own type, the compiler inlines it, which is "
    "why this beats qsort on the same data.",
    "sort(items.begin(), items.end(), [](int x, int y) { return x > y; }) "
    "— strictly greater, never greater-or-equal",
    "cpp_sort",
    tuple(
        (f"Sort {{{_seq(v)}}} ascending with sort and print it, then sort "
         f"it again descending with a lambda and print that.",
         {"values": list(v), "want": "numbers"})
        for v in _NUMBER_SORTS
    ) + tuple(
        (f"Sort {{{_wordlist(w)}}} by length, alphabetically where lengths "
         f"tie, using a lambda. Print it space separated.",
         {"words": list(w), "want": "words"})
        for w in _WORD_SORTS
    ),
)


# ── 85. Iterators ────────────────────────────────────────────

_ITERS = (
    ((3, 1, 4, 1, 5), 4), ((2, 7, 1, 8), 7), ((9, 4, 6, 2), 6),
    ((5, 5, 3, 1), 3), ((1, 2, 3, 4), 9), ((8, 3, 7, 2), 8),
    ((6, 1, 9, 4), 1), ((4, 8, 2, 5), 5), ((7, 2, 6, 3), 9),
    ((1, 5, 9, 2), 5), ((2, 4, 6, 8), 6), ((5, 1, 7, 3), 7),
    ((3, 9, 2, 6), 4), ((8, 2, 4, 1), 2), ((6, 3, 1, 9), 3),
    ((4, 7, 5, 2), 8), ((9, 6, 2, 8), 2), ((1, 3, 5, 7), 5),
    ((7, 4, 8, 1), 4), ((2, 9, 1, 6), 3),
)

ITER_PAGE = _page(
    "cpp-iterators", 85, "begin, end, and what sits between them",
    "end points one past the last element, not at it, which is why the loop "
    "condition is != end rather than <= something and why dereferencing end "
    "is undefined. find returns end when it did not find anything, so the "
    "comparison against end is the whole result. Subtracting two iterators "
    "gives the distance between them, which is how an index comes out.",
    "auto found = find(items.begin(), items.end(), 4); then compare found "
    "against end — that is the not-found answer",
    "cpp_iterators",
    tuple(
        (f"Total {{{_seq(v)}}} by walking it with an explicit iterator, "
         f"print the total, then use find to look for {t} and print its "
         f"index or -1, then print the first element and the last through "
         f"iterators.", {"values": list(v), "target": t})
        for v, t in _ITERS
    ),
)


# ── 86. stack and queue ──────────────────────────────────────
#
# No list here reads the same backwards, because that is the only data
# where the two orders would print the same line.

_ADAPTERS = (
    (3, 1, 4), (2, 7, 1), (9, 4, 6), (5, 5, 3), (1, 2, 3),
    (8, 3, 7), (6, 1, 9), (4, 8, 2), (7, 2, 6), (1, 5, 9),
    (2, 4, 6), (5, 1, 7), (3, 9, 2), (8, 2, 4), (6, 3, 1),
    (4, 7, 5), (9, 6, 2), (1, 3, 5), (7, 4, 8), (2, 9, 1),
)

ADAPTER_PAGE = _page(
    "cpp-adapters", 86, "A stack and a queue, made of something else",
    "Neither is a container. Both are wrappers that take one and expose "
    "only the operations that make sense, which is why a stack has top and "
    "a queue has front and neither can be walked. pop returns nothing: you "
    "read the element first and remove it second, because returning it "
    "would have to copy it and that copy could throw.",
    "pile.top() then pile.pop() — two calls, because pop returns void on "
    "purpose",
    "cpp_adapters",
    tuple(
        (f"Push {{{_seq(v)}}} onto a stack and empty it, printing the "
         f"values space separated. Then push the same into a queue and "
         f"empty that. The two lines come out opposite.",
         {"values": list(v)})
        for v in _ADAPTERS
    ),
)


# ── 87. Algorithms ───────────────────────────────────────────

_ALGOS = (
    (3, 9, 2, 8), (1, 7, 4, 6), (5, 2, 9, 1), (6, 3, 7, 2),
    (2, 8, 1, 9), (7, 1, 5, 3), (9, 2, 6, 4), (4, 8, 2, 7),
    (1, 6, 3, 9), (8, 3, 1, 6), (2, 9, 5, 1), (5, 4, 8, 2),
    (3, 7, 1, 9), (6, 2, 4, 8), (1, 5, 9, 3), (7, 4, 2, 6),
    (9, 1, 8, 3), (2, 6, 4, 9), (4, 1, 7, 5), (8, 5, 2, 6),
)

ALGO_PAGE = _page(
    "cpp-algorithms", 87, "The header that does the work for you",
    "max_element and min_element return iterators rather than values, so "
    "they need dereferencing, and both return end on an empty range. "
    "accumulate takes the starting value, and that value decides the type: "
    "pass 0 to sum doubles and you get integer arithmetic and a wrong "
    "answer, which is the classic version of this bug.",
    "*max_element(items.begin(), items.end()) — the star, because it "
    "hands back where the largest is rather than what it is",
    "cpp_algorithms",
    tuple(
        (f"From {{{_seq(v)}}} print the largest, the smallest, the total "
         f"with accumulate, then reverse it in place and print it space "
         f"separated.", {"values": list(v)})
        for v in _ALGOS
    ),
)


# ── 88. Strings ──────────────────────────────────────────────

_STRINGS = (
    ("banana", 3, "nan", "ab", 3), ("mississippi", 4, "ssi", "xy", 2),
    ("letter", 3, "tt", "-", 5), ("success", 4, "cc", "ab", 2),
    ("coffee", 3, "ff", "=", 4), ("balloon", 4, "ll", "no", 3),
    ("committee", 5, "mm", "z", 6), ("possess", 4, "ss", "qp", 2),
    ("running", 3, "nn", "*", 5), ("little", 3, "tt", "mn", 3),
    ("bookkeeper", 4, "kk", "ab", 4), ("address", 3, "dd", "xy", 3),
    ("tomorrow", 4, "rr", ".", 6), ("different", 4, "ff", "pq", 2),
    ("necessary", 4, "ss", "+", 5), ("beginning", 5, "nn", "rs", 3),
    ("parallel", 4, "ll", "~", 4), ("occurred", 4, "cc", "tu", 2),
    ("access", 3, "cc", "#", 6), ("sheep", 3, "ee", "vw", 3),
)

STRING_PAGE = _page(
    "cpp-string", 88, "The string calls worth knowing",
    "substr takes a start and a length, not a start and an end, which is "
    "the opposite of most languages here and the reason to check. find "
    "returns string::npos when it misses, which is the largest possible "
    "size_t rather than -1, so comparing it against a signed number does "
    "the wrong thing quietly.",
    "size_t at = text.find(needle); then compare against string::npos — "
    "never against -1, because npos is unsigned",
    "cpp_string",
    tuple(
        (f"From {txt!r} print the first {c} characters with substr, then "
         f"the length, then the index of {needle!r} or -1 if it is not "
         f"there, then build {u!r} repeated {t} times with += and print it.",
         {"text": txt, "cut": c, "needle": needle, "unit": u, "times": t})
        for txt, c, needle, u, t in _STRINGS
    ),
)


# ── 89. Node structs ─────────────────────────────────────────

_CHAINS = (
    (3, 1, 4), (2, 7, 1, 8), (9, 4, 6), (5, 5, 3, 1), (1, 2, 3, 4),
    (8, 3, 7), (6, 1, 9, 2), (4, 8, 2), (7, 2, 6, 1), (1, 5, 9),
    (2, 4, 6, 8), (5, 1, 7), (3, 9, 2), (8, 2, 4, 6), (6, 3, 1),
    (4, 7, 5, 2), (9, 6, 2), (1, 3, 5, 7), (7, 4, 8), (2, 9, 1),
)

NODE_PAGE = _page(
    "cpp-node", 89, "A struct, a pointer, and the arrow",
    "new instead of malloc, delete instead of free, and a constructor that "
    "sets the fields in an initialiser list rather than by assignment. The "
    "duty is the same as it was in C: every new needs its delete, and "
    "freeing a chain still means saving the next pointer before letting go "
    "of the node holding it.",
    "ListNode(int v) : val(v), next(nullptr) {} — the colon starts the "
    "initialiser list, which sets rather than assigns",
    "cpp_node",
    tuple(
        (f"Build a chain of new'd ListNode from {{{_seq(v)}}}. Print it "
         f"with arrows, then the total of the values, then delete every "
         f"node.", {"values": list(v)})
        for v in _CHAINS
    ),
)


# ── 90. Trees ────────────────────────────────────────────────

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
    "cpp-tree", 90, "Two pointers per node",
    "The same struct with one more pointer, and a free that has to go down "
    "before it comes back up — delete the node first and the pointers to "
    "its children go with it, so the children leak. That ordering is the "
    "only thing freeTree is really about.",
    "freeTree(node->left); freeTree(node->right); delete node; — in that "
    "order, always",
    "cpp_tree",
    tuple(
        (f"Build the complete tree {{{_seq(v)}}} with new, linking each "
         f"position to the two below it. Print the root value, the depth, "
         f"and the total, then free it from the bottom up.",
         {"values": list(v)})
        for v in _TREES
    ),
)


CPP2_PAGES: tuple[Page, ...] = (
    VECTOR_PAGE, MAP_PAGE, SET_PAGE, SORT_PAGE, ITER_PAGE,
    ADAPTER_PAGE, ALGO_PAGE, STRING_PAGE, NODE_PAGE, TREE_PAGE,
)
