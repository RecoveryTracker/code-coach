"""Pages 289-298: the moves the interview patterns are made of.

The 288 pages before this teach Python — the syntax, then the library. They
do not teach you to solve a LeetCode problem, and it is worth being exact
about why: there is already a page on heapq and a page on bisect, and they
teach heappush and insort. Knowing the tool is not knowing when to reach for
it.

These ten drill the reasoning instead. Count as you scan. Hold two pointers
and move whichever one helps. Grow a window until it breaks, then shrink it
from the left. Keep the best answer so far. Each one is the whole idea
behind a pattern in the LeetCode tier, at a size that fits on a page, and
the intent is that by the twentieth repetition the move is in your fingers
and the interview problem is an application rather than an invention.

Python only. One language, done properly.
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


def _quoted(items) -> str:
    return ", ".join(f'"{w}"' for w in items)


# ── 289. Counting as you go ──────────────────────────────────

_TALLIES = (
    (("a", "b", "a", "c", "a"), "a"),
    (("red", "blue", "red", "green"), "blue"),
    (("x", "x", "y", "x", "z"), "y"),
    (("cat", "dog", "cat", "cat", "hen"), "dog"),
    (("one", "two", "one", "three", "one"), "three"),
    (("up", "down", "up", "up", "left"), "up"),
    (("tin", "lead", "tin", "tin", "zinc"), "lead"),
    (("thu", "fri", "thu", "thu", "sat"), "sat"),
    (("oak", "ash", "oak", "oak", "elm"), "oak"),
    (("la", "ti", "la", "la", "do"), "ti"),
    (("in", "out", "in", "in", "up"), "in"),
    (("kiwi", "plum", "kiwi", "kiwi", "sloe"), "plum"),
    (("teal", "plum", "teal", "teal", "amber"), "amber"),
    (("finn", "kit", "finn", "finn", "ida"), "kit"),
    (("near", "far", "near", "near", "mid"), "near"),
    (("hot", "cold", "hot", "hot", "warm"), "cold"),
    (("north", "south", "north", "north", "east"), "east"),
    (("soft", "loud", "soft", "soft", "mid"), "soft"),
    (("cabin", "hold", "cabin", "cabin", "deck"), "hold"),
    (("art", "sons", "art", "art", "low"), "sons"),
)

_P289 = _page(
    "algo-tally",
    289,
    "Counting as you go",
    "One pass, a dict, and get with a default.",
    "This is the whole hash-map pattern in four lines, and half the "
    "interview problems that look hard are this with a question attached. "
    "The move is `counts[item] = counts.get(item, 0) + 1` — no checking "
    "whether the key is there first, no second pass. Once the counts exist, "
    "most-common is a max with a key, and how-many-distinct is a len.",
    "algo_tally",
    [
        (
            f"Count how many times each of {_quoted(items)} appears, in one "
            f'pass with a dict. Print the count for "{asked}", how many '
            f"different items there were, and the most common one.",
            {"items": items, "asked": asked},
        )
        for items, asked in _TALLIES
    ],
)


# ── 290. The first thing you have met before ─────────────────

_SEEN = (
    (3, 1, 4, 1, 5),
    (7, 2, 9, 2, 8),
    (5, 5, 1, 2),
    (10, 20, 30, 10),
    (1, 2, 3, 4, 2),
    (8, 6, 7, 6, 9),
    (11, 13, 11, 17),
    (4, 9, 16, 4, 25),
    (2, 4, 8, 16, 8),
    (100, 50, 25, 50),
    (6, 12, 18, 6, 24),
    (9, 8, 7, 9, 6),
    (13, 26, 39, 26),
    (5, 10, 15, 20, 5),
    (14, 7, 21, 7),
    (3, 6, 9, 12, 3),
    (17, 34, 17, 51),
    (2, 3, 5, 7, 3),
    (40, 30, 20, 30),
    (1, 4, 9, 16, 9),
)

_P290 = _page(
    "algo-seen",
    290,
    "The first thing you have met before",
    "A set built as you scan, and the early exit when a member is found.",
    "A set answers `have I met this` in constant time, which is the only "
    "reason this is one pass rather than two nested loops. Note where the "
    "add happens: after the check, never before, or every item is its own "
    "duplicate. The break matters too — the question was the *first* "
    "repeat, and carrying on would find the last.",
    "algo_seen",
    [
        (
            f"Scan {_seq(items)} keeping a set of what you have seen, and "
            f"stop at the first item already in it. Print that item and how "
            f"many you had added before you stopped.",
            {"items": items},
        )
        for items in _SEEN
    ],
)


# ── 291. The number that completes a pair ────────────────────

_COMPLEMENTS = (
    ((2, 7, 11, 15), 9),
    ((3, 2, 4), 6),
    ((3, 3), 6),
    ((1, 5, 9, 13), 14),
    ((10, 20, 30, 40), 50),
    ((4, 8, 15, 16), 23),
    ((5, 25, 75), 100),
    ((1, 2, 3, 4, 5), 9),
    ((12, 7, 3, 9), 16),
    ((6, 6, 11), 12),
    ((2, 4, 6, 8), 14),
    ((14, 2, 5, 9), 11),
    ((21, 13, 8, 5), 21),
    ((30, 11, 19, 7), 30),
    ((9, 1, 8, 2), 10),
    ((45, 5, 25, 20), 45),
    ((17, 3, 14, 6), 20),
    ((100, 40, 60, 25), 100),
    ((11, 22, 33, 44), 55),
    ((7, 13, 6, 8), 15),
)

_P291 = _page(
    "algo-complement",
    291,
    "The number that completes a pair",
    "Ask for what you need, not for what you have.",
    "This is two-sum, and it is the page that changes how people think. The "
    "naive answer checks every pair against every other. The move is to "
    "turn the question round: for this number, what would complete it? Then "
    "ask the dict whether you have already walked past it. One pass, and "
    "the dict holds where each number was so the answer is a pair of "
    "positions.",
    "algo_complement",
    [
        (
            f"In {_seq(items)}, find the two positions whose numbers add to "
            f"{target}. Keep a dict of number to position as you go, and for "
            f"each number look up the one that would complete it. Print the "
            f"pair of positions.",
            {"items": items, "target": target},
        )
        for items, target in _COMPLEMENTS
    ],
)


# ── 292. Two pointers walking inward ─────────────────────────

_INWARD = (
    ((1, 2, 4, 7, 11, 15), 15),
    ((2, 3, 4), 6),
    ((1, 3, 5, 7, 9), 10),
    ((10, 20, 30, 40), 50),
    ((2, 4, 6, 8, 10), 14),
    ((1, 2, 3, 4, 5, 6), 7),
    ((5, 15, 25, 35), 40),
    ((3, 6, 9, 12, 15), 18),
    ((1, 4, 9, 16, 25), 26),
    ((7, 14, 21, 28), 35),
    ((2, 5, 11, 17, 23), 28),
    ((4, 8, 12, 16, 20), 24),
    ((1, 5, 9, 13, 17), 22),
    ((6, 12, 18, 24, 30), 36),
    ((3, 9, 15, 21), 24),
    ((2, 7, 13, 19, 25), 32),
    ((5, 10, 20, 40, 80), 60),
    ((1, 2, 5, 10, 20), 22),
    ((8, 16, 24, 32), 40),
    ((11, 13, 17, 19, 23), 30),
)

_P292 = _page(
    "algo-pair-inward",
    292,
    "Two pointers walking towards each other",
    "A sorted list, one pointer at each end, and moving the one that helps.",
    "The list being sorted is what makes this work, and it is the whole "
    "trick. If the two ends add to less than the target, the only way to "
    "get more is to move the left one up. If they add to more, move the "
    "right one down. Every step throws away a possibility for good, so a "
    "list of a thousand takes a thousand steps rather than a million — and "
    "the step count is printed so you can watch that happen.",
    "algo_pair_inward",
    [
        (
            f"The list {_seq(items)} is sorted. Put one pointer at each end "
            f"and move whichever one brings the total closer to {target}. "
            f"Print the pair you find and how many steps it took.",
            {"items": items, "target": target},
        )
        for items, target in _INWARD
    ],
)


# ── 293. A slow pointer and a fast one ───────────────────────

_SAME_WAY = (
    ((3, 0, 5, 0, 7, 0), "!= 0"),
    ((1, 2, 3, 4, 5, 6), "% 2 == 0"),
    ((4, 4, 9, 4, 2), "!= 4"),
    ((10, 3, 20, 7, 30), "> 9"),
    ((1, 2, 3, 4, 5), "> 2"),
    ((0, 1, 0, 2, 0, 3), "!= 0"),
    ((5, 10, 15, 20, 25), "% 10 == 0"),
    ((2, 3, 5, 7, 8, 9), "% 2 == 1"),
    ((6, 1, 6, 2, 6), "!= 6"),
    ((11, 22, 33, 44), "> 25"),
    ((1, 4, 9, 16, 25), "> 8"),
    ((7, 7, 3, 7, 1), "!= 7"),
    ((2, 4, 6, 7, 8), "% 2 == 0"),
    ((100, 5, 200, 6), "> 50"),
    ((3, 6, 9, 10, 12), "% 3 == 0"),
    ((8, 0, 8, 0, 9), "!= 0"),
    ((13, 26, 39, 40), "% 13 == 0"),
    ((1, 2, 3, 40, 50), "> 10"),
    ((5, 5, 2, 5, 8), "!= 5"),
    ((12, 15, 18, 20, 21), "% 3 == 0"),
)

_P293 = _page(
    "algo-two-pointer-same",
    293,
    "A slow pointer and a fast one",
    "Both moving the same way, the slow one only when something is kept.",
    "The fast pointer reads every item; the slow one marks where the next "
    "keeper goes. That gap between them is the number of things thrown "
    "away so far. This is how you remove items from a list without "
    "building a second one, and it is the same shape as removing "
    "duplicates, moving zeroes to the end, and half a dozen other "
    "problems that look unrelated until you have written it once.",
    "algo_two_pointer_same",
    [
        (
            f"Walk {_seq(items)} with a fast pointer, and a slow one that "
            f"only advances when an item is {keep}. Overwrite in place, then "
            f"print how many were kept and those items joined by commas.",
            {"items": items, "keep": keep},
        )
        for items, keep in _SAME_WAY
    ],
)


# ── 294. A window of fixed width ─────────────────────────────

_FIXED = (
    ((1, 4, 2, 10, 2, 3, 1, 0, 20), 4),
    ((2, 1, 5, 1, 3, 2), 3),
    ((1, 1, 1, 9, 1), 2),
    ((5, 2, 8, 1, 9, 3), 2),
    ((3, 3, 3, 12, 3), 3),
    ((7, 1, 2, 9, 8, 1), 3),
    ((4, 4, 4, 4, 20), 2),
    ((1, 2, 3, 4, 5, 6), 3),
    ((10, 1, 1, 1, 30, 1), 2),
    ((6, 2, 4, 8, 10, 1), 3),
    ((2, 2, 2, 2, 9, 9), 2),
    ((1, 5, 1, 5, 1, 15), 2),
    ((8, 3, 1, 12, 4), 2),
    ((5, 5, 5, 5, 5, 25), 3),
    ((9, 2, 3, 4, 18, 2), 2),
    ((1, 3, 5, 7, 9, 11), 4),
    ((2, 8, 1, 1, 14, 2), 3),
    ((11, 1, 1, 1, 1, 40), 2),
    ((3, 7, 2, 9, 6, 8), 3),
    ((4, 1, 6, 2, 20, 5), 2),
)

_P294 = _page(
    "algo-window-fixed",
    294,
    "A window of fixed width, slid along",
    "Add the one entering, subtract the one leaving. Never re-add the rest.",
    "The obvious version re-adds the whole window at every position, which "
    "for a width of four and a list of a thousand is four thousand "
    "additions. Sliding it is two: one in, one out. The first window is "
    "summed the slow way to get started, and printing it alongside the best "
    "shows that the answer moved — a page where the first window happens to "
    "win would teach nothing, so the emitter rejects those.",
    "algo_window_fixed",
    [
        (
            f"Slide a window {width} wide along {_seq(items)}, adding the "
            f"number entering and subtracting the one leaving. Print the "
            f"biggest window total and the first window's total.",
            {"items": items, "width": width},
        )
        for items, width in _FIXED
    ],
)


# ── 295. A window that grows until it breaks ─────────────────

_GROW = (
    ((2, 1, 5, 1, 3, 2), 8),
    ((1, 2, 3, 4, 5), 9),
    ((4, 2, 1, 7, 8), 10),
    ((3, 1, 4, 1, 5, 9), 12),
    ((5, 5, 5, 5), 12),
    ((1, 1, 1, 1, 1, 1), 4),
    ((6, 2, 4, 1, 8), 11),
    ((2, 3, 5, 7, 11), 14),
    ((9, 1, 2, 3, 4), 9),
    ((1, 4, 2, 8, 3), 10),
    ((7, 3, 2, 5, 1), 11),
    ((2, 2, 4, 4, 6), 9),
    ((8, 1, 1, 1, 9), 10),
    ((3, 3, 3, 3, 3), 10),
    ((5, 1, 4, 2, 6), 12),
    ((1, 6, 2, 3, 7), 11),
    ((4, 4, 1, 1, 8), 9),
    ((2, 5, 1, 6, 2), 10),
    ((6, 1, 3, 2, 5), 11),
    ((1, 2, 8, 2, 1), 12),
)

_P295 = _page(
    "algo-window-grow",
    295,
    "A window that grows until it breaks",
    "Widen on the right always; shrink from the left only while it is over.",
    "The fixed window knew its width in advance. This one does not — it "
    "grows on the right every step, and whenever it breaks the rule the "
    "left edge walks in until it is legal again. The while is the part "
    "people get wrong: shrinking once is not enough, because one step in "
    "might still be over. Both pointers only ever move forward, so the "
    "whole thing is still one pass.",
    "algo_window_grow",
    [
        (
            f"Find the longest run in {_seq(items)} whose total stays at or "
            f"under {limit}. Widen on the right, and while the total is over "
            f"the limit take from the left. Print the length of the best run.",
            {"items": items, "limit": limit},
        )
        for items, limit in _GROW
    ],
)


# ── 296. The best answer so far ──────────────────────────────

_BEST = (
    ((-2, 1, -3, 4, -1, 2, 1, -5, 4), None),
    ((1, 2, -1, 3), None),
    ((-1, 4, -2, 5), None),
    ((3, -1, 2), None),
    ((2, -1, 2, 3), None),
    ((-3, 5, -1, 4), None),
    ((1, 1, -2, 3, 3), None),
    ((4, -1, 5, -3), None),
    ((-2, 3, 2, -1), None),
    ((6, -2, 3, -1), None),
    ((1, -1, 2, 2), None),
    ((-4, 6, -1, 3), None),
    ((2, 2, -3, 4, 1), None),
    ((5, -2, 4, -1), None),
    ((-1, 2, 3, -2, 2), None),
    ((3, -2, 5, -1, 2), None),
    ((1, 3, -2, 4), None),
    ((-5, 4, 1, -2, 3), None),
    ((2, -1, 3, -2, 4), None),
    ((7, -3, 2, 4, -1), None),
)

_P296 = _page(
    "algo-running-best",
    296,
    "The best answer so far",
    "Two numbers carried along: the best ending here, and the best anywhere.",
    "Kadane's algorithm, and the insight is one line: `here = max(number, "
    "here + number)`. Either this number joins the run you were building, "
    "or the run was doing you more harm than good and you start again from "
    "here. Everything before that decision can be forgotten, which is why "
    "one pass and two variables is enough. The biggest single item is "
    "printed alongside, and the pages are chosen so the run always beats "
    "it — otherwise the algorithm proves nothing.",
    "algo_running_best",
    [
        (
            f"Find the biggest total of any run of neighbours in "
            f"{_seq(items)}. Carry the best ending here and the best seen "
            f"anywhere. Print the best run total and the biggest single item.",
            {"items": items},
        )
        for items, _ in _BEST
    ],
)


# ── 297. Totals worked out once ──────────────────────────────

_PREFIX = (
    ((1, 2, 3, 4, 5), ((0, 3), (2, 5), (1, 4))),
    ((10, 20, 30, 40), ((0, 2), (1, 4))),
    ((5, 5, 5, 5, 5), ((0, 5), (2, 4))),
    ((2, 4, 6, 8, 10), ((1, 3), (0, 5))),
    ((7, 1, 3, 9), ((0, 2), (2, 4))),
    ((1, 1, 2, 3, 5, 8), ((0, 4), (3, 6))),
    ((100, 200, 300), ((0, 1), (1, 3))),
    ((3, 6, 9, 12, 15), ((1, 4), (0, 3))),
    ((4, 8, 12, 16), ((2, 4), (0, 2))),
    ((11, 22, 33, 44, 55), ((0, 2), (3, 5))),
    ((6, 12, 18, 24), ((1, 3), (0, 4))),
    ((9, 18, 27, 36, 45), ((2, 5), (0, 1))),
    ((2, 3, 5, 7, 11, 13), ((0, 3), (2, 6))),
    ((14, 7, 21, 28), ((1, 4), (0, 2))),
    ((5, 10, 15, 20, 25), ((0, 4), (1, 5))),
    ((8, 16, 24, 32), ((0, 3), (2, 4))),
    ((13, 26, 39, 52), ((1, 2), (0, 4))),
    ((1, 4, 9, 16, 25), ((0, 2), (2, 5))),
    ((30, 20, 10, 40), ((0, 2), (1, 4))),
    ((17, 34, 51, 68, 85), ((1, 3), (0, 5))),
)

_P297 = _page(
    "algo-prefix-sum",
    297,
    "Totals worked out once and reused",
    "A running total list, and the subtraction that answers any range.",
    "Build a list where entry i is the total of everything before i, and "
    "any range total becomes one subtraction: running[hi] - running[lo]. "
    "The leading zero is what makes that work for a range starting at the "
    "beginning, which is why the list is one longer than the data. Answer "
    "one range and this was wasted effort; answer a thousand and it is the "
    "difference between instant and unusable.",
    "algo_prefix_sum",
    [
        (
            f"Build a running-total list for {_seq(items)}, starting with a "
            f"zero. Use it to print the total of "
            + ", then ".join(f"items {lo} up to {hi}" for lo, hi in ranges)
            + ", and finally the total of the whole list.",
            {"items": items, "ranges": ranges},
        )
        for items, ranges in _PREFIX
    ],
)


# ── 298. A stack for the most recent thing ───────────────────

_BRACKETS = (
    "()",
    "()[]{}",
    "(]",
    "([)]",
    "{[]}",
    "((()))",
    "(()",
    "())",
    "[({})]",
    "[(])",
    "{{{}}}",
    "{{}",
    "([]{})",
    "([}",
    "(([]))",
    "([)",
    "{[()]}",
    "{[(])}",
    "((){})",
    "((]",
)

_P298 = _page(
    "algo-stack-match",
    298,
    "A stack for the thing most recently opened",
    "Push every opener, and make every closer match the top.",
    "A closing bracket has to match the most recent unmatched opener, and "
    "most recent is exactly what a stack gives you. Two ways to fail and "
    "both matter: a closer that does not match the top, and a stack that "
    "is not empty at the end because something was never closed. The "
    "second is the one people forget, so the leftover count is printed. "
    "This shape is also how undo works, and how a compiler reads nesting.",
    "algo_stack_match",
    [
        (
            f'Decide whether the brackets in "{text}" are balanced. Push '
            f"every opener onto a stack; for every closer, check it matches "
            f"what you pop. Print whether it balanced, and how many openers "
            f"were left over.",
            {"text": text},
        )
        for text in _BRACKETS
    ],
)


ALGO_PAGES: tuple[Page, ...] = (
    _P289,
    _P290,
    _P291,
    _P292,
    _P293,
    _P294,
    _P295,
    _P296,
    _P297,
    _P298,
)
