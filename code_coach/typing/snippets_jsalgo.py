"""JavaScript for algorithms: the shapes interview problems are built from.

The same moves as the Python set (snippets_pyalgo), written the way
JavaScript writes them: a Map where Python reaches for a dict, a Set for a
visited set, `arr.at(-1)` for the top of a stack, `Math.floor` for the
midpoint, an array used as a queue with an index so shift() is never paid
for, and sort comparators, because sort() with nothing sorts numbers as
text.

The blocks are whole small solutions that print their answer, and the tests
run every one in Node and hold what it prints to an answer worked out by
hand. No clock, no dice.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

JSALGO_LINES: tuple[Passage, ...] = (
    # two pointers and windows
    _s("let lo = 0, hi = heights.length - 1;", "two pointers, one at each end"),
    _s("while (lo < hi && nums[lo] + nums[hi] !== target) {", "closing in on a pair"),
    _s("[nums[lo], nums[hi]] = [nums[hi], nums[lo]];", "swap by destructuring"),
    _s("windowSum += nums[i] - nums[i - k];", "slide: add the new end, drop the old"),
    _s("bestLen = Math.max(bestLen, end - start + 1);", "the widest window so far"),
    _s("lastSeen.set(ch, end);", "where this letter was last seen"),
    _s("if (lastSeen.has(ch) && lastSeen.get(ch) >= start) {", "a repeat inside the window"),
    # binary search
    _s("const middle = Math.floor((left + right) / 2);", "the middle, rounded down"),
    _s("const midpoint = lo + ((hi - lo) >> 1);", "the same, written with a shift"),
    _s("if (sorted[mid] < target) lo = mid + 1;", "the answer is to the right"),
    _s("hi = sorted[mid] > target ? mid - 1 : hi;", "the answer is to the left"),
    # Map, Set and counting
    _s("const index = new Map();", "value to position, for two sum"),
    _s("if (index.has(target - x)) return [index.get(target - x), i];", "found the pair"),
    _s("counts.set(word, (counts.get(word) ?? 0) + 1);", "counting with a Map"),
    _s("const unique = [...new Set(nums)];", "each value once, order kept"),
    _s("const visited = new Set([start]);", "the start is visited before it is queued"),
    _s("if (!visited.has(next)) { visited.add(next); queue.push([next, dist + 1]); }", "never queue a node twice"),
    _s("const key = [...word].sort().join(\"\");", "an anagram's sorted letters"),
    _s("(groups[key] ??= []).push(word);", "make the group if it is missing, then add"),
    # stacks and queues
    _s("const top = stack.at(-1);", "the top of the stack without popping"),
    _s("while (stack.length && temps[stack.at(-1)] < t) {", "a monotonic stack"),
    _s("if (stack.pop() !== closerFor[ch]) return false;", "the bracket that should close"),
    _s("const queue = [[start, 0]];", "a queue of node and distance"),
    _s("for (let head = 0; head < queue.length; head++) {", "an index, so shift() is never paid"),
    _s("const [node, dist] = queue[head];", "the next one in the queue"),
    _s("for (const next of graph[node] ?? []) {", "every neighbour, or none"),
    # recursion and memo
    _s("const memo = new Map();", "a cache for a recursive function"),
    _s("if (memo.has(n)) return memo.get(n);", "already worked out"),
    _s("memo.set(n, ways(n - 1) + ways(n - 2));", "worked out once, then kept"),
    _s("if (root === null || root === undefined) return 0;", "the base case of every tree recursion"),
    _s("return 1 + Math.max(depth(node.left), depth(node.right));", "a tree's height"),
    _s("const dfs = (r, c) => {", "an arrow function that can call itself"),
    # dynamic programming
    _s("const dp = new Array(n + 1).fill(0);", "one slot per subproblem"),
    _s("dp[i] = Math.max(dp[i - 1], dp[i - 2] + houses[i - 1]);", "take it or skip it"),
    _s("const grid = Array.from({ length: rows }, () => new Array(cols).fill(0));",
       "a grid with a fresh row each time"),
    _s("dp[i][j] = a[i - 1] === b[j - 1] ? dp[i - 1][j - 1] + 1 : 0;", "extend the match"),
    _s("for (let total = coin; total <= amount; total++) {", "every amount this coin can help"),
    _s("ways[total] += ways[total - coin];", "the ways of making change"),
    # prefix sums
    _s("const prefix = [0];", "the empty prefix comes first"),
    _s("for (const x of nums) prefix.push(prefix.at(-1) + x);", "running totals"),
    _s("const rangeSum = prefix[j + 1] - prefix[i];", "any slice's sum in one step"),
    _s("count += seenSums.get(running - k) ?? 0;", "subarrays that add up to k"),
    # sorting
    _s("prices.sort((x, y) => x - y);", "numbers as numbers, not as text"),
    _s("intervals.sort((a, b) => a[0] - b[0]);", "by start, before merging"),
    _s("people.sort((a, b) => b.score - a.score || a.name.localeCompare(b.name));",
       "high score first, then A to Z"),
    _s("if (start <= merged.at(-1)[1]) merged.at(-1)[1] = Math.max(merged.at(-1)[1], end);",
       "stretch the last interval"),
    _s("const topThree = [...scores].sort((a, b) => b - a).slice(0, 3);",
       "the three largest, without touching scores"),
    # strings
    _s("const reversed = [...text].reverse().join(\"\");", "a string, backwards"),
    _s("const isPal = cleaned === [...cleaned].reverse().join(\"\");", "a palindrome test"),
    _s("const cleaned = text.toLowerCase().replace(/[^a-z0-9]/g, \"\");", "letters and digits only"),
    _s("const code = ch.charCodeAt(0) - 97;", "a to 0, b to 1 and so on"),
    _s("const letter = String.fromCharCode(97 + ((code + shift) % 26));", "a Caesar shift"),
    # bits
    _s("if (n & 1) odd++;", "the lowest bit says odd"),
    _s("bits &= bits - 1;", "clears the lowest set bit"),
    _s("const single = nums.reduce((acc, x) => acc ^ x, 0);", "pairs cancel out"),
    _s("const isPowerOfTwo = n > 0 && (n & (n - 1)) === 0;", "exactly one bit set"),
    # grids
    _s("const DIRS = [[1, 0], [-1, 0], [0, 1], [0, -1]];", "the four neighbours"),
    _s("if (r < 0 || c < 0 || r >= rows || c >= cols) return;", "off the edge of the grid"),
    _s("for (const [dr, dc] of DIRS) dfs(r + dr, c + dc);", "spread to each neighbour"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"JavaScript · {note}")


JSALGO_BLOCKS: tuple[Passage, ...] = (
    _b("""function twoSum(nums, target) {
  const index = new Map();
  for (let i = 0; i < nums.length; i++) {
    const want = target - nums[i];
    if (index.has(want)) return [index.get(want), i];
    index.set(nums[i], i);
  }
  return [];
}
console.log(twoSum([2, 7, 11, 15], 9), twoSum([1, 2], 7));""",
       "two sum with a Map"),
    _b("""function search(sorted, target) {
  let lo = 0, hi = sorted.length - 1;
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2);
    if (sorted[mid] === target) return mid;
    if (sorted[mid] < target) lo = mid + 1;
    else hi = mid - 1;
  }
  return -1;
}
console.log(search([1, 3, 5, 7, 9], 9), search([2, 4], 3));""",
       "binary search"),
    _b("""function longestUnique(s) {
  const last = new Map();
  let start = 0, best = 0;
  for (let end = 0; end < s.length; end++) {
    if (last.has(s[end]) && last.get(s[end]) >= start) start = last.get(s[end]) + 1;
    last.set(s[end], end);
    best = Math.max(best, end - start + 1);
  }
  return best;
}
console.log(longestUnique("abcabcbb"), longestUnique("pwwkew"));""",
       "the longest run without a repeat"),
    _b("""function valid(text) {
  const closer = { "(": ")", "[": "]", "{": "}" };
  const stack = [];
  for (const ch of text) {
    if (ch in closer) stack.push(closer[ch]);
    else if (stack.pop() !== ch) return false;
  }
  return stack.length === 0;
}
console.log(valid("{[()]}"), valid("(]"), valid("(("));""",
       "matching brackets with a stack"),
    _b("""const graph = { a: ["b", "c"], b: ["d"], c: ["d"], d: [] };
const dist = { a: 0 };
const queue = ["a"];
for (let head = 0; head < queue.length; head++) {
  const node = queue[head];
  for (const next of graph[node]) {
    if (next in dist) continue;
    dist[next] = dist[node] + 1;
    queue.push(next);
  }
}
console.log(JSON.stringify(dist));""",
       "breadth-first search for distances"),
    _b("""const memo = new Map();
function climb(n) {
  if (n <= 1) return 1;
  if (!memo.has(n)) memo.set(n, climb(n - 1) + climb(n - 2));
  return memo.get(n);
}
console.log([1, 2, 3, 4, 5, 6, 7].map(climb).join(" "));""",
       "climbing stairs with a memo"),
    _b("""function rob(houses) {
  let take = 0, skip = 0;
  for (const money of houses) {
    [take, skip] = [skip + money, Math.max(take, skip)];
  }
  return Math.max(take, skip);
}
console.log(rob([2, 7, 9, 3, 1]), rob([5]), rob([]));""",
       "house robber in two variables"),
    _b("""function merge(intervals) {
  const merged = [];
  for (const [start, end] of [...intervals].sort((a, b) => a[0] - b[0])) {
    if (merged.length && start <= merged.at(-1)[1]) {
      merged.at(-1)[1] = Math.max(merged.at(-1)[1], end);
    } else merged.push([start, end]);
  }
  return merged;
}
console.log(JSON.stringify(merge([[1, 3], [8, 10], [2, 6], [9, 12]])));""",
       "merging overlapping intervals"),
    _b("""function coinWays(coins, amount) {
  const ways = [1, ...new Array(amount).fill(0)];
  for (const coin of coins) {
    for (let total = coin; total <= amount; total++) ways[total] += ways[total - coin];
  }
  return ways[amount];
}
console.log(coinWays([1, 2, 5], 5), coinWays([2], 3));""",
       "counting the ways to make change"),
    _b("""const words = ["eat", "tea", "tan", "ate", "nat", "bat"];
const groups = {};
for (const word of words) {
  const key = [...word].sort().join("");
  (groups[key] ??= []).push(word);
}
const sorted = Object.values(groups).sort((a, b) => b.length - a.length);
console.log(JSON.stringify(sorted));""",
       "grouping anagrams by sorted letters"),
    _b("""const scores = [10, 9, 100, 1, 25];
const asText = [...scores].sort();
const asNumbers = [...scores].sort((a, b) => a - b);
console.log(asText.join(" "));
console.log(asNumbers.join(" "));
console.log(scores.join(" "));""",
       "sort with and without a comparator"),
    _b("""function subarraysSummingTo(nums, k) {
  const seen = new Map([[0, 1]]);
  let running = 0, count = 0;
  for (const x of nums) {
    running += x;
    count += seen.get(running - k) ?? 0;
    seen.set(running, (seen.get(running) ?? 0) + 1);
  }
  return count;
}
console.log(subarraysSummingTo([1, 1, 1], 2), subarraysSummingTo([1, 2, 3], 3));""",
       "counting subarrays with prefix sums"),
)

#: What each block prints, by its note - worked out by hand before Node was
#: asked, and held to the real run by tests/test_typing_jsalgo.py.
JSALGO_PRINTS: dict[str, str] = {
    "two sum with a Map": "[ 0, 1 ] []",
    "binary search": "4 -1",
    "the longest run without a repeat": "3 3",
    "matching brackets with a stack": "true false false",
    "breadth-first search for distances": '{"a":0,"b":1,"c":1,"d":2}',
    "climbing stairs with a memo": "1 2 3 5 8 13 21",
    "house robber in two variables": "12 5 0",
    "merging overlapping intervals": "[[1,6],[8,12]]",
    "counting the ways to make change": "4 0",
    "grouping anagrams by sorted letters": '[["eat","tea","ate"],["tan","nat"],["bat"]]',
    "sort with and without a comparator": "1 10 100 25 9\n1 9 10 25 100\n10 9 100 1 25",
    "counting subarrays with prefix sums": "2 2",
}
