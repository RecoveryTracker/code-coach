"""
Rust patterns 5 to 13, split out of `problems_rust` to keep each file a
readable length. `problems_rust.PATTERNS` stitches them together.

Two things here are genuinely Rust rather than a translation of the Python:

Linked lists use `Option<Box<ListNode>>`, LeetCode's own type. Box is unique
ownership, so a Box list can be rebuilt cheaply but cannot physically contain
a cycle — which is why LeetCode does not offer #141 in Rust at all. That one
is posed over a next-index array instead, so the tortoise-and-hare is exactly
the same and the lesson survives.

Heaps invert. `BinaryHeap` is a MAX-heap where Python's `heapq` is a min-heap,
so where Python negates to get the largest out first, Rust wraps in `Reverse`
to get the smallest. The `idea` lines say so rather than repeating Python's.
"""

from __future__ import annotations

from code_coach.leetcode.problems import Pattern
from code_coach.leetcode.rust_common import (
    BINARY_HEAP,
    COLLECTIONS,
    GRAPH_NODE,
    HASH_MAP,
    LIST_NODE,
    RC_REFCELL,
    TREE_NODE,
    VEC_DEQUE,
    _p,
)

# ── 5. Linked lists ─────────────────────────────────────────

_LINKED_LIST = Pattern(
    id="lc-linked-list",
    name="Linked Lists",
    order=5,
    blurb="Nodes joined by .next - you can only walk forward, so save what you need.",
    tell="Reversing, merging, or finding a position relative to the end.",
    preamble=(LIST_NODE,),
    problems=(
        _p(
            206, "Reverse Linked List", "Easy",
            "Take the next out of the node, point it back at prev, then step on.",
            "O(n) time, O(1) space",
            """
            pub fn reverse_list(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
                let mut prev = None;
                let mut head = head;
                while let Some(mut node) = head {
                    head = node.next.take();
                    node.next = prev;
                    prev = Some(node);
                }
                prev
            }
            """,
        ),
        _p(
            21, "Merge Two Sorted Lists", "Easy",
            "A dummy head means you never special-case the first node.",
            "O(n + m) time, O(1) space",
            """
            pub fn merge_two_lists(
                list1: Option<Box<ListNode>>,
                list2: Option<Box<ListNode>>,
            ) -> Option<Box<ListNode>> {
                let mut dummy = Box::new(ListNode::new(0));
                let mut tail = &mut dummy;
                let mut a = list1;
                let mut b = list2;
                while a.is_some() && b.is_some() {
                    let take_a = a.as_ref().unwrap().val <= b.as_ref().unwrap().val;
                    let mut node = if take_a {
                        a.take().unwrap()
                    } else {
                        b.take().unwrap()
                    };
                    if take_a {
                        a = node.next.take();
                    } else {
                        b = node.next.take();
                    }
                    tail.next = Some(node);
                    tail = tail.next.as_mut().unwrap();
                }
                tail.next = if a.is_some() { a } else { b };
                dummy.next
            }
            """,
        ),
        _p(
            141, "Linked List Cycle", "Easy",
            "Fast moves two, slow moves one - in a loop they must collide. Posed "
            "over next-indexes, because a Box list cannot hold a cycle.",
            "O(n) time, O(1) space",
            """
            pub fn has_cycle(next: Vec<i32>, start: i32) -> bool {
                let step = |at: i32| -> i32 {
                    if at < 0 {
                        -1
                    } else {
                        next[at as usize]
                    }
                };
                let mut slow = start;
                let mut fast = start;
                while fast >= 0 && step(fast) >= 0 {
                    slow = step(slow);
                    fast = step(step(fast));
                    if slow == fast {
                        return true;
                    }
                }
                false
            }
            """,
        ),
        _p(
            19, "Remove Nth Node From End", "Medium",
            "Counting from the end is counting from the front once you know the "
            "length.",
            "O(n) time, O(1) space",
            """
            pub fn remove_nth_from_end(
                head: Option<Box<ListNode>>,
                n: i32,
            ) -> Option<Box<ListNode>> {
                let mut length = 0;
                let mut cursor = &head;
                while let Some(node) = cursor {
                    length += 1;
                    cursor = &node.next;
                }
                let mut dummy = Box::new(ListNode::new(0));
                dummy.next = head;
                let mut node = &mut dummy;
                for _ in 0..(length - n) {
                    node = node.next.as_mut().unwrap();
                }
                let doomed = node.next.take();
                node.next = doomed.unwrap().next;
                dummy.next
            }
            """,
        ),
        _p(
            876, "Middle of the Linked List", "Easy",
            "Measure once, then walk half way. Two cursors at different speeds "
            "need two borrows, which Box will not give you.",
            "O(n) time, O(1) space",
            """
            pub fn middle_node(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
                let mut length = 0;
                let mut cursor = &head;
                while let Some(node) = cursor {
                    length += 1;
                    cursor = &node.next;
                }
                let mut node = head;
                for _ in 0..length / 2 {
                    node = node.unwrap().next;
                }
                node
            }
            """,
        ),
        _p(
            83, "Remove Duplicates from Sorted List", "Easy",
            "Sorted means duplicates are neighbours, so one pass and a skipped "
            "link does it.",
            "O(n) time, O(1) space",
            """
            pub fn delete_duplicates(head: Option<Box<ListNode>>) -> Option<Box<ListNode>> {
                let mut head = head;
                let mut cursor = &mut head;
                while cursor.is_some() {
                    let node = cursor.as_mut().unwrap();
                    let same = match &node.next {
                        Some(next) => next.val == node.val,
                        None => false,
                    };
                    if same {
                        let after = node.next.as_mut().unwrap().next.take();
                        node.next = after;
                    } else {
                        cursor = &mut cursor.as_mut().unwrap().next;
                    }
                }
                head
            }
            """,
        ),
        _p(
            234, "Palindrome Linked List", "Easy",
            "Collect the values, then two-pointer them - the idiomatic Rust "
            "answer, and it needs no surgery on the list.",
            "O(n) time, O(n) space",
            """
            pub fn is_palindrome_list(head: Option<Box<ListNode>>) -> bool {
                let mut values = Vec::new();
                let mut cursor = &head;
                while let Some(node) = cursor {
                    values.push(node.val);
                    cursor = &node.next;
                }
                let mut left = 0;
                let mut right = values.len();
                while left + 1 < right {
                    right -= 1;
                    if values[left] != values[right] {
                        return false;
                    }
                    left += 1;
                }
                true
            }
            """,
        ),
        _p(
            2, "Add Two Numbers", "Medium",
            "Long addition, digit by digit. The carry is the only thing you have "
            "to remember.",
            "O(n) time, O(n) space",
            """
            pub fn add_two_numbers(
                first: Option<Box<ListNode>>,
                second: Option<Box<ListNode>>,
            ) -> Option<Box<ListNode>> {
                let mut head = Box::new(ListNode::new(0));
                let mut node = &mut head;
                let mut a = first;
                let mut b = second;
                let mut carry = 0;
                while a.is_some() || b.is_some() || carry > 0 {
                    let mut total = carry;
                    if let Some(n) = a {
                        total += n.val;
                        a = n.next;
                    }
                    if let Some(n) = b {
                        total += n.val;
                        b = n.next;
                    }
                    carry = total / 10;
                    node.next = Some(Box::new(ListNode::new(total % 10)));
                    node = node.next.as_mut().unwrap();
                }
                head.next
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
    problems=(
        _p(
            704, "Binary Search", "Easy",
            "Closed range [low, high]: shrink past mid every time. Signed "
            "bounds, because usize cannot go below zero.",
            "O(log n) time, O(1) space",
            """
            pub fn search(nums: Vec<i32>, target: i32) -> i32 {
                let mut low = 0i32;
                let mut high = nums.len() as i32 - 1;
                while low <= high {
                    let mid = (low + high) / 2;
                    let value = nums[mid as usize];
                    if value == target {
                        return mid;
                    }
                    if value < target {
                        low = mid + 1;
                    } else {
                        high = mid - 1;
                    }
                }
                -1
            }
            """,
        ),
        _p(
            35, "Search Insert Position", "Easy",
            "Half-open range [low, high): low lands on the insert point.",
            "O(log n) time, O(1) space",
            """
            pub fn search_insert(nums: Vec<i32>, target: i32) -> i32 {
                let mut low = 0;
                let mut high = nums.len();
                while low < high {
                    let mid = (low + high) / 2;
                    if nums[mid] < target {
                        low = mid + 1;
                    } else {
                        high = mid;
                    }
                }
                low as i32
            }
            """,
        ),
        _p(
            153, "Find Minimum in Rotated Sorted Array", "Medium",
            "Compare mid to the right end to learn which half holds the dip.",
            "O(log n) time, O(1) space",
            """
            pub fn find_min(nums: Vec<i32>) -> i32 {
                let mut low = 0;
                let mut high = nums.len() - 1;
                while low < high {
                    let mid = (low + high) / 2;
                    if nums[mid] > nums[high] {
                        low = mid + 1;
                    } else {
                        high = mid;
                    }
                }
                nums[low]
            }
            """,
        ),
        _p(
            33, "Search in Rotated Sorted Array", "Medium",
            "One half is always sorted - check if the target lies inside it.",
            "O(log n) time, O(1) space",
            """
            pub fn search_rotated(nums: Vec<i32>, target: i32) -> i32 {
                let mut low = 0i32;
                let mut high = nums.len() as i32 - 1;
                while low <= high {
                    let mid = (low + high) / 2;
                    let value = nums[mid as usize];
                    if value == target {
                        return mid;
                    }
                    if nums[low as usize] <= value {
                        if nums[low as usize] <= target && target < value {
                            high = mid - 1;
                        } else {
                            low = mid + 1;
                        }
                    } else if value < target && target <= nums[high as usize] {
                        low = mid + 1;
                    } else {
                        high = mid - 1;
                    }
                }
                -1
            }
            """,
        ),
        _p(
            875, "Koko Eating Bananas", "Medium",
            "Binary search the ANSWER: the slowest speed that still finishes in time.",
            "O(n log m) time, O(1) space",
            """
            pub fn min_eating_speed(piles: Vec<i32>, h: i32) -> i32 {
                let mut low = 1;
                let mut high = *piles.iter().max().unwrap();
                while low < high {
                    let speed = (low + high) / 2;
                    let mut hours = 0i64;
                    for pile in &piles {
                        hours += ((pile + speed - 1) / speed) as i64;
                    }
                    if hours <= h as i64 {
                        high = speed;
                    } else {
                        low = speed + 1;
                    }
                }
                low
            }
            """,
        ),
        _p(
            278, "First Bad Version", "Easy",
            "Search for a boundary: keep the mid when it's bad, discard it when "
            "it isn't. low + (high - low) / 2 cannot overflow.",
            "O(log n) time, O(1) space",
            """
            pub fn first_bad_version(n: i32, is_bad: impl Fn(i32) -> bool) -> i32 {
                let mut low = 1;
                let mut high = n;
                while low < high {
                    let mid = low + (high - low) / 2;
                    if is_bad(mid) {
                        high = mid;
                    } else {
                        low = mid + 1;
                    }
                }
                low
            }
            """,
        ),
        _p(
            34, "Find First and Last Position of Element in Sorted Array", "Medium",
            "Two searches, not one: the same closure finds the left edge and "
            "then the right.",
            "O(log n) time, O(1) space",
            """
            pub fn search_range(nums: Vec<i32>, target: i32) -> Vec<i32> {
                let edge = |first: bool| -> i32 {
                    let mut low = 0i32;
                    let mut high = nums.len() as i32 - 1;
                    let mut found = -1;
                    while low <= high {
                        let mid = (low + high) / 2;
                        let value = nums[mid as usize];
                        if value == target {
                            found = mid;
                            if first {
                                high = mid - 1;
                            } else {
                                low = mid + 1;
                            }
                        } else if value < target {
                            low = mid + 1;
                        } else {
                            high = mid - 1;
                        }
                    }
                    found
                };
                vec![edge(true), edge(false)]
            }
            """,
        ),
        _p(
            74, "Search a 2D Matrix", "Medium",
            "A sorted matrix is one sorted list folded up, so divide the index "
            "to unfold it.",
            "O(log(m * n)) time, O(1) space",
            """
            pub fn search_matrix(matrix: Vec<Vec<i32>>, target: i32) -> bool {
                if matrix.is_empty() || matrix[0].is_empty() {
                    return false;
                }
                let rows = matrix.len();
                let cols = matrix[0].len();
                let mut low = 0i32;
                let mut high = (rows * cols) as i32 - 1;
                while low <= high {
                    let mid = (low + high) / 2;
                    let value = matrix[mid as usize / cols][mid as usize % cols];
                    if value == target {
                        return true;
                    }
                    if value < target {
                        low = mid + 1;
                    } else {
                        high = mid - 1;
                    }
                }
                false
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
    preamble=(RC_REFCELL, TREE_NODE),
    problems=(
        _p(
            104, "Maximum Depth of Binary Tree", "Easy",
            "Depth here = 1 + the deeper of my two children.",
            "O(n) time, O(h) space",
            """
            pub fn max_depth(root: Tree) -> i32 {
                match root {
                    None => 0,
                    Some(node) => {
                        let left = node.borrow().left.clone();
                        let right = node.borrow().right.clone();
                        1 + max_depth(left).max(max_depth(right))
                    }
                }
            }
            """,
        ),
        _p(
            226, "Invert Binary Tree", "Easy",
            "Swap the children, then let recursion handle each side.",
            "O(n) time, O(h) space",
            """
            pub fn invert_tree(root: Tree) -> Tree {
                if let Some(node) = &root {
                    let left = node.borrow().left.clone();
                    let right = node.borrow().right.clone();
                    node.borrow_mut().left = invert_tree(right);
                    node.borrow_mut().right = invert_tree(left);
                }
                root
            }
            """,
        ),
        _p(
            112, "Path Sum", "Easy",
            "Subtract as you descend; at a leaf ask whether the remainder fits.",
            "O(n) time, O(h) space",
            """
            pub fn has_path_sum(root: Tree, target_sum: i32) -> bool {
                match root {
                    None => false,
                    Some(node) => {
                        let left = node.borrow().left.clone();
                        let right = node.borrow().right.clone();
                        let val = node.borrow().val;
                        if left.is_none() && right.is_none() {
                            return target_sum == val;
                        }
                        let rest = target_sum - val;
                        has_path_sum(left, rest) || has_path_sum(right, rest)
                    }
                }
            }
            """,
        ),
        _p(
            543, "Diameter of Binary Tree", "Easy",
            "Return depth upward, but record left + right as a candidate answer. "
            "Rust has no nonlocal, so the best travels as &mut.",
            "O(n) time, O(h) space",
            """
            pub fn diameter_of_binary_tree(root: Tree) -> i32 {
                fn depth(node: Tree, best: &mut i32) -> i32 {
                    match node {
                        None => 0,
                        Some(n) => {
                            let left = depth(n.borrow().left.clone(), best);
                            let right = depth(n.borrow().right.clone(), best);
                            *best = (*best).max(left + right);
                            1 + left.max(right)
                        }
                    }
                }
                let mut best = 0;
                depth(root, &mut best);
                best
            }
            """,
        ),
        _p(
            98, "Validate Binary Search Tree", "Medium",
            "Carry an allowed (low, high) range down instead of checking "
            "neighbours. i64 bounds, so a node holding i32::MIN still passes.",
            "O(n) time, O(h) space",
            """
            pub fn is_valid_bst(root: Tree) -> bool {
                fn check(node: Tree, low: i64, high: i64) -> bool {
                    match node {
                        None => true,
                        Some(n) => {
                            let val = n.borrow().val as i64;
                            if val <= low || val >= high {
                                return false;
                            }
                            let left = n.borrow().left.clone();
                            let right = n.borrow().right.clone();
                            check(left, low, val) && check(right, val, high)
                        }
                    }
                }
                check(root, i64::MIN, i64::MAX)
            }
            """,
        ),
        _p(
            100, "Same Tree", "Easy",
            "Two trees match when their roots match and both pairs of children "
            "do. Matching on the pair says it in one expression.",
            "O(n) time, O(h) space",
            """
            pub fn is_same_tree(first: Tree, second: Tree) -> bool {
                match (first, second) {
                    (None, None) => true,
                    (None, Some(_)) | (Some(_), None) => false,
                    (Some(a), Some(b)) => {
                        if a.borrow().val != b.borrow().val {
                            return false;
                        }
                        let (al, ar) = (a.borrow().left.clone(), a.borrow().right.clone());
                        let (bl, br) = (b.borrow().left.clone(), b.borrow().right.clone());
                        is_same_tree(al, bl) && is_same_tree(ar, br)
                    }
                }
            }
            """,
        ),
        _p(
            101, "Symmetric Tree", "Easy",
            "A mirror compares left against right - the recursion crosses over.",
            "O(n) time, O(h) space",
            """
            pub fn is_symmetric(root: Tree) -> bool {
                fn mirror(left: Tree, right: Tree) -> bool {
                    match (left, right) {
                        (None, None) => true,
                        (None, Some(_)) | (Some(_), None) => false,
                        (Some(a), Some(b)) => {
                            if a.borrow().val != b.borrow().val {
                                return false;
                            }
                            let (al, ar) = (a.borrow().left.clone(), a.borrow().right.clone());
                            let (bl, br) = (b.borrow().left.clone(), b.borrow().right.clone());
                            mirror(al, br) && mirror(ar, bl)
                        }
                    }
                }
                let copy = root.clone();
                mirror(root, copy)
            }
            """,
        ),
        _p(
            236, "Lowest Common Ancestor of a Binary Tree", "Medium",
            "A node whose two sides each found something is the meeting point.",
            "O(n) time, O(h) space",
            """
            pub fn lowest_common_ancestor(root: Tree, p: Tree, q: Tree) -> Tree {
                let node = root.as_ref()?;
                let val = node.borrow().val;
                let p_val = p.as_ref().map(|n| n.borrow().val);
                let q_val = q.as_ref().map(|n| n.borrow().val);
                if Some(val) == p_val || Some(val) == q_val {
                    return root;
                }
                let left =
                    lowest_common_ancestor(node.borrow().left.clone(), p.clone(), q.clone());
                let right = lowest_common_ancestor(node.borrow().right.clone(), p, q);
                if left.is_some() && right.is_some() {
                    return root;
                }
                left.or(right)
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
    preamble=(RC_REFCELL, VEC_DEQUE, TREE_NODE),
    problems=(
        _p(
            102, "Binary Tree Level Order Traversal", "Medium",
            "Snapshot queue.len() first - that's exactly one level's worth. Bind "
            "the children before pushing, or the borrow outlives the node.",
            "O(n) time, O(n) space",
            """
            pub fn level_order(root: Tree) -> Vec<Vec<i32>> {
                let mut levels = Vec::new();
                if root.is_none() {
                    return levels;
                }
                let mut queue: VecDeque<Rc<RefCell<TreeNode>>> = VecDeque::new();
                queue.push_back(root.unwrap());
                while !queue.is_empty() {
                    let mut level = Vec::new();
                    for _ in 0..queue.len() {
                        let node = queue.pop_front().unwrap();
                        level.push(node.borrow().val);
                        let left = node.borrow().left.clone();
                        let right = node.borrow().right.clone();
                        if let Some(left) = left {
                            queue.push_back(left);
                        }
                        if let Some(right) = right {
                            queue.push_back(right);
                        }
                    }
                    levels.push(level);
                }
                levels
            }
            """,
        ),
        _p(
            199, "Binary Tree Right Side View", "Medium",
            "Keep the last node of every level.",
            "O(n) time, O(n) space",
            """
            pub fn right_side_view(root: Tree) -> Vec<i32> {
                let mut view = Vec::new();
                if root.is_none() {
                    return view;
                }
                let mut queue: VecDeque<Rc<RefCell<TreeNode>>> = VecDeque::new();
                queue.push_back(root.unwrap());
                while !queue.is_empty() {
                    let size = queue.len();
                    for i in 0..size {
                        let node = queue.pop_front().unwrap();
                        if i == size - 1 {
                            view.push(node.borrow().val);
                        }
                        let left = node.borrow().left.clone();
                        let right = node.borrow().right.clone();
                        if let Some(left) = left {
                            queue.push_back(left);
                        }
                        if let Some(right) = right {
                            queue.push_back(right);
                        }
                    }
                }
                view
            }
            """,
        ),
        _p(
            103, "Binary Tree Zigzag Level Order", "Medium",
            "Same level walk - just reverse every other row before storing it.",
            "O(n) time, O(n) space",
            """
            pub fn zigzag_level_order(root: Tree) -> Vec<Vec<i32>> {
                let mut levels = Vec::new();
                if root.is_none() {
                    return levels;
                }
                let mut queue: VecDeque<Rc<RefCell<TreeNode>>> = VecDeque::new();
                queue.push_back(root.unwrap());
                let mut left_to_right = true;
                while !queue.is_empty() {
                    let mut level = Vec::new();
                    for _ in 0..queue.len() {
                        let node = queue.pop_front().unwrap();
                        level.push(node.borrow().val);
                        let left = node.borrow().left.clone();
                        let right = node.borrow().right.clone();
                        if let Some(left) = left {
                            queue.push_back(left);
                        }
                        if let Some(right) = right {
                            queue.push_back(right);
                        }
                    }
                    if !left_to_right {
                        level.reverse();
                    }
                    levels.push(level);
                    left_to_right = !left_to_right;
                }
                levels
            }
            """,
        ),
        _p(
            111, "Minimum Depth of Binary Tree", "Easy",
            "BFS stops at the first leaf it meets - DFS would walk the whole "
            "tree first.",
            "O(n) time, O(n) space",
            """
            pub fn min_depth(root: Tree) -> i32 {
                if root.is_none() {
                    return 0;
                }
                let mut queue: VecDeque<Rc<RefCell<TreeNode>>> = VecDeque::new();
                queue.push_back(root.unwrap());
                let mut depth = 1;
                while !queue.is_empty() {
                    for _ in 0..queue.len() {
                        let node = queue.pop_front().unwrap();
                        let left = node.borrow().left.clone();
                        let right = node.borrow().right.clone();
                        if left.is_none() && right.is_none() {
                            return depth;
                        }
                        if let Some(left) = left {
                            queue.push_back(left);
                        }
                        if let Some(right) = right {
                            queue.push_back(right);
                        }
                    }
                    depth += 1;
                }
                depth
            }
            """,
        ),
        _p(
            637, "Average of Levels in Binary Tree", "Easy",
            "One row at a time, so the divisor is just that row's length. Sum in "
            "i64: a full row of large values overflows i32.",
            "O(n) time, O(n) space",
            """
            pub fn average_of_levels(root: Tree) -> Vec<f64> {
                let mut averages = Vec::new();
                if root.is_none() {
                    return averages;
                }
                let mut queue: VecDeque<Rc<RefCell<TreeNode>>> = VecDeque::new();
                queue.push_back(root.unwrap());
                while !queue.is_empty() {
                    let size = queue.len();
                    let mut total = 0i64;
                    for _ in 0..size {
                        let node = queue.pop_front().unwrap();
                        total += node.borrow().val as i64;
                        let left = node.borrow().left.clone();
                        let right = node.borrow().right.clone();
                        if let Some(left) = left {
                            queue.push_back(left);
                        }
                        if let Some(right) = right {
                            queue.push_back(right);
                        }
                    }
                    averages.push(total as f64 / size as f64);
                }
                averages
            }
            """,
        ),
        _p(
            515, "Find Largest Value in Each Tree Row", "Medium",
            "Same row walk as the average - swap the running total for a running "
            "max. Option, not 0, or an all-negative row comes back wrong.",
            "O(n) time, O(n) space",
            """
            pub fn largest_values(root: Tree) -> Vec<i32> {
                let mut largest = Vec::new();
                if root.is_none() {
                    return largest;
                }
                let mut queue: VecDeque<Rc<RefCell<TreeNode>>> = VecDeque::new();
                queue.push_back(root.unwrap());
                while !queue.is_empty() {
                    let mut best: Option<i32> = None;
                    for _ in 0..queue.len() {
                        let node = queue.pop_front().unwrap();
                        let val = node.borrow().val;
                        if best.is_none() || val > best.unwrap() {
                            best = Some(val);
                        }
                        let left = node.borrow().left.clone();
                        let right = node.borrow().right.clone();
                        if let Some(left) = left {
                            queue.push_back(left);
                        }
                        if let Some(right) = right {
                            queue.push_back(right);
                        }
                    }
                    largest.push(best.unwrap());
                }
                largest
            }
            """,
        ),
        _p(
            1161, "Maximum Level Sum of a Binary Tree", "Medium",
            "Number the levels as you go and keep the best - ties go to the "
            "shallower one, which strict greater-than gives you.",
            "O(n) time, O(n) space",
            """
            pub fn max_level_sum(root: Tree) -> i32 {
                if root.is_none() {
                    return 0;
                }
                let mut queue: VecDeque<Rc<RefCell<TreeNode>>> = VecDeque::new();
                queue.push_back(root.unwrap());
                let mut level = 0;
                let mut best_level = 1;
                let mut best_sum: Option<i64> = None;
                while !queue.is_empty() {
                    level += 1;
                    let mut total = 0i64;
                    for _ in 0..queue.len() {
                        let node = queue.pop_front().unwrap();
                        total += node.borrow().val as i64;
                        let left = node.borrow().left.clone();
                        let right = node.borrow().right.clone();
                        if let Some(left) = left {
                            queue.push_back(left);
                        }
                        if let Some(right) = right {
                            queue.push_back(right);
                        }
                    }
                    if best_sum.is_none() || total > best_sum.unwrap() {
                        best_sum = Some(total);
                        best_level = level;
                    }
                }
                best_level
            }
            """,
        ),
        _p(
            662, "Maximum Width of Binary Tree", "Medium",
            "Queue the heap index with each node; a row's width is last minus "
            "first plus one. Rebase each row at zero or the index overflows.",
            "O(n) time, O(n) space",
            """
            pub fn width_of_binary_tree(root: Tree) -> i32 {
                if root.is_none() {
                    return 0;
                }
                let mut widest = 0u64;
                let mut queue: VecDeque<(Rc<RefCell<TreeNode>>, u64)> = VecDeque::new();
                queue.push_back((root.unwrap(), 0));
                while !queue.is_empty() {
                    let size = queue.len();
                    let first = queue.front().unwrap().1;
                    let mut last = first;
                    for _ in 0..size {
                        let (node, index) = queue.pop_front().unwrap();
                        let index = index - first;
                        last = index;
                        let left = node.borrow().left.clone();
                        let right = node.borrow().right.clone();
                        if let Some(left) = left {
                            queue.push_back((left, index * 2));
                        }
                        if let Some(right) = right {
                            queue.push_back((right, index * 2 + 1));
                        }
                    }
                    let width = last + 1;
                    if width > widest {
                        widest = width;
                    }
                }
                widest as i32
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
    preamble=(RC_REFCELL, COLLECTIONS, VEC_DEQUE, GRAPH_NODE),
    problems=(
        _p(
            733, "Flood Fill", "Easy",
            "Recurse to the four neighbours, stopping when the colour doesn't "
            "match. The grid travels as &mut rather than being captured.",
            "O(n) time, O(n) space",
            """
            pub fn flood_fill(
                image: Vec<Vec<i32>>,
                sr: i32,
                sc: i32,
                color: i32,
            ) -> Vec<Vec<i32>> {
                let mut image = image;
                let start = image[sr as usize][sc as usize];
                if start == color {
                    return image;
                }
                fn fill(image: &mut Vec<Vec<i32>>, r: i32, c: i32, start: i32, color: i32) {
                    let rows = image.len() as i32;
                    let cols = image[0].len() as i32;
                    if r < 0 || r >= rows || c < 0 || c >= cols {
                        return;
                    }
                    if image[r as usize][c as usize] != start {
                        return;
                    }
                    image[r as usize][c as usize] = color;
                    fill(image, r + 1, c, start, color);
                    fill(image, r - 1, c, start, color);
                    fill(image, r, c + 1, start, color);
                    fill(image, r, c - 1, start, color);
                }
                fill(&mut image, sr, sc, start, color);
                image
            }
            """,
        ),
        _p(
            200, "Number of Islands", "Medium",
            "Each unvisited land cell starts an island; sink the whole thing.",
            "O(rows * cols) time, O(rows * cols) space",
            """
            pub fn num_islands(grid: Vec<Vec<char>>) -> i32 {
                if grid.is_empty() {
                    return 0;
                }
                let mut grid = grid;
                let rows = grid.len();
                let cols = grid[0].len();
                let mut count = 0;
                fn sink(grid: &mut Vec<Vec<char>>, r: i32, c: i32) {
                    let rows = grid.len() as i32;
                    let cols = grid[0].len() as i32;
                    if r < 0 || r >= rows || c < 0 || c >= cols {
                        return;
                    }
                    if grid[r as usize][c as usize] != '1' {
                        return;
                    }
                    grid[r as usize][c as usize] = '0';
                    sink(grid, r + 1, c);
                    sink(grid, r - 1, c);
                    sink(grid, r, c + 1);
                    sink(grid, r, c - 1);
                }
                for r in 0..rows {
                    for c in 0..cols {
                        if grid[r][c] == '1' {
                            count += 1;
                            sink(&mut grid, r as i32, c as i32);
                        }
                    }
                }
                count
            }
            """,
        ),
        _p(
            994, "Rotting Oranges", "Medium",
            "Multi-source BFS - every rotten orange starts in the queue at minute 0.",
            "O(rows * cols) time, O(rows * cols) space",
            """
            pub fn oranges_rotting(grid: Vec<Vec<i32>>) -> i32 {
                let mut grid = grid;
                let rows = grid.len();
                let cols = grid[0].len();
                let mut queue: VecDeque<(usize, usize)> = VecDeque::new();
                let mut fresh = 0;
                for r in 0..rows {
                    for c in 0..cols {
                        if grid[r][c] == 2 {
                            queue.push_back((r, c));
                        } else if grid[r][c] == 1 {
                            fresh += 1;
                        }
                    }
                }
                let mut minutes = 0;
                while !queue.is_empty() && fresh > 0 {
                    minutes += 1;
                    for _ in 0..queue.len() {
                        let (r, c) = queue.pop_front().unwrap();
                        for (dr, dc) in [(1i32, 0i32), (-1, 0), (0, 1), (0, -1)] {
                            let nr = r as i32 + dr;
                            let nc = c as i32 + dc;
                            if nr < 0 || nr >= rows as i32 || nc < 0 || nc >= cols as i32 {
                                continue;
                            }
                            if grid[nr as usize][nc as usize] == 1 {
                                grid[nr as usize][nc as usize] = 2;
                                fresh -= 1;
                                queue.push_back((nr as usize, nc as usize));
                            }
                        }
                    }
                }
                if fresh > 0 {
                    -1
                } else {
                    minutes
                }
            }
            """,
        ),
        _p(
            133, "Clone Graph", "Medium",
            "A map from value to its copy doubles as the visited set - and it "
            "must be filled BEFORE recursing, or a cycle never ends.",
            "O(n + e) time, O(n) space",
            """
            pub fn clone_graph(node: Option<Rc<RefCell<Node>>>) -> Option<Rc<RefCell<Node>>> {
                fn copy(
                    cur: Option<Rc<RefCell<Node>>>,
                    clones: &mut HashMap<i32, Rc<RefCell<Node>>>,
                ) -> Option<Rc<RefCell<Node>>> {
                    let cur = cur?;
                    let val = cur.borrow().val;
                    if let Some(existing) = clones.get(&val) {
                        return Some(existing.clone());
                    }
                    let clone = Rc::new(RefCell::new(Node::new(val)));
                    clones.insert(val, clone.clone());
                    let neighbors = cur.borrow().neighbors.clone();
                    for neighbor in neighbors {
                        let copied = copy(Some(neighbor), clones);
                        clone.borrow_mut().neighbors.push(copied.unwrap());
                    }
                    Some(clone)
                }
                let mut clones = HashMap::new();
                copy(node, &mut clones)
            }
            """,
        ),
        _p(
            695, "Max Area of Island", "Medium",
            "Same flood fill, but the walk returns a size instead of just "
            "marking cells.",
            "O(m * n) time, O(m * n) space",
            """
            pub fn max_area_of_island(grid: Vec<Vec<i32>>) -> i32 {
                if grid.is_empty() {
                    return 0;
                }
                let mut grid = grid;
                let rows = grid.len();
                let cols = grid[0].len();
                fn fill(grid: &mut Vec<Vec<i32>>, r: i32, c: i32) -> i32 {
                    let rows = grid.len() as i32;
                    let cols = grid[0].len() as i32;
                    if r < 0 || c < 0 || r >= rows || c >= cols {
                        return 0;
                    }
                    if grid[r as usize][c as usize] != 1 {
                        return 0;
                    }
                    grid[r as usize][c as usize] = 0;
                    1 + fill(grid, r + 1, c)
                        + fill(grid, r - 1, c)
                        + fill(grid, r, c + 1)
                        + fill(grid, r, c - 1)
                }
                let mut best = 0;
                for r in 0..rows {
                    for c in 0..cols {
                        let area = fill(&mut grid, r as i32, c as i32);
                        if area > best {
                            best = area;
                        }
                    }
                }
                best
            }
            """,
        ),
        _p(
            547, "Number of Provinces", "Medium",
            "Every walk that starts somewhere unvisited is one more connected group.",
            "O(n * n) time, O(n) space",
            """
            pub fn find_circle_num(is_connected: Vec<Vec<i32>>) -> i32 {
                let n = is_connected.len();
                let mut seen: HashSet<usize> = HashSet::new();
                fn visit(city: usize, is_connected: &Vec<Vec<i32>>, seen: &mut HashSet<usize>) {
                    seen.insert(city);
                    for other in 0..is_connected.len() {
                        if is_connected[city][other] == 1 && !seen.contains(&other) {
                            visit(other, is_connected, seen);
                        }
                    }
                }
                let mut groups = 0;
                for city in 0..n {
                    if !seen.contains(&city) {
                        visit(city, &is_connected, &mut seen);
                        groups += 1;
                    }
                }
                groups
            }
            """,
        ),
        _p(
            542, "01 Matrix", "Medium",
            "Start the queue from every zero at once, and the first visit is the "
            "nearest one. -1 marks unreached, so no second grid is needed.",
            "O(m * n) time, O(m * n) space",
            """
            pub fn update_matrix(mat: Vec<Vec<i32>>) -> Vec<Vec<i32>> {
                let rows = mat.len();
                let cols = mat[0].len();
                let mut out = vec![vec![-1; cols]; rows];
                let mut queue: VecDeque<(usize, usize)> = VecDeque::new();
                for r in 0..rows {
                    for c in 0..cols {
                        if mat[r][c] == 0 {
                            out[r][c] = 0;
                            queue.push_back((r, c));
                        }
                    }
                }
                while let Some((r, c)) = queue.pop_front() {
                    for (dr, dc) in [(1i32, 0i32), (-1, 0), (0, 1), (0, -1)] {
                        let nr = r as i32 + dr;
                        let nc = c as i32 + dc;
                        if nr < 0 || nr >= rows as i32 || nc < 0 || nc >= cols as i32 {
                            continue;
                        }
                        let (nr, nc) = (nr as usize, nc as usize);
                        if out[nr][nc] == -1 {
                            out[nr][nc] = out[r][c] + 1;
                            queue.push_back((nr, nc));
                        }
                    }
                }
                out
            }
            """,
        ),
        _p(
            417, "Pacific Atlantic Water Flow", "Medium",
            "Walk uphill from each ocean instead of downhill from each cell; the "
            "answer is the overlap.",
            "O(m * n) time, O(m * n) space",
            """
            pub fn pacific_atlantic(heights: Vec<Vec<i32>>) -> Vec<Vec<i32>> {
                if heights.is_empty() {
                    return Vec::new();
                }
                let rows = heights.len();
                let cols = heights[0].len();
                fn climb(
                    r: usize,
                    c: usize,
                    heights: &Vec<Vec<i32>>,
                    seen: &mut HashSet<(usize, usize)>,
                ) {
                    seen.insert((r, c));
                    let rows = heights.len() as i32;
                    let cols = heights[0].len() as i32;
                    for (dr, dc) in [(1i32, 0i32), (-1, 0), (0, 1), (0, -1)] {
                        let nr = r as i32 + dr;
                        let nc = c as i32 + dc;
                        if nr < 0 || nr >= rows || nc < 0 || nc >= cols {
                            continue;
                        }
                        let (nr, nc) = (nr as usize, nc as usize);
                        if !seen.contains(&(nr, nc)) && heights[nr][nc] >= heights[r][c] {
                            climb(nr, nc, heights, seen);
                        }
                    }
                }
                let mut pacific: HashSet<(usize, usize)> = HashSet::new();
                let mut atlantic: HashSet<(usize, usize)> = HashSet::new();
                for c in 0..cols {
                    climb(0, c, &heights, &mut pacific);
                    climb(rows - 1, c, &heights, &mut atlantic);
                }
                for r in 0..rows {
                    climb(r, 0, &heights, &mut pacific);
                    climb(r, cols - 1, &heights, &mut atlantic);
                }
                let mut both: Vec<(usize, usize)> =
                    pacific.intersection(&atlantic).copied().collect();
                both.sort();
                both.iter().map(|&(r, c)| vec![r as i32, c as i32]).collect()
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
    preamble=(HASH_MAP,),
    problems=(
        _p(
            78, "Subsets", "Medium",
            "Every prefix of the walk is already a valid subset - record on entry.",
            "O(n * 2^n) time, O(n) recursion depth",
            """
            pub fn subsets(nums: Vec<i32>) -> Vec<Vec<i32>> {
                fn backtrack(
                    start: usize,
                    nums: &Vec<i32>,
                    current: &mut Vec<i32>,
                    result: &mut Vec<Vec<i32>>,
                ) {
                    result.push(current.clone());
                    for i in start..nums.len() {
                        current.push(nums[i]);
                        backtrack(i + 1, nums, current, result);
                        current.pop();
                    }
                }
                let mut result = Vec::new();
                let mut current = Vec::new();
                backtrack(0, &nums, &mut current, &mut result);
                result
            }
            """,
        ),
        _p(
            90, "Subsets II", "Medium",
            "Sort first, then skip a duplicate unless it's the first pick at "
            "this level - the guard is i > start, not i > 0.",
            "O(n * 2^n) time, O(n) recursion depth",
            """
            pub fn subsets_with_dup(nums: Vec<i32>) -> Vec<Vec<i32>> {
                let mut nums = nums;
                nums.sort();
                fn backtrack(
                    start: usize,
                    nums: &Vec<i32>,
                    current: &mut Vec<i32>,
                    result: &mut Vec<Vec<i32>>,
                ) {
                    result.push(current.clone());
                    for i in start..nums.len() {
                        if i > start && nums[i] == nums[i - 1] {
                            continue;
                        }
                        current.push(nums[i]);
                        backtrack(i + 1, nums, current, result);
                        current.pop();
                    }
                }
                let mut result = Vec::new();
                let mut current = Vec::new();
                backtrack(0, &nums, &mut current, &mut result);
                result
            }
            """,
        ),
        _p(
            46, "Permutations", "Medium",
            "Order matters, so track which indexes are already used - and clear "
            "the flag on the way back out.",
            "O(n * n!) time, O(n) recursion depth",
            """
            pub fn permute(nums: Vec<i32>) -> Vec<Vec<i32>> {
                fn backtrack(
                    nums: &Vec<i32>,
                    used: &mut Vec<bool>,
                    current: &mut Vec<i32>,
                    result: &mut Vec<Vec<i32>>,
                ) {
                    if current.len() == nums.len() {
                        result.push(current.clone());
                        return;
                    }
                    for i in 0..nums.len() {
                        if used[i] {
                            continue;
                        }
                        used[i] = true;
                        current.push(nums[i]);
                        backtrack(nums, used, current, result);
                        current.pop();
                        used[i] = false;
                    }
                }
                let mut result = Vec::new();
                let mut current = Vec::new();
                let mut used = vec![false; nums.len()];
                backtrack(&nums, &mut used, &mut current, &mut result);
                result
            }
            """,
        ),
        _p(
            39, "Combination Sum", "Medium",
            "Reuse allowed, so recurse with i (not i + 1) and shrink the remainder.",
            "O(n^(target/min)) time, O(target) depth",
            """
            pub fn combination_sum(candidates: Vec<i32>, target: i32) -> Vec<Vec<i32>> {
                fn backtrack(
                    start: usize,
                    remaining: i32,
                    candidates: &Vec<i32>,
                    current: &mut Vec<i32>,
                    result: &mut Vec<Vec<i32>>,
                ) {
                    if remaining == 0 {
                        result.push(current.clone());
                        return;
                    }
                    if remaining < 0 {
                        return;
                    }
                    for i in start..candidates.len() {
                        current.push(candidates[i]);
                        backtrack(i, remaining - candidates[i], candidates, current, result);
                        current.pop();
                    }
                }
                let mut result = Vec::new();
                let mut current = Vec::new();
                backtrack(0, target, &candidates, &mut current, &mut result);
                result
            }
            """,
        ),
        _p(
            79, "Word Search", "Medium",
            "Backtracking on a grid - blank out the cell, recurse, then restore it.",
            "O(rows * cols * 4^len(word)) time, O(len(word)) depth",
            """
            pub fn exist(board: Vec<Vec<char>>, word: String) -> bool {
                let mut board = board;
                let word: Vec<char> = word.chars().collect();
                let rows = board.len();
                let cols = board[0].len();
                fn search(
                    board: &mut Vec<Vec<char>>,
                    word: &Vec<char>,
                    r: i32,
                    c: i32,
                    i: usize,
                ) -> bool {
                    if i == word.len() {
                        return true;
                    }
                    let rows = board.len() as i32;
                    let cols = board[0].len() as i32;
                    if r < 0 || r >= rows || c < 0 || c >= cols {
                        return false;
                    }
                    if board[r as usize][c as usize] != word[i] {
                        return false;
                    }
                    board[r as usize][c as usize] = '#';
                    let found = search(board, word, r + 1, c, i + 1)
                        || search(board, word, r - 1, c, i + 1)
                        || search(board, word, r, c + 1, i + 1)
                        || search(board, word, r, c - 1, i + 1);
                    board[r as usize][c as usize] = word[i];
                    found
                }
                for r in 0..rows {
                    for c in 0..cols {
                        if search(&mut board, &word, r as i32, c as i32, 0) {
                            return true;
                        }
                    }
                }
                false
            }
            """,
        ),
        _p(
            77, "Combinations", "Medium",
            "Only ever pick numbers after the last one taken, so no pair is "
            "built twice.",
            "O(k * C(n, k)) time, O(k) space",
            """
            pub fn combine(n: i32, k: i32) -> Vec<Vec<i32>> {
                fn walk(
                    start: i32,
                    n: i32,
                    k: i32,
                    picked: &mut Vec<i32>,
                    out: &mut Vec<Vec<i32>>,
                ) {
                    if picked.len() as i32 == k {
                        out.push(picked.clone());
                        return;
                    }
                    for value in start..=n {
                        picked.push(value);
                        walk(value + 1, n, k, picked, out);
                        picked.pop();
                    }
                }
                let mut out = Vec::new();
                let mut picked = Vec::new();
                walk(1, n, k, &mut picked, &mut out);
                out
            }
            """,
        ),
        _p(
            17, "Letter Combinations of a Phone Number", "Medium",
            "One digit is one level of the tree, and its letters are that "
            "level's branches.",
            "O(4 ** n) time, O(n) space",
            """
            pub fn letter_combinations(digits: String) -> Vec<String> {
                if digits.is_empty() {
                    return Vec::new();
                }
                let keys: HashMap<char, &str> = [
                    ('2', "abc"),
                    ('3', "def"),
                    ('4', "ghi"),
                    ('5', "jkl"),
                    ('6', "mno"),
                    ('7', "pqrs"),
                    ('8', "tuv"),
                    ('9', "wxyz"),
                ]
                .into_iter()
                .collect();
                fn walk(
                    index: usize,
                    built: String,
                    digits: &Vec<char>,
                    keys: &HashMap<char, &str>,
                    out: &mut Vec<String>,
                ) {
                    if index == digits.len() {
                        out.push(built);
                        return;
                    }
                    for letter in keys[&digits[index]].chars() {
                        walk(index + 1, format!("{}{}", built, letter), digits, keys, out);
                    }
                }
                let digits: Vec<char> = digits.chars().collect();
                let mut out = Vec::new();
                walk(0, String::new(), &digits, &keys, &mut out);
                out
            }
            """,
        ),
        _p(
            131, "Palindrome Partitioning", "Medium",
            "Cut after every position whose prefix reads the same both ways, "
            "then solve the rest.",
            "O(n * 2 ** n) time, O(n) space",
            """
            pub fn partition(text: String) -> Vec<Vec<String>> {
                let chars: Vec<char> = text.chars().collect();
                fn walk(
                    start: usize,
                    chars: &Vec<char>,
                    built: &mut Vec<String>,
                    out: &mut Vec<Vec<String>>,
                ) {
                    if start == chars.len() {
                        out.push(built.clone());
                        return;
                    }
                    for end in (start + 1)..=chars.len() {
                        let piece: Vec<char> = chars[start..end].to_vec();
                        let reversed: Vec<char> = piece.iter().rev().copied().collect();
                        if piece == reversed {
                            built.push(piece.into_iter().collect());
                            walk(end, chars, built, out);
                            built.pop();
                        }
                    }
                }
                let mut out = Vec::new();
                let mut built = Vec::new();
                walk(0, &chars, &mut built, &mut out);
                out
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
    preamble=(BINARY_HEAP, HASH_MAP),
    problems=(
        _p(
            215, "Kth Largest Element in an Array", "Medium",
            "Hold a min-heap of size k; its root is the kth largest. BinaryHeap "
            "is a MAX-heap, so Reverse is what makes it a min-heap.",
            "O(n log k) time, O(k) space",
            """
            pub fn find_kth_largest(nums: Vec<i32>, k: i32) -> i32 {
                let mut heap: BinaryHeap<Reverse<i32>> = BinaryHeap::new();
                for n in nums {
                    heap.push(Reverse(n));
                    if heap.len() > k as usize {
                        heap.pop();
                    }
                }
                heap.peek().unwrap().0
            }
            """,
        ),
        _p(
            347, "Top K Frequent Elements", "Medium",
            "Count first, then a Reverse heap on (count, value) keeps only k.",
            "O(n log k) time, O(n) space",
            """
            pub fn top_k_frequent(nums: Vec<i32>, k: i32) -> Vec<i32> {
                let mut counts: HashMap<i32, i32> = HashMap::new();
                for n in nums {
                    *counts.entry(n).or_insert(0) += 1;
                }
                let mut heap: BinaryHeap<Reverse<(i32, i32)>> = BinaryHeap::new();
                for (value, count) in counts {
                    heap.push(Reverse((count, value)));
                    if heap.len() > k as usize {
                        heap.pop();
                    }
                }
                heap.into_iter().map(|Reverse((_, value))| value).collect()
            }
            """,
        ),
        _p(
            973, "K Closest Points to Origin", "Medium",
            "A plain max-heap already pops the FURTHEST point first, so no "
            "negation - that is Python's workaround, not Rust's.",
            "O(n log k) time, O(k) space",
            """
            pub fn k_closest(points: Vec<Vec<i32>>, k: i32) -> Vec<Vec<i32>> {
                let mut heap: BinaryHeap<(i32, i32, i32)> = BinaryHeap::new();
                for point in points {
                    let (x, y) = (point[0], point[1]);
                    let dist = x * x + y * y;
                    heap.push((dist, x, y));
                    if heap.len() > k as usize {
                        heap.pop();
                    }
                }
                heap.into_iter().map(|(_, x, y)| vec![x, y]).collect()
            }
            """,
        ),
        _p(
            1046, "Last Stone Weight", "Easy",
            "Rust's heap is a max-heap, so the two heaviest stones just pop off "
            "the top - collect() builds it in one pass.",
            "O(n log n) time, O(n) space",
            """
            pub fn last_stone_weight(stones: Vec<i32>) -> i32 {
                let mut heap: BinaryHeap<i32> = stones.into_iter().collect();
                while heap.len() > 1 {
                    let first = heap.pop().unwrap();
                    let second = heap.pop().unwrap();
                    if first != second {
                        heap.push(first - second);
                    }
                }
                heap.pop().unwrap_or(0)
            }
            """,
        ),
        _p(
            692, "Top K Frequent Words", "Medium",
            "Key on (count, Reverse(word)): the max-heap then gives most "
            "frequent first and breaks ties alphabetically for free.",
            "O(n + k log n) time, O(n) space",
            """
            pub fn top_k_frequent_words(words: Vec<String>, k: i32) -> Vec<String> {
                let mut counts: HashMap<String, i32> = HashMap::new();
                for word in words {
                    *counts.entry(word).or_insert(0) += 1;
                }
                let mut heap: BinaryHeap<(i32, Reverse<String>)> = counts
                    .into_iter()
                    .map(|(word, count)| (count, Reverse(word)))
                    .collect();
                let mut out = Vec::new();
                for _ in 0..k {
                    if let Some((_, Reverse(word))) = heap.pop() {
                        out.push(word);
                    }
                }
                out
            }
            """,
        ),
        _p(
            451, "Sort Characters By Frequency", "Medium",
            "Count, then pop the max-heap most-frequent-first and repeat each "
            "character.",
            "O(n log n) time, O(n) space",
            """
            pub fn frequency_sort(s: String) -> String {
                let mut counts: HashMap<char, i32> = HashMap::new();
                for ch in s.chars() {
                    *counts.entry(ch).or_insert(0) += 1;
                }
                let mut heap: BinaryHeap<(i32, char)> = counts
                    .into_iter()
                    .map(|(ch, count)| (count, ch))
                    .collect();
                let mut out = String::new();
                while let Some((count, ch)) = heap.pop() {
                    for _ in 0..count {
                        out.push(ch);
                    }
                }
                out
            }
            """,
        ),
        _p(
            378, "Kth Smallest Element in a Sorted Matrix", "Medium",
            "Seed the heap with each row's head, then keep pulling the smallest "
            "and refilling from its row.",
            "O(k log n) time, O(n) space",
            """
            pub fn kth_smallest(matrix: Vec<Vec<i32>>, k: i32) -> i32 {
                let mut heap: BinaryHeap<Reverse<(i32, usize, usize)>> = BinaryHeap::new();
                for row in 0..matrix.len().min(k as usize) {
                    heap.push(Reverse((matrix[row][0], row, 0)));
                }
                let mut value = 0;
                for _ in 0..k {
                    let Reverse((v, row, col)) = heap.pop().unwrap();
                    value = v;
                    if col + 1 < matrix[row].len() {
                        heap.push(Reverse((matrix[row][col + 1], row, col + 1)));
                    }
                }
                value
            }
            """,
        ),
        _p(
            767, "Reorganize String", "Medium",
            "Always place the most common letter left, holding the one you just "
            "used aside for a turn.",
            "O(n log n) time, O(n) space",
            """
            pub fn reorganize_string(s: String) -> String {
                let mut counts: HashMap<char, i32> = HashMap::new();
                for ch in s.chars() {
                    *counts.entry(ch).or_insert(0) += 1;
                }
                let mut heap: BinaryHeap<(i32, char)> = counts
                    .into_iter()
                    .map(|(ch, count)| (count, ch))
                    .collect();
                let mut out = String::new();
                let mut held: Option<(i32, char)> = None;
                while let Some((count, ch)) = heap.pop() {
                    out.push(ch);
                    if let Some(previous) = held.take() {
                        heap.push(previous);
                    }
                    if count - 1 > 0 {
                        held = Some((count - 1, ch));
                    }
                }
                if out.len() == s.len() {
                    out
                } else {
                    String::new()
                }
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
    preamble=(COLLECTIONS, VEC_DEQUE),
    problems=(
        _p(
            207, "Course Schedule", "Medium",
            "If a cycle exists you can never drain the queue - count what you took.",
            "O(v + e) time, O(v + e) space",
            """
            pub fn can_finish(num_courses: i32, prerequisites: Vec<Vec<i32>>) -> bool {
                let n = num_courses as usize;
                let mut graph: Vec<Vec<usize>> = vec![Vec::new(); n];
                let mut indegree = vec![0; n];
                for pair in &prerequisites {
                    let (course, prereq) = (pair[0] as usize, pair[1] as usize);
                    graph[prereq].push(course);
                    indegree[course] += 1;
                }
                let mut queue: VecDeque<usize> =
                    (0..n).filter(|&i| indegree[i] == 0).collect();
                let mut taken = 0;
                while let Some(node) = queue.pop_front() {
                    taken += 1;
                    for &next in &graph[node] {
                        indegree[next] -= 1;
                        if indegree[next] == 0 {
                            queue.push_back(next);
                        }
                    }
                }
                taken == n
            }
            """,
        ),
        _p(
            210, "Course Schedule II", "Medium",
            "Same peel, but keep the order you took things in.",
            "O(v + e) time, O(v + e) space",
            """
            pub fn find_order(num_courses: i32, prerequisites: Vec<Vec<i32>>) -> Vec<i32> {
                let n = num_courses as usize;
                let mut graph: Vec<Vec<usize>> = vec![Vec::new(); n];
                let mut indegree = vec![0; n];
                for pair in &prerequisites {
                    let (course, prereq) = (pair[0] as usize, pair[1] as usize);
                    graph[prereq].push(course);
                    indegree[course] += 1;
                }
                let mut queue: VecDeque<usize> =
                    (0..n).filter(|&i| indegree[i] == 0).collect();
                let mut order = Vec::new();
                while let Some(node) = queue.pop_front() {
                    order.push(node as i32);
                    for &next in &graph[node] {
                        indegree[next] -= 1;
                        if indegree[next] == 0 {
                            queue.push_back(next);
                        }
                    }
                }
                if order.len() == n {
                    order
                } else {
                    Vec::new()
                }
            }
            """,
        ),
        _p(
            310, "Minimum Height Trees", "Medium",
            "Peel leaves layer by layer; the last 1 or 2 left are the centres.",
            "O(v + e) time, O(v + e) space",
            """
            pub fn find_min_height_trees(n: i32, edges: Vec<Vec<i32>>) -> Vec<i32> {
                if n == 1 {
                    return vec![0];
                }
                let n = n as usize;
                let mut graph: Vec<HashSet<usize>> = vec![HashSet::new(); n];
                for edge in &edges {
                    let (a, b) = (edge[0] as usize, edge[1] as usize);
                    graph[a].insert(b);
                    graph[b].insert(a);
                }
                let mut leaves: Vec<usize> =
                    (0..n).filter(|&i| graph[i].len() == 1).collect();
                let mut remaining = n;
                while remaining > 2 {
                    remaining -= leaves.len();
                    let mut next_leaves = Vec::new();
                    for leaf in leaves {
                        let neighbor = *graph[leaf].iter().next().unwrap();
                        graph[leaf].remove(&neighbor);
                        graph[neighbor].remove(&leaf);
                        if graph[neighbor].len() == 1 {
                            next_leaves.push(neighbor);
                        }
                    }
                    leaves = next_leaves;
                }
                leaves.into_iter().map(|x| x as i32).collect()
            }
            """,
        ),
        _p(
            802, "Find Eventual Safe States", "Medium",
            "Reverse every edge, then peel from the terminal nodes - whatever "
            "drains is safe.",
            "O(v + e) time, O(v + e) space",
            """
            pub fn eventual_safe_nodes(graph: Vec<Vec<i32>>) -> Vec<i32> {
                let n = graph.len();
                let mut reverse: Vec<Vec<usize>> = vec![Vec::new(); n];
                let mut outdegree = vec![0; n];
                for node in 0..n {
                    outdegree[node] = graph[node].len();
                    for &next in &graph[node] {
                        reverse[next as usize].push(node);
                    }
                }
                let mut queue: VecDeque<usize> =
                    (0..n).filter(|&i| outdegree[i] == 0).collect();
                let mut safe = Vec::new();
                while let Some(node) = queue.pop_front() {
                    safe.push(node as i32);
                    for &prev in &reverse[node] {
                        outdegree[prev] -= 1;
                        if outdegree[prev] == 0 {
                            queue.push_back(prev);
                        }
                    }
                }
                safe.sort();
                safe
            }
            """,
        ),
        _p(
            1462, "Course Schedule IV", "Medium",
            "Peel in order, and let each course inherit the prerequisite set of "
            "everything before it.",
            "O(v * e) time, O(v * v) space",
            """
            pub fn check_if_prerequisite(
                num_courses: i32,
                prerequisites: Vec<Vec<i32>>,
                queries: Vec<Vec<i32>>,
            ) -> Vec<bool> {
                let n = num_courses as usize;
                let mut graph: Vec<Vec<usize>> = vec![Vec::new(); n];
                let mut indegree = vec![0; n];
                for pair in &prerequisites {
                    let (prereq, course) = (pair[0] as usize, pair[1] as usize);
                    graph[prereq].push(course);
                    indegree[course] += 1;
                }
                let mut needs: Vec<HashSet<usize>> = vec![HashSet::new(); n];
                let mut queue: VecDeque<usize> =
                    (0..n).filter(|&i| indegree[i] == 0).collect();
                while let Some(node) = queue.pop_front() {
                    let inherited = needs[node].clone();
                    for &next in &graph[node].clone() {
                        needs[next].insert(node);
                        for &item in &inherited {
                            needs[next].insert(item);
                        }
                        indegree[next] -= 1;
                        if indegree[next] == 0 {
                            queue.push_back(next);
                        }
                    }
                }
                queries
                    .iter()
                    .map(|q| needs[q[1] as usize].contains(&(q[0] as usize)))
                    .collect()
            }
            """,
        ),
        _p(
            2115, "Find All Possible Recipes from Given Supplies", "Medium",
            "Ingredients are prerequisites: a recipe unlocks once its count of "
            "missing items hits zero, and then becomes an ingredient itself.",
            "O(v + e) time, O(v + e) space",
            """
            pub fn find_all_recipes(
                recipes: Vec<String>,
                ingredients: Vec<Vec<String>>,
                supplies: Vec<String>,
            ) -> Vec<String> {
                let mut graph: HashMap<String, Vec<String>> = HashMap::new();
                let mut indegree: HashMap<String, i32> = HashMap::new();
                for recipe in &recipes {
                    indegree.insert(recipe.clone(), 0);
                }
                for (recipe, needed) in recipes.iter().zip(ingredients.iter()) {
                    for item in needed {
                        graph
                            .entry(item.clone())
                            .or_insert_with(Vec::new)
                            .push(recipe.clone());
                        *indegree.get_mut(recipe).unwrap() += 1;
                    }
                }
                let mut queue: VecDeque<String> = supplies.into_iter().collect();
                let mut made = Vec::new();
                while let Some(item) = queue.pop_front() {
                    if let Some(dependents) = graph.get(&item) {
                        for recipe in dependents.clone() {
                            let count = indegree.get_mut(&recipe).unwrap();
                            *count -= 1;
                            if *count == 0 {
                                made.push(recipe.clone());
                                queue.push_back(recipe);
                            }
                        }
                    }
                }
                made
            }
            """,
        ),
        _p(
            1136, "Parallel Courses", "Medium",
            "Every drained layer of the queue is one semester - count the "
            "layers, not the courses.",
            "O(v + e) time, O(v + e) space",
            """
            pub fn minimum_semesters(n: i32, relations: Vec<Vec<i32>>) -> i32 {
                let n = n as usize;
                let mut graph: Vec<Vec<usize>> = vec![Vec::new(); n + 1];
                let mut indegree = vec![0; n + 1];
                for pair in &relations {
                    let (prereq, course) = (pair[0] as usize, pair[1] as usize);
                    graph[prereq].push(course);
                    indegree[course] += 1;
                }
                let mut queue: VecDeque<usize> =
                    (1..=n).filter(|&i| indegree[i] == 0).collect();
                let mut studied = 0;
                let mut semesters = 0;
                while !queue.is_empty() {
                    semesters += 1;
                    for _ in 0..queue.len() {
                        let node = queue.pop_front().unwrap();
                        studied += 1;
                        for &next in &graph[node] {
                            indegree[next] -= 1;
                            if indegree[next] == 0 {
                                queue.push_back(next);
                            }
                        }
                    }
                }
                if studied == n {
                    semesters
                } else {
                    -1
                }
            }
            """,
        ),
        _p(
            269, "Alien Dictionary", "Hard",
            "Adjacent words give one letter order each; the first difference is "
            "the only edge they prove.",
            "O(c) time, O(1) space",
            """
            pub fn alien_order(words: Vec<String>) -> String {
                let mut graph: HashMap<char, HashSet<char>> = HashMap::new();
                let mut indegree: HashMap<char, i32> = HashMap::new();
                for word in &words {
                    for ch in word.chars() {
                        graph.entry(ch).or_insert_with(HashSet::new);
                        indegree.entry(ch).or_insert(0);
                    }
                }
                for pair in words.windows(2) {
                    let first: Vec<char> = pair[0].chars().collect();
                    let second: Vec<char> = pair[1].chars().collect();
                    let mut split = false;
                    for (a, b) in first.iter().zip(second.iter()) {
                        if a != b {
                            if graph.get_mut(a).unwrap().insert(*b) {
                                *indegree.get_mut(b).unwrap() += 1;
                            }
                            split = true;
                            break;
                        }
                    }
                    if !split && first.len() > second.len() {
                        return String::new();
                    }
                }
                let mut queue: VecDeque<char> = indegree
                    .iter()
                    .filter(|(_, &d)| d == 0)
                    .map(|(&ch, _)| ch)
                    .collect();
                let mut order = String::new();
                while let Some(ch) = queue.pop_front() {
                    order.push(ch);
                    for &next in &graph[&ch].clone() {
                        let count = indegree.get_mut(&next).unwrap();
                        *count -= 1;
                        if *count == 0 {
                            queue.push_back(next);
                        }
                    }
                }
                if order.chars().count() == indegree.len() {
                    order
                } else {
                    String::new()
                }
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
    problems=(
        _p(
            70, "Climbing Stairs", "Easy",
            "Ways to reach step n = ways to n-1 plus ways to n-2. It's Fibonacci.",
            "O(n) time, O(1) space",
            """
            pub fn climb_stairs(n: i32) -> i32 {
                let mut prev = 1;
                let mut cur = 1;
                for _ in 0..(n - 1) {
                    let next = prev + cur;
                    prev = cur;
                    cur = next;
                }
                cur
            }
            """,
        ),
        _p(
            198, "House Robber", "Medium",
            "At each house: best so far if you skip it, or (best before last) "
            "plus it. Rust has no tuple swap, so bank the old value first.",
            "O(n) time, O(1) space",
            """
            pub fn rob(nums: Vec<i32>) -> i32 {
                let mut skip = 0;
                let mut take = 0;
                for n in nums {
                    let next_skip = skip.max(take);
                    take = skip + n;
                    skip = next_skip;
                }
                skip.max(take)
            }
            """,
        ),
        _p(
            322, "Coin Change", "Medium",
            "Build up every amount from 1 to target, trying each coin as the "
            "last one.",
            "O(amount * coins) time, O(amount) space",
            """
            pub fn coin_change(coins: Vec<i32>, amount: i32) -> i32 {
                let amount = amount as usize;
                let mut best = vec![amount as i32 + 1; amount + 1];
                best[0] = 0;
                for value in 1..=amount {
                    for &coin in &coins {
                        let coin = coin as usize;
                        if coin <= value {
                            best[value] = best[value].min(best[value - coin] + 1);
                        }
                    }
                }
                if best[amount] <= amount as i32 {
                    best[amount]
                } else {
                    -1
                }
            }
            """,
        ),
        _p(
            300, "Longest Increasing Subsequence", "Medium",
            "Keep the smallest possible tail for each length; binary search its "
            "slot.",
            "O(n log n) time, O(n) space",
            """
            pub fn length_of_lis(nums: Vec<i32>) -> i32 {
                let mut tails: Vec<i32> = Vec::new();
                for n in nums {
                    let mut low = 0;
                    let mut high = tails.len();
                    while low < high {
                        let mid = (low + high) / 2;
                        if tails[mid] < n {
                            low = mid + 1;
                        } else {
                            high = mid;
                        }
                    }
                    if low == tails.len() {
                        tails.push(n);
                    } else {
                        tails[low] = n;
                    }
                }
                tails.len() as i32
            }
            """,
        ),
        _p(
            746, "Min Cost Climbing Stairs", "Easy",
            "The cost of a step is its own plus the cheaper of the two ways off it.",
            "O(n) time, O(1) space",
            """
            pub fn min_cost_climbing_stairs(cost: Vec<i32>) -> i32 {
                let mut one = 0;
                let mut two = 0;
                for i in 2..=cost.len() {
                    let next = (one + cost[i - 1]).min(two + cost[i - 2]);
                    two = one;
                    one = next;
                }
                one
            }
            """,
        ),
        _p(
            1143, "Longest Common Subsequence", "Medium",
            "Matching letters extend the diagonal; otherwise take the better of "
            "dropping one.",
            "O(m * n) time, O(m * n) space",
            """
            pub fn longest_common_subsequence(first: String, second: String) -> i32 {
                let a: Vec<char> = first.chars().collect();
                let b: Vec<char> = second.chars().collect();
                let mut grid = vec![vec![0; b.len() + 1]; a.len() + 1];
                for i in (0..a.len()).rev() {
                    for j in (0..b.len()).rev() {
                        grid[i][j] = if a[i] == b[j] {
                            1 + grid[i + 1][j + 1]
                        } else {
                            grid[i + 1][j].max(grid[i][j + 1])
                        };
                    }
                }
                grid[0][0]
            }
            """,
        ),
        _p(
            139, "Word Break", "Medium",
            "A position is reachable when some word ends there and its start was "
            "reachable too.",
            "O(n * n * w) time, O(n) space",
            """
            pub fn word_break(text: String, words: Vec<String>) -> bool {
                let chars: Vec<char> = text.chars().collect();
                let mut reachable = vec![false; chars.len() + 1];
                reachable[0] = true;
                for end in 1..=chars.len() {
                    for word in &words {
                        let length = word.chars().count();
                        if length > end {
                            continue;
                        }
                        let start = end - length;
                        if reachable[start] {
                            let piece: String = chars[start..end].iter().collect();
                            if &piece == word {
                                reachable[end] = true;
                                break;
                            }
                        }
                    }
                }
                reachable[chars.len()]
            }
            """,
        ),
        _p(
            152, "Maximum Product Subarray", "Medium",
            "Track the smallest product too - a negative turns the worst into "
            "the best.",
            "O(n) time, O(1) space",
            """
            pub fn max_product(nums: Vec<i32>) -> i32 {
                let mut best = nums[0];
                let mut high = nums[0];
                let mut low = nums[0];
                for &n in &nums[1..] {
                    let options = [n, high * n, low * n];
                    high = *options.iter().max().unwrap();
                    low = *options.iter().min().unwrap();
                    if high > best {
                        best = high;
                    }
                }
                best
            }
            """,
        ),
    ),
)
