"""Pages 339-341: the last four constructs.

The audit that produced pages 329-338 left four things uncovered, one
problem each. Two of them read as trivia and are not: a node holding a list
of other nodes is a third kind of object, after the chain and the tree, and
it is the first one where a walk can arrive somewhere it has already been.
list.remove takes the first match and stops, which is a thing you find out
once, usually the hard way.

The third earns a page outright. First Bad Version gives you a function and
nothing to look at. You cannot scan the versions; you can only ask about
one. Binary search still works, and seeing that it applies to a question
rather than to a list is the part worth drilling.
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


def _edge_text(edges) -> str:
    return ", ".join(f"{a}-{b}" for a, b in edges)


def _seq(items) -> str:
    return ", ".join(str(n) for n in items)


# ── 339. Nodes with neighbours ───────────────────────────────
#
# Every graph here has at least one cycle, which the guard insists on:
# without one, cloning never revisits a node and the mapping that makes
# Clone Graph work would never be needed.

_GRAPHS = (
    ((1, 2), (2, 3), (1, 3)),
    ((1, 2), (2, 3), (3, 4), (4, 1)),
    ((1, 2), (1, 3), (2, 4), (3, 4)),
    ((1, 2), (2, 3), (3, 1), (3, 4)),
    ((1, 2), (2, 3), (3, 4), (4, 2)),
    ((1, 2), (1, 3), (2, 3), (3, 4), (4, 1)),
    ((1, 2), (2, 4), (4, 3), (3, 1)),
)

_GRAPH_ROWS = (
    tuple((g, "walk", 1) for g in _GRAPHS)
    + tuple((g, "degrees", 1) for g in _GRAPHS)
    + tuple((g, "clone", 1) for g in _GRAPHS[:6])
)

_GRAPH_WORDS = {
    "walk": (
        "Walk it breadth-first from node 1 and print the order the nodes "
        "come out, on one line."
    ),
    "degrees": (
        "Print every node and how many neighbours it has, in order of "
        "value, as val:count on one line."
    ),
    "clone": (
        "Copy the whole graph so that no node object is shared with the "
        "original, then print a breadth-first walk of the copy, then print "
        "whether the copied start is the same object as the original."
    ),
}

GRAPH_PAGE = _page(
    "graph-nodes", 339, "Nodes that hold a list of other nodes",
    "A graph node keeps a list called neighbours instead of one next or "
    "two children. That one change is what lets a walk arrive somewhere it "
    "has already been, which is why every walk here carries a seen set and "
    "why copying one needs a map from old node to new.",
    "node.neighbors is a list of Nodes, so a walk needs a seen set or it "
    "goes round the cycle forever",
    "graph_nodes",
    tuple(
        (f"Build a graph of Node objects from the edges {_edge_text(g)}. "
         f"{_GRAPH_WORDS[w]}",
         {"edges": [list(e) for e in g], "want": w, "start": s})
        for g, w, s in _GRAPH_ROWS
    ),
)


# ── 340. Taking something out by value ───────────────────────

_FIRST_ONLY = (
    ((3, 1, 4, 1, 5), 1), ((2, 7, 2, 8), 2), ((5, 5, 5, 9), 5),
    ((1, 6, 1, 6), 6), ((4, 2, 9, 2), 2), ((8, 3, 8, 1), 8),
    ((7, 7, 2, 4), 7),
)

_DISCARDS = (
    ((1, 2, 3, 4), 2, 9), ((5, 6, 7), 6, 1), ((2, 4, 8), 4, 3),
    ((3, 5, 9), 9, 7), ((1, 4, 6, 8), 6, 2), ((2, 3, 7), 3, 5),
    ((4, 5, 9), 5, 8),
)

_PEELS = (
    (((1, 2), (2, 3), (3, 4), (2, 5)), 1),
    (((1, 2), (2, 3), (3, 4), (4, 5), (3, 6)), 1),
    (((1, 2), (1, 3), (1, 4), (4, 5)), 1),
    (((1, 2), (2, 3), (2, 4), (4, 5), (5, 6)), 1),
    (((1, 2), (2, 3), (3, 4), (4, 5), (5, 6)), 2),
    (((1, 2), (2, 3), (3, 4), (2, 5), (5, 6)), 2),
)

REMOVE_PAGE = _page(
    "value-remove", 340, "Taking something out by value",
    "remove takes the first match and stops, which is the part that "
    "surprises people, and raises if there is no match at all. discard is "
    "the version that shrugs. Peeling the leaves off a tree is what those "
    "become when the value you are removing is a node.",
    "items.remove(1) on [3, 1, 4, 1, 5] leaves [3, 4, 1, 5] — one of the "
    "ones is still there",
    "value_remove",
    tuple(
        (f"Remove {d} from [{_seq(v)}] with list.remove, print what is "
         f"left, then print how many are left. Note how many {d}s went.",
         {"values": list(v), "want": "first_only", "drop": d})
        for v, d in _FIRST_ONLY
    ) + tuple(
        (f"Make a set from [{_seq(v)}]. discard {m}, which is not in it, "
         f"then remove {d}, which is. Print what is left in order.",
         {"values": list(v), "want": "discard", "drop": d, "missing": m})
        for v, d, m in _DISCARDS
    ) + tuple(
        (f"Build the tree with edges {_edge_text(g)}. Strip off every node "
         f"with a single connection, {r} round(s) of it, and print what "
         f"remains in order.",
         {"edges": [list(e) for e in g], "want": "peel", "rounds": r})
        for g, r in _PEELS
    ),
)


# ── 341. Searching a question ────────────────────────────────

_SEARCHES = (
    (20, 7), (100, 42), (16, 5), (50, 33), (64, 9), (30, 24),
    (128, 77), (25, 13), (40, 6), (200, 111), (12, 8), (75, 50),
    (256, 199), (18, 3), (60, 44), (33, 17), (90, 22), (150, 96),
    (45, 31), (80, 61),
)

SEARCH_PAGE = _page(
    "predicate-search", 341, "Searching a question instead of a list",
    "There is no array here. You are handed a function that answers one "
    "question about one version, and the versions themselves are invisible. "
    "Binary search does not care: all it needs is that the answer is False "
    "up to a point and True from there on, and finding that point costs log "
    "n questions rather than n.",
    "is_bad(mid) is the only thing you can see, and hi = mid keeps the "
    "candidate rather than discarding it",
    "predicate_search",
    tuple(
        (f"Versions 1 to {n} are numbered in order, and every version from "
         f"the first bad one onwards is bad. Find the first bad version by "
         f"asking is_bad, then print it and how many times you asked. Use "
         f"first_bad = {b} to build the function.",
         {"n": n, "first_bad": b})
        for n, b in _SEARCHES
    ),
)


GRAPH_PAGES: tuple[Page, ...] = (GRAPH_PAGE, REMOVE_PAGE, SEARCH_PAGE)
