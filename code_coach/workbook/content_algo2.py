"""Pages 299-308: the rest of the moves.

The first ten were linear — one scan, sometimes with two pointers on it.
These have a shape: halving, recursing down a tree, a frontier spreading
out a level at a time, a table filled in an order that guarantees what you
need is already there.

With these ten the workbook covers every pattern in the LeetCode tier.
That does not mean the problems become free — knowing the move and
spotting which move a problem wants are still two things — but the second
is a much smaller step when the first is in your fingers.

Python only.
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


def _shape_of(node) -> str:
    """A tree as value(left, right), a leaf as just its value.

    The prompt has to carry the tree. Saying "the tree below" and putting
    it only in the answer leaves nothing to work from — and two different
    trees with the same total and depth then become the same exercise,
    which is how this was noticed.
    """
    value, left, right = node
    if left is None and right is None:
        return str(value)
    inner = ", ".join(
        _shape_of(child) if child else "-" for child in (left, right)
    )
    return f"{value}({inner})"


# ── 299. Halving the range ───────────────────────────────────

_SEARCHES = (
    ((1, 3, 5, 7, 9, 11, 13), 3),
    ((2, 4, 6, 8, 10, 12), 10),
    ((5, 10, 15, 20, 25, 30, 35), 5),
    ((1, 2, 3, 4, 5, 6, 7, 8), 7),
    ((10, 20, 30, 40, 50), 20),
    ((3, 6, 9, 12, 15, 18, 21), 18),
    ((11, 22, 33, 44, 55, 66), 22),
    ((1, 4, 9, 16, 25, 36, 49), 9),
    ((2, 3, 5, 7, 11, 13, 17), 13),
    ((100, 200, 300, 400, 500), 400),
    ((8, 16, 24, 32, 40, 48), 16),
    ((1, 5, 9, 13, 17, 21, 25), 21),
    ((7, 14, 21, 28, 35, 42), 28),
    ((6, 12, 18, 24, 30, 36, 42), 12),
    ((13, 26, 39, 52, 65), 26),
    ((4, 8, 12, 16, 20, 24, 28), 24),
    ((9, 18, 27, 36, 45, 54), 45),
    ((15, 30, 45, 60, 75, 90), 30),
    ((2, 5, 8, 11, 14, 17, 20), 5),
    ((17, 34, 51, 68, 85, 102), 68),
)

_P299 = _page(
    "algo-binary-search",
    299,
    "Halving the range until it is empty",
    "low, high, mid — and throwing away half the list every step.",
    "Sorted is what buys you this. Look at the middle: if it is too small "
    "then the answer is not in the left half, and you never look there "
    "again. Twenty items take five steps, a thousand take ten, a million "
    "take twenty — the step count is printed beside the length so you can "
    "see that. Two details bite everyone: the loop is `low <= high` "
    "because a range of one item is still a range, and mid uses `//` "
    "because an index is an integer.",
    "algo_binary_search",
    [
        (
            f"Find {target} in the sorted list {_seq(items)} by halving. "
            f"Print the position you found it at, how many steps that took, "
            f"and how long the list was.",
            {"items": items, "target": target},
        )
        for items, target in _SEARCHES
    ],
)


# ── 300. The first position where it becomes true ────────────

_BOUNDARIES = (
    ((1, 3, 5, 7, 9, 11), 6),
    ((2, 4, 6, 8, 10), 5),
    ((10, 20, 30, 40, 50), 35),
    ((1, 2, 3, 4, 5, 6), 4.5),
    ((5, 15, 25, 35, 45), 20),
    ((3, 6, 9, 12, 15), 10),
    ((11, 22, 33, 44, 55), 40),
    ((1, 4, 9, 16, 25), 10),
    ((2, 3, 5, 7, 11), 6),
    ((100, 200, 300, 400), 250),
    ((8, 16, 24, 32, 40), 20),
    ((1, 5, 9, 13, 17), 11),
    ((7, 14, 21, 28, 35), 15),
    ((6, 12, 18, 24, 30), 20),
    ((13, 26, 39, 52), 30),
    ((4, 8, 12, 16, 20), 14),
    ((9, 18, 27, 36, 45), 20),
    ((15, 30, 45, 60), 40),
    ((2, 5, 8, 11, 14), 9),
    ((17, 34, 51, 68), 40),
)

_P300 = _page(
    "algo-search-boundary",
    300,
    "The first position where it becomes true",
    "The same halving, but hunting a boundary rather than a value.",
    "This is the version that actually comes up. The list is sorted, so "
    "somewhere it stops being under the limit and starts being over — and "
    "you want that crossing point, whether or not the limit is in the list "
    "at all. Two changes from the plain search and both matter: high "
    "starts at len rather than len - 1 because the answer can be off the "
    "end, and the loop is `low < high` because it is closing on a gap, not "
    "looking for a hit. Once you have this, insertion points and "
    "first-true-in-a-range are the same function.",
    "algo_search_boundary",
    [
        (
            f"In the sorted list {_seq(items)}, find the position of the "
            f"first number that reaches {limit}. Halve the range, moving "
            f"high down to mid when the middle is big enough. Print the "
            f"position and the number there.",
            {"items": items, "limit": limit},
        )
        for items, limit in _BOUNDARIES
    ],
)


# ── 301. Down one branch, then the next ──────────────────────

_DFS_TREES = (
    (3, (9, None, None), (20, (15, None, None), (7, None, None))),
    (1, (2, (4, None, None), None), (3, None, None)),
    (5, (3, (2, None, None), (4, None, None)), (8, None, None)),
    (10, (5, (1, None, None), None), (15, None, (20, None, None))),
    (2, (1, None, None), (3, None, (4, None, None))),
    (7, (3, (1, None, None), (5, None, None)), (9, None, None)),
    (4, (2, (1, None, None), (3, None, None)), (6, None, None)),
    (8, (4, None, (6, None, None)), (12, (10, None, None), None)),
    (6, (2, (1, None, None), None), (9, (7, None, None), None)),
    (11, (5, (2, None, None), None), (17, None, None)),
    (13, (6, (3, None, None), (9, None, None)), (20, None, None)),
    (1, (2, (3, None, None), (4, None, None)), (5, None, None)),
    (9, (4, (2, None, None), None), (14, (11, None, None), None)),
    (15, (7, (3, None, None), None), (22, None, (30, None, None))),
    (12, (6, None, (8, None, None)), (18, (16, None, None), None)),
    (20, (10, (5, None, None), (15, None, None)), (30, None, None)),
    (3, (1, None, (2, None, None)), (5, (4, None, None), None)),
    (25, (12, (6, None, None), None), (37, None, (40, None, None))),
    (14, (7, (2, None, None), (9, None, None)), (21, None, None)),
    (18, (9, None, (11, None, None)), (27, (24, None, None), None)),
)

_P301 = _page(
    "algo-tree-dfs",
    301,
    "Down one branch, all the way, then the next",
    "Recursion on a tree, and the None that ends it.",
    "Every tree function has the same two lines at the top: what is the "
    "answer for nothing, and how do the two sides combine. Total is the "
    "value plus both sides. Depth is one plus the deeper side. Get the "
    "empty case right and the rest writes itself — and the empty case is "
    "always None, never a leaf, because a leaf still has two children that "
    "happen to be nothing.",
    "algo_tree_dfs",
    [
        (
            f"Build the tree {_shape_of(tree)} — written value(left, "
            f"right), a bare number for a leaf, a dash for nothing — with a "
            f"Node class. Write total and depth as recursive functions and "
            f"print both.",
            {"tree": tree},
        )
        for tree in _DFS_TREES
    ],
)


# ── 302. A whole level at a time ─────────────────────────────

_BFS_TREES = (
    (3, (9, (1, None, None), None), (20, (15, None, None), (7, None, None))),
    (1, (2, (4, None, None), (5, None, None)), (3, (6, None, None), None)),
    (5, (3, (2, None, None), (4, None, None)), (8, (7, None, None), None)),
    (10, (5, (1, None, None), (7, None, None)), (15, None, (20, None, None))),
    (2, (1, (8, None, None), None), (3, (4, None, None), (5, None, None))),
    (7, (3, (1, None, None), (5, None, None)), (9, (8, None, None), None)),
    (4, (2, (1, None, None), (3, None, None)), (6, (5, None, None), None)),
    (8, (4, (2, None, None), (6, None, None)), (12, (10, None, None), None)),
    (6, (2, (1, None, None), (3, None, None)), (9, (7, None, None), None)),
    (11, (5, (2, None, None), (8, None, None)), (17, (14, None, None), None)),
    (13, (6, (3, None, None), (9, None, None)), (20, (17, None, None), None)),
    (1, (2, (3, None, None), (4, None, None)), (5, (6, None, None), None)),
    (9, (4, (2, None, None), (6, None, None)), (14, (11, None, None), None)),
    (15, (7, (3, None, None), (9, None, None)), (22, (18, None, None), None)),
    (12, (6, (4, None, None), (8, None, None)), (18, (16, None, None), None)),
    (20, (10, (5, None, None), (15, None, None)), (30, (25, None, None), None)),
    (3, (1, (0, None, None), (2, None, None)), (5, (4, None, None), None)),
    (25, (12, (6, None, None), (18, None, None)), (37, (30, None, None), None)),
    (14, (7, (2, None, None), (9, None, None)), (21, (17, None, None), None)),
    (18, (9, (5, None, None), (11, None, None)), (27, (24, None, None), None)),
)

_P302 = _page(
    "algo-tree-bfs",
    302,
    "A whole level before any of the next",
    "A queue, and taking exactly one level's worth at a time.",
    "Depth first uses the call stack; breadth first needs a queue you hold "
    "yourself. The trick that makes levels come out separately is the "
    "inner `for _ in range(len(queue))` — measure the queue *before* you "
    "start adding to it, and you take exactly the nodes that were on this "
    "level. Without that you get every value in the right order but no "
    "idea where one row ends.",
    "algo_tree_bfs",
    [
        (
            f"Walk the tree {_shape_of(tree)} — value(left, right), a bare "
            f"number for a leaf, a dash for nothing — level by level with a "
            f"deque. Print each level's values joined by commas, then how "
            f"many levels there were. Take the queue's length before adding "
            f"to it.",
            {"tree": tree},
        )
        for tree in _BFS_TREES
    ],
)


# ── 303. Everything you can get to ───────────────────────────

_REACH = (
    ((("a", ("b", "c")), ("b", ("d",)), ("c", ()), ("d", ()), ("x", ("y",)), ("y", ())), "a"),
    ((("start", ("mid",)), ("mid", ("end",)), ("end", ()), ("lone", ())), "start"),
    ((("p", ("q", "r")), ("q", ()), ("r", ("s",)), ("s", ()), ("z", ())), "p"),
    ((("one", ("two",)), ("two", ("three",)), ("three", ()), ("four", ())), "one"),
    ((("n", ("e", "w")), ("e", ()), ("w", ("s",)), ("s", ()), ("far", ())), "n"),
    ((("hub", ("a1", "b1")), ("a1", ()), ("b1", ("c1",)), ("c1", ()), ("off", ())), "hub"),
    ((("root", ("l", "r")), ("l", ()), ("r", ("rr",)), ("rr", ()), ("apart", ())), "root"),
    ((("in", ("mid1",)), ("mid1", ("mid2",)), ("mid2", ()), ("out", ())), "in"),
    ((("m", ("n1", "n2")), ("n1", ()), ("n2", ("n3",)), ("n3", ()), ("iso", ())), "m"),
    ((("top", ("k1",)), ("k1", ("k2", "k3")), ("k2", ()), ("k3", ()), ("gone", ())), "top"),
    ((("first", ("g",)), ("g", ("h",)), ("h", ()), ("nope", ())), "first"),
    ((("base", ("t1", "t2")), ("t1", ()), ("t2", ("t3",)), ("t3", ()), ("split", ())), "base"),
    ((("home", ("road",)), ("road", ("town",)), ("town", ()), ("island", ())), "home"),
    ((("core", ("ring",)), ("ring", ("edge",)), ("edge", ()), ("dust", ())), "core"),
    ((("head", ("neck",)), ("neck", ("arm",)), ("arm", ()), ("tail", ())), "head"),
    ((("src", ("via",)), ("via", ("dst",)), ("dst", ()), ("orphan", ())), "src"),
    ((("alpha", ("beta",)), ("beta", ("gamma",)), ("gamma", ()), ("omega", ())), "alpha"),
    ((("oak", ("ash",)), ("ash", ("elm",)), ("elm", ()), ("yew", ())), "oak"),
    ((("tin", ("lead",)), ("lead", ("zinc",)), ("zinc", ()), ("gold", ())), "tin"),
    ((("la", ("ti",)), ("ti", ("do",)), ("do", ()), ("fa", ())), "la"),
)

_P303 = _page(
    "algo-graph-reach",
    303,
    "Everything you can get to from here",
    "A stack, a seen set, and why the seen set is not optional.",
    "A graph is a dict from each place to the places it leads. The walk "
    "itself is four lines — pop, skip if seen, mark seen, push the "
    "neighbours — and the seen set is what stops a cycle running forever. "
    "Every one of these graphs has something the start cannot reach, so "
    "the count is a real answer rather than just the size of the graph.",
    "algo_graph_reach",
    [
        (
            f'Walk the graph below from "{start}" with a stack and a seen '
            f"set. Print how many places you reached and their names sorted "
            f"and joined by commas.",
            {"edges": edges, "start": start},
        )
        for edges, start in _REACH
    ],
)


# ── 304. The fewest steps ────────────────────────────────────

_HOPS = (
    ((("a", ("b", "c")), ("b", ("d",)), ("c", ("d",)), ("d", ("e",)), ("e", ())), "a", "e"),
    ((("s", ("t",)), ("t", ("u",)), ("u", ("v",)), ("v", ())), "s", "v"),
    ((("p", ("q",)), ("q", ("r",)), ("r", ("t",)), ("t", ())), "p", "t"),
    ((("one", ("two",)), ("two", ("three",)), ("three", ("four",)), ("four", ())), "one", "four"),
    ((("n", ("e",)), ("e", ("s",)), ("s", ("w",)), ("w", ())), "n", "w"),
    ((("hub", ("a1",)), ("a1", ("b1",)), ("b1", ("c1",)), ("c1", ())), "hub", "c1"),
    ((("root", ("l",)), ("l", ("ll",)), ("ll", ("lll",)), ("lll", ())), "root", "lll"),
    ((("in", ("m1",)), ("m1", ("m2",)), ("m2", ("out",)), ("out", ())), "in", "out"),
    ((("m", ("n",)), ("n", ("o",)), ("o", ("p",)), ("p", ())), "m", "p"),
    ((("top", ("k1",)), ("k1", ("k2",)), ("k2", ("k3",)), ("k3", ())), "top", "k3"),
    ((("g", ("h",)), ("h", ("i",)), ("i", ("j",)), ("j", ())), "g", "j"),
    ((("base", ("t1",)), ("t1", ("t2",)), ("t2", ("t3",)), ("t3", ())), "base", "t3"),
    ((("home", ("road",)), ("road", ("town",)), ("town", ("city",)), ("city", ())), "home", "city"),
    ((("core", ("ring",)), ("ring", ("edge",)), ("edge", ("rim",)), ("rim", ())), "core", "rim"),
    ((("head", ("neck",)), ("neck", ("arm",)), ("arm", ("hand",)), ("hand", ())), "head", "hand"),
    ((("src", ("v1",)), ("v1", ("v2",)), ("v2", ("dst",)), ("dst", ())), "src", "dst"),
    ((("alpha", ("beta",)), ("beta", ("gamma",)), ("gamma", ("delta",)), ("delta", ())), "alpha", "delta"),
    ((("oak", ("ash",)), ("ash", ("elm",)), ("elm", ("yew",)), ("yew", ())), "oak", "yew"),
    ((("tin", ("lead",)), ("lead", ("zinc",)), ("zinc", ("gold",)), ("gold", ())), "tin", "gold"),
    ((("la", ("ti",)), ("ti", ("do",)), ("do", ("re",)), ("re", ())), "la", "re"),
)

_P304 = _page(
    "algo-graph-hops",
    304,
    "The fewest steps between two places",
    "The same walk with a queue instead of a stack, and why that changes it.",
    "Swap the stack for a queue and depth first becomes breadth first — "
    "and breadth first finds the shortest route, because it looks at "
    "everything one step away before anything two steps away. The first "
    "time it reaches the goal is therefore the fewest hops, which is why "
    "the loop can stop dead rather than comparing routes. Carrying the "
    "distance alongside each place in the queue is the tidy way to know it.",
    "algo_graph_hops",
    [
        (
            f'Find the fewest hops from "{start}" to "{goal}" in the graph '
            f"below, using a deque of place-and-distance pairs. Print the "
            f"hop count and how many places you looked at.",
            {"edges": edges, "start": start, "goal": goal},
        )
        for edges, start, goal in _HOPS
    ],
)


# ── 305. Try it, keep going, put it back ─────────────────────

_BACKTRACKS = (
    ((2, 3, 5, 7), 10),
    ((1, 2, 3, 4), 5),
    ((3, 4, 5, 6), 9),
    ((1, 3, 5, 7), 8),
    ((2, 4, 6, 8), 10),
    ((5, 10, 15, 20), 25),
    ((1, 2, 4, 5), 6),
    ((3, 6, 9, 12), 15),
    ((2, 5, 8, 11), 13),
    ((4, 7, 10, 13), 17),
    ((1, 5, 9, 13), 14),
    ((6, 9, 12, 15), 21),
    ((2, 3, 7, 10), 12),
    ((5, 7, 9, 11), 16),
    ((1, 4, 6, 10), 11),
    ((8, 12, 16, 20), 28),
    ((3, 5, 11, 13), 16),
    ((2, 6, 10, 14), 16),
    ((7, 11, 13, 17), 24),
    ((1, 6, 8, 14), 15),
)

_P305 = _page(
    "algo-backtrack",
    305,
    "Try it, keep going, put it back",
    "Choose, recurse, undo — and the undo is the whole idea.",
    "Backtracking is three lines around a recursive call: add the choice, "
    "explore everything that follows from it, then remove it and explore "
    "what happens without it. The pop is the part people leave out, and "
    "without it every branch pollutes the next. Notice the answer is "
    "copied with `list(chosen)` when it is recorded — record the list "
    "itself and the pops will empty it behind you.",
    "algo_backtrack",
    [
        (
            f"Find every subset of {_seq(items)} that adds up to {target}. "
            f"Add a number, recurse, then take it back and recurse again "
            f"without it. Print how many subsets work and the first one.",
            {"items": items, "target": target},
        )
        for items, target in _BACKTRACKS
    ],
)


# ── 306. A heap that holds only the best k ───────────────────

_TOP_K = (
    ((3, 1, 4, 1, 5, 9, 2, 6), 3),
    ((10, 4, 7, 1, 9, 2), 2),
    ((5, 5, 8, 2, 9, 1), 3),
    ((20, 15, 30, 5, 25), 2),
    ((1, 2, 3, 4, 5, 6, 7), 4),
    ((8, 3, 12, 7, 15, 2), 3),
    ((100, 50, 200, 25, 150), 2),
    ((6, 11, 3, 14, 9, 1), 4),
    ((13, 26, 7, 39, 18), 3),
    ((4, 8, 16, 2, 32, 1), 2),
    ((9, 18, 27, 6, 36), 3),
    ((11, 22, 5, 33, 17), 2),
    ((2, 7, 13, 21, 4, 30), 4),
    ((14, 3, 28, 9, 42), 3),
    ((17, 34, 8, 51, 25), 2),
    ((5, 12, 19, 26, 3, 40), 3),
    ((23, 46, 11, 69, 35), 2),
    ((6, 13, 20, 27, 34, 4), 4),
    ((31, 62, 15, 93, 47), 3),
    ((7, 21, 35, 49, 14), 2),
)

_P306 = _page(
    "algo-top-k",
    306,
    "A heap that only ever holds the best k",
    "Push everything, pop the smallest whenever the heap outgrows k.",
    "Sorting the whole list to take the top three does far more work than "
    "the question needs. Keep a min-heap of size k instead: push each "
    "number, and if the heap is now too big throw away its smallest. What "
    "survives is the k largest, and the smallest of those — the k-th "
    "largest, which is what the question usually actually wants — is "
    "sitting at best[0] for free. Python's heapq is a min-heap, and that "
    "is exactly why this works.",
    "algo_top_k",
    [
        (
            f"Keep the {k} largest of {_seq(items)} using a heap that never "
            f"grows past {k}. Print the smallest one still in it, then all "
            f"of them sorted biggest first.",
            {"items": items, "k": k},
        )
        for items, k in _TOP_K
    ],
)


# ── 307. The same subproblem, answered once ──────────────────

_GRIDS = (
    (3, 3),
    (3, 4),
    (4, 3),
    (4, 4),
    (3, 5),
    (5, 3),
    (4, 5),
    (5, 4),
    (5, 5),
    (3, 6),
    (6, 3),
    (4, 6),
    (6, 4),
    (5, 6),
    (6, 5),
    (6, 6),
    (3, 7),
    (7, 3),
    (4, 7),
    (7, 4),
)

_P307 = _page(
    "algo-memo-grid",
    307,
    "The same subproblem, answered once",
    "A dict between the recursion and the work.",
    "The plain recursion here is correct and unusable: it asks how many "
    "paths lead from the same square over and over, and the number of "
    "calls doubles with the grid. Three lines fix it — look in the dict "
    "first, store before returning — and the count of stored entries "
    "printed at the end is exactly how many distinct subproblems there "
    "were. That number is the whole argument: everything else was a "
    "repeat.",
    "algo_memo_grid",
    [
        (
            f"Count the paths from the top left to the bottom right of a "
            f"{rows} by {cols} grid moving only down and right. Recurse, and "
            f"keep answers in a dict keyed by square. Print the count and "
            f"how many squares ended up in the dict.",
            {"rows": rows, "cols": cols},
        )
        for rows, cols in _GRIDS
    ],
)


# ── 308. Filling a table ─────────────────────────────────────

_TABLES = (
    (10, 5),
    (12, 6),
    (8, 4),
    (15, 7),
    (9, 5),
    (14, 8),
    (11, 6),
    (16, 9),
    (7, 4),
    (13, 7),
    (18, 10),
    (6, 3),
    (17, 8),
    (20, 12),
    (19, 11),
    (5, 3),
    (22, 13),
    (21, 14),
    (24, 15),
    (25, 16),
)

_P308 = _page(
    "algo-dp-table",
    308,
    "Filling a table in an order that always works",
    "The same answers as the memo, built forwards instead of found backwards.",
    "Page 307 recursed and remembered. This fills the same answers in from "
    "the bottom, and needs no recursion at all — because if you go in "
    "order, everything a row depends on is already behind you. Ways to "
    "climb i steps is ways to climb i-1 plus ways to climb i-2, which is "
    "Fibonacci wearing a hat. Start the table at ways[0] = 1: there is "
    "exactly one way to stand still, and getting that seed wrong is the "
    "usual bug.",
    "algo_dp_table",
    [
        (
            f"Count the ways to climb {steps} steps taking one or two at a "
            f"time. Fill a table from the bottom, where each entry is the "
            f"two before it added. Print the answer for {steps} steps and "
            f"the entry for {peek}.",
            {"steps": steps, "peek": peek},
        )
        for steps, peek in _TABLES
    ],
)


ALGO_PAGES_2: tuple[Page, ...] = (
    _P299,
    _P300,
    _P301,
    _P302,
    _P303,
    _P304,
    _P305,
    _P306,
    _P307,
    _P308,
)
