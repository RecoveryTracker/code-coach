"""Algorithm Patterns: a passive deck. Outputs were worked out by hand; the oracle test runs the code."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 120

DECK = Deck(
    id="py-algorithms",
    title="Algorithm Patterns",
    language="python",
    blurb="The patterns behind many interview problems: prefix sums, hash maps, stacks, BFS and DFS, topological order, union-find, dynamic programming, greedy, backtracking and intervals.",
    slides=(
        Slide(
            title="Prefix sums",
            text="Build a list where prefix[i] is the sum of the first i numbers. Then the sum of any slice is one subtraction instead of a loop.",
            code=r"""nums = [2, 4, 1, 3]
prefix = [0]
for n in nums:
    prefix.append(prefix[-1] + n)
print(prefix)
print(prefix[4] - prefix[1])""",
            output="[0, 2, 6, 7, 10]\n8",
            point="sum(nums[i:j]) = prefix[j] - prefix[i], after one pass.",
        ),
        Slide(
            title="Hash map complement: two sum",
            text="For each number, ask whether its partner (target minus the number) has been seen already. A dict from value to index answers that in one step, so a single pass is enough.",
            code=r"""def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return seen[target - n], i
        seen[n] = i
print(two_sum([2, 7, 11, 15], 9))""",
            output="(0, 1)",
            point="Look up what you need instead of searching for it.",
        ),
        Slide(
            title="Frequency maps for anagrams",
            text="Two words are anagrams when every letter appears the same number of times in both. Counting the letters of each and comparing the counts avoids sorting.",
            code=r"""from collections import Counter
def is_anagram(a, b):
    return Counter(a) == Counter(b)
print(is_anagram("listen", "silent"), is_anagram("abc", "abd"))""",
            output="True False",
            point="Same counts means same letters: a frequency map is a fingerprint.",
        ),
        Slide(
            title="Monotonic stack: next greater",
            text="To find the next bigger number to the right of each item, keep a stack of items still waiting. A new number settles every smaller waiting item on top of the stack.",
            code=r"""nums = [2, 1, 5, 3]
result = [-1] * len(nums)
stack = []
for i, n in enumerate(nums):
    while stack and nums[stack[-1]] < n:
        result[stack.pop()] = n
    stack.append(i)
print(result)""",
            output="[5, 5, -1, -1]",
            point="Each index is pushed and popped once, so it is O(n).",
        ),
        Slide(
            title="BFS: level by level",
            text="Breadth-first search uses a queue and visits the closest nodes first. A seen set stops it from visiting a node twice. A is linked to B and C, and B links back to A.",
            code=r"""from collections import deque
graph = {"A": ["B", "C"], "B": ["A", "D"], "C": [], "D": []}
seen, queue = {"A"}, deque(["A"])
while queue:
    node = queue.popleft()
    print(node)
    for nxt in graph[node]:
        if nxt not in seen:
            seen.add(nxt)
            queue.append(nxt)""",
            output="A\nB\nC\nD",
            point="BFS = queue. It finds the fewest-steps path.",
        ),
        Slide(
            title="DFS with recursion and visited",
            text="Depth-first search goes as deep as it can before backing up. The seen set matters: B links back to A, and without the check we would loop forever.",
            code=r"""graph = {"A": ["B", "C"], "B": ["A", "D"], "C": [], "D": []}
seen = set()
def dfs(node):
    if node in seen:
        return
    seen.add(node)
    print(node)
    for nxt in graph[node]:
        dfs(nxt)
dfs("A")""",
            output="A\nB\nD\nC",
            point="DFS = recursion. Always mark a node visited in a graph.",
        ),
        Slide(
            title="DFS with an explicit stack",
            text="Swap the call stack for your own list. Pop a node, skip it if it is already seen, print it, and push its neighbours. Reversing them keeps the same visiting order as the recursive version.",
            code=r"""graph = {"A": ["B", "C"], "B": ["A", "D"], "C": [], "D": []}
stack, seen = ["A"], set()
while stack:
    node = stack.pop()
    if node in seen:
        continue
    seen.add(node)
    print(node)
    stack.extend(reversed(graph[node]))""",
            output="A\nB\nD\nC",
            point="Queue gives BFS, stack gives DFS: the rest is the same.",
        ),
        Slide(
            title="Topological sort (Kahn's)",
            text="To order tasks so each comes after its prerequisites, repeatedly take a task that nothing is waiting on. Taking it frees later tasks, so lower their waiting count and add any that reach 0.",
            code=r"""graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
indeg = {"a": 0, "b": 1, "c": 1, "d": 2}
ready = ["a"]
while ready:
    node = ready.pop(0)
    print(node)
    for nxt in graph[node]:
        indeg[nxt] -= 1
        if indeg[nxt] == 0:
            ready.append(nxt)""",
            output="a\nb\nc\nd",
            point="indeg = how many prerequisites are still unfinished.",
        ),
        Slide(
            title="Union-find",
            text="Union-find tracks which items belong to the same group. find follows parents up to the group's root, and union links one root under another. Two items share a group when their roots match.",
            code=r"""parent = list(range(5))
def find(x):
    while parent[x] != x:
        x = parent[x]
    return x
def union(a, b):
    parent[find(a)] = find(b)
union(0, 1)
union(1, 2)
print(find(0) == find(2), find(0) == find(4))""",
            output="True False",
            point="Great for 'are these connected?' and counting groups.",
        ),
        Slide(
            title="DP: bottom-up and top-down",
            text="Dynamic programming reuses answers to smaller problems. Climbing 5 stairs, one or two at a time, has ways(n) = ways(n-1) + ways(n-2). Fill a table upward, or recurse with a cache. Both give 8.",
            code=r"""from functools import lru_cache
@lru_cache(None)
def top(n):
    return 1 if n < 2 else top(n - 1) + top(n - 2)
ways = [1, 1]
for i in range(2, 6):
    ways.append(ways[-1] + ways[-2])
print(top(5), ways[5])""",
            output="8 8",
            point="Define the answer for size n in terms of smaller sizes.",
        ),
        Slide(
            title="DP: coin change, counting ways",
            text="dp[a] is the number of ways to make amount a. Handle one coin at a time: every amount can also use that coin on top of the ways to make what is left. Here: ways to make 5 from 1, 2 and 5.",
            code=r"""dp = [1, 0, 0, 0, 0, 0]
for c in (1, 2, 5):
    for amt in range(c, 6):
        dp[amt] += dp[amt - c]
print(dp)
print(dp[5])""",
            output="[1, 1, 2, 2, 3, 4]\n4",
            point="Coin on the outside, amount on the inside: order does not matter.",
        ),
        Slide(
            title="Greedy: interval scheduling",
            text="To fit the most non-overlapping meetings, always pick the one that ends earliest, then the next one that starts after it. Sorting by end time makes that choice easy.",
            code=r"""meetings = [(1, 3), (2, 5), (4, 6), (5, 9), (6, 8)]
count, end = 0, 0
for s, e in sorted(meetings, key=lambda m: m[1]):
    if s >= end:
        count += 1
        end = e
print(count)""",
            output="3",
            point="Greedy: take the locally best choice and never look back.",
        ),
        Slide(
            title="Binary search on the answer",
            text="Sometimes you search for a number instead of an item. Guess a speed and test whether it finishes in time. If it does, try smaller; if not, larger. Here: slowest pile-eating speed that finishes four piles in 8 hours.",
            code=r"""piles = [3, 6, 7, 11]
hours = lambda s: sum(-(-p // s) for p in piles)
lo, hi = 1, 11
while lo < hi:
    mid = (lo + hi) // 2
    if hours(mid) <= 8:
        hi = mid
    else:
        lo = mid + 1
print(lo)""",
            output="4",
            point="If a yes/no test flips once as the answer grows, binary search it.",
        ),
        Slide(
            title="Backtracking with pruning",
            text="Try choices one at a time and undo them when they fail. Pruning means stopping early: the numbers are sorted, so once one is bigger than the target left, all later ones are too and we break.",
            code=r"""def combos(nums, target, start=0, path=()):
    if target == 0:
        print(path)
        return
    for i in range(start, len(nums)):
        if nums[i] > target:
            break
        combos(nums, target - nums[i], i + 1, path + (nums[i],))
combos([1, 2, 3, 4, 5], 6)""",
            output="(1, 2, 3)\n(1, 5)\n(2, 4)",
            point="Prune a branch as soon as it cannot possibly work.",
        ),
        Slide(
            title="Merging overlapping intervals",
            text="Sort the intervals by start. Then walk through them: if the next one starts before the last merged one ends, stretch that one; otherwise begin a new one.",
            code=r"""def merge(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out
print(merge([(8, 10), (1, 3), (2, 6), (15, 18), (17, 20)]))""",
            output="[[1, 6], [8, 10], [15, 20]]",
            point="Interval problems almost always start with: sort by start.",
        ),
    ),
)
