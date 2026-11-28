"""Big-O Intuition: a passive deck. Outputs were worked out by hand; the oracle test runs the code."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 112

DECK = Deck(
    id="py-bigo",
    title="Big-O Intuition",
    language="python",
    blurb="How the work grows as the input grows: counting steps for O(1), O(log n), O(n), O(n log n) and O(n^2), plus space, cases and reading a solution's cost.",
    slides=(
        Slide(
            title="O(n): work grows with the input",
            text="Big-O describes how the number of steps grows as the input n grows. If a loop runs once per item, ten times more items means ten times more steps. That is O(n).",
            code=r"""def steps(n):
    count = 0
    for _ in range(n):
        count += 1
    return count
print(steps(10), steps(100), steps(1000))""",
            output="10 100 1000",
            point="O(n): double the input, double the work.",
        ),
        Slide(
            title="O(1) dict vs O(n) list search",
            text="Finding an item in a list means checking one after another, up to n checks. A set or dict jumps straight to the item in about one step, however big it is.",
            code=r"""items = list(range(1000))
checks = 0
for x in items:
    checks += 1
    if x == 999:
        break
print(checks)
lookup = set(items)
print(999 in lookup)""",
            output="1000\nTrue",
            point="x in list is O(n); x in set or dict is O(1) on average.",
        ),
        Slide(
            title="O(n^2): a loop inside a loop",
            text="When every item is paired with every other item, the work is n times n. Doubling the input quadruples the steps, so it gets slow fast.",
            code=r"""def pairs(n):
    count = 0
    for i in range(n):
        for j in range(n):
            count += 1
    return count
print(pairs(10), pairs(20), pairs(40))""",
            output="100 400 1600",
            point="O(n^2): double the input, four times the work.",
        ),
        Slide(
            title="O(log n): halving",
            text="If each step throws away half of what is left, even huge inputs finish in few steps. Eight items take 3 halvings and 1024 take 10. A million takes only 19.",
            code=r"""def halvings(n):
    steps = 0
    while n > 1:
        n //= 2
        steps += 1
    return steps
print(halvings(8), halvings(1024), halvings(1_000_000))""",
            output="3 10 19",
            point="O(log n): the input can grow enormously and the steps barely move.",
        ),
        Slide(
            title="O(n log n): sorting",
            text="Good sorting algorithms, including Python's sorted, take about n times log n steps. That sits between O(n) and O(n^2), and is much closer to O(n) for big inputs.",
            code=r"""import math
for n in (8, 1024):
    print(n, n * int(math.log2(n)), n * n)""",
            output="8 24 64\n1024 10240 1048576",
            point="Sorting first is usually cheap compared with an O(n^2) search.",
        ),
        Slide(
            title="Space complexity",
            text="Big-O also measures memory. Building a list of n squares needs room for n numbers, which is O(n) space. Keeping just a running best needs one number, which is O(1).",
            code=r"""squares = [i * i for i in range(5)]
print(len(squares))
best = 0
for i in range(5):
    best = max(best, i * i)
print(best)""",
            output="5\n16",
            point="Ask both questions: how many steps, and how much memory?",
        ),
        Slide(
            title="Amortised append",
            text="Lists grow by doubling their space when full. A toy model: after 16 appends, only 15 items were ever copied, less than one copy per append. So append averages O(1) even though a few are costly.",
            code=r"""capacity, copies = 1, 0
for length in range(1, 17):
    if length > capacity:
        copies += capacity
        capacity *= 2
print(capacity, copies)""",
            output="16 15",
            point="Amortised O(1): rare expensive steps are spread over many cheap ones.",
        ),
        Slide(
            title="A set turns O(n^2) into O(n)",
            text="To spot a duplicate by comparing every pair of 5 numbers takes 10 comparisons, and the count explodes as n grows. One pass that remembers items in a set looks at each number once.",
            code=r"""nums = [4, 2, 7, 2, 9]
slow = fast = 0
for i in range(5):
    for j in range(i + 1, 5):
        slow += 1
seen = set()
for n in nums:
    fast += 1
    seen.add(n)
print(slow, fast, len(seen) < len(nums))""",
            output="10 5 True",
            point="Trade a little memory for a lot of speed: use a set.",
        ),
        Slide(
            title="String += in a loop vs join",
            text="Strings cannot be changed, so s += x may build a whole new string each time, and a long loop can end up copying O(n^2) characters in total. Collecting pieces in a list and joining once copies each piece once.",
            code=r"""parts = []
for i in range(5):
    parts.append(str(i))
print("".join(parts))
s = ""
for i in range(5):
    s += str(i)
print(s)""",
            output="01234\n01234",
            point="Build pieces in a list, then join once.",
        ),
        Slide(
            title="Recursion depth is space",
            text="Every pending recursive call takes room on the call stack. A recursion that goes n levels deep uses O(n) space, even if it creates no lists of its own.",
            code=r"""deepest = 0
def down(n, level=1):
    global deepest
    deepest = max(deepest, level)
    if n > 0:
        down(n - 1, level + 1)
down(5)
print(deepest)""",
            output="6",
            point="Depth of recursion = extra space used.",
        ),
        Slide(
            title="Best, worst and average case",
            text="The same algorithm can be fast or slow depending on the input. Searching for the first item takes 1 step, a middle item takes about half of n, and a missing item takes all n. Big-O usually quotes the worst case.",
            code=r"""def find(xs, t):
    steps = 0
    for x in xs:
        steps += 1
        if x == t:
            break
    return steps
xs = list(range(1, 11))
print(find(xs, 1), find(xs, 5), find(xs, 10), find(xs, 99))""",
            output="1 5 10 10",
            point="Worst case is what you can promise.",
        ),
        Slide(
            title="Choose a structure by its operations",
            text="Ask what you do most. Removing from the front fits a deque, repeatedly taking the smallest fits a heap, and asking 'is it in there?' fits a set.",
            code=r"""from collections import deque
import heapq
q = deque([5, 3, 8])
print(q.popleft())
h = [5, 3, 8]
heapq.heapify(h)
print(heapq.heappop(h))
print(8 in {5, 3, 8})""",
            output="5\n3\nTrue",
            point="The right data structure often is the whole optimisation.",
        ),
        Slide(
            title="Reading complexity from loops",
            text="One loop over n is O(n). A loop inside a loop is O(n^2). A loop that halves n is O(log n). Loops one after another add up, and the biggest term wins.",
            code=r"""n, a, b, c = 8, 0, 0, 0
for i in range(n):
    a += 1
for i in range(n):
    for j in range(n):
        b += 1
while n > 1:
    n //= 2
    c += 1
print(a, b, c)""",
            output="8 64 3",
            point="Sequential: add. Nested: multiply. Halving: log.",
        ),
        Slide(
            title="Constants and small terms are dropped",
            text="Two passes over the data is 2n steps, which is still O(n). A cost of n squared plus n is O(n^2), because for large n the square dominates. Big-O is about the shape of growth.",
            code=r"""n = 10
count = 0
for _ in range(n):
    count += 1
for _ in range(n):
    count += 1
print(count, n * n + n)""",
            output="20 110",
            point="Drop constant factors and smaller terms.",
        ),
        Slide(
            title="How fast growth escalates",
            text="Compare the step counts for just n = 20. Logarithms are tiny, n squared is a few hundred, and 2 to the n already passes a million. Exponential solutions only work for very small inputs.",
            code=r"""import math
n = 20
print(int(math.log2(n)), n, n * n, 2 ** n)""",
            output="4 20 400 1048576",
            point="O(log n) < O(n) < O(n log n) < O(n^2) < O(2^n).",
        ),
    ),
)
