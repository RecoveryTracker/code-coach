"""TypeScript for algorithms: the shapes interview problems are built from.

The same moves as the Python, JavaScript and Dart sets, written the way
strict TypeScript writes them: annotated declarations (`const seen:
Set<string>`), `Map<K, V>` and `Record<string, number>` for counting,
generic helpers (`function f<T>(...)`), tuple types and `as const` for
directions, `readonly` parameters, `?? 0` where a lookup can miss, `?.` for
a grid cell that may be off the edge, and `!` where the algorithm knows
better than the compiler.

The blocks are whole programs that print with `console.log`, and the tests
compile every one with `tsc --strict` and run it, then hold what it prints to
an answer worked out by hand.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

TSALGO_LINES: tuple[Passage, ...] = (
    # two pointers and windows
    _s("let lo: number = 0, hi: number = nums.length - 1;", "two pointers, typed, one at each end"),
    _s("while (lo < hi && nums[lo] + nums[hi] !== goal) {", "closing in on a pair"),
    _s("windowSum += values[i] - values[i - k];", "slide: add the new end, drop the old"),
    _s("best = Math.max(best, end - start + 1);", "the widest window so far"),
    _s("const firstSeen = new Map<string, number>();", "a typed map from letter to position"),
    _s("if ((firstSeen.get(ch) ?? -1) >= start) start = firstSeen.get(ch)! + 1;",
       "a repeat inside the window; ! says the key is there"),
    _s("function keep<T>(items: readonly T[], ok: (x: T) => boolean): T[] {",
       "a generic filter that cannot touch its input"),
    # binary search
    _s("const mid: number = lo + Math.floor((hi - lo) / 2);", "a midpoint that cannot overflow"),
    _s("if (sorted[mid] === target) return mid;", "found it"),
    _s("if (sorted[mid] < target) lo = mid + 1; else hi = mid - 1;", "go right or left"),
    _s("function bisect<T>(xs: readonly T[], x: T, cmp: (a: T, b: T) => number): number {",
       "binary search for any type, given a comparator"),
    # maps, sets, counting
    _s("const indexOf = new Map<number, number>();", "value to position, for two sum"),
    _s("const partner: number | undefined = indexOf.get(target - nums[i]);",
       "undefined when the partner is not there yet"),
    _s("if (partner !== undefined) return [partner, i];", "narrowed to a number, so it is a pair"),
    _s("function twoSum(nums: number[], target: number): [number, number] | null {",
       "a tuple type says exactly two numbers come back"),
    _s("const tally: Record<string, number> = {};", "a plain object as a letter counter"),
    _s("tally[ch] = (tally[ch] ?? 0) + 1;", "counting; ?? covers the first sighting"),
    _s("freq.set(w, (freq.get(w) ?? 0) + 1);", "the same count with a Map"),
    _s("const unique: number[] = [...new Set(nums)].sort((a, b) => a - b);",
       "each value once, in numeric order"),
    _s("const visited = new Set<string>([start]);", "a typed set with the start in it"),
    _s("if (!visited.has(next)) { visited.add(next); queue.push(next); }", "visit each node once"),
    _s("const key: string = [...word].sort().join('');", "an anagram's sorted letters"),
    _s("(buckets[key] ??= []).push(word);", "make the group if missing, then add"),
    _s("function countBy<K extends string>(keys: K[]): Record<K, number> {",
       "a generic counter keyed by the exact strings you pass"),
    # stacks and queues
    _s("const openers: string[] = [];", "an array used as a stack"),
    _s("if (openers.length === 0 || openers.pop() !== pairs[ch]) return false;", "the wrong closer"),
    _s("while (stack.length > 0 && temps[stack[stack.length - 1]] < t) {", "a monotonic stack"),
    _s("const queue: string[] = [start];", "an array used as a queue"),
    _s("const current: string = queue.shift()!;", "the oldest in the queue; the loop checked it is not empty"),
    _s("for (const next of adjacency.get(node) ?? []) {", "every neighbour, or none"),
    _s("const dist: Record<string, number> = { [start]: 0 };", "a computed key puts the start at zero"),
    _s("dist.set(next, (dist.get(node) ?? 0) + 1);", "one further than the node it came from, in a Map"),
    # recursion and memo
    _s("const memo = new Map<number, number>();", "a cache for a recursive function"),
    _s("function fib(n: number, cache: Map<number, number> = new Map()): number {",
       "a default parameter holds the cache"),
    _s("interface TreeNode { val: number; left: TreeNode | null; right: TreeNode | null }",
       "a tree whose children may be missing"),
    _s("if (root === undefined) return 0;", "the base case when a child may be missing"),
    _s("return 1 + Math.max(height(root.left), height(root.right));", "a tree's height"),
    # dynamic programming
    _s("const dp: number[] = new Array(n + 1).fill(0);", "one slot per subproblem"),
    _s("dp[i] = Math.max(dp[i - 1], dp[i - 2] + loot[i - 1]);", "take it or skip it"),
    _s("const table: number[][] = Array.from({ length: rows }, () => Array(cols).fill(0));",
       "a grid with a fresh row each time"),
    _s("for (let amt: number = coin; amt <= amount; amt++) {", "every amount this coin helps"),
    _s("change[total] += change[total - coin];", "the ways of making change"),
    _s("const best: [number, number] = [0, -1];", "a tuple: the score and where it was found"),
    # prefix sums and folds
    _s("const prefix: number[] = [0];", "the empty prefix comes first"),
    _s("for (const x of nums) prefix.push(prefix[prefix.length - 1] + x);", "running totals"),
    _s("const rangeSum: number = prefix[j + 1] - prefix[i];", "any slice's sum in one step"),
    _s("const total = nums.reduce((sum, x) => sum + x, 0);", "adding up with reduce"),
    _s("const biggest: number = Math.max(...nums);", "spread the array into max"),
    # sorting
    _s("const ordered = [...heights].sort((a, b) => a - b);", "a numeric sort of a copy"),
    _s("ranges.sort((a, b) => a[0] - b[0] || a[1] - b[1]);", "by start, before merging"),
    _s("people.sort((a, b) => b.score - a.score || a.id - b.id);", "high score first, then by id"),
    _s("const top3: number[] = [...scores].sort((a, b) => b - a).slice(0, 3);",
       "the three largest, without touching scores"),
    _s("names.sort((a, b) => a.localeCompare(b, 'en', { sensitivity: 'base' }));",
       "sorted the way a person reads"),
    # strings
    _s("const reversed: string = [...text].reverse().join('');", "a string, backwards"),
    _s("const cleaned = text.toLowerCase().replace(/[^a-z0-9]/g, '');", "letters and digits only"),
    _s("const code: number = ch.charCodeAt(0) - 97;", "a to 0, b to 1 and so on"),
    _s("const shifted: string = String.fromCharCode(97 + ((code + shift) % 26));", "a Caesar shift"),
    # bits
    _s("if ((n & 1) === 1) odd++;", "the lowest bit says odd"),
    _s("rest &= rest - 1;", "clears the lowest set bit"),
    _s("const single: number = nums.reduce((a, b) => a ^ b, 0);", "pairs cancel out"),
    _s("const isPow2 = (n: number): boolean => n > 0 && (n & (n - 1)) === 0;", "exactly one bit set"),
    # grids
    _s("const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]] as const;", "the four neighbours, frozen as tuples"),
    _s("if (grid[row]?.[col] !== '1') return 0;", "off the edge, or not land: stop"),
    _s("for (const [dr, dc] of dirs) sink(r + dr, c + dc);", "spread to each neighbour"),
    # types doing the work
    _s("type Pair = readonly [number, number];", "a tuple that cannot be changed"),
    _s("const moves = ['U', 'D', 'L', 'R'] as const;", "as const keeps each letter as its own type"),
    _s("type Move = (typeof moves)[number];", "a union of the four letters, from the array"),
    _s("const owner: string = user?.profile?.name ?? 'guest';", "optional chaining, then a fallback"),
    _s("function last<T>(items: readonly T[]): T | undefined {", "a generic that admits an empty array"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"TypeScript · {note}")


TSALGO_BLOCKS: tuple[Passage, ...] = (
    _b("""function twoSum(nums: number[], target: number): [number, number] | null {
  const seen = new Map<number, number>();
  for (let i = 0; i < nums.length; i++) {
    const j = seen.get(target - nums[i]);
    if (j !== undefined) return [j, i];
    seen.set(nums[i], i);
  }
  return null;
}

console.log(twoSum([2, 7, 11, 15], 9)?.join(','), twoSum([1, 2], 7) ?? 'none');""",
       "two sum with a tuple result"),
    _b("""function search<T>(sorted: readonly T[], target: T, less: (a: T, b: T) => boolean): number {
  let lo = 0, hi = sorted.length - 1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (sorted[mid] === target) return mid;
    if (less(sorted[mid], target)) lo = mid + 1; else hi = mid - 1;
  }
  return -1;
}
const asc = (a: number, b: number): boolean => a < b;
console.log(search([1, 3, 5, 7, 9], 7, asc), search([2, 4], 3, asc));""",
       "a generic binary search"),
    _b("""const closer: Record<string, string> = { '(': ')', '[': ']', '{': '}' };

function valid(text: string): boolean {
  const stack: string[] = [];
  for (const ch of text) {
    if (ch in closer) stack.push(closer[ch]);
    else if (stack.pop() !== ch) return false;
  }
  return stack.length === 0;
}

console.log(valid('{[()]}'), valid('(]'), valid('(('), valid(')'));""",
       "matching brackets with a stack"),
    _b("""const graph = new Map<string, string[]>([['a', ['b', 'c']], ['b', ['d']], ['c', ['d']], ['d', []]]);
const dist = new Map<string, number>([['a', 0]]);
const queue: string[] = ['a'];
for (let head = 0; head < queue.length; head++) {
  const node = queue[head];
  for (const next of graph.get(node) ?? []) {
    if (dist.has(next)) continue;
    dist.set(next, dist.get(node)! + 1);
    queue.push(next);
  }
}
console.log([...dist].map(([k, v]) => k + v).join(' '));""",
       "breadth-first search for distances"),
    _b("""const memo = new Map<number, number>();

function climb(n: number): number {
  if (n <= 1) return 1;
  const cached = memo.get(n);
  if (cached !== undefined) return cached;
  const ways = climb(n - 1) + climb(n - 2);
  memo.set(n, ways);
  return ways;
}

console.log(Array.from({ length: 7 }, (_, i) => climb(i + 1)).join(' '));""",
       "climbing stairs with a Map memo"),
    _b("""function rob(houses: readonly number[]): number {
  let [take, skip] = [0, 0];
  for (const money of houses) {
    [take, skip] = [skip + money, Math.max(take, skip)];
  }
  return Math.max(take, skip);
}

console.log(rob([2, 7, 9, 3, 1]), rob([5]), rob([]));""",
       "house robber with tuple swaps"),
    _b("""type Interval = [number, number];

function merge(intervals: Interval[]): Interval[] {
  const merged: Interval[] = [];
  for (const [start, end] of [...intervals].sort((a, b) => a[0] - b[0])) {
    const last = merged[merged.length - 1];
    if (last && start <= last[1]) last[1] = Math.max(last[1], end);
    else merged.push([start, end]);
  }
  return merged;
}

console.log(JSON.stringify(merge([[1, 3], [8, 10], [2, 6], [9, 12]])));""",
       "merging overlapping intervals"),
    _b("""function coinWays(coins: number[], amount: number): number {
  const ways: number[] = new Array(amount + 1).fill(0);
  ways[0] = 1;
  for (const coin of coins) {
    for (let total = coin; total <= amount; total++) ways[total] += ways[total - coin];
  }
  return ways[amount];
}

console.log(coinWays([1, 2, 5], 5), coinWays([2], 3));""",
       "counting the ways to make change"),
    _b("""const words = ['eat', 'tea', 'tan', 'ate', 'nat', 'bat'];
const groups: Record<string, string[]> = {};
for (const word of words) {
  const key = [...word].sort().join('');
  (groups[key] ??= []).push(word);
}
const sizes = Object.values(groups).map((g) => g.length).sort((a, b) => b - a);
console.log(sizes.join(' '), Object.keys(groups).join(','));""",
       "grouping anagrams in a Record"),
    _b("""const counts = new Map<string, number>();
for (const word of 'the cat and the hat and the bat'.split(' ')) {
  counts.set(word, (counts.get(word) ?? 0) + 1);
}
const leader = [...counts.entries()].sort((a, b) => b[1] - a[1])[0];
console.log(leader[0], leader[1], counts.size);""",
       "counting words with a Map"),
    _b("""const nums = [3, 1, 4, 1, 5, 9, 2, 6];
const prefix: number[] = [0];
for (const x of nums) prefix.push(prefix[prefix.length - 1] + x);
const range = (i: number, j: number): number => prefix[j + 1] - prefix[i];
let best = 0;
for (let i = 0; i + 3 <= nums.length; i++) best = Math.max(best, range(i, i + 2));
console.log(range(2, 5), best);""",
       "prefix sums and a window of three"),
    _b("""const grid: string[] = ['11000', '11000', '00100', '00011'];
const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]] as const;

function sink(r: number, c: number): number {
  if (grid[r]?.[c] !== '1') return 0;
  grid[r] = grid[r].slice(0, c) + '0' + grid[r].slice(c + 1);
  return 1 + dirs.reduce((sum, [dr, dc]) => sum + sink(r + dr, c + dc), 0);
}

const sizes: number[] = [];
for (let r = 0; r < grid.length; r++) {
  for (let c = 0; c < grid[r].length; c++) if (grid[r][c] === '1') sizes.push(sink(r, c));
}
console.log(sizes.join(' '));""",
       "island sizes with as const directions"),
    _b("""function single(nums: number[]): number {
  return nums.reduce((a, b) => a ^ b, 0);
}

const isPow2 = (n: number): boolean => n > 0 && (n & (n - 1)) === 0;
let bits = 0;
for (let m = 0b10110111; m > 0; m &= m - 1) bits++;
console.log(single([4, 1, 2, 1, 2]), [1, 6, 8, 64].map(isPow2).join(), bits);""",
       "bit tricks: xor, powers of two, popcount"),
    _b("""type Player = { name: string; score: number };

const players: Player[] = [
  { name: 'Mo', score: 7 },
  { name: 'Ana', score: 9 },
  { name: 'Bo', score: 7 },
];
players.sort((a, b) => b.score - a.score || a.name.localeCompare(b.name));
console.log(players.map((p) => p.name + ':' + p.score).join(' '));""",
       "sorting objects with a comparator"),
    _b("""function warmer(temps: number[]): number[] {
  const days: number[] = new Array(temps.length).fill(0);
  const stack: number[] = [];
  for (let i = 0; i < temps.length; i++) {
    while (stack.length > 0 && temps[stack[stack.length - 1]] < temps[i]) {
      const j = stack.pop()!; days[j] = i - j;
    }
    stack.push(i);
  }
  return days;
}

console.log(warmer([73, 74, 75, 71, 69, 72, 76, 73]).join(' '));""",
       "warmer days with a monotonic stack"),
    _b("""function isPalindrome(text: string): boolean {
  const s = text.toLowerCase().replace(/[^a-z0-9]/g, '');
  let lo = 0, hi = s.length - 1;
  while (lo < hi) if (s[lo++] !== s[hi--]) return false;
  return true;
}

console.log(isPalindrome('A man, a plan, a canal: Panama'), isPalindrome('race a car'));""",
       "a palindrome with two pointers"),
)

#: What each block prints, by its note - worked out by hand before node was
#: asked, and held to the real run by tests/test_typing_tsalgo.py.
TSALGO_PRINTS: dict[str, str] = {
    "two sum with a tuple result": "0,1 none",
    "a generic binary search": "3 -1",
    "matching brackets with a stack": "true false false false",
    "breadth-first search for distances": "a0 b1 c1 d2",
    "climbing stairs with a Map memo": "1 2 3 5 8 13 21",
    "house robber with tuple swaps": "12 5 0",
    "merging overlapping intervals": "[[1,6],[8,12]]",
    "counting the ways to make change": "4 0",
    "grouping anagrams in a Record": "3 2 1 aet,ant,abt",
    "counting words with a Map": "the 3 5",
    "prefix sums and a window of three": "19 17",
    "island sizes with as const directions": "4 1 2",
    "bit tricks: xor, powers of two, popcount": "4 true,false,true,true 6",
    "sorting objects with a comparator": "Ana:9 Bo:7 Mo:7",
    "warmer days with a monotonic stack": "1 1 4 2 1 1 0 0",
    "a palindrome with two pointers": "true false",
}
