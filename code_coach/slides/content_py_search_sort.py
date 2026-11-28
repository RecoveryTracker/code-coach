"""Searching and Sorting: a passive deck. Outputs were worked out by hand; the oracle test runs the code."""

from __future__ import annotations

from . import Deck, Slide

#: Where the deck sits in the picker (lower is earlier).
ORDER = 111

DECK = Deck(
    id="py-search-sort",
    title="Searching and Sorting",
    language="python",
    blurb="Linear and binary search, bisect, stable sorting with keys, the classic sorts by hand, heaps, counting sort, and why sorted input unlocks faster tricks.",
    slides=(
        Slide(
            title="Linear search",
            text="Look at the items one by one until you find the target. It works on any list, sorted or not, but may have to check every item.",
            code=r"""def find(xs, t):
    for i, x in enumerate(xs):
        if x == t:
            return i
    return -1
print(find([5, 8, 2], 2), find([5, 8, 2], 9))""",
            output="2 -1",
            point="Linear search: simple, works anywhere, O(n).",
        ),
        Slide(
            title="Binary search by hand",
            text="On a sorted list, check the middle and throw away the half that cannot hold the target. This version finds the first spot whose value is at least the target. Watch lo and hi close in.",
            code=r"""xs = [1, 3, 5, 7, 9, 11, 13]
lo, hi = 0, len(xs)
while lo < hi:
    mid = (lo + hi) // 2
    print(lo, hi, mid)
    if xs[mid] < 11:
        lo = mid + 1
    else:
        hi = mid
print(lo)""",
            output="0 7 3\n4 7 5\n4 5 4\n5",
            point="Binary search halves the range each step: O(log n).",
        ),
        Slide(
            title="The bisect module",
            text="bisect_left gives the first index where a value could go, and bisect_right the index just after any equal values. insort inserts a value and keeps the list sorted.",
            code=r"""from bisect import bisect_left, bisect_right, insort
xs = [1, 3, 3, 5]
print(bisect_left(xs, 3), bisect_right(xs, 3))
insort(xs, 4)
print(xs)""",
            output="1 3\n[1, 3, 3, 4, 5]",
            point="Right - left tells you how many copies of a value there are.",
        ),
        Slide(
            title="Sorting is stable",
            text="A stable sort keeps items that tie in their original order. Here bo and cy are both 25 and ann and di are both 30, and each pair stays in the order it started in.",
            code=r"""people = [("bo", 25), ("ann", 30), ("cy", 25), ("di", 30)]
print(sorted(people, key=lambda p: p[1]))""",
            output="[('bo', 25), ('cy', 25), ('ann', 30), ('di', 30)]",
            point="Python's sort is stable: ties keep their original order.",
        ),
        Slide(
            title="Sort by several keys",
            text="Use a tuple key, or lean on stability: sort by the least important key first, then by the most important. Both give age high to low, then name A to Z.",
            code=r"""people = [("bo", 25), ("ann", 30), ("cy", 25), ("al", 30)]
print(sorted(people, key=lambda p: (-p[1], p[0])))
s = sorted(people, key=lambda p: p[0])
s.sort(key=lambda p: p[1], reverse=True)
print(s)""",
            output="[('al', 30), ('ann', 30), ('bo', 25), ('cy', 25)]\n[('al', 30), ('ann', 30), ('bo', 25), ('cy', 25)]",
            point="Least important key first, most important last.",
        ),
        Slide(
            title="Sorting with reverse=True",
            text="reverse=True sorts from biggest to smallest. sorted() returns a new list, while list.sort() changes the list in place and returns None.",
            code=r"""nums = [3, 1, 2]
print(sorted(nums, reverse=True))
print(nums)
print(nums.sort(reverse=True))
print(nums)""",
            output="[3, 2, 1]\n[3, 1, 2]\nNone\n[3, 2, 1]",
            point="sorted() gives a new list; .sort() returns None.",
        ),
        Slide(
            title="Bubble sort",
            text="Compare neighbours and swap them if they are in the wrong order, repeating until nothing moves. It is slow, O(n^2), but easy to watch. Each swap is printed.",
            code=r"""xs = [3, 1, 2]
for i in range(len(xs)):
    for j in range(len(xs) - 1 - i):
        if xs[j] > xs[j + 1]:
            xs[j], xs[j + 1] = xs[j + 1], xs[j]
            print("swap", xs)
print(xs)""",
            output="swap [1, 3, 2]\nswap [1, 2, 3]\n[1, 2, 3]",
            point="Bubble sort is for learning, not for real use.",
        ),
        Slide(
            title="Insertion sort",
            text="Keep the front of the list sorted. Take the next item and slide it left past every bigger item until it fits. It is quick on lists that are already nearly sorted.",
            code=r"""xs = [4, 2, 5, 1]
for i in range(1, len(xs)):
    key = xs[i]
    j = i - 1
    while j >= 0 and xs[j] > key:
        xs[j + 1] = xs[j]
        j -= 1
    xs[j + 1] = key
    print(xs)""",
            output="[2, 4, 5, 1]\n[2, 4, 5, 1]\n[1, 2, 4, 5]",
            point="Insertion sort: grow a sorted prefix one item at a time.",
        ),
        Slide(
            title="Merge sort: the merge step",
            text="Merge sort splits a list in half, sorts each half, then merges the two sorted halves. Merging is the clever part: keep taking the smaller front item.",
            code=r"""def merge(a, b):
    out = []
    while a and b:
        out.append(a.pop(0) if a[0] <= b[0] else b.pop(0))
    return out + a + b
print(merge([1, 4, 6], [2, 3, 7]))""",
            output="[1, 2, 3, 4, 6, 7]",
            point="Merge sort is O(n log n): log n levels of merging.",
        ),
        Slide(
            title="Quick sort: partition around a pivot",
            text="Pick a pivot, put smaller items on one side and the rest on the other, then sort each side the same way. The pivot is already in its final place.",
            code=r"""def qsort(xs):
    if len(xs) < 2:
        return xs
    pivot = xs[0]
    small = [x for x in xs[1:] if x < pivot]
    big = [x for x in xs[1:] if x >= pivot]
    return qsort(small) + [pivot] + qsort(big)
print(qsort([3, 6, 1, 8, 2, 3]))""",
            output="[1, 2, 3, 3, 6, 8]",
            point="Quick sort: partition, then recurse on both sides.",
        ),
        Slide(
            title="heapq: a priority queue",
            text="A heap always lets you pull out the smallest item quickly. heappush adds, heappop removes the smallest, and nsmallest or nlargest take a few from a whole list.",
            code=r"""import heapq
h = []
for n in [5, 1, 4, 2]:
    heapq.heappush(h, n)
print(heapq.heappop(h), heapq.heappop(h))
print(heapq.nsmallest(2, [5, 1, 4, 2, 9]))
print(heapq.nlargest(2, [5, 1, 4, 2, 9]))""",
            output="1 2\n[1, 2]\n[9, 5]",
            point="heappop always returns the smallest item first.",
        ),
        Slide(
            title="Counting sort for small ranges",
            text="When values are small whole numbers, count how many times each appears, then write them out in order. No comparing needed, so it is O(n + range).",
            code=r"""nums = [3, 1, 3, 0, 2, 1]
counts = [0] * 4
for n in nums:
    counts[n] += 1
print(counts)
out = []
for value, c in enumerate(counts):
    out += [value] * c
print(out)""",
            output="[1, 2, 1, 2]\n[0, 1, 1, 2, 3, 3]",
            point="If the range is small, counting beats comparing.",
        ),
        Slide(
            title="k-th largest with a heap",
            text="Keep a min-heap of size k. Push every number and pop the smallest whenever the heap grows past k. What is left are the k largest, and the smallest of them is the k-th largest.",
            code=r"""import heapq
def kth_largest(nums, k):
    heap = []
    for n in nums:
        heapq.heappush(heap, n)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]
print(kth_largest([3, 2, 1, 5, 6, 4], 2))""",
            output="5",
            point="A size-k min-heap keeps only the k biggest: O(n log k).",
        ),
        Slide(
            title="Sort first, then two pointers",
            text="Once a list is sorted, one pointer at each end can find a pair with a target sum. If the sum is too small, move the left pointer up; too big, move the right one down.",
            code=r"""nums = sorted([8, 2, 11, 5, 3])
lo, hi = 0, len(nums) - 1
while lo < hi and nums[lo] + nums[hi] != 10:
    if nums[lo] + nums[hi] < 10:
        lo += 1
    else:
        hi -= 1
print(nums[lo], nums[hi])""",
            output="2 8",
            point="Sorting costs O(n log n) but makes the pair search O(n).",
        ),
        Slide(
            title="Rotated sorted array: find the break",
            text="A sorted list was rotated, like [6, 7, 9, 1, 3, 4]. Compare the middle with the last item: if it is bigger, the break is to its right, otherwise it is at the middle or left. This finds the smallest.",
            code=r"""xs = [6, 7, 9, 1, 3, 4]
lo, hi = 0, len(xs) - 1
while lo < hi:
    mid = (lo + hi) // 2
    if xs[mid] > xs[hi]:
        lo = mid + 1
    else:
        hi = mid
print(lo, xs[lo])""",
            output="3 1",
            point="One half is always sorted, so binary search still works.",
        ),
    ),
)
