"""
C++ patterns 5 to 13, split out of `problems_cpp` to keep each file a
readable length. `problems_cpp.PATTERNS` stitches them together.

Where this differs from the Rust bank is instructive. Raw pointers can alias
freely, so #141 is the ordinary fast/slow walk on a real list rather than the
next-index reframing Rust needed. And `priority_queue` is a max-heap like
Rust's `BinaryHeap`, so the same inversion applies against Python: where
Python negates to pop the largest, C++ asks for `greater<>` to pop the
smallest.
"""

from __future__ import annotations

from code_coach.leetcode.cpp_common import (
    ALGORITHM,
    CLIMITS,
    FUNCTIONAL,
    GRAPH_NODE,
    LIST_NODE,
    MAPS,
    ORDERED,
    QUEUE,
    STRING,
    TUPLE,
    TREE_NODE,
    USING,
    VECTOR,
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
    preamble=(VECTOR, USING, LIST_NODE),
    problems=(
        _p(
            206, "Reverse Linked List", "Easy",
            "Save next, flip the arrow backward, then step both cursors forward.",
            "O(n) time, O(1) space",
            """
            ListNode* reverseList(ListNode* head) {
                ListNode* prev = nullptr;
                while (head) {
                    ListNode* next = head->next;
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
            "A dummy head means you never special-case the first node.",
            "O(n + m) time, O(1) space",
            """
            ListNode* mergeTwoLists(ListNode* list1, ListNode* list2) {
                ListNode dummy;
                ListNode* tail = &dummy;
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
            bool hasCycle(ListNode* head) {
                ListNode* slow = head;
                ListNode* fast = head;
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
            ListNode* removeNthFromEnd(ListNode* head, int n) {
                ListNode dummy(0, head);
                ListNode* slow = &dummy;
                ListNode* fast = &dummy;
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
            ListNode* middleNode(ListNode* head) {
                ListNode* slow = head;
                ListNode* fast = head;
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
            ListNode* deleteDuplicates(ListNode* head) {
                ListNode* node = head;
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
            bool isPalindromeList(ListNode* head) {
                ListNode* slow = head;
                ListNode* fast = head;
                while (fast && fast->next) {
                    slow = slow->next;
                    fast = fast->next->next;
                }
                ListNode* second = nullptr;
                while (slow) {
                    ListNode* next = slow->next;
                    slow->next = second;
                    second = slow;
                    slow = next;
                }
                ListNode* first = head;
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
            ListNode* addTwoNumbers(ListNode* first, ListNode* second) {
                ListNode head;
                ListNode* node = &head;
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
                    node->next = new ListNode(total % 10);
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
    preamble=(VECTOR, ALGORITHM, USING),
    problems=(
        _p(
            704, "Binary Search", "Easy",
            "Closed range [low, high]: shrink past mid every time.",
            "O(log n) time, O(1) space",
            """
            int search(vector<int>& nums, int target) {
                int low = 0;
                int high = (int)nums.size() - 1;
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
            int searchInsert(vector<int>& nums, int target) {
                int low = 0;
                int high = (int)nums.size();
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
            int findMin(vector<int>& nums) {
                int low = 0;
                int high = (int)nums.size() - 1;
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
            int searchRotated(vector<int>& nums, int target) {
                int low = 0;
                int high = (int)nums.size() - 1;
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
            "time. Count the hours in long long, or a big pile overflows.",
            "O(n log m) time, O(1) space",
            """
            int minEatingSpeed(vector<int>& piles, int h) {
                int low = 1;
                int high = *max_element(piles.begin(), piles.end());
                while (low < high) {
                    int speed = low + (high - low) / 2;
                    long long hours = 0;
                    for (int pile : piles) {
                        hours += (pile + speed - 1) / speed;
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
            "it isn't. low + (high - low) / 2 cannot overflow.",
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
            "Two searches, not one: the same loop finds the left edge and then "
            "the right.",
            "O(log n) time, O(1) space",
            """
            vector<int> searchRange(vector<int>& nums, int target) {
                auto edge = [&](bool first) {
                    int low = 0;
                    int high = (int)nums.size() - 1;
                    int found = -1;
                    while (low <= high) {
                        int mid = low + (high - low) / 2;
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
                };
                return {edge(true), edge(false)};
            }
            """,
        ),
        _p(
            74, "Search a 2D Matrix", "Medium",
            "A sorted matrix is one sorted list folded up, so divide the index "
            "to unfold it.",
            "O(log(m * n)) time, O(1) space",
            """
            bool searchMatrix(vector<vector<int>>& matrix, int target) {
                if (matrix.empty() || matrix[0].empty()) {
                    return false;
                }
                int rows = (int)matrix.size();
                int cols = (int)matrix[0].size();
                int low = 0;
                int high = rows * cols - 1;
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
    preamble=(VECTOR, ALGORITHM, CLIMITS, FUNCTIONAL, USING, TREE_NODE),
    problems=(
        _p(
            104, "Maximum Depth of Binary Tree", "Easy",
            "Depth here = 1 + the deeper of my two children.",
            "O(n) time, O(h) space",
            """
            int maxDepth(TreeNode* root) {
                if (!root) {
                    return 0;
                }
                return 1 + max(maxDepth(root->left), maxDepth(root->right));
            }
            """,
        ),
        _p(
            226, "Invert Binary Tree", "Easy",
            "Swap the children, then let recursion handle each side.",
            "O(n) time, O(h) space",
            """
            TreeNode* invertTree(TreeNode* root) {
                if (!root) {
                    return nullptr;
                }
                TreeNode* left = invertTree(root->right);
                TreeNode* right = invertTree(root->left);
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
            bool hasPathSum(TreeNode* root, int targetSum) {
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
            "Return depth upward, but record left + right as a candidate answer.",
            "O(n) time, O(h) space",
            """
            int diameterOfBinaryTree(TreeNode* root) {
                int best = 0;
                function<int(TreeNode*)> depth = [&](TreeNode* node) {
                    if (!node) {
                        return 0;
                    }
                    int left = depth(node->left);
                    int right = depth(node->right);
                    best = max(best, left + right);
                    return 1 + max(left, right);
                };
                depth(root);
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
            bool isValidBST(TreeNode* root) {
                function<bool(TreeNode*, long long, long long)> check =
                    [&](TreeNode* node, long long low, long long high) {
                        if (!node) {
                            return true;
                        }
                        if (node->val <= low || node->val >= high) {
                            return false;
                        }
                        return check(node->left, low, node->val) &&
                               check(node->right, node->val, high);
                    };
                return check(root, LLONG_MIN, LLONG_MAX);
            }
            """,
        ),
        _p(
            100, "Same Tree", "Easy",
            "Two trees match when their roots match and both pairs of children do.",
            "O(n) time, O(h) space",
            """
            bool isSameTree(TreeNode* first, TreeNode* second) {
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
            bool isSymmetric(TreeNode* root) {
                function<bool(TreeNode*, TreeNode*)> mirror =
                    [&](TreeNode* left, TreeNode* right) {
                        if (!left && !right) {
                            return true;
                        }
                        if (!left || !right) {
                            return false;
                        }
                        if (left->val != right->val) {
                            return false;
                        }
                        return mirror(left->left, right->right) &&
                               mirror(left->right, right->left);
                    };
                return mirror(root, root);
            }
            """,
        ),
        _p(
            236, "Lowest Common Ancestor of a Binary Tree", "Medium",
            "A node whose two sides each found something is the meeting point.",
            "O(n) time, O(h) space",
            """
            TreeNode* lowestCommonAncestor(TreeNode* root, TreeNode* p,
                                           TreeNode* q) {
                if (!root || root == p || root == q) {
                    return root;
                }
                TreeNode* left = lowestCommonAncestor(root->left, p, q);
                TreeNode* right = lowestCommonAncestor(root->right, p, q);
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
    preamble=(VECTOR, QUEUE, ALGORITHM, CLIMITS, USING, TREE_NODE),
    problems=(
        _p(
            102, "Binary Tree Level Order Traversal", "Medium",
            "Snapshot queue.size() first - that's exactly one level's worth.",
            "O(n) time, O(n) space",
            """
            vector<vector<int>> levelOrder(TreeNode* root) {
                vector<vector<int>> levels;
                if (!root) {
                    return levels;
                }
                queue<TreeNode*> pending;
                pending.push(root);
                while (!pending.empty()) {
                    int size = (int)pending.size();
                    vector<int> level;
                    for (int i = 0; i < size; i++) {
                        TreeNode* node = pending.front();
                        pending.pop();
                        level.push_back(node->val);
                        if (node->left) {
                            pending.push(node->left);
                        }
                        if (node->right) {
                            pending.push(node->right);
                        }
                    }
                    levels.push_back(level);
                }
                return levels;
            }
            """,
        ),
        _p(
            199, "Binary Tree Right Side View", "Medium",
            "Keep the last node of every level.",
            "O(n) time, O(n) space",
            """
            vector<int> rightSideView(TreeNode* root) {
                vector<int> view;
                if (!root) {
                    return view;
                }
                queue<TreeNode*> pending;
                pending.push(root);
                while (!pending.empty()) {
                    int size = (int)pending.size();
                    for (int i = 0; i < size; i++) {
                        TreeNode* node = pending.front();
                        pending.pop();
                        if (i == size - 1) {
                            view.push_back(node->val);
                        }
                        if (node->left) {
                            pending.push(node->left);
                        }
                        if (node->right) {
                            pending.push(node->right);
                        }
                    }
                }
                return view;
            }
            """,
        ),
        _p(
            103, "Binary Tree Zigzag Level Order", "Medium",
            "Same level walk - just reverse every other row before storing it.",
            "O(n) time, O(n) space",
            """
            vector<vector<int>> zigzagLevelOrder(TreeNode* root) {
                vector<vector<int>> levels;
                if (!root) {
                    return levels;
                }
                queue<TreeNode*> pending;
                pending.push(root);
                bool leftToRight = true;
                while (!pending.empty()) {
                    int size = (int)pending.size();
                    vector<int> level;
                    for (int i = 0; i < size; i++) {
                        TreeNode* node = pending.front();
                        pending.pop();
                        level.push_back(node->val);
                        if (node->left) {
                            pending.push(node->left);
                        }
                        if (node->right) {
                            pending.push(node->right);
                        }
                    }
                    if (!leftToRight) {
                        reverse(level.begin(), level.end());
                    }
                    levels.push_back(level);
                    leftToRight = !leftToRight;
                }
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
            int minDepth(TreeNode* root) {
                if (!root) {
                    return 0;
                }
                queue<TreeNode*> pending;
                pending.push(root);
                int depth = 1;
                while (!pending.empty()) {
                    int size = (int)pending.size();
                    for (int i = 0; i < size; i++) {
                        TreeNode* node = pending.front();
                        pending.pop();
                        if (!node->left && !node->right) {
                            return depth;
                        }
                        if (node->left) {
                            pending.push(node->left);
                        }
                        if (node->right) {
                            pending.push(node->right);
                        }
                    }
                    depth++;
                }
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
            vector<double> averageOfLevels(TreeNode* root) {
                vector<double> averages;
                if (!root) {
                    return averages;
                }
                queue<TreeNode*> pending;
                pending.push(root);
                while (!pending.empty()) {
                    int size = (int)pending.size();
                    long long total = 0;
                    for (int i = 0; i < size; i++) {
                        TreeNode* node = pending.front();
                        pending.pop();
                        total += node->val;
                        if (node->left) {
                            pending.push(node->left);
                        }
                        if (node->right) {
                            pending.push(node->right);
                        }
                    }
                    averages.push_back((double)total / size);
                }
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
            vector<int> largestValues(TreeNode* root) {
                vector<int> largest;
                if (!root) {
                    return largest;
                }
                queue<TreeNode*> pending;
                pending.push(root);
                while (!pending.empty()) {
                    int size = (int)pending.size();
                    int best = INT_MIN;
                    for (int i = 0; i < size; i++) {
                        TreeNode* node = pending.front();
                        pending.pop();
                        best = max(best, node->val);
                        if (node->left) {
                            pending.push(node->left);
                        }
                        if (node->right) {
                            pending.push(node->right);
                        }
                    }
                    largest.push_back(best);
                }
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
            int maxLevelSum(TreeNode* root) {
                if (!root) {
                    return 0;
                }
                queue<TreeNode*> pending;
                pending.push(root);
                int level = 0;
                int bestLevel = 1;
                long long bestSum = LLONG_MIN;
                while (!pending.empty()) {
                    level++;
                    int size = (int)pending.size();
                    long long total = 0;
                    for (int i = 0; i < size; i++) {
                        TreeNode* node = pending.front();
                        pending.pop();
                        total += node->val;
                        if (node->left) {
                            pending.push(node->left);
                        }
                        if (node->right) {
                            pending.push(node->right);
                        }
                    }
                    if (total > bestSum) {
                        bestSum = total;
                        bestLevel = level;
                    }
                }
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
            int widthOfBinaryTree(TreeNode* root) {
                if (!root) {
                    return 0;
                }
                unsigned long long widest = 0;
                queue<pair<TreeNode*, unsigned long long>> pending;
                pending.push({root, 0});
                while (!pending.empty()) {
                    int size = (int)pending.size();
                    unsigned long long first = pending.front().second;
                    unsigned long long last = first;
                    for (int i = 0; i < size; i++) {
                        auto [node, raw] = pending.front();
                        pending.pop();
                        unsigned long long index = raw - first;
                        last = index;
                        if (node->left) {
                            pending.push({node->left, index * 2});
                        }
                        if (node->right) {
                            pending.push({node->right, index * 2 + 1});
                        }
                    }
                    widest = max(widest, last + 1);
                }
                return (int)widest;
            }
            """,
        ),
    ),
)


# ── 9. Graphs and grids ─────────────────────────────────────

_GRAPH = Pattern(
    id="lc-graph",
    name="Graphs & Grids",
    order=9,
    blurb="Same DFS/BFS as trees, but you must mark visited - graphs have cycles.",
    tell="A grid of cells, or nodes with edges/neighbours.",
    preamble=(VECTOR, QUEUE, MAPS, ALGORITHM, FUNCTIONAL, USING, GRAPH_NODE),
    problems=(
        _p(
            733, "Flood Fill", "Easy",
            "Recurse to the four neighbours, stopping when the colour doesn't "
            "match.",
            "O(n) time, O(n) space",
            """
            vector<vector<int>> floodFill(vector<vector<int>>& image, int sr,
                                          int sc, int color) {
                int start = image[sr][sc];
                if (start == color) {
                    return image;
                }
                int rows = (int)image.size();
                int cols = (int)image[0].size();
                function<void(int, int)> fill = [&](int r, int c) {
                    if (r < 0 || r >= rows || c < 0 || c >= cols) {
                        return;
                    }
                    if (image[r][c] != start) {
                        return;
                    }
                    image[r][c] = color;
                    fill(r + 1, c);
                    fill(r - 1, c);
                    fill(r, c + 1);
                    fill(r, c - 1);
                };
                fill(sr, sc);
                return image;
            }
            """,
        ),
        _p(
            200, "Number of Islands", "Medium",
            "Each unvisited land cell starts an island; sink the whole thing.",
            "O(rows * cols) time, O(rows * cols) space",
            """
            int numIslands(vector<vector<char>>& grid) {
                if (grid.empty()) {
                    return 0;
                }
                int rows = (int)grid.size();
                int cols = (int)grid[0].size();
                int count = 0;
                function<void(int, int)> sink = [&](int r, int c) {
                    if (r < 0 || r >= rows || c < 0 || c >= cols) {
                        return;
                    }
                    if (grid[r][c] != '1') {
                        return;
                    }
                    grid[r][c] = '0';
                    sink(r + 1, c);
                    sink(r - 1, c);
                    sink(r, c + 1);
                    sink(r, c - 1);
                };
                for (int r = 0; r < rows; r++) {
                    for (int c = 0; c < cols; c++) {
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
            "Multi-source BFS - every rotten orange starts in the queue at "
            "minute 0.",
            "O(rows * cols) time, O(rows * cols) space",
            """
            int orangesRotting(vector<vector<int>>& grid) {
                int rows = (int)grid.size();
                int cols = (int)grid[0].size();
                queue<pair<int, int>> pending;
                int fresh = 0;
                for (int r = 0; r < rows; r++) {
                    for (int c = 0; c < cols; c++) {
                        if (grid[r][c] == 2) {
                            pending.push({r, c});
                        } else if (grid[r][c] == 1) {
                            fresh++;
                        }
                    }
                }
                int minutes = 0;
                int dr[] = {1, -1, 0, 0};
                int dc[] = {0, 0, 1, -1};
                while (!pending.empty() && fresh > 0) {
                    minutes++;
                    int size = (int)pending.size();
                    for (int i = 0; i < size; i++) {
                        auto [r, c] = pending.front();
                        pending.pop();
                        for (int d = 0; d < 4; d++) {
                            int nr = r + dr[d];
                            int nc = c + dc[d];
                            if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) {
                                continue;
                            }
                            if (grid[nr][nc] == 1) {
                                grid[nr][nc] = 2;
                                fresh--;
                                pending.push({nr, nc});
                            }
                        }
                    }
                }
                return fresh > 0 ? -1 : minutes;
            }
            """,
        ),
        _p(
            133, "Clone Graph", "Medium",
            "A map from original node to its copy doubles as the visited set - "
            "and must be filled BEFORE recursing, or a cycle never ends.",
            "O(n + e) time, O(n) space",
            """
            Node* cloneGraph(Node* node) {
                unordered_map<Node*, Node*> clones;
                function<Node*(Node*)> copy = [&](Node* cur) -> Node* {
                    if (!cur) {
                        return nullptr;
                    }
                    auto it = clones.find(cur);
                    if (it != clones.end()) {
                        return it->second;
                    }
                    Node* clone = new Node(cur->val);
                    clones[cur] = clone;
                    for (Node* neighbor : cur->neighbors) {
                        clone->neighbors.push_back(copy(neighbor));
                    }
                    return clone;
                };
                return copy(node);
            }
            """,
        ),
        _p(
            695, "Max Area of Island", "Medium",
            "Same flood fill, but the walk returns a size instead of just "
            "marking cells.",
            "O(m * n) time, O(m * n) space",
            """
            int maxAreaOfIsland(vector<vector<int>>& grid) {
                if (grid.empty()) {
                    return 0;
                }
                int rows = (int)grid.size();
                int cols = (int)grid[0].size();
                function<int(int, int)> fill = [&](int r, int c) {
                    if (r < 0 || c < 0 || r >= rows || c >= cols) {
                        return 0;
                    }
                    if (grid[r][c] != 1) {
                        return 0;
                    }
                    grid[r][c] = 0;
                    return 1 + fill(r + 1, c) + fill(r - 1, c) +
                           fill(r, c + 1) + fill(r, c - 1);
                };
                int best = 0;
                for (int r = 0; r < rows; r++) {
                    for (int c = 0; c < cols; c++) {
                        best = max(best, fill(r, c));
                    }
                }
                return best;
            }
            """,
        ),
        _p(
            547, "Number of Provinces", "Medium",
            "Every walk that starts somewhere unvisited is one more connected "
            "group.",
            "O(n * n) time, O(n) space",
            """
            int findCircleNum(vector<vector<int>>& isConnected) {
                int n = (int)isConnected.size();
                vector<bool> seen(n, false);
                function<void(int)> visit = [&](int city) {
                    seen[city] = true;
                    for (int other = 0; other < n; other++) {
                        if (isConnected[city][other] && !seen[other]) {
                            visit(other);
                        }
                    }
                };
                int groups = 0;
                for (int city = 0; city < n; city++) {
                    if (!seen[city]) {
                        visit(city);
                        groups++;
                    }
                }
                return groups;
            }
            """,
        ),
        _p(
            542, "01 Matrix", "Medium",
            "Start the queue from every zero at once, and the first visit is the "
            "nearest one. -1 marks unreached, so no second grid is needed.",
            "O(m * n) time, O(m * n) space",
            """
            vector<vector<int>> updateMatrix(vector<vector<int>>& mat) {
                int rows = (int)mat.size();
                int cols = (int)mat[0].size();
                vector<vector<int>> out(rows, vector<int>(cols, -1));
                queue<pair<int, int>> pending;
                for (int r = 0; r < rows; r++) {
                    for (int c = 0; c < cols; c++) {
                        if (mat[r][c] == 0) {
                            out[r][c] = 0;
                            pending.push({r, c});
                        }
                    }
                }
                int dr[] = {1, -1, 0, 0};
                int dc[] = {0, 0, 1, -1};
                while (!pending.empty()) {
                    auto [r, c] = pending.front();
                    pending.pop();
                    for (int d = 0; d < 4; d++) {
                        int nr = r + dr[d];
                        int nc = c + dc[d];
                        if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) {
                            continue;
                        }
                        if (out[nr][nc] == -1) {
                            out[nr][nc] = out[r][c] + 1;
                            pending.push({nr, nc});
                        }
                    }
                }
                return out;
            }
            """,
        ),
        _p(
            417, "Pacific Atlantic Water Flow", "Medium",
            "Walk uphill from each ocean instead of downhill from each cell; the "
            "answer is the overlap.",
            "O(m * n) time, O(m * n) space",
            """
            vector<vector<int>> pacificAtlantic(vector<vector<int>>& heights) {
                if (heights.empty()) {
                    return {};
                }
                int rows = (int)heights.size();
                int cols = (int)heights[0].size();
                vector<vector<bool>> pacific(rows, vector<bool>(cols, false));
                vector<vector<bool>> atlantic(rows, vector<bool>(cols, false));
                int dr[] = {1, -1, 0, 0};
                int dc[] = {0, 0, 1, -1};
                function<void(int, int, vector<vector<bool>>&)> climb =
                    [&](int r, int c, vector<vector<bool>>& seen) {
                        seen[r][c] = true;
                        for (int d = 0; d < 4; d++) {
                            int nr = r + dr[d];
                            int nc = c + dc[d];
                            if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) {
                                continue;
                            }
                            if (!seen[nr][nc] && heights[nr][nc] >= heights[r][c]) {
                                climb(nr, nc, seen);
                            }
                        }
                    };
                for (int c = 0; c < cols; c++) {
                    climb(0, c, pacific);
                    climb(rows - 1, c, atlantic);
                }
                for (int r = 0; r < rows; r++) {
                    climb(r, 0, pacific);
                    climb(r, cols - 1, atlantic);
                }
                vector<vector<int>> both;
                for (int r = 0; r < rows; r++) {
                    for (int c = 0; c < cols; c++) {
                        if (pacific[r][c] && atlantic[r][c]) {
                            both.push_back({r, c});
                        }
                    }
                }
                return both;
            }
            """,
        ),
    ),
)


# ── 10. Subsets and backtracking ────────────────────────────

_SUBSETS = Pattern(
    id="lc-backtracking",
    name="Subsets & Backtracking",
    order=10,
    blurb="Choose, recurse, un-choose - explore every combination without repeating work.",
    tell="'All subsets / permutations / combinations that ...'",
    preamble=(VECTOR, STRING, MAPS, ALGORITHM, FUNCTIONAL, USING),
    problems=(
        _p(
            78, "Subsets", "Medium",
            "Every prefix of the walk is already a valid subset - record on entry.",
            "O(n * 2^n) time, O(n) recursion depth",
            """
            vector<vector<int>> subsets(vector<int>& nums) {
                vector<vector<int>> result;
                vector<int> current;
                function<void(int)> backtrack = [&](int start) {
                    result.push_back(current);
                    for (int i = start; i < (int)nums.size(); i++) {
                        current.push_back(nums[i]);
                        backtrack(i + 1);
                        current.pop_back();
                    }
                };
                backtrack(0);
                return result;
            }
            """,
        ),
        _p(
            90, "Subsets II", "Medium",
            "Sort first, then skip a duplicate unless it's the first pick at "
            "this level - the guard is i > start, not i > 0.",
            "O(n * 2^n) time, O(n) recursion depth",
            """
            vector<vector<int>> subsetsWithDup(vector<int>& nums) {
                sort(nums.begin(), nums.end());
                vector<vector<int>> result;
                vector<int> current;
                function<void(int)> backtrack = [&](int start) {
                    result.push_back(current);
                    for (int i = start; i < (int)nums.size(); i++) {
                        if (i > start && nums[i] == nums[i - 1]) {
                            continue;
                        }
                        current.push_back(nums[i]);
                        backtrack(i + 1);
                        current.pop_back();
                    }
                };
                backtrack(0);
                return result;
            }
            """,
        ),
        _p(
            46, "Permutations", "Medium",
            "Order matters, so track which indexes are already used - and clear "
            "the flag on the way back out.",
            "O(n * n!) time, O(n) recursion depth",
            """
            vector<vector<int>> permute(vector<int>& nums) {
                vector<vector<int>> result;
                vector<int> current;
                vector<bool> used(nums.size(), false);
                function<void()> backtrack = [&]() {
                    if (current.size() == nums.size()) {
                        result.push_back(current);
                        return;
                    }
                    for (int i = 0; i < (int)nums.size(); i++) {
                        if (used[i]) {
                            continue;
                        }
                        used[i] = true;
                        current.push_back(nums[i]);
                        backtrack();
                        current.pop_back();
                        used[i] = false;
                    }
                };
                backtrack();
                return result;
            }
            """,
        ),
        _p(
            39, "Combination Sum", "Medium",
            "Reuse allowed, so recurse with i (not i + 1) and shrink the "
            "remainder.",
            "O(n^(target/min)) time, O(target) depth",
            """
            vector<vector<int>> combinationSum(vector<int>& candidates,
                                               int target) {
                vector<vector<int>> result;
                vector<int> current;
                function<void(int, int)> backtrack = [&](int start,
                                                         int remaining) {
                    if (remaining == 0) {
                        result.push_back(current);
                        return;
                    }
                    if (remaining < 0) {
                        return;
                    }
                    for (int i = start; i < (int)candidates.size(); i++) {
                        current.push_back(candidates[i]);
                        backtrack(i, remaining - candidates[i]);
                        current.pop_back();
                    }
                };
                backtrack(0, target);
                return result;
            }
            """,
        ),
        _p(
            79, "Word Search", "Medium",
            "Backtracking on a grid - blank out the cell, recurse, then restore it.",
            "O(rows * cols * 4^len(word)) time, O(len(word)) depth",
            """
            bool exist(vector<vector<char>>& board, string word) {
                int rows = (int)board.size();
                int cols = (int)board[0].size();
                function<bool(int, int, int)> search = [&](int r, int c, int i) {
                    if (i == (int)word.size()) {
                        return true;
                    }
                    if (r < 0 || r >= rows || c < 0 || c >= cols) {
                        return false;
                    }
                    if (board[r][c] != word[i]) {
                        return false;
                    }
                    char saved = board[r][c];
                    board[r][c] = '#';
                    bool found = search(r + 1, c, i + 1) ||
                                 search(r - 1, c, i + 1) ||
                                 search(r, c + 1, i + 1) ||
                                 search(r, c - 1, i + 1);
                    board[r][c] = saved;
                    return found;
                };
                for (int r = 0; r < rows; r++) {
                    for (int c = 0; c < cols; c++) {
                        if (search(r, c, 0)) {
                            return true;
                        }
                    }
                }
                return false;
            }
            """,
        ),
        _p(
            77, "Combinations", "Medium",
            "Only ever pick numbers after the last one taken, so no pair is "
            "built twice.",
            "O(k * C(n, k)) time, O(k) space",
            """
            vector<vector<int>> combine(int n, int k) {
                vector<vector<int>> out;
                vector<int> picked;
                function<void(int)> walk = [&](int start) {
                    if ((int)picked.size() == k) {
                        out.push_back(picked);
                        return;
                    }
                    for (int value = start; value <= n; value++) {
                        picked.push_back(value);
                        walk(value + 1);
                        picked.pop_back();
                    }
                };
                walk(1);
                return out;
            }
            """,
        ),
        _p(
            17, "Letter Combinations of a Phone Number", "Medium",
            "One digit is one level of the tree, and its letters are that "
            "level's branches.",
            "O(4 ** n) time, O(n) space",
            """
            vector<string> letterCombinations(string digits) {
                if (digits.empty()) {
                    return {};
                }
                unordered_map<char, string> keys = {
                    {'2', "abc"}, {'3', "def"}, {'4', "ghi"}, {'5', "jkl"},
                    {'6', "mno"}, {'7', "pqrs"}, {'8', "tuv"}, {'9', "wxyz"}
                };
                vector<string> out;
                function<void(int, string)> walk = [&](int index, string built) {
                    if (index == (int)digits.size()) {
                        out.push_back(built);
                        return;
                    }
                    for (char letter : keys[digits[index]]) {
                        walk(index + 1, built + letter);
                    }
                };
                walk(0, "");
                return out;
            }
            """,
        ),
        _p(
            131, "Palindrome Partitioning", "Medium",
            "Cut after every position whose prefix reads the same both ways, "
            "then solve the rest.",
            "O(n * 2 ** n) time, O(n) space",
            """
            vector<vector<string>> partition(string text) {
                vector<vector<string>> out;
                vector<string> built;
                function<void(int)> walk = [&](int start) {
                    if (start == (int)text.size()) {
                        out.push_back(built);
                        return;
                    }
                    for (int end = start + 1; end <= (int)text.size(); end++) {
                        string piece = text.substr(start, end - start);
                        string reversed = piece;
                        reverse(reversed.begin(), reversed.end());
                        if (piece == reversed) {
                            built.push_back(piece);
                            walk(end);
                            built.pop_back();
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
    blurb="A size-k heap keeps the best k items without sorting everything.",
    tell="'K largest / K closest / K most frequent'.",
    preamble=(VECTOR, STRING, QUEUE, MAPS, ALGORITHM, TUPLE, USING),
    problems=(
        _p(
            215, "Kth Largest Element in an Array", "Medium",
            "Hold a min-heap of size k; its root is the kth largest. "
            "priority_queue is a MAX-heap, so greater<> is what inverts it.",
            "O(n log k) time, O(k) space",
            """
            int findKthLargest(vector<int>& nums, int k) {
                priority_queue<int, vector<int>, greater<int>> heap;
                for (int n : nums) {
                    heap.push(n);
                    if ((int)heap.size() > k) {
                        heap.pop();
                    }
                }
                return heap.top();
            }
            """,
        ),
        _p(
            347, "Top K Frequent Elements", "Medium",
            "Count first, then a min-heap on (count, value) keeps only k.",
            "O(n log k) time, O(n) space",
            """
            vector<int> topKFrequent(vector<int>& nums, int k) {
                unordered_map<int, int> counts;
                for (int n : nums) {
                    counts[n]++;
                }
                priority_queue<pair<int, int>, vector<pair<int, int>>,
                               greater<pair<int, int>>> heap;
                for (auto& [value, count] : counts) {
                    heap.push({count, value});
                    if ((int)heap.size() > k) {
                        heap.pop();
                    }
                }
                vector<int> out;
                while (!heap.empty()) {
                    out.push_back(heap.top().second);
                    heap.pop();
                }
                return out;
            }
            """,
        ),
        _p(
            973, "K Closest Points to Origin", "Medium",
            "A plain max-heap already pops the FURTHEST point first, so no "
            "negation - that is Python's workaround, not C++'s.",
            "O(n log k) time, O(k) space",
            """
            vector<vector<int>> kClosest(vector<vector<int>>& points, int k) {
                priority_queue<pair<int, pair<int, int>>> heap;
                for (auto& point : points) {
                    int x = point[0];
                    int y = point[1];
                    heap.push({x * x + y * y, {x, y}});
                    if ((int)heap.size() > k) {
                        heap.pop();
                    }
                }
                vector<vector<int>> out;
                while (!heap.empty()) {
                    auto [x, y] = heap.top().second;
                    heap.pop();
                    out.push_back({x, y});
                }
                return out;
            }
            """,
        ),
        _p(
            1046, "Last Stone Weight", "Easy",
            "C++'s heap is a max-heap, so the two heaviest stones just pop off "
            "the top - no negation needed.",
            "O(n log n) time, O(n) space",
            """
            int lastStoneWeight(vector<int>& stones) {
                priority_queue<int> heap(stones.begin(), stones.end());
                while (heap.size() > 1) {
                    int first = heap.top();
                    heap.pop();
                    int second = heap.top();
                    heap.pop();
                    if (first != second) {
                        heap.push(first - second);
                    }
                }
                return heap.empty() ? 0 : heap.top();
            }
            """,
        ),
        _p(
            692, "Top K Frequent Words", "Medium",
            "Most frequent first, then alphabetical. Two orderings in opposite "
            "directions, so a comparator is clearer than any key trick.",
            "O(n + k log n) time, O(n) space",
            """
            vector<string> topKFrequentWords(vector<string>& words, int k) {
                unordered_map<string, int> counts;
                for (const string& word : words) {
                    counts[word]++;
                }
                vector<pair<string, int>> entries(counts.begin(), counts.end());
                sort(entries.begin(), entries.end(),
                     [](const pair<string, int>& a, const pair<string, int>& b) {
                         if (a.second != b.second) {
                             return a.second > b.second;
                         }
                         return a.first < b.first;
                     });
                vector<string> out;
                for (int i = 0; i < k && i < (int)entries.size(); i++) {
                    out.push_back(entries[i].first);
                }
                return out;
            }
            """,
        ),
        _p(
            451, "Sort Characters By Frequency", "Medium",
            "Count, then pop the max-heap most-frequent-first and repeat each "
            "character.",
            "O(n log n) time, O(n) space",
            """
            string frequencySort(string s) {
                unordered_map<char, int> counts;
                for (char ch : s) {
                    counts[ch]++;
                }
                priority_queue<pair<int, char>> heap;
                for (auto& [ch, count] : counts) {
                    heap.push({count, ch});
                }
                string out;
                while (!heap.empty()) {
                    auto [count, ch] = heap.top();
                    heap.pop();
                    out.append(count, ch);
                }
                return out;
            }
            """,
        ),
        _p(
            378, "Kth Smallest Element in a Sorted Matrix", "Medium",
            "Seed the heap with each row's head, then keep pulling the smallest "
            "and refilling from its row.",
            "O(k log n) time, O(n) space",
            """
            int kthSmallest(vector<vector<int>>& matrix, int k) {
                typedef tuple<int, int, int> Entry;
                priority_queue<Entry, vector<Entry>, greater<Entry>> heap;
                int rows = min((int)matrix.size(), k);
                for (int row = 0; row < rows; row++) {
                    heap.push({matrix[row][0], row, 0});
                }
                int value = 0;
                for (int i = 0; i < k; i++) {
                    auto [v, row, col] = heap.top();
                    heap.pop();
                    value = v;
                    if (col + 1 < (int)matrix[row].size()) {
                        heap.push({matrix[row][col + 1], row, col + 1});
                    }
                }
                return value;
            }
            """,
        ),
        _p(
            767, "Reorganize String", "Medium",
            "Always place the most common letter left, holding the one you just "
            "used aside for a turn.",
            "O(n log n) time, O(n) space",
            """
            string reorganizeString(string s) {
                unordered_map<char, int> counts;
                for (char ch : s) {
                    counts[ch]++;
                }
                priority_queue<pair<int, char>> heap;
                for (auto& [ch, count] : counts) {
                    heap.push({count, ch});
                }
                string out;
                pair<int, char> held = {0, ' '};
                while (!heap.empty()) {
                    auto [count, ch] = heap.top();
                    heap.pop();
                    out += ch;
                    if (held.first > 0) {
                        heap.push(held);
                    }
                    held = {count - 1, ch};
                    if (held.first == 0) {
                        held = {0, ' '};
                    }
                }
                return out.size() == s.size() ? out : "";
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
    blurb="Repeatedly take whatever has no unmet prerequisites (indegree 0).",
    tell="Dependencies, ordering, 'can this schedule be completed?'",
    preamble=(VECTOR, STRING, QUEUE, MAPS, ORDERED, ALGORITHM, USING),
    problems=(
        _p(
            207, "Course Schedule", "Medium",
            "If a cycle exists you can never drain the queue - count what you "
            "took.",
            "O(v + e) time, O(v + e) space",
            """
            bool canFinish(int numCourses, vector<vector<int>>& prerequisites) {
                vector<vector<int>> graph(numCourses);
                vector<int> indegree(numCourses, 0);
                for (auto& pair : prerequisites) {
                    graph[pair[1]].push_back(pair[0]);
                    indegree[pair[0]]++;
                }
                queue<int> pending;
                for (int i = 0; i < numCourses; i++) {
                    if (indegree[i] == 0) {
                        pending.push(i);
                    }
                }
                int taken = 0;
                while (!pending.empty()) {
                    int node = pending.front();
                    pending.pop();
                    taken++;
                    for (int next : graph[node]) {
                        if (--indegree[next] == 0) {
                            pending.push(next);
                        }
                    }
                }
                return taken == numCourses;
            }
            """,
        ),
        _p(
            210, "Course Schedule II", "Medium",
            "Same peel, but keep the order you took things in.",
            "O(v + e) time, O(v + e) space",
            """
            vector<int> findOrder(int numCourses,
                                  vector<vector<int>>& prerequisites) {
                vector<vector<int>> graph(numCourses);
                vector<int> indegree(numCourses, 0);
                for (auto& pair : prerequisites) {
                    graph[pair[1]].push_back(pair[0]);
                    indegree[pair[0]]++;
                }
                queue<int> pending;
                for (int i = 0; i < numCourses; i++) {
                    if (indegree[i] == 0) {
                        pending.push(i);
                    }
                }
                vector<int> order;
                while (!pending.empty()) {
                    int node = pending.front();
                    pending.pop();
                    order.push_back(node);
                    for (int next : graph[node]) {
                        if (--indegree[next] == 0) {
                            pending.push(next);
                        }
                    }
                }
                return (int)order.size() == numCourses ? order : vector<int>();
            }
            """,
        ),
        _p(
            310, "Minimum Height Trees", "Medium",
            "Peel leaves layer by layer; the last 1 or 2 left are the centres.",
            "O(v + e) time, O(v + e) space",
            """
            vector<int> findMinHeightTrees(int n, vector<vector<int>>& edges) {
                if (n == 1) {
                    return {0};
                }
                vector<set<int>> graph(n);
                for (auto& edge : edges) {
                    graph[edge[0]].insert(edge[1]);
                    graph[edge[1]].insert(edge[0]);
                }
                vector<int> leaves;
                for (int i = 0; i < n; i++) {
                    if (graph[i].size() == 1) {
                        leaves.push_back(i);
                    }
                }
                int remaining = n;
                while (remaining > 2) {
                    remaining -= (int)leaves.size();
                    vector<int> nextLeaves;
                    for (int leaf : leaves) {
                        int neighbor = *graph[leaf].begin();
                        graph[leaf].erase(neighbor);
                        graph[neighbor].erase(leaf);
                        if (graph[neighbor].size() == 1) {
                            nextLeaves.push_back(neighbor);
                        }
                    }
                    leaves = nextLeaves;
                }
                return leaves;
            }
            """,
        ),
        _p(
            802, "Find Eventual Safe States", "Medium",
            "Reverse every edge, then peel from the terminal nodes - whatever "
            "drains is safe.",
            "O(v + e) time, O(v + e) space",
            """
            vector<int> eventualSafeNodes(vector<vector<int>>& graph) {
                int n = (int)graph.size();
                vector<vector<int>> reverse(n);
                vector<int> outdegree(n, 0);
                for (int node = 0; node < n; node++) {
                    outdegree[node] = (int)graph[node].size();
                    for (int next : graph[node]) {
                        reverse[next].push_back(node);
                    }
                }
                queue<int> pending;
                for (int i = 0; i < n; i++) {
                    if (outdegree[i] == 0) {
                        pending.push(i);
                    }
                }
                vector<int> safe;
                while (!pending.empty()) {
                    int node = pending.front();
                    pending.pop();
                    safe.push_back(node);
                    for (int prev : reverse[node]) {
                        if (--outdegree[prev] == 0) {
                            pending.push(prev);
                        }
                    }
                }
                sort(safe.begin(), safe.end());
                return safe;
            }
            """,
        ),
        _p(
            1462, "Course Schedule IV", "Medium",
            "Peel in order, and let each course inherit the prerequisite set of "
            "everything before it.",
            "O(v * e) time, O(v * v) space",
            """
            vector<bool> checkIfPrerequisite(int numCourses,
                                             vector<vector<int>>& prerequisites,
                                             vector<vector<int>>& queries) {
                vector<vector<int>> graph(numCourses);
                vector<int> indegree(numCourses, 0);
                for (auto& pair : prerequisites) {
                    graph[pair[0]].push_back(pair[1]);
                    indegree[pair[1]]++;
                }
                vector<set<int>> needs(numCourses);
                queue<int> pending;
                for (int i = 0; i < numCourses; i++) {
                    if (indegree[i] == 0) {
                        pending.push(i);
                    }
                }
                while (!pending.empty()) {
                    int node = pending.front();
                    pending.pop();
                    for (int next : graph[node]) {
                        needs[next].insert(node);
                        needs[next].insert(needs[node].begin(),
                                           needs[node].end());
                        if (--indegree[next] == 0) {
                            pending.push(next);
                        }
                    }
                }
                vector<bool> answers;
                for (auto& query : queries) {
                    answers.push_back(needs[query[1]].count(query[0]) > 0);
                }
                return answers;
            }
            """,
        ),
        _p(
            2115, "Find All Possible Recipes from Given Supplies", "Medium",
            "Ingredients are prerequisites: a recipe unlocks once its count of "
            "missing items hits zero, and then becomes an ingredient itself.",
            "O(v + e) time, O(v + e) space",
            """
            vector<string> findAllRecipes(vector<string>& recipes,
                                          vector<vector<string>>& ingredients,
                                          vector<string>& supplies) {
                unordered_map<string, vector<string>> graph;
                unordered_map<string, int> indegree;
                for (const string& recipe : recipes) {
                    indegree[recipe] = 0;
                }
                for (size_t i = 0; i < recipes.size(); i++) {
                    for (const string& item : ingredients[i]) {
                        graph[item].push_back(recipes[i]);
                        indegree[recipes[i]]++;
                    }
                }
                queue<string> pending;
                for (const string& item : supplies) {
                    pending.push(item);
                }
                vector<string> made;
                while (!pending.empty()) {
                    string item = pending.front();
                    pending.pop();
                    for (const string& recipe : graph[item]) {
                        if (--indegree[recipe] == 0) {
                            made.push_back(recipe);
                            pending.push(recipe);
                        }
                    }
                }
                return made;
            }
            """,
        ),
        _p(
            1136, "Parallel Courses", "Medium",
            "Every drained layer of the queue is one semester - count the "
            "layers, not the courses.",
            "O(v + e) time, O(v + e) space",
            """
            int minimumSemesters(int n, vector<vector<int>>& relations) {
                vector<vector<int>> graph(n + 1);
                vector<int> indegree(n + 1, 0);
                for (auto& pair : relations) {
                    graph[pair[0]].push_back(pair[1]);
                    indegree[pair[1]]++;
                }
                queue<int> pending;
                for (int i = 1; i <= n; i++) {
                    if (indegree[i] == 0) {
                        pending.push(i);
                    }
                }
                int studied = 0;
                int semesters = 0;
                while (!pending.empty()) {
                    semesters++;
                    int size = (int)pending.size();
                    for (int i = 0; i < size; i++) {
                        int node = pending.front();
                        pending.pop();
                        studied++;
                        for (int next : graph[node]) {
                            if (--indegree[next] == 0) {
                                pending.push(next);
                            }
                        }
                    }
                }
                return studied == n ? semesters : -1;
            }
            """,
        ),
        _p(
            269, "Alien Dictionary", "Hard",
            "Adjacent words give one letter order each; the first difference is "
            "the only edge they prove.",
            "O(c) time, O(1) space",
            """
            string alienOrder(vector<string>& words) {
                unordered_map<char, set<char>> graph;
                unordered_map<char, int> indegree;
                for (const string& word : words) {
                    for (char ch : word) {
                        graph[ch];
                        indegree[ch] += 0;
                    }
                }
                for (size_t i = 0; i + 1 < words.size(); i++) {
                    const string& first = words[i];
                    const string& second = words[i + 1];
                    bool split = false;
                    size_t shorter = min(first.size(), second.size());
                    for (size_t j = 0; j < shorter; j++) {
                        if (first[j] != second[j]) {
                            if (graph[first[j]].insert(second[j]).second) {
                                indegree[second[j]]++;
                            }
                            split = true;
                            break;
                        }
                    }
                    if (!split && first.size() > second.size()) {
                        return "";
                    }
                }
                queue<char> pending;
                for (auto& [ch, degree] : indegree) {
                    if (degree == 0) {
                        pending.push(ch);
                    }
                }
                string order;
                while (!pending.empty()) {
                    char ch = pending.front();
                    pending.pop();
                    order += ch;
                    for (char next : graph[ch]) {
                        if (--indegree[next] == 0) {
                            pending.push(next);
                        }
                    }
                }
                return order.size() == indegree.size() ? order : "";
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
    blurb="Solve small cases once, store them, and build the big answer from them.",
    tell="Overlapping subproblems - the naive recursion recomputes the same thing.",
    preamble=(VECTOR, STRING, ALGORITHM, USING),
    problems=(
        _p(
            70, "Climbing Stairs", "Easy",
            "Ways to reach step n = ways to n-1 plus ways to n-2. It's Fibonacci.",
            "O(n) time, O(1) space",
            """
            int climbStairs(int n) {
                int prev = 1;
                int cur = 1;
                for (int i = 0; i < n - 1; i++) {
                    int next = prev + cur;
                    prev = cur;
                    cur = next;
                }
                return cur;
            }
            """,
        ),
        _p(
            198, "House Robber", "Medium",
            "At each house: best so far if you skip it, or (best before last) "
            "plus it. Bank the old skip before overwriting it.",
            "O(n) time, O(1) space",
            """
            int rob(vector<int>& nums) {
                int skip = 0;
                int take = 0;
                for (int n : nums) {
                    int nextSkip = max(skip, take);
                    take = skip + n;
                    skip = nextSkip;
                }
                return max(skip, take);
            }
            """,
        ),
        _p(
            322, "Coin Change", "Medium",
            "Build up every amount from 1 to target, trying each coin as the "
            "last one.",
            "O(amount * coins) time, O(amount) space",
            """
            int coinChange(vector<int>& coins, int amount) {
                vector<int> best(amount + 1, amount + 1);
                best[0] = 0;
                for (int value = 1; value <= amount; value++) {
                    for (int coin : coins) {
                        if (coin <= value) {
                            best[value] = min(best[value], best[value - coin] + 1);
                        }
                    }
                }
                return best[amount] <= amount ? best[amount] : -1;
            }
            """,
        ),
        _p(
            300, "Longest Increasing Subsequence", "Medium",
            "Keep the smallest possible tail for each length; binary search its "
            "slot.",
            "O(n log n) time, O(n) space",
            """
            int lengthOfLIS(vector<int>& nums) {
                vector<int> tails;
                for (int n : nums) {
                    auto slot = lower_bound(tails.begin(), tails.end(), n);
                    if (slot == tails.end()) {
                        tails.push_back(n);
                    } else {
                        *slot = n;
                    }
                }
                return (int)tails.size();
            }
            """,
        ),
        _p(
            746, "Min Cost Climbing Stairs", "Easy",
            "The cost of a step is its own plus the cheaper of the two ways off it.",
            "O(n) time, O(1) space",
            """
            int minCostClimbingStairs(vector<int>& cost) {
                int one = 0;
                int two = 0;
                for (int i = 2; i <= (int)cost.size(); i++) {
                    int next = min(one + cost[i - 1], two + cost[i - 2]);
                    two = one;
                    one = next;
                }
                return one;
            }
            """,
        ),
        _p(
            1143, "Longest Common Subsequence", "Medium",
            "Matching letters extend the diagonal; otherwise take the better of "
            "dropping one.",
            "O(m * n) time, O(m * n) space",
            """
            int longestCommonSubsequence(string first, string second) {
                vector<vector<int>> grid(first.size() + 1,
                                         vector<int>(second.size() + 1, 0));
                for (int i = (int)first.size() - 1; i >= 0; i--) {
                    for (int j = (int)second.size() - 1; j >= 0; j--) {
                        if (first[i] == second[j]) {
                            grid[i][j] = 1 + grid[i + 1][j + 1];
                        } else {
                            grid[i][j] = max(grid[i + 1][j], grid[i][j + 1]);
                        }
                    }
                }
                return grid[0][0];
            }
            """,
        ),
        _p(
            139, "Word Break", "Medium",
            "A position is reachable when some word ends there and its start was "
            "reachable too.",
            "O(n * n * w) time, O(n) space",
            """
            bool wordBreak(string text, vector<string>& words) {
                vector<bool> reachable(text.size() + 1, false);
                reachable[0] = true;
                for (int end = 1; end <= (int)text.size(); end++) {
                    for (const string& word : words) {
                        int start = end - (int)word.size();
                        if (start >= 0 && reachable[start]) {
                            if (text.compare(start, word.size(), word) == 0) {
                                reachable[end] = true;
                                break;
                            }
                        }
                    }
                }
                return reachable[text.size()];
            }
            """,
        ),
        _p(
            152, "Maximum Product Subarray", "Medium",
            "Track the smallest product too - a negative turns the worst into "
            "the best.",
            "O(n) time, O(1) space",
            """
            int maxProduct(vector<int>& nums) {
                int best = nums[0];
                int high = nums[0];
                int low = nums[0];
                for (size_t i = 1; i < nums.size(); i++) {
                    int n = nums[i];
                    int candidates[] = {n, high * n, low * n};
                    high = max({candidates[0], candidates[1], candidates[2]});
                    low = min({candidates[0], candidates[1], candidates[2]});
                    if (high > best) {
                        best = high;
                    }
                }
                return best;
            }
            """,
        ),
    ),
)
