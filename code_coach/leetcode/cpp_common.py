"""Pieces shared by the C++ pattern files.

A separate module so `problems_cpp` and `problems_cpp2` can both use the node
types without importing each other — the same split the Dart and Rust banks
use.

The node definitions are LeetCode's own, raw pointers and all. That is what
the site hands you, and the muscle memory should match it.
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


VECTOR = "#include <vector>"
STRING = "#include <string>"
MAPS = "#include <unordered_map>\n#include <unordered_set>"
ORDERED = "#include <map>\n#include <set>"
ALGORITHM = "#include <algorithm>"
# std::function, for a recursive lambda — the usual way to write a
# helper that needs to see the enclosing function's variables.
FUNCTIONAL = "#include <functional>"
TUPLE = "#include <tuple>"
QUEUE = "#include <queue>"
STACK = "#include <stack>"
CLIMITS = "#include <climits>"
USING = "using namespace std;"

LIST_NODE = _src(
    """
    struct ListNode {
        int val;
        ListNode *next;
        ListNode() : val(0), next(nullptr) {}
        ListNode(int x) : val(x), next(nullptr) {}
        ListNode(int x, ListNode *next) : val(x), next(next) {}
    };
    """
)

TREE_NODE = _src(
    """
    struct TreeNode {
        int val;
        TreeNode *left;
        TreeNode *right;
        TreeNode() : val(0), left(nullptr), right(nullptr) {}
        TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
    };
    """
)

GRAPH_NODE = _src(
    """
    struct Node {
        int val;
        vector<Node*> neighbors;
        Node() : val(0) {}
        Node(int x) : val(x) {}
    };
    """
)
