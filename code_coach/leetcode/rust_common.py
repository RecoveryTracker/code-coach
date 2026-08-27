"""Pieces shared by the Rust pattern files.

A separate module so `problems_rust` and `problems_rust2` can both use the
node types without importing each other — the same split the Dart bank uses.

The node definitions are LeetCode's own: `Option<Box<ListNode>>` for a list,
`Option<Rc<RefCell<TreeNode>>>` for a tree. Box is unique ownership, which is
why a list can be walked and rebuilt cheaply but cannot contain a cycle; a
tree needs shared, mutable children and so needs Rc and RefCell.
"""

from __future__ import annotations

from code_coach.leetcode.problems import Problem, _src


def _p(
    number: int,
    title: str,
    difficulty: str,
    idea: str,
    complexity: str,
    code: str,
) -> Problem:
    return Problem(number, title, difficulty, idea, complexity, _src(code))


COLLECTIONS = "use std::collections::HashMap;\nuse std::collections::HashSet;"
HASH_MAP = "use std::collections::HashMap;"
HASH_SET = "use std::collections::HashSet;"
VEC_DEQUE = "use std::collections::VecDeque;"
BINARY_HEAP = "use std::cmp::Reverse;\nuse std::collections::BinaryHeap;"
RC_REFCELL = "use std::cell::RefCell;\nuse std::rc::Rc;"

LIST_NODE = _src(
    """
    #[derive(PartialEq, Eq, Clone, Debug)]
    pub struct ListNode {
        pub val: i32,
        pub next: Option<Box<ListNode>>,
    }

    impl ListNode {
        pub fn new(val: i32) -> Self {
            ListNode { next: None, val }
        }
    }
    """
)

TREE_NODE = _src(
    """
    #[derive(Debug, PartialEq, Eq)]
    pub struct TreeNode {
        pub val: i32,
        pub left: Option<Rc<RefCell<TreeNode>>>,
        pub right: Option<Rc<RefCell<TreeNode>>>,
    }

    impl TreeNode {
        pub fn new(val: i32) -> Self {
            TreeNode { val, left: None, right: None }
        }
    }

    type Tree = Option<Rc<RefCell<TreeNode>>>;
    """
)

GRAPH_NODE = _src(
    """
    #[derive(Debug)]
    pub struct Node {
        pub val: i32,
        pub neighbors: Vec<Rc<RefCell<Node>>>,
    }

    impl Node {
        pub fn new(val: i32) -> Self {
            Node { val, neighbors: Vec::new() }
        }
    }
    """
)
