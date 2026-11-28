"""Heaps and Priority Queues: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 125

DECK = Deck(
    id="py-heaps",
    title="Heaps and Priority Queues",
    language="python",
    blurb="heapq in depth: min and max heaps, tuples, ties, top-k, merging, running median and scheduling.",
    slides=(
        Slide(
            title="A min-heap with heapq",
            text="A heap is a list kept so that the smallest item is always first. heappush adds an item, heappop removes and returns the smallest, and h[0] peeks without removing.",
            code=r"""import heapq
h = []
for x in (5, 1, 4, 2): heapq.heappush(h, x)
print(h[0])
print(heapq.heappop(h), heapq.heappop(h))""",
            output="1\n1 2",
            point="heapq is a set of functions on a plain list: h[0] is always the minimum.",
        ),
        Slide(
            title="A heap is only partly sorted",
            text="Only the front item is guaranteed. Every parent is no bigger than its children, but the rest of the list is not in order, so never read a heap as if it were sorted.",
            code=r"""import heapq
h = []
for x in (5, 3, 4, 1, 2): heapq.heappush(h, x)
print(h)
print(sorted(h))""",
            output="[1, 2, 4, 5, 3]\n[1, 2, 3, 4, 5]",
            point="Parent <= children is the whole rule. Use heappop, or sorted(), to get order.",
        ),
        Slide(
            title="heapify: a list into a heap",
            text="heapify rearranges an existing list in place in O(n), which beats pushing items one by one at O(n log n). Then popping repeatedly returns the items in order.",
            code=r"""import heapq
nums = [9, 4, 7, 1, 3]
heapq.heapify(nums)
print(nums[0])
print([heapq.heappop(nums) for _ in range(5)])""",
            output="1\n[1, 3, 4, 7, 9]",
            point="Have all the data up front? heapify it. Data arrives over time? heappush.",
        ),
        Slide(
            title="Heap sort in two lines",
            text="Heapify, then pop everything: the pops come out smallest first. It costs O(n log n), and it works on strings or any comparable items too.",
            code=r"""import heapq
def heapsort(it):
    h = list(it); heapq.heapify(h)
    return [heapq.heappop(h) for _ in range(len(h))]
print(heapsort([5, 2, 8, 1, 9, 3]))
print(heapsort("pear fig apple kiwi".split()))""",
            output="[1, 2, 3, 5, 8, 9]\n['apple', 'fig', 'kiwi', 'pear']",
            point="Popping a heap until empty is a sort.",
        ),
        Slide(
            title="A max-heap by negating",
            text="heapq only builds min-heaps. To get the biggest first, store the negative of each number, then flip the sign again when you read it back.",
            code=r"""import heapq
h = []
for x in (3, 10, 7): heapq.heappush(h, -x)
print(-h[0])
print(-heapq.heappop(h), -heapq.heappop(h))""",
            output="10\n10 7",
            point="Max-heap trick: push -x, read -h[0].",
        ),
        Slide(
            title="Tuples as (priority, item)",
            text="Push tuples and the heap orders by the first element, then the next one to break ties. The item rides along with its priority.",
            code=r"""import heapq
tasks = []
heapq.heappush(tasks, (2, "write"))
heapq.heappush(tasks, (1, "plan"))
heapq.heappush(tasks, (3, "ship"))
while tasks: print(heapq.heappop(tasks))""",
            output="(1, 'plan')\n(2, 'write')\n(3, 'ship')",
            point="(priority, item) is the standard shape of a priority queue entry.",
        ),
        Slide(
            title="Ties and a counter",
            text="If priorities tie, Python compares the items, which can fail or reorder things. Add a running counter as the second field so equal priorities come out first in, first out.",
            code=r"""import heapq, itertools
count = itertools.count()
h = []
for pri, name in [(1, "b"), (1, "a"), (0, "z")]:
    heapq.heappush(h, (pri, next(count), name))
print([heapq.heappop(h)[2] for _ in range(3)])""",
            output="['z', 'b', 'a']",
            point="(priority, counter, item): the counter never ties, so items are never compared.",
        ),
        Slide(
            title="heapreplace and heappushpop",
            text="heapreplace pops the smallest first and then pushes the new item. heappushpop pushes first and then pops, so a new item smaller than everything is returned straight away. Each is one efficient step.",
            code=r"""import heapq
h = [2, 5, 9]
print(heapq.heapreplace(h, 7))
print(heapq.heappushpop(h, 1))
print(sorted(h))""",
            output="2\n1\n[5, 7, 9]",
            point="Keeping the k largest: a size-k min-heap with heappushpop drops the smallest each time.",
        ),
        Slide(
            title="nlargest and nsmallest with key",
            text="heapq.nlargest(k, items) gives the k biggest without sorting everything. A key function says what to compare, such as length, and ties keep their original order.",
            code=r"""import heapq
words = ["fig", "banana", "kiwi", "apple", "plum"]
print(heapq.nlargest(2, words, key=len))
print(heapq.nsmallest(2, words, key=len))
print(heapq.nlargest(2, [4, 1, 9, 7]))""",
            output="['banana', 'apple']\n['fig', 'kiwi']\n[9, 7]",
            point="For small k these beat sorted(); for k near n, just sort.",
        ),
        Slide(
            title="K smallest pairs",
            text="Given two sorted lists, find the k pairs with the smallest sums. Start from the pair of first items; each time you pop a pair, push its two neighbours (next in a, next in b) once.",
            code=r"""import heapq
def k_pairs(a, b, k):
    h = [(a[0] + b[0], 0, 0)]; seen = {(0, 0)}; out = []
    while h and len(out) < k:
        s, i, j = heapq.heappop(h); out.append((a[i], b[j]))
        for x, y in ((i + 1, j), (i, j + 1)):
            if x < len(a) and y < len(b) and (x, y) not in seen:
                seen.add((x, y)); heapq.heappush(h, (a[x] + b[y], x, y))
    return out
print(k_pairs([1, 7, 11], [2, 4, 6], 3))""",
            output="[(1, 2), (1, 4), (1, 6)]",
            point="Grow the frontier lazily: the heap only ever holds candidates for the next smallest.",
        ),
        Slide(
            title="Merging k sorted lists",
            text="heapq.merge takes any number of already-sorted inputs and yields one sorted stream, lazily, using a heap of the front items. Pass reverse=True when the inputs are sorted high to low.",
            code=r"""import heapq
a, b, c = [1, 4, 7], [2, 5, 8], [3, 6, 9]
print(list(heapq.merge(a, b, c)))
print(list(heapq.merge([5, 3, 1], [6, 4, 2], reverse=True)))""",
            output="[1, 2, 3, 4, 5, 6, 7, 8, 9]\n[6, 5, 4, 3, 2, 1]",
            point="k sorted lists, n items in total: O(n log k).",
        ),
        Slide(
            title="Running median with two heaps",
            text="Keep the smaller half in a max-heap and the larger half in a min-heap, balanced so the lower one is never smaller by size. The median is at the tops of the heaps.",
            code=r"""import heapq
lo, hi = [], []   # lo: max-heap (negated), hi: min-heap
def add(x):
    heapq.heappush(lo, -x)
    heapq.heappush(hi, -heapq.heappop(lo))
    if len(hi) > len(lo): heapq.heappush(lo, -heapq.heappop(hi))
def median(): return -lo[0] if len(lo) > len(hi) else (-lo[0] + hi[0]) / 2
for x in (5, 2, 8, 1): add(x); print(median())""",
            output="5\n3.5\n5\n3.5",
            point="Two heaps keep the middle always within reach: O(log n) per number, O(1) to read the median.",
        ),
        Slide(
            title="Top k frequent words",
            text="Count the words, then ask the heap for the k best by count. To break ties alphabetically, use a key of (negative count, word) and pick the smallest.",
            code=r"""import heapq
from collections import Counter
words = "the day the night the day a day".split()
count = Counter(words)
print(heapq.nsmallest(2, count, key=lambda w: (-count[w], w)))""",
            output="['day', 'the']",
            point="Negative count turns 'smallest' into 'most frequent'; the word then breaks ties.",
        ),
        Slide(
            title="Scheduling with a heap",
            text="How many meeting rooms are needed? Sort by start time and keep a heap of end times. If the earliest-ending meeting is over, reuse its room; otherwise open a new one.",
            code=r"""import heapq
def rooms(meetings):
    ends = []
    for s, e in sorted(meetings):
        if ends and ends[0] <= s: heapq.heapreplace(ends, e)
        else: heapq.heappush(ends, e)
    return len(ends)
print(rooms([(0, 30), (5, 10), (15, 20)]), rooms([(7, 10), (2, 4)]))""",
            output="2 1",
            point="The heap's top answers 'which room frees up first?' in O(1).",
        ),
        Slide(
            title="Why a heap is O(log n)",
            text="A heap is a complete tree stored in a list: the parent of position i is (i - 1) // 2. A push or pop swaps along one path from top to bottom, and a path in n items is only about log2 n long.",
            code=r"""h = [1, 3, 2, 7, 4, 5, 6]
for i in range(1, len(h)):
    print(h[(i - 1) // 2], "<=", h[i])
print("levels:", len(h).bit_length())""",
            output="1 <= 3\n1 <= 2\n3 <= 7\n3 <= 4\n2 <= 5\n2 <= 6\nlevels: 3",
            point="Seven items need 3 levels; a million need only 20. That is the log n.",
        ),
    ),
)
