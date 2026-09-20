"""The Odin Project's computer science half, as katas.

The Odin Project's JavaScript course ends with a section called "A Bit
of Computer Science" — recursion, time and space complexity, then
projects for linked lists, a HashMap, binary search trees and Knight's
Travails. That section is the part of Odin this app can honestly mark,
and it is worth marking: every one of these is a pure function with an
answer that is a number or an array, so a Python oracle can compute it
and JavaScript can be run against it.

What is deliberately not here
-----------------------------
Most of the rest of the course is projects — Library, Tic Tac Toe,
Restaurant Page, Weather App — and they are DOM work, npm, webpack and
fetch. None of that can be marked by running a function and comparing a
value, and pretending otherwise would mean inventing answers, which is
the one thing this project refuses to do. Odin's own instruction for
those is to build them and look at them, which is right.

The objects half — factory functions, constructors, the module pattern,
classes — is real and markable but not as katas: a factory returns an
object holding functions, and a function holding functions cannot be
compared with an expected value. That material is better served by
arranging the lines of one (Magnets) or saying what a closure holds
(Trace), where the answer is something you can actually check.

Linked lists are missing for a different reason. Odin builds them from
scratch because it is teaching what a list is underneath; in a kata the
input would arrive as a JavaScript array, and every interesting
operation on a linked list is one line on an array. The exercise would
be about nothing.

Knight's Travails counts moves rather than returning the path. The
shortest path between two squares is usually not unique — a marker
comparing one correct path against another correct path would fail
people for breadth-first ordering, which teaches distrust rather than
search.
"""

from __future__ import annotations

from collections import deque

from code_coach.kata import Kata

# ── Recursion ────────────────────────────────────────────────


def _factorial_of(n: int) -> int:
    return 1 if n <= 1 else n * _factorial_of(n - 1)


def _fibonacci(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _sum_digits(n: int) -> int:
    n = abs(n)
    return n if n < 10 else n % 10 + _sum_digits(n // 10)


def _power_of(base: int, exponent: int) -> int:
    return 1 if exponent == 0 else base * _power_of(base, exponent - 1)


def _flatten_deep(items: list) -> list:
    out: list = []
    for item in items:
        if isinstance(item, list):
            out.extend(_flatten_deep(item))
        else:
            out.append(item)
    return out


# ── Searching and sorting ────────────────────────────────────


def _binary_search_index(sorted_values: list, target) -> int:
    low, high = 0, len(sorted_values) - 1
    while low <= high:
        middle = (low + high) // 2
        if sorted_values[middle] == target:
            return middle
        if sorted_values[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1


def _merge_sort(numbers: list) -> list:
    if len(numbers) <= 1:
        return list(numbers)
    middle = len(numbers) // 2
    left = _merge_sort(numbers[:middle])
    right = _merge_sort(numbers[middle:])
    out: list = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


# ── The data structure projects ──────────────────────────────


def _hash_string(text: str, capacity: int) -> int:
    total = 0
    for ch in text:
        total = (total * 31 + ord(ch)) % capacity
    return total


def _bst_depth(values: list) -> int:
    """How tall the tree is after inserting these in this order.

    Depth rather than the sorted contents on purpose: an in-order walk
    of a search tree is the sorted values, which `values.sort()` also
    produces, so that kata could be passed without building anything.
    The height depends on the order they arrived in, and nothing but
    the tree knows it.
    """
    tree: dict = {}

    def insert(node: dict, value) -> dict:
        if not node:
            return {"value": value, "left": {}, "right": {}}
        if value < node["value"]:
            node["left"] = insert(node["left"], value)
        elif value > node["value"]:
            node["right"] = insert(node["right"], value)
        return node

    def height(node: dict) -> int:
        if not node:
            return 0
        return 1 + max(height(node["left"]), height(node["right"]))

    for value in values:
        tree = insert(tree, value)
    return height(tree)


def _knight_move_count(start: list, end: list) -> int:
    jumps = ((1, 2), (2, 1), (2, -1), (1, -2),
             (-1, -2), (-2, -1), (-2, 1), (-1, 2))
    begin, target = tuple(start), tuple(end)
    seen = {begin}
    queue = deque([(begin, 0)])
    while queue:
        (x, y), moves = queue.popleft()
        if (x, y) == target:
            return moves
        for dx, dy in jumps:
            nxt = (x + dx, y + dy)
            if 0 <= nxt[0] <= 7 and 0 <= nxt[1] <= 7 and nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, moves + 1))
    return -1


FAMILY = "Odin: computer science"


ODIN: tuple[Kata, ...] = (
    Kata(
        id="odin-factorial",
        level=1,
        language="javascript",
        name="factorialOf",
        family=FAMILY,
        brief=(
            "Return n factorial: n times every whole number below it, "
            "down to 1. Zero factorial is 1, which is the base case "
            "rather than a special case."
        ),
        params=("n",),
        example="factorialOf(5) is 120",
        hint=(
            "Every recursion needs a case that does not recurse. Here it "
            "is n of 0 or 1 returning 1 — get that wrong and it never "
            "stops."
        ),
        cases=((5,), (0,), (1,), (2,), (3,), (4,), (6,), (7,), (10,), (12,)),
        solve=_factorial_of,
        checks=(((0,), 1), ((1,), 1), ((2,), 2), ((5,), 120), ((6,), 720)),
        js_answer=(
            "function factorialOf(n) {\n"
            "  if (n <= 1) return 1;\n"
            "  return n * factorialOf(n - 1);\n"
            "}"
        ),
    ),
    Kata(
        id="odin-fibonacci",
        level=2,
        language="javascript",
        name="fibonacci",
        family=FAMILY,
        brief=(
            "Return the nth Fibonacci number, counting from zero: the "
            "0th is 0, the 1st is 1, and each one after that is the two "
            "before it added together."
        ),
        params=("n",),
        example="fibonacci(7) is 13",
        hint=(
            "The plain recursion is two calls per step and recomputes the "
            "same numbers over and over — Odin's point about time "
            "complexity. A loop carrying the last two values is linear "
            "and shorter to write."
        ),
        cases=((7,), (0,), (1,), (2,), (3,), (5,), (10,), (15,), (20,), (30,)),
        solve=_fibonacci,
        checks=(((0,), 0), ((1,), 1), ((2,), 1), ((7,), 13), ((10,), 55)),
        js_answer=(
            "function fibonacci(n) {\n"
            "  let a = 0;\n"
            "  let b = 1;\n"
            "  for (let i = 0; i < n; i += 1) {\n"
            "    [a, b] = [b, a + b];\n"
            "  }\n"
            "  return a;\n"
            "}"
        ),
    ),
    Kata(
        id="odin-sum-digits",
        level=2,
        language="javascript",
        name="sumDigits",
        family=FAMILY,
        brief=(
            "Add up the digits of a whole number and return the total. A "
            "negative number counts the same as its positive, and a "
            "single digit is its own total."
        ),
        params=("n",),
        example="sumDigits(942) is 15",
        hint=(
            "The remainder after dividing by ten is the last digit, and "
            "dividing by ten with the remainder thrown away is everything "
            "else. That pair is the whole recursion."
        ),
        cases=((942,), (0,), (7,), (10,), (99,), (-45,), (100,), (123,),
               (5050,), (98765,)),
        solve=_sum_digits,
        checks=(((0,), 0), ((7,), 7), ((10,), 1), ((-45,), 9), ((942,), 15)),
        js_answer=(
            "function sumDigits(n) {\n"
            "  const value = Math.abs(n);\n"
            "  if (value < 10) return value;\n"
            "  return (value % 10) + sumDigits(Math.floor(value / 10));\n"
            "}"
        ),
    ),
    Kata(
        id="odin-power-of",
        level=2,
        language="javascript",
        name="powerOf",
        family=FAMILY,
        brief=(
            "Return the base raised to the exponent, without using ** or "
            "Math.pow. The exponent is never negative, and anything to "
            "the power of zero is 1."
        ),
        params=("base", "exponent"),
        example="powerOf(2, 10) is 1024",
        hint=(
            "One multiplication and one smaller exponent. The base case "
            "is the exponent reaching zero, not the base reaching "
            "anything."
        ),
        cases=((2, 10), (2, 0), (5, 1), (3, 3), (10, 2), (1, 50),
               (0, 3), (7, 2), (2, 16), (9, 0)),
        solve=_power_of,
        checks=(((2, 0), 1), ((9, 0), 1), ((5, 1), 5), ((0, 3), 0),
                ((2, 10), 1024)),
        js_answer=(
            "function powerOf(base, exponent) {\n"
            "  if (exponent === 0) return 1;\n"
            "  return base * powerOf(base, exponent - 1);\n"
            "}"
        ),
    ),
    Kata(
        id="odin-flatten-deep",
        level=3,
        language="javascript",
        name="flattenDeep",
        family=FAMILY,
        brief=(
            "Flatten an array however deeply it is nested, keeping the "
            "order. The array you were given must not change."
        ),
        params=("items",),
        example="flattenDeep([1, [2, [3]]]) is [1, 2, 3]",
        hint=(
            "Array.isArray is how you tell a nested row from a value. "
            "Recurse on the rows, keep the values — and note that flat() "
            "with no argument only goes one level, which is the trap."
        ),
        cases=(
            ([1, [2, [3]]],), ([],), ([1],), ([[1]],), ([[[[2]]]],),
            ([1, [2], 3],), ([[1, 2], [3, 4]],), ([[], []],),
            ([1, [2, [3, [4, [5]]]]],), ([[-1], [-2, [-3]]],),
        ),
        solve=_flatten_deep,
        checks=(
            (([],), []), (([1],), [1]), (([[1]],), [1]),
            (([[], []],), []), (([1, [2, [3]]],), [1, 2, 3]),
        ),
        js_answer=(
            "function flattenDeep(items) {\n"
            "  const out = [];\n"
            "  for (const item of items) {\n"
            "    if (Array.isArray(item)) {\n"
            "      out.push(...flattenDeep(item));\n"
            "    } else {\n"
            "      out.push(item);\n"
            "    }\n"
            "  }\n"
            "  return out;\n"
            "}"
        ),
    ),
    Kata(
        id="odin-binary-search",
        level=3,
        language="javascript",
        name="binarySearchIndex",
        family=FAMILY,
        brief=(
            "Find the target in a sorted array and return its index, or "
            "-1 if it is not there. The array has no duplicates."
        ),
        params=("sortedValues", "target"),
        example="binarySearchIndex([1, 3, 5, 7], 5) is 2",
        hint=(
            "Two ends and a middle. Every comparison throws away half of "
            "what is left, which is why this is log n and a scan is not."
        ),
        cases=(
            ([1, 3, 5, 7], 5), ([], 1), ([4], 4), ([4], 9),
            ([1, 2, 3, 4, 5], 1), ([1, 2, 3, 4, 5], 5),
            ([1, 2, 3, 4, 5], 6), ([-9, -4, 0, 3], -4),
            ([2, 4, 6, 8, 10, 12], 12), ([2, 4, 6, 8, 10, 12], 7),
        ),
        solve=_binary_search_index,
        checks=(
            (([], 1), -1), (([4], 4), 0), (([4], 9), -1),
            (([-9, -4, 0, 3], -4), 1), (([1, 3, 5, 7], 5), 2),
        ),
        js_answer=(
            "function binarySearchIndex(sortedValues, target) {\n"
            "  let low = 0;\n"
            "  let high = sortedValues.length - 1;\n"
            "  while (low <= high) {\n"
            "    const middle = Math.floor((low + high) / 2);\n"
            "    if (sortedValues[middle] === target) return middle;\n"
            "    if (sortedValues[middle] < target) {\n"
            "      low = middle + 1;\n"
            "    } else {\n"
            "      high = middle - 1;\n"
            "    }\n"
            "  }\n"
            "  return -1;\n"
            "}"
        ),
    ),
    Kata(
        id="odin-merge-sort",
        level=4,
        language="javascript",
        name="mergeSort",
        family=FAMILY,
        brief=(
            "Sort the numbers smallest first and return a new array. The "
            "array you were given must not change — which rules out "
            "sort() on it directly."
        ),
        params=("numbers",),
        example="mergeSort([3, 1, 2]) is [1, 2, 3]",
        hint=(
            "Split in half, sort each half the same way, then walk the "
            "two sorted halves together taking the smaller front value "
            "each time. The base case is an array of one, which is "
            "already sorted."
        ),
        cases=(
            ([3, 1, 2],), ([],), ([1],), ([2, 1],), ([1, 2],),
            ([5, 4, 3, 2, 1],), ([-3, 1, -2],), ([4, 4, 2],),
            ([10, 1, 9, 2, 8, 3],), ([0, -1, 1],),
        ),
        solve=_merge_sort,
        checks=(
            (([],), []), (([1],), [1]), (([2, 1],), [1, 2]),
            (([-3, 1, -2],), [-3, -2, 1]), (([3, 1, 2],), [1, 2, 3]),
        ),
        js_answer=(
            "function mergeSort(numbers) {\n"
            "  if (numbers.length <= 1) return [...numbers];\n"
            "  const middle = Math.floor(numbers.length / 2);\n"
            "  const left = mergeSort(numbers.slice(0, middle));\n"
            "  const right = mergeSort(numbers.slice(middle));\n"
            "  const out = [];\n"
            "  let i = 0;\n"
            "  let j = 0;\n"
            "  while (i < left.length && j < right.length) {\n"
            "    if (left[i] <= right[j]) {\n"
            "      out.push(left[i]);\n"
            "      i += 1;\n"
            "    } else {\n"
            "      out.push(right[j]);\n"
            "      j += 1;\n"
            "    }\n"
            "  }\n"
            "  return [...out, ...left.slice(i), ...right.slice(j)];\n"
            "}"
        ),
    ),
    Kata(
        id="odin-hash-string",
        level=4,
        language="javascript",
        name="hashString",
        family=FAMILY,
        brief=(
            "Turn text into a bucket number for a hash map of this "
            "capacity. Start at 0 and, for each character in turn, "
            "multiply what you have by 31, add the character's code, and "
            "take the remainder by the capacity. Empty text is bucket 0."
        ),
        params=("text", "capacity"),
        example="hashString('b', 16) is 2",
        hint=(
            "charCodeAt gives the number for one character. Taking the "
            "remainder inside the loop rather than at the end is what "
            "stops the running total overflowing on a long key — the "
            "reason Odin's hash does it that way."
        ),
        cases=(
            ("ab", 16), ("", 16), ("a", 16), ("b", 16), ("abc", 16),
            ("hello", 16), ("hello", 64), ("Z", 8), ("zz", 8),
            ("odin", 32),
        ),
        solve=_hash_string,
        checks=(
            (("", 16), 0), (("a", 16), 1), (("b", 16), 2),
            (("Z", 8), 2), (("ab", 16), 1),
        ),
        js_answer=(
            "function hashString(text, capacity) {\n"
            "  let total = 0;\n"
            "  for (const ch of text) {\n"
            "    total = (total * 31 + ch.charCodeAt(0)) % capacity;\n"
            "  }\n"
            "  return total;\n"
            "}"
        ),
    ),
    Kata(
        id="odin-bst-depth",
        level=4,
        language="javascript",
        name="bstDepth",
        family=FAMILY,
        brief=(
            "Insert the values into a binary search tree, one at a time "
            "in the order given, then return how many levels deep the "
            "tree is. No values is depth 0, one value is depth 1. "
            "Duplicates are ignored."
        ),
        params=("values",),
        example="bstDepth([2, 1, 3]) is 2",
        hint=(
            "The order they arrive in is the whole answer: the same "
            "values sorted give a tree as deep as the list is long, and "
            "balanced give the shallowest one there is. That is why "
            "sorting cannot answer this."
        ),
        cases=(
            ([2, 1, 3],), ([],), ([5],), ([1, 2, 3],), ([3, 2, 1],),
            ([4, 2, 6, 1, 3, 5, 7],), ([1, 1, 1],), ([5, 3, 8, 1],),
            ([10, 5, 15, 2, 7, 20],), ([-1, -2, -3, -4],),
        ),
        solve=_bst_depth,
        checks=(
            (([],), 0), (([5],), 1), (([1, 1, 1],), 1),
            (([-1, -2, -3, -4],), 4), (([2, 1, 3],), 2),
        ),
        js_answer=(
            "function bstDepth(values) {\n"
            "  let root = null;\n"
            "  for (const value of values) {\n"
            "    root = insert(root, value);\n"
            "  }\n"
            "  return height(root);\n"
            "\n"
            "  function insert(node, value) {\n"
            "    if (node === null) return { value, left: null, right: null };\n"
            "    if (value < node.value) node.left = insert(node.left, value);\n"
            "    else if (value > node.value) node.right = insert(node.right, value);\n"
            "    return node;\n"
            "  }\n"
            "\n"
            "  function height(node) {\n"
            "    if (node === null) return 0;\n"
            "    return 1 + Math.max(height(node.left), height(node.right));\n"
            "  }\n"
            "}"
        ),
    ),
    Kata(
        id="odin-knight-moves",
        level=5,
        language="javascript",
        name="knightMoveCount",
        family=FAMILY,
        brief=(
            "On a standard 8x8 board, return the fewest knight moves from "
            "one square to another. Squares are [x, y] with both from 0 "
            "to 7. Starting where you already are takes no moves."
        ),
        params=("start", "end"),
        example="knightMoveCount([0, 0], [1, 2]) is 1",
        hint=(
            "Breadth first, not depth first. Walk outwards one move at a "
            "time and the first time you reach the target you have the "
            "fewest — go deep instead and the first path you find is "
            "almost never the shortest."
        ),
        edge_note=(
            "The awkward input here is a start equal to the end, which "
            "answers 0 and is checked below. The suite's idea of an "
            "awkward value cannot see it: the argument is [0, 0], a "
            "two-item list holding no negative, which looks ordinary to "
            "a rule written for sizes and signs."
        ),
        cases=(
            ([0, 0], [1, 2]), ([0, 0], [0, 0]), ([3, 3], [3, 3]),
            ([0, 0], [7, 7]), ([0, 0], [3, 3]), ([1, 1], [2, 3]),
            ([4, 4], [5, 6]), ([0, 0], [2, 2]), ([7, 0], [0, 7]),
            ([2, 5], [6, 1]),
        ),
        solve=_knight_move_count,
        checks=(
            (([0, 0], [0, 0]), 0), (([3, 3], [3, 3]), 0),
            (([0, 0], [1, 2]), 1), (([0, 0], [2, 2]), 4),
            (([0, 0], [7, 7]), 6),
        ),
        js_answer=(
            "function knightMoveCount(start, end) {\n"
            "  const jumps = [\n"
            "    [1, 2], [2, 1], [2, -1], [1, -2],\n"
            "    [-1, -2], [-2, -1], [-2, 1], [-1, 2],\n"
            "  ];\n"
            "  const key = ([x, y]) => `${x},${y}`;\n"
            "  const seen = new Set([key(start)]);\n"
            "  let queue = [[start, 0]];\n"
            "  while (queue.length) {\n"
            "    const [[x, y], moves] = queue.shift();\n"
            "    if (x === end[0] && y === end[1]) return moves;\n"
            "    for (const [dx, dy] of jumps) {\n"
            "      const next = [x + dx, y + dy];\n"
            "      if (next[0] < 0 || next[0] > 7) continue;\n"
            "      if (next[1] < 0 || next[1] > 7) continue;\n"
            "      if (seen.has(key(next))) continue;\n"
            "      seen.add(key(next));\n"
            "      queue.push([next, moves + 1]);\n"
            "    }\n"
            "  }\n"
            "  return -1;\n"
            "}"
        ),
    ),
)
