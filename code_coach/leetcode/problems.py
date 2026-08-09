"""
LeetCode solution bank, grouped by pattern.

Every solution here is plain runnable Python — no `class Solution`, no typing
imports — so a student can type it into practice.py and press Run. Names are
snake_case (Python convention) rather than LeetCode's camelCase; the algorithm
is what transfers, and the muscle memory should build correct Python habits.

Patterns are ordered for learning, not by LeetCode number: each one only needs
ideas from the patterns above it.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass, field


def _src(code: str) -> str:
    """Normalize an indented literal into flush-left source."""
    return textwrap.dedent(code).strip("\n")


@dataclass(frozen=True)
class Problem:
    number: int
    title: str
    difficulty: str  # Easy | Medium | Hard
    idea: str  # the one insight that makes it click
    complexity: str  # "O(n) time, O(1) space"
    code: str

    @property
    def label(self) -> str:
        return f"#{self.number} {self.title}"


@dataclass(frozen=True)
class Pattern:
    id: str  # also the Code Coach class id
    name: str
    order: int  # learning order (1 = do first)
    blurb: str  # what the pattern is
    tell: str  # how to recognize a problem that wants it
    problems: tuple[Problem, ...]
    preamble: tuple[str, ...] = field(default_factory=tuple)
    """Lines/blocks the pattern's solutions assume (imports, node classes).
    These become the first typing exercises of the pattern."""


def _p(
    number: int,
    title: str,
    difficulty: str,
    idea: str,
    complexity: str,
    code: str,
) -> Problem:
    return Problem(number, title, difficulty, idea, complexity, _src(code))


# ── Shared preambles ────────────────────────────────────────

_LIST_NODE = _src(
    """
    class ListNode:
        def __init__(self, val=0, next=None):
            self.val = val
            self.next = next
    """
)

_TREE_NODE = _src(
    """
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right
    """
)

_GRAPH_NODE = _src(
    """
    class Node:
        def __init__(self, val=0, neighbors=None):
            self.val = val
            self.neighbors = neighbors or []
    """
)

_DEQUE = "from collections import deque"
_HEAPQ = "import heapq"


# ── 1. Hash map / frequency counting ────────────────────────

_HASHMAP = Pattern(
    id="lc-hashmap",
    name="Hash Maps",
    order=1,
    blurb="Trade memory for speed: remember what you've seen in a dict or set.",
    tell="You'd otherwise need a nested loop to ask 'have I seen this before?'",
    problems=(
        _p(
            1,
            "Two Sum",
            "Easy",
            "Store each number's index as you pass it, then look up the complement.",
            "O(n) time, O(n) space",
            """
            def two_sum(nums, target):
                seen = {}
                for i, n in enumerate(nums):
                    need = target - n
                    if need in seen:
                        return [seen[need], i]
                    seen[n] = i
                return []
            """,
        ),
        _p(
            217,
            "Contains Duplicate",
            "Easy",
            "A set answers 'seen already?' in constant time.",
            "O(n) time, O(n) space",
            """
            def contains_duplicate(nums):
                seen = set()
                for n in nums:
                    if n in seen:
                        return True
                    seen.add(n)
                return False
            """,
        ),
        _p(
            242,
            "Valid Anagram",
            "Easy",
            "Count letters up for one word, down for the other.",
            "O(n) time, O(1) space (26 letters)",
            """
            def is_anagram(s, t):
                if len(s) != len(t):
                    return False
                counts = {}
                for ch in s:
                    counts[ch] = counts.get(ch, 0) + 1
                for ch in t:
                    if counts.get(ch, 0) == 0:
                        return False
                    counts[ch] -= 1
                return True
            """,
        ),
        _p(
            49,
            "Group Anagrams",
            "Medium",
            "Sorted letters make a key that all anagrams share.",
            "O(n k log k) time, O(n k) space",
            """
            def group_anagrams(strs):
                groups = {}
                for word in strs:
                    key = "".join(sorted(word))
                    if key not in groups:
                        groups[key] = []
                    groups[key].append(word)
                return list(groups.values())
            """,
        ),
    ),
)


# ── 2. Two pointers ─────────────────────────────────────────

_TWO_POINTERS = Pattern(
    id="lc-two-pointers",
    name="Two Pointers",
    order=2,
    blurb="Walk two indexes toward each other (or together) instead of nesting loops.",
    tell="The input is sorted, or you care about pairs from opposite ends.",
    problems=(
        _p(
            125,
            "Valid Palindrome",
            "Easy",
            "Skip non-letters from both ends and compare inward.",
            "O(n) time, O(1) space",
            """
            def is_palindrome(s):
                left, right = 0, len(s) - 1
                while left < right:
                    while left < right and not s[left].isalnum():
                        left += 1
                    while left < right and not s[right].isalnum():
                        right -= 1
                    if s[left].lower() != s[right].lower():
                        return False
                    left += 1
                    right -= 1
                return True
            """,
        ),
        _p(
            167,
            "Two Sum II (sorted)",
            "Medium",
            "Too big? Move right in. Too small? Move left out.",
            "O(n) time, O(1) space",
            """
            def two_sum_sorted(numbers, target):
                left, right = 0, len(numbers) - 1
                while left < right:
                    total = numbers[left] + numbers[right]
                    if total == target:
                        return [left + 1, right + 1]
                    if total < target:
                        left += 1
                    else:
                        right -= 1
                return []
            """,
        ),
        _p(
            11,
            "Container With Most Water",
            "Medium",
            "Always move the shorter wall — the taller one can't help you.",
            "O(n) time, O(1) space",
            """
            def max_area(height):
                left, right = 0, len(height) - 1
                best = 0
                while left < right:
                    width = right - left
                    best = max(best, width * min(height[left], height[right]))
                    if height[left] < height[right]:
                        left += 1
                    else:
                        right -= 1
                return best
            """,
        ),
        _p(
            15,
            "3Sum",
            "Medium",
            "Sort, fix one number, then two-pointer the rest for its negative.",
            "O(n^2) time, O(1) extra space",
            """
            def three_sum(nums):
                nums.sort()
                result = []
                for i in range(len(nums) - 2):
                    if i > 0 and nums[i] == nums[i - 1]:
                        continue
                    left, right = i + 1, len(nums) - 1
                    while left < right:
                        total = nums[i] + nums[left] + nums[right]
                        if total < 0:
                            left += 1
                        elif total > 0:
                            right -= 1
                        else:
                            result.append([nums[i], nums[left], nums[right]])
                            left += 1
                            while left < right and nums[left] == nums[left - 1]:
                                left += 1
                return result
            """,
        ),
    ),
)


# ── 3. Sliding window ───────────────────────────────────────

_SLIDING_WINDOW = Pattern(
    id="lc-sliding-window",
    name="Sliding Window",
    order=3,
    blurb="Two pointers where the gap between them IS the answer you're measuring.",
    tell="'Longest / shortest / best contiguous run that satisfies ...'",
    problems=(
        _p(
            121,
            "Best Time to Buy and Sell Stock",
            "Easy",
            "Track the cheapest price so far; every day ask what selling today pays.",
            "O(n) time, O(1) space",
            """
            def max_profit(prices):
                best = 0
                cheapest = float("inf")
                for price in prices:
                    cheapest = min(cheapest, price)
                    best = max(best, price - cheapest)
                return best
            """,
        ),
        _p(
            3,
            "Longest Substring Without Repeating Characters",
            "Medium",
            "On a repeat, jump the window start past the previous copy.",
            "O(n) time, O(min(n, alphabet)) space",
            """
            def length_of_longest_substring(s):
                last_seen = {}
                start = 0
                best = 0
                for i, ch in enumerate(s):
                    if ch in last_seen and last_seen[ch] >= start:
                        start = last_seen[ch] + 1
                    last_seen[ch] = i
                    best = max(best, i - start + 1)
                return best
            """,
        ),
        _p(
            209,
            "Minimum Size Subarray Sum",
            "Medium",
            "Grow right always; shrink left while the window still qualifies.",
            "O(n) time, O(1) space",
            """
            def min_sub_array_len(target, nums):
                left = 0
                total = 0
                best = len(nums) + 1
                for right, n in enumerate(nums):
                    total += n
                    while total >= target:
                        best = min(best, right - left + 1)
                        total -= nums[left]
                        left += 1
                return best if best <= len(nums) else 0
            """,
        ),
        _p(
            424,
            "Longest Repeating Character Replacement",
            "Medium",
            "A window is legal when (size - most common letter) <= k.",
            "O(n) time, O(1) space",
            """
            def character_replacement(s, k):
                counts = {}
                left = 0
                most_common = 0
                best = 0
                for right, ch in enumerate(s):
                    counts[ch] = counts.get(ch, 0) + 1
                    most_common = max(most_common, counts[ch])
                    while (right - left + 1) - most_common > k:
                        counts[s[left]] -= 1
                        left += 1
                    best = max(best, right - left + 1)
                return best
            """,
        ),
    ),
)


# ── 4. Stack ────────────────────────────────────────────────

_STACK = Pattern(
    id="lc-stack",
    name="Stacks",
    order=4,
    blurb="A list you only push and pop from the end of — last in, first out.",
    tell="Matching pairs, undo, or 'the next bigger thing to the right'.",
    problems=(
        _p(
            20,
            "Valid Parentheses",
            "Easy",
            "Push openers; every closer must match the most recent opener.",
            "O(n) time, O(n) space",
            """
            def is_valid(s):
                pairs = {")": "(", "]": "[", "}": "{"}
                stack = []
                for ch in s:
                    if ch in pairs:
                        if not stack or stack.pop() != pairs[ch]:
                            return False
                    else:
                        stack.append(ch)
                return not stack
            """,
        ),
        _p(
            155,
            "Min Stack",
            "Medium",
            "Keep a parallel stack of 'the minimum as of this push'.",
            "O(1) per operation, O(n) space",
            """
            class MinStack:
                def __init__(self):
                    self.stack = []
                    self.mins = []

                def push(self, val):
                    self.stack.append(val)
                    if not self.mins or val <= self.mins[-1]:
                        self.mins.append(val)

                def pop(self):
                    val = self.stack.pop()
                    if self.mins and val == self.mins[-1]:
                        self.mins.pop()

                def top(self):
                    return self.stack[-1]

                def get_min(self):
                    return self.mins[-1]
            """,
        ),
        _p(
            150,
            "Evaluate Reverse Polish Notation",
            "Medium",
            "Numbers go on the stack; an operator pops two and pushes the result.",
            "O(n) time, O(n) space",
            """
            def eval_rpn(tokens):
                stack = []
                for token in tokens:
                    if token == "+":
                        stack.append(stack.pop() + stack.pop())
                    elif token == "*":
                        stack.append(stack.pop() * stack.pop())
                    elif token == "-":
                        b, a = stack.pop(), stack.pop()
                        stack.append(a - b)
                    elif token == "/":
                        b, a = stack.pop(), stack.pop()
                        stack.append(int(a / b))
                    else:
                        stack.append(int(token))
                return stack[0]
            """,
        ),
        _p(
            739,
            "Daily Temperatures",
            "Medium",
            "Monotonic stack of indexes still waiting for a warmer day.",
            "O(n) time, O(n) space",
            """
            def daily_temperatures(temperatures):
                answer = [0] * len(temperatures)
                stack = []
                for i, temp in enumerate(temperatures):
                    while stack and temperatures[stack[-1]] < temp:
                        prev = stack.pop()
                        answer[prev] = i - prev
                    stack.append(i)
                return answer
            """,
        ),
    ),
)


# ── 5. Linked list ──────────────────────────────────────────

_LINKED_LIST = Pattern(
    id="lc-linked-list",
    name="Linked Lists",
    order=5,
    blurb="Nodes joined by .next — you can only walk forward, so save what you need.",
    tell="Reversing, merging, or finding a position relative to the end.",
    preamble=(_LIST_NODE,),
    problems=(
        _p(
            206,
            "Reverse Linked List",
            "Easy",
            "Save next, flip the arrow backward, then step both cursors forward.",
            "O(n) time, O(1) space",
            """
            def reverse_list(head):
                prev = None
                while head:
                    nxt = head.next
                    head.next = prev
                    prev = head
                    head = nxt
                return prev
            """,
        ),
        _p(
            21,
            "Merge Two Sorted Lists",
            "Easy",
            "A dummy head means you never special-case the first node.",
            "O(n + m) time, O(1) space",
            """
            def merge_two_lists(list1, list2):
                dummy = ListNode()
                tail = dummy
                while list1 and list2:
                    if list1.val <= list2.val:
                        tail.next = list1
                        list1 = list1.next
                    else:
                        tail.next = list2
                        list2 = list2.next
                    tail = tail.next
                tail.next = list1 or list2
                return dummy.next
            """,
        ),
        _p(
            141,
            "Linked List Cycle",
            "Easy",
            "Fast moves two, slow moves one — in a loop they must collide.",
            "O(n) time, O(1) space",
            """
            def has_cycle(head):
                slow = head
                fast = head
                while fast and fast.next:
                    slow = slow.next
                    fast = fast.next.next
                    if slow is fast:
                        return True
                return False
            """,
        ),
        _p(
            19,
            "Remove Nth Node From End",
            "Medium",
            "Start fast n nodes ahead; when it ends, slow is on the node before.",
            "O(n) time, O(1) space",
            """
            def remove_nth_from_end(head, n):
                dummy = ListNode(0, head)
                slow = dummy
                fast = dummy
                for _ in range(n):
                    fast = fast.next
                while fast.next:
                    slow = slow.next
                    fast = fast.next
                slow.next = slow.next.next
                return dummy.next
            """,
        ),
    ),
)


# ── 6. Modified binary search ───────────────────────────────

_BINARY_SEARCH = Pattern(
    id="lc-binary-search",
    name="Binary Search",
    order=6,
    blurb="Halve the search space every step by asking one yes/no question.",
    tell="Sorted input, or 'smallest value that works' over a numeric range.",
    problems=(
        _p(
            704,
            "Binary Search",
            "Easy",
            "Closed range [low, high]: shrink past mid every time.",
            "O(log n) time, O(1) space",
            """
            def search(nums, target):
                low, high = 0, len(nums) - 1
                while low <= high:
                    mid = (low + high) // 2
                    if nums[mid] == target:
                        return mid
                    if nums[mid] < target:
                        low = mid + 1
                    else:
                        high = mid - 1
                return -1
            """,
        ),
        _p(
            35,
            "Search Insert Position",
            "Easy",
            "Half-open range [low, high): low lands on the insert point.",
            "O(log n) time, O(1) space",
            """
            def search_insert(nums, target):
                low, high = 0, len(nums)
                while low < high:
                    mid = (low + high) // 2
                    if nums[mid] < target:
                        low = mid + 1
                    else:
                        high = mid
                return low
            """,
        ),
        _p(
            153,
            "Find Minimum in Rotated Sorted Array",
            "Medium",
            "Compare mid to the right end to learn which half holds the dip.",
            "O(log n) time, O(1) space",
            """
            def find_min(nums):
                low, high = 0, len(nums) - 1
                while low < high:
                    mid = (low + high) // 2
                    if nums[mid] > nums[high]:
                        low = mid + 1
                    else:
                        high = mid
                return nums[low]
            """,
        ),
        _p(
            33,
            "Search in Rotated Sorted Array",
            "Medium",
            "One half is always sorted — check if the target lies inside it.",
            "O(log n) time, O(1) space",
            """
            def search_rotated(nums, target):
                low, high = 0, len(nums) - 1
                while low <= high:
                    mid = (low + high) // 2
                    if nums[mid] == target:
                        return mid
                    if nums[low] <= nums[mid]:
                        if nums[low] <= target < nums[mid]:
                            high = mid - 1
                        else:
                            low = mid + 1
                    else:
                        if nums[mid] < target <= nums[high]:
                            low = mid + 1
                        else:
                            high = mid - 1
                return -1
            """,
        ),
        _p(
            875,
            "Koko Eating Bananas",
            "Medium",
            "Binary search the ANSWER: the slowest speed that still finishes in time.",
            "O(n log m) time, O(1) space",
            """
            def min_eating_speed(piles, h):
                low, high = 1, max(piles)
                while low < high:
                    speed = (low + high) // 2
                    hours = 0
                    for pile in piles:
                        hours += (pile + speed - 1) // speed
                    if hours <= h:
                        high = speed
                    else:
                        low = speed + 1
                return low
            """,
        ),
    ),
)


# ── 7. Binary tree DFS ──────────────────────────────────────

_TREE_DFS = Pattern(
    id="lc-tree-dfs",
    name="Tree DFS",
    order=7,
    blurb="Recursion down one branch at a time: solve the children, combine, return.",
    tell="The answer for a node is built from the answers for its subtrees.",
    preamble=(_TREE_NODE,),
    problems=(
        _p(
            104,
            "Maximum Depth of Binary Tree",
            "Easy",
            "Depth here = 1 + the deeper of my two children.",
            "O(n) time, O(h) space",
            """
            def max_depth(root):
                if not root:
                    return 0
                return 1 + max(max_depth(root.left), max_depth(root.right))
            """,
        ),
        _p(
            226,
            "Invert Binary Tree",
            "Easy",
            "Swap the children, then let recursion handle each side.",
            "O(n) time, O(h) space",
            """
            def invert_tree(root):
                if not root:
                    return None
                root.left, root.right = invert_tree(root.right), invert_tree(root.left)
                return root
            """,
        ),
        _p(
            112,
            "Path Sum",
            "Easy",
            "Subtract as you descend; at a leaf ask whether the remainder fits.",
            "O(n) time, O(h) space",
            """
            def has_path_sum(root, target_sum):
                if not root:
                    return False
                if not root.left and not root.right:
                    return target_sum == root.val
                rest = target_sum - root.val
                return has_path_sum(root.left, rest) or has_path_sum(root.right, rest)
            """,
        ),
        _p(
            543,
            "Diameter of Binary Tree",
            "Easy",
            "Return depth upward, but record left + right as a candidate answer.",
            "O(n) time, O(h) space",
            """
            def diameter_of_binary_tree(root):
                best = 0

                def depth(node):
                    nonlocal best
                    if not node:
                        return 0
                    left = depth(node.left)
                    right = depth(node.right)
                    best = max(best, left + right)
                    return 1 + max(left, right)

                depth(root)
                return best
            """,
        ),
        _p(
            98,
            "Validate Binary Search Tree",
            "Medium",
            "Carry an allowed (low, high) range down instead of checking neighbours.",
            "O(n) time, O(h) space",
            """
            def is_valid_bst(root):
                def check(node, low, high):
                    if not node:
                        return True
                    if not low < node.val < high:
                        return False
                    return check(node.left, low, node.val) and check(node.right, node.val, high)

                return check(root, float("-inf"), float("inf"))
            """,
        ),
    ),
)


# ── 8. Binary tree BFS ──────────────────────────────────────

_TREE_BFS = Pattern(
    id="lc-tree-bfs",
    name="Tree BFS",
    order=8,
    blurb="A queue walks the tree level by level instead of branch by branch.",
    tell="The question mentions levels, rows, depth order, or 'nearest'.",
    preamble=(_TREE_NODE, _DEQUE),
    problems=(
        _p(
            102,
            "Binary Tree Level Order Traversal",
            "Medium",
            "Snapshot len(queue) first — that's exactly one level's worth.",
            "O(n) time, O(n) space",
            """
            def level_order(root):
                if not root:
                    return []
                levels = []
                queue = deque([root])
                while queue:
                    level = []
                    for _ in range(len(queue)):
                        node = queue.popleft()
                        level.append(node.val)
                        if node.left:
                            queue.append(node.left)
                        if node.right:
                            queue.append(node.right)
                    levels.append(level)
                return levels
            """,
        ),
        _p(
            199,
            "Binary Tree Right Side View",
            "Medium",
            "Keep the last node of every level.",
            "O(n) time, O(n) space",
            """
            def right_side_view(root):
                if not root:
                    return []
                view = []
                queue = deque([root])
                while queue:
                    size = len(queue)
                    for i in range(size):
                        node = queue.popleft()
                        if i == size - 1:
                            view.append(node.val)
                        if node.left:
                            queue.append(node.left)
                        if node.right:
                            queue.append(node.right)
                return view
            """,
        ),
        _p(
            103,
            "Binary Tree Zigzag Level Order",
            "Medium",
            "Same level walk — just reverse every other row before storing it.",
            "O(n) time, O(n) space",
            """
            def zigzag_level_order(root):
                if not root:
                    return []
                levels = []
                queue = deque([root])
                left_to_right = True
                while queue:
                    level = []
                    for _ in range(len(queue)):
                        node = queue.popleft()
                        level.append(node.val)
                        if node.left:
                            queue.append(node.left)
                        if node.right:
                            queue.append(node.right)
                    if not left_to_right:
                        level.reverse()
                    levels.append(level)
                    left_to_right = not left_to_right
                return levels
            """,
        ),
    ),
)


# ── 9. Graphs & grids ───────────────────────────────────────

_GRAPH = Pattern(
    id="lc-graph",
    name="Graphs & Grids",
    order=9,
    blurb="Same DFS/BFS as trees, but you must mark visited — graphs have cycles.",
    tell="A grid of cells, or nodes with edges/neighbours.",
    preamble=(_DEQUE, _GRAPH_NODE),
    problems=(
        _p(
            733,
            "Flood Fill",
            "Easy",
            "Recurse to the four neighbours, stopping when the colour doesn't match.",
            "O(n) time, O(n) space",
            """
            def flood_fill(image, sr, sc, color):
                start = image[sr][sc]
                if start == color:
                    return image
                rows, cols = len(image), len(image[0])

                def fill(r, c):
                    if r < 0 or r >= rows or c < 0 or c >= cols:
                        return
                    if image[r][c] != start:
                        return
                    image[r][c] = color
                    fill(r + 1, c)
                    fill(r - 1, c)
                    fill(r, c + 1)
                    fill(r, c - 1)

                fill(sr, sc)
                return image
            """,
        ),
        _p(
            200,
            "Number of Islands",
            "Medium",
            "Each unvisited land cell starts an island; sink the whole thing.",
            "O(rows * cols) time, O(rows * cols) space",
            """
            def num_islands(grid):
                if not grid:
                    return 0
                rows, cols = len(grid), len(grid[0])
                count = 0

                def sink(r, c):
                    if r < 0 or r >= rows or c < 0 or c >= cols:
                        return
                    if grid[r][c] != "1":
                        return
                    grid[r][c] = "0"
                    sink(r + 1, c)
                    sink(r - 1, c)
                    sink(r, c + 1)
                    sink(r, c - 1)

                for r in range(rows):
                    for c in range(cols):
                        if grid[r][c] == "1":
                            count += 1
                            sink(r, c)
                return count
            """,
        ),
        _p(
            994,
            "Rotting Oranges",
            "Medium",
            "Multi-source BFS — every rotten orange starts in the queue at minute 0.",
            "O(rows * cols) time, O(rows * cols) space",
            """
            def oranges_rotting(grid):
                rows, cols = len(grid), len(grid[0])
                queue = deque()
                fresh = 0
                for r in range(rows):
                    for c in range(cols):
                        if grid[r][c] == 2:
                            queue.append((r, c))
                        elif grid[r][c] == 1:
                            fresh += 1
                minutes = 0
                while queue and fresh:
                    minutes += 1
                    for _ in range(len(queue)):
                        r, c = queue.popleft()
                        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                                grid[nr][nc] = 2
                                fresh -= 1
                                queue.append((nr, nc))
                return -1 if fresh else minutes
            """,
        ),
        _p(
            133,
            "Clone Graph",
            "Medium",
            "A dict from original node to its copy doubles as the visited set.",
            "O(n + e) time, O(n) space",
            """
            def clone_graph(node):
                clones = {}

                def copy(cur):
                    if not cur:
                        return None
                    if cur in clones:
                        return clones[cur]
                    clone = Node(cur.val)
                    clones[cur] = clone
                    for neighbor in cur.neighbors:
                        clone.neighbors.append(copy(neighbor))
                    return clone

                return copy(node)
            """,
        ),
    ),
)


# ── 10. Backtracking / subsets ──────────────────────────────

_BACKTRACKING = Pattern(
    id="lc-backtracking",
    name="Subsets & Backtracking",
    order=10,
    blurb="Choose, recurse, un-choose — explore every combination without repeating work.",
    tell="'All subsets / permutations / combinations that ...'",
    problems=(
        _p(
            78,
            "Subsets",
            "Medium",
            "Every prefix of the walk is already a valid subset — record on entry.",
            "O(n * 2^n) time, O(n) recursion depth",
            """
            def subsets(nums):
                result = []
                current = []

                def backtrack(start):
                    result.append(current[:])
                    for i in range(start, len(nums)):
                        current.append(nums[i])
                        backtrack(i + 1)
                        current.pop()

                backtrack(0)
                return result
            """,
        ),
        _p(
            90,
            "Subsets II",
            "Medium",
            "Sort first, then skip a duplicate unless it's the first pick at this level.",
            "O(n * 2^n) time, O(n) recursion depth",
            """
            def subsets_with_dup(nums):
                nums.sort()
                result = []
                current = []

                def backtrack(start):
                    result.append(current[:])
                    for i in range(start, len(nums)):
                        if i > start and nums[i] == nums[i - 1]:
                            continue
                        current.append(nums[i])
                        backtrack(i + 1)
                        current.pop()

                backtrack(0)
                return result
            """,
        ),
        _p(
            46,
            "Permutations",
            "Medium",
            "Order matters, so track which indexes are already used.",
            "O(n * n!) time, O(n) recursion depth",
            """
            def permute(nums):
                result = []
                current = []
                used = [False] * len(nums)

                def backtrack():
                    if len(current) == len(nums):
                        result.append(current[:])
                        return
                    for i in range(len(nums)):
                        if used[i]:
                            continue
                        used[i] = True
                        current.append(nums[i])
                        backtrack()
                        current.pop()
                        used[i] = False

                backtrack()
                return result
            """,
        ),
        _p(
            39,
            "Combination Sum",
            "Medium",
            "Reuse allowed, so recurse with i (not i + 1) and shrink the remainder.",
            "O(n^(target/min)) time, O(target) depth",
            """
            def combination_sum(candidates, target):
                result = []
                current = []

                def backtrack(start, remaining):
                    if remaining == 0:
                        result.append(current[:])
                        return
                    if remaining < 0:
                        return
                    for i in range(start, len(candidates)):
                        current.append(candidates[i])
                        backtrack(i, remaining - candidates[i])
                        current.pop()

                backtrack(0, target)
                return result
            """,
        ),
        _p(
            79,
            "Word Search",
            "Medium",
            "Backtracking on a grid — blank out the cell, recurse, then restore it.",
            "O(rows * cols * 4^len(word)) time, O(len(word)) depth",
            """
            def exist(board, word):
                rows, cols = len(board), len(board[0])

                def search(r, c, i):
                    if i == len(word):
                        return True
                    if r < 0 or r >= rows or c < 0 or c >= cols:
                        return False
                    if board[r][c] != word[i]:
                        return False
                    board[r][c] = "#"
                    found = (
                        search(r + 1, c, i + 1)
                        or search(r - 1, c, i + 1)
                        or search(r, c + 1, i + 1)
                        or search(r, c - 1, i + 1)
                    )
                    board[r][c] = word[i]
                    return found

                for r in range(rows):
                    for c in range(cols):
                        if search(r, c, 0):
                            return True
                return False
            """,
        ),
    ),
)


# ── 11. Top K / heap ────────────────────────────────────────

_HEAP = Pattern(
    id="lc-heap",
    name="Top K (Heaps)",
    order=11,
    blurb="A size-k heap keeps the best k items without sorting everything.",
    tell="'K largest / K closest / K most frequent'.",
    preamble=(_HEAPQ,),
    problems=(
        _p(
            215,
            "Kth Largest Element in an Array",
            "Medium",
            "Hold a min-heap of size k; its root is the kth largest.",
            "O(n log k) time, O(k) space",
            """
            def find_kth_largest(nums, k):
                heap = []
                for n in nums:
                    heapq.heappush(heap, n)
                    if len(heap) > k:
                        heapq.heappop(heap)
                return heap[0]
            """,
        ),
        _p(
            347,
            "Top K Frequent Elements",
            "Medium",
            "Count first, then heap on (count, value) and keep only k.",
            "O(n log k) time, O(n) space",
            """
            def top_k_frequent(nums, k):
                counts = {}
                for n in nums:
                    counts[n] = counts.get(n, 0) + 1
                heap = []
                for value, count in counts.items():
                    heapq.heappush(heap, (count, value))
                    if len(heap) > k:
                        heapq.heappop(heap)
                return [value for count, value in heap]
            """,
        ),
        _p(
            973,
            "K Closest Points to Origin",
            "Medium",
            "Push negative distance so the max-distance point pops first.",
            "O(n log k) time, O(k) space",
            """
            def k_closest(points, k):
                heap = []
                for x, y in points:
                    dist = x * x + y * y
                    heapq.heappush(heap, (-dist, x, y))
                    if len(heap) > k:
                        heapq.heappop(heap)
                return [[x, y] for dist, x, y in heap]
            """,
        ),
    ),
)


# ── 12. Topological sort ────────────────────────────────────

_TOPOLOGICAL = Pattern(
    id="lc-topological",
    name="Topological Sort",
    order=12,
    blurb="Repeatedly take whatever has no unmet prerequisites (indegree 0).",
    tell="Dependencies, ordering, 'can this schedule be completed?'",
    preamble=(_DEQUE,),
    problems=(
        _p(
            207,
            "Course Schedule",
            "Medium",
            "If a cycle exists you can never drain the queue — count what you took.",
            "O(v + e) time, O(v + e) space",
            """
            def can_finish(num_courses, prerequisites):
                graph = {i: [] for i in range(num_courses)}
                indegree = [0] * num_courses
                for course, prereq in prerequisites:
                    graph[prereq].append(course)
                    indegree[course] += 1
                queue = deque([i for i in range(num_courses) if indegree[i] == 0])
                taken = 0
                while queue:
                    node = queue.popleft()
                    taken += 1
                    for nxt in graph[node]:
                        indegree[nxt] -= 1
                        if indegree[nxt] == 0:
                            queue.append(nxt)
                return taken == num_courses
            """,
        ),
        _p(
            210,
            "Course Schedule II",
            "Medium",
            "Same peel, but keep the order you took things in.",
            "O(v + e) time, O(v + e) space",
            """
            def find_order(num_courses, prerequisites):
                graph = {i: [] for i in range(num_courses)}
                indegree = [0] * num_courses
                for course, prereq in prerequisites:
                    graph[prereq].append(course)
                    indegree[course] += 1
                queue = deque([i for i in range(num_courses) if indegree[i] == 0])
                order = []
                while queue:
                    node = queue.popleft()
                    order.append(node)
                    for nxt in graph[node]:
                        indegree[nxt] -= 1
                        if indegree[nxt] == 0:
                            queue.append(nxt)
                return order if len(order) == num_courses else []
            """,
        ),
        _p(
            310,
            "Minimum Height Trees",
            "Medium",
            "Peel leaves layer by layer; the last 1 or 2 left are the centres.",
            "O(v + e) time, O(v + e) space",
            """
            def find_min_height_trees(n, edges):
                if n == 1:
                    return [0]
                graph = {i: set() for i in range(n)}
                for a, b in edges:
                    graph[a].add(b)
                    graph[b].add(a)
                leaves = [i for i in range(n) if len(graph[i]) == 1]
                remaining = n
                while remaining > 2:
                    remaining -= len(leaves)
                    next_leaves = []
                    for leaf in leaves:
                        neighbor = graph[leaf].pop()
                        graph[neighbor].remove(leaf)
                        if len(graph[neighbor]) == 1:
                            next_leaves.append(neighbor)
                    leaves = next_leaves
                return leaves
            """,
        ),
    ),
)


# ── 13. Dynamic programming ─────────────────────────────────

_DP = Pattern(
    id="lc-dp",
    name="Dynamic Programming",
    order=13,
    blurb="Solve small cases once, store them, and build the big answer from them.",
    tell="Overlapping subproblems — the naive recursion recomputes the same thing.",
    problems=(
        _p(
            70,
            "Climbing Stairs",
            "Easy",
            "Ways to reach step n = ways to n-1 plus ways to n-2. It's Fibonacci.",
            "O(n) time, O(1) space",
            """
            def climb_stairs(n):
                prev, cur = 1, 1
                for _ in range(n - 1):
                    prev, cur = cur, prev + cur
                return cur
            """,
        ),
        _p(
            198,
            "House Robber",
            "Medium",
            "At each house: best so far if you skip it, or (best before last) + it.",
            "O(n) time, O(1) space",
            """
            def rob(nums):
                skip, take = 0, 0
                for n in nums:
                    skip, take = max(skip, take), skip + n
                return max(skip, take)
            """,
        ),
        _p(
            322,
            "Coin Change",
            "Medium",
            "Build up every amount from 1 to target, trying each coin as the last one.",
            "O(amount * coins) time, O(amount) space",
            """
            def coin_change(coins, amount):
                best = [amount + 1] * (amount + 1)
                best[0] = 0
                for value in range(1, amount + 1):
                    for coin in coins:
                        if coin <= value:
                            best[value] = min(best[value], best[value - coin] + 1)
                return best[amount] if best[amount] <= amount else -1
            """,
        ),
        _p(
            300,
            "Longest Increasing Subsequence",
            "Medium",
            "Keep the smallest possible tail for each length; binary search its slot.",
            "O(n log n) time, O(n) space",
            """
            def length_of_lis(nums):
                tails = []
                for n in nums:
                    low, high = 0, len(tails)
                    while low < high:
                        mid = (low + high) // 2
                        if tails[mid] < n:
                            low = mid + 1
                        else:
                            high = mid
                    if low == len(tails):
                        tails.append(n)
                    else:
                        tails[low] = n
                return len(tails)
            """,
        ),
    ),
)


# ── Registry ────────────────────────────────────────────────

PATTERNS: tuple[Pattern, ...] = (
    _HASHMAP,
    _TWO_POINTERS,
    _SLIDING_WINDOW,
    _STACK,
    _LINKED_LIST,
    _BINARY_SEARCH,
    _TREE_DFS,
    _TREE_BFS,
    _GRAPH,
    _BACKTRACKING,
    _HEAP,
    _TOPOLOGICAL,
    _DP,
)

PATTERNS_BY_ID: dict[str, Pattern] = {p.id: p for p in PATTERNS}

# The "type every answer" class — not a real pattern, a view over all of them.
ALL_CLASS_ID = "lc-all"


def get_pattern(pattern_id: str) -> Pattern | None:
    return PATTERNS_BY_ID.get(pattern_id)


def all_problems() -> list[Problem]:
    """Every solution, in learning order."""
    out: list[Problem] = []
    for pattern in PATTERNS:
        out.extend(pattern.problems)
    return out


def problem_count() -> int:
    return sum(len(p.problems) for p in PATTERNS)
