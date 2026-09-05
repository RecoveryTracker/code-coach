"""Pages 342-349: C, and the memory it never asked for.

The C solutions in the bank call malloc fifty times, sizeof fifty times and
free forty times. The seventy-two C pages before these called none of them.
That is the largest gap the coverage audit found in any of the seven
languages, and the least defensible: allocation is not a corner of C, it is
most of what writing C consists of.

Eight pages, in the order the ideas need each other. Ask for memory and
give it back. Count a thing that does not know its own length. Zero it,
copy it. Return a count through a pointer, which is the shape every
LeetCode signature in C has. Then a struct with a pointer in it, and the
arrow, twice: once for a chain and once for a tree.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

C_ONLY = ("c",)


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
        languages=C_ONLY,
        tier="advanced",
    )


def _seq(items) -> str:
    return ", ".join(str(n) for n in items)


def _words(items) -> str:
    return ", ".join(f'"{w}"' for w in items)


# ── 342. malloc and free ─────────────────────────────────────

_ALLOCS = (
    (5, 2, 3), (4, 1, 2), (6, 0, 5), (3, 10, -2), (7, 1, 1),
    (5, 100, -10), (4, 3, 7), (8, 2, 2), (6, 50, -5), (3, 9, 4),
    (5, 1, 6), (7, 0, 3), (4, 20, -4), (6, 5, 5), (3, 2, 9),
    (8, 1, 3), (5, 40, -8), (4, 6, 6), (7, 3, 2), (6, 12, -1),
)

MALLOC_PAGE = _page(
    "c-malloc", 342, "Asking for memory and giving it back",
    "malloc takes a number of bytes, not a number of items, which is why "
    "it is always written as a count times sizeof something. It hands back "
    "a pointer or NULL, and every one of them has to reach a free.",
    "int *items = malloc(n * sizeof(int)); and at the end, free(items);",
    "c_malloc",
    tuple(
        (f"Allocate room for {n} ints. Fill position i with {s} + i * {k}, "
         f"print them space separated, then print the total. Free it.",
         {"n": n, "start": s, "step": k})
        for n, s, k in _ALLOCS
    ),
)


# ── 343. Counting without a length ───────────────────────────

_ARRAYS = (
    (4, 8, 15, 16, 23), (3, 1, 4, 1, 5), (2, 7, 1, 8), (9, 4, 6),
    (5, 5, 3, 1, 9), (1, 2, 3, 4, 5, 6), (8, 3, 7), (2, 4, 6, 8),
    (7, 1, 9, 3), (6, 6, 2, 7, 1), (5, 2, 8), (1, 9, 3, 7, 5),
    (4, 2, 9, 6), (3, 8, 5, 2), (9, 1, 2, 4, 8), (2, 5, 9, 1),
    (7, 3, 6, 2), (1, 4, 1, 5, 9), (8, 2, 6, 4), (5, 9, 1, 3, 7),
)

SIZEOF_PAGE = _page(
    "c-sizeof", 343, "How many, when nothing records how many",
    "An array in C does not know its length. sizeof the array over sizeof "
    "one element gives it, but only where the array still is one: pass it "
    "to a function and it decays to a pointer, sizeof answers about the "
    "pointer, and the count you get back is nonsense. This is why every C "
    "function in the bank takes a size alongside the array.",
    "int n = (int)(sizeof(items) / sizeof(items[0])); works here and not "
    "one line further down, inside a function",
    "c_sizeof",
    tuple(
        (f"Take the array {{{_seq(v)}}}. Print its length worked out with "
         f"sizeof, then print whether a function given the array agrees "
         f"(1 for yes, 0 for no), then print the total.",
         {"values": list(v)})
        for v in _ARRAYS
    ),
)


# ── 344. calloc and memcpy ───────────────────────────────────

_COPIES = (
    (3, 1, 4, 1, 5), (2, 7, 1, 8), (9, 4, 6), (5, 5, 3, 1),
    (1, 2, 3, 4), (8, 3, 7, 2), (6, 1, 9), (2, 4, 6, 8, 1),
    (7, 2, 5), (3, 9, 1, 6), (4, 8, 2), (5, 1, 7, 3),
    (9, 6, 2, 4), (1, 5, 8), (2, 3, 9, 7), (6, 4, 1, 8),
    (3, 7, 2, 5), (8, 1, 6), (4, 9, 3, 2), (7, 5, 1, 9),
)

CALLOC_PAGE = _page(
    "c-calloc", 344, "Zeroed memory, and copying a block",
    "calloc takes the count and the size separately and hands back memory "
    "that is already zero, which malloc does not promise. memcpy moves a "
    "block of bytes, so it takes bytes too, which means sizeof again.",
    "int *zeroed = calloc(n, sizeof(int)); then memcpy(zeroed, source, "
    "n * sizeof(int));",
    "c_calloc",
    tuple(
        (f"calloc room for {len(v)} ints and print their total, which "
         f"should be 0. Then memcpy {{{_seq(v)}}} into it and print what is "
         f"there. Free it.", {"values": list(v)})
        for v in _COPIES
    ),
)


# ── 345. The out-parameter ───────────────────────────────────

_PICKS = (
    ((3, 9, 2, 8, 5), 4), ((1, 7, 4, 6), 3), ((5, 2, 9, 1, 8), 4),
    ((6, 3, 7, 2), 4), ((2, 8, 1, 9, 4), 5), ((7, 1, 5, 3), 4),
    ((9, 2, 6, 4, 1), 3), ((4, 8, 2, 7), 5), ((1, 6, 3, 9, 5), 4),
    ((8, 3, 1, 6), 4), ((2, 9, 5, 1, 7), 5), ((5, 4, 8, 2), 4),
    ((3, 7, 1, 9, 6), 5), ((6, 2, 4, 8), 3), ((1, 5, 9, 3, 7), 4),
    ((7, 4, 2, 6), 5), ((9, 1, 8, 3, 5), 6), ((2, 6, 4, 9), 5),
    ((4, 1, 7, 5, 8), 4), ((8, 5, 2, 6), 4),
)

OUT_PARAM_PAGE = _page(
    "c-out-param", 345, "Returning a count through a pointer",
    "A C function can only return one thing, and an array is really two: "
    "the memory and how much of it is used. So the count goes out through "
    "a pointer the caller supplies. Every array-returning signature in the "
    "solution bank is this shape, and the caller frees what comes back.",
    "int *pick(int *nums, int numsSize, int over, int *returnSize) writes "
    "*returnSize = kept; and returns the memory",
    "c_out_param",
    tuple(
        (f"Write a function that keeps everything in {{{_seq(v)}}} greater "
         f"than {o}, returning the memory and writing how many through a "
         f"pointer. Print the count, then the values. Free it.",
         {"values": list(v), "over": o})
        for v, o in _PICKS
    ),
)


# ── 346. A struct, a pointer, and the arrow ──────────────────

_CHAIN_ROWS = (
    ((3, 1, 4), "sum"), ((2, 7, 1, 8), "count"), ((1, 9, 3), "max"),
    ((5, 2, 8), "sum"), ((6, 6, 2, 7), "count"), ((2, 5, 9), "max"),
    ((4, 1, 7), "sum"), ((9, 1, 8, 2), "count"), ((3, 8, 5), "max"),
    ((7, 3, 6), "sum"), ((1, 2, 3, 4), "count"), ((2, 9, 4), "max"),
    ((5, 1, 3), "sum"), ((8, 2, 6, 1), "count"), ((1, 4, 9), "max"),
    ((6, 2, 8), "sum"), ((3, 6, 1, 5), "count"), ((4, 7, 2), "max"),
    ((9, 4, 7), "sum"), ((2, 2, 6, 3), "count"),
)

_CHAIN_WORDS = {
    "sum": "add up every value",
    "count": "count the nodes",
    "max": "find the largest value",
}

LIST_NODE_PAGE = _page(
    "c-list-node", 346, "A struct, a pointer, and the arrow",
    "A node is a struct holding a value and a pointer at another one of "
    "itself. Every node comes from its own malloc, so every node needs its "
    "own free — and you have to save the next pointer before freeing, "
    "because after free the node is gone and so is the way onward.",
    "struct ListNode { int val; struct ListNode *next; }; and node->val "
    "is (*node).val written the way everyone writes it",
    "c_list_node",
    tuple(
        (f"Build a chain of malloc'd nodes from {{{_seq(v)}}}. Print it "
         f"with arrows, then {_CHAIN_WORDS[w]} and print that. Free every "
         f"node.", {"values": list(v), "want": w})
        for v, w in _CHAIN_ROWS
    ),
)


# ── 347. Rebuilding a chain ──────────────────────────────────

_REVERSES = (
    (1, 2, 3), (3, 1, 4), (5, 2, 9), (2, 8, 5, 1), (9, 4, 6),
    (1, 2, 3, 4), (6, 1, 8), (4, 9, 2), (8, 3, 7), (2, 7, 1, 8),
)

_MERGES = (
    ((1, 4, 7), (2, 3, 9)), ((1, 3, 5), (2, 4, 6)), ((2, 6), (1, 5, 8)),
    ((1, 2, 9), (3, 4, 5)), ((4, 8), (1, 6, 9)), ((3, 7), (2, 5, 8)),
    ((1, 5), (2, 3, 4)), ((2, 4, 9), (1, 6, 7)), ((5, 6), (1, 3, 8)),
    ((1, 7), (4, 5, 9)),
)

LIST_OPS_PAGE = _page(
    "c-list-ops", 347, "Rebuilding a chain that you also have to free",
    "The same two exercises as the Python pages, with the part Python does "
    "for you put back. Reversing hands you a new head and the old one is "
    "now the tail, so free from the new head. Merging with a dummy on the "
    "stack costs no malloc and no free, which is the reason to put it "
    "there rather than allocate one.",
    "struct ListNode dummy; dummy.next = NULL; — a dummy on the stack "
    "needs no free, and &dummy is the tail to start from",
    "c_list_ops",
    tuple(
        (f"Reverse a malloc'd chain built from {{{_seq(v)}}} in place, "
         f"print it with arrows, then free it from its new head.",
         {"values": list(v), "want": "reverse"})
        for v in _REVERSES
    ) + tuple(
        (f"Merge the sorted chains {{{_seq(a)}}} and {{{_seq(b)}}} into one "
         f"chain using a dummy node on the stack. Print it, then free it.",
         {"left": list(a), "right": list(b), "want": "merge"})
        for a, b in _MERGES
    ),
)


# ── 348. Two pointers per node ───────────────────────────────

_TREES = (
    (3, 9, 20, 15, 7), (5, 3, 8, 1, 4, 7, 9), (1, 2, 3, 4),
    (10, 5, 15, 3, 7, 12, 18), (2, 1, 3, 6), (8, 4, 12, 2, 6),
    (6, 2, 9, 1, 4, 8), (7, 3, 11, 1, 5, 9, 13), (4, 2, 6, 1),
    (9, 5, 12, 3, 7, 11), (20, 10, 30, 5, 15), (1, 2, 3, 4, 5, 6, 7),
    (15, 9, 21, 4, 12), (3, 1, 5, 2, 4, 6), (11, 6, 16, 3, 8),
    (2, 7, 5, 1, 6, 9), (12, 7, 17, 4, 9, 14), (5, 2, 8, 1, 3),
    (30, 15, 45, 8, 20, 40), (1, 3, 2, 5, 4),
)

TREE_NODE_PAGE = _page(
    "c-tree-node", 348, "Two pointers per node",
    "The same struct with one more pointer in it. Freeing a tree has to "
    "happen from the bottom up — free the node first and the pointers to "
    "its children go with it — which is why freeTree recurses before it "
    "frees rather than after.",
    "struct TreeNode { int val; struct TreeNode *left; struct TreeNode "
    "*right; }; and freeTree goes down before it frees",
    "c_tree_node",
    tuple(
        (f"Build the complete tree {{{_seq(v)}}} node by node with malloc, "
         f"linking each position to the two below it. Print the root, the "
         f"depth, and the total of every value. Free the tree.",
         {"values": list(v)})
        for v in _TREES
    ),
)


# ── 349. Handing a function to a function ────────────────────

_SORTS = (
    (5, 1, 4, 2), (3, 9, 1, 6), (8, 2, 7, 4), (6, 3, 9, 1, 5),
    (2, 8, 4, 6), (9, 1, 5, 3), (7, 4, 8, 2), (1, 6, 2, 9, 3),
    (4, 7, 1, 8), (5, 2, 9, 6),
)

_WORD_SETS = (
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

QSORT_PAGE = _page(
    "c-qsort", 349, "Handing a function to a function",
    "qsort does not know what it is sorting. You give it the memory, how "
    "many, how big each one is, and a function that compares two of them "
    "through void pointers — which you have to cast back yourself, because "
    "nothing else knows the type either.",
    "static int byValue(const void *a, const void *b) { return *(const "
    "int *)a - *(const int *)b; } and qsort(items, n, sizeof(int), byValue)",
    "c_qsort",
    tuple(
        (f"Sort {{{_seq(v)}}} ascending with qsort and a comparator you "
         f"write, then print the result.",
         {"values": list(v), "want": "ints"})
        for v in _SORTS
    ) + tuple(
        (f"Sort {{{_words(w)}}} by length, and alphabetically where the "
         f"lengths tie. The comparator gets pointers to the pointers, so "
         f"cast accordingly. Print the result.",
         {"words": list(w), "want": "words"})
        for w in _WORD_SETS
    ),
)


C_PAGES: tuple[Page, ...] = (
    MALLOC_PAGE,
    SIZEOF_PAGE,
    CALLOC_PAGE,
    OUT_PARAM_PAGE,
    LIST_NODE_PAGE,
    LIST_OPS_PAGE,
    TREE_NODE_PAGE,
    QSORT_PAGE,
)
