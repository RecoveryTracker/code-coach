"""Node objects: the shape every linked-list and tree problem hands you.

The workbook models chains and trees as Python lists and tuples, which is
why its tree pages have to draw the tree in the prompt. That is fine for
learning the algorithm and useless for the moment you sit down to a real
problem, because fifteen of the hundred and four solutions in the bank open
with a node class and reach straight for `.val` and `.next`. Before these
pages the workbook contained no `.val` access at all — not one, in six and
a half thousand answers. The algorithms were all there and the object they
run on was missing.

So these ten pages are the missing rung. The algorithms are mostly ones
already met on earlier tiers — reverse a sequence, walk it with two
pointers, measure a tree's depth — done again against nodes, because that
is the translation that was never drilled. The last page mops up three
small things the same audit found: heapify, isdigit, isalnum.

Python only, and every program prints an answer worked out twice — once by
the emitted code and once here, independently.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("node_build", "making a chain out of a list"),
    Shape("node_walk", "walking a chain to the end"),
    Shape("node_reverse", "turning a chain around"),
    Shape("node_dummy", "the spare head that saves the special case"),
    Shape("node_two_pointers", "one pointer twice as fast as the other"),
    Shape("node_remove", "dropping a node out of a chain"),
    Shape("tree_build", "a tree made of nodes"),
    Shape("tree_walk", "visiting every node in a tree"),
    Shape("tree_levels", "a tree, one row at a time"),
    Shape("node_toolkit", "heapify, isdigit, isalnum"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return "[" + ", ".join(str(n) for n in items) + "]"


def _strs(items) -> str:
    return "[" + ", ".join(repr(s) for s in items) + "]"


# The node classes. Written out in the program rather than imported,
# exactly as every LeetCode solution has to, so the fingers learn it.
_LIST_NODE = (
    "class ListNode:",
    "    def __init__(self, val=0, next=None):",
    "        self.val = val",
    "        self.next = next",
    "",
)

_TREE_NODE = (
    "class TreeNode:",
    "    def __init__(self, val=0, left=None, right=None):",
    "        self.val = val",
    "        self.left = left",
    "        self.right = right",
    "",
)

_BUILD_CHAIN = (
    "def build(values):",
    "    dummy = ListNode()",
    "    tail = dummy",
    "    for v in values:",
    "        tail.next = ListNode(v)",
    "        tail = tail.next",
    "    return dummy.next",
    "",
)

_CHAIN_TEXT = (
    "def as_text(head):",
    "    out = []",
    "    node = head",
    "    while node is not None:",
    "        out.append(str(node.val))",
    "        node = node.next",
    "    return ' -> '.join(out)",
    "",
)


# ── 329. Making a chain ──────────────────────────────────────


def _build(a: dict) -> str:
    return _lines(
        *_LIST_NODE,
        *_BUILD_CHAIN,
        *_CHAIN_TEXT,
        f"head = build({_nums(a['values'])})",
        "print(as_text(head))",
        "print(head.val)",
    )


# ── 330. Walking to the end ──────────────────────────────────


def _walk(a: dict) -> str:
    want = a["want"]
    body = {
        "count": ("total = 0", "    total += 1", "total"),
        "sum": ("total = 0", "    total += node.val", "total"),
        "max": ("total = None", "    if total is None or node.val > total:\n"
                "        total = node.val", "total"),
        "last": ("total = None", "    total = node.val", "total"),
    }[want]
    return _lines(
        *_LIST_NODE,
        *_BUILD_CHAIN,
        f"head = build({_nums(a['values'])})",
        body[0],
        "node = head",
        "while node is not None:",
        body[1],
        "    node = node.next",
        f"print({body[2]})",
    )


# ── 331. Turning a chain around ──────────────────────────────


def _reverse(a: dict) -> str:
    return _lines(
        *_LIST_NODE,
        *_BUILD_CHAIN,
        *_CHAIN_TEXT,
        f"head = build({_nums(a['values'])})",
        "prev = None",
        "cur = head",
        "while cur is not None:",
        "    nxt = cur.next",
        "    cur.next = prev",
        "    prev = cur",
        "    cur = nxt",
        "print(as_text(prev))",
    )


# ── 332. The dummy head ──────────────────────────────────────


def _dummy(a: dict) -> str:
    return _lines(
        *_LIST_NODE,
        *_BUILD_CHAIN,
        *_CHAIN_TEXT,
        f"left = build({_nums(a['left'])})",
        f"right = build({_nums(a['right'])})",
        "dummy = ListNode()",
        "tail = dummy",
        "while left is not None and right is not None:",
        "    if left.val <= right.val:",
        "        tail.next = left",
        "        left = left.next",
        "    else:",
        "        tail.next = right",
        "        right = right.next",
        "    tail = tail.next",
        "tail.next = left if left is not None else right",
        "print(as_text(dummy.next))",
    )


# ── 333. Fast and slow ───────────────────────────────────────


def _two_pointers(a: dict) -> str:
    if a["want"] == "middle":
        return _lines(
            *_LIST_NODE,
            *_BUILD_CHAIN,
            f"head = build({_nums(a['values'])})",
            "slow = head",
            "fast = head",
            "while fast is not None and fast.next is not None:",
            "    slow = slow.next",
            "    fast = fast.next.next",
            "print(slow.val)",
        )
    return _lines(
        *_LIST_NODE,
        *_BUILD_CHAIN,
        f"head = build({_nums(a['values'])})",
        f"n = {a['n']}",
        "lead = head",
        "for _ in range(n):",
        "    lead = lead.next",
        "trail = head",
        "while lead is not None:",
        "    lead = lead.next",
        "    trail = trail.next",
        "print(trail.val)",
    )


# ── 334. Dropping a node ─────────────────────────────────────


def _remove(a: dict) -> str:
    if a["want"] == "dedupe":
        return _lines(
            *_LIST_NODE,
            *_BUILD_CHAIN,
            *_CHAIN_TEXT,
            f"head = build({_nums(a['values'])})",
            "node = head",
            "while node is not None and node.next is not None:",
            "    if node.val == node.next.val:",
            "        node.next = node.next.next",
            "    else:",
            "        node = node.next",
            "print(as_text(head))",
        )
    return _lines(
        *_LIST_NODE,
        *_BUILD_CHAIN,
        *_CHAIN_TEXT,
        f"head = build({_nums(a['values'])})",
        f"drop = {a['drop']}",
        "dummy = ListNode(0, head)",
        "node = dummy",
        "while node.next is not None:",
        "    if node.next.val == drop:",
        "        node.next = node.next.next",
        "    else:",
        "        node = node.next",
        "print(as_text(dummy.next))",
    )


# ── 335. A tree made of nodes ────────────────────────────────
#
# The tree arrives as a level-order list with None for a missing child,
# which is how LeetCode writes one down. Building it from that list is
# half the point of the page.

_BUILD_TREE = (
    "def build(values):",
    "    if not values or values[0] is None:",
    "        return None",
    "    root = TreeNode(values[0])",
    "    queue = [root]",
    "    i = 1",
    "    while queue and i < len(values):",
    "        node = queue.pop(0)",
    "        if i < len(values) and values[i] is not None:",
    "            node.left = TreeNode(values[i])",
    "            queue.append(node.left)",
    "        i += 1",
    "        if i < len(values) and values[i] is not None:",
    "            node.right = TreeNode(values[i])",
    "            queue.append(node.right)",
    "        i += 1",
    "    return root",
    "",
)


def _levels_literal(values) -> str:
    return "[" + ", ".join("None" if v is None else str(v) for v in values) + "]"


def _tree_build(a: dict) -> str:
    return _lines(
        *_TREE_NODE,
        *_BUILD_TREE,
        f"root = build({_levels_literal(a['values'])})",
        "",
        "def depth(node):",
        "    if node is None:",
        "        return 0",
        "    return 1 + max(depth(node.left), depth(node.right))",
        "",
        "print(root.val)",
        "print(depth(root))",
    )


# ── 336. Visiting every node ─────────────────────────────────


def _tree_walk(a: dict) -> str:
    want = a["want"]
    if want == "invert":
        return _lines(
            *_TREE_NODE,
            *_BUILD_TREE,
            f"root = build({_levels_literal(a['values'])})",
            "",
            "def invert(node):",
            "    if node is None:",
            "        return None",
            "    node.left, node.right = invert(node.right), invert(node.left)",
            "    return node",
            "",
            "def inorder(node, out):",
            "    if node is None:",
            "        return out",
            "    inorder(node.left, out)",
            "    out.append(str(node.val))",
            "    inorder(node.right, out)",
            "    return out",
            "",
            "print(' '.join(inorder(root, [])))",
            "print(' '.join(inorder(invert(root), [])))",
        )
    if want == "path_sum":
        return _lines(
            *_TREE_NODE,
            *_BUILD_TREE,
            f"root = build({_levels_literal(a['values'])})",
            f"target = {a['target']}",
            "",
            "def has_path(node, left):",
            "    if node is None:",
            "        return False",
            "    left = left - node.val",
            "    if node.left is None and node.right is None:",
            "        return left == 0",
            "    return has_path(node.left, left) or has_path(node.right, left)",
            "",
            "print(has_path(root, target))",
        )
    order = {
        "inorder": ("    walk(node.left, out)",
                    "    out.append(str(node.val))",
                    "    walk(node.right, out)"),
        "preorder": ("    out.append(str(node.val))",
                     "    walk(node.left, out)",
                     "    walk(node.right, out)"),
        "postorder": ("    walk(node.left, out)",
                      "    walk(node.right, out)",
                      "    out.append(str(node.val))"),
    }[want]
    return _lines(
        *_TREE_NODE,
        *_BUILD_TREE,
        f"root = build({_levels_literal(a['values'])})",
        "",
        "def walk(node, out):",
        "    if node is None:",
        "        return out",
        *order,
        "    return out",
        "",
        "print(' '.join(walk(root, [])))",
    )


# ── 337. One row at a time ───────────────────────────────────


def _tree_levels(a: dict) -> str:
    zigzag = a["want"] == "zigzag"
    body = [
        "from collections import deque",
        "",
        *_TREE_NODE,
        *_BUILD_TREE,
        f"root = build({_levels_literal(a['values'])})",
        "queue = deque([root]) if root is not None else deque()",
    ]
    if zigzag:
        body.append("flip = False")
    body += [
        "while queue:",
        "    row = []",
        "    for _ in range(len(queue)):",
        "        node = queue.popleft()",
        "        row.append(str(node.val))",
        "        if node.left is not None:",
        "            queue.append(node.left)",
        "        if node.right is not None:",
        "            queue.append(node.right)",
    ]
    if zigzag:
        body += [
            "    if flip:",
            "        row.reverse()",
            "    flip = not flip",
        ]
    body.append("    print(' '.join(row))")
    return _lines(*body)


# ── 338. Three small things ──────────────────────────────────


def _toolkit(a: dict) -> str:
    want = a["want"]
    if want == "heapify":
        return _lines(
            "import heapq",
            "",
            f"items = {_nums(a['values'])}",
            "heapq.heapify(items)",
            f"taken = [heapq.heappop(items) for _ in range({a['take']})]",
            "print(' '.join(str(n) for n in taken))",
            "print(len(items))",
        )
    if want == "heap_largest":
        return _lines(
            "import heapq",
            "",
            f"items = [-n for n in {_nums(a['values'])}]",
            "heapq.heapify(items)",
            f"taken = [-heapq.heappop(items) for _ in range({a['take']})]",
            "print(' '.join(str(n) for n in taken))",
        )
    if want == "isdigit":
        return _lines(
            f"text = {a['text']!r}",
            "digits = []",
            "letters = []",
            "for ch in text:",
            "    if ch.isdigit():",
            "        digits.append(ch)",
            "    else:",
            "        letters.append(ch)",
            "print(''.join(digits))",
            "print(''.join(letters))",
        )
    return _lines(
        f"text = {a['text']!r}",
        "kept = [ch.lower() for ch in text if ch.isalnum()]",
        "print(''.join(kept))",
        "print(''.join(kept) == ''.join(reversed(kept)))",
    )


_BUILDERS = {
    "node_build": _build,
    "node_walk": _walk,
    "node_reverse": _reverse,
    "node_dummy": _dummy,
    "node_two_pointers": _two_pointers,
    "node_remove": _remove,
    "tree_build": _tree_build,
    "tree_walk": _tree_walk,
    "tree_levels": _tree_levels,
    "node_toolkit": _toolkit,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out here with plain Python values, never by walking nodes.

    That independence is the whole point: these pages are about the object,
    so computing the answer with the object would be checking the program
    against itself. Lists, and recursion over tuples, are a different
    enough route to be worth something.

    The guards ask whether the data can demonstrate the page's point: a
    reversal that reads the same backwards, a merge that never interleaves,
    an invert that leaves the tree alone. Any of those would pass while
    proving nothing.
    """
    a = args
    if shape == "node_build":
        values = list(a["values"])
        if not values:
            raise ValueError("a chain needs at least one node")
        lines = [" -> ".join(str(v) for v in values), str(values[0])]
    elif shape == "node_walk":
        values = list(a["values"])
        want = a["want"]
        if not values:
            raise ValueError("a chain needs at least one node")
        if want == "max" and values[0] == max(values):
            raise ValueError(
                "the largest must not be the first, or stopping at the head "
                "would have given the same answer"
            )
        if want == "last" and len(values) < 2:
            raise ValueError("finding the last needs more than one node")
        got = {
            "count": len(values),
            "sum": sum(values),
            "max": max(values),
            "last": values[-1],
        }[want]
        lines = [str(got)]
    elif shape == "node_reverse":
        values = list(a["values"])
        backwards = values[::-1]
        if backwards == values:
            raise ValueError(
                "the chain must not read the same backwards, or reversing "
                "it would be indistinguishable from doing nothing"
            )
        lines = [" -> ".join(str(v) for v in backwards)]
    elif shape == "node_dummy":
        left, right = list(a["left"]), list(a["right"])
        if not left or not right:
            raise ValueError("merging needs two chains")
        for side in (left, right):
            if side != sorted(side):
                raise ValueError("each chain must already be sorted")
        merged = sorted(left + right)
        if merged == left + right or merged == right + left:
            raise ValueError(
                "the two chains must interleave, or the merge would be a "
                "join and the comparison would never be exercised"
            )
        lines = [" -> ".join(str(v) for v in merged)]
    elif shape == "node_two_pointers":
        values = list(a["values"])
        if a["want"] == "middle":
            if len(values) < 3:
                raise ValueError("a middle needs at least three nodes")
            lines = [str(values[len(values) // 2])]
        else:
            n = a["n"]
            if not 0 < n <= len(values):
                raise ValueError("n must land inside the chain")
            if n == len(values):
                raise ValueError(
                    "counting the whole chain from the end is the head, "
                    "which the lead pointer never had to move for"
                )
            lines = [str(values[len(values) - n])]
    elif shape == "node_remove":
        values = list(a["values"])
        if a["want"] == "dedupe":
            kept = [
                v for i, v in enumerate(values) if i == 0 or v != values[i - 1]
            ]
            if kept == values:
                raise ValueError(
                    "the chain must have a neighbouring repeat, or nothing "
                    "would be removed"
                )
        else:
            drop = a["drop"]
            if drop not in values:
                raise ValueError("the value to drop must be in the chain")
            kept = [v for v in values if v != drop]
            if not kept:
                raise ValueError("removing everything leaves nothing to print")
        lines = [" -> ".join(str(v) for v in kept)]
    elif shape in ("tree_build", "tree_walk", "tree_levels"):
        lines = _tree_expected(shape, a)
    elif shape == "node_toolkit":
        lines = _toolkit_expected(a)
    else:
        raise KeyError(shape)
    return NL.join(lines)


def _as_tree(values):
    """The level-order list as nested tuples: (val, left, right).

    Built by index arithmetic over a list rather than by linking objects,
    so it is a genuinely separate route to the same tree.
    """
    values = list(values)
    if not values or values[0] is None:
        return None
    kids: list[list] = [[] for _ in values]
    order = [0]
    i = 1
    while order and i < len(values):
        here = order.pop(0)
        for _ in range(2):
            if i < len(values) and values[i] is not None:
                kids[here].append(i)
                order.append(i)
            elif i < len(values):
                kids[here].append(None)
            i += 1

    def shape_at(idx):
        if idx is None:
            return None
        left = kids[idx][0] if len(kids[idx]) > 0 else None
        right = kids[idx][1] if len(kids[idx]) > 1 else None
        return (values[idx], shape_at(left), shape_at(right))

    return shape_at(0)


def _depth(node) -> int:
    if node is None:
        return 0
    return 1 + max(_depth(node[1]), _depth(node[2]))


def _visit(node, order) -> list:
    if node is None:
        return []
    val, left, right = node
    if order == "inorder":
        return _visit(left, order) + [val] + _visit(right, order)
    if order == "preorder":
        return [val] + _visit(left, order) + _visit(right, order)
    return _visit(left, order) + _visit(right, order) + [val]


def _flip(node):
    if node is None:
        return None
    val, left, right = node
    return (val, _flip(right), _flip(left))


def _rows(node) -> list:
    rows, level = [], [node] if node is not None else []
    while level:
        rows.append([n[0] for n in level])
        level = [k for n in level for k in (n[1], n[2]) if k is not None]
    return rows


def _leaf_sums(node, running=0) -> list:
    if node is None:
        return []
    val, left, right = node
    running += val
    if left is None and right is None:
        return [running]
    return _leaf_sums(left, running) + _leaf_sums(right, running)


def _tree_expected(shape: str, a: dict) -> list[str]:
    root = _as_tree(a["values"])
    if root is None:
        raise ValueError("a tree needs a root")
    if shape == "tree_build":
        if _depth(root) < 2:
            raise ValueError("a single node does not need building")
        return [str(root[0]), str(_depth(root))]
    if shape == "tree_levels":
        rows = _rows(root)
        if len(rows) < 2:
            raise ValueError("one row is not a level order")
        if a["want"] == "zigzag":
            flipped = [r[::-1] if i % 2 else r for i, r in enumerate(rows)]
            if flipped == rows:
                raise ValueError(
                    "zigzag must differ from plain level order, or the "
                    "reverse is doing nothing"
                )
            rows = flipped
        return [" ".join(str(v) for v in r) for r in rows]
    want = a["want"]
    if want == "invert":
        flipped = _flip(root)
        before = _visit(root, "inorder")
        after = _visit(flipped, "inorder")
        if before == after:
            raise ValueError(
                "inverting must change the inorder walk, or the tree is a "
                "mirror of itself and the page proves nothing"
            )
        return [
            " ".join(str(v) for v in before),
            " ".join(str(v) for v in after),
        ]
    if want == "path_sum":
        target = a["target"]
        sums = _leaf_sums(root)
        if len(set(sums)) < 2:
            raise ValueError("the root-to-leaf sums must differ")
        return [str(target in sums)]
    walked = _visit(root, want)
    if want != "inorder" and walked == _visit(root, "inorder"):
        raise ValueError(f"{want} must differ from inorder on this tree")
    return [" ".join(str(v) for v in walked)]


def _toolkit_expected(a: dict) -> list[str]:
    want = a["want"]
    if want in ("heapify", "heap_largest"):
        values, take = list(a["values"]), a["take"]
        if not 0 < take < len(values):
            raise ValueError("take must leave something behind")
        order = sorted(values, reverse=(want == "heap_largest"))
        if order[:take] == values[:take]:
            raise ValueError(
                "the data must not already start in the wanted order, or "
                "the heap would be indistinguishable from a slice"
            )
        got = [" ".join(str(n) for n in order[:take])]
        if want == "heapify":
            got.append(str(len(values) - take))
        return got
    text = a["text"]
    if want == "isdigit":
        digits = "".join(c for c in text if c.isdigit())
        rest = "".join(c for c in text if not c.isdigit())
        if not digits or not rest:
            raise ValueError("the text must hold both digits and non-digits")
        return [digits, rest]
    kept = "".join(c.lower() for c in text if c.isalnum())
    if kept == text:
        raise ValueError(
            "something must be stripped, or isalnum is not being tested"
        )
    if not kept:
        raise ValueError("stripping must leave something")
    return [kept, str(kept == kept[::-1])]
