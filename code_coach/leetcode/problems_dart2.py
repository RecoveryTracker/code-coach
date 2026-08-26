"""Dart solutions, patterns 5–13. Continues `problems_dart`."""

from __future__ import annotations

from code_coach.leetcode.dart_common import (
    COLLECTION,
    GRAPH_NODE,
    LIST_NODE,
    TREE_NODE,
    _p,
)
from code_coach.leetcode.problems import Pattern

# ── 5. Linked lists ─────────────────────────────────────────

_LINKED_LIST = Pattern(
    id="lc-linked-list",
    name="Linked Lists",
    order=5,
    blurb="Rewire pointers one node at a time, holding on to what's next.",
    tell="You're asked to reverse, merge, or find a position in a chain.",
    preamble=(LIST_NODE,),
    problems=(
        _p(
            206, "Reverse Linked List", "Easy",
            "Flip each link backwards, remembering the next node before you lose it.",
            "O(n) time, O(1) space",
            """
            ListNode? reverseList(ListNode? head) {
              ListNode? prev;
              var cur = head;
              while (cur != null) {
                final nxt = cur.next;
                cur.next = prev;
                prev = cur;
                cur = nxt;
              }
              return prev;
            }
            """,
        ),
        _p(
            21, "Merge Two Sorted Lists", "Easy",
            "A dummy head saves you from special-casing the first node.",
            "O(n + m) time, O(1) space",
            """
            ListNode? mergeTwoLists(ListNode? list1, ListNode? list2) {
              final dummy = ListNode(0);
              var tail = dummy;
              var a = list1;
              var b = list2;
              while (a != null && b != null) {
                if (a.val <= b.val) {
                  tail.next = a;
                  a = a.next;
                } else {
                  tail.next = b;
                  b = b.next;
                }
                tail = tail.next!;
              }
              tail.next = a ?? b;
              return dummy.next;
            }
            """,
        ),
        _p(
            141, "Linked List Cycle", "Easy",
            "A fast pointer laps a slow one only if the track loops.",
            "O(n) time, O(1) space",
            """
            bool hasCycle(ListNode? head) {
              var slow = head;
              var fast = head;
              while (fast != null && fast.next != null) {
                slow = slow!.next;
                fast = fast.next!.next;
                if (identical(slow, fast)) return true;
              }
              return false;
            }
            """,
        ),
        _p(
            19, "Remove Nth Node From End", "Medium",
            "Send one pointer n ahead; when it lands, the other is at the gap.",
            "O(n) time, O(1) space",
            """
            ListNode? removeNthFromEnd(ListNode? head, int n) {
              final dummy = ListNode(0, head);
              var lead = dummy;
              var trail = dummy;
              for (var i = 0; i < n; i++) {
                lead = lead.next!;
              }
              while (lead.next != null) {
                lead = lead.next!;
                trail = trail.next!;
              }
              trail.next = trail.next!.next;
              return dummy.next;
            }
            """,
        ),
        _p(
            876, 'Middle of the Linked List', 'Easy',
            "One pointer takes two steps per the other's one, so it ends at twice the distance.",
            'O(n) time, O(1) space',
            """
            ListNode? middleNode(ListNode? head) {
              var slow = head;
              var fast = head;
              while (fast != null && fast.next != null) {
                slow = slow!.next;
                fast = fast.next!.next;
              }
              return slow;
            }
            """,
        ),
        _p(
            83, 'Remove Duplicates from Sorted List', 'Easy',
            'Sorted means duplicates are neighbours, so one pass and a skipped link does it.',
            'O(n) time, O(1) space',
            """
            ListNode? deleteDuplicates(ListNode? head) {
              var node = head;
              while (node != null && node.next != null) {
                if (node.val == node.next!.val) {
                  node.next = node.next!.next;
                } else {
                  node = node.next;
                }
              }
              return head;
            }
            """,
        ),
        _p(
            234, 'Palindrome Linked List', 'Easy',
            'Find the middle, reverse the second half, then walk the two halves together.',
            'O(n) time, O(1) space',
            """
            bool isPalindromeList(ListNode? head) {
              var slow = head;
              var fast = head;
              while (fast != null && fast.next != null) {
                slow = slow!.next;
                fast = fast.next!.next;
              }
              ListNode? second;
              while (slow != null) {
                final next = slow.next;
                slow.next = second;
                second = slow;
                slow = next;
              }
              var first = head;
              while (second != null) {
                if (first!.val != second.val) return false;
                first = first.next;
                second = second.next;
              }
              return true;
            }
            """,
        ),
        _p(
            2, 'Add Two Numbers', 'Medium',
            'Long addition, digit by digit. The carry is the only thing you have to remember.',
            'O(n) time, O(n) space',
            """
            ListNode? addTwoNumbers(ListNode? first, ListNode? second) {
              final head = ListNode(0);
              var node = head;
              var carry = 0;
              while (first != null || second != null || carry != 0) {
                var total = carry;
                if (first != null) {
                  total += first.val;
                  first = first.next;
                }
                if (second != null) {
                  total += second.val;
                  second = second.next;
                }
                carry = total ~/ 10;
                node.next = ListNode(total % 10);
                node = node.next!;
              }
              return head.next;
            }
            """,
        ),
    ),
)


# ── 6. Binary search ────────────────────────────────────────

_BINARY_SEARCH = Pattern(
    id="lc-binary-search",
    name="Binary Search",
    order=6,
    blurb="Halve the search space every step.",
    tell="The data is sorted, or the answer is a number you can test.",
    problems=(
        _p(
            704, "Binary Search", "Easy",
            "Compare the middle, then throw away the half that can't hold it.",
            "O(log n) time, O(1) space",
            """
            int search(List<int> nums, int target) {
              var lo = 0;
              var hi = nums.length - 1;
              while (lo <= hi) {
                final mid = lo + (hi - lo) ~/ 2;
                if (nums[mid] == target) return mid;
                if (nums[mid] < target) {
                  lo = mid + 1;
                } else {
                  hi = mid - 1;
                }
              }
              return -1;
            }
            """,
        ),
        _p(
            35, "Search Insert Position", "Easy",
            "When the loop ends, lo is exactly where the value belongs.",
            "O(log n) time, O(1) space",
            """
            int searchInsert(List<int> nums, int target) {
              var lo = 0;
              var hi = nums.length - 1;
              while (lo <= hi) {
                final mid = lo + (hi - lo) ~/ 2;
                if (nums[mid] == target) return mid;
                if (nums[mid] < target) {
                  lo = mid + 1;
                } else {
                  hi = mid - 1;
                }
              }
              return lo;
            }
            """,
        ),
        _p(
            153, "Find Minimum in Rotated Sorted Array", "Medium",
            "If the middle is above the right end, the dip is to its right.",
            "O(log n) time, O(1) space",
            """
            int findMin(List<int> nums) {
              var lo = 0;
              var hi = nums.length - 1;
              while (lo < hi) {
                final mid = lo + (hi - lo) ~/ 2;
                if (nums[mid] > nums[hi]) {
                  lo = mid + 1;
                } else {
                  hi = mid;
                }
              }
              return nums[lo];
            }
            """,
        ),
        _p(
            33, "Search in Rotated Sorted Array", "Medium",
            "One half is always properly sorted — work out which, then decide.",
            "O(log n) time, O(1) space",
            """
            int searchRotated(List<int> nums, int target) {
              var lo = 0;
              var hi = nums.length - 1;
              while (lo <= hi) {
                final mid = lo + (hi - lo) ~/ 2;
                if (nums[mid] == target) return mid;
                if (nums[lo] <= nums[mid]) {
                  if (nums[lo] <= target && target < nums[mid]) {
                    hi = mid - 1;
                  } else {
                    lo = mid + 1;
                  }
                } else {
                  if (nums[mid] < target && target <= nums[hi]) {
                    lo = mid + 1;
                  } else {
                    hi = mid - 1;
                  }
                }
              }
              return -1;
            }
            """,
        ),
        _p(
            875, "Koko Eating Bananas", "Medium",
            "Binary search the answer: speeds are sorted even when the data isn't.",
            "O(n log max) time, O(1) space",
            """
            int minEatingSpeed(List<int> piles, int h) {
              var lo = 1;
              var hi = piles.reduce((a, b) => a > b ? a : b);
              while (lo < hi) {
                final speed = lo + (hi - lo) ~/ 2;
                var hours = 0;
                for (final pile in piles) {
                  hours += (pile + speed - 1) ~/ speed;
                }
                if (hours <= h) {
                  hi = speed;
                } else {
                  lo = speed + 1;
                }
              }
              return lo;
            }
            """,
        ),
        _p(
            278, 'First Bad Version', 'Easy',
            "Search for a boundary: keep the mid when it's bad, discard it when it isn't.",
            'O(log n) time, O(1) space',
            """
            int firstBadVersion(int n, bool Function(int) isBad) {
              var low = 1;
              var high = n;
              while (low < high) {
                final mid = (low + high) ~/ 2;
                if (isBad(mid)) {
                  high = mid;
                } else {
                  low = mid + 1;
                }
              }
              return low;
            }
            """,
        ),
        _p(
            34, 'Find First and Last Position of Element in Sorted Array', 'Medium',
            'Two searches, not one: the same loop finds the left edge and then the right.',
            'O(log n) time, O(1) space',
            """
            List<int> searchRange(List<int> nums, int target) {
              int edge(bool first) {
                var low = 0;
                var high = nums.length - 1;
                var found = -1;
                while (low <= high) {
                  final mid = (low + high) ~/ 2;
                  if (nums[mid] == target) {
                    found = mid;
                    if (first) {
                      high = mid - 1;
                    } else {
                      low = mid + 1;
                    }
                  } else if (nums[mid] < target) {
                    low = mid + 1;
                  } else {
                    high = mid - 1;
                  }
                }
                return found;
              }

              return [edge(true), edge(false)];
            }
            """,
        ),
        _p(
            74, 'Search a 2D Matrix', 'Medium',
            'A sorted matrix is one sorted list folded up, so divide the index to unfold it.',
            'O(log(m * n)) time, O(1) space',
            """
            bool searchMatrix(List<List<int>> matrix, int target) {
              if (matrix.isEmpty || matrix[0].isEmpty) return false;
              final rows = matrix.length;
              final cols = matrix[0].length;
              var low = 0;
              var high = rows * cols - 1;
              while (low <= high) {
                final mid = (low + high) ~/ 2;
                final value = matrix[mid ~/ cols][mid % cols];
                if (value == target) return true;
                if (value < target) {
                  low = mid + 1;
                } else {
                  high = mid - 1;
                }
              }
              return false;
            }
            """,
        ),
    ),
)


# ── 7. Tree DFS ─────────────────────────────────────────────

_TREE_DFS = Pattern(
    id="lc-tree-dfs",
    name="Tree DFS",
    order=7,
    blurb="Solve a node by asking its children the same question.",
    tell="The answer for a node depends on its subtrees.",
    preamble=(TREE_NODE,),
    problems=(
        _p(
            104, "Maximum Depth of Binary Tree", "Easy",
            "A node's depth is one more than its deeper child.",
            "O(n) time, O(h) space",
            """
            int maxDepth(TreeNode? root) {
              if (root == null) return 0;
              final left = maxDepth(root.left);
              final right = maxDepth(root.right);
              return 1 + (left > right ? left : right);
            }
            """,
        ),
        _p(
            226, "Invert Binary Tree", "Easy",
            "Swap the two children, then tell each of them to do the same.",
            "O(n) time, O(h) space",
            """
            TreeNode? invertTree(TreeNode? root) {
              if (root == null) return null;
              final temp = root.left;
              root.left = root.right;
              root.right = temp;
              invertTree(root.left);
              invertTree(root.right);
              return root;
            }
            """,
        ),
        _p(
            112, "Path Sum", "Easy",
            "Spend the target as you descend; a leaf must land on exactly zero.",
            "O(n) time, O(h) space",
            """
            bool hasPathSum(TreeNode? root, int targetSum) {
              if (root == null) return false;
              final left = targetSum - root.val;
              if (root.left == null && root.right == null) return left == 0;
              return hasPathSum(root.left, left) || hasPathSum(root.right, left);
            }
            """,
        ),
        _p(
            543, "Diameter of Binary Tree", "Easy",
            "The longest path through a node is its two child depths added.",
            "O(n) time, O(h) space",
            """
            int diameterOfBinaryTree(TreeNode? root) {
              var best = 0;

              int depth(TreeNode? node) {
                if (node == null) return 0;
                final left = depth(node.left);
                final right = depth(node.right);
                if (left + right > best) best = left + right;
                return 1 + (left > right ? left : right);
              }

              depth(root);
              return best;
            }
            """,
        ),
        _p(
            98, "Validate Binary Search Tree", "Medium",
            "Carry the allowed range down; each node narrows it for its children.",
            "O(n) time, O(h) space",
            """
            bool isValidBST(TreeNode? root, [int? low, int? high]) {
              if (root == null) return true;
              if (low != null && root.val <= low) return false;
              if (high != null && root.val >= high) return false;
              return isValidBST(root.left, low, root.val) &&
                  isValidBST(root.right, root.val, high);
            }
            """,
        ),
        _p(
            100, 'Same Tree', 'Easy',
            'Two trees match when their roots match and both pairs of children do.',
            'O(n) time, O(h) space',
            """
            bool isSameTree(TreeNode? first, TreeNode? second) {
              if (first == null && second == null) return true;
              if (first == null || second == null) return false;
              if (first.val != second.val) return false;
              return isSameTree(first.left, second.left) &&
                  isSameTree(first.right, second.right);
            }
            """,
        ),
        _p(
            101, 'Symmetric Tree', 'Easy',
            'A mirror compares left against right — the recursion crosses over.',
            'O(n) time, O(h) space',
            """
            bool isSymmetric(TreeNode? root) {
              bool mirror(TreeNode? left, TreeNode? right) {
                if (left == null && right == null) return true;
                if (left == null || right == null) return false;
                if (left.val != right.val) return false;
                return mirror(left.left, right.right) && mirror(left.right, right.left);
              }

              return mirror(root, root);
            }
            """,
        ),
        _p(
            236, 'Lowest Common Ancestor of a Binary Tree', 'Medium',
            'A node whose two sides each found something is the meeting point.',
            'O(n) time, O(h) space',
            """
            TreeNode? lowestCommonAncestor(TreeNode? root, TreeNode? p, TreeNode? q) {
              if (root == null || identical(root, p) || identical(root, q)) return root;
              final left = lowestCommonAncestor(root.left, p, q);
              final right = lowestCommonAncestor(root.right, p, q);
              if (left != null && right != null) return root;
              return left ?? right;
            }
            """,
        ),
    ),
)


# ── 8. Tree BFS ─────────────────────────────────────────────

_TREE_BFS = Pattern(
    id="lc-tree-bfs",
    name="Tree BFS",
    order=8,
    blurb="Walk the tree a level at a time using a queue.",
    tell="The question mentions levels, rows, or the shallowest anything.",
    # Import first: Dart rejects a directive that follows a declaration, and
    # these preamble blocks are typed in this order.
    preamble=(COLLECTION, TREE_NODE),
    problems=(
        _p(
            102, "Binary Tree Level Order Traversal", "Medium",
            "Drain exactly one level per round, queueing the next as you go.",
            "O(n) time, O(n) space",
            """
            List<List<int>> levelOrder(TreeNode? root) {
              final out = <List<int>>[];
              if (root == null) return out;
              final queue = Queue<TreeNode>()..add(root);
              while (queue.isNotEmpty) {
                final level = <int>[];
                for (var i = queue.length; i > 0; i--) {
                  final node = queue.removeFirst();
                  level.add(node.val);
                  if (node.left != null) queue.add(node.left!);
                  if (node.right != null) queue.add(node.right!);
                }
                out.add(level);
              }
              return out;
            }
            """,
        ),
        _p(
            199, "Binary Tree Right Side View", "Medium",
            "From each level, keep only the last node you popped.",
            "O(n) time, O(n) space",
            """
            List<int> rightSideView(TreeNode? root) {
              final out = <int>[];
              if (root == null) return out;
              final queue = Queue<TreeNode>()..add(root);
              while (queue.isNotEmpty) {
                var last = 0;
                for (var i = queue.length; i > 0; i--) {
                  final node = queue.removeFirst();
                  last = node.val;
                  if (node.left != null) queue.add(node.left!);
                  if (node.right != null) queue.add(node.right!);
                }
                out.add(last);
              }
              return out;
            }
            """,
        ),
        _p(
            103, "Binary Tree Zigzag Level Order", "Medium",
            "Same level walk — just reverse every other row before storing it.",
            "O(n) time, O(n) space",
            """
            List<List<int>> zigzagLevelOrder(TreeNode? root) {
              final out = <List<int>>[];
              if (root == null) return out;
              final queue = Queue<TreeNode>()..add(root);
              var leftToRight = true;
              while (queue.isNotEmpty) {
                final level = <int>[];
                for (var i = queue.length; i > 0; i--) {
                  final node = queue.removeFirst();
                  level.add(node.val);
                  if (node.left != null) queue.add(node.left!);
                  if (node.right != null) queue.add(node.right!);
                }
                out.add(leftToRight ? level : level.reversed.toList());
                leftToRight = !leftToRight;
              }
              return out;
            }
            """,
        ),
        _p(
            111, 'Minimum Depth of Binary Tree', 'Easy',
            'BFS stops at the first leaf it meets — DFS would walk the whole tree first.',
            'O(n) time, O(n) space',
            """
            int minDepth(TreeNode? root) {
              if (root == null) return 0;
              final queue = Queue<TreeNode>()..add(root);
              var depth = 1;
              while (queue.isNotEmpty) {
                for (var i = queue.length; i > 0; i--) {
                  final node = queue.removeFirst();
                  if (node.left == null && node.right == null) return depth;
                  if (node.left != null) queue.add(node.left!);
                  if (node.right != null) queue.add(node.right!);
                }
                depth++;
              }
              return depth;
            }
            """,
        ),
        _p(
            637, 'Average of Levels in Binary Tree', 'Easy',
            "One row at a time, so the divisor is just that row's length.",
            'O(n) time, O(n) space',
            """
            List<double> averageOfLevels(TreeNode? root) {
              final averages = <double>[];
              if (root == null) return averages;
              final queue = Queue<TreeNode>()..add(root);
              while (queue.isNotEmpty) {
                final size = queue.length;
                var total = 0;
                for (var i = size; i > 0; i--) {
                  final node = queue.removeFirst();
                  total += node.val;
                  if (node.left != null) queue.add(node.left!);
                  if (node.right != null) queue.add(node.right!);
                }
                averages.add(total / size);
              }
              return averages;
            }
            """,
        ),
        _p(
            515, 'Find Largest Value in Each Tree Row', 'Medium',
            'Same row walk as the average — swap the running total for a running max.',
            'O(n) time, O(n) space',
            """
            List<int> largestValues(TreeNode? root) {
              final largest = <int>[];
              if (root == null) return largest;
              final queue = Queue<TreeNode>()..add(root);
              while (queue.isNotEmpty) {
                int? best;
                for (var i = queue.length; i > 0; i--) {
                  final node = queue.removeFirst();
                  if (best == null || node.val > best) best = node.val;
                  if (node.left != null) queue.add(node.left!);
                  if (node.right != null) queue.add(node.right!);
                }
                largest.add(best!);
              }
              return largest;
            }
            """,
        ),
        _p(
            1161, 'Maximum Level Sum of a Binary Tree', 'Medium',
            'Number the levels as you go and keep the best — ties go to the shallower one.',
            'O(n) time, O(n) space',
            """
            int maxLevelSum(TreeNode? root) {
              if (root == null) return 0;
              final queue = Queue<TreeNode>()..add(root);
              var level = 0;
              var bestLevel = 1;
              int? bestSum;
              while (queue.isNotEmpty) {
                level++;
                var total = 0;
                for (var i = queue.length; i > 0; i--) {
                  final node = queue.removeFirst();
                  total += node.val;
                  if (node.left != null) queue.add(node.left!);
                  if (node.right != null) queue.add(node.right!);
                }
                if (bestSum == null || total > bestSum) {
                  bestSum = total;
                  bestLevel = level;
                }
              }
              return bestLevel;
            }
            """,
        ),
        _p(
            662, 'Maximum Width of Binary Tree', 'Medium',
            "Queue the heap index with each node; a row's width is last minus first plus one.",
            'O(n) time, O(n) space',
            """
            int widthOfBinaryTree(TreeNode? root) {
              if (root == null) return 0;
              var widest = 0;
              var queue = <MapEntry<TreeNode, int>>[MapEntry(root, 0)];
              while (queue.isNotEmpty) {
                final first = queue.first.value;
                var last = first;
                final next = <MapEntry<TreeNode, int>>[];
                for (final pair in queue) {
                  last = pair.value;
                  if (pair.key.left != null) {
                    next.add(MapEntry(pair.key.left!, pair.value * 2));
                  }
                  if (pair.key.right != null) {
                    next.add(MapEntry(pair.key.right!, pair.value * 2 + 1));
                  }
                }
                if (last - first + 1 > widest) widest = last - first + 1;
                queue = next;
              }
              return widest;
            }
            """,
        ),
    ),
)


# ── 9. Graphs & grids ───────────────────────────────────────

_GRAPH = Pattern(
    id="lc-graph",
    name="Graphs & Grids",
    order=9,
    blurb="A grid is a graph; neighbours are the cells beside you.",
    tell="Islands, regions, flood fill, shortest hops.",
    preamble=(COLLECTION, GRAPH_NODE),
    problems=(
        _p(
            733, "Flood Fill", "Easy",
            "Repaint outward from the start while the colour still matches.",
            "O(m·n) time, O(m·n) space",
            """
            List<List<int>> floodFill(List<List<int>> image, int sr, int sc, int color) {
              final start = image[sr][sc];
              if (start == color) return image;
              final rows = image.length;
              final cols = image[0].length;

              void fill(int r, int c) {
                if (r < 0 || r >= rows || c < 0 || c >= cols) return;
                if (image[r][c] != start) return;
                image[r][c] = color;
                fill(r + 1, c);
                fill(r - 1, c);
                fill(r, c + 1);
                fill(r, c - 1);
              }

              fill(sr, sc);
              return image;
            }
            """,
        ),
        _p(
            200, "Number of Islands", "Medium",
            "Every unvisited land cell starts one island; sink the rest of it.",
            "O(m·n) time, O(m·n) space",
            """
            int numIslands(List<List<String>> grid) {
              if (grid.isEmpty) return 0;
              final rows = grid.length;
              final cols = grid[0].length;
              var count = 0;

              void sink(int r, int c) {
                if (r < 0 || r >= rows || c < 0 || c >= cols) return;
                if (grid[r][c] != '1') return;
                grid[r][c] = '0';
                sink(r + 1, c);
                sink(r - 1, c);
                sink(r, c + 1);
                sink(r, c - 1);
              }

              for (var r = 0; r < rows; r++) {
                for (var c = 0; c < cols; c++) {
                  if (grid[r][c] == '1') {
                    count++;
                    sink(r, c);
                  }
                }
              }
              return count;
            }
            """,
        ),
        _p(
            994, "Rotting Oranges", "Medium",
            "Rot spreads a ring per minute — that's BFS from every rotten cell at once.",
            "O(m·n) time, O(m·n) space",
            """
            int orangesRotting(List<List<int>> grid) {
              final rows = grid.length;
              final cols = grid[0].length;
              final queue = Queue<List<int>>();
              var fresh = 0;
              for (var r = 0; r < rows; r++) {
                for (var c = 0; c < cols; c++) {
                  if (grid[r][c] == 2) queue.add([r, c]);
                  if (grid[r][c] == 1) fresh++;
                }
              }
              if (fresh == 0) return 0;
              var minutes = 0;
              const steps = [[1, 0], [-1, 0], [0, 1], [0, -1]];
              while (queue.isNotEmpty && fresh > 0) {
                minutes++;
                for (var i = queue.length; i > 0; i--) {
                  final cell = queue.removeFirst();
                  for (final step in steps) {
                    final r = cell[0] + step[0];
                    final c = cell[1] + step[1];
                    if (r < 0 || r >= rows || c < 0 || c >= cols) continue;
                    if (grid[r][c] != 1) continue;
                    grid[r][c] = 2;
                    fresh--;
                    queue.add([r, c]);
                  }
                }
              }
              return fresh == 0 ? minutes : -1;
            }
            """,
        ),
        _p(
            133, "Clone Graph", "Medium",
            "Keep a map from old node to new so a cycle doesn't loop forever.",
            "O(n) time, O(n) space",
            """
            Node? cloneGraph(Node? node, [Map<Node, Node>? made]) {
              if (node == null) return null;
              made ??= <Node, Node>{};
              final existing = made[node];
              if (existing != null) return existing;
              final copy = Node(node.val);
              made[node] = copy;
              for (final neighbor in node.neighbors) {
                copy.neighbors.add(cloneGraph(neighbor, made)!);
              }
              return copy;
            }
            """,
        ),
        _p(
            695, 'Max Area of Island', 'Medium',
            'Same flood fill, but the walk returns a size instead of just marking cells.',
            'O(m * n) time, O(m * n) space',
            """
            int maxAreaOfIsland(List<List<int>> grid) {
              if (grid.isEmpty) return 0;
              final rows = grid.length;
              final cols = grid[0].length;
              int fill(int r, int c) {
                if (r < 0 || c < 0 || r >= rows || c >= cols) return 0;
                if (grid[r][c] != 1) return 0;
                grid[r][c] = 0;
                return 1 + fill(r + 1, c) + fill(r - 1, c) + fill(r, c + 1) + fill(r, c - 1);
              }

              var best = 0;
              for (var r = 0; r < rows; r++) {
                for (var c = 0; c < cols; c++) {
                  final area = fill(r, c);
                  if (area > best) best = area;
                }
              }
              return best;
            }
            """,
        ),
        _p(
            547, 'Number of Provinces', 'Medium',
            'Every walk that starts somewhere unvisited is one more connected group.',
            'O(n * n) time, O(n) space',
            """
            int findCircleNum(List<List<int>> isConnected) {
              final n = isConnected.length;
              final seen = <int>{};
              void visit(int city) {
                seen.add(city);
                for (var other = 0; other < n; other++) {
                  if (isConnected[city][other] == 1 && !seen.contains(other)) visit(other);
                }
              }

              var groups = 0;
              for (var city = 0; city < n; city++) {
                if (!seen.contains(city)) {
                  visit(city);
                  groups++;
                }
              }
              return groups;
            }
            """,
        ),
        _p(
            542, '01 Matrix', 'Medium',
            'Start the queue from every zero at once, and the first visit is the nearest one.',
            'O(m * n) time, O(m * n) space',
            """
            List<List<int>> updateMatrix(List<List<int>> mat) {
              final rows = mat.length;
              final cols = mat[0].length;
              final out = List.generate(rows, (_) => List.filled(cols, -1));
              final queue = Queue<List<int>>();
              for (var r = 0; r < rows; r++) {
                for (var c = 0; c < cols; c++) {
                  if (mat[r][c] == 0) {
                    out[r][c] = 0;
                    queue.add([r, c]);
                  }
                }
              }
              const steps = [[1, 0], [-1, 0], [0, 1], [0, -1]];
              while (queue.isNotEmpty) {
                final cell = queue.removeFirst();
                for (final step in steps) {
                  final nr = cell[0] + step[0];
                  final nc = cell[1] + step[1];
                  if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && out[nr][nc] == -1) {
                    out[nr][nc] = out[cell[0]][cell[1]] + 1;
                    queue.add([nr, nc]);
                  }
                }
              }
              return out;
            }
            """,
        ),
        _p(
            417, 'Pacific Atlantic Water Flow', 'Medium',
            'Walk uphill from each ocean instead of downhill from each cell; the answer is the overlap.',
            'O(m * n) time, O(m * n) space',
            """
            List<List<int>> pacificAtlantic(List<List<int>> heights) {
              if (heights.isEmpty) return [];
              final rows = heights.length;
              final cols = heights[0].length;
              final pacific = <String>{};
              final atlantic = <String>{};
              const steps = [[1, 0], [-1, 0], [0, 1], [0, -1]];
              void climb(int r, int c, Set<String> seen) {
                seen.add('$r,$c');
                for (final step in steps) {
                  final nr = r + step[0];
                  final nc = c + step[1];
                  if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
                    if (!seen.contains('$nr,$nc') && heights[nr][nc] >= heights[r][c]) {
                      climb(nr, nc, seen);
                    }
                  }
                }
              }

              for (var c = 0; c < cols; c++) {
                climb(0, c, pacific);
                climb(rows - 1, c, atlantic);
              }
              for (var r = 0; r < rows; r++) {
                climb(r, 0, pacific);
                climb(r, cols - 1, atlantic);
              }
              final both = <List<int>>[];
              for (final cell in pacific) {
                if (atlantic.contains(cell)) {
                  both.add(cell.split(',').map(int.parse).toList());
                }
              }
              both.sort((a, b) => a[0] != b[0] ? a[0] - b[0] : a[1] - b[1]);
              return both;
            }
            """,
        ),
    ),
)


# ── 10. Subsets & backtracking ──────────────────────────────

_SUBSETS = Pattern(
    id="lc-backtracking",
    name="Subsets & Backtracking",
    order=10,
    blurb="Choose, explore, then un-choose.",
    tell="You need every combination, permutation, or arrangement.",
    problems=(
        _p(
            78, "Subsets", "Medium",
            "For each item: take it or don't, then undo the choice.",
            "O(n·2ⁿ) time, O(n) depth",
            """
            List<List<int>> subsets(List<int> nums) {
              final out = <List<int>>[];
              final current = <int>[];

              void backtrack(int start) {
                out.add(List<int>.from(current));
                for (var i = start; i < nums.length; i++) {
                  current.add(nums[i]);
                  backtrack(i + 1);
                  current.removeLast();
                }
              }

              backtrack(0);
              return out;
            }
            """,
        ),
        _p(
            90, "Subsets II", "Medium",
            "Sort first, then skip a duplicate unless it follows its twin.",
            "O(n·2ⁿ) time, O(n) depth",
            """
            List<List<int>> subsetsWithDup(List<int> nums) {
              nums.sort();
              final out = <List<int>>[];
              final current = <int>[];

              void backtrack(int start) {
                out.add(List<int>.from(current));
                for (var i = start; i < nums.length; i++) {
                  if (i > start && nums[i] == nums[i - 1]) continue;
                  current.add(nums[i]);
                  backtrack(i + 1);
                  current.removeLast();
                }
              }

              backtrack(0);
              return out;
            }
            """,
        ),
        _p(
            46, "Permutations", "Medium",
            "Swap each unused number into the next slot, then put it back.",
            "O(n·n!) time, O(n) depth",
            """
            List<List<int>> permute(List<int> nums) {
              final out = <List<int>>[];
              final current = <int>[];
              final used = List<bool>.filled(nums.length, false);

              void backtrack() {
                if (current.length == nums.length) {
                  out.add(List<int>.from(current));
                  return;
                }
                for (var i = 0; i < nums.length; i++) {
                  if (used[i]) continue;
                  used[i] = true;
                  current.add(nums[i]);
                  backtrack();
                  current.removeLast();
                  used[i] = false;
                }
              }

              backtrack();
              return out;
            }
            """,
        ),
        _p(
            39, "Combination Sum", "Medium",
            "Reuse is allowed, so recurse from i, not i + 1.",
            "O(n^(t/m)) time, O(t/m) depth",
            """
            List<List<int>> combinationSum(List<int> candidates, int target) {
              final out = <List<int>>[];
              final current = <int>[];

              void backtrack(int start, int left) {
                if (left == 0) {
                  out.add(List<int>.from(current));
                  return;
                }
                for (var i = start; i < candidates.length; i++) {
                  if (candidates[i] > left) continue;
                  current.add(candidates[i]);
                  backtrack(i, left - candidates[i]);
                  current.removeLast();
                }
              }

              backtrack(0, target);
              return out;
            }
            """,
        ),
        _p(
            79, "Word Search", "Medium",
            "Mark a cell used while you explore from it, then put it back.",
            "O(m·n·4^L) time, O(L) depth",
            """
            bool exist(List<List<String>> board, String word) {
              final rows = board.length;
              final cols = board[0].length;

              bool search(int r, int c, int i) {
                if (i == word.length) return true;
                if (r < 0 || r >= rows || c < 0 || c >= cols) return false;
                if (board[r][c] != word[i]) return false;
                final saved = board[r][c];
                board[r][c] = '#';
                final found = search(r + 1, c, i + 1) ||
                    search(r - 1, c, i + 1) ||
                    search(r, c + 1, i + 1) ||
                    search(r, c - 1, i + 1);
                board[r][c] = saved;
                return found;
              }

              for (var r = 0; r < rows; r++) {
                for (var c = 0; c < cols; c++) {
                  if (search(r, c, 0)) return true;
                }
              }
              return false;
            }
            """,
        ),
        _p(
            77, 'Combinations', 'Medium',
            'Only ever pick numbers after the last one taken, so no pair is built twice.',
            'O(k * C(n, k)) time, O(k) space',
            """
            List<List<int>> combine(int n, int k) {
              final out = <List<int>>[];
              final picked = <int>[];
              void walk(int start) {
                if (picked.length == k) {
                  out.add(List<int>.from(picked));
                  return;
                }
                for (var value = start; value <= n; value++) {
                  picked.add(value);
                  walk(value + 1);
                  picked.removeLast();
                }
              }

              walk(1);
              return out;
            }
            """,
        ),
        _p(
            17, 'Letter Combinations of a Phone Number', 'Medium',
            "One digit is one level of the tree, and its letters are that level's branches.",
            'O(4 ** n) time, O(n) space',
            """
            List<String> letterCombinations(String digits) {
              if (digits.isEmpty) return [];
              const keys = {
                '2': 'abc', '3': 'def', '4': 'ghi', '5': 'jkl',
                '6': 'mno', '7': 'pqrs', '8': 'tuv', '9': 'wxyz',
              };
              final out = <String>[];
              void walk(int index, String built) {
                if (index == digits.length) {
                  out.add(built);
                  return;
                }
                for (final letter in keys[digits[index]]!.split('')) {
                  walk(index + 1, built + letter);
                }
              }

              walk(0, '');
              return out;
            }
            """,
        ),
        _p(
            131, 'Palindrome Partitioning', 'Medium',
            'Cut after every position whose prefix reads the same both ways, then solve the rest.',
            'O(n * 2 ** n) time, O(n) space',
            """
            List<List<String>> partition(String text) {
              final out = <List<String>>[];
              final built = <String>[];
              void walk(int start) {
                if (start == text.length) {
                  out.add(List<String>.from(built));
                  return;
                }
                for (var end = start + 1; end <= text.length; end++) {
                  final piece = text.substring(start, end);
                  if (piece == piece.split('').reversed.join()) {
                    built.add(piece);
                    walk(end);
                    built.removeLast();
                  }
                }
              }

              walk(0);
              return out;
            }
            """,
        ),
    ),
)


# ── 11. Top K (heaps) ───────────────────────────────────────

_HEAP = Pattern(
    id="lc-heap",
    name="Top K (Heaps)",
    order=11,
    blurb="Keep only the k best, and know the worst of them instantly.",
    tell="'Top k', 'k closest', 'k most frequent'.",
    problems=(
        _p(
            215, "Kth Largest Element", "Medium",
            "Sorting is the clear version; a heap of size k is the fast one.",
            "O(n log n) time, O(1) extra space",
            """
            int findKthLargest(List<int> nums, int k) {
              final sorted = List<int>.from(nums)..sort();
              return sorted[sorted.length - k];
            }
            """,
        ),
        _p(
            347, "Top K Frequent Elements", "Medium",
            "Count first, then sort the distinct values by their counts.",
            "O(n log n) time, O(n) space",
            """
            List<int> topKFrequent(List<int> nums, int k) {
              final counts = <int, int>{};
              for (final n in nums) {
                counts[n] = (counts[n] ?? 0) + 1;
              }
              final byCount = counts.keys.toList()
                ..sort((a, b) => counts[b]!.compareTo(counts[a]!));
              return byCount.take(k).toList();
            }
            """,
        ),
        _p(
            973, "K Closest Points to Origin", "Medium",
            "Compare squared distances — the square root changes nothing.",
            "O(n log n) time, O(n) space",
            """
            List<List<int>> kClosest(List<List<int>> points, int k) {
              int distance(List<int> p) => p[0] * p[0] + p[1] * p[1];
              final sorted = List<List<int>>.from(points)
                ..sort((a, b) => distance(a).compareTo(distance(b)));
              return sorted.take(k).toList();
            }
            """,
        ),
        _p(
            1046, 'Last Stone Weight', 'Easy',
            'No heap in the language, so re-sort: the two biggest are always at the front.',
            'O(n * n log n) time, O(n) space',
            """
            int lastStoneWeight(List<int> stones) {
              final heap = List<int>.from(stones);
              while (heap.length > 1) {
                heap.sort((a, b) => b - a);
                final first = heap.removeAt(0);
                final second = heap.removeAt(0);
                if (first != second) heap.add(first - second);
              }
              return heap.isEmpty ? 0 : heap[0];
            }
            """,
        ),
        _p(
            692, 'Top K Frequent Words', 'Medium',
            'Sort by count, then alphabetically — the comparator does both in one line.',
            'O(n log n) time, O(n) space',
            """
            List<String> topKFrequentWords(List<String> words, int k) {
              final counts = <String, int>{};
              for (final word in words) {
                counts[word] = (counts[word] ?? 0) + 1;
              }
              final ranked = counts.keys.toList()
                ..sort((a, b) =>
                    counts[b] != counts[a] ? counts[b]! - counts[a]! : a.compareTo(b));
              return ranked.take(k).toList();
            }
            """,
        ),
        _p(
            451, 'Sort Characters By Frequency', 'Medium',
            'Count, sort the characters by how common they are, then repeat each one.',
            'O(n log n) time, O(n) space',
            """
            String frequencySort(String s) {
              final counts = <String, int>{};
              for (final ch in s.split('')) {
                counts[ch] = (counts[ch] ?? 0) + 1;
              }
              final ranked = counts.keys.toList()
                ..sort((a, b) =>
                    counts[b] != counts[a] ? counts[b]! - counts[a]! : a.compareTo(b));
              return ranked.map((ch) => ch * counts[ch]!).join();
            }
            """,
        ),
        _p(
            378, 'Kth Smallest Element in a Sorted Matrix', 'Medium',
            'The matrix is small enough to flatten and sort — no heap in the language.',
            'O(n log n) time, O(n) space',
            """
            int kthSmallest(List<List<int>> matrix, int k) {
              final flat = <int>[];
              for (final row in matrix) {
                flat.addAll(row);
              }
              flat.sort();
              return flat[k - 1];
            }
            """,
        ),
        _p(
            767, 'Reorganize String', 'Medium',
            "Take the commonest letter that isn't the one you just used, and repeat.",
            'O(n * n log n) time, O(n) space',
            """
            String reorganizeString(String s) {
              final counts = <String, int>{};
              for (final ch in s.split('')) {
                counts[ch] = (counts[ch] ?? 0) + 1;
              }
              final out = <String>[];
              String? held;
              while (true) {
                final ready = counts.keys.where((ch) => ch != held).toList()
                  ..sort((a, b) =>
                      counts[b] != counts[a] ? counts[b]! - counts[a]! : a.compareTo(b));
                if (ready.isEmpty) break;
                final ch = ready.first;
                out.add(ch);
                if (counts[ch] == 1) {
                  counts.remove(ch);
                } else {
                  counts[ch] = counts[ch]! - 1;
                }
                held = ch;
              }
              return out.length == s.length ? out.join() : '';
            }
            """,
        ),
    ),
)


# ── 12. Topological sort ────────────────────────────────────

_TOPOLOGICAL = Pattern(
    id="lc-topological",
    name="Topological Sort",
    order=12,
    blurb="Do the things nothing is waiting on, then repeat.",
    tell="Prerequisites, build order, 'can this be finished?'.",
    preamble=(COLLECTION,),
    problems=(
        _p(
            207, "Course Schedule", "Medium",
            "If you can retire every course, there was no cycle.",
            "O(V + E) time, O(V + E) space",
            """
            bool canFinish(int numCourses, List<List<int>> prerequisites) {
              final nextCourses = List.generate(numCourses, (_) => <int>[]);
              final waitingOn = List<int>.filled(numCourses, 0);
              for (final pair in prerequisites) {
                nextCourses[pair[1]].add(pair[0]);
                waitingOn[pair[0]]++;
              }
              final ready = Queue<int>();
              for (var course = 0; course < numCourses; course++) {
                if (waitingOn[course] == 0) ready.add(course);
              }
              var done = 0;
              while (ready.isNotEmpty) {
                final course = ready.removeFirst();
                done++;
                for (final next in nextCourses[course]) {
                  waitingOn[next]--;
                  if (waitingOn[next] == 0) ready.add(next);
                }
              }
              return done == numCourses;
            }
            """,
        ),
        _p(
            210, "Course Schedule II", "Medium",
            "Same walk, but record the order you retired them in.",
            "O(V + E) time, O(V + E) space",
            """
            List<int> findOrder(int numCourses, List<List<int>> prerequisites) {
              final nextCourses = List.generate(numCourses, (_) => <int>[]);
              final waitingOn = List<int>.filled(numCourses, 0);
              for (final pair in prerequisites) {
                nextCourses[pair[1]].add(pair[0]);
                waitingOn[pair[0]]++;
              }
              final ready = Queue<int>();
              for (var course = 0; course < numCourses; course++) {
                if (waitingOn[course] == 0) ready.add(course);
              }
              final order = <int>[];
              while (ready.isNotEmpty) {
                final course = ready.removeFirst();
                order.add(course);
                for (final next in nextCourses[course]) {
                  waitingOn[next]--;
                  if (waitingOn[next] == 0) ready.add(next);
                }
              }
              return order.length == numCourses ? order : <int>[];
            }
            """,
        ),
        _p(
            310, "Minimum Height Trees", "Medium",
            "Peel the leaves layer by layer; whatever survives last is the centre.",
            "O(V + E) time, O(V + E) space",
            """
            List<int> findMinHeightTrees(int n, List<List<int>> edges) {
              if (n == 1) return [0];
              final neighbors = List.generate(n, (_) => <int>{});
              for (final edge in edges) {
                neighbors[edge[0]].add(edge[1]);
                neighbors[edge[1]].add(edge[0]);
              }
              var leaves = <int>[];
              for (var node = 0; node < n; node++) {
                if (neighbors[node].length == 1) leaves.add(node);
              }
              var remaining = n;
              while (remaining > 2) {
                remaining -= leaves.length;
                final next = <int>[];
                for (final leaf in leaves) {
                  for (final neighbor in neighbors[leaf]) {
                    neighbors[neighbor].remove(leaf);
                    if (neighbors[neighbor].length == 1) next.add(neighbor);
                  }
                  neighbors[leaf].clear();
                }
                leaves = next;
              }
              leaves.sort();
              return leaves;
            }
            """,
        ),
        _p(
            802, 'Find Eventual Safe States', 'Medium',
            'Reverse every edge, then peel from the terminal nodes — whatever drains is safe.',
            'O(v + e) time, O(v + e) space',
            """
            List<int> eventualSafeNodes(List<List<int>> graph) {
              final n = graph.length;
              final reverse = List.generate(n, (_) => <int>[]);
              final outdegree = List<int>.filled(n, 0);
              for (var node = 0; node < n; node++) {
                outdegree[node] = graph[node].length;
                for (final next in graph[node]) {
                  reverse[next].add(node);
                }
              }
              final queue = Queue<int>();
              for (var i = 0; i < n; i++) {
                if (outdegree[i] == 0) queue.add(i);
              }
              final safe = <int>[];
              while (queue.isNotEmpty) {
                final node = queue.removeFirst();
                safe.add(node);
                for (final prev in reverse[node]) {
                  outdegree[prev]--;
                  if (outdegree[prev] == 0) queue.add(prev);
                }
              }
              safe.sort();
              return safe;
            }
            """,
        ),
        _p(
            1462, 'Course Schedule IV', 'Medium',
            'Peel in order, and let each course inherit the prerequisite set of everything before it.',
            'O(v * e) time, O(v * v) space',
            """
            List<bool> checkIfPrerequisite(
              int numCourses,
              List<List<int>> prerequisites,
              List<List<int>> queries,
            ) {
              final graph = List.generate(numCourses, (_) => <int>[]);
              final indegree = List<int>.filled(numCourses, 0);
              for (final pair in prerequisites) {
                graph[pair[0]].add(pair[1]);
                indegree[pair[1]]++;
              }
              final needs = List.generate(numCourses, (_) => <int>{});
              final queue = Queue<int>();
              for (var i = 0; i < numCourses; i++) {
                if (indegree[i] == 0) queue.add(i);
              }
              while (queue.isNotEmpty) {
                final node = queue.removeFirst();
                for (final next in graph[node]) {
                  needs[next].add(node);
                  needs[next].addAll(needs[node]);
                  indegree[next]--;
                  if (indegree[next] == 0) queue.add(next);
                }
              }
              return queries.map((q) => needs[q[1]].contains(q[0])).toList();
            }
            """,
        ),
        _p(
            2115, 'Find All Possible Recipes from Given Supplies', 'Medium',
            'Ingredients are prerequisites: a recipe unlocks once its indegree of missing items hits zero.',
            'O(v + e) time, O(v + e) space',
            """
            List<String> findAllRecipes(
              List<String> recipes,
              List<List<String>> ingredients,
              List<String> supplies,
            ) {
              final graph = <String, List<String>>{};
              final indegree = <String, int>{};
              for (final recipe in recipes) {
                indegree[recipe] = 0;
              }
              for (var i = 0; i < recipes.length; i++) {
                for (final item in ingredients[i]) {
                  graph.putIfAbsent(item, () => <String>[]).add(recipes[i]);
                  indegree[recipes[i]] = indegree[recipes[i]]! + 1;
                }
              }
              final queue = Queue<String>()..addAll(supplies);
              final made = <String>[];
              while (queue.isNotEmpty) {
                final item = queue.removeFirst();
                for (final recipe in graph[item] ?? const <String>[]) {
                  indegree[recipe] = indegree[recipe]! - 1;
                  if (indegree[recipe] == 0) {
                    made.add(recipe);
                    queue.add(recipe);
                  }
                }
              }
              return made;
            }
            """,
        ),
        _p(
            1136, 'Parallel Courses', 'Medium',
            'Every drained layer of the queue is one semester — count the layers, not the courses.',
            'O(v + e) time, O(v + e) space',
            """
            int minimumSemesters(int n, List<List<int>> relations) {
              final graph = List.generate(n + 1, (_) => <int>[]);
              final indegree = List<int>.filled(n + 1, 0);
              for (final pair in relations) {
                graph[pair[0]].add(pair[1]);
                indegree[pair[1]]++;
              }
              final queue = Queue<int>();
              for (var i = 1; i <= n; i++) {
                if (indegree[i] == 0) queue.add(i);
              }
              var studied = 0;
              var semesters = 0;
              while (queue.isNotEmpty) {
                semesters++;
                for (var i = queue.length; i > 0; i--) {
                  final node = queue.removeFirst();
                  studied++;
                  for (final course in graph[node]) {
                    indegree[course]--;
                    if (indegree[course] == 0) queue.add(course);
                  }
                }
              }
              return studied == n ? semesters : -1;
            }
            """,
        ),
        _p(
            269, 'Alien Dictionary', 'Hard',
            'Adjacent words give one letter order each; the first difference is the only edge they prove.',
            'O(c) time, O(1) space',
            """
            String alienOrder(List<String> words) {
              final graph = <String, Set<String>>{};
              final indegree = <String, int>{};
              for (final word in words) {
                for (final ch in word.split('')) {
                  graph.putIfAbsent(ch, () => <String>{});
                  indegree.putIfAbsent(ch, () => 0);
                }
              }
              for (var i = 0; i + 1 < words.length; i++) {
                final first = words[i];
                final second = words[i + 1];
                var split = false;
                final shorter = first.length < second.length ? first.length : second.length;
                for (var j = 0; j < shorter; j++) {
                  if (first[j] != second[j]) {
                    if (graph[first[j]]!.add(second[j])) {
                      indegree[second[j]] = indegree[second[j]]! + 1;
                    }
                    split = true;
                    break;
                  }
                }
                if (!split && first.length > second.length) return '';
              }
              final queue = Queue<String>();
              indegree.forEach((ch, count) {
                if (count == 0) queue.add(ch);
              });
              final order = <String>[];
              while (queue.isNotEmpty) {
                final ch = queue.removeFirst();
                order.add(ch);
                for (final next in graph[ch]!) {
                  indegree[next] = indegree[next]! - 1;
                  if (indegree[next] == 0) queue.add(next);
                }
              }
              return order.length == indegree.length ? order.join() : '';
            }
            """,
        ),
    ),
)


# ── 13. Dynamic programming ─────────────────────────────────

_DP = Pattern(
    id="lc-dp",
    name="Dynamic Programming",
    order=13,
    blurb="Build the answer from smaller answers you already worked out.",
    tell="Counting ways, or a best total made of earlier choices.",
    problems=(
        _p(
            70, "Climbing Stairs", "Easy",
            "Ways to reach a step = ways to the two steps below it.",
            "O(n) time, O(1) space",
            """
            int climbStairs(int n) {
              var oneBack = 1;
              var twoBack = 1;
              for (var i = 2; i <= n; i++) {
                final total = oneBack + twoBack;
                twoBack = oneBack;
                oneBack = total;
              }
              return oneBack;
            }
            """,
        ),
        _p(
            198, "House Robber", "Medium",
            "At each house: skip it, or take it plus the best from two back.",
            "O(n) time, O(1) space",
            """
            int rob(List<int> nums) {
              var skip = 0;
              var take = 0;
              for (final money in nums) {
                final newTake = skip + money;
                final newSkip = skip > take ? skip : take;
                take = newTake;
                skip = newSkip;
              }
              return skip > take ? skip : take;
            }
            """,
        ),
        _p(
            322, "Coin Change", "Medium",
            "Best for an amount = one coin plus the best for the remainder.",
            "O(amount·coins) time, O(amount) space",
            """
            int coinChange(List<int> coins, int amount) {
              final unreachable = amount + 1;
              final best = List<int>.filled(amount + 1, unreachable);
              best[0] = 0;
              for (var total = 1; total <= amount; total++) {
                for (final coin in coins) {
                  if (coin <= total && best[total - coin] + 1 < best[total]) {
                    best[total] = best[total - coin] + 1;
                  }
                }
              }
              return best[amount] == unreachable ? -1 : best[amount];
            }
            """,
        ),
        _p(
            300, "Longest Increasing Subsequence", "Medium",
            "Each item extends the best chain ending in a smaller item.",
            "O(n²) time, O(n) space",
            """
            int lengthOfLIS(List<int> nums) {
              if (nums.isEmpty) return 0;
              final best = List<int>.filled(nums.length, 1);
              var longest = 1;
              for (var i = 1; i < nums.length; i++) {
                for (var j = 0; j < i; j++) {
                  if (nums[j] < nums[i] && best[j] + 1 > best[i]) {
                    best[i] = best[j] + 1;
                  }
                }
                if (best[i] > longest) longest = best[i];
              }
              return longest;
            }
            """,
        ),
        _p(
            746, 'Min Cost Climbing Stairs', 'Easy',
            'The cost of a step is its own plus the cheaper of the two ways off it.',
            'O(n) time, O(1) space',
            """
            int minCostClimbingStairs(List<int> cost) {
              var one = 0;
              var two = 0;
              for (var i = 2; i <= cost.length; i++) {
                final a = one + cost[i - 1];
                final b = two + cost[i - 2];
                final next = a < b ? a : b;
                two = one;
                one = next;
              }
              return one;
            }
            """,
        ),
        _p(
            1143, 'Longest Common Subsequence', 'Medium',
            'Matching letters extend the diagonal; otherwise take the better of dropping one.',
            'O(m * n) time, O(m * n) space',
            """
            int longestCommonSubsequence(String first, String second) {
              final grid = List.generate(first.length + 1, (_) => List.filled(second.length + 1, 0));
              for (var i = first.length - 1; i >= 0; i--) {
                for (var j = second.length - 1; j >= 0; j--) {
                  if (first[i] == second[j]) {
                    grid[i][j] = 1 + grid[i + 1][j + 1];
                  } else {
                    final down = grid[i + 1][j];
                    final rightward = grid[i][j + 1];
                    grid[i][j] = down > rightward ? down : rightward;
                  }
                }
              }
              return grid[0][0];
            }
            """,
        ),
        _p(
            139, 'Word Break', 'Medium',
            'A position is reachable when some word ends there and its start was reachable too.',
            'O(n * n * w) time, O(n) space',
            """
            bool wordBreak(String text, List<String> words) {
              final reachable = List<bool>.filled(text.length + 1, false);
              reachable[0] = true;
              for (var end = 1; end <= text.length; end++) {
                for (final word in words) {
                  final start = end - word.length;
                  if (start >= 0 && reachable[start] && text.substring(start, end) == word) {
                    reachable[end] = true;
                    break;
                  }
                }
              }
              return reachable[text.length];
            }
            """,
        ),
        _p(
            152, 'Maximum Product Subarray', 'Medium',
            'Track the smallest product too — a negative turns the worst into the best.',
            'O(n) time, O(1) space',
            """
            int maxProduct(List<int> nums) {
              var best = nums[0];
              var high = nums[0];
              var low = nums[0];
              for (var i = 1; i < nums.length; i++) {
                final n = nums[i];
                final options = [n, high * n, low * n];
                high = options.reduce((a, b) => a > b ? a : b);
                low = options.reduce((a, b) => a < b ? a : b);
                if (high > best) best = high;
              }
              return best;
            }
            """,
        ),
    ),
)
