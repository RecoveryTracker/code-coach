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
        _p(
            876, 'Middle of the Linked List', 'Easy',
            "One pointer takes two steps per the other's one, so it ends at twice the distance.",
            'O(n) time, O(1) space',
            """
            function middleNode(head) {
              let slow = head;
              let fast = head;
              while (fast && fast.next) {
                slow = slow.next;
                fast = fast.next.next;
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
            function deleteDuplicates(head) {
              let node = head;
              while (node && node.next) {
                if (node.val === node.next.val) node.next = node.next.next;
                else node = node.next;
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
            function isPalindromeList(head) {
              let slow = head;
              let fast = head;
              while (fast && fast.next) {
                slow = slow.next;
                fast = fast.next.next;
              }
              let second = null;
              while (slow) {
                const next = slow.next;
                slow.next = second;
                second = slow;
                slow = next;
              }
              let first = head;
              while (second) {
                if (first.val !== second.val) return false;
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
            function addTwoNumbers(first, second) {
              const head = new ListNode();
              let node = head;
              let carry = 0;
              while (first || second || carry) {
                let total = carry;
                if (first) {
                  total += first.val;
                  first = first.next;
                }
                if (second) {
                  total += second.val;
                  second = second.next;
                }
                carry = Math.floor(total / 10);
                node.next = new ListNode(total % 10);
                node = node.next;
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
        _p(
            278, 'First Bad Version', 'Easy',
            "Search for a boundary: keep the mid when it's bad, discard it when it isn't.",
            'O(log n) time, O(1) space',
            """
            function firstBadVersion(n, isBad) {
              let low = 1;
              let high = n;
              while (low < high) {
                const mid = Math.floor((low + high) / 2);
                if (isBad(mid)) high = mid;
                else low = mid + 1;
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
            function searchRange(nums, target) {
              const edge = (first) => {
                let low = 0;
                let high = nums.length - 1;
                let found = -1;
                while (low <= high) {
                  const mid = Math.floor((low + high) / 2);
                  if (nums[mid] === target) {
                    found = mid;
                    if (first) high = mid - 1;
                    else low = mid + 1;
                  } else if (nums[mid] < target) {
                    low = mid + 1;
                  } else {
                    high = mid - 1;
                  }
                }
                return found;
              };
              return [edge(true), edge(false)];
            }
            """,
        ),
        _p(
            74, 'Search a 2D Matrix', 'Medium',
            'A sorted matrix is one sorted list folded up, so divide the index to unfold it.',
            'O(log(m * n)) time, O(1) space',
            """
            function searchMatrix(matrix, target) {
              if (matrix.length === 0 || matrix[0].length === 0) return false;
              const rows = matrix.length;
              const cols = matrix[0].length;
              let low = 0;
              let high = rows * cols - 1;
              while (low <= high) {
                const mid = Math.floor((low + high) / 2);
                const value = matrix[Math.floor(mid / cols)][mid % cols];
                if (value === target) return true;
                if (value < target) low = mid + 1;
                else high = mid - 1;
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
        _p(
            100, 'Same Tree', 'Easy',
            'Two trees match when their roots match and both pairs of children do.',
            'O(n) time, O(h) space',
            """
            function isSameTree(first, second) {
              if (!first && !second) return true;
              if (!first || !second) return false;
              if (first.val !== second.val) return false;
              return isSameTree(first.left, second.left) && isSameTree(first.right, second.right);
            }
            """,
        ),
        _p(
            101, 'Symmetric Tree', 'Easy',
            'A mirror compares left against right — the recursion crosses over.',
            'O(n) time, O(h) space',
            """
            function isSymmetric(root) {
              const mirror = (left, right) => {
                if (!left && !right) return true;
                if (!left || !right) return false;
                if (left.val !== right.val) return false;
                return mirror(left.left, right.right) && mirror(left.right, right.left);
              };
              return mirror(root, root);
            }
            """,
        ),
        _p(
            236, 'Lowest Common Ancestor of a Binary Tree', 'Medium',
            'A node whose two sides each found something is the meeting point.',
            'O(n) time, O(h) space',
            """
            function lowestCommonAncestor(root, p, q) {
              if (!root || root === p || root === q) return root;
              const left = lowestCommonAncestor(root.left, p, q);
              const right = lowestCommonAncestor(root.right, p, q);
              if (left && right) return root;
              return left || right;
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
        _p(
            111, 'Minimum Depth of Binary Tree', 'Easy',
            'BFS stops at the first leaf it meets — DFS would walk the whole tree first.',
            'O(n) time, O(n) space',
            """
            function minDepth(root) {
              if (!root) return 0;
              let queue = [root];
              let depth = 1;
              while (queue.length) {
                const next = [];
                for (const node of queue) {
                  if (!node.left && !node.right) return depth;
                  if (node.left) next.push(node.left);
                  if (node.right) next.push(node.right);
                }
                queue = next;
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
            function averageOfLevels(root) {
              if (!root) return [];
              const averages = [];
              let queue = [root];
              while (queue.length) {
                let total = 0;
                const next = [];
                for (const node of queue) {
                  total += node.val;
                  if (node.left) next.push(node.left);
                  if (node.right) next.push(node.right);
                }
                averages.push(total / queue.length);
                queue = next;
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
            function largestValues(root) {
              if (!root) return [];
              const largest = [];
              let queue = [root];
              while (queue.length) {
                let best = null;
                const next = [];
                for (const node of queue) {
                  if (best === null || node.val > best) best = node.val;
                  if (node.left) next.push(node.left);
                  if (node.right) next.push(node.right);
                }
                largest.push(best);
                queue = next;
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
            function maxLevelSum(root) {
              if (!root) return 0;
              let queue = [root];
              let level = 0;
              let bestLevel = 1;
              let bestSum = null;
              while (queue.length) {
                level++;
                let total = 0;
                const next = [];
                for (const node of queue) {
                  total += node.val;
                  if (node.left) next.push(node.left);
                  if (node.right) next.push(node.right);
                }
                if (bestSum === null || total > bestSum) {
                  bestSum = total;
                  bestLevel = level;
                }
                queue = next;
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
            function widthOfBinaryTree(root) {
              if (!root) return 0;
              let widest = 0;
              let queue = [[root, 0]];
              while (queue.length) {
                const first = queue[0][1];
                let last = first;
                const next = [];
                for (const [node, index] of queue) {
                  last = index;
                  if (node.left) next.push([node.left, index * 2]);
                  if (node.right) next.push([node.right, index * 2 + 1]);
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
        _p(
            695, 'Max Area of Island', 'Medium',
            'Same flood fill, but the walk returns a size instead of just marking cells.',
            'O(m * n) time, O(m * n) space',
            """
            function maxAreaOfIsland(grid) {
              if (grid.length === 0) return 0;
              const rows = grid.length;
              const cols = grid[0].length;
              const fill = (r, c) => {
                if (r < 0 || c < 0 || r >= rows || c >= cols) return 0;
                if (grid[r][c] !== 1) return 0;
                grid[r][c] = 0;
                return 1 + fill(r + 1, c) + fill(r - 1, c) + fill(r, c + 1) + fill(r, c - 1);
              };
              let best = 0;
              for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
                  const area = fill(r, c);
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
            function findCircleNum(isConnected) {
              const n = isConnected.length;
              const seen = new Set();
              const visit = (city) => {
                seen.add(city);
                for (let other = 0; other < n; other++) {
                  if (isConnected[city][other] && !seen.has(other)) visit(other);
                }
              };
              let groups = 0;
              for (let city = 0; city < n; city++) {
                if (!seen.has(city)) {
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
            function updateMatrix(mat) {
              const rows = mat.length;
              const cols = mat[0].length;
              const out = Array.from({ length: rows }, () => new Array(cols).fill(-1));
              const queue = [];
              for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
                  if (mat[r][c] === 0) {
                    out[r][c] = 0;
                    queue.push([r, c]);
                  }
                }
              }
              let head = 0;
              while (head < queue.length) {
                const [r, c] = queue[head++];
                for (const [dr, dc] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
                  const nr = r + dr;
                  const nc = c + dc;
                  if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && out[nr][nc] === -1) {
                    out[nr][nc] = out[r][c] + 1;
                    queue.push([nr, nc]);
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
            function pacificAtlantic(heights) {
              if (heights.length === 0) return [];
              const rows = heights.length;
              const cols = heights[0].length;
              const pacific = new Set();
              const atlantic = new Set();
              const climb = (r, c, seen) => {
                seen.add(`${r},${c}`);
                for (const [dr, dc] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
                  const nr = r + dr;
                  const nc = c + dc;
                  if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
                    if (!seen.has(`${nr},${nc}`) && heights[nr][nc] >= heights[r][c]) {
                      climb(nr, nc, seen);
                    }
                  }
                }
              };
              for (let c = 0; c < cols; c++) {
                climb(0, c, pacific);
                climb(rows - 1, c, atlantic);
              }
              for (let r = 0; r < rows; r++) {
                climb(r, 0, pacific);
                climb(r, cols - 1, atlantic);
              }
              const both = [];
              for (const cell of pacific) {
                if (atlantic.has(cell)) both.push(cell.split(',').map(Number));
              }
              return both.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
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
        _p(
            77, 'Combinations', 'Medium',
            'Only ever pick numbers after the last one taken, so no pair is built twice.',
            'O(k * C(n, k)) time, O(k) space',
            """
            function combine(n, k) {
              const out = [];
              const picked = [];
              const walk = (start) => {
                if (picked.length === k) {
                  out.push([...picked]);
                  return;
                }
                for (let value = start; value <= n; value++) {
                  picked.push(value);
                  walk(value + 1);
                  picked.pop();
                }
              };
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
            function letterCombinations(digits) {
              if (digits.length === 0) return [];
              const keys = {
                2: 'abc', 3: 'def', 4: 'ghi', 5: 'jkl',
                6: 'mno', 7: 'pqrs', 8: 'tuv', 9: 'wxyz',
              };
              const out = [];
              const walk = (index, built) => {
                if (index === digits.length) {
                  out.push(built);
                  return;
                }
                for (const letter of keys[digits[index]]) walk(index + 1, built + letter);
              };
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
            function partition(text) {
              const out = [];
              const built = [];
              const walk = (start) => {
                if (start === text.length) {
                  out.push([...built]);
                  return;
                }
                for (let end = start + 1; end <= text.length; end++) {
                  const piece = text.slice(start, end);
                  if (piece === [...piece].reverse().join('')) {
                    built.push(piece);
                    walk(end);
                    built.pop();
                  }
                }
              };
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
        _p(
            1046, 'Last Stone Weight', 'Easy',
            'No heap in the language, so re-sort: the two biggest are always at the front.',
            'O(n * n log n) time, O(n) space',
            """
            function lastStoneWeight(stones) {
              const heap = [...stones];
              while (heap.length > 1) {
                heap.sort((a, b) => b - a);
                const first = heap.shift();
                const second = heap.shift();
                if (first !== second) heap.push(first - second);
              }
              return heap.length ? heap[0] : 0;
            }
            """,
        ),
        _p(
            692, 'Top K Frequent Words', 'Medium',
            'Sort by count, then alphabetically — the comparator does both in one line.',
            'O(n log n) time, O(n) space',
            """
            function topKFrequentWords(words, k) {
              const counts = new Map();
              for (const word of words) counts.set(word, (counts.get(word) || 0) + 1);
              return [...counts.keys()]
                .sort((a, b) => counts.get(b) - counts.get(a) || (a < b ? -1 : a > b ? 1 : 0))
                .slice(0, k);
            }
            """,
        ),
        _p(
            451, 'Sort Characters By Frequency', 'Medium',
            'Count, sort the characters by how common they are, then repeat each one.',
            'O(n log n) time, O(n) space',
            """
            function frequencySort(s) {
              const counts = new Map();
              for (const ch of s) counts.set(ch, (counts.get(ch) || 0) + 1);
              return [...counts.keys()]
                .sort((a, b) => counts.get(b) - counts.get(a) || (a < b ? -1 : a > b ? 1 : 0))
                .map((ch) => ch.repeat(counts.get(ch)))
                .join('');
            }
            """,
        ),
        _p(
            378, 'Kth Smallest Element in a Sorted Matrix', 'Medium',
            'The matrix is small enough to flatten and sort — no heap in the language.',
            'O(n log n) time, O(n) space',
            """
            function kthSmallest(matrix, k) {
              const flat = [];
              for (const row of matrix) flat.push(...row);
              flat.sort((a, b) => a - b);
              return flat[k - 1];
            }
            """,
        ),
        _p(
            767, 'Reorganize String', 'Medium',
            "Take the commonest letter that isn't the one you just used, and repeat.",
            'O(n * n log n) time, O(n) space',
            """
            function reorganizeString(s) {
              const counts = new Map();
              for (const ch of s) counts.set(ch, (counts.get(ch) || 0) + 1);
              const out = [];
              let held = null;
              while (true) {
                const ready = [...counts.entries()].filter(([ch]) => ch !== held);
                if (ready.length === 0) break;
                ready.sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1));
                const [ch, count] = ready[0];
                out.push(ch);
                if (count === 1) counts.delete(ch);
                else counts.set(ch, count - 1);
                held = ch;
              }
              return out.length === s.length ? out.join('') : '';
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
        _p(
            802, 'Find Eventual Safe States', 'Medium',
            'Reverse every edge, then peel from the terminal nodes — whatever drains is safe.',
            'O(v + e) time, O(v + e) space',
            """
            function eventualSafeNodes(graph) {
              const n = graph.length;
              const reverse = Array.from({ length: n }, () => []);
              const outdegree = new Array(n).fill(0);
              for (let node = 0; node < n; node++) {
                outdegree[node] = graph[node].length;
                for (const next of graph[node]) reverse[next].push(node);
              }
              const queue = [];
              for (let i = 0; i < n; i++) if (outdegree[i] === 0) queue.push(i);
              const safe = [];
              let head = 0;
              while (head < queue.length) {
                const node = queue[head++];
                safe.push(node);
                for (const prev of reverse[node]) {
                  outdegree[prev]--;
                  if (outdegree[prev] === 0) queue.push(prev);
                }
              }
              return safe.sort((a, b) => a - b);
            }
            """,
        ),
        _p(
            1462, 'Course Schedule IV', 'Medium',
            'Peel in order, and let each course inherit the prerequisite set of everything before it.',
            'O(v * e) time, O(v * v) space',
            """
            function checkIfPrerequisite(numCourses, prerequisites, queries) {
              const graph = Array.from({ length: numCourses }, () => []);
              const indegree = new Array(numCourses).fill(0);
              for (const [prereq, course] of prerequisites) {
                graph[prereq].push(course);
                indegree[course]++;
              }
              const needs = Array.from({ length: numCourses }, () => new Set());
              const queue = [];
              for (let i = 0; i < numCourses; i++) if (indegree[i] === 0) queue.push(i);
              let head = 0;
              while (head < queue.length) {
                const node = queue[head++];
                for (const next of graph[node]) {
                  needs[next].add(node);
                  for (const earlier of needs[node]) needs[next].add(earlier);
                  indegree[next]--;
                  if (indegree[next] === 0) queue.push(next);
                }
              }
              return queries.map(([prereq, course]) => needs[course].has(prereq));
            }
            """,
        ),
        _p(
            2115, 'Find All Possible Recipes from Given Supplies', 'Medium',
            'Ingredients are prerequisites: a recipe unlocks once its indegree of missing items hits zero.',
            'O(v + e) time, O(v + e) space',
            """
            function findAllRecipes(recipes, ingredients, supplies) {
              const graph = new Map();
              const indegree = new Map();
              for (const recipe of recipes) indegree.set(recipe, 0);
              for (let i = 0; i < recipes.length; i++) {
                for (const item of ingredients[i]) {
                  if (!graph.has(item)) graph.set(item, []);
                  graph.get(item).push(recipes[i]);
                  indegree.set(recipes[i], indegree.get(recipes[i]) + 1);
                }
              }
              const queue = [...supplies];
              const made = [];
              let head = 0;
              while (head < queue.length) {
                const item = queue[head++];
                for (const recipe of graph.get(item) || []) {
                  indegree.set(recipe, indegree.get(recipe) - 1);
                  if (indegree.get(recipe) === 0) {
                    made.push(recipe);
                    queue.push(recipe);
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
            function minimumSemesters(n, relations) {
              const graph = Array.from({ length: n + 1 }, () => []);
              const indegree = new Array(n + 1).fill(0);
              for (const [prereq, course] of relations) {
                graph[prereq].push(course);
                indegree[course]++;
              }
              let queue = [];
              for (let i = 1; i <= n; i++) if (indegree[i] === 0) queue.push(i);
              let studied = 0;
              let semesters = 0;
              while (queue.length) {
                semesters++;
                const next = [];
                for (const node of queue) {
                  studied++;
                  for (const course of graph[node]) {
                    indegree[course]--;
                    if (indegree[course] === 0) next.push(course);
                  }
                }
                queue = next;
              }
              return studied === n ? semesters : -1;
            }
            """,
        ),
        _p(
            269, 'Alien Dictionary', 'Hard',
            'Adjacent words give one letter order each; the first difference is the only edge they prove.',
            'O(c) time, O(1) space',
            """
            function alienOrder(words) {
              const graph = new Map();
              const indegree = new Map();
              for (const word of words) {
                for (const ch of word) {
                  if (!graph.has(ch)) graph.set(ch, new Set());
                  if (!indegree.has(ch)) indegree.set(ch, 0);
                }
              }
              for (let i = 0; i + 1 < words.length; i++) {
                const first = words[i];
                const second = words[i + 1];
                let split = false;
                const shorter = Math.min(first.length, second.length);
                for (let j = 0; j < shorter; j++) {
                  if (first[j] !== second[j]) {
                    if (!graph.get(first[j]).has(second[j])) {
                      graph.get(first[j]).add(second[j]);
                      indegree.set(second[j], indegree.get(second[j]) + 1);
                    }
                    split = true;
                    break;
                  }
                }
                if (!split && first.length > second.length) return '';
              }
              const queue = [];
              for (const [ch, count] of indegree) if (count === 0) queue.push(ch);
              const order = [];
              let head = 0;
              while (head < queue.length) {
                const ch = queue[head++];
                order.push(ch);
                for (const next of graph.get(ch)) {
                  indegree.set(next, indegree.get(next) - 1);
                  if (indegree.get(next) === 0) queue.push(next);
                }
              }
              return order.length === indegree.size ? order.join('') : '';
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
        _p(
            746, 'Min Cost Climbing Stairs', 'Easy',
            'The cost of a step is its own plus the cheaper of the two ways off it.',
            'O(n) time, O(1) space',
            """
            function minCostClimbingStairs(cost) {
              let one = 0;
              let two = 0;
              for (let i = 2; i <= cost.length; i++) {
                const next = Math.min(one + cost[i - 1], two + cost[i - 2]);
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
            function longestCommonSubsequence(first, second) {
              const grid = Array.from({ length: first.length + 1 }, () =>
                new Array(second.length + 1).fill(0)
              );
              for (let i = first.length - 1; i >= 0; i--) {
                for (let j = second.length - 1; j >= 0; j--) {
                  if (first[i] === second[j]) grid[i][j] = 1 + grid[i + 1][j + 1];
                  else grid[i][j] = Math.max(grid[i + 1][j], grid[i][j + 1]);
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
            function wordBreak(text, words) {
              const reachable = new Array(text.length + 1).fill(false);
              reachable[0] = true;
              for (let end = 1; end <= text.length; end++) {
                for (const word of words) {
                  const start = end - word.length;
                  if (start >= 0 && reachable[start] && text.slice(start, end) === word) {
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
            function maxProduct(nums) {
              let best = nums[0];
              let high = nums[0];
              let low = nums[0];
              for (let i = 1; i < nums.length; i++) {
                const n = nums[i];
                const options = [n, high * n, low * n];
                high = Math.max(...options);
                low = Math.min(...options);
                if (high > best) best = high;
              }
              return best;
            }
            """,
        ),
    ),
)
