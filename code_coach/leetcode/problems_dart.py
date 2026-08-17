"""
The same LeetCode patterns, written in Dart.

Mirrors `problems.py` problem for problem, so switching language keeps your
place in the curriculum. The algorithms are identical; what changes is the
idiom — `Map` and `Set` instead of dict and set, `List<int>` instead of list,
null-safety `!` where Dart needs proof a lookup succeeded.

Every solution is a plain top-level function that runs under `dart run`, with
lowerCamelCase names because that is Dart's convention and the muscle memory
should build correct Dart habits.
"""

from __future__ import annotations

from code_coach.leetcode.dart_common import _p
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
            List<int> twoSum(List<int> nums, int target) {
              final seen = <int, int>{};
              for (var i = 0; i < nums.length; i++) {
                final need = target - nums[i];
                if (seen.containsKey(need)) return [seen[need]!, i];
                seen[nums[i]] = i;
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
            bool containsDuplicate(List<int> nums) {
              final seen = <int>{};
              for (final n in nums) {
                if (seen.contains(n)) return true;
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
            bool isAnagram(String s, String t) {
              if (s.length != t.length) return false;
              final counts = <String, int>{};
              for (final ch in s.split('')) {
                counts[ch] = (counts[ch] ?? 0) + 1;
              }
              for (final ch in t.split('')) {
                if ((counts[ch] ?? 0) == 0) return false;
                counts[ch] = counts[ch]! - 1;
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
            List<List<String>> groupAnagrams(List<String> strs) {
              final groups = <String, List<String>>{};
              for (final word in strs) {
                final letters = word.split('')..sort();
                final key = letters.join();
                groups.putIfAbsent(key, () => []).add(word);
              }
              return groups.values.toList();
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
            bool isPalindrome(String s) {
              var left = 0;
              var right = s.length - 1;
              bool alnum(String c) => RegExp(r'[a-zA-Z0-9]').hasMatch(c);
              while (left < right) {
                while (left < right && !alnum(s[left])) left++;
                while (left < right && !alnum(s[right])) right--;
                if (s[left].toLowerCase() != s[right].toLowerCase()) return false;
                left++;
                right--;
              }
              return true;
            }
            """,
        ),
        _p(
            167, "Two Sum II (Sorted)", "Medium",
            "Sorted input means a too-small sum moves left, too-big moves right.",
            "O(n) time, O(1) space",
            """
            List<int> twoSumSorted(List<int> numbers, int target) {
              var left = 0;
              var right = numbers.length - 1;
              while (left < right) {
                final total = numbers[left] + numbers[right];
                if (total == target) return [left + 1, right + 1];
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
            int maxArea(List<int> height) {
              var left = 0;
              var right = height.length - 1;
              var best = 0;
              while (left < right) {
                final shorter = height[left] < height[right] ? height[left] : height[right];
                final area = shorter * (right - left);
                if (area > best) best = area;
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
            List<List<int>> threeSum(List<int> nums) {
              nums.sort();
              final out = <List<int>>[];
              for (var i = 0; i < nums.length - 2; i++) {
                if (i > 0 && nums[i] == nums[i - 1]) continue;
                var left = i + 1;
                var right = nums.length - 1;
                while (left < right) {
                  final total = nums[i] + nums[left] + nums[right];
                  if (total < 0) {
                    left++;
                  } else if (total > 0) {
                    right--;
                  } else {
                    out.add([nums[i], nums[left], nums[right]]);
                    while (left < right && nums[left] == nums[left + 1]) left++;
                    while (left < right && nums[right] == nums[right - 1]) right--;
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
            int maxProfit(List<int> prices) {
              var cheapest = prices.isEmpty ? 0 : prices[0];
              var best = 0;
              for (final price in prices) {
                if (price < cheapest) cheapest = price;
                final profit = price - cheapest;
                if (profit > best) best = profit;
              }
              return best;
            }
            """,
        ),
        _p(
            3, "Longest Substring Without Repeating", "Medium",
            "When a repeat appears, drag the left edge past its last position.",
            "O(n) time, O(k) space",
            """
            int lengthOfLongestSubstring(String s) {
              final lastSeen = <String, int>{};
              var left = 0;
              var best = 0;
              for (var right = 0; right < s.length; right++) {
                final ch = s[right];
                final seenAt = lastSeen[ch];
                if (seenAt != null && seenAt >= left) left = seenAt + 1;
                lastSeen[ch] = right;
                final width = right - left + 1;
                if (width > best) best = width;
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
            int minSubArrayLen(int target, List<int> nums) {
              var left = 0;
              var total = 0;
              var best = nums.length + 1;
              for (var right = 0; right < nums.length; right++) {
                total += nums[right];
                while (total >= target) {
                  final width = right - left + 1;
                  if (width < best) best = width;
                  total -= nums[left];
                  left++;
                }
              }
              return best == nums.length + 1 ? 0 : best;
            }
            """,
        ),
        _p(
            424, "Longest Repeating Character Replacement", "Medium",
            "A window is valid while its size minus its commonest letter is ≤ k.",
            "O(n) time, O(1) space",
            """
            int characterReplacement(String s, int k) {
              final counts = <String, int>{};
              var left = 0;
              var best = 0;
              var mostCommon = 0;
              for (var right = 0; right < s.length; right++) {
                final ch = s[right];
                counts[ch] = (counts[ch] ?? 0) + 1;
                if (counts[ch]! > mostCommon) mostCommon = counts[ch]!;
                while (right - left + 1 - mostCommon > k) {
                  counts[s[left]] = counts[s[left]]! - 1;
                  left++;
                }
                final width = right - left + 1;
                if (width > best) best = width;
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
            bool isValid(String s) {
              final pairs = {')': '(', ']': '[', '}': '{'};
              final stack = <String>[];
              for (final ch in s.split('')) {
                if (pairs.containsValue(ch)) {
                  stack.add(ch);
                } else if (pairs.containsKey(ch)) {
                  if (stack.isEmpty || stack.removeLast() != pairs[ch]) return false;
                }
              }
              return stack.isEmpty;
            }
            """,
        ),
        _p(
            155, "Min Stack", "Medium",
            "Store the running minimum beside each value, so it pops with it.",
            "O(1) per operation",
            """
            class MinStack {
              final List<List<int>> _items = [];

              void push(int val) {
                final smallest = _items.isEmpty || val < _items.last[1] ? val : _items.last[1];
                _items.add([val, smallest]);
              }

              void pop() => _items.removeLast();

              int top() => _items.last[0];

              int getMin() => _items.last[1];
            }
            """,
        ),
        _p(
            150, "Evaluate Reverse Polish Notation", "Medium",
            "Numbers wait on the stack until an operator claims the last two.",
            "O(n) time, O(n) space",
            """
            int evalRPN(List<String> tokens) {
              final stack = <int>[];
              for (final token in tokens) {
                if (token == '+' || token == '-' || token == '*' || token == '/') {
                  final b = stack.removeLast();
                  final a = stack.removeLast();
                  if (token == '+') stack.add(a + b);
                  if (token == '-') stack.add(a - b);
                  if (token == '*') stack.add(a * b);
                  if (token == '/') stack.add(a ~/ b);
                } else {
                  stack.add(int.parse(token));
                }
              }
              return stack.last;
            }
            """,
        ),
        _p(
            739, "Daily Temperatures", "Medium",
            "Keep indexes waiting for a warmer day; pop them when it arrives.",
            "O(n) time, O(n) space",
            """
            List<int> dailyTemperatures(List<int> temperatures) {
              final answer = List<int>.filled(temperatures.length, 0);
              final stack = <int>[];
              for (var i = 0; i < temperatures.length; i++) {
                while (stack.isNotEmpty && temperatures[i] > temperatures[stack.last]) {
                  final day = stack.removeLast();
                  answer[day] = i - day;
                }
                stack.add(i);
              }
              return answer;
            }
            """,
        ),
    ),
)


# The rest of the patterns are added in problems_dart_part2 to keep each file
# a readable length; PATTERNS below stitches them together.
from code_coach.leetcode.problems_dart2 import (  # noqa: E402
    _BINARY_SEARCH,
    _DP,
    _GRAPH,
    _HEAP,
    _LINKED_LIST,
    _SUBSETS,
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
    _SUBSETS,
    _HEAP,
    _TOPOLOGICAL,
    _DP,
)
