"""Pieces shared by the Dart pattern files.

Separate module so `problems_dart` and `problems_dart2` can both use the node
classes without importing each other.
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


LIST_NODE = _src(
    """
    class ListNode {
      int val;
      ListNode? next;
      ListNode(this.val, [this.next]);
    }
    """
)

TREE_NODE = _src(
    """
    class TreeNode {
      int val;
      TreeNode? left;
      TreeNode? right;
      TreeNode(this.val, [this.left, this.right]);
    }
    """
)

GRAPH_NODE = _src(
    """
    class Node {
      int val;
      List<Node> neighbors;
      Node(this.val, [List<Node>? neighbors]) : neighbors = neighbors ?? [];
    }
    """
)

COLLECTION = "import 'dart:collection';"
MATH = "import 'dart:math';"
