"""The moves the interview patterns are made of, second half.

The first ten were the linear scans: count as you go, two pointers, a
window, a running best. These are the ones with a shape to them — halving,
recursion down a tree, a frontier spreading out, a table filled in order.

Python only, and because both the program and its expected output are
Python here, a list can be printed directly: repr on one side matches repr
on the other. That is not true of the JavaScript and TypeScript tiers, and
it is why these pages read more like the code you would actually write.

Every emitted program is a real implementation rather than a call into the
library. There is already a page on bisect and a page on heapq; these build
the search and the heap-of-size-k by hand, because the point is the move
and not the import.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("algo_binary_search", "halving the range until it is empty"),
    Shape("algo_search_boundary", "the first position where it becomes true"),
    Shape("algo_tree_dfs", "down one branch, all the way, then the next"),
    Shape("algo_tree_bfs", "a whole level before any of the next"),
    Shape("algo_graph_reach", "everything you can get to from here"),
    Shape("algo_graph_hops", "the fewest steps between two places"),
    Shape("algo_backtrack", "try it, keep going, put it back"),
    Shape("algo_top_k", "a heap that only ever holds the best k"),
    Shape("algo_memo_grid", "the same subproblem, answered once"),
    Shape("algo_dp_table", "filling a table in an order that always works"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return "[" + ", ".join(str(n) for n in items) + "]"


def _tree(node) -> str:
    """A nested (value, left, right) tuple as a Node(...) expression."""
    if node is None:
        return "None"
    value, left, right = node
    if left is None and right is None:
        return f"Node({value})"
    return f"Node({value}, {_tree(left)}, {_tree(right)})"


def _walk(node):
    """Every value in a nested tuple tree, depth first."""
    if node is None:
        return []
    value, left, right = node
    return [value] + _walk(left) + _walk(right)


def _depth(node) -> int:
    if node is None:
        return 0
    _, left, right = node
    return 1 + max(_depth(left), _depth(right))


def _levels(node) -> list[list[int]]:
    out: list[list[int]] = []
    row = [node] if node else []
    while row:
        out.append([n[0] for n in row])
        nxt = []
        for _, left, right in row:
            if left:
                nxt.append(left)
            if right:
                nxt.append(right)
        row = nxt
    return out


NODE_CLASS = (
    "class Node:",
    "    def __init__(self, value, left=None, right=None):",
    "        self.value = value",
    "        self.left = left",
    "        self.right = right",
    "",
)


# ── 299. Halving the range ───────────────────────────────────


def _binary_search(a: dict) -> str:
    return _lines(
        f"numbers = {_nums(a['items'])}",
        f"target = {a['target']}",
        "low = 0",
        "high = len(numbers) - 1",
        "found = -1",
        "steps = 0",
        "while low <= high:",
        "    steps += 1",
        "    mid = (low + high) // 2",
        "    if numbers[mid] == target:",
        "        found = mid",
        "        break",
        "    if numbers[mid] < target:",
        "        low = mid + 1",
        "    else:",
        "        high = mid - 1",
        "",
        "print(found)",
        "print(steps)",
        "print(len(numbers))",
    )


# ── 300. The first position where it becomes true ────────────


def _search_boundary(a: dict) -> str:
    return _lines(
        f"numbers = {_nums(a['items'])}",
        f"limit = {a['limit']}",
        "low = 0",
        "high = len(numbers)",
        "while low < high:",
        "    mid = (low + high) // 2",
        "    if numbers[mid] >= limit:",
        "        high = mid",
        "    else:",
        "        low = mid + 1",
        "",
        "print(low)",
        "print(numbers[low] if low < len(numbers) else None)",
    )


# ── 301. Depth first ─────────────────────────────────────────


def _tree_dfs(a: dict) -> str:
    return _lines(
        *NODE_CLASS,
        f"root = {_tree(a['tree'])}",
        "",
        "def total(node):",
        "    if node is None:",
        "        return 0",
        "    return node.value + total(node.left) + total(node.right)",
        "",
        "def depth(node):",
        "    if node is None:",
        "        return 0",
        "    return 1 + max(depth(node.left), depth(node.right))",
        "",
        "print(total(root))",
        "print(depth(root))",
    )


# ── 302. Breadth first ───────────────────────────────────────


def _tree_bfs(a: dict) -> str:
    return _lines(
        "from collections import deque",
        "",
        *NODE_CLASS,
        f"root = {_tree(a['tree'])}",
        "",
        "queue = deque([root])",
        "levels = []",
        "while queue:",
        "    row = []",
        "    for _ in range(len(queue)):",
        "        node = queue.popleft()",
        "        row.append(node.value)",
        "        if node.left:",
        "            queue.append(node.left)",
        "        if node.right:",
        "            queue.append(node.right)",
        "    levels.append(row)",
        "",
        "for row in levels:",
        '    print(", ".join(str(v) for v in row))',
        "print(len(levels))",
    )


# ── 303. Everything reachable ────────────────────────────────


def _graph_reach(a: dict) -> str:
    edges = ", ".join(
        f"{_q(node)}: [{', '.join(_q(n) for n in nbrs)}]"
        for node, nbrs in a["edges"]
    )
    return _lines(
        f"graph = {{{edges}}}",
        f"start = {_q(a['start'])}",
        "",
        "seen = set()",
        "stack = [start]",
        "while stack:",
        "    here = stack.pop()",
        "    if here in seen:",
        "        continue",
        "    seen.add(here)",
        "    for nxt in graph.get(here, []):",
        "        if nxt not in seen:",
        "            stack.append(nxt)",
        "",
        "print(len(seen))",
        'print(", ".join(sorted(seen)))',
    )


# ── 304. Fewest steps ────────────────────────────────────────


def _graph_hops(a: dict) -> str:
    edges = ", ".join(
        f"{_q(node)}: [{', '.join(_q(n) for n in nbrs)}]"
        for node, nbrs in a["edges"]
    )
    return _lines(
        "from collections import deque",
        "",
        f"graph = {{{edges}}}",
        f"start = {_q(a['start'])}",
        f"goal = {_q(a['goal'])}",
        "",
        "queue = deque([(start, 0)])",
        "seen = {start}",
        "hops = -1",
        "while queue:",
        "    here, so_far = queue.popleft()",
        "    if here == goal:",
        "        hops = so_far",
        "        break",
        "    for nxt in graph.get(here, []):",
        "        if nxt not in seen:",
        "            seen.add(nxt)",
        "            queue.append((nxt, so_far + 1))",
        "",
        "print(hops)",
        "print(len(seen))",
    )


# ── 305. Try it, keep going, put it back ─────────────────────


def _backtrack(a: dict) -> str:
    return _lines(
        f"numbers = {_nums(a['items'])}",
        f"target = {a['target']}",
        "found = []",
        "chosen = []",
        "",
        "def search(index, left):",
        "    if left == 0:",
        "        found.append(list(chosen))",
        "        return",
        "    if left < 0 or index == len(numbers):",
        "        return",
        "    chosen.append(numbers[index])",
        "    search(index + 1, left - numbers[index])",
        "    chosen.pop()",
        "    search(index + 1, left)",
        "",
        "search(0, target)",
        "",
        "print(len(found))",
        'print(", ".join(str(n) for n in found[0]))',
    )


# ── 306. A heap of size k ────────────────────────────────────


def _top_k(a: dict) -> str:
    return _lines(
        "import heapq",
        "",
        f"numbers = {_nums(a['items'])}",
        f"k = {a['k']}",
        "best = []",
        "for number in numbers:",
        "    heapq.heappush(best, number)",
        "    if len(best) > k:",
        "        heapq.heappop(best)",
        "",
        "print(best[0])",
        "print(sorted(best, reverse=True))",
    )


# ── 307. The same subproblem, answered once ──────────────────


def _memo_grid(a: dict) -> str:
    return _lines(
        f"rows = {a['rows']}",
        f"cols = {a['cols']}",
        "memo = {}",
        "",
        "def paths(r, c):",
        "    if r == rows - 1 or c == cols - 1:",
        "        return 1",
        "    if (r, c) in memo:",
        "        return memo[(r, c)]",
        "    memo[(r, c)] = paths(r + 1, c) + paths(r, c + 1)",
        "    return memo[(r, c)]",
        "",
        "print(paths(0, 0))",
        "print(len(memo))",
    )


# ── 308. Filling a table ─────────────────────────────────────


def _dp_table(a: dict) -> str:
    return _lines(
        f"steps = {a['steps']}",
        "ways = [0] * (steps + 1)",
        "ways[0] = 1",
        "for i in range(1, steps + 1):",
        "    ways[i] = ways[i - 1]",
        "    if i >= 2:",
        "        ways[i] += ways[i - 2]",
        "",
        "print(ways[steps])",
        f"print(ways[{a['peek']}])",
    )


_BUILDERS = {
    "algo_binary_search": _binary_search,
    "algo_search_boundary": _search_boundary,
    "algo_tree_dfs": _tree_dfs,
    "algo_tree_bfs": _tree_bfs,
    "algo_graph_reach": _graph_reach,
    "algo_graph_hops": _graph_hops,
    "algo_backtrack": _backtrack,
    "algo_top_k": _top_k,
    "algo_memo_grid": _memo_grid,
    "algo_dp_table": _dp_table,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    if build is None:
        return None
    return build(args)


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out here, independently of the program that prints it.

    The guards matter more on this tier than any other. A binary search
    over a list that is not sorted finds nothing and looks fine. A tree
    that is a straight line makes depth-first and breadth-first agree. A
    backtracking page whose target no subset reaches prints an empty
    answer. Each of those runs perfectly and teaches the wrong thing.
    """
    a = args
    lines: list[str] = []
    if shape == "algo_binary_search":
        items = list(a["items"])
        if items != sorted(items):
            raise ValueError("binary search needs a sorted list")
        if a["target"] not in items:
            raise ValueError("the target must be in the list")
        low, high, found, steps = 0, len(items) - 1, -1, 0
        while low <= high:
            steps += 1
            mid = (low + high) // 2
            if items[mid] == a["target"]:
                found = mid
                break
            if items[mid] < a["target"]:
                low = mid + 1
            else:
                high = mid - 1
        if steps < 2:
            raise ValueError("a one-step search shows nothing about halving")
        lines = [str(found), str(steps), str(len(items))]
    elif shape == "algo_search_boundary":
        items = list(a["items"])
        if items != sorted(items):
            raise ValueError("the boundary search needs a sorted list")
        if a["limit"] in items:
            raise ValueError(
                "the limit must fall between values, or this is a plain find"
            )
        low, high = 0, len(items)
        while low < high:
            mid = (low + high) // 2
            if items[mid] >= a["limit"]:
                high = mid
            else:
                low = mid + 1
        if low in (0, len(items)):
            raise ValueError("the boundary must land inside the list")
        lines = [str(low), str(items[low])]
    elif shape == "algo_tree_dfs":
        tree = a["tree"]
        if _depth(tree) < 3:
            raise ValueError("the tree must be deeper than two levels")
        lines = [str(sum(_walk(tree))), str(_depth(tree))]
    elif shape == "algo_tree_bfs":
        rows = _levels(a["tree"])
        if len(rows) < 3:
            raise ValueError("a level order needs more than two levels")
        if max(len(r) for r in rows) < 2:
            raise ValueError("some level must hold more than one node")
        lines = [", ".join(str(v) for v in row) for row in rows]
        lines.append(str(len(rows)))
    elif shape == "algo_graph_reach":
        graph = {node: list(nbrs) for node, nbrs in a["edges"]}
        seen: set[str] = set()
        stack = [a["start"]]
        while stack:
            here = stack.pop()
            if here in seen:
                continue
            seen.add(here)
            for nxt in graph.get(here, []):
                if nxt not in seen:
                    stack.append(nxt)
        every = set(graph) | {n for nbrs in graph.values() for n in nbrs}
        if seen == every:
            raise ValueError("something must be unreachable, or this is a walk")
        if len(seen) < 3:
            raise ValueError("the reachable part must be more than a pair")
        lines = [str(len(seen)), ", ".join(sorted(seen))]
    elif shape == "algo_graph_hops":
        from collections import deque

        graph = {node: list(nbrs) for node, nbrs in a["edges"]}
        queue = deque([(a["start"], 0)])
        seen = {a["start"]}
        hops = -1
        while queue:
            here, so_far = queue.popleft()
            if here == a["goal"]:
                hops = so_far
                break
            for nxt in graph.get(here, []):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, so_far + 1))
        if hops < 2:
            raise ValueError("the goal must be more than one step away")
        lines = [str(hops), str(len(seen))]
    elif shape == "algo_backtrack":
        items, target = list(a["items"]), a["target"]
        found: list[list[int]] = []
        chosen: list[int] = []

        def search(index: int, left: int) -> None:
            if left == 0:
                found.append(list(chosen))
                return
            if left < 0 or index == len(items):
                return
            chosen.append(items[index])
            search(index + 1, left - items[index])
            chosen.pop()
            search(index + 1, left)

        search(0, target)
        if not found:
            raise ValueError("some subset must reach the target")
        if len(found) < 2:
            raise ValueError("more than one subset must work, or nothing backtracks")
        lines = [str(len(found)), ", ".join(str(n) for n in found[0])]
    elif shape == "algo_top_k":
        import heapq

        items, k = list(a["items"]), a["k"]
        if k >= len(items):
            raise ValueError("k must be smaller than the list")
        best: list[int] = []
        for number in items:
            heapq.heappush(best, number)
            if len(best) > k:
                heapq.heappop(best)
        lines = [str(best[0]), repr(sorted(best, reverse=True))]
    elif shape == "algo_memo_grid":
        rows, cols = a["rows"], a["cols"]
        if rows < 3 or cols < 3:
            raise ValueError("a grid this small has nothing to remember")
        memo: dict[tuple[int, int], int] = {}

        def paths(r: int, c: int) -> int:
            if r == rows - 1 or c == cols - 1:
                return 1
            if (r, c) in memo:
                return memo[(r, c)]
            memo[(r, c)] = paths(r + 1, c) + paths(r, c + 1)
            return memo[(r, c)]

        total = paths(0, 0)
        lines = [str(total), str(len(memo))]
    elif shape == "algo_dp_table":
        steps, peek = a["steps"], a["peek"]
        if not 0 <= peek <= steps:
            raise ValueError("the peek must be inside the table")
        if steps < 4:
            raise ValueError("a table this short shows nothing")
        ways = [0] * (steps + 1)
        ways[0] = 1
        for i in range(1, steps + 1):
            ways[i] = ways[i - 1] + (ways[i - 2] if i >= 2 else 0)
        lines = [str(ways[steps]), str(ways[peek])]
    else:
        raise KeyError(shape)
    return NL.join(lines)
