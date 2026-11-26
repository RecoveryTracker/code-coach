"""Dart for algorithms: the shapes interview problems are built from.

The same moves as the Python and JavaScript sets, written the way Dart
writes them: typed collections (`<int, int>{}`, `<String>[]`), `final` for
everything that is not reassigned, `~/` for the midpoint, `Queue` from
dart:collection for breadth-first search, `?? 0` where a map lookup can
miss, `List.filled` and `List.generate` for DP tables, and `compareTo` in
the sort comparators.

The blocks are whole programs with a `main`, and the tests run every one
in Dart and hold what it prints to an answer worked out by hand.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

DARTALGO_LINES: tuple[Passage, ...] = (
    # two pointers and windows
    _s("var lo = 0, hi = nums.length - 1;", "two pointers, one at each end"),
    _s("while (lo < hi && nums[lo] + nums[hi] != target) {", "closing in on a pair"),
    _s("final tmp = nums[lo]; nums[lo] = nums[hi]; nums[hi] = tmp;", "a swap, written out"),
    _s("runSum += values[i] - values[i - k];", "slide: add the new end, drop the old"),
    _s("best = max(best, end - start + 1);", "the widest window so far, from dart:math"),
    _s("final seenAt = <String, int>{};", "a typed map from letter to position"),
    _s("if ((seenAt[ch] ?? -1) >= start) start = seenAt[ch]! + 1;", "a repeat inside the window"),
    # binary search
    _s("final mid = (lo + hi) ~/ 2;", "integer division for the midpoint"),
    _s("if (sorted[mid] == target) return mid;", "found it"),
    _s("if (sorted[mid] < target) { lo = mid + 1; } else { hi = mid - 1; }", "go right or left"),
    # maps, sets, counting
    _s("final index = <int, int>{};", "value to position, for two sum"),
    _s("final want = index[target - nums[i]];", "null when the partner is not there yet"),
    _s("if (want != null) return [want, i];", "the pair, once both are seen"),
    _s("tally[letter] = (tally[letter] ?? 0) + 1;", "counting with a map"),
    _s("counts.update(word, (n) => n + 1, ifAbsent: () => 1);", "the same, with update"),
    _s("final unique = nums.toSet().toList()..sort();", "each value once, in order"),
    _s("final visited = <String>{start};", "a typed set with the start in it"),
    _s("if (visited.add(next)) queue.add(next);", "add returns false if it was there"),
    _s("final key = (word.split('')..sort()).join();", "an anagram's sorted letters"),
    _s("byKey.putIfAbsent(key, () => <String>[]).add(word);", "make the group if missing, then add"),
    # stacks and queues
    _s("final openers = <String>[];", "a list used as a stack"),
    _s("if (openers.isEmpty || openers.removeLast() != closerFor[ch]) return false;", "the wrong closer"),
    _s("while (stack.isNotEmpty && temps[stack.last] < t) {", "a monotonic stack"),
    _s("final queue = Queue<String>()..add(start);", "a queue from dart:collection"),
    _s("final current = queue.removeFirst();", "the oldest in the queue"),
    _s("for (final next in graph[node] ?? const <String>[]) {", "every neighbour, or none"),
    _s("dist[next] = dist[node]! + 1;", "one further than the node it came from"),
    # recursion and memo
    _s("final memo = <int, int>{};", "a cache for a recursive function"),
    _s("int ways(int n) => n <= 1 ? 1 : memo[n] ??= ways(n - 1) + ways(n - 2);",
       "worked out once, then kept, with ??="),
    _s("if (tree == null) return 0;", "the base case of every tree recursion"),
    _s("return 1 + max(depth(node.left), depth(node.right));", "a tree's height"),
    # dynamic programming
    _s("final dp = List<int>.filled(n + 1, 0);", "one slot per subproblem"),
    _s("dp[i] = max(dp[i - 1], dp[i - 2] + houses[i - 1]);", "take it or skip it"),
    _s("final table = List.generate(rows, (_) => List<int>.filled(cols, 0));",
       "a grid with a fresh row each time"),
    _s("final ways = [1, ...List<int>.filled(amount, 0)];", "one way to make nothing"),
    _s("for (var total = coin; total <= amount; total++) {", "every amount this coin helps"),
    _s("combos[sum] += combos[sum - coin];", "the ways of making change"),
    # prefix sums and folds
    _s("final prefix = [0];", "the empty prefix comes first"),
    _s("for (final x in nums) { prefix.add(prefix.last + x); }", "running totals"),
    _s("final rangeSum = prefix[j + 1] - prefix[i];", "any slice's sum in one step"),
    _s("final total = nums.fold<int>(0, (sum, x) => sum + x);", "adding up with fold"),
    _s("final biggest = nums.reduce(max);", "reduce with a function from dart:math"),
    # sorting
    _s("final ordered = [...heights]..sort();", "a sorted copy; ints sort as numbers in Dart"),
    _s("intervals.sort((a, b) => a[0].compareTo(b[0]));", "by start, before merging"),
    _s("people.sort((a, b) => b.score != a.score ? b.score - a.score : a.id - b.id);",
       "high score first, then by id"),
    _s("final top = ([...scores]..sort((a, b) => b - a)).take(3).toList();",
       "the three largest, without touching scores"),
    _s("final sorted = [...names]..sort((a, b) => a.toLowerCase().compareTo(b.toLowerCase()));",
       "sorted the way a person reads"),
    # strings
    _s("final reversed = text.split('').reversed.join();", "a string, backwards"),
    _s("final cleaned = text.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]'), '');",
       "letters and digits only"),
    _s("final code = ch.codeUnitAt(0) - 97;", "a to 0, b to 1 and so on"),
    _s("final letter = String.fromCharCode(97 + (code + shift) % 26);", "a Caesar shift"),
    # bits
    _s("if (n & 1 == 1) odd++;", "the lowest bit says odd"),
    _s("mask &= mask - 1;", "clears the lowest set bit"),
    _s("final single = nums.reduce((a, b) => a ^ b);", "pairs cancel out"),
    _s("final isPowerOfTwo = n > 0 && n & (n - 1) == 0;", "exactly one bit set"),
    # grids
    _s("const dirs = [[1, 0], [-1, 0], [0, 1], [0, -1]];", "the four neighbours"),
    _s("if (row < 0 || col < 0 || row >= rows || col >= cols) return;", "off the edge of the grid"),
    _s("for (final d in dirs) { sink(r + d[0], c + d[1]); }", "spread to each neighbour"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"Dart · {note}")


DARTALGO_BLOCKS: tuple[Passage, ...] = (
    _b("""List<int> twoSum(List<int> nums, int target) {
  final index = <int, int>{};
  for (var i = 0; i < nums.length; i++) {
    final want = index[target - nums[i]];
    if (want != null) return [want, i];
    index[nums[i]] = i;
  }
  return [];
}

void main() => print('${twoSum([2, 7, 11, 15], 9)} ${twoSum([1, 2], 7)}');""",
       "two sum with a map"),
    _b("""int search(List<int> sorted, int target) {
  var lo = 0, hi = sorted.length - 1;
  while (lo <= hi) {
    final mid = (lo + hi) ~/ 2;
    if (sorted[mid] == target) return mid;
    if (sorted[mid] < target) { lo = mid + 1; } else { hi = mid - 1; }
  }
  return -1;
}

void main() => print('${search([1, 3, 5, 7, 9], 1)} ${search([2, 4], 3)}');""",
       "binary search"),
    _b("""bool valid(String text) {
  const closer = {'(': ')', '[': ']', '{': '}'};
  final stack = <String>[];
  for (final ch in text.split('')) {
    if (closer.containsKey(ch)) { stack.add(closer[ch]!); }
    else if (stack.isEmpty || stack.removeLast() != ch) { return false; }
  }
  return stack.isEmpty;
}

void main() => print('${valid('{[()]}')} ${valid('(]')} ${valid('((')}');""",
       "matching brackets with a stack"),
    _b("""void main() {
  final graph = {'a': ['b', 'c'], 'b': ['d'], 'c': ['d'], 'd': <String>[]};
  final dist = {'a': 0}, queue = ['a'];
  for (var head = 0; head < queue.length; head++) {
    final node = queue[head];
    for (final next in graph[node]!.where((n) => !dist.containsKey(n))) {
      dist[next] = dist[node]! + 1;
      queue.add(next);
    }
  }
  print(dist);
}""",
       "breadth-first search for distances"),
    _b("""final memo = <int, int>{};

int climb(int n) => n <= 1 ? 1 : memo[n] ??= climb(n - 1) + climb(n - 2);

void main() {
  print([for (var n = 1; n <= 7; n++) climb(n)].join(' '));
}""",
       "climbing stairs with ??="),
    _b("""import 'dart:math';

int rob(List<int> houses) {
  var take = 0, skip = 0;
  for (final money in houses) {
    final newTake = skip + money;
    skip = max(take, skip);
    take = newTake;
  }
  return max(take, skip);
}

void main() => print('${rob([2, 7, 9, 3, 1])} ${rob([5])} ${rob([])}');""",
       "house robber in two variables"),
    _b("""import 'dart:math';

List<List<int>> merge(List<List<int>> intervals) {
  final merged = <List<int>>[];
  for (final iv in [...intervals]..sort((a, b) => a[0].compareTo(b[0]))) {
    if (merged.isNotEmpty && iv[0] <= merged.last[1]) {
      merged.last[1] = max(merged.last[1], iv[1]);
    } else { merged.add([...iv]); }
  }
  return merged;
}

void main() => print(merge([[1, 3], [8, 10], [2, 6], [9, 12]]));""",
       "merging overlapping intervals"),
    _b("""int coinWays(List<int> coins, int amount) {
  final ways = [1, ...List<int>.filled(amount, 0)];
  for (final coin in coins) {
    for (var total = coin; total <= amount; total++) {
      ways[total] += ways[total - coin];
    }
  }
  return ways[amount];
}

void main() => print('${coinWays([1, 2, 5], 5)} ${coinWays([2], 3)}');""",
       "counting the ways to make change"),
    _b("""void main() {
  final words = ['eat', 'tea', 'tan', 'ate', 'nat', 'bat'];
  final groups = <String, List<String>>{};
  for (final word in words) {
    final key = (word.split('')..sort()).join();
    groups.putIfAbsent(key, () => []).add(word);
  }
  final sorted = groups.values.toList()..sort((a, b) => b.length - a.length);
  print(sorted);
}""",
       "grouping anagrams by sorted letters"),
    _b("""void main() {
  final counts = <String, int>{};
  for (final word in 'the cat and the hat and the bat'.split(' ')) {
    counts.update(word, (n) => n + 1, ifAbsent: () => 1);
  }
  final top = counts.entries.toList()..sort((a, b) => b.value - a.value);
  print('${top.first.key} ${top.first.value} ${counts.length}');
}""",
       "counting words with update"),
)

#: What each block prints, by its note - worked out by hand before Dart was
#: asked, and held to the real run by tests/test_typing_dartalgo.py.
DARTALGO_PRINTS: dict[str, str] = {
    "two sum with a map": "[0, 1] []",
    "binary search": "0 -1",
    "matching brackets with a stack": "true false false",
    "breadth-first search for distances": "{a: 0, b: 1, c: 1, d: 2}",
    "climbing stairs with ??=": "1 2 3 5 8 13 21",
    "house robber in two variables": "12 5 0",
    "merging overlapping intervals": "[[1, 6], [8, 12]]",
    "counting the ways to make change": "4 0",
    "grouping anagrams by sorted letters": "[[eat, tea, ate], [tan, nat], [bat]]",
    "counting words with update": "the 3 5",
}
