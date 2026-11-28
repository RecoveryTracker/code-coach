"""Interview Classics: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 127

DECK = Deck(
    id="py-classics",
    title="Interview Classics",
    language="python",
    blurb="Fifteen famous problems, one core idea each: stacks, hash maps, windows, two pointers and tricks.",
    slides=(
        Slide(
            title="Valid parentheses (stack)",
            text="Push every opening bracket. When a closing bracket arrives, the top of the stack must be its partner. At the end the stack must be empty.",
            code=r"""def valid(s):
    pairs, st = {")": "(", "]": "[", "}": "{"}, []
    for ch in s:
        if ch in pairs:
            if not st or st.pop() != pairs[ch]: return False
        else: st.append(ch)
    return not st
print(valid("([]{})"), valid("(]"), valid("(("))""",
            output="True False False",
            point="Brackets close in reverse order of opening: that is exactly what a stack gives you.",
        ),
        Slide(
            title="Two sum (hash map)",
            text="For each number, ask whether the partner that completes the target has already been seen. A dict from value to index answers in O(1), so one pass is enough.",
            code=r"""def two_sum(nums, t):
    seen = {}
    for i, x in enumerate(nums):
        if t - x in seen: return [seen[t - x], i]
        seen[x] = i
print(two_sum([2, 7, 11, 15], 9))
print(two_sum([3, 2, 4], 6))""",
            output="[0, 1]\n[1, 2]",
            point="Trade memory for time: remember what you have seen instead of searching again.",
        ),
        Slide(
            title="Best time to buy and sell stock",
            text="Walk through the prices keeping the lowest price so far. At each day the best profit is today's price minus that low. Track the biggest of those.",
            code=r"""def profit(p):
    low, best = p[0], 0
    for x in p: low = min(low, x); best = max(best, x - low)
    return best
print(profit([7, 1, 5, 3, 6, 4]), profit([7, 6, 4, 3, 1]))""",
            output="5 0",
            point="One pass with a running minimum: buy at the lowest so far, sell today.",
        ),
        Slide(
            title="Maximum subarray (Kadane)",
            text="At each number choose: start a new run here, or extend the run so far. Keep the best run seen. A run that has gone negative only holds you back, so it is dropped.",
            code=r"""def kadane(a):
    cur = best = a[0]
    for x in a[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
print(kadane([-2, 1, -3, 4, -1, 2, 1, -5, 4]))""",
            output="6",
            point="cur = max(x, cur + x): the best sum of a run ending right here. The winner is 4, -1, 2, 1.",
        ),
        Slide(
            title="Product of array except self",
            text="No division allowed. Each answer is the product of everything to its left times everything to its right. Sweep left to right storing prefix products, then right to left multiplying in suffixes.",
            code=r"""def prod(a):
    out, p = [1] * len(a), 1
    for i in range(len(a)): out[i] = p; p *= a[i]
    p = 1
    for i in reversed(range(len(a))): out[i] *= p; p *= a[i]
    return out
print(prod([1, 2, 3, 4]))""",
            output="[24, 12, 8, 6]",
            point="Left product times right product, two passes, no division and no extra arrays.",
        ),
        Slide(
            title="Longest substring without repeats",
            text="Slide a window along the string. If the new letter already sits inside the window, move the start just past its last position. Record the longest window you see.",
            code=r"""def longest(s):
    last, start, best = {}, 0, 0
    for i, ch in enumerate(s):
        if last.get(ch, -1) >= start: start = last[ch] + 1
        last[ch] = i
        best = max(best, i - start + 1)
    return best
print(longest("abcabcbb"), longest("pwwkew"), longest(""))""",
            output="3 3 0",
            point="Remember each letter's last index, and the window start jumps straight past a repeat.",
        ),
        Slide(
            title="Group anagrams (sorted key)",
            text="Words that are anagrams become identical when their letters are sorted. Use the sorted letters as a dict key and collect words under it.",
            code=r"""groups = {}
for w in ["eat", "tea", "tan", "ate", "nat", "bat"]:
    groups.setdefault("".join(sorted(w)), []).append(w)
print(list(groups.values()))""",
            output="[['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]",
            point="Find a canonical form (a key that equal things share), then group by it.",
        ),
        Slide(
            title="Top k frequent (Counter)",
            text="Counter counts everything in one call, and most_common(k) returns the k biggest as (item, count) pairs. Take just the items if that is all you need.",
            code=r"""from collections import Counter
nums = [1, 1, 1, 2, 2, 3]
print([x for x, _ in Counter(nums).most_common(2)])
print(Counter("mississippi").most_common(2))""",
            output="[1, 2]\n[('i', 4), ('s', 4)]",
            point="Counter(...).most_common(k) is the whole solution; ties keep first-seen order.",
        ),
        Slide(
            title="Merge intervals",
            text="Sort by start. Then each interval either overlaps the last merged one (its start is not after that end), so stretch the end, or it begins a new block. Touching intervals merge.",
            code=r"""def merge(iv):
    out = []
    for s, e in sorted(iv):
        if out and s <= out[-1][1]: out[-1][1] = max(out[-1][1], e)
        else: out.append([s, e])
    return out
print(merge([[1, 4], [4, 5], [7, 9]]))
print(merge([[1, 10], [2, 3]]))""",
            output="[[1, 5], [7, 9]]\n[[1, 10]]",
            point="Sorting makes overlaps neighbours; use max for the end, since one interval can swallow another.",
        ),
        Slide(
            title="Move zeroes (two pointers)",
            text="Keep a write position w for the next non-zero. Scan with a read pointer; each non-zero is swapped into place at w, and w moves on. The zeros drift to the end, in place.",
            code=r"""nums = [0, 1, 0, 3, 12]
w = 0
for r in range(len(nums)):
    if nums[r] != 0: nums[w], nums[r] = nums[r], nums[w]; w += 1
print(nums)""",
            output="[1, 3, 12, 0, 0]",
            point="One pointer reads, one writes: O(n) time, O(1) space, order kept.",
        ),
        Slide(
            title="Climbing stairs",
            text="You climb 1 or 2 steps at a time. The ways to reach step n are the ways to reach n-1 plus the ways to reach n-2: Fibonacci again. Two variables are enough.",
            code=r"""def climb(n):
    a, b = 1, 1
    for _ in range(n - 1): a, b = b, a + b
    return b
print([climb(n) for n in range(1, 8)])""",
            output="[1, 2, 3, 5, 8, 13, 21]",
            point="'Count the ways with small steps' usually hides a Fibonacci-style recurrence.",
        ),
        Slide(
            title="Rotate array by reversing",
            text="To rotate right by k in place, reverse the whole list, then reverse the first k items and the rest separately. Three reversals, no extra list.",
            code=r"""a = [1, 2, 3, 4, 5, 6, 7]; k = 3
a.reverse(); print(a)
a[:k] = a[:k][::-1]; print(a)
a[k:] = a[k:][::-1]; print(a)""",
            output="[7, 6, 5, 4, 3, 2, 1]\n[5, 6, 7, 4, 3, 2, 1]\n[5, 6, 7, 1, 2, 3, 4]",
            point="Reverse all, reverse the front k, reverse the back: that is a rotation. Use k %= len(a) first.",
        ),
        Slide(
            title="Contains duplicate (set)",
            text="A set holds each value once, so if converting to a set makes the list shorter, something repeated. To stop early, add values one by one and quit at the first one already present.",
            code=r"""def dup(a): return len(set(a)) < len(a)
print(dup([1, 2, 3, 1]), dup([1, 2, 3]))
seen = set()
for x in [4, 7, 4, 9]:
    if x in seen: print("dup", x); break
    seen.add(x)""",
            output="True False\ndup 4",
            point="Membership in a set is O(1), so 'have I seen this?' is cheap.",
        ),
        Slide(
            title="Majority element (Boyer-Moore)",
            text="Hold a candidate and a count. A matching number adds one, a different one subtracts one, and at zero take a new candidate. A value in over half the items always survives.",
            code=r"""def majority(a):
    cand, cnt = None, 0
    for x in a:
        if cnt == 0: cand = x
        cnt += 1 if x == cand else -1
    return cand
print(majority([2, 2, 1, 1, 1, 2, 2]), majority([3, 2, 3]))""",
            output="2 3",
            point="Pairs of different numbers cancel out; the true majority cannot be cancelled away. O(1) space.",
        ),
        Slide(
            title="Missing number (sum or xor)",
            text="The list holds 0 to n with one number missing. The expected total is n(n+1)/2, so the gap is that minus the actual sum. XOR works too, since equal values cancel.",
            code=r"""nums = [3, 0, 1]
n = len(nums)
print(n * (n + 1) // 2 - sum(nums))
x = n
for i, v in enumerate(nums): x ^= i ^ v
print(x)""",
            output="2\n2",
            point="Know what the total should be, and the difference is the answer. XOR avoids big sums.",
        ),
    ),
)
