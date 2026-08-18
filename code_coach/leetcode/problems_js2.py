"""JavaScript solutions, patterns 5–13. Continues `problems_js`."""

from __future__ import annotations

from code_coach.leetcode.js_common import GRAPH_NODE, LIST_NODE, TREE_NODE, _p
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
            function reverseList(head) {
              let prev = null;
              let cur = head;
              while (cur !== null) {
                const nxt = cur.next;
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
            function mergeTwoLists(list1, list2) {
              const dummy = new ListNode(0);
              let tail = dummy;
              let a = list1;
              let b = list2;
              while (a !== null && b !== null) {
                if (a.val <= b.val) {
                  tail.next = a;
                  a = a.next;
                } else {
                  tail.next = b;
                  b = b.next;
                }
                tail = tail.next;
              }
              tail.next = a !== null ? a : b;
              return dummy.next;
            }
            """,
        ),
        _p(
            141, "Linked List Cycle", "Easy",
            "A fast pointer laps a slow one only if the track loops.",
            "O(n) time, O(1) space",
            """
            function hasCycle(head) {
              let slow = head;
              let fast = head;
              while (fast !== null && fast.next !== null) {
                slow = slow.next;
                fast = fast.next.next;
                if (slow === fast) return true;
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
            function removeNthFromEnd(head, n) {
              const dummy = new ListNode(0, head);
              let lead = dummy;
              let trail = dummy;
              for (let i = 0; i < n; i++) {
                lead = lead.next;
              }
              while (lead.next !== null) {
                lead = lead.next;
                trail = trail.next;
              }
              trail.next = trail.next.next;
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
            function search(nums, target) {
              let lo = 0;
              let hi = nums.length - 1;
              while (lo <= hi) {
                const mid = Math.floor((lo + hi) / 2);
                if (nums[mid] === target) return mid;
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
            function searchInsert(nums, target) {
              let lo = 0;
              let hi = nums.length - 1;
              while (lo <= hi) {
                const mid = Math.floor((lo + hi) / 2);
                if (nums[mid] === target) return mid;
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
            function findMin(nums) {
              let lo = 0;
              let hi = nums.length - 1;
              while (lo < hi) {
                const mid = Math.floor((lo + hi) / 2);
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
            function searchRotated(nums, target) {
              let lo = 0;
              let hi = nums.length - 1;
              while (lo <= hi) {
                const mid = Math.floor((lo + hi) / 2);
                if (nums[mid] === target) return mid;
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
            function minEatingSpeed(piles, h) {
              let lo = 1;
              let hi = Math.max(...piles);
              while (lo < hi) {
                const speed = Math.floor((lo + hi) / 2);
                let hours = 0;
                for (const pile of piles) {
                  hours += Math.ceil(pile / speed);
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
            function maxDepth(root) {
              if (root === null) return 0;
              return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
            }
            """,
        ),
        _p(
            226, "Invert Binary Tree", "Easy",
            "Swap the two children, then tell each of them to do the same.",
            "O(n) time, O(h) space",
            """
            function invertTree(root) {
              if (root === null) return null;
              const temp = root.left;
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
            function hasPathSum(root, targetSum) {
              if (root === null) return false;
              const left = targetSum - root.val;
              if (root.left === null && root.right === null) return left === 0;
              return hasPathSum(root.left, left) || hasPathSum(root.right, left);
            }
            """,
        ),
        _p(
            543, "Diameter of Binary Tree", "Easy",
            "The longest path through a node is its two child depths added.",
            "O(n) time, O(h) space",
            """
            function diameterOfBinaryTree(root) {
              let best = 0;

              function depth(node) {
                if (node === null) return 0;
                const left = depth(node.left);
                const right = depth(node.right);
                best = Math.max(best, left + right);
                return 1 + Math.max(left, right);
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
            function isValidBST(root, low = null, high = null) {
              if (root === null) return true;
              if (low !== null && root.val <= low) return false;
              if (high !== null && root.val >= high) return false;
              return (
                isValidBST(root.left, low, root.val) &&
                isValidBST(root.right, root.val, high)
              );
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
    preamble=(TREE_NODE,),
    problems=(
        _p(
            102, "Binary Tree Level Order Traversal", "Medium",
            "Drain exactly one level per round, queueing the next as you go.",
            "O(n) time, O(n) space",
            """
            function levelOrder(root) {
              const out = [];
              if (root === null) return out;
              let queue = [root];
              while (queue.length) {
                const level = [];
                const next = [];
                for (const node of queue) {
                  level.push(node.val);
                  if (node.left) next.push(node.left);
                  if (node.right) next.push(node.right);
                }
                out.push(level);
                queue = next;
              }
              return out;
            }
            """,
        ),
        _p(
            199, "Binary Tree Right Side View", "Medium",
            "From each level, keep only the last node you saw.",
            "O(n) time, O(n) space",
            """
            function rightSideView(root) {
              const out = [];
              if (root === null) return out;
              let queue = [root];
              while (queue.length) {
                const next = [];
                for (const node of queue) {
                  if (node.left) next.push(node.left);
                  if (node.right) next.push(node.right);
                }
                out.push(queue[queue.length - 1].val);
                queue = next;
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
            function zigzagLevelOrder(root) {
              const out = [];
              if (root === null) return out;
              let queue = [root];
              let leftToRight = true;
              while (queue.length) {
                const level = [];
                const next = [];
                for (const node of queue) {
                  level.push(node.val);
                  if (node.left) next.push(node.left);
                  if (node.right) next.push(node.right);
                }
                out.push(leftToRight ? level : level.reverse());
                leftToRight = !leftToRight;
                queue = next;
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
    preamble=(GRAPH_NODE,),
    problems=(
        _p(
            733, "Flood Fill", "Easy",
            "Repaint outward from the start while the colour still matches.",
            "O(m·n) time, O(m·n) space",
            """
            function floodFill(image, sr, sc, color) {
              const start = image[sr][sc];
              if (start === color) return image;
              const rows = image.length;
              const cols = image[0].length;

              function fill(r, c) {
                if (r < 0 || r >= rows || c < 0 || c >= cols) return;
                if (image[r][c] !== start) return;
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
            function numIslands(grid) {
              if (grid.length === 0) return 0;
              const rows = grid.length;
              const cols = grid[0].length;
              let count = 0;

              function sink(r, c) {
                if (r < 0 || r >= rows || c < 0 || c >= cols) return;
                if (grid[r][c] !== '1') return;
                grid[r][c] = '0';
                sink(r + 1, c);
                sink(r - 1, c);
                sink(r, c + 1);
                sink(r, c - 1);
              }

              for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
                  if (grid[r][c] === '1') {
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
            function orangesRotting(grid) {
              const rows = grid.length;
              const cols = grid[0].length;
              let queue = [];
              let fresh = 0;
              for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
                  if (grid[r][c] === 2) queue.push([r, c]);
                  if (grid[r][c] === 1) fresh++;
                }
              }
              if (fresh === 0) return 0;
              const steps = [[1, 0], [-1, 0], [0, 1], [0, -1]];
              let minutes = 0;
              while (queue.length && fresh > 0) {
                minutes++;
                const next = [];
                for (const [r, c] of queue) {
                  for (const [dr, dc] of steps) {
                    const nr = r + dr;
                    const nc = c + dc;
                    if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
                    if (grid[nr][nc] !== 1) continue;
                    grid[nr][nc] = 2;
                    fresh--;
                    next.push([nr, nc]);
                  }
                }
                queue = next;
              }
              return fresh === 0 ? minutes : -1;
            }
            """,
        ),
        _p(
            133, "Clone Graph", "Medium",
            "Keep a map from old node to new so a cycle doesn't loop forever.",
            "O(n) time, O(n) space",
            """
            function cloneGraph(node, made = new Map()) {
              if (node === null) return null;
              if (made.has(node)) return made.get(node);
              const copy = new GraphNode(node.val);
              made.set(node, copy);
              for (const neighbor of node.neighbors) {
                copy.neighbors.push(cloneGraph(neighbor, made));
              }
              return copy;
            }
            """,
        ),
    ),
)


# ── 10. Subsets & backtracking ──────────────────────────────

_BACKTRACKING = Pattern(
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
            function subsets(nums) {
              const out = [];
              const current = [];

              function backtrack(start) {
                out.push([...current]);
                for (let i = start; i < nums.length; i++) {
                  current.push(nums[i]);
                  backtrack(i + 1);
                  current.pop();
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
            function subsetsWithDup(nums) {
              nums.sort((a, b) => a - b);
              const out = [];
              const current = [];

              function backtrack(start) {
                out.push([...current]);
                for (let i = start; i < nums.length; i++) {
                  if (i > start && nums[i] === nums[i - 1]) continue;
                  current.push(nums[i]);
                  backtrack(i + 1);
                  current.pop();
                }
              }

              backtrack(0);
              return out;
            }
            """,
        ),
        _p(
            46, "Permutations", "Medium",
            "Take each unused number into the next slot, then put it back.",
            "O(n·n!) time, O(n) depth",
            """
            function permute(nums) {
              const out = [];
              const current = [];
              const used = new Array(nums.length).fill(false);

              function backtrack() {
                if (current.length === nums.length) {
                  out.push([...current]);
                  return;
                }
                for (let i = 0; i < nums.length; i++) {
                  if (used[i]) continue;
                  used[i] = true;
                  current.push(nums[i]);
                  backtrack();
                  current.pop();
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
            function combinationSum(candidates, target) {
              const out = [];
              const current = [];

              function backtrack(start, left) {
                if (left === 0) {
                  out.push([...current]);
                  return;
                }
                for (let i = start; i < candidates.length; i++) {
                  if (candidates[i] > left) continue;
                  current.push(candidates[i]);
                  backtrack(i, left - candidates[i]);
                  current.pop();
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
            function exist(board, word) {
              const rows = board.length;
              const cols = board[0].length;

              function search(r, c, i) {
                if (i === word.length) return true;
                if (r < 0 || r >= rows || c < 0 || c >= cols) return false;
                if (board[r][c] !== word[i]) return false;
                const saved = board[r][c];
                board[r][c] = '#';
                const found =
                  search(r + 1, c, i + 1) ||
                  search(r - 1, c, i + 1) ||
                  search(r, c + 1, i + 1) ||
                  search(r, c - 1, i + 1);
                board[r][c] = saved;
                return found;
              }

              for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
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
            215, "Kth Largest Element in an Array", "Medium",
            "Sorting is the clear version; a heap of size k is the fast one.",
            "O(n log n) time, O(n) space",
            """
            function findKthLargest(nums, k) {
              const sorted = [...nums].sort((a, b) => a - b);
              return sorted[sorted.length - k];
            }
            """,
        ),
        _p(
            347, "Top K Frequent Elements", "Medium",
            "Count first, then sort the distinct values by their counts.",
            "O(n log n) time, O(n) space",
            """
            function topKFrequent(nums, k) {
              const counts = new Map();
              for (const n of nums) {
                counts.set(n, (counts.get(n) || 0) + 1);
              }
              return [...counts.keys()]
                .sort((a, b) => counts.get(b) - counts.get(a))
                .slice(0, k);
            }
            """,
        ),
        _p(
            973, "K Closest Points to Origin", "Medium",
            "Compare squared distances — the square root changes nothing.",
            "O(n log n) time, O(n) space",
            """
            function kClosest(points, k) {
              const distance = (p) => p[0] * p[0] + p[1] * p[1];
              return [...points]
                .sort((a, b) => distance(a) - distance(b))
                .slice(0, k);
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
    problems=(
        _p(
            207, "Course Schedule", "Medium",
            "If you can retire every course, there was no cycle.",
            "O(V + E) time, O(V + E) space",
            """
            function canFinish(numCourses, prerequisites) {
              const nextCourses = Array.from({ length: numCourses }, () => []);
              const waitingOn = new Array(numCourses).fill(0);
              for (const [course, before] of prerequisites) {
                nextCourses[before].push(course);
                waitingOn[course]++;
              }
              const ready = [];
              for (let c = 0; c < numCourses; c++) {
                if (waitingOn[c] === 0) ready.push(c);
              }
              let done = 0;
              while (ready.length) {
                const course = ready.pop();
                done++;
                for (const next of nextCourses[course]) {
                  waitingOn[next]--;
                  if (waitingOn[next] === 0) ready.push(next);
                }
              }
              return done === numCourses;
            }
            """,
        ),
        _p(
            210, "Course Schedule II", "Medium",
            "Same walk, but record the order you retired them in.",
            "O(V + E) time, O(V + E) space",
            """
            function findOrder(numCourses, prerequisites) {
              const nextCourses = Array.from({ length: numCourses }, () => []);
              const waitingOn = new Array(numCourses).fill(0);
              for (const [course, before] of prerequisites) {
                nextCourses[before].push(course);
                waitingOn[course]++;
              }
              const ready = [];
              for (let c = 0; c < numCourses; c++) {
                if (waitingOn[c] === 0) ready.push(c);
              }
              const order = [];
              while (ready.length) {
                const course = ready.shift();
                order.push(course);
                for (const next of nextCourses[course]) {
                  waitingOn[next]--;
                  if (waitingOn[next] === 0) ready.push(next);
                }
              }
              return order.length === numCourses ? order : [];
            }
            """,
        ),
        _p(
            310, "Minimum Height Trees", "Medium",
            "Peel the leaves layer by layer; whatever survives last is the centre.",
            "O(V + E) time, O(V + E) space",
            """
            function findMinHeightTrees(n, edges) {
              if (n === 1) return [0];
              const neighbors = Array.from({ length: n }, () => new Set());
              for (const [a, b] of edges) {
                neighbors[a].add(b);
                neighbors[b].add(a);
              }
              let leaves = [];
              for (let node = 0; node < n; node++) {
                if (neighbors[node].size === 1) leaves.push(node);
              }
              let remaining = n;
              while (remaining > 2) {
                remaining -= leaves.length;
                const next = [];
                for (const leaf of leaves) {
                  for (const neighbor of neighbors[leaf]) {
                    neighbors[neighbor].delete(leaf);
                    if (neighbors[neighbor].size === 1) next.push(neighbor);
                  }
                  neighbors[leaf].clear();
                }
                leaves = next;
              }
              return leaves.sort((a, b) => a - b);
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
            function climbStairs(n) {
              let oneBack = 1;
              let twoBack = 1;
              for (let i = 2; i <= n; i++) {
                const total = oneBack + twoBack;
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
            function rob(nums) {
              let skip = 0;
              let take = 0;
              for (const money of nums) {
                const newTake = skip + money;
                const newSkip = Math.max(skip, take);
                take = newTake;
                skip = newSkip;
              }
              return Math.max(skip, take);
            }
            """,
        ),
        _p(
            322, "Coin Change", "Medium",
            "Best for an amount = one coin plus the best for the remainder.",
            "O(amount·coins) time, O(amount) space",
            """
            function coinChange(coins, amount) {
              const unreachable = amount + 1;
              const best = new Array(amount + 1).fill(unreachable);
              best[0] = 0;
              for (let total = 1; total <= amount; total++) {
                for (const coin of coins) {
                  if (coin <= total) {
                    best[total] = Math.min(best[total], best[total - coin] + 1);
                  }
                }
              }
              return best[amount] === unreachable ? -1 : best[amount];
            }
            """,
        ),
        _p(
            300, "Longest Increasing Subsequence", "Medium",
            "Each item extends the best chain ending in a smaller item.",
            "O(n²) time, O(n) space",
            """
            function lengthOfLIS(nums) {
              if (nums.length === 0) return 0;
              const best = new Array(nums.length).fill(1);
              let longest = 1;
              for (let i = 1; i < nums.length; i++) {
                for (let j = 0; j < i; j++) {
                  if (nums[j] < nums[i]) {
                    best[i] = Math.max(best[i], best[j] + 1);
                  }
                }
                longest = Math.max(longest, best[i]);
              }
              return longest;
            }
            """,
        ),
    ),
)
