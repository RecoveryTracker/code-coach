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
        _p(
            454, '4Sum II', 'Medium',
            'Count every sum from the first two lists, then look up its negation from the other two.',
            'O(n^2) time, O(n^2) space',
            """
            int fourSumCount(List<int> a, List<int> b, List<int> c, List<int> d) {
              final pairs = <int, int>{};
              for (final x in a) {
                for (final y in b) {
                  pairs[x + y] = (pairs[x + y] ?? 0) + 1;
                }
              }
              var found = 0;
              for (final z in c) {
                for (final w in d) {
                  found += pairs[-(z + w)] ?? 0;
                }
              }
              return found;
            }
            """,
        ),
        _p(
            560, 'Subarray Sum Equals K', 'Medium',
            "Remember every running total you've seen; the gap between two of them is a subarray.",
            'O(n) time, O(n) space',
            """
            int subarraySum(List<int> nums, int k) {
              final seen = <int, int>{0: 1};
              var running = 0;
              var found = 0;
              for (final n in nums) {
                running += n;
                found += seen[running - k] ?? 0;
                seen[running] = (seen[running] ?? 0) + 1;
              }
              return found;
            }
            """,
        ),
        _p(
            128, 'Longest Consecutive Sequence', 'Medium',
            'Only start counting from a number with no left neighbour — each run is walked once.',
            'O(n) time, O(n) space',
            """
            int longestConsecutive(List<int> nums) {
              final pool = nums.toSet();
              var best = 0;
              for (final n in pool) {
                if (pool.contains(n - 1)) continue;
                var length = 1;
                while (pool.contains(n + length)) length++;
                if (length > best) best = length;
              }
              return best;
            }
            """,
        ),
        _p(
            36, 'Valid Sudoku', 'Medium',
            'Three sets per cell: its row, its column, and its box at (r // 3, c // 3).',
            'O(1) time, O(1) space',
            """
            bool isValidSudoku(List<List<String>> board) {
              final rows = <int, Set<String>>{};
              final cols = <int, Set<String>>{};
              final boxes = <String, Set<String>>{};
              for (var r = 0; r < 9; r++) {
                for (var c = 0; c < 9; c++) {
                  final value = board[r][c];
                  if (value == '.') continue;
                  final box = '${r ~/ 3},${c ~/ 3}';
                  if (!rows.putIfAbsent(r, () => <String>{}).add(value)) return false;
                  if (!cols.putIfAbsent(c, () => <String>{}).add(value)) return false;
                  if (!boxes.putIfAbsent(box, () => <String>{}).add(value)) return false;
                }
              }
              return true;
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
        _p(
            26, 'Remove Duplicates from Sorted Array', 'Easy',
            'One pointer writes, the other reads — the writer only moves on a new value.',
            'O(n) time, O(1) space',
            """
            int removeDuplicates(List<int> nums) {
              if (nums.isEmpty) return 0;
              var write = 1;
              for (var read = 1; read < nums.length; read++) {
                if (nums[read] != nums[write - 1]) {
                  nums[write] = nums[read];
                  write++;
                }
              }
              return write;
            }
            """,
        ),
        _p(
            283, 'Move Zeroes', 'Easy',
            'Same read/write pair: write every non-zero forward, then fill the tail.',
            'O(n) time, O(1) space',
            """
            List<int> moveZeroes(List<int> nums) {
              var write = 0;
              for (var read = 0; read < nums.length; read++) {
                if (nums[read] != 0) {
                  nums[write] = nums[read];
                  write++;
                }
              }
              for (var i = write; i < nums.length; i++) {
                nums[i] = 0;
              }
              return nums;
            }
            """,
        ),
        _p(
            42, 'Trapping Rain Water', 'Hard',
            'Water over a column is the smaller of the two tallest walls beside it, minus the column.',
            'O(n) time, O(1) space',
            """
            int trap(List<int> height) {
              if (height.isEmpty) return 0;
              var left = 0;
              var right = height.length - 1;
              var leftMax = height[left];
              var rightMax = height[right];
              var water = 0;
              while (left < right) {
                if (leftMax < rightMax) {
                  left++;
                  if (height[left] > leftMax) leftMax = height[left];
                  water += leftMax - height[left];
                } else {
                  right--;
                  if (height[right] > rightMax) rightMax = height[right];
                  water += rightMax - height[right];
                }
              }
              return water;
            }
            """,
        ),
        _p(
            977, 'Squares of a Sorted Array', 'Easy',
            'The biggest square is at one end or the other, so fill the answer backwards.',
            'O(n) time, O(n) space',
            """
            List<int> sortedSquares(List<int> nums) {
              final out = List<int>.filled(nums.length, 0);
              var left = 0;
              var right = nums.length - 1;
              for (var slot = nums.length - 1; slot >= 0; slot--) {
                if (nums[left].abs() > nums[right].abs()) {
                  out[slot] = nums[left] * nums[left];
                  left++;
                } else {
                  out[slot] = nums[right] * nums[right];
                  right--;
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
        _p(
            643, 'Maximum Average Subarray I', 'Easy',
            'The window never changes size, so each step adds one number and drops one.',
            'O(n) time, O(1) space',
            """
            double findMaxAverage(List<int> nums, int k) {
              var window = 0;
              for (var i = 0; i < k; i++) {
                window += nums[i];
              }
              var best = window;
              for (var i = k; i < nums.length; i++) {
                window += nums[i] - nums[i - k];
                if (window > best) best = window;
              }
              return best / k;
            }
            """,
        ),
        _p(
            567, 'Permutation in String', 'Medium',
            'A fixed window whose letter counts match is a permutation — no sorting needed.',
            'O(n) time, O(1) space',
            """
            bool checkInclusion(String pattern, String text) {
              if (pattern.length > text.length) return false;
              final need = <String, int>{};
              for (final ch in pattern.split('')) {
                need[ch] = (need[ch] ?? 0) + 1;
              }
              final window = <String, int>{};
              bool same() {
                if (window.length != need.length) return false;
                for (final entry in need.entries) {
                  if (window[entry.key] != entry.value) return false;
                }
                return true;
              }

              for (var i = 0; i < text.length; i++) {
                final ch = text[i];
                window[ch] = (window[ch] ?? 0) + 1;
                if (i >= pattern.length) {
                  final out = text[i - pattern.length];
                  window[out] = window[out]! - 1;
                  if (window[out] == 0) window.remove(out);
                }
                if (same()) return true;
              }
              return false;
            }
            """,
        ),
        _p(
            1004, 'Max Consecutive Ones III', 'Medium',
            'Grow while at most k zeros are inside; shrink from the left when a k+1th appears.',
            'O(n) time, O(1) space',
            """
            int longestOnes(List<int> nums, int k) {
              var left = 0;
              var zeros = 0;
              var best = 0;
              for (var right = 0; right < nums.length; right++) {
                if (nums[right] == 0) zeros++;
                while (zeros > k) {
                  if (nums[left] == 0) zeros--;
                  left++;
                }
                if (right - left + 1 > best) best = right - left + 1;
              }
              return best;
            }
            """,
        ),
        _p(
            76, 'Minimum Window Substring', 'Hard',
            'Count how many required letters are satisfied; shrink only while all of them are.',
            'O(n) time, O(1) space',
            """
            String minWindow(String text, String pattern) {
              if (pattern.isEmpty || text.isEmpty) return '';
              final need = <String, int>{};
              for (final ch in pattern.split('')) {
                need[ch] = (need[ch] ?? 0) + 1;
              }
              var missing = need.length;
              final window = <String, int>{};
              var best = '';
              var left = 0;
              for (var right = 0; right < text.length; right++) {
                final ch = text[right];
                window[ch] = (window[ch] ?? 0) + 1;
                if (need.containsKey(ch) && window[ch] == need[ch]) missing--;
                while (missing == 0) {
                  if (best.isEmpty || right - left + 1 < best.length) {
                    best = text.substring(left, right + 1);
                  }
                  final out = text[left];
                  window[out] = window[out]! - 1;
                  if (need.containsKey(out) && window[out]! < need[out]!) missing++;
                  left++;
                }
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
        _p(
            682, 'Baseball Game', 'Easy',
            'Every operation only ever looks at the top of the stack, which is the whole idea.',
            'O(n) time, O(n) space',
            """
            int calPoints(List<String> operations) {
              final stack = <int>[];
              for (final op in operations) {
                if (op == 'C') {
                  stack.removeLast();
                } else if (op == 'D') {
                  stack.add(stack.last * 2);
                } else if (op == '+') {
                  stack.add(stack.last + stack[stack.length - 2]);
                } else {
                  stack.add(int.parse(op));
                }
              }
              return stack.fold(0, (total, n) => total + n);
            }
            """,
        ),
        _p(
            71, 'Simplify Path', 'Medium',
            "A '..' pops the directory before it, which is exactly what a stack is for.",
            'O(n) time, O(n) space',
            """
            String simplifyPath(String path) {
              final stack = <String>[];
              for (final part in path.split('/')) {
                if (part.isEmpty || part == '.') continue;
                if (part == '..') {
                  if (stack.isNotEmpty) stack.removeLast();
                } else {
                  stack.add(part);
                }
              }
              return '/${stack.join('/')}';
            }
            """,
        ),
        _p(
            84, 'Largest Rectangle in Histogram', 'Hard',
            'Keep bars increasing; a shorter one closes off every taller bar behind it.',
            'O(n) time, O(n) space',
            """
            int largestRectangleArea(List<int> heights) {
              final stack = <List<int>>[];
              var best = 0;
              final bars = [...heights, 0];
              for (var i = 0; i < bars.length; i++) {
                var start = i;
                while (stack.isNotEmpty && stack.last[1] > bars[i]) {
                  final closed = stack.removeLast();
                  final area = closed[1] * (i - closed[0]);
                  if (area > best) best = area;
                  start = closed[0];
                }
                stack.add([start, bars[i]]);
              }
              return best;
            }
            """,
        ),
        _p(
            394, 'Decode String', 'Medium',
            'Push the work in progress when a bracket opens, finish it when one closes.',
            'O(n) time, O(n) space',
            """
            String decodeString(String encoded) {
              final stack = <List<Object>>[];
              var current = '';
              var count = 0;
              for (final ch in encoded.split('')) {
                final digit = int.tryParse(ch);
                if (digit != null) {
                  count = count * 10 + digit;
                } else if (ch == '[') {
                  stack.add([current, count]);
                  current = '';
                  count = 0;
                } else if (ch == ']') {
                  final frame = stack.removeLast();
                  current = (frame[0] as String) + current * (frame[1] as int);
                } else {
                  current += ch;
                }
              }
              return current;
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
