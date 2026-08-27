"""
C patterns 5 to 8, split out of `problems_c` to keep each file a readable
length. `problems_c.PATTERNS` stitches all of them together.

The tree patterns need a queue, and C does not have one, so `c_common`
supplies a flat array queue the same way it supplies the hash map. Everything
else here is the algorithm with the bookkeeping C makes you do yourself:
lengths travel beside pointers, and anything returned is malloc'd.
"""

from __future__ import annotations

from code_coach.leetcode.c_common import (
    LIMITS,
    LIST_NODE,
    STDBOOL,
    STDLIB,
    STRING_H,
    TREE_NODE,
    _p,
)
from code_coach.leetcode.problems import Pattern

# ── 5. Linked lists ─────────────────────────────────────────

_LINKED_LIST = Pattern(
    id="lc-linked-list",
    name="Linked Lists",
    order=5,
    blurb="Nodes joined by ->next - you can only walk forward, so save what you need.",
    tell="Reversing, merging, or finding a position relative to the end.",
    preamble=(STDLIB, STDBOOL, LIST_NODE),
    problems=(
        _p(
            206, "Reverse Linked List", "Easy",
            "Save next, flip the arrow backward, then step both cursors forward.",
            "O(n) time, O(1) space",
            """
            struct ListNode *reverseList(struct ListNode *head) {
                struct ListNode *prev = NULL;
                while (head) {
                    struct ListNode *next = head->next;
                    head->next = prev;
                    prev = head;
                    head = next;
                }
                return prev;
            }
            """,
        ),
        _p(
            21, "Merge Two Sorted Lists", "Easy",
            "A dummy head on the stack means you never special-case the first "
            "node, and nothing has to be freed.",
            "O(n + m) time, O(1) space",
            """
            struct ListNode *mergeTwoLists(struct ListNode *list1,
                                           struct ListNode *list2) {
                struct ListNode dummy;
                dummy.next = NULL;
                struct ListNode *tail = &dummy;
                while (list1 && list2) {
                    if (list1->val <= list2->val) {
                        tail->next = list1;
                        list1 = list1->next;
                    } else {
                        tail->next = list2;
                        list2 = list2->next;
                    }
                    tail = tail->next;
                }
                tail->next = list1 ? list1 : list2;
                return dummy.next;
            }
            """,
        ),
        _p(
            141, "Linked List Cycle", "Easy",
            "Fast moves two, slow moves one - in a loop they must collide. "
            "Compare the pointers, not the values.",
            "O(n) time, O(1) space",
            """
            bool hasCycle(struct ListNode *head) {
                struct ListNode *slow = head;
                struct ListNode *fast = head;
                while (fast && fast->next) {
                    slow = slow->next;
                    fast = fast->next->next;
                    if (slow == fast) {
                        return true;
                    }
                }
                return false;
            }
            """,
        ),
        _p(
            19, "Remove Nth Node From End", "Medium",
            "Start fast n nodes ahead; when it ends, slow is on the node before.",
            "O(n) time, O(1) space",
            """
            struct ListNode *removeNthFromEnd(struct ListNode *head, int n) {
                struct ListNode dummy;
                dummy.next = head;
                struct ListNode *slow = &dummy;
                struct ListNode *fast = &dummy;
                for (int i = 0; i < n; i++) {
                    fast = fast->next;
                }
                while (fast->next) {
                    slow = slow->next;
                    fast = fast->next;
                }
                slow->next = slow->next->next;
                return dummy.next;
            }
            """,
        ),
        _p(
            876, "Middle of the Linked List", "Easy",
            "One pointer takes two steps per the other's one, so it ends at "
            "twice the distance.",
            "O(n) time, O(1) space",
            """
            struct ListNode *middleNode(struct ListNode *head) {
                struct ListNode *slow = head;
                struct ListNode *fast = head;
                while (fast && fast->next) {
                    slow = slow->next;
                    fast = fast->next->next;
                }
                return slow;
            }
            """,
        ),
        _p(
            83, "Remove Duplicates from Sorted List", "Easy",
            "Sorted means duplicates are neighbours, so one pass and a skipped "
            "link does it.",
            "O(n) time, O(1) space",
            """
            struct ListNode *deleteDuplicates(struct ListNode *head) {
                struct ListNode *node = head;
                while (node && node->next) {
                    if (node->val == node->next->val) {
                        node->next = node->next->next;
                    } else {
                        node = node->next;
                    }
                }
                return head;
            }
            """,
        ),
        _p(
            234, "Palindrome Linked List", "Easy",
            "Find the middle, reverse the second half, then walk the two halves "
            "together.",
            "O(n) time, O(1) space",
            """
            bool isPalindromeList(struct ListNode *head) {
                struct ListNode *slow = head;
                struct ListNode *fast = head;
                while (fast && fast->next) {
                    slow = slow->next;
                    fast = fast->next->next;
                }
                struct ListNode *second = NULL;
                while (slow) {
                    struct ListNode *next = slow->next;
                    slow->next = second;
                    second = slow;
                    slow = next;
                }
                struct ListNode *first = head;
                while (second) {
                    if (first->val != second->val) {
                        return false;
                    }
                    first = first->next;
                    second = second->next;
                }
                return true;
            }
            """,
        ),
        _p(
            2, "Add Two Numbers", "Medium",
            "Long addition, digit by digit. The carry is the only thing you have "
            "to remember.",
            "O(n) time, O(n) space",
            """
            struct ListNode *addTwoNumbers(struct ListNode *first,
                                           struct ListNode *second) {
                struct ListNode head;
                head.next = NULL;
                struct ListNode *node = &head;
                int carry = 0;
                while (first || second || carry) {
                    int total = carry;
                    if (first) {
                        total += first->val;
                        first = first->next;
                    }
                    if (second) {
                        total += second->val;
                        second = second->next;
                    }
                    carry = total / 10;
                    node->next = malloc(sizeof(struct ListNode));
                    node->next->val = total % 10;
                    node->next->next = NULL;
                    node = node->next;
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
    blurb="Halve the search space every step by asking one yes/no question.",
    tell="Sorted input, or 'smallest value that works' over a numeric range.",
    preamble=(STDLIB, STDBOOL, LIMITS),
    problems=(
        _p(
            704, "Binary Search", "Easy",
            "Closed range [low, high]: shrink past mid every time. low + (high "
            "- low) / 2 rather than (low + high) / 2, which can overflow.",
            "O(log n) time, O(1) space",
            """
            int search(int *nums, int numsSize, int target) {
                int low = 0;
                int high = numsSize - 1;
                while (low <= high) {
                    int mid = low + (high - low) / 2;
                    if (nums[mid] == target) {
                        return mid;
                    }
                    if (nums[mid] < target) {
                        low = mid + 1;
                    } else {
                        high = mid - 1;
                    }
                }
                return -1;
            }
            """,
        ),
        _p(
            35, "Search Insert Position", "Easy",
            "Half-open range [low, high): low lands on the insert point.",
            "O(log n) time, O(1) space",
            """
            int searchInsert(int *nums, int numsSize, int target) {
                int low = 0;
                int high = numsSize;
                while (low < high) {
                    int mid = low + (high - low) / 2;
                    if (nums[mid] < target) {
                        low = mid + 1;
                    } else {
                        high = mid;
                    }
                }
                return low;
            }
            """,
        ),
        _p(
            153, "Find Minimum in Rotated Sorted Array", "Medium",
            "Compare mid to the right end to learn which half holds the dip.",
            "O(log n) time, O(1) space",
            """
            int findMin(int *nums, int numsSize) {
                int low = 0;
                int high = numsSize - 1;
                while (low < high) {
                    int mid = low + (high - low) / 2;
                    if (nums[mid] > nums[high]) {
                        low = mid + 1;
                    } else {
                        high = mid;
                    }
                }
                return nums[low];
            }
            """,
        ),
        _p(
            33, "Search in Rotated Sorted Array", "Medium",
            "One half is always sorted - check if the target lies inside it.",
            "O(log n) time, O(1) space",
            """
            int searchRotated(int *nums, int numsSize, int target) {
                int low = 0;
                int high = numsSize - 1;
                while (low <= high) {
                    int mid = low + (high - low) / 2;
                    if (nums[mid] == target) {
                        return mid;
                    }
                    if (nums[low] <= nums[mid]) {
                        if (nums[low] <= target && target < nums[mid]) {
                            high = mid - 1;
                        } else {
                            low = mid + 1;
                        }
                    } else {
                        if (nums[mid] < target && target <= nums[high]) {
                            low = mid + 1;
                        } else {
                            high = mid - 1;
                        }
                    }
                }
                return -1;
            }
            """,
        ),
        _p(
            875, "Koko Eating Bananas", "Medium",
            "Binary search the ANSWER: the slowest speed that still finishes in "
            "time. Count the hours as long long, or a big pile overflows.",
            "O(n log m) time, O(1) space",
            """
            int minEatingSpeed(int *piles, int pilesSize, int h) {
                int low = 1;
                int high = piles[0];
                for (int i = 1; i < pilesSize; i++) {
                    if (piles[i] > high) {
                        high = piles[i];
                    }
                }
                while (low < high) {
                    int speed = low + (high - low) / 2;
                    long long hours = 0;
                    for (int i = 0; i < pilesSize; i++) {
                        hours += (piles[i] + speed - 1) / speed;
                    }
                    if (hours <= h) {
                        high = speed;
                    } else {
                        low = speed + 1;
                    }
                }
                return low;
            }
            """,
        ),
        _p(
            278, "First Bad Version", "Easy",
            "Search for a boundary: keep the mid when it's bad, discard it when "
            "it isn't. The checker arrives as a function pointer.",
            "O(log n) time, O(1) space",
            """
            int firstBadVersion(int n, bool (*isBad)(int)) {
                int low = 1;
                int high = n;
                while (low < high) {
                    int mid = low + (high - low) / 2;
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
            34, "Find First and Last Position of Element in Sorted Array",
            "Medium",
            "Two searches, not one: the same helper finds the left edge and then "
            "the right.",
            "O(log n) time, O(1) space",
            """
            static int findEdge(int *nums, int numsSize, int target,
                                bool wantFirst) {
                int low = 0;
                int high = numsSize - 1;
                int found = -1;
                while (low <= high) {
                    int mid = low + (high - low) / 2;
                    if (nums[mid] == target) {
                        found = mid;
                        if (wantFirst) {
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

            int *searchRange(int *nums, int numsSize, int target,
                             int *returnSize) {
                int *out = malloc(2 * sizeof(int));
                out[0] = findEdge(nums, numsSize, target, true);
                out[1] = findEdge(nums, numsSize, target, false);
                *returnSize = 2;
                return out;
            }
            """,
        ),
        _p(
            74, "Search a 2D Matrix", "Medium",
            "A sorted matrix is one sorted list folded up, so divide the index "
            "to unfold it.",
            "O(log(m * n)) time, O(1) space",
            """
            bool searchMatrix(int **matrix, int matrixSize, int *matrixColSize,
                              int target) {
                if (matrixSize == 0 || matrixColSize[0] == 0) {
                    return false;
                }
                int cols = matrixColSize[0];
                int low = 0;
                int high = matrixSize * cols - 1;
                while (low <= high) {
                    int mid = low + (high - low) / 2;
                    int value = matrix[mid / cols][mid % cols];
                    if (value == target) {
                        return true;
                    }
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
    blurb="Recursion down one branch at a time: solve the children, combine, return.",
    tell="The answer for a node is built from the answers for its subtrees.",
    preamble=(STDLIB, STDBOOL, LIMITS, TREE_NODE),
    problems=(
        _p(
            104, "Maximum Depth of Binary Tree", "Easy",
            "Depth here = 1 + the deeper of my two children.",
            "O(n) time, O(h) space",
            """
            int maxDepth(struct TreeNode *root) {
                if (!root) {
                    return 0;
                }
                int left = maxDepth(root->left);
                int right = maxDepth(root->right);
                return 1 + (left > right ? left : right);
            }
            """,
        ),
        _p(
            226, "Invert Binary Tree", "Easy",
            "Swap the children, then let recursion handle each side.",
            "O(n) time, O(h) space",
            """
            struct TreeNode *invertTree(struct TreeNode *root) {
                if (!root) {
                    return NULL;
                }
                struct TreeNode *left = invertTree(root->right);
                struct TreeNode *right = invertTree(root->left);
                root->left = left;
                root->right = right;
                return root;
            }
            """,
        ),
        _p(
            112, "Path Sum", "Easy",
            "Subtract as you descend; at a leaf ask whether the remainder fits.",
            "O(n) time, O(h) space",
            """
            bool hasPathSum(struct TreeNode *root, int targetSum) {
                if (!root) {
                    return false;
                }
                if (!root->left && !root->right) {
                    return targetSum == root->val;
                }
                int rest = targetSum - root->val;
                return hasPathSum(root->left, rest) ||
                       hasPathSum(root->right, rest);
            }
            """,
        ),
        _p(
            543, "Diameter of Binary Tree", "Easy",
            "Return depth upward, but record left + right as a candidate answer. "
            "C has no closures, so the best travels as a pointer.",
            "O(n) time, O(h) space",
            """
            static int depthTracking(struct TreeNode *node, int *best) {
                if (!node) {
                    return 0;
                }
                int left = depthTracking(node->left, best);
                int right = depthTracking(node->right, best);
                if (left + right > *best) {
                    *best = left + right;
                }
                return 1 + (left > right ? left : right);
            }

            int diameterOfBinaryTree(struct TreeNode *root) {
                int best = 0;
                depthTracking(root, &best);
                return best;
            }
            """,
        ),
        _p(
            98, "Validate Binary Search Tree", "Medium",
            "Carry an allowed (low, high) range down instead of checking "
            "neighbours. long long bounds, so a node holding INT_MIN passes.",
            "O(n) time, O(h) space",
            """
            static bool withinRange(struct TreeNode *node, long long low,
                                    long long high) {
                if (!node) {
                    return true;
                }
                if (node->val <= low || node->val >= high) {
                    return false;
                }
                return withinRange(node->left, low, node->val) &&
                       withinRange(node->right, node->val, high);
            }

            bool isValidBST(struct TreeNode *root) {
                return withinRange(root, LLONG_MIN, LLONG_MAX);
            }
            """,
        ),
        _p(
            100, "Same Tree", "Easy",
            "Two trees match when their roots match and both pairs of children do.",
            "O(n) time, O(h) space",
            """
            bool isSameTree(struct TreeNode *first, struct TreeNode *second) {
                if (!first && !second) {
                    return true;
                }
                if (!first || !second) {
                    return false;
                }
                if (first->val != second->val) {
                    return false;
                }
                return isSameTree(first->left, second->left) &&
                       isSameTree(first->right, second->right);
            }
            """,
        ),
        _p(
            101, "Symmetric Tree", "Easy",
            "A mirror compares left against right - the recursion crosses over.",
            "O(n) time, O(h) space",
            """
            static bool mirrors(struct TreeNode *left, struct TreeNode *right) {
                if (!left && !right) {
                    return true;
                }
                if (!left || !right) {
                    return false;
                }
                if (left->val != right->val) {
                    return false;
                }
                return mirrors(left->left, right->right) &&
                       mirrors(left->right, right->left);
            }

            bool isSymmetric(struct TreeNode *root) {
                return mirrors(root, root);
            }
            """,
        ),
        _p(
            236, "Lowest Common Ancestor of a Binary Tree", "Medium",
            "A node whose two sides each found something is the meeting point.",
            "O(n) time, O(h) space",
            """
            struct TreeNode *lowestCommonAncestor(struct TreeNode *root,
                                                  struct TreeNode *p,
                                                  struct TreeNode *q) {
                if (!root || root == p || root == q) {
                    return root;
                }
                struct TreeNode *left = lowestCommonAncestor(root->left, p, q);
                struct TreeNode *right = lowestCommonAncestor(root->right, p, q);
                if (left && right) {
                    return root;
                }
                return left ? left : right;
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
    blurb="A queue walks the tree level by level instead of branch by branch.",
    tell="The question mentions levels, rows, depth order, or 'nearest'.",
    preamble=(STDLIB, STRING_H, STDBOOL, LIMITS, TREE_NODE),
    problems=(
        _p(
            102, "Binary Tree Level Order Traversal", "Medium",
            "Snapshot the queue length first - that's exactly one level's worth. "
            "A plain array with head and tail indexes is the whole queue.",
            "O(n) time, O(n) space",
            """
            #define MAX_NODES 4096

            int **levelOrder(struct TreeNode *root, int *returnSize,
                             int **columnSizes) {
                if (!root) {
                    *returnSize = 0;
                    *columnSizes = NULL;
                    return NULL;
                }
                struct TreeNode **queue =
                    malloc(MAX_NODES * sizeof(struct TreeNode *));
                int head = 0;
                int tail = 0;
                queue[tail++] = root;
                int **levels = malloc(MAX_NODES * sizeof(int *));
                int *sizes = malloc(MAX_NODES * sizeof(int));
                int depth = 0;
                while (head < tail) {
                    int size = tail - head;
                    levels[depth] = malloc(size * sizeof(int));
                    sizes[depth] = size;
                    for (int i = 0; i < size; i++) {
                        struct TreeNode *node = queue[head++];
                        levels[depth][i] = node->val;
                        if (node->left) {
                            queue[tail++] = node->left;
                        }
                        if (node->right) {
                            queue[tail++] = node->right;
                        }
                    }
                    depth++;
                }
                free(queue);
                *returnSize = depth;
                *columnSizes = sizes;
                return levels;
            }
            """,
        ),
        _p(
            199, "Binary Tree Right Side View", "Medium",
            "Keep the last node of every level.",
            "O(n) time, O(n) space",
            """
            int *rightSideView(struct TreeNode *root, int *returnSize) {
                *returnSize = 0;
                if (!root) {
                    return NULL;
                }
                struct TreeNode **queue =
                    malloc(MAX_NODES * sizeof(struct TreeNode *));
                int head = 0;
                int tail = 0;
                queue[tail++] = root;
                int *view = malloc(MAX_NODES * sizeof(int));
                int seen = 0;
                while (head < tail) {
                    int size = tail - head;
                    for (int i = 0; i < size; i++) {
                        struct TreeNode *node = queue[head++];
                        if (i == size - 1) {
                            view[seen++] = node->val;
                        }
                        if (node->left) {
                            queue[tail++] = node->left;
                        }
                        if (node->right) {
                            queue[tail++] = node->right;
                        }
                    }
                }
                free(queue);
                *returnSize = seen;
                return view;
            }
            """,
        ),
        _p(
            103, "Binary Tree Zigzag Level Order", "Medium",
            "Same level walk - just reverse every other row before storing it.",
            "O(n) time, O(n) space",
            """
            int **zigzagLevelOrder(struct TreeNode *root, int *returnSize,
                                   int **columnSizes) {
                if (!root) {
                    *returnSize = 0;
                    *columnSizes = NULL;
                    return NULL;
                }
                struct TreeNode **queue =
                    malloc(MAX_NODES * sizeof(struct TreeNode *));
                int head = 0;
                int tail = 0;
                queue[tail++] = root;
                int **levels = malloc(MAX_NODES * sizeof(int *));
                int *sizes = malloc(MAX_NODES * sizeof(int));
                int depth = 0;
                bool leftToRight = true;
                while (head < tail) {
                    int size = tail - head;
                    int *level = malloc(size * sizeof(int));
                    for (int i = 0; i < size; i++) {
                        struct TreeNode *node = queue[head++];
                        int slot = leftToRight ? i : size - 1 - i;
                        level[slot] = node->val;
                        if (node->left) {
                            queue[tail++] = node->left;
                        }
                        if (node->right) {
                            queue[tail++] = node->right;
                        }
                    }
                    levels[depth] = level;
                    sizes[depth] = size;
                    depth++;
                    leftToRight = !leftToRight;
                }
                free(queue);
                *returnSize = depth;
                *columnSizes = sizes;
                return levels;
            }
            """,
        ),
        _p(
            111, "Minimum Depth of Binary Tree", "Easy",
            "BFS stops at the first leaf it meets - DFS would walk the whole "
            "tree first.",
            "O(n) time, O(n) space",
            """
            int minDepth(struct TreeNode *root) {
                if (!root) {
                    return 0;
                }
                struct TreeNode **queue =
                    malloc(MAX_NODES * sizeof(struct TreeNode *));
                int head = 0;
                int tail = 0;
                queue[tail++] = root;
                int depth = 1;
                while (head < tail) {
                    int size = tail - head;
                    for (int i = 0; i < size; i++) {
                        struct TreeNode *node = queue[head++];
                        if (!node->left && !node->right) {
                            free(queue);
                            return depth;
                        }
                        if (node->left) {
                            queue[tail++] = node->left;
                        }
                        if (node->right) {
                            queue[tail++] = node->right;
                        }
                    }
                    depth++;
                }
                free(queue);
                return depth;
            }
            """,
        ),
        _p(
            637, "Average of Levels in Binary Tree", "Easy",
            "One row at a time, so the divisor is just that row's length. Sum in "
            "long long: a full row of large values overflows int.",
            "O(n) time, O(n) space",
            """
            double *averageOfLevels(struct TreeNode *root, int *returnSize) {
                *returnSize = 0;
                if (!root) {
                    return NULL;
                }
                struct TreeNode **queue =
                    malloc(MAX_NODES * sizeof(struct TreeNode *));
                int head = 0;
                int tail = 0;
                queue[tail++] = root;
                double *averages = malloc(MAX_NODES * sizeof(double));
                int depth = 0;
                while (head < tail) {
                    int size = tail - head;
                    long long total = 0;
                    for (int i = 0; i < size; i++) {
                        struct TreeNode *node = queue[head++];
                        total += node->val;
                        if (node->left) {
                            queue[tail++] = node->left;
                        }
                        if (node->right) {
                            queue[tail++] = node->right;
                        }
                    }
                    averages[depth++] = (double)total / size;
                }
                free(queue);
                *returnSize = depth;
                return averages;
            }
            """,
        ),
        _p(
            515, "Find Largest Value in Each Tree Row", "Medium",
            "Same row walk as the average - swap the running total for a running "
            "max. Start at INT_MIN, or an all-negative row comes back wrong.",
            "O(n) time, O(n) space",
            """
            int *largestValues(struct TreeNode *root, int *returnSize) {
                *returnSize = 0;
                if (!root) {
                    return NULL;
                }
                struct TreeNode **queue =
                    malloc(MAX_NODES * sizeof(struct TreeNode *));
                int head = 0;
                int tail = 0;
                queue[tail++] = root;
                int *largest = malloc(MAX_NODES * sizeof(int));
                int depth = 0;
                while (head < tail) {
                    int size = tail - head;
                    int best = INT_MIN;
                    for (int i = 0; i < size; i++) {
                        struct TreeNode *node = queue[head++];
                        if (node->val > best) {
                            best = node->val;
                        }
                        if (node->left) {
                            queue[tail++] = node->left;
                        }
                        if (node->right) {
                            queue[tail++] = node->right;
                        }
                    }
                    largest[depth++] = best;
                }
                free(queue);
                *returnSize = depth;
                return largest;
            }
            """,
        ),
        _p(
            1161, "Maximum Level Sum of a Binary Tree", "Medium",
            "Number the levels as you go and keep the best - ties go to the "
            "shallower one, which strict greater-than gives you.",
            "O(n) time, O(n) space",
            """
            int maxLevelSum(struct TreeNode *root) {
                if (!root) {
                    return 0;
                }
                struct TreeNode **queue =
                    malloc(MAX_NODES * sizeof(struct TreeNode *));
                int head = 0;
                int tail = 0;
                queue[tail++] = root;
                int level = 0;
                int bestLevel = 1;
                long long bestSum = LLONG_MIN;
                while (head < tail) {
                    level++;
                    int size = tail - head;
                    long long total = 0;
                    for (int i = 0; i < size; i++) {
                        struct TreeNode *node = queue[head++];
                        total += node->val;
                        if (node->left) {
                            queue[tail++] = node->left;
                        }
                        if (node->right) {
                            queue[tail++] = node->right;
                        }
                    }
                    if (total > bestSum) {
                        bestSum = total;
                        bestLevel = level;
                    }
                }
                free(queue);
                return bestLevel;
            }
            """,
        ),
        _p(
            662, "Maximum Width of Binary Tree", "Medium",
            "Queue the heap index with each node; a row's width is last minus "
            "first plus one. Rebase each row at zero or the index overflows.",
            "O(n) time, O(n) space",
            """
            int widthOfBinaryTree(struct TreeNode *root) {
                if (!root) {
                    return 0;
                }
                struct TreeNode **queue =
                    malloc(MAX_NODES * sizeof(struct TreeNode *));
                unsigned long long *indexes =
                    malloc(MAX_NODES * sizeof(unsigned long long));
                int head = 0;
                int tail = 0;
                queue[tail] = root;
                indexes[tail] = 0;
                tail++;
                unsigned long long widest = 0;
                while (head < tail) {
                    int size = tail - head;
                    unsigned long long first = indexes[head];
                    unsigned long long last = first;
                    for (int i = 0; i < size; i++) {
                        struct TreeNode *node = queue[head];
                        unsigned long long index = indexes[head] - first;
                        head++;
                        last = index;
                        if (node->left) {
                            queue[tail] = node->left;
                            indexes[tail] = index * 2;
                            tail++;
                        }
                        if (node->right) {
                            queue[tail] = node->right;
                            indexes[tail] = index * 2 + 1;
                            tail++;
                        }
                    }
                    if (last + 1 > widest) {
                        widest = last + 1;
                    }
                }
                free(queue);
                free(indexes);
                return (int)widest;
            }
            """,
        ),
    ),
)
