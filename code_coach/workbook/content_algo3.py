"""Pages 309-318: pointers you rewire, and order you work out.

Linked lists are where the move *is* the pointer handling. No index to fall
back on, so reversing, finding the middle and spotting a loop are all one
skill: hold the right number of references and let go in the right order.
Six pages, because that skill only arrives by repetition.

Topological sort is the other half — count what each thing is waiting for,
take whatever is waiting for nothing, repeat. The same code detects an
impossible cycle for free, which is page 316.

Then two that earn their place on usefulness alone: a monotonic stack,
which turns "the next bigger one" from a nested loop into one pass, and
merging overlapping ranges, which is a sort and a single comparison.

With these the workbook covers all thirteen LeetCode patterns.
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


def _arrows(items) -> str:
    return " -> ".join(str(n) for n in items)


def _spans(items) -> str:
    return ", ".join(f"{a}-{b}" for a, b in items)


# ── 309. A chain of nodes ────────────────────────────────────

_WALKS = (
    (1, 2, 3),
    (5, 10, 15, 20),
    (7, 14, 21),
    (2, 4, 6, 8, 10),
    (9, 8, 7),
    (11, 22, 33, 44),
    (3, 6, 9, 12),
    (100, 200, 300),
    (4, 8, 12, 16, 20),
    (13, 26, 39),
    (6, 12, 18, 24),
    (17, 34, 51),
    (1, 4, 9, 16, 25),
    (30, 20, 10),
    (8, 16, 24, 32),
    (2, 3, 5, 7, 11),
    (25, 50, 75),
    (5, 15, 25, 35),
    (12, 24, 36, 48),
    (19, 38, 57),
)

_P309 = _page(
    "algo-list-walk",
    309,
    "A chain of nodes, and walking to the end",
    "A Node with a value and a next, and the while that follows it.",
    "There is no length and no index — the only thing a node knows is the "
    "one after it, and the only way to reach the end is to walk. The loop "
    "condition is `while node is not None`, never `while node.nxt`, "
    "because the last node is real and its next is what is missing. "
    "Building the chain backwards with reversed is the tidy trick: each "
    "new node points at what you already have.",
    "algo_list_walk",
    [
        (
            f"Build the linked list {_arrows(items)} from a Node class with "
            f"a value and a next. Walk it to the end, printing the values "
            f"joined by commas, how many nodes there were, and the last "
            f"value.",
            {"items": items},
        )
        for items in _WALKS
    ],
)


# ── 310. Turning every arrow round ───────────────────────────

_REVERSES = (
    (1, 2, 3),
    (5, 10, 15, 20),
    (7, 14, 21),
    (2, 4, 6, 8),
    (9, 8, 7),
    (11, 22, 33, 44),
    (3, 6, 9, 12),
    (100, 200, 300),
    (4, 8, 12, 16, 20),
    (13, 26, 39),
    (6, 12, 18, 24),
    (17, 34, 51),
    (1, 4, 9, 16),
    (30, 20, 10),
    (8, 16, 24, 32),
    (2, 3, 5, 7, 11),
    (25, 50, 75),
    (5, 15, 25, 35),
    (12, 24, 36, 48),
    (19, 38, 57),
)

_P310 = _page(
    "algo-list-reverse",
    310,
    "Turning every arrow round, one at a time",
    "Three references — previous, current, and the one you must not lose.",
    "This is the page that makes linked lists click. Reversing means "
    "pointing each node at the one before it, but the moment you do that "
    "you have thrown away the way forward — so you save it first. Four "
    "lines in a fixed order: remember what is after, point backwards, move "
    "previous up, move current on. Write them in any other order and the "
    "chain falls apart. The new head is previous, not node, because node "
    "has walked off the end.",
    "algo_list_reverse",
    [
        (
            f"Build {_arrows(items)} as a linked list and reverse it in "
            f"place with previous, current and a saved next. Print the "
            f"reversed values joined by commas, then the new head's value.",
            {"items": items},
        )
        for items in _REVERSES
    ],
)


# ── 311. One pointer twice as fast ───────────────────────────

_MIDDLES = (
    (1, 2, 3, 4, 5),
    (10, 20, 30, 40),
    (7, 14, 21, 28, 35),
    (2, 4, 6, 8, 10, 12),
    (9, 8, 7, 6),
    (11, 22, 33, 44, 55),
    (3, 6, 9, 12, 15, 18),
    (100, 200, 300, 400),
    (4, 8, 12, 16, 20),
    (13, 26, 39, 52),
    (6, 12, 18, 24, 30, 36),
    (17, 34, 51, 68),
    (1, 4, 9, 16, 25),
    (30, 25, 20, 15),
    (8, 16, 24, 32, 40),
    (2, 3, 5, 7, 11, 13),
    (25, 50, 75, 100),
    (5, 15, 25, 35, 45),
    (12, 24, 36, 48, 60, 72),
    (19, 38, 57, 76),
)

_P311 = _page(
    "algo-list-middle",
    311,
    "One pointer twice as fast as the other",
    "Fast moves two, slow moves one — so slow lands on the middle.",
    "You cannot ask a linked list how long it is without walking it, and "
    "walking it twice is a waste. Move one pointer at double speed "
    "instead: when the fast one runs out, the slow one is exactly halfway. "
    "The loop condition has to check both `fast` and `fast.nxt`, because "
    "stepping two at a time can leap straight over the end — and that "
    "missing check is the crash everybody writes once.",
    "algo_list_middle",
    [
        (
            f"Build {_arrows(items)} as a linked list and find the middle "
            f"node with a slow pointer and a fast one. Print the middle "
            f"value, then the half-length to check it.",
            {"items": items},
        )
        for items in _MIDDLES
    ],
)


# ── 312. The two that must meet ──────────────────────────────

_CYCLES = (
    ((1, 2, 3, 4), 1),
    ((1, 2, 3, 4), None),
    ((5, 10, 15, 20, 25), 2),
    ((5, 10, 15, 20, 25), None),
    ((7, 14, 21), 0),
    ((7, 14, 21), None),
    ((2, 4, 6, 8), 3),
    ((2, 4, 6, 8), None),
    ((9, 18, 27, 36, 45), 1),
    ((9, 18, 27, 36, 45), None),
    ((3, 6, 9, 12), 2),
    ((3, 6, 9, 12), None),
    ((11, 22, 33), 1),
    ((11, 22, 33), None),
    ((4, 8, 12, 16, 20), 0),
    ((4, 8, 12, 16, 20), None),
    ((6, 12, 18, 24), 1),
    ((6, 12, 18, 24), None),
    ((13, 26, 39, 52, 65), 3),
    ((13, 26, 39, 52, 65), None),
)

_P312 = _page(
    "algo-list-cycle",
    312,
    "The two pointers that must meet if it loops",
    "Floyd's: if there is a loop, fast catches slow. If not, fast escapes.",
    "The argument is simpler than it looks. Once both pointers are inside "
    "a loop, fast gains exactly one place on slow every step — so it "
    "cannot jump past, it must land on it. And if there is no loop, fast "
    "reaches the end and the question is settled. Two pointers, no extra "
    "memory, and the alternative is a set of every node you have seen. "
    "The pages alternate: the same chain looped and not looped.",
    "algo_list_cycle",
    [
        (
            f"Build {_arrows(items)} as a linked list"
            + (
                f", then point the last node back at position {link}. "
                if link is not None
                else ", leaving the last node pointing at nothing. "
            )
            + "Use a slow pointer and a fast one to decide whether it "
            "loops, and print the answer.",
            {"items": items, "links_to": link},
        )
        for items, link in _CYCLES
    ],
)


# ── 313. Two sorted chains zipped ────────────────────────────

_MERGES = (
    ((1, 3, 5), (2, 4, 6)),
    ((1, 2, 4), (1, 3, 4)),
    ((10, 30, 50), (20, 40, 60)),
    ((5, 15), (10, 20, 25)),
    ((2, 6, 10), (4, 8, 12)),
    ((1, 5, 9), (3, 7, 11)),
    ((7, 21), (14, 28, 35)),
    ((3, 9, 15), (6, 12, 18)),
    ((11, 33), (22, 44, 55)),
    ((4, 12, 20), (8, 16, 24)),
    ((13, 39), (26, 52)),
    ((6, 18, 30), (12, 24, 36)),
    ((17, 51), (34, 68)),
    ((2, 8, 14), (5, 11, 17)),
    ((25, 75), (50, 100)),
    ((9, 27, 45), (18, 36, 54)),
    ((1, 4, 7), (2, 5, 8)),
    ((16, 48), (32, 64)),
    ((3, 12, 21), (6, 15, 24)),
    ((19, 57), (38, 76)),
)

_P313 = _page(
    "algo-list-merge",
    313,
    "Two sorted chains zipped into one",
    "A dummy head, so there is no special case for the first node.",
    "Both chains are sorted, so the smallest thing left is always at the "
    "front of one of them — take it, advance that one, repeat. The dummy "
    "node at the start is the trick worth stealing: without it the first "
    "append needs its own branch because there is no tail yet. Build "
    "everything onto a node you throw away and return front.nxt.",
    "algo_list_merge",
    [
        (
            f"Build {_arrows(first)} and {_arrows(second)} as two sorted "
            f"linked lists and merge them into one sorted chain, using a "
            f"dummy head. Print the merged values joined by commas and how "
            f"many there are.",
            {"first": first, "second": second},
        )
        for first, second in _MERGES
    ],
)


# ── 314. A fixed gap ─────────────────────────────────────────

_GAPS = (
    ((1, 2, 3, 4, 5), 2),
    ((10, 20, 30, 40), 2),
    ((7, 14, 21, 28, 35), 3),
    ((2, 4, 6, 8, 10, 12), 4),
    ((9, 8, 7, 6, 5), 2),
    ((11, 22, 33, 44, 55), 3),
    ((3, 6, 9, 12, 15), 4),
    ((100, 200, 300, 400), 3),
    ((4, 8, 12, 16, 20, 24), 5),
    ((13, 26, 39, 52), 2),
    ((6, 12, 18, 24, 30), 3),
    ((17, 34, 51, 68, 85), 4),
    ((1, 4, 9, 16, 25), 2),
    ((30, 25, 20, 15, 10), 3),
    ((8, 16, 24, 32, 40), 4),
    ((2, 3, 5, 7, 11, 13), 5),
    ((25, 50, 75, 100), 2),
    ((5, 15, 25, 35, 45), 3),
    ((12, 24, 36, 48, 60), 4),
    ((19, 38, 57, 76), 3),
)

_P314 = _page(
    "algo-list-gap",
    314,
    "A fixed gap held while both pointers walk",
    "Send one ahead by n, then move both until it falls off the end.",
    "Counting from the end of a chain sounds like it needs the length, and "
    "it does not. Put one pointer n ahead, then walk both together: when "
    "the leader runs out, the follower is exactly n from the end, because "
    "the gap between them never changed. This is how you remove the nth "
    "from the end in one pass, and the idea — hold a constant distance "
    "while both move — turns up well beyond linked lists.",
    "algo_list_gap",
    [
        (
            f"Build {_arrows(items)} as a linked list. Send one pointer {n} "
            f"nodes ahead, then move both until the leader falls off the "
            f"end. Print the value the follower is on — the {n}th from the "
            f"end.",
            {"items": items, "n": n},
        )
        for items, n in _GAPS
    ],
)


# ── 315. An order that works ─────────────────────────────────

_ORDERS = (
    (("shirt", "tie", "jacket", "shoes"),
     (("shirt", "tie"), ("tie", "jacket"), ("shoes", "jacket"))),
    (("flour", "dough", "bread", "yeast"),
     (("flour", "dough"), ("yeast", "dough"), ("dough", "bread"))),
    (("wake", "dress", "eat", "leave"),
     (("wake", "dress"), ("dress", "eat"), ("eat", "leave"))),
    (("dig", "plant", "water", "pick"),
     (("dig", "plant"), ("plant", "water"), ("water", "pick"))),
    (("sand", "prime", "paint", "seal"),
     (("sand", "prime"), ("prime", "paint"), ("paint", "seal"))),
    (("mine", "smelt", "cast", "cool"),
     (("mine", "smelt"), ("smelt", "cast"), ("cast", "cool"))),
    (("write", "edit", "print", "bind"),
     (("write", "edit"), ("edit", "print"), ("print", "bind"))),
    (("shear", "wash", "spin", "weave"),
     (("shear", "wash"), ("wash", "spin"), ("spin", "weave"))),
    (("pick", "press", "ferment", "bottle"),
     (("pick", "press"), ("press", "ferment"), ("ferment", "bottle"))),
    (("quarry", "cut", "polish", "fit"),
     (("quarry", "cut"), ("cut", "polish"), ("polish", "fit"))),
    (("fell", "saw", "dry", "plane"),
     (("fell", "saw"), ("saw", "dry"), ("dry", "plane"))),
    (("melt", "blow", "anneal", "grind"),
     (("melt", "blow"), ("blow", "anneal"), ("anneal", "grind"))),
    (("weigh", "mix", "prove", "bake"),
     (("weigh", "mix"), ("mix", "prove"), ("prove", "bake"))),
    (("draft", "review", "sign", "file"),
     (("draft", "review"), ("review", "sign"), ("sign", "file"))),
    (("charge", "test", "pack", "ship"),
     (("charge", "test"), ("test", "pack"), ("pack", "ship"))),
    (("thaw", "season", "roast", "rest"),
     (("thaw", "season"), ("season", "roast"), ("roast", "rest"))),
    (("survey", "clear", "build", "roof"),
     (("survey", "clear"), ("clear", "build"), ("build", "roof"))),
    (("tune", "record", "mix", "master"),
     (("tune", "record"), ("record", "mix"), ("mix", "master"))),
    (("soak", "rinse", "dry", "fold"),
     (("soak", "rinse"), ("rinse", "dry"), ("dry", "fold"))),
    (("hatch", "feed", "grow", "sell"),
     (("hatch", "feed"), ("feed", "grow"), ("grow", "sell"))),
)

_P315 = _page(
    "algo-topo-order",
    315,
    "Doing things in an order that works",
    "Kahn's: count what each thing waits for, take whatever waits for none.",
    "Every one of these is a list of jobs where some must come before "
    "others, and the question is an order that never breaks a rule. Count "
    "how many things each job is waiting on, start with the ones waiting "
    "on nothing, and every time you finish a job decrement whatever it was "
    "blocking. Anything that drops to zero is now ready. The queue is kept "
    "sorted here so there is one answer rather than any valid one — real "
    "code does not need that, but a page with an expected output does.",
    "algo_topo_order",
    [
        (
            "Order these so nothing comes before what it depends on: "
            + ", ".join(sorted(names))
            + ". The rules are "
            + ", ".join(f"{a} before {b}" for a, b in edges)
            + ". Count what each waits for, start with those waiting for "
            "nothing, and break ties alphabetically. Print the order and "
            "its length.",
            {"names": names, "edges": edges},
        )
        for names, edges in _ORDERS
    ],
)


# ── 316. The leftovers that prove a cycle ────────────────────

_TOPO_CYCLES = (
    (("a", "b", "c", "d"), (("a", "b"), ("b", "c"), ("c", "b"))),
    (("w", "x", "y", "z"), (("w", "x"), ("x", "y"), ("y", "x"))),
    (("p", "q", "r", "s"), (("p", "q"), ("q", "r"), ("r", "q"))),
    (("one", "two", "three", "four"),
     (("one", "two"), ("two", "three"), ("three", "two"))),
    (("red", "green", "blue", "grey"),
     (("red", "green"), ("green", "blue"), ("blue", "green"))),
    (("mon", "tue", "wed", "thu"),
     (("mon", "tue"), ("tue", "wed"), ("wed", "tue"))),
    (("tin", "lead", "zinc", "iron"),
     (("tin", "lead"), ("lead", "zinc"), ("zinc", "lead"))),
    (("oak", "ash", "elm", "yew"),
     (("oak", "ash"), ("ash", "elm"), ("elm", "ash"))),
    (("la", "ti", "do", "re"), (("la", "ti"), ("ti", "do"), ("do", "ti"))),
    (("in", "out", "up", "down"),
     (("in", "out"), ("out", "up"), ("up", "out"))),
    (("cat", "dog", "hen", "cow"),
     (("cat", "dog"), ("dog", "hen"), ("hen", "dog"))),
    (("east", "west", "north", "south"),
     (("east", "west"), ("west", "north"), ("north", "west"))),
    (("dig", "sow", "reap", "sell"),
     (("dig", "sow"), ("sow", "reap"), ("reap", "sow"))),
    (("melt", "cast", "cool", "trim"),
     (("melt", "cast"), ("cast", "cool"), ("cool", "cast"))),
    (("draft", "edit", "sign", "post"),
     (("draft", "edit"), ("edit", "sign"), ("sign", "edit"))),
    (("wake", "wash", "dress", "go"),
     (("wake", "wash"), ("wash", "dress"), ("dress", "wash"))),
    (("mix", "bake", "ice", "eat"),
     (("mix", "bake"), ("bake", "ice"), ("ice", "bake"))),
    (("plan", "build", "test", "ship"),
     (("plan", "build"), ("build", "test"), ("test", "build"))),
    (("sand", "paint", "seal", "hang"),
     (("sand", "paint"), ("paint", "seal"), ("seal", "paint"))),
    (("soak", "rinse", "dry", "fold"),
     (("soak", "rinse"), ("rinse", "dry"), ("dry", "rinse"))),
)

_P316 = _page(
    "algo-topo-cycle",
    316,
    "The leftovers that prove a cycle",
    "The same algorithm, and what it means when the queue empties early.",
    "This is page 315's code unchanged, which is the point. If some jobs "
    "depend on each other in a circle then none of them ever reaches zero "
    "waiting, so the queue runs dry with work still outstanding. Count "
    "what came out: fewer than you started with means a cycle, and the "
    "difference is exactly how many things are tangled. No separate "
    "cycle-detection pass, no extra colour marking — the count is the "
    "answer.",
    "algo_topo_cycle",
    [
        (
            "Try to order "
            + ", ".join(sorted(names))
            + " given "
            + ", ".join(f"{a} before {b}" for a, b in edges)
            + ". Count how many come out. Print that count, how many were "
            "left stuck, and whether an order was possible at all.",
            {"names": names, "edges": edges},
        )
        for names, edges in _TOPO_CYCLES
    ],
)


# ── 317. A stack that only goes one way ──────────────────────

_MONOTONIC = (
    (2, 1, 2, 4, 3),
    (5, 4, 6, 3, 2),
    (1, 4, 3, 2),
    (7, 8, 1, 4),
    (3, 3, 5, 2),
    (9, 2, 7, 1),
    (4, 6, 2, 8, 5),
    (10, 1, 12, 3),
    (2, 5, 1, 6, 4),
    (8, 3, 9, 2),
    (1, 2, 3, 1),
    (6, 4, 7, 2, 5),
    (11, 5, 13, 4),
    (3, 7, 2, 9, 6),
    (5, 2, 8, 1),
    (4, 9, 3, 10, 7),
    (12, 6, 14, 5),
    (2, 8, 4, 11, 3),
    (7, 3, 10, 2),
    (6, 13, 5, 15, 9),
)

_P317 = _page(
    "algo-monotonic",
    317,
    "A stack that only ever goes one way",
    "Hold the ones still waiting for an answer, and pop them when it comes.",
    "For each number, what is the next bigger one to its right? Nested "
    "loops answer that in n squared. Instead push each position onto a "
    "stack and, whenever a bigger number arrives, pop everything it "
    "answers — each position is pushed once and popped once, so the whole "
    "thing is one pass. Whatever is still on the stack at the end never "
    "found a bigger number, which is why those entries stay -1 and why "
    "the leftover count is worth printing.",
    "algo_monotonic",
    [
        (
            f"For each number in {_seq(items)}, find the next bigger number "
            f"to its right, or -1 if there is none. Keep a stack of "
            f"positions still waiting for an answer. Print the answers "
            f"joined by commas and how many were left waiting.",
            {"items": items},
        )
        for items in _MONOTONIC
    ],
)


# ── 318. Overlapping ranges folded together ──────────────────

_SPANS = (
    ((1, 3), (2, 6), (8, 10), (15, 18)),
    ((1, 4), (4, 5), (7, 9)),
    ((5, 10), (8, 12), (20, 25)),
    ((2, 3), (3, 7), (10, 14)),
    ((1, 5), (3, 8), (12, 16)),
    ((6, 9), (8, 11), (14, 20)),
    ((0, 2), (1, 4), (7, 8)),
    ((10, 15), (12, 18), (30, 33)),
    ((3, 6), (5, 9), (11, 13)),
    ((1, 2), (2, 4), (9, 12)),
    ((4, 8), (6, 11), (20, 24)),
    ((7, 10), (9, 14), (18, 21)),
    ((2, 5), (4, 9), (13, 17)),
    ((11, 14), (13, 19), (25, 28)),
    ((1, 6), (5, 8), (15, 19)),
    ((8, 13), (11, 16), (22, 26)),
    ((3, 9), (7, 12), (16, 20)),
    ((5, 7), (6, 10), (21, 27)),
    ((12, 17), (15, 21), (29, 32)),
    ((2, 8), (6, 13), (17, 23)),
)

_P318 = _page(
    "algo-merge-spans",
    318,
    "Overlapping ranges folded together",
    "Sort by where they start, then compare each with the last one kept.",
    "Unsorted, deciding which ranges overlap is a mess of cases. Sorted by "
    "start, it collapses to one question: does this one begin before the "
    "last one ended? If so, stretch the last one to whichever end is "
    "further — `max` matters, because the new range can be entirely "
    "inside the old one. If not, start a new one. The sort is most of the "
    "work and the rest is four lines.",
    "algo_merge_spans",
    [
        (
            f"Fold the overlapping ranges {_spans(spans)} together. Sort by "
            f"start, then extend the last kept range whenever the next one "
            f"begins before it ended. Print the merged ranges and how many "
            f"are left.",
            {"spans": spans},
        )
        for spans in _SPANS
    ],
)


ALGO_PAGES_3: tuple[Page, ...] = (
    _P309,
    _P310,
    _P311,
    _P312,
    _P313,
    _P314,
    _P315,
    _P316,
    _P317,
    _P318,
)
