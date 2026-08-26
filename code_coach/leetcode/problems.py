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
        _p(
            454,
            "4Sum II",
            "Medium",
            "Count every sum from the first two lists, then look up its negation from the other two.",
            "O(n^2) time, O(n^2) space",
            """
            def four_sum_count(a, b, c, d):
                pairs = {}
                for x in a:
                    for y in b:
                        pairs[x + y] = pairs.get(x + y, 0) + 1
                found = 0
                for z in c:
                    for w in d:
                        found += pairs.get(-(z + w), 0)
                return found
            """,
        ),
        _p(
            560,
            "Subarray Sum Equals K",
            "Medium",
            "Remember every running total you've seen; the gap between two of them is a subarray.",
            "O(n) time, O(n) space",
            """
            def subarray_sum(nums, k):
                seen = {0: 1}
                running = 0
                found = 0
                for n in nums:
                    running += n
                    found += seen.get(running - k, 0)
                    seen[running] = seen.get(running, 0) + 1
                return found
            """,
        ),
        _p(
            128,
            "Longest Consecutive Sequence",
            "Medium",
            "Only start counting from a number with no left neighbour — each run is walked once.",
            "O(n) time, O(n) space",
            """
            def longest_consecutive(nums):
                pool = set(nums)
                best = 0
                for n in pool:
                    if n - 1 in pool:
                        continue
                    length = 1
                    while n + length in pool:
                        length += 1
                    if length > best:
                        best = length
                return best
            """,
        ),
        _p(
            36,
            "Valid Sudoku",
            "Medium",
            "Three sets per cell: its row, its column, and its box at (r // 3, c // 3).",
            "O(1) time, O(1) space",
            """
            def is_valid_sudoku(board):
                rows = {}
                cols = {}
                boxes = {}
                for r in range(9):
                    for c in range(9):
                        value = board[r][c]
                        if value == ".":
                            continue
                        box = (r // 3, c // 3)
                        if value in rows.setdefault(r, set()):
                            return False
                        if value in cols.setdefault(c, set()):
                            return False
                        if value in boxes.setdefault(box, set()):
                            return False
                        rows[r].add(value)
                        cols[c].add(value)
                        boxes[box].add(value)
                return True
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
        _p(
            26,
            "Remove Duplicates from Sorted Array",
            "Easy",
            "One pointer writes, the other reads — the writer only moves on a new value.",
            "O(n) time, O(1) space",
            """
            def remove_duplicates(nums):
                if not nums:
                    return 0
                write = 1
                for read in range(1, len(nums)):
                    if nums[read] != nums[write - 1]:
                        nums[write] = nums[read]
                        write += 1
                return write
            """,
        ),
        _p(
            283,
            "Move Zeroes",
            "Easy",
            "Same read/write pair: write every non-zero forward, then fill the tail.",
            "O(n) time, O(1) space",
            """
            def move_zeroes(nums):
                write = 0
                for read in range(len(nums)):
                    if nums[read] != 0:
                        nums[write] = nums[read]
                        write += 1
                for i in range(write, len(nums)):
                    nums[i] = 0
                return nums
            """,
        ),
        _p(
            42,
            "Trapping Rain Water",
            "Hard",
            "Water over a column is the smaller of the two tallest walls beside it, minus the column.",
            "O(n) time, O(1) space",
            """
            def trap(height):
                if not height:
                    return 0
                left, right = 0, len(height) - 1
                left_max, right_max = height[left], height[right]
                water = 0
                while left < right:
                    if left_max < right_max:
                        left += 1
                        left_max = max(left_max, height[left])
                        water += left_max - height[left]
                    else:
                        right -= 1
                        right_max = max(right_max, height[right])
                        water += right_max - height[right]
                return water
            """,
        ),
        _p(
            977,
            "Squares of a Sorted Array",
            "Easy",
            "The biggest square is at one end or the other, so fill the answer backwards.",
            "O(n) time, O(n) space",
            """
            def sorted_squares(nums):
                out = [0] * len(nums)
                left, right = 0, len(nums) - 1
                for slot in range(len(nums) - 1, -1, -1):
                    if abs(nums[left]) > abs(nums[right]):
                        out[slot] = nums[left] * nums[left]
                        left += 1
                    else:
                        out[slot] = nums[right] * nums[right]
                        right -= 1
                return out
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
        _p(
            643,
            "Maximum Average Subarray I",
            "Easy",
            "The window never changes size, so each step adds one number and drops one.",
            "O(n) time, O(1) space",
            """
            def find_max_average(nums, k):
                window = sum(nums[:k])
                best = window
                for i in range(k, len(nums)):
                    window += nums[i] - nums[i - k]
                    if window > best:
                        best = window
                return best / k
            """,
        ),
        _p(
            567,
            "Permutation in String",
            "Medium",
            "A fixed window whose letter counts match is a permutation — no sorting needed.",
            "O(n) time, O(1) space",
            """
            def check_inclusion(pattern, text):
                if len(pattern) > len(text):
                    return False
                need = {}
                for ch in pattern:
                    need[ch] = need.get(ch, 0) + 1
                window = {}
                for i, ch in enumerate(text):
                    window[ch] = window.get(ch, 0) + 1
                    if i >= len(pattern):
                        out = text[i - len(pattern)]
                        window[out] -= 1
                        if window[out] == 0:
                            del window[out]
                    if window == need:
                        return True
                return False
            """,
        ),
        _p(
            1004,
            "Max Consecutive Ones III",
            "Medium",
            "Grow while at most k zeros are inside; shrink from the left when a k+1th appears.",
            "O(n) time, O(1) space",
            """
            def longest_ones(nums, k):
                left = 0
                zeros = 0
                best = 0
                for right in range(len(nums)):
                    if nums[right] == 0:
                        zeros += 1
                    while zeros > k:
                        if nums[left] == 0:
                            zeros -= 1
                        left += 1
                    if right - left + 1 > best:
                        best = right - left + 1
                return best
            """,
        ),
        _p(
            76,
            "Minimum Window Substring",
            "Hard",
            "Count how many required letters are satisfied; shrink only while all of them are.",
            "O(n) time, O(1) space",
            """
            def min_window(text, pattern):
                if not pattern or not text:
                    return ""
                need = {}
                for ch in pattern:
                    need[ch] = need.get(ch, 0) + 1
                missing = len(need)
                window = {}
                best = ""
                left = 0
                for right, ch in enumerate(text):
                    window[ch] = window.get(ch, 0) + 1
                    if ch in need and window[ch] == need[ch]:
                        missing -= 1
                    while missing == 0:
                        if not best or right - left + 1 < len(best):
                            best = text[left:right + 1]
                        out = text[left]
                        window[out] -= 1
                        if out in need and window[out] < need[out]:
                            missing += 1
                        left += 1
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
        _p(
            682,
            "Baseball Game",
            "Easy",
            "Every operation only ever looks at the top of the stack, which is the whole idea.",
            "O(n) time, O(n) space",
            """
            def cal_points(operations):
                stack = []
                for op in operations:
                    if op == "C":
                        stack.pop()
                    elif op == "D":
                        stack.append(stack[-1] * 2)
                    elif op == "+":
                        stack.append(stack[-1] + stack[-2])
                    else:
                        stack.append(int(op))
                return sum(stack)
            """,
        ),
        _p(
            71,
            "Simplify Path",
            "Medium",
            "A '..' pops the directory before it, which is exactly what a stack is for.",
            "O(n) time, O(n) space",
            """
            def simplify_path(path):
                stack = []
                for part in path.split("/"):
                    if part == "" or part == ".":
                        continue
                    if part == "..":
                        if stack:
                            stack.pop()
                    else:
                        stack.append(part)
                return "/" + "/".join(stack)
            """,
        ),
        _p(
            84,
            "Largest Rectangle in Histogram",
            "Hard",
            "Keep bars increasing; a shorter one closes off every taller bar behind it.",
            "O(n) time, O(n) space",
            """
            def largest_rectangle_area(heights):
                stack = []
                best = 0
                for i, height in enumerate(heights + [0]):
                    start = i
                    while stack and stack[-1][1] > height:
                        left, tall = stack.pop()
                        if tall * (i - left) > best:
                            best = tall * (i - left)
                        start = left
                    stack.append((start, height))
                return best
            """,
        ),
        _p(
            394,
            "Decode String",
            "Medium",
            "Push the work in progress when a bracket opens, finish it when one closes.",
            "O(n) time, O(n) space",
            """
            def decode_string(encoded):
                stack = []
                current = ""
                count = 0
                for ch in encoded:
                    if ch.isdigit():
                        count = count * 10 + int(ch)
                    elif ch == "[":
                        stack.append((current, count))
                        current = ""
                        count = 0
                    elif ch == "]":
                        before, times = stack.pop()
                        current = before + current * times
                    else:
                        current += ch
                return current
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
        _p(
            876,
            "Middle of the Linked List",
            "Easy",
            "One pointer takes two steps per the other's one, so it ends at twice the distance.",
            "O(n) time, O(1) space",
            """
            def middle_node(head):
                slow = head
                fast = head
                while fast and fast.next:
                    slow = slow.next
                    fast = fast.next.next
                return slow
            """,
        ),
        _p(
            83,
            "Remove Duplicates from Sorted List",
            "Easy",
            "Sorted means duplicates are neighbours, so one pass and a skipped link does it.",
            "O(n) time, O(1) space",
            """
            def delete_duplicates(head):
                node = head
                while node and node.next:
                    if node.val == node.next.val:
                        node.next = node.next.next
                    else:
                        node = node.next
                return head
            """,
        ),
        _p(
            234,
            "Palindrome Linked List",
            "Easy",
            "Find the middle, reverse the second half, then walk the two halves together.",
            "O(n) time, O(1) space",
            """
            def is_palindrome_list(head):
                slow = head
                fast = head
                while fast and fast.next:
                    slow = slow.next
                    fast = fast.next.next
                second = None
                while slow:
                    nxt = slow.next
                    slow.next = second
                    second = slow
                    slow = nxt
                first = head
                while second:
                    if first.val != second.val:
                        return False
                    first = first.next
                    second = second.next
                return True
            """,
        ),
        _p(
            2,
            "Add Two Numbers",
            "Medium",
            "Long addition, digit by digit. The carry is the only thing you have to remember.",
            "O(n) time, O(n) space",
            """
            def add_two_numbers(first, second):
                head = ListNode()
                node = head
                carry = 0
                while first or second or carry:
                    total = carry
                    if first:
                        total += first.val
                        first = first.next
                    if second:
                        total += second.val
                        second = second.next
                    carry = total // 10
                    node.next = ListNode(total % 10)
                    node = node.next
                return head.next
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
        _p(
            278,
            "First Bad Version",
            "Easy",
            "Search for a boundary: keep the mid when it's bad, discard it when it isn't.",
            "O(log n) time, O(1) space",
            """
            def first_bad_version(n, is_bad):
                low, high = 1, n
                while low < high:
                    mid = (low + high) // 2
                    if is_bad(mid):
                        high = mid
                    else:
                        low = mid + 1
                return low
            """,
        ),
        _p(
            34,
            "Find First and Last Position of Element in Sorted Array",
            "Medium",
            "Two searches, not one: the same loop finds the left edge and then the right.",
            "O(log n) time, O(1) space",
            """
            def search_range(nums, target):
                def edge(first):
                    low, high = 0, len(nums) - 1
                    found = -1
                    while low <= high:
                        mid = (low + high) // 2
                        if nums[mid] == target:
                            found = mid
                            if first:
                                high = mid - 1
                            else:
                                low = mid + 1
                        elif nums[mid] < target:
                            low = mid + 1
                        else:
                            high = mid - 1
                    return found

                return [edge(True), edge(False)]
            """,
        ),
        _p(
            74,
            "Search a 2D Matrix",
            "Medium",
            "A sorted matrix is one sorted list folded up, so divide the index to unfold it.",
            "O(log(m * n)) time, O(1) space",
            """
            def search_matrix(matrix, target):
                if not matrix or not matrix[0]:
                    return False
                rows, cols = len(matrix), len(matrix[0])
                low, high = 0, rows * cols - 1
                while low <= high:
                    mid = (low + high) // 2
                    value = matrix[mid // cols][mid % cols]
                    if value == target:
                        return True
                    if value < target:
                        low = mid + 1
                    else:
                        high = mid - 1
                return False
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
        _p(
            100,
            "Same Tree",
            "Easy",
            "Two trees match when their roots match and both pairs of children do.",
            "O(n) time, O(h) space",
            """
            def is_same_tree(first, second):
                if not first and not second:
                    return True
                if not first or not second:
                    return False
                if first.val != second.val:
                    return False
                return is_same_tree(first.left, second.left) and is_same_tree(
                    first.right, second.right
                )
            """,
        ),
        _p(
            101,
            "Symmetric Tree",
            "Easy",
            "A mirror compares left against right — the recursion crosses over.",
            "O(n) time, O(h) space",
            """
            def is_symmetric(root):
                def mirror(left, right):
                    if not left and not right:
                        return True
                    if not left or not right:
                        return False
                    if left.val != right.val:
                        return False
                    return mirror(left.left, right.right) and mirror(
                        left.right, right.left
                    )

                return mirror(root, root)
            """,
        ),
        _p(
            236,
            "Lowest Common Ancestor of a Binary Tree",
            "Medium",
            "A node whose two sides each found something is the meeting point.",
            "O(n) time, O(h) space",
            """
            def lowest_common_ancestor(root, p, q):
                if not root or root is p or root is q:
                    return root
                left = lowest_common_ancestor(root.left, p, q)
                right = lowest_common_ancestor(root.right, p, q)
                if left and right:
                    return root
                return left or right
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
        _p(
            111,
            "Minimum Depth of Binary Tree",
            "Easy",
            "BFS stops at the first leaf it meets — DFS would walk the whole tree first.",
            "O(n) time, O(n) space",
            """
            def min_depth(root):
                if not root:
                    return 0
                queue = deque([root])
                depth = 1
                while queue:
                    for _ in range(len(queue)):
                        node = queue.popleft()
                        if not node.left and not node.right:
                            return depth
                        if node.left:
                            queue.append(node.left)
                        if node.right:
                            queue.append(node.right)
                    depth += 1
                return depth
            """,
        ),
        _p(
            637,
            "Average of Levels in Binary Tree",
            "Easy",
            "One row at a time, so the divisor is just that row's length.",
            "O(n) time, O(n) space",
            """
            def average_of_levels(root):
                if not root:
                    return []
                averages = []
                queue = deque([root])
                while queue:
                    size = len(queue)
                    total = 0
                    for _ in range(size):
                        node = queue.popleft()
                        total += node.val
                        if node.left:
                            queue.append(node.left)
                        if node.right:
                            queue.append(node.right)
                    averages.append(total / size)
                return averages
            """,
        ),
        _p(
            515,
            "Find Largest Value in Each Tree Row",
            "Medium",
            "Same row walk as the average — swap the running total for a running max.",
            "O(n) time, O(n) space",
            """
            def largest_values(root):
                if not root:
                    return []
                largest = []
                queue = deque([root])
                while queue:
                    best = None
                    for _ in range(len(queue)):
                        node = queue.popleft()
                        if best is None or node.val > best:
                            best = node.val
                        if node.left:
                            queue.append(node.left)
                        if node.right:
                            queue.append(node.right)
                    largest.append(best)
                return largest
            """,
        ),
        _p(
            1161,
            "Maximum Level Sum of a Binary Tree",
            "Medium",
            "Number the levels as you go and keep the best — ties go to the shallower one.",
            "O(n) time, O(n) space",
            """
            def max_level_sum(root):
                if not root:
                    return 0
                queue = deque([root])
                level = 0
                best_level = 1
                best_sum = None
                while queue:
                    level += 1
                    total = 0
                    for _ in range(len(queue)):
                        node = queue.popleft()
                        total += node.val
                        if node.left:
                            queue.append(node.left)
                        if node.right:
                            queue.append(node.right)
                    if best_sum is None or total > best_sum:
                        best_sum = total
                        best_level = level
                return best_level
            """,
        ),
        _p(
            662,
            "Maximum Width of Binary Tree",
            "Medium",
            "Queue the heap index with each node; a row's width is last minus first plus one.",
            "O(n) time, O(n) space",
            """
            def width_of_binary_tree(root):
                if not root:
                    return 0
                widest = 0
                queue = deque([(root, 0)])
                while queue:
                    size = len(queue)
                    _, first = queue[0]
                    last = first
                    for _ in range(size):
                        node, index = queue.popleft()
                        last = index
                        if node.left:
                            queue.append((node.left, index * 2))
                        if node.right:
                            queue.append((node.right, index * 2 + 1))
                    width = last - first + 1
                    if width > widest:
                        widest = width
                return widest
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
        _p(
            695,
            "Max Area of Island",
            "Medium",
            "Same flood fill, but the walk returns a size instead of just marking cells.",
            "O(m * n) time, O(m * n) space",
            """
            def max_area_of_island(grid):
                if not grid:
                    return 0
                rows, cols = len(grid), len(grid[0])

                def fill(r, c):
                    if r < 0 or c < 0 or r >= rows or c >= cols:
                        return 0
                    if grid[r][c] != 1:
                        return 0
                    grid[r][c] = 0
                    return 1 + fill(r + 1, c) + fill(r - 1, c) + fill(
                        r, c + 1
                    ) + fill(r, c - 1)

                best = 0
                for r in range(rows):
                    for c in range(cols):
                        area = fill(r, c)
                        if area > best:
                            best = area
                return best
            """,
        ),
        _p(
            547,
            "Number of Provinces",
            "Medium",
            "Every walk that starts somewhere unvisited is one more connected group.",
            "O(n * n) time, O(n) space",
            """
            def find_circle_num(is_connected):
                n = len(is_connected)
                seen = set()

                def visit(city):
                    seen.add(city)
                    for other in range(n):
                        if is_connected[city][other] and other not in seen:
                            visit(other)

                groups = 0
                for city in range(n):
                    if city not in seen:
                        visit(city)
                        groups += 1
                return groups
            """,
        ),
        _p(
            542,
            "01 Matrix",
            "Medium",
            "Start the queue from every zero at once, and the first visit is the nearest one.",
            "O(m * n) time, O(m * n) space",
            """
            def update_matrix(mat):
                rows, cols = len(mat), len(mat[0])
                out = [[-1] * cols for _ in range(rows)]
                queue = deque()
                for r in range(rows):
                    for c in range(cols):
                        if mat[r][c] == 0:
                            out[r][c] = 0
                            queue.append((r, c))
                while queue:
                    r, c = queue.popleft()
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and out[nr][nc] == -1:
                            out[nr][nc] = out[r][c] + 1
                            queue.append((nr, nc))
                return out
            """,
        ),
        _p(
            417,
            "Pacific Atlantic Water Flow",
            "Medium",
            "Walk uphill from each ocean instead of downhill from each cell; the answer is the overlap.",
            "O(m * n) time, O(m * n) space",
            """
            def pacific_atlantic(heights):
                if not heights:
                    return []
                rows, cols = len(heights), len(heights[0])
                pacific = set()
                atlantic = set()

                def climb(r, c, seen):
                    seen.add((r, c))
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if (nr, nc) not in seen and heights[nr][nc] >= heights[r][c]:
                                climb(nr, nc, seen)

                for c in range(cols):
                    climb(0, c, pacific)
                    climb(rows - 1, c, atlantic)
                for r in range(rows):
                    climb(r, 0, pacific)
                    climb(r, cols - 1, atlantic)
                return [list(cell) for cell in sorted(pacific & atlantic)]
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
        _p(
            77,
            "Combinations",
            "Medium",
            "Only ever pick numbers after the last one taken, so no pair is built twice.",
            "O(k * C(n, k)) time, O(k) space",
            """
            def combine(n, k):
                out = []
                picked = []

                def walk(start):
                    if len(picked) == k:
                        out.append(list(picked))
                        return
                    for value in range(start, n + 1):
                        picked.append(value)
                        walk(value + 1)
                        picked.pop()

                walk(1)
                return out
            """,
        ),
        _p(
            17,
            "Letter Combinations of a Phone Number",
            "Medium",
            "One digit is one level of the tree, and its letters are that level's branches.",
            "O(4 ** n) time, O(n) space",
            """
            def letter_combinations(digits):
                if not digits:
                    return []
                keys = {
                    "2": "abc",
                    "3": "def",
                    "4": "ghi",
                    "5": "jkl",
                    "6": "mno",
                    "7": "pqrs",
                    "8": "tuv",
                    "9": "wxyz",
                }
                out = []

                def walk(index, built):
                    if index == len(digits):
                        out.append(built)
                        return
                    for letter in keys[digits[index]]:
                        walk(index + 1, built + letter)

                walk(0, "")
                return out
            """,
        ),
        _p(
            131,
            "Palindrome Partitioning",
            "Medium",
            "Cut after every position whose prefix reads the same both ways, then solve the rest.",
            "O(n * 2 ** n) time, O(n) space",
            """
            def partition(text):
                out = []
                built = []

                def walk(start):
                    if start == len(text):
                        out.append(list(built))
                        return
                    for end in range(start + 1, len(text) + 1):
                        piece = text[start:end]
                        if piece == piece[::-1]:
                            built.append(piece)
                            walk(end)
                            built.pop()

                walk(0)
                return out
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
        _p(
            1046,
            "Last Stone Weight",
            "Easy",
            "Python's heap is a min-heap — push negatives to pop the biggest first.",
            "O(n log n) time, O(n) space",
            """
            def last_stone_weight(stones):
                heap = [-s for s in stones]
                heapq.heapify(heap)
                while len(heap) > 1:
                    first = -heapq.heappop(heap)
                    second = -heapq.heappop(heap)
                    if first != second:
                        heapq.heappush(heap, -(first - second))
                return -heap[0] if heap else 0
            """,
        ),
        _p(
            692,
            "Top K Frequent Words",
            "Medium",
            "Key on (-count, word): the heap then breaks ties alphabetically for free.",
            "O(n + k log n) time, O(n) space",
            """
            def top_k_frequent_words(words, k):
                counts = {}
                for word in words:
                    counts[word] = counts.get(word, 0) + 1
                heap = [(-count, word) for word, count in counts.items()]
                heapq.heapify(heap)
                return [heapq.heappop(heap)[1] for _ in range(k)]
            """,
        ),
        _p(
            451,
            "Sort Characters By Frequency",
            "Medium",
            "Count, then pop the heap most-frequent-first and repeat each character.",
            "O(n log n) time, O(n) space",
            """
            def frequency_sort(s):
                counts = {}
                for ch in s:
                    counts[ch] = counts.get(ch, 0) + 1
                heap = [(-count, ch) for ch, count in counts.items()]
                heapq.heapify(heap)
                out = []
                while heap:
                    count, ch = heapq.heappop(heap)
                    out.append(ch * -count)
                return "".join(out)
            """,
        ),
        _p(
            378,
            "Kth Smallest Element in a Sorted Matrix",
            "Medium",
            "Seed the heap with each row's head, then keep pulling the smallest and refilling from its row.",
            "O(k log n) time, O(n) space",
            """
            def kth_smallest(matrix, k):
                heap = []
                for row in range(min(len(matrix), k)):
                    heapq.heappush(heap, (matrix[row][0], row, 0))
                value = 0
                for _ in range(k):
                    value, row, col = heapq.heappop(heap)
                    if col + 1 < len(matrix[row]):
                        heapq.heappush(heap, (matrix[row][col + 1], row, col + 1))
                return value
            """,
        ),
        _p(
            767,
            "Reorganize String",
            "Medium",
            "Always place the most common letter left, holding the one you just used aside for a turn.",
            "O(n log n) time, O(n) space",
            """
            def reorganize_string(s):
                counts = {}
                for ch in s:
                    counts[ch] = counts.get(ch, 0) + 1
                heap = [(-count, ch) for ch, count in counts.items()]
                heapq.heapify(heap)
                out = []
                held = None
                while heap:
                    count, ch = heapq.heappop(heap)
                    out.append(ch)
                    if held:
                        heapq.heappush(heap, held)
                    count += 1
                    held = (count, ch) if count else None
                return "".join(out) if len(out) == len(s) else ""
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
        _p(
            802,
            "Find Eventual Safe States",
            "Medium",
            "Reverse every edge, then peel from the terminal nodes — whatever drains is safe.",
            "O(v + e) time, O(v + e) space",
            """
            def eventual_safe_nodes(graph):
                n = len(graph)
                reverse = {i: [] for i in range(n)}
                outdegree = [0] * n
                for node, edges in enumerate(graph):
                    outdegree[node] = len(edges)
                    for nxt in edges:
                        reverse[nxt].append(node)
                queue = deque([i for i in range(n) if outdegree[i] == 0])
                safe = []
                while queue:
                    node = queue.popleft()
                    safe.append(node)
                    for prev in reverse[node]:
                        outdegree[prev] -= 1
                        if outdegree[prev] == 0:
                            queue.append(prev)
                safe.sort()
                return safe
            """,
        ),
        _p(
            1462,
            "Course Schedule IV",
            "Medium",
            "Peel in order, and let each course inherit the prerequisite set of everything before it.",
            "O(v * e) time, O(v * v) space",
            """
            def check_if_prerequisite(num_courses, prerequisites, queries):
                graph = {i: [] for i in range(num_courses)}
                indegree = [0] * num_courses
                for prereq, course in prerequisites:
                    graph[prereq].append(course)
                    indegree[course] += 1
                needs = [set() for _ in range(num_courses)]
                queue = deque([i for i in range(num_courses) if indegree[i] == 0])
                while queue:
                    node = queue.popleft()
                    for nxt in graph[node]:
                        needs[nxt].add(node)
                        needs[nxt] |= needs[node]
                        indegree[nxt] -= 1
                        if indegree[nxt] == 0:
                            queue.append(nxt)
                return [prereq in needs[course] for prereq, course in queries]
            """,
        ),
        _p(
            2115,
            "Find All Possible Recipes from Given Supplies",
            "Medium",
            "Ingredients are prerequisites: a recipe unlocks once its indegree of missing items hits zero.",
            "O(v + e) time, O(v + e) space",
            """
            def find_all_recipes(recipes, ingredients, supplies):
                graph = {}
                indegree = {recipe: 0 for recipe in recipes}
                for recipe, needed in zip(recipes, ingredients):
                    for item in needed:
                        graph.setdefault(item, []).append(recipe)
                        indegree[recipe] += 1
                queue = deque(supplies)
                made = []
                while queue:
                    item = queue.popleft()
                    for recipe in graph.get(item, []):
                        indegree[recipe] -= 1
                        if indegree[recipe] == 0:
                            made.append(recipe)
                            queue.append(recipe)
                return made
            """,
        ),
        _p(
            1136,
            "Parallel Courses",
            "Medium",
            "Every drained layer of the queue is one semester — count the layers, not the courses.",
            "O(v + e) time, O(v + e) space",
            """
            def minimum_semesters(n, relations):
                graph = {i: [] for i in range(1, n + 1)}
                indegree = {i: 0 for i in range(1, n + 1)}
                for prereq, course in relations:
                    graph[prereq].append(course)
                    indegree[course] += 1
                queue = deque([i for i in range(1, n + 1) if indegree[i] == 0])
                studied = 0
                semesters = 0
                while queue:
                    semesters += 1
                    for _ in range(len(queue)):
                        node = queue.popleft()
                        studied += 1
                        for nxt in graph[node]:
                            indegree[nxt] -= 1
                            if indegree[nxt] == 0:
                                queue.append(nxt)
                return semesters if studied == n else -1
            """,
        ),
        _p(
            269,
            "Alien Dictionary",
            "Hard",
            "Adjacent words give one letter order each; the first difference is the only edge they prove.",
            "O(c) time, O(1) space",
            """
            def alien_order(words):
                graph = {ch: set() for word in words for ch in word}
                indegree = {ch: 0 for ch in graph}
                for first, second in zip(words, words[1:]):
                    for a, b in zip(first, second):
                        if a != b:
                            if b not in graph[a]:
                                graph[a].add(b)
                                indegree[b] += 1
                            break
                    else:
                        if len(first) > len(second):
                            return ""
                queue = deque([ch for ch in indegree if indegree[ch] == 0])
                order = []
                while queue:
                    ch = queue.popleft()
                    order.append(ch)
                    for nxt in graph[ch]:
                        indegree[nxt] -= 1
                        if indegree[nxt] == 0:
                            queue.append(nxt)
                return "".join(order) if len(order) == len(indegree) else ""
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
        _p(
            746,
            "Min Cost Climbing Stairs",
            "Easy",
            "The cost of a step is its own plus the cheaper of the two ways off it.",
            "O(n) time, O(1) space",
            """
            def min_cost_climbing_stairs(cost):
                one, two = 0, 0
                for i in range(2, len(cost) + 1):
                    one, two = min(one + cost[i - 1], two + cost[i - 2]), one
                return one
            """,
        ),
        _p(
            1143,
            "Longest Common Subsequence",
            "Medium",
            "Matching letters extend the diagonal; otherwise take the better of dropping one.",
            "O(m * n) time, O(m * n) space",
            """
            def longest_common_subsequence(first, second):
                grid = [[0] * (len(second) + 1) for _ in range(len(first) + 1)]
                for i in range(len(first) - 1, -1, -1):
                    for j in range(len(second) - 1, -1, -1):
                        if first[i] == second[j]:
                            grid[i][j] = 1 + grid[i + 1][j + 1]
                        else:
                            grid[i][j] = max(grid[i + 1][j], grid[i][j + 1])
                return grid[0][0]
            """,
        ),
        _p(
            139,
            "Word Break",
            "Medium",
            "A position is reachable when some word ends there and its start was reachable too.",
            "O(n * n * w) time, O(n) space",
            """
            def word_break(text, words):
                reachable = [False] * (len(text) + 1)
                reachable[0] = True
                for end in range(1, len(text) + 1):
                    for word in words:
                        start = end - len(word)
                        if start >= 0 and reachable[start]:
                            if text[start:end] == word:
                                reachable[end] = True
                                break
                return reachable[len(text)]
            """,
        ),
        _p(
            152,
            "Maximum Product Subarray",
            "Medium",
            "Track the smallest product too — a negative turns the worst into the best.",
            "O(n) time, O(1) space",
            """
            def max_product(nums):
                best = nums[0]
                high, low = nums[0], nums[0]
                for n in nums[1:]:
                    options = (n, high * n, low * n)
                    high, low = max(options), min(options)
                    if high > best:
                        best = high
                return best
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
