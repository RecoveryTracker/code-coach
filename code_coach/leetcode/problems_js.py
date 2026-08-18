"""
The same LeetCode patterns, written in JavaScript.

Mirrors `problems.py` problem for problem, so switching language keeps your
place. Solutions are plain top-level functions that run under `node`, using
`Map` and `Set` rather than bare objects — that's what these algorithms
actually want, and it's what an interviewer expects to see.
"""

from __future__ import annotations

from code_coach.leetcode.js_common import _p
from code_coach.leetcode.problems import Pattern

# ── 1. Hash maps ────────────────────────────────────────────

_HASH_MAP = Pattern(
    id="lc-hashmap",
    name="Hash Maps",
    order=1,
    blurb="Trade memory for time: remember what you've seen.",
    tell="You catch yourself wanting a nested loop to ask 'have I seen this?'",
    problems=(
        _p(
            1, "Two Sum", "Easy",
            "Store each number's index as you pass it, then look up the complement.",
            "O(n) time, O(n) space",
            """
            function twoSum(nums, target) {
              const seen = new Map();
              for (let i = 0; i < nums.length; i++) {
                const need = target - nums[i];
                if (seen.has(need)) return [seen.get(need), i];
                seen.set(nums[i], i);
              }
              return [];
            }
            """,
        ),
        _p(
            217, "Contains Duplicate", "Easy",
            "A Set answers 'seen before?' in constant time.",
            "O(n) time, O(n) space",
            """
            function containsDuplicate(nums) {
              const seen = new Set();
              for (const n of nums) {
                if (seen.has(n)) return true;
                seen.add(n);
              }
              return false;
            }
            """,
        ),
        _p(
            242, "Valid Anagram", "Easy",
            "Count letters in one word, spend them on the other.",
            "O(n) time, O(1) space",
            """
            function isAnagram(s, t) {
              if (s.length !== t.length) return false;
              const counts = new Map();
              for (const ch of s) {
                counts.set(ch, (counts.get(ch) || 0) + 1);
              }
              for (const ch of t) {
                if (!counts.get(ch)) return false;
                counts.set(ch, counts.get(ch) - 1);
              }
              return true;
            }
            """,
        ),
        _p(
            49, "Group Anagrams", "Medium",
            "Sorted letters make a key that every anagram shares.",
            "O(n·k log k) time, O(n·k) space",
            """
            function groupAnagrams(strs) {
              const groups = new Map();
              for (const word of strs) {
                const key = word.split('').sort().join('');
                if (!groups.has(key)) groups.set(key, []);
                groups.get(key).push(word);
              }
              return [...groups.values()];
            }
            """,
        ),
    ),
)


# ── 2. Two pointers ─────────────────────────────────────────

_TWO_POINTERS = Pattern(
    id="lc-two-pointers",
    name="Two Pointers",
    order=2,
    blurb="Walk two indexes toward each other, or at different speeds.",
    tell="The list is sorted, or you care about pairs from both ends.",
    problems=(
        _p(
            125, "Valid Palindrome", "Easy",
            "Skip non-letters from both ends and compare inward.",
            "O(n) time, O(1) space",
            """
            function isPalindrome(s) {
              const ok = (c) => /[a-z0-9]/i.test(c);
              let left = 0;
              let right = s.length - 1;
              while (left < right) {
                while (left < right && !ok(s[left])) left++;
                while (left < right && !ok(s[right])) right--;
                if (s[left].toLowerCase() !== s[right].toLowerCase()) return false;
                left++;
                right--;
              }
              return true;
            }
            """,
        ),
        _p(
            167, "Two Sum II (sorted)", "Medium",
            "Sorted input means a too-small sum moves left, too-big moves right.",
            "O(n) time, O(1) space",
            """
            function twoSumSorted(numbers, target) {
              let left = 0;
              let right = numbers.length - 1;
              while (left < right) {
                const total = numbers[left] + numbers[right];
                if (total === target) return [left + 1, right + 1];
                if (total < target) {
                  left++;
                } else {
                  right--;
                }
              }
              return [];
            }
            """,
        ),
        _p(
            11, "Container With Most Water", "Medium",
            "Move whichever wall is shorter — it's the one limiting you.",
            "O(n) time, O(1) space",
            """
            function maxArea(height) {
              let left = 0;
              let right = height.length - 1;
              let best = 0;
              while (left < right) {
                const shorter = Math.min(height[left], height[right]);
                best = Math.max(best, shorter * (right - left));
                if (height[left] < height[right]) {
                  left++;
                } else {
                  right--;
                }
              }
              return best;
            }
            """,
        ),
        _p(
            15, "3Sum", "Medium",
            "Fix one number, then it's Two Sum on the rest — sort first.",
            "O(n²) time, O(1) extra space",
            """
            function threeSum(nums) {
              nums.sort((a, b) => a - b);
              const out = [];
              for (let i = 0; i < nums.length - 2; i++) {
                if (i > 0 && nums[i] === nums[i - 1]) continue;
                let left = i + 1;
                let right = nums.length - 1;
                while (left < right) {
                  const total = nums[i] + nums[left] + nums[right];
                  if (total < 0) {
                    left++;
                  } else if (total > 0) {
                    right--;
                  } else {
                    out.push([nums[i], nums[left], nums[right]]);
                    while (left < right && nums[left] === nums[left + 1]) left++;
                    while (left < right && nums[right] === nums[right - 1]) right--;
                    left++;
                    right--;
                  }
                }
              }
              return out;
            }
            """,
        ),
    ),
)


# ── 3. Sliding window ───────────────────────────────────────

_SLIDING_WINDOW = Pattern(
    id="lc-sliding-window",
    name="Sliding Window",
    order=3,
    blurb="Grow a window on the right, shrink it from the left.",
    tell="You want the best contiguous run of something.",
    problems=(
        _p(
            121, "Best Time to Buy and Sell Stock", "Easy",
            "Track the cheapest price so far; every day is a possible sell.",
            "O(n) time, O(1) space",
            """
            function maxProfit(prices) {
              let cheapest = Infinity;
              let best = 0;
              for (const price of prices) {
                cheapest = Math.min(cheapest, price);
                best = Math.max(best, price - cheapest);
              }
              return best;
            }
            """,
        ),
        _p(
            3, "Longest Substring Without Repeating Characters", "Medium",
            "When a repeat appears, drag the left edge past its last position.",
            "O(n) time, O(k) space",
            """
            function lengthOfLongestSubstring(s) {
              const lastSeen = new Map();
              let left = 0;
              let best = 0;
              for (let right = 0; right < s.length; right++) {
                const ch = s[right];
                if (lastSeen.has(ch) && lastSeen.get(ch) >= left) {
                  left = lastSeen.get(ch) + 1;
                }
                lastSeen.set(ch, right);
                best = Math.max(best, right - left + 1);
              }
              return best;
            }
            """,
        ),
        _p(
            209, "Minimum Size Subarray Sum", "Medium",
            "Grow until the sum is enough, then shrink while it still is.",
            "O(n) time, O(1) space",
            """
            function minSubArrayLen(target, nums) {
              let left = 0;
              let total = 0;
              let best = Infinity;
              for (let right = 0; right < nums.length; right++) {
                total += nums[right];
                while (total >= target) {
                  best = Math.min(best, right - left + 1);
                  total -= nums[left];
                  left++;
                }
              }
              return best === Infinity ? 0 : best;
            }
            """,
        ),
        _p(
            424, "Longest Repeating Character Replacement", "Medium",
            "A window is valid while its size minus its commonest letter is ≤ k.",
            "O(n) time, O(1) space",
            """
            function characterReplacement(s, k) {
              const counts = new Map();
              let left = 0;
              let mostCommon = 0;
              let best = 0;
              for (let right = 0; right < s.length; right++) {
                const ch = s[right];
                counts.set(ch, (counts.get(ch) || 0) + 1);
                mostCommon = Math.max(mostCommon, counts.get(ch));
                while (right - left + 1 - mostCommon > k) {
                  counts.set(s[left], counts.get(s[left]) - 1);
                  left++;
                }
                best = Math.max(best, right - left + 1);
              }
              return best;
            }
            """,
        ),
    ),
)


# ── 4. Stacks ───────────────────────────────────────────────

_STACK = Pattern(
    id="lc-stack",
    name="Stacks",
    order=4,
    blurb="Remember what's still open, and close it in reverse order.",
    tell="Nesting, matching pairs, or 'the next bigger thing'.",
    problems=(
        _p(
            20, "Valid Parentheses", "Easy",
            "Push openers; every closer must match the most recent one.",
            "O(n) time, O(n) space",
            """
            function isValid(s) {
              const pairs = { ')': '(', ']': '[', '}': '{' };
              const stack = [];
              for (const ch of s) {
                if (ch === '(' || ch === '[' || ch === '{') {
                  stack.push(ch);
                } else if (pairs[ch]) {
                  if (stack.pop() !== pairs[ch]) return false;
                }
              }
              return stack.length === 0;
            }
            """,
        ),
        _p(
            155, "Min Stack", "Medium",
            "Store the running minimum beside each value, so it pops with it.",
            "O(1) per operation",
            """
            class MinStack {
              constructor() {
                this.items = [];
              }

              push(val) {
                const smallest = this.items.length
                  ? Math.min(val, this.getMin())
                  : val;
                this.items.push([val, smallest]);
              }

              pop() {
                this.items.pop();
              }

              top() {
                return this.items[this.items.length - 1][0];
              }

              getMin() {
                return this.items[this.items.length - 1][1];
              }
            }
            """,
        ),
        _p(
            150, "Evaluate Reverse Polish Notation", "Medium",
            "Numbers wait on the stack until an operator claims the last two.",
            "O(n) time, O(n) space",
            """
            function evalRPN(tokens) {
              const stack = [];
              for (const token of tokens) {
                if (token === '+' || token === '-' || token === '*' || token === '/') {
                  const b = stack.pop();
                  const a = stack.pop();
                  if (token === '+') stack.push(a + b);
                  if (token === '-') stack.push(a - b);
                  if (token === '*') stack.push(a * b);
                  if (token === '/') stack.push(Math.trunc(a / b));
                } else {
                  stack.push(Number(token));
                }
              }
              return stack.pop();
            }
            """,
        ),
        _p(
            739, "Daily Temperatures", "Medium",
            "Keep indexes waiting for a warmer day; pop them when it arrives.",
            "O(n) time, O(n) space",
            """
            function dailyTemperatures(temperatures) {
              const answer = new Array(temperatures.length).fill(0);
              const stack = [];
              for (let i = 0; i < temperatures.length; i++) {
                while (
                  stack.length &&
                  temperatures[i] > temperatures[stack[stack.length - 1]]
                ) {
                  const day = stack.pop();
                  answer[day] = i - day;
                }
                stack.push(i);
              }
              return answer;
            }
            """,
        ),
    ),
)


from code_coach.leetcode.problems_js2 import (  # noqa: E402
    _BACKTRACKING,
    _BINARY_SEARCH,
    _DP,
    _GRAPH,
    _HEAP,
    _LINKED_LIST,
    _TOPOLOGICAL,
    _TREE_BFS,
    _TREE_DFS,
)

PATTERNS: tuple[Pattern, ...] = (
    _HASH_MAP,
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
