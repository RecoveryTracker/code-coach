"""
The same LeetCode patterns, written in TypeScript.

The algorithms match `problems_js.py` — what's added is the type layer, which
is the part worth drilling: `number[]` versus `number[][]`, `Map<number,
number>`, the `!` that tells the compiler a lookup succeeded, and the `| null`
unions that linked lists and trees need.
"""

from __future__ import annotations

from code_coach.leetcode.ts_common import _p
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
            function twoSum(nums: number[], target: number): number[] {
              const seen = new Map<number, number>();
              for (let i = 0; i < nums.length; i++) {
                const need = target - nums[i];
                if (seen.has(need)) return [seen.get(need)!, i];
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
            function containsDuplicate(nums: number[]): boolean {
              const seen = new Set<number>();
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
            function isAnagram(s: string, t: string): boolean {
              if (s.length !== t.length) return false;
              const counts = new Map<string, number>();
              for (const ch of s) {
                counts.set(ch, (counts.get(ch) ?? 0) + 1);
              }
              for (const ch of t) {
                const left = counts.get(ch) ?? 0;
                if (left === 0) return false;
                counts.set(ch, left - 1);
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
            function groupAnagrams(strs: string[]): string[][] {
              const groups = new Map<string, string[]>();
              for (const word of strs) {
                const key = word.split('').sort().join('');
                if (!groups.has(key)) groups.set(key, []);
                groups.get(key)!.push(word);
              }
              return [...groups.values()];
            }
            """,
        ),
        _p(
            454, '4Sum II', 'Medium',
            'Count every sum from the first two lists, then look up its negation from the other two.',
            'O(n^2) time, O(n^2) space',
            """
            function fourSumCount(a: number[], b: number[], c: number[], d: number[]): number {
              const pairs = new Map<number, number>();
              for (const x of a) {
                for (const y of b) {
                  pairs.set(x + y, (pairs.get(x + y) || 0) + 1);
                }
              }
              let found = 0;
              for (const z of c) {
                for (const w of d) {
                  found += pairs.get(-(z + w)) || 0;
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
            function subarraySum(nums: number[], k: number): number {
              const seen = new Map<number, number>([[0, 1]]);
              let running = 0;
              let found = 0;
              for (const n of nums) {
                running += n;
                found += seen.get(running - k) || 0;
                seen.set(running, (seen.get(running) || 0) + 1);
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
            function longestConsecutive(nums: number[]): number {
              const pool = new Set<number>(nums);
              let best = 0;
              for (const n of pool) {
                if (pool.has(n - 1)) continue;
                let length = 1;
                while (pool.has(n + length)) length++;
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
            function isValidSudoku(board: string[][]): boolean {
              const rows = new Map<number, Set<string>>();
              const cols = new Map<number, Set<string>>();
              const boxes = new Map<string, Set<string>>();
              const clash = <K>(store: Map<K, Set<string>>, key: K, value: string): boolean => {
                if (!store.has(key)) store.set(key, new Set<string>());
                const seen = store.get(key)!;
                if (seen.has(value)) return true;
                seen.add(value);
                return false;
              };
              for (let r = 0; r < 9; r++) {
                for (let c = 0; c < 9; c++) {
                  const value = board[r][c];
                  if (value === '.') continue;
                  const box = `${Math.floor(r / 3)},${Math.floor(c / 3)}`;
                  if (clash(rows, r, value)) return false;
                  if (clash(cols, c, value)) return false;
                  if (clash(boxes, box, value)) return false;
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
            function isPalindrome(s: string): boolean {
              const ok = (c: string): boolean => /[a-z0-9]/i.test(c);
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
            function twoSumSorted(numbers: number[], target: number): number[] {
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
            function maxArea(height: number[]): number {
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
            function threeSum(nums: number[]): number[][] {
              nums.sort((a, b) => a - b);
              const out: number[][] = [];
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
        _p(
            26, 'Remove Duplicates from Sorted Array', 'Easy',
            'One pointer writes, the other reads — the writer only moves on a new value.',
            'O(n) time, O(1) space',
            """
            function removeDuplicates(nums: number[]): number {
              if (nums.length === 0) return 0;
              let write = 1;
              for (let read = 1; read < nums.length; read++) {
                if (nums[read] !== nums[write - 1]) {
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
            function moveZeroes(nums: number[]): number[] {
              let write = 0;
              for (let read = 0; read < nums.length; read++) {
                if (nums[read] !== 0) {
                  nums[write] = nums[read];
                  write++;
                }
              }
              for (let i = write; i < nums.length; i++) nums[i] = 0;
              return nums;
            }
            """,
        ),
        _p(
            42, 'Trapping Rain Water', 'Hard',
            'Water over a column is the smaller of the two tallest walls beside it, minus the column.',
            'O(n) time, O(1) space',
            """
            function trap(height: number[]): number {
              if (height.length === 0) return 0;
              let left = 0;
              let right = height.length - 1;
              let leftMax = height[left];
              let rightMax = height[right];
              let water = 0;
              while (left < right) {
                if (leftMax < rightMax) {
                  left++;
                  leftMax = Math.max(leftMax, height[left]);
                  water += leftMax - height[left];
                } else {
                  right--;
                  rightMax = Math.max(rightMax, height[right]);
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
            function sortedSquares(nums: number[]): number[] {
              const out = new Array<number>(nums.length).fill(0);
              let left = 0;
              let right = nums.length - 1;
              for (let slot = nums.length - 1; slot >= 0; slot--) {
                if (Math.abs(nums[left]) > Math.abs(nums[right])) {
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
            function maxProfit(prices: number[]): number {
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
            function lengthOfLongestSubstring(s: string): number {
              const lastSeen = new Map<string, number>();
              let left = 0;
              let best = 0;
              for (let right = 0; right < s.length; right++) {
                const ch = s[right];
                const seenAt = lastSeen.get(ch);
                if (seenAt !== undefined && seenAt >= left) left = seenAt + 1;
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
            function minSubArrayLen(target: number, nums: number[]): number {
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
            "A window is valid while its size minus its commonest letter is at most k.",
            "O(n) time, O(1) space",
            """
            function characterReplacement(s: string, k: number): number {
              const counts = new Map<string, number>();
              let left = 0;
              let mostCommon = 0;
              let best = 0;
              for (let right = 0; right < s.length; right++) {
                const ch = s[right];
                counts.set(ch, (counts.get(ch) ?? 0) + 1);
                mostCommon = Math.max(mostCommon, counts.get(ch)!);
                while (right - left + 1 - mostCommon > k) {
                  counts.set(s[left], counts.get(s[left])! - 1);
                  left++;
                }
                best = Math.max(best, right - left + 1);
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
            function findMaxAverage(nums: number[], k: number): number {
              let window = 0;
              for (let i = 0; i < k; i++) window += nums[i];
              let best = window;
              for (let i = k; i < nums.length; i++) {
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
            function checkInclusion(pattern: string, text: string): boolean {
              if (pattern.length > text.length) return false;
              const need = new Map<string, number>();
              for (const ch of pattern) need.set(ch, (need.get(ch) || 0) + 1);
              const window = new Map<string, number>();
              const same = (): boolean => {
                if (window.size !== need.size) return false;
                for (const [ch, count] of need) {
                  if (window.get(ch) !== count) return false;
                }
                return true;
              };
              for (let i = 0; i < text.length; i++) {
                const ch = text[i];
                window.set(ch, (window.get(ch) || 0) + 1);
                if (i >= pattern.length) {
                  const out = text[i - pattern.length];
                  window.set(out, (window.get(out) || 0) - 1);
                  if (window.get(out) === 0) window.delete(out);
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
            function longestOnes(nums: number[], k: number): number {
              let left = 0;
              let zeros = 0;
              let best = 0;
              for (let right = 0; right < nums.length; right++) {
                if (nums[right] === 0) zeros++;
                while (zeros > k) {
                  if (nums[left] === 0) zeros--;
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
            function minWindow(text: string, pattern: string): string {
              if (pattern.length === 0 || text.length === 0) return '';
              const need = new Map<string, number>();
              for (const ch of pattern) need.set(ch, (need.get(ch) || 0) + 1);
              let missing = need.size;
              const window = new Map<string, number>();
              let best = '';
              let left = 0;
              for (let right = 0; right < text.length; right++) {
                const ch = text[right];
                window.set(ch, (window.get(ch) || 0) + 1);
                if (need.has(ch) && window.get(ch) === need.get(ch)) missing--;
                while (missing === 0) {
                  if (best === '' || right - left + 1 < best.length) {
                    best = text.slice(left, right + 1);
                  }
                  const out = text[left];
                  window.set(out, (window.get(out) || 0) - 1);
                  if (need.has(out) && (window.get(out) || 0) < (need.get(out) || 0)) missing++;
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
            function isValid(s: string): boolean {
              const pairs: Record<string, string> = { ')': '(', ']': '[', '}': '{' };
              const stack: string[] = [];
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
              private items: number[][] = [];

              push(val: number): void {
                const smallest = this.items.length
                  ? Math.min(val, this.getMin())
                  : val;
                this.items.push([val, smallest]);
              }

              pop(): void {
                this.items.pop();
              }

              top(): number {
                return this.items[this.items.length - 1][0];
              }

              getMin(): number {
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
            function evalRPN(tokens: string[]): number {
              const stack: number[] = [];
              for (const token of tokens) {
                if (token === '+' || token === '-' || token === '*' || token === '/') {
                  const b = stack.pop()!;
                  const a = stack.pop()!;
                  if (token === '+') stack.push(a + b);
                  if (token === '-') stack.push(a - b);
                  if (token === '*') stack.push(a * b);
                  if (token === '/') stack.push(Math.trunc(a / b));
                } else {
                  stack.push(Number(token));
                }
              }
              return stack.pop()!;
            }
            """,
        ),
        _p(
            739, "Daily Temperatures", "Medium",
            "Keep indexes waiting for a warmer day; pop them when it arrives.",
            "O(n) time, O(n) space",
            """
            function dailyTemperatures(temperatures: number[]): number[] {
              const answer = new Array<number>(temperatures.length).fill(0);
              const stack: number[] = [];
              for (let i = 0; i < temperatures.length; i++) {
                while (
                  stack.length &&
                  temperatures[i] > temperatures[stack[stack.length - 1]]
                ) {
                  const day = stack.pop()!;
                  answer[day] = i - day;
                }
                stack.push(i);
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
            function calPoints(operations: string[]): number {
              const stack: number[] = [];
              for (const op of operations) {
                if (op === 'C') stack.pop();
                else if (op === 'D') stack.push(stack[stack.length - 1] * 2);
                else if (op === '+') stack.push(stack[stack.length - 1] + stack[stack.length - 2]);
                else stack.push(Number(op));
              }
              return stack.reduce((total, n) => total + n, 0);
            }
            """,
        ),
        _p(
            71, 'Simplify Path', 'Medium',
            "A '..' pops the directory before it, which is exactly what a stack is for.",
            'O(n) time, O(n) space',
            """
            function simplifyPath(path: string): string {
              const stack: string[] = [];
              for (const part of path.split('/')) {
                if (part === '' || part === '.') continue;
                if (part === '..') stack.pop();
                else stack.push(part);
              }
              return '/' + stack.join('/');
            }
            """,
        ),
        _p(
            84, 'Largest Rectangle in Histogram', 'Hard',
            'Keep bars increasing; a shorter one closes off every taller bar behind it.',
            'O(n) time, O(n) space',
            """
            function largestRectangleArea(heights: number[]): number {
              const stack: [number, number][] = [];
              let best = 0;
              const bars = [...heights, 0];
              for (let i = 0; i < bars.length; i++) {
                let start = i;
                while (stack.length && stack[stack.length - 1][1] > bars[i]) {
                  const [left, tall] = stack.pop()!;
                  if (tall * (i - left) > best) best = tall * (i - left);
                  start = left;
                }
                stack.push([start, bars[i]]);
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
            function decodeString(encoded: string): string {
              const stack: [string, number][] = [];
              let current = '';
              let count = 0;
              for (const ch of encoded) {
                if (ch >= '0' && ch <= '9') {
                  count = count * 10 + Number(ch);
                } else if (ch === '[') {
                  stack.push([current, count]);
                  current = '';
                  count = 0;
                } else if (ch === ']') {
                  const [before, times] = stack.pop()!;
                  current = before + current.repeat(times);
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


from code_coach.leetcode.problems_ts2 import (  # noqa: E402
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
