"""Dynamic Programming: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 124

DECK = Deck(
    id="py-dp",
    title="Dynamic Programming",
    language="python",
    blurb="Remember sub-answers instead of recomputing them: fib, robber, coins, subsequences, knapsack and grids.",
    slides=(
        Slide(
            title="Overlapping subproblems",
            text="Naive Fibonacci solves the same small questions again and again. Counting the calls shows the waste: computing fib(10) takes 177 calls for only 11 different inputs.",
            code=r"""calls = 0
def fib(n):
    global calls
    calls += 1
    return n if n < 2 else fib(n - 1) + fib(n - 2)
print(fib(10))
print(calls)""",
            output="55\n177",
            point="Same inputs, repeated work: that is the first sign that DP will help.",
        ),
        Slide(
            title="Top-down with lru_cache",
            text="Keep the plain recursion and add @lru_cache. Each input is now computed once and remembered, so fib(50) needs just 51 real calls instead of billions.",
            code=r"""from functools import lru_cache
@lru_cache(None)
def fib(n): return n if n < 2 else fib(n - 1) + fib(n - 2)
print(fib(50))
print(fib.cache_info().misses)""",
            output="12586269025\n51",
            point="Memoisation = recursion + a cache. Write the recursion first, then add the decorator.",
        ),
        Slide(
            title="Bottom-up with a table",
            text="Instead of recursing down, fill a table from the smallest case upward. Each cell is built from cells already filled, so there is no recursion at all.",
            code=r"""n = 10
dp = [0] * (n + 1)
dp[1] = 1
for i in range(2, n + 1): dp[i] = dp[i - 1] + dp[i - 2]
print(dp)""",
            output="[0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]",
            point="Bottom-up: define the table, set the base cases, fill in order.",
        ),
        Slide(
            title="House robber",
            text="You cannot rob two neighbouring houses. At each house either skip it (keep the best so far) or rob it (its value plus the best from two houses back). Only two numbers are needed.",
            code=r"""def rob(h):
    a = b = 0
    for x in h: a, b = b, max(b, a + x)
    return b
print(rob([2, 7, 9, 3, 1]), rob([1, 2, 3, 1]))""",
            output="12 4",
            point="best[i] = max(best[i-1], best[i-2] + value[i]): take it or leave it.",
        ),
        Slide(
            title="Minimum coin change",
            text="dp[a] is the fewest coins that make amount a. Try each coin as the last one: dp[a - coin] + 1. Greedy fails here, since 10 with coins 1, 5, 6 is best as 5 + 5.",
            code=r"""def coins(cs, amt):
    dp = [0] + [float("inf")] * amt
    for a in range(1, amt + 1):
        for c in cs:
            if c <= a: dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amt]
print(coins([1, 5, 6], 10), coins([2], 3))""",
            output="2 inf",
            point="inf marks 'cannot be made'; the answer inf means no solution.",
        ),
        Slide(
            title="Longest increasing subsequence",
            text="dp[i] is the longest increasing run that ends at position i. Look at every earlier smaller value j and extend its run by one. This is O(n^2).",
            code=r"""def lis(a):
    dp = [1] * len(a)
    for i in range(len(a)):
        for j in range(i):
            if a[j] < a[i]: dp[i] = max(dp[i], dp[j] + 1)
    return dp
dp = lis([10, 9, 2, 5, 3, 7, 101, 18])
print(dp, max(dp))""",
            output="[1, 1, 1, 2, 2, 3, 4, 4] 4",
            point="The answer is the max over the whole table, because the best run can end anywhere.",
        ),
        Slide(
            title="Longest common subsequence",
            text="dp[i][j] is the LCS of the first i letters of one string and the first j of the other. If the letters match, take the diagonal plus 1; otherwise the better of up or left.",
            code=r"""def lcs(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            dp[i][j] = dp[i-1][j-1] + 1 if a[i-1] == b[j-1] else max(dp[i-1][j], dp[i][j-1])
    return dp
t = lcs("abc", "ac")
for row in t: print(row)
print("length", t[-1][-1])""",
            output="[0, 0, 0]\n[0, 1, 1]\n[0, 1, 1]\n[0, 1, 2]\nlength 2",
            point="The extra row and column of zeros are the empty-string base cases; the answer is the corner.",
        ),
        Slide(
            title="Edit distance",
            text="The fewest inserts, deletes and replacements to turn one word into another. If the last letters match, ignore them; otherwise try each of the three edits and take the cheapest.",
            code=r"""from functools import lru_cache
a, b = "horse", "ros"
@lru_cache(None)
def edit(i, j):
    if i == 0 or j == 0: return i + j
    if a[i-1] == b[j-1]: return edit(i - 1, j - 1)
    return 1 + min(edit(i - 1, j), edit(i, j - 1), edit(i - 1, j - 1))
print(edit(len(a), len(b)))""",
            output="3",
            point="State = (letters used of a, letters used of b); three choices, take the minimum.",
        ),
        Slide(
            title="0/1 knapsack",
            text="Each item can be taken once. dp[c] is the best value with capacity c. Loop capacity downwards so an item is not counted twice in the same pass.",
            code=r"""def knap(items, cap):
    dp = [0] * (cap + 1)
    for w, v in items:
        for c in range(cap, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[cap]
print(knap([(1, 1), (3, 4), (4, 5), (5, 7)], 7))""",
            output="9",
            point="Going downwards keeps dp[c - w] from the previous item: the '0/1' guarantee.",
        ),
        Slide(
            title="Unique paths on a grid",
            text="A robot moves only right or down. The number of ways to reach a cell is the ways to the cell above plus the ways to the cell on the left; the first row and column are all 1.",
            code=r"""def paths(r, c):
    dp = [[1] * c for _ in range(r)]
    for i in range(1, r):
        for j in range(1, c): dp[i][j] = dp[i-1][j] + dp[i][j-1]
    return dp[-1][-1]
print(paths(3, 3))
print(paths(3, 7))""",
            output="6\n28",
            point="Counting problems add the sub-answers; optimising problems take a max or min.",
        ),
        Slide(
            title="Minimum path sum on a grid",
            text="The cheapest way from top-left to bottom-right, moving right or down. Add into each cell the smaller of the cell above and the cell to the left, using infinity at the edges.",
            code=r"""g = [[1, 3, 1], [1, 5, 1], [4, 2, 1]]
inf = float("inf")
for i in range(3):
    for j in range(3):
        if i or j:
            up = g[i-1][j] if i else inf
            left = g[i][j-1] if j else inf
            g[i][j] += min(up, left)
print(g)""",
            output="[[1, 4, 5], [2, 7, 6], [6, 8, 7]]",
            point="Each cell becomes 'cost of the best way to get here'; the corner holds the answer, 7.",
        ),
        Slide(
            title="Partition into equal subsets",
            text="Can a list be split into two groups with the same sum? That is the same as asking whether some subset adds up to half the total. Track every sum reachable so far.",
            code=r"""def can_split(nums):
    total = sum(nums)
    if total % 2: return False
    reach = {0}
    for x in nums: reach |= {s + x for s in reach}
    return total // 2 in reach
print(can_split([1, 5, 11, 5]), can_split([1, 2, 3, 5]))""",
            output="True False",
            point="An odd total is an instant no. Otherwise it is subset-sum: a set of reachable sums.",
        ),
        Slide(
            title="Word break",
            text="Can a string be cut into dictionary words? ok[i] says the first i letters can be. It is true if some earlier ok[j] is true and the piece from j to i is a word.",
            code=r"""def word_break(s, words):
    ok = [True] + [False] * len(s)
    for i in range(1, len(s) + 1):
        ok[i] = any(ok[j] and s[j:i] in words for j in range(i))
    return ok[-1]
print(word_break("leetcode", {"leet", "code"}))
print(word_break("catsandog", {"cats", "dog", "sand", "and", "cat"}))""",
            output="True\nFalse",
            point="Look backwards for a good cut point: ok[i] = any(ok[j] and s[j:i] is a word).",
        ),
        Slide(
            title="Rolling arrays save space",
            text="Each grid row depends only on the row above, so keep a single row and update it in place. The memory falls from rows times columns to just columns.",
            code=r"""def paths(r, c):
    row = [1] * c
    for _ in range(r - 1):
        for j in range(1, c): row[j] += row[j - 1]
    return row[-1]
print(paths(3, 7))""",
            output="28",
            point="If a table row needs only the previous row, keep one row (or two numbers, like the robber).",
        ),
        Slide(
            title="How to spot a DP problem",
            text="Look for: best, fewest, longest or count-the-ways; a choice at each step; and a recursion whose inputs repeat. Below, calling trace(6) visits the same small inputs many times.",
            code=r"""seen = {}
def trace(n):
    seen[n] = seen.get(n, 0) + 1
    if n > 1: trace(n - 1); trace(n - 2)
trace(6)
print(dict(sorted(seen.items())))""",
            output="{0: 5, 1: 8, 2: 5, 3: 3, 4: 2, 5: 1, 6: 1}",
            point="Name the state, write the choice, find the base case; if inputs repeat, cache them.",
        ),
    ),
)
