"""Every Dart solution is compiled and executed against real cases.

Dart can't share the JavaScript checks the way TypeScript can — `===` isn't a
thing, `console.log` isn't either, and a list compares by identity unless you
turn it into a string. So these are the same assertions written in Dart.

One `dart run` per pattern: its preamble, every solution in it, and the checks.
The source executed is the exact string the student is asked to type.
"""

from __future__ import annotations

import unittest

from code_coach.engine import dart_available, run_code
from code_coach.leetcode.problems_dart import PATTERNS as DART_PATTERNS

PATTERNS_BY_ID = {p.id: p for p in DART_PATTERNS}

# `toString` rather than a deep equality helper: it renders lists and maps
# readably, so a failure says what came back rather than just "not equal".
HARNESS = """
final failed = <String>[];
void eq(String label, Object? got, Object? want) {
  if (got.toString() != want.toString()) {
    failed.add('$label: got $got, want $want');
  }
}
void ok(String label, Object? value) => eq(label, value == true, true);
"""

LIST_HELPERS = """
ListNode? makeList(List<int> vals) {
  ListNode? head;
  for (var i = vals.length - 1; i >= 0; i--) {
    head = ListNode(vals[i], head);
  }
  return head;
}
List<int> readList(ListNode? head) {
  final out = <int>[];
  var node = head;
  while (node != null) {
    out.add(node.val);
    node = node.next;
  }
  return out;
}
"""

TREE_HELPERS = """
TreeNode? makeTree(List<int?> vals) {
  if (vals.isEmpty || vals[0] == null) return null;
  final root = TreeNode(vals[0]!);
  final queue = <TreeNode>[root];
  var i = 1;
  while (queue.isNotEmpty && i < vals.length) {
    final node = queue.removeAt(0);
    if (i < vals.length) {
      if (vals[i] != null) {
        node.left = TreeNode(vals[i]!);
        queue.add(node.left!);
      }
      i++;
    }
    if (i < vals.length) {
      if (vals[i] != null) {
        node.right = TreeNode(vals[i]!);
        queue.add(node.right!);
      }
      i++;
    }
  }
  return root;
}
"""

CHECKS: dict[str, tuple[str, str]] = {
    "lc-hashmap": ("", """
  eq('twoSum', twoSum([2, 7, 11, 15], 9), [0, 1]);
  ok('containsDuplicate', containsDuplicate([1, 2, 3, 1]));
  ok('isAnagram', isAnagram('anagram', 'nagaram'));
  eq('groupAnagrams', groupAnagrams(['eat', 'tea', 'tan']).length, 2);
  eq('fourSumCount', fourSumCount([1, 2], [-2, -1], [-1, 2], [0, 2]), 2);
  eq('subarraySum', subarraySum([1, 1, 1], 2), 2);
  eq('subarraySum negatives', subarraySum([1, -1, 0], 0), 3);
  eq('longestConsecutive', longestConsecutive([100, 4, 200, 1, 3, 2]), 4);
  final blank = List.generate(9, (_) => List.filled(9, '.'));
  ok('isValidSudoku blank', isValidSudoku(blank));
  final dup = List.generate(9, (_) => List.filled(9, '.'));
  dup[0][0] = '5';
  dup[1][1] = '5';
  eq('isValidSudoku box', isValidSudoku(dup), false);
"""),
    "lc-two-pointers": ("", """
  ok('isPalindrome', isPalindrome('A man, a plan, a canal: Panama'));
  eq('twoSumSorted', twoSumSorted([2, 7, 11, 15], 9), [1, 2]);
  eq('maxArea', maxArea([1, 8, 6, 2, 5, 4, 8, 3, 7]), 49);
  eq('threeSum', threeSum([-1, 0, 1, 2, -1, -4]).length, 2);
  final dedup = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4];
  eq('removeDuplicates', removeDuplicates(dedup), 5);
  eq('removeDuplicates front', dedup.sublist(0, 5), [0, 1, 2, 3, 4]);
  eq('moveZeroes', moveZeroes([0, 1, 0, 3, 12]), [1, 3, 12, 0, 0]);
  eq('trap', trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]), 6);
  eq('trap flat', trap([1, 2, 3]), 0);
  eq('sortedSquares', sortedSquares([-4, -1, 0, 3, 10]), [0, 1, 9, 16, 100]);
"""),
    "lc-sliding-window": ("", """
  eq('maxProfit', maxProfit([7, 1, 5, 3, 6, 4]), 5);
  eq('lengthOfLongestSubstring', lengthOfLongestSubstring('abcabcbb'), 3);
  eq('minSubArrayLen', minSubArrayLen(7, [2, 3, 1, 2, 4, 3]), 2);
  eq('characterReplacement', characterReplacement('AABABBA', 1), 4);
  eq('findMaxAverage', findMaxAverage([1, 12, -5, -6, 50, 3], 4), 12.75);
  eq('findMaxAverage negative', findMaxAverage([-1, -2, -3], 2), -1.5);
  ok('checkInclusion', checkInclusion('ab', 'eidbaooo'));
  eq('checkInclusion no', checkInclusion('ab', 'eidboaoo'), false);
  eq('longestOnes', longestOnes([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2), 6);
  eq('minWindow', minWindow('ADOBECODEBANC', 'ABC'), 'BANC');
  eq('minWindow duplicates', minWindow('aa', 'aa'), 'aa');
  eq('minWindow impossible', minWindow('a', 'aa'), '');
"""),
    "lc-stack": ("", """
  ok('isValid', isValid('()[]{}'));
  eq('isValid no', isValid('(]'), false);
  final ms = MinStack();
  ms.push(-2);
  ms.push(0);
  ms.push(-3);
  eq('MinStack min', ms.getMin(), -3);
  ms.pop();
  eq('MinStack min after pop', ms.getMin(), -2);
  eq('evalRPN', evalRPN(['2', '1', '+', '3', '*']), 9);
  eq('dailyTemperatures', dailyTemperatures([73, 74, 75, 71, 69, 72, 76, 73]),
      [1, 1, 4, 2, 1, 1, 0, 0]);
  eq('calPoints', calPoints(['5', '2', 'C', 'D', '+']), 30);
  eq('simplifyPath', simplifyPath('/a/./b/../../c/'), '/c');
  eq('simplifyPath root', simplifyPath('/../'), '/');
  eq('largestRectangleArea', largestRectangleArea([2, 1, 5, 6, 2, 3]), 10);
  eq('decodeString', decodeString('3[a2[c]]'), 'accaccacc');
  eq('decodeString wide', decodeString('12[a]'), 'a' * 12);
"""),
    "lc-linked-list": (LIST_HELPERS, """
  eq('reverseList', readList(reverseList(makeList([1, 2, 3]))), [3, 2, 1]);
  eq('mergeTwoLists',
      readList(mergeTwoLists(makeList([1, 2, 4]), makeList([1, 3, 4]))),
      [1, 1, 2, 3, 4, 4]);
  eq('hasCycle', hasCycle(makeList([1, 2, 3])), false);
  eq('removeNthFromEnd', readList(removeNthFromEnd(makeList([1, 2, 3, 4, 5]), 2)),
      [1, 2, 3, 5]);
  eq('middleNode', middleNode(makeList([1, 2, 3, 4, 5]))!.val, 3);
  eq('middleNode even', middleNode(makeList([1, 2, 3, 4]))!.val, 3);
  eq('deleteDuplicates', readList(deleteDuplicates(makeList([1, 1, 2, 3, 3]))),
      [1, 2, 3]);
  ok('isPalindromeList', isPalindromeList(makeList([1, 2, 2, 1])));
  eq('isPalindromeList no', isPalindromeList(makeList([1, 2])), false);
  eq('addTwoNumbers',
      readList(addTwoNumbers(makeList([2, 4, 3]), makeList([5, 6, 4]))),
      [7, 0, 8]);
  eq('addTwoNumbers carry',
      readList(addTwoNumbers(makeList([9, 9]), makeList([1]))), [0, 0, 1]);
"""),
    "lc-binary-search": ("", """
  eq('search', search([-1, 0, 3, 5, 9, 12], 9), 4);
  eq('searchInsert', searchInsert([1, 3, 5, 6], 5), 2);
  eq('findMin', findMin([3, 4, 5, 1, 2]), 1);
  eq('searchRotated', searchRotated([4, 5, 6, 7, 0, 1, 2], 0), 4);
  eq('minEatingSpeed', minEatingSpeed([3, 6, 7, 11], 8), 4);
  eq('firstBadVersion', firstBadVersion(5, (v) => v >= 4), 4);
  eq('searchRange', searchRange([5, 7, 7, 8, 8, 10], 8), [3, 4]);
  eq('searchRange miss', searchRange([5, 7, 7, 8, 8, 10], 6), [-1, -1]);
  eq('searchRange all', searchRange([2, 2, 2], 2), [0, 2]);
  final mat = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]];
  ok('searchMatrix', searchMatrix(mat, 3));
  eq('searchMatrix miss', searchMatrix(mat, 13), false);
  eq('searchMatrix empty', searchMatrix(<List<int>>[], 1), false);
"""),
    "lc-tree-dfs": (TREE_HELPERS, """
  eq('maxDepth', maxDepth(makeTree([3, 9, 20, null, null, 15, 7])), 3);
  eq('invertTree', invertTree(makeTree([2, 1, 3]))!.left!.val, 3);
  ok('hasPathSum', hasPathSum(makeTree([1, 2, 3]), 3));
  eq('diameterOfBinaryTree', diameterOfBinaryTree(makeTree([1, 2, 3, 4, 5])), 3);
  ok('isValidBST', isValidBST(makeTree([2, 1, 3])));
  ok('isSameTree', isSameTree(makeTree([1, 2, 3]), makeTree([1, 2, 3])));
  eq('isSameTree shape',
      isSameTree(makeTree([1, 2, null]), makeTree([1, null, 2])), false);
  ok('isSymmetric', isSymmetric(makeTree([1, 2, 2, 3, 4, 4, 3])));
  eq('isSymmetric no',
      isSymmetric(makeTree([1, 2, 2, null, 3, null, 3])), false);
  final lca = makeTree([3, 5, 1, 6, 2, 0, 8])!;
  ok('lowestCommonAncestor',
      identical(lowestCommonAncestor(lca, lca.left, lca.right), lca));
  ok('lowestCommonAncestor self',
      identical(lowestCommonAncestor(lca, lca.left, lca.left!.right), lca.left));
"""),
    "lc-tree-bfs": (TREE_HELPERS, """
  eq('levelOrder', levelOrder(makeTree([3, 9, 20, null, null, 15, 7])),
      [[3], [9, 20], [15, 7]]);
  eq('rightSideView', rightSideView(makeTree([1, 2, 3, null, 5, null, 4])),
      [1, 3, 4]);
  eq('zigzagLevelOrder', zigzagLevelOrder(makeTree([3, 9, 20, null, null, 15, 7])),
      [[3], [20, 9], [15, 7]]);
  eq('minDepth', minDepth(makeTree([3, 9, 20, null, null, 15, 7])), 2);
  eq('minDepth spine', minDepth(makeTree([2, null, 3, null, 4, null, 5])), 4);
  eq('averageOfLevels', averageOfLevels(makeTree([3, 9, 20, null, null, 15, 7])),
      [3.0, 14.5, 11.0]);
  eq('largestValues', largestValues(makeTree([1, 3, 2, 5, 3, null, 9])), [1, 3, 9]);
  eq('largestValues negative', largestValues(makeTree([-1, -2, -3])), [-1, -2]);
  eq('maxLevelSum', maxLevelSum(makeTree([1, 7, 0, 7, -8, null, null])), 2);
  eq('maxLevelSum negative',
      maxLevelSum(makeTree([-100, -200, -300, -20, -5, -10, -50])), 3);
  eq('widthOfBinaryTree', widthOfBinaryTree(makeTree([1, 3, 2, 5, 3, null, 9])), 4);
  eq('widthOfBinaryTree sparse',
      widthOfBinaryTree(makeTree([1, 3, 2, 5, null, null, 9])), 4);
"""),
    "lc-graph": ("", """
  eq('floodFill', floodFill([[1, 1, 1], [1, 1, 0], [1, 0, 1]], 1, 1, 2)[0][0], 2);
  eq('numIslands', numIslands([['1', '1', '0'], ['0', '1', '0'], ['0', '0', '1']]), 2);
  eq('orangesRotting', orangesRotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]), 4);
  eq('cloneGraph', cloneGraph(Node(1, [Node(2)]))!.val, 1);
  eq('maxAreaOfIsland',
      maxAreaOfIsland([[0, 0, 1, 0], [0, 1, 1, 0], [0, 0, 0, 0], [1, 1, 0, 0]]), 3);
  eq('findCircleNum', findCircleNum([[1, 1, 0], [1, 1, 0], [0, 0, 1]]), 2);
  eq('findCircleNum all', findCircleNum([[1, 0, 0], [0, 1, 0], [0, 0, 1]]), 3);
  eq('updateMatrix', updateMatrix([[0, 0, 0], [0, 1, 0], [1, 1, 1]]),
      [[0, 0, 0], [0, 1, 0], [1, 2, 1]]);
  eq('pacificAtlantic', pacificAtlantic([[1, 2, 2, 3, 5], [3, 2, 3, 4, 4],
      [2, 4, 5, 3, 1], [6, 7, 1, 4, 5], [5, 1, 1, 2, 4]]),
      [[0, 4], [1, 3], [1, 4], [2, 2], [3, 0], [3, 1], [4, 0]]);
"""),
    "lc-backtracking": ("", """
  eq('subsets', subsets([1, 2, 3]).length, 8);
  eq('subsetsWithDup', subsetsWithDup([1, 2, 2]).length, 6);
  eq('permute', permute([1, 2, 3]).length, 6);
  eq('combinationSum', combinationSum([2, 3, 6, 7], 7).length, 2);
  ok('exist', exist([['A', 'B'], ['C', 'D']], 'ABDC'));
  eq('combine', combine(4, 2), [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]);
  eq('letterCombinations', letterCombinations('23'),
      ['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf']);
  eq('letterCombinations empty', letterCombinations(''), []);
  eq('partition', partition('aab'), [['a', 'a', 'b'], ['aa', 'b']]);
  eq('partition triple', partition('aaa').length, 4);
"""),
    "lc-heap": ("", """
  eq('findKthLargest', findKthLargest([3, 2, 1, 5, 6, 4], 2), 5);
  eq('topKFrequent', topKFrequent([1, 1, 1, 2, 2, 3], 2), [1, 2]);
  eq('kClosest', kClosest([[1, 3], [-2, 2]], 1), [[-2, 2]]);
  eq('lastStoneWeight', lastStoneWeight([2, 7, 4, 1, 8, 1]), 1);
  eq('lastStoneWeight pair', lastStoneWeight([2, 2]), 0);
  eq('lastStoneWeight one', lastStoneWeight([3]), 3);
  eq('topKFrequentWords',
      topKFrequentWords(['i', 'love', 'leetcode', 'i', 'love', 'coding'], 2),
      ['i', 'love']);
  eq('topKFrequentWords ties', topKFrequentWords(['b', 'a', 'c'], 3),
      ['a', 'b', 'c']);
  eq('frequencySort', frequencySort('cccaaa'), 'aaaccc');
  eq('kthSmallest', kthSmallest([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8), 13);
  final ro = reorganizeString('aab');
  eq('reorganizeString length', ro.length, 3);
  eq('reorganizeString impossible', reorganizeString('aaab'), '');
  eq('reorganizeString one', reorganizeString('a'), 'a');
"""),
    "lc-topological": ("", """
  ok('canFinish', canFinish(2, [[1, 0]]));
  eq('canFinish cycle', canFinish(2, [[1, 0], [0, 1]]), false);
  eq('findOrder', findOrder(2, [[1, 0]]), [0, 1]);
  eq('findMinHeightTrees', findMinHeightTrees(4, [[1, 0], [1, 2], [1, 3]]), [1]);
  eq('eventualSafeNodes', eventualSafeNodes([[1, 2], [2, 3], [5], [0], [5], [], []]),
      [2, 4, 5, 6]);
  eq('checkIfPrerequisite', checkIfPrerequisite(2, [[1, 0]], [[0, 1], [1, 0]]),
      [false, true]);
  eq('checkIfPrerequisite transitive',
      checkIfPrerequisite(3, [[0, 1], [1, 2]], [[0, 2]]), [true]);
  eq('findAllRecipes',
      findAllRecipes(['bread'], [['yeast', 'flour']], ['yeast', 'flour', 'corn']),
      ['bread']);
  eq('findAllRecipes short',
      findAllRecipes(['bread'], [['yeast', 'flour']], ['yeast']), []);
  eq('minimumSemesters', minimumSemesters(3, [[1, 3], [2, 3]]), 2);
  eq('minimumSemesters cycle', minimumSemesters(3, [[1, 2], [2, 3], [3, 1]]), -1);
  eq('alienOrder', alienOrder(['wrt', 'wrf', 'er', 'ett', 'rftt']), 'wertf');
  eq('alienOrder cycle', alienOrder(['z', 'x', 'z']), '');
  eq('alienOrder prefix', alienOrder(['abc', 'ab']), '');
"""),
    "lc-dp": ("", """
  eq('climbStairs', climbStairs(5), 8);
  eq('rob', rob([2, 7, 9, 3, 1]), 12);
  eq('coinChange', coinChange([1, 2, 5], 11), 3);
  eq('lengthOfLIS', lengthOfLIS([10, 9, 2, 5, 3, 7, 101, 18]), 4);
  eq('minCostClimbingStairs', minCostClimbingStairs([10, 15, 20]), 15);
  eq('minCostClimbingStairs long',
      minCostClimbingStairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1]), 6);
  eq('longestCommonSubsequence', longestCommonSubsequence('abcde', 'ace'), 3);
  eq('longestCommonSubsequence none', longestCommonSubsequence('abc', 'def'), 0);
  ok('wordBreak', wordBreak('leetcode', ['leet', 'code']));
  eq('wordBreak no', wordBreak('catsandog', ['cats', 'dog', 'sand', 'and', 'cat']),
      false);
  eq('maxProduct', maxProduct([2, 3, -2, 4]), 6);
  eq('maxProduct zero', maxProduct([-2, 0, -1]), 0);
  eq('maxProduct two negatives', maxProduct([-2, 3, -4]), 24);
"""),
}


@unittest.skipUnless(dart_available(), "needs the Dart SDK on PATH")
class DartSolutionTests(unittest.TestCase):
    def _run(self, pattern_id: str) -> None:
        pattern = PATTERNS_BY_ID[pattern_id]
        helpers, checks = CHECKS[pattern_id]
        # Dart rejects a directive that follows a declaration, so the
        # preamble's imports have to stay at the top of the file.
        parts = list(pattern.preamble) + [p.code for p in pattern.problems]
        src = "\n\n".join(parts)
        body = f"void main() {{\n{checks}\n" + (
            "  print(failed.isEmpty ? '' : failed.join('\\n'));\n}\n"
        )
        out, err, code = run_code(
            f"{src}\n{helpers}\n{HARNESS}\n{body}", language="dart"
        )
        self.assertEqual(code, 0, f"{pattern_id}\n{out[:900]}\n{err[:800]}")
        self.assertEqual(out.strip(), "", f"{pattern_id}: {out}")

    def test_every_pattern_is_covered(self) -> None:
        self.assertEqual(sorted(CHECKS), sorted(PATTERNS_BY_ID))


def _make(pattern_id: str):
    def test(self):
        self._run(pattern_id)

    test.__doc__ = f"Every solution in {pattern_id} compiles, runs, answers."
    return test


for _pid in CHECKS:
    setattr(DartSolutionTests, f"test_{_pid.replace('-', '_')}", _make(_pid))


if __name__ == "__main__":
    unittest.main()
