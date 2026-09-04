"""The moves the interview patterns are made of.

Everything up to page 288 teaches Python: the syntax, then the library. This
tier teaches the handful of *moves* that the LeetCode patterns are assembled
from, which is a different skill and the one that was missing.

The distinction matters. There is already a page on heapq and a page on
bisect, and they teach the tool - heappush, insort, the argument order.
Knowing the tool is not knowing when to reach for it. These pages drill the
shape of the reasoning instead: count as you scan, hold two pointers and
move the one that helps, grow a window until it breaks and then shrink it,
keep the best answer so far.

Each is small enough to be one page and real enough that a LeetCode easy is
an application of it rather than a new idea. They are Python only, which is
the point - one language, done until the fingers know it.

Every program prints a definite answer, and the emitters compute the same
answer independently, so a page that drifts from its own reference fails
rather than teaching the drift.
"""

from __future__ import annotations

from code_coach.workbook.emit import NL, Shape, _lines, _q

LANGUAGES: tuple[str, ...] = ("python",)

SHAPES: tuple[Shape, ...] = (
    Shape("algo_tally", "counting as you go, in one pass"),
    Shape("algo_seen", "the first thing you have met before"),
    Shape("algo_complement", "looking for the number that completes a pair"),
    Shape("algo_pair_inward", "two pointers walking towards each other"),
    Shape("algo_two_pointer_same", "a slow pointer and a fast one"),
    Shape("algo_window_fixed", "a window of fixed width, slid along"),
    Shape("algo_window_grow", "a window that grows until it breaks"),
    Shape("algo_running_best", "the best answer so far, kept as you go"),
    Shape("algo_prefix_sum", "totals worked out once and reused"),
    Shape("algo_stack_match", "a stack for the thing most recently opened"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


def _nums(items) -> str:
    return "[" + ", ".join(str(n) for n in items) + "]"


def _words(items) -> str:
    return "[" + ", ".join(_q(w) for w in items) + "]"


# ── 289. Counting as you go ──────────────────────────────────


def _tally(a: dict) -> str:
    return _lines(
        f"items = {_words(a['items'])}",
        "counts = {}",
        "for item in items:",
        "    counts[item] = counts.get(item, 0) + 1",
        "",
        f"print(counts[{_q(a['asked'])}])",
        "print(len(counts))",
        "print(max(counts, key=counts.get))",
    )


# ── 290. The first thing you have met before ─────────────────


def _seen(a: dict) -> str:
    return _lines(
        f"items = {_nums(a['items'])}",
        "seen = set()",
        "first_repeat = None",
        "for item in items:",
        "    if item in seen:",
        "        first_repeat = item",
        "        break",
        "    seen.add(item)",
        "",
        "print(first_repeat)",
        "print(len(seen))",
    )


# ── 291. The number that completes a pair ────────────────────


def _complement(a: dict) -> str:
    return _lines(
        f"numbers = {_nums(a['items'])}",
        f"target = {a['target']}",
        "seen = {}",
        "answer = None",
        "for index, number in enumerate(numbers):",
        "    wanted = target - number",
        "    if wanted in seen:",
        "        answer = (seen[wanted], index)",
        "        break",
        "    seen[number] = index",
        "",
        "print(answer)",
    )


# ── 292. Two pointers walking inward ─────────────────────────


def _pair_inward(a: dict) -> str:
    return _lines(
        f"numbers = {_nums(a['items'])}",
        f"target = {a['target']}",
        "low = 0",
        "high = len(numbers) - 1",
        "answer = None",
        "steps = 0",
        "while low < high:",
        "    steps += 1",
        "    total = numbers[low] + numbers[high]",
        "    if total == target:",
        "        answer = (numbers[low], numbers[high])",
        "        break",
        "    if total < target:",
        "        low += 1",
        "    else:",
        "        high -= 1",
        "",
        "print(answer)",
        "print(steps)",
    )


# ── 293. A slow pointer and a fast one ───────────────────────


def _two_pointer_same(a: dict) -> str:
    return _lines(
        f"numbers = {_nums(a['items'])}",
        "slow = 0",
        "for fast in range(len(numbers)):",
        f"    if numbers[fast] {a['keep']}:",
        "        numbers[slow] = numbers[fast]",
        "        slow += 1",
        "",
        "print(slow)",
        'print(", ".join(str(n) for n in numbers[:slow]))',
    )


# ── 294. A window of fixed width ─────────────────────────────


def _window_fixed(a: dict) -> str:
    return _lines(
        f"numbers = {_nums(a['items'])}",
        f"width = {a['width']}",
        "total = sum(numbers[:width])",
        "best = total",
        "for i in range(width, len(numbers)):",
        "    total += numbers[i] - numbers[i - width]",
        "    if total > best:",
        "        best = total",
        "",
        "print(best)",
        "print(sum(numbers[:width]))",
    )


# ── 295. A window that grows until it breaks ─────────────────


def _window_grow(a: dict) -> str:
    return _lines(
        f"numbers = {_nums(a['items'])}",
        f"limit = {a['limit']}",
        "left = 0",
        "total = 0",
        "best = 0",
        "for right in range(len(numbers)):",
        "    total += numbers[right]",
        "    while total > limit:",
        "        total -= numbers[left]",
        "        left += 1",
        "    if right - left + 1 > best:",
        "        best = right - left + 1",
        "",
        "print(best)",
    )


# ── 296. The best answer so far ──────────────────────────────


def _running_best(a: dict) -> str:
    return _lines(
        f"numbers = {_nums(a['items'])}",
        "best = numbers[0]",
        "here = numbers[0]",
        "for number in numbers[1:]:",
        "    here = max(number, here + number)",
        "    if here > best:",
        "        best = here",
        "",
        "print(best)",
        "print(max(numbers))",
    )


# ── 297. Totals worked out once ──────────────────────────────


def _prefix_sum(a: dict) -> str:
    return _lines(
        f"numbers = {_nums(a['items'])}",
        "running = [0]",
        "for number in numbers:",
        "    running.append(running[-1] + number)",
        "",
        *[
            f"print(running[{hi}] - running[{lo}])"
            for lo, hi in a["ranges"]
        ],
        "print(running[-1])",
    )


# ── 298. A stack for the most recent thing ───────────────────


def _stack_match(a: dict) -> str:
    return _lines(
        f"text = {_q(a['text'])}",
        'pairs = {")": "(", "]": "[", "}": "{"}',
        "stack = []",
        "balanced = True",
        "for ch in text:",
        "    if ch in pairs.values():",
        "        stack.append(ch)",
        "    elif ch in pairs:",
        "        if not stack or stack.pop() != pairs[ch]:",
        "            balanced = False",
        "            break",
        "",
        "print(balanced and not stack)",
        "print(len(stack))",
    )


_BUILDERS = {
    "algo_tally": _tally,
    "algo_seen": _seen,
    "algo_complement": _complement,
    "algo_pair_inward": _pair_inward,
    "algo_two_pointer_same": _two_pointer_same,
    "algo_window_fixed": _window_fixed,
    "algo_window_grow": _window_grow,
    "algo_running_best": _running_best,
    "algo_prefix_sum": _prefix_sum,
    "algo_stack_match": _stack_match,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    if build is None:
        return None
    return build(args)


def expected_output(shape: str, args: dict, value) -> str:
    """Work the answer out independently of the program that prints it.

    These are algorithms rather than one-liners, so the guards here are
    doing more than usual: a window wider than its list, a target no pair
    reaches, a bracket string that happens to be balanced on a page about
    spotting when it is not. Each would run perfectly and teach nothing.
    """
    a = args
    lines: list[str] = []
    if shape == "algo_tally":
        counts: dict[str, int] = {}
        for item in a["items"]:
            counts[item] = counts.get(item, 0) + 1
        if a["asked"] not in counts:
            raise ValueError("the item asked about must be in the list")
        top = max(counts, key=lambda k: counts[k])
        if sorted(counts.values())[-2:] == [counts[top], counts[top]]:
            raise ValueError("the most common item must be a clear winner")
        lines = [str(counts[a["asked"]]), str(len(counts)), top]
    elif shape == "algo_seen":
        seen: set[int] = set()
        first_repeat = None
        for item in a["items"]:
            if item in seen:
                first_repeat = item
                break
            seen.add(item)
        if first_repeat is None:
            raise ValueError("something must actually repeat")
        lines = [str(first_repeat), str(len(seen))]
    elif shape == "algo_complement":
        seen_at: dict[int, int] = {}
        answer = None
        for index, number in enumerate(a["items"]):
            wanted = a["target"] - number
            if wanted in seen_at:
                answer = (seen_at[wanted], index)
                break
            seen_at[number] = index
        if answer is None:
            raise ValueError("some pair must reach the target")
        lines = [str(answer)]
    elif shape == "algo_pair_inward":
        items = list(a["items"])
        if items != sorted(items):
            raise ValueError("walking inward needs a sorted list")
        low, high, answer, steps = 0, len(items) - 1, None, 0
        while low < high:
            steps += 1
            total = items[low] + items[high]
            if total == a["target"]:
                answer = (items[low], items[high])
                break
            if total < a["target"]:
                low += 1
            else:
                high -= 1
        if answer is None:
            raise ValueError("some pair must reach the target")
        lines = [str(answer), str(steps)]
    elif shape == "algo_two_pointer_same":
        kept = [n for n in a["items"] if value(f"n {a['keep']}", {"n": n})]
        if len(kept) == len(a["items"]):
            raise ValueError("the filter must drop something")
        if not kept:
            raise ValueError("the filter must keep something")
        lines = [str(len(kept)), ", ".join(str(n) for n in kept)]
    elif shape == "algo_window_fixed":
        items, width = a["items"], a["width"]
        if width >= len(items):
            raise ValueError("the window must be narrower than the list")
        sums = [
            sum(items[i : i + width]) for i in range(len(items) - width + 1)
        ]
        if max(sums) == sums[0]:
            raise ValueError("the best window must not be the first one")
        lines = [str(max(sums)), str(sums[0])]
    elif shape == "algo_window_grow":
        items, limit = a["items"], a["limit"]
        if any(n > limit for n in items):
            raise ValueError("every single item must fit inside the limit")
        if sum(items) <= limit:
            raise ValueError("the whole list must not fit, or nothing shrinks")
        left = total = best = 0
        for right, number in enumerate(items):
            total += number
            while total > limit:
                total -= items[left]
                left += 1
            best = max(best, right - left + 1)
        lines = [str(best)]
    elif shape == "algo_running_best":
        items = a["items"]
        best = here = items[0]
        for number in items[1:]:
            here = max(number, here + number)
            best = max(best, here)
        if best == max(items):
            raise ValueError("the best run must beat the biggest single item")
        lines = [str(best), str(max(items))]
    elif shape == "algo_prefix_sum":
        items = a["items"]
        running = [0]
        for number in items:
            running.append(running[-1] + number)
        for lo, hi in a["ranges"]:
            if not 0 <= lo < hi <= len(items):
                raise ValueError("each range must lie inside the list")
        lines = [str(running[hi] - running[lo]) for lo, hi in a["ranges"]]
        lines.append(str(running[-1]))
    elif shape == "algo_stack_match":
        opens = {")": "(", "]": "[", "}": "{"}
        stack: list[str] = []
        balanced = True
        for ch in a["text"]:
            if ch in opens.values():
                stack.append(ch)
            elif ch in opens:
                if not stack or stack.pop() != opens[ch]:
                    balanced = False
                    break
        lines = [str(balanced and not stack), str(len(stack))]
    else:
        raise KeyError(shape)
    return NL.join(lines)
