"""The last four constructs the solution bank uses and the workbook did not.

Pages 329-338 closed the big gap. The audit that found it left four things
behind, each in a single problem, and two of them looked like trivia: a
node attribute called neighbors, and list.remove. They are not quite
trivia. A graph node holding a list of other nodes is a different object
from a chain or a tree, and copying one is the first time a walk has to
cope with arriving somewhere it has already been. list.remove takes the
first match and only the first, which is the sort of thing you learn once
by having it go wrong.

The third is worth a page on its own merits. First Bad Version hands you a
function and no data: you cannot look at the versions, only ask about one.
Binary search still applies, and noticing that it applies to a question
rather than to a list is the whole trick.

Python only, and every program prints an answer worked out twice.
"""

from __future__ import annotations


from code_coach.workbook.emit import NL, Shape, _lines

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("graph_nodes", "nodes that hold a list of other nodes"),
    Shape("value_remove", "taking something out by value"),
    Shape("predicate_search", "searching a question instead of a list"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _pairs(items) -> str:
    return "[" + ", ".join(f"({a}, {b})" for a, b in items) + "]"


def _nums(items) -> str:
    return "[" + ", ".join(str(n) for n in items) + "]"


_GRAPH_NODE = (
    "class Node:",
    "    def __init__(self, val):",
    "        self.val = val",
    "        self.neighbors = []",
    "",
)

_BUILD_GRAPH = (
    "nodes = {}",
    "for a, b in edges:",
    "    for v in (a, b):",
    "        if v not in nodes:",
    "            nodes[v] = Node(v)",
    "    nodes[a].neighbors.append(nodes[b])",
    "    nodes[b].neighbors.append(nodes[a])",
    "",
)


# ── 339. Nodes with neighbours ───────────────────────────────


def _graph_nodes(a: dict) -> str:
    want = a["want"]
    head = (
        *_GRAPH_NODE,
        f"edges = {_pairs(a['edges'])}",
        *_BUILD_GRAPH,
    )
    if want == "degrees":
        return _lines(
            *head,
            "out = []",
            "for val in sorted(nodes):",
            "    out.append(str(val) + ':' + str(len(nodes[val].neighbors)))",
            "print(' '.join(out))",
        )
    walk = (
        "from collections import deque",
        "",
        "def walk(start):",
        "    seen = {start.val}",
        "    queue = deque([start])",
        "    order = []",
        "    while queue:",
        "        node = queue.popleft()",
        "        order.append(str(node.val))",
        "        for nb in node.neighbors:",
        "            if nb.val not in seen:",
        "                seen.add(nb.val)",
        "                queue.append(nb)",
        "    return ' '.join(order)",
        "",
    )
    start = f"start = nodes[{a['start']}]"
    if want == "walk":
        return _lines(*walk[:2], *head, *walk[2:], start, "print(walk(start))")
    return _lines(
        *walk[:2],
        *head,
        *walk[2:],
        "def clone(node, made):",
        "    if node.val in made:",
        "        return made[node.val]",
        "    copy = Node(node.val)",
        "    made[node.val] = copy",
        "    for nb in node.neighbors:",
        "        copy.neighbors.append(clone(nb, made))",
        "    return copy",
        "",
        start,
        "copied = clone(start, {})",
        "print(walk(copied))",
        "print(copied is start)",
    )


# ── 340. Taking something out by value ───────────────────────


def _value_remove(a: dict) -> str:
    want = a["want"]
    if want == "first_only":
        return _lines(
            f"items = {_nums(a['values'])}",
            f"items.remove({a['drop']})",
            "print(' '.join(str(n) for n in items))",
            "print(len(items))",
        )
    if want == "discard":
        return _lines(
            f"seen = set({_nums(a['values'])})",
            f"seen.discard({a['missing']})",
            f"seen.remove({a['drop']})",
            "print(' '.join(str(n) for n in sorted(seen)))",
        )
    return _lines(
        f"edges = {_pairs(a['edges'])}",
        "linked = {}",
        "for x, y in edges:",
        "    linked.setdefault(x, []).append(y)",
        "    linked.setdefault(y, []).append(x)",
        "left = set(linked)",
        f"for _ in range({a['rounds']}):",
        "    leaves = [v for v in left if len(linked[v]) == 1]",
        "    for leaf in leaves:",
        "        for other in linked[leaf]:",
        "            linked[other].remove(leaf)",
        "        linked[leaf] = []",
        "        left.remove(leaf)",
        "print(' '.join(str(v) for v in sorted(left)))",
    )


# ── 341. Searching a question ────────────────────────────────


def _predicate_search(a: dict) -> str:
    # The program prints whether it stayed inside the log2 bound rather
    # than how many questions it asked. The exact count is not a property
    # of n: (lo + hi) // 2 splits the range unevenly, so the same n needs
    # a different number of questions depending on where the answer sits.
    # Printing the count would mean the expectation had to re-run this very
    # loop to know it, which is grading the program against itself.
    return _lines(
        "import math",
        "",
        f"first_bad = {a['first_bad']}",
        "calls = 0",
        "",
        "def is_bad(version):",
        "    global calls",
        "    calls += 1",
        "    return version >= first_bad",
        "",
        f"n = {a['n']}",
        "lo, hi = 1, n",
        "while lo < hi:",
        "    mid = (lo + hi) // 2",
        "    if is_bad(mid):",
        "        hi = mid",
        "    else:",
        "        lo = mid + 1",
        "print(lo)",
        "print(calls <= math.ceil(math.log2(n)))",
    )


_BUILDERS = {
    "graph_nodes": _graph_nodes,
    "value_remove": _value_remove,
    "predicate_search": _predicate_search,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


def _adjacency(edges) -> dict:
    """The same graph as a dict of lists, built in the same edge order.

    A dict of lists rather than linked objects: the same walk, over a
    different structure, which is what makes it worth comparing against.
    """
    linked: dict = {}
    for x, y in edges:
        linked.setdefault(x, []).append(y)
        linked.setdefault(y, []).append(x)
    return linked


def _bfs(linked: dict, start) -> list:
    seen = {start}
    queue = [start]
    order = []
    while queue:
        here = queue.pop(0)
        order.append(here)
        for there in linked.get(here, []):
            if there not in seen:
                seen.add(there)
                queue.append(there)
    return order


def expected_output(shape: str, args: dict, value) -> str:
    """Worked out here, from dicts and arithmetic, never from the objects.

    The guards ask the usual question: could this data pass while proving
    nothing. A graph with no cycle makes the clone mapping pointless. A
    value that appears once makes remove look like it removes everything.
    A first bad version at either end is found before the search starts.
    """
    a = args
    if shape == "graph_nodes":
        edges = [tuple(e) for e in a["edges"]]
        linked = _adjacency(edges)
        want = a["want"]
        if want == "degrees":
            return NL.join([
                " ".join(f"{v}:{len(linked[v])}" for v in sorted(linked))
            ])
        start = a["start"]
        if start not in linked:
            raise ValueError("the starting node must be in the graph")
        order = _bfs(linked, start)
        if len(order) < len(linked):
            raise ValueError(
                "every node must be reachable from the start, or the walk "
                "quietly misses part of the graph"
            )
        if len(edges) < len(linked):
            raise ValueError(
                "the graph must contain a cycle, or arriving somewhere "
                "twice never happens and the seen check is decoration"
            )
        walked = " ".join(str(v) for v in order)
        if want == "walk":
            return walked
        return NL.join([walked, "False"])
    if shape == "value_remove":
        want = a["want"]
        if want == "first_only":
            values, drop = list(a["values"]), a["drop"]
            if values.count(drop) < 2:
                raise ValueError(
                    "the value must appear at least twice, or removing only "
                    "the first is indistinguishable from removing them all"
                )
            kept = list(values)
            kept.remove(drop)
            return NL.join([
                " ".join(str(n) for n in kept), str(len(kept))
            ])
        if want == "discard":
            values, drop, missing = set(a["values"]), a["drop"], a["missing"]
            if drop not in values:
                raise ValueError("remove needs a value that is there")
            if missing in values:
                raise ValueError(
                    "discard must be given a value that is absent, or it is "
                    "not showing what it does differently from remove"
                )
            return " ".join(str(n) for n in sorted(values - {drop}))
        edges = [tuple(e) for e in a["edges"]]
        linked = _adjacency(edges)
        left = set(linked)
        for _ in range(a["rounds"]):
            leaves = {v for v in left if len(linked[v]) == 1}
            if not leaves:
                raise ValueError("a round with no leaves peels nothing")
            for leaf in leaves:
                for other in linked[leaf]:
                    linked[other].remove(leaf)
                linked[leaf] = []
            left -= leaves
        if not left:
            raise ValueError("peeling must leave something behind")
        return " ".join(str(v) for v in sorted(left))
    if shape == "predicate_search":
        n, first_bad = a["n"], a["first_bad"]
        if not 1 < first_bad < n:
            raise ValueError(
                "the first bad version must not be at either end, where the "
                "search finds it without narrowing anything"
            )
        # Two claims, both computable without running the search: the
        # answer is the version the data names, and finding it took no
        # more than log2(n) questions. The first version of this expected
        # an exact call count of ceil(log2(n)) and was wrong — the split
        # is uneven, so n=25 needs four questions for one target and five
        # for another. The program was right and the expectation was not.
        if n < 2:
            raise ValueError("a search needs a range to narrow")
        return NL.join([str(first_bad), "True"])
    raise KeyError(shape)
