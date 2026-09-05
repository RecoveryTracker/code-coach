"""Pages 329-338: node objects.

These close the one gap an audit of the solution bank actually found. The
workbook taught every algorithm the interview patterns need and never once
taught the object they run on: before these pages there was not a single
`.val` access in six and a half thousand Python answers. Fifteen of the
hundred and four solutions open with a node class, so the gap was not
academic. You could know exactly what to do on Merge Two Sorted Lists and
still stall on `dummy = ListNode(0)`.

The algorithms here are deliberately ones already met. Reversing, two
pointers, depth, level order: all of them appeared earlier against lists
and tuples. Doing them again against nodes is the translation that was
missing, and the repetition is the point rather than a defect.

The last page is a mop-up of the three other things the same audit turned
up: heapify, isdigit, isalnum.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

PYTHON = ("python",)


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
        languages=PYTHON,
        tier="advanced",
    )


def _seq(items) -> str:
    return ", ".join(str(n) for n in items)


def _tree_text(values) -> str:
    """The level-order list as text, None spelled out.

    The prompt has to carry the whole tree. A page that says "the tree
    below" with the tree only in the answer is not answerable, which is a
    mistake these pages inherited the fix for.
    """
    return "[" + ", ".join("None" if v is None else str(v) for v in values) + "]"


# ── 329. Making a chain ──────────────────────────────────────

_CHAINS = (
    (3, 1, 4), (5, 2, 9), (1, 2, 3, 4), (7, 7, 3), (2, 8, 5, 1),
    (9, 4), (6, 1, 8, 2), (4, 4, 4), (1, 5, 9, 2, 6), (8, 3),
    (2, 7, 1, 8), (5, 5, 3, 1), (3, 6, 9), (1, 4, 1, 5), (7, 2, 8, 3),
    (9, 9, 1), (2, 4, 6, 8), (5, 1, 3), (6, 6, 2, 7), (1, 8, 4, 2, 9),
)

BUILD_PAGE = _page(
    "node-build", 329, "Making a chain out of a list",
    "A node holds a value and a pointer at the next one. Build the chain "
    "with a dummy head and a tail you keep moving, then print it and the "
    "value at the front.",
    "build([3, 1, 4]) links three nodes into 3 -> 1 -> 4, and head.val "
    "is 3 while head.next.val is 1",
    "node_build",
    tuple(
        (f"Build a chain from [{_seq(v)}], print it as an arrow list, then "
         f"print the head value.", {"values": list(v)})
        for v in _CHAINS
    ),
)


# ── 330. Walking to the end ──────────────────────────────────

_WALKS = (
    ((3, 1, 4, 1, 5), "count"), ((2, 7, 1, 8), "sum"),
    ((1, 9, 3), "max"), ((5, 2, 8), "last"),
    ((6, 6, 2, 7, 1), "count"), ((4, 4, 4), "sum"),
    ((2, 5, 9, 1), "max"), ((7, 3, 6), "last"),
    ((9, 1, 8, 2, 4), "count"), ((1, 2, 3, 4), "sum"),
    ((3, 8, 5), "max"), ((2, 9, 4), "last"),
    ((5, 1, 3, 7), "count"), ((6, 2, 8), "sum"),
    ((1, 4, 9, 2), "max"), ((8, 5, 1), "last"),
    ((2, 2, 6, 3), "count"), ((9, 4, 7), "sum"),
    ((4, 7, 2, 9), "max"), ((3, 6, 1, 5), "last"),
)

_WALK_WORDS = {
    "count": "count the nodes",
    "sum": "add up every value",
    "max": "find the largest value",
    "last": "find the value in the last node",
}

WALK_PAGE = _page(
    "node-walk", 330, "Walking a chain to the end",
    "The loop that every chain problem starts with: hold a node, do "
    "something with node.val, move to node.next, stop at None.",
    "node = head; while node is not None: total += node.val; node = "
    "node.next — and the loop ends because the last next is None",
    "node_walk",
    tuple(
        (f"Build [{_seq(v)}] into a chain, then walk it to "
         f"{_WALK_WORDS[w]}. Print the answer.", {"values": list(v), "want": w})
        for v, w in _WALKS
    ),
)


# ── 331. Turning a chain around ──────────────────────────────

_REVERSALS = (
    (1, 2, 3), (3, 1, 4, 1), (5, 2, 9), (7, 3), (2, 8, 5, 1),
    (9, 4, 6), (1, 2, 3, 4, 5), (6, 1, 8), (4, 9, 2), (8, 3, 7),
    (2, 7, 1, 8), (5, 5, 3), (3, 6, 9, 2), (1, 4, 5), (7, 2, 8),
    (9, 1, 2), (2, 4, 6, 8), (5, 1, 3), (6, 2, 7), (1, 8, 4, 2),
)

REVERSE_PAGE = _page(
    "node-reverse", 331, "Turning a chain around",
    "Three pointers and no new nodes. Remember where you are going before "
    "you point backwards, or you lose the rest of the chain.",
    "nxt = cur.next (save it first); cur.next = prev; prev = cur; cur = "
    "nxt — four lines, and the order of them is the whole exercise",
    "node_reverse",
    tuple(
        (f"Reverse the chain [{_seq(v)}] in place and print it. The answer "
         f"is a chain that ends where this one starts.", {"values": list(v)})
        for v in _REVERSALS
    ),
)


# ── 332. The dummy head ──────────────────────────────────────

_MERGES = (
    ((1, 4, 7), (2, 3, 9)), ((1, 3, 5), (2, 4, 6)), ((2, 6), (1, 5, 8)),
    ((1, 2, 9), (3, 4, 5)), ((4, 8), (1, 6, 9)), ((3, 7), (2, 5, 8)),
    ((1, 5), (2, 3, 4)), ((2, 4, 9), (1, 6, 7)), ((5, 6), (1, 3, 8)),
    ((1, 7), (4, 5, 9)), ((2, 8), (3, 6, 7)), ((1, 4), (2, 5, 6)),
    ((3, 9), (1, 2, 8)), ((6, 7), (2, 4, 9)), ((1, 8), (3, 5, 7)),
    ((2, 3), (1, 4, 8)), ((5, 9), (2, 6, 7)), ((1, 6), (3, 4, 9)),
    ((4, 7), (1, 5, 8)), ((2, 9), (3, 6, 8)),
)

MERGE_PAGE = _page(
    "node-dummy", 332, "The spare head that saves the special case",
    "Build the answer onto a node you throw away. Without it every append "
    "needs an is-the-list-empty check first, and that check is where the "
    "bugs live.",
    "dummy = ListNode(); tail = dummy; tail.next = node; tail = "
    "tail.next; and at the end the answer is dummy.next, never dummy",
    "node_dummy",
    tuple(
        (f"Merge the sorted chains [{_seq(a)}] and [{_seq(b)}] into one "
         f"sorted chain and print it. Build it onto a dummy head.",
         {"left": list(a), "right": list(b)})
        for a, b in _MERGES
    ),
)


# ── 333. Fast and slow ───────────────────────────────────────

_MIDDLES = (
    (1, 2, 3), (1, 2, 3, 4, 5), (3, 1, 4, 1, 5), (2, 7, 1),
    (6, 6, 2, 7, 1), (9, 1, 8, 2, 4), (5, 2, 8), (1, 4, 9, 2, 6),
    (7, 3, 6), (2, 5, 9, 1, 3),
)

_NTHS = (
    ((1, 2, 3, 4, 5), 2), ((3, 1, 4, 1, 5), 1), ((2, 7, 1, 8), 3),
    ((9, 4, 6, 2), 2), ((5, 1, 3, 7, 9), 4), ((6, 2, 8), 2),
    ((1, 5, 9, 2, 6), 3), ((8, 3, 7, 1), 1), ((4, 9, 2, 5), 2),
    ((2, 6, 1, 7, 3), 5 - 1),
)

TWO_POINTER_PAGE = _page(
    "node-two-pointers", 333, "One pointer twice as fast as the other",
    "You cannot ask a chain how long it is without walking it, so send two "
    "pointers instead. One at double speed finds the middle; one started "
    "n ahead finds the nth from the end. Both in a single pass.",
    "while fast is not None and fast.next is not None: slow = slow.next; "
    "fast = fast.next.next",
    "node_two_pointers",
    tuple(
        (f"Find the middle node of [{_seq(v)}] with a fast and a slow "
         f"pointer, and print its value.",
         {"values": list(v), "want": "middle"})
        for v in _MIDDLES
    ) + tuple(
        (f"Find the node {n} from the end of [{_seq(v)}] by starting one "
         f"pointer {n} ahead, and print its value.",
         {"values": list(v), "want": "nth", "n": n})
        for v, n in _NTHS
    ),
)


# ── 334. Dropping a node ─────────────────────────────────────

_DEDUPES = (
    (1, 1, 2, 3), (1, 2, 2, 3), (3, 3, 3, 4), (1, 1, 2, 2, 3),
    (2, 2, 5), (1, 2, 3, 3), (4, 4, 6, 7), (5, 5, 5, 8),
    (1, 1, 4, 4, 9), (2, 3, 3, 6),
)

_DROPS = (
    ((1, 2, 6, 3, 6), 6), ((3, 1, 4, 1, 5), 1), ((2, 7, 2, 8), 2),
    ((9, 4, 9, 2), 9), ((5, 1, 3, 1), 1), ((6, 2, 6, 8), 6),
    ((1, 5, 5, 2), 5), ((8, 3, 7, 3), 3), ((4, 4, 2, 5), 4),
    ((2, 6, 1, 6, 3), 6),
)

REMOVE_PAGE = _page(
    "node-remove", 334, "Dropping a node out of a chain",
    "Removing means pointing over it. You have to stand on the node before "
    "the one you want gone, which is why the dummy head turns up again the "
    "moment the head itself might go.",
    "node.next = node.next.next skips the node in between, which is all "
    "that removing means when nothing else points at it",
    "node_remove",
    tuple(
        (f"Remove the neighbouring duplicates from the sorted chain "
         f"[{_seq(v)}] and print what is left.",
         {"values": list(v), "want": "dedupe"})
        for v in _DEDUPES
    ) + tuple(
        (f"Remove every {d} from the chain [{_seq(v)}] and print what is "
         f"left. Use a dummy head so the first node is not a special case.",
         {"values": list(v), "want": "drop", "drop": d})
        for v, d in _DROPS
    ),
)


# ── 335-337. Trees ───────────────────────────────────────────

_TREES = (
    (3, 9, 20, None, None, 15, 7),
    (5, 3, 8, 1, 4, 7, 9),
    (1, 2, 3, 4, 5, 6, 7),
    (10, 5, 15, 3, 7, 12, 18),
    (2, 1, 3),
    (8, 4, 12, 2, 6, 10, 14),
    (6, 2, 9, 1, 4),
    (7, 3, 11, 1, 5, 9, 13),
    (4, 2, 6, 1, 3, 5, 7),
    (9, 5, 12, 3, 7),
    (20, 10, 30, 5, 15, 25, 35),
    (1, 2, 3, 4, None, None, 5),
    (15, 9, 21, 4, 12, 18, 25),
    (3, 1, 5, None, 2, 4, 6),
    (11, 6, 16, 3, 8, 13, 19),
    (2, 7, 5, 1, 6, None, 9),
    (12, 7, 17, 4, 9, 14, 20),
    (5, 2, 8, 1, 3, 6, 10),
    (30, 15, 45, 8, 20, 40, 50),
    (1, 3, 2, 5, 4, None, 9),
)

TREE_BUILD_PAGE = _page(
    "tree-build", 335, "A tree made of nodes",
    "A tree arrives as a level-order list with None where a child is "
    "missing, which is how it is written down everywhere. Build it with a "
    "queue, then measure how deep it goes.",
    "build([3, 9, 20, None, None, 15, 7]) is a root of 3 with depth 3",
    "tree_build",
    tuple(
        (f"Build the tree {_tree_text(v)} from its level-order list, then "
         f"print the root value and the depth.", {"values": list(v)})
        for v in _TREES
    ),
)

_WALK_ORDERS = ("inorder", "preorder", "postorder", "invert")

_TREE_WALKS = tuple(
    (_TREES[i], _WALK_ORDERS[i % 4]) for i in range(16)
)

_PATH_SUMS = (
    (_TREES[0], 12), (_TREES[1], 9), (_TREES[3], 18), (_TREES[5], 14),
)

_WALK_WORDS_TREE = {
    "inorder": "left, then the node, then right",
    "preorder": "the node, then left, then right",
    "postorder": "left, then right, then the node",
}

TREE_WALK_PAGE = _page(
    "tree-walk", 336, "Visiting every node in a tree",
    "Three orders and one rewrite. The recursion is the same three lines "
    "every time and only their order changes, which is the whole idea.",
    "inorder visits left, then the node, then right; preorder moves that "
    "one line to the top and changes everything",
    "tree_walk",
    tuple(
        ((f"Walk the tree {_tree_text(v)} in {w} order ({_WALK_WORDS_TREE[w]}) "
          f"and print the values on one line.")
         if w != "invert" else
         (f"Print the inorder walk of the tree {_tree_text(v)}, then swap "
          f"every left and right child and print the inorder walk again."),
         {"values": list(v), "want": w})
        for v, w in _TREE_WALKS
    ) + tuple(
        (f"Is there a path from the root of {_tree_text(v)} down to a leaf "
         f"whose values add up to {t}? Print True or False.",
         {"values": list(v), "want": "path_sum", "target": t})
        for v, t in _PATH_SUMS
    ),
)

TREE_LEVEL_PAGE = _page(
    "tree-levels", 337, "A tree, one row at a time",
    "A queue instead of recursion, and the trick that makes the rows come "
    "out separately: before you start a row, ask how many nodes are in the "
    "queue right now, and take exactly that many.",
    "for _ in range(len(queue)): node = queue.popleft() — asking the "
    "length first is what keeps the rows from running together",
    "tree_levels",
    tuple(
        (f"Print the tree {_tree_text(v)} one row per line, left to right.",
         {"values": list(v), "want": "plain"})
        for v in _TREES[:10]
    ) + tuple(
        (f"Print the tree {_tree_text(v)} one row per line, but reverse "
         f"every second row so the direction zigzags down the tree.",
         {"values": list(v), "want": "zigzag"})
        for v in _TREES[10:]
    ),
)


# ── 338. Three small things ──────────────────────────────────

_HEAPS = (
    ((5, 1, 8, 3, 9), 2), ((7, 2, 6, 4), 3), ((9, 3, 1, 7, 5), 2),
    ((4, 8, 2, 6), 2), ((6, 1, 9, 2, 8), 3),
)

_BIG_HEAPS = (
    ((1, 9, 3, 7, 5), 2), ((2, 8, 4, 6), 3), ((3, 1, 9, 5, 7), 2),
    ((4, 2, 8, 6), 2), ((5, 3, 9, 1, 7), 3),
)

_DIGIT_TEXTS = ("a1b2c3", "3 apples", "x9y8", "room 402", "no7go8")

_ALNUM_TEXTS = (
    "A man, a plan, a canal: Panama",
    "race a car",
    "Was it a cat I saw?",
    "hello, world!",
    "No lemon, no melon",
)

TOOLKIT_PAGE = _page(
    "node-toolkit", 338, "Heapify, isdigit, isalnum",
    "Three things the solution bank uses that nothing else here has asked "
    "for. heapify turns a list into a heap in place and in linear time; "
    "isdigit and isalnum are the character tests that decide what a parser "
    "or a palindrome check keeps.",
    "heapq.heapify(items) reorders items in place, no return value",
    "node_toolkit",
    tuple(
        (f"Heapify [{_seq(v)}] in place, pop the {t} smallest and print "
         f"them on one line, then print how many are left.",
         {"values": list(v), "want": "heapify", "take": t})
        for v, t in _HEAPS
    ) + tuple(
        (f"Print the {t} largest of [{_seq(v)}] on one line, using a heap "
         f"of negated values.",
         {"values": list(v), "want": "heap_largest", "take": t})
        for v, t in _BIG_HEAPS
    ) + tuple(
        (f"Split {s!r} with isdigit: print the digits, then everything "
         f"else, each on its own line.",
         {"text": s, "want": "isdigit"})
        for s in _DIGIT_TEXTS
    ) + tuple(
        (f"Keep only the letters and digits of {s!r}, lowercased. Print "
         f"what is left, then whether it reads the same backwards.",
         {"text": s, "want": "isalnum"})
        for s in _ALNUM_TEXTS
    ),
)


NODE_PAGES: tuple[Page, ...] = (
    BUILD_PAGE,
    WALK_PAGE,
    REVERSE_PAGE,
    MERGE_PAGE,
    TWO_POINTER_PAGE,
    REMOVE_PAGE,
    TREE_BUILD_PAGE,
    TREE_WALK_PAGE,
    TREE_LEVEL_PAGE,
    TOOLKIT_PAGE,
)
