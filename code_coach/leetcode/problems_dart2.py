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
    ),
)
