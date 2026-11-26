"""Python for algorithms: the shapes interview problems are built from.

The lines are the moves a solution is made of, one at a time: two pointers
closing in, a window sliding along, a binary search's midpoint, a stack and
a queue, a heap, a visited set, a memo, a DP table, prefix sums, bit tricks
and the sort keys that do half the work. Typing them until they are
automatic is the point - in an interview the shape should already be in
your hands so your head is free for the problem.

The blocks are whole small solutions that print their answer, and the tests
run every one in the real interpreter and hold what it prints to an answer
worked out by hand. No clock, no unseeded dice, no files.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

PYALGO_LINES: tuple[Passage, ...] = (
    # two pointers
    _s("lo_ptr, hi_ptr = 0, len(heights) - 1", "two pointers over the heights"),
    _s("while lo_ptr < hi_ptr and nums[lo_ptr] <= nums[hi_ptr]:", "close in while sorted"),
    _s("total = nums[left] + nums[right]", "the pair the pointers are on"),
    _s("if total < target: left += 1", "too small: move the low end up"),
    _s("nums[left], nums[right] = nums[right], nums[left]", "swap the two ends"),
    _s("slow, fast = head, head.next", "the tortoise and the hare"),
    _s("while fast and fast.next: slow, fast = slow.next, fast.next.next", "both move at once"),
    # sliding window
    _s("window_sum = sum(nums[:k])", "the first window, added up once"),
    _s("window_sum += nums[i] - nums[i - k]", "slide: add the new end, drop the old"),
    _s("best_len = max(best_len, end - start + 1)", "the widest window seen so far"),
    _s("while counts[ch] > 1:", "shrink until the window is valid again"),
    _s("in_window[text[start]] -= 1", "the letter leaving the window"),
    # binary search
    _s("lo, hi = 0, len(nums) - 1", "the search range, both ends included"),
    _s("mid = (lo + hi) // 2", "the middle, rounded down"),
    _s("if nums[mid] == target: return mid", "found it"),
    _s("lo = mid + 1 if nums[mid] < target else lo", "the answer is to the right"),
    _s("hi = mid - 1 if nums[mid] > target else hi", "the answer is to the left"),
    _s("i = bisect.bisect_left(sorted_nums, x)", "where x would go, from the library"),
    # stacks and queues
    _s("stack.append((index, temp))", "push the position along with the value"),
    _s("if not opened or opened.pop() != closer_for[ch]:", "the bracket that should close"),
    _s("while stack and temps[stack[-1]] < t:", "a monotonic stack, popping smaller"),
    _s("queue = deque([start])", "a queue for breadth-first search"),
    _s("node, steps = queue.popleft()", "the oldest in the queue, with its distance"),
    _s("for neighbour in adjacency[node]:", "every neighbour of this node"),
    _s("if nxt not in seen:", "only the ones not visited yet"),
    _s("visited.add(neighbour)", "marked when queued, so it is queued once"),
    # heaps
    _s("heapq.heappush(heap, (dist, node))", "smallest distance on top"),
    _s("dist, node = heapq.heappop(heap)", "the closest one not yet settled"),
    _s("largest = heapq.nlargest(3, nums)", "the top three without sorting it all"),
    _s("heapq.heappushpop(heap, x)", "push then pop, keeping the size fixed"),
    _s("heap = [-n for n in nums]", "negated, to make a max-heap from a min-heap"),
    # recursion and memo
    _s("memo: dict[tuple[int, int], int] = {}", "a hand-made cache, keyed by the arguments"),
    _s("def fib(n: int) -> int:", "the function the cache is wrapping"),
    _s("return fib(n - 1) + fib(n - 2)", "two smaller problems"),
    _s("def dfs(node, depth):", "depth-first, carrying the depth down"),
    _s("if node is None: return 0", "the base case of every tree recursion"),
    _s("return 1 + max(dfs(node.left), dfs(node.right))", "a tree's height"),
    # dynamic programming
    _s("dp = [0] * (n + 1)", "one slot per subproblem, plus the empty one"),
    _s("dp[i] = max(dp[i - 1], dp[i - 2] + nums[i - 1])", "take it or skip it"),
    _s("dp = [[0] * (m + 1) for _ in range(n + 1)]", "a grid with fresh rows"),
    _s("dp[i][j] = dp[i - 1][j - 1] + 1", "the strings agree here: extend"),
    _s("dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])", "or keep the better neighbour"),
    _s("for coin in sorted(denominations):", "each coin, smallest first"),
    _s("ways[amount] += ways[amount - coin]", "the ways of making change"),
    # prefix sums and counting
    _s("prefix = list(itertools.accumulate(nums, initial=0))", "running totals"),
    _s("range_sum = prefix[j + 1] - prefix[i]", "any slice's sum in one subtraction"),
    _s("seen_sums = {0: 1}", "the empty prefix, seen once"),
    _s("count += seen_sums.get(running - k, 0)", "subarrays summing to k"),
    _s("first_seen.setdefault(x, i)", "keeps only the first index of each value"),
    _s("if target - x in index: return [index[target - x], i]", "two sum"),
    # sorting
    _s("intervals.sort(key=lambda iv: iv[0])", "by start, before merging"),
    _s("if start <= merged[-1][1]:", "overlaps the last one kept"),
    _s("merged[-1][1] = max(merged[-1][1], end)", "stretch it to cover both"),
    _s("people.sort(key=lambda p: (-p.score, p.name))", "high score first, then A-Z"),
    _s("anagrams[''.join(sorted(word))].append(word)", "same letters, same key"),
    # bits
    _s("if n & 1: odd += 1", "the lowest bit says odd or even"),
    _s("bits &= bits - 1", "clears the lowest set bit"),
    _s("single = functools.reduce(operator.xor, nums)", "pairs cancel out"),
    _s("is_power = n > 0 and n & (n - 1) == 0", "exactly one bit set"),
    # grids
    _s("for dr, dc in DIRECTIONS:", "the four neighbours, named once"),
    _s("if 0 <= r < rows and 0 <= c < cols:", "still inside the grid"),
    _s("grid[r][c] = '#'", "marked as visited in place"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"Python · {note}")


PYALGO_BLOCKS: tuple[Passage, ...] = (
    _b(r"""def two_sum(nums, target):
    index = {}
    for i, x in enumerate(nums):
        if target - x in index:
            return [index[target - x], i]
        index[x] = i
    return []

print(two_sum([2, 7, 11, 15], 9), two_sum([3, 3], 6))""",
       "two sum with a dict"),
    _b(r"""def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

print(search([1, 3, 5, 7, 9], 7), search([1, 3, 5], 4))""",
       "binary search"),
    _b(r"""def longest_unique(s):
    seen = {}
    left = best = 0
    for right, ch in enumerate(s):
        if seen.get(ch, -1) >= left:
            left = seen[ch] + 1
        seen[ch] = right
        best = max(best, right - left + 1)
    return best

print(longest_unique("abcabcbb"), longest_unique("bbbb"))""",
       "the longest run without a repeat"),
    _b(r"""def valid(text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif not stack or stack.pop() != pairs[ch]:
            return False
    return not stack

print(valid("{[()]}"), valid("([)]"), valid("(("))""",
       "matching brackets with a stack"),
    _b(r"""from collections import deque

graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
dist = {"a": 0}
queue = deque(["a"])
while queue:
    node = queue.popleft()
    for nxt in graph[node]:
        if nxt not in dist:
            dist[nxt] = dist[node] + 1
            queue.append(nxt)
print(dist)""",
       "breadth-first search for distances"),
    _b(r"""import heapq

nums = [5, 1, 9, 3, 7, 2]
heap = []
for n in nums:
    heapq.heappush(heap, n)
    if len(heap) > 3:
        heapq.heappop(heap)
print(sorted(heap), heap[0])""",
       "the three largest with a heap"),
    _b(r"""from functools import cache

@cache
def climb(n):
    if n <= 1:
        return 1
    return climb(n - 1) + climb(n - 2)

print([climb(n) for n in range(1, 8)])""",
       "climbing stairs with a cache"),
    _b(r"""def rob(houses):
    take, skip = 0, 0
    for money in houses:
        take, skip = skip + money, max(take, skip)
    return max(take, skip)

print(rob([2, 7, 9, 3, 1]), rob([5]), rob([]))""",
       "house robber in two variables"),
    _b(r"""def merge(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged

print(merge([[1, 3], [8, 10], [2, 6], [9, 12]]))""",
       "merging overlapping intervals"),
    _b(r"""def coin_ways(coins, amount):
    ways = [1] + [0] * amount
    for coin in coins:
        for total in range(coin, amount + 1):
            ways[total] += ways[total - coin]
    return ways[amount]

print(coin_ways([1, 2, 5], 5), coin_ways([2], 3))""",
       "counting the ways to make change"),
    _b(r"""def islands(grid):
    rows, cols = len(grid), len(grid[0])
    def sink(r, c):
        if 0 <= r < rows and 0 <= c < cols and grid[r][c] == "1":
            grid[r][c] = "0"
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                sink(r + dr, c + dc)
            return 1
        return 0
    return sum(sink(r, c) for r in range(rows) for c in range(cols))

print(islands([list("1100"), list("0100"), list("0011")]))""",
       "counting islands with a flood fill"),
    _b(r"""from collections import defaultdict

words = ["eat", "tea", "tan", "ate", "nat", "bat"]
groups = defaultdict(list)
for word in words:
    groups["".join(sorted(word))].append(word)
print(sorted(groups.values(), key=len, reverse=True))""",
       "grouping anagrams by sorted letters"),
)

#: What each block prints, by its note - worked out by hand before Python
#: was asked, and held to the real run by tests/test_typing_python_themes2.py.
PYALGO_PRINTS: dict[str, str] = {
    "two sum with a dict": "[0, 1] [0, 1]",
    "binary search": "3 -1",
    "the longest run without a repeat": "3 1",
    "matching brackets with a stack": "True False False",
    "breadth-first search for distances": "{'a': 0, 'b': 1, 'c': 1, 'd': 2}",
    "the three largest with a heap": "[5, 7, 9] 5",
    "climbing stairs with a cache": "[1, 2, 3, 5, 8, 13, 21]",
    "house robber in two variables": "12 5 0",
    "merging overlapping intervals": "[[1, 6], [8, 12]]",
    "counting the ways to make change": "4 0",
    "counting islands with a flood fill": "2",
    "grouping anagrams by sorted letters": "[['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]",
}
