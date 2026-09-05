"""Pages 319-328: the harder variants.

The thirty pages before these covered the thirteen interview patterns. These
are the ones that turn up when a problem is a step past its pattern — a
window that has to remember its maximum, a search that runs over answers
rather than over data, a structure built because the obvious one is too
slow.

Four are worth the tier on their own. Binary search on the answer (323) is
the trick nobody sees coming, because the thing being searched is not the
input. Union-find (325) makes connectivity questions almost trivial. A trie
(326) turns "how many start with this" from a scan into a walk. And the
monotonic deque (320) is what makes sliding-window maximum linear when
every obvious approach is not.
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


def _spans(items) -> str:
    return ", ".join(f"{a}-{b}" for a, b in items)


def _grid_words(grid) -> str:
    return " / ".join("".join(str(v) for v in row) for row in grid)


# ── 319. Spreading across a grid ─────────────────────────────

_GRIDS = (
    ((1, 1, 0, 0), (1, 0, 0, 1), (1, 0, 0, 0)),
    ((0, 1, 1, 0), (1, 0, 0, 0), (1, 0, 1, 1)),
    ((0, 1, 1, 0), (1, 1, 0, 1), (0, 0, 0, 0)),
    ((1, 0, 0), (1, 1, 0), (0, 0, 1)),
    ((0, 0, 0, 0), (1, 1, 0, 1), (1, 1, 0, 0)),
    ((0, 0, 1), (1, 1, 0), (1, 0, 1)),
    ((1, 1, 0), (0, 0, 1), (1, 1, 0)),
    ((0, 1, 0, 1), (1, 0, 0, 0), (1, 1, 0, 0)),
    ((0, 1, 0), (1, 0, 1), (0, 1, 1)),
    ((1, 1, 0, 1), (1, 0, 0, 0), (1, 1, 1, 0)),
    ((1, 0, 1), (0, 0, 1), (0, 1, 0)),
    ((1, 1, 1), (0, 0, 1), (1, 0, 0)),
    ((0, 0, 1), (0, 0, 0), (1, 1, 0)),
    ((0, 0, 0, 0), (0, 1, 0, 1), (1, 1, 0, 1)),
    ((0, 1, 0), (1, 0, 1), (1, 0, 0)),
    ((1, 0, 1, 1), (1, 0, 1, 0), (1, 1, 0, 1)),
    ((0, 1, 0), (0, 1, 0), (1, 0, 0)),
    ((1, 0, 0, 0), (0, 0, 0, 1), (0, 1, 1, 0)),
    ((0, 0, 0), (0, 0, 1), (1, 0, 1)),
    ((0, 0, 1, 0), (0, 0, 1, 1), (0, 1, 0, 0)),
)

_P319 = _page(
    "algo-grid-flood",
    319,
    "Spreading out across a grid",
    "A grid is a graph. Each cell's neighbours are its four sides.",
    "Once you see that a grid is just a graph with the edges implied, the "
    "island problems stop being their own thing — this is page 303's walk "
    "with the neighbours worked out rather than looked up. The seen set is "
    "doing double duty: it stops the walk going round in circles, and it is "
    "how the outer loop knows which cells have already been counted.",
    "algo_grid_flood",
    [
        (
            f"In the grid {_grid_words(grid)} — rows separated by slashes, "
            f"1 for land — count the islands joined up and down and left to "
            f"right, and print how many there are and the size of the "
            f"biggest.",
            {"grid": grid},
        )
        for grid in _GRIDS
    ],
)


# ── 320. A window that remembers its largest ─────────────────

_WINDOW_MAX = (
    ((4, 1, 2, 16, 5, 7), 2),
    ((5, 15, 3, 4, 11), 3),
    ((2, 7, 6, 14, 15, 12, 12, 13), 2),
    ((6, 4, 1, 11, 3, 13, 7, 11), 3),
    ((4, 6, 13, 5, 11, 12), 3),
    ((13, 7, 6, 3, 11), 3),
    ((1, 4, 9, 9, 9, 11), 4),
    ((14, 4, 15, 3, 2, 13, 6, 13), 3),
    ((13, 10, 12, 10, 16, 9, 10, 10), 2),
    ((8, 2, 6, 14, 13), 2),
    ((13, 2, 11, 3, 8, 14), 4),
    ((9, 8, 2, 4, 15, 5), 2),
    ((4, 2, 14, 15, 4, 7, 2, 12), 4),
    ((9, 14, 12, 5, 10, 5, 8, 16), 2),
    ((10, 12, 9, 9, 7, 9, 8, 7), 2),
    ((7, 2, 2, 1, 9, 9, 14, 1), 4),
    ((8, 12, 16, 16, 12), 2),
    ((11, 16, 5, 3, 4, 15), 4),
    ((15, 14, 9, 13, 5), 3),
    ((15, 11, 3, 3, 14), 4),
)

_P320 = _page(
    "algo-window-max",
    320,
    "A window that remembers its largest",
    "A deque of positions, kept so the front is always the answer.",
    "Taking max of every window is the width times the length. The trick is "
    "what you throw away: when a new number arrives, every smaller number "
    "still waiting is now useless — it can never be the maximum again, "
    "because the newcomer is bigger and will outlast it. Drop those, and "
    "the front of the deque is always the answer. Each position is added "
    "once and removed once, so the whole thing is one pass.",
    "algo_window_max",
    [
        (
            f"Slide a window {width} wide along {_seq(items)} and print the "
            f"largest in each position, joined by commas, then the biggest "
            f"of those. Keep a deque of positions and drop any that a new "
            f"number has made useless.",
            {"items": items, "width": width},
        )
        for items, width in _WINDOW_MAX
    ],
)


# ── 321. Taking as many as will fit ──────────────────────────

_PICKS = (
    ((1, 3), (2, 5), (4, 7), (6, 9)),
    ((0, 2), (1, 4), (3, 6), (5, 7)),
    ((1, 4), (2, 3), (3, 5), (4, 6)),
    ((2, 6), (3, 4), (5, 8), (7, 9)),
    ((0, 3), (2, 5), (4, 6), (6, 8)),
    ((1, 5), (2, 4), (6, 9), (8, 10)),
    ((3, 7), (4, 5), (6, 8), (7, 10)),
    ((0, 4), (1, 2), (3, 6), (5, 9)),
    ((2, 8), (3, 5), (4, 6), (7, 9)),
    ((1, 6), (2, 3), (5, 8), (7, 11)),
    ((0, 5), (1, 3), (4, 7), (6, 10)),
    ((2, 4), (3, 8), (5, 6), (7, 9)),
    ((1, 7), (2, 4), (3, 5), (6, 8)),
    ((0, 6), (2, 3), (4, 8), (5, 7)),
    ((3, 9), (4, 6), (5, 7), (8, 10)),
    ((1, 2), (2, 6), (4, 5), (7, 9)),
    ((2, 7), (3, 4), (5, 9), (6, 8)),
    ((0, 8), (1, 4), (3, 5), (6, 9)),
    ((4, 10), (5, 6), (7, 8), (9, 11)),
    ((1, 9), (2, 5), (3, 4), (6, 10)),
)

_P321 = _page(
    "algo-intervals-pick",
    321,
    "Taking as many as will fit",
    "Sort by when they end, then take greedily.",
    "The instinct is to sort by start, or by length, and both give the "
    "wrong answer. Sorting by *end* is what works, and the reason is worth "
    "holding: the one that finishes soonest leaves the most room for "
    "everything after it, so taking it is never a mistake. That argument — "
    "this choice cannot make things worse — is what separates a greedy "
    "algorithm that works from one that only usually does.",
    "algo_intervals_pick",
    [
        (
            f"From the spans {_spans(spans)}, take as many as you can "
            f"without any two overlapping. Sort by end, then take each one "
            f"that starts after the last one you took. Print how many and "
            f"which.",
            {"spans": spans},
        )
        for spans in _PICKS
    ],
)


# ── 322. The longest run two sequences share ─────────────────

_LCS = (
    ('stone', 'longest'),
    ('python', 'typhoon'),
    ('garden', 'grades'),
    ('silent', 'listen'),
    ('banana', 'cabana'),
    ('winter', 'writer'),
    ('marker', 'market'),
    ('candle', 'sandal'),
    ('pointer', 'printer'),
    ('silver', 'sliver'),
    ('bright', 'blight'),
    ('planet', 'plants'),
    ('stream', 'steamer'),
    ('border', 'broader'),
    ('mother', 'harbour'),
    ('smother', 'arbour'),
    ('copper', 'cooper'),
    ('thread', 'treads'),
    ('shelter', 'shatter'),
    ('cellar', 'caller'),
)

_P322 = _page(
    "algo-lcs",
    322,
    "The longest run two sequences share",
    "A table where each cell asks one smaller question.",
    "This is the shape of every two-sequence problem — edit distance, diff, "
    "sequence alignment — and it is always the same table. Each cell asks: "
    "if these two letters match, it is one more than the answer without "
    "either; if they do not, it is the better of dropping one or dropping "
    "the other. Filling it row by row means both of those are already "
    "behind you. The second number printed is the size of the table, which "
    "is what it costs.",
    "algo_lcs",
    [
        (
            f'Find the longest subsequence "{first}" and "{second}" share — '
            f"letters in order but not necessarily together. Fill a table "
            f"and print its length, then the size of the table you filled.",
            {"first": first, "second": second},
        )
        for first, second in _LCS
    ],
)


# ── 323. Searching the answers ───────────────────────────────

_SEARCH_ANSWER = (
    ((8, 11, 8, 5, 1, 2, 5), 2),
    ((10, 2, 12, 5, 8, 12, 12), 3),
    ((3, 4, 6, 11, 12, 6), 3),
    ((6, 12, 8, 10, 10), 4),
    ((8, 9, 5, 8, 6, 4), 3),
    ((9, 4, 2, 6, 6, 1, 6), 4),
    ((10, 7, 4, 12, 10, 6), 3),
    ((3, 10, 10, 3, 3, 2, 8), 3),
    ((4, 9, 1, 9, 3), 4),
    ((1, 11, 7, 2, 10, 9), 3),
    ((2, 6, 2, 5, 12, 2, 6), 2),
    ((4, 12, 4, 8, 9, 6), 3),
    ((6, 6, 6, 11, 3, 8), 3),
    ((12, 2, 12, 10, 1, 7, 11), 3),
    ((7, 2, 8, 9, 11), 2),
    ((6, 12, 1, 2, 7, 7, 3), 2),
    ((3, 11, 7, 11, 3, 6, 4), 3),
    ((9, 5, 5, 1, 8, 5), 4),
    ((10, 8, 1, 6, 2), 2),
    ((10, 9, 4, 8, 3, 5), 3),
)

_P323 = _page(
    "algo-search-answer",
    323,
    "Searching the answers, not the data",
    "Binary search over the possible answers, with a feasibility check.",
    "This is the one nobody sees coming. There is nothing sorted to search "
    "— the list is in whatever order it came. What is sorted is the "
    "*answers*: if a capacity of 20 works then so does 21, and if 19 fails "
    "then so does 18. That monotonicity is all binary search needs. So you "
    "halve the range of possible capacities and ask a yes-or-no question "
    "each time. Whenever a problem says smallest-that-works or "
    "largest-that-fits, this is the shape.",
    "algo_search_answer",
    [
        (
            f"Ship the weights {_seq(weights)} in order, within {days} days. "
            f"Find the smallest daily capacity that manages it, by binary "
            f"searching the capacities and counting days for each. Print the "
            f"capacity and the days it takes.",
            {"weights": weights, "days": days},
        )
        for weights, days in _SEARCH_ANSWER
    ],
)


# ── 324. The middle value as things arrive ───────────────────

_MEDIANS = (
    (5, 15, 1, 3), (2, 8, 4, 6), (10, 2, 7, 5), (1, 9, 3, 7),
    (6, 2, 11, 4), (3, 12, 5, 8), (7, 1, 9, 4), (4, 14, 6, 2),
    (8, 3, 10, 5), (2, 13, 7, 9), (5, 11, 2, 8), (9, 4, 12, 6),
    (1, 6, 10, 3), (7, 15, 4, 11), (3, 9, 6, 12), (5, 2, 8, 14),
    (11, 5, 9, 2), (4, 10, 7, 13), (6, 1, 12, 8), (2, 7, 15, 5),
)

_P324 = _page(
    "algo-two-heaps",
    324,
    "The middle value, kept as things arrive",
    "Two heaps facing each other, kept the same size.",
    "Sorting after every arrival to find the middle is n log n each time. "
    "Two heaps hold it instead: a max-heap of the smaller half and a "
    "min-heap of the larger, with the middle always sitting at one or both "
    "of their fronts. The push-then-move-then-rebalance dance is what keeps "
    "them the right sizes — push into one, move its top to the other, and "
    "move back only if the sizes went wrong. Python has no max-heap, hence "
    "the negatives.",
    "algo_two_heaps",
    [
        (
            f"As each of {_seq(items)} arrives, print the middle value so "
            f"far — the average of the two middles when there is an even "
            f"number. Keep two heaps. Print all the middles, then the last.",
            {"items": items},
        )
        for items in _MEDIANS
    ],
)


# ── 325. Joining groups ──────────────────────────────────────

_UNIONS = (
    (6, ((0, 1), (1, 2), (3, 4), (0, 2)), (0, 2)),
    (6, ((0, 1), (2, 3), (4, 5), (1, 0)), (0, 3)),
    (7, ((0, 1), (1, 2), (2, 0), (3, 4)), (0, 2)),
    (5, ((0, 1), (1, 2), (0, 2)), (1, 2)),
    (8, ((0, 1), (2, 3), (4, 5), (0, 1)), (2, 3)),
    (6, ((1, 2), (2, 3), (1, 3), (4, 5)), (1, 3)),
    (7, ((0, 1), (1, 2), (3, 4), (4, 5), (0, 2)), (3, 5)),
    (5, ((0, 1), (2, 3), (1, 0)), (2, 3)),
    (9, ((0, 1), (1, 2), (3, 4), (5, 6), (2, 0)), (0, 1)),
    (6, ((0, 2), (2, 4), (0, 4), (1, 3)), (0, 4)),
    (7, ((1, 2), (3, 4), (5, 6), (2, 1)), (5, 6)),
    (8, ((0, 1), (1, 2), (2, 3), (0, 3), (4, 5)), (0, 3)),
    (5, ((0, 1), (1, 2), (2, 0)), (0, 1)),
    (6, ((0, 3), (1, 4), (2, 5), (3, 0)), (1, 4)),
    (7, ((0, 1), (2, 3), (4, 5), (1, 2), (0, 3)), (0, 3)),
    (6, ((1, 3), (3, 5), (1, 5), (0, 2)), (1, 5)),
    (8, ((0, 1), (2, 3), (4, 5), (6, 7), (1, 0)), (6, 7)),
    (5, ((0, 2), (1, 3), (2, 0)), (1, 3)),
    (9, ((0, 1), (1, 2), (2, 3), (4, 5), (3, 0)), (4, 5)),
    (7, ((0, 1), (2, 4), (4, 6), (2, 6), (3, 5)), (2, 6)),
)

_P325 = _page(
    "algo-union-find",
    325,
    "Joining groups and asking what is connected",
    "Every item points at a parent; the root is the group.",
    "For connectivity, this is almost cheating. Each item points at its "
    "parent and the root names the group, so joining two groups is one "
    "pointer and asking whether two things are connected is two walks up. "
    "The line that flattens as it walks — parent[x] = parent[parent[x]] — "
    "is what keeps those walks short, and the join returning False when "
    "both are already in the same group is how you detect a cycle for free.",
    "algo_union_find",
    [
        (
            f"Start with {count} separate items and join "
            + ", ".join(f"{x} to {y}" for x, y in joins)
            + f". Print how many groups are left, how many joins actually "
            f"merged anything, and whether {ask[0]} and {ask[1]} ended up "
            f"together.",
            {"count": count, "joins": joins, "ask": ask},
        )
        for count, joins, ask in _UNIONS
    ],
)


# ── 326. A tree of prefixes ──────────────────────────────────

_TRIES = (
    (("cat", "car", "dog"), "ca", "z"),
    (("bat", "bath", "bar", "owl"), "ba", "q"),
    (("tin", "tip", "top", "ash"), "ti", "x"),
    (("plum", "plot", "play", "oak"), "pl", "z"),
    (("stone", "stop", "star", "elm"), "st", "y"),
    (("hen", "her", "hem", "cow"), "he", "q"),
    (("fern", "ferry", "fern2", "oak"), "fer", "z"),
    (("moss", "moth", "mole", "ash"), "mo", "x"),
    (("rain", "rail", "raid", "sun"), "rai", "q"),
    (("gold", "golf", "gone", "tin"), "gol", "z"),
    (("sand", "sane", "sank", "elm"), "san", "y"),
    (("wind", "wine", "wing", "oak"), "win", "x"),
    (("lake", "lane", "lamb", "fir"), "la", "z"),
    (("bark", "barn", "bard", "owl"), "bar", "q"),
    (("mist", "mile", "mind", "yew"), "mi", "z"),
    (("reed", "reef", "reel", "oak"), "ree", "x"),
    (("vine", "vice", "view", "ash"), "vi", "q"),
    (("hark", "harm", "harp", "elm"), "har", "z"),
    (("dusk", "dust", "duel", "fir"), "du", "y"),
    (("clay", "claw", "clan", "oak"), "cla", "x"),
)

_P326 = _page(
    "algo-trie",
    326,
    "A tree of prefixes",
    "Nested dicts, one level per letter.",
    "How many words start with these letters? Scanning every word is the "
    "length of the list times the length of the prefix, every time you ask. "
    "A trie makes it the length of the prefix alone: walk down one level "
    "per letter and everything below where you stop is an answer. The dot "
    "marks where a word ends, because a prefix can be a word and a longer "
    "word at once. This is what autocomplete is.",
    "algo_trie",
    [
        (
            "Build a trie of nested dicts from "
            + ", ".join(f'"{w}"' for w in words)
            + f', marking word ends. Print how many start with "{prefix}", '
            f'how many start with "{missing}", and how many letters the '
            f"root has.",
            {"words": words, "prefix": prefix, "missing": missing},
        )
        for words, prefix, missing in _TRIES
    ],
)


# ── 327. Totals over a rectangle ─────────────────────────────

_MATRICES = (
    (((1, 2, 3), (4, 5, 6), (7, 8, 9)), (0, 0, 1, 1)),
    (((1, 2, 3), (4, 5, 6), (7, 8, 9)), (1, 1, 2, 2)),
    (((2, 4, 6), (1, 3, 5), (7, 9, 11)), (0, 1, 2, 2)),
    (((1, 1, 1), (1, 1, 1), (1, 1, 1)), (0, 0, 2, 1)),
    (((5, 2, 8), (3, 7, 1), (9, 4, 6)), (1, 0, 2, 1)),
    (((10, 20), (30, 40), (50, 60)), (0, 0, 1, 1)),
    (((1, 3, 5, 7), (2, 4, 6, 8)), (0, 1, 1, 2)),
    (((9, 8, 7), (6, 5, 4), (3, 2, 1)), (0, 0, 1, 2)),
    (((2, 2, 2), (2, 2, 2), (2, 2, 2)), (1, 1, 2, 2)),
    (((1, 5, 9), (2, 6, 10), (3, 7, 11)), (0, 2, 2, 2)),
    (((4, 8, 12), (16, 20, 24), (28, 32, 36)), (1, 0, 1, 2)),
    (((3, 1, 4), (1, 5, 9), (2, 6, 5)), (0, 0, 2, 0)),
    (((7, 2, 9), (4, 6, 1), (8, 3, 5)), (1, 1, 2, 2)),
    (((1, 2), (3, 4), (5, 6), (7, 8)), (1, 0, 2, 1)),
    (((11, 12, 13), (14, 15, 16), (17, 18, 19)), (0, 1, 1, 2)),
    (((6, 3, 8), (2, 9, 4), (7, 1, 5)), (0, 0, 1, 1)),
    (((20, 10, 30), (40, 50, 60), (70, 80, 90)), (1, 1, 2, 2)),
    (((1, 4, 7), (2, 5, 8), (3, 6, 9)), (2, 0, 2, 2)),
    (((5, 5, 5, 5), (5, 5, 5, 5)), (0, 1, 1, 2)),
    (((2, 7, 1), (8, 2, 8), (1, 8, 2)), (0, 1, 2, 2)),
)

_P327 = _page(
    "algo-prefix-matrix",
    327,
    "Totals over a rectangle",
    "Page 297's running total, with a second dimension.",
    "The one-dimensional version was one subtraction. In two it is a "
    "subtraction, another subtraction, and an addition to put back the "
    "corner you removed twice — inclusion and exclusion, and drawing the "
    "four rectangles on paper is the only way it ever makes sense. Built "
    "once, any rectangle's total is four lookups regardless of how large "
    "it is.",
    "algo_prefix_matrix",
    [
        (
            f"Build a running-total grid for {_grid_words(grid)} — rows "
            f"separated by slashes — with a zero row and column in front. "
            f"Print the total of the rectangle from row {box[0]} column "
            f"{box[1]} to row {box[2]} column {box[3]}, then the total of "
            f"the whole grid.",
            {"grid": grid, "box": box},
        )
        for grid, box in _MATRICES
    ],
)


# ── 328. The cheapest way ────────────────────────────────────

_ROADS = (
    ((("a", "b", 1), ("b", "c", 1), ("a", "c", 5)), "a", "c"),
    ((("a", "b", 2), ("b", "d", 2), ("a", "d", 9)), "a", "d"),
    ((("s", "t", 3), ("t", "u", 1), ("s", "u", 7)), "s", "u"),
    ((("p", "q", 1), ("q", "r", 2), ("p", "r", 6)), "p", "r"),
    ((("m", "n", 4), ("n", "o", 1), ("m", "o", 8)), "m", "o"),
    ((("x", "y", 2), ("y", "z", 3), ("x", "z", 9)), "x", "z"),
    ((("a", "b", 1), ("b", "c", 2), ("c", "d", 1), ("a", "d", 7)), "a", "d"),
    ((("h", "i", 3), ("i", "j", 2), ("h", "j", 8)), "h", "j"),
    ((("e", "f", 1), ("f", "g", 1), ("e", "g", 4)), "e", "g"),
    ((("k", "l", 2), ("l", "m", 2), ("k", "m", 6)), "k", "m"),
    ((("a", "c", 2), ("c", "e", 3), ("a", "e", 10)), "a", "e"),
    ((("b", "d", 1), ("d", "f", 4), ("b", "f", 9)), "b", "f"),
    ((("n", "p", 3), ("p", "q", 1), ("n", "q", 7)), "n", "q"),
    ((("r", "s", 2), ("s", "t", 4), ("r", "t", 9)), "r", "t"),
    ((("u", "v", 1), ("v", "w", 3), ("u", "w", 6)), "u", "w"),
    ((("a", "b", 3), ("b", "c", 3), ("a", "c", 8)), "a", "c"),
    ((("g", "h", 2), ("h", "k", 2), ("g", "k", 7)), "g", "k"),
    ((("l", "n", 1), ("n", "r", 5), ("l", "r", 9)), "l", "r"),
    ((("t", "v", 4), ("v", "x", 1), ("t", "x", 8)), "t", "x"),
    ((("c", "f", 2), ("f", "j", 2), ("c", "j", 7)), "c", "j"),
)

_P328 = _page(
    "algo-dijkstra",
    328,
    "The cheapest way, not the shortest",
    "Breadth first with a heap instead of a queue, once the steps cost.",
    "Breadth first finds fewest hops because every step costs the same. "
    "Give the steps different costs and that breaks — one hop down an "
    "expensive road can be worse than three cheap ones, and every graph "
    "here is built so the direct route is the dearer one. Swap the queue "
    "for a heap ordered by cost so far, and the first time you reach "
    "somewhere is again the best time. That is the whole change: a heap "
    "instead of a queue.",
    "algo_dijkstra",
    [
        (
            "Given the roads "
            + ", ".join(f"{x} to {y} costing {w}" for x, y, w in edges)
            + f", find the cheapest total cost from {start} to {goal} using "
            f"a heap ordered by cost so far. Print that cost and how many "
            f"places you found a best cost for.",
            {"edges": edges, "start": start, "goal": goal},
        )
        for edges, start, goal in _ROADS
    ],
)


ALGO_PAGES_4: tuple[Page, ...] = (
    _P319, _P320, _P321, _P322, _P323, _P324, _P325, _P326, _P327, _P328,
)
